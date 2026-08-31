"""Build committed-run candidate-native stationary physical integrals.

The thin canonical request reopens a result-blind replay plan, a separate
candidate bundle, and a structurally authenticated predecessor commitment.
The plan binds every scientific authority, exact partition, implementation,
runtime, output slot, and validation-receipt slot before roles 8--10 run.  No
expected output value or result digest is accepted anywhere in that chain.

This module deliberately imports no legacy scientific implementation.  It
computes factorized physical cell integrals ``M_x^pi`` and the finite-box mass
``M_L`` with directed MPFR arithmetic at request-selected primary and sentinel
precisions.  Tensor-sized arrays are not materialized.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import secrets
import stat
import sys
import threading
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final, Sequence

import gmpy2

_STAGE_OPEN: Final = os.open
_STAGE_FSTAT: Final = os.fstat

REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_stationary_integrals_request_v3"
OUTPUT_SCHEMA: Final = "encounter_c1_n0_stationary_physical_integral_source_v2"
RECEIPT_SCHEMA: Final = "encounter_c1_n0_stationary_physical_integral_validation_receipt_v1"
PLAN_SCHEMA: Final = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v1"
BUNDLE_SCHEMA: Final = "encounter_continuum_c1_n0_precommit_candidate_bundle_v1"
COMMITMENT_SCHEMA: Final = "encounter_external_predecessor_commitment_v1"
ROLE_ID: Final = 9
ROLE_NAME: Final = "role9_stationary_physical_integral"
ROLE8_NAME: Final = "role8_raw_axis_formula_primitive"
ROLE10_NAME: Final = "role10_killing_factor_geometry"
ROLE8_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_raw_axis_formula_request_v3"
ROLE10_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_killing_factor_geometry_request_v3"
ROLE8_OUTPUT_SCHEMA: Final = "encounter_c1_n0_raw_axis_formula_primitive_source_v2"
ROLE10_OUTPUT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_source_v2"
ROLE8_RECEIPT_SCHEMA: Final = "encounter_c1_n0_raw_axis_formula_primitive_validation_receipt_v1"
ROLE10_RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_validation_receipt_v1"
ROLE8_RUNTIME_CLOSURE_SCHEMA: Final = (
    "encounter_continuum_c1_n0_role8_implementation_runtime_closure_v1"
)
ROLE8_RUNTIME_CLOSURE_STATUS: Final = (
    "FROZEN_SOURCE_SEPARATED_ROLE8_IMPLEMENTATION_RUNTIME_CLOSURE_NO_EXECUTION_RESULT"
)
PLAN_STATUS: Final = "RESULT_BLIND_PRECOMMIT_REPLAY_PLAN_NO_EXECUTION_RESULTS"
BUNDLE_STATUS: Final = "RESULT_BLIND_PRECOMMIT_CANDIDATE_BUNDLE_NO_EXECUTION_RESULTS"
REQUEST_STATUS: Final = (
    "EXTERNAL_PREDECESSOR_COMMITMENT_BOUND_RESULT_BLIND_REQUEST_NO_EXECUTION_RESULT"
)
COMMITMENT_STATUS: Final = (
    "EXTERNAL_PREDECESSOR_COMMITMENT_STRUCTURALLY_BOUND_AUTHENTICITY_NOT_LOCALLY_PROVEN"
)
_ALLOWED_RESULT_METADATA_STRINGS: Final = frozenset(
    {
        PLAN_STATUS,
        BUNDLE_STATUS,
        REQUEST_STATUS,
        ROLE8_RUNTIME_CLOSURE_STATUS,
    }
)
OUTPUT_STATUS: Final = (
    "PASS_COMMITTED_REPLAY_ROLE9_STATIONARY_PHYSICAL_INTEGRALS_"
    "PRIMARY_SENTINEL_CONTAINMENT_ONLY_NOT_PRODUCTION_NOT_COMPLETE_C1_C2"
)
MEMBER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_member_spec_v4_candidate"
MEMBER_RELATIVE_PATH: Final = "artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json"
MEMBER_SHA256: Final = "b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5"
MEMBER_IDENTITY_SHA256: Final = "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
REFERENCE_SCHEMA: Final = "encounter_continuum_c1_reference_density_source_v1"
REFERENCE_RELATIVE_PATH: Final = "artifacts/data/continuum_c1_reference_density_source_v1.json"
FORMULA_SCHEMA: Final = "encounter_continuum_c1_ideal_formula_source_v1"
FORMULA_RELATIVE_PATH: Final = "artifacts/data/continuum_c1_ideal_formula_source_v1.json"
CONFIGURATION_SCHEMA: Final = "encounter_physical_configuration_family_control_free_v1"
CONFIGURATION_RELATIVE_PATH: Final = (
    "artifacts/data/physical_configuration_family_control_free_v1.json"
)
FACTORIZATION_SCHEMA: Final = "encounter_continuum_c1_factorization_source_v2_candidate"
FACTORIZATION_SHA256: Final = "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26"
FACTORIZATION_RELATIVE_PATH: Final = (
    "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"
)
PARAMETER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
PARAMETER_RELATIVE_PATH: Final = (
    "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json"
)
PARAMETER_SHA256: Final = "e403a9576abb08d3ada884cd283cce29ce8f877b0e9843cc8d5b911c8c0b0ac5"
ANTI_VACUITY_POLICY_SCHEMA: Final = "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate"
ANTI_VACUITY_POLICY_RELATIVE_PATH: Final = (
    "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json"
)
ANTI_VACUITY_POLICY_SHA256: Final = (
    "599252aa1a9fd1d65d9ff3d0faa1e21bb2609da96cca6b6fff1e61a89ebff196"
)
PARAMETER_STATUS: Final = (
    "RESULT_BLIND_CANDIDATE_NATIVE_METHOD_PARAMETERS_ONLY_NOT_EXTERNALLY_COMMITTED"
)
PARAMETER_DIGEST_DOMAIN: Final = "encounter-outward-method-parameters-v4"
PRIMARY_PARAMETER_ID: Final = "stationary_directed_mpfr_320_v2"
SENTINEL_PARAMETER_ID: Final = "stationary_directed_mpfr_640_sentinel_v2"
EXACT_PARAMETER_ID: Final = "exact_fraction_expression_dag_v2"
GENERIC_CONTAINMENT: Final = "primary_interval_contains_higher_precision_same_backend_sentinel"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"
COORDINATES: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
MAX_JSON_BYTES: Final = 8_000_000
MAX_RUNTIME_BYTES: Final = 64_000_000
MAX_INTEGER_BITS: Final = 65_536
MAX_JSON_DEPTH: Final = 64
MAX_CONFIGURATIONS: Final = 1_024
MAX_AXIS_CELLS: Final = 1_000_000
EXPECTED_CONFIGURATION_COUNT: Final = 12
EXPECTED_AXIS_COUNT: Final = 36
EXPECTED_AXIS_CELL_COUNT: Final = 5_037
EXPECTED_AXIS_EDGE_COUNT: Final = 5_013
EXPECTED_PERIODIC_SEAM_COUNT: Final = 12
EXPECTED_PROFILE_INDEX_COUNT: Final = 48
EXPECTED_TOTAL_STATES: Final = 34_787_462
MEMBER_STATUS: Final = (
    "STRUCTURAL_PARTITION_IDENTITY_V4_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
)
PRECOMMIT_CONTEXT_DOMAIN: Final = "encounter-continuum-c1-n0-shared-precommit-context-v1"
REPLAY_CONTEXT_DOMAIN: Final = "encounter-continuum-c1-n0-shared-replay-context-v1"
PRECOMMIT_PROJECTION_DOMAIN: Final = "encounter-continuum-c1-n0-role-precommit-projection-v1"
CONFIGURATION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-configuration-row-inventory-v1"
PARTITION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-partition-inventory-v1"
STREAM_DOMAIN: Final = "encounter-continuum-c1-n0-role9-stationary-axis-stream-v1"
DAG_DOMAIN: Final = "encounter-continuum-c1-n0-role9-partition-closure-dag-v1"
COMMITMENT_MESSAGE_DOMAIN: Final = "encounter-external-predecessor-commitment-message-v1"
ACCEPTED_AUTHENTICATION_CLASSES: Final = {
    "distinct_operator_authenticated_signature",
    "independently_audited_predecessor_commit_hash",
    "independent_trust_domain_receipt_hash",
}
CONFIGURATION_INITIAL_GEOMETRY_SCHEMA: Final = "encounter_physical_initial_analytic_source_v1"
FACTORIZATION_INITIAL_PARTITION_SCHEMA: Final = (
    "encounter_control_free_production_initial_stream_v1"
)
FACTORIZATION_INITIAL_PARTITION_STATUS: Final = (
    "PASS_CONTROL_FREE_12_ROW_FILE_BACKED_PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0_NOT_F1"
)
FACTORIZATION_KILLING_GEOMETRY_SCHEMA: Final = "encounter_physical_killing_geometry_source_v1"
FACTORIZATION_KILLING_GEOMETRY_STATUS: Final = (
    "FROZEN_CONTROL_FREE_CONTACT_AND_SUPPORT_BASIS_SOURCE_ONLY_"
    "NO_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)

HOLD_REQUEST = "HOLD_CANDIDATE_STATIONARY_REQUEST"
HOLD_IMMUTABLE = "HOLD_CANDIDATE_STATIONARY_IMMUTABLE_INPUT"
HOLD_INPUT = "HOLD_CANDIDATE_STATIONARY_INPUT"
HOLD_MEMBER = "HOLD_CANDIDATE_STATIONARY_MEMBER_PARTITION"
HOLD_METHOD = "HOLD_CANDIDATE_STATIONARY_METHOD"
HOLD_RUNTIME = "HOLD_CANDIDATE_STATIONARY_RUNTIME"
HOLD_NUMERICAL = "HOLD_CANDIDATE_STATIONARY_NUMERICAL"
HOLD_OUTPUT = "HOLD_CANDIDATE_STATIONARY_OUTPUT"

_REQUEST_KEYS: Final = {
    "external_predecessor_commitment",
    "plan",
    "plan_entry_id",
    "role",
    "schema",
    "shared_precommit_context_sha256",
    "shared_replay_context_sha256",
    "status",
}
_PIN_KEYS: Final = {"path", "sha256"}
_INPUT_AUTHORITY_ROLES: Final = {
    "anti_vacuity_policy",
    "configuration",
    "configuration_design",
    "configuration_implementation",
    "configuration_initial_geometry",
    "configuration_test",
    "factorization",
    "factorization_initial_partition_bundle",
    "factorization_killing_geometry",
    "ideal_formula",
    "member_spec",
    "method_parameters",
    "reference_density",
}
_ROLE8_INPUT_AUTHORITY_ROLES: Final = _INPUT_AUTHORITY_ROLES - {"configuration_initial_geometry"}
_PARTITION_PIN_KEYS: Final = {
    "configuration_index",
    "coordinate",
    "member_report_relative_path",
    "path",
    "sha256",
}
_METHOD_SELECTION_KEYS: Final = {
    "exact_parameter_id",
    "primary_parameter_id",
    "sentinel_parameter_id",
}
_RUNTIME_KEYS: Final = {"gmp", "gmpy2", "mpc", "mpfr", "python_abi"}
_OUTPUT_KEYS: Final = {"path", "schema"}
_PLAN_KEYS: Final = {
    "claim_boundary",
    "entries",
    "schema",
    "shared_context",
    "shared_precommit_context_sha256",
    "status",
}
_PLAN_BUNDLE_CLAIM_KEYS: Final = {
    "external_predecessor_commitment_present",
    "ordered_roles_8_10_replay_executed",
    "production_same_member_bridge_accepted",
    "release_eligible",
}
_PLAN_ENTRY_KEYS: Final = {
    "entry_id",
    "implementation_runtime_closure",
    "input_authorities",
    "invocations",
    "method_selection",
    "outputs",
    "partition_path_bindings",
    "precommit_projection_sha256",
    "request",
    "role",
}
_SHARED_CONTEXT_KEYS: Final = {
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
}
_CONTEXT_PIN_KEYS: Final = {"path", "schema", "sha256"}
_BUNDLE_KEYS: Final = {
    "claim_boundary",
    "member_spec",
    "method_parameter_registry",
    "replay_plan",
    "schema",
    "shared_precommit_context_sha256",
    "status",
}
_COMMITMENT_KEYS: Final = {
    "authentication",
    "authority",
    "candidate_bundle",
    "claim_boundary",
    "commitment_message_sha256",
    "ordering",
    "schema",
    "status",
}
_AUTHENTICATION_KEYS: Final = {
    "authentication_class",
    "evidence_identifier",
    "structural_validation_only",
}
_AUTHORITY_KEYS: Final = {"authority_identifier", "trust_domain_identifier"}
_COMMITMENT_CLAIM_KEYS: Final = {
    "cryptographic_authenticity_verified_locally",
    "externality_proven_by_local_code",
    "roles_8_10_outputs_observed",
}
_ORDERING_KEYS: Final = {
    "committed_before_roles_8_10_replay",
    "no_role_8_10_outputs_observed",
    "result_blind_plan",
}
_RUNTIME_CLOSURE_KEYS: Final = {"producer", "runtime_requirements", "verifier"}
_ROLE8_RUNTIME_CLOSURE_KEYS: Final = {
    "claim_boundary",
    "code_inputs",
    "native_libraries",
    "native_runtime",
    "python_executable",
    "python_imports",
    "report_local_dependencies",
    "schema",
    "status",
}
_ROLE8_RUNTIME_CLAIM_KEYS: Final = {
    "complete_report_local_and_native_runtime_closure",
    "legacy_scientific_backend_imported",
    "result_artifact_dependency_present",
}
_ROLE8_RUNTIME_CLAIMS: Final = {
    "complete_report_local_and_native_runtime_closure": True,
    "legacy_scientific_backend_imported": False,
    "result_artifact_dependency_present": False,
}
_ROLE8_PYTHON_IMPORTS: Final = {
    "producer": [
        "argparse",
        "dataclasses",
        "fractions",
        "gmpy2",
        "hashlib",
        "json",
        "math",
        "os",
        "pathlib",
        "secrets",
        "stat",
        "sys",
        "threading",
        "typing",
        "unicodedata",
    ],
    "verifier": [
        "argparse",
        "dataclasses",
        "fractions",
        "gmpy2",
        "hashlib",
        "json",
        "math",
        "os",
        "pathlib",
        "stat",
        "sys",
        "typing",
        "unicodedata",
    ],
}
_ROLE8_NATIVE_LIBRARY_ROLES: Final = ("gmpy2_extension", "libgmp", "libmpfr", "libmpc")
_ROLE8_NATIVE_LIBRARY_PIN_KEYS: Final = {"path", "role", "sha256"}
_INVOCATIONS_KEYS: Final = {"producer", "verifier"}
_INVOCATION_KEYS: Final = {"argv", "cwd"}
_ENTRY_OUTPUT_KEYS: Final = {"artifact", "validation_receipt"}
_ENTRY_REQUEST_KEYS: Final = {"path", "schema", "status"}
_ROLE_KEYS: Final = {"role_id", "role_name"}
_ROLE8_METHOD_RECORD_KEYS: Final = {"method_parameter_sha256", "parameter_id"}
_ROLE_ENTRY_NAMES: Final = {
    8: ROLE8_NAME,
    9: ROLE_NAME,
    10: ROLE10_NAME,
}
_ROLE_REQUEST_SCHEMAS: Final = {
    8: ROLE8_REQUEST_SCHEMA,
    9: REQUEST_SCHEMA,
    10: ROLE10_REQUEST_SCHEMA,
}
_ROLE_OUTPUT_SCHEMAS: Final = {
    8: ROLE8_OUTPUT_SCHEMA,
    9: OUTPUT_SCHEMA,
    10: ROLE10_OUTPUT_SCHEMA,
}
_ROLE_RECEIPT_SCHEMAS: Final = {
    8: ROLE8_RECEIPT_SCHEMA,
    9: RECEIPT_SCHEMA,
    10: ROLE10_RECEIPT_SCHEMA,
}
_ROLE_SOURCE_FILENAMES: Final = {
    8: (
        "build_continuum_c1_n0_candidate_native_raw_axis_formula_v2.py",
        "validate_continuum_c1_n0_candidate_native_raw_axis_formula_v2.py",
    ),
    9: (
        "build_continuum_c1_n0_candidate_native_stationary_integrals_v2.py",
        "validate_continuum_c1_n0_candidate_native_stationary_integrals_v2.py",
    ),
    10: (
        "build_continuum_c1_n0_candidate_native_killing_factor_geometry_v2.py",
        "validate_continuum_c1_n0_candidate_native_killing_factor_geometry_v2.py",
    ),
}
_ROLE8_METHOD_SELECTION: Final = [
    {
        "method_parameter_sha256": (
            "2393d646b5a5d1d0e0c6c3a97e91b62e9f3e74b3c4007b38b01107161a18cc38"
        ),
        "parameter_id": "raw_flux_directed_mpfr_320_v2",
    },
    {
        "method_parameter_sha256": (
            "d1f3f3074f74ab276b375ef977a467d208a6d730e0b5baeeece19c1178c3caaa"
        ),
        "parameter_id": "raw_flux_directed_mpfr_640_sentinel_v2",
    },
    {
        "method_parameter_sha256": (
            "47e7248b048b4d042397e8f0123f5eceed2433a8b552099eb7883c2dfb60d6f8"
        ),
        "parameter_id": "raw_flux_binary64_decode_v2",
    },
    {
        "method_parameter_sha256": (
            "c1e11de7305a3035973e98d1913e14075f0ba3b2a32180a73689aee4c9b4b851"
        ),
        "parameter_id": EXACT_PARAMETER_ID,
    },
]
_ROLE10_METHOD_SELECTION: Final = {
    "analytic_area_parameter_id": "killing_analytic_disk_area_mpfr_256_v3",
    "classification_parameter_id": "killing_exact_contact_cell_classification_v3",
    "contact_profile_parameter_id": "killing_contact_profile_mpfr_192_v3",
    "verifier_parameter_id": "killing_source_independent_same_backend_verifier_v3",
}
_PARAMETER_REGISTRY_KEYS: Final = {
    "claim_boundary",
    "parameter_count",
    "parameters",
    "schema",
    "status",
}
_PARAMETER_CLAIM_KEYS: Final = {
    "backend_independence_claimed",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "external_predecessor_commitment_present",
    "formal_outer_open_operation_model_present",
    "formal_selected_source_dag_complete",
    "formal_symbolic_candidate_materialized",
    "one_correlated_distinguished_ideal_member_is_contained",
    "ordered_roles_8_10_replay_executed",
    "policy_predecessor_order_independently_sealed",
    "production_same_member_bridge_accepted",
    "release_eligible",
    "root_transfer_complete",
    "science_executed",
    "submission_eligible",
    "symbolic_acceptance_receipt_materialized",
}
_PARAMETER_ORDER: Final = (
    PRIMARY_PARAMETER_ID,
    SENTINEL_PARAMETER_ID,
    "raw_flux_directed_mpfr_320_v2",
    "raw_flux_directed_mpfr_640_sentinel_v2",
    "raw_flux_binary64_decode_v2",
    EXACT_PARAMETER_ID,
    "killing_contact_profile_mpfr_192_v3",
    "killing_analytic_disk_area_mpfr_256_v3",
    "killing_source_independent_same_backend_verifier_v3",
    "killing_exact_contact_cell_classification_v3",
)
_EXPECTED_PARAMETER_RECORDS: Final = {
    PRIMARY_PARAMETER_ID: {
        "aggregation": "exact_Fraction_endpoint_sums_and_nonnegative_products",
        "dense_tensor_materialized": False,
        "precision_bits": 320,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role9_stationary_physical_integral"],
    },
    SENTINEL_PARAMETER_ID: {
        "containment_relation": GENERIC_CONTAINMENT,
        "independent_backend": False,
        "precision_bits": 640,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role9_stationary_physical_integral"],
    },
    EXACT_PARAMETER_ID: {
        "arithmetic": "Python_Fraction_exact_reduced_rationals",
        "precision_bits": "unbounded_integer_fraction",
        "rounding_mode": "exact",
        "source_role_scope": [
            "role8_raw_axis_formula_primitive",
            "role9_stationary_physical_integral",
            "same_member_mass_flux_composition",
            "symbolic_killing_composition",
        ],
    },
}


@dataclass(frozen=True, slots=True)
class MethodRegistryContract:
    schema: str
    status: str
    digest_domain: str
    parameter_order: tuple[str, ...]
    expected_records: dict[str, dict[str, Any]]
    primary_parameter_id: str
    sentinel_parameter_id: str
    exact_parameter_id: str


_ACCEPTED_V4_METHOD_REGISTRY_CONTRACT: Final = MethodRegistryContract(
    schema=PARAMETER_SCHEMA,
    status=PARAMETER_STATUS,
    digest_domain=PARAMETER_DIGEST_DOMAIN,
    parameter_order=_PARAMETER_ORDER,
    expected_records=_EXPECTED_PARAMETER_RECORDS,
    primary_parameter_id=PRIMARY_PARAMETER_ID,
    sentinel_parameter_id=SENTINEL_PARAMETER_ID,
    exact_parameter_id=EXACT_PARAMETER_ID,
)
_ACTIVE_METHOD_REGISTRY_CONTRACT: Final = _ACCEPTED_V4_METHOD_REGISTRY_CONTRACT

_REFERENCE_KEYS: Final = {
    "boundary_and_measure",
    "claim_boundary",
    "coordinate_order",
    "diffusion_and_drift",
    "normalization",
    "physical_parameter_bundle",
    "schema",
    "source_pins",
    "status",
    "unit_table",
}
_FORMULA_KEYS: Final = {
    "claim_boundary",
    "formulae",
    "member_semantics",
    "potential_formulae",
    "schema",
    "source_pins",
    "status",
}
_CONFIGURATION_KEYS: Final = {
    "authority",
    "authorizes_scientific_execution",
    "axis_construction_contracts",
    "configuration_count",
    "configuration_order",
    "configurations",
    "contains_budget_value",
    "contains_control_values",
    "coordinate_order",
    "dynamics",
    "initial_geometry",
    "physical_dimension",
    "quotient_dimension",
    "schema",
    "scope",
    "status",
    "total_state_workload",
    "workload_semantics",
}
_CONFIGURATION_ROW_KEYS: Final = {
    "expected_states",
    "label",
    "midpoint",
    "purpose",
    "relative_parallel",
    "relative_perpendicular",
    "shape",
}
_REFLECTING_AXIS_KEYS: Final = {
    "alignment",
    "lower_binary64_hex",
    "size",
    "upper_binary64_hex",
}
_PERIODIC_AXIS_KEYS: Final = {
    "alignment",
    "periodic_shift_exact",
    "size",
}
_CONFIGURATION_AUTHORITY_KEYS: Final = {
    "design_path",
    "design_sha256",
    "implementation_path",
    "implementation_sha256",
    "test_path",
    "test_sha256",
}
_INITIAL_GEOMETRY_KEYS: Final = {
    "construction",
    "half_width_binary64_hex",
    "normalization",
    "periodic_wrap",
    "shape_definition",
    "source_path",
    "source_schema",
    "source_sha256",
    "starts_binary64_hex",
}
_INITIAL_GEOMETRY_SOURCE_KEYS: Final = {
    "analytic_total_mass_exact",
    "construction",
    "coordinate_order",
    "half_width_binary64_hex",
    "marginal_density",
    "normalization",
    "periodic_coordinate",
    "periodic_wrap",
    "physical_dimension",
    "quotient_dimension",
    "schema",
    "scope",
    "shape_definition",
    "shared_normalizer_across_cells_and_axes",
    "starts_binary64_hex",
    "transverse_period_exact",
}
_INITIAL_PARTITION_BUNDLE_KEYS: Final = {
    "analytic_source_sha256",
    "configuration_count",
    "configuration_sha256",
    "family_relation_sha256",
    "file_inventory",
    "flags",
    "method",
    "rows",
    "schema",
    "status",
    "total_dense_expansion_byte_length",
    "total_state_workload",
}
_KILLING_GEOMETRY_SOURCE_KEYS: Final = {
    "configuration_bundle",
    "contact_geometry",
    "coordinate_order",
    "flags",
    "physical_dimension",
    "quotient_dimension",
    "schema",
    "status",
    "support_basis",
}
_AXIS_CONTRACT_KEYS: Final = {
    "boundary_rule",
    "cardinality_semantics",
    "cell_segments_formula",
    "cell_volumes_formula",
    "positions_formula",
    "source_construction_tag",
    "step_formula",
}
_PERIODIC_AXIS_CONTRACT_KEYS: Final = _AXIS_CONTRACT_KEYS | {"shift_formula"}
_DYNAMICS_KEYS: Final = {
    "directed_precision_bits",
    "midpoint_diffusion_formula",
    "midpoint_potential_formula",
    "ou_mean_binary64_hex",
    "ou_stiffness_binary64_hex",
    "particle_diffusion_binary64_hex",
    "relative_diffusion_formula",
    "relative_parallel_mean_exact",
    "relative_parallel_potential_formula",
    "relative_perpendicular_potential_formula",
    "transverse_domain_start_exact",
    "transverse_period_exact",
}
_SEMANTIC_ID_KEYS: Final = {
    "authority_label",
    "refinement_family_id",
    "refinement_member_id",
}
_SEQUENCE_BINDING_KEYS: Final = {
    "authority_label",
    "configuration_geometry_sha256",
    "configuration_index",
    "initial_partition_row_manifest_path",
    "initial_partition_row_manifest_sha256",
    "n0_anchor_expected_states",
    "n0_anchor_shape",
    "n0_axes",
    "physical_parameter_bundle_sha256",
    "refinement_family_id",
    "refinement_member_id",
    "sequence_id",
    "sequence_source_row_canonical_sha256",
    "sequence_source_row_index",
}
_MEMBER_AXIS_KEYS: Final = {
    "alignment",
    "cell_count",
    "coordinate",
    "exact_box_or_period",
    "partition_report_relative_path",
    "partition_schema",
    "partition_sha256",
    "periodic",
    "refinement_family_id",
    "refinement_member_id",
    "sequence_id",
    "sequence_source_row_canonical_sha256",
}
_MEMBER_PERIODIC_AXIS_KEYS: Final = _MEMBER_AXIS_KEYS | {"periodic_shift_n0_exact"}
_LINEAGE_KEYS: Final = {
    "initial_partition_bundle",
    "joint_refinement_family",
    "predecessor_member_v3",
}
_FACTORIZATION_KEYS: Final = {
    "cell_average_formulae",
    "claim_boundary",
    "contact_geometry",
    "coordinate_and_measure_contract",
    "dependency_closure",
    "enclosure_semantics",
    "outcome_free_contract",
    "profile_basis",
    "schema",
    "source_pins",
    "status",
    "storage_contract",
}
_EXPECTED_FORMULAE: Final = {
    "bernoulli": "Bernoulli(s)=s/(exp(s)-1),Bernoulli(0)=1",
    "common_axis_flux": "kappa_edge=mu_i*q_i_to_j=mu_j*q_j_to_i",
    "discrete_killing": "k=B*V",
    "exact_adjoint_map": "P_h[u]_i=integral_C_i_u*pi_dx/pi_h_i",
    "global_gauge": "G=M_L/(S_midpoint*S_relative_parallel*S_relative_perpendicular)",
    "ideal_axis_mass": "mu_i=cell_volume_i*exp(-potential(representative_i))",
    "map_ratio": "rho_i=M_i_pi/pi_h_i",
    "periodic_axis_mass": "mu_i=cell_volume_i",
    "periodic_rate": "q=D_axis/(cell_width^2)",
    "physical_cell_mass": "M_i_pi=integral_C_i_pi_dx",
    "reconstructed_killing_multiplier": "K=V/rho",
    "reflecting_sg_rate": (
        "q_i_to_j=D_axis/(cell_volume_i*distance_ij)*Bernoulli(potential_j-potential_i)"
    ),
    "tensor_common_conductance": ("c_edge=G*kappa_axis_edge*product_spectator_axis_mu"),
    "tensor_gauged_mass": "pi_h_tensor=G*product_axis_mu",
}
_EXPECTED_CONFIGURATION_AUTHORITY: Final = {
    "design_path": "notes/positive_b_fixed_control_robustness_design_v2.md",
    "design_sha256": "264cf2d2ef17feedcb3c1a5469e18b5c57ba5981b57dc6201147955df3684dcd",
    "implementation_path": "code/rate_defined_tensor_f0.py",
    "implementation_sha256": ("321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5"),
    "test_path": "code/test_rate_defined_tensor_f0.py",
    "test_sha256": "f646ab3d545f698f225296baf774ae629776c17c2882b3f30d3a95cefa6bbd8d",
}
_EXPECTED_SOURCE_LINEAGE: Final = {
    "initial_partition_bundle": {
        "path": "artifacts/data/physical_production_initial_stream_v1/bundle.json",
        "sha256": "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e",
    },
    "joint_refinement_family": {
        "path": "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json",
        "sha256": "1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9",
    },
    "predecessor_member_v3": {
        "path": (
            "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/"
            "continuum_c1_c2_n0_member_spec_v3_candidate.json"
        ),
        "sha256": "b5eea6553d329bcbc4a1eb301dd3d5fb5b5acd387b80bfee5094286d3ca8ab71",
    },
}
_MEMBER_KEYS: Final = {
    "claim_boundary",
    "configuration_order",
    "configuration_semantic_ids",
    "identity_properties",
    "member_identity_sha256",
    "member_semantics",
    "n0_sequence_bindings",
    "reconstruction_counts",
    "role_bindings",
    "schema",
    "source_lineage_evidence",
    "status",
}
_INTERVAL_KEYS: Final = {"lower_exact_p_over_q", "upper_exact_p_over_q"}


class CandidateStationaryFailure(RuntimeError):
    """Fail-closed request, scientific, or publication failure."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code


