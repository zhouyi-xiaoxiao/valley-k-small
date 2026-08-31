"""Bounded, semantics-free supervision for one isolated child process.

This is a generic component only.  The supervisor owns process mechanics and does not interpret
codes, stdout, stderr, or any numerical payload.  A caller supplies an
absolute argv, a fresh private working directory, the exact five-key process
environment, and an absolute monotonic deadline.

Every successfully started process is placed in a new session.  All paths
after ``Popen`` converge on the same bounded TERM -> KILL -> reap cleanup
state machine, including capture failures and output-limit violations.

This component does not authenticate executable bytes, prove directory
freshness, close the path-validation-to-Popen race, or contain a descendant
that deliberately escapes the observed session/process group.

No production deadline adapter is implemented here.  A production caller
must bind ``global_deadline = phase_end - 10``,
``cleanup_deadline = phase_end <= D_outer``, and the operation contract's
exact phase limits (including the exact 5-second TERM and 5-second KILL
limits) before calling this generic API.
"""

from __future__ import annotations

import math
import os
import selectors
import signal
import stat
import subprocess
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

ENVIRONMENT_KEYS: Final = frozenset({"HOME", "LANG", "LC_ALL", "TMPDIR", "TZ"})

ISSUE_GLOBAL_DEADLINE: Final = "GLOBAL_DEADLINE_EXCEEDED"
ISSUE_PROCESS_TIMEOUT: Final = "PROCESS_DEADLINE_EXCEEDED"
ISSUE_STDOUT_LIMIT: Final = "STDOUT_LIMIT_EXCEEDED"
ISSUE_STDERR_LIMIT: Final = "STDERR_LIMIT_EXCEEDED"
ISSUE_LIVE_PROCESS_GROUP: Final = "PROCESS_GROUP_LIVE_AFTER_DIRECT_CHILD_EXIT"
ISSUE_PIPE_EOF_TIMEOUT: Final = "PIPE_EOF_DEADLINE_EXCEEDED"
ISSUE_CAPTURE_FAILURE: Final = "CAPTURE_FAILURE"
ISSUE_CLEANUP_FAILURE: Final = "CLEANUP_INCOMPLETE"
ISSUE_CLEANUP_DEADLINE: Final = "CLEANUP_DEADLINE_EXCEEDED"
ISSUE_SPAWN_FAILURE: Final = "SPAWN_FAILED"
ISSUE_SELECTOR_FAILURE: Final = "SELECTOR_CREATION_FAILED"
ISSUE_SESSION_OBSERVATION: Final = "SESSION_IDENTITY_OBSERVATION_FAILED"
ISSUE_SESSION_MISMATCH: Final = "SESSION_IDENTITY_MISMATCH"

_READ_CHUNK_BYTES: Final = 65_536
_MAX_READS_PER_TURN: Final = 16
_MAX_ARG_COUNT: Final = 4_096
_MAX_ARG_BYTES: Final = 1_048_576
_MAX_CAPTURE_LIMIT: Final = 64 * 1024 * 1024


class SupervisorInputError(ValueError):
    """The requested launch does not satisfy the isolated-process contract."""


@dataclass(frozen=True)
class SupervisorLimits:
    """All durations are monotonic seconds and all byte limits exclude cap+1."""

    stdout_bytes: int = 1_048_576
    stderr_bytes: int = 262_144
    process_seconds: float = 60.0
    term_grace_seconds: float = 2.0
    kill_wait_seconds: float = 2.0
    group_absence_seconds: float = 2.0
    pipe_drain_seconds: float = 2.0
    select_interval_seconds: float = 0.05

    def __post_init__(self) -> None:
        for name in ("stdout_bytes", "stderr_bytes"):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value <= _MAX_CAPTURE_LIMIT:
                raise SupervisorInputError(f"invalid {name}")
        for name in (
            "process_seconds",
            "kill_wait_seconds",
            "group_absence_seconds",
            "pipe_drain_seconds",
            "select_interval_seconds",
        ):
            _positive_finite(getattr(self, name), name)
        value = self.term_grace_seconds
        if type(value) not in {int, float} or not math.isfinite(value) or value < 0.0:
            raise SupervisorInputError("invalid term_grace_seconds")


