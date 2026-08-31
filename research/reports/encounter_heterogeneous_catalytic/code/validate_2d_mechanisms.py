#!/usr/bin/env python3
"""Mechanism controls for obstacle-free finite-radius 2D encounters.

This companion to ``validate_2d_finite_radius.py`` answers two distinct
questions that a publication-level positive example must not conflate:

1. Does the two-patch double peak survive when the late catalyst is strictly
   inside the reflecting domain?
2. Are two heterogeneous catalyst patches necessary, or can the transport
   geometry itself generate two separated encounter clocks?

All densities come from the sparse killed CTMC, not Monte Carlo smoothing.
The reaction rule is the finite-radius Doi sink implemented in
``vkcore.encounter2d``.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq
from scipy.sparse.linalg import expm_multiply
from vkcore.encounter2d import (
    DoiCatalyticPatch,
    RectangularGrid2D,
    build_doi_encounter_2d,
    contact_safe_initial_distribution_2d,
    initial_distribution_diagnostics_2d,
    reflecting_advection_diffusion_generator_2d,
    solve_doi_encounter_2d,
)
from vkcore.morphology import MorphologyConfig, analyze_fpt_morphology
from vkcore.plotting import enforce_publication_graphics
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

REACTION_RADIUS = 0.13
START_ONE = (0.10, 0.50)
START_TWO = (0.35, 0.50)
WALKER_ONE = {
    "diffusion": 0.0025,
    "drift_x": 0.18,
    "transverse_confinement": 1.5,
}
WALKER_TWO = {
    "diffusion": 0.0008,
    "drift_x": 0.02,
    "transverse_confinement": 1.5,
}
NEAR_PATCH = DoiCatalyticPatch((0.28, 0.50), 0.12, 0.20, "near")
BOUNDARY_FAR_PATCH = DoiCatalyticPatch((0.90, 0.50), 0.20, 4.00, "far")
INTERIOR_FAR_PATCH = DoiCatalyticPatch((0.75, 0.50), 0.18, 4.00, "far")
INTERIOR_GRIDS = ((9, 5), (11, 7), (13, 9), (15, 11))
SHAPE_TIMES = np.linspace(0.0, 80.0, 801)
INTERIOR_TAIL_TIME = 960.0
CONTROL_TAIL_TIME = 480.0
DOMAIN_TIMES = np.linspace(0.0, 160.0, 801)
DOMAIN_TAIL_TIME = 480.0
DOMAIN_POST_WINDOW_DT = 0.25
DOMAIN_AUDIT_CHUNK_STEPS = 80
DOMAIN_TAIL_GATE = 1e-8
DOMAIN_LENGTHS = ((1.0, 11), (1.5, 16), (2.0, 21), (3.0, 31))
FAMILY_ID = "M2D-C"

MORPHOLOGY = MorphologyConfig(
    smoothing_windows=(1, 3, 5, 9, 15),
    bin_widths=(1, 2, 4, 8, 16),
    bin_offsets=(),
    min_peak_height_rel=0.03,
    min_prominence_rel=0.015,
    min_lobe_mass_rel=0.01,
    min_r_peak=0.05,
    max_r_valley=0.80,
    min_peak_separation_widths=1.0,
    expected_total_mass=1.0,
    mass_tolerance=0.02,
)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _write_json(path: Path, payload: object) -> None:
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _model(
    grid: RectangularGrid2D,
    patches: tuple[DoiCatalyticPatch, ...],
):
    first = reflecting_advection_diffusion_generator_2d(grid, **WALKER_ONE)
    second = reflecting_advection_diffusion_generator_2d(grid, **WALKER_TWO)
    return build_doi_encounter_2d(
        grid,
        first,
        second,
        reaction_radius=REACTION_RADIUS,
        patches=patches,
        centre_weight=0.5,
    )


def _morphology(result):
    dt = float(result.times[1] - result.times[0])
    probability_mass = result.total_flux_density * dt
    probability_mass[[0, -1]] *= 0.5
    return analyze_fpt_morphology(
        probability_mass,
        times=result.times,
        config=MORPHOLOGY,
        tail_mass_upper_bound=result.tail_mass + result.quadrature_closure_error,
    )


def _raw_local_peak_indices(density: np.ndarray) -> np.ndarray:
    return (
        np.flatnonzero(
            (density[1:-1] > density[:-2])
            & (density[1:-1] >= density[2:])
        )
        + 1
    )


def _killed_generator_trace(model: Any) -> float:
    """Return the exact trace used by ``expm_multiply`` trace shifting."""

    return float(np.asarray(model.killed_generator.diagonal(), dtype=float).sum())


def _tail_and_late_maxima(model, initial, *, start: float, stop: float) -> tuple[float, int]:
    audit_times = np.linspace(start, stop, 441)
    states = expm_multiply(
        model.killed_generator.T,
        initial,
        start=float(audit_times[0]),
        stop=float(audit_times[-1]),
        num=audit_times.size,
        endpoint=True,
        traceA=_killed_generator_trace(model),
    )
    density = np.asarray(states @ model.channel_rate_matrix).sum(axis=1)
    return float(np.sum(states[-1])), int(_raw_local_peak_indices(density).size)


def _post_window_stationary_audit(
    model: Any,
    initial: np.ndarray,
    *,
    start: float,
    stop: float,
    dt: float,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Audit the exact finite-CTMC density derivative after the shape window.

    For the column-state convention ``p'(t) = Q.T @ p(t)`` and reaction-rate
    observable ``r``, the density and its first two derivatives are
    ``f = p @ r``, ``f' = p @ (Q @ r)``, and ``f'' = p @ (Q**2 @ r)``.  The
    evolution is chunked so the largest M2D-C domain does not require retaining
    all 1,281 product-state vectors simultaneously.
    """

    step_count = int(round((stop - start) / dt))
    if step_count <= 0 or not np.isclose(start + step_count * dt, stop):
        raise ValueError("post-window audit interval must be an integer multiple of dt")

    generator = model.killed_generator
    transpose = generator.T
    trace = _killed_generator_trace(model)
    rate = np.asarray(model.channel_rate_matrix.sum(axis=1), dtype=float).reshape(-1)
    first_observable = np.asarray(generator @ rate, dtype=float).reshape(-1)
    second_observable = np.asarray(
        generator @ first_observable, dtype=float
    ).reshape(-1)

    scaled_start = transpose * float(start)
    state = np.asarray(
        expm_multiply(
            scaled_start,
            initial,
            traceA=trace * float(start),
        ),
        dtype=float,
    )
    times = [float(start)]
    survival = [float(state.sum())]
    density = [float(state @ rate)]
    first_derivative = [float(state @ first_observable)]
    second_derivative = [float(state @ second_observable)]

    completed_steps = 0
    while completed_steps < step_count:
        chunk_steps = min(DOMAIN_AUDIT_CHUNK_STEPS, step_count - completed_steps)
        duration = float(chunk_steps * dt)
        states = np.asarray(
            expm_multiply(
                transpose,
                state,
                start=0.0,
                stop=duration,
                num=chunk_steps + 1,
                endpoint=True,
                traceA=trace,
            ),
            dtype=float,
        )
        chunk_times = start + (completed_steps + np.arange(1, chunk_steps + 1)) * dt
        times.extend(float(value) for value in chunk_times)
        survival.extend(float(value) for value in states[1:].sum(axis=1))
        density.extend(float(value) for value in states[1:] @ rate)
        first_derivative.extend(float(value) for value in states[1:] @ first_observable)
        second_derivative.extend(
            float(value) for value in states[1:] @ second_observable
        )
        state = states[-1].copy()
        completed_steps += chunk_steps

    times_array = np.asarray(times, dtype=float)
    survival_array = np.asarray(survival, dtype=float)
    density_array = np.asarray(density, dtype=float)
    first_array = np.asarray(first_derivative, dtype=float)
    second_array = np.asarray(second_derivative, dtype=float)
    sign_changes = np.flatnonzero(first_array[:-1] * first_array[1:] < 0.0)
    sampled_zeros = np.flatnonzero(first_array == 0.0)
    local_maxima = _raw_local_peak_indices(density_array)
    local_minima = _raw_local_peak_indices(-density_array)

    stationary_points: list[dict[str, Any]] = []
    for index in sign_changes:
        left = float(times_array[index])
        right = float(times_array[index + 1])
        scaled_left = transpose * left
        left_state = np.asarray(
            expm_multiply(
                scaled_left,
                initial,
                traceA=trace * left,
            ),
            dtype=float,
        )

        def derivative_at(time: float) -> float:
            elapsed = float(time - left)
            if elapsed == 0.0:
                evolved = left_state
            else:
                evolved = np.asarray(
                    expm_multiply(
                        transpose * elapsed,
                        left_state,
                        traceA=trace * elapsed,
                    ),
                    dtype=float,
                )
            return float(evolved @ first_observable)

        root = float(brentq(derivative_at, left, right, xtol=2e-12, rtol=2e-14))
        elapsed = root - left
        root_state = np.asarray(
            expm_multiply(
                transpose * elapsed,
                left_state,
                traceA=trace * elapsed,
            ),
            dtype=float,
        )
        curvature = float(root_state @ second_observable)
        stationary_points.append(
            {
                "time": root,
                "density": float(root_state @ rate),
                "f_t": float(root_state @ first_observable),
                "f_tt": curvature,
                "type": "maximum" if curvature < 0.0 else "minimum",
            }
        )
    for index in sampled_zeros:
        curvature = float(second_array[index])
        stationary_points.append(
            {
                "time": float(times_array[index]),
                "density": float(density_array[index]),
                "f_t": 0.0,
                "f_tt": curvature,
                "type": "maximum" if curvature < 0.0 else "minimum",
            }
        )

    metrics = {
        "post_window_audit_start": float(start),
        "post_window_audit_stop": float(stop),
        "post_window_audit_dt": float(dt),
        "post_window_audit_samples": int(times_array.size),
        "post_window_f_t_min": float(first_array.min()),
        "post_window_f_t_max": float(first_array.max()),
        "post_window_f_tt_min": float(second_array.min()),
        "post_window_f_tt_max": float(second_array.max()),
        "post_window_derivative_strictly_negative": bool(np.all(first_array < 0.0)),
        "post_window_second_derivative_strictly_positive": bool(
            np.all(second_array > 0.0)
        ),
        "post_window_derivative_sign_change_count": int(sign_changes.size),
        "post_window_sampled_zero_derivative_count": int(sampled_zeros.size),
        "post_window_stationary_point_count": len(stationary_points),
        "post_window_stationary_points": stationary_points,
        "post_window_local_maxima": int(local_maxima.size),
        "post_window_local_minima": int(local_minima.size),
        "post_window_local_maximum_times": times_array[local_maxima].tolist(),
        "post_window_local_minimum_times": times_array[local_minima].tolist(),
        "tail_at_480": float(survival_array[-1]),
    }
    series = {
        "times": times_array,
        "survival": survival_array,
        "density": density_array,
        "f_t": first_array,
        "f_tt": second_array,
    }
    return metrics, series


