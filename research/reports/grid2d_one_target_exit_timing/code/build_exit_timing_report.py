#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
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
TABLE_ROOT = REPORT_ROOT / "artifacts" / "tables"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SOURCE_REPORT_CODE) not in sys.path:
    sys.path.insert(0, str(SOURCE_REPORT_CODE))

import one_two_target_gating_report as report_mod
from vkcore.grid2d.one_two_target_gating import (
    build_membrane_case_directional,
    compute_one_target_first_event_statistics,
    compute_one_target_forward_history,
    window_ranges,
)
from vkcore.grid2d.rect_bimodality.cli import smooth_series_display


CASE_TITLE = "One-target corridor-only soft-bias membrane-timing continuation"
KAPPA_VALUES = [0.0, 0.00025, 0.0005, 0.00075, 0.0010, 0.00125, 0.0015, 0.00175, 0.0020, 0.0025, 0.0030, 0.0040, 0.0050, 0.0060]
REPRESENTATIVE_KAPPAS = [0.0, 0.0140, 0.0152]
SCAN_EVAL_KAPPAS = sorted(set(KAPPA_VALUES + REPRESENTATIVE_KAPPAS))
CRITICAL_KAPPAS = [0.0120, 0.0130, 0.0140, 0.0145, 0.0148, 0.0149, 0.0150, 0.0151, 0.0152, 0.0153]
CRITICAL_CURVE_KAPPAS = [0.0140, 0.0152, 0.0153]
REP_T_MAX = 40000
REP_CURVE_T_MAX = 4000
DELTA_CORE = 0.8
DELTA_OPEN = 0.0
WINDOW_ORDER = ["peak1", "valley", "peak2"]
WINDOW_COLORS = {
    "peak1": "#c62828",
    "valley": "#fb8c00",
    "peak2": "#1565c0",
}
EVENT_COLORS = {
    "tau_out": "#2e7d32",
    "tau_mem": "#6a1b9a",
}
SPLIT_COLORS = {
    "early": "#26a69a",
    "late": "#ffa726",
    "no_exit": "#9e9e9e",
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

SCAN_SUMMARY_CSV = DATA_ROOT / "exit_timing_scan_summary.csv"
REP_CDF_CSV = DATA_ROOT / "representative_exit_timing_cdfs.csv"
FULLY_REFLECTIVE_REGION_CSV = DATA_ROOT / "fully_reflective_overall_region_summary.csv"
CRITICAL_SCAN_CSV = DATA_ROOT / "critical_takeover_scan.csv"
CRITICAL_CURVE_CSV = DATA_ROOT / "critical_collapse_profiles.csv"
SCAN_METADATA_JSON = DATA_ROOT / "exit_timing_metadata.json"
REP_OVERVIEW_TEX = TABLE_ROOT / "representative_exit_timing_overview.tex"

FIG1_PNG = FIG_ROOT / "fig1_kappa_continuation.png"
FIG1_PDF = FIG_ROOT / "fig1_kappa_continuation.pdf"
FIG2_PNG = FIG_ROOT / "fig2_fully_reflective_overall_distribution.png"
FIG2_PDF = FIG_ROOT / "fig2_fully_reflective_overall_distribution.pdf"
FIG3_PNG = FIG_ROOT / "fig3_tau_out_timing.png"
FIG3_PDF = FIG_ROOT / "fig3_tau_out_timing.pdf"
FIG4_PNG = FIG_ROOT / "fig4_tau_mem_timing.png"
FIG4_PDF = FIG_ROOT / "fig4_tau_mem_timing.pdf"
FIG5_PNG = FIG_ROOT / "fig5_tau_out_split.png"
FIG5_PDF = FIG_ROOT / "fig5_tau_out_split.pdf"
FIG6_PNG = FIG_ROOT / "fig6_tau_mem_split.png"
FIG6_PDF = FIG_ROOT / "fig6_tau_mem_split.pdf"
FIG7_PNG = FIG_ROOT / "fig7_takeover_before_collapse.png"
FIG7_PDF = FIG_ROOT / "fig7_takeover_before_collapse.pdf"
FIG8_PNG = FIG_ROOT / "fig8_critical_collapse_curves.png"
FIG8_PDF = FIG_ROOT / "fig8_critical_collapse_curves.pdf"


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


def fmt_kappa(kappa: float) -> str:
    return f"{kappa:.4f}"


def build_case(kappa: float) -> dict[str, Any]:
    base_args = dict(report_mod.ONE_TARGET_BASE_ARGS)
    base_args.pop("delta_core", None)
    base_args.pop("delta_open", None)
    case = build_membrane_case_directional(
        **base_args,
        delta_core=float(DELTA_CORE),
        delta_open=float(DELTA_OPEN),
        kappa_c2o=float(kappa),
        kappa_o2c=float(kappa),
        t_max_total=int(REP_T_MAX),
    )
    case["case_name"] = f"kappa_{fmt_kappa(float(kappa))}"
    case["display_name"] = f"kappa={fmt_kappa(float(kappa))}"
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


def _event_state_mask_outside(case: dict[str, Any]) -> np.ndarray:
    return ~np.asarray(case["channel_mask"], dtype=bool)


def _event_edge_pairs_membrane(case: dict[str, Any]) -> set[tuple[int, int]]:
    lx = int(case["Lx"])
    return {
        (int(a[1]) * lx + int(a[0]), int(b[1]) * lx + int(b[0]))
        for a, b in case.get("membrane_c2o_edges", set())
    }


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


def compute_region_summary(case: dict[str, Any], occ_grid: np.ndarray) -> list[dict[str, Any]]:
    masks = region_masks(case)
    rows: list[dict[str, Any]] = []
    for region in REGION_ORDER:
        vals = occ_grid[masks[region]]
        rows.append(
            {
                "case": str(case["case_name"]),
                "display_name": str(case["display_name"]),
                "region": region,
                "region_label": REGION_LABELS[region],
                "occupancy_share": float(np.sum(vals)),
                "mean_cell_occupancy": float(np.mean(vals)) if vals.size else 0.0,
                "max_cell_occupancy": float(np.max(vals)) if vals.size else 0.0,
            }
        )
    return rows


def _split_event_masses(stat: dict[str, Any]) -> tuple[float, float, float]:
    mean_hit = float(stat["mean_hit_time_in_window"])
    density = np.asarray(stat["conditional_density"], dtype=np.float64)
    if not np.isfinite(mean_hit):
        return 0.0, 0.0, 1.0
    threshold = 0.5 * mean_hit
    ts = np.arange(len(density), dtype=np.float64)
    early_mass = float(np.sum(density[ts <= threshold]))
    exit_prob = float(stat["event_probability"])
    late_mass = max(0.0, exit_prob - early_mass)
    no_exit_mass = max(0.0, 1.0 - exit_prob)
    return early_mass, late_mass, no_exit_mass


def _nan_to_zero(value: float) -> float:
    return 0.0 if not np.isfinite(value) else float(value)


def _lookup_window_exit_prob(stats_map: dict[str, dict[str, Any]], window_name: str) -> float:
    stat = stats_map.get(str(window_name))
    if stat is None:
        return float("nan")
    return float(stat["event_probability"])


def build_scan_products() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[float, dict[str, Any]]]:
    summary_rows: list[dict[str, Any]] = []
    rep_curve_rows: list[dict[str, Any]] = []
    rep_cases: dict[float, dict[str, Any]] = {}

    for kappa in SCAN_EVAL_KAPPAS:
        case = build_case(kappa)
        windows = window_ranges(case["res"].t_peak1, case["res"].t_valley, case["res"].t_peak2, len(case["f_total"]))
        tau_out = compute_one_target_first_event_statistics(
            case,
            Lx=int(case["Lx"]),
            windows=windows,
            event_state_mask=_event_state_mask_outside(case),
        )
        tau_mem = compute_one_target_first_event_statistics(
            case,
            Lx=int(case["Lx"]),
            windows=windows,
            event_edge_pairs=_event_edge_pairs_membrane(case),
        )
        if any(abs(float(kappa) - float(rep)) < 1.0e-12 for rep in REPRESENTATIVE_KAPPAS):
            rep_cases[float(kappa)] = {
                "case": case,
                "windows": windows,
                "tau_out": tau_out,
                "tau_mem": tau_mem,
            }

        for observable, stats_map in (("tau_out", tau_out), ("tau_mem", tau_mem)):
            for window_name, _lo, _hi in windows:
                stat = stats_map[window_name]
                early_mass, late_mass, no_exit_mass = _split_event_masses(stat)
                mean_event_time = float(stat["mean_event_time_given_event"])
                mean_hit_time = float(stat["mean_hit_time_in_window"])
                ratio = float("nan")
                if np.isfinite(mean_event_time) and np.isfinite(mean_hit_time) and mean_hit_time > 0.0:
                    ratio = mean_event_time / mean_hit_time
                summary_rows.append(
                    {
                        "kappa": float(kappa),
                        "window": window_name,
                        "observable": observable,
                        "exit_prob": float(stat["event_probability"]),
                        "mean_event_time": mean_event_time,
                        "mean_hit_time": mean_hit_time,
                        "ratio": ratio,
                        "early_mass": early_mass,
                        "late_mass": late_mass,
                        "no_exit_mass": no_exit_mass,
                        "phase": int(case["res"].phase),
                        "sep_peaks": float(case["res"].sep_peaks),
                        "t_peak1": int(case["res"].t_peak1),
                        "t_valley": int(case["res"].t_valley),
                        "t_peak2": int(case["res"].t_peak2),
                    }
                )

        if float(kappa) in rep_cases:
            for observable, stats_map in (("tau_out", tau_out), ("tau_mem", tau_mem)):
                for window_name in WINDOW_ORDER:
                    stat = stats_map[window_name]
                    cdf = np.asarray(stat["conditional_cdf"], dtype=np.float64)
                    density = np.asarray(stat["conditional_density"], dtype=np.float64)
                    t_cap = min(len(cdf) - 1, int(REP_CURVE_T_MAX))
                    for t in range(t_cap + 1):
                        rep_curve_rows.append(
                            {
                                "kappa": float(kappa),
                                "observable": observable,
                                "window": window_name,
                                "t": int(t),
                                "conditional_density": float(density[t]),
                                "conditional_cdf": float(cdf[t]),
                            }
                        )

    return summary_rows, rep_curve_rows, rep_cases