@dataclass(frozen=True)
class CleanupResult:
    """Mechanically checkable postcondition for the supervisor-owned resources."""

    process_started: bool
    owned_pgid: int | None
    direct_child_reaped: bool
    process_group_absent: bool
    stdout_eof_observed: bool
    stderr_eof_observed: bool
    parent_pipe_fds_closed: bool
    selector_closed: bool
    term_signal_sent: bool
    kill_signal_sent: bool
    term_phase_deadline_reached: bool
    kill_phase_deadline_reached: bool
    group_phase_deadline_reached: bool
    pipe_phase_deadline_reached: bool
    complete: bool


@dataclass(frozen=True)
class SupervisionResult:
    """Raw process outcome plus bounded-cleanup evidence."""

    argv: tuple[str, ...]
    pid: int | None
    observed_pgid: int | None
    observed_sid: int | None
    session_identity_matches: bool | None
    returncode: int | None
    stdout: bytes
    stderr: bytes
    stdout_truncated: bool
    stderr_truncated: bool
    issues: tuple[str, ...]
    cleanup: CleanupResult
    started_monotonic: float
    finished_monotonic: float
    global_deadline: float
    cleanup_deadline: float
    spawn_error_type: str | None
    spawn_errno: int | None


@dataclass
class _CaptureState:
    stdout: bytearray
    stderr: bytearray
    stdout_eof: bool = False
    stderr_eof: bool = False
    stdout_truncated: bool = False
    stderr_truncated: bool = False
    stdout_nonblocking_ready: bool = False
    stderr_nonblocking_ready: bool = False


def _positive_finite(value: object, name: str) -> float:
    if type(value) not in {int, float}:
        raise SupervisorInputError(f"invalid {name}")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric <= 0.0:
        raise SupervisorInputError(f"invalid {name}")
    return numeric


def _append_issue(issues: list[str], issue: str) -> None:
    if issue not in issues:
        issues.append(issue)


def _validate_argv(argv: Sequence[str]) -> tuple[str, ...]:
    if type(argv) not in {list, tuple}:
        raise SupervisorInputError("argv must be a plain list or tuple")
    fixed = tuple(argv)
    if not fixed or len(fixed) > _MAX_ARG_COUNT:
        raise SupervisorInputError("invalid argv length")
    total = 0
    for argument in fixed:
        if type(argument) is not str or "\x00" in argument:
            raise SupervisorInputError("invalid argv member")
        if len(argument) > _MAX_ARG_BYTES:
            raise SupervisorInputError("argv is too large")
        try:
            total += len(argument.encode("utf-8"))
        except UnicodeEncodeError as error:
            raise SupervisorInputError("argv members must be valid UTF-8 text") from error
    if total > _MAX_ARG_BYTES:
        raise SupervisorInputError("argv is too large")
    executable = Path(fixed[0])
    if not executable.is_absolute():
        raise SupervisorInputError("argv[0] must be absolute")
    return fixed


def _validate_private_directory(raw: os.PathLike[str] | str, name: str) -> Path:
    if isinstance(raw, bytes):
        raise SupervisorInputError(f"{name} must be a text path")
    try:
        path = Path(raw)
    except TypeError as error:
        raise SupervisorInputError(f"invalid {name}") from error
    if not path.is_absolute():
        raise SupervisorInputError(f"{name} must be absolute")
    try:
        resolved = path.resolve(strict=True)
        metadata = path.lstat()
    except OSError as error:
        raise SupervisorInputError(f"unavailable {name}") from error
    if resolved != path or stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise SupervisorInputError(f"{name} must be a canonical directory")
    if stat.S_IMODE(metadata.st_mode) != 0o700:
        raise SupervisorInputError(f"{name} must have mode 0700")
    if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
        raise SupervisorInputError(f"{name} must be owned by the current uid")
    return path


