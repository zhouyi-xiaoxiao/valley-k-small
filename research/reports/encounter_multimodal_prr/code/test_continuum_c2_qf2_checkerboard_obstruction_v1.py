#!/usr/bin/env python3
"""Independent exact tests for the tensor-Q1 checkerboard obstruction."""

from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = REPORT / "code/continuum_c2_qf2_checkerboard_obstruction_v1.py"
ARTIFACT = REPORT / "artifacts/data/continuum_c2_qf2_checkerboard_obstruction_v1.json"
EXPECTED_ARTIFACT_SHA256 = "40f7c0689343eef0aca0b17a2bc95183cbf8fdca073a6d9a0d4ae1fbaa53c9bf"
DIMENSIONS = (1, 2, 3)
EVEN_INTERVALS = (2, 4, 8, 16)


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", *arguments],
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


def _f(value: Fraction | int) -> str:
    exact = Fraction(value)
    return f"{exact.numerator}/{exact.denominator}"


def _product(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def _checkerboard(index: tuple[int, ...]) -> int:
    return (-1) ** (sum(index) % 2)


def _independent_discrete_enumeration(
    dimension: int, intervals: int
) -> tuple[Fraction, Fraction]:
    """Direct graph enumeration, independent of the fixture builder."""

    h = Fraction(1, intervals)
    node_weight = h**dimension
    norm_squared = sum(
        (
            node_weight * _checkerboard(node) ** 2
            for node in itertools.product(range(intervals), repeat=dimension)
        ),
        Fraction(0),
    )
    energy = Fraction(0)
    for node in itertools.product(range(intervals), repeat=dimension):
        for axis in range(dimension):
            neighbour = tuple(
                (coordinate + 1) % intervals
                if index == axis
                else coordinate
                for index, coordinate in enumerate(node)
            )
            slope = Fraction(_checkerboard(neighbour) - _checkerboard(node), 1) / h
            energy += node_weight * slope * slope
    return norm_squared, energy


def _subsets(dimension: int) -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(index for index in range(dimension) if mask & (1 << index))
        for mask in range(1 << dimension)
    )


def _independent_q1_polynomial_enumeration(
    dimension: int, intervals: int
) -> tuple[Fraction, Fraction]:
    """Integrate monomial coefficients, not the builder's Gram matrices."""

    h = Fraction(1, intervals)
    subsets = _subsets(dimension)
    mass_total = Fraction(0)
    energy_total = Fraction(0)

    for cell in itertools.product(range(intervals), repeat=dimension):
        coefficients: dict[frozenset[int], Fraction] = {}
        for subset in subsets:
            coefficient = Fraction(0)
            subset_axes = tuple(sorted(subset))
            for mask in range(1 << len(subset_axes)):
                active = frozenset(
                    subset_axes[position]
                    for position in range(len(subset_axes))
                    if mask & (1 << position)
                )
                corner = tuple(1 if axis in active else 0 for axis in range(dimension))
                node = tuple(
                    (cell[axis] + corner[axis]) % intervals
                    for axis in range(dimension)
                )
                sign = -1 if (len(subset) - len(active)) % 2 else 1
                coefficient += sign * _checkerboard(node)
            coefficients[subset] = coefficient

        local_mass = Fraction(0)
        local_energy = Fraction(0)
        for left in subsets:
            for right in subsets:
                coefficient_product = coefficients[left] * coefficients[right]
                local_mass += coefficient_product * _product(
                    Fraction(1, 1 + (axis in left) + (axis in right))
                    for axis in range(dimension)
                )
                for derivative_axis in range(dimension):
                    if derivative_axis not in left or derivative_axis not in right:
                        continue
                    local_energy += coefficient_product * _product(
                        Fraction(1, 1 + (axis in left) + (axis in right))
                        for axis in range(dimension)
                        if axis != derivative_axis
                    )

        mass_total += h**dimension * local_mass
        energy_total += h**dimension / (h * h) * local_energy

    return mass_total, energy_total


