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
from scipy.signal import find_peaks

from encounter_search.shape import jensen_shannon_divergence
from encounter_search.shape import smooth_signal
from encounter_search.solver import AbsorptionChain
from encounter_search.solver import EncounterChain
from encounter_search.solver import Start
from encounter_search.solver import build_absorption_chain
from encounter_search.solver import build_chain
from encounter_search.solver import exact_distribution
from encounter_search.solver import exact_total_distribution


Q_GRID = (0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 0.85, 0.9)
N_VALUES = (15, 21, 31)
SMOOTH_WINDOWS = (7, 11, 21, 31)
REPORT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = REPORT_ROOT.parents[2]
DEFAULT_RESULTS_DIR = REPORT_ROOT / "artifacts" / "encounter_search" / "results"
DEFAULT_FIGURE_ROOT = REPORT_ROOT / "artifacts" / "encounter_search" / "figures"
NEGATIVE_CONTROL_RANKS = (1, 3, 25, 29)
ARTIFACT_REASONS = (
    "none",
    "parity_comb",
    "ballistic_short_distance",
    "smoothing_vanishes",
    "crossing_sensitive",
    "weak_target_shift",
)


@dataclass(frozen=True)
class Feature:
    index: int | None
    time: int | None
    height: float
    ratio: float
    valley_ratio: float
    score: float


@dataclass(frozen=True)
class CurveDiagnostics:
    label: str
    artifact_reason: str
    score: float
    t_main: int
    t_late: int | None
    raw_peaks: tuple[int, ...]
    raw_late: Feature
    smooth_peaks: dict[int, tuple[int, ...]]
    smooth_late_times: dict[int, int | None]
    smoothing_persistence: int
    f2: np.ndarray
    f2_main_n: int
    f2_main_t: int
    f2_late_t: int | None
    f2_peak_late: Feature
    f2_shoulder_t: int | None
    f2_shoulder_excess: float
    f2_shoulder_score: float
    f2_peaks: tuple[int, ...]
    oscillation_index: float
    repeat2_peaks: bool
    min_late_t: int

    @property
    def has_f2_late(self) -> bool:
        return self.f2_late_t is not None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Stage-2 artifact-resistant encounter search")
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--max-t", type=int, default=6_000)
    parser.add_argument("--detail-max-t", type=int, default=120_000)
    parser.add_argument("--survival-tol", type=float, default=1e-12)
    parser.add_argument("--top-nonartifact", type=int, default=50)
    parser.add_argument("--top-artifacts", type=int, default=20)
    args = parser.parse_args(argv)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    figure_root = DEFAULT_FIGURE_ROOT / "stage2"
    (figure_root / "top_nonartifact").mkdir(parents=True, exist_ok=True)
    (figure_root / "negative_controls").mkdir(parents=True, exist_ok=True)

    print("loading Stage-1 negative controls")
    controls = load_negative_controls(out / "top_shape_cases.csv")
    print("running Stage-2 scan")
    scan_df = run_scan(max_t=args.max_t, survival_tol=args.survival_tol)

    robust_pool = scan_df[scan_df["stage2_label"].isin(["robust_double_peak", "robust_shoulder"])]
    robust_pool = robust_pool.sort_values("stage2_score", ascending=False).head(
        max(args.top_nonartifact * 3, 75)
    )
    weak_pool = scan_df[~scan_df.index.isin(robust_pool.index)].sort_values(
        "stage2_score", ascending=False
    ).head(max(args.top_artifacts * 3, 60))

    print(f"enriching {len(robust_pool)} robust-pool rows")
    enriched_robust = [
        enrich_candidate(row, args.survival_tol, args.detail_max_t) for _, row in robust_pool.iterrows()
    ]
    print(f"enriching {len(weak_pool)} weak/artifact-pool rows")
    enriched_weak = [
        enrich_candidate(row, args.survival_tol, args.detail_max_t) for _, row in weak_pool.iterrows()
    ]
    print("enriching negative controls")
    enriched_controls = [
        enrich_candidate(control, args.survival_tol, args.detail_max_t, is_control=True)
        for _, control in controls.iterrows()
    ]

    enriched_df = pd.DataFrame(enriched_robust + enriched_weak + enriched_controls)
    nonartifact_df = enriched_df[
        enriched_df["final_label"].isin(["robust_double_peak", "robust_shoulder"])
        & (enriched_df["is_control"] == False)  # noqa: E712
    ].sort_values("final_score", ascending=False)
    artifact_df = enriched_df[
        ~enriched_df.index.isin(nonartifact_df.index)
    ].sort_values(["is_control", "final_score"], ascending=[False, False])

    shape_out = nonartifact_df.head(args.top_nonartifact).copy()
    artifact_out = pd.concat(
        [
            artifact_df[artifact_df["is_control"] == True],  # noqa: E712
            artifact_df[artifact_df["is_control"] == False].head(args.top_artifacts),  # noqa: E712
        ],
        ignore_index=True,
    )

    shape_out = _assign_rank(shape_out, "stage2_rank")
    artifact_out = _assign_rank(artifact_out, "artifact_rank")

    shape_out.to_csv(out / "stage2_shape_cases.csv", index=False)
    artifact_out.to_csv(out / "stage2_artifacts.csv", index=False)
    print(f"wrote {out / 'stage2_shape_cases.csv'}")
    print(f"wrote {out / 'stage2_artifacts.csv'}")

    print("plotting top non-artifact cases and controls")
    for _, row in shape_out.head(15).iterrows():
        plot_case_bundle(row, figure_root / "top_nonartifact", args.survival_tol, args.detail_max_t)
    for _, row in artifact_out[artifact_out["is_control"] == True].iterrows():  # noqa: E712
        plot_case_bundle(row, figure_root / "negative_controls", args.survival_tol, args.detail_max_t)

    write_report(out / "stage2_report.md", shape_out, artifact_out, scan_df, figure_root)
    print(f"wrote {out / 'stage2_report.md'}")


