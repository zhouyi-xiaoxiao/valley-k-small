#!/usr/bin/env python3
"""Frozen result-informed confirmation of an observable four-patch continuum design.

The producer evaluates exact unbounded OU x periodic free kernels for the
physical d=2 slab quotient.  It confirms a four-channel cusp on the affine
slice w_0=0.28 and applies a prospectively frozen inward-step selection rule.

The geometry and approximate cusp were known before the manifest was frozen.
This is therefore not preregistered discovery, not a finite-B killed-Doi
calculation, and not a passed project or publication gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import scipy
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.optimize import brentq

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "continuum_observable_four_patch_manifest.json"
OUTPUT = DATA / "continuum_observable_four_patch_result.json"
TEST_FILE = HERE.with_name("test_continuum_observable_four_patch.py")
PROTOCOL = REPORT / "notes" / "observable_four_patch_protocol.md"

EVIDENCE_TIMING = "RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY"
RESULT_STATUS = "PASS_RESULT_INFORMED_OBSERVABLE_FREE_EXPOSURE_CONFIRMATION"


@dataclass(frozen=True)
class PhysicalParameters:
    particle_diffusion: float = 0.002
    ou_stiffness: float = 0.1
    ou_mean: float = 0.95
    transverse_width: float = 1.0
    contact_radius: float = 0.16
    midpoint_start: float = 0.14
    initial_half_width: float = 0.004
    relative_parallel_start: float = -0.35
    relative_perp_start: float = 0.0
    patch_centres: tuple[float, float, float, float] = (0.35, 0.60, 0.75, 0.90)
    patch_half_width: float = 0.008
    fixed_first_weight: float = 0.28


@dataclass(frozen=True)
class NumericalConfiguration:
    bump_order: int
    patch_order: int
    contact_angle_order: int
    transverse_fourier_modes: int
    cauchy_samples: int
    cauchy_radius: float


COARSE = NumericalConfiguration(72, 72, 112, 28, 48, 0.50)
PRIMARY = NumericalConfiguration(104, 104, 160, 40, 64, 0.40)
FINE = NumericalConfiguration(136, 136, 208, 52, 80, 0.30)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if type(value) is not dict:
        raise ValueError(f"{path} must contain one JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def require_repository_venv() -> None:
    expected = (REPOSITORY / ".venv").resolve()
    if Path(sys.prefix).resolve() != expected:
        raise RuntimeError("four-patch confirmation must run inside the repository .venv")


def _base_bump_integral() -> float:
    return float(
        quad(
            lambda value: math.exp(-1.0 / (1.0 - value * value)),
            -1.0,
            1.0,
            epsabs=2.0e-15,
            epsrel=2.0e-14,
            limit=200,
        )[0]
    )


BASE_BUMP_INTEGRAL = _base_bump_integral()


def normalized_bump_rule(order: int) -> tuple[np.ndarray, np.ndarray]:
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

    time_values = np.atleast_1d(np.asarray(times, dtype=complex))
    if np.any(np.real(time_values) <= 0.0):
        raise ValueError("OU kernels require Re(t)>0")
    target_values = np.asarray(targets, dtype=float)
    start_values = np.asarray(starts, dtype=float)
    decay = np.exp(-stiffness * time_values)
    variance = (diffusion_coefficient / stiffness) * (1.0 - np.exp(-2.0 * stiffness * time_values))
    conditional_mean = mean + decay[:, None] * (start_values[None, :] - mean)
    displacement = target_values[None, :, None] - conditional_mean[:, None, :]
    return np.exp(-(displacement * displacement) / (2.0 * variance[:, None, None])) / np.sqrt(
        2.0 * np.pi * variance[:, None, None]
    )


def ou_density_and_first_derivative(
    times: np.ndarray,
    targets: np.ndarray,
    starts: np.ndarray,
    *,
    diffusion_coefficient: float,
    stiffness: float,
    mean: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return real OU density and its exact first time derivative."""

    time_values = np.atleast_1d(np.asarray(times, dtype=float))
    if np.any(time_values <= 0.0):
        raise ValueError("real OU kernels require t>0")
    target_values = np.asarray(targets, dtype=float)
    start_values = np.asarray(starts, dtype=float)
    decay = np.exp(-stiffness * time_values)
    decay_two = np.exp(-2.0 * stiffness * time_values)
    variance = (diffusion_coefficient / stiffness) * (1.0 - decay_two)
    variance_derivative = 2.0 * diffusion_coefficient * decay_two
    conditional_mean = mean + decay[:, None] * (start_values[None, :] - mean)
    displacement = target_values[None, :, None] - conditional_mean[:, None, :]
    displacement_derivative = (stiffness * decay[:, None] * (start_values[None, :] - mean))[
        :, None, :
    ]
    density = np.exp(-(displacement * displacement) / (2.0 * variance[:, None, None])) / np.sqrt(
        2.0 * np.pi * variance[:, None, None]
    )
    log_derivative = (
        -0.5 * variance_derivative[:, None, None] / variance[:, None, None]
        - displacement * displacement_derivative / variance[:, None, None]
        + 0.5
        * displacement
        * displacement
        * variance_derivative[:, None, None]
        / (variance[:, None, None] ** 2)
    )
    return density, density * log_derivative


