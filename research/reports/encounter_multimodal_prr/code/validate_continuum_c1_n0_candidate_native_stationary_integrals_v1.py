"""Independently validate candidate-native stationary physical integrals.

This verifier does not import the producer or any legacy scientific module.
It independently parses the result-blind request, reconstructs all member
partitions, evaluates every ``M_x^pi`` cell integral and ``M_L`` enclosure with
separately coded directed MPFR operations, and compares the complete canonical
artifact bytes.  It is read-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
import sys
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final, Sequence

import gmpy2

REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_stationary_integrals_request_v2"
ARTIFACT_SCHEMA: Final = "encounter_continuum_c1_n0_candidate_native_stationary_integrals_v1"
ARTIFACT_STATUS: Final = (
    "PASS_RESULT_BLIND_CANDIDATE_NATIVE_STATIONARY_PHYSICAL_INTEGRALS_"
    "PRIMARY_SENTINEL_CONTAINMENT_ONLY_NOT_EXTERNAL_COMMITMENT_NOT_COMPLETE_C1_C2"
)
MEMBER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_member_spec_v3_candidate"
REFERENCE_SCHEMA: Final = "encounter_continuum_c1_reference_density_source_v1"
FORMULA_SCHEMA: Final = "encounter_continuum_c1_ideal_formula_source_v1"
CONFIGURATION_SCHEMA: Final = "encounter_physical_configuration_family_control_free_v1"
FACTORIZATION_SCHEMA: Final = "encounter_continuum_c1_factorization_source_v2_candidate"
FACTORIZATION_SHA256: Final = "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26"
FACTORIZATION_RELATIVE_PATH: Final = (
    "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"
)
PARAMETER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_method_parameter_registry_v3_candidate"
PARAMETER_STATUS: Final = (
    "RESULT_BLIND_CANDIDATE_NATIVE_METHOD_PARAMETERS_ONLY_NOT_EXTERNALLY_COMMITTED"
)
PARAMETER_DIGEST_DOMAIN: Final = "encounter-outward-method-parameters-v3"
PRIMARY_PARAMETER_ID: Final = "stationary_directed_mpfr_320_v2"
SENTINEL_PARAMETER_ID: Final = "stationary_directed_mpfr_640_sentinel_v2"
EXACT_PARAMETER_ID: Final = "exact_fraction_expression_dag_v2"
GENERIC_CONTAINMENT: Final = "primary_interval_contains_higher_precision_same_backend_sentinel"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"
AXIS_ORDER: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
MAX_JSON_BYTES: Final = 8_000_000
MAX_JSON_DEPTH: Final = 64
MAX_INTEGER_BITS: Final = 65_536
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
    "STRUCTURAL_PARTITION_IDENTITY_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
)
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

HOLD_REQUEST = "HOLD_CANDIDATE_STATIONARY_VERIFY_REQUEST"
HOLD_IMMUTABLE = "HOLD_CANDIDATE_STATIONARY_VERIFY_IMMUTABLE"
HOLD_INPUT = "HOLD_CANDIDATE_STATIONARY_VERIFY_INPUT"
HOLD_MEMBER = "HOLD_CANDIDATE_STATIONARY_VERIFY_MEMBER_PARTITION"
HOLD_METHOD = "HOLD_CANDIDATE_STATIONARY_VERIFY_METHOD"
HOLD_RUNTIME = "HOLD_CANDIDATE_STATIONARY_VERIFY_RUNTIME"
HOLD_SCIENCE = "HOLD_CANDIDATE_STATIONARY_VERIFY_SCIENCE"
HOLD_ARTIFACT = "HOLD_CANDIDATE_STATIONARY_VERIFY_ARTIFACT"

_REQUEST_KEYS: Final = {
    "code_inputs",
    "input_authorities",
    "method_selection",
    "output",
    "partitions",
    "runtime_requirements",
    "schema",
    "status",
}
_PIN_KEYS: Final = {"path", "sha256"}
_INPUT_AUTHORITY_ROLES: Final = {
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
_PARTITION_PIN_KEYS: Final = {
    "configuration_index",
    "coordinate",
    "member_report_relative_path",
    "path",
    "sha256",
}
_METHOD_KEYS: Final = {
    "exact_parameter_id",
    "primary_parameter_id",
    "sentinel_parameter_id",
}
_RUNTIME_KEYS: Final = {"gmp", "gmpy2", "mpc", "mpfr", "python_abi"}
_OUTPUT_KEYS: Final = {"path", "schema"}
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
    "killing_contact_profile_mpfr_192_v2",
    "killing_analytic_disk_area_mpfr_256_v2",
    "killing_independent_simpson_remainder_v2",
    "killing_exact_full_cell_classification_v2",
)
_PARAMETER_SCOPES: Final = {
    PRIMARY_PARAMETER_ID: ["role9_stationary_physical_integral"],
    SENTINEL_PARAMETER_ID: ["role9_stationary_physical_integral"],
    "raw_flux_directed_mpfr_320_v2": ["role8_raw_axis_formula_primitive"],
    "raw_flux_directed_mpfr_640_sentinel_v2": ["role8_raw_axis_formula_primitive"],
    "raw_flux_binary64_decode_v2": ["role8_raw_axis_formula_primitive"],
    EXACT_PARAMETER_ID: [
        "role8_raw_axis_formula_primitive",
        "role9_stationary_physical_integral",
        "same_member_mass_flux_composition",
        "symbolic_killing_composition",
    ],
    "killing_contact_profile_mpfr_192_v2": ["role10_killing_factor_geometry"],
    "killing_analytic_disk_area_mpfr_256_v2": ["role10_killing_factor_geometry"],
    "killing_independent_simpson_remainder_v2": ["role10_killing_factor_geometry"],
    "killing_exact_full_cell_classification_v2": ["role10_killing_factor_geometry"],
}
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
    "raw_flux_directed_mpfr_320_v2": {
        "aggregation": "exact_Fraction_endpoint_algebra",
        "common_kappa_rule": "intersection_after_formula_witness",
        "precision_bits": 320,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role8_raw_axis_formula_primitive"],
    },
    "raw_flux_directed_mpfr_640_sentinel_v2": {
        "containment_relation": GENERIC_CONTAINMENT,
        "independent_backend": False,
        "precision_bits": 640,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role8_raw_axis_formula_primitive"],
    },
    "raw_flux_binary64_decode_v2": {
        "decode": "exact_binary64_endpoint_to_reduced_dyadic_fraction",
        "precision_bits": 53,
        "rounding_mode": "stored_outward_endpoints",
        "source_role_scope": ["role8_raw_axis_formula_primitive"],
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
    "killing_contact_profile_mpfr_192_v2": {
        "contact_fraction_record_format": ">dd",
        "panels_per_unit": 16384,
        "precision_bits": 192,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role10_killing_factor_geometry"],
        "support_density_record_format": ">dd",
    },
    "killing_analytic_disk_area_mpfr_256_v2": {
        "analytic_area_precision_bits": 256,
        "formula": "pi_times_radius_squared",
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": ["role10_killing_factor_geometry"],
    },
    "killing_independent_simpson_remainder_v2": {
        "independent_backend": False,
        "maximum_panel_count": 4_194_304,
        "primary_precision_bits": 384,
        "remainder_rule": "rigorous_fourth_derivative_simpson_remainder",
        "sentinel_precision_bits": 512,
        "source_role_scope": ["role10_killing_factor_geometry"],
    },
    "killing_exact_full_cell_classification_v2": {
        "classification": (
            "every_corner_of_every_exact_partition_segment_inside_or_on_contact_disk"
        ),
        "full_cell_serialization": "exact_[1,1]",
        "precision_bits": "exact_rational",
        "rounding_mode": "exact",
        "source_role_scope": ["role10_killing_factor_geometry"],
    },
}


@dataclass(frozen=True, slots=True)
class MethodRegistryContract:
    schema: str
    status: str
    digest_domain: str
    parameter_order: tuple[str, ...]
    parameter_scopes: dict[str, list[str]]
    expected_records: dict[str, dict[str, Any]]
    primary_parameter_id: str
    sentinel_parameter_id: str
    exact_parameter_id: str


# Registry v3 is an explicitly transitional compatibility contract, not the
# terminal registry.  Frozen v4 can be installed by defining its contract
# beside this one and changing only _ACTIVE_METHOD_REGISTRY_CONTRACT.
_TRANSITIONAL_V3_METHOD_REGISTRY_CONTRACT: Final = MethodRegistryContract(
    schema=PARAMETER_SCHEMA,
    status=PARAMETER_STATUS,
    digest_domain=PARAMETER_DIGEST_DOMAIN,
    parameter_order=_PARAMETER_ORDER,
    parameter_scopes=_PARAMETER_SCOPES,
    expected_records=_EXPECTED_PARAMETER_RECORDS,
    primary_parameter_id=PRIMARY_PARAMETER_ID,
    sentinel_parameter_id=SENTINEL_PARAMETER_ID,
    exact_parameter_id=EXACT_PARAMETER_ID,
)
_ACTIVE_METHOD_REGISTRY_CONTRACT: Final = _TRANSITIONAL_V3_METHOD_REGISTRY_CONTRACT

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
    "legacy_member_spec",
    "round176_member_candidate",
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
    "legacy_member_spec": {
        "path": "artifacts/data/continuum_c1_c2_fixed_row_member_spec_v1.json",
        "sha256": "e2166e62ae2e5e67a8e3eb058fe4333f59192525ca5614939f417ba285d8d2ef",
    },
    "round176_member_candidate": {
        "path": "artifacts/data/continuum_c1_c2_n0_member_spec_v2.json",
        "sha256": "cbf967d795648fe5c433ed827d1365e70b84ff1a2444811e3a14244abedadc21",
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


class CandidateStationaryVerificationFailure(RuntimeError):
    """Fail-closed independent validation failure."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code


