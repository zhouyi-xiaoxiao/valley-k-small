#!/usr/bin/env python3
"""Result-informed continuum free-exposure exploration for the G1 quotient.

This script is deliberately outside the production pipeline.  It evaluates
the unbounded-longitudinal continuum model on R x T_W from analytic OU and
wrapped-Brownian transition kernels, with deterministic Gaussian quadrature
for the compact initial/patch bumps and the circular contact set.  Time jets
are extracted from the analytic kernels by Cauchy differentiation.

The current and redesigned patch centres were both known before this script
was written.  Consequently every output is RESULT_INFORMED EXPLORATION, not a
preregistered discovery, a finite-B Doi result, or a continuum certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import ndtr

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
CODE = REPORT / "code"
DATA = REPORT / "artifacts" / "data"
DEFAULT_OUTPUT = HERE.with_name("continuum_free_exposure_exploration_result.json")

EVIDENCE_LABEL = "RESULT_INFORMED_EXPLORATION_NOT_FORMAL_EVIDENCE"
CURRENT_CENTRES = (0.48, 0.67, 0.86)
REDESIGNED_CENTRES = (0.37, 0.61, 0.85)


@dataclass(frozen=True)
class PhysicalParameters:
    particle_diffusion: float = 0.0045
    ou_stiffness: float = 0.1
    ou_mean: float = 0.95
    transverse_width: float = 1.0
    contact_radius: float = 0.16
    midpoint_start: float = 0.14
    midpoint_initial_half_width: float = 0.02
    relative_parallel_start: float = -0.35
    relative_perp_start: float = 0.0
    relative_initial_half_width: float = 0.02
    patch_half_width: float = 0.08


@dataclass(frozen=True)
class NumericalConfiguration:
    bump_order: int
    patch_order: int
    contact_angle_order: int
    transverse_fourier_modes: int
    cauchy_samples: int
    cauchy_radius: float


COARSE = NumericalConfiguration(48, 48, 64, 16, 32, 0.55)
PRIMARY = NumericalConfiguration(80, 80, 96, 24, 48, 0.55)
FINE = NumericalConfiguration(112, 112, 144, 32, 64, 0.42)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _base_bump_integral() -> float:
    return float(
        quad(
            lambda u: math.exp(-1.0 / (1.0 - u * u)),
            -1.0,
            1.0,
            epsabs=2.0e-15,
            epsrel=2.0e-14,
            limit=200,
        )[0]
    )


BASE_BUMP_INTEGRAL = _base_bump_integral()


def normalized_bump_rule(order: int) -> tuple[np.ndarray, np.ndarray]:
    """Return u nodes and probability weights for exp[-1/(1-u^2)]."""

    if order < 24:
        raise ValueError("compact-bump quadrature order is too small")
    nodes, weights = leggauss(order)
    values = np.exp(-1.0 / (1.0 - nodes * nodes))
    probability_weights = weights * values / BASE_BUMP_INTEGRAL
    return nodes, probability_weights


def ou_transition_density(
    times: np.ndarray,
    targets: np.ndarray,
    starts: np.ndarray,
    *,
    diffusion_coefficient: float,
    stiffness: float,
    mean: float,
) -> np.ndarray:
    """OU transition density for generator kappa*d_xx-gamma(x-m)*d_x."""

    t = np.asarray(times, dtype=complex)
    if t.ndim != 1 or np.any(np.real(t) <= 0.0):
        raise ValueError("OU kernels require a one-dimensional time array with Re(t)>0")
    target = np.asarray(targets, dtype=float)
    start = np.asarray(starts, dtype=float)
    decay = np.exp(-stiffness * t)
    variance = (diffusion_coefficient / stiffness) * (1.0 - np.exp(-2.0 * stiffness * t))
    conditional_mean = mean + decay[:, None] * (start[None, :] - mean)
    displacement = target[None, :, None] - conditional_mean[:, None, :]
    return np.exp(-(displacement * displacement) / (2.0 * variance[:, None, None])) / np.sqrt(
        2.0 * np.pi * variance[:, None, None]
    )


class ContinuumFreeExposure:
    """Semi-analytic continuum clocks on R x T_W for physical d=2."""

    def __init__(
        self,
        centres: Sequence[float],
        configuration: NumericalConfiguration,
        parameters: PhysicalParameters | None = None,
    ) -> None:
        self.parameters = parameters or PhysicalParameters()
        self.configuration = configuration
        self.centres = np.asarray(tuple(centres), dtype=float)
        if self.centres.shape != (3,) or not np.all(np.diff(self.centres) > 0.0):
            raise ValueError("exactly three strictly ordered patch centres are required")

        bump_nodes, bump_weights = normalized_bump_rule(configuration.bump_order)
        patch_nodes, patch_weights = normalized_bump_rule(configuration.patch_order)
        self.midpoint_starts = (
            self.parameters.midpoint_start
            + self.parameters.midpoint_initial_half_width * bump_nodes
        )
        self.relative_parallel_starts = (
            self.parameters.relative_parallel_start
            + self.parameters.relative_initial_half_width * bump_nodes
        )
        self.bump_weights = bump_weights
        self.patch_targets = (
            self.centres[:, None] + self.parameters.patch_half_width * patch_nodes[None, :]
        )
        self.patch_weights = patch_weights

        angle_nodes, angle_weights = leggauss(configuration.contact_angle_order)
        angle = 0.5 * np.pi * angle_nodes
        self.contact_parallel_targets = self.parameters.contact_radius * np.sin(angle)
        half_chord = self.parameters.contact_radius * np.cos(angle)
        self.contact_parallel_weights = (
            0.5 * np.pi * angle_weights * self.parameters.contact_radius * np.cos(angle)
        )
        self.contact_half_chords = half_chord

        mode_numbers = np.arange(1, configuration.transverse_fourier_modes + 1, dtype=float)
        omega = 2.0 * np.pi / self.parameters.transverse_width
        initial_perp_offsets = self.parameters.relative_initial_half_width * bump_nodes
        self.transverse_mode_numbers = mode_numbers
        self.transverse_eigenvalues = (
            2.0 * self.parameters.particle_diffusion * (omega * mode_numbers) ** 2
        )
        self.transverse_initial_cosine_coefficients = np.asarray(
            [
                np.dot(
                    bump_weights,
                    np.cos(
                        mode * omega * initial_perp_offsets
                        + mode * omega * self.parameters.relative_perp_start
                    ),
                )
                for mode in mode_numbers
            ],
            dtype=float,
        )
        self.transverse_interval_modes = (
            4.0
            / self.parameters.transverse_width
            * np.sin(mode_numbers[:, None] * omega * self.contact_half_chords[None, :])
            / (mode_numbers[:, None] * omega)
        )

    def factors(self, times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return longitudinal patch factors a_j and contact factor c_2."""

        t = np.atleast_1d(np.asarray(times, dtype=complex))
        flattened_targets = self.patch_targets.reshape(-1)
        midpoint_kernel = ou_transition_density(
            t,
            flattened_targets,
            self.midpoint_starts,
            diffusion_coefficient=self.parameters.particle_diffusion / 2.0,
            stiffness=self.parameters.ou_stiffness,
            mean=self.parameters.ou_mean,
        ).reshape(
            len(t),
            len(self.centres),
            self.configuration.patch_order,
            self.configuration.bump_order,
        )
        midpoint = (
            np.einsum(
                "tcvu,u,v->tc",
                midpoint_kernel,
                self.bump_weights,
                self.patch_weights,
                optimize=True,
            )
            / self.parameters.transverse_width
        )

        relative_parallel_kernel = ou_transition_density(
            t,
            self.contact_parallel_targets,
            self.relative_parallel_starts,
            diffusion_coefficient=2.0 * self.parameters.particle_diffusion,
            stiffness=self.parameters.ou_stiffness,
            mean=0.0,
        )
        relative_parallel_density = np.einsum(
            "txu,u->tx", relative_parallel_kernel, self.bump_weights, optimize=True
        )
        transverse_decay = np.exp(-t[:, None] * self.transverse_eigenvalues[None, :])
        transverse_interval_probability = (
            2.0 * self.contact_half_chords[None, :] / self.parameters.transverse_width
            + (transverse_decay * self.transverse_initial_cosine_coefficients[None, :])
            @ self.transverse_interval_modes
        )
        contact = np.einsum(
            "tx,tx,x->t",
            relative_parallel_density,
            transverse_interval_probability,
            self.contact_parallel_weights,
            optimize=True,
        )
        return midpoint, contact

    def channels(self, times: np.ndarray, *, chunk_size: int = 128) -> np.ndarray:
        """Return g_j=a_j*c for arbitrary real or complex time arrays."""

        values = np.atleast_1d(np.asarray(times, dtype=complex))
        output = np.empty((len(values), 3), dtype=complex)
        for start in range(0, len(values), chunk_size):
            stop = min(start + chunk_size, len(values))
            midpoint, contact = self.factors(values[start:stop])
            output[start:stop] = midpoint * contact[:, None]
        return output

    def cauchy_jets(
        self,
        time: float,
        *,
        maximum_order: int = 4,
    ) -> dict[str, Any]:
        """Extract time jets from analytic kernels using a Cauchy circle."""

        value = float(time)
        radius = float(self.configuration.cauchy_radius)
        samples = int(self.configuration.cauchy_samples)
        if value <= radius:
            raise ValueError("Cauchy circle would cross the t=0 singularity")
        angles = 2.0 * np.pi * np.arange(samples, dtype=float) / samples
        circle = value + radius * np.exp(1j * angles)
        midpoint_values, contact_values = self.factors(circle)
        channel_values = midpoint_values * contact_values[:, None]

        def differentiate(samples_by_channel: np.ndarray) -> tuple[np.ndarray, float]:
            samples_array = np.asarray(samples_by_channel, dtype=complex)
            if samples_array.ndim == 1:
                samples_array = samples_array[:, None]
            jets = np.empty((maximum_order + 1, samples_array.shape[1]), dtype=float)
            maximum_imaginary = 0.0
            for order in range(maximum_order + 1):
                phase = np.exp(-1j * order * angles)
                coefficient = np.mean(samples_array * phase[:, None], axis=0) / radius**order
                derivative = math.factorial(order) * coefficient
                jets[order] = np.real(derivative)
                maximum_imaginary = max(
                    maximum_imaginary,
                    float(np.max(np.abs(np.imag(derivative)))),
                )
            return jets, maximum_imaginary

        midpoint_jets, midpoint_imaginary = differentiate(midpoint_values)
        contact_jets_2d, contact_imaginary = differentiate(contact_values)
        channel_jets, channel_imaginary = differentiate(channel_values)
        contact_jets = contact_jets_2d[:, 0]
        leibniz = np.zeros_like(channel_jets)
        for order in range(maximum_order + 1):
            for left_order in range(order + 1):
                leibniz[order] += (
                    math.comb(order, left_order)
                    * midpoint_jets[left_order]
                    * contact_jets[order - left_order]
                )
        return {
            "midpoint": midpoint_jets,
            "contact": contact_jets,
            "channels": channel_jets,
            "maximum_imaginary_residual": max(
                midpoint_imaginary, contact_imaginary, channel_imaginary
            ),
            "maximum_direct_vs_leibniz_difference": float(np.max(np.abs(channel_jets - leibniz))),
        }


