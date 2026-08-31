"""Positive tests for the source-separated role-10 operation-model v2 validator."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

CODE = Path(__file__).resolve().parent
REPORT = CODE.parent
BUILDER_PATH = CODE / "build_continuum_c1_n0_role10_numerical_operation_model_v2_candidate.py"
VALIDATOR_PATH = CODE / "validate_continuum_c1_n0_role10_numerical_operation_model_v2_candidate.py"
ARTIFACT = (
    REPORT / "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v2_candidate.json"
)


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


validator = load_module("role10_operation_model_v2_validator_positive", VALIDATOR_PATH)


@pytest.fixture(scope="module")
def raw() -> bytes:
    return validator.read_immutable(ARTIFACT, label="positive-test artifact")


@pytest.fixture(scope="module")
def model(raw: bytes) -> dict[str, Any]:
    return validator.parse_canonical_json(raw, "positive-test artifact")


def test_installed_artifact_identity_and_frozen_mode(raw: bytes) -> None:
    status = ARTIFACT.stat()
    assert stat.S_IMODE(status.st_mode) == 0o444
    assert status.st_nlink == 1
    assert len(raw) == 212_071
    assert hashlib.sha256(raw).hexdigest() == validator.FROZEN_MODEL_SHA256


def test_validator_never_imports_or_executes_either_builder() -> None:
    tree = ast.parse(VALIDATOR_PATH.read_text(encoding="utf-8"))
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any("build_continuum" in name for name in imported)
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"run", "Popen", "check_call", "check_output"}
    ]
    assert calls == []


def test_full_semantic_oracle_and_separate_frozen_sha(model: dict[str, Any], raw: bytes) -> None:
    assert validator.validate_value(model, enforce_frozen_sha=False) == (
        validator.FROZEN_MODEL_SHA256
    )
    assert (
        validator.validate_value(model, enforce_frozen_sha=True, observed_raw=raw)
        == validator.FROZEN_MODEL_SHA256
    )
    assert model == validator.expected_model()


def test_sha_gate_is_separate_from_semantic_oracle(
    monkeypatch: pytest.MonkeyPatch, model: dict[str, Any], raw: bytes
) -> None:
    monkeypatch.setattr(validator, "FROZEN_MODEL_SHA256", "0" * 64)
    assert validator.validate_value(model, enforce_frozen_sha=False) == (
        hashlib.sha256(raw).hexdigest()
    )
    with pytest.raises(validator.OperationModelV2ValidationError, match="whole-file"):
        validator.validate_value(model, enforce_frozen_sha=True, observed_raw=raw)


def test_v1_lineage_is_authenticated_and_reconstruction_is_exact(
    model: dict[str, Any],
) -> None:
    v1_raw = validator.read_immutable(validator.V1_PATH, label="positive-test v1")
    assert hashlib.sha256(v1_raw).hexdigest() == validator.V1_SHA256
    assert model["lineage"]["v1"] == {
        "path": (
            "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v1_candidate.json"
        ),
        "schema": validator.V1_SCHEMA,
        "sha256": validator.V1_SHA256,
        "status": "HISTORICAL_RESULT_BLIND_DRAFT_SUPERSEDED_BEFORE_EXTERNAL_COMMITMENT",
    }
    delta = validator.decoded_delta()
    assert delta["o"] == "d"
    reconstructed = validator._apply_delta(
        validator.parse_canonical_json(v1_raw, "positive-test v1"), delta
    )
    repair = validator.decoded_repair_delta()
    if repair is not None:
        reconstructed = validator._apply_delta(reconstructed, repair)
    assert reconstructed == model


def test_declared_v1_reuse_and_only_row_schema_transform(
    model: dict[str, Any],
) -> None:
    v1 = validator._v1_model_cached()
    for section in (
        "authority_bindings",
        "authority_model",
        "method_contract",
        "resource_caps",
    ):
        assert model[section] == v1[section]
    for section in (
        "directory_paths",
        "file_paths",
        "path_templates",
        "top_file_inventory",
        "totals",
    ):
        assert model["artifact_contract"][section] == v1["artifact_contract"][section]
    for row, v1_row in zip(
        model["artifact_contract"]["rows"],
        v1["artifact_contract"]["rows"],
        strict=True,
    ):
        assert row["row_schema"] == validator.ROW_SCHEMA
        assert v1_row["row_schema"].endswith("_row_v1")
        assert {key: value for key, value in row.items() if key != "row_schema"} == {
            key: value for key, value in v1_row.items() if key != "row_schema"
        }


def test_root_status_and_every_precommit_promotion_claim_false(
    model: dict[str, Any],
) -> None:
    assert model["schema"] == validator.MODEL_SCHEMA
    assert model["status"] == validator.MODEL_STATUS
    assert model["claim_boundary"] == validator.precommit_claims()
    assert all(value is False for value in model["claim_boundary"].values())
    lifecycle = model["wire_schema_contract"]["lifecycle_maps"]
    assert lifecycle["promotion_claims"] == validator.promotion_claims()
    assert all(value is False for value in lifecycle["promotion_claims"].values())
    assert all(
        value is False for value in model["replay_plan_contract"]["plan_claim_boundary"].values()
    )


def test_lifecycle_maps_are_truthful_and_stage_specific(model: dict[str, Any]) -> None:
    lifecycle = model["wire_schema_contract"]["lifecycle_maps"]
    for stage in ("source_and_rows", "semantic_receipt", "outer_receipt"):
        assert lifecycle[stage] == validator.lifecycle_observations(stage)
    assert lifecycle["source_and_rows"]["this_clean_child_validation_completed"] is False
    assert lifecycle["semantic_receipt"]["this_clean_child_validation_completed"] is True
    assert lifecycle["outer_receipt"]["two_clean_child_match_completed"] is True
    assert lifecycle["outer_receipt"]["outer_validation_completed"] is True


def test_all_normative_internal_pointers_resolve(model: dict[str, Any]) -> None:
    prefixes = (
        "/wire_schema_contract/",
        "/replay_plan_contract/",
        "/publication_contract/",
        "/process_contract/",
    )
    pointers = [
        value
        for _, value in validator._walk(model)
        if isinstance(value, str) and value.startswith(prefixes)
    ]
    assert len(pointers) == 99
    assert len(set(pointers)) == 49
    for pointer in pointers:
        assert validator._json_pointer(model, pointer) is not None


def test_exact_artifact_topology_and_row_schema_transform(
    model: dict[str, Any],
) -> None:
    artifact = model["artifact_contract"]
    assert artifact["totals"] == {
        "configuration_rows": 12,
        "contact_interval_bytes": 3_730_224,
        "contact_interval_records": 233_139,
        "directories": 14,
        "files": 73,
        "profile_files": 48,
        "profile_interval_bytes": 109_632,
        "profile_interval_records": 6_852,
        "raw_numerical_leaves": 60,
        "row_manifests": 12,
        "top_manifests": 1,
    }
    assert len(artifact["rows"]) == 12
    assert [row["configuration_index"] for row in artifact["rows"]] == list(range(12))
    assert {row["row_schema"] for row in artifact["rows"]} == {validator.ROW_SCHEMA}
    assert len(artifact["directory_paths"]) == 14
    assert len(artifact["file_paths"]) == 73


def test_classification_partitions_and_digest_domains(model: dict[str, Any]) -> None:
    contact = model["classification_contract"]["contact"]
    assert contact["global_counts"] == {
        "full": 4_142,
        "partial": 1_304,
        "total": 233_139,
        "zero": 227_693,
    }
    assert sum(contact["global_counts"][key] for key in ("zero", "full", "partial")) == (233_139)
    assert contact["classification_digest"]["label_bytes"] == {
        "full": "0x01",
        "partial": "0x02",
        "zero": "0x00",
    }
    assert contact["serialization"]["negative_zero"] == "forbidden"
    profile = model["classification_contract"]["profile"]
    assert profile["per_row_profile_ledger"]["cardinality"] == 48
    assert "all_6852" in profile["independent_verifier_scope"]
    assert "negative_zero_forbidden" in profile["outside_support"]


def test_precision_coverage_and_normalization_boundary(model: dict[str, Any]) -> None:
    assert model["numerical_semantics"]["precision"] == {
        "analytic_area_saved_bits": 256,
        "producer_contact_bits": 192,
        "producer_profile_bits": 192,
        "verifier_primary_bits": 384,
        "verifier_sentinel_bits": 512,
    }
    normalization = model["numerical_semantics"]["normalization_boundary"]
    assert normalization["W_inverse_in_contact"] == "forbidden"
    assert normalization["W_inverse_in_profile"] == "forbidden"
    assert model["verification_contract"]["contact_coverage"]["all_partial_cells_at_384"] == 1_304
    assert (
        model["verification_contract"]["profile_coverage"]["all_profile_cells_at_paired_384_512"]
        == 6_852
    )


def test_ten_slot_replay_plan_topology_and_exact_order(
    model: dict[str, Any],
) -> None:
    plan = model["replay_plan_contract"]
    assert plan["schema"] == validator.PLAN_SCHEMA
    assert plan["status"] == validator.PLAN_STATUS
    slots = plan["slot_templates"]
    assert [slot["ordinal"] for slot in slots] == list(range(10))
    assert [slot["role"] for slot in slots] == [8, 8, 8, 9, 9, 9, 10, 10, 10, 10]
    assert sum(slot["kind"] == "request" for slot in slots) == 3
    assert sum(slot["lifecycle"].startswith("must_be_absent") for slot in slots) == 7
    assert len({slot["slot_id"] for slot in slots}) == 10


def test_process_isolation_exact_argv_and_darwin_grammar(
    model: dict[str, Any],
) -> None:
    process = model["process_contract"]
    assert set(process["argv"]) == {
        "child_semantic_verifier",
        "producer",
        "transaction_orchestrator",
    }
    assert process["filesystem"]["umask"] == "0077"
    assert process["io_and_session"]["close_fds"] is True
    assert process["io_and_session"]["pass_fds"] == []
    assert process["io_and_session"]["shell"] is False
    assert process["io_and_session"]["stdin"] == "DEVNULL"
    for vector in process["argv"].values():
        assert vector[1:3] == ["-I", "-B"]
    grammar = process["environment"]["darwin_observation_exception"]
    assert "^0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+$" in grammar
    deadlines = process["deadline_accounting"]
    assert deadlines["outer_total_seconds"] == 2_700
    assert deadlines["semantic_seconds"] == 1_140
    assert deadlines["outer_nonchild_reserve_seconds"] == 300
    assert deadlines["phase_caps_seconds"] == {
        "producer_including_signal_reap": 1_200,
        "semantic_children_concurrent_including_signal_reap": 1_140,
        "transaction_orchestrator_total": 2_700,
    }
    assert 1_200 + 1_140 + 300 == 2_640 <= 2_700
    assert "concurrent" in deadlines["timing_rule"]


def test_ack_and_three_run_observation_contracts(model: dict[str, Any]) -> None:
    process = model["process_contract"]
    observations = process["run_observation_contract"]
    assert observations["cardinality"] == 3
    assert observations["order"] == [
        "producer_child",
        "semantic_child_0",
        "semantic_child_1",
    ]
    acknowledgements = process["ack_contracts"]
    assert set(acknowledgements) == {
        "encoding",
        "maximum_bytes",
        "producer_child",
        "public_transaction_commit",
        "semantic_child",
    }
    assert acknowledgements["producer_child"]["exact_keys"] == [
        "darwin_cf_user_text_encoding_observation",
        "schema",
        "staged_artifact_binding_sha256",
        "status",
    ]
    public_ack = acknowledgements["public_transaction_commit"]
    assert public_ack["exact_keys"] == [
        "artifact_binding_sha256",
        "darwin_cf_user_text_encoding_observation",
        "outer_receipt_sha256",
        "schema",
        "semantic_receipt_sha256",
        "status",
    ]
    composite_pointer = "/process_contract/digest_contracts/staged_artifact_binding_sha256"
    assert public_ack["field_schemas"]["artifact_binding_sha256"] == composite_pointer
    assert (
        acknowledgements["producer_child"]["field_schemas"]["staged_artifact_binding_sha256"]
        == composite_pointer
    )
    assert (
        "top_manifest_envelope"
        in process["digest_contracts"]["staged_artifact_binding_sha256"]["preimage"]
    )
    assert (
        "file_inventory_tree_sha256"
        in process["digest_contracts"]["staged_artifact_binding_sha256"]["preimage"]
    )


def test_plan_v2_runner_runtime_and_cross_request_boundaries(
    model: dict[str, Any],
) -> None:
    replay = model["replay_plan_contract"]
    runtime = replay["runtime_closure"]
    assert runtime["schema"] == validator.RUNTIME_SCHEMA
    assert runtime["exact_keys"] == [
        "claim_boundary",
        "global_runner",
        "host_runtime_trust_boundary",
        "process_contract",
        "roles",
        "schema",
        "status",
    ]
    assert runtime["claim_boundary"]["complete_host_runtime_image"] is False
    assert runtime["claim_boundary"]["host_runtime_dependencies_byte_pinned"] is False
    assert runtime["field_schemas"]["global_runner"]["object_schema"] == (
        "/replay_plan_contract/objects/runtime_global_runner"
    )
    assert (
        runtime["field_schemas"]["host_runtime_trust_boundary"]["object_schema"]
        == "/replay_plan_contract/objects/runtime_host_trust_boundary"
    )
    runner = replay["global_replay_runner_contract"]
    assert runner["entrypoint_basename"] == ("execute_continuum_c1_n0_roles_8_10_replay_v2.py")
    assert runner["runner_id"] == "roles_8_10_global_replay_runner_v2"
    assert "runner_contract_sha256" in runner["runtime_binding"]
    request = replay["request_contract"]
    assert request["join_rules"][-1] == (
        "all_three_requests_have_byte_identical_external_predecessor_commitment_pin_"
        "plan_pin_shared_precommit_context_sha256_and_shared_replay_context_sha256_values"
    )
    assert request["shared_replay_preimage"]["exact_keys"] == [
        "external_predecessor_commitment_sha256",
        "replay_plan_sha256",
        "shared_precommit_context_sha256",
    ]


def test_recovery_journal_state_and_auxiliary_receipt_contract(
    model: dict[str, Any],
) -> None:
    publication = model["publication_contract"]
    journal = publication["recovery_journal"]
    assert journal["exact_keys"] == [
        "auxiliary_semantic_receipts",
        "journal_identity",
        "owned_stage_root",
        "output_parent_identity",
        "prepublication_journal_snapshot_sha256",
        "request_sha256",
        "staged_identity_ledger_sha256",
        "staged_outputs",
        "state",
        "target_slots",
    ]
    states = journal["state_order"]
    assert len(states) == len(set(states)) == 28
    assert states[0] == "INTENT_DURABLE"
    assert states[-1] == "COMMITTED"
    assert len(journal["state_value_matrix"]) == 19
    auxiliary = model["receipt_contract"]["temporary_child_receipts"]
    assert auxiliary["cardinality"] == 2
    assert auxiliary["paths_in_run_order"] == [
        ".semantic-child-0-receipt.json",
        ".semantic-child-1-receipt.json",
    ]
    assert all(
        "/" not in path and path.startswith(".") and path.endswith(".json")
        for path in auxiliary["paths_in_run_order"]
    )
    assert journal["field_schemas"]["auxiliary_semantic_receipts"]["cardinality"] == 2
    parent_checks = publication["output_parent"]["path_rebind_identity_checks"]
    assert "before_caller_commit_ACK" in parent_checks
    assert all("after_caller" not in check for check in parent_checks)


def test_three_output_transaction_and_parent_global_lock(
    model: dict[str, Any],
) -> None:
    publication = model["publication_contract"]
    assert publication["install_order"] == [
        "artifact_directory",
        "canonical_semantic_receipt_sibling",
        "outer_validation_receipt_sibling",
    ]
    assert "journal" in json.dumps(publication["recovery_journal"]).lower()
    assert "owned" in json.dumps(publication["rollback"]).lower()
    lock = publication["single_writer_lock"]
    assert "independent_of_request_or_target_names" in lock["identity"]
    assert "persistent" in lock["identity"]
    assert "same_authenticated_output_parent" in lock["serialization_scope"]


def test_no_numerical_payload_future_hash_or_stale_reference(
    model: dict[str, Any],
) -> None:
    serialized = json.dumps(model, sort_keys=True)
    assert '"document_sha256"' not in serialized
    assert "closed_object_schemas" not in serialized
    assert "model_section_binding_" not in serialized
    forbidden = model["forbidden_surface"]
    assert forbidden["future_code_hashes"].startswith("required_in_runtime_closure")
    assert forbidden["unknown_future_output_or_result_hash_pins"] == "forbidden"
    assert forbidden["forbidden_scientific_payloads"]


@pytest.mark.parametrize(
    "bad_raw",
    [
        b'{"a":1,"a":2}\n',
        b'{"a":1.0}\n',
        b'{"a":NaN}\n',
        b'{"a": 1}\\n',
        b'{"a":"\\u00e9"}\n',
    ],
)
def test_strict_canonical_parser_rejects_ambiguous_bytes(bad_raw: bytes) -> None:
    with pytest.raises(validator.OperationModelV2ValidationError):
        validator.parse_canonical_json(bad_raw, "bad")


def test_builder_check_and_validator_cli_are_read_only() -> None:
    before = ARTIFACT.read_bytes()
    subprocess.run(
        [sys.executable, str(BUILDER_PATH), "--check"],
        cwd=REPORT,
        check=True,
        capture_output=True,
        text=True,
    )
    frozen = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH)],
        cwd=REPORT,
        check=True,
        capture_output=True,
        text=True,
    )
    semantic = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--no-frozen-sha"],
        cwd=REPORT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert frozen.stdout.startswith("PASS_ROLE10_OPERATION_MODEL_V2_SEMANTIC ")
    assert semantic.stdout == frozen.stdout
    assert ARTIFACT.read_bytes() == before
