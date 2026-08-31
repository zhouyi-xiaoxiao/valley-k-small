#!/usr/bin/env python3
"""Render the pinned physical-d=2 versus physical-d=3 shape comparison.

The figure compares exact B=0 free-exposure kernels at the same physical
parameters and slab geometry, using each dimension's separately frozen
selected conserved allocation.  It is result-informed and concerns relative
shape only; it supplies no event-mass, interval, finite-B, independent-PDE, or
project-gate evidence.
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

import continuum_observable_four_patch as d2_design
import continuum_observable_four_patch_d3 as d3_design
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"

D2_RESULT = DATA / "continuum_observable_four_patch_result.json"
D2_MANIFEST = DATA / "continuum_observable_four_patch_manifest.json"
D2_PRODUCER = REPORT / "code" / "continuum_observable_four_patch.py"
D2_TEST = REPORT / "code" / "test_continuum_observable_four_patch.py"
D3_RESULT = DATA / "continuum_observable_four_patch_d3_result.json"
D3_MANIFEST = DATA / "continuum_observable_four_patch_d3_manifest.json"
D3_PRODUCER = REPORT / "code" / "continuum_observable_four_patch_d3.py"
D3_TEST = REPORT / "code" / "test_continuum_observable_four_patch_d3.py"

OUTPUT_PDF = FIGURES / "d2_d3_four_patch.pdf"
OUTPUT_PNG = FIGURES / "d2_d3_four_patch.png"
OUTPUT_METADATA = FIGURES / "d2_d3_four_patch_metadata.json"

EXPECTED_HASHES = {
    "d2": {
        "result": "4a929cdaf915a9b6180acc0c272a16ae77087d097f2d078b6483c6c9b320a9fc",
        "manifest": "1c79fcb31abbc622cee20e915d60f55337376d7555c1c25dab210b3cc5976a69",
        "producer": "a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da",
        "test": "c3a2c11c71daf9fcb04e1db9e7c4e489a515d7dfbbb51bc470d310d0c3f76243",
    },
    "d3": {
        "result": "125234df2817287c30699d80e30af0e711c036193f0a64a404c8f3e98f98f984",
        "manifest": "a11e1c4a7842ae69efc76e21a4b6587981d612a457070d601e7001810f16b8cb",
        "producer": "f8fde83ecdf435acf28a32fb0dec6a22f216bf9f5a817d954f165e62811bf885",
        "test": "bcb0b4264d0d89f140017004b083cb16ad7bf8f8ac7a8ab7b59f48ff9cef3a56",
    },
}

D2_REQUIRED_CLAIM_FLAGS = {
    "continuum_verified": False,
    "finite_B_Doi_verified": False,
    "observable_free_exposure_confirmation_passed": True,
    "preregistered_discovery": False,
    "project_gate_passed": False,
}
D3_REQUIRED_CLAIM_FLAGS = {
    "continuum_verified": False,
    "finite_B_Doi_verified": False,
    "independent_PDE_solver_verified": False,
    "observable_d3_free_exposure_confirmation_passed": True,
    "preregistered_discovery": False,
    "project_gate_passed": False,
}
FIGURE_CLAIM_FLAGS = {
    "preregistered_discovery": False,
    "continuum_verified": False,
    "finite_B_Doi_verified": False,
    "independent_PDE_solver_verified": False,
    "project_gate_passed": False,
    "relative_shape_only": True,
    "event_mass_observability_verified": False,
    "d2_relative_shape_gate_passed": True,
    "d3_relative_shape_gate_passed": True,
}

EVIDENCE_TIMING = "RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY"
D2_STATUS = "PASS_RESULT_INFORMED_OBSERVABLE_FREE_EXPOSURE_CONFIRMATION"
D3_STATUS = "PASS_RESULT_INFORMED_PHYSICAL_D3_OBSERVABLE_FREE_EXPOSURE_CONFIRMATION"
FIGURE_STATUS = "PASS_RESULT_INFORMED_D2_D3_RELATIVE_SHAPE_COMPARISON_FIGURE"

BLUE = "#2F6B9A"
ORANGE = "#C46A2B"
INK = "#22252A"
MID_GREY = "#6F747C"
LIGHT_GREY = "#E2E5E9"
PALE_GREY = "#F4F5F6"

CHART_CONTRACT = {
    "analytical_question": (
        "With the same four-slab geometry and physical parameters, do the exact "
        "physical-d=2 disk and physical-d=3 sphere B=0 free-exposure kernels both "
        "retain relative-prominence-qualified three-peak shape under their separately "
        "frozen selected conserved allocations?"
    ),
    "takeaway": (
        "Both dimensions pass the frozen relative-shape gates, but physical d=3 has "
        "weaker peak balance and its second valley lies closer to the 0.85 ceiling."
    ),
    "canonical_family": "small-multiple trend plus benchmarked dot comparison",
    "static_variant": (
        "two normalized line panels with refined root markers and one connected-dot "
        "panel with category-specific benchmark segments"
    ),
    "data_sufficiency": {
        "trend_time_range": [0.1, 30.0],
        "trend_points_per_dimension": 2401,
        "stationary_roots_per_dimension": 5,
        "shape_metrics_per_dimension": 3,
        "grain": (
            "exact-kernel density shape on a common time grid; refined stationary roots "
            "and dimension-level relative-height metrics"
        ),
    },
    "comparison_scope": (
        "shared diffusion, drift, contact radius, slab centres, slab widths, and initial "
        "law; each dimension uses its own frozen selected weight vector"
    ),
    "palette_policy": "hard two-root cap: d2 blue and d3 orange plus neutrals",
    "non_colour_distinction": (
        "d2 solid line and filled circles; d3 dashed line and open squares; maxima and "
        "minima use different marker shapes"
    ),
    "output_footprint": "7.2 x 3.15 inch static figure* for a double-column manuscript",
    "renderer": "Matplotlib static vector PDF with a PNG review preview",
    "visible_scope_note": (
        "B=0; result-informed; relative shape only; continuum_verified=false; "
        "finite_B=false; independent_PDE=false; project=false"
    ),
}


@dataclass(frozen=True)
class DimensionData:
    label: str
    physical_dimension: int
    times: np.ndarray
    mixture: np.ndarray
    normalized_mixture: np.ndarray
    mixture_derivative: np.ndarray
    selected_weights: np.ndarray
    selected_step: float
    roots: tuple[dict[str, Any], ...]
    root_times: np.ndarray
    root_density: np.ndarray
    normalized_root_density: np.ndarray
    peak_ratio: float
    valley_ratios: tuple[float, float]
    normalizer: float


@dataclass(frozen=True)
class FigureData:
    d2: DimensionData
    d3: DimensionData


def _require_hash(path: Path, expected: str, label: str) -> None:
    observed = d2_design.sha256(path)
    if observed != expected:
        raise ValueError(f"pinned {label} hash mismatch: expected {expected}, observed {observed}")


def preflight_sources(
    *,
    d2_result_path: Path = D2_RESULT,
    d2_manifest_path: Path = D2_MANIFEST,
    d2_producer_path: Path = D2_PRODUCER,
    d2_test_path: Path = D2_TEST,
    d3_result_path: Path = D3_RESULT,
    d3_manifest_path: Path = D3_MANIFEST,
    d3_producer_path: Path = D3_PRODUCER,
    d3_test_path: Path = D3_TEST,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Fail closed unless both frozen evidence chains and scopes match."""

    paths = {
        "d2": {
            "result": d2_result_path,
            "manifest": d2_manifest_path,
            "producer": d2_producer_path,
            "test": d2_test_path,
        },
        "d3": {
            "result": d3_result_path,
            "manifest": d3_manifest_path,
            "producer": d3_producer_path,
            "test": d3_test_path,
        },
    }
    for dimension, members in paths.items():
        for member, path in members.items():
            _require_hash(path, EXPECTED_HASHES[dimension][member], f"{dimension} {member}")

    d2_result = d2_design.load_json(d2_result_path)
    d2_manifest = d2_design.load_json(d2_manifest_path)
    d3_result = d2_design.load_json(d3_result_path)
    d3_manifest = d2_design.load_json(d3_manifest_path)
    if d2_result["status"] != D2_STATUS or d3_result["status"] != D3_STATUS:
        raise ValueError("one frozen dimension result is not the declared PASS")
    if {
        d2_result["evidence_timing"],
        d2_manifest["evidence_timing"],
        d3_result["evidence_timing"],
        d3_manifest["evidence_timing"],
    } != {EVIDENCE_TIMING}:
        raise ValueError("result-informed evidence timing was weakened")
    if d2_result["claim_flags"] != D2_REQUIRED_CLAIM_FLAGS:
        raise ValueError("d2 claim flags do not match the frozen scope")
    if d3_result["claim_flags"] != D3_REQUIRED_CLAIM_FLAGS:
        raise ValueError("d3 claim flags do not match the frozen scope")
    if not all(d2_result["gates"].values()) or not all(d3_result["gates"].values()):
        raise ValueError("one or more frozen numerical gates are false")

    expected_provenance = {
        "d2": {
            "manifest_sha256": EXPECTED_HASHES["d2"]["manifest"],
            "producer_sha256": EXPECTED_HASHES["d2"]["producer"],
            "test_sha256": EXPECTED_HASHES["d2"]["test"],
        },
        "d3": {
            "manifest_sha256": EXPECTED_HASHES["d3"]["manifest"],
            "producer_sha256": EXPECTED_HASHES["d3"]["producer"],
            "test_sha256": EXPECTED_HASHES["d3"]["test"],
        },
    }
    for dimension, result in (("d2", d2_result), ("d3", d3_result)):
        for key, expected in expected_provenance[dimension].items():
            if result["provenance"].get(key) != expected:
                raise ValueError(f"{dimension} result provenance mismatch for {key}")
        selected = result["inward_step_scan"]["selected"]
        structure = selected["stationary_structure"]
        if selected["eligible"] is not True:
            raise ValueError(f"{dimension} selected candidate is not eligible")
        if structure["topology"] != [
            "maximum",
            "minimum",
            "maximum",
            "minimum",
            "maximum",
        ]:
            raise ValueError(f"{dimension} topology is not max-min-max-min-max")
        if structure["peak_minimum_to_maximum_ratio"] < 0.10:
            raise ValueError(f"{dimension} peak ratio fails the common floor")
        if max(structure["valley_to_smaller_adjacent_peak_ratios"]) > 0.85:
            raise ValueError(f"{dimension} valley ratio fails the common ceiling")

    if d2_result["model"]["parameters"] != d3_result["model"]["parameters"]:
        raise ValueError("d2 and d3 physical parameter dictionaries differ")
    if d2_result["model"]["physical_dimension"] != 2:
        raise ValueError("d2 result has the wrong physical dimension")
    if d3_result["model"]["physical_dimension"] != 3:
        raise ValueError("d3 result has the wrong physical dimension")
    return d2_result, d2_manifest, d3_result, d3_manifest


