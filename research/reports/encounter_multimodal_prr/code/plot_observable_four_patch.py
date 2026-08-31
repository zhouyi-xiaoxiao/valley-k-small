#!/usr/bin/env python3
"""Render the pinned four-patch free-exposure relative-shape confirmation.

The figure recomputes exact continuum channel curves only after validating the
byte-pinned result, manifest, producer, protocol, and focused tests.  It shows
a relative-shape-qualified B=0 free-exposure topology.  It does not assert event-mass,
interval-level
continuum verification, positive-B killed-Doi persistence, or a project gate.
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

import continuum_observable_four_patch as design
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
RESULT = DATA / "continuum_observable_four_patch_result.json"
MANIFEST = DATA / "continuum_observable_four_patch_manifest.json"
PRODUCER = REPORT / "code" / "continuum_observable_four_patch.py"
PROTOCOL = REPORT / "notes" / "observable_four_patch_protocol.md"
SOURCE_TEST = REPORT / "code" / "test_continuum_observable_four_patch.py"
OUTPUT_PDF = FIGURES / "observable_four_patch.pdf"
OUTPUT_PNG = FIGURES / "observable_four_patch.png"
OUTPUT_METADATA = FIGURES / "observable_four_patch_metadata.json"

EXPECTED_RESULT_SHA256 = "4a929cdaf915a9b6180acc0c272a16ae77087d097f2d078b6483c6c9b320a9fc"
EXPECTED_MANIFEST_SHA256 = "1c79fcb31abbc622cee20e915d60f55337376d7555c1c25dab210b3cc5976a69"
EXPECTED_PRODUCER_SHA256 = "a553092f3d8bbf50fdf0124a3ea36ba32947c3b339cfcc0265a1cd7f6bc2d4da"
EXPECTED_PROTOCOL_SHA256 = "cbfb6fbe7b69fb66f3b25f7bcde404929a53cf1e8d2045c5fa037fe0fa8432a1"
EXPECTED_SOURCE_TEST_SHA256 = "c3a2c11c71daf9fcb04e1db9e7c4e489a515d7dfbbb51bc470d310d0c3f76243"

EVIDENCE_TIMING = "RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY"
RESULT_STATUS = "PASS_RESULT_INFORMED_OBSERVABLE_FREE_EXPOSURE_CONFIRMATION"
REQUIRED_CLAIM_FLAGS = {
    "continuum_verified": False,
    "finite_B_Doi_verified": False,
    "observable_free_exposure_confirmation_passed": True,
    "preregistered_discovery": False,
    "project_gate_passed": False,
}
PUBLICATION_SCOPE_FLAGS = {
    "relative_shape_gate_passed": True,
    "event_mass_observability_verified": False,
    "finite_B_Doi_verified": False,
    "independent_PDE_solver_verified": False,
    "continuum_verified": False,
    "project_gate_passed": False,
}

CHANNEL_COLOURS = ("#2F6B9A", "#C46A2B", "#7A8535", "#A85D7A")
CHANNEL_STYLES = ("-", "--", "-.", ":")
INK = "#22252A"
MID_GREY = "#777C84"
LIGHT_GREY = "#E3E6EA"
ORANGE = "#C46A2B"
BLUE = "#2F6B9A"
OLIVE = "#7A8535"


@dataclass(frozen=True)
class FigureData:
    times: np.ndarray
    channels: np.ndarray
    channel_derivatives: np.ndarray
    mixture: np.ndarray
    mixture_derivative: np.ndarray
    selected_weights: np.ndarray
    selected_step: float
    roots: tuple[dict[str, Any], ...]
    candidates: tuple[dict[str, Any], ...]
    cusp: dict[str, Any]
    recomputed_cusp: dict[str, Any]
    relative_shape: dict[str, Any]
    parameters: dict[str, Any]


def _require_hash(path: Path, expected: str, label: str) -> None:
    observed = design.sha256(path)
    if observed != expected:
        raise ValueError(f"pinned {label} hash mismatch: expected {expected}, observed {observed}")


def preflight_sources(
    *,
    result_path: Path = RESULT,
    manifest_path: Path = MANIFEST,
    producer_path: Path = PRODUCER,
    protocol_path: Path = PROTOCOL,
    source_test_path: Path = SOURCE_TEST,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fail closed unless every frozen source and claim flag matches."""

    for path, expected, label in (
        (result_path, EXPECTED_RESULT_SHA256, "result"),
        (manifest_path, EXPECTED_MANIFEST_SHA256, "manifest"),
        (producer_path, EXPECTED_PRODUCER_SHA256, "producer"),
        (protocol_path, EXPECTED_PROTOCOL_SHA256, "protocol"),
        (source_test_path, EXPECTED_SOURCE_TEST_SHA256, "source test"),
    ):
        _require_hash(path, expected, label)
    result = design.load_json(result_path)
    manifest = design.load_json(manifest_path)
    if result["status"] != RESULT_STATUS:
        raise ValueError("frozen four-patch result is not the declared PASS")
    if (
        result["evidence_timing"] != EVIDENCE_TIMING
        or manifest["evidence_timing"] != EVIDENCE_TIMING
    ):
        raise ValueError("result-informed evidence label was weakened")
    if result["claim_flags"] != REQUIRED_CLAIM_FLAGS:
        raise ValueError("four-patch claim flags do not match the bounded scope")
    if manifest["required_claim_flags"] != {
        "continuum_verified": False,
        "finite_B_Doi_verified": False,
        "project_gate_passed": False,
    }:
        raise ValueError("manifest negative claim flags were weakened")
    provenance = result["provenance"]
    expected_provenance = {
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "producer_sha256": EXPECTED_PRODUCER_SHA256,
        "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
        "test_sha256": EXPECTED_SOURCE_TEST_SHA256,
    }
    for key, expected in expected_provenance.items():
        if provenance.get(key) != expected:
            raise ValueError(f"result provenance mismatch for {key}")
    if result["stage"] != manifest["stage"]:
        raise ValueError("result and manifest stages disagree")
    if result["model"]["parameters"] != manifest["physical_model"]:
        raise ValueError("result and manifest physical parameters disagree")
    selected = result["inward_step_scan"]["selected"]
    if selected["step"] != 0.11 or selected["eligible"] is not True:
        raise ValueError("frozen selected candidate is not the declared step 0.11 PASS")
    structure = selected["stationary_structure"]
    if structure["topology"] != [
        "maximum",
        "minimum",
        "maximum",
        "minimum",
        "maximum",
    ]:
        raise ValueError("frozen selected topology is not max-min-max-min-max")
    if structure["worst_valley_ratio"] > manifest["inward_step_scan"]["maximum_valley_ratio"]:
        raise ValueError("selected candidate no longer passes the valley ceiling")
    if (
        structure["peak_minimum_to_maximum_ratio"]
        < manifest["inward_step_scan"]["minimum_peak_ratio"]
    ):
        raise ValueError("selected candidate no longer passes the peak floor")
    if not all(result["gates"].values()):
        raise ValueError("one or more frozen formal gates are false")
    return result, manifest


