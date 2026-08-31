from __future__ import annotations

import os
import signal
import stat
import sys
import time
from pathlib import Path

import continuum_c1_n0_runtime_process_supervisor_v1 as supervisor
import pytest

PYTHON = os.path.realpath(sys.executable)
_REAL_SELECTOR = supervisor.selectors.DefaultSelector
_REAL_POPEN = supervisor.subprocess.Popen
_REAL_GETPGID = os.getpgid


class _SelectorProxy:
    def __init__(self, *, delay: float = 0.0, fail: bool = False) -> None:
        self._inner = _REAL_SELECTOR()
        self._delay = delay
        self._fail = fail

    def register(self, *args: object, **kwargs: object) -> object:
        return self._inner.register(*args, **kwargs)

    def unregister(self, *args: object, **kwargs: object) -> object:
        return self._inner.unregister(*args, **kwargs)

    def select(self, timeout: float | None = None) -> object:
        if self._fail:
            raise RuntimeError("injected selector failure")
        time.sleep(max(0.0, 0.0 if timeout is None else timeout) + self._delay)
        return self._inner.select(0.0)

    def close(self) -> None:
        self._inner.close()


def _private_launch_root(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    cwd = (tmp_path / "run").resolve()
    cwd.mkdir(mode=0o700)
    home = cwd / "home"
    temporary = cwd / "tmp"
    home.mkdir(mode=0o700)
    temporary.mkdir(mode=0o700)
    return cwd, {
        "HOME": os.fspath(home),
        "LANG": "C",
        "LC_ALL": "C",
        "TMPDIR": os.fspath(temporary),
        "TZ": "UTC",
    }


def _limits(**changes: object) -> supervisor.SupervisorLimits:
    values: dict[str, object] = {
        "stdout_bytes": 4_096,
        "stderr_bytes": 4_096,
        "process_seconds": 3.0,
        "term_grace_seconds": 0.15,
        "kill_wait_seconds": 0.75,
        "group_absence_seconds": 0.75,
        "pipe_drain_seconds": 0.75,
        "select_interval_seconds": 0.01,
    }
    values.update(changes)
    return supervisor.SupervisorLimits(**values)  # type: ignore[arg-type]


def _run(
    tmp_path: Path,
    source: str,
    *,
    limits: supervisor.SupervisorLimits | None = None,
) -> tuple[supervisor.SupervisionResult, Path]:
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    result = supervisor.supervise_process(
        (PYTHON, "-I", "-B", "-c", source),
        cwd=cwd,
        environment=environment,
        global_deadline=now + 8.0,
        cleanup_deadline=now + 10.0,
        limits=_limits() if limits is None else limits,
    )
    return result, cwd


def _assert_complete_started_cleanup(result: supervisor.SupervisionResult) -> None:
    assert result.cleanup.process_started
    assert result.cleanup.owned_pgid == result.pid
    assert result.cleanup.direct_child_reaped
    assert result.cleanup.process_group_absent
    assert result.cleanup.stdout_eof_observed
    assert result.cleanup.stderr_eof_observed
    assert result.cleanup.parent_pipe_fds_closed
    assert result.cleanup.selector_closed
    assert result.cleanup.complete


def _assert_incomplete_started_cleanup(result: supervisor.SupervisionResult) -> None:
    assert result.cleanup.process_started
    assert result.cleanup.direct_child_reaped
    assert result.cleanup.parent_pipe_fds_closed
    assert result.cleanup.selector_closed
    assert not result.cleanup.complete
    assert supervisor.ISSUE_CLEANUP_FAILURE in result.issues


def test_clean_success_and_umask_are_captured_without_semantic_interpretation(
    tmp_path: Path,
) -> None:
    result, cwd = _run(
        tmp_path,
        "from pathlib import Path; Path('made').write_bytes(b'x'); print('ok')",
    )
    assert result.returncode == 0
    assert result.stdout == b"ok\n"
    assert result.stderr == b""
    assert result.issues == ()
    assert not result.stdout_truncated
    assert not result.stderr_truncated
    assert stat.S_IMODE((cwd / "made").stat().st_mode) == 0o600
    _assert_complete_started_cleanup(result)


def test_new_session_identity_is_observed_immediately(tmp_path: Path) -> None:
    result, _cwd = _run(tmp_path, "print('identity')")
    assert result.pid is not None
    assert result.observed_pgid == result.pid
    assert result.observed_sid == result.pid
    assert result.session_identity_matches is True
    assert result.issues == ()
    _assert_complete_started_cleanup(result)


def test_session_identity_mismatch_enters_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(supervisor.os, "getpgid", lambda pid: pid + 1)
    result, _cwd = _run(tmp_path, "import time; time.sleep(60)")
    assert supervisor.ISSUE_SESSION_MISMATCH in result.issues
    assert result.pid is not None
    assert result.observed_pgid == result.pid + 1
    assert result.observed_sid == result.pid
    assert result.session_identity_matches is False
    assert result.cleanup.owned_pgid is None
    assert not result.cleanup.process_group_absent
    assert result.cleanup.term_signal_sent
    _assert_incomplete_started_cleanup(result)


def test_session_identity_observation_failure_enters_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_observation(_pid: int) -> int:
        raise ProcessLookupError

    monkeypatch.setattr(supervisor.os, "getpgid", fail_observation)
    result, _cwd = _run(tmp_path, "import time; time.sleep(60)")
    assert supervisor.ISSUE_SESSION_OBSERVATION in result.issues
    assert result.observed_pgid is None
    assert result.observed_sid is None
    assert result.session_identity_matches is None
    assert result.cleanup.owned_pgid is None
    assert not result.cleanup.process_group_absent
    _assert_incomplete_started_cleanup(result)


def test_stderr_is_raw_data_and_strict_rejection_remains_a_caller_policy(
    tmp_path: Path,
) -> None:
    result, _cwd = _run(
        tmp_path,
        "import sys; sys.stderr.write('warning\\n')",
    )
    assert result.returncode == 0
    assert result.stderr == b"warning\n"
    assert result.issues == ()
    strict_caller_accepts = (
        result.returncode == 0
        and result.stdout == b""
        and result.stderr == b""
        and not result.issues
    )
    assert not strict_caller_accepts
    _assert_complete_started_cleanup(result)


def test_nonzero_returncode_is_raw_caller_policy(tmp_path: Path) -> None:
    result, _cwd = _run(tmp_path, "raise SystemExit(7)")
    assert result.returncode == 7
    assert result.stdout == b""
    assert result.stderr == b""
    assert result.issues == ()
    _assert_complete_started_cleanup(result)


def test_stdout_and_stderr_eof_are_observed_independently(tmp_path: Path) -> None:
    result, _cwd = _run(
        tmp_path,
        (
            "import os,time\n"
            "os.write(1, b'first\\n')\n"
            "os.close(1)\n"
            "time.sleep(0.05)\n"
            "os.write(2, b'second\\n')"
        ),
    )
    assert result.returncode == 0
    assert result.stdout == b"first\n"
    assert result.stderr == b"second\n"
    assert result.issues == ()
    _assert_complete_started_cleanup(result)


@pytest.mark.parametrize(
    ("stream", "issue"),
    [
        ("1", supervisor.ISSUE_STDOUT_LIMIT),
        ("2", supervisor.ISSUE_STDERR_LIMIT),
    ],
)
def test_output_flood_is_stored_only_through_cap_plus_one_and_cleaned(
    tmp_path: Path,
    stream: str,
    issue: str,
) -> None:
    result, _cwd = _run(
        tmp_path,
        f"import os\nwhile True: os.write({stream}, b'x' * 65536)",
        limits=_limits(stdout_bytes=127, stderr_bytes=127),
    )
    captured = result.stdout if stream == "1" else result.stderr
    assert len(captured) == 128
    assert issue in result.issues
    assert result.stdout_truncated is (stream == "1")
    assert result.stderr_truncated is (stream == "2")
    assert result.cleanup.term_signal_sent or result.cleanup.kill_signal_sent
    assert result.cleanup.owned_pgid == result.pid
    assert result.cleanup.process_group_absent
    assert not result.cleanup.stdout_eof_observed
    assert not result.cleanup.stderr_eof_observed
    _assert_incomplete_started_cleanup(result)


def test_selector_capture_failure_enters_cleanup_without_normal_drain(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        supervisor.selectors,
        "DefaultSelector",
        lambda: _SelectorProxy(fail=True),
    )
    result, _cwd = _run(tmp_path, "import time; time.sleep(60)")
    assert supervisor.ISSUE_CAPTURE_FAILURE in result.issues
    assert result.cleanup.term_signal_sent
    assert not result.cleanup.stdout_eof_observed
    assert not result.cleanup.stderr_eof_observed
    _assert_incomplete_started_cleanup(result)


def test_delayed_selector_cannot_turn_deadline_overshoot_into_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        supervisor.selectors,
        "DefaultSelector",
        lambda: _SelectorProxy(delay=0.06),
    )
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    result = supervisor.supervise_process(
        (PYTHON, "-I", "-B", "-c", "import time; time.sleep(0.02)"),
        cwd=cwd,
        environment=environment,
        global_deadline=now + 0.04,
        cleanup_deadline=now + 0.50,
        limits=_limits(process_seconds=2.0),
    )
    assert supervisor.ISSUE_GLOBAL_DEADLINE in result.issues
    assert result.finished_monotonic >= result.global_deadline
    _assert_complete_started_cleanup(result)