@dataclass(frozen=True, slots=True)
class ExactInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if type(self.lower) is not Fraction or type(self.upper) is not Fraction:
            raise CandidateStationaryFailure(HOLD_NUMERICAL, "non-Fraction interval endpoint")
        if self.lower > self.upper:
            raise CandidateStationaryFailure(HOLD_NUMERICAL, "reversed interval")

    def contains(self, other: ExactInterval) -> bool:
        return self.lower <= other.lower and other.upper <= self.upper

    def add(self, other: ExactInterval) -> ExactInterval:
        return ExactInterval(self.lower + other.lower, self.upper + other.upper)

    def multiply_nonnegative(self, other: ExactInterval) -> ExactInterval:
        if self.lower < 0 or other.lower < 0:
            raise CandidateStationaryFailure(HOLD_NUMERICAL, "negative product factor")
        return ExactInterval(self.lower * other.lower, self.upper * other.upper)

    def intersect(self, other: ExactInterval) -> ExactInterval:
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower > upper:
            raise CandidateStationaryFailure(HOLD_NUMERICAL, "disjoint interval witnesses")
        return ExactInterval(lower, upper)


@dataclass(frozen=True, slots=True)
class DirectedInterval:
    lower: gmpy2.mpfr
    upper: gmpy2.mpfr
    precision: int

    def exact(self) -> ExactInterval:
        return ExactInterval(_mpfr_fraction(self.lower), _mpfr_fraction(self.upper))


@dataclass(frozen=True, slots=True)
class Snapshot:
    path: Path
    raw: bytes
    sha256: str


@dataclass(frozen=True, slots=True)
class ReplayProtocol:
    request: dict[str, Any]
    request_snapshot: Snapshot
    plan: dict[str, Any]
    plan_snapshot: Snapshot
    bundle: dict[str, Any]
    bundle_snapshot: Snapshot
    commitment: dict[str, Any]
    commitment_snapshot: Snapshot
    entry: dict[str, Any]
    artifact_path: Path
    receipt_path: Path
    shared_precommit_context_sha256: str
    shared_replay_context_sha256: str