class FourPatchContinuum:
    """Exact free-exposure clocks on R x T_W for physical d=2."""

    def __init__(
        self,
        configuration: NumericalConfiguration,
        parameters: PhysicalParameters | None = None,
    ) -> None:
        self.configuration = configuration
        self.parameters = parameters or PhysicalParameters()
        pars = self.parameters
        centres = np.asarray(pars.patch_centres, dtype=float)
        if centres.shape != (4,) or not np.all(np.diff(centres) > 0.0):
            raise ValueError("four strictly ordered patch centres are required")
        if pars.contact_radius >= 0.5 * pars.transverse_width:
            raise ValueError("contact disk reaches the torus cut locus")
        if not 0.0 < pars.fixed_first_weight < 1.0:
            raise ValueError("fixed_first_weight must be strictly between zero and one")

        bump_nodes, bump_weights = normalized_bump_rule(configuration.bump_order)
        patch_nodes, patch_weights = normalized_bump_rule(configuration.patch_order)
        self.bump_nodes = bump_nodes
        self.bump_weights = bump_weights
        self.patch_nodes = patch_nodes
        self.patch_weights = patch_weights
        self.midpoint_starts = pars.midpoint_start + pars.initial_half_width * bump_nodes
        self.relative_parallel_starts = (
            pars.relative_parallel_start + pars.initial_half_width * bump_nodes
        )
        self.patch_targets = centres[:, None] + pars.patch_half_width * patch_nodes[None, :]

        angle_nodes, angle_weights = leggauss(configuration.contact_angle_order)
        angle = 0.5 * np.pi * angle_nodes
        self.contact_parallel_targets = pars.contact_radius * np.sin(angle)
        self.contact_half_chords = pars.contact_radius * np.cos(angle)
        self.contact_parallel_weights = (
            0.5 * np.pi * angle_weights * pars.contact_radius * np.cos(angle)
        )

        mode_numbers = np.arange(1, configuration.transverse_fourier_modes + 1, dtype=float)
        omega = 2.0 * np.pi / pars.transverse_width
        transverse_starts = pars.relative_perp_start + pars.initial_half_width * bump_nodes
        self.mode_numbers = mode_numbers
        self.omega = omega
        self.transverse_eigenvalues = 2.0 * pars.particle_diffusion * (omega * mode_numbers) ** 2
        self.transverse_initial_cosine_coefficients = np.asarray(
            [
                np.dot(bump_weights, np.cos(mode * omega * transverse_starts))
                for mode in mode_numbers
            ],
            dtype=float,
        )
        self.transverse_interval_modes = (
            4.0
            / pars.transverse_width
            * np.sin(mode_numbers[:, None] * omega * self.contact_half_chords[None, :])
            / (mode_numbers[:, None] * omega)
        )

    def factors(self, times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return complex-capable midpoint patch factors and disk-contact factor."""

        pars = self.parameters
        time_values = np.atleast_1d(np.asarray(times, dtype=complex))
        flat_targets = self.patch_targets.reshape(-1)
        midpoint_kernel = ou_transition_density(
            time_values,
            flat_targets,
            self.midpoint_starts,
            diffusion_coefficient=pars.particle_diffusion / 2.0,
            stiffness=pars.ou_stiffness,
            mean=pars.ou_mean,
        ).reshape(
            len(time_values),
            4,
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
            / pars.transverse_width
        )

        parallel_kernel = ou_transition_density(
            time_values,
            self.contact_parallel_targets,
            self.relative_parallel_starts,
            diffusion_coefficient=2.0 * pars.particle_diffusion,
            stiffness=pars.ou_stiffness,
            mean=0.0,
        )
        parallel_density = np.einsum("txu,u->tx", parallel_kernel, self.bump_weights, optimize=True)
        mode_decay = np.exp(-time_values[:, None] * self.transverse_eigenvalues[None, :])
        interval_probability = (
            2.0 * self.contact_half_chords[None, :] / pars.transverse_width
            + (mode_decay * self.transverse_initial_cosine_coefficients[None, :])
            @ self.transverse_interval_modes
        )
        contact = np.einsum(
            "tx,tx,x->t",
            parallel_density,
            interval_probability,
            self.contact_parallel_weights,
            optimize=True,
        )
        return midpoint, contact

    def channels(self, times: np.ndarray, *, chunk_size: int = 128) -> np.ndarray:
        values = np.atleast_1d(np.asarray(times, dtype=complex))
        output = np.empty((len(values), 4), dtype=complex)
        for start in range(0, len(values), chunk_size):
            stop = min(start + chunk_size, len(values))
            midpoint, contact = self.factors(values[start:stop])
            output[start:stop] = midpoint * contact[:, None]
        return output

    def real_channels_and_first_derivatives(
        self,
        times: np.ndarray,
        *,
        chunk_size: int = 96,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Evaluate channels and exact real first-time derivatives."""

        values = np.atleast_1d(np.asarray(times, dtype=float))
        if np.any(values <= 0.0):
            raise ValueError("time grid must be strictly positive")
        channels = np.empty((len(values), 4), dtype=float)
        derivatives = np.empty_like(channels)
        pars = self.parameters
        flat_targets = self.patch_targets.reshape(-1)
        for start in range(0, len(values), chunk_size):
            stop = min(start + chunk_size, len(values))
            local_times = values[start:stop]
            midpoint_kernel, midpoint_kernel_d1 = ou_density_and_first_derivative(
                local_times,
                flat_targets,
                self.midpoint_starts,
                diffusion_coefficient=pars.particle_diffusion / 2.0,
                stiffness=pars.ou_stiffness,
                mean=pars.ou_mean,
            )
            shape = (
                len(local_times),
                4,
                self.configuration.patch_order,
                self.configuration.bump_order,
            )
            midpoint_kernel = midpoint_kernel.reshape(shape)
            midpoint_kernel_d1 = midpoint_kernel_d1.reshape(shape)
            midpoint = (
                np.einsum(
                    "tcvu,u,v->tc",
                    midpoint_kernel,
                    self.bump_weights,
                    self.patch_weights,
                    optimize=True,
                )
                / pars.transverse_width
            )
            midpoint_d1 = (
                np.einsum(
                    "tcvu,u,v->tc",
                    midpoint_kernel_d1,
                    self.bump_weights,
                    self.patch_weights,
                    optimize=True,
                )
                / pars.transverse_width
            )

            parallel_kernel, parallel_kernel_d1 = ou_density_and_first_derivative(
                local_times,
                self.contact_parallel_targets,
                self.relative_parallel_starts,
                diffusion_coefficient=2.0 * pars.particle_diffusion,
                stiffness=pars.ou_stiffness,
                mean=0.0,
            )
            parallel = np.einsum("txu,u->tx", parallel_kernel, self.bump_weights, optimize=True)
            parallel_d1 = np.einsum(
                "txu,u->tx", parallel_kernel_d1, self.bump_weights, optimize=True
            )
            mode_decay = np.exp(-local_times[:, None] * self.transverse_eigenvalues[None, :])
            interval = (
                2.0 * self.contact_half_chords[None, :] / pars.transverse_width
                + (mode_decay * self.transverse_initial_cosine_coefficients[None, :])
                @ self.transverse_interval_modes
            )
            interval_d1 = (
                mode_decay
                * (-self.transverse_eigenvalues[None, :])
                * self.transverse_initial_cosine_coefficients[None, :]
            ) @ self.transverse_interval_modes
            contact = np.einsum(
                "tx,tx,x->t",
                parallel,
                interval,
                self.contact_parallel_weights,
                optimize=True,
            )
            contact_d1 = np.einsum(
                "tx,tx,x->t",
                parallel_d1,
                interval,
                self.contact_parallel_weights,
                optimize=True,
            ) + np.einsum(
                "tx,tx,x->t",
                parallel,
                interval_d1,
                self.contact_parallel_weights,
                optimize=True,
            )
            channels[start:stop] = midpoint * contact[:, None]
            derivatives[start:stop] = (
                midpoint_d1 * contact[:, None] + midpoint * contact_d1[:, None]
            )
        return channels, derivatives

    def cauchy_jets(self, time: float, *, maximum_order: int = 4) -> dict[str, Any]:
        value = float(time)
        radius = float(self.configuration.cauchy_radius)
        samples = int(self.configuration.cauchy_samples)
        if value <= radius:
            raise ValueError("Cauchy circle would cross the t=0 singularity")
        angles = 2.0 * np.pi * np.arange(samples, dtype=float) / samples
        circle = value + radius * np.exp(1j * angles)
        midpoint_values, contact_values = self.factors(circle)
        channel_values = midpoint_values * contact_values[:, None]

        def differentiate(values: np.ndarray) -> tuple[np.ndarray, float]:
            array = np.asarray(values, dtype=complex)
            if array.ndim == 1:
                array = array[:, None]
            jets = np.empty((maximum_order + 1, array.shape[1]), dtype=float)
            maximum_imaginary = 0.0
            for order in range(maximum_order + 1):
                phase = np.exp(-1j * order * angles)
                coefficient = np.mean(array * phase[:, None], axis=0) / radius**order
                derivative = math.factorial(order) * coefficient
                jets[order] = np.real(derivative)
                maximum_imaginary = max(
                    maximum_imaginary,
                    float(np.max(np.abs(np.imag(derivative)))),
                )
            return jets, maximum_imaginary

        midpoint_jets, midpoint_imaginary = differentiate(midpoint_values)
        contact_matrix, contact_imaginary = differentiate(contact_values)
        channel_jets, channel_imaginary = differentiate(channel_values)
        contact_jets = contact_matrix[:, 0]
        leibniz = np.zeros_like(channel_jets)
        for order in range(maximum_order + 1):
            for left_order in range(order + 1):
                leibniz[order] += (
                    math.comb(order, left_order)
                    * midpoint_jets[left_order]
                    * contact_jets[order - left_order]
                )
        _real_channels, real_d1 = self.real_channels_and_first_derivatives(np.asarray((value,)))
        return {
            "midpoint": midpoint_jets,
            "contact": contact_jets,
            "channels": channel_jets,
            "maximum_imaginary_residual": max(
                midpoint_imaginary,
                contact_imaginary,
                channel_imaginary,
            ),
            "maximum_direct_vs_leibniz_difference": float(np.max(np.abs(channel_jets - leibniz))),
            "maximum_cauchy_vs_real_first_derivative_difference": float(
                np.max(np.abs(channel_jets[1] - real_d1[0]))
            ),
        }


def affine_cusp_matrix(jets: np.ndarray, fixed_first_weight: float) -> np.ndarray:
    values = np.asarray(jets, dtype=float)
    if values.shape[0] < 4 or values.shape[1] != 4:
        raise ValueError("four channel jets through order three are required")
    derivative_rows = values[1:4]
    base = derivative_rows[:, 3] + fixed_first_weight * (
        derivative_rows[:, 0] - derivative_rows[:, 3]
    )
    return np.column_stack(
        (
            derivative_rows[:, 1] - derivative_rows[:, 3],
            derivative_rows[:, 2] - derivative_rows[:, 3],
            base,
        )
    )


def row_normalized_determinant(matrix: np.ndarray) -> float:
    values = np.asarray(matrix, dtype=float)
    norms = np.linalg.norm(values, axis=1)
    if values.shape != (3, 3) or np.any(norms <= 0.0):
        raise ValueError("a nonzero 3 x 3 matrix is required")
    return float(np.linalg.det(values / norms[:, None]))


def cusp_metrics(
    jets: np.ndarray,
    time: float,
    fixed_first_weight: float,
) -> dict[str, Any]:
    values = np.asarray(jets, dtype=float)
    affine_matrix = affine_cusp_matrix(values, fixed_first_weight)
    _left, affine_singular_values, right = np.linalg.svd(affine_matrix)
    null = right[-1]
    if abs(null[2]) <= 1.0e-12 * np.linalg.norm(null):
        raise FloatingPointError("affine cusp null vector has zero chart coordinate")
    controls = null[:2] / null[2]
    weights = np.asarray(
        (
            fixed_first_weight,
            controls[0],
            controls[1],
            1.0 - fixed_first_weight - controls[0] - controls[1],
        ),
        dtype=float,
    )
    mixture = values @ weights
    density = float(mixture[0])
    tangent_directions = np.asarray(
        (
            (0.0, 1.0, 0.0, -1.0),
            (0.0, 0.0, 1.0, -1.0),
        )
    )
    raw_unfolding = np.asarray(
        [[float(direction @ values[order]) for direction in tangent_directions] for order in (1, 2)]
    )
    dimensionless_unfolding = np.diag((time / density, time**2 / density)) @ raw_unfolding
    unfolding_singular_values = np.linalg.svd(dimensionless_unfolding, compute_uv=False)
    direction_2d = np.asarray((raw_unfolding[0, 1], -raw_unfolding[0, 0]), dtype=float)
    direction_2d /= np.linalg.norm(direction_2d)
    cubic_coefficient = float(mixture[4] / 6.0)
    if float(raw_unfolding[1] @ direction_2d) * cubic_coefficient >= 0.0:
        direction_2d = -direction_2d
    direction_4d = np.asarray((0.0, direction_2d[0], direction_2d[1], -float(np.sum(direction_2d))))
    row_norms = np.linalg.norm(dimensionless_unfolding, axis=1)
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
        "affine_cusp_matrix": affine_matrix.tolist(),
        "affine_cusp_matrix_singular_values": affine_singular_values.tolist(),
        "row_normalized_determinant": row_normalized_determinant(affine_matrix),
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
        "strict_inward_normal": {
            "direction_2d": direction_2d.tolist(),
            "direction_4d": direction_4d.tolist(),
            "first_unfolding_projection": float(raw_unfolding[0] @ direction_2d),
            "second_unfolding_projection": float(raw_unfolding[1] @ direction_2d),
            "normal_form_cubic_coefficient": cubic_coefficient,
        },
    }