def test_selector_construction_is_regated_before_popen_with_both_deadlines(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    popen_calls = 0

    def delayed_selector() -> _SelectorProxy:
        time.sleep(0.07)
        return _SelectorProxy()

    def forbidden_popen(*args: object, **kwargs: object) -> object:
        nonlocal popen_calls
        popen_calls += 1
        return _REAL_POPEN(*args, **kwargs)

    monkeypatch.setattr(supervisor.selectors, "DefaultSelector", delayed_selector)
    monkeypatch.setattr(supervisor.subprocess, "Popen", forbidden_popen)
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    result = supervisor.supervise_process(
        (PYTHON, "-I", "-B", "-c", "raise SystemExit(99)"),
        cwd=cwd,
        environment=environment,
        global_deadline=now + 0.02,
        cleanup_deadline=now + 0.04,
        limits=_limits(),
    )
    assert popen_calls == 0
    assert result.pid is None
    assert result.issues == (
        supervisor.ISSUE_GLOBAL_DEADLINE,
        supervisor.ISSUE_CLEANUP_DEADLINE,
    )
    assert result.finished_monotonic >= result.cleanup_deadline
    assert result.cleanup.selector_closed


def test_popen_overshoot_enters_direct_no_drain_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def delayed_popen(*args: object, **kwargs: object) -> object:
        process = _REAL_POPEN(*args, **kwargs)
        time.sleep(0.07)
        return process

    monkeypatch.setattr(supervisor.subprocess, "Popen", delayed_popen)
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    result = supervisor.supervise_process(
        (PYTHON, "-I", "-B", "-c", "import time; time.sleep(60)"),
        cwd=cwd,
        environment=environment,
        global_deadline=now + 0.03,
        cleanup_deadline=now + 0.50,
        limits=_limits(),
    )
    assert supervisor.ISSUE_GLOBAL_DEADLINE in result.issues
    assert result.observed_pgid is None
    assert result.observed_sid is None
    assert result.cleanup.owned_pgid is None
    assert not result.cleanup.process_group_absent
    assert not result.cleanup.stdout_eof_observed
    assert not result.cleanup.stderr_eof_observed
    _assert_incomplete_started_cleanup(result)


def test_process_timeout_terminates_and_reaps_child(tmp_path: Path) -> None:
    result, _cwd = _run(
        tmp_path,
        "import time; time.sleep(60)",
        limits=_limits(process_seconds=0.20),
    )
    assert supervisor.ISSUE_PROCESS_TIMEOUT in result.issues
    assert result.cleanup.term_signal_sent
    assert result.returncode is not None
    _assert_complete_started_cleanup(result)


def test_term_ignoring_child_reaches_kill_phase(tmp_path: Path) -> None:
    result, _cwd = _run(
        tmp_path,
        (
            "import signal,time\n"
            "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "print('ready', flush=True)\n"
            "time.sleep(60)"
        ),
        limits=_limits(process_seconds=0.50, term_grace_seconds=0.05),
    )
    assert supervisor.ISSUE_PROCESS_TIMEOUT in result.issues
    assert result.stdout == b"ready\n"
    assert result.cleanup.term_signal_sent
    assert result.cleanup.kill_signal_sent
    assert result.returncode == -signal.SIGKILL
    _assert_complete_started_cleanup(result)


def test_live_descendant_holding_pipes_is_killed_with_process_group(
    tmp_path: Path,
) -> None:
    child_source = "import time; time.sleep(60)"
    parent_source = (
        f"import subprocess\nsubprocess.Popen(({PYTHON!r}, '-I', '-B', '-c', {child_source!r}))\n"
    )
    result, _cwd = _run(tmp_path, parent_source)
    assert supervisor.ISSUE_LIVE_PROCESS_GROUP in result.issues
    assert result.returncode == 0
    assert result.cleanup.term_signal_sent
    _assert_complete_started_cleanup(result)


def test_unowned_observed_group_is_not_signalled_and_really_persists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    pid_file = cwd / "same-group-descendant.pid"
    descendant_source = "import time; time.sleep(60)"
    parent_source = (
        "import pathlib,subprocess,time\n"
        f"p=subprocess.Popen(({PYTHON!r}, '-I', '-B', '-c', {descendant_source!r}),"
        "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
        "pathlib.Path('same-group-descendant.pid').write_text(str(p.pid))\n"
        "time.sleep(60)"
    )
    group_signal_calls: list[tuple[int, signal.Signals]] = []

    def delayed_mismatch(pid: int) -> int:
        wait_deadline = time.monotonic() + 0.30
        while not pid_file.exists() and time.monotonic() < wait_deadline:
            time.sleep(0.005)
        return pid + 1

    def forbidden_group_signal(pgid: int, action: signal.Signals) -> bool:
        group_signal_calls.append((pgid, action))
        raise AssertionError("unowned process group must not be signalled")

    monkeypatch.setattr(supervisor.os, "getpgid", delayed_mismatch)
    monkeypatch.setattr(supervisor, "_signal_group", forbidden_group_signal)
    now = time.monotonic()
    descendant_pid: int | None = None
    try:
        result = supervisor.supervise_process(
            (PYTHON, "-I", "-B", "-c", parent_source),
            cwd=cwd,
            environment=environment,
            global_deadline=now + 1.0,
            cleanup_deadline=now + 2.0,
            limits=_limits(),
        )
        descendant_pid = int(pid_file.read_text())
        assert result.pid is not None
        assert result.cleanup.owned_pgid is None
        assert not result.cleanup.process_group_absent
        assert not result.cleanup.complete
        assert group_signal_calls == []
        assert _REAL_GETPGID(descendant_pid) == result.pid
        os.kill(descendant_pid, 0)
    finally:
        if descendant_pid is not None:
            try:
                os.kill(descendant_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_set_blocking_failure_with_escaped_pipe_never_reads_or_drains(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    pid_file = cwd / "escaped-descendant.pid"
    descendant_source = "import time; time.sleep(60)"
    parent_source = (
        "import pathlib,signal,subprocess,time\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        f"p=subprocess.Popen(({PYTHON!r}, '-I', '-B', '-c', {descendant_source!r}),"
        "start_new_session=True)\n"
        "pathlib.Path('escaped-descendant.pid').write_text(str(p.pid))\n"
        "time.sleep(60)"
    )
    read_calls = 0

    def fail_after_descendant_started(_descriptor: int, _blocking: bool) -> None:
        wait_deadline = time.monotonic() + 0.30
        while not pid_file.exists() and time.monotonic() < wait_deadline:
            time.sleep(0.005)
        raise OSError("injected set_blocking failure")

    def forbidden_read_stream(*_args: object, **_kwargs: object) -> None:
        nonlocal read_calls
        read_calls += 1
        raise AssertionError("blocking pipe must never reach _read_stream")

    monkeypatch.setattr(supervisor.os, "set_blocking", fail_after_descendant_started)
    monkeypatch.setattr(supervisor, "_read_stream", forbidden_read_stream)
    now = time.monotonic()
    absolute_cleanup_deadline = now + 0.55
    descendant_pid: int | None = None
    result: supervisor.SupervisionResult | None = None
    try:
        result = supervisor.supervise_process(
            (PYTHON, "-I", "-B", "-c", parent_source),
            cwd=cwd,
            environment=environment,
            global_deadline=now + 0.40,
            cleanup_deadline=absolute_cleanup_deadline,
            limits=_limits(
                process_seconds=2.0,
                term_grace_seconds=5.0,
                pipe_drain_seconds=0.8,
            ),
        )
        assert pid_file.exists()
        descendant_pid = int(pid_file.read_text())
        assert read_calls == 0
        assert supervisor.ISSUE_CAPTURE_FAILURE in result.issues
        assert result.finished_monotonic >= absolute_cleanup_deadline - 0.08
        assert result.finished_monotonic <= absolute_cleanup_deadline + 0.08
        assert not result.cleanup.stdout_eof_observed
        assert not result.cleanup.stderr_eof_observed
        assert result.cleanup.parent_pipe_fds_closed
        assert result.cleanup.selector_closed
        assert not result.cleanup.complete
    finally:
        if result is not None and result.pid is not None:
            try:
                os.kill(result.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if descendant_pid is not None:
            try:
                os.kill(descendant_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_invalid_environment_is_rejected_before_spawn(tmp_path: Path) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    environment.pop("TZ")
    now = time.monotonic()
    with pytest.raises(supervisor.SupervisorInputError, match="exactly five"):
        supervisor.supervise_process(
            (PYTHON, "-c", "pass"),
            cwd=cwd,
            environment=environment,
            global_deadline=now + 1.0,
            cleanup_deadline=now + 2.0,
        )


def test_environment_surrogate_is_normalized_to_input_error(tmp_path: Path) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    environment["HOME"] += "\ud800"
    now = time.monotonic()
    with pytest.raises(supervisor.SupervisorInputError, match="UTF-8"):
        supervisor.supervise_process(
            (PYTHON, "-c", "pass"),
            cwd=cwd,
            environment=environment,
            global_deadline=now + 1.0,
            cleanup_deadline=now + 2.0,
        )


def test_wrong_cwd_mode_is_rejected_before_spawn(tmp_path: Path) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    cwd.chmod(0o755)
    now = time.monotonic()
    with pytest.raises(supervisor.SupervisorInputError, match="cwd must have mode 0700"):
        supervisor.supervise_process(
            (PYTHON, "-c", "pass"),
            cwd=cwd,
            environment=environment,
            global_deadline=now + 1.0,
            cleanup_deadline=now + 2.0,
        )


def test_wrong_home_mode_is_rejected_before_spawn(tmp_path: Path) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    Path(environment["HOME"]).chmod(0o755)
    now = time.monotonic()
    with pytest.raises(supervisor.SupervisorInputError, match="HOME must have mode 0700"):
        supervisor.supervise_process(
            (PYTHON, "-c", "pass"),
            cwd=cwd,
            environment=environment,
            global_deadline=now + 1.0,
            cleanup_deadline=now + 2.0,
        )


def test_spawn_failure_is_a_structured_not_started_result(tmp_path: Path) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    invalid_executable = cwd / "invalid-executable"
    invalid_executable.write_bytes(b"not an executable format\n")
    invalid_executable.chmod(0o700)
    now = time.monotonic()
    result = supervisor.supervise_process(
        (os.fspath(invalid_executable),),
        cwd=cwd,
        environment=environment,
        global_deadline=now + 2.0,
        cleanup_deadline=now + 3.0,
        limits=_limits(),
    )
    assert result.issues == (supervisor.ISSUE_SPAWN_FAILURE,)
    assert result.pid is None
    assert result.returncode is None
    assert result.spawn_error_type == "OSError"
    assert type(result.spawn_errno) is int
    assert not result.cleanup.process_started
    assert result.cleanup.selector_closed
    assert result.cleanup.complete


def test_already_expired_global_deadline_does_not_spawn(tmp_path: Path) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    result = supervisor.supervise_process(
        (PYTHON, "-c", "raise SystemExit(99)"),
        cwd=cwd,
        environment=environment,
        global_deadline=now - 0.001,
        cleanup_deadline=now + 1.0,
        limits=_limits(),
    )
    assert result.issues == (supervisor.ISSUE_GLOBAL_DEADLINE,)
    assert result.pid is None
    assert result.returncode is None
    assert not result.cleanup.process_started
    assert result.cleanup.complete


def test_short_global_deadline_interrupts_a_started_process(tmp_path: Path) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    result = supervisor.supervise_process(
        (PYTHON, "-I", "-B", "-c", "import time; time.sleep(60)"),
        cwd=cwd,
        environment=environment,
        global_deadline=now + 0.15,
        cleanup_deadline=now + 1.0,
        limits=_limits(process_seconds=3.0),
    )
    assert supervisor.ISSUE_GLOBAL_DEADLINE in result.issues
    assert result.pid is not None
    assert result.cleanup.term_signal_sent
    _assert_complete_started_cleanup(result)


def test_caller_supplied_phase_end_boundary_is_preserved_without_an_adapter(
    tmp_path: Path,
) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    phase_end = now + 10.50
    outer_deadline = phase_end + 0.25
    work_deadline = phase_end - 10.0
    exact_contract_limits = supervisor.SupervisorLimits(
        stdout_bytes=4_096,
        stderr_bytes=4_096,
        process_seconds=0.30,
        term_grace_seconds=5.0,
        kill_wait_seconds=5.0,
        group_absence_seconds=5.0,
        pipe_drain_seconds=5.0,
        select_interval_seconds=0.01,
    )
    result = supervisor.supervise_process(
        (PYTHON, "-I", "-B", "-c", "print('boundary')"),
        cwd=cwd,
        environment=environment,
        global_deadline=work_deadline,
        cleanup_deadline=phase_end,
        limits=exact_contract_limits,
    )
    assert result.global_deadline == phase_end - 10.0
    assert result.cleanup_deadline == phase_end
    assert result.cleanup_deadline <= outer_deadline
    assert exact_contract_limits.term_grace_seconds == 5.0
    assert exact_contract_limits.kill_wait_seconds == 5.0
    assert result.issues == ()
    _assert_complete_started_cleanup(result)


def test_all_cleanup_waits_are_clipped_to_one_absolute_deadline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(supervisor, "_group_exists", lambda _pgid: True)
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    absolute_cleanup_deadline = now + 0.28
    result = supervisor.supervise_process(
        (PYTHON, "-I", "-B", "-c", "import time; time.sleep(60)"),
        cwd=cwd,
        environment=environment,
        global_deadline=now + 0.08,
        cleanup_deadline=absolute_cleanup_deadline,
        limits=_limits(
            process_seconds=2.0,
            term_grace_seconds=0.03,
            kill_wait_seconds=5.0,
            group_absence_seconds=5.0,
            pipe_drain_seconds=5.0,
        ),
    )
    assert result.finished_monotonic <= absolute_cleanup_deadline + 0.08
    assert supervisor.ISSUE_GLOBAL_DEADLINE in result.issues
    assert supervisor.ISSUE_CLEANUP_DEADLINE in result.issues
    assert supervisor.ISSUE_CLEANUP_FAILURE in result.issues
    assert result.cleanup.kill_phase_deadline_reached
    assert result.cleanup.parent_pipe_fds_closed
    assert result.cleanup.selector_closed


def test_injected_zero_term_grace_still_kills_and_reaps(tmp_path: Path) -> None:
    result, _cwd = _run(
        tmp_path,
        "import time; time.sleep(60)",
        limits=_limits(process_seconds=0.15, term_grace_seconds=0.0),
    )
    assert supervisor.ISSUE_PROCESS_TIMEOUT in result.issues
    assert result.cleanup.term_signal_sent
    assert result.cleanup.kill_signal_sent or result.returncode == -signal.SIGTERM
    _assert_complete_started_cleanup(result)


@pytest.mark.parametrize(
    "argv",
    [
        ("python3", "-c", "pass"),
        (),
        ("bad\x00path",),
    ],
)
def test_nonfixed_argv_is_rejected(tmp_path: Path, argv: tuple[str, ...]) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    with pytest.raises(supervisor.SupervisorInputError):
        supervisor.supervise_process(
            argv,
            cwd=cwd,
            environment=environment,
            global_deadline=now + 1.0,
            cleanup_deadline=now + 2.0,
        )


def test_argv_surrogate_is_normalized_to_input_error(tmp_path: Path) -> None:
    cwd, environment = _private_launch_root(tmp_path)
    now = time.monotonic()
    with pytest.raises(supervisor.SupervisorInputError, match="UTF-8"):
        supervisor.supervise_process(
            (PYTHON, "\ud800"),
            cwd=cwd,
            environment=environment,
            global_deadline=now + 1.0,
            cleanup_deadline=now + 2.0,
        )
