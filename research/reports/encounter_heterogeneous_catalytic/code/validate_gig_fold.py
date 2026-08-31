#!/usr/bin/env python3
"""Validate GIG channel asymptotics and a physical CTMC modality fold.

The GIG calculation is an asymptotic screening model.  The physical fold is
located independently in the finite-state killed CTMC using floating-point
finite-matrix semigroup derivative evaluations and an augmented sensitivity
equation for the control parameter.  The script deliberately keeps those two
evidence levels separate.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import sparse
from scipy.optimize import brentq, minimize_scalar, root
from scipy.signal import find_peaks
from scipy.sparse.linalg import expm_multiply, spsolve
from scipy.special import gammaln, kve
from vkcore.encounter import reflecting_biased_ctmc_generator
from vkcore.plotting import enforce_publication_graphics
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
NOTES = REPORT / "notes"
for directory in (DATA, FIGURES, NOTES):
    directory.mkdir(parents=True, exist_ok=True)


LARGE_BESSEL_ARGUMENT = 1e5


def _log_scaled_bessel_k(order: float, argument: float) -> float:
    """Return ``log(exp(x) K_order(x))`` across the binary64 range."""

    x = float(argument)
    if not x > 0.0:
        raise ValueError("Bessel argument must be positive")
    if x >= LARGE_BESSEL_ARGUMENT:
        # DLMF 10.40.2.  Four terms are ample at the deliberately conservative
        # threshold; unlike scipy.special.kve this remains finite at x~1e9.
        mu = 4.0 * float(order) ** 2
        term = 1.0
        series = 1.0
        for index in range(1, 5):
            term *= (mu - float((2 * index - 1) ** 2)) / (index * 8.0 * x)
            series += term
        if not series > 0.0:
            raise FloatingPointError("large-argument Bessel asymptotic lost positivity")
        return float(0.5 * (np.log(np.pi) - np.log(2.0 * x)) + np.log(series))
    scaled = float(kve(order, x))
    return float(np.log(scaled)) if np.isfinite(scaled) and scaled > 0.0 else float("nan")


@dataclass(frozen=True)
class GIGChannel:
    """Normalized ``t^-nu exp(-A/t-B*t)`` channel on positive time."""

    name: str
    A: float
    B: float
    nu: float

    def __post_init__(self) -> None:
        if not self.A > 0.0:
            raise ValueError("A must be positive")
        if self.B < 0.0:
            raise ValueError("B must be non-negative")
        if self.B == 0.0 and not self.nu > 1.0:
            raise ValueError("B=0 requires nu>1 for normalization")

    @property
    def log_normalization(self) -> float:
        """Return ``log Z`` without raw Bessel or power under/overflow."""

        if self.B == 0.0:
            return float((1.0 - self.nu) * np.log(self.A) + gammaln(self.nu - 1.0))
        argument = 2.0 * np.sqrt(self.A * self.B)
        log_scaled_bessel = _log_scaled_bessel_k(1.0 - self.nu, argument)
        if np.isfinite(log_scaled_bessel):
            return float(
                np.log(2.0)
                + ((1.0 - self.nu) / 2.0)
                * (np.log(self.A) - np.log(self.B))
                + log_scaled_bessel
                - argument
            )
        if argument < 1e-6 and self.nu > 1.0:
            # Leading small-argument K_{nu-1} asymptotic.  This branch is
            # reached only after scaled kve itself overflows.  At that point
            # the correction is below binary64 resolution for the physical
            # nu >= 3/2 family.
            return float(
                (1.0 - self.nu) * np.log(self.A) + gammaln(self.nu - 1.0)
            )
        raise FloatingPointError(
            "scaled Bessel evaluation failed outside certified small/large-argument branches"
        )

    @property
    def normalization(self) -> float:
        """Return ``Z`` when representable; use ``log_normalization`` generally."""

        return float(np.exp(self.log_normalization))

    @property
    def mode(self) -> float:
        if self.B == 0.0:
            return self.A / self.nu
        # The algebraically equivalent conjugate form avoids subtracting two
        # nearly equal numbers when B is small.
        return float(
            2.0
            * self.A
            / (self.nu + np.sqrt(self.nu**2 + 4.0 * self.A * self.B))
        )

    def derivatives(
        self, times: float | np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return density and its first three exact time derivatives."""

        t = np.asarray(times, dtype=float)
        if np.any(t <= 0.0):
            raise ValueError("GIG density is defined only for t>0")
        log_density = (
            -self.nu * np.log(t)
            - self.A / t
            - self.B * t
            - self.log_normalization
        )
        density = np.exp(log_density)
        log_d1 = self.A / t**2 - self.B - self.nu / t
        log_d2 = -2.0 * self.A / t**3 + self.nu / t**2
        log_d3 = 6.0 * self.A / t**4 - 2.0 * self.nu / t**3
        d1 = density * log_d1
        d2 = density * (log_d1**2 + log_d2)
        d3 = density * (log_d1**3 + 3.0 * log_d1 * log_d2 + log_d3)
        return density, d1, d2, d3


def _scalar(value: np.ndarray | float) -> float:
    return float(np.asarray(value))


def _dot(left: np.ndarray, right: np.ndarray) -> float:
    """A warning-free dot product for cancellation-sensitive diagnostics."""

    return float(np.sum(np.asarray(left) * np.asarray(right)))


