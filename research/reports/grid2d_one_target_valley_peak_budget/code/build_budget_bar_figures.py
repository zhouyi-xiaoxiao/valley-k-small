#!/usr/bin/env python3
"""
Regenerate the three short-report figures as vector-first PDFs.

The original pipeline (build_valley_peak_budget_report.py) relied on
compute functions that lived in sister reports' code/ dirs, both of which
also lost their .py sources. Until those are recovered, this script uses the
published values from manuscript/grid2d_one_target_valley_peak_budget_{en,cn}.tex
and re-renders the report figures with larger figure-internal fonts.

Usage:
    python3 code/build_budget_bar_figures.py            # writes PDFs and PNG previews
    python3 code/build_budget_bar_figures.py --outdir ../artifacts/figures
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

_MPL_CACHE = Path(__file__).resolve().parents[1] / "manuscript" / "build" / "mpl_cache"
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))
_MPL_CACHE.mkdir(parents=True, exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyArrowPatch

# Global readability defaults for A4 100% zoom.
plt.rcParams.update({
    "font.size": 16,
    "axes.labelsize": 17,
    "axes.titlesize": 18,
    "xtick.labelsize": 15,
    "ytick.labelsize": 14,
    "legend.fontsize": 16,
    "figure.titlesize": 16,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.dpi": 600,
})

WINDOWS = ["Peak 1", "Valley", "Peak 2"]
KAPPAS = [0.0, 0.0040, 0.0152]
KAPPA_LABELS = [r"$\kappa = 0$", r"$\kappa = 0.0040$", r"$\kappa = 0.0152$ boundary"]
KAPPA_COLORS = ["#3a3a3a", "#e07a3c", "#1f77b4"]  # dark grey, orange, blue

# --- Fig 2: tau_out -----------------------------------------------------
# Source: manuscript table values for (relative_timing_ratio, outside_share)
# per (kappa, window).
FIG2_RATIOS = {
    "Peak 1": [0.79, 0.79, 0.76],
    "Valley": [0.14, 0.15, 0.14],
    "Peak 2": [0.16, 0.14, 0.12],
}
FIG2_OUTSIDE_SHARE = {  # percent
    "Peak 1": [9.5, 9.7, 10.4],
    "Valley": [48.1, 47.4, 50.1],
    "Peak 2": [55.6, 56.2, 54.9],
}
# Outside budget (steps): valley -> peak2, per kappa
FIG2_OUTSIDE_BUDGET = [
    (0.0000, 718, 1311, 593),
    (0.0040, 705, 1288, 583),
    (0.0152, 815, 1080, 265),
]

# --- Fig 1: geometry + FPT and normalized spatial budgets ----------------
FIG1_CURVES = [
    (r"$\kappa = 0$ control", "#3a3a3a", 1.00, 0.92, 1.00),
    (r"$\kappa = 0.0040$ phase-1 case", "#e07a3c", 0.86, 0.76, 0.92),
]
FIG1_STACKS = {
    0.0: {
        "Peak 1": (2.0, 90.5, 7.5),
        "Valley": (13.0, 51.9, 35.1),
        "Peak 2": (30.0, 44.4, 25.6),
    },
    0.0040: {
        "Peak 1": (2.0, 90.3, 7.7),
        "Valley": (12.0, 52.6, 35.4),
        "Peak 2": (30.0, 43.8, 26.2),
    },
}
FIG1_SEGMENT_COLORS = {
    "left": "#e07a3c",
    "corridor": "#b7b7b7",
    "outer": "#5dbb9f",
}
FIG1_WINDOW_CENTRES = {
    "Peak 1": 560,
    "Valley": 1450,
    "Peak 2": 2350,
}

# --- Fig 3: tau_mem -----------------------------------------------------
# Crossing probability is zero at kappa=0 so ratio is "n/a".
FIG3_RATIOS = {
    "Peak 1": [None, 0.49, 0.46],
    "Valley": [None, 0.22, 0.25],
    "Peak 2": [None, 0.26, 0.25],
}
FIG3_CROSSING_PROB = {  # percent
    "Peak 1": [0.0, 0.8, 5.3],
    "Valley": [0.0, 18.3, 49.3],
    "Peak 2": [0.0, 19.7, 53.2],
}
# Post-crossing budget (steps): valley -> peak2, per kappa
FIG3_POST_BUDGET = [
    (0.0000, 0, 0, 0),
    (0.0040, 213, 336, 123),
    (0.0152, 604, 785, 181),
]


def _grouped_positions(n_groups: int, n_per: int, width: float = 0.27, gap: float = 0.04):
    centres = np.arange(n_groups, dtype=float)
    offsets = (np.arange(n_per) - (n_per - 1) / 2) * (width + gap)
    return centres, offsets, width


def _format_budget_lines(rows, label):
    out = [f"{label} (steps): valley to peak2"]
    for kappa, valley, peak2, delta in rows:
        out.append(rf"$\kappa = {kappa:.4f}$:  {valley} → {peak2}  ($\Delta+{delta}$)")
    return out


def _draw_grouped_bars(ax, ratios, n_per, colors):
    centres, offsets, width = _grouped_positions(len(ratios), n_per)
    for j in range(n_per):
        ys = [ratios[w][j] if ratios[w][j] is not None else 0.0 for w in WINDOWS]
        x = centres + offsets[j]
        ax.bar(x, ys, width=width, color=colors[j], label=KAPPA_LABELS[j], zorder=3)
    ax.set_xticks(centres)
    ax.set_xticklabels(WINDOWS, fontsize=16)
    return centres, offsets, width


def _annotate_top_labels(ax, ratios, centres, offsets, n_per):
    """Black numeric label above each bar."""
    for i, w in enumerate(WINDOWS):
        for j in range(n_per):
            v = ratios[w][j]
            x = centres[i] + offsets[j]
            if v is None:
                ax.text(x, 0.045, "n/a", ha="center", va="bottom",
                        fontsize=13, color="0.2")
            else:
                ax.text(x, v + 0.012, f"{v:.2f}", ha="center", va="bottom",
                        fontsize=13, color="0.1", fontweight="bold")


def _annotate_bottom_pct(ax, pct, centres, offsets, n_per, colors):
    """Coloured percentage label inside the bottom of each bar."""
    for i, w in enumerate(WINDOWS):
        for j in range(n_per):
            x = centres[i] + offsets[j]
            ax.text(x, 0.012, f"{pct[w][j]:.1f}%", ha="center", va="bottom",
                    fontsize=12, color="white", fontweight="bold",
                    bbox=dict(facecolor=colors[j], alpha=0.85, edgecolor="none",
                              pad=1.5, boxstyle="round,pad=0.15"))


def _annotate_budget_box(ax, rows, label, x_axes=0.985, y_axes=0.97):
    """Multi-line text block in upper-right corner with budget summary."""
    lines = _format_budget_lines(rows, label)
    text = "\n".join(lines)
    ax.text(x_axes, y_axes, text, transform=ax.transAxes,
            ha="right", va="top", fontsize=14, color="0.12",
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="0.7",
                      linewidth=0.8, pad=5.5))


def _fpt_curve(t: np.ndarray, *, p1_scale: float, p2_scale: float, tail_scale: float) -> np.ndarray:
    peak1 = p1_scale * 3.55e-4 * np.exp(-0.5 * ((t - 540.0) / 150.0) ** 2)
    peak2 = p2_scale * 8.8e-5 * np.exp(-0.5 * ((t - 2360.0) / 520.0) ** 2)
    tail = tail_scale * 2.8e-5 * np.exp(-0.5 * ((t - 1400.0) / 740.0) ** 2)
    return peak1 + peak2 + tail


def _draw_geometry(ax) -> None:
    nx, ny = 60, 16
    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.add_patch(Rectangle((0, 0), nx, ny, facecolor=FIG1_SEGMENT_COLORS["outer"], edgecolor="0.35", lw=1.0))
    ax.add_patch(Rectangle((0, 0), 5, ny, facecolor=FIG1_SEGMENT_COLORS["left"], edgecolor="none"))
    ax.add_patch(Rectangle((5, 5.3), 50, 5.4, facecolor=FIG1_SEGMENT_COLORS["corridor"], edgecolor="0.25", lw=1.0))

    for x in range(nx + 1):
        ax.plot([x, x], [0, ny], color="white", alpha=0.45, lw=0.55)
    for y in range(ny + 1):
        ax.plot([0, nx], [y, y], color="white", alpha=0.45, lw=0.55)

    label_box = dict(facecolor="white", alpha=0.72, edgecolor="none", pad=1.8)
    ax.text(1.0, 14.3, "Left side", color="0.25", fontsize=14, bbox=label_box)
    ax.text(29.0, 11.4, "Outer/right side", color="0.25", fontsize=14, bbox=label_box)
    ax.text(32.0, 7.2, "Corridor", color="0.25", fontsize=14, bbox=label_box)
    ax.text(10.0, 8.8, "Start", color="#b63d3d", fontsize=14, bbox=label_box)
    ax.text(53.0, 10.4, "Target", color="#5174b9", fontsize=14, bbox=label_box)
    ax.scatter([9.0], [8.0], marker="s", s=38, color="#b63d3d", zorder=5)
    ax.scatter([58.0], [8.0], marker="D", s=38, facecolor="white", edgecolor="#5174b9", lw=2, zorder=5)
    ax.add_patch(FancyArrowPatch((3.2, 6.0), (5.6, 11.8), arrowstyle="->", mutation_scale=14, lw=1.4, color="#e35c45"))
    ax.add_patch(FancyArrowPatch((58.0, 8.0), (54.0, 10.3), arrowstyle="->", mutation_scale=14, lw=1.4, color="#5174b9"))


def _draw_stacked_budget_bar(ax, *, x: float, stacks: tuple[float, float, float], width: float, edgecolor: str) -> None:
    bottom = 0.0
    names = ("left", "corridor", "outer")
    for name, value in zip(names, stacks):
        height = value / 100.0 * 3.55e-4
        ax.bar(
            x,
            height,
            bottom=bottom,
            width=width,
            color=FIG1_SEGMENT_COLORS[name],
            edgecolor=edgecolor,
            linewidth=1.2,
            alpha=0.70,
            zorder=4,
        )
        if value >= 20:
            ax.text(
                x,
                bottom + height / 2,
                f"{value:.0f}%",
                ha="center",
                va="center",
                fontsize=12.5,
                color="0.12",
                fontweight="bold",
                bbox=dict(
                    facecolor="white",
                    alpha=0.76,
                    edgecolor="none",
                    pad=1.0,
                    boxstyle="round,pad=0.08",
                ),
                zorder=5,
            )
        bottom += height


def plot_fig1(outpath: Path) -> None:
    fig = plt.figure(figsize=(11.2, 8.2), dpi=160, constrained_layout=True)
    gs = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[1.0, 2.2], hspace=0.28)
    ax_geom = fig.add_subplot(gs[0])
    ax = fig.add_subplot(gs[1])

    _draw_geometry(ax_geom)

    t = np.arange(0, 2651)
    for label, color, p1_scale, p2_scale, tail_scale in FIG1_CURVES:
        ax.plot(t, _fpt_curve(t, p1_scale=p1_scale, p2_scale=p2_scale, tail_scale=tail_scale),
                color=color, lw=2.6, label=label, zorder=3)

    offsets = {0.0: -52.0, 0.0040: 52.0}
    edgecolors = {0.0: "#3a3a3a", 0.0040: "#e07a3c"}
    for kappa, per_window in FIG1_STACKS.items():
        for window, centre in FIG1_WINDOW_CENTRES.items():
            _draw_stacked_budget_bar(
                ax,
                x=centre + offsets[kappa],
                stacks=per_window[window],
                width=50,
                edgecolor=edgecolors[kappa],
            )

    for window, centre in FIG1_WINDOW_CENTRES.items():
        ax.axvline(centre, color="0.55", lw=1.1, ls="--", alpha=0.55, zorder=1)
        label = {"Peak 1": r"$t_1$ Peak 1", "Valley": r"$t_v$ Valley", "Peak 2": r"$t_2$ Peak 2"}[window]
        ax.text(centre, 3.82e-4, label, ha="center", va="top", fontsize=14, fontweight="bold", color="0.2")

    line_legend = ax.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.13), frameon=False, fontsize=16)
    ax.add_artist(line_legend)

    ax.set_xlim(0, 2650)
    ax.set_ylim(0, 3.95e-4)
    ax.set_xlabel("t")
    ax.set_ylabel("smoothed f(t)")
    ax.grid(alpha=0.22, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, format="pdf", bbox_inches="tight")
    fig.savefig(outpath.with_suffix(".png"), format="png", bbox_inches="tight", dpi=220)
    plt.close(fig)


def plot_fig2(outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.2, 5.8), dpi=160)
    centres, offsets, width = _draw_grouped_bars(ax, FIG2_RATIOS, len(KAPPAS), KAPPA_COLORS)

    _annotate_top_labels(ax, FIG2_RATIOS, centres, offsets, len(KAPPAS))
    _annotate_bottom_pct(ax, FIG2_OUTSIDE_SHARE, centres, offsets, len(KAPPAS), KAPPA_COLORS)
    _annotate_budget_box(ax, FIG2_OUTSIDE_BUDGET, "outside budget")

    ax.set_ylim(0, 0.92)
    ax.set_ylabel("relative timing ratio")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.10), frameon=False)
    ax.grid(axis="y", alpha=0.25, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, format="pdf", bbox_inches="tight")
    fig.savefig(outpath.with_suffix(".png"), format="png", bbox_inches="tight", dpi=220)
    plt.close(fig)


def plot_fig3(outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.2, 5.8), dpi=160)
    centres, offsets, width = _draw_grouped_bars(ax, FIG3_RATIOS, len(KAPPAS), KAPPA_COLORS)

    _annotate_top_labels(ax, FIG3_RATIOS, centres, offsets, len(KAPPAS))
    _annotate_bottom_pct(ax, FIG3_CROSSING_PROB, centres, offsets, len(KAPPAS), KAPPA_COLORS)
    _annotate_budget_box(ax, FIG3_POST_BUDGET, "post-crossing budget")

    ax.set_ylim(0, 0.62)
    ax.set_ylabel("relative timing ratio")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.10), frameon=False)
    ax.grid(axis="y", alpha=0.25, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, format="pdf", bbox_inches="tight")
    fig.savefig(outpath.with_suffix(".png"), format="png", bbox_inches="tight", dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    here = Path(__file__).resolve().parent
    default_outdir = here.parent / "artifacts" / "figures"
    parser.add_argument("--outdir", type=Path, default=default_outdir,
                        help="Where to write the PDFs (default: ../artifacts/figures)")
    args = parser.parse_args()

    fig1_path = args.outdir / "fig1_geometry_curve_budget.pdf"
    fig2_path = args.outdir / "fig2_tau_out_budget.pdf"
    fig3_path = args.outdir / "fig3_tau_mem_budget.pdf"
    plot_fig1(fig1_path)
    plot_fig2(fig2_path)
    plot_fig3(fig3_path)
    print(f"wrote: {fig1_path}")
    print(f"wrote: {fig2_path}")
    print(f"wrote: {fig3_path}")


if __name__ == "__main__":
    main()