def independent_contact_polar_reference(
    model: ContinuumFreeExposure,
    times: Sequence[float] = (1.0, 5.0, 9.0, 20.0),
    *,
    radial_order: int = 64,
    angular_points: int = 256,
) -> dict[str, Any]:
    """Cross-check c_2 by direct polar disk quadrature, without H(h,t)."""

    radial_nodes, radial_weights = leggauss(radial_order)
    radius = 0.5 * model.parameters.contact_radius * (radial_nodes + 1.0)
    radius_weights = 0.5 * model.parameters.contact_radius * radial_weights
    angle = 2.0 * np.pi * np.arange(angular_points, dtype=float) / angular_points
    parallel_targets = (radius[:, None] * np.cos(angle)[None, :]).reshape(-1)
    transverse_targets = (radius[:, None] * np.sin(angle)[None, :]).reshape(-1)
    area_weights = (
        radius_weights[:, None]
        * radius[:, None]
        * np.full((1, angular_points), 2.0 * np.pi / angular_points)
    ).reshape(-1)
    omega = 2.0 * np.pi / model.parameters.transverse_width
    rows = []
    maximum_absolute_difference = 0.0
    maximum_relative_difference = 0.0
    for time in times:
        t = np.asarray((float(time),), dtype=complex)
        parallel_kernel = ou_transition_density(
            t,
            parallel_targets,
            model.relative_parallel_starts,
            diffusion_coefficient=2.0 * model.parameters.particle_diffusion,
            stiffness=model.parameters.ou_stiffness,
            mean=0.0,
        )[0]
        parallel_density = np.real(parallel_kernel @ model.bump_weights)
        mode_decay = np.exp(-float(time) * model.transverse_eigenvalues)
        transverse_density = (
            1.0
            + 2.0
            * np.sum(
                (model.transverse_initial_cosine_coefficients * mode_decay)[:, None]
                * np.cos(
                    model.transverse_mode_numbers[:, None] * omega * transverse_targets[None, :]
                ),
                axis=0,
            )
        ) / model.parameters.transverse_width
        polar_value = float(np.dot(area_weights, parallel_density * transverse_density))
        factor_value = float(np.real(model.factors(t)[1][0]))
        difference = abs(polar_value - factor_value)
        relative = difference / abs(factor_value)
        maximum_absolute_difference = max(maximum_absolute_difference, difference)
        maximum_relative_difference = max(maximum_relative_difference, relative)
        rows.append(
            {
                "time": float(time),
                "half_chord_formula": factor_value,
                "independent_polar_disk_quadrature": polar_value,
                "absolute_difference": difference,
                "relative_difference": relative,
            }
        )
    return {
        "radial_order": radial_order,
        "angular_points": angular_points,
        "transverse_fourier_modes": model.configuration.transverse_fourier_modes,
        "rows": rows,
        "maximum_absolute_difference": maximum_absolute_difference,
        "maximum_relative_difference": maximum_relative_difference,
    }


