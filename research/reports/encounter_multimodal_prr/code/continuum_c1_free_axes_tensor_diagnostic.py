#!/usr/bin/env python3
"""Neutral free-axis and separable-tensor diagnostic for the C1 programme.

This fixture contains no control, killing, reaction-time, root, or topology
payload.  It exercises only the ideal fixed-box rate families stated in the
living C1 candidate: two cell-centred OU axes, a vertex-dual OU axis, and the
base/half-shift periodic free-diffusion axis.  Its tensor check uses one-axis
reductions and scalar products; it never materializes a three-dimensional
array.  Passing this fixture is not a complete-C1 or release promotion.
"""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

import gmpy2
import rate_defined_tensor_f0 as f0

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
OUTPUT = REPORT / "artifacts/data/continuum_c1_free_axes_tensor_diagnostic_v1.json"
SCHEMA = "encounter_continuum_c1_free_axes_tensor_diagnostic_v1"
STATUS = "PASS_NEUTRAL_DIAGNOSTIC_ONLY_COMPLETE_C1_HOLD"
PRECISION_BITS = 256
REFINEMENT_INTERVALS = (16, 32, 64, 128, 256)
PERIODIC_MODE = 3
ENCOUNTER_D = Fraction(2, 5)
OU_GAMMA = Fraction(3, 5)

MIDPOINT_SPEC = {
    "name": "midpoint_ou",
    "lower": Fraction(-3, 2),
    "upper": Fraction(2),
    "diffusion": ENCOUNTER_D / 2,
    "gamma": OU_GAMMA,
    "mean": Fraction(1, 4),
}
RELATIVE_SPEC = {
    "name": "relative_ou",
    "lower": Fraction(-2),
    "upper": Fraction(3, 2),
    "diffusion": Fraction(4, 5),
    "gamma": Fraction(3, 5),
    "mean": Fraction(0),
}
VERTEX_SPEC = {
    "name": "vertex_dual_ou",
    "lower": MIDPOINT_SPEC["lower"],
    "upper": MIDPOINT_SPEC["upper"],
    "diffusion": MIDPOINT_SPEC["diffusion"],
    "gamma": MIDPOINT_SPEC["gamma"],
    "mean": MIDPOINT_SPEC["mean"],
}
PERIODIC_WIDTH = Fraction(5, 2)
PERIODIC_DIFFUSION = Fraction(7, 9)


def _mp(value: Fraction | int) -> gmpy2.mpfr:
    exact = Fraction(value)
    return gmpy2.mpfr(exact.numerator) / gmpy2.mpfr(exact.denominator)


def _float_hex(value: gmpy2.mpfr | float) -> str:
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeError("diagnostic produced a nonfinite binary64 summary")
    if result == 0.0:
        result = 0.0
    return result.hex()


def _fraction_hex(value: Fraction) -> str:
    return float(value).hex()


