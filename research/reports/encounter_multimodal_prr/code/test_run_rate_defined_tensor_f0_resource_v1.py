from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest
import run_rate_defined_tensor_f0_resource_v1 as runner


def _sidecar(output: Path) -> Path:
    return output.with_name(output.name + ".resources.json")


def test_frozen_formal_constants_and_complete_schedule() -> None:
    fixture = runner._FORMAL_FIXTURE
    assert runner.FORMAL_SHAPE == (207, 215, 161)
    assert runner.FORMAL_PERIODIC == (False, False, True)
    assert math.prod(runner.FORMAL_SHAPE) == runner.FORMAL_STATES == 7_165_305
    assert runner.FORMAL_UNIFORMIZATION_RATE == 256
    assert runner.FORMAL_KILLING == Fraction(1, 64)
    assert runner.FORMAL_SERIES_HORIZON == 100
    assert runner.FORMAL_TAIL_TOLERANCE == Fraction(1, 10**18)
    assert runner.FORMAL_MPFR_PRECISION_BITS == 192
    assert runner.FORMAL_MAXIMUM_POISSON_TERMS == 200_000
    assert runner.FORMAL_REDUCTION_BLOCK_SIZE == 65_536
    assert runner.FORMAL_EXPECTED_POISSON_MODE == 25_600
    assert runner.FORMAL_EXPECTED_RIGHT_INDEX == 27_014
    assert runner.FORMAL_EXPECTED_MAXIMUM_POWER == 27_018
    assert runner.FORMAL_MAXIMUM_WALL_SECONDS == 3_600
    assert runner.FORMAL_MAXIMUM_RSS_BYTES == 4_294_967_296
    assert runner.FORMAL_MAXIMUM_PEAK_FOOTPRINT_BYTES == 8_589_934_592
    assert runner.FORMAL_MAXIMUM_PROCESS_SWAP_DELTA == 0
    assert runner.FORMAL_MAXIMUM_STATE_RADIUS == Fraction(1, 100_000_000)
    assert fixture.topology_schedule_complete is True
    assert len(fixture.topology_times) == 512
    assert fixture.topology_times[0] == Fraction(1, 2)
    assert fixture.topology_times[-1] == Fraction(35)
    assert tuple(sorted(set(fixture.topology_times))) == fixture.topology_times
    union = set(fixture.topology_times) | set(fixture.mandatory_tail_times)
    assert fixture.mandatory_tail_times == (
        Fraction(35),
        Fraction(50),
        Fraction(75),
        Fraction(100),
    )
    assert len(union) == 515
    assert len(union) <= fixture.maximum_union_time_count
    assert runner._schedule_payload(fixture)["generator"] == (
        "rate_defined_tensor_f0_topology_schedule_v1"
    )
    assert runner._schedule_payload(fixture)["artifact_sha256"] == (
        runner.FORMAL_TOPOLOGY_SCHEDULE_ARTIFACT_SHA256
    )
    observed = {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in runner._DEPENDENCY_PATHS.items()
    }
    assert observed == runner._EXPECTED_DEPENDENCY_SHA256


def test_public_runner_has_only_output_path_and_cli_has_no_science_knobs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signature = inspect.signature(runner.run_resource_candidate)
    assert list(signature.parameters) == ["output_path"]
    parser = runner._argument_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }
    assert option_strings == {"-h", "--help"}
    relative = Path("relative.json")
    with pytest.raises(runner.ResourceRunnerFailure, match="absolute"):
        runner.run_resource_candidate(relative)
    provisional = dataclasses.replace(
        runner._FORMAL_FIXTURE,
        topology_schedule_complete=False,
    )
    monkeypatch.setattr(runner, "_FORMAL_FIXTURE", provisional)
    output = tmp_path / "formal.json"
    with pytest.raises(runner.ResourceRunnerFailure, match="provisional"):
        runner.run_resource_candidate(output)
    assert not output.exists()
    assert not _sidecar(output).exists()


