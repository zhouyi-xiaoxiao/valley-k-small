from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np


ShapeLabel = Literal["unimodal", "shoulder", "local_bump", "double_peak"]

DEFAULT_THRESHOLDS: dict[str, float] = {
    "R_peak": 0.05,
    "R_valley": 0.8,
    "peak_separation": 5.0,
}


@dataclass(frozen=True)
class PeakClassification:
    classification: ShapeLabel
    metrics: dict[str, float | int | None]
    candidate_peaks: tuple[int, ...] = field(default_factory=tuple)
    thresholds: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_THRESHOLDS))

    def __getitem__(self, key: str) -> Any:
        if key == "classification":
            return self.classification
        if key == "metrics":
            return self.metrics
        if key == "candidate_peaks":
            return self.candidate_peaks
        if key == "thresholds":
            return self.thresholds
        raise KeyError(key)


def _as_signal(f: Any) -> np.ndarray:
    x = np.asarray(f, dtype=float).reshape(-1)
    if not np.all(np.isfinite(x)):
        raise ValueError("distribution contains non-finite values")
    if x.size == 0:
        raise ValueError("distribution is empty")
    return x


def find_candidate_peaks(f: Any, min_separation: int = 5) -> tuple[int, ...]:
    """Find local maxima, keeping the tallest peak in each separation window."""

    x = _as_signal(f)
    min_sep = max(1, int(min_separation))
    if x.size < 3:
        return (int(np.argmax(x)),)

    mask = (x[1:-1] >= x[:-2]) & (x[1:-1] > x[2:])
    peaks = list((np.where(mask)[0] + 1).astype(int))
    if not peaks:
        return (int(np.argmax(x)),)

    selected: list[int] = []
    for idx in sorted(peaks, key=lambda i: float(x[i]), reverse=True):
        if all(abs(idx - kept) >= min_sep for kept in selected):
            selected.append(idx)
    return tuple(int(i) for i in sorted(selected))


def _best_peak_pair(x: np.ndarray, peaks: tuple[int, ...], min_sep: int) -> tuple[int | None, int | None]:
    if len(peaks) < 2:
        return (int(peaks[0]) if peaks else int(np.argmax(x)), None)

    best: tuple[float, int, int] | None = None
    for i, left in enumerate(peaks):
        for right in peaks[i + 1 :]:
            sep = int(right) - int(left)
            if sep < min_sep:
                continue
            hi = max(float(x[left]), float(x[right]), 1e-300)
            lo = min(float(x[left]), float(x[right]))
            valley = float(np.min(x[left : right + 1]))
            r_peak = lo / hi
            r_valley = valley / hi
            score = sep * r_peak / max(r_valley, 1e-12)
            key = (score, sep, -r_valley)
            if best is None or key > (best[0], best[1], best[2]):
                best = (score, int(left), int(right))
    if best is None:
        tallest = int(max(peaks, key=lambda i: float(x[i])))
        return tallest, None
    return best[1], best[2]


def classify_distribution_shape(
    f: Any,
    thresholds: dict[str, float] | None = None,
) -> PeakClassification:
    """Classify a first-passage distribution shape using conservative thresholds."""

    x = _as_signal(f)
    cfg = dict(DEFAULT_THRESHOLDS)
    if thresholds:
        cfg.update({str(k): float(v) for k, v in thresholds.items()})

    min_sep = max(1, int(round(cfg["peak_separation"])))
    peaks = find_candidate_peaks(x, min_separation=min_sep)
    t1, t2 = _best_peak_pair(x, peaks, min_sep=min_sep)

    if t2 is None:
        metrics: dict[str, float | int | None] = {
            "t1": int(t1) if t1 is not None else None,
            "t2": None,
            "tv": None,
            "R_peak": 0.0,
            "R_valley": 1.0,
            "peak_separation": 0,
            "score": 0.0,
        }
        return PeakClassification("unimodal", metrics, peaks, cfg)

    lo_t, hi_t = sorted((int(t1), int(t2)))
    peak_hi = max(float(x[lo_t]), float(x[hi_t]), 1e-300)
    peak_lo = min(float(x[lo_t]), float(x[hi_t]))
    tv = int(lo_t + np.argmin(x[lo_t : hi_t + 1]))
    r_peak = peak_lo / peak_hi
    r_valley = float(x[tv]) / peak_hi
    separation = hi_t - lo_t
    score = separation * r_peak / max(r_valley, 1e-12)

    if (
        r_peak >= cfg["R_peak"]
        and r_valley <= cfg["R_valley"]
        and separation >= cfg["peak_separation"]
    ):
        label: ShapeLabel = "double_peak"
    elif r_peak >= 0.5 * cfg["R_peak"] and separation >= cfg["peak_separation"]:
        label = "local_bump"
    else:
        label = "shoulder"

    metrics = {
        "t1": lo_t,
        "t2": hi_t,
        "tv": tv,
        "R_peak": float(r_peak),
        "R_valley": float(r_valley),
        "peak_separation": int(separation),
        "score": float(score),
    }
    return PeakClassification(label, metrics, peaks, cfg)