def _structural_zero(value: gmpy2.mpfr) -> gmpy2.mpfr:
    threshold = gmpy2.mpfr(2) ** (-PRECISION_BITS // 2 + 8)
    return gmpy2.mpfr(0) if abs(value) < threshold else value


def _bernoulli(value: gmpy2.mpfr) -> gmpy2.mpfr:
    return gmpy2.mpfr(1) if value == 0 else value / gmpy2.expm1(value)


def _interval_contains(interval: f0.OutwardInterval, value: gmpy2.mpfr) -> bool:
    return _mp(interval.lower_fraction) <= value <= _mp(interval.upper_fraction)


def _gaussian_moments(
    lower: gmpy2.mpfr,
    upper: gmpy2.mpfr,
    alpha: gmpy2.mpfr,
    maximum_power: int,
) -> list[gmpy2.mpfr]:
    """Return integrals of y^k exp(-alpha*y^2) by exact recurrence."""

    if lower >= upper or alpha <= 0 or maximum_power < 0:
        raise ValueError("invalid Gaussian moment request")
    root = gmpy2.sqrt(alpha)
    moments = [
        gmpy2.sqrt(gmpy2.const_pi())
        * (gmpy2.erf(root * upper) - gmpy2.erf(root * lower))
        / (2 * root)
    ]
    if maximum_power == 0:
        return moments
    moments.append(
        (gmpy2.exp(-alpha * lower**2) - gmpy2.exp(-alpha * upper**2))
        / (2 * alpha)
    )
    for power in range(2, maximum_power + 1):
        boundary = (
            lower ** (power - 1) * gmpy2.exp(-alpha * lower**2)
            - upper ** (power - 1) * gmpy2.exp(-alpha * upper**2)
        ) / (2 * alpha)
        moments.append(boundary + (power - 1) * moments[power - 2] / (2 * alpha))
    return moments


def _polynomial_product(
    left: dict[int, Fraction],
    right: dict[int, Fraction],
) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = result.get(power, Fraction(0)) + (
                left_coefficient * right_coefficient
            )
    return result


def _integrate_x_polynomial(
    coefficients: dict[int, Fraction],
    moments_about_mean: Sequence[gmpy2.mpfr],
    mean: Fraction,
) -> gmpy2.mpfr:
    """Integrate p(x) exp(-alpha*(x-mean)^2) from centred moments."""

    result = gmpy2.mpfr(0)
    for power, coefficient in coefficients.items():
        for centred_power in range(power + 1):
            translated = (
                coefficient
                * math.comb(power, centred_power)
                * mean ** (power - centred_power)
            )
            result += _mp(translated) * moments_about_mean[centred_power]
    return result


def _potential(spec: dict[str, Any], position: Fraction) -> Fraction:
    return (
        spec["gamma"]
        * (position - spec["mean"]) ** 2
        / (2 * spec["diffusion"])
    )


def _smoothstep_value(spec: dict[str, Any], position: Fraction) -> Fraction:
    scaled = (position - spec["lower"]) / (spec["upper"] - spec["lower"])
    return 3 * scaled**2 - 2 * scaled**3


def _smoothstep_derivative_square(spec: dict[str, Any]) -> dict[int, Fraction]:
    width = spec["upper"] - spec["lower"]
    intercept = -spec["lower"] / width
    slope = 1 / width
    derivative = {
        0: 6 * (intercept - intercept**2) / width,
        1: 6 * (slope - 2 * intercept * slope) / width,
        2: -6 * slope**2 / width,
    }
    return _polynomial_product(derivative, derivative)


def _vertex_probe_value(position: Fraction) -> Fraction:
    return 1 + position + position**2 / 4


def _axis_quadratics(
    masses: Sequence[gmpy2.mpfr],
    conductances: Sequence[gmpy2.mpfr],
    values: Sequence[gmpy2.mpfr],
    *,
    periodic: bool,
) -> tuple[gmpy2.mpfr, gmpy2.mpfr]:
    if len(masses) != len(values):
        raise ValueError("axis mass/value length mismatch")
    expected_edges = len(values) if periodic else len(values) - 1
    if len(conductances) != expected_edges:
        raise ValueError("axis conductance length mismatch")
    norm = sum(
        (mass * value**2 for mass, value in zip(masses, values, strict=True)),
        gmpy2.mpfr(0),
    )
    energy = gmpy2.mpfr(0)
    for left, conductance in enumerate(conductances):
        right = (left + 1) % len(values)
        energy += conductance * (values[right] - values[left]) ** 2
    return norm, energy


def _observed_order(coarse: dict[str, Any], fine: dict[str, Any], key: str) -> float:
    coarse_error = float.fromhex(coarse[key])
    fine_error = float.fromhex(fine[key])
    coarse_h = float.fromhex(coarse["h_hex"])
    fine_h = float.fromhex(fine["h_hex"])
    if min(coarse_error, fine_error, coarse_h, fine_h) <= 0:
        raise RuntimeError(f"nonpositive observed-order input for {key}")
    return math.log(coarse_error / fine_error) / math.log(coarse_h / fine_h)


def _reflecting_row(
    spec: dict[str, Any],
    intervals: int,
    *,
    vertex_dual: bool,
) -> dict[str, Any]:
    lower = spec["lower"]
    upper = spec["upper"]
    width = upper - lower
    step_fraction = width / intervals
    alpha_fraction = spec["gamma"] / (2 * spec["diffusion"])
    if vertex_dual:
        positions = tuple(lower + index * step_fraction for index in range(intervals + 1))
        axis = f0.build_reflecting_sg_axis(
            spec["name"],
            positions,
            tuple(_potential(spec, position) for position in positions),
            spec["diffusion"],
            precision_bits=PRECISION_BITS,
        )
    else:
        axis = f0.build_cell_centred_reflecting_sg_axis(
            spec["name"],
            lower,
            upper,
            intervals,
            lambda position: _potential(spec, position),
            spec["diffusion"],
            precision_bits=PRECISION_BITS,
        )

    alpha = _mp(alpha_fraction)
    mean = _mp(spec["mean"])
    full_moments = _gaussian_moments(
        _mp(lower) - mean,
        _mp(upper) - mean,
        alpha,
        6,
    )
    box_mass = full_moments[0]
    raw_masses: list[gmpy2.mpfr] = []
    potentials: list[gmpy2.mpfr] = []
    raw_mass_intervals_contain = True
    for volume, position, interval in zip(
        axis.cell_volumes,
        axis.positions,
        axis.stationary_masses,
        strict=True,
    ):
        potential = _mp(_potential(spec, position))
        raw_mass = _mp(volume) * gmpy2.exp(-potential)
        raw_masses.append(raw_mass)
        potentials.append(potential)
        raw_mass_intervals_contain &= _interval_contains(interval, raw_mass)
    gauge = box_mass / sum(raw_masses, gmpy2.mpfr(0))
    masses = [gauge * mass for mass in raw_masses]

    physical_cell_masses: list[gmpy2.mpfr] = []
    for segments in axis.cell_segments:
        cell_mass = gmpy2.mpfr(0)
        for segment_lower, segment_upper in segments:
            cell_mass += _gaussian_moments(
                _mp(segment_lower) - mean,
                _mp(segment_upper) - mean,
                alpha,
                0,
            )[0]
        physical_cell_masses.append(cell_mass)
    rhos = [
        physical / discrete
        for physical, discrete in zip(physical_cell_masses, masses, strict=True)
    ]

    conductances: list[gmpy2.mpfr] = []
    raw_rate_intervals_contain = True
    raw_conductance_intervals_contain = True
    edge_ratio_errors: list[gmpy2.mpfr] = []
    for left in range(axis.size - 1):
        right = left + 1
        distance_fraction = axis.positions[right] - axis.positions[left]
        distance = _mp(distance_fraction)
        delta = potentials[right] - potentials[left]
        forward_rate = (
            _mp(spec["diffusion"])
            / (_mp(axis.cell_volumes[left]) * distance)
            * _bernoulli(delta)
        )
        backward_rate = (
            _mp(spec["diffusion"])
            / (_mp(axis.cell_volumes[right]) * distance)
            * _bernoulli(-delta)
        )
        raw_rate_intervals_contain &= _interval_contains(
            axis.forward_rates[left], forward_rate
        )
        raw_rate_intervals_contain &= _interval_contains(
            axis.backward_rates[right], backward_rate
        )
        raw_conductance = raw_masses[left] * forward_rate
        raw_conductance_intervals_contain &= _interval_contains(
            axis.stationary_masses[left].multiply_nonnegative(axis.forward_rates[left]),
            raw_conductance,
        )
        raw_conductance_intervals_contain &= _interval_contains(
            axis.stationary_masses[right].multiply_nonnegative(axis.backward_rates[right]),
            raw_conductance,
        )
        conductance = gauge * raw_conductance
        conductances.append(conductance)
        edge_mass = _gaussian_moments(
            _mp(axis.positions[left]) - mean,
            _mp(axis.positions[right]) - mean,
            alpha,
            0,
        )[0]
        interpolant_conductance = _mp(spec["diffusion"]) * edge_mass / distance**2
        edge_ratio_errors.append(abs(conductance / interpolant_conductance - 1))

    if vertex_dual:
        probe_values = [_mp(_vertex_probe_value(position)) for position in axis.positions]
        derivative_square = {0: Fraction(1), 1: Fraction(1), 2: Fraction(1, 4)}
    else:
        probe_values = [_mp(_smoothstep_value(spec, position)) for position in axis.positions]
        derivative_square = _smoothstep_derivative_square(spec)
    probe_norm, probe_energy = _axis_quadratics(
        masses,
        conductances,
        probe_values,
        periodic=False,
    )
    continuum_energy = _mp(spec["diffusion"]) * _integrate_x_polynomial(
        derivative_square,
        full_moments,
        spec["mean"],
    )
    form_relative_error = abs(probe_energy - continuum_energy) / continuum_energy
    map_errors = [abs(rho - 1) for rho in rhos]
    mass_error = _structural_zero(abs(sum(masses, gmpy2.mpfr(0)) - box_mass))
    physical_partition_error = _structural_zero(
        abs(sum(physical_cell_masses, gmpy2.mpfr(0)) - box_mass)
    )
    record: dict[str, Any] = {
        "axis_size": axis.size,
        "box_mass_hex": _float_hex(box_mass),
        "construction": axis.construction,
        "edge_interpolant_ratio_sup_error_hex": _float_hex(max(edge_ratio_errors)),
        "gauge_mass_absolute_error_hex": _float_hex(mass_error),
        "gauge_scale_hex": _float_hex(gauge),
        "h_exact": str(step_fraction),
        "h_hex": _fraction_hex(step_fraction),
        "physical_cell_partition_absolute_error_hex": _float_hex(
            physical_partition_error
        ),
        "probe_continuum_form_hex": _float_hex(continuum_energy),
        "probe_discrete_form_hex": _float_hex(probe_energy),
        "probe_discrete_norm_squared_hex": _float_hex(probe_norm),
        "probe_form_relative_error_hex": _float_hex(form_relative_error),
        "raw_conductance_intervals_contain_formula": raw_conductance_intervals_contain,
        "raw_mass_intervals_contain_formula": raw_mass_intervals_contain,
        "raw_rate_intervals_contain_formula": raw_rate_intervals_contain,
        "rho_sup_error_hex": _float_hex(max(map_errors)),
    }
    if vertex_dual:
        endpoint_error = max(map_errors[0], map_errors[-1])
        interior_error = max(map_errors[1:-1])
        left_reference = (
            _mp(spec["diffusion"])
            / _mp(step_fraction) ** 2
            * _bernoulli(potentials[1] - potentials[0])
        )
        right_reference = (
            _mp(spec["diffusion"])
            / _mp(step_fraction) ** 2
            * _bernoulli(potentials[-2] - potentials[-1])
        )
        left_endpoint_rate = (
            _mp(spec["diffusion"])
            / (_mp(axis.cell_volumes[0]) * _mp(step_fraction))
            * _bernoulli(potentials[1] - potentials[0])
        )
        right_endpoint_rate = (
            _mp(spec["diffusion"])
            / (_mp(axis.cell_volumes[-1]) * _mp(step_fraction))
            * _bernoulli(potentials[-2] - potentials[-1])
        )
        record.update(
            {
                "endpoint_half_volumes_exact": (
                    axis.cell_volumes[0] == step_fraction / 2
                    and axis.cell_volumes[-1] == step_fraction / 2
                    and all(volume == step_fraction for volume in axis.cell_volumes[1:-1])
                ),
                "endpoint_outgoing_rate_factor_left_hex": _float_hex(
                    left_endpoint_rate / left_reference
                ),
                "endpoint_outgoing_rate_factor_right_hex": _float_hex(
                    right_endpoint_rate / right_reference
                ),
                "interior_rho_sup_error_hex": _float_hex(interior_error),
                "endpoint_rho_sup_error_hex": _float_hex(endpoint_error),
            }
        )
    return record


def _reflecting_family(
    spec: dict[str, Any],
    *,
    vertex_dual: bool,
) -> dict[str, Any]:
    rows = [
        _reflecting_row(spec, intervals, vertex_dual=vertex_dual)
        for intervals in REFINEMENT_INTERVALS
    ]
    penultimate, finest = rows[-2:]
    orders = {
        "edge_interpolant_ratio_sup_error": _observed_order(
            penultimate, finest, "edge_interpolant_ratio_sup_error_hex"
        ),
        "probe_form_relative_error": _observed_order(
            penultimate, finest, "probe_form_relative_error_hex"
        ),
        "rho_sup_error": _observed_order(penultimate, finest, "rho_sup_error_hex"),
    }
    if vertex_dual:
        orders.update(
            {
                "endpoint_rho_sup_error": _observed_order(
                    penultimate, finest, "endpoint_rho_sup_error_hex"
                ),
                "interior_rho_sup_error": _observed_order(
                    penultimate, finest, "interior_rho_sup_error_hex"
                ),
            }
        )
    return {
        "alignment": "vertex_dual" if vertex_dual else "cell_centred",
        "expected_orders": {
            "edge_interpolant_ratio_sup_error": 2,
            "probe_form_relative_error": 2,
            "rho_sup_error": 1 if vertex_dual else 2,
        },
        "observed_last_pair_orders": orders,
        "parameters": {
            "diffusion_exact": str(spec["diffusion"]),
            "gamma_exact": str(spec["gamma"]),
            "lower_exact": str(spec["lower"]),
            "mean_exact": str(spec["mean"]),
            "upper_exact": str(spec["upper"]),
        },
        "probe": (
            "u(x)=1+x+x^2/4"
            if vertex_dual
            else "u(x)=3*s(x)^2-2*s(x)^3_with_zero_endpoint_derivatives"
        ),
        "rows": rows,
    }


def _periodic_row(intervals: int, *, half_shift: bool) -> dict[str, Any]:
    axis = f0.build_periodic_diffusion_axis(
        "periodic_half_shift" if half_shift else "periodic_base",
        intervals,
        PERIODIC_WIDTH,
        PERIODIC_DIFFUSION,
        half_cell_shift=half_shift,
    )
    step = PERIODIC_WIDTH / intervals
    mass = step / PERIODIC_WIDTH
    rate = PERIODIC_DIFFUSION / step**2
    conductance = mass * rate
    exact_rate_containment = all(
        interval.contains_fraction(rate)
        for interval in (*axis.forward_rates, *axis.backward_rates)
    )
    raw_mass_containment = all(
        interval.contains_fraction(step) for interval in axis.stationary_masses
    )
    angle_factor = 2 * gmpy2.const_pi() * PERIODIC_MODE / _mp(PERIODIC_WIDTH)
    cosine = [
        gmpy2.cos(angle_factor * _mp(position - axis.domain_start))
        for position in axis.positions
    ]
    sine = [
        gmpy2.sin(angle_factor * _mp(position - axis.domain_start))
        for position in axis.positions
    ]
    masses = [_mp(mass)] * intervals
    conductances = [_mp(conductance)] * intervals
    cosine_norm, cosine_energy = _axis_quadratics(
        masses, conductances, cosine, periodic=True
    )
    sine_norm, sine_energy = _axis_quadratics(
        masses, conductances, sine, periodic=True
    )
    combined_norm = cosine_norm + sine_norm
    combined_energy = cosine_energy + sine_energy
    continuum_energy = _mp(PERIODIC_DIFFUSION) * angle_factor**2
    formula_energy = continuum_energy * (
        gmpy2.sin(gmpy2.const_pi() * PERIODIC_MODE / intervals)
        / (gmpy2.const_pi() * PERIODIC_MODE / intervals)
    ) ** 2
    formula_residual = _structural_zero(abs(combined_energy - formula_energy))
    relative_error = abs(combined_energy - continuum_energy) / continuum_energy
    return {
        "alignment": "half_shift" if half_shift else "base",
        "axis_size": intervals,
        "combined_fourier_continuum_form_hex": _float_hex(continuum_energy),
        "combined_fourier_discrete_form_hex": _float_hex(combined_energy),
        "combined_fourier_norm_squared_hex": _float_hex(combined_norm),
        "conductance_exact": str(conductance),
        "cosine_discrete_form_hex": _float_hex(cosine_energy),
        "cosine_discrete_norm_squared_hex": _float_hex(cosine_norm),
        "fourier_formula_absolute_residual_hex": _float_hex(formula_residual),
        "fourier_relative_error_hex": _float_hex(relative_error),
        "h_exact": str(step),
        "h_hex": _fraction_hex(step),
        "normalized_cell_mass_exact": str(mass),
        "normalized_mass_sum_exact": str(mass * intervals),
        "periodic_rate_exact": str(rate),
        "raw_builder_mass_intervals_contain_h": raw_mass_containment,
        "rate_intervals_contain_formula": exact_rate_containment,
        "wrapped_cell_count": sum(len(segments) == 2 for segments in axis.cell_segments),
    }


def _periodic_family() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for intervals in REFINEMENT_INTERVALS:
        rows.append(_periodic_row(intervals, half_shift=False))
        rows.append(_periodic_row(intervals, half_shift=True))
    base_rows = [row for row in rows if row["alignment"] == "base"]
    half_rows = [row for row in rows if row["alignment"] == "half_shift"]
    translation_gaps = []
    for base, shifted in zip(base_rows, half_rows, strict=True):
        gap = abs(
            float.fromhex(base["combined_fourier_discrete_form_hex"])
            - float.fromhex(shifted["combined_fourier_discrete_form_hex"])
        )
        translation_gaps.append(gap)
    return {
        "expected_fourier_order": 2,
        "fourier_mode": PERIODIC_MODE,
        "observed_last_pair_order": _observed_order(
            base_rows[-2], base_rows[-1], "fourier_relative_error_hex"
        ),
        "rows": rows,
        "translation_energy_gap_max_hex": float(max(translation_gaps)).hex(),
        "width_exact": str(PERIODIC_WIDTH),
        "diffusion_exact": str(PERIODIC_DIFFUSION),
    }


def factorized_tensor_quantities(
    norms: Sequence[Fraction],
    energies: Sequence[Fraction],
) -> tuple[Fraction, Fraction]:
    """Exact separable norm and Kronecker-sum form from axis scalars only."""

    if len(norms) != 3 or len(energies) != 3:
        raise ValueError("three axis norm/form scalars are required")
    norm = norms[0] * norms[1] * norms[2]
    energy = (
        energies[0] * norms[1] * norms[2]
        + norms[0] * energies[1] * norms[2]
        + norms[0] * norms[1] * energies[2]
    )
    return norm, energy


def _streaming_tensor_sentinel() -> dict[str, Any]:
    """Compare factorized and direct scalar streaming sums, with no 3D array."""

    masses = (
        (Fraction(1, 3), Fraction(2, 3)),
        (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)),
        (Fraction(1, 5),) * 5,
    )
    values = (
        (Fraction(1), Fraction(2)),
        (Fraction(2), Fraction(-1), Fraction(3)),
        (Fraction(0), Fraction(1), Fraction(-1), Fraction(2), Fraction(-2)),
    )
    conductances = (
        (Fraction(3, 7),),
        (Fraction(2, 5), Fraction(4, 9)),
        (Fraction(1, 6),) * 5,
    )
    periodic = (False, False, True)
    axis_norms: list[Fraction] = []
    axis_energies: list[Fraction] = []
    for axis in range(3):
        axis_norms.append(
            sum(
                (
                    masses[axis][index] * values[axis][index] ** 2
                    for index in range(len(values[axis]))
                ),
                Fraction(0),
            )
        )
        edge_total = len(values[axis]) if periodic[axis] else len(values[axis]) - 1
        axis_energies.append(
            sum(
                (
                    conductances[axis][left]
                    * (
                        values[axis][(left + 1) % len(values[axis])]
                        - values[axis][left]
                    )
                    ** 2
                    for left in range(edge_total)
                ),
                Fraction(0),
            )
        )
    factorized_norm, factorized_energy = factorized_tensor_quantities(
        axis_norms, axis_energies
    )

    direct_norm = Fraction(0)
    direct_energy = Fraction(0)
    for i in range(len(values[0])):
        for j in range(len(values[1])):
            for k in range(len(values[2])):
                tensor_value = values[0][i] * values[1][j] * values[2][k]
                direct_norm += masses[0][i] * masses[1][j] * masses[2][k] * tensor_value**2
    for left in range(len(values[0]) - 1):
        for j in range(len(values[1])):
            for k in range(len(values[2])):
                jump = (
                    (values[0][left + 1] - values[0][left])
                    * values[1][j]
                    * values[2][k]
                )
                direct_energy += (
                    conductances[0][left] * masses[1][j] * masses[2][k] * jump**2
                )
    for i in range(len(values[0])):
        for left in range(len(values[1]) - 1):
            for k in range(len(values[2])):
                jump = (
                    values[0][i]
                    * (values[1][left + 1] - values[1][left])
                    * values[2][k]
                )
                direct_energy += (
                    masses[0][i] * conductances[1][left] * masses[2][k] * jump**2
                )
    for i in range(len(values[0])):
        for j in range(len(values[1])):
            for left in range(len(values[2])):
                jump = (
                    values[0][i]
                    * values[1][j]
                    * (values[2][(left + 1) % len(values[2])] - values[2][left])
                )
                direct_energy += (
                    masses[0][i] * masses[1][j] * conductances[2][left] * jump**2
                )
    return {
        "axis_energies_exact": [str(value) for value in axis_energies],
        "axis_norms_exact": [str(value) for value in axis_norms],
        "direct_streaming_energy_exact": str(direct_energy),
        "direct_streaming_norm_exact": str(direct_norm),
        "factorized_energy_exact": str(factorized_energy),
        "factorized_norm_exact": str(factorized_norm),
        "full_tensor_values_materialized": False,
        "identity_exact": (
            direct_norm == factorized_norm and direct_energy == factorized_energy
        ),
        "streaming_virtual_cell_count": (
            len(values[0]) * len(values[1]) * len(values[2])
        ),
    }