def test_isolated_cli_imports_fixed_sibling_modules_before_fail_closed() -> None:
    source = Path(runner.__file__).resolve()
    completed = subprocess.run(
        [sys.executable, "-I", str(source), "relative.json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 2
    assert "output path must be an absolute" in completed.stderr
    assert "ModuleNotFoundError" not in completed.stderr


def test_private_small_fixture_writes_separated_bound_evidence(
    tmp_path: Path,
) -> None:
    output = tmp_path / "small.json"
    sidecar = runner._run_private_small_fixture(output)
    assert sidecar == _sidecar(output)
    assert output.is_file()
    assert sidecar.is_file()
    canonical_bytes = output.read_bytes()
    parsed = runner.validate_canonical_resource_payload_bytes(canonical_bytes)
    observation = json.loads(sidecar.read_text(encoding="ascii"))
    assert parsed["schema"] == runner.CANONICAL_SCHEMA
    assert parsed["promotion_flags"] == runner._PROMOTION_FLAGS
    assert parsed["fixture"]["production_scale"] is False
    assert len(parsed["compiled_batch_evidence"]["evaluations"]) == 3
    assert len(parsed["mandatory_tail_evaluations"]) == 1
    assert observation["schema"] == runner.OBSERVATION_SCHEMA
    assert observation["status"] == runner.PRIVATE_STATUS
    assert observation["promotion_flags"] == runner._PROMOTION_FLAGS
    assert observation["canonical_artifact"]["sha256"] == hashlib.sha256(
        canonical_bytes
    ).hexdigest()
    assert observation["method_counts"]["compiled_power_stream_run_count"] == 1
    assert observation["method_counts"]["repeated_p_actions_during_reevaluation"] == 0
    assert observation["method_counts"]["topology_evaluation_count"] == 3
    assert observation["method_counts"]["mandatory_tail_evaluation_count"] == 1
    assert parsed["compiled_batch_evidence"]["receipt"]["resource_pass"] is False
    assert parsed["compiled_batch_evidence"]["receipt"]["f0_pass"] is False
    assert parsed["schedule"]["artifact_sha256"] is None


def test_cap_violation_is_recorded_without_promoting_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tiny_cap = dataclasses.replace(
        runner._SMALL_TEST_FIXTURE,
        maximum_wall_seconds=Fraction(0),
    )
    monkeypatch.setattr(runner, "_SMALL_TEST_FIXTURE", tiny_cap)
    output = tmp_path / "cap.json"
    runner._run_private_small_fixture(output)
    observation = json.loads(_sidecar(output).read_text(encoding="ascii"))
    assert observation["status"] == runner.PRIVATE_STATUS
    assert observation["resource_caps_satisfied"] is False
    assert "wall_cap_exceeded" in observation["failure_reasons"]
    assert observation["promotion_flags"]["resource_pass"] is False
    assert observation["promotion_flags"]["f0_pass"] is False


def test_canonical_mutation_and_duplicate_key_fail_closed(
    tmp_path: Path,
) -> None:
    output = tmp_path / "mutation.json"
    runner._run_private_small_fixture(output)
    payload = output.read_bytes()
    parsed = json.loads(payload)
    parsed["status"] = "PASS_F0"
    mutated = json.dumps(
        parsed,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    with pytest.raises(runner.ResourceRunnerFailure):
        runner.validate_canonical_resource_payload_bytes(mutated)
    duplicate = payload.replace(
        b'{"compiled_batch_evidence":',
        b'{"schema":"duplicate","compiled_batch_evidence":',
        1,
    )
    with pytest.raises(runner.ResourceRunnerFailure, match="duplicate"):
        runner.validate_canonical_resource_payload_bytes(duplicate)


def test_rehashed_nested_claim_promotion_fails_closed(tmp_path: Path) -> None:
    output = tmp_path / "nested-promotion.json"
    runner._run_private_small_fixture(output)
    parsed = json.loads(output.read_bytes())
    evidence = parsed["compiled_batch_evidence"]
    receipt = evidence["receipt"]
    receipt["f0_pass"] = True
    receipt["receipt_sha256"] = runner._binding_without(
        receipt,
        "receipt_sha256",
    )
    evidence["evidence_binding_sha256"] = runner._binding_with_zero(
        evidence,
        "evidence_binding_sha256",
    )
    parsed["payload_binding_sha256"] = runner._binding_with_zero(
        parsed,
        "payload_binding_sha256",
    )
    mutated = runner._canonical_json_bytes(parsed)
    with pytest.raises(runner.ResourceRunnerFailure, match="promoted"):
        runner.validate_canonical_resource_payload_bytes(mutated)


def test_dependency_hash_mutation_fails_before_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mutated = dict(runner._EXPECTED_DEPENDENCY_SHA256)
    mutated["compiled_batch_source"] = "0" * 64
    monkeypatch.setattr(runner, "_EXPECTED_DEPENDENCY_SHA256", mutated)
    output = tmp_path / "dependency.json"
    with pytest.raises(runner.ResourceRunnerFailure, match="dependency hash mismatch"):
        runner._run_private_small_fixture(output)
    assert not output.exists()
    assert not _sidecar(output).exists()


def test_atomic_exclusive_publication_never_overwrites(
    tmp_path: Path,
) -> None:
    output = tmp_path / "exclusive.json"
    runner._run_private_small_fixture(output)
    canonical_before = output.read_bytes()
    sidecar_before = _sidecar(output).read_bytes()
    with pytest.raises(runner.ResourceRunnerFailure, match="already exists"):
        runner._run_private_small_fixture(output)
    assert output.read_bytes() == canonical_before
    assert _sidecar(output).read_bytes() == sidecar_before
