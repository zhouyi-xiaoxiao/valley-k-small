from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import build_continuum_c0_model_contract_candidate_v2 as producer
import pytest
import validate_continuum_c0_model_contract_candidate_v2 as verifier

REPORT = Path(__file__).resolve().parents[1]
CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v2.json"
V1_CONTRACT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v1.json"


def test_producer_check_cli_accepts_only_the_current_rebuild() -> None:
    completed = subprocess.run(
        [sys.executable, str(Path(producer.__file__).resolve()), "--check"],
        cwd=REPORT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    receipt = json.loads(completed.stdout)
    assert receipt == {
        "action": "check",
        "complete_c0": False,
        "contract_sha256": verifier.EXPECTED_CONTRACT_SHA256,
        "control_values_read": False,
        "opened_auxiliary_paths": [
            "artifacts/data/continuum_c0_model_contract_candidate_v1.json"
        ],
        "opened_source_paths": [
            producer.FROZEN_SOURCES[role]["path"]
            for role in sorted(producer.FROZEN_SOURCES)
        ],
        "positive_budget_scientific_values_read": False,
        "release_eligible": False,
        "scratch_or_result_payload_read": False,
        "status": producer.PASS_CHECK,
        "v1_sha256": producer.V1_SHA256,
    }


def test_current_five_source_pins_rebuild_without_following_embedded_paths() -> None:
    payload = producer.build_payload()
    assert payload["frozen_sources"] == producer.FROZEN_SOURCES
    assert len(payload["frozen_sources"]) == 5
    assert payload["source_policy"] == producer.SOURCE_POLICY
    assert payload["source_policy"]["embedded_source_paths_followed"] is False
    assert payload["source_policy"]["opaque_scratch_or_result_payload_opened"] is False
    assert payload["source_policy"]["living_continuum_program_pinned"] is False
    assert producer.canonical_json_bytes(payload) == CONTRACT.read_bytes()


def test_legacy_initial_source_ordering_exception_is_exact_byte_pinned() -> None:
    descriptor = producer.FROZEN_SOURCES["initial_source"]
    source = REPORT / descriptor["path"]
    raw = source.read_bytes()
    decoded = producer.parse_source_json(raw)
    producer._scan_result_bearing(decoded)
    assert hashlib.sha256(raw).hexdigest() == descriptor["sha256"]
    assert raw != producer.canonical_json_bytes(decoded)


def test_historical_v1_contract_bytes_remain_immutable() -> None:
    v1_bytes = V1_CONTRACT.read_bytes()
    v1_sha256 = hashlib.sha256(v1_bytes).hexdigest()
    assert v1_sha256 == producer.V1_SHA256 == verifier.V1_SHA256
    assert producer.assert_v1_immutable() == v1_bytes

    current = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert current["previous_contract"] == verifier.EXPECTED_PREVIOUS
    assert current["previous_contract"]["sha256"] == v1_sha256
    assert current["previous_contract"]["v1_bytes_mutated"] is False


def test_actual_python_open_set_is_read_only_and_result_blind(monkeypatch) -> None:
    observed: list[tuple[str, int]] = []
    real_open = os.open

    def audited_open(path, flags, *args, **kwargs):
        observed.append((os.fspath(path), flags))
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", audited_open)
    producer.build_bytes()
    verifier.verify_contract_bytes(CONTRACT.read_bytes())

    json_names = {
        Path(path).name for path, _flags in observed if Path(path).suffix == ".json"
    }
    expected_names = {
        "continuum_c0_control_method_commitment_v2.json",
        "continuum_c0_mathematical_source_v2.json",
        "continuum_c0_model_contract_candidate_v1.json",
        "physical_configuration_family_control_free_v1.json",
        "physical_initial_analytic_source_v1.json",
        "physical_killing_geometry_source_v1.json",
    }
    assert json_names == expected_names
    assert all(
        not ({"scratch", "result", "results", "control", "controls"} & set(Path(path).parts))
        for path, _flags in observed
    )
    write_mask = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
    legacy_events = [
        flags
        for path, flags in observed
        if Path(path).name == "continuum_c0_model_contract_candidate_v1.json"
    ]
    assert legacy_events
    assert all(flags & write_mask == 0 for flags in legacy_events)


def test_create_collision_is_fail_closed_and_preserves_v1(tmp_path: Path, capsys) -> None:
    target = tmp_path / "candidate.json"
    producer._exclusive_publish(target, b"first\n")
    with pytest.raises(FileExistsError):
        producer._exclusive_publish(target, b"second\n")
    assert target.read_bytes() == b"first\n"

    before_bytes = V1_CONTRACT.read_bytes()
    before = V1_CONTRACT.stat()
    assert producer.main(["--create"]) == 2
    capsys.readouterr()
    after = V1_CONTRACT.stat()
    assert V1_CONTRACT.read_bytes() == before_bytes
    assert (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) == (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )


def test_publish_rejects_a_symlinked_parent_without_redirecting(tmp_path: Path) -> None:
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent.name, target_is_directory=True)
    with pytest.raises((OSError, producer.BuildHold)):
        producer._exclusive_publish(linked_parent / "candidate.json", b"payload\n")
    assert not (real_parent / "candidate.json").exists()


def test_read_loops_enforce_cap_during_growth(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "growing.json"
    source.write_bytes(b"")
    monkeypatch.setattr(producer, "MAX_FILE_BYTES", 8)
    monkeypatch.setattr(verifier, "MAX_FILE_BYTES", 8)
    calls = 0

    def growing_read(_fd: int, requested: int) -> bytes:
        nonlocal calls
        calls += 1
        return b"x" * min(requested, 4)

    monkeypatch.setattr(os, "read", growing_read)
    with pytest.raises(producer.BuildHold):
        producer.read_regular_snapshot(source)
    assert calls == 3

    calls = 0
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.read_regular_snapshot(source, code=verifier.HOLD_SOURCES)
    assert caught.value.code == verifier.HOLD_SOURCES
    assert calls == 3


def test_reader_os_errors_are_converted_to_stable_holds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.json"
    source.write_bytes(b"{}\n")

    def failed_read(_fd: int, _requested: int) -> bytes:
        raise OSError("injected read failure")

    monkeypatch.setattr(os, "read", failed_read)
    with pytest.raises(producer.BuildHold):
        producer.read_regular_snapshot(source)
    with pytest.raises(verifier.C0V2Hold) as caught:
        verifier.read_regular_snapshot(source, code=verifier.HOLD_SOURCES)
    assert caught.value.code == verifier.HOLD_SOURCES