@dataclass(frozen=True, slots=True)
class RationalBounds:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if (
            type(self.lower) is not Fraction
            or type(self.upper) is not Fraction
            or self.lower > self.upper
        ):
            raise CandidateStationaryVerificationFailure(HOLD_SCIENCE, "invalid rational enclosure")

    def encloses(self, other: RationalBounds) -> bool:
        return self.lower <= other.lower and other.upper <= self.upper


@dataclass(frozen=True, slots=True)
class MpfrBounds:
    lower: gmpy2.mpfr
    upper: gmpy2.mpfr
    bits: int


@dataclass(frozen=True, slots=True)
class FileImage:
    path: Path
    raw: bytes
    sha256: str


@dataclass(frozen=True, slots=True)
class SelectedMethods:
    primary_id: str
    sentinel_id: str
    exact_id: str
    primary_bits: int
    sentinel_bits: int
    digests: dict[str, str]


def _duplicate_rejector(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise CandidateStationaryVerificationFailure(HOLD_INPUT, "duplicate JSON object key")
        result[key] = value
    return result


def _check_json_tree(value: Any, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "JSON depth cap")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if value.bit_length() > MAX_INTEGER_BITS:
            raise CandidateStationaryVerificationFailure(HOLD_INPUT, "integer bit cap")
        return
    if type(value) is float:
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "JSON float forbidden")
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise CandidateStationaryVerificationFailure(HOLD_INPUT, "non-NFC string")
        return
    if type(value) is list:
        for item in value:
            _check_json_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise CandidateStationaryVerificationFailure(HOLD_INPUT, "invalid JSON key")
            _check_json_tree(item, depth + 1)
        return
    raise CandidateStationaryVerificationFailure(HOLD_INPUT, "unsupported JSON type")


def canonical_bytes(value: Any) -> bytes:
    _check_json_tree(value)
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def _decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_duplicate_rejector,
            parse_float=lambda token: (_ for _ in ()).throw(
                CandidateStationaryVerificationFailure(HOLD_INPUT, f"{label}: float {token}")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                CandidateStationaryVerificationFailure(HOLD_INPUT, f"{label}: constant {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, f"{label}: invalid ASCII JSON"
        ) from error
    _check_json_tree(value)
    if type(value) is not dict or canonical_bytes(value) != raw:
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, f"{label}: noncanonical JSON bytes"
        )
    return value


def _decode_authenticated_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_duplicate_rejector,
            parse_float=lambda token: (_ for _ in ()).throw(
                CandidateStationaryVerificationFailure(HOLD_INPUT, f"{label}: float {token}")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                CandidateStationaryVerificationFailure(HOLD_INPUT, f"{label}: constant {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, f"{label}: invalid authenticated ASCII JSON"
        ) from error
    _check_json_tree(value)
    if type(value) is not dict:
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, f"{label}: authenticated JSON object required"
        )
    return value


def _keys(value: Any, expected: set[str], code: str, label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != expected:
        raise CandidateStationaryVerificationFailure(code, f"{label}: exact-key mismatch")
    return value


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _valid_sha(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_nonempty_string(value: Any) -> bool:
    return type(value) is str and bool(value)


def _absolute(value: Any, code: str, label: str) -> Path:
    if type(value) is not str or not value:
        raise CandidateStationaryVerificationFailure(code, f"{label}: path type")
    path = Path(value)
    if not path.is_absolute() or path != Path(os.path.abspath(path)):
        raise CandidateStationaryVerificationFailure(
            code, f"{label}: canonical absolute path required"
        )
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
        raise CandidateStationaryVerificationFailure(
            HOLD_IMMUTABLE, "anchored input traversal unavailable"
        )
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK
    descriptor: int | None = None
    identities: list[tuple[int, int]] = []
    try:
        descriptor = os.open(path.anchor, flags)
        root_metadata = os.fstat(descriptor)
        if not stat.S_ISDIR(root_metadata.st_mode):
            raise CandidateStationaryVerificationFailure(
                HOLD_IMMUTABLE, "input root is not a directory"
            )
        identities.append(_dev_ino(root_metadata))
        for component in path.parent.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptor)
            child_metadata = os.fstat(child)
            if not stat.S_ISDIR(child_metadata.st_mode):
                _close_descriptor(child)
                raise CandidateStationaryVerificationFailure(
                    HOLD_IMMUTABLE, "input path component is not a directory"
                )
            identities.append(_dev_ino(child_metadata))
            os.close(descriptor)
            descriptor = child
        return descriptor, tuple(identities)
    except BaseException as error:
        _close_descriptor(descriptor)
        if isinstance(error, CandidateStationaryVerificationFailure):
            raise
        if isinstance(error, OSError):
            raise CandidateStationaryVerificationFailure(
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
        if isinstance(error, CandidateStationaryVerificationFailure):
            raise
        if isinstance(error, OSError):
            raise CandidateStationaryVerificationFailure(
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
            raise CandidateStationaryVerificationFailure(
                HOLD_IMMUTABLE, "input directory chain identity changed"
            )
        flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
        leaf_descriptor = os.open(path.name, flags, dir_fd=parent_descriptor)
        if _stable_file_identity(os.fstat(leaf_descriptor)) != expected_file:
            raise CandidateStationaryVerificationFailure(
                HOLD_IMMUTABLE, "input leaf identity changed"
            )
    except BaseException as error:
        if isinstance(error, CandidateStationaryVerificationFailure):
            raise
        if isinstance(error, OSError):
            raise CandidateStationaryVerificationFailure(
                HOLD_IMMUTABLE, "live input chain revalidation failed"
            ) from error
        raise
    finally:
        _close_descriptor(leaf_descriptor)
        _close_descriptor(parent_descriptor)


def _immutable_image(path: Path, cap: int = MAX_JSON_BYTES) -> FileImage:
    descriptor, directory_chain = _open_anchored_leaf(path)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.getuid()
            or before.st_nlink != 1
            or before.st_mode & 0o222
            or not 0 < before.st_size <= cap
        ):
            raise CandidateStationaryVerificationFailure(
                HOLD_IMMUTABLE, f"unsafe immutable file metadata: {path}"
            )
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1 << 20))
            if not block:
                raise CandidateStationaryVerificationFailure(
                    HOLD_IMMUTABLE, f"short immutable read: {path}"
                )
            chunks.append(block)
            remaining -= len(block)
        if os.read(descriptor, 1):
            raise CandidateStationaryVerificationFailure(
                HOLD_IMMUTABLE, f"immutable input grew: {path}"
            )
        after = os.fstat(descriptor)
        if _stable_file_identity(before) != _stable_file_identity(after):
            raise CandidateStationaryVerificationFailure(
                HOLD_IMMUTABLE, f"immutable input changed: {path}"
            )
        _revalidate_anchored_image(path, directory_chain, _stable_file_identity(after))
    finally:
        _close_descriptor(descriptor)
    raw = b"".join(chunks)
    return FileImage(path, raw, _sha256(raw))


def _read_pin(pin: Any, label: str) -> FileImage:
    current = _keys(pin, _PIN_KEYS, HOLD_REQUEST, label)
    path = _absolute(current["path"], HOLD_REQUEST, label)
    if not _valid_sha(current["sha256"]):
        raise CandidateStationaryVerificationFailure(HOLD_REQUEST, f"{label}: invalid SHA-256")
    image = _immutable_image(path)
    if image.sha256 != current["sha256"]:
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, f"{label}: SHA-256 mismatch")
    return image


def _q(value: Any, code: str = HOLD_INPUT, label: str = "fraction") -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise CandidateStationaryVerificationFailure(code, f"{label}: p/q required")
    numerator, denominator = value.split("/")
    try:
        parsed = Fraction(int(numerator), int(denominator))
    except (ValueError, ZeroDivisionError) as error:
        raise CandidateStationaryVerificationFailure(code, f"{label}: invalid p/q") from error
    if (
        parsed.denominator <= 0
        or _q_text(parsed) != value
        or max(abs(parsed.numerator).bit_length(), parsed.denominator.bit_length())
        > MAX_INTEGER_BITS
    ):
        raise CandidateStationaryVerificationFailure(code, f"{label}: noncanonical p/q")
    return parsed


