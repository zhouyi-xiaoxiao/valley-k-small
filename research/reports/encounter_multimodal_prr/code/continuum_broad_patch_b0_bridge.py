#!/usr/bin/env python3
"""Result-informed exact-continuum to finite-volume B=0 numerical bridge.

This producer is separate from the frozen narrow-patch chain.  It confirms or
rejects a broader, more mesh-resolvable geometry and retains all finite-B,
interval, unbounded-domain-limit, and project-level flags as false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import continuum_g1_smoke as smoke
import continuum_observable_four_patch as continuum
import continuum_weak_budget_design as discrete
import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import brentq
from scipy.sparse.linalg import expm_multiply

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "continuum_broad_patch_b0_bridge_manifest.json"
OUTPUT = DATA / "continuum_broad_patch_b0_bridge_result.json"
TEST_FILE = HERE.with_name("test_continuum_broad_patch_b0_bridge.py")
PROTOCOL = REPORT / "notes" / "broad_patch_b0_bridge_protocol.md"

STAGE = "result_informed_broad_patch_B0_numerical_bridge"
EVIDENCE_TIMING = "RESULT_INFORMED_NUMERICAL_BRIDGE_NOT_PREREGISTERED_DISCOVERY"


@dataclass(frozen=True)
class FVFactors:
    grid: smoke.QuotientGrid2D
    midpoint_generator: sparse.csr_matrix
    relative_generator: sparse.csr_matrix
    midpoint_initial: np.ndarray
    relative_initial: np.ndarray
    patch_profiles: np.ndarray
    contact_profile: np.ndarray
    midpoint_actions: np.ndarray
    relative_actions: np.ndarray
    diagnostics: dict[str, Any]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if type(payload) is not dict:
        raise ValueError(f"{path} must contain one JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def require_repository_venv() -> None:
    if Path(sys.prefix).resolve() != (REPOSITORY / ".venv").resolve():
        raise RuntimeError("broad-patch bridge must run inside the repository .venv")


@contextmanager
def pinned_numpy_global_seed(seed: int) -> Iterator[None]:
    """Make SciPy's legacy-global-RNG norm estimation deterministic and isolated."""

    if type(seed) is not int or seed < 0 or seed > 2**32 - 1:
        raise ValueError("NumPy global seed must be a uint32-compatible integer")
    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)


def parameters_from_manifest(manifest: dict[str, Any]) -> continuum.PhysicalParameters:
    raw = manifest["physical_parameters"]
    parameters = continuum.PhysicalParameters(
        particle_diffusion=float(raw["particle_diffusion"]),
        ou_stiffness=float(raw["ou_stiffness"]),
        ou_mean=float(raw["ou_mean"]),
        transverse_width=float(raw["transverse_width"]),
        contact_radius=float(raw["contact_radius"]),
        midpoint_start=float(raw["midpoint_start"]),
        initial_half_width=float(raw["initial_half_width"]),
        relative_parallel_start=float(raw["relative_parallel_start"]),
        relative_perp_start=float(raw["relative_perp_start"]),
        patch_centres=tuple(float(value) for value in raw["patch_centres"]),
        patch_half_width=float(raw["patch_half_width"]),
        fixed_first_weight=float(raw["fixed_first_weight"]),
    )
    expected = continuum.PhysicalParameters(
        initial_half_width=0.02,
        patch_half_width=0.04,
    )
    if parameters != expected:
        raise ValueError("manifest physical parameters do not match the frozen bridge")
    return parameters


def _generator_row_error(generator: sparse.csr_matrix) -> float:
    return float(np.max(np.abs(np.asarray(generator.sum(axis=1)).reshape(-1))))