@dataclass(frozen=True, slots=True)
class MethodParameters:
    primary_id: str
    sentinel_id: str
    exact_id: str
    primary_bits: int
    sentinel_bits: int
    parameter_digests: dict[str, str]


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise CandidateStationaryFailure(HOLD_INPUT, "duplicate or invalid JSON key")
        result[key] = value
    return result


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        raise CandidateStationaryFailure(HOLD_INPUT, "JSON depth cap exceeded")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if value.bit_length() > MAX_INTEGER_BITS:
            raise CandidateStationaryFailure(HOLD_INPUT, "JSON integer bit cap exceeded")
        return
    if type(value) is float:
        raise CandidateStationaryFailure(HOLD_INPUT, "JSON floating literals are forbidden")
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise CandidateStationaryFailure(HOLD_INPUT, "non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise CandidateStationaryFailure(HOLD_INPUT, "invalid JSON object key")
            _strict_tree(item, depth + 1)
        return
    raise CandidateStationaryFailure(HOLD_INPUT, "unsupported JSON value type")


def canonical_bytes(value: Any) -> bytes:
    _strict_tree(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _parse_canonical(raw: bytes, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                CandidateStationaryFailure(HOLD_INPUT, f"{label}: float {token}")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                CandidateStationaryFailure(HOLD_INPUT, f"{label}: constant {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise CandidateStationaryFailure(HOLD_INPUT, f"{label}: invalid ASCII JSON") from error
    _strict_tree(value)
    if type(value) is not dict or canonical_bytes(value) != raw:
        raise CandidateStationaryFailure(HOLD_INPUT, f"{label}: noncanonical JSON")
    return value


def _parse_authenticated_json(raw: bytes, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                CandidateStationaryFailure(HOLD_INPUT, f"{label}: float {token}")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                CandidateStationaryFailure(HOLD_INPUT, f"{label}: constant {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise CandidateStationaryFailure(
            HOLD_INPUT, f"{label}: invalid authenticated ASCII JSON"
        ) from error
    _strict_tree(value)
    if type(value) is not dict:
        raise CandidateStationaryFailure(HOLD_INPUT, f"{label}: authenticated JSON object required")
    return value


def _exact_keys(value: Any, keys: set[str], *, code: str, label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise CandidateStationaryFailure(code, f"{label}: exact-key mismatch")
    return value


def _json_exactly_equal(value: Any, expected: Any) -> bool:
    if type(value) is not type(expected):
        return False
    if type(value) is dict:
        return set(value) == set(expected) and all(
            _json_exactly_equal(value[key], expected[key]) for key in expected
        )
    if type(value) is list:
        return len(value) == len(expected) and all(
            _json_exactly_equal(left, right) for left, right in zip(value, expected, strict=True)
        )
    return bool(value == expected)


def _is_sha256(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_nonempty_string(value: Any) -> bool:
    return type(value) is str and bool(value)


def _absolute_lexical(value: Any, *, code: str, label: str) -> Path:
    if type(value) is not str or not value:
        raise CandidateStationaryFailure(code, f"{label}: path must be a string")
    path = Path(value)
    lexical = Path(os.path.abspath(path))
    if not path.is_absolute() or path != lexical:
        raise CandidateStationaryFailure(code, f"{label}: canonical absolute path required")
    return path


def _dev_ino(metadata: os.stat_result) -> tuple[int, int]:
    return metadata.st_dev, metadata.st_ino


def _stable_file_identity(metadata: os.stat_result) -> tuple[int, ...]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_uid,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _close_descriptor(descriptor: int | None) -> None:
    if descriptor is None:
        return
    try:
        os.close(descriptor)
    except BaseException:
        pass


def _open_anchored_parent_chain(path: Path) -> tuple[int, tuple[tuple[int, int], ...]]:
    if (
        not path.is_absolute()
        or path != Path(os.path.abspath(path))
        or not path.name
        or any(component in {"", ".", ".."} for component in path.parts[1:])
        or not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
    ):
        raise CandidateStationaryFailure(HOLD_IMMUTABLE, "anchored input traversal unavailable")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK
    descriptor: int | None = None
    identities: list[tuple[int, int]] = []
    try:
        descriptor = os.open(path.anchor, flags)
        root_metadata = os.fstat(descriptor)
        if not stat.S_ISDIR(root_metadata.st_mode):
            raise CandidateStationaryFailure(HOLD_IMMUTABLE, "input root is not a directory")
        identities.append(_dev_ino(root_metadata))
        for component in path.parent.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptor)
            child_metadata = os.fstat(child)
            if not stat.S_ISDIR(child_metadata.st_mode):
                _close_descriptor(child)
                raise CandidateStationaryFailure(
                    HOLD_IMMUTABLE, "input path component is not a directory"
                )
            identities.append(_dev_ino(child_metadata))
            os.close(descriptor)
            descriptor = child
        return descriptor, tuple(identities)
    except BaseException as error:
        _close_descriptor(descriptor)
        if isinstance(error, CandidateStationaryFailure):
            raise
        if isinstance(error, OSError):
            raise CandidateStationaryFailure(
                HOLD_IMMUTABLE, "anchored input directory traversal failed"
            ) from error
        raise


def _open_anchored_leaf(
    path: Path,
) -> tuple[int, tuple[tuple[int, int], ...]]:
    parent_descriptor: int | None = None
    leaf_descriptor: int | None = None
    try:
        parent_descriptor, chain = _open_anchored_parent_chain(path)
        flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
        leaf_descriptor = os.open(path.name, flags, dir_fd=parent_descriptor)
        os.close(parent_descriptor)
        parent_descriptor = None
        return leaf_descriptor, chain
    except BaseException as error:
        _close_descriptor(leaf_descriptor)
        _close_descriptor(parent_descriptor)
        if isinstance(error, CandidateStationaryFailure):
            raise
        if isinstance(error, OSError):
            raise CandidateStationaryFailure(
                HOLD_IMMUTABLE, "descriptor-relative input leaf open failed"
            ) from error
        raise


def _revalidate_anchored_image(
    path: Path,
    expected_chain: tuple[tuple[int, int], ...],
    expected_file: tuple[int, ...],
) -> None:
    parent_descriptor: int | None = None
    leaf_descriptor: int | None = None
    try:
        parent_descriptor, observed_chain = _open_anchored_parent_chain(path)
        if observed_chain != expected_chain:
            raise CandidateStationaryFailure(
                HOLD_IMMUTABLE, "input directory chain identity changed"
            )
        flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
        leaf_descriptor = os.open(path.name, flags, dir_fd=parent_descriptor)
        if _stable_file_identity(os.fstat(leaf_descriptor)) != expected_file:
            raise CandidateStationaryFailure(HOLD_IMMUTABLE, "input leaf identity changed")
    except BaseException as error:
        if isinstance(error, CandidateStationaryFailure):
            raise
        if isinstance(error, OSError):
            raise CandidateStationaryFailure(
                HOLD_IMMUTABLE, "live input chain revalidation failed"
            ) from error
        raise
    finally:
        _close_descriptor(leaf_descriptor)
        _close_descriptor(parent_descriptor)


def immutable_snapshot(
    path: Path,
    *,
    cap: int = MAX_JSON_BYTES,
    require_read_only: bool = True,
) -> Snapshot:
    descriptor, directory_chain = _open_anchored_leaf(path)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.getuid()
            or before.st_nlink != 1
            or (require_read_only and before.st_mode & 0o222)
            or before.st_size <= 0
            or before.st_size > cap
        ):
            raise CandidateStationaryFailure(
                HOLD_IMMUTABLE, f"input must be owned, read-only, single-link regular: {path}"
            )
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1 << 20))
            if not chunk:
                raise CandidateStationaryFailure(HOLD_IMMUTABLE, f"short read: {path}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise CandidateStationaryFailure(HOLD_IMMUTABLE, f"input grew: {path}")
        after = os.fstat(descriptor)
        if _stable_file_identity(before) != _stable_file_identity(after):
            raise CandidateStationaryFailure(HOLD_IMMUTABLE, f"input changed: {path}")
        _revalidate_anchored_image(path, directory_chain, _stable_file_identity(after))
    finally:
        _close_descriptor(descriptor)
    raw = b"".join(chunks)
    return Snapshot(path=path, raw=raw, sha256=hashlib.sha256(raw).hexdigest())


def _pin_snapshot(pin: Any, *, label: str, cap: int = MAX_JSON_BYTES) -> Snapshot:
    current = _exact_keys(pin, _PIN_KEYS, code=HOLD_REQUEST, label=label)
    path = _absolute_lexical(current["path"], code=HOLD_REQUEST, label=label)
    expected = current["sha256"]
    if not _is_sha256(expected):
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: invalid SHA-256")
    observed = immutable_snapshot(path, cap=cap)
    if observed.sha256 != expected:
        raise CandidateStationaryFailure(HOLD_INPUT, f"{label}: SHA-256 mismatch")
    return observed


def _runtime_pin_snapshot(
    pin: Any,
    *,
    label: str,
    cap: int = MAX_RUNTIME_BYTES,
) -> Snapshot:
    current = _exact_keys(pin, _PIN_KEYS, code=HOLD_RUNTIME, label=label)
    path = _absolute_lexical(current["path"], code=HOLD_RUNTIME, label=label)
    expected = current["sha256"]
    if not _is_sha256(expected):
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: invalid SHA-256")
    observed = immutable_snapshot(path, cap=cap, require_read_only=False)
    if observed.sha256 != expected:
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: SHA-256 mismatch")
    return observed


def _fraction(value: Any, *, code: str = HOLD_INPUT, label: str = "fraction") -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise CandidateStationaryFailure(code, f"{label}: canonical p/q required")
    numerator_text, denominator_text = value.split("/")
    try:
        result = Fraction(int(numerator_text), int(denominator_text))
    except (ValueError, ZeroDivisionError) as error:
        raise CandidateStationaryFailure(code, f"{label}: invalid fraction") from error
    if result.denominator <= 0 or _fraction_text(result) != value:
        raise CandidateStationaryFailure(code, f"{label}: noncanonical fraction")
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_INTEGER_BITS:
        raise CandidateStationaryFailure(code, f"{label}: fraction bit cap exceeded")
    return result


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _binary64_fraction(value: Any, *, label: str) -> Fraction:
    if type(value) is not str:
        raise CandidateStationaryFailure(HOLD_INPUT, f"{label}: binary64 hex required")
    try:
        parsed = float.fromhex(value)
    except (OverflowError, ValueError) as error:
        raise CandidateStationaryFailure(HOLD_INPUT, f"{label}: invalid binary64 hex") from error
    if (
        not math.isfinite(parsed)
        or parsed.hex() != value
        or (parsed == 0 and math.copysign(1.0, parsed) < 0)
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, f"{label}: noncanonical binary64")
    return Fraction.from_float(parsed)


def _domain_digest(domain: str, value: Any) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\0" + canonical_bytes(value)).hexdigest()


def _interval_json(value: ExactInterval) -> dict[str, str]:
    return {
        "lower_exact_p_over_q": _fraction_text(value.lower),
        "upper_exact_p_over_q": _fraction_text(value.upper),
    }


def _context(bits: int, rounding: int) -> gmpy2.context:
    return gmpy2.context(
        precision=bits,
        round=rounding,
        emax=1_073_741_823,
        emin=-1_073_741_823,
        subnormalize=False,
        trap_underflow=False,
        trap_overflow=False,
        trap_inexact=False,
        trap_invalid=False,
        trap_erange=False,
        trap_divzero=False,
        allow_complex=False,
        rational_division=False,
        allow_release_gil=False,
    )


def _rounded_fraction(value: Fraction, bits: int, rounding: int) -> gmpy2.mpfr:
    with gmpy2.context(_context(bits, rounding)):
        return +gmpy2.mpfr(gmpy2.mpq(value.numerator, value.denominator))


def _mpfr_fraction(value: gmpy2.mpfr) -> Fraction:
    rational = gmpy2.mpq(value)
    return Fraction(int(rational.numerator), int(rational.denominator))


def _from_fraction(value: Fraction, bits: int) -> DirectedInterval:
    return DirectedInterval(
        _rounded_fraction(value, bits, gmpy2.RoundDown),
        _rounded_fraction(value, bits, gmpy2.RoundUp),
        bits,
    )


def _binary(left: DirectedInterval, right: DirectedInterval, operation: str) -> DirectedInterval:
    if left.precision != right.precision:
        raise CandidateStationaryFailure(HOLD_NUMERICAL, "precision mismatch")
    pairs = (
        (left.lower, right.lower),
        (left.lower, right.upper),
        (left.upper, right.lower),
        (left.upper, right.upper),
    )
    bits = left.precision
    if operation == "subtract":
        with gmpy2.context(_context(bits, gmpy2.RoundDown)):
            lower = +(left.lower - right.upper)
        with gmpy2.context(_context(bits, gmpy2.RoundUp)):
            upper = +(left.upper - right.lower)
        return DirectedInterval(lower, upper, bits)
    if operation == "multiply":
        lowers: list[gmpy2.mpfr] = []
        uppers: list[gmpy2.mpfr] = []
        for a, b in pairs:
            with gmpy2.context(_context(bits, gmpy2.RoundDown)):
                lowers.append(+(a * b))
            with gmpy2.context(_context(bits, gmpy2.RoundUp)):
                uppers.append(+(a * b))
        return DirectedInterval(min(lowers), max(uppers), bits)
    raise CandidateStationaryFailure(HOLD_NUMERICAL, "unknown directed operation")


def _monotone(value: DirectedInterval, function: Any) -> DirectedInterval:
    with gmpy2.context(_context(value.precision, gmpy2.RoundDown)):
        lower = +function(value.lower)
    with gmpy2.context(_context(value.precision, gmpy2.RoundUp)):
        upper = +function(value.upper)
    return DirectedInterval(lower, upper, value.precision)


def _gaussian_mass(
    lower: Fraction,
    upper: Fraction,
    *,
    coefficient: Fraction,
    centre: Fraction,
    bits: int,
) -> ExactInterval:
    if lower >= upper or coefficient <= 0:
        raise CandidateStationaryFailure(HOLD_NUMERICAL, "invalid Gaussian segment")
    root = _monotone(_from_fraction(coefficient, bits), gmpy2.sqrt)
    low_argument = _binary(root, _from_fraction(lower - centre, bits), "multiply")
    high_argument = _binary(root, _from_fraction(upper - centre, bits), "multiply")
    low_erf = _monotone(low_argument, gmpy2.erf)
    high_erf = _monotone(high_argument, gmpy2.erf)
    difference = _binary(high_erf, low_erf, "subtract")
    result = _binary(difference, _from_fraction(Fraction(1, 2), bits), "multiply").exact()
    if not 0 < result.lower <= result.upper <= 1:
        raise CandidateStationaryFailure(HOLD_NUMERICAL, "Gaussian mass escaped [0,1]")
    return result


def _sum_intervals(values: Sequence[ExactInterval]) -> ExactInterval:
    result = ExactInterval(Fraction(0), Fraction(0))
    for value in values:
        result = result.add(value)
    return result


def _modulo(value: Fraction, period: Fraction) -> Fraction:
    if period <= 0:
        raise CandidateStationaryFailure(HOLD_MEMBER, "nonpositive periodic width")
    return value - (value // period) * period


def _reconstruct_partition(
    coordinate: str,
    configuration_axis: dict[str, Any],
    dynamics: dict[str, Any],
) -> dict[str, Any]:
    size = configuration_axis.get("size")
    alignment = configuration_axis.get("alignment")
    if type(size) is not int or size < 2 or size > MAX_AXIS_CELLS or type(alignment) is not str:
        raise CandidateStationaryFailure(HOLD_MEMBER, "invalid configuration axis")
    if alignment in {"cell_centred_reflecting", "vertex_centred_reflecting_dual"}:
        lower = _binary64_fraction(configuration_axis.get("lower_binary64_hex"), label="axis lower")
        upper = _binary64_fraction(configuration_axis.get("upper_binary64_hex"), label="axis upper")
        if lower >= upper:
            raise CandidateStationaryFailure(HOLD_MEMBER, "reflecting domain is reversed")
        width = upper - lower
        shift = Fraction(0)
        if alignment == "cell_centred_reflecting":
            step = width / size
            positions = [lower + (Fraction(index) + Fraction(1, 2)) * step for index in range(size)]
            segments = [
                [(lower + index * step, lower + (index + 1) * step)] for index in range(size)
            ]
            construction = "cell_centred_reflecting_scharfetter_gummel"
        else:
            step = width / (size - 1)
            positions = [lower + index * step for index in range(size)]
            boundaries = (
                [lower]
                + [lower + (Fraction(index) - Fraction(1, 2)) * step for index in range(1, size)]
                + [upper]
            )
            segments = [[(boundaries[index], boundaries[index + 1])] for index in range(size)]
            construction = "vertex_centred_reflecting_scharfetter_gummel"
        start = lower
        periodic = False
    elif alignment in {"cell_centred_periodic_base", "cell_centred_periodic_half_shift"}:
        start = _fraction(
            dynamics.get("transverse_domain_start_exact"), code=HOLD_MEMBER, label="period start"
        )
        width = _fraction(
            dynamics.get("transverse_period_exact"), code=HOLD_MEMBER, label="period width"
        )
        step = width / size
        shift = _fraction(
            configuration_axis.get("periodic_shift_exact"),
            code=HOLD_MEMBER,
            label="periodic shift",
        )
        expected_shift = Fraction(0) if alignment.endswith("_base") else step / 2
        if shift != expected_shift:
            raise CandidateStationaryFailure(HOLD_MEMBER, "periodic shift mismatch")
        positions = [
            start + _modulo((Fraction(index) + Fraction(1, 2)) * step + shift, width)
            for index in range(size)
        ]
        end = start + width
        segments: list[list[tuple[Fraction, Fraction]]] = []
        for index in range(size):
            cell_start = start + _modulo(index * step + shift, width)
            cell_end = cell_start + step
            if cell_end <= end:
                segments.append([(cell_start, cell_end)])
            else:
                segments.append([(cell_start, end), (start, start + cell_end - end)])
        construction = (
            "cell_centred_periodic_diffusion"
            if alignment.endswith("_base")
            else "cell_centred_periodic_diffusion_half_shift"
        )
        periodic = True
    else:
        raise CandidateStationaryFailure(HOLD_MEMBER, "unknown axis alignment")
    volumes = [sum((upper - lower for lower, upper in cell), Fraction(0)) for cell in segments]
    return {
        "cell_segments_exact": [
            [[_fraction_text(lower), _fraction_text(upper)] for lower, upper in cell]
            for cell in segments
        ],
        "cell_volumes_exact": [_fraction_text(value) for value in volumes],
        "construction": construction,
        "coordinate": coordinate,
        "domain_start_exact": _fraction_text(start),
        "domain_width_exact": _fraction_text(width),
        "periodic": periodic,
        "periodic_shift_exact": _fraction_text(shift),
        "positions_exact": [_fraction_text(value) for value in positions],
        "schema": PARTITION_SCHEMA,
        "size": size,
    }


def _runtime_versions() -> dict[str, str]:
    return {
        "gmp": gmpy2.mp_version(),
        "gmpy2": gmpy2.__version__,
        "mpc": gmpy2.mpc_version(),
        "mpfr": gmpy2.mpfr_version(),
        "python_abi": f"CPython {sys.version_info.major}.{sys.version_info.minor}",
    }


def _validate_runtime(request: dict[str, Any]) -> dict[str, str]:
    required = _exact_keys(
        request["runtime_requirements"], _RUNTIME_KEYS, code=HOLD_REQUEST, label="runtime"
    )
    if any(type(value) is not str or not value for value in required.values()):
        raise CandidateStationaryFailure(HOLD_REQUEST, "runtime values must be nonempty strings")
    observed = _runtime_versions()
    if observed != required:
        raise CandidateStationaryFailure(HOLD_RUNTIME, "runtime version mismatch")
    return observed


def _validate_method_registry(
    registry: dict[str, Any], selection: dict[str, Any]
) -> MethodParameters:
    contract = _ACTIVE_METHOD_REGISTRY_CONTRACT
    _exact_keys(selection, _METHOD_SELECTION_KEYS, code=HOLD_REQUEST, label="method selection")
    _exact_keys(
        registry,
        _PARAMETER_REGISTRY_KEYS,
        code=HOLD_METHOD,
        label="parameter registry",
    )
    claims = registry["claim_boundary"]
    if (
        registry["schema"] != contract.schema
        or registry["status"] != contract.status
        or type(claims) is not dict
        or set(claims) != _PARAMETER_CLAIM_KEYS
        or any(value is not False for value in claims.values())
    ):
        raise CandidateStationaryFailure(HOLD_METHOD, "parameter registry boundary mismatch")
    entries = registry.get("parameters")
    count = registry.get("parameter_count")
    _reject_result_observed_keys(registry, code=HOLD_METHOD, label="parameter registry")
    if (
        type(entries) is not list
        or type(count) is not int
        or count != 10
        or count != len(entries)
        or [entry.get("parameter_id") if type(entry) is dict else None for entry in entries]
        != list(contract.parameter_order)
    ):
        raise CandidateStationaryFailure(HOLD_METHOD, "parameter registry cardinality mismatch")
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if type(entry) is not dict or set(entry) != {
            "method_parameter_sha256",
            "parameter_id",
            "parameters",
        }:
            raise CandidateStationaryFailure(HOLD_METHOD, "invalid parameter entry")
        identifier = entry["parameter_id"]
        parameters = entry["parameters"]
        digest = entry["method_parameter_sha256"]
        if (
            type(identifier) is not str
            or identifier in by_id
            or type(parameters) is not dict
            or not _is_sha256(digest)
            or digest != _domain_digest(contract.digest_domain, parameters)
        ):
            raise CandidateStationaryFailure(HOLD_METHOD, "parameter record mismatch")
        by_id[identifier] = entry
    identifiers = {
        "primary": selection["primary_parameter_id"],
        "sentinel": selection["sentinel_parameter_id"],
        "exact": selection["exact_parameter_id"],
    }
    if identifiers != {
        "primary": contract.primary_parameter_id,
        "sentinel": contract.sentinel_parameter_id,
        "exact": contract.exact_parameter_id,
    } or any(value not in by_id for value in identifiers.values()):
        raise CandidateStationaryFailure(HOLD_METHOD, "selected parameter identity mismatch")
    for identifier in identifiers.values():
        if canonical_bytes(by_id[identifier]["parameters"]) != canonical_bytes(
            contract.expected_records[identifier]
        ):
            raise CandidateStationaryFailure(HOLD_METHOD, "selected parameter record mismatch")
    return MethodParameters(
        primary_id=identifiers["primary"],
        sentinel_id=identifiers["sentinel"],
        exact_id=identifiers["exact"],
        primary_bits=contract.expected_records[contract.primary_parameter_id]["precision_bits"],
        sentinel_bits=contract.expected_records[contract.sentinel_parameter_id]["precision_bits"],
        parameter_digests={
            identifier: by_id[identifier]["method_parameter_sha256"]
            for identifier in identifiers.values()
        },
    )


def _require_false_boundary(value: Any, *, label: str) -> dict[str, bool]:
    if (
        type(value) is not dict
        or not value
        or any(type(key) is not str or not key for key in value)
        or any(item is not False for item in value.values())
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: false-only boundary required")
    return value


def _pin_without_schema(value: Any, *, label: str) -> dict[str, str]:
    pin = _exact_keys(value, _CONTEXT_PIN_KEYS, code=HOLD_REQUEST, label=label)
    if not _is_nonempty_string(pin["schema"]) or not _is_sha256(pin["sha256"]):
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: invalid contextual pin")
    path = pin["path"]
    pure = PurePosixPath(path) if _is_nonempty_string(path) else None
    if (
        pure is None
        or pure.is_absolute()
        or not pure.parts
        or any(part in {"", ".", ".."} for part in pure.parts)
        or pure.as_posix() != path
    ):
        raise CandidateStationaryFailure(
            HOLD_REQUEST, f"{label}: canonical report-relative POSIX path required"
        )
    return {"path": pin["path"], "sha256": pin["sha256"]}


def _same_pin(left: Any, right: Any, *, label: str) -> None:
    left_pin = _exact_keys(left, _PIN_KEYS, code=HOLD_REQUEST, label=f"{label} left")
    right_pin = _exact_keys(right, _PIN_KEYS, code=HOLD_REQUEST, label=f"{label} right")
    if left_pin != right_pin:
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: pin mismatch")


def _same_logical_authority(absolute_pin: Any, logical_pin: Any, *, label: str) -> None:
    execution = _exact_keys(absolute_pin, _PIN_KEYS, code=HOLD_REQUEST, label=f"{label} execution")
    logical = _exact_keys(logical_pin, _PIN_KEYS, code=HOLD_REQUEST, label=f"{label} logical")
    absolute = _absolute_lexical(
        execution["path"], code=HOLD_REQUEST, label=f"{label} execution path"
    )
    pure = PurePosixPath(logical["path"])
    if (
        execution["sha256"] != logical["sha256"]
        or tuple(absolute.parts[-len(pure.parts) :]) != pure.parts
    ):
        raise CandidateStationaryFailure(
            HOLD_REQUEST, f"{label}: logical/execution authority mismatch"
        )


def _plan_pin_shape(value: Any, *, label: str) -> tuple[dict[str, str], Path]:
    pin = _exact_keys(value, _PIN_KEYS, code=HOLD_REQUEST, label=label)
    if not _is_sha256(pin["sha256"]):
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: invalid SHA-256")
    path = _absolute_lexical(pin["path"], code=HOLD_REQUEST, label=f"{label} path")
    snapshot = immutable_snapshot(path, cap=MAX_JSON_BYTES)
    if snapshot.sha256 != pin["sha256"]:
        raise CandidateStationaryFailure(HOLD_INPUT, f"{label}: SHA-256 mismatch")
    return pin, path


def _validate_role8_runtime_closure(
    closure_snapshot: Snapshot,
    *,
    label: str,
) -> tuple[dict[str, Snapshot], set[Path]]:
    closure = _parse_canonical(closure_snapshot.raw, label=f"{label} closure content")
    _exact_keys(
        closure,
        _ROLE8_RUNTIME_CLOSURE_KEYS,
        code=HOLD_RUNTIME,
        label=f"{label} closure content",
    )
    _validate_result_blind_string_values(
        closure,
        code=HOLD_RUNTIME,
        label=f"{label} closure content",
    )
    if (
        closure["schema"] != ROLE8_RUNTIME_CLOSURE_SCHEMA
        or closure["status"] != ROLE8_RUNTIME_CLOSURE_STATUS
    ):
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: schema/status mismatch")
    claims = _exact_keys(
        closure["claim_boundary"],
        _ROLE8_RUNTIME_CLAIM_KEYS,
        code=HOLD_RUNTIME,
        label=f"{label} claims",
    )
    if not _json_exactly_equal(claims, _ROLE8_RUNTIME_CLAIMS):
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: claim mismatch")
    if (
        type(closure["report_local_dependencies"]) is not list
        or closure["report_local_dependencies"]
    ):
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: report-local dependency mismatch")

    code_inputs = _exact_keys(
        closure["code_inputs"],
        {"producer", "verifier"},
        code=HOLD_RUNTIME,
        label=f"{label} code inputs",
    )
    source_snapshots = {
        role: _pin_snapshot(pin, label=f"{label} {role} source")
        for role, pin in code_inputs.items()
    }
    if source_snapshots["producer"].path == source_snapshots["verifier"].path:
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: source separation mismatch")

    native_runtime = _exact_keys(
        closure["native_runtime"],
        _RUNTIME_KEYS,
        code=HOLD_RUNTIME,
        label=f"{label} native runtime",
    )
    if any(
        type(value) is not str or not value for value in native_runtime.values()
    ) or not _json_exactly_equal(native_runtime, _runtime_versions()):
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: native runtime mismatch")

    executable = _runtime_pin_snapshot(
        closure["python_executable"],
        label=f"{label} Python executable",
    )
    if executable.path != Path(sys.executable).resolve():
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: Python executable mismatch")
    if not _json_exactly_equal(closure["python_imports"], _ROLE8_PYTHON_IMPORTS):
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: Python imports mismatch")

    package_directory = Path(gmpy2.__file__).resolve().parent
    library_directory = package_directory.parent / "gmpy2.libs"
    expected_candidates = {
        "gmpy2_extension": sorted(package_directory.glob("gmpy2*.so")),
        "libgmp": sorted(library_directory.glob("libgmp.*.dylib")),
        "libmpfr": sorted(library_directory.glob("libmpfr.*.dylib")),
        "libmpc": sorted(library_directory.glob("libmpc.*.dylib")),
    }
    if any(len(paths) != 1 for paths in expected_candidates.values()):
        raise CandidateStationaryFailure(
            HOLD_RUNTIME, f"{label}: native library discovery mismatch"
        )
    native_libraries = closure["native_libraries"]
    if type(native_libraries) is not list or len(native_libraries) != len(
        _ROLE8_NATIVE_LIBRARY_ROLES
    ):
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: native library count")
    native_snapshots: list[Snapshot] = []
    for ordinal, raw_pin in enumerate(native_libraries):
        pin = _exact_keys(
            raw_pin,
            _ROLE8_NATIVE_LIBRARY_PIN_KEYS,
            code=HOLD_RUNTIME,
            label=f"{label} native library {ordinal}",
        )
        expected_role = _ROLE8_NATIVE_LIBRARY_ROLES[ordinal]
        if pin["role"] != expected_role:
            raise CandidateStationaryFailure(
                HOLD_RUNTIME, f"{label}: native library role/order mismatch"
            )
        native_snapshot = _runtime_pin_snapshot(
            {"path": pin["path"], "sha256": pin["sha256"]},
            label=f"{label} native library {expected_role}",
        )
        if native_snapshot.path != expected_candidates[expected_role][0].resolve():
            raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: native library path mismatch")
        native_snapshots.append(native_snapshot)

    dependency_paths = {
        closure_snapshot.path,
        executable.path,
        *(snapshot.path for snapshot in source_snapshots.values()),
        *(snapshot.path for snapshot in native_snapshots),
    }
    if len(dependency_paths) != 2 + len(source_snapshots) + len(native_snapshots):
        raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: runtime path alias")
    return source_snapshots, dependency_paths


def _validate_plan_partition_bindings(
    value: Any,
    *,
    label: str,
) -> tuple[list[dict[str, Any]], set[Path]]:
    if type(value) is not list or len(value) != EXPECTED_AXIS_COUNT:
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: partition cardinality")
    validated: list[dict[str, Any]] = []
    dependency_paths: set[Path] = set()
    for ordinal, raw_pin in enumerate(value):
        pin = _exact_keys(
            raw_pin,
            _PARTITION_PIN_KEYS,
            code=HOLD_REQUEST,
            label=f"{label} partition {ordinal}",
        )
        expected_index, coordinate_ordinal = divmod(ordinal, len(COORDINATES))
        coordinate = COORDINATES[coordinate_ordinal]
        relative = pin["member_report_relative_path"]
        pure = PurePosixPath(relative) if _is_nonempty_string(relative) else None
        absolute = _absolute_lexical(
            pin["path"], code=HOLD_REQUEST, label=f"{label} partition path {ordinal}"
        )
        if (
            type(pin["configuration_index"]) is not int
            or pin["configuration_index"] != expected_index
            or pin["coordinate"] != coordinate
            or pure is None
            or pure.is_absolute()
            or not pure.parts
            or any(part in {"", ".", ".."} for part in pure.parts)
            or pure.as_posix() != relative
            or tuple(absolute.parts[-len(pure.parts) :]) != pure.parts
            or not _is_sha256(pin["sha256"])
        ):
            raise CandidateStationaryFailure(
                HOLD_REQUEST, f"{label}: partition binding mismatch at {ordinal}"
            )
        snapshot = immutable_snapshot(absolute, cap=MAX_JSON_BYTES)
        if snapshot.sha256 != pin["sha256"]:
            raise CandidateStationaryFailure(
                HOLD_INPUT, f"{label}: partition SHA-256 mismatch at {ordinal}"
            )
        validated.append(pin)
        dependency_paths.add(snapshot.path)
    return validated, dependency_paths


def _validate_plan_entry_semantics(
    entry: dict[str, Any],
    *,
    role: int,
    shared_context: dict[str, Any],
) -> tuple[tuple[Path, Path, Path], set[Path]]:
    label = f"role-{role} plan entry"
    dependency_paths: set[Path] = set()
    if (
        type(entry["role"]) is not int
        or entry["role"] != role
        or entry["entry_id"] != _ROLE_ENTRY_NAMES[role]
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: identity mismatch")

    planned_request = _exact_keys(
        entry["request"], _ENTRY_REQUEST_KEYS, code=HOLD_REQUEST, label=f"{label} request"
    )
    request_path = _absolute_lexical(
        planned_request["path"], code=HOLD_REQUEST, label=f"{label} request path"
    )
    if planned_request != {
        "path": str(request_path),
        "schema": _ROLE_REQUEST_SCHEMAS[role],
        "status": REQUEST_STATUS,
    }:
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: request contract")

    outputs = _exact_keys(
        entry["outputs"], _ENTRY_OUTPUT_KEYS, code=HOLD_REQUEST, label=f"{label} outputs"
    )
    artifact = _exact_keys(
        outputs["artifact"], _OUTPUT_KEYS, code=HOLD_REQUEST, label=f"{label} artifact"
    )
    receipt = _exact_keys(
        outputs["validation_receipt"],
        _OUTPUT_KEYS,
        code=HOLD_REQUEST,
        label=f"{label} receipt",
    )
    artifact_path = _absolute_lexical(
        artifact["path"], code=HOLD_REQUEST, label=f"{label} artifact path"
    )
    receipt_path = _absolute_lexical(
        receipt["path"], code=HOLD_REQUEST, label=f"{label} receipt path"
    )
    if (
        artifact["schema"] != _ROLE_OUTPUT_SCHEMAS[role]
        or receipt["schema"] != _ROLE_RECEIPT_SCHEMAS[role]
        or len({request_path, artifact_path, receipt_path}) != 3
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: output contract")

    runtime = entry["implementation_runtime_closure"]
    if role == 8:
        closure_pin = _exact_keys(
            runtime,
            _CONTEXT_PIN_KEYS,
            code=HOLD_REQUEST,
            label=f"{label} runtime closure",
        )
        if closure_pin["schema"] != ROLE8_RUNTIME_CLOSURE_SCHEMA or not _is_sha256(
            closure_pin["sha256"]
        ):
            raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: runtime closure pin")
        closure_path = _absolute_lexical(
            closure_pin["path"], code=HOLD_REQUEST, label=f"{label} runtime closure path"
        )
        closure_snapshot = immutable_snapshot(closure_path, cap=MAX_JSON_BYTES)
        if closure_snapshot.sha256 != closure_pin["sha256"]:
            raise CandidateStationaryFailure(
                HOLD_INPUT, f"{label}: runtime closure SHA-256 mismatch"
            )
        source_snapshots, runtime_paths = _validate_role8_runtime_closure(
            closure_snapshot,
            label=f"{label} runtime closure",
        )
        producer_path = source_snapshots["producer"].path
        verifier_path = source_snapshots["verifier"].path
        dependency_paths.update(runtime_paths)
        expected_prefix = [sys.executable, "-I", "-B"]
    else:
        closure = _exact_keys(
            runtime,
            _RUNTIME_CLOSURE_KEYS,
            code=HOLD_REQUEST,
            label=f"{label} runtime closure",
        )
        _, producer_path = _plan_pin_shape(closure["producer"], label=f"{label} producer source")
        _, verifier_path = _plan_pin_shape(closure["verifier"], label=f"{label} verifier source")
        dependency_paths.update((producer_path, verifier_path))
        required_runtime = _exact_keys(
            closure["runtime_requirements"],
            _RUNTIME_KEYS,
            code=HOLD_REQUEST,
            label=f"{label} runtime requirements",
        )
        if required_runtime != _runtime_versions():
            raise CandidateStationaryFailure(HOLD_RUNTIME, f"{label}: runtime mismatch")
        expected_prefix = [sys.executable]

    invocations = _exact_keys(
        entry["invocations"], _INVOCATIONS_KEYS, code=HOLD_REQUEST, label=f"{label} invocations"
    )
    checked_invocations: dict[str, dict[str, Any]] = {}
    for invocation_role in ("producer", "verifier"):
        invocation = _exact_keys(
            invocations[invocation_role],
            _INVOCATION_KEYS,
            code=HOLD_REQUEST,
            label=f"{label} {invocation_role} invocation",
        )
        if (
            type(invocation["argv"]) is not list
            or any(type(argument) is not str or not argument for argument in invocation["argv"])
            or type(invocation["cwd"]) is not str
        ):
            raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: invocation type mismatch")
        _absolute_lexical(
            invocation["cwd"], code=HOLD_REQUEST, label=f"{label} {invocation_role} cwd"
        )
        checked_invocations[invocation_role] = invocation

    expected_producer = [
        *expected_prefix,
        str(producer_path),
        "--request",
        str(request_path),
        "--output",
        str(artifact_path),
    ]
    expected_verifier = [
        *expected_prefix,
        str(verifier_path),
        "--request",
        str(request_path),
        "--output",
        str(artifact_path),
        "--receipt",
        str(receipt_path),
    ]
    expected_source_names = _ROLE_SOURCE_FILENAMES[role]
    expected_cwd = producer_path.parent.parent
    if (
        producer_path.name != expected_source_names[0]
        or verifier_path.name != expected_source_names[1]
        or producer_path.parent != verifier_path.parent
        or checked_invocations["producer"]["argv"] != expected_producer
        or checked_invocations["verifier"]["argv"] != expected_verifier
        or checked_invocations["producer"]["cwd"] != str(expected_cwd)
        or checked_invocations["verifier"]["cwd"] != str(expected_cwd)
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, f"{label}: exact invocation mismatch")

    authority_keys = _ROLE8_INPUT_AUTHORITY_ROLES if role == 8 else _INPUT_AUTHORITY_ROLES
    authorities = _exact_keys(
        entry["input_authorities"],
        authority_keys,
        code=HOLD_REQUEST,
        label=f"{label} authorities",
    )
    for authority_role, authority_pin in authorities.items():
        _, authority_path = _plan_pin_shape(
            authority_pin, label=f"{label} authority {authority_role}"
        )
        dependency_paths.add(authority_path)
    context_role_map = {
        "anti_vacuity_policy": "anti_vacuity_policy",
        "configuration": "configuration",
        "factorization": "factorization",
        "ideal_formula": "ideal_formula",
        "member_spec": "member_spec",
        "method_parameters": "method_parameter_registry",
        "reference_density": "reference_density",
    }
    for authority_role, context_role in context_role_map.items():
        _same_logical_authority(
            authorities[authority_role],
            _pin_without_schema(shared_context[context_role], label=f"shared {context_role}"),
            label=f"{label} shared {authority_role}",
        )

    method_selection = entry["method_selection"]
    if role == 8:
        if type(method_selection) is not list or method_selection != _ROLE8_METHOD_SELECTION:
            raise CandidateStationaryFailure(HOLD_METHOD, f"{label}: method selection")
        for ordinal, record in enumerate(method_selection):
            _exact_keys(
                record,
                _ROLE8_METHOD_RECORD_KEYS,
                code=HOLD_METHOD,
                label=f"{label} method record {ordinal}",
            )
    elif role == 9:
        selected = _exact_keys(
            method_selection,
            _METHOD_SELECTION_KEYS,
            code=HOLD_METHOD,
            label=f"{label} method selection",
        )
        if selected != {
            "exact_parameter_id": EXACT_PARAMETER_ID,
            "primary_parameter_id": PRIMARY_PARAMETER_ID,
            "sentinel_parameter_id": SENTINEL_PARAMETER_ID,
        }:
            raise CandidateStationaryFailure(HOLD_METHOD, f"{label}: method selection")
    else:
        if method_selection != _ROLE10_METHOD_SELECTION:
            raise CandidateStationaryFailure(HOLD_METHOD, f"{label}: method selection")
        _exact_keys(
            method_selection,
            set(_ROLE10_METHOD_SELECTION),
            code=HOLD_METHOD,
            label=f"{label} method selection",
        )

    _, partition_paths = _validate_plan_partition_bindings(
        entry["partition_path_bindings"], label=label
    )
    dependency_paths.update(partition_paths)
    return (request_path, artifact_path, receipt_path), dependency_paths


def _validate_all_plan_entries(
    entries: list[dict[str, Any]], shared_context: dict[str, Any]
) -> tuple[tuple[Path, ...], tuple[Path, ...], frozenset[Path]]:
    request_paths: list[Path] = []
    output_paths: list[Path] = []
    dependency_paths: set[Path] = set()
    reference_partitions: bytes | None = None
    for role, entry in zip((8, 9, 10), entries, strict=True):
        slots, entry_dependencies = _validate_plan_entry_semantics(
            entry,
            role=role,
            shared_context=shared_context,
        )
        request_paths.append(slots[0])
        output_paths.extend(slots[1:])
        dependency_paths.update(entry_dependencies)
        encoded_partitions = canonical_bytes(entry["partition_path_bindings"])
        if reference_partitions is None:
            reference_partitions = encoded_partitions
        elif encoded_partitions != reference_partitions:
            raise CandidateStationaryFailure(HOLD_REQUEST, "roles 8--10 partition bindings differ")
    all_slots = [*request_paths, *output_paths]
    if len(all_slots) != 9 or len(set(all_slots)) != 9:
        raise CandidateStationaryFailure(HOLD_REQUEST, "roles 8--10 replay slots collide")
    if set(output_paths) & dependency_paths:
        raise CandidateStationaryFailure(HOLD_REQUEST, "planned output aliases an input")
    if any(os.path.lexists(path) for path in output_paths):
        raise CandidateStationaryFailure(HOLD_REQUEST, "planned output slot is not fresh")
    return tuple(request_paths), tuple(output_paths), frozenset(dependency_paths)


def _validate_result_blind_keys(value: Any, *, label: str) -> None:
    forbidden = (
        "artifact_sha",
        "expected_output",
        "expected_result",
        "observed",
        "output_sha",
        "production_result",
        "result_digest",
        "result_sha",
        "role8_result",
        "role9_result",
        "role10_result",
        "stream_sha",
    )
    for key in _walk_keys(value):
        lowered = key.lower()
        if any(fragment in lowered for fragment in forbidden):
            raise CandidateStationaryFailure(
                HOLD_REQUEST, f"{label}: result leakage key forbidden: {key}"
            )
    _validate_result_blind_string_values(value, code=HOLD_REQUEST, label=label)


def _validate_result_blind_string_values(
    value: Any,
    *,
    code: str,
    label: str,
) -> None:
    for field, string in _walk_string_values(value):
        if field == "status" and string in _ALLOWED_RESULT_METADATA_STRINGS:
            continue
        lowered = string.lower()
        if "result" in lowered or "observed" in lowered:
            raise CandidateStationaryFailure(
                code,
                f"{label}: result leakage string forbidden",
            )


def _load_request(request_path: Path, output_path: Path) -> tuple[dict[str, Any], ReplayProtocol]:
    request_snapshot = immutable_snapshot(request_path, cap=MAX_JSON_BYTES)
    request = _parse_canonical(request_snapshot.raw, label="request")
    _exact_keys(request, _REQUEST_KEYS, code=HOLD_REQUEST, label="request")
    _validate_result_blind_keys(request, label="request")
    if (
        request["schema"] != REQUEST_SCHEMA
        or request["status"] != REQUEST_STATUS
        or request["plan_entry_id"] != ROLE_NAME
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, "request boundary mismatch")
    role = _exact_keys(request["role"], _ROLE_KEYS, code=HOLD_REQUEST, label="request role")
    if role != {"role_id": ROLE_ID, "role_name": ROLE_NAME}:
        raise CandidateStationaryFailure(HOLD_REQUEST, "request role mismatch")
    plan_snapshot = _pin_snapshot(request["plan"], label="replay plan")
    plan = _parse_canonical(plan_snapshot.raw, label="replay plan")
    _exact_keys(plan, _PLAN_KEYS, code=HOLD_REQUEST, label="replay plan")
    _validate_result_blind_keys(plan, label="replay plan")
    if plan["schema"] != PLAN_SCHEMA or plan["status"] != PLAN_STATUS:
        raise CandidateStationaryFailure(HOLD_REQUEST, "replay-plan boundary mismatch")
    plan_claims = _require_false_boundary(
        plan["claim_boundary"], label="replay-plan claim boundary"
    )
    if set(plan_claims) != _PLAN_BUNDLE_CLAIM_KEYS:
        raise CandidateStationaryFailure(HOLD_REQUEST, "replay-plan claim keys mismatch")
    shared_context = _exact_keys(
        plan["shared_context"],
        _SHARED_CONTEXT_KEYS,
        code=HOLD_REQUEST,
        label="shared context",
    )
    for key in (
        "anti_vacuity_policy",
        "configuration",
        "factorization",
        "ideal_formula",
        "member_spec",
        "method_parameter_registry",
        "reference_density",
    ):
        _pin_without_schema(shared_context[key], label=f"shared context {key}")
    if (
        shared_context["member_identity_sha256"] != MEMBER_IDENTITY_SHA256
        or shared_context["anti_vacuity_policy"]["schema"] != ANTI_VACUITY_POLICY_SCHEMA
        or shared_context["anti_vacuity_policy"]["sha256"] != ANTI_VACUITY_POLICY_SHA256
        or not _is_sha256(shared_context["configuration_row_inventory_sha256"])
        or not _is_sha256(shared_context["partition_inventory_sha256"])
        or shared_context["member_spec"]["schema"] != MEMBER_SCHEMA
        or shared_context["member_spec"]["sha256"] != MEMBER_SHA256
        or shared_context["method_parameter_registry"]["schema"] != PARAMETER_SCHEMA
        or shared_context["method_parameter_registry"]["sha256"] != PARAMETER_SHA256
        or shared_context["configuration"]["schema"] != CONFIGURATION_SCHEMA
        or shared_context["reference_density"]["schema"] != REFERENCE_SCHEMA
        or shared_context["ideal_formula"]["schema"] != FORMULA_SCHEMA
        or shared_context["factorization"]["schema"] != FACTORIZATION_SCHEMA
        or shared_context["anti_vacuity_policy"]["path"] != ANTI_VACUITY_POLICY_RELATIVE_PATH
        or shared_context["configuration"]["path"] != CONFIGURATION_RELATIVE_PATH
        or shared_context["factorization"]["path"] != FACTORIZATION_RELATIVE_PATH
        or shared_context["ideal_formula"]["path"] != FORMULA_RELATIVE_PATH
        or shared_context["member_spec"]["path"] != MEMBER_RELATIVE_PATH
        or shared_context["method_parameter_registry"]["path"] != PARAMETER_RELATIVE_PATH
        or shared_context["reference_density"]["path"] != REFERENCE_RELATIVE_PATH
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, "shared-context authority mismatch")
    precommit_digest = _domain_digest(PRECOMMIT_CONTEXT_DOMAIN, shared_context)
    if (
        plan["shared_precommit_context_sha256"] != precommit_digest
        or request["shared_precommit_context_sha256"] != precommit_digest
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, "shared precommit digest mismatch")
    entries = plan["entries"]
    if (
        type(entries) is not list
        or len(entries) != 3
        or any(type(entry) is not dict for entry in entries)
        or [entry.get("role") for entry in entries] != [8, 9, 10]
        or [entry.get("entry_id") for entry in entries]
        != [
            "role8_raw_axis_formula_primitive",
            ROLE_NAME,
            "role10_killing_factor_geometry",
        ]
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, "replay-plan role ordering mismatch")
    for ordered_entry in entries:
        _exact_keys(
            ordered_entry,
            _PLAN_ENTRY_KEYS,
            code=HOLD_REQUEST,
            label=f"role-{ordered_entry['role']} plan entry",
        )
        ordered_projection = {
            key: value
            for key, value in ordered_entry.items()
            if key != "precommit_projection_sha256"
        }
        if ordered_entry["precommit_projection_sha256"] != _domain_digest(
            PRECOMMIT_PROJECTION_DOMAIN, ordered_projection
        ):
            raise CandidateStationaryFailure(
                HOLD_REQUEST, "ordered role precommit projection mismatch"
            )
    planned_request_paths, planned_output_paths, planned_dependency_paths = (
        _validate_all_plan_entries(entries, shared_context)
    )
    if set(planned_output_paths) & {
        request_snapshot.path,
        plan_snapshot.path,
        *planned_request_paths,
    }:
        raise CandidateStationaryFailure(HOLD_REQUEST, "planned output aliases protocol input")
    entry = entries[1]
    projection = {
        key: value for key, value in entry.items() if key != "precommit_projection_sha256"
    }
    if entry["precommit_projection_sha256"] != _domain_digest(
        PRECOMMIT_PROJECTION_DOMAIN, projection
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, "role-9 precommit projection mismatch")
    entry_request = _exact_keys(
        entry["request"], _ENTRY_REQUEST_KEYS, code=HOLD_REQUEST, label="planned request"
    )
    if entry_request != {
        "path": str(request_path),
        "schema": REQUEST_SCHEMA,
        "status": REQUEST_STATUS,
    }:
        raise CandidateStationaryFailure(HOLD_REQUEST, "planned request mismatch")
    outputs = _exact_keys(
        entry["outputs"], _ENTRY_OUTPUT_KEYS, code=HOLD_REQUEST, label="planned outputs"
    )
    artifact_output = _exact_keys(
        outputs["artifact"], _OUTPUT_KEYS, code=HOLD_REQUEST, label="planned artifact"
    )
    receipt_output = _exact_keys(
        outputs["validation_receipt"],
        _OUTPUT_KEYS,
        code=HOLD_REQUEST,
        label="planned validation receipt",
    )
    artifact_path = _absolute_lexical(
        artifact_output["path"], code=HOLD_REQUEST, label="planned artifact path"
    )
    receipt_path = _absolute_lexical(
        receipt_output["path"], code=HOLD_REQUEST, label="planned receipt path"
    )
    if (
        artifact_output["schema"] != OUTPUT_SCHEMA
        or receipt_output["schema"] != RECEIPT_SCHEMA
        or artifact_path != output_path
        or artifact_path == receipt_path
        or os.path.lexists(artifact_path)
        or os.path.lexists(receipt_path)
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, "planned output slots are not fresh")
    runtime_closure = _exact_keys(
        entry["implementation_runtime_closure"],
        _RUNTIME_CLOSURE_KEYS,
        code=HOLD_REQUEST,
        label="runtime closure",
    )
    _exact_keys(
        runtime_closure["runtime_requirements"],
        _RUNTIME_KEYS,
        code=HOLD_REQUEST,
        label="runtime requirements",
    )
    invocations = _exact_keys(
        entry["invocations"], _INVOCATIONS_KEYS, code=HOLD_REQUEST, label="invocations"
    )
    for label, invocation in invocations.items():
        _exact_keys(invocation, _INVOCATION_KEYS, code=HOLD_REQUEST, label=f"{label} invocation")
        if (
            type(invocation["cwd"]) is not str
            or not Path(invocation["cwd"]).is_absolute()
            or type(invocation["argv"]) is not list
            or any(type(argument) is not str or not argument for argument in invocation["argv"])
        ):
            raise CandidateStationaryFailure(HOLD_REQUEST, f"{label} invocation type mismatch")
    producer_path = _absolute_lexical(
        runtime_closure["producer"]["path"], code=HOLD_REQUEST, label="producer path"
    )
    verifier_path = _absolute_lexical(
        runtime_closure["verifier"]["path"], code=HOLD_REQUEST, label="verifier path"
    )
    expected_producer_argv = [
        sys.executable,
        str(producer_path),
        "--request",
        str(request_path),
        "--output",
        str(artifact_path),
    ]
    expected_verifier_argv = [
        sys.executable,
        str(verifier_path),
        "--request",
        str(request_path),
        "--output",
        str(artifact_path),
        "--receipt",
        str(receipt_path),
    ]
    if (
        invocations["producer"]["argv"] != expected_producer_argv
        or invocations["verifier"]["argv"] != expected_verifier_argv
        or invocations["producer"]["cwd"] != invocations["verifier"]["cwd"]
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, "planned invocation mismatch")
    authorities = _exact_keys(
        entry["input_authorities"],
        _INPUT_AUTHORITY_ROLES,
        code=HOLD_REQUEST,
        label="planned input authorities",
    )
    context_role_map = {
        "anti_vacuity_policy": "anti_vacuity_policy",
        "configuration": "configuration",
        "factorization": "factorization",
        "ideal_formula": "ideal_formula",
        "member_spec": "member_spec",
        "method_parameters": "method_parameter_registry",
        "reference_density": "reference_density",
    }
    for authority_role, context_role in context_role_map.items():
        _same_logical_authority(
            authorities[authority_role],
            _pin_without_schema(shared_context[context_role], label=f"shared {context_role}"),
            label=f"entry/shared {authority_role}",
        )
    commitment_snapshot = _pin_snapshot(
        request["external_predecessor_commitment"], label="external commitment"
    )
    commitment = _parse_canonical(commitment_snapshot.raw, label="external commitment")
    _exact_keys(commitment, _COMMITMENT_KEYS, code=HOLD_REQUEST, label="external commitment")
    _validate_result_blind_string_values(
        commitment,
        code=HOLD_REQUEST,
        label="external commitment",
    )
    bundle_snapshot = _pin_snapshot(commitment["candidate_bundle"], label="candidate bundle")
    bundle = _parse_canonical(bundle_snapshot.raw, label="candidate bundle")
    _exact_keys(bundle, _BUNDLE_KEYS, code=HOLD_REQUEST, label="candidate bundle")
    _validate_result_blind_keys(bundle, label="candidate bundle")
    if bundle["schema"] != BUNDLE_SCHEMA or bundle["status"] != BUNDLE_STATUS:
        raise CandidateStationaryFailure(HOLD_REQUEST, "candidate-bundle boundary mismatch")
    bundle_claims = _require_false_boundary(
        bundle["claim_boundary"], label="candidate-bundle claim boundary"
    )
    if set(bundle_claims) != _PLAN_BUNDLE_CLAIM_KEYS:
        raise CandidateStationaryFailure(HOLD_REQUEST, "candidate-bundle claim keys mismatch")
    _same_pin(bundle["replay_plan"], request["plan"], label="bundle replay plan")
    _same_pin(bundle["member_spec"], authorities["member_spec"], label="bundle member")
    _same_pin(
        bundle["method_parameter_registry"],
        authorities["method_parameters"],
        label="bundle method registry",
    )
    if bundle["shared_precommit_context_sha256"] != precommit_digest:
        raise CandidateStationaryFailure(HOLD_REQUEST, "candidate-bundle context mismatch")
    if commitment["schema"] != COMMITMENT_SCHEMA or commitment["status"] != COMMITMENT_STATUS:
        raise CandidateStationaryFailure(HOLD_REQUEST, "commitment boundary mismatch")
    authentication = _exact_keys(
        commitment["authentication"],
        _AUTHENTICATION_KEYS,
        code=HOLD_REQUEST,
        label="commitment authentication",
    )
    authority = _exact_keys(
        commitment["authority"], _AUTHORITY_KEYS, code=HOLD_REQUEST, label="authority"
    )
    ordering = _exact_keys(
        commitment["ordering"], _ORDERING_KEYS, code=HOLD_REQUEST, label="ordering"
    )
    claims = _exact_keys(
        commitment["claim_boundary"],
        _COMMITMENT_CLAIM_KEYS,
        code=HOLD_REQUEST,
        label="commitment claim boundary",
    )
    if (
        authentication["authentication_class"] not in ACCEPTED_AUTHENTICATION_CLASSES
        or authentication["structural_validation_only"] is not True
        or not _is_nonempty_string(authentication["evidence_identifier"])
        or any(not _is_nonempty_string(value) for value in authority.values())
        or any(value is not True for value in ordering.values())
        or any(value is not False for value in claims.values())
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, "commitment structure mismatch")
    _same_pin(
        commitment["candidate_bundle"],
        {"path": str(bundle_snapshot.path), "sha256": bundle_snapshot.sha256},
        label="commitment candidate bundle",
    )
    message_projection = {
        "authority": authority,
        "candidate_bundle": commitment["candidate_bundle"],
        "claim_boundary": claims,
        "ordering": ordering,
    }
    if commitment["commitment_message_sha256"] != _domain_digest(
        COMMITMENT_MESSAGE_DOMAIN, message_projection
    ):
        raise CandidateStationaryFailure(HOLD_REQUEST, "commitment message digest mismatch")
    replay_digest = _domain_digest(
        REPLAY_CONTEXT_DOMAIN,
        {
            "external_predecessor_commitment_sha256": commitment_snapshot.sha256,
            "replay_plan_sha256": plan_snapshot.sha256,
            "shared_precommit_context_sha256": precommit_digest,
        },
    )
    if request["shared_replay_context_sha256"] != replay_digest:
        raise CandidateStationaryFailure(HOLD_REQUEST, "shared replay digest mismatch")
    if set(planned_output_paths) & {
        request_snapshot.path,
        plan_snapshot.path,
        bundle_snapshot.path,
        commitment_snapshot.path,
        *planned_request_paths,
        *planned_dependency_paths,
    }:
        raise CandidateStationaryFailure(HOLD_REQUEST, "planned output aliases replay input")
    expanded = {
        "code_inputs": {
            "producer": runtime_closure["producer"],
            "verifier": runtime_closure["verifier"],
        },
        "input_authorities": authorities,
        "method_selection": entry["method_selection"],
        "output": artifact_output,
        "partitions": entry["partition_path_bindings"],
        "runtime_requirements": runtime_closure["runtime_requirements"],
        "schema": REQUEST_SCHEMA,
        "status": REQUEST_STATUS,
    }
    protocol = ReplayProtocol(
        request=request,
        request_snapshot=request_snapshot,
        plan=plan,
        plan_snapshot=plan_snapshot,
        bundle=bundle,
        bundle_snapshot=bundle_snapshot,
        commitment=commitment,
        commitment_snapshot=commitment_snapshot,
        entry=entry,
        artifact_path=artifact_path,
        receipt_path=receipt_path,
        shared_precommit_context_sha256=precommit_digest,
        shared_replay_context_sha256=replay_digest,
    )
    return expanded, protocol


def _walk_keys(value: Any) -> list[str]:
    result: list[str] = []
    if type(value) is dict:
        for key, item in value.items():
            result.append(key)
            result.extend(_walk_keys(item))
    elif type(value) is list:
        for item in value:
            result.extend(_walk_keys(item))
    return result


def _walk_string_values(
    value: Any,
    field: str | None = None,
) -> list[tuple[str | None, str]]:
    result: list[tuple[str | None, str]] = []
    if type(value) is str:
        result.append((field, value))
    elif type(value) is dict:
        for key, item in value.items():
            result.extend(_walk_string_values(item, key))
    elif type(value) is list:
        for item in value:
            result.extend(_walk_string_values(item, field))
    return result


def _reject_result_observed_keys(value: Any, *, code: str, label: str) -> None:
    offending = sorted(
        {key for key in _walk_keys(value) if "result" in key.lower() or "observed" in key.lower()}
    )
    if offending:
        raise CandidateStationaryFailure(
            code, f"{label}: result/observed metadata key forbidden: {offending[0]}"
        )


def _binding_matches_pin(binding: Any, pin: Any, *, label: str, code: str = HOLD_INPUT) -> None:
    current = _exact_keys(binding, _PIN_KEYS, code=code, label=label)
    requested = _exact_keys(pin, _PIN_KEYS, code=HOLD_REQUEST, label=f"{label} request pin")
    relative = current["path"]
    if type(relative) is not str or not relative:
        raise CandidateStationaryFailure(code, f"{label}: invalid relative path")
    pure = PurePosixPath(relative)
    absolute = _absolute_lexical(
        requested["path"], code=HOLD_REQUEST, label=f"{label} request path"
    )
    if (
        pure.is_absolute()
        or ".." in pure.parts
        or tuple(absolute.parts[-len(pure.parts) :]) != pure.parts
        or current["sha256"] != requested["sha256"]
    ):
        raise CandidateStationaryFailure(code, f"{label}: request binding mismatch")


def _validate_configuration_nested(
    request: dict[str, Any],
    configuration: dict[str, Any],
    snapshots: dict[str, Snapshot],
    initial_source: dict[str, Any],
) -> None:
    authority = _exact_keys(
        configuration["authority"],
        _CONFIGURATION_AUTHORITY_KEYS,
        code=HOLD_INPUT,
        label="configuration authority",
    )
    if canonical_bytes(authority) != canonical_bytes(_EXPECTED_CONFIGURATION_AUTHORITY):
        raise CandidateStationaryFailure(HOLD_INPUT, "configuration authority mismatch")
    for role, prefix in (
        ("configuration_design", "design"),
        ("configuration_implementation", "implementation"),
        ("configuration_test", "test"),
    ):
        binding = {
            "path": authority[f"{prefix}_path"],
            "sha256": authority[f"{prefix}_sha256"],
        }
        _binding_matches_pin(
            binding,
            request["input_authorities"][role],
            label=f"configuration {prefix} authority",
        )
        if snapshots[role].sha256 != binding["sha256"]:
            raise CandidateStationaryFailure(
                HOLD_INPUT, f"configuration {prefix} authority bytes mismatch"
            )
    initial = _exact_keys(
        configuration["initial_geometry"],
        _INITIAL_GEOMETRY_KEYS,
        code=HOLD_INPUT,
        label="initial geometry",
    )
    if (
        initial["source_path"] != "artifacts/data/physical_initial_analytic_source_v1.json"
        or initial["source_schema"] != CONFIGURATION_INITIAL_GEOMETRY_SCHEMA
        or initial["source_sha256"]
        != "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "initial geometry source pin mismatch")
    initial_binding = {
        "path": initial["source_path"],
        "sha256": initial["source_sha256"],
    }
    _binding_matches_pin(
        initial_binding,
        request["input_authorities"]["configuration_initial_geometry"],
        label="configuration initial geometry source",
    )
    if snapshots["configuration_initial_geometry"].sha256 != initial["source_sha256"]:
        raise CandidateStationaryFailure(
            HOLD_INPUT, "configuration initial geometry bytes mismatch"
        )
    _exact_keys(
        initial_source,
        _INITIAL_GEOMETRY_SOURCE_KEYS,
        code=HOLD_INPUT,
        label="configuration initial geometry source",
    )
    if (
        initial_source["schema"] != CONFIGURATION_INITIAL_GEOMETRY_SCHEMA
        or initial_source["scope"] != "physical_initial_law_only_no_control_no_budget"
        or initial_source["coordinate_order"] != list(COORDINATES)
        or initial_source["physical_dimension"] != 2
        or initial_source["quotient_dimension"] != 3
        or initial_source["analytic_total_mass_exact"] != "1/1"
        or initial_source["transverse_period_exact"] != "1/1"
        or initial_source["periodic_coordinate"] != "relative_perpendicular"
        or initial_source["shared_normalizer_across_cells_and_axes"] is not True
        or any(
            initial_source[key] != initial[key]
            for key in (
                "construction",
                "half_width_binary64_hex",
                "normalization",
                "periodic_wrap",
                "shape_definition",
                "starts_binary64_hex",
            )
        )
    ):
        raise CandidateStationaryFailure(
            HOLD_INPUT, "configuration initial geometry semantics mismatch"
        )
    starts = _exact_keys(
        initial["starts_binary64_hex"],
        set(COORDINATES),
        code=HOLD_INPUT,
        label="initial geometry starts",
    )
    for coordinate, value in starts.items():
        _binary64_fraction(value, label=f"initial {coordinate}")
    contracts = _exact_keys(
        configuration["axis_construction_contracts"],
        {
            "cell_centred_periodic_base",
            "cell_centred_periodic_half_shift",
            "cell_centred_reflecting",
            "vertex_centred_reflecting_dual",
        },
        code=HOLD_INPUT,
        label="axis construction contracts",
    )
    for name, contract in contracts.items():
        expected_keys = (
            _PERIODIC_AXIS_CONTRACT_KEYS
            if name
            in {
                "cell_centred_periodic_base",
                "cell_centred_periodic_half_shift",
            }
            else _AXIS_CONTRACT_KEYS
        )
        _exact_keys(
            contract,
            expected_keys,
            code=HOLD_INPUT,
            label=f"axis construction contract {name}",
        )
    rows = configuration["configurations"]
    if type(rows) is not list:
        raise CandidateStationaryFailure(HOLD_INPUT, "configuration rows missing")
    alignment_counts: dict[str, int] = {}
    for index, row in enumerate(rows):
        _exact_keys(
            row,
            _CONFIGURATION_ROW_KEYS,
            code=HOLD_INPUT,
            label=f"configuration row {index}",
        )
        if type(row["label"]) is not str or type(row["purpose"]) is not str:
            raise CandidateStationaryFailure(HOLD_INPUT, "configuration row text mismatch")
        shape = row["shape"]
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(value) is not int or value < 2 for value in shape)
            or type(row["expected_states"]) is not int
            or row["expected_states"] != math.prod(shape)
        ):
            raise CandidateStationaryFailure(HOLD_INPUT, "configuration row shape mismatch")
        for axis_index, coordinate in enumerate(COORDINATES):
            axis = row[coordinate]
            if type(axis) is not dict:
                raise CandidateStationaryFailure(HOLD_INPUT, "configuration axis missing")
            alignment = axis.get("alignment")
            if alignment in {
                "cell_centred_reflecting",
                "vertex_centred_reflecting_dual",
            }:
                _exact_keys(
                    axis,
                    _REFLECTING_AXIS_KEYS,
                    code=HOLD_INPUT,
                    label=f"configuration row {index} {coordinate}",
                )
                _binary64_fraction(axis["lower_binary64_hex"], label="axis lower")
                _binary64_fraction(axis["upper_binary64_hex"], label="axis upper")
            elif alignment in {
                "cell_centred_periodic_base",
                "cell_centred_periodic_half_shift",
            }:
                _exact_keys(
                    axis,
                    _PERIODIC_AXIS_KEYS,
                    code=HOLD_INPUT,
                    label=f"configuration row {index} {coordinate}",
                )
                _fraction(
                    axis["periodic_shift_exact"],
                    code=HOLD_INPUT,
                    label="periodic shift",
                )
            else:
                raise CandidateStationaryFailure(HOLD_INPUT, "configuration alignment mismatch")
            if type(axis["size"]) is not int or axis["size"] != shape[axis_index]:
                raise CandidateStationaryFailure(HOLD_INPUT, "configuration axis size mismatch")
            alignment_counts[alignment] = alignment_counts.get(alignment, 0) + 1
    if alignment_counts != {
        "cell_centred_periodic_base": 10,
        "cell_centred_periodic_half_shift": 2,
        "cell_centred_reflecting": 20,
        "vertex_centred_reflecting_dual": 4,
    }:
        raise CandidateStationaryFailure(HOLD_INPUT, "configuration alignment counts mismatch")


def _validate_factorization_authority(
    request: dict[str, Any],
    factorization: dict[str, Any],
    snapshot: Snapshot,
    snapshots: dict[str, Snapshot],
    initial_partition_bundle: dict[str, Any],
    killing_geometry: dict[str, Any],
) -> None:
    _exact_keys(
        factorization,
        _FACTORIZATION_KEYS,
        code=HOLD_INPUT,
        label="factorization",
    )
    claims = factorization["claim_boundary"]
    expected_path = PurePosixPath(FACTORIZATION_RELATIVE_PATH)
    if (
        snapshot.sha256 != FACTORIZATION_SHA256
        or tuple(snapshot.path.parts[-len(expected_path.parts) :]) != expected_path.parts
        or factorization["schema"] != FACTORIZATION_SCHEMA
        or factorization["status"]
        != (
            "OUTCOME_FREE_CONTROL_FREE_FACTORIZATION_CANDIDATE_ONLY_NOT_EXTERNALLY_"
            "COMMITTED_NO_NUMERIC_ENCLOSURES_NO_CONCRETE_KILLING"
        )
        or type(claims) is not dict
        or set(claims) != _PARAMETER_CLAIM_KEYS
        or any(value is not False for value in claims.values())
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "factorization authority mismatch")
    outcome = factorization["outcome_free_contract"]
    if canonical_bytes(outcome) != canonical_bytes(
        {
            "budget_present": False,
            "concrete_killing_tensor_present": False,
            "control_weights_present": False,
            "external_commitment_present": False,
            "numeric_enclosure_payload_present": False,
            "primitive_source_only": True,
            "production_bridge_present": False,
        }
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "factorization outcome boundary mismatch")
    source_pins = _exact_keys(
        factorization["source_pins"],
        {
            "configuration_source",
            "initial_partition_bundle",
            "killing_geometry_source",
        },
        code=HOLD_INPUT,
        label="factorization source pins",
    )
    configuration_pin = _exact_keys(
        source_pins["configuration_source"],
        {"path", "schema", "sha256"},
        code=HOLD_INPUT,
        label="factorization configuration source",
    )
    if configuration_pin["schema"] != CONFIGURATION_SCHEMA:
        raise CandidateStationaryFailure(HOLD_INPUT, "factorization configuration schema")
    _binding_matches_pin(
        {"path": configuration_pin["path"], "sha256": configuration_pin["sha256"]},
        request["input_authorities"]["configuration"],
        label="factorization configuration source",
    )
    if snapshots["configuration"].sha256 != configuration_pin["sha256"]:
        raise CandidateStationaryFailure(HOLD_INPUT, "factorization configuration bytes mismatch")
    expected_other_pins = {
        "initial_partition_bundle": {
            "path": "artifacts/data/physical_production_initial_stream_v1/bundle.json",
            "schema": "encounter_control_free_production_initial_stream_v1",
            "sha256": "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e",
        },
        "killing_geometry_source": {
            "path": "artifacts/data/physical_killing_geometry_source_v1.json",
            "schema": "encounter_physical_killing_geometry_source_v1",
            "sha256": "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
        },
    }
    for name, expected in expected_other_pins.items():
        current = _exact_keys(
            source_pins[name],
            {"path", "schema", "sha256"},
            code=HOLD_INPUT,
            label=f"factorization {name}",
        )
        if canonical_bytes(current) != canonical_bytes(expected):
            raise CandidateStationaryFailure(HOLD_INPUT, f"factorization {name} mismatch")
        role = (
            "factorization_initial_partition_bundle"
            if name == "initial_partition_bundle"
            else "factorization_killing_geometry"
        )
        _binding_matches_pin(
            {"path": current["path"], "sha256": current["sha256"]},
            request["input_authorities"][role],
            label=f"factorization {name}",
        )
        if snapshots[role].sha256 != current["sha256"]:
            raise CandidateStationaryFailure(HOLD_INPUT, f"factorization {name} bytes mismatch")
    _exact_keys(
        initial_partition_bundle,
        _INITIAL_PARTITION_BUNDLE_KEYS,
        code=HOLD_INPUT,
        label="factorization initial partition bundle",
    )
    if (
        initial_partition_bundle["schema"] != FACTORIZATION_INITIAL_PARTITION_SCHEMA
        or initial_partition_bundle["status"] != FACTORIZATION_INITIAL_PARTITION_STATUS
        or initial_partition_bundle["configuration_sha256"] != snapshots["configuration"].sha256
        or initial_partition_bundle["analytic_source_sha256"]
        != snapshots["configuration_initial_geometry"].sha256
        or initial_partition_bundle["configuration_count"] != EXPECTED_CONFIGURATION_COUNT
        or initial_partition_bundle["total_state_workload"] != EXPECTED_TOTAL_STATES
    ):
        raise CandidateStationaryFailure(
            HOLD_INPUT, "factorization initial partition bundle semantics mismatch"
        )
    _exact_keys(
        killing_geometry,
        _KILLING_GEOMETRY_SOURCE_KEYS,
        code=HOLD_INPUT,
        label="factorization killing geometry",
    )
    killing_configuration = _exact_keys(
        killing_geometry["configuration_bundle"],
        {
            "configuration_path",
            "configuration_sha256",
            "partition_bundle_path",
            "partition_bundle_sha256",
        },
        code=HOLD_INPUT,
        label="killing geometry configuration bundle",
    )
    if (
        killing_geometry["schema"] != FACTORIZATION_KILLING_GEOMETRY_SCHEMA
        or killing_geometry["status"] != FACTORIZATION_KILLING_GEOMETRY_STATUS
        or killing_geometry["coordinate_order"] != list(COORDINATES)
        or killing_geometry["physical_dimension"] != 2
        or killing_geometry["quotient_dimension"] != 3
    ):
        raise CandidateStationaryFailure(
            HOLD_INPUT, "factorization killing geometry semantics mismatch"
        )
    _binding_matches_pin(
        {
            "path": killing_configuration["configuration_path"],
            "sha256": killing_configuration["configuration_sha256"],
        },
        request["input_authorities"]["configuration"],
        label="killing geometry configuration source",
    )
    _binding_matches_pin(
        {
            "path": killing_configuration["partition_bundle_path"],
            "sha256": killing_configuration["partition_bundle_sha256"],
        },
        request["input_authorities"]["factorization_initial_partition_bundle"],
        label="killing geometry initial partition bundle",
    )
    if (
        killing_configuration["configuration_sha256"] != snapshots["configuration"].sha256
        or killing_configuration["partition_bundle_sha256"]
        != snapshots["factorization_initial_partition_bundle"].sha256
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "killing geometry dependency bytes mismatch")


def _validate_scientific_authorities(
    request: dict[str, Any],
    reference: dict[str, Any],
    formula: dict[str, Any],
    configuration: dict[str, Any],
    factorization: dict[str, Any],
    factorization_snapshot: Snapshot,
    snapshots: dict[str, Snapshot],
    initial_source: dict[str, Any],
    initial_partition_bundle: dict[str, Any],
    killing_geometry: dict[str, Any],
) -> None:
    _exact_keys(reference, _REFERENCE_KEYS, code=HOLD_INPUT, label="reference")
    _exact_keys(formula, _FORMULA_KEYS, code=HOLD_INPUT, label="formula")
    _exact_keys(configuration, _CONFIGURATION_KEYS, code=HOLD_INPUT, label="configuration")
    _validate_configuration_nested(request, configuration, snapshots, initial_source)
    _validate_factorization_authority(
        request,
        factorization,
        factorization_snapshot,
        snapshots,
        initial_partition_bundle,
        killing_geometry,
    )
    if (
        reference["schema"] != REFERENCE_SCHEMA
        or reference["status"]
        != "FROZEN_CONTROL_FREE_REFERENCE_DENSITY_AUTHORITY_ONLY_NO_COMPLETE_C0_C1_C2"
        or reference["coordinate_order"] != list(COORDINATES)
        or reference["boundary_and_measure"]
        != {
            "finite_nonperiodic_faces": "reflecting_zero_flux_approximants",
            "finite_periodic_coordinate": "relative_perpendicular_mod_W",
            "physical_cell_measure": ("d_midpoint*d_relative_parallel*d_relative_perpendicular"),
            "target_nonperiodic_domain": "R_times_R",
            "target_periodic_domain": "T_W",
        }
        or reference["diffusion_and_drift"]
        != {
            "diffusion_diagonal": [
                "particle_diffusion/2",
                "2*particle_diffusion",
                "2*particle_diffusion",
            ],
            "drift": [
                "-ou_stiffness*(midpoint-ou_mean)",
                "-ou_stiffness*relative_parallel",
                "0/1",
            ],
        }
        or reference["normalization"]
        != {
            "box_mass": "M_L=integral_Omega_L_pi_dx",
            "conditional_box_renormalization_used": False,
            "full_space_normalizer": "Z=2*pi*particle_diffusion*W/ou_stiffness",
            "periodic_factor": "1/W",
            "reference_density": (
                "pi=Z^-1*exp[-ou_stiffness*(midpoint-ou_mean)^2/"
                "particle_diffusion-ou_stiffness*relative_parallel^2/"
                "(4*particle_diffusion)]"
            ),
            "restricted_density_retains_global_normalization": True,
        }
        or reference["normalization"]["conditional_box_renormalization_used"] is not False
        or reference["normalization"]["restricted_density_retains_global_normalization"] is not True
        or reference["unit_table"]
        != {
            "box_mass_M_L": "dimensionless_probability",
            "diffusion_coefficients": "length_squared_per_time",
            "full_space_normalizer_Z": "length_cubed",
            "ou_stiffness": "inverse_time",
            "physical_cell_measure": "length_cubed",
            "reference_density_pi": "inverse_length_cubed",
            "spatial_coordinates": "length",
            "transverse_period_W": "length",
        }
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "reference semantics mismatch")
    reference_claims = reference["claim_boundary"]
    if (
        type(reference_claims) is not dict
        or set(reference_claims)
        != {
            "box_truncation_proved",
            "complete_C0",
            "complete_C1",
            "complete_C2",
            "complete_C3",
            "continuum_topology_proved",
            "production_bridge_accepted",
            "release_eligible",
        }
        or any(value is not False for value in reference_claims.values())
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "reference claim boundary mismatch")
    reference_pins = _exact_keys(
        reference["source_pins"],
        {"c0_mathematical_source", "configuration_source"},
        code=HOLD_INPUT,
        label="reference source pins",
    )
    c0_pin = _exact_keys(
        reference_pins["c0_mathematical_source"],
        _PIN_KEYS,
        code=HOLD_INPUT,
        label="reference C0 source pin",
    )
    if c0_pin != {
        "path": "artifacts/data/continuum_c0_mathematical_source_v2.json",
        "sha256": "522bd667e5f6fd6a4d12f270f0c2f4b9e86be9b207d471961d4f67db972df559",
    }:
        raise CandidateStationaryFailure(HOLD_INPUT, "reference C0 source pin mismatch")
    _binding_matches_pin(
        reference_pins["configuration_source"],
        request["input_authorities"]["configuration"],
        label="reference configuration source",
    )

    if (
        formula["schema"] != FORMULA_SCHEMA
        or formula["status"]
        != "FROZEN_CONTROL_FREE_IDEAL_FORMULA_AUTHORITY_ONLY_NO_PRODUCTION_ACCEPTANCE"
        or formula["potential_formulae"]
        != {
            "midpoint": "ou_stiffness*(x-ou_mean)^2/particle_diffusion",
            "relative_parallel": "ou_stiffness*x^2/(4*particle_diffusion)",
            "relative_perpendicular": "0/1",
        }
        or formula["member_semantics"]
        != {
            "common_flux_uses_one_formula_defined_exact_value": True,
            "formula_defined_member_is_independent_of_production_centres": True,
            "global_gauge_is_single_scalar_per_configuration": True,
            "one_correlated_distinguished_member_required": True,
        }
        or any(
            formula["member_semantics"][key] is not True
            for key in (
                "common_flux_uses_one_formula_defined_exact_value",
                "formula_defined_member_is_independent_of_production_centres",
                "global_gauge_is_single_scalar_per_configuration",
                "one_correlated_distinguished_member_required",
            )
        )
        or canonical_bytes(formula["formulae"]) != canonical_bytes(_EXPECTED_FORMULAE)
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "formula semantics mismatch")
    formula_claims = formula["claim_boundary"]
    if (
        type(formula_claims) is not dict
        or set(formula_claims)
        != {
            "binary64_centres_define_ideal_member",
            "complete_C0",
            "complete_C1",
            "complete_C2",
            "every_interval_endpoint_combination_is_a_model",
            "production_bridge_accepted",
            "release_eligible",
        }
        or any(value is not False for value in formula_claims.values())
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "formula claim boundary mismatch")
    formula_pins = _exact_keys(
        formula["source_pins"],
        {"c0_mathematical_source", "production_bridge_design"},
        code=HOLD_INPUT,
        label="formula source pins",
    )
    expected_formula_pins = {
        "c0_mathematical_source": {
            "path": "artifacts/data/continuum_c0_mathematical_source_v2.json",
            "sha256": "522bd667e5f6fd6a4d12f270f0c2f4b9e86be9b207d471961d4f67db972df559",
        },
        "production_bridge_design": {
            "path": "notes/continuum_c1_production_gauge_killing_bridge_design_v1.md",
            "sha256": "d23c088f917832bb9d8078a046133556e8ee8547d8a062d3102a922881ba67e4",
        },
    }
    for name, expected in expected_formula_pins.items():
        current = _exact_keys(
            formula_pins[name], _PIN_KEYS, code=HOLD_INPUT, label=f"formula {name}"
        )
        if current != expected:
            raise CandidateStationaryFailure(HOLD_INPUT, f"formula {name} mismatch")

    dynamics = _exact_keys(
        configuration["dynamics"], _DYNAMICS_KEYS, code=HOLD_INPUT, label="dynamics"
    )
    rows = configuration["configurations"]
    if (
        configuration["schema"] != CONFIGURATION_SCHEMA
        or configuration["status"] != "CONTROL_FREE_GEOMETRY_SPEC_ONLY_NOT_F0_NOT_F1"
        or configuration["scope"] != "physical_d2_control_free_axis_and_initial_geometry_only"
        or configuration["workload_semantics"]
        != "sum_of_state_counts_across_the_12_prescribed_axis_triples_for_one_future_control"
        or configuration["authorizes_scientific_execution"] is not False
        or configuration["contains_budget_value"] is not False
        or configuration["contains_control_values"] is not False
        or configuration["coordinate_order"] != list(COORDINATES)
        or configuration["physical_dimension"] != 2
        or configuration["quotient_dimension"] != 3
        or type(rows) is not list
        or type(configuration["configuration_count"]) is not int
        or configuration["configuration_count"] != EXPECTED_CONFIGURATION_COUNT
        or len(rows) != EXPECTED_CONFIGURATION_COUNT
        or configuration["configuration_order"]
        != [row.get("label") if type(row) is dict else None for row in rows]
        or type(configuration["total_state_workload"]) is not int
        or configuration["total_state_workload"] != EXPECTED_TOTAL_STATES
        or sum(row["expected_states"] for row in rows) != EXPECTED_TOTAL_STATES
        or dynamics["directed_precision_bits"] != 192
        or dynamics["midpoint_diffusion_formula"] != "particle_diffusion/2"
        or dynamics["midpoint_potential_formula"]
        != "ou_stiffness*(x-ou_mean)^2/(2*midpoint_diffusion)"
        or dynamics["relative_diffusion_formula"] != "2*particle_diffusion"
        or dynamics["relative_parallel_mean_exact"] != "0/1"
        or dynamics["relative_parallel_potential_formula"]
        != "ou_stiffness*x^2/(2*relative_diffusion)"
        or dynamics["relative_perpendicular_potential_formula"] != "0/1"
        or dynamics["transverse_domain_start_exact"] != "-1/2"
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "configuration semantics mismatch")
    parameters = _exact_keys(
        reference["physical_parameter_bundle"],
        {
            "ou_mean_binary64_hex",
            "ou_stiffness_binary64_hex",
            "particle_diffusion_binary64_hex",
            "physical_dimension",
            "quotient_dimension",
            "transverse_period_exact",
        },
        code=HOLD_INPUT,
        label="physical parameter bundle",
    )
    if (
        parameters["physical_dimension"] != 2
        or parameters["quotient_dimension"] != 3
        or any(
            dynamics[name] != parameters[name]
            for name in (
                "ou_mean_binary64_hex",
                "ou_stiffness_binary64_hex",
                "particle_diffusion_binary64_hex",
                "transverse_period_exact",
            )
        )
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "configuration parameter binding mismatch")
    _binary64_fraction(parameters["ou_mean_binary64_hex"], label="OU mean")
    _binary64_fraction(parameters["ou_stiffness_binary64_hex"], label="OU stiffness")
    _binary64_fraction(parameters["particle_diffusion_binary64_hex"], label="diffusion")
    _fraction(parameters["transverse_period_exact"], label="transverse period")
    if factorization["contact_geometry"]["transverse_period_exact"] != parameters[
        "transverse_period_exact"
    ] or factorization["coordinate_and_measure_contract"]["coordinate_order"] != list(COORDINATES):
        raise CandidateStationaryFailure(HOLD_INPUT, "factorization geometry binding mismatch")


def _validate_member_and_partitions(
    request: dict[str, Any],
    member: dict[str, Any],
    reference: dict[str, Any],
    configuration: dict[str, Any],
) -> tuple[list[tuple[dict[str, Any], list[dict[str, Any]]]], list[dict[str, str]]]:
    _exact_keys(member, _MEMBER_KEYS, code=HOLD_MEMBER, label="member")
    member_claims = member["claim_boundary"]
    if (
        member["schema"] != MEMBER_SCHEMA
        or member["status"] != MEMBER_STATUS
        or type(member_claims) is not dict
        or set(member_claims) != _PARAMETER_CLAIM_KEYS
        or any(value is not False for value in member_claims.values())
    ):
        raise CandidateStationaryFailure(HOLD_MEMBER, "candidate member boundary mismatch")
    lineage = _exact_keys(
        member["source_lineage_evidence"],
        _LINEAGE_KEYS,
        code=HOLD_MEMBER,
        label="member source lineage",
    )
    if canonical_bytes(lineage) != canonical_bytes(_EXPECTED_SOURCE_LINEAGE):
        raise CandidateStationaryFailure(HOLD_MEMBER, "candidate member lineage mismatch")
    if reference.get("schema") != REFERENCE_SCHEMA:
        raise CandidateStationaryFailure(HOLD_INPUT, "reference schema mismatch")
    if configuration.get("schema") != CONFIGURATION_SCHEMA:
        raise CandidateStationaryFailure(HOLD_INPUT, "configuration schema mismatch")
    parameters = reference.get("physical_parameter_bundle")
    rows = configuration.get("configurations")
    bindings = member.get("n0_sequence_bindings")
    order = member.get("configuration_order")
    semantics = member.get("configuration_semantic_ids")
    if (
        type(parameters) is not dict
        or type(rows) is not list
        or type(bindings) is not list
        or type(order) is not list
        or type(semantics) is not list
        or len(rows) != EXPECTED_CONFIGURATION_COUNT
        or not len(rows) == len(bindings) == len(order) == len(semantics)
    ):
        raise CandidateStationaryFailure(HOLD_MEMBER, "candidate cardinality mismatch")
    member_semantics = member.get("member_semantics")
    expected_member_semantics = {
        "configuration_count": EXPECTED_CONFIGURATION_COUNT,
        "configuration_rows_are_finite_anchors": True,
        "coordinate_order": list(COORDINATES),
        "every_cartesian_interval_endpoint_combination_is_a_model": False,
        "one_formula_defined_correlated_member_per_configuration": True,
        "physical_dimension": 2,
        "quotient_dimension": 3,
        "scalar_convention": "complex_inner_product_conjugate_first_factor",
    }
    if (
        type(member_semantics) is not dict
        or type(member_semantics.get("configuration_count")) is not int
        or type(member_semantics.get("physical_dimension")) is not int
        or type(member_semantics.get("quotient_dimension")) is not int
        or type(member_semantics.get("configuration_rows_are_finite_anchors")) is not bool
        or type(member_semantics.get("every_cartesian_interval_endpoint_combination_is_a_model"))
        is not bool
        or type(member_semantics.get("one_formula_defined_correlated_member_per_configuration"))
        is not bool
        or type(member_semantics.get("coordinate_order")) is not list
        or any(
            not _is_nonempty_string(value) for value in member_semantics.get("coordinate_order", [])
        )
        or not _is_nonempty_string(member_semantics.get("scalar_convention"))
        or member_semantics != expected_member_semantics
    ):
        raise CandidateStationaryFailure(HOLD_MEMBER, "candidate member semantics mismatch")
    role_bindings = _exact_keys(
        member["role_bindings"],
        {
            "configuration_source",
            "factorization_source",
            "ideal_formula_source",
            "reference_density_source",
        },
        code=HOLD_MEMBER,
        label="member role bindings",
    )
    _binding_matches_pin(
        role_bindings["configuration_source"],
        request["input_authorities"]["configuration"],
        label="member configuration source",
        code=HOLD_MEMBER,
    )
    _binding_matches_pin(
        role_bindings["ideal_formula_source"],
        request["input_authorities"]["ideal_formula"],
        label="member ideal formula source",
        code=HOLD_MEMBER,
    )
    _binding_matches_pin(
        role_bindings["reference_density_source"],
        request["input_authorities"]["reference_density"],
        label="member reference density source",
        code=HOLD_MEMBER,
    )
    _binding_matches_pin(
        role_bindings["factorization_source"],
        request["input_authorities"]["factorization"],
        label="member factorization source",
        code=HOLD_MEMBER,
    )
    parameter_digest = _domain_digest("encounter-physical-parameter-bundle-v1", parameters)

    raw_partition_pins = request["partitions"]
    if type(raw_partition_pins) is not list or len(raw_partition_pins) != 3 * len(rows):
        raise CandidateStationaryFailure(HOLD_REQUEST, "partition request cardinality mismatch")
    requested: dict[tuple[int, str], dict[str, Any]] = {}
    for raw_pin in raw_partition_pins:
        pin = _exact_keys(raw_pin, _PARTITION_PIN_KEYS, code=HOLD_REQUEST, label="partition pin")
        index = pin["configuration_index"]
        coordinate = pin["coordinate"]
        if (
            type(index) is not int
            or not 0 <= index < len(rows)
            or not _is_nonempty_string(coordinate)
            or coordinate not in COORDINATES
            or (index, coordinate) in requested
            or not _is_sha256(pin["sha256"])
            or not _is_nonempty_string(pin["member_report_relative_path"])
        ):
            raise CandidateStationaryFailure(HOLD_REQUEST, "invalid partition pin identity")
        requested[(index, coordinate)] = pin

    dynamics = configuration.get("dynamics")
    if type(dynamics) is not dict:
        raise CandidateStationaryFailure(HOLD_MEMBER, "configuration dynamics missing")
    result: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    output_pins: list[dict[str, str]] = []
    identity_bindings: list[dict[str, Any]] = []
    seen_labels: set[str] = set()
    seen_sequences: set[str] = set()
    axis_cell_count = 0
    axis_edge_count = 0
    periodic_seam_count = 0
    total_virtual_states = 0
    for index, (row, binding, label, semantic) in enumerate(
        zip(rows, bindings, order, semantics, strict=True)
    ):
        if any(type(value) is not dict for value in (row, binding, semantic)):
            raise CandidateStationaryFailure(HOLD_MEMBER, "candidate row type mismatch")
        _exact_keys(
            semantic,
            _SEMANTIC_ID_KEYS,
            code=HOLD_MEMBER,
            label=f"member semantic id {index}",
        )
        _exact_keys(
            binding,
            _SEQUENCE_BINDING_KEYS,
            code=HOLD_MEMBER,
            label=f"member sequence binding {index}",
        )
        manifest_path = binding["initial_partition_row_manifest_path"]
        manifest_pure = PurePosixPath(manifest_path) if _is_nonempty_string(manifest_path) else None
        if (
            manifest_pure is None
            or manifest_pure.is_absolute()
            or ".." in manifest_pure.parts
            or not _is_sha256(binding["initial_partition_row_manifest_sha256"])
        ):
            raise CandidateStationaryFailure(HOLD_MEMBER, "initial row manifest binding mismatch")
        binding_index = binding.get("configuration_index")
        source_row_index = binding.get("sequence_source_row_index")
        semantic_family_id = semantic.get("refinement_family_id")
        semantic_member_id = semantic.get("refinement_member_id")
        binding_family_id = binding.get("refinement_family_id")
        binding_member_id = binding.get("refinement_member_id")
        if (
            not _is_nonempty_string(label)
            or not _is_nonempty_string(row.get("label"))
            or not _is_nonempty_string(binding.get("authority_label"))
            or not _is_nonempty_string(semantic.get("authority_label"))
            or row.get("label") != label
            or binding.get("authority_label") != label
            or semantic.get("authority_label") != label
            or type(binding_index) is not int
            or type(source_row_index) is not int
            or not 0 <= binding_index < len(rows)
            or not 0 <= source_row_index < len(rows)
            or binding_index != source_row_index
            or binding_index != index
            or label in seen_labels
        ):
            raise CandidateStationaryFailure(HOLD_MEMBER, "candidate row identity mismatch")
        if not all(
            _is_nonempty_string(value)
            for value in (
                semantic_family_id,
                semantic_member_id,
                binding_family_id,
                binding_member_id,
            )
        ):
            raise CandidateStationaryFailure(
                HOLD_MEMBER, "candidate refinement identity type mismatch"
            )
        shape = row.get("shape")
        axis_sizes = [
            row.get(coordinate, {}).get("size") if type(row.get(coordinate)) is dict else None
            for coordinate in COORDINATES
        ]
        expected_states = row.get("expected_states")
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(value) is not int or value < 2 for value in shape)
            or shape != axis_sizes
            or type(expected_states) is not int
            or expected_states != math.prod(shape)
        ):
            raise CandidateStationaryFailure(HOLD_MEMBER, "configuration shape/state mismatch")
        total_virtual_states += expected_states
        seen_labels.add(label)
        sequence_id = binding.get("sequence_id")
        if not _is_nonempty_string(sequence_id) or sequence_id in seen_sequences:
            raise CandidateStationaryFailure(HOLD_MEMBER, "duplicate sequence identity")
        seen_sequences.add(sequence_id)
        row_sha = hashlib.sha256(canonical_bytes(row)).hexdigest()
        if binding.get("sequence_source_row_canonical_sha256") != row_sha:
            raise CandidateStationaryFailure(HOLD_MEMBER, "configuration row digest mismatch")
        anchor_shape = binding.get("n0_anchor_shape")
        anchor_states = binding.get("n0_anchor_expected_states")
        if (
            not _is_sha256(binding.get("configuration_geometry_sha256"))
            or not _is_sha256(binding.get("physical_parameter_bundle_sha256"))
            or not _is_sha256(binding.get("sequence_source_row_canonical_sha256"))
            or type(anchor_states) is not int
            or type(anchor_shape) is not list
            or len(anchor_shape) != 3
            or any(type(value) is not int or value < 2 for value in anchor_shape)
            or binding.get("physical_parameter_bundle_sha256") != parameter_digest
            or anchor_states != row.get("expected_states")
            or anchor_shape != row.get("shape")
            or binding_family_id != semantic_family_id
            or binding_member_id != semantic_member_id
        ):
            raise CandidateStationaryFailure(HOLD_MEMBER, "candidate binding mismatch")
        axes = binding.get("n0_axes")
        if type(axes) is not list or len(axes) != 3:
            raise CandidateStationaryFailure(HOLD_MEMBER, "candidate axis binding mismatch")
        loaded: list[dict[str, Any]] = []
        partition_hashes: list[str] = []
        for coordinate, axis_binding in zip(COORDINATES, axes, strict=True):
            if type(axis_binding) is not dict or axis_binding.get("coordinate") != coordinate:
                raise CandidateStationaryFailure(HOLD_MEMBER, "candidate axis order mismatch")
            expected_axis_keys = (
                _MEMBER_PERIODIC_AXIS_KEYS
                if axis_binding.get("periodic") is True
                else _MEMBER_AXIS_KEYS
            )
            _exact_keys(
                axis_binding,
                expected_axis_keys,
                code=HOLD_MEMBER,
                label=f"member axis binding {index}:{coordinate}",
            )
            _exact_keys(
                axis_binding["exact_box_or_period"],
                {"domain_start_exact", "domain_width_exact"},
                code=HOLD_MEMBER,
                label=f"member axis box {index}:{coordinate}",
            )
            axis_box = axis_binding["exact_box_or_period"]
            axis_family_id = axis_binding.get("refinement_family_id")
            axis_member_id = axis_binding.get("refinement_member_id")
            axis_sequence_id = axis_binding.get("sequence_id")
            if (
                not _is_nonempty_string(axis_binding.get("alignment"))
                or type(axis_binding.get("cell_count")) is not int
                or axis_binding["cell_count"] < 2
                or not _is_nonempty_string(axis_binding.get("coordinate"))
                or type(axis_binding.get("periodic")) is not bool
                or not _is_nonempty_string(axis_binding.get("partition_report_relative_path"))
                or not _is_nonempty_string(axis_binding.get("partition_schema"))
                or not _is_sha256(axis_binding.get("partition_sha256"))
                or not _is_nonempty_string(axis_family_id)
                or not _is_nonempty_string(axis_member_id)
                or not _is_nonempty_string(axis_sequence_id)
                or not _is_sha256(axis_binding.get("sequence_source_row_canonical_sha256"))
                or any(not _is_nonempty_string(value) for value in axis_box.values())
                or (
                    "periodic_shift_n0_exact" in axis_binding
                    and not _is_nonempty_string(axis_binding["periodic_shift_n0_exact"])
                )
            ):
                raise CandidateStationaryFailure(HOLD_MEMBER, "candidate axis type mismatch")
            request_pin = requested.get((index, coordinate))
            if request_pin is None:
                raise CandidateStationaryFailure(HOLD_REQUEST, "partition request is incomplete")
            member_relative = axis_binding.get("partition_report_relative_path")
            if (
                type(member_relative) is not str
                or request_pin["member_report_relative_path"] != member_relative
                or request_pin["sha256"] != axis_binding.get("partition_sha256")
                or axis_binding.get("partition_schema") != PARTITION_SCHEMA
            ):
                raise CandidateStationaryFailure(HOLD_MEMBER, "member/request partition mismatch")
            pure = PurePosixPath(member_relative)
            absolute = _absolute_lexical(
                request_pin["path"], code=HOLD_REQUEST, label="partition path"
            )
            if (
                pure.is_absolute()
                or ".." in pure.parts
                or tuple(absolute.parts[-len(pure.parts) :]) != pure.parts
            ):
                raise CandidateStationaryFailure(HOLD_MEMBER, "partition path suffix mismatch")
            snapshot = immutable_snapshot(absolute, cap=MAX_JSON_BYTES)
            if snapshot.sha256 != request_pin["sha256"]:
                raise CandidateStationaryFailure(HOLD_INPUT, "partition SHA-256 mismatch")
            partition = _parse_canonical(snapshot.raw, label=f"partition {index}:{coordinate}")
            configuration_axis = row.get(coordinate)
            if type(configuration_axis) is not dict:
                raise CandidateStationaryFailure(HOLD_MEMBER, "configuration axis missing")
            expected = _reconstruct_partition(coordinate, configuration_axis, dynamics)
            if partition != expected:
                raise CandidateStationaryFailure(
                    HOLD_MEMBER, f"partition geometry mismatch at {index}:{coordinate}"
                )
            if (
                axis_binding.get("cell_count") != partition["size"]
                or axis_binding.get("periodic") is not partition["periodic"]
                or axis_binding.get("alignment") != configuration_axis.get("alignment")
                or axis_family_id != binding_family_id
                or axis_member_id != binding_member_id
                or axis_sequence_id != sequence_id
                or axis_binding.get("sequence_source_row_canonical_sha256") != row_sha
                or axis_binding.get("exact_box_or_period")
                != {
                    "domain_start_exact": partition["domain_start_exact"],
                    "domain_width_exact": partition["domain_width_exact"],
                }
            ):
                raise CandidateStationaryFailure(HOLD_MEMBER, "axis geometry binding mismatch")
            if partition["periodic"] and axis_binding.get(
                "periodic_shift_n0_exact"
            ) != configuration_axis.get("periodic_shift_exact"):
                raise CandidateStationaryFailure(HOLD_MEMBER, "periodic shift binding mismatch")
            loaded.append(partition)
            partition_hashes.append(snapshot.sha256)
            output_pins.append({"path": str(absolute), "sha256": snapshot.sha256})
            axis_cell_count += partition["size"]
            if partition["periodic"]:
                axis_edge_count += partition["size"]
                periodic_seam_count += 1
            else:
                axis_edge_count += partition["size"] - 1
        geometry_record = {
            "configuration_index": index,
            "configuration_row": row,
            "n0_partition_sha256s": partition_hashes,
        }
        if binding.get("configuration_geometry_sha256") != _domain_digest(
            "encounter-configuration-geometry-v1", geometry_record
        ):
            raise CandidateStationaryFailure(HOLD_MEMBER, "configuration geometry digest mismatch")
        result.append((binding, loaded))
        identity_bindings.append(binding)

    reconstruction_counts = member["reconstruction_counts"]
    expected_reconstruction_counts = {
        "axis_cell_count": EXPECTED_AXIS_CELL_COUNT,
        "axis_count": EXPECTED_AXIS_COUNT,
        "axis_edge_count": EXPECTED_AXIS_EDGE_COUNT,
        "configuration_count": EXPECTED_CONFIGURATION_COUNT,
        "periodic_seam_count": EXPECTED_PERIODIC_SEAM_COUNT,
        "profile_index_count": EXPECTED_PROFILE_INDEX_COUNT,
        "total_virtual_tensor_state_count": EXPECTED_TOTAL_STATES,
    }
    if (
        type(reconstruction_counts) is not dict
        or any(type(value) is not int for value in reconstruction_counts.values())
        or reconstruction_counts != expected_reconstruction_counts
        or axis_cell_count != EXPECTED_AXIS_CELL_COUNT
        or 3 * len(rows) != EXPECTED_AXIS_COUNT
        or axis_edge_count != EXPECTED_AXIS_EDGE_COUNT
        or periodic_seam_count != EXPECTED_PERIODIC_SEAM_COUNT
        or 4 * len(rows) != EXPECTED_PROFILE_INDEX_COUNT
        or total_virtual_states != EXPECTED_TOTAL_STATES
    ):
        raise CandidateStationaryFailure(HOLD_MEMBER, "member reconstruction counts mismatch")
    identity_properties = member["identity_properties"]
    expected_identity_properties = {
        "alignment_counts": {
            "cell_centred_periodic_base": 10,
            "cell_centred_periodic_half_shift": 2,
            "cell_centred_reflecting": 20,
            "vertex_centred_reflecting_dual": 4,
        },
        "candidate_authoritative": False,
        "current_enclosures_bind_this_candidate": False,
        "n0_partition_sha256s_structurally_bound": True,
        "partition_file_count": EXPECTED_AXIS_COUNT,
        "round172_source_itself_contains_partition_sha256": False,
        "source_roles_1_through_4_only_in_production_role_bindings": True,
    }
    if type(identity_properties) is not dict or canonical_bytes(
        identity_properties
    ) != canonical_bytes(expected_identity_properties):
        raise CandidateStationaryFailure(HOLD_MEMBER, "member identity properties mismatch")
    identity = {
        "configuration_order": order,
        "configuration_semantic_ids": semantics,
        "member_semantics": member_semantics,
        "n0_sequence_bindings": identity_bindings,
        "role_bindings_1_through_4": member["role_bindings"],
    }
    member_identity_sha256 = member.get("member_identity_sha256")
    if member_identity_sha256 != MEMBER_IDENTITY_SHA256 or member_identity_sha256 != _domain_digest(
        "encounter-continuum-c1-c2-n0-member-identity-v4", identity
    ):
        raise CandidateStationaryFailure(HOLD_MEMBER, "member identity digest mismatch")
    return result, output_pins


def _configuration_inventory(configuration: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "configuration_index": index,
            "configuration_label": row["label"],
            "configuration_row_canonical_sha256": hashlib.sha256(canonical_bytes(row)).hexdigest(),
            "expected_states": row["expected_states"],
            "shape": row["shape"],
        }
        for index, row in enumerate(configuration["configurations"])
    ]


def _partition_inventory(member: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, binding in enumerate(member["n0_sequence_bindings"]):
        for coordinate, axis in zip(COORDINATES, binding["n0_axes"], strict=True):
            records.append(
                {
                    "alignment": axis["alignment"],
                    "cell_count": axis["cell_count"],
                    "configuration_index": index,
                    "configuration_label": binding["authority_label"],
                    "coordinate": coordinate,
                    "partition_report_relative_path": axis["partition_report_relative_path"],
                    "partition_schema": axis["partition_schema"],
                    "partition_sha256": axis["partition_sha256"],
                    "periodic": axis["periodic"],
                    "refinement_family_id": binding["refinement_family_id"],
                    "refinement_member_id": binding["refinement_member_id"],
                    "sequence_id": binding["sequence_id"],
                }
            )
    return records


def _partition_closure(
    member: dict[str, Any],
    configuration: dict[str, Any],
    partition_inventory: list[dict[str, Any]],
) -> dict[str, Any]:
    nodes: list[dict[str, str]] = [
        {
            "id": "00:member",
            "kind": "member",
            "payload_sha256": member["member_identity_sha256"],
        },
        {
            "id": "01:configuration",
            "kind": "configuration_authority",
            "payload_sha256": hashlib.sha256(canonical_bytes(configuration)).hexdigest(),
        },
    ]
    edges: list[dict[str, str]] = [
        {
            "from": "00:member",
            "relation": "binds_configuration_authority",
            "to": "01:configuration",
        }
    ]
    for index, row in enumerate(configuration["configurations"]):
        row_id = f"02:row:{index:02d}"
        nodes.append(
            {
                "id": row_id,
                "kind": "configuration_row",
                "payload_sha256": hashlib.sha256(canonical_bytes(row)).hexdigest(),
            }
        )
        edges.append(
            {
                "from": "01:configuration",
                "relation": "contains_ordered_row",
                "to": row_id,
            }
        )
        for axis_index, coordinate in enumerate(COORDINATES):
            record = partition_inventory[3 * index + axis_index]
            partition_id = f"03:partition:{index:02d}:{axis_index}:{coordinate}"
            nodes.append(
                {
                    "id": partition_id,
                    "kind": "exact_axis_partition",
                    "payload_sha256": _domain_digest(PARTITION_INVENTORY_DOMAIN, record),
                }
            )
            edges.append(
                {
                    "from": row_id,
                    "relation": "binds_ordered_axis_partition",
                    "to": partition_id,
                }
            )
    nodes.sort(key=lambda node: node["id"])
    edges.sort(key=lambda edge: (edge["from"], edge["relation"], edge["to"]))
    payload = {"edges": edges, "nodes": nodes}
    return {
        "domain": DAG_DOMAIN,
        "edge_count": len(edges),
        "edges": edges,
        "node_count": len(nodes),
        "nodes": nodes,
        "sha256": _domain_digest(DAG_DOMAIN, payload),
    }


def _axis_stream_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        row_identity = {
            "configuration_index": row["configuration_index"],
            "configuration_label": row["configuration_label"],
            "refinement_family_id": row["refinement_family_id"],
            "refinement_member_id": row["refinement_member_id"],
            "sequence_id": row["sequence_id"],
        }
        records.append({"record_type": "row_header", **row_identity})
        for axis_index, axis in enumerate(row["axes"]):
            axis_identity = {
                "axis_index": axis_index,
                "configuration_index": row["configuration_index"],
                "coordinate": axis["coordinate"],
            }
            records.append(
                {
                    "cell_count": axis["cell_count"],
                    "partition_path": axis["partition_path"],
                    "partition_sha256": axis["partition_sha256"],
                    "record_type": "axis_header",
                    **axis_identity,
                }
            )
            for cell in axis["M_x_pi_cell_intervals"]:
                records.append(
                    {
                        **axis_identity,
                        **cell,
                        "record_type": "M_x_pi_cell",
                    }
                )
            for interval_name, key in (
                ("sum_of_cells", "M_x_pi_sum_of_cells_interval"),
                ("direct_domain", "M_x_pi_direct_domain_interval"),
                ("joint_domain", "M_x_pi_joint_domain_interval"),
            ):
                records.append(
                    {
                        **axis_identity,
                        **axis[key],
                        "interval_name": interval_name,
                        "record_type": "axis_interval",
                    }
                )
        for interval_name, key in (
            ("factorized", "M_L_factorized_interval"),
            ("single_domain", "M_L_single_domain_interval"),
            ("joint", "M_L_joint_interval"),
        ):
            records.append(
                {
                    "configuration_index": row["configuration_index"],
                    **row[key],
                    "interval_name": interval_name,
                    "record_type": "M_L_interval",
                }
            )
    return records


def _length_framed_stream_digest(records: Sequence[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    digest.update(STREAM_DOMAIN.encode("ascii"))
    digest.update(b"\0")
    digest.update(len(records).to_bytes(8, "big"))
    for record in records:
        raw = canonical_bytes(record)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
    return digest.hexdigest()


def build_from_request(request_path: Path, output_path: Path) -> bytes:
    request, protocol = _load_request(request_path, output_path)
    runtime = _validate_runtime(request)
    authorities = _exact_keys(
        request["input_authorities"],
        _INPUT_AUTHORITY_ROLES,
        code=HOLD_REQUEST,
        label="input authorities",
    )
    code_inputs = _exact_keys(
        request["code_inputs"],
        {"producer", "verifier"},
        code=HOLD_REQUEST,
        label="code inputs",
    )
    snapshots = {
        role: _pin_snapshot(pin, label=role) for role, pin in {**authorities, **code_inputs}.items()
    }
    current_source = Path(__file__).resolve()
    if snapshots["producer"].path != current_source:
        raise CandidateStationaryFailure(HOLD_INPUT, "producer source pin path mismatch")
    if (
        snapshots["member_spec"].sha256 != MEMBER_SHA256
        or snapshots["method_parameters"].sha256 != PARAMETER_SHA256
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "accepted member/registry pin mismatch")
    anti_vacuity_policy = _parse_canonical(
        snapshots["anti_vacuity_policy"].raw, label="anti-vacuity policy"
    )
    shared_context = protocol.plan["shared_context"]
    if (
        anti_vacuity_policy.get("schema") != ANTI_VACUITY_POLICY_SCHEMA
        or snapshots["anti_vacuity_policy"].sha256 != ANTI_VACUITY_POLICY_SHA256
    ):
        raise CandidateStationaryFailure(HOLD_INPUT, "anti-vacuity policy binding mismatch")
    member = _parse_canonical(snapshots["member_spec"].raw, label="member")
    reference = _parse_canonical(snapshots["reference_density"].raw, label="reference")
    formula = _parse_canonical(snapshots["ideal_formula"].raw, label="formula")
    configuration = _parse_canonical(snapshots["configuration"].raw, label="configuration")
    factorization = _parse_canonical(snapshots["factorization"].raw, label="factorization")
    initial_source = _parse_authenticated_json(
        snapshots["configuration_initial_geometry"].raw,
        label="configuration initial geometry",
    )
    initial_partition_bundle = _parse_authenticated_json(
        snapshots["factorization_initial_partition_bundle"].raw,
        label="factorization initial partition bundle",
    )
    killing_geometry = _parse_authenticated_json(
        snapshots["factorization_killing_geometry"].raw,
        label="factorization killing geometry",
    )
    parameter_registry = _parse_canonical(
        snapshots["method_parameters"].raw, label="method parameters"
    )
    for label, value, code in (
        ("member", member, HOLD_MEMBER),
        ("reference", reference, HOLD_INPUT),
        ("formula", formula, HOLD_INPUT),
        ("configuration", configuration, HOLD_INPUT),
    ):
        _reject_result_observed_keys(value, code=code, label=label)
    _validate_scientific_authorities(
        request,
        reference,
        formula,
        configuration,
        factorization,
        snapshots["factorization"],
        snapshots,
        initial_source,
        initial_partition_bundle,
        killing_geometry,
    )
    methods = _validate_method_registry(parameter_registry, request["method_selection"])
    rows_and_partitions, partition_pins = _validate_member_and_partitions(
        request, member, reference, configuration
    )
    configuration_inventory = _configuration_inventory(configuration)
    partition_inventory = _partition_inventory(member)
    if (
        len(configuration_inventory) != EXPECTED_CONFIGURATION_COUNT
        or len(partition_inventory) != EXPECTED_AXIS_COUNT
        or _domain_digest(CONFIGURATION_INVENTORY_DOMAIN, configuration_inventory)
        != shared_context["configuration_row_inventory_sha256"]
        or _domain_digest(PARTITION_INVENTORY_DOMAIN, partition_inventory)
        != shared_context["partition_inventory_sha256"]
    ):
        raise CandidateStationaryFailure(HOLD_MEMBER, "shared inventory digest mismatch")
    partition_closure = _partition_closure(member, configuration, partition_inventory)

    parameters = reference["physical_parameter_bundle"]
    diffusion = _binary64_fraction(
        parameters.get("particle_diffusion_binary64_hex"), label="particle diffusion"
    )
    stiffness = _binary64_fraction(
        parameters.get("ou_stiffness_binary64_hex"), label="OU stiffness"
    )
    mean = _binary64_fraction(parameters.get("ou_mean_binary64_hex"), label="OU mean")
    period = _fraction(parameters.get("transverse_period_exact"), label="period")
    if diffusion <= 0 or stiffness <= 0 or period <= 0:
        raise CandidateStationaryFailure(HOLD_INPUT, "nonpositive physical parameter")
    coefficients = {
        "midpoint": stiffness / diffusion,
        "relative_parallel": stiffness / (4 * diffusion),
    }

    output_rows: list[dict[str, Any]] = []
    cell_count = 0
    gaussian_count = 0
    periodic_count = 0
    maximum_relative_width = Fraction(0)
    minimum_positive_lower: Fraction | None = None
    configuration_rows = configuration["configurations"]
    for index, ((binding, partitions), config_row) in enumerate(
        zip(rows_and_partitions, configuration_rows, strict=True)
    ):
        axes_output: list[dict[str, Any]] = []
        axis_sums: list[ExactInterval] = []
        axis_directs: list[ExactInterval] = []
        for coordinate, partition in zip(COORDINATES, partitions, strict=True):
            primary_cells: list[ExactInterval] = []
            sentinel_cells: list[ExactInterval] = []
            for segments in partition["cell_segments_exact"]:
                if type(segments) is not list or not segments:
                    raise CandidateStationaryFailure(HOLD_MEMBER, "empty partition cell")
                if coordinate == "relative_perpendicular":
                    volume = sum(
                        (
                            _fraction(segment[1], code=HOLD_MEMBER)
                            - _fraction(segment[0], code=HOLD_MEMBER)
                            for segment in segments
                        ),
                        Fraction(0),
                    )
                    primary = ExactInterval(volume / period, volume / period)
                    sentinel = primary
                    periodic_count += 1
                else:
                    centre = mean if coordinate == "midpoint" else Fraction(0)
                    primary_parts: list[ExactInterval] = []
                    sentinel_parts: list[ExactInterval] = []
                    for segment in segments:
                        if type(segment) is not list or len(segment) != 2:
                            raise CandidateStationaryFailure(HOLD_MEMBER, "invalid segment")
                        lower = _fraction(segment[0], code=HOLD_MEMBER)
                        upper = _fraction(segment[1], code=HOLD_MEMBER)
                        primary_parts.append(
                            _gaussian_mass(
                                lower,
                                upper,
                                coefficient=coefficients[coordinate],
                                centre=centre,
                                bits=methods.primary_bits,
                            )
                        )
                        sentinel_parts.append(
                            _gaussian_mass(
                                lower,
                                upper,
                                coefficient=coefficients[coordinate],
                                centre=centre,
                                bits=methods.sentinel_bits,
                            )
                        )
                    primary = _sum_intervals(primary_parts)
                    sentinel = _sum_intervals(sentinel_parts)
                    gaussian_count += 1
                if primary.lower <= 0 or not primary.contains(sentinel):
                    raise CandidateStationaryFailure(
                        HOLD_NUMERICAL, "primary cell misses positive sentinel"
                    )
                relative_width = (primary.upper - primary.lower) / primary.lower
                maximum_relative_width = max(maximum_relative_width, relative_width)
                minimum_positive_lower = (
                    primary.lower
                    if minimum_positive_lower is None
                    else min(minimum_positive_lower, primary.lower)
                )
                primary_cells.append(primary)
                sentinel_cells.append(sentinel)
            primary_sum = _sum_intervals(primary_cells)
            sentinel_sum = _sum_intervals(sentinel_cells)
            start = _fraction(partition["domain_start_exact"], code=HOLD_MEMBER)
            stop = start + _fraction(partition["domain_width_exact"], code=HOLD_MEMBER)
            if coordinate == "relative_perpendicular":
                primary_direct = ExactInterval(Fraction(1), Fraction(1))
                sentinel_direct = primary_direct
            else:
                centre = mean if coordinate == "midpoint" else Fraction(0)
                primary_direct = _gaussian_mass(
                    start,
                    stop,
                    coefficient=coefficients[coordinate],
                    centre=centre,
                    bits=methods.primary_bits,
                )
                sentinel_direct = _gaussian_mass(
                    start,
                    stop,
                    coefficient=coefficients[coordinate],
                    centre=centre,
                    bits=methods.sentinel_bits,
                )
            if not primary_sum.contains(sentinel_sum) or not primary_direct.contains(
                sentinel_direct
            ):
                raise CandidateStationaryFailure(HOLD_NUMERICAL, "primary axis misses sentinel")
            joint = primary_sum.intersect(primary_direct)
            axis_binding = binding["n0_axes"][COORDINATES.index(coordinate)]
            axes_output.append(
                {
                    "M_x_pi_cell_intervals": [
                        {"cell_index": cell_index, **_interval_json(interval)}
                        for cell_index, interval in enumerate(primary_cells)
                    ],
                    "M_x_pi_direct_domain_interval": _interval_json(primary_direct),
                    "M_x_pi_joint_domain_interval": _interval_json(joint),
                    "M_x_pi_sum_of_cells_interval": _interval_json(primary_sum),
                    "cell_count": partition["size"],
                    "coordinate": coordinate,
                    "partition_path": axis_binding["partition_report_relative_path"],
                    "partition_sha256": axis_binding["partition_sha256"],
                }
            )
            axis_sums.append(primary_sum)
            axis_directs.append(primary_direct)
            cell_count += partition["size"]
        factorized = ExactInterval(Fraction(1), Fraction(1))
        direct = ExactInterval(Fraction(1), Fraction(1))
        for axis_sum, axis_direct in zip(axis_sums, axis_directs, strict=True):
            factorized = factorized.multiply_nonnegative(axis_sum)
            direct = direct.multiply_nonnegative(axis_direct)
        joint = factorized.intersect(direct)
        if not 0 < joint.lower <= joint.upper <= 1:
            raise CandidateStationaryFailure(HOLD_NUMERICAL, "M_L escaped (0,1]")
        output_rows.append(
            {
                "M_L_factorized_interval": _interval_json(factorized),
                "M_L_joint_interval": _interval_json(joint),
                "M_L_single_domain_interval": _interval_json(direct),
                "M_x_pi_tensor_factorization": (
                    "M_x_pi[i_midpoint,i_relative_parallel,i_relative_perpendicular]="
                    "M_midpoint[i_midpoint]*M_relative_parallel[i_relative_parallel]*"
                    "M_relative_perpendicular[i_relative_perpendicular]"
                ),
                "axes": axes_output,
                "configuration_index": index,
                "configuration_label": config_row["label"],
                "refinement_family_id": binding["refinement_family_id"],
                "refinement_member_id": binding["refinement_member_id"],
                "sequence_id": binding["sequence_id"],
                "tensor_state_count": config_row["expected_states"],
            }
        )
    if minimum_positive_lower is None:
        raise CandidateStationaryFailure(HOLD_NUMERICAL, "no cell integral was produced")

    stream_records = _axis_stream_records(output_rows)
    axis_stream = {
        "domain": STREAM_DOMAIN,
        "record_count": len(stream_records),
        "sha256": _length_framed_stream_digest(stream_records),
    }
    output = {
        "axis_stream": axis_stream,
        "claim_boundary": {
            "backend_independence_claimed": False,
            "complete_C0": False,
            "complete_C1": False,
            "complete_C2": False,
            "complete_C3": False,
            "production_same_member_bridge_accepted": False,
            "release_eligible": False,
            "root_transfer_complete": False,
            "submission_eligible": False,
        },
        "member_binding": {
            "member_identity_sha256": member["member_identity_sha256"],
            "path": str(snapshots["member_spec"].path),
            "schema": MEMBER_SCHEMA,
            "sha256": snapshots["member_spec"].sha256,
        },
        "method_binding": {
            "aggregation": "exact_Fraction_endpoint_sums_and_nonnegative_products",
            "dense_tensor_materialized": False,
            "exact_parameter_id": methods.exact_id,
            "parameter_sha256s": methods.parameter_digests,
            "primary_parameter_id": methods.primary_id,
            "primary_precision_bits": methods.primary_bits,
            "rounding": "directed_RoundDown_RoundUp",
            "sentinel_parameter_id": methods.sentinel_id,
            "sentinel_precision_bits": methods.sentinel_bits,
            "sentinel_semantics": "same_backend_higher_precision_containment_only",
            "registry": {
                "path": str(snapshots["method_parameters"].path),
                "schema": PARAMETER_SCHEMA,
                "sha256": snapshots["method_parameters"].sha256,
            },
        },
        "partition_closure": partition_closure,
        "replay_binding": {
            "candidate_bundle": {
                "path": str(protocol.bundle_snapshot.path),
                "sha256": protocol.bundle_snapshot.sha256,
            },
            "external_predecessor_commitment": {
                "path": str(protocol.commitment_snapshot.path),
                "sha256": protocol.commitment_snapshot.sha256,
            },
            "replay_plan": {
                "path": str(protocol.plan_snapshot.path),
                "sha256": protocol.plan_snapshot.sha256,
            },
            "request": {
                "path": str(protocol.request_snapshot.path),
                "sha256": protocol.request_snapshot.sha256,
            },
            "shared_precommit_context_sha256": (protocol.shared_precommit_context_sha256),
            "shared_replay_context_sha256": protocol.shared_replay_context_sha256,
        },
        "role": {
            "role_id": ROLE_ID,
            "role_name": ROLE_NAME,
        },
        "rows": output_rows,
        "runtime_binding": {
            "implementation_runtime_closure": protocol.entry["implementation_runtime_closure"],
            "observed_runtime": runtime,
        },
        "schema": OUTPUT_SCHEMA,
        "source_pins": {
            "code_inputs": {
                role: {"path": str(snapshot.path), "sha256": snapshot.sha256}
                for role, snapshot in snapshots.items()
                if role in code_inputs
            },
            "input_authorities": {
                role: {"path": str(snapshot.path), "sha256": snapshot.sha256}
                for role, snapshot in snapshots.items()
                if role in authorities
            },
            "partitions": partition_pins,
        },
        "status": OUTPUT_STATUS,
        "summary": {
            "all_primary_intervals_contain_sentinels": True,
            "axis_count": EXPECTED_AXIS_COUNT,
            "axis_stream_record_count": len(stream_records),
            "configuration_count": len(output_rows),
            "factorized_axis_cell_count": cell_count,
            "gaussian_axis_cell_count": gaussian_count,
            "maximum_primary_cell_relative_width_exact": _fraction_text(maximum_relative_width),
            "minimum_positive_primary_cell_lower_exact": _fraction_text(minimum_positive_lower),
            "partition_closure_edge_count": partition_closure["edge_count"],
            "partition_closure_node_count": partition_closure["node_count"],
            "periodic_axis_cell_count": periodic_count,
            "total_virtual_tensor_state_count": sum(
                row["tensor_state_count"] for row in output_rows
            ),
        },
    }
    return canonical_bytes(output)


def _directory_identity(metadata: os.stat_result) -> tuple[int, int]:
    return metadata.st_dev, metadata.st_ino


def _close_best_effort(descriptor: int | None) -> None:
    if descriptor is None:
        return
    try:
        os.close(descriptor)
    except BaseException:
        pass


class StageCreationTransaction:
    def __init__(self, parent_descriptor: int, leaf: str) -> None:
        self.parent_descriptor = parent_descriptor
        self.leaf = leaf
        self.descriptor: int | None = None
        self.identity: tuple[int, int] | None = None
        self.error: BaseException | None = None
        self._ready = threading.Event()
        self._thread = threading.Thread(
            target=self._create,
            name="candidate-stationary-stage-create",
        )

    def _create(self) -> None:
        try:
            descriptor = _STAGE_OPEN(
                self.leaf,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o444,
                dir_fd=self.parent_descriptor,
            )
            self.descriptor = descriptor
            metadata = _STAGE_FSTAT(descriptor)
            if (
                not stat.S_ISREG(metadata.st_mode)
                or metadata.st_uid != os.getuid()
                or metadata.st_nlink != 1
                or metadata.st_size != 0
                or stat.S_IMODE(metadata.st_mode) != 0o444
            ):
                raise CandidateStationaryFailure(HOLD_OUTPUT, "new staging inode invariant failure")
            self.identity = _directory_identity(metadata)
        except BaseException as error:
            self.error = error
        finally:
            self._ready.set()

    def start(self) -> None:
        self._thread.start()

    def await_ready(self) -> None:
        self._ready.wait()
        if self.error is not None:
            raise self.error
        if self.descriptor is None or self.identity is None:
            raise CandidateStationaryFailure(
                HOLD_OUTPUT, "stage creation transaction lost authoritative state"
            )

    def settle(self) -> None:
        while self._thread.is_alive():
            try:
                self._thread.join()
            except BaseException:
                continue

    def release_descriptor(self, descriptor: int) -> None:
        if self.descriptor != descriptor:
            raise CandidateStationaryFailure(HOLD_OUTPUT, "stage descriptor transfer mismatch")
        self.descriptor = None


def _open_output_parent(path: Path) -> tuple[int, tuple[int, int]]:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise CandidateStationaryFailure(HOLD_OUTPUT, "descriptor-safe publication unavailable")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_DIRECTORY | os.O_NONBLOCK
    descriptor: int | None = None
    try:
        descriptor = os.open(path.anchor, flags)
        for component in path.parent.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISDIR(metadata.st_mode)
            or metadata.st_uid != os.getuid()
            or stat.S_IMODE(metadata.st_mode) != 0o700
        ):
            raise CandidateStationaryFailure(
                HOLD_OUTPUT, "output parent must be current-UID-owned mode 0700"
            )
        return descriptor, _directory_identity(metadata)
    except BaseException as error:
        _close_best_effort(descriptor)
        if isinstance(error, CandidateStationaryFailure):
            raise
        if isinstance(error, OSError):
            raise CandidateStationaryFailure(
                HOLD_OUTPUT, "anchored output parent traversal failed"
            ) from error
        raise


def _revalidate_output_parent(path: Path, expected: tuple[int, int]) -> None:
    descriptor, observed = _open_output_parent(path)
    _close_best_effort(descriptor)
    if observed != expected:
        raise CandidateStationaryFailure(HOLD_OUTPUT, "output parent identity changed")


def _entry_identity(parent_descriptor: int, name: str) -> tuple[int, int] | None:
    try:
        return _directory_identity(os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False))
    except FileNotFoundError:
        return None


def _unlink_if_owned(
    parent_descriptor: int,
    name: str,
    expected: tuple[int, int],
) -> bool:
    try:
        if _entry_identity(parent_descriptor, name) != expected:
            return False
        os.unlink(name, dir_fd=parent_descriptor)
        return True
    except FileNotFoundError:
        return False


def _rollback_publication(
    parent_descriptor: int,
    *,
    final_name: str,
    installation_attempted: bool,
    stage_identity: tuple[int, int] | None,
    stage_name: str,
) -> None:
    if stage_identity is None:
        return
    changed = False
    for name, eligible in (
        (final_name, installation_attempted),
        (stage_name, True),
    ):
        if not eligible:
            continue
        try:
            changed = _unlink_if_owned(parent_descriptor, name, stage_identity) or changed
        except BaseException:
            pass
    if changed:
        try:
            os.fsync(parent_descriptor)
        except BaseException:
            pass


def _rollback_via_live_parent(
    path: Path,
    expected_parent: tuple[int, int],
    *,
    installation_attempted: bool,
    stage_identity: tuple[int, int] | None,
    stage_name: str,
) -> None:
    descriptor: int | None = None
    try:
        descriptor, observed_parent = _open_output_parent(path)
        if observed_parent == expected_parent:
            _rollback_publication(
                descriptor,
                final_name=path.name,
                installation_attempted=installation_attempted,
                stage_identity=stage_identity,
                stage_name=stage_name,
            )
    except BaseException:
        pass
    finally:
        _close_best_effort(descriptor)


def _read_installed_output(
    parent_descriptor: int,
    name: str,
    expected_identity: tuple[int, int],
    payload_size: int,
) -> bytes:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK | os.O_NOFOLLOW
    descriptor: int | None = None
    try:
        descriptor = os.open(name, flags, dir_fd=parent_descriptor)
        before = os.fstat(descriptor)
        if (
            _directory_identity(before) != expected_identity
            or not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.getuid()
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o444
            or before.st_size != payload_size
        ):
            raise CandidateStationaryFailure(HOLD_OUTPUT, "installed output metadata mismatch")
        remaining = payload_size
        chunks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 1 << 20))
            if not block:
                raise CandidateStationaryFailure(HOLD_OUTPUT, "short installed output read")
            chunks.append(block)
            remaining -= len(block)
        if os.read(descriptor, 1):
            raise CandidateStationaryFailure(HOLD_OUTPUT, "installed output grew")
        after = os.fstat(descriptor)
        if _directory_identity(after) != expected_identity or (
            after.st_mode,
            after.st_nlink,
            after.st_uid,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ) != (
            before.st_mode,
            before.st_nlink,
            before.st_uid,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ):
            raise CandidateStationaryFailure(HOLD_OUTPUT, "installed output changed")
        return b"".join(chunks)
    finally:
        _close_best_effort(descriptor)


def _validate_output_target(path: Path) -> None:
    descriptor, _ = _open_output_parent(path)
    _close_best_effort(descriptor)


def _publish(path: Path, payload: bytes) -> None:
    parent_descriptor: int | None = None
    parent_identity: tuple[int, int] | None = None
    stage_transaction: StageCreationTransaction | None = None
    stage_descriptor: int | None = None
    stage_identity: tuple[int, int] | None = None
    installation_attempted = False
    parent_close_attempted = False
    rollback_performed = False
    acknowledged = False
    stage_name = ""
    try:
        parent_descriptor, parent_identity = _open_output_parent(path)
        if _entry_identity(parent_descriptor, path.name) is not None:
            raise CandidateStationaryFailure(HOLD_OUTPUT, "output already exists")
        for _ in range(16):
            stage_name = f".{path.name}.{secrets.token_hex(16)}.stage"
            if stage_name == path.name:
                continue
            stage_transaction = StageCreationTransaction(parent_descriptor, stage_name)
            try:
                stage_transaction.start()
                stage_transaction.await_ready()
                stage_descriptor = stage_transaction.descriptor
                stage_identity = stage_transaction.identity
                if stage_descriptor is None or stage_identity is None:
                    raise CandidateStationaryFailure(
                        HOLD_OUTPUT, "stage transaction result missing"
                    )
                stage_transaction.release_descriptor(stage_descriptor)
                break
            except FileExistsError:
                stage_transaction.settle()
                stage_transaction = None
                stage_name = ""
                continue
        if stage_descriptor is None or stage_identity is None or not stage_name:
            raise CandidateStationaryFailure(
                HOLD_OUTPUT, "could not reserve same-directory staging file"
            )
        view = memoryview(payload)
        while view:
            written = os.write(stage_descriptor, view)
            if written <= 0:
                raise CandidateStationaryFailure(HOLD_OUTPUT, "short output write")
            view = view[written:]
        os.fchmod(stage_descriptor, 0o444)
        os.fsync(stage_descriptor)
        finished_stage = os.fstat(stage_descriptor)
        if (
            _directory_identity(finished_stage) != stage_identity
            or not stat.S_ISREG(finished_stage.st_mode)
            or finished_stage.st_uid != os.getuid()
            or finished_stage.st_nlink != 1
            or stat.S_IMODE(finished_stage.st_mode) != 0o444
            or finished_stage.st_size != len(payload)
        ):
            raise CandidateStationaryFailure(HOLD_OUTPUT, "staged output metadata mismatch")
        os.close(stage_descriptor)
        stage_descriptor = None

        _revalidate_output_parent(path, parent_identity)
        installation_attempted = True
        os.link(
            stage_name,
            path.name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        if _entry_identity(parent_descriptor, path.name) != stage_identity:
            raise CandidateStationaryFailure(HOLD_OUTPUT, "installed output identity mismatch")
        os.fsync(parent_descriptor)
        _revalidate_output_parent(path, parent_identity)
        if not _unlink_if_owned(parent_descriptor, stage_name, stage_identity):
            raise CandidateStationaryFailure(HOLD_OUTPUT, "owned stage cleanup failed")
        os.fsync(parent_descriptor)
        if (
            _read_installed_output(
                parent_descriptor,
                path.name,
                stage_identity,
                len(payload),
            )
            != payload
        ):
            raise CandidateStationaryFailure(HOLD_OUTPUT, "published output stable reread mismatch")
        live_output = immutable_snapshot(path, cap=max(MAX_JSON_BYTES, len(payload)))
        if live_output.raw != payload:
            raise CandidateStationaryFailure(
                HOLD_OUTPUT, "published output anchored reread mismatch"
            )
        _revalidate_output_parent(path, parent_identity)
        parent_close_attempted = True
        os.close(parent_descriptor)
        parent_descriptor = None
        acknowledged = True
    except BaseException as error:
        if stage_transaction is not None:
            stage_transaction.settle()
            if stage_identity is None:
                stage_identity = stage_transaction.identity
            if stage_transaction.descriptor is not None:
                if stage_descriptor is None:
                    stage_descriptor = stage_transaction.descriptor
                elif stage_descriptor != stage_transaction.descriptor:
                    _close_best_effort(stage_transaction.descriptor)
                stage_transaction.descriptor = None
        if stage_identity is None and stage_descriptor is not None:
            try:
                stage_identity = _directory_identity(_STAGE_FSTAT(stage_descriptor))
            except BaseException:
                pass
        _close_best_effort(stage_descriptor)
        stage_descriptor = None
        if parent_descriptor is not None and not parent_close_attempted:
            _rollback_publication(
                parent_descriptor,
                final_name=path.name,
                installation_attempted=installation_attempted,
                stage_identity=stage_identity,
                stage_name=stage_name,
            )
        if parent_identity is not None and parent_close_attempted:
            _rollback_via_live_parent(
                path,
                parent_identity,
                installation_attempted=installation_attempted,
                stage_identity=stage_identity,
                stage_name=stage_name,
            )
        rollback_performed = True
        if isinstance(error, CandidateStationaryFailure):
            raise
        if isinstance(error, OSError):
            detail = (
                "output already exists"
                if isinstance(error, FileExistsError) and installation_attempted
                else "publication failed"
            )
            raise CandidateStationaryFailure(HOLD_OUTPUT, detail) from error
        raise
    finally:
        if stage_transaction is not None:
            stage_transaction.settle()
            if stage_transaction.descriptor is not None:
                _close_best_effort(stage_transaction.descriptor)
                stage_transaction.descriptor = None
        _close_best_effort(stage_descriptor)
        if not acknowledged and not rollback_performed and parent_descriptor is not None:
            _rollback_publication(
                parent_descriptor,
                final_name=path.name,
                installation_attempted=installation_attempted,
                stage_identity=stage_identity,
                stage_name=stage_name,
            )
        if (
            not acknowledged
            and not rollback_performed
            and parent_identity is not None
            and parent_descriptor is None
        ):
            _rollback_via_live_parent(
                path,
                parent_identity,
                installation_attempted=installation_attempted,
                stage_identity=stage_identity,
                stage_name=stage_name,
            )
        _close_best_effort(parent_descriptor)
    if not acknowledged:
        raise CandidateStationaryFailure(HOLD_OUTPUT, "publication was not acknowledged")


def _parse_cli(argv: Sequence[str] | None) -> tuple[Path, Path]:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args(argv)
    request = _absolute_lexical(arguments.request, code=HOLD_REQUEST, label="request CLI")
    output = _absolute_lexical(arguments.output, code=HOLD_REQUEST, label="output CLI")
    if request == output:
        raise CandidateStationaryFailure(HOLD_REQUEST, "request and output must differ")
    return request, output


def main(argv: Sequence[str] | None = None) -> int:
    try:
        request_path, output_path = _parse_cli(argv)
        payload = build_from_request(request_path, output_path)
        _publish(output_path, payload)
    except CandidateStationaryFailure as error:
        print(error, file=sys.stderr)
        return 2
    print(
        canonical_bytes(
            {
                "output_path": str(output_path),
                "schema": "encounter_continuum_c1_n0_stationary_integrals_ack_v1",
                "status": "PASS_EXCLUSIVE_PUBLICATION",
            }
        ).decode("ascii"),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