def _assert_close(
    observed: Any,
    expected: Any,
    label: str,
    *,
    atol: float,
) -> None:
    if not np.allclose(
        np.asarray(observed, dtype=float),
        np.asarray(expected, dtype=float),
        rtol=3.0e-11,
        atol=atol,
    ):
        raise RuntimeError(f"recomputed {label} disagrees with the frozen result")


def recompute_figure_data(
    result: dict[str, Any],
    manifest: dict[str, Any],
) -> FigureData:
    """Recompute continuum curves, cusp, roots, and relative-shape ratios."""

    design.require_repository_venv()
    selected = result["inward_step_scan"]["selected"]
    selected_weights = np.asarray(selected["weights"], dtype=float)
    roots = tuple(selected["stationary_structure"]["roots"])
    times = np.linspace(0.1, 30.0, 2401, dtype=float)
    fine_model = design.FourPatchContinuum(design.FINE)
    channels, derivatives = fine_model.real_channels_and_first_derivatives(times)
    mixture = channels @ selected_weights
    mixture_derivative = derivatives @ selected_weights
    if np.any(~np.isfinite(channels)) or np.any(channels < -2.0e-14):
        raise RuntimeError("recomputed channel curves are invalid")

    root_times = np.asarray([row["time"] for row in roots], dtype=float)
    root_channels, root_derivatives = fine_model.real_channels_and_first_derivatives(root_times)
    root_density = root_channels @ selected_weights
    root_d1 = root_derivatives @ selected_weights
    frozen_density = np.asarray([row["density"] for row in roots], dtype=float)
    _assert_close(root_density, frozen_density, "root densities", atol=5.0e-12)
    if float(np.max(np.abs(root_d1))) > 2.0e-13:
        raise RuntimeError("recomputed selected roots have excessive derivative residual")

    peak_density = root_density[[0, 2, 4]]
    valley_density = root_density[[1, 3]]
    peak_ratio = float(np.min(peak_density) / np.max(peak_density))
    valley_ratios = np.asarray(
        (
            valley_density[0] / min(peak_density[0], peak_density[1]),
            valley_density[1] / min(peak_density[1], peak_density[2]),
        )
    )
    frozen_structure = selected["stationary_structure"]
    _assert_close(
        peak_ratio,
        frozen_structure["peak_minimum_to_maximum_ratio"],
        "peak ratio",
        atol=2.0e-12,
    )
    _assert_close(
        valley_ratios,
        frozen_structure["valley_to_smaller_adjacent_peak_ratios"],
        "valley ratios",
        atol=2.0e-12,
    )

    bracket = tuple(float(value) for value in manifest["cusp_confirmation"]["determinant_bracket"])
    recomputed_cusp, _diagnostics = design.locate_cusp(
        design.FourPatchContinuum(design.PRIMARY),
        bracket,
    )
    frozen_cusp = result["cusp"]
    _assert_close(recomputed_cusp["time"], frozen_cusp["time"], "cusp time", atol=4.0e-11)
    _assert_close(
        recomputed_cusp["weights"],
        frozen_cusp["weights"],
        "cusp weights",
        atol=4.0e-11,
    )
    _assert_close(
        recomputed_cusp["scaled_fourth_derivative"],
        frozen_cusp["scaled_fourth_derivative"],
        "scaled fourth derivative",
        atol=3.0e-8,
    )

    return FigureData(
        times=times,
        channels=channels,
        channel_derivatives=derivatives,
        mixture=mixture,
        mixture_derivative=mixture_derivative,
        selected_weights=selected_weights,
        selected_step=float(selected["step"]),
        roots=roots,
        candidates=tuple(result["inward_step_scan"]["candidates"]),
        cusp=frozen_cusp,
        recomputed_cusp=recomputed_cusp,
        relative_shape={
            "peak_minimum_to_maximum_ratio": peak_ratio,
            "valley_to_smaller_adjacent_peak_ratios": valley_ratios.tolist(),
            "maximum_valley_ratio": float(np.max(valley_ratios)),
            "minimum_weight": float(np.min(selected_weights)),
        },
        parameters=dict(result["model"]["parameters"]),
    )


