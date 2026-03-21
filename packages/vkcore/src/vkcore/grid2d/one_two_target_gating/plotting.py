from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Rectangle

from .one_target import GATE_ANCHOR_FAMILY_LABELS, SIDE_GATE_ANCHOR_LABELS, SIDE_R_LABELS, THREE_FAMILY_LABELS, build_start_basin_mask
from .two_target import (
    FAMILY_LABELS_FINE,
    PALETTE_FINE,
    plot_branch_fpt,
    plot_family_fpt,
    plot_geometry_with_gates,
    plot_mc_vs_exact,
    plot_robustness_heatmap,
    plot_scan_family_lines,
    plot_side_usage,
    plot_window_composition,
    save_fig,
)


GATE_FAMILY_COLORS = {
    "N0": "#c62828",
    "N1": "#1f77b4",
    "P0": "#ef6c00",
    "P1": "#6a1b9a",
    "Q0": "#00897b",
    "Q1": "#3949ab",
}
THREE_FAMILY_COLORS = {
    "N": "#c62828",
    "P": "#ef6c00",
    "Q": "#1565c0",
}
SIDE_FAMILY_COLORS = {
    "N": "#b71c1c",
    "TP": "#f9a825",
    "BP": "#ef6c00",
    "TQ": "#1565c0",
    "BQ": "#3949ab",
    "D0": "#b71c1c",
    "D1": "#1565c0",
    "T0": "#f9a825",
    "T1": "#ef6c00",
    "B0": "#3949ab",
    "B1": "#6a1b9a",
}

ROLLBACK_CLASS_COLORS = {
    "L0R0": "#c62828",
    "L0R1": "#1565c0",
    "L1R0": "#ef6c00",
    "L1R1": "#6a1b9a",
}


def _hide_axes(ax: plt.Axes) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def _draw_lattice(ax: plt.Axes, *, lx: int, wy: int, major_step: int = 5) -> None:
    for x in range(lx + 1):
        lw = 0.55 if x % major_step == 0 else 0.28
        color = "#9aa0a6" if x % major_step == 0 else "#d4d7db"
        ax.plot([x - 0.5, x - 0.5], [-0.5, wy - 0.5], color=color, lw=lw, zorder=1)
    for y in range(wy + 1):
        lw = 0.55 if y % major_step == 0 else 0.28
        color = "#9aa0a6" if y % major_step == 0 else "#d4d7db"
        ax.plot([-0.5, lx - 0.5], [y - 0.5, y - 0.5], color=color, lw=lw, zorder=1)


def _set_geometry_ticks(ax: plt.Axes, *, lx: int, wy: int, x_step: int = 5, y_step: int = 2) -> None:
    ax.set_xticks(np.arange(0, lx, x_step))
    ax.set_yticks(np.arange(0, wy, y_step))
    ax.tick_params(axis="both", labelsize=8)
    ax.set_xlabel("x")
    ax.set_ylabel("y")


def _boxed(ax: plt.Axes, x: float, y: float, text: str, *, fc: str, ec: str = "#333333", size: float = 0.18) -> None:
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=9,
        bbox=dict(boxstyle=f"round,pad={size}", fc=fc, ec=ec, lw=1.0),
    )


def _arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], *, text: str | None = None, color: str = "#444444") -> None:
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2, shrinkA=10, shrinkB=10),
    )
    if text:
        mx = 0.5 * (start[0] + end[0])
        my = 0.5 * (start[1] + end[1])
        ax.text(mx, my + 0.045, text, ha="center", va="bottom", fontsize=8, color=color)


def _pretty_case_name(case_name: str) -> str:
    labels = {
        "sym_shared": "shared symmetric baseline",
        "tb_asym_balanced": "top/bottom balanced asymmetry",
        "dir_asym_easy_out_balanced": "directional easy-out / hard-return",
        "dir_asym_easy_in_balanced": "directional hard-out / easy-return",
        "sym": "symmetric membranes",
        "asym": "top-open / bottom-closed",
    }
    return labels.get(case_name, case_name.replace("_", " "))


def _ordered_case_names(rows: Sequence[dict]) -> list[str]:
    preferred = [
        "sym_shared",
        "tb_asym_balanced",
        "dir_asym_easy_out_balanced",
        "dir_asym_easy_in_balanced",
        "sym",
        "asym",
    ]
    cases = {str(row["case"]) for row in rows}
    ordered = [name for name in preferred if name in cases]
    ordered.extend(sorted(cases - set(ordered)))
    return ordered


