from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.sparse.linalg as spla

from encounter_search.shape import jensen_shannon_divergence
from encounter_search.shape import smooth_signal
from encounter_search.solver import Start
from encounter_search.solver import build_chain
from encounter_search.solver import exact_distribution
from encounter_search.stage2 import Q_GRID
from encounter_search.stage2 import SMOOTH_WINDOWS
from encounter_search.stage2 import all_start_total_curves
from encounter_search.stage2 import crop_index_for_mass
from encounter_search.stage2 import diagnose_curve
from encounter_search.stage2 import f2_shoulder_diagnostic
from encounter_search.stage2 import iter_scan_starts
from encounter_search.stage2 import parity_pair_curve


REPRESENTATIVE_CASES = (
    ("A_boundary_1_5", 31, (1, 5), 0.05, 0.02, "representative"),
    ("B_boundary_1_7", 31, (1, 7), 0.10, 0.02, "representative"),
    ("C_boundary_1_4", 31, (1, 4), 0.05, 0.02, "representative"),
    ("D_negative_control", 21, (6, 2), 0.02, 0.90, "negative_control"),
)
N_VALUES = (15, 21, 31)
REPORT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = REPORT_ROOT.parents[2]
DEFAULT_RESULTS_DIR = REPORT_ROOT / "artifacts" / "encounter_search" / "results"
DEFAULT_FIGURE_ROOT = REPORT_ROOT / "artifacts" / "encounter_search" / "figures"


@dataclass(frozen=True)
class ChannelMetrics:
    early_window: tuple[int, int]
    late_window: tuple[int, int]
    c_early: np.ndarray
    c_late: np.ndarray
    delta: np.ndarray
    jsd: float
    top_k_early: int
    top_k_late: int
    max_positive_delta_k: int
    max_positive_delta: float
    late_window_mass: float
    target_shift_score: float


@dataclass(frozen=True)
class SpectralSummary:
    eigenvalues: np.ndarray
    rows: list[dict[str, object]]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Stage-2b mechanism-focused encounter analysis")
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--scan-max-t", type=int, default=6_000)
    parser.add_argument("--detail-max-t", type=int, default=120_000)
    parser.add_argument("--survival-tol", type=float, default=1e-12)
    parser.add_argument("--candidate-pool", type=int, default=260)
    parser.add_argument("--top-target-shift", type=int, default=30)
    args = parser.parse_args(argv)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    fig_root = DEFAULT_FIGURE_ROOT / "stage2b"
    for sub in ("diagnostics", "boundary_vs_interior", "group_decomposition", "spectral"):
        (fig_root / sub).mkdir(parents=True, exist_ok=True)

    print("analysing representative cases")
    representative_rows = analyse_representatives(
        out=out,
        fig_root=fig_root,
        survival_tol=args.survival_tol,
        detail_max_t=args.detail_max_t,
    )

    print("running target-shift reranking scan")
    target_shift_df = target_shift_rerank(
        survival_tol=args.survival_tol,
        scan_max_t=args.scan_max_t,
        detail_max_t=args.detail_max_t,
        candidate_pool=args.candidate_pool,
        top_n=args.top_target_shift,
    )
    target_shift_df = target_shift_df.reset_index(drop=True)
    target_shift_df.insert(0, "target_shift_rank", np.arange(1, len(target_shift_df) + 1))
    if "case_id" in target_shift_df.columns:
        target_shift_df["case_id"] = [
            f"target_shift_{int(rank):02d}" for rank in target_shift_df["target_shift_rank"]
        ]
    target_shift_df.to_csv(out / "stage2b_target_shift.csv", index=False)
    print(f"wrote {out / 'stage2b_target_shift.csv'}")

    selected_for_plots = target_shift_df.head(8)
    print("plotting group decompositions and spectral checks for selected target-shift cases")
    extra_case_rows: list[dict[str, object]] = []
    for _, row in selected_for_plots.iterrows():
        case_id = str(row["case_id"])
        analysis = analyse_single_case(
            case_id,
            int(row["N"]),
            (int(row["start_a"]), int(row["start_b"])),
            float(row["q1"]),
            float(row["q2"]),
            "target_shift_candidate",
            survival_tol=args.survival_tol,
            detail_max_t=args.detail_max_t,
        )
        plot_group_decomposition(analysis, fig_root / "group_decomposition")
        plot_spectral_summary(analysis, fig_root / "spectral")
        extra_case_rows.append(compact_case_row(analysis))

    case_df = pd.DataFrame(representative_rows + extra_case_rows)
    case_df.to_csv(out / "stage2b_cases.csv", index=False)
    print(f"wrote {out / 'stage2b_cases.csv'}")

    write_report(out / "stage2b_report.md", case_df, target_shift_df, fig_root)
    print(f"wrote {out / 'stage2b_report.md'}")