def unbounded_box_tail_diagnostic(
    parameters: PhysicalParameters,
) -> dict[str, Any]:
    """Maximize free Gaussian tail mass beyond the pilot finite box."""

    times = np.linspace(0.01, 40.0, 4000)

    def maximize(
        *,
        diffusion_coefficient: float,
        mean: float,
        starts: tuple[float, float],
        bounds: tuple[float, float],
    ) -> dict[str, Any]:
        best: dict[str, Any] | None = None
        for start in starts:
            conditional_mean = mean + (start - mean) * np.exp(-parameters.ou_stiffness * times)
            standard_deviation = np.sqrt(
                diffusion_coefficient
                / parameters.ou_stiffness
                * (1.0 - np.exp(-2.0 * parameters.ou_stiffness * times))
            )
            tail = ndtr((bounds[0] - conditional_mean) / standard_deviation) + ndtr(
                (conditional_mean - bounds[1]) / standard_deviation
            )
            index = int(np.argmax(tail))
            candidate = {
                "maximum_tail_probability": float(tail[index]),
                "initial_support_extreme": start,
                "time": float(times[index]),
                "conditional_mean": float(conditional_mean[index]),
                "standard_deviation": float(standard_deviation[index]),
            }
            if (
                best is None
                or candidate["maximum_tail_probability"] > best["maximum_tail_probability"]
            ):
                best = candidate
        if best is None:
            raise AssertionError("tail maximization received no initial points")
        return best

    return {
        "time_grid": {"start": 0.01, "stop": 40.0, "points": len(times)},
        "midpoint": maximize(
            diffusion_coefficient=parameters.particle_diffusion / 2.0,
            mean=parameters.ou_mean,
            starts=(
                parameters.midpoint_start - parameters.midpoint_initial_half_width,
                parameters.midpoint_start + parameters.midpoint_initial_half_width,
            ),
            bounds=(-0.25, 1.85),
        ),
        "relative_parallel": maximize(
            diffusion_coefficient=2.0 * parameters.particle_diffusion,
            mean=0.0,
            starts=(
                parameters.relative_parallel_start - parameters.relative_initial_half_width,
                parameters.relative_parallel_start + parameters.relative_initial_half_width,
            ),
            bounds=(-1.8, 1.8),
        ),
        "interpretation": (
            "zero-order free-law tail diagnostic only; not a mixed-jet "
            "reflecting-boundary error bound"
        ),
    }


