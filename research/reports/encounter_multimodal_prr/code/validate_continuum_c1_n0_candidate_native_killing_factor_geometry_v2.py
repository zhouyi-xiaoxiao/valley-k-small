"""Fail-closed protocol verifier for candidate-native role-10 killing geometry.

This is a protocol shell, not a numerical implementation.  It authenticates
the result-blind replay chain, frozen scientific authorities, runtime and
method closure, and every exact member partition.  Once those gates pass it
stops at the explicit numerical-implementation hold.  It never reads a
role-8/9 result and contains no artifact or receipt publication path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import sys
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final, Sequence

import gmpy2

REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_killing_factor_geometry_request_v3"
OUTPUT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_source_v2"
RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_validation_receipt_v1"
PLAN_SCHEMA: Final = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v1"
BUNDLE_SCHEMA: Final = "encounter_continuum_c1_n0_precommit_candidate_bundle_v1"
COMMITMENT_SCHEMA: Final = "encounter_external_predecessor_commitment_v1"
ROLE_ID: Final = 10
ROLE_NAME: Final = "role10_killing_factor_geometry"
ROLE8_NAME: Final = "role8_raw_axis_formula_primitive"
ROLE9_NAME: Final = "role9_stationary_physical_integral"
ROLE8_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_raw_axis_formula_request_v3"
ROLE9_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_stationary_integrals_request_v3"
ROLE8_OUTPUT_SCHEMA: Final = "encounter_c1_n0_raw_axis_formula_primitive_source_v2"
ROLE9_OUTPUT_SCHEMA: Final = "encounter_c1_n0_stationary_physical_integral_source_v2"
ROLE8_RECEIPT_SCHEMA: Final = "encounter_c1_n0_raw_axis_formula_primitive_validation_receipt_v1"
ROLE9_RECEIPT_SCHEMA: Final = "encounter_c1_n0_stationary_physical_integral_validation_receipt_v1"
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

MEMBER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_member_spec_v4_candidate"
MEMBER_SHA256: Final = "b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5"
MEMBER_IDENTITY_SHA256: Final = "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
PARAMETER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
PARAMETER_SHA256: Final = "e403a9576abb08d3ada884cd283cce29ce8f877b0e9843cc8d5b911c8c0b0ac5"
FACTORIZATION_SCHEMA: Final = "encounter_continuum_c1_factorization_source_v2_candidate"
FACTORIZATION_SHA256: Final = "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26"
ANTI_VACUITY_POLICY_SCHEMA: Final = "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate"
ANTI_VACUITY_POLICY_SHA256: Final = (
    "599252aa1a9fd1d65d9ff3d0faa1e21bb2609da96cca6b6fff1e61a89ebff196"
)
REFERENCE_SCHEMA: Final = "encounter_continuum_c1_reference_density_source_v1"
FORMULA_SCHEMA: Final = "encounter_continuum_c1_ideal_formula_source_v1"
CONFIGURATION_SCHEMA: Final = "encounter_physical_configuration_family_control_free_v1"
INITIAL_GEOMETRY_SCHEMA: Final = "encounter_physical_initial_analytic_source_v1"
INITIAL_PARTITION_SCHEMA: Final = "encounter_control_free_production_initial_stream_v1"
KILLING_GEOMETRY_SCHEMA: Final = "encounter_physical_killing_geometry_source_v1"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"

PRECOMMIT_CONTEXT_DOMAIN: Final = "encounter-continuum-c1-n0-shared-precommit-context-v1"
REPLAY_CONTEXT_DOMAIN: Final = "encounter-continuum-c1-n0-shared-replay-context-v1"
PRECOMMIT_PROJECTION_DOMAIN: Final = "encounter-continuum-c1-n0-role-precommit-projection-v1"
CONFIGURATION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-configuration-row-inventory-v1"
PARTITION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-partition-inventory-v1"
COMMITMENT_MESSAGE_DOMAIN: Final = "encounter-external-predecessor-commitment-message-v1"
PARAMETER_DIGEST_DOMAIN: Final = "encounter-outward-method-parameters-v4"
CONFIGURATION_INVENTORY_SHA256: Final = (
    "8da99e7910cac1f2ba6b69fb2d0ec52b21412abfa1d59c898462e138d82ebbb2"
)
PARTITION_INVENTORY_SHA256: Final = (
    "f3507f4eec07e216bd54bcf4486ab5cef1589511367f781174b89fdfe2e7b51f"
)

CONTACT_PROFILE_PARAMETER_ID: Final = "killing_contact_profile_mpfr_192_v3"
ANALYTIC_AREA_PARAMETER_ID: Final = "killing_analytic_disk_area_mpfr_256_v3"
VERIFIER_PARAMETER_ID: Final = "killing_source_independent_same_backend_verifier_v3"
CLASSIFICATION_PARAMETER_ID: Final = "killing_exact_contact_cell_classification_v3"

PARAMETER_ORDER: Final = (
    "stationary_directed_mpfr_320_v2",
    "stationary_directed_mpfr_640_sentinel_v2",
    "raw_flux_directed_mpfr_320_v2",
    "raw_flux_directed_mpfr_640_sentinel_v2",
    "raw_flux_binary64_decode_v2",
    "exact_fraction_expression_dag_v2",
    CONTACT_PROFILE_PARAMETER_ID,
    ANALYTIC_AREA_PARAMETER_ID,
    VERIFIER_PARAMETER_ID,
    CLASSIFICATION_PARAMETER_ID,
)
PARAMETER_DIGEST_ORDER: Final = (
    "1226335c739734613508bacbaba3d8fb7f6c0607557d11190fe846ba08000da7",
    "67d76049763a982144e2b41fc1722ce6e4663bccb8bdcec9e2af398d7c1511f9",
    "2393d646b5a5d1d0e0c6c3a97e91b62e9f3e74b3c4007b38b01107161a18cc38",
    "d1f3f3074f74ab276b375ef977a467d208a6d730e0b5baeeece19c1178c3caaa",
    "47e7248b048b4d042397e8f0123f5eceed2433a8b552099eb7883c2dfb60d6f8",
    "c1e11de7305a3035973e98d1913e14075f0ba3b2a32180a73689aee4c9b4b851",
    "b48ff460eb56ab91f27b26104b69874f0e0169e658ea69c71c2a6dd6f1fd30df",
    "0ade3fb790db8845715652762776073a1c2db6570bc562fec7b46a6a66c41057",
    "40907be35641ad4cfc2d64b9479d45df572adcd4ee2f7e9afdf39340ebe6b421",
    "ca866475725fe801833f8f2ec9702fe825010a69a59712c4d87f1584048fe631",
)
PARAMETER_SCOPES: Final = {
    "stationary_directed_mpfr_320_v2": ["role9_stationary_physical_integral"],
    "stationary_directed_mpfr_640_sentinel_v2": ["role9_stationary_physical_integral"],
    "raw_flux_directed_mpfr_320_v2": ["role8_raw_axis_formula_primitive"],
    "raw_flux_directed_mpfr_640_sentinel_v2": ["role8_raw_axis_formula_primitive"],
    "raw_flux_binary64_decode_v2": ["role8_raw_axis_formula_primitive"],
    "exact_fraction_expression_dag_v2": [
        "role8_raw_axis_formula_primitive",
        "role9_stationary_physical_integral",
        "same_member_mass_flux_composition",
        "symbolic_killing_composition",
    ],
    CONTACT_PROFILE_PARAMETER_ID: [ROLE_NAME],
    ANALYTIC_AREA_PARAMETER_ID: [ROLE_NAME],
    VERIFIER_PARAMETER_ID: [ROLE_NAME],
    CLASSIFICATION_PARAMETER_ID: [ROLE_NAME],
}

COORDINATES: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
EXPECTED_CONFIGURATION_COUNT: Final = 12
EXPECTED_AXIS_COUNT: Final = 36
EXPECTED_AXIS_CELL_COUNT: Final = 5_037
EXPECTED_AXIS_EDGE_COUNT: Final = 5_013
EXPECTED_PERIODIC_SEAM_COUNT: Final = 12
EXPECTED_PROFILE_INDEX_COUNT: Final = 48
EXPECTED_TOTAL_STATES: Final = 34_787_462
MAX_JSON_BYTES: Final = 8_000_000
MAX_RUNTIME_BYTES: Final = 64_000_000
MAX_JSON_DEPTH: Final = 64
MAX_INTEGER_BITS: Final = 65_536

HOLD_REQUEST: Final = "HOLD_CANDIDATE_KILLING_REQUEST"
HOLD_AUTHORITY: Final = "HOLD_CANDIDATE_KILLING_AUTHORITY"
HOLD_RUNTIME: Final = "HOLD_CANDIDATE_KILLING_RUNTIME"
HOLD_METHOD: Final = "HOLD_CANDIDATE_KILLING_METHOD"
HOLD_PARTITION: Final = "HOLD_CANDIDATE_KILLING_PARTITION"
HOLD_CANDIDATE_KILLING_NUMERICAL_IMPLEMENTATION_INCOMPLETE: Final = (
    "HOLD_CANDIDATE_KILLING_NUMERICAL_IMPLEMENTATION_INCOMPLETE"
)
HOLD_NUMERICAL_INCOMPLETE: Final = HOLD_CANDIDATE_KILLING_NUMERICAL_IMPLEMENTATION_INCOMPLETE

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
_CONTEXT_PIN_KEYS: Final = {"path", "schema", "sha256"}
_ROLE_KEYS: Final = {"role_id", "role_name"}
_OUTPUT_KEYS: Final = {"path", "schema"}
_PLAN_KEYS: Final = {
    "claim_boundary",
    "entries",
    "schema",
    "shared_context",
    "shared_precommit_context_sha256",
    "status",
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
_PLAN_CLAIM_KEYS: Final = {
    "external_predecessor_commitment_present",
    "ordered_roles_8_10_replay_executed",
    "production_same_member_bridge_accepted",
    "release_eligible",
}
_ENTRY_REQUEST_KEYS: Final = {"path", "schema", "status"}
_ENTRY_OUTPUT_KEYS: Final = {"artifact", "validation_receipt"}
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
_NATIVE_LIBRARY_ROLES: Final = ("gmpy2_extension", "libgmp", "libmpfr", "libmpc")
_NATIVE_LIBRARY_PIN_KEYS: Final = {"path", "role", "sha256"}
_RUNTIME_KEYS: Final = {"gmp", "gmpy2", "mpc", "mpfr", "python_abi"}
_INVOCATIONS_KEYS: Final = {"producer", "verifier"}
_INVOCATION_KEYS: Final = {"argv", "cwd"}
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
_PARTITION_PIN_KEYS: Final = {
    "configuration_index",
    "coordinate",
    "member_report_relative_path",
    "path",
    "sha256",
}
_METHOD_SELECTION_KEYS: Final = {
    "analytic_area_parameter_id",
    "classification_parameter_id",
    "contact_profile_parameter_id",
    "verifier_parameter_id",
}
_ROLE8_METHOD_RECORD_KEYS: Final = {"method_parameter_sha256", "parameter_id"}
_ROLE8_METHOD_SELECTION: Final = [
    {
        "method_parameter_sha256": PARAMETER_DIGEST_ORDER[2],
        "parameter_id": PARAMETER_ORDER[2],
    },
    {
        "method_parameter_sha256": PARAMETER_DIGEST_ORDER[3],
        "parameter_id": PARAMETER_ORDER[3],
    },
    {
        "method_parameter_sha256": PARAMETER_DIGEST_ORDER[4],
        "parameter_id": PARAMETER_ORDER[4],
    },
    {
        "method_parameter_sha256": PARAMETER_DIGEST_ORDER[5],
        "parameter_id": PARAMETER_ORDER[5],
    },
]
_ROLE9_METHOD_SELECTION_KEYS: Final = {
    "exact_parameter_id",
    "primary_parameter_id",
    "sentinel_parameter_id",
}
_ROLE9_METHOD_SELECTION: Final = {
    "exact_parameter_id": PARAMETER_ORDER[5],
    "primary_parameter_id": PARAMETER_ORDER[0],
    "sentinel_parameter_id": PARAMETER_ORDER[1],
}
_ROLE10_METHOD_SELECTION: Final = {
    "analytic_area_parameter_id": ANALYTIC_AREA_PARAMETER_ID,
    "classification_parameter_id": CLASSIFICATION_PARAMETER_ID,
    "contact_profile_parameter_id": CONTACT_PROFILE_PARAMETER_ID,
    "verifier_parameter_id": VERIFIER_PARAMETER_ID,
}
_EXPECTED_METHOD_SELECTION: Final = _ROLE10_METHOD_SELECTION
_ROLE_ENTRY_NAMES: Final = {8: ROLE8_NAME, 9: ROLE9_NAME, 10: ROLE_NAME}
_ROLE_REQUEST_SCHEMAS: Final = {
    8: ROLE8_REQUEST_SCHEMA,
    9: ROLE9_REQUEST_SCHEMA,
    10: REQUEST_SCHEMA,
}
_ROLE_OUTPUT_SCHEMAS: Final = {
    8: ROLE8_OUTPUT_SCHEMA,
    9: ROLE9_OUTPUT_SCHEMA,
    10: OUTPUT_SCHEMA,
}
_ROLE_RECEIPT_SCHEMAS: Final = {
    8: ROLE8_RECEIPT_SCHEMA,
    9: ROLE9_RECEIPT_SCHEMA,
    10: RECEIPT_SCHEMA,
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
_ACCEPTED_AUTHENTICATION_CLASSES: Final = {
    "distinct_operator_authenticated_signature",
    "independently_audited_predecessor_commit_hash",
    "independent_trust_domain_receipt_hash",
}
_COMMITMENT_RESULT_BLIND_ALLOWED_KEYS: Final = {
    "commitment_message_sha256",
    "no_role_8_10_outputs_observed",
    "result_blind_plan",
    "roles_8_10_outputs_observed",
    "sha256",
}
_COMMITMENT_RESULT_BLIND_ALLOWED_VALUES: Final = {
    COMMITMENT_SCHEMA,
    COMMITMENT_STATUS,
    *_ACCEPTED_AUTHENTICATION_CLASSES,
}
_COMMITMENT_EVIDENCE_TOKENS: Final = {
    "acceptance",
    "artifact",
    "digest",
    "fail",
    "observed",
    "output",
    "pass",
    "receipt",
    "result",
    "sha",
    "sha256",
}
_COMMITMENT_FREE_TEXT_FIELDS: Final = {
    "authority_identifier",
    "evidence_identifier",
    "trust_domain_identifier",
}
_COMMITMENT_COMBINED_EVIDENCE_FRAGMENTS: Final = {
    "artifact_digest",
    "artifact_sha",
    "expected_output",
    "expected_result",
    "observed_output",
    "observed_result",
    "output_digest",
    "output_sha",
    "pass_receipt",
    "production_result",
    "receipt_digest",
    "receipt_sha",
    "result_artifact",
    "result_digest",
    "result_receipt",
    "result_sha",
    "role8_result",
    "role9_result",
    "role10_result",
}
_CONTEXT_RELATIVE_PATHS: Final = {
    "anti_vacuity_policy": (
        "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json"
    ),
    "configuration": "artifacts/data/physical_configuration_family_control_free_v1.json",
    "factorization": "artifacts/data/continuum_c1_factorization_source_v2_candidate.json",
    "ideal_formula": "artifacts/data/continuum_c1_ideal_formula_source_v1.json",
    "member_spec": "artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json",
    "method_parameter_registry": (
        "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json"
    ),
    "reference_density": "artifacts/data/continuum_c1_reference_density_source_v1.json",
}
_RESULT_DERIVED_FRAGMENTS: Final = (
    "artifact_sha",
    "expected_output",
    "expected_result",
    "observed_output",
    "observed_result",
    "output_digest",
    "output_sha",
    "production_result",
    "result_digest",
    "result_sha",
    "role8_result",
    "role9_result",
    "role10_result",
    "stream_digest",
    "stream_sha",
)


class CandidateKillingVerificationFailure(RuntimeError):
    """A fail-closed protocol, authority, method, partition, or final hold."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        message = code if code == HOLD_NUMERICAL_INCOMPLETE else f"{code}: {detail}"
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class FileImage:
    path: Path
    raw: bytes
    sha256: str


