#!/usr/bin/env python3
"""Result-informed weak-budget/free-exposure design diagnostic.

The calculation differentiates the *discrete* killed quotient at zero full
installed budget.  It reproduces a cusp that was already seen in scratch work,
so it is not preregistered discovery and cannot verify a finite-B Doi cusp or a
continuum claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import continuum_g1_smoke as smoke
import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import brentq
from scipy.sparse.linalg import expm_multiply

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "continuum_weak_budget_design_manifest.json"
OUTPUT = DATA / "continuum_weak_budget_design_result.json"


@dataclass(frozen=True)
class FactorGrid:
    midpoint_cells: int
    relative_parallel_cells: int
    relative_perp_cells: int

    @property
    def full_state_count(self) -> int:
        return int(self.midpoint_cells * self.relative_parallel_cells * self.relative_perp_cells)


@dataclass(frozen=True)
class FreeExposureFactors:
    grid: FactorGrid
    midpoint_generator: sparse.csr_matrix
    relative_generator: sparse.csr_matrix
    midpoint_initial: np.ndarray
    relative_initial: np.ndarray
    patch_profiles: np.ndarray
    contact_profile: np.ndarray
    midpoint_actions: np.ndarray
    relative_actions: np.ndarray


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


def repository_venv() -> Path:
    return (REPOSITORY / ".venv").resolve()


def require_repository_venv() -> None:
    if Path(sys.prefix).resolve() != repository_venv():
        raise RuntimeError("weak-budget diagnostic must run inside the repository .venv")


def _action_columns(
    generator: sparse.csr_matrix,
    observables: np.ndarray,
    *,
    maximum_order: int,
) -> np.ndarray:
    """Return columns Q^n q_j ordered first by n and then by j."""

    base = np.asarray(observables, dtype=float)
    if base.ndim == 1:
        base = base[:, None]
    if base.ndim != 2 or base.shape[0] != generator.shape[0]:
        raise ValueError("observable columns do not match the generator")
    blocks = [base]
    for _order in range(maximum_order):
        blocks.append(np.asarray(generator @ blocks[-1], dtype=float))
    actions = np.column_stack(blocks)
    if np.any(~np.isfinite(actions)):
        raise FloatingPointError("generator actions are non-finite")
    return actions


def build_free_exposure_factors(grid: FactorGrid) -> FreeExposureFactors:
    """Build the free midpoint and relative factors without a killed operator."""

    pars = smoke.PilotParameters()
    quotient_grid = smoke.QuotientGrid2D(
        midpoint_cells=grid.midpoint_cells,
        relative_parallel_cells=grid.relative_parallel_cells,
        relative_perp_cells=grid.relative_perp_cells,
        midpoint_bounds=pars.midpoint_bounds,
        relative_parallel_bounds=pars.relative_parallel_bounds,
        transverse_width=pars.transverse_width,
    )
    midpoint_generator = smoke.sg_reflecting_generator(
        quotient_grid.midpoint_edges,
        diffusion=pars.diffusion / 2.0,
        drift=lambda z: -pars.ou_stiffness * (z - pars.ou_mean),
    )
    parallel_generator = smoke.sg_reflecting_generator(
        quotient_grid.relative_parallel_edges,
        diffusion=2.0 * pars.diffusion,
        drift=lambda r: -pars.ou_stiffness * r,
    )
    perpendicular_generator = smoke.periodic_diffusion_generator(
        quotient_grid.relative_perp_cells,
        quotient_grid.relative_perp_spacing,
        2.0 * pars.diffusion,
    )
    relative_generator = sparse.kron(
        parallel_generator,
        sparse.eye(quotient_grid.relative_perp_cells, format="csr"),
        format="csr",
    ) + sparse.kron(
        sparse.eye(quotient_grid.relative_parallel_cells, format="csr"),
        perpendicular_generator,
        format="csr",
    )

    patch_profiles = []
    for centre, half_width in zip(
        pars.patch_centres,
        pars.patch_half_widths,
        strict=True,
    ):
        masses, _error = smoke.bump_cell_masses(
            quotient_grid.midpoint_edges,
            centre=centre,
            half_width=half_width,
        )
        patch_profiles.append(masses / quotient_grid.midpoint_spacing)
    patch_matrix = np.asarray(patch_profiles, dtype=float)
    contact, _area, _error = smoke.contact_cell_fractions(
        quotient_grid.relative_parallel_edges,
        quotient_grid.relative_perp_edges,
        radius=pars.contact_radius,
    )
    contact_profile = contact.reshape(-1)

    midpoint_initial, _error = smoke.bump_cell_masses(
        quotient_grid.midpoint_edges,
        centre=pars.midpoint_start,
        half_width=pars.midpoint_bump_half_width,
    )
    parallel_initial, _error = smoke.bump_cell_masses(
        quotient_grid.relative_parallel_edges,
        centre=pars.relative_parallel_start,
        half_width=pars.relative_bump_half_width,
    )
    perpendicular_initial, _error = smoke.bump_cell_masses(
        quotient_grid.relative_perp_edges,
        centre=pars.relative_perp_start,
        half_width=pars.relative_bump_half_width,
        period=pars.transverse_width,
    )
    relative_initial = np.kron(parallel_initial, perpendicular_initial)

    midpoint_actions = _action_columns(
        midpoint_generator,
        patch_matrix.T / pars.transverse_width,
        maximum_order=4,
    )
    relative_actions = _action_columns(
        relative_generator,
        contact_profile,
        maximum_order=4,
    )
    return FreeExposureFactors(
        grid=grid,
        midpoint_generator=midpoint_generator,
        relative_generator=relative_generator,
        midpoint_initial=np.asarray(midpoint_initial, dtype=float),
        relative_initial=np.asarray(relative_initial, dtype=float),
        patch_profiles=patch_matrix,
        contact_profile=contact_profile,
        midpoint_actions=midpoint_actions,
        relative_actions=relative_actions,
    )


def _projected_curves_chunked(
    generator: sparse.csr_matrix,
    initial: np.ndarray,
    actions: np.ndarray,
    times: np.ndarray,
    *,
    chunk_points: int,
) -> np.ndarray:
    """Evaluate p exp(tQ) against action columns without retaining all states."""

    time_values = np.asarray(times, dtype=float)
    if (
        time_values.ndim != 1
        or time_values.size < 2
        or time_values[0] != 0.0
        or np.any(np.diff(time_values) <= 0.0)
        or not np.allclose(
            np.diff(time_values),
            time_values[1] - time_values[0],
            rtol=2.0e-12,
            atol=5.0e-14,
        )
    ):
        raise ValueError("times must be a uniform increasing grid starting at zero")
    if not 2 <= chunk_points <= time_values.size:
        raise ValueError("invalid chunk size")
    state = np.asarray(initial, dtype=float).copy()
    if state.shape != (generator.shape[0],):
        raise ValueError("initial law does not match the generator")
    output = np.empty((time_values.size, actions.shape[1]), dtype=float)
    output[0] = state @ actions
    cursor = 0
    trace = float(np.sum(generator.diagonal()))
    operator = generator.T.tocsr()
    while cursor < time_values.size - 1:
        end = min(cursor + chunk_points - 1, time_values.size - 1)
        rows = end - cursor + 1
        states = np.asarray(
            expm_multiply(
                operator,
                state,
                start=0.0,
                stop=float(time_values[end] - time_values[cursor]),
                num=rows,
                endpoint=True,
                traceA=trace,
            ),
            dtype=float,
        )
        if states.shape != (rows, generator.shape[0]) or np.any(~np.isfinite(states)):
            raise FloatingPointError("invalid state chunk")
        output[cursor + 1 : end + 1] = states[1:] @ actions
        state = states[-1].copy()
        cursor = end
    if np.any(~np.isfinite(output)):
        raise FloatingPointError("projected curves are non-finite")
    return output


def leibniz_channels(
    midpoint_jets: np.ndarray,
    relative_jets: np.ndarray,
) -> np.ndarray:
    """Combine a_j and c jets through fourth order by the Leibniz rule."""

    a = np.asarray(midpoint_jets, dtype=float)
    c = np.asarray(relative_jets, dtype=float)
    if a.ndim < 2 or a.shape[0] != 5 or c.shape[0] != 5:
        raise ValueError("both factor jets must contain orders zero through four")
    if a.shape[1:-1] != c.shape[1:]:
        raise ValueError("midpoint and relative jet sample axes disagree")
    output = np.zeros_like(a)
    for order in range(5):
        for left_order in range(order + 1):
            coefficient = math.comb(order, left_order)
            output[order] += coefficient * a[left_order] * c[order - left_order][..., None]
    return output


def factorized_channel_curves(
    factors: FreeExposureFactors,
    times: np.ndarray,
    *,
    chunk_points: int,
) -> np.ndarray:
    """Return h_j^(n)(t) with shape (5, time, 3)."""

    midpoint_flat = _projected_curves_chunked(
        factors.midpoint_generator,
        factors.midpoint_initial,
        factors.midpoint_actions,
        times,
        chunk_points=min(chunk_points, len(times)),
    )
    relative_flat = _projected_curves_chunked(
        factors.relative_generator,
        factors.relative_initial,
        factors.relative_actions,
        times,
        chunk_points=min(chunk_points, len(times)),
    )
    midpoint_jets = midpoint_flat.reshape(len(times), 5, 3).transpose(1, 0, 2)
    relative_jets = relative_flat.reshape(len(times), 5).T
    return leibniz_channels(midpoint_jets, relative_jets)


def factorized_channel_point(
    factors: FreeExposureFactors,
    time: float,
) -> np.ndarray:
    """Return h_j^(n)(t) with shape (5,3) at one time."""

    value = float(time)
    if value < 0.0 or not np.isfinite(value):
        raise ValueError("time must be finite and nonnegative")
    if value == 0.0:
        midpoint_state = factors.midpoint_initial
        relative_state = factors.relative_initial
    else:
        midpoint_state = np.asarray(
            expm_multiply(
                value * factors.midpoint_generator.T,
                factors.midpoint_initial,
                traceA=value * float(np.sum(factors.midpoint_generator.diagonal())),
            ),
            dtype=float,
        )
        relative_state = np.asarray(
            expm_multiply(
                value * factors.relative_generator.T,
                factors.relative_initial,
                traceA=value * float(np.sum(factors.relative_generator.diagonal())),
            ),
            dtype=float,
        )
    midpoint_jets = (midpoint_state @ factors.midpoint_actions).reshape(5, 3)
    relative_jets = (relative_state @ factors.relative_actions).reshape(5)
    return leibniz_channels(midpoint_jets[:, None, :], relative_jets[:, None])[:, 0, :]


def _row_normalized_determinant(channel_jets: np.ndarray) -> float:
    matrix = np.asarray(channel_jets[1:4], dtype=float)
    norms = np.linalg.norm(matrix, axis=1)
    if np.any(norms <= 0.0) or np.any(~np.isfinite(norms)):
        raise FloatingPointError("cusp determinant row has zero or non-finite norm")
    return float(np.linalg.det(matrix / norms[:, None]))


def reproduce_cusp(
    factors: FreeExposureFactors,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    rules = manifest["cusp_reproduction"]
    left, right = map(float, rules["determinant_bracket"])

    def determinant(time: float) -> float:
        return _row_normalized_determinant(factorized_channel_point(factors, time))

    endpoint_values = (determinant(left), determinant(right))
    if endpoint_values[0] * endpoint_values[1] >= 0.0:
        raise RuntimeError("frozen determinant bracket does not contain a strict sign change")
    cusp_time = float(brentq(determinant, left, right, xtol=2.0e-12, rtol=1.0e-14))
    jets = factorized_channel_point(factors, cusp_time)
    derivative_matrix = jets[1:4]
    _u, singular_values, vh = np.linalg.svd(derivative_matrix)
    weights = np.asarray(vh[-1], dtype=float)
    if float(np.sum(weights)) < 0.0:
        weights = -weights
    weights /= float(np.sum(weights))
    mixture = jets @ weights
    density = float(mixture[0])
    scaled_residuals = [
        float(abs(mixture[order]) * cusp_time**order / density) for order in (1, 2, 3)
    ]
    scaled_fourth = float(mixture[4] * cusp_time**4 / density)

    control_directions = np.asarray(((1.0, 0.0, -1.0), (0.0, 1.0, -1.0)))
    raw_unfolding = np.asarray(
        [[float(direction @ jets[order]) for direction in control_directions] for order in (1, 2)]
    )
    dimensionless_unfolding = np.diag((cusp_time / density, cusp_time**2 / density)) @ raw_unfolding
    unfolding_singular_values = np.linalg.svd(
        dimensionless_unfolding,
        compute_uv=False,
    )
    unfolding_ratio = float(unfolding_singular_values[-1] / unfolding_singular_values[0])
    unfolding_rank = int(
        np.linalg.matrix_rank(
            dimensionless_unfolding,
            tol=1.0e-12 * unfolding_singular_values[0],
        )
    )
    row_norms = np.linalg.norm(dimensionless_unfolding, axis=1)
    row_angle_sine = float(abs(np.linalg.det(dimensionless_unfolding / row_norms[:, None])))
    return {
        "cusp_time": cusp_time,
        "weights": weights.tolist(),
        "determinant_bracket": [left, right],
        "row_normalized_determinant_at_bracket": list(endpoint_values),
        "row_normalized_determinant_at_root": determinant(cusp_time),
        "raw_derivative_matrix": derivative_matrix.tolist(),
        "raw_derivative_matrix_singular_values": singular_values.tolist(),
        "density_per_unit_budget": density,
        "mixture_raw_jets_orders_0_to_4": mixture.tolist(),
        "scaled_derivative_residuals_orders_1_to_3": scaled_residuals,
        "scaled_fourth_derivative": scaled_fourth,
        "control_directions": control_directions.tolist(),
        "unfolding": {
            "raw_matrix": raw_unfolding.tolist(),
            "dimensionless_matrix": dimensionless_unfolding.tolist(),
            "dimensionless_singular_values": unfolding_singular_values.tolist(),
            "dimensionless_svd_ratio": unfolding_ratio,
            "row_angle_sine_magnitude": row_angle_sine,
            "rank": unfolding_rank,
        },
    }


def full_kronecker_reference(manifest: dict[str, Any]) -> dict[str, Any]:
    """Compare the factorization with directly formed full-generator actions."""

    reference = manifest["full_kronecker_reference"]
    mesh = reference["mesh"]
    grid = FactorGrid(
        midpoint_cells=mesh["midpoint_cells"],
        relative_parallel_cells=mesh["relative_parallel_cells"],
        relative_perp_cells=mesh["relative_perp_cells"],
    )
    if grid.full_state_count != mesh["state_count"]:
        raise ValueError("reference mesh state count is inconsistent")
    factors = build_free_exposure_factors(grid)
    relative_states = factors.relative_generator.shape[0]
    full_generator = sparse.kron(
        factors.midpoint_generator,
        sparse.eye(relative_states, format="csr"),
        format="csr",
    ) + sparse.kron(
        sparse.eye(grid.midpoint_cells, format="csr"),
        factors.relative_generator,
        format="csr",
    )
    initial = np.kron(factors.midpoint_initial, factors.relative_initial)
    observables = np.column_stack(
        [
            np.kron(
                factors.patch_profiles[channel] / smoke.PilotParameters().transverse_width,
                factors.contact_profile,
            )
            for channel in range(3)
        ]
    )
    actions = _action_columns(full_generator, observables, maximum_order=4)
    trace = float(np.sum(full_generator.diagonal()))
    rows = []
    maximum_scaled_difference = 0.0
    maximum_absolute_difference = 0.0
    for time in reference["times"]:
        value = float(time)
        if value == 0.0:
            state = initial
        else:
            state = np.asarray(
                expm_multiply(
                    value * full_generator.T,
                    initial,
                    traceA=value * trace,
                ),
                dtype=float,
            )
        direct = (state @ actions).reshape(5, 3)
        factorized = factorized_channel_point(factors, value)
        difference = np.abs(direct - factorized)
        scaled = difference / (1.0 + np.abs(direct))
        maximum_absolute_difference = max(
            maximum_absolute_difference,
            float(np.max(difference)),
        )
        maximum_scaled_difference = max(
            maximum_scaled_difference,
            float(np.max(scaled)),
        )
        rows.append(
            {
                "time": value,
                "maximum_absolute_difference": float(np.max(difference)),
                "maximum_scaled_absolute_difference": float(np.max(scaled)),
            }
        )
    return {
        "mesh": mesh,
        "times": reference["times"],
        "derivative_orders": reference["derivative_orders"],
        "comparison_rows": rows,
        "maximum_absolute_difference": maximum_absolute_difference,
        "maximum_scaled_absolute_difference": maximum_scaled_difference,
    }


def _strict_sign_brackets(
    times: np.ndarray,
    values: np.ndarray,
    *,
    lower: float,
    upper: float,
) -> list[tuple[float, float]]:
    selected = np.flatnonzero((times >= lower) & (times <= upper))
    brackets = []
    for left_index, right_index in zip(selected[:-1], selected[1:], strict=True):
        left_value = float(values[left_index])
        right_value = float(values[right_index])
        if left_value * right_value < 0.0:
            brackets.append((float(times[left_index]), float(times[right_index])))
    return brackets


def verify_inward_direction(
    factors: FreeExposureFactors,
    channel_curves: np.ndarray,
    times: np.ndarray,
    cusp: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    rules = manifest["normal_form_inward_check"]
    weights = np.asarray(cusp["weights"], dtype=float)
    raw_unfolding = np.asarray(cusp["unfolding"]["raw_matrix"], dtype=float)
    direction = np.asarray((raw_unfolding[0, 1], -raw_unfolding[0, 0]), dtype=float)
    direction /= float(np.linalg.norm(direction))
    cubic_coefficient = float(cusp["mixture_raw_jets_orders_0_to_4"][4]) / 6.0
    if float(raw_unfolding[1] @ direction) * cubic_coefficient >= 0.0:
        direction = -direction
    step = float(rules["step"])
    perturbed = weights.copy()
    perturbed[:2] += step * direction
    perturbed[2] = 1.0 - float(np.sum(perturbed[:2]))
    sampled_derivative = channel_curves[1] @ perturbed
    cusp_time = float(cusp["cusp_time"])
    half_width = float(rules["local_time_half_width"])
    brackets = _strict_sign_brackets(
        times,
        sampled_derivative,
        lower=cusp_time - half_width,
        upper=cusp_time + half_width,
    )

    def derivative(time: float) -> float:
        return float(factorized_channel_point(factors, time)[1] @ perturbed)

    roots = []
    for left, right in brackets:
        root = float(brentq(derivative, left, right, xtol=2.0e-11, rtol=1.0e-13))
        jets = factorized_channel_point(factors, root) @ perturbed
        topology = "maximum" if jets[2] < 0.0 else "minimum"
        roots.append(
            {
                "time": root,
                "topology": topology,
                "raw_first_derivative_residual": float(jets[1]),
                "scaled_first_derivative_residual": float(abs(root * jets[1] / jets[0])),
                "scaled_second_derivative": float(root**2 * jets[2] / jets[0]),
            }
        )
    return {
        "normal_form_cubic_coefficient": cubic_coefficient,
        "control_direction_2d": direction.tolist(),
        "control_direction_3d": [
            float(direction[0]),
            float(direction[1]),
            float(-direction[0] - direction[1]),
        ],
        "second_unfolding_row_projection": float(raw_unfolding[1] @ direction),
        "step": step,
        "perturbed_weights": perturbed.tolist(),
        "sampled_sign_brackets": [list(bracket) for bracket in brackets],
        "stationary_roots": roots,
        "root_count": len(roots),
        "topology": [row["topology"] for row in roots],
    }


def simplex_weights(denominator: int) -> np.ndarray:
    rows = []
    for left in range(denominator + 1):
        for middle in range(denominator - left + 1):
            right = denominator - left - middle
            rows.append((left / denominator, middle / denominator, right / denominator))
    return np.asarray(rows, dtype=float)


def sampled_mode_count(
    density: np.ndarray,
    derivative: np.ndarray,
    times: np.ndarray,
    *,
    minimum_time: float,
    relative_density_floor: float,
    derivative_zero_relative_tolerance: float,
) -> tuple[int, int, list[float]]:
    """Count sign-changing maxima/minima on the declared sampled time grid."""

    peak = float(np.max(density))
    keep = (times >= minimum_time) & (density >= relative_density_floor * peak)
    retained_indices = np.flatnonzero(keep)
    if retained_indices.size < 2:
        return 0, 0, []
    values = derivative[retained_indices]
    tolerance = derivative_zero_relative_tolerance * max(float(np.max(np.abs(values))), 1.0)
    nonzero = np.abs(values) > tolerance
    indices = retained_indices[nonzero]
    if indices.size < 2:
        return 0, 0, []
    signs = np.sign(derivative[indices])
    maximum_mask = (signs[:-1] > 0.0) & (signs[1:] < 0.0)
    minimum_mask = (signs[:-1] < 0.0) & (signs[1:] > 0.0)
    maximum_times = [
        float(0.5 * (times[indices[index]] + times[indices[index + 1]]))
        for index in np.flatnonzero(maximum_mask)
    ]
    return int(np.sum(maximum_mask)), int(np.sum(minimum_mask)), maximum_times


def screen_simplex(
    channel_curves: np.ndarray,
    times: np.ndarray,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    rules = manifest["simplex_screen"]
    denominator = int(rules["integer_denominator"])
    weights = simplex_weights(denominator)
    if len(weights) != rules["control_count"]:
        raise RuntimeError("simplex enumeration count disagrees with the manifest")
    histogram: dict[int, int] = {}
    examples: dict[int, list[dict[str, Any]]] = {}
    maximum_modes = -1
    for weight in weights:
        density = channel_curves[0] @ weight
        derivative = channel_curves[1] @ weight
        maxima, minima, maximum_times = sampled_mode_count(
            density,
            derivative,
            times,
            minimum_time=float(rules["minimum_mode_analysis_time"]),
            relative_density_floor=float(rules["relative_density_floor"]),
            derivative_zero_relative_tolerance=float(rules["derivative_zero_relative_tolerance"]),
        )
        histogram[maxima] = histogram.get(maxima, 0) + 1
        maximum_modes = max(maximum_modes, maxima)
        if len(examples.setdefault(maxima, [])) < 8:
            examples[maxima].append(
                {
                    "weights": weight.tolist(),
                    "sampled_maximum_times": maximum_times,
                    "sampled_minimum_count": minima,
                }
            )
    minimum_index = int(round(rules["minimum_mode_analysis_time"] / rules["time_spacing"]))
    vertex_entry_derivatives = channel_curves[1, minimum_index].tolist()
    vertex_tail_derivatives = channel_curves[1, -1].tolist()
    return {
        "spacing": rules["spacing"],
        "integer_denominator": denominator,
        "control_count": len(weights),
        "time_grid": {
            "start": float(times[0]),
            "stop": float(times[-1]),
            "spacing": float(times[1] - times[0]),
            "points": len(times),
        },
        "sampled_mode_count_histogram": {str(key): histogram[key] for key in sorted(histogram)},
        "maximum_sampled_mode_count": maximum_modes,
        "representative_controls_by_mode_count": {
            str(key): examples[key] for key in sorted(examples)
        },
        "vertex_derivatives_at_minimum_analysis_time": vertex_entry_derivatives,
        "vertex_derivatives_at_time_stop": vertex_tail_derivatives,
        "all_vertex_entry_derivatives_positive": bool(min(vertex_entry_derivatives) > 0.0),
        "all_vertex_tail_derivatives_negative": bool(max(vertex_tail_derivatives) < 0.0),
        "interpretation": rules["interpretation"],
    }


def _curve_digest(times: np.ndarray, curves: np.ndarray) -> str:
    digest = hashlib.sha256()
    for array in (times, curves):
        canonical = np.ascontiguousarray(array, dtype="<f8")
        digest.update(str(canonical.shape).encode("ascii"))
        digest.update(canonical.tobytes())
    return digest.hexdigest()


def _validate_manifest_inputs(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest["evidence_timing"] != ("RESULT_INFORMED_REPRODUCTION_NOT_PREREGISTERED_DISCOVERY"):
        raise ValueError("manifest must retain the result-informed evidence label")
    flags = manifest["required_claim_flags"]
    if flags != {
        "continuum_verified": False,
        "project_gate_passed": False,
        "finite_B_Doi_cusp_verified": False,
    }:
        raise ValueError("manifest claim flags must all remain false")
    requirement = manifest["required_inputs"]["g1a_foundation"]
    artifact = REPORT / requirement["artifact"]
    producer = REPORT / requirement["producer_code"]
    if sha256(artifact) != requirement["artifact_sha256"]:
        raise ValueError("pinned G1a artifact hash mismatch")
    if sha256(producer) != requirement["producer_code_sha256"]:
        raise ValueError("pinned G1a producer hash mismatch")
    payload = load_json(artifact)
    for observed, expected, label in (
        (payload["status"], requirement["required_status"], "status"),
        (payload["stage"], requirement["required_stage"], "stage"),
        (
            payload["continuum_verified"],
            requirement["required_continuum_verified"],
            "continuum flag",
        ),
    ):
        if observed != expected:
            raise ValueError(f"pinned G1a {label} mismatch")
    return {
        "artifact": requirement["artifact"],
        "artifact_sha256": sha256(artifact),
        "producer_code": requirement["producer_code"],
        "producer_code_sha256": sha256(producer),
        "status": payload["status"],
        "stage": payload["stage"],
        "continuum_verified": payload["continuum_verified"],
    }


def run() -> dict[str, Any]:
    require_repository_venv()
    manifest = load_json(MANIFEST)
    g1a_preflight = _validate_manifest_inputs(manifest)
    mesh = manifest["design_mesh"]
    grid = FactorGrid(
        midpoint_cells=mesh["midpoint_cells"],
        relative_parallel_cells=mesh["relative_parallel_cells"],
        relative_perp_cells=mesh["relative_perp_cells"],
    )
    if grid.full_state_count != mesh["state_count_if_formed"]:
        raise ValueError("design mesh state count is inconsistent")
    factors = build_free_exposure_factors(grid)
    simplex_rules = manifest["simplex_screen"]
    times = np.linspace(
        simplex_rules["time_start"],
        simplex_rules["time_stop"],
        simplex_rules["time_points"],
        dtype=float,
    )
    if not np.isclose(
        times[1] - times[0],
        simplex_rules["time_spacing"],
        rtol=0.0,
        atol=1.0e-15,
    ):
        raise ValueError("simplex time grid is inconsistent")
    channel_curves = factorized_channel_curves(
        factors,
        times,
        chunk_points=simplex_rules["chunk_points"],
    )
    cusp = reproduce_cusp(factors, manifest)
    inward = verify_inward_direction(factors, channel_curves, times, cusp, manifest)
    simplex = screen_simplex(channel_curves, times, manifest)
    kronecker = full_kronecker_reference(manifest)

    cusp_rules = manifest["cusp_reproduction"]
    inward_rules = manifest["normal_form_inward_check"]
    gates = {
        "result_informed_label_preserved": manifest["evidence_timing"]
        == "RESULT_INFORMED_REPRODUCTION_NOT_PREREGISTERED_DISCOVERY",
        "g1a_input_preflight": g1a_preflight["status"] == "PASS",
        "positive_interior_cusp_weights": min(cusp["weights"]) >= cusp_rules["minimum_weight"],
        "cusp_weights_sum_to_one": abs(sum(cusp["weights"]) - 1.0) <= 2.0e-14,
        "triple_derivative_residual": max(cusp["scaled_derivative_residuals_orders_1_to_3"])
        <= cusp_rules["maximum_scaled_derivative_residual"],
        "nonzero_fourth_derivative": abs(cusp["scaled_fourth_derivative"])
        >= cusp_rules["minimum_absolute_scaled_fourth_derivative"],
        "unfolding_rank_two": cusp["unfolding"]["rank"] == 2,
        "unfolding_conditioning": cusp["unfolding"]["dimensionless_svd_ratio"]
        >= cusp_rules["minimum_dimensionless_unfolding_svd_ratio"],
        "inward_three_roots": inward["root_count"]
        == inward_rules["expected_local_stationary_roots"],
        "inward_max_min_max": inward["topology"] == inward_rules["expected_local_topology"],
        "inward_weights_positive": min(inward["perturbed_weights"]) > 0.0,
        "complete_simplex_enumerated": simplex["control_count"] == simplex_rules["control_count"],
        "simplex_maximum_mode_count_reproduced": simplex["maximum_sampled_mode_count"]
        == simplex_rules["expected_maximum_mode_count"],
        "simplex_vertex_window_bracketed": simplex["all_vertex_entry_derivatives_positive"]
        and simplex["all_vertex_tail_derivatives_negative"],
        "full_kronecker_factorization_reference": kronecker["maximum_scaled_absolute_difference"]
        <= manifest["full_kronecker_reference"]["maximum_scaled_absolute_difference"],
        "negative_claim_flags_preserved": manifest["required_claim_flags"]
        == {
            "continuum_verified": False,
            "project_gate_passed": False,
            "finite_B_Doi_cusp_verified": False,
        },
    }
    passed = bool(all(gates.values()))
    selected_indices = [0, 100, 500, 900, 945, 1000, 2000, 8000]
    result = {
        "schema_version": 1,
        "stage": manifest["stage"],
        "status": (
            "PASS_RESULT_INFORMED_WEAK_BUDGET_DESIGN_DIAGNOSTIC"
            if passed
            else "FAIL_WEAK_BUDGET_DESIGN_DIAGNOSTIC"
        ),
        "evidence_timing": manifest["evidence_timing"],
        "claim_scope": manifest["claim_scope"],
        "continuum_verified": False,
        "project_gate_passed": False,
        "finite_B_Doi_cusp_verified": False,
        "finite_volume_free_factorization_verified": gates[
            "full_kronecker_factorization_reference"
        ],
        "next_theorem_target": (
            "uniform compact-time C4 expansion f_B^(q)=B H^(q)+O(B^2), "
            "followed by positive-B persistence and mesh refinement"
        ),
        "provenance": {
            "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "script": str(HERE.relative_to(REPORT)),
            "script_sha256": sha256(HERE),
            "manifest": str(MANIFEST.relative_to(REPORT)),
            "manifest_sha256": sha256(MANIFEST),
            "protocol_note": manifest["protocol_note"],
            "protocol_note_sha256": sha256(REPORT / manifest["protocol_note"]),
            "g1a_preflight": g1a_preflight,
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
        },
        "design_mesh": mesh,
        "factorization_identity": (
            "h_j^(n)=sum_{q=0}^n binom(n,q) "
            "a_j^(q)c^(n-q), using free-generator actions through n=4"
        ),
        "channel_curve_digest_sha256": _curve_digest(times, channel_curves),
        "selected_channel_jet_samples": [
            {
                "time": float(times[index]),
                "jets_orders_0_to_4_by_channel": channel_curves[:, index, :].tolist(),
            }
            for index in selected_indices
        ],
        "cusp_reproduction": cusp,
        "normal_form_inward_check": inward,
        "simplex_screen": simplex,
        "full_kronecker_reference": kronecker,
        "gates": gates,
        "limitations": [
            "the cusp and current-geometry mode count were known before this reproduction protocol",
            "B=0 first-exposure derivative only; no positive finite-B killed-semigroup cusp is verified",
            "one finite-volume mesh only; continuum_verified remains false",
            "the 0.01 simplex and 0.01 time grids are finite screens, not exhaustive root proofs",
            "the current fixed geometry reaches two sampled modes and is not a trimodality result",
            "the more promising redesigned-centre trimodal wedge remains unfrozen scratch excluded from this artifact claim",
        ],
    }
    return result


def write_result(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    payload = run()
    write_result(args.output, payload)
    cusp = payload["cusp_reproduction"]
    print(f"status={payload['status']}")
    print(
        "cusp="
        f"t={cusp['cusp_time']:.12g}, "
        f"weights={cusp['weights']}, "
        f"scaled_f4={cusp['scaled_fourth_derivative']:.6g}"
    )
    print(
        "simplex="
        f"controls={payload['simplex_screen']['control_count']}, "
        f"max_modes={payload['simplex_screen']['maximum_sampled_mode_count']}"
    )
    print(f"output={args.output}")
    return 0 if payload["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
