#!/usr/bin/env python3
"""Static and two-build checks for the neutral C2 cut-layer fixture."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/build_continuum_c2_cut_layer_neutral_fixture_v1.py"
VALIDATOR = REPORT / "code/validate_continuum_c2_cut_layer_neutral_fixture_v1.py"
SOURCE = REPORT / "artifacts/data/continuum_c2_cut_layer_neutral_source_v1.json"
ARTIFACT = REPORT / "artifacts/data/continuum_c2_cut_layer_neutral_fixture_v1.json"


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=REPORT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _check(condition: bool, name: str) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"PASS {name}")


def main() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="continuum-c2-cut-layer-") as directory:
        first = Path(directory) / "first.json"
        second = Path(directory) / "second.json"
        run_first = _run(str(BUILDER), "--source", str(SOURCE), "--output", str(first))
        _check(run_first.returncode == 0 and first.is_file(), "clean_build_one")
        checks += 1
        run_second = _run(str(BUILDER), "--source", str(SOURCE), "--output", str(second))
        _check(run_second.returncode == 0 and second.is_file(), "clean_build_two")
        checks += 1
        _check(first.read_bytes() == second.read_bytes(), "two_builds_byte_identical")
        checks += 1
        _check(first.read_bytes() == ARTIFACT.read_bytes(), "canonical_artifact_current")
        checks += 1
        validate = _run(str(VALIDATOR), "--source", str(SOURCE), "--artifact", str(first))
        _check(validate.returncode == 0 and validate.stdout.startswith("PASS "), "independent_integer_validator")
        checks += 1

    artifact_bytes = ARTIFACT.read_bytes()
    artifact = json.loads(artifact_bytes)
    canonical = (json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    _check(artifact_bytes == canonical, "canonical_sorted_json")
    checks += 1
    _check(len(artifact["rows"]) == 20, "twenty_refinement_alignment_rows")
    checks += 1
    _check(artifact["aggregate"]["finite_fixture_max_cut_area_over_h"] == "9/4", "finite_maximum_nine_quarters")
    checks += 1
    _check(artifact["aggregate"]["analytic_rational_cut_area_over_h_cap"] == "1065/226", "analytic_rational_cap")
    checks += 1
    certificate = artifact["method"]["pi_upper_certificate"]
    _check(certificate["target_circle_pi_upper"] == "355/113", "pi_upper_target_pinned")
    checks += 1
    _check(
        Fraction(certificate["certified_pi_upper_from_series"]) < Fraction(certificate["target_circle_pi_upper"]),
        "machin_series_upper_below_target",
    )
    checks += 1
    for row in artifact["rows"]:
        intervals = row["intervals_per_axis"]
        shifted = row["shift_x_cell_units"] != "0/1" or row["shift_y_cell_units"] != "0/1"
        expected = 2 * intervals if shifted else 2 * intervals + 4
        _check(row["cut_count"] == expected, f"count_pattern_{row['alignment_id']}_{intervals}")
        checks += 1
        cut_area = Fraction(row["cut_area"])
        cap = Fraction(row["analytic_cut_area_cap"])
        _check(cut_area <= cap, f"analytic_cap_{row['alignment_id']}_{intervals}")
        checks += 1
    claims = artifact["claim_boundary"]
    _check(claims["cut_layer_inequality_neutral_fixture_pass"] is True, "neutral_fixture_flag_true")
    checks += 1
    _check(
        all(
            claims[key] is False
            for key in (
                "complete_C1",
                "complete_C2",
                "complete_C3",
                "contact_fraction_values_verified",
                "production_geometry_evidence",
                "release_submission_science_execution",
                "source_bound_cut_layer_constant",
            )
        ),
        "all_stronger_claims_false",
    )
    checks += 1
    _check(artifact["method"]["finite_fixture_constant_is_not_theorem_constant"] is True, "finite_constant_nonpromotion")
    checks += 1
    _check(hashlib.sha256(artifact_bytes).hexdigest() == "4b09d65fe5092face47f30a43e7f5ad793dd03cf5368b441b332a1d611a59f2c", "frozen_artifact_sha")
    checks += 1
    print(f"SUMMARY {checks}/{checks} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