def geometry_to_channels() -> tuple[dict[str, float], GIGChannel, GIGChannel, GIGChannel]:
    """Map the canonical lattice's interior rates to Brownian channel laws."""

    q1, q2 = 0.7, 0.2
    bias1 = bias2 = 0.3
    diffusion1, diffusion2 = q1 / 2.0, q2 / 2.0
    velocity1, velocity2 = q1 * bias1, q2 * bias2
    relative_diffusion = diffusion1 + diffusion2
    centre_diffusion = diffusion1 * diffusion2 / relative_diffusion
    closing_speed = velocity1 - velocity2
    centre_velocity = (
        diffusion2 * velocity1 + diffusion1 * velocity2
    ) / relative_diffusion

    start1, start2 = 3.0, 15.0
    near_site, far_site = 13.0, 30.0
    separation = start2 - start1
    centre_start = (
        diffusion2 * start1 + diffusion1 * start2
    ) / relative_diffusion
    centre_offset = near_site - centre_start
    far_distance = far_site - start2

    relative_A = separation**2 / (4.0 * relative_diffusion)
    relative_B = closing_speed**2 / (4.0 * relative_diffusion)
    early_A = relative_A + centre_offset**2 / (4.0 * centre_diffusion)
    early_B = relative_B + centre_velocity**2 / (4.0 * centre_diffusion)
    late_A = far_distance**2 / (4.0 * diffusion2)
    late_B = velocity2**2 / (4.0 * diffusion2)

    parameters = {
        "q1": q1,
        "q2": q2,
        "bias1": bias1,
        "bias2": bias2,
        "D1": diffusion1,
        "D2": diffusion2,
        "v1": velocity1,
        "v2": velocity2,
        "D_relative": relative_diffusion,
        "D_centre": centre_diffusion,
        "closing_speed": closing_speed,
        "centre_velocity": centre_velocity,
        "start1": start1,
        "start2": start2,
        "near_site": near_site,
        "far_site": far_site,
        "initial_separation": separation,
        "centre_start": centre_start,
        "centre_offset_to_near_patch": centre_offset,
        "far_distance": far_distance,
    }
    relative = GIGChannel("relative_IG", relative_A, relative_B, 1.5)
    early = GIGChannel("joint_relative_centre_GIG", early_A, early_B, 2.0)
    late = GIGChannel("boundary_IG", late_A, late_B, 1.5)
    return parameters, relative, early, late


def fixed_shape_folds(
    channel1: GIGChannel,
    channel2: GIGChannel,
    *,
    t_min: float = 0.05,
    t_max: float = 5000.0,
    scan_points: int = 20_001,
) -> list[dict[str, float]]:
    """Find all admissible fixed-shape mixture folds on a log-time scan."""

    def determinant(time: float) -> float:
        _, g1p, g1pp, _ = channel1.derivatives(time)
        _, g2p, g2pp, _ = channel2.derivatives(time)
        return _scalar(g1p * g2pp - g2p * g1pp)

    times = np.geomspace(t_min, t_max, scan_points)
    values = np.asarray([determinant(time) for time in times])
    brackets: list[tuple[float, float]] = []
    for left, right, f_left, f_right in zip(
        times[:-1], times[1:], values[:-1], values[1:], strict=True
    ):
        # Both channel densities underflow in the remote log-time tails.  A
        # literal zero there is not a determinant root, so bracket only
        # strict, nonzero sign changes (and avoid multiplying tiny values).
        if (
            f_left != 0.0
            and f_right != 0.0
            and np.signbit(f_left) != np.signbit(f_right)
        ):
            brackets.append((float(left), float(right)))

    folds: list[dict[str, float]] = []
    for left, right in brackets:
        time = float(brentq(determinant, left, right, xtol=1e-13, rtol=1e-13))
        _, g1p, g1pp, g1ppp = channel1.derivatives(time)
        _, g2p, g2pp, g2ppp = channel2.derivatives(time)
        denominator = _scalar(g1p - g2p)
        weight = -_scalar(g2p) / denominator
        if not 0.0 < weight < 1.0:
            continue
        first = weight * _scalar(g1p) + (1.0 - weight) * _scalar(g2p)
        second = weight * _scalar(g1pp) + (1.0 - weight) * _scalar(g2pp)
        third = weight * _scalar(g1ppp) + (1.0 - weight) * _scalar(g2ppp)
        folds.append(
            {
                "time": time,
                "early_weight": weight,
                "determinant_residual": determinant(time),
                "mixture_first_derivative": first,
                "mixture_second_derivative": second,
                "mixture_third_derivative": third,
                "weight_transversality": denominator,
            }
        )
    return folds


@dataclass(frozen=True)
class PhysicalCTMC:
    theta: float
    killed_generator: sparse.csr_matrix
    total_rate: np.ndarray
    channel_rates: np.ndarray
    theta_generator: sparse.csr_matrix
    theta_total_rate: np.ndarray
    initial: np.ndarray
    kappa_near: float
    kappa_far: float


LATTICE_SIZE = 31
NEAR_SITE = 13
FAR_SITE = 30
START = (3, 15)
KAPPA_FAR = float(-np.log(0.4))


def _free_generator() -> sparse.csr_matrix:
    generator1 = sparse.csr_matrix(
        reflecting_biased_ctmc_generator(LATTICE_SIZE, 0.7, 0.3)
    )
    generator2 = sparse.csr_matrix(
        reflecting_biased_ctmc_generator(LATTICE_SIZE, 0.2, 0.3)
    )
    identity = sparse.eye(LATTICE_SIZE, format="csr")
    return (
        sparse.kron(generator1, identity, format="csr")
        + sparse.kron(identity, generator2, format="csr")
    ).tocsr()


FREE_GENERATOR = _free_generator()
NEAR_INDEX = NEAR_SITE * LATTICE_SIZE + NEAR_SITE
FAR_INDEX = FAR_SITE * LATTICE_SIZE + FAR_SITE
INITIAL = np.zeros(LATTICE_SIZE**2)
INITIAL[START[0] * LATTICE_SIZE + START[1]] = 1.0


