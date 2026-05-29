from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from encounter_search.shape import smooth_signal
from encounter_search.solver import Start
from encounter_search.solver import build_chain
from encounter_search.solver import exact_distribution
from encounter_search.stage2 import SMOOTH_WINDOWS
from encounter_search.stage2 import crop_index_for_mass
from encounter_search.stage2 import diagnose_curve
from encounter_search.stage2 import parity_pair_curve
from encounter_search.stage2b import ChannelMetrics
from encounter_search.stage2b import SpectralSummary
from encounter_search.stage2b import channel_metrics
from encounter_search.stage2b import f2_has_true_double_peak
from encounter_search.stage2b import spectral_summary


INPUT_FILES = (
    "validation_mean.csv",
    "validation_gf.csv",
    "mean_ratio_pilot.csv",
    "stage2_shape_cases.csv",
    "stage2_artifacts.csv",
    "stage2b_cases.csv",
    "stage2b_target_shift.csv",
    "stage2b_report.md",
)
REPORT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = REPORT_ROOT.parents[2]
DEFAULT_RESULTS_DIR = REPORT_ROOT / "artifacts" / "encounter_search" / "results"
DEFAULT_FIGURE_ROOT = REPORT_ROOT / "artifacts" / "encounter_search" / "figures"


@dataclass(frozen=True)
class FinalCase:
    case_id: str
    label: str
    N: int
    start: Start
    q1: float
    q2: float
    mechanism: str


