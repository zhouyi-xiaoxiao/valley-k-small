#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Polygon, Rectangle


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "packages" / "vkcore" / "src"
GATING_REPORT_CODE = REPO_ROOT / "research" / "reports" / "grid2d_one_two_target_gating" / "code"
EXIT_TIMING_CODE = REPO_ROOT / "research" / "reports" / "grid2d_one_target_exit_timing" / "code"
REPORT_ROOT = Path(__file__).resolve().parents[1]
FIG_ROOT = REPORT_ROOT / "artifacts" / "figures"
DATA_ROOT = REPORT_ROOT / "artifacts" / "data"
EXIT_TIMING_FIG_ROOT = REPO_ROOT / "research" / "reports" / "grid2d_one_target_exit_timing" / "artifacts" / "figures"

for path in (SRC_ROOT, GATING_REPORT_CODE, EXIT_TIMING_CODE):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

import build_exit_timing_report as base
from vkcore.grid2d.one_two_target_gating import (
    compute_one_target_first_event_statistics,
    compute_one_target_window_path_statistics,
)
from vkcore.grid2d.rect_bimodality.cli import smooth_series_display


REPORT_ID = "grid2d_one_target_valley_peak_budget"
REPRESENTATIVE_KAPPAS = [0.0, 0.0040, 0.0152]
OVERVIEW_CURVE_KAPPAS = [0.0, 0.0040]
OVERVIEW_WINDOWS = ["peak1", "valley", "peak2"]
COMPARE_WINDOWS = ["peak1", "valley", "peak2"]
KAPPA_COLORS = {
    0.0: "#424242",
    0.0040: "#ef6c00",
    0.0152: "#1f78b4",
}
KAPPA_LABELS = {
    0.0: r"$\kappa=0$",
    0.0040: r"$\kappa=0.0040$",
    0.0152: r"$\kappa=0.0152$ boundary",
}
WINDOW_LABELS = {
    "peak1": "Peak 1",
    "valley": "Valley",
    "peak2": "Peak 2",
}
DISPLAY_SMOOTH_WINDOW = 3
REGION_GROUPS = [
    ("Left side", "left_side_share", ("left_core", "left_shoulders", "left_outer"), "#d94801"),
    ("Corridor", "corridor_share", ("corridor",), "#8d8d8d"),
    ("Outside reservoir", "outer_reservoir_share", ("outer_reservoir",), "#1b9e77"),
    ("Target funnel", "target_funnel_share", ("target_funnel",), "#386cb0"),
]
DISPLAY_REGION_GROUPS = [
    ("Left side", "left_side_share", "#d94801"),
    ("Corridor", "corridor_share", "#8d8d8d"),
    ("Outer/right side", "right_outside_share", "#1b9e77"),
]

SUMMARY_CSV = DATA_ROOT / "window_budget_summary.csv"
FIG1_PNG = FIG_ROOT / "fig1_geometry_curve_budget.png"
FIG1_PDF = FIG_ROOT / "fig1_geometry_curve_budget.pdf"
FIG2_PNG = FIG_ROOT / "fig2_tau_out_budget.png"
FIG2_PDF = FIG_ROOT / "fig2_tau_out_budget.pdf"
FIG3_PNG = FIG_ROOT / "fig3_tau_mem_budget.png"
FIG3_PDF = FIG_ROOT / "fig3_tau_mem_budget.pdf"
FIG1_RIGHT_PDF = FIG_ROOT / "fig1_curve_budget_panel.pdf"
FIG1_LEFT_PDF = FIG_ROOT / "fig1_partition_schematic.pdf"
PARTITION_PNG = EXIT_TIMING_FIG_ROOT / "one_target_partition.png"
PARTITION_PDF = EXIT_TIMING_FIG_ROOT / "one_target_partition.pdf"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def fmt_kappa(kappa: float) -> str:
    return f"{kappa:.4f}"


def _window_bounds(windows: list[tuple[str, int, int]]) -> dict[str, tuple[int, int]]:
    return {str(name): (int(lo), int(hi)) for name, lo, hi in windows}


def _group_shares(case: dict[str, Any], occupancy: np.ndarray) -> dict[str, float]:
    masks = base.region_masks(case)
    shares: dict[str, float] = {}
    for label, _key, regions, _color in REGION_GROUPS:
        shares[label] = float(sum(float(np.sum(occupancy[masks[region]])) for region in regions))
    shares["Outer/right side"] = shares["Outside reservoir"] + shares["Target funnel"]
    shares["Outside share"] = 1.0 - shares["Corridor"]
    return shares


