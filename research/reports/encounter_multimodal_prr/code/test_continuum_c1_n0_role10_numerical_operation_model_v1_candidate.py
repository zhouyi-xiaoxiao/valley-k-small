"""Positive tests for the result-blind role-10 numerical operation model."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

CODE = Path(__file__).resolve().parent
REPORT = CODE.parent
BUILDER_PATH = CODE / "build_continuum_c1_n0_role10_numerical_operation_model_v1_candidate.py"
VALIDATOR_PATH = CODE / "validate_continuum_c1_n0_role10_numerical_operation_model_v1_candidate.py"
ARTIFACT = (
    REPORT / "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v1_candidate.json"
)


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


builder = load_module("role10_operation_model_builder_tests", BUILDER_PATH)
validator = load_module("role10_operation_model_validator_tests", VALIDATOR_PATH)


@pytest.fixture(scope="module")
def model() -> dict[str, Any]:
    return builder.build_model()


def test_identity_status_and_all_claims_false(model: dict[str, Any]) -> None:
    assert model["schema"] == builder.SCHEMA
    assert model["status"] == builder.STATUS
    assert set(model["claim_boundary"]) == set(builder.CLAIM_KEYS)
    assert all(value is False for value in model["claim_boundary"].values())


def test_normative_dependencies_are_separate_from_authentication(
    model: dict[str, Any],
) -> None:
    authority = model["authority_model"]
    assert authority["normative_direct_role_dependencies"] == [1, 3, 5, 6, 7]
    assert "configuration_implementation" in authority["authentication_closure_roles"]
    assert "producer_runtime_closure" in authority["authentication_closure_roles"]
    assert "authentication_closure_roles" in authority["separation_rule"]


def test_sealed_mirror_is_exact_and_future_execution_uses_it(
    model: dict[str, Any],
) -> None:
    mirror = model["authority_model"]["sealed_authentication_mirror"]
    assert mirror["manifest_sha256"] == (
        "1ba1b582c17e90ab19f04f1aefce1ea5cf9a9dad8cbcfcaed309314014d8dc51"
    )
    assert (mirror["entry_count"], mirror["file_count"], mirror["directory_count"]) == (
        40,
        41,
        20,
    )
    assert mirror["total_bytes"] == 1_176_207
    assert mirror["validated_coverage"]["member_v4_partition_file_count"] == 36
    assert mirror["future_execution_source"].startswith("sealed_mirror_copies_only")


def test_registry_v4_and_four_exact_method_records(model: dict[str, Any]) -> None:
    method = model["method_contract"]
    assert (
        method["registry_binding"]["sha256"]
        == builder.AUTHORITY_SPECS["method_parameter_registry"][2]
    )
    assert method["method_record_order"] == list(builder.METHOD_IDS)
    assert method["method_record_digests"] == list(builder.METHOD_DIGESTS)
    assert len(method["selected_records"]) == 4
    for record, digest in zip(
        method["selected_records"],
        builder.METHOD_DIGESTS,
        strict=True,
    ):
        assert record["method_parameter_sha256"] == digest
        assert builder._method_digest(record["parameters"]) == digest


def test_exact_73_file_14_directory_topology(model: dict[str, Any]) -> None:
    artifact = model["artifact_contract"]
    assert len(artifact["directory_paths"]) == 14
    assert len(artifact["file_paths"]) == 73
    assert artifact["directory_paths"][:2] == [".", "rows"]
    assert artifact["file_paths"][0] == "manifest.json"
    assert artifact["totals"]["raw_numerical_leaves"] == 60
    assert artifact["totals"]["profile_files"] == 48


def test_row_paths_shapes_counts_and_byte_lengths(model: dict[str, Any]) -> None:
    rows = model["artifact_contract"]["rows"]
    assert len(rows) == 12
    contact_records = 0
    profile_records = 0
    for index, row in enumerate(rows):
        n_m, n_r, n_y = row["state_shape"]
        assert row["row_directory"] == f"rows/row_{index:02d}"
        assert row["row_manifest_path"] == f"rows/row_{index:02d}/row.json"
        assert row["contact"]["record_count"] == n_r * n_y
        assert row["contact"]["byte_length"] == n_r * n_y * 16
        assert row["future_V_metadata_only"]["logical_shape"] == [n_m, n_r, n_y]
        assert row["future_V_metadata_only"]["materialization"] == "forbidden"
        assert [profile["profile_index"] for profile in row["profiles"]] == [0, 1, 2, 3]
        assert all(profile["record_count"] == n_m for profile in row["profiles"])
        assert all(profile["byte_length"] == n_m * 16 for profile in row["profiles"])
        contact_records += row["contact"]["record_count"]
        profile_records += sum(profile["record_count"] for profile in row["profiles"])
    assert contact_records == 233_139
    assert profile_records == 6_852


def test_top_inventory_excludes_self(model: dict[str, Any]) -> None:
    artifact = model["artifact_contract"]
    inventory = artifact["top_file_inventory"]
    assert inventory["entry_count"] == 72
    assert inventory["ordered_paths"] == artifact["file_paths"][1:]
    assert "manifest.json" not in inventory["ordered_paths"]


def test_source_row_raw_schemas_and_exact_key_sets(model: dict[str, Any]) -> None:
    artifact = model["artifact_contract"]
    assert artifact["schemas"] == {
        "raw_interval_file": builder.RAW_SCHEMA,
        "row": builder.ROW_SCHEMA,
        "source": builder.SOURCE_SCHEMA,
    }
    keys = artifact["schema_key_contracts"]
    assert "schema" in keys["raw_manifest_exact_keys"]
    assert "record_count" in keys["profile_section_exact_keys"]
    for required in (
        "operation_model_binding",
        "replay_plan_binding",
        "candidate_bundle_binding",
        "request_binding",
        "external_commitment_binding",
        "producer_runtime_closure",
        "sealed_authentication_mirror_binding",
    ):
        assert required in keys["top_manifest_exact_keys"]


def test_binary_encoding_and_saved_precision_boundary(model: dict[str, Any]) -> None:
    encoding = model["artifact_contract"]["encoding"]
    assert encoding == {
        "byte_order": "big",
        "endpoint_semantics": "closed_outward_binary64",
        "record_byte_length": 16,
        "record_format": ">dd",
    }
    stored = model["artifact_contract"]["stored_precision_policy"]
    assert stored["contact_and_profile_payloads"] == ("producer_192_bit_outward_intervals_only")
    assert "manifest.json#/normalization_anchor/" in stored["analytic_disk_area_anchor"]
    assert "256" in stored["analytic_disk_area_anchor"]


def test_exact_tangent_equality_classification(model: dict[str, Any]) -> None:
    contact = model["numerical_semantics"]["contact"]
    classification = contact["cell_classification"]
    assert classification["zero_segment_pair"] == (
        "nearest_squared_distance_greater_than_or_equal_to_radius_squared"
    )
    assert classification["full_segment_pair"] == (
        "all_four_corner_squared_distances_less_than_or_equal_to_radius_squared"
    )
    assert classification["partial_segment_pair"] == "otherwise"
    assert "equality" in contact["tangent_equality_convention"]
    assert contact["derived_expected_partial_cell_count"] == 1_304
    assert "not_method_threshold" in contact["derived_count_role"]


def test_profile_density_cell_mass_width_and_units(model: dict[str, Any]) -> None:
    profile = model["numerical_semantics"]["profile"]
    assert profile["stored_quantity"] == "cell_average_density_not_cell_mass"
    assert profile["units"] == "inverse_length"
    assert profile["cell_mass_width_definition"] == (
        "cell_volume_exact*(published_upper_exact-published_lower_exact)"
    )
    assert "exact_cell_volume_times_Phi_jm" in profile["unit_mass_identity"]
    assert model["numerical_semantics"]["producer_gates"]["profile_cell_mass_width"] == (
        "1/1099511627776"
    )


def test_W_inverse_is_absent_from_role10_payloads(model: dict[str, Any]) -> None:
    boundary = model["numerical_semantics"]["normalization_boundary"]
    assert boundary["W_inverse_in_contact"] == "forbidden"
    assert boundary["W_inverse_in_profile"] == "forbidden"
    assert boundary["later_factorization_only"] == "V_jmab=W^-1*C_ab*Phi_jm"


def test_verifier_384_512_coverage_and_ratio_gates(model: dict[str, Any]) -> None:
    verification = model["verification_contract"]
    contact = verification["contact_coverage"]
    profile = verification["profile_coverage"]
    assert contact["all_partial_cells_at_384"] == 1_304
    assert contact["first_partial_cell_per_row_at_512"] == 12
    assert "1/8" in contact["ratio_gate"]
    assert contact["ratio_scope"] == "partial_nonzero_producer_widths_only"
    assert profile["all_profile_cells_at_paired_384_512"] == 6_852
    assert profile["all_profile_aggregates_at_paired_384_512"] == 48
    assert "1/8" in profile["ratio_gate"]
    assert "exact_zero_cells_excluded" in profile["ratio_scope"]


def test_two_clean_child_receipt_topology_and_caps(model: dict[str, Any]) -> None:
    receipt = model["receipt_contract"]
    assert receipt["child_observation_count"] == 2
    assert "byte_identical" in receipt["child_semantic_body_rule"]
    assert receipt["semantic_receipt"]["schema"] == builder.SEMANTIC_RECEIPT_SCHEMA
    assert receipt["semantic_receipt"]["maximum_bytes"] == 2_097_152
    assert receipt["outer_receipt"]["schema"] == builder.OUTER_RECEIPT_SCHEMA
    assert receipt["outer_receipt"]["maximum_bytes"] == 262_144
    assert all(value is False for value in receipt["semantic_receipt"]["claim_boundary"].values())
    assert all(value is False for value in receipt["outer_receipt"]["claim_boundary"].values())


def test_three_outputs_and_global_plan_v2_slot_count(model: dict[str, Any]) -> None:
    slots = model["receipt_contract"]["slot_contract"]
    assert slots["role10_output_count"] == 3
    assert slots["role10_slots_including_request"] == 4
    assert slots["roles8_9_slots_each"] == 3
    assert slots["global_plan_v2_slot_count"] == 10
    assert set(slots["slots"]) == {
        "artifact",
        "outer_validation_receipt",
        "request",
        "semantic_receipt",
    }


def test_all_invocations_require_isolated_python(model: dict[str, Any]) -> None:
    invocations = model["invocation_contract"]
    for key in (
        "producer_argv",
        "outer_verifier_argv",
        "child_semantic_verifier_argv",
    ):
        assert invocations[key][1:3] == ["-I", "-B"]
    outer = invocations["outer_verifier_argv"]
    assert "--semantic-receipt" in outer
    assert "--receipt" in outer


def test_process_environment_group_timeout_and_cleanup_are_frozen(
    model: dict[str, Any],
) -> None:
    process = model["invocation_contract"]["process_isolation_and_cleanup"]
    assert process["child_process_group"] == "one_new_process_group_per_clean_child"
    assert "no_PYTHONPATH" in process["child_environment"]
    assert process["semantic_deadline_seconds"] == 1_140
    assert process["wall_deadline_seconds"] == 1_200
    assert process["stdout_ack_bytes_maximum"] == 4_096
    assert process["observation_bytes_maximum"] == 65_536
    assert "terminate_process_group" in process["cleanup"]


def test_only_pinned_protocol_module_may_be_shared(model: dict[str, Any]) -> None:
    shared = model["invocation_contract"]["shared_module_boundary"]
    assert shared["numerical_source_sets"] == "producer_and_verifier_disjoint"
    assert "protocol_only" in shared["allowed_shared_surface"]
    assert shared["shared_unpinned_module"] == "forbidden"


def test_future_publication_parent_and_mode_transitions(model: dict[str, Any]) -> None:
    publication = model["publication_contract"]
    assert publication["output_parent"] == {
        "creation_by_role10": "forbidden",
        "group_or_world_writable": "forbidden",
        "mode": "0700",
        "must_preexist": "required",
        "owner": "effective_uid",
        "same_filesystem_for_all_three_outputs": "required",
    }
    assert publication["file_mode_transition"] == "0600_staging_to_0444_published"
    assert publication["directory_mode_transition"] == "0700_staging_to_0555_published"
    assert publication["destination_policy"].endswith("never_replaced")
    assert publication["publication_order"] == [
        "artifact_directory",
        "canonical_semantic_receipt_sibling",
        "outer_validation_receipt_sibling",
    ]


def test_resource_caps_are_registry_v4_values(model: dict[str, Any]) -> None:
    caps = model["resource_caps"]
    assert caps["maximum_simpson_panels"] == 4_194_304
    assert caps["maximum_simpson_dyadic_depth"] == 64
    assert caps["maximum_simpson_dfs_stack"] == 65
    assert caps["maximum_bump_breakpoints"] == 20_000
    assert caps["maximum_raw_contact_file_bytes"] == 553_840
    assert caps["maximum_raw_support_file_bytes"] == 3_312
    assert caps["semantic_deadline_seconds"] == 1_140
    assert caps["child_process_deadline_seconds"] == 1_200
    assert caps["outer_deadline_seconds"] == 2_700


def test_future_code_hashes_required_but_unknown_outputs_forbidden(
    model: dict[str, Any],
) -> None:
    forbidden = model["forbidden_surface"]
    assert forbidden["future_code_hashes"].startswith("required_in_runtime_closure")
    assert forbidden["unknown_future_output_or_result_hash_pins"] == "forbidden"
    assert "producer_code_sha256" not in forbidden["forbidden_precommit_or_artifact_fields"]
    assert "verifier_code_sha256" not in forbidden["forbidden_precommit_or_artifact_fields"]


def test_legacy_lineage_is_not_an_executable_import(model: dict[str, Any]) -> None:
    forbidden = model["forbidden_surface"]
    assert "rate_defined_tensor_f0" in forbidden["forbidden_legacy_import_prefixes"]
    assert "allowed_as_sealed_configuration_lineage" in forbidden["legacy_import_scope"]
    assert forbidden["legacy_result_bytes_read"] == "forbidden"


def test_builder_and_validator_have_no_cross_import_or_numerical_import() -> None:
    for path in (BUILDER_PATH, VALIDATOR_PATH):
        tree = ast.parse(path.read_text("utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )
        assert not any(name.startswith("rate_defined_tensor_f0") for name in imports)
        assert not any(name.startswith("numpy") for name in imports)
        assert not any(name.startswith("scipy") for name in imports)
    validator_source = VALIDATOR_PATH.read_text("utf-8")
    assert BUILDER_PATH.stem not in validator_source


def test_canonical_model_contains_no_float_and_roundtrips(model: dict[str, Any]) -> None:
    raw = builder.canonical_bytes(model)
    assert builder.parse_canonical_json(raw, "model") == model
    assert validator.parse_canonical_json(raw, "model") == model

    def walk(value: Any) -> None:
        assert not isinstance(value, float)
        if type(value) is list:
            for item in value:
                walk(item)
        elif type(value) is dict:
            for item in value.values():
                walk(item)

    walk(model)


def test_source_separated_semantic_validation(model: dict[str, Any]) -> None:
    raw = builder.canonical_bytes(model)
    validator.validate_value(model, raw=raw, enforce_frozen_sha=False)


def test_builder_publishes_and_checks_0444_one_link(tmp_path: Path) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"
    raw = builder.canonical_bytes(builder.build_model())
    builder.publish_no_replace(output, raw)
    observed = output.stat()
    assert stat.S_IMODE(observed.st_mode) == 0o444
    assert observed.st_nlink == 1
    assert builder.check(output) == hashlib.sha256(raw).hexdigest()


def test_builder_refuses_replace_and_preserves_existing(tmp_path: Path) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"
    output.write_bytes(b"foreign")
    output.chmod(0o444)
    with pytest.raises(builder.OperationModelBuildError, match="refusing to replace"):
        builder.publish_no_replace(output, b"candidate")
    assert output.read_bytes() == b"foreign"


def test_builder_refuses_group_world_writable_parent(tmp_path: Path) -> None:
    output = tmp_path / "model.json"
    tmp_path.chmod(0o777)
    try:
        with pytest.raises(builder.OperationModelBuildError, match="output parent"):
            builder.publish_no_replace(output, b"candidate")
    finally:
        tmp_path.chmod(0o700)


def test_builder_cli_temp_publication_and_check(tmp_path: Path) -> None:
    tmp_path.chmod(0o700)
    output = tmp_path / "model.json"
    built = subprocess.run(
        [sys.executable, str(BUILDER_PATH), "--output", str(output)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert built.returncode == 0, built.stderr
    checked = subprocess.run(
        [sys.executable, str(BUILDER_PATH), "--check", "--output", str(output)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert checked.returncode == 0, checked.stderr
    assert "PASS_ROLE10_OPERATION_MODEL" in checked.stdout


def test_published_artifact_is_immutable_and_validator_accepted() -> None:
    if not ARTIFACT.exists():
        pytest.skip("final candidate publication occurs after prepublication test pass")
    observed = ARTIFACT.stat()
    assert stat.S_IMODE(observed.st_mode) == 0o444
    assert observed.st_nlink == 1
    assert builder.check(ARTIFACT) == hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    assert validator.validate(ARTIFACT) == hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