def _q_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _hex_q(value: Any, label: str) -> Fraction:
    if type(value) is not str:
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, f"{label}: hex float required")
    try:
        number = float.fromhex(value)
    except (OverflowError, ValueError) as error:
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, f"{label}: invalid hex float"
        ) from error
    if (
        not math.isfinite(number)
        or number.hex() != value
        or (number == 0 and math.copysign(1.0, number) < 0)
    ):
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, f"{label}: noncanonical hex float")
    return Fraction.from_float(number)


def _digest(domain: str, value: Any) -> str:
    return _sha256(domain.encode("ascii") + b"\0" + canonical_bytes(value))


def _bounds_json(value: RationalBounds) -> dict[str, str]:
    return {
        "lower_exact_p_over_q": _q_text(value.lower),
        "upper_exact_p_over_q": _q_text(value.upper),
    }


def _mp_context(bits: int, rounding: int) -> gmpy2.context:
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


def _mp_from_q(value: Fraction, bits: int) -> MpfrBounds:
    rational = gmpy2.mpq(value.numerator, value.denominator)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundDown)):
        lower = +gmpy2.mpfr(rational)
    with gmpy2.context(_mp_context(bits, gmpy2.RoundUp)):
        upper = +gmpy2.mpfr(rational)
    return MpfrBounds(lower, upper, bits)


def _mp_to_q(value: gmpy2.mpfr) -> Fraction:
    rational = gmpy2.mpq(value)
    return Fraction(int(rational.numerator), int(rational.denominator))


def _mp_product(left: MpfrBounds, right: MpfrBounds) -> MpfrBounds:
    if left.bits != right.bits:
        raise CandidateStationaryVerificationFailure(HOLD_SCIENCE, "MPFR bit mismatch")
    combinations = (
        (left.lower, right.lower),
        (left.lower, right.upper),
        (left.upper, right.lower),
        (left.upper, right.upper),
    )
    lower_candidates: list[gmpy2.mpfr] = []
    upper_candidates: list[gmpy2.mpfr] = []
    for a, b in combinations:
        with gmpy2.context(_mp_context(left.bits, gmpy2.RoundDown)):
            lower_candidates.append(+(a * b))
        with gmpy2.context(_mp_context(left.bits, gmpy2.RoundUp)):
            upper_candidates.append(+(a * b))
    return MpfrBounds(min(lower_candidates), max(upper_candidates), left.bits)


def _mp_difference(left: MpfrBounds, right: MpfrBounds) -> MpfrBounds:
    if left.bits != right.bits:
        raise CandidateStationaryVerificationFailure(HOLD_SCIENCE, "MPFR bit mismatch")
    with gmpy2.context(_mp_context(left.bits, gmpy2.RoundDown)):
        lower = +(left.lower - right.upper)
    with gmpy2.context(_mp_context(left.bits, gmpy2.RoundUp)):
        upper = +(left.upper - right.lower)
    return MpfrBounds(lower, upper, left.bits)


def _mp_monotone(value: MpfrBounds, function: Any) -> MpfrBounds:
    with gmpy2.context(_mp_context(value.bits, gmpy2.RoundDown)):
        lower = +function(value.lower)
    with gmpy2.context(_mp_context(value.bits, gmpy2.RoundUp)):
        upper = +function(value.upper)
    return MpfrBounds(lower, upper, value.bits)


def _normal_probability(
    lower: Fraction,
    upper: Fraction,
    coefficient: Fraction,
    centre: Fraction,
    bits: int,
) -> RationalBounds:
    if lower >= upper or coefficient <= 0:
        raise CandidateStationaryVerificationFailure(HOLD_SCIENCE, "invalid Gaussian domain")
    root = _mp_monotone(_mp_from_q(coefficient, bits), gmpy2.sqrt)
    left_argument = _mp_product(root, _mp_from_q(lower - centre, bits))
    right_argument = _mp_product(root, _mp_from_q(upper - centre, bits))
    left_erf = _mp_monotone(left_argument, gmpy2.erf)
    right_erf = _mp_monotone(right_argument, gmpy2.erf)
    difference = _mp_difference(right_erf, left_erf)
    half = _mp_product(difference, _mp_from_q(Fraction(1, 2), bits))
    result = RationalBounds(_mp_to_q(half.lower), _mp_to_q(half.upper))
    if not 0 < result.lower <= result.upper <= 1:
        raise CandidateStationaryVerificationFailure(
            HOLD_SCIENCE, "Gaussian probability escaped [0,1]"
        )
    return result


def _add_bounds(values: Sequence[RationalBounds]) -> RationalBounds:
    lower = sum((value.lower for value in values), Fraction(0))
    upper = sum((value.upper for value in values), Fraction(0))
    return RationalBounds(lower, upper)


def _multiply_bounds(left: RationalBounds, right: RationalBounds) -> RationalBounds:
    if left.lower < 0 or right.lower < 0:
        raise CandidateStationaryVerificationFailure(HOLD_SCIENCE, "negative factor")
    return RationalBounds(left.lower * right.lower, left.upper * right.upper)


def _intersect_bounds(left: RationalBounds, right: RationalBounds) -> RationalBounds:
    lower = max(left.lower, right.lower)
    upper = min(left.upper, right.upper)
    if lower > upper:
        raise CandidateStationaryVerificationFailure(HOLD_SCIENCE, "empty intersection")
    return RationalBounds(lower, upper)


def _fraction_mod(value: Fraction, period: Fraction) -> Fraction:
    if period <= 0:
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "nonpositive period")
    return value - (value // period) * period


def _expected_partition(
    coordinate: str, axis: dict[str, Any], dynamics: dict[str, Any]
) -> dict[str, Any]:
    size = axis.get("size")
    alignment = axis.get("alignment")
    if type(size) is not int or not 2 <= size <= MAX_AXIS_CELLS or type(alignment) is not str:
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "invalid axis")
    if alignment in {"cell_centred_reflecting", "vertex_centred_reflecting_dual"}:
        start = _hex_q(axis.get("lower_binary64_hex"), "axis lower")
        stop = _hex_q(axis.get("upper_binary64_hex"), "axis upper")
        if start >= stop:
            raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "reversed axis")
        width = stop - start
        shift = Fraction(0)
        if alignment == "cell_centred_reflecting":
            spacing = width / size
            positions = [
                start + (Fraction(index) + Fraction(1, 2)) * spacing for index in range(size)
            ]
            cells = [
                [(start + index * spacing, start + (index + 1) * spacing)] for index in range(size)
            ]
            construction = "cell_centred_reflecting_scharfetter_gummel"
        else:
            spacing = width / (size - 1)
            positions = [start + index * spacing for index in range(size)]
            cuts = (
                [start]
                + [start + (Fraction(index) - Fraction(1, 2)) * spacing for index in range(1, size)]
                + [stop]
            )
            cells = [[(cuts[index], cuts[index + 1])] for index in range(size)]
            construction = "vertex_centred_reflecting_scharfetter_gummel"
        periodic = False
    elif alignment in {"cell_centred_periodic_base", "cell_centred_periodic_half_shift"}:
        start = _q(dynamics.get("transverse_domain_start_exact"), HOLD_MEMBER, "period start")
        width = _q(dynamics.get("transverse_period_exact"), HOLD_MEMBER, "period width")
        spacing = width / size
        shift = _q(axis.get("periodic_shift_exact"), HOLD_MEMBER, "period shift")
        desired = Fraction(0) if alignment.endswith("_base") else spacing / 2
        if shift != desired:
            raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "period shift mismatch")
        positions = [
            start + _fraction_mod((Fraction(index) + Fraction(1, 2)) * spacing + shift, width)
            for index in range(size)
        ]
        stop = start + width
        cells: list[list[tuple[Fraction, Fraction]]] = []
        for index in range(size):
            lower = start + _fraction_mod(index * spacing + shift, width)
            upper = lower + spacing
            if upper <= stop:
                cells.append([(lower, upper)])
            else:
                cells.append([(lower, stop), (start, start + upper - stop)])
        construction = (
            "cell_centred_periodic_diffusion"
            if alignment.endswith("_base")
            else "cell_centred_periodic_diffusion_half_shift"
        )
        periodic = True
    else:
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "unknown alignment")
    volumes = [sum((upper - lower for lower, upper in cell), Fraction(0)) for cell in cells]
    return {
        "cell_segments_exact": [
            [[_q_text(lower), _q_text(upper)] for lower, upper in cell] for cell in cells
        ],
        "cell_volumes_exact": [_q_text(value) for value in volumes],
        "construction": construction,
        "coordinate": coordinate,
        "domain_start_exact": _q_text(start),
        "domain_width_exact": _q_text(width),
        "periodic": periodic,
        "periodic_shift_exact": _q_text(shift),
        "positions_exact": [_q_text(value) for value in positions],
        "schema": PARTITION_SCHEMA,
        "size": size,
    }


def _runtime() -> dict[str, str]:
    return {
        "gmp": gmpy2.mp_version(),
        "gmpy2": gmpy2.__version__,
        "mpc": gmpy2.mpc_version(),
        "mpfr": gmpy2.mpfr_version(),
        "python_abi": f"CPython {sys.version_info.major}.{sys.version_info.minor}",
    }


