"""Round-144 attacks on selector isolation, bindings, and fail-closed status."""

from __future__ import annotations

import os
import select
import signal
import subprocess
import sys
import time
from fractions import Fraction

import f1_to_f2_common_observable_selector_v2 as selector
import pytest


def _valid_cp_request() -> bytes:
    return selector._cp_worker_request_bytes(
        1_000,
        Fraction(1, 200),
        Fraction(3, 200),
        Fraction(1, 800),
        selector._cp_worker_identity(),
    )


def _valid_power_request(**bindings: str | None) -> bytes:
    parameters = selector._binomial_power_parameters(
        1_000,
        Fraction(1, 10),
        0,
        120,
        Fraction(9, 10),
        "lt",
    )
    return selector._power_worker_request_bytes(
        "binomial_decision",
        parameters,
        selector._cp_worker_identity(),
        **bindings,
    )


def test_round144_internal_worker_functions_reject_parent_calls() -> None:
    with pytest.raises(selector.SelectorError) as cp_error:
        selector._run_internal_cp_worker(_valid_cp_request())
    assert cp_error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"

    with pytest.raises(selector.SelectorError) as power_error:
        selector._run_internal_power_worker(_valid_power_request())
    assert power_error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"


@pytest.mark.parametrize("mode", ("--internal-cp-worker", "--internal-power-worker"))
def test_round144_hidden_cli_rejects_launch_without_inherited_capability(mode: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-I", str(selector.Path(selector.__file__).resolve()), mode],
        input=b"{}\n",
        capture_output=True,
        check=False,
        timeout=10,
        env={"PATH": os.environ.get("PATH", "")},
    )
    assert completed.returncode != 0
    assert completed.stdout == b""
    assert b"worker launch capability is absent" in completed.stderr


def test_round144_power_request_binds_schedule_and_row_identity() -> None:
    schedule_sha256 = "a" * 64
    raw = _valid_power_request(assertion_id="basin_floor:01", schedule_sha256=schedule_sha256)
    request = selector.strict_load_canonical_json(raw)
    assert request["assertion_id"] == "basin_floor:01"
    assert request["schedule_sha256"] == schedule_sha256

    with pytest.raises(selector.SelectorError) as partial:
        _valid_power_request(assertion_id="basin_floor:01")
    assert partial.value.reason == "HOLD_POWER_BOUNDARY"


def test_round144_malformed_decision_type_holds_without_typeerror() -> None:
    interval = selector._mp_interval_exact(Fraction(3, 4), 256).canonical_payload()
    malformed = {
        "attempts": [{"interval": interval, "precision_bits": 256}],
        "decision": [],
        "precision_bits": 256,
    }
    with pytest.raises(selector.SelectorError) as error:
        selector._validate_power_decision_result(malformed, Fraction(1, 2), "gt")
    assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"


def test_round144_failed_assertion_cannot_return_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = selector.synthetic_power_resource_fixture(100_000)
    schedule_sha256 = selector.sha256_bytes(selector.powered_assertion_schedule_bytes(fixture))
    calls = 0

    def failed_worker(
        operation: str, parameters: dict[str, object], **bindings: object
    ) -> tuple[dict[str, object], int, dict[str, object]]:
        del operation, parameters
        nonlocal calls
        calls += 1
        return (
            {"decision": "FAIL"},
            1,
            {
                "assertion_id": bindings["assertion_id"],
                "schedule_sha256": bindings["schedule_sha256"],
            },
        )

    monkeypatch.setattr(selector, "_isolated_power_decision", failed_worker)
    with pytest.raises(selector.SelectorError) as error:
        selector.execute_powered_assertion_schedule(
            fixture, expected_schedule_sha256=schedule_sha256
        )
    assert error.value.reason == "HOLD_POWER_BOUNDARY"
    assert calls == 1


