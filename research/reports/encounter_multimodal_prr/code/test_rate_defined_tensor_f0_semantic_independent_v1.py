from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

import rate_defined_tensor_f0_semantic_independent_v1 as replay


REPORT = Path(__file__).resolve().parent.parent
ARTIFACTS = REPORT / "artifacts" / "data"


def _inputs() -> tuple[bytes, bytes, bytes, bytes, bytes]:
    candidate_a = (
        ARTIFACTS / "rate_defined_tensor_f0_candidate_v1_replica_a.json"
    ).read_bytes()
    candidate_b = (
        ARTIFACTS / "rate_defined_tensor_f0_candidate_v1_replica_b.json"
    ).read_bytes()
    schedule = (
        ARTIFACTS / "rate_defined_tensor_f0_topology_schedule_v1.json"
    ).read_bytes()
    resource_path = ARTIFACTS / "rate_defined_tensor_f0_resource_v1.json"
    return (
        candidate_a,
        candidate_b,
        schedule,
        resource_path.read_bytes(),
        Path(f"{resource_path}.resources.json").read_bytes(),
    )


def test_current_formal_receipt_passes_semantics_but_holds_authority() -> None:
    receipt = replay.independent_replay(*_inputs())
    assert receipt["method_semantic_replay_pass"] is True
    assert receipt["status"] == "PASS_F0_SEMANTIC_REPLAY_RESOURCE_HOLD_NOT_F0"
    assert receipt["terminal_branch_recommendation"] == "HOLD_F0_METHOD_OR_RESOURCE"
    assert receipt["resource_replay"]["failure_reasons"] == [
        "rss_cap_exceeded",
        "peak_footprint_cap_exceeded",
    ]
    assert all(value is False for value in receipt["authority_flags"].values())
    rows = receipt["selector_configuration_replay"]["fixed_36_row_order"]
    assert [(row["control_role"], row["configuration"]) for row in rows] == [
        (control, configuration)
        for control in ("lp_m1", "lp_m2", "lp_m3")
        for configuration in (
            "O113/Base",
            "E128/Base",
            "O129/Base",
            "O161/Base",
            "M+",
            "R+",
            "MR+",
            "MR+F",
            "A_M",
            "A_R",
            "A_Y",
            "A_MRY",
        )
    ]


def test_checked_in_receipt_is_canonical_and_current() -> None:
    path = ARTIFACTS / "rate_defined_tensor_f0_semantic_independent_v1.json"
    payload = path.read_bytes()
    parsed = replay.strict_json_bytes(payload, canonical=True)
    assert payload == replay.canonical_bytes(replay.independent_replay(*_inputs()))
    assert parsed["schema"] == replay.SCHEMA


def test_missing_resource_is_fail_closed_but_fixture_capable() -> None:
    candidate_a, candidate_b, schedule, _resource, _receipt = _inputs()
    result = replay.independent_replay(
        candidate_a, candidate_b, schedule, None, None
    )
    assert result["method_semantic_replay_pass"] is True
    assert result["status"] == "PASS_F0_SEMANTIC_REPLAY_AWAITING_RESOURCE"
    assert result["resource_replay"]["resource_gate_pass"] is False
    assert result["authority_flags"]["f0_accepted"] is False


def test_candidate_replica_mutation_is_rejected() -> None:
    candidate_a, candidate_b, schedule, resource, receipt = _inputs()
    mutation = bytearray(candidate_b)
    mutation[-2] = ord(" ")
    with pytest.raises(replay.ReplayFailure):
        replay.independent_replay(
            candidate_a, bytes(mutation), schedule, resource, receipt
        )


def test_schedule_mutation_is_rejected() -> None:
    candidate_a, candidate_b, schedule, resource, receipt = _inputs()
    mutation = bytearray(schedule)
    mutation[-2] = ord(" ")
    with pytest.raises(replay.ReplayFailure):
        replay.independent_replay(
            candidate_a, candidate_b, bytes(mutation), resource, receipt
        )


def test_resource_receipt_false_pass_mutation_is_rejected() -> None:
    candidate_a, candidate_b, schedule, resource, receipt = _inputs()
    parsed = json.loads(receipt)
    parsed["resource_caps_satisfied"] = True
    mutated = replay.canonical_bytes(parsed) + b"\n"
    with pytest.raises(replay.ReplayFailure, match="classification"):
        replay.independent_replay(
            candidate_a, candidate_b, schedule, resource, mutated
        )


def test_heterogeneous_jet_mutation_fails_targeted_replay() -> None:
    candidate = replay.strict_json_bytes(_inputs()[0], canonical=True)
    mutated = copy.deepcopy(candidate)
    jet = mutated["integrated_compiled_fixture"]["compiled_batch_evidence"][
        "evaluations"
    ][0]["jets"][0]
    jet["lower_hex"] = jet["upper_hex"]
    mutated["integrated_compiled_fixture"]["compiled_batch_evidence_sha256"] = (
        replay._sha256(
            replay.canonical_bytes(
                mutated["integrated_compiled_fixture"]["compiled_batch_evidence"]
            )
        )
    )
    with pytest.raises(replay.ReplayFailure, match="J0"):
        replay._heterogeneous_replay(mutated)


def test_analytic_root_mutation_fails_targeted_replay() -> None:
    candidate = replay.strict_json_bytes(_inputs()[0], canonical=True)
    mutated = copy.deepcopy(candidate)
    mutated["analytic_topology_fixtures"]["fixtures"][0][
        "analytic_definition"
    ]["roots"][0] = "9/1"
    with pytest.raises(replay.ReplayFailure, match="definition"):
        replay._analytic_replay(mutated)


def test_strict_parser_rejects_duplicate_keys_floats_and_noncanonical() -> None:
    with pytest.raises(replay.ReplayFailure):
        replay.strict_json_bytes(b'{"a":1,"a":2}', canonical=True)
    with pytest.raises(replay.ReplayFailure):
        replay.strict_json_bytes(b'{"a":1.0}', canonical=True)
    with pytest.raises(replay.ReplayFailure):
        replay.strict_json_bytes(b'{ "a":1}', canonical=True)


def test_validator_has_no_producer_imports() -> None:
    tree = ast.parse(Path(replay.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not [
        name for name in imported if name.startswith("rate_defined_tensor_f0")
    ]