def _panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.085,
        1.04,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=10.0,
        fontweight="bold",
        color=INK,
    )


def _plot_layout(ax: plt.Axes, data: FigureData) -> None:
    pars = data.parameters
    centres = np.asarray(pars["patch_centres"], dtype=float)
    half_width = float(pars["patch_half_width"])
    ax.set_xlim(0.08, 1.02)
    ax.set_ylim(0.0, 1.0)
    ax.add_patch(
        Rectangle(
            (0.10, 0.21),
            0.88,
            0.53,
            facecolor="#F4F5F6",
            edgecolor="#777C84",
            linewidth=0.8,
        )
    )
    for index, (centre, colour, weight) in enumerate(
        zip(centres, CHANNEL_COLOURS, data.selected_weights, strict=True)
    ):
        ax.add_patch(
            Rectangle(
                (centre - half_width, 0.21),
                2.0 * half_width,
                0.53,
                facecolor=colour,
                edgecolor=INK,
                linewidth=0.55,
            )
        )
        ax.text(
            centre,
            0.79,
            f"$w_{index}={weight:.3f}$",
            ha="center",
            va="bottom",
            fontsize=7.2,
            color=colour,
        )
        ax.text(
            centre,
            0.16,
            f"{centre:.2f}",
            ha="center",
            va="top",
            fontsize=7.0,
            color=INK,
        )
    start = float(pars["midpoint_start"])
    initial_half_width = float(pars["initial_half_width"])
    ax.add_patch(
        Rectangle(
            (start - initial_half_width, 0.36),
            2.0 * initial_half_width,
            0.23,
            facecolor="#525860",
            edgecolor="#22252A",
            linewidth=0.6,
        )
    )
    ax.text(start, 0.31, "$z_0=0.14$", ha="center", va="top", fontsize=7.0)
    mean = float(pars["ou_mean"])
    ax.axvline(mean, ymin=0.20, ymax=0.76, color=MID_GREY, linewidth=0.8, linestyle="--")
    ax.text(mean + 0.006, 0.68, "$\\bar z=0.95$", ha="left", va="center", fontsize=7.0)
    ax.add_patch(
        FancyArrowPatch(
            (start + 0.018, 0.48),
            (mean - 0.02, 0.48),
            arrowstyle="-|>",
            mutation_scale=9,
            linewidth=0.8,
            color=MID_GREY,
        )
    )
    ax.annotate(
        "",
        xy=(0.095, 0.72),
        xytext=(0.095, 0.23),
        arrowprops={"arrowstyle": "<->", "color": MID_GREY, "linewidth": 0.7},
    )
    ax.text(0.083, 0.48, "$\\mathbb{T}_1$", ha="right", va="center", fontsize=7.2)
    ax.text(
        0.17,
        0.68,
        (
            "$\\sum_j w_j=1$\n"
            "$w_0$ fixed at 0.28\n"
            f"$\\sigma={half_width:.3f}$;  $a={pars['contact_radius']:.2f}$"
        ),
        ha="left",
        va="top",
        fontsize=6.5,
        color="#33363B",
    )
    ax.set_xlabel("longitudinal midpoint $z$", labelpad=8.0)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Four narrow catalyst slabs and the selected conserved allocation", loc="left")
    _panel_label(ax, "(a)")