def test_round144_every_schedule_row_has_a_bound_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = selector.synthetic_power_resource_fixture(100_000)
    schedule_sha256 = selector.sha256_bytes(selector.powered_assertion_schedule_bytes(fixture))

    def passing_worker(
        operation: str, parameters: dict[str, object], **bindings: object
    ) -> tuple[dict[str, object], int, dict[str, object]]:
        del parameters
        return (
            {"decision": "PASS"},
            2,
            {
                "assertion_id": bindings["assertion_id"],
                "operation": operation,
                "schedule_sha256": bindings["schedule_sha256"],
            },
        )

    monkeypatch.setattr(selector, "_isolated_power_decision", passing_worker)
    result = selector.execute_powered_assertion_schedule(
        fixture, expected_schedule_sha256=schedule_sha256
    )
    receipts = result["assertion_receipts"]
    assert len(receipts) == 68
    assert tuple(row["assertion_id"] for row in receipts) == tuple(
        assertion_id for _family, assertion_id, _operation in selector.POWER_ASSERTION_LAYOUT
    )
    assert {row["schedule_sha256"] for row in receipts} == {schedule_sha256}
    assert result["status"] == "PASS_POWERED_ASSERTION_EXECUTION"
    assert result["schedule_kind"] == "CALLER_SUPPLIED_UNCLASSIFIED"


def test_round144_lock_path_is_fixed_and_tmpdir_independent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: selector.Path
) -> None:
    original = selector.SPECIAL_WORKER_LOCK_PATH
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    with selector._special_worker_slot(time.monotonic() + 1):
        assert selector.SPECIAL_WORKER_LOCK_PATH == original
        assert original.parent == selector.Path("/tmp").resolve() / (
            f"encounter-selector-v2-special-worker-{os.getuid()}"
        )


def test_round144_thread_queue_timeout_is_fail_closed() -> None:
    assert selector._SPECIAL_WORKER_THREAD_SLOT.acquire(timeout=1)
    try:
        with pytest.raises(selector.SelectorError) as error:
            with selector._special_worker_thread_slot(time.monotonic() + 0.01):
                pytest.fail("a second worker entered a saturated queue")
        assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"
    finally:
        selector._SPECIAL_WORKER_THREAD_SLOT.release()


def test_round144_cache_key_rejects_cross_process_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selector._isolated_cp_acceptance_set.cache_clear()
    monkeypatch.setattr(
        selector,
        "_run_special_worker_subprocess",
        lambda *_args, **_kwargs: pytest.fail("a worker ran after a PID mismatch"),
    )
    with pytest.raises(selector.SelectorError) as error:
        selector._isolated_cp_acceptance_set(
            1_000,
            1,
            200,
            3,
            200,
            1,
            800,
            *selector._cp_worker_identity(),
            os.getpid() + 1,
        )
    assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"


def test_round144_runtime_snapshot_hashes_exact_parsed_bytes(tmp_path: selector.Path) -> None:
    path = tmp_path / "snapshot.json"
    raw = selector.canonical_json_bytes({"schema_version": 1, "value": "frozen"})
    path.write_bytes(raw)
    snapshot = selector._read_ordinary_file_snapshot(path, "snapshot changed", maximum_bytes=128)
    assert snapshot == raw
    assert selector.sha256_bytes(snapshot) == selector.sha256_bytes(raw)
    assert selector.strict_load_canonical_json(snapshot)["value"] == "frozen"


@pytest.mark.skipif(not hasattr(os, "fork"), reason="requires POSIX fork")
def test_round145_atfork_closes_both_tracked_capability_pipe_ends() -> None:
    capability_read, capability_write = os.pipe()
    report_read, report_write = os.pipe()
    with selector._SPECIAL_WORKER_DESCRIPTOR_GUARD:
        selector._SPECIAL_WORKER_OPEN_DESCRIPTORS.update({capability_read, capability_write})
    child_pid = os.fork()
    if child_pid == 0:
        os.close(report_read)
        closed = []
        for descriptor in (capability_read, capability_write):
            try:
                os.fstat(descriptor)
            except OSError:
                closed.append(True)
            else:
                closed.append(False)
        os.write(report_write, b"PASS" if all(closed) else b"FAIL")
        os._exit(0)

    os.close(report_write)
    try:
        assert os.read(report_read, 4) == b"PASS"
        _waited_pid, wait_status = os.waitpid(child_pid, 0)
        assert os.waitstatus_to_exitcode(wait_status) == 0
    finally:
        os.close(report_read)
        with selector._SPECIAL_WORKER_DESCRIPTOR_GUARD:
            selector._SPECIAL_WORKER_OPEN_DESCRIPTORS.difference_update(
                {capability_read, capability_write}
            )
        os.close(capability_read)
        os.close(capability_write)