def build_fv_factors(
    cells: int,
    parameters: continuum.PhysicalParameters,
    manifest: dict[str, Any],
) -> FVFactors:
    rules = manifest["finite_volume"]
    midpoint_bounds = tuple(float(value) for value in rules["midpoint_bounds"])
    relative_bounds = tuple(float(value) for value in rules["relative_parallel_bounds"])
    grid = smoke.QuotientGrid2D(
        midpoint_cells=cells,
        relative_parallel_cells=cells,
        relative_perp_cells=cells,
        midpoint_bounds=midpoint_bounds,
        relative_parallel_bounds=relative_bounds,
        transverse_width=parameters.transverse_width,
    )
    midpoint_generator = smoke.sg_reflecting_generator(
        grid.midpoint_edges,
        diffusion=parameters.particle_diffusion / 2.0,
        drift=lambda value: -parameters.ou_stiffness * (value - parameters.ou_mean),
    )
    parallel_generator = smoke.sg_reflecting_generator(
        grid.relative_parallel_edges,
        diffusion=2.0 * parameters.particle_diffusion,
        drift=lambda value: -parameters.ou_stiffness * value,
    )
    perpendicular_generator = smoke.periodic_diffusion_generator(
        cells,
        grid.relative_perp_spacing,
        2.0 * parameters.particle_diffusion,
    )
    relative_generator = sparse.kron(
        parallel_generator,
        sparse.eye(cells, format="csr"),
        format="csr",
    ) + sparse.kron(
        sparse.eye(cells, format="csr"),
        perpendicular_generator,
        format="csr",
    )

    patch_profiles = []
    patch_errors = []
    for centre in parameters.patch_centres:
        masses, error = smoke.bump_cell_masses(
            grid.midpoint_edges,
            centre=centre,
            half_width=parameters.patch_half_width,
        )
        patch_profiles.append(masses / grid.midpoint_spacing)
        patch_errors.append(error)
    patch_matrix = np.asarray(patch_profiles, dtype=float)
    contact, contact_area, contact_error = smoke.contact_cell_fractions(
        grid.relative_parallel_edges,
        grid.relative_perp_edges,
        radius=parameters.contact_radius,
    )
    midpoint_initial, midpoint_error = smoke.bump_cell_masses(
        grid.midpoint_edges,
        centre=parameters.midpoint_start,
        half_width=parameters.initial_half_width,
    )
    parallel_initial, parallel_error = smoke.bump_cell_masses(
        grid.relative_parallel_edges,
        centre=parameters.relative_parallel_start,
        half_width=parameters.initial_half_width,
    )
    perpendicular_initial, perpendicular_error = smoke.bump_cell_masses(
        grid.relative_perp_edges,
        centre=parameters.relative_perp_start,
        half_width=parameters.initial_half_width,
        period=parameters.transverse_width,
    )
    relative_initial = np.kron(parallel_initial, perpendicular_initial)
    contact_profile = contact.reshape(-1)
    midpoint_actions = discrete._action_columns(  # noqa: SLF001
        midpoint_generator,
        patch_matrix.T / parameters.transverse_width,
        maximum_order=4,
    )
    relative_actions = discrete._action_columns(  # noqa: SLF001
        relative_generator,
        contact_profile,
        maximum_order=4,
    )
    diagnostics = {
        "cells_per_coordinate": cells,
        "state_count_if_full_matrix_formed": int(cells**3),
        "spacings": {
            "midpoint": grid.midpoint_spacing,
            "relative_parallel": grid.relative_parallel_spacing,
            "relative_perp": grid.relative_perp_spacing,
        },
        "patch_integrals": (np.sum(patch_matrix, axis=1) * grid.midpoint_spacing).tolist(),
        "maximum_patch_quadrature_error_estimate": float(max(patch_errors)),
        "midpoint_initial_mass": float(np.sum(midpoint_initial)),
        "relative_initial_mass": float(np.sum(relative_initial)),
        "maximum_initial_quadrature_error_estimate": float(
            max(midpoint_error, parallel_error, perpendicular_error)
        ),
        "contact_area": float(contact_area),
        "contact_area_exact": float(math.pi * parameters.contact_radius**2),
        "contact_area_error_estimate": float(contact_error),
        "midpoint_generator_row_error": _generator_row_error(midpoint_generator),
        "relative_generator_row_error": _generator_row_error(relative_generator),
    }
    return FVFactors(
        grid=grid,
        midpoint_generator=midpoint_generator,
        relative_generator=relative_generator,
        midpoint_initial=np.asarray(midpoint_initial, dtype=float),
        relative_initial=np.asarray(relative_initial, dtype=float),
        patch_profiles=patch_matrix,
        contact_profile=contact_profile,
        midpoint_actions=midpoint_actions,
        relative_actions=relative_actions,
        diagnostics=diagnostics,
    )