def physical_ctmc(theta: float) -> PhysicalCTMC:
    """Build the killed CTMC for ``theta=log(kappa_near/kappa_far)``."""

    value = float(theta)
    kappa_near = KAPPA_FAR * np.exp(value)
    killed = FREE_GENERATOR.tolil(copy=True)
    killed[NEAR_INDEX, NEAR_INDEX] -= kappa_near
    killed[FAR_INDEX, FAR_INDEX] -= KAPPA_FAR
    killed = killed.tocsr()
    channel_rates = np.zeros((LATTICE_SIZE**2, 2))
    channel_rates[NEAR_INDEX, 0] = kappa_near
    channel_rates[FAR_INDEX, 1] = KAPPA_FAR
    total_rate = channel_rates.sum(axis=1)
    theta_generator = sparse.csr_matrix(
        ([-kappa_near], ([NEAR_INDEX], [NEAR_INDEX])),
        shape=killed.shape,
    )
    theta_total_rate = np.zeros_like(total_rate)
    theta_total_rate[NEAR_INDEX] = kappa_near
    return PhysicalCTMC(
        theta=value,
        killed_generator=killed,
        total_rate=total_rate,
        channel_rates=channel_rates,
        theta_generator=theta_generator,
        theta_total_rate=theta_total_rate,
        initial=INITIAL.copy(),
        kappa_near=float(kappa_near),
        kappa_far=KAPPA_FAR,
    )


def ctmc_density_derivative(model: PhysicalCTMC, time: float, order: int) -> float:
    state = expm_multiply(model.killed_generator.T * float(time), model.initial)
    observable = model.total_rate.copy()
    for _ in range(int(order)):
        observable = model.killed_generator @ observable
    return _dot(state, observable)


def ctmc_density(model: PhysicalCTMC, time: float) -> float:
    return ctmc_density_derivative(model, time, 0)


def ctmc_channel_density_derivative(
    model: PhysicalCTMC,
    time: float,
    channel: int,
    order: int,
) -> float:
    """Evaluate ``alpha exp(T t) T^order b_channel`` for the finite CTMC.

    The displayed expression is an exact finite-state identity, while its
    value is obtained with floating-point sparse matrix-exponential algebra.
    No sampled-grid extremum or finite-difference derivative is substituted.
    """

    channel_index = int(channel)
    if channel_index < 0 or channel_index >= model.channel_rates.shape[1]:
        raise IndexError(f"channel index {channel_index} is out of range")
    derivative_order = int(order)
    if derivative_order < 0:
        raise ValueError("derivative order must be non-negative")
    state = expm_multiply(model.killed_generator.T * float(time), model.initial)
    observable = model.channel_rates[:, channel_index].copy()
    for _ in range(derivative_order):
        observable = model.killed_generator @ observable
    return _dot(state, observable)


def locate_ctmc_channel_mode(
    model: PhysicalCTMC,
    channel: int,
    *,
    time_max: float = 500.0,
    scan_points: int = 1001,
) -> dict[str, float | int | str]:
    """Locate the largest detected channel maximum within ``[0, time_max]``.

    A deterministic grid detects positive-to-negative derivative sign changes.
    Brent's method then refines each bracket using finite-matrix semigroup
    derivative evaluations, and negative curvature identifies local maxima.
    The largest density among the detected roots is returned; this is neither
    an exhaustive root isolation nor a global-mode claim on ``(0, infinity)``.
    """

    horizon = float(time_max)
    points = int(scan_points)
    if not horizon > 0.0:
        raise ValueError("time_max must be positive")
    if points < 3:
        raise ValueError("scan_points must be at least three")

    times = np.linspace(0.0, horizon, points)
    states = expm_multiply(
        model.killed_generator.T,
        model.initial,
        start=0.0,
        stop=horizon,
        num=points,
        endpoint=True,
    )
    channel_index = int(channel)
    rate = model.channel_rates[:, channel_index]
    derivative_observable = model.killed_generator @ rate
    derivative = np.einsum("ti,i->t", states, derivative_observable)
    maxima: list[dict[str, float]] = []
    for left, right, d_left, d_right in zip(
        times[:-1], times[1:], derivative[:-1], derivative[1:], strict=True
    ):
        if not (d_left > 0.0 and d_right < 0.0):
            continue
        root_time = float(
            brentq(
                lambda value: ctmc_channel_density_derivative(
                    model, value, channel_index, 1
                ),
                float(left),
                float(right),
                xtol=1e-12,
                rtol=1e-13,
                maxiter=200,
            )
        )
        density = ctmc_channel_density_derivative(
            model, root_time, channel_index, 0
        )
        first = ctmc_channel_density_derivative(
            model, root_time, channel_index, 1
        )
        second = ctmc_channel_density_derivative(
            model, root_time, channel_index, 2
        )
        if second >= 0.0:
            raise RuntimeError("positive-to-negative derivative root lacks negative curvature")
        maxima.append(
            {
                "time": root_time,
                "density": density,
                "first_derivative": first,
                "second_derivative": second,
                "dimensionless_first_residual": abs(first) * root_time / density,
                "dimensionless_curvature": second * root_time**2 / density,
                "bracket_left": float(left),
                "bracket_right": float(right),
            }
        )

    if not maxima:
        raise RuntimeError("no negative-curvature channel mode was bracketed")
    selected = max(maxima, key=lambda row: row["density"])
    if derivative[-1] >= 0.0:
        raise RuntimeError("channel derivative has not entered its decreasing tail")
    selected.update(
        {
            "channel_index": channel_index,
            "root_count": len(maxima),
            "search_horizon": horizon,
            "scan_points": points,
            "root_method": (
                "Brent root refinement of detected alpha exp(T t) T b_channel "
                "sign changes within the declared horizon"
            ),
        }
    )
    return selected