def locate_cusp(
    model: FourPatchContinuum,
    bracket: tuple[float, float],
) -> tuple[dict[str, Any], dict[str, Any]]:
    fixed_weight = model.parameters.fixed_first_weight

    def determinant(time: float) -> float:
        jets = model.cauchy_jets(time)["channels"]
        return row_normalized_determinant(affine_cusp_matrix(jets, fixed_weight))

    endpoint_values = [determinant(bracket[0]), determinant(bracket[1])]
    if endpoint_values[0] * endpoint_values[1] >= 0.0:
        raise RuntimeError(f"cusp bracket lacks a strict sign change: {endpoint_values}")
    root = float(brentq(determinant, *bracket, xtol=4.0e-12, rtol=2.0e-14))
    jet_payload = model.cauchy_jets(root)
    metrics = cusp_metrics(jet_payload["channels"], root, fixed_weight)
    diagnostics = {
        "bracket": list(bracket),
        "row_normalized_determinant_at_bracket": endpoint_values,
        "maximum_imaginary_cauchy_residual": jet_payload["maximum_imaginary_residual"],
        "maximum_direct_vs_leibniz_difference": jet_payload["maximum_direct_vs_leibniz_difference"],
        "maximum_cauchy_vs_real_first_derivative_difference": jet_payload[
            "maximum_cauchy_vs_real_first_derivative_difference"
        ],
        "channel_jets_orders_0_to_4_by_channel": jet_payload["channels"].tolist(),
        "midpoint_jets_orders_0_to_4_by_channel": jet_payload["midpoint"].tolist(),
        "contact_jets_orders_0_to_4": jet_payload["contact"].tolist(),
    }
    return metrics, diagnostics