def test_round145_worker_rejects_unrelated_inherited_lock(tmp_path: selector.Path) -> None:
    unrelated_path = tmp_path / "unrelated.lock"
    descriptor = os.open(unrelated_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        with pytest.raises(selector.SelectorError) as error:
            selector._validate_inherited_worker_lock(descriptor)
        assert error.value.reason == "HOLD_SPECIAL_FUNCTION_DAG"
    finally:
        os.close(descriptor)


def test_round145_two_parents_never_have_two_resident_power_workers() -> None:
    script = f"""
import sys
from fractions import Fraction
sys.path.insert(0, {str(selector.HERE)!r})
import f1_to_f2_common_observable_selector_v2 as selector
result = selector.binomial_precision_ladder_decision(
    1000, Fraction(1, 10), 0, 120, Fraction(9, 10), 'lt'
)
assert result['decision'] in {{'PASS', 'FAIL'}}
"""
    parents = [
        subprocess.Popen(
            [sys.executable, "-I", "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _index in range(2)
    ]
    maximum_workers = 0
    source = str(selector.Path(selector.__file__).resolve())
    deadline = time.monotonic() + 30
    while any(parent.poll() is None for parent in parents):
        listing = subprocess.check_output(["/bin/ps", "-axo", "command="], text=True)
        maximum_workers = max(
            maximum_workers,
            sum(
                "--internal-power-worker" in line and source in line
                for line in listing.splitlines()
            ),
        )
        if time.monotonic() >= deadline:
            for parent in parents:
                parent.kill()
            pytest.fail("independent selector parents timed out")
        time.sleep(0.01)
    for parent in parents:
        _stdout, stderr = parent.communicate(timeout=1)
        assert parent.returncode == 0, stderr.decode(errors="replace")
    assert maximum_workers == 1


@pytest.mark.skipif(not hasattr(signal, "SIGSTOP"), reason="requires POSIX stop signals")
def test_round145_orphan_worker_retains_lock_after_parent_death() -> None:
    """A killed parent must not release the lock while its worker is resident."""

    source = str(selector.Path(selector.__file__).resolve())
    ordinary_script = f"""
import sys
from fractions import Fraction
sys.path.insert(0, {str(selector.HERE)!r})
import f1_to_f2_common_observable_selector_v2 as selector
result = selector.binomial_precision_ladder_decision(
    1000, Fraction(1, 10), 0, 120, Fraction(9, 10), 'lt'
)
assert result['decision'] in {{'PASS', 'FAIL'}}
"""
    stopped_worker_script = f"""
import array
import fcntl
import os
import signal
import subprocess
import sys
import termios
import time
from fractions import Fraction
sys.path.insert(0, {str(selector.HERE)!r})
import f1_to_f2_common_observable_selector_v2 as selector
real_popen = selector.subprocess.Popen
def stopped_run(command, **kwargs):
    assert kwargs['capture_output'] is True
    process = real_popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=kwargs['env'],
        pass_fds=kwargs['pass_fds'],
    )
    print('SPAWNED ' + str(process.pid), flush=True)
    capability_descriptor = kwargs['pass_fds'][0]
    authorization_deadline = time.monotonic() + 2
    while True:
        unread = array.array('i', [0])
        fcntl.ioctl(
            capability_descriptor, termios.FIONREAD, unread, True
        )
        if unread[0] == 0:
            break
        assert unread[0] == 32
        assert process.poll() is None
        assert time.monotonic() < authorization_deadline
        time.sleep(0.001)
    stop_deadline = time.monotonic() + 2
    while True:
        os.kill(process.pid, signal.SIGSTOP)
        waited_pid, wait_status = os.waitpid(
            process.pid, os.WUNTRACED | os.WNOHANG
        )
        if waited_pid == process.pid:
            assert os.WIFSTOPPED(wait_status)
            assert os.WSTOPSIG(wait_status) == signal.SIGSTOP
            break
        assert waited_pid == 0
        assert time.monotonic() < stop_deadline
        time.sleep(0.001)
    print('STOPPED ' + str(process.pid), flush=True)
    stdout, stderr = process.communicate(
        input=kwargs['input'], timeout=kwargs['timeout']
    )
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
selector.subprocess.run = stopped_run
selector.binomial_precision_ladder_decision(
    1000, Fraction(1, 10), 0, 120, Fraction(9, 10), 'lt'
)
"""

    def active_workers() -> list[tuple[int, int]]:
        listing = subprocess.check_output(
            ["/bin/ps", "-axo", "pid=,ppid=,stat=,command="], text=True
        )
        rows = []
        for line in listing.splitlines():
            fields = line.strip().split(None, 3)
            if len(fields) != 4:
                continue
            pid_text, parent_text, process_status, command = fields
            if (
                not process_status.startswith("Z")
                and "--internal-power-worker" in command
                and source in command
            ):
                rows.append((int(pid_text), int(parent_text)))
        return rows

    first_parent: subprocess.Popen[bytes] | None = None
    second_parent: subprocess.Popen[bytes] | None = None
    orphan_pid: int | None = None
    try:
        first_parent = subprocess.Popen(
            [sys.executable, "-I", "-c", stopped_worker_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert first_parent.stdout is not None
        spawned_ready, _writable, _exceptional = select.select(
            [first_parent.stdout], [], [], 10
        )
        assert spawned_ready, "first parent did not report its spawned worker"
        spawned_line = first_parent.stdout.readline().decode("ascii").strip().split()
        assert len(spawned_line) == 2 and spawned_line[0] == "SPAWNED"
        orphan_pid = int(spawned_line[1])
        stopped_ready, _writable, _exceptional = select.select(
            [first_parent.stdout], [], [], 10
        )
        assert stopped_ready, "first parent did not confirm its stopped worker"
        stopped_line = first_parent.stdout.readline().decode("ascii").strip().split()
        if stopped_line != ["STOPPED", str(orphan_pid)]:
            first_parent.wait(timeout=1)
            assert first_parent.stderr is not None
            parent_stderr = first_parent.stderr.read().decode(errors="replace")
            pytest.fail(
                f"invalid stopped-worker report {stopped_line!r}; "
                f"parent stderr: {parent_stderr}"
            )
        status_deadline = time.monotonic() + 0.5
        orphan_status = ""
        while not orphan_status.startswith("T") and time.monotonic() < status_deadline:
            orphan_status = subprocess.check_output(
                ["/bin/ps", "-o", "stat=", "-p", str(orphan_pid)], text=True
            ).strip()
            if not orphan_status.startswith("T"):
                time.sleep(0.001)
        assert orphan_status.startswith("T"), (
            f"reported worker was not confirmed stopped: {orphan_status!r}"
        )
        assert any(pid == orphan_pid for pid, _ppid in active_workers()), (
            "reported stopped worker was not resident"
        )

        first_parent.kill()
        first_parent.wait(timeout=2)
        second_parent = subprocess.Popen(
            [sys.executable, "-I", "-c", ordinary_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        observation_deadline = time.monotonic() + 0.5
        while time.monotonic() < observation_deadline:
            assert second_parent.poll() is None, (
                "second parent completed while the stopped orphan still held the lock"
            )
            assert all(ppid != second_parent.pid for _pid, ppid in active_workers()), (
                "second parent spawned a worker while the orphan was resident"
            )
            time.sleep(0.01)

        os.kill(orphan_pid, signal.SIGKILL)
        orphan_pid = None
        _stdout, stderr = second_parent.communicate(timeout=10)
        assert second_parent.returncode == 0, stderr.decode(errors="replace")
    finally:
        if orphan_pid is not None:
            try:
                os.kill(orphan_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        for parent in (first_parent, second_parent):
            if parent is not None and parent.poll() is None:
                parent.kill()
                parent.wait(timeout=2)
