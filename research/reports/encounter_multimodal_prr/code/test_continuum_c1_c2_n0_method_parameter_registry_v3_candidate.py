"""Positive tests for the candidate-native method registry v3."""

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
BUILDER = REPORT / "code/build_continuum_c1_c2_n0_method_parameter_registry_v3_candidate.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_c2_n0_method_parameter_registry_v3_candidate.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v3_candidate.json"
DOMAIN = "encounter-outward-method-parameters-v3"
ORDER = [
    "stationary_directed_mpfr_320_v2",
    "stationary_directed_mpfr_640_sentinel_v2",
    "raw_flux_directed_mpfr_320_v2",
    "raw_flux_directed_mpfr_640_sentinel_v2",
    "raw_flux_binary64_decode_v2",
    "exact_fraction_expression_dag_v2",
    "killing_contact_profile_mpfr_192_v2",
    "killing_analytic_disk_area_mpfr_256_v2",
    "killing_independent_simpson_remainder_v2",
    "killing_exact_full_cell_classification_v2",
]


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


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
    )


def load() -> dict[str, Any]:
    value = json.loads(ARTIFACT.read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def test_builder_check_and_independent_validator_pass() -> None:
    build = run(str(BUILDER), "--check")
    assert build.returncode == 0, build.stderr
    assert "PASS_METHOD_PARAMETER_REGISTRY_V3_CANDIDATE_CHECK" in build.stdout
    validation = run(str(VALIDATOR))
    assert validation.returncode == 0, validation.stderr
    assert "PASS_METHOD_PARAMETER_REGISTRY_V3_CANDIDATE_VALIDATION" in validation.stdout


def test_fresh_build_is_identical_and_no_replace(tmp_path: Path) -> None:
    output = tmp_path / "registry.json"
    first = run(str(BUILDER), "--output", str(output))
    assert first.returncode == 0, first.stderr
    assert output.read_bytes() == ARTIFACT.read_bytes()
    second = run(str(BUILDER), "--output", str(output))
    assert second.returncode != 0
    assert "refusing to replace existing output" in second.stderr


def test_exact_order_count_and_digest_domain() -> None:
    registry = load()
    entries = registry["parameters"]
    assert registry["parameter_count"] == 10
    assert [entry["parameter_id"] for entry in entries] == ORDER
    for entry in entries:
        expected = hashlib.sha256(
            DOMAIN.encode("ascii") + b"\0" + canonical(entry["parameters"])
        ).hexdigest()
        assert entry["method_parameter_sha256"] == expected


def test_scopes_are_candidate_native_and_exact() -> None:
    by_id = {entry["parameter_id"]: entry["parameters"] for entry in load()["parameters"]}
    assert by_id["stationary_directed_mpfr_320_v2"]["source_role_scope"] == [
        "role9_stationary_physical_integral"
    ]
    assert by_id["raw_flux_directed_mpfr_320_v2"]["source_role_scope"] == [
        "role8_raw_axis_formula_primitive"
    ]
    assert by_id["exact_fraction_expression_dag_v2"]["source_role_scope"] == [
        "role8_raw_axis_formula_primitive",
        "role9_stationary_physical_integral",
        "same_member_mass_flux_composition",
        "symbolic_killing_composition",
    ]
    for identifier in ORDER[6:]:
        assert by_id[identifier]["source_role_scope"] == ["role10_killing_factor_geometry"]


def test_selected_precision_and_sentinel_semantics_are_exact() -> None:
    by_id = {entry["parameter_id"]: entry["parameters"] for entry in load()["parameters"]}
    generic = "primary_interval_contains_higher_precision_same_backend_sentinel"
    assert by_id["stationary_directed_mpfr_320_v2"]["precision_bits"] == 320
    assert by_id["stationary_directed_mpfr_640_sentinel_v2"]["precision_bits"] == 640
    assert by_id["stationary_directed_mpfr_640_sentinel_v2"]["containment_relation"] == generic
    assert by_id["raw_flux_directed_mpfr_320_v2"]["precision_bits"] == 320
    assert by_id["raw_flux_directed_mpfr_640_sentinel_v2"]["precision_bits"] == 640
    assert by_id["raw_flux_directed_mpfr_640_sentinel_v2"]["containment_relation"] == generic


def test_all_claims_are_false_and_no_outcome_keys_exist() -> None:
    registry = load()
    claims = registry["claim_boundary"]
    assert len(claims) == 18
    assert set(claims.values()) == {False}

    def keys(node: Any) -> list[str]:
        if type(node) is dict:
            return [key for key, item in node.items()] + [
                nested for item in node.values() for nested in keys(item)
            ]
        if type(node) is list:
            return [nested for item in node for nested in keys(item)]
        return []

    assert not [
        key for key in keys(registry) if "result" in key.lower() or "observed" in key.lower()
    ]


def test_builder_and_validator_are_source_separated() -> None:
    builder = BUILDER.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8")
    assert VALIDATOR.stem not in builder
    assert BUILDER.stem not in validator
    assert "import build_continuum_c1_c2_n0_method_parameter" not in validator