def _assert_close(observed: Any, expected: Any, label: str, *, atol: float) -> None:
    if not np.allclose(
        np.asarray(observed, dtype=float),
        np.asarray(expected, dtype=float),
        rtol=3.0e-11,
        atol=atol,
    ):
        raise RuntimeError(f"recomputed {label} disagrees with the frozen result")


def _recompute_dimension(
    result: dict[str, Any],
    *,
    label: str,
    physical_dimension: int,
) -> DimensionData:
    selected = result["inward_step_scan"]["selected"]
    selected_weights = np.asarray(selected["weights"], dtype=float)
    roots = tuple(selected["stationary_structure"]["roots"])
    root_times = np.asarray([row["time"] for row in roots], dtype=float)
    times = np.linspace(0.1, 30.0, 2401, dtype=float)
    if physical_dimension == 2:
        model = d2_design.FourPatchContinuum(d2_design.FINE)
    elif physical_dimension == 3:
        model = d3_design.FourPatchContinuumD3(d3_design.FINE)
    else:
        raise ValueError("only physical dimensions two and three are supported")

    channels, derivatives = model.real_channels_and_first_derivatives(times)
    root_channels, root_derivatives = model.real_channels_and_first_derivatives(root_times)
    mixture = channels @ selected_weights
    mixture_derivative = derivatives @ selected_weights
    root_density = root_channels @ selected_weights
    root_d1 = root_derivatives @ selected_weights
    if np.any(~np.isfinite(mixture)) or np.any(mixture < -2.0e-14):
        raise RuntimeError(f"{label} recomputed curve is invalid")
    frozen_root_density = np.asarray([row["density"] for row in roots], dtype=float)
    _assert_close(root_density, frozen_root_density, f"{label} root densities", atol=6.0e-12)
    if float(np.max(np.abs(root_d1))) > 3.0e-13:
        raise RuntimeError(f"{label} refined roots have excessive derivative residual")

    peak_density = root_density[[0, 2, 4]]
    valley_density = root_density[[1, 3]]
    peak_ratio = float(np.min(peak_density) / np.max(peak_density))
    valley_ratios = (
        float(valley_density[0] / min(peak_density[0], peak_density[1])),
        float(valley_density[1] / min(peak_density[1], peak_density[2])),
    )
    frozen_structure = selected["stationary_structure"]
    _assert_close(
        peak_ratio,
        frozen_structure["peak_minimum_to_maximum_ratio"],
        f"{label} peak ratio",
        atol=2.0e-12,
    )
    _assert_close(
        valley_ratios,
        frozen_structure["valley_to_smaller_adjacent_peak_ratios"],
        f"{label} valley ratios",
        atol=2.0e-12,
    )
    normalizer = float(np.max(peak_density))
    normalized_mixture = mixture / normalizer
    normalized_root_density = root_density / normalizer
    if float(np.max(normalized_mixture)) > 1.00002:
        raise RuntimeError(f"{label} dense curve exceeds the refined-root normalizer")
    return DimensionData(
        label=label,
        physical_dimension=physical_dimension,
        times=times,
        mixture=mixture,
        normalized_mixture=normalized_mixture,
        mixture_derivative=mixture_derivative,
        selected_weights=selected_weights,
        selected_step=float(selected["step"]),
        roots=roots,
        root_times=root_times,
        root_density=root_density,
        normalized_root_density=normalized_root_density,
        peak_ratio=peak_ratio,
        valley_ratios=valley_ratios,
        normalizer=normalizer,
    )


