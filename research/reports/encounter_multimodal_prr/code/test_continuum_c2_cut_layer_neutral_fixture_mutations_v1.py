#!/usr/bin/env python3
"""Adversarial mutation checks for the neutral C2 cut-layer fixture."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/build_continuum_c2_cut_layer_neutral_fixture_v1.py"
VALIDATOR = REPORT / "code/validate_continuum_c2_cut_layer_neutral_fixture_v1.py"
SOURCE = REPORT / "artifacts/data/continuum_c2_cut_layer_neutral_source_v1.json"
ARTIFACT = REPORT / "artifacts/data/continuum_c2_cut_layer_neutral_fixture_v1.json"


def _canonical(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def _validator(source: Path, artifact: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--source", str(source), "--artifact", str(artifact)],
        cwd=REPORT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _builder(source: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BUILDER), "--source", str(source), "--output", str(output)],
        cwd=REPORT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    base = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    source_base = json.loads(SOURCE.read_text(encoding="utf-8"))
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("cut_count", lambda value: value["rows"][0].__setitem__("cut_count", value["rows"][0]["cut_count"] + 1)),
        ("cut_area", lambda value: value["rows"][0].__setitem__("cut_area", "1/1")),
        ("shift", lambda value: value["rows"][0].__setitem__("shift_x_cell_units", "1/2")),
        ("finite_cap", lambda value: value["aggregate"].__setitem__("finite_fixture_max_cut_area_over_h", "2/1")),
        ("complete_c2", lambda value: value["claim_boundary"].__setitem__("complete_C2", True)),
        ("source_sha", lambda value: value["source_binding"].__setitem__("sha256", "0" * 64)),
        ("remove_row", lambda value: value["rows"].pop()),
        ("noncanonical_rational", lambda value: value["rows"][0].__setitem__("h", "2/32")),
        ("row_order", lambda value: value.__setitem__("rows", list(reversed(value["rows"])))),
        ("analytic_flag", lambda value: value["rows"][0].__setitem__("analytic_cut_area_cap_pass", False)),
        ("contact_fraction_claim", lambda value: value["claim_boundary"].__setitem__("contact_fraction_values_verified", True)),
        ("builder_sha", lambda value: value["builder_binding"].__setitem__("sha256", "f" * 64)),
        ("strict_count", lambda value: value["rows"][0].__setitem__("strict_boundary_cell_count", 0)),
        ("tangent_count", lambda value: value["rows"][0].__setitem__("tangent_boundary_cell_count", 0)),
        ("claim_false_numeric_alias", lambda value: value["claim_boundary"].__setitem__("complete_C2", 0)),
        ("flag_true_numeric_alias", lambda value: value["claim_boundary"].__setitem__("cut_layer_inequality_neutral_fixture_pass", 1)),
        ("row_int_float_alias", lambda value: value["rows"][0].__setitem__("cut_count", float(value["rows"][0]["cut_count"]))),
    ]
    passes = 0
    with tempfile.TemporaryDirectory(prefix="continuum-c2-cut-layer-mutations-") as directory:
        root = Path(directory)
        for name, mutate in mutations:
            candidate = copy.deepcopy(base)
            mutate(candidate)
            path = root / f"{name}.json"
            path.write_bytes(_canonical(candidate))
            result = _validator(SOURCE, path)
            if result.returncode == 0:
                raise AssertionError(f"mutation unexpectedly accepted: {name}")
            print(f"PASS reject_{name}")
            passes += 1

        duplicate = root / "duplicate_key.json"
        raw = ARTIFACT.read_text(encoding="utf-8")
        duplicate.write_text(raw.replace('{\n  "aggregate"', '{\n  "schema": "duplicate",\n  "aggregate"', 1), encoding="utf-8")
        result = _validator(SOURCE, duplicate)
        if result.returncode == 0:
            raise AssertionError("duplicate key unexpectedly accepted")
        print("PASS reject_duplicate_key")
        passes += 1

        source_mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
            ("source_radius", lambda value: value["geometry"].__setitem__("contact_radius", "1/3")),
            ("source_false_pi_upper", lambda value: (value["geometry"].__setitem__("circle_pi_upper", "62831/20000"), value["pi_upper_certificate"].__setitem__("target_circle_pi_upper", "62831/20000"))),
            ("source_empty_claims", lambda value: value.__setitem__("claim_boundary", {})),
            ("source_missing_claim", lambda value: value["claim_boundary"].pop("complete_C2")),
            ("source_extra_claim", lambda value: value["claim_boundary"].__setitem__("invented", False)),
            ("source_method_formula", lambda value: value["method"].__setitem__("cell_face_formula", "nonsense")),
            ("source_extra_method", lambda value: value["method"].__setitem__("invented", True)),
            ("source_negative_density", lambda value: value["geometry"].__setitem__("density_upper", "-1/1")),
            ("source_refinements", lambda value: value.__setitem__("refinement_counts", [16, 32])),
            ("source_schema", lambda value: value.__setitem__("schema", "wrong")),
            ("source_status", lambda value: value.__setitem__("status", "wrong")),
            ("source_certificate_terms", lambda value: value["pi_upper_certificate"].__setitem__("atan_1_over_5_upper_term_count", 3)),
            ("source_certificate_fraction", lambda value: value["pi_upper_certificate"].__setitem__("certified_pi_upper_from_series", "3/1")),
            ("source_claim_false_numeric_alias", lambda value: value["claim_boundary"].__setitem__("complete_C2", 0)),
            ("source_method_false_numeric_alias", lambda value: value["method"].__setitem__("contact_fraction_values_computed", 0)),
            ("source_method_true_numeric_alias", lambda value: value["method"].__setitem__("rational_arithmetic_only", 1)),
            ("source_certificate_term_float", lambda value: value["pi_upper_certificate"].__setitem__("atan_1_over_5_upper_term_count", 5.0)),
            ("source_refinement_float", lambda value: value["refinement_counts"].__setitem__(0, 16.0)),
        ]
        for name, mutate in source_mutations:
            candidate_source = copy.deepcopy(source_base)
            mutate(candidate_source)
            source_path = root / f"{name}.json"
            source_path.write_bytes(_canonical(candidate_source))
            validator_result = _validator(source_path, ARTIFACT)
            builder_result = _builder(source_path, root / f"{name}_artifact.json")
            if validator_result.returncode == 0 or builder_result.returncode == 0:
                raise AssertionError(f"mutated source unexpectedly accepted: {name}")
            print(f"PASS reject_{name}_by_builder_and_validator")
            passes += 1

    print(f"SUMMARY {passes}/{passes} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
