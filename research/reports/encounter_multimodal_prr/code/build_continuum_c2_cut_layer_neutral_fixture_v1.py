#!/usr/bin/env python3
"""Build an exact-rational neutral cut-layer fixture for the C2 route.

The fixture counts only Cartesian cells whose closed rectangle meets the
boundary of a radius-1/4 disk on a unit torus.  It does not evaluate contact
fractions, controls, budgets, semigroups, roots, or production results.  Its
finite exact count and the analytic tube cap are diagnostics, not C2 evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_SOURCE = REPORT / "artifacts/data/continuum_c2_cut_layer_neutral_source_v1.json"
DEFAULT_OUTPUT = REPORT / "artifacts/data/continuum_c2_cut_layer_neutral_fixture_v1.json"
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


def _load_json_bytes(payload: bytes, path: Path) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON object required: {path}")
    return value


def _fraction(text: Any) -> Fraction:
    if not isinstance(text, str) or "/" not in text:
        raise ValueError(f"canonical p/q string required, got {text!r}")
    numerator_text, denominator_text = text.split("/", 1)
    if not numerator_text or not denominator_text:
        raise ValueError(f"invalid rational: {text!r}")
    numerator = int(numerator_text)
    denominator = int(denominator_text)
    if denominator <= 0:
        raise ValueError(f"positive denominator required: {text!r}")
    value = Fraction(numerator, denominator)
    if f"{value.numerator}/{value.denominator}" != text:
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


def _axis_min_square(lower: Fraction, upper: Fraction) -> Fraction:
    if not lower < upper:
        raise ValueError("nonpositive cell interval")
    if lower <= 0 <= upper:
        return Fraction(0)
    return min(lower * lower, upper * upper)


def _axis_max_square(lower: Fraction, upper: Fraction) -> Fraction:
    return max(lower * lower, upper * upper)


def _count_boundary_cells(
    intervals: int,
    shift_x: Fraction,
    shift_y: Fraction,
    radius: Fraction,
) -> tuple[int, int, int]:
    radius_square = radius * radius
    cut_count = 0
    strict_count = 0
    tangent_count = 0
    indices = range(-intervals // 2, intervals // 2)
    for index_x in indices:
        lower_x = (Fraction(index_x) + shift_x) / intervals
        upper_x = (Fraction(index_x + 1) + shift_x) / intervals
        min_x = _axis_min_square(lower_x, upper_x)
        max_x = _axis_max_square(lower_x, upper_x)
        for index_y in indices:
            lower_y = (Fraction(index_y) + shift_y) / intervals
            upper_y = (Fraction(index_y + 1) + shift_y) / intervals
            minimum = min_x + _axis_min_square(lower_y, upper_y)
            maximum = max_x + _axis_max_square(lower_y, upper_y)
            if minimum <= radius_square <= maximum:
                cut_count += 1
                if minimum < radius_square < maximum:
                    strict_count += 1
                else:
                    tangent_count += 1
    return cut_count, strict_count, tangent_count


def _validate_source(source: dict[str, Any]) -> None:
    if set(source) != {
        "claim_boundary",
        "geometry",
        "method",
        "pi_upper_certificate",
        "refinement_counts",
        "schema",
        "status",
    }:
        raise ValueError("wrong top-level neutral-source key set")
    if source.get("schema") != SOURCE_SCHEMA:
        raise ValueError("wrong neutral-source schema")
    if source.get("status") != "NEUTRAL_GEOMETRY_SOURCE_ONLY_NO_PRODUCTION_NO_C2":
        raise ValueError("wrong neutral-source status")
    geometry = source.get("geometry")
    method = source.get("method")
    claims = source.get("claim_boundary")
    certificate = source.get("pi_upper_certificate")
    refinements = source.get("refinement_counts")
    if not all(isinstance(value, dict) for value in (geometry, method, claims, certificate)):
        raise ValueError("source sections must be objects")
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
        raise ValueError("pi-certificate rational reconstruction mismatch")
    if not certified_upper < _fraction(geometry["circle_pi_upper"]):
        raise ValueError("Machin alternating-series upper does not fit below target")


def build(source_path: Path = DEFAULT_SOURCE) -> dict[str, Any]:
    source_path = source_path.resolve()
    source_bytes = source_path.read_bytes()
    builder_bytes = HERE.read_bytes()
    source = _load_json_bytes(source_bytes, source_path)
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    builder_sha256 = hashlib.sha256(builder_bytes).hexdigest()
    _validate_source(source)
    geometry = source["geometry"]
    method = source["method"]
    radius = _fraction(geometry["contact_radius"])
    width = _fraction(geometry["torus_width"])
    midpoint_length = _fraction(geometry["midpoint_length"])
    density_upper = _fraction(geometry["density_upper"])
    pi_upper = _fraction(geometry["circle_pi_upper"])
    sqrt_two_upper = _fraction(geometry["sqrt_two_upper"])
    if width != 1 or radius != Fraction(1, 4):
        raise ValueError("v1 neutral fixture freezes W=1 and a=1/4")
    if pi_upper != Fraction(355, 113):
        raise ValueError("v1 circle-pi upper must be exactly 355/113")
    if not sqrt_two_upper * sqrt_two_upper > 2:
        raise ValueError("declared sqrt-two upper bound is not strict")

    analytic_constant = (
        4 * pi_upper * radius * sqrt_two_upper * midpoint_length * density_upper
    )
    shifts = tuple(_fraction(value) for value in method["face_shift_units"])
    rows: list[dict[str, Any]] = []
    ratios: list[Fraction] = []
    for intervals in source["refinement_counts"]:
        h = Fraction(1, intervals)
        diameter_upper = sqrt_two_upper * h
        injectivity_gap = min(radius, width / 2 - radius)
        if not diameter_upper < injectivity_gap:
            raise ValueError("declared mesh is too coarse for the nonoverlapping tube chart")
        for shift_x in shifts:
            for shift_y in shifts:
                chart_lower_x = (Fraction(-intervals // 2) + shift_x) / intervals
                chart_upper_x = (Fraction(intervals // 2) + shift_x) / intervals
                chart_lower_y = (Fraction(-intervals // 2) + shift_y) / intervals
                chart_upper_y = (Fraction(intervals // 2) + shift_y) / intervals
                required_radius = radius + diameter_upper
                if not min(
                    -chart_lower_x,
                    chart_upper_x,
                    -chart_lower_y,
                    chart_upper_y,
                ) > required_radius:
                    raise ValueError("contact tube is not strictly inside the shifted chart")
                cut_count, strict_count, tangent_count = _count_boundary_cells(
                    intervals, shift_x, shift_y, radius
                )
                cell_area = h * h
                cut_area = cut_count * cell_area
                ratio = cut_area / h
                l2_squared_upper = cut_area / 4
                analytic_rhs = analytic_constant * h
                if not cut_area <= analytic_rhs:
                    raise RuntimeError("exact cut area exceeds analytic rational tube cap")
                expected_count = 2 * intervals + (4 if shift_x == 0 and shift_y == 0 else 0)
                if cut_count != expected_count:
                    raise RuntimeError("neutral dyadic cut-count sentinel failed")
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
                        "l2_squared_cell_average_error_upper": _f(l2_squared_upper),
                        "l2_squared_rate_cap": _f(analytic_rhs / 4),
                        "shift_x_cell_units": _f(shift_x),
                        "shift_y_cell_units": _f(shift_y),
                        "strict_boundary_cell_count": strict_count,
                        "tangent_boundary_cell_count": tangent_count,
                    }
                )

    finite_maximum = max(ratios)
    if finite_maximum != Fraction(9, 4):
        raise RuntimeError("unexpected finite fixture maximum")
    if not finite_maximum <= analytic_constant:
        raise RuntimeError("finite fixture constant exceeds analytic cap")

    return {
        "aggregate": {
            "alignment_count": len(shifts) ** 2,
            "analytic_rational_cut_area_over_h_cap": _f(analytic_constant),
            "cut_area_le_C_h_all_rows": True,
            "finite_fixture_max_cut_area_over_h": _f(finite_maximum),
            "l2_squared_cell_average_error_le_C_h_over_4_all_rows": True,
            "refinement_count": len(source["refinement_counts"]),
            "row_count": len(rows),
        },
        "builder_binding": {
            "path": _relative(HERE),
            "sha256": builder_sha256,
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
            _relative(HERE): 1,
            _relative(source_path): 1,
        },
        "method": {
            "analytic_cap_formula": "4*pi_upper*a*sqrt_two_upper*midpoint_length*density_upper",
            "boundary_intersection_rule": method["boundary_intersection_rule"],
            "cell_average_l2_identity_used": "cell_area*p*(1-p)<=cell_area/4_for_cut_cells",
            "contact_fraction_values_computed": False,
            "exact_arithmetic": "python_fractions_Fraction",
            "finite_fixture_constant_is_not_theorem_constant": True,
            "periodic_chart_rule": method["periodic_chart_rule"],
            "pi_upper_certificate": {
                "alternating_series_parity": "five_terms_upper_for_atan_1_over_5_and_two_terms_lower_for_atan_1_over_239",
                "certified_pi_upper_from_series": source["pi_upper_certificate"]["certified_pi_upper_from_series"],
                "identity": source["pi_upper_certificate"]["identity"],
                "target_circle_pi_upper": geometry["circle_pi_upper"],
            },
        },
        "rows": rows,
        "schema": OUTPUT_SCHEMA,
        "source_binding": {
            "path": _relative(source_path),
            "sha256": source_sha256,
        },
        "status": OUTPUT_STATUS,
    }


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def _write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        temporary = Path(temporary_name)
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = _canonical_bytes(build(arguments.source))
    output = arguments.output.resolve()
    if arguments.check:
        if not output.is_file() or output.read_bytes() != payload:
            raise SystemExit("cut-layer neutral fixture is stale or absent")
        print(f"PASS {output}")
        return 0
    _write_atomic(output, payload)
    print(f"WROTE {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