def _plot_channels(ax: plt.Axes, data: FigureData) -> None:
    centres = data.parameters["patch_centres"]
    for index, (colour, style, centre) in enumerate(
        zip(CHANNEL_COLOURS, CHANNEL_STYLES, centres, strict=True)
    ):
        ax.plot(
            data.times,
            data.channels[:, index],
            color=colour,
            linestyle=style,
            linewidth=1.35,
            label=f"$g_{index}(t)$, $z_{index}={centre:.2f}$",
        )
    ax.plot(
        data.times,
        data.mixture,
        color=INK,
        linewidth=2.1,
        label="$G_{w_*}(t)$ (zoom below)",
        zorder=5,
    )
    ax.set_xlim(0.1, 30.0)
    ax.set_ylim(0.0, 0.84)
    ax.set_ylabel("free-exposure response / unit budget")
    ax.tick_params(labelbottom=False)
    ax.set_title("Free-exposure channels and selected mixture", loc="left")
    ax.legend(
        loc="upper right",
        frameon=False,
        fontsize=6.5,
        ncol=2,
        handlelength=2.7,
        columnspacing=0.9,
    )
    _panel_label(ax, "(b)")


def _plot_mixture(ax: plt.Axes, data: FigureData) -> None:
    ax.plot(data.times, data.mixture, color=INK, linewidth=2.0)
    labels = ("$P_1$", "$V_1$", "$P_2$", "$V_2$", "$P_3$")
    for label, row in zip(labels, data.roots, strict=True):
        time = float(row["time"])
        density = float(row["density"])
        maximum = row["topology"] == "maximum"
        ax.axvline(time, color=LIGHT_GREY, linewidth=0.65, linestyle=":")
        ax.plot(
            time,
            density,
            marker="o",
            markersize=4.6,
            markerfacecolor=ORANGE if maximum else "white",
            markeredgecolor=ORANGE if maximum else BLUE,
            markeredgewidth=1.0,
            zorder=5,
        )
        ax.annotate(
            label,
            xy=(time, density),
            xytext=(0, 7 if maximum else -12),
            textcoords="offset points",
            ha="center",
            va="bottom" if maximum else "top",
            fontsize=7.0,
            color=ORANGE if maximum else BLUE,
        )
    valley = data.relative_shape["valley_to_smaller_adjacent_peak_ratios"]
    text = (
        f"peak balance = {data.relative_shape['peak_minimum_to_maximum_ratio']:.3f}\n"
        f"$V_1/\\min(P_1,P_2)={valley[0]:.3f}$\n"
        f"$V_2/\\min(P_2,P_3)={valley[1]:.3f}\\leq0.85$"
    )
    ax.text(
        0.985,
        0.055,
        text,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.9,
        color="#33363B",
        bbox={"facecolor": "white", "edgecolor": "#D6D9DD", "linewidth": 0.55},
    )
    ax.set_xlim(0.1, 30.0)
    ax.set_ylim(0.0, 0.27)
    ax.set_xlabel("dimensionless time $t$")
    ax.set_ylabel("selected $G_{w_*}(t)$")


