#!/usr/bin/env python3
"""Build the exact neutral tensor-Q1 checkerboard obstruction fixture.

On the unit periodic d-torus, let the nodal checkerboard be

    v_j = (-1)^(j_1 + ... + j_d),   h = 1/N,

with even N.  This script independently enumerates the positive periodic
grid edges and the tensor-Q1 cell mass/stiffness integrals using Fraction
arithmetic.  The resulting counterexample obstructs one specific proposed
QF2 route: an O(h) free-form defect bound for *all* discrete pairs using the
standard nodal tensor-Q1 reconstruction and the discrete energy norm.

It does not rule out other reconstructions, restricted/smooth data classes,
or residual consistency routes, and it is not a C1/C2/C3 or production
receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_OUTPUT = (
    REPORT / "artifacts/data/continuum_c2_qf2_checkerboard_obstruction_v1.json"
)
SCHEMA = "encounter_continuum_c2_qf2_checkerboard_obstruction_v1"
STATUS = "PASS_NEUTRAL_EXACT_TENSOR_Q1_CHECKERBOARD_OBSTRUCTION_ONLY_QF2_OPEN"
DIMENSIONS = (1, 2, 3)
EVEN_INTERVALS = (2, 4, 8, 16)

MASS_1D = {
    (0, 0): Fraction(1, 3),
    (0, 1): Fraction(1, 6),
    (1, 0): Fraction(1, 6),
    (1, 1): Fraction(1, 3),
}
DERIVATIVE_1D = {
    (0, 0): Fraction(1),
    (0, 1): Fraction(-1),
    (1, 0): Fraction(-1),
    (1, 1): Fraction(1),
}


def _f(value: Fraction | int) -> str:
    exact = Fraction(value)
    return f"{exact.numerator}/{exact.denominator}"


def _product(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def _checkerboard(index: tuple[int, ...]) -> int:
    return 1 if sum(index) % 2 == 0 else -1


def _enumerate_discrete(dimension: int, intervals: int) -> tuple[Fraction, Fraction]:
    """Enumerate the mass-lumped norm and all positive periodic edges."""

    h = Fraction(1, intervals)
    volume = h**dimension
    norm_squared = Fraction(0)
    free_energy = Fraction(0)
    for node in itertools.product(range(intervals), repeat=dimension):
        value = _checkerboard(node)
        norm_squared += volume * value * value
        for axis in range(dimension):
            neighbour = list(node)
            neighbour[axis] = (neighbour[axis] + 1) % intervals
            difference_quotient = Fraction(
                _checkerboard(tuple(neighbour)) - value, 1
            ) / h
            free_energy += volume * difference_quotient * difference_quotient
    return norm_squared, free_energy


def _enumerate_tensor_q1(dimension: int, intervals: int) -> tuple[Fraction, Fraction]:
    """Enumerate exact Q1 cell integrals from nodal basis Gram matrices."""

    h = Fraction(1, intervals)
    mass_scale = h**dimension
    stiffness_scale = mass_scale / (h * h)
    corners = tuple(itertools.product((0, 1), repeat=dimension))
    norm_squared = Fraction(0)
    free_energy = Fraction(0)

    for cell in itertools.product(range(intervals), repeat=dimension):
        values: dict[tuple[int, ...], int] = {}
        for corner in corners:
            periodic_node = tuple(
                (cell[axis] + corner[axis]) % intervals
                for axis in range(dimension)
            )
            values[corner] = _checkerboard(periodic_node)

        for alpha in corners:
            for beta in corners:
                coefficient = Fraction(values[alpha] * values[beta])
                mass_weight = _product(
                    MASS_1D[(alpha[axis], beta[axis])]
                    for axis in range(dimension)
                )
                norm_squared += mass_scale * coefficient * mass_weight

                for derivative_axis in range(dimension):
                    stiffness_weight = DERIVATIVE_1D[
                        (alpha[derivative_axis], beta[derivative_axis])
                    ] * _product(
                        MASS_1D[(alpha[axis], beta[axis])]
                        for axis in range(dimension)
                        if axis != derivative_axis
                    )
                    free_energy += (
                        stiffness_scale * coefficient * stiffness_weight
                    )

    return norm_squared, free_energy


def _closed_forms(dimension: int, intervals: int) -> dict[str, Fraction]:
    h = Fraction(1, intervals)
    discrete_norm_squared = Fraction(1)
    discrete_energy = Fraction(4 * dimension, 1) / (h * h)
    q1_norm_squared = Fraction(1, 3**dimension)
    q1_energy = Fraction(4 * dimension, 3 ** (dimension - 1)) / (h * h)
    defect = abs(discrete_energy - q1_energy)
    energy_norm_squared = discrete_norm_squared + discrete_energy
    required_c_min = defect / (h * energy_norm_squared)
    return {
        "discrete_l2_norm_squared": discrete_norm_squared,
        "discrete_free_energy": discrete_energy,
        "tensor_q1_l2_norm_squared": q1_norm_squared,
        "tensor_q1_free_energy": q1_energy,
        "absolute_free_form_defect": defect,
        "discrete_energy_norm_squared": energy_norm_squared,
        "checkerboard_required_C_min": required_c_min,
        "h_times_checkerboard_required_C_min": h * required_c_min,
    }


def _dimension_certificate(dimension: int) -> dict[str, Any]:
    energy_ratio = Fraction(1, 3 ** (dimension - 1))
    defect_ratio = 1 - energy_ratio
    even_mesh_scaled_lower_bound = defect_ratio * Fraction(
        16 * dimension, 16 * dimension + 1
    )
    return {
        "asymptotic_h_times_C_min_limit": _f(defect_ratio),
        "c_min_behavior": (
            "IDENTICALLY_ZERO_FOR_THIS_CHECKERBOARD_WITNESS"
            if dimension == 1
            else "STRICTLY_INCREASING_AND_UNBOUNDED_ALONG_EVEN_N"
        ),
        "dimension": dimension,
        "even_N_ge_2_uniform_h_times_C_min_lower_bound": _f(
            even_mesh_scaled_lower_bound
        ),
        "exact_formulas": {
            "absolute_free_form_defect": "4*d*(1-3^(-(d-1)))/h^2",
            "checkerboard_required_C_min": (
                "4*d*(1-3^(-(d-1)))/(h*(h^2+4*d))"
            ),
            "discrete_free_energy": "4*d/h^2",
            "discrete_l2_norm_squared": "1",
            "discrete_energy_norm_squared": "1+4*d/h^2",
            "h_times_C_min_gap_below_limit": (
                "(1-3^(-(d-1)))*h^2/(h^2+4*d)"
            ),
            "tensor_q1_free_energy": "4*d*3^(-(d-1))/h^2",
            "tensor_q1_l2_norm_squared": "3^(-d)",
        },
        "q1_energy_ratio_to_discrete_energy": _f(energy_ratio),
        "free_form_defect_ratio_to_discrete_energy": _f(defect_ratio),
    }


def build_fixture() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for dimension in DIMENSIONS:
        previous_c_min: Fraction | None = None
        for intervals in EVEN_INTERVALS:
            h = Fraction(1, intervals)
            discrete_norm, discrete_energy = _enumerate_discrete(
                dimension, intervals
            )
            q1_norm, q1_energy = _enumerate_tensor_q1(dimension, intervals)
            closed = _closed_forms(dimension, intervals)
            enumerated = {
                "absolute_free_form_defect": abs(discrete_energy - q1_energy),
                "checkerboard_required_C_min": abs(
                    discrete_energy - q1_energy
                )
                / (h * (discrete_norm + discrete_energy)),
                "discrete_energy_norm_squared": discrete_norm + discrete_energy,
                "discrete_free_energy": discrete_energy,
                "discrete_l2_norm_squared": discrete_norm,
                "h_times_checkerboard_required_C_min": h
                * abs(discrete_energy - q1_energy)
                / (h * (discrete_norm + discrete_energy)),
                "tensor_q1_free_energy": q1_energy,
                "tensor_q1_l2_norm_squared": q1_norm,
            }
            if enumerated != closed:
                raise AssertionError(
                    f"enumeration/formula mismatch for d={dimension}, N={intervals}"
                )
            required_c_min = enumerated["checkerboard_required_C_min"]
            if previous_c_min is not None:
                if dimension == 1 and required_c_min != previous_c_min:
                    raise AssertionError("d=1 checkerboard C_min must remain zero")
                if dimension >= 2 and not required_c_min > previous_c_min:
                    raise AssertionError("positive-dimensional C_min must increase")
            previous_c_min = required_c_min

            rows.append(
                {
                    "closed_form": {key: _f(value) for key, value in closed.items()},
                    "dimension": dimension,
                    "enumerated": {
                        key: _f(value) for key, value in enumerated.items()
                    },
                    "enumeration_counts": {
                        "periodic_directed_positive_edges": (
                            dimension * intervals**dimension
                        ),
                        "periodic_grid_nodes": intervals**dimension,
                        "tensor_q1_cells": intervals**dimension,
                        "tensor_q1_ordered_corner_pairs_per_cell": 4**dimension,
                    },
                    "enumeration_matches_closed_form": True,
                    "h": _f(h),
                    "intervals_per_axis": intervals,
                    "positive_defect": enumerated[
                        "absolute_free_form_defect"
                    ]
                    > 0,
                }
            )

    return {
        "claim_boundary": {
            "QF2_complete": False,
            "all_conforming_reconstructions_refuted": False,
            "all_QF2_routes_refuted": False,
            "complete_C1": False,
            "complete_C2": False,
            "complete_C3": False,
            "exact_checkerboard_obstruction_verified": True,
            "formal_QF2_replacement_proved": False,
            "production_evidence": False,
            "production_reconstruction_accepted": False,
            "release_submission_ready": False,
            "release_submission_science_execution": False,
            "residual_or_smooth_solution_routes_refuted": False,
            "standard_tensor_Q1_all_discrete_pairs_O_h_claim_valid": False,
        },
        "conclusion": {
            "dimension_1": (
                "THIS_WITNESS_HAS_ZERO_FREE_FORM_DEFECT_AND_GIVES_NO_OBSTRUCTION"
            ),
            "dimensions_2_and_3": (
                "POSITIVE_DEFECT_FOR_EVERY_LISTED_MESH_AND_C_MIN_DIVERGES_AS_1_OVER_H"
            ),
            "finite_rows_are_neutral_exact_diagnostics": True,
            "qf2_status": "OPEN_REQUIRES_A_DIFFERENT_OR_RESTRICTED_ROUTE",
            "standard_tensor_Q1_route_status": (
                "REFUTED_FOR_ALL_DISCRETE_PAIRS_IN_D_2_AND_D_3_BY_EXACT_FAMILY"
            ),
        },
        "definitions": {
            "all_pairs_claim_tested": (
                "abs(a_h(u_h,v_h)-a_Q1(I_hu_h,I_hv_h)) "
                "<= C*h*||u_h||_(1,h)*||v_h||_(1,h)"
            ),
            "checkerboard": "v_j=(-1)^(sum_i j_i)",
            "discrete_energy_norm_squared": (
                "||v_h||_(1,h)^2=||v_h||_h^2+a_h(v_h,v_h)"
            ),
            "discrete_free_energy": (
                "a_h(v,v)=h^d*sum_nodes*sum_positive_axes*((v_(j+e_i)-v_j)/h)^2"
            ),
            "discrete_l2_norm_squared": "||v||_h^2=h^d*sum_nodes*v_j^2",
            "grid": "unit_periodic_d_torus_with_h=1/N_and_even_N",
            "minimum_constant_definition": (
                "C_min=defect/(h*||v_h||_(1,h)^2)_for_u_h=v_h=checkerboard"
            ),
            "rational_encoding": "canonical_reduced_p_over_q_strings",
            "tensor_q1_reconstruction": (
                "standard_periodic_nodal_multilinear_interpolant_on_each_cartesian_cell"
            ),
        },
        "dimension_certificates": [
            _dimension_certificate(dimension) for dimension in DIMENSIONS
        ],
        "fixture_grid": {
            "dimensions": list(DIMENSIONS),
            "even_intervals_per_axis": list(EVEN_INTERVALS),
        },
        "rows": rows,
        "schema": SCHEMA,
        "scope": {
            "does_not_refute": [
                "nonstandard_or_frequency_filtered_reconstructions",
                "estimates_restricted_to_smooth_or_resolvent_generated_data",
                "residual_consistency_for_manufactured_smooth_solutions",
                "alternative_flux_reconstructions_or_modified_norms",
                "all_possible_replacements_for_QF2",
            ],
            "refutes_only": (
                "standard_periodic_nodal_tensor_Q1_reconstruction_with_an_O(h)_free_form_"
                "defect_bound_uniform_over_all_discrete_pairs_in_the_discrete_energy_norm"
            ),
        },
        "status": STATUS,
    }


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def _exclusive_write(output: Path, payload: bytes) -> None:
    output = output.resolve()
    if not output.parent.is_dir():
        raise FileNotFoundError(f"output parent does not exist: {output.parent}")
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            output.unlink()
        except FileNotFoundError:
            pass
        raise
    directory_descriptor = os.open(output.parent, os.O_RDONLY)
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="recompute expected bytes/hash and require an exact existing artifact",
    )
    arguments = parser.parse_args()

    try:
        expected = _canonical_bytes(build_fixture())
        expected_sha256 = hashlib.sha256(expected).hexdigest()
        output = arguments.output.resolve()
        if arguments.check:
            if not output.is_file():
                raise FileNotFoundError(f"artifact missing: {output}")
            actual = output.read_bytes()
            if actual != expected:
                raise ValueError(
                    "artifact bytes differ from regenerated canonical fixture: "
                    f"expected_sha256={expected_sha256} "
                    f"actual_sha256={hashlib.sha256(actual).hexdigest()}"
                )
            print(
                "PASS checkerboard_obstruction_v1_check "
                f"sha256={expected_sha256} bytes={len(expected)} "
                "output_not_written=true"
            )
            return 0

        _exclusive_write(output, expected)
        print(
            "PASS checkerboard_obstruction_v1_build "
            f"sha256={expected_sha256} bytes={len(expected)} "
            "no_overwrite=true output_not_reopened=true"
        )
        return 0
    except (AssertionError, FileExistsError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