def plot_phase_v2_flow(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _hide_axes(ax)
    _boxed(ax, 0.13, 0.72, "credible double peak\nfind_two_peaks", fc="#ffe0b2")
    _boxed(ax, 0.40, 0.72, "branch / gate\ntime separation", fc="#c8e6c9")
    _boxed(ax, 0.67, 0.72, "phase-v2\ntwo hard rules", fc="#bbdefb")
    _boxed(ax, 0.88, 0.72, "other metrics\nas diagnostics", fc="#ede7f6")
    _arrow(ax, (0.20, 0.72), (0.33, 0.72))
    _arrow(ax, (0.47, 0.72), (0.60, 0.72))
    _arrow(ax, (0.74, 0.72), (0.83, 0.72))
    _boxed(ax, 0.24, 0.28, "one-target\nfast=C00\nslow=C10+C01+C11", fc="#fff3e0", size=0.24)
    _boxed(ax, 0.53, 0.28, "two-target\nnear / far branch\nsep >= 1", fc="#e8f5e9", size=0.24)
    _boxed(ax, 0.82, 0.28, "unified language\npeak1 -> valley -> peak2", fc="#e3f2fd", size=0.24)
    _arrow(ax, (0.40, 0.62), (0.24, 0.38), color="#8d6e63")
    _arrow(ax, (0.67, 0.62), (0.53, 0.38), color="#2e7d32")
    _arrow(ax, (0.74, 0.62), (0.82, 0.38), color="#1565c0")
    ax.set_title("Phase-v2 flow promoted from the gating-game memo", fontsize=11)
    save_fig(fig, out_path)


def plot_one_target_gate_schematic(
    out_path: Path,
    *,
    case: dict,
    q_values: np.ndarray,
    basin_mask: np.ndarray,
    q_star: float,
) -> None:
    wy = int(case["Wy"])
    lx = int(q_values.size // wy)
    arr = q_values.reshape(wy, lx)
    basin = basin_mask.reshape(wy, lx)
    start = case["start"]
    target = case["target"]
    y_mid, y_low, y_high, x0, x1 = case["wall_span"]

    fig, ax = plt.subplots(figsize=(11.6, 4.9))
    ax.set_facecolor("#f5f3eb")
    im = ax.imshow(
        arr,
        origin="lower",
        cmap="magma",
        vmin=0.0,
        vmax=1.0,
        aspect="equal",
        alpha=0.90,
        extent=(-0.5, lx - 0.5, -0.5, wy - 0.5),
        zorder=0,
    )

    for y in range(y_low, y_high + 1):
        ax.add_patch(
            Rectangle(
                (-0.5, y - 0.5),
                float(lx),
                1.0,
                facecolor="#d9f0ff",
                edgecolor="none",
                alpha=0.18,
                zorder=2,
            )
        )
    ax.add_patch(
        Rectangle(
            (x0 - 0.5, y_low - 0.5),
            float(x1 - x0 + 1),
            float(y_high - y_low + 1),
            facecolor="#9ecae1",
            edgecolor="none",
            alpha=0.14,
            zorder=2,
        )
    )

    sigma_mask = np.where(arr >= float(q_star), 1.0, np.nan)
    ax.contourf(
        np.arange(lx),
        np.arange(wy),
        sigma_mask,
        levels=[0.5, 1.5],
        colors=["#8ecae6"],
        alpha=0.18,
        antialiased=True,
        zorder=2,
    )

    _draw_lattice(ax, lx=lx, wy=wy)

    for y in range(wy):
        for x in range(lx):
            if basin[y, x]:
                ax.add_patch(
                    Rectangle(
                        (x - 0.5, y - 0.5),
                        1.0,
                        1.0,
                        facecolor="#8bc34a",
                        edgecolor="white",
                        lw=0.2,
                        alpha=0.36,
                        zorder=3,
                    )
                )

    membrane_ls = (0, (5, 3))
    if y_low > 0:
        ax.plot([x0 - 0.5, x1 + 0.5], [y_low - 0.5, y_low - 0.5], color="#2d2d2d", lw=2.1, linestyle=membrane_ls, zorder=5)
    if y_high < wy - 1:
        ax.plot([x0 - 0.5, x1 + 0.5], [y_high + 0.5, y_high + 0.5], color="#2d2d2d", lw=2.1, linestyle=membrane_ls, zorder=5)

    xs = np.arange(lx)
    ys = np.arange(wy)
    xx, yy = np.meshgrid(xs, ys)
    ax.contour(xx, yy, arr, levels=[float(q_star)], colors=["#ffffff"], linewidths=2.2, zorder=6)

    ax.scatter([start[0]], [start[1]], s=70, marker="s", color="#e53935", edgecolors="white", linewidths=0.8, zorder=8)
    ax.scatter([target[0]], [target[1]], s=84, marker="D", color="#1565c0", edgecolors="white", linewidths=0.8, zorder=8)

    ax.annotate(
        "start",
        xy=(start[0], start[1]),
        xytext=(max(0.6, float(start[0]) - 2.0), min(float(wy) - 1.0, float(start[1]) + 1.9)),
        fontsize=8,
        color="#b71c1c",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#b71c1c", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#b71c1c", mutation_scale=9),
        zorder=9,
    )
    ax.annotate(
        "target",
        xy=(target[0], target[1]),
        xytext=(max(0.8, float(target[0]) - 5.4), min(float(wy) - 1.0, float(target[1]) + 1.9)),
        fontsize=8,
        color="#0d47a1",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#0d47a1", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#0d47a1", mutation_scale=9),
        zorder=9,
    )

    gate_x = None
    for x in range(lx):
        if float(arr[y_mid, x]) >= float(q_star):
            gate_x = x
            break
    if gate_x is None:
        gate_x = int(round(0.5 * (start[0] + target[0])))

    ax.annotate(
        rf"gate: $q=q^*={q_star:.1f}$",
        xy=(gate_x, y_mid),
        xytext=(min(float(lx) - 12.0, gate_x + 6.0), min(float(wy) - 1.5, y_high + 4.2)),
        fontsize=8.2,
        color="#ffffff",
        bbox=dict(boxstyle="round,pad=0.18", fc="#37474f", ec="#ffffff", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#ffffff", mutation_scale=9),
        zorder=9,
    )
    ax.text(
        0.72,
        0.90,
        rf"$\Sigma_{{q^*}}=\{{q \geq {q_star:.1f}\}}$",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=10,
        color="#ffffff",
        bbox=dict(boxstyle="round,pad=0.22", fc="#0d47a1", ec="#ffffff", lw=0.8, alpha=0.78),
        zorder=9,
    )
    ax.text(
        0.18,
        0.82,
        r"start basin $A=\{x \leq x_s+1,\ |y-y_s|\leq 1\}$",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=8.6,
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#558b2f", lw=0.8, alpha=0.92),
        zorder=9,
    )
    ax.annotate(
        "top membrane",
        xy=(x0 + 8.0, y_high + 0.5),
        xytext=(x0 + 12.6, min(float(wy) - 1.0, y_high + 3.0)),
        fontsize=8,
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="#444444", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#333333", mutation_scale=9),
        zorder=9,
    )
    ax.annotate(
        "bottom membrane",
        xy=(x0 + 8.0, y_low - 0.5),
        xytext=(x0 + 18.0, max(1.5, y_low - 1.9)),
        fontsize=8,
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="#444444", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#333333", mutation_scale=9),
        zorder=9,
    )
    ax.text(
        0.01,
        0.05,
        (
            f"rep case: Wy={wy}, bx={float(case['bx']):+.2f}, h={int(case['corridor_halfwidth'])}, "
            f"m={int(case['wall_margin'])}, wall span x={x0}..{x1}\n"
            "membranes on corridor/outside interfaces; gate from the q=q* contour"
        ),
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.8,
        color="#222222",
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#777777", lw=0.7, alpha=0.92),
        zorder=9,
    )

    ax.set_xlim(-0.5, lx - 0.5)
    ax.set_ylim(-0.5, wy - 0.5)
    ax.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)
    for s in ax.spines.values():
        s.set_linewidth(1.4)
        s.set_color("#000000")
    ax.set_title("One-target exact gate geometry on the representative membrane case", fontsize=11)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(r"$q(x)$")
    save_fig(fig, out_path)


def plot_four_family_windows(out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2))
    time_x = np.array([0.0, 1.0, 2.0])
    window_names = ["peak1", "valley", "peak2"]
    demo = np.array(
        [
            [0.82, 0.10, 0.04, 0.04],
            [0.39, 0.37, 0.11, 0.13],
            [0.14, 0.73, 0.04, 0.09],
        ],
        dtype=np.float64,
    )
    colors = ["#c62828", "#1f77b4", "#ef6c00", "#6a1b9a"]
    labels = ["L0R0", "L0R1", "L1R0", "L1R1"]
    bottom = np.zeros(len(window_names), dtype=np.float64)
    for idx, label in enumerate(labels):
        axes[0].bar(time_x, demo[:, idx], bottom=bottom, color=colors[idx], width=0.64, label=label)
        bottom += demo[:, idx]
    axes[0].set_xticks(time_x)
    axes[0].set_xticklabels(window_names)
    axes[0].set_ylim(0, 1.0)
    axes[0].set_ylabel("family fraction")
    axes[0].set_title("Three-window family composition")
    axes[0].grid(axis="y", alpha=0.22)
    axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2, fontsize=8, frameon=False)

    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    _hide_axes(axes[1])
    _boxed(axes[1], 0.20, 0.75, "L0R0\nno leak\nno rollback", fc="#ffebee")
    _boxed(axes[1], 0.52, 0.75, "L0R1\nno leak\nrollback", fc="#e3f2fd")
    _boxed(axes[1], 0.20, 0.33, "L1R0\nleak\nno rollback", fc="#fff3e0")
    _boxed(axes[1], 0.52, 0.33, "L1R1\nleak\nrollback", fc="#f3e5f5")
    _boxed(axes[1], 0.84, 0.54, "late peak:\nmoderate q* -> L0R1", fc="#e8f5e9", size=0.24)
    _arrow(axes[1], (0.28, 0.68), (0.46, 0.68), text="rollback axis")
    _arrow(axes[1], (0.12, 0.58), (0.12, 0.42), text="leak axis")
    axes[1].set_title("Exact four-family language", fontsize=11)
    fig.tight_layout()
    save_fig(fig, out_path)


