#!/usr/bin/env python3
"""Redraw the final-report K=2/K=4 shortcut-ring mechanism panel.

The underlying FPT curves and window-composition data are reused from the
fixed-shortcut report. This script only changes the presentation for the final
report: panel labels live in the left margin and the window bars leave a small
top gutter so labels do not touch the axes frame.
"""

from __future__ import annotations

import json
import os
import csv
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).resolve().parents[1] / "build" / "mpl_cache"),
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle


REPORT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = REPORT_DIR.parents[2]
SOURCE_DIR = REPO_DIR / "research" / "reports" / "ring_lazy_jump_ext_rev2"
INPUT_JSON = SOURCE_DIR / "artifacts" / "data" / "fig2_bins_bars_beta0.01.json"
INPUT_FT = SOURCE_DIR / "artifacts" / "data" / "ft_beta0.01.csv"
OUTPUT = REPORT_DIR / "artifacts" / "figures" / "shortcut_ring_k2_k4_beta001.pdf"

WINDOW_ORDER = ["peak1", "valley", "peak2"]
CLASS_ORDER = ["C0J0", "C1pJ0", "C0J1p", "C1pJ1p"]
LINE_COLORS = {"K=2": "#2B2D42", "K=4": "#D90429"}

plt.rcParams.update(
    {
        "font.size": 13,
        "axes.labelsize": 14,
        "axes.titlesize": 15,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "lines.linewidth": 2.0,
        "savefig.dpi": 600,
    }
)


def _intervals_for(data: dict, k_label: str) -> dict[str, tuple[float, float]]:
    intervals = data["bin_intervals_by_k"][k_label]
    return {name: (float(bounds[0]), float(bounds[1])) for name, bounds in intervals.items()}


def _draw_window_bars(
    ax: plt.Axes,
    *,
    data: dict,
    k_label: str,
    band_h: float = 0.92,
) -> None:
    trans = ax.get_xaxis_transform()
    intervals = _intervals_for(data, k_label)
    for window in WINDOW_ORDER:
        t_l, t_r = intervals[window]
        width = t_r - t_l
        y_base = 0.0
        for cls in CLASS_ORDER:
            prop = float(data["proportions"][k_label][window][cls])
            height = prop * band_h
            ax.add_patch(
                Rectangle(
                    (t_l, y_base),
                    width,
                    height,
                    transform=trans,
                    facecolor=data["class_colors"][cls],
                    alpha=0.6,
                    edgecolor="white",
                    linewidth=0.4,
                    zorder=2,
                )
            )
            y_base += height
        ax.add_patch(
            Rectangle(
                (t_l, 0.0),
                width,
                band_h,
                transform=trans,
                fill=False,
                edgecolor="0.2",
                linewidth=0.6,
                zorder=3,
            )
        )


def _annotate_windows(ax: plt.Axes, data: dict, k_label: str) -> None:
    intervals = _intervals_for(data, k_label)
    trans = ax.get_xaxis_transform()
    center_labels = {"peak1": "t1", "valley": "t_v", "peak2": "t2"}
    label_y = {"peak1": 0.77, "valley": 0.50, "peak2": 0.77}
    centers = {window: int(round((intervals[window][0] + intervals[window][1]) / 2.0)) for window in WINDOW_ORDER}
    top_x = {window: float(center) for window, center in centers.items()}
    top_y = {window: 1.015 for window in WINDOW_ORDER}
    top_ha = {window: "center" for window in WINDOW_ORDER}

    for left, right in zip(WINDOW_ORDER, WINDOW_ORDER[1:]):
        if centers[right] - centers[left] < 90:
            top_x[left] = 1.0
            top_x[right] = centers[right] + 14.0
            top_ha[left] = "left"
            top_ha[right] = "left"
            top_y[right] = max(top_y[right], top_y[left] + 0.045)

    for window in WINDOW_ORDER:
        t_l, t_r = intervals[window]
        center = centers[window]
        ax.axvline(center, color="0.25", lw=0.9, ls=":", zorder=7)
        ax.text(
            top_x[window],
            top_y[window],
            f"{center_labels[window]}={center}",
            transform=trans,
            ha=top_ha[window],
            va="bottom",
            fontsize=12,
            color="0.2",
            clip_on=False,
            bbox=dict(facecolor="white", alpha=0.86, edgecolor="none", pad=1.0),
        )
        ax.text(
            center,
            label_y[window],
            f"{window}\n[{int(t_l)},{int(t_r)}]",
            transform=trans,
            ha="center",
            va="bottom",
            fontsize=11,
            color="0.2",
            bbox=dict(facecolor="white", alpha=0.78, edgecolor="none", pad=0.6),
        )


def main() -> None:
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    t: list[float] = []
    f_k2: list[float] = []
    f_k4: list[float] = []
    with INPUT_FT.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            t.append(float(row["t"]))
            f_k2.append(float(row["f_K2"]))
            f_k4.append(float(row["f_K4"]))

    fig, axes = plt.subplots(2, 1, figsize=(8.7, 8.9), dpi=160, sharex=True)
    for ax, k_label, y in zip(axes, ["K=2", "K=4"], [f_k2, f_k4]):
        color = LINE_COLORS[k_label]
        ax.plot(t, y, color=color, lw=2.1, zorder=6)
        ax.set_xlim(1, 1350)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("f(t)")
        ax.text(
            -0.11,
            1.04,
            k_label,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=15,
            fontweight="bold",
            color=color,
            clip_on=False,
            bbox=dict(facecolor="white", alpha=0.9, edgecolor="none", pad=0.4),
        )
        _draw_window_bars(ax, data=data, k_label=k_label)
        _annotate_windows(ax, data=data, k_label=k_label)

    axes[-1].set_xlabel("t (time steps)")
    axes[0].label_outer()
    handles = [Patch(facecolor=data["class_colors"][cls], edgecolor="none", label=cls) for cls in CLASS_ORDER]
    axes[-1].legend(handles=handles, loc="upper right", frameon=True, fontsize=12)
    fig.suptitle("f(t) + windowed class composition bars", fontsize=16, y=0.985)
    fig.tight_layout(rect=[0.04, 0.0, 1.0, 0.955], h_pad=1.45)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
