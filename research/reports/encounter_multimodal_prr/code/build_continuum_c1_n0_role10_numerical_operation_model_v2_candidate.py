"""Build the result-blind role-10 numerical operation model v2 candidate.

Version 2 preserves the accepted authority, topology, method, and resource
sections of the historical v1 draft while replacing every execution-facing
contract that the independent v1 audit rejected.  It does not implement or
run the role-10 numerics and it never pins future output or result bytes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any, Final, Sequence

CODE: Final = Path(__file__).resolve().parent
REPORT: Final = CODE.parent
V1_RELATIVE: Final = Path(
    "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v1_candidate.json"
)
V1_PATH: Final = REPORT / V1_RELATIVE
V1_SHA256: Final = "d0e4abd040865863f1cbf9768d17975f4fbd4310f47eda87d9878bd4fffd6109"
V1_SCHEMA: Final = "encounter_continuum_c1_n0_role10_numerical_operation_model_v1_candidate"
V1_BUILDER_PATH: Final = (
    CODE / "build_continuum_c1_n0_role10_numerical_operation_model_v1_candidate.py"
)
V1_BUILDER_SHA256: Final = "5937c180f65dc8865e6eb0303d00d87388987ce236d44617ee97cab554e0c9cd"

DEFAULT_OUTPUT: Final = (
    REPORT / "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v2_candidate.json"
)
SCHEMA: Final = "encounter_continuum_c1_n0_role10_numerical_operation_model_v2_candidate"
STATUS: Final = "RESULT_BLIND_CONTRACT_ONLY_CANDIDATE_NO_NUMERICAL_IMPLEMENTATION_OR_EXECUTION"

SOURCE_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_source_v4"
ROW_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_row_v2"
RAW_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_raw_interval_file_v2"
SEMANTIC_RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_semantic_receipt_v2"
OUTER_RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_validation_receipt_v3"
ROLE8_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_raw_axis_formula_request_v4"
ROLE9_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_stationary_integrals_request_v4"
ROLE10_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_killing_factor_geometry_request_v4"
PLAN_SCHEMA: Final = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v2"
PLAN_STATUS: Final = "RESULT_BLIND_PRECOMMIT_REPLAY_PLAN_NO_EXECUTION_RESULTS"
REQUEST_STATUS: Final = (
    "EXTERNAL_PREDECESSOR_COMMITMENT_BOUND_RESULT_BLIND_REQUEST_NO_EXECUTION_RESULT"
)
RUNTIME_SCHEMA: Final = "encounter_continuum_c1_n0_roles_8_10_implementation_runtime_closure_v1"


class OperationModelV2BuildError(RuntimeError):
    """Raised when the v2 model cannot be built or published safely."""


def fail(message: str) -> None:
    raise OperationModelV2BuildError(message)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_v1() -> tuple[dict[str, Any], bytes]:
    descriptor = os.open(
        V1_PATH,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o444
        ):
            fail("v1 lineage artifact is not an immutable single-link regular file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1 << 20)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            fail("v1 lineage artifact changed while read")
    finally:
        os.close(descriptor)
    raw = b"".join(chunks)
    if sha256(raw) != V1_SHA256:
        fail("v1 lineage SHA-256 drift")
    try:
        value = json.loads(raw.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(f"v1 lineage is not canonical ASCII JSON: {error}")
    if type(value) is not dict or canonical_bytes(value) != raw:
        fail("v1 lineage is not canonical")
    if value.get("schema") != V1_SCHEMA or value.get("status") != STATUS:
        fail("v1 lineage identity drift")
    return value, raw


def load_v1_publisher() -> Any:
    """Load only the hash-pinned, already-audited v1 publication primitive."""

    before = V1_BUILDER_PATH.read_bytes()
    if sha256(before) != V1_BUILDER_SHA256:
        fail("v1 builder publication primitive SHA-256 drift")
    specification = importlib.util.spec_from_file_location(
        "role10_operation_model_v1_publisher_for_v2",
        V1_BUILDER_PATH,
    )
    if specification is None or specification.loader is None:
        fail("cannot load v1 publication primitive")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    try:
        specification.loader.exec_module(module)
    finally:
        sys.modules.pop(specification.name, None)
    after = V1_BUILDER_PATH.read_bytes()
    if before != after or sha256(after) != V1_BUILDER_SHA256:
        fail("v1 builder publication primitive changed while loaded")
    publisher = getattr(module, "publish_no_replace", None)
    if not callable(publisher):
        fail("v1 publication primitive unavailable")
    return publisher


def precommit_claims() -> dict[str, bool]:
    return {
        "B06_cleared": False,
        "B06_structural_remedy_prepared": False,
        "backend_independence_claimed": False,
        "complete_C1": False,
        "external_predecessor_commitment_present": False,
        "numerical_execution_performed": False,
        "numerical_implementation_present": False,
        "ordered_roles_8_10_replay_executed": False,
        "production_same_member_bridge_accepted": False,
        "release_eligible": False,
        "role10_numerical_source_materialized": False,
        "same_member_acceptance": False,
        "science_executed": False,
        "submission_eligible": False,
    }


def promotion_claims() -> dict[str, bool]:
    return {
        "B06_cleared": False,
        "B06_structural_remedy_prepared": False,
        "backend_independence_claimed": False,
        "complete_C1": False,
        "ordered_roles_8_10_replay_executed": False,
        "production_same_member_bridge_accepted": False,
        "release_eligible": False,
        "same_member_acceptance": False,
        "submission_eligible": False,
    }


def lifecycle_observations(*, child: bool, matched_children: bool, outer: bool) -> dict[str, bool]:
    return {
        "external_predecessor_commitment_authenticated": True,
        "numerical_execution_completed": True,
        "numerical_implementation_authenticated": True,
        "outer_validation_completed": outer,
        "role10_numerical_source_materialized": True,
        "science_computation_executed": True,
        "this_clean_child_validation_completed": child,
        "two_clean_child_match_completed": matched_children,
    }


def envelope_contract(
    *,
    schema: str,
    status: str,
    digest_domain: str,
    payload_exact_keys: list[str],
) -> dict[str, Any]:
    return {
        "digest_rule": {
            "algorithm": "sha256",
            "domain": digest_domain,
            "preimage": "domain_ascii+NUL+canonical_payload_bytes",
        },
        "envelope_exact_keys": ["payload", "payload_digest", "schema", "status"],
        "payload_exact_keys": payload_exact_keys,
        "schema": schema,
        "status": status,
        "whole_file_sha256_rule": (
            "sha256_of_the_canonical_complete_envelope_bytes_recorded_only_in_the_"
            "containing_parent_binding_and_never_self_embedded"
        ),
    }


def closed_object_schemas() -> dict[str, Any]:
    """Return recursively closed schemas used by future source/receipt payloads."""

    return {
        "artifact_binding": {
            "exact_keys": [
                "manifest_sha256",
                "path",
                "schema",
                "tree_inventory_sha256",
            ],
            "types": {
                "manifest_sha256": "sha256_of_canonical_top_manifest_envelope_file",
                "path": "canonical_absolute_path",
                "schema": "exact_schema_string",
                "tree_inventory_sha256": "lowercase_sha256",
            },
        },
        "authority_bindings": {
            "exact_keys": [
                "anti_vacuity_policy",
                "configuration",
                "factorization",
                "ideal_formula",
                "initial_geometry",
                "initial_partition_bundle",
                "killing_geometry",
                "member_spec",
                "method_parameter_registry",
                "reference_density",
                "sealed_authentication_mirror",
            ],
            "value_schema": "schema_pin",
        },
        "canonical_pin": {
            "exact_keys": ["path", "sha256"],
            "types": {
                "path": "canonical_absolute_path",
                "sha256": "lowercase_sha256",
            },
        },
        "classification_ledger": {
            "exact_keys": ["contact", "profiles", "schema", "status"],
            "fields": {
                "contact": "contact_classification_ledger",
                "profiles": "profile_classification_ledger",
                "schema": "encounter_role10_classification_ledger_v2",
                "status": "COMPLETE_INDEPENDENT_CLASSIFICATION_NO_PROMOTION",
            },
        },
        "contact_classification_ledger": {
            "exact_keys": ["global_counts", "global_digest", "rows"],
            "cardinality": {"rows": 12},
            "fields": {
                "global_counts": "contact_count_object",
                "global_digest": "lowercase_sha256",
                "rows": "ordered_contact_row_classification_array",
            },
        },
        "contact_count_object": {
            "exact_keys": ["full", "partial", "total", "zero"],
            "types": {
                "full": "nonnegative_integer",
                "partial": "nonnegative_integer",
                "total": "nonnegative_integer",
                "zero": "nonnegative_integer",
            },
            "join": "zero_plus_full_plus_partial_equals_total",
        },
        "contact_row_classification": {
            "exact_keys": [
                "configuration_index",
                "digest",
                "full",
                "partial",
                "record_count",
                "zero",
            ],
            "types": {
                "configuration_index": "integer_0_through_11",
                "digest": "lowercase_sha256",
                "full": "nonnegative_integer",
                "partial": "nonnegative_integer",
                "record_count": "positive_integer",
                "zero": "nonnegative_integer",
            },
            "join": "zero_plus_full_plus_partial_equals_record_count",
        },
        "contact_section": {
            "exact_keys": [
                "analytic_area_anchor_reference",
                "flat_index",
                "logical_shape",
                "producer_classification_summary",
                "quality_gate_ledger",
                "raw_manifest",
                "record_count",
                "units",
                "weighted_area_enclosure_exact",
            ],
            "fields": {
                "analytic_area_anchor_reference": "package_section_binding",
                "flat_index": "literal_a*n_Y+b",
                "logical_shape": "two_positive_integer_array",
                "producer_classification_summary": ("producer_contact_classification_summary"),
                "quality_gate_ledger": "quality_gate_ledger",
                "raw_manifest": "raw_manifest",
                "record_count": "positive_integer",
                "units": "literal_dimensionless",
                "weighted_area_enclosure_exact": "exact_rational_interval",
            },
        },
        "cleanup_evidence": {
            "exact_keys": [
                "all_children_reaped",
                "foreign_paths_preserved",
                "owned_temporary_paths_remaining",
                "process_groups_remaining",
            ],
            "values": {
                "all_children_reaped": True,
                "foreign_paths_preserved": True,
                "owned_temporary_paths_remaining": 0,
                "process_groups_remaining": 0,
            },
            "scope": (
                "owned_temporary_paths_means_child_workdirs_HOME_TMPDIR_and_the_two_"
                "temporary_child_receipts_it_excludes_the_three_active_transaction_"
                "staging_objects_the_owned_stage_root_lock_and_journal_that_must_still_"
                "exist_when_the_prepublication_outer_receipt_is_serialized"
            ),
        },
        "configuration_binding": {
            "exact_keys": [
                "configuration_index",
                "configuration_row_canonical_sha256",
                "configuration_semantic_id",
            ],
            "types": {
                "configuration_index": "integer_0_through_11",
                "configuration_row_canonical_sha256": "lowercase_sha256",
                "configuration_semantic_id": ("configuration_semantic_id"),
            },
        },
        "configuration_semantic_id": {
            "exact_keys": [
                "authority_label",
                "refinement_family_id",
                "refinement_member_id",
            ],
            "types": {
                "authority_label": "nonempty_ASCII_string_equal_member_v4_row",
                "refinement_family_id": "nonempty_ASCII_identifier_equal_member_v4_row",
                "refinement_member_id": "nonempty_ASCII_identifier_equal_member_v4_row",
            },
        },
        "containment_ledger": {
            "exact_keys": [
                "analytic_area",
                "contact",
                "profiles",
                "quality_gates_passed",
            ],
            "fields": {
                "analytic_area": "analytic_area_containment_ledger",
                "contact": "contact_containment_ledger",
                "profiles": "profile_containment_ledger",
                "quality_gates_passed": "literal_true",
            },
        },
        "analytic_area_containment_ledger": {
            "exact_keys": [
                "primary_384",
                "primary_contains_sentinel",
                "saved_256",
                "saved_contains_primary",
                "sentinel_512",
            ],
            "types": {
                "primary_384": "exact_rational_interval",
                "primary_contains_sentinel": "literal_true",
                "saved_256": "exact_rational_interval",
                "saved_contains_primary": "literal_true",
                "sentinel_512": "exact_rational_interval",
            },
        },
        "contact_containment_ledger": {
            "exact_keys": [
                "classification_digest_matches",
                "partial_primary_contained",
                "partial_primary_count",
                "partial_sentinel_contained",
                "partial_sentinel_count",
                "quality_gate_ledger",
            ],
            "values": {
                "classification_digest_matches": True,
                "partial_primary_contained": True,
                "partial_primary_count": 1304,
                "partial_sentinel_contained": True,
                "partial_sentinel_count": 12,
            },
            "fields": {
                "quality_gate_ledger": {
                    "gate_set": "/wire_schema_contract/quality_gate_sets/semantic_verifier",
                    "object_schema": "/wire_schema_contract/objects/quality_gate_ledger",
                }
            },
        },
        "profile_containment_ledger": {
            "exact_keys": [
                "aggregate_primary_and_sentinel_contained",
                "aggregate_record_count",
                "cell_primary_and_sentinel_contained",
                "cell_record_count",
                "classification_digest_matches",
                "quality_gate_ledger",
            ],
            "values": {
                "aggregate_primary_and_sentinel_contained": True,
                "aggregate_record_count": 48,
                "cell_primary_and_sentinel_contained": True,
                "cell_record_count": 6852,
                "classification_digest_matches": True,
            },
            "fields": {
                "quality_gate_ledger": {
                    "gate_set": "/wire_schema_contract/quality_gate_sets/semantic_verifier",
                    "object_schema": "/wire_schema_contract/objects/quality_gate_ledger",
                }
            },
        },
        "dev_ino_pair": {
            "exact_keys": ["device", "inode"],
            "types": {
                "device": "positive_JSON_integer",
                "inode": "positive_JSON_integer",
            },
        },
        "journal_owned_stage_root": {
            "exact_keys": ["identity", "leaf_name"],
            "fields": {
                "identity": "JSON_null_or_dev_ino_pair",
                "leaf_name": (
                    "single_hidden_ASCII_leaf_below_the_authenticated_output_parent_"
                    "chosen_before_INTENT_DURABLE"
                ),
            },
        },
        "journal_auxiliary_semantic_receipt": {
            "exact_keys": ["relative_path", "run_ordinal", "staged_identity"],
            "fields": {
                "relative_path": (
                    "single_hidden_ASCII_leaf_below_the_owned_stage_root_equal_.semantic-"
                    "child-0-receipt.json_or_.semantic-child-1-receipt.json_matching_"
                    "run_ordinal"
                ),
                "run_ordinal": "literal_1_or_2",
                "staged_identity": "JSON_null_or_dev_ino_pair",
            },
        },
        "journal_staged_output": {
            "exact_keys": [
                "node_type",
                "stage_leaf",
                "staged_identity",
                "target_leaf",
                "target_slot_id",
            ],
            "fields": {
                "node_type": "literal_directory_or_regular_file",
                "stage_leaf": (
                    "single_canonical_ASCII_leaf_below_the_owned_stage_root_distinct_"
                    "from_every_other_stage_leaf"
                ),
                "staged_identity": "JSON_null_or_dev_ino_pair",
                "target_leaf": (
                    "single_canonical_ASCII_leaf_below_the_authenticated_output_parent_"
                    "distinct_from_every_other_target_leaf"
                ),
                "target_slot_id": (
                    "literal_role10_artifact_directory_or_role10_semantic_receipt_or_"
                    "role10_outer_validation_receipt"
                ),
            },
        },
        "journal_target_slot": {
            "exact_keys": ["node_type", "target_leaf", "target_slot_id"],
            "fields": {
                "node_type": "literal_directory_or_regular_file",
                "target_leaf": (
                    "single_canonical_ASCII_leaf_below_the_authenticated_output_parent"
                ),
                "target_slot_id": (
                    "literal_role10_artifact_directory_or_role10_semantic_receipt_or_"
                    "role10_outer_validation_receipt"
                ),
            },
        },
        "staged_identity_ledger_preimage": {
            "exact_keys": [
                "auxiliary_semantic_receipts",
                "owned_stage_root",
                "staged_outputs",
            ],
            "fields": {
                "auxiliary_semantic_receipts": (
                    "exactly_two_journal_auxiliary_semantic_receipt_objects_in_run_"
                    "ordinal_order_with_nonnull_staged_identity"
                ),
                "owned_stage_root": ("journal_owned_stage_root_with_nonnull_identity"),
                "staged_outputs": (
                    "exactly_three_journal_staged_output_objects_in_install_order_"
                    "with_nonnull_staged_identity"
                ),
            },
        },
        "file_inventory": {
            "exact_keys": ["directories", "entries", "entry_count", "tree_sha256"],
            "cardinality": {"directories": 14, "entries": 72, "entry_count": 72},
            "fields": {
                "directories": "ordered_unique_report_relative_directory_array",
                "entries": "ordered_file_inventory_entry_array",
                "entry_count": "literal_72",
                "tree_sha256": "lowercase_sha256",
            },
        },
        "package_section_binding": {
            "exact_keys": ["json_pointer", "path", "section_sha256"],
            "types": {
                "section_sha256": "sha256_of_canonical_section_value_bytes",
            },
            "values": {
                "json_pointer": "/payload/normalization_anchor",
                "path": "manifest.json",
            },
            "join": (
                "outer_and_top_manifest_validators_resolve_the_package_relative_"
                "manifest_path_recompute_the_normalization_anchor_section_sha256_and_"
                "require_exact_equality_without_embedding_the_complete_manifest_sha256_"
                "in_any_row"
            ),
        },
        "file_inventory_entry": {
            "exact_keys": ["byte_length", "mode", "path", "sha256"],
            "types": {
                "byte_length": "positive_integer",
                "mode": "literal_0444",
                "path": "canonical_report_relative_file_path",
                "sha256": "lowercase_sha256",
            },
        },
        "lifecycle_observations": {
            "exact_keys": [
                "external_predecessor_commitment_authenticated",
                "numerical_execution_completed",
                "numerical_implementation_authenticated",
                "outer_validation_completed",
                "role10_numerical_source_materialized",
                "science_computation_executed",
                "this_clean_child_validation_completed",
                "two_clean_child_match_completed",
            ],
            "types": "JSON_boolean_only",
            "values": "must_equal_the_stage_specific_frozen_lifecycle_map",
        },
        "layout_and_units": {
            "exact_keys": [
                "contact_flat_index",
                "contact_units",
                "future_V_materialization",
                "future_V_shape_order",
                "profile_flat_index",
                "profile_order",
                "profile_units",
            ],
            "values": {
                "contact_flat_index": "a*n_Y+b",
                "contact_units": "dimensionless",
                "future_V_materialization": "forbidden",
                "future_V_shape_order": ["n_M", "n_R", "n_Y"],
                "profile_flat_index": "m",
                "profile_order": [0, 1, 2, 3],
                "profile_units": "inverse_length",
            },
        },
        "method_bindings": {
            "exact_keys": [
                "analytic_area",
                "contact_and_profile_producer",
                "exact_contact_classifier",
                "independent_same_backend_verifier",
            ],
            "value_schema": "method_record_binding",
        },
        "method_record_binding": {
            "exact_keys": [
                "method_parameter_sha256",
                "parameter_id",
                "registry_sha256",
            ],
            "types": {
                "method_parameter_sha256": "lowercase_sha256",
                "parameter_id": "exact_registry_v4_parameter_id",
                "registry_sha256": "lowercase_sha256",
            },
        },
        "model_section_binding": {
            "exact_keys": [
                "json_pointer",
                "model_path",
                "model_schema",
                "model_sha256",
                "section_sha256",
            ],
            "types": {
                "json_pointer": "exact_frozen_JSON_pointer",
                "model_path": "canonical_absolute_path",
                "model_schema": SCHEMA,
                "model_sha256": "lowercase_sha256_equal_operation_model_binding",
                "section_sha256": (
                    "sha256_of_canonical_section_value_bytes_without_self_reference"
                ),
            },
        },
        "normalization_anchor": {
            "exact_keys": [
                "analytic_area_enclosure_exact",
                "formula",
                "precision_bits",
                "radius_exact",
            ],
            "fields": {
                "analytic_area_enclosure_exact": "exact_rational_interval",
                "formula": "literal_pi_times_radius_squared",
                "precision_bits": "literal_256",
                "radius_exact": "positive_exact_rational_string",
            },
        },
        "partition_binding": {
            "exact_keys": [
                "axis_cell_count",
                "axis_name",
                "coordinate_order_digest",
                "path",
                "schema",
                "sha256",
            ],
            "types": {
                "axis_cell_count": "positive_integer",
                "axis_name": "one_of_midpoint_relative_parallel_relative_perpendicular",
                "coordinate_order_digest": "lowercase_sha256",
                "path": "canonical_report_relative_path",
                "schema": "exact_member_v4_partition_schema",
                "sha256": "lowercase_sha256",
            },
        },
        "partition_bindings": {
            "exact_keys": [
                "midpoint",
                "relative_parallel",
                "relative_perpendicular",
            ],
            "value_schema": "partition_binding",
        },
        "profile_classification_ledger": {
            "exact_keys": ["global_digest", "profiles", "record_count"],
            "cardinality": {"profiles": 48, "record_count": 6852},
            "fields": {
                "global_digest": "lowercase_sha256",
                "profiles": "ordered_profile_classification_array",
                "record_count": "literal_6852",
            },
        },
        "profile_classification_row": {
            "exact_keys": [
                "configuration_index",
                "digest",
                "outside_support",
                "profile_index",
                "record_count",
                "support",
            ],
            "types": {
                "configuration_index": "integer_0_through_11",
                "digest": "lowercase_sha256",
                "outside_support": "nonnegative_integer",
                "profile_index": "integer_0_through_3",
                "record_count": "positive_integer",
                "support": "nonnegative_integer",
            },
            "join": "outside_support_plus_support_equals_record_count",
        },
        "profile_section": {
            "exact_keys": [
                "centre_exact",
                "flat_index",
                "half_width_exact",
                "logical_shape",
                "profile_index",
                "producer_classification_summary",
                "quality_gate_ledger",
                "raw_manifest",
                "record_count",
                "units",
                "weighted_unit_mass_enclosure_exact",
            ],
            "fields": {
                "centre_exact": "exact_rational_string",
                "flat_index": "literal_m",
                "half_width_exact": "positive_exact_rational_string",
                "logical_shape": "one_positive_integer_array",
                "profile_index": "integer_0_through_3",
                "producer_classification_summary": ("producer_profile_classification_summary"),
                "quality_gate_ledger": "quality_gate_ledger",
                "raw_manifest": "raw_manifest",
                "record_count": "positive_integer",
                "units": "literal_inverse_length",
                "weighted_unit_mass_enclosure_exact": "exact_rational_interval",
            },
        },
        "producer_classification_metadata": {
            "exact_keys": ["contact", "profiles", "schema", "status"],
            "fields": {
                "contact": "producer_contact_classification_summary",
                "profiles": ("exactly_four_producer_profile_classification_summaries_in_order"),
                "schema": "encounter_role10_producer_classification_metadata_v1",
                "status": "PRODUCER_CLASSIFICATION_MATERIALIZED_PENDING_INDEPENDENT_CHECK",
            },
        },
        "producer_contact_classification_summary": {
            "exact_keys": ["digest", "full", "partial", "record_count", "zero"],
            "types": {
                "digest": "lowercase_sha256_under_contact_classification_contract",
                "full": "nonnegative_integer",
                "partial": "nonnegative_integer",
                "record_count": "positive_integer",
                "zero": "nonnegative_integer",
            },
            "join": "zero_plus_full_plus_partial_equals_record_count",
        },
        "producer_profile_classification_summary": {
            "exact_keys": [
                "digest",
                "outside_support",
                "profile_index",
                "record_count",
                "support",
            ],
            "types": {
                "digest": "lowercase_sha256_under_profile_classification_contract",
                "outside_support": "nonnegative_integer",
                "profile_index": "integer_0_through_3",
                "record_count": "positive_integer",
                "support": "nonnegative_integer",
            },
            "join": "outside_support_plus_support_equals_record_count",
        },
        "precision_coverage": {
            "exact_keys": [
                "analytic_area_saved_bits",
                "producer_contact_bits",
                "producer_profile_bits",
                "verifier_primary_bits",
                "verifier_sentinel_bits",
            ],
            "values": {
                "analytic_area_saved_bits": 256,
                "producer_contact_bits": 192,
                "producer_profile_bits": 192,
                "verifier_primary_bits": 384,
                "verifier_sentinel_bits": 512,
            },
        },
        "promotion_claims": {
            "exact_keys": list(promotion_claims()),
            "types": "JSON_boolean_only",
            "values": "all_exactly_false",
        },
        "quality_gate_ledger": {
            "exact_keys": ["gate_ids", "observations", "passed"],
            "fields": {
                "gate_ids": ("parent_specific_exact_ordered_subset_of_wire_quality_gate_sets"),
                "observations": ("exact_same_keys_as_gate_ids_each_value_quality_gate_observation"),
                "passed": "literal_true",
            },
        },
        "quality_gate_observation": {
            "exact_keys": ["bound_exact", "observed_upper_exact", "passed"],
            "types": {
                "bound_exact": "positive_exact_rational_string",
                "observed_upper_exact": "nonnegative_exact_rational_string",
                "passed": "literal_true",
            },
            "join": "observed_upper_exact_less_than_or_equal_to_bound_exact",
        },
        "representation_contract": {
            "exact_keys": [
                "byte_order",
                "endpoint_semantics",
                "record_format",
                "shape_order",
                "stored_profile_quantity",
                "W_inverse_in_contact",
                "W_inverse_in_profile",
            ],
            "values": {
                "byte_order": "big",
                "endpoint_semantics": "closed_outward_binary64",
                "record_format": ">dd",
                "shape_order": ["n_M", "n_R", "n_Y"],
                "stored_profile_quantity": "cell_average_density_not_cell_mass",
                "W_inverse_in_contact": "forbidden",
                "W_inverse_in_profile": "forbidden",
            },
        },
        "raw_manifest": {
            "exact_keys": [
                "byte_length",
                "byte_order",
                "endpoint_semantics",
                "flat_index",
                "logical_role",
                "logical_shape",
                "normalization",
                "path",
                "record_count",
                "record_format",
                "schema",
                "sha256",
                "units",
            ],
            "types": {
                "byte_length": "positive_integer_equal_record_count_times_16",
                "byte_order": "literal_big",
                "endpoint_semantics": "literal_closed_outward_binary64",
                "flat_index": "literal_a*n_Y+b_or_m",
                "logical_role": "literal_contact_or_profile_0_1_2_3",
                "logical_shape": "positive_integer_array_matching_parent",
                "normalization": "exact_frozen_contact_or_profile_normalization_string",
                "path": "canonical_report_relative_raw_leaf_path",
                "record_count": "positive_integer",
                "record_format": "literal_>dd",
                "schema": RAW_SCHEMA,
                "sha256": "lowercase_sha256",
                "units": "literal_dimensionless_or_inverse_length",
            },
        },
        "run_observation": {
            "exact_keys": [
                "ack_sha256",
                "darwin_cf_user_text_encoding_observation",
                "ended_monotonic_ns",
                "pgid",
                "pid",
                "returncode",
                "run_ordinal",
                "started_monotonic_ns",
                "stderr_sha256",
            ],
            "types": {
                "ack_sha256": "lowercase_sha256",
                "darwin_cf_user_text_encoding_observation": (
                    "/wire_schema_contract/scalar_encodings/null_or_validated_Darwin_string"
                ),
                "ended_monotonic_ns": "nonnegative_integer",
                "pgid": "positive_integer_equal_pid",
                "pid": "positive_integer",
                "returncode": "literal_0",
                "run_ordinal": ("integer_0_for_producer_or_1_2_for_the_two_semantic_children"),
                "started_monotonic_ns": "nonnegative_integer_less_than_or_equal_to_end",
                "stderr_sha256": "sha256_of_empty_bytes",
            },
        },
        "runtime_closure_bindings": {
            "exact_keys": ["producer", "verifier"],
            "value_schema": "schema_pin",
            "join": "pins_equal_the_role10_runtime_closure_entrypoint_subclosures",
        },
        "schema_pin": {
            "exact_keys": ["path", "schema", "sha256"],
            "types": {
                "path": "canonical_absolute_or_report_relative_path_as_parent_requires",
                "schema": "exact_schema_string",
                "sha256": "lowercase_sha256",
            },
        },
        "transaction_evidence_prepublication": {
            "exact_keys": [
                "atomic_no_replace_primitive",
                "output_parent_identity",
                "preflight_fresh_slots",
                "staged_identity_ledger_sha256",
                "write_ahead_journal_sha256",
            ],
            "fields": {
                "atomic_no_replace_primitive": "literal_renameat2_or_renameatx_np",
                "output_parent_identity": "/wire_schema_contract/objects/dev_ino_pair",
                "preflight_fresh_slots": "exact_three_role10_output_slot_ids",
                "staged_identity_ledger_sha256": (
                    "lowercase_sha256_under_publication_contract_staged_identity_ledger_digest"
                ),
                "write_ahead_journal_sha256": (
                    "lowercase_sha256_of_the_exact_canonical_durable_journal_snapshot_"
                    "whose_state_is_ABOUT_TO_INSTALL_OUTER_RECEIPT"
                ),
            },
            "forbidden_post_install_claims": [
                "outer_receipt_installed",
                "transaction_committed",
                "journal_removed",
            ],
        },
        "totals": {
            "exact_keys": [
                "configuration_rows",
                "contact_interval_bytes",
                "contact_interval_records",
                "directories",
                "files",
                "profile_files",
                "profile_interval_bytes",
                "profile_interval_records",
                "raw_numerical_leaves",
                "row_manifests",
                "top_manifests",
            ],
            "values": {
                "configuration_rows": 12,
                "contact_interval_bytes": 3730224,
                "contact_interval_records": 233139,
                "directories": 14,
                "files": 73,
                "profile_files": 48,
                "profile_interval_bytes": 109632,
                "profile_interval_records": 6852,
                "raw_numerical_leaves": 60,
                "row_manifests": 12,
                "top_manifests": 1,
            },
        },
        "tree_stability_evidence": {
            "exact_keys": [
                "after_child_0_tree_sha256",
                "after_child_1_tree_sha256",
                "before_children_tree_sha256",
                "stable",
            ],
            "types": {
                "after_child_0_tree_sha256": (
                    "/process_contract/digest_contracts/staged_artifact_binding_sha256"
                ),
                "after_child_1_tree_sha256": (
                    "/process_contract/digest_contracts/staged_artifact_binding_sha256"
                ),
                "before_children_tree_sha256": (
                    "/process_contract/digest_contracts/staged_artifact_binding_sha256"
                ),
                "stable": "literal_true",
            },
            "join": "all_three_tree_sha256_values_are_identical",
        },
        "verification_counts": {
            "exact_keys": [
                "contact_full",
                "contact_partial_primary",
                "contact_partial_sentinel",
                "contact_total_classified",
                "contact_zero",
                "profile_aggregates_primary_and_sentinel",
                "profile_cells_primary_and_sentinel",
                "profile_total_support_classified",
            ],
            "values": {
                "contact_full": 4142,
                "contact_partial_primary": 1304,
                "contact_partial_sentinel": 12,
                "contact_total_classified": 233139,
                "contact_zero": 227693,
                "profile_aggregates_primary_and_sentinel": 48,
                "profile_cells_primary_and_sentinel": 6852,
                "profile_total_support_classified": 6852,
            },
        },
    }


def relation_digest_contracts() -> dict[str, Any]:
    return {
        "family_relation_digest": {
            "domain": "encounter-role10-family-relation-v2",
            "preimage": (
                "domain_ascii+NUL+uint64be_12_then_for_each_configuration_in_index_"
                "order_uint64be_32_plus_raw_32_byte_row_relation_digest"
            ),
        },
        "file_inventory_tree_sha256": {
            "domain": "encounter-role10-file-inventory-v2",
            "preimage": (
                "domain_ascii+NUL+uint64be_72_then_for_each_frozen_order_entry_"
                "uint64be_path_length+path_utf8+uint64be_byte_length+raw_32_byte_sha256"
            ),
        },
        "partition_reference_digest": {
            "domain": "encounter-role10-partition-reference-v2",
            "preimage": (
                "domain_ascii+NUL+uint64be_36_then_ordered_configuration_and_axis_"
                "records_each_with_uint64be_length_prefixed_canonical_binding_bytes"
            ),
        },
        "row_relation_digest": {
            "domain": "encounter-role10-row-relation-v2",
            "preimage": (
                "domain_ascii+NUL+uint16be_configuration_index+for_each_axis_in_"
                "midpoint_relative_parallel_relative_perpendicular_order_uint64be_"
                "canonical_binding_length+canonical_binding_bytes"
            ),
        },
    }


def wire_schema_contract() -> dict[str, Any]:
    row_payload = [
        "authority_bindings",
        "configuration_binding",
        "contact",
        "expected_states",
        "layout_and_units",
        "lifecycle_observations",
        "member_binding",
        "partition_bindings",
        "producer_closure_binding",
        "producer_classification_metadata",
        "profiles",
        "promotion_claims",
        "request_binding",
        "row_relation_digest",
        "shape",
    ]
    source_payload = [
        "authority_bindings",
        "candidate_bundle_binding",
        "classification_contract_binding",
        "external_commitment_binding",
        "family_relation_digest",
        "file_inventory",
        "lifecycle_observations",
        "member_binding",
        "method_selection",
        "normalization_anchor",
        "operation_model_binding",
        "partition_reference_digest",
        "producer_runtime_closure",
        "promotion_claims",
        "replay_plan_binding",
        "representation_contract",
        "request_binding",
        "rows",
        "sealed_authentication_mirror_binding",
        "shared_precommit_context_sha256",
        "totals",
        "transaction_recovery_policy_binding",
    ]
    semantic_payload = [
        "artifact_binding",
        "authority_bindings",
        "classification_ledger",
        "containment_ledger",
        "lifecycle_observations",
        "method_bindings",
        "precision_coverage",
        "promotion_claims",
        "request_binding",
        "runtime_closure_bindings",
        "tree_inventory_sha256",
        "verification_counts",
    ]
    outer_payload = [
        "artifact_binding",
        "authority_bindings",
        "canonical_semantic_receipt_binding",
        "cleanup_evidence",
        "lifecycle_observations",
        "method_bindings",
        "producer_runtime_closure_binding",
        "promotion_claims",
        "request_binding",
        "run_observations",
        "transaction_evidence",
        "tree_stability_evidence",
        "verifier_runtime_closure_binding",
    ]
    return {
        "binary_interval_rules": {
            "byte_length_join": "raw_file_byte_length_equals_record_count_times_16",
            "contact_range": "positive_zero_le_lower_le_upper_le_one",
            "endpoint_rules": "finite_not_nan_not_infinite_and_lower_less_than_or_equal_to_upper",
            "exact_full": "bit_exact_[1.0,1.0]",
            "exact_zero": "bit_exact_[positive_zero,positive_zero]",
            "file_rules": "regular_single_link_exact_length_no_trailing_bytes_sha256_join",
            "negative_zero_bit_pattern": "forbidden_for_every_endpoint",
            "profile_range": "positive_zero_le_lower_le_upper",
            "record_byte_length": 16,
            "record_format": ">dd",
        },
        "binding_targets": {
            "analytic_area_anchor_reference": (
                "same_package_manifest_payload_normalization_anchor_by_acyclic_"
                "package_section_binding"
            ),
            "candidate_bundle_binding": (
                "encounter_continuum_c1_n0_precommit_candidate_bundle_v2_absolute_file"
            ),
            "classification_contract_binding": ("this_operation_model_v2_/classification_contract"),
            "external_commitment_binding": (
                "encounter_external_predecessor_commitment_v1_absolute_file"
            ),
            "member_binding": (
                "encounter_continuum_c1_c2_n0_member_spec_v4_candidate_absolute_file"
            ),
            "operation_model_binding": f"{SCHEMA}_absolute_file",
            "producer_runtime_closure": (
                f"{RUNTIME_SCHEMA}_role10_producer_subclosure_absolute_file"
            ),
            "producer_closure_binding": (
                f"{RUNTIME_SCHEMA}_role10_producer_subclosure_absolute_file"
            ),
            "replay_plan_binding": f"{PLAN_SCHEMA}_absolute_file",
            "request_binding": f"{ROLE10_REQUEST_SCHEMA}_absolute_file",
            "sealed_authentication_mirror_binding": (
                "encounter_continuum_c1_n0_role10_sealed_authentication_mirror_"
                "v1_candidate_absolute_directory_manifest"
            ),
            "transaction_recovery_policy_binding": (
                "this_operation_model_v2_/publication_contract_not_the_transient_journal"
            ),
            "verifier_runtime_closure_binding": (
                f"{RUNTIME_SCHEMA}_role10_verifier_subclosure_absolute_file"
            ),
        },
        "digest_framing": {
            "canonical_json": "ASCII_sort_keys_indent_2_trailing_newline",
            "envelope_payload_rule": "domain_ascii+NUL+canonical_payload_bytes",
            "relation_component_length_encoding": "unsigned_uint64_big_endian",
            "whole_file_rule": (
                "sha256_of_canonical_complete_envelope_bytes_separate_from_payload_digest"
            ),
        },
        "envelopes": {
            "outer_receipt": envelope_contract(
                schema=OUTER_RECEIPT_SCHEMA,
                status="ROLE10_OUTER_VALIDATION_PASSED_NO_SAME_MEMBER_PROMOTION",
                digest_domain="encounter-role10-outer-receipt-v3",
                payload_exact_keys=outer_payload,
            ),
            "row": envelope_contract(
                schema=ROW_SCHEMA,
                status="ROLE10_ROW_MATERIALIZED_PENDING_INDEPENDENT_VALIDATION",
                digest_domain="encounter-role10-killing-row-v2",
                payload_exact_keys=row_payload,
            ),
            "semantic_receipt": envelope_contract(
                schema=SEMANTIC_RECEIPT_SCHEMA,
                status="ROLE10_ONE_CLEAN_CHILD_SEMANTIC_VALIDATION_PASSED_NO_PROMOTION",
                digest_domain="encounter-role10-semantic-receipt-v2",
                payload_exact_keys=semantic_payload,
            ),
            "source": envelope_contract(
                schema=SOURCE_SCHEMA,
                status="ROLE10_NUMERICAL_SOURCE_MATERIALIZED_PENDING_INDEPENDENT_VALIDATION",
                digest_domain="encounter-role10-killing-source-v4",
                payload_exact_keys=source_payload,
            ),
        },
        "objects": {
            **closed_object_schemas(),
            "raw_manifest": {
                **closed_object_schemas()["raw_manifest"],
                "schema": RAW_SCHEMA,
                "semantic_role": (
                    "canonical_JSON_metadata_object_inside_a_row_payload_describing_one_"
                    "separate_binary_interval_leaf_not_an_envelope_around_the_binary_bytes"
                ),
            },
        },
        "payload_field_schemas": {
            "outer_receipt": {
                "artifact_binding": "artifact_binding",
                "authority_bindings": "authority_bindings",
                "canonical_semantic_receipt_binding": "schema_pin",
                "cleanup_evidence": "cleanup_evidence",
                "lifecycle_observations": {
                    "object_schema": "/wire_schema_contract/objects/lifecycle_observations",
                    "value_constraint": ("/wire_schema_contract/lifecycle_maps/outer_receipt"),
                },
                "method_bindings": "method_bindings",
                "producer_runtime_closure_binding": "schema_pin",
                "promotion_claims": "promotion_claims",
                "request_binding": "schema_pin",
                "run_observations": (
                    "exactly_three_ordered_run_observation_objects_for_producer_then_"
                    "semantic_child_0_then_semantic_child_1"
                ),
                "transaction_evidence": "transaction_evidence_prepublication",
                "tree_stability_evidence": "tree_stability_evidence",
                "verifier_runtime_closure_binding": "schema_pin",
            },
            "row": {
                "authority_bindings": "authority_bindings",
                "configuration_binding": "configuration_binding",
                "contact": "contact_section",
                "expected_states": "positive_integer_equal_product_of_shape",
                "layout_and_units": "layout_and_units",
                "lifecycle_observations": {
                    "object_schema": "/wire_schema_contract/objects/lifecycle_observations",
                    "value_constraint": ("/wire_schema_contract/lifecycle_maps/source_and_rows"),
                },
                "member_binding": "schema_pin",
                "partition_bindings": "partition_bindings",
                "producer_closure_binding": "schema_pin",
                "producer_classification_metadata": ("producer_classification_metadata"),
                "profiles": "exactly_four_profile_section_objects_in_index_order",
                "promotion_claims": "promotion_claims",
                "request_binding": "schema_pin",
                "row_relation_digest": "lowercase_sha256_under_row_relation_contract",
                "shape": "exact_three_positive_integer_array_n_M_n_R_n_Y",
            },
            "semantic_receipt": {
                "artifact_binding": "artifact_binding",
                "authority_bindings": "authority_bindings",
                "classification_ledger": "classification_ledger",
                "containment_ledger": "containment_ledger",
                "lifecycle_observations": {
                    "object_schema": "/wire_schema_contract/objects/lifecycle_observations",
                    "value_constraint": ("/wire_schema_contract/lifecycle_maps/semantic_receipt"),
                },
                "method_bindings": "method_bindings",
                "precision_coverage": "precision_coverage",
                "promotion_claims": "promotion_claims",
                "request_binding": "schema_pin",
                "runtime_closure_bindings": "runtime_closure_bindings",
                "tree_inventory_sha256": "lowercase_sha256",
                "verification_counts": "verification_counts",
            },
            "source": {
                "authority_bindings": "authority_bindings",
                "candidate_bundle_binding": "schema_pin",
                "classification_contract_binding": {
                    "json_pointer": "/classification_contract",
                    "object_schema": ("/wire_schema_contract/objects/model_section_binding"),
                    "target_constraint": (
                        "/wire_schema_contract/binding_targets/classification_contract_binding"
                    ),
                },
                "external_commitment_binding": "schema_pin",
                "family_relation_digest": "lowercase_sha256_under_family_relation_contract",
                "file_inventory": "file_inventory",
                "lifecycle_observations": {
                    "object_schema": "/wire_schema_contract/objects/lifecycle_observations",
                    "value_constraint": ("/wire_schema_contract/lifecycle_maps/source_and_rows"),
                },
                "member_binding": "schema_pin",
                "method_selection": "method_bindings",
                "normalization_anchor": "normalization_anchor",
                "operation_model_binding": "schema_pin",
                "partition_reference_digest": (
                    "lowercase_sha256_under_partition_reference_contract"
                ),
                "producer_runtime_closure": "schema_pin",
                "promotion_claims": "promotion_claims",
                "replay_plan_binding": "schema_pin",
                "representation_contract": "representation_contract",
                "request_binding": "schema_pin",
                "rows": "exactly_twelve_ordered_schema_pin_objects",
                "sealed_authentication_mirror_binding": "schema_pin",
                "shared_precommit_context_sha256": "lowercase_sha256",
                "totals": "totals",
                "transaction_recovery_policy_binding": {
                    "json_pointer": "/publication_contract",
                    "object_schema": ("/wire_schema_contract/objects/model_section_binding"),
                    "target_constraint": (
                        "/wire_schema_contract/binding_targets/transaction_recovery_policy_binding"
                    ),
                },
            },
        },
        "quality_gate_sets": {
            "contact_producer": [
                "contact_area_relative_width_over_radius_squared",
                "published_contact_interval_width",
            ],
            "global_analytic_area": ["analytic_area_relative_width"],
            "profile_producer": [
                "profile_integral_relative_width",
                "profile_cell_mass_width",
            ],
            "semantic_verifier": [
                "contact_oracle_relative_width",
                "contact_oracle_to_nonzero_producer_width_ratio",
                "profile_oracle_to_nonzero_producer_cell_mass_width_ratio",
                "aggregate_profile_mass_relative_width",
            ],
        },
        "relation_digests": relation_digest_contracts(),
        "scalar_encodings": {
            "exact_rational_interval": {
                "exact_keys": ["lower_exact", "upper_exact"],
                "join": "parsed_lower_less_than_or_equal_to_parsed_upper",
                "value_type": "exact_rational_string",
            },
            "exact_rational_string": {
                "canonical_grammar": "^-?(0|[1-9][0-9]*)/[1-9][0-9]*$",
                "normalization": (
                    "denominator_positive_gcd_absolute_numerator_denominator_equals_1_"
                    "and_zero_is_exactly_0/1"
                ),
            },
            "nonnegative_exact_rational_string": (
                "exact_rational_string_whose_parsed_value_is_greater_than_or_equal_to_zero"
            ),
            "null_or_validated_Darwin_string": {
                "allowed_values": [
                    "JSON_null",
                    "ASCII_string_matching_exactly_the_canonical_grammar",
                ],
                "canonical_grammar": ("^0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+$"),
                "platform_join": (
                    "must_be_JSON_null_off_Darwin_and_on_Darwin_is_null_only_when_the_"
                    "OS_did_not_add___CF_USER_TEXT_ENCODING_otherwise_the_exact_"
                    "observed_string"
                ),
            },
            "positive_exact_rational_string": (
                "exact_rational_string_whose_parsed_value_is_strictly_greater_than_zero"
            ),
        },
        "join_rules": {
            "authority_and_lifecycle": [
                "every_binding_has_exact_path_schema_sha256_and_matches_the_request",
                "source_and_row_lifecycle_observations_equal_the_source_observation_map",
                "receipt_lifecycle_observations_equal_their_stage_specific_observation_map",
                "every_promotion_claim_map_equals_the_frozen_all_false_map",
            ],
            "file_inventory": [
                "top_inventory_has_exactly_72_nonself_entries_in_frozen_order",
                "every_row_manifest_and_raw_leaf_path_hash_byte_length_and_mode_join_exactly",
                "no_unlisted_file_directory_symlink_or_hardlink",
            ],
            "partition": [
                "each_row_binds_exactly_midpoint_relative_parallel_relative_perpendicular",
                "partition_path_sha256_axis_name_coordinate_order_and_cell_count_join_member_v4",
                "row_shape_equals_ordered_n_M_n_R_n_Y_partition_cell_counts",
                "row_relation_digest_is_length_framed_over_configuration_and_three_partition_bindings",
                "family_relation_digest_is_length_framed_over_the_twelve_ordered_row_relation_digests",
            ],
            "raw": [
                "raw_manifest_path_role_shape_flat_index_units_normalization_count_length_sha256_join",
                "contact_has_one_file_and_profiles_have_exactly_four_files_in_order_0_1_2_3",
                "all_binary_records_pass_the_frozen_endpoint_and_range_rules",
            ],
        },
        "lifecycle_maps": {
            "outer_receipt": lifecycle_observations(child=False, matched_children=True, outer=True),
            "promotion_claims": promotion_claims(),
            "semantic_receipt": lifecycle_observations(
                child=True, matched_children=False, outer=False
            ),
            "source_and_rows": lifecycle_observations(
                child=False, matched_children=False, outer=False
            ),
        },
        "type_rules": {
            "booleans": "JSON_boolean_only_not_integer",
            "counts_and_ordinals": "JSON_integer_only_nonnegative_and_bounded",
            "digests": "lowercase_64_hex",
            "paths": "canonical_POSIX_absolute_or_report_relative_as_field_requires_no_dotdot_no_backslash",
            "strings": "ASCII_nonempty_unless_field_explicitly_allows_empty",
        },
    }


def classification_contract() -> dict[str, Any]:
    return {
        "contact": {
            "cell_rule": {
                "full_predicate": (
                    "after_zero_is_false_every_positive_area_exact_wrapped_segment_"
                    "pair_has_all_four_corner_squared_distances_less_than_or_equal_to_"
                    "radius_squared"
                ),
                "partial_predicate": "zero_is_false_and_full_is_false",
                "precedence": ["zero", "full", "partial"],
                "zero_predicate": (
                    "every_positive_area_exact_wrapped_segment_pair_has_nearest_"
                    "squared_distance_greater_than_or_equal_to_radius_squared"
                ),
                "zero_measure_equality": "tangency_is_zero_and_zero_precedence_wins",
            },
            "classification_digest": {
                "domain": "encounter-role10-contact-classification-v2",
                "global_preimage": (
                    "domain_ascii+NUL+uint64be_233139_then_for_rows_0_through_11_"
                    "and_flat_indices_in_ascending_order_uint16be_row_index+uint64be_"
                    "flat_index+uint8_label"
                ),
                "label_bytes": {
                    "full": "0x01",
                    "partial": "0x02",
                    "zero": "0x00",
                },
                "per_row_preimage": (
                    "domain_ascii+NUL+uint16be_row_index+uint64be_row_record_count+"
                    "ascending_uint64be_flat_index+uint8_label_records"
                ),
                "recorded_in_each_clean_child_receipt": True,
            },
            "global_counts": {
                "full": 4142,
                "partial": 1304,
                "total": 233139,
                "zero": 227693,
            },
            "independent_verifier_scope": "classify_all_233139_cells_without_branching_on_candidate_values",
            "ledger_schema": {
                "object_schema": ("/wire_schema_contract/objects/contact_classification_ledger")
            },
            "per_row_ledger": {
                "cardinality": 12,
                "object_schema": ("/wire_schema_contract/objects/contact_row_classification"),
                "order": "ascending_configuration_index_0_through_11",
                "receipt_join": (
                    "recorded_in_each_clean_child_receipt_and_byte_identical_before_outer_receipt"
                ),
            },
            "serialization": {
                "full": "bit_exact_[1.0,1.0]",
                "negative_zero": "forbidden",
                "partial": "finite_0_le_lower_le_upper_le_1_and_not_exact_zero_or_full",
                "zero": "bit_exact_[positive_zero,positive_zero]",
            },
        },
        "profile": {
            "cell_rule": {
                "outside_support_predicate": (
                    "for_exact_cell_[lower,upper]_and_exact_open_positive_support_"
                    "(centre-half_width,centre+half_width)_outside_support_iff_"
                    "upper_less_than_or_equal_to_centre_minus_half_width_or_lower_"
                    "greater_than_or_equal_to_centre_plus_half_width"
                ),
                "support_predicate": "logical_negation_of_outside_support_predicate",
                "zero_measure_equality": (
                    "cell_support_boundary_tangency_has_zero_integral_and_is_outside_support"
                ),
            },
            "classification_digest": {
                "domain": "encounter-role10-profile-support-classification-v2",
                "global_preimage": (
                    "domain_ascii+NUL+uint64be_6852_then_rows_0_through_11_profiles_"
                    "0_through_3_and_cell_indices_in_ascending_order_uint16be_row+"
                    "uint8_profile+uint64be_cell_index+uint8_label"
                ),
                "label_bytes": {"outside_support": "0x00", "support": "0x01"},
                "per_profile_preimage": (
                    "domain_ascii+NUL+uint16be_row+uint8_profile+uint64be_record_count+"
                    "ascending_uint64be_cell_index+uint8_label_records"
                ),
                "recorded_in_each_clean_child_receipt": True,
            },
            "independent_verifier_scope": "classify_all_6852_cells_from_exact_support_and_partition_coordinates",
            "outside_support": "bit_exact_[positive_zero,positive_zero]_and_negative_zero_forbidden",
            "ledger_schema": {
                "object_schema": ("/wire_schema_contract/objects/profile_classification_ledger")
            },
            "per_row_profile_ledger": {
                "cardinality": 48,
                "object_schema": ("/wire_schema_contract/objects/profile_classification_row"),
                "order": ("ascending_configuration_index_then_profile_index_0_through_3"),
                "receipt_join": (
                    "recorded_in_each_clean_child_receipt_and_byte_identical_before_outer_receipt"
                ),
            },
            "support": "finite_nonnegative_density_interval_with_paired_384_512_containment",
        },
        "two_child_equality": (
            "the_two_clean_children_must_emit_byte_identical_classification_ledgers_"
            "and_semantic_receipt_payloads"
        ),
    }


def replay_plan_contract() -> dict[str, Any]:
    slot_rows = [
        (0, "role8_request", 8, "request", "file", ROLE8_REQUEST_SCHEMA),
        (
            1,
            "role8_artifact",
            8,
            "artifact",
            "file",
            "encounter_c1_n0_raw_axis_formula_primitive_source_v2",
        ),
        (
            2,
            "role8_validation_receipt",
            8,
            "validation_receipt",
            "file",
            "encounter_c1_n0_raw_axis_formula_primitive_validation_receipt_v1",
        ),
        (
            3,
            "role9_request",
            9,
            "request",
            "file",
            ROLE9_REQUEST_SCHEMA,
        ),
        (
            4,
            "role9_artifact",
            9,
            "artifact",
            "file",
            "encounter_c1_n0_stationary_physical_integral_source_v2",
        ),
        (
            5,
            "role9_validation_receipt",
            9,
            "validation_receipt",
            "file",
            "encounter_c1_n0_stationary_physical_integral_validation_receipt_v1",
        ),
        (6, "role10_request", 10, "request", "file", ROLE10_REQUEST_SCHEMA),
        (7, "role10_artifact_directory", 10, "artifact", "directory", SOURCE_SCHEMA),
        (
            8,
            "role10_semantic_receipt",
            10,
            "semantic_receipt",
            "file",
            SEMANTIC_RECEIPT_SCHEMA,
        ),
        (
            9,
            "role10_outer_validation_receipt",
            10,
            "outer_validation_receipt",
            "file",
            OUTER_RECEIPT_SCHEMA,
        ),
    ]
    slots = [
        {
            "kind": kind,
            "lifecycle": (
                "future_request_after_commitment_then_immutable_input"
                if kind == "request"
                else "must_be_absent_before_global_launch_atomic_no_replace_output"
            ),
            "node_type": node_type,
            "ordinal": ordinal,
            "path_field": "actual_canonical_absolute_path_in_the_materialized_plan",
            "role": role,
            "schema": schema,
            "slot_id": slot_id,
        }
        for ordinal, slot_id, role, kind, node_type, schema in slot_rows
    ]
    return {
        "acyclic_materialization_contract": {
            "forbidden_back_edges": [
                "operation_model_to_runtime_closure_hash",
                "operation_model_to_plan_hash",
                "operation_model_to_bundle_hash",
                "runtime_closure_to_plan_or_bundle_hash",
                "plan_to_bundle_commitment_request_or_output_hash",
                "bundle_to_commitment_request_or_output_hash",
                "commitment_to_request_or_output_hash",
                "request_to_any_output_hash",
                "artifact_or_semantic_receipt_to_outer_receipt_hash",
                "row_to_complete_top_manifest_hash",
            ],
            "hash_dependency_order": [
                "operation_model_v2",
                "future_role_v3_and_global_runner_v2_entrypoints_and_transitive_runtime_sources",
                "shared_runtime_closure_v1",
                "replay_plan_v2",
                "precommit_candidate_bundle_v2",
                "external_predecessor_commitment_v1",
                "three_request_v4_files",
                "role_output_artifacts",
                "role10_semantic_receipt_v2",
                "role10_outer_receipt_v3",
            ],
            "plan_slot_rule": (
                "the_plan_serializes_all_ten_future_absolute_paths_but_no_request_or_"
                "output_content_hash"
            ),
            "role10_package_rule": (
                "rows_bind_only_the_top_normalization_anchor_section_sha256_top_"
                "inventory_excludes_its_own_manifest_semantic_receipt_binds_artifact_"
                "outer_receipt_binds_artifact_and_semantic_receipt"
            ),
        },
        "canonical_digest_framing": {
            "canonical_JSON": "ASCII_sort_keys_indent_2_one_trailing_LF",
            "entry_projection": (
                "domain_encounter-role-replay-entry-v2+NUL+uint64be_byte_length+"
                "canonical_entry_with_only_precommit_projection_sha256_omitted"
            ),
            "process_contract_section_sha256": (
                "sha256_of_raw_canonical_process_contract_section_bytes_with_no_domain_"
                "or_length_prefix"
            ),
            "shared_precommit_context": (
                "domain_encounter-shared-precommit-context-v2+NUL+canonical_shared_"
                "context_bytes_with_no_length_prefix"
            ),
            "shared_replay_context": (
                "domain_encounter-continuum-c1-n0-shared-replay-context-v2+NUL+"
                "canonical_three_key_preimage_bytes_with_no_length_prefix"
            ),
        },
        "objects": {
            "invocation": {
                "exact_keys": [
                    "argv",
                    "invocation_id",
                    "process_contract_sha256",
                ],
                "field_schemas": {
                    "argv": (
                        "exact_role_and_caller_specific_ASCII_argv_array_after_runtime_"
                        "and_slot_substitution"
                    ),
                    "invocation_id": "exact_role_and_caller_specific_v3_literal",
                    "process_contract_sha256": (
                        "lowercase_sha256_under_canonical_digest_framing_process_rule"
                    ),
                },
            },
            "replay_partition_binding": {
                "exact_keys": [
                    "configuration_index",
                    "coordinate",
                    "member_report_relative_path",
                    "path",
                    "sha256",
                ],
                "field_schemas": {
                    "configuration_index": "JSON_integer_0_through_11",
                    "coordinate": (
                        "literal_midpoint_or_relative_parallel_or_relative_perpendicular"
                    ),
                    "member_report_relative_path": (
                        "canonical_report_relative_path_equal_member_v4_axis_path"
                    ),
                    "path": ("canonical_absolute_regular_file_path_with_report_relative_suffix"),
                    "sha256": ("lowercase_sha256_equal_member_v4_axis_sha256_and_opened_bytes"),
                },
                "member_join": (
                    "for_ordinal_0_through_35_configuration_index_equals_ordinal_div_3_"
                    "coordinate_equals_[midpoint,relative_parallel,relative_"
                    "perpendicular][ordinal_mod_3]_and_all_path_sha256_values_equal_"
                    "the_corresponding_member_v4_n0_axis_the_opened_partition_schema_"
                    "must_equal_that_axis_partition_schema_without_serializing_a_"
                    "redundant_schema_field"
                ),
            },
            "request_role": {
                "exact_keys": ["role_id", "role_name"],
                "values_by_role": {
                    "8": {
                        "role_id": 8,
                        "role_name": "role8_raw_axis_formula_primitive",
                    },
                    "9": {
                        "role_id": 9,
                        "role_name": "role9_stationary_physical_integral",
                    },
                    "10": {
                        "role_id": 10,
                        "role_name": "role10_killing_factor_geometry",
                    },
                },
            },
            "runtime_code_inputs": {
                "exact_keys": ["producer", "verifier"],
                "value_schema": "/replay_plan_contract/pin_schemas/pin",
                "join": (
                    "producer_and_verifier_are_distinct_future_v3_entrypoint_regular_"
                    "files_matching_source_version_identity_by_role"
                ),
            },
            "runtime_native_library": {
                "exact_keys": ["path", "role", "sha256"],
                "field_schemas": {
                    "path": "canonical_absolute_regular_file_path",
                    "role": ("literal_gmpy2_extension_or_libgmp_or_libmpfr_or_libmpc"),
                    "sha256": "lowercase_sha256_equal_opened_bytes",
                },
            },
            "runtime_native_runtime": {
                "exact_keys": [
                    "gmp",
                    "gmpy2",
                    "mpc",
                    "mpfr",
                    "python_abi",
                    "python_version",
                ],
                "value_schema": "nonempty_canonical_ASCII_string",
            },
            "runtime_python_identity": {
                "exact_keys": ["python_abi", "python_version"],
                "field_schemas": {
                    "python_abi": "nonempty_canonical_ASCII_string",
                    "python_version": "nonempty_canonical_ASCII_string",
                },
            },
            "runtime_python_imports": {
                "exact_keys": ["producer", "verifier"],
                "value_schema": (
                    "unique_lexicographically_sorted_fully_qualified_ASCII_import_name_"
                    "array_with_dynamic_imports_forbidden"
                ),
            },
            "runtime_resolved_python_dependencies": {
                "exact_keys": ["producer", "verifier"],
                "field_schemas": {
                    "producer": {
                        "array_item_schema": (
                            "/replay_plan_contract/objects/resolved_python_dependency"
                        ),
                        "array_rule": (
                            "unique_nonempty_array_sorted_lexicographically_by_import_name"
                        ),
                    },
                    "verifier": {
                        "array_item_schema": (
                            "/replay_plan_contract/objects/resolved_python_dependency"
                        ),
                        "array_rule": (
                            "unique_nonempty_array_sorted_lexicographically_by_import_name"
                        ),
                    },
                },
            },
            "resolved_python_dependency": {
                "exact_keys": ["import_name", "origin_kind", "path", "sha256"],
                "field_schemas": {
                    "import_name": (
                        "fully_qualified_canonical_ASCII_import_name_appearing_exactly_"
                        "once_in_the_corresponding_transitive_python_imports_array"
                    ),
                    "origin_kind": (
                        "literal_builtin_or_frozen_or_file_report_local_or_"
                        "file_runtime_prefix_or_numerical_native_extension"
                    ),
                    "path": (
                        "JSON_null_for_builtin_or_frozen_otherwise_canonical_absolute_"
                        "regular_single_link_file_path"
                    ),
                    "sha256": (
                        "JSON_null_for_builtin_or_frozen_otherwise_lowercase_sha256_"
                        "equal_opened_bytes"
                    ),
                },
                "classification_rules": [
                    "builtin_and_frozen_have_null_path_and_sha256_are_bound_to_the_same_"
                    "pinned_Python_executable_ABI_and_version_and_remain_inside_the_"
                    "declared_non_byte_complete_host_runtime_trust_boundary",
                    "file_report_local_paths_are_below_the_canonical_report_root_and_"
                    "equal_the_same_side_code_input_report_local_dependency_or_allowed_"
                    "shared_protocol_pin",
                    "file_runtime_prefix_paths_are_outside_the_report_root_and_their_"
                    "own_file_bytes_are_pinned_as_runtime_support_not_numerical_source_"
                    "independence_while_their_non_report_dynamic_carriers_remain_in_the_"
                    "declared_host_runtime_trust_boundary",
                    "numerical_native_extension_path_and_sha256_equal_the_pinned_gmpy2_"
                    "extension_native_library_record",
                    "namespace_packages_missing_origins_and_dynamic_imports_are_forbidden",
                ],
            },
            "runtime_global_runner": {
                "exact_keys": [
                    "code_input",
                    "python_executable",
                    "python_imports",
                    "python_runtime",
                    "report_local_dependencies",
                    "resolved_python_dependencies",
                    "runner_contract_sha256",
                    "runner_id",
                ],
                "field_schemas": {
                    "code_input": {"object_schema": "/replay_plan_contract/pin_schemas/pin"},
                    "python_executable": {"object_schema": "/replay_plan_contract/pin_schemas/pin"},
                    "python_imports": (
                        "unique_lexicographically_sorted_transitive_fully_qualified_"
                        "ASCII_import_name_array_with_dynamic_imports_forbidden"
                    ),
                    "python_runtime": ("/replay_plan_contract/objects/runtime_python_identity"),
                    "report_local_dependencies": {
                        "array_item_schema": "/replay_plan_contract/pin_schemas/pin",
                        "array_rule": (
                            "unique_canonical_absolute_pin_array_sorted_by_path_excluding_"
                            "the_code_input"
                        ),
                    },
                    "resolved_python_dependencies": {
                        "array_item_schema": (
                            "/replay_plan_contract/objects/resolved_python_dependency"
                        ),
                        "array_rule": (
                            "unique_nonempty_array_sorted_lexicographically_by_import_name"
                        ),
                    },
                    "runner_contract_sha256": (
                        "lowercase_sha256_of_raw_canonical_global_replay_runner_contract_"
                        "section_bytes_after_this_operation_model_is_frozen"
                    ),
                    "runner_id": ("literal_roles_8_10_global_replay_runner_v2"),
                },
                "closure_rules": [
                    "every_transitive_python_import_name_has_exactly_one_resolved_"
                    "python_dependency_record_and_no_extra_record_is_present",
                    "every_report_local_import_origin_is_pinned_as_the_code_input_or_one_"
                    "report_local_dependency",
                    "the_runner_contains_or_imports_no_numerical_method_function_or_constant",
                    "the_runner_code_input_basename_is_execute_continuum_c1_n0_roles_8_"
                    "10_replay_v2.py",
                ],
            },
            "runtime_host_trust_boundary": {
                "exact_keys": [
                    "byte_complete",
                    "darwin_kernel_release",
                    "machine",
                    "macos_build_version",
                    "scope",
                    "status",
                ],
                "field_schemas": {
                    "byte_complete": "literal_false",
                    "darwin_kernel_release": (
                        "nonempty_canonical_ASCII_uname_release_observed_at_freeze"
                    ),
                    "machine": "nonempty_canonical_ASCII_uname_machine_observed_at_freeze",
                    "macos_build_version": (
                        "nonempty_canonical_ASCII_sw_vers_buildVersion_observed_at_freeze"
                    ),
                    "scope": {
                        "exact_order": [
                            "CPython_builtin_and_frozen_module_carrier_bytes_not_"
                            "separately_pinned_beyond_the_Python_executable_ABI_and_version",
                            "non_report_dynamic_dependencies_of_the_Python_executable_"
                            "and_stdlib_or_prefix_extension_modules",
                            "macOS_dyld_shared_cache_usr_lib_and_System_frameworks",
                        ]
                    },
                    "status": ("literal_DECLARED_HOST_RUNTIME_TRUST_BOUNDARY_NOT_BYTE_COMPLETE"),
                },
                "semantic_boundary": (
                    "this_object_is_a_reproducibility_limitation_and_host_compatibility_"
                    "gate_not_a_claim_that_unpinned_carrier_or_OS_bytes_are_authenticated"
                ),
            },
        },
        "plan_field_schemas": {
            "claim_boundary": {"value_constraint": "/replay_plan_contract/plan_claim_boundary"},
            "entries": {
                "cardinality": 3,
                "item_contract": "/replay_plan_contract/entry_contract",
                "order": [8, 9, 10],
            },
            "runtime_closure": {
                "expected_schema": RUNTIME_SCHEMA,
                "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                "representation": "pin_to_separate_immutable_document_not_inline",
            },
            "schema": f"literal_{PLAN_SCHEMA}",
            "shared_context": {"object_schema": "/replay_plan_contract/shared_context_contract"},
            "shared_precommit_context_sha256": (
                "lowercase_sha256_recomputed_under_shared_context_digest"
            ),
            "slots": {
                "cardinality": 10,
                "item_contract": "/replay_plan_contract/slot_object_contract",
                "materialization": (
                    "deep_equal_same_index_slot_template_after_replacing_only_path_field_"
                    "with_path_and_the_actual_canonical_absolute_path"
                ),
            },
            "status": f"literal_{PLAN_STATUS}",
        },
        "candidate_bundle_contract": {
            "claim_boundary": {
                "external_predecessor_commitment_present": False,
                "ordered_roles_8_10_replay_executed": False,
                "production_same_member_bridge_accepted": False,
                "release_eligible": False,
            },
            "exact_keys": [
                "claim_boundary",
                "member_spec",
                "method_parameter_registry",
                "operation_model",
                "replay_plan",
                "runtime_closure",
                "schema",
                "shared_precommit_context_sha256",
                "status",
            ],
            "field_schemas": {
                "claim_boundary": {"value_constraint": "/replay_plan_contract/plan_claim_boundary"},
                "member_spec": {
                    "expected_schema": ("encounter_continuum_c1_c2_n0_member_spec_v4_candidate"),
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "method_parameter_registry": {
                    "expected_schema": (
                        "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
                    ),
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "operation_model": {
                    "expected_schema": SCHEMA,
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "replay_plan": {
                    "expected_schema": PLAN_SCHEMA,
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "runtime_closure": {
                    "expected_schema": RUNTIME_SCHEMA,
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "schema": ("literal_encounter_continuum_c1_n0_precommit_candidate_bundle_v2"),
                "shared_precommit_context_sha256": "lowercase_sha256_equal_plan_value",
                "status": ("literal_RESULT_BLIND_PRECOMMIT_CANDIDATE_BUNDLE_NO_EXECUTION_RESULTS"),
            },
            "join_rules": [
                "claim_boundary_byte_equals_plan_claim_boundary",
                "replay_plan_pin_authenticates_the_exact_plan_v2_bytes",
                "runtime_closure_pin_equals_the_plan_runtime_closure_pin",
                "member_spec_method_parameter_registry_and_operation_model_pins_equal_"
                "the_corresponding_plan_shared_context_pins",
                "shared_precommit_context_sha256_equals_the_plan_value",
                "the_bundle_contains_no_request_output_result_or_receipt_field",
            ],
            "publication": ("canonical_ASCII_immutable_0444_single_link_atomic_no_replace_file"),
            "schema": "encounter_continuum_c1_n0_precommit_candidate_bundle_v2",
            "status": "RESULT_BLIND_PRECOMMIT_CANDIDATE_BUNDLE_NO_EXECUTION_RESULTS",
        },
        "entry_contract": {
            "catalog_order": [8, 9, 10],
            "exact_keys": [
                "entry_id",
                "input_authorities",
                "invocations",
                "method_selection",
                "output_slot_ids",
                "partition_path_bindings",
                "precommit_projection_sha256",
                "request_slot_id",
                "role",
                "runtime_role_id",
            ],
            "projection_digest": (
                "sha256(encounter-role-replay-entry-v2+NUL+uint64be_length+"
                "canonical_entry_without_projection_digest)"
            ),
            "field_schemas": {
                "entry_id": {
                    "value_constraint": ("/replay_plan_contract/entry_contract/values_by_role")
                },
                "input_authorities": {
                    "exact_keys": (
                        "/replay_plan_contract/entry_contract/"
                        "normative_input_authority_keys_by_role"
                    ),
                    "expected_schemas": (
                        "/replay_plan_contract/entry_contract/authority_schema_by_key"
                    ),
                    "value_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "invocations": {
                    "exact_keys_by_role": {
                        "8": ["producer", "verifier"],
                        "9": ["producer", "verifier"],
                        "10": ["transaction_orchestrator"],
                    },
                    "value_schema": "/replay_plan_contract/objects/invocation",
                },
                "method_selection": {
                    "cardinalities_by_role": {"8": 4, "9": 3, "10": 4},
                    "registry_join": (
                        "ordered_unique_string_IDs_are_looked_up_in_the_pinned_registry_"
                        "v4_and_each_selected_record_digest_is_recomputed_no_plan_v1_"
                        "record_or_dictionary_shape_is_accepted"
                    ),
                    "value_constraint": (
                        "/replay_plan_contract/entry_contract/method_parameter_ids_by_role"
                    ),
                },
                "output_slot_ids": {
                    "value_constraint": ("/replay_plan_contract/entry_contract/values_by_role")
                },
                "partition_path_bindings": {
                    "cardinality": 36,
                    "item_schema": ("/replay_plan_contract/objects/replay_partition_binding"),
                    "order": (
                        "configuration_index_0_through_11_then_midpoint_relative_"
                        "parallel_relative_perpendicular"
                    ),
                    "three_entry_join": "byte_identical_across_all_three_entries",
                },
                "precommit_projection_sha256": ("lowercase_sha256_under_projection_digest_rule"),
                "request_slot_id": {
                    "value_constraint": ("/replay_plan_contract/entry_contract/values_by_role")
                },
                "role": "literal_8_9_or_10_matching_catalog_position",
                "runtime_role_id": {
                    "value_constraint": ("/replay_plan_contract/entry_contract/values_by_role")
                },
            },
            "authority_schema_by_key": {
                "anti_vacuity_policy": (
                    "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate"
                ),
                "configuration": ("encounter_physical_configuration_family_control_free_v1"),
                "factorization": ("encounter_continuum_c1_factorization_source_v2_candidate"),
                "ideal_formula": "encounter_continuum_c1_ideal_formula_source_v1",
                "killing_geometry": "encounter_physical_killing_geometry_source_v1",
                "member_spec": ("encounter_continuum_c1_c2_n0_member_spec_v4_candidate"),
                "method_parameter_registry": (
                    "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
                ),
                "reference_density": ("encounter_continuum_c1_reference_density_source_v1"),
                "sealed_authentication_mirror": (
                    "encounter_continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate"
                ),
            },
            "authority_join_rules": [
                "authority_keys_present_in_shared_context_equal_the_same_schema_path_"
                "and_sha256_after_absolute_materialization",
                "killing_geometry_and_sealed_authentication_mirror_equal_the_operation_"
                "model_authority_bindings_after_absolute_materialization",
                "every_pin_is_opened_immutably_and_matches_schema_and_sha256",
            ],
            "method_parameter_ids_by_role": {
                "8": [
                    "raw_flux_directed_mpfr_320_v2",
                    "raw_flux_directed_mpfr_640_sentinel_v2",
                    "raw_flux_binary64_decode_v2",
                    "exact_fraction_expression_dag_v2",
                ],
                "9": [
                    "stationary_directed_mpfr_320_v2",
                    "stationary_directed_mpfr_640_sentinel_v2",
                    "exact_fraction_expression_dag_v2",
                ],
                "10": [
                    "killing_contact_profile_mpfr_192_v3",
                    "killing_analytic_disk_area_mpfr_256_v3",
                    "killing_source_independent_same_backend_verifier_v3",
                    "killing_exact_contact_cell_classification_v3",
                ],
            },
            "invocation_templates_by_role": {
                "8": {
                    "producer": {
                        "argv": [
                            "{role8_pinned_python}",
                            "-I",
                            "-B",
                            "{role8_pinned_producer}",
                            "--request",
                            "{slot:role8_request}",
                            "--output",
                            "{slot:role8_artifact}",
                        ],
                        "invocation_id": "role8_raw_axis_formula_producer_v3",
                    },
                    "verifier": {
                        "argv": [
                            "{role8_pinned_python}",
                            "-I",
                            "-B",
                            "{role8_pinned_verifier}",
                            "--request",
                            "{slot:role8_request}",
                            "--output",
                            "{slot:role8_artifact}",
                            "--receipt",
                            "{slot:role8_validation_receipt}",
                        ],
                        "invocation_id": "role8_raw_axis_formula_verifier_v3",
                    },
                },
                "9": {
                    "producer": {
                        "argv": [
                            "{role9_pinned_python}",
                            "-I",
                            "-B",
                            "{role9_pinned_producer}",
                            "--request",
                            "{slot:role9_request}",
                            "--output",
                            "{slot:role9_artifact}",
                        ],
                        "invocation_id": "role9_stationary_integrals_producer_v3",
                    },
                    "verifier": {
                        "argv": [
                            "{role9_pinned_python}",
                            "-I",
                            "-B",
                            "{role9_pinned_verifier}",
                            "--request",
                            "{slot:role9_request}",
                            "--output",
                            "{slot:role9_artifact}",
                            "--receipt",
                            "{slot:role9_validation_receipt}",
                        ],
                        "invocation_id": "role9_stationary_integrals_verifier_v3",
                    },
                },
                "10": {
                    "transaction_orchestrator": {
                        "argv": [
                            "{role10_pinned_python}",
                            "-I",
                            "-B",
                            "{role10_pinned_verifier}",
                            "--request",
                            "{slot:role10_request}",
                            "--output",
                            "{slot:role10_artifact_directory}",
                            "--semantic-receipt",
                            "{slot:role10_semantic_receipt}",
                            "--receipt",
                            "{slot:role10_outer_validation_receipt}",
                        ],
                        "invocation_id": ("role10_killing_geometry_transaction_orchestrator_v3"),
                    },
                },
            },
            "invocation_process_digest_join": (
                "every_invocation_object_has_process_contract_sha256_equal_sha256_of_"
                "canonical_operation_model_v2_process_contract_section_bytes"
            ),
            "invocation_materialization": (
                "each_argv_deep_equals_the_same_role_and_caller_template_after_exact_"
                "substitution_of_runtime_closure_python_and_v3_code_input_paths_and_"
                "materialized_slot_paths_no_extra_flag_or_cwd_field"
            ),
            "role10_orchestration_boundary": (
                "the_role10_plan_has_one_public_orchestrator_invocation_using_the_"
                "pinned_verifier_entrypoint_it_resolves_the_separate_pinned_producer_"
                "from_runtime_closure_launches_it_only_as_an_internal_child_into_an_"
                "owned_hidden_staged_artifact_runs_two_semantic_children_stages_both_"
                "receipts_and_owns_the_single_three_output_transaction_through_commit_"
                "or_rollback_no_lock_or_journal_handoff_between_public_processes"
            ),
            "runtime_role_join": (
                "entry.runtime_role_id_is_the_JSON_integer_8_9_or_10_equal_to_the_"
                "selected_runtime_roles_item.role_id_and_entry.entry_id_equals_that_"
                "runtime_role_item.role_name"
            ),
            "normative_input_authority_keys_by_role": {
                "8": [
                    "anti_vacuity_policy",
                    "configuration",
                    "ideal_formula",
                    "member_spec",
                    "method_parameter_registry",
                    "reference_density",
                    "sealed_authentication_mirror",
                ],
                "9": [
                    "anti_vacuity_policy",
                    "configuration",
                    "ideal_formula",
                    "member_spec",
                    "method_parameter_registry",
                    "reference_density",
                    "sealed_authentication_mirror",
                ],
                "10": [
                    "anti_vacuity_policy",
                    "configuration",
                    "factorization",
                    "ideal_formula",
                    "killing_geometry",
                    "member_spec",
                    "method_parameter_registry",
                    "sealed_authentication_mirror",
                ],
            },
            "role_numbers_are_catalog_order_not_dependency_edges": True,
            "source_version_identity_by_role": {
                "10": {
                    "producer_basename": (
                        "build_continuum_c1_n0_candidate_native_killing_factor_geometry_v3.py"
                    ),
                    "verifier_basename": (
                        "validate_continuum_c1_n0_candidate_native_killing_factor_geometry_v3.py"
                    ),
                },
                "8": {
                    "producer_basename": (
                        "build_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py"
                    ),
                    "verifier_basename": (
                        "validate_continuum_c1_n0_candidate_native_raw_axis_formula_v3.py"
                    ),
                },
                "9": {
                    "producer_basename": (
                        "build_continuum_c1_n0_candidate_native_stationary_integrals_v3.py"
                    ),
                    "verifier_basename": (
                        "validate_continuum_c1_n0_candidate_native_stationary_integrals_v3.py"
                    ),
                },
            },
            "version_boundary": (
                "the_existing_role8_role9_and_role10_v2_entrypoints_remain_historical_"
                "plan_v1_request_v3_compatibility_shells_and_must_not_be_mutated_into_"
                "dual_mode_loaders_or_selected_by_plan_v2"
            ),
            "values_by_role": {
                "8": {
                    "entry_id": "role8_raw_axis_formula_primitive",
                    "invocation_slot_joins": {
                        "producer": {
                            "reads": ["role8_request"],
                            "writes": ["role8_artifact"],
                        },
                        "verifier": {
                            "reads": ["role8_request", "role8_artifact"],
                            "writes": ["role8_validation_receipt"],
                        },
                    },
                    "output_slot_ids": [
                        "role8_artifact",
                        "role8_validation_receipt",
                    ],
                    "request_slot_id": "role8_request",
                    "role": 8,
                    "runtime_role_id": 8,
                },
                "9": {
                    "entry_id": "role9_stationary_physical_integral",
                    "invocation_slot_joins": {
                        "producer": {
                            "reads": ["role9_request"],
                            "writes": ["role9_artifact"],
                        },
                        "verifier": {
                            "reads": ["role9_request", "role9_artifact"],
                            "writes": ["role9_validation_receipt"],
                        },
                    },
                    "output_slot_ids": [
                        "role9_artifact",
                        "role9_validation_receipt",
                    ],
                    "request_slot_id": "role9_request",
                    "role": 9,
                    "runtime_role_id": 9,
                },
                "10": {
                    "entry_id": "role10_killing_factor_geometry",
                    "invocation_slot_joins": {
                        "transaction_orchestrator": {
                            "reads": [
                                "role10_request",
                            ],
                            "writes": [
                                "role10_artifact_directory",
                                "role10_semantic_receipt",
                                "role10_outer_validation_receipt",
                            ],
                        },
                    },
                    "output_slot_ids": [
                        "role10_artifact_directory",
                        "role10_semantic_receipt",
                        "role10_outer_validation_receipt",
                    ],
                    "request_slot_id": "role10_request",
                    "role": 10,
                    "runtime_role_id": 10,
                },
            },
        },
        "global_path_rules": {
            "all_ten_slots": (
                "lexically_normalized_absolute_pairwise_unequal_and_no_ancestor_descendant_alias"
            ),
            "descriptor_resolution": (
                "open_every_existing_ancestor_component_NOFOLLOW_record_dev_ino_and_"
                "reject_equal_parent_identity_plus_equal_leaf_or_any_resolved_ancestor_"
                "relationship_including_symlink_mount_and_hardlink_aliases"
            ),
            "freshness": "all_seven_outputs_absent_before_any_role_launch",
            "input_path_classes": [
                "three_request_slots",
                "external_predecessor_commitment",
                "replay_plan",
                "candidate_bundle",
                "runtime_closure",
                "operation_model",
                "authority_files",
                "sealed_mirror_tree",
                "thirty_six_partition_files",
                "python_executable",
                "six_role_v3_entrypoints_and_one_global_runner_v2_entrypoint",
                "report_local_dependencies",
                "resolved_python_dependency_files",
                "allowed_shared_protocol",
                "native_libraries",
                "transaction_journals",
                "single_writer_locks",
                "private_stage_roots",
            ],
            "output_input_disjointness": (
                "every_output_is_unequal_and_not_ancestor_or_descendant_of_every_request_"
                "commitment_plan_bundle_runtime_closure_operation_model_authority_"
                "mirror_partition_"
                "role_or_runner_source_executable_resolved_dependency_extension_native_"
                "library_transaction_journal_and_single_writer_lock_path"
            ),
            "output_slot_ids": [
                "role8_artifact",
                "role8_validation_receipt",
                "role9_artifact",
                "role9_validation_receipt",
                "role10_artifact_directory",
                "role10_semantic_receipt",
                "role10_outer_validation_receipt",
            ],
            "peer_output_reads_after_launch": "forbidden",
            "preflight": (
                "one_descriptor_anchored_global_preflight_revalidates_every_existing_"
                "input_and_parent_dev_ino_checks_every_resolved_lexical_symlink_hardlink_"
                "mount_and_ancestor_relation_and_proves_all_seven_outputs_absent_before_"
                "any_role_launch"
            ),
            "request_slot_ids": [
                "role8_request",
                "role9_request",
                "role10_request",
            ],
            "role10_transaction_parent_join": (
                "role10_artifact_directory_role10_semantic_receipt_and_role10_outer_"
                "validation_receipt_are_three_distinct_leaf_names_below_one_exact_same_"
                "preexisting_authenticated_mode_0700_owner_effective_uid_output_parent"
            ),
            "same_parent": "allowed_when_leaf_slots_remain_distinct",
        },
        "global_replay_runner_contract": {
            "ack_contract": {
                "encoding": (
                    "one_canonical_ASCII_JSON_line_with_one_trailing_LF_and_no_other_stdout"
                ),
                "exact_keys": [
                    "completed_role_ids",
                    "schema",
                    "status",
                ],
                "field_schemas": {
                    "completed_role_ids": "literal_integer_array_[8,9,10]",
                    "schema": ("literal_encounter_roles_8_10_global_replay_runner_ack_v1"),
                    "status": ("literal_ROLES_8_10_REPLAY_OUTPUTS_AUTHENTICATED_NO_PROMOTION"),
                },
                "emission_gate": (
                    "only_after_all_seven_outputs_are_reopened_reauthenticated_and_all_"
                    "three_role_workflows_report_success_no_scientific_or_same_member_"
                    "claim_is_implied"
                ),
            },
            "argv": [
                "{pinned_python_executable}",
                "-I",
                "-B",
                "{pinned_global_runner_v2}",
                "--external-commitment",
                "{external_predecessor_commitment}",
                "--candidate-bundle",
                "{candidate_bundle_v2}",
                "--plan",
                "{replay_plan_v2}",
                "--runtime-closure",
                "{runtime_closure_v1}",
                "--role8-request",
                "{slot:role8_request}",
                "--role9-request",
                "{slot:role9_request}",
                "--role10-request",
                "{slot:role10_request}",
            ],
            "argv_materialization": (
                "argv_deep_equals_this_template_after_substituting_only_the_runtime_"
                "closure_pinned_Python_and_runner_paths_the_external_commitment_path_"
                "byte_identical_across_all_three_requests_the_candidate_bundle_path_"
                "authenticated_by_that_commitment_the_plan_and_runtime_closure_pins_"
                "and_the_three_plan_request_slot_paths_no_cwd_shell_or_extra_flag"
            ),
            "entrypoint_basename": ("execute_continuum_c1_n0_roles_8_10_replay_v2.py"),
            "implementation_status": "REQUIRED_BEFORE_REPLAY_NOT_PRESENT_IN_THIS_MODEL",
            "launch_graph": (
                "after_the_single_global_preflight_roles_8_9_10_may_run_in_parallel_"
                "while_each_role_preserves_its_internal_producer_then_verifier_or_"
                "single_transaction_orchestrator_edges_peer_output_reads_are_forbidden"
            ),
            "prelaunch_authority": (
                "the_runtime_closure_pinned_runner_authenticates_its_own_source_contract_"
                "Python_and_transitive_dependencies_then_authenticates_the_external_"
                "commitment_bundle_plan_runtime_closure_and_all_three_request_v4_files_"
                "including_the_four_field_cross_request_equality_join_then_obtains_one_"
                "descriptor_anchored_snapshot_proving_all_seven_outputs_absent_before_"
                "launching_any_role"
            ),
            "required_claim_boundary": (
                "the_plan_bundle_requests_and_individual_role_CLIs_do_not_by_"
                "themselves_establish_global_freshness_or_ordered_replay"
            ),
            "runner_id": "roles_8_10_global_replay_runner_v2",
            "runtime_binding": (
                "runtime_closure.global_runner_deep_matches_the_runtime_global_runner_"
                "schema_its_runner_contract_sha256_equals_sha256_of_raw_canonical_"
                "bytes_of_this_complete_global_replay_runner_contract_section_and_the_"
                "runner_entrypoint_Python_and_all_resolved_dependencies_participate_in_"
                "global_output_disjointness"
            ),
            "seven_output_preflight": (
                "under_one_descriptor_anchored_snapshot_authenticate_all_existing_inputs_"
                "and_output_parents_reject_every_alias_ancestor_descendant_symlink_"
                "hardlink_or_mount_conflict_and_require_the_seven_materialized_output_"
                "slots_absent_before_the_first_role_process_spawn"
            ),
        },
        "plan_exact_keys": [
            "claim_boundary",
            "entries",
            "runtime_closure",
            "schema",
            "shared_context",
            "shared_precommit_context_sha256",
            "slots",
            "status",
        ],
        "plan_claim_boundary": {
            "external_predecessor_commitment_present": False,
            "ordered_roles_8_10_replay_executed": False,
            "production_same_member_bridge_accepted": False,
            "release_eligible": False,
        },
        "pin_schemas": {
            "pin": {
                "exact_keys": ["path", "sha256"],
                "types": {
                    "path": "actual_canonical_absolute_path",
                    "sha256": "lowercase_sha256",
                },
            },
            "schema_pin": {
                "exact_keys": ["path", "schema", "sha256"],
                "types": {
                    "path": "actual_canonical_absolute_path",
                    "schema": "exact_expected_schema",
                    "sha256": "lowercase_sha256",
                },
            },
        },
        "request_contract": {
            "exact_keys": [
                "external_predecessor_commitment",
                "plan",
                "plan_entry_id",
                "role",
                "schema",
                "shared_precommit_context_sha256",
                "shared_replay_context_sha256",
                "status",
            ],
            "schemas_by_role": {
                "8": ROLE8_REQUEST_SCHEMA,
                "9": ROLE9_REQUEST_SCHEMA,
                "10": ROLE10_REQUEST_SCHEMA,
            },
            "field_schemas": {
                "external_predecessor_commitment": {
                    "expected_document_schema": ("encounter_external_predecessor_commitment_v1"),
                    "expected_document_status": (
                        "EXTERNAL_PREDECESSOR_COMMITMENT_STRUCTURALLY_BOUND_"
                        "AUTHENTICITY_NOT_LOCALLY_PROVEN"
                    ),
                    "object_schema": "/replay_plan_contract/pin_schemas/pin",
                },
                "plan": {
                    "expected_document_schema": PLAN_SCHEMA,
                    "object_schema": "/replay_plan_contract/pin_schemas/pin",
                },
                "plan_entry_id": {
                    "value_constraint": ("/replay_plan_contract/entry_contract/values_by_role")
                },
                "role": {"object_schema": "/replay_plan_contract/objects/request_role"},
                "schema": {
                    "value_constraint": ("/replay_plan_contract/request_contract/schemas_by_role")
                },
                "shared_precommit_context_sha256": "lowercase_sha256_equal_plan_value",
                "shared_replay_context_sha256": "lowercase_sha256_under_exact_preimage",
                "status": f"literal_{REQUEST_STATUS}",
            },
            "join_rules": [
                "exactly_three_requests_in_role_order_8_9_10_each_path_equals_the_"
                "matching_plan_request_slot",
                "plan_pin_sha256_authenticates_the_exact_plan_bytes",
                "plan_entry_id_role_and_schema_select_the_same_plan_entry",
                "external_commitment_authenticates_the_exact_candidate_bundle_v2_"
                "which_in_turn_authenticates_this_plan_runtime_closure_and_operation_"
                "model_before_any_request_is_materialized",
                "shared_precommit_context_sha256_equals_the_plan_value",
                "all_three_requests_have_byte_identical_external_predecessor_commitment_"
                "pin_plan_pin_shared_precommit_context_sha256_and_shared_replay_context_"
                "sha256_values",
            ],
            "materialization": (
                "after_external_commitment_authentication_all_three_request_slots_are_"
                "preflight_absent_then_each_canonical_request_is_published_immutable_"
                "0444_single_link_atomic_no_replace_any_owned_partial_publication_is_"
                "rolled_back_before_success"
            ),
            "shared_replay_preimage": {
                "domain": "encounter-continuum-c1-n0-shared-replay-context-v2",
                "exact_keys": [
                    "external_predecessor_commitment_sha256",
                    "replay_plan_sha256",
                    "shared_precommit_context_sha256",
                ],
                "framing": "domain_ascii+NUL+canonical_preimage_bytes_no_length_prefix",
                "value_schema": "lowercase_sha256",
            },
            "shared_replay_digest": (
                "sha256(encounter-continuum-c1-n0-shared-replay-context-v2+NUL+"
                "canonical_ASCII_object_with_exact_keys_external_predecessor_commitment_"
                "sha256_replay_plan_sha256_shared_precommit_context_sha256)"
            ),
            "status": REQUEST_STATUS,
        },
        "runtime_closure": {
            "claim_boundary": {
                "complete_host_runtime_image": False,
                "complete_report_local_and_declared_numerical_runtime_closure": True,
                "host_runtime_dependencies_byte_pinned": False,
                "legacy_scientific_backend_imported": False,
                "output_or_result_hash_present": False,
                "result_artifact_dependency_present": False,
            },
            "exact_keys": [
                "claim_boundary",
                "global_runner",
                "host_runtime_trust_boundary",
                "process_contract",
                "roles",
                "schema",
                "status",
            ],
            "field_schemas": {
                "claim_boundary": {
                    "value_constraint": ("/replay_plan_contract/runtime_closure/claim_boundary")
                },
                "global_runner": {
                    "object_schema": ("/replay_plan_contract/objects/runtime_global_runner")
                },
                "host_runtime_trust_boundary": {
                    "object_schema": ("/replay_plan_contract/objects/runtime_host_trust_boundary")
                },
                "process_contract": ("deep_equal_operation_model_v2_process_contract_section"),
                "roles": {
                    "cardinality": 3,
                    "item_exact_keys": ("/replay_plan_contract/runtime_closure/role_exact_keys"),
                    "item_field_schemas": (
                        "/replay_plan_contract/runtime_closure/role_field_schemas"
                    ),
                    "item_values": ("/replay_plan_contract/runtime_closure/role_values"),
                    "order": [8, 9, 10],
                },
                "schema": f"literal_{RUNTIME_SCHEMA}",
                "status": (
                    "literal_FROZEN_SOURCE_SEPARATED_ROLES_8_10_IMPLEMENTATION_"
                    "RUNTIME_CLOSURE_NO_EXECUTION_RESULTS"
                ),
            },
            "role_exact_keys": [
                "allowed_shared_protocol",
                "code_inputs",
                "native_libraries",
                "native_runtime",
                "python_executable",
                "python_imports",
                "report_local_dependencies",
                "resolved_python_dependencies",
                "role_id",
                "role_name",
            ],
            "role_field_schemas": {
                "allowed_shared_protocol": {
                    "allowed_types": ["JSON_null", "pin_object"],
                    "nonnull_object_schema": ("/replay_plan_contract/pin_schemas/pin"),
                    "semantic_constraint": (
                        "when_nonnull_the_same_single_semantics_free_protocol_pin_is_"
                        "used_by_every_role_that_imports_it_and_no_numerical_function_"
                        "or_constant_is_present"
                    ),
                },
                "code_inputs": {
                    "object_schema": ("/replay_plan_contract/objects/runtime_code_inputs")
                },
                "native_libraries": {
                    "cardinality": 4,
                    "item_schema": ("/replay_plan_contract/objects/runtime_native_library"),
                    "order": ["gmpy2_extension", "libgmp", "libmpfr", "libmpc"],
                },
                "native_runtime": {
                    "object_schema": ("/replay_plan_contract/objects/runtime_native_runtime")
                },
                "python_executable": {"object_schema": "/replay_plan_contract/pin_schemas/pin"},
                "python_imports": {
                    "object_schema": ("/replay_plan_contract/objects/runtime_python_imports")
                },
                "report_local_dependencies": {
                    "exact_keys": ["producer", "verifier"],
                    "array_item_schema": ("/replay_plan_contract/pin_schemas/pin"),
                    "array_rule": (
                        "unique_canonical_absolute_pins_sorted_lexicographically_by_"
                        "path_excluding_code_inputs_and_allowed_shared_protocol"
                    ),
                },
                "resolved_python_dependencies": {
                    "object_schema": (
                        "/replay_plan_contract/objects/runtime_resolved_python_dependencies"
                    ),
                    "closure_rule": (
                        "for_each_side_every_transitive_python_import_name_has_exactly_"
                        "one_resolved_python_dependency_object_and_no_extra_object"
                    ),
                },
                "role_id": "literal_8_9_or_10",
                "role_name": ("exact_entry_id_selected_by_the_same_integer_role_id"),
            },
            "role_order": [8, 9, 10],
            "role_values": {
                "10": {
                    "role_id": 10,
                    "role_name": "role10_killing_factor_geometry",
                },
                "8": {
                    "role_id": 8,
                    "role_name": "role8_raw_axis_formula_primitive",
                },
                "9": {
                    "role_id": 9,
                    "role_name": "role9_stationary_physical_integral",
                },
            },
            "schema": RUNTIME_SCHEMA,
            "source_rule": (
                "for_each_role_the_producer_source_set_is_code_inputs.producer_union_"
                "report_local_dependencies.producer_and_the_verifier_source_set_is_"
                "code_inputs.verifier_union_report_local_dependencies.verifier_the_two_"
                "sets_are_disjoint_by_canonical_path_and_sha256_only_the_globally_"
                "identical_nonnull_allowed_shared_protocol_pin_may_overlap"
            ),
            "resolved_dependency_rule": (
                "each_side_transitively_resolves_imports_until_fixed_point_with_dynamic_"
                "imports_forbidden_file_report_local_records_joining_the_same_side_"
                "source_pins_numerical_native_extension_records_joining_the_pinned_"
                "gmpy2_library_and_each_file_runtime_prefix_module_origin_pinning_its_"
                "own_bytes_builtin_frozen_and_non_report_dynamic_carrier_or_OS_bytes_"
                "remain_inside_the_explicit_non_byte_complete_host_runtime_trust_"
                "boundary_and_are_not_a_numerical_source_independence_claim_no_report_"
                "root_path_may_be_reclassified_as_runtime_prefix"
            ),
            "source_version_boundary": (
                "all_six_code_inputs_are_future_v3_entrypoints_matching_entry_contract."
                "source_version_identity_by_role_existing_v2_plan_v1_request_v3_shells_"
                "are_forbidden"
            ),
            "status": (
                "FROZEN_SOURCE_SEPARATED_ROLES_8_10_IMPLEMENTATION_RUNTIME_CLOSURE_"
                "NO_EXECUTION_RESULTS"
            ),
            "value_joins": [
                "each_plan_entry_runtime_role_id_selects_exactly_one_same_id_role",
                "each_plan_entry_entry_id_equals_the_selected_runtime_role_name",
                "each_invocation_argv_0_equals_the_pinned_python_executable_path",
                "each_invocation_argv_1_2_are_exactly_-I_-B",
                "role8_and_role9_producer_verifier_invocation_entrypoints_equal_the_"
                "matching_code_input_paths",
                "role10_transaction_orchestrator_entrypoint_equals_the_role10_verifier_"
                "code_input_and_it_launches_the_role10_producer_code_input_only_as_an_"
                "internal_staged_child",
                "all_runtime_code_dependency_executable_extension_and_library_paths_"
                "participate_in_global_output_disjointness",
                "global_runner_code_Python_import_and_resolved_dependency_closure_is_"
                "complete_and_its_contract_sha256_binds_the_global_runner_contract",
                "the_one_host_runtime_trust_boundary_applies_identically_to_all_roles_"
                "and_the_global_runner_and_its_byte_complete_false_status_is_required",
                "producer_and_verifier_transitive_numerical_source_sets_are_disjoint",
                "process_contract_equals_the_operation_model_v2_process_contract",
            ],
            "whole_document": (
                "canonical_ASCII_immutable_0444_single_link_atomic_no_replace_regular_"
                "file_complete_for_all_six_v3_entrypoints_the_one_global_runner_v2_"
                "every_report_local_source_every_Python_module_origin_and_the_declared_"
                "gmpy2_GMP_MPFR_MPC_native_closure_only_the_serialized_host_runtime_"
                "trust_boundary_is_explicitly_not_byte_complete_or_authenticated"
            ),
        },
        "schema": PLAN_SCHEMA,
        "shared_context_contract": {
            "exact_keys": [
                "anti_vacuity_policy",
                "configuration",
                "configuration_row_inventory_sha256",
                "factorization",
                "ideal_formula",
                "member_identity_sha256",
                "member_spec",
                "method_parameter_registry",
                "partition_inventory_sha256",
                "reference_density",
                "role10_operation_model",
            ],
            "field_schemas": {
                "anti_vacuity_policy": {
                    "expected_schema": (
                        "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate"
                    ),
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "configuration": {
                    "expected_schema": ("encounter_physical_configuration_family_control_free_v1"),
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "configuration_row_inventory_sha256": (
                    "literal_8da99e7910cac1f2ba6b69fb2d0ec52b21412abfa1d59c898462e138d82ebbb2"
                ),
                "factorization": {
                    "expected_schema": ("encounter_continuum_c1_factorization_source_v2_candidate"),
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "ideal_formula": {
                    "expected_schema": ("encounter_continuum_c1_ideal_formula_source_v1"),
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "member_identity_sha256": (
                    "literal_68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
                ),
                "member_spec": {
                    "expected_schema": ("encounter_continuum_c1_c2_n0_member_spec_v4_candidate"),
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "method_parameter_registry": {
                    "expected_schema": (
                        "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
                    ),
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "partition_inventory_sha256": (
                    "literal_f3507f4eec07e216bd54bcf4486ab5cef1589511367f781174b89fdfe2e7b51f"
                ),
                "reference_density": {
                    "expected_schema": ("encounter_continuum_c1_reference_density_source_v1"),
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
                "role10_operation_model": {
                    "expected_schema": SCHEMA,
                    "object_schema": "/replay_plan_contract/pin_schemas/schema_pin",
                },
            },
            "inventory_digest_lineage": {
                "configuration_rows": (
                    "recompute_the_exact_v1_domain_encounter-continuum-c1-n0-"
                    "configuration-row-inventory-v1_over_the_unchanged_ordered_record_"
                    "array"
                ),
                "partitions": (
                    "recompute_the_exact_v1_domain_encounter-continuum-c1-n0-"
                    "partition-inventory-v1_over_the_unchanged_ordered_record_array"
                ),
            },
            "join_rules": [
                "the_first_seven_authority_schema_pins_equal_the_operation_model_"
                "authority_bindings_after_materializing_canonical_absolute_paths",
                "role10_operation_model_is_the_final_frozen_operation_model_v2_pin",
                "member_identity_sha256_is_recomputed_from_member_v4",
                "configuration_and_partition_inventory_sha256_values_are_recomputed_"
                "under_the_inherited_v1_inventory_domains",
                "all_eight_schema_pin_paths_are_canonical_absolute_regular_single_link_"
                "immutable_files_with_matching_schema_and_sha256",
            ],
        },
        "slot_object_contract": {
            "exact_keys": [
                "kind",
                "lifecycle",
                "node_type",
                "ordinal",
                "path",
                "role",
                "schema",
                "slot_id",
            ],
            "field_schemas": {
                "kind": "exact_same_index_slot_template_literal",
                "lifecycle": "exact_same_index_slot_template_literal",
                "node_type": "exact_same_index_slot_template_literal",
                "ordinal": "JSON_integer_equal_array_index_0_through_9",
                "path": "actual_canonical_absolute_path_not_a_placeholder",
                "role": "exact_same_index_slot_template_literal_8_9_or_10",
                "schema": "exact_same_index_slot_template_literal",
                "slot_id": "exact_same_index_slot_template_literal",
            },
            "materialization_rule": (
                "for_each_index_deep_copy_slot_templates[index]_remove_the_path_field_"
                "key_insert_the_path_key_with_the_actual_canonical_absolute_path_and_"
                "make_no_other_change"
            ),
            "set_joins": [
                "serialized_slot_array_cardinality_is_exactly_10",
                "slot_ids_are_unique_and_equal_the_ten_template_ids_in_order",
                "ordinals_are_unique_and_equal_array_indices_0_through_9",
                "paths_are_pairwise_unique_and_pass_global_path_rules",
                "request_indices_are_exactly_0_3_6",
                "output_indices_are_exactly_1_2_4_5_7_8_9",
                "only_role10_artifact_directory_has_node_type_directory",
            ],
        },
        "shared_context_exact_keys": [
            "anti_vacuity_policy",
            "configuration",
            "configuration_row_inventory_sha256",
            "factorization",
            "ideal_formula",
            "member_identity_sha256",
            "member_spec",
            "method_parameter_registry",
            "partition_inventory_sha256",
            "reference_density",
            "role10_operation_model",
        ],
        "shared_context_digest": (
            "sha256(encounter-shared-precommit-context-v2+NUL+canonical_shared_context)"
        ),
        "slot_templates": slots,
        "status": PLAN_STATUS,
    }


def process_contract(resource_caps: dict[str, Any]) -> dict[str, Any]:
    return {
        "ack_contracts": {
            "encoding": (
                "each_success_ACK_is_one_canonical_ASCII_JSON_line_with_one_trailing_"
                "LF_and_no_other_stdout"
            ),
            "producer_child": {
                "exact_keys": [
                    "darwin_cf_user_text_encoding_observation",
                    "schema",
                    "staged_artifact_binding_sha256",
                    "status",
                ],
                "field_schemas": {
                    "darwin_cf_user_text_encoding_observation": (
                        "/wire_schema_contract/scalar_encodings/null_or_validated_Darwin_string"
                    ),
                    "schema": "literal_encounter_role10_producer_child_ack_v1",
                    "staged_artifact_binding_sha256": (
                        "/process_contract/digest_contracts/staged_artifact_binding_sha256"
                    ),
                    "status": ("literal_ROLE10_STAGED_ARTIFACT_COMPLETED_NO_PROMOTION"),
                },
                "schema": "encounter_role10_producer_child_ack_v1",
                "status": "ROLE10_STAGED_ARTIFACT_COMPLETED_NO_PROMOTION",
            },
            "public_transaction_commit": {
                "emission_gate": (
                    "only_after_COMMITTED_is_durable_all_three_outputs_are_reopened_"
                    "and_reauthenticated_the_owned_journal_is_removed_and_parent_fsync_"
                    "and_the_final_before_caller_ACK_parent_identity_check_passes"
                ),
                "exact_keys": [
                    "artifact_binding_sha256",
                    "darwin_cf_user_text_encoding_observation",
                    "outer_receipt_sha256",
                    "schema",
                    "semantic_receipt_sha256",
                    "status",
                ],
                "field_schemas": {
                    "artifact_binding_sha256": (
                        "/process_contract/digest_contracts/staged_artifact_binding_sha256"
                    ),
                    "darwin_cf_user_text_encoding_observation": (
                        "/wire_schema_contract/scalar_encodings/null_or_validated_Darwin_string"
                    ),
                    "outer_receipt_sha256": (
                        "lowercase_sha256_equal_reauthenticated_published_outer_receipt"
                    ),
                    "schema": ("literal_encounter_role10_transaction_commit_ack_v1"),
                    "semantic_receipt_sha256": (
                        "lowercase_sha256_equal_reauthenticated_published_semantic_receipt"
                    ),
                    "status": ("literal_ROLE10_THREE_OUTPUT_TRANSACTION_COMMITTED_NO_PROMOTION"),
                },
                "join_rules": [
                    "artifact_binding_sha256_equals_the_authenticated_producer_ACK_"
                    "staged_artifact_binding_sha256",
                    "artifact_binding_sha256_equals_the_composite_recomputed_from_the_"
                    "published_semantic_and_outer_receipt_identical_artifact_binding_"
                    "manifest_sha256_and_tree_inventory_sha256_fields",
                ],
                "schema": "encounter_role10_transaction_commit_ack_v1",
                "status": ("ROLE10_THREE_OUTPUT_TRANSACTION_COMMITTED_NO_PROMOTION"),
            },
            "semantic_child": {
                "exact_keys": [
                    "darwin_cf_user_text_encoding_observation",
                    "schema",
                    "semantic_receipt_sha256",
                    "status",
                ],
                "field_schemas": {
                    "darwin_cf_user_text_encoding_observation": (
                        "/wire_schema_contract/scalar_encodings/null_or_validated_Darwin_string"
                    ),
                    "schema": "literal_encounter_role10_semantic_child_ack_v1",
                    "semantic_receipt_sha256": (
                        "lowercase_sha256_equal_sha256_of_the_canonical_owned_temporary_"
                        "semantic_receipt_bytes"
                    ),
                    "status": ("literal_ROLE10_SEMANTIC_CHILD_COMPLETED_NO_PROMOTION"),
                },
                "schema": "encounter_role10_semantic_child_ack_v1",
                "status": "ROLE10_SEMANTIC_CHILD_COMPLETED_NO_PROMOTION",
            },
            "maximum_bytes": resource_caps["maximum_child_ack_bytes"],
        },
        "digest_contracts": {
            "staged_artifact_binding_sha256": {
                "domain": "encounter-role10-staged-artifact-ack-binding-v1",
                "preimage": (
                    "domain_ascii+NUL+raw_32_byte_SHA256_of_the_complete_canonical_top_"
                    "manifest_envelope+raw_32_byte_manifest_payload_file_inventory_tree_"
                    "sha256_in_that_exact_order_with_no_length_prefix"
                ),
                "recomputation": (
                    "the_orchestrator_reopens_the_owned_staged_tree_recomputes_the_top_"
                    "manifest_whole_file_SHA_and_the_inventory_tree_SHA_requires_the_"
                    "manifest_inventory_join_with_exactly_72_inventory_entries_and_then_"
                    "requires_the_composite_digest_to_equal_the_producer_ACK_field_the_"
                    "top_inventory_excludes_the_top_manifest_so_no_self_hash_cycle_exists"
                ),
            },
        },
        "argv": {
            "child_semantic_verifier": [
                "{pinned_python_executable}",
                "-I",
                "-B",
                "{pinned_verifier_entrypoint}",
                "--semantic-child",
                "--request",
                "{role10_request}",
                "--output",
                "{owned_hidden_staged_role10_artifact_directory}",
                "--semantic-receipt",
                "{owned_temporary_semantic_receipt}",
            ],
            "transaction_orchestrator": [
                "{pinned_python_executable}",
                "-I",
                "-B",
                "{pinned_verifier_entrypoint}",
                "--request",
                "{role10_request}",
                "--output",
                "{role10_artifact_directory}",
                "--semantic-receipt",
                "{role10_semantic_receipt}",
                "--receipt",
                "{role10_outer_validation_receipt}",
            ],
            "producer": [
                "{pinned_python_executable}",
                "-I",
                "-B",
                "{pinned_producer_entrypoint}",
                "--request",
                "{role10_request}",
                "--staged-output",
                "{owned_hidden_staged_role10_artifact_directory}",
            ],
        },
        "argv_materialization": (
            "child_semantic_verifier_is_materialized_twice_with_run_ordinal_1_using_"
            "the_journaled_.semantic-child-0-receipt.json_identity_and_run_ordinal_2_"
            "using_the_distinct_journaled_.semantic-child-1-receipt.json_identity_all_"
            "other_placeholders_are_identical_and_no_child_can_open_the_canonical_"
            "semantic_receipt_staged_inode"
        ),
        "deadline_accounting": {
            "absolute_maximum_single_child_wall_seconds": (
                resource_caps["child_process_deadline_seconds"]
            ),
            "child_signal_and_reap_reserve_seconds": 10,
            "clock": "time_monotonic_absolute_deadlines",
            "phase_caps_seconds": {
                "producer_including_signal_reap": (resource_caps["child_process_deadline_seconds"]),
                "semantic_children_concurrent_including_signal_reap": (
                    resource_caps["semantic_deadline_seconds"]
                ),
                "transaction_orchestrator_total": (resource_caps["outer_deadline_seconds"]),
            },
            "kill_reap_grace_seconds": 5,
            "outer_nonchild_reserve_seconds": resource_caps["outer_nonchild_reserve_seconds"],
            "outer_total_seconds": resource_caps["outer_deadline_seconds"],
            "semantic_seconds": resource_caps["semantic_deadline_seconds"],
            "term_grace_seconds": 5,
            "deadline_rules": [
                "at_or_before_orchestrator_start_capture_D_outer_equal_monotonic_now_"
                "plus_2700_seconds_and_charge_every_operation_to_that_deadline",
                "launch_the_producer_first_with_phase_end_equal_min_of_its_start_plus_"
                "1200_seconds_and_D_outer_minus_1140_seconds_minus_300_seconds",
                "after_authenticated_producer_success_launch_semantic_child_0_and_1_"
                "concurrently_each_with_phase_end_equal_min_of_its_start_plus_1140_"
                "seconds_and_D_outer_minus_300_seconds",
                "for_each_child_stop_accepting_work_and_send_SIGTERM_no_later_than_"
                "phase_end_minus_10_seconds_allow_at_most_5_seconds_then_SIGKILL_and_"
                "allow_at_most_5_seconds_to_reap_no_child_may_remain_live_at_phase_end",
                "the_final_300_seconds_are_reserved_for_parent_checks_fsync_install_"
                "rollback_and_failure_cleanup_and_success_is_forbidden_at_or_after_D_outer",
                "the_frozen_phase_budget_arithmetic_is_1200_plus_1140_plus_300_equal_"
                "2640_less_than_or_equal_to_2700_leaving_60_seconds_for_phase_transition_"
                "overhead_without_weakening_any_phase_or_cleanup_reserve",
            ],
            "timing_rule": (
                "all_spawn_wait_TERM_KILL_reap_fsync_and_owned_cleanup_time_is_charged_"
                "inside_one_2700_second_outer_absolute_deadline_the_two_semantic_children_"
                "are_concurrent_not_sequential_and_every_wait_or_signal_interval_is_"
                "clipped_to_its_phase_end_and_D_outer"
            ),
        },
        "environment": {
            "allowlist_exact": {
                "HOME": "{private_stage}/home",
                "LANG": "C",
                "LC_ALL": "C",
                "TMPDIR": "{private_stage}/tmp",
                "TZ": "UTC",
            },
            "darwin_observation_exception": (
                "only___CF_USER_TEXT_ENCODING_may_be_OS_added_it_must_match_"
                "^0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+$_be_reported_in_"
                "each_applicable_exact_ACK_and_parent_run_observation_and_is_excluded_"
                "from_all_numerical_or_semantic_digests_any_other_added_variable_is_HOLD"
            ),
            "forbidden": [
                "PYTHONHOME",
                "PYTHONPATH",
                "PYTHONSTARTUP",
                "PYTHONUSERBASE",
                "PYTHONHASHSEED",
            ],
        },
        "filesystem": {
            "cwd": (
                "four_distinct_fresh_mode_0700_invocation_subdirectories_for_producer_"
                "child_0_child_1_and_outer_below_the_one_journaled_owned_stage_root_"
                "each_opened_and_identity_rechecked_by_the_orchestrator"
            ),
            "home_and_tmp": (
                "distinct_mode_0700_HOME_and_TMPDIR_children_below_each_invocation_"
                "stage_never_reused_between_clean_children"
            ),
            "stage_disjointness": (
                "stage_is_not_equal_ancestor_or_descendant_of_any_input_or_plan_slot"
            ),
            "temporary_cleanup": "owned_inode_only_preserve_foreign_replacements",
            "umask": "0077",
        },
        "io_and_session": {
            "cap_overrun": (
                "bounded_selector_reads_stop_accepting_at_cap_plus_one_then_SIGTERM_"
                "process_group_wait_up_to_5_seconds_SIGKILL_group_wait_and_reap_up_to_"
                "5_seconds_close_pipe_ends_remove_owned_temporaries_and_HOLD"
            ),
            "close_fds": True,
            "observation_maximum_bytes": resource_caps["maximum_child_observation_bytes"],
            "pass_fds": [],
            "process_group": "start_new_session_true_and_observed_pgid_equals_pid",
            "shell": False,
            "stderr_maximum_bytes": resource_caps["maximum_child_stderr_bytes"],
            "stderr_success_rule": "exactly_empty",
            "stdin": "DEVNULL",
            "stdout_ack_maximum_bytes": resource_caps["maximum_child_ack_bytes"],
        },
        "native_closure": (
            "pin_resolved_python_executable_ABI_version_gmpy2_extension_and_ordered_"
            "libgmp_libmpfr_libmpc_paths_and_sha256_with_the_explicit_serialized_non_"
            "byte_complete_host_runtime_trust_boundary_for_builtin_frozen_carrier_"
            "stdlib_extension_dynamic_and_OS_system_library_bytes"
        ),
        "orchestration": {
            "public_invocation": (
                "one_role10_transaction_orchestrator_v3_using_the_pinned_verifier_entrypoint"
            ),
            "producer_child": (
                "the_orchestrator_loads_and_authenticates_runtime_closure_then_launches_"
                "the_exact_pinned_producer_entrypoint_into_an_owned_hidden_staged_"
                "artifact_directory_precreated_by_the_orchestrator_never_the_public_"
                "destination_and_requires_the_exact_producer_ACK"
            ),
            "semantic_children": (
                "after_authenticated_producer_success_the_same_orchestrator_launches_"
                "two_clean_semantic_children_concurrently_against_the_same_staged_"
                "artifact_and_requires_exact_ACKs_and_byte_identical_receipts"
            ),
            "transaction_owner": (
                "the_same_orchestrator_acquires_and_holds_the_parent_global_lock_"
                "writes_and_recovers_the_journal_stages_both_receipts_and_commits_or_"
                "rolls_back_all_three_public_outputs_without_cross_process_handoff"
            ),
        },
        "run_observation_contract": {
            "cardinality": 3,
            "order": [
                "producer_child",
                "semantic_child_0",
                "semantic_child_1",
            ],
            "schema": "/wire_schema_contract/objects/run_observation",
            "storage": (
                "outer_receipt_records_one_producer_and_two_semantic_child_ordered_"
                "parent_observations_not_child_controlled_semantic_fields"
            ),
            "joins": [
                "run_ordinal_0_ack_sha256_equals_SHA256_of_the_exact_authenticated_"
                "producer_child_ACK_and_its_Darwin_observation_matches_that_ACK",
                "run_ordinals_1_and_2_ack_sha256_each_equal_SHA256_of_the_corresponding_"
                "exact_authenticated_semantic_child_ACK_and_each_Darwin_observation_"
                "matches_that_ACK",
                "all_three_stderr_sha256_values_equal_SHA256_of_empty_bytes_and_all_"
                "three_returncodes_are_integer_zero",
            ],
        },
        "signal_sequence": [
            "killpg_SIGTERM",
            "wait_reap_until_term_grace_or_exit",
            "if_alive_killpg_SIGKILL",
            "wait_reap_until_kill_grace",
            "verify_no_live_owned_pid_or_pgid",
            "owned_temporary_cleanup",
        ],
    }


def publication_contract() -> dict[str, Any]:
    return {
        "owner": (
            "the_single_public_role10_transaction_orchestrator_v3_process_owns_the_"
            "parent_global_lock_journal_hidden_staged_artifact_two_temporary_semantic_"
            "receipts_and_all_three_public_installs_from_preflight_through_commit_or_"
            "rollback_no_cross_process_lock_or_journal_handoff"
        ),
        "all_three_preflight": (
            "after_parent_global_lock_acquisition_and_mandatory_parent_global_journal_"
            "recovery_artifact_semantic_receipt_outer_receipt_and_transaction_journal_"
            "are_absent_and_parent_identity_is_path_rebound_before_first_install"
        ),
        "atomicity": "same_filesystem_atomic_no_replace_primitive_required_otherwise_HOLD",
        "component_reads": "component_anchored_no_symlink_regular_single_link_bounded_reads_only",
        "destination_policy": "existing_destination_is_terminal_failure_never_replaced",
        "install_order": [
            "artifact_directory",
            "canonical_semantic_receipt_sibling",
            "outer_validation_receipt_sibling",
        ],
        "modes": {
            "published_directories": "0555",
            "published_files": "0444",
            "staging_directories": "0700",
            "staging_files": "0600",
            "transaction_journal": "0600",
        },
        "output_parent": {
            "creation_by_role10": "forbidden",
            "group_or_world_writable": "forbidden",
            "mode": "0700",
            "must_preexist": "required",
            "owner": "effective_uid",
            "role10_slot_join": (
                "the_artifact_semantic_receipt_and_outer_receipt_targets_are_distinct_"
                "siblings_below_this_exact_same_authenticated_parent"
            ),
            "path_rebind_identity_checks": [
                "before_preflight",
                "before_each_install",
                "after_each_install_and_parent_fsync",
                "before_caller_commit_ACK",
                "after_rollback",
            ],
            "same_filesystem_for_all_three_outputs": "required",
        },
        "digest_contracts": {
            "staged_identity_ledger_sha256": {
                "domain": "encounter-role10-staged-identity-ledger-v1",
                "object_schema": ("/wire_schema_contract/objects/staged_identity_ledger_preimage"),
                "preimage": (
                    "domain_ascii+NUL+canonical_ASCII_bytes_of_exact_object_two_"
                    "auxiliary_semantic_receipts_owned_stage_root_and_three_staged_"
                    "outputs_after_all_six_identities_are_nonnull_with_no_length_prefix"
                ),
            },
            "write_ahead_journal_sha256": {
                "preimage": (
                    "the_exact_raw_canonical_ASCII_complete_journal_bytes_including_one_"
                    "trailing_LF_reopened_after_the_ABOUT_TO_INSTALL_OUTER_RECEIPT_"
                    "snapshot_is_durable"
                ),
                "rule": (
                    "direct_SHA256_with_no_domain_or_length_prefix_the_hashed_ABOUT_TO_"
                    "INSTALL_OUTER_RECEIPT_snapshot_has_null_prepublication_journal_"
                    "snapshot_sha256_and_no_current_snapshot_self_hash_later_states_may_"
                    "carry_only_that_prior_snapshot_digest"
                ),
            },
        },
        "recovery_journal": {
            "exact_keys": [
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
            ],
            "field_schemas": {
                "auxiliary_semantic_receipts": {
                    "cardinality": 2,
                    "item_schema": (
                        "/wire_schema_contract/objects/journal_auxiliary_semantic_receipt"
                    ),
                    "order": ["semantic_child_0", "semantic_child_1"],
                },
                "journal_identity": "/wire_schema_contract/objects/dev_ino_pair",
                "owned_stage_root": ("/wire_schema_contract/objects/journal_owned_stage_root"),
                "output_parent_identity": ("/wire_schema_contract/objects/dev_ino_pair"),
                "prepublication_journal_snapshot_sha256": (
                    "JSON_null_through_the_durable_ABOUT_TO_INSTALL_OUTER_RECEIPT_"
                    "snapshot_then_in_OUTER_RECEIPT_INSTALLED_and_COMMITTED_lowercase_"
                    "sha256_equal_the_raw_bytes_of_that_prior_snapshot_and_equal_the_"
                    "outer_receipt_write_ahead_journal_sha256"
                ),
                "request_sha256": (
                    "lowercase_sha256_equal_the_opened_authenticated_role10_request_bytes"
                ),
                "staged_identity_ledger_sha256": (
                    "JSON_null_until_all_six_stage_and_auxiliary_identities_are_recorded_"
                    "then_lowercase_sha256_under_publication_contract_digest_contracts"
                ),
                "staged_outputs": {
                    "cardinality": 3,
                    "item_schema": ("/wire_schema_contract/objects/journal_staged_output"),
                    "order": [
                        "role10_artifact_directory",
                        "role10_semantic_receipt",
                        "role10_outer_validation_receipt",
                    ],
                },
                "state": (
                    "exact_literal_from_recovery_journal_state_order_with_no_skips_or_"
                    "backward_transition"
                ),
                "target_slots": {
                    "cardinality": 3,
                    "item_schema": ("/wire_schema_contract/objects/journal_target_slot"),
                    "order": [
                        "role10_artifact_directory",
                        "role10_semantic_receipt",
                        "role10_outer_validation_receipt",
                    ],
                },
            },
            "identity": (
                "literal_.encounter-role10-killing-geometry-transaction-v1.json_"
                "single_parent_global_leaf_below_the_authenticated_output_parent_"
                "independent_of_request_or_target_names_opened_NOFOLLOW_mode_0600_"
                "nlink_1_and_guarded_by_its_own_dev_ino_the_body_records_request_"
                "sha256_and_exact_target_slots"
            ),
            "identity_location_join": (
                "before_each_output_install_its_recorded_dev_ino_is_present_only_at_"
                "the_declared_stage_leaf_after_the_corresponding_INSTALLED_state_the_"
                "same_dev_ino_is_present_only_at_the_declared_target_leaf_and_the_stage_"
                "leaf_is_absent_each_auxiliary_receipt_is_present_only_at_its_declared_"
                "relative_path_until_its_ABOUT_TO_REMOVE_transition_and_absent_after_"
                "its_REMOVED_state_ANY_duplicate_missing_or_rebound_location_outside_"
                "the_exact_about_to_transition_rules_is_HOLD"
            ),
            "intent_before_stage": (
                "after_lock_recovery_and_global_freshness_preflight_choose_the_hidden_"
                "stage_root_three_output_stage_leaf_names_and_two_auxiliary_semantic_"
                "receipt_relative_paths_create_and_fsync_the_canonical_INTENT_DURABLE_"
                "journal_by_atomic_no_replace_and_fsync_parent_before_creating_any_"
                "stage_root_staged_output_or_auxiliary_receipt"
            ),
            "record": (
                "the_INTENT_DURABLE_snapshot_has_null_stage_and_auxiliary_receipt_"
                "identities_null_ledger_digest_and_null_prepublication_journal_snapshot_"
                "digest_but_exact_owned_stage_root_stage_leaf_auxiliary_relative_path_"
                "target_leaf_node_type_and_target_slot_names_each_creation_is_preceded_"
                "by_a_durable_ABOUT_TO_CREATE_state_and_followed_by_a_durable_identity_"
                "record_state_after_all_six_identities_are_recorded_compute_and_freeze_"
                "the_ledger_digest"
            ),
            "state_value_matrix": {
                "ABOUT_TO_CREATE_ARTIFACT_DIRECTORY": (
                    "owned_stage_root.identity_nonnull_all_three_staged_identities_null_"
                    "both_auxiliary_identities_null_ledger_null_prepublication_journal_"
                    "snapshot_null"
                ),
                "ABOUT_TO_CREATE_CHILD_0_RECEIPT": (
                    "all_four_stage_identities_nonnull_both_auxiliary_identities_null_"
                    "ledger_null_prepublication_journal_snapshot_null"
                ),
                "ABOUT_TO_CREATE_CHILD_1_RECEIPT": (
                    "all_four_stage_identities_and_child_0_identity_nonnull_child_1_"
                    "identity_null_ledger_null_prepublication_journal_snapshot_null"
                ),
                "ABOUT_TO_CREATE_OUTER_RECEIPT": (
                    "owned_stage_root_artifact_and_semantic_identities_nonnull_outer_"
                    "identity_and_both_auxiliary_identities_null_ledger_null_"
                    "prepublication_journal_snapshot_null"
                ),
                "ABOUT_TO_CREATE_SEMANTIC_RECEIPT": (
                    "owned_stage_root_and_artifact_identities_nonnull_semantic_and_outer_"
                    "identities_and_both_auxiliary_identities_null_ledger_null_"
                    "prepublication_journal_snapshot_null"
                ),
                "ABOUT_TO_CREATE_STAGE_ROOT": (
                    "owned_stage_root.identity_and_all_three_staged_identities_null_"
                    "both_auxiliary_identities_null_ledger_null_prepublication_journal_"
                    "snapshot_null"
                ),
                "ABOUT_TO_REMOVE_CHILD_0_RECEIPT": (
                    "all_six_recorded_identities_nonnull_ledger_frozen_child_1_path_"
                    "absent_child_0_path_may_contain_only_its_recorded_identity_or_be_"
                    "absent_after_a_crash_prepublication_journal_snapshot_null"
                ),
                "ABOUT_TO_REMOVE_CHILD_1_RECEIPT": (
                    "all_six_recorded_identities_nonnull_ledger_frozen_child_0_path_"
                    "contains_its_recorded_identity_child_1_path_may_contain_only_its_"
                    "recorded_identity_or_be_absent_after_a_crash_prepublication_"
                    "journal_snapshot_null"
                ),
                "ARTIFACT_DIRECTORY_IDENTITY_RECORDED": (
                    "owned_stage_root_and_artifact_identities_nonnull_semantic_and_outer_"
                    "identities_and_both_auxiliary_identities_null_ledger_null_"
                    "prepublication_journal_snapshot_null"
                ),
                "CHILD_0_RECEIPT_IDENTITY_RECORDED": (
                    "all_four_stage_identities_and_child_0_identity_nonnull_child_1_"
                    "identity_null_ledger_null_prepublication_journal_snapshot_null"
                ),
                "CHILD_0_RECEIPT_REMOVED_through_ABOUT_TO_INSTALL_OUTER_RECEIPT": (
                    "all_six_recorded_identities_nonnull_ledger_equals_the_recomputed_"
                    "frozen_digest_both_auxiliary_receipt_paths_absent_prepublication_"
                    "journal_snapshot_null"
                ),
                "CHILD_1_RECEIPT_IDENTITY_RECORDED": (
                    "all_six_identities_nonnull_ledger_null_prepublication_journal_snapshot_null"
                ),
                "CHILD_1_RECEIPT_REMOVED": (
                    "all_six_recorded_identities_nonnull_ledger_frozen_child_1_path_"
                    "absent_child_0_path_contains_its_recorded_identity_prepublication_"
                    "journal_snapshot_null"
                ),
                "INTENT_DURABLE": (
                    "owned_stage_root.identity_and_all_three_staged_identities_null_"
                    "both_auxiliary_identities_null_ledger_null_prepublication_journal_"
                    "snapshot_null"
                ),
                "OUTER_RECEIPT_IDENTITY_RECORDED": (
                    "all_four_stage_identities_nonnull_both_auxiliary_identities_null_"
                    "ledger_null_prepublication_journal_snapshot_null"
                ),
                "OUTER_RECEIPT_INSTALLED_and_COMMITTED": (
                    "all_six_recorded_identities_nonnull_ledger_equals_the_recomputed_"
                    "frozen_digest_both_auxiliary_paths_absent_prepublication_journal_"
                    "snapshot_equals_the_prior_durable_ABOUT_TO_INSTALL_OUTER_RECEIPT_"
                    "raw_bytes_SHA256"
                ),
                "SEMANTIC_RECEIPT_IDENTITY_RECORDED": (
                    "owned_stage_root_artifact_and_semantic_identities_nonnull_outer_"
                    "identity_and_both_auxiliary_identities_null_ledger_null_"
                    "prepublication_journal_snapshot_null"
                ),
                "STAGE_ROOT_IDENTITY_RECORDED": (
                    "owned_stage_root.identity_nonnull_all_three_staged_identities_null_"
                    "both_auxiliary_identities_null_ledger_null_prepublication_journal_"
                    "snapshot_null"
                ),
                "STAGING_IDENTITIES_COMPLETE_through_SEMANTIC_CHILDREN_MATCHED": (
                    "all_six_identities_nonnull_ledger_equals_the_recomputed_frozen_"
                    "digest_both_auxiliary_receipt_paths_contain_only_their_recorded_"
                    "identities_prepublication_journal_snapshot_null"
                ),
            },
            "state_semantics": {
                "CHILD_1_RECEIPT_REMOVED_then_CHILD_0_RECEIPT_REMOVED": (
                    "each_owned_auxiliary_receipt_is_unlinked_in_reverse_run_order_only_"
                    "after_a_durable_ABOUT_TO_REMOVE_state_and_exact_dev_ino_recheck_"
                    "each_REMOVED_state_is_durable_before_the_next_removal"
                ),
                "PRODUCER_COMPLETED": (
                    "the_exact_producer_ACK_and_composite_staged_artifact_binding_are_"
                    "authenticated_the_tree_is_stable_and_the_artifact_identity_is_"
                    "unchanged"
                ),
                "SEMANTIC_CHILDREN_MATCHED": (
                    "both_concurrent_child_ACKs_are_authenticated_their_receipt_bytes_"
                    "are_identical_and_those_canonical_bytes_are_written_fsynced_and_"
                    "reauthenticated_in_the_precreated_canonical_semantic_staged_inode"
                ),
                "PREPARED_FOR_INSTALL": (
                    "all_children_are_reaped_auxiliary_temporary_paths_are_cleaned_and_"
                    "the_artifact_and_canonical_semantic_staged_outputs_are_immutable_"
                    "stable_and_reauthenticated_the_outer_staged_inode_remains_owned_"
                    "and_empty_until_the_prepublication_journal_snapshot_is_durable"
                ),
            },
            "state_order": [
                "INTENT_DURABLE",
                "ABOUT_TO_CREATE_STAGE_ROOT",
                "STAGE_ROOT_IDENTITY_RECORDED",
                "ABOUT_TO_CREATE_ARTIFACT_DIRECTORY",
                "ARTIFACT_DIRECTORY_IDENTITY_RECORDED",
                "ABOUT_TO_CREATE_SEMANTIC_RECEIPT",
                "SEMANTIC_RECEIPT_IDENTITY_RECORDED",
                "ABOUT_TO_CREATE_OUTER_RECEIPT",
                "OUTER_RECEIPT_IDENTITY_RECORDED",
                "ABOUT_TO_CREATE_CHILD_0_RECEIPT",
                "CHILD_0_RECEIPT_IDENTITY_RECORDED",
                "ABOUT_TO_CREATE_CHILD_1_RECEIPT",
                "CHILD_1_RECEIPT_IDENTITY_RECORDED",
                "STAGING_IDENTITIES_COMPLETE",
                "PRODUCER_COMPLETED",
                "SEMANTIC_CHILDREN_MATCHED",
                "ABOUT_TO_REMOVE_CHILD_1_RECEIPT",
                "CHILD_1_RECEIPT_REMOVED",
                "ABOUT_TO_REMOVE_CHILD_0_RECEIPT",
                "CHILD_0_RECEIPT_REMOVED",
                "PREPARED_FOR_INSTALL",
                "ABOUT_TO_INSTALL_ARTIFACT",
                "ARTIFACT_INSTALLED",
                "ABOUT_TO_INSTALL_SEMANTIC_RECEIPT",
                "SEMANTIC_RECEIPT_INSTALLED",
                "ABOUT_TO_INSTALL_OUTER_RECEIPT",
                "OUTER_RECEIPT_INSTALLED",
                "COMMITTED",
            ],
            "update": (
                "write_next_state_to_owned_0600_stage_fsync_atomic_replace_only_the_"
                "owned_journal_inode_with_the_new_journal_identity_in_its_body_then_"
                "fsync_parent_and_reopen_reauthenticate_exact_canonical_bytes"
            ),
            "write_outer_after_journal_snapshot": (
                "after_the_semantic_receipt_is_installed_durably_write_and_fsync_the_"
                "exact_ABOUT_TO_INSTALL_OUTER_RECEIPT_journal_snapshot_reopen_and_hash_"
                "those_raw_bytes_then_serialize_the_outer_receipt_into_the_precreated_"
                "owned_outer_staged_inode_with_that_digest_recheck_and_fsync_the_inode_"
                "and_only_then_attempt_the_no_replace_outer_install_the_following_"
                "OUTER_RECEIPT_INSTALLED_and_COMMITTED_journal_states_preserve_that_"
                "prior_snapshot_digest_for_recovery_comparison"
            ),
        },
        "rollback": {
            "events": "error_timeout_BaseException_cancellation_or_recovery_from_noncommitted_journal",
            "foreign_policy": "never_remove_or_replace_an_object_whose_dev_ino_is_not_owned",
            "parent_fsync": "after_every_owned_unlink_or_directory_removal",
            "scope": (
                "reverse_public_install_order_then_reverse_auxiliary_run_order_only_"
                "objects_matching_the_recorded_owned_identity_ledger"
            ),
        },
        "single_writer_lock": {
            "acquisition_order": (
                "open_or_atomically_create_then_fsync_the_persistent_lock_file_acquire_"
                "nonblocking_flock_LOCK_EX_before_reading_any_journal_or_preflighting_"
                "destinations"
            ),
            "busy_policy": "HOLD_or_bounded_wait_never_recover_or_rollback_while_lock_is_held",
            "identity": (
                "literal_.encounter-role10-killing-geometry-single-writer-v1.lock_"
                "persistent_leaf_below_the_authenticated_output_parent_independent_of_"
                "request_or_target_names_owner_effective_uid_mode_0600_nlink_1_"
                "NOFOLLOW_dev_ino_guarded"
            ),
            "lifecycle": (
                "hold_the_same_open_locked_inode_through_recovery_install_commit_or_"
                "rollback_then_flock_UNLOCK_and_close_persistent_leaf_is_not_unlinked"
            ),
            "serialization_scope": (
                "all_role10_transactions_whose_three_target_leaves_share_the_same_"
                "authenticated_output_parent_are_serialized_even_when_their_requests_"
                "or_target_names_differ"
            ),
            "recovery_precondition": (
                "journal_recovery_is_permitted_only_after_exclusive_lock_acquisition_"
                "which_proves_no_live_cooperating_transaction_owns_the_request_scope"
            ),
        },
        "staging_capability": {
            "creation_owner": (
                "the_orchestrator_precreates_the_mode_0700_owned_stage_root_and_artifact_"
                "directory_the_mode_0600_canonical_semantic_and_outer_output_placeholder_"
                "files_and_two_distinct_mode_0600_auxiliary_semantic_child_receipt_"
                "files_in_exact_journal_order_before_any_child_launch"
            ),
            "descriptor_boundary": (
                "because_pass_fds_is_empty_each_child_resolves_the_predeclared_stage_"
                "path_component_by_component_NOFOLLOW_requires_the_exact_recorded_dev_"
                "ino_mode_type_and_parent_identity_and_the_orchestrator_rechecks_the_"
                "same_identity_before_and_after_every_child"
            ),
            "outer_receipt_write": (
                "the_orchestrator_writes_truncates_fsyncs_and_reauthenticates_only_the_"
                "precreated_owned_outer_receipt_inode_without_path_replacement"
            ),
            "producer_write": (
                "the_producer_accepts_only_--staged-output_to_the_precreated_owned_"
                "artifact_directory_must_not_replace_that_directory_and_cannot_resolve_"
                "or_publish_any_public_output_slot"
            ),
            "semantic_child_write": (
                "each_semantic_child_writes_truncates_fsyncs_and_reauthenticates_only_"
                "its_distinct_run_ordinal_specific_precreated_journaled_auxiliary_"
                "semantic_receipt_inode_without_path_replacement_after_byte_identity_"
                "the_orchestrator_copies_the_canonical_bytes_into_the_separate_"
                "precreated_canonical_semantic_output_inode_fsyncs_reauthenticates_and_"
                "journal_removes_both_auxiliary_inodes_in_reverse_order"
            ),
        },
        "successful_commit": (
            "after_outer_install_mark_COMMITTED_durable_reopen_and_reauthenticate_all_"
            "three_outputs_remove_only_the_owned_journal_fsync_parent_rebind_parent_"
            "identity_before_caller_commit_ACK_then_emit_the_exact_commit_ACK_no_"
            "fallible_success_gate_occurs_after_that_ACK"
        ),
        "transaction_evidence_boundary": {
            "caller_commit_ack": (
                "the_exact_process_contract_public_transaction_commit_ACK_emitted_only_"
                "after_COMMITTED_is_durable_all_three_outputs_are_reauthenticated_the_"
                "owned_journal_is_removed_parent_is_fsynced_and_the_final_parent_"
                "identity_check_passes"
            ),
            "outer_receipt_may_record": (
                "preflight_parent_identity_atomic_primitive_the_six_identity_staged_"
                "ledger_digest_and_write_ahead_journal_digest_observed_before_outer_"
                "install"
            ),
            "outer_receipt_must_not_record": [
                "outer_receipt_installed",
                "transaction_committed",
                "journal_removed",
            ],
        },
        "unexpected_process_death": (
            "the_next_transaction_after_exclusive_parent_global_lock_acquisition_always_"
            "checks_the_parent_global_journal_before_any_preflight_for_an_ABOUT_TO_"
            "CREATE_state_if_the_declared_object_is_absent_recovery_may_rollback_only_"
            "previously_recorded_owned_identities_if_the_declared_object_exists_while_"
            "its_identity_is_null_the_state_is_ambiguous_HOLD_and_every_residue_is_"
            "preserved_for_any_identity_recorded_or_install_state_recovery_searches_"
            "each_output_stage_auxiliary_receipt_and_target_by_path_and_dev_ino_rolls_"
            "back_only_exact_matches_in_reverse_public_slot_and_auxiliary_run_order_"
            "fsyncs_parent_and_removes_only_the_owned_journal_for_"
            "COMMITTED_recovery_reauthenticates_all_three_targets_then_removes_only_"
            "the_owned_journal_any_unrecorded_auxiliary_stage_residue_or_any_missing_"
            "object_outside_the_exact_state_value_matrix_and_identity_location_join_"
            "ABOUT_TO_REMOVE_absence_allowances_or_any_mismatch_foreign_inode_invalid_"
            "transition_or_digest_disagreement_is_HOLD_and_is_preserved"
        ),
    }


def verification_contract(base: dict[str, Any]) -> dict[str, Any]:
    verification = copy.deepcopy(base)
    verification["contact_coverage"] = {
        "all_cells_independently_classified": 233139,
        "all_full_cells_exactly_serialized": 4142,
        "all_partial_cells_at_384": 1304,
        "all_zero_cells_exactly_serialized": 227693,
        "first_partial_cell_per_row_at_512": 12,
        "negative_zero_allowed": False,
        "oracle_relative_width_gate_per_partial_cell": (
            "1/1532495540865888858358347027150309183618739122183602176"
        ),
        "published_contains_primary_for_every_partial": 1304,
        "published_contains_sentinel_for_first_partial_per_row": 12,
        "ratio_gate": ("oracle_cell_width_divided_by_nonzero_producer_cell_width_at_most_1/8"),
        "ratio_scope": "partial_nonzero_producer_widths_only",
    }
    verification["profile_coverage"] = {
        "aggregate_relative_width_gate": "1/10000000000",
        "all_profile_aggregates_at_paired_384_512": 48,
        "all_profile_cells_at_paired_384_512": 6852,
        "all_profile_cells_independently_support_classified": 6852,
        "cell_mass_width_gate": "1/1099511627776",
        "negative_zero_allowed": False,
        "outside_support_serialization": "bit_exact_[positive_zero,positive_zero]",
        "ratio_gate": (
            "oracle_cell_mass_width_divided_by_nonzero_producer_cell_mass_width_at_most_1/8"
        ),
        "ratio_scope": (
            "support_nonzero_profile_cell_mass_widths_only_outside_support_exact_zero_"
            "cells_are_independently_classified"
        ),
    }
    verification["classification_evidence"] = classification_contract()
    return verification


def build_model() -> dict[str, Any]:
    v1, _ = read_v1()
    model = copy.deepcopy(v1)
    model["schema"] = SCHEMA
    model["status"] = STATUS
    model["claim_boundary"] = precommit_claims()
    model["lineage"] = {
        "reused_sections": [
            "authority_bindings",
            "authority_model",
            "method_contract",
            "resource_caps",
            "artifact_contract.rows_except_row_schema",
            "artifact_contract.directory_paths",
            "artifact_contract.file_paths",
            "artifact_contract.path_templates",
            "artifact_contract.top_file_inventory",
            "artifact_contract.totals",
        ],
        "transformations": {
            "artifact_contract.rows[*].row_schema": {
                "from": "encounter_c1_n0_killing_factor_geometry_row_v1",
                "to": ROW_SCHEMA,
            },
            "artifact_contract.schema_key_contracts": "replaced_by_recursively_closed_v2_contract",
            "artifact_contract.schemas": "replaced_by_source_v4_row_v2_raw_v2",
        },
        "superseded_reason": [
            "post_run_claim_contradiction",
            "singleton_classification_undercoverage",
            "wire_schema_underclosure",
            "semantic_validator_undercoverage",
            "three_output_transaction_underclosure",
            "ten_slot_plan_v2_isolation_absent",
            "process_isolation_prose_only",
        ],
        "v1": {
            "path": V1_RELATIVE.as_posix(),
            "schema": V1_SCHEMA,
            "sha256": V1_SHA256,
            "status": "HISTORICAL_RESULT_BLIND_DRAFT_SUPERSEDED_BEFORE_EXTERNAL_COMMITMENT",
        },
    }

    artifact = model["artifact_contract"]
    artifact["schemas"] = {
        "raw_interval_file": RAW_SCHEMA,
        "row": ROW_SCHEMA,
        "source": SOURCE_SCHEMA,
    }
    for row in artifact["rows"]:
        row["row_schema"] = ROW_SCHEMA
    artifact["schema_key_contracts"] = {
        "envelope_exact_keys": ["payload", "payload_digest", "schema", "status"],
        "outer_receipt_payload_exact_keys": wire_schema_contract()["envelopes"]["outer_receipt"][
            "payload_exact_keys"
        ],
        "raw_manifest_exact_keys": wire_schema_contract()["objects"]["raw_manifest"]["exact_keys"],
        "row_payload_exact_keys": wire_schema_contract()["envelopes"]["row"]["payload_exact_keys"],
        "semantic_receipt_payload_exact_keys": wire_schema_contract()["envelopes"][
            "semantic_receipt"
        ]["payload_exact_keys"],
        "source_payload_exact_keys": wire_schema_contract()["envelopes"]["source"][
            "payload_exact_keys"
        ],
    }
    artifact["stored_precision_policy"] = {
        "producer_saved_interval_precision_bits": 192,
        "raw_endpoint_storage": "outward_binary64_>dd",
        "verifier_oracle_values": "not_materialized_in_the_source_package",
    }

    numerical = model["numerical_semantics"]
    numerical["contact"]["derived_expected_full_cell_count"] = 4142
    numerical["contact"]["derived_expected_partial_cell_count"] = 1304
    numerical["contact"]["derived_expected_total_cell_count"] = 233139
    numerical["contact"]["derived_expected_zero_cell_count"] = 227693
    numerical["contact"]["exact_serialization"] = {
        "full": "bit_exact_[1.0,1.0]",
        "negative_zero": "forbidden",
        "zero": "bit_exact_[positive_zero,positive_zero]",
    }
    numerical["profile"]["outside_support_serialization"] = {
        "negative_zero": "forbidden",
        "value": "bit_exact_[positive_zero,positive_zero]",
    }

    model["wire_schema_contract"] = wire_schema_contract()
    model["classification_contract"] = classification_contract()
    model["replay_plan_contract"] = replay_plan_contract()
    model["process_contract"] = process_contract(model["resource_caps"])
    model["publication_contract"] = publication_contract()
    model["verification_contract"] = verification_contract(model["verification_contract"])
    model["invocation_contract"] = {
        "process_contract_binding": {
            "json_pointer": "/process_contract",
            "model_schema": SCHEMA,
        },
        "public_plan_invocations": {
            "role10": ["transaction_orchestrator"],
            "role8": ["producer", "verifier"],
            "role9": ["producer", "verifier"],
        },
        "replay_plan_runtime_closure_binding": RUNTIME_SCHEMA,
        "role10_request_schema": ROLE10_REQUEST_SCHEMA,
        "role10_internal_children": [
            "pinned_producer_to_owned_hidden_staged_artifact",
            "semantic_child_0_against_the_same_staged_artifact",
            "semantic_child_1_against_the_same_staged_artifact",
        ],
        "runtime_closure_rule": (
            "all_six_role_entrypoints_the_global_runner_v2_every_report_local_and_file_"
            "runtime_prefix_Python_module_origin_the_pinned_Python_executable_and_the_"
            "declared_gmpy2_GMP_MPFR_MPC_native_bytes_are_frozen_in_runtime_closure_v1_"
            "before_external_commitment_builtin_frozen_carrier_non_report_dynamic_and_"
            "OS_bytes_remain_only_inside_the_explicit_non_byte_complete_host_runtime_"
            "trust_boundary"
        ),
        "shared_module_boundary": {
            "allowed_shared_surface": (
                "zero_or_one_globally_identical_separately_pinned_semantics_free_"
                "protocol_module_only"
            ),
            "numerical_source_sets": "producer_and_verifier_disjoint",
            "shared_unpinned_report_local_or_numerical_module": "forbidden",
            "scope": (
                "report_local_protocol_and_numerical_source_modules_only_the_explicit_"
                "host_runtime_trust_boundary_is_excluded"
            ),
        },
    }
    model["receipt_contract"] = {
        "child_observation_count": 3,
        "child_observation_order": [
            "producer_child",
            "semantic_child_0",
            "semantic_child_1",
        ],
        "creator": (
            "the_single_public_role10_transaction_orchestrator_stages_the_canonical_"
            "semantic_and_outer_receipts_before_the_same_three_output_commit"
        ),
        "child_semantic_body_rule": (
            "two_clean_isolated_children_create_byte_identical_canonical_v2_"
            "semantic_receipt_payloads_including_classification_ledgers"
        ),
        "outer_receipt": model["wire_schema_contract"]["envelopes"]["outer_receipt"],
        "retention_rule": (
            "outer_binds_one_canonical_semantic_receipt_and_three_run_observations_"
            "transaction_tree_stability_and_cleanup_evidence"
        ),
        "semantic_receipt": model["wire_schema_contract"]["envelopes"]["semantic_receipt"],
        "slot_contract": {
            "global_plan_v2_slot_count": 10,
            "role10_output_count": 3,
            "role10_slots_including_request": 4,
            "roles8_9_slots_each": 3,
            "slot_ids": [
                slot["slot_id"] for slot in model["replay_plan_contract"]["slot_templates"]
            ],
        },
        "temporary_child_receipts": {
            "cardinality": 2,
            "journal_schema": ("/wire_schema_contract/objects/journal_auxiliary_semantic_receipt"),
            "paths_in_run_order": [
                ".semantic-child-0-receipt.json",
                ".semantic-child-1-receipt.json",
            ],
            "retention": (
                "both_are_removed_in_reverse_order_only_by_recorded_owned_dev_ino_after_"
                "the_orchestrator_rechecks_byte_identity_and_fsyncs_the_same_canonical_"
                "body_into_the_distinct_canonical_semantic_output_staged_inode"
            ),
        },
    }
    model["forbidden_surface"] = {
        **model["forbidden_surface"],
        "classification_digest_values_in_precommit_model": "forbidden",
        "future_output_tree_or_relation_digest_values_in_precommit_model": "forbidden",
        "post_run_lifecycle_facts_must_not_be_copied_from_precommit_claims": True,
        "unknown_future_output_or_result_hash_pins": "forbidden",
    }
    return model


def immutable_payload(path: Path) -> bytes:
    descriptor = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        value = os.fstat(descriptor)
        if (
            not stat.S_ISREG(value.st_mode)
            or value.st_nlink != 1
            or stat.S_IMODE(value.st_mode) != 0o444
        ):
            fail("installed v2 model is not an immutable single-link regular file")
        raw = b""
        while True:
            chunk = os.read(descriptor, 1 << 20)
            if not chunk:
                break
            raw += chunk
        return raw
    finally:
        os.close(descriptor)


def publish(path: Path, raw: bytes) -> None:
    try:
        load_v1_publisher()(path.absolute(), raw)
    except OperationModelV2BuildError:
        raise
    except BaseException as error:
        raise OperationModelV2BuildError(
            f"anchored no-replace publication failed: {error}"
        ) from error


def check(path: Path) -> str:
    expected = canonical_bytes(build_model())
    observed = immutable_payload(path)
    if observed != expected:
        fail("v2 operation-model byte drift")
    return sha256(observed)


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_args(argv)
    try:
        if arguments.check:
            digest = check(arguments.output)
        else:
            raw = canonical_bytes(build_model())
            publish(arguments.output, raw)
            digest = sha256(raw)
    except (OSError, OperationModelV2BuildError) as error:
        print(f"HOLD_ROLE10_OPERATION_MODEL_V2: {error}", file=os.sys.stderr)
        return 2
    print(f"PASS_ROLE10_OPERATION_MODEL_V2 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