def row_normalized_determinant(jets: np.ndarray) -> float:
    rows = np.asarray(jets[1:4], dtype=float)
    norms = np.linalg.norm(rows, axis=1)
    if np.any(norms <= 0.0):
        raise FloatingPointError("zero row in cusp determinant")
    return float(np.linalg.det(rows / norms[:, None]))


def cusp_metrics(jets: np.ndarray, time: float) -> dict[str, Any]:
    derivative_matrix = np.asarray(jets[1:4], dtype=float)
    _u, singular_values, vh = np.linalg.svd(derivative_matrix)
    weights = vh[-1].copy()
    if np.sum(weights) < 0.0:
        weights = -weights
    weights /= np.sum(weights)
    mixture = np.asarray(jets, dtype=float) @ weights
    density = float(mixture[0])
    control_directions = np.asarray(((1.0, 0.0, -1.0), (0.0, 1.0, -1.0)))
    raw_unfolding = np.asarray(
        [[float(direction @ jets[order]) for direction in control_directions] for order in (1, 2)]
    )
    dimensionless_unfolding = np.diag((time / density, time**2 / density)) @ raw_unfolding
    unfolding_singular_values = np.linalg.svd(dimensionless_unfolding, compute_uv=False)
    row_norms = np.linalg.norm(dimensionless_unfolding, axis=1)
    determinant_prime = float(np.linalg.det(jets[[1, 2, 4]]))
    return {
        "time": float(time),
        "weights": weights.tolist(),
        "minimum_weight": float(np.min(weights)),
        "density_per_unit_budget": density,
        "mixture_jets_orders_0_to_4": mixture.tolist(),
        "scaled_residuals_orders_1_to_3": [
            float(abs(mixture[order]) * time**order / density) for order in (1, 2, 3)
        ],
        "scaled_fourth_derivative": float(mixture[4] * time**4 / density),
        "derivative_matrix_singular_values": singular_values.tolist(),
        "row_normalized_determinant": row_normalized_determinant(jets),
        "determinant_time_derivative_via_g1_g2_g4": determinant_prime,
        "unfolding": {
            "raw_matrix": raw_unfolding.tolist(),
            "dimensionless_matrix": dimensionless_unfolding.tolist(),
            "dimensionless_singular_values": unfolding_singular_values.tolist(),
            "dimensionless_svd_ratio": float(
                unfolding_singular_values[-1] / unfolding_singular_values[0]
            ),
            "row_angle_sine_magnitude": float(
                abs(np.linalg.det(dimensionless_unfolding / row_norms[:, None]))
            ),
            "rank": int(
                np.linalg.matrix_rank(
                    dimensionless_unfolding,
                    tol=1.0e-12 * unfolding_singular_values[0],
                )
            ),
        },
    }


def locate_cusp(
    model: ContinuumFreeExposure,
    bracket: tuple[float, float],
) -> tuple[dict[str, Any], dict[str, Any]]:
    def determinant(time: float) -> float:
        return row_normalized_determinant(model.cauchy_jets(time)["channels"])

    endpoint_values = [determinant(bracket[0]), determinant(bracket[1])]
    if endpoint_values[0] * endpoint_values[1] >= 0.0:
        raise RuntimeError(
            f"determinant bracket {bracket} lacks a strict sign change: {endpoint_values}"
        )
    root = float(brentq(determinant, *bracket, xtol=4.0e-12, rtol=2.0e-14))
    jet_payload = model.cauchy_jets(root)
    metrics = cusp_metrics(jet_payload["channels"], root)
    diagnostics = {
        "bracket": list(bracket),
        "row_normalized_determinant_at_bracket": endpoint_values,
        "maximum_imaginary_cauchy_residual": jet_payload["maximum_imaginary_residual"],
        "maximum_direct_vs_leibniz_difference": jet_payload["maximum_direct_vs_leibniz_difference"],
        "midpoint_jets_orders_0_to_4_by_channel": jet_payload["midpoint"].tolist(),
        "contact_jets_orders_0_to_4": jet_payload["contact"].tolist(),
        "channel_jets_orders_0_to_4_by_channel": jet_payload["channels"].tolist(),
    }
    return metrics, diagnostics


def inward_weights(cusp: dict[str, Any], step: float = 0.005) -> dict[str, Any]:
    weights = np.asarray(cusp["weights"], dtype=float)
    raw_unfolding = np.asarray(cusp["unfolding"]["raw_matrix"], dtype=float)
    direction = np.asarray((raw_unfolding[0, 1], -raw_unfolding[0, 0]), dtype=float)
    direction /= np.linalg.norm(direction)
    cubic_coefficient = float(cusp["mixture_jets_orders_0_to_4"][4]) / 6.0
    if float(raw_unfolding[1] @ direction) * cubic_coefficient >= 0.0:
        direction = -direction
    perturbed = weights.copy()
    perturbed[:2] += step * direction
    perturbed[2] = 1.0 - float(np.sum(perturbed[:2]))
    return {
        "step": step,
        "control_direction_2d": direction.tolist(),
        "control_direction_3d": [
            float(direction[0]),
            float(direction[1]),
            float(-direction[0] - direction[1]),
        ],
        "second_unfolding_row_projection": float(raw_unfolding[1] @ direction),
        "normal_form_cubic_coefficient": cubic_coefficient,
        "weights": perturbed.tolist(),
    }


