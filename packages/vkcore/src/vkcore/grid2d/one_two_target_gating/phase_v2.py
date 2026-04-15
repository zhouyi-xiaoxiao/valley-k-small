from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class GateWord:
    used_excursion: bool
    used_rollback: bool
    side: str
    bin_tag: str
    n_rollbacks: int


def collapse_repeated_events(events: Sequence[str]) -> list[str]:
    out: list[str] = []
    for event in events:
        if not out or out[-1] != event:
            out.append(str(event))
    return out


def reduce_gate_word(events: Sequence[str]) -> GateWord:
    collapsed = collapse_repeated_events(events)
    used_excursion = any(tag in collapsed for tag in ("U1", "D1", "U2", "D2"))

    used_rollback = False
    n_rollbacks = 0
    seen_gq = False
    for tag in collapsed:
        if tag == "Gq":
            seen_gq = True
            continue
        if seen_gq and tag == "A":
            used_rollback = True
            n_rollbacks += 1
            seen_gq = False

    upper = any(tag in collapsed for tag in ("U1", "U2"))
    lower = any(tag in collapsed for tag in ("D1", "D2"))
    if upper and lower:
        side = "UD"
    elif upper:
        side = "U"
    elif lower:
        side = "D"
    else:
        side = "none"

    pre = any(tag in collapsed for tag in ("U1", "D1"))
    post = any(tag in collapsed for tag in ("U2", "D2"))
    if pre and post:
        bin_tag = "both"
    elif pre:
        bin_tag = "preQ"
    elif post:
        bin_tag = "postQ"
    else:
        bin_tag = "none"

    return GateWord(
        used_excursion=used_excursion,
        used_rollback=used_rollback,
        side=side,
        bin_tag=bin_tag,
        n_rollbacks=n_rollbacks,
    )


def top_level_class(word: GateWord) -> str:
    return f"C{int(word.used_excursion)}{int(word.used_rollback)}"


def mode_time(series: Sequence[float]) -> int:
    arr = np.asarray(series, dtype=np.float64)
    if arr.size <= 1:
        return 0
    return int(np.argmax(arr[1:]) + 1)


def half_width(series: Sequence[float], t_mode: int) -> float:
    arr = np.asarray(series, dtype=np.float64)
    if t_mode <= 0 or t_mode >= arr.size:
        return 0.0
    peak = float(arr[t_mode])
    if peak <= 0.0:
        return 0.0
    threshold = 0.5 * peak
    left = int(t_mode)
    right = int(t_mode)
    while left > 1 and float(arr[left - 1]) >= threshold:
        left -= 1
    while right < arr.size - 1 and float(arr[right + 1]) >= threshold:
        right += 1
    return 0.5 * float(right - left)


def gate_sep(f_fast: Sequence[float], f_slow: Sequence[float]) -> float:
    t_fast = mode_time(f_fast)
    t_slow = mode_time(f_slow)
    w_fast = half_width(f_fast, t_fast)
    w_slow = half_width(f_slow, t_slow)
    return abs(float(t_slow) - float(t_fast)) / max(w_fast + w_slow, 1.0e-12)


def classify_phase_one_target_v2(
    t_peak1: int | None,
    t_peak2: int | None,
    f_fast: Sequence[float],
    f_slow: Sequence[float],
) -> int:
    has_double = int(t_peak1 is not None and t_peak2 is not None)
    separation = gate_sep(f_fast, f_slow)
    return 2 if (has_double and separation >= 1.0) else (1 if has_double else 0)


__all__ = [
    "GateWord",
    "classify_phase_one_target_v2",
    "collapse_repeated_events",
    "gate_sep",
    "half_width",
    "mode_time",
    "reduce_gate_word",
    "top_level_class",
]