def _validate_environment(
    environment: Mapping[str, str],
    *,
    cwd: Path,
) -> dict[str, str]:
    if type(environment) is not dict:
        raise SupervisorInputError("environment must be a plain dict")
    if set(environment) != ENVIRONMENT_KEYS or len(environment) != len(ENVIRONMENT_KEYS):
        raise SupervisorInputError("environment must contain exactly five keys")
    copied: dict[str, str] = {}
    for key in sorted(ENVIRONMENT_KEYS):
        value = environment[key]
        if type(key) is not str or type(value) is not str or "\x00" in value:
            raise SupervisorInputError("environment keys and values must be text")
        try:
            encoded = value.encode("utf-8")
        except UnicodeEncodeError as error:
            raise SupervisorInputError("environment values must be valid UTF-8 text") from error
        if len(encoded) > _MAX_ARG_BYTES:
            raise SupervisorInputError("environment value is too large")
        copied[key] = value
    if copied["LANG"] != "C" or copied["LC_ALL"] != "C" or copied["TZ"] != "UTC":
        raise SupervisorInputError("locale and timezone values are not exact")
    home = _validate_private_directory(copied["HOME"], "HOME")
    temporary = _validate_private_directory(copied["TMPDIR"], "TMPDIR")
    if home == temporary or home == cwd or temporary == cwd:
        raise SupervisorInputError("HOME and TMPDIR must be distinct private children")
    for path, name in ((home, "HOME"), (temporary, "TMPDIR")):
        try:
            path.relative_to(cwd)
        except ValueError as error:
            raise SupervisorInputError(f"{name} must be below cwd") from error
    return copied


def _group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def _signal_group(pgid: int, action: signal.Signals) -> bool:
    try:
        os.killpg(pgid, action)
    except ProcessLookupError:
        return False
    except OSError:
        return False
    return True


def _state_eof(state: _CaptureState, name: str) -> bool:
    return state.stdout_eof if name == "stdout" else state.stderr_eof


def _set_state_eof(state: _CaptureState, name: str) -> None:
    if name == "stdout":
        state.stdout_eof = True
    else:
        state.stderr_eof = True


def _state_nonblocking_ready(state: _CaptureState, name: str) -> bool:
    return state.stdout_nonblocking_ready if name == "stdout" else state.stderr_nonblocking_ready


def _set_state_nonblocking_ready(state: _CaptureState, name: str) -> None:
    if name == "stdout":
        state.stdout_nonblocking_ready = True
    else:
        state.stderr_nonblocking_ready = True


def _capture_aborted(issues: list[str]) -> bool:
    return any(
        issue
        in {
            ISSUE_STDOUT_LIMIT,
            ISSUE_STDERR_LIMIT,
            ISSUE_CAPTURE_FAILURE,
            ISSUE_SELECTOR_FAILURE,
        }
        for issue in issues
    )


def _read_stream(
    name: str,
    stream: object,
    selector: selectors.BaseSelector,
    state: _CaptureState,
    limits: SupervisorLimits,
    issues: list[str],
) -> None:
    if _state_eof(state, name) or getattr(stream, "closed", True):
        return
    if not _state_nonblocking_ready(state, name):
        _append_issue(issues, ISSUE_CAPTURE_FAILURE)
        return
    buffer = state.stdout if name == "stdout" else state.stderr
    limit = limits.stdout_bytes if name == "stdout" else limits.stderr_bytes
    for _read_index in range(_MAX_READS_PER_TURN):
        try:
            chunk = os.read(stream.fileno(), _READ_CHUNK_BYTES)  # type: ignore[attr-defined]
        except BlockingIOError:
            return
        except BaseException:
            _append_issue(issues, ISSUE_CAPTURE_FAILURE)
            return
        if chunk == b"":
            _set_state_eof(state, name)
            try:
                selector.unregister(stream)
            except (KeyError, ValueError):
                pass
            except BaseException:
                _append_issue(issues, ISSUE_CAPTURE_FAILURE)
            return
        remaining = limit + 1 - len(buffer)
        if remaining > 0:
            buffer.extend(chunk[:remaining])
        if len(buffer) > limit:
            if name == "stdout":
                newly_truncated = not state.stdout_truncated
                state.stdout_truncated = True
                _append_issue(issues, ISSUE_STDOUT_LIMIT)
            else:
                newly_truncated = not state.stderr_truncated
                state.stderr_truncated = True
                _append_issue(issues, ISSUE_STDERR_LIMIT)
            if newly_truncated:
                return


def _drain_all(
    streams: dict[str, object],
    selector: selectors.BaseSelector,
    state: _CaptureState,
    limits: SupervisorLimits,
    issues: list[str],
    *,
    stop_on_abort: bool,
) -> None:
    for name, stream in streams.items():
        if stop_on_abort and _capture_aborted(issues):
            return
        _read_stream(name, stream, selector, state, limits, issues)