def _strict_stationary_points(model: Any, initial: np.ndarray) -> list[dict[str, Any]]:
    """Detect and Brent-refine sign changes on the declared shape window."""

    states = np.asarray(
        expm_multiply(
            model.killed_generator.T,
            initial,
            start=float(SHAPE_TIMES[0]),
            stop=float(SHAPE_TIMES[-1]),
            num=SHAPE_TIMES.size,
            endpoint=True,
            traceA=_killed_generator_trace(model),
        ),
        dtype=float,
    )
    rate = np.asarray(
        model.channel_rate_matrix.sum(axis=1), dtype=float
    ).reshape(-1)
    first_observable = np.asarray(model.killed_generator @ rate, dtype=float)
    second_observable = np.asarray(
        model.killed_generator @ first_observable, dtype=float
    )
    sampled_first = np.asarray(states @ first_observable, dtype=float)
    brackets = np.flatnonzero(
        np.signbit(sampled_first[:-1]) != np.signbit(sampled_first[1:])
    )
    trace = _killed_generator_trace(model)

    def values(time: float) -> tuple[float, float, float]:
        state = np.asarray(
            expm_multiply(
                model.killed_generator.T * float(time),
                initial,
                traceA=trace * float(time),
            ),
            dtype=float,
        )
        return (
            float(state @ rate),
            float(state @ first_observable),
            float(state @ second_observable),
        )

    roots: list[dict[str, Any]] = []
    for index in brackets:
        root_time = float(
            brentq(
                lambda time: values(time)[1],
                float(SHAPE_TIMES[index]),
                float(SHAPE_TIMES[index + 1]),
                xtol=2e-12,
                rtol=2e-14,
            )
        )
        density, first, second = values(root_time)
        roots.append(
            {
                "time": root_time,
                "density": density,
                "f_t": first,
                "f_tt": second,
                "type": "maximum" if second < 0.0 else "minimum",
            }
        )
    return roots