def locate_physical_fold() -> tuple[dict[str, float], PhysicalCTMC]:
    """Numerically solve ``f_t=f_tt=0`` with finite-matrix semigroup derivatives."""

    residual_scales = np.asarray([1e-9, 1e-10])

    def residual(unknowns: np.ndarray) -> np.ndarray:
        time, theta = map(float, unknowns)
        model = physical_ctmc(theta)
        return np.asarray(
            [
                ctmc_density_derivative(model, time, 1),
                ctmc_density_derivative(model, time, 2),
            ]
        ) / residual_scales

    solution = root(residual, np.asarray([37.0, -9.7]), method="hybr", options={"xtol": 1e-11})
    if not solution.success:
        raise RuntimeError(f"physical fold root failed: {solution.message}")
    time, theta = map(float, solution.x)
    if not np.isfinite([time, theta]).all() or not (1e-6 < time < 5000.0):
        raise RuntimeError(
            f"physical fold root left the admissible time domain: t={time}, theta={theta}"
        )
    if not (-25.0 < theta < 10.0):
        raise RuntimeError(f"physical fold root left the declared control domain: {theta}")
    model = physical_ctmc(theta)
    density = ctmc_density(model, time)
    first = ctmc_density_derivative(model, time, 1)
    second = ctmc_density_derivative(model, time, 2)
    third = ctmc_density_derivative(model, time, 3)
    if not np.isfinite([density, first, second, third]).all() or density <= 1e-14:
        raise RuntimeError(
            "physical fold root has nonfinite or underflow-scale positive density"
        )
    dimensionless_first = abs(first) * time / density
    dimensionless_second = abs(second) * time**2 / density
    if max(dimensionless_first, dimensionless_second) >= 1e-8:
        raise RuntimeError(
            "physical fold root fails the dimensionless residual guard: "
            f"({dimensionless_first}, {dimensionless_second})"
        )

    zero = sparse.csr_matrix(model.killed_generator.shape)
    augmented = sparse.bmat(
        [
            [model.killed_generator.T, zero],
            [model.theta_generator.T, model.killed_generator.T],
        ],
        format="csr",
    )
    augmented_initial = np.concatenate([model.initial, np.zeros_like(model.initial)])
    augmented_state = expm_multiply(augmented * time, augmented_initial)
    state, sensitivity = np.split(augmented_state, 2)
    first_theta = (
        _dot(sensitivity, model.killed_generator @ model.total_rate)
        + _dot(state, model.theta_generator @ model.total_rate)
        + _dot(state, model.killed_generator @ model.theta_total_rate)
    )
    density_theta = _dot(sensitivity, model.total_rate) + _dot(
        state, model.theta_total_rate
    )
    dimensionless_third = third * time**3 / density
    dimensionless_transversality = first_theta * time / density
    if abs(dimensionless_third) <= 1e-3 or abs(dimensionless_transversality) <= 1e-5:
        raise RuntimeError(
            "physical fold root fails the nondegeneracy/transversality guard"
        )

    occupation = spsolve((-model.killed_generator).T, model.initial)
    splitting = np.asarray(occupation @ model.channel_rates, dtype=float)
    mass_closure_error = abs(float(np.sum(splitting)) - 1.0)
    tail_at_5000 = float(
        np.sum(expm_multiply(model.killed_generator.T * 5000.0, model.initial))
    )

    summary = {
        "time": time,
        "theta_log_kappa_near_over_far": theta,
        "kappa_near": model.kappa_near,
        "kappa_far": model.kappa_far,
        "density": density,
        "first_derivative": first,
        "second_derivative": second,
        "third_derivative": third,
        "time_parameter_transversality": first_theta,
        "density_parameter_derivative": density_theta,
        "dimensionless_first_residual": dimensionless_first,
        "dimensionless_second_residual": dimensionless_second,
        "dimensionless_third_derivative": dimensionless_third,
        "dimensionless_transversality": dimensionless_transversality,
        "root_acceptance_guard": {
            "time_domain": [1e-6, 5000.0],
            "theta_domain": [-25.0, 10.0],
            "minimum_positive_density": 1e-14,
            "maximum_dimensionless_fold_residual": 1e-8,
            "minimum_abs_dimensionless_third_derivative": 1e-3,
            "minimum_abs_dimensionless_transversality": 1e-5,
        },
        "near_splitting_probability": float(splitting[0]),
        "far_splitting_probability": float(splitting[1]),
        "mass_closure_error": mass_closure_error,
        "tail_at_5000": tail_at_5000,
    }
    return summary, model


def _critical_pair(
    theta: float,
    fold_time: float,
    normal_half_separation: float,
) -> tuple[float, float]:
    model = physical_ctmc(theta)

    def derivative(time: float) -> float:
        return ctmc_density_derivative(model, time, 1)

    span = max(0.25, 3.0 * normal_half_separation)
    for _ in range(8):
        left = fold_time - span
        right = fold_time + span
        centre_value = derivative(fold_time)
        if derivative(left) > 0.0 and centre_value < 0.0 and derivative(right) > 0.0:
            maximum = brentq(derivative, left, fold_time, xtol=2e-12, rtol=2e-14)
            minimum = brentq(derivative, fold_time, right, xtol=2e-12, rtol=2e-14)
            return float(maximum), float(minimum)
        span *= 1.7
    raise RuntimeError(f"could not bracket critical pair at theta={theta}")


