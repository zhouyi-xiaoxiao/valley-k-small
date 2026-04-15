#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Rectangle


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "packages" / "vkcore" / "src"
REPORT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPORT_ROOT / "artifacts" / "data" / "region_scans" / "one_target_sym_shared_mechanism_regions"
FIG_ROOT = REPORT_ROOT / "artifacts" / "figures" / "region_scans"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import one_two_target_gating_report as report_mod
from vkcore.grid2d.one_two_target_gating import (
    build_membrane_case_directional,
    compute_one_target_window_path_statistics,
    window_ranges,
)


WINDOW_ORDER = ["peak1", "valley", "peak2"]
WINDOW_SHADE = {
    "peak1": "#fde0dc",
    "valley": "#eceff1",
    "peak2": "#e3f2fd",
}
REGION_ORDER = [
    "left_core",
    "left_shoulders",
    "left_outer",
    "corridor",
    "outer_reservoir",
    "target_funnel",
]
REGION_LABELS = {
    "left_core": "Left core",
    "left_shoulders": "Left shoulders",
    "left_outer": "Left outer",
    "corridor": "Corridor",
    "outer_reservoir": "Outer reservoir",
    "target_funnel": "Target funnel",
}
REGION_COLORS = {
    "left_core": "#c62828",
    "left_shoulders": "#ef5350",
    "left_outer": "#fb8c00",
    "corridor": "#8d8d8d",
    "outer_reservoir": "#00897b",
    "target_funnel": "#1565c0",
}
NON_CORRIDOR_ORDER = [region for region in REGION_ORDER if region != "corridor"]

DELTA_CORE_SELECTED = 0.8
DELTA_OPEN_SELECTED = 0.0
KAPPA_C2O_SELECTED = 0.002
KAPPA_O2C_SELECTED = 0.002
CASE_NAME_SELECTED = "corridor_only_soft"
CASE_DISPLAY_SELECTED = "corridor-only soft bias"

SUMMARY_CSV = DATA_ROOT / "window_region_summary.csv"
DETAIL_CSV = DATA_ROOT / "window_region_cells.csv"
META_JSON = DATA_ROOT / "scan_metadata.json"
ARRAYS_NPZ = DATA_ROOT / "window_region_arrays.npz"

SCHEMATIC_PNG = FIG_ROOT / "one_target_sym_shared_mechanism_partition.png"
SCHEMATIC_PDF = FIG_ROOT / "one_target_sym_shared_mechanism_partition.pdf"
BIMODAL_PNG = FIG_ROOT / "one_target_sym_shared_mechanism_bimodal_distribution.png"
BIMODAL_PDF = FIG_ROOT / "one_target_sym_shared_mechanism_bimodal_distribution.pdf"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_case() -> dict[str, Any]:
    base_args = dict(report_mod.ONE_TARGET_BASE_ARGS)
    base_args.pop("delta_core", None)
    base_args.pop("delta_open", None)
    case = build_membrane_case_directional(
        **base_args,
        delta_core=float(DELTA_CORE_SELECTED),
        delta_open=float(DELTA_OPEN_SELECTED),
        kappa_c2o=float(KAPPA_C2O_SELECTED),
        kappa_o2c=float(KAPPA_O2C_SELECTED),
        t_max_total=int(report_mod.ONE_TARGET_REP_T_MAX),
    )
    case["case_name"] = CASE_NAME_SELECTED
    case["display_name"] = CASE_DISPLAY_SELECTED
    return case


def region_masks(case: dict[str, Any]) -> dict[str, np.ndarray]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    start_y = int(case["start"][1])
    _y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    yy, xx = np.meshgrid(np.arange(wy), np.arange(lx), indexing="ij")
    left = xx < int(x0)
    in_corridor = (yy >= int(y_low)) & (yy <= int(y_high))
    center_strip = np.abs(yy - int(start_y)) <= 1
    return {
        "left_core": left & center_strip,
        "left_shoulders": left & in_corridor & (~center_strip),
        "left_outer": left & (~in_corridor),
        "corridor": (xx >= int(x0)) & (xx <= int(x1)) & in_corridor,
        "outer_reservoir": (xx >= int(x0)) & (xx <= int(x1)) & (~in_corridor),
        "target_funnel": xx > int(x1),
    }