def build_critical_takeover_scan() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for kappa in CRITICAL_KAPPAS:
        case = build_case(kappa)
        windows = window_ranges(case["res"].t_peak1, case["res"].t_valley, case["res"].t_peak2, len(case["f_total"]))
        tau_out = compute_one_target_first_event_statistics(
            case,
            Lx=int(case["Lx"]),
            windows=windows,
            event_state_mask=_event_state_mask_outside(case),
        )
        tau_mem = compute_one_target_first_event_statistics(
            case,
            Lx=int(case["Lx"]),
            windows=windows,
            event_edge_pairs=_event_edge_pairs_membrane(case),
        )
        rows.append(
            {
                "kappa": float(kappa),
                "phase": int(case["res"].phase),
                "sep_peaks": float(case["res"].sep_peaks),
                "t_peak1": (None if case["res"].t_peak1 is None else int(case["res"].t_peak1)),
                "t_valley": (None if case["res"].t_valley is None else int(case["res"].t_valley)),
                "t_peak2": (None if case["res"].t_peak2 is None else int(case["res"].t_peak2)),
                "tau_mem_peak1": _lookup_window_exit_prob(tau_mem, "peak1"),
                "tau_mem_valley": _lookup_window_exit_prob(tau_mem, "valley"),
                "tau_mem_peak2": _lookup_window_exit_prob(tau_mem, "peak2"),
                "tau_out_peak2": _lookup_window_exit_prob(tau_out, "peak2"),
            }
        )
    return rows