def physical_continuation(fold: dict[str, float]) -> tuple[list[dict], dict[str, float]]:
    """Generate held-out points on both sides of the fold."""

    time_star = fold["time"]
    theta_star = fold["theta_log_kappa_near_over_far"]
    a = fold["time_parameter_transversality"]
    b = fold["third_derivative"]
    if not (a < 0.0 and b > 0.0):
        raise RuntimeError("unexpected fold orientation")
    half_separation_coefficient = float(np.sqrt(-2.0 * a / b))
    separation_coefficient = 2.0 * half_separation_coefficient
    prominence_coefficient = (
        2.0 / 3.0 * b * half_separation_coefficient**3
    )

    negative_deltas = -np.asarray([0.064, 0.032, 0.016, 0.008, 0.004, 0.002, 0.001])
    positive_deltas = np.asarray([0.001, 0.002, 0.004, 0.008, 0.016, 0.032, 0.064])
    rows: list[dict] = []
    for delta in negative_deltas:
        model = physical_ctmc(theta_star + float(delta))
        minimum = minimize_scalar(
            lambda time: ctmc_density_derivative(model, time, 1),
            bounds=(time_star - 3.0, time_star + 3.0),
            method="bounded",
            options={"xatol": 1e-10},
        )
        rows.append(
            {
                "delta_theta": float(delta),
                "theta": theta_star + float(delta),
                "side": "one-peak-side",
                "local_critical_pair_count": 0,
                "early_maximum_time": "",
                "intervening_minimum_time": "",
                "critical_point_separation": "",
                "local_prominence": "",
                "minimum_local_first_derivative": float(minimum.fun),
                "normal_form_separation": "",
                "normal_form_prominence": "",
            }
        )
    positive_rows: list[dict] = []
    for delta in positive_deltas:
        half_prediction = half_separation_coefficient * np.sqrt(delta)
        maximum, minimum = _critical_pair(
            theta_star + float(delta), time_star, half_prediction
        )
        model = physical_ctmc(theta_star + float(delta))
        separation = minimum - maximum
        prominence = ctmc_density(model, maximum) - ctmc_density(model, minimum)
        row = {
            "delta_theta": float(delta),
            "theta": theta_star + float(delta),
            "side": "two-peak-side",
            "local_critical_pair_count": 2,
            "early_maximum_time": maximum,
            "intervening_minimum_time": minimum,
            "critical_point_separation": separation,
            "local_prominence": prominence,
            "minimum_local_first_derivative": ctmc_density_derivative(
                model, time_star, 1
            ),
            "normal_form_separation": separation_coefficient * np.sqrt(delta),
            "normal_form_prominence": prominence_coefficient * delta**1.5,
        }
        positive_rows.append(row)
        rows.append(row)

    fit_rows = positive_rows[:6]
    log_delta = np.log([row["delta_theta"] for row in fit_rows])
    separation_slope, separation_intercept = np.polyfit(
        log_delta,
        np.log([row["critical_point_separation"] for row in fit_rows]),
        1,
    )
    prominence_slope, prominence_intercept = np.polyfit(
        log_delta,
        np.log([row["local_prominence"] for row in fit_rows]),
        1,
    )
    fits = {
        "normal_form_half_separation_coefficient": half_separation_coefficient,
        "normal_form_separation_coefficient": separation_coefficient,
        "normal_form_prominence_coefficient": prominence_coefficient,
        "held_out_fit_max_delta": float(fit_rows[-1]["delta_theta"]),
        "held_out_separation_loglog_slope": float(separation_slope),
        "held_out_separation_loglog_intercept": float(separation_intercept),
        "held_out_prominence_loglog_slope": float(prominence_slope),
        "held_out_prominence_loglog_intercept": float(prominence_intercept),
    }
    return rows, fits


def _quadratic_vertex(times: np.ndarray, values: np.ndarray, index: int) -> float:
    coefficients = np.polyfit(times[index - 1 : index + 2], values[index - 1 : index + 2], 2)
    return float(-coefficients[1] / (2.0 * coefficients[0]))


def convergence_rows(
    early: GIGChannel,
    late: GIGChannel,
    fold: dict[str, float],
    continuation: list[dict],
) -> list[dict]:
    """Independent quadrature and sampled-time convergence diagnostics."""

    rows: list[dict] = []
    for points in (501, 1001, 2001, 4001, 8001, 16001):
        times = np.geomspace(1e-4, 2e4, points)
        early_mass = float(np.trapezoid(early.derivatives(times)[0], times))
        late_mass = float(np.trapezoid(late.derivatives(times)[0], times))
        rows.append(
            {
                "diagnostic": "GIG_log_quadrature_grid",
                "resolution": points,
                "secondary_resolution": "",
                "error_primary": abs(early_mass - 1.0),
                "error_secondary": abs(late_mass - 1.0),
                "estimate_primary": early_mass,
                "estimate_secondary": late_mass,
            }
        )

    time_star = fold["time"]
    model_star = physical_ctmc(fold["theta_log_kappa_near_over_far"])
    density_star = ctmc_density(model_star, time_star)
    for step in (1.0, 0.5, 0.25, 0.125, 0.0625):
        minus = ctmc_density(model_star, time_star - step)
        plus = ctmc_density(model_star, time_star + step)
        first_fd = (plus - minus) / (2.0 * step)
        second_fd = (plus - 2.0 * density_star + minus) / step**2
        rows.append(
            {
                "diagnostic": "CTMC_fold_central_time_difference",
                "resolution": step,
                "secondary_resolution": "",
                "error_primary": abs(first_fd - fold["first_derivative"]),
                "error_secondary": abs(second_fd - fold["second_derivative"]),
                "estimate_primary": first_fd,
                "estimate_secondary": second_fd,
            }
        )

    reference = next(
        row for row in continuation if np.isclose(row["delta_theta"], 0.064)
    )
    model = physical_ctmc(fold["theta_log_kappa_near_over_far"] + 0.064)
    for requested_step in (0.8, 0.4, 0.2, 0.1, 0.05):
        times = np.arange(25.0, 50.0 + 0.5 * requested_step, requested_step)
        states = expm_multiply(
            model.killed_generator.T,
            model.initial,
            start=float(times[0]),
            stop=float(times[-1]),
            num=times.size,
            endpoint=True,
        )
        density = np.einsum("ti,i->t", states, model.total_rate)
        maxima = find_peaks(density)[0]
        minima = find_peaks(-density)[0]
        if maxima.size != 1 or minima.size != 1:
            raise RuntimeError(f"sampled extrema failure at dt={requested_step}")
        estimated_maximum = _quadratic_vertex(times, density, int(maxima[0]))
        estimated_minimum = _quadratic_vertex(times, density, int(minima[0]))
        max_error = max(
            abs(estimated_maximum - float(reference["early_maximum_time"])),
            abs(estimated_minimum - float(reference["intervening_minimum_time"])),
        )
        rows.append(
            {
                "diagnostic": "CTMC_sampled_extremum_time_grid",
                "resolution": requested_step,
                "secondary_resolution": times.size,
                "error_primary": max_error,
                "error_secondary": abs(
                    (estimated_minimum - estimated_maximum)
                    - float(reference["critical_point_separation"])
                ),
                "estimate_primary": estimated_maximum,
                "estimate_secondary": estimated_minimum,
            }
        )

    transversality = fold["time_parameter_transversality"]
    for step in (1e-2, 3e-3, 1e-3, 3e-4, 1e-4):
        plus = ctmc_density_derivative(
            physical_ctmc(fold["theta_log_kappa_near_over_far"] + step),
            time_star,
            1,
        )
        minus = ctmc_density_derivative(
            physical_ctmc(fold["theta_log_kappa_near_over_far"] - step),
            time_star,
            1,
        )
        finite_difference = (plus - minus) / (2.0 * step)
        rows.append(
            {
                "diagnostic": "CTMC_parameter_sensitivity_check",
                "resolution": step,
                "secondary_resolution": "",
                "error_primary": abs(finite_difference - transversality),
                "error_secondary": "",
                "estimate_primary": finite_difference,
                "estimate_secondary": transversality,
            }
        )
    return rows