def candidate_steps(start: float, stop: float, spacing: float) -> list[float]:
    count = int(round((stop - start) / spacing))
    values = [round(start + index * spacing, 12) for index in range(count + 1)]
    if not values or abs(values[-1] - stop) > 1.0e-12:
        raise ValueError("candidate step grid does not close at its declared stop")
    return values


def _root_brackets(
    times: np.ndarray,
    derivative: np.ndarray,
    *,
    zero_relative_tolerance: float,
) -> tuple[list[tuple[float, float]], list[list[int]]]:
    time_values = np.asarray(times, dtype=float)
    derivative_values = np.asarray(derivative, dtype=float)
    scale = max(float(np.max(np.abs(derivative_values))), np.finfo(float).tiny)
    zero_mask = np.abs(derivative_values) <= zero_relative_tolerance * scale
    zero_runs: list[list[int]] = []
    cursor = 0
    while cursor < len(zero_mask):
        if not zero_mask[cursor]:
            cursor += 1
            continue
        stop = cursor + 1
        while stop < len(zero_mask) and zero_mask[stop]:
            stop += 1
        zero_runs.append(list(range(cursor, stop)))
        cursor = stop

    brackets = [
        (float(time_values[index]), float(time_values[index + 1]))
        for index in np.flatnonzero(derivative_values[:-1] * derivative_values[1:] < 0.0)
    ]
    for run in zero_runs:
        left_index = run[0] - 1
        right_index = run[-1] + 1
        if (
            left_index >= 0
            and right_index < len(time_values)
            and derivative_values[left_index] * derivative_values[right_index] < 0.0
        ):
            brackets.append(
                (
                    float(time_values[left_index]),
                    float(time_values[right_index]),
                )
            )
    brackets = sorted(set(brackets))
    merged: list[tuple[float, float]] = []
    for bracket in brackets:
        if merged and bracket[0] <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], bracket[1]))
        else:
            merged.append(bracket)
    return merged, zero_runs