def stationary_roots_from_sample(
    model: ContinuumFreeExposure,
    weights: np.ndarray,
    *,
    start: float = 0.5,
    stop: float = 40.0,
    spacing: float = 0.002,
) -> dict[str, Any]:
    times = np.arange(start, stop + 0.5 * spacing, spacing)
    density = np.real(model.channels(times) @ weights)
    sampled_derivative = np.gradient(density, spacing, edge_order=2)
    sign_change_indices = np.flatnonzero(sampled_derivative[:-1] * sampled_derivative[1:] < 0.0)

    def derivative(time: float) -> float:
        return float(model.cauchy_jets(time)["channels"][1] @ weights)

    roots: list[dict[str, Any]] = []
    for index in sign_change_indices:
        left = max(start, float(times[index] - 3.0 * spacing))
        right = min(stop, float(times[index + 1] + 3.0 * spacing))
        left_value = derivative(left)
        right_value = derivative(right)
        if left_value * right_value >= 0.0:
            continue
        root = float(brentq(derivative, left, right, xtol=5.0e-11, rtol=1.0e-13))
        if roots and abs(root - roots[-1]["time"]) < 2.0e-7:
            continue
        jets = model.cauchy_jets(root)["channels"] @ weights
        if jets[0] < 1.0e-12 * float(np.max(density)):
            continue
        roots.append(
            {
                "time": root,
                "topology": "maximum" if jets[2] < 0.0 else "minimum",
                "density": float(jets[0]),
                "scaled_first_derivative_residual": float(abs(root * jets[1] / jets[0])),
                "scaled_second_derivative": float(root**2 * jets[2] / jets[0]),
            }
        )
    return {
        "time_grid": {
            "start": start,
            "stop": stop,
            "spacing": spacing,
            "points": len(times),
        },
        "weights": weights.tolist(),
        "stationary_root_count": len(roots),
        "maximum_count": sum(row["topology"] == "maximum" for row in roots),
        "minimum_count": sum(row["topology"] == "minimum" for row in roots),
        "topology": [row["topology"] for row in roots],
        "roots": roots,
        "sampled_peak_density": float(np.max(density)),
    }


def continuum_inward_step_screen(
    model: ContinuumFreeExposure,
    cusp: dict[str, Any],
) -> dict[str, Any]:
    """Screen topology as distance into the cusp wedge changes."""

    inward = inward_weights(cusp)
    base_weights = np.asarray(cusp["weights"], dtype=float)
    direction = np.asarray(inward["control_direction_3d"], dtype=float)
    spacing = 0.001
    times = np.arange(0.5, 20.0 + 0.5 * spacing, spacing)
    channel_density = np.real(model.channels(times))
    channel_derivative = np.gradient(channel_density, spacing, axis=0, edge_order=2)
    rows = []
    for step in (5.0e-5, 5.0e-4, 1.0e-3, 2.0e-3, 5.0e-3):
        weights = base_weights + step * direction
        derivative = channel_derivative @ weights
        indices = np.flatnonzero(derivative[:-1] * derivative[1:] < 0.0)
        roots = [
            {
                "sampled_time": float(0.5 * (times[index] + times[index + 1])),
                "topology": "maximum" if derivative[index] > 0.0 else "minimum",
            }
            for index in indices
        ]
        rows.append(
            {
                "normal_step": step,
                "weights": weights.tolist(),
                "sampled_stationary_root_count": len(roots),
                "sampled_maximum_count": sum(row["topology"] == "maximum" for row in roots),
                "roots": roots,
            }
        )
    return {
        "time_grid": {
            "start": 0.5,
            "stop": 20.0,
            "spacing": spacing,
            "points": len(times),
        },
        "interpretation": (
            "sampled topology screen in the continuum cusp-normal coordinate; "
            "the selected step is root-refined separately"
        ),
        "rows": rows,
    }


def continuum_geometry(
    centres: tuple[float, float, float],
    bracket: tuple[float, float],
    configuration: NumericalConfiguration,
    *,
    include_modes: bool,
) -> dict[str, Any]:
    model = ContinuumFreeExposure(centres, configuration)
    cusp, jets = locate_cusp(model, bracket)
    inward = inward_weights(cusp)
    result: dict[str, Any] = {
        "centres": list(centres),
        "configuration": asdict(configuration),
        "cusp": cusp,
        "factor_jets_at_cusp": jets,
        "inward_control": inward,
    }
    if include_modes:
        result["inward_stationary_structure"] = stationary_roots_from_sample(
            model, np.asarray(inward["weights"], dtype=float)
        )
        result["inward_step_screen"] = continuum_inward_step_screen(model, cusp)
    return result