def _interior_family() -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    archive: dict[str, np.ndarray] = {}
    for nx, ny in INTERIOR_GRIDS:
        grid = RectangularGrid2D(nx, ny)
        model = _model(grid, (NEAR_PATCH, INTERIOR_FAR_PATCH))
        initial = contact_safe_initial_distribution_2d(model, START_ONE, START_TWO)
        initial_diagnostics = initial_distribution_diagnostics_2d(
            model,
            initial,
            walker1_position=START_ONE,
            walker2_position=START_TWO,
        )
        result = solve_doi_encounter_2d(model, initial, SHAPE_TIMES)
        morphology = _morphology(result)
        if morphology.classification != "bimodal":
            raise RuntimeError(f"interior grid {(nx, ny)} is not canonically bimodal")
        valley = morphology.qualifying_valleys[0]
        tail, late_maxima = _tail_and_late_maxima(
            model,
            initial,
            start=float(SHAPE_TIMES[-1]),
            stop=INTERIOR_TAIL_TIME,
        )
        positive_views = int(
            sum(
                len(view.accepted_peak_indices) >= 2
                for view in morphology.scale_views
                if not view.excluded_from_persistence
            )
        )
        rows.append(
            {
                "family_id": FAMILY_ID,
                "branch_id": "interior_two_patch",
                "evidence_relationship": (
                    "four correlated grid resolutions of one M2D-C interior "
                    "two-patch branch, not independent model families"
                ),
                "nx": nx,
                "ny": ny,
                "initial_distribution": asdict(initial_diagnostics),
                "spacing_x": grid.spacing_x,
                "spacing_y": grid.spacing_y,
                "product_states": model.state_count,
                "classification": morphology.classification,
                "peak_early": morphology.modal_peaks[0].time,
                "peak_late": morphology.modal_peaks[1].time,
                "R_peak": valley.r_peak,
                "R_valley": valley.r_valley,
                "separation_widths": valley.separation_widths,
                "positive_scale_views": positive_views,
                "scale_views": len(morphology.scale_views),
                "shape_window_tail": result.tail_mass,
                "tail_at_960": tail,
                "post_window_local_maxima": late_maxima,
                "operator_mass_balance_error": model.operator_mass_balance_error,
                "far_patch_boundary_clearance": 1.0
                - INTERIOR_FAR_PATCH.centre[0]
                - INTERIOR_FAR_PATCH.radius,
                "evidence_grade": (
                    "verified_interior_positive"
                    if tail < 1e-8 and late_maxima == 0 and positive_views >= 145
                    else "conditional"
                ),
            }
        )
        key = f"interior_g{nx}x{ny}"
        archive[f"{key}_times"] = result.times
        archive[f"{key}_density"] = result.total_flux_density
        archive[f"{key}_channels"] = result.channel_flux_density
        archive[f"{key}_survival"] = result.survival
    return rows, archive


