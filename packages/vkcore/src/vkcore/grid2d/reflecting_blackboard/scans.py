from __future__ import annotations

import argparse
from typing import List, Tuple

import numpy as np

from vkcore.grid2d.bimod_legacy_imports import choose_aw_params, compute_bimodality_metrics, smooth_ma
from vkcore.grid2d.model_core_reflecting import LatticeConfig, build_mc_arrays


def windowed_peak_indices(
    t: np.ndarray,
    f_s: np.ndarray,
    *,
    early_window: Tuple[int, int],
    late_window: Tuple[int, int],
) -> Tuple[int, int]:
    early_mask = (t >= early_window[0]) & (t <= early_window[1])
    late_mask = (t >= late_window[0]) & (t <= late_window[1])
    if not np.any(early_mask):
        early_mask = t <= max(1, int(0.2 * t.max()))
    if not np.any(late_mask):
        late_mask = t >= max(int(0.6 * t.max()), 1)
    p1 = int(np.argmax(f_s[early_mask]))
    p2 = int(np.argmax(f_s[late_mask]))
    p1 = int(np.flatnonzero(early_mask)[p1])
    p2 = int(np.flatnonzero(late_mask)[p2])
    if p2 < p1:
        p1, p2 = p2, p1
    return p1, p2


def metrics_from_peak_indices(
    f: np.ndarray,
    p1: int,
    p2: int,
    *,
    smooth_w: int,
    min_gap: int,
) -> dict:
    f_s = smooth_ma(f, int(smooth_w))
    if p2 <= p1:
        p2 = min(len(f_s) - 1, p1 + min_gap)
    v = int(p1 + np.argmin(f_s[p1 : p2 + 1]))
    h1, h2, hv = float(f_s[p1]), float(f_s[p2]), float(f_s[v])
    t_p1, t_p2, t_v = int(p1 + 1), int(p2 + 1), int(v + 1)
    peak_ratio = min(h1, h2) / max(h1, h2) if max(h1, h2) > 0 else 0.0
    valley_ratio = hv / min(h1, h2) if min(h1, h2) > 0 else 1.0
    return {
        "t_p1": t_p1,
        "t_p2": t_p2,
        "t_v": t_v,
        "h1": h1,
        "h2": h2,
        "hv": hv,
        "h2_over_h1": h2 / h1 if h1 > 0 else np.nan,
        "peak_ratio": peak_ratio,
        "valley_ratio": valley_ratio,
        "valley_depth": 1.0 - valley_ratio,
        "gap": int(t_p2 - t_p1),
        "smooth_window": int(smooth_w),
        "min_sep": 0,
        "min_gap": int(min_gap),
    }


def compute_metrics_with_fallback(
    f_exact: np.ndarray,
    *,
    t_max: int,
    peak_smooth_window: int,
    min_gap: int = 20,
) -> tuple[dict, str]:
    t = np.arange(1, len(f_exact) + 1)
    try:
        metrics = compute_bimodality_metrics(
            f_exact,
            smooth_w=peak_smooth_window,
            min_sep=5,
            min_gap=min_gap,
            min_height=1e-12,
        )
        metrics["bimodal"] = True
        metrics["passes"] = bool(metrics.get("valley_ratio", 1.0) <= 0.07 and metrics.get("gap", 0) >= min_gap)
        return metrics, "peaks"
    except Exception:
        early_end = max(200, int(0.2 * t_max))
        late_start = max(early_end + 1, int(0.5 * t_max))
        early_window = (1, min(t_max, early_end))
        late_window = (late_start, t_max)
        f_s = smooth_ma(f_exact, int(peak_smooth_window))
        p1, p2 = windowed_peak_indices(t, f_s, early_window=early_window, late_window=late_window)
        metrics = metrics_from_peak_indices(
            f_exact,
            p1,
            p2,
            smooth_w=peak_smooth_window,
            min_gap=min_gap,
        )
        metrics["bimodal"] = False
        metrics["method"] = "windowed"
        metrics["early_window"] = early_window
        metrics["late_window"] = late_window
        metrics["passes"] = bool(metrics.get("valley_ratio", 1.0) <= 0.07 and metrics.get("gap", 0) >= min_gap)
        return metrics, "windowed"