def region_formulas(case: dict[str, Any]) -> dict[str, str]:
    start_y = int(case["start"][1])
    _y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    return {
        "left_core": f"x < {int(x0)} and |y-{start_y}| <= 1",
        "left_shoulders": f"x < {int(x0)} and {int(y_low)} <= y <= {int(y_high)} and |y-{start_y}| > 1",
        "left_outer": f"x < {int(x0)} and (y < {int(y_low)} or y > {int(y_high)})",
        "corridor": f"{int(x0)} <= x <= {int(x1)} and {int(y_low)} <= y <= {int(y_high)}",
        "outer_reservoir": f"{int(x0)} <= x <= {int(x1)} and (y < {int(y_low)} or y > {int(y_high)})",
        "target_funnel": f"x > {int(x1)}",
    }


def windows_payload(case: dict[str, Any]) -> list[tuple[str, int, int]]:
    return window_ranges(
        case["res"].t_peak1,
        case["res"].t_valley,
        case["res"].t_peak2,
        len(case["f_total"]),
    )


def draw_lattice(ax: plt.Axes, *, lx: int, wy: int, major_step: int = 5) -> None:
    for x in range(lx + 1):
        lw = 0.55 if x % major_step == 0 else 0.28
        color = "#9aa0a6" if x % major_step == 0 else "#d9dde2"
        ax.plot([x - 0.5, x - 0.5], [-0.5, wy - 0.5], color=color, lw=lw, zorder=3)
    for y in range(wy + 1):
        lw = 0.55 if y % major_step == 0 else 0.28
        color = "#9aa0a6" if y % major_step == 0 else "#d9dde2"
        ax.plot([-0.5, lx - 0.5], [y - 0.5, y - 0.5], color=color, lw=lw, zorder=3)


def label_box(ax: plt.Axes, x: float, y: float, text: str, color: str) -> None:
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=8.5,
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec=color, lw=0.9, alpha=0.96),
        zorder=8,
    )