def recompute_figure_data(
    d2_result: dict[str, Any],
    _d2_manifest: dict[str, Any],
    d3_result: dict[str, Any],
    _d3_manifest: dict[str, Any],
) -> FigureData:
    d2_design.require_repository_venv()
    return FigureData(
        d2=_recompute_dimension(d2_result, label="physical d=2", physical_dimension=2),
        d3=_recompute_dimension(d3_result, label="physical d=3", physical_dimension=3),
    )


def _plot_shape_panel(
    ax: plt.Axes,
    data: DimensionData,
    *,
    colour: str,
    line_style: str,
    dimension_marker: str,
    title: str,
    show_y_label: bool,
) -> None:
    ax.plot(
        data.times,
        data.normalized_mixture,
        color=colour,
        linewidth=1.65,
        linestyle=line_style,
        label=f"{data.label} mixture",
    )
    maxima = np.asarray([row["topology"] == "maximum" for row in data.roots])
    minima = ~maxima
    ax.plot(
        data.root_times[maxima],
        data.normalized_root_density[maxima],
        linestyle="none",
        marker=dimension_marker,
        markersize=5.2,
        markerfacecolor=colour if data.physical_dimension == 2 else "white",
        markeredgecolor=colour,
        markeredgewidth=1.0,
        label="maxima",
        zorder=5,
    )
    ax.plot(
        data.root_times[minima],
        data.normalized_root_density[minima],
        linestyle="none",
        marker="v",
        markersize=5.0,
        markerfacecolor="white",
        markeredgecolor=colour,
        markeredgewidth=1.0,
        label="minima",
        zorder=5,
    )
    ax.text(
        0.97,
        0.94,
        f"$s_*={data.selected_step:.2f}$\n3 maxima + 2 minima",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.5,
        color=INK,
    )
    ax.set_xlim(0.1, 30.0)
    ax.set_ylim(0.0, 1.055)
    ax.set_xticks((0.1, 5, 10, 15, 20, 25, 30))
    ax.set_xticklabels((".1", "5", "10", "15", "20", "25", "30"))
    ax.set_xlim(0.1, 30.0)
    ax.set_yticks((0.0, 0.25, 0.5, 0.75, 1.0))
    ax.set_xlabel("dimensionless time $t$")
    if show_y_label:
        ax.set_ylabel(r"$G(t)/\max G$")
    else:
        ax.tick_params(labelleft=False)
    ax.set_title(title, loc="left", pad=7.0)