def aw_from_exact(f_exact: np.ndarray, *, t_max: int, oversample: int, r_pow10: float) -> tuple[np.ndarray, dict]:
    params = choose_aw_params(t_max, oversample=oversample, r_pow10=r_pow10)
    m = params.m
    r = params.r
    t = np.arange(m, dtype=np.float64)
    x = np.zeros(m, dtype=np.complex128)
    t_vals = np.arange(1, t_max + 1, dtype=np.float64)
    x[1 : t_max + 1] = f_exact[:t_max] * (r ** t_vals)
    fz = np.fft.ifft(x) * m
    c = np.fft.fft(fz) / float(m)
    coeffs = (r ** (-t)) * c
    f_aw = coeffs[1 : t_max + 1].real.astype(np.float64, copy=False)
    return f_aw, {"r": float(r), "m": int(m), "r_pow10": float(r_pow10), "oversample": int(oversample)}


def aw_errors(f_aw: np.ndarray, f_exact: np.ndarray) -> dict:
    diff = np.abs(f_aw - f_exact)
    l1 = float(np.sum(diff))
    linf = float(np.max(diff)) if diff.size else 0.0
    base = float(np.sum(np.abs(f_exact))) if f_exact.size else 1.0
    rel = float(l1 / base) if base > 0 else 0.0
    return {"l1": l1, "linf": linf, "rel_l1": rel}