def _selector_wait(
    selector: selectors.BaseSelector,
    streams: dict[str, object],
    state: _CaptureState,
    limits: SupervisorLimits,
    issues: list[str],
    *,
    deadline: float,
    stop_on_abort: bool,
) -> None:
    if stop_on_abort and _capture_aborted(issues):
        return
    remaining = max(0.0, deadline - time.monotonic())
    timeout = min(limits.select_interval_seconds, remaining)
    try:
        events = selector.select(timeout)
    except BaseException:
        _append_issue(issues, ISSUE_CAPTURE_FAILURE)
        return
    for key, _mask in events:
        if stop_on_abort and _capture_aborted(issues):
            return
        _read_stream(key.data, key.fileobj, selector, state, limits, issues)
    _drain_all(
        streams,
        selector,
        state,
        limits,
        issues,
        stop_on_abort=stop_on_abort,
    )


def _prepare_capture_streams(
    streams: dict[str, object],
    selector: selectors.BaseSelector,
    state: _CaptureState,
    issues: list[str],
) -> bool:
    for name, stream in streams.items():
        if stream is None:
            _append_issue(issues, ISSUE_CAPTURE_FAILURE)
            return False
        try:
            descriptor = stream.fileno()  # type: ignore[attr-defined]
            os.set_blocking(descriptor, False)
            if os.get_blocking(descriptor):
                raise OSError("pipe remained blocking")
            _set_state_nonblocking_ready(state, name)
            selector.register(stream, selectors.EVENT_READ, name)
        except BaseException:
            _append_issue(issues, ISSUE_CAPTURE_FAILURE)
            return False
    return True


def _wait_process_and_group(
    process: subprocess.Popen[bytes],
    owned_pgid: int | None,
    selector: selectors.BaseSelector,
    streams: dict[str, object],
    state: _CaptureState,
    limits: SupervisorLimits,
    issues: list[str],
    *,
    deadline: float,
    drain_while_waiting: bool,
) -> tuple[bool, bool]:
    while time.monotonic() < deadline:
        reaped = process.poll() is not None
        absence_verified = owned_pgid is not None and not _group_exists(owned_pgid)
        if reaped and (owned_pgid is None or absence_verified):
            return reaped, absence_verified
        if drain_while_waiting and not _capture_aborted(issues):
            _selector_wait(
                selector,
                streams,
                state,
                limits,
                issues,
                deadline=deadline,
                stop_on_abort=True,
            )
        else:
            time.sleep(
                min(
                    limits.select_interval_seconds,
                    max(0.0, deadline - time.monotonic()),
                )
            )
    return (
        process.poll() is not None,
        owned_pgid is not None and not _group_exists(owned_pgid),
    )