FINAL_CASES = (
    FinalCase("A_boundary_1_5", "A same-target tail", 31, (1, 5), 0.05, 0.02, "same_target_tail"),
    FinalCase("B_boundary_1_7", "B same-target tail", 31, (1, 7), 0.10, 0.02, "same_target_tail"),
    FinalCase("C_boundary_1_4", "C same-target tail", 31, (1, 4), 0.05, 0.02, "same_target_tail"),
    FinalCase("D_negative_control", "D parity-artifact control", 21, (6, 2), 0.02, 0.90, "parity_artifact"),
    FinalCase(
        "E_target_shift_2_4",
        "Best weak target-shift shoulder",
        31,
        (2, 4),
        0.70,
        0.20,
        "weak_target_shift_shoulder",
    ),
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Finalize exact 1D encounter-analysis package")
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--survival-tol", type=float, default=1e-12)
    parser.add_argument("--max-t", type=int, default=120_000)
    args = parser.parse_args(argv)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    fig_root = DEFAULT_FIGURE_ROOT / "final"
    final_table_dir = out / "final_tables"
    for path in (
        fig_root,
        fig_root / "diagnostics",
        final_table_dir,
        DEFAULT_FIGURE_ROOT / "stage2b" / "diagnostics",
    ):
        path.mkdir(parents=True, exist_ok=True)

    data = load_inputs(out)
    analyses = {
        case.case_id: analyse_case(case, survival_tol=args.survival_tol, max_t=args.max_t)
        for case in FINAL_CASES
    }

    for case_id, analysis in analyses.items():
        final_path = fig_root / "diagnostics" / f"{case_id}.pdf"
        stage2b_path = DEFAULT_FIGURE_ROOT / "stage2b" / "diagnostics" / f"{case_id}.pdf"
        plot_diagnostic_bundle(analysis, final_path)
        plot_diagnostic_bundle(analysis, stage2b_path)

    plot_spatial_configurations(list(analyses.values()), fig_root / "spatial_configurations.pdf")
    plot_spatial_configurations(list(analyses.values()), fig_root / "spatial_configurations.png")
    plot_mean_ratio(data["mean_ratio_pilot"], fig_root / "mean_vs_ratio.pdf")
    plot_stage1_artifact(analyses["D_negative_control"], fig_root / "stage1_artifact_raw_vs_f2.pdf")
    plot_same_target_examples(
        [analyses["A_boundary_1_5"], analyses["B_boundary_1_7"], analyses["C_boundary_1_4"]],
        fig_root / "same_target_tail_ABC.pdf",
    )
    plot_boundary_vs_interior(data["stage2b_cases"], fig_root / "boundary_vs_interior_summary.pdf")
    plot_best_target_shift(analyses["E_target_shift_2_4"], fig_root / "best_target_shift.pdf")
    plot_spectral_pair(
        analyses["A_boundary_1_5"],
        analyses["E_target_shift_2_4"],
        fig_root / "spectral_A_and_target_shift.pdf",
    )

    tables = write_final_tables(data, analyses, final_table_dir)
    write_final_report(out / "final_report.md", tables, data, analyses, fig_root, final_table_dir)
    update_readme(REPORT_ROOT / "README.md")
    print(f"wrote {out / 'final_report.md'}")
    print(f"wrote final tables under {final_table_dir}")
    print(f"wrote final figures under {fig_root}")


def load_inputs(out: Path) -> dict[str, pd.DataFrame | str]:
    missing = [name for name in INPUT_FILES if not (out / name).exists()]
    if missing:
        raise FileNotFoundError(f"missing required Stage 1/2/2b inputs: {missing}")
    data: dict[str, pd.DataFrame | str] = {}
    for name in INPUT_FILES:
        key = name.removesuffix(".csv").removesuffix(".md")
        path = out / name
        if name.endswith(".csv"):
            data[key] = pd.read_csv(path)
        else:
            data[key] = path.read_text(encoding="utf-8")
    return data


def analyse_case(case: FinalCase, *, survival_tol: float, max_t: int) -> dict[str, object]:
    chain = build_chain(case.N, case.q1, case.q2)
    dist = exact_distribution(chain, case.start, survival_tol=survival_tol, max_t=max_t)
    diag = diagnose_curve(dist.f)
    metrics = channel_metrics(dist, diag)
    spectral = spectral_summary(chain, case.start, metrics, modes=8)
    return {
        "case": case,
        "dist": dist,
        "diag": diag,
        "metrics": metrics,
        "spectral": spectral,
        "f2_true_double_peak": f2_has_true_double_peak(diag.f2),
    }


def plot_diagnostic_bundle(analysis: dict[str, object], path: Path) -> None:
    case = analysis["case"]
    dist = analysis["dist"]
    diag = analysis["diag"]
    metrics = analysis["metrics"]
    assert isinstance(case, FinalCase)
    assert isinstance(metrics, ChannelMetrics)

    f = np.asarray(dist.f, dtype=float)
    times = np.asarray(dist.times, dtype=int)
    f2 = parity_pair_curve(f)
    f2_times = 2 * (np.arange(f2.size) + 1)
    hazard = np.divide(f, dist.survival[:-1], out=np.zeros_like(f), where=dist.survival[:-1] > 0)
    late_t = diag.t_late or diag.f2_late_t or diag.f2_shoulder_t or metrics.late_window[1] or diag.t_main
    x_max = min(int(times[-1]), max(40, int(4 * int(late_t))))
    crop = max(5, min(f.size, int(np.searchsorted(times, x_max, side="right"))))
    f2_crop = max(3, min(f2.size, int(math.ceil(crop / 2))))

    fig, axes = plt.subplots(4, 2, figsize=(12, 13), constrained_layout=True)
    axes = axes.ravel()

    axes[0].plot(times[:crop], f[:crop], lw=1.2)
    mark_times(axes[0], [diag.t_main, diag.t_late or diag.f2_late_t or diag.f2_shoulder_t])
    add_time_zoom_inset(
        axes[0],
        times[:crop],
        f[:crop],
        center=diag.t_late or diag.f2_late_t or diag.f2_shoulder_t or diag.t_main,
        half_width=max(8, int(0.22 * max(int(late_t), 1))),
        box=(0.53, 0.46, 0.42, 0.43),
        title="late/shoulder zoom",
    )
    axes[0].set_title("raw f(t)")
    axes[0].set_xlabel("t")
    axes[0].grid(alpha=0.25)

    axes[1].plot(times[:crop], f[:crop], color="0.7", lw=0.8, label="raw")
    for window in SMOOTH_WINDOWS:
        smoothed = smooth_signal(f, window)
        if smoothed is not None:
            axes[1].plot(times[:crop], smoothed[:crop], lw=1.0, label=f"sg {window}")
    axes[1].set_title("smoothed f(t)")
    axes[1].set_xlabel("t")
    axes[1].legend(fontsize=7)
    axes[1].grid(alpha=0.25)

    axes[2].plot(f2_times[:f2_crop], f2[:f2_crop], color="C1", lw=1.2)
    mark_times(axes[2], [diag.f2_main_t, diag.f2_late_t or diag.f2_shoulder_t])
    add_time_zoom_inset(
        axes[2],
        f2_times[:f2_crop],
        f2[:f2_crop],
        center=diag.f2_late_t or diag.f2_shoulder_t or diag.f2_main_t,
        half_width=max(8, int(0.22 * max(int(late_t), 1))),
        box=(0.53, 0.46, 0.42, 0.43),
        color="C1",
        title="F2 decision zoom",
    )
    axes[2].set_title("F2=f(2n-1)+f(2n)")
    axes[2].set_xlabel("paired t")
    axes[2].grid(alpha=0.25)

    log_crop = crop
    positive = f[:log_crop] > 0.0
    log_values = np.log(f[:log_crop][positive])
    axes[3].plot(times[:log_crop][positive], log_values, lw=1.0)
    if log_values.size:
        lo, hi = np.percentile(log_values, [1, 99])
        pad = max(0.2, 0.12 * max(abs(float(hi - lo)), 1e-9))
        axes[3].set_ylim(float(lo) - pad, float(hi) + pad)
    axes[3].set_title("log f(t), zoomed")
    axes[3].set_xlabel("t")
    axes[3].grid(alpha=0.25)

    axes[4].plot(times[:crop], hazard[:crop], color="C2", lw=1.1)
    axes[4].set_title("hazard h(t)=f(t)/S(t-1)")
    axes[4].set_xlabel("t")
    axes[4].grid(alpha=0.25)

    derivative = np.diff(np.log(np.maximum(f2, 1e-300)))
    if derivative.size:
        axes[5].plot(f2_times[1 : derivative.size + 1], derivative, color="C4", lw=1.0)
        local_deriv = derivative[2:f2_crop] if f2_crop > 5 else derivative[:f2_crop]
        finite = local_deriv[np.isfinite(local_deriv)]
        if finite.size:
            lo, hi = np.percentile(finite, [2, 98])
            pad = max(0.05, 0.15 * max(abs(float(hi - lo)), 1e-9))
            axes[5].set_ylim(min(float(lo) - pad, -0.05), max(float(hi) + pad, 0.05))
    axes[5].axhline(0.0, color="0.35", lw=0.8)
    axes[5].set_xlim(0, x_max)
    axes[5].set_title("log-derivative of F2")
    axes[5].set_xlabel("paired t")
    axes[5].grid(alpha=0.25)

    heat = np.log10(np.maximum(dist.f_by_k[:crop, :].T, 1e-300))
    mesh = axes[6].imshow(
        heat,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        extent=[float(times[0]), float(times[crop - 1]), 0.5, case.N + 0.5],
        cmap="magma",
    )
    axes[6].set_title("k-time heatmap, log10 f_k(t)")
    axes[6].set_xlabel("t")
    axes[6].set_ylabel("encounter site k")
    fig.colorbar(mesh, ax=axes[6], fraction=0.046, pad=0.02)

    sites = np.arange(1, case.N + 1)
    axes[7].bar(sites - 0.2, metrics.c_early, width=0.4, label=f"early {metrics.early_window}")
    axes[7].bar(sites + 0.2, metrics.c_late, width=0.4, label=f"late {metrics.late_window}")
    axes[7].set_title("early/late encounter-site C_k")
    axes[7].set_xlabel("k")
    axes[7].legend(fontsize=7)
    axes[7].grid(axis="y", alpha=0.25)

    title = (
        f"{case.label}: N={case.N}, start={case.start}, q1={case.q1:g}, q2={case.q2:g}; "
        f"class={case.mechanism}; F2 true double={analysis['f2_true_double_peak']}"
    )
    fig.suptitle(title)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def mark_times(ax, values: list[int | None]) -> None:
    colors = ("C2", "C3")
    for idx, value in enumerate(values):
        if value is not None and value != "":
            ax.axvline(int(value), color=colors[min(idx, len(colors) - 1)], ls="--", lw=0.9)


def add_time_zoom_inset(
    ax,
    x: np.ndarray,
    y: np.ndarray,
    *,
    center: int | float | None,
    half_width: int | float,
    box: tuple[float, float, float, float] = (0.52, 0.48, 0.42, 0.42),
    color: str | None = None,
    title: str = "local zoom",
) -> None:
    if center is None:
        return
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    if x_arr.size == 0 or y_arr.size == 0:
        return
    lo = max(float(np.min(x_arr)), float(center) - float(half_width))
    hi = min(float(np.max(x_arr)), float(center) + float(half_width))
    mask = (x_arr >= lo) & (x_arr <= hi)
    if int(np.sum(mask)) < 3:
        return
    ax.axvspan(lo, hi, color="0.85", alpha=0.18, lw=0)
    inset = ax.inset_axes(list(box))
    inset.plot(x_arr[mask], y_arr[mask], lw=1.0, color=color)
    local_y = y_arr[mask]
    finite = local_y[np.isfinite(local_y)]
    if finite.size:
        ymin = float(np.min(finite))
        ymax = float(np.max(finite))
        pad = max(1e-12, 0.12 * max(ymax - ymin, abs(ymax), 1e-12))
        inset.set_ylim(ymin - pad, ymax + pad)
    inset.set_xlim(lo, hi)
    inset.set_title(title, fontsize=7)
    inset.tick_params(labelsize=6)
    inset.grid(alpha=0.18)


def plot_mean_ratio(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8), constrained_layout=True)
    labels = {
        "A_fixed_q2_start_5_1": "fixed q2, start=(5,1)",
        "B_fixed_sum_start_7_9": "q1+q2=1, start=(7,9)",
        "C_fixed_sum_start_1_15": "q1+q2=1, start=(1,15)",
    }
    for scan_id, group in df.sort_values("r").groupby("scan_id"):
        group = group.sort_values("r")
        ax.plot(group["r"], group["mean"], lw=1.3, label=labels.get(scan_id, scan_id))
        extrema = group[group["extremum_kind"].fillna("") != ""]
        ax.scatter(extrema["r"], extrema["mean"], s=24)
    ax.set_xscale("log")
    ax.set_xlabel("mobility ratio r=q1/q2")
    ax.set_ylabel("exact mean encounter time")
    ax.set_title("mean first-encounter time versus mobility ratio")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def plot_spatial_configurations(analyses: list[dict[str, object]], path: Path) -> None:
    fig, axes = plt.subplots(
        len(analyses),
        2,
        figsize=(12, 2.45 * len(analyses)),
        constrained_layout=True,
        width_ratios=(1.25, 1.0),
    )
    if len(analyses) == 1:
        axes = np.array([axes])
    for row, analysis in enumerate(analyses):
        draw_physical_lattice(axes[row, 0], analysis)
        draw_state_space(axes[row, 1], analysis)
    handles = [
        Line2D([0], [0], marker="^", color="none", markerfacecolor="C0", markersize=8, label="walker 1 start x0"),
        Line2D([0], [0], marker="v", color="none", markerfacecolor="C1", markersize=8, label="walker 2 start y0"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="C2", markersize=7, label="early top encounter k"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="C3", markersize=7, label="late top encounter k"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="C4", markersize=7, label="largest positive Delta k"),
        Line2D([0], [0], color="0.25", lw=2, label="absorbing diagonal D: x=y"),
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.012),
        ncol=3,
        fontsize=8,
        frameon=True,
    )
    fig.suptitle("Actual spatial configurations and Markov state-space views", fontsize=13)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180 if path.suffix.lower() == ".png" else None, bbox_inches="tight")
    plt.close(fig)