def _candidate_arrays(data: FigureData) -> dict[str, np.ndarray]:
    steps = np.asarray([row["step"] for row in data.candidates], dtype=float)
    eligible = np.asarray([row["eligible"] for row in data.candidates], dtype=bool)
    structures = [row["stationary_structure"] for row in data.candidates]
    return {
        "steps": steps,
        "eligible": eligible,
        "worst_valley": np.asarray([row["worst_valley_ratio"] for row in structures], dtype=float),
        "peak_balance": np.asarray(
            [row["peak_minimum_to_maximum_ratio"] for row in structures],
            dtype=float,
        ),
        "minimum_weight": np.asarray([row["minimum_weight"] for row in structures], dtype=float),
    }


def _plot_candidate_metrics(ax: plt.Axes, data: FigureData) -> None:
    values = _candidate_arrays(data)
    steps = values["steps"]
    eligible = values["eligible"]
    ax.plot(
        steps,
        values["worst_valley"],
        color=BLUE,
        linewidth=1.55,
        marker="o",
        markersize=3.0,
        label="worst valley ratio (lower is better)",
    )
    ax.plot(
        steps,
        values["peak_balance"],
        color=OLIVE,
        linewidth=1.3,
        linestyle="--",
        marker="s",
        markersize=2.8,
        label="peak balance (higher is better)",
    )
    ax.axhline(0.85, color=MID_GREY, linewidth=0.9, linestyle=":", label="valley ceiling 0.85")
    ax.scatter(
        steps[~eligible],
        values["worst_valley"][~eligible],
        s=22,
        facecolors="white",
        edgecolors=BLUE,
        linewidths=0.8,
        zorder=5,
    )
    ax.scatter(
        steps[eligible],
        values["worst_valley"][eligible],
        s=22,
        facecolors=ORANGE,
        edgecolors=ORANGE,
        linewidths=0.8,
        zorder=5,
    )
    selected_index = int(np.flatnonzero(np.isclose(steps, data.selected_step))[0])
    ax.plot(
        data.selected_step,
        values["worst_valley"][selected_index],
        marker="D",
        markersize=6.0,
        markerfacecolor=INK,
        markeredgecolor="white",
        markeredgewidth=0.7,
        zorder=7,
    )
    ax.annotate(
        "selected $s_*=0.11$\nfirst eligible step",
        xy=(data.selected_step, values["worst_valley"][selected_index]),
        xytext=(0.135, 0.94),
        arrowprops={"arrowstyle": "-", "color": "#555A62", "linewidth": 0.7},
        fontsize=6.8,
        color="#33363B",
        ha="left",
        va="center",
    )
    ax.set_xlim(0.015, 0.205)
    ax.set_ylim(0.62, 1.015)
    ax.set_ylabel("relative-shape ratio")
    ax.tick_params(labelbottom=False)
    ax.set_title("  Frozen inward-step scan", loc="left")
    ax.legend(loc="lower left", frameon=False, fontsize=6.2, handlelength=2.2)
    _panel_label(ax, "(c)")