def plot_two_target_extension(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.0, 3.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _hide_axes(ax)
    xs = [0.08, 0.26, 0.45, 0.64, 0.82, 0.93]
    texts = [
        "start",
        "near ring",
        "rollback gate",
        "escape gate",
        "progress gates",
        "far target",
    ]
    colors = ["#ffebee", "#fff3e0", "#fbe9e7", "#e3f2fd", "#e8eaf6", "#e8f5e9"]
    for x, text, color in zip(xs, texts, colors):
        _boxed(ax, x, 0.62, text, fc=color)
    for x0, x1 in zip(xs[:-1], xs[1:]):
        _arrow(ax, (x0 + 0.055, 0.62), (x1 - 0.055, 0.62))
    _boxed(ax, 0.28, 0.22, "N_direct / N_detour", fc="#ffe0b2", size=0.24)
    _boxed(ax, 0.74, 0.22, "F_no_return / F_rollback", fc="#bbdefb", size=0.24)
    _arrow(ax, (0.28, 0.52), (0.28, 0.30), color="#ef6c00")
    _arrow(ax, (0.74, 0.52), (0.74, 0.30), color="#1565c0")
    ax.set_title("Two-target extension: from one gate to a gate ladder around the near target", fontsize=11)
    save_fig(fig, out_path)


def plot_unified_mechanism_ladder(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.0, 4.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _hide_axes(ax)
    for y, title, slow_text, color in [
        (0.70, "one-target membrane", "slow branch = leak / rollback family", "#ef6c00"),
        (0.32, "two-target no-corridor", "slow branch = far no-return family", "#1565c0"),
    ]:
        ax.text(0.04, y + 0.08, title, fontsize=10, fontweight="bold")
        for x, label, fc in [
            (0.18, "peak1", "#ffebee"),
            (0.46, "valley", "#eceff1"),
            (0.74, "peak2", "#e3f2fd"),
        ]:
            _boxed(ax, x, y, label, fc=fc)
        _arrow(ax, (0.24, y), (0.40, y), text="mechanism switch", color=color)
        _arrow(ax, (0.52, y), (0.68, y), text=slow_text, color=color)
    ax.text(0.04, 0.90, "common gate language", fontsize=11)
    ax.text(0.04, 0.52, "same three windows, different slow skeleton", fontsize=9, color="#616161")
    save_fig(fig, out_path)


def plot_one_target_qstar_sensitivity(rows: Sequence[dict], out_path: Path) -> None:
    cases = sorted({str(row["case"]) for row in rows})
    labels = ["L0R0", "L0R1", "L1R0", "L1R1"]
    colors = ["#c62828", "#1f77b4", "#ef6c00", "#6a1b9a"]
    fig, axes = plt.subplots(1, len(cases), figsize=(4.8 * len(cases), 4.2), sharey=True)
    if len(cases) == 1:
        axes = [axes]
    for ax, case in zip(axes, cases):
        case_rows = sorted((row for row in rows if str(row["case"]) == case), key=lambda row: float(row["q_star"]))
        x = np.asarray([float(row["q_star"]) for row in case_rows], dtype=np.float64)
        for label, color in zip(labels, colors):
            y = np.asarray([float(row[label]) for row in case_rows], dtype=np.float64)
            ax.plot(x, y, marker="o", lw=1.6, color=color, label=label)
        ax.axvspan(0.4, 0.6, color="#eeeeee", alpha=0.45, lw=0)
        ax.set_title(case)
        ax.set_xlabel("$q^*$")
        ax.set_ylim(0, 1.0)
        ax.grid(alpha=0.22)
    axes[0].set_ylabel("peak2 family fraction")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.05), ncol=4, frameon=False, fontsize=8)
    fig.suptitle("One-target peak2 family fractions across gate placements", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save_fig(fig, out_path)


def plot_one_target_side_window_bars(rows: Sequence[dict], out_path: Path) -> None:
    cases = sorted({str(row["case"]) for row in rows})
    labels = ["D0", "D1", "T0", "T1", "B0", "B1"]
    colors = ["#b71c1c", "#e53935", "#fb8c00", "#ffcc80", "#1565c0", "#90caf9"]
    fig, axes = plt.subplots(1, len(cases), figsize=(5.2 * len(cases), 4.4), sharey=True)
    if len(cases) == 1:
        axes = [axes]
    for ax, case in zip(axes, cases):
        case_rows = [row for row in rows if str(row["case"]) == case]
        order = ["peak1", "valley", "peak2"]
        x = np.arange(len(order), dtype=np.int64)
        bottom = np.zeros(len(order), dtype=np.float64)
        for label, color in zip(labels, colors):
            vals = np.asarray(
                [float(next(row[label] for row in case_rows if str(row["window"]) == window)) for window in order],
                dtype=np.float64,
            )
            ax.bar(x, vals, bottom=bottom, color=color, label=label)
            bottom += vals
        ax.set_xticks(x)
        ax.set_xticklabels(order)
        ax.set_ylim(0, 1.0)
        ax.set_title(case)
        ax.grid(axis="y", alpha=0.22)
    axes[0].set_ylabel("window fraction")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=6, frameon=False, fontsize=8)
    fig.suptitle("One-target side-aware window composition", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save_fig(fig, out_path)


def plot_two_target_phase_atlas(rows: Sequence[dict], out_path: Path) -> None:
    d_vals = sorted({int(float(row["d"])) for row in rows})
    dy_vals = sorted({int(float(row["dy"])) for row in rows})
    phase = np.zeros((len(dy_vals), len(d_vals)), dtype=np.float64)
    purity = np.zeros_like(phase)
    for i, dy in enumerate(dy_vals):
        for j, d in enumerate(d_vals):
            row = next(row for row in rows if int(float(row["d"])) == d and int(float(row["dy"])) == dy)
            phase[i, j] = float(row["phase"])
            purity[i, j] = float(row["windowL_F_no_return"])
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), sharey=True)
    im0 = axes[0].imshow(phase, origin="lower", cmap="YlGnBu", vmin=0.0, vmax=2.0, aspect="auto")
    im1 = axes[1].imshow(purity, origin="lower", cmap="Blues", vmin=0.0, vmax=1.0, aspect="auto")
    for ax, title in zip(axes, ["phase", "late-window F_no_return purity"]):
        ax.set_xticks(np.arange(len(d_vals)))
        ax.set_xticklabels(d_vals)
        ax.set_yticks(np.arange(len(dy_vals)))
        ax.set_yticklabels(dy_vals)
        ax.set_xlabel("d")
        ax.set_title(title)
    axes[0].set_ylabel("$\\Delta y$")
    for i, dy in enumerate(dy_vals):
        for j, d in enumerate(d_vals):
            axes[0].text(j, i, f"{int(phase[i,j])}", ha="center", va="center", fontsize=7)
            axes[1].text(j, i, f"{purity[i,j]:.2f}", ha="center", va="center", fontsize=7)
    c0 = fig.colorbar(im0, ax=axes[0])
    c0.set_label("phase")
    c1 = fig.colorbar(im1, ax=axes[1])
    c1.set_label("late-window F_no_return fraction")
    fig.suptitle("Two-target $(d,\\Delta y)$ atlas rebuilt from canonical code", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save_fig(fig, out_path)


def plot_progress_medians(rows: Sequence[dict], out_path: Path) -> None:
    cases = sorted({str(row["case"]) for row in rows})
    fig, axes = plt.subplots(1, len(cases), figsize=(4.4 * len(cases), 4.0), sharey=True)
    if len(cases) == 1:
        axes = [axes]
    for ax, case in zip(axes, cases):
        case_rows = [row for row in rows if str(row["case"]) == case]
        for row in case_rows:
            stages: list[str] = []
            values: list[float] = []
            if row.get("t_escape_med") not in ("", None):
                stages.append("escape")
                values.append(float(row["t_escape_med"]))
            progress_cols = sorted(
                [key for key, value in row.items() if key.startswith("t_x") and value not in ("", None)],
                key=lambda key: int(key.split("_x", 1)[1].split("_", 1)[0]),
            )
            for key in progress_cols:
                stages.append(key.replace("t_", "").replace("_med", ""))
                values.append(float(row[key]))
            if row.get("t_hit_med") not in ("", None):
                stages.append("hit")
                values.append(float(row["t_hit_med"]))
            if not values:
                continue
            x = np.arange(len(values), dtype=np.int64)
            color = PALETTE_FINE.get(str(row["family"]), "#546e7a")
            ax.plot(x, values, marker="o", lw=1.6, color=color, label=str(row["family"]))
            ax.set_xticks(x)
            ax.set_xticklabels(stages, rotation=20)
        ax.set_title(case)
        ax.grid(alpha=0.22)
        ax.set_xlabel("stage")
    axes[0].set_ylabel("median time")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=5, frameon=False, fontsize=8)
    fig.suptitle("Representative progress medians by family", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save_fig(fig, out_path)


def plot_first_escape_side_usage(rows: Sequence[dict], out_path: Path) -> None:
    cases = sorted({str(row["case"]) for row in rows})
    fig, axes = plt.subplots(1, len(cases), figsize=(4.2 * len(cases), 4.0), sharey=True)
    if len(cases) == 1:
        axes = [axes]
    for ax, case in zip(axes, cases):
        case_rows = [row for row in rows if str(row["case"]) == case]
        families = [str(row["family"]) for row in case_rows]
        lower = np.asarray([float(row["lower"]) for row in case_rows], dtype=np.float64)
        center = np.asarray([float(row["center"]) for row in case_rows], dtype=np.float64)
        upper = np.asarray([float(row["upper"]) for row in case_rows], dtype=np.float64)
        x = np.arange(len(case_rows), dtype=np.int64)
        ax.bar(x, lower, color="#42a5f5", label="lower")
        ax.bar(x, center, bottom=lower, color="#b0bec5", label="center")
        ax.bar(x, upper, bottom=lower + center, color="#ffb74d", label="upper")
        ax.set_xticks(x)
        ax.set_xticklabels(families, rotation=25, ha="right")
        ax.set_ylim(0, 1.0)
        ax.set_title(case)
        ax.grid(axis="y", alpha=0.22)
    axes[0].set_ylabel("fraction")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=3, frameon=False, fontsize=8)
    fig.suptitle("First-escape side usage across representative cases", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save_fig(fig, out_path)


def _draw_one_target_realset_panel(
    ax: plt.Axes,
    *,
    case: dict,
    x_gate: int,
    gate_mode: str,
    title: str,
) -> None:
    wy = int(case["Wy"])
    lx = int(case.get("Lx", max(int(case["start"][0]), int(case["target"][0])) + 2))
    start = case["start"]
    target = case["target"]
    y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    channel_mask = np.asarray(case["channel_mask"], dtype=bool).reshape(wy, lx)
    basin = build_start_basin_mask(Lx=lx, Wy=wy, start_x=int(start[0]), y_mid=int(case["y_mid"])).reshape(wy, lx)

    ax.set_facecolor("#f5f3eb")
    for y in range(wy):
        for x in range(lx):
            if channel_mask[y, x]:
                ax.add_patch(
                    Rectangle(
                        (x - 0.5, y - 0.5),
                        1.0,
                        1.0,
                        facecolor="#d9f0ff",
                        edgecolor="none",
                        alpha=0.28,
                        zorder=0,
                    )
                )
            if basin[y, x]:
                ax.add_patch(
                    Rectangle(
                        (x - 0.5, y - 0.5),
                        1.0,
                        1.0,
                        facecolor="#8bc34a",
                        edgecolor="white",
                        lw=0.20,
                        alpha=0.36,
                        zorder=1,
                    )
                )

    if gate_mode == "line":
        ax.add_patch(
            Rectangle(
                (float(x_gate) - 0.5, -0.5),
                1.0,
                float(wy),
                facecolor="#ce93d8",
                edgecolor="none",
                alpha=0.26,
                zorder=1,
            )
        )
        ax.plot(
            [float(x_gate), float(x_gate)],
            [-0.5, float(wy) - 0.5],
            color="#8e24aa",
            lw=2.2,
            linestyle=(0, (5, 3)),
            zorder=4,
        )
        gate_label = rf"$H_{{X_g}}=\{{x={int(x_gate)}\}}$"
    else:
        ax.add_patch(
            Rectangle(
                (float(x_gate) - 0.5, -0.5),
                float(lx - int(x_gate)),
                float(wy),
                facecolor="#bbdefb",
                edgecolor="none",
                alpha=0.24,
                zorder=0,
            )
        )
        ax.plot(
            [float(x_gate) - 0.5, float(x_gate) - 0.5],
            [-0.5, float(wy) - 0.5],
            color="#1565c0",
            lw=2.2,
            linestyle=(0, (5, 3)),
            zorder=4,
        )
        gate_label = rf"$R_{{X_g}}=\{{x \geq {int(x_gate)}\}}$"

    _draw_lattice(ax, lx=lx, wy=wy)

    membrane_ls = (0, (5, 3))
    ax.plot(
        [x0 - 0.5, x1 + 0.5],
        [y_low - 0.5, y_low - 0.5],
        color="#222222",
        lw=2.0,
        linestyle=membrane_ls,
        zorder=5,
    )
    ax.plot(
        [x0 - 0.5, x1 + 0.5],
        [y_high + 0.5, y_high + 0.5],
        color="#222222",
        lw=2.0,
        linestyle=membrane_ls,
        zorder=5,
    )

    ax.scatter([start[0]], [start[1]], s=68, marker="s", color="#e53935", edgecolors="white", linewidths=0.8, zorder=6)
    ax.scatter([target[0]], [target[1]], s=82, marker="D", color="#1565c0", edgecolors="white", linewidths=0.8, zorder=6)
    ax.annotate(
        "start",
        xy=(start[0], start[1]),
        xytext=(max(0.8, float(start[0]) - 4.0), min(float(wy) - 0.8, float(start[1]) + 2.0)),
        fontsize=8,
        color="#b71c1c",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#b71c1c", lw=0.7, alpha=0.94),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#b71c1c", mutation_scale=9),
        zorder=7,
    )
    ax.annotate(
        "target",
        xy=(target[0], target[1]),
        xytext=(max(0.8, float(target[0]) - 6.8), min(float(wy) - 0.8, float(target[1]) + 2.0)),
        fontsize=8,
        color="#0d47a1",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#0d47a1", lw=0.7, alpha=0.94),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#0d47a1", mutation_scale=9),
        zorder=7,
    )
    ax.text(
        0.03,
        0.97,
        (
            rf"$A=\{{x \leq x_s+1,\ |y-y_s|\leq 1\}}$" "\n"
            rf"$x_s={int(start[0])}$, $x_t={int(target[0])}$, $X_g={int(x_gate)}$"
        ),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.0,
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#558b2f", lw=0.8, alpha=0.94),
        zorder=7,
    )
    ax.text(
        0.97,
        0.97,
        gate_label,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8.6,
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#5d4037", lw=0.8, alpha=0.94),
        zorder=7,
    )
    ax.annotate(
        "top membrane",
        xy=(x0 + 8.0, y_high + 0.5),
        xytext=(min(float(lx) - 8.0, x0 + 15.0), min(float(wy) - 1.2, y_high + 3.0)),
        fontsize=7.8,
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="#444444", lw=0.7, alpha=0.94),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#333333", mutation_scale=8),
        zorder=7,
    )
    ax.annotate(
        "bottom membrane",
        xy=(x0 + 8.0, y_low - 0.5),
        xytext=(min(float(lx) - 9.0, x0 + 18.0), max(1.1, y_low - 2.2)),
        fontsize=7.8,
        color="#111111",
        bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="#444444", lw=0.7, alpha=0.94),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#333333", mutation_scale=8),
        zorder=7,
    )
    ax.text(
        0.02,
        0.03,
        f"corridor: y={y_low}..{y_high}, wall span x={x0}..{x1}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.6,
        color="#222222",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#777777", lw=0.7, alpha=0.94),
        zorder=7,
    )

    ax.set_xlim(-0.5, lx - 0.5)
    ax.set_ylim(-0.5, wy - 0.5)
    ax.set_aspect("equal")
    _set_geometry_ticks(ax, lx=lx, wy=wy)
    for spine in ax.spines.values():
        spine.set_linewidth(1.3)
        spine.set_color("#111111")
    ax.set_title(title, fontsize=10)


