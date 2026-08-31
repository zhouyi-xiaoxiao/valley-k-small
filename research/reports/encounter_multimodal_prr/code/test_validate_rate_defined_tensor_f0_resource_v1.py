from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest
import run_rate_defined_tensor_f0_resource_v1 as runner
import validate_rate_defined_tensor_f0_resource_v1 as validator


REPORT_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = (
    REPORT_ROOT / "artifacts/data/rate_defined_tensor_f0_resource_v1.json"
)
SIDECAR = CANONICAL.with_name(CANONICAL.name + ".resources.json")
SCHEDULE = (
    REPORT_ROOT
    / "artifacts/data/rate_defined_tensor_f0_topology_schedule_v1.json"
)


def _formal_receipt() -> dict[str, object]:
    return validator.build_independent_replay_receipt(
        canonical_artifact=CANONICAL,
        resource_sidecar=SIDECAR,
        topology_schedule=SCHEDULE,
        report_root=REPORT_ROOT,
    )


def test_real_formal_artifact_is_independently_confirmed_resource_hold() -> None:
    receipt = _formal_receipt()
    assert receipt["schema"] == validator.REPLAY_SCHEMA
    assert receipt["status"] == validator.HOLD_REPLAY_STATUS
    assert receipt["failure_reasons"] == [
        "rss_cap_exceeded",
        "peak_footprint_cap_exceeded",
    ]
    assert receipt["promotion_flags"] == validator.REPLAY_PROMOTION_FLAGS
    assert not any(receipt["promotion_flags"].values())
    assert receipt["checks"] == {
        "absolute_time_rows_validated": 516,
        "canonical_ascii_and_key_sets_validated": True,
        "canonical_scalar_records_validated": 27_019,
        "dependency_files_rehashed": 14,
        "formal_schedule_union_count": 515,
        "identity_fixture_reconstructed": True,
        "nested_sha_bindings_replayed": True,
        "poisson_plans_independently_checked": 517,
        "resource_caps_satisfied": False,
        "sidecar_failure_reasons_replayed": True,
    }
    assert receipt["observed_measurements"]["process_swap_delta"] == 0
    assert receipt["observed_measurements"]["peak_rss_bytes"] > (
        receipt["frozen_caps"]["maximum_rss_bytes"]
    )
    assert receipt["observed_measurements"]["host_peak_footprint_bytes"] > (
        receipt["frozen_caps"]["maximum_peak_footprint_bytes"]
    )
    assert receipt["receipt_binding_sha256"] == validator._binding_with_zero(
        receipt,
        "receipt_binding_sha256",
    )
    with pytest.raises(
        validator.IndependentReplayFailure,
        match="formal resource PASS required",
    ):
        validator.require_formal_resource_pass(receipt)


def test_real_formal_artifact_hash_and_exact_count_bindings() -> None:
    receipt = _formal_receipt()
    artifacts = receipt["artifacts"]
    assert artifacts["canonical_resource"]["sha256"] == hashlib.sha256(
        CANONICAL.read_bytes()
    ).hexdigest()
    assert artifacts["resource_sidecar"]["sha256"] == hashlib.sha256(
        SIDECAR.read_bytes()
    ).hexdigest()
    assert artifacts["topology_schedule"]["sha256"] == (
        validator.SCHEDULE_ARTIFACT_SHA256
    )
    parsed = json.loads(CANONICAL.read_bytes())
    assert len(parsed["compiled_batch_evidence"]["series"]["records"]) == 27_019
    assert len(parsed["compiled_batch_evidence"]["evaluations"]) == 512
    assert len(parsed["mandatory_tail_evaluations"]) == 4


def test_private_small_fixture_is_never_accepted_as_formal(
    tmp_path: Path,
) -> None:
    private_artifact = tmp_path / "private-small.json"
    runner._run_private_small_fixture(private_artifact)
    schedule, topology = validator._validate_schedule(
        SCHEDULE.read_bytes(),
        report_root=REPORT_ROOT,
    )
    assert schedule["counts"]["topology"] == 512
    with pytest.raises(
        validator.IndependentReplayFailure,
        match="canonical resource header drifted",
    ):
        validator.validate_canonical_artifact_bytes(
            private_artifact.read_bytes(),
            topology=topology,
        )


def test_duplicate_unknown_and_noncanonical_json_fail_closed() -> None:
    payload = b'{"a":1,"a":2}'
    with pytest.raises(validator.IndependentReplayFailure, match="duplicate"):
        validator._strict_json_loads(
            payload,
            label="mutation",
            maximum_bytes=100,
        )
    parsed = json.loads(SCHEDULE.read_bytes())
    parsed["unknown"] = False
    mutated = validator._canonical_json_bytes(parsed)
    with pytest.raises(
        validator.IndependentReplayFailure,
        match="hash drifted",
    ):
        validator._validate_schedule(mutated, report_root=REPORT_ROOT)
    spaced = b'{"a": 1}'
    assert validator._canonical_json_bytes(
        validator._strict_json_loads(
            spaced,
            label="spaced",
            maximum_bytes=100,
        )
    ) != spaced


def test_rehashed_sidecar_status_or_cap_promotion_fails_closed(
    tmp_path: Path,
) -> None:
    sidecar = json.loads(SIDECAR.read_bytes())
    sidecar["status"] = validator.PASS_OBSERVATION_STATUS
    sidecar["resource_caps_satisfied"] = True
    mutation = tmp_path / "promoted.resources.json"
    mutation.write_bytes(validator._pretty_json_bytes(sidecar))
    with pytest.raises(
        validator.IndependentReplayFailure,
        match="held resource sidecar status drifted",
    ):
        validator.build_independent_replay_receipt(
            canonical_artifact=CANONICAL,
            resource_sidecar=mutation,
            topology_schedule=SCHEDULE,
            report_root=REPORT_ROOT,
        )


def test_cli_surface_has_only_paths_and_output_is_exclusive(
    tmp_path: Path,
) -> None:
    parser = validator._argument_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }
    assert option_strings == {
        "-h",
        "--help",
        "--canonical-artifact",
        "--resource-sidecar",
        "--topology-schedule",
        "--report-root",
        "--output",
    }
    output = tmp_path / "receipt.json"
    validator._write_exclusive(output.resolve(), b"first")
    with pytest.raises(validator.IndependentReplayFailure, match="reservation"):
        validator._write_exclusive(output.resolve(), b"second")
    assert output.read_bytes() == b"first"
    with pytest.raises(validator.IndependentReplayFailure, match="absolute"):
        validator._write_exclusive(Path("relative.json"), b"x")


def test_validator_source_has_no_numerical_pipeline_imports() -> None:
    tree = ast.parse(Path(validator.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", 1)[0])
    prohibited = {
        "gmpy2",
        "numpy",
        "rate_defined_tensor_f0_batched_scalar_uniformization_v1",
        "rate_defined_tensor_f0_candidate_v1",
        "rate_defined_tensor_f0_compiled_batch_v1",
        "rate_defined_tensor_f0_compiled_power_stream_v1",
        "run_rate_defined_tensor_f0_resource_v1",
    }
    assert imported.isdisjoint(prohibited)