def _plot_candidate_weight(ax: plt.Axes, data: FigureData) -> None:
    values = _candidate_arrays(data)
    steps = values["steps"]
    eligible = values["eligible"]
    ax.plot(
        steps,
        values["minimum_weight"],
        color=INK,
        linewidth=1.35,
        marker="o",
        markersize=3.0,
    )
    ax.scatter(
        steps[eligible],
        values["minimum_weight"][eligible],
        s=20,
        facecolors=ORANGE,
        edgecolors=ORANGE,
        linewidths=0.7,
        zorder=5,
    )
    selected_index = int(np.flatnonzero(np.isclose(steps, data.selected_step))[0])
    ax.plot(
        data.selected_step,
        values["minimum_weight"][selected_index],
        marker="D",
        markersize=5.8,
        markerfacecolor=INK,
        markeredgecolor="white",
        markeredgewidth=0.7,
        zorder=7,
    )
    ax.text(
        0.98,
        0.90,
        "priority 1: maximize\nminimum catalyst weight",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.7,
        color="#33363B",
    )
    ax.set_xlim(0.015, 0.205)
    ax.set_ylim(0.0, 0.205)
    ax.set_xlabel("inward normal step $s$")
    ax.set_ylabel("$\\min_j w_j$")


def render_figure(data: FigureData, pdf_path: Path, png_path: Path) -> None:
    """Render deterministic vector and preview outputs."""

    rc = {
        "font.family": "DejaVu Sans",
        "font.size": 8.0,
        "axes.titlesize": 9.0,
        "axes.titleweight": "normal",
        "axes.labelsize": 7.6,
        "axes.edgecolor": "#4E535A",
        "axes.linewidth": 0.75,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": LIGHT_GREY,
        "grid.linewidth": 0.55,
        "grid.alpha": 1.0,
        "xtick.labelsize": 6.8,
        "ytick.labelsize": 6.8,
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
        figure = plt.figure(figsize=(7.2, 6.15))
        outer = figure.add_gridspec(
            2,
            2,
            height_ratios=(0.82, 2.72),
            width_ratios=(1.44, 1.0),
            hspace=0.30,
            wspace=0.27,
        )
        panel_a = figure.add_subplot(outer[0, :])
        left = outer[1, 0].subgridspec(2, 1, height_ratios=(1.08, 1.0), hspace=0.08)
        right = outer[1, 1].subgridspec(2, 1, height_ratios=(1.34, 0.72), hspace=0.12)
        panel_b_channels = figure.add_subplot(left[0, 0])
        panel_b_mixture = figure.add_subplot(left[1, 0], sharex=panel_b_channels)
        panel_c_metrics = figure.add_subplot(right[0, 0])
        panel_c_weight = figure.add_subplot(right[1, 0], sharex=panel_c_metrics)
        figure.patch.set_edgecolor("white")
        figure.patch.set_linewidth(0.0)
        for panel in (
            panel_a,
            panel_b_channels,
            panel_b_mixture,
            panel_c_metrics,
            panel_c_weight,
        ):
            panel.patch.set_edgecolor("white")
            panel.patch.set_linewidth(0.0)
        _plot_layout(panel_a, data)
        _plot_channels(panel_b_channels, data)
        _plot_mixture(panel_b_mixture, data)
        _plot_candidate_metrics(panel_c_metrics, data)
        _plot_candidate_weight(panel_c_weight, data)
        figure.subplots_adjust(left=0.085, right=0.985, bottom=0.095, top=0.955)
        figure.text(
            0.5,
            0.018,
            (
                "Result-informed B=0 direct-continuum calculation: relative-shape gate PASS; "
                "no event-mass claim; continuum_verified = finite-B = project gate = false."
            ),
            ha="center",
            va="bottom",
            fontsize=6.5,
            color="#444950",
        )
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        png_path.parent.mkdir(parents=True, exist_ok=True)
        fixed_date = datetime(2026, 7, 13, tzinfo=timezone.utc)
        pdf_metadata = {
            "Title": "Four-patch free-exposure relative-shape confirmation",
            "Author": "Encounter multimodality project",
            "Subject": "Result-informed direct-continuum B=0 confirmation",
            "Keywords": "encounter time, free exposure, four patches, relative shape",
            "Creator": "plot_observable_four_patch.py",
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
            metadata={"Software": "plot_observable_four_patch.py"},
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
    return {
        "schema_version": 1,
        "stage": "G1o_observable_four_patch_figure",
        "status": "PASS_RESULT_INFORMED_FREE_EXPOSURE_RELATIVE_SHAPE_FIGURE",
        "evidence_timing": EVIDENCE_TIMING,
        "claim_flags": dict(REQUIRED_CLAIM_FLAGS),
        "publication_scope_flags": dict(PUBLICATION_SCOPE_FLAGS),
        "source_pins": {
            "result": str(RESULT.relative_to(REPORT)),
            "result_sha256": EXPECTED_RESULT_SHA256,
            "manifest": str(MANIFEST.relative_to(REPORT)),
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "producer": str(PRODUCER.relative_to(REPORT)),
            "producer_sha256": EXPECTED_PRODUCER_SHA256,
            "protocol": str(PROTOCOL.relative_to(REPORT)),
            "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
            "source_test": str(SOURCE_TEST.relative_to(REPORT)),
            "source_test_sha256": EXPECTED_SOURCE_TEST_SHA256,
        },
        "recomputation": {
            "configuration": "fine curves plus primary cusp",
            "time_grid": {
                "start": float(data.times[0]),
                "stop": float(data.times[-1]),
                "points": int(len(data.times)),
            },
            "cusp_time": data.recomputed_cusp["time"],
            "cusp_weights": data.recomputed_cusp["weights"],
            "selected_step": data.selected_step,
            "selected_weights": data.selected_weights.tolist(),
            "stationary_roots": list(data.roots),
            "peak_minimum_to_maximum_ratio": data.relative_shape["peak_minimum_to_maximum_ratio"],
            "valley_to_smaller_adjacent_peak_ratios": data.relative_shape[
                "valley_to_smaller_adjacent_peak_ratios"
            ],
            "maximum_valley_ratio": data.relative_shape["maximum_valley_ratio"],
            "minimum_weight": data.relative_shape["minimum_weight"],
        },
        "chart_contract": {
            "analytical_question": (
                "How does the frozen four-slab conserved allocation produce a "
                "relative-shape-qualified three-maximum free-exposure curve, and why did "
                "the frozen rule select "
                "inward step 0.11?"
            ),
            "takeaway": (
                "The selected allocation combines four separated continuum exposure clocks "
                "into three resolved maxima and two valleys; both valley ratios pass the "
                "0.85 ceiling, and 0.11 is the eligible step with the largest minimum weight."
            ),
            "panels": {
                "a": "physical slab layout, initial midpoint, OU mean, and conserved weights",
                "b": "four continuum channels and selected mixture with five refined roots",
                "c": "frozen inward-step relative-shape scan and minimum-weight priority",
            },
            "palette_policy": (
                "four restrained category roots for the four physical channels; line style, "
                "marker fill, and direct labels provide non-colour distinctions"
            ),
            "renderer": "Matplotlib static vector PDF and PNG preview",
        },
        "render_policy": {
            "figure_inches": [7.2, 6.15],
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
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "limitations": list(result["limitations"]),
        "caption": (
            "Four-patch direct-continuum free-exposure relative-shape confirmation. "
            "(a) Four narrow catalyst slabs on the longitudinal midpoint coordinate, "
            "with the selected conserved weights. (b) The four exact B=0 exposure "
            "channels and their selected G mixture on dimensionless time, whose refined "
            "stationary points have "
            "max-min-max-min-max topology. The peak balance is 0.8541 and the valley "
            "ratios are 0.6668 and 0.8375. (c) The frozen inward-step scan: step 0.11 is "
            "the first eligible candidate and therefore maximizes the minimum catalyst "
            "weight under the predeclared priority. This result-informed floating-point "
            "confirmation passes the declared free-exposure relative-shape gate but is "
            "not evidence of event-mass observability and is "
            "not interval-level continuum verification, finite-B killed-Doi evidence, "
            "or a passed project gate."
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
    print(
        "relative_shape="
        f"peak_ratio={metadata['recomputation']['peak_minimum_to_maximum_ratio']:.8f}, "
        f"valleys={metadata['recomputation']['valley_to_smaller_adjacent_peak_ratios']}"
    )
    print(f"pdf={args.pdf}")
    print(f"png={args.png}")
    print(f"metadata={args.metadata}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