def drift_scaling_rows(diffusion: float = 0.1, drift: float = 0.06) -> list[dict]:
    rows: list[dict] = []
    for distance in (5.0, 10.0, 20.0, 40.0, 80.0, 160.0, 320.0):
        drifted = GIGChannel(
            "drifted_boundary_IG",
            distance**2 / (4.0 * diffusion),
            drift**2 / (4.0 * diffusion),
            1.5,
        )
        zero_drift = GIGChannel(
            "zero_drift_boundary_IG",
            distance**2 / (4.0 * diffusion),
            0.0,
            1.5,
        )
        rows.append(
            {
                "distance": distance,
                "drifted_mode": drifted.mode,
                "drifted_mode_over_distance": drifted.mode / distance,
                "ballistic_limit_inverse_speed": 1.0 / drift,
                "zero_drift_mode": zero_drift.mode,
                "zero_drift_mode_over_distance_squared": zero_drift.mode
                / distance**2,
                "diffusive_limit_coefficient": 1.0 / (6.0 * diffusion),
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _jsonable(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)


def _series(
    early: GIGChannel,
    late: GIGChannel,
    lower_fold: dict[str, float],
    physical_fold: dict[str, float],
) -> dict[str, np.ndarray]:
    transport_times = np.linspace(0.1, 400.0, 4000)
    early_density = early.derivatives(transport_times)[0]
    late_density = late.derivatives(transport_times)[0]

    mixture_times = np.linspace(26.5, 30.5, 1601)
    early_values = early.derivatives(mixture_times)
    late_values = late.derivatives(mixture_times)
    early_mixture = early_values[0]
    late_mixture = late_values[0]
    weight = lower_fold["early_weight"]
    mixture_weights = np.asarray([0.65 * weight, weight, 1.35 * weight])
    mixtures = np.vstack(
        [
            p * early_mixture + (1.0 - p) * late_mixture
            for p in mixture_weights
        ]
    )
    mixture_first_derivatives = np.vstack(
        [
            p * early_values[1] + (1.0 - p) * late_values[1]
            for p in mixture_weights
        ]
    )

    local_times = np.linspace(32.0, 43.0, 1101)
    theta_star = physical_fold["theta_log_kappa_near_over_far"]
    theta_offsets = np.asarray([-0.032, 0.0, 0.032])
    local_derivatives = []
    for offset in theta_offsets:
        model = physical_ctmc(theta_star + float(offset))
        states = expm_multiply(
            model.killed_generator.T,
            model.initial,
            start=float(local_times[0]),
            stop=float(local_times[-1]),
            num=local_times.size,
            endpoint=True,
        )
        local_derivatives.append(
            np.einsum(
                "ti,i->t",
                states,
                model.killed_generator @ model.total_rate,
            )
        )

    canonical_times = np.linspace(0.0, 400.0, 1601)
    canonical = physical_ctmc(0.0)
    canonical_states = expm_multiply(
        canonical.killed_generator.T,
        canonical.initial,
        start=0.0,
        stop=400.0,
        num=canonical_times.size,
        endpoint=True,
    )
    canonical_channels = np.einsum(
        "ti,ic->tc", canonical_states, canonical.channel_rates
    )
    return {
        "transport_times": transport_times,
        "early_GIG_density": early_density,
        "late_IG_density": late_density,
        "mixture_times": mixture_times,
        "mixture_weights": mixture_weights,
        "GIG_mixtures": mixtures,
        "GIG_mixture_first_derivatives": mixture_first_derivatives,
        "local_times": local_times,
        "physical_theta_offsets": theta_offsets,
        "physical_local_first_derivatives": np.asarray(local_derivatives),
        "canonical_times": canonical_times,
        "canonical_channel_density": canonical_channels,
    }


def _plot(
    series: dict[str, np.ndarray],
    early: GIGChannel,
    late: GIGChannel,
    lower_fold: dict[str, float],
    physical_fold: dict[str, float],
    continuation: list[dict],
) -> tuple[Path, Path]:
    pdf = FIGURES / "gig_fold_validation.pdf"
    png = FIGURES / "gig_fold_validation.png"
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.8))

    ax = axes[0, 0]
    ax.plot(
        series["transport_times"],
        series["early_GIG_density"],
        color="#d95f02",
        label=f"joint early GIG (mode {early.mode:.1f})",
    )
    ax.plot(
        series["transport_times"],
        series["late_IG_density"],
        color="#1b9e77",
        label=f"boundary IG (mode {late.mode:.1f})",
    )
    ax.plot(
        series["canonical_times"],
        series["canonical_channel_density"][:, 0]
        / np.trapezoid(
            series["canonical_channel_density"][:, 0], series["canonical_times"]
        ),
        color="#e6ab02",
        linestyle="--",
        linewidth=1.2,
        label="near CTMC",
    )
    ax.plot(
        series["canonical_times"],
        series["canonical_channel_density"][:, 1]
        / np.trapezoid(
            series["canonical_channel_density"][:, 1], series["canonical_times"]
        ),
        color="#7570b3",
        linestyle="--",
        linewidth=1.2,
        label="far CTMC",
    )
    ax.set_xlim(0.0, 330.0)
    ax.set_xlabel("time")
    ax.set_ylabel("conditional density")
    ax.set_title("A  Channel-clock screening")
    handles, labels = ax.get_legend_handles_labels()
    labels = ["early GIG", "late GIG", "near CTMC", "far CTMC"]
    ax.legend(handles, labels, frameon=False, fontsize=7.5, ncol=2, loc="upper right")

    ax = axes[0, 1]
    colors = ("#7570b3", "black", "#d95f02")
    labels = ("below fold", "at fold", "above fold")
    for derivative, weight, color, label in zip(
        series["GIG_mixture_first_derivatives"],
        series["mixture_weights"],
        colors,
        labels,
        strict=True,
    ):
        ax.plot(
            series["mixture_times"],
            derivative * 1e9,
            color=color,
            label=f"{label}: p={weight:.2e}",
        )
    ax.axvline(lower_fold["time"], color="0.55", linestyle=":", linewidth=1.0)
    ax.set_xlabel("time")
    ax.axhline(0.0, color="0.55", linewidth=0.8)
    ax.set_ylabel(r"finite-matrix mixture $f_t$ ($\times 10^9$)")
    ax.set_title("B  Fixed-shape GIG fold")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    colors = ("#7570b3", "black", "#d95f02")
    for derivative, offset, color in zip(
        series["physical_local_first_derivatives"],
        series["physical_theta_offsets"],
        colors,
        strict=True,
    ):
        ax.plot(
            series["local_times"],
            derivative * 1e9,
            color=color,
            label=rf"$\theta-\theta_*={offset:+.3f}$",
        )
    ax.axhline(0.0, color="0.55", linewidth=0.8)
    ax.axvline(physical_fold["time"], color="0.55", linestyle=":", linewidth=1.0)
    ax.set_xlim(35.5, 38.8)
    ax.set_ylim(-0.045, 0.25)
    ax.set_xlabel("time")
    ax.set_ylabel(r"finite-matrix $f_t$ ($\times 10^9$)")
    ax.set_title("C  Physical CTMC fold")
    ax.legend(frameon=False, fontsize=8)

    positive = [row for row in continuation if row["side"] == "two-peak-side"]
    deltas = np.asarray([row["delta_theta"] for row in positive], dtype=float)
    separation = np.asarray(
        [row["critical_point_separation"] for row in positive], dtype=float
    )
    prominence = np.asarray([row["local_prominence"] for row in positive], dtype=float)
    predicted_separation = np.asarray(
        [row["normal_form_separation"] for row in positive], dtype=float
    )
    predicted_prominence = np.asarray(
        [row["normal_form_prominence"] for row in positive], dtype=float
    )
    ax = axes[1, 1]
    ax.loglog(deltas, separation, "o", color="#1b9e77", label="separation")
    ax.loglog(
        deltas,
        predicted_separation,
        color="#1b9e77",
        linestyle="--",
        label=r"normal form $\propto\Delta\theta^{1/2}$",
    )
    ax.set_xlabel(r"$\Delta\theta>0$")
    ax.set_ylabel("critical-point separation", color="#1b9e77")
    ax.tick_params(axis="y", labelcolor="#1b9e77")
    twin = ax.twinx()
    twin.loglog(deltas, prominence, "s", color="#d95f02", label="prominence")
    twin.loglog(
        deltas,
        predicted_prominence,
        color="#d95f02",
        linestyle="--",
        label=r"normal form $\propto\Delta\theta^{3/2}$",
    )
    twin.set_ylabel("local prominence", color="#d95f02")
    twin.tick_params(axis="y", labelcolor="#d95f02")
    handles1, labels1 = ax.get_legend_handles_labels()
    handles2, labels2 = twin.get_legend_handles_labels()
    ax.legend(handles1 + handles2, labels1 + labels2, frameon=False, fontsize=7.2)
    ax.set_title("D  Held-out fold scaling")

    enforce_publication_graphics(fig)
    fig.tight_layout()
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return pdf, png