def _select_methods(registry: dict[str, Any], selection: dict[str, Any]) -> SelectedMethods:
    contract = _ACTIVE_METHOD_REGISTRY_CONTRACT
    _keys(selection, _METHOD_KEYS, HOLD_REQUEST, "method selection")
    _keys(registry, _PARAMETER_REGISTRY_KEYS, HOLD_METHOD, "parameter registry")
    claims = registry["claim_boundary"]
    if (
        registry["schema"] != contract.schema
        or registry["status"] != contract.status
        or type(claims) is not dict
        or set(claims) != _PARAMETER_CLAIM_KEYS
        or any(value is not False for value in claims.values())
    ):
        raise CandidateStationaryVerificationFailure(HOLD_METHOD, "registry boundary")
    entries = registry.get("parameters")
    _reject_result_observed_keys(registry, HOLD_METHOD, "parameter registry")
    if (
        type(entries) is not list
        or type(registry.get("parameter_count")) is not int
        or registry["parameter_count"] != len(contract.parameter_order)
        or registry["parameter_count"] != len(entries)
        or [entry.get("parameter_id") if type(entry) is dict else None for entry in entries]
        != list(contract.parameter_order)
    ):
        raise CandidateStationaryVerificationFailure(HOLD_METHOD, "registry cardinality")
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if type(entry) is not dict or set(entry) != {
            "method_parameter_sha256",
            "parameter_id",
            "parameters",
        }:
            raise CandidateStationaryVerificationFailure(HOLD_METHOD, "parameter entry")
        identifier = entry["parameter_id"]
        parameters = entry["parameters"]
        digest = entry["method_parameter_sha256"]
        if (
            type(identifier) is not str
            or identifier in by_id
            or type(parameters) is not dict
            or not _valid_sha(digest)
            or digest != _digest(contract.digest_domain, parameters)
            or canonical_bytes(parameters) != canonical_bytes(contract.expected_records[identifier])
        ):
            raise CandidateStationaryVerificationFailure(HOLD_METHOD, "parameter record mismatch")
        by_id[identifier] = entry
    primary_id = selection["primary_parameter_id"]
    sentinel_id = selection["sentinel_parameter_id"]
    exact_id = selection["exact_parameter_id"]
    if (primary_id, sentinel_id, exact_id) != (
        contract.primary_parameter_id,
        contract.sentinel_parameter_id,
        contract.exact_parameter_id,
    ) or any(item not in by_id for item in (primary_id, sentinel_id, exact_id)):
        raise CandidateStationaryVerificationFailure(HOLD_METHOD, "selected parameter identity")
    return SelectedMethods(
        primary_id,
        sentinel_id,
        exact_id,
        contract.expected_records[contract.primary_parameter_id]["precision_bits"],
        contract.expected_records[contract.sentinel_parameter_id]["precision_bits"],
        {
            identifier: by_id[identifier]["method_parameter_sha256"]
            for identifier in (primary_id, sentinel_id, exact_id)
        },
    )


def _all_keys(value: Any) -> list[str]:
    result: list[str] = []
    if type(value) is dict:
        for key, item in value.items():
            result.append(key)
            result.extend(_all_keys(item))
    elif type(value) is list:
        for item in value:
            result.extend(_all_keys(item))
    return result


def _reject_result_observed_keys(value: Any, code: str, label: str) -> None:
    offending = sorted(
        {key for key in _all_keys(value) if "result" in key.lower() or "observed" in key.lower()}
    )
    if offending:
        raise CandidateStationaryVerificationFailure(
            code, f"{label}: result/observed metadata key forbidden: {offending[0]}"
        )


def _binding_matches_pin(binding: Any, pin: Any, label: str, code: str = HOLD_INPUT) -> None:
    current = _keys(binding, _PIN_KEYS, code, label)
    requested = _keys(pin, _PIN_KEYS, HOLD_REQUEST, f"{label} request pin")
    relative = current["path"]
    if type(relative) is not str or not relative:
        raise CandidateStationaryVerificationFailure(code, f"{label}: invalid relative path")
    pure = PurePosixPath(relative)
    absolute = _absolute(requested["path"], HOLD_REQUEST, f"{label} request path")
    if (
        pure.is_absolute()
        or ".." in pure.parts
        or tuple(absolute.parts[-len(pure.parts) :]) != pure.parts
        or current["sha256"] != requested["sha256"]
    ):
        raise CandidateStationaryVerificationFailure(code, f"{label}: request binding mismatch")


def _validate_configuration_nested(
    request: dict[str, Any],
    configuration: dict[str, Any],
    images: dict[str, FileImage],
    initial_source: dict[str, Any],
) -> None:
    authority = _keys(
        configuration["authority"],
        _CONFIGURATION_AUTHORITY_KEYS,
        HOLD_INPUT,
        "configuration authority",
    )
    if canonical_bytes(authority) != canonical_bytes(_EXPECTED_CONFIGURATION_AUTHORITY):
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "configuration authority mismatch")
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
            f"configuration {prefix} authority",
        )
        if images[role].sha256 != binding["sha256"]:
            raise CandidateStationaryVerificationFailure(
                HOLD_INPUT, f"configuration {prefix} authority bytes mismatch"
            )
    initial = _keys(
        configuration["initial_geometry"],
        _INITIAL_GEOMETRY_KEYS,
        HOLD_INPUT,
        "initial geometry",
    )
    if (
        initial["source_path"] != "artifacts/data/physical_initial_analytic_source_v1.json"
        or initial["source_schema"] != CONFIGURATION_INITIAL_GEOMETRY_SCHEMA
        or initial["source_sha256"]
        != "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
    ):
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "initial geometry source pin mismatch"
        )
    initial_binding = {
        "path": initial["source_path"],
        "sha256": initial["source_sha256"],
    }
    _binding_matches_pin(
        initial_binding,
        request["input_authorities"]["configuration_initial_geometry"],
        "configuration initial geometry source",
    )
    if images["configuration_initial_geometry"].sha256 != initial["source_sha256"]:
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "configuration initial geometry bytes mismatch"
        )
    _keys(
        initial_source,
        _INITIAL_GEOMETRY_SOURCE_KEYS,
        HOLD_INPUT,
        "configuration initial geometry source",
    )
    if (
        initial_source["schema"] != CONFIGURATION_INITIAL_GEOMETRY_SCHEMA
        or initial_source["scope"] != "physical_initial_law_only_no_control_no_budget"
        or initial_source["coordinate_order"] != list(AXIS_ORDER)
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
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "configuration initial geometry semantics mismatch"
        )
    starts = _keys(
        initial["starts_binary64_hex"],
        set(AXIS_ORDER),
        HOLD_INPUT,
        "initial geometry starts",
    )
    for coordinate, value in starts.items():
        _hex_q(value, f"initial {coordinate}")
    contracts = _keys(
        configuration["axis_construction_contracts"],
        {
            "cell_centred_periodic_base",
            "cell_centred_periodic_half_shift",
            "cell_centred_reflecting",
            "vertex_centred_reflecting_dual",
        },
        HOLD_INPUT,
        "axis construction contracts",
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
        _keys(
            contract,
            expected_keys,
            HOLD_INPUT,
            f"axis construction contract {name}",
        )
    rows = configuration["configurations"]
    if type(rows) is not list:
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "configuration rows missing")
    alignment_counts: dict[str, int] = {}
    for index, row in enumerate(rows):
        _keys(
            row,
            _CONFIGURATION_ROW_KEYS,
            HOLD_INPUT,
            f"configuration row {index}",
        )
        if type(row["label"]) is not str or type(row["purpose"]) is not str:
            raise CandidateStationaryVerificationFailure(
                HOLD_INPUT, "configuration row text mismatch"
            )
        shape = row["shape"]
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(value) is not int or value < 2 for value in shape)
            or type(row["expected_states"]) is not int
            or row["expected_states"] != math.prod(shape)
        ):
            raise CandidateStationaryVerificationFailure(
                HOLD_INPUT, "configuration row shape mismatch"
            )
        for axis_index, coordinate in enumerate(AXIS_ORDER):
            axis = row[coordinate]
            if type(axis) is not dict:
                raise CandidateStationaryVerificationFailure(
                    HOLD_INPUT, "configuration axis missing"
                )
            alignment = axis.get("alignment")
            if alignment in {
                "cell_centred_reflecting",
                "vertex_centred_reflecting_dual",
            }:
                _keys(
                    axis,
                    _REFLECTING_AXIS_KEYS,
                    HOLD_INPUT,
                    f"configuration row {index} {coordinate}",
                )
                _hex_q(axis["lower_binary64_hex"], "axis lower")
                _hex_q(axis["upper_binary64_hex"], "axis upper")
            elif alignment in {
                "cell_centred_periodic_base",
                "cell_centred_periodic_half_shift",
            }:
                _keys(
                    axis,
                    _PERIODIC_AXIS_KEYS,
                    HOLD_INPUT,
                    f"configuration row {index} {coordinate}",
                )
                _q(axis["periodic_shift_exact"], HOLD_INPUT, "periodic shift")
            else:
                raise CandidateStationaryVerificationFailure(
                    HOLD_INPUT, "configuration alignment mismatch"
                )
            if type(axis["size"]) is not int or axis["size"] != shape[axis_index]:
                raise CandidateStationaryVerificationFailure(
                    HOLD_INPUT, "configuration axis size mismatch"
                )
            alignment_counts[alignment] = alignment_counts.get(alignment, 0) + 1
    if alignment_counts != {
        "cell_centred_periodic_base": 10,
        "cell_centred_periodic_half_shift": 2,
        "cell_centred_reflecting": 20,
        "vertex_centred_reflecting_dual": 4,
    }:
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "configuration alignment counts mismatch"
        )


