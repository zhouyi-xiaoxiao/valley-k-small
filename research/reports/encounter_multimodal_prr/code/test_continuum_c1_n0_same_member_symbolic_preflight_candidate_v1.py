"""Static/currentness tests for the Round-176 n=0 same-member preflight."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/build_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.py"
CANDIDATE_RELATIVE = (
    "artifacts/data/continuum_c1_n0_same_member_symbolic_preflight_candidate_v1.json"
)
OUTPUTS = [
    "artifacts/data/continuum_c1_c2_n0_member_spec_v2.json",
    "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v2.json",
    "artifacts/data/continuum_c1_symbolic_control_method_source_v1.json",
    "artifacts/data/continuum_c1_n0_same_member_preflight_outer_manifest_v1.json",
    CANDIDATE_RELATIVE,
]


def load_validator():
    spec = importlib.util.spec_from_file_location("round176_validator", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATION = load_validator()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return environment


def run_builder(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(BUILDER), *arguments],
        cwd=REPORT.parents[2],
        env=clean_environment(),
        check=False,
        capture_output=True,
        text=True,
    )


def test_independent_validator_reconstructs_all_join_counts() -> None:
    candidate_sha, counts = VALIDATION.validate_package()
    assert candidate_sha == sha(REPORT / CANDIDATE_RELATIVE)
    assert counts == {
        "axis_join_count": 36,
        "configuration_join_count": 12,
        "killing_profile_join_count": 48,
        "periodic_seam_edge_count": 12,
        "raw_axis_cell_record_count": 5037,
        "raw_axis_edge_record_count": 5013,
        "stationary_axis_cell_record_count": 5037,
    }


def test_builder_check_is_current_and_does_not_modify_outputs() -> None:
    before = {relative: sha(REPORT / relative) for relative in OUTPUTS}
    result = run_builder("--check")
    after = {relative: sha(REPORT / relative) for relative in OUTPUTS}
    assert result.returncode == 0, result.stderr
    assert "correlated_member=false formal_candidate=false release=false" in result.stdout
    assert before == after


def test_two_clean_builds_are_byte_identical(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    result_first = run_builder("--output-root", str(first))
    result_second = run_builder("--output-root", str(second))
    assert result_first.returncode == 0, result_first.stderr
    assert result_second.returncode == 0, result_second.stderr
    for relative in OUTPUTS:
        assert (first / relative).read_bytes() == (second / relative).read_bytes()
        assert (first / relative).read_bytes() == (REPORT / relative).read_bytes()


def test_check_on_missing_output_root_creates_nothing(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    result = run_builder("--check", "--output-root", str(empty))
    assert result.returncode != 0
    assert not empty.exists()


def test_every_promotion_flag_and_blocker_remains_false() -> None:
    candidate = json.loads((REPORT / CANDIDATE_RELATIVE).read_text(encoding="ascii"))
    assert candidate["claim_boundary"]
    assert all(value is False for value in candidate["claim_boundary"].values())
    assert [item["cleared"] for item in candidate["blocking_conditions"]] == [False] * 9
    assert (
        candidate["member_semantics"]["one_correlated_distinguished_ideal_member_is_contained"]
        is False
    )
    assert (
        candidate["role_binding_summary"]["production_payload_roles_1_through_11_formally_bound"]
        is False
    )


def test_preflight_uses_no_reserved_formal_candidate_or_receipt_basename() -> None:
    forbidden = {
        "encounter_c1_gauge_killing_symbolic_candidate_v1.json",
        "encounter_c1_gauge_killing_symbolic_acceptance_receipt_v1.json",
    }
    assert not forbidden.intersection(path.name for path in (REPORT / "artifacts/data").iterdir())
    assert Path(CANDIDATE_RELATIVE).name not in forbidden


@pytest.mark.parametrize("path", [BUILDER, VALIDATOR])
def test_builder_and_validator_use_standard_library_only(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    assert imports <= {
        "__future__",
        "argparse",
        "collections",
        "fractions",
        "hashlib",
        "json",
        "os",
        "pathlib",
        "stat",
        "sys",
        "tempfile",
        "typing",
    }
    if path == VALIDATOR:
        assert all(
            not (
                isinstance(node, ast.ImportFrom)
                and node.module
                and "build_continuum" in node.module
            )
            for node in ast.walk(tree)
        )


def test_validator_rejects_symlink_candidate(tmp_path: Path) -> None:
    candidate = REPORT / CANDIDATE_RELATIVE
    link = tmp_path / "candidate-link.json"
    link.symlink_to(candidate)
    with pytest.raises(VALIDATION.PreflightValidationError):
        VALIDATION.validate_package(candidate_path=link)