def combine_factor_jets(midpoint: np.ndarray, relative: np.ndarray) -> np.ndarray:
    """Combine four midpoint channels and one contact factor through order four."""

    a = np.asarray(midpoint, dtype=float)
    c = np.asarray(relative, dtype=float)
    if a.shape[0] != 5 or a.shape[-1] != 4 or c.shape[0] != 5:
        raise ValueError("factor jets must have orders zero through four and four channels")
    if a.shape[1:-1] != c.shape[1:]:
        raise ValueError("factor sample axes do not agree")
    output = np.zeros_like(a)
    for order in range(5):
        for left_order in range(order + 1):
            output[order] += (
                math.comb(order, left_order) * a[left_order] * c[order - left_order][..., None]
            )
    return output


def factorized_point(factors: FVFactors, time: float) -> np.ndarray:
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
    midpoint = (midpoint_state @ factors.midpoint_actions).reshape(5, 4)
    relative = (relative_state @ factors.relative_actions).reshape(5)
    return combine_factor_jets(midpoint[:, None, :], relative[:, None])[:, 0, :]


def factorized_curves(
    factors: FVFactors,
    times: np.ndarray,
    *,
    chunk_points: int,
) -> np.ndarray:
    time_values = np.asarray(times, dtype=float)
    midpoint = (
        discrete._projected_curves_chunked(  # noqa: SLF001
            factors.midpoint_generator,
            factors.midpoint_initial,
            factors.midpoint_actions,
            time_values,
            chunk_points=chunk_points,
        )
        .reshape(len(time_values), 5, 4)
        .transpose(1, 0, 2)
    )
    relative = (
        discrete._projected_curves_chunked(  # noqa: SLF001
            factors.relative_generator,
            factors.relative_initial,
            factors.relative_actions,
            time_values,
            chunk_points=chunk_points,
        )
        .reshape(len(time_values), 5)
        .T
    )
    return combine_factor_jets(midpoint, relative)


def fv_cusp(
    factors: FVFactors,
    bracket: tuple[float, float],
    fixed_first_weight: float,
) -> dict[str, Any]:
    def determinant(time: float) -> float:
        jets = factorized_point(factors, time)
        matrix = continuum.affine_cusp_matrix(jets, fixed_first_weight)
        return continuum.row_normalized_determinant(matrix)

    endpoint_values = [determinant(bracket[0]), determinant(bracket[1])]
    if endpoint_values[0] * endpoint_values[1] >= 0.0:
        raise RuntimeError(f"FV cusp bracket lacks a sign change: {endpoint_values}")
    root = float(brentq(determinant, *bracket, xtol=2.0e-11, rtol=1.0e-13))
    metrics = continuum.cusp_metrics(
        factorized_point(factors, root),
        root,
        fixed_first_weight,
    )
    metrics["determinant_at_bracket"] = endpoint_values
    return metrics


def fv_stationary_structure(
    factors: FVFactors,
    curves: np.ndarray,
    times: np.ndarray,
    weights: np.ndarray,
    *,
    minimum_time: float,
    relative_density_floor: float,
) -> dict[str, Any]:
    weight_values = np.asarray(weights, dtype=float)
    density_curve = curves[0] @ weight_values
    derivative_curve = curves[1] @ weight_values
    peak_density = float(np.max(density_curve))
    brackets = [
        (float(times[index]), float(times[index + 1]))
        for index in np.flatnonzero(derivative_curve[:-1] * derivative_curve[1:] < 0.0)
        if times[index] >= minimum_time
    ]

    def derivative(time: float) -> float:
        return float(factorized_point(factors, time)[1] @ weight_values)

    roots = []
    for left, right in brackets:
        root = float(brentq(derivative, left, right, xtol=2.0e-11, rtol=1.0e-13))
        jets = factorized_point(factors, root) @ weight_values
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
    valley_ratios = []
    if [row["topology"] for row in roots] == [
        "maximum",
        "minimum",
        "maximum",
        "minimum",
        "maximum",
    ]:
        for index in (1, 3):
            valley_ratios.append(
                float(
                    roots[index]["density"]
                    / min(roots[index - 1]["density"], roots[index + 1]["density"])
                )
            )
    start_index = int(round(minimum_time / (times[1] - times[0])))
    return {
        "weights": weight_values.tolist(),
        "time_screen": {
            "start": float(times[0]),
            "stop": float(times[-1]),
            "spacing": float(times[1] - times[0]),
            "points": int(len(times)),
        },
        "sampled_sign_change_count": len(brackets),
        "stationary_root_count": len(roots),
        "maximum_count": len(maxima),
        "minimum_count": len(roots) - len(maxima),
        "topology": [row["topology"] for row in roots],
        "roots": roots,
        "peak_minimum_to_maximum_ratio": (
            float(min(row["density"] for row in maxima) / max(row["density"] for row in maxima))
            if maxima
            else 0.0
        ),
        "valley_to_smaller_adjacent_peak_ratios": valley_ratios,
        "derivative_at_minimum_time": float(derivative_curve[start_index]),
        "derivative_at_time_stop": float(derivative_curve[-1]),
    }


