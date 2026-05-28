#!/usr/bin/env python3
"""Plot two readable 2D two-target double-peak examples for the briefing.

This script reuses the exact 2D two-target kernel and does not modify the
scientific model. The examples are targeted theta-expanded cases found after
the fixed theta=0 heatmap, so they should be described as illustrative examples
rather than as a full angular phase diagram. The report figure uses binned
probability mass for readability; classifier labels still come from the raw
discrete-time PMF.
"""

from __future__ import annotations

import sys
import math
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
FINAL_REPORT = ROOT / "research" / "reports" / "final_multitimescale_fpt_encounter"
FIGURE_DIR = FINAL_REPORT / "artifacts" / "figures"
DATA_DIR = FINAL_REPORT / "artifacts" / "data"

VKCORE_SRC = ROOT / "packages" / "vkcore" / "src"
sys.path.insert(0, str(VKCORE_SRC))
from vkcore.grid2d.two_target_bias_radius import (  # type: ignore  # noqa: E402
    build_reflecting_kernel,
    exact_near_far_decomposition,
)
from vkcore.peaks import classify_distribution_shape  # type: ignore  # noqa: E402


BIN_WIDTH = 4

SELECTED_CASES = [
    {
        "case_id": "theta90_r03_b024",
        "near": (2, 7),
        "r": 3.0,
        "theta": math.pi / 2,
        "b": 0.24,
        "note": "near target above start; far target remains on east-bias path",
    },
    {
        "case_id": "theta45_r04p24_b024",
        "near": (5, 7),
        "r": math.sqrt(18),
        "theta": math.pi / 4,
        "b": 0.24,
        "note": "near target diagonal to start; far target remains on east-bias path",
    },
]


def bin_mass(t: np.ndarray, values: np.ndarray, width: int, max_t: int) -> tuple[np.ndarray, np.ndarray, list[str]]:
    centers: list[float] = []
    masses: list[float] = []
    labels: list[str] = []
    for start in range(0, max_t + 1, width):
        stop = start + width
        mask = (t >= start) & (t < stop)
        if not np.any(mask):
            continue
        centers.append(start + (width - 1) / 2)
        masses.append(float(np.sum(values[mask])))
        labels.append(f"{start}-{stop - 1}")
    return np.asarray(centers), np.asarray(masses), labels


def bin_center_for_time(raw_t: int, width: int) -> float:
    start = (raw_t // width) * width
    return start + (width - 1) / 2


def run_case(config: dict[str, object]) -> dict[str, object]:
    Lx = 15
    Ly = 9
    q = 0.70
    start = (2, 4)
    far = (12, 4)
    near = config["near"]
    b = float(config["b"])
    kernel = build_reflecting_kernel(
        Lx=Lx,
        Ly=Ly,
        q=q,
        bias_strength=b,
        bias_direction="E",
        absorbing=[near, far],
    )
    decomp = exact_near_far_decomposition(
        kernel=kernel,
        start=start,
        near_target=near,
        far_target=far,
        t_max=220,
    )
    shape = classify_distribution_shape(decomp.f_total)
    return {
        "config": config,
        "Lx": Lx,
        "Ly": Ly,
        "q": q,
        "start": start,
        "far": far,
        "decomp": decomp,
        "classification": shape.classification,
        "metrics": shape.metrics,
    }


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    results = [run_case(config) for config in SELECTED_CASES]

    out_csv = DATA_DIR / "grid2d_typical_double_peak_cases.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "case_id",
                "near",
                "far",
                "r",
                "theta",
                "b",
                "classification",
                "t1",
                "tv",
                "t2",
                "p_near",
                "p_far",
                "survival_tail",
                "display_bin_width",
                "note",
            ]
        )
        for result in results:
            config = result["config"]
            decomp = result["decomp"]
            writer.writerow(
                [
                    config["case_id"],
                    config["near"],
                    result["far"],
                    f"{float(config['r']):.6g}",
                    f"{float(config['theta']):.6g}",
                    f"{float(config['b']):.2f}",
                    result["classification"],
                    result["metrics"].get("t1"),
                    result["metrics"].get("tv"),
                    result["metrics"].get("t2"),
                    f"{np.sum(decomp.f_near):.6g}",
                    f"{np.sum(decomp.f_far):.6g}",
                    f"{decomp.survival[-1]:.6g}",
                    BIN_WIDTH,
                    config["note"],
                ]
            )

    fig, axes = plt.subplots(2, 1, figsize=(7.6, 8.4), sharey=False)
    for ax, result in zip(axes, results, strict=True):
        config = result["config"]
        decomp = result["decomp"]
        t = decomp.t
        max_t = 111

        centers, total, _ = bin_mass(t, decomp.f_total, BIN_WIDTH, max_t)
        _, near, _ = bin_mass(t, decomp.f_near, BIN_WIDTH, max_t)
        _, far, _ = bin_mass(t, decomp.f_far, BIN_WIDTH, max_t)

        ax.plot(centers, total, color="#111111", lw=2.6, marker="o", ms=4.5, label="total binned")
        ax.plot(centers, near, color="#1f77b4", lw=2.2, marker="o", ms=3.7, alpha=0.92, label="near binned")
        ax.plot(centers, far, color="#d95f02", lw=2.2, marker="o", ms=3.7, alpha=0.92, label="far binned")

        t1 = int(result["metrics"]["t1"])
        tv = int(result["metrics"]["tv"])
        t2 = int(result["metrics"]["t2"])
        for raw_x, label, color in [(t1, "early bin", "#111111"), (t2, "late bin", "#111111")]:
            x = bin_center_for_time(raw_x, BIN_WIDTH)
            ax.axvline(x, color=color, lw=1.0, ls="--", alpha=0.75)
            ax.text(
                x,
                ax.get_ylim()[1] * 0.93,
                label,
                ha="center",
                va="top",
                fontsize=9.5,
                color=color,
                rotation=90,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 0.4},
            )

        ax.set_title(
            (
                f"{config['case_id']}: near={config['near']}, "
                f"b={float(config['b']):.2f}, {result['classification']}"
            ),
            fontsize=12,
        )
        ax.set_xlabel("time step t", fontsize=11)
        ax.set_ylabel(f"PMF mass per {BIN_WIDTH}-step bin", fontsize=11)
        ax.tick_params(axis="both", labelsize=10)
        ax.grid(True, alpha=0.22)
        ax.text(
            0.98,
            0.96,
            (
                f"near={config['near']}, far={result['far']}\n"
                f"p_near={np.sum(decomp.f_near):.3f}, "
                f"p_far={np.sum(decomp.f_far):.3f}\n"
                f"raw t1={t1}, tv={tv}, t2={t2}\n"
                f"display: {BIN_WIDTH}-step bins"
            ),
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=9.2,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.92},
        )

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=10)
    fig.suptitle(
        f"2D near-vs-far examples ({BIN_WIDTH}-step binned PMF)",
        fontsize=14,
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.95), h_pad=2.0)

    out_pdf = FIGURE_DIR / "grid2d_typical_double_peak_cases.pdf"
    out_png = FIGURE_DIR / "grid2d_typical_double_peak_cases.png"
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, dpi=220, bbox_inches="tight")
    plt.close(fig)

    print(out_pdf.relative_to(ROOT))
    print(out_csv.relative_to(ROOT))


if __name__ == "__main__":
    main()