def draw_physical_lattice(ax, analysis: dict[str, object]) -> None:
    case = analysis["case"]
    metrics = analysis["metrics"]
    assert isinstance(case, FinalCase)
    assert isinstance(metrics, ChannelMetrics)
    N = int(case.N)
    a, b = case.start
    sites = np.arange(1, N + 1)

    ax.hlines(0.0, 1, N, color="0.35", lw=1.2)
    ax.scatter(sites, np.zeros_like(sites), s=9, color="0.62", zorder=2)
    ax.vlines([1, N], -0.28, 0.28, color="0.1", lw=2.4)
    ax.text(1, 0.38, "reflect", ha="left", fontsize=7)
    ax.text(N, 0.38, "reflect", ha="right", fontsize=7)

    ax.scatter([a], [0.18], marker="^", s=70, color="C0", label="walker 1 start", zorder=4)
    ax.scatter([b], [-0.18], marker="v", s=70, color="C1", label="walker 2 start", zorder=4)

    top_early = int(metrics.top_k_early)
    top_late = int(metrics.top_k_late)
    max_delta = int(metrics.max_positive_delta_k)
    ax.scatter([top_early], [0.56], marker="s", s=52, color="C2", label="early top k", zorder=5)
    ax.scatter([top_late], [0.72], marker="s", s=52, color="C3", label="late top k", zorder=5)
    ax.scatter([max_delta], [-0.56], marker="D", s=48, color="C4", label="max +Delta k", zorder=5)
    info = (
        f"start=({a},{b})\n"
        f"early top k={top_early}\n"
        f"late top k={top_late}\n"
        f"max +Delta k={max_delta}"
    )
    ax.text(
        0.985,
        0.92,
        info,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "0.75", "alpha": 0.92},
    )

    ticks = sorted({1, N, a, b, top_early, top_late, max_delta})
    ax.set_xticks(ticks)
    ax.tick_params(axis="x", labelsize=7)
    ax.set_xlim(0.2, N + 0.8)
    ax.set_ylim(-0.86, 1.0)
    ax.set_yticks([])
    ax.set_title(f"{case.case_id}: physical lattice 1..{N}", fontsize=9)
    ax.set_xlabel("site k")
    ax.grid(axis="x", alpha=0.12)