def load_negative_controls(stage1_csv: Path) -> pd.DataFrame:
    if not stage1_csv.exists():
        fallback = DEFAULT_RESULTS_DIR / "top_shape_cases.csv"
        if fallback.exists():
            stage1_csv = fallback
        else:
            raise FileNotFoundError(f"Stage-1 top cases not found: {stage1_csv}")
    df = pd.read_csv(stage1_csv)
    controls = df[df["rank"].isin(NEGATIVE_CONTROL_RANKS)].copy()
    if len(controls) != len(NEGATIVE_CONTROL_RANKS):
        missing = sorted(set(NEGATIVE_CONTROL_RANKS) - set(controls["rank"].astype(int)))
        raise ValueError(f"missing Stage-1 negative-control ranks: {missing}")
    rows = []
    for _, row in controls.iterrows():
        rows.append(
            {
                "source": "stage1_negative_control",
                "stage1_rank": int(row["rank"]),
                "N": int(row["N"]),
                "start_a": int(row["start_a"]),
                "start_b": int(row["start_b"]),
                "q1": float(row["q1"]),
                "q2": float(row["q2"]),
                "scan_mode": "stage1_control",
                "scan_tail_mass": np.nan,
                "scan_reached_tol": np.nan,
                "scan_steps": np.nan,
            }
        )
    return pd.DataFrame(rows)


