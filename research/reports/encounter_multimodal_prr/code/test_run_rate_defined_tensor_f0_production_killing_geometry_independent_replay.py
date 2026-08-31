from __future__ import annotations

import ast
import inspect
import json
import os
import stat
import sys
import time
from pathlib import Path

import pytest
import run_rate_defined_tensor_f0_production_killing_geometry_independent_replay as replay

REPORT_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_ROOT = REPORT_ROOT / "artifacts/data/physical_production_killing_geometry_v1"


@pytest.fixture(scope="module")
def frozen_snapshot() -> replay.Snapshot:
    runtime_chain = replay._lstat_chain(Path(sys.executable))
    extension_chain = replay._gmpy2_link_chain()
    return replay._snapshot(
        replay._component_specs(
            REPORT_ROOT,
            BUNDLE_ROOT,
            None,
            runtime_chain,
            extension_chain,
        ),
        staged=False,
    )


def _receipt_target(path: Path) -> replay.ReceiptTarget:
    metadata = os.lstat(path.parent)
    return replay.ReceiptTarget(path, replay._directory_identity(metadata))


def _semantic(snapshot: replay.Snapshot) -> dict[str, object]:
    frozen = {
        "authority_sha256": snapshot.component("authority_bytes")["sha256"],
        "configuration_sha256": snapshot.component("control_free_configuration_bytes")["sha256"],
        "design_sha256": snapshot.component("design_bytes")["sha256"],
        "f0_core_sha256": snapshot.component("f0_core_source")["sha256"],
        "initial_stream_source_sha256": snapshot.component("initial_stream_source")["sha256"],
        "operation_model_sha256": snapshot.component("operation_model_bytes")["sha256"],
        "partition_bundle_sha256": "1" * 64,
        "partition_tree_sha256": "2" * 64,
        "producer_sha256": snapshot.component("producer_source")["sha256"],
        "producer_test_sha256": snapshot.component("producer_test_source")["sha256"],
    }
    flags = dict(replay.REQUIRED_SEMANTIC_FLAGS)
    flags.update(replay.ADDITIONAL_SEMANTIC_FLAGS)
    return {
        "candidate": {
            "bundle_sha256": "3" * 64,
            "factorization_contract_sha256": "4" * 64,
            "family_relation_sha256": "5" * 64,
            "partition_reference_graph_sha256": "6" * 64,
            "tree_sha256": "7" * 64,
        },
        "contact_summary": {},
        "flags": flags,
        "frozen_sources": frozen,
        "independent_partition_semantic_sha256s": [],
        "precision_bits": {"primary": 384, "sentinel": 512},
        "runtime": snapshot.body["runtime_versions"],
        "schema": replay.CHILD_SEMANTIC_SCHEMA,
        "status": replay.CHILD_PASS_STATUS,
        "support_policy_digests": {
            "flat_tail_M4_upper_sha256": "8" * 64,
            "flat_tail_bump_upper_sha256": "9" * 64,
            "flat_tail_policy_sha256": "a" * 64,
            "paired_simpson_policy_sha256": "b" * 64,
        },
        "support_summary": {},
        "verifier_staged_file_sha256_at_receipt": snapshot.component("independent_verifier_source")[
            "sha256"
        ],
    }


def _run_record(
    *,
    run_index: int,
    pid: int,
    semantic_raw: bytes,
    snapshot_digest: str,
) -> dict[str, object]:
    cleanup = {key: True for key in replay.CLEANUP_KEYS}
    phases = {key: snapshot_digest for key in replay.SNAPSHOT_PHASE_KEYS}
    return {
        "cleanup": cleanup,
        "exit_code": 0,
        "launch_nonce": f"{run_index + 1:064x}",
        "observation_byte_length": 100,
        "observation_sha256": "c" * 64,
        "pgid": pid,
        "pid": pid,
        "run_index": run_index,
        "semantic_receipt_byte_length": len(semantic_raw),
        "semantic_receipt_sha256": replay._sha256(semantic_raw),
        "snapshot_sha256s": phases,
        "stderr_byte_length": 0,
        "stderr_sha256": replay._sha256(b""),
        "stdout_byte_length": 100,
        "stdout_sha256": "d" * 64,
    }


def _write_script(path: Path, source: str) -> None:
    path.write_text(source, encoding="ascii")