def _large_tensor_diagnostic(
    midpoint: dict[str, Any],
    relative: dict[str, Any],
    periodic: dict[str, Any],
) -> dict[str, Any]:
    midpoint_row = midpoint["rows"][-1]
    relative_row = relative["rows"][-1]
    periodic_row = [
        row
        for row in periodic["rows"]
        if row["axis_size"] == REFINEMENT_INTERVALS[-1] and row["alignment"] == "base"
    ][0]
    norms = [
        gmpy2.mpfr(float.fromhex(midpoint_row["probe_discrete_norm_squared_hex"])),
        gmpy2.mpfr(float.fromhex(relative_row["probe_discrete_norm_squared_hex"])),
        gmpy2.mpfr(float.fromhex(periodic_row["cosine_discrete_norm_squared_hex"])),
    ]
    energies = [
        gmpy2.mpfr(float.fromhex(midpoint_row["probe_discrete_form_hex"])),
        gmpy2.mpfr(float.fromhex(relative_row["probe_discrete_form_hex"])),
        gmpy2.mpfr(float.fromhex(periodic_row["cosine_discrete_form_hex"])),
    ]
    tensor_norm = norms[0] * norms[1] * norms[2]
    tensor_terms = (
        energies[0] * norms[1] * norms[2],
        norms[0] * energies[1] * norms[2],
        norms[0] * norms[1] * energies[2],
    )
    axis_sizes = (
        midpoint_row["axis_size"],
        relative_row["axis_size"],
        periodic_row["axis_size"],
    )
    return {
        "axis_energy_hex": [_float_hex(value) for value in energies],
        "axis_norm_squared_hex": [_float_hex(value) for value in norms],
        "axis_sizes": list(axis_sizes),
        "factorized_energy_hex": _float_hex(sum(tensor_terms, gmpy2.mpfr(0))),
        "factorized_energy_terms_hex": [_float_hex(value) for value in tensor_terms],
        "factorized_norm_squared_hex": _float_hex(tensor_norm),
        "full_tensor_array_allocated": False,
        "implementation": "one_axis_vectors_then_scalar_product_and_kronecker_sum",
        "largest_live_axis_vector_length": max(axis_sizes),
        "stored_axis_value_count": sum(axis_sizes),
        "virtual_tensor_cell_count": math.prod(axis_sizes),
    }


