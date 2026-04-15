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
    window_ranges,
)


WINDOW_COLORS = {
    "peak1": "#d32f2f",
    "valley": "#fb8c00",
    "peak2": "#1565c0",
}

FIG_PNG = FIG_ROOT / "one_target_membrane_exit_timing_prototype.png"
FIG_PDF = FIG_ROOT / "one_target_membrane_exit_timing_prototype.pdf"
SUMMARY_CSV = DATA_ROOT / "one_target_membrane_exit_timing_summary.csv"
CURVE_CSV = DATA_ROOT / "one_target_membrane_exit_timing_curves.csv"
META_JSON = DATA_ROOT / "one_target_membrane_exit_timing_metadata.json"


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


def build_case(*, case_name: str, display_name: str, kappa_c2o: float, kappa_o2c: float) -> dict[str, Any]:
    base_args = dict(report_mod.ONE_TARGET_BASE_ARGS)
    base_args.pop("delta_core", None)
    base_args.pop("delta_open", None)
    case = build_membrane_case_directional(
        **base_args,
        delta_core=float(mech.DELTA_CORE_SELECTED),
        delta_open=float(mech.DELTA_OPEN_SELECTED),
        kappa_c2o=float(kappa_c2o),
        kappa_o2c=float(kappa_o2c),
        t_max_total=int(report_mod.ONE_TARGET_REP_T_MAX),
    )
    case["case_name"] = case_name
    case["display_name"] = display_name
    return case


def _window_hit_mean(case: dict[str, Any], *, lo: int, hi: int) -> float:
    t = np.arange(len(case["f_total"]), dtype=np.float64)
    weights = np.asarray(case["f_total"][int(lo) : int(hi) + 1], dtype=np.float64)
    total = float(np.sum(weights))
    if total <= 0.0:
        return float("nan")
    return float(np.sum(t[int(lo) : int(hi) + 1] * weights) / total)