def _validate_factorization_authority(
    request: dict[str, Any],
    factorization: dict[str, Any],
    image: FileImage,
    images: dict[str, FileImage],
    initial_partition_bundle: dict[str, Any],
    killing_geometry: dict[str, Any],
) -> None:
    _keys(factorization, _FACTORIZATION_KEYS, HOLD_INPUT, "factorization")
    claims = factorization["claim_boundary"]
    expected_path = PurePosixPath(FACTORIZATION_RELATIVE_PATH)
    if (
        image.sha256 != FACTORIZATION_SHA256
        or tuple(image.path.parts[-len(expected_path.parts) :]) != expected_path.parts
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
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "factorization authority mismatch")
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
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "factorization outcome boundary mismatch"
        )
    source_pins = _keys(
        factorization["source_pins"],
        {
            "configuration_source",
            "initial_partition_bundle",
            "killing_geometry_source",
        },
        HOLD_INPUT,
        "factorization source pins",
    )
    configuration_pin = _keys(
        source_pins["configuration_source"],
        {"path", "schema", "sha256"},
        HOLD_INPUT,
        "factorization configuration source",
    )
    if configuration_pin["schema"] != CONFIGURATION_SCHEMA:
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "factorization configuration schema"
        )
    _binding_matches_pin(
        {"path": configuration_pin["path"], "sha256": configuration_pin["sha256"]},
        request["input_authorities"]["configuration"],
        "factorization configuration source",
    )
    if images["configuration"].sha256 != configuration_pin["sha256"]:
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "factorization configuration bytes mismatch"
        )
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
        current = _keys(
            source_pins[name],
            {"path", "schema", "sha256"},
            HOLD_INPUT,
            f"factorization {name}",
        )
        if canonical_bytes(current) != canonical_bytes(expected):
            raise CandidateStationaryVerificationFailure(
                HOLD_INPUT, f"factorization {name} mismatch"
            )
        role = (
            "factorization_initial_partition_bundle"
            if name == "initial_partition_bundle"
            else "factorization_killing_geometry"
        )
        _binding_matches_pin(
            {"path": current["path"], "sha256": current["sha256"]},
            request["input_authorities"][role],
            f"factorization {name}",
        )
        if images[role].sha256 != current["sha256"]:
            raise CandidateStationaryVerificationFailure(
                HOLD_INPUT, f"factorization {name} bytes mismatch"
            )
    _keys(
        initial_partition_bundle,
        _INITIAL_PARTITION_BUNDLE_KEYS,
        HOLD_INPUT,
        "factorization initial partition bundle",
    )
    if (
        initial_partition_bundle["schema"] != FACTORIZATION_INITIAL_PARTITION_SCHEMA
        or initial_partition_bundle["status"] != FACTORIZATION_INITIAL_PARTITION_STATUS
        or initial_partition_bundle["configuration_sha256"] != images["configuration"].sha256
        or initial_partition_bundle["analytic_source_sha256"]
        != images["configuration_initial_geometry"].sha256
        or initial_partition_bundle["configuration_count"] != EXPECTED_CONFIGURATION_COUNT
        or initial_partition_bundle["total_state_workload"] != EXPECTED_TOTAL_STATES
    ):
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "factorization initial partition bundle semantics mismatch"
        )
    _keys(
        killing_geometry,
        _KILLING_GEOMETRY_SOURCE_KEYS,
        HOLD_INPUT,
        "factorization killing geometry",
    )
    killing_configuration = _keys(
        killing_geometry["configuration_bundle"],
        {
            "configuration_path",
            "configuration_sha256",
            "partition_bundle_path",
            "partition_bundle_sha256",
        },
        HOLD_INPUT,
        "killing geometry configuration bundle",
    )
    if (
        killing_geometry["schema"] != FACTORIZATION_KILLING_GEOMETRY_SCHEMA
        or killing_geometry["status"] != FACTORIZATION_KILLING_GEOMETRY_STATUS
        or killing_geometry["coordinate_order"] != list(AXIS_ORDER)
        or killing_geometry["physical_dimension"] != 2
        or killing_geometry["quotient_dimension"] != 3
    ):
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "factorization killing geometry semantics mismatch"
        )
    _binding_matches_pin(
        {
            "path": killing_configuration["configuration_path"],
            "sha256": killing_configuration["configuration_sha256"],
        },
        request["input_authorities"]["configuration"],
        "killing geometry configuration source",
    )
    _binding_matches_pin(
        {
            "path": killing_configuration["partition_bundle_path"],
            "sha256": killing_configuration["partition_bundle_sha256"],
        },
        request["input_authorities"]["factorization_initial_partition_bundle"],
        "killing geometry initial partition bundle",
    )
    if (
        killing_configuration["configuration_sha256"] != images["configuration"].sha256
        or killing_configuration["partition_bundle_sha256"]
        != images["factorization_initial_partition_bundle"].sha256
    ):
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "killing geometry dependency bytes mismatch"
        )


def _validate_scientific_authorities(
    request: dict[str, Any],
    reference: dict[str, Any],
    formula: dict[str, Any],
    configuration: dict[str, Any],
    factorization: dict[str, Any],
    factorization_image: FileImage,
    images: dict[str, FileImage],
    initial_source: dict[str, Any],
    initial_partition_bundle: dict[str, Any],
    killing_geometry: dict[str, Any],
) -> None:
    _keys(reference, _REFERENCE_KEYS, HOLD_INPUT, "reference")
    _keys(formula, _FORMULA_KEYS, HOLD_INPUT, "formula")
    _keys(configuration, _CONFIGURATION_KEYS, HOLD_INPUT, "configuration")
    _validate_configuration_nested(request, configuration, images, initial_source)
    _validate_factorization_authority(
        request,
        factorization,
        factorization_image,
        images,
        initial_partition_bundle,
        killing_geometry,
    )
    if (
        reference["schema"] != REFERENCE_SCHEMA
        or reference["status"]
        != "FROZEN_CONTROL_FREE_REFERENCE_DENSITY_AUTHORITY_ONLY_NO_COMPLETE_C0_C1_C2"
        or reference["coordinate_order"] != list(AXIS_ORDER)
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
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "reference semantics")
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
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "reference claim boundary")
    reference_pins = _keys(
        reference["source_pins"],
        {"c0_mathematical_source", "configuration_source"},
        HOLD_INPUT,
        "reference source pins",
    )
    c0_pin = _keys(
        reference_pins["c0_mathematical_source"],
        _PIN_KEYS,
        HOLD_INPUT,
        "reference C0 source pin",
    )
    if c0_pin != {
        "path": "artifacts/data/continuum_c0_mathematical_source_v2.json",
        "sha256": "522bd667e5f6fd6a4d12f270f0c2f4b9e86be9b207d471961d4f67db972df559",
    }:
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "reference C0 source pin")
    _binding_matches_pin(
        reference_pins["configuration_source"],
        request["input_authorities"]["configuration"],
        "reference configuration source",
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
        or type(formula["formulae"]) is not dict
        or canonical_bytes(formula["formulae"]) != canonical_bytes(_EXPECTED_FORMULAE)
    ):
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "formula semantics")
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
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "formula claim boundary")
    formula_pins = _keys(
        formula["source_pins"],
        {"c0_mathematical_source", "production_bridge_design"},
        HOLD_INPUT,
        "formula source pins",
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
        current = _keys(formula_pins[name], _PIN_KEYS, HOLD_INPUT, f"formula {name}")
        if current != expected:
            raise CandidateStationaryVerificationFailure(HOLD_INPUT, f"formula {name}")

    dynamics = _keys(configuration["dynamics"], _DYNAMICS_KEYS, HOLD_INPUT, "dynamics")
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
        or configuration["coordinate_order"] != list(AXIS_ORDER)
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
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "configuration semantics")
    parameters = _keys(
        reference["physical_parameter_bundle"],
        {
            "ou_mean_binary64_hex",
            "ou_stiffness_binary64_hex",
            "particle_diffusion_binary64_hex",
            "physical_dimension",
            "quotient_dimension",
            "transverse_period_exact",
        },
        HOLD_INPUT,
        "physical parameter bundle",
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
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "configuration parameters")
    _hex_q(parameters["ou_mean_binary64_hex"], "mean")
    _hex_q(parameters["ou_stiffness_binary64_hex"], "stiffness")
    _hex_q(parameters["particle_diffusion_binary64_hex"], "diffusion")
    _q(parameters["transverse_period_exact"], HOLD_INPUT, "period")
    if factorization["contact_geometry"]["transverse_period_exact"] != parameters[
        "transverse_period_exact"
    ] or factorization["coordinate_and_measure_contract"]["coordinate_order"] != list(AXIS_ORDER):
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "factorization geometry binding mismatch"
        )


