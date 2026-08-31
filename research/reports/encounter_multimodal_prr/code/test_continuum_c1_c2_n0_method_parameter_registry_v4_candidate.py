"""Positive tests for the standalone method-parameter registry v4."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/build_continuum_c1_c2_n0_method_parameter_registry_v4_candidate.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_c2_n0_method_parameter_registry_v4_candidate.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json"
ACCEPTED_VERIFIER = (
    REPORT / "code/rate_defined_tensor_f0_production_killing_geometry_independent.py"
)
ACCEPTED_VERIFIER_TEST = (
    REPORT / "code/test_rate_defined_tensor_f0_production_killing_geometry_independent.py"
)
V3_ARTIFACT = (
    REPORT / "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v3_candidate.json"
)
DOMAIN = "encounter-outward-method-parameters-v4"
ORDER = [
    "stationary_directed_mpfr_320_v2",
    "stationary_directed_mpfr_640_sentinel_v2",
    "raw_flux_directed_mpfr_320_v2",
    "raw_flux_directed_mpfr_640_sentinel_v2",
    "raw_flux_binary64_decode_v2",
    "exact_fraction_expression_dag_v2",
    "killing_contact_profile_mpfr_192_v3",
    "killing_analytic_disk_area_mpfr_256_v3",
    "killing_source_independent_same_backend_verifier_v3",
    "killing_exact_contact_cell_classification_v3",
]


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def policy_digest(domain: str, preimage: dict[str, Any]) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\0" + canonical(preimage)).hexdigest()


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return subprocess.run(
        [sys.executable, "-I", "-B", *arguments],
        cwd=REPORT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )


def load(path: Path = ARTIFACT) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def records_by_id() -> dict[str, dict[str, Any]]:
    return {record["parameter_id"]: record["parameters"] for record in load()["parameters"]}


def test_builder_check_validator_and_fresh_no_replace(tmp_path: Path) -> None:
    checked = run(str(BUILDER), "--check")
    assert checked.returncode == 0, checked.stderr
    assert "PASS_METHOD_PARAMETER_REGISTRY_V4_CANDIDATE_CHECK" in checked.stdout
    validated = run(str(VALIDATOR))
    assert validated.returncode == 0, validated.stderr
    assert "PASS_METHOD_PARAMETER_REGISTRY_V4_CANDIDATE_VALIDATION" in validated.stdout

    output = tmp_path / "registry.json"
    built = run(str(BUILDER), "--output", str(output))
    assert built.returncode == 0, built.stderr
    assert output.read_bytes() == ARTIFACT.read_bytes()
    assert output.stat().st_mode & 0o777 == 0o444
    assert output.stat().st_nlink == 1
    refused = run(str(BUILDER), "--output", str(output))
    assert refused.returncode != 0
    assert "refusing to replace existing output" in refused.stderr


def test_exact_top_level_shape_order_claims_and_v4_digests() -> None:
    registry = load()
    assert set(registry) == {
        "claim_boundary",
        "parameter_count",
        "parameters",
        "schema",
        "status",
    }
    assert registry["schema"] == (
        "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
    )
    assert registry["parameter_count"] == 10
    assert len(registry["claim_boundary"]) == 18
    assert set(registry["claim_boundary"].values()) == {False}
    assert [record["parameter_id"] for record in registry["parameters"]] == ORDER
    for record in registry["parameters"]:
        expected = hashlib.sha256(
            DOMAIN.encode("ascii") + b"\0" + canonical(record["parameters"])
        ).hexdigest()
        assert record["method_parameter_sha256"] == expected


def test_v3_history_and_first_six_semantics_are_preserved() -> None:
    assert hashlib.sha256(V3_ARTIFACT.read_bytes()).hexdigest() == (
        "6c1879edaefe5f99da4fffcb76e12466862577376c305e14c857b880067e3b32"
    )
    v3 = load(V3_ARTIFACT)["parameters"]
    v4 = load()["parameters"]
    assert [(record["parameter_id"], record["parameters"]) for record in v4[:6]] == [
        (record["parameter_id"], record["parameters"]) for record in v3[:6]
    ]
    assert all(
        left["method_parameter_sha256"] != right["method_parameter_sha256"]
        for left, right in zip(v3[:6], v4[:6], strict=True)
    )


def test_role10_producer_and_analytic_anchor_are_implementation_sufficient() -> None:
    records = records_by_id()
    producer = records["killing_contact_profile_mpfr_192_v3"]
    assert producer["precision_bits"] == 192
    assert producer["contact_fraction_record_format"] == ">dd"
    assert producer["support_density_record_format"] == ">dd"
    assert producer["panels_per_unit"] == 16384
    assert producer["support_panel_rule"] == "even(max(2,ceil_exact(length*16384)))"
    assert producer["support_fourth_derivative_global_bound"] == "322000/1"
    assert producer["support_simpson_remainder"] == "length*h^4*M4/180"
    assert producer["support_normalization_division"] == ("outward_positive_interval_division")
    assert producer["contact_area_relative_width_gate"] == "1/10000000000"
    assert producer["profile_integral_relative_width_gate"] == "1/10000000000"
    assert producer["published_contact_width_gate"] == "1/1099511627776"
    assert producer["profile_cell_mass_width_gate"] == "1/1099511627776"
    for primitive in ("sqrt", "asin", "quadrant_inclusion_exclusion", "[0,1]_clipping"):
        assert primitive in producer["contact_algorithm"]

    anchor = records["killing_analytic_disk_area_mpfr_256_v3"]
    assert anchor["formula"] == "pi_times_radius_squared"
    assert anchor["analytic_area_precision_bits"] == 256
    assert anchor["oracle_precision_bits"] == 384
    assert anchor["sentinel_precision_bits"] == 512
    assert anchor["analytic_area_relative_width_gate"] == "1/1000000000000"
    assert anchor["containment_chain"] == [
        "saved_256_contains_oracle_384",
        "oracle_384_contains_sentinel_512",
    ]


def test_role10_verifier_binds_precision_containment_resources_and_policies() -> None:
    verifier = records_by_id()["killing_source_independent_same_backend_verifier_v3"]
    assert verifier["independent_backend"] is False
    assert verifier["source_independence"] == (
        "oracle_reconstruction_from_frozen_role3_sources_without_using_published_"
        "192_bit_producer_values_while_the_verifier_reads_those_values_as_"
        "candidate_enclosures_for_containment"
    )
    assert verifier["primary_precision_bits"] == 384
    assert verifier["sentinel_precision_bits"] == 512
    assert verifier["contact_containment_relations"] == [
        "published_192_contains_primary_384_for_every_partial_contact_cell",
        "primary_384_contains_sentinel_512_for_first_partial_contact_cell_per_row",
        "published_192_contains_sentinel_512_for_first_partial_contact_cell_per_row",
    ]
    assert verifier["analytic_area_containment"] == (
        "saved_256_contains_oracle_384_contains_sentinel_512"
    )
    assert verifier["contact_cell_verification"] == (
        "every_partial_contact_cell_independently_recomputed_at_384_bits_"
        "and_first_partial_contact_cell_per_row_at_512_bits"
    )
    assert verifier["support_cell_verification"] == (
        "every_support_cell_and_aggregate_at_384_and_512_bits"
    )
    assert verifier["contact_oracle_width_gate"] == (
        "1/1532495540865888858358347027150309183618739122183602176"
    )
    assert verifier["oracle_to_nonzero_producer_width_max"] == "1/8"
    assert verifier["aggregate_profile_relative_width_gate"] == "1/10000000000"
    assert verifier["primary_target_width"] == "1/18446744073709551616"
    assert {
        key: verifier[key]
        for key in (
            "maximum_tree_files",
            "maximum_tree_directories",
            "maximum_tree_relative_depth",
            "maximum_tree_total_bytes",
            "maximum_json_file_bytes",
            "maximum_raw_contact_file_bytes",
            "maximum_raw_support_file_bytes",
        )
    } == {
        "maximum_tree_files": 256,
        "maximum_tree_directories": 64,
        "maximum_tree_relative_depth": 3,
        "maximum_tree_total_bytes": 67108864,
        "maximum_json_file_bytes": 2097152,
        "maximum_raw_contact_file_bytes": 553840,
        "maximum_raw_support_file_bytes": 3312,
    }
    assert verifier["maximum_simpson_panels"] == 2**22
    assert verifier["maximum_simpson_dyadic_depth"] == 64
    assert verifier["maximum_simpson_dfs_stack"] == 65
    assert verifier["maximum_bump_breakpoints"] == 20000
    assert verifier["flat_tail_threshold"] == 2048
    assert verifier["maximum_dyadic_coordinate_component_bits"] == 256
    assert verifier["maximum_mpfr_to_mpq_denominator_bits"] == 4096
    assert verifier["maximum_simpson_exact_component_bits"] == 8192
    assert verifier["semantic_deadline_seconds"] == 1140
    assert verifier["child_process_deadline_seconds"] == 1200
    assert verifier["outer_nonchild_reserve_seconds"] == 300
    assert verifier["outer_deadline_seconds"] == 2700
    assert {
        key: verifier[key]
        for key in (
            "maximum_child_semantic_receipt_bytes",
            "maximum_child_observation_bytes",
            "maximum_child_ack_bytes",
            "maximum_child_stderr_bytes",
            "maximum_outer_receipt_bytes",
        )
    } == {
        "maximum_child_semantic_receipt_bytes": 2097152,
        "maximum_child_observation_bytes": 65536,
        "maximum_child_ack_bytes": 4096,
        "maximum_child_stderr_bytes": 4096,
        "maximum_outer_receipt_bytes": 262144,
    }


def test_role10_v4_claims_match_accepted_source_and_semantic_counts() -> None:
    registry = load()
    verifier = records_by_id()["killing_source_independent_same_backend_verifier_v3"]
    source = ACCEPTED_VERIFIER.read_text(encoding="utf-8")
    semantic_test = ACCEPTED_VERIFIER_TEST.read_text(encoding="utf-8")
    parse_candidate = source[
        source.index("def parse_candidate_bundle(") : source.index(
            "\ndef require_exact_containment(",
            source.index("def parse_candidate_bundle("),
        )
    ]
    verify_contact = source[
        source.index("def verify_contact_rows(") : source.index(
            "\ndef _bump_value_enclosure_with_tail(",
            source.index("def verify_contact_rows("),
        )
    ]
    verify_support = source[
        source.index("def verify_support_rows(") : source.index(
            "\ndef ",
            source.index("def verify_support_rows(") + 1,
        )
    ]

    assert "contact_raw = _read_candidate_entry(" in parse_candidate
    assert "support_raw = _read_candidate_entry(" in parse_candidate
    assert "candidate.contacts," in verify_contact
    assert "candidate.supports," in verify_support
    assert verify_contact.count("sentinel_done = False") == 1
    assert verify_contact.count("if not sentinel_done:") == 1
    assert verify_contact.count("sentinel_done = True") == 1
    assert 'assert contact["partial_oracle_count"] == 1_304' in semantic_test
    assert 'assert contact["sentinel_partial_count"] == 12' in semantic_test
    assert verifier["contact_cell_verification"] == (
        "every_partial_contact_cell_independently_recomputed_at_384_bits_"
        "and_first_partial_contact_cell_per_row_at_512_bits"
    )
    assert registry["status"].endswith("NOT_EXTERNALLY_COMMITTED")
    assert registry["claim_boundary"]["science_executed"] is False
    assert registry["claim_boundary"]["ordered_roles_8_10_replay_executed"] is False
    assert verifier["parent_sample_reuse"] is True
    assert verifier["dfs_order"] == "right_push_left_first_depth_first"
    assert verifier["accumulation"] == "balanced_exact_bin_accumulation"
    assert verifier["sentinel_evaluation_rule"] == (
        "512_bits_only_on_leaves_accepted_by_384_bit_primary"
    )
    assert verifier["paired_simpson_policy_sha256"] == (
        "0fb7e19ff04a60c0ebee938fc725fe49ba5c030bb3a18f2570bbabb519a25895"
    )
    assert verifier["flat_tail_policy_sha256"] == (
        "b7720e13964c58cb14a6f1ca9aa4060a45b0cfaf8108587a62333dcf14933f9a"
    )
    assert (
        policy_digest(
            verifier["paired_simpson_policy_digest_domain"],
            verifier["paired_simpson_policy_preimage"],
        )
        == verifier["paired_simpson_policy_sha256"]
    )
    assert (
        policy_digest(
            verifier["flat_tail_policy_digest_domain"],
            verifier["flat_tail_policy_preimage"],
        )
        == verifier["flat_tail_policy_sha256"]
    )
    assert verifier["paired_simpson_policy_preimage"]["schema"] == (
        "encounter_independent_paired_root_local_simpson_policy_v2"
    )
    assert verifier["flat_tail_policy_preimage"]["schema"] == (
        "encounter_independent_compact_bump_flat_tail_policy_v1"
    )


def test_role10_aggregate_identities_and_all_precision_containments_are_explicit() -> None:
    verifier = records_by_id()["killing_source_independent_same_backend_verifier_v3"]
    assert verifier["contact_aggregate_identity"] == (
        "each_row_volume_weighted_contact_cell_sum_contains_analytic_pi_times_radius_squared"
    )
    assert verifier["support_aggregate_identity"] == (
        "each_compact_support_profile_volume_weighted_cell_mass_sum_contains_exact_one"
    )
    assert verifier["support_containment_relations"] == [
        "published_192_contains_primary_384_per_cell_and_aggregate",
        "primary_384_contains_sentinel_512_per_cell_and_aggregate",
        "published_192_contains_sentinel_512_per_cell_and_aggregate",
    ]


def test_exact_classification_and_role10_scope_are_frozen() -> None:
    records = records_by_id()
    classification = records["killing_exact_contact_cell_classification_v3"]
    assert classification["zero_rule"] == (
        "nearest_squared_distance_of_every_wrapped_segment_outside_closed_disk"
    )
    assert classification["full_rule"] == (
        "all_corners_of_every_exact_wrapped_segment_inside_or_on_closed_disk"
    )
    assert classification["partial_rule"] == "otherwise_partial_directed_interval"
    assert classification["periodic_segmentation"] == "exact_wrapped_periodic_segments"
    assert classification["tangency_convention"] == "boundary_tangency_is_measure_zero"
    assert classification["zero_serialization"] == "exact_[0,0]"
    assert classification["full_serialization"] == "exact_[1,1]"
    for identifier in ORDER[6:]:
        assert records[identifier]["source_role_scope"] == ["role10_killing_factor_geometry"]


def test_registry_is_result_blind_and_contains_only_policy_hashes() -> None:
    registry = load()

    def keys(node: Any) -> list[str]:
        if type(node) is dict:
            return [key for key, value in node.items() for key in [key, *keys(value)]]
        if type(node) is list:
            return [key for value in node for key in keys(value)]
        return []

    all_keys = keys(registry)
    assert not [
        key
        for key in all_keys
        if any(
            marker in key.lower()
            for marker in ("result", "observed", "accepted_leaf", "output_hash")
        )
    ]
    policy_hashes = {
        key for key in all_keys if key.endswith("_sha256") and key != "method_parameter_sha256"
    }
    assert policy_hashes == {
        "paired_simpson_policy_sha256",
        "flat_tail_policy_sha256",
    }


def test_builder_and_validator_are_source_separated() -> None:
    builder = BUILDER.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8")
    assert VALIDATOR.stem not in builder
    assert BUILDER.stem not in validator
    assert "import build_continuum_c1_c2_n0_method_parameter" not in validator
    assert "rate_defined_tensor_f0_production_killing_geometry_independent" not in builder
    assert "rate_defined_tensor_f0_production_killing_geometry_independent" not in validator