def convergence_rows(
    centres: tuple[float, float, float],
    bracket: tuple[float, float],
) -> list[dict[str, Any]]:
    rows = []
    for label, configuration in (
        ("coarse", COARSE),
        ("primary", PRIMARY),
        ("fine", FINE),
    ):
        model = ContinuumFreeExposure(centres, configuration)
        cusp, diagnostics = locate_cusp(model, bracket)
        rows.append(
            {
                "label": label,
                "configuration": asdict(configuration),
                "cusp_time": cusp["time"],
                "weights": cusp["weights"],
                "scaled_fourth_derivative": cusp["scaled_fourth_derivative"],
                "unfolding_svd_ratio": cusp["unfolding"]["dimensionless_svd_ratio"],
                "minimum_weight": cusp["minimum_weight"],
                "maximum_scaled_cusp_residual": max(cusp["scaled_residuals_orders_1_to_3"]),
                "maximum_imaginary_cauchy_residual": diagnostics[
                    "maximum_imaginary_cauchy_residual"
                ],
                "maximum_direct_vs_leibniz_difference": diagnostics[
                    "maximum_direct_vs_leibniz_difference"
                ],
            }
        )
    fine = rows[-1]
    for row in rows[:-1]:
        row["absolute_difference_from_fine"] = {
            "cusp_time": abs(row["cusp_time"] - fine["cusp_time"]),
            "weights_linf": float(
                np.max(np.abs(np.asarray(row["weights"]) - np.asarray(fine["weights"])))
            ),
            "scaled_fourth_derivative": abs(
                row["scaled_fourth_derivative"] - fine["scaled_fourth_derivative"]
            ),
            "unfolding_svd_ratio": abs(row["unfolding_svd_ratio"] - fine["unfolding_svd_ratio"]),
        }
    fine["absolute_difference_from_fine"] = {
        "cusp_time": 0.0,
        "weights_linf": 0.0,
        "scaled_fourth_derivative": 0.0,
        "unfolding_svd_ratio": 0.0,
    }
    return rows


def _finite_volume_factors(
    centres: tuple[float, float, float],
    shape: tuple[int, int, int] = (65, 65, 49),
) -> Any:
    sys.path.insert(0, str(CODE))
    import continuum_g1_smoke as smoke  # noqa: PLC0415
    import continuum_weak_budget_design as discrete  # noqa: PLC0415

    grid = discrete.FactorGrid(*shape)
    factors = discrete.build_free_exposure_factors(grid)
    if np.allclose(centres, smoke.PilotParameters().patch_centres, rtol=0.0, atol=0.0):
        return factors
    parameters = smoke.PilotParameters()
    quotient = smoke.QuotientGrid2D(
        midpoint_cells=grid.midpoint_cells,
        relative_parallel_cells=grid.relative_parallel_cells,
        relative_perp_cells=grid.relative_perp_cells,
        midpoint_bounds=parameters.midpoint_bounds,
        relative_parallel_bounds=parameters.relative_parallel_bounds,
        transverse_width=parameters.transverse_width,
    )
    profiles = []
    for centre in centres:
        masses, _error = smoke.bump_cell_masses(
            quotient.midpoint_edges,
            centre=centre,
            half_width=parameters.patch_half_widths[0],
        )
        profiles.append(masses / quotient.midpoint_spacing)
    patch_profiles = np.asarray(profiles, dtype=float)
    midpoint_actions = discrete._action_columns(  # noqa: SLF001
        factors.midpoint_generator,
        patch_profiles.T / parameters.transverse_width,
        maximum_order=4,
    )
    return replace(
        factors,
        patch_profiles=patch_profiles,
        midpoint_actions=midpoint_actions,
    )


def finite_volume_geometry(
    centres: tuple[float, float, float],
    bracket: tuple[float, float],
    shape: tuple[int, int, int] = (65, 65, 49),
) -> dict[str, Any]:
    sys.path.insert(0, str(CODE))
    import continuum_weak_budget_design as discrete  # noqa: PLC0415

    factors = _finite_volume_factors(centres, shape)

    def jets(time: float) -> np.ndarray:
        return discrete.factorized_channel_point(factors, time)

    def determinant(time: float) -> float:
        return row_normalized_determinant(jets(time))

    endpoint_values = [determinant(bracket[0]), determinant(bracket[1])]
    root = float(brentq(determinant, *bracket, xtol=4.0e-12, rtol=2.0e-14))
    cusp = cusp_metrics(jets(root), root)
    inward = inward_weights(cusp)
    times = np.linspace(0.0, 40.0, 8001)
    curves = discrete.factorized_channel_curves(factors, times, chunk_points=201)
    weights = np.asarray(inward["weights"], dtype=float)
    derivative_curve = curves[1] @ weights
    brackets = []
    for left, right, left_value, right_value in zip(
        times[:-1],
        times[1:],
        derivative_curve[:-1],
        derivative_curve[1:],
        strict=True,
    ):
        if left >= 0.5 and left_value * right_value < 0.0:
            brackets.append((float(left), float(right)))
    roots = []
    for left, right in brackets:
        root_time = float(
            brentq(
                lambda time: float(jets(time)[1] @ weights),
                left,
                right,
                xtol=5.0e-11,
                rtol=1.0e-13,
            )
        )
        mixture = jets(root_time) @ weights
        roots.append(
            {
                "time": root_time,
                "topology": "maximum" if mixture[2] < 0.0 else "minimum",
                "scaled_first_derivative_residual": float(abs(root_time * mixture[1] / mixture[0])),
                "scaled_second_derivative": float(root_time**2 * mixture[2] / mixture[0]),
            }
        )
    return {
        "centres": list(centres),
        "mesh": list(shape),
        "state_count_if_formed": int(np.prod(shape)),
        "determinant_at_bracket": endpoint_values,
        "cusp": cusp,
        "inward_control": inward,
        "inward_stationary_structure": {
            "stationary_root_count": len(roots),
            "maximum_count": sum(row["topology"] == "maximum" for row in roots),
            "minimum_count": sum(row["topology"] == "minimum" for row in roots),
            "topology": [row["topology"] for row in roots],
            "roots": roots,
        },
    }