def exact_continuum_arm(
    parameters: continuum.PhysicalParameters,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    rules = manifest["exact_continuum"]
    bracket = tuple(float(value) for value in rules["cusp_bracket"])
    primary_model = continuum.FourPatchContinuum(continuum.PRIMARY, parameters)
    fine_model = continuum.FourPatchContinuum(continuum.FINE, parameters)
    primary_cusp, primary_diagnostics = continuum.locate_cusp(primary_model, bracket)
    fine_cusp, fine_diagnostics = continuum.locate_cusp(fine_model, bracket)
    scan = rules["time_screen"]
    times = np.linspace(
        float(scan["start"]),
        float(scan["stop"]),
        int(scan["points"]),
    )
    primary_channels, primary_first = primary_model.real_channels_and_first_derivatives(times)
    direction = np.asarray(primary_cusp["strict_inward_normal"]["direction_4d"], dtype=float)
    base_weights = np.asarray(primary_cusp["weights"], dtype=float)
    eligibility = rules["eligibility"]
    step_rules = rules["candidate_steps"]
    candidates = []
    for step in continuum.candidate_steps(
        float(step_rules["start"]),
        float(step_rules["stop"]),
        float(step_rules["spacing"]),
    ):
        structure = continuum.stationary_structure(
            primary_model,
            base_weights + step * direction,
            times,
            primary_channels,
            primary_first,
            relative_density_floor=float(eligibility["relative_density_floor"]),
            derivative_zero_relative_tolerance=float(
                eligibility["derivative_zero_relative_tolerance"]
            ),
        )
        eligible, gates = continuum.candidate_is_eligible(
            {"stationary_structure": structure},
            minimum_peak_ratio=float(eligibility["minimum_peak_ratio"]),
            maximum_valley_ratio=float(eligibility["maximum_valley_ratio"]),
            minimum_abs_scaled_curvature=float(eligibility["minimum_absolute_scaled_curvature"]),
            maximum_scaled_root_residual=float(eligibility["maximum_scaled_root_residual"]),
        )
        candidates.append(
            {
                "step": step,
                "eligible": eligible,
                "eligibility_gates": gates,
                "stationary_structure": structure,
            }
        )
    selected = continuum.select_candidate(candidates)
    selected_weights = np.asarray(selected["stationary_structure"]["weights"], dtype=float)
    fine_channels, fine_first = fine_model.real_channels_and_first_derivatives(times)
    fine_selected = continuum.stationary_structure(
        fine_model,
        selected_weights,
        times,
        fine_channels,
        fine_first,
        relative_density_floor=float(eligibility["relative_density_floor"]),
        derivative_zero_relative_tolerance=float(eligibility["derivative_zero_relative_tolerance"]),
    )
    fine_eligible, fine_gates = continuum.candidate_is_eligible(
        {"stationary_structure": fine_selected},
        minimum_peak_ratio=float(eligibility["minimum_peak_ratio"]),
        maximum_valley_ratio=float(eligibility["maximum_valley_ratio"]),
        minimum_abs_scaled_curvature=float(eligibility["minimum_absolute_scaled_curvature"]),
        maximum_scaled_root_residual=float(eligibility["maximum_scaled_root_residual"]),
    )
    bridge_steps = {float(value) for value in manifest["bridge_selection"]["candidate_steps"]}
    bridge_candidates = [row for row in candidates if float(row["step"]) in bridge_steps]
    if len(bridge_candidates) != len(bridge_steps):
        raise RuntimeError("bridge candidate steps are not contained in the exact grid")
    fine_bridge_candidates = []
    for candidate in bridge_candidates:
        structure = continuum.stationary_structure(
            fine_model,
            np.asarray(candidate["stationary_structure"]["weights"], dtype=float),
            times,
            fine_channels,
            fine_first,
            relative_density_floor=float(eligibility["relative_density_floor"]),
            derivative_zero_relative_tolerance=float(
                eligibility["derivative_zero_relative_tolerance"]
            ),
        )
        eligible_on_fine, gates_on_fine = continuum.candidate_is_eligible(
            {"stationary_structure": structure},
            minimum_peak_ratio=float(eligibility["minimum_peak_ratio"]),
            maximum_valley_ratio=float(eligibility["maximum_valley_ratio"]),
            minimum_abs_scaled_curvature=float(eligibility["minimum_absolute_scaled_curvature"]),
            maximum_scaled_root_residual=float(eligibility["maximum_scaled_root_residual"]),
        )
        fine_bridge_candidates.append(
            {
                "step": candidate["step"],
                "eligible": eligible_on_fine,
                "eligibility_gates": gates_on_fine,
                "stationary_structure": structure,
            }
        )
    return {
        "primary_cusp": primary_cusp,
        "primary_cusp_diagnostics": primary_diagnostics,
        "fine_cusp": fine_cusp,
        "fine_cusp_diagnostics": fine_diagnostics,
        "cusp_convergence": {
            "time_absolute_difference": abs(primary_cusp["time"] - fine_cusp["time"]),
            "weights_linf_difference": float(
                np.max(
                    np.abs(np.asarray(primary_cusp["weights"]) - np.asarray(fine_cusp["weights"]))
                )
            ),
            "scaled_fourth_derivative_absolute_difference": abs(
                primary_cusp["scaled_fourth_derivative"] - fine_cusp["scaled_fourth_derivative"]
            ),
        },
        "candidate_count": len(candidates),
        "eligible_steps": [row["step"] for row in candidates if row["eligible"]],
        "selected": selected,
        "bridge_candidates": bridge_candidates,
        "fine_bridge_candidates": fine_bridge_candidates,
        "fine_selected_stationary_structure": fine_selected,
        "fine_selected_eligible": fine_eligible,
        "fine_selected_eligibility_gates": fine_gates,
    }


def validate_manifest(manifest: dict[str, Any]) -> dict[str, str]:
    if manifest.get("stage") != STAGE or manifest.get("evidence_timing") != EVIDENCE_TIMING:
        raise ValueError("manifest stage or evidence timing is not frozen")
    if manifest.get("required_claim_flags") != {
        "preregistered_discovery": False,
        "continuum_interval_verified": False,
        "finite_B_Doi_verified": False,
        "unbounded_domain_FV_limit_verified": False,
        "project_gate_passed": False,
    }:
        raise ValueError("mandatory negative claim flags changed")
    if manifest["finite_volume"]["odd_cubic_meshes"] != [65, 97, 129, 193]:
        raise ValueError("frozen mesh sequence changed")
    if manifest["bridge_selection"] != {
        "candidate_steps": [0.11, 0.12, 0.13],
        "required_meshes": [129, 193],
        "priority": [
            "maximum_worst_valley_margin",
            "maximum_worst_peak_ratio",
            "maximum_minimum_weight",
            "smaller_step",
        ],
    }:
        raise ValueError("frozen bridge-selection rule changed")
    if manifest["numerical_reproducibility"] != {
        "numpy_global_seed": 1729,
        "restore_numpy_global_rng_state": True,
        "full_rerun_byte_identity_required": True,
        "reason": "SciPy sparse one-norm estimation uses the legacy NumPy global RNG",
    }:
        raise ValueError("frozen deterministic-execution contract changed")
    observed = {}
    for label, item in manifest["pinned_files"].items():
        path = REPORT / item["path"]
        observed[label] = sha256(path)
        if observed[label] != item["sha256"]:
            raise ValueError(f"pinned {label} hash mismatch")
    return observed


def _run_formal_with_seed_active(manifest: dict[str, Any]) -> dict[str, Any]:
    parameters = parameters_from_manifest(manifest)
    pinned_hashes = validate_manifest(manifest)
    exact = exact_continuum_arm(parameters, manifest)
    exact_cusp_time = float(exact["primary_cusp"]["time"])
    bridge_candidates = exact["bridge_candidates"]
    fine_bridge_by_step = {float(row["step"]): row for row in exact["fine_bridge_candidates"]}

    fv_rules = manifest["finite_volume"]
    screen = fv_rules["time_screen"]
    times = np.linspace(float(screen["start"]), float(screen["stop"]), int(screen["points"]))
    rows = []
    for cells in fv_rules["odd_cubic_meshes"]:
        factors = build_fv_factors(int(cells), parameters, manifest)
        curves = factorized_curves(
            factors,
            times,
            chunk_points=int(screen["chunk_points"]),
        )
        cusp = fv_cusp(
            factors,
            tuple(float(value) for value in fv_rules["cusp_bracket"]),
            parameters.fixed_first_weight,
        )
        candidate_structures = []
        for candidate in bridge_candidates:
            stationary = fv_stationary_structure(
                factors,
                curves,
                times,
                np.asarray(candidate["stationary_structure"]["weights"], dtype=float),
                minimum_time=float(screen["minimum_analysis_time"]),
                relative_density_floor=float(screen["relative_density_floor"]),
            )
            candidate_structures.append(
                {
                    "step": candidate["step"],
                    "exact_primary_eligible": candidate["eligible"],
                    "exact_fine_eligible": fine_bridge_by_step[float(candidate["step"])][
                        "eligible"
                    ],
                    "stationary_structure": stationary,
                }
            )
        rows.append(
            {
                "mesh": [int(cells), int(cells), int(cells)],
                "diagnostics": factors.diagnostics,
                "cusp": cusp,
                "bridge_candidate_stationary_structures": candidate_structures,
                "absolute_error_from_exact_continuum": {
                    "cusp_time": abs(float(cusp["time"]) - exact_cusp_time),
                },
            }
        )

    thresholds = manifest["gates"]
    topology = ["maximum", "minimum", "maximum", "minimum", "maximum"]
    mass_tolerance = float(thresholds["maximum_mass_or_conservation_error"])

    def observable(structure: dict[str, Any]) -> bool:
        ratios = structure["valley_to_smaller_adjacent_peak_ratios"]
        return bool(
            structure["topology"] == topology
            and structure["peak_minimum_to_maximum_ratio"]
            >= float(thresholds["minimum_peak_ratio"])
            and len(ratios) == 2
            and max(ratios) <= float(thresholds["maximum_valley_ratio"])
            and all(
                abs(root["scaled_second_derivative"])
                >= float(thresholds["minimum_absolute_scaled_curvature"])
                and root["scaled_first_derivative_residual"]
                <= float(thresholds["maximum_scaled_root_residual"])
                for root in structure["roots"]
            )
        )

    required_meshes = set(manifest["bridge_selection"]["required_meshes"])
    selection_rows = []
    for candidate in bridge_candidates:
        step = float(candidate["step"])
        target_structures = []
        for row in rows:
            if row["mesh"][0] in required_meshes:
                target_structures.append(
                    next(
                        item["stationary_structure"]
                        for item in row["bridge_candidate_stationary_structures"]
                        if float(item["step"]) == step
                    )
                )
        valley_margins = [
            float(thresholds["maximum_valley_ratio"])
            - max(structure["valley_to_smaller_adjacent_peak_ratios"])
            if len(structure["valley_to_smaller_adjacent_peak_ratios"]) == 2
            else -math.inf
            for structure in target_structures
        ]
        peak_ratios = [
            structure["peak_minimum_to_maximum_ratio"] for structure in target_structures
        ]
        fine_candidate = fine_bridge_by_step[step]
        selection_rows.append(
            {
                "step": step,
                "exact_primary_eligible": bool(candidate["eligible"]),
                "exact_fine_eligible": bool(fine_candidate["eligible"]),
                "required_meshes_observable": len(target_structures) == len(required_meshes)
                and all(observable(structure) for structure in target_structures),
                "worst_valley_margin_across_required_meshes": min(valley_margins),
                "worst_peak_ratio_across_required_meshes": min(peak_ratios),
                "minimum_weight": candidate["stationary_structure"]["minimum_weight"],
            }
        )
    eligible_bridge = [
        row
        for row in selection_rows
        if row["exact_primary_eligible"]
        and row["exact_fine_eligible"]
        and row["required_meshes_observable"]
    ]
    if not eligible_bridge:
        raise RuntimeError("no bridge control passes the frozen required-mesh rule")
    selected_bridge = max(
        eligible_bridge,
        key=lambda row: (
            row["worst_valley_margin_across_required_meshes"],
            row["worst_peak_ratio_across_required_meshes"],
            row["minimum_weight"],
            -row["step"],
        ),
    )
    selected_step = float(selected_bridge["step"])
    exact_selected_candidate = next(
        candidate for candidate in bridge_candidates if float(candidate["step"]) == selected_step
    )
    exact_selected_structure = exact_selected_candidate["stationary_structure"]
    exact_roots = np.asarray(
        [root["time"] for root in exact_selected_structure["roots"]], dtype=float
    )
    for row in rows:
        selected_structure = next(
            item["stationary_structure"]
            for item in row["bridge_candidate_stationary_structures"]
            if float(item["step"]) == selected_step
        )
        root_times = np.asarray([root["time"] for root in selected_structure["roots"]], dtype=float)
        root_error = (
            float(np.max(np.abs(root_times - exact_roots)))
            if root_times.shape == exact_roots.shape
            else None
        )
        row["bridge_selected_control_stationary_structure"] = selected_structure
        row["absolute_error_from_exact_continuum"]["maximum_root_time"] = root_error

    cusp_errors = [row["absolute_error_from_exact_continuum"]["cusp_time"] for row in rows]
    root_errors = [row["absolute_error_from_exact_continuum"]["maximum_root_time"] for row in rows]

    def mesh_normalized(row: dict[str, Any]) -> bool:
        diagnostics = row["diagnostics"]
        errors = [
            max(abs(value - 1.0) for value in diagnostics["patch_integrals"]),
            abs(diagnostics["midpoint_initial_mass"] - 1.0),
            abs(diagnostics["relative_initial_mass"] - 1.0),
            abs(diagnostics["contact_area"] - diagnostics["contact_area_exact"]),
            diagnostics["midpoint_generator_row_error"],
            diagnostics["relative_generator_row_error"],
        ]
        return max(errors) <= mass_tolerance

    finest_structure = rows[-1]["bridge_selected_control_stationary_structure"]
    gates = {
        "result_informed_label_preserved": manifest["evidence_timing"] == EVIDENCE_TIMING,
        "exact_continuum_selected_candidate_eligible": bool(exact["selected"]["eligible"]),
        "exact_continuum_fine_candidate_eligible": bool(exact["fine_selected_eligible"]),
        "bridge_selected_candidate_exact_primary_and_fine_eligible": bool(
            selected_bridge["exact_primary_eligible"] and selected_bridge["exact_fine_eligible"]
        ),
        "bridge_control_passes_required_meshes": bool(
            selected_bridge["required_meshes_observable"]
        ),
        "exact_continuum_primary_fine_cusp_time": exact["cusp_convergence"][
            "time_absolute_difference"
        ]
        <= float(thresholds["maximum_exact_primary_fine_cusp_time_difference"]),
        "exact_continuum_primary_fine_weights": exact["cusp_convergence"]["weights_linf_difference"]
        <= float(thresholds["maximum_exact_primary_fine_weight_difference"]),
        "all_meshes_five_alternating_roots": all(
            row["bridge_selected_control_stationary_structure"]["topology"] == topology
            for row in rows
        ),
        "all_meshes_normalized_and_conservative": all(mesh_normalized(row) for row in rows),
        "cusp_time_error_strictly_decreases": all(
            right < left for left, right in zip(cusp_errors[:-1], cusp_errors[1:], strict=True)
        ),
        "maximum_root_time_error_strictly_decreases": all(
            right is not None and left is not None and right < left
            for left, right in zip(root_errors[:-1], root_errors[1:], strict=True)
        ),
        "finest_cusp_time_error": cusp_errors[-1]
        <= float(thresholds["maximum_finest_cusp_time_error"]),
        "finest_maximum_root_time_error": root_errors[-1] is not None
        and root_errors[-1] <= float(thresholds["maximum_finest_root_time_error"]),
        "finest_peak_ratio": finest_structure["peak_minimum_to_maximum_ratio"]
        >= float(thresholds["minimum_peak_ratio"]),
        "finest_valley_ratios": len(finest_structure["valley_to_smaller_adjacent_peak_ratios"]) == 2
        and max(finest_structure["valley_to_smaller_adjacent_peak_ratios"])
        <= float(thresholds["maximum_valley_ratio"]),
        "mandatory_negative_claim_flags": manifest["required_claim_flags"]
        == {
            "preregistered_discovery": False,
            "continuum_interval_verified": False,
            "finite_B_Doi_verified": False,
            "unbounded_domain_FV_limit_verified": False,
            "project_gate_passed": False,
        },
    }
    passed = bool(all(gates.values()))
    return {
        "schema_version": 1,
        "stage": STAGE,
        "status": (
            "PASS_RESULT_INFORMED_B0_NUMERICAL_BRIDGE"
            if passed
            else "HOLD_RESULT_INFORMED_B0_NUMERICAL_BRIDGE"
        ),
        "evidence_timing": EVIDENCE_TIMING,
        "claim_scope": manifest["claim_scope"],
        "preregistered_discovery": False,
        "continuum_interval_verified": False,
        "finite_B_Doi_verified": False,
        "unbounded_domain_FV_limit_verified": False,
        "project_gate_passed": False,
        "exact_continuum_observability_passed": bool(
            exact["selected"]["eligible"] and exact["fine_selected_eligible"]
        ),
        "finite_volume_B0_bridge_passed": passed,
        "physical_parameters": manifest["physical_parameters"],
        "exact_continuum": exact,
        "bridge_control_selection": {
            "rule": manifest["bridge_selection"],
            "candidate_rows": selection_rows,
            "selected": selected_bridge,
            "exact_continuum_selected_stationary_structure": exact_selected_structure,
        },
        "finite_volume_mesh_rows": rows,
        "convergence_summary": {
            "cusp_time_absolute_errors": cusp_errors,
            "maximum_fixed_control_root_time_absolute_errors": root_errors,
        },
        "gates": gates,
        "all_gates_passed": passed,
        "pinned_file_hashes": pinned_hashes,
        "manifest_sha256": sha256(MANIFEST),
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "limitations": [
            "result-informed geometry and mesh trend, not preregistered discovery",
            "floating-point root screen, not interval-exhaustive certification",
            "finite-volume convergence is on one fixed reflecting box",
            "B=0 free exposure only; no positive-budget killed-Doi solve",
            "no physical d=3 calculation and no project or publication gate",
        ],
    }


def run_formal(manifest: dict[str, Any]) -> dict[str, Any]:
    """Run the full bridge with a manifest-pinned seed and restore caller state."""

    reproducibility = manifest["numerical_reproducibility"]
    seed = int(reproducibility["numpy_global_seed"])
    with pinned_numpy_global_seed(seed):
        result = _run_formal_with_seed_active(manifest)
    result["numerical_reproducibility"] = reproducibility
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-frozen", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    if not args.execute_frozen:
        parser.error("formal execution requires --execute-frozen")
    require_repository_venv()
    manifest = load_json(MANIFEST)
    result = run_formal(manifest)
    write_json(args.output, result)
    print(result["status"])
    finest = result["finite_volume_mesh_rows"][-1]["bridge_selected_control_stationary_structure"]
    print("bridge selected step", result["bridge_control_selection"]["selected"]["step"])
    print("finest valley ratios", finest["valley_to_smaller_adjacent_peak_ratios"])
    print(args.output)
    return 0 if result["all_gates_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