def _load_request(
    request_path: Path, artifact_path: Path
) -> tuple[dict[str, Any], FileImage, dict[str, FileImage]]:
    request_image = _immutable_image(request_path)
    request = _decode_canonical(request_image.raw, "request")
    _keys(request, _REQUEST_KEYS, HOLD_REQUEST, "request")
    if (
        request["schema"] != REQUEST_SCHEMA
        or request["status"] != "RESULT_BLIND_REQUEST_NOT_EXECUTION_RESULT"
    ):
        raise CandidateStationaryVerificationFailure(HOLD_REQUEST, "request boundary")
    output = _keys(request["output"], _OUTPUT_KEYS, HOLD_REQUEST, "output")
    if (
        output["schema"] != ARTIFACT_SCHEMA
        or _absolute(output["path"], HOLD_REQUEST, "output") != artifact_path
    ):
        raise CandidateStationaryVerificationFailure(HOLD_REQUEST, "artifact path mismatch")
    forbidden = (
        "artifact_sha",
        "expected_output",
        "expected_result",
        "observed",
        "output_sha",
        "production_result",
        "result_sha",
        "role9_result",
        "role10_result",
    )
    if any(fragment in key.lower() for key in _all_keys(request) for fragment in forbidden):
        raise CandidateStationaryVerificationFailure(
            HOLD_REQUEST, "request contains result/observed pin"
        )
    authorities = _keys(
        request["input_authorities"],
        _INPUT_AUTHORITY_ROLES,
        HOLD_REQUEST,
        "authorities",
    )
    code = _keys(request["code_inputs"], {"producer", "verifier"}, HOLD_REQUEST, "code inputs")
    images = {role: _read_pin(pin, role) for role, pin in {**authorities, **code}.items()}
    if images["verifier"].path != Path(__file__).resolve():
        raise CandidateStationaryVerificationFailure(
            HOLD_INPUT, "verifier source pin path mismatch"
        )
    runtime_required = _keys(
        request["runtime_requirements"], _RUNTIME_KEYS, HOLD_REQUEST, "runtime"
    )
    if runtime_required != _runtime():
        raise CandidateStationaryVerificationFailure(HOLD_RUNTIME, "runtime mismatch")
    return request, request_image, images


