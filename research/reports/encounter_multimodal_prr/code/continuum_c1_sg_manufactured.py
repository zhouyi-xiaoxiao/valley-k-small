#!/usr/bin/env python3
"""Neutral fixed-box SG form-convergence fixture for the continuum C1 route.

The fixture uses no catalyst control, killing field, budget propagation, or
reaction-time output.  It compares one cell-centred reflecting OU axis with
closed-form Gaussian-weighted polynomial moments on a fixed box.
"""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import gmpy2
import rate_defined_tensor_f0 as f0

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
OUTPUT = REPORT / "artifacts/data/continuum_c1_sg_manufactured_v2.json"
SCHEMA = "encounter_continuum_c1_sg_manufactured_v2"
STATUS = "PASS_NEUTRAL_SINGLE_AXIS_MAP_FORM_DIAGNOSTIC_ONLY_C1_MOSCO_STILL_OPEN"
PREVIOUS_ARTIFACT_SHA256 = "d5acdad670656cccc974d40f56bac33292a1ae7a462acedb7588eb572147b9cc"
PRECISION_BITS = 256
SIZES = (17, 33, 65, 129, 257, 513, 1025)
FLAT_SENTINEL_SIZES = (4, 8, 16, 32, 64)
LOWER = Fraction.from_float(float.fromhex("-0x1.0000000000000p-2"))
UPPER = Fraction.from_float(float.fromhex("0x1.d99999999999ap+0"))
DIFFUSION = Fraction.from_float(float.fromhex("0x1.0624dd2f1a9fcp-9"))
STIFFNESS = Fraction.from_float(float.fromhex("0x1.999999999999ap-4"))
MEAN = Fraction.from_float(float.fromhex("0x1.e666666666666p-1"))
WIDTH = UPPER - LOWER
NORMALIZED_MEAN_OFFSET = (MEAN - LOWER) / WIDTH
NORMALIZED_SLOPE = 1 / WIDTH

POLYNOMIALS: dict[str, dict[int, Fraction]] = {
    "constant": {0: Fraction(1)},
    "linear": {1: Fraction(1)},
    "quadratic": {2: Fraction(1)},
    "cubic_mixed": {1: Fraction(1), 3: Fraction(1)},
    # 3*s^2-2*s^3 with s=(x-lower)/(upper-lower).  Its derivative
    # vanishes at both reflecting endpoints, unlike the generic H1 probes.
    "neumann_cubic": {
        0: 3 * NORMALIZED_MEAN_OFFSET**2 - 2 * NORMALIZED_MEAN_OFFSET**3,
        1: 6
        * NORMALIZED_MEAN_OFFSET
        * NORMALIZED_SLOPE
        * (1 - NORMALIZED_MEAN_OFFSET),
        2: 3 * NORMALIZED_SLOPE**2 * (1 - 2 * NORMALIZED_MEAN_OFFSET),
        3: -2 * NORMALIZED_SLOPE**3,
    },
}


def _mp(value: Fraction | int) -> gmpy2.mpfr:
    exact = Fraction(value)
    return gmpy2.mpfr(exact.numerator) / gmpy2.mpfr(exact.denominator)


def _fraction_hex(value: Fraction) -> str:
    return float(value).hex()


def _float_hex(value: gmpy2.mpfr) -> str:
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeError("manufactured fixture produced a nonfinite binary64 summary")
    return result.hex()