def _plot_metric_panel(ax: plt.Axes, data: FigureData) -> None:
    categories = ("peak balance ↑", "valley 1 ↓", "valley 2 ↓")
    y = np.asarray((2.0, 1.0, 0.0))
    d2_values = np.asarray((data.d2.peak_ratio, *data.d2.valley_ratios))
    d3_values = np.asarray((data.d3.peak_ratio, *data.d3.valley_ratios))
    d2_y = y + 0.10
    d3_y = y - 0.10
    for index in range(3):
        ax.plot(
            (d2_values[index], d3_values[index]),
            (d2_y[index], d3_y[index]),
            color="#A8ADB4",
            linewidth=0.75,
            zorder=1,
        )
    ax.scatter(
        d2_values,
        d2_y,
        s=31,
        marker="o",
        facecolor=BLUE,
        edgecolor=BLUE,
        linewidth=0.8,
        label="physical d=2",
        zorder=4,
    )
    ax.scatter(
        d3_values,
        d3_y,
        s=34,
        marker="s",
        facecolor="white",
        edgecolor=ORANGE,
        linewidth=1.15,
        label="physical d=3",
        zorder=4,
    )
    for values, positions, colour, horizontal in (
        (d2_values, d2_y, BLUE, "right"),
        (d3_values, d3_y, ORANGE, "left"),
    ):
        offset = -0.018 if horizontal == "right" else 0.018
        for value, position in zip(values, positions, strict=True):
            ax.text(
                value + offset,
                position,
                f"{value:.3f}",
                ha=horizontal,
                va="center",
                fontsize=6.0,
                color=colour,
            )

    ax.plot((0.10, 0.10), (1.73, 2.27), color=MID_GREY, linewidth=0.9, linestyle="--")
    for centre in (1.0, 0.0):
        ax.plot(
            (0.85, 0.85),
            (centre - 0.27, centre + 0.27),
            color=MID_GREY,
            linewidth=0.9,
            linestyle=":",
        )
    ax.text(0.10, 2.31, "floor .10", ha="center", va="bottom", fontsize=5.8, color=MID_GREY)
    ax.text(0.85, 1.31, "ceiling .85", ha="center", va="bottom", fontsize=5.8, color=MID_GREY)
    ax.annotate(
        "d3 margin\n0.0052",
        xy=(data.d3.valley_ratios[1], d3_y[2]),
        xytext=(0.69, 0.36),
        arrowprops={"arrowstyle": "-", "color": ORANGE, "linewidth": 0.7},
        ha="left",
        va="center",
        fontsize=5.9,
        color=ORANGE,
    )
    ax.set_xlim(0.0, 1.015)
    ax.set_ylim(-0.42, 2.45)
    ax.set_xticks((0.0, 0.10, 0.40, 0.70, 0.85, 1.0))
    ax.set_xticklabels(("0", ".10", ".40", ".70", ".85", "1"))
    ax.set_yticks(y)
    ax.set_yticklabels(categories)
    ax.set_xlabel("relative-height ratio")
    ax.set_title("(c) Relative-shape metrics", loc="left", pad=7.0)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.15, 0.995),
        ncol=2,
        frameon=False,
        fontsize=5.7,
        handletextpad=0.4,
        columnspacing=0.9,
    )