def stationary_structure(
    model: FourPatchContinuum,
    weights: np.ndarray,
    times: np.ndarray,
    channels: np.ndarray,
    channel_derivatives: np.ndarray,
    *,
    relative_density_floor: float,
    derivative_zero_relative_tolerance: float,
) -> dict[str, Any]:
    weight_values = np.asarray(weights, dtype=float)
    density_curve = np.asarray(channels, dtype=float) @ weight_values
    derivative_curve = np.asarray(channel_derivatives, dtype=float) @ weight_values
    brackets, zero_runs = _root_brackets(
        times,
        derivative_curve,
        zero_relative_tolerance=derivative_zero_relative_tolerance,
    )
    peak_density = float(np.max(density_curve))
    retained_zero_runs = [
        run
        for run in zero_runs
        if float(np.max(density_curve[run])) >= relative_density_floor * peak_density
    ]

    def derivative(time: float) -> float:
        return float(model.cauchy_jets(time)["channels"][1] @ weight_values)

    roots: list[dict[str, Any]] = []
    for left, right in brackets:
        left_value = derivative(left)
        right_value = derivative(right)
        if left_value * right_value >= 0.0:
            continue
        root = float(brentq(derivative, left, right, xtol=5.0e-12, rtol=2.0e-14))
        jets = model.cauchy_jets(root)["channels"] @ weight_values
        if jets[0] < relative_density_floor * peak_density:
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
    maxima = [row for row in roots if row["topology"] == "maximum"]
    minima = [row for row in roots if row["topology"] == "minimum"]
    peak_ratio = (
        min(row["density"] for row in maxima) / max(row["density"] for row in maxima)
        if maxima
        else 0.0
    )
    valley_ratios: list[float] = []
    if [row["topology"] for row in roots] == [
        "maximum",
        "minimum",
        "maximum",
        "minimum",
        "maximum",
    ]:
        for valley_index in (1, 3):
            valley = roots[valley_index]["density"]
            adjacent = min(
                roots[valley_index - 1]["density"],
                roots[valley_index + 1]["density"],
            )
            valley_ratios.append(float(valley / adjacent))
    return {
        "weights": weight_values.tolist(),
        "minimum_weight": float(np.min(weight_values)),
        "weight_sum_residual": float(abs(np.sum(weight_values) - 1.0)),
        "time_grid": {
            "start": float(times[0]),
            "stop": float(times[-1]),
            "spacing": float(times[1] - times[0]),
            "points": int(len(times)),
        },
        "stationary_root_count": len(roots),
        "maximum_count": len(maxima),
        "minimum_count": len(minima),
        "topology": [row["topology"] for row in roots],
        "roots": roots,
        "peak_minimum_to_maximum_ratio": float(peak_ratio),
        "valley_to_smaller_adjacent_peak_ratios": valley_ratios,
        "worst_valley_ratio": max(valley_ratios) if valley_ratios else None,
        "worst_valley_margin_to_0p85": (
            min(0.85 - ratio for ratio in valley_ratios) if valley_ratios else None
        ),
        "sampled_peak_density": peak_density,
        "derivative_at_time_start": float(derivative_curve[0]),
        "derivative_at_time_stop": float(derivative_curve[-1]),
        "near_zero_sample_runs_above_density_floor": retained_zero_runs,
        "discarded_subfloor_near_zero_run_count": len(zero_runs) - len(retained_zero_runs),
        "unresolved_zero_plateau": any(len(run) > 1 for run in retained_zero_runs),
    }