def finite_volume_cusp_refinement(
    centres: tuple[float, float, float],
    bracket: tuple[float, float],
) -> list[dict[str, Any]]:
    """Track the discrete factorized cusp toward the analytic continuum."""

    sys.path.insert(0, str(CODE))
    import continuum_weak_budget_design as discrete  # noqa: PLC0415

    rows = []
    for shape in ((65, 65, 49), (81, 81, 65), (97, 97, 81), (113, 113, 97)):
        factors = _finite_volume_factors(centres, shape)

        def jets(time: float) -> np.ndarray:
            return discrete.factorized_channel_point(factors, time)

        def determinant(time: float) -> float:
            return row_normalized_determinant(jets(time))

        endpoint_values = [determinant(bracket[0]), determinant(bracket[1])]
        root = float(brentq(determinant, *bracket, xtol=4.0e-12, rtol=2.0e-14))
        cusp = cusp_metrics(jets(root), root)
        inward = inward_weights(cusp)
        base_weights = np.asarray(cusp["weights"], dtype=float)
        direction = np.asarray(inward["control_direction_3d"], dtype=float)
        sample_times = np.linspace(0.0, 20.0, 4001)
        curves = discrete.factorized_channel_curves(factors, sample_times, chunk_points=201)
        step_screen = []
        for step in (5.0e-5, 5.0e-4, 1.0e-3, 2.0e-3, 5.0e-3):
            weights = base_weights + step * direction
            derivative = curves[1] @ weights
            indices = np.flatnonzero(
                (sample_times[:-1] >= 0.5) & (derivative[:-1] * derivative[1:] < 0.0)
            )
            stationary_rows = [
                {
                    "sampled_time": float(0.5 * (sample_times[index] + sample_times[index + 1])),
                    "topology": ("maximum" if curves[2, index] @ weights < 0.0 else "minimum"),
                }
                for index in indices
            ]
            step_screen.append(
                {
                    "normal_step": step,
                    "weights": weights.tolist(),
                    "sampled_stationary_root_count": len(stationary_rows),
                    "sampled_maximum_count": sum(
                        row["topology"] == "maximum" for row in stationary_rows
                    ),
                    "roots": stationary_rows,
                }
            )
        rows.append(
            {
                "mesh": list(shape),
                "state_count_if_formed": int(np.prod(shape)),
                "determinant_at_bracket": endpoint_values,
                "cusp_time": cusp["time"],
                "weights": cusp["weights"],
                "scaled_fourth_derivative": cusp["scaled_fourth_derivative"],
                "unfolding_svd_ratio": cusp["unfolding"]["dimensionless_svd_ratio"],
                "minimum_weight": cusp["minimum_weight"],
                "maximum_scaled_cusp_residual": max(cusp["scaled_residuals_orders_1_to_3"]),
                "inward_normal_direction_3d": direction.tolist(),
                "inward_step_screen": {
                    "time_grid": {
                        "start": 0.0,
                        "stop": 20.0,
                        "spacing": 0.005,
                        "points": 4001,
                    },
                    "interpretation": (
                        "sampled topology screen in each mesh's own cusp-normal "
                        "coordinate; not exhaustive root isolation"
                    ),
                    "rows": step_screen,
                },
            }
        )
    return rows


def comparison(continuum: dict[str, Any], finite_volume: dict[str, Any]) -> dict[str, Any]:
    continuum_cusp = continuum["cusp"]
    discrete_cusp = finite_volume["cusp"]
    continuum_roots = continuum["inward_stationary_structure"]["roots"]
    discrete_roots = finite_volume["inward_stationary_structure"]["roots"]
    paired_root_differences = []
    if len(continuum_roots) == len(discrete_roots):
        paired_root_differences = [
            abs(left["time"] - right["time"])
            for left, right in zip(continuum_roots, discrete_roots, strict=True)
        ]
    return {
        "continuum_minus_finite_volume": {
            "cusp_time": continuum_cusp["time"] - discrete_cusp["time"],
            "weights": (
                np.asarray(continuum_cusp["weights"]) - np.asarray(discrete_cusp["weights"])
            ).tolist(),
            "weights_linf": float(
                np.max(
                    np.abs(
                        np.asarray(continuum_cusp["weights"]) - np.asarray(discrete_cusp["weights"])
                    )
                )
            ),
            "scaled_fourth_derivative": (
                continuum_cusp["scaled_fourth_derivative"]
                - discrete_cusp["scaled_fourth_derivative"]
            ),
            "unfolding_svd_ratio": (
                continuum_cusp["unfolding"]["dimensionless_svd_ratio"]
                - discrete_cusp["unfolding"]["dimensionless_svd_ratio"]
            ),
        },
        "same_stationary_root_count": len(continuum_roots) == len(discrete_roots),
        "same_topology": [row["topology"] for row in continuum_roots]
        == [row["topology"] for row in discrete_roots],
        "paired_root_time_absolute_differences": paired_root_differences,
        "maximum_paired_root_time_absolute_difference": (
            max(paired_root_differences) if paired_root_differences else None
        ),
    }