def smooth_pmf(pmf: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return pmf
    return smooth_ma(pmf, int(window))


def bin_pmf(pmf: np.ndarray, bin_width: int) -> tuple[np.ndarray, np.ndarray]:
    if bin_width <= 1:
        t = np.arange(1, len(pmf) + 1, dtype=np.float64)
        return t, pmf
    n_bins = len(pmf) // bin_width
    if n_bins <= 0:
        t = np.arange(1, len(pmf) + 1, dtype=np.float64)
        return t, pmf
    trimmed = pmf[: n_bins * bin_width]
    binned = trimmed.reshape(n_bins, bin_width).mean(axis=1)
    centers = (np.arange(n_bins, dtype=np.float64) * bin_width) + (bin_width + 1) / 2.0
    return centers, binned


def mc_histogram(
    times: np.ndarray,
    *,
    t_max: int,
    bin_width: int,
    smooth_window: int,
    tail_start: int | None = None,
    tail_bin_width: int | None = None,
    tail_smooth_window: int | None = None,
    censor: bool = True,
    n_total: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    if times.size == 0:
        centers = np.arange(1, t_max + 1, max(1, bin_width))
        return centers, np.zeros_like(centers, dtype=np.float64)
    valid = times < t_max if censor else times <= t_max
    times_use = times[valid]
    use_tail = (
        tail_start is not None
        and tail_bin_width is not None
        and tail_bin_width > bin_width
        and 1 < tail_start < t_max
    )
    if use_tail:
        early_end = min(t_max, int(tail_start))
        edges_early = np.arange(1, early_end + bin_width, bin_width)
        if edges_early.size == 0:
            edges_early = np.array([1], dtype=np.int64)
        tail_edge = int(edges_early[-1])
        edges_tail = np.arange(tail_edge, t_max + tail_bin_width + 1, tail_bin_width)
        edges = np.concatenate([edges_early, edges_tail[1:]]) if edges_tail.size > 1 else edges_early
    else:
        edges = np.arange(1, t_max + bin_width + 1, bin_width)
    counts, _ = np.histogram(times_use, bins=edges)
    total = float(n_total) if n_total is not None else float(times.size)
    if total <= 0:
        centers = (edges[:-1] + edges[1:] - 1) / 2.0
        return centers, np.zeros_like(centers, dtype=np.float64)
    widths = np.diff(edges).astype(np.float64)
    pmf = counts / total / widths
    centers = edges[:-1] + (widths - 1.0) / 2.0
    pmf_base = smooth_ma(pmf, smooth_window) if smooth_window > 1 else pmf.copy()
    pmf_out = pmf_base
    if tail_smooth_window is None:
        tail_smooth_window = smooth_window
    if use_tail and tail_smooth_window > smooth_window:
        pmf_tail = smooth_ma(pmf, tail_smooth_window)
        tail_mask = centers >= float(tail_start)
        if np.any(tail_mask):
            pmf_out = pmf_base.copy()
            pmf_out[tail_mask] = pmf_tail[tail_mask]
    return centers, pmf_out


def mc_params_for_case(case, args: argparse.Namespace, *, profile: str) -> tuple[int, int, int, int | None]:
    mc_samples = int(args.mc_samples)
    bin_width = int(args.mc_bin_width)
    smooth_window = int(args.mc_smooth_window)
    smooth_window_slow: int | None = None

    if profile == "reflecting":
        if case.case_id in {"R1", "R6", "R7", "C3"}:
            mc_samples = max(mc_samples, 60000)
            bin_width = max(bin_width, 4)
            smooth_window = max(smooth_window, 9)
            smooth_window_slow = 15
        if case.case_id in {"NB4", "NB5"}:
            mc_samples = max(mc_samples, 60000)
            bin_width = max(bin_width, 4)
            smooth_window = max(smooth_window, 7)
            smooth_window_slow = 19

    return mc_samples, bin_width, smooth_window, smooth_window_slow


def median_time(times: np.ndarray, labels: np.ndarray, label: int) -> int | None:
    subset = times[labels == label]
    if subset.size == 0:
        return None
    return int(np.median(subset))


def to_one_based(path: np.ndarray) -> np.ndarray:
    if path.size == 0:
        return path
    return path.astype(np.int64) + 1


def simulate_path(
    cfg: LatticeConfig,
    *,
    neighbors: np.ndarray,
    cum_probs: np.ndarray,
    slow_mask: np.ndarray,
    max_steps: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, int, int]:
    start_idx = cfg.start[0] * cfg.N + cfg.start[1]
    target_idx = cfg.target[0] * cfg.N + cfg.target[1]
    s = int(start_idx)
    path = [(cfg.start[0], cfg.start[1])]
    hit_slow = False
    for t in range(1, max_steps + 1):
        u = rng.random()
        move_idx = int((u > cum_probs[s]).sum())
        s_next = int(neighbors[s, move_idx])
        hit_slow = hit_slow or bool(slow_mask[s_next])
        s = s_next
        path.append((s // cfg.N, s % cfg.N))
        if s == target_idx:
            return np.asarray(path, dtype=np.int64), t, int(hit_slow)
    return np.asarray(path, dtype=np.int64), max_steps, int(hit_slow)


def pick_representative_path(
    sample_func,
    *,
    label: int,
    target_time: int,
    rng: np.random.Generator,
    max_attempts: int,
) -> tuple[np.ndarray, int] | None:
    if target_time <= 0:
        return None
    tol = max(3, int(0.05 * target_time))
    best = None
    best_diff = None
    for _ in range(max_attempts):
        path, time, lab = sample_func(rng)
        if lab != label:
            continue
        diff = abs(int(time) - target_time)
        if best is None or diff < best_diff:
            best = (path, int(time))
            best_diff = diff
        if diff <= tol:
            break
    return best


def collect_paths(
    sample_func,
    *,
    label: int,
    n_paths: int,
    rng: np.random.Generator,
    max_attempts: int,
) -> List[np.ndarray]:
    paths: List[np.ndarray] = []
    attempts = 0
    while len(paths) < n_paths and attempts < max_attempts:
        path, _, lab = sample_func(rng)
        attempts += 1
        if lab != label:
            continue
        paths.append(to_one_based(path))
    return paths


def mc_times_labels(
    cfg: LatticeConfig,
    *,
    slow_mask: np.ndarray,
    n_walkers: int,
    max_steps: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, dict, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    neighbors, cum_probs = build_mc_arrays(cfg)
    start_idx = cfg.start[0] * cfg.N + cfg.start[1]
    target_idx = cfg.target[0] * cfg.N + cfg.target[1]

    states = np.full(n_walkers, start_idx, dtype=np.int64)
    times = np.zeros(n_walkers, dtype=np.int64)
    hit_slow = np.zeros(n_walkers, dtype=bool)

    alive = states != target_idx
    steps = 0
    while np.any(alive) and steps < max_steps:
        idx_alive = np.nonzero(alive)[0]
        s = states[idx_alive]
        u = rng.random(size=s.size)
        cum = cum_probs[s]
        move_idx = (u[:, None] > cum).sum(axis=1)
        s_next = neighbors[s, move_idx]

        hit_slow[idx_alive] |= slow_mask[s_next]
        states[idx_alive] = s_next
        times[idx_alive] += 1
        alive = states != target_idx
        steps += 1

    truncated = alive
    if np.any(truncated):
        times[truncated] = max_steps

    labels = hit_slow.astype(np.int64)
    stats = {
        "n_walkers": int(n_walkers),
        "fast_fraction": float(1.0 - labels.mean()),
        "slow_fraction": float(labels.mean()),
        "truncated_fraction": float(truncated.mean()) if n_walkers > 0 else 0.0,
    }
    return times, labels, stats, neighbors, cum_probs


__all__ = [
    "aw_errors",
    "aw_from_exact",
    "bin_pmf",
    "collect_paths",
    "compute_metrics_with_fallback",
    "mc_histogram",
    "mc_params_for_case",
    "mc_times_labels",
    "median_time",
    "metrics_from_peak_indices",
    "pick_representative_path",
    "simulate_path",
    "smooth_pmf",
    "to_one_based",
    "windowed_peak_indices",
]
