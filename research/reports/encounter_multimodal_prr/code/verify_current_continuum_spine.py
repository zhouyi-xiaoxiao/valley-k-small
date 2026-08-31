#!/usr/bin/env python3
"""Run the explicitly scoped current theorem/continuum verification spine.

This is not a full-report test runner and it is not a CI attestation.  It
closes the collection gap caused by the repository-level pytest configuration
for the current Round-10/11 and Round-172--177 continuum chain, then checks
the theorem-first manuscript freshness/scope tests.  It does not execute
production science, positive-budget numerics, C2/C3 evaluation, root transfer,
or a release pipeline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import stat
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

import compile_theorem_first_working as theorem_build

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
CODE_PREFIX = "research/reports/encounter_multimodal_prr/code"
EXPECTED_PYTEST_CASES = 265
EXPECTED_JUNIT_TESTS = 333
DECLARED_NEUTRAL_ASSERTIONS = 1619


@dataclass(frozen=True)
class Check:
    """One named subprocess check with an argument-vector contract."""

    name: str
    argv: tuple[str, ...]
    expected_output: str | None = None
    expected_pytest_tests: int | None = None
    expected_pytest_cases: int | None = None


class CurrentSpineFailure(RuntimeError):
    """Fail-closed current-spine verification error."""


FROZEN_ROUND174: dict[str, str] = {
    "notes/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.md": (
        "13da61f8a41a6d659800595bb73d6ea717530a3c6b33244f0c39703351a80660"
    ),
    "artifacts/data/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.json": (
        "ffbd822e8a3649405f27d9d22f21688049df6a7cc045b0899ac5b38540b4cb70"
    ),
    "code/build_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py": (
        "3b1739af644bf710c3e1830b4978e2d7010a0c8f93d3e2d3483f5ded95d967fd"
    ),
    "code/validate_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py": (
        "d067eeb854b5d9d8ca0669ea99b0bdd9c50c02a236faccc0e0a3513c669e1a90"
    ),
    "code/test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py": (
        "be44611c7957140c72348bbaa8f66ee90e7c3c27556143aee07e042929cfa8bd"
    ),
    "code/test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_mutations_v1.py": (
        "6a67565b1881763086070fde3841cf0cd8b875d737c52118ac3be784f5d0c048"
    ),
    "audits/round_174_twelve_family_ideal_fixed_box_c1_composition.md": (
        "8023ca031110a16b92d74b78c935e9354a868bb2613315e0c651f278f2754fe1"
    ),
}

ROUND175_RECEIPT = "audits/round_175_round174_post_audit_acceptance_receipt.md"
ROUND175_RECEIPT_SHA256 = "4dafc680012b26ce4a23f416c7d46353a7598317f7386564306a3e1bb950a0fc"
ROUND176_MANIFEST = "artifacts/data/continuum_c1_n0_same_member_preflight_outer_manifest_v1.json"
ROUND177_PACKAGE = Path("artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1")
ROUND177_MANIFEST = (
    ROUND177_PACKAGE / "continuum_c1_c2_n0_predecessor_authority_candidate_manifest_v1.json"
)
REQUIRED_RECEIPT_TEXT = (
    "verdict: ACCEPTED_WITH_P2",
    "accepted_layer: ideal_fixed_box_C1_theorem_layer",
    "round174_frozen_bytes_modified: false",
    "cryptographic_independence_proved: false",
    "P0 = 0",
    "P1 = 0",
    "P2 = 3",
    "ideal_density_ratio_uniformity: true",
    "uniform_over_f_w_B: true",
    "half_order_operator_norm: true",
    "initial_projection: true",
    "dunford_r_0_1_2: true",
    "compact_positive_time_tau_T: true",
    "production_binding: false",
    "production_n0_correlated_containment_receipt_present = false",
    "production_same_member_bridge_accepted               = false",
    "project_or_production_complete_C1                     = false",
    "computable_C2 / complete_C2 / complete_C3             = false",
    "box_exhaustion / componentwise_root_transfer          = false",
    "release_eligible / submission_eligible                = false",
)


def _python(*args: str) -> tuple[str, ...]:
    return (sys.executable, "-B", *args)


def _isolated_python(*args: str) -> tuple[str, ...]:
    return (sys.executable, "-I", "-B", *args)


def _pytest(*paths: str) -> tuple[str, ...]:
    return _python(
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "--strict-config",
        "--strict-markers",
        "-o",
        "xfail_strict=true",
        *paths,
    )


def _isolated_pytest(*paths: str) -> tuple[str, ...]:
    return _isolated_python(
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "--strict-config",
        "--strict-markers",
        "-o",
        "xfail_strict=true",
        *paths,
    )


def _code(name: str) -> str:
    return f"{CODE_PREFIX}/{name}"


CHECKS: tuple[Check, ...] = (
    Check(
        "round175-receipt-currentness-tests",
        _pytest(_code("test_verify_current_continuum_spine.py")),
        expected_pytest_tests=6,
        expected_pytest_cases=6,
    ),
    Check(
        "round10-free-residual-builder",
        _python(_code("continuum_c2_one_sided_free_residual_neutral_fixture_v1.py"), "--check"),
        expected_output="PASS one_sided_free_residual_neutral_v1_check",
    ),
    Check(
        "round10-free-residual-independent-validator",
        _python(_code("test_continuum_c2_one_sided_free_residual_neutral_fixture_v1.py")),
        expected_output="SUMMARY 107/107 PASS",
    ),
    Check(
        "round10-free-residual-mutations",
        _python(_code("test_continuum_c2_one_sided_free_residual_neutral_fixture_mutations_v1.py")),
        expected_output="SUMMARY 30/30 PASS",
    ),
    Check(
        "round11-sector-contour-builder",
        _python(_code("continuum_c2_complex_sector_h2_neutral_fixture_v1.py"), "--check"),
        expected_output="PASS complex_sector_h2_neutral_v1_check",
    ),
    Check(
        "round11-sector-contour-independent-validator",
        _python(_code("test_continuum_c2_complex_sector_h2_neutral_fixture_v1.py")),
        expected_output="SUMMARY 1436/1436 PASS",
    ),
    Check(
        "round11-sector-contour-mutations",
        _python(_code("test_continuum_c2_complex_sector_h2_neutral_fixture_mutations_v1.py")),
        expected_output="SUMMARY 46/46 PASS",
    ),
    Check(
        "round172-refinement-builder",
        _python(_code("build_continuum_c1_genuine_joint_refinement_family_v2.py"), "--check"),
        expected_output="PASS_C1_REFINEMENT_V2_BUILD",
    ),
    Check(
        "round172-refinement-validator",
        _python(_code("validate_continuum_c1_genuine_joint_refinement_family_v2.py")),
        expected_output="PASS_C1_REFINEMENT_V2_VERIFY",
    ),
    Check(
        "round172-refinement-tests",
        _pytest(
            _code("test_continuum_c1_genuine_joint_refinement_family_v2.py"),
            _code("test_continuum_c1_genuine_joint_refinement_family_mutations_v2.py"),
        ),
        expected_pytest_tests=28,
        expected_pytest_cases=28,
    ),
    Check(
        "round173-source-bound-builder",
        _python(_code("build_continuum_c2_source_bound_map_cut_killing_contract_v1.py"), "--check"),
        expected_output="PASS source-bound map/cut/killing contract",
    ),
    Check(
        "round173-source-bound-validator",
        _python(_code("validate_continuum_c2_source_bound_map_cut_killing_contract_v1.py")),
        expected_output="PASS independent source/geometry and exact-string-contract validation",
    ),
    Check(
        "round173-source-bound-tests",
        _pytest(
            _code("test_continuum_c2_source_bound_map_cut_killing_contract_v1.py"),
            _code("test_continuum_c2_source_bound_map_cut_killing_contract_mutations_v1.py"),
        ),
        expected_pytest_tests=45,
        expected_pytest_cases=20,
    ),
    Check(
        "round174-composition-builder",
        _python(
            _code("build_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py"),
            "--check",
        ),
        expected_output="PASS_C1_COMPOSITION_BUILD",
    ),
    Check(
        "round174-composition-validator",
        _python(_code("validate_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py")),
        expected_output="PASS_C1_COMPOSITION_INDEPENDENT_SOURCE_GEOMETRY",
    ),
    Check(
        "round174-composition-tests",
        _pytest(
            _code("test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py"),
            _code("test_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_mutations_v1.py"),
        ),
        expected_pytest_tests=69,
        expected_pytest_cases=26,
    ),
    Check(
        "round176-n0-same-member-preflight-builder",
        _isolated_python(
            _code("build_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py"),
            "--check",
        ),
        expected_output="PASS_N0_SAME_MEMBER_PREFLIGHT_BUILD",
    ),
    Check(
        "round176-n0-same-member-preflight-validator",
        _isolated_python(
            _code("validate_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py")
        ),
        expected_output="PASS_N0_SAME_MEMBER_PREFLIGHT_VALIDATION",
    ),
    Check(
        "round176-n0-same-member-preflight-tests",
        _isolated_pytest(
            _code("test_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py"),
            _code("test_continuum_c1_n0_same_member_symbolic_preflight_candidate_mutations_v1.py"),
        ),
        expected_pytest_tests=97,
        expected_pytest_cases=97,
    ),
    Check(
        "round177-predecessor-authority-candidate-builder",
        _isolated_python(
            _code("build_continuum_c1_n0_predecessor_authority_candidate_v1.py"),
            "--check",
        ),
        expected_output="PASS_PREDECESSOR_AUTHORITY_CANDIDATE_BUILD",
    ),
    Check(
        "round177-predecessor-authority-candidate-validator",
        _isolated_python(_code("validate_continuum_c1_n0_predecessor_authority_candidate_v1.py")),
        expected_output="PASS_PREDECESSOR_AUTHORITY_CANDIDATE_VALIDATION",
    ),
    Check(
        "round177-predecessor-authority-candidate-tests",
        _isolated_pytest(
            _code("test_continuum_c1_n0_predecessor_authority_candidate_v1.py"),
            _code("test_continuum_c1_n0_predecessor_authority_candidate_mutations_v1.py"),
        ),
        expected_pytest_tests=69,
        expected_pytest_cases=69,
    ),
    Check(
        "theorem-first-manuscript-freshness-and-scope",
        _pytest(
            _code("test_compile_theorem_first_working.py"),
            _code("test_theorem_first_scope_consistency.py"),
        ),
        expected_pytest_tests=19,
        expected_pytest_cases=19,
    ),
)


def _stable_regular_bytes(path: Path) -> bytes:
    """Read one stable regular-file snapshot without following a symlink."""
    before = path.lstat()
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise CurrentSpineFailure(f"regular nonsymlink file required: {path}")
    payload = path.read_bytes()
    after = path.lstat()
    signature_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    signature_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    if signature_before != signature_after or len(payload) != after.st_size:
        raise CurrentSpineFailure(f"file changed during snapshot: {path}")
    return payload


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise CurrentSpineFailure(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _decode_manifest() -> dict[str, object]:
    payload = _stable_regular_bytes(theorem_build.MANIFEST)
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                CurrentSpineFailure(f"non-finite JSON token: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CurrentSpineFailure(f"strict manifest decode failed: {exc}") from exc
    if type(value) is not dict:
        raise CurrentSpineFailure("theorem-first manifest must be an object")
    return value


def validate_environment() -> None:
    """Require the repository-owned environment used by the frozen checks."""
    expected = (REPOSITORY / ".venv").resolve()
    actual = Path(sys.prefix).resolve()
    if actual != expected:
        raise CurrentSpineFailure(f"repository .venv required: expected {expected}, got {actual}")


def validate_manifest() -> None:
    """Fail closed on theorem-first manifest drift or claim promotion."""
    payload = _decode_manifest()
    if payload.get("schema_version") != theorem_build.SCHEMA_VERSION:
        raise CurrentSpineFailure("theorem-first manifest schema drifted")
    if payload.get("status") != "PASS_INTERNAL_THEOREM_FIRST_WORKING_SET":
        raise CurrentSpineFailure("theorem-first manifest status drifted")
    build = payload.get("build")
    if type(build) is not dict or build.get("driver") != "code/compile_theorem_first_working.py":
        raise CurrentSpineFailure("theorem-first manifest driver drifted")
    for field in (
        "release_eligible",
        "positive_budget_evaluated",
        "positive_budget_scientific_values_read",
    ):
        if payload.get(field) is not False:
            raise CurrentSpineFailure(f"theorem-first promotion flag is not false: {field}")
    validation = payload.get("validation")
    expected_validation: dict[str, object] = {
        "all_fonts_embedded": True,
        "byte_identical_main_rebuilds": True,
        "byte_identical_supplement_rebuilds": True,
        "ghostscript_parse": True,
        "overfull_boxes": 0,
        "text_extraction_replacement_or_nul_characters": 0,
        "type3_fonts": 0,
        "undefined_citations": 0,
        "undefined_references": 0,
    }
    if type(validation) is not dict:
        raise CurrentSpineFailure("theorem-first validation ledger is missing")
    for field, expected in expected_validation.items():
        if type(validation.get(field)) is not type(expected) or validation.get(field) != expected:
            raise CurrentSpineFailure(
                f"theorem-first validation gate drifted: {field}={validation.get(field)!r}"
            )
    freshness_errors = theorem_build._manifest_freshness_errors(payload)
    if freshness_errors:
        raise CurrentSpineFailure("theorem-first manifest is stale: " + "; ".join(freshness_errors))


def validate_round175_receipt() -> None:
    """Authenticate the frozen Round-174 bytes and the Round-175 receipt."""
    for relative, expected in FROZEN_ROUND174.items():
        actual = _sha256(_stable_regular_bytes(REPORT / relative))
        if actual != expected:
            raise CurrentSpineFailure(
                f"frozen Round-174 hash mismatch: {relative}: expected {expected}, got {actual}"
            )

    receipt_bytes = _stable_regular_bytes(REPORT / ROUND175_RECEIPT)
    receipt_sha256 = _sha256(receipt_bytes)
    if receipt_sha256 != ROUND175_RECEIPT_SHA256:
        raise CurrentSpineFailure(
            "Round-175 receipt hash mismatch: "
            f"expected {ROUND175_RECEIPT_SHA256}, got {receipt_sha256}"
        )
    try:
        receipt = receipt_bytes.decode("ascii")
    except UnicodeDecodeError as exc:
        raise CurrentSpineFailure("Round-175 receipt must be ASCII") from exc
    for required in REQUIRED_RECEIPT_TEXT:
        if required not in receipt:
            raise CurrentSpineFailure(f"Round-175 claim-boundary text is missing: {required!r}")


def _round176_dependency_paths() -> set[Path]:
    """Return the complete manifest-declared Round-176 read dependency set."""
    manifest_path = REPORT / ROUND176_MANIFEST
    manifest_bytes = _stable_regular_bytes(manifest_path)

    def reject_json_token(token: str) -> object:
        raise CurrentSpineFailure(f"Round-176 manifest numeric token forbidden: {token}")

    try:
        manifest = json.loads(
            manifest_bytes.decode("ascii"),
            object_pairs_hook=_unique_object,
            parse_float=reject_json_token,
            parse_constant=reject_json_token,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CurrentSpineFailure(f"strict Round-176 manifest decode failed: {exc}") from exc
    if type(manifest) is not dict:
        raise CurrentSpineFailure("Round-176 manifest must be an object")

    expected_top_keys = {
        "claim_boundary",
        "forbidden_selected_roles",
        "preflight_role_catalog",
        "preflight_subordinate_inventory",
        "schema",
        "source_dependency_dag",
        "stage",
        "status",
        "supporting_evidence",
    }
    if set(manifest) != expected_top_keys:
        raise CurrentSpineFailure("Round-176 manifest top-level schema drifted")
    if (
        manifest.get("schema")
        != "encounter_continuum_c1_n0_same_member_preflight_outer_manifest_v1"
    ):
        raise CurrentSpineFailure("Round-176 manifest schema identifier drifted")

    claim_boundary = manifest.get("claim_boundary")
    if type(claim_boundary) is not dict or not claim_boundary:
        raise CurrentSpineFailure("Round-176 claim boundary is missing")
    if any(type(value) is not bool or value is not False for value in claim_boundary.values()):
        raise CurrentSpineFailure("Round-176 claim boundary contains a promoted flag")

    role_catalog = manifest.get("preflight_role_catalog")
    if type(role_catalog) is not dict or set(role_catalog) != {
        "preflight_role_catalog_cardinality_11",
        "primitive_sources",
    }:
        raise CurrentSpineFailure("Round-176 primitive role catalog drifted")

    inventories: tuple[tuple[str, object, int], ...] = (
        ("primitive_sources", role_catalog.get("primitive_sources"), 11),
        ("supporting_evidence", manifest.get("supporting_evidence"), 18),
        (
            "preflight_subordinate_inventory",
            manifest.get("preflight_subordinate_inventory"),
            48,
        ),
    )
    dependencies = {manifest_path}
    declared_relative_paths: set[str] = set()
    for label, inventory, expected_count in inventories:
        if type(inventory) is not list or len(inventory) != expected_count:
            raise CurrentSpineFailure(
                f"Round-176 {label} cardinality drifted: expected {expected_count}"
            )
        for index, entry in enumerate(inventory):
            if type(entry) is not dict or type(entry.get("path")) is not str:
                raise CurrentSpineFailure(f"Round-176 {label}[{index}] path is malformed")
            relative_text = entry["path"]
            relative_path = Path(relative_text)
            if (
                not relative_text
                or "\\" in relative_text
                or relative_path.is_absolute()
                or relative_path.as_posix() != relative_text
                or any(part in ("", ".", "..") for part in relative_path.parts)
            ):
                raise CurrentSpineFailure(f"unsafe Round-176 dependency path: {relative_text!r}")
            if relative_text in declared_relative_paths:
                raise CurrentSpineFailure(f"duplicate Round-176 dependency path: {relative_text}")
            declared_relative_paths.add(relative_text)
            dependencies.add(REPORT / relative_path)

    if len(declared_relative_paths) != 77 or len(dependencies) != 78:
        raise CurrentSpineFailure("Round-176 dependency-set cardinality drifted")
    return dependencies


def _round177_dependency_paths() -> set[Path]:
    """Return the authenticated Round-177 package and declared dependency set."""
    package = REPORT / ROUND177_PACKAGE
    manifest_path = REPORT / ROUND177_MANIFEST
    manifest_bytes = _stable_regular_bytes(manifest_path)

    def reject_json_token(token: str) -> object:
        raise CurrentSpineFailure(f"Round-177 manifest numeric token forbidden: {token}")

    try:
        manifest = json.loads(
            manifest_bytes.decode("ascii"),
            object_pairs_hook=_unique_object,
            parse_float=reject_json_token,
            parse_constant=reject_json_token,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CurrentSpineFailure(f"strict Round-177 manifest decode failed: {exc}") from exc
    if type(manifest) is not dict:
        raise CurrentSpineFailure("Round-177 manifest must be an object")

    expected_top_keys = {
        "claim_boundary",
        "code_inventory",
        "forbidden_selected_roles",
        "predecessor_prefix_dag",
        "reconstruction_counts",
        "role_catalog",
        "schema",
        "stage",
        "status",
        "subordinate_inventory",
        "supporting_evidence",
    }
    if set(manifest) != expected_top_keys:
        raise CurrentSpineFailure("Round-177 manifest top-level schema drifted")
    if (
        manifest.get("schema")
        != "encounter_continuum_c1_c2_n0_predecessor_authority_candidate_manifest_v1"
    ):
        raise CurrentSpineFailure("Round-177 manifest schema identifier drifted")

    claim_boundary = manifest.get("claim_boundary")
    if type(claim_boundary) is not dict or not claim_boundary:
        raise CurrentSpineFailure("Round-177 claim boundary is missing")
    if any(type(value) is not bool or value is not False for value in claim_boundary.values()):
        raise CurrentSpineFailure("Round-177 claim boundary contains a promoted flag")

    inventories: tuple[tuple[str, object, int], ...] = (
        ("role_catalog", manifest.get("role_catalog"), 8),
        ("supporting_evidence", manifest.get("supporting_evidence"), 9),
        ("subordinate_inventory", manifest.get("subordinate_inventory"), 48),
        ("code_inventory", manifest.get("code_inventory"), 9),
    )
    dependencies: set[Path] = set()
    declared_relative_paths: set[str] = set()
    for label, inventory, expected_count in inventories:
        if type(inventory) is not list or len(inventory) != expected_count:
            raise CurrentSpineFailure(
                f"Round-177 {label} cardinality drifted: expected {expected_count}"
            )
        for index, entry in enumerate(inventory):
            if (
                type(entry) is not dict
                or set(entry) != {"path", "role", "sha256"}
                or type(entry.get("path")) is not str
                or type(entry.get("role")) is not str
                or type(entry.get("sha256")) is not str
            ):
                raise CurrentSpineFailure(f"Round-177 {label}[{index}] is malformed")
            relative_text = entry["path"]
            relative_path = Path(relative_text)
            if (
                not relative_text
                or "\\" in relative_text
                or relative_path.is_absolute()
                or relative_path.as_posix() != relative_text
                or any(part in ("", ".", "..") for part in relative_path.parts)
            ):
                raise CurrentSpineFailure(f"unsafe Round-177 dependency path: {relative_text!r}")
            if relative_text in declared_relative_paths:
                raise CurrentSpineFailure(f"duplicate Round-177 dependency path: {relative_text}")
            declared_relative_paths.add(relative_text)
            dependency = REPORT / relative_path
            if _sha256(_stable_regular_bytes(dependency)) != entry["sha256"]:
                raise CurrentSpineFailure(f"Round-177 dependency hash mismatch: {relative_text}")
            dependencies.add(dependency)

    if len(declared_relative_paths) != 74 or len(dependencies) != 74:
        raise CurrentSpineFailure("Round-177 manifest dependency-set cardinality drifted")

    expected_package_filenames = {
        "bundle.json",
        "continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate.json",
        "continuum_c1_c2_n0_external_commitment_review_request_v1.json",
        "continuum_c1_c2_n0_member_spec_v3_candidate.json",
        "continuum_c1_c2_n0_method_parameter_registry_v2_candidate.json",
        "continuum_c1_c2_n0_outward_method_registry_v2_candidate.json",
        "continuum_c1_c2_n0_predecessor_authority_candidate_manifest_v1.json",
    }
    try:
        package_entries = tuple(package.iterdir())
    except OSError as exc:
        raise CurrentSpineFailure(f"Round-177 package cannot be listed: {exc}") from exc
    if {entry.name for entry in package_entries} != expected_package_filenames:
        raise CurrentSpineFailure("Round-177 package filename inventory drifted")
    package_paths = {package / name for name in expected_package_filenames}
    for path in package_paths:
        _stable_regular_bytes(path)
    dependencies.update(package_paths)
    if len(dependencies) != 77:
        raise CurrentSpineFailure("Round-177 complete dependency-set cardinality drifted")
    return dependencies


def _snapshot_allowlist(checks: Sequence[Check]) -> dict[str, str]:
    paths = {
        theorem_build.MANIFEST,
        *theorem_build._required_source_paths().values(),
        *theorem_build._published_file_paths().values(),
        *(REPORT / relative for relative in FROZEN_ROUND174),
        REPORT / ROUND175_RECEIPT,
        REPORT / "artifacts/data/continuum_c2_one_sided_free_residual_neutral_fixture_v1.json",
        REPORT / "artifacts/data/continuum_c2_complex_sector_h2_neutral_fixture_v1.json",
        REPORT / "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json",
        REPORT / "artifacts/data/continuum_c2_source_bound_map_cut_killing_contract_v1.json",
        REPORT / "artifacts/data/continuum_c1_c2_n0_member_spec_v2.json",
        REPORT / "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v2.json",
        REPORT / "artifacts/data/continuum_c1_symbolic_control_method_source_v1.json",
        REPORT / "artifacts/data/continuum_c1_n0_same_member_preflight_outer_manifest_v1.json",
        REPORT / "artifacts/data/continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.json",
        *_round176_dependency_paths(),
        *_round177_dependency_paths(),
    }
    for check in checks:
        for argument in check.argv:
            if argument.endswith(".py"):
                paths.add(REPOSITORY / argument)
    return {
        str(path.relative_to(REPOSITORY)): _sha256(_stable_regular_bytes(path))
        for path in sorted(paths)
    }


def _junit_counts(path: Path) -> tuple[int, int, int, int, int]:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, FileNotFoundError) as exc:
        raise CurrentSpineFailure(f"pytest JUnit receipt is missing or malformed: {exc}") from exc
    if root.tag == "testsuite":
        suites = [root]
    elif root.tag == "testsuites":
        suites = list(root.findall("testsuite"))
    else:
        raise CurrentSpineFailure(f"unexpected JUnit root: {root.tag}")
    ledger = tuple(
        sum(int(suite.attrib.get(field, "0")) for suite in suites)
        for field in ("tests", "failures", "errors", "skipped")
    )
    cases = sum(len(suite.findall("testcase")) for suite in suites)
    return (*ledger, cases)


Runner = Callable[..., subprocess.CompletedProcess[str]]


def run_checks(
    checks: Sequence[Check] = CHECKS,
    *,
    runner: Runner = subprocess.run,
) -> None:
    """Run checks serially and stop at the first nonzero subprocess."""
    validate_environment()
    validate_round175_receipt()
    validate_manifest()
    before = _snapshot_allowlist(checks)
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
        }
    )
    environment.pop("PYTEST_ADDOPTS", None)
    with tempfile.TemporaryDirectory(prefix="encounter-current-spine-") as directory:
        temporary = Path(directory)
        for index, check in enumerate(checks, start=1):
            print(f"[{index}/{len(checks)}] {check.name}", flush=True)
            argv = check.argv
            junit = temporary / f"{index:02d}-{check.name}.xml"
            if check.expected_pytest_tests is not None:
                if check.expected_pytest_cases is None:
                    raise CurrentSpineFailure(
                        f"pytest case count missing from contract: {check.name}"
                    )
                argv = (
                    *argv,
                    f"--junitxml={junit}",
                    f"--basetemp={temporary / f'{index:02d}-pytest'}",
                )
            completed = runner(
                argv,
                cwd=REPOSITORY,
                env=environment,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            output = completed.stdout or ""
            if completed.returncode != 0:
                if output:
                    print(output, file=sys.stderr, end="" if output.endswith("\n") else "\n")
                raise CurrentSpineFailure(
                    f"check failed with exit {completed.returncode}: {check.name}"
                )
            if check.expected_output is not None and check.expected_output not in output:
                raise CurrentSpineFailure(
                    f"success signature missing for {check.name}: {check.expected_output!r}"
                )
            if check.expected_pytest_tests is not None:
                tests, failures, errors, skipped, cases = _junit_counts(junit)
                expected_tests = check.expected_pytest_tests
                expected_cases = check.expected_pytest_cases
                if (tests, failures, errors, skipped, cases) != (
                    expected_tests,
                    0,
                    0,
                    0,
                    expected_cases,
                ):
                    raise CurrentSpineFailure(
                        f"pytest ledger mismatch for {check.name}: "
                        f"expected {(expected_tests, 0, 0, 0, expected_cases)}, "
                        f"got {(tests, failures, errors, skipped, cases)}"
                    )
                print(
                    f"PASS {check.name} junit_tests={tests} "
                    f"collected_cases={cases} failures=0 errors=0 skipped=0"
                )
            else:
                summary = next(
                    (line for line in reversed(output.splitlines()) if line.strip()),
                    "PASS",
                )
                print(summary)
    validate_manifest()
    after = _snapshot_allowlist(checks)
    if after != before:
        changed = sorted(set(before) | set(after))
        changed = [path for path in changed if before.get(path) != after.get(path)]
        raise CurrentSpineFailure(
            "allowlisted inputs or outputs changed during verification: " + ", ".join(changed)
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list",
        action="store_true",
        help="list the exact scoped checks without executing them",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.list:
        for check in CHECKS:
            print(f"{check.name}: {shlex.join(check.argv)}")
        return 0
    try:
        run_checks()
    except (CurrentSpineFailure, FileNotFoundError, OSError) as exc:
        print(f"FAIL_CURRENT_CONTINUUM_SPINE {exc}", file=sys.stderr)
        return 1
    print(
        "PASS_CURRENT_CONTINUUM_SPINE "
        f"checks={len(CHECKS)} "
        f"neutral_assertions={DECLARED_NEUTRAL_ASSERTIONS} "
        f"pytest_collected_cases={EXPECTED_PYTEST_CASES} "
        f"pytest_junit_tests={EXPECTED_JUNIT_TESTS} "
        "scope=round10_round11_round172_round177_and_manuscript_freshness "
        "full_report=false ci_attestation=false production_complete_C1=false "
        "production_same_member_bridge=false formal_symbolic_candidate=false "
        "computable_C2=false complete_C3=false root_transfer=false "
        "release_eligible=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