@dataclass(frozen=True, slots=True)
class ReplayProtocol:
    request: dict[str, Any]
    request_image: FileImage
    plan: dict[str, Any]
    plan_image: FileImage
    bundle: dict[str, Any]
    bundle_image: FileImage
    commitment: dict[str, Any]
    commitment_image: FileImage
    entry: dict[str, Any]
    artifact_path: Path
    receipt_path: Path


def _fail(code: str, detail: str) -> None:
    raise CandidateKillingVerificationFailure(code, detail)


def _duplicate_rejector(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            _fail(HOLD_AUTHORITY, "duplicate or invalid JSON key")
        result[key] = value
    return result


def _check_json_tree(value: Any, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        _fail(HOLD_AUTHORITY, "JSON depth cap exceeded")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if value.bit_length() > MAX_INTEGER_BITS:
            _fail(HOLD_AUTHORITY, "JSON integer cap exceeded")
        return
    if type(value) is float:
        _fail(HOLD_AUTHORITY, "JSON floating literals are forbidden")
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            _fail(HOLD_AUTHORITY, "non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _check_json_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                _fail(HOLD_AUTHORITY, "invalid JSON key")
            _check_json_tree(item, depth + 1)
        return
    _fail(HOLD_AUTHORITY, "unsupported JSON value")


def canonical_bytes(value: Any) -> bytes:
    _check_json_tree(value)
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def _decode_json(raw: bytes, label: str, *, require_canonical: bool = True) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_duplicate_rejector,
            parse_float=lambda token: (_ for _ in ()).throw(
                CandidateKillingVerificationFailure(
                    HOLD_AUTHORITY, f"{label}: floating token {token}"
                )
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                CandidateKillingVerificationFailure(
                    HOLD_AUTHORITY, f"{label}: nonfinite token {token}"
                )
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise CandidateKillingVerificationFailure(
            HOLD_AUTHORITY, f"{label}: invalid ASCII JSON"
        ) from error
    _check_json_tree(value)
    if type(value) is not dict:
        _fail(HOLD_AUTHORITY, f"{label}: JSON object required")
    if require_canonical and canonical_bytes(value) != raw:
        _fail(HOLD_AUTHORITY, f"{label}: noncanonical JSON")
    return value


def _exact_keys(value: Any, expected: set[str], code: str, label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != expected:
        _fail(code, f"{label}: exact-key mismatch")
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


def _valid_sha(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _nonempty(value: Any) -> bool:
    return type(value) is str and bool(value)


def _absolute(value: Any, code: str, label: str) -> Path:
    if not _nonempty(value):
        _fail(code, f"{label}: absolute path required")
    path = Path(value)
    if not path.is_absolute() or path != Path(os.path.abspath(path)):
        _fail(code, f"{label}: canonical absolute path required")
    return path


def _directory_flags() -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NONBLOCK
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _close_descriptors(descriptors: Sequence[int]) -> None:
    for descriptor in reversed(descriptors):
        try:
            os.close(descriptor)
        except OSError:
            pass


def _open_anchored_directory_chain(
    directory: Path,
    *,
    code: str,
    label: str,
) -> tuple[list[int], list[tuple[int, str, int, int, int]]]:
    lexical = Path(os.path.abspath(directory))
    if not directory.is_absolute() or directory != lexical:
        _fail(code, f"{label}: canonical absolute directory required")
    descriptors: list[int] = []
    links: list[tuple[int, str, int, int, int]] = []
    try:
        root = os.open(directory.anchor, _directory_flags())
        descriptors.append(root)
        if not stat.S_ISDIR(os.fstat(root).st_mode):
            _fail(code, f"{label}: filesystem anchor is not a directory")
        for component in directory.parts[1:]:
            parent = descriptors[-1]
            child = os.open(component, _directory_flags(), dir_fd=parent)
            descriptors.append(child)
            opened = os.fstat(child)
            linked = os.stat(component, dir_fd=parent, follow_symlinks=False)
            if (
                not stat.S_ISDIR(opened.st_mode)
                or not stat.S_ISDIR(linked.st_mode)
                or (opened.st_dev, opened.st_ino) != (linked.st_dev, linked.st_ino)
            ):
                _fail(code, f"{label}: directory component identity mismatch")
            links.append((parent, component, child, opened.st_dev, opened.st_ino))
    except CandidateKillingVerificationFailure:
        _close_descriptors(descriptors)
        raise
    except OSError as error:
        _close_descriptors(descriptors)
        raise CandidateKillingVerificationFailure(
            code,
            f"{label}: symlinked or unavailable ancestor directory",
        ) from error
    return descriptors, links


def _revalidate_anchored_directory_chain(
    links: Sequence[tuple[int, str, int, int, int]],
    *,
    code: str,
    label: str,
) -> None:
    try:
        for parent, component, child, device, inode in links:
            opened = os.fstat(child)
            linked = os.stat(component, dir_fd=parent, follow_symlinks=False)
            if (
                not stat.S_ISDIR(opened.st_mode)
                or not stat.S_ISDIR(linked.st_mode)
                or (opened.st_dev, opened.st_ino) != (device, inode)
                or (linked.st_dev, linked.st_ino) != (device, inode)
            ):
                _fail(code, f"{label}: anchored directory chain changed")
    except CandidateKillingVerificationFailure:
        raise
    except OSError as error:
        raise CandidateKillingVerificationFailure(
            code,
            f"{label}: anchored directory chain changed",
        ) from error


def _require_anchored_directory(directory: Path, *, code: str, label: str) -> None:
    descriptors, links = _open_anchored_directory_chain(
        directory,
        code=code,
        label=label,
    )
    try:
        _revalidate_anchored_directory_chain(links, code=code, label=label)
    finally:
        _close_descriptors(descriptors)


def _immutable_image(
    path: Path,
    cap: int = MAX_JSON_BYTES,
    *,
    code: str = HOLD_AUTHORITY,
    label: str = "immutable input",
    require_read_only: bool = True,
) -> FileImage:
    lexical = Path(os.path.abspath(path))
    if not path.is_absolute() or path != lexical or not path.name:
        _fail(code, f"{label}: canonical absolute input path required")
    directories, links = _open_anchored_directory_chain(
        path.parent,
        code=code,
        label=label,
    )
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    try:
        descriptor = os.open(path.name, flags, dir_fd=directories[-1])
        opened = os.fstat(descriptor)
        linked_before = os.stat(
            path.name,
            dir_fd=directories[-1],
            follow_symlinks=False,
        )
        identity = (
            opened.st_dev,
            opened.st_ino,
            opened.st_mode,
            opened.st_nlink,
            opened.st_uid,
            opened.st_size,
            opened.st_mtime_ns,
            opened.st_ctime_ns,
        )
        if (
            not stat.S_ISREG(opened.st_mode)
            or not stat.S_ISREG(linked_before.st_mode)
            or (opened.st_dev, opened.st_ino) != (linked_before.st_dev, linked_before.st_ino)
            or opened.st_uid != os.getuid()
            or opened.st_nlink != 1
            or (require_read_only and opened.st_mode & 0o222)
            or not 0 < opened.st_size <= cap
        ):
            _fail(code, f"{label}: not an owned immutable single-link regular file")
        chunks: list[bytes] = []
        remaining = opened.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1 << 20))
            if not chunk:
                _fail(code, f"{label}: short immutable read")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            _fail(code, f"{label}: immutable input grew")
        after = os.fstat(descriptor)
        after_identity = (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_nlink,
            after.st_uid,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        linked_after = os.stat(
            path.name,
            dir_fd=directories[-1],
            follow_symlinks=False,
        )
        if (
            identity != after_identity
            or not stat.S_ISREG(linked_after.st_mode)
            or (linked_after.st_dev, linked_after.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            _fail(code, f"{label}: immutable input changed")
        _revalidate_anchored_directory_chain(
            links,
            code=code,
            label=label,
        )
    except CandidateKillingVerificationFailure:
        raise
    except OSError as error:
        raise CandidateKillingVerificationFailure(
            code,
            f"{label}: symlinked path component or immutable input open failed",
        ) from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
        _close_descriptors(directories)
    raw = b"".join(chunks)
    return FileImage(path=path, raw=raw, sha256=hashlib.sha256(raw).hexdigest())


def _read_pin(pin: Any, label: str, *, code: str = HOLD_REQUEST) -> FileImage:
    current = _exact_keys(pin, _PIN_KEYS, code, label)
    path = _absolute(current["path"], code, f"{label} path")
    if not _valid_sha(current["sha256"]):
        _fail(code, f"{label}: invalid SHA-256")
    image = _immutable_image(path, code=code, label=label)
    if image.sha256 != current["sha256"]:
        _fail(code, f"{label}: SHA-256 mismatch")
    return image


def _domain_digest(domain: str, value: Any) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\0" + canonical_bytes(value)).hexdigest()


def _normalized_result_blind_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def _walk_result_blind_text(value: Any) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    if type(value) is dict:
        for key, item in value.items():
            result.append(("key", key))
            result.extend(_walk_result_blind_text(item))
    elif type(value) is list:
        for item in value:
            result.extend(_walk_result_blind_text(item))
    elif type(value) is str:
        result.append(("string value", value))
    return result


def _walk_commitment_string_fields(
    value: Any,
    field: str = "",
) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    if type(value) is str:
        result.append((field, value))
    elif type(value) is dict:
        for key, item in value.items():
            result.extend(_walk_commitment_string_fields(item, key))
    elif type(value) is list:
        for item in value:
            result.extend(_walk_commitment_string_fields(item, field))
    return result


def _validate_result_blind_keys(value: Any, label: str) -> None:
    """Reject result-derived metadata in keys and arbitrarily nested string values."""

    for kind, text in _walk_result_blind_text(value):
        normalized = _normalized_result_blind_text(text)
        compact = "".join(normalized.split("_"))
        fragments = (
            ("observed", *_RESULT_DERIVED_FRAGMENTS) if kind == "key" else _RESULT_DERIVED_FRAGMENTS
        )
        if any(
            fragment in normalized or "".join(fragment.split("_")) in compact
            for fragment in fragments
        ):
            _fail(HOLD_REQUEST, f"{label}: result leakage {kind} forbidden: {text}")


def _validate_commitment_result_blind(value: Any, label: str) -> None:
    """Reject future-result evidence outside exact structural vocabulary."""

    for key in (text for kind, text in _walk_result_blind_text(value) if kind == "key"):
        if key in _COMMITMENT_RESULT_BLIND_ALLOWED_KEYS:
            continue
        normalized = _normalized_result_blind_text(key)
        token_list = [token for token in normalized.split("_") if token]
        tokens = set(token_list)
        compact = "".join(token_list)
        if (tokens & _COMMITMENT_EVIDENCE_TOKENS) or any(
            fragment in normalized or "".join(fragment.split("_")) in compact
            for fragment in _COMMITMENT_COMBINED_EVIDENCE_FRAGMENTS
        ):
            _fail(HOLD_REQUEST, f"{label}: future-result evidence key forbidden: {key}")
    for field, text in _walk_commitment_string_fields(value):
        if text in _COMMITMENT_RESULT_BLIND_ALLOWED_VALUES:
            continue
        normalized = _normalized_result_blind_text(text)
        token_list = [token for token in normalized.split("_") if token]
        tokens = set(token_list)
        compact = "".join(token_list)
        if (field in _COMMITMENT_FREE_TEXT_FIELDS and tokens & _COMMITMENT_EVIDENCE_TOKENS) or any(
            fragment in normalized or "".join(fragment.split("_")) in compact
            for fragment in _COMMITMENT_COMBINED_EVIDENCE_FRAGMENTS
        ):
            _fail(HOLD_REQUEST, f"{label}: future-result evidence value forbidden: {text}")


def _false_boundary(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    current = _exact_keys(value, expected, HOLD_REQUEST, label)
    if any(item is not False for item in current.values()):
        _fail(HOLD_REQUEST, f"{label}: claim promotion")
    return current


def _same_pin(left: Any, right: Any, label: str, *, code: str = HOLD_REQUEST) -> None:
    if _exact_keys(left, _PIN_KEYS, code, f"{label} left") != _exact_keys(
        right, _PIN_KEYS, code, f"{label} right"
    ):
        _fail(code, f"{label}: pin mismatch")


def _context_pin(
    value: Any,
    schema: str,
    relative_path: str,
    label: str,
) -> dict[str, str]:
    current = _exact_keys(value, _CONTEXT_PIN_KEYS, HOLD_REQUEST, label)
    path = PurePosixPath(current["path"]) if _nonempty(current["path"]) else None
    if (
        path is None
        or path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != relative_path
        or current["schema"] != schema
        or not _valid_sha(current["sha256"])
    ):
        _fail(HOLD_REQUEST, f"{label}: contextual pin mismatch")
    return current


def _binding_matches_pin(binding: Any, pin: Any, label: str) -> None:
    left = _exact_keys(binding, _PIN_KEYS, HOLD_AUTHORITY, f"{label} binding")
    right = _exact_keys(pin, _PIN_KEYS, HOLD_AUTHORITY, f"{label} pin")
    if left["sha256"] != right["sha256"] or not _valid_sha(left["sha256"]):
        _fail(HOLD_AUTHORITY, f"{label}: digest mismatch")
    right_path = _absolute(right["path"], HOLD_AUTHORITY, f"{label} pinned path")
    left_path = PurePosixPath(left["path"]) if _nonempty(left["path"]) else None
    if left_path is None or ".." in left_path.parts:
        _fail(HOLD_AUTHORITY, f"{label}: invalid binding path")
    if left_path.is_absolute():
        if Path(left["path"]) != right_path:
            _fail(HOLD_AUTHORITY, f"{label}: absolute path mismatch")
    elif tuple(right_path.parts[-len(left_path.parts) :]) != left_path.parts:
        _fail(HOLD_AUTHORITY, f"{label}: relative path suffix mismatch")


def _runtime_versions() -> dict[str, str]:
    return {
        "gmp": gmpy2.mp_version(),
        "gmpy2": gmpy2.__version__,
        "mpc": gmpy2.mpc_version(),
        "mpfr": gmpy2.mpfr_version(),
        "python_abi": f"CPython {sys.version_info.major}.{sys.version_info.minor}",
    }


def _read_runtime_pin(pin: Any, label: str) -> FileImage:
    current = _exact_keys(pin, _PIN_KEYS, HOLD_RUNTIME, label)
    path = _absolute(current["path"], HOLD_RUNTIME, f"{label} path")
    if not _valid_sha(current["sha256"]):
        _fail(HOLD_RUNTIME, f"{label}: invalid SHA-256")
    image = _immutable_image(
        path,
        MAX_RUNTIME_BYTES,
        code=HOLD_RUNTIME,
        label=label,
        require_read_only=False,
    )
    if image.sha256 != current["sha256"]:
        _fail(HOLD_RUNTIME, f"{label}: SHA-256 mismatch")
    return image


def _validate_role8_runtime_closure(
    value: Any,
    label: str,
) -> tuple[FileImage, FileImage, frozenset[Path]]:
    pin = _exact_keys(value, _CONTEXT_PIN_KEYS, HOLD_REQUEST, f"{label} pin")
    if pin["schema"] != ROLE8_RUNTIME_CLOSURE_SCHEMA or not _valid_sha(pin["sha256"]):
        _fail(HOLD_REQUEST, f"{label}: external runtime-closure pin mismatch")
    closure_path = _absolute(pin["path"], HOLD_REQUEST, f"{label} path")
    closure_image = _immutable_image(
        closure_path,
        code=HOLD_RUNTIME,
        label=label,
    )
    if closure_image.sha256 != pin["sha256"]:
        _fail(HOLD_RUNTIME, f"{label}: external runtime-closure SHA-256 mismatch")
    closure = _decode_json(closure_image.raw, label)
    _exact_keys(closure, _ROLE8_RUNTIME_CLOSURE_KEYS, HOLD_RUNTIME, label)
    claims = _exact_keys(
        closure["claim_boundary"],
        _ROLE8_RUNTIME_CLAIM_KEYS,
        HOLD_RUNTIME,
        f"{label} claims",
    )
    if (
        closure["schema"] != ROLE8_RUNTIME_CLOSURE_SCHEMA
        or closure["status"] != ROLE8_RUNTIME_CLOSURE_STATUS
        or not _json_exactly_equal(claims, _ROLE8_RUNTIME_CLAIMS)
        or closure["native_runtime"] != _runtime_versions()
        or not _json_exactly_equal(closure["python_imports"], _ROLE8_PYTHON_IMPORTS)
        or closure["report_local_dependencies"] != []
    ):
        _fail(HOLD_RUNTIME, f"{label}: external runtime-closure semantics mismatch")

    code_inputs = _exact_keys(
        closure["code_inputs"],
        {"producer", "verifier"},
        HOLD_RUNTIME,
        f"{label} code inputs",
    )
    source_images = {
        role: _read_pin(pin_value, f"{label} {role} source", code=HOLD_RUNTIME)
        for role, pin_value in code_inputs.items()
    }

    executable = _read_runtime_pin(
        closure["python_executable"],
        f"{label} Python executable",
    )
    if executable.path != Path(sys.executable).resolve():
        _fail(HOLD_RUNTIME, f"{label}: Python executable mismatch")

    package_directory = Path(gmpy2.__file__).resolve().parent
    expected_candidates = {
        "gmpy2_extension": sorted(package_directory.glob("gmpy2*.so")),
        "libgmp": sorted((package_directory.parent / "gmpy2.libs").glob("libgmp.*.dylib")),
        "libmpfr": sorted((package_directory.parent / "gmpy2.libs").glob("libmpfr.*.dylib")),
        "libmpc": sorted((package_directory.parent / "gmpy2.libs").glob("libmpc.*.dylib")),
    }
    native_libraries = closure["native_libraries"]
    if (
        any(len(paths) != 1 for paths in expected_candidates.values())
        or type(native_libraries) is not list
        or len(native_libraries) != len(_NATIVE_LIBRARY_ROLES)
    ):
        _fail(HOLD_RUNTIME, f"{label}: native-library discovery/count mismatch")
    native_images: list[FileImage] = []
    for ordinal, raw_pin in enumerate(native_libraries):
        native_pin = _exact_keys(
            raw_pin,
            _NATIVE_LIBRARY_PIN_KEYS,
            HOLD_RUNTIME,
            f"{label} native library {ordinal}",
        )
        expected_role = _NATIVE_LIBRARY_ROLES[ordinal]
        if native_pin["role"] != expected_role:
            _fail(HOLD_RUNTIME, f"{label}: native-library role/order mismatch")
        image = _read_runtime_pin(
            {"path": native_pin["path"], "sha256": native_pin["sha256"]},
            f"{label} native library {expected_role}",
        )
        if image.path != expected_candidates[expected_role][0].resolve():
            _fail(HOLD_RUNTIME, f"{label}: native-library path mismatch")
        native_images.append(image)
    dependency_paths = {
        closure_image.path,
        executable.path,
        *(image.path for image in source_images.values()),
        *(image.path for image in native_images),
    }
    return (
        source_images["producer"],
        source_images["verifier"],
        frozenset(dependency_paths),
    )


def _validate_inline_runtime_closure(
    value: Any,
    label: str,
) -> tuple[FileImage, FileImage, frozenset[Path]]:
    closure = _exact_keys(value, _RUNTIME_CLOSURE_KEYS, HOLD_REQUEST, label)
    required = _exact_keys(
        closure["runtime_requirements"],
        _RUNTIME_KEYS,
        HOLD_RUNTIME,
        f"{label} requirements",
    )
    if required != _runtime_versions():
        _fail(HOLD_RUNTIME, f"{label}: runtime requirements mismatch")
    producer = _read_pin(
        closure["producer"],
        f"{label} producer source",
        code=HOLD_RUNTIME,
    )
    verifier = _read_pin(
        closure["verifier"],
        f"{label} verifier source",
        code=HOLD_RUNTIME,
    )
    return producer, verifier, frozenset({producer.path, verifier.path})


def _validate_plan_partition_bindings(
    value: Any,
    label: str,
) -> tuple[bytes, frozenset[Path]]:
    if type(value) is not list or len(value) != EXPECTED_AXIS_COUNT:
        _fail(HOLD_PARTITION, f"{label}: partition binding cardinality mismatch")
    dependency_paths: set[Path] = set()
    for ordinal, raw_pin in enumerate(value):
        pin = _exact_keys(
            raw_pin,
            _PARTITION_PIN_KEYS,
            HOLD_PARTITION,
            f"{label} partition {ordinal}",
        )
        expected_index, coordinate_ordinal = divmod(ordinal, len(COORDINATES))
        expected_coordinate = COORDINATES[coordinate_ordinal]
        relative = pin["member_report_relative_path"]
        pure = PurePosixPath(relative) if _nonempty(relative) else None
        absolute = _absolute(pin["path"], HOLD_PARTITION, f"{label} partition path {ordinal}")
        if (
            type(pin["configuration_index"]) is not int
            or pin["configuration_index"] != expected_index
            or pin["coordinate"] != expected_coordinate
            or pure is None
            or pure.is_absolute()
            or not pure.parts
            or any(part in {"", ".", ".."} for part in pure.parts)
            or pure.as_posix() != relative
            or tuple(absolute.parts[-len(pure.parts) :]) != pure.parts
            or not _valid_sha(pin["sha256"])
        ):
            _fail(HOLD_PARTITION, f"{label}: partition binding mismatch at {ordinal}")
        image = _immutable_image(
            absolute,
            code=HOLD_PARTITION,
            label=f"{label} partition {ordinal}",
        )
        if image.sha256 != pin["sha256"]:
            _fail(HOLD_PARTITION, f"{label}: partition SHA-256 mismatch at {ordinal}")
        dependency_paths.add(image.path)
    return canonical_bytes(value), frozenset(dependency_paths)


def _validate_plan_entry_semantics(
    entry: dict[str, Any],
    *,
    role: int,
    shared_context: dict[str, Any],
) -> tuple[Path, Path, Path, bytes, frozenset[Path]]:
    label = f"role-{role} plan entry"
    dependency_paths: set[Path] = set()
    if (
        type(entry["role"]) is not int
        or entry["role"] != role
        or entry["entry_id"] != _ROLE_ENTRY_NAMES[role]
    ):
        _fail(HOLD_REQUEST, f"{label}: identity mismatch")

    request = _exact_keys(
        entry["request"],
        _ENTRY_REQUEST_KEYS,
        HOLD_REQUEST,
        f"{label} request",
    )
    request_path = _absolute(request["path"], HOLD_REQUEST, f"{label} request path")
    if request != {
        "path": str(request_path),
        "schema": _ROLE_REQUEST_SCHEMAS[role],
        "status": REQUEST_STATUS,
    }:
        _fail(HOLD_REQUEST, f"{label}: request contract mismatch")

    outputs = _exact_keys(
        entry["outputs"],
        _ENTRY_OUTPUT_KEYS,
        HOLD_REQUEST,
        f"{label} outputs",
    )
    artifact = _exact_keys(
        outputs["artifact"],
        _OUTPUT_KEYS,
        HOLD_REQUEST,
        f"{label} artifact",
    )
    receipt = _exact_keys(
        outputs["validation_receipt"],
        _OUTPUT_KEYS,
        HOLD_REQUEST,
        f"{label} receipt",
    )
    artifact_path = _absolute(artifact["path"], HOLD_REQUEST, f"{label} artifact path")
    receipt_path = _absolute(receipt["path"], HOLD_REQUEST, f"{label} receipt path")
    if (
        artifact["schema"] != _ROLE_OUTPUT_SCHEMAS[role]
        or receipt["schema"] != _ROLE_RECEIPT_SCHEMAS[role]
        or len({request_path, artifact_path, receipt_path}) != 3
    ):
        _fail(HOLD_REQUEST, f"{label}: output contract mismatch")
    for slot_name, slot_path in (
        ("request", request_path),
        ("artifact", artifact_path),
        ("receipt", receipt_path),
    ):
        _require_anchored_directory(
            slot_path.parent,
            code=HOLD_REQUEST,
            label=f"{label} {slot_name} parent",
        )

    if role == 8:
        producer_image, verifier_image, runtime_paths = _validate_role8_runtime_closure(
            entry["implementation_runtime_closure"],
            f"{label} runtime closure",
        )
        invocation_prefix = [sys.executable, "-I", "-B"]
    else:
        producer_image, verifier_image, runtime_paths = _validate_inline_runtime_closure(
            entry["implementation_runtime_closure"],
            f"{label} runtime closure",
        )
        invocation_prefix = [sys.executable]
    dependency_paths.update(runtime_paths)
    producer_path = producer_image.path
    verifier_path = verifier_image.path
    expected_source_names = _ROLE_SOURCE_FILENAMES[role]
    if (
        producer_path.name != expected_source_names[0]
        or verifier_path.name != expected_source_names[1]
        or producer_path.parent != verifier_path.parent
    ):
        _fail(HOLD_RUNTIME, f"{label}: source identity mismatch")

    invocations = _exact_keys(
        entry["invocations"],
        _INVOCATIONS_KEYS,
        HOLD_REQUEST,
        f"{label} invocations",
    )
    for invocation_role in ("producer", "verifier"):
        invocation = _exact_keys(
            invocations[invocation_role],
            _INVOCATION_KEYS,
            HOLD_REQUEST,
            f"{label} {invocation_role} invocation",
        )
        if (
            type(invocation["argv"]) is not list
            or any(not _nonempty(argument) for argument in invocation["argv"])
            or not _nonempty(invocation["cwd"])
        ):
            _fail(HOLD_REQUEST, f"{label}: invocation shape mismatch")
        cwd = _absolute(
            invocation["cwd"],
            HOLD_REQUEST,
            f"{label} {invocation_role} cwd",
        )
        _require_anchored_directory(
            cwd,
            code=HOLD_REQUEST,
            label=f"{label} {invocation_role} cwd",
        )
    expected_cwd = producer_path.parent.parent
    expected_invocations = {
        "producer": {
            "argv": [
                *invocation_prefix,
                str(producer_path),
                "--request",
                str(request_path),
                "--output",
                str(artifact_path),
            ],
            "cwd": str(expected_cwd),
        },
        "verifier": {
            "argv": [
                *invocation_prefix,
                str(verifier_path),
                "--request",
                str(request_path),
                "--output",
                str(artifact_path),
                "--receipt",
                str(receipt_path),
            ],
            "cwd": str(expected_cwd),
        },
    }
    if not _json_exactly_equal(invocations, expected_invocations):
        _fail(HOLD_REQUEST, f"{label}: exact invocation mismatch")

    authority_keys = _ROLE8_INPUT_AUTHORITY_ROLES if role == 8 else _INPUT_AUTHORITY_ROLES
    authorities = _exact_keys(
        entry["input_authorities"],
        authority_keys,
        HOLD_REQUEST,
        f"{label} input authorities",
    )
    for authority_role, authority_pin in authorities.items():
        authority_image = _read_pin(
            authority_pin,
            f"{label} authority {authority_role}",
            code=HOLD_AUTHORITY,
        )
        dependency_paths.add(authority_image.path)
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
        context = shared_context[context_role]
        _binding_matches_pin(
            {"path": context["path"], "sha256": context["sha256"]},
            authorities[authority_role],
            f"{label} shared {authority_role}",
        )

    method_selection = entry["method_selection"]
    if role == 8:
        if type(method_selection) is not list or len(method_selection) != len(
            _ROLE8_METHOD_SELECTION
        ):
            _fail(HOLD_METHOD, f"{label}: ordered method record count mismatch")
        for ordinal, record in enumerate(method_selection):
            _exact_keys(
                record,
                _ROLE8_METHOD_RECORD_KEYS,
                HOLD_METHOD,
                f"{label} method record {ordinal}",
            )
        if not _json_exactly_equal(method_selection, _ROLE8_METHOD_SELECTION):
            _fail(HOLD_METHOD, f"{label}: ordered method records mismatch")
    elif role == 9:
        selected = _exact_keys(
            method_selection,
            _ROLE9_METHOD_SELECTION_KEYS,
            HOLD_METHOD,
            f"{label} method selection",
        )
        if not _json_exactly_equal(selected, _ROLE9_METHOD_SELECTION):
            _fail(HOLD_METHOD, f"{label}: method-ID selection mismatch")
    else:
        selected = _exact_keys(
            method_selection,
            _METHOD_SELECTION_KEYS,
            HOLD_METHOD,
            f"{label} method selection",
        )
        if not _json_exactly_equal(selected, _ROLE10_METHOD_SELECTION):
            _fail(HOLD_METHOD, f"{label}: method-ID selection mismatch")

    partition_bytes, partition_paths = _validate_plan_partition_bindings(
        entry["partition_path_bindings"],
        label,
    )
    dependency_paths.update(partition_paths)
    return (
        request_path,
        artifact_path,
        receipt_path,
        partition_bytes,
        frozenset(dependency_paths),
    )


def _validate_all_plan_entries(
    entries: list[dict[str, Any]],
    shared_context: dict[str, Any],
) -> tuple[dict[int, tuple[Path, Path, Path]], frozenset[Path]]:
    slots: list[Path] = []
    validated: dict[int, tuple[Path, Path, Path]] = {}
    dependency_paths: set[Path] = set()
    reference_partitions: bytes | None = None
    for role, entry in zip((8, 9, 10), entries, strict=True):
        (
            request_path,
            artifact_path,
            receipt_path,
            partition_bytes,
            entry_dependencies,
        ) = _validate_plan_entry_semantics(
            entry,
            role=role,
            shared_context=shared_context,
        )
        role_slots = (request_path, artifact_path, receipt_path)
        validated[role] = role_slots
        slots.extend(role_slots)
        dependency_paths.update(entry_dependencies)
        if reference_partitions is None:
            reference_partitions = partition_bytes
        elif partition_bytes != reference_partitions:
            _fail(HOLD_PARTITION, "roles 8--10 partition bindings differ")
    if len(set(slots)) != 9:
        _fail(HOLD_REQUEST, "roles 8--10 replay slots collide")
    output_paths = {
        path
        for _, artifact_path, receipt_path in validated.values()
        for path in (artifact_path, receipt_path)
    }
    if output_paths & dependency_paths:
        _fail(HOLD_REQUEST, "planned output aliases a replay dependency")
    role8_authorities = entries[0]["input_authorities"]
    for entry in entries[1:]:
        for authority_role in _ROLE8_INPUT_AUTHORITY_ROLES:
            if not _json_exactly_equal(
                entry["input_authorities"][authority_role],
                role8_authorities[authority_role],
            ):
                _fail(
                    HOLD_AUTHORITY,
                    f"roles 8--10 authority pin differs: {authority_role}",
                )
    if not _json_exactly_equal(
        entries[1]["input_authorities"]["configuration_initial_geometry"],
        entries[2]["input_authorities"]["configuration_initial_geometry"],
    ):
        _fail(
            HOLD_AUTHORITY,
            "roles 9--10 configuration_initial_geometry authority differs",
        )
    return validated, frozenset(dependency_paths)


def _load_protocol(
    request_path: Path,
    artifact_path: Path,
    receipt_path: Path | None,
) -> ReplayProtocol:
    request_image = _immutable_image(
        request_path,
        code=HOLD_REQUEST,
        label="request",
    )
    request = _decode_json(request_image.raw, "request")
    _exact_keys(request, _REQUEST_KEYS, HOLD_REQUEST, "request")
    _validate_result_blind_keys(request, "request")
    if (
        request["schema"] != REQUEST_SCHEMA
        or request["status"] != REQUEST_STATUS
        or request["plan_entry_id"] != ROLE_NAME
        or _exact_keys(request["role"], _ROLE_KEYS, HOLD_REQUEST, "request role")
        != {"role_id": ROLE_ID, "role_name": ROLE_NAME}
    ):
        _fail(HOLD_REQUEST, "request boundary mismatch")

    plan_image = _read_pin(request["plan"], "replay plan", code=HOLD_REQUEST)
    plan = _decode_json(plan_image.raw, "replay plan")
    _exact_keys(plan, _PLAN_KEYS, HOLD_REQUEST, "replay plan")
    if plan["schema"] != PLAN_SCHEMA or plan["status"] != PLAN_STATUS:
        _fail(HOLD_REQUEST, "replay-plan schema/status mismatch")
    _false_boundary(plan["claim_boundary"], _PLAN_CLAIM_KEYS, "replay-plan claims")
    _validate_result_blind_keys(plan, "replay plan")

    shared = _exact_keys(
        plan["shared_context"], _SHARED_CONTEXT_KEYS, HOLD_REQUEST, "shared context"
    )
    schemas = {
        "anti_vacuity_policy": ANTI_VACUITY_POLICY_SCHEMA,
        "configuration": CONFIGURATION_SCHEMA,
        "factorization": FACTORIZATION_SCHEMA,
        "ideal_formula": FORMULA_SCHEMA,
        "member_spec": MEMBER_SCHEMA,
        "method_parameter_registry": PARAMETER_SCHEMA,
        "reference_density": REFERENCE_SCHEMA,
    }
    for key, schema in schemas.items():
        _context_pin(
            shared[key],
            schema,
            _CONTEXT_RELATIVE_PATHS[key],
            f"shared {key}",
        )
    if (
        shared["member_identity_sha256"] != MEMBER_IDENTITY_SHA256
        or shared["member_spec"]["sha256"] != MEMBER_SHA256
        or shared["method_parameter_registry"]["sha256"] != PARAMETER_SHA256
        or shared["factorization"]["sha256"] != FACTORIZATION_SHA256
        or shared["anti_vacuity_policy"]["sha256"] != ANTI_VACUITY_POLICY_SHA256
        or shared["configuration_row_inventory_sha256"] != CONFIGURATION_INVENTORY_SHA256
        or shared["partition_inventory_sha256"] != PARTITION_INVENTORY_SHA256
    ):
        _fail(HOLD_REQUEST, "shared-context authority mismatch")
    precommit = _domain_digest(PRECOMMIT_CONTEXT_DOMAIN, shared)
    if (
        plan["shared_precommit_context_sha256"] != precommit
        or request["shared_precommit_context_sha256"] != precommit
    ):
        _fail(HOLD_REQUEST, "shared precommit digest mismatch")

    entries = plan["entries"]
    expected_names = [_ROLE_ENTRY_NAMES[role] for role in (8, 9, 10)]
    if (
        type(entries) is not list
        or len(entries) != 3
        or any(type(entry) is not dict for entry in entries)
        or [entry.get("role") for entry in entries] != [8, 9, 10]
        or any(type(entry.get("role")) is not int for entry in entries)
        or [entry.get("entry_id") for entry in entries] != expected_names
    ):
        _fail(HOLD_REQUEST, "replay-plan role ordering mismatch")
    for entry in entries:
        _exact_keys(entry, _PLAN_ENTRY_KEYS, HOLD_REQUEST, "plan entry")
        projection = {
            key: value for key, value in entry.items() if key != "precommit_projection_sha256"
        }
        if entry["precommit_projection_sha256"] != _domain_digest(
            PRECOMMIT_PROJECTION_DOMAIN, projection
        ):
            _fail(HOLD_REQUEST, "role precommit projection mismatch")
    validated_slots, planned_dependency_paths = _validate_all_plan_entries(
        entries,
        shared,
    )
    entry = entries[2]
    planned_request_path, planned_artifact, planned_receipt = validated_slots[ROLE_ID]
    if planned_request_path != request_path:
        _fail(HOLD_REQUEST, "planned request mismatch")

    if planned_artifact != artifact_path or (
        receipt_path is not None and planned_receipt != receipt_path
    ):
        _fail(HOLD_REQUEST, "planned output/receipt binding mismatch")

    authorities = entry["input_authorities"]

    commitment_image = _read_pin(
        request["external_predecessor_commitment"],
        "external commitment",
        code=HOLD_REQUEST,
    )
    commitment = _decode_json(commitment_image.raw, "external commitment")
    _exact_keys(commitment, _COMMITMENT_KEYS, HOLD_REQUEST, "external commitment")
    _validate_commitment_result_blind(commitment, "external commitment")
    bundle_image = _read_pin(
        commitment["candidate_bundle"],
        "candidate bundle",
        code=HOLD_REQUEST,
    )
    bundle = _decode_json(bundle_image.raw, "candidate bundle")
    _exact_keys(bundle, _BUNDLE_KEYS, HOLD_REQUEST, "candidate bundle")
    _validate_result_blind_keys(bundle, "candidate bundle")
    if bundle["schema"] != BUNDLE_SCHEMA or bundle["status"] != BUNDLE_STATUS:
        _fail(HOLD_REQUEST, "candidate-bundle boundary mismatch")
    _false_boundary(bundle["claim_boundary"], _PLAN_CLAIM_KEYS, "bundle claims")
    _same_pin(bundle["replay_plan"], request["plan"], "bundle replay plan")
    _same_pin(bundle["member_spec"], authorities["member_spec"], "bundle member")
    _same_pin(
        bundle["method_parameter_registry"],
        authorities["method_parameters"],
        "bundle method registry",
    )
    if bundle["shared_precommit_context_sha256"] != precommit:
        _fail(HOLD_REQUEST, "candidate-bundle precommit mismatch")

    if commitment["schema"] != COMMITMENT_SCHEMA or commitment["status"] != COMMITMENT_STATUS:
        _fail(HOLD_REQUEST, "commitment boundary mismatch")
    authentication = _exact_keys(
        commitment["authentication"],
        _AUTHENTICATION_KEYS,
        HOLD_REQUEST,
        "commitment authentication",
    )
    authority = _exact_keys(
        commitment["authority"], _AUTHORITY_KEYS, HOLD_REQUEST, "commitment authority"
    )
    ordering = _exact_keys(
        commitment["ordering"], _ORDERING_KEYS, HOLD_REQUEST, "commitment ordering"
    )
    claims = _exact_keys(
        commitment["claim_boundary"],
        _COMMITMENT_CLAIM_KEYS,
        HOLD_REQUEST,
        "commitment claims",
    )
    if (
        authentication["authentication_class"] not in _ACCEPTED_AUTHENTICATION_CLASSES
        or authentication["structural_validation_only"] is not True
        or not _nonempty(authentication["evidence_identifier"])
        or any(not _nonempty(item) for item in authority.values())
        or any(item is not True for item in ordering.values())
        or any(item is not False for item in claims.values())
    ):
        _fail(HOLD_REQUEST, "structural commitment authentication mismatch")
    _same_pin(
        commitment["candidate_bundle"],
        {"path": str(bundle_image.path), "sha256": bundle_image.sha256},
        "commitment candidate bundle",
    )
    message_preimage = {
        "authority": authority,
        "candidate_bundle": commitment["candidate_bundle"],
        "claim_boundary": claims,
        "ordering": ordering,
    }
    if commitment["commitment_message_sha256"] != _domain_digest(
        COMMITMENT_MESSAGE_DOMAIN, message_preimage
    ):
        _fail(HOLD_REQUEST, "commitment message digest mismatch")
    replay = _domain_digest(
        REPLAY_CONTEXT_DOMAIN,
        {
            "external_predecessor_commitment_sha256": commitment_image.sha256,
            "replay_plan_sha256": plan_image.sha256,
            "shared_precommit_context_sha256": precommit,
        },
    )
    if request["shared_replay_context_sha256"] != replay:
        _fail(HOLD_REQUEST, "shared replay digest mismatch")
    planned_request_paths = {slots[0] for slots in validated_slots.values()}
    planned_output_paths = {
        path
        for _, artifact_output_path, receipt_output_path in validated_slots.values()
        for path in (artifact_output_path, receipt_output_path)
    }
    protocol_input_paths = {
        request_image.path,
        plan_image.path,
        bundle_image.path,
        commitment_image.path,
        *planned_request_paths,
        *planned_dependency_paths,
    }
    if planned_output_paths & protocol_input_paths:
        _fail(HOLD_REQUEST, "planned output aliases a protocol input")
    if any(os.path.lexists(path) for path in planned_output_paths):
        _fail(HOLD_REQUEST, "planned output slot is not fresh")
    return ReplayProtocol(
        request=request,
        request_image=request_image,
        plan=plan,
        plan_image=plan_image,
        bundle=bundle,
        bundle_image=bundle_image,
        commitment=commitment,
        commitment_image=commitment_image,
        entry=entry,
        artifact_path=planned_artifact,
        receipt_path=planned_receipt,
    )


def _validate_authorities(
    protocol: ReplayProtocol,
    *,
    caller_path: Path,
    caller_role: str,
) -> tuple[dict[str, FileImage], dict[str, dict[str, Any]]]:
    authorities = protocol.entry["input_authorities"]
    runtime = protocol.entry["implementation_runtime_closure"]
    images = {
        role: _read_pin(pin, role, code=HOLD_AUTHORITY)
        for role, pin in {
            **authorities,
            "producer": runtime["producer"],
            "verifier": runtime["verifier"],
        }.items()
    }
    if (
        caller_role not in {"producer", "verifier"}
        or images[caller_role].path != caller_path
        or images["producer"].path == images["verifier"].path
    ):
        _fail(HOLD_RUNTIME, "caller/runtime source binding mismatch")
    accepted = {
        "member_spec": MEMBER_SHA256,
        "method_parameters": PARAMETER_SHA256,
        "factorization": FACTORIZATION_SHA256,
        "anti_vacuity_policy": ANTI_VACUITY_POLICY_SHA256,
    }
    for role, expected in accepted.items():
        if images[role].sha256 != expected:
            _fail(HOLD_AUTHORITY, f"{role}: accepted SHA-256 mismatch")

    canonical_roles = {
        "anti_vacuity_policy",
        "configuration",
        "factorization",
        "ideal_formula",
        "member_spec",
        "method_parameters",
        "reference_density",
    }
    parsed = {
        role: _decode_json(image.raw, role, require_canonical=role in canonical_roles)
        for role, image in images.items()
        if role in _INPUT_AUTHORITY_ROLES
        and role
        not in {"configuration_design", "configuration_implementation", "configuration_test"}
    }
    expected_schemas = {
        "anti_vacuity_policy": ANTI_VACUITY_POLICY_SCHEMA,
        "configuration": CONFIGURATION_SCHEMA,
        "configuration_initial_geometry": INITIAL_GEOMETRY_SCHEMA,
        "factorization": FACTORIZATION_SCHEMA,
        "factorization_initial_partition_bundle": INITIAL_PARTITION_SCHEMA,
        "factorization_killing_geometry": KILLING_GEOMETRY_SCHEMA,
        "ideal_formula": FORMULA_SCHEMA,
        "member_spec": MEMBER_SCHEMA,
        "method_parameters": PARAMETER_SCHEMA,
        "reference_density": REFERENCE_SCHEMA,
    }
    for role, schema in expected_schemas.items():
        if parsed[role].get("schema") != schema:
            _fail(HOLD_AUTHORITY, f"{role}: schema mismatch")

    configuration = parsed["configuration"]
    configuration_authority = _exact_keys(
        configuration.get("authority"),
        {
            "design_path",
            "design_sha256",
            "implementation_path",
            "implementation_sha256",
            "test_path",
            "test_sha256",
        },
        HOLD_AUTHORITY,
        "configuration authority",
    )
    authority_roles = {
        "configuration_design": ("design_path", "design_sha256"),
        "configuration_implementation": ("implementation_path", "implementation_sha256"),
        "configuration_test": ("test_path", "test_sha256"),
    }
    for role, (path_key, sha_key) in authority_roles.items():
        _binding_matches_pin(
            {"path": configuration_authority[path_key], "sha256": configuration_authority[sha_key]},
            authorities[role],
            f"configuration {role}",
        )
        if images[role].sha256 != configuration_authority[sha_key]:
            _fail(HOLD_AUTHORITY, f"{role}: bytes mismatch")
    if (
        configuration.get("status") != "CONTROL_FREE_GEOMETRY_SPEC_ONLY_NOT_F0_NOT_F1"
        or configuration.get("authorizes_scientific_execution") is not False
        or configuration.get("contains_budget_value") is not False
        or configuration.get("contains_control_values") is not False
        or configuration.get("coordinate_order") != list(COORDINATES)
        or configuration.get("configuration_count") != EXPECTED_CONFIGURATION_COUNT
        or configuration.get("total_state_workload") != EXPECTED_TOTAL_STATES
    ):
        _fail(HOLD_AUTHORITY, "configuration semantic boundary mismatch")

    factorization = parsed["factorization"]
    if any(
        item is not False for item in factorization.get("claim_boundary", {}).values()
    ) or factorization.get("coordinate_and_measure_contract", {}).get("coordinate_order") != list(
        COORDINATES
    ):
        _fail(HOLD_AUTHORITY, "factorization semantic boundary mismatch")
    source_pins = _exact_keys(
        factorization.get("source_pins"),
        {"configuration_source", "initial_partition_bundle", "killing_geometry_source"},
        HOLD_AUTHORITY,
        "factorization source pins",
    )
    factorization_roles = {
        "configuration_source": "configuration",
        "initial_partition_bundle": "factorization_initial_partition_bundle",
        "killing_geometry_source": "factorization_killing_geometry",
    }
    for source_role, authority_role in factorization_roles.items():
        contextual = _exact_keys(
            source_pins[source_role],
            _CONTEXT_PIN_KEYS,
            HOLD_AUTHORITY,
            f"factorization {source_role}",
        )
        _binding_matches_pin(
            {"path": contextual["path"], "sha256": contextual["sha256"]},
            authorities[authority_role],
            f"factorization {source_role}",
        )
        if contextual["sha256"] != images[authority_role].sha256:
            _fail(HOLD_AUTHORITY, f"factorization {source_role}: bytes mismatch")

    initial_bundle = parsed["factorization_initial_partition_bundle"]
    if (
        initial_bundle.get("configuration_sha256") != images["configuration"].sha256
        or initial_bundle.get("analytic_source_sha256")
        != images["configuration_initial_geometry"].sha256
        or initial_bundle.get("configuration_count") != EXPECTED_CONFIGURATION_COUNT
        or initial_bundle.get("total_state_workload") != EXPECTED_TOTAL_STATES
    ):
        _fail(HOLD_AUTHORITY, "initial-partition authority mismatch")
    killing = parsed["factorization_killing_geometry"]
    killing_bundle = _exact_keys(
        killing.get("configuration_bundle"),
        {
            "configuration_path",
            "configuration_sha256",
            "partition_bundle_path",
            "partition_bundle_sha256",
        },
        HOLD_AUTHORITY,
        "killing geometry configuration bundle",
    )
    _binding_matches_pin(
        {
            "path": killing_bundle["configuration_path"],
            "sha256": killing_bundle["configuration_sha256"],
        },
        authorities["configuration"],
        "killing geometry configuration",
    )
    _binding_matches_pin(
        {
            "path": killing_bundle["partition_bundle_path"],
            "sha256": killing_bundle["partition_bundle_sha256"],
        },
        authorities["factorization_initial_partition_bundle"],
        "killing geometry partition bundle",
    )
    if (
        killing.get("coordinate_order") != list(COORDINATES)
        or killing.get("physical_dimension") != 2
        or killing.get("quotient_dimension") != 3
        or killing_bundle["configuration_sha256"] != images["configuration"].sha256
        or killing_bundle["partition_bundle_sha256"]
        != images["factorization_initial_partition_bundle"].sha256
    ):
        _fail(HOLD_AUTHORITY, "killing geometry authority mismatch")

    policy = parsed["anti_vacuity_policy"]
    if (
        any(item is not False for item in policy.get("claim_boundary", {}).values())
        or set(policy.get("claim_boundary", {})) != _PARAMETER_CLAIM_KEYS
    ):
        _fail(HOLD_AUTHORITY, "anti-vacuity policy boundary mismatch")
    policy_sources = policy.get("source_pins", {})
    member_policy = policy_sources.get("member_spec_v4_candidate", {})
    registry_policy = policy_sources.get("method_parameter_registry_v4_candidate", {})
    if (
        member_policy.get("sha256") != MEMBER_SHA256
        or member_policy.get("member_identity_sha256") != MEMBER_IDENTITY_SHA256
        or registry_policy.get("sha256") != PARAMETER_SHA256
        or policy.get("successor_binding_counts", {}).get("future_fresh_replay_role_catalog_order")
        != [8, 9, 10]
    ):
        _fail(HOLD_AUTHORITY, "anti-vacuity policy pin mismatch")

    member = parsed["member_spec"]
    if (
        member.get("member_identity_sha256") != MEMBER_IDENTITY_SHA256
        or any(item is not False for item in member.get("claim_boundary", {}).values())
        or member.get("configuration_order") != configuration.get("configuration_order")
    ):
        _fail(HOLD_AUTHORITY, "member authority mismatch")
    role_bindings = member.get("role_bindings", {})
    member_role_map = {
        "configuration_source": "configuration",
        "factorization_source": "factorization",
        "ideal_formula_source": "ideal_formula",
        "reference_density_source": "reference_density",
    }
    for binding_role, authority_role in member_role_map.items():
        _binding_matches_pin(
            role_bindings.get(binding_role),
            authorities[authority_role],
            f"member {binding_role}",
        )
    return images, parsed


def _validate_runtime(protocol: ReplayProtocol) -> None:
    required = _exact_keys(
        protocol.entry["implementation_runtime_closure"]["runtime_requirements"],
        _RUNTIME_KEYS,
        HOLD_RUNTIME,
        "runtime requirements",
    )
    if any(not _nonempty(value) for value in required.values()) or required != _runtime_versions():
        _fail(HOLD_RUNTIME, "runtime version mismatch")


def _validate_method_registry(registry: dict[str, Any], selection: Any) -> None:
    selected = _exact_keys(selection, _METHOD_SELECTION_KEYS, HOLD_METHOD, "method selection")
    if selected != _EXPECTED_METHOD_SELECTION:
        _fail(HOLD_METHOD, "role-10 method selection mismatch")
    _exact_keys(registry, _PARAMETER_REGISTRY_KEYS, HOLD_METHOD, "method registry")
    claims = registry["claim_boundary"]
    entries = registry["parameters"]
    if (
        registry["schema"] != PARAMETER_SCHEMA
        or registry["status"]
        != "RESULT_BLIND_CANDIDATE_NATIVE_METHOD_PARAMETERS_ONLY_NOT_EXTERNALLY_COMMITTED"
        or type(claims) is not dict
        or set(claims) != _PARAMETER_CLAIM_KEYS
        or any(item is not False for item in claims.values())
        or registry["parameter_count"] != 10
        or type(entries) is not list
        or len(entries) != 10
    ):
        _fail(HOLD_METHOD, "method registry boundary mismatch")
    identifiers: list[str] = []
    digests: list[str] = []
    for entry in entries:
        _exact_keys(
            entry,
            {"method_parameter_sha256", "parameter_id", "parameters"},
            HOLD_METHOD,
            "method record",
        )
        identifier = entry["parameter_id"]
        digest = entry["method_parameter_sha256"]
        parameters = entry["parameters"]
        if (
            not _nonempty(identifier)
            or type(parameters) is not dict
            or not _valid_sha(digest)
            or digest != _domain_digest(PARAMETER_DIGEST_DOMAIN, parameters)
            or parameters.get("source_role_scope") != PARAMETER_SCOPES.get(identifier)
        ):
            _fail(HOLD_METHOD, "method record digest/scope mismatch")
        identifiers.append(identifier)
        digests.append(digest)
    if identifiers != list(PARAMETER_ORDER) or digests != list(PARAMETER_DIGEST_ORDER):
        _fail(HOLD_METHOD, "method registry order/digest mismatch")


def _fraction(value: Any, label: str) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        _fail(HOLD_PARTITION, f"{label}: canonical p/q required")
    numerator, denominator = value.split("/")
    try:
        result = Fraction(int(numerator), int(denominator))
    except (ValueError, ZeroDivisionError) as error:
        raise CandidateKillingVerificationFailure(
            HOLD_PARTITION, f"{label}: invalid rational"
        ) from error
    if f"{result.numerator}/{result.denominator}" != value:
        _fail(HOLD_PARTITION, f"{label}: noncanonical rational")
    return result


def _binary64_fraction(value: Any, label: str) -> Fraction:
    if type(value) is not str:
        _fail(HOLD_PARTITION, f"{label}: binary64 hex required")
    try:
        parsed = float.fromhex(value)
    except (OverflowError, ValueError) as error:
        raise CandidateKillingVerificationFailure(
            HOLD_PARTITION, f"{label}: invalid binary64 hex"
        ) from error
    if (
        not math.isfinite(parsed)
        or parsed.hex() != value
        or (parsed == 0 and math.copysign(1.0, parsed) < 0)
    ):
        _fail(HOLD_PARTITION, f"{label}: noncanonical binary64")
    return Fraction.from_float(parsed)


def _q_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _modulo(value: Fraction, period: Fraction) -> Fraction:
    if period <= 0:
        _fail(HOLD_PARTITION, "nonpositive periodic width")
    return value - (value // period) * period


def _reconstruct_partition(
    coordinate: str,
    axis: dict[str, Any],
    dynamics: dict[str, Any],
) -> dict[str, Any]:
    size = axis.get("size")
    alignment = axis.get("alignment")
    if type(size) is not int or size < 2 or not _nonempty(alignment):
        _fail(HOLD_PARTITION, "invalid configuration axis")
    if alignment in {"cell_centred_reflecting", "vertex_centred_reflecting_dual"}:
        lower = _binary64_fraction(axis.get("lower_binary64_hex"), "axis lower")
        upper = _binary64_fraction(axis.get("upper_binary64_hex"), "axis upper")
        if lower >= upper:
            _fail(HOLD_PARTITION, "reversed reflecting domain")
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
        start = _fraction(dynamics.get("transverse_domain_start_exact"), "period start")
        width = _fraction(dynamics.get("transverse_period_exact"), "period width")
        step = width / size
        shift = _fraction(axis.get("periodic_shift_exact"), "periodic shift")
        expected_shift = Fraction(0) if alignment.endswith("_base") else step / 2
        if shift != expected_shift:
            _fail(HOLD_PARTITION, "periodic shift mismatch")
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
        _fail(HOLD_PARTITION, "unknown axis alignment")
    volumes = [sum((upper - lower for lower, upper in cell), Fraction(0)) for cell in segments]
    return {
        "cell_segments_exact": [
            [[_q_text(lower), _q_text(upper)] for lower, upper in cell] for cell in segments
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


def _validate_partitions(
    protocol: ReplayProtocol,
    member: dict[str, Any],
    configuration: dict[str, Any],
) -> None:
    rows = configuration.get("configurations")
    bindings = member.get("n0_sequence_bindings")
    if (
        type(rows) is not list
        or type(bindings) is not list
        or len(rows) != EXPECTED_CONFIGURATION_COUNT
        or len(bindings) != EXPECTED_CONFIGURATION_COUNT
    ):
        _fail(HOLD_PARTITION, "member/configuration cardinality mismatch")
    configuration_inventory_sha256 = _domain_digest(
        CONFIGURATION_INVENTORY_DOMAIN, _configuration_inventory(configuration)
    )
    if (
        configuration_inventory_sha256 != CONFIGURATION_INVENTORY_SHA256
        or configuration_inventory_sha256
        != protocol.plan["shared_context"]["configuration_row_inventory_sha256"]
    ):
        _fail(HOLD_PARTITION, "configuration inventory digest mismatch")
    partition_inventory = _partition_inventory(member)
    partition_inventory_sha256 = _domain_digest(PARTITION_INVENTORY_DOMAIN, partition_inventory)
    if (
        len(partition_inventory) != EXPECTED_AXIS_COUNT
        or partition_inventory_sha256 != PARTITION_INVENTORY_SHA256
        or partition_inventory_sha256
        != protocol.plan["shared_context"]["partition_inventory_sha256"]
    ):
        _fail(HOLD_PARTITION, "partition inventory digest mismatch")

    pins = protocol.entry["partition_path_bindings"]
    if type(pins) is not list or len(pins) != EXPECTED_AXIS_COUNT:
        _fail(HOLD_PARTITION, "partition pin cardinality mismatch")
    requested: dict[tuple[int, str], dict[str, Any]] = {}
    for value in pins:
        pin = _exact_keys(value, _PARTITION_PIN_KEYS, HOLD_PARTITION, "partition pin")
        index = pin["configuration_index"]
        coordinate = pin["coordinate"]
        if (
            type(index) is not int
            or not 0 <= index < EXPECTED_CONFIGURATION_COUNT
            or coordinate not in COORDINATES
            or (index, coordinate) in requested
            or not _valid_sha(pin["sha256"])
            or not _nonempty(pin["member_report_relative_path"])
        ):
            _fail(HOLD_PARTITION, "invalid partition pin identity")
        requested[index, coordinate] = pin

    dynamics = configuration.get("dynamics")
    if type(dynamics) is not dict:
        _fail(HOLD_PARTITION, "configuration dynamics missing")
    axis_cells = 0
    axis_edges = 0
    periodic_seams = 0
    total_states = 0
    for index, (row, binding) in enumerate(zip(rows, bindings, strict=True)):
        if type(row) is not dict or type(binding) is not dict:
            _fail(HOLD_PARTITION, "row/binding object required")
        shape = row.get("shape")
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(item) is not int or item < 2 for item in shape)
            or row.get("expected_states") != math.prod(shape)
            or binding.get("configuration_index") != index
            or binding.get("n0_anchor_shape") != shape
            or binding.get("n0_anchor_expected_states") != row.get("expected_states")
            or binding.get("sequence_source_row_canonical_sha256")
            != hashlib.sha256(canonical_bytes(row)).hexdigest()
        ):
            _fail(HOLD_PARTITION, "row/member binding mismatch")
        total_states += row["expected_states"]
        axes = binding.get("n0_axes")
        if type(axes) is not list or len(axes) != 3:
            _fail(HOLD_PARTITION, "member axis list mismatch")
        for coordinate, axis in zip(COORDINATES, axes, strict=True):
            pin = requested.get((index, coordinate))
            relative = axis.get("partition_report_relative_path")
            if (
                pin is None
                or axis.get("coordinate") != coordinate
                or axis.get("partition_schema") != PARTITION_SCHEMA
                or axis.get("partition_sha256") != pin["sha256"]
                or relative != pin["member_report_relative_path"]
            ):
                _fail(HOLD_PARTITION, "member/request partition mismatch")
            pure = PurePosixPath(relative)
            absolute = _absolute(pin["path"], HOLD_PARTITION, "partition path")
            if (
                pure.is_absolute()
                or ".." in pure.parts
                or tuple(absolute.parts[-len(pure.parts) :]) != pure.parts
            ):
                _fail(HOLD_PARTITION, "partition path suffix mismatch")
            image = _immutable_image(
                absolute,
                code=HOLD_PARTITION,
                label=f"partition {index}:{coordinate}",
            )
            if image.sha256 != pin["sha256"]:
                _fail(HOLD_PARTITION, "partition digest mismatch")
            partition = _decode_json(image.raw, f"partition {index}:{coordinate}")
            configuration_axis = row.get(coordinate)
            if type(configuration_axis) is not dict or partition != _reconstruct_partition(
                coordinate, configuration_axis, dynamics
            ):
                _fail(HOLD_PARTITION, f"partition geometry mismatch at {index}:{coordinate}")
            if (
                axis.get("cell_count") != partition["size"]
                or axis.get("periodic") is not partition["periodic"]
                or axis.get("alignment") != configuration_axis.get("alignment")
            ):
                _fail(HOLD_PARTITION, "partition/member axis semantics mismatch")
            axis_cells += partition["size"]
            axis_edges += partition["size"] if partition["periodic"] else partition["size"] - 1
            periodic_seams += int(partition["periodic"])

    counts = member.get("reconstruction_counts")
    expected_counts = {
        "axis_cell_count": EXPECTED_AXIS_CELL_COUNT,
        "axis_count": EXPECTED_AXIS_COUNT,
        "axis_edge_count": EXPECTED_AXIS_EDGE_COUNT,
        "configuration_count": EXPECTED_CONFIGURATION_COUNT,
        "periodic_seam_count": EXPECTED_PERIODIC_SEAM_COUNT,
        "profile_index_count": EXPECTED_PROFILE_INDEX_COUNT,
        "total_virtual_tensor_state_count": EXPECTED_TOTAL_STATES,
    }
    if (
        counts != expected_counts
        or axis_cells != EXPECTED_AXIS_CELL_COUNT
        or axis_edges != EXPECTED_AXIS_EDGE_COUNT
        or periodic_seams != EXPECTED_PERIODIC_SEAM_COUNT
        or total_states != EXPECTED_TOTAL_STATES
    ):
        _fail(HOLD_PARTITION, "partition reconstruction counts mismatch")


def validate_protocol(
    request_path: Path,
    artifact_path: Path,
    receipt_path: Path | None,
    *,
    caller_path: Path,
    caller_role: str,
) -> ReplayProtocol:
    """Run every non-numerical role-10 gate and return only internal state."""

    protocol = _load_protocol(request_path, artifact_path, receipt_path)
    _, parsed = _validate_authorities(protocol, caller_path=caller_path, caller_role=caller_role)
    _validate_runtime(protocol)
    _validate_method_registry(parsed["method_parameters"], protocol.entry["method_selection"])
    _validate_partitions(protocol, parsed["member_spec"], parsed["configuration"])
    return protocol


def validate(request_path: Path, artifact_path: Path, receipt_path: Path) -> None:
    validate_protocol(
        request_path,
        artifact_path,
        receipt_path,
        caller_path=Path(__file__).resolve(),
        caller_role="verifier",
    )
    raise CandidateKillingVerificationFailure(HOLD_NUMERICAL_INCOMPLETE)


def _parse_cli(argv: Sequence[str] | None = None) -> tuple[Path, Path, Path]:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    arguments = parser.parse_args(argv)
    request = _absolute(arguments.request, HOLD_REQUEST, "request CLI")
    output = _absolute(arguments.output, HOLD_REQUEST, "output CLI")
    receipt = _absolute(arguments.receipt, HOLD_REQUEST, "receipt CLI")
    if len({request, output, receipt}) != 3:
        _fail(HOLD_REQUEST, "CLI paths must be distinct")
    return request, output, receipt


def main(argv: Sequence[str] | None = None) -> int:
    try:
        request, output, receipt = _parse_cli(argv)
        validate(request, output, receipt)
    except CandidateKillingVerificationFailure as error:
        print(error, file=sys.stderr)
        return 2
    raise AssertionError("role-10 protocol shell cannot claim success")


if __name__ == "__main__":
    raise SystemExit(main())
