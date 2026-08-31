#!/usr/bin/env python3
"""Validate the finite-radius and logarithmic-capacity limits in two dimensions.

For two translation-invariant walkers on a flat two-torus, the relative
coordinate is itself a diffusion with ``Drel=D1+D2``.  This exact quotient
reduces the pair state space to a two-dimensional periodic Doi problem,

    (-Drel Laplacian + kappa * indicator(|r|<a)) u = 1.

The script checks both sides of the two-dimensional point-sink warning:

* at fixed ``kappa``, shrinking the disk is reaction limited and
  ``mean(T) ~ area/(kappa*pi*a**2)``;
* at fixed dimensionless Doi strength ``chi=kappa*a**2/Drel``, the sink is
  renormalized and the universal outer resistance is logarithmic,
  ``mean(T) = area/(2*pi*Drel)*log(1/a) + O(1)``.

The disk indicator is cell-averaged by deterministic subcell quadrature so
that the convergence study is not dominated by a staircase mask.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from vkcore.encounter2d import PeriodicGrid2D, solve_periodic_doi_mean_time
from vkcore.plotting import enforce_publication_graphics
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

DOMAIN_LENGTH = 1.0
RELATIVE_DIFFUSIVITY = 1.0
SUBCELL_SAMPLES = 8
FIXED_KAPPA = 1.0
FIXED_KAPPA_GRID = 241
FIXED_KAPPA_RADII = (0.12, 0.08, 0.05, 0.03, 0.02)
RENORMALIZED_CHI = 1.0
CAPACITY_GRIDS = (161, 241, 321, 401)
CAPACITY_RADII = (0.05, 0.04, 0.03, 0.025, 0.02)
THEORY_LOG_SLOPE = DOMAIN_LENGTH**2 / (2.0 * np.pi * RELATIVE_DIFFUSIVITY)
REACTION_LIMIT_PANEL_TITLE = "(b) reaction-limited target-area law"


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _fixed_kappa_rows() -> list[dict[str, Any]]:
    grid = PeriodicGrid2D(FIXED_KAPPA_GRID, FIXED_KAPPA_GRID)
    rows: list[dict[str, Any]] = []
    for radius in FIXED_KAPPA_RADII:
        result = solve_periodic_doi_mean_time(
            grid,
            diffusion=RELATIVE_DIFFUSIVITY,
            reaction_radius=radius,
            reaction_rate=FIXED_KAPPA,
            subcell_samples=SUBCELL_SAMPLES,
        )
        disk_area = np.pi * radius**2
        rows.append(
            {
                "grid_n": FIXED_KAPPA_GRID,
                "radius": radius,
                "reaction_rate": FIXED_KAPPA,
                "mean_time": result.mean_from_uniform_outside,
                "reaction_limited_scaled_mean": FIXED_KAPPA
                * disk_area
                * result.mean_from_uniform_outside,
                "target_area_fraction": result.target_area_fraction,
                "target_area_ratio": result.target_area_fraction / disk_area,
                "linear_solve_residual": result.linear_solve_residual,
                "linear_solve_relative_residual": (
                    result.linear_solve_relative_residual
                ),
            }
        )
    return rows


def _capacity_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    fits: list[dict[str, Any]] = []
    log_inverse_radius = np.log(1.0 / np.asarray(CAPACITY_RADII, dtype=float))
    for grid_n in CAPACITY_GRIDS:
        grid = PeriodicGrid2D(grid_n, grid_n)
        means: list[float] = []
        for radius in CAPACITY_RADII:
            reaction_rate = (
                RENORMALIZED_CHI * RELATIVE_DIFFUSIVITY / radius**2
            )
            result = solve_periodic_doi_mean_time(
                grid,
                diffusion=RELATIVE_DIFFUSIVITY,
                reaction_radius=radius,
                reaction_rate=reaction_rate,
                subcell_samples=SUBCELL_SAMPLES,
            )
            means.append(result.mean_from_uniform_outside)
            disk_area = np.pi * radius**2
            rows.append(
                {
                    "grid_n": grid_n,
                    "spacing": grid.spacing_x,
                    "radius": radius,
                    "radius_in_cells": radius / grid.spacing_x,
                    "dimensionless_doi_strength": RENORMALIZED_CHI,
                    "reaction_rate": reaction_rate,
                    "mean_time": result.mean_from_uniform_outside,
                    "target_area_ratio": result.target_area_fraction / disk_area,
                    "linear_solve_residual": result.linear_solve_residual,
                    "linear_solve_relative_residual": (
                        result.linear_solve_relative_residual
                    ),
                }
            )
        slope, intercept = np.polyfit(
            log_inverse_radius,
            np.asarray(means, dtype=float),
            1,
        )
        fitted = slope * log_inverse_radius + intercept
        residual = np.asarray(means) - fitted
        total = np.asarray(means) - float(np.mean(means))
        fits.append(
            {
                "grid_n": grid_n,
                "spacing": grid.spacing_x,
                "fitted_log_slope": float(slope),
                "fitted_intercept": float(intercept),
                "theory_log_slope": THEORY_LOG_SLOPE,
                "slope_ratio_to_theory": float(slope / THEORY_LOG_SLOPE),
                "relative_slope_error": float(abs(slope / THEORY_LOG_SLOPE - 1.0)),
                "r_squared": float(
                    1.0 - np.sum(residual**2) / np.sum(total**2)
                ),
                "max_absolute_fit_residual": float(np.max(np.abs(residual))),
            }
        )
    return rows, fits


def main() -> None:
    fixed_rows = _fixed_kappa_rows()
    capacity_rows, capacity_fits = _capacity_rows()
    finest_fit = capacity_fits[-1]
    payload = {
        "theory": {
            "relative_coordinate_reduction": "D_relative = D1 + D2",
            "fixed_kappa_asymptotic": "mean ~ area/(kappa*pi*a^2)",
            "fixed_chi_asymptotic": (
                "mean = area/(2*pi*D_relative)*log(1/a) + O(1)"
            ),
            "theory_log_slope": THEORY_LOG_SLOPE,
        },
        "fixed_kappa": fixed_rows,
        "renormalized_capacity": capacity_rows,
        "capacity_fits": capacity_fits,
        "numerical_method": {
            "fixed_radius_and_grid_limits_separated": False,
            "reason": (
                "the calculation refines the lattice over one fixed five-radius "
                "window but does not perform independent h->0 fits at successively "
                "shrinking radius windows"
            ),
        },
        "summary_checks": {
            "finest_finite_grid_slope_ratio_to_theory": finest_fit[
                "slope_ratio_to_theory"
            ],
            "finest_finite_grid_r_squared": finest_fit["r_squared"],
            "finite_grid_slope_consistency_pass": bool(
                finest_fit["slope_ratio_to_theory"] > 0.98
                and finest_fit["r_squared"] > 0.9999
            ),
            "continuum_capacity_coefficient_certified": False,
        },
        "claim_boundary": (
            "The finite-grid fixed-chi data are consistent with the predicted "
            "two-dimensional logarithmic slope. They do not certify the continuum "
            "capacity coefficient because the radius and grid limits are not "
            "independently extrapolated."
        ),
    }

    metrics_json = DATA / "finite_radius_2d_capacity_metrics.json"
    fixed_csv = DATA / "finite_radius_2d_fixed_kappa.csv"
    capacity_csv = DATA / "finite_radius_2d_capacity_rows.csv"
    fits_csv = DATA / "finite_radius_2d_capacity_fits.csv"
    _write_json(metrics_json, payload)
    _write_csv(fixed_csv, fixed_rows)
    _write_csv(capacity_csv, capacity_rows)
    _write_csv(fits_csv, capacity_fits)

    figure_pdf = FIGURES / "finite_radius_2d_capacity_scaling.pdf"
    figure_png = FIGURES / "finite_radius_2d_capacity_scaling.png"
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.8))

    ax = axes[0, 0]
    ax.set_aspect("equal")
    ax.add_patch(plt.Rectangle((0.0, 0.0), 1.0, 1.0, fill=False, lw=1.5))
    ax.add_patch(plt.Circle((0.5, 0.5), 0.14, color="#d95f02", alpha=0.25))
    ax.annotate(
        r"periodic relative coordinate $r=X_1-X_2$",
        xy=(0.5, 0.66),
        xytext=(0.08, 0.86),
        arrowprops={"arrowstyle": "->", "lw": 0.8},
        fontsize=8,
    )
    ax.text(
        0.96,
        0.045,
        "periodic in both coordinates",
        ha="right",
        va="bottom",
        fontsize=8,
    )
    ax.set(
        xlim=(-0.03, 1.03),
        ylim=(-0.03, 1.03),
        xlabel="relative x",
        ylabel="relative y",
        title="(a) relative-coordinate torus",
    )

    ax = axes[0, 1]
    radii = np.asarray([row["radius"] for row in fixed_rows])
    means = np.asarray([row["mean_time"] for row in fixed_rows])
    ax.loglog(radii, means, "o-", color="#7570b3", label="computed")
    ax.loglog(
        radii,
        1.0 / (FIXED_KAPPA * np.pi * radii**2),
        "--",
        color="black",
        label=r"$1/(\kappa\pi a^2)$",
    )
    ax.invert_xaxis()
    ax.set(
        xlabel="reaction radius a (smaller to the right)",
        ylabel="mean reaction time",
        title=REACTION_LIMIT_PANEL_TITLE,
    )
    ax.set_xticks([0.12, 0.05, 0.02], labels=["0.12", "0.05", "0.02"])
    ax.minorticks_off()
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    log_radius = np.log(1.0 / np.asarray(CAPACITY_RADII))
    colors = plt.cm.viridis(np.linspace(0.12, 0.88, len(CAPACITY_GRIDS)))
    for grid_n, color in zip(CAPACITY_GRIDS, colors, strict=True):
        grid_rows = [row for row in capacity_rows if row["grid_n"] == grid_n]
        values = np.asarray([row["mean_time"] for row in grid_rows])
        ax.plot(log_radius, values, "o-", color=color, ms=4, label=f"N={grid_n}")
    finest = capacity_fits[-1]
    ax.plot(
        log_radius,
        THEORY_LOG_SLOPE * log_radius + finest["fitted_intercept"],
        "--",
        color="black",
        lw=1.4,
        label="theory",
    )
    ax.set(
        xlabel="log(1/a)",
        ylabel="mean reaction time",
        title="(c) logarithmic-capacity slope",
    )
    ax.legend(frameon=False, fontsize=7)

    ax = axes[1, 1]
    spacings = np.asarray([row["spacing"] for row in capacity_fits])
    slope_ratios = np.asarray(
        [row["slope_ratio_to_theory"] for row in capacity_fits]
    )
    # Scale the tightly clustered spacings before plotting so the final-size
    # APS panel has short, non-overlapping tick labels.
    scaled_spacings = 1.0e3 * spacings
    ax.plot(scaled_spacings, slope_ratios, "o-", color="#1b9e77")
    ax.axhline(1.0, color="black", ls="--", lw=1.2, label="continuum")
    ax.invert_xaxis()
    ax.set(
        xlabel=r"$10^3 h$ (finer to the right)",
        ylabel="fitted slope / predicted slope",
        title="(d) slope convergence",
    )
    ax.legend(frameon=False, fontsize=8)

    for ax in axes.reshape(-1):
        ax.grid(alpha=0.18)
    enforce_publication_graphics(fig)
    fig.tight_layout()
    temporary_pdf = figure_pdf.with_name(f".{figure_pdf.stem}.tmp.pdf")
    temporary_png = figure_png.with_name(f".{figure_png.stem}.tmp.png")
    fig.savefig(temporary_pdf)
    fig.savefig(temporary_png, dpi=300)
    plt.close(fig)
    temporary_pdf.replace(figure_pdf)
    temporary_png.replace(figure_png)

    outputs = [
        metrics_json,
        fixed_csv,
        capacity_csv,
        fits_csv,
        figure_pdf,
        figure_png,
    ]
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=["python", str(HERE.relative_to(REPO))],
        model_spec={
            "geometry": "unit flat two-torus in relative coordinates",
            "relative_diffusivity": RELATIVE_DIFFUSIVITY,
            "reaction_model": "cell-averaged finite-radius Doi volume sink",
            "subcell_samples": SUBCELL_SAMPLES,
            "fixed_kappa": FIXED_KAPPA,
            "fixed_kappa_grid": FIXED_KAPPA_GRID,
            "fixed_kappa_radii": FIXED_KAPPA_RADII,
            "renormalized_chi": RENORMALIZED_CHI,
            "capacity_grids": CAPACITY_GRIDS,
            "capacity_radii": CAPACITY_RADII,
        },
        dependencies=[
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter2d.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
        ],
        outputs=outputs,
        horizon={
            "quantity": "mean reaction time from sparse backward solve",
            "theory_log_slope": THEORY_LOG_SLOPE,
        },
    )
    manifest_path = DATA / "finite_radius_2d_capacity.manifest.json"
    manifest_tmp = DATA / ".finite_radius_2d_capacity.manifest.tmp.json"
    write_manifest(manifest_tmp, manifest)
    manifest_tmp.replace(manifest_path)


if __name__ == "__main__":
    main()