def _capture_script(
    tmp_path: Path,
    source: str,
    *,
    deadline_seconds: float = 10.0,
) -> replay.CaptureResult:
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "home").mkdir()
    (stage / "tmp").mkdir()
    script = tmp_path / "child_fixture.py"
    _write_script(script, source)
    return replay._capture_child(
        (sys.executable, "-I", "-B", os.fspath(script)),
        cwd=stage,
        environment=replay._child_environment(stage),
        global_deadline=time.monotonic() + deadline_seconds,
    )


def test_frozen_operation_source_runtime_and_no_network_imports_are_exact(
    frozen_snapshot: replay.Snapshot,
) -> None:
    replay._operation_model_preflight(REPORT_ROOT)
    assert replay._sha256((REPORT_ROOT / replay.OPERATION_MODEL_PATH).read_bytes()) == (
        replay.OPERATION_MODEL_SHA256
    )
    assert frozen_snapshot.component("independent_verifier_source")["sha256"] == (
        replay.EXPECTED_VERIFIER_SHA256
    )
    extension = replay._gmpy2_link_chain().final_target
    assert extension.name.endswith(".so")
    assert frozen_snapshot.component("gmpy2_extension")["sha256"] == replay._sha256(
        extension.read_bytes()
    )
    source = Path(replay.__file__).read_text("utf-8")
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert not imported & {"socket", "requests", "urllib", "http", "ftplib"}


def test_snapshot_has_exact_thirteen_domain_separated_components(
    frozen_snapshot: replay.Snapshot,
) -> None:
    assert [item["component"] for item in frozen_snapshot.body["components"]] == list(
        replay.COMPONENT_ORDER
    )
    assert frozen_snapshot.digest == replay._sha256(replay.SNAPSHOT_DOMAIN + frozen_snapshot.raw)
    assert replay._canonical_json_bytes(frozen_snapshot.body) == frozen_snapshot.raw
    for component in ("candidate_tree", "accepted_partition_tree"):
        record = frozen_snapshot.component(component)
        assert record["directories"][0] == "."
        assert record["directories"] == sorted(record["directories"])
        assert [item["path"] for item in record["files"]] == sorted(
            item["path"] for item in record["files"]
        )


def test_byte_copy_stage_has_no_hardlinks_is_read_only_and_snapshot_identical(
    frozen_snapshot: replay.Snapshot,
) -> None:
    runtime_chain = replay._lstat_chain(Path(sys.executable))
    extension_chain = replay._gmpy2_link_chain()
    stage = replay._new_stage((REPORT_ROOT, BUNDLE_ROOT), 0)
    try:
        specs = replay._component_specs(
            REPORT_ROOT,
            BUNDLE_ROOT,
            stage,
            runtime_chain,
            extension_chain,
        )
        replay._copy_staged_components(specs, frozen_snapshot)
        post_copy = replay._snapshot(specs, staged=True)
        assert post_copy.raw == frozen_snapshot.raw
        first_file = frozen_snapshot.component("candidate_tree")["files"][0]["path"]
        origin = BUNDLE_ROOT / first_file
        staged = stage / "inputs/candidate_tree" / first_file
        assert (os.stat(origin).st_dev, os.stat(origin).st_ino) != (
            os.stat(staged).st_dev,
            os.stat(staged).st_ino,
        )
        assert os.stat(staged).st_nlink == 1
        replay._make_inputs_read_only(stage / "inputs")
        prelaunch = replay._snapshot(
            specs,
            staged=True,
            require_read_only=True,
        )
        assert prelaunch.raw == frozen_snapshot.raw
        assert not (os.stat(staged).st_mode & 0o222)
    finally:
        assert replay._remove_stage(stage)


def test_directory_signature_change_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "tree"
    root.mkdir()
    (root / "value.bin").write_bytes(b"stable")
    original = replay._directory_signature
    calls = 0

    def changed(path: Path):
        nonlocal calls
        result = original(path)
        if path == root:
            calls += 1
            if calls >= 2:
                identity = list(result[0])
                identity[-1] += 1
                return tuple(identity), result[1]
        return result

    monkeypatch.setattr(replay, "_directory_signature", changed)
    with pytest.raises(replay.ReplayHold) as caught:
        replay._tree_record("candidate_tree", root)
    assert caught.value.status == replay.HOLD_TREE