def main() -> None:
    geometry, relative, early, late = geometry_to_channels()
    folds = fixed_shape_folds(early, late)
    if len(folds) != 2:
        raise RuntimeError(f"expected two admissible GIG folds, found {len(folds)}")
    lower_fold = folds[0]

    physical_fold, fold_model = locate_physical_fold()
    continuation, normal_form_fits = physical_continuation(physical_fold)
    convergence = convergence_rows(early, late, physical_fold, continuation)
    scaling = drift_scaling_rows()

    canonical = physical_ctmc(0.0)
    canonical_mode_details = [
        locate_ctmc_channel_mode(canonical, channel, time_max=500.0, scan_points=1001)
        for channel in range(2)
    ]
    canonical_modes = [float(row["time"]) for row in canonical_mode_details]

    gig_rows = [
        {
            "channel": channel.name,
            "A": channel.A,
            "B": channel.B,
            "nu": channel.nu,
            "normalization": channel.normalization,
            "log_normalization": channel.log_normalization,
            "mode": channel.mode,
        }
        for channel in (relative, early, late)
    ]
    fold_rows = [
        {"model": "fixed_shape_GIG", "fold_index": index + 1, **fold}
        for index, fold in enumerate(folds)
    ]
    fold_rows.append(
        {
            "model": "physical_finite_state_CTMC",
            "fold_index": 1,
            "time": physical_fold["time"],
            "early_weight": physical_fold["near_splitting_probability"],
            "determinant_residual": "",
            "mixture_first_derivative": physical_fold["first_derivative"],
            "mixture_second_derivative": physical_fold["second_derivative"],
            "mixture_third_derivative": physical_fold["third_derivative"],
            "weight_transversality": physical_fold["time_parameter_transversality"],
        }
    )

    gig_csv = DATA / "gig_channel_parameters.csv"
    folds_csv = DATA / "gig_fold_points.csv"
    continuation_csv = DATA / "gig_fold_continuation.csv"
    convergence_csv = DATA / "gig_fold_convergence.csv"
    scaling_csv = DATA / "gig_drift_scaling.csv"
    _write_csv(gig_csv, gig_rows)
    _write_csv(folds_csv, fold_rows)
    _write_csv(continuation_csv, continuation)
    _write_csv(convergence_csv, convergence)
    _write_csv(scaling_csv, scaling)

    series = _series(early, late, lower_fold, physical_fold)
    series_npz = DATA / "gig_fold_series.npz"
    np.savez_compressed(series_npz, **series)
    figure_pdf, figure_png = _plot(
        series, early, late, lower_fold, physical_fold, continuation
    )

    summary = {
        "evidence_grade": "validated_finite_state_fold_with_asymptotic_screening",
        "geometry": geometry,
        "channels": {row["channel"]: row for row in gig_rows},
        "fixed_shape_GIG_folds": folds,
        "physical_CTMC_fold": physical_fold,
        "normal_form": normal_form_fits,
        "canonical_channel_comparison": {
            "CTMC_near_mode": canonical_modes[0],
            "CTMC_far_mode": canonical_modes[1],
            "CTMC_near_mode_details": canonical_mode_details[0],
            "CTMC_far_mode_details": canonical_mode_details[1],
            "joint_GIG_early_mode": early.mode,
            "boundary_IG_late_mode": late.mode,
            "early_mode_relative_error": abs(early.mode - canonical_modes[0])
            / canonical_modes[0],
            "late_mode_relative_error": abs(late.mode - canonical_modes[1])
            / canonical_modes[1],
            "GIG_lower_fold_early_weight": lower_fold["early_weight"],
            "CTMC_fold_near_splitting_probability": physical_fold[
                "near_splitting_probability"
            ],
        },
        "controls": {
            "one_peak_side_points": sum(
                row["side"] == "one-peak-side" for row in continuation
            ),
            "two_peak_side_points": sum(
                row["side"] == "two-peak-side" for row in continuation
            ),
            "continuation_points_were_not_used_to_locate_fold": True,
            "time_derivatives": "alpha exp(T t) T^n b",
            "canonical_channel_modes": (
                "largest detected negative-curvature maxima from Brent-refined "
                "alpha exp(T t) T b_channel sign changes within the declared horizon"
            ),
            "parameter_sensitivity": (
                "finite-matrix evaluation of the exact augmented CTMC "
                "sensitivity identity"
            ),
        },
        "claim_boundary": {
            "GIG": "leading narrow-patch/free-motion screening law; no remainder bound claimed",
            "physical_fold": (
                "numerically located nondegenerate fold for the stated finite "
                "L=31 independent-clock CTMC within the declared search domain"
            ),
            "spatial_limit": "no lattice-to-continuum convergence claim is made by this artifact",
            "time_grid": (
                "fold candidate uses finite-matrix semigroup derivative evaluations; "
                "sampled grids provide validation but not exhaustive root isolation"
            ),
        },
    }
    summary_json = DATA / "gig_fold_summary.json"
    summary_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=_jsonable) + "\n",
        encoding="utf-8",
    )

    outputs: list[Path] = [
        summary_json,
        gig_csv,
        folds_csv,
        continuation_csv,
        convergence_csv,
        scaling_csv,
        series_npz,
        figure_pdf,
        figure_png,
    ]
    manifest_path = DATA / "gig_fold.manifest.json"
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=[".venv/bin/python", str(HERE.relative_to(REPO))],
        model_spec={
            "asymptotic_channels": "normalized GIG laws from relative/centre Brownian coordinates",
            "physical_model": "two biased reflecting CTMC walkers with site-dependent killing",
            "lattice_size": LATTICE_SIZE,
            "site_labels": [0, LATTICE_SIZE - 1],
            "walker_interior_attempt_jump_rates": [0.7, 0.2],
            "walker_common_right_bias": 0.3,
            "walker_interior_left_right_rates": [
                [0.245, 0.455],
                [0.07, 0.13],
            ],
            "reflection": "stay: omit out-of-range boundary jumps",
            "product_generator": "L1 kron I + I kron L2",
            "product_state_ordering": "index=x1*lattice_size+x2",
            "start": list(START),
            "catalytic_sites": [NEAR_SITE, FAR_SITE],
            "reactive_pairs": [[NEAR_SITE, NEAR_SITE], [FAR_SITE, FAR_SITE]],
            "kappa_far": KAPPA_FAR,
            "kappa_far_definition": "-log(0.4)",
            "control": "theta=log(kappa_near/kappa_far), kappa_far fixed",
            "root_method": (
                "scipy.optimize.root on finite-matrix semigroup derivative "
                "evaluations within the declared time/control search domain"
            ),
        },
        classifier_spec={
            "fold": "f_t=f_tt=0, f_ttt!=0, f_ttheta!=0",
            "normal_form_tests": "held-out positive and negative delta-theta points",
        },
        dependencies=[
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
            NOTES / "gig_fold_derivation.md",
        ],
        outputs=outputs,
        horizon={
            "canonical_channel_comparison": 500.0,
            "tail_check": 5000.0,
            "GIG_quadrature_interval": [1e-4, 2e4],
        },
    )
    write_manifest(manifest_path, manifest)

    print(
        json.dumps(
            {
                "GIG_lower_fold": folds[0],
                "physical_CTMC_fold": physical_fold,
                "normal_form": normal_form_fits,
                "outputs": [str(path.relative_to(REPO)) for path in outputs],
                "manifest": str(manifest_path.relative_to(REPO)),
            },
            indent=2,
            sort_keys=True,
            default=_jsonable,
        )
    )


if __name__ == "__main__":
    main()