def _cleanup_started_process(
    process: subprocess.Popen[bytes],
    selector: selectors.BaseSelector,
    state: _CaptureState,
    limits: SupervisorLimits,
    issues: list[str],
    *,
    cleanup_deadline: float,
    owned_pgid: int | None,
    drain_allowed: bool,
) -> CleanupResult:
    streams: dict[str, object] = {
        "stdout": process.stdout,
        "stderr": process.stderr,
    }
    term_sent = False
    kill_sent = False
    term_deadline_reached = False
    kill_deadline_reached = False
    group_deadline_reached = False
    pipe_deadline_reached = False

    running = process.poll() is None
    group_alive = owned_pgid is not None and _group_exists(owned_pgid)
    if running or group_alive:
        if owned_pgid is not None:
            term_sent = _signal_group(owned_pgid, signal.SIGTERM)
        elif running:
            try:
                process.terminate()
                term_sent = True
            except ProcessLookupError:
                pass
            except BaseException:
                _append_issue(issues, ISSUE_CLEANUP_FAILURE)
        term_deadline = min(
            time.monotonic() + limits.term_grace_seconds,
            cleanup_deadline,
        )
        reaped, absent = _wait_process_and_group(
            process,
            owned_pgid,
            selector,
            streams,
            state,
            limits,
            issues,
            deadline=term_deadline,
            drain_while_waiting=drain_allowed and not _capture_aborted(issues),
        )
        term_deadline_reached = not (reaped and (owned_pgid is None or absent))
        if not reaped or (owned_pgid is not None and not absent):
            if owned_pgid is not None:
                kill_sent = _signal_group(owned_pgid, signal.SIGKILL)
            elif not reaped:
                try:
                    process.kill()
                    kill_sent = True
                except ProcessLookupError:
                    pass
                except BaseException:
                    _append_issue(issues, ISSUE_CLEANUP_FAILURE)
            kill_deadline = min(
                time.monotonic() + limits.kill_wait_seconds,
                cleanup_deadline,
            )
            reaped, absent = _wait_process_and_group(
                process,
                owned_pgid,
                selector,
                streams,
                state,
                limits,
                issues,
                deadline=kill_deadline,
                drain_while_waiting=drain_allowed and not _capture_aborted(issues),
            )
            kill_deadline_reached = not (reaped and (owned_pgid is None or absent))

    direct_reaped = process.poll() is not None
    if not direct_reaped:
        try:
            process.kill()
            kill_sent = True
        except ProcessLookupError:
            pass
        except BaseException:
            _append_issue(issues, ISSUE_CLEANUP_FAILURE)
        try:
            process.wait(
                timeout=max(
                    0.0,
                    min(
                        limits.kill_wait_seconds,
                        cleanup_deadline - time.monotonic(),
                    ),
                )
            )
            direct_reaped = True
        except BaseException:
            direct_reaped = False

    group_absent = owned_pgid is not None and not _group_exists(owned_pgid)
    if owned_pgid is not None and not group_absent:
        kill_sent = _signal_group(owned_pgid, signal.SIGKILL) or kill_sent
        group_deadline = min(
            time.monotonic() + limits.group_absence_seconds,
            cleanup_deadline,
        )
        while time.monotonic() < group_deadline and _group_exists(owned_pgid):
            if not drain_allowed or _capture_aborted(issues):
                time.sleep(
                    min(
                        limits.select_interval_seconds,
                        max(0.0, group_deadline - time.monotonic()),
                    )
                )
            else:
                _selector_wait(
                    selector,
                    streams,
                    state,
                    limits,
                    issues,
                    deadline=group_deadline,
                    stop_on_abort=True,
                )
        group_absent = not _group_exists(owned_pgid)
        group_deadline_reached = not group_absent

    if drain_allowed:
        _drain_all(
            streams,
            selector,
            state,
            limits,
            issues,
            stop_on_abort=False,
        )
        pipe_deadline = min(
            time.monotonic() + limits.pipe_drain_seconds,
            cleanup_deadline,
        )
        while not (state.stdout_eof and state.stderr_eof) and time.monotonic() < pipe_deadline:
            _drain_all(
                streams,
                selector,
                state,
                limits,
                issues,
                stop_on_abort=False,
            )
            if state.stdout_eof and state.stderr_eof:
                break
            time.sleep(
                min(
                    limits.select_interval_seconds,
                    max(0.0, pipe_deadline - time.monotonic()),
                )
            )
        pipe_deadline_reached = not (state.stdout_eof and state.stderr_eof)
        if pipe_deadline_reached:
            _append_issue(issues, ISSUE_PIPE_EOF_TIMEOUT)

    for stream in streams.values():
        if stream is None:
            continue
        try:
            selector.unregister(stream)
        except (KeyError, ValueError):
            pass
        except BaseException:
            _append_issue(issues, ISSUE_CLEANUP_FAILURE)
        try:
            stream.close()  # type: ignore[attr-defined]
        except BaseException:
            _append_issue(issues, ISSUE_CLEANUP_FAILURE)
    pipes_closed = all(
        stream is not None and getattr(stream, "closed", False) for stream in streams.values()
    )
    try:
        selector.close()
        selector_closed = True
    except BaseException:
        selector_closed = False

    complete = all(
        (
            direct_reaped,
            group_absent,
            state.stdout_eof,
            state.stderr_eof,
            pipes_closed,
            selector_closed,
        )
    )
    if not complete:
        _append_issue(issues, ISSUE_CLEANUP_FAILURE)
    return CleanupResult(
        process_started=True,
        owned_pgid=owned_pgid,
        direct_child_reaped=direct_reaped,
        process_group_absent=group_absent,
        stdout_eof_observed=state.stdout_eof,
        stderr_eof_observed=state.stderr_eof,
        parent_pipe_fds_closed=pipes_closed,
        selector_closed=selector_closed,
        term_signal_sent=term_sent,
        kill_signal_sent=kill_sent,
        term_phase_deadline_reached=term_deadline_reached,
        kill_phase_deadline_reached=kill_deadline_reached,
        group_phase_deadline_reached=group_deadline_reached,
        pipe_phase_deadline_reached=pipe_deadline_reached,
        complete=complete,
    )


