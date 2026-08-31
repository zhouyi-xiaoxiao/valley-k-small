#!/usr/bin/env python3
"""Fail-closed GIG screening pilot for a future multimodal encounter paper.

The calculation in this module is deliberately limited to normalized
free-space GIG channel laws

    g(t) = Z^-1 t^-p exp(-a/t-bt),  t > 0.

It validates two mathematical screening fixtures:

* a three-channel, two-control cusp candidate for ``d=2``; and
* an explicit well-separated construction with two through six modes.

This is not a bounded-domain, finite-radius, continuum Doi/Robin, or physical
catalyst-realizability calculation.  The generated JSON repeats that boundary
so it cannot be mistaken for the later continuum campaign.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq, root
from scipy.special import kve, logsumexp

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_OUTPUT = REPORT / "artifacts" / "data" / "gig_constructive_pilot.json"

CLAIM_SCOPE = (
    "normalized free-space GIG channel screening only; not bounded-domain, "
    "finite-radius, continuum Doi/Robin, or physical catalyst-realizability "
    "evidence"
)

SCHEMA_VERSION = 2
SCAN_POINTS = 120_000

# Fail-closed thresholds.  They are intentionally much weaker than the
# observed margins but strong enough to catch lost roots and degeneracies.
NORMALIZATION_TOL = 2.0e-10
DERIVATIVE_CROSSCHECK_TOL = 2.0e-10
CUSP_RESIDUAL_TOL = 1.0e-10
CUSP_REFERENCE_TOL = 2.0e-9
CUSP_MIN_WEIGHT = 5.0e-2
CUSP_MIN_ABS_SCALED_FOURTH = 1.0e-2
CUSP_MIN_ROW_ANGLE_SINE = 1.0e-1
CUSP_MIN_SINGULAR_VALUE_RATIO = 1.0e-1
CUSP_INVARIANT_REFERENCE_TOL = 2.0e-8
ROOT_RESIDUAL_TOL = 1.0e-7
MIN_DIMENSIONLESS_CURVATURE = 1.0e-1
MIN_PROMINENCE_RATIO = 1.5
MIN_LOG_ROOT_SPACING = 2.0e-1
MIN_INFLECTION_SCORE_MARGIN = 1.0e-1
MAX_WEIGHT_DYNAMIC_RANGE = 1.0e5
WEIGHT_SUM_TOL = 2.0e-13
ISOLATED_MODE_RESIDUAL_TOL = 2.0e-13

CUSP_P = 2.5  # p=(d+3)/2 for d=2 narrow-patch screening
CUSP_B = 0.01
CUSP_TARGET_MODES = np.asarray((0.35, 1.0, 1.5), dtype=float)
CUSP_INITIAL_GUESS = np.asarray((0.573, 0.277, 0.320), dtype=float)
CUSP_REFERENCE = np.asarray(
    (
        0.5728883706366298,
        0.2769343322238386,
        0.3200588141402115,
    ),
    dtype=float,
)
CUSP_REFERENCE_SCALED_FOURTH = -13.61053628261525
CUSP_REFERENCE_ROW_ANGLE_SINE = 0.9632674238749193

# The previously implemented b=0.1 solution is retained only as a robustness
# fixture.  It must never replace the b=0.01 canonical preliminary result.
ROBUSTNESS_CUSP_B = 0.1
ROBUSTNESS_CUSP_INITIAL_GUESS = np.asarray((0.57, 0.30, 0.35), dtype=float)
ROBUSTNESS_CUSP_REFERENCE = np.asarray(
    (
        0.56884271249279217,
        0.30103661599989961,
        0.35453314478013609,
    ),
    dtype=float,
)
ROBUSTNESS_CUSP_REFERENCE_SCALED_FOURTH = -14.289015686061406
ROBUSTNESS_CUSP_REFERENCE_ROW_ANGLE_SINE = 0.9806334944999429

CONSTRUCTION_P = 2.5
CONSTRUCTION_B = 0.01
CONSTRUCTION_MODE_COUNTS = tuple(range(2, 7))
CONSTRUCTION_SEPARATION_FACTOR = 10.0


@dataclass(frozen=True)
class GIGSpecification:
    """A normalized finite mixture of GIG screening channels."""

    p: float
    b: float
    target_modes: np.ndarray
    actions: np.ndarray
    weights: np.ndarray
    log_normalizers: np.ndarray

    @property
    def log_weights(self) -> np.ndarray:
        return np.log(self.weights)


def gig_log_normalization(
    actions: Sequence[float] | np.ndarray,
    *,
    b: float,
    p: float,
) -> np.ndarray:
    """Return stable logarithms of the normalized GIG channel constants."""

    action = np.asarray(actions, dtype=float).reshape(-1)
    if action.size == 0 or np.any(~np.isfinite(action)) or np.any(action <= 0.0):
        raise ValueError("actions must be a non-empty finite positive array")
    if not np.isfinite(b) or b <= 0.0:
        raise ValueError("b must be finite and positive")
    if not np.isfinite(p):
        raise ValueError("p must be finite")

    argument = 2.0 * np.sqrt(action * b)
    scaled_bessel = np.asarray(kve(1.0 - p, argument), dtype=float)
    if np.any(~np.isfinite(scaled_bessel)) or np.any(scaled_bessel <= 0.0):
        raise FloatingPointError("scaled Bessel K evaluation failed")
    result = (
        math.log(2.0)
        + 0.5 * (1.0 - p) * (np.log(action) - math.log(b))
        + np.log(scaled_bessel)
        - argument
    )
    if np.any(~np.isfinite(result)):
        raise FloatingPointError("GIG log normalizer is non-finite")
    return result


def _derivative_ratio_tensor(
    times: Sequence[float] | np.ndarray,
    actions: Sequence[float] | np.ndarray,
    *,
    b: float,
    p: float,
) -> np.ndarray:
    """Return ``g^(n)/g`` for ``n=0,...,4``.

    The recurrence ``P[n+1] = P[n]' + ell' P[n]`` for
    ``g=exp(ell)`` gives the explicit complete-Bell-polynomial expressions
    below.  Evaluating the ratios before multiplying by a density avoids
    underflow in the well-separated construction.
    """

    t = np.asarray(times, dtype=float).reshape(1, -1)
    action = np.asarray(actions, dtype=float).reshape(-1, 1)
    if t.size == 0 or np.any(~np.isfinite(t)) or np.any(t <= 0.0):
        raise ValueError("times must be a non-empty finite positive array")

    ell1 = action / t**2 - p / t - b
    ell2 = -2.0 * action / t**3 + p / t**2
    ell3 = 6.0 * action / t**4 - 2.0 * p / t**3
    ell4 = -24.0 * action / t**5 + 6.0 * p / t**4

    result = np.stack(
        (
            np.ones_like(ell1),
            ell1,
            ell1**2 + ell2,
            ell1**3 + 3.0 * ell1 * ell2 + ell3,
            ell1**4 + 6.0 * ell1**2 * ell2 + 3.0 * ell2**2 + 4.0 * ell1 * ell3 + ell4,
        ),
        axis=0,
    )
    if np.any(~np.isfinite(result)):
        raise FloatingPointError("analytic derivative ratios became non-finite")
    return result


def channel_derivatives(
    time: float,
    actions: Sequence[float] | np.ndarray,
    *,
    b: float,
    p: float,
    log_normalizers: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """Return normalized channel derivatives through fourth order.

    The result has shape ``(channel_count, 5)`` with columns
    ``g, g', g'', g''', g''''``.
    """

    t = float(time)
    if not np.isfinite(t) or t <= 0.0:
        raise ValueError("time must be finite and positive")
    action = np.asarray(actions, dtype=float).reshape(-1)
    log_z = (
        gig_log_normalization(action, b=b, p=p)
        if log_normalizers is None
        else np.asarray(log_normalizers, dtype=float).reshape(-1)
    )
    if log_z.shape != action.shape or np.any(~np.isfinite(log_z)):
        raise ValueError("log normalizers must match actions and be finite")

    log_density = -log_z - p * math.log(t) - action / t - b * t
    density = np.exp(log_density)
    ratios = _derivative_ratio_tensor((t,), action, b=b, p=p)[:, :, 0].T
    result = density[:, None] * ratios
    if np.any(~np.isfinite(result)):
        raise FloatingPointError("channel derivatives became non-finite")
    return result


def _cauchy_channel_derivatives(
    time: float,
    actions: Sequence[float] | np.ndarray,
    *,
    b: float,
    p: float,
    log_normalizers: Sequence[float] | np.ndarray,
    circle_fraction: float = 0.3,
    points: int = 256,
) -> np.ndarray:
    """Independently recover derivatives with the Cauchy integral formula."""

    t = float(time)
    if not (0.0 < circle_fraction < 1.0):
        raise ValueError("circle_fraction must lie in (0, 1)")
    if int(points) != points or points < 32:
        raise ValueError("points must be an integer of at least 32")
    action = np.asarray(actions, dtype=float).reshape(-1)
    log_z = np.asarray(log_normalizers, dtype=float).reshape(-1)
    theta = 2.0 * np.pi * np.arange(points, dtype=float) / points
    radius = circle_fraction * t
    z = t + radius * np.exp(1j * theta)
    values = np.exp(
        -log_z[:, None] - p * np.log(z)[None, :] - action[:, None] / z[None, :] - b * z[None, :]
    )
    derivatives = np.empty((action.size, 5), dtype=complex)
    for order in range(5):
        coefficient = np.mean(
            values * np.exp(-1j * order * theta)[None, :],
            axis=1,
        )
        derivatives[:, order] = math.factorial(order) * coefficient / radius**order
    return derivatives


def make_gig_specification(
    target_modes: Sequence[float] | np.ndarray,
    *,
    b: float,
    p: float,
    weights: Sequence[float] | np.ndarray | None = None,
) -> GIGSpecification:
    """Construct normalized channels with prescribed isolated modes.

    ``a_j=b*m_j^2+p*m_j`` makes the isolated mode exactly ``m_j``.  If
    weights are omitted, inverse isolated peak heights balance the weighted
    isolated maxima without a numerical optimizer.
    """

    modes = np.asarray(target_modes, dtype=float).reshape(-1)
    if modes.size == 0 or np.any(~np.isfinite(modes)) or np.any(modes <= 0.0):
        raise ValueError("target modes must be a non-empty finite positive array")
    if np.any(np.diff(modes) <= 0.0):
        raise ValueError("target modes must be strictly increasing")
    actions = b * modes**2 + p * modes
    log_z = gig_log_normalization(actions, b=b, p=p)

    if weights is None:
        log_isolated_heights = -log_z - p * np.log(modes) - actions / modes - b * modes
        log_inverse_heights = -log_isolated_heights
        normalized_log_weights = log_inverse_heights - logsumexp(log_inverse_heights)
        mixture_weights = np.exp(normalized_log_weights)
    else:
        mixture_weights = np.asarray(weights, dtype=float).reshape(-1)
        if mixture_weights.shape != modes.shape:
            raise ValueError("weights must match target modes")
        if np.any(~np.isfinite(mixture_weights)) or np.any(mixture_weights <= 0.0):
            raise ValueError("weights must be finite and strictly positive")
        mixture_weights = mixture_weights / mixture_weights.sum()

    return GIGSpecification(
        p=float(p),
        b=float(b),
        target_modes=modes,
        actions=actions,
        weights=mixture_weights,
        log_normalizers=log_z,
    )


def mixture_profile(
    times: Sequence[float] | np.ndarray,
    spec: GIGSpecification,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return log density, derivative ratios through order four, and shares."""

    t = np.asarray(times, dtype=float).reshape(-1)
    ratios_by_channel = _derivative_ratio_tensor(
        t,
        spec.actions,
        b=spec.b,
        p=spec.p,
    )
    log_components = (
        spec.log_weights[:, None]
        - spec.log_normalizers[:, None]
        - spec.p * np.log(t)[None, :]
        - spec.actions[:, None] / t[None, :]
        - spec.b * t[None, :]
    )
    log_total = logsumexp(log_components, axis=0)
    shares = np.exp(log_components - log_total[None, :])
    mixture_ratios = np.einsum(
        "it,nit->nt",
        shares,
        ratios_by_channel,
        optimize=True,
    )
    if (
        np.any(~np.isfinite(log_total))
        or np.any(~np.isfinite(shares))
        or np.any(~np.isfinite(mixture_ratios))
    ):
        raise FloatingPointError("mixture profile became non-finite")
    return log_total, mixture_ratios, shares


def _normalization_audit(spec: GIGSpecification) -> dict[str, Any]:
    integrals: list[float] = []
    errors: list[float] = []
    for action, log_z in zip(
        spec.actions,
        spec.log_normalizers,
        strict=True,
    ):
        integral, integration_error = quad(
            lambda value: math.exp(
                -float(log_z) - spec.p * math.log(value) - float(action) / value - spec.b * value
            ),
            0.0,
            np.inf,
            epsabs=1.0e-12,
            epsrel=1.0e-12,
            limit=500,
        )
        integrals.append(float(integral))
        errors.append(float(integration_error))
    max_error = max(abs(value - 1.0) for value in integrals)
    return {
        "integrals": integrals,
        "reported_quadrature_errors": errors,
        "maximum_absolute_normalization_error": max_error,
        "threshold": NORMALIZATION_TOL,
        "passed": bool(max_error <= NORMALIZATION_TOL),
    }


def _derivative_crosscheck(spec: GIGSpecification) -> dict[str, Any]:
    time = 0.7
    analytic = channel_derivatives(
        time,
        spec.actions,
        b=spec.b,
        p=spec.p,
        log_normalizers=spec.log_normalizers,
    )
    cauchy = _cauchy_channel_derivatives(
        time,
        spec.actions,
        b=spec.b,
        p=spec.p,
        log_normalizers=spec.log_normalizers,
    )
    scale = np.maximum(np.abs(analytic), 1.0e-12)
    relative_error = np.abs(cauchy.real - analytic) / scale
    maximum_relative_error = float(np.max(relative_error))
    maximum_scaled_imaginary = float(np.max(np.abs(cauchy.imag) / scale))
    maximum_error = max(maximum_relative_error, maximum_scaled_imaginary)
    return {
        "method": "analytic Bell recurrence versus 256-point Cauchy integral",
        "time": time,
        "orders": [0, 1, 2, 3, 4],
        "maximum_relative_real_error": maximum_relative_error,
        "maximum_scaled_imaginary_residue": maximum_scaled_imaginary,
        "maximum_error": maximum_error,
        "threshold": DERIVATIVE_CROSSCHECK_TOL,
        "passed": bool(maximum_error <= DERIVATIVE_CROSSCHECK_TOL),
    }


def _validate_cusp_fixture(
    *,
    fixture_role: str,
    b: float,
    initial_guess: np.ndarray,
    reference: np.ndarray,
    reference_scaled_fourth: float,
    reference_row_angle_sine: float,
) -> dict[str, Any]:
    """Solve and fail-closed audit one deterministic d=2 cusp fixture."""

    base = make_gig_specification(
        CUSP_TARGET_MODES,
        b=b,
        p=CUSP_P,
        weights=(1.0, 1.0, 1.0),
    )

    def equations(variables: np.ndarray) -> np.ndarray:
        time, weight_one, weight_two = map(float, variables)
        weights = np.asarray(
            (weight_one, weight_two, 1.0 - weight_one - weight_two),
            dtype=float,
        )
        if time <= 0.0 or np.any(weights <= 0.0):
            return np.full(3, 1.0e6, dtype=float)
        derivatives = channel_derivatives(
            time,
            base.actions,
            b=base.b,
            p=base.p,
            log_normalizers=base.log_normalizers,
        )
        return weights @ derivatives[:, 1:4]

    solution = root(
        equations,
        initial_guess,
        method="hybr",
        options={"xtol": 1.0e-12, "maxfev": 2_000},
    )
    time, weight_one, weight_two = map(float, solution.x)
    weights = np.asarray(
        (weight_one, weight_two, 1.0 - weight_one - weight_two),
        dtype=float,
    )
    spec = make_gig_specification(
        CUSP_TARGET_MODES,
        b=b,
        p=CUSP_P,
        weights=weights,
    )
    log_density, ratios, _shares = mixture_profile((time,), spec)
    density = float(np.exp(log_density[0]))
    raw_derivatives = density * ratios[:, 0]
    scaled_residuals = np.asarray(
        (
            abs(ratios[1, 0] * time),
            abs(ratios[2, 0] * time**2),
            abs(ratios[3, 0] * time**3),
        ),
        dtype=float,
    )
    scaled_fourth = float(ratios[4, 0] * time**4)

    channel_values = channel_derivatives(
        time,
        spec.actions,
        b=spec.b,
        p=spec.p,
        log_normalizers=spec.log_normalizers,
    )
    control_directions = np.asarray(
        ((1.0, 0.0, -1.0), (0.0, 1.0, -1.0)),
        dtype=float,
    )
    raw_unfolding = np.asarray(
        [
            [
                float(direction @ channel_values[:, derivative_order])
                for direction in control_directions
            ]
            for derivative_order in (1, 2)
        ],
        dtype=float,
    )
    dimensionless_unfolding = np.diag((time / density, time**2 / density)) @ raw_unfolding
    row_norms = np.linalg.norm(dimensionless_unfolding, axis=1)
    if np.any(~np.isfinite(row_norms)) or np.any(row_norms <= 0.0):
        raise FloatingPointError("unfolding row norm is zero or non-finite")
    row_normalized_unfolding = dimensionless_unfolding / row_norms[:, None]
    row_angle_normalized_determinant = float(np.linalg.det(row_normalized_unfolding))
    row_angle_sine_magnitude = abs(row_angle_normalized_determinant)
    raw_dimensionless_singular_values = np.linalg.svd(
        dimensionless_unfolding,
        compute_uv=False,
    )
    raw_dimensionless_svd_ratio = float(
        raw_dimensionless_singular_values[-1] / raw_dimensionless_singular_values[0]
    )
    unfolding_rank = int(
        np.linalg.matrix_rank(
            dimensionless_unfolding,
            tol=1.0e-12 * raw_dimensionless_singular_values[0],
        )
    )
    raw_determinant = float(np.linalg.det(raw_unfolding))
    dimensionless_raw_determinant = float(np.linalg.det(dimensionless_unfolding))
    reference_error = float(np.max(np.abs(solution.x - reference)))
    scaled_fourth_reference_error = abs(scaled_fourth - reference_scaled_fourth)
    row_angle_reference_error = abs(row_angle_sine_magnitude - reference_row_angle_sine)

    normalization = _normalization_audit(spec)
    derivative_crosscheck = _derivative_crosscheck(spec)
    gates = {
        "solver_converged": bool(solution.success),
        "reference_reproduced": bool(reference_error <= CUSP_REFERENCE_TOL),
        "positive_interior_weights": bool(np.min(weights) >= CUSP_MIN_WEIGHT),
        "weights_sum_to_one": bool(abs(float(weights.sum()) - 1.0) <= WEIGHT_SUM_TOL),
        "triple_derivative_residual": bool(float(np.max(scaled_residuals)) <= CUSP_RESIDUAL_TOL),
        "nonzero_fourth_derivative": bool(abs(scaled_fourth) >= CUSP_MIN_ABS_SCALED_FOURTH),
        "fourth_derivative_reference_reproduced": bool(
            scaled_fourth_reference_error <= CUSP_INVARIANT_REFERENCE_TOL
        ),
        "unfolding_rank_two": bool(unfolding_rank == 2),
        "unfolding_row_angle_transversality": bool(
            row_angle_sine_magnitude >= CUSP_MIN_ROW_ANGLE_SINE
        ),
        "unfolding_row_angle_reference_reproduced": bool(
            row_angle_reference_error <= CUSP_INVARIANT_REFERENCE_TOL
        ),
        "unfolding_raw_dimensionless_svd_conditioning": bool(
            raw_dimensionless_svd_ratio >= CUSP_MIN_SINGULAR_VALUE_RATIO
        ),
        "normalization": bool(normalization["passed"]),
        "fourth_derivative_crosscheck": bool(derivative_crosscheck["passed"]),
    }
    passed = bool(all(gates.values()))
    return {
        "status": "PASS" if passed else "FAIL",
        "fixture_role": fixture_role,
        "dimension": 2,
        "p": spec.p,
        "b": spec.b,
        "target_isolated_modes": spec.target_modes.tolist(),
        "actions": spec.actions.tolist(),
        "cusp_time": time,
        "weights": weights.tolist(),
        "solver_message": str(solution.message),
        "reference_candidate": reference.tolist(),
        "maximum_reference_error": reference_error,
        "reference_scaled_fourth_derivative": reference_scaled_fourth,
        "scaled_fourth_derivative_reference_error": (scaled_fourth_reference_error),
        "reference_row_angle_sine_magnitude": reference_row_angle_sine,
        "row_angle_sine_reference_error": row_angle_reference_error,
        "density": density,
        "raw_derivatives": {
            "f_t": float(raw_derivatives[1]),
            "f_tt": float(raw_derivatives[2]),
            "f_ttt": float(raw_derivatives[3]),
            "f_tttt": float(raw_derivatives[4]),
        },
        "scaled_derivative_residuals": {
            "t_f_t_over_f": float(scaled_residuals[0]),
            "t2_f_tt_over_f": float(scaled_residuals[1]),
            "t3_f_ttt_over_f": float(scaled_residuals[2]),
        },
        "scaled_fourth_derivative": scaled_fourth,
        "control_directions": control_directions.tolist(),
        "unfolding_transversality": {
            "raw_derivative_matrix": raw_unfolding.tolist(),
            "raw_derivative_matrix_determinant": raw_determinant,
            "dimensionless_raw_matrix": dimensionless_unfolding.tolist(),
            "dimensionless_raw_matrix_determinant": (dimensionless_raw_determinant),
            "row_normalized_dimensionless_matrix": (row_normalized_unfolding.tolist()),
            "row_angle_normalized_determinant": (row_angle_normalized_determinant),
            "row_angle_sine_magnitude": row_angle_sine_magnitude,
            "dimensionless_raw_matrix_singular_values": (
                raw_dimensionless_singular_values.tolist()
            ),
            "dimensionless_raw_matrix_svd_ratio": (raw_dimensionless_svd_ratio),
            "rank": unfolding_rank,
        },
        "normalization_audit": normalization,
        "derivative_crosscheck": derivative_crosscheck,
        "gates": gates,
    }


def validate_cusp_candidate() -> dict[str, Any]:
    """Audit the canonical b=0.01 d=2 three-channel preliminary result."""

    return _validate_cusp_fixture(
        fixture_role="canonical_preliminary_result",
        b=CUSP_B,
        initial_guess=CUSP_INITIAL_GUESS,
        reference=CUSP_REFERENCE,
        reference_scaled_fourth=CUSP_REFERENCE_SCALED_FOURTH,
        reference_row_angle_sine=CUSP_REFERENCE_ROW_ANGLE_SINE,
    )


def validate_cusp_robustness_candidate() -> dict[str, Any]:
    """Audit the distinct b=0.1 robustness fixture."""

    return _validate_cusp_fixture(
        fixture_role="robustness_case_not_canonical",
        b=ROBUSTNESS_CUSP_B,
        initial_guess=ROBUSTNESS_CUSP_INITIAL_GUESS,
        reference=ROBUSTNESS_CUSP_REFERENCE,
        reference_scaled_fourth=ROBUSTNESS_CUSP_REFERENCE_SCALED_FOURTH,
        reference_row_angle_sine=ROBUSTNESS_CUSP_REFERENCE_ROW_ANGLE_SINE,
    )


def _sign_change_indices(values: np.ndarray) -> np.ndarray:
    data = np.asarray(values, dtype=float).reshape(-1)
    if data.size < 2 or np.any(~np.isfinite(data)):
        raise FloatingPointError("root scan contains insufficient or non-finite values")
    if np.any(data == 0.0):
        raise RuntimeError("root scan landed exactly on zero; adjust deterministic grid")
    return np.flatnonzero(np.signbit(data[:-1]) != np.signbit(data[1:]))


def _dimensionless_derivative_at_log_time(
    log_time: float,
    spec: GIGSpecification,
    derivative_order: int,
) -> float:
    time = math.exp(float(log_time))
    _log_density, ratios, _shares = mixture_profile((time,), spec)
    return float(time**derivative_order * ratios[derivative_order, 0])


def _refine_scan_roots(
    log_times: np.ndarray,
    sampled_values: np.ndarray,
    spec: GIGSpecification,
    derivative_order: int,
) -> list[float]:
    roots: list[float] = []
    for index in _sign_change_indices(sampled_values):
        root_log_time = brentq(
            lambda value: _dimensionless_derivative_at_log_time(
                value,
                spec,
                derivative_order,
            ),
            float(log_times[index]),
            float(log_times[index + 1]),
            xtol=5.0e-15,
            rtol=1.0e-14,
            maxiter=300,
        )
        root_time = math.exp(root_log_time)
        if roots and root_time <= roots[-1]:
            raise RuntimeError("refined roots are not strictly ordered")
        roots.append(root_time)
    return roots


def validate_well_separated_case(
    mode_count: int,
    *,
    scan_points: int = SCAN_POINTS,
) -> dict[str, Any]:
    """Validate one deterministic ``m``-mode well-separated construction."""

    if mode_count not in CONSTRUCTION_MODE_COUNTS:
        raise ValueError(f"mode_count must be one of {CONSTRUCTION_MODE_COUNTS}")
    if int(scan_points) != scan_points or scan_points < 20_000:
        raise ValueError("scan_points must be an integer of at least 20000")
    target_modes = CONSTRUCTION_SEPARATION_FACTOR ** np.arange(
        mode_count,
        dtype=float,
    )
    spec = make_gig_specification(
        target_modes,
        b=CONSTRUCTION_B,
        p=CONSTRUCTION_P,
    )
    lower_time = float(target_modes[0] / 50.0)
    upper_time = float(target_modes[-1] * 5.0)
    log_times = np.linspace(
        math.log(lower_time),
        math.log(upper_time),
        scan_points,
    )
    times = np.exp(log_times)
    _sampled_log_density, sampled_ratios, _sampled_shares = mixture_profile(
        times,
        spec,
    )
    sampled_score = times * sampled_ratios[1]
    sampled_curvature = times**2 * sampled_ratios[2]
    roots = _refine_scan_roots(
        log_times,
        sampled_score,
        spec,
        derivative_order=1,
    )
    inflection_roots = _refine_scan_roots(
        log_times,
        sampled_curvature,
        spec,
        derivative_order=2,
    )

    root_rows: list[dict[str, Any]] = []
    for root_index, root_time in enumerate(roots, start=1):
        root_log_density, root_ratios, root_shares = mixture_profile(
            (root_time,),
            spec,
        )
        dimensionless_curvature = float(root_time**2 * root_ratios[2, 0])
        root_rows.append(
            {
                "root_index": root_index,
                "time": root_time,
                "kind": "maximum" if dimensionless_curvature < 0.0 else "minimum",
                "log_density": float(root_log_density[0]),
                "scaled_first_derivative_residual": abs(float(root_time * root_ratios[1, 0])),
                "dimensionless_curvature": dimensionless_curvature,
                "dominant_channel": int(np.argmax(root_shares[:, 0])) + 1,
                "dominant_channel_share": float(np.max(root_shares[:, 0])),
            }
        )

    prominence_rows: list[dict[str, Any]] = []
    for index, row in enumerate(root_rows):
        if row["kind"] != "maximum":
            continue
        adjacent_indices = [
            neighbor
            for neighbor in (index - 1, index + 1)
            if 0 <= neighbor < len(root_rows) and root_rows[neighbor]["kind"] == "minimum"
        ]
        ratios = [
            math.exp(row["log_density"] - root_rows[neighbor]["log_density"])
            for neighbor in adjacent_indices
        ]
        if not ratios:
            raise RuntimeError("maximum has no adjacent audited minimum")
        prominence_rows.append(
            {
                "maximum_root_index": row["root_index"],
                "adjacent_peak_to_valley_ratios": ratios,
                "minimum_ratio": min(ratios),
            }
        )

    inflection_score_margins: list[float] = []
    for inflection_time in inflection_roots:
        _log_density, ratios, _shares = mixture_profile((inflection_time,), spec)
        inflection_score_margins.append(abs(float(inflection_time * ratios[1, 0])))

    expected_kinds = [
        "maximum" if index % 2 == 0 else "minimum" for index in range(2 * mode_count - 1)
    ]
    observed_kinds = [row["kind"] for row in root_rows]
    maximum_count = observed_kinds.count("maximum")
    minimum_count = observed_kinds.count("minimum")
    maximum_root_residual = max(row["scaled_first_derivative_residual"] for row in root_rows)
    minimum_curvature = min(abs(row["dimensionless_curvature"]) for row in root_rows)
    minimum_prominence = min(row["minimum_ratio"] for row in prominence_rows)
    minimum_log_spacing = min(math.log(right / left) for left, right in zip(roots, roots[1:]))
    minimum_inflection_margin = min(inflection_score_margins)
    weight_dynamic_range = float(np.max(spec.weights) / np.min(spec.weights))
    isolated_mode_residuals = np.abs(
        (spec.actions / spec.target_modes**2 - spec.p / spec.target_modes - spec.b)
        * spec.target_modes
    )
    early_score = float(sampled_score[0])
    late_score = float(sampled_score[-1])
    gates = {
        "positive_normalized_weights": bool(
            np.all(spec.weights > 0.0) and abs(float(spec.weights.sum()) - 1.0) <= WEIGHT_SUM_TOL
        ),
        "prescribed_isolated_modes": bool(
            float(np.max(isolated_mode_residuals)) <= ISOLATED_MODE_RESIDUAL_TOL
        ),
        "tail_derivative_signs": bool(early_score > 0.0 and late_score < 0.0),
        "expected_root_count": bool(len(root_rows) == 2 * mode_count - 1),
        "expected_extrema_counts": bool(
            maximum_count == mode_count and minimum_count == mode_count - 1
        ),
        "alternating_topology": bool(observed_kinds == expected_kinds),
        "root_residuals": bool(maximum_root_residual <= ROOT_RESIDUAL_TOL),
        "nondegenerate_curvature": bool(minimum_curvature >= MIN_DIMENSIONLESS_CURVATURE),
        "prominence": bool(minimum_prominence >= MIN_PROMINENCE_RATIO),
        "root_spacing": bool(minimum_log_spacing >= MIN_LOG_ROOT_SPACING),
        "tangency_falsifier": bool(minimum_inflection_margin >= MIN_INFLECTION_SCORE_MARGIN),
        "weight_conditioning": bool(weight_dynamic_range <= MAX_WEIGHT_DYNAMIC_RANGE),
    }
    passed = bool(all(gates.values()))
    return {
        "status": "PASS" if passed else "FAIL",
        "mode_count": mode_count,
        "p": spec.p,
        "b": spec.b,
        "target_isolated_modes": spec.target_modes.tolist(),
        "actions": spec.actions.tolist(),
        "weights": spec.weights.tolist(),
        "weight_dynamic_range": weight_dynamic_range,
        "scan_interval": [lower_time, upper_time],
        "scan_points": int(scan_points),
        "early_dimensionless_score": early_score,
        "late_dimensionless_score": late_score,
        "roots": root_rows,
        "inflection_root_count": len(inflection_roots),
        "minimum_inflection_score_margin": minimum_inflection_margin,
        "prominence": prominence_rows,
        "maximum_scaled_root_residual": maximum_root_residual,
        "minimum_absolute_dimensionless_curvature": minimum_curvature,
        "minimum_peak_to_adjacent_valley_ratio": minimum_prominence,
        "minimum_log_root_spacing": minimum_log_spacing,
        "maximum_isolated_mode_residual": float(np.max(isolated_mode_residuals)),
        "gates": gates,
    }


def build_payload(*, scan_points: int = SCAN_POINTS) -> dict[str, Any]:
    cusp = validate_cusp_candidate()
    robustness_cusps = [validate_cusp_robustness_candidate()]
    cases = [
        validate_well_separated_case(mode_count, scan_points=scan_points)
        for mode_count in CONSTRUCTION_MODE_COUNTS
    ]
    all_cases_pass = all(case["status"] == "PASS" for case in cases)
    all_robustness_cusps_pass = all(case["status"] == "PASS" for case in robustness_cusps)
    passed = cusp["status"] == "PASS" and all_robustness_cusps_pass and all_cases_pass
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if passed else "FAIL",
        "claim_scope": CLAIM_SCOPE,
        "generator": str(HERE.relative_to(REPORT)),
        "deterministic_parameters": {
            "cusp": {
                "fixture_role": "canonical_preliminary_result",
                "dimension": 2,
                "p": CUSP_P,
                "b": CUSP_B,
                "target_modes": CUSP_TARGET_MODES.tolist(),
            },
            "cusp_robustness_cases": [
                {
                    "fixture_role": "robustness_case_not_canonical",
                    "dimension": 2,
                    "p": CUSP_P,
                    "b": ROBUSTNESS_CUSP_B,
                    "target_modes": CUSP_TARGET_MODES.tolist(),
                }
            ],
            "well_separated": {
                "p": CONSTRUCTION_P,
                "b": CONSTRUCTION_B,
                "mode_counts": list(CONSTRUCTION_MODE_COUNTS),
                "separation_factor": CONSTRUCTION_SEPARATION_FACTOR,
                "scan_points": int(scan_points),
            },
        },
        "thresholds": {
            "normalization_tolerance": NORMALIZATION_TOL,
            "derivative_crosscheck_tolerance": DERIVATIVE_CROSSCHECK_TOL,
            "cusp_scaled_residual_tolerance": CUSP_RESIDUAL_TOL,
            "cusp_minimum_weight": CUSP_MIN_WEIGHT,
            "cusp_minimum_absolute_scaled_fourth": CUSP_MIN_ABS_SCALED_FOURTH,
            "cusp_minimum_row_angle_sine": CUSP_MIN_ROW_ANGLE_SINE,
            "cusp_minimum_raw_dimensionless_svd_ratio": (CUSP_MIN_SINGULAR_VALUE_RATIO),
            "cusp_invariant_reference_tolerance": CUSP_INVARIANT_REFERENCE_TOL,
            "root_scaled_residual_tolerance": ROOT_RESIDUAL_TOL,
            "minimum_dimensionless_curvature": MIN_DIMENSIONLESS_CURVATURE,
            "minimum_peak_to_valley_ratio": MIN_PROMINENCE_RATIO,
            "minimum_log_root_spacing": MIN_LOG_ROOT_SPACING,
            "minimum_inflection_score_margin": MIN_INFLECTION_SCORE_MARGIN,
            "maximum_weight_dynamic_range": MAX_WEIGHT_DYNAMIC_RANGE,
        },
        "cusp_candidate": cusp,
        "cusp_robustness_cases": robustness_cusps,
        "well_separated_constructions": cases,
        "summary": {
            "cusp_passed": cusp["status"] == "PASS",
            "canonical_cusp_b": cusp["b"],
            "robustness_cusp_cases_passed": all_robustness_cusps_pass,
            "passed_mode_counts": [
                case["mode_count"] for case in cases if case["status"] == "PASS"
            ],
            "maximum_verified_mode_count": max(
                case["mode_count"] for case in cases if case["status"] == "PASS"
            )
            if all_cases_pass
            else None,
            "minimum_prominence_ratio": min(
                case["minimum_peak_to_adjacent_valley_ratio"] for case in cases
            ),
            "minimum_curvature_margin": min(
                case["minimum_absolute_dimensionless_curvature"] for case in cases
            ),
            "maximum_root_residual": max(case["maximum_scaled_root_residual"] for case in cases),
        },
        "limitations": [
            "the GIG channel form is a free-space narrow-patch screening law",
            "abstract mixture weights are not yet realized by a Doi or Robin catalyst field",
            "finite sign-change and inflection scans are not interval-exhaustive root proofs",
            "no bounded-domain PDE, Brownian dynamics, mesh refinement, or continuum limit is evaluated",
        ],
    }


def _write_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def run_validation(
    output: Path = DEFAULT_OUTPUT,
    *,
    scan_points: int = SCAN_POINTS,
) -> dict[str, Any]:
    payload = build_payload(scan_points=scan_points)
    _write_payload(output, payload)
    if payload["status"] != "PASS":
        raise RuntimeError(f"GIG constructive pilot failed; inspect {output}")
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="JSON output path (default: report artifacts/data)",
    )
    parser.add_argument(
        "--scan-points",
        type=int,
        default=SCAN_POINTS,
        help="deterministic log-time points per well-separated case",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    payload = run_validation(args.output, scan_points=args.scan_points)
    cusp = payload["cusp_candidate"]
    summary = payload["summary"]
    print(
        "GIG constructive pilot PASS: "
        f"canonical b={cusp['b']:.3g}, t={cusp['cusp_time']:.12g}, "
        f"rank={cusp['unfolding_transversality']['rank']}, "
        f"m=2..{summary['maximum_verified_mode_count']}, "
        f"min prominence={summary['minimum_prominence_ratio']:.6g}"
    )
    print(args.output)


if __name__ == "__main__":
    main()