def run_scan(*, max_t: int, survival_tol: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for N in N_VALUES:
        starts = list(iter_scan_starts(N))
        scan_mode = "all_ordered_starts"
        for q1 in Q_GRID:
            for q2 in Q_GRID:
                print(f"stage2 scan N={N} q1={q1:g} q2={q2:g} starts={len(starts)}")
                chain = build_chain(N, q1, q2)
                curves, tails, reached = all_start_total_curves(
                    chain,
                    max_t=max_t,
                    survival_tol=survival_tol,
                )
                start_to_index = {state: i for i, state in enumerate(chain.transient_states)}
                for start in starts:
                    start_idx = start_to_index[start]
                    f = curves[:, start_idx]
                    diag = diagnose_curve(f)
                    row = diagnostics_row(diag)
                    row.update(
                        {
                            "source": "stage2_scan",
                            "stage1_rank": "",
                            "N": N,
                            "start_a": start[0],
                            "start_b": start[1],
                            "q1": q1,
                            "q2": q2,
                            "scan_mode": scan_mode,
                            "scan_tail_mass": float(tails[start_idx]),
                            "scan_reached_tol": bool(reached),
                            "scan_steps": curves.shape[0],
                        }
                    )
                    rows.append(row)
    return pd.DataFrame(rows)


def iter_scan_starts(N: int) -> Iterable[Start]:
    for a in range(1, int(N) + 1):
        for b in range(1, int(N) + 1):
            if a != b:
                yield (a, b)


def all_start_total_curves(
    chain: EncounterChain,
    *,
    max_t: int,
    survival_tol: float,
) -> tuple[np.ndarray, np.ndarray, bool]:
    h = np.asarray(chain.R.sum(axis=1)).reshape(-1)
    values = h.copy()
    survival = np.ones(chain.Q.shape[0], dtype=float)
    curves = np.empty((int(max_t), chain.Q.shape[0]), dtype=float)
    reached = False
    steps = 0
    for idx in range(int(max_t)):
        curves[idx, :] = values
        survival = np.asarray(chain.Q @ survival).reshape(-1)
        steps = idx + 1
        if float(np.max(survival)) <= float(survival_tol):
            reached = True
            break
        values = np.asarray(chain.Q @ values).reshape(-1)
    return curves[:steps, :], survival, reached


def diagnose_curve(f: np.ndarray) -> CurveDiagnostics:
    y = np.asarray(f, dtype=float).reshape(-1)
    if y.size == 0 or float(np.max(y, initial=0.0)) <= 0.0:
        empty = Feature(None, None, 0.0, 0.0, 1.0, 0.0)
        return CurveDiagnostics(
            label="artifact",
            artifact_reason="smoothing_vanishes",
            score=0.0,
            t_main=0,
            t_late=None,
            raw_peaks=(),
            raw_late=empty,
            smooth_peaks={w: () for w in SMOOTH_WINDOWS},
            smooth_late_times={w: None for w in SMOOTH_WINDOWS},
            smoothing_persistence=0,
            f2=np.array([], dtype=float),
            f2_main_n=0,
            f2_main_t=0,
            f2_late_t=None,
            f2_peak_late=empty,
            f2_shoulder_t=None,
            f2_shoulder_excess=0.0,
            f2_shoulder_score=0.0,
            f2_peaks=(),
            oscillation_index=0.0,
            repeat2_peaks=False,
            min_late_t=0,
        )

    main_idx = int(np.argmax(y))
    t_main = main_idx + 1
    min_late_t = max(t_main + 8, int(math.ceil(1.5 * t_main)))
    raw_peak_idx = detect_peak_indices(y, prominence_ratio=1e-5, distance=1)
    raw_late = best_late_peak(y, raw_peak_idx, main_idx, min_late_t=min_late_t, pair_curve=False)

    smooth_peaks: dict[int, tuple[int, ...]] = {}
    smooth_late_times: dict[int, int | None] = {}
    smooth_lates: list[Feature] = []
    for window in SMOOTH_WINDOWS:
        smoothed = smooth_signal(y, window)
        if smoothed is None:
            smooth_peaks[window] = ()
            smooth_late_times[window] = None
            smooth_lates.append(Feature(None, None, 0.0, 0.0, 1.0, 0.0))
            continue
        peaks = detect_peak_indices(smoothed, prominence_ratio=1e-5, distance=1)
        late = best_late_peak(smoothed, peaks, int(np.argmax(smoothed)), min_late_t=min_late_t, pair_curve=False)
        smooth_peaks[window] = tuple(int(p + 1) for p in peaks)
        smooth_late_times[window] = late.time
        smooth_lates.append(late)

    smoothing_persistence = sum(
        1
        for late in smooth_lates
        if late.time is not None
        and raw_late.time is not None
        and abs(int(late.time) - int(raw_late.time)) <= max(4, int(0.25 * max(raw_late.time - t_main, 1)))
    )

    f2 = parity_pair_curve(y)
    f2_main_idx = int(np.argmax(f2)) if f2.size else 0
    f2_main_n = f2_main_idx + 1
    f2_main_t = 2 * f2_main_n
    f2_peaks_idx = detect_peak_indices(f2, prominence_ratio=1e-5, distance=1)
    f2_late_peak = best_late_peak(
        f2,
        f2_peaks_idx,
        f2_main_idx,
        min_late_t=min_late_t,
        pair_curve=True,
    )
    f2_shoulder_t, f2_shoulder_excess, f2_shoulder_score = f2_shoulder_diagnostic(
        f2,
        min_late_t=min_late_t,
    )
    f2_late_t = f2_late_peak.time or f2_shoulder_t

    centers = [t for t in [t_main, raw_late.time] if t is not None]
    oscillation = local_oscillation_index(y, centers)
    repeat2 = peaks_repeat_every_two(tuple(int(p + 1) for p in raw_peak_idx), t_main=t_main)

    raw_has_late = raw_late.time is not None
    f2_has_late = f2_late_t is not None
    f2_peak_has_late = f2_late_peak.time is not None

    artifact_reason = "none"
    if t_main <= 6 and repeat2 and not f2_peak_has_late:
        artifact_reason = "ballistic_short_distance"
    elif raw_has_late and not f2_has_late and oscillation >= 0.25:
        artifact_reason = "parity_comb"
    elif raw_has_late and smoothing_persistence == 0 and not f2_has_late:
        artifact_reason = "smoothing_vanishes"

    robust_double = (
        artifact_reason == "none"
        and raw_has_late
        and smoothing_persistence >= 2
        and f2_peak_has_late
        and raw_late.time is not None
        and raw_late.time >= min_late_t
    )
    robust_shoulder = (
        artifact_reason == "none"
        and f2_shoulder_t is not None
        and f2_shoulder_excess >= math.log(1.20)
        and f2_shoulder_t >= min_late_t
    )

    if robust_double:
        label = "robust_double_peak"
        score = (
            raw_late.score
            * max(f2_late_peak.ratio, 0.05)
            * (1.0 + smoothing_persistence / len(SMOOTH_WINDOWS))
            / (1.0 + oscillation)
        )
        t_late = raw_late.time
    elif robust_shoulder:
        label = "robust_shoulder"
        gap = max((f2_shoulder_t or min_late_t) - t_main, 1)
        score = f2_shoulder_score * math.sqrt(gap) / (1.0 + 0.5 * oscillation)
        t_late = f2_shoulder_t
    elif artifact_reason != "none":
        label = "artifact"
        score = raw_late.score if raw_has_late else f2_shoulder_score
        t_late = raw_late.time or f2_late_t
    elif raw_has_late or f2_has_late:
        label = "weak"
        score = max(raw_late.score, f2_shoulder_score, f2_late_peak.score)
        t_late = raw_late.time or f2_late_t
    else:
        label = "unimodal"
        score = 0.0
        t_late = None

    return CurveDiagnostics(
        label=label,
        artifact_reason=artifact_reason,
        score=float(score),
        t_main=t_main,
        t_late=t_late,
        raw_peaks=tuple(int(p + 1) for p in raw_peak_idx),
        raw_late=raw_late,
        smooth_peaks=smooth_peaks,
        smooth_late_times=smooth_late_times,
        smoothing_persistence=int(smoothing_persistence),
        f2=f2,
        f2_main_n=f2_main_n,
        f2_main_t=f2_main_t,
        f2_late_t=f2_late_t,
        f2_peak_late=f2_late_peak,
        f2_shoulder_t=f2_shoulder_t,
        f2_shoulder_excess=float(f2_shoulder_excess),
        f2_shoulder_score=float(f2_shoulder_score),
        f2_peaks=tuple(int(p + 1) for p in f2_peaks_idx),
        oscillation_index=float(oscillation),
        repeat2_peaks=bool(repeat2),
        min_late_t=int(min_late_t),
    )


def detect_peak_indices(y: np.ndarray, *, prominence_ratio: float, distance: int) -> np.ndarray:
    arr = np.asarray(y, dtype=float).reshape(-1)
    if arr.size < 3 or float(np.max(arr, initial=0.0)) <= 0.0:
        return np.array([], dtype=int)
    prominence = max(float(np.max(arr)) * float(prominence_ratio), 1e-300)
    peaks, _ = find_peaks(arr, prominence=prominence, distance=max(1, int(distance)))
    return peaks.astype(int)


def best_late_peak(
    y: np.ndarray,
    peaks: np.ndarray,
    main_idx: int,
    *,
    min_late_t: int,
    pair_curve: bool,
) -> Feature:
    arr = np.asarray(y, dtype=float).reshape(-1)
    if arr.size == 0:
        return Feature(None, None, 0.0, 0.0, 1.0, 0.0)
    main_height = max(float(arr[int(main_idx)]), 1e-300)
    best: Feature | None = None
    for idx in peaks:
        time = 2 * (int(idx) + 1) if pair_curve else int(idx) + 1
        if time < int(min_late_t):
            continue
        lo, hi = sorted((int(main_idx), int(idx)))
        if hi <= lo:
            continue
        valley = float(np.min(arr[lo : hi + 1]))
        ratio = float(arr[int(idx)]) / main_height
        valley_ratio = valley / main_height
        separation = time - (2 * (int(main_idx) + 1) if pair_curve else int(main_idx) + 1)
        score = separation * ratio * max(0.02, 1.0 - valley_ratio)
        feature = Feature(int(idx), int(time), float(arr[int(idx)]), ratio, valley_ratio, float(score))
        if best is None or feature.score > best.score:
            best = feature
    return best or Feature(None, None, 0.0, 0.0, 1.0, 0.0)


def parity_pair_curve(f: np.ndarray) -> np.ndarray:
    arr = np.asarray(f, dtype=float).reshape(-1)
    if arr.size == 0:
        return arr
    if arr.size % 2 == 1:
        arr = np.pad(arr, (0, 1))
    return arr[0::2] + arr[1::2]


def f2_shoulder_diagnostic(f2: np.ndarray, *, min_late_t: int) -> tuple[int | None, float, float]:
    y = np.asarray(f2, dtype=float).reshape(-1)
    if y.size < 12 or float(np.max(y, initial=0.0)) <= 0.0:
        return None, 0.0, 0.0
    main_idx = int(np.argmax(y))
    main_height = max(float(y[main_idx]), 1e-300)
    mass = np.cumsum(y)
    crop = int(np.searchsorted(mass, 0.999 * max(float(mass[-1]), 1e-300)))
    crop = min(max(crop, main_idx + 8), y.size - 1)
    idx = np.arange(y.size)
    valid = (idx >= main_idx + 2) & (idx <= crop) & (y > main_height * 1e-8)
    if int(np.sum(valid)) < 8:
        return None, 0.0, 0.0

    x_fit = idx[valid].astype(float)
    log_fit = np.log(y[valid])
    keep = np.ones_like(log_fit, dtype=bool)
    coeff = np.polyfit(x_fit, log_fit, 1)
    for _ in range(2):
        baseline = coeff[0] * x_fit + coeff[1]
        resid = log_fit - baseline
        threshold = np.quantile(resid, 0.60)
        keep = resid <= threshold
        if int(np.sum(keep)) < 4:
            break
        coeff = np.polyfit(x_fit[keep], log_fit[keep], 1)

    baseline_all = coeff[0] * idx.astype(float) + coeff[1]
    residual = np.full(y.shape, -np.inf, dtype=float)
    positive = y > 0.0
    residual[positive] = np.log(y[positive]) - baseline_all[positive]
    late_mask = (2 * (idx + 1) >= int(min_late_t)) & (idx <= crop) & positive
    late_mask &= y >= main_height * 5e-5
    if not np.any(late_mask):
        return None, 0.0, 0.0
    late_indices = np.where(late_mask)[0]
    best_idx = int(late_indices[np.argmax(residual[late_indices])])
    excess = float(residual[best_idx])
    if not np.isfinite(excess) or excess <= math.log(1.20):
        return None, max(excess, 0.0), 0.0
    local = residual[max(main_idx + 1, best_idx - 2) : min(y.size, best_idx + 3)]
    width = int(np.sum(local > math.log(1.10)))
    score = max(excess, 0.0) * max(width, 1) * float(y[best_idx] / main_height)
    return 2 * (best_idx + 1), excess, float(score)


def local_oscillation_index(f: np.ndarray, centers_t: list[int]) -> float:
    y = np.asarray(f, dtype=float).reshape(-1)
    if y.size == 0:
        return 0.0
    values: list[float] = []
    for t in centers_t:
        center = int(t) - 1
        lo = max(0, center - 6)
        hi = min(y.size, center + 7)
        local = y[lo:hi]
        total = float(np.sum(local))
        if total <= 0.0:
            continue
        times = np.arange(lo + 1, hi + 1)
        odd = float(np.sum(local[times % 2 == 1]))
        even = float(np.sum(local[times % 2 == 0]))
        parity_contrast = abs(odd - even) / total
        if local.size >= 3:
            one_step = float(np.sum(np.abs(np.diff(local))))
            two_step = float(np.sum(np.abs(local[2:] - local[:-2])))
            alternating_excess = max(0.0, (one_step - two_step) / max(one_step, 1e-300))
        else:
            alternating_excess = 0.0
        values.append(0.65 * parity_contrast + 0.35 * alternating_excess)
    return float(max(values)) if values else 0.0


def peaks_repeat_every_two(peaks_t: tuple[int, ...], *, t_main: int) -> bool:
    nearby = [int(t) for t in peaks_t if int(t) >= int(t_main) and int(t) <= int(t_main) + 12]
    if len(nearby) < 3:
        return False
    diffs = np.diff(nearby)
    return bool(np.mean(diffs == 2) >= 0.70)


def diagnostics_row(diag: CurveDiagnostics) -> dict[str, object]:
    row: dict[str, object] = {
        "stage2_label": diag.label,
        "artifact_reason": diag.artifact_reason,
        "stage2_score": diag.score,
        "t_main": diag.t_main,
        "t_late": "" if diag.t_late is None else diag.t_late,
        "min_late_t": diag.min_late_t,
        "raw_peaks": _join_ints(diag.raw_peaks),
        "raw_late_ratio": diag.raw_late.ratio,
        "raw_late_valley_ratio": diag.raw_late.valley_ratio,
        "smooth7_peaks": _join_ints(diag.smooth_peaks[7]),
        "smooth11_peaks": _join_ints(diag.smooth_peaks[11]),
        "smooth21_peaks": _join_ints(diag.smooth_peaks[21]),
        "smooth31_peaks": _join_ints(diag.smooth_peaks[31]),
        "smooth7_late_t": _empty_none(diag.smooth_late_times[7]),
        "smooth11_late_t": _empty_none(diag.smooth_late_times[11]),
        "smooth21_late_t": _empty_none(diag.smooth_late_times[21]),
        "smooth31_late_t": _empty_none(diag.smooth_late_times[31]),
        "smoothing_persistence": diag.smoothing_persistence,
        "f2_peaks_n": _join_ints(diag.f2_peaks),
        "f2_main_n": diag.f2_main_n,
        "f2_main_t": diag.f2_main_t,
        "f2_late_t": _empty_none(diag.f2_late_t),
        "f2_peak_late_ratio": diag.f2_peak_late.ratio,
        "f2_peak_late_valley_ratio": diag.f2_peak_late.valley_ratio,
        "f2_shoulder_t": _empty_none(diag.f2_shoulder_t),
        "f2_shoulder_excess": diag.f2_shoulder_excess,
        "f2_shoulder_score": diag.f2_shoulder_score,
        "oscillation_index": diag.oscillation_index,
        "repeat2_peaks": diag.repeat2_peaks,
    }
    return row


def enrich_candidate(
    row: pd.Series,
    survival_tol: float,
    max_t: int,
    *,
    is_control: bool = False,
) -> dict[str, object]:
    N = int(row["N"])
    q1 = float(row["q1"])
    q2 = float(row["q2"])
    start = (int(row["start_a"]), int(row["start_b"]))
    chain = build_chain(N, q1, q2)
    dist = exact_distribution(chain, start, survival_tol=survival_tol, max_t=max_t)
    diag = diagnose_curve(dist.f)
    attribution = channel_attribution(dist, diag)

    crossing = comparison_distribution(
        N,
        q1,
        q2,
        start,
        survival_tol=survival_tol,
        max_t=max_t,
        absorption_mode="co_location_or_crossing",
        reflect_mode="stay",
    )
    bounce = comparison_distribution(
        N,
        q1,
        q2,
        start,
        survival_tol=survival_tol,
        max_t=max_t,
        absorption_mode="co_location",
        reflect_mode="bounce",
    )
    crossing_diag = diagnose_curve(crossing.f)
    bounce_diag = diagnose_curve(bounce.f)

    final_label = diag.label
    artifact_reason = diag.artifact_reason
    if final_label in {"robust_double_peak", "robust_shoulder"}:
        if attribution["attribution_label"] == "weak":
            final_label = "weak"
            artifact_reason = "weak_target_shift"
        elif crossing_diag.label not in {"robust_double_peak", "robust_shoulder"} and bounce_diag.label not in {
            "robust_double_peak",
            "robust_shoulder",
        }:
            final_label = "weak"
            artifact_reason = "crossing_sensitive"

    final_score = diag.score
    if final_label == "weak":
        final_score *= 0.5
    if final_label == "artifact":
        final_score *= 0.2

    out = {
        "is_control": bool(is_control),
        "source": row.get("source", "stage2_scan"),
        "stage1_rank": row.get("stage1_rank", ""),
        "N": N,
        "start_a": start[0],
        "start_b": start[1],
        "q1": q1,
        "q2": q2,
        "scan_mode": row.get("scan_mode", ""),
        "scan_tail_mass": row.get("scan_tail_mass", np.nan),
        "scan_reached_tol": row.get("scan_reached_tol", np.nan),
        "scan_steps": row.get("scan_steps", np.nan),
        "base_mass": dist.mass,
        "base_tail_mass": dist.tail_mass,
        "base_reached_tol": dist.reached_tol,
        "base_mean": dist.mean,
        "stage2_label": diag.label,
        "final_label": final_label,
        "artifact_reason": artifact_reason,
        "stage2_score": diag.score,
        "final_score": final_score,
    }
    out.update(diagnostics_row(diag))
    out.update(attribution)
    out.update(
        {
            "crossing_label": crossing_diag.label,
            "crossing_artifact_reason": crossing_diag.artifact_reason,
            "crossing_t_late": _empty_none(crossing_diag.t_late),
            "crossing_score": crossing_diag.score,
            "crossing_mean": crossing.mean,
            "crossing_tail_mass": crossing.tail_mass,
            "crossing_survives": crossing_diag.label in {"robust_double_peak", "robust_shoulder"},
            "bounce_label": bounce_diag.label,
            "bounce_artifact_reason": bounce_diag.artifact_reason,
            "bounce_t_late": _empty_none(bounce_diag.t_late),
            "bounce_score": bounce_diag.score,
            "bounce_mean": bounce.mean,
            "bounce_tail_mass": bounce.tail_mass,
            "bounce_survives": bounce_diag.label in {"robust_double_peak", "robust_shoulder"},
        }
    )
    return out


def channel_attribution(dist, diag: CurveDiagnostics) -> dict[str, object]:
    f = dist.f
    f_by_k = dist.f_by_k
    early_center = max(diag.t_main - 1, 0)
    late_center = (diag.t_late - 1) if diag.t_late is not None else min(f.size - 1, early_center + 12)
    radius = max(3, min(21, int(max((late_center - early_center) // 5, 3))))
    early_lo, early_hi = _window(early_center, f.size, radius)
    late_lo, late_hi = _window(late_center, f.size, radius)
    early_by_k = np.sum(f_by_k[early_lo : early_hi + 1, :], axis=0)
    late_by_k = np.sum(f_by_k[late_lo : late_hi + 1, :], axis=0)
    C_early = _normalise_or_zero(early_by_k)
    C_late = _normalise_or_zero(late_by_k)
    delta = C_late - C_early
    jsd = jensen_shannon_divergence(C_early, C_late)
    top_early = int(np.argmax(C_early)) if C_early.size else 0
    top_late = int(np.argmax(C_late)) if C_late.size else 0
    top_delta = int(np.argmax(np.abs(delta))) if delta.size else 0
    top_channel = top_late if C_late[top_late] >= C_early[top_early] else top_early
    channel_diag = diagnose_curve(f_by_k[:, top_channel]) if f_by_k.size else None
    channel_robust = (
        channel_diag is not None and channel_diag.label in {"robust_double_peak", "robust_shoulder"}
    )
    if jsd >= 0.05 and top_late != top_early:
        attribution_label = "target_mixture"
    elif top_late == top_early and channel_robust:
        attribution_label = "same_target_multi_path"
    else:
        attribution_label = "weak"

    return {
        "early_window": f"{int(dist.times[early_lo])}-{int(dist.times[early_hi])}",
        "late_window": f"{int(dist.times[late_lo])}-{int(dist.times[late_hi])}",
        "early_window_mass": float(np.sum(f[early_lo : early_hi + 1])),
        "late_window_mass": float(np.sum(f[late_lo : late_hi + 1])),
        "top_k_early": top_early + 1,
        "top_k_late": top_late + 1,
        "top_k_delta": top_delta + 1,
        "max_delta": float(delta[top_delta]) if delta.size else 0.0,
        "jsd_early_late_bits": float(jsd),
        "C_early_top5": _top_entries(C_early, n=5),
        "C_late_top5": _top_entries(C_late, n=5),
        "Delta_top5": _top_entries(delta, n=5, by_abs=True),
        "attribution_label": attribution_label,
        "top_channel_label": "" if channel_diag is None else channel_diag.label,
        "top_channel_t_late": "" if channel_diag is None else _empty_none(channel_diag.t_late),
        "top_channel_f2_late_t": "" if channel_diag is None else _empty_none(channel_diag.f2_late_t),
    }


def comparison_distribution(
    N: int,
    q1: float,
    q2: float,
    start: Start,
    *,
    survival_tol: float,
    max_t: int,
    absorption_mode: str,
    reflect_mode: str,
):
    if absorption_mode == "co_location" and reflect_mode == "stay":
        chain = build_absorption_chain(N, q1, q2)
    else:
        chain = build_absorption_chain(
            N,
            q1,
            q2,
            absorption_mode=absorption_mode,  # type: ignore[arg-type]
            reflect_mode=reflect_mode,  # type: ignore[arg-type]
        )
    return exact_total_distribution(chain, start, survival_tol=survival_tol, max_t=max_t)


def plot_case_bundle(row: pd.Series, out_dir: Path, survival_tol: float, max_t: int) -> None:
    N = int(row["N"])
    q1 = float(row["q1"])
    q2 = float(row["q2"])
    start = (int(row["start_a"]), int(row["start_b"]))
    chain = build_chain(N, q1, q2)
    dist = exact_distribution(chain, start, survival_tol=survival_tol, max_t=max_t)
    diag = diagnose_curve(dist.f)
    crossing = comparison_distribution(
        N,
        q1,
        q2,
        start,
        survival_tol=survival_tol,
        max_t=max_t,
        absorption_mode="co_location_or_crossing",
        reflect_mode="stay",
    )
    bounce_chain = build_chain(N, q1, q2, reflect_mode="bounce")
    bounce = exact_distribution(bounce_chain, start, survival_tol=survival_tol, max_t=max_t)
    attribution = channel_attribution(dist, diag)

    crop = crop_index_for_mass(dist.f, mass_fraction=0.999, pad=20)
    crop = min(crop, dist.f.size)
    top_channels = sorted(
        {
            int(row.get("top_k_early", 1)) - 1 if not pd.isna(row.get("top_k_early", 1)) else 0,
            int(row.get("top_k_late", 1)) - 1 if not pd.isna(row.get("top_k_late", 1)) else 0,
        }
    )

    fig, axes = plt.subplots(4, 2, figsize=(12, 14), constrained_layout=True)
    axes = axes.ravel()

    axes[0].plot(dist.times[:crop], dist.f[:crop], lw=1.2, color="C0")
    axes[0].set_title("raw f(t)")
    axes[0].set_xlabel("t")
    axes[0].set_ylabel("f")
    axes[0].grid(alpha=0.25)
    for t in [diag.t_main, diag.t_late]:
        if t:
            axes[0].axvline(int(t), color="C3" if t == diag.t_late else "C2", ls="--", lw=0.9)
    inset = axes[0].inset_axes([0.56, 0.45, 0.40, 0.48])
    early_crop = min(crop, max(30, int(diag.min_late_t + 10)))
    inset.plot(dist.times[:early_crop], dist.f[:early_crop], lw=1.0)
    inset.set_title("early", fontsize=8)
    inset.tick_params(labelsize=7)

    axes[1].plot(dist.times[:crop], dist.f[:crop], color="0.65", lw=0.9, label="raw")
    for window in SMOOTH_WINDOWS:
        smoothed = smooth_signal(dist.f, window)
        if smoothed is not None:
            axes[1].plot(dist.times[:crop], smoothed[:crop], lw=1.0, label=f"sg {window}")
    axes[1].set_title("smoothed f(t)")
    axes[1].set_xlabel("t")
    axes[1].legend(fontsize=7)
    axes[1].grid(alpha=0.25)

    f2 = parity_pair_curve(dist.f)
    f2_times = 2 * (np.arange(f2.size) + 1)
    f2_crop = min(f2.size, max(3, int(math.ceil(crop / 2))))
    axes[2].plot(f2_times[:f2_crop], f2[:f2_crop], lw=1.2, color="C1")
    axes[2].set_title("F2[n]=f(2n-1)+f(2n)")
    axes[2].set_xlabel("paired t")
    axes[2].grid(alpha=0.25)
    if diag.f2_late_t:
        axes[2].axvline(int(diag.f2_late_t), color="C3", ls="--", lw=0.9)

    for k in top_channels:
        axes[3].plot(dist.times[:crop], dist.f_by_k[:crop, k], lw=1.0, label=f"k={k + 1}")
    axes[3].set_title("top f_k(t)")
    axes[3].set_xlabel("t")
    axes[3].legend(fontsize=7)
    axes[3].grid(alpha=0.25)

    mesh = axes[4].imshow(
        dist.f_by_k[:crop, :].T,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        extent=[float(dist.times[0]), float(dist.times[crop - 1]), 0.5, N + 0.5],
        cmap="magma",
    )
    axes[4].set_title("k-time heatmap")
    axes[4].set_xlabel("t")
    axes[4].set_ylabel("k")
    fig.colorbar(mesh, ax=axes[4], fraction=0.046, pad=0.02)

    C_early = _parse_top_distribution(attribution["C_early_top5"], N)
    C_late = _parse_top_distribution(attribution["C_late_top5"], N)
    x = np.arange(1, N + 1)
    axes[5].bar(x - 0.2, C_early, width=0.4, label="early")
    axes[5].bar(x + 0.2, C_late, width=0.4, label="late")
    axes[5].set_title("early/late C_k")
    axes[5].set_xlabel("k")
    axes[5].legend(fontsize=7)

    comp_crop = min(crop, crossing.f.size)
    axes[6].plot(dist.times[:crop], dist.f[:crop], lw=1.0, label="co-location")
    axes[6].plot(crossing.times[:comp_crop], crossing.f[:comp_crop], lw=1.0, label="co-location or crossing")
    axes[6].set_title("crossing comparison")
    axes[6].set_xlabel("t")
    axes[6].legend(fontsize=7)
    axes[6].grid(alpha=0.25)

    bounce_crop = min(crop, bounce.f.size)
    axes[7].plot(dist.times[:crop], dist.f[:crop], lw=1.0, label="stay")
    axes[7].plot(bounce.times[:bounce_crop], bounce.f[:bounce_crop], lw=1.0, label="bounce")
    axes[7].set_title("stay/bounce comparison")
    axes[7].set_xlabel("t")
    axes[7].legend(fontsize=7)
    axes[7].grid(alpha=0.25)

    title = (
        f"N={N}, start={start}, q1={q1:g}, q2={q2:g}, "
        f"label={row.get('final_label', diag.label)}, reason={row.get('artifact_reason', diag.artifact_reason)}"
    )
    fig.suptitle(title)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / case_slug(row) / "diagnostic_bundle.pdf"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def write_report(
    path: Path,
    shape_df: pd.DataFrame,
    artifact_df: pd.DataFrame,
    scan_df: pd.DataFrame,
    figure_root: Path,
) -> None:
    figure_root_label = repo_rel(figure_root)
    controls = artifact_df[artifact_df["is_control"] == True]  # noqa: E712
    robust_double = shape_df[shape_df["final_label"] == "robust_double_peak"]
    robust_shoulder = shape_df[shape_df["final_label"] == "robust_shoulder"]
    lines = [
        "# Stage-2 Artifact-Resistant 1D Encounter Search",
        "",
        "Stage 2 treats the Stage-1 distance-4, extreme-mobility cases as negative",
        "controls. Ranking is now based on raw peaks, Savitzky-Golay persistence",
        "for windows 7/11/21/31, the parity-pair curve `F2[n]=f(2n-1)+f(2n)`,",
        "a local oscillation index, target-channel attribution, and crossing/bounce",
        "sensitivity checks.",
        "",
        "## Scan Summary",
        "",
        f"- scanned rows: {len(scan_df)}",
        f"- N values: {', '.join(str(n) for n in N_VALUES)}",
        f"- q grid: {', '.join(f'{q:g}' for q in Q_GRID)}",
        "- starts: all ordered off-diagonal starts for N=15, N=21, and N=31",
        f"- non-artifact rows retained: {len(shape_df)}",
        f"- weak/artifact rows retained: {len(artifact_df)}",
        f"- figures: `{figure_root_label}/top_nonartifact/` and `{figure_root_label}/negative_controls/`",
        "",
        "## 1. Stage-1 Rejections",
        "",
    ]
    if controls.empty:
        lines.append("No Stage-1 negative controls were available.")
    else:
        lines.extend(["| Stage-1 rank | N | start | q1 | q2 | final label | reason | raw peaks | F2 peaks | F2 late | oscillation |", "|---:|---:|---|---:|---:|---|---|---|---|---:|---:|"])
        for _, row in controls.sort_values("stage1_rank").iterrows():
            lines.append(
                f"| {row['stage1_rank']} | {int(row['N'])} | ({int(row['start_a'])},{int(row['start_b'])}) | "
                f"{float(row['q1']):.3g} | {float(row['q2']):.3g} | {row['final_label']} | "
                f"{row['artifact_reason']} | {row['raw_peaks']} | {row['f2_peaks_n']} | "
                f"{row['f2_late_t']} | {float(row['oscillation_index']):.3g} |"
            )
        lines.append("")
        lines.append(
            "These controls still show multiple raw peaks, but the F2 peak list has",
        )
        lines.append(
            "only one peak. The reported F2-late column is a baseline-shoulder",
        )
        lines.append(
            "diagnostic, not an accepted F2 late peak; the Stage-1 interpretation is",
        )
        lines.append(
            "rejected when the late feature is only an even/odd comb or",
        )
        lines.append("a very short-distance ballistic repeat.")

    lines.extend(["", "## 2. Robust Double Peaks", ""])
    if robust_double.empty:
        lines.append("No robust double peaks survived the F2/parity filtering in this scan.")
    else:
        lines.append(f"Robust double peaks retained: {len(robust_double)}.")

    lines.extend(["", "## 3. Strongest Robust Shoulders", ""])
    if robust_shoulder.empty:
        lines.append("No robust shoulders survived all filters. The strongest retained rows, if any, are weak/sensitive.")
    else:
        lines.extend(["| rank | N | start | q1 | q2 | score | t_main | t_late | F2 late | reason |", "|---:|---:|---|---:|---:|---:|---:|---:|---:|---|"])
        for _, row in robust_shoulder.head(10).iterrows():
            lines.append(
                f"| {int(row['stage2_rank'])} | {int(row['N'])} | ({int(row['start_a'])},{int(row['start_b'])}) | "
                f"{float(row['q1']):.3g} | {float(row['q2']):.3g} | {float(row['final_score']):.3g} | "
                f"{int(row['t_main'])} | {row['t_late']} | {row['f2_late_t']} | {row['artifact_reason']} |"
            )

    lines.extend(["", "## 4. Encounter-Site Attribution", ""])
    if shape_df.empty:
        lines.append("No non-artifact rows remained for strong encounter-site attribution.")
    else:
        lines.extend(["| rank | attribution | top early k | top late k | JSD bits | Delta top |", "|---:|---|---:|---:|---:|---|"])
        for _, row in shape_df.head(15).iterrows():
            lines.append(
                f"| {int(row['stage2_rank'])} | {row['attribution_label']} | {int(row['top_k_early'])} | "
                f"{int(row['top_k_late'])} | {float(row['jsd_early_late_bits']):.3g} | {row['Delta_top5']} |"
            )

    lines.extend(["", "## 5. Crossing And Bounce Survival", ""])
    if shape_df.empty:
        lines.append("No non-artifact rows remained for survival comparisons.")
    else:
        lines.extend(["| rank | crossing survives | crossing label | bounce survives | bounce label |", "|---:|---|---|---|---|"])
        for _, row in shape_df.head(15).iterrows():
            lines.append(
                f"| {int(row['stage2_rank'])} | {bool(row['crossing_survives'])} | {row['crossing_label']} | "
                f"{bool(row['bounce_survives'])} | {row['bounce_label']} |"
            )

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `artifacts/encounter_search/results/stage2_shape_cases.csv`",
            "- `artifacts/encounter_search/results/stage2_artifacts.csv`",
            "- `artifacts/encounter_search/results/stage2_report.md`",
            f"- `{figure_root_label}/top_nonartifact/`",
            f"- `{figure_root_label}/negative_controls/`",
            "",
            "## Notes",
            "",
            "- `target_mixture` requires `JSD>=0.05` bits and a changed top encounter site.",
            "- `same_target_multi_path` requires the dominant `f_k(t)` channel itself to pass the robust F2 feature test.",
            "- Rows with features that vanish under both crossing absorption and bounce reflection are demoted to `weak` with `artifact_reason=crossing_sensitive`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _assign_rank(df: pd.DataFrame, column: str) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    out.insert(0, column, np.arange(1, len(out) + 1, dtype=int))
    return out


def _window(center: int, size: int, radius: int) -> tuple[int, int]:
    if size <= 0:
        return 0, -1
    c = min(max(int(center), 0), size - 1)
    return max(0, c - int(radius)), min(size - 1, c + int(radius))


def crop_index_for_mass(f: np.ndarray, *, mass_fraction: float, pad: int) -> int:
    arr = np.asarray(f, dtype=float).reshape(-1)
    if arr.size == 0:
        return 0
    cdf = np.cumsum(arr)
    target = float(mass_fraction) * max(float(cdf[-1]), 1e-300)
    idx = int(np.searchsorted(cdf, target))
    return min(arr.size, max(5, idx + int(pad)))


def _normalise_or_zero(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    total = float(np.sum(arr))
    if total <= 0.0:
        return np.zeros_like(arr)
    return arr / total


def _top_entries(values: np.ndarray, *, n: int, by_abs: bool = False) -> str:
    arr = np.asarray(values, dtype=float).reshape(-1)
    if arr.size == 0:
        return ""
    key = np.abs(arr) if by_abs else arr
    order = np.argsort(key)[::-1]
    parts = []
    for idx in order[: int(n)]:
        parts.append(f"k={idx + 1}:{arr[idx]:.6g}")
    return ";".join(parts)


def _parse_top_distribution(text: object, N: int) -> np.ndarray:
    out = np.zeros(int(N), dtype=float)
    if not isinstance(text, str):
        return out
    for part in text.split(";"):
        if not part or ":" not in part or not part.startswith("k="):
            continue
        k_text, value_text = part.split(":", 1)
        k = int(k_text.replace("k=", "")) - 1
        if 0 <= k < N:
            out[k] = float(value_text)
    return out


def _join_ints(values: Iterable[int]) -> str:
    return ";".join(str(int(v)) for v in values)


def _empty_none(value: object) -> object:
    return "" if value is None else value


def case_slug(row: pd.Series) -> str:
    prefix = "control" if bool(row.get("is_control", False)) else "case"
    rank = row.get("stage2_rank", row.get("artifact_rank", row.get("stage1_rank", "")))
    return (
        f"{prefix}{rank}_N{int(row['N'])}_a{int(row['start_a'])}_b{int(row['start_b'])}_"
        f"q1{_q_label(float(row['q1']))}_q2{_q_label(float(row['q2']))}"
    )


def _q_label(value: float) -> str:
    return f"{float(value):.3g}".replace(".", "p")


if __name__ == "__main__":
    main()