def plot_one_target_realset_gate_geometry(out_path: Path, *, case: dict, x_gate: int) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.9), sharey=True)
    _draw_one_target_realset_panel(
        axes[0],
        case=case,
        x_gate=int(x_gate),
        gate_mode="line",
        title="Line gate $H_{X_g}$",
    )
    _draw_one_target_realset_panel(
        axes[1],
        case=case,
        x_gate=int(x_gate),
        gate_mode="halfspace",
        title="Half-space gate $R_{X_g}$",
    )
    fig.suptitle("One-target real-set gate geometry on the membrane representative", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_fig(fig, out_path)


def plot_one_target_gate_geometry(out_path: Path, *, case: dict, x_gate: int) -> None:
    fig, ax = plt.subplots(figsize=(11.2, 4.9))
    _draw_one_target_realset_panel(
        ax,
        case=case,
        x_gate=int(x_gate),
        gate_mode="line",
        title="Canonical gate $G_{X_g} = \\{x = X_g\\}$",
    )
    ax.text(
        0.98,
        0.05,
        "Nearest-neighbor steps with no long-range jumps imply:\n"
        "hit $x=X_g$ iff the trajectory first enters $x\\geq X_g$.",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.8,
        color="#222222",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#3949ab", lw=0.8, alpha=0.96),
        zorder=8,
    )
    fig.suptitle("One-target canonical real-set gate geometry on the membrane representative", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_fig(fig, out_path)


def plot_one_target_state_bookkeeping(out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.4))
    ax = axes[0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _hide_axes(ax)
    cols = [0.12, 0.34, 0.58, 0.80]
    rows = [0.72, 0.30]
    col_titles = ["G0R0", "G0R1", "G1R0", "G1R1"]
    for x, label in zip(cols, col_titles):
        ax.text(x, 0.92, label, ha="center", va="center", fontsize=9, fontweight="bold")
    for y, leak_label in zip(rows, ["L0", "L1"]):
        ax.text(0.03, y, leak_label, ha="center", va="center", fontsize=9, fontweight="bold")
    state_text = {
        (0, 0): "L0G0R0\npre-gate / no leak",
        (0, 1): "L0G0R1\nstructural zero",
        (0, 2): "L0G1R0\ngate seen / no rollback",
        (0, 3): "L0G1R1\ngate seen / rollback",
        (1, 0): "L1G0R0\npre-gate / leak",
        (1, 1): "L1G0R1\nstructural zero",
        (1, 2): "L1G1R0\ngate seen / no rollback",
        (1, 3): "L1G1R1\ngate seen / rollback",
    }
    for row_idx, y in enumerate(rows):
        for col_idx, x in enumerate(cols):
            fc = "#eeeeee" if col_idx == 1 else ["#ffebee", "#f5f5f5", "#e3f2fd", "#f3e5f5"][col_idx]
            _boxed(ax, x, y, state_text[(row_idx, col_idx)], fc=fc, size=0.18)
    _arrow(ax, (0.18, 0.82), (0.28, 0.82), text="leak fixed")
    _arrow(ax, (0.50, 0.82), (0.70, 0.82), text="after seeing gate")
    _arrow(ax, (0.93, 0.66), (0.93, 0.36), text="same G/R,\nwith leak")
    ax.set_title("8-state bookkeeping", fontsize=11)

    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _hide_axes(ax)
    _boxed(ax, 0.18, 0.72, "L0R0\n=L0G0R0 + L0G1R0", fc="#ffebee")
    _boxed(ax, 0.52, 0.72, "L0R1\n=L0G0R1 + L0G1R1", fc="#e3f2fd")
    _boxed(ax, 0.18, 0.30, "L1R0\n=L1G0R0 + L1G1R0", fc="#fff3e0")
    _boxed(ax, 0.52, 0.30, "L1R1\n=L1G0R1 + L1G1R1", fc="#f3e5f5")
    _boxed(ax, 0.84, 0.51, "For left-start representatives,\nall target-hit paths must see the x-gate,\nso G mainly matters as bookkeeping,\nwhile rollback stays the physical separator.", fc="#e8f5e9", size=0.22)
    _arrow(ax, (0.26, 0.64), (0.44, 0.64), text="rollback axis")
    _arrow(ax, (0.10, 0.58), (0.10, 0.38), text="leak axis")
    ax.set_title("4-class continuity summary", fontsize=11)
    fig.tight_layout()
    save_fig(fig, out_path)


def plot_one_target_class_crosswalk(out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.6))

    ax = axes[0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _hide_axes(ax)
    _boxed(ax, 0.18, 0.72, "L0R0\nno leak\nno return to A", fc="#ffebee")
    _boxed(ax, 0.48, 0.72, "L0R1\nno leak\nreturn to A", fc="#e3f2fd")
    _boxed(ax, 0.18, 0.30, "L1R0\nleak\nno return to A", fc="#fff3e0")
    _boxed(ax, 0.48, 0.30, "L1R1\nleak\nreturn to A", fc="#f3e5f5")
    _boxed(ax, 0.82, 0.51, "Rollback is now gate-free:\nleave A first, then later re-enter A.\nThis is the main discrete class language.", fc="#e8f5e9", size=0.20)
    _arrow(ax, (0.12, 0.58), (0.12, 0.36), text="leak axis")
    _arrow(ax, (0.26, 0.64), (0.40, 0.64), text="return-to-A axis")
    ax.set_title("Gate-free rollback classes", fontsize=11)

    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _hide_axes(ax)
    _boxed(ax, 0.18, 0.55, "N\nno leak", fc="#ffebee")
    _boxed(ax, 0.48, 0.55, "P\nfirst leak\nbefore $x=X_g$", fc="#fff3e0")
    _boxed(ax, 0.78, 0.55, "Q\nfirst leak\nafter $x=X_g$", fc="#e3f2fd")
    _arrow(ax, (0.28, 0.55), (0.38, 0.55), text="gate time anchor")
    _arrow(ax, (0.58, 0.55), (0.68, 0.55), text="same leak,\ndifferent timing")
    _boxed(ax, 0.50, 0.18, "$G_{X_g}=\\{x=X_g\\}$ is kept as a real geometric anchor.\nIt answers when the first leak occurs, not whether rollback happened.", fc="#f5f5f5", size=0.20)
    ax.set_title("Gate-anchor N/P/Q classes", fontsize=11)

    fig.tight_layout()
    save_fig(fig, out_path)


def plot_one_target_gate_scan_families(rows: Sequence[dict], out_path: Path) -> None:
    cases = _ordered_case_names(rows)
    fig, axes = plt.subplots(len(cases), 1, figsize=(8.2, 3.8 * len(cases)), sharex=True, sharey=True)
    axes_arr = np.atleast_1d(axes)
    for ax, case in zip(axes_arr, cases):
        case_rows = sorted((row for row in rows if str(row["case"]) == case), key=lambda row: int(row["X_g"]))
        x = np.asarray([int(row["X_g"]) for row in case_rows], dtype=np.int64)
        for label in THREE_FAMILY_LABELS:
            y = np.asarray([float(row[label]) for row in case_rows], dtype=np.float64)
            ax.plot(x, y, marker="o", markersize=3.0, lw=1.5, color=THREE_FAMILY_COLORS[label], label=label)
        ax.set_title(_pretty_case_name(case))
        ax.set_ylim(0, 1.0)
        ax.grid(alpha=0.22)
        ax.set_xlabel("$X_g$")
    axes_arr[0].set_ylabel("late-window family fraction")
    handles, labels = axes_arr[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=3, frameon=False, fontsize=8)
    fig.suptitle("One-target gate-position scan: late-window N/P/Q fractions", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_fig(fig, out_path)


def plot_one_target_gate_scan_totals(rows: Sequence[dict], out_path: Path) -> None:
    cases = _ordered_case_names(rows)
    fig, axes = plt.subplots(len(cases), 1, figsize=(8.2, 3.8 * len(cases)), sharex=True, sharey=True)
    axes_arr = np.atleast_1d(axes)
    series = [
        ("no_leak_total", "no leak", "#c62828"),
        ("pre_gate_leak_total", "pre-gate leak", "#ef6c00"),
        ("post_gate_leak_total", "post-gate leak", "#1565c0"),
        ("rollback_total", "rollback", "#6a1b9a"),
    ]
    for ax, case in zip(axes_arr, cases):
        case_rows = sorted((row for row in rows if str(row["case"]) == case), key=lambda row: int(row["X_g"]))
        x = np.asarray([int(row["X_g"]) for row in case_rows], dtype=np.int64)
        for key, label, color in series:
            ax.plot(x, [float(row[key]) for row in case_rows], color=color, lw=1.6, marker="o", markersize=3.0, label=label)
        ax.set_title(_pretty_case_name(case))
        ax.set_ylim(0, 1.02)
        ax.grid(alpha=0.22)
        ax.set_xlabel("$X_g$")
    axes_arr[0].set_ylabel("total absorption fraction")
    handles, labels = axes_arr[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=4, frameon=False, fontsize=8)
    fig.suptitle("One-target gate-position scan: totals by gate-anchor mechanism", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_fig(fig, out_path)


def plot_one_target_window_families(rows: Sequence[dict], out_path: Path) -> None:
    cases = _ordered_case_names(rows)
    window_order = ["peak1", "valley", "peak2"]
    fig, axes = plt.subplots(1, len(cases), figsize=(6.2 * len(cases), 4.0), sharey=True)
    if len(cases) == 1:
        axes = [axes]
    for ax, case in zip(axes, cases):
        case_rows = [row for row in rows if str(row["case"]) == case]
        x = np.arange(len(window_order), dtype=np.int64)
        bottom = np.zeros(len(window_order), dtype=np.float64)
        for label in THREE_FAMILY_LABELS:
            vals = np.asarray(
                [float(next(row[label] for row in case_rows if str(row["window"]) == window)) for window in window_order],
                dtype=np.float64,
            )
            ax.bar(x, vals, bottom=bottom, color=THREE_FAMILY_COLORS[label], label=label)
            bottom += vals
        ax.set_xticks(x)
        ax.set_xticklabels(window_order)
        ax.set_ylim(0, 1.0)
        ax.set_title(_pretty_case_name(case))
        ax.grid(axis="y", alpha=0.22)
    axes[0].set_ylabel("window fraction")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=3, frameon=False, fontsize=8)
    fig.suptitle("Representative one-target window decomposition under the N/P/Q mechanism", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save_fig(fig, out_path)


def plot_one_target_side_window_bars(rows: Sequence[dict], out_path: Path) -> None:
    cases = _ordered_case_names(rows)
    order = ["peak1", "valley", "peak2"]
    fig, axes = plt.subplots(1, len(cases), figsize=(6.2 * len(cases), 4.0), sharey=True)
    if len(cases) == 1:
        axes = [axes]
    for ax, case in zip(axes, cases):
        case_rows = [row for row in rows if str(row["case"]) == case]
        x = np.arange(len(order), dtype=np.int64)
        bottom = np.zeros(len(order), dtype=np.float64)
        labels = SIDE_R_LABELS if all(label in case_rows[0] for label in SIDE_R_LABELS) else SIDE_GATE_ANCHOR_LABELS
        for label in labels:
            vals = np.asarray(
                [float(next(row[label] for row in case_rows if str(row["window"]) == window)) for window in order],
                dtype=np.float64,
            )
            ax.bar(x, vals, bottom=bottom, color=SIDE_FAMILY_COLORS[label], label=label)
            bottom += vals
        ax.set_xticks(x)
        ax.set_xticklabels(order)
        ax.set_ylim(0, 1.0)
        ax.set_title(_pretty_case_name(case))
        ax.grid(axis="y", alpha=0.22)
    axes[0].set_ylabel("window fraction")
    handles, labels = axes[0].get_legend_handles_labels()
    legend_cols = 6 if labels and labels[0].startswith(("D", "T", "B")) else 5
    title = (
        "One-target rollback side split across the three windows"
        if labels and labels[0].startswith(("D", "T", "B"))
        else "One-target side-aware first-leak timing across the three windows"
    )
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=legend_cols, frameon=False, fontsize=8)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save_fig(fig, out_path)


def _start_scan_grid(rows: Sequence[dict], *, case_name: str, value_key: str) -> tuple[np.ndarray, list[int], list[int], tuple[int, int], tuple[int, int], int]:
    case_rows = [row for row in rows if str(row["case"]) == case_name]
    x_vals = sorted({int(row["start_x"]) for row in case_rows})
    y_vals = sorted({int(row["start_y"]) for row in case_rows})
    grid = np.full((len(y_vals), len(x_vals)), np.nan, dtype=np.float64)
    base_start = next((int(row["base_start_x"]), int(row["base_start_y"])) for row in case_rows)
    target = next((int(row["target_x"]), int(row["target_y"])) for row in case_rows)
    x_gate = int(next(row["x_gate"] for row in case_rows))
    for row in case_rows:
        iy = y_vals.index(int(row["start_y"]))
        ix = x_vals.index(int(row["start_x"]))
        value = row.get(value_key, "")
        if value in ("", None):
            continue
        grid[iy, ix] = float(value)
    return grid, x_vals, y_vals, base_start, target, x_gate


def _draw_start_scan_panel(
    ax: plt.Axes,
    *,
    grid: np.ndarray,
    x_vals: Sequence[int],
    y_vals: Sequence[int],
    base_start: tuple[int, int],
    target: tuple[int, int],
    x_gate: int,
    title: str,
    cbar_label: str,
    cmap: str,
    vmin: float,
    vmax: float,
    discrete_ticks: Sequence[float] | None = None,
) -> None:
    im = ax.imshow(
        grid,
        origin="lower",
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        aspect="equal",
        extent=(min(x_vals) - 0.5, max(x_vals) + 0.5, min(y_vals) - 0.5, max(y_vals) + 0.5),
    )
    for x in range(min(x_vals), max(x_vals) + 2):
        ax.plot([x - 0.5, x - 0.5], [min(y_vals) - 0.5, max(y_vals) + 0.5], color="white", lw=0.18, alpha=0.55, zorder=2)
    for y in range(min(y_vals), max(y_vals) + 2):
        ax.plot([min(x_vals) - 0.5, max(x_vals) + 0.5], [y - 0.5, y - 0.5], color="white", lw=0.18, alpha=0.55, zorder=2)
    ax.scatter([base_start[0]], [base_start[1]], s=68, marker="s", color="#e53935", edgecolors="white", linewidths=0.8, zorder=4)
    ax.scatter([target[0]], [target[1]], s=78, marker="D", color="#1565c0", edgecolors="white", linewidths=0.8, zorder=4)
    ax.plot([x_gate, x_gate], [min(y_vals) - 0.5, max(y_vals) + 0.5], color="#8e24aa", lw=1.8, linestyle=(0, (5, 3)), zorder=4)
    ax.set_xticks(np.arange(min(x_vals), max(x_vals) + 1, 5))
    ax.set_yticks(np.arange(min(y_vals), max(y_vals) + 1, 2))
    ax.tick_params(axis="both", labelsize=8)
    ax.set_xlabel("start x")
    ax.set_ylabel("start y")
    ax.set_title(title, fontsize=10)
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)
        spine.set_color("#111111")
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label(cbar_label)
    if discrete_ticks is not None:
        cbar.set_ticks(discrete_ticks)


def plot_one_target_start_phase_map(rows: Sequence[dict], out_path: Path) -> None:
    phase_labels = ["0", "1", "2"]
    phase_colors = ["#eceff1", "#ffcc80", "#90caf9"]
    cmap = ListedColormap(phase_colors)
    norm = BoundaryNorm(np.arange(-0.5, len(phase_colors) + 0.5, 1.0), cmap.N)
    cases = _ordered_case_names(rows)
    n_cols = min(2, max(1, len(cases)))
    n_rows = int(np.ceil(len(cases) / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6.2 * n_cols, 4.6 * n_rows), sharey=True)
    axes_list = list(np.atleast_1d(axes).reshape(-1))
    for ax in axes_list[len(cases):]:
        ax.axis("off")
    for ax, case_name in zip(axes_list, cases):
        case_rows = [row for row in rows if str(row["case"]) == case_name]
        x_vals = sorted({int(row["start_x"]) for row in case_rows})
        y_vals = sorted({int(row["start_y"]) for row in case_rows})
        grid = np.full((len(y_vals), len(x_vals)), np.nan, dtype=np.float64)
        base_start = next((int(row["base_start_x"]), int(row["base_start_y"])) for row in case_rows)
        target = next((int(row["target_x"]), int(row["target_y"])) for row in case_rows)
        x_gate = int(next(row["x_gate"] for row in case_rows))
        for row in case_rows:
            iy = y_vals.index(int(row["start_y"]))
            ix = x_vals.index(int(row["start_x"]))
            grid[iy, ix] = float(row["phase"])
        im = ax.imshow(
            grid,
            origin="lower",
            cmap=cmap,
            norm=norm,
            aspect="equal",
            extent=(min(x_vals) - 0.5, max(x_vals) + 0.5, min(y_vals) - 0.5, max(y_vals) + 0.5),
        )
        for x in range(min(x_vals), max(x_vals) + 2):
            ax.plot([x - 0.5, x - 0.5], [min(y_vals) - 0.5, max(y_vals) + 0.5], color="white", lw=0.18, alpha=0.55, zorder=2)
        for y in range(min(y_vals), max(y_vals) + 2):
            ax.plot([min(x_vals) - 0.5, max(x_vals) + 0.5], [y - 0.5, y - 0.5], color="white", lw=0.18, alpha=0.55, zorder=2)
        ax.scatter([base_start[0]], [base_start[1]], s=68, marker="s", color="#e53935", edgecolors="white", linewidths=0.8, zorder=4)
        ax.scatter([target[0]], [target[1]], s=78, marker="D", color="#1565c0", edgecolors="white", linewidths=0.8, zorder=4)
        ax.plot([x_gate, x_gate], [min(y_vals) - 0.5, max(y_vals) + 0.5], color="#8e24aa", lw=1.8, linestyle=(0, (5, 3)), zorder=4)
        ax.set_xticks(np.arange(min(x_vals), max(x_vals) + 1, 5))
        ax.set_yticks(np.arange(min(y_vals), max(y_vals) + 1, 2))
        ax.tick_params(axis="both", labelsize=8)
        ax.set_xlabel("start x")
        ax.set_ylabel("start y")
        ax.set_title(_pretty_case_name(case_name), fontsize=10)
        for spine in ax.spines.values():
            spine.set_linewidth(1.2)
            spine.set_color("#111111")
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cbar.set_ticks(range(len(phase_labels)))
        cbar.set_ticklabels(phase_labels)
        cbar.set_label("phase")
    fig.suptitle("One-target full start scan: phase map and phase-0 loss regions", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_fig(fig, out_path)


def plot_one_target_start_leak_balance_map(rows: Sequence[dict], out_path: Path) -> None:
    cases = _ordered_case_names(rows)
    n_cols = min(2, max(1, len(cases)))
    n_rows = int(np.ceil(len(cases) / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6.2 * n_cols, 4.5 * n_rows), sharey=True)
    axes_list = list(np.atleast_1d(axes).reshape(-1))
    vmax = 0.0
    cached = []
    for case_name in cases:
        payload = _start_scan_grid(rows, case_name=case_name, value_key="leak_balance")
        cached.append(payload)
        if np.all(np.isnan(payload[0])):
            continue
        vmax = max(vmax, float(np.nanmax(payload[0])))
    vmax = max(vmax, 1.0)
    for ax, case_name, payload in zip(axes_list, cases, cached):
        grid, x_vals, y_vals, base_start, target, x_gate = payload
        _draw_start_scan_panel(
            ax,
            grid=grid,
            x_vals=x_vals,
            y_vals=y_vals,
            base_start=base_start,
            target=target,
            x_gate=x_gate,
            title=f"{_pretty_case_name(case_name)} | leak balance $Q/(P+Q)$",
            cbar_label="$Q/(P+Q)$",
            cmap="viridis",
            vmin=0.0,
            vmax=1.0,
        )
    for ax in axes_list[len(cases):]:
        ax.axis("off")
    fig.suptitle("One-target start scan: post-gate leak balance under the same canonical $G_{X_g}$", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_fig(fig, out_path)


def _plot_param_heatmap(
    rows: Sequence[dict],
    *,
    out_path: Path,
    x_key: str,
    y_key: str,
    value_key: str,
    title: str,
    x_label: str,
    y_label: str,
    cmap: str,
    annotate_fmt: str,
    discrete_ticks: Sequence[float] | None = None,
    discrete_ticklabels: Sequence[str] | None = None,
    marker_points: Sequence[tuple[str, float, float, str]] = (),
) -> None:
    x_vals = sorted({float(row[x_key]) for row in rows})
    y_vals = sorted({float(row[y_key]) for row in rows})
    grid = np.full((len(y_vals), len(x_vals)), np.nan, dtype=np.float64)
    for row in rows:
        iy = y_vals.index(float(row[y_key]))
        ix = x_vals.index(float(row[x_key]))
        grid[iy, ix] = float(row[value_key])

    discrete = discrete_ticks is not None
    if discrete:
        colors = ["#eceff1", "#ffcc80", "#90caf9"]
        cmap_obj = ListedColormap(colors[: len(discrete_ticks)])
        norm = BoundaryNorm(np.arange(-0.5, len(discrete_ticks) + 0.5, 1.0), cmap_obj.N)
        im_kwargs = {"cmap": cmap_obj, "norm": norm}
    else:
        im_kwargs = {"cmap": cmap}

    fig, ax = plt.subplots(figsize=(7.4, 5.8))
    im = ax.imshow(grid, origin="lower", aspect="auto", extent=(-0.5, len(x_vals) - 0.5, -0.5, len(y_vals) - 0.5), **im_kwargs)
    ax.set_xticks(np.arange(len(x_vals)))
    ax.set_xticklabels([f"{value:.4f}".rstrip("0").rstrip(".") for value in x_vals], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(y_vals)))
    ax.set_yticklabels([f"{value:.4f}".rstrip("0").rstrip(".") for value in y_vals], fontsize=8)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title, fontsize=11)
    for x in range(len(x_vals) + 1):
        ax.plot([x - 0.5, x - 0.5], [-0.5, len(y_vals) - 0.5], color="white", lw=0.45, alpha=0.70, zorder=2)
    for y in range(len(y_vals) + 1):
        ax.plot([-0.5, len(x_vals) - 0.5], [y - 0.5, y - 0.5], color="white", lw=0.45, alpha=0.70, zorder=2)
    for iy in range(len(y_vals)):
        for ix in range(len(x_vals)):
            value = grid[iy, ix]
            if np.isnan(value):
                continue
            ax.text(ix, iy, annotate_fmt.format(value), ha="center", va="center", fontsize=7.3, color="#111111")
    for label, xv, yv, color in marker_points:
        if float(xv) not in x_vals or float(yv) not in y_vals:
            continue
        ix = x_vals.index(float(xv))
        iy = y_vals.index(float(yv))
        ax.scatter([ix], [iy], s=58, marker="o", facecolors="none", edgecolors=color, linewidths=1.5, zorder=4)
        ax.text(ix + 0.14, iy + 0.10, label, fontsize=8.0, color=color, weight="bold", zorder=4)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    if discrete and discrete_ticks is not None:
        cbar.set_ticks(discrete_ticks)
        if discrete_ticklabels is not None:
            cbar.set_ticklabels(discrete_ticklabels)
    cbar.set_label(value_key.replace("_", " "))
    fig.tight_layout()
    save_fig(fig, out_path)


def plot_one_target_parameter_phase_map(
    rows: Sequence[dict],
    out_path: Path,
    *,
    x_key: str,
    y_key: str,
    x_label: str,
    y_label: str,
    title: str,
    marker_points: Sequence[tuple[str, float, float, str]] = (),
) -> None:
    _plot_param_heatmap(
        rows,
        out_path=out_path,
        x_key=x_key,
        y_key=y_key,
        value_key="phase",
        title=title,
        x_label=x_label,
        y_label=y_label,
        cmap="viridis",
        annotate_fmt="{:.0f}",
        discrete_ticks=[0.0, 1.0, 2.0],
        discrete_ticklabels=["0", "1", "2"],
        marker_points=marker_points,
    )


def plot_one_target_parameter_sep_map(
    rows: Sequence[dict],
    out_path: Path,
    *,
    x_key: str,
    y_key: str,
    x_label: str,
    y_label: str,
    title: str,
    marker_points: Sequence[tuple[str, float, float, str]] = (),
) -> None:
    _plot_param_heatmap(
        rows,
        out_path=out_path,
        x_key=x_key,
        y_key=y_key,
        value_key="sep_peaks",
        title=title,
        x_label=x_label,
        y_label=y_label,
        cmap="magma",
        annotate_fmt="{:.2f}",
        marker_points=marker_points,
    )


def plot_one_target_rollback_window_bars(rows: Sequence[dict], out_path: Path) -> None:
    cases = _ordered_case_names(rows)
    order = ["peak1", "valley", "peak2"]
    labels = ["L0R0", "L0R1", "L1R0", "L1R1"]
    fig, axes = plt.subplots(1, len(cases), figsize=(6.1 * len(cases), 4.0), sharey=True)
    axes_list = [axes] if len(cases) == 1 else list(axes)
    for ax, case in zip(axes_list, cases):
        case_rows = [row for row in rows if str(row["case"]) == case]
        x = np.arange(len(order), dtype=np.int64)
        bottom = np.zeros(len(order), dtype=np.float64)
        for label in labels:
            vals = np.asarray(
                [float(next(row[label] for row in case_rows if str(row["window"]) == window)) for window in order],
                dtype=np.float64,
            )
            ax.bar(x, vals, bottom=bottom, color=ROLLBACK_CLASS_COLORS[label], label=label)
            bottom += vals
        ax.set_xticks(x)
        ax.set_xticklabels(order)
        ax.set_ylim(0, 1.0)
        ax.set_title(_pretty_case_name(case))
        ax.grid(axis="y", alpha=0.22)
    axes_list[0].set_ylabel("window fraction")
    handles, labels = axes_list[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=4, frameon=False, fontsize=8)
    fig.suptitle("Gate-free rollback classes across the three windows", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save_fig(fig, out_path)


def plot_one_target_directional_flux(
    out_path: Path,
    *,
    case_blocks: Sequence[tuple[str, dict[str, dict[str, float]]]],
    window_names: Sequence[str] = ("peak1", "valley", "peak2"),
) -> None:
    n = max(1, len(case_blocks))
    fig, axes = plt.subplots(1, n, figsize=(5.2 * n, 4.2), sharey=True)
    axes_list = [axes] if n == 1 else list(axes)
    xs = np.arange(len(window_names), dtype=float)
    width = 0.34
    for ax, (label, stats) in zip(axes_list, case_blocks):
        c2o_vals: list[float] = []
        o2c_vals: list[float] = []
        for wn in window_names:
            payload = stats.get(str(wn), {})
            hit_mass = max(1e-15, float(payload.get("hit_mass", 0.0)))
            c2o_vals.append(float(payload.get("flux_c2o", 0.0)) / hit_mass)
            o2c_vals.append(float(payload.get("flux_o2c", 0.0)) / hit_mass)
        ax.bar(xs - 0.5 * width, c2o_vals, width=width, color="#2c7fb8", label="corridor→outer")
        ax.bar(xs + 0.5 * width, o2c_vals, width=width, color="#f03b20", label="outer→corridor")
        ax.set_xticks(xs)
        ax.set_xticklabels(list(window_names))
        ax.set_title(label, fontsize=10)
        ax.grid(axis="y", alpha=0.20)
        ax.set_xlabel("window")
    axes_list[0].set_ylabel("expected membrane crossings per window-hit trajectory")
    handles, labels = axes_list[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=2, fontsize=8)
    fig.suptitle("Exact directional membrane flux by peak/valley window", fontsize=12, y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save_fig(fig, out_path)


def plot_one_target_window_occupancy_atlas(
    out_path: Path,
    *,
    Lx: int,
    case_blocks: Sequence[tuple[str, dict, dict[str, dict[str, Any]]]],
    window_names: Sequence[str] = ("peak1", "valley", "peak2"),
) -> None:
    n_rows = max(1, len(case_blocks))
    n_cols = max(1, len(window_names))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4.0 * n_cols, 3.6 * n_rows))
    axes_arr = np.atleast_2d(axes)
    vmax = 0.0
    for _, case, stats in case_blocks:
        for wn in window_names:
            if wn in stats:
                vmax = max(vmax, float(np.max(stats[wn]["occupancy"])))
    vmax = max(vmax, 1e-6)

    for i, (label, case, stats) in enumerate(case_blocks):
        wy = int(case["Wy"])
        _, y_low, y_high, x0, x1 = case["wall_span"]
        for j, wn in enumerate(window_names):
            ax = axes_arr[i, j]
            payload = stats.get(str(wn))
            arr = np.asarray(payload["occupancy"], dtype=float) if payload is not None else np.zeros((wy, Lx), dtype=float)
            im = ax.imshow(arr, origin="lower", cmap="magma", vmin=0.0, vmax=vmax, aspect="equal", alpha=0.95)
            for y in range(y_low, y_high + 1):
                ax.add_patch(Rectangle((-0.5, y - 0.5), float(Lx), 1.0, facecolor="#bde4f4", edgecolor="none", alpha=0.08, zorder=2))
            _draw_lattice(ax, lx=Lx, wy=wy)
            membrane_ls = (0, (5, 3))
            ax.plot([x0 - 0.5, x1 + 0.5], [y_low - 0.5, y_low - 0.5], color="#ffffff", lw=1.8, linestyle=membrane_ls, alpha=0.9, zorder=5)
            ax.plot([x0 - 0.5, x1 + 0.5], [y_high + 0.5, y_high + 0.5], color="#ffffff", lw=1.8, linestyle=membrane_ls, alpha=0.9, zorder=5)
            ax.scatter([case["start"][0]], [case["start"][1]], s=48, marker="s", color="#e53935", edgecolors="white", linewidths=0.7, zorder=7)
            ax.scatter([case["target"][0]], [case["target"][1]], s=58, marker="D", color="#1565c0", edgecolors="white", linewidths=0.7, zorder=7)
            hit_mass = 0.0 if payload is None else float(payload.get("hit_mass", 0.0))
            ax.set_title(f"{label} | {wn}", fontsize=10)
            ax.text(
                0.02,
                0.98,
                f"hit={hit_mass:.3e}",
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=7.5,
                color="white",
                bbox=dict(boxstyle="round,pad=0.16", fc=(0.05, 0.05, 0.05, 0.55), ec="none"),
            )
            ax.set_xlim(-0.5, Lx - 0.5)
            ax.set_ylim(-0.5, wy - 0.5)
            ax.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)
            for spine in ax.spines.values():
                spine.set_linewidth(1.2)
                spine.set_color("#111111")

    cbar = fig.colorbar(im, ax=axes_arr.ravel().tolist(), shrink=0.88)
    cbar.set_label("normalized pre-hit occupancy")
    fig.suptitle("Exact window-conditioned occupancy before absorption", fontsize=12, y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    save_fig(fig, out_path)


__all__ = [
    "plot_branch_fpt",
    "plot_family_fpt",
    "plot_first_escape_side_usage",
    "plot_four_family_windows",
    "plot_geometry_with_gates",
    "plot_mc_vs_exact",
    "plot_one_target_class_crosswalk",
    "plot_one_target_directional_flux",
    "plot_one_target_gate_geometry",
    "plot_one_target_gate_schematic",
    "plot_one_target_gate_scan_families",
    "plot_one_target_gate_scan_totals",
    "plot_one_target_parameter_phase_map",
    "plot_one_target_parameter_sep_map",
    "plot_one_target_realset_gate_geometry",
    "plot_one_target_rollback_window_bars",
    "plot_one_target_start_leak_balance_map",
    "plot_one_target_start_phase_map",
    "plot_one_target_side_window_bars",
    "plot_one_target_state_bookkeeping",
    "plot_one_target_window_occupancy_atlas",
    "plot_one_target_window_families",
    "plot_phase_v2_flow",
    "plot_progress_medians",
    "plot_robustness_heatmap",
    "plot_scan_family_lines",
    "plot_side_usage",
    "plot_two_target_extension",
    "plot_two_target_phase_atlas",
    "plot_unified_mechanism_ladder",
    "plot_window_composition",
]