def _member_partitions(
    request: dict[str, Any],
    member: dict[str, Any],
    reference: dict[str, Any],
    configuration: dict[str, Any],
) -> tuple[list[tuple[dict[str, Any], list[dict[str, Any]]]], list[dict[str, str]]]:
    _keys(member, _MEMBER_KEYS, HOLD_MEMBER, "member")
    member_claims = member["claim_boundary"]
    if (
        member["schema"] != MEMBER_SCHEMA
        or member["status"] != MEMBER_STATUS
        or type(member_claims) is not dict
        or set(member_claims) != _PARAMETER_CLAIM_KEYS
        or any(value is not False for value in member_claims.values())
        or reference.get("schema") != REFERENCE_SCHEMA
        or configuration.get("schema") != CONFIGURATION_SCHEMA
    ):
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "authority schema")
    lineage = _keys(
        member["source_lineage_evidence"],
        _LINEAGE_KEYS,
        HOLD_MEMBER,
        "member source lineage",
    )
    if canonical_bytes(lineage) != canonical_bytes(_EXPECTED_SOURCE_LINEAGE):
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "member source lineage")
    parameters = reference.get("physical_parameter_bundle")
    rows = configuration.get("configurations")
    bindings = member.get("n0_sequence_bindings")
    order = member.get("configuration_order")
    semantics = member.get("configuration_semantic_ids")
    member_semantics = member.get("member_semantics")
    expected_member_semantics = {
        "configuration_count": EXPECTED_CONFIGURATION_COUNT,
        "configuration_rows_are_finite_anchors": True,
        "coordinate_order": list(AXIS_ORDER),
        "every_cartesian_interval_endpoint_combination_is_a_model": False,
        "one_formula_defined_correlated_member_per_configuration": True,
        "physical_dimension": 2,
        "quotient_dimension": 3,
        "scalar_convention": "complex_inner_product_conjugate_first_factor",
    }
    if (
        type(parameters) is not dict
        or type(rows) is not list
        or type(bindings) is not list
        or type(order) is not list
        or type(semantics) is not list
        or type(member_semantics) is not dict
        or len(rows) != EXPECTED_CONFIGURATION_COUNT
        or not len(rows) == len(bindings) == len(order) == len(semantics)
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
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "member cardinality")
    role_bindings = _keys(
        member["role_bindings"],
        {
            "configuration_source",
            "factorization_source",
            "ideal_formula_source",
            "reference_density_source",
        },
        HOLD_MEMBER,
        "member role bindings",
    )
    _binding_matches_pin(
        role_bindings["configuration_source"],
        request["input_authorities"]["configuration"],
        "member configuration source",
        HOLD_MEMBER,
    )
    _binding_matches_pin(
        role_bindings["ideal_formula_source"],
        request["input_authorities"]["ideal_formula"],
        "member ideal formula source",
        HOLD_MEMBER,
    )
    _binding_matches_pin(
        role_bindings["reference_density_source"],
        request["input_authorities"]["reference_density"],
        "member reference density source",
        HOLD_MEMBER,
    )
    _binding_matches_pin(
        role_bindings["factorization_source"],
        request["input_authorities"]["factorization"],
        "member factorization source",
        HOLD_MEMBER,
    )
    partition_pins = request["partitions"]
    if type(partition_pins) is not list or len(partition_pins) != 3 * len(rows):
        raise CandidateStationaryVerificationFailure(HOLD_REQUEST, "partition cardinality")
    pin_map: dict[tuple[int, str], dict[str, Any]] = {}
    for item in partition_pins:
        pin = _keys(item, _PARTITION_PIN_KEYS, HOLD_REQUEST, "partition pin")
        index = pin["configuration_index"]
        coordinate = pin["coordinate"]
        if (
            type(index) is not int
            or not 0 <= index < len(rows)
            or not _is_nonempty_string(coordinate)
            or coordinate not in AXIS_ORDER
            or (index, coordinate) in pin_map
            or not _valid_sha(pin["sha256"])
            or not _is_nonempty_string(pin["member_report_relative_path"])
        ):
            raise CandidateStationaryVerificationFailure(HOLD_REQUEST, "partition pin identity")
        pin_map[(index, coordinate)] = pin
    dynamics = configuration.get("dynamics")
    if type(dynamics) is not dict:
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "missing dynamics")
    parameter_digest = _digest("encounter-physical-parameter-bundle-v1", parameters)
    loaded_rows: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    output_pins: list[dict[str, str]] = []
    seen_labels: set[str] = set()
    seen_sequences: set[str] = set()
    axis_cell_count = 0
    axis_edge_count = 0
    periodic_seam_count = 0
    total_virtual_states = 0
    for index, (row, binding, label, semantic) in enumerate(
        zip(rows, bindings, order, semantics, strict=True)
    ):
        if any(type(item) is not dict for item in (row, binding, semantic)):
            raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "member row type")
        _keys(semantic, _SEMANTIC_ID_KEYS, HOLD_MEMBER, f"member semantic id {index}")
        _keys(binding, _SEQUENCE_BINDING_KEYS, HOLD_MEMBER, f"member sequence binding {index}")
        manifest_path = binding["initial_partition_row_manifest_path"]
        manifest_pure = PurePosixPath(manifest_path) if _is_nonempty_string(manifest_path) else None
        if (
            manifest_pure is None
            or manifest_pure.is_absolute()
            or ".." in manifest_pure.parts
            or not _valid_sha(binding["initial_partition_row_manifest_sha256"])
        ):
            raise CandidateStationaryVerificationFailure(
                HOLD_MEMBER, "initial row manifest binding"
            )
        binding_index = binding.get("configuration_index")
        source_row_index = binding.get("sequence_source_row_index")
        semantic_family_id = semantic.get("refinement_family_id")
        semantic_member_id = semantic.get("refinement_member_id")
        binding_family_id = binding.get("refinement_family_id")
        binding_member_id = binding.get("refinement_member_id")
        sequence_id = binding.get("sequence_id")
        if (
            not _is_nonempty_string(label)
            or not _is_nonempty_string(row.get("label"))
            or not _is_nonempty_string(binding.get("authority_label"))
            or not _is_nonempty_string(semantic.get("authority_label"))
            or label in seen_labels
            or not _is_nonempty_string(sequence_id)
            or sequence_id in seen_sequences
            or row.get("label") != label
            or binding.get("authority_label") != label
            or semantic.get("authority_label") != label
            or type(binding_index) is not int
            or type(source_row_index) is not int
            or not 0 <= binding_index < len(rows)
            or not 0 <= source_row_index < len(rows)
            or binding_index != source_row_index
            or binding_index != index
        ):
            raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "member row identity")
        if not all(
            _is_nonempty_string(value)
            for value in (
                semantic_family_id,
                semantic_member_id,
                binding_family_id,
                binding_member_id,
            )
        ):
            raise CandidateStationaryVerificationFailure(
                HOLD_MEMBER, "member refinement identity type"
            )
        shape = row.get("shape")
        axis_sizes = [
            row.get(coordinate, {}).get("size") if type(row.get(coordinate)) is dict else None
            for coordinate in AXIS_ORDER
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
            raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "shape/state mismatch")
        total_virtual_states += expected_states
        seen_labels.add(label)
        seen_sequences.add(sequence_id)
        row_sha = _sha256(canonical_bytes(row))
        anchor_shape = binding.get("n0_anchor_shape")
        anchor_states = binding.get("n0_anchor_expected_states")
        if (
            not _valid_sha(binding.get("configuration_geometry_sha256"))
            or not _valid_sha(binding.get("physical_parameter_bundle_sha256"))
            or not _valid_sha(binding.get("sequence_source_row_canonical_sha256"))
            or type(anchor_states) is not int
            or type(anchor_shape) is not list
            or len(anchor_shape) != 3
            or any(type(value) is not int or value < 2 for value in anchor_shape)
            or binding.get("sequence_source_row_canonical_sha256") != row_sha
            or binding.get("physical_parameter_bundle_sha256") != parameter_digest
            or anchor_states != row.get("expected_states")
            or anchor_shape != row.get("shape")
            or binding_family_id != semantic_family_id
            or binding_member_id != semantic_member_id
        ):
            raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "member row binding")
        axes = binding.get("n0_axes")
        if type(axes) is not list or len(axes) != 3:
            raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "member axes")
        partitions: list[dict[str, Any]] = []
        hashes: list[str] = []
        for coordinate, axis_binding in zip(AXIS_ORDER, axes, strict=True):
            if type(axis_binding) is not dict or axis_binding.get("coordinate") != coordinate:
                raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "axis order")
            expected_axis_keys = (
                _MEMBER_PERIODIC_AXIS_KEYS
                if axis_binding.get("periodic") is True
                else _MEMBER_AXIS_KEYS
            )
            _keys(
                axis_binding,
                expected_axis_keys,
                HOLD_MEMBER,
                f"member axis binding {index}:{coordinate}",
            )
            _keys(
                axis_binding["exact_box_or_period"],
                {"domain_start_exact", "domain_width_exact"},
                HOLD_MEMBER,
                f"member axis box {index}:{coordinate}",
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
                or not _valid_sha(axis_binding.get("partition_sha256"))
                or not _is_nonempty_string(axis_family_id)
                or not _is_nonempty_string(axis_member_id)
                or not _is_nonempty_string(axis_sequence_id)
                or not _valid_sha(axis_binding.get("sequence_source_row_canonical_sha256"))
                or any(not _is_nonempty_string(value) for value in axis_box.values())
                or (
                    "periodic_shift_n0_exact" in axis_binding
                    and not _is_nonempty_string(axis_binding["periodic_shift_n0_exact"])
                )
            ):
                raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "member axis type")
            pin = pin_map.get((index, coordinate))
            relative = axis_binding.get("partition_report_relative_path")
            if (
                pin is None
                or type(relative) is not str
                or pin["member_report_relative_path"] != relative
                or pin["sha256"] != axis_binding.get("partition_sha256")
                or axis_binding.get("partition_schema") != PARTITION_SCHEMA
            ):
                raise CandidateStationaryVerificationFailure(
                    HOLD_MEMBER, "member/partition pin mismatch"
                )
            pure = PurePosixPath(relative)
            absolute = _absolute(pin["path"], HOLD_REQUEST, "partition")
            if (
                pure.is_absolute()
                or ".." in pure.parts
                or tuple(absolute.parts[-len(pure.parts) :]) != pure.parts
            ):
                raise CandidateStationaryVerificationFailure(
                    HOLD_MEMBER, "partition suffix mismatch"
                )
            image = _immutable_image(absolute)
            if image.sha256 != pin["sha256"]:
                raise CandidateStationaryVerificationFailure(HOLD_INPUT, "partition hash mismatch")
            partition = _decode_canonical(image.raw, f"partition {index}:{coordinate}")
            config_axis = row.get(coordinate)
            if type(config_axis) is not dict:
                raise CandidateStationaryVerificationFailure(
                    HOLD_MEMBER, "configuration axis absent"
                )
            expected = _expected_partition(coordinate, config_axis, dynamics)
            if partition != expected:
                raise CandidateStationaryVerificationFailure(
                    HOLD_MEMBER, f"partition geometry {index}:{coordinate}"
                )
            if (
                axis_binding.get("cell_count") != partition["size"]
                or axis_binding.get("periodic") is not partition["periodic"]
                or axis_binding.get("alignment") != config_axis.get("alignment")
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
                raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "axis geometry binding")
            if partition["periodic"] and axis_binding.get(
                "periodic_shift_n0_exact"
            ) != config_axis.get("periodic_shift_exact"):
                raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "periodic shift binding")
            partitions.append(partition)
            hashes.append(image.sha256)
            output_pins.append({"path": str(absolute), "sha256": image.sha256})
            axis_cell_count += partition["size"]
            if partition["periodic"]:
                axis_edge_count += partition["size"]
                periodic_seam_count += 1
            else:
                axis_edge_count += partition["size"] - 1
        geometry = {
            "configuration_index": index,
            "configuration_row": row,
            "n0_partition_sha256s": hashes,
        }
        if binding.get("configuration_geometry_sha256") != _digest(
            "encounter-configuration-geometry-v1", geometry
        ):
            raise CandidateStationaryVerificationFailure(
                HOLD_MEMBER, "configuration geometry digest"
            )
        loaded_rows.append((binding, partitions))
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
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "reconstruction counts")
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
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "identity properties")
    identity = {
        "configuration_order": order,
        "configuration_semantic_ids": semantics,
        "coordinate_order": list(AXIS_ORDER),
        "n0_sequence_bindings": bindings,
        "role_bindings_1_through_4": member["role_bindings"],
        "scalar_convention": member_semantics.get("scalar_convention"),
    }
    member_identity_sha256 = member.get("member_identity_sha256")
    if not _valid_sha(member_identity_sha256) or member_identity_sha256 != _digest(
        "encounter-continuum-c1-c2-n0-member-identity-v3", identity
    ):
        raise CandidateStationaryVerificationFailure(HOLD_MEMBER, "member identity digest")
    return loaded_rows, output_pins