def _not_started_cleanup(*, selector_closed: bool) -> CleanupResult:
    return CleanupResult(
        process_started=False,
        owned_pgid=None,
        direct_child_reaped=False,
        process_group_absent=True,
        stdout_eof_observed=False,
        stderr_eof_observed=False,
        parent_pipe_fds_closed=True,
        selector_closed=selector_closed,
        term_signal_sent=False,
        kill_signal_sent=False,
        term_phase_deadline_reached=False,
        kill_phase_deadline_reached=False,
        group_phase_deadline_reached=False,
        pipe_phase_deadline_reached=False,
        complete=selector_closed,
    )


def _not_started_result(
    argv: tuple[str, ...],
    *,
    started: float,
    global_deadline: float,
    cleanup_deadline: float,
    issue: str,
    selector_closed: bool,
    error: BaseException | None = None,
) -> SupervisionResult:
    error_number = getattr(error, "errno", None)
    finished = time.monotonic()
    issues = [issue]
    if finished >= global_deadline:
        _append_issue(issues, ISSUE_GLOBAL_DEADLINE)
    if finished >= cleanup_deadline:
        _append_issue(issues, ISSUE_CLEANUP_DEADLINE)
    return SupervisionResult(
        argv=argv,
        pid=None,
        observed_pgid=None,
        observed_sid=None,
        session_identity_matches=None,
        returncode=None,
        stdout=b"",
        stderr=b"",
        stdout_truncated=False,
        stderr_truncated=False,
        issues=tuple(issues),
        cleanup=_not_started_cleanup(selector_closed=selector_closed),
        started_monotonic=started,
        finished_monotonic=finished,
        global_deadline=global_deadline,
        cleanup_deadline=cleanup_deadline,
        spawn_error_type=None if error is None else type(error).__name__,
        spawn_errno=error_number if type(error_number) is int else None,
    )


