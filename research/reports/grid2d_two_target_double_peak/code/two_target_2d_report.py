#!/usr/bin/env python3
"""Build data/figures/tables for the 2D two-target double-peak report."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

Coord = Tuple[int, int]

DIR_VEC = {
    "E": (1, 0),
    "W": (-1, 0),
    "N": (0, 1),
    "S": (0, -1),
}

# Unified visual style (kept consistent across geometry/heatmap/curve/legend figures).
C_BG = "#f1eedf"
C_FAST = "#cde8f3"
C_SLOW = "#e8e2ad"
C_OVERLAP = "#cdbfe2"
C_ARROW = "#ff5b4f"
C_START = "#e53935"
C_M1 = "#1565c0"
C_M2 = "#0d2a8a"
C_GRID = "#c8c8b4"
C_TEXT_START = "#c62828"
C_TEXT_M1 = "#0d47a1"
C_TEXT_M2 = "#1b2a72"
C_ANY = "#111111"
C_SPLIT1 = "#1f77b4"
C_SPLIT2 = "#ff7f0e"
C_PHASE0 = "#e8e8e8"
C_PHASE1 = "#9ecae1"
C_PHASE2 = "#fb9a99"
C_STICKY = "#9ed9f6"
C_BARRIER_PERM = "#e86f00"
C_SHORTCUT = "#7b1fa2"

MARK_START = "s"
MARK_M1 = "D"
MARK_M2 = "o"

PEAK_SMOOTH_W = 7
PEAK_MIN_REL_HEIGHT = 0.01
PEAK_MIN_REL_RATIO = 0.03
PEAK_MIN_SEP_FRAC = 0.04
PEAK_MAX_VALLEY_REL = 0.98


@dataclass(frozen=True)
class CaseConfig:
    case_id: str
    title: str
    w1: int
    w2: int
    skip2: int
    delta: float = 0.2


@dataclass
class CaseResult:
    config: CaseConfig
    steps: int
    t_peak1: int | None
    t_peak2: int | None
    h_peak1: float | None
    h_peak2: float | None
    t_valley: int | None
    h_valley: float | None
    peak_ratio: float | None
    valley_over_max: float | None
    p_m1: float
    p_m2: float
    t_mode_m1: int
    t_mode_m2: int
    h_mode_m1: float
    h_mode_m2: float
    hw_m1: float
    hw_m2: float
    sep_mode_width: float
    absorbed_mass: float
    survival_tail: float


@dataclass
class ExternalCaseSpec:
    case_id: str
    name: str
    type_name: str
    expected: str
    note: str
    local_bias_map: Dict[Coord, Tuple[str, float]]
    sticky_map: Dict[Coord, float]
    barrier_map: Dict[Tuple[Coord, Coord], float]
    long_range_map: Dict[Coord, List[Tuple[Coord, float]]]
    global_bias: Tuple[float, float]


@dataclass
class ExternalCaseResult:
    spec: ExternalCaseSpec
    result: CaseResult
    local_bias_count: int
    sticky_count: int
    barrier_count: int
    shortcut_count: int
    phase: int


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def to0(c: Coord) -> Coord:
    return (c[0] - 1, c[1] - 1)


def step_dir(a: Coord, b: Coord) -> str:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    if dx == 1 and dy == 0:
        return "E"
    if dx == -1 and dy == 0:
        return "W"
    if dx == 0 and dy == 1:
        return "N"
    if dx == 0 and dy == -1:
        return "S"
    raise ValueError(f"non-axis step: {a} -> {b}")


def segment_points(a: Coord, b: Coord) -> List[Coord]:
    if a[0] != b[0] and a[1] != b[1]:
        raise ValueError("segment must be axis-aligned")
    points: List[Coord] = []
    if a[0] == b[0]:
        y0, y1 = sorted((a[1], b[1]))
        for y in range(y0, y1 + 1):
            points.append((a[0], y))
        if b[1] < a[1]:
            points.reverse()
        return points
    x0, x1 = sorted((a[0], b[0]))
    for x in range(x0, x1 + 1):
        points.append((x, a[1]))
    if b[0] < a[0]:
        points.reverse()
    return points


def polyline_points(nodes: Sequence[Coord]) -> List[Coord]:
    if len(nodes) < 2:
        raise ValueError("polyline needs >=2 nodes")
    out: List[Coord] = []
    for i in range(len(nodes) - 1):
        seg = segment_points(nodes[i], nodes[i + 1])
        if i > 0:
            seg = seg[1:]
        out.extend(seg)
    return out


def corridor_assignments(
    path_points: Sequence[Coord],
    *,
    width: int,
    skip: int,
    N: int,
) -> Tuple[Dict[Coord, str], set[Coord]]:
    arrows: Dict[Coord, str] = {}
    cells: set[Coord] = set()
    if width < 0:
        raise ValueError("width must be >=0")
    if skip < 0:
        raise ValueError("skip must be >=0")

    for i in range(skip, len(path_points) - 1):
        c = path_points[i]
        d = step_dir(path_points[i], path_points[i + 1])
        for dx in range(-width, width + 1):
            for dy in range(-width, width + 1):
                if abs(dx) + abs(dy) > width:
                    continue
                x = c[0] + dx
                y = c[1] + dy
                if 0 <= x < N and 0 <= y < N:
                    arrows[(x, y)] = d
                    cells.add((x, y))
    return arrows, cells


def build_case_layout(
    *,
    N: int,
    fast_path: Sequence[Coord],
    slow_path: Sequence[Coord],
    w1: int,
    w2: int,
    skip2: int,
) -> Tuple[Dict[Coord, str], set[Coord], set[Coord]]:
    fast_arrows, fast_cells = corridor_assignments(fast_path, width=w1, skip=0, N=N)
    slow_arrows, slow_cells = corridor_assignments(slow_path, width=w2, skip=skip2, N=N)

    # Order matters: slow corridor overrides fast corridor where they overlap.
    arrow_map = dict(fast_arrows)
    arrow_map.update(slow_arrows)
    return arrow_map, fast_cells, slow_cells


def build_transition_arrays(
    *,
    N: int,
    q: float,
    delta: float,
    arrow_map: Dict[Coord, str],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    p_step = q / 4.0
    p_stay0 = 1.0 - q

    src: List[int] = []
    dst: List[int] = []
    prob: List[float] = []

    def idx(x: int, y: int) -> int:
        return y * N + x

    for y in range(N):
        for x in range(N):
            moves = {
                "E": p_step,
                "W": p_step,
                "N": p_step,
                "S": p_step,
            }
            p_stay = p_stay0
            arrow = arrow_map.get((x, y))
            if arrow is not None and p_stay > 0.0:
                shift = delta * p_stay
                p_stay -= shift
                moves[arrow] += shift

            out: Dict[int, float] = {}
            stay_extra = p_stay
            for d, p in moves.items():
                dx, dy = DIR_VEC[d]
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= N or ny < 0 or ny >= N:
                    stay_extra += p
                    continue
                j = idx(nx, ny)
                out[j] = out.get(j, 0.0) + p
            j_self = idx(x, y)
            out[j_self] = out.get(j_self, 0.0) + stay_extra

            s = float(sum(out.values()))
            if not np.isclose(s, 1.0, atol=1e-12):
                raise ValueError(f"row sum != 1 at {(x, y)}: {s}")

            i = idx(x, y)
            for j, p in out.items():
                src.append(i)
                dst.append(j)
                prob.append(p)

    return (
        np.asarray(src, dtype=np.int64),
        np.asarray(dst, dtype=np.int64),
        np.asarray(prob, dtype=np.float64),
    )


def _edge_key(a: Coord, b: Coord) -> Tuple[Coord, Coord]:
    return (a, b) if a <= b else (b, a)


def _to0_checked(pos_1b: Sequence[int], N: int) -> Coord:
    if len(pos_1b) != 2:
        raise ValueError(f"invalid coordinate: {pos_1b}")
    x = int(pos_1b[0]) - 1
    y = int(pos_1b[1]) - 1
    if not (0 <= x < N and 0 <= y < N):
        raise ValueError(f"coordinate out of bounds (1-based): {pos_1b}")
    return (x, y)


def _parse_global_bias(
    q: float,
    bx: float,
    by: float,
) -> Dict[str, float]:
    # Interpret bx/by as net directional biases split across opposite directions.
    moves = {
        "E": q / 4.0 + 0.5 * bx,
        "W": q / 4.0 - 0.5 * bx,
        "N": q / 4.0 + 0.5 * by,
        "S": q / 4.0 - 0.5 * by,
    }
    arr = np.asarray([moves["E"], moves["W"], moves["N"], moves["S"]], dtype=np.float64)
    arr = np.maximum(arr, 0.0)
    s = float(arr.sum())
    if s <= 0.0:
        arr[:] = q / 4.0
    else:
        arr *= q / s
    return {
        "E": float(arr[0]),
        "W": float(arr[1]),
        "N": float(arr[2]),
        "S": float(arr[3]),
    }


def build_transition_arrays_general(
    *,
    N: int,
    q: float,
    local_bias_map: Dict[Coord, Tuple[str, float]],
    sticky_map: Dict[Coord, float],
    barrier_map: Dict[Tuple[Coord, Coord], float],
    long_range_map: Dict[Coord, List[Tuple[Coord, float]]],
    global_bias: Tuple[float, float],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    base_moves = _parse_global_bias(q, float(global_bias[0]), float(global_bias[1]))

    src: List[int] = []
    dst: List[int] = []
    prob: List[float] = []

    def idx(x: int, y: int) -> int:
        return y * N + x

    for y in range(N):
        for x in range(N):
            c = (x, y)
            moves = dict(base_moves)
            sticky = float(sticky_map.get(c, 1.0))
            sticky = min(max(sticky, 0.0), 1.0)
            for d in moves:
                moves[d] *= sticky

            p_stay = 1.0 - float(sum(moves.values()))
            if p_stay < 0.0 and p_stay > -1e-12:
                p_stay = 0.0
            if p_stay < -1e-9:
                raise ValueError(f"negative stay probability at {c}: {p_stay}")

            lb = local_bias_map.get(c)
            if lb is not None and p_stay > 0.0:
                d, delta = lb
                if d not in DIR_VEC:
                    raise ValueError(f"unknown local bias direction: {d}")
                delta = float(min(max(delta, 0.0), 1.0))
                shift = delta * p_stay
                p_stay -= shift
                moves[d] += shift

            out: Dict[int, float] = {}
            stay_extra = p_stay
            for d, p in moves.items():
                if p <= 0.0:
                    continue
                dx, dy = DIR_VEC[d]
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= N or ny < 0 or ny >= N:
                    stay_extra += p
                    continue
                pass_prob = float(barrier_map.get(_edge_key(c, (nx, ny)), 1.0))
                pass_prob = min(max(pass_prob, 0.0), 1.0)
                flow = p * pass_prob
                blocked = p - flow
                if blocked > 0.0:
                    stay_extra += blocked
                if flow > 0.0:
                    j = idx(nx, ny)
                    out[j] = out.get(j, 0.0) + flow

            for to_pos, p_jump in long_range_map.get(c, []):
                if p_jump <= 0.0:
                    continue
                take = min(float(p_jump), max(stay_extra, 0.0))
                if take <= 0.0:
                    continue
                stay_extra -= take
                j_to = idx(to_pos[0], to_pos[1])
                out[j_to] = out.get(j_to, 0.0) + take

            j_self = idx(x, y)
            out[j_self] = out.get(j_self, 0.0) + stay_extra

            s = float(sum(out.values()))
            if s <= 0.0:
                raise ValueError(f"row sum <= 0 at {(x, y)}")
            if not np.isclose(s, 1.0, atol=1e-12):
                for j in list(out.keys()):
                    out[j] /= s

            i = idx(x, y)
            for j, p in out.items():
                src.append(i)
                dst.append(j)
                prob.append(float(p))

    return (
        np.asarray(src, dtype=np.int64),
        np.asarray(dst, dtype=np.int64),
        np.asarray(prob, dtype=np.float64),
    )


def _build_local_bias_from_corridor(
    *,
    N: int,
    fast_centerline: Sequence[Coord],
    slow_centerline: Sequence[Coord],
    fast_width: int,
    slow_width: int,
    slow_skip: int,
    default_delta: float,
) -> Dict[Coord, Tuple[str, float]]:
    local_bias_map: Dict[Coord, Tuple[str, float]] = {}
    fast_map, _ = corridor_assignments(fast_centerline, width=fast_width, skip=0, N=N)
    slow_map, _ = corridor_assignments(slow_centerline, width=slow_width, skip=slow_skip, N=N)
    for c, d in fast_map.items():
        local_bias_map[c] = (d, default_delta)
    for c, d in slow_map.items():
        local_bias_map[c] = (d, default_delta)
    return local_bias_map


def _region_cells_rectangle(x_range: Sequence[int], y_range: Sequence[int], N: int) -> List[Coord]:
    if len(x_range) != 2 or len(y_range) != 2:
        raise ValueError("x_range/y_range must have length 2")
    x0, x1 = sorted((int(x_range[0]), int(x_range[1])))
    y0, y1 = sorted((int(y_range[0]), int(y_range[1])))
    out: List[Coord] = []
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            c = _to0_checked((x, y), N)
            out.append(c)
    return out


def load_external_sparse_specs(
    *,
    path: Path,
    N: int,
    default_delta: float,
) -> List[ExternalCaseSpec]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    cases = obj.get("cases", [])
    common = obj.get("common_geometry", {})

    fast_centerline_1b = common.get("fast_centerline", [])
    slow_centerline_1b = common.get("slow_centerline", [])
    fast_centerline = [_to0_checked(c, N) for c in fast_centerline_1b]
    slow_centerline = [_to0_checked(c, N) for c in slow_centerline_1b]

    specs: List[ExternalCaseSpec] = []
    for i, c in enumerate(cases, start=1):
        name = str(c.get("name", f"case_{i}"))
        type_name = str(c.get("type", "unknown"))
        exp = c.get("expected", {})
        expected = str(exp.get("peaks", exp.get("phase_map_class", "unknown")))
        note = str(exp.get("notes", ""))
        het = c.get("heterogeneities", {})

        local_bias_map: Dict[Coord, Tuple[str, float]] = {}
        sticky_map: Dict[Coord, float] = {}
        barrier_map: Dict[Tuple[Coord, Coord], float] = {}
        long_range_map: Dict[Coord, List[Tuple[Coord, float]]] = {}
        global_bias = (0.0, 0.0)

        corridor_bias = het.get("corridor_bias")
        if corridor_bias:
            fw = int(corridor_bias.get("fast", {}).get("width", 1))
            sw = int(corridor_bias.get("slow", {}).get("width", 1))
            sk = int(corridor_bias.get("slow", {}).get("skip", 0))
            local_bias_map.update(
                _build_local_bias_from_corridor(
                    N=N,
                    fast_centerline=fast_centerline,
                    slow_centerline=slow_centerline,
                    fast_width=fw,
                    slow_width=sw,
                    slow_skip=sk,
                    default_delta=default_delta,
                )
            )

        for item in het.get("local_bias_sites", []):
            pos = _to0_checked(item["pos"], N)
            d = str(item["dir"]).upper()
            delta = float(item.get("delta", default_delta))
            local_bias_map[pos] = (d, delta)

        for reg in het.get("sticky_regions", []):
            shape = str(reg.get("shape", "rectangle"))
            if shape != "rectangle":
                continue
            sf = float(reg.get("slow_factor", 1.0))
            for pos in _region_cells_rectangle(reg["x_range"], reg["y_range"], N):
                old = sticky_map.get(pos, 1.0)
                sticky_map[pos] = min(old, sf)

        for item in het.get("sticky_sites", []):
            pos = _to0_checked(item["pos"], N)
            sf = float(item.get("slow_factor", 1.0))
            old = sticky_map.get(pos, 1.0)
            sticky_map[pos] = min(old, sf)

        for b in het.get("barriers", []):
            a = _to0_checked(b["between"][0], N)
            d = _to0_checked(b["between"][1], N)
            if abs(a[0] - d[0]) + abs(a[1] - d[1]) != 1:
                continue
            t = str(b.get("type", "reflecting")).lower()
            pass_prob = 0.0 if t == "reflecting" else float(b.get("pass_prob", 1.0))
            barrier_map[_edge_key(a, d)] = min(max(pass_prob, 0.0), 1.0)

        for lr in het.get("long_range_connections", []):
            frm = _to0_checked(lr["from"], N)
            to = _to0_checked(lr["to"], N)
            p = float(lr.get("prob", 0.0))
            long_range_map.setdefault(frm, []).append((to, max(p, 0.0)))

        gb = het.get("global_bias")
        if gb:
            global_bias = (float(gb.get("bx", 0.0)), float(gb.get("by", 0.0)))

        specs.append(
            ExternalCaseSpec(
                case_id=f"S{i:02d}",
                name=name,
                type_name=type_name,
                expected=expected,
                note=note,
                local_bias_map=local_bias_map,
                sticky_map=sticky_map,
                barrier_map=barrier_map,
                long_range_map=long_range_map,
                global_bias=global_bias,
            )
        )
    return specs


def run_exact_two_target(
    *,
    N: int,
    start: Coord,
    target1: Coord,
    target2: Coord,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    t_max: int,
    surv_tol: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n_states = N * N

    def idx(xy: Coord) -> int:
        return xy[1] * N + xy[0]

    i_start = idx(start)
    i_m1 = idx(target1)
    i_m2 = idx(target2)

    p = np.zeros(n_states, dtype=np.float64)
    p[i_start] = 1.0

    f_any = [0.0]
    f_m1 = [0.0]
    f_m2 = [0.0]
    surv = [1.0]

    for _ in range(1, t_max + 1):
        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_idx, p[src_idx] * probs)

        hit1 = float(p_next[i_m1])
        hit2 = float(p_next[i_m2])
        hit = hit1 + hit2

        p_next[i_m1] = 0.0
        p_next[i_m2] = 0.0

        s = float(p_next.sum())

        f_any.append(hit)
        f_m1.append(hit1)
        f_m2.append(hit2)
        surv.append(s)

        p = p_next
        if s < surv_tol:
            break

    return (
        np.asarray(f_any, dtype=np.float64),
        np.asarray(f_m1, dtype=np.float64),
        np.asarray(f_m2, dtype=np.float64),
        np.asarray(surv, dtype=np.float64),
    )


def conditional_snapshots_two_target(
    *,
    N: int,
    start: Coord,
    target1: Coord,
    target2: Coord,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    times: Sequence[int],
) -> Dict[int, np.ndarray]:
    req_times = sorted({int(t) for t in times if int(t) >= 1})
    if not req_times:
        return {}

    t_max = req_times[-1]
    times_set = set(req_times)
    n_states = N * N

    def idx(xy: Coord) -> int:
        return xy[1] * N + xy[0]

    i_start = idx(start)
    i_m1 = idx(target1)
    i_m2 = idx(target2)

    p = np.zeros(n_states, dtype=np.float64)
    p[i_start] = 1.0
    out: Dict[int, np.ndarray] = {}

    for t in range(1, t_max + 1):
        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_idx, p[src_idx] * probs)
        p_next[i_m1] = 0.0
        p_next[i_m2] = 0.0

        if t in times_set:
            s = float(p_next.sum())
            snap = p_next.reshape(N, N).copy()
            if s > 0.0:
                snap /= s
            out[t] = snap
        p = p_next
    return out


def _moving_average(y: np.ndarray, w: int) -> np.ndarray:
    n = int(y.size)
    if n == 0:
        return y.copy()
    ww = max(1, int(w))
    if ww % 2 == 0:
        ww += 1
    if ww == 1:
        return y.astype(np.float64, copy=True)
    pad = ww // 2
    k = np.ones(ww, dtype=np.float64) / float(ww)
    y_pad = np.pad(y.astype(np.float64, copy=False), (pad, pad), mode="edge")
    out = np.convolve(y_pad, k, mode="valid")
    return out[:n]


def _strict_local_maxima(y: np.ndarray) -> np.ndarray:
    if y.size < 3:
        return np.zeros(0, dtype=np.int64)
    idx = np.where((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:]))[0] + 1
    return idx.astype(np.int64, copy=False)


def _refine_raw_peak(y: np.ndarray, center: int, win: int) -> int:
    n = int(y.size)
    if n == 0:
        return 0
    w = max(1, int(win))
    lo = max(1, int(center) - w)
    hi = min(n - 2, int(center) + w)
    if hi <= lo:
        return int(np.clip(center, 1, n - 2))
    seg = y[lo : hi + 1]
    return int(lo + np.argmax(seg))


def find_two_peaks(f: np.ndarray) -> Tuple[int | None, int | None]:
    if f.size < 5:
        return None, None
    f = np.asarray(f, dtype=np.float64)
    f_max = float(np.max(f))
    if not np.isfinite(f_max) or f_max <= 0.0:
        return None, None

    fs = _moving_average(f, PEAK_SMOOTH_W)
    peaks = _strict_local_maxima(fs)
    if peaks.size < 2:
        return None, None

    min_h = PEAK_MIN_REL_HEIGHT * f_max
    peaks = peaks[fs[peaks] >= min_h]
    if peaks.size < 2:
        return None, None

    n = int(f.size)
    min_sep = max(5, int(round(PEAK_MIN_SEP_FRAC * n)))
    best_pair: Tuple[int, int] | None = None
    best_score = -1.0

    for i in range(peaks.size - 1):
        p1 = int(peaks[i])
        for j in range(i + 1, peaks.size):
            p2 = int(peaks[j])
            if p2 - p1 < min_sep:
                continue
            h1 = float(fs[p1])
            h2 = float(fs[p2])
            if h1 <= 0.0 or h2 <= 0.0:
                continue
            if min(h1, h2) / max(h1, h2) < PEAK_MIN_REL_RATIO:
                continue
            valley = float(np.min(fs[p1 : p2 + 1]))
            valley_rel = valley / max(h1, h2)
            if valley_rel > PEAK_MAX_VALLEY_REL:
                continue
            sep_bonus = 0.25 * float(p2 - p1) / float(max(1, n))
            score = min(h1, h2) * (1.0 + sep_bonus)
            if score > best_score:
                best_score = score
                best_pair = (p1, p2)

    if best_pair is None:
        return None, None

    p1s, p2s = best_pair
    win = max(2, PEAK_SMOOTH_W)
    p1 = _refine_raw_peak(f, p1s, win)
    p2 = _refine_raw_peak(f, p2s, win)
    if p2 <= p1:
        return None, None
    return p1, p2


def save_series_csv(path: Path, f_any: np.ndarray, f_m1: np.ndarray, f_m2: np.ndarray, surv: np.ndarray) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["t", "f_any", "f_m1_first", "f_m2_first", "survival"])
        for t in range(len(f_any)):
            writer.writerow([t, f_any[t], f_m1[t], f_m2[t], surv[t]])


def render_metrics_table(results: Sequence[CaseResult], out_path: Path) -> None:
    lines = []
    lines.append("\\begin{tabular}{lcccccccc}")
    lines.append("\\toprule")
    lines.append("Case & $w_2$ & skip2 & $t_{p1}$ & $t_{p2}$ & $h_1$ & $h_2$ & $P(m_1)$ & $P(m_2)$ \\\\")
    lines.append("\\midrule")
    for r in results:
        tp1 = "-" if r.t_peak1 is None else f"{r.t_peak1}"
        tp2 = "-" if r.t_peak2 is None else f"{r.t_peak2}"
        h1 = "-" if r.h_peak1 is None else f"{r.h_peak1:.2e}"
        h2 = "-" if r.h_peak2 is None else f"{r.h_peak2:.2e}"
        lines.append(
            f"{r.config.case_id} & {r.config.w2} & {r.config.skip2} & {tp1} & {tp2} & {h1} & {h2} & {r.p_m1:.3f} & {r.p_m2:.3f} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def render_mechanism_table(results: Sequence[CaseResult], out_path: Path) -> None:
    lines = []
    lines.append("\\begin{tabular}{lcccccc}")
    lines.append("\\toprule")
    lines.append("Case & $t^*_{m_1|m_2}$ & $t^*_{m_2|m_1}$ & $t_v$ & valley/max & absorbed@6000 & tail@6000 \\\\")
    lines.append("\\midrule")
    for r in results:
        tv = "-" if r.t_valley is None else f"{r.t_valley}"
        vr = "-" if r.valley_over_max is None else f"{r.valley_over_max:.3f}"
        lines.append(
            f"{r.config.case_id} & {r.t_mode_m1} & {r.t_mode_m2} & {tv} & {vr} & {r.absorbed_mass:.3f} & {r.survival_tail:.3f} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def render_separation_table(results: Sequence[CaseResult], out_path: Path) -> None:
    lines = []
    lines.append("\\begin{tabular}{lccccc}")
    lines.append("\\toprule")
    lines.append("Case & $t^*_{m_1|m_2}$ & $t^*_{m_2|m_1}$ & $w_{1/2}^{(1)}$ & $w_{1/2}^{(2)}$ & $|\\Delta t^*|/(w_{1/2}^{(1)}+w_{1/2}^{(2)})$ \\\\")
    lines.append("\\midrule")
    for r in results:
        lines.append(
            f"{r.config.case_id} & {r.t_mode_m1} & {r.t_mode_m2} & {r.hw_m1:.1f} & {r.hw_m2:.1f} & {r.sep_mode_width:.3f} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _draw_path_arrows(ax: plt.Axes, path: Sequence[Coord], *, start_idx: int, color: str) -> None:
    i0 = max(0, int(start_idx))
    for i in range(i0, len(path) - 1):
        a = path[i]
        b = path[i + 1]
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=1.6, alpha=0.90, zorder=6)

    step = 3
    for i in range(i0, len(path) - 1, step):
        a = path[i]
        b = path[min(i + 1, len(path) - 1)]
        ax.annotate(
            "",
            xy=(b[0], b[1]),
            xytext=(a[0], a[1]),
            arrowprops=dict(arrowstyle="->", lw=1.3, color=color, shrinkA=6, shrinkB=6),
            zorder=8,
        )


def _path_turn_points(path: Sequence[Coord]) -> List[Coord]:
    if len(path) < 3:
        return []
    turns: List[Coord] = []
    prev = (path[1][0] - path[0][0], path[1][1] - path[0][1])
    for i in range(1, len(path) - 1):
        cur = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        if cur != prev:
            turns.append(path[i])
        prev = cur
    return turns


def _draw_environment_panel(
    ax: plt.Axes,
    *,
    N: int,
    fast_cells: set[Coord],
    slow_cells: set[Coord],
    start: Coord,
    m1: Coord,
    m2: Coord,
    fast_path: Sequence[Coord],
    slow_path: Sequence[Coord],
    slow_skip: int,
    title: str,
    draw_sampled_arrows: bool = True,
    draw_turn_points: bool = True,
    annotate_nodes: bool = True,
) -> None:
    base = np.zeros((N, N), dtype=np.float64)
    ax.imshow(base, origin="lower", cmap=plt.matplotlib.colors.ListedColormap([C_BG]), vmin=0.0, vmax=1.0, interpolation="nearest")

    for x, y in sorted(fast_cells):
        ax.add_patch(
            Rectangle(
                (x - 0.5, y - 0.5),
                1.0,
                1.0,
                facecolor=C_FAST,
                edgecolor="none",
                alpha=0.88,
                zorder=2,
            )
        )

    for x, y in sorted(slow_cells):
        in_fast = (x, y) in fast_cells
        face = C_OVERLAP if in_fast else C_SLOW
        ax.add_patch(
            Rectangle(
                (x - 0.5, y - 0.5),
                1.0,
                1.0,
                facecolor=face,
                edgecolor="none",
                alpha=0.82,
                zorder=3,
            )
        )

    if draw_sampled_arrows:
        _draw_path_arrows(ax, fast_path, start_idx=0, color=C_ARROW)
        _draw_path_arrows(ax, slow_path, start_idx=slow_skip, color=C_ARROW)

    if draw_turn_points:
        # Mark slow-path turning points explicitly so bends are visible at a glance.
        turn_pts = _path_turn_points(slow_path)
        if turn_pts:
            tx = [p[0] for p in turn_pts]
            ty = [p[1] for p in turn_pts]
            ax.scatter(tx, ty, c="#111111", s=28, marker="o", edgecolors="white", linewidths=0.5, zorder=9, label="turn")

    ax.scatter([start[0]], [start[1]], c=C_START, s=58, marker=MARK_START, label="start", zorder=10)
    ax.scatter([m1[0]], [m1[1]], c=C_M1, s=72, marker=MARK_M1, label="m1", zorder=10)
    ax.scatter([m2[0]], [m2[1]], c=C_M2, s=72, marker=MARK_M2, label="m2", zorder=10)

    if annotate_nodes:
        ax.text(start[0] + 0.8, start[1] + 0.8, "start", color=C_TEXT_START, fontsize=8, weight="bold", zorder=11)
        ax.text(m1[0] + 0.8, m1[1] + 0.8, "m1", color=C_TEXT_M1, fontsize=8, weight="bold", zorder=11)
        ax.text(m2[0] + 0.8, m2[1] + 0.8, "m2", color=C_TEXT_M2, fontsize=8, weight="bold", zorder=11)

    ax.set_xlim(-0.5, N - 0.5)
    ax.set_ylim(-0.5, N - 0.5)
    ax.set_aspect("equal")

    ax.set_xticks(np.arange(-0.5, N, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, N, 1), minor=True)
    ax.grid(which="minor", color=C_GRID, linewidth=0.34)
    ax.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)

    for s in ax.spines.values():
        s.set_linewidth(2.2)
        s.set_color("black")
    ax.set_title(title, fontsize=10, pad=6)


def plot_case_arrowfield(
    out_path: Path,
    *,
    N: int,
    start: Coord,
    m1: Coord,
    m2: Coord,
    arrow_map: Dict[Coord, str],
    fast_cells: set[Coord],
    slow_cells: set[Coord],
    fast_path: Sequence[Coord],
    slow_path: Sequence[Coord],
    slow_skip: int,
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(8.8, 8.8))
    _draw_environment_panel(
        ax,
        N=N,
        fast_cells=fast_cells,
        slow_cells=slow_cells,
        start=start,
        m1=m1,
        m2=m2,
        fast_path=fast_path,
        slow_path=slow_path,
        slow_skip=slow_skip,
        title=title,
        draw_sampled_arrows=False,
        draw_turn_points=False,
        annotate_nodes=True,
    )

    if arrow_map:
        xs = np.array([c[0] for c in arrow_map.keys()], dtype=np.float64)
        ys = np.array([c[1] for c in arrow_map.keys()], dtype=np.float64)
        us = np.array([DIR_VEC[d][0] for d in arrow_map.values()], dtype=np.float64) * 0.72
        vs = np.array([DIR_VEC[d][1] for d in arrow_map.values()], dtype=np.float64) * 0.72
        ax.quiver(
            xs,
            ys,
            us,
            vs,
            angles="xy",
            scale_units="xy",
            scale=1.0,
            color=C_ARROW,
            width=0.0036,
            headwidth=3.4,
            headlength=4.6,
            headaxislength=4.0,
            pivot="middle",
            alpha=0.92,
            zorder=7,
        )

    handles, labels = ax.get_legend_handles_labels()
    if handles:
        wanted = ["start", "m1", "m2"]
        hl = {lab: h for h, lab in zip(handles, labels)}
        sel_h = [hl[k] for k in wanted if k in hl]
        sel_l = [k for k in wanted if k in hl]
        if sel_h:
            ax.legend(sel_h, sel_l, loc="upper right", fontsize=9, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _draw_heatmap_panel(
    ax: plt.Axes,
    *,
    arr: np.ndarray,
    t: int,
    m1: Coord,
    m2: Coord,
    vmax: float,
) -> plt.AxesImage:
    norm = plt.matplotlib.colors.PowerNorm(gamma=0.55, vmin=0.0, vmax=vmax)
    im = ax.imshow(arr, origin="lower", cmap="plasma", interpolation="nearest", norm=norm)
    ax.scatter([m1[0]], [m1[1]], c=C_M1, s=52, marker=MARK_M1, edgecolors="white", linewidths=0.45, zorder=5)
    ax.scatter([m2[0]], [m2[1]], c=C_M2, s=52, marker=MARK_M2, edgecolors="white", linewidths=0.45, zorder=5)
    ax.text(
        0.95,
        0.06,
        f"$t={t}$",
        color="white",
        fontsize=14,
        ha="right",
        va="bottom",
        transform=ax.transAxes,
        fontstyle="italic",
    )
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_linewidth(2.0)
        s.set_color("white")
    return im


def _draw_fpt(ax: plt.Axes, f_any: np.ndarray, f_m1: np.ndarray, f_m2: np.ndarray, result: CaseResult) -> None:
    t = np.arange(len(f_any))
    f_any_s = _moving_average(f_any, PEAK_SMOOTH_W)
    f_m1_s = _moving_average(f_m1, PEAK_SMOOTH_W)
    f_m2_s = _moving_average(f_m2, PEAK_SMOOTH_W)

    ax.plot(t, f_any, color=C_ANY, lw=0.8, alpha=0.30)
    ax.plot(t, f_m1, color=C_SPLIT1, lw=0.7, alpha=0.25)
    ax.plot(t, f_m2, color=C_SPLIT2, lw=0.7, alpha=0.25)
    ax.plot(t, f_any_s, color=C_ANY, lw=1.8, label="F_any (smooth)")
    ax.plot(t, f_m1_s, color=C_SPLIT1, lw=1.3, label="F_m1|m2 (smooth)")
    ax.plot(t, f_m2_s, color=C_SPLIT2, lw=1.3, label="F_m2|m1 (smooth)")

    if result.t_peak1 is not None and result.t_peak2 is not None:
        ax.scatter(
            [result.t_peak1, result.t_peak2],
            [f_any_s[result.t_peak1], f_any_s[result.t_peak2]],
            c=C_ANY,
            s=18,
            zorder=3,
        )
    ax.set_xlim(0, len(f_any) - 1)
    ax.set_xlabel("t")
    ax.set_ylabel("probability")
    ax.set_title(
        f"{result.config.case_id}: w2={result.config.w2}, skip2={result.config.skip2}, "
        f"P(m1)={result.p_m1:.3f}, P(m2)={result.p_m2:.3f}",
        fontsize=9,
    )
    ax.grid(alpha=0.25)


def plot_case_geometry(
    out_path: Path,
    *,
    N: int,
    start: Coord,
    m1: Coord,
    m2: Coord,
    fast_cells: set[Coord],
    slow_cells: set[Coord],
    fast_path: Sequence[Coord],
    slow_path: Sequence[Coord],
    slow_skip: int,
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(5.4, 5.1))
    _draw_environment_panel(
        ax,
        N=N,
        fast_cells=fast_cells,
        slow_cells=slow_cells,
        start=start,
        m1=m1,
        m2=m2,
        fast_path=fast_path,
        slow_path=slow_path,
        slow_skip=slow_skip,
        title=title,
    )
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        wanted = ["start", "m1", "m2", "turn"]
        hl = {lab: h for h, lab in zip(handles, labels)}
        sel_h = [hl[k] for k in wanted if k in hl]
        sel_l = [k for k in wanted if k in hl]
        if sel_h:
            ax.legend(sel_h, sel_l, loc="upper right", fontsize=8, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_case_fpt(out_path: Path, f_any: np.ndarray, f_m1: np.ndarray, f_m2: np.ndarray, result: CaseResult) -> None:
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    _draw_fpt(ax, f_any, f_m1, f_m2, result)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_geometry_grid(
    out_path: Path,
    *,
    N: int,
    start: Coord,
    m1: Coord,
    m2: Coord,
    fast_path: Sequence[Coord],
    slow_path: Sequence[Coord],
    cases: Sequence[CaseConfig],
    layouts: Dict[str, Tuple[Dict[Coord, str], set[Coord], set[Coord]]],
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    for ax, case in zip(axes.flatten(), cases):
        _, fast_cells, slow_cells = layouts[case.case_id]
        _draw_environment_panel(
            ax,
            N=N,
            fast_cells=fast_cells,
            slow_cells=slow_cells,
            start=start,
            m1=m1,
            m2=m2,
            fast_path=fast_path,
            slow_path=slow_path,
            slow_skip=case.skip2,
            title=f"{case.case_id}: w2={case.w2}, skip2={case.skip2}",
        )
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_fpt_grid(
    out_path: Path,
    *,
    cases: Sequence[CaseConfig],
    results_map: Dict[str, CaseResult],
    series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(8.8, 6.6))
    for ax, case in zip(axes.flatten(), cases):
        f_any, f_m1, f_m2, _ = series_map[case.case_id]
        _draw_fpt(ax, f_any, f_m1, f_m2, results_map[case.case_id])
        ax.set_xlim(0, 900)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path)
    plt.close(fig)


def _hazard_components(
    f_any: np.ndarray,
    f_m1: np.ndarray,
    f_m2: np.ndarray,
    surv: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if len(f_any) < 2:
        z = np.zeros(0, dtype=np.float64)
        return z, z, z, z
    t = np.arange(1, len(f_any), dtype=np.int64)
    s_prev = np.maximum(surv[:-1], 1e-15)
    h_any = f_any[1:] / s_prev
    h1 = f_m1[1:] / s_prev
    h2 = f_m2[1:] / s_prev
    return t, h_any, h1, h2


def plot_hazard_grid(
    out_path: Path,
    *,
    cases: Sequence[CaseConfig],
    series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    results_map: Dict[str, CaseResult],
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(8.8, 6.6))
    for ax, case in zip(axes.flatten(), cases):
        f_any, f_m1, f_m2, surv = series_map[case.case_id]
        t, h_any, h1, h2 = _hazard_components(f_any, f_m1, f_m2, surv)
        ax.plot(t, h_any, color=C_ANY, lw=1.6, label="h_any")
        ax.plot(t, h1, color=C_SPLIT1, lw=1.2, label="h_m1")
        ax.plot(t, h2, color=C_SPLIT2, lw=1.2, label="h_m2")
        res = results_map[case.case_id]
        if res.t_valley is not None and res.t_valley > 0 and res.t_valley < len(h_any):
            ax.axvline(res.t_valley, color="#444444", lw=1.0, ls="--", alpha=0.65)
        ax.set_xlim(1, min(len(t), 900))
        ax.set_xlabel("t")
        ax.set_ylabel("hazard")
        ax.set_title(f"{case.case_id}: hazard decomposition", fontsize=9)
        ax.grid(alpha=0.25)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path)
    plt.close(fig)


def plot_symbol_legend_panel(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 4.0))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    y0 = 0.84
    dy = 0.105

    def row(y: float, label: str, desc: str) -> None:
        ax.text(0.08, y, label, ha="left", va="center", fontsize=10, color="black")
        ax.text(0.34, y, desc, ha="left", va="center", fontsize=10, color="black")

    # Corridor fills
    ax.add_patch(Rectangle((0.02, y0 - 0.03), 0.045, 0.06, facecolor=C_FAST, edgecolor="black", lw=0.6))
    row(y0, "Fast corridor", "cell region guided to m1")
    y0 -= dy
    ax.add_patch(Rectangle((0.02, y0 - 0.03), 0.045, 0.06, facecolor=C_SLOW, edgecolor="black", lw=0.6))
    row(y0, "Slow corridor", "cell region guided to m2")
    y0 -= dy
    ax.add_patch(Rectangle((0.02, y0 - 0.03), 0.045, 0.06, facecolor=C_OVERLAP, edgecolor="black", lw=0.6))
    row(y0, "Overlap", "fast/slow corridor overlap cells")
    y0 -= dy

    # Markers and arrows
    ax.text(0.044, y0, r"$\rightarrow$", ha="center", va="center", fontsize=18, color=C_ARROW)
    row(y0, "Local bias arrow", "20% of stay probability shifts to arrow direction")
    y0 -= dy
    ax.scatter([0.044], [y0], s=38, marker="o", c="#111111", edgecolors="white", linewidths=0.5)
    row(y0, "Turn point", "centerline turning node (bend location)")
    y0 -= dy
    ax.scatter([0.044], [y0], s=58, marker=MARK_START, c=C_START, edgecolors="black", linewidths=0.45)
    row(y0, "Start", "initial state n0")
    y0 -= dy
    ax.scatter([0.044], [y0], s=74, marker=MARK_M1, c=C_M1, edgecolors="black", linewidths=0.45)
    row(y0, "Target m1", "absorbing target m1")
    y0 -= dy
    ax.scatter([0.044], [y0], s=74, marker=MARK_M2, c=C_M2, edgecolors="black", linewidths=0.45)
    row(y0, "Target m2", "absorbing target m2")

    # Curves
    ax.plot([0.60, 0.68], [0.83, 0.83], color=C_ANY, lw=1.7)
    ax.text(0.70, 0.83, r"$F_{\mathrm{any}}(t)$", va="center", fontsize=10)
    ax.plot([0.60, 0.68], [0.71, 0.71], color=C_SPLIT1, lw=1.4)
    ax.text(0.70, 0.71, r"$F_{m_1|m_2}(t)$", va="center", fontsize=10)
    ax.plot([0.60, 0.68], [0.59, 0.59], color=C_SPLIT2, lw=1.4)
    ax.text(0.70, 0.59, r"$F_{m_2|m_1}(t)$", va="center", fontsize=10)

    # Phase colors
    ax.add_patch(Rectangle((0.60, 0.38), 0.04, 0.07, facecolor=C_PHASE0, edgecolor="black", lw=0.6))
    ax.text(0.66, 0.415, "0: single", va="center", fontsize=9)
    ax.add_patch(Rectangle((0.60, 0.28), 0.04, 0.07, facecolor=C_PHASE1, edgecolor="black", lw=0.6))
    ax.text(0.66, 0.315, "1: weak double", va="center", fontsize=9)
    ax.add_patch(Rectangle((0.60, 0.18), 0.04, 0.07, facecolor=C_PHASE2, edgecolor="black", lw=0.6))
    ax.text(0.66, 0.215, "2: clear double", va="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_case_environment_heatmaps(
    out_path: Path,
    *,
    N: int,
    start: Coord,
    m1: Coord,
    m2: Coord,
    fast_cells: set[Coord],
    slow_cells: set[Coord],
    fast_path: Sequence[Coord],
    slow_path: Sequence[Coord],
    slow_skip: int,
    case_title: str,
    snapshots: Dict[int, np.ndarray],
    heat_times: Sequence[int],
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 10), constrained_layout=True)
    ax_env = axes[0, 0]
    _draw_environment_panel(
        ax_env,
        N=N,
        fast_cells=fast_cells,
        slow_cells=slow_cells,
        start=start,
        m1=m1,
        m2=m2,
        fast_path=fast_path,
        slow_path=slow_path,
        slow_skip=slow_skip,
        title=f"{case_title} environment",
    )

    vmax = 0.0
    for t in heat_times:
        arr = snapshots.get(int(t))
        if arr is not None:
            vmax = max(vmax, float(arr.max()))
    if vmax <= 0:
        vmax = 1e-6

    heat_im = None
    for k, t in enumerate(heat_times):
        ax = axes.flatten()[k + 1]
        arr = snapshots.get(int(t))
        if arr is None:
            arr = np.zeros((N, N), dtype=np.float64)
        heat_im = _draw_heatmap_panel(ax, arr=arr, t=int(t), m1=m1, m2=m2, vmax=vmax)
        if k == 0:
            ax.set_title("Conditional occupancy heatmap", color="white", fontsize=10)

    if heat_im is not None:
        cbar = fig.colorbar(heat_im, ax=[axes[0, 1], axes[1, 0], axes[1, 1]], fraction=0.03, pad=0.02)
        cbar.ax.tick_params(labelsize=8, colors="black")
        cbar.outline.set_edgecolor("black")
        cbar.set_label(r"$P(X_t=n\mid T>t)$", color="black", fontsize=9)

    fig.savefig(out_path)
    plt.close(fig)


def make_cases() -> List[CaseConfig]:
    return [
        CaseConfig("C1", "balanced double peak", w1=1, w2=3, skip2=2),
        CaseConfig("C2", "late peak dominates", w1=1, w2=2, skip2=1),
        CaseConfig("C3", "strong slow capture", w1=1, w2=2, skip2=0),
        CaseConfig("C4", "largest peak separation", w1=1, w2=1, skip2=1),
    ]


def choose_heat_times(result: CaseResult) -> List[int]:
    if result.t_peak1 is not None and result.t_peak2 is not None and result.t_valley is not None:
        t_a = max(5, result.t_peak1 + 15)
        t_b = max(t_a + 1, result.t_valley)
        t_c = max(t_b + 1, result.t_peak2)
        return [int(t_a), int(t_b), int(t_c)]
    return [50, 120, 260]


def half_width_at_half_max(f: np.ndarray, mode: int) -> float:
    if mode <= 0 or mode >= len(f):
        return 0.0
    peak = float(f[mode])
    if peak <= 0.0:
        return 0.0
    thr = 0.5 * peak
    left = mode
    right = mode
    while left > 1 and f[left - 1] >= thr:
        left -= 1
    while right < len(f) - 1 and f[right + 1] >= thr:
        right += 1
    return 0.5 * float(right - left)


def summarize_case(case: CaseConfig, f_any: np.ndarray, f_m1: np.ndarray, f_m2: np.ndarray, surv: np.ndarray) -> CaseResult:
    tp1, tp2 = find_two_peaks(f_any)
    hp1 = None if tp1 is None else float(f_any[tp1])
    hp2 = None if tp2 is None else float(f_any[tp2])

    tv = None
    hv = None
    peak_ratio = None
    valley_over_max = None
    if tp1 is not None and tp2 is not None and tp1 + 1 < tp2:
        window = f_any[tp1 : tp2 + 1]
        k = int(np.argmin(window))
        tv = tp1 + k
        hv = float(f_any[tv])
        if hp1 is not None and hp1 > 0 and hp2 is not None:
            peak_ratio = hp2 / hp1
            valley_over_max = hv / max(hp1, hp2)

    p_m1 = float(np.sum(f_m1))
    p_m2 = float(np.sum(f_m2))
    absorbed_mass = float(np.sum(f_any))
    tail = float(surv[-1])

    t_mode_m1 = int(np.argmax(f_m1[1:]) + 1) if len(f_m1) > 1 else 0
    t_mode_m2 = int(np.argmax(f_m2[1:]) + 1) if len(f_m2) > 1 else 0
    hw_m1 = half_width_at_half_max(f_m1, t_mode_m1)
    hw_m2 = half_width_at_half_max(f_m2, t_mode_m2)
    denom = hw_m1 + hw_m2
    sep_mode_width = float(abs(t_mode_m2 - t_mode_m1) / denom) if denom > 0 else 0.0

    return CaseResult(
        config=case,
        steps=len(f_any) - 1,
        t_peak1=tp1,
        t_peak2=tp2,
        h_peak1=hp1,
        h_peak2=hp2,
        t_valley=tv,
        h_valley=hv,
        peak_ratio=peak_ratio,
        valley_over_max=valley_over_max,
        p_m1=p_m1,
        p_m2=p_m2,
        t_mode_m1=t_mode_m1,
        t_mode_m2=t_mode_m2,
        h_mode_m1=float(f_m1[t_mode_m1]) if t_mode_m1 < len(f_m1) else 0.0,
        h_mode_m2=float(f_m2[t_mode_m2]) if t_mode_m2 < len(f_m2) else 0.0,
        hw_m1=hw_m1,
        hw_m2=hw_m2,
        sep_mode_width=sep_mode_width,
        absorbed_mass=absorbed_mass,
        survival_tail=tail,
    )


def classify_phase(r: CaseResult) -> int:
    has_double = int(r.t_peak1 is not None and r.t_peak2 is not None)
    clear_double = int(has_double and r.sep_mode_width >= 1.0)
    return 2 if clear_double else (1 if has_double else 0)


def _tex_escape(s: str) -> str:
    return (
        s.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("&", "\\&")
        .replace("#", "\\#")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def render_external_sparse_config_table(results: Sequence[ExternalCaseResult], out_path: Path) -> None:
    lines: List[str] = []
    lines.append("\\begin{tabular}{lp{0.35\\linewidth}lcccc}")
    lines.append("\\toprule")
    lines.append("ID & Name & Type & local-bias & sticky & barriers & shortcuts \\\\")
    lines.append("\\midrule")
    for r in results:
        display_name = r.spec.name.replace("_", " ")
        lines.append(
            f"{_tex_escape(r.spec.case_id)} & {_tex_escape(display_name)} & {_tex_escape(r.spec.type_name)} & "
            f"{r.local_bias_count} & {r.sticky_count} & {r.barrier_count} & {r.shortcut_count} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def render_external_sparse_metrics_table(results: Sequence[ExternalCaseResult], out_path: Path) -> None:
    lines: List[str] = []
    lines.append("\\begin{tabular}{lccccccc}")
    lines.append("\\toprule")
    lines.append("ID & $t_{p1}$ & $t_{p2}$ & valley/max & $P(m_1)$ & $P(m_2)$ & sep-score & phase \\\\")
    lines.append("\\midrule")
    for er in results:
        r = er.result
        tp1 = "-" if r.t_peak1 is None else f"{r.t_peak1}"
        tp2 = "-" if r.t_peak2 is None else f"{r.t_peak2}"
        vm = "-" if r.valley_over_max is None else f"{r.valley_over_max:.3f}"
        lines.append(
            f"{_tex_escape(er.spec.case_id)} & {tp1} & {tp2} & {vm} & {r.p_m1:.3f} & {r.p_m2:.3f} & {r.sep_mode_width:.2f} & {er.phase} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def plot_external_sparse_fpt_grid(
    out_path: Path,
    *,
    external_results: Sequence[ExternalCaseResult],
    series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
) -> None:
    n = len(external_results)
    if n == 0:
        return
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12.0, 3.2 * nrows))
    axes_arr = np.atleast_1d(axes).reshape(nrows, ncols)
    for ax in axes_arr.flatten():
        ax.set_visible(False)

    for ax, er in zip(axes_arr.flatten(), external_results):
        ax.set_visible(True)
        f_any, f_m1, f_m2, _ = series_map[er.spec.case_id]
        t = np.arange(len(f_any))
        f_any_s = _moving_average(f_any, PEAK_SMOOTH_W)
        f_m1_s = _moving_average(f_m1, PEAK_SMOOTH_W)
        f_m2_s = _moving_average(f_m2, PEAK_SMOOTH_W)
        ax.plot(t, f_any, color=C_ANY, lw=0.7, alpha=0.30)
        ax.plot(t, f_m1, color=C_SPLIT1, lw=0.6, alpha=0.25)
        ax.plot(t, f_m2, color=C_SPLIT2, lw=0.6, alpha=0.25)
        ax.plot(t, f_any_s, color=C_ANY, lw=1.2)
        ax.plot(t, f_m1_s, color=C_SPLIT1, lw=0.9)
        ax.plot(t, f_m2_s, color=C_SPLIT2, lw=0.9)
        rp = er.result
        peak_marks_x: List[int] = []
        peak_marks_y: List[float] = []
        if rp.t_peak1 is not None and 0 <= rp.t_peak1 < len(f_any):
            peak_marks_x.append(int(rp.t_peak1))
            peak_marks_y.append(float(f_any_s[rp.t_peak1]))
        if rp.t_peak2 is not None and 0 <= rp.t_peak2 < len(f_any):
            peak_marks_x.append(int(rp.t_peak2))
            peak_marks_y.append(float(f_any_s[rp.t_peak2]))
        if peak_marks_x:
            ax.scatter(peak_marks_x, peak_marks_y, c=C_ANY, s=14, zorder=3)
        x_hi = 900
        if rp.t_peak2 is not None:
            x_hi = max(x_hi, int(rp.t_peak2) + 80)
        ax.set_xlim(0, min(x_hi, len(f_any) - 1))
        ax.grid(alpha=0.20)
        ax.set_title(
            f"{er.spec.case_id} ({er.spec.type_name}) phase={er.phase}",
            fontsize=8,
        )
        ax.tick_params(labelsize=7)

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _draw_barrier_segment(ax: plt.Axes, a: Coord, b: Coord, pass_prob: float) -> None:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    if abs(dx) + abs(dy) != 1:
        return
    if dx != 0:
        xb = min(a[0], b[0]) + 0.5
        y = a[1]
        x0, x1 = xb, xb
        y0, y1 = y - 0.48, y + 0.48
    else:
        yb = min(a[1], b[1]) + 0.5
        x = a[0]
        x0, x1 = x - 0.48, x + 0.48
        y0, y1 = yb, yb

    if pass_prob <= 0.0:
        ax.plot([x0, x1], [y0, y1], color="black", lw=2.0, zorder=9)
    else:
        ax.plot([x0, x1], [y0, y1], color=C_BARRIER_PERM, lw=2.0, ls="--", zorder=9)


def _draw_external_config_panel(
    ax: plt.Axes,
    *,
    N: int,
    start: Coord,
    m1: Coord,
    m2: Coord,
    spec: ExternalCaseSpec,
    title: str,
    show_legend: bool,
) -> None:
    base = np.zeros((N, N), dtype=np.float64)
    ax.imshow(
        base,
        origin="lower",
        cmap=plt.matplotlib.colors.ListedColormap([C_BG]),
        vmin=0.0,
        vmax=1.0,
        interpolation="nearest",
    )

    local_cells = set(spec.local_bias_map.keys())
    sticky_cells = set(spec.sticky_map.keys())
    for x, y in sorted(local_cells):
        face = C_OVERLAP if (x, y) in sticky_cells else C_SLOW
        ax.add_patch(
            Rectangle(
                (x - 0.5, y - 0.5),
                1.0,
                1.0,
                facecolor=face,
                edgecolor="none",
                alpha=0.85,
                zorder=2,
            )
        )
    for x, y in sorted(sticky_cells):
        if (x, y) in local_cells:
            continue
        ax.add_patch(
            Rectangle(
                (x - 0.5, y - 0.5),
                1.0,
                1.0,
                facecolor=C_STICKY,
                edgecolor="none",
                alpha=0.82,
                zorder=2,
            )
        )

    if spec.local_bias_map:
        xs = np.array([c[0] for c in spec.local_bias_map.keys()], dtype=np.float64)
        ys = np.array([c[1] for c in spec.local_bias_map.keys()], dtype=np.float64)
        us = np.array([DIR_VEC[v[0]][0] for v in spec.local_bias_map.values()], dtype=np.float64) * 0.72
        vs = np.array([DIR_VEC[v[0]][1] for v in spec.local_bias_map.values()], dtype=np.float64) * 0.72
        ax.quiver(
            xs,
            ys,
            us,
            vs,
            angles="xy",
            scale_units="xy",
            scale=1.0,
            color=C_ARROW,
            width=0.0036,
            headwidth=3.4,
            headlength=4.6,
            headaxislength=4.0,
            pivot="middle",
            alpha=0.92,
            zorder=7,
        )

    for (a, b), pass_prob in spec.barrier_map.items():
        _draw_barrier_segment(ax, a, b, pass_prob)

    for frm, to_list in spec.long_range_map.items():
        for to, _p in to_list:
            ax.annotate(
                "",
                xy=(to[0], to[1]),
                xytext=(frm[0], frm[1]),
                arrowprops=dict(arrowstyle="->", lw=1.8, color=C_SHORTCUT, shrinkA=8, shrinkB=8),
                zorder=8,
            )

    ax.scatter([start[0]], [start[1]], c=C_START, s=62, marker=MARK_START, zorder=10)
    ax.scatter([m1[0]], [m1[1]], c=C_M1, s=76, marker=MARK_M1, zorder=10)
    ax.scatter([m2[0]], [m2[1]], c=C_M2, s=76, marker=MARK_M2, zorder=10)
    ax.text(start[0] + 0.8, start[1] + 0.8, "start", color=C_TEXT_START, fontsize=8, weight="bold", zorder=11)
    ax.text(m1[0] + 0.8, m1[1] + 0.8, "m1", color=C_TEXT_M1, fontsize=8, weight="bold", zorder=11)
    ax.text(m2[0] + 0.8, m2[1] + 0.8, "m2", color=C_TEXT_M2, fontsize=8, weight="bold", zorder=11)

    ax.set_xlim(-0.5, N - 0.5)
    ax.set_ylim(-0.5, N - 0.5)
    ax.set_aspect("equal")
    ax.set_xticks(np.arange(-0.5, N, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, N, 1), minor=True)
    ax.grid(which="minor", color=C_GRID, linewidth=0.34)
    ax.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)
    for s in ax.spines.values():
        s.set_linewidth(2.2)
        s.set_color("black")
    ax.set_title(title, fontsize=10, pad=6)

    if show_legend:
        items = [
            Rectangle((0, 0), 1, 1, facecolor=C_SLOW, edgecolor="none", label="local bias cells"),
            Rectangle((0, 0), 1, 1, facecolor=C_STICKY, edgecolor="none", label="sticky cells"),
            Rectangle((0, 0), 1, 1, facecolor=C_OVERLAP, edgecolor="none", label="bias+sticky"),
            Line2D([0], [0], color=C_ARROW, lw=1.6, label="local bias arrows"),
            Line2D([0], [0], color="black", lw=2.0, label="reflecting barrier"),
            Line2D([0], [0], color=C_BARRIER_PERM, lw=2.0, ls="--", label="permeable barrier"),
            Line2D([0], [0], color=C_SHORTCUT, lw=1.8, label="long-range shortcut"),
            Line2D([0], [0], marker=MARK_START, color="w", markerfacecolor=C_START, markeredgecolor="black", markersize=7, label="start"),
            Line2D([0], [0], marker=MARK_M1, color="w", markerfacecolor=C_M1, markeredgecolor="black", markersize=7, label="m1"),
            Line2D([0], [0], marker=MARK_M2, color="w", markerfacecolor=C_M2, markeredgecolor="black", markersize=7, label="m2"),
        ]
        ax.legend(handles=items, loc="upper right", fontsize=8, frameon=True)


def plot_external_case_detailed_config(
    out_path: Path,
    *,
    N: int,
    start: Coord,
    m1: Coord,
    m2: Coord,
    spec: ExternalCaseSpec,
) -> None:
    fig, ax = plt.subplots(figsize=(8.8, 8.8))
    _draw_external_config_panel(
        ax,
        N=N,
        start=start,
        m1=m1,
        m2=m2,
        spec=spec,
        title=f"{spec.case_id}: {spec.name} (detailed config)",
        show_legend=True,
    )
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_external_case_heatmaps(
    out_path: Path,
    *,
    N: int,
    start: Coord,
    m1: Coord,
    m2: Coord,
    spec: ExternalCaseSpec,
    snapshots: Dict[int, np.ndarray],
    heat_times: Sequence[int],
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 10), constrained_layout=True)
    _draw_external_config_panel(
        axes[0, 0],
        N=N,
        start=start,
        m1=m1,
        m2=m2,
        spec=spec,
        title=f"{spec.case_id} config (same setup)",
        show_legend=False,
    )

    vmax = 0.0
    for t in heat_times:
        arr = snapshots.get(int(t))
        if arr is not None:
            vmax = max(vmax, float(arr.max()))
    if vmax <= 0:
        vmax = 1e-6

    heat_im = None
    for k, t in enumerate(heat_times):
        ax = axes.flatten()[k + 1]
        arr = snapshots.get(int(t))
        if arr is None:
            arr = np.zeros((N, N), dtype=np.float64)
        heat_im = _draw_heatmap_panel(ax, arr=arr, t=int(t), m1=m1, m2=m2, vmax=vmax)
        if k == 0:
            ax.set_title("Conditional occupancy heatmap", color="white", fontsize=10)

    if heat_im is not None:
        cbar = fig.colorbar(heat_im, ax=[axes[0, 1], axes[1, 0], axes[1, 1]], fraction=0.03, pad=0.02)
        cbar.ax.tick_params(labelsize=8, colors="black")
        cbar.outline.set_edgecolor("black")
        cbar.set_label(r"$P(X_t=n\mid T>t)$", color="black", fontsize=9)

    fig.savefig(out_path)
    plt.close(fig)


def plot_phase_category_map(
    out_path: Path,
    *,
    phase: np.ndarray,
    w2_values: Sequence[int],
    skip_values: Sequence[int],
) -> None:
    cmap = plt.matplotlib.colors.ListedColormap([C_PHASE0, C_PHASE1, C_PHASE2])
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(phase, origin="lower", cmap=cmap, vmin=-0.5, vmax=2.5, aspect="auto")
    ax.set_xticks(range(len(skip_values)))
    ax.set_xticklabels([str(v) for v in skip_values])
    ax.set_yticks(range(len(w2_values)))
    ax.set_yticklabels([str(v) for v in w2_values])
    ax.set_xlabel("skip2")
    ax.set_ylabel("w2")
    ax.set_title("Phase Map: single / weak-double / clear-double")
    for i in range(len(w2_values)):
        for j in range(len(skip_values)):
            ax.text(j, i, f"{int(phase[i,j])}", ha="center", va="center", fontsize=8, color="black")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cbar.set_ticks([0, 1, 2])
    cbar.set_ticklabels(["single", "weak double", "clear double"])
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_phase_sep_map(
    out_path: Path,
    *,
    sep: np.ndarray,
    w2_values: Sequence[int],
    skip_values: Sequence[int],
) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(sep, origin="lower", cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(skip_values)))
    ax.set_xticklabels([str(v) for v in skip_values])
    ax.set_yticks(range(len(w2_values)))
    ax.set_yticklabels([str(v) for v in w2_values])
    ax.set_xlabel("skip2")
    ax.set_ylabel("w2")
    ax.set_title(r"Separation Heatmap: $|\Delta t^*|/(w_{1/2}^{(1)}+w_{1/2}^{(2)})$")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cbar.set_label("separation score")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 2D two-target double-peak report assets.")
    parser.add_argument("--t-max", type=int, default=6000)
    parser.add_argument("--surv-tol", type=float, default=1e-13)
    parser.add_argument("--scan-t-max", type=int, default=2500)
    parser.add_argument("--scan-w2-min", type=int, default=1)
    parser.add_argument("--scan-w2-max", type=int, default=5)
    parser.add_argument("--scan-skip-max", type=int, default=6)
    parser.add_argument("--disable-phase-scan", action="store_true")
    parser.add_argument(
        "--external-testset",
        type=str,
        default="external/sparse_double_peak_testset.json",
        help="Path to sparse external testset JSON.",
    )
    parser.add_argument("--disable-external-testset", action="store_true")
    args = parser.parse_args()

    report_dir = Path(__file__).resolve().parent.parent
    data_dir = report_dir / "data"
    fig_dir = report_dir / "figures"
    out_dir = report_dir / "outputs"
    table_dir = report_dir / "tables"

    for d in (data_dir, fig_dir, out_dir, table_dir):
        ensure_dir(d)

    N = 31
    q = 0.2

    start = to0((15, 15))
    m1 = to0((22, 15))
    m2 = to0((7, 7))

    fast_nodes = [to0((15, 15)), to0((22, 15))]
    slow_nodes = [to0((15, 15)), to0((15, 27)), to0((3, 27)), to0((3, 7)), to0((7, 7))]

    fast_path = polyline_points(fast_nodes)
    slow_path = polyline_points(slow_nodes)

    cases = make_cases()

    results: List[CaseResult] = []
    layouts: Dict[str, Tuple[Dict[Coord, str], set[Coord], set[Coord]]] = {}
    series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    results_map: Dict[str, CaseResult] = {}
    heat_times_map: Dict[str, List[int]] = {}
    external_results: List[ExternalCaseResult] = []
    external_series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    external_transition_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]] = {}

    for case in cases:
        arrow_map, fast_cells, slow_cells = build_case_layout(
            N=N,
            fast_path=fast_path,
            slow_path=slow_path,
            w1=case.w1,
            w2=case.w2,
            skip2=case.skip2,
        )
        layouts[case.case_id] = (arrow_map, fast_cells, slow_cells)

        src_idx, dst_idx, probs = build_transition_arrays(N=N, q=q, delta=case.delta, arrow_map=arrow_map)
        f_any, f_m1, f_m2, surv = run_exact_two_target(
            N=N,
            start=start,
            target1=m1,
            target2=m2,
            src_idx=src_idx,
            dst_idx=dst_idx,
            probs=probs,
            t_max=args.t_max,
            surv_tol=args.surv_tol,
        )
        series_map[case.case_id] = (f_any, f_m1, f_m2, surv)

        result = summarize_case(case, f_any, f_m1, f_m2, surv)
        results.append(result)
        results_map[case.case_id] = result

        save_series_csv(out_dir / f"{case.case_id}_fpt.csv", f_any, f_m1, f_m2, surv)

        plot_case_geometry(
            fig_dir / f"case_{case.case_id}_geometry.pdf",
            N=N,
            start=start,
            m1=m1,
            m2=m2,
            fast_cells=fast_cells,
            slow_cells=slow_cells,
            fast_path=fast_path,
            slow_path=slow_path,
            slow_skip=case.skip2,
            title=f"{case.case_id}: w2={case.w2}, skip2={case.skip2}",
        )
        plot_case_fpt(fig_dir / f"case_{case.case_id}_fpt.pdf", f_any, f_m1, f_m2, result)
        plot_case_arrowfield(
            fig_dir / f"case_{case.case_id}_arrowfield.pdf",
            N=N,
            start=start,
            m1=m1,
            m2=m2,
            arrow_map=arrow_map,
            fast_cells=fast_cells,
            slow_cells=slow_cells,
            fast_path=fast_path,
            slow_path=slow_path,
            slow_skip=case.skip2,
            title=f"{case.case_id}: full local-bias arrow field (w2={case.w2}, skip2={case.skip2})",
        )

        heat_times = choose_heat_times(result)
        heat_times_map[case.case_id] = list(heat_times)
        snaps = conditional_snapshots_two_target(
            N=N,
            start=start,
            target1=m1,
            target2=m2,
            src_idx=src_idx,
            dst_idx=dst_idx,
            probs=probs,
            times=heat_times,
        )
        plot_case_environment_heatmaps(
            fig_dir / f"case_{case.case_id}_env_heatmap.pdf",
            N=N,
            start=start,
            m1=m1,
            m2=m2,
            fast_cells=fast_cells,
            slow_cells=slow_cells,
            fast_path=fast_path,
            slow_path=slow_path,
            slow_skip=case.skip2,
            case_title=f"{case.case_id}: w2={case.w2}, skip2={case.skip2}",
            snapshots=snaps,
            heat_times=heat_times,
        )

    plot_geometry_grid(
        fig_dir / "geometry_grid.pdf",
        N=N,
        start=start,
        m1=m1,
        m2=m2,
        fast_path=fast_path,
        slow_path=slow_path,
        cases=cases,
        layouts=layouts,
    )

    plot_fpt_grid(
        fig_dir / "fpt_grid.pdf",
        cases=cases,
        results_map=results_map,
        series_map=series_map,
    )
    plot_hazard_grid(
        fig_dir / "hazard_grid.pdf",
        cases=cases,
        series_map=series_map,
        results_map=results_map,
    )
    plot_symbol_legend_panel(fig_dir / "symbol_legend_panel.pdf")

    render_metrics_table(results, table_dir / "case_metrics.tex")
    render_mechanism_table(results, table_dir / "case_mechanism.tex")
    render_separation_table(results, table_dir / "case_separation.tex")

    if not args.disable_phase_scan:
        w2_values = list(range(args.scan_w2_min, args.scan_w2_max + 1))
        skip_values = list(range(0, args.scan_skip_max + 1))
        sep_grid = np.zeros((len(w2_values), len(skip_values)), dtype=np.float64)
        phase_grid = np.zeros((len(w2_values), len(skip_values)), dtype=np.int64)
        rows: List[dict] = []

        for i, w2 in enumerate(w2_values):
            for j, skip2 in enumerate(skip_values):
                scan_case = CaseConfig(
                    case_id=f"scan_w{w2}_s{skip2}",
                    title="phase scan",
                    w1=1,
                    w2=int(w2),
                    skip2=int(skip2),
                )
                arrow_map_s, _, _ = build_case_layout(
                    N=N,
                    fast_path=fast_path,
                    slow_path=slow_path,
                    w1=scan_case.w1,
                    w2=scan_case.w2,
                    skip2=scan_case.skip2,
                )
                s_src, s_dst, s_prob = build_transition_arrays(N=N, q=q, delta=scan_case.delta, arrow_map=arrow_map_s)
                s_any, s_m1, s_m2, s_surv = run_exact_two_target(
                    N=N,
                    start=start,
                    target1=m1,
                    target2=m2,
                    src_idx=s_src,
                    dst_idx=s_dst,
                    probs=s_prob,
                    t_max=args.scan_t_max,
                    surv_tol=max(args.surv_tol, 1e-10),
                )
                s_res = summarize_case(scan_case, s_any, s_m1, s_m2, s_surv)
                sep_grid[i, j] = s_res.sep_mode_width

                has_double = int(s_res.t_peak1 is not None and s_res.t_peak2 is not None)
                phase = classify_phase(s_res)
                clear_double = int(phase == 2)
                phase_grid[i, j] = phase

                rows.append(
                    {
                        "w2": int(w2),
                        "skip2": int(skip2),
                        "phase": int(phase),
                        "double_peak": int(has_double),
                        "clear_double_peak": int(clear_double),
                        "sep_mode_width": float(s_res.sep_mode_width),
                        "t_peak1": s_res.t_peak1,
                        "t_peak2": s_res.t_peak2,
                        "p_m1": float(s_res.p_m1),
                        "p_m2": float(s_res.p_m2),
                        "valley_over_max": s_res.valley_over_max,
                    }
                )

        if rows:
            with (data_dir / "scan_w2_skip2.csv").open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        (data_dir / "scan_w2_skip2.json").write_text(
            json.dumps(
                {
                    "w2_values": w2_values,
                    "skip_values": skip_values,
                    "phase_grid": phase_grid.tolist(),
                    "sep_grid": sep_grid.tolist(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        plot_phase_category_map(
            fig_dir / "phase_w2_skip2.pdf",
            phase=phase_grid,
            w2_values=w2_values,
            skip_values=skip_values,
        )
        plot_phase_sep_map(
            fig_dir / "phase_sep_w2_skip2.pdf",
            sep=sep_grid,
            w2_values=w2_values,
            skip_values=skip_values,
        )

    ext_path = Path(args.external_testset).expanduser()
    if not args.disable_external_testset and ext_path.exists():
        specs = load_external_sparse_specs(path=ext_path, N=N, default_delta=0.2)
        for spec in specs:
            src_idx, dst_idx, probs = build_transition_arrays_general(
                N=N,
                q=q,
                local_bias_map=spec.local_bias_map,
                sticky_map=spec.sticky_map,
                barrier_map=spec.barrier_map,
                long_range_map=spec.long_range_map,
                global_bias=spec.global_bias,
            )
            f_any, f_m1, f_m2, surv = run_exact_two_target(
                N=N,
                start=start,
                target1=m1,
                target2=m2,
                src_idx=src_idx,
                dst_idx=dst_idx,
                probs=probs,
                t_max=args.t_max,
                surv_tol=args.surv_tol,
            )
            case_cfg = CaseConfig(
                case_id=spec.case_id,
                title=spec.name,
                w1=1,
                w2=0,
                skip2=0,
            )
            res = summarize_case(case_cfg, f_any, f_m1, f_m2, surv)
            phase = classify_phase(res)
            ext_res = ExternalCaseResult(
                spec=spec,
                result=res,
                local_bias_count=len(spec.local_bias_map),
                sticky_count=len(spec.sticky_map),
                barrier_count=len(spec.barrier_map),
                shortcut_count=sum(len(v) for v in spec.long_range_map.values()),
                phase=phase,
            )
            external_results.append(ext_res)
            external_series_map[spec.case_id] = (f_any, f_m1, f_m2, surv)
            external_transition_map[spec.case_id] = (src_idx, dst_idx, probs)
            save_series_csv(out_dir / f"{spec.case_id}_external_fpt.csv", f_any, f_m1, f_m2, surv)

        external_double = [er for er in external_results if er.phase > 0]
        render_external_sparse_config_table(external_double, table_dir / "sparse_testset_configs.tex")
        render_external_sparse_metrics_table(external_double, table_dir / "sparse_testset_metrics.tex")
        plot_external_sparse_fpt_grid(
            fig_dir / "sparse_testset_fpt_grid.pdf",
            external_results=external_double,
            series_map=external_series_map,
        )

        for er in external_double:
            plot_external_case_detailed_config(
                fig_dir / f"sparse_{er.spec.case_id}_config_detailed.pdf",
                N=N,
                start=start,
                m1=m1,
                m2=m2,
                spec=er.spec,
            )
            heat_times = choose_heat_times(er.result)
            src_idx, dst_idx, probs = external_transition_map[er.spec.case_id]
            snaps = conditional_snapshots_two_target(
                N=N,
                start=start,
                target1=m1,
                target2=m2,
                src_idx=src_idx,
                dst_idx=dst_idx,
                probs=probs,
                times=heat_times,
            )
            plot_external_case_heatmaps(
                fig_dir / f"sparse_{er.spec.case_id}_env_heatmap.pdf",
                N=N,
                start=start,
                m1=m1,
                m2=m2,
                spec=er.spec,
                snapshots=snaps,
                heat_times=heat_times,
            )

        ext_summary: Dict[str, Any] = {
            "source_json": str(ext_path),
            "n_cases": len(external_results),
            "n_double_cases": len(external_double),
            "double_case_ids": [er.spec.case_id for er in external_double],
            "cases": [],
        }
        for er in external_results:
            ext_summary["cases"].append(
                {
                    "case_id": er.spec.case_id,
                    "name": er.spec.name,
                    "type": er.spec.type_name,
                    "expected": er.spec.expected,
                    "note": er.spec.note,
                    "local_bias_count": er.local_bias_count,
                    "sticky_count": er.sticky_count,
                    "barrier_count": er.barrier_count,
                    "shortcut_count": er.shortcut_count,
                    "global_bias": list(er.spec.global_bias),
                    "phase": er.phase,
                    "t_peak1": er.result.t_peak1,
                    "t_peak2": er.result.t_peak2,
                    "p_m1": er.result.p_m1,
                    "p_m2": er.result.p_m2,
                    "sep_mode_width": er.result.sep_mode_width,
                    "valley_over_max": er.result.valley_over_max,
                }
            )
        (data_dir / "sparse_testset_results.json").write_text(json.dumps(ext_summary, indent=2), encoding="utf-8")
    else:
        placeholder = "\n".join(
            [
                "\\begin{tabular}{ll}",
                "\\toprule",
                "Status & Note \\\\",
                "\\midrule",
                "disabled & external testset not run \\\\",
                "\\bottomrule",
                "\\end{tabular}",
            ]
        )
        (table_dir / "sparse_testset_configs.tex").write_text(placeholder, encoding="utf-8")
        (table_dir / "sparse_testset_metrics.tex").write_text(placeholder, encoding="utf-8")

    summary = {
        "model": {
            "N": N,
            "q": q,
            "boundary": "reflecting",
            "local_bias_rule": "shift 20% of stay probability to arrow direction",
            "start_1_based": [15, 15],
            "target1_1_based": [22, 15],
            "target2_1_based": [7, 7],
            "fast_path_1_based": [[15, 15], [22, 15]],
            "slow_path_1_based": [[15, 15], [15, 27], [3, 27], [3, 7], [7, 7]],
        },
        "cases": [
            {
                "case_id": r.config.case_id,
                "title": r.config.title,
                "w1": r.config.w1,
                "w2": r.config.w2,
                "skip2": r.config.skip2,
                "delta": r.config.delta,
                "steps": r.steps,
                "t_peak1": r.t_peak1,
                "t_peak2": r.t_peak2,
                "h_peak1": r.h_peak1,
                "h_peak2": r.h_peak2,
                "t_valley": r.t_valley,
                "h_valley": r.h_valley,
                "peak_ratio": r.peak_ratio,
                "valley_over_max": r.valley_over_max,
                "p_m1": r.p_m1,
                "p_m2": r.p_m2,
                "t_mode_m1": r.t_mode_m1,
                "t_mode_m2": r.t_mode_m2,
                "h_mode_m1": r.h_mode_m1,
                "h_mode_m2": r.h_mode_m2,
                "hw_m1": r.hw_m1,
                "hw_m2": r.hw_m2,
                "sep_mode_width": r.sep_mode_width,
                "absorbed_mass": r.absorbed_mass,
                "survival_tail": r.survival_tail,
                "heat_times": heat_times_map.get(r.config.case_id, []),
            }
            for r in results
        ],
    }
    if external_results:
        summary["external_sparse_testset"] = {
            "source_json": str(ext_path),
            "cases": [
                {
                    "case_id": er.spec.case_id,
                    "name": er.spec.name,
                    "type": er.spec.type_name,
                    "phase": er.phase,
                    "t_peak1": er.result.t_peak1,
                    "t_peak2": er.result.t_peak2,
                    "p_m1": er.result.p_m1,
                    "p_m2": er.result.p_m2,
                    "sep_mode_width": er.result.sep_mode_width,
                }
                for er in external_results
            ],
        }
    if not args.disable_phase_scan:
        summary["phase_scan"] = {
            "w2_values": list(range(args.scan_w2_min, args.scan_w2_max + 1)),
            "skip_values": list(range(0, args.scan_skip_max + 1)),
            "scan_t_max": int(args.scan_t_max),
            "files": {
                "csv": "data/scan_w2_skip2.csv",
                "json": "data/scan_w2_skip2.json",
                "phase_map": "figures/phase_w2_skip2.pdf",
                "sep_map": "figures/phase_sep_w2_skip2.pdf",
            },
        }
    (data_dir / "case_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