def analyse_representatives(
    *,
    out: Path,
    fig_root: Path,
    survival_tol: float,
    detail_max_t: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case_id, N, start, q1, q2, role in REPRESENTATIVE_CASES:
        analysis = analyse_single_case(
            case_id,
            N,
            start,
            q1,
            q2,
            role,
            survival_tol=survival_tol,
            detail_max_t=detail_max_t,
        )
        if role == "representative":
            boundary_rows = boundary_null_rows(
                analysis,
                survival_tol=survival_tol,
                detail_max_t=detail_max_t,
            )
            parent_score = float(analysis["diag"].f2_shoulder_score)
            best_control = max((float(row["f2_shoulder_score"]) for row in boundary_rows), default=0.0)
            ratio = safe_ratio(parent_score, best_control)
            analysis["boundary_best_interior_score"] = best_control
            analysis["boundary_score_ratio"] = ratio
            analysis["boundary_induced"] = bool(ratio >= 1.5)
            if not analysis["boundary_induced"] and analysis["classification"] == "boundary_long_tail":
                metrics = analysis["metrics"]
                if isinstance(metrics, ChannelMetrics) and metrics.top_k_early == metrics.top_k_late:
                    analysis["classification"] = "same_target_tail"
                else:
                    analysis["classification"] = "generic_tail"
            plot_diagnostics(analysis, fig_root / "diagnostics")
            plot_group_decomposition(analysis, fig_root / "group_decomposition")
            plot_spectral_summary(analysis, fig_root / "spectral")
            rows.append(compact_case_row(analysis))
            rows.extend(boundary_rows)
            plot_boundary_comparison(analysis, boundary_rows, fig_root / "boundary_vs_interior")
        else:
            plot_diagnostics(analysis, fig_root / "diagnostics")
            plot_group_decomposition(analysis, fig_root / "group_decomposition")
            plot_spectral_summary(analysis, fig_root / "spectral")
            rows.append(compact_case_row(analysis))
    return rows


def analyse_single_case(
    case_id: str,
    N: int,
    start: Start,
    q1: float,
    q2: float,
    role: str,
    *,
    survival_tol: float,
    detail_max_t: int,
) -> dict[str, object]:
    chain = build_chain(N, q1, q2)
    dist = exact_distribution(chain, start, survival_tol=survival_tol, max_t=detail_max_t)
    diag = diagnose_curve(dist.f)
    metrics = channel_metrics(dist, diag)
    spectral = spectral_summary(chain, start, metrics, modes=8)
    classification = classify_mechanism(dist, diag, metrics, role=role)
    return {
        "case_id": case_id,
        "role": role,
        "N": int(N),
        "start": start,
        "start_a": int(start[0]),
        "start_b": int(start[1]),
        "q1": float(q1),
        "q2": float(q2),
        "dist": dist,
        "diag": diag,
        "metrics": metrics,
        "spectral": spectral,
        "classification": classification,
    }


def compact_case_row(analysis: dict[str, object]) -> dict[str, object]:
    diag = analysis["diag"]
    metrics = analysis["metrics"]
    spectral = analysis["spectral"]
    dist = analysis["dist"]
    assert hasattr(diag, "label")
    assert isinstance(metrics, ChannelMetrics)
    assert isinstance(spectral, SpectralSummary)
    lead = spectral.rows[0] if spectral.rows else {}
    hazard = np.divide(
        dist.f,
        dist.survival[:-1],
        out=np.zeros_like(dist.f),
        where=dist.survival[:-1] > 0,
    )
    early_hazard = window_mean_by_time(hazard, metrics.early_window)
    late_hazard = window_mean_by_time(hazard, metrics.late_window)
    return {
        "case_id": analysis["case_id"],
        "role": analysis["role"],
        "N": analysis["N"],
        "start_a": analysis["start_a"],
        "start_b": analysis["start_b"],
        "q1": analysis["q1"],
        "q2": analysis["q2"],
        "t_main": diag.t_main,
        "t_late": "" if diag.t_late is None else diag.t_late,
        "f2_peaks_n": ";".join(str(v) for v in diag.f2_peaks),
        "f2_true_double_peak": f2_has_true_double_peak(diag.f2),
        "f2_shoulder_t": "" if diag.f2_shoulder_t is None else diag.f2_shoulder_t,
        "f2_shoulder_score": diag.f2_shoulder_score,
        "oscillation_index": diag.oscillation_index,
        "jsd_early_late_bits": metrics.jsd,
        "late_window_mass": metrics.late_window_mass,
        "hazard_early_mean": early_hazard,
        "hazard_late_mean": late_hazard,
        "hazard_late_over_early": safe_ratio(late_hazard, early_hazard),
        "max_positive_delta_k": metrics.max_positive_delta_k,
        "max_positive_delta": metrics.max_positive_delta,
        "target_shift_score": metrics.target_shift_score,
        "top_k_early": metrics.top_k_early,
        "top_k_late": metrics.top_k_late,
        "top_k_changed": metrics.top_k_early != metrics.top_k_late,
        "classification": analysis["classification"],
        "leading_lambda": lead.get("lambda", ""),
        "leading_timescale": lead.get("timescale", ""),
        "leading_mode_top_k": lead.get("top_R_k", ""),
        "leading_mode_tail_weight": lead.get("tail_weight", ""),
        "boundary_best_interior_score": analysis.get("boundary_best_interior_score", ""),
        "boundary_score_ratio": analysis.get("boundary_score_ratio", ""),
        "boundary_induced": analysis.get("boundary_induced", ""),
    }


def channel_metrics(dist, diag) -> ChannelMetrics:
    f = np.asarray(dist.f, dtype=float)
    f_by_k = np.asarray(dist.f_by_k, dtype=float)
    early_center = max(int(diag.t_main) - 1, 0)
    late_t = diag.t_late or diag.f2_late_t or diag.f2_shoulder_t or max(diag.t_main + 8, int(1.5 * diag.t_main))
    late_center = min(max(int(late_t) - 1, 0), f.size - 1)
    radius = max(4, min(30, int(max(late_center - early_center, 1) // 5)))
    early_lo, early_hi = window(early_center, f.size, radius)
    late_lo, late_hi = window(late_center, f.size, radius)
    early_by_k = np.sum(f_by_k[early_lo : early_hi + 1], axis=0)
    late_by_k = np.sum(f_by_k[late_lo : late_hi + 1], axis=0)
    c_early = normalise_or_zero(early_by_k)
    c_late = normalise_or_zero(late_by_k)
    delta = c_late - c_early
    max_pos_idx = int(np.argmax(delta)) if delta.size else 0
    max_pos_delta = max(float(delta[max_pos_idx]) if delta.size else 0.0, 0.0)
    jsd = jensen_shannon_divergence(c_early, c_late)
    late_mass = float(np.sum(f[late_lo : late_hi + 1]))
    return ChannelMetrics(
        early_window=(int(dist.times[early_lo]), int(dist.times[early_hi])),
        late_window=(int(dist.times[late_lo]), int(dist.times[late_hi])),
        c_early=c_early,
        c_late=c_late,
        delta=delta,
        jsd=float(jsd),
        top_k_early=int(np.argmax(c_early)) + 1 if c_early.size else 0,
        top_k_late=int(np.argmax(c_late)) + 1 if c_late.size else 0,
        max_positive_delta_k=max_pos_idx + 1,
        max_positive_delta=max_pos_delta,
        late_window_mass=late_mass,
        target_shift_score=float(jsd * late_mass * max_pos_delta),
    )


def boundary_null_rows(
    analysis: dict[str, object],
    *,
    survival_tol: float,
    detail_max_t: int,
) -> list[dict[str, object]]:
    N = int(analysis["N"])
    start = analysis["start"]
    q1 = float(analysis["q1"])
    q2 = float(analysis["q2"])
    sep = int(start[1]) - int(start[0])
    abs_sep = abs(sep)
    candidates: list[Start] = []
    anchors = [4, 7, 10, max(2, N // 2 - abs_sep // 2), N - abs_sep - 8, N - abs_sep - 4]
    for a in anchors:
        b = a + sep
        if 1 <= a <= N and 1 <= b <= N and a != b and min(a, b) > 2 and max(a, b) < N - 1:
            candidates.append((int(a), int(b)))
    unique: list[Start] = []
    for item in candidates:
        if item not in unique:
            unique.append(item)
    rows: list[dict[str, object]] = []
    for idx, control_start in enumerate(unique[:4], start=1):
        control = analyse_single_case(
            f"{analysis['case_id']}_interior_{idx}",
            N,
            control_start,
            q1,
            q2,
            "interior_control",
            survival_tol=survival_tol,
            detail_max_t=detail_max_t,
        )
        row = compact_case_row(control)
        row["boundary_parent"] = analysis["case_id"]
        row["boundary_score_ratio"] = safe_ratio(
            float(compact_case_row(analysis)["f2_shoulder_score"]),
            float(row["f2_shoulder_score"]),
        )
        rows.append(row)
    return rows


def target_shift_rerank(
    *,
    survival_tol: float,
    scan_max_t: int,
    detail_max_t: int,
    candidate_pool: int,
    top_n: int,
) -> pd.DataFrame:
    prelim_rows: list[dict[str, object]] = []
    for N in N_VALUES:
        starts = list(iter_scan_starts(N))
        for q1 in Q_GRID:
            for q2 in Q_GRID:
                print(f"stage2b target scan N={N} q1={q1:g} q2={q2:g}")
                chain = build_chain(N, q1, q2)
                curves, tails, reached = all_start_total_curves(
                    chain,
                    max_t=scan_max_t,
                    survival_tol=survival_tol,
                )
                start_to_index = {state: i for i, state in enumerate(chain.transient_states)}
                for start in starts:
                    f = curves[:, start_to_index[start]]
                    diag = diagnose_curve(f)
                    if diag.t_late is None and diag.f2_late_t is None:
                        continue
                    late_idx = min(
                        f.size - 1,
                        max((diag.t_late or diag.f2_late_t or diag.f2_shoulder_t or diag.min_late_t) - 1, 0),
                    )
                    late_lo, late_hi = window(late_idx, f.size, radius=12)
                    late_mass = float(np.sum(f[late_lo : late_hi + 1]))
                    pre_score = late_mass * max(float(diag.f2_shoulder_score), float(diag.score), 1e-12)
                    if diag.repeat2_peaks and diag.t_main <= 6:
                        pre_score *= 0.05
                    prelim_rows.append(
                        {
                            "N": N,
                            "start_a": start[0],
                            "start_b": start[1],
                            "q1": q1,
                            "q2": q2,
                            "pre_score": pre_score,
                            "pre_label": diag.label,
                            "pre_t_main": diag.t_main,
                            "pre_t_late": diag.t_late or diag.f2_late_t or "",
                            "pre_late_mass": late_mass,
                            "scan_tail_mass": float(tails[start_to_index[start]]),
                            "scan_reached_tol": bool(reached),
                        }
                    )
    prelim = pd.DataFrame(prelim_rows)
    if prelim.empty:
        return prelim
    pool = prelim.sort_values("pre_score", ascending=False).head(int(candidate_pool))
    enriched: list[dict[str, object]] = []
    seen: set[tuple[int, int, int, float, float]] = set()
    for _, row in pool.iterrows():
        key = (int(row["N"]), int(row["start_a"]), int(row["start_b"]), float(row["q1"]), float(row["q2"]))
        if key in seen:
            continue
        seen.add(key)
        analysis = analyse_single_case(
            "target_shift_pool",
            key[0],
            (key[1], key[2]),
            key[3],
            key[4],
            "target_shift_candidate",
            survival_tol=survival_tol,
            detail_max_t=detail_max_t,
        )
        compact = compact_case_row(analysis)
        compact["pre_score"] = float(row["pre_score"])
        compact["scan_tail_mass"] = float(row["scan_tail_mass"])
        compact["scan_reached_tol"] = bool(row["scan_reached_tol"])
        enriched.append(compact)
    enriched_df = pd.DataFrame(enriched)
    if enriched_df.empty:
        return enriched_df
    return enriched_df.sort_values("target_shift_score", ascending=False).head(int(top_n)).reset_index(drop=True)


def classify_mechanism(dist, diag, metrics: ChannelMetrics, *, role: str) -> str:
    if diag.artifact_reason != "none" or (diag.repeat2_peaks and diag.t_main <= 6):
        return "parity_artifact"
    if f2_has_true_double_peak(diag.f2):
        return "true_double_peak"
    if metrics.top_k_early != metrics.top_k_late and metrics.jsd >= 0.05 and metrics.max_positive_delta > 0.03:
        return "target_shift_shoulder"
    boundary_mass_late = float(np.sum(metrics.c_late[:3]) + np.sum(metrics.c_late[-3:]))
    boundary_mass_early = float(np.sum(metrics.c_early[:3]) + np.sum(metrics.c_early[-3:]))
    if boundary_mass_late > boundary_mass_early + 0.03 or min(dist.start) <= 2 or max(dist.start) >= dist.N - 1:
        return "boundary_long_tail"
    if metrics.top_k_early == metrics.top_k_late and diag.f2_shoulder_t is not None:
        return "same_target_tail"
    return "generic_tail"


F2_DOUBLE_PEAK_MIN_REL_HEIGHT = 0.05
F2_DOUBLE_PEAK_MAX_VALLEY_OVER_SMALLER_PEAK = 0.80


def f2_has_true_double_peak(f2: np.ndarray) -> bool:
    """Apply the repo's visual peak-valley rule after parity-pair aggregation."""
    y = np.asarray(f2, dtype=float)
    if y.size < 5 or float(np.max(y, initial=0.0)) <= 0.0:
        return False
    from scipy.signal import find_peaks

    peaks, _ = find_peaks(y, prominence=max(float(np.max(y)) * 1e-4, 1e-300), distance=2)
    if peaks.size < 2:
        return False
    main = int(peaks[np.argmax(y[peaks])])
    later = [
        int(p)
        for p in peaks
        if int(p) > main + 2 and float(y[int(p)]) >= F2_DOUBLE_PEAK_MIN_REL_HEIGHT * float(y[main])
    ]
    for p in later:
        valley = float(np.min(y[main : p + 1]))
        if valley <= F2_DOUBLE_PEAK_MAX_VALLEY_OVER_SMALLER_PEAK * min(float(y[main]), float(y[p])):
            return True
    return False


def spectral_summary(chain, start: Start, metrics: ChannelMetrics, *, modes: int) -> SpectralSummary:
    k = min(int(modes), chain.Q.shape[0] - 2)
    if k <= 0:
        return SpectralSummary(np.array([], dtype=float), [])
    vals, vecs = spla.eigsh(chain.Q, k=k, which="LA")
    order = np.argsort(vals)[::-1]
    vals = np.asarray(vals[order], dtype=float)
    vecs = np.asarray(vecs[:, order], dtype=float)
    start_idx = chain.start_position(start)
    R = chain.R.toarray()
    rows: list[dict[str, object]] = []
    for mode_idx, lam in enumerate(vals, start=1):
        v = vecs[:, mode_idx - 1]
        alpha_coeff = float(v[start_idx])
        channel_amplitude = np.asarray(v @ R).reshape(-1)
        tail_channel = alpha_coeff * channel_amplitude
        top_k = int(np.argmax(np.abs(tail_channel))) + 1 if tail_channel.size else 0
        tail_weight = float(np.sum(np.abs(tail_channel)))
        signed_total = float(np.sum(tail_channel))
        timescale = float(-1.0 / math.log(max(min(float(lam), 0.999999999999), 1e-12)))
        rows.append(
            {
                "mode": mode_idx,
                "lambda": float(lam),
                "timescale": timescale,
                "alpha_coeff": alpha_coeff,
                "signed_total_R": signed_total,
                "tail_weight": tail_weight,
                "top_R_k": top_k,
                "early_C_at_top_R_k": float(metrics.c_early[top_k - 1]) if top_k else 0.0,
                "late_C_at_top_R_k": float(metrics.c_late[top_k - 1]) if top_k else 0.0,
            }
        )
    return SpectralSummary(vals, rows)


def plot_diagnostics(analysis: dict[str, object], out_dir: Path) -> None:
    dist = analysis["dist"]
    diag = analysis["diag"]
    f = np.asarray(dist.f, dtype=float)
    times = np.asarray(dist.times, dtype=int)
    f2 = parity_pair_curve(f)
    f2_times = 2 * (np.arange(f2.size) + 1)
    hazard = np.divide(f, dist.survival[:-1], out=np.zeros_like(f), where=dist.survival[:-1] > 0)
    x_max = min(int(max((diag.t_late or diag.f2_late_t or diag.f2_shoulder_t or diag.t_main) * 4, 40)), int(times[-1]))
    crop = int(np.searchsorted(times, x_max, side="right"))
    crop = max(5, min(crop, f.size))

    fig, axes = plt.subplots(3, 2, figsize=(12, 11), constrained_layout=True)
    axes = axes.ravel()
    axes[0].plot(times[:crop], f[:crop], lw=1.2)
    axes[0].set_title("raw f(t)")
    axes[0].grid(alpha=0.25)
    axes[1].plot(times[:crop], f[:crop], color="0.7", label="raw", lw=0.8)
    for window_size in SMOOTH_WINDOWS:
        smoothed = smooth_signal(f, window_size)
        if smoothed is not None:
            axes[1].plot(times[:crop], smoothed[:crop], lw=1.0, label=f"sg {window_size}")
    axes[1].set_title("smoothed f(t)")
    axes[1].legend(fontsize=7)
    axes[1].grid(alpha=0.25)
    f2_crop = max(3, min(f2.size, int(math.ceil(crop / 2))))
    axes[2].plot(f2_times[:f2_crop], f2[:f2_crop], lw=1.2, color="C1")
    axes[2].set_title("F2 parity-pair curve")
    axes[2].grid(alpha=0.25)
    axes[3].plot(times, np.log(np.maximum(f, 1e-300)), lw=1.0)
    axes[3].set_xlim(0, min(times[-1], max(x_max, int(np.searchsorted(np.cumsum(f), 0.9999 * max(np.sum(f), 1e-300)) + 50))))
    axes[3].set_title("log f(t), tail view")
    axes[3].grid(alpha=0.25)
    axes[4].plot(times[:crop], hazard[:crop], lw=1.1, color="C2")
    axes[4].set_title("hazard h(t)=f(t)/S(t-1)")
    axes[4].grid(alpha=0.25)
    log_f2 = np.log(np.maximum(f2, 1e-300))
    derivative = np.diff(log_f2)
    axes[5].plot(f2_times[1 : derivative.size + 1], derivative, lw=1.0, color="C4")
    axes[5].axhline(0.0, color="0.4", lw=0.8)
    axes[5].set_xlim(0, x_max)
    axes[5].set_title("log-derivative of F2")
    axes[5].grid(alpha=0.25)
    fig.suptitle(case_title(analysis))
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{analysis['case_id']}.pdf")
    plt.close(fig)


def plot_boundary_comparison(parent: dict[str, object], rows: list[dict[str, object]], out_dir: Path) -> None:
    parent_row = compact_case_row(parent)
    df = pd.DataFrame([parent_row] + rows)
    labels = [
        "boundary" if str(v) == str(parent["case_id"]) else str(v).replace(f"{parent['case_id']}_", "")
        for v in df["case_id"]
    ]
    x = np.arange(len(df))
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), constrained_layout=True)
    axes = axes.ravel()
    axes[0].bar(x, df["f2_shoulder_score"].astype(float))
    axes[0].set_title("F2 shoulder score")
    axes[1].bar(x, df["hazard_late_over_early"].astype(float))
    axes[1].set_title("late/early hazard")
    axes[2].bar(x, df["jsd_early_late_bits"].astype(float))
    axes[2].set_title("JSD(C_early, C_late)")
    axes[3].bar(x, df["max_positive_delta"].astype(float))
    axes[3].set_title("max positive Delta_k")
    axes[4].bar(x, df["target_shift_score"].astype(float))
    axes[4].set_title("target shift score")
    axes[5].bar(x, df["top_k_changed"].astype(float))
    axes[5].set_title("top k changed")
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle(f"Boundary null comparison for {parent['case_id']}")
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{parent['case_id']}.pdf")
    plt.close(fig)


def plot_group_decomposition(analysis: dict[str, object], out_dir: Path) -> None:
    dist = analysis["dist"]
    metrics = analysis["metrics"]
    groups = group_indices(int(analysis["N"]), metrics)
    crop = crop_index_for_mass(dist.f, mass_fraction=0.999, pad=30)
    fig, ax = plt.subplots(figsize=(8, 4.6), constrained_layout=True)
    for name, indices in groups.items():
        if not indices:
            continue
        group_f = np.sum(dist.f_by_k[:, [idx - 1 for idx in indices]], axis=1)
        ax.plot(dist.times[:crop], group_f[:crop], lw=1.1, label=name)
    ax.plot(dist.times[:crop], dist.f[:crop], color="0.2", lw=1.4, label="total")
    ax.set_title(f"group decomposition: {case_title(analysis)}")
    ax.set_xlabel("time t")
    ax.set_ylabel("group f_G(t)")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{analysis['case_id']}.pdf")
    plt.close(fig)


def plot_spectral_summary(analysis: dict[str, object], out_dir: Path) -> None:
    spectral = analysis["spectral"]
    if not isinstance(spectral, SpectralSummary) or not spectral.rows:
        return
    df = pd.DataFrame(spectral.rows)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
    axes[0].plot(df["mode"], df["lambda"], marker="o")
    axes[0].set_title("leading eigenvalues of Q")
    axes[0].set_xlabel("mode")
    axes[0].set_ylabel("lambda")
    axes[0].grid(alpha=0.25)
    axes[1].bar(df["mode"], df["tail_weight"])
    axes[1].set_title("mode tail-channel weight |alpha v^T R|")
    axes[1].set_xlabel("mode")
    axes[1].grid(axis="y", alpha=0.25)
    fig.suptitle(f"spectral check: {case_title(analysis)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{analysis['case_id']}.pdf")
    plt.close(fig)


def write_report(path: Path, cases: pd.DataFrame, target_shift: pd.DataFrame, fig_root: Path) -> None:
    fig_root_label = repo_rel(fig_root)
    reps = cases[cases["role"] == "representative"]
    controls = cases[cases["role"] == "negative_control"]
    interior = cases[cases["role"] == "interior_control"]
    robust_double_count = int(cases["f2_true_double_peak"].astype(bool).sum()) if not cases.empty else 0
    lines = [
        "# Stage-2b Mechanism-Focused Encounter Analysis",
        "",
        "Stage 2b asks whether the Stage-2 shoulders are boundary-induced delayed",
        "channels, same-target long tails, target-shift shoulders, or generic spectral",
        "tails. Double peaks are only claimed when F2 has two true local maxima with",
        "a visible valley.",
        "",
        "## Representative Cases",
        "",
        "| case | class | t_main | t_late | F2 true double? | JSD | top early k | top late k | target shift score |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for _, row in reps.iterrows():
        lines.append(
            f"| {row['case_id']} | {row['classification']} | {row['t_main']} | {row['t_late']} | "
            f"{bool(row['f2_true_double_peak'])} | {float(row['jsd_early_late_bits']):.4g} | "
            f"{int(row['top_k_early'])} | {int(row['top_k_late'])} | {float(row['target_shift_score']):.4g} |"
        )
    lines.extend(["", "## Negative Control", ""])
    if not controls.empty:
        for _, row in controls.iterrows():
            lines.append(
                f"- {row['case_id']}: classified `{row['classification']}`; raw/F2 diagnostics stay in "
                f"`{fig_root_label}/diagnostics/{row['case_id']}.pdf`."
            )
    lines.extend(["", "## Boundary Null Comparison", ""])
    if interior.empty:
        lines.append("No translated interior controls were available.")
    else:
        for parent, group in interior.groupby("boundary_parent", dropna=True):
            parent_row = cases[cases["case_id"] == parent]
            if parent_row.empty:
                continue
            pscore = float(parent_row.iloc[0]["f2_shoulder_score"])
            best_control = float(group["f2_shoulder_score"].astype(float).max())
            ratio = safe_ratio(pscore, best_control)
            label = "boundary-induced" if ratio >= 1.5 else "not boundary-specific"
            phazard = float(parent_row.iloc[0]["hazard_late_over_early"])
            best_hazard = float(group["hazard_late_over_early"].astype(float).max())
            pjsd = float(parent_row.iloc[0]["jsd_early_late_bits"])
            best_jsd = float(group["jsd_early_late_bits"].astype(float).max())
            pdelta = float(parent_row.iloc[0]["max_positive_delta"])
            best_delta = float(group["max_positive_delta"].astype(float).max())
            lines.append(
                f"- {parent}: boundary shoulder score {pscore:.4g}, best interior {best_control:.4g}, "
                f"ratio {ratio:.3g}; hazard late/early {phazard:.3g} vs best interior {best_hazard:.3g}; "
                f"JSD {pjsd:.3g} vs best interior {best_jsd:.3g}; max Delta_k {pdelta:.3g} vs best interior "
                f"{best_delta:.3g} -> {label}."
            )
    lines.extend(["", "## Target-Shift Reranking", ""])
    if target_shift.empty:
        lines.append("No target-shift candidates were produced.")
    else:
        lines.extend(
            [
                "| rank | class | N | start | q1 | q2 | score | JSD | late mass | max +Delta k | top k changed |",
                "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for _, row in target_shift.head(15).iterrows():
            lines.append(
                f"| {int(row['target_shift_rank'])} | {row['classification']} | {int(row['N'])} | "
                f"({int(row['start_a'])},{int(row['start_b'])}) | {float(row['q1']):.3g} | {float(row['q2']):.3g} | "
                f"{float(row['target_shift_score']):.3e} | {float(row['jsd_early_late_bits']):.3g} | "
                f"{float(row['late_window_mass']):.3g} | {int(row['max_positive_delta_k'])} | {bool(row['top_k_changed'])} |"
            )
    lines.extend(["", "## Spectral Interpretation", ""])
    for _, row in reps.iterrows():
        lines.append(
            f"- {row['case_id']}: leading lambda={float(row['leading_lambda']):.8f}, "
            f"timescale={float(row['leading_timescale']):.3g}, top R-channel k={row['leading_mode_top_k']}. "
            "Late behavior is treated as a slow-mode tail unless target-shift metrics separate it."
        )
    target_cases = cases[cases["role"] == "target_shift_candidate"]
    if not target_cases.empty:
        lines.extend(["", "Selected target-shift spectral checks:"])
        for _, row in target_cases.head(8).iterrows():
            lines.append(
                f"- {row['case_id']}: class={row['classification']}, "
                f"leading lambda={float(row['leading_lambda']):.8f}, "
                f"timescale={float(row['leading_timescale']):.3g}, "
                f"top R-channel k={row['leading_mode_top_k']}, "
                f"mode tail weight={float(row['leading_mode_tail_weight']):.3g}, "
                f"top k changed={bool(row['top_k_changed'])}."
            )
    class_counts = cases["classification"].value_counts().to_dict() if not cases.empty else {}
    lines.extend(["", "## Final Classification", ""])
    for label, count in class_counts.items():
        lines.append(f"- `{label}`: {int(count)}")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `artifacts/encounter_search/results/stage2b_cases.csv`",
            "- `artifacts/encounter_search/results/stage2b_target_shift.csv`",
            "- `artifacts/encounter_search/results/stage2b_report.md`",
            f"- `{fig_root_label}/diagnostics/`",
            f"- `{fig_root_label}/boundary_vs_interior/`",
            f"- `{fig_root_label}/group_decomposition/`",
            f"- `{fig_root_label}/spectral/`",
            "",
            "## Answer Summary",
            "",
            f"- Robust F2 double peaks found: {robust_double_count}.",
            "- A-C are not promoted to double peaks; they are shoulders/long tails under the F2 rule.",
            "- The target-shift reranking is usually dominated by small JSD values; changed top-k rows are flagged explicitly.",
            "- Group plots distinguish same-k tails from genuine late mass moving to new encounter-site groups.",
            "- Spectral plots report whether the late tail aligns with leading slow modes near lambda=1.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def group_indices(N: int, metrics: ChannelMetrics) -> dict[str, list[int]]:
    sites = set(range(1, int(N) + 1))
    boundary = {k for k in sites if k <= 3 or k >= int(N) - 2}
    main = {k for k in sites if abs(k - metrics.top_k_early) <= 1}
    shift = {k for k in sites if abs(k - metrics.max_positive_delta_k) <= 1}
    groups = {
        "boundary_near": sorted(boundary),
        "main_k_neighborhood": sorted(main - boundary),
        "interior_shift": sorted(shift - boundary - main),
    }
    used = set().union(*[set(v) for v in groups.values()])
    groups["far"] = sorted(sites - used)
    return groups


def window(center: int, size: int, radius: int) -> tuple[int, int]:
    if size <= 0:
        return 0, -1
    c = min(max(int(center), 0), size - 1)
    return max(0, c - int(radius)), min(size - 1, c + int(radius))


def normalise_or_zero(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    total = float(np.sum(arr))
    if total <= 0.0:
        return np.zeros_like(arr)
    return arr / total


def window_mean_by_time(values: np.ndarray, time_window: tuple[int, int]) -> float:
    start_t, end_t = time_window
    lo = max(int(start_t) - 1, 0)
    hi = min(int(end_t), len(values))
    if hi <= lo:
        return 0.0
    return float(np.mean(values[lo:hi]))


def safe_ratio(a: float, b: float) -> float:
    if abs(float(b)) < 1e-300:
        return float("inf") if float(a) > 0.0 else 1.0
    return float(a) / float(b)


def case_title(analysis: dict[str, object]) -> str:
    return (
        f"{analysis['case_id']}: N={analysis['N']}, start={analysis['start']}, "
        f"q1={float(analysis['q1']):g}, q2={float(analysis['q2']):g}, class={analysis['classification']}"
    )


if __name__ == "__main__":
    main()