def run(*, skip_discrete: bool = False) -> dict[str, Any]:
    current = continuum_geometry(CURRENT_CENTRES, (8.5, 10.5), FINE, include_modes=True)
    redesigned = continuum_geometry(REDESIGNED_CENTRES, (8.0, 9.5), FINE, include_modes=True)
    audit_model = ContinuumFreeExposure(CURRENT_CENTRES, FINE)
    result: dict[str, Any] = {
        "schema_version": 1,
        "stage": "G1x_continuum_free_exposure_result_informed_exploration",
        "status": EVIDENCE_LABEL,
        "claim_flags": {
            "preregistered_discovery": False,
            "continuum_verified": False,
            "finite_B_Doi_verified": False,
            "project_gate_passed": False,
        },
        "model": {
            "physical_dimension": 2,
            "domain": "R longitudinal x T_W transverse; unbounded OU kernels",
            "free_generator": (
                "midpoint OU (kappa=D/2) plus relative-parallel OU "
                "(kappa=2D) plus transverse periodic Brownian (kappa=2D)"
            ),
            "contact": "exact disk indicator in relative coordinates",
            "compact_profiles": "normalized C-infinity exp[-1/(1-u^2)] bumps",
            "parameters": asdict(PhysicalParameters()),
            "factorization": "g_j(t)=a_j(t)c_2(t)",
            "time_jet_method": "Cauchy differentiation of analytic transition kernels",
        },
        "continuum": {
            "current_geometry": current,
            "redesigned_geometry": redesigned,
        },
        "quadrature_and_cauchy_convergence": {
            "current_geometry": convergence_rows(CURRENT_CENTRES, (8.5, 10.5)),
            "redesigned_geometry": convergence_rows(REDESIGNED_CENTRES, (8.0, 9.5)),
        },
        "analytic_kernel_audits": {
            "compact_bump_probability_weight_sum": float(np.sum(audit_model.bump_weights)),
            "compact_patch_probability_weight_sum": float(np.sum(audit_model.patch_weights)),
            "contact_half_chord_vs_independent_polar_disk": (
                independent_contact_polar_reference(audit_model)
            ),
            "unbounded_free_law_box_tail": unbounded_box_tail_diagnostic(audit_model.parameters),
        },
        "interpretation": {
            "current_geometry": (
                "A nondegenerate free-exposure cusp survives removal of the 65-grid, "
                "but its inward control has only two maxima."
            ),
            "redesigned_geometry": (
                "The result-informed redesigned centres retain a positive-weight cusp "
                "and an inward five-root max-min-max-min-max structure in the direct "
                "continuum kernels, hence a trimodal free-exposure mixture."
            ),
        },
        "limitations": [
            "both geometries and approximate cusp locations were known before this calculation",
            "the unbounded longitudinal OU model is the intended R x T_W continuum, not the bounded reflecting box used by the finite-volume pilot",
            "the calculation concerns only the B=0 derivative per unit installed budget",
            "no explicit positive-B persistence radius is computed",
            "no interval-arithmetic root isolation or certified quadrature bound is supplied",
            "the 65-grid cusp shift is wider than the thinnest trimodal wedge, so the same absolute catalyst weights are not yet pointwise grid-stable",
            "finite-volume cusp-normal topology is nonmonotone under coarse grid alignment even though the cusp coordinates trend toward the analytic continuum",
            "no physical d=3 calculation is included",
        ],
        "next_formal_study": [
            "prospectively freeze the redesigned centres and all quadrature/root margins",
            "add interval or ball arithmetic for the determinant root, positive null vector, fourth jet, unfolding rank, and all five stationary roots",
            "bound finite-box reflection tails and numerical quadrature/Fourier truncation errors",
            "freeze odd/even mesh sequences and continue both cusp coordinates and the two neighboring fold sheets, not only one chosen weight",
            "combine those margins with the weak-budget persistence theorem to choose a defensible positive B range",
            "then run independent finite-B continuum solvers and a d=3 sphere-contact extension",
        ],
        "provenance": {
            "script": str(HERE.relative_to(REPORT)),
            "script_sha256_before_output": sha256(HERE),
            "finite_volume_reference_artifact": str(
                (DATA / "continuum_weak_budget_design_result.json").relative_to(REPORT)
            ),
        },
    }
    if not skip_discrete:
        current_discrete = finite_volume_geometry(CURRENT_CENTRES, (8.5, 10.5))
        redesigned_discrete = finite_volume_geometry(REDESIGNED_CENTRES, (8.0, 9.5))
        result["finite_volume_65x65x49_crosscheck"] = {
            "evidence_status": "COMPARISON_ONLY_NOT_NEW_PRODUCTION_ARTIFACT",
            "current_geometry": current_discrete,
            "redesigned_geometry": redesigned_discrete,
        }
        result["continuum_vs_finite_volume"] = {
            "current_geometry": comparison(current, current_discrete),
            "redesigned_geometry": comparison(redesigned, redesigned_discrete),
        }
        result["finite_volume_cusp_refinement"] = {
            "interpretation": (
                "factorized free-exposure refinement only; the rows are not a "
                "formal odd/even continuum certificate"
            ),
            "current_geometry": finite_volume_cusp_refinement(CURRENT_CENTRES, (8.5, 10.5)),
            "redesigned_geometry": finite_volume_cusp_refinement(REDESIGNED_CENTRES, (8.0, 9.5)),
        }
    return result


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-discrete", action="store_true")
    args = parser.parse_args(argv)
    payload = run(skip_discrete=args.skip_discrete)
    write_json(args.output, payload)
    for label in ("current_geometry", "redesigned_geometry"):
        row = payload["continuum"][label]
        cusp = row["cusp"]
        structure = row["inward_stationary_structure"]
        print(
            f"{label}: t_c={cusp['time']:.12g}, weights={cusp['weights']}, "
            f"scaled_f4={cusp['scaled_fourth_derivative']:.6g}, "
            f"roots={structure['stationary_root_count']}, "
            f"maxima={structure['maximum_count']}"
        )
    print(f"status={payload['status']}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