def build_critical_curve_profiles() -> tuple[list[dict[str, Any]], dict[float, dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    case_map: dict[float, dict[str, Any]] = {}
    for kappa in CRITICAL_CURVE_KAPPAS:
        case = build_case(kappa)
        case_map[float(kappa)] = case
        f_s = smooth_series_display(np.asarray(case["f_total"], dtype=np.float64), window=7)
        t_cap = min(len(f_s) - 1, 3000)
        for t in range(t_cap + 1):
            rows.append(
                {
                    "kappa": float(kappa),
                    "t": int(t),
                    "smoothed_f": float(f_s[t]),
                    "phase": int(case["res"].phase),
                    "t_peak1": (None if case["res"].t_peak1 is None else int(case["res"].t_peak1)),
                    "t_valley": (None if case["res"].t_valley is None else int(case["res"].t_valley)),
                    "t_peak2": (None if case["res"].t_peak2 is None else int(case["res"].t_peak2)),
                }
            )
    return rows, case_map


def write_representative_table(rows: list[dict[str, Any]]) -> None:
    reps = list(REPRESENTATIVE_KAPPAS)
    lines = [
        r"\begin{tabular}{llcccc}",
        r"\toprule",
        r"$\kappa$ & Observable & peak1 exit & valley exit & peak2 exit & peak2 ratio \\",
        r"\midrule",
    ]
    for kappa in reps:
        for observable, label in (("tau_out", r"$\tau_{\mathrm{out}}$"), ("tau_mem", r"$\tau_{\mathrm{mem}}$")):
            case_rows = [row for row in rows if abs(float(row["kappa"]) - kappa) < 1.0e-12 and str(row["observable"]) == observable]
            lookup = {str(row["window"]): row for row in case_rows}
            peak2_ratio = _nan_to_zero(float(lookup["peak2"]["ratio"]))
            lines.append(
                f"{kappa:.4f} & {label} & {100.0 * float(lookup['peak1']['exit_prob']):.1f}\\% & "
                f"{100.0 * float(lookup['valley']['exit_prob']):.1f}\\% & "
                f"{100.0 * float(lookup['peak2']['exit_prob']):.1f}\\% & "
                f"{peak2_ratio:.2f} \\\\"
            )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    ensure_dir(TABLE_ROOT)
    REP_OVERVIEW_TEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_kappa_continuation(summary_rows: list[dict[str, Any]], rep_cases: dict[float, dict[str, Any]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8), gridspec_kw={"width_ratios": [1.25, 1.0]})
    ax_curve, ax_scan = axes

    x_max = 4000
    colors = {0.0: "#424242", 0.0140: "#fb8c00", 0.0152: "#1565c0"}
    for kappa in REPRESENTATIVE_KAPPAS:
        case = rep_cases[float(kappa)]["case"]
        f_s = smooth_series_display(np.asarray(case["f_total"], dtype=np.float64), window=7)
        t = np.arange(min(len(f_s), x_max + 1), dtype=np.int64)
        ax_curve.plot(t, f_s[: len(t)], lw=2.0, color=colors[float(kappa)], label=rf"$\kappa={kappa:.4f}$")
        for window_name, lo, hi in rep_cases[float(kappa)]["windows"]:
            if window_name not in WINDOW_ORDER:
                continue
            ax_curve.axvspan(lo, hi, color=WINDOW_COLORS[window_name], alpha=0.06)
    ax_curve.set_xlim(0, x_max)
    ax_curve.set_xlabel("t")
    ax_curve.set_ylabel("smoothed first-passage pmf")
    ax_curve.set_title("Representative $f(t)$ curves", fontsize=11)
    ax_curve.grid(alpha=0.22)
    ax_curve.legend(frameon=False, fontsize=8.5, loc="upper right")

    kappas = np.asarray(sorted({float(row["kappa"]) for row in summary_rows}), dtype=np.float64)
    sep_vals = np.asarray(
        [next(float(row["sep_peaks"]) for row in summary_rows if float(row["kappa"]) == k and str(row["observable"]) == "tau_out" and str(row["window"]) == "peak1") for k in kappas],
        dtype=np.float64,
    )
    phase_vals = np.asarray(
        [next(float(row["phase"]) for row in summary_rows if float(row["kappa"]) == k and str(row["observable"]) == "tau_out" and str(row["window"]) == "peak1") for k in kappas],
        dtype=np.float64,
    )
    peak2_out = np.asarray(
        [next(float(row["exit_prob"]) for row in summary_rows if float(row["kappa"]) == k and str(row["observable"]) == "tau_out" and str(row["window"]) == "peak2") for k in kappas],
        dtype=np.float64,
    )
    peak2_mem = np.asarray(
        [next(float(row["exit_prob"]) for row in summary_rows if float(row["kappa"]) == k and str(row["observable"]) == "tau_mem" and str(row["window"]) == "peak2") for k in kappas],
        dtype=np.float64,
    )
    ax_scan.plot(kappas, sep_vals, marker="o", lw=2.0, color="#111111", label="sep_peaks")
    ax_scan.plot(kappas, peak2_out, marker="o", lw=2.0, color=EVENT_COLORS["tau_out"], label=r"$P(\tau_{\mathrm{out}}<T \mid T\in\mathrm{peak2})$")
    ax_scan.plot(kappas, peak2_mem, marker="o", lw=2.0, color=EVENT_COLORS["tau_mem"], label=r"$P(\tau_{\mathrm{mem}}<T \mid T\in\mathrm{peak2})$")
    ax_scan.set_xlabel(r"$\kappa$")
    ax_scan.tick_params(axis="x", rotation=30)
    ax_scan.set_ylabel("probability / separation score")
    ax_scan.set_ylim(0.0, max(1.02, float(np.max(sep_vals)) + 0.08))
    ax_scan.grid(alpha=0.22)
    ax_phase = ax_scan.twinx()
    ax_phase.plot(kappas, phase_vals, linestyle="none", marker="s", ms=5.0, color="#8e24aa", label="phase")
    ax_phase.set_ylabel("phase")
    ax_phase.set_ylim(-0.1, 2.1)
    ax_phase.set_yticks([0, 1, 2])
    handles1, labels1 = ax_scan.get_legend_handles_labels()
    handles2, labels2 = ax_phase.get_legend_handles_labels()
    ax_scan.legend(handles1 + handles2, labels1 + labels2, frameon=False, fontsize=7.9, loc="upper left")
    ax_scan.set_title(r"Continuation: $\kappa \mapsto$ peak separation and late-window exits", fontsize=11)

    fig.suptitle("Fig. 1  Symmetric soft-corridor baseline under symmetric membrane continuation", fontsize=12.5, y=0.99)
    fig.tight_layout()
    ensure_dir(FIG_ROOT)
    fig.savefig(FIG1_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIG1_PDF, bbox_inches="tight")
    plt.close(fig)


def plot_fully_reflective_overall(case: dict[str, Any], occ_grid: np.ndarray, region_rows: list[dict[str, Any]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.8, 4.8), gridspec_kw={"width_ratios": [1.35, 1.0]})
    ax_heat, ax_bar = axes
    im = ax_heat.imshow(occ_grid, origin="lower", cmap="magma", aspect="auto")
    cbar = fig.colorbar(im, ax=ax_heat, fraction=0.046, pad=0.03)
    cbar.set_label("normalized pre-hit occupancy")
    start = case["start"]
    target = case["target"]
    _y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    ax_heat.scatter([start[0]], [start[1]], s=62, color="#2e7d32", edgecolors="white", linewidths=0.9, marker="o", label="start", zorder=5)
    ax_heat.scatter([target[0]], [target[1]], s=86, facecolors="white", edgecolors="#111111", linewidths=1.0, marker="*", label="target", zorder=5)
    ax_heat.hlines([y_low - 0.5, y_high + 0.5], xmin=x0 - 0.5, xmax=x1 + 0.5, colors="white", linestyles="--", linewidth=1.15)
    ax_heat.text(
        0.02,
        0.98,
        r"$\kappa=0$: no membrane crossing, but the left opening still allows outside detours",
        transform=ax_heat.transAxes,
        ha="left",
        va="top",
        fontsize=8.8,
        color="white",
        bbox=dict(facecolor="black", alpha=0.28, edgecolor="none", pad=2.0),
    )
    ax_heat.set_title("Fully reflective control: long-horizon occupancy heatmap", fontsize=11)
    ax_heat.set_xlabel("x")
    ax_heat.set_ylabel("y")
    ax_heat.legend(loc="upper right", frameon=False, fontsize=8.4)

    vals = np.asarray([float(next(row["occupancy_share"] for row in region_rows if row["region"] == region)) for region in REGION_ORDER], dtype=np.float64)
    ax_bar.bar(np.arange(len(REGION_ORDER)), vals, color=[REGION_COLORS[r] for r in REGION_ORDER], alpha=0.92)
    for i, val in enumerate(vals):
        ax_bar.text(i, val + 0.008, f"{100.0 * val:.1f}%", ha="center", va="bottom", fontsize=8.5)
    ax_bar.set_xticks(np.arange(len(REGION_ORDER)))
    ax_bar.set_xticklabels(["Left\ncore", "Left\nshoulders", "Left\nouter", "Corridor", "Outer\nreservoir", "Target\nfunnel"], fontsize=8.4)
    ax_bar.set_ylabel("share of total pre-hit occupancy")
    ax_bar.set_ylim(0.0, max(0.36, float(np.max(vals)) + 0.06))
    ax_bar.grid(axis="y", alpha=0.22)
    ax_bar.set_title("Region-level overall composition", fontsize=11)

    fig.suptitle("Fig. 2  Fully reflective control still supports a slow branch without membrane crossing", fontsize=12.5, y=0.99)
    fig.tight_layout()
    fig.savefig(FIG2_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIG2_PDF, bbox_inches="tight")
    plt.close(fig)


def plot_event_timing(
    *,
    observable: str,
    case_panels: list[float],
    rep_cases: dict[float, dict[str, Any]],
    output_png: Path,
    output_pdf: Path,
    figure_title: str,
) -> None:
    n_case_panels = len(case_panels)
    fig, axes = plt.subplots(1, n_case_panels + 1, figsize=(4.8 * (n_case_panels + 1), 4.6), gridspec_kw={"width_ratios": [1.0] * n_case_panels + [0.95]})
    if not isinstance(axes, np.ndarray):
        axes = np.asarray([axes])

    if observable == "tau_mem":
        max_exit_prob = max(
            float(rep_cases[float(kappa)][observable][window_name]["event_probability"])
            for kappa in case_panels
            for window_name in WINDOW_ORDER
        )
        cdf_ylim = min(1.02, max(0.15, 0.05 * math.ceil((1.18 * max_exit_prob) / 0.05)))
        max_ratio = max(
            _nan_to_zero(
                float(rep_cases[float(kappa)][observable][window_name]["mean_event_time_given_event"])
                / float(rep_cases[float(kappa)][observable][window_name]["mean_hit_time_in_window"])
            )
            if float(rep_cases[float(kappa)][observable][window_name]["event_probability"]) > 0.0 else 0.0
            for kappa in case_panels
            for window_name in WINDOW_ORDER
        )
        ratio_ylim = min(1.02, max(0.25, 0.05 * math.ceil((1.18 * max_ratio) / 0.05)))
    else:
        cdf_ylim = 1.02
        ratio_ylim = 1.02

    for ax, kappa in zip(axes[:-1], case_panels, strict=False):
        stats_map = rep_cases[float(kappa)][observable]
        for window_name in WINDOW_ORDER:
            stat = stats_map[window_name]
            cdf = np.asarray(stat["conditional_cdf"], dtype=np.float64)
            t_cap = min(len(cdf) - 1, int(REP_CURVE_T_MAX))
            xs = np.arange(t_cap + 1, dtype=np.int64)
            ax.plot(xs, cdf[: t_cap + 1], lw=2.0, color=WINDOW_COLORS[window_name], label=window_name)
            ax.text(
                0.98,
                {"peak1": 0.92, "valley": 0.83, "peak2": 0.74}[window_name],
                f"{window_name}: exit={100.0 * float(stat['event_probability']):.1f}%",
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=8.1,
                color=WINDOW_COLORS[window_name],
                bbox=dict(facecolor="white", alpha=0.82, edgecolor="none", pad=0.8),
            )
        ax.set_title(rf"$\kappa={kappa:.4f}$", fontsize=11)
        ax.set_xlabel("t")
        ax.set_ylim(0.0, cdf_ylim)
        ax.grid(alpha=0.22)
    axes[0].set_ylabel(
        r"$P(\tau_{\mathrm{out}} \leq t \mid T\in W)$"
        if observable == "tau_out"
        else r"$P(\tau_{\mathrm{mem}} \leq t \mid T\in W)$ (zoomed)"
    )

    ax_ratio = axes[-1]
    bar_width = 0.22
    x = np.arange(len(WINDOW_ORDER), dtype=np.float64)
    for offset_idx, kappa in enumerate(case_panels):
        ratios = np.asarray(
            [
                _nan_to_zero(float(rep_cases[float(kappa)][observable][window_name]["mean_event_time_given_event"]) / float(rep_cases[float(kappa)][observable][window_name]["mean_hit_time_in_window"]))
                if float(rep_cases[float(kappa)][observable][window_name]["event_probability"]) > 0.0 else 0.0
                for window_name in WINDOW_ORDER
            ],
            dtype=np.float64,
        )
        positions = x + (offset_idx - 0.5 * (len(case_panels) - 1)) * bar_width
        ax_ratio.bar(positions, ratios, width=bar_width, alpha=0.88, label=rf"$\kappa={kappa:.4f}$")
        for pos, ratio, window_name in zip(positions, ratios, WINDOW_ORDER, strict=False):
            ax_ratio.text(pos, ratio + 0.02, f"{ratio:.2f}", ha="center", va="bottom", fontsize=8.2, color="#222222")
            event_prob = float(rep_cases[float(kappa)][observable][window_name]["event_probability"])
            ax_ratio.text(pos, 0.04 + 0.03 * offset_idx, f"{100.0 * event_prob:.1f}%", ha="center", va="bottom", fontsize=7.4, color=WINDOW_COLORS[window_name])
    ax_ratio.set_xticks(x)
    ax_ratio.set_xticklabels(WINDOW_ORDER)
    ax_ratio.set_ylim(0.0, ratio_ylim)
    ax_ratio.grid(axis="y", alpha=0.22)
    ax_ratio.set_ylabel("relative timing ratio")
    ax_ratio.set_title("Relative timing ratio" if observable == "tau_out" else "Relative timing ratio (zoomed)", fontsize=11)
    ax_ratio.legend(frameon=False, fontsize=8)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False)
    fig.suptitle(figure_title, fontsize=12.5, y=1.05)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
    fig.savefig(output_png, dpi=180, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def plot_event_split(
    *,
    observable: str,
    case_panels: list[float],
    summary_rows: list[dict[str, Any]],
    output_png: Path,
    output_pdf: Path,
    figure_title: str,
) -> None:
    fig, axes = plt.subplots(1, len(case_panels), figsize=(5.1 * len(case_panels), 4.2), sharey=True)
    if len(case_panels) == 1:
        axes = [axes]
    for ax, kappa in zip(axes, case_panels, strict=False):
        case_rows = [row for row in summary_rows if abs(float(row["kappa"]) - float(kappa)) < 1.0e-12 and str(row["observable"]) == observable]
        x = np.arange(len(WINDOW_ORDER), dtype=np.int64)
        early = np.asarray([float(next(row["early_mass"] for row in case_rows if str(row["window"]) == w)) for w in WINDOW_ORDER], dtype=np.float64)
        late = np.asarray([float(next(row["late_mass"] for row in case_rows if str(row["window"]) == w)) for w in WINDOW_ORDER], dtype=np.float64)
        no_exit = np.asarray([float(next(row["no_exit_mass"] for row in case_rows if str(row["window"]) == w)) for w in WINDOW_ORDER], dtype=np.float64)
        ax.bar(x, early, color=SPLIT_COLORS["early"], label="early")
        ax.bar(x, late, bottom=early, color=SPLIT_COLORS["late"], label="late")
        ax.bar(x, no_exit, bottom=early + late, color=SPLIT_COLORS["no_exit"], label="no exit")
        for i in range(len(WINDOW_ORDER)):
            ax.text(i, 1.01, f"{100.0 * (early[i] + late[i]):.1f}%", ha="center", va="bottom", fontsize=8.2)
        ax.set_xticks(x)
        ax.set_xticklabels(WINDOW_ORDER)
        ax.set_ylim(0.0, 1.08)
        ax.grid(axis="y", alpha=0.22)
        ax.set_title(rf"$\kappa={kappa:.4f}$", fontsize=11)
    axes[0].set_ylabel("window-conditioned mass")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.04), ncol=3, frameon=False)
    fig.suptitle(figure_title, fontsize=12.5, y=1.06)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.93))
    fig.savefig(output_png, dpi=180, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def _first_kappa_where(rows: list[dict[str, Any]], predicate: Any) -> float | None:
    for row in rows:
        if predicate(row):
            return float(row["kappa"])
    return None


def plot_takeover_before_collapse(rows: list[dict[str, Any]]) -> None:
    kappas = np.asarray([float(row["kappa"]) for row in rows], dtype=np.float64)
    tau_mem_peak1 = np.asarray([float(row["tau_mem_peak1"]) for row in rows], dtype=np.float64)
    tau_mem_valley = np.asarray([float(row["tau_mem_valley"]) for row in rows], dtype=np.float64)
    tau_mem_peak2 = np.asarray([float(row["tau_mem_peak2"]) for row in rows], dtype=np.float64)
    sep_vals = np.asarray([float(row["sep_peaks"]) for row in rows], dtype=np.float64)
    phase_vals = np.asarray([float(row["phase"]) for row in rows], dtype=np.float64)

    takeover_kappa = _first_kappa_where(
        rows,
        lambda row: int(row["phase"]) == 1 and np.isfinite(float(row["tau_mem_peak2"])) and float(row["tau_mem_peak2"]) >= 0.5,
    )
    collapse_kappa = _first_kappa_where(rows, lambda row: int(row["phase"]) == 0)

    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.7), gridspec_kw={"width_ratios": [1.05, 1.0]})
    ax_left, ax_right = axes

    ax_left.plot(kappas, tau_mem_peak1, marker="o", lw=2.0, color=WINDOW_COLORS["peak1"], label=r"$P(\tau_{\mathrm{mem}}<T\mid T\in\mathrm{peak1})$")
    ax_left.plot(kappas, tau_mem_valley, marker="o", lw=2.0, color=WINDOW_COLORS["valley"], label=r"$P(\tau_{\mathrm{mem}}<T\mid T\in\mathrm{valley})$")
    ax_left.plot(kappas, tau_mem_peak2, marker="o", lw=2.0, color=WINDOW_COLORS["peak2"], label=r"$P(\tau_{\mathrm{mem}}<T\mid T\in\mathrm{peak2})$")
    ax_left.axhline(0.5, color="#555555", lw=1.1, ls="--", alpha=0.85)
    ax_left.text(kappas[0], 0.515, "50% takeover threshold", ha="left", va="bottom", fontsize=8.2, color="#444444")
    ax_left.set_xlabel(r"$\kappa$")
    ax_left.set_ylabel("window-conditioned membrane-exit probability")
    ax_left.set_ylim(0.0, 1.02)
    ax_left.tick_params(axis="x", rotation=30)
    ax_left.grid(alpha=0.22)
    ax_left.set_title(r"Membrane-exit share in the critical band", fontsize=11)

    ax_right.plot(kappas, sep_vals, marker="o", lw=2.0, color="#111111", label="sep_peaks")
    ax_right.set_xlabel(r"$\kappa$")
    ax_right.set_ylabel("sep_peaks")
    ax_right.tick_params(axis="x", rotation=30)
    ax_right.grid(alpha=0.22)
    ax_right.set_title("Peak separation and phase collapse", fontsize=11)
    ax_phase = ax_right.twinx()
    ax_phase.plot(kappas, phase_vals, linestyle="none", marker="s", ms=5.5, color="#8e24aa", label="phase")
    ax_phase.set_ylabel("phase")
    ax_phase.set_ylim(-0.1, 2.1)
    ax_phase.set_yticks([0, 1, 2])

    if takeover_kappa is not None:
        for ax in (ax_left, ax_right):
            ax.axvline(takeover_kappa, color="#1565c0", lw=1.15, ls="--", alpha=0.9)
        ax_left.text(takeover_kappa, 0.08, rf"takeover at $\kappa\approx {takeover_kappa:.4f}$", rotation=90, ha="left", va="bottom", fontsize=8.1, color="#1565c0")
    if collapse_kappa is not None:
        for ax in (ax_left, ax_right):
            ax.axvline(collapse_kappa, color="#c62828", lw=1.15, ls=":", alpha=0.95)
        ax_right.text(collapse_kappa, float(np.nanmax(sep_vals)) * 0.72, rf"phase=0 at $\kappa\approx {collapse_kappa:.4f}$", rotation=90, ha="left", va="bottom", fontsize=8.1, color="#c62828")
    if takeover_kappa is not None and collapse_kappa is not None and collapse_kappa > takeover_kappa:
        for ax in (ax_left, ax_right):
            ax.axvspan(takeover_kappa, collapse_kappa, color="#6a1b9a", alpha=0.07)

    handles1, labels1 = ax_left.get_legend_handles_labels()
    handles2, labels2 = ax_right.get_legend_handles_labels()
    handles3, labels3 = ax_phase.get_legend_handles_labels()
    fig.legend(handles1 + handles2 + handles3, labels1 + labels2 + labels3, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=3, frameon=False, fontsize=8.2)
    fig.suptitle("Fig. 7  Membrane takeover occurs only in a narrow pre-collapse band", fontsize=12.5, y=1.04)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))
    fig.savefig(FIG7_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIG7_PDF, bbox_inches="tight")
    plt.close(fig)