def _expected_values(dimension: int, intervals: int) -> dict[str, Fraction]:
    h = Fraction(1, intervals)
    norm = Fraction(1)
    discrete_energy = Fraction(4 * dimension, 1) / (h * h)
    q1_norm = Fraction(1, 3**dimension)
    q1_energy = Fraction(4 * dimension, 3 ** (dimension - 1)) / (h * h)
    defect = abs(discrete_energy - q1_energy)
    energy_norm = norm + discrete_energy
    c_min = defect / (h * energy_norm)
    return {
        "absolute_free_form_defect": defect,
        "checkerboard_required_C_min": c_min,
        "discrete_energy_norm_squared": energy_norm,
        "discrete_free_energy": discrete_energy,
        "discrete_l2_norm_squared": norm,
        "h_times_checkerboard_required_C_min": h * c_min,
        "tensor_q1_free_energy": q1_energy,
        "tensor_q1_l2_norm_squared": q1_norm,
    }


def main() -> int:
    checks = 0

    before_check = ARTIFACT.read_bytes()
    check_run = _run(str(BUILDER), "--check")
    _check(
        check_run.returncode == 0
        and check_run.stdout.startswith("PASS checkerboard_obstruction_v1_check ")
        and "output_not_written=true" in check_run.stdout,
        "builder_check_regenerates_without_writing",
    )
    checks += 1
    _check(ARTIFACT.read_bytes() == before_check, "check_mode_preserves_artifact_bytes")
    checks += 1

    with tempfile.TemporaryDirectory(prefix="qf2-checkerboard-") as directory:
        first = Path(directory) / "first.json"
        second = Path(directory) / "second.json"
        first_run = _run(str(BUILDER), "--output", str(first))
        second_run = _run(str(BUILDER), "--output", str(second))
        _check(first_run.returncode == 0 and first.is_file(), "clean_build_one")
        checks += 1
        _check(second_run.returncode == 0 and second.is_file(), "clean_build_two")
        checks += 1
        _check(first.read_bytes() == second.read_bytes(), "two_builds_byte_identical")
        checks += 1
        _check(first.read_bytes() == before_check, "generated_artifact_is_current")
        checks += 1
        duplicate_before = first.read_bytes()
        duplicate_run = _run(str(BUILDER), "--output", str(first))
        _check(duplicate_run.returncode != 0, "duplicate_output_rejected")
        checks += 1
        _check(first.read_bytes() == duplicate_before, "duplicate_rejection_preserves_bytes")
        checks += 1

    artifact_bytes = ARTIFACT.read_bytes()
    artifact = json.loads(artifact_bytes)
    canonical = (
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    _check(artifact_bytes == canonical, "artifact_is_canonical_sorted_json")
    checks += 1
    _check(
        hashlib.sha256(artifact_bytes).hexdigest() == EXPECTED_ARTIFACT_SHA256,
        "frozen_artifact_sha256",
    )
    checks += 1
    _check(
        artifact["fixture_grid"]
        == {
            "dimensions": list(DIMENSIONS),
            "even_intervals_per_axis": list(EVEN_INTERVALS),
        },
        "fixture_grid_exact",
    )
    checks += 1
    _check(len(artifact["rows"]) == 12, "twelve_exact_rows")
    checks += 1

    row_map = {
        (row["dimension"], row["intervals_per_axis"]): row
        for row in artifact["rows"]
    }
    _check(set(row_map) == set(itertools.product(DIMENSIONS, EVEN_INTERVALS)), "row_keys_exact")
    checks += 1

    for dimension, intervals in itertools.product(DIMENSIONS, EVEN_INTERVALS):
        row = row_map[(dimension, intervals)]
        discrete_norm, discrete_energy = _independent_discrete_enumeration(
            dimension, intervals
        )
        q1_norm, q1_energy = _independent_q1_polynomial_enumeration(
            dimension, intervals
        )
        expected = _expected_values(dimension, intervals)
        independent = dict(expected)
        independent["discrete_l2_norm_squared"] = discrete_norm
        independent["discrete_free_energy"] = discrete_energy
        independent["tensor_q1_l2_norm_squared"] = q1_norm
        independent["tensor_q1_free_energy"] = q1_energy
        independent["absolute_free_form_defect"] = abs(discrete_energy - q1_energy)
        independent["discrete_energy_norm_squared"] = discrete_norm + discrete_energy
        h = Fraction(1, intervals)
        independent["checkerboard_required_C_min"] = independent[
            "absolute_free_form_defect"
        ] / (h * independent["discrete_energy_norm_squared"])
        independent["h_times_checkerboard_required_C_min"] = h * independent[
            "checkerboard_required_C_min"
        ]
        _check(independent == expected, f"independent_enumeration_formula_d{dimension}_N{intervals}")
        checks += 1
        encoded = {key: _f(value) for key, value in expected.items()}
        _check(row["enumerated"] == encoded, f"artifact_enumeration_d{dimension}_N{intervals}")
        checks += 1
        _check(row["closed_form"] == encoded, f"artifact_formula_d{dimension}_N{intervals}")
        checks += 1
        expected_counts = {
            "periodic_directed_positive_edges": dimension * intervals**dimension,
            "periodic_grid_nodes": intervals**dimension,
            "tensor_q1_cells": intervals**dimension,
            "tensor_q1_ordered_corner_pairs_per_cell": 4**dimension,
        }
        _check(row["enumeration_counts"] == expected_counts, f"enumeration_counts_d{dimension}_N{intervals}")
        checks += 1

    for dimension in DIMENSIONS:
        rows = [row_map[(dimension, intervals)] for intervals in EVEN_INTERVALS]
        defects = [Fraction(row["enumerated"]["absolute_free_form_defect"]) for row in rows]
        constants = [Fraction(row["enumerated"]["checkerboard_required_C_min"]) for row in rows]
        scaled = [Fraction(row["enumerated"]["h_times_checkerboard_required_C_min"]) for row in rows]
        certificate = artifact["dimension_certificates"][dimension - 1]
        limit = Fraction(certificate["asymptotic_h_times_C_min_limit"])
        lower_bound = Fraction(
            certificate["even_N_ge_2_uniform_h_times_C_min_lower_bound"]
        )
        if dimension == 1:
            _check(defects == [0] * 4 and constants == [0] * 4, "d1_zero_defect")
            checks += 1
            _check(limit == 0 and lower_bound == 0, "d1_zero_scaled_limit")
            checks += 1
        else:
            _check(all(defect > 0 for defect in defects), f"d{dimension}_positive_defect")
            checks += 1
            _check(
                all(left < right for left, right in zip(constants, constants[1:])),
                f"d{dimension}_C_min_strictly_increasing",
            )
            checks += 1
            _check(
                all(left < right < limit for left, right in zip(scaled, scaled[1:])),
                f"d{dimension}_scaled_values_increase_to_limit",
            )
            checks += 1
            _check(
                all(value >= lower_bound for value in scaled),
                f"d{dimension}_listed_scaled_lower_bound",
            )
            checks += 1
            for intervals in (2, 4, 8, 16, 32, 64, 128, 256):
                exact = _expected_values(dimension, intervals)
                c_min = exact["checkerboard_required_C_min"]
                h = Fraction(1, intervals)
                _check(
                    h * c_min >= lower_bound and c_min >= lower_bound * intervals,
                    f"d{dimension}_asymptotic_lower_bound_N{intervals}",
                )
                checks += 1

    claims = artifact["claim_boundary"]
    required_false = {
        "QF2_complete",
        "all_conforming_reconstructions_refuted",
        "all_QF2_routes_refuted",
        "complete_C1",
        "complete_C2",
        "complete_C3",
        "formal_QF2_replacement_proved",
        "production_evidence",
        "production_reconstruction_accepted",
        "release_submission_ready",
        "release_submission_science_execution",
        "residual_or_smooth_solution_routes_refuted",
        "standard_tensor_Q1_all_discrete_pairs_O_h_claim_valid",
    }
    _check(
        all(key in claims and claims[key] is False for key in required_false),
        "all_complete_release_production_and_broader_route_flags_false",
    )
    checks += 1
    _check(
        claims["exact_checkerboard_obstruction_verified"] is True,
        "neutral_exact_obstruction_flag_true",
    )
    checks += 1
    _check(
        artifact["scope"]["refutes_only"].startswith(
            "standard_periodic_nodal_tensor_Q1_reconstruction"
        )
        and "all_possible_replacements_for_QF2" in artifact["scope"]["does_not_refute"]
        and "residual_consistency_for_manufactured_smooth_solutions"
        in artifact["scope"]["does_not_refute"],
        "scope_excludes_other_reconstructions_and_residual_routes",
    )
    checks += 1

    print(f"SUMMARY {checks}/{checks} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
