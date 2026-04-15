#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPORT_ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOT = REPORT_ROOT / "artifacts" / "data" / "region_scans" / "one_target_sym_shared_left_top_bottom"
FIG_ROOT = REPORT_ROOT / "artifacts" / "figures" / "region_scans"
SUMMARY_CSV = SCAN_ROOT / "window_region_summary.csv"
OUT_PNG = FIG_ROOT / "one_target_sym_shared_left_top_bottom_window_distribution.png"
OUT_PDF = FIG_ROOT / "one_target_sym_shared_left_top_bottom_window_distribution.pdf"

WINDOW_ORDER = ["peak1", "valley", "peak2"]
REGION_ORDER = ["left_full", "top_full", "bottom_full"]
REGION_LABELS = {
    "left_full": "Left",
    "top_full": "Top",
    "bottom_full": "Bottom",
}
REGION_COLORS = {
    "left_full": "#c62828",
    "top_full": "#1565c0",
    "bottom_full": "#2e7d32",
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_summary() -> dict[str, dict[str, float]]:
    with SUMMARY_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out: dict[str, dict[str, float]] = {window: {} for window in WINDOW_ORDER}
    for row in rows:
        window = str(row["window"])
        region = str(row["region"])
        if window not in out or region not in REGION_ORDER:
            continue
        out[window][region] = float(row["occupancy_share"])
    return out


def main() -> int:
    summary = load_summary()
    raw = np.asarray(
        [[summary[window].get(region, 0.0) for region in REGION_ORDER] for window in WINDOW_ORDER],
        dtype=np.float64,
    )
    selected = np.sum(raw, axis=1, keepdims=True)
    conditional = np.divide(raw, selected, out=np.zeros_like(raw), where=selected > 0.0)

    ensure_dir(FIG_ROOT)
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))
    x = np.arange(len(WINDOW_ORDER), dtype=np.float64)

    for ax_idx, (ax, values, title, ylabel) in enumerate(
        [
            (axes[0], raw, "Raw occupancy share", "share of full pre-hit occupancy"),
            (axes[1], conditional, "Conditional share within selected regions", "share within left/top/bottom"),
        ]
    ):
        bottom = np.zeros(len(WINDOW_ORDER), dtype=np.float64)
        for region in REGION_ORDER:
            ridx = REGION_ORDER.index(region)
            vals = values[:, ridx]
            bars = ax.bar(
                x,
                vals,
                bottom=bottom,
                width=0.65,
                color=REGION_COLORS[region],
                label=REGION_LABELS[region],
                edgecolor="white",
                linewidth=0.8,
            )
            if ax_idx == 1:
                for i, (bar, val) in enumerate(zip(bars, vals, strict=False)):
                    if val < 0.08:
                        continue
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        bottom[i] + val / 2.0,
                        f"{100.0 * val:.1f}%",
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="white",
                        fontweight="bold",
                    )
            bottom += vals

        ax.set_xticks(x, WINDOW_ORDER)
        ax.set_title(title, fontsize=11)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", color="#cccccc", alpha=0.45, linewidth=0.8)
        ax.set_axisbelow(True)

    for i, total in enumerate(selected[:, 0]):
        axes[0].text(x[i], total + 0.01, f"{100.0 * total:.1f}%", ha="center", va="bottom", fontsize=8.5, color="#222222")
        axes[1].text(
            x[i],
            1.015,
            f"selected cover={100.0 * total:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8.2,
            color="#444444",
        )

    axes[1].set_ylim(0.0, 1.10)
    axes[0].legend(frameon=False, loc="upper right")
    fig.suptitle("One-target symmetric baseline: left/top/bottom distribution across peak1, valley, peak2", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(OUT_PDF, bbox_inches="tight")
    plt.close(fig)

    print(OUT_PNG)
    print(OUT_PDF)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