def candidate_is_eligible(
    candidate: dict[str, Any],
    *,
    minimum_peak_ratio: float,
    maximum_valley_ratio: float,
    minimum_abs_scaled_curvature: float,
    maximum_scaled_root_residual: float,
) -> tuple[bool, dict[str, bool]]:
    structure = candidate["stationary_structure"]
    root_checks = structure["roots"]
    gates = {
        "all_weights_strictly_positive": structure["minimum_weight"] > 0.0,
        "weights_sum_to_one": structure["weight_sum_residual"] < 1.0e-12,
        "exactly_three_maxima_two_minima": (
            structure["maximum_count"] == 3
            and structure["minimum_count"] == 2
            and structure["stationary_root_count"] == 5
        ),
        "alternating_topology": structure["topology"]
        == ["maximum", "minimum", "maximum", "minimum", "maximum"],
        "peak_height_floor": structure["peak_minimum_to_maximum_ratio"] >= minimum_peak_ratio,
        "both_valley_floors": (
            len(structure["valley_to_smaller_adjacent_peak_ratios"]) == 2
            and max(structure["valley_to_smaller_adjacent_peak_ratios"]) <= maximum_valley_ratio
        ),
        "simple_curvature_margin": bool(root_checks)
        and all(
            abs(row["scaled_second_derivative"]) >= minimum_abs_scaled_curvature
            for row in root_checks
        ),
        "root_residuals": bool(root_checks)
        and all(
            row["scaled_first_derivative_residual"] <= maximum_scaled_root_residual
            for row in root_checks
        ),
        "no_unresolved_zero_plateau": not structure["unresolved_zero_plateau"],
        "endpoint_derivative_signs": (
            structure["derivative_at_time_start"] > 0.0
            and structure["derivative_at_time_stop"] < 0.0
        ),
    }
    return all(gates.values()), gates


def select_candidate(candidates: Sequence[dict[str, Any]]) -> dict[str, Any]:
    eligible = [row for row in candidates if row["eligible"]]
    if not eligible:
        raise RuntimeError("no candidate passes the frozen observability rule")
    return max(
        eligible,
        key=lambda row: (
            row["stationary_structure"]["minimum_weight"],
            row["stationary_structure"]["worst_valley_margin_to_0p85"],
            row["stationary_structure"]["peak_minimum_to_maximum_ratio"],
            -row["step"],
        ),
    )


def polar_contact_reference(
    model: FourPatchContinuum,
    times: Sequence[float],
    *,
    radial_order: int,
    angular_points: int,
) -> dict[str, Any]:
    pars = model.parameters
    radial_nodes, radial_weights = leggauss(radial_order)
    radii = 0.5 * pars.contact_radius * (radial_nodes + 1.0)
    radial_weights = 0.5 * pars.contact_radius * radial_weights
    angles = 2.0 * np.pi * np.arange(angular_points, dtype=float) / angular_points
    parallel_targets = (radii[:, None] * np.cos(angles)[None, :]).reshape(-1)
    transverse_targets = (radii[:, None] * np.sin(angles)[None, :]).reshape(-1)
    area_weights = (
        radial_weights[:, None]
        * radii[:, None]
        * np.full((1, angular_points), 2.0 * np.pi / angular_points)
    ).reshape(-1)
    rows = []
    maximum_relative = 0.0
    for time in times:
        value = float(time)
        parallel_kernel = ou_transition_density(
            np.asarray((value,)),
            parallel_targets,
            model.relative_parallel_starts,
            diffusion_coefficient=2.0 * pars.particle_diffusion,
            stiffness=pars.ou_stiffness,
            mean=0.0,
        )[0]
        parallel_density = np.real(parallel_kernel @ model.bump_weights)
        mode_decay = np.exp(-value * model.transverse_eigenvalues)
        transverse_density = (
            1.0
            + 2.0
            * np.sum(
                (model.transverse_initial_cosine_coefficients * mode_decay)[:, None]
                * np.cos(model.mode_numbers[:, None] * model.omega * transverse_targets[None, :]),
                axis=0,
            )
        ) / pars.transverse_width
        polar = float(area_weights @ (parallel_density * transverse_density))
        half_chord = float(np.real(model.factors(np.asarray((value,)))[1][0]))
        difference = abs(polar - half_chord)
        relative = difference / abs(half_chord)
        maximum_relative = max(maximum_relative, relative)
        rows.append(
            {
                "time": value,
                "half_chord": half_chord,
                "polar": polar,
                "absolute_difference": difference,
                "relative_difference": relative,
            }
        )
    return {
        "radial_order": radial_order,
        "angular_points": angular_points,
        "rows": rows,
        "maximum_relative_difference": maximum_relative,
    }


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("evidence_timing") != EVIDENCE_TIMING:
        raise RuntimeError("manifest evidence timing is not fail-closed")
    required_flags = manifest.get("required_claim_flags")
    if required_flags != {
        "continuum_verified": False,
        "finite_B_Doi_verified": False,
        "project_gate_passed": False,
    }:
        raise RuntimeError("manifest negative claim flags were altered")
    expected_hashes = {
        "producer": (HERE, manifest["frozen_files"]["producer_sha256"]),
        "test": (TEST_FILE, manifest["frozen_files"]["test_sha256"]),
        "protocol": (PROTOCOL, manifest["frozen_files"]["protocol_sha256"]),
    }
    for label, (path, expected) in expected_hashes.items():
        observed = sha256(path)
        if observed != expected:
            raise RuntimeError(
                f"frozen {label} hash mismatch: expected {expected}, observed {observed}"
            )
    expected_physical_model = json.loads(json.dumps(asdict(PhysicalParameters()), allow_nan=False))
    if manifest["physical_model"] != expected_physical_model:
        raise RuntimeError("manifest physical model does not match the producer")
    expected_configurations = {
        "coarse": asdict(COARSE),
        "primary": asdict(PRIMARY),
        "fine": asdict(FINE),
    }
    if manifest["numerical_configurations"] != expected_configurations:
        raise RuntimeError("manifest numerical configurations do not match the producer")
    scan = manifest["inward_step_scan"]
    expected_steps = candidate_steps(scan["step_start"], scan["step_stop"], scan["step_spacing"])
    if scan["candidate_steps"] != expected_steps:
        raise RuntimeError("manifest candidate step grid is inconsistent")
    if scan["selection_priority"] != [
        "maximum minimum catalyst weight",
        "maximum worst-valley margin to the 0.85 ceiling",
        "maximum minimum-to-maximum peak ratio",
        "smallest step as deterministic final tie-break",
    ]:
        raise RuntimeError("manifest candidate selection priority was altered")


