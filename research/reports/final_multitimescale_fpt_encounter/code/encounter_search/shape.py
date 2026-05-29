from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import find_peaks, savgol_filter


@dataclass(frozen=True)
class SignalShape:
    label: str
    score: float
    t_main_index: int
    t_late_index: int | None
    valley_index: int | None
    r_peak: float
    r_valley: float
    separation: int
    candidate_peaks: tuple[int, ...]


@dataclass(frozen=True)
class ShapeScore:
    label: str
    score: float
    raw: SignalShape
    smooth: tuple[SignalShape, ...]
    persistence: int
    parity_penalty: float
    smoothing_penalty: float


def smooth_signal(f: np.ndarray, window: int) -> np.ndarray | None:
    y = np.asarray(f, dtype=float).reshape(-1)
    if y.size < max(5, int(window)):
        return None
    win = int(window)
    if win % 2 == 0:
        win += 1
    if win > y.size:
        win = y.size if y.size % 2 == 1 else y.size - 1
    if win < 5:
        return None
    smoothed = savgol_filter(y, window_length=win, polyorder=min(3, win - 2), mode="interp")
    return np.maximum(smoothed, 0.0)


def classify_signal(f: np.ndarray, *, min_separation: int = 5) -> SignalShape:
    y = np.asarray(f, dtype=float).reshape(-1)
    if y.size == 0 or not np.any(y > 0.0):
        return SignalShape("artifact", 0.0, 0, None, None, 0.0, 1.0, 0, ())

    main = int(np.argmax(y))
    main_height = max(float(y[main]), 1e-300)
    min_sep = max(1, int(min_separation))

    prominence = max(main_height * 1e-4, 1e-300)
    peak_indices, _ = find_peaks(y, distance=min_sep, prominence=prominence)
    peaks = tuple(int(i) for i in peak_indices if float(y[i]) >= main_height * 1e-4)

    late_candidates = [i for i in peaks if i >= main + min_sep]
    if late_candidates:
        best: tuple[float, int, int, int, float, float] | None = None
        for late in late_candidates:
            lo, hi = sorted((main, int(late)))
            valley = int(lo + np.argmin(y[lo : hi + 1]))
            r_peak = float(y[late]) / main_height
            r_valley = float(y[valley]) / main_height
            sep = int(late - main)
            score = sep * r_peak * max(0.05, 1.0 - r_valley)
            key = (score, sep, r_peak, -r_valley)
            if best is None or key > (best[0], best[1], best[4], -best[5]):
                best = (score, sep, int(late), int(valley), r_peak, r_valley)
        assert best is not None
        score, sep, late, valley, r_peak, r_valley = best
        if r_peak >= 0.05 and r_valley <= 0.8 and sep >= min_sep:
            label = "double_peak"
        elif r_peak >= 0.025 and sep >= min_sep:
            label = "local_bump"
        else:
            label = "shoulder"
        return SignalShape(label, float(score), main, late, valley, r_peak, r_valley, sep, peaks)

    # Shoulder fallback: look for a late flattening in the smoothed derivative.
    if y.size >= main + min_sep + 5:
        dy = np.diff(y)
        tail_start = main + min_sep
        derivative_peaks, _ = find_peaks(dy[tail_start:], distance=min_sep)
        derivative_peaks = [int(p + tail_start + 1) for p in derivative_peaks]
        derivative_peaks = [p for p in derivative_peaks if p < y.size and y[p] >= main_height * 0.005]
        if derivative_peaks:
            late = max(derivative_peaks, key=lambda i: float(y[i]) * np.sqrt(max(i - main, 1)))
            lo, hi = sorted((main, late))
            valley = int(lo + np.argmin(y[lo : hi + 1]))
            r_peak = float(y[late]) / main_height
            r_valley = float(y[valley]) / main_height
            sep = int(late - main)
            score = 0.35 * sep * r_peak * max(0.02, 1.0 - r_valley)
            return SignalShape("shoulder", float(score), main, late, valley, r_peak, r_valley, sep, peaks)

    return SignalShape("unimodal", 0.0, main, None, None, 0.0, 1.0, 0, peaks)


def score_distribution(f: np.ndarray, *, smooth_windows: tuple[int, ...] = (7, 11, 21)) -> ShapeScore:
    y = np.asarray(f, dtype=float).reshape(-1)
    raw = classify_signal(y)
    smooth_shapes: list[SignalShape] = []
    for window in smooth_windows:
        smoothed = smooth_signal(y, window)
        if smoothed is None:
            continue
        smooth_shapes.append(classify_signal(smoothed))

    persistence = 0
    for shape in smooth_shapes:
        if raw.t_late_index is None or shape.t_late_index is None:
            continue
        tolerance = max(5, int(0.20 * max(raw.separation, 1)))
        if abs(shape.t_late_index - raw.t_late_index) <= tolerance and shape.label != "unimodal":
            persistence += 1

    parity_penalty = _parity_penalty(y)
    if not smooth_shapes:
        smoothing_penalty = 0.5
    elif raw.label in {"double_peak", "local_bump", "shoulder"} and persistence == 0:
        smoothing_penalty = 0.2
    else:
        smoothing_penalty = 1.0

    score = raw.score * smoothing_penalty * (1.0 - 0.75 * parity_penalty)
    if raw.label == "double_peak" and persistence == len(smooth_shapes) and parity_penalty < 0.2:
        label = "double_peak"
    elif raw.label in {"double_peak", "local_bump"} and persistence >= 1:
        label = "local_bump"
    elif raw.label in {"double_peak", "local_bump", "shoulder"} and persistence >= 1:
        label = "shoulder"
    elif raw.score > 0.0:
        label = "artifact"
    else:
        label = "unimodal"

    return ShapeScore(
        label=label,
        score=max(float(score), 0.0),
        raw=raw,
        smooth=tuple(smooth_shapes),
        persistence=int(persistence),
        parity_penalty=float(parity_penalty),
        smoothing_penalty=float(smoothing_penalty),
    )


def _parity_penalty(y: np.ndarray) -> float:
    mass = float(np.sum(y))
    if mass <= 0.0:
        return 0.0
    even = float(np.sum(y[::2]))
    odd = float(np.sum(y[1::2]))
    mass_contrast = abs(even - odd) / mass
    if y.size < 5:
        return min(1.0, mass_contrast)
    two_step = y[2:] - y[:-2]
    one_step = y[1:] - y[:-1]
    denom = float(np.sum(np.abs(one_step))) + 1e-300
    alternation = max(0.0, 1.0 - float(np.sum(np.abs(two_step))) / denom)
    return min(1.0, 0.65 * mass_contrast + 0.35 * alternation)


def window_bounds(center: int | None, size: int, *, radius: int = 5) -> tuple[int, int]:
    if size <= 0:
        return (0, -1)
    if center is None:
        center = size - 1
    c = min(max(int(center), 0), size - 1)
    return max(0, c - int(radius)), min(size - 1, c + int(radius))


def jensen_shannon_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p_arr = _normalise(p)
    q_arr = _normalise(q)
    m = 0.5 * (p_arr + q_arr)
    return 0.5 * _kl_bits(p_arr, m) + 0.5 * _kl_bits(q_arr, m)


def _normalise(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    total = float(np.sum(arr))
    if total <= 0.0:
        return np.full(arr.shape, 1.0 / max(arr.size, 1), dtype=float)
    return arr / total


def _kl_bits(p: np.ndarray, q: np.ndarray) -> float:
    mask = p > 0.0
    return float(np.sum(p[mask] * np.log2(p[mask] / np.maximum(q[mask], 1e-300))))