def _control_cases() -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    cases = (
        (
            "separated_boundary",
            (NEAR_PATCH, BOUNDARY_FAR_PATCH),
            "bimodal",
            "two spatial reaction opportunities",
        ),
        (
            "single_far",
            (BOUNDARY_FAR_PATCH,),
            "unimodal",
            "one late reaction opportunity",
        ),
        (
            "coalesced_far",
            (
                DoiCatalyticPatch((0.90, 0.50), 0.20, 0.20, "near_label"),
                DoiCatalyticPatch((0.90, 0.50), 0.20, 4.00, "far_label"),
            ),
            "unimodal",
            "two labels but one spatial opportunity",
        ),
        (
            "uniform_reactivity",
            (DoiCatalyticPatch((0.50, 0.50), 2.00, 0.20, "uniform"),),
            "bimodal",
            (
                "one reaction law with transport clocks consistent with a "
                "first-pass/boundary-return interpretation"
            ),
        ),
    )
    rows: list[dict[str, Any]] = []
    archive: dict[str, np.ndarray] = {}
    grid = RectangularGrid2D(11, 7)
    for name, patches, expected, interpretation in cases:
        model = _model(grid, patches)
        initial = contact_safe_initial_distribution_2d(model, START_ONE, START_TWO)
        initial_diagnostics = initial_distribution_diagnostics_2d(
            model,
            initial,
            walker1_position=START_ONE,
            walker2_position=START_TWO,
        )
        result = solve_doi_encounter_2d(model, initial, SHAPE_TIMES)
        morphology = _morphology(result)
        if morphology.classification != expected:
            raise RuntimeError(
                f"control {name} classified {morphology.classification}, expected {expected}"
            )
        tail, late_maxima = _tail_and_late_maxima(
            model,
            initial,
            start=float(SHAPE_TIMES[-1]),
            stop=CONTROL_TAIL_TIME,
        )
        raw = _raw_local_peak_indices(result.total_flux_density)
        strict_points = _strict_stationary_points(model, initial)
        strict_maxima = [
            point for point in strict_points if point["type"] == "maximum"
        ]
        strict_peak_ratio = min(
            float(point["density"]) for point in strict_maxima
        ) / max(float(point["density"]) for point in strict_maxima)
        rows.append(
            {
                "family_id": FAMILY_ID,
                "branch_id": name,
                "evidence_relationship": (
                    "same model as the four-grid M2D-C separated-boundary "
                    "artifact at 11x7; not independent evidence"
                    if name == "separated_boundary"
                    else "separate M2D-C control branch"
                ),
                "case": name,
                "initial_distribution": asdict(initial_diagnostics),
                "classification": morphology.classification,
                "resolved_classification": f"resolved_{morphology.classification}",
                "classification_semantics": (
                    "canonical resolved morphology, not strict stationary-point count"
                ),
                "strict_stationary_points": strict_points,
                "strict_mode_count": len(strict_maxima),
                "strict_secondary_peak_ratio": strict_peak_ratio,
                "modal_peak_times": ";".join(
                    f"{peak.time:.12g}" for peak in morphology.modal_peaks
                ),
                "raw_local_peak_times": ";".join(
                    f"{result.times[index]:.12g}" for index in raw
                ),
                "positive_scale_views": int(
                    sum(
                        len(view.accepted_peak_indices) >= 2
                        for view in morphology.scale_views
                        if not view.excluded_from_persistence
                    )
                ),
                "scale_views": len(morphology.scale_views),
                "shape_window_tail": result.tail_mass,
                "tail_at_480": tail,
                "post_window_local_maxima": late_maxima,
                "channel_count": model.channel_count,
                "interpretation": interpretation,
            }
        )
        archive[f"control_{name}_times"] = result.times
        archive[f"control_{name}_density"] = result.total_flux_density
        archive[f"control_{name}_channels"] = result.channel_flux_density
    return rows, archive