def _ratio_and_post_share(stats_map: dict[str, Any], window_name: str) -> tuple[float, float, float]:
    stat = stats_map[window_name]
    event_prob = float(stat["event_probability"])
    ratio = float("nan")
    if event_prob > 0.0:
        mean_event = float(stat["mean_event_time_given_event"])
        mean_hit = float(stat["mean_hit_time_in_window"])
        if np.isfinite(mean_event) and np.isfinite(mean_hit) and mean_hit > 0.0:
            ratio = mean_event / mean_hit
    post_share = float("nan")
    if np.isfinite(ratio):
        post_share = event_prob * (1.0 - ratio)
    return event_prob, ratio, post_share


def build_summary_rows() -> tuple[list[dict[str, Any]], dict[float, dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    bundles: dict[float, dict[str, Any]] = {}

    for kappa in REPRESENTATIVE_KAPPAS:
        case = base.build_case(kappa)
        windows = base.window_ranges(case["res"].t_peak1, case["res"].t_valley, case["res"].t_peak2, len(case["f_total"]))
        occupancy_stats = compute_one_target_window_path_statistics(
            case,
            Lx=int(case["Lx"]),
            windows=windows,
        )
        tau_out_stats = compute_one_target_first_event_statistics(
            case,
            Lx=int(case["Lx"]),
            windows=windows,
            event_state_mask=base._event_state_mask_outside(case),
        )
        tau_mem_stats = compute_one_target_first_event_statistics(
            case,
            Lx=int(case["Lx"]),
            windows=windows,
            event_edge_pairs=base._event_edge_pairs_membrane(case),
        )

        bundles[float(kappa)] = {
            "case": case,
            "windows": windows,
            "window_bounds": _window_bounds(windows),
            "occupancy_stats": occupancy_stats,
            "tau_out": tau_out_stats,
            "tau_mem": tau_mem_stats,
        }

        for window_name, lo, hi in windows:
            occupancy = np.asarray(occupancy_stats[window_name]["occupancy"], dtype=np.float64)
            grouped = _group_shares(case, occupancy)
            out_prob, out_ratio, out_post = _ratio_and_post_share(tau_out_stats, window_name)
            mem_prob, mem_ratio, mem_post = _ratio_and_post_share(tau_mem_stats, window_name)
            mean_hit_time = float(tau_out_stats[window_name]["mean_hit_time_in_window"])
            rows.append(
                {
                    "kappa": float(kappa),
                    "window": str(window_name),
                    "window_lo": int(lo),
                    "window_hi": int(hi),
                    "window_width": int(hi) - int(lo) + 1,
                    "phase": int(case["res"].phase),
                    "sep_peaks": float(case["res"].sep_peaks),
                    "mean_hit_time": mean_hit_time,
                    "corridor_share": grouped["Corridor"],
                    "outside_share": grouped["Outside share"],
                    "left_side_share": grouped["Left side"],
                    "outer_reservoir_share": grouped["Outside reservoir"],
                    "target_funnel_share": grouped["Target funnel"],
                    "right_outside_share": grouped["Outer/right side"],
                    "outside_steps": grouped["Outside share"] * mean_hit_time,
                    "tau_out_prob": out_prob,
                    "tau_out_ratio": out_ratio,
                    "tau_out_post_share": out_post,
                    "tau_mem_prob": mem_prob,
                    "tau_mem_ratio": mem_ratio,
                    "tau_mem_post_share": mem_post,
                    "tau_mem_post_steps": (float("nan") if not np.isfinite(mem_post) else mem_post * mean_hit_time),
                }
            )
    return rows, bundles


def write_summary_csv(rows: list[dict[str, Any]]) -> None:
    ensure_dir(DATA_ROOT)
    fieldnames = [
        "kappa",
        "window",
        "window_lo",
        "window_hi",
        "window_width",
        "phase",
        "sep_peaks",
        "mean_hit_time",
        "corridor_share",
        "outside_share",
        "left_side_share",
        "outer_reservoir_share",
        "target_funnel_share",
        "right_outside_share",
        "outside_steps",
        "tau_out_prob",
        "tau_out_ratio",
        "tau_out_post_share",
        "tau_mem_prob",
        "tau_mem_ratio",
        "tau_mem_post_share",
        "tau_mem_post_steps",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _rows_lookup(rows: list[dict[str, Any]]) -> dict[tuple[float, str], dict[str, Any]]:
    return {(float(row["kappa"]), str(row["window"])): row for row in rows}


def _relative_path(from_dir: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, start=from_dir)


def _plot_partition_schematic(case: dict[str, Any]) -> None:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    _y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    start_x, start_y = map(int, case["start"])
    target_x, target_y = map(int, case["target"])

    fig, ax = plt.subplots(figsize=(5.2, 2.8))

    left_color = DISPLAY_REGION_GROUPS[0][2]
    corridor_color = DISPLAY_REGION_GROUPS[1][2]
    outer_color = DISPLAY_REGION_GROUPS[2][2]
    target_color = "#386cb0"

    # Draw all regions in cell-boundary coordinates so lattice points stay centered in cells.
    ax.add_patch(Rectangle((-0.5, -0.5), x0, wy, facecolor=left_color, alpha=0.86, edgecolor="none"))
    ax.add_patch(
        Rectangle(
            (x0 - 0.5, y_low - 0.5),
            x1 - x0 + 1,
            y_high - y_low + 1,
            facecolor=corridor_color,
            alpha=0.86,
            edgecolor="none",
        )
    )
    ax.add_patch(Rectangle((x0 - 0.5, -0.5), x1 - x0 + 1, y_low, facecolor=outer_color, alpha=0.86, edgecolor="none"))
    ax.add_patch(
        Rectangle(
            (x0 - 0.5, y_high + 0.5),
            x1 - x0 + 1,
            wy - (y_high + 1),
            facecolor=outer_color,
            alpha=0.86,
            edgecolor="none",
        )
    )
    ax.add_patch(Rectangle((x1 + 0.5, -0.5), lx - (x1 + 1), wy, facecolor=outer_color, alpha=0.86, edgecolor="none"))
    ax.add_patch(Rectangle((x1 + 0.5, -0.5), lx - (x1 + 1), wy, facecolor=target_color, alpha=0.16, edgecolor="none"))
    ax.add_patch(
        Rectangle(
            (x1 + 0.5, -0.5),
            lx - (x1 + 1),
            wy,
            fill=False,
            edgecolor=target_color,
            linewidth=1.0,
            linestyle=(0, (4, 2)),
        )
    )

    ax.hlines([y_low - 0.5, y_high + 0.5], x0 - 0.5, x1 + 0.5, colors="#404040", linewidth=1.0, linestyles=(0, (6, 4)))
    ax.hlines(start_y, 0, lx, colors="#ffffff", linewidth=0.7, linestyles=(0, (2, 2)), alpha=0.85, zorder=4)

    ax.add_patch(
        Rectangle(
            (start_x - 0.5, start_y - 0.5),
            1.0,
            1.0,
            facecolor="#c62828",
            edgecolor="white",
            linewidth=0.9,
            zorder=6,
        )
    )
    ax.add_patch(
        Polygon(
            [
                (target_x, target_y + 0.5),
                (target_x + 0.5, target_y),
                (target_x, target_y - 0.5),
                (target_x - 0.5, target_y),
            ],
            closed=True,
            facecolor="white",
            edgecolor=target_color,
            linewidth=1.2,
            zorder=6,
        )
    )

    label_box = dict(facecolor="white", edgecolor="none", alpha=0.9, pad=0.25)
    ax.annotate(
        "Left side",
        xy=(x0 * 0.42, start_y + 0.15),
        xytext=(3.2, wy - 1.1),
        fontsize=8.8,
        color="#333333",
        ha="left",
        va="center",
        bbox=label_box,
        arrowprops=dict(arrowstyle="-", color=left_color, lw=1.0),
    )
    ax.text((x0 + x1) / 2.0, (y_low + y_high + 1) / 2.0, "Corridor", ha="center", va="center", fontsize=9.8, color="#333333", bbox=label_box)
    ax.text((x0 + x1) / 2.0, y_high + 2.2, "Outer/right side", ha="center", va="center", fontsize=8.8, color="#333333", bbox=label_box)
    ax.annotate(
        "Start",
        xy=(start_x, start_y),
        xytext=(start_x + 4.2, start_y + 1.55),
        fontsize=8.5,
        color="#c62828",
        ha="center",
        va="center",
        bbox=label_box,
        arrowprops=dict(arrowstyle="-|>", color="#c62828", lw=1.0),
    )
    ax.annotate(
        "Target",
        xy=(target_x, target_y),
        xytext=(target_x - 4.2, target_y + 3.3),
        fontsize=8.5,
        color=target_color,
        ha="center",
        va="center",
        bbox=label_box,
        arrowprops=dict(arrowstyle="-|>", color=target_color, lw=1.0),
    )

    ax.set_xlim(-0.5, lx - 0.5)
    ax.set_ylim(-0.5, wy - 0.5)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticks(np.arange(-0.5, lx, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, wy, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.32, alpha=0.72)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_linewidth(0.9)
        spine.set_color("#444444")

    fig.tight_layout(pad=0.2)
    ensure_dir(FIG_ROOT)
    fig.savefig(FIG1_LEFT_PDF, bbox_inches="tight")
    plt.close(fig)


def _compose_overview_vector_pdf() -> None:
    build_dir = FIG_ROOT / "_fig1_vector_build"
    ensure_dir(build_dir)
    tex_path = build_dir / "fig1_geometry_curve_budget.tex"
    pdf_name = "fig1_geometry_curve_budget.pdf"
    left_rel = _relative_path(build_dir, FIG1_LEFT_PDF)
    right_rel = _relative_path(build_dir, FIG1_RIGHT_PDF)
    tex_path.write_text(
        "\n".join(
            [
                r"\documentclass{article}",
                r"\usepackage[paperwidth=10.4in,paperheight=8.0in,margin=0.12in]{geometry}",
                r"\usepackage{graphicx}",
                r"\pagestyle{empty}",
                r"\begin{document}",
                r"\centering",
                r"\begin{minipage}[c]{0.96\linewidth}",
                r"\centering",
                rf"\includegraphics[width=0.72\linewidth]{{{left_rel}}}",
                r"\end{minipage}",
                r"\vspace{0.45em}",
                r"",
                r"\begin{minipage}[c]{0.96\linewidth}",
                r"\centering",
                rf"\includegraphics[width=\linewidth]{{{right_rel}}}",
                r"\end{minipage}",
                r"\end{document}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    subprocess.run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={build_dir}",
            tex_path.name,
        ],
        check=True,
        cwd=build_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    built_pdf = build_dir / pdf_name
    FIG1_PDF.write_bytes(built_pdf.read_bytes())
    try:
        subprocess.run(
            ["sips", "-s", "format", "png", str(FIG1_PDF), "--out", str(FIG1_PNG)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"Warning: failed to render preview PNG for {FIG1_PDF}: {exc.stdout}")


def _draw_window_budget_row(
    ax: plt.Axes,
    *,
    kappa: float,
    lookup: dict[tuple[float, str], dict[str, Any]],
    bounds: dict[str, tuple[int, int]],
    windows: list[str],
    y0: float,
    row_h: float,
    x_shift: float = 0.0,
    outline_color: str = "#333333",
) -> None:
    trans = ax.get_xaxis_transform()
    for window_name in windows:
        lo, hi = bounds[window_name]
        width = float(hi - lo + 1)
        bottom = 0.0
        row = lookup[(float(kappa), window_name)]
        for label, key, color in DISPLAY_REGION_GROUPS:
            share = float(row[key])
            y_start = y0 + bottom * row_h
            y_height = share * row_h
            rect = Rectangle(
                (float(lo) + x_shift, y_start),
                width,
                y_height,
                transform=trans,
                facecolor=color,
                alpha=0.64,
                edgecolor="white",
                linewidth=0.5,
                zorder=2,
            )
            ax.add_patch(rect)
            if y_height >= 0.075:
                txt_color = "white" if key in {"left_side_share", "right_outside_share"} else "#222222"
                ax.text(
                    float(lo) + x_shift + width / 2.0,
                    y_start + y_height / 2.0,
                    f"{100.0 * share:.0f}%",
                    transform=trans,
                    ha="center",
                    va="center",
                    fontsize=6.1,
                    color=txt_color,
                    bbox=dict(facecolor="white", alpha=0.18, edgecolor="none", pad=0.08),
                    zorder=5,
                )
            bottom += share
        outline = Rectangle(
            (float(lo) + x_shift, y0),
            width,
            row_h,
            transform=trans,
            fill=False,
            edgecolor=outline_color,
            linewidth=0.7,
            zorder=3,
        )
        ax.add_patch(outline)

def plot_overview(rows: list[dict[str, Any]], bundles: dict[float, dict[str, Any]]) -> None:
    lookup = _rows_lookup(rows)
    fig, ax_curve = plt.subplots(figsize=(9.3, 5.1))

    x_max = int(max(float(bundles[float(k)]["case"]["res"].t_peak2) for k in OVERVIEW_CURVE_KAPPAS) + 260)
    curve_labels = {
        0.0: r"$\kappa=0$ control",
        0.0040: r"$\kappa=0.0040$ phase-1 case",
    }
    curve_cache: dict[float, tuple[np.ndarray, np.ndarray]] = {}
    curve_ymax = 0.0
    x_shifts = {
        0.0: -82.0,
        0.0040: 82.0,
    }
    center_label_offsets = {
        0.0: {"peak1": (-26, 12), "valley": (-56, 32), "peak2": (-28, 12)},
        0.0040: {"peak1": (14, -18), "valley": (46, -58), "peak2": (16, -18)},
    }
    for kappa in OVERVIEW_CURVE_KAPPAS:
        case = bundles[float(kappa)]["case"]
        smoothed = smooth_series_display(np.asarray(case["f_total"], dtype=np.float64), window=DISPLAY_SMOOTH_WINDOW)
        t = np.arange(min(len(smoothed), x_max + 1), dtype=np.int64)
        curve = smoothed[: len(t)]
        curve_cache[float(kappa)] = (t, curve)
        curve_ymax = max(curve_ymax, float(np.max(curve)))

    for kappa in OVERVIEW_CURVE_KAPPAS:
        t, curve = curve_cache[float(kappa)]
        case = bundles[float(kappa)]["case"]
        color = KAPPA_COLORS[float(kappa)]
        ax_curve.plot(t, curve, lw=2.25, color=color, label=curve_labels[float(kappa)], zorder=5)
        bounds = bundles[float(kappa)]["window_bounds"]
        _draw_window_budget_row(
            ax_curve,
            kappa=float(kappa),
            lookup=lookup,
            bounds=bounds,
            windows=OVERVIEW_WINDOWS,
            y0=0.04,
            row_h=0.88,
            x_shift=x_shifts[float(kappa)],
            outline_color=color,
        )
        trans = ax_curve.get_xaxis_transform()
        for window_name in OVERVIEW_WINDOWS:
            lo, hi = bounds[window_name]
            center_t = int(round((lo + hi) / 2.0))
            shifted_center = (float(lo) + float(hi)) / 2.0 + x_shifts[float(kappa)]
            ax_curve.axvspan(float(lo), float(hi), ymin=0.0, ymax=0.05, facecolor=color, alpha=0.10, edgecolor=color, linewidth=0.6, zorder=1)
            ax_curve.plot(
                [center_t, shifted_center],
                [0.058, 0.058],
                transform=trans,
                color=color,
                lw=0.8,
                ls=":",
                alpha=0.8,
                zorder=4,
            )
            y_mark = float(curve[min(center_t, len(curve) - 1)])
            ax_curve.scatter([center_t], [y_mark], s=18, color=color, edgecolor="white", linewidth=0.55, zorder=6)
            if window_name == "peak1":
                short_label = r"$t_1$"
            elif window_name == "valley":
                short_label = r"$t_v$"
            else:
                short_label = r"$t_2$"
            dx, dy = center_label_offsets[float(kappa)][window_name]
            ax_curve.annotate(
                short_label,
                xy=(center_t, y_mark),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=7.2,
                color=color,
                ha="left",
                va="bottom",
                bbox=dict(facecolor="white", alpha=0.78, edgecolor="none", pad=0.2),
                arrowprops=dict(arrowstyle="-", color=color, lw=0.55, alpha=0.55),
                zorder=7,
            )

    for window_name in OVERVIEW_WINDOWS:
        centers = []
        for kappa in OVERVIEW_CURVE_KAPPAS:
            lo, hi = bundles[float(kappa)]["window_bounds"][window_name]
            centers.append((float(lo) + float(hi)) / 2.0 + x_shifts[float(kappa)])
        ax_curve.text(
            float(np.mean(centers)),
            0.965,
            WINDOW_LABELS[window_name],
            transform=ax_curve.get_xaxis_transform(),
            ha="center",
            va="bottom",
            fontsize=9.0,
            fontweight="bold",
            color="#333333",
            bbox=dict(facecolor="white", alpha=0.84, edgecolor="none", pad=0.25),
            zorder=7,
        )

    ax_curve.set_xlim(0, x_max)
    ax_curve.set_ylim(0.0, curve_ymax * 1.08)
    ax_curve.set_ylabel("smoothed f(t)")
    ax_curve.set_xlabel("t")
    ax_curve.grid(alpha=0.18)
    ax_curve.legend(
        frameon=False,
        fontsize=8.0,
        ncol=2,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.03),
        borderaxespad=0.0,
        columnspacing=1.3,
        handlelength=1.7,
    )

    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.93])
    ensure_dir(FIG_ROOT)
    fig.savefig(FIG1_RIGHT_PDF, bbox_inches="tight")
    plt.close(fig)
    _compose_overview_vector_pdf()


def _grouped_positions() -> tuple[np.ndarray, dict[float, np.ndarray], float]:
    x = np.arange(len(COMPARE_WINDOWS), dtype=np.float64)
    width = 0.26
    shifts = np.linspace(-width, width, num=len(REPRESENTATIVE_KAPPAS))
    offsets = {float(kappa): x + shift for kappa, shift in zip(REPRESENTATIVE_KAPPAS, shifts, strict=False)}
    return x, offsets, width


def _add_pair_budget_note(
    ax: plt.Axes,
    *,
    title: str,
    valley_values: dict[float, float],
    peak2_values: dict[float, float],
    x_anchor: float = 0.985,
    y_anchor: float = 0.975,
) -> None:
    ax.text(
        x_anchor,
        y_anchor,
        title,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8.1,
        color="#333333",
        bbox=dict(facecolor="white", alpha=0.88, edgecolor="#dddddd", pad=0.25),
        zorder=6,
    )
    for idx, kappa in enumerate(REPRESENTATIVE_KAPPAS):
        valley_val = valley_values[float(kappa)]
        peak2_val = peak2_values[float(kappa)]
        delta_val = peak2_val - valley_val
        ax.text(
            x_anchor,
            y_anchor - 0.07 * (idx + 1),
            rf"$\kappa={kappa:.4f}$: {valley_val:.0f}$\to${peak2_val:.0f} ($\Delta${delta_val:+.0f})",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=7.9,
            color=KAPPA_COLORS[float(kappa)],
            zorder=6,
        )


def plot_tau_out_budget(rows: list[dict[str, Any]]) -> None:
    lookup = _rows_lookup(rows)
    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    x, offsets, width = _grouped_positions()

    valley_steps: dict[float, float] = {}
    peak2_steps: dict[float, float] = {}
    for kappa in REPRESENTATIVE_KAPPAS:
        vals = np.asarray([float(lookup[(float(kappa), window)]["tau_out_ratio"]) for window in COMPARE_WINDOWS], dtype=np.float64)
        outside = np.asarray([float(lookup[(float(kappa), window)]["outside_share"]) for window in COMPARE_WINDOWS], dtype=np.float64)
        valley_steps[float(kappa)] = float(lookup[(float(kappa), "valley")]["outside_steps"])
        peak2_steps[float(kappa)] = float(lookup[(float(kappa), "peak2")]["outside_steps"])
        bars = ax.bar(offsets[float(kappa)], vals, width=width, color=KAPPA_COLORS[float(kappa)], alpha=0.9, label=KAPPA_LABELS[float(kappa)])
        for bar, val in zip(bars, vals, strict=False):
            y_text = val + 0.012
            ax.text(bar.get_x() + bar.get_width() / 2.0, y_text, f"{val:.2f}", ha="center", va="bottom", fontsize=8.3, color="#222222")
        for idx, (xpos, share) in enumerate(zip(offsets[float(kappa)], outside, strict=False)):
            ax.text(
                xpos,
                0.048 + 0.026 * REPRESENTATIVE_KAPPAS.index(float(kappa)),
                f"{100.0 * share:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8.8,
                fontweight="bold",
                color=KAPPA_COLORS[float(kappa)],
                bbox=dict(facecolor="white", alpha=0.9, edgecolor="none", pad=0.18),
            )
    ax.set_xticks(x)
    ax.set_xticklabels([WINDOW_LABELS[w] for w in COMPARE_WINDOWS])
    ax.set_ylim(0.0, 0.92)
    ax.set_ylabel(r"relative timing ratio")
    ax.grid(axis="y", alpha=0.22)
    ax.legend(
        frameon=False,
        fontsize=8,
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.04),
        borderaxespad=0.0,
        columnspacing=1.2,
        handlelength=1.8,
    )
    _add_pair_budget_note(
        ax,
        title="outside budget (steps): valley to peak2",
        valley_values=valley_steps,
        peak2_values=peak2_steps,
    )

    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.92])
    fig.savefig(FIG2_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIG2_PDF, bbox_inches="tight")
    plt.close(fig)


def plot_tau_mem_budget(rows: list[dict[str, Any]]) -> None:
    lookup = _rows_lookup(rows)
    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    x, offsets, width = _grouped_positions()

    valley_steps: dict[float, float] = {}
    peak2_steps: dict[float, float] = {}
    raw_ratio_map: dict[float, list[float]] = {}
    for kappa in REPRESENTATIVE_KAPPAS:
        vals = []
        probs = []
        raw_ratios = []
        for window in COMPARE_WINDOWS:
            ratio = float(lookup[(float(kappa), window)]["tau_mem_ratio"])
            raw_ratios.append(ratio)
            vals.append(0.0 if not np.isfinite(ratio) else ratio)
            prob = float(lookup[(float(kappa), window)]["tau_mem_prob"])
            probs.append(0.0 if not np.isfinite(prob) else prob)
        vals_arr = np.asarray(vals, dtype=np.float64)
        probs_arr = np.asarray(probs, dtype=np.float64)
        raw_ratio_map[float(kappa)] = raw_ratios
        valley_steps[float(kappa)] = float(lookup[(float(kappa), "valley")]["tau_mem_post_steps"]) if np.isfinite(float(lookup[(float(kappa), "valley")]["tau_mem_post_steps"])) else 0.0
        peak2_steps[float(kappa)] = float(lookup[(float(kappa), "peak2")]["tau_mem_post_steps"]) if np.isfinite(float(lookup[(float(kappa), "peak2")]["tau_mem_post_steps"])) else 0.0
        bars = ax.bar(offsets[float(kappa)], vals_arr, width=width, color=KAPPA_COLORS[float(kappa)], alpha=0.9, label=KAPPA_LABELS[float(kappa)])
        for bar, val, raw_ratio in zip(bars, vals_arr, raw_ratios, strict=False):
            y_text = max(0.012, val + 0.012)
            label = "n/a" if not np.isfinite(raw_ratio) else f"{val:.2f}"
            ax.text(bar.get_x() + bar.get_width() / 2.0, y_text, label, ha="center", va="bottom", fontsize=8.3, color="#222222")
        for idx, (xpos, prob) in enumerate(zip(offsets[float(kappa)], probs_arr, strict=False)):
            ax.text(
                xpos,
                0.042 + 0.026 * REPRESENTATIVE_KAPPAS.index(float(kappa)),
                f"{100.0 * prob:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8.8,
                fontweight="bold",
                color=KAPPA_COLORS[float(kappa)],
                bbox=dict(facecolor="white", alpha=0.9, edgecolor="none", pad=0.18),
            )
    ax.set_xticks(x)
    ax.set_xticklabels([WINDOW_LABELS[w] for w in COMPARE_WINDOWS])
    ax.set_ylim(0.0, 0.62)
    ax.set_ylabel(r"relative timing ratio")
    ax.grid(axis="y", alpha=0.22)
    ax.legend(
        frameon=False,
        fontsize=8,
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.04),
        borderaxespad=0.0,
        columnspacing=1.2,
        handlelength=1.8,
    )
    _add_pair_budget_note(
        ax,
        title="post-crossing budget (steps): valley to peak2",
        valley_values=valley_steps,
        peak2_values=peak2_steps,
    )

    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.92])
    fig.savefig(FIG3_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIG3_PDF, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    rows, bundles = build_summary_rows()
    write_summary_csv(rows)
    _plot_partition_schematic(bundles[0.0]["case"])
    plot_overview(rows, bundles)
    plot_tau_out_budget(rows)
    plot_tau_mem_budget(rows)
    print(f"Wrote {SUMMARY_CSV}")
    print(f"Wrote {FIG1_PDF}")
    print(f"Wrote {FIG2_PDF}")
    print(f"Wrote {FIG3_PDF}")


if __name__ == "__main__":
    main()