def test_new_stage_mid_creation_failure_removes_private_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: list[Path] = []
    real_mkdtemp = replay.tempfile.mkdtemp
    real_mkdir = Path.mkdir

    def tracked_mkdtemp(*args, **kwargs):
        path = Path(real_mkdtemp(*args, **kwargs))
        created.append(path)
        return os.fspath(path)

    def fail_tmp(self: Path, *args, **kwargs):
        if self.name == "tmp" and self.parent in created:
            raise OSError("fixture mkdir failure")
        return real_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(replay.tempfile, "mkdtemp", tracked_mkdtemp)
    monkeypatch.setattr(Path, "mkdir", fail_tmp)
    with pytest.raises(replay.ReplayHold) as caught:
        replay._new_stage((tmp_path,), 0)
    assert caught.value.status == replay.HOLD_SOURCE
    assert created and all(not os.path.lexists(path) for path in created)


def test_capture_uses_exact_five_key_parent_mapping_and_observes_both_eofs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_environment: dict[str, str] = {}
    real_popen = replay.subprocess.Popen

    def recording_popen(*args, **kwargs):
        captured_environment.update(kwargs["env"])
        return real_popen(*args, **kwargs)

    monkeypatch.setattr(replay.subprocess, "Popen", recording_popen)
    result = _capture_script(
        tmp_path,
        "import sys\nsys.stdout.buffer.write(b'ack')\n",
    )
    assert set(captured_environment) == {"HOME", "LANG", "LC_ALL", "TMPDIR", "TZ"}
    assert len(captured_environment) == 5
    assert result.exit_code == 0
    assert result.stdout == b"ack"
    assert result.stderr == b""
    assert result.issue_status is None
    assert all(value for key, value in result.cleanup.items() if key != "stage_absent")


def test_selector_constructor_failure_occurs_before_popen(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    popen_called = False

    def fail_selector():
        raise OSError("fixture selector constructor failure")

    def observe_popen(*args, **kwargs):
        nonlocal popen_called
        popen_called = True
        raise AssertionError("Popen must not run")

    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "home").mkdir()
    (stage / "tmp").mkdir()
    monkeypatch.setattr(replay.selectors, "DefaultSelector", fail_selector)
    monkeypatch.setattr(replay.subprocess, "Popen", observe_popen)
    with pytest.raises(replay.ReplayHold) as caught:
        replay._capture_child(
            (sys.executable, "-c", "pass"),
            cwd=stage,
            environment=replay._child_environment(stage),
            global_deadline=time.monotonic() + 5,
        )
    assert caught.value.status == replay.HOLD_REPEAT
    assert popen_called is False


def test_expired_global_deadline_is_checked_immediately_before_popen(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    popen_called = False

    def observe_popen(*args, **kwargs):
        nonlocal popen_called
        popen_called = True
        raise AssertionError("Popen must not run after the global deadline")

    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "home").mkdir()
    (stage / "tmp").mkdir()
    monkeypatch.setattr(replay.subprocess, "Popen", observe_popen)
    with pytest.raises(replay.ReplayHold) as caught:
        replay._capture_child(
            (sys.executable, "-c", "pass"),
            cwd=stage,
            environment=replay._child_environment(stage),
            global_deadline=time.monotonic() - 1,
        )
    assert caught.value.status == replay.HOLD_TIMEOUT
    assert popen_called is False


def test_execute_run_rechecks_reserve_after_staging_before_capture() -> None:
    source = inspect.getsource(replay._execute_run)
    read_only = source.index("_make_inputs_read_only")
    reserve_check = source.index("_prelaunch_time_check", read_only)
    child_start = source.index("child_started", reserve_check)
    capture = source.index("_capture_child", child_start)
    assert read_only < reserve_check < child_start < capture


