#!/usr/bin/env python3
"""Exact vertex selector for a frozen rationalized B=0 modal-certificate LP.

This module is deliberately science-free.  It imports no continuum kernel,
finite-volume generator, positive-budget result, NumPy, SciPy, or LP solver.
The only numerical inputs are frozen decimal strings.  Those strings are
parsed as :class:`fractions.Fraction` objects, every candidate vertex is
solved and checked exactly, and ties are broken by the exact lexicographic
order of the four weights.

Exactness here applies only to the finite rational LP encoded by
``FROZEN_TABLES``.  The source decimals came from an ordinary binary64 B=0
quadrature and are not outward interval enclosures of continuum derivatives.
Accordingly, the method artifact produced by this module always keeps the
continuum/publication certificate on HOLD.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent
DEFAULT_OUTPUT = REPORT / "scratch" / "modal_certificate_exact_selector_method_only_result.json"

SCHEMA_VERSION = 1
STAGE = "method_only_b0_exact_rational_modal_selector"
STATUS_PASS = "PASS_EXACT_RATIONALIZED_SELECTOR"
STATUS_HOLD_NONPOSITIVE = "HOLD_RATIONALIZED_OPTIMUM_NONPOSITIVE"
STATUS_HOLD_INFEASIBLE_FLOOR = "HOLD_RATIONALIZED_SIMPLEX_FLOOR_INFEASIBLE"
STATUS_HOLD_NO_VERTEX = "HOLD_RATIONALIZED_NO_FEASIBLE_VERTEX"
STATUS_HOLD_SCALE_ZERO = "HOLD_CHECKPOINT_SCALE_ZERO"
STATUS_HOLD_INVALID_TABLE = "HOLD_RATIONALIZED_COEFFICIENT_TABLE_INVALID"
OVERALL_HOLD = "HOLD_METHOD_ONLY_NOT_A_CONTINUUM_OR_F0_CONTROL_CERTIFICATE"
CONTINUUM_HOLD = "HOLD_CONTINUUM_COEFFICIENTS_NOT_INTERVAL_CERTIFIED"
F0_COMPATIBILITY_HOLD = "HOLD_F0_CONTROL_COMPATIBILITY_NO_SILENT_REPLACEMENT"
F0_COMPATIBILITY_PASS = "PASS_EXACTLY_REPRODUCES_F0_CONTROL"

CHANNEL_COUNT = 4
VARIABLE_COUNT = CHANNEL_COUNT + 1  # four weights and unrestricted rho


@dataclass(frozen=True)
class FrozenRationalTable:
    """Frozen decimal representation of one signed normalized LP table."""

    name: str
    target_maxima: int
    checkpoint_times_decimal: tuple[str, ...]
    desired_signs: tuple[int, ...]
    weight_floor_decimal: str
    row_scales_decimal: tuple[str, ...]
    signed_normalized_coefficients_decimal: tuple[tuple[str, str, str, str], ...]

    def validate(self) -> None:
        if not self.name:
            raise ValueError("table name must be nonempty")
        if self.target_maxima < 1:
            raise ValueError("target_maxima must be positive")
        row_count = len(self.signed_normalized_coefficients_decimal)
        if row_count != 2 * self.target_maxima:
            raise ValueError("a target-m table requires exactly 2m rows")
        if len(self.checkpoint_times_decimal) != row_count:
            raise ValueError("checkpoint count must match coefficient rows")
        if len(self.desired_signs) != row_count:
            raise ValueError("sign count must match coefficient rows")
        expected_signs = tuple(1 if index % 2 == 0 else -1 for index in range(row_count))
        if self.desired_signs != expected_signs:
            raise ValueError("desired signs must alternate starting with +1")
        times = tuple(_parse_decimal(value) for value in self.checkpoint_times_decimal)
        if any(value <= 0 for value in times):
            raise ValueError("checkpoint times must be positive")
        if any(left >= right for left, right in zip(times, times[1:], strict=False)):
            raise ValueError("checkpoint times must be strictly increasing")
        floor = _parse_decimal(self.weight_floor_decimal)
        if floor < 0:
            raise ValueError("weight floor must be nonnegative")
        if len(self.row_scales_decimal) != row_count:
            raise ValueError("row-scale count must match coefficient rows")
        scales = tuple(_parse_decimal(value) for value in self.row_scales_decimal)
        if any(value <= 0 for value in scales):
            raise ValueError("every frozen row scale must be strictly positive")
        for row in self.signed_normalized_coefficients_decimal:
            if len(row) != CHANNEL_COUNT:
                raise ValueError("every coefficient row must contain exactly four channels")
            values = tuple(_parse_decimal(value) for value in row)
            if max(abs(value) for value in values) != 1:
                raise ValueError("every signed normalized row must have exact max norm one")

    @property
    def floor(self) -> Fraction:
        return _parse_decimal(self.weight_floor_decimal)

    @property
    def scales(self) -> tuple[Fraction, ...]:
        return tuple(_parse_decimal(value) for value in self.row_scales_decimal)

    @property
    def rows(self) -> tuple[tuple[Fraction, ...], ...]:
        return tuple(
            tuple(_parse_decimal(value) for value in row)
            for row in self.signed_normalized_coefficients_decimal
        )


# These are the shortest round-trip decimal representations of the ordinary
# binary64 values sign_l*d_lj/max_j(abs(d_lj)) generated by
# FourPatchContinuum(PRIMARY, broad_parameters()) on 2026-07-14.  They are
# frozen finite rationals for this selector, not continuum interval bounds.
FROZEN_TABLES = (
    FrozenRationalTable(
        name="m1",
        target_maxima=1,
        checkpoint_times_decimal=("5.5", "12.0"),
        desired_signs=(1, -1),
        weight_floor_decimal="0.03",
        row_scales_decimal=("0.2674801474024189", "0.11213730751238601"),
        signed_normalized_coefficients_decimal=(
            ("-0.6593397434471837", "1.0", "0.04057643049449547", "4.293408212312281e-05"),
            ("0.005908164154451627", "1.0", "-0.5316894021563535", "-0.4412050300032699"),
        ),
    ),
    FrozenRationalTable(
        name="m2",
        target_maxima=2,
        checkpoint_times_decimal=("2.0", "5.5", "16.0", "35.0"),
        desired_signs=(1, -1, 1, -1),
        weight_floor_decimal="0.03",
        row_scales_decimal=(
            "0.554048268115002",
            "0.2674801474024188",
            "0.06072999278484658",
            "0.005587099274431895",
        ),
        signed_normalized_coefficients_decimal=(
            ("1.0", "1.1603546024409161e-05", "1.3855853269321413e-12", "1.9616636844203973e-22"),
            ("0.6593397434471842", "-1.0", "-0.040576430494495476", "-4.2934082123122815e-05"),
            ("-0.0004475615149088995", "-0.5744836141548475", "-0.7637944413288659", "1.0"),
            ("1.339325051000316e-06", "0.046511727711955726", "1.0", "0.7262071720607719"),
        ),
    ),
    FrozenRationalTable(
        name="m3",
        target_maxima=3,
        checkpoint_times_decimal=("2.0", "5.0", "6.5", "11.0", "17.0", "35.0"),
        desired_signs=(1, -1, 1, -1, 1, -1),
        weight_floor_decimal="0.03",
        row_scales_decimal=(
            "0.554048268115002",
            "0.22974144714713002",
            "0.23845731109916096",
            "0.12927504142810492",
            "0.05394093798151121",
            "0.005587099274431895",
        ),
        signed_normalized_coefficients_decimal=(
            ("1.0", "1.1603546024409161e-05", "1.3855853269321413e-12", "1.9616636844203973e-22"),
            ("1.0", "-0.9594096685761585", "-0.016418201193845627", "-6.59128259330763e-06"),
            ("-0.3631544024050941", "1.0", "0.18552572414898608", "0.0009189373821381621"),
            ("0.012342182682642163", "1.0", "-0.8041490975383898", "-0.2763202566199642"),
            ("-0.0002487340322843361", "-0.46177069114264063", "-0.9464871578663434", "1.0"),
            ("1.339325051000316e-06", "0.046511727711955726", "1.0", "0.7262071720607719"),
        ),
    ),
)


# Raw binary64 ratios already frozen by positive_b_fixed_control_robustness_design_v1.md.
# Their exact dyadic normalizations are comparison controls only.  A different
# exact-selector vertex must never silently replace them.
F0_RAW_WEIGHT_HEX = {
    "m1": (
        "0x1.eb851eb851eb8p-6",
        "0x1.d1eb851eb8520p-1",
        "0x1.eb851eb851eb8p-6",
        "0x1.eb851eb851eb8p-6",
    ),
    "m2": (
        "0x1.1584359032fd2p-1",
        "0x1.eb851eb851eb8p-6",
        "0x1.8b39347154f3cp-5",
        "0x1.84d81c65ea487p-2",
    ),
    "m3": (
        "0x1.9b4482caaf892p-2",
        "0x1.1acf5b8b8445bp-2",
        "0x1.eb851eb851eb8p-6",
        "0x1.2b33cfbe47127p-2",
    ),
}


@dataclass(frozen=True)
class LinearConstraint:
    label: str
    coefficients: tuple[Fraction, ...]
    rhs: Fraction

    def residual(self, point: tuple[Fraction, ...]) -> Fraction:
        return sum((coefficient * value for coefficient, value in zip(self.coefficients, point, strict=True)), Fraction(0)) - self.rhs


@dataclass(frozen=True)
class VertexCandidate:
    point: tuple[Fraction, ...]
    generating_active_set: tuple[str, ...]

    @property
    def weights(self) -> tuple[Fraction, Fraction, Fraction, Fraction]:
        return self.point[:CHANNEL_COUNT]  # type: ignore[return-value]

    @property
    def rho(self) -> Fraction:
        return self.point[-1]


def _parse_decimal(value: str) -> Fraction:
    if not isinstance(value, str) or not value:
        raise ValueError("rational decimal input must be a nonempty string")
    try:
        parsed = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid finite rational decimal: {value!r}") from exc
    return parsed


def fraction_from_hex(value: str) -> Fraction:
    """Parse a finite normalized hexadecimal float literal without using float."""

    if not isinstance(value, str) or not value:
        raise ValueError("hex input must be a nonempty string")
    text = value.lower()
    sign = -1 if text.startswith("-") else 1
    if text[:1] in ("+", "-"):
        text = text[1:]
    if not text.startswith("0x") or "p" not in text:
        raise ValueError(f"unsupported hexadecimal rational: {value!r}")
    significand, exponent_text = text[2:].split("p", maxsplit=1)
    if significand.count(".") > 1:
        raise ValueError(f"unsupported hexadecimal rational: {value!r}")
    integer_text, dot, fractional_text = significand.partition(".")
    if not integer_text or (dot and not fractional_text):
        raise ValueError(f"unsupported hexadecimal rational: {value!r}")
    digits = integer_text + fractional_text
    try:
        numerator = int(digits, 16)
        exponent = int(exponent_text, 10) - 4 * len(fractional_text)
    except ValueError as exc:
        raise ValueError(f"unsupported hexadecimal rational: {value!r}") from exc
    result = Fraction(sign * numerator, 1)
    return result * (Fraction(2**exponent, 1) if exponent >= 0 else Fraction(1, 2 ** (-exponent)))


def _solve_square_exact(
    matrix: Sequence[Sequence[Fraction]], rhs: Sequence[Fraction]
) -> tuple[Fraction, ...] | None:
    """Gauss-Jordan solve in exact arithmetic; return None for singular systems."""

    size = len(matrix)
    if size == 0 or len(rhs) != size or any(len(row) != size for row in matrix):
        raise ValueError("exact square solve requires matching nonempty dimensions")
    augmented = [list(row) + [rhs_value] for row, rhs_value in zip(matrix, rhs, strict=True)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if augmented[row][column] != 0), None)
        if pivot is None:
            return None
        if pivot != column:
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor != 0:
                augmented[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(augmented[row], augmented[column], strict=True)
                ]
    return tuple(row[-1] for row in augmented)


def _constraints(table: FrozenRationalTable) -> tuple[LinearConstraint, ...]:
    checkpoint_constraints = tuple(
        LinearConstraint(
            label=f"checkpoint_{index}",
            coefficients=tuple(row) + (Fraction(-1),),
            rhs=Fraction(0),
        )
        for index, row in enumerate(table.rows)
    )
    floor_constraints = tuple(
        LinearConstraint(
            label=f"weight_floor_{index}",
            coefficients=tuple(
                Fraction(1) if index == column else Fraction(0)
                for column in range(CHANNEL_COUNT)
            )
            + (Fraction(0),),
            rhs=table.floor,
        )
        for index in range(CHANNEL_COUNT)
    )
    return checkpoint_constraints + floor_constraints


def _fraction_decimal(value: Fraction, significant_digits: int = 40) -> str:
    with localcontext() as context:
        context.prec = significant_digits + 12
        decimal_value = Decimal(value.numerator) / Decimal(value.denominator)
        return format(decimal_value, f".{significant_digits}g")


def _fraction_payload(value: Fraction) -> dict[str, str]:
    return {
        "exact": f"{value.numerator}/{value.denominator}",
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal_40_significant": _fraction_decimal(value),
    }


def _vector_payload(values: Sequence[Fraction]) -> list[dict[str, str]]:
    return [_fraction_payload(value) for value in values]


def _table_source_payload(table: FrozenRationalTable) -> dict[str, Any]:
    return {
        "name": table.name,
        "target_maxima": table.target_maxima,
        "checkpoint_times_decimal": list(table.checkpoint_times_decimal),
        "desired_signs": list(table.desired_signs),
        "weight_floor_decimal": table.weight_floor_decimal,
        "row_scales_decimal": list(table.row_scales_decimal),
        "signed_normalized_coefficients_decimal": [
            list(row) for row in table.signed_normalized_coefficients_decimal
        ],
    }


def _canonical_compact(payload: Any) -> str:
    return json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _selected_metrics(
    table: FrozenRationalTable, weights: Sequence[Fraction], rho: Fraction
) -> dict[str, Any]:
    normalized_margins = tuple(
        sum((coefficient * weight for coefficient, weight in zip(row, weights, strict=True)), Fraction(0))
        for row in table.rows
    )
    raw_signed_margins = tuple(
        scale * margin for scale, margin in zip(table.scales, normalized_margins, strict=True)
    )
    return {
        "weights": _vector_payload(weights),
        "normalized_optimum_rho": _fraction_payload(rho),
        "signed_normalized_checkpoint_margins": _vector_payload(normalized_margins),
        "minimum_signed_normalized_checkpoint_margin": _fraction_payload(min(normalized_margins)),
        "row_scales": _vector_payload(table.scales),
        "raw_signed_checkpoint_margins_in_rationalized_table_units": _vector_payload(
            raw_signed_margins
        ),
        "minimum_raw_signed_checkpoint_margin_in_rationalized_table_units": _fraction_payload(
            min(raw_signed_margins)
        ),
    }


def solve_exact_selector(table: FrozenRationalTable) -> dict[str, Any]:
    """Enumerate and verify every rational vertex, then apply exact tie breaks."""

    table_payload = _table_source_payload(table)
    common = {
        "name": table.name,
        "target_maxima": table.target_maxima,
        "coefficient_table_sha256": _sha256_text(_canonical_compact(table_payload)),
        "frozen_coefficient_source": table_payload,
        "exactness_scope": "finite_rational_lp_defined_by_frozen_decimal_strings_only",
    }
    try:
        parsed_scales = tuple(_parse_decimal(value) for value in table.row_scales_decimal)
    except ValueError as exc:
        return {
            **common,
            "status": STATUS_HOLD_INVALID_TABLE,
            "reason": "row_scale_parse_failed",
            "validation_error": str(exc),
            "selected": None,
            "enumeration": None,
        }
    if any(scale == 0 for scale in parsed_scales):
        return {
            **common,
            "status": STATUS_HOLD_SCALE_ZERO,
            "reason": "one_or_more_checkpoint_scales_are_exactly_zero",
            "selected": None,
            "enumeration": None,
        }
    try:
        table.validate()
    except ValueError as exc:
        return {
            **common,
            "status": STATUS_HOLD_INVALID_TABLE,
            "reason": "coefficient_table_validation_failed",
            "validation_error": str(exc),
            "selected": None,
            "enumeration": None,
        }
    floor = table.floor
    if CHANNEL_COUNT * floor > 1:
        return {
            **common,
            "status": STATUS_HOLD_INFEASIBLE_FLOOR,
            "reason": "four_times_weight_floor_exceeds_one_exactly",
            "selected": None,
            "enumeration": None,
        }

    constraints = _constraints(table)
    equality_coefficients = (Fraction(1),) * CHANNEL_COUNT + (Fraction(0),)
    equality_rhs = Fraction(1)
    active_set_size = VARIABLE_COUNT - 1
    solved_count = 0
    singular_count = 0
    feasible_solution_count = 0
    unique_vertices: dict[tuple[Fraction, ...], tuple[str, ...]] = {}

    for active in itertools.combinations(constraints, active_set_size):
        matrix = [equality_coefficients] + [constraint.coefficients for constraint in active]
        rhs = [equality_rhs] + [constraint.rhs for constraint in active]
        point = _solve_square_exact(matrix, rhs)
        if point is None:
            singular_count += 1
            continue
        solved_count += 1
        if sum(point[:CHANNEL_COUNT], Fraction(0)) != 1:
            raise AssertionError("exact square solve violated the simplex equality")
        if any(constraint.residual(point) < 0 for constraint in constraints):
            continue
        feasible_solution_count += 1
        labels = tuple(constraint.label for constraint in active)
        unique_vertices.setdefault(point, labels)

    enumerated_active_sets = len(tuple(itertools.combinations(constraints, active_set_size)))
    if not unique_vertices:
        return {
            **common,
            "status": STATUS_HOLD_NO_VERTEX,
            "reason": "no_exactly_feasible_vertex_found",
            "selected": None,
            "enumeration": {
                "constraints": len(constraints),
                "active_set_size": active_set_size,
                "enumerated_active_sets": enumerated_active_sets,
                "singular_active_sets": singular_count,
                "nonsingular_exact_solutions": solved_count,
                "exactly_feasible_solutions_before_deduplication": feasible_solution_count,
                "unique_exactly_feasible_vertices": 0,
            },
        }

    vertices = [VertexCandidate(point=point, generating_active_set=labels) for point, labels in unique_vertices.items()]
    optimum = max(vertex.rho for vertex in vertices)
    primary_vertices = tuple(vertex for vertex in vertices if vertex.rho == optimum)
    selected_vertex = min(primary_vertices, key=lambda vertex: vertex.weights)
    selected_residuals = {
        constraint.label: constraint.residual(selected_vertex.point) for constraint in constraints
    }
    exact_feasibility_rechecked = bool(
        sum(selected_vertex.weights, Fraction(0)) == 1
        and all(residual >= 0 for residual in selected_residuals.values())
    )
    if not exact_feasibility_rechecked:
        raise AssertionError("selected rational vertex failed its exact reconstruction")
    active_labels = sorted(label for label, residual in selected_residuals.items() if residual == 0)
    status = STATUS_PASS if optimum > 0 else STATUS_HOLD_NONPOSITIVE
    reason = "positive_exact_rationalized_optimum" if optimum > 0 else "nonpositive_exact_optimum"
    return {
        **common,
        "status": status,
        "reason": reason,
        "objective": "maximize_unrestricted_rho_then_lexicographically_minimize_w0_w1_w2_w3",
        "enumeration": {
            "constraints": len(constraints),
            "active_set_size": active_set_size,
            "enumerated_active_sets": enumerated_active_sets,
            "singular_active_sets": singular_count,
            "nonsingular_exact_solutions": solved_count,
            "exactly_feasible_solutions_before_deduplication": feasible_solution_count,
            "unique_exactly_feasible_vertices": len(vertices),
            "primary_optimal_vertices": len(primary_vertices),
            "all_linear_systems_and_constraint_residuals_used_fraction_exact_arithmetic": True,
        },
        "selected": {
            **_selected_metrics(table, selected_vertex.weights, selected_vertex.rho),
            "generating_active_set": list(selected_vertex.generating_active_set),
            "all_exactly_active_constraints": active_labels,
            "constraint_residuals": {
                label: _fraction_payload(residual)
                for label, residual in sorted(selected_residuals.items())
            },
            "simplex_sum_residual": _fraction_payload(
                sum(selected_vertex.weights, Fraction(0)) - 1
            ),
            "exact_feasibility_rechecked": exact_feasibility_rechecked,
        },
    }


def f0_exact_control(name: str) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    raw = tuple(fraction_from_hex(value) for value in F0_RAW_WEIGHT_HEX[name])
    total = sum(raw, Fraction(0))
    normalized = tuple(value / total for value in raw)
    return normalized  # type: ignore[return-value]


def compare_with_f0_control(
    table: FrozenRationalTable, selector_result: dict[str, Any]
) -> dict[str, Any]:
    if selector_result["selected"] is None:
        return {
            "status": F0_COMPATIBILITY_HOLD,
            "reason": "selector_has_no_selected_control",
            "replacement_authorized": False,
        }
    selector_weights = tuple(
        Fraction(item["exact"]) for item in selector_result["selected"]["weights"]
    )
    f0_weights = f0_exact_control(table.name)
    deltas = tuple(selector - frozen for selector, frozen in zip(selector_weights, f0_weights, strict=True))
    exact_equal = all(delta == 0 for delta in deltas)
    f0_margins = tuple(
        sum((coefficient * weight for coefficient, weight in zip(row, f0_weights, strict=True)), Fraction(0))
        for row in table.rows
    )
    f0_rho = min(f0_margins)
    selector_rho = Fraction(selector_result["selected"]["normalized_optimum_rho"]["exact"])
    signed_margin_difference = selector_rho - f0_rho
    f0_floor_feasible = all(weight >= table.floor for weight in f0_weights)
    if f0_floor_feasible and signed_margin_difference < 0:
        raise AssertionError("enumerated exact selector is worse than the comparison control")
    status = F0_COMPATIBILITY_PASS if exact_equal else F0_COMPATIBILITY_HOLD
    reason = (
        "exact_selector_weights_equal_f0_raw_over_exact_sum_control"
        if exact_equal
        else "exact_selector_weights_differ_from_f0_raw_over_exact_sum_control"
    )
    return {
        "status": status,
        "reason": reason,
        "f0_raw_weight_hex": list(F0_RAW_WEIGHT_HEX[table.name]),
        "f0_exact_raw_over_sum_weights": _vector_payload(f0_weights),
        "selector_weights": _vector_payload(selector_weights),
        "selector_minus_f0_component_deltas": _vector_payload(deltas),
        "maximum_absolute_component_delta": _fraction_payload(max(abs(delta) for delta in deltas)),
        "weights_exactly_equal": exact_equal,
        "f0_control_satisfies_exact_selector_floor": f0_floor_feasible,
        "f0_control_margin_in_the_rationalized_lp": _fraction_payload(f0_rho),
        "selector_rho_minus_f0_control_margin": _fraction_payload(signed_margin_difference),
        "selector_exact_optimality_gap_over_feasible_f0_control": (
            _fraction_payload(signed_margin_difference) if f0_floor_feasible else None
        ),
        "replacement_authorized": False,
        "required_policy_if_different": (
            "Before any positive-B evaluation, either amend and independently audit the F0 v1 "
            "control freeze, or retain the existing F0 control and treat this exact selector only "
            "as a candidate/method result while disclosing the prior family pilot."
        ),
    }


def build_method_only_result() -> dict[str, Any]:
    selector_results = {table.name: solve_exact_selector(table) for table in FROZEN_TABLES}
    compatibility = {
        table.name: compare_with_f0_control(table, selector_results[table.name])
        for table in FROZEN_TABLES
    }
    selector_passed = all(result["status"] == STATUS_PASS for result in selector_results.values())
    f0_reproduced = all(
        result["status"] == F0_COMPATIBILITY_PASS for result in compatibility.values()
    )
    source_paths = {
        "implementation": HERE / "modal_certificate_exact_selector.py",
        "tests": HERE / "test_modal_certificate_exact_selector.py",
        "exploratory_poc": HERE / "modal_certificate_lp_poc.py",
        "exploratory_poc_result": REPORT / "scratch" / "modal_certificate_lp_poc_result.json",
        "theory_note": REPORT / "notes" / "modal_certificate_theory_and_prr_redirect.md",
        "f0_design": REPORT / "notes" / "positive_b_fixed_control_robustness_design_v1.md",
    }
    source_hashes = {
        name: _sha256_file(path) if path.exists() else None for name, path in source_paths.items()
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "stage": STAGE,
        "status": OVERALL_HOLD,
        "evidence_timing": "POST_EXPLORATORY_POC_METHOD_ONLY_B0_RATIONALIZATION",
        "positive_budget_evaluated": False,
        "primary_finite_volume_grid_evaluated": False,
        "continuum_kernel_executed_by_this_producer": False,
        "external_lp_solver_used": False,
        "source_hashes": source_hashes,
        "selector_results": selector_results,
        "f0_control_compatibility": compatibility,
        "gates": {
            "all_finite_rational_lp_selectors_have_positive_exact_optima": selector_passed,
            "all_selector_weights_exactly_reproduce_f0_controls": f0_reproduced,
            "continuum_derivative_coefficients_outward_interval_certified": False,
            "full_window_box_and_complement_certificate_present": False,
            "positive_budget_evaluated": False,
        },
        "publication_certificate_status": CONTINUUM_HOLD,
        "f0_control_freeze_status": (
            F0_COMPATIBILITY_PASS if f0_reproduced else F0_COMPATIBILITY_HOLD
        ),
        "authorized_scientific_command": None,
        "claim_scope": (
            "Exact optimality and deterministic lexicographic selection for three finite LPs "
            "whose coefficients are the frozen finite rationals represented by the recorded "
            "decimal strings."
        ),
        "limitations": [
            "The exact proof concerns the rationalized coefficient tables, not continuum derivatives.",
            "The source binary64 quadrature values have no outward coefficient error intervals.",
            "Raw signed margins are exact only in the internally reconstructed rationalized table units.",
            "No box-curvature or full-complement derivative enclosure is supplied.",
            "No exact-selector weight may silently replace a different F0 raw-over-exact-sum control.",
            "No positive-budget killed process, primary FV grid, or off-lattice trajectory was evaluated.",
            "This method-only artifact is neither a publication gate nor F1 authorization.",
        ],
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-method-only-b0",
        action="store_true",
        help="enumerate only the frozen rational B=0 LP vertices",
    )
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.execute_method_only_b0:
        raise SystemExit("explicit --execute-method-only-b0 is required")
    result = build_method_only_result()
    rendered = canonical_json(result)
    if args.output is None:
        print(rendered, end="")
    else:
        output = args.output.resolve()
        if output != DEFAULT_OUTPUT.resolve():
            raise SystemExit(f"output must be exactly {DEFAULT_OUTPUT}")
        if output.exists():
            raise SystemExit("method-only output already exists; refusing overwrite")
        output.write_text(rendered, encoding="utf-8")
        print(output)
    # Overall HOLD is intentional; the command succeeds when the exact finite LPs pass.
    return 0 if all(row["status"] == STATUS_PASS for row in result["selector_results"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
