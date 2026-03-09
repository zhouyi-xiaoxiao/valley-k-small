from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BimodalityResult:
    is_bimodal: bool
    peak_indices: tuple[int, ...]
    valley_index: int | None
    peak_ratio: float


def detect_peaks(signal: np.ndarray, h_min: float = 1e-12) -> np.ndarray:
    x = np.asarray(signal, dtype=float)
    if x.size < 3:
        return np.array([], dtype=int)
    left = x[1:-1] > x[:-2]
    right = x[1:-1] > x[2:]
    mask = left & right & (x[1:-1] >= h_min)
    return np.where(mask)[0] + 1


def paper_style_bimodality(signal: np.ndarray, h_min: float = 1e-12, min_ratio: float = 0.01) -> BimodalityResult:
    x = np.asarray(signal, dtype=float)
    peaks = detect_peaks(x, h_min=h_min)
    if peaks.size < 2:
        return BimodalityResult(False, tuple(int(p) for p in peaks), None, 0.0)

    pvals = x[peaks]
    order = np.argsort(pvals)[::-1]
    p1, p2 = peaks[order[0]], peaks[order[1]]
    ratio = float(x[p2] / max(x[p1], 1e-300))
    lo, hi = sorted((int(p1), int(p2)))
    valley = int(lo + np.argmin(x[lo : hi + 1]))
    return BimodalityResult(ratio >= min_ratio, tuple(int(p) for p in peaks), valley, ratio)