def run_formal(manifest: dict[str, Any]) -> dict[str, Any]:
    validate_manifest(manifest)
    scan = manifest["inward_step_scan"]
    bracket = tuple(manifest["cusp_confirmation"]["determinant_bracket"])
    primary_model = FourPatchContinuum(PRIMARY)
    cusp, cusp_diagnostics = locate_cusp(primary_model, bracket)

    times = np.arange(
        scan["time_start"],
        scan["time_stop"] + 0.5 * scan["time_spacing"],
        scan["time_spacing"],
    )
    channels, derivatives = primary_model.real_channels_and_first_derivatives(times)
    base_weights = np.asarray(cusp["weights"], dtype=float)
    direction = np.asarray(cusp["strict_inward_normal"]["direction_4d"], dtype=float)
    candidates = []
    for step in scan["candidate_steps"]:
        weights = base_weights + step * direction
        structure = stationary_structure(
            primary_model,
            weights,
            times,
            channels,
            derivatives,
            relative_density_floor=scan["relative_density_floor"],
            derivative_zero_relative_tolerance=scan["derivative_zero_relative_tolerance"],
        )
        row: dict[str, Any] = {
            "step": step,
            "weights": weights.tolist(),
            "stationary_structure": structure,
        }
        eligible, gates = candidate_is_eligible(
            row,
            minimum_peak_ratio=scan["minimum_peak_ratio"],
            maximum_valley_ratio=scan["maximum_valley_ratio"],
            minimum_abs_scaled_curvature=scan["minimum_abs_scaled_curvature"],
            maximum_scaled_root_residual=scan["maximum_scaled_root_residual"],
        )
        row["eligible"] = eligible
        row["gates"] = gates
        candidates.append(row)
    selected = select_candidate(candidates)

    convergence_rows = []
    configuration_map = {
        "coarse": COARSE,
        "primary": PRIMARY,
        "fine": FINE,
    }
    for label, configuration in configuration_map.items():
        if label == "primary":
            metrics = cusp
            diagnostics = cusp_diagnostics
        else:
            metrics, diagnostics = locate_cusp(
                FourPatchContinuum(configuration),
                bracket,
            )
        convergence_rows.append(
            {
                "label": label,
                "configuration": asdict(configuration),
                "cusp_time": metrics["time"],
                "weights": metrics["weights"],
                "scaled_fourth_derivative": metrics["scaled_fourth_derivative"],
                "unfolding_svd_ratio": metrics["unfolding"]["dimensionless_svd_ratio"],
                "maximum_scaled_cusp_residual": max(metrics["scaled_residuals_orders_1_to_3"]),
                "maximum_imaginary_cauchy_residual": diagnostics[
                    "maximum_imaginary_cauchy_residual"
                ],
                "maximum_direct_vs_leibniz_difference": diagnostics[
                    "maximum_direct_vs_leibniz_difference"
                ],
            }
        )

    selected_weights = np.asarray(selected["weights"], dtype=float)
    fine_model = FourPatchContinuum(FINE)
    fine_channels, fine_derivatives = fine_model.real_channels_and_first_derivatives(times)
    fine_structure = stationary_structure(
        fine_model,
        selected_weights,
        times,
        fine_channels,
        fine_derivatives,
        relative_density_floor=scan["relative_density_floor"],
        derivative_zero_relative_tolerance=scan["derivative_zero_relative_tolerance"],
    )
    fine_row = {
        "step": selected["step"],
        "weights": selected["weights"],
        "stationary_structure": fine_structure,
    }
    fine_eligible, fine_gates = candidate_is_eligible(
        fine_row,
        minimum_peak_ratio=scan["minimum_peak_ratio"],
        maximum_valley_ratio=scan["maximum_valley_ratio"],
        minimum_abs_scaled_curvature=scan["minimum_abs_scaled_curvature"],
        maximum_scaled_root_residual=scan["maximum_scaled_root_residual"],
    )
    fine_row["eligible"] = fine_eligible
    fine_row["gates"] = fine_gates

    polar = polar_contact_reference(
        primary_model,
        manifest["polar_contact_check"]["times"],
        radial_order=manifest["polar_contact_check"]["radial_order"],
        angular_points=manifest["polar_contact_check"]["angular_points"],
    )
    convergence = {row["label"]: row for row in convergence_rows}
    primary_weights = np.asarray(convergence["primary"]["weights"])
    fine_weights = np.asarray(convergence["fine"]["weights"])
    primary_roots = selected["stationary_structure"]["roots"]
    fine_roots = fine_structure["roots"]
    root_differences = (
        [
            abs(left["time"] - right["time"])
            for left, right in zip(primary_roots, fine_roots, strict=True)
        ]
        if len(primary_roots) == len(fine_roots)
        else []
    )
    gates = {
        "cusp_weights_strictly_positive": cusp["minimum_weight"] > 0.0,
        "fixed_first_weight_preserved": abs(
            cusp["weights"][0] - PhysicalParameters().fixed_first_weight
        )
        < 1.0e-13,
        "cusp_residual": max(cusp["scaled_residuals_orders_1_to_3"])
        <= manifest["cusp_confirmation"]["maximum_scaled_cusp_residual"],
        "fourth_derivative_nonzero": abs(cusp["scaled_fourth_derivative"])
        >= manifest["cusp_confirmation"]["minimum_absolute_scaled_fourth_derivative"],
        "unfolding_rank_two": cusp["unfolding"]["rank"] == 2,
        "unfolding_ratio": cusp["unfolding"]["dimensionless_svd_ratio"]
        >= manifest["cusp_confirmation"]["minimum_unfolding_svd_ratio"],
        "strict_normal_first_projection": abs(
            cusp["strict_inward_normal"]["first_unfolding_projection"]
        )
        <= 1.0e-12,
        "strict_normal_signed_inward": (
            cusp["strict_inward_normal"]["second_unfolding_projection"]
            * cusp["strict_inward_normal"]["normal_form_cubic_coefficient"]
            < 0.0
        ),
        "eligible_candidate_exists": any(row["eligible"] for row in candidates),
        "selected_candidate_observable": selected["eligible"],
        "selected_step_follows_frozen_priority": selected == select_candidate(candidates),
        "fine_fixed_weight_observable": fine_eligible,
        "fine_primary_cusp_time_agreement": abs(
            convergence["fine"]["cusp_time"] - convergence["primary"]["cusp_time"]
        )
        <= manifest["convergence_gates"]["maximum_cusp_time_difference"],
        "fine_primary_weight_agreement": float(np.max(np.abs(fine_weights - primary_weights)))
        <= manifest["convergence_gates"]["maximum_weight_linf_difference"],
        "fine_primary_scaled_f4_agreement": abs(
            convergence["fine"]["scaled_fourth_derivative"]
            - convergence["primary"]["scaled_fourth_derivative"]
        )
        <= manifest["convergence_gates"]["maximum_scaled_f4_difference"],
        "fine_fixed_weight_root_count": len(primary_roots) == len(fine_roots) == 5,
        "fine_fixed_weight_root_times": bool(root_differences)
        and max(root_differences) <= manifest["convergence_gates"]["maximum_root_time_difference"],
        "polar_contact_check": polar["maximum_relative_difference"]
        <= manifest["polar_contact_check"]["maximum_relative_difference"],
    }
    if not all(gates.values()):
        failed = [name for name, passed in gates.items() if not passed]
        raise RuntimeError(f"formal four-patch confirmation failed gates: {failed}")

    return {
        "schema_version": 1,
        "stage": manifest["stage"],
        "status": RESULT_STATUS,
        "evidence_timing": EVIDENCE_TIMING,
        "claim_flags": {
            "preregistered_discovery": False,
            "continuum_verified": False,
            "finite_B_Doi_verified": False,
            "project_gate_passed": False,
            "observable_free_exposure_confirmation_passed": True,
        },
        "model": {
            "physical_dimension": 2,
            "domain": "R longitudinal x T_W transverse; unbounded OU kernels",
            "parameters": asdict(PhysicalParameters()),
            "full_budget_factor": "1 / transverse_width",
            "factorization": "g_j(t)=a_j(t)c_2(t)",
            "affine_control_slice": ("w0 fixed at 0.28; w1,w2 free; w3=1-w0-w1-w2"),
        },
        "cusp": cusp,
        "cusp_diagnostics": cusp_diagnostics,
        "inward_step_scan": {
            "selection_rule": scan["selection_priority"],
            "candidate_count": len(candidates),
            "eligible_count": sum(row["eligible"] for row in candidates),
            "candidates": candidates,
            "selected": selected,
        },
        "quadrature_and_cauchy_convergence": convergence_rows,
        "selected_absolute_weight_fine_crosscheck": fine_row,
        "selected_root_time_absolute_differences_primary_vs_fine": root_differences,
        "polar_contact_check": polar,
        "gates": gates,
        "limitations": [
            "geometry, approximate cusp, and a passing inward step were known before freeze",
            "floating-point quadrature convergence is not interval certification",
            "the calculation is the B=0 derivative per unit full installed budget",
            "no explicit positive-B persistence radius or killed-Doi calculation is included",
            "no bounded-box SG/FEM or independent PDE solver is included",
            "no physical d=3 calculation is included",
        ],
        "provenance": {
            "manifest": str(MANIFEST.relative_to(REPORT)),
            "manifest_sha256": sha256(MANIFEST),
            "producer": str(HERE.relative_to(REPORT)),
            "producer_sha256": sha256(HERE),
            "test": str(TEST_FILE.relative_to(REPORT)),
            "test_sha256": sha256(TEST_FILE),
            "protocol": str(PROTOCOL.relative_to(REPORT)),
            "protocol_sha256": sha256(PROTOCOL),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-frozen", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    if not args.execute_frozen:
        parser.error("formal execution requires --execute-frozen")
    require_repository_venv()
    manifest = load_json(MANIFEST)
    payload = run_formal(manifest)
    write_json(args.output, payload)
    selected = payload["inward_step_scan"]["selected"]
    structure = selected["stationary_structure"]
    print(
        f"cusp_time={payload['cusp']['time']:.12g} "
        f"selected_step={selected['step']:.2f} "
        f"valley_ratios={structure['valley_to_smaller_adjacent_peak_ratios']}"
    )
    print(f"status={payload['status']}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