def compute_membrane_exit_curves(case: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    n_states = lx * wy
    windows = window_ranges(case["res"].t_peak1, case["res"].t_valley, case["res"].t_peak2, len(case["f_total"]))
    max_hi = max(int(hi) for _, _, hi in windows)

    history, src_nonhit, dst_nonhit, prob_nonhit, hit_prob = compute_one_target_forward_history(case, Lx=lx, max_t=max_hi)
    start_idx = int(case["start"][1]) * lx + int(case["start"][0])
    c2o_edge_keys = {
        (int(a[1]) * lx + int(a[0]), int(b[1]) * lx + int(b[0]))
        for a, b in case.get("membrane_c2o_edges", set())
    }
    c2o_mask = np.fromiter(
        ((int(s), int(d)) in c2o_edge_keys for s, d in zip(src_nonhit.tolist(), dst_nonhit.tolist())),
        dtype=bool,
        count=src_nonhit.size,
    )

    p = np.zeros(n_states, dtype=np.float64)
    p[start_idx] = 1.0
    history_no_exit: list[np.ndarray] = [p.copy()]
    no_c2o_mask = ~c2o_mask
    for _ in range(max_hi):
        p_next = np.zeros_like(p)
        if np.any(no_c2o_mask):
            np.add.at(
                p_next,
                dst_nonhit[no_c2o_mask],
                p[src_nonhit[no_c2o_mask]] * prob_nonhit[no_c2o_mask],
            )
        history_no_exit.append(p_next.copy())
        p = p_next

    summary_rows: list[dict[str, Any]] = []
    curve_rows: list[dict[str, Any]] = []

    for window_name, lo, hi in windows:
        lo_i = int(lo)
        hi_i = int(hi)
        total_hit = float(np.sum(case["f_total"][lo_i : hi_i + 1]))
        first_exit_joint = np.zeros(max_hi + 1, dtype=np.float64)
        b_next = np.zeros(n_states, dtype=np.float64)
        for t in range(max_hi - 1, -1, -1):
            if t <= max_hi - 1 and np.any(c2o_mask):
                src_exit = src_nonhit[c2o_mask]
                dst_exit = dst_nonhit[c2o_mask]
                pr_exit = prob_nonhit[c2o_mask]
                first_exit_joint[t + 1] = float(np.sum(history_no_exit[t][src_exit] * pr_exit * b_next[dst_exit]))

            b_t = np.zeros(n_states, dtype=np.float64)
            np.add.at(b_t, src_nonhit, prob_nonhit * b_next[dst_nonhit])
            if lo_i <= (t + 1) <= hi_i:
                b_t += hit_prob
            b_next = b_t

        conditional_density = np.zeros_like(first_exit_joint)
        if total_hit > 0.0:
            conditional_density = first_exit_joint / total_hit
        cdf = np.cumsum(conditional_density)
        exit_prob = float(cdf[-1]) if cdf.size else 0.0
        mean_exit_time = float("nan")
        if exit_prob > 0.0:
            ts = np.arange(len(first_exit_joint), dtype=np.float64)
            mean_exit_time = float(np.sum(ts * conditional_density) / exit_prob)
        mean_hit_time = _window_hit_mean(case, lo=lo_i, hi=hi_i)
        mean_exit_phase = float("nan")
        if exit_prob > 0.0 and np.isfinite(mean_hit_time) and mean_hit_time > 0.0:
            mean_exit_phase = float(mean_exit_time / mean_hit_time)

        summary_rows.append(
            {
                "case": str(case["case_name"]),
                "display_name": str(case["display_name"]),
                "window": window_name,
                "t_lo": lo_i,
                "t_hi": hi_i,
                "total_hit_mass": total_hit,
                "membrane_exit_probability": exit_prob,
                "mean_first_membrane_exit_time_given_exit": mean_exit_time,
                "mean_hit_time_in_window": mean_hit_time,
                "mean_exit_phase_ratio": mean_exit_phase,
                "phase": int(case["res"].phase),
                "sep_peaks": float(case["res"].sep_peaks),
            }
        )
        for t in range(len(first_exit_joint)):
            curve_rows.append(
                {
                    "case": str(case["case_name"]),
                    "display_name": str(case["display_name"]),
                    "window": window_name,
                    "t": int(t),
                    "first_membrane_exit_density_given_window": float(conditional_density[t]),
                    "first_membrane_exit_cdf_given_window": float(cdf[t]),
                }
            )

    return summary_rows, curve_rows


def plot_exit_timing(summary_rows: list[dict[str, Any]], curve_rows: list[dict[str, Any]]) -> None:
    case_order = ["fully_reflective", "corridor_only_soft"]
    case_titles = {
        "fully_reflective": "Fully reflective control (kappa=0)",
        "corridor_only_soft": "Corridor-only soft case (kappa=0.002)",
    }
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6), gridspec_kw={"width_ratios": [1.1, 1.1, 0.9]})

    for ax, case_name in zip(axes[:2], case_order, strict=False):
        case_curves = [row for row in curve_rows if str(row["case"]) == case_name]
        case_summary = {str(row["window"]): row for row in summary_rows if str(row["case"]) == case_name}
        for window_name in mech.WINDOW_ORDER:
            rows = [row for row in case_curves if str(row["window"]) == window_name]
            xs = np.asarray([int(row["t"]) for row in rows], dtype=np.int64)
            ys = np.asarray([float(row["first_membrane_exit_cdf_given_window"]) for row in rows], dtype=np.float64)
            ax.plot(xs, ys, lw=2.0, color=WINDOW_COLORS[window_name], label=window_name)
            if window_name in case_summary:
                row = case_summary[window_name]
                txt = f"{window_name}: exit={100.0 * float(row['membrane_exit_probability']):.1f}%"
                ax.text(
                    0.98,
                    {"peak1": 0.92, "valley": 0.83, "peak2": 0.74}[window_name],
                    txt,
                    transform=ax.transAxes,
                    ha="right",
                    va="top",
                    fontsize=8.2,
                    color=WINDOW_COLORS[window_name],
                    bbox=dict(facecolor="white", alpha=0.80, edgecolor="none", pad=0.8),
                )
        ax.set_title(case_titles[case_name], fontsize=11)
        ax.set_xlabel("t")
        ax.set_ylim(0.0, 1.02)
        ax.grid(alpha=0.22)

    axes[0].set_ylabel(r"$P(\tau_{\mathrm{mem}} \leq t \mid T \in W)$")

    x = np.arange(len(mech.WINDOW_ORDER), dtype=np.int64)
    phase_vals = np.asarray(
        [
            next(
                float(row["mean_exit_phase_ratio"])
                for row in summary_rows
                if str(row["case"]) == "corridor_only_soft" and str(row["window"]) == window_name
            )
            for window_name in mech.WINDOW_ORDER
        ],
        dtype=np.float64,
    )
    exit_probs = np.asarray(
        [
            next(
                float(row["membrane_exit_probability"])
                for row in summary_rows
                if str(row["case"]) == "corridor_only_soft" and str(row["window"]) == window_name
            )
            for window_name in mech.WINDOW_ORDER
        ],
        dtype=np.float64,
    )
    axes[2].bar(x, phase_vals, color=[WINDOW_COLORS[w] for w in mech.WINDOW_ORDER], alpha=0.88)
    for idx, (phase, prob) in enumerate(zip(phase_vals, exit_probs, strict=False)):
        if np.isfinite(phase):
            axes[2].text(idx, phase + 0.02, f"{phase:.2f}", ha="center", va="bottom", fontsize=9)
        axes[2].text(idx, 0.05, f"exit {100.0 * prob:.1f}%", ha="center", va="bottom", fontsize=8, color="#333333")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(mech.WINDOW_ORDER)
    axes[2].set_ylim(0.0, 1.02)
    axes[2].set_ylabel(r"$E[\tau_{\mathrm{mem}} \mid \tau_{\mathrm{mem}}<T,\ T\in W] / E[T \mid T\in W]$")
    axes[2].set_title("Soft case: relative first-exit timing", fontsize=11)
    axes[2].grid(axis="y", alpha=0.22)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False)
    fig.suptitle("Prototype: when do window-hit walkers first cross the membrane to the outside?", fontsize=12, y=1.04)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
    ensure_dir(FIG_ROOT)
    fig.savefig(FIG_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIG_PDF, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    reflective = build_case(
        case_name="fully_reflective",
        display_name="fully reflective control",
        kappa_c2o=0.0,
        kappa_o2c=0.0,
    )
    soft = build_case(
        case_name="corridor_only_soft",
        display_name="corridor-only soft case",
        kappa_c2o=float(mech.KAPPA_C2O_SELECTED),
        kappa_o2c=float(mech.KAPPA_O2C_SELECTED),
    )

    summary_rows: list[dict[str, Any]] = []
    curve_rows: list[dict[str, Any]] = []
    for case in (reflective, soft):
        rows_summary, rows_curves = compute_membrane_exit_curves(case)
        summary_rows.extend(rows_summary)
        curve_rows.extend(rows_curves)

    write_csv(
        SUMMARY_CSV,
        summary_rows,
        [
            "case",
            "display_name",
            "window",
            "t_lo",
            "t_hi",
            "total_hit_mass",
            "membrane_exit_probability",
            "mean_first_membrane_exit_time_given_exit",
            "mean_hit_time_in_window",
            "mean_exit_phase_ratio",
            "phase",
            "sep_peaks",
        ],
    )
    write_csv(
        CURVE_CSV,
        curve_rows,
        [
            "case",
            "display_name",
            "window",
            "t",
            "first_membrane_exit_density_given_window",
            "first_membrane_exit_cdf_given_window",
        ],
    )
    write_json(
        META_JSON,
        {
            "cases": [
                {
                    "case": str(reflective["case_name"]),
                    "display_name": str(reflective["display_name"]),
                    "kappa_c2o": float(reflective["kappa_c2o"]),
                    "kappa_o2c": float(reflective["kappa_o2c"]),
                    "delta_core": float(reflective["delta_core"]),
                    "delta_open": float(reflective["delta_open"]),
                },
                {
                    "case": str(soft["case_name"]),
                    "display_name": str(soft["display_name"]),
                    "kappa_c2o": float(soft["kappa_c2o"]),
                    "kappa_o2c": float(soft["kappa_o2c"]),
                    "delta_core": float(soft["delta_core"]),
                    "delta_open": float(soft["delta_open"]),
                },
            ],
            "definition": {
                "tau_mem": "first time the walker crosses a membrane c2o edge into the outside",
                "window_conditioning": "condition on hitting the target with T in the named window",
            },
        },
    )
    plot_exit_timing(summary_rows, curve_rows)

    for path in (SUMMARY_CSV, CURVE_CSV, META_JSON, FIG_PNG, FIG_PDF):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