def _structural_zero(value: gmpy2.mpfr) -> gmpy2.mpfr:
    threshold = gmpy2.mpfr(2) ** (-PRECISION_BITS // 2 + 8)
    return gmpy2.mpfr(0) if abs(value) < threshold else value


def _poly_value(coefficients: dict[int, Fraction], y: gmpy2.mpfr) -> gmpy2.mpfr:
    result = gmpy2.mpfr(0)
    for power, coefficient in coefficients.items():
        result += _mp(coefficient) * y**power
    return result


def _poly_derivative(coefficients: dict[int, Fraction]) -> dict[int, Fraction]:
    return {
        power - 1: coefficient * power
        for power, coefficient in coefficients.items()
        if power > 0
    }


def _poly_product(
    left: dict[int, Fraction],
    right: dict[int, Fraction],
) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = result.get(power, Fraction(0)) + left_coefficient * right_coefficient
    return result


def _gaussian_moments(
    lower_y: gmpy2.mpfr,
    upper_y: gmpy2.mpfr,
    alpha: gmpy2.mpfr,
    maximum_power: int,
) -> list[gmpy2.mpfr]:
    if lower_y >= upper_y or alpha <= 0 or maximum_power < 0:
        raise ValueError("invalid Gaussian moment request")
    root = gmpy2.sqrt(alpha)
    moments = [
        gmpy2.sqrt(gmpy2.const_pi())
        * (gmpy2.erf(root * upper_y) - gmpy2.erf(root * lower_y))
        / (2 * root)
    ]
    if maximum_power == 0:
        return moments
    moments.append(
        (gmpy2.exp(-alpha * lower_y**2) - gmpy2.exp(-alpha * upper_y**2))
        / (2 * alpha)
    )
    for power in range(2, maximum_power + 1):
        boundary = (
            lower_y ** (power - 1) * gmpy2.exp(-alpha * lower_y**2)
            - upper_y ** (power - 1) * gmpy2.exp(-alpha * upper_y**2)
        ) / (2 * alpha)
        moments.append(boundary + gmpy2.mpfr(power - 1) * moments[power - 2] / (2 * alpha))
    return moments


def _integrate_polynomial(
    coefficients: dict[int, Fraction],
    moments: list[gmpy2.mpfr],
) -> gmpy2.mpfr:
    return sum(
        (_mp(coefficient) * moments[power] for power, coefficient in coefficients.items()),
        gmpy2.mpfr(0),
    )


def _bernoulli(value: gmpy2.mpfr) -> gmpy2.mpfr:
    if value == 0:
        return gmpy2.mpfr(1)
    return value / gmpy2.expm1(value)


def _interval_contains(interval: f0.OutwardInterval, value: gmpy2.mpfr) -> bool:
    return _mp(interval.lower_fraction) <= value <= _mp(interval.upper_fraction)


def _interval_centre_mp(interval: f0.OutwardInterval) -> gmpy2.mpfr:
    return _mp(Fraction.from_float(interval.centre()))


def _axis(cells: int) -> f0.TensorAxis:
    alpha = STIFFNESS / DIFFUSION

    def potential_at(position: Fraction) -> Fraction:
        return alpha * (position - MEAN) ** 2

    return f0.build_cell_centred_reflecting_sg_axis(
        "neutral_midpoint",
        LOWER,
        UPPER,
        cells,
        potential_at,
        DIFFUSION / 2,
        precision_bits=PRECISION_BITS,
    )


def _flat_boundary_order_sentinel() -> dict[str, Any]:
    """Exact flat-density sentinel exposing the reflecting boundary O(h) term."""

    rows: list[dict[str, Any]] = []
    for cells in FLAT_SENTINEL_SIZES:
        step = Fraction(2, cells)
        axis = f0.build_cell_centred_reflecting_sg_axis(
            "flat_boundary_order_sentinel",
            Fraction(-1),
            Fraction(1),
            cells,
            lambda _position: Fraction(0),
            Fraction(1),
            precision_bits=PRECISION_BITS,
        )
        expected_positions = tuple(
            Fraction(-1) + (index + Fraction(1, 2)) * step for index in range(cells)
        )
        expected_raw_rate = 1 / step**2
        expected_gauged_mass = step / 2
        expected_gauged_conductance = 1 / (2 * step)
        interval_formulae_contained = all(
            interval.contains_fraction(step) for interval in axis.stationary_masses
        ) and all(
            axis.forward_rates[index].contains_fraction(expected_raw_rate)
            and axis.backward_rates[index + 1].contains_fraction(expected_raw_rate)
            and axis.stationary_masses[index]
            .multiply_nonnegative(axis.forward_rates[index])
            .scale_nonnegative(Fraction(1, 2))
            .contains_fraction(expected_gauged_conductance)
            for index in range(cells - 1)
        )
        geometry_and_reflection_exact = (
            axis.positions == expected_positions
            and axis.cell_volumes == (step,) * cells
            and not axis.periodic
            and axis.backward_rates[0].contains_fraction(0)
            and axis.backward_rates[0].upper_fraction == 0
            and axis.forward_rates[-1].contains_fraction(0)
            and axis.forward_rates[-1].upper_fraction == 0
        )
        continuum_energy = Fraction(1)
        discrete_energy = 1 - step / 2
        energy_gap = step / 2
        continuum_norm_squared = Fraction(1, 3)
        norm_gap = step**2 / 12
        discrete_norm_squared = continuum_norm_squared - norm_gap
        quadratic_continuum_energy = Fraction(4, 3)
        quadratic_discrete_energy = Fraction(4, 3) - 2 * step + Fraction(2, 3) * step**2
        rows.append(
            {
                "cells": cells,
                "continuum_energy_exact": str(continuum_energy),
                "continuum_norm_squared_exact": str(continuum_norm_squared),
                "discrete_energy_exact": str(discrete_energy),
                "discrete_norm_squared_exact": str(discrete_norm_squared),
                "energy_gap_exact": str(energy_gap),
                "energy_gap_hex": float(energy_gap).hex(),
                "gauged_cell_mass_exact": str(expected_gauged_mass),
                "gauged_conductance_exact": str(expected_gauged_conductance),
                "geometry_and_reflection_exact": geometry_and_reflection_exact,
                "h_exact": str(step),
                "h_hex": float(step).hex(),
                "interval_formulae_contained": interval_formulae_contained,
                "norm_gap_exact": str(norm_gap),
                "projection_l2_error_squared_exact": str(norm_gap),
                "quadratic_continuum_energy_exact": str(quadratic_continuum_energy),
                "quadratic_discrete_energy_exact": str(quadratic_discrete_energy),
                "quadratic_energy_gap_exact": str(
                    quadratic_continuum_energy - quadratic_discrete_energy
                ),
                "raw_stationary_mass_sum_exact": "2",
                "stationary_gauge_exact": "1/2",
                "target_box_mass_exact": "1",
            }
        )
    reconstruction_cells = 4
    reconstruction_step = Fraction(2, reconstruction_cells)
    reconstruction_density = Fraction(1, 2)
    reconstruction_diffusion = Fraction(1)
    reconstruction_values = (0, 1, 0, 1)
    reconstruction_jumps = tuple(
        Fraction(reconstruction_values[index + 1] - reconstruction_values[index])
        for index in range(len(reconstruction_values) - 1)
    )
    reconstruction_conductance = (
        reconstruction_diffusion * reconstruction_density / reconstruction_step
    )
    reconstruction_energy = reconstruction_conductance * sum(
        (jump**2 for jump in reconstruction_jumps),
        Fraction(0),
    )
    # On each side of an interior face, |I_h v-J_h v| is a linear ramp over
    # one half cell.  The two exact ramp integrals contribute pi*h*jump^2/12.
    reconstruction_norm_squared = reconstruction_density * reconstruction_step * sum(
        (jump**2 for jump in reconstruction_jumps),
        Fraction(0),
    ) / 12
    if reconstruction_norm_squared != (
        reconstruction_step**2 * reconstruction_energy / (12 * reconstruction_diffusion)
    ):
        raise RuntimeError("interpolant reconstruction sentinel lost its exact identity")

    return {
        "claim": "generic_form_domain_boundary_gap_is_first_order_not_second_order",
        "continuum_density_exact": "1/2",
        "continuum_diffusion_exact": "1",
        "continuum_energy_formula": "E(x)=1",
        "continuum_interval": "[-1,1]",
        "exact_orders_under_uniform_halving": {
            "energy_gap": 1,
            "norm_squared_gap": 2,
            "projection_l2_error": 1,
        },
        "function": "u(x)=x",
        "interpolant_reconstruction_sentinel": {
            "cells": reconstruction_cells,
            "discrete_energy_exact": str(reconstruction_energy),
            "formula": "norm_squared=(h^2/(12*d))*discrete_energy",
            "h_exact": str(reconstruction_step),
            "reconstruction_l2_norm_squared_exact": str(reconstruction_norm_squared),
            "values": list(reconstruction_values),
        },
        "quadratic_function": "u(x)=x^2",
        "quadratic_formula": "E_h=4/3-2*h+(2/3)*h^2",
        "rows": rows,
        "sizes": list(FLAT_SENTINEL_SIZES),
    }


def _row(cells: int) -> dict[str, Any]:
    axis = _axis(cells)
    alpha = _mp(STIFFNESS / DIFFUSION)
    diffusion_axis = _mp(DIFFUSION / 2)
    mean = _mp(MEAN)
    lower = _mp(LOWER)
    upper = _mp(UPPER)
    step = _mp((UPPER - LOWER) / cells)
    normalization = gmpy2.sqrt(alpha / gmpy2.const_pi())
    full_moments = _gaussian_moments(lower - mean, upper - mean, alpha, 6)
    box_mass = normalization * full_moments[0]

    raw_masses: list[gmpy2.mpfr] = []
    potentials: list[gmpy2.mpfr] = []
    raw_stationary_containment = True
    for index, position in enumerate(axis.positions):
        potential = alpha * (_mp(position) - mean) ** 2
        raw_mass = step * gmpy2.exp(-potential)
        potentials.append(potential)
        raw_masses.append(raw_mass)
        raw_stationary_containment &= _interval_contains(
            axis.stationary_masses[index],
            raw_mass,
        )
    gauge = box_mass / sum(raw_masses, gmpy2.mpfr(0))
    discrete_masses = [gauge * mass for mass in raw_masses]
    gauged_stationary_containment = all(
        _interval_contains(interval, mass)
        for interval, mass in zip(
            axis.stationary_masses,
            discrete_masses,
            strict=True,
        )
    )

    conductances: list[gmpy2.mpfr] = []
    raw_conductance_containment = True
    gauged_conductance_containment = True
    for left in range(cells - 1):
        delta = potentials[left + 1] - potentials[left]
        forward_rate = diffusion_axis / step**2 * _bernoulli(delta)
        backward_rate = diffusion_axis / step**2 * _bernoulli(-delta)
        conductance = raw_masses[left] * forward_rate
        reverse_conductance = raw_masses[left + 1] * backward_rate
        if abs(conductance - reverse_conductance) > gmpy2.mpfr("1e-70"):
            raise RuntimeError("independent SG conductance lost detailed balance")
        left_interval = axis.stationary_masses[left].multiply_nonnegative(
            axis.forward_rates[left]
        )
        right_interval = axis.stationary_masses[left + 1].multiply_nonnegative(
            axis.backward_rates[left + 1]
        )
        gauged_conductance = gauge * conductance
        raw_conductance_containment &= _interval_contains(left_interval, conductance)
        raw_conductance_containment &= _interval_contains(right_interval, conductance)
        gauged_conductance_containment &= _interval_contains(
            left_interval,
            gauged_conductance,
        )
        gauged_conductance_containment &= _interval_contains(
            right_interval,
            gauged_conductance,
        )
        conductances.append(gauged_conductance)

    cell_masses: list[gmpy2.mpfr] = []
    cell_moments: list[list[gmpy2.mpfr]] = []
    density_ratio_min = gmpy2.mpfr("inf")
    density_ratio_max = gmpy2.mpfr(0)
    for index, segments in enumerate(axis.cell_segments):
        if len(segments) != 1:
            raise RuntimeError("reflecting cell-centred fixture has a wrapped cell")
        cell_lower, cell_upper = segments[0]
        local = _gaussian_moments(
            _mp(cell_lower) - mean,
            _mp(cell_upper) - mean,
            alpha,
            6,
        )
        cell_moments.append(local)
        cell_mass = normalization * local[0]
        cell_masses.append(cell_mass)
        probe_points = [_mp(cell_lower), _mp(cell_upper)]
        if cell_lower <= MEAN <= cell_upper:
            probe_points.append(mean)
        discrete_density = discrete_masses[index] / step
        for point in probe_points:
            continuum_density = normalization * gmpy2.exp(-alpha * (point - mean) ** 2)
            ratio = discrete_density / continuum_density
            density_ratio_min = min(density_ratio_min, ratio)
            density_ratio_max = max(density_ratio_max, ratio)

    cell_mass_ratios = [
        discrete_mass / cell_mass
        for discrete_mass, cell_mass in zip(discrete_masses, cell_masses, strict=True)
    ]
    adjoint_map_ratios = [1 / ratio for ratio in cell_mass_ratios]
    cell_mass_ratio_min = min(cell_mass_ratios)
    cell_mass_ratio_max = max(cell_mass_ratios)
    adjoint_map_ratio_min = min(adjoint_map_ratios)
    adjoint_map_ratio_max = max(adjoint_map_ratios)

    edge_interpolant_ratios: list[gmpy2.mpfr] = []
    for left, conductance in enumerate(conductances):
        continuum_edge_mass = normalization * _gaussian_moments(
            _mp(axis.positions[left]) - mean,
            _mp(axis.positions[left + 1]) - mean,
            alpha,
            0,
        )[0]
        continuum_interpolant_conductance = (
            diffusion_axis * continuum_edge_mass / step**2
        )
        edge_interpolant_ratios.append(conductance / continuum_interpolant_conductance)
    edge_interpolant_ratio_min = min(edge_interpolant_ratios)
    edge_interpolant_ratio_max = max(edge_interpolant_ratios)

    centre_masses = [_interval_centre_mp(interval) for interval in axis.stationary_masses]
    centre_forward = [_interval_centre_mp(interval) for interval in axis.forward_rates]
    centre_backward = [_interval_centre_mp(interval) for interval in axis.backward_rates]
    centre_balance_residuals: list[gmpy2.mpfr] = []
    recursive_reversible_masses = [centre_masses[0]]
    for left in range(cells - 1):
        lhs = centre_masses[left] * centre_forward[left]
        rhs = centre_masses[left + 1] * centre_backward[left + 1]
        centre_balance_residuals.append(abs(lhs - rhs) / max(abs(lhs), abs(rhs)))
        recursive_reversible_masses.append(
            recursive_reversible_masses[-1]
            * centre_forward[left]
            / centre_backward[left + 1]
        )
    centre_shape_ratios = [
        (recursive / recursive_reversible_masses[0]) / (mass / centre_masses[0])
        for recursive, mass in zip(
            recursive_reversible_masses,
            centre_masses,
            strict=True,
        )
    ]
    centre_shape_drift = max(abs(ratio - 1) for ratio in centre_shape_ratios)

    functions: dict[str, dict[str, str]] = {}
    for name, polynomial in POLYNOMIALS.items():
        square = _poly_product(polynomial, polynomial)
        derivative_square = _poly_product(
            _poly_derivative(polynomial),
            _poly_derivative(polynomial),
        )
        continuum_norm = normalization * _integrate_polynomial(square, full_moments)
        continuum_energy = (
            diffusion_axis * normalization * _integrate_polynomial(derivative_square, full_moments)
        )
        averages: list[gmpy2.mpfr] = []
        projected_continuum_norm = gmpy2.mpfr(0)
        for local, cell_mass in zip(cell_moments, cell_masses, strict=True):
            average = _integrate_polynomial(polynomial, local) / local[0]
            averages.append(average)
            projected_continuum_norm += cell_mass * average**2
        discrete_norm = sum(
            (mass * average**2 for mass, average in zip(discrete_masses, averages, strict=True)),
            gmpy2.mpfr(0),
        )
        discrete_energy = sum(
            (
                conductances[index] * (averages[index + 1] - averages[index]) ** 2
                for index in range(cells - 1)
            ),
            gmpy2.mpfr(0),
        )
        energy_error = _structural_zero(abs(discrete_energy - continuum_energy))
        projection_error_squared = max(
            gmpy2.mpfr(0),
            continuum_norm - projected_continuum_norm,
        )
        projection_error_squared = _structural_zero(projection_error_squared)
        norm_identification_error = _structural_zero(
            abs(discrete_norm - projected_continuum_norm)
        )
        relative_energy_error = (
            gmpy2.mpfr(0)
            if continuum_energy == 0
            else energy_error / abs(continuum_energy)
        )
        functions[name] = {
            "continuum_energy_hex": _float_hex(continuum_energy),
            "continuum_norm_squared_hex": _float_hex(continuum_norm),
            "discrete_energy_hex": _float_hex(discrete_energy),
            "discrete_norm_squared_hex": _float_hex(discrete_norm),
            "energy_absolute_error_hex": _float_hex(energy_error),
            "energy_relative_error_hex": _float_hex(relative_energy_error),
            "norm_identification_absolute_error_hex": _float_hex(norm_identification_error),
            "projection_l2_error_hex": _float_hex(gmpy2.sqrt(projection_error_squared)),
        }

    mass_error = _structural_zero(abs(sum(discrete_masses, gmpy2.mpfr(0)) - box_mass))
    return {
        "adjoint_map_ratio_max_hex": _float_hex(adjoint_map_ratio_max),
        "adjoint_map_ratio_min_hex": _float_hex(adjoint_map_ratio_min),
        "adjoint_map_ratio_sup_error_hex": _float_hex(
            max(abs(adjoint_map_ratio_min - 1), abs(adjoint_map_ratio_max - 1))
        ),
        "box_mass_hex": _float_hex(box_mass),
        "cell_mass_ratio_max_hex": _float_hex(cell_mass_ratio_max),
        "cell_mass_ratio_min_hex": _float_hex(cell_mass_ratio_min),
        "cell_mass_ratio_sup_error_hex": _float_hex(
            max(abs(cell_mass_ratio_min - 1), abs(cell_mass_ratio_max - 1))
        ),
        "cells": cells,
        "gauged_conductance_interval_containment": gauged_conductance_containment,
        "gauged_stationary_mass_interval_containment": gauged_stationary_containment,
        "density_ratio_max_hex": _float_hex(density_ratio_max),
        "density_ratio_min_hex": _float_hex(density_ratio_min),
        "density_ratio_sup_error_hex": _float_hex(
            max(abs(density_ratio_min - 1), abs(density_ratio_max - 1))
        ),
        "functions": functions,
        "gauge_mass_absolute_error_hex": _float_hex(mass_error),
        "gauge_scale_hex": _float_hex(gauge),
        "h_hex": _fraction_hex((UPPER - LOWER) / cells),
        "ideal_edge_interpolant_ratio_max_hex": _float_hex(edge_interpolant_ratio_max),
        "ideal_edge_interpolant_ratio_min_hex": _float_hex(edge_interpolant_ratio_min),
        "ideal_edge_interpolant_ratio_sup_error_hex": _float_hex(
            max(
                abs(edge_interpolant_ratio_min - 1),
                abs(edge_interpolant_ratio_max - 1),
            )
        ),
        "production_centre_balance_max_relative_residual_hex": _float_hex(
            max(centre_balance_residuals)
        ),
        "production_centre_recursive_mass_shape_drift_hex": _float_hex(
            centre_shape_drift
        ),
        "raw_conductance_interval_containment": raw_conductance_containment,
        "raw_stationary_mass_interval_containment": raw_stationary_containment,
    }


def _observed_order(
    coarse: dict[str, Any],
    fine: dict[str, Any],
    key: str,
) -> float | None:
    coarse_error = float.fromhex(coarse[key])
    fine_error = float.fromhex(fine[key])
    coarse_h = float.fromhex(coarse["h_hex"])
    fine_h = float.fromhex(fine["h_hex"])
    if coarse_error == 0 and fine_error == 0:
        return None
    if min(coarse_error, fine_error, coarse_h, fine_h) <= 0:
        raise RuntimeError("observed-order input has an isolated nonpositive error")
    return math.log(coarse_error / fine_error) / math.log(coarse_h / fine_h)


def build_payload() -> dict[str, Any]:
    with gmpy2.context(gmpy2.get_context(), precision=PRECISION_BITS):
        rows = [_row(cells) for cells in SIZES]
        alpha = _mp(STIFFNESS / DIFFUSION)
        normalization = gmpy2.sqrt(alpha / gmpy2.const_pi())
        endpoint_density_lower = normalization * gmpy2.exp(
            -alpha * (_mp(LOWER) - _mp(MEAN)) ** 2
        )
        endpoint_density_upper = normalization * gmpy2.exp(
            -alpha * (_mp(UPPER) - _mp(MEAN)) ** 2
        )
        generic_linear_boundary_coefficient = (
            _mp(DIFFUSION / 2)
            * (endpoint_density_lower + endpoint_density_upper)
            / 2
        )
    finest = rows[-1]
    penultimate = rows[-2]
    orders: dict[str, Any] = {
        "adjoint_map_ratio_sup_error": _observed_order(
            penultimate,
            finest,
            "adjoint_map_ratio_sup_error_hex",
        ),
        "cell_mass_ratio_sup_error": _observed_order(
            penultimate,
            finest,
            "cell_mass_ratio_sup_error_hex",
        ),
        "density_ratio_sup_error": _observed_order(
            penultimate,
            finest,
            "density_ratio_sup_error_hex",
        ),
        "functions": {},
        "ideal_edge_interpolant_ratio_sup_error": _observed_order(
            penultimate,
            finest,
            "ideal_edge_interpolant_ratio_sup_error_hex",
        ),
    }
    for name in POLYNOMIALS:
        coarse_record = {"h_hex": penultimate["h_hex"], **penultimate["functions"][name]}
        fine_record = {"h_hex": finest["h_hex"], **finest["functions"][name]}
        orders["functions"][name] = {
            "energy_absolute_error": _observed_order(
                coarse_record,
                fine_record,
                "energy_absolute_error_hex",
            ),
            "norm_identification_absolute_error": _observed_order(
                coarse_record,
                fine_record,
                "norm_identification_absolute_error_hex",
            ),
            "projection_l2_error": _observed_order(
                coarse_record,
                fine_record,
                "projection_l2_error_hex",
            ),
        }
    return {
        "alignment_scope": {
            "axis": "midpoint_z",
            "one_dimensional_rule": "cell_centred_reflecting_scharfetter_gummel",
            "periodic_axis_tested": False,
            "tensor_alignment_vector_frozen": False,
            "vertex_dual_tested": False,
        },
        "claim_boundary": {
            "c1_mosco_proved": False,
            "c2_error_bound_proved": False,
            "control_or_budget_read": False,
            "fixed_1d_free_ideal_mosco_proved": False,
            "ideal_analytic_scheme_only": True,
            "manufactured_fixture_only": True,
            "positive_budget_scientific_values_read": False,
            "production_centre_mosco_proved": False,
            "release_eligible": False,
        },
        "fixed_box": {
            "endpoint_density_lower_hex": _float_hex(endpoint_density_lower),
            "endpoint_density_upper_hex": _float_hex(endpoint_density_upper),
            "generic_linear_boundary_coefficient_hex": _float_hex(
                generic_linear_boundary_coefficient
            ),
            "lower_exact": str(LOWER),
            "lower_hex": _fraction_hex(LOWER),
            "upper_exact": str(UPPER),
            "upper_hex": _fraction_hex(UPPER),
        },
        "flat_boundary_order_sentinel": _flat_boundary_order_sentinel(),
        "fixture_projection_map": {
            "A_h_J_h_exact_for_piecewise_constants": True,
            "c1_contract_map_choice_closed": False,
            "denominator": "integral_C_i_pi",
            "formula": "A_h[u]_i=(integral_C_i u*pi)/(integral_C_i pi)",
            "weighted_adjoint_exact": False,
            "weighted_adjoint_error_controlled_by_cell_mass_ratio": True,
        },
        "independent_formulae": {
            "adjoint_map_ratio": "rho_i=(integral_C_i_pi)/m_i",
            "cell_projection": "pi_weighted_exact_Gaussian_polynomial_cell_average",
            "conductance": "gauge*h*exp(-U_i)*(D_axis/h^2)*Bernoulli(U_j-U_i)",
            "continuum_energy": "integral_(fixed_box) D_axis*(u_prime)^2*pi",
            "continuum_moments": "closed_form_erf_plus_Gaussian_recurrence",
            "density_ratio_cell_extrema": "both_cell_endpoints_plus_interior_OU_mean_if_present",
            "interpolant_edge_conductance": "D_axis*h^-2*integral_between_adjacent_centres_pi",
            "potential": "U(z)=gamma*(z-zbar)^2/D",
            "stationary_gauge": "sum_i_pi_h_i=integral_(fixed_box)_pi",
        },
        "observed_last_pair_orders": orders,
        "parameters": {
            "D_exact": str(DIFFUSION),
            "D_hex": _fraction_hex(DIFFUSION),
            "D_axis_exact": str(DIFFUSION / 2),
            "gamma_exact": str(STIFFNESS),
            "gamma_hex": _fraction_hex(STIFFNESS),
            "zbar_exact": str(MEAN),
            "zbar_hex": _fraction_hex(MEAN),
        },
        "previous_artifact": {
            "path": "artifacts/data/continuum_c1_sg_manufactured_v1.json",
            "sha256": PREVIOUS_ARTIFACT_SHA256,
        },
        "precision_bits": PRECISION_BITS,
        "rows": rows,
        "schema": SCHEMA,
        "scheme_boundary": {
            "gauged_ideal_form_values_contained_in_production_outward_intervals": False,
            "ideal_analytic_common_conductance_used_for_form": True,
            "production_gauge_linkage_proved": False,
            "production_binary64_centres_exactly_reversible": False,
            "production_centre_limit_claimed": False,
            "production_interval_width_belongs_to": "E_eval_not_Mosco_form",
            "raw_ungauged_axis_values_contained_in_production_outward_intervals": True,
        },
        "sizes": list(SIZES),
        "status": STATUS,
        "theorem_map_candidate": {
            "P_h_J_h_formula": "diag(rho_i)",
            "c1_contract_adoption_complete": False,
            "exact_adjoint": True,
            "formula": "P_h_adj[u]_i=(integral_C_i u*pi)/m_i",
            "J_h_P_h_pointwise_strong_not_operator_norm": True,
            "physical_cell_mass_preserved": True,
            "proposed_not_independently_accepted": True,
        },
        "theory_boundary": {
            "complete_c1_from_finite_tables": False,
            "form_domain": "weighted_H1_no_Neumann_trace_constraint",
            "generic_smooth_energy_asymptotic": "O(h)_from_two_missing_boundary_half_cells",
            "J_h_P_h_operator_norm_convergence_claimed": False,
            "neumann_compatible_energy_asymptotic": "O(h^2)_when_both_endpoint_derivatives_vanish",
            "production_box_observed_order_warning": "tiny_endpoint_density_masks_generic_O(h)_term_on_accessible_meshes",
        },
    }


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")


def main() -> None:
    payload = build_payload()
    raw = canonical_json_bytes(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(raw)
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(REPORT)),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "status": payload["status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
