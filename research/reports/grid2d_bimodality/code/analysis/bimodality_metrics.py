#!/usr/bin/env python3
"""Unified bimodality metrics (v13)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:  # optional scipy
    from scipy.signal import find_peaks  # type: ignore

    _HAS_SCIPY = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_SCIPY = False


def _smooth_ma(y: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return y
    k = np.ones(window, dtype=np.float64) / float(window)
    return np.convolve(y, k, mode="same")


def _local_maxima(y: np.ndarray) -> np.ndarray:
    return np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1


def _fallback_prominence(y: np.ndarray, idx: int, *, span: int) -> float:
    left = max(0, idx - span)
    right = min(len(y) - 1, idx + span)
    left_min = float(np.min(y[left : idx + 1])) if idx > left else float(y[idx])
    right_min = float(np.min(y[idx : right + 1])) if right > idx else float(y[idx])
    return float(y[idx] - max(left_min, right_min))


def _pick_two_peaks(y: np.ndarray, idx: np.ndarray, *, min_sep: int) -> Optional[Tuple[int, int]]:
    if idx.size < 2:
        return None
    order = idx[np.argsort(y[idx])[::-1]]
    p1 = int(order[0])
    for p2 in order[1:]:
        if abs(int(p2) - p1) >= min_sep:
            return tuple(sorted((p1, int(p2))))
    return None


def compute_bimodality_metrics(
    t_grid: np.ndarray,
    f: np.ndarray,
    *,
    smooth_window: int = 9,
    ignore_ends: int = 20,
    min_sep: int = 40,
    prom_frac: float = 0.005,
    min_height: float = 1e-12,
    use_scipy: bool = True,
    strict: bool = False,
) -> Dict[str, Any]:
    """Compute bimodality metrics from a single f(t) series.

    Returns a dict with peak/valley indices, times mapped via t_grid, and
    diagnostic metadata. When peaks are not found, status="not_bimodal".
    """
    t_grid = np.asarray(t_grid, dtype=np.float64)
    f = np.asarray(f, dtype=np.float64)
    if t_grid.shape[0] != f.shape[0]:
        raise ValueError("t_grid and f must have the same length.")

    n = f.shape[0]
    ignore_ends = int(ignore_ends)
    if n <= 2 * ignore_ends + 2:
        ignore_ends = max(1, n // 10)
    valid = slice(ignore_ends, n - ignore_ends)
    ys = _smooth_ma(f, smooth_window)
    max_y = float(np.max(ys[valid])) if n > 0 else 0.0

    result: Dict[str, Any] = {
        "status": "not_bimodal",
        "method": "scipy_find_peaks" if (_HAS_SCIPY and use_scipy) else "fallback_local_max",
        "smooth_window": int(smooth_window),
        "ignore_ends": int(ignore_ends),
        "min_sep": int(min_sep),
        "prom_frac": float(prom_frac),
        "min_height": float(min_height),
        "sanity": {
            "sum_f": float(np.sum(f)),
            "min_f": float(np.min(f)),
            "max_f": float(np.max(f)),
        },
        "peaks_all": [],
    }

    if not np.isfinite(max_y) or max_y <= 0.0:
        if strict:
            raise RuntimeError("No valid signal for peak detection.")
        return result

    prom_thresh = float(prom_frac * max_y)

    if _HAS_SCIPY and use_scipy:
        peaks, props = find_peaks(
            ys[valid],
            distance=min_sep,
            prominence=prom_thresh,
            height=min_height,
        )
        peaks = peaks + ignore_ends
        prominences = props.get("prominences", np.zeros_like(peaks, dtype=np.float64))
        heights = props.get("peak_heights", ys[peaks])
        for p, h, pr in zip(peaks, heights, prominences):
            result["peaks_all"].append(
                {
                    "idx": int(p),
                    "t": float(t_grid[int(p)]),
                    "height": float(h),
                    "prominence": float(pr),
                }
            )
    else:
        peaks = _local_maxima(ys)
        peaks = peaks[(peaks >= ignore_ends) & (peaks <= n - 1 - ignore_ends)]
        span = max(min_sep, 5)
        filtered = []
        for p in peaks:
            if ys[p] < min_height:
                continue
            prom = _fallback_prominence(ys, int(p), span=span)
            if prom < prom_thresh:
                continue
            filtered.append(int(p))
            result["peaks_all"].append(
                {
                    "idx": int(p),
                    "t": float(t_grid[int(p)]),
                    "height": float(ys[int(p)]),
                    "prominence": float(prom),
                }
            )
        peaks = np.array(filtered, dtype=int)

    pair = _pick_two_peaks(ys, peaks, min_sep=min_sep)
    if pair is None:
        if strict:
            raise RuntimeError("Failed to find two separated peaks.")
        return result

    p1, p2 = pair
    if p2 - p1 < min_sep:
        if strict:
            raise RuntimeError("Peak separation too small.")
        return result

    v = int(p1 + np.argmin(ys[p1 : p2 + 1]))
    h1, h2, hv = float(ys[p1]), float(ys[p2]), float(ys[v])
    if h1 <= 0 or h2 <= 0:
        if strict:
            raise RuntimeError("Non-positive peak height.")
        return result

    ratio_h2_h1 = h2 / h1
    valley_ratio = hv / min(h1, h2)
    result.update(
        {
            "status": "bimodal",
            "idx_p1": int(p1),
            "idx_p2": int(p2),
            "idx_v": int(v),
            "tp1": float(t_grid[int(p1)]),
            "tp2": float(t_grid[int(p2)]),
            "tv": float(t_grid[int(v)]),
            "h1": h1,
            "h2": h2,
            "hv": hv,
            "ratio_h2_h1": ratio_h2_h1,
            "valley_ratio": valley_ratio,
        }
    )
    return result