def render_figure(data: FigureData, pdf_path: Path, png_path: Path) -> None:
    """Render deterministic manuscript-ready vector and preview outputs."""

    rc = {
        "font.family": "DejaVu Sans",
        "font.size": 7.5,
        "axes.titlesize": 8.2,
        "axes.titleweight": "normal",
        "axes.labelsize": 7.0,
        "axes.edgecolor": "#4E535A",
        "axes.linewidth": 0.7,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": LIGHT_GREY,
        "grid.linewidth": 0.5,
        "grid.alpha": 1.0,
        "xtick.labelsize": 6.2,
        "ytick.labelsize": 6.2,
        "xtick.color": "#4E535A",
        "ytick.color": "#4E535A",
        "text.color": INK,
        "axes.labelcolor": "#33363B",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.transparent": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
    with plt.rc_context(rc):
        figure, axes = plt.subplots(
            1,
            3,
            figsize=(7.2, 3.15),
            gridspec_kw={"width_ratios": (0.93, 0.93, 1.22), "wspace": 0.50},
            sharey=False,
        )
        figure.patch.set_edgecolor("white")
        figure.patch.set_linewidth(0.0)
        for axis in axes:
            axis.patch.set_edgecolor("white")
            axis.patch.set_linewidth(0.0)
        _plot_shape_panel(
            axes[0],
            data.d2,
            colour=BLUE,
            line_style="-",
            dimension_marker="o",
            title="(a) Physical d=2: disk contact",
            show_y_label=True,
        )
        _plot_shape_panel(
            axes[1],
            data.d3,
            colour=ORANGE,
            line_style="--",
            dimension_marker="s",
            title="(b) Physical d=3: sphere contact",
            show_y_label=False,
        )
        _plot_metric_panel(axes[2], data)
        axes[0].legend(
            loc="lower right",
            frameon=False,
            fontsize=5.9,
            handlelength=1.7,
            labelspacing=0.25,
        )
        figure.suptitle(
            "The same four-slab geometry retains three relative-prominence-qualified peaks",
            x=0.50,
            y=0.955,
            fontsize=8.5,
            fontweight="normal",
            color=INK,
        )
        figure.subplots_adjust(left=0.074, right=0.992, bottom=0.235, top=0.83)
        figure.text(
            0.5,
            0.075,
            "Exact free-exposure kernels • B=0 • result-informed • relative shape only",
            ha="center",
            va="bottom",
            fontsize=6.1,
            color="#40454C",
        )
        figure.text(
            0.5,
            0.035,
            (
                "continuum_verified=false • finite_B=false • independent_PDE=false • "
                "project=false • no event-mass observability claim"
            ),
            ha="center",
            va="bottom",
            fontsize=5.8,
            color="#565B63",
        )
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        png_path.parent.mkdir(parents=True, exist_ok=True)
        fixed_date = datetime(2026, 7, 13, tzinfo=timezone.utc)
        pdf_metadata = {
            "Title": "Physical d=2 and d=3 four-slab relative-shape comparison",
            "Author": "Encounter multimodality project",
            "Subject": "Result-informed B=0 relative-shape comparison",
            "Keywords": "encounter time, free exposure, physical dimension, relative shape",
            "Creator": "plot_d2_d3_four_patch.py",
            "CreationDate": fixed_date,
            "ModDate": fixed_date,
        }
        figure.savefig(
            pdf_path,
            format="pdf",
            dpi=300,
            facecolor="white",
            edgecolor="white",
            metadata=pdf_metadata,
        )
        figure.savefig(
            png_path,
            format="png",
            dpi=240,
            facecolor="white",
            edgecolor="white",
            metadata={"Software": "plot_d2_d3_four_patch.py"},
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


def _source_pin(
    dimension: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    file_map = {
        "d2": {
            "result": D2_RESULT,
            "manifest": D2_MANIFEST,
            "producer": D2_PRODUCER,
            "test": D2_TEST,
        },
        "d3": {
            "result": D3_RESULT,
            "manifest": D3_MANIFEST,
            "producer": D3_PRODUCER,
            "test": D3_TEST,
        },
    }
    pin: dict[str, Any] = {"claim_flags": dict(result["claim_flags"])}
    for label, path in file_map[dimension].items():
        pin[label] = str(path.relative_to(REPORT))
        pin[f"{label}_sha256"] = EXPECTED_HASHES[dimension][label]
    return pin


def _dimension_metadata(data: DimensionData) -> dict[str, Any]:
    return {
        "physical_dimension": data.physical_dimension,
        "time_grid": {
            "start": float(data.times[0]),
            "stop": float(data.times[-1]),
            "points": int(len(data.times)),
        },
        "selected_step": data.selected_step,
        "selected_weights": data.selected_weights.tolist(),
        "stationary_roots": list(data.roots),
        "normalizer_maximum_peak_density": data.normalizer,
        "peak_minimum_to_maximum_ratio": data.peak_ratio,
        "valley_to_smaller_adjacent_peak_ratios": list(data.valley_ratios),
    }


def build_metadata(
    data: FigureData,
    d2_result: dict[str, Any],
    _d2_manifest: dict[str, Any],
    d3_result: dict[str, Any],
    _d3_manifest: dict[str, Any],
    *,
    pdf_path: Path,
    png_path: Path,
    pdf_qa: dict[str, int],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "stage": "G1q_physical_d2_d3_four_slab_relative_shape_figure",
        "status": FIGURE_STATUS,
        "evidence_timing": EVIDENCE_TIMING,
        "claim_flags": dict(FIGURE_CLAIM_FLAGS),
        "chart_contract": dict(CHART_CONTRACT),
        "source_pins": {
            "d2": _source_pin("d2", d2_result),
            "d3": _source_pin("d3", d3_result),
        },
        "recomputation": {
            "d2": _dimension_metadata(data.d2),
            "d3": _dimension_metadata(data.d3),
            "shape_gates": {
                "peak_floor": 0.10,
                "valley_ceiling": 0.85,
                "d2_pass": data.d2.peak_ratio >= 0.10 and max(data.d2.valley_ratios) <= 0.85,
                "d3_pass": data.d3.peak_ratio >= 0.10 and max(data.d3.valley_ratios) <= 0.85,
                "d3_second_valley_margin": 0.85 - data.d3.valley_ratios[1],
            },
        },
        "render_policy": {
            "figure_inches": [7.2, 3.15],
            "figure_role": "double-column manuscript figure*",
            "pdf_fonttype": 42,
            "transparent_background": False,
            "font_family": "DejaVu Sans",
            "palette": {"d2": BLUE, "d3": ORANGE},
            "non_colour_distinction": CHART_CONTRACT["non_colour_distinction"],
        },
        "pdf_qa": pdf_qa,
        "outputs": {
            "pdf": str(pdf_path.relative_to(REPORT)),
            "pdf_sha256": d2_design.sha256(pdf_path),
            "png": str(png_path.relative_to(REPORT)),
            "png_sha256": d2_design.sha256(png_path),
        },
        "provenance": {
            "plot_script": str(HERE.relative_to(REPORT)),
            "plot_script_sha256": d2_design.sha256(HERE),
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "caption": (
            "Physical-dimension comparison of the frozen four-slab B=0 free-exposure "
            "shape. Panels (a) and (b) show the exact-kernel selected mixture, normalized "
            "by its largest refined peak, for physical d=2 disk contact and physical d=3 "
            "sphere contact on the common dimensionless-time interval 0.1 <= t <= 30; "
            "circles/squares mark "
            "maxima and open triangles mark minima. Each dimension uses its separately "
            "frozen selected conserved weights at the same physical parameters and slab "
            "geometry. Panel (c) compares the relative peak-balance and valley ratios with "
            "the frozen peak floor 0.10 and valley ceiling 0.85. Both dimensions pass these "
            "relative-shape gates, while d=3 has lower peak balance (0.6338 versus 0.8541) "
            "and its second valley is closer to the ceiling (0.8448; margin 0.0052). This "
            "is a result-informed, relative-shape-only B=0 comparison: "
            "continuum_verified=false, finite_B=false, independent_PDE=false, "
            "project=false, with no event-mass observability claim."
        ),
        "limitations": [
            "result-informed confirmation rather than preregistered discovery",
            "relative height and prominence only; no event-mass observability evidence",
            "floating-point exact-kernel quadrature rather than interval certification",
            "B=0 free exposure rather than a positive-B killed-Doi calculation",
            "no independent PDE solver and no passed project or publication gate",
        ],
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
    sources = preflight_sources()
    data = recompute_figure_data(*sources)
    render_figure(data, args.pdf, args.png)
    pdf_qa = verify_vector_pdf(args.pdf)
    metadata = build_metadata(
        data,
        *sources,
        pdf_path=args.pdf,
        png_path=args.png,
        pdf_qa=pdf_qa,
    )
    write_json(args.metadata, metadata)
    print(f"status={metadata['status']}")
    print(
        "metrics="
        f"d2=({data.d2.peak_ratio:.8f}, {data.d2.valley_ratios}), "
        f"d3=({data.d3.peak_ratio:.8f}, {data.d3.valley_ratios})"
    )
    print(f"pdf={args.pdf}")
    print(f"png={args.png}")
    print(f"metadata={args.metadata}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
