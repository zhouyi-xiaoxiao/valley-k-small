#!/usr/bin/env python3
"""Finite-grid sensitivity to the catalytic centre-coordinate convention.

The principal matched endpoint family is evaluated twice with every physical
parameter fixed.  The sole patterned-model change is

    C_eta = eta * X1 + (1-eta) * X2,

using the declared physical midpoint ``eta=1/2`` and the scalar-diffusion
noise-decoupling coordinate ``eta=D2/(D1+D2)``.  A homogeneous control is
matched separately inside each convention because changing eta changes the
coarse-grid patterned support and hence its raw discrete killing budget.

This is a sensitivity calculation, not an equivalence argument and not a
continuum comparison.  A supplemental 13x9 three-patch calculation is kept
separate from the principal matched family.
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
NOTE = REPORT / "notes" / "finite_radius_2d_centre_coordinate_sensitivity.md"
DATA.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

GRIDS = ((9, 5), (11, 7), (13, 9))
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
PATTERNED_PATCHES = (
    DoiCatalyticPatch((0.25, 0.50), 0.18, 0.50, "near"),
    DoiCatalyticPatch((0.72, 0.50), 0.20, 15.00, "far"),
)
MIDPOINT_ETA = 0.5
WEIGHTED_ETA = WALKER_TWO["diffusion"] / (
    WALKER_ONE["diffusion"] + WALKER_TWO["diffusion"]
)
COORDINATES = (
    ("physical_midpoint", MIDPOINT_ETA),
    ("diffusivity_weighted", WEIGHTED_ETA),
)
SHAPE_TIMES = np.linspace(0.0, 80.0, 801)
TAIL_TIME = 960.0

TRIMODAL_GRID = (13, 9)
TRIMODAL_REACTION_RADIUS = 0.13
TRIMODAL_START_ONE = (0.05, 0.50)
TRIMODAL_START_TWO = (0.20, 0.50)
TRIMODAL_WALKER_ONE = {
    "diffusion": 0.0025,
    "drift_x": 0.10,
    "transverse_confinement": 1.5,
}
TRIMODAL_WALKER_TWO = WALKER_TWO
TRIMODAL_PATCHES = (
    DoiCatalyticPatch((0.20, 0.50), 0.06, 0.03, "near"),
    DoiCatalyticPatch((0.70, 0.50), 0.05, 1.00, "middle"),
    DoiCatalyticPatch((0.94, 0.50), 0.05, 0.05, "far"),
)
TRIMODAL_TIMES = np.linspace(0.0, 400.0, 2001)
TRIMODAL_TAIL_TIME = 2000.0

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


def _stable_float(value: float, *, significant_digits: int = 12) -> float:
    """Round diagnostics below scientific resolution for byte-stable artifacts.

    Sparse exponential norm estimation can perturb an extremely small tail in
    its last floating-point bits.  Twelve significant digits are far beyond
    the tail thresholds used here while making repeated serializations stable.
    Shape arrays and densities are retained at full binary precision.
    """

    return float(f"{float(value):.{int(significant_digits)}g}")


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


def _analyse_morphology(result: Any) -> tuple[Any, dict[str, Any]]:
    dt = float(result.times[1] - result.times[0])
    probability_mass = np.asarray(result.total_flux_density, dtype=float) * dt
    probability_mass[[0, -1]] *= 0.5
    morphology = analyze_fpt_morphology(
        probability_mass,
        times=result.times,
        config=MORPHOLOGY,
        tail_mass_upper_bound=result.tail_mass + result.quadrature_closure_error,
    )
    peak_times = [float(peak.time) for peak in morphology.modal_peaks]
    peak_densities = [
        float(np.interp(time, result.times, result.total_flux_density))
        for time in peak_times
    ]
    return morphology, {
        "classification": morphology.classification,
        "mode_count": int(morphology.mode_count),
        "modal_peak_times": peak_times,
        "modal_peak_densities": peak_densities,
        "qualifying_valleys": [
            {
                "left_peak_time": float(valley.left_peak_time),
                "right_peak_time": float(valley.right_peak_time),
                "valley_time": float(valley.valley_time),
                "r_peak": float(valley.r_peak),
                "r_valley": float(valley.r_valley),
                "separation_widths": float(valley.separation_widths),
            }
            for valley in morphology.qualifying_valleys
        ],
        "views_with_at_least_two_peaks": int(
            sum(
                len(view.accepted_peak_indices) >= 2
                for view in morphology.scale_views
                if not view.excluded_from_persistence
            )
        ),
        "views_with_at_least_three_peaks": int(
            sum(
                len(view.accepted_peak_indices) >= 3
                for view in morphology.scale_views
                if not view.excluded_from_persistence
            )
        ),
        "scale_views": len(morphology.scale_views),
        "shape_window_tail": float(result.tail_mass),
        "quadrature_closure_error": float(result.quadrature_closure_error),
        "classifier_tail_certified": bool(morphology.tail_certificate.certified),
        "warnings": list(morphology.warnings),
    }


def _strict_stationary_audit(
    model: Any, initial: np.ndarray, times: np.ndarray
) -> dict[str, Any]:
    """Brent-refine detected sign changes on the declared finite time window."""

    audit_times = np.asarray(times, dtype=float)
    states = np.asarray(
        expm_multiply(
            model.killed_generator.T,
            initial,
            start=float(audit_times[0]),
            stop=float(audit_times[-1]),
            num=audit_times.size,
            endpoint=True,
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

    def values(time: float) -> tuple[float, float, float]:
        state = np.asarray(
            expm_multiply(model.killed_generator.T * float(time), initial),
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
                float(audit_times[index]),
                float(audit_times[index + 1]),
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
    maxima = [root for root in roots if root["type"] == "maximum"]
    peak_ratio = (
        min(float(root["density"]) for root in maxima)
        / max(float(root["density"]) for root in maxima)
        if len(maxima) >= 2
        else 0.0
    )
    return {
        "strict_stationary_points": roots,
        "strict_mode_count": len(maxima),
        "strict_secondary_peak_ratio": peak_ratio,
        "classification_semantics": (
            "canonical morphology is a resolved class, not strict root count"
        ),
    }


def _tail_audit(
    model: Any,
    initial: np.ndarray,
    *,
    start: float,
    stop: float,
    samples: int,
) -> dict[str, Any]:
    states = np.asarray(
        expm_multiply(
            model.killed_generator.T,
            initial,
            start=float(start),
            stop=float(stop),
            num=int(samples),
            endpoint=True,
        ),
        dtype=float,
    )
    density = np.asarray(states @ model.channel_rate_matrix).sum(axis=1)
    sampled_maxima = int(
        np.sum(
            (density[1:-1] > density[:-2])
            & (density[1:-1] >= density[2:])
        )
    )
    return {
        "tail_check_time": float(stop),
        "tail_survival": _stable_float(states[-1].sum()),
        "post_window_sample_count": int(samples),
        "post_window_sampled_local_maxima": sampled_maxima,
    }


def _support(model: Any, channel: int | None = None) -> set[int]:
    if channel is None:
        values = np.asarray(model.channel_rate_matrix.sum(axis=1)).reshape(-1)
        return set(np.flatnonzero(values > 0.0).tolist())
    return set(model.channel_rate_matrix[:, int(channel)].nonzero()[0].tolist())


def _set_comparison(
    midpoint: set[int],
    weighted: set[int],
    *,
    label: str,
) -> dict[str, Any]:
    union = midpoint | weighted
    intersection = midpoint & weighted
    symmetric_difference = midpoint ^ weighted
    return {
        "channel": label,
        "midpoint_count": len(midpoint),
        "diffusivity_weighted_count": len(weighted),
        "intersection_count": len(intersection),
        "union_count": len(union),
        "midpoint_only_count": len(midpoint - weighted),
        "diffusivity_weighted_only_count": len(weighted - midpoint),
        "symmetric_difference_count": len(symmetric_difference),
        "jaccard_distance": float(len(symmetric_difference) / len(union)),
    }


def _mask_comparisons(midpoint_model: Any, weighted_model: Any) -> list[dict[str, Any]]:
    if [patch.label for patch in midpoint_model.patches] != [
        patch.label for patch in weighted_model.patches
    ]:
        raise RuntimeError("coordinate comparison requires identical patch labels")
    rows = [
        _set_comparison(
            _support(midpoint_model, channel),
            _support(weighted_model, channel),
            label=patch.label,
        )
        for channel, patch in enumerate(midpoint_model.patches)
    ]
    rows.append(
        _set_comparison(
            _support(midpoint_model),
            _support(weighted_model),
            label="patterned_union",
        )
    )
    return rows


def _endpoint_csv_row(
    *,
    nx: int,
    ny: int,
    coordinate: str,
    eta: float,
    patterned_model: Any,
    patterned: dict[str, Any],
    homogeneous: dict[str, Any],
    matched_rate: float,
    patterned_budget: float,
    homogeneous_budget: float,
) -> dict[str, Any]:
    return {
        "family": "principal_matched_endpoint",
        "nx": nx,
        "ny": ny,
        "coordinate": coordinate,
        "eta": eta,
        "near_mask_count": int(patterned_model.reactive_state_counts[0]),
        "far_mask_count": int(patterned_model.reactive_state_counts[1]),
        "patterned_classification": patterned["classification"],
        "patterned_mode_count": patterned["mode_count"],
        "patterned_peak_times": ";".join(
            f"{value:.12g}" for value in patterned["modal_peak_times"]
        ),
        "patterned_views_with_at_least_two_peaks": patterned[
            "views_with_at_least_two_peaks"
        ],
        "patterned_tail_at_960": patterned["tail_survival"],
        "patterned_post_window_sampled_local_maxima": patterned[
            "post_window_sampled_local_maxima"
        ],
        "homogeneous_classification": homogeneous["classification"],
        "homogeneous_mode_count": homogeneous["mode_count"],
        "homogeneous_peak_times": ";".join(
            f"{value:.12g}" for value in homogeneous["modal_peak_times"]
        ),
        "homogeneous_tail_at_960": homogeneous["tail_survival"],
        "homogeneous_post_window_sampled_local_maxima": homogeneous[
            "post_window_sampled_local_maxima"
        ],
        "matched_homogeneous_rate": matched_rate,
        "patterned_state_sum_killing": patterned_budget,
        "homogeneous_state_sum_killing": homogeneous_budget,
        "matched_budget_relative_error": abs(homogeneous_budget - patterned_budget)
        / patterned_budget,
    }


def _principal_family() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, np.ndarray]]:
    grid_rows: list[dict[str, Any]] = []
    endpoint_rows: list[dict[str, Any]] = []
    archive: dict[str, np.ndarray] = {}
    for nx, ny in GRIDS:
        grid = RectangularGrid2D(nx, ny)
        generator_one = reflecting_advection_diffusion_generator_2d(
            grid, **WALKER_ONE
        )
        generator_two = reflecting_advection_diffusion_generator_2d(
            grid, **WALKER_TWO
        )
        coordinate_models: dict[str, Any] = {}
        coordinate_results: dict[str, Any] = {}
        for coordinate, eta in COORDINATES:
            patterned_model = build_doi_encounter_2d(
                grid,
                generator_one,
                generator_two,
                reaction_radius=REACTION_RADIUS,
                patches=PATTERNED_PATCHES,
                centre_weight=eta,
            )
            homogeneous_unit = build_doi_encounter_2d(
                grid,
                generator_one,
                generator_two,
                reaction_radius=REACTION_RADIUS,
                patches=(DoiCatalyticPatch((0.50, 0.50), 2.0, 1.0, "tube"),),
                centre_weight=eta,
            )
            patterned_budget = float(patterned_model.channel_rate_matrix.sum())
            unit_budget = float(homogeneous_unit.channel_rate_matrix.sum())
            matched_rate = patterned_budget / unit_budget
            homogeneous_model = build_doi_encounter_2d(
                grid,
                generator_one,
                generator_two,
                reaction_radius=REACTION_RADIUS,
                patches=(
                    DoiCatalyticPatch(
                        (0.50, 0.50),
                        2.0,
                        matched_rate,
                        "uniform_matched",
                    ),
                ),
                centre_weight=eta,
            )
            homogeneous_budget = float(homogeneous_model.channel_rate_matrix.sum())
            budget_error = abs(homogeneous_budget - patterned_budget) / patterned_budget
            if budget_error > 8e-16:
                raise RuntimeError(f"matched budget failed on {(nx, ny, coordinate)}")

            initial = contact_safe_initial_distribution_2d(
                patterned_model, START_ONE, START_TWO
            )
            initial_diagnostics = initial_distribution_diagnostics_2d(
                patterned_model,
                initial,
                walker1_position=START_ONE,
                walker2_position=START_TWO,
            )
            endpoint_payload: dict[str, Any] = {}
            for endpoint, model in (
                ("patterned", patterned_model),
                ("homogeneous", homogeneous_model),
            ):
                result = solve_doi_encounter_2d(model, initial, SHAPE_TIMES)
                _morphology, summary = _analyse_morphology(result)
                summary.update(
                    _strict_stationary_audit(model, initial, SHAPE_TIMES)
                )
                summary.update(
                    _tail_audit(
                        model,
                        initial,
                        start=float(SHAPE_TIMES[-1]),
                        stop=TAIL_TIME,
                        samples=221,
                    )
                )
                endpoint_payload[endpoint] = summary
                key = f"principal_g{nx}x{ny}_{coordinate}_{endpoint}"
                archive[f"{key}_times"] = result.times
                archive[f"{key}_density"] = result.total_flux_density
                archive[f"{key}_channels"] = result.channel_flux_density

            coordinate_models[coordinate] = patterned_model
            coordinate_results[coordinate] = {
                "eta": float(eta),
                "initial_distribution": asdict(initial_diagnostics),
                "patterned_reactive_state_counts": [
                    int(value) for value in patterned_model.reactive_state_counts
                ],
                "tube_state_count": int(homogeneous_unit.reactive_state_counts[0]),
                "patterned_state_sum_killing": patterned_budget,
                "matched_homogeneous_rate": matched_rate,
                "homogeneous_state_sum_killing": homogeneous_budget,
                "matched_budget_relative_error": budget_error,
                "endpoints": endpoint_payload,
            }
            endpoint_rows.append(
                _endpoint_csv_row(
                    nx=nx,
                    ny=ny,
                    coordinate=coordinate,
                    eta=eta,
                    patterned_model=patterned_model,
                    patterned=endpoint_payload["patterned"],
                    homogeneous=endpoint_payload["homogeneous"],
                    matched_rate=matched_rate,
                    patterned_budget=patterned_budget,
                    homogeneous_budget=homogeneous_budget,
                )
            )

        masks = _mask_comparisons(
            coordinate_models["physical_midpoint"],
            coordinate_models["diffusivity_weighted"],
        )
        midpoint_class = coordinate_results["physical_midpoint"]["endpoints"][
            "patterned"
        ]["classification"]
        weighted_class = coordinate_results["diffusivity_weighted"]["endpoints"][
            "patterned"
        ]["classification"]
        grid_rows.append(
            {
                "grid": [nx, ny],
                "spacing_x": float(grid.spacing_x),
                "spacing_y": float(grid.spacing_y),
                "product_state_count": int(grid.state_count**2),
                "coordinate_results": coordinate_results,
                "mask_comparison": masks,
                "patterned_classification_changed": midpoint_class != weighted_class,
                "patterned_classification_transition": (
                    f"{midpoint_class}->{weighted_class}"
                ),
            }
        )
    return grid_rows, endpoint_rows, archive


def _supplemental_trimodal() -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    nx, ny = TRIMODAL_GRID
    grid = RectangularGrid2D(nx, ny)
    generator_one = reflecting_advection_diffusion_generator_2d(
        grid, **TRIMODAL_WALKER_ONE
    )
    generator_two = reflecting_advection_diffusion_generator_2d(
        grid, **TRIMODAL_WALKER_TWO
    )
    models: dict[str, Any] = {}
    results: dict[str, Any] = {}
    archive: dict[str, np.ndarray] = {}
    for coordinate, eta in COORDINATES:
        model = build_doi_encounter_2d(
            grid,
            generator_one,
            generator_two,
            reaction_radius=TRIMODAL_REACTION_RADIUS,
            patches=TRIMODAL_PATCHES,
            centre_weight=eta,
        )
        initial = contact_safe_initial_distribution_2d(
            model, TRIMODAL_START_ONE, TRIMODAL_START_TWO
        )
        initial_diagnostics = initial_distribution_diagnostics_2d(
            model,
            initial,
            walker1_position=TRIMODAL_START_ONE,
            walker2_position=TRIMODAL_START_TWO,
        )
        result = solve_doi_encounter_2d(model, initial, TRIMODAL_TIMES)
        _morphology, summary = _analyse_morphology(result)
        summary.update(
            _tail_audit(
                model,
                initial,
                start=float(TRIMODAL_TIMES[-1]),
                stop=TRIMODAL_TAIL_TIME,
                samples=161,
            )
        )
        summary["eta"] = float(eta)
        summary["reactive_state_counts"] = [
            int(value) for value in model.reactive_state_counts
        ]
        summary["initial_distribution"] = asdict(initial_diagnostics)
        models[coordinate] = model
        results[coordinate] = summary
        key = f"trimodal_g{nx}x{ny}_{coordinate}"
        archive[f"{key}_times"] = result.times
        archive[f"{key}_density"] = result.total_flux_density
        archive[f"{key}_channels"] = result.channel_flux_density

    return (
        {
            "family_id": "M2D-T",
            "role": (
                "separate-family sensitivity diagnostic; not part of the principal "
                "matched endpoint claim"
            ),
            "grid": [nx, ny],
            "coordinate_results": results,
            "mask_comparison": _mask_comparisons(
                models["physical_midpoint"], models["diffusivity_weighted"]
            ),
        },
        archive,
    )


def _coordinate_panel_title(nx: int, ny: int, row: dict[str, Any]) -> str:
    """Build a data-derived morphology title; never hard-code a class label."""

    midpoint_class = row["coordinate_results"]["physical_midpoint"]["endpoints"][
        "patterned"
    ]["classification"]
    weighted_class = row["coordinate_results"]["diffusivity_weighted"][
        "endpoints"
    ]["patterned"]["classification"]
    panel = chr(97 + list(GRIDS).index((nx, ny)))
    return (
        f"({panel}) {nx}x{ny}\n"
        f"midpoint: {midpoint_class}; weighted: {weighted_class}"
    )


def _draw_figure(
    grid_rows: list[dict[str, Any]],
    archive: dict[str, np.ndarray],
    figure_pdf: Path,
    figure_png: Path,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.4))
    colors = {
        "physical_midpoint": "#20252B",
        "diffusivity_weighted": "#D7812A",
    }
    for ax, (nx, ny) in zip(axes.reshape(-1)[:3], GRIDS, strict=True):
        row = next(value for value in grid_rows if value["grid"] == [nx, ny])
        for coordinate, _eta in COORDINATES:
            for endpoint, linestyle, alpha in (
                ("patterned", "-", 1.0),
                ("homogeneous", "--", 0.72),
            ):
                key = f"principal_g{nx}x{ny}_{coordinate}_{endpoint}"
                times = archive[f"{key}_times"]
                density = archive[f"{key}_density"]
                visible = times <= 45.0
                label = f"{coordinate}; {endpoint}"
                ax.plot(
                    times[visible],
                    density[visible],
                    color=colors[coordinate],
                    ls=linestyle,
                    lw=1.65 if endpoint == "patterned" else 1.05,
                    alpha=alpha,
                    label=label,
                )
        ax.set(
            xlabel="time",
            ylabel="reaction-time density",
            title=_coordinate_panel_title(nx, ny, row),
        )
        ax.grid(alpha=0.18)

    ax = axes[1, 1]
    x = np.arange(len(GRIDS), dtype=float)
    width = 0.24
    for offset, channel, color in (
        (-width, "near", "#2F6B9A"),
        (0.0, "far", "#D7812A"),
        (width, "patterned_union", "#6B7280"),
    ):
        values = [
            next(
                item["jaccard_distance"]
                for item in row["mask_comparison"]
                if item["channel"] == channel
            )
            for row in grid_rows
        ]
        ax.bar(x + offset, values, width=width, label=channel, color=color)
    ax.set_xticks(x, [f"{nx}x{ny}" for nx, ny in GRIDS])
    ax.set(
        xlabel="grid",
        ylabel="symmetric difference / union",
        title="(d) mask sensitivity",
        ylim=(0.0, 0.26),
    )
    ax.legend(frameon=False, fontsize=7, ncol=3, loc="upper center")
    ax.grid(axis="y", alpha=0.18)
    handles, _labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        ["mid pat.", "mid hom.", "weighted pat.", "weighted hom."],
        frameon=False,
        ncol=4,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.0),
    )
    enforce_publication_graphics(fig)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.93))
    temporary_pdf = figure_pdf.with_name(
        f".{figure_pdf.stem}.tmp{figure_pdf.suffix}"
    )
    temporary_png = figure_png.with_name(
        f".{figure_png.stem}.tmp{figure_png.suffix}"
    )
    fig.savefig(
        temporary_pdf,
        metadata={"CreationDate": None, "ModDate": None, "Title": "2D centre-coordinate sensitivity"},
    )
    fig.savefig(temporary_png, dpi=300, metadata={"Software": "valley-k-small"})
    temporary_pdf.replace(figure_pdf)
    temporary_png.replace(figure_png)
    plt.close(fig)


def main() -> None:
    grid_rows, endpoint_rows, archive = _principal_family()
    trimodal, trimodal_archive = _supplemental_trimodal()
    archive.update(trimodal_archive)

    classification_change_grids = [
        row["grid"] for row in grid_rows if row["patterned_classification_changed"]
    ]
    if any(
        item["jaccard_distance"] <= 0.0
        for row in grid_rows
        for item in row["mask_comparison"]
        if item["channel"] != "patterned_union"
    ):
        raise RuntimeError("a principal patch mask did not respond to centre coordinate")

    mask_rows: list[dict[str, Any]] = []
    for row in grid_rows:
        for item in row["mask_comparison"]:
            mask_rows.append(
                {
                    "family": "principal_matched_endpoint",
                    "nx": row["grid"][0],
                    "ny": row["grid"][1],
                    **item,
                }
            )
    for item in trimodal["mask_comparison"]:
        mask_rows.append(
            {
                "family": "supplemental_trimodal",
                "nx": trimodal["grid"][0],
                "ny": trimodal["grid"][1],
                **item,
            }
        )

    payload = {
        "claim_scope": (
            "finite-grid one-factor centre-coordinate sensitivity; no equivalence "
            "or continuum-modality claim"
        ),
        "coordinate_definition": "C_eta = eta*X1 + (1-eta)*X2",
        "coordinate_conventions": {
            "physical_midpoint": {
                "eta": MIDPOINT_ETA,
                "definition": "(X1+X2)/2",
                "role": "declared physical catalyst coordinate",
            },
            "diffusivity_weighted": {
                "eta": WEIGHTED_ETA,
                "definition": "(D2*X1+D1*X2)/(D1+D2)",
                "role": "noise-decoupling sensitivity comparator",
            },
        },
        "principal_family": {
            "family_id": "M2D-E",
            "evidence_relationship": (
                "one-factor coordinate sensitivity within M2D-E; the three grids "
                "are correlated evaluations of one family"
            ),
            "model": {
                "grids": [list(value) for value in GRIDS],
                "reaction_radius": REACTION_RADIUS,
                "walker_one": WALKER_ONE,
                "walker_two": WALKER_TWO,
                "start_one": START_ONE,
                "start_two": START_TWO,
                "initial_distribution": (
                    "hierarchical contact-safe selector: minimum physical Euclidean "
                    "spread on the smallest feasible local stencil, followed by a "
                    "strictly convex closest-to-product QP on the optimal LP face; "
                    "exact product-bilinear return when already contact-safe"
                ),
                "patches": [asdict(patch) for patch in PATTERNED_PATCHES],
                "matching_rule": (
                    "homogeneous state-sum killing is re-matched separately within "
                    "each coordinate convention"
                ),
            },
            "grid_rows": grid_rows,
        },
        "supplemental_trimodal": trimodal,
        "summary": {
            "classification_change_grids": classification_change_grids,
            "coordinate_convention_changes_coarse_grid_modality": bool(
                classification_change_grids
            ),
            "principal_transition_by_grid": {
                f"{row['grid'][0]}x{row['grid'][1]}": row[
                    "patterned_classification_transition"
                ]
                for row in grid_rows
            },
            "minimum_principal_patch_jaccard_distance": min(
                item["jaccard_distance"]
                for row in grid_rows
                for item in row["mask_comparison"]
                if item["channel"] != "patterned_union"
            ),
            "maximum_principal_patch_jaccard_distance": max(
                item["jaccard_distance"]
                for row in grid_rows
                for item in row["mask_comparison"]
                if item["channel"] != "patterned_union"
            ),
            "interpretation": (
                "the two coordinates define different finite-grid catalyst masks; "
                "classification agreement under the contact-safe initial law is "
                "not model equivalence"
            ),
        },
    }

    metrics_json = DATA / "finite_radius_2d_centre_coordinate.json"
    endpoints_csv = DATA / "finite_radius_2d_centre_coordinate_endpoints.csv"
    masks_csv = DATA / "finite_radius_2d_centre_coordinate_masks.csv"
    series_npz = DATA / "finite_radius_2d_centre_coordinate_series.npz"
    figure_pdf = FIGURES / "finite_radius_2d_centre_coordinate_sensitivity.pdf"
    figure_png = FIGURES / "finite_radius_2d_centre_coordinate_sensitivity.png"

    _write_json(metrics_json, payload)
    _write_csv(endpoints_csv, endpoint_rows)
    _write_csv(masks_csv, mask_rows)
    series_tmp = series_npz.with_name(f".{series_npz.stem}.tmp.npz")
    np.savez_compressed(series_tmp, **archive)
    series_tmp.replace(series_npz)
    _draw_figure(grid_rows, archive, figure_pdf, figure_png)

    outputs = [
        metrics_json,
        endpoints_csv,
        masks_csv,
        series_npz,
        figure_pdf,
        figure_png,
    ]
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=["python", str(HERE.relative_to(REPO))],
        model_spec={
            "principal_family_id": "M2D-E",
            "supplemental_family_id": "M2D-T",
            "comparison": (
                "one-factor eta sensitivity; midpoint and diffusivity-weighted "
                "coordinates are not treated as equivalent"
            ),
            "coordinate_definition": "C_eta = eta*X1 + (1-eta)*X2",
            "coordinates": {
                label: eta for label, eta in COORDINATES
            },
            "principal_grids": [list(value) for value in GRIDS],
            "principal_reaction_radius": REACTION_RADIUS,
            "principal_patches": [asdict(patch) for patch in PATTERNED_PATCHES],
            "principal_walker_one": WALKER_ONE,
            "principal_walker_two": WALKER_TWO,
            "principal_starts": [START_ONE, START_TWO],
            "initial_distribution": (
                "hierarchical contact-safe selector: minimum physical Euclidean "
                "spread on the smallest feasible local stencil, followed by a "
                "strictly convex closest-to-product QP on the optimal LP face; "
                "exact product-bilinear return when already contact-safe"
            ),
            "homogeneous_matching": (
                "separate exact state-sum killing match within each eta and grid"
            ),
            "tail_serialization": (
                "12 significant digits; shape series retain full binary precision"
            ),
            "supplemental_trimodal_grid": list(TRIMODAL_GRID),
            "supplemental_trimodal_patches": [
                asdict(patch) for patch in TRIMODAL_PATCHES
            ],
        },
        classifier_spec=asdict(MORPHOLOGY),
        dependencies=[
            NOTE,
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter2d.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "morphology.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
        ],
        outputs=outputs,
        horizon={
            "principal_shape_tmax": float(SHAPE_TIMES[-1]),
            "principal_shape_dt": float(SHAPE_TIMES[1] - SHAPE_TIMES[0]),
            "principal_tail_check": TAIL_TIME,
            "supplemental_shape_tmax": float(TRIMODAL_TIMES[-1]),
            "supplemental_shape_dt": float(
                TRIMODAL_TIMES[1] - TRIMODAL_TIMES[0]
            ),
            "supplemental_tail_check": TRIMODAL_TAIL_TIME,
        },
    )
    manifest_path = DATA / "finite_radius_2d_centre_coordinate.manifest.json"
    manifest_tmp = DATA / ".finite_radius_2d_centre_coordinate.manifest.tmp.json"
    write_manifest(manifest_tmp, manifest)
    manifest_tmp.replace(manifest_path)


if __name__ == "__main__":
    main()
