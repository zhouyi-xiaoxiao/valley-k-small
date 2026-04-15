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


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "packages" / "vkcore" / "src"
SOURCE_REPORT_CODE = REPO_ROOT / "research" / "reports" / "grid2d_one_two_target_gating" / "code"
REPORT_ROOT = Path(__file__).resolve().parents[1]
FIG_ROOT = REPORT_ROOT / "artifacts" / "figures"
DATA_ROOT = REPORT_ROOT / "artifacts" / "data"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SOURCE_REPORT_CODE) not in sys.path:
    sys.path.insert(0, str(SOURCE_REPORT_CODE))

import one_target_mechanism_region_figures as mech
import one_two_target_gating_report as report_mod
from vkcore.grid2d.one_two_target_gating import (
    build_membrane_case_directional,
    compute_one_target_forward_history,
)


FIG_PNG = FIG_ROOT / "one_target_fully_reflective_overall_occupancy.png"
FIG_PDF = FIG_ROOT / "one_target_fully_reflective_overall_occupancy.pdf"
SUMMARY_CSV = DATA_ROOT / "one_target_fully_reflective_overall_region_summary.csv"
META_JSON = DATA_ROOT / "one_target_fully_reflective_overall_metadata.json"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_case() -> dict[str, Any]:
    base_args = dict(report_mod.ONE_TARGET_BASE_ARGS)
    base_args.pop("delta_core", None)
    base_args.pop("delta_open", None)
    case = build_membrane_case_directional(
        **base_args,
        delta_core=float(mech.DELTA_CORE_SELECTED),
        delta_open=float(mech.DELTA_OPEN_SELECTED),
        kappa_c2o=0.0,
        kappa_o2c=0.0,
        t_max_total=40000,
    )
    case["case_name"] = "fully_reflective"
    case["display_name"] = "fully reflective control"
    return case


def compute_overall_occupancy(case: dict[str, Any]) -> np.ndarray:
    history, _src_nonhit, _dst_nonhit, _prob_nonhit, _hit_prob = compute_one_target_forward_history(
        case,
        Lx=int(case["Lx"]),
        max_t=len(case["f_total"]) - 1,
    )
    occ = np.sum(np.asarray(history, dtype=np.float64), axis=0)
    total = float(np.sum(occ))
    if total <= 0.0:
        raise RuntimeError("overall occupancy mass is zero")
    return (occ / total).reshape(int(case["Wy"]), int(case["Lx"]))


def region_summary(case: dict[str, Any], occ_grid: np.ndarray) -> list[dict[str, Any]]:
    masks = mech.region_masks(case)
    formulas = mech.region_formulas(case)
    rows: list[dict[str, Any]] = []
    for region in mech.REGION_ORDER:
        mask = np.asarray(masks[region], dtype=bool)
        vals = occ_grid[mask]
        rows.append(
            {
                "case": str(case["case_name"]),
                "display_name": str(case["display_name"]),
                "region": region,
                "region_label": mech.REGION_LABELS[region],
                "region_formula": formulas[region],
                "cell_count": int(np.sum(mask)),
                "occupancy_share": float(np.sum(vals)),
                "mean_cell_occupancy": float(np.mean(vals)) if vals.size else 0.0,
                "max_cell_occupancy": float(np.max(vals)) if vals.size else 0.0,
            }
        )
    return rows


def plot_overall_distribution(case: dict[str, Any], occ_grid: np.ndarray, summary_rows: list[dict[str, Any]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 4.8), gridspec_kw={"width_ratios": [1.4, 1.0]})

    im = axes[0].imshow(occ_grid, origin="lower", cmap="magma", aspect="auto")
    cbar = fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.03)
    cbar.set_label("normalized pre-hit occupancy")

    start = case["start"]
    target = case["target"]
    _y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    axes[0].scatter([start[0]], [start[1]], s=48, color="#2e7d32", marker="o", label="start", zorder=5)
    axes[0].scatter([target[0]], [target[1]], s=56, color="#111111", marker="*", label="target", zorder=5)
    axes[0].hlines([y_low - 0.5, y_high + 0.5], xmin=x0 - 0.5, xmax=x1 + 0.5, colors="white", linestyles="--", linewidth=1.1)
    axes[0].text(
        0.02,
        0.98,
        "kappa=0, so the membrane-top/bottom reservoir is inaccessible",
        transform=axes[0].transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color="white",
        bbox=dict(facecolor="black", alpha=0.25, edgecolor="none", pad=2.0),
    )
    axes[0].set_title("Fully reflective: long-horizon full pre-hit occupancy heatmap", fontsize=11.5)
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    axes[0].legend(loc="upper right", frameon=False, fontsize=8.5)

    order = mech.REGION_ORDER
    vals = np.asarray([float(next(row["occupancy_share"] for row in summary_rows if row["region"] == region)) for region in order], dtype=np.float64)
    colors = [mech.REGION_COLORS[region] for region in order]
    x = np.arange(len(order), dtype=np.int64)
    axes[1].bar(x, vals, color=colors, alpha=0.9)
    for i, value in enumerate(vals):
        axes[1].text(i, value + 0.008, f"{100.0 * value:.1f}%", ha="center", va="bottom", fontsize=8.5)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(
        ["Left\ncore", "Left\nshoulders", "Left\nouter", "Corridor", "Outer\nreservoir", "Target\nfunnel"],
        fontsize=8.5,
    )
    axes[1].set_ylim(0.0, max(0.65, float(np.max(vals)) + 0.06))
    axes[1].set_ylabel("share of total pre-hit occupancy")
    axes[1].set_title("Region-level overall composition", fontsize=11.5)
    axes[1].grid(axis="y", alpha=0.22)

    fig.suptitle("Fully reflective control: overall spatial distribution without peak/valley splitting", fontsize=12.5, y=1.02)
    fig.tight_layout()
    ensure_dir(FIG_ROOT)
    fig.savefig(FIG_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIG_PDF, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    case = build_case()
    occ_grid = compute_overall_occupancy(case)
    summary_rows = region_summary(case, occ_grid)

    write_csv(
        SUMMARY_CSV,
        summary_rows,
        [
            "case",
            "display_name",
            "region",
            "region_label",
            "region_formula",
            "cell_count",
            "occupancy_share",
            "mean_cell_occupancy",
            "max_cell_occupancy",
        ],
    )
    write_json(
        META_JSON,
        {
            "case": {
                "case_name": str(case["case_name"]),
                "display_name": str(case["display_name"]),
                "Lx": int(case["Lx"]),
                "Wy": int(case["Wy"]),
                "start": list(case["start"]),
                "target": list(case["target"]),
                "wall_span": list(case["wall_span"]),
                "bx": float(case["bx"]),
                "delta_core": float(case["delta_core"]),
                "delta_open": float(case["delta_open"]),
                "kappa_c2o": float(case["kappa_c2o"]),
                "kappa_o2c": float(case["kappa_o2c"]),
                "phase": int(case["res"].phase),
                "sep_peaks": float(case["res"].sep_peaks),
            },
            "occupancy_total": float(np.sum(occ_grid)),
            "survival_tail": float(case["surv"][-1]),
        },
    )
    plot_overall_distribution(case, occ_grid, summary_rows)

    for path in (SUMMARY_CSV, META_JSON, FIG_PNG, FIG_PDF):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