def supervise_process(
    argv: Sequence[str],
    *,
    cwd: os.PathLike[str] | str,
    environment: Mapping[str, str],
    global_deadline: float,
    cleanup_deadline: float,
    limits: SupervisorLimits | None = None,
) -> SupervisionResult:
    """Launch and completely supervise one process without interpreting its payload.

    Invalid launch contracts raise :class:`SupervisorInputError`.  Runtime
    failures, including ``Popen`` failure, are returned as structured results.
    Every cleanup wait is clipped to the caller's absolute cleanup deadline,
    which must be later than the global work deadline.
    """

    fixed_argv = _validate_argv(argv)
    private_cwd = _validate_private_directory(cwd, "cwd")
    copied_environment = _validate_environment(environment, cwd=private_cwd)
    deadline = _positive_finite(global_deadline, "global_deadline")
    absolute_cleanup_deadline = _positive_finite(cleanup_deadline, "cleanup_deadline")
    if absolute_cleanup_deadline <= deadline:
        raise SupervisorInputError("cleanup_deadline must be after global_deadline")
    active_limits = SupervisorLimits() if limits is None else limits
    if not isinstance(active_limits, SupervisorLimits):
        raise SupervisorInputError("limits must be SupervisorLimits")

    started = time.monotonic()
    if started >= deadline:
        return _not_started_result(
            fixed_argv,
            started=started,
            global_deadline=deadline,
            cleanup_deadline=absolute_cleanup_deadline,
            issue=ISSUE_GLOBAL_DEADLINE,
            selector_closed=True,
        )
    try:
        selector = selectors.DefaultSelector()
    except BaseException as error:
        return _not_started_result(
            fixed_argv,
            started=started,
            global_deadline=deadline,
            cleanup_deadline=absolute_cleanup_deadline,
            issue=ISSUE_SELECTOR_FAILURE,
            selector_closed=False,
            error=error,
        )
    if time.monotonic() >= deadline:
        try:
            selector.close()
            selector_closed = True
        except BaseException:
            selector_closed = False
        return _not_started_result(
            fixed_argv,
            started=started,
            global_deadline=deadline,
            cleanup_deadline=absolute_cleanup_deadline,
            issue=ISSUE_GLOBAL_DEADLINE,
            selector_closed=selector_closed,
        )
    try:
        process = subprocess.Popen(
            fixed_argv,
            cwd=private_cwd,
            env=copied_environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            close_fds=True,
            start_new_session=True,
            bufsize=0,
            umask=0o077,
        )
    except BaseException as error:
        try:
            selector.close()
            selector_closed = True
        except BaseException:
            selector_closed = False
        return _not_started_result(
            fixed_argv,
            started=started,
            global_deadline=deadline,
            cleanup_deadline=absolute_cleanup_deadline,
            issue=ISSUE_SPAWN_FAILURE,
            selector_closed=selector_closed,
            error=error,
        )

    post_spawn_now = time.monotonic()
    observed_pgid: int | None = None
    observed_sid: int | None = None
    session_identity_matches: bool | None = None
    owned_pgid: int | None = None
    issues: list[str] = []
    if post_spawn_now >= deadline:
        _append_issue(issues, ISSUE_GLOBAL_DEADLINE)
        if post_spawn_now >= absolute_cleanup_deadline:
            _append_issue(issues, ISSUE_CLEANUP_DEADLINE)
    else:
        try:
            observed_pgid = os.getpgid(process.pid)
            observed_sid = os.getsid(process.pid)
        except BaseException:
            _append_issue(issues, ISSUE_SESSION_OBSERVATION)
        else:
            session_identity_matches = observed_pgid == process.pid and observed_sid == process.pid
            if session_identity_matches:
                owned_pgid = process.pid
            else:
                _append_issue(issues, ISSUE_SESSION_MISMATCH)

    state = _CaptureState(bytearray(), bytearray())
    streams: dict[str, object] = {"stdout": process.stdout, "stderr": process.stderr}
    process_deadline = min(started + active_limits.process_seconds, deadline)
    exit_pipe_deadline: float | None = None
    capture_prepared = False
    if post_spawn_now < deadline:
        capture_prepared = _prepare_capture_streams(
            streams,
            selector,
            state,
            issues,
        )
    try:
        while capture_prepared and not issues:
            now = time.monotonic()
            next_deadline = (
                process_deadline
                if exit_pipe_deadline is None
                else min(exit_pipe_deadline, deadline)
            )
            _selector_wait(
                selector,
                streams,
                state,
                active_limits,
                issues,
                deadline=next_deadline,
                stop_on_abort=True,
            )
            now = time.monotonic()
            if now >= deadline:
                _append_issue(issues, ISSUE_GLOBAL_DEADLINE)
                break
            if _capture_aborted(issues):
                break
            if exit_pipe_deadline is None and now >= process_deadline:
                _append_issue(issues, ISSUE_PROCESS_TIMEOUT)
                break
            returncode = process.poll()
            if returncode is not None:
                if owned_pgid is not None and _group_exists(owned_pgid):
                    _append_issue(issues, ISSUE_LIVE_PROCESS_GROUP)
                    break
                if state.stdout_eof and state.stderr_eof:
                    break
                if exit_pipe_deadline is None:
                    exit_pipe_deadline = min(
                        now + active_limits.pipe_drain_seconds,
                        deadline,
                    )
                if now >= exit_pipe_deadline:
                    _append_issue(issues, ISSUE_PIPE_EOF_TIMEOUT)
                    break
    except BaseException:
        _append_issue(issues, ISSUE_CAPTURE_FAILURE)

    cleanup = _cleanup_started_process(
        process,
        selector,
        state,
        active_limits,
        issues,
        cleanup_deadline=absolute_cleanup_deadline,
        owned_pgid=owned_pgid,
        drain_allowed=capture_prepared and not _capture_aborted(issues),
    )
    finished = time.monotonic()
    if finished >= deadline:
        _append_issue(issues, ISSUE_GLOBAL_DEADLINE)
    if finished >= absolute_cleanup_deadline:
        _append_issue(issues, ISSUE_CLEANUP_DEADLINE)
    return SupervisionResult(
        argv=fixed_argv,
        pid=process.pid,
        observed_pgid=observed_pgid,
        observed_sid=observed_sid,
        session_identity_matches=session_identity_matches,
        returncode=process.returncode,
        stdout=bytes(state.stdout),
        stderr=bytes(state.stderr),
        stdout_truncated=state.stdout_truncated,
        stderr_truncated=state.stderr_truncated,
        issues=tuple(issues),
        cleanup=cleanup,
        started_monotonic=started,
        finished_monotonic=finished,
        global_deadline=deadline,
        cleanup_deadline=absolute_cleanup_deadline,
        spawn_error_type=None,
        spawn_errno=None,
    )