def test_selector_register_failure_still_reaps_and_closes_process_group(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_selector = replay.selectors.DefaultSelector

    class RegisterFailureSelector:
        def __init__(self):
            self.inner = real_selector()

        def register(self, *args, **kwargs):
            raise OSError("fixture register failure")

        def unregister(self, *args, **kwargs):
            return self.inner.unregister(*args, **kwargs)

        def select(self, *args, **kwargs):
            return self.inner.select(*args, **kwargs)

        def get_map(self):
            return self.inner.get_map()

        def close(self):
            return self.inner.close()

    monkeypatch.setattr(replay.selectors, "DefaultSelector", RegisterFailureSelector)
    result = _capture_script(tmp_path, "import time\ntime.sleep(30)\n")
    assert result.issue_status == replay.HOLD_REPEAT
    assert result.cleanup["direct_child_reaped"] is True
    assert result.cleanup["process_group_absent"] is True
    assert result.cleanup["stdout_eof_observed"] is True
    assert result.cleanup["stderr_eof_observed"] is True
    assert result.cleanup["parent_pipe_fds_closed"] is True
    assert result.cleanup["selector_closed"] is True
    assert replay._group_exists(result.pid) is False


def test_output_cap_overflow_terminates_and_cleans_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(replay, "MAX_CHILD_ACK_BYTES", 16)
    result = _capture_script(
        tmp_path,
        "import sys,time\nsys.stdout.buffer.write(b'x'*4096)\nsys.stdout.flush()\ntime.sleep(30)\n",
    )
    assert result.issue_status == replay.HOLD_REPEAT
    assert len(result.stdout) == 17
    assert all(value for key, value in result.cleanup.items() if key != "stage_absent")


def test_complete_child_wire_and_nonpromotion_flags_are_validated(
    tmp_path: Path,
    frozen_snapshot: replay.Snapshot,
) -> None:
    semantic = _semantic(frozen_snapshot)
    semantic_raw = replay._canonical_json_bytes(semantic)
    verifier_sha = frozen_snapshot.component("independent_verifier_source")["sha256"]
    pid = 43_210
    nonce = "e" * 64
    observation = {
        "elapsed_monotonic_ns": 1,
        "launch_nonce": nonce,
        "peak_rss_bytes": 2,
        "pgid": pid,
        "pid": pid,
        "ppid": os.getpid(),
        "run_index": 0,
        "schema": replay.CHILD_OBSERVATION_SCHEMA,
        "semantic_receipt_byte_length": len(semantic_raw),
        "semantic_receipt_sha256": replay._sha256(semantic_raw),
        "status": replay.CHILD_PASS_STATUS,
        "verifier_staged_file_sha256_at_observation": verifier_sha,
    }
    observation_raw = replay._canonical_json_bytes(observation)
    ack = {
        "launch_nonce": nonce,
        "observation_byte_length": len(observation_raw),
        "observation_sha256": replay._sha256(observation_raw),
        "run_index": 0,
        "schema": replay.CHILD_ACK_SCHEMA,
        "semantic_receipt_byte_length": len(semantic_raw),
        "semantic_receipt_sha256": replay._sha256(semantic_raw),
        "status": replay.CHILD_PASS_STATUS,
    }
    semantic_path = tmp_path / "semantic.json"
    observation_path = tmp_path / "observation.json"
    semantic_path.write_bytes(semantic_raw)
    observation_path.write_bytes(observation_raw)
    capture = replay.CaptureResult(
        pid,
        0,
        replay._canonical_json_bytes(ack),
        b"",
        None,
        {key: True for key in replay.CLEANUP_KEYS},
    )
    validated = replay._validate_child_wire(
        capture=capture,
        semantic_path=semantic_path,
        observation_path=observation_path,
        nonce=nonce,
        run_index=0,
        snapshot=frozen_snapshot,
        verifier_sha256=verifier_sha,
    )
    assert validated[0] == semantic_raw
    assert validated[2] == observation_raw
    semantic["flags"]["f0_pass"] = True
    with pytest.raises(replay.ReplayHold) as caught:
        replay._validate_semantic(
            replay._canonical_json_bytes(semantic),
            snapshot=frozen_snapshot,
            verifier_sha256=verifier_sha,
        )
    assert caught.value.status == replay.HOLD_REPEAT


def test_bound_semantic_hold_wire_is_fully_validated_and_propagated(
    tmp_path: Path,
    frozen_snapshot: replay.Snapshot,
) -> None:
    status = replay.HOLD_SUPPORT
    semantic_raw = replay._canonical_json_bytes(
        {"schema": replay.CHILD_SEMANTIC_HOLD_SCHEMA, "status": status}
    )
    verifier_sha = frozen_snapshot.component("independent_verifier_source")["sha256"]
    pid = 43_211
    nonce = "f" * 64
    observation = {
        "elapsed_monotonic_ns": 1,
        "launch_nonce": nonce,
        "peak_rss_bytes": 2,
        "pgid": pid,
        "pid": pid,
        "ppid": os.getpid(),
        "run_index": 1,
        "schema": replay.CHILD_OBSERVATION_SCHEMA,
        "semantic_receipt_byte_length": len(semantic_raw),
        "semantic_receipt_sha256": replay._sha256(semantic_raw),
        "status": status,
        "verifier_staged_file_sha256_at_observation": verifier_sha,
    }
    observation_raw = replay._canonical_json_bytes(observation)
    ack = {
        "launch_nonce": nonce,
        "observation_byte_length": len(observation_raw),
        "observation_sha256": replay._sha256(observation_raw),
        "run_index": 1,
        "schema": replay.CHILD_ACK_SCHEMA,
        "semantic_receipt_byte_length": len(semantic_raw),
        "semantic_receipt_sha256": replay._sha256(semantic_raw),
        "status": status,
    }
    semantic_path = tmp_path / "hold-semantic.json"
    observation_path = tmp_path / "hold-observation.json"
    semantic_path.write_bytes(semantic_raw)
    observation_path.write_bytes(observation_raw)
    capture = replay.CaptureResult(
        pid,
        2,
        replay._canonical_json_bytes(ack),
        b"",
        None,
        {key: True for key in replay.CLEANUP_KEYS},
    )
    with pytest.raises(replay.ReplayHold) as caught:
        replay._validate_child_wire(
            capture=capture,
            semantic_path=semantic_path,
            observation_path=observation_path,
            nonce=nonce,
            run_index=1,
            snapshot=frozen_snapshot,
            verifier_sha256=verifier_sha,
        )
    assert caught.value.status == status


def test_canonical_wire_rejects_floats_and_bool_as_integer(
    frozen_snapshot: replay.Snapshot,
) -> None:
    with pytest.raises(replay.ReplayHold) as caught:
        replay._decode_canonical_object(
            replay._canonical_json_bytes({"value": 1.0}),
            maximum_bytes=1024,
        )
    assert caught.value.status == replay.HOLD_REPEAT
    semantic_raw = replay._canonical_json_bytes(_semantic(frozen_snapshot))
    observation = {
        "elapsed_monotonic_ns": 1,
        "launch_nonce": "f" * 64,
        "peak_rss_bytes": 2,
        "pgid": 10,
        "pid": 10,
        "ppid": os.getpid(),
        "run_index": True,
        "schema": replay.CHILD_OBSERVATION_SCHEMA,
        "semantic_receipt_byte_length": len(semantic_raw),
        "semantic_receipt_sha256": replay._sha256(semantic_raw),
        "status": replay.CHILD_PASS_STATUS,
        "verifier_staged_file_sha256_at_observation": replay.EXPECTED_VERIFIER_SHA256,
    }
    observation_raw = replay._canonical_json_bytes(observation)
    ack = {
        "launch_nonce": "f" * 64,
        "observation_byte_length": len(observation_raw),
        "observation_sha256": replay._sha256(observation_raw),
        "run_index": True,
        "schema": replay.CHILD_ACK_SCHEMA,
        "semantic_receipt_byte_length": len(semantic_raw),
        "semantic_receipt_sha256": replay._sha256(semantic_raw),
        "status": replay.CHILD_PASS_STATUS,
    }
    capture = replay.CaptureResult(
        10,
        0,
        replay._canonical_json_bytes(ack),
        b"",
        None,
        {key: True for key in replay.CLEANUP_KEYS},
    )
    with pytest.raises(replay.ReplayHold) as caught:
        replay._validate_observation_and_ack(
            semantic_raw=semantic_raw,
            observation_raw=observation_raw,
            stdout_raw=capture.stdout,
            capture=capture,
            nonce="f" * 64,
            run_index=1,
            verifier_sha256=replay.EXPECTED_VERIFIER_SHA256,
        )
    assert caught.value.status == replay.HOLD_REPEAT


def test_semantic_raw_bytes_and_distinct_pids_are_outer_acceptance_conditions(
    frozen_snapshot: replay.Snapshot,
) -> None:
    semantic = _semantic(frozen_snapshot)
    raw = replay._canonical_json_bytes(semantic)
    runs = [
        replay.RunResult(
            _run_record(
                run_index=index,
                pid=50_000 + index,
                semantic_raw=raw,
                snapshot_digest=frozen_snapshot.digest,
            ),
            raw,
            semantic,
        )
        for index in (0, 1)
    ]
    receipt = replay._build_outer_receipt(runs, frozen_snapshot)
    assert receipt["status"] == replay.OUTER_PASS_STATUS
    assert receipt["flags"]["full_binary_dependency_filesystem_closure"] is False
    assert receipt["flags"]["f0_pass"] is False
    runs[1].semantic_raw = raw + b" "
    with pytest.raises(replay.ReplayHold) as caught:
        replay._build_outer_receipt(runs, frozen_snapshot)
    assert caught.value.status == replay.HOLD_REPEAT


def test_publication_is_exclusive_parent_bound_and_stably_reread(tmp_path: Path) -> None:
    path = tmp_path / "receipt.json"
    target = _receipt_target(path)
    raw = replay._canonical_json_bytes({"schema": "fixture", "status": "pass"})
    publication = replay._publish_exclusive(target, raw, maximum_bytes=1024)
    assert path.read_bytes() == raw
    assert replay._publication_parent_stable(publication) is True
    assert replay._close_publication(publication) is True
    with pytest.raises(replay.ReplayHold) as caught:
        replay._publish_exclusive(target, raw, maximum_bytes=1024)
    assert caught.value.status == replay.HOLD_API
    assert path.read_bytes() == raw


def test_publication_parent_close_failure_removes_receipt_closes_fd_and_holds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "receipt.json"
    publication = replay._publish_exclusive(
        _receipt_target(path),
        b"owned",
        maximum_bytes=1024,
    )
    publication_descriptor = publication.directory_descriptor
    real_close = replay.os.close
    injected = False

    def fail_publication_close_once(descriptor: int) -> None:
        nonlocal injected
        if descriptor == publication_descriptor and not injected:
            injected = True
            raise OSError("fixture publication parent close failure")
        real_close(descriptor)

    monkeypatch.setattr(replay.os, "close", fail_publication_close_once)
    with pytest.raises(replay.ReplayHold) as caught:
        if not replay._close_publication(publication):
            raise replay.ReplayHold(replay.HOLD_CLEANUP)
    assert caught.value.status == replay.HOLD_CLEANUP
    assert injected is True
    assert publication.closed is True
    assert not path.exists()
    with pytest.raises(OSError) as fd_closed:
        os.fstat(publication_descriptor)
    assert fd_closed.value.errno == replay.errno.EBADF


def test_post_close_reopen_cleanup_retries_and_confirms_reopened_fd_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "receipt.json"
    publication = replay._publish_exclusive(
        _receipt_target(path),
        b"owned",
        maximum_bytes=1024,
    )
    original_descriptor = publication.directory_descriptor
    real_close = replay.os.close
    real_fstat = replay.os.fstat
    initial_after_close_failure = False
    reopened_before_close_failure = False
    reopened_descriptor: int | None = None

    def fail_both_close_branches_once(descriptor: int) -> None:
        nonlocal initial_after_close_failure
        nonlocal reopened_before_close_failure
        nonlocal reopened_descriptor
        metadata = real_fstat(descriptor)
        if descriptor == original_descriptor and not initial_after_close_failure:
            initial_after_close_failure = True
            real_close(descriptor)
            raise OSError("fixture error reported after original fd closed")
        if (
            stat.S_ISDIR(metadata.st_mode)
            and initial_after_close_failure
            and not reopened_before_close_failure
        ):
            reopened_before_close_failure = True
            reopened_descriptor = descriptor
            raise OSError("fixture error before reopened cleanup fd closed")
        real_close(descriptor)

    monkeypatch.setattr(replay.os, "close", fail_both_close_branches_once)
    assert replay._close_publication(publication) is False
    assert initial_after_close_failure is True
    assert reopened_before_close_failure is True
    assert reopened_descriptor is not None
    assert not path.exists()
    with pytest.raises(OSError) as fd_closed:
        os.fstat(reopened_descriptor)
    assert fd_closed.value.errno == replay.errno.EBADF


def test_final_reread_file_close_failure_is_retried_without_fd_leak(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "receipt.json"
    publication = replay._publish_exclusive(
        _receipt_target(path),
        b"owned",
        maximum_bytes=1024,
    )
    real_close = replay.os.close
    real_fstat = replay.os.fstat
    failed_descriptor: int | None = None

    def fail_first_regular_file_close(descriptor: int) -> None:
        nonlocal failed_descriptor
        metadata = real_fstat(descriptor)
        if failed_descriptor is None and stat.S_ISREG(metadata.st_mode):
            failed_descriptor = descriptor
            raise OSError("fixture reread file close failure")
        real_close(descriptor)

    monkeypatch.setattr(replay.os, "close", fail_first_regular_file_close)
    assert replay._close_publication(publication) is True
    assert failed_descriptor is not None
    assert path.read_bytes() == b"owned"
    with pytest.raises(OSError) as fd_closed:
        os.fstat(failed_descriptor)
    assert fd_closed.value.errno == replay.errno.EBADF


def test_publication_write_failure_removes_only_self_created_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "receipt.json"
    target = _receipt_target(path)

    def fail_write(*args, **kwargs):
        raise OSError("fixture write failure")

    monkeypatch.setattr(replay.os, "write", fail_write)
    with pytest.raises(replay.ReplayHold) as caught:
        replay._publish_exclusive(target, b"payload", maximum_bytes=1024)
    assert caught.value.status == replay.HOLD_API
    assert not os.path.lexists(path)


def test_exclusive_open_then_initial_fstat_failure_removes_owned_empty_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "receipt.json"
    target = _receipt_target(path)
    real_fstat = replay.os.fstat
    failed = False

    def fail_first_empty_regular(descriptor: int):
        nonlocal failed
        metadata = real_fstat(descriptor)
        if not failed and stat.S_ISREG(metadata.st_mode) and metadata.st_size == 0:
            failed = True
            raise OSError("fixture initial fstat failure")
        return metadata

    monkeypatch.setattr(replay.os, "fstat", fail_first_empty_regular)
    with pytest.raises(replay.ReplayHold) as caught:
        replay._publish_exclusive(target, b"owned", maximum_bytes=1024)
    assert caught.value.status == replay.HOLD_API
    assert failed is True
    assert not os.path.lexists(path)


def test_publication_replacement_is_retained_and_cleanup_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "receipt.json"
    target = _receipt_target(path)

    def replace_before_reread(directory_descriptor, name, **kwargs):
        os.unlink(name, dir_fd=directory_descriptor)
        descriptor = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=directory_descriptor,
        )
        try:
            os.write(descriptor, b"replacement")
        finally:
            os.close(descriptor)
        raise replay.ReplayHold(replay.HOLD_REPEAT)

    monkeypatch.setattr(replay, "_read_published_at", replace_before_reread)
    with pytest.raises(replay.ReplayHold) as caught:
        replay._publish_exclusive(target, b"owned", maximum_bytes=1024)
    assert caught.value.status == replay.HOLD_CLEANUP
    assert path.read_bytes() == b"replacement"


def test_parent_replacement_after_cli_identity_capture_is_rejected(tmp_path: Path) -> None:
    parent = tmp_path / "output"
    parent.mkdir()
    target = _receipt_target(parent / "receipt.json")
    moved = tmp_path / "moved"
    parent.rename(moved)
    parent.mkdir()
    with pytest.raises(replay.ReplayHold) as caught:
        replay._publish_exclusive(target, b"owned", maximum_bytes=1024)
    assert caught.value.status == replay.HOLD_API
    assert not (parent / "receipt.json").exists()
    assert not (moved / "receipt.json").exists()


def test_stdout_failure_reopens_identity_token_and_removes_closed_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "receipt.json"
    publication = replay._publish_exclusive(
        _receipt_target(path),
        b"owned",
        maximum_bytes=1024,
    )
    assert replay._close_publication(publication) is True

    class FailingBuffer:
        def write(self, payload: bytes) -> int:
            raise OSError("fixture stdout failure")

        def flush(self) -> None:
            raise AssertionError("flush must not follow write failure")

    class FailingStdout:
        buffer = FailingBuffer()

    monkeypatch.setattr(
        replay, "_validate_cli", lambda argv: (tmp_path, tmp_path, publication.target)
    )
    monkeypatch.setattr(
        replay,
        "run_replay",
        lambda *args: (b"pass-ack", publication, time.monotonic() + 10),
    )
    monkeypatch.setattr(replay.sys, "stdout", FailingStdout())
    assert replay._main([]) == 2
    assert not path.exists()


def test_final_deadline_gate_removes_receipt_and_emits_timeout_hold(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "receipt.json"
    publication = replay._publish_exclusive(
        _receipt_target(path),
        b"owned",
        maximum_bytes=1024,
    )
    assert replay._close_publication(publication) is True
    written = bytearray()

    class RecordingBuffer:
        def write(self, payload: bytes) -> int:
            written.extend(payload)
            return len(payload)

        def flush(self) -> None:
            return None

    class RecordingStdout:
        buffer = RecordingBuffer()

    monkeypatch.setattr(
        replay, "_validate_cli", lambda argv: (tmp_path, tmp_path, publication.target)
    )
    monkeypatch.setattr(
        replay,
        "run_replay",
        lambda *args: (b"forbidden-pass", publication, time.monotonic() - 1),
    )
    monkeypatch.setattr(replay.sys, "stdout", RecordingStdout())
    assert replay._main([]) == 2
    assert not path.exists()
    decoded = json.loads(bytes(written))
    assert decoded == {
        "schema": replay.OUTER_HOLD_ACK_SCHEMA,
        "status": replay.HOLD_TIMEOUT,
    }


def test_pass_ack_boundary_follows_publication_close_and_final_deadline_gate() -> None:
    run_source = inspect.getsource(replay.run_replay)
    publish = run_source.index("_publish_exclusive")
    close = run_source.index("_close_publication", publish)
    final_deadline = run_source.index("_global_time_check", close)
    returned = run_source.index("return acknowledgement_raw", final_deadline)
    main_source = inspect.getsource(replay._main)
    stdout_write = main_source.index("sys.stdout.buffer.write")
    assert publish < close < final_deadline < returned
    assert main_source.index("run_replay") < stdout_write


def test_prelaunch_reserve_is_spent_only_by_nonchild_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(replay.time, "monotonic", lambda: 10.0)
    replay._prelaunch_time_check(
        outer_started=0.0,
        global_deadline=2700.0,
        completed_child_seconds=0.0,
        remaining_runs=2,
    )
    monkeypatch.setattr(replay.time, "monotonic", lambda: 301.0)
    with pytest.raises(replay.ReplayHold) as caught:
        replay._prelaunch_time_check(
            outer_started=0.0,
            global_deadline=2700.0,
            completed_child_seconds=0.0,
            remaining_runs=2,
        )
    assert caught.value.status == replay.HOLD_TIMEOUT


def test_outer_cli_is_exact_and_output_must_be_outside_inputs(tmp_path: Path) -> None:
    output = tmp_path / "receipt.json"
    report, bundle, target = replay._validate_cli(
        [
            "--report-root",
            os.fspath(REPORT_ROOT),
            "--bundle",
            os.fspath(BUNDLE_ROOT),
            "--outer-receipt",
            os.fspath(output),
        ]
    )
    assert report == REPORT_ROOT.resolve()
    assert bundle == BUNDLE_ROOT.resolve()
    assert target.path == output
    with pytest.raises(replay.ReplayHold) as caught:
        replay._validate_cli(
            [
                "--report-root",
                os.fspath(REPORT_ROOT),
                "--bundle",
                os.fspath(BUNDLE_ROOT),
                "--outer-receipt",
                os.fspath(REPORT_ROOT / "forbidden.json"),
            ]
        )
    assert caught.value.status == replay.HOLD_API
    with pytest.raises(replay.ReplayHold) as caught:
        replay._validate_cli(
            [
                "--report-root",
                os.fspath(REPORT_ROOT),
                "--bundle",
                os.fspath(BUNDLE_ROOT),
                "--outer-receipt",
                f"/private/tmp/encounter-receipt-{os.getpid()}.json",
            ]
        )
    assert caught.value.status == replay.HOLD_API


def test_operation_model_freezes_all_required_cleanup_and_wire_predicates() -> None:
    model = json.loads((REPORT_ROOT / replay.OPERATION_MODEL_PATH).read_bytes())
    assert model["replay"]["input_snapshot_components"] == list(replay.COMPONENT_ORDER)
    assert model["runtime_launcher_policy"] == {
        "child_argv_zero_is_absolute_outer_sys_executable": True,
        "executing_only_the_physically_resolved_target_is_forbidden": True,
        "full_binary_dependency_filesystem_closure": False,
        "launcher_may_be_a_venv_symlink": True,
        "launcher_symlink_chain_stable_pre_launch_post_exit": True,
        "python_stdlib_and_dynamic_library_bytes_fully_snapshotted": False,
        "resolved_regular_target_bytes_are_the_runtime_executable_component": True,
        "runtime_executable_and_gmpy2_extension_bytes_bound": True,
    }
    cleanup = model["cleanup_state_machine"]
    assert cleanup["direct_child_reap_required"] is True
    assert cleanup["stdout_eof_required"] is True
    assert cleanup["stderr_eof_required"] is True
    assert cleanup["selector_empty_and_closed_required"] is True
    assert cleanup["stage_absence_required_before_next_launch"] is True
    assert model["failure_wire"]["outer_hold_retains_outer_receipt"] is False
