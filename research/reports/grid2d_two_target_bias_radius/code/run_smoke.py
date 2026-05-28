#!/usr/bin/env python3
"""Run one exact 2D two-target bias-radius smoke case."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

REPO_ROOT = Path(__file__).resolve().parents[4]
VKCORE_SRC = REPO_ROOT / "packages" / "vkcore" / "src"
if str(VKCORE_SRC) not in sys.path:
    sys.path.insert(0, str(VKCORE_SRC))

import matplotlib.pyplot as plt

from vkcore.grid2d.two_target_bias_radius import (
    build_reflecting_kernel,
    exact_near_far_decomposition,
    near_target_candidates,
    validation_errors,
)

REPORT_DIR = Path(__file__).resolve().parents[1]
FIGURE_DIR = REPORT_DIR / "artifacts" / "figures"
DATA_DIR = REPORT_DIR / "artifacts" / "data"
OUTPUT_DIR = REPORT_DIR / "artifacts" / "outputs"


def main() -> None:
    for path in (FIGURE_DIR, DATA_DIR, OUTPUT_DIR):
        path.mkdir(parents=True, exist_ok=True)

    case = {
        "Lx": 9,
        "Ly": 7,
        "q": 0.70,
        "bias_strength": 0.08,
        "bias_direction": "E",
        "start": (2, 3),
        "far_target": (7, 3),
        "near_radius": 2.0,
        "near_theta": 1.5707963267948966,
        "t_max": 120,
    }

    candidates = near_target_candidates(
        Lx=case["Lx"],
        Ly=case["Ly"],
        start=case["start"],
        radii=[case["near_radius"]],
        thetas=[case["near_theta"]],
        bias_direction=case["bias_direction"],
        exclude=[case["far_target"]],
    )
    if len(candidates) != 1:
        raise RuntimeError(f"expected one near-target candidate, got {len(candidates)}")
    near = candidates[0]

    kernel = build_reflecting_kernel(
        Lx=case["Lx"],
        Ly=case["Ly"],
        q=case["q"],
        bias_strength=case["bias_strength"],
        bias_direction=case["bias_direction"],
        absorbing=[near.coord, case["far_target"]],
    )
    decomp = exact_near_far_decomposition(
        kernel=kernel,
        start=case["start"],
        near_target=near.coord,
        far_target=case["far_target"],
        t_max=case["t_max"],
    )
    errors = validation_errors(kernel, decomp)

    if errors["nonnegative_min_probability"] < -1e-15:
        raise AssertionError(errors)
    if errors["row_stochasticity_error"] >= 1e-12:
        raise AssertionError(errors)
    if errors["mass_balance_error"] >= 1e-10:
        raise AssertionError(errors)
    if errors["decomposition_error"] >= 1e-10:
        raise AssertionError(errors)

    csv_path = OUTPUT_DIR / "smoke_fpt_channels.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["t", "f_total", "f_near", "f_far", "survival"])
        for row in zip(decomp.t, decomp.f_total, decomp.f_near, decomp.f_far, decomp.survival):
            writer.writerow([int(row[0]), f"{row[1]:.17g}", f"{row[2]:.17g}", f"{row[3]:.17g}", f"{row[4]:.17g}"])

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(decomp.t, decomp.f_total, color="#111111", lw=2.0, label="total")
    ax.plot(decomp.t, decomp.f_near, color="#1f77b4", lw=1.8, label="near channel")
    ax.plot(decomp.t, decomp.f_far, color="#d95f02", lw=1.8, label="far channel")
    ax.set_xlabel("time step t")
    ax.set_ylabel("first-passage probability")
    ax.set_title(
        "2D two-target smoke: reflecting boundary, global stay-to-east bias",
        fontsize=11,
    )
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    ax.text(
        0.98,
        0.96,
        (
            f"L={case['Lx']}x{case['Ly']}, q={case['q']}, b={case['bias_strength']}\n"
            f"x0={case['start']}, near={near.coord}, far={case['far_target']}\n"
            f"r={near.r_actual:.3g}, theta={near.theta_actual:.3g} rad"
        ),
        ha="right",
        va="top",
        transform=ax.transAxes,
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.9},
    )
    fig.tight_layout()
    fig_path = FIGURE_DIR / "smoke_fpt_channels.pdf"
    fig.savefig(fig_path)
    plt.close(fig)

    summary = {
        "case": {
            **case,
            "start": list(case["start"]),
            "far_target": list(case["far_target"]),
            "near_target": list(near.coord),
            "near_radius_actual": near.r_actual,
            "near_theta_actual": near.theta_actual,
            "bias_rule": kernel.bias_rule,
            "boundary_rule": kernel.boundary_rule,
        },
        "validation": errors,
        "outputs": {
            "csv": str(csv_path.relative_to(REPO_ROOT)),
            "figure": str(fig_path.relative_to(REPO_ROOT)),
        },
    }
    summary_path = DATA_DIR / "smoke_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary["validation"], sort_keys=True))
    print(f"wrote {csv_path.relative_to(REPO_ROOT)}")
    print(f"wrote {fig_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
