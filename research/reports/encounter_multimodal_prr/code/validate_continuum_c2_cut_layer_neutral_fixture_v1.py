#!/usr/bin/env python3
"""Independent exact-integer validator for the neutral C2 cut-layer fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_SOURCE = REPORT / "artifacts/data/continuum_c2_cut_layer_neutral_source_v1.json"
DEFAULT_ARTIFACT = REPORT / "artifacts/data/continuum_c2_cut_layer_neutral_fixture_v1.json"
BUILDER = REPORT / "code/build_continuum_c2_cut_layer_neutral_fixture_v1.py"
SOURCE_SCHEMA = "encounter_continuum_c2_cut_layer_neutral_source_v1"
OUTPUT_SCHEMA = "encounter_continuum_c2_cut_layer_neutral_fixture_v1"
OUTPUT_STATUS = "PASS_NEUTRAL_EXACT_CUT_LAYER_FIXTURE_ONLY_C2_HOLD"
EXPECTED_REFINEMENTS = [16, 32, 64, 128, 256]
EXPECTED_GEOMETRY = {
    "circle_pi_upper": "355/113",
    "contact_radius": "1/4",
    "density_upper": "1/1",
    "midpoint_length": "1/1",
    "sqrt_two_upper": "3/2",
    "torus_width": "1/1",
}
EXPECTED_METHOD = {
    "boundary_intersection_rule": "closed_rectangle_rmin2_le_radius2_le_rmax2",
    "cell_face_formula": "(integer_index+face_shift_in_cell_units)/N",
    "contact_fraction_values_computed": False,
    "face_shift_units": ["0/1", "1/2"],
    "periodic_chart_rule": "one_length_shifted_chart_with_contact_tube_strictly_inside",
    "rational_arithmetic_only": True,
}
EXPECTED_SOURCE_CLAIMS = {
    "complete_C1": False,
    "complete_C2": False,
    "complete_C3": False,
    "production_geometry_evidence": False,
    "release_submission_science_execution": False,
    "source_bound_cut_layer_constant": False,
}


def _json_exact_equal(actual: Any, expected: Any) -> bool:
    """Compare decoded JSON without Python's bool/int/float aliases."""

    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            _json_exact_equal(actual[key], expected[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _json_exact_equal(actual_value, expected_value)
            for actual_value, expected_value in zip(actual, expected)
        )
    return actual == expected


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json_snapshot(path: Path) -> tuple[dict[str, Any], bytes]:
    payload = path.read_bytes()
    value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON object required: {path}")
    return value, payload


def _fraction(text: Any) -> Fraction:
    if not isinstance(text, str) or text.count("/") != 1:
        raise ValueError(f"canonical p/q string required: {text!r}")
    numerator_text, denominator_text = text.split("/")
    value = Fraction(int(numerator_text), int(denominator_text))
    if value.denominator <= 0 or f"{value.numerator}/{value.denominator}" != text:
        raise ValueError(f"noncanonical rational: {text!r}")
    return value


def _f(value: Fraction | int) -> str:
    exact = Fraction(value)
    return f"{exact.numerator}/{exact.denominator}"


def _atan_alternating_partial(argument: Fraction, term_count: int) -> Fraction:
    if not 0 < argument <= 1 or term_count <= 0:
        raise ValueError("invalid arctangent certificate request")
    result = Fraction(0)
    for index in range(term_count):
        term = argument ** (2 * index + 1) / (2 * index + 1)
        result += term if index % 2 == 0 else -term
    return result


def _relative(path: Path) -> str:
    return path.resolve().relative_to(REPORT).as_posix()


def _integer_axis_min_square(lower: int, upper: int) -> int:
    if lower <= 0 <= upper:
        return 0
    return min(lower * lower, upper * upper)


def _integer_axis_max_square(lower: int, upper: int) -> int:
    return max(lower * lower, upper * upper)


def _independent_count(intervals: int, shift_x_twice: int, shift_y_twice: int) -> tuple[int, int, int]:
    """Count after scaling every coordinate by 2*N, using integers only."""

    radius_scaled = intervals // 2
    radius_square = radius_scaled * radius_scaled
    cut_count = 0
    strict_count = 0
    tangent_count = 0
    for index_x in range(-intervals // 2, intervals // 2):
        lower_x = 2 * index_x + shift_x_twice
        upper_x = lower_x + 2
        min_x = _integer_axis_min_square(lower_x, upper_x)
        max_x = _integer_axis_max_square(lower_x, upper_x)
        for index_y in range(-intervals // 2, intervals // 2):
            lower_y = 2 * index_y + shift_y_twice
            upper_y = lower_y + 2
            minimum = min_x + _integer_axis_min_square(lower_y, upper_y)
            maximum = max_x + _integer_axis_max_square(lower_y, upper_y)
            if minimum <= radius_square <= maximum:
                cut_count += 1
                if minimum < radius_square < maximum:
                    strict_count += 1
                else:
                    tangent_count += 1
    return cut_count, strict_count, tangent_count


def _expected(source: dict[str, Any], source_path: Path, source_bytes: bytes) -> dict[str, Any]:
    if set(source) != {
        "claim_boundary",
        "geometry",
        "method",
        "pi_upper_certificate",
        "refinement_counts",
        "schema",
        "status",
    }:
        raise ValueError("wrong top-level source key set")
    if source.get("schema") != SOURCE_SCHEMA:
        raise ValueError("wrong source schema")
    if source.get("status") != "NEUTRAL_GEOMETRY_SOURCE_ONLY_NO_PRODUCTION_NO_C2":
        raise ValueError("wrong source status")
    geometry = source.get("geometry")
    method = source.get("method")
    refinements = source.get("refinement_counts")
    claims = source.get("claim_boundary")
    certificate = source.get("pi_upper_certificate")
    if not all(isinstance(value, dict) for value in (geometry, method, claims, certificate)):
        raise ValueError("malformed source sections")
    if not _json_exact_equal(geometry, EXPECTED_GEOMETRY):
        raise ValueError("v1 geometry constants or keys changed")
    if not _json_exact_equal(method, EXPECTED_METHOD):
        raise ValueError("v1 method constants or keys changed")
    if not _json_exact_equal(claims, EXPECTED_SOURCE_CLAIMS):
        raise ValueError("v1 source claim keys or false values changed")
    if not _json_exact_equal(refinements, EXPECTED_REFINEMENTS):
        raise ValueError("v1 refinements changed")
    if set(certificate) != {
        "atan_1_over_239_lower_term_count",
        "atan_1_over_5_upper_term_count",
        "certified_pi_upper_from_series",
        "identity",
        "target_circle_pi_upper",
    }:
        raise ValueError("wrong pi-certificate key set")
    if certificate.get("identity") != "pi_eq_16_atan_1_over_5_minus_4_atan_1_over_239":
        raise ValueError("wrong Machin identity id")
    upper_term_count = certificate.get("atan_1_over_5_upper_term_count")
    lower_term_count = certificate.get("atan_1_over_239_lower_term_count")
    if type(upper_term_count) is not int or upper_term_count != 5:
        raise ValueError("wrong upper arctangent term count")
    if type(lower_term_count) is not int or lower_term_count != 2:
        raise ValueError("wrong lower arctangent term count")
    if certificate.get("target_circle_pi_upper") != geometry["circle_pi_upper"]:
        raise ValueError("pi-certificate target mismatch")
    certified_upper = (
        16 * _atan_alternating_partial(Fraction(1, 5), 5)
        - 4 * _atan_alternating_partial(Fraction(1, 239), 2)
    )
    if _f(certified_upper) != certificate.get("certified_pi_upper_from_series"):
        raise ValueError("pi-certificate reconstruction mismatch")
    if not certified_upper < _fraction(geometry["circle_pi_upper"]):
        raise ValueError("pi-certificate upper does not fit below target")
    radius = _fraction(geometry.get("contact_radius"))
    width = _fraction(geometry.get("torus_width"))
    pi_upper = _fraction(geometry.get("circle_pi_upper"))
    sqrt_two_upper = _fraction(geometry.get("sqrt_two_upper"))
    midpoint_length = _fraction(geometry.get("midpoint_length"))
    density_upper = _fraction(geometry.get("density_upper"))
    if radius != Fraction(1, 4) or width != 1 or pi_upper != Fraction(355, 113):
        raise ValueError("v1 geometry changed")
    analytic_constant = 4 * pi_upper * radius * sqrt_two_upper * midpoint_length * density_upper
    rows: list[dict[str, Any]] = []
    ratios: list[Fraction] = []
    for intervals in refinements:
        h = Fraction(1, intervals)
        diameter_upper = sqrt_two_upper * h
        if not diameter_upper < min(radius, width / 2 - radius):
            raise ValueError("injectivity-gap precondition failed")
        for shift_x_twice in (0, 1):
            for shift_y_twice in (0, 1):
                shift_x = Fraction(shift_x_twice, 2)
                shift_y = Fraction(shift_y_twice, 2)
                cut_count, strict_count, tangent_count = _independent_count(
                    intervals, shift_x_twice, shift_y_twice
                )
                expected_count = 2 * intervals + (4 if shift_x_twice == shift_y_twice == 0 else 0)
                if cut_count != expected_count:
                    raise RuntimeError("independent integer count violated the frozen pattern")
                cell_area = h * h
                cut_area = cut_count * cell_area
                ratio = cut_area / h
                analytic_rhs = analytic_constant * h
                if not cut_area <= analytic_rhs:
                    raise RuntimeError("independent exact area exceeds analytic cap")
                ratios.append(ratio)
                rows.append(
                    {
                        "alignment_id": f"shift_x_{_f(shift_x)}__shift_y_{_f(shift_y)}",
                        "analytic_cut_area_cap": _f(analytic_rhs),
                        "analytic_cut_area_cap_pass": True,
                        "cell_area": _f(cell_area),
                        "cut_area": _f(cut_area),
                        "cut_area_over_h": _f(ratio),
                        "cut_count": cut_count,
                        "diameter_upper": _f(diameter_upper),
                        "h": _f(h),
                        "intervals_per_axis": intervals,
                        "l2_squared_cell_average_error_upper": _f(cut_area / 4),
                        "l2_squared_rate_cap": _f(analytic_rhs / 4),
                        "shift_x_cell_units": _f(shift_x),
                        "shift_y_cell_units": _f(shift_y),
                        "strict_boundary_cell_count": strict_count,
                        "tangent_boundary_cell_count": tangent_count,
                    }
                )
    finite_maximum = max(ratios)
    builder_bytes = BUILDER.read_bytes()
    return {
        "aggregate": {
            "alignment_count": 4,
            "analytic_rational_cut_area_over_h_cap": _f(analytic_constant),
            "cut_area_le_C_h_all_rows": True,
            "finite_fixture_max_cut_area_over_h": _f(finite_maximum),
            "l2_squared_cell_average_error_le_C_h_over_4_all_rows": True,
            "refinement_count": len(refinements),
            "row_count": len(rows),
        },
        "builder_binding": {
            "path": _relative(BUILDER),
            "sha256": hashlib.sha256(builder_bytes).hexdigest(),
        },
        "claim_boundary": {
            "complete_C1": False,
            "complete_C2": False,
            "complete_C3": False,
            "contact_fraction_values_verified": False,
            "cut_layer_inequality_neutral_fixture_pass": True,
            "production_geometry_evidence": False,
            "release_submission_science_execution": False,
            "source_bound_cut_layer_constant": False,
        },
        "explicit_read_counter": {
            _relative(BUILDER): 1,
            _relative(source_path): 1,
        },
        "method": {
            "analytic_cap_formula": "4*pi_upper*a*sqrt_two_upper*midpoint_length*density_upper",
            "boundary_intersection_rule": "closed_rectangle_rmin2_le_radius2_le_rmax2",
            "cell_average_l2_identity_used": "cell_area*p*(1-p)<=cell_area/4_for_cut_cells",
            "contact_fraction_values_computed": False,
            "exact_arithmetic": "python_fractions_Fraction",
            "finite_fixture_constant_is_not_theorem_constant": True,
            "periodic_chart_rule": "one_length_shifted_chart_with_contact_tube_strictly_inside",
            "pi_upper_certificate": {
                "alternating_series_parity": "five_terms_upper_for_atan_1_over_5_and_two_terms_lower_for_atan_1_over_239",
                "certified_pi_upper_from_series": certificate["certified_pi_upper_from_series"],
                "identity": certificate["identity"],
                "target_circle_pi_upper": geometry["circle_pi_upper"],
            },
        },
        "rows": rows,
        "schema": OUTPUT_SCHEMA,
        "source_binding": {
            "path": _relative(source_path),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
        },
        "status": OUTPUT_STATUS,
    }


def validate(source_path: Path, artifact_path: Path) -> dict[str, int | str]:
    source_path = source_path.resolve()
    artifact_path = artifact_path.resolve()
    source, source_bytes = _read_json_snapshot(source_path)
    artifact, artifact_bytes = _read_json_snapshot(artifact_path)
    canonical = (json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if artifact_bytes != canonical:
        raise ValueError("artifact bytes are not canonical sorted JSON")
    expected = _expected(source, source_path, source_bytes)
    if not _json_exact_equal(artifact, expected):
        raise ValueError("artifact differs from independent exact-integer reconstruction")
    return {
        "alignment_count": artifact["aggregate"]["alignment_count"],
        "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
        "refinement_count": artifact["aggregate"]["refinement_count"],
        "row_count": artifact["aggregate"]["row_count"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    arguments = parser.parse_args()
    summary = validate(arguments.source, arguments.artifact)
    print("PASS " + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