def plot_critical_collapse_curves(case_map: dict[float, dict[str, Any]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8), gridspec_kw={"width_ratios": [1.2, 1.0]})
    ax_full, ax_zoom = axes
    colors = {
        0.0140: "#1565c0",
        0.0152: "#00897b",
        0.0153: "#c62828",
    }
    labels = {
        0.0140: r"$\kappa=0.0140$ (takeover onset, phase=1)",
        0.0152: r"$\kappa=0.0152$ (last phase=1)",
        0.0153: r"$\kappa=0.0153$ (first phase=0)",
    }
    full_xmax = 2800
    zoom_lo = 1100
    zoom_hi = 2350
    zoom_ymax = 0.0
    for kappa in CRITICAL_CURVE_KAPPAS:
        case = case_map[float(kappa)]
        f_s = smooth_series_display(np.asarray(case["f_total"], dtype=np.float64), window=7)
        xs = np.arange(min(len(f_s), full_xmax + 1), dtype=np.int64)
        ax_full.plot(xs, f_s[: len(xs)], lw=2.2, color=colors[float(kappa)], label=labels[float(kappa)])
        z_hi = min(len(f_s), zoom_hi + 1)
        z_xs = np.arange(zoom_lo, z_hi, dtype=np.int64)
        ax_zoom.plot(z_xs, f_s[zoom_lo:z_hi], lw=2.2, color=colors[float(kappa)], label=labels[float(kappa)])
        if z_hi > zoom_lo:
            zoom_ymax = max(zoom_ymax, float(np.max(f_s[zoom_lo:z_hi])))

    last_phase1 = case_map[0.0152]["res"]
    if last_phase1.t_peak1 is not None and last_phase1.t_valley is not None and last_phase1.t_peak2 is not None:
        for t_mark, name in (
            (int(last_phase1.t_peak1), "peak1"),
            (int(last_phase1.t_valley), "valley"),
            (int(last_phase1.t_peak2), "peak2"),
        ):
            ax_zoom.axvline(t_mark, color="#00897b", lw=1.0, ls="--", alpha=0.55)
            ax_zoom.text(t_mark, zoom_ymax * {"peak1": 0.98, "valley": 0.82, "peak2": 0.66}[name], name, rotation=90, ha="right", va="top", fontsize=8.0, color="#00695c")

    ax_full.set_xlim(0, full_xmax)
    ax_full.set_xlabel("t")
    ax_full.set_ylabel("smoothed first-passage pmf")
    ax_full.set_title("Critical-point profiles: full view", fontsize=11)
    ax_full.grid(alpha=0.22)

    ax_zoom.set_xlim(zoom_lo, zoom_hi)
    ax_zoom.set_ylim(0.0, zoom_ymax * 1.08 if zoom_ymax > 0.0 else 1.0)
    ax_zoom.set_xlabel("t")
    ax_zoom.set_title("Late-window zoom around the collapse threshold", fontsize=11)
    ax_zoom.grid(alpha=0.22)
    ax_zoom.text(
        0.98,
        0.95,
        "The last detectable double peak\nmerges into a single broad hump",
        transform=ax_zoom.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        bbox=dict(facecolor="white", alpha=0.82, edgecolor="none", pad=1.0),
    )

    handles, labels_h = ax_full.get_legend_handles_labels()
    fig.legend(handles, labels_h, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=3, frameon=False, fontsize=8.3)
    fig.suptitle("Fig. 8  The collapse threshold in the smoothed first-passage curves", fontsize=12.5, y=1.05)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.93))
    fig.savefig(FIG8_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIG8_PDF, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    summary_rows, rep_curve_rows, rep_cases = build_scan_products()
    critical_rows = build_critical_takeover_scan()
    critical_curve_rows, critical_curve_cases = build_critical_curve_profiles()
    full_reflective_case = rep_cases[0.0]["case"]
    overall_occ = compute_overall_occupancy(full_reflective_case)
    overall_region_rows = compute_region_summary(full_reflective_case, overall_occ)

    write_csv(
        SCAN_SUMMARY_CSV,
        summary_rows,
        [
            "kappa",
            "window",
            "observable",
            "exit_prob",
            "mean_event_time",
            "mean_hit_time",
            "ratio",
            "early_mass",
            "late_mass",
            "no_exit_mass",
            "phase",
            "sep_peaks",
            "t_peak1",
            "t_valley",
            "t_peak2",
        ],
    )
    write_csv(
        REP_CDF_CSV,
        rep_curve_rows,
        ["kappa", "observable", "window", "t", "conditional_density", "conditional_cdf"],
    )
    write_csv(
        FULLY_REFLECTIVE_REGION_CSV,
        overall_region_rows,
        ["case", "display_name", "region", "region_label", "occupancy_share", "mean_cell_occupancy", "max_cell_occupancy"],
    )
    write_csv(
        CRITICAL_SCAN_CSV,
        critical_rows,
        ["kappa", "phase", "sep_peaks", "t_peak1", "t_valley", "t_peak2", "tau_mem_peak1", "tau_mem_valley", "tau_mem_peak2", "tau_out_peak2"],
    )
    write_csv(
        CRITICAL_CURVE_CSV,
        critical_curve_rows,
        ["kappa", "t", "smoothed_f", "phase", "t_peak1", "t_valley", "t_peak2"],
    )
    takeover_kappa = _first_kappa_where(
        critical_rows,
        lambda row: int(row["phase"]) == 1 and np.isfinite(float(row["tau_mem_peak2"])) and float(row["tau_mem_peak2"]) >= 0.5,
    )
    collapse_kappa = _first_kappa_where(critical_rows, lambda row: int(row["phase"]) == 0)
    write_json(
        SCAN_METADATA_JSON,
        {
            "case_title": CASE_TITLE,
            "geometry": {
                "Lx": int(full_reflective_case["Lx"]),
                "Wy": int(full_reflective_case["Wy"]),
                "start": list(full_reflective_case["start"]),
                "target": list(full_reflective_case["target"]),
                "wall_span": list(full_reflective_case["wall_span"]),
                "bx": float(full_reflective_case["bx"]),
                "delta_core": float(full_reflective_case["delta_core"]),
                "delta_open": float(full_reflective_case["delta_open"]),
                "t_max": int(REP_T_MAX),
            },
            "kappa_values": KAPPA_VALUES,
            "representative_kappas": REPRESENTATIVE_KAPPAS,
            "critical_kappa_values": CRITICAL_KAPPAS,
            "critical_curve_kappas": CRITICAL_CURVE_KAPPAS,
            "timing_observables": {
                "tau_out": "first time the walker leaves the corridor band and enters any outside state",
                "tau_mem": "first time the walker crosses a membrane c->o edge",
            },
            "early_late_rule": r"early if \tau \le 0.5 E[T | T \in W], late otherwise",
            "fully_reflective_survival_tail": float(full_reflective_case["surv"][-1]),
            "critical_band": {
                "takeover_threshold_kappa": takeover_kappa,
                "collapse_threshold_kappa": collapse_kappa,
                "definition": "takeover = first phase-1 kappa with P(tau_mem < T | T in peak2) >= 0.5; collapse = first kappa with phase = 0",
            },
        },
    )
    write_representative_table(summary_rows)

    plot_kappa_continuation(summary_rows, rep_cases)
    plot_fully_reflective_overall(full_reflective_case, overall_occ, overall_region_rows)
    plot_event_timing(
        observable="tau_out",
        case_panels=list(REPRESENTATIVE_KAPPAS),
        rep_cases=rep_cases,
        output_png=FIG3_PNG,
        output_pdf=FIG3_PDF,
        figure_title=r"Fig. 3  $\tau_{\mathrm{out}}$: first time the walker leaves the corridor band",
    )
    plot_event_timing(
        observable="tau_mem",
        case_panels=list(REPRESENTATIVE_KAPPAS),
        rep_cases=rep_cases,
        output_png=FIG4_PNG,
        output_pdf=FIG4_PDF,
        figure_title=r"Fig. 4  $\tau_{\mathrm{mem}}$: first membrane crossing to the outside",
    )
    plot_event_split(
        observable="tau_out",
        case_panels=list(REPRESENTATIVE_KAPPAS),
        summary_rows=summary_rows,
        output_png=FIG5_PNG,
        output_pdf=FIG5_PDF,
        figure_title=r"Fig. 5  $\tau_{\mathrm{out}}$ split into early / late / no-exit mass",
    )
    plot_event_split(
        observable="tau_mem",
        case_panels=list(REPRESENTATIVE_KAPPAS),
        summary_rows=summary_rows,
        output_png=FIG6_PNG,
        output_pdf=FIG6_PDF,
        figure_title=r"Fig. 6  $\tau_{\mathrm{mem}}$ split into early / late / no-exit mass",
    )
    plot_takeover_before_collapse(critical_rows)
    plot_critical_collapse_curves(critical_curve_cases)

    for path in [
        SCAN_SUMMARY_CSV,
        REP_CDF_CSV,
        FULLY_REFLECTIVE_REGION_CSV,
        CRITICAL_SCAN_CSV,
        CRITICAL_CURVE_CSV,
        SCAN_METADATA_JSON,
        REP_OVERVIEW_TEX,
        FIG1_PNG,
        FIG1_PDF,
        FIG2_PNG,
        FIG2_PDF,
        FIG3_PNG,
        FIG3_PDF,
        FIG4_PNG,
        FIG4_PDF,
        FIG5_PNG,
        FIG5_PDF,
        FIG6_PNG,
        FIG6_PDF,
        FIG7_PNG,
        FIG7_PDF,
        FIG8_PNG,
        FIG8_PDF,
    ]:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
