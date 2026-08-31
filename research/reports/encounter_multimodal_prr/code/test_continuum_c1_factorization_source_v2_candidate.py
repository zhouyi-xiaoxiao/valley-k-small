"""Positive and structural tests for the role-3 factorization candidate."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/build_continuum_c1_factorization_source_v2_candidate.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_factorization_source_v2_candidate.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return environment


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", *arguments],
        cwd=REPORT,
        env=clean_environment(),
        check=False,
        capture_output=True,
        text=True,
    )


def load_artifact() -> dict[str, object]:
    value = json.loads(ARTIFACT.read_text(encoding="ascii"))
    assert type(value) is dict
    return value


def test_builder_check_and_independent_validator_pass() -> None:
    build = run(str(BUILDER), "--check")
    assert build.returncode == 0, build.stderr
    assert "PASS_FACTORIZATION_SOURCE_V2_CANDIDATE_CHECK" in build.stdout
    validation = run(str(VALIDATOR))
    assert validation.returncode == 0, validation.stderr
    assert "PASS_FACTORIZATION_SOURCE_V2_CANDIDATE_VALIDATION" in validation.stdout


def test_fresh_no_replace_build_is_byte_identical(tmp_path: Path) -> None:
    output = tmp_path / "candidate.json"
    first = run(str(BUILDER), "--output", str(output))
    assert first.returncode == 0, first.stderr
    assert output.read_bytes() == ARTIFACT.read_bytes()
    second = run(str(BUILDER), "--output", str(output))
    assert second.returncode != 0
    assert "refusing to replace existing output" in second.stderr


def test_artifact_is_outcome_free_and_not_legacy_contract_bound() -> None:
    payload = ARTIFACT.read_text(encoding="ascii")
    for forbidden in (
        "physical_production_killing_geometry_v1",
        "two_repeat",
        "canonical_object_sha256",
        "factorization_contract_sha256",
        "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca",
        "d635dfb7dd24fc15731dfd69e20264a5515c3bf82b92569a58cd2bed3264fcd9",
        "de42fefbfc163fdcffd573d49d1156d761341c78b3756903755579dc8e9b23af",
    ):
        assert forbidden not in payload


def test_exact_measure_and_factorization_contract_is_explicit() -> None:
    artifact = load_artifact()
    measure = artifact["coordinate_and_measure_contract"]
    formulae = artifact["cell_average_formulae"]
    assert type(measure) is dict
    assert type(formulae) is dict
    assert measure["longitudinal_absolute_jacobian_exact"] == "1/1"
    assert measure["quotient_density_normalization"] == "W^-1"
    assert "Haar" in measure["transverse_common_coordinate_reduction"]
    assert formulae["factorized_profile_cell_average"] == "V_jmab=W^-1*C_ab*Phi_jm"
    assert "|R_a|*|Y_b|" in formulae["contact_average"]
    assert "|M_m|^-1" in formulae["profile_average"]


def test_profile_order_and_storage_order_are_frozen() -> None:
    artifact = load_artifact()
    profiles = artifact["profile_basis"]
    storage = artifact["storage_contract"]
    assert type(profiles) is dict
    assert type(storage) is dict
    mapping = profiles["ordered_profile_mapping"]
    assert [item["profile_index"] for item in mapping] == [0, 1, 2, 3]
    assert [item["source_role"] for item in mapping] == [
        "physical_midpoint_support_density_00",
        "physical_midpoint_support_density_01",
        "physical_midpoint_support_density_02",
        "physical_midpoint_support_density_03",
    ]
    assert storage["full_flat_index"] == "(m*n_R+a)*n_Y+b"
    assert storage["tensor_storage_order"] == "C"


def test_all_stronger_claims_remain_false() -> None:
    claims = load_artifact()["claim_boundary"]
    assert type(claims) is dict
    assert len(claims) == 18
    assert set(claims.values()) == {False}
    boundary = load_artifact()["outcome_free_contract"]
    assert type(boundary) is dict
    assert boundary["primitive_source_only"] is True
    assert all(value is False for key, value in boundary.items() if key != "primitive_source_only")


def test_source_pins_match_current_bytes() -> None:
    artifact = load_artifact()
    source_pins = artifact["source_pins"]
    assert type(source_pins) is dict
    for record in source_pins.values():
        assert type(record) is dict
        payload = (REPORT / record["path"]).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]


def test_builder_and_validator_do_not_import_one_another() -> None:
    builder_source = BUILDER.read_text(encoding="utf-8")
    validator_source = VALIDATOR.read_text(encoding="utf-8")
    assert VALIDATOR.stem not in builder_source
    assert BUILDER.stem not in validator_source
    assert "import build_continuum_c1_factorization" not in validator_source
