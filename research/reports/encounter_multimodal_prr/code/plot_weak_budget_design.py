#!/usr/bin/env python3
"""Render the frozen weak-budget/free-exposure design diagnostic.

The plotted quantities are recomputed from the pinned finite-volume producer.
They are a result-informed B=0 diagnostic, not evidence for a finite-B Doi
cusp, a continuum limit, a trimodal geometry, or the project-level claim.
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import continuum_weak_budget_design as design
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
RESULT = DATA / "continuum_weak_budget_design_result.json"
MANIFEST = DATA / "continuum_weak_budget_design_manifest.json"
PRODUCER = REPORT / "code" / "continuum_weak_budget_design.py"
OUTPUT_PDF = FIGURES / "weak_budget_design.pdf"
OUTPUT_PNG = FIGURES / "weak_budget_design.png"
OUTPUT_METADATA = FIGURES / "weak_budget_design_metadata.json"

EXPECTED_RESULT_SHA256 = "dcbfb9c9ccee4378a8ceeebe00be01de0bf5c5db7914b83032333e066439369f"
EXPECTED_MANIFEST_SHA256 = "b912aa5d9d6cd21601bab8ec847670b28934a20887319872571ed014622d5949"
EXPECTED_PRODUCER_SHA256 = "7fa9ea6114328736c89739459c293aefa9311514764ec3cfe4f0ceb5a1875201"
REQUIRED_FALSE_FLAGS = {
    "continuum_verified": False,
    "project_gate_passed": False,
    "finite_B_Doi_cusp_verified": False,
}


@dataclass(frozen=True)
class FigureData:
    times: np.ndarray
    channel_curves: np.ndarray
    simplex_weights: np.ndarray
    sampled_mode_counts: np.ndarray
    cusp: dict[str, Any]
    inward: dict[str, Any]


def _require_hash(path: Path, expected: str, label: str) -> None:
    observed = design.sha256(path)
    if observed != expected:
        raise ValueError(f"pinned {label} hash mismatch: expected {expected}, observed {observed}")


def preflight_sources(
    *,
    result_path: Path = RESULT,
    manifest_path: Path = MANIFEST,
    producer_path: Path = PRODUCER,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fail closed unless all frozen inputs and negative claim flags match."""

    _require_hash(result_path, EXPECTED_RESULT_SHA256, "result")
    _require_hash(manifest_path, EXPECTED_MANIFEST_SHA256, "manifest")
    _require_hash(producer_path, EXPECTED_PRODUCER_SHA256, "producer")
    result = design.load_json(result_path)
    manifest = design.load_json(manifest_path)

    if result["status"] != "PASS_RESULT_INFORMED_WEAK_BUDGET_DESIGN_DIAGNOSTIC":
        raise ValueError("frozen weak-budget result is not the declared bounded PASS")
    timing = "RESULT_INFORMED_REPRODUCTION_NOT_PREREGISTERED_DISCOVERY"
    if result["evidence_timing"] != timing or manifest["evidence_timing"] != timing:
        raise ValueError("result-informed evidence label was weakened")
    for flag, expected in REQUIRED_FALSE_FLAGS.items():
        if result.get(flag) is not expected:
            raise ValueError(f"result flag {flag} must remain false")
    if manifest["required_claim_flags"] != REQUIRED_FALSE_FLAGS:
        raise ValueError("manifest claim flags must all remain false")
    if result["provenance"]["manifest_sha256"] != EXPECTED_MANIFEST_SHA256:
        raise ValueError("result does not pin the expected manifest")
    if result["provenance"]["script_sha256"] != EXPECTED_PRODUCER_SHA256:
        raise ValueError("result does not pin the expected producer")
    if result["claim_scope"] != manifest["claim_scope"]:
        raise ValueError("result and manifest claim scopes disagree")
    if result["finite_volume_free_factorization_verified"] is not True:
        raise ValueError("finite-volume free-factorization reference did not pass")
    if manifest["physical_model"]["installed_budget_limit"] != 0.0:
        raise ValueError("this figure is restricted to the B=0 diagnostic")
    if manifest["physical_model"]["patch_centres"] != [0.48, 0.67, 0.86]:
        raise ValueError("the plot must not substitute the unfrozen redesigned geometry")
    expected_histogram = {"1": 4696, "2": 455}
    if result["simplex_screen"]["sampled_mode_count_histogram"] != expected_histogram:
        raise ValueError("unexpected frozen sampled-mode histogram")
    if result["simplex_screen"]["maximum_sampled_mode_count"] != 2:
        raise ValueError("the current geometry is not allowed to imply trimodality")
    return result, manifest


