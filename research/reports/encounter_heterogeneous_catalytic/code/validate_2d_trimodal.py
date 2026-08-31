#!/usr/bin/env python3
"""Finite-radius 2D trimodality certificate on reflecting rectangles.

The calculation fixes one obstacle-free two-walker Doi model and checks it on
four grids using a joint contact-safe initial law.  The three finer grids must
have three classifier-resolved modes.  All four grids must retain five
detected simple positive-time stationary roots and an ordered near/middle/far
channel attribution; the coarsest is explicitly recorded as a classifier
shoulder.  Sparse matrix exponentials and generator actions are used
throughout; finite differences are not used to locate or classify stationary
points.

This is deliberately an independent validation target.  It does not alter the
matched-fold calculation or the main manuscript.
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
from matplotlib.patches import Circle, Rectangle
from scipy import sparse
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
NOTE = REPORT / "notes" / "finite_radius_2d_trimodality.md"
DATA.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

GRIDS = ((9, 5), (11, 7), (13, 9), (15, 11))
REACTION_RADIUS = 0.13
START_ONE = (0.05, 0.50)
START_TWO = (0.20, 0.50)
WALKER_ONE = {
    "diffusion": 0.0025,
    "drift_x": 0.10,
    "transverse_confinement": 1.5,
}
WALKER_TWO = {
    "diffusion": 0.0008,
    "drift_x": 0.02,
    "transverse_confinement": 1.5,
}
PATCHES = (
    DoiCatalyticPatch((0.20, 0.50), 0.06, 0.03, "near"),
    DoiCatalyticPatch((0.70, 0.50), 0.05, 1.00, "middle"),
    DoiCatalyticPatch((0.94, 0.50), 0.05, 0.05, "far"),
)

SHAPE_TIMES = np.linspace(0.0, 400.0, 2001)
ROOT_FINE_STOP = 100.0
ROOT_FINE_DT = 0.02
ROOT_TAIL_DT = 1.0
ROOT_AUDIT_STOP = 2000.0

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
    mass_tolerance=0.03,
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


def _model(grid: RectangularGrid2D):
    first = reflecting_advection_diffusion_generator_2d(grid, **WALKER_ONE)
    second = reflecting_advection_diffusion_generator_2d(grid, **WALKER_TWO)
    return build_doi_encounter_2d(
        grid,
        first,
        second,
        reaction_radius=REACTION_RADIUS,
        patches=PATCHES,
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


def _raw_local_peak_indices(values: np.ndarray) -> np.ndarray:
    return (
        np.flatnonzero(
            (values[1:-1] > values[:-2])
            & (values[1:-1] >= values[2:])
        )
        + 1
    )


def _generator_vectors(model) -> tuple[np.ndarray, ...]:
    total_rate = np.asarray(model.channel_rate_matrix.sum(axis=1)).reshape(-1)
    vectors = [total_rate]
    for _ in range(3):
        vectors.append(np.asarray(model.killed_generator @ vectors[-1]).reshape(-1))
    return tuple(vectors)


def _scan_segment(
    model,
    state: np.ndarray,
    *,
    start: float,
    stop: float,
    dt: float,
    chunk_span: float,
    vectors: tuple[np.ndarray, ...],
) -> tuple[np.ndarray, tuple[np.ndarray, ...], np.ndarray]:
    """Evaluate f and three finite-matrix semigroup derivatives in chunks."""

    time_parts: list[np.ndarray] = []
    value_parts: list[list[np.ndarray]] = [[] for _ in vectors]
    current_time = float(start)
    current_state = np.asarray(state, dtype=float)
    first_chunk = True
    while current_time < stop - 1e-12:
        end = min(float(stop), current_time + chunk_span)
        count = int(round((end - current_time) / dt)) + 1
        states = expm_multiply(
            model.killed_generator.T,
            current_state,
            start=0.0,
            stop=end - current_time,
            num=count,
            endpoint=True,
        )
        local_times = np.linspace(current_time, end, count)
        selection = slice(None) if first_chunk else slice(1, None)
        time_parts.append(local_times[selection])
        for position, vector in enumerate(vectors):
            value_parts[position].append(np.asarray(states @ vector)[selection])
        current_state = np.asarray(states[-1])
        current_time = end
        first_chunk = False
    return (
        np.concatenate(time_parts),
        tuple(np.concatenate(parts) for parts in value_parts),
        current_state,
    )


def _root_audit(model, initial: np.ndarray) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, np.ndarray]]:
    vectors = _generator_vectors(model)
    fine_times, fine_values, state_at_fine_stop = _scan_segment(
        model,
        initial,
        start=0.0,
        stop=ROOT_FINE_STOP,
        dt=ROOT_FINE_DT,
        chunk_span=20.0,
        vectors=vectors,
    )
    tail_times, tail_values, _ = _scan_segment(
        model,
        state_at_fine_stop,
        start=ROOT_FINE_STOP,
        stop=ROOT_AUDIT_STOP,
        dt=ROOT_TAIL_DT,
        chunk_span=200.0,
        vectors=vectors,
    )
    audit_times = np.concatenate((fine_times, tail_times[1:]))
    audit_values = tuple(
        np.concatenate((fine_values[index], tail_values[index][1:]))
        for index in range(len(vectors))
    )
    density, first_derivative, second_derivative, third_derivative = audit_values
    sign_changes = np.flatnonzero(first_derivative[:-1] * first_derivative[1:] < 0.0)

    trace = float(model.killed_generator.diagonal().sum())

    def semigroup_values(time: float) -> tuple[np.ndarray, np.ndarray, float]:
        state = expm_multiply(
            model.killed_generator.T * float(time),
            initial,
            traceA=trace * float(time),
        )
        derivatives = np.asarray([float(state @ vector) for vector in vectors])
        channels = np.asarray(state @ model.channel_rate_matrix).reshape(-1)
        return derivatives, channels, float(np.sum(state))

    root_rows: list[dict[str, Any]] = []
    for number, bracket_index in enumerate(sign_changes, start=1):
        left = float(audit_times[bracket_index])
        right = float(audit_times[bracket_index + 1])
        root = brentq(
            lambda time: float(semigroup_values(time)[0][1]),
            left,
            right,
            xtol=1e-12,
            rtol=1e-13,
        )
        derivatives, channels, survival = semigroup_values(root)
        root_type = "maximum" if derivatives[2] < 0.0 else "minimum"
        dominant = int(np.argmax(channels))
        root_rows.append(
            {
                "root_number": number,
                "time": root,
                "type": root_type,
                "density": float(derivatives[0]),
                "f_t": float(derivatives[1]),
                "f_tt": float(derivatives[2]),
                "f_ttt": float(derivatives[3]),
                "near_flux": float(channels[0]),
                "middle_flux": float(channels[1]),
                "far_flux": float(channels[2]),
                "dominant_channel": PATCHES[dominant].label,
                "dominant_share": float(channels[dominant] / derivatives[0]),
                "survival": survival,
                "bracket_left": left,
                "bracket_right": right,
            }
        )

    if len(root_rows) != 5:
        raise RuntimeError(
            "expected five detected derivative roots in the declared audit window, "
            f"found {len(root_rows)}"
        )
    expected_types = ["maximum", "minimum", "maximum", "minimum", "maximum"]
    if [row["type"] for row in root_rows] != expected_types:
        raise RuntimeError("stationary roots do not alternate max/min/max/min/max")

    last_root = float(root_rows[-1]["time"])
    after_last = audit_times >= last_root + 0.5
    if not np.all(first_derivative[after_last] < 0.0):
        raise RuntimeError("positive derivative found after the third maximum")
    local_steps = np.where(audit_times <= ROOT_FINE_STOP, ROOT_FINE_DT, ROOT_TAIL_DT)
    no_root_ratio = (-first_derivative[after_last]) / (
        np.abs(second_derivative[after_last]) * local_steps[after_last] + 1e-300
    )

    # Search for unresolved even-multiplicity stationary points through the
    # logarithmic slope, excluding declared roots by a conservative buffer.
    log_slope = first_derivative / np.maximum(density, 1e-300)
    away = np.ones_like(audit_times, dtype=bool)
    for row in root_rows:
        buffer = 0.10 if row["time"] <= ROOT_FINE_STOP else 2.0
        away &= np.abs(audit_times - float(row["time"])) >= buffer
    away &= density > 1e-14 * float(np.max(density))
    abs_log_slope = np.abs(log_slope)
    local_minima = (
        np.flatnonzero(
            (abs_log_slope[1:-1] <= abs_log_slope[:-2])
            & (abs_log_slope[1:-1] <= abs_log_slope[2:])
            & away[1:-1]
        )
        + 1
    )
    tangency_floor = (
        float(np.min(abs_log_slope[local_minima]))
        if local_minima.size
        else float(np.min(abs_log_slope[away]))
    )
    post_shape = audit_times >= float(SHAPE_TIMES[-1])
    diagnostics = {
        "scan_start": 0.0,
        "scan_stop": ROOT_AUDIT_STOP,
        "fine_scan_stop": ROOT_FINE_STOP,
        "fine_dt": ROOT_FINE_DT,
        "tail_dt": ROOT_TAIL_DT,
        "scan_sample_count": int(audit_times.size),
        "sign_change_root_count": int(sign_changes.size),
        "post_shape_sign_change_count": int(
            np.sum(
                first_derivative[:-1][post_shape[:-1]]
                * first_derivative[1:][post_shape[:-1]]
                < 0.0
            )
        ),
        "derivative_at_zero": float(first_derivative[0]),
        "derivative_at_audit_stop": float(first_derivative[-1]),
        "density_at_audit_stop": float(density[-1]),
        "minimum_tail_no_root_ratio": float(np.min(no_root_ratio)),
        "minimum_off_root_abs_log_slope": tangency_floor,
        "minimum_root_abs_curvature": float(
            min(abs(float(row["f_tt"])) for row in root_rows)
        ),
        "maximum_root_abs_f_t": float(
            max(abs(float(row["f_t"])) for row in root_rows)
        ),
    }
    archive = {
        "audit_times": audit_times,
        "audit_density": density,
        "audit_f_t": first_derivative,
        "audit_f_tt": second_derivative,
        "audit_f_ttt": third_derivative,
    }
    return root_rows, diagnostics, archive


def _integrated_channel_masses(model, initial: np.ndarray) -> dict[str, Any]:
    """Integrate all channel fluxes by one augmented sparse exponential."""

    state_count = model.state_count
    channel_count = model.channel_count
    zero_top = sparse.csr_matrix((state_count, channel_count))
    zero_bottom = sparse.csr_matrix((channel_count, channel_count))
    augmented = sparse.bmat(
        [
            [model.killed_generator.T, zero_top],
            [model.channel_rate_matrix.T, zero_bottom],
        ],
        format="csr",
    )
    augmented_initial = np.concatenate((initial, np.zeros(channel_count)))
    trace = float(model.killed_generator.diagonal().sum())
    final = expm_multiply(
        augmented * ROOT_AUDIT_STOP,
        augmented_initial,
        traceA=trace * ROOT_AUDIT_STOP,
    )
    state = np.asarray(final[:state_count])
    masses = np.asarray(final[state_count:])
    survival = float(np.sum(state))
    total_rate = np.asarray(model.channel_rate_matrix.sum(axis=1)).reshape(-1)
    tail_density = float(state @ total_rate)
    tail_derivative = float(state @ (model.killed_generator @ total_rate))
    return {
        "channel_masses": masses.tolist(),
        "channel_mass_sum": float(np.sum(masses)),
        "tail_survival": survival,
        "tail_density": tail_density,
        "tail_derivative": tail_derivative,
        "augmented_closure_error": abs(float(np.sum(masses)) + survival - 1.0),
    }


def _classifier_margins(morphology) -> dict[str, float]:
    modal = morphology.modal_peaks
    valleys = morphology.qualifying_valleys
    return {
        "min_peak_height_margin": float(
            min(peak.relative_height for peak in modal) - MORPHOLOGY.min_peak_height_rel
        ),
        "min_prominence_margin": float(
            min(peak.relative_prominence for peak in modal)
            - MORPHOLOGY.min_prominence_rel
        ),
        "min_lobe_mass_margin": float(
            min(peak.relative_lobe_mass for peak in modal)
            - MORPHOLOGY.min_lobe_mass_rel
        ),
        "min_r_peak_margin": float(
            min(valley.r_peak for valley in valleys) - MORPHOLOGY.min_r_peak
        ),
        "min_valley_margin": float(
            MORPHOLOGY.max_r_valley - max(valley.r_valley for valley in valleys)
        ),
        "min_separation_width_margin": float(
            min(valley.separation_widths for valley in valleys)
            - MORPHOLOGY.min_peak_separation_widths
        ),
    }


def _analyse_grid(nx: int, ny: int) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, np.ndarray]]:
    grid = RectangularGrid2D(nx, ny)
    model = _model(grid)
    initial = contact_safe_initial_distribution_2d(model, START_ONE, START_TWO)
    initial_diagnostics = initial_distribution_diagnostics_2d(
        model,
        initial,
        walker1_position=START_ONE,
        walker2_position=START_TWO,
    )
    result = solve_doi_encounter_2d(model, initial, SHAPE_TIMES)
    morphology = _morphology(result)
    raw_indices = _raw_local_peak_indices(result.total_flux_density)
    root_rows, root_diagnostics, root_archive = _root_audit(model, initial)
    mass_audit = _integrated_channel_masses(model, initial)

    resolved_trimodal = (
        morphology.classification == "multimodal" and morphology.mode_count == 3
    )
    if (nx, ny) == (9, 5):
        if morphology.classification != "shoulder" or morphology.mode_count != 1:
            raise RuntimeError("contact-safe 9x5 grid did not retain its shoulder")
    elif not resolved_trimodal:
        raise RuntimeError(f"grid {(nx, ny)} is not canonically trimodal")
    if raw_indices.size != 3:
        raise RuntimeError(f"grid {(nx, ny)} does not have exactly three raw peaks")
    if resolved_trimodal and len(morphology.qualifying_valleys) != 2:
        raise RuntimeError(f"grid {(nx, ny)} lost a resolved classifier valley")
    maxima = [row for row in root_rows if row["type"] == "maximum"]
    if [row["dominant_channel"] for row in maxima] != ["near", "middle", "far"]:
        raise RuntimeError(f"grid {(nx, ny)} lost ordered channel attribution")
    if min(float(row["dominant_share"]) for row in maxima) <= 0.50:
        raise RuntimeError(f"grid {(nx, ny)} has a non-dominant nominal peak channel")

    adjacent_prominences: list[float] = []
    for left, valley, right in (
        (root_rows[0], root_rows[1], root_rows[2]),
        (root_rows[2], root_rows[3], root_rows[4]),
    ):
        adjacent_prominences.extend(
            (
                float(left["density"]) - float(valley["density"]),
                float(right["density"]) - float(valley["density"]),
            )
        )
    if min(adjacent_prominences) <= 0.0:
        raise RuntimeError(f"grid {(nx, ny)} has a nonpositive raw prominence")

    if resolved_trimodal:
        margins: dict[str, float | None] = _classifier_margins(morphology)
        if min(value for value in margins.values() if value is not None) <= 0.0:
            raise RuntimeError(f"grid {(nx, ny)} has a nonpositive classifier margin")
    else:
        margins = {
            "min_peak_height_margin": None,
            "min_prominence_margin": None,
            "min_lobe_mass_margin": None,
            "min_r_peak_margin": None,
            "min_valley_margin": None,
            "min_separation_width_margin": None,
        }

    positive_scale_views = int(
        sum(
            len(view.accepted_peak_indices) >= 3
            for view in morphology.scale_views
            if not view.excluded_from_persistence
        )
    )
    row: dict[str, Any] = {
        "nx": nx,
        "ny": ny,
        "spacing_x": grid.spacing_x,
        "spacing_y": grid.spacing_y,
        "product_states": model.state_count,
        "initial_distribution": asdict(initial_diagnostics),
        "reactive_state_counts": model.reactive_state_counts.tolist(),
        "resolution_diagnostics": {
            "interpretation": (
                "finite-lattice mechanism; binary patch supports are not "
                "spatially resolved as continuum disks"
            ),
            "reaction_radius_over_spacing_x": REACTION_RADIUS / grid.spacing_x,
            "reaction_radius_over_spacing_y": REACTION_RADIUS / grid.spacing_y,
            "patch_radius_over_spacing_x": [
                patch.radius / grid.spacing_x for patch in PATCHES
            ],
            "patch_radius_over_spacing_y": [
                patch.radius / grid.spacing_y for patch in PATCHES
            ],
            "all_patch_radii_below_spacing_x": all(
                patch.radius < grid.spacing_x for patch in PATCHES
            ),
            "walker_one_cell_peclet_x": (
                abs(WALKER_ONE["drift_x"])
                * grid.spacing_x
                / WALKER_ONE["diffusion"]
            ),
            "walker_two_cell_peclet_x": (
                abs(WALKER_TWO["drift_x"])
                * grid.spacing_x
                / WALKER_TWO["diffusion"]
            ),
            "walker_one_one_cell_from_centre_peclet_y": (
                WALKER_ONE["transverse_confinement"]
                * grid.spacing_y**2
                / WALKER_ONE["diffusion"]
            ),
            "walker_two_one_cell_from_centre_peclet_y": (
                WALKER_TWO["transverse_confinement"]
                * grid.spacing_y**2
                / WALKER_TWO["diffusion"]
            ),
        },
        "operator_mass_balance_error": model.operator_mass_balance_error,
        "classification": morphology.classification,
        "mode_count": morphology.mode_count,
        "raw_local_peak_count": int(raw_indices.size),
        "raw_peak_times": result.times[raw_indices].tolist(),
        "classifier_peak_times": [peak.time for peak in morphology.modal_peaks],
        "classifier_peak_relative_heights": [
            peak.relative_height for peak in morphology.modal_peaks
        ],
        "classifier_peak_relative_prominences": [
            peak.relative_prominence for peak in morphology.modal_peaks
        ],
        "classifier_peak_relative_lobe_masses": [
            peak.relative_lobe_mass for peak in morphology.modal_peaks
        ],
        "valley_r_peak": [valley.r_peak for valley in morphology.qualifying_valleys],
        "valley_r_valley": [
            valley.r_valley for valley in morphology.qualifying_valleys
        ],
        "valley_separation_widths": [
            valley.separation_widths for valley in morphology.qualifying_valleys
        ],
        "classifier_tail_certified": morphology.tail_certificate.certified,
        "positive_three_peak_scale_views": positive_scale_views,
        "shape_tail_mass": result.tail_mass,
        "shape_quadrature_closure_error": result.quadrature_closure_error,
        "channel_decomposition_error": result.channel_decomposition_error,
        "root_detection_schema_version": 2,
        "detected_root_times": [entry["time"] for entry in root_rows],
        "detected_root_types": [entry["type"] for entry in root_rows],
        "detected_peak_dominant_channels": [
            entry["dominant_channel"] for entry in maxima
        ],
        "detected_peak_dominant_shares": [
            entry["dominant_share"] for entry in maxima
        ],
        "deprecated_fields": {
            "exact_root_times": "detected_root_times",
            "exact_root_types": "detected_root_types",
            "exact_peak_dominant_channels": "detected_peak_dominant_channels",
            "exact_peak_dominant_shares": "detected_peak_dominant_shares",
        },
        "exact_root_times": [entry["time"] for entry in root_rows],
        "exact_root_types": [entry["type"] for entry in root_rows],
        "exact_peak_dominant_channels": [
            entry["dominant_channel"] for entry in maxima
        ],
        "exact_peak_dominant_shares": [
            entry["dominant_share"] for entry in maxima
        ],
        "minimum_raw_adjacent_prominence": min(adjacent_prominences),
        "minimum_raw_adjacent_prominence_rel": min(adjacent_prominences)
        / max(float(entry["density"]) for entry in maxima),
        **margins,
        **root_diagnostics,
        **mass_audit,
        "evidence_grade": (
            "verified_finite_grid_trimodality"
            if resolved_trimodal
            else "verified_five_root_contact_safe_shoulder"
        ),
    }

    prefix = f"g{nx}x{ny}"
    archive = {
        f"{prefix}_times": result.times,
        f"{prefix}_total_density": result.total_flux_density,
        f"{prefix}_channel_density": result.channel_flux_density,
        f"{prefix}_survival": result.survival,
        f"{prefix}_root_times": np.asarray(row["detected_root_times"]),
        **{f"{prefix}_{key}": value for key, value in root_archive.items()},
    }
    for root_row in root_rows:
        root_row["nx"] = nx
        root_row["ny"] = ny
    return row, root_rows, archive


def _flat_grid_row(row: dict[str, Any]) -> dict[str, Any]:
    roots = row["detected_root_times"]
    return {
        "nx": row["nx"],
        "ny": row["ny"],
        "spacing_x": row["spacing_x"],
        "spacing_y": row["spacing_y"],
        "product_states": row["product_states"],
        "reactive_near": row["reactive_state_counts"][0],
        "reactive_middle": row["reactive_state_counts"][1],
        "reactive_far": row["reactive_state_counts"][2],
        "classification": row["classification"],
        "mode_count": row["mode_count"],
        "peak_1_time": roots[0],
        "valley_1_time": roots[1],
        "peak_2_time": roots[2],
        "valley_2_time": roots[3],
        "peak_3_time": roots[4],
        "valley_1_ratio": (
            row["valley_r_valley"][0] if row["valley_r_valley"] else None
        ),
        "valley_2_ratio": (
            row["valley_r_valley"][1] if row["valley_r_valley"] else None
        ),
        "minimum_classifier_margin": (
            min(
                row["min_peak_height_margin"],
                row["min_prominence_margin"],
                row["min_lobe_mass_margin"],
                row["min_r_peak_margin"],
                row["min_valley_margin"],
                row["min_separation_width_margin"],
            )
            if row["min_peak_height_margin"] is not None
            else None
        ),
        "minimum_raw_prominence_rel": row["minimum_raw_adjacent_prominence_rel"],
        "near_peak_share": row["detected_peak_dominant_shares"][0],
        "middle_peak_share": row["detected_peak_dominant_shares"][1],
        "far_peak_share": row["detected_peak_dominant_shares"][2],
        "tail_at_2000": row["tail_survival"],
        "post_shape_roots": row["post_shape_sign_change_count"],
        "root_residual": row["maximum_root_abs_f_t"],
        "operator_error": row["operator_mass_balance_error"],
    }


def _make_figure(rows: list[dict[str, Any]], archive: dict[str, np.ndarray]) -> tuple[Path, Path]:
    figure_pdf = FIGURES / "finite_radius_2d_trimodality.pdf"
    figure_png = FIGURES / "finite_radius_2d_trimodality.png"
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 7.6))

    ax = axes[0, 0]
    ax.add_patch(Rectangle((0, 0), 1, 1, fill=False, lw=1.5, color="black"))
    patch_colors = ("#1b9e77", "#d95f02", "#7570b3")
    for patch, color in zip(PATCHES, patch_colors, strict=True):
        ax.add_patch(
            Circle(patch.centre, patch.radius, color=color, alpha=0.28, lw=1.5)
        )
        label_above = patch.label != "far"
        label_y = patch.centre[1] + (
            patch.radius + 0.035 if label_above else -patch.radius - 0.035
        )
        ax.text(
            patch.centre[0],
            label_y,
            f"{patch.label}\n$\\kappa={patch.reaction_rate:g}$",
            ha="center",
            va="bottom" if label_above else "top",
            fontsize=8,
        )
    ax.plot(*START_ONE, "o", color="#377eb8", ms=6, label="walker 1 start")
    ax.plot(*START_TWO, "s", color="#e41a1c", ms=5, label="walker 2 start")
    ax.annotate(
        "drift",
        xy=(0.47, 0.28),
        xytext=(0.25, 0.28),
        arrowprops={"arrowstyle": "->", "lw": 1.2},
        va="center",
        fontsize=8,
    )
    ax.set(
        xlim=(-0.03, 1.03),
        ylim=(-0.03, 1.03),
        aspect="equal",
        xlabel="$x$",
        ylabel="$y$",
        title="(a) three-patch geometry",
    )
    ax.legend(frameon=False, fontsize=7, loc="lower right")

    ax = axes[0, 1]
    grid_colors = ("#1b9e77", "#d95f02", "#7570b3", "#e7298a")
    for row, color in zip(rows, grid_colors, strict=True):
        prefix = f"g{row['nx']}x{row['ny']}"
        times = archive[f"{prefix}_times"]
        visible = times <= 80.0
        ax.plot(
            times[visible],
            archive[f"{prefix}_total_density"][visible],
            color=color,
            lw=1.35,
            label=f"{row['nx']}x{row['ny']}",
        )
    ax.set(
        xlabel="time",
        ylabel="reaction-time density",
        title="(b) contact-safe densities by grid",
    )
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    finest = rows[-1]
    prefix = f"g{finest['nx']}x{finest['ny']}"
    times = archive[f"{prefix}_times"]
    visible = times <= 80.0
    channels = archive[f"{prefix}_channel_density"]
    total = archive[f"{prefix}_total_density"]
    ax.plot(times[visible], total[visible], color="black", lw=1.8, label="total")
    for channel, patch, color in zip(
        range(3), PATCHES, patch_colors, strict=True
    ):
        ax.plot(
            times[visible],
            channels[visible, channel],
            color=color,
            lw=1.25,
            label=patch.label,
        )
    for root_number, root_time in enumerate(finest["detected_root_times"]):
        if root_number % 2 == 0:
            ax.axvline(root_time, color="0.55", lw=0.7, ls=":")
    ax.set(
        xlabel="time",
        ylabel="channel flux density",
        title=r"(c) channel attribution ($15\times11$)",
    )
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    spacings = np.asarray([row["spacing_x"] for row in rows])
    root_matrix = np.asarray([row["detected_root_times"] for row in rows])
    stationary_styles = (
        (0, "o", "peak 1"),
        (1, "v", "valley 1"),
        (2, "o", "peak 2"),
        (3, "v", "valley 2"),
        (4, "o", "peak 3"),
    )
    for position, marker, label in stationary_styles:
        ax.plot(
            spacings,
            root_matrix[:, position],
            marker=marker,
            lw=1.0,
            ms=5,
            label=label,
        )
    ax.invert_xaxis()
    ax.set(
        xlabel=r"spacing $h_x$ (finer right)",
        ylabel="detected stationary-root time",
        title="(d) five-root ordering",
    )
    ax.legend(frameon=False, fontsize=7, ncol=2)

    for plot_axis in axes.reshape(-1)[1:]:
        plot_axis.grid(alpha=0.18)
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
    return figure_pdf, figure_png


def main() -> None:
    rows: list[dict[str, Any]] = []
    roots: list[dict[str, Any]] = []
    archive: dict[str, np.ndarray] = {}
    for nx, ny in GRIDS:
        row, grid_roots, grid_archive = _analyse_grid(nx, ny)
        rows.append(row)
        roots.extend(grid_roots)
        archive.update(grid_archive)
        print(
            f"{nx}x{ny}: roots={np.round(row['detected_root_times'], 6).tolist()} "
            f"tail={row['tail_survival']:.3e} "
            f"valleys={np.round(row['valley_r_valley'], 4).tolist()}"
        )

    last_two_peak_differences = np.abs(
        np.asarray(rows[-1]["detected_root_times"])[[0, 2, 4]]
        - np.asarray(rows[-2]["detected_root_times"])[[0, 2, 4]]
    )
    summary = {
        "schema_version": 2,
        "deprecated_fields": {
            "grid_rows[].exact_root_times": "grid_rows[].detected_root_times",
            "grid_rows[].exact_root_types": "grid_rows[].detected_root_types",
            "grid_rows[].exact_peak_dominant_channels": (
                "grid_rows[].detected_peak_dominant_channels"
            ),
            "grid_rows[].exact_peak_dominant_shares": (
                "grid_rows[].detected_peak_dominant_shares"
            ),
        },
        "claim_status": (
            "verified_three_resolved_grids_four_five_detected_root_grids"
        ),
        "claim_boundary": (
            "Three finer finite CTMC grids are classifier-resolved trimodal; the "
            "contact-safe 9x5 grid is a shoulder while retaining five detected "
            "alternating stationary roots. This is not a continuum trimodality theorem, a "
            "converged continuum parameter claim, or an interval-certified "
            "exhaustive positive-time root count."
        ),
        "root_search_scope": {
            "interval": [0.0, ROOT_AUDIT_STOP],
            "method": (
                "finite sign-change scan followed by Brent refinement using "
                "finite-matrix semigroup derivative evaluations"
            ),
            "machine_field_semantics": (
                "detected_root_times/detected_root_types store sign-changing "
                "roots refined with finite-matrix semigroup derivative evaluations; "
                "the fields do not assert interval-exhaustive root counts"
            ),
            "exhaustive_positive_time_root_count_claimed": False,
            "tangential_or_unresolved_narrow_root_pairs_excluded": False,
        },
        "model": {
            "family_id": "M2D-T",
            "domain": "unit obstacle-free reflecting rectangle",
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
            "patches": [asdict(patch) for patch in PATCHES],
            "grids": [list(grid) for grid in GRIDS],
        },
        "classifier": asdict(MORPHOLOGY),
        "grid_rows": rows,
        "cross_grid": {
            "all_patch_disks_underresolved_longitudinally": all(
                row["resolution_diagnostics"][
                    "all_patch_radii_below_spacing_x"
                ]
                for row in rows
            ),
            "reactive_state_count_range": [
                min(min(row["reactive_state_counts"]) for row in rows),
                max(max(row["reactive_state_counts"]) for row in rows),
            ],
            "all_four_canonically_trimodal": all(
                row["classification"] == "multimodal" and row["mode_count"] == 3
                for row in rows
            ),
            "three_finer_canonically_trimodal": all(
                row["classification"] == "multimodal" and row["mode_count"] == 3
                for row in rows[1:]
            ),
            "coarsest_contact_safe_classification": rows[0]["classification"],
            "all_four_have_five_detected_alternating_roots": all(
                row["detected_root_types"]
                == ["maximum", "minimum", "maximum", "minimum", "maximum"]
                for row in rows
            ),
            "all_four_have_ordered_channel_dominance": all(
                row["detected_peak_dominant_channels"]
                == ["near", "middle", "far"]
                for row in rows
            ),
            "minimum_classifier_margin": float(
                min(
                    min(
                        row["min_peak_height_margin"],
                        row["min_prominence_margin"],
                        row["min_lobe_mass_margin"],
                        row["min_r_peak_margin"],
                        row["min_valley_margin"],
                        row["min_separation_width_margin"],
                    )
                    for row in rows
                    if row["min_peak_height_margin"] is not None
                )
            ),
            "minimum_raw_prominence_rel": float(
                min(row["minimum_raw_adjacent_prominence_rel"] for row in rows)
            ),
            "minimum_peak_channel_share": float(
                min(min(row["detected_peak_dominant_shares"]) for row in rows)
            ),
            "maximum_tail_at_2000": float(
                max(row["tail_survival"] for row in rows)
            ),
            "maximum_root_residual": float(
                max(row["maximum_root_abs_f_t"] for row in rows)
            ),
            "last_two_peak_time_differences": last_two_peak_differences.tolist(),
        },
    }

    metrics_json = DATA / "finite_radius_2d_trimodal_metrics.json"
    metrics_csv = DATA / "finite_radius_2d_trimodal_metrics.csv"
    roots_csv = DATA / "finite_radius_2d_trimodal_roots.csv"
    series_npz = DATA / "finite_radius_2d_trimodal_series.npz"
    _write_json(metrics_json, summary)
    _write_csv(metrics_csv, [_flat_grid_row(row) for row in rows])
    _write_csv(roots_csv, roots)
    series_tmp = series_npz.with_name(f".{series_npz.stem}.tmp.npz")
    np.savez_compressed(series_tmp, **archive)
    series_tmp.replace(series_npz)
    figure_pdf, figure_png = _make_figure(rows, archive)

    outputs = [
        metrics_json,
        metrics_csv,
        roots_csv,
        series_npz,
        figure_pdf,
        figure_png,
    ]
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=["uv", "run", "python", str(HERE.relative_to(REPO))],
        model_spec=summary["model"],
        classifier_spec=asdict(MORPHOLOGY),
        dependencies=[
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter2d.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "morphology.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
            NOTE,
        ],
        outputs=outputs,
        horizon={
            "shape_tmax": float(SHAPE_TIMES[-1]),
            "shape_dt": float(SHAPE_TIMES[1] - SHAPE_TIMES[0]),
            "root_scan_start": 0.0,
            "root_scan_stop": ROOT_AUDIT_STOP,
            "root_scan_fine_stop": ROOT_FINE_STOP,
            "root_scan_fine_dt": ROOT_FINE_DT,
            "root_scan_tail_dt": ROOT_TAIL_DT,
            "root_refinement": (
                "Brent refinement of detected generator-derivative sign changes "
                "within the declared root-scan horizon"
            ),
        },
    )
    manifest_path = DATA / "finite_radius_2d_trimodal.manifest.json"
    manifest_tmp = DATA / ".finite_radius_2d_trimodal.manifest.tmp.json"
    write_manifest(manifest_tmp, manifest)
    manifest_tmp.replace(manifest_path)


if __name__ == "__main__":
    main()