def draw_state_space(ax, analysis: dict[str, object]) -> None:
    case = analysis["case"]
    metrics = analysis["metrics"]
    assert isinstance(case, FinalCase)
    assert isinstance(metrics, ChannelMetrics)
    N = int(case.N)
    a, b = case.start
    diagonal = np.arange(1, N + 1)

    ax.plot(diagonal, diagonal, color="0.25", lw=2.0, label="absorbing diagonal D")
    ax.fill_between(diagonal, diagonal - 0.35, diagonal + 0.35, color="0.85", alpha=0.75)
    ax.scatter([a], [b], marker="*", s=120, color="C0", edgecolor="black", linewidth=0.4, zorder=4)

    top_early = int(metrics.top_k_early)
    top_late = int(metrics.top_k_late)
    max_delta = int(metrics.max_positive_delta_k)
    ax.scatter([top_early], [top_early], marker="s", s=52, color="C2", zorder=5)
    ax.scatter([top_late], [top_late], marker="s", s=52, color="C3", zorder=6)
    ax.scatter([max_delta], [max_delta], marker="D", s=48, color="C4", zorder=7)
    ax.vlines(a, 1, b, color="C0", lw=0.8, ls=":", alpha=0.6)
    ax.hlines(b, 1, a, color="C0", lw=0.8, ls=":", alpha=0.6)

    info = (
        f"start ({a},{b})\n"
        f"D: x=y\n"
        f"early/late {top_early}->{top_late}"
    )
    ax.text(
        0.04,
        0.96,
        info,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "0.75", "alpha": 0.92},
    )

    ax.set_xlim(0.5, N + 0.5)
    ax.set_ylim(0.5, N + 0.5)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([1, N])
    ax.set_yticks([1, N])
    ax.set_xlabel("walker 1 site x")
    ax.set_ylabel("walker 2 site y")
    ax.set_title("state space O plus absorbing diagonal D", fontsize=9)
    ax.grid(alpha=0.12)

    relevant = np.array([a, b, top_early, top_late, max_delta], dtype=float)
    lo = max(0.5, float(np.min(relevant)) - 2.0)
    hi = min(N + 0.5, float(np.max(relevant)) + 2.0)
    if hi - lo < 5:
        mid = 0.5 * (lo + hi)
        lo = max(0.5, mid - 2.5)
        hi = min(N + 0.5, mid + 2.5)
    inset = ax.inset_axes([0.54, 0.08, 0.42, 0.42])
    inset.plot(diagonal, diagonal, color="0.25", lw=1.2)
    inset.scatter([a], [b], marker="*", s=70, color="C0", edgecolor="black", linewidth=0.3, zorder=4)
    inset.scatter([top_early], [top_early], marker="s", s=35, color="C2", zorder=5)
    inset.scatter([top_late], [top_late], marker="s", s=35, color="C3", zorder=6)
    inset.scatter([max_delta], [max_delta], marker="D", s=32, color="C4", zorder=7)
    inset.set_xlim(lo, hi)
    inset.set_ylim(lo, hi)
    inset.set_aspect("equal", adjustable="box")
    inset.set_title("local zoom", fontsize=6)
    tick_candidates = sorted({int(v) for v in [a, b, top_early, top_late, max_delta] if lo <= int(v) <= hi})
    if len(tick_candidates) > 4:
        tick_candidates = [tick_candidates[0], tick_candidates[len(tick_candidates) // 2], tick_candidates[-1]]
    inset.set_xticks(tick_candidates)
    inset.set_yticks(tick_candidates)
    inset.tick_params(labelsize=6)
    inset.grid(alpha=0.15)


def plot_stage1_artifact(analysis: dict[str, object], path: Path) -> None:
    dist = analysis["dist"]
    diag = analysis["diag"]
    f = np.asarray(dist.f, dtype=float)
    times = np.asarray(dist.times, dtype=int)
    f2 = parity_pair_curve(f)
    f2_times = 2 * (np.arange(f2.size) + 1)
    x_max = min(int(times[-1]), max(40, int(4 * (diag.t_late or diag.f2_late_t or 12))))
    crop = max(5, min(f.size, int(np.searchsorted(times, x_max, side="right"))))
    f2_crop = max(3, min(f2.size, int(math.ceil(crop / 2))))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    axes[0].plot(times[:crop], f[:crop], lw=1.2)
    for t in diag.raw_peaks[:8]:
        axes[0].axvline(int(t), color="C3", alpha=0.25, lw=0.8)
    raw_zoom_center = int(diag.t_late or diag.t_main or 10)
    add_time_zoom_inset(
        axes[0],
        times[:crop],
        f[:crop],
        center=raw_zoom_center,
        half_width=max(6, int(0.55 * raw_zoom_center)),
        box=(0.48, 0.45, 0.47, 0.45),
        title="early parity-comb zoom",
    )
    axes[0].set_title("raw repeated peaks")
    axes[0].set_xlabel("t")
    axes[0].grid(alpha=0.25)
    axes[1].plot(f2_times[:f2_crop], f2[:f2_crop], color="C1", lw=1.2)
    for n in diag.f2_peaks:
        axes[1].axvline(2 * int(n), color="C2", alpha=0.4, lw=0.8)
    add_time_zoom_inset(
        axes[1],
        f2_times[:f2_crop],
        f2[:f2_crop],
        center=diag.f2_late_t or diag.f2_shoulder_t or diag.f2_main_t,
        half_width=max(6, int(0.55 * raw_zoom_center)),
        box=(0.48, 0.45, 0.47, 0.45),
        color="C1",
        title="paired-time zoom",
    )
    axes[1].set_title("F2 collapses to a single peak")
    axes[1].set_xlabel("paired t")
    axes[1].grid(alpha=0.25)
    fig.suptitle("Stage-1 artifact example: raw parity comb, not a robust double peak")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def plot_same_target_examples(analyses: list[dict[str, object]], path: Path) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(11, 9.8), constrained_layout=True)
    for row, analysis in enumerate(analyses):
        case = analysis["case"]
        dist = analysis["dist"]
        diag = analysis["diag"]
        metrics = analysis["metrics"]
        assert isinstance(case, FinalCase)
        assert isinstance(metrics, ChannelMetrics)
        f = np.asarray(dist.f, dtype=float)
        times = np.asarray(dist.times, dtype=int)
        f2 = parity_pair_curve(f)
        f2_times = 2 * (np.arange(f2.size) + 1)
        late_t = diag.t_late or diag.f2_late_t or diag.f2_shoulder_t or metrics.late_window[1]
        x_max = min(int(times[-1]), max(40, int(4 * late_t)))
        crop = max(5, min(f.size, int(np.searchsorted(times, x_max, side="right"))))
        f2_crop = max(3, min(f2.size, int(math.ceil(crop / 2))))
        raw_norm = f[:crop] / np.max(f)
        axes[row, 0].plot(times[:crop], raw_norm, lw=1.0, label="raw")
        smoothed = smooth_signal(f, 21)
        if smoothed is not None:
            axes[row, 0].plot(times[:crop], smoothed[:crop] / np.max(smoothed), lw=1.0, label="sg21")
        add_time_zoom_inset(
            axes[row, 0],
            times[:crop],
            raw_norm,
            center=late_t,
            half_width=max(10, int(0.20 * int(late_t))),
            box=(0.53, 0.45, 0.42, 0.43),
            title="shoulder zoom",
        )
        axes[row, 0].set_title(f"{case.case_id}: raw shoulder")
        axes[row, 0].grid(alpha=0.25)
        f2_norm = f2[:f2_crop] / np.max(f2)
        axes[row, 1].plot(f2_times[:f2_crop], f2_norm, color="C1", lw=1.0)
        add_time_zoom_inset(
            axes[row, 1],
            f2_times[:f2_crop],
            f2_norm,
            center=diag.f2_late_t or diag.f2_shoulder_t or late_t,
            half_width=max(10, int(0.20 * int(late_t))),
            box=(0.53, 0.45, 0.42, 0.43),
            color="C1",
            title="F2 shoulder zoom",
        )
        axes[row, 1].set_title(
            f"F2 no true double; top k {metrics.top_k_early}->{metrics.top_k_late}"
        )
        axes[row, 1].grid(alpha=0.25)
    axes[-1, 0].set_xlabel("t")
    axes[-1, 1].set_xlabel("paired t")
    fig.suptitle("Stage-2b same-target long-tail examples A/B/C")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def plot_boundary_vs_interior(df: pd.DataFrame, path: Path) -> None:
    reps = df[df["role"] == "representative"].copy()
    rows = []
    for _, rep in reps.iterrows():
        parent = rep["case_id"]
        controls = df[df["boundary_parent"] == parent]
        rows.append(
            {
                "case": parent.replace("_boundary", ""),
                "score_ratio": float(rep["boundary_score_ratio"]),
                "hazard_ratio": float(rep["hazard_late_over_early"])
                / max(float(controls["hazard_late_over_early"].max()), 1e-300),
                "jsd_ratio": float(rep["jsd_early_late_bits"])
                / max(float(controls["jsd_early_late_bits"].max()), 1e-300),
                "delta_ratio": float(rep["max_positive_delta"])
                / max(float(controls["max_positive_delta"].max()), 1e-300),
            }
        )
    comp = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8, 4.2), constrained_layout=True)
    x = np.arange(len(comp))
    width = 0.2
    for offset, col, label in (
        (-1.5 * width, "score_ratio", "shoulder score"),
        (-0.5 * width, "hazard_ratio", "hazard late/early"),
        (0.5 * width, "jsd_ratio", "JSD"),
        (1.5 * width, "delta_ratio", "max Delta"),
    ):
        ax.bar(x + offset, comp[col], width=width, label=label)
    ax.axhline(1.5, color="C3", ls="--", lw=0.9, label="boundary-induced threshold")
    ax.set_xticks(x)
    ax.set_xticklabels(comp["case"], rotation=15, ha="right")
    ax.set_ylabel("boundary / best-interior ratio")
    ax.set_title("Boundary effect is weak in A/B/C")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=7)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def plot_best_target_shift(analysis: dict[str, object], path: Path) -> None:
    case = analysis["case"]
    dist = analysis["dist"]
    diag = analysis["diag"]
    metrics = analysis["metrics"]
    assert isinstance(case, FinalCase)
    assert isinstance(metrics, ChannelMetrics)
    f = np.asarray(dist.f, dtype=float)
    times = np.asarray(dist.times, dtype=int)
    f2 = parity_pair_curve(f)
    f2_times = 2 * (np.arange(f2.size) + 1)
    late_t = diag.t_late or diag.f2_late_t or diag.f2_shoulder_t or metrics.late_window[1]
    x_max = min(int(times[-1]), max(40, int(4 * late_t)))
    crop = max(5, min(f.size, int(np.searchsorted(times, x_max, side="right"))))
    f2_crop = max(3, min(f2.size, int(math.ceil(crop / 2))))

    fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.2), constrained_layout=True)
    axes[0].plot(times[:crop], f[:crop], lw=1.2)
    add_time_zoom_inset(
        axes[0],
        times[:crop],
        f[:crop],
        center=late_t,
        half_width=max(6, int(0.35 * int(late_t))),
        box=(0.48, 0.45, 0.47, 0.45),
        title="shoulder zoom",
    )
    axes[0].set_title("weak target-shift shoulder")
    axes[0].set_xlabel("t")
    axes[0].grid(alpha=0.25)
    axes[1].plot(f2_times[:f2_crop], f2[:f2_crop], color="C1", lw=1.2)
    add_time_zoom_inset(
        axes[1],
        f2_times[:f2_crop],
        f2[:f2_crop],
        center=diag.f2_late_t or diag.f2_shoulder_t or late_t,
        half_width=max(6, int(0.35 * int(late_t))),
        box=(0.48, 0.45, 0.47, 0.45),
        color="C1",
        title="F2 zoom",
    )
    axes[1].set_title("F2: no true double peak")
    axes[1].set_xlabel("paired t")
    axes[1].grid(alpha=0.25)
    sites = np.arange(1, case.N + 1)
    axes[2].bar(sites - 0.2, metrics.c_early, width=0.4, label=f"early {metrics.early_window}")
    axes[2].bar(sites + 0.2, metrics.c_late, width=0.4, label=f"late {metrics.late_window}")
    axes[2].set_title(
        f"C_k shift: top {metrics.top_k_early}->{metrics.top_k_late}, JSD={metrics.jsd:.3g}"
    )
    axes[2].set_xlabel("k")
    axes[2].legend(fontsize=7)
    axes[2].grid(axis="y", alpha=0.25)
    fig.suptitle("Best target-shift case: weak shoulder, not a double peak")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def plot_spectral_pair(left: dict[str, object], right: dict[str, object], path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for col, analysis in enumerate((left, right)):
        case = analysis["case"]
        spectral = analysis["spectral"]
        assert isinstance(case, FinalCase)
        assert isinstance(spectral, SpectralSummary)
        df = pd.DataFrame(spectral.rows)
        axes[0, col].plot(df["mode"], df["lambda"], marker="o", lw=1.0)
        axes[0, col].set_title(f"{case.case_id}: leading eigenvalues")
        axes[0, col].set_xlabel("mode")
        axes[0, col].set_ylabel("lambda")
        axes[0, col].grid(alpha=0.25)
        axes[1, col].bar(df["mode"], df["tail_weight"])
        for _, row in df.iterrows():
            axes[1, col].text(
                float(row["mode"]),
                float(row["tail_weight"]),
                f"k={int(row['top_R_k'])}",
                ha="center",
                va="bottom",
                fontsize=7,
                rotation=90,
            )
        axes[1, col].set_title("tail-channel weight |alpha v^T R|")
        axes[1, col].set_xlabel("mode")
        axes[1, col].grid(axis="y", alpha=0.25)
    fig.suptitle("Spectral check: late tails align with slow modes near lambda=1")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def write_final_tables(
    data: dict[str, pd.DataFrame | str],
    analyses: dict[str, dict[str, object]],
    out_dir: Path,
) -> dict[str, pd.DataFrame]:
    out_dir.mkdir(parents=True, exist_ok=True)
    validation_mean = data["validation_mean"]
    validation_gf = data["validation_gf"]
    mean_ratio = data["mean_ratio_pilot"]
    artifacts = data["stage2_artifacts"]
    stage2b_cases = data["stage2b_cases"]
    target_shift = data["stage2b_target_shift"]
    assert isinstance(validation_mean, pd.DataFrame)
    assert isinstance(validation_gf, pd.DataFrame)
    assert isinstance(mean_ratio, pd.DataFrame)
    assert isinstance(artifacts, pd.DataFrame)
    assert isinstance(stage2b_cases, pd.DataFrame)
    assert isinstance(target_shift, pd.DataFrame)

    formula_table = validation_mean[
        [
            "case_id",
            "N",
            "start_a",
            "start_b",
            "q1",
            "q2",
            "sum_t_f",
            "tail_mass",
            "sum_t_t_f",
            "mean_formula",
            "mean_abs_error",
            "sum_k_p_k",
            "p_tau_mean_abs_error",
            "decomposition_error",
        ]
    ].copy()

    gf_table = validation_gf[
        [
            "z",
            "absorbing_re",
            "determinant_re",
            "abs_error",
            "rel_error",
        ]
    ].copy()

    extrema_rows: list[dict[str, object]] = []
    for scan_id, group in mean_ratio.groupby("scan_id"):
        group = group.sort_values("r")
        for _, row in group[group["extremum_kind"].fillna("") != ""].iterrows():
            extrema_rows.append(
                {
                    "scan_id": scan_id,
                    "description": row["description"],
                    "kind": row["extremum_kind"],
                    "r": float(row["r"]),
                    "q1": float(row["q1"]),
                    "q2": float(row["q2"]),
                    "mean": float(row["mean"]),
                }
            )
    extrema_table = pd.DataFrame(extrema_rows)

    artifact_table = artifacts[
        [
            "artifact_rank",
            "is_control",
            "stage1_rank",
            "N",
            "start_a",
            "start_b",
            "q1",
            "q2",
            "raw_peaks",
            "f2_peaks_n",
            "final_label",
            "artifact_reason",
            "oscillation_index",
        ]
    ].head(12).copy()

    selected_ids = [
        "A_boundary_1_5",
        "B_boundary_1_7",
        "C_boundary_1_4",
        "D_negative_control",
    ]
    mechanism_rows = stage2b_cases[stage2b_cases["case_id"].isin(selected_ids)].copy()
    target_row = target_shift[
        (target_shift["N"] == 31)
        & (target_shift["start_a"] == 2)
        & (target_shift["start_b"] == 4)
        & np.isclose(target_shift["q1"], 0.7)
        & np.isclose(target_shift["q2"], 0.2)
    ].head(1)
    if not target_row.empty:
        target_row = target_row.copy()
        target_row["case_id"] = "E_target_shift_2_4"
        target_row["classification"] = "target_shift_shoulder"
        mechanism_rows = pd.concat([mechanism_rows, target_row], ignore_index=True, sort=False)
    mechanism_table = mechanism_rows[
        [
            "case_id",
            "classification",
            "N",
            "start_a",
            "start_b",
            "q1",
            "q2",
            "f2_true_double_peak",
            "jsd_early_late_bits",
            "late_window_mass",
            "max_positive_delta_k",
            "max_positive_delta",
            "target_shift_score",
            "top_k_early",
            "top_k_late",
            "top_k_changed",
            "leading_lambda",
            "leading_mode_top_k",
        ]
    ].copy()

    tables = {
        "formula_validation": formula_table,
        "gf_validation": gf_table,
        "mean_ratio_extrema": extrema_table,
        "artifact_rejection": artifact_table,
        "mechanism_classification": mechanism_table,
    }
    for name, table in tables.items():
        table.to_csv(out_dir / f"{name}.csv", index=False)
        (out_dir / f"{name}.md").write_text(markdown_table(table), encoding="utf-8")
    return tables


def write_final_report(
    path: Path,
    tables: dict[str, pd.DataFrame],
    data: dict[str, pd.DataFrame | str],
    analyses: dict[str, dict[str, object]],
    fig_root: Path,
    table_dir: Path,
) -> None:
    formula = tables["formula_validation"]
    gf = tables["gf_validation"]
    extrema = tables["mean_ratio_extrema"]
    mechanisms = tables["mechanism_classification"]
    stage2b_cases = data["stage2b_cases"]
    target_shift = data["stage2b_target_shift"]
    assert isinstance(stage2b_cases, pd.DataFrame)
    assert isinstance(target_shift, pd.DataFrame)
    fig_root_label = repo_rel(fig_root)
    table_dir_label = repo_rel(table_dir)
    a = mechanisms[mechanisms["case_id"] == "A_boundary_1_5"].iloc[0]
    e = mechanisms[mechanisms["case_id"] == "E_target_shift_2_4"].iloc[0]
    robust_doubles = int(stage2b_cases["f2_true_double_peak"].astype(bool).sum()) + int(
        target_shift["f2_true_double_peak"].astype(bool).sum()
    )
    lines = [
        "# Final Exact Encounter-Analysis Report",
        "",
        "## Executive conclusion",
        "",
        f"Robust F2 double peaks found: {robust_doubles}. The current finite 1D reflecting,",
        "synchronous, co-location-only encounter model does not produce a robust double",
        "peak in the retained Stage 1/2/2b scans. Apparent unusual shapes are classified",
        "as parity artifacts, same-target long tails, or weak target-shift shoulders.",
        "",
        "Where do the visible bumps or shoulders appear? Short-distance, strongly",
        "asymmetric mobility cases can show jagged raw peaks from odd/even parity; the",
        "negative control `N=21, start=(6,2), q1=0.02, q2=0.9` is the clearest example.",
        "Slow near-boundary cases such as A/B/C show long tails or shoulders, but the",
        "dominant encounter site does not change (`4->4`, `6->6`, `3->3`). The best",
        "target-shift case `N=31, start=(2,4), q1=0.7, q2=0.2` has a weak site shift",
        "`4->3`, but still no true F2 double peak.",
        "",
        "The jagged figure is therefore normal for this synchronous discrete-time",
        "model: it is a parity-comb artifact in raw `f(t)`. The decision curve is `F2`,",
        "which pairs odd/even times before applying the same peak-valley rule used in",
        "the rest of the repository.",
        "",
        "## Model and exact absorbing-chain formulation",
        "",
        "The model is the finite one-dimensional reflecting lattice with sites `1..N`.",
        "Walker `i` has lazy mobility `q_i`; boundary reflection uses attempted-outside-stays.",
        "The synchronous independent update has joint transition `P = kron(P1, P2)`.",
        "Transient states are off-diagonal ordered pairs `O={(x,y):x!=y}` and encounter",
        "states are diagonal co-locations `D={(k,k)}`. The exact absorbing-chain blocks are",
        "`Q=P[O,O]` and `R=P[O,D]`, so `f_k(t)=alpha Q^(t-1) R[:,k]` and",
        "`f(t)=sum_k f_k(t)`. No Monte Carlo is used.",
        "",
        "## Spatial configuration views",
        "",
        "The final package now includes the actual spatial layout for A/B/C, the",
        "negative control, and the best target-shift case. Each row shows the physical",
        "one-dimensional reflecting lattice on the left and the ordered state space",
        "`(x,y)` on the right. In the state-space panel, the diagonal is the absorbing",
        "co-location set `D={(k,k)}`.",
        "",
        f"Figure: `{fig_root_label}/spatial_configurations.pdf`.",
        "",
        "How to read this figure: blue up-triangle is walker 1 start `x0`; orange",
        "down-triangle is walker 2 start `y0`; green square is the dominant encounter",
        "site in the early window; red square is the dominant encounter site in the late",
        "window; purple diamond is the site with the largest positive `Delta_k = C_late-C_early`.",
        "The right panel is the ordered state space, where the diagonal line is the",
        "absorbing set `D` and the inset is a local zoom around the actual start and",
        "dominant encounter sites.",
        "",
        "## Operational double-peak rule",
        "",
        "A raw second bump is not enough. The final rule first forms the parity-pair",
        "curve `F2[n]=f(2n-1)+f(2n)` to remove odd/even update oscillations. A case is",
        "called a robust F2 double peak only if F2 has at least two true local maxima:",
        "a main peak and a later peak more than two F2 bins later. The later peak must",
        "be at least 5% of the main peak, and the minimum valley between the two peaks",
        "must be at most 80% of the smaller peak. Otherwise the feature is reported as",
        "a shoulder, long tail, target-shift shoulder, or artifact. This is why A/B/C",
        "and the best target-shift case are not called double peaks.",
        "",
        "This is aligned with the repository's existing visual double-peak convention",
        "`rho = h_valley/min(h1,h2) <= 0.8`. The encounter-specific part is only the",
        "preprocessing step: synchronous co-location curves can alternate strongly",
        "between odd and even time steps, so the classifier is applied to `F2` rather",
        "than to raw `f(t)` when making the final double-peak claim.",
        "",
        "In diagnostic bundles, dashed green/red vertical lines mark the main and late",
        "diagnostic times; `C_k` compares normalized encounter-site mass in early and",
        "late windows; the heatmap shows `log10 f_k(t)` by encounter site and time.",
        "Light gray bands and small inset axes are local zooms for the jagged, shoulder,",
        "or F2-decision regions that are hard to read on the full time axis.",
        "",
        "## Mean identities and GF determinant validation",
        "",
        f"The formula checks close to numerical precision: max `mean_abs_error` is "
        f"{float(formula['mean_abs_error'].max()):.3g}, max `p_tau_mean_abs_error` is "
        f"{float(formula['p_tau_mean_abs_error'].max()):.3g}, and max decomposition error is "
        f"{float(formula['decomposition_error'].max()):.3g}.",
        f"The small-`N` Green/determinant validation has max absolute error "
        f"{float(gf['abs_error'].max()):.3g}.",
        "",
        f"Tables: `{table_dir_label}/formula_validation.csv`, `{table_dir_label}/gf_validation.csv`.",
        "",
        "## Mean first-passage time vs q1/q2: maximum is not universal",
        "",
        "The three pilot scans show different extremum structure. Two starts have an",
        "interior maximum in the scanned mobility ratio range, while the boundary-to-boundary",
        "fixed-sum case has an interior minimum and an endpoint maximum. Thus an interior",
        "maximum of mean encounter time is a geometry/start-dependent phenomenon, not a",
        "universal rule.",
        "",
        f"Figure: `{fig_root_label}/mean_vs_ratio.pdf`.",
        f"Table: `{table_dir_label}/mean_ratio_extrema.csv`.",
        "",
        markdown_table(extrema),
        "",
        "## Why Stage-1 double peaks were artifacts",
        "",
        "Stage 1 ranked raw curves and therefore promoted short-distance parity combs.",
        "The representative negative control keeps multiple raw peaks at alternating times,",
        "but the parity-pair curve `F2[n]=f(2n-1)+f(2n)` collapses the feature to a single",
        "peak. These cases are rejected as parity or ballistic-short-distance artifacts,",
        "not as genuine double peaks.",
        "",
        f"Figure: `{fig_root_label}/stage1_artifact_raw_vs_f2.pdf`.",
        f"Table: `{table_dir_label}/artifact_rejection.csv`.",
        "",
        "## Stage-2/2b result: no robust F2 double peaks",
        "",
        f"In the Stage-2b case table plus the top-30 target-shift table, robust F2 double peaks found: {robust_doubles}.",
        "Across the current reflecting synchronous co-location model, the observed unusual",
        "shapes are better classified as parity artifacts, same-target long tails, or weak",
        "target-shift shoulders. This report does not claim a robust double peak.",
        "",
        f"Table: `{table_dir_label}/mechanism_classification.csv`.",
        "",
        "## Same-target long-tail cases A/B/C",
        "",
        "Cases A, B, and C are not double peaks. Their top encounter site is unchanged",
        "between early and late windows, and the boundary-null controls do not show a large",
        "boundary-specific amplification. They are therefore reported as same-target long",
        "tails with weak boundary influence, not boundary-induced delayed channels.",
        "",
        f"Figure: `{fig_root_label}/same_target_tail_ABC.pdf`.",
        f"Boundary comparison: `{fig_root_label}/boundary_vs_interior_summary.pdf`.",
        "",
        "## Weak target-shift case and responsible k sites",
        "",
        "The clearest target-shift shoulder in the retained Stage-2b list is",
        "`N=31, start=(2,4), q1=0.7, q2=0.2`. It is a weak target-shift shoulder,",
        "not a double peak. Its early/late encounter-site distributions shift enough",
        "to change the top site and produce a modest JSD, but F2 still lacks two true",
        "local maxima separated by a visible valley.",
        "",
        f"For this case: top k {int(e['top_k_early'])}->{int(e['top_k_late'])}, "
        f"JSD={float(e['jsd_early_late_bits']):.3g}, max positive Delta at "
        f"k={int(e['max_positive_delta_k'])}, target-shift score="
        f"{float(e['target_shift_score']):.3g}.",
        "",
        f"Figure: `{fig_root_label}/best_target_shift.pdf`.",
        "",
        "## Spectral interpretation: late tail as generic slow-mode relaxation",
        "",
        "The spectral checks show leading eigenvalues close to one and slow tail-channel",
        "weights that are not cleanly aligned with a new dominant encounter site. For A,",
        f"the leading mode has lambda={float(a['leading_lambda']):.8f} and top R-channel "
        f"k={int(a['leading_mode_top_k'])}, while the early/late top encounter site remains "
        f"k={int(a['top_k_early'])}. For the weak target-shift case, the site shift is",
        "visible in `C_k`, but the curve still reads as slow-mode relaxation plus modest",
        "redistribution, not as a separate second-peak mechanism.",
        "",
        f"Figure: `{fig_root_label}/spectral_A_and_target_shift.pdf`.",
        "",
        "## Final scientific conclusion and limitations",
        "",
        "Final conclusion: no robust F2 double peak was found in the current reflecting",
        "synchronous co-location model. The weird shapes observed in Stage 1, Stage 2,",
        "and Stage 2b are parity artifacts, same-target long tails, or weak target-shift",
        "shoulders. The conclusion is limited to the scanned finite 1D reflecting model,",
        "the synchronous lazy update rule, and co-location-only encounters; it does not",
        "rule out stronger effects under different boundary conditions, crossing absorption,",
        "higher dimensions, or different mobility/start regimes.",
        "",
        "## Reproducibility",
        "",
        "Install dependencies with Python 3.11 and run the final packaging command:",
        "",
        "```bash",
        "python3.11 -m venv .local/encounter-py311",
        ".local/encounter-py311/bin/python -m pip install -r requirements.txt",
        "PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m encounter_search.finalize",
        "PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m pytest tests/test_encounter_search.py tests/test_encounter_reflecting_mean_validation.py tests/test_encounter_green_formula_comparison.py -q",
        "```",
        "",
        "One command to reproduce the final outputs from existing Stage 1/2/2b inputs:",
        "",
        "```bash",
        "PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m encounter_search.finalize",
        "```",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def markdown_table(df: pd.DataFrame, *, max_rows: int | None = None) -> str:
    table = df if max_rows is None else df.head(max_rows)
    if table.empty:
        return "_No rows._"
    columns = list(table.columns)
    lines = [
        "| " + " | ".join(str(c) for c in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in table.iterrows():
        values = [format_cell(row[col]) for col in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def format_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, (float, np.floating)):
        if value == 0:
            return "0"
        if abs(float(value)) < 1e-3 or abs(float(value)) >= 1e4:
            return f"{float(value):.3e}"
        return f"{float(value):.6g}"
    return str(value).replace("|", "/")


def update_readme(path: Path) -> None:
    marker = "## Exact Encounter Analysis Package"
    text = path.read_text(encoding="utf-8") if path.exists() else "# valley-k-small\n"
    section = f"""
{marker}

This repository contains an exact Markov-chain pilot for first encounter of two
lazy random walkers on a finite reflecting one-dimensional lattice. The final
analysis package uses Stage 1, Stage 2, and Stage 2b outputs and does not launch
a new broad search.

Install:

```bash
python3.11 -m venv .local/encounter-py311
.local/encounter-py311/bin/python -m pip install -r requirements.txt
```

Reproduce the final package from the existing Stage 1/2/2b inputs:

```bash
PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m encounter_search.finalize
```

Full upstream regeneration, if needed:

```bash
PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m encounter_search.run --pilot
PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m encounter_search.stage2
PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m encounter_search.stage2b
PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m encounter_search.finalize
```

Validation:

```bash
PYTHONPATH=research/reports/final_multitimescale_fpt_encounter/code .local/encounter-py311/bin/python -m pytest tests/test_encounter_search.py tests/test_encounter_reflecting_mean_validation.py tests/test_encounter_green_formula_comparison.py -q
python3 scripts/reportctl.py check-docs-paths
python3 scripts/reportctl.py validate-science-rules
```

Final outputs:

- `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/results/final_report.md`
- `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/results/final_tables/`
- `research/reports/final_multitimescale_fpt_encounter/artifacts/encounter_search/figures/final/`

Final conclusion: no robust F2 double peak was found in the current reflecting
synchronous co-location model; observed unusual shapes are parity artifacts,
same-target long tails, or weak target-shift shoulders.
"""
    if marker in text:
        prefix = text.split(marker, 1)[0].rstrip()
        path.write_text(prefix + "\n\n" + section.lstrip(), encoding="utf-8")
    else:
        path.write_text(text.rstrip() + "\n\n" + section.lstrip(), encoding="utf-8")


if __name__ == "__main__":
    main()