def simplex_mode_counts(
    channel_curves: np.ndarray,
    times: np.ndarray,
    manifest: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    """Recompute the sampled mode count at every frozen simplex control."""

    rules = manifest["simplex_screen"]
    weights = design.simplex_weights(int(rules["integer_denominator"]))
    counts = np.empty(len(weights), dtype=np.int8)
    for index, weight in enumerate(weights):
        density = channel_curves[0] @ weight
        derivative = channel_curves[1] @ weight
        maxima, _minima, _maximum_times = design.sampled_mode_count(
            density,
            derivative,
            times,
            minimum_time=float(rules["minimum_mode_analysis_time"]),
            relative_density_floor=float(rules["relative_density_floor"]),
            derivative_zero_relative_tolerance=float(rules["derivative_zero_relative_tolerance"]),
        )
        counts[index] = maxima
    return weights, counts


def _assert_close(observed: Any, expected: Any, label: str, *, atol: float) -> None:
    if not np.allclose(
        np.asarray(observed, dtype=float),
        np.asarray(expected, dtype=float),
        rtol=2.0e-10,
        atol=atol,
    ):
        raise RuntimeError(f"recomputed {label} disagrees with the frozen result")


def recompute_figure_data(
    result: dict[str, Any],
    manifest: dict[str, Any],
) -> FigureData:
    """Recompute every curve and simplex point used by the figure."""

    design.require_repository_venv()
    mesh = manifest["design_mesh"]
    grid = design.FactorGrid(
        midpoint_cells=int(mesh["midpoint_cells"]),
        relative_parallel_cells=int(mesh["relative_parallel_cells"]),
        relative_perp_cells=int(mesh["relative_perp_cells"]),
    )
    if grid.full_state_count != int(mesh["state_count_if_formed"]):
        raise ValueError("design mesh state count is inconsistent")
    factors = design.build_free_exposure_factors(grid)
    rules = manifest["simplex_screen"]
    times = np.linspace(
        float(rules["time_start"]),
        float(rules["time_stop"]),
        int(rules["time_points"]),
        dtype=float,
    )
    channel_curves = design.factorized_channel_curves(
        factors,
        times,
        chunk_points=int(rules["chunk_points"]),
    )
    digest = design._curve_digest(times, channel_curves)
    if digest != result["channel_curve_digest_sha256"]:
        raise RuntimeError("recomputed channel-curve digest disagrees with the frozen result")

    cusp = design.reproduce_cusp(factors, manifest)
    inward = design.verify_inward_direction(factors, channel_curves, times, cusp, manifest)
    frozen_cusp = result["cusp_reproduction"]
    frozen_inward = result["normal_form_inward_check"]
    _assert_close(cusp["cusp_time"], frozen_cusp["cusp_time"], "cusp time", atol=3.0e-10)
    _assert_close(cusp["weights"], frozen_cusp["weights"], "cusp weights", atol=3.0e-10)
    _assert_close(
        cusp["mixture_raw_jets_orders_0_to_4"],
        frozen_cusp["mixture_raw_jets_orders_0_to_4"],
        "cusp jets",
        atol=3.0e-11,
    )
    _assert_close(
        inward["perturbed_weights"],
        frozen_inward["perturbed_weights"],
        "inward weights",
        atol=3.0e-10,
    )
    _assert_close(
        [row["time"] for row in inward["stationary_roots"]],
        [row["time"] for row in frozen_inward["stationary_roots"]],
        "inward roots",
        atol=3.0e-9,
    )
    if inward["topology"] != ["maximum", "minimum", "maximum"]:
        raise RuntimeError("recomputed inward topology is not max-min-max")

    weights, mode_counts = simplex_mode_counts(channel_curves, times, manifest)
    values, counts = np.unique(mode_counts, return_counts=True)
    histogram = {str(int(value)): int(count) for value, count in zip(values, counts, strict=True)}
    if histogram != result["simplex_screen"]["sampled_mode_count_histogram"]:
        raise RuntimeError("recomputed simplex histogram disagrees with the frozen result")
    if int(np.max(mode_counts)) != 2:
        raise RuntimeError("recomputed current-geometry screen must have maximum count two")
    return FigureData(
        times=times,
        channel_curves=channel_curves,
        simplex_weights=weights,
        sampled_mode_counts=mode_counts,
        cusp=cusp,
        inward=inward,
    )


def barycentric_xy(weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Map (w1,w2,w3) to an equilateral simplex with w3 at the apex."""

    values = np.asarray(weights, dtype=float)
    if values.ndim != 2 or values.shape[1] != 3:
        raise ValueError("barycentric weights must have shape (n,3)")
    if not np.allclose(np.sum(values, axis=1), 1.0, atol=2.0e-14, rtol=0.0):
        raise ValueError("barycentric weights must sum to one")
    if np.min(values) < -2.0e-14:
        raise ValueError("barycentric weights must be nonnegative")
    x = values[:, 1] + 0.5 * values[:, 2]
    y = (np.sqrt(3.0) / 2.0) * values[:, 2]
    return x, y


def _plot_exposure_clocks(ax: plt.Axes, data: FigureData) -> None:
    times = data.times
    keep = times <= 30.0
    cusp_weights = np.asarray(data.cusp["weights"], dtype=float)
    mixture = data.channel_curves[0] @ cusp_weights
    colours = ("#2F6B9A", "#7A8535", "#C46A2B")
    styles = ("-", "--", "-.")
    centres = (0.48, 0.67, 0.86)
    for channel, (colour, style, centre) in enumerate(zip(colours, styles, centres, strict=True)):
        ax.plot(
            times[keep],
            data.channel_curves[0, keep, channel],
            color=colour,
            linestyle=style,
            linewidth=1.35,
            label=f"H{channel + 1}(t), centre {centre:.2f}",
        )
    ax.plot(
        times[keep],
        mixture[keep],
        color="#22252A",
        linewidth=2.0,
        label="cusp mixture",
        zorder=4,
    )
    cusp_time = float(data.cusp["cusp_time"])
    cusp_density = float(data.cusp["density_per_unit_budget"])
    ax.axvline(cusp_time, color="#777C84", linewidth=0.8, linestyle=":")
    ax.plot(cusp_time, cusp_density, marker="o", markersize=4.2, color="#22252A", zorder=5)
    ax.annotate(
        f"t* = {cusp_time:.3f}",
        xy=(cusp_time, cusp_density),
        xytext=(12.0, 0.215),
        arrowprops={"arrowstyle": "-", "color": "#555A62", "linewidth": 0.7},
        fontsize=7.2,
        color="#33363B",
    )
    ax.set_xlim(0.0, 30.0)
    ax.set_ylim(bottom=0.0)
    ax.set_xlabel("Dimensionless time, t")
    ax.set_ylabel("Exposure density per unit budget, H(t)")
    ax.set_title(
        "(a) Free-exposure clocks and cusp mixture\nB=0; 207,025-state finite-volume quotient",
        loc="left",
    )
    ax.legend(loc="upper right", frameon=False, fontsize=6.8, handlelength=2.8)


def _plot_local_derivative(ax: plt.Axes, data: FigureData) -> None:
    cusp_time = float(data.cusp["cusp_time"])
    keep = (data.times >= cusp_time - 3.0) & (data.times <= cusp_time + 3.0)
    cusp_weights = np.asarray(data.cusp["weights"], dtype=float)
    inward_weights = np.asarray(data.inward["perturbed_weights"], dtype=float)
    cusp_derivative = data.channel_curves[1] @ cusp_weights
    inward_derivative = data.channel_curves[1] @ inward_weights
    ax.axhline(0.0, color="#777C84", linewidth=0.8)
    ax.plot(
        data.times[keep],
        cusp_derivative[keep],
        color="#2F6B9A",
        linewidth=1.5,
        linestyle="--",
        label="cusp weights",
    )
    ax.plot(
        data.times[keep],
        inward_derivative[keep],
        color="#C46A2B",
        linewidth=1.8,
        label="inward step 0.005",
    )
    ax.plot(cusp_time, 0.0, marker="D", markersize=4.2, color="#2F6B9A", zorder=5)
    for index, row in enumerate(data.inward["stationary_roots"]):
        root = float(row["time"])
        topology = str(row["topology"])
        marker = "v" if topology == "maximum" else "^"
        ax.plot(root, 0.0, marker=marker, markersize=5.0, color="#8D431F", zorder=5)
        offset = 8 if index != 1 else -14
        ax.annotate(
            "max" if topology == "maximum" else "min",
            xy=(root, 0.0),
            xytext=(0, offset),
            textcoords="offset points",
            ha="center",
            va="bottom" if offset > 0 else "top",
            fontsize=6.8,
            color="#6C351C",
        )
    ax.set_xlim(cusp_time - 3.0, cusp_time + 3.0)
    ax.set_xlabel("Dimensionless time, t")
    ax.set_ylabel("Time derivative, dH_w/dt")
    ax.set_title(
        "(b) Local stationary-point unfolding\nThe inward control has three resolved roots",
        loc="left",
    )
    ax.legend(loc="upper right", frameon=False, fontsize=7.0, handlelength=2.7)


def _plot_simplex(ax: plt.Axes, data: FigureData) -> None:
    x, y = barycentric_xy(data.simplex_weights)
    one = data.sampled_mode_counts == 1
    two = data.sampled_mode_counts == 2
    ax.scatter(
        x[one],
        y[one],
        s=4.0,
        marker="o",
        facecolors="#D6DCE3",
        edgecolors="#D6DCE3",
        linewidths=0.0,
        rasterized=False,
    )
    ax.scatter(
        x[two],
        y[two],
        s=7.0,
        marker="s",
        facecolors="#C46A2B",
        edgecolors="#9A4A22",
        linewidths=0.25,
        rasterized=False,
    )
    height = np.sqrt(3.0) / 2.0
    ax.plot((0.0, 1.0, 0.5, 0.0), (0.0, 0.0, height, 0.0), color="#33363B", lw=0.9)
    cusp_x, cusp_y = barycentric_xy(np.asarray([data.cusp["weights"]], dtype=float))
    inward_x, inward_y = barycentric_xy(np.asarray([data.inward["perturbed_weights"]], dtype=float))
    ax.plot(cusp_x, cusp_y, marker="x", markersize=7.0, mew=1.4, color="#111316")
    ax.plot(
        inward_x,
        inward_y,
        marker="D",
        markersize=5.0,
        markerfacecolor="white",
        markeredgecolor="#111316",
        markeredgewidth=1.0,
    )
    ax.text(-0.025, -0.028, "w1=1\ncentre 0.48", ha="right", va="top", fontsize=7.0)
    ax.text(1.025, -0.028, "w2=1\ncentre 0.67", ha="left", va="top", fontsize=7.0)
    ax.text(0.5, height + 0.028, "w3=1; centre 0.86", ha="center", va="bottom", fontsize=7.0)
    handles = [
        Line2D(
            [],
            [],
            marker="o",
            linestyle="none",
            markerfacecolor="#D6DCE3",
            markeredgecolor="#D6DCE3",
            markersize=4.5,
            label="1 sampled mode (4696)",
        ),
        Line2D(
            [],
            [],
            marker="s",
            linestyle="none",
            markerfacecolor="#C46A2B",
            markeredgecolor="#9A4A22",
            markersize=4.5,
            label="2 sampled modes (455)",
        ),
        Line2D(
            [],
            [],
            marker="x",
            linestyle="none",
            markeredgecolor="#111316",
            markersize=5.5,
            label="reproduced cusp",
        ),
        Line2D(
            [],
            [],
            marker="D",
            linestyle="none",
            markerfacecolor="white",
            markeredgecolor="#111316",
            markersize=4.5,
            label="inward perturbation",
        ),
    ]
    ax.legend(
        handles=handles,
        loc="upper right",
        bbox_to_anchor=(0.995, 0.79),
        frameon=False,
        fontsize=7.1,
        ncol=1,
    )
    ax.text(
        0.012,
        0.74,
        "Maximum sampled count = 2\nNo trimodal sample\nin the current geometry",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7.3,
        color="#33363B",
    )
    ax.set_xlim(-0.43, 1.43)
    ax.set_ylim(-0.105, height + 0.105)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        "(c) Sampled catalyst-weight simplex\n5151 controls; weight and time spacing 0.01",
        loc="left",
        pad=3.0,
    )


def render_figure(data: FigureData, pdf_path: Path, png_path: Path) -> None:
    """Render deterministic vector and preview outputs without transparency."""

    rc = {
        "font.family": "DejaVu Sans",
        "font.size": 8.0,
        "axes.titlesize": 9.2,
        "axes.titleweight": "normal",
        "axes.labelsize": 7.8,
        "axes.edgecolor": "#4E535A",
        "axes.linewidth": 0.75,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#E3E6EA",
        "grid.linewidth": 0.55,
        "grid.alpha": 1.0,
        "xtick.labelsize": 7.0,
        "ytick.labelsize": 7.0,
        "xtick.color": "#4E535A",
        "ytick.color": "#4E535A",
        "text.color": "#22252A",
        "axes.labelcolor": "#33363B",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.transparent": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
    with plt.rc_context(rc):
        figure = plt.figure(figsize=(7.2, 6.7))
        grid = figure.add_gridspec(2, 2, height_ratios=(0.92, 1.15))
        panel_a = figure.add_subplot(grid[0, 0])
        panel_b = figure.add_subplot(grid[0, 1])
        panel_c = figure.add_subplot(grid[1, :])
        figure.patch.set_edgecolor("white")
        figure.patch.set_linewidth(0.0)
        for panel in (panel_a, panel_b, panel_c):
            panel.patch.set_edgecolor("white")
            panel.patch.set_linewidth(0.0)
        _plot_exposure_clocks(panel_a, data)
        _plot_local_derivative(panel_b, data)
        _plot_simplex(panel_c, data)
        figure.subplots_adjust(
            left=0.085,
            right=0.985,
            bottom=0.105,
            top=0.905,
            wspace=0.27,
            hspace=0.36,
        )
        figure.text(
            0.5,
            0.018,
            "Result-informed B=0 discrete finite-volume diagnostic. "
            "No finite-B, continuum, project-gate, or trimodality claim.",
            ha="center",
            va="bottom",
            fontsize=7.2,
            color="#444950",
        )
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        png_path.parent.mkdir(parents=True, exist_ok=True)
        fixed_date = datetime(2026, 7, 13, tzinfo=timezone.utc)
        metadata = {
            "Title": "Weak-budget free-exposure design diagnostic",
            "Author": "Encounter multimodality project",
            "Subject": "Result-informed B=0 finite-volume diagnostic",
            "Keywords": "encounter time, free exposure, cusp, finite volume, B=0",
            "Creator": "plot_weak_budget_design.py",
            "CreationDate": fixed_date,
            "ModDate": fixed_date,
        }
        figure.savefig(
            pdf_path,
            format="pdf",
            dpi=300,
            facecolor="white",
            edgecolor="white",
            metadata=metadata,
        )
        figure.savefig(
            png_path,
            format="png",
            dpi=240,
            facecolor="white",
            edgecolor="white",
            metadata={"Software": "plot_weak_budget_design.py"},
        )
        plt.close(figure)


def verify_vector_pdf(path: Path) -> dict[str, int]:
    """Reject Type 3 fonts, transparency states, and raster image XObjects."""

    payload = path.read_bytes()
    if not payload.startswith(b"%PDF-"):
        raise RuntimeError("figure output is not a PDF")
    type3_tokens = len(re.findall(rb"/Type3\b", payload))
    transparency_tokens = len(re.findall(rb"/(?:ca|CA|SMask|BM)\b", payload))
    raster_image_tokens = len(re.findall(rb"/Subtype\s*/Image\b", payload))
    if type3_tokens:
        raise RuntimeError("figure PDF contains a Type 3 font")
    if transparency_tokens:
        raise RuntimeError("figure PDF contains a transparency graphics-state token")
    if raster_image_tokens:
        raise RuntimeError("figure PDF contains a raster image XObject")
    return {
        "type3_font_tokens": type3_tokens,
        "transparency_graphics_state_tokens": transparency_tokens,
        "raster_image_xobject_tokens": raster_image_tokens,
    }


def build_metadata(
    data: FigureData,
    result: dict[str, Any],
    manifest: dict[str, Any],
    *,
    pdf_path: Path,
    png_path: Path,
    pdf_qa: dict[str, int],
) -> dict[str, Any]:
    values, counts = np.unique(data.sampled_mode_counts, return_counts=True)
    histogram = {str(int(value)): int(count) for value, count in zip(values, counts, strict=True)}
    return {
        "schema_version": 1,
        "stage": "G1w_weak_budget_figure",
        "status": "PASS_BOUNDED_FIGURE_REPRODUCTION",
        "evidence_timing": result["evidence_timing"],
        "claim_scope": result["claim_scope"],
        "continuum_verified": False,
        "project_gate_passed": False,
        "finite_B_Doi_cusp_verified": False,
        "trimodality_verified": False,
        "source_pins": {
            "result": str(RESULT.relative_to(REPORT)),
            "result_sha256": EXPECTED_RESULT_SHA256,
            "manifest": str(MANIFEST.relative_to(REPORT)),
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "producer": str(PRODUCER.relative_to(REPORT)),
            "producer_sha256": EXPECTED_PRODUCER_SHA256,
        },
        "recomputation": {
            "channel_curve_digest_sha256": design._curve_digest(data.times, data.channel_curves),
            "cusp_time": data.cusp["cusp_time"],
            "cusp_weights": data.cusp["weights"],
            "inward_step": data.inward["step"],
            "inward_stationary_roots": data.inward["stationary_roots"],
            "sampled_mode_count_histogram": histogram,
            "maximum_sampled_mode_count": int(np.max(data.sampled_mode_counts)),
            "simplex_control_count": int(len(data.simplex_weights)),
        },
        "chart_contract": {
            "analytical_question": (
                "Does the frozen current geometry show a B=0 free-exposure cusp, its local "
                "two-mode unfolding, and a sampled two-mode region on the full 0.01 simplex?"
            ),
            "takeaway": (
                "The result-informed discrete diagnostic reproduces the cusp and a local "
                "max-min-max unfolding; 455 of 5151 sampled controls are bimodal, and none "
                "is trimodal."
            ),
            "panels": {
                "a": "three free-exposure channel clocks and their cusp mixture",
                "b": "local derivative at the cusp and at the frozen inward perturbation",
                "c": "complete 0.01 sampled simplex map of one versus two sampled modes",
            },
            "palette_policy": (
                "explicit restrained channel colours plus neutral cusp mixture; mode classes "
                "also differ by marker shape and fill"
            ),
            "renderer": "Matplotlib static PDF and PNG",
        },
        "render_policy": {
            "figure_inches": [7.2, 6.7],
            "pdf_fonttype": 42,
            "transparent_background": False,
            "font_family": "DejaVu Sans",
        },
        "pdf_qa": pdf_qa,
        "outputs": {
            "pdf": str(pdf_path.relative_to(REPORT)),
            "pdf_sha256": design.sha256(pdf_path),
            "png": str(png_path.relative_to(REPORT)),
            "png_sha256": design.sha256(png_path),
        },
        "provenance": {
            "plot_script": str(HERE.relative_to(REPORT)),
            "plot_script_sha256": design.sha256(HERE),
            "source_result_generated_utc": result["provenance"]["generated_utc"],
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "limitations": list(result["limitations"]),
        "caption": (
            "Weak-budget/free-exposure design diagnostic for the frozen current geometry. "
            "(a) The three B=0 free-exposure clocks and their reproduced cusp mixture on one "
            "207,025-state finite-volume quotient. (b) The cusp derivative and the frozen "
            "inward perturbation, whose three stationary roots have max-min-max topology. "
            "(c) The complete 0.01 catalyst-weight simplex screen: 4696 controls have one "
            "sampled mode and 455 have two. This result-informed finite-grid diagnostic is "
            "neither a finite-B or continuum verification nor a trimodality claim."
        ),
        "manifest_stage": manifest["stage"],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=OUTPUT_PDF)
    parser.add_argument("--png", type=Path, default=OUTPUT_PNG)
    parser.add_argument("--metadata", type=Path, default=OUTPUT_METADATA)
    args = parser.parse_args(argv)
    result, manifest = preflight_sources()
    figure_data = recompute_figure_data(result, manifest)
    render_figure(figure_data, args.pdf, args.png)
    pdf_qa = verify_vector_pdf(args.pdf)
    metadata = build_metadata(
        figure_data,
        result,
        manifest,
        pdf_path=args.pdf,
        png_path=args.png,
        pdf_qa=pdf_qa,
    )
    write_json(args.metadata, metadata)
    print(f"status={metadata['status']}")
    print(f"histogram={metadata['recomputation']['sampled_mode_count_histogram']}")
    print(f"pdf={args.pdf}")
    print(f"png={args.png}")
    print(f"metadata={args.metadata}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
