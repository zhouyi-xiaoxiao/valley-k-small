#!/usr/bin/env python3
"""Validate an obstacle-free 2D finite-radius catalytic encounter family."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
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

GRIDS = ((9, 5), (11, 7), (13, 9), (15, 11))
REACTION_RADIUS = 0.13
START_ONE = (0.10, 0.50)
START_TWO = (0.35, 0.50)
PATCHES = (
    DoiCatalyticPatch((0.28, 0.50), 0.12, 0.20, "near"),
    DoiCatalyticPatch((0.90, 0.50), 0.20, 4.00, "far"),
)
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
SHAPE_TIMES = np.linspace(0.0, 80.0, 801)
TAIL_TIME = 240.0
FAMILY_ID = "M2D-C"
BRANCH_ID = "separated_boundary"

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


def _row_for_grid(nx: int, ny: int) -> tuple[dict, dict[str, np.ndarray]]:
    grid = RectangularGrid2D(nx, ny)
    generator_one = reflecting_advection_diffusion_generator_2d(
        grid,
        **WALKER_ONE,
    )
    generator_two = reflecting_advection_diffusion_generator_2d(
        grid,
        **WALKER_TWO,
    )
    model = build_doi_encounter_2d(
        grid,
        generator_one,
        generator_two,
        reaction_radius=REACTION_RADIUS,
        patches=PATCHES,
        centre_weight=0.5,
    )
    initial = contact_safe_initial_distribution_2d(model, START_ONE, START_TWO)
    initial_diagnostics = initial_distribution_diagnostics_2d(
        model,
        initial,
        walker1_position=START_ONE,
        walker2_position=START_TWO,
    )
    result = solve_doi_encounter_2d(model, initial, SHAPE_TIMES)
    time_step = float(SHAPE_TIMES[1] - SHAPE_TIMES[0])
    probability_mass = result.total_flux_density * time_step
    probability_mass[[0, -1]] *= 0.5
    morphology = analyze_fpt_morphology(
        probability_mass,
        times=SHAPE_TIMES,
        config=MORPHOLOGY,
        tail_mass_upper_bound=result.tail_mass + result.quadrature_closure_error,
    )
    if morphology.classification != "bimodal":
        raise RuntimeError(f"grid {(nx, ny)} is not canonically bimodal")
    valley = morphology.qualifying_valleys[0]

    tail_state = expm_multiply(model.killed_generator.T * TAIL_TIME, initial)
    tail_at_completion = float(np.sum(tail_state))
    audit_times = np.linspace(80.0, TAIL_TIME, 161)
    late_states = expm_multiply(
        model.killed_generator.T,
        initial,
        start=float(audit_times[0]),
        stop=float(audit_times[-1]),
        num=audit_times.size,
        endpoint=True,
    )
    late_density_channels = np.asarray(late_states @ model.channel_rate_matrix)
    late_density = late_density_channels.sum(axis=1)
    late_extrema_count = int(
        np.sum(
            (late_density[1:-1] > late_density[:-2])
            & (late_density[1:-1] >= late_density[2:])
        )
    )

    row = {
        "family_id": FAMILY_ID,
        "branch_id": BRANCH_ID,
        "nx": nx,
        "ny": ny,
        "single_walker_states": grid.state_count,
        "product_states": model.state_count,
        "initial_distribution": asdict(initial_diagnostics),
        "spacing_x": grid.spacing_x,
        "spacing_y": grid.spacing_y,
        "classification": morphology.classification,
        "peak_early": morphology.modal_peaks[0].time,
        "peak_late": morphology.modal_peaks[1].time,
        "peak_early_persistence": morphology.modal_peaks[0].persistence,
        "peak_late_persistence": morphology.modal_peaks[1].persistence,
        "R_peak": valley.r_peak,
        "R_valley": valley.r_valley,
        "separation_widths": valley.separation_widths,
        "shape_window_tail": result.tail_mass,
        "tail_at_240": tail_at_completion,
        "post_window_local_maxima": late_extrema_count,
        "quadrature_closure_error": result.quadrature_closure_error,
        "operator_mass_balance_error": model.operator_mass_balance_error,
        "near_reactive_states": int(model.reactive_state_counts[0]),
        "far_reactive_states": int(model.reactive_state_counts[1]),
        "scale_views": len(morphology.scale_views),
        "positive_scale_views": int(
            sum(
                len(view.accepted_peak_indices) >= 2
                for view in morphology.scale_views
                if not view.excluded_from_persistence
            )
        ),
        "evidence_grade": (
            "verified_positive"
            if tail_at_completion < 1e-7 and late_extrema_count == 0
            else "conditional"
        ),
    }
    archive = {
        "times": result.times,
        "total_density": result.total_flux_density,
        "channel_density": result.channel_flux_density,
        "survival": result.survival,
        "audit_times": audit_times,
        "audit_density": late_density,
    }
    return row, archive


def _write_csv(path: Path, rows: list[dict]) -> None:
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
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


def main() -> None:
    rows: list[dict] = []
    archives: dict[tuple[int, int], dict[str, np.ndarray]] = {}
    for nx, ny in GRIDS:
        row, archive = _row_for_grid(nx, ny)
        rows.append(row)
        archives[(nx, ny)] = archive

    metrics_json = DATA / "finite_radius_2d_metrics.json"
    metrics_csv = DATA / "finite_radius_2d_metrics.csv"
    series_npz = DATA / "finite_radius_2d_series.npz"
    _write_json(metrics_json, rows)
    _write_csv(metrics_csv, rows)
    series_tmp = series_npz.with_name(f".{series_npz.stem}.tmp.npz")
    np.savez_compressed(
        series_tmp,
        **{
            f"g{nx}x{ny}_{key}": value
            for (nx, ny), archive in archives.items()
            for key, value in archive.items()
        },
    )
    series_tmp.replace(series_npz)

    figure_pdf = FIGURES / "finite_radius_2d_validation.pdf"
    figure_png = FIGURES / "finite_radius_2d_validation.png"
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.8))

    ax = axes[0, 0]
    ax.set_aspect("equal")
    for patch, color in zip(PATCHES, ("#d95f02", "#7570b3"), strict=True):
        circle = plt.Circle(
            patch.centre,
            patch.radius,
            color=color,
            alpha=0.22,
            label=f"{patch.label} centre patch",
        )
        ax.add_patch(circle)
        ax.scatter(*patch.centre, marker="*", s=90, color=color)
    ax.scatter(*START_ONE, color="#1b9e77", s=55, label="faster trailing start")
    ax.scatter(*START_TWO, color="#66a61e", s=55, label="slower leading start")
    ax.annotate("soft transverse confinement", (0.48, 0.56), ha="center", fontsize=8)
    ax.set(
        xlim=(0.0, 1.0),
        ylim=(0.0, 1.0),
        xlabel="x",
        ylabel="y",
        title="(a) obstacle-free finite-radius encounter geometry",
    )
    ax.legend(frameon=False, fontsize=7, loc="lower right")

    ax = axes[0, 1]
    for nx, ny in GRIDS:
        archive = archives[(nx, ny)]
        visible = archive["times"] <= 45.0
        ax.plot(
            archive["times"][visible],
            archive["total_density"][visible],
            lw=1.4,
            label=(
                f"{nx}x{ny} (tail conditional)"
                if (nx, ny) == (9, 5)
                else f"{nx}x{ny}"
            ),
        )
    ax.set(
        xlabel="time",
        ylabel="reaction-time density",
        title="(b) bimodality across four declared finite grids",
    )
    ax.legend(frameon=False, fontsize=8)

    representative = archives[(13, 9)]
    ax = axes[1, 0]
    visible = representative["times"] <= 45.0
    ax.plot(
        representative["times"][visible],
        representative["total_density"][visible],
        color="black",
        lw=1.8,
        label="total",
    )
    ax.plot(
        representative["times"][visible],
        representative["channel_density"][visible, 0],
        color="#d95f02",
        label="near patch",
    )
    ax.plot(
        representative["times"][visible],
        representative["channel_density"][visible, 1],
        color="#7570b3",
        label="far patch",
    )
    ax.set(
        xlabel="time",
        ylabel="channel density",
        title="(c) resolved physical reaction channels, 13x9 grid",
    )
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    spacing = np.asarray([row["spacing_x"] for row in rows])
    early = np.asarray([row["peak_early"] for row in rows])
    late = np.asarray([row["peak_late"] for row in rows])
    ax.plot(spacing, early, "o-", color="#1b9e77", label="early peak")
    ax.plot(spacing, late, "s-", color="#7570b3", label="late peak")
    ax.invert_xaxis()
    ax.set(
        xlabel="grid spacing hx (finer to the right)",
        ylabel="peak time",
        title="(d) finite-grid peak-time diagnostic",
    )
    ax.legend(frameon=False, fontsize=8)

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

    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=["python", str(HERE.relative_to(REPO))],
        model_spec={
            "family_id": FAMILY_ID,
            "branch_id": BRANCH_ID,
            "evidence_relationship": (
                "four-grid audit of the M2D-C separated-boundary branch; the "
                "11x7 curve is reused in the mechanism-control artifact and is "
                "not independent evidence"
            ),
            "grids": [list(value) for value in GRIDS],
            "domain": [1.0, 1.0],
            "reaction_model": "finite-radius Doi volume sink",
            "catalytic_coordinate": "arithmetic midpoint C_eta with eta=0.5",
            "reaction_radius": REACTION_RADIUS,
            "patches": [asdict(patch) for patch in PATCHES],
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
            "boundary": "reflecting by omitted outward CTMC jumps",
        },
        classifier_spec=asdict(MORPHOLOGY),
        dependencies=[
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter2d.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "morphology.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
        ],
        outputs=[
            metrics_json,
            metrics_csv,
            series_npz,
            figure_pdf,
            figure_png,
        ],
        horizon={
            "shape_tmax": float(SHAPE_TIMES[-1]),
            "shape_dt": float(SHAPE_TIMES[1] - SHAPE_TIMES[0]),
            "tail_check_time": TAIL_TIME,
            "publication_tail_tolerance": 1e-7,
        },
    )
    manifest_path = DATA / "finite_radius_2d.manifest.json"
    manifest_tmp = DATA / ".finite_radius_2d.manifest.tmp.json"
    write_manifest(manifest_tmp, manifest)
    manifest_tmp.replace(manifest_path)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