def plot_partition_schematic(case: dict[str, Any], masks: dict[str, np.ndarray]) -> None:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    start = case["start"]
    target = case["target"]
    _y_mid, y_low, y_high, x0, x1 = case["wall_span"]

    region_grid = np.full((wy, lx), -1, dtype=np.int64)
    for idx, region in enumerate(REGION_ORDER):
        region_grid[masks[region]] = idx
    if np.any(region_grid < 0):
        raise RuntimeError("mechanism partition does not cover the full state space")

    fig, ax = plt.subplots(figsize=(12.4, 4.9))
    ax.set_facecolor("#f5f3eb")

    for y in range(wy):
        for x in range(lx):
            region = REGION_ORDER[int(region_grid[y, x])]
            ax.add_patch(
                Rectangle(
                    (x - 0.5, y - 0.5),
                    1.0,
                    1.0,
                    facecolor=REGION_COLORS[region],
                    edgecolor="white",
                    lw=0.18,
                    alpha=0.78,
                    zorder=1,
                )
            )

    membrane_ls = (0, (5, 3))
    if y_low > 0:
        ax.plot([x0 - 0.5, x1 + 0.5], [y_low - 0.5, y_low - 0.5], color="#303030", lw=2.1, linestyle=membrane_ls, zorder=5)
    if y_high < wy - 1:
        ax.plot([x0 - 0.5, x1 + 0.5], [y_high + 0.5, y_high + 0.5], color="#303030", lw=2.1, linestyle=membrane_ls, zorder=5)

    draw_lattice(ax, lx=lx, wy=wy)

    ax.scatter([start[0]], [start[1]], s=74, marker="s", color="#e53935", edgecolors="white", linewidths=0.8, zorder=9)
    ax.scatter([target[0]], [target[1]], s=88, marker="D", color="#0d47a1", edgecolors="white", linewidths=0.8, zorder=9)

    ax.annotate(
        "start",
        xy=(start[0], start[1]),
        xytext=(start[0] + 2.8, start[1] + 3.2),
        fontsize=8.2,
        color="#b71c1c",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#b71c1c", lw=0.7, alpha=0.95),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#b71c1c", mutation_scale=9),
        zorder=10,
    )
    ax.annotate(
        "target",
        xy=(target[0], target[1]),
        xytext=(target[0] - 4.8, target[1] + 3.2),
        fontsize=8.2,
        color="#0d47a1",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#0d47a1", lw=0.7, alpha=0.95),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#0d47a1", mutation_scale=9),
        zorder=10,
    )

    label_box(ax, 2.0, start[1], "left core", REGION_COLORS["left_core"])
    ax.annotate(
        "left shoulders",
        xy=(2.0, y_high),
        xytext=(9.2, wy - 1.1),
        fontsize=8.2,
        ha="center",
        va="center",
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=REGION_COLORS["left_shoulders"], lw=0.8, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color=REGION_COLORS["left_shoulders"], mutation_scale=9),
        zorder=10,
    )
    ax.annotate(
        "left outer",
        xy=(1.7, 1.7),
        xytext=(8.8, 1.0),
        fontsize=8.2,
        ha="center",
        va="center",
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=REGION_COLORS["left_outer"], lw=0.8, alpha=0.96),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color=REGION_COLORS["left_outer"], mutation_scale=9),
        zorder=10,
    )
    label_box(ax, 29.5, start[1], "corridor", REGION_COLORS["corridor"])
    label_box(ax, 29.5, wy - 2.0, "outer reservoir", REGION_COLORS["outer_reservoir"])
    label_box(ax, 29.5, 1.0, "outer reservoir", REGION_COLORS["outer_reservoir"])
    label_box(ax, 57.0, wy - 2.0, "target funnel", REGION_COLORS["target_funnel"])

    ax.text(
        0.01,
        0.03,
        (
            f"corridor-only soft-bias variant, Wy={wy}, corridor y={y_low}..{y_high}, wall span x={x0}..{x1}\n"
            f"delta_core={DELTA_CORE_SELECTED:.2f}, delta_open={DELTA_OPEN_SELECTED:.2f}, kappa={KAPPA_C2O_SELECTED:.4f}; no gate contour is drawn"
        ),
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.9,
        color="#222222",
        bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="#666666", lw=0.7, alpha=0.95),
        zorder=10,
    )

    ax.set_xlim(-0.5, lx - 0.5)
    ax.set_ylim(-0.5, wy - 0.5)
    ax.set_xticks(np.arange(0, lx, 5))
    ax.set_yticks(np.arange(0, wy, 2))
    ax.tick_params(axis="both", labelsize=8)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)
        spine.set_color("#000000")
    ax.set_title("One-target corridor-only soft-bias variant: mechanism-aware spatial partition", fontsize=11.5)

    legend_handles = [Patch(facecolor=REGION_COLORS[r], edgecolor="none", label=REGION_LABELS[r]) for r in REGION_ORDER]
    fig.legend(legend_handles, [REGION_LABELS[r] for r in REGION_ORDER], loc="upper center", bbox_to_anchor=(0.5, 0.98), ncol=3, frameon=False, fontsize=8.2)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    ensure_dir(FIG_ROOT)
    fig.savefig(SCHEMATIC_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(SCHEMATIC_PDF, bbox_inches="tight")
    plt.close(fig)


def compute_window_region_matrix(
    summary_map: dict[str, dict[str, float]],
    *,
    region_order: list[str],
) -> np.ndarray:
    return np.asarray(
        [[summary_map[window].get(region, 0.0) for region in region_order] for window in WINDOW_ORDER],
        dtype=np.float64,
    )


def compute_conditional_profile(
    summary_map: dict[str, dict[str, float]],
    *,
    region_order: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    raw = compute_window_region_matrix(summary_map, region_order=region_order)
    totals = np.sum(raw, axis=1)
    conditional = np.divide(
        raw,
        totals[:, None],
        out=np.zeros_like(raw),
        where=totals[:, None] > 0.0,
    )
    return raw, totals, conditional


def draw_window_composition_bars(
    ax: plt.Axes,
    *,
    windows: list[tuple[str, int, int]],
    proportions: np.ndarray,
    region_order: list[str],
    value_labels: dict[str, str] | None = None,
    window_note_labels: dict[str, str] | None = None,
    top_labels: dict[str, str] | None = None,
    top_label_y: float = 1.008,
    note_y_cycle: tuple[float, float] = (0.80, 0.60),
) -> None:
    trans = ax.get_xaxis_transform()
    for idx, (window_name, lo, hi) in enumerate(windows):
        x_left = float(lo)
        width = float(max(1, int(hi) - int(lo)))
        cumulative = 0.0
        for region_name, prop in zip(region_order, proportions[idx], strict=False):
            height = float(prop)
            if height <= 0.0:
                continue
            ax.add_patch(
                Rectangle(
                    (x_left, cumulative),
                    width,
                    height,
                    transform=trans,
                    facecolor=REGION_COLORS[region_name],
                    alpha=0.62,
                    edgecolor="white",
                    linewidth=0.45,
                    zorder=2,
                )
            )
            cumulative += height
        ax.add_patch(
            Rectangle(
                (x_left, 0.0),
                width,
                1.0,
                transform=trans,
                fill=False,
                edgecolor="#333333",
                linewidth=0.65,
                zorder=3,
            )
        )
        x_center = 0.5 * (float(lo) + float(hi))
        ax.axvline(x_center, color="#424242", lw=0.9, ls=":", zorder=7)
        if top_labels is not None:
            ax.text(
                x_center,
                float(top_label_y),
                top_labels[window_name],
                transform=trans,
                ha="center",
                va="bottom",
                fontsize=7.7,
                color="#222222",
                clip_on=False,
                bbox=dict(facecolor="white", alpha=0.76, edgecolor="none", pad=0.8),
            )
        if window_note_labels is not None:
            note_y = float(note_y_cycle[idx % len(note_y_cycle)])
            ax.text(
                x_center,
                note_y,
                window_note_labels[window_name],
                transform=trans,
                ha="center",
                va="bottom",
                fontsize=7.0,
                color="#222222",
                bbox=dict(facecolor="white", alpha=0.78, edgecolor="none", pad=0.55),
                zorder=8,
            )
        if value_labels is not None:
            ax.text(
                x_center,
                0.03,
                value_labels[window_name],
                transform=trans,
                ha="center",
                va="bottom",
                fontsize=7.2,
                color="#222222",
                bbox=dict(facecolor="white", alpha=0.82, edgecolor="none", pad=0.55),
                zorder=8,
            )


def plot_bimodal_distribution(case: dict[str, Any], summary_map: dict[str, dict[str, float]], windows: list[tuple[str, int, int]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), gridspec_kw={"width_ratios": [1.15, 1.0]})
    ax_curve, ax_bar = axes

    f_total = np.asarray(case["f_total"], dtype=np.float64)
    t = np.arange(f_total.size, dtype=np.int64)
    ax_curve.plot(t, f_total, color="#111111", lw=1.9)

    top_labels = {
        "peak1": f"t1={int(case['res'].t_peak1)}",
        "valley": f"t_v={int(case['res'].t_valley)}",
        "peak2": f"t2={int(case['res'].t_peak2)}",
    }
    window_note_labels = {
        window_name: f"{window_name}\n[{int(lo)},{int(hi)}]"
        for window_name, lo, hi in windows
    }

    ax_curve.set_xlim(0, min(int(f_total.size - 1), 2300))
    ax_curve.set_ylim(0.0, 1.15 * float(np.max(f_total)))
    ax_curve.set_xlabel("t")
    ax_curve.set_ylabel("first-passage pmf")
    ax_curve.grid(alpha=0.24)
    raw = compute_window_region_matrix(summary_map, region_order=REGION_ORDER)
    totals = np.sum(raw, axis=1)
    if not np.allclose(totals, 1.0, atol=1.0e-10):
        raise RuntimeError(f"window shares should sum to 1, got {totals!r}")

    shown_regions = list(NON_CORRIDOR_ORDER)
    _shown_raw, non_corridor_mass, conditional = compute_conditional_profile(
        summary_map,
        region_order=shown_regions,
    )
    draw_window_composition_bars(
        ax_curve,
        windows=windows,
        proportions=conditional,
        region_order=shown_regions,
        value_labels={
            window_name: f"remaining={100.0 * non_corridor_mass[WINDOW_ORDER.index(window_name)]:.1f}%"
            for window_name in WINDOW_ORDER
        },
        window_note_labels=window_note_labels,
        top_labels=top_labels,
        top_label_y=1.006,
        note_y_cycle=(0.78, 0.55),
    )

    x = np.arange(len(WINDOW_ORDER), dtype=np.float64)
    bottom = np.zeros(len(WINDOW_ORDER), dtype=np.float64)
    for region in shown_regions:
        idx = shown_regions.index(region)
        vals = conditional[:, idx]
        bars = ax_bar.bar(
            x,
            vals,
            bottom=bottom,
            width=0.66,
            color=REGION_COLORS[region],
            edgecolor="white",
            linewidth=0.8,
            label=REGION_LABELS[region],
        )
        for i, (bar, val) in enumerate(zip(bars, vals, strict=False)):
            if val < 0.07:
                continue
            ax_bar.text(
                bar.get_x() + bar.get_width() / 2.0,
                bottom[i] + 0.5 * val,
                f"{100.0 * val:.1f}%",
                ha="center",
                va="center",
                fontsize=7.6,
                color="white",
                fontweight="bold",
            )
        bottom += vals

    ax_bar.set_xticks(x, WINDOW_ORDER)
    ax_bar.set_ylim(0.0, 1.0)
    ax_bar.set_ylabel("share within remaining mass")
    ax_bar.set_title("Remaining-region composition", fontsize=11, pad=10)
    ax_bar.grid(axis="y", alpha=0.24)
    ax_bar.set_axisbelow(True)
    for i, total in enumerate(non_corridor_mass):
        ax_bar.text(
            x[i],
            0.992,
            f"remaining={100.0 * total:.1f}%",
            ha="center",
            va="top",
            fontsize=8.0,
            color="#444444",
        )

    handles = [Patch(facecolor=REGION_COLORS[r], edgecolor="none", label=REGION_LABELS[r]) for r in shown_regions]
    fig.legend(handles, [REGION_LABELS[r] for r in shown_regions], loc="upper center", bbox_to_anchor=(0.5, 0.97), ncol=3, frameon=False, fontsize=8.2)
    fig.suptitle("One-target corridor-only soft-bias variant: bimodality and non-corridor mechanism-region distribution", fontsize=12, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    ensure_dir(FIG_ROOT)
    fig.savefig(BIMODAL_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(BIMODAL_PDF, bbox_inches="tight")
    plt.close(fig)


def run_scan_and_plot() -> dict[str, Path]:
    case = build_case()
    windows = windows_payload(case)
    stats = compute_one_target_window_path_statistics(case, Lx=int(case["Lx"]), windows=windows)
    masks = region_masks(case)
    formulas = region_formulas(case)

    full_cover = np.zeros((int(case["Wy"]), int(case["Lx"])), dtype=np.int64)
    for region in REGION_ORDER:
        full_cover += masks[region].astype(np.int64)
    if not np.all(full_cover == 1):
        raise RuntimeError("mechanism masks do not partition the full lattice exactly once")

    summary_rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    arrays_payload: dict[str, np.ndarray] = {}
    summary_map: dict[str, dict[str, float]] = {window_name: {} for window_name, _, _ in windows}

    for region_name, mask in masks.items():
        arrays_payload[f"{region_name}_mask"] = mask.astype(np.uint8)

    for window_name, lo, hi in windows:
        payload = stats[window_name]
        occ = np.asarray(payload["occupancy"], dtype=np.float64)
        arrays_payload[f"{window_name}_occupancy"] = occ
        arrays_payload[f"{window_name}_occupancy_mass"] = np.asarray([np.sum(occ)], dtype=np.float64)

        for region_name, mask in masks.items():
            coords = np.argwhere(mask)
            values = occ[mask]
            region_share = float(np.sum(values))
            summary_map[window_name][region_name] = region_share
            summary_rows.append(
                {
                    "case": case["case_name"],
                    "window": window_name,
                    "t_lo": int(lo),
                    "t_hi": int(hi),
                    "region": region_name,
                    "region_label": REGION_LABELS[region_name],
                    "region_formula": formulas[region_name],
                    "cell_count": int(mask.sum()),
                    "occupancy_share": region_share,
                    "mean_cell_occupancy": float(np.mean(values)),
                    "max_cell_occupancy": float(np.max(values)),
                    "hit_mass": float(payload["hit_mass"]),
                    "window_flux_c2o": float(payload["flux_c2o"]),
                    "window_flux_o2c": float(payload["flux_o2c"]),
                }
            )

            order = np.argsort(-values, kind="stable")
            for rank, idx_in_order in enumerate(order, start=1):
                y, x = coords[int(idx_in_order)]
                detail_rows.append(
                    {
                        "case": case["case_name"],
                        "window": window_name,
                        "region": region_name,
                        "x": int(x),
                        "y": int(y),
                        "occupancy": float(values[int(idx_in_order)]),
                        "rank_in_region": int(rank),
                    }
                )

    metadata = {
        "case": case["case_name"],
        "display_name": case["display_name"],
        "geometry": {
            "Lx": int(case["Lx"]),
            "Wy": int(case["Wy"]),
            "start": [int(case["start"][0]), int(case["start"][1])],
            "target": [int(case["target"][0]), int(case["target"][1])],
            "wall_span": [int(v) for v in case["wall_span"]],
        },
        "windows": [
            {
                "window": str(window_name),
                "t_lo": int(lo),
                "t_hi": int(hi),
                "hit_mass": float(stats[window_name]["hit_mass"]),
                "flux_c2o": float(stats[window_name]["flux_c2o"]),
                "flux_o2c": float(stats[window_name]["flux_o2c"]),
                "region_mass_total": float(sum(summary_map[window_name].values())),
            }
            for window_name, lo, hi in windows
        ],
        "region_formulas": formulas,
        "region_labels": {name: REGION_LABELS[name] for name in REGION_ORDER},
        "region_order": REGION_ORDER,
        "window_order": WINDOW_ORDER,
    }

    ensure_dir(DATA_ROOT)
    write_csv(
        SUMMARY_CSV,
        summary_rows,
        [
            "case",
            "window",
            "t_lo",
            "t_hi",
            "region",
            "region_label",
            "region_formula",
            "cell_count",
            "occupancy_share",
            "mean_cell_occupancy",
            "max_cell_occupancy",
            "hit_mass",
            "window_flux_c2o",
            "window_flux_o2c",
        ],
    )
    write_csv(
        DETAIL_CSV,
        detail_rows,
        ["case", "window", "region", "x", "y", "occupancy", "rank_in_region"],
    )
    write_json(META_JSON, metadata)
    np.savez_compressed(ARRAYS_NPZ, **arrays_payload)

    plot_partition_schematic(case, masks)
    plot_bimodal_distribution(case, summary_map, windows)

    return {
        "summary": SUMMARY_CSV,
        "detail": DETAIL_CSV,
        "metadata": META_JSON,
        "arrays": ARRAYS_NPZ,
        "schematic_png": SCHEMATIC_PNG,
        "schematic_pdf": SCHEMATIC_PDF,
        "bimodal_png": BIMODAL_PNG,
        "bimodal_pdf": BIMODAL_PDF,
    }


def main() -> int:
    outputs = run_scan_and_plot()
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