def _domain_scaling() -> tuple[list[dict[str, Any]], dict[str, np.ndarray], dict[str, float]]:
    rows: list[dict[str, Any]] = []
    archive: dict[str, np.ndarray] = {}
    for length_x, nx in DOMAIN_LENGTHS:
        grid = RectangularGrid2D(nx, 7, length_x=length_x)
        uniform_patch = DoiCatalyticPatch(
            (length_x / 2.0, 0.50),
            2.0 * length_x,
            0.20,
            "uniform",
        )
        model = _model(grid, (uniform_patch,))
        initial = contact_safe_initial_distribution_2d(model, START_ONE, START_TWO)
        initial_diagnostics = initial_distribution_diagnostics_2d(
            model,
            initial,
            walker1_position=START_ONE,
            walker2_position=START_TWO,
        )
        result = solve_doi_encounter_2d(model, initial, DOMAIN_TIMES)
        raw = _raw_local_peak_indices(result.total_flux_density)
        if raw.size != 2:
            raise RuntimeError(
                f"uniform domain length {length_x:g} has {raw.size} raw maxima, expected two"
            )
        first_time = float(result.times[raw[0]])
        late_time = float(result.times[raw[1]])
        post_window, post_window_series = _post_window_stationary_audit(
            model,
            initial,
            start=float(DOMAIN_TIMES[-1]),
            stop=DOMAIN_TAIL_TIME,
            dt=DOMAIN_POST_WINDOW_DT,
        )
        tail_complete = bool(post_window["tail_at_480"] < DOMAIN_TAIL_GATE)
        no_late_extrema = bool(
            post_window["post_window_stationary_point_count"] == 0
            and post_window["post_window_local_maxima"] == 0
            and post_window["post_window_local_minima"] == 0
            and post_window["post_window_derivative_strictly_negative"]
            and post_window["post_window_second_derivative_strictly_positive"]
        )
        rows.append(
            {
                "family_id": FAMILY_ID,
                "branch_id": "uniform_reactivity_domain_scaling",
                "evidence_relationship": (
                    "same unit-domain uniform_reactivity control with a longer "
                    "sampling window; not independent model evidence"
                    if length_x == 1.0
                    else "correlated parameter sweep within the same finite-grid "
                    "M2D-C uniform-reactivity domain-scaling branch"
                ),
                "length_x": length_x,
                "initial_distribution": asdict(initial_diagnostics),
                "nx": nx,
                "ny": grid.ny,
                "spacing_x": grid.spacing_x,
                "early_peak": first_time,
                "late_peak": late_time,
                "late_peak_height": float(result.total_flux_density[raw[1]]),
                "tail_at_160": result.tail_mass,
                "slow_walker_boundary_time": (length_x - START_TWO[0])
                / WALKER_TWO["drift_x"],
                **post_window,
                "tail_gate_pass": tail_complete,
                "post_window_no_detected_extrema": no_late_extrema,
                "evidence_grade": (
                    "verified_finite_grid_domain_scaling"
                    if tail_complete and no_late_extrema
                    else "conditional"
                ),
            }
        )
        key = f"uniform_L{str(length_x).replace('.', 'p')}"
        archive[f"{key}_times"] = result.times
        archive[f"{key}_density"] = result.total_flux_density
        for field, values in post_window_series.items():
            archive[f"{key}_post_window_{field}"] = values

    lengths = np.asarray([row["length_x"] for row in rows], dtype=float)
    late_peaks = np.asarray([row["late_peak"] for row in rows], dtype=float)
    slope, intercept = np.polyfit(lengths, late_peaks, 1)
    fitted = slope * lengths + intercept
    residual = late_peaks - fitted
    r_squared = 1.0 - float(np.sum(residual**2)) / float(
        np.sum((late_peaks - late_peaks.mean()) ** 2)
    )
    fit = {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": r_squared,
        "slope_times_slow_drift": float(slope * WALKER_TWO["drift_x"]),
        "max_absolute_residual": float(np.max(np.abs(residual))),
    }
    return rows, archive, fit