def build_payload() -> dict[str, Any]:
    with gmpy2.context(gmpy2.get_context(), precision=PRECISION_BITS):
        midpoint = _reflecting_family(MIDPOINT_SPEC, vertex_dual=False)
        relative = _reflecting_family(RELATIVE_SPEC, vertex_dual=False)
        vertex = _reflecting_family(VERTEX_SPEC, vertex_dual=True)
        periodic = _periodic_family()
        large_tensor = _large_tensor_diagnostic(midpoint, relative, periodic)
        streaming = _streaming_tensor_sentinel()
    return {
        "claim_boundary": {
            "control_result_or_scratch_payload_read": False,
            "ideal_fixed_box_free_rates_only": True,
            "neutral_diagnostic_only": True,
            "positive_budget_values_read": False,
            "production_bridge_claimed": False,
            "three_dimensional_array_allocated": False,
        },
        "independent_formulae": {
            "cell_mass_ratio": "rho_i=integral_C_i_exp(-Phi)/m_i",
            "global_axis_gauge": "g_h=integral_I_exp(-Phi)/sum_i(nu_i*exp(-Phi_i))",
            "periodic_conductance": "d_y/(W*h)",
            "periodic_fourier_ratio": "sinc(pi*k/N)^2",
            "reflecting_conductance": "g_h*d*exp(-Phi_i)*B(Phi_j-Phi_i)/h",
            "tensor_energy": "E_z*N_r*N_y+N_z*E_r*N_y+N_z*N_r*E_y",
        },
        "encounter_ou_parameter_relation": {
            "base_D_exact": str(ENCOUNTER_D),
            "midpoint_diffusion_equals_D_over_2": (
                MIDPOINT_SPEC["diffusion"] == ENCOUNTER_D / 2
            ),
            "relative_diffusion_equals_2D": (
                RELATIVE_SPEC["diffusion"] == 2 * ENCOUNTER_D
            ),
            "shared_gamma_exact": str(OU_GAMMA),
        },
        "midpoint_ou": midpoint,
        "periodic": periodic,
        "precision_bits": PRECISION_BITS,
        "promotion_flags": {
            "c1_generalized_mosco_accepted": False,
            "c1_refinement_source_accepted": False,
            "c2_quantitative_error_accepted": False,
            "c3_root_margin_accepted": False,
            "complete_c1": False,
            "prr_release": False,
            "production_rate_bridge_accepted": False,
            "submission_eligible": False,
        },
        "refinement_intervals": list(REFINEMENT_INTERVALS),
        "relative_ou": relative,
        "schema": SCHEMA,
        "status": STATUS,
        "tensor_factorization": {
            "large_axis_only_diagnostic": large_tensor,
            "small_exact_streaming_sentinel": streaming,
        },
        "theory_boundary": {
            "cell_centred_rho_expected_order": 2,
            "complete_c1": "HOLD",
            "finite_tables_are_a_proof": False,
            "periodic_fourier_form_expected_order": 2,
            "smooth_vertex_form_expected_order": 2,
            "vertex_edge_ratio_expected_order": 2,
            "vertex_endpoint_rho_expected_order": 1,
        },
        "vertex_dual_ou": vertex,
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