def _expected_artifact(request_path: Path, artifact_path: Path) -> tuple[bytes, dict[str, Any]]:
    request, request_image, images = _load_request(request_path, artifact_path)
    member = _decode_canonical(images["member_spec"].raw, "member")
    reference = _decode_canonical(images["reference_density"].raw, "reference")
    formula = _decode_canonical(images["ideal_formula"].raw, "formula")
    configuration = _decode_canonical(images["configuration"].raw, "configuration")
    factorization = _decode_canonical(images["factorization"].raw, "factorization")
    initial_source = _decode_authenticated_json(
        images["configuration_initial_geometry"].raw,
        "configuration initial geometry",
    )
    initial_partition_bundle = _decode_authenticated_json(
        images["factorization_initial_partition_bundle"].raw,
        "factorization initial partition bundle",
    )
    killing_geometry = _decode_authenticated_json(
        images["factorization_killing_geometry"].raw,
        "factorization killing geometry",
    )
    registry = _decode_canonical(images["method_parameters"].raw, "method registry")
    for label, value, code in (
        ("member", member, HOLD_MEMBER),
        ("reference", reference, HOLD_INPUT),
        ("formula", formula, HOLD_INPUT),
        ("configuration", configuration, HOLD_INPUT),
    ):
        _reject_result_observed_keys(value, code, label)
    _validate_scientific_authorities(
        request,
        reference,
        formula,
        configuration,
        factorization,
        images["factorization"],
        images,
        initial_source,
        initial_partition_bundle,
        killing_geometry,
    )
    methods = _select_methods(registry, request["method_selection"])
    rows_and_partitions, partition_pins = _member_partitions(
        request, member, reference, configuration
    )
    parameters = reference["physical_parameter_bundle"]
    diffusion = _hex_q(parameters.get("particle_diffusion_binary64_hex"), "diffusion")
    stiffness = _hex_q(parameters.get("ou_stiffness_binary64_hex"), "stiffness")
    mean = _hex_q(parameters.get("ou_mean_binary64_hex"), "mean")
    period = _q(parameters.get("transverse_period_exact"), HOLD_INPUT, "period")
    if min(diffusion, stiffness, period) <= 0:
        raise CandidateStationaryVerificationFailure(HOLD_INPUT, "nonpositive parameter")
    coefficients = {
        "midpoint": stiffness / diffusion,
        "relative_parallel": stiffness / (4 * diffusion),
    }

    output_rows: list[dict[str, Any]] = []
    total_cells = 0
    gaussian_cells = 0
    periodic_cells = 0
    maximum_width = Fraction(0)
    minimum_lower: Fraction | None = None
    for index, ((binding, partitions), config_row) in enumerate(
        zip(rows_and_partitions, configuration["configurations"], strict=True)
    ):
        axes_output: list[dict[str, Any]] = []
        sums: list[RationalBounds] = []
        directs: list[RationalBounds] = []
        for coordinate, partition, axis_binding in zip(
            AXIS_ORDER, partitions, binding["n0_axes"], strict=True
        ):
            primary_cells: list[RationalBounds] = []
            sentinel_cells: list[RationalBounds] = []
            for cell in partition["cell_segments_exact"]:
                if type(cell) is not list or not cell:
                    raise CandidateStationaryVerificationFailure(
                        HOLD_MEMBER, "empty partition cell"
                    )
                if coordinate == "relative_perpendicular":
                    volume = sum(
                        (
                            _q(segment[1], HOLD_MEMBER) - _q(segment[0], HOLD_MEMBER)
                            for segment in cell
                        ),
                        Fraction(0),
                    )
                    primary = RationalBounds(volume / period, volume / period)
                    sentinel = primary
                    periodic_cells += 1
                else:
                    centre = mean if coordinate == "midpoint" else Fraction(0)
                    primary_parts: list[RationalBounds] = []
                    sentinel_parts: list[RationalBounds] = []
                    for segment in cell:
                        if type(segment) is not list or len(segment) != 2:
                            raise CandidateStationaryVerificationFailure(
                                HOLD_MEMBER, "invalid segment"
                            )
                        lower = _q(segment[0], HOLD_MEMBER)
                        upper = _q(segment[1], HOLD_MEMBER)
                        primary_parts.append(
                            _normal_probability(
                                lower,
                                upper,
                                coefficients[coordinate],
                                centre,
                                methods.primary_bits,
                            )
                        )
                        sentinel_parts.append(
                            _normal_probability(
                                lower,
                                upper,
                                coefficients[coordinate],
                                centre,
                                methods.sentinel_bits,
                            )
                        )
                    primary = _add_bounds(primary_parts)
                    sentinel = _add_bounds(sentinel_parts)
                    gaussian_cells += 1
                if primary.lower <= 0 or not primary.encloses(sentinel):
                    raise CandidateStationaryVerificationFailure(
                        HOLD_SCIENCE, "primary cell misses sentinel"
                    )
                maximum_width = max(maximum_width, (primary.upper - primary.lower) / primary.lower)
                minimum_lower = (
                    primary.lower if minimum_lower is None else min(minimum_lower, primary.lower)
                )
                primary_cells.append(primary)
                sentinel_cells.append(sentinel)
            primary_sum = _add_bounds(primary_cells)
            sentinel_sum = _add_bounds(sentinel_cells)
            start = _q(partition["domain_start_exact"], HOLD_MEMBER)
            end = start + _q(partition["domain_width_exact"], HOLD_MEMBER)
            if coordinate == "relative_perpendicular":
                primary_direct = RationalBounds(Fraction(1), Fraction(1))
                sentinel_direct = primary_direct
            else:
                centre = mean if coordinate == "midpoint" else Fraction(0)
                primary_direct = _normal_probability(
                    start,
                    end,
                    coefficients[coordinate],
                    centre,
                    methods.primary_bits,
                )
                sentinel_direct = _normal_probability(
                    start,
                    end,
                    coefficients[coordinate],
                    centre,
                    methods.sentinel_bits,
                )
            if not primary_sum.encloses(sentinel_sum) or not primary_direct.encloses(
                sentinel_direct
            ):
                raise CandidateStationaryVerificationFailure(
                    HOLD_SCIENCE, "primary axis misses sentinel"
                )
            joint = _intersect_bounds(primary_sum, primary_direct)
            axes_output.append(
                {
                    "M_x_pi_cell_intervals": [
                        {"cell_index": cell_index, **_bounds_json(bounds)}
                        for cell_index, bounds in enumerate(primary_cells)
                    ],
                    "M_x_pi_direct_domain_interval": _bounds_json(primary_direct),
                    "M_x_pi_joint_domain_interval": _bounds_json(joint),
                    "M_x_pi_sum_of_cells_interval": _bounds_json(primary_sum),
                    "cell_count": partition["size"],
                    "coordinate": coordinate,
                    "partition_path": axis_binding["partition_report_relative_path"],
                    "partition_sha256": axis_binding["partition_sha256"],
                }
            )
            sums.append(primary_sum)
            directs.append(primary_direct)
            total_cells += partition["size"]
        factorized = RationalBounds(Fraction(1), Fraction(1))
        direct = RationalBounds(Fraction(1), Fraction(1))
        for axis_sum, axis_direct in zip(sums, directs, strict=True):
            factorized = _multiply_bounds(factorized, axis_sum)
            direct = _multiply_bounds(direct, axis_direct)
        joint = _intersect_bounds(factorized, direct)
        if not 0 < joint.lower <= joint.upper <= 1:
            raise CandidateStationaryVerificationFailure(HOLD_SCIENCE, "M_L range")
        output_rows.append(
            {
                "M_L_factorized_interval": _bounds_json(factorized),
                "M_L_joint_interval": _bounds_json(joint),
                "M_L_single_domain_interval": _bounds_json(direct),
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
    if minimum_lower is None:
        raise CandidateStationaryVerificationFailure(HOLD_SCIENCE, "empty result")
    artifact = {
        "claim_boundary": {
            "backend_independence_claimed": False,
            "complete_C1": False,
            "complete_C2": False,
            "externally_committed_request": False,
            "release_eligible": False,
            "role8_or_role10_result_consumed": False,
        },
        "method": {
            "aggregation": "exact_Fraction_endpoint_sums_and_nonnegative_products",
            "dense_tensor_materialized": False,
            "exact_parameter_id": methods.exact_id,
            "parameter_sha256s": methods.digests,
            "primary_parameter_id": methods.primary_id,
            "primary_precision_bits": methods.primary_bits,
            "rounding": "directed_RoundDown_RoundUp",
            "sentinel_parameter_id": methods.sentinel_id,
            "sentinel_precision_bits": methods.sentinel_bits,
            "sentinel_semantics": "same_backend_higher_precision_containment_only",
        },
        "request": {"path": str(request_image.path), "sha256": request_image.sha256},
        "rows": output_rows,
        "runtime": _runtime(),
        "schema": ARTIFACT_SCHEMA,
        "source_pins": {
            "code_inputs": {
                role: {"path": str(images[role].path), "sha256": images[role].sha256}
                for role in request["code_inputs"]
            },
            "input_authorities": {
                role: {"path": str(images[role].path), "sha256": images[role].sha256}
                for role in request["input_authorities"]
            },
            "partitions": partition_pins,
        },
        "status": ARTIFACT_STATUS,
        "summary": {
            "all_primary_intervals_contain_sentinels": True,
            "configuration_count": len(output_rows),
            "factorized_axis_cell_count": total_cells,
            "gaussian_axis_cell_count": gaussian_cells,
            "maximum_primary_cell_relative_width_exact": _q_text(maximum_width),
            "minimum_positive_primary_cell_lower_exact": _q_text(minimum_lower),
            "periodic_axis_cell_count": periodic_cells,
            "total_virtual_tensor_state_count": sum(
                row["tensor_state_count"] for row in output_rows
            ),
        },
    }
    return canonical_bytes(artifact), artifact


def validate(request_path: Path, artifact_path: Path) -> dict[str, Any]:
    expected_raw, expected = _expected_artifact(request_path, artifact_path)
    observed = _immutable_image(artifact_path, cap=max(MAX_JSON_BYTES, len(expected_raw)))
    observed_object = _decode_canonical(observed.raw, "artifact")
    if observed.raw != expected_raw or observed_object != expected:
        raise CandidateStationaryVerificationFailure(HOLD_ARTIFACT, "complete artifact mismatch")
    return {
        "artifact_path": str(artifact_path),
        "artifact_sha256": observed.sha256,
        "configuration_count": expected["summary"]["configuration_count"],
        "schema": "encounter_continuum_c1_n0_stationary_integrals_validation_v1",
        "status": "PASS_INDEPENDENT_COMPLETE_RECOMPUTATION",
    }


def _parse_cli(argv: Sequence[str] | None) -> tuple[Path, Path]:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args(argv)
    request = _absolute(arguments.request, HOLD_REQUEST, "request CLI")
    artifact = _absolute(arguments.output, HOLD_REQUEST, "output CLI")
    if request == artifact:
        raise CandidateStationaryVerificationFailure(
            HOLD_REQUEST, "request and artifact must differ"
        )
    return request, artifact


def main(argv: Sequence[str] | None = None) -> int:
    try:
        request_path, artifact_path = _parse_cli(argv)
        receipt = validate(request_path, artifact_path)
    except CandidateStationaryVerificationFailure as error:
        print(error, file=sys.stderr)
        return 2
    print(canonical_bytes(receipt).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