def main() -> None:
    interior_rows, interior_archive = _interior_family()
    control_rows, control_archive = _control_cases()
    domain_rows, domain_archive, domain_fit = _domain_scaling()

    interior_json = DATA / "finite_radius_2d_interior_metrics.json"
    interior_csv = DATA / "finite_radius_2d_interior_metrics.csv"
    controls_json = DATA / "finite_radius_2d_control_metrics.json"
    controls_csv = DATA / "finite_radius_2d_control_metrics.csv"
    domain_json = DATA / "finite_radius_2d_domain_scaling.json"
    domain_csv = DATA / "finite_radius_2d_domain_scaling.csv"
    series_npz = DATA / "finite_radius_2d_mechanism_series.npz"
    _write_json(interior_json, interior_rows)
    _write_csv(interior_csv, interior_rows)
    _write_json(controls_json, control_rows)
    _write_csv(controls_csv, control_rows)
    maximum_domain_tail = max(float(row["tail_at_480"]) for row in domain_rows)
    maximum_stationary_points = max(
        int(row["post_window_stationary_point_count"]) for row in domain_rows
    )
    maximum_sampled_extrema = max(
        int(row["post_window_local_maxima"])
        + int(row["post_window_local_minima"])
        for row in domain_rows
    )
    all_derivatives_negative = all(
        bool(row["post_window_derivative_strictly_negative"])
        for row in domain_rows
    )
    all_second_derivatives_positive = all(
        bool(row["post_window_second_derivative_strictly_positive"])
        for row in domain_rows
    )
    domain_payload = {
        "scope": {
            "family_id": FAMILY_ID,
            "branch_id": "uniform_reactivity_domain_scaling",
            "claim_scope": (
                "finite-grid M2D-C uniform-reactivity branch only; the sweep "
                "supports a transport-clock interpretation and is not a "
                "continuum or grid-convergence theorem"
            ),
            "unit_domain_relationship": (
                "Lx=1 is the same unit-domain uniform_reactivity control with "
                "a longer sampling window, not independent model evidence"
            ),
            "domain_lengths": [float(length) for length, _ in DOMAIN_LENGTHS],
            "shape_window": [float(DOMAIN_TIMES[0]), float(DOMAIN_TIMES[-1])],
            "post_window": [float(DOMAIN_TIMES[-1]), DOMAIN_TAIL_TIME],
            "post_window_dt": DOMAIN_POST_WINDOW_DT,
            "post_window_samples": int(
                round(
                    (DOMAIN_TAIL_TIME - float(DOMAIN_TIMES[-1]))
                    / DOMAIN_POST_WINDOW_DT
                )
            )
            + 1,
            "analytic_observables": {
                "density": "f(t) = p(t)^T r",
                "first_derivative": "f'(t) = p(t)^T Q r",
                "second_derivative": "f''(t) = p(t)^T Q^2 r",
            },
        },
        "gates": {
            "tail_completion": {
                "criterion": "max_Lx S_Lx(480) < 1e-8",
                "horizon": DOMAIN_TAIL_TIME,
                "threshold": DOMAIN_TAIL_GATE,
                "observed_maximum": maximum_domain_tail,
                "passed": maximum_domain_tail < DOMAIN_TAIL_GATE,
            },
            "no_post_window_stationary_points": {
                "criterion": (
                    "zero analytic-derivative sign changes or sampled zeros "
                    "and zero sampled local extrema on [160, 480]"
                ),
                "observed_maximum_stationary_points": maximum_stationary_points,
                "observed_maximum_sampled_extrema": maximum_sampled_extrema,
                "passed": maximum_stationary_points == 0
                and maximum_sampled_extrema == 0,
            },
            "strict_post_window_decay": {
                "criterion": "f'(t) < 0 and f''(t) > 0 at all audit samples",
                "all_first_derivatives_negative": all_derivatives_negative,
                "all_second_derivatives_positive": all_second_derivatives_positive,
                "passed": all_derivatives_negative
                and all_second_derivatives_positive,
            },
        },
        "rows": domain_rows,
        "linear_fit": domain_fit,
    }
    _write_json(domain_json, domain_payload)
    _write_csv(domain_csv, domain_rows)
    series_tmp = series_npz.with_name(f".{series_npz.stem}.tmp.npz")
    np.savez_compressed(
        series_tmp,
        **interior_archive,
        **control_archive,
        **domain_archive,
    )
    series_tmp.replace(series_npz)

    figure_pdf = FIGURES / "finite_radius_2d_mechanism_controls.pdf"
    figure_png = FIGURES / "finite_radius_2d_mechanism_controls.png"
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.9))

    ax = axes[0, 0]
    ax.set_aspect("equal")
    for patch, color in zip(
        (NEAR_PATCH, INTERIOR_FAR_PATCH),
        ("#d95f02", "#7570b3"),
        strict=True,
    ):
        ax.add_patch(plt.Circle(patch.centre, patch.radius, color=color, alpha=0.22))
        ax.scatter(*patch.centre, marker="*", s=90, color=color, label=patch.label)
    ax.scatter(*START_ONE, color="#1b9e77", s=55, label="walker 1 start")
    ax.scatter(*START_TWO, color="#66a61e", s=55, label="walker 2 start")
    clearance = interior_rows[-1]["far_patch_boundary_clearance"]
    ax.annotate(
        f"clearance={clearance:.2f}",
        xy=(0.93, 0.50),
        xytext=(0.52, 0.77),
        arrowprops={"arrowstyle": "->", "lw": 0.8},
        fontsize=8,
    )
    ax.set(
        xlim=(0.0, 1.0),
        ylim=(0.0, 1.0),
        xlabel="x",
        ylabel="y",
        title="(a) interior patches",
    )
    ax.legend(frameon=False, fontsize=7, loc="lower right")

    ax = axes[0, 1]
    for nx, ny in INTERIOR_GRIDS:
        key = f"interior_g{nx}x{ny}"
        times = interior_archive[f"{key}_times"]
        density = interior_archive[f"{key}_density"]
        visible = times <= 45.0
        ax.plot(times[visible], density[visible], lw=1.35, label=f"{nx}x{ny}")
    ax.set(
        xlabel="time",
        ylabel="reaction-time density",
        title="(b) interior family by grid",
    )
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    control_styles = {
        "separated_boundary": ("black", "separated"),
        "single_far": ("#1b9e77", "far only"),
        "coalesced_far": ("#d95f02", "co-located"),
        "uniform_reactivity": ("#7570b3", "uniform"),
    }
    for name, (color, label) in control_styles.items():
        times = control_archive[f"control_{name}_times"]
        density = control_archive[f"control_{name}_density"]
        visible = times <= 45.0
        ax.plot(times[visible], density[visible], color=color, lw=1.45, label=label)
    ax.set(
        xlabel="time",
        ylabel="reaction-time density",
        title="(c) mechanism controls",
    )
    ax.legend(frameon=False, fontsize=7)

    ax = axes[1, 1]
    lengths = np.asarray([row["length_x"] for row in domain_rows])
    late_peaks = np.asarray([row["late_peak"] for row in domain_rows])
    dense_lengths = np.linspace(lengths.min(), lengths.max(), 100)
    ax.plot(lengths, late_peaks, "o", color="#7570b3", label="late peak")
    ax.plot(
        dense_lengths,
        domain_fit["slope"] * dense_lengths + domain_fit["intercept"],
        "--",
        color="black",
        label=rf"fit: slope={domain_fit['slope']:.2f}, $R^2$={domain_fit['r_squared']:.4f}",
    )
    ax.set(
        xlabel=r"domain length $L_x$",
        ylabel="late peak time",
        title="(d) boundary clock versus size",
    )
    ax.legend(frameon=False, fontsize=7)

    for ax in axes.reshape(-1):
        ax.grid(alpha=0.18)
    enforce_publication_graphics(fig)
    fig.tight_layout()
    temporary_pdf = figure_pdf.with_name(
        f".{figure_pdf.stem}.tmp{figure_pdf.suffix}"
    )
    temporary_png = figure_png.with_name(
        f".{figure_png.stem}.tmp{figure_png.suffix}"
    )
    fig.savefig(temporary_pdf)
    fig.savefig(temporary_png, dpi=300)
    temporary_pdf.replace(figure_pdf)
    temporary_png.replace(figure_png)
    plt.close(fig)

    outputs = [
        interior_json,
        interior_csv,
        controls_json,
        controls_csv,
        domain_json,
        domain_csv,
        series_npz,
        figure_pdf,
        figure_png,
    ]
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=["python", str(HERE.relative_to(REPO))],
        model_spec={
            "family_id": FAMILY_ID,
            "separated_boundary_evidence_relationship": (
                "the 11x7 separated-boundary curve is the same M2D-C model as "
                "the four-grid finite_radius_2d artifact, not an independent "
                "replication"
            ),
            "domain": "reflecting obstacle-free rectangle",
            "reaction_model": "finite-radius Doi volume sink",
            "discretization": "boundary-node nearest-neighbour lattice CTMC with binary masks",
            "catalytic_coordinate": "arithmetic midpoint C_eta with eta=0.5",
            "reaction_radius": REACTION_RADIUS,
            "start_one": START_ONE,
            "start_two": START_TWO,
            "walker_one": WALKER_ONE,
            "walker_two": WALKER_TWO,
            "initial_distribution": (
                "hierarchical contact-safe selector: minimum physical Euclidean "
                "spread on the smallest feasible local stencil, followed by a "
                "strictly convex closest-to-product QP on the optimal LP face; "
                "exact product-bilinear return when already contact-safe"
            ),
            "near_patch": asdict(NEAR_PATCH),
            "boundary_far_patch": asdict(BOUNDARY_FAR_PATCH),
            "interior_far_patch": asdict(INTERIOR_FAR_PATCH),
            "interior_grids": [list(value) for value in INTERIOR_GRIDS],
            "uniform_domain_lengths": [list(value) for value in DOMAIN_LENGTHS],
        },
        classifier_spec=asdict(MORPHOLOGY),
        dependencies=[
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter2d.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "morphology.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
        ],
        outputs=outputs,
        horizon={
            "shape_tmax": float(SHAPE_TIMES[-1]),
            "shape_dt": float(SHAPE_TIMES[1] - SHAPE_TIMES[0]),
            "interior_tail_time": INTERIOR_TAIL_TIME,
            "control_tail_time": CONTROL_TAIL_TIME,
            "domain_scaling_tmax": float(DOMAIN_TIMES[-1]),
            "domain_tail_time": DOMAIN_TAIL_TIME,
            "domain_post_window_dt": DOMAIN_POST_WINDOW_DT,
            "domain_tail_gate": DOMAIN_TAIL_GATE,
        },
    )
    manifest_path = DATA / "finite_radius_2d_mechanisms.manifest.json"
    manifest_tmp = DATA / ".finite_radius_2d_mechanisms.manifest.tmp.json"
    write_manifest(manifest_tmp, manifest)
    manifest_tmp.replace(manifest_path)


if __name__ == "__main__":
    main()
