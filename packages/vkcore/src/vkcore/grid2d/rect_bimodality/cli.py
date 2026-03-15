#!/usr/bin/env python3
"""Build data/figures/tables for the 2D rectangle bimodality report.

This report has two parts:
1) Two targets placed near the two ends of a non-square rectangle. We design a short
   (fast) and a long (slow) biased path to induce two timescales, then scan rectangle
   width and start position to find when the total FPT becomes double-peaked.
2) One target with a reflecting-wall corridor and local bias inside the corridor,
   optionally with a global bias. We scan rectangle width to see when two peaks appear.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

Coord = Tuple[int, int]
Edge = Tuple[Coord, Coord]
DirectedEdge = Tuple[Coord, Coord]

DIR_VEC: dict[str, Coord] = {
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
C_TGT = "#1565c0"
C_GRID = "#c8c8b4"
C_GRID_MAJOR = "#9ea390"
C_TEXT_START = "#c62828"
C_TEXT_M1 = "#0d47a1"
C_TEXT_M2 = "#1b2a72"
C_TEXT_TGT = "#0d47a1"
C_ANY = "#111111"
C_SPLIT1 = "#1f77b4"
C_SPLIT2 = "#ff7f0e"
C_WALL = "#111111"
C_PHASE0 = "#e8e8e8"
C_PHASE1 = "#9ecae1"
C_PHASE2 = "#fb9a99"
C_CH1 = "#2c7fb8"
C_CH2 = "#f03b20"

MARK_START = "s"
MARK_M1 = "D"
MARK_M2 = "o"
MARK_TGT = "D"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def purge_case_level_artifacts(*, fig_dir: Path, out_dir: Path) -> None:
    """Remove stale case-level files from previous runs.

    Representative sets can change across runs. Without cleanup, old per-case
    files remain in `figures/` and `outputs/` and may be mistaken as current
    results, even though they are no longer referenced by tables/summary.
    """
    patterns = [
        # time-series exports
        ("out", "TT_*_fpt.csv"),
        ("out", "OT_*_fpt.csv"),
        # two-target per-case figures
        ("fig", "TT_*_geometry.pdf"),
        ("fig", "TT_*_fpt.pdf"),
        ("fig", "TT_*_hazard.pdf"),
        ("fig", "TT_*_env_heatmap.pdf"),
        # one-target per-case figures
        ("fig", "OT_*_geometry.pdf"),
        ("fig", "OT_*_fpt.pdf"),
        ("fig", "OT_*_hazard.pdf"),
        ("fig", "OT_*_env_heatmap.pdf"),
    ]
    for where, pat in patterns:
        root = out_dir if where == "out" else fig_dir
        for fp in root.glob(pat):
            try:
                fp.unlink()
            except FileNotFoundError:
                pass


def purge_generated_artifacts(
    *,
    data_dir: Path,
    fig_dir: Path,
    out_dir: Path,
    table_dir: Path,
    keep_scan_data: bool = False,
) -> None:
    """Remove generated artifacts so each run is self-consistent.

    This prevents stale files from old runs being silently reused when some
    branch of the current run does not emit a specific figure/table.
    """
    # Case-level files (many per run).
    purge_case_level_artifacts(fig_dir=fig_dir, out_dir=out_dir)

    # Scan-level and summary data.
    data_patterns = ["case_summary.json"]
    if not bool(keep_scan_data):
        data_patterns.extend(
            [
                "tt_scan_width_xstart.csv",
                "tt_scan_width_xstart.json",
                "ot_scan_width_globalbias.csv",
                "ot_scan_width_globalbias.json",
                "ot_scan_corridor_halfwidth.csv",
                "ot_scan_corridor_halfwidth.json",
                "ot_scan_bias2d.csv",
                "ot_scan_bias2d.json",
            ]
        )
    for pat in data_patterns:
        fp = data_dir / pat
        if fp.exists():
            fp.unlink()

    # Generated tables.
    for pat in ("tt_*.tex", "ot_*.tex"):
        for fp in table_dir.glob(pat):
            fp.unlink()

    # Generated report figures (this report namespace only).
    for pat in ("tt_*.pdf", "ot_*.pdf", "symbol_legend_panel.pdf"):
        for fp in fig_dir.glob(pat):
            fp.unlink()


def validate_summary_artifact_paths(summary: dict, *, report_dir: Path) -> None:
    """Ensure all path references recorded in case_summary exist on disk."""

    missing: List[str] = []

    def walk(v: Any) -> None:
        if isinstance(v, dict):
            for vv in v.values():
                walk(vv)
            return
        if isinstance(v, list):
            for vv in v:
                walk(vv)
            return
        if isinstance(v, str):
            if v.startswith(("figures/", "tables/", "data/", "outputs/")):
                if not (report_dir / v).exists():
                    missing.append(v)

    walk(summary)
    if missing:
        missing_txt = ", ".join(sorted(set(missing)))
        raise FileNotFoundError(f"Missing generated artifacts referenced in case_summary.json: {missing_txt}")


def validate_representative_phase_consistency(
    *,
    tt_rows: Sequence[dict],
    ot_rows: Sequence[dict],
    tt_rep_specs: Sequence["TTCaseSpec"],
    tt_width_specs: Sequence["TTCaseSpec"],
    ot_rep_specs: Sequence["OTCaseSpec"],
) -> None:
    """Check selected representatives are present in scan rows with expected phases."""

    tt_phase_map = {(int(r["Wy"]), int(r["x_start"])): int(r["phase"]) for r in tt_rows}
    ot_phase_map = {(int(r["Wy"]), round(float(r["bx"]), 3)): int(r["phase"]) for r in ot_rows}

    for s in tt_rep_specs:
        key = (int(s.Wy), int(s.x_start))
        if key not in tt_phase_map:
            raise KeyError(f"Two-target representative missing in scan rows: {s.case_id}")
        if int(tt_phase_map[key]) != 2:
            raise ValueError(f"Two-target representative must be phase=2, got phase={tt_phase_map[key]} for {s.case_id}")

    for s in tt_width_specs:
        key = (int(s.Wy), int(s.x_start))
        if key not in tt_phase_map:
            raise KeyError(f"Two-target width-sweep case missing in scan rows: {s.case_id}")

    for s in ot_rep_specs:
        key = (int(s.Wy), round(float(s.bx), 3))
        if key not in ot_phase_map:
            raise KeyError(f"One-target representative missing in scan rows: {s.case_id}")


def validate_tt_representative_branch_coverage(
    *,
    tt_rows: Sequence[dict],
    tt_rep_specs: Sequence["TTCaseSpec"],
    key_branches: Sequence[int] = (8, 10, 12),
) -> None:
    """Ensure TT representatives cover all key branches that actually have phase-2 rows."""

    clear_branches = {int(r["x_start"]) for r in tt_rows if int(r["phase"]) == 2}
    key_set = {int(x) for x in key_branches}
    required = sorted(clear_branches.intersection(key_set))
    if not required:
        return

    rep_branches = {int(s.x_start) for s in tt_rep_specs}
    missing = [x for x in required if x not in rep_branches]
    if missing:
        raise ValueError(
            "Two-target representatives miss key clear-double branch(es): "
            f"{missing}; required key branches with phase=2 are {required}."
        )


def validate_tt_width_sweep_transition(results: Sequence["TTCaseResult"]) -> None:
    """Ensure fixed-branch width sweep can support transition-focused narrative."""
    if not results:
        return
    phases = [int(r.phase) for r in results]
    if not any(p >= 2 for p in phases):
        raise ValueError("Width-sweep set has no clear-double case (phase=2).")
    if not any(p == 0 for p in phases):
        raise ValueError("Width-sweep set has no single-peak case (phase=0).")


def _edge_key(a: Coord, b: Coord) -> Edge:
    return (a, b) if a <= b else (b, a)


def _directed_edge_key(a: Coord, b: Coord) -> DirectedEdge:
    return (a, b)


def idx(x: int, y: int, Lx: int) -> int:
    return y * Lx + x


def project_mass_nonnegative(p: np.ndarray, *, cap: float, eps: float = 1e-12) -> float:
    """Project tiny floating drift to a valid nonnegative mass budget.

    The exact recursion should keep probabilities nonnegative and total mass <= `cap`.
    Numerically we may get tiny negative entries or tiny overflow (e.g. 1+1e-15).
    This helper removes those artifacts without changing the underlying model.
    """
    np.maximum(p, 0.0, out=p)
    s = float(p.sum())
    cap = max(0.0, float(cap))
    if s <= cap:
        return s
    # Near-boundary overflow: project back to cap.
    if s <= cap + float(eps):
        if s > 0.0:
            p *= cap / s
        else:
            p.fill(0.0)
        return cap
    # Conservative fallback if drift is larger than expected.
    if s > 0.0:
        p *= cap / s
    else:
        p.fill(0.0)
    return cap


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


def corridor_assignments(
    path_points: Sequence[Coord],
    *,
    width: int,
    skip: int,
    Lx: int,
    Wy: int,
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
        for dx0 in range(-width, width + 1):
            for dy0 in range(-width, width + 1):
                if abs(dx0) + abs(dy0) > width:
                    continue
                x = c[0] + dx0
                y = c[1] + dy0
                if 0 <= x < Lx and 0 <= y < Wy:
                    arrows[(x, y)] = d
                    cells.add((x, y))
    return arrows, cells


def _parse_global_bias(q: float, bx: float, by: float) -> Dict[str, float]:
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


def build_transition_arrays_general_rect(
    *,
    Lx: int,
    Wy: int,
    q: float,
    local_bias_map: Dict[Coord, Tuple[str, float]],
    sticky_map: Dict[Coord, float],
    barrier_map: Dict[Edge, float],
    directed_barrier_map: Dict[DirectedEdge, float] | None = None,
    long_range_map: Dict[Coord, List[Tuple[Coord, float]]],
    global_bias: Tuple[float, float],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build the transition kernel for the rectangular grid model.

    `barrier_map` keeps the legacy undirected pass probability on an edge. When
    `directed_barrier_map` is provided it overrides the pass probability for the
    specific ordered crossing `(from_cell, to_cell)`, which lets callers model
    directional membrane permeability without affecting existing reports.
    """
    base_moves = _parse_global_bias(q, float(global_bias[0]), float(global_bias[1]))

    src: List[int] = []
    dst: List[int] = []
    prob: List[float] = []

    for y in range(Wy):
        for x in range(Lx):
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
                dx0, dy0 = DIR_VEC[d]
                nx = x + dx0
                ny = y + dy0
                if nx < 0 or nx >= Lx or ny < 0 or ny >= Wy:
                    stay_extra += p
                    continue
                pass_prob = float(barrier_map.get(_edge_key(c, (nx, ny)), 1.0))
                if directed_barrier_map is not None:
                    pass_prob = float(directed_barrier_map.get(_directed_edge_key(c, (nx, ny)), pass_prob))
                pass_prob = min(max(pass_prob, 0.0), 1.0)
                flow = p * pass_prob
                blocked = p - flow
                if blocked > 0.0:
                    stay_extra += blocked
                if flow > 0.0:
                    j = idx(nx, ny, Lx)
                    out[j] = out.get(j, 0.0) + flow

            for to_pos, p_jump in long_range_map.get(c, []):
                if p_jump <= 0.0:
                    continue
                take = min(float(p_jump), max(stay_extra, 0.0))
                if take <= 0.0:
                    continue
                stay_extra -= take
                j_to = idx(to_pos[0], to_pos[1], Lx)
                out[j_to] = out.get(j_to, 0.0) + take

            j_self = idx(x, y, Lx)
            out[j_self] = out.get(j_self, 0.0) + stay_extra

            s = float(sum(out.values()))
            if s <= 0.0:
                raise ValueError(f"row sum <= 0 at {(x, y)}")
            if not np.isclose(s, 1.0, atol=1e-12):
                for j in list(out.keys()):
                    out[j] /= s

            i = idx(x, y, Lx)
            for j, p in out.items():
                src.append(i)
                dst.append(j)
                prob.append(float(p))

    return (
        np.asarray(src, dtype=np.int64),
        np.asarray(dst, dtype=np.int64),
        np.asarray(prob, dtype=np.float64),
    )


def run_exact_two_target_rect(
    *,
    Lx: int,
    Wy: int,
    start: Coord,
    target1: Coord,
    target2: Coord,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    t_max: int,
    surv_tol: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n_states = Lx * Wy
    i_start = idx(start[0], start[1], Lx)
    i_m1 = idx(target1[0], target1[1], Lx)
    i_m2 = idx(target2[0], target2[1], Lx)

    p = np.zeros(n_states, dtype=np.float64)
    p[i_start] = 1.0

    f_any = [0.0]
    f_m1 = [0.0]
    f_m2 = [0.0]
    surv = [1.0]

    for _ in range(1, int(t_max) + 1):
        surv_prev = float(surv[-1])
        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_idx, p[src_idx] * probs)

        hit1 = max(float(p_next[i_m1]), 0.0)
        hit2 = max(float(p_next[i_m2]), 0.0)
        hit = hit1 + hit2
        if hit > surv_prev:
            scale = (surv_prev / hit) if hit > 0.0 else 0.0
            hit1 *= scale
            hit2 *= scale
            hit = surv_prev

        p_next[i_m1] = 0.0
        p_next[i_m2] = 0.0

        remaining_cap = max(0.0, surv_prev - hit)
        s = project_mass_nonnegative(p_next, cap=remaining_cap)

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


def run_exact_one_target_rect(
    *,
    Lx: int,
    Wy: int,
    start: Coord,
    target: Coord,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    t_max: int,
    surv_tol: float,
    channel_mask: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Exact recursion for one absorbing target.

    If channel_mask is provided (shape (n_states,), bool), also returns a two-channel
    decomposition of absorption flux into the target:
      f_ch1: flux from channel_mask=True sources,
      f_ch2: flux from channel_mask=False sources.
    """
    n_states = Lx * Wy
    i_start = idx(start[0], start[1], Lx)
    i_tgt = idx(target[0], target[1], Lx)

    p = np.zeros(n_states, dtype=np.float64)
    p[i_start] = 1.0

    f = [0.0]
    f_ch1 = [0.0]
    f_ch2 = [0.0]
    surv = [1.0]

    hit_mask = (dst_idx == i_tgt)
    hit_src = src_idx[hit_mask]
    hit_prob = probs[hit_mask]
    hit_src_is_ch1: np.ndarray | None = None
    if channel_mask is not None:
        hit_src_is_ch1 = channel_mask[hit_src]

    for _ in range(1, int(t_max) + 1):
        surv_prev = float(surv[-1])

        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_idx, p[src_idx] * probs)

        # Compute hit flux decomposition from p (time t-1), aligned with p_next[target].
        hit_total = max(float(p_next[i_tgt]), 0.0)
        if hit_total > surv_prev:
            hit_total = surv_prev

        hit1 = 0.0
        if hit_src_is_ch1 is not None:
            hit1 = max(float(np.sum(p[hit_src[hit_src_is_ch1]] * hit_prob[hit_src_is_ch1])), 0.0)
            hit1 = min(hit1, hit_total)
        hit2 = hit_total - hit1

        p_next[i_tgt] = 0.0

        remaining_cap = max(0.0, surv_prev - hit_total)
        s = project_mass_nonnegative(p_next, cap=remaining_cap)

        f.append(hit_total)
        f_ch1.append(hit1)
        f_ch2.append(hit2)
        surv.append(s)

        p = p_next
        if s < surv_tol:
            break

    return (
        np.asarray(f, dtype=np.float64),
        np.asarray(f_ch1, dtype=np.float64),
        np.asarray(f_ch2, dtype=np.float64),
        np.asarray(surv, dtype=np.float64),
    )


def validate_tt_series_consistency(
    *,
    case_id: str,
    f_any: np.ndarray,
    f_m1: np.ndarray,
    f_m2: np.ndarray,
    surv: np.ndarray,
    tol: float = 1e-9,
) -> None:
    if not (len(f_any) == len(f_m1) == len(f_m2) == len(surv)):
        raise ValueError(f"{case_id}: TT series length mismatch")
    if len(f_any) == 0:
        raise ValueError(f"{case_id}: empty TT series")
    if np.min(f_any) < -tol or np.min(f_m1) < -tol or np.min(f_m2) < -tol:
        raise ValueError(f"{case_id}: TT negative FPT mass detected")
    if np.min(surv) < -tol:
        raise ValueError(f"{case_id}: TT negative survival detected")
    if np.max(surv) > 1.0 + tol:
        raise ValueError(f"{case_id}: TT survival exceeds 1")
    ds = np.diff(surv.astype(np.float64))
    if np.max(ds) > tol:
        raise ValueError(f"{case_id}: TT survival is not nonincreasing")
    decomp_err = float(np.max(np.abs(f_any - (f_m1 + f_m2))))
    if decomp_err > tol:
        raise ValueError(f"{case_id}: TT decomposition error={decomp_err:.3e}")
    if len(f_any) > 1:
        bal_err = float(np.max(np.abs(surv[:-1] - f_any[1:] - surv[1:])))
        if bal_err > tol:
            raise ValueError(f"{case_id}: TT mass-balance error={bal_err:.3e}")


def validate_ot_series_consistency(
    *,
    case_id: str,
    f_total: np.ndarray,
    f_corr: np.ndarray,
    f_outer: np.ndarray,
    surv: np.ndarray,
    tol: float = 1e-9,
) -> None:
    if not (len(f_total) == len(f_corr) == len(f_outer) == len(surv)):
        raise ValueError(f"{case_id}: OT series length mismatch")
    if len(f_total) == 0:
        raise ValueError(f"{case_id}: empty OT series")
    if np.min(f_total) < -tol or np.min(f_corr) < -tol or np.min(f_outer) < -tol:
        raise ValueError(f"{case_id}: OT negative FPT mass detected")
    if np.min(surv) < -tol:
        raise ValueError(f"{case_id}: OT negative survival detected")
    if np.max(surv) > 1.0 + tol:
        raise ValueError(f"{case_id}: OT survival exceeds 1")
    ds = np.diff(surv.astype(np.float64))
    if np.max(ds) > tol:
        raise ValueError(f"{case_id}: OT survival is not nonincreasing")
    decomp_err = float(np.max(np.abs(f_total - (f_corr + f_outer))))
    if decomp_err > tol:
        raise ValueError(f"{case_id}: OT decomposition error={decomp_err:.3e}")
    if len(f_total) > 1:
        bal_err = float(np.max(np.abs(surv[:-1] - f_total[1:] - surv[1:])))
        if bal_err > tol:
            raise ValueError(f"{case_id}: OT mass-balance error={bal_err:.3e}")


def conditional_snapshots_two_target_rect(
    *,
    Lx: int,
    Wy: int,
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
    n_states = Lx * Wy

    i_start = idx(start[0], start[1], Lx)
    i_m1 = idx(target1[0], target1[1], Lx)
    i_m2 = idx(target2[0], target2[1], Lx)

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
            snap = p_next.reshape(Wy, Lx).copy()
            if s > 0.0:
                snap /= s
            out[int(t)] = snap
        p = p_next
    return out


def conditional_snapshots_one_target_rect(
    *,
    Lx: int,
    Wy: int,
    start: Coord,
    target: Coord,
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
    n_states = Lx * Wy

    i_start = idx(start[0], start[1], Lx)
    i_tgt = idx(target[0], target[1], Lx)

    p = np.zeros(n_states, dtype=np.float64)
    p[i_start] = 1.0
    out: Dict[int, np.ndarray] = {}

    for t in range(1, t_max + 1):
        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_idx, p[src_idx] * probs)
        p_next[i_tgt] = 0.0
        if t in times_set:
            s = float(p_next.sum())
            snap = p_next.reshape(Wy, Lx).copy()
            if s > 0.0:
                snap /= s
            out[int(t)] = snap
        p = p_next
    return out


def find_two_peaks(
    f: np.ndarray,
    *,
    min_rel_height: float = 0.06,
    min_gap: int = 20,
    smooth_window: int = 7,
    min_peak_balance: float = 0.08,
    min_valley_drop: float = 0.08,
    min_minor_peak_drop: float = 0.005,
    dominance_tol: float = 0.02,
) -> Tuple[int | None, int | None]:
    if f.size < 3:
        return None, None
    # Detect on a smoothed envelope to suppress parity/staircase artifacts.
    fs = smooth_series_display(f.astype(np.float64), window=max(3, int(smooth_window)))
    f_max = float(np.max(fs))
    if f_max <= 0.0:
        return None, None
    thr = float(min_rel_height) * f_max
    peaks: List[int] = []
    for t in range(1, fs.size - 1):
        if fs[t] > fs[t - 1] and fs[t] >= fs[t + 1] and fs[t] >= thr:
            peaks.append(t)
    if len(peaks) < 2:
        return None, None

    # Require meaningful two-lobe separation.
    gap = max(1, int(min_gap))
    best_pair: Tuple[int, int] | None = None
    best_score = -1.0
    for i, a in enumerate(peaks[:-1]):
        ha = float(fs[a])
        for b in peaks[i + 1 :]:
            if (b - a) < gap:
                continue
            hb = float(fs[b])
            if ha <= 0.0 or hb <= 0.0:
                continue
            # Prevent shoulder artifacts: each selected peak should be near-dominant
            # on its own side of the valley.
            k_min = int(np.argmin(fs[a : b + 1]))
            v_idx = int(a + k_min)
            if not (a < v_idx < b):
                continue
            left_dom = float(np.max(fs[: v_idx + 1]))
            right_dom = float(np.max(fs[v_idx:]))
            tol = max(0.0, float(dominance_tol))
            if ha < (1.0 - tol) * left_dom:
                continue
            if hb < (1.0 - tol) * right_dom:
                continue
            bal = float(min(ha, hb) / max(ha, hb))
            if bal < float(min_peak_balance):
                continue
            hv = float(fs[v_idx])
            valley_drop = float(1.0 - hv / max(ha, hb))
            if valley_drop < float(min_valley_drop):
                continue
            # Also require valley to be below the weaker peak by a non-trivial amount;
            # this rejects almost-flat "pseudo second peaks".
            minor_drop = float(1.0 - hv / max(min(ha, hb), 1e-15))
            if minor_drop < float(min_minor_peak_drop):
                continue
            score = float(b - a) * min(ha, hb) * valley_drop * max(1e-6, minor_drop)
            if score > best_score:
                best_score = score
                best_pair = (int(a), int(b))
    if best_pair is None:
        return None, None
    return best_pair


def half_width_at_half_max(f: np.ndarray, mode: int) -> float:
    if mode <= 0 or mode >= len(f):
        return 0.0
    peak = float(f[mode])
    if peak <= 0.0:
        return 0.0
    thr = 0.5 * peak
    left = int(mode)
    right = int(mode)
    while left > 1 and f[left - 1] >= thr:
        left -= 1
    while right < len(f) - 1 and f[right + 1] >= thr:
        right += 1
    return 0.5 * float(right - left)


@dataclass(frozen=True)
class TTCaseSpec:
    Wy: int
    x_start: int
    w_fast: int
    w_slow: int
    fast_skip: int
    slow_skip: int
    delta_fast: float
    delta_slow: float

    @property
    def case_id(self) -> str:
        return f"TT_W{self.Wy:02d}_X{self.x_start:02d}"


@dataclass
class TTCaseResult:
    spec: TTCaseSpec
    steps: int
    t_peak1: int | None
    t_peak2: int | None
    t_valley: int | None
    peak_ratio: float | None
    valley_over_max: float | None
    p_m1: float
    p_m2: float
    t_mode_m1: int
    t_mode_m2: int
    hw_m1: float
    hw_m2: float
    sep_mode_width: float
    absorbed_mass: float
    survival_tail: float
    phase: int


@dataclass(frozen=True)
class OTCaseSpec:
    Wy: int
    bx: float
    corridor_halfwidth: int
    wall_margin: int
    delta_core: float
    delta_open: float

    @property
    def case_id(self) -> str:
        b = f"{self.bx:.3f}".replace(".", "p").replace("-", "m")
        return f"OT_W{self.Wy:02d}_bx{b}"


@dataclass
class OTCaseResult:
    spec: OTCaseSpec
    steps: int
    t_peak1: int | None
    t_peak2: int | None
    t_valley: int | None
    valley_over_max: float | None
    peak_balance: float | None
    sep_peaks: float
    absorbed_mass: float
    survival_tail: float
    phase: int


def classify_phase_two_target(r: TTCaseResult) -> int:
    has_double = int(r.t_peak1 is not None and r.t_peak2 is not None)
    peak_ratio_ok = bool(r.peak_ratio is not None and r.peak_ratio >= 0.10)
    valley_margin_ok = bool(
        r.peak_ratio is not None
        and r.valley_over_max is not None
        and (r.peak_ratio - r.valley_over_max) >= 0.01
    )
    clear_double = int(
        has_double
        and r.sep_mode_width >= 1.0
        and min(r.p_m1, r.p_m2) >= 0.15
        and (r.valley_over_max is not None and r.valley_over_max <= 0.35)
        and peak_ratio_ok
        and valley_margin_ok
    )
    return 2 if clear_double else (1 if has_double else 0)


def classify_phase_one_target(r: OTCaseResult) -> int:
    has_double = int(r.t_peak1 is not None and r.t_peak2 is not None)
    clear_double = int(
        has_double
        and r.sep_peaks >= 1.0
        and (r.valley_over_max is not None and r.valley_over_max <= 0.35)
        and (r.peak_balance is not None and r.peak_balance >= 0.15)
    )
    return 2 if clear_double else (1 if has_double else 0)


def summarize_two_target(
    spec: TTCaseSpec,
    f_any: np.ndarray,
    f_m1: np.ndarray,
    f_m2: np.ndarray,
    surv: np.ndarray,
) -> TTCaseResult:
    tp1, tp2 = find_two_peaks(f_any)
    tv = None
    peak_ratio = None
    valley_over_max = None
    f_any_s = smooth_series_display(f_any.astype(np.float64), window=7)
    if tp1 is not None and tp2 is not None and tp1 + 1 < tp2:
        window = f_any_s[tp1 : tp2 + 1]
        k = int(np.argmin(window))
        tv = tp1 + k
        hp1 = float(f_any_s[tp1])
        hp2 = float(f_any_s[tp2])
        hv = float(f_any_s[tv])
        if hp1 > 0 and hp2 > 0:
            peak_ratio = float(min(hp1, hp2) / max(hp1, hp2))
            valley_over_max = float(hv / max(hp1, hp2))

    absorbed_mass = float(np.sum(f_any))
    p_m1_raw = float(np.sum(f_m1))
    p_m2_raw = float(np.sum(f_m2))
    if absorbed_mass > 1e-15:
        p_m1 = p_m1_raw / absorbed_mass
        p_m2 = p_m2_raw / absorbed_mass
    else:
        p_m1 = 0.0
        p_m2 = 0.0
    tail = float(surv[-1])

    t_mode_m1 = int(np.argmax(f_m1[1:]) + 1) if len(f_m1) > 1 else 0
    t_mode_m2 = int(np.argmax(f_m2[1:]) + 1) if len(f_m2) > 1 else 0
    hw_m1 = half_width_at_half_max(f_m1, t_mode_m1)
    hw_m2 = half_width_at_half_max(f_m2, t_mode_m2)
    denom = hw_m1 + hw_m2
    sep_mode_width = float(abs(t_mode_m2 - t_mode_m1) / denom) if denom > 0 else 0.0

    tmp = TTCaseResult(
        spec=spec,
        steps=len(f_any) - 1,
        t_peak1=tp1,
        t_peak2=tp2,
        t_valley=tv,
        peak_ratio=peak_ratio,
        valley_over_max=valley_over_max,
        p_m1=p_m1,
        p_m2=p_m2,
        t_mode_m1=t_mode_m1,
        t_mode_m2=t_mode_m2,
        hw_m1=hw_m1,
        hw_m2=hw_m2,
        sep_mode_width=sep_mode_width,
        absorbed_mass=absorbed_mass,
        survival_tail=tail,
        phase=0,
    )
    tmp.phase = classify_phase_two_target(tmp)
    return tmp


def summarize_one_target(
    spec: OTCaseSpec,
    f: np.ndarray,
    surv: np.ndarray,
) -> OTCaseResult:
    tp1, tp2 = find_two_peaks(f)
    tv = None
    valley_over_max = None
    peak_balance = None
    sep_peaks = 0.0
    f_s = smooth_series_display(f.astype(np.float64), window=7)

    if tp1 is not None and tp2 is not None and tp1 + 1 < tp2:
        hp1 = float(f_s[tp1])
        hp2 = float(f_s[tp2])
        window = f_s[tp1 : tp2 + 1]
        k = int(np.argmin(window))
        tv = tp1 + k
        hv = float(f_s[tv])
        if max(hp1, hp2) > 0:
            valley_over_max = float(hv / max(hp1, hp2))
            peak_balance = float(min(hp1, hp2) / max(hp1, hp2))
        hw1 = half_width_at_half_max(f, tp1)
        hw2 = half_width_at_half_max(f, tp2)
        denom = hw1 + hw2
        if denom > 0:
            sep_peaks = float(abs(tp2 - tp1) / denom)

    absorbed_mass = float(np.sum(f))
    tail = float(surv[-1])

    tmp = OTCaseResult(
        spec=spec,
        steps=len(f) - 1,
        t_peak1=tp1,
        t_peak2=tp2,
        t_valley=tv,
        valley_over_max=valley_over_max,
        peak_balance=peak_balance,
        sep_peaks=sep_peaks,
        absorbed_mass=absorbed_mass,
        survival_tail=tail,
        phase=0,
    )
    tmp.phase = classify_phase_one_target(tmp)
    return tmp


def choose_heat_times(tp1: int | None, tv: int | None, tp2: int | None) -> List[int]:
    if tp1 is not None and tp2 is not None and tv is not None:
        p1 = int(tp1)
        p2 = int(tp2)
        pv = int(tv)
        gap = max(1, p2 - p1)
        if gap < 30:
            t_a = max(5, p1)
            t_b = max(t_a + 1, p1 + gap // 2)
            t_c = max(t_b + 1, p2 + max(4, gap // 3))
        else:
            t_a = max(5, p1 + max(6, gap // 6))
            t_b = max(t_a + 1, pv)
            t_c = max(t_b + 1, p2)
        return [t_a, t_b, t_c]
    return [50, 120, 260]


def smooth_series_display(y: np.ndarray, window: int = 5) -> np.ndarray:
    w = int(max(1, window))
    if w <= 1 or y.size < w:
        return y.astype(np.float64, copy=True)
    if w % 2 == 0:
        w += 1
    pad = w // 2
    ypad = np.pad(y.astype(np.float64), (pad, pad), mode="edge")
    kernel = np.ones(w, dtype=np.float64) / float(w)
    return np.convolve(ypad, kernel, mode="valid")


def suggest_fpt_xmax(n_points: int, t_peak2: int | None) -> int:
    xmax = max(1, int(n_points) - 1)
    if t_peak2 is None:
        return xmax
    tp2 = int(t_peak2)
    if tp2 <= 120:
        return min(xmax, max(140, int(tp2 * 4)))
    # Keep enough right-side margin so a late second peak is not visually cramped.
    return min(xmax, max(420, int(tp2 * 1.5), int(tp2 + 180)))


def suggest_fpt_xmax_grid(n_points: int, t_peak1: int | None, t_peak2: int | None) -> int:
    """Tighter panel-range suggestion for FPT grids."""
    xmax = max(1, int(n_points) - 1)
    if t_peak2 is not None:
        tp2 = int(t_peak2)
        return min(xmax, max(240, int(tp2 * 1.25), int(tp2 + 120)))
    if t_peak1 is not None:
        tp1 = int(t_peak1)
        return min(xmax, max(180, int(tp1 * 4)))
    return min(xmax, 480)


def suggest_ot_fpt_xmax(
    n_points: int,
    *,
    f_total: np.ndarray,
    t_peak2: int | None,
    tight: bool = False,
) -> int:
    """Readable x-range for one-target FPT/hazard plots.

    If a second peak exists, keep enough right margin around it.
    Otherwise, cap the tail using the dominant-mode timescale so
    the first lobe is still visible (instead of flattening into a spike).
    """
    xmax = max(1, int(n_points) - 1)
    if t_peak2 is not None:
        tp2 = int(t_peak2)
        if bool(tight):
            return min(xmax, max(320, int(tp2 * 1.22), int(tp2 + 120)))
        return min(xmax, max(420, int(tp2 * 1.32), int(tp2 + 180)))

    mode = int(np.argmax(f_total[1:]) + 1) if len(f_total) > 1 else 1
    if bool(tight):
        return min(xmax, max(380, int(mode * 4.2), int(mode + 280)))
    return min(xmax, max(520, int(mode * 5.2), int(mode + 360)))


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


def _draw_path_arrows(ax: plt.Axes, path: Sequence[Coord], *, start_idx: int, color: str) -> None:
    i0 = max(0, int(start_idx))
    for i in range(i0, len(path) - 1):
        a = path[i]
        b = path[i + 1]
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=1.6, alpha=0.90, zorder=6)

    step = 4
    for i in range(i0, len(path) - 1, step):
        a = path[i]
        b = path[min(i + 1, len(path) - 1)]
        ax.annotate(
            "",
            xy=(b[0], b[1]),
            xytext=(a[0], a[1]),
            arrowprops=dict(arrowstyle="->", lw=1.2, color=color, shrinkA=6, shrinkB=6),
            zorder=8,
        )


def _draw_rectangle_background(ax: plt.Axes, *, Lx: int, Wy: int) -> None:
    base = np.zeros((Wy, Lx), dtype=np.float64)
    ax.imshow(
        base,
        origin="lower",
        cmap=plt.matplotlib.colors.ListedColormap([C_BG]),
        vmin=0.0,
        vmax=1.0,
        interpolation="nearest",
    )


def _draw_lattice_grid(ax: plt.Axes, *, Lx: int, Wy: int, major_step: int = 5) -> None:
    """Draw per-cell lattice lines, plus a coarser reference grid."""
    # Fine cell grid: makes each lattice cell boundary visible.
    x_fine = np.arange(-0.5, float(Lx) + 0.5, 1.0)
    y_fine = np.arange(-0.5, float(Wy) + 0.5, 1.0)
    ax.vlines(x_fine, -0.5, Wy - 0.5, colors=C_GRID, linewidth=0.34, alpha=0.52, zorder=4)
    ax.hlines(y_fine, -0.5, Lx - 0.5, colors=C_GRID, linewidth=0.34, alpha=0.52, zorder=4)

    # Coarse grid every k cells: helps quickly estimate distances on wide panels.
    step = max(1, int(major_step))
    x_major = np.arange(-0.5, float(Lx) + 0.5, float(step))
    y_major = np.arange(-0.5, float(Wy) + 0.5, float(step))
    ax.vlines(x_major, -0.5, Wy - 0.5, colors=C_GRID_MAJOR, linewidth=0.78, alpha=0.70, zorder=4)
    ax.hlines(y_major, -0.5, Lx - 0.5, colors=C_GRID_MAJOR, linewidth=0.78, alpha=0.70, zorder=4)


def _draw_environment_tt(
    ax: plt.Axes,
    *,
    Lx: int,
    Wy: int,
    fast_cells: set[Coord],
    slow_cells: set[Coord],
    start: Coord,
    m1: Coord,
    m2: Coord,
    fast_path: Sequence[Coord],
    slow_path: Sequence[Coord],
    fast_skip: int,
    slow_skip: int,
    title: str,
    draw_paths: bool = True,
    draw_turns: bool = True,
    arrow_map: Dict[Coord, str] | None = None,
    arrow_stride: int = 3,
    equal_aspect: bool = True,
) -> None:
    _draw_rectangle_background(ax, Lx=Lx, Wy=Wy)

    for x, y in sorted(fast_cells):
        ax.add_patch(
            Rectangle((x - 0.5, y - 0.5), 1.0, 1.0, facecolor=C_FAST, edgecolor="none", alpha=0.88, zorder=2)
        )
    for x, y in sorted(slow_cells):
        face = C_OVERLAP if (x, y) in fast_cells else C_SLOW
        ax.add_patch(
            Rectangle((x - 0.5, y - 0.5), 1.0, 1.0, facecolor=face, edgecolor="none", alpha=0.82, zorder=3)
        )

    if arrow_map:
        stride = max(1, int(arrow_stride))
        for (x, y), d in arrow_map.items():
            # Subsample to keep the figure readable for thick bands.
            if ((x + 2 * y) % stride) != 0:
                continue
            v = DIR_VEC.get(d)
            if v is None:
                continue
            dx, dy = v
            x0 = x - 0.30 * dx
            y0 = y - 0.30 * dy
            x1 = x + 0.30 * dx
            y1 = y + 0.30 * dy
            ax.annotate(
                "",
                xy=(x1, y1),
                xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", lw=1.15, color=C_ARROW, alpha=0.92, shrinkA=0, shrinkB=0),
                zorder=7,
            )
    elif draw_paths:
        _draw_path_arrows(ax, fast_path, start_idx=fast_skip, color=C_ARROW)
        _draw_path_arrows(ax, slow_path, start_idx=slow_skip, color=C_ARROW)

    if draw_turns:
        turns = _path_turn_points(slow_path)
        if turns:
            ax.scatter(
                [p[0] for p in turns],
                [p[1] for p in turns],
                c="#111111",
                s=24,
                marker="o",
                edgecolors="white",
                linewidths=0.5,
                zorder=9,
                label="turn",
            )

    ax.scatter([start[0]], [start[1]], c=C_START, s=58, marker=MARK_START, label="start", zorder=10)
    ax.scatter([m1[0]], [m1[1]], c=C_M1, s=72, marker=MARK_M1, label="m1", zorder=10)
    ax.scatter([m2[0]], [m2[1]], c=C_M2, s=72, marker=MARK_M2, label="m2", zorder=10)

    # Keep endpoint labels inside panel bounds to avoid clipping near borders.
    def _text_x(x: int) -> float:
        return (x - 1.35) if int(x) >= int(Lx - 3) else (x + 0.8)

    ax.text(_text_x(start[0]), start[1] + 0.8, "start", color=C_TEXT_START, fontsize=8, weight="bold", zorder=11)
    ax.text(_text_x(m1[0]), m1[1] + 0.8, "m1", color=C_TEXT_M1, fontsize=8, weight="bold", zorder=11)
    ax.text(_text_x(m2[0]), m2[1] + 0.8, "m2", color=C_TEXT_M2, fontsize=8, weight="bold", zorder=11)

    ax.set_xlim(-0.5, Lx - 0.5)
    ax.set_ylim(-0.5, Wy - 0.5)
    ax.set_aspect("equal" if bool(equal_aspect) else "auto")

    _draw_lattice_grid(ax, Lx=Lx, Wy=Wy, major_step=5)
    ax.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)

    for s in ax.spines.values():
        s.set_linewidth(2.2)
        s.set_color("black")
    ax.set_title(title, fontsize=10, pad=6)


def _draw_heatmap_panel(
    ax: plt.Axes,
    *,
    arr: np.ndarray,
    t: int,
    marks: Sequence[Tuple[Coord, str, str]],
    vmax: float,
    equal_aspect: bool = True,
) -> None:
    norm = plt.matplotlib.colors.PowerNorm(gamma=0.55, vmin=0.0, vmax=vmax)
    im = ax.imshow(
        arr,
        origin="lower",
        cmap="plasma",
        interpolation="nearest",
        norm=norm,
        aspect=("equal" if bool(equal_aspect) else "auto"),
    )
    # Keep lattice cells readable on occupancy heatmaps too.
    Wy_h, Lx_h = int(arr.shape[0]), int(arr.shape[1])
    x_fine = np.arange(-0.5, float(Lx_h) + 0.5, 1.0)
    y_fine = np.arange(-0.5, float(Wy_h) + 0.5, 1.0)
    ax.vlines(x_fine, -0.5, Wy_h - 0.5, colors="white", linewidth=0.22, alpha=0.20, zorder=4)
    ax.hlines(y_fine, -0.5, Lx_h - 0.5, colors="white", linewidth=0.22, alpha=0.20, zorder=4)
    x_major = np.arange(-0.5, float(Lx_h) + 0.5, 5.0)
    y_major = np.arange(-0.5, float(Wy_h) + 0.5, 5.0)
    ax.vlines(x_major, -0.5, Wy_h - 0.5, colors="white", linewidth=0.42, alpha=0.33, zorder=4)
    ax.hlines(y_major, -0.5, Lx_h - 0.5, colors="white", linewidth=0.42, alpha=0.33, zorder=4)
    for pos, color, marker in marks:
        ax.scatter([pos[0]], [pos[1]], c=color, s=52, marker=marker, edgecolors="white", linewidths=0.45, zorder=5)
    ax.text(
        0.90,
        0.06,
        f"$t={t}$",
        color="white",
        fontsize=13,
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
    # attach to parent for colorbar
    ax._rect_im = im  # type: ignore[attr-defined]


def plot_tt_env_heatmaps(
    out_path: Path,
    *,
    Lx: int,
    Wy: int,
    start: Coord,
    m1: Coord,
    m2: Coord,
    fast_cells: set[Coord],
    slow_cells: set[Coord],
    fast_path: Sequence[Coord],
    slow_path: Sequence[Coord],
    fast_skip: int,
    slow_skip: int,
    case_title: str,
    snapshots: Dict[int, np.ndarray],
    heat_times: Sequence[int],
    arrow_map: Dict[Coord, str] | None = None,
) -> None:
    # Keep geometry-preserving (non-stretched) panels and reserve enough height
    # so thin rectangles are still readable.
    aspect = float(Lx) / float(max(1, Wy))
    fig_h = float(np.clip(2.15 + 9.0 / max(1e-9, aspect), 2.05, 4.00))
    fig = plt.figure(figsize=(13.4, fig_h), constrained_layout=True)
    gs = fig.add_gridspec(1, 5, width_ratios=[1.18, 1, 1, 1, 0.08], wspace=0.05)
    ax0 = fig.add_subplot(gs[0, 0])
    _draw_environment_tt(
        ax0,
        Lx=Lx,
        Wy=Wy,
        fast_cells=fast_cells,
        slow_cells=slow_cells,
        start=start,
        m1=m1,
        m2=m2,
        fast_path=fast_path,
        slow_path=slow_path,
        fast_skip=fast_skip,
        slow_skip=slow_skip,
        title="environment",
        draw_paths=False,
        draw_turns=False,
        arrow_map=arrow_map,
        equal_aspect=True,
    )

    vmax = 0.0
    for t in heat_times:
        if int(t) in snapshots:
            vmax = max(vmax, float(np.max(snapshots[int(t)])))
    vmax = max(vmax, 1e-12)

    marks = [(m1, C_M1, MARK_M1), (m2, C_M2, MARK_M2)]
    heat_axes: List[plt.Axes] = []
    for k, t in enumerate(heat_times):
        ax = fig.add_subplot(gs[0, k + 1])
        arr = snapshots.get(int(t))
        if arr is None:
            arr = np.zeros((Wy, Lx), dtype=np.float64)
        _draw_heatmap_panel(ax, arr=arr, t=int(t), marks=marks, vmax=vmax, equal_aspect=True)
        heat_axes.append(ax)

    # Shared colorbar on a dedicated axis to avoid overlapping panel labels.
    im = getattr(heat_axes[-1], "_rect_im")
    cax = fig.add_subplot(gs[0, 4])
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label(r"$P(X_t=n\mid T>t)$", fontsize=10)
    fig.suptitle(case_title, fontsize=12, y=0.98)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def _draw_fpt_two_target(
    ax: plt.Axes,
    f_any: np.ndarray,
    f_m1: np.ndarray,
    f_m2: np.ndarray,
    title: str,
    *,
    res: TTCaseResult | None = None,
    normalize: bool = False,
    yscale: str = "linear",
    show_legend: bool = True,
    show_second_peak_inset: bool = False,
    show_raw_trace: bool = True,
    smooth_window: int = 5,
) -> None:
    t = np.arange(len(f_any))
    scale = float(np.max(f_any)) if bool(normalize) else 1.0
    if scale <= 0.0:
        scale = 1.0
    fa = f_any / scale
    f1 = f_m1 / scale
    f2 = f_m2 / scale

    # For log plots we need to avoid zeros; keep an epsilon below the visible floor.
    yscale = str(yscale).lower()
    if yscale in ("log", "symlog"):
        eps = 1e-8 if bool(normalize) else 1e-15
        fa_p = np.maximum(fa, eps)
        f1_p = np.maximum(f1, eps)
        f2_p = np.maximum(f2, eps)
    else:
        fa_p, f1_p, f2_p = fa, f1, f2

    # Display smoothing is visual-only; metrics/labels are still from exact series.
    win = max(3, int(smooth_window))
    fa_s = smooth_series_display(fa_p, window=win)
    f1_s = smooth_series_display(f1_p, window=win)
    f2_s = smooth_series_display(f2_p, window=win)

    if bool(show_raw_trace):
        ax.plot(t, fa_p, color=C_ANY, lw=0.7, alpha=0.16)
        ax.plot(t, f1_p, color=C_SPLIT1, lw=0.6, alpha=0.12)
        ax.plot(t, f2_p, color=C_SPLIT2, lw=0.6, alpha=0.12)
    ax.plot(t, fa_s, color=C_ANY, lw=1.9, label="F_any")
    ax.plot(t, f1_s, color=C_SPLIT1, lw=1.25, alpha=0.92, label="F_m1")
    ax.plot(t, f2_s, color=C_SPLIT2, lw=1.25, alpha=0.92, label="F_m2")

    if yscale == "log":
        ax.set_yscale("log")
    elif yscale == "symlog":
        ax.set_yscale("symlog", linthresh=1e-6)

    ax.set_xlabel("t")
    ax.set_ylabel("F(t) / max(F)" if bool(normalize) else "probability")
    ax.set_title(title, fontsize=9)
    ax.grid(alpha=0.25)

    if res is not None:
        if res.t_peak1 is not None and 0 <= int(res.t_peak1) < len(f_any):
            ax.axvline(int(res.t_peak1), color="#444444", lw=1.0, ls="--", alpha=0.55)
        if res.t_peak2 is not None and 0 <= int(res.t_peak2) < len(f_any):
            ax.axvline(int(res.t_peak2), color="#444444", lw=1.0, ls="--", alpha=0.55)
        if res.t_valley is not None and 0 <= int(res.t_valley) < len(f_any):
            ax.axvline(int(res.t_valley), color="#999999", lw=1.0, ls=":", alpha=0.70)
        if res.t_peak1 is not None and res.t_peak2 is not None:
            p1 = int(res.t_peak1)
            p2 = int(res.t_peak2)
            if 0 <= p1 < len(f_any) and 0 <= p2 < len(f_any):
                # Use smoothed heights for markers so peak dots align with displayed curve.
                ax.scatter([p1, p2], [fa_s[p1], fa_s[p2]], c=C_ANY, s=18, zorder=3)

    if show_legend:
        ax.legend(loc="upper right", fontsize=8)

    if (
        bool(show_second_peak_inset)
        and res is not None
        and res.t_peak2 is not None
        and 0 <= int(res.t_peak2) < len(f_any)
        and yscale == "linear"
    ):
        tp2 = int(res.t_peak2)
        left = max(0, tp2 - max(60, int(0.30 * max(tp2, 1))))
        right = min(len(f_any) - 1, tp2 + max(120, int(0.45 * max(tp2, 1))))
        if right - left >= 20:
            ains = inset_axes(ax, width="41%", height="40%", loc="upper right", borderpad=1.0)
            fa_z = smooth_series_display(fa, window=7)
            f1_z = smooth_series_display(f1, window=7)
            f2_z = smooth_series_display(f2, window=7)
            ains.plot(t[left : right + 1], fa[left : right + 1], color=C_ANY, lw=0.6, alpha=0.12)
            ains.plot(t[left : right + 1], f1[left : right + 1], color=C_SPLIT1, lw=0.55, alpha=0.10)
            ains.plot(t[left : right + 1], f2[left : right + 1], color=C_SPLIT2, lw=0.55, alpha=0.10)
            ains.plot(t[left : right + 1], fa_z[left : right + 1], color=C_ANY, lw=1.6)
            ains.plot(t[left : right + 1], f1_z[left : right + 1], color=C_SPLIT1, lw=1.0, alpha=0.85)
            ains.plot(t[left : right + 1], f2_z[left : right + 1], color=C_SPLIT2, lw=1.0, alpha=0.85)
            ains.axvline(tp2, color="#444444", lw=0.9, ls="--", alpha=0.70)
            yseg = fa_z[left : right + 1]
            y_min = float(np.min(yseg))
            y_max = float(np.max(yseg))
            pad = max(0.01, 0.15 * max(y_max - y_min, 1e-6))
            ains.set_xlim(left, right)
            ains.set_ylim(max(0.0, y_min - pad), min(1.05 if bool(normalize) else 1.0, y_max + pad))
            ains.set_title("2nd-peak zoom", fontsize=7)
            ains.grid(alpha=0.20)
            ains.tick_params(labelsize=7)


def plot_tt_fpt(
    out_path: Path,
    *,
    f_any: np.ndarray,
    f_m1: np.ndarray,
    f_m2: np.ndarray,
    res: TTCaseResult,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9), gridspec_kw=dict(wspace=0.20))
    title = (
        f"{res.spec.case_id}: Wy={res.spec.Wy}, x0={res.spec.x_start}, "
        f"P(m1)={res.p_m1:.3f}, P(m2)={res.p_m2:.3f}, sep={res.sep_mode_width:.2f}, phase={res.phase}"
    )
    ax0, ax1 = axes
    _draw_fpt_two_target(
        ax0,
        f_any,
        f_m1,
        f_m2,
        title + " (linear)",
        res=res,
        normalize=True,
        yscale="linear",
        show_legend=True,
        show_second_peak_inset=True,
    )
    _draw_fpt_two_target(ax1, f_any, f_m1, f_m2, title + " (log)", res=res, normalize=True, yscale="log", show_legend=False)

    # Auto x-lim focusing on peaks if present (use the same xlim on both panels).
    xmax = suggest_fpt_xmax(len(f_any), res.t_peak2)
    for ax in axes:
        ax.set_xlim(0, xmax)
        if ax.get_yscale() == "linear":
            ax.set_ylim(0.0, 1.05)
        else:
            ax.set_ylim(1e-6, 1.2)
    fig.subplots_adjust(left=0.06, right=0.985, bottom=0.12, top=0.90, wspace=0.22)
    fig.savefig(out_path)
    plt.close(fig)


def _hazard_components_two_target(f_any: np.ndarray, f_m1: np.ndarray, f_m2: np.ndarray, surv: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if len(f_any) < 2:
        z = np.zeros(0, dtype=np.float64)
        return z, z, z, z
    t = np.arange(1, len(f_any), dtype=np.int64)
    s_prev = np.maximum(surv[:-1], 1e-15)
    h_any = f_any[1:] / s_prev
    h1 = f_m1[1:] / s_prev
    h2 = f_m2[1:] / s_prev
    return t, h_any, h1, h2


def plot_tt_hazard_grid(
    out_path: Path,
    *,
    reps: Sequence[TTCaseResult],
    series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
) -> None:
    if not reps:
        return
    n = min(6, len(reps))
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.8 * ncols, 3.2 * nrows))
    axes_list = axes.flatten() if hasattr(axes, "flatten") else [axes]
    for ax in axes_list[n:]:
        ax.axis("off")
    for ax, r in zip(axes_list, reps[:n]):
        f_any, f_m1, f_m2, surv = series_map[r.spec.case_id]
        t, h_any, h1, h2 = _hazard_components_two_target(f_any, f_m1, f_m2, surv)
        h_any_s = smooth_series_display(h_any, window=7)
        h1_s = smooth_series_display(h1, window=7)
        h2_s = smooth_series_display(h2, window=7)
        ax.plot(t, h_any, color=C_ANY, lw=0.65, alpha=0.10)
        ax.plot(t, h1, color=C_SPLIT1, lw=0.55, alpha=0.08)
        ax.plot(t, h2, color=C_SPLIT2, lw=0.55, alpha=0.08)
        ax.plot(t, h_any_s, color=C_ANY, lw=1.6, label="h_any")
        ax.plot(t, h1_s, color=C_SPLIT1, lw=1.2, label="h_m1")
        ax.plot(t, h2_s, color=C_SPLIT2, lw=1.2, label="h_m2")
        if r.t_valley is not None and r.t_valley > 0 and r.t_valley < len(h_any):
            ax.axvline(r.t_valley, color="#444444", lw=1.0, ls="--", alpha=0.65)
        xmax = suggest_fpt_xmax(len(t) + 1, r.t_peak2)
        xmax = min(len(t), xmax)
        ax.set_xlim(1, xmax)
        ax.set_xlabel("t")
        ax.set_ylabel("hazard")
        ax.set_title(f"{r.spec.case_id}: hazard decomposition", fontsize=9)
        ax.grid(alpha=0.25)
    handles, labels = axes_list[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path)
    plt.close(fig)


def plot_tt_rep_geometry_grid(
    out_path: Path,
    *,
    Lx: int,
    layouts: Dict[str, dict],
    reps: Sequence[TTCaseResult],
) -> None:
    if not reps:
        return
    n = min(6, len(reps))
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.8 * ncols, 3.2 * nrows))
    axes_list = axes.flatten() if hasattr(axes, "flatten") else [axes]
    for ax in axes_list[n:]:
        ax.axis("off")
    for ax, r in zip(axes_list, reps[:n]):
        lay = layouts[r.spec.case_id]
        _draw_environment_tt(
            ax,
            Lx=Lx,
            Wy=int(lay["Wy"]),
            fast_cells=lay["fast_cells"],
            slow_cells=lay["slow_cells"],
            start=lay["start"],
            m1=lay["m1"],
            m2=lay["m2"],
            fast_path=lay["fast_path"],
            slow_path=lay["slow_path"],
            fast_skip=int(lay["fast_skip"]),
            slow_skip=int(lay["slow_skip"]),
            title=f"{r.spec.case_id} (phase={r.phase})",
            draw_paths=False,
            draw_turns=False,
            arrow_map=lay.get("arrow_map"),
        )
    fig.subplots_adjust(left=0.05, right=0.995, bottom=0.09, top=0.94, wspace=0.20, hspace=0.34)
    fig.savefig(out_path)
    plt.close(fig)


def plot_tt_rep_fpt_grid(
    out_path: Path,
    *,
    reps: Sequence[TTCaseResult],
    series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
) -> None:
    if not reps:
        return
    n = min(6, len(reps))
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.8 * ncols, 3.2 * nrows))
    axes_list = axes.flatten() if hasattr(axes, "flatten") else [axes]
    for ax in axes_list[n:]:
        ax.axis("off")
    for ax, r in zip(axes_list, reps[:n]):
        f_any, f_m1, f_m2, _ = series_map[r.spec.case_id]
        title = f"{r.spec.case_id}: phase={r.phase}, P2={r.p_m2:.2f}, splitSep={r.sep_mode_width:.2f}"
        _draw_fpt_two_target(
            ax,
            f_any,
            f_m1,
            f_m2,
            title,
            res=r,
            normalize=True,
            yscale="linear",
            show_legend=False,
            show_second_peak_inset=True,
            show_raw_trace=False,
            smooth_window=7,
        )
        xmax = suggest_fpt_xmax_grid(len(f_any), r.t_peak1, r.t_peak2)
        ax.set_xlim(0, xmax)
        ax.set_ylim(0.0, 1.05)
        if r.peak_ratio is not None and r.valley_over_max is not None:
            ax.text(
                0.03,
                0.96,
                f"pmin/pmax={r.peak_ratio:.2f}, valley={r.valley_over_max:.2f}",
                transform=ax.transAxes,
                fontsize=7.8,
                ha="left",
                va="top",
                color="#222222",
                bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="none", alpha=0.72),
            )
    fig.subplots_adjust(left=0.05, right=0.995, bottom=0.09, top=0.94, wspace=0.20, hspace=0.34)
    fig.savefig(out_path)
    plt.close(fig)


def plot_symbol_legend_panel(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.4, 4.6))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    y0 = 0.85
    dy = 0.105

    def row(y: float, label: str, desc: str) -> None:
        ax.text(0.08, y, label, ha="left", va="center", fontsize=10, color="black")
        ax.text(0.34, y, desc, ha="left", va="center", fontsize=10, color="black")

    # Corridor fills
    ax.add_patch(Rectangle((0.02, y0 - 0.03), 0.045, 0.06, facecolor=C_FAST, edgecolor="black", lw=0.6))
    row(y0, "Fast region", "biased fast corridor cells")
    y0 -= dy
    ax.add_patch(Rectangle((0.02, y0 - 0.03), 0.045, 0.06, facecolor=C_SLOW, edgecolor="black", lw=0.6))
    row(y0, "Slow region", "biased slow corridor / outer detour region")
    y0 -= dy
    ax.add_patch(Rectangle((0.02, y0 - 0.03), 0.045, 0.06, facecolor=C_OVERLAP, edgecolor="black", lw=0.6))
    row(y0, "Overlap", "overlap between fast and slow biased sets")
    y0 -= dy

    # Markers
    ax.scatter([0.044], [y0], s=58, marker=MARK_START, c=C_START, edgecolors="black", linewidths=0.45)
    row(y0, "Start", "starting site")
    y0 -= dy
    ax.scatter([0.044], [y0], s=74, marker=MARK_M1, c=C_M1, edgecolors="black", linewidths=0.45)
    row(y0, "Target m1", "left target (two-target part)")
    y0 -= dy
    ax.scatter([0.044], [y0], s=74, marker=MARK_M2, c=C_M2, edgecolors="black", linewidths=0.45)
    row(y0, "Target m2", "right target (two-target part)")
    y0 -= dy

    # Arrows and walls
    ax.annotate("", xy=(0.055, y0), xytext=(0.03, y0), arrowprops=dict(arrowstyle="->", lw=1.6, color=C_ARROW))
    row(y0, "Local bias", "shift a fraction of stay probability to arrow direction")
    y0 -= dy
    ax.plot([0.02, 0.065], [y0, y0], color=C_WALL, lw=2.2)
    row(y0, "Reflecting wall", "internal reflecting barrier (corridor walls)")
    y0 -= dy

    # Curves and phase
    ax.plot([0.02, 0.065], [y0, y0], color=C_ANY, lw=1.8)
    ax.plot([0.02, 0.065], [y0 - 0.02, y0 - 0.02], color=C_SPLIT1, lw=1.3)
    ax.plot([0.02, 0.065], [y0 - 0.04, y0 - 0.04], color=C_SPLIT2, lw=1.3)
    row(y0 - 0.02, "FPT curves", "black: total; blue/orange: channel/splitting components")
    y0 -= dy

    ax.add_patch(Rectangle((0.02, y0 - 0.03), 0.015, 0.06, facecolor=C_PHASE0, edgecolor="black", lw=0.6))
    ax.add_patch(Rectangle((0.04, y0 - 0.03), 0.015, 0.06, facecolor=C_PHASE1, edgecolor="black", lw=0.6))
    ax.add_patch(Rectangle((0.06, y0 - 0.03), 0.015, 0.06, facecolor=C_PHASE2, edgecolor="black", lw=0.6))
    row(y0, "Phase 0/1/2", "0=single; 1=weak double; 2=clear double")

    fig.subplots_adjust(left=0.06, right=0.995, bottom=0.13, top=0.93, wspace=0.26)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def save_csv(path: Path, header: Sequence[str], rows: Iterable[Sequence[Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(list(header))
        for r in rows:
            w.writerow(list(r))


def _tex_escape(s: str) -> str:
    return (
        str(s)
        .replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("&", "\\&")
        .replace("#", "\\#")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def _opt_float(v: Any, default: float) -> float:
    """Convert optional numeric-like value to float without bool-coercion traps."""
    if v is None:
        return float(default)
    return float(v)


def plot_phase_map(
    out_path: Path,
    *,
    phase: np.ndarray,
    x_ticks: Sequence[int],
    y_ticks: Sequence[int],
    xlabel: str,
    ylabel: str,
    title: str,
) -> None:
    cmap = plt.matplotlib.colors.ListedColormap([C_PHASE0, C_PHASE1, C_PHASE2])
    fig, ax = plt.subplots(figsize=(8.0, 4.9))
    im = ax.imshow(phase, origin="lower", cmap=cmap, vmin=-0.5, vmax=2.5, aspect="auto")
    ax.set_xticks(range(len(x_ticks)))
    ax.set_xticklabels([str(v) for v in x_ticks])
    ax.set_yticks(range(len(y_ticks)))
    ax.set_yticklabels([str(v) for v in y_ticks])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    for i in range(phase.shape[0]):
        for j in range(phase.shape[1]):
            ax.text(j, i, f"{int(phase[i, j])}", ha="center", va="center", fontsize=8, color="black")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cbar.set_ticks([0, 1, 2])
    # Keep labels short to avoid clipping in narrow exports.
    cbar.set_ticklabels(["single", "weak", "clear"])
    fig.subplots_adjust(left=0.07, right=0.965, bottom=0.16, top=0.90, wspace=0.28)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def plot_scalar_map(
    out_path: Path,
    *,
    arr: np.ndarray,
    x_ticks: Sequence[int],
    y_ticks: Sequence[int],
    xlabel: str,
    ylabel: str,
    title: str,
    cbar_label: str,
    cmap: str = "viridis",
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.9))
    im = ax.imshow(arr, origin="lower", cmap=cmap, aspect="auto")
    ax.set_xticks(range(len(x_ticks)))
    ax.set_xticklabels([str(v) for v in x_ticks])
    ax.set_yticks(range(len(y_ticks)))
    ax.set_yticklabels([str(v) for v in y_ticks])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cbar.set_label(cbar_label)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def build_tt_case_geometry(
    *,
    Lx: int,
    Wy: int,
    x_start: int,
    w_fast: int,
    w_slow: int,
    fast_skip: int,
    slow_skip: int,
    delta_fast: float,
    delta_slow: float,
    style: str = "straight",
) -> Tuple[Coord, Coord, Coord, List[Coord], List[Coord], Dict[Coord, Tuple[str, float]], Dict[Coord, str], set[Coord], set[Coord]]:
    if Wy < 5:
        raise ValueError("Wy must be >=5")
    y_mid = int((Wy - 1) // 2)
    start = (int(x_start), int(y_mid))
    m1 = (1, y_mid)
    m2 = (Lx - 2, y_mid)

    fast_nodes = [start, m1]
    if str(style).lower() in ("straight", "stream", "streams"):
        # Two straight one-cell-thick streams on the midline:
        #   - fast: westward to m1 (short distance),
        #   - slow: eastward to m2 (long distance).
        # With `fast_skip=slow_skip=1`, the start site itself can remain unbiased,
        # while the immediate neighbors carry opposite drifts.
        slow_nodes = [start, m2]
    elif str(style).lower() in ("detour", "polyline"):
        # Old-style long detour with turns (kept as an option).
        slow_nodes = [start, (x_start, Wy - 2), (Lx - 2, Wy - 2), m2]
    else:
        raise ValueError(f"unknown two-target style: {style}")
    fast_path = polyline_points(fast_nodes)
    slow_path = polyline_points(slow_nodes)

    fast_arrows, fast_cells = corridor_assignments(fast_path, width=w_fast, skip=fast_skip, Lx=Lx, Wy=Wy)
    slow_arrows, slow_cells = corridor_assignments(slow_path, width=w_slow, skip=slow_skip, Lx=Lx, Wy=Wy)

    # slow overrides fast in overlaps.
    arrow_map = dict(fast_arrows)
    arrow_map.update(slow_arrows)

    local_bias_map: Dict[Coord, Tuple[str, float]] = {c: (d, float(delta_fast)) for c, d in fast_arrows.items()}
    for c, d in slow_arrows.items():
        local_bias_map[c] = (d, float(delta_slow))

    return start, m1, m2, fast_path, slow_path, local_bias_map, arrow_map, fast_cells, slow_cells


def render_tt_scan_overview(rows: List[dict], out_path: Path) -> None:
    # Group by width.
    widths = sorted({int(r["Wy"]) for r in rows})
    lines: List[str] = []
    lines.append("\\begin{tabular}{rcccc}")
    lines.append("\\toprule")
    lines.append("$W_y$ & n(single) & n(weak) & n(clear) & best $\\min(p_1,p_2)$ \\\\")
    lines.append("\\midrule")
    for Wy in widths:
        group = [r for r in rows if int(r["Wy"]) == Wy]
        n0 = sum(int(r["phase"]) == 0 for r in group)
        n1 = sum(int(r["phase"]) == 1 for r in group)
        n2 = sum(int(r["phase"]) == 2 for r in group)
        # Show balance only for phase>=1 rows; otherwise this column can look
        # misleadingly high even when no double peak is detected.
        best_bal = None
        for r in group:
            if int(r["phase"]) < 1:
                continue
            bal = float(min(r["p_m1"], r["p_m2"]))
            best_bal = bal if best_bal is None else max(best_bal, bal)
        bal_txt = "-" if best_bal is None else f"{best_bal:.3f}"
        lines.append(f"{Wy} & {n0} & {n1} & {n2} & {bal_txt} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _contiguous_intervals(vals: Sequence[int], *, step: int = 1) -> List[Tuple[int, int]]:
    if not vals:
        return []
    a = sorted(int(v) for v in vals)
    step_i = max(1, int(step))
    out: List[Tuple[int, int]] = []
    s = a[0]
    e = a[0]
    for v in a[1:]:
        if int(v) == e + step_i:
            e = int(v)
        else:
            out.append((s, e))
            s = int(v)
            e = int(v)
    out.append((s, e))
    return out


def render_tt_critical_width_table(rows: List[dict], out_path: Path, *, branches: Sequence[int] = (8, 10, 12)) -> None:
    """Render branch-wise clear-double critical widths for selected x0 branches."""
    x_all = sorted({int(r["x_start"]) for r in rows})
    w_all = sorted({int(r["Wy"]) for r in rows})
    width_steps = [b - a for a, b in zip(w_all[:-1], w_all[1:]) if (b - a) > 0]
    scan_step = min(width_steps) if width_steps else 1

    lines: List[str] = []
    lines.append("\\begin{tabular}{rcccc}")
    lines.append("\\toprule")
    lines.append("$x_0$ & clear interval(s) & upper clear branch & first loss width & phase at loss \\\\")
    lines.append("\\midrule")
    for x0 in branches:
        if int(x0) not in x_all:
            lines.append(f"{x0} & - & - & - & - \\\\")
            continue
        branch_rows = [r for r in rows if int(r["x_start"]) == int(x0)]
        branch_ws = sorted({int(r["Wy"]) for r in branch_rows})
        branch_steps = [b - a for a, b in zip(branch_ws[:-1], branch_ws[1:]) if (b - a) > 0]
        branch_step = min(branch_steps) if branch_steps else scan_step
        w_max_scan = max(branch_ws) if branch_ws else 0

        clear_ws = sorted(int(r["Wy"]) for r in branch_rows if int(r["phase"]) == 2)
        if not clear_ws:
            lines.append(f"{x0} & - & - & - & - \\\\")
            continue
        intervals = _contiguous_intervals(clear_ws, step=branch_step)
        intervals_txt_parts: List[str] = []
        for a, b in intervals:
            if a == b:
                intervals_txt_parts.append(f"{a}")
            elif branch_step > 1:
                intervals_txt_parts.append(f"{a}-{b} (step={branch_step})")
            else:
                intervals_txt_parts.append(f"{a}-{b}")
        intervals_txt = ", ".join(intervals_txt_parts)
        up_a, up_b = intervals[-1]
        if up_a == up_b:
            upper_txt = f"{up_a}"
        elif branch_step > 1:
            upper_txt = f"{up_a}-{up_b} (step={branch_step})"
        else:
            upper_txt = f"{up_a}-{up_b}"
        loss_candidates = [w for w in branch_ws if int(w) > int(up_b)]
        if not loss_candidates:
            loss_txt = f">{w_max_scan}"
            phase_txt = "-"
        else:
            loss_w = int(loss_candidates[0])
            loss_txt = str(loss_w)
            phase_at_loss = [int(r["phase"]) for r in branch_rows if int(r["Wy"]) == int(loss_w)]
            phase_txt = str(phase_at_loss[0]) if phase_at_loss else "-"
        lines.append(f"{x0} & {intervals_txt} & {upper_txt} & {loss_txt} & {phase_txt} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def plot_tt_critical_vs_xstart(
    out_path: Path,
    *,
    rows: List[dict],
    branches: Sequence[int] | None = None,
) -> None:
    x_vals = sorted({int(r["x_start"]) for r in rows})
    if branches is not None:
        branch_set = {int(x) for x in branches}
        x_vals = [x for x in x_vals if x in branch_set]
    if not x_vals:
        return
    y_clear: List[float] = []
    y_double: List[float] = []
    for x0 in x_vals:
        clear_ws = [int(r["Wy"]) for r in rows if int(r["x_start"]) == int(x0) and int(r["phase"]) == 2]
        weak_or_clear = [int(r["Wy"]) for r in rows if int(r["x_start"]) == int(x0) and int(r["phase"]) >= 1]
        y_clear.append(float(max(clear_ws)) if clear_ws else np.nan)
        y_double.append(float(max(weak_or_clear)) if weak_or_clear else np.nan)

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(x_vals, y_clear, marker="o", lw=1.7, color="#1f77b4", label="max Wy (clear double, phase=2)")
    ax.plot(x_vals, y_double, marker="s", lw=1.4, color="#ff7f0e", label="max Wy (any double, phase>=1)")
    ax.set_xlabel(r"$x_0$")
    ax.set_ylabel(r"maximum width $W_y$")
    ax.set_title("Two-target branch-wise width limit for bimodality", fontsize=10)
    ax.grid(alpha=0.28)
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def pick_representatives_tt(rows: List[dict], *, max_total: int = 6) -> List[TTCaseSpec]:
    """Pick two-target representatives with emphasis on clear double peaks.

    The representative panel should support the report conclusions with
    clear-double cases only, emphasizing robust bimodality on straight streams.
    """
    clear_rows = [r for r in rows if int(r["phase"]) == 2]
    if not clear_rows:
        return []

    # Strong-visibility pool: ensure panels show explicit two-peak structure.
    def is_strong(r: dict) -> bool:
        valley = float(r["valley_over_max"]) if r.get("valley_over_max") is not None else 1.0
        pr = _opt_float(r.get("peak_ratio"), 0.0)
        prom = max(0.0, pr - valley)
        t2 = float(r["t_peak2"]) if r.get("t_peak2") is not None else 0.0
        return (
            float(r["sep_mode_width"]) >= 1.15
            and valley <= 0.24
            and pr >= 0.10
            and prom >= 0.01
            and float(r["p_m2"]) >= 0.32
            and t2 >= 200.0
        )

    strong_rows = [r for r in clear_rows if is_strong(r)]
    pool = strong_rows if len(strong_rows) >= int(max_total) else clear_rows

    def quality_key(r: dict) -> Tuple[float, float, float, float, float]:
        valley = _opt_float(r.get("valley_over_max"), 9.0)
        pr = _opt_float(r.get("peak_ratio"), 0.0)
        prom = max(0.0, pr - valley)
        bal = float(min(float(r["p_m1"]), float(r["p_m2"])))
        sep = float(r["sep_mode_width"])
        return (prom, pr, bal, sep, -valley)

    def to_spec(r: dict) -> TTCaseSpec:
        return TTCaseSpec(
            Wy=int(r["Wy"]),
            x_start=int(r["x_start"]),
            w_fast=int(r["w_fast"]),
            w_slow=int(r["w_slow"]),
            fast_skip=int(r["fast_skip"]),
            slow_skip=int(r["slow_skip"]),
            delta_fast=float(r["delta_fast"]),
            delta_slow=float(r["delta_slow"]),
        )

    reps: List[TTCaseSpec] = []
    seen: set[str] = set()

    # First ensure key branches (if available) are represented by their best-quality cases.
    for x0 in (8, 10, 12):
        if len(reps) >= int(max_total):
            break
        cand = [r for r in pool if int(r["x_start"]) == int(x0)]
        if not cand:
            continue
        best = max(cand, key=quality_key)
        s = to_spec(best)
        if s.case_id in seen:
            continue
        reps.append(s)
        seen.add(s.case_id)

    if len(reps) < int(max_total):
        tail = [r for r in pool if to_spec(r).case_id not in seen]
        tail.sort(
            key=lambda r: (
                -quality_key(r)[0],
                -quality_key(r)[1],
                -quality_key(r)[2],
                -quality_key(r)[3],
                quality_key(r)[4],
                -_opt_float(r.get("t_peak2"), 0.0),
            )
        )
        for r in tail:
            if len(reps) >= int(max_total):
                break
            s = to_spec(r)
            if s.case_id in seen:
                continue
            reps.append(s)
            seen.add(s.case_id)
    return reps


def render_tt_representative_table(results: Sequence[TTCaseResult], out_path: Path) -> None:
    lines: List[str] = []
    lines.append("\\begin{tabular}{lrrrrrr}")
    lines.append("\\toprule")
    lines.append("ID & $W_y$ & $x_0$ & phase & $P(m_1)$ & $P(m_2)$ & sep-score \\\\")
    lines.append("\\midrule")
    for r in results:
        lines.append(
            f"{_tex_escape(r.spec.case_id)} & {r.spec.Wy} & {r.spec.x_start} & {r.phase} & "
            f"{r.p_m1:.3f} & {r.p_m2:.3f} & {r.sep_mode_width:.2f} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def pick_clear_width_sweep_tt(
    rows: List[dict],
    *,
    target_widths: Sequence[int] = (5, 6, 7, 8, 14, 24),
    preferred_xstart: int = 10,
    min_phase: int = 0,
) -> List[TTCaseSpec]:
    """Pick width-sweep cases along a fixed x0 branch (allowing phase transitions)."""
    elig_rows = [
        r
        for r in rows
        if int(r["x_start"]) == int(preferred_xstart) and int(r["phase"]) >= int(min_phase)
    ]
    if not elig_rows:
        x_vals = sorted({int(r["x_start"]) for r in rows})
        if x_vals:
            x_near = min(x_vals, key=lambda x: (abs(int(x) - int(preferred_xstart)), int(x)))
            elig_rows = [r for r in rows if int(r["x_start"]) == int(x_near) and int(r["phase"]) >= int(min_phase)]
    if not elig_rows:
        return []

    elig_widths = sorted({int(r["Wy"]) for r in elig_rows})
    chosen_specs: List[TTCaseSpec] = []
    used_case_ids: set[str] = set()
    used_widths: set[int] = set()

    def score(r: dict) -> Tuple[float, float, float, float, float, float]:
        valley = float(r["valley_over_max"]) if r.get("valley_over_max") is not None else 9.0
        peak_ratio = _opt_float(r.get("peak_ratio"), 0.0)
        prom = max(0.0, peak_ratio - valley)
        bal = float(min(float(r["p_m1"]), float(r["p_m2"])))
        sep = float(r["sep_mode_width"])
        phase = float(r["phase"])
        return (phase, prom, peak_ratio, bal, sep, -valley)

    def to_spec(r: dict) -> TTCaseSpec:
        return TTCaseSpec(
            Wy=int(r["Wy"]),
            x_start=int(r["x_start"]),
            w_fast=int(r["w_fast"]),
            w_slow=int(r["w_slow"]),
            fast_skip=int(r["fast_skip"]),
            slow_skip=int(r["slow_skip"]),
            delta_fast=float(r["delta_fast"]),
            delta_slow=float(r["delta_slow"]),
        )

    for wt in target_widths:
        candidates_w = sorted(elig_widths, key=lambda w: (abs(int(w) - int(wt)), int(w)))
        if not candidates_w:
            continue
        picked_w: int | None = None
        for w in candidates_w:
            if int(w) not in used_widths:
                picked_w = int(w)
                break
        if picked_w is None:
            continue
        group = [r for r in elig_rows if int(r["Wy"]) == picked_w]
        if not group:
            continue
        best = max(group, key=score)
        spec = to_spec(best)
        if spec.case_id in used_case_ids:
            continue
        chosen_specs.append(spec)
        used_case_ids.add(spec.case_id)
        used_widths.add(int(picked_w))

    # If target widths collapse under coarse scan steps, fill with remaining widths
    # so the width-evolution panel stays informative.
    if len(chosen_specs) < len(tuple(target_widths)):
        remain_ws = [int(w) for w in elig_widths if int(w) not in used_widths]
        # Prefer widths near the transition from clear to non-clear if available.
        clear_ws = sorted(int(r["Wy"]) for r in elig_rows if int(r["phase"]) == 2)
        if clear_ws:
            w_pivot = int(clear_ws[-1]) + 1
            remain_ws.sort(key=lambda w: (abs(int(w) - int(w_pivot)), int(w)))
        for w_pick in remain_ws:
            if len(chosen_specs) >= len(tuple(target_widths)):
                break
            group = [r for r in elig_rows if int(r["Wy"]) == int(w_pick)]
            if not group:
                continue
            best = max(group, key=score)
            spec = to_spec(best)
            if spec.case_id in used_case_ids:
                continue
            chosen_specs.append(spec)
            used_case_ids.add(spec.case_id)
            used_widths.add(int(w_pick))
    return chosen_specs


def render_tt_width_sweep_table(results: Sequence[TTCaseResult], out_path: Path) -> None:
    rows = sorted(results, key=lambda r: (r.spec.Wy, r.spec.x_start))
    lines: List[str] = []
    lines.append("\\begin{tabular}{lrrrrrrr}")
    lines.append("\\toprule")
    lines.append("ID & $W_y$ & $x_0$ & phase & $t_{p1}$ & $t_{p2}$ & $p_{\\min}/p_{\\max}$ & valley/max \\\\")
    lines.append("\\midrule")
    for r in rows:
        tp1 = "-" if r.t_peak1 is None else str(int(r.t_peak1))
        tp2 = "-" if r.t_peak2 is None else str(int(r.t_peak2))
        pr = "-" if r.peak_ratio is None else f"{r.peak_ratio:.3f}"
        vm = "-" if r.valley_over_max is None else f"{r.valley_over_max:.3f}"
        lines.append(
            f"{_tex_escape(r.spec.case_id)} & {r.spec.Wy} & {r.spec.x_start} & {r.phase} & "
            f"{tp1} & {tp2} & {pr} & {vm} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def plot_tt_width_sweep_trend(out_path: Path, *, results: Sequence[TTCaseResult]) -> None:
    rows = sorted(results, key=lambda r: (r.spec.Wy, r.spec.x_start))
    if not rows:
        return
    W = np.asarray([r.spec.Wy for r in rows], dtype=np.float64)
    peak_ratio = np.asarray([(float(r.peak_ratio) if r.peak_ratio is not None else np.nan) for r in rows], dtype=np.float64)
    valley = np.asarray([(float(r.valley_over_max) if r.valley_over_max is not None else np.nan) for r in rows], dtype=np.float64)
    tp1 = np.asarray([(float(r.t_peak1) if r.t_peak1 is not None else np.nan) for r in rows], dtype=np.float64)
    tp2 = np.asarray([(float(r.t_peak2) if r.t_peak2 is not None else np.nan) for r in rows], dtype=np.float64)
    phases = np.asarray([int(r.phase) for r in rows], dtype=np.int64)

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9.6, 3.8), gridspec_kw=dict(wspace=0.28))
    ax0.plot(W, peak_ratio, marker="o", lw=1.6, color="#37474f", label=r"$p_{\min}/p_{\max}$")
    ax0.plot(W, valley, marker="s", lw=1.3, color="#8d6e63", label="valley/max")
    ax0.set_xlabel(r"$W_y$")
    ax0.set_ylabel("shape indicators")
    ax0.set_title("Peak-shape metrics vs width", fontsize=9)
    ax0.grid(alpha=0.25)
    ax0.legend(fontsize=8, loc="best")

    ax1.plot(W, tp1, marker="o", lw=1.4, color=C_SPLIT1, label=r"$t_{p1}$")
    ax1.plot(W, tp2, marker="o", lw=1.4, color=C_SPLIT2, label=r"$t_{p2}$")
    ax1.set_xlabel(r"$W_y$")
    ax1.set_ylabel("peak time")
    ax1.set_title("Peak-time drift vs width", fontsize=9)
    ax1.grid(alpha=0.25)
    ax1.legend(fontsize=8, loc="best")

    loss_idx = np.where(phases < 2)[0]
    if loss_idx.size > 0:
        w_loss = float(W[int(loss_idx[0])])
        for ax in (ax0, ax1):
            ax.axvline(w_loss, color="#777777", lw=1.0, ls="--", alpha=0.7)
        ax0.text(
            w_loss + 0.25,
            float(np.nanmax(np.r_[peak_ratio, valley])) * 0.96,
            "first clear-loss",
            fontsize=7.5,
            color="#444444",
            ha="left",
            va="top",
        )
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.16, top=0.90, wspace=0.28)
    fig.savefig(out_path)
    plt.close(fig)


def build_ot_case_geometry(
    *,
    Lx: int,
    Wy: int,
    corridor_halfwidth: int,
    wall_margin: int,
    delta_core: float,
    delta_open: float,
    start_x: int = 1,
    target_x: int | None = None,
) -> Tuple[Coord, Coord, Dict[Coord, Tuple[str, float]], Dict[Edge, float], np.ndarray, Tuple[int, int, int, int, int]]:
    if Wy < 5:
        raise ValueError("Wy must be >=5")
    y_mid = int((Wy - 1) // 2)
    sx = max(0, min(Lx - 1, int(start_x)))
    tx_raw = (Lx - 2) if target_x is None else int(target_x)
    tx = max(0, min(Lx - 1, tx_raw))
    if tx == sx:
        tx = min(Lx - 1, sx + 1)
    start = (sx, y_mid)
    target = (tx, y_mid)

    y_low = max(0, y_mid - int(corridor_halfwidth))
    y_high = min(Wy - 1, y_mid + int(corridor_halfwidth))
    x0 = int(wall_margin)
    x1 = int((Lx - 1) - wall_margin)
    x0 = max(0, min(Lx - 1, x0))
    x1 = max(0, min(Lx - 1, x1))
    if x1 < x0:
        x0, x1 = x1, x0

    # corridor mask
    n_states = Lx * Wy
    channel_mask = np.zeros(n_states, dtype=bool)
    for y in range(y_low, y_high + 1):
        for x in range(Lx):
            channel_mask[idx(x, y, Lx)] = True

    # internal walls are reflecting barriers between corridor band and outside, only in x-range [x0,x1].
    barrier_map: Dict[Edge, float] = {}
    for x in range(x0, x1 + 1):
        if y_low > 0:
            a = (x, y_low - 1)
            b = (x, y_low)
            barrier_map[_edge_key(a, b)] = 0.0
        if y_high < Wy - 1:
            a = (x, y_high)
            b = (x, y_high + 1)
            barrier_map[_edge_key(a, b)] = 0.0

    # local bias inside corridor: eastward, stronger in core x-span.
    local_bias_map: Dict[Coord, Tuple[str, float]] = {}
    for y in range(y_low, y_high + 1):
        for x in range(Lx):
            delta = float(delta_core) if x0 <= x <= x1 else float(delta_open)
            local_bias_map[(x, y)] = ("E", delta)
    # Do not bias the start/target themselves (harmless but makes branching/diagrams clearer).
    local_bias_map.pop(start, None)
    local_bias_map.pop(target, None)

    return start, target, local_bias_map, barrier_map, channel_mask, (y_mid, y_low, y_high, x0, x1)


def _draw_environment_ot(
    ax: plt.Axes,
    *,
    Lx: int,
    Wy: int,
    start: Coord,
    target: Coord,
    corridor_mask: np.ndarray,
    barrier_map: Dict[Edge, float],
    wall_span: Tuple[int, int, int, int, int],
    title: str,
    annotate: bool = True,
    equal_aspect: bool = True,
) -> None:
    _draw_rectangle_background(ax, Lx=Lx, Wy=Wy)

    y_mid, y_low, y_high, x0_wall, x1_wall = wall_span

    # Shade corridor cells.
    for y in range(Wy):
        for x in range(Lx):
            if corridor_mask[idx(x, y, Lx)]:
                # Darker shading on the wall-protected core span.
                in_core = (x0_wall <= x <= x1_wall) and (y_low <= y <= y_high)
                alpha = 0.55 if in_core else 0.28
                ax.add_patch(
                    Rectangle((x - 0.5, y - 0.5), 1.0, 1.0, facecolor=C_FAST, edgecolor="none", alpha=alpha, zorder=2)
                )

    # Draw internal walls (reflecting barriers).
    for (a, b), p_pass in barrier_map.items():
        if p_pass != 0.0:
            continue
        x0, y0 = a
        x1, y1 = b
        if x0 == x1 and abs(y1 - y0) == 1:
            y = min(y0, y1) + 0.5
            ax.plot([x0 - 0.5, x0 + 0.5], [y, y], color=C_WALL, lw=2.2, zorder=5)
        elif y0 == y1 and abs(x1 - x0) == 1:
            x = min(x0, x1) + 0.5
            ax.plot([x, x], [y0 - 0.5, y0 + 0.5], color=C_WALL, lw=2.2, zorder=5)

    # Local-bias arrows inside the corridor (visual guide; dynamics are encoded in local_bias_map).
    # Draw a few arrows to avoid clutter.
    for x in range(max(0, x0_wall), min(Lx - 1, x1_wall) + 1, 6):
        ax.annotate(
            "",
            xy=(x + 0.33, y_mid),
            xytext=(x - 0.33, y_mid),
            arrowprops=dict(arrowstyle="-|>", lw=1.05, color=C_ARROW, alpha=0.85, shrinkA=0, shrinkB=0),
            zorder=6,
        )

    ax.scatter([start[0]], [start[1]], c=C_START, s=58, marker=MARK_START, label="start", zorder=10)
    ax.scatter([target[0]], [target[1]], c=C_TGT, s=74, marker=MARK_TGT, label="target", zorder=10)

    if annotate:
        def _text_x(x: int) -> float:
            return (x - 2.0) if int(x) >= int(Lx - 3) else (x + 0.8)

        ax.text(_text_x(start[0]), start[1] + 0.8, "start", color=C_TEXT_START, fontsize=8, weight="bold", zorder=11)
        ax.text(_text_x(target[0]), target[1] + 0.8, "target", color=C_TEXT_TGT, fontsize=8, weight="bold", zorder=11)

    ax.set_xlim(-0.5, Lx - 0.5)
    ax.set_ylim(-0.5, Wy - 0.5)
    ax.set_aspect("equal" if bool(equal_aspect) else "auto")
    _draw_lattice_grid(ax, Lx=Lx, Wy=Wy, major_step=5)
    ax.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)

    for s in ax.spines.values():
        s.set_linewidth(2.2)
        s.set_color("black")
    ax.set_title(title, fontsize=10, pad=6)

    # Lightweight band guides (optional but helps read corridor thickness).
    ax.plot(
        [x0_wall - 0.5, x1_wall + 0.5],
        [y_low - 0.5, y_low - 0.5],
        color="#444444",
        lw=0.9,
        ls="--",
        alpha=0.32,
        zorder=4,
    )
    ax.plot(
        [x0_wall - 0.5, x1_wall + 0.5],
        [y_high + 0.5, y_high + 0.5],
        color="#444444",
        lw=0.9,
        ls="--",
        alpha=0.32,
        zorder=4,
    )


def plot_ot_geometry(
    out_path: Path,
    *,
    Lx: int,
    Wy: int,
    start: Coord,
    target: Coord,
    corridor_mask: np.ndarray,
    barrier_map: Dict[Edge, float],
    wall_span: Tuple[int, int, int, int, int],
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    _draw_environment_ot(
        ax,
        Lx=Lx,
        Wy=Wy,
        start=start,
        target=target,
        corridor_mask=corridor_mask,
        barrier_map=barrier_map,
        wall_span=wall_span,
        title=title,
    )
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        wanted = ["start", "target"]
        hl = {lab: h for h, lab in zip(handles, labels)}
        sel_h = [hl[k] for k in wanted if k in hl]
        sel_l = [k for k in wanted if k in hl]
        if sel_h:
            ax.legend(sel_h, sel_l, loc="upper right", fontsize=8, frameon=True)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_ot_env_heatmaps(
    out_path: Path,
    *,
    Lx: int,
    Wy: int,
    start: Coord,
    target: Coord,
    corridor_mask: np.ndarray,
    barrier_map: Dict[Edge, float],
    wall_span: Tuple[int, int, int, int, int],
    case_title: str,
    snapshots: Dict[int, np.ndarray],
    heat_times: Sequence[int],
) -> None:
    # Keep geometry-preserving aspect while avoiding oversized vertical whitespace
    # for very slender rectangles.
    aspect = float(Lx) / float(max(1, Wy))
    fig_h = float(np.clip(0.95 + 3.2 / max(1e-9, aspect), 1.30, 3.20))
    fig = plt.figure(figsize=(13.4, fig_h), constrained_layout=True)
    gs = fig.add_gridspec(1, 5, width_ratios=[1.18, 1, 1, 1, 0.08], wspace=0.05)
    ax0 = fig.add_subplot(gs[0, 0])
    _draw_environment_ot(
        ax0,
        Lx=Lx,
        Wy=Wy,
        start=start,
        target=target,
        corridor_mask=corridor_mask,
        barrier_map=barrier_map,
        wall_span=wall_span,
        title="environment",
        equal_aspect=True,
    )

    vmax = 0.0
    for t in heat_times:
        if int(t) in snapshots:
            vmax = max(vmax, float(np.max(snapshots[int(t)])))
    vmax = max(vmax, 1e-12)

    marks = [(target, C_TGT, MARK_TGT)]
    heat_axes: List[plt.Axes] = []
    for k, t in enumerate(heat_times):
        ax = fig.add_subplot(gs[0, k + 1])
        arr = snapshots.get(int(t))
        if arr is None:
            arr = np.zeros((Wy, Lx), dtype=np.float64)
        _draw_heatmap_panel(ax, arr=arr, t=int(t), marks=marks, vmax=vmax, equal_aspect=True)
        heat_axes.append(ax)

    im = getattr(heat_axes[-1], "_rect_im")
    cax = fig.add_subplot(gs[0, 4])
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label(r"$P(X_t=n\mid T>t)$", fontsize=10)
    fig.suptitle(case_title, fontsize=12, y=0.98)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def plot_ot_fpt(
    out_path: Path,
    *,
    f: np.ndarray,
    f_ch1: np.ndarray,
    f_ch2: np.ndarray,
    res: OTCaseResult,
) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    t = np.arange(len(f))
    f_s = smooth_series_display(f, window=7)
    f1_s = smooth_series_display(f_ch1, window=7)
    f2_s = smooth_series_display(f_ch2, window=7)
    ax.plot(t, f, color=C_ANY, lw=0.65, alpha=0.12)
    ax.plot(t, f_ch1, color=C_CH1, lw=0.55, alpha=0.10)
    ax.plot(t, f_ch2, color=C_CH2, lw=0.55, alpha=0.10)
    ax.plot(t, f_s, color=C_ANY, lw=1.7, label="F_total")
    ax.plot(t, f1_s, color=C_CH1, lw=1.2, label="F_from_corridor")
    ax.plot(t, f2_s, color=C_CH2, lw=1.2, label="F_from_outer")
    title = (
        f"{res.spec.case_id}: Wy={res.spec.Wy}, bx={res.spec.bx:.3f}, "
        f"sep={res.sep_peaks:.2f}, phase={res.phase}"
    )
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("t")
    ax.set_ylabel("probability")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)
    if res.t_peak1 is not None and res.t_peak2 is not None:
        ax.scatter([res.t_peak1, res.t_peak2], [f_s[res.t_peak1], f_s[res.t_peak2]], c=C_ANY, s=18, zorder=3)
    xmax = suggest_ot_fpt_xmax(len(f), f_total=f, t_peak2=res.t_peak2, tight=False)
    ax.set_xlim(0, xmax)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _hazard_components_one_target(f: np.ndarray, f_ch1: np.ndarray, f_ch2: np.ndarray, surv: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if len(f) < 2:
        z = np.zeros(0, dtype=np.float64)
        return z, z, z, z
    t = np.arange(1, len(f), dtype=np.int64)
    s_prev = np.maximum(surv[:-1], 1e-15)
    h = f[1:] / s_prev
    h1 = f_ch1[1:] / s_prev
    h2 = f_ch2[1:] / s_prev
    return t, h, h1, h2


def plot_ot_hazard(
    out_path: Path,
    *,
    f: np.ndarray,
    f_ch1: np.ndarray,
    f_ch2: np.ndarray,
    surv: np.ndarray,
    res: OTCaseResult,
) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 3.7))
    t, h, h1, h2 = _hazard_components_one_target(f, f_ch1, f_ch2, surv)
    h_s = smooth_series_display(h, window=7)
    h1_s = smooth_series_display(h1, window=7)
    h2_s = smooth_series_display(h2, window=7)
    ax.plot(t, h, color=C_ANY, lw=0.65, alpha=0.12)
    ax.plot(t, h1, color=C_CH1, lw=0.55, alpha=0.10)
    ax.plot(t, h2, color=C_CH2, lw=0.55, alpha=0.10)
    ax.plot(t, h_s, color=C_ANY, lw=1.7, label="h_total")
    ax.plot(t, h1_s, color=C_CH1, lw=1.2, label="h_corridor")
    ax.plot(t, h2_s, color=C_CH2, lw=1.2, label="h_outer")
    if res.t_valley is not None and res.t_valley > 0:
        ax.axvline(res.t_valley, color="#444444", lw=1.0, ls="--", alpha=0.65)
    ax.set_xlabel("t")
    ax.set_ylabel("hazard")
    ax.set_title(f"{res.spec.case_id}: hazard decomposition", fontsize=9)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)
    xmax = suggest_ot_fpt_xmax(len(f), f_total=f, t_peak2=res.t_peak2, tight=True)
    xmax = min(len(t), xmax)
    ax.set_xlim(1, max(2, int(xmax)))
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_ot_rep_geometry_grid(
    out_path: Path,
    *,
    Lx: int,
    layouts: Dict[str, dict],
    reps: Sequence[OTCaseResult],
) -> None:
    if not reps:
        return
    n = min(4, len(reps))
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.2))
    axes_list = axes.flatten()
    for ax in axes_list[n:]:
        ax.axis("off")
    for ax, r in zip(axes_list, reps[:n]):
        lay = layouts[r.spec.case_id]
        _draw_environment_ot(
            ax,
            Lx=Lx,
            Wy=int(lay["Wy"]),
            start=lay["start"],
            target=lay["target"],
            corridor_mask=lay["corridor_mask"],
            barrier_map=lay["barrier_map"],
            wall_span=lay["wall_span"],
            title=f"{r.spec.case_id} (phase={r.phase}, x_s={lay['start'][0]}, x_t={lay['target'][0]})",
            annotate=False,
        )
        # Show global bias value and direction explicitly; this is not visible from
        # corridor geometry alone, but it strongly affects peak splitting.
        bx = float(r.spec.bx)
        ax.text(
            0.02,
            0.97,
            f"$b_x={bx:+.2f}$",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=8.0,
            color="#222222",
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.70),
        )
        if abs(bx) > 1e-12:
            x0a, x1a = (0.08, 0.20) if bx > 0 else (0.20, 0.08)
            ax.annotate(
                "",
                xy=(x1a, 0.91),
                xytext=(x0a, 0.91),
                xycoords=ax.transAxes,
                arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#444444", alpha=0.85),
            )
        phase_i = int(r.phase)
        if phase_i >= 2:
            tag = "clear-double"
            tag_color = "#c62828"
        elif phase_i == 1:
            tag = "weak-double"
            tag_color = "#ef6c00"
        else:
            tag = "single-peak"
            tag_color = "#444444"
        ax.text(
            0.98,
            0.97,
            tag,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=7.8,
            color=tag_color,
        )
        cfg_txt = "\n".join(
            [
                f"size={Lx}x{int(lay['Wy'])}",
                f"x_s={int(lay['start'][0])}, x_t={int(lay['target'][0])}",
                f"corr_h={int(r.spec.corridor_halfwidth)}, wall_m={int(r.spec.wall_margin)}",
                f"delta_c={float(r.spec.delta_core):.2f}, delta_o={float(r.spec.delta_open):.2f}",
            ]
        )
        ax.text(
            0.985,
            0.03,
            cfg_txt,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=7.0,
            family="monospace",
            color="#222222",
            bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#aaaaaa", lw=0.6, alpha=0.82),
        )
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_ot_rep_fpt_grid(
    out_path: Path,
    *,
    reps: Sequence[OTCaseResult],
    series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
) -> None:
    if not reps:
        return
    n = min(4, len(reps))
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.0))
    axes_list = axes.flatten()
    for ax in axes_list[n:]:
        ax.axis("off")
    for ax, r in zip(axes_list, reps[:n]):
        f, f1, f2, _ = series_map[r.spec.case_id]
        t = np.arange(len(f))
        f_s = smooth_series_display(f, window=7)
        f1_s = smooth_series_display(f1, window=7)
        f2_s = smooth_series_display(f2, window=7)
        ax.plot(t, f_s, color=C_ANY, lw=1.6, label="F_total")
        ax.plot(t, f1_s, color=C_CH1, lw=1.1, label="F_corridor")
        ax.plot(t, f2_s, color=C_CH2, lw=1.1, label="F_outer")
        if r.t_peak1 is not None and 0 <= int(r.t_peak1) < len(f):
            tp1 = int(r.t_peak1)
            y1 = float(f_s[tp1])
            ax.axvline(tp1, color="#666666", lw=1.0, ls="--", alpha=0.65)
            ax.scatter([tp1], [y1], s=20, c=C_ANY, zorder=4)
            ax.text(tp1 + 4, y1 * 1.03, r"$p_1$", fontsize=8, color="#333333")
        if r.t_peak2 is not None and 0 <= int(r.t_peak2) < len(f):
            tp2 = int(r.t_peak2)
            y2 = float(f_s[tp2])
            ax.axvline(tp2, color="#666666", lw=1.0, ls="--", alpha=0.65)
            ax.scatter([tp2], [y2], s=20, c=C_ANY, zorder=4)
            ax.text(tp2 + 4, y2 * 1.03, r"$p_2$", fontsize=8, color="#333333")
        if r.t_valley is not None and 0 <= int(r.t_valley) < len(f):
            ax.axvline(int(r.t_valley), color="#999999", lw=0.9, ls=":", alpha=0.70)
        title = f"{r.spec.case_id}: phase={r.phase}, sep={r.sep_peaks:.2f}"
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("t")
        ax.set_ylabel("probability")
        ax.grid(alpha=0.25)
        xmax = suggest_ot_fpt_xmax(len(f), f_total=f, t_peak2=r.t_peak2, tight=True)
        ax.set_xlim(0, xmax)
    handles, labels = axes_list[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path)
    plt.close(fig)


def plot_ot_rep_hazard_grid(
    out_path: Path,
    *,
    reps: Sequence[OTCaseResult],
    series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
) -> None:
    if not reps:
        return
    n = min(4, len(reps))
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.0))
    axes_list = axes.flatten()
    for ax in axes_list[n:]:
        ax.axis("off")
    for ax, r in zip(axes_list, reps[:n]):
        f, f1, f2, surv = series_map[r.spec.case_id]
        t, h, h1, h2 = _hazard_components_one_target(f, f1, f2, surv)
        h_s = smooth_series_display(h, window=7)
        h1_s = smooth_series_display(h1, window=7)
        h2_s = smooth_series_display(h2, window=7)
        ax.plot(t, h_s, color=C_ANY, lw=1.6, label="h_total")
        ax.plot(t, h1_s, color=C_CH1, lw=1.1, label="h_corridor")
        ax.plot(t, h2_s, color=C_CH2, lw=1.1, label="h_outer")
        if r.t_valley is not None and r.t_valley > 0:
            ax.axvline(r.t_valley, color="#444444", lw=1.0, ls="--", alpha=0.65)
        xmax = suggest_ot_fpt_xmax(len(f), f_total=f, t_peak2=r.t_peak2, tight=True)
        xmax = min(len(t), xmax)
        ax.set_xlim(1, max(2, int(xmax)))
        ax.set_xlabel("t")
        ax.set_ylabel("hazard")
        ax.set_title(f"{r.spec.case_id}: hazard", fontsize=9)
        ax.grid(alpha=0.25)
    handles, labels = axes_list[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=10, frameon=False, bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path)
    plt.close(fig)


def render_ot_scan_overview(rows: List[dict], out_path: Path) -> None:
    widths = sorted({int(r["Wy"]) for r in rows})
    bx_vals = sorted({float(r["bx"]) for r in rows})
    lines: List[str] = []
    lines.append("\\begin{tabular}{r" + "c" * len(bx_vals) + "}")
    header = " $W_y$ " + " & " + " & ".join([f"$b_x={b:.2f}$" for b in bx_vals]) + " \\\\"
    lines.append("\\toprule")
    lines.append(header)
    lines.append("\\midrule")
    for Wy in widths:
        cells = []
        for bx in bx_vals:
            group = [r for r in rows if int(r["Wy"]) == Wy and abs(float(r["bx"]) - bx) < 1e-12]
            ph = int(group[0]["phase"]) if group else 0
            cells.append(str(ph))
        lines.append(f"{Wy} & " + " & ".join(cells) + " \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def render_ot_anchor_table(
    rows: List[dict],
    out_path: Path,
    *,
    start_x: int,
    target_x: int,
    bx_ref: float,
    wy_ref: int,
    phase_ref: int,
) -> None:
    rows_ref = [r for r in rows if abs(float(r["bx"]) - float(bx_ref)) < 1e-12]
    widths = sorted({int(r["Wy"]) for r in rows_ref}) if rows_ref else sorted({int(r["Wy"]) for r in rows})
    width_steps = [int(b - a) for a, b in zip(widths[:-1], widths[1:]) if int(b) > int(a)]
    scan_step = min(width_steps) if width_steps else 1
    clear_ws = sorted(int(r["Wy"]) for r in rows_ref if int(r["phase"]) == 2)
    intervals = _contiguous_intervals(clear_ws, step=scan_step)
    if intervals:
        clear_txt_parts: List[str] = []
        for a, b in intervals:
            if a == b:
                clear_txt_parts.append(f"{a}")
            elif scan_step > 1:
                clear_txt_parts.append(f"{a}-{b} (step={scan_step})")
            else:
                clear_txt_parts.append(f"{a}-{b}")
        clear_txt = ", ".join(clear_txt_parts)
        _, up_b = intervals[-1]
        loss_candidates = [w for w in widths if int(w) > int(up_b)]
        loss_txt = str(int(loss_candidates[0])) if loss_candidates else "-"
    else:
        clear_txt = "-"
        loss_txt = "-"

    lines: List[str] = []
    lines.append("\\begin{tabular}{rrrrccc}")
    lines.append("\\toprule")
    lines.append("$x_s$ & $x_t$ & $b_x^{*}$ & $W_y^{\\mathrm{ref}}$ & phase(ref) & clear interval(s) & first loss \\\\")
    lines.append("\\midrule")
    lines.append(
        f"{int(start_x)} & {int(target_x)} & {float(bx_ref):.3f} & {int(wy_ref)} & {int(phase_ref)} & {clear_txt} & {loss_txt} \\\\"
    )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def pick_representatives_ot(rows: List[dict], *, max_total: int = 4) -> List[OTCaseSpec]:
    """Pick a small, readable representative set.

    Goal: show contrast across global bias values (bx) and phases with a few cases.
    """
    rows2 = sorted(
        rows,
        key=lambda r: (
            -int(r["phase"]),
            _opt_float(r.get("valley_over_max"), 9.0),
            -_opt_float(r.get("sep_peaks"), 0.0),
        ),
    )

    def to_spec(r: dict) -> OTCaseSpec:
        return OTCaseSpec(
            Wy=int(r["Wy"]),
            bx=float(r["bx"]),
            corridor_halfwidth=int(r["corridor_halfwidth"]),
            wall_margin=int(r["wall_margin"]),
            delta_core=float(r["delta_core"]),
            delta_open=float(r["delta_open"]),
        )

    def case_id(r: dict) -> str:
        return to_spec(r).case_id

    def bx_of(r: dict) -> float:
        return float(r["bx"])

    chosen: List[dict] = []
    seen: set[str] = set()

    def add_first(predicate) -> None:
        if len(chosen) >= max_total:
            return
        for r in rows2:
            if not predicate(r):
                continue
            cid = case_id(r)
            if cid in seen:
                continue
            chosen.append(r)
            seen.add(cid)
            return

    # 1) Best clear double (phase=2), if any.
    add_first(lambda r: int(r["phase"]) == 2)

    # 2) Best weak double (phase=1).
    add_first(lambda r: int(r["phase"]) == 1)

    # 3) Another weak double at a different bx (helps comparison), if possible.
    if chosen:
        bx0 = bx_of(chosen[-1])
        add_first(lambda r: int(r["phase"]) == 1 and abs(bx_of(r) - bx0) > 1e-12)

    # 4) One single peak (phase=0), prefer bx=0.
    n_before = len(chosen)
    add_first(lambda r: int(r["phase"]) == 0 and abs(bx_of(r) - 0.0) < 1e-12)
    if len(chosen) == n_before:
        add_first(lambda r: int(r["phase"]) == 0)

    # Fill remaining by best cases, preferring new widths.
    seen_Wy = {int(r["Wy"]) for r in chosen}
    for r in rows2:
        if len(chosen) >= max_total:
            break
        cid = case_id(r)
        if cid in seen:
            continue
        if int(r["Wy"]) in seen_Wy and (len(chosen) + 1) < max_total:
            continue
        chosen.append(r)
        seen.add(cid)
        seen_Wy.add(int(r["Wy"]))

    # Order by informativeness so ot_repA/B heatmaps correspond to the strongest cases.
    chosen.sort(
        key=lambda r: (
            -int(r["phase"]),
            _opt_float(r.get("valley_over_max"), 9.0),
            -_opt_float(r.get("sep_peaks"), 0.0),
        )
    )
    return [to_spec(r) for r in chosen]


def render_ot_representative_table(results: Sequence[OTCaseResult], out_path: Path) -> None:
    lines: List[str] = []
    lines.append("\\begin{tabular}{lrrrrr}")
    lines.append("\\toprule")
    lines.append("ID & $W_y$ & $b_x$ & phase & valley/max & sep-score \\\\")
    lines.append("\\midrule")
    for r in results:
        vm = "-" if r.valley_over_max is None else f"{r.valley_over_max:.3f}"
        lines.append(
            f"{_tex_escape(r.spec.case_id)} & {r.spec.Wy} & {r.spec.bx:.3f} & {r.phase} & {vm} & {r.sep_peaks:.2f} \\\\"
        )
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _interval_text(vals: Sequence[int], *, step: int = 1) -> str:
    vv = sorted({int(v) for v in vals})
    if not vv:
        return "-"
    ints = _contiguous_intervals(vv, step=max(1, int(step)))
    parts: List[str] = []
    for a, b in ints:
        if int(a) == int(b):
            parts.append(f"{int(a)}")
        else:
            parts.append(f"{int(a)}-{int(b)}")
    return ", ".join(parts)


def _nearest_in_list(values: Sequence[float], target: float) -> float:
    vals = [float(v) for v in values]
    if not vals:
        raise ValueError("empty value list")
    return float(min(vals, key=lambda v: (abs(float(v) - float(target)), abs(float(v)), float(v))))


def build_ot_corridor_focus_grids(
    rows: Sequence[dict],
    *,
    widths: Sequence[int],
    corridor_halfwidth_values: Sequence[int],
    bx_focus: float,
) -> Tuple[np.ndarray, np.ndarray]:
    lookup = {
        (int(r["corridor_halfwidth"]), int(r["Wy"]), round(float(r["bx"]), 12)): r
        for r in rows
    }
    phase = np.zeros((len(corridor_halfwidth_values), len(widths)), dtype=np.int64)
    sep = np.zeros_like(phase, dtype=np.float64)
    for ih, h in enumerate(corridor_halfwidth_values):
        for iW, Wy in enumerate(widths):
            row = lookup.get((int(h), int(Wy), round(float(bx_focus), 12)))
            if row is None:
                raise KeyError(f"missing corridor scan row for h={h}, Wy={Wy}, bx={bx_focus}")
            phase[ih, iW] = int(row["phase"])
            sep[ih, iW] = float(row["sep_peaks"])
    return phase, sep


def plot_ot_corridor_phase_vs_width(
    out_path: Path,
    *,
    phase: np.ndarray,
    widths: Sequence[int],
    corridor_halfwidth_values: Sequence[int],
    bx_focus: float,
) -> None:
    cmap = plt.matplotlib.colors.ListedColormap([C_PHASE0, C_PHASE1, C_PHASE2])
    band_ws = [int(2 * int(h) + 1) for h in corridor_halfwidth_values]
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    im = ax.imshow(phase, origin="lower", cmap=cmap, vmin=-0.5, vmax=2.5, aspect="auto")
    ax.set_xticks(range(len(widths)))
    ax.set_xticklabels([str(int(w)) for w in widths])
    ax.set_yticks(range(len(band_ws)))
    ax.set_yticklabels([str(int(w)) for w in band_ws])
    ax.set_xlabel("Wy")
    ax.set_ylabel("corridor band width (cells)")
    ax.set_title(f"One-target phase vs corridor width (bx={bx_focus:+.2f})")
    for i in range(phase.shape[0]):
        for j in range(phase.shape[1]):
            ax.text(j, i, f"{int(phase[i, j])}", ha="center", va="center", fontsize=8, color="black")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cbar.set_ticks([0, 1, 2])
    cbar.set_ticklabels(["single", "weak", "clear"])
    fig.subplots_adjust(left=0.09, right=0.965, bottom=0.16, top=0.90, wspace=0.25)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def plot_ot_corridor_sep_vs_width(
    out_path: Path,
    *,
    sep: np.ndarray,
    widths: Sequence[int],
    corridor_halfwidth_values: Sequence[int],
    bx_focus: float,
) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    band_ws = [int(2 * int(h) + 1) for h in corridor_halfwidth_values]
    for i, bw in enumerate(band_ws):
        ax.plot(widths, sep[i, :], marker="o", ms=3.3, lw=1.25, label=f"band={bw}")
    ax.axhline(1.0, color="#666666", lw=1.0, ls="--", alpha=0.75, label="sep=1 threshold")
    ax.set_xlabel("Wy")
    ax.set_ylabel("sep-score")
    ax.set_title(f"One-target separation vs corridor width (bx={bx_focus:+.2f})")
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=8.5, ncol=2)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def render_ot_corridor_width_summary(
    rows: List[dict],
    out_path: Path,
    *,
    widths: Sequence[int],
    corridor_halfwidth_values: Sequence[int],
    bx_focus: float,
    bx_weak: float,
    bx_zero: float,
) -> None:
    width_steps = [int(b - a) for a, b in zip(widths[:-1], widths[1:]) if int(b) > int(a)]
    step = min(width_steps) if width_steps else 1
    lookup = {
        (int(r["corridor_halfwidth"]), int(r["Wy"]), round(float(r["bx"]), 12)): r
        for r in rows
    }

    lines: List[str] = []
    lines.append("\\begin{tabular}{rccccc}")
    lines.append("\\toprule")
    lines.append(
        "$h$ & band width & "
        + f"phase2 @ $b_x={bx_focus:+.2f}$"
        + " & first loss & "
        + f"phase$\\ge1$ @ $b_x={bx_weak:+.2f}$"
        + " & "
        + f"phase$\\ge1$ @ $b_x={bx_zero:+.2f}$ \\\\"
    )
    lines.append("\\midrule")

    for h in corridor_halfwidth_values:
        rows_focus = []
        rows_weak = []
        rows_zero = []
        for Wy in widths:
            rf = lookup.get((int(h), int(Wy), round(float(bx_focus), 12)))
            rw = lookup.get((int(h), int(Wy), round(float(bx_weak), 12)))
            rz = lookup.get((int(h), int(Wy), round(float(bx_zero), 12)))
            if rf is not None:
                rows_focus.append(rf)
            if rw is not None:
                rows_weak.append(rw)
            if rz is not None:
                rows_zero.append(rz)

        clear_ws = sorted(int(r["Wy"]) for r in rows_focus if int(r["phase"]) >= 2)
        weak_ws = sorted(int(r["Wy"]) for r in rows_weak if int(r["phase"]) >= 1)
        zero_ws = sorted(int(r["Wy"]) for r in rows_zero if int(r["phase"]) >= 1)
        clear_txt = _interval_text(clear_ws, step=step)
        weak_txt = _interval_text(weak_ws, step=step)
        zero_txt = _interval_text(zero_ws, step=step)

        if clear_ws:
            up = int(max(clear_ws))
            loss_candidates = [
                int(r["Wy"]) for r in rows_focus if int(r["Wy"]) > up and int(r["phase"]) < 2
            ]
            loss_txt = str(min(loss_candidates)) if loss_candidates else "-"
        else:
            loss_txt = "-"

        lines.append(
            f"{int(h)} & {int(2 * int(h) + 1)} & {clear_txt} & {loss_txt} & {weak_txt} & {zero_txt} \\\\"
        )

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def build_ot_bias2d_grids(
    rows: Sequence[dict],
    *,
    bx_values: Sequence[float],
    by_values: Sequence[float],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lookup = {
        (round(float(r["bx"]), 12), round(float(r["by"]), 12)): r
        for r in rows
    }
    phase = np.zeros((len(by_values), len(bx_values)), dtype=np.int64)
    sep = np.zeros_like(phase, dtype=np.float64)
    valley = np.zeros_like(phase, dtype=np.float64)
    for iy, by in enumerate(by_values):
        for jx, bx in enumerate(bx_values):
            row = lookup.get((round(float(bx), 12), round(float(by), 12)))
            if row is None:
                raise KeyError(f"missing bias2d row for bx={bx}, by={by}")
            phase[iy, jx] = int(row["phase"])
            sep[iy, jx] = float(row["sep_peaks"])
            valley[iy, jx] = float(row["valley_over_max"]) if row.get("valley_over_max") is not None else 1.0
    return phase, sep, valley


def render_ot_bias2d_phase_table(
    rows: Sequence[dict],
    out_path: Path,
    *,
    bx_values: Sequence[float],
    by_values: Sequence[float],
) -> None:
    lookup = {
        (round(float(r["bx"]), 12), round(float(r["by"]), 12)): int(r["phase"])
        for r in rows
    }
    lines: List[str] = []
    lines.append("\\begin{tabular}{r" + "c" * len(bx_values) + "}")
    lines.append("\\toprule")
    lines.append("$b_y$ & " + " & ".join([f"$b_x={float(bx):.2f}$" for bx in bx_values]) + " \\\\")
    lines.append("\\midrule")
    for by in by_values:
        cells: List[str] = []
        for bx in bx_values:
            ph = lookup.get((round(float(bx), 12), round(float(by), 12)), 0)
            cells.append(str(int(ph)))
        lines.append(f"{float(by):.2f} & " + " & ".join(cells) + " \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parse_float_list(s: str) -> List[float]:
    out: List[float] = []
    for tok in str(s).split(","):
        tok = tok.strip()
        if not tok:
            continue
        out.append(float(tok))
    return out


def parse_int_list(s: str) -> List[int]:
    out: List[int] = []
    for tok in str(s).split(","):
        tok = tok.strip()
        if not tok:
            continue
        out.append(int(tok))
    return out


def _parse_csv_scalar(v: Any) -> Any:
    if v is None:
        return None
    s = str(v).strip()
    if not s or s in ("-", "None", "none", "NaN", "nan"):
        return None
    if re.fullmatch(r"[+-]?\d+", s):
        return int(s)
    try:
        return float(s)
    except ValueError:
        return s


def load_scan_rows_csv(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append({k: _parse_csv_scalar(v) for k, v in r.items()})
    return rows


def _float_close(a: float, b: float, tol: float = 1e-12) -> bool:
    return abs(float(a) - float(b)) <= float(tol)


def _match_unique_int(rows: List[dict], key: str, target: int) -> bool:
    vals = {int(r[key]) for r in rows if r.get(key) is not None}
    return vals == {int(target)}


def _match_unique_float(rows: List[dict], key: str, target: float, tol: float = 1e-12) -> bool:
    vals = [float(r[key]) for r in rows if r.get(key) is not None]
    if not vals:
        return False
    return all(_float_close(v, float(target), tol=tol) for v in vals)


def _match_float_list(a: Sequence[float], b: Sequence[float], tol: float = 1e-12) -> bool:
    if len(a) != len(b):
        return False
    return all(_float_close(float(x), float(y), tol=tol) for x, y in zip(a, b))


def try_reuse_tt_scan(
    *,
    data_dir: Path,
    widths: Sequence[int],
    x_starts: Sequence[int],
    Lx: int,
    q: float,
    args: argparse.Namespace,
) -> Tuple[List[dict], np.ndarray, np.ndarray, np.ndarray] | None:
    tt_csv = data_dir / "tt_scan_width_xstart.csv"
    tt_json = data_dir / "tt_scan_width_xstart.json"
    if not (tt_csv.exists() and tt_json.exists()):
        return None
    try:
        info = json.loads(tt_json.read_text(encoding="utf-8"))
    except Exception:
        return None

    meta = info.get("meta", {})
    if int(meta.get("Lx", -1)) != int(Lx):
        return None
    if not _float_close(float(meta.get("q", -1.0)), float(q)):
        return None
    if str(meta.get("tt_style", "")) != str(args.tt_style):
        return None
    if int(meta.get("scan_t_max", -1)) != int(args.scan_t_max):
        return None
    if not _float_close(float(meta.get("scan_surv_tol", -1.0)), float(args.scan_surv_tol), tol=1e-18):
        return None

    ws_json = [int(v) for v in info.get("widths", [])]
    xs_json = [int(v) for v in info.get("x_starts", [])]
    if ws_json != [int(v) for v in widths] or xs_json != [int(v) for v in x_starts]:
        return None

    try:
        rows = load_scan_rows_csv(tt_csv)
    except Exception:
        return None
    if len(rows) != len(widths) * len(x_starts):
        return None
    if not rows:
        return None

    if not _match_unique_int(rows, "w_fast", int(args.tt_w_fast)):
        return None
    if not _match_unique_int(rows, "w_slow", int(args.tt_w_slow)):
        return None
    if not _match_unique_int(rows, "fast_skip", int(args.tt_fast_skip)):
        return None
    if not _match_unique_int(rows, "slow_skip", int(args.tt_slow_skip)):
        return None
    if not _match_unique_float(rows, "delta_fast", float(args.tt_delta_fast)):
        return None
    if not _match_unique_float(rows, "delta_slow", float(args.tt_delta_slow)):
        return None

    lookup = {(int(r["Wy"]), int(r["x_start"])): r for r in rows}
    tt_phase = np.zeros((len(widths), len(x_starts)), dtype=np.int64)
    tt_sep = np.zeros_like(tt_phase, dtype=np.float64)
    tt_valley = np.zeros_like(tt_phase, dtype=np.float64)
    for iW, Wy in enumerate(widths):
        for jx, x0 in enumerate(x_starts):
            row = lookup.get((int(Wy), int(x0)))
            if row is None:
                return None
            tt_phase[iW, jx] = int(row["phase"])
            tt_sep[iW, jx] = float(row["sep_mode_width"])
            tt_valley[iW, jx] = float(row["valley_over_max"]) if row.get("valley_over_max") is not None else 1.0
    return rows, tt_phase, tt_sep, tt_valley


def try_reuse_ot_scan(
    *,
    data_dir: Path,
    widths: Sequence[int],
    bx_values: Sequence[float],
    placement_width: int,
    Lx: int,
    q: float,
    args: argparse.Namespace,
) -> Tuple[List[dict], np.ndarray, np.ndarray, np.ndarray, int, int, dict] | None:
    ot_csv = data_dir / "ot_scan_width_globalbias.csv"
    ot_json = data_dir / "ot_scan_width_globalbias.json"
    if not (ot_csv.exists() and ot_json.exists()):
        return None
    try:
        info = json.loads(ot_json.read_text(encoding="utf-8"))
    except Exception:
        return None
    meta = info.get("meta", {})
    if int(meta.get("Lx", -1)) != int(Lx):
        return None
    if not _float_close(float(meta.get("q", -1.0)), float(q)):
        return None
    if int(meta.get("scan_t_max", -1)) != int(args.scan_t_max):
        return None
    if not _float_close(float(meta.get("scan_surv_tol", -1.0)), float(args.scan_surv_tol), tol=1e-18):
        return None
    ws_json = [int(v) for v in info.get("widths", [])]
    if ws_json != [int(v) for v in widths]:
        return None
    bxs_json = [float(v) for v in meta.get("bx_values", [])]
    if not _match_float_list(bxs_json, [float(v) for v in bx_values]):
        return None

    try:
        rows = load_scan_rows_csv(ot_csv)
    except Exception:
        return None
    if len(rows) != len(widths) * len(bx_values):
        return None
    if not rows:
        return None
    if not _match_unique_int(rows, "corridor_halfwidth", int(args.ot_corridor_halfwidth)):
        return None
    if not _match_unique_int(rows, "wall_margin", int(args.ot_wall_margin)):
        return None
    if not _match_unique_float(rows, "delta_core", float(args.ot_delta_core)):
        return None
    if not _match_unique_float(rows, "delta_open", float(args.ot_delta_open)):
        return None
    start_vals = {int(r["start_x"]) for r in rows if r.get("start_x") is not None}
    target_vals = {int(r["target_x"]) for r in rows if r.get("target_x") is not None}
    if len(start_vals) != 1 or len(target_vals) != 1:
        return None
    ot_start_x = int(next(iter(start_vals)))
    ot_target_x = int(next(iter(target_vals)))

    lookup = {(int(r["Wy"]), round(float(r["bx"]), 12)): r for r in rows}
    ot_phase = np.zeros((len(widths), len(bx_values)), dtype=np.int64)
    ot_sep = np.zeros_like(ot_phase, dtype=np.float64)
    ot_valley = np.zeros_like(ot_phase, dtype=np.float64)
    for iW, Wy in enumerate(widths):
        for j, bx in enumerate(bx_values):
            row = lookup.get((int(Wy), round(float(bx), 12)))
            if row is None:
                return None
            ot_phase[iW, j] = int(row["phase"])
            ot_sep[iW, j] = float(row["sep_peaks"])
            ot_valley[iW, j] = float(row["valley_over_max"]) if row.get("valley_over_max") is not None else 1.0

    bx_stats: Dict[float, Tuple[int, int, float, float, float]] = {}
    for bx in [float(v) for v in bx_values]:
        group = [r for r in rows if _float_close(float(r["bx"]), bx)]
        if not group:
            continue
        n2 = int(sum(int(r["phase"]) == 2 for r in group))
        n1p = int(sum(int(r["phase"]) >= 1 for r in group))
        sep_vals = [float(r["sep_peaks"]) for r in group if r.get("sep_peaks") is not None]
        valley_vals = [float(r["valley_over_max"]) for r in group if r.get("valley_over_max") is not None]
        sep_mean = float(np.mean(sep_vals)) if sep_vals else 0.0
        valley_mean = float(np.mean(valley_vals)) if valley_vals else 1.0
        bx_stats[round(float(bx), 12)] = (n2, n1p, sep_mean, -valley_mean, -abs(float(bx)))
    if not bx_stats:
        return None
    bx_ref = max(
        [float(v) for v in bx_values],
        key=lambda b: bx_stats.get(round(float(b), 12), (-1, -1, -1.0, -1.0, -1.0)),
    )

    wy_ref = int(min(widths, key=lambda w: (abs(int(w) - int(placement_width)), int(w))))
    row_ref = lookup.get((int(wy_ref), round(float(bx_ref), 12)))
    if row_ref is None:
        cand = [r for r in rows if _float_close(float(r["bx"]), float(bx_ref))]
        if not cand:
            return None
        row_ref = max(cand, key=lambda r: int(r["phase"]))

    group_ref = [r for r in rows if _float_close(float(r["bx"]), float(bx_ref))]
    phase2_count = int(sum(int(r["phase"]) >= 2 for r in group_ref))
    phase1plus_count = int(sum(int(r["phase"]) >= 1 for r in group_ref))
    placement_ws = sorted(
        {
            int(min(widths, key=lambda w: (abs(int(w) - int(wt)), int(w))))
            for wt in (int(placement_width) - 4, int(placement_width), int(placement_width) + 4)
        }
    )
    best_anchor = {
        "start_x": int(ot_start_x),
        "target_x": int(ot_target_x),
        "bx": float(bx_ref),
        "Wy_ref": int(row_ref["Wy"]),
        "phase": int(row_ref["phase"]),
        "sep_peaks": float(row_ref["sep_peaks"]),
        "valley_over_max": row_ref.get("valley_over_max"),
        "peak_balance": None,
        "t_peak1": row_ref.get("t_peak1"),
        "t_peak2": row_ref.get("t_peak2"),
        "phase2_count": int(phase2_count),
        "phase1plus_count": int(phase1plus_count),
        "placement_widths": [int(w) for w in placement_ws],
    }
    return rows, ot_phase, ot_sep, ot_valley, ot_start_x, ot_target_x, best_anchor


def try_reuse_ot_corridor_scan(
    *,
    data_dir: Path,
    widths: Sequence[int],
    bx_values: Sequence[float],
    corridor_halfwidth_values: Sequence[int],
    Lx: int,
    q: float,
    args: argparse.Namespace,
    start_x: int,
    target_x: int,
) -> List[dict] | None:
    csv_path = data_dir / "ot_scan_corridor_halfwidth.csv"
    json_path = data_dir / "ot_scan_corridor_halfwidth.json"
    if not (csv_path.exists() and json_path.exists()):
        return None
    try:
        info = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    meta = info.get("meta", {})
    if int(meta.get("Lx", -1)) != int(Lx):
        return None
    if not _float_close(float(meta.get("q", -1.0)), float(q)):
        return None
    if int(meta.get("scan_t_max", -1)) != int(args.scan_t_max):
        return None
    if not _float_close(float(meta.get("scan_surv_tol", -1.0)), float(args.scan_surv_tol), tol=1e-18):
        return None
    if int(meta.get("start_x", -999)) != int(start_x):
        return None
    if int(meta.get("target_x", -999)) != int(target_x):
        return None
    if int(meta.get("wall_margin", -999)) != int(args.ot_wall_margin):
        return None
    if not _float_close(float(meta.get("delta_core", -1.0)), float(args.ot_delta_core)):
        return None
    if not _float_close(float(meta.get("delta_open", -1.0)), float(args.ot_delta_open)):
        return None

    ws_json = [int(v) for v in info.get("widths", [])]
    hs_json = [int(v) for v in info.get("corridor_halfwidth_values", [])]
    bx_json = [float(v) for v in info.get("bx_values", [])]
    if ws_json != [int(v) for v in widths]:
        return None
    if hs_json != [int(v) for v in corridor_halfwidth_values]:
        return None
    if not _match_float_list(bx_json, [float(v) for v in bx_values]):
        return None

    try:
        rows = load_scan_rows_csv(csv_path)
    except Exception:
        return None
    if len(rows) != len(widths) * len(bx_values) * len(corridor_halfwidth_values):
        return None
    if not rows:
        return None
    if not _match_unique_int(rows, "wall_margin", int(args.ot_wall_margin)):
        return None
    if not _match_unique_float(rows, "delta_core", float(args.ot_delta_core)):
        return None
    if not _match_unique_float(rows, "delta_open", float(args.ot_delta_open)):
        return None
    start_vals = {int(r["start_x"]) for r in rows if r.get("start_x") is not None}
    target_vals = {int(r["target_x"]) for r in rows if r.get("target_x") is not None}
    if start_vals != {int(start_x)} or target_vals != {int(target_x)}:
        return None

    return rows


def try_reuse_ot_bias2d_scan(
    *,
    data_dir: Path,
    bx_values: Sequence[float],
    by_values: Sequence[float],
    Wy_ref: int,
    Lx: int,
    q: float,
    args: argparse.Namespace,
    start_x: int,
    target_x: int,
) -> Tuple[List[dict], np.ndarray, np.ndarray, np.ndarray] | None:
    csv_path = data_dir / "ot_scan_bias2d.csv"
    json_path = data_dir / "ot_scan_bias2d.json"
    if not (csv_path.exists() and json_path.exists()):
        return None
    try:
        info = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    meta = info.get("meta", {})
    if int(meta.get("Lx", -1)) != int(Lx):
        return None
    if not _float_close(float(meta.get("q", -1.0)), float(q)):
        return None
    if int(meta.get("Wy_ref", -1)) != int(Wy_ref):
        return None
    if int(meta.get("scan_t_max", -1)) != int(args.scan_t_max):
        return None
    if not _float_close(float(meta.get("scan_surv_tol", -1.0)), float(args.scan_surv_tol), tol=1e-18):
        return None
    if int(meta.get("start_x", -999)) != int(start_x):
        return None
    if int(meta.get("target_x", -999)) != int(target_x):
        return None
    if int(meta.get("corridor_halfwidth", -999)) != int(args.ot_corridor_halfwidth):
        return None
    if int(meta.get("wall_margin", -999)) != int(args.ot_wall_margin):
        return None
    if not _float_close(float(meta.get("delta_core", -1.0)), float(args.ot_delta_core)):
        return None
    if not _float_close(float(meta.get("delta_open", -1.0)), float(args.ot_delta_open)):
        return None

    bx_json = [float(v) for v in info.get("bx_values", [])]
    by_json = [float(v) for v in info.get("by_values", [])]
    if not _match_float_list(bx_json, [float(v) for v in bx_values]):
        return None
    if not _match_float_list(by_json, [float(v) for v in by_values]):
        return None

    try:
        rows = load_scan_rows_csv(csv_path)
    except Exception:
        return None
    if len(rows) != len(bx_values) * len(by_values):
        return None
    if not rows:
        return None
    if not _match_unique_int(rows, "Wy", int(Wy_ref)):
        return None
    if not _match_unique_int(rows, "corridor_halfwidth", int(args.ot_corridor_halfwidth)):
        return None
    if not _match_unique_int(rows, "wall_margin", int(args.ot_wall_margin)):
        return None
    if not _match_unique_float(rows, "delta_core", float(args.ot_delta_core)):
        return None
    if not _match_unique_float(rows, "delta_open", float(args.ot_delta_open)):
        return None
    start_vals = {int(r["start_x"]) for r in rows if r.get("start_x") is not None}
    target_vals = {int(r["target_x"]) for r in rows if r.get("target_x") is not None}
    if start_vals != {int(start_x)} or target_vals != {int(target_x)}:
        return None

    phase, sep, valley = build_ot_bias2d_grids(rows, bx_values=bx_values, by_values=by_values)
    return rows, phase, sep, valley


def resolve_x_token(x: int, *, Lx: int) -> int:
    """Resolve x tokens where negative values mean offset from the right boundary."""
    xv = int(x)
    if xv < 0:
        xv = int(Lx) + xv
    return max(0, min(int(Lx) - 1, int(xv)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 2D rectangle bimodality report assets.")
    parser.add_argument("--Lx", type=int, default=60)
    parser.add_argument("--q", type=float, default=0.8)
    parser.add_argument("--t-max", type=int, default=20000)
    parser.add_argument("--surv-tol", type=float, default=1e-13)
    parser.add_argument("--scan-t-max", type=int, default=5000)
    parser.add_argument("--scan-surv-tol", type=float, default=1e-10)
    parser.add_argument("--quick", action="store_true")

    # Two-target scan grid
    parser.add_argument("--tt-width-min", type=int, default=5)
    parser.add_argument("--tt-width-max", type=int, default=28)
    parser.add_argument("--tt-width-step", type=int, default=1)
    parser.add_argument(
        "--tt-critical-width-max",
        type=int,
        default=60,
        help="optional extended max Wy for branch-wise critical-width estimation",
    )
    parser.add_argument("--tt-xstart-min", type=int, default=6)
    parser.add_argument("--tt-xstart-max", type=int, default=22)
    parser.add_argument("--tt-xstart-step", type=int, default=2)
    parser.add_argument("--tt-style", type=str, default="straight", choices=["straight", "detour"])
    # Use one-cell-thick streams by default (the user can widen into a band).
    parser.add_argument("--tt-w-fast", type=int, default=0)
    parser.add_argument("--tt-w-slow", type=int, default=0)
    parser.add_argument("--tt-fast-skip", type=int, default=1)
    parser.add_argument("--tt-slow-skip", type=int, default=1)
    parser.add_argument("--tt-delta-fast", type=float, default=0.85)
    parser.add_argument("--tt-delta-slow", type=float, default=0.85)
    parser.add_argument("--tt-width-sweep-xstart", type=int, default=10)
    parser.add_argument("--tt-width-sweep-target-widths", type=str, default="5,6,7,8,14,24")

    # One-target corridor scan
    parser.add_argument("--ot-width-min", type=int, default=8)
    parser.add_argument("--ot-width-max", type=int, default=28)
    parser.add_argument("--ot-width-step", type=int, default=2)
    parser.add_argument("--ot-corridor-halfwidth", type=int, default=1)
    parser.add_argument(
        "--ot-corridor-halfwidth-values",
        type=str,
        default="0,1,2,3",
        help="additional corridor halfwidth values for thickness-sensitivity scan",
    )
    parser.add_argument("--ot-wall-margin", type=int, default=5)
    parser.add_argument("--ot-delta-core", type=float, default=0.95)
    parser.add_argument("--ot-delta-open", type=float, default=0.60)
    # Include stronger bx<0 values: with corridor local bias, these are the cases
    # most likely to produce a late channel and clear bimodality.
    parser.add_argument("--ot-global-bx-values", type=str, default="-0.12,-0.08,-0.04,0.0,0.08")
    parser.add_argument(
        "--ot-global-by-values",
        type=str,
        default="-0.08,-0.04,0.0,0.04,0.08",
        help="global by values for additional bias-vector scan",
    )
    parser.add_argument(
        "--ot-bias-scan-width",
        type=int,
        default=12,
        help="reference Wy used in additional (bx,by) bias-vector scan",
    )
    # One-target anchor placement (negative target x means offset from right boundary).
    parser.add_argument("--ot-start-x", type=int, default=1)
    parser.add_argument("--ot-target-x", type=int, default=-2)
    # Pre-scan candidates to auto-select a more informative start/target placement.
    parser.add_argument("--ot-start-x-candidates", type=str, default="1,3,5,7")
    parser.add_argument("--ot-target-x-candidates", type=str, default="-2,-4,-6")
    parser.add_argument("--ot-placement-width", type=int, default=12)
    parser.add_argument("--ot-placement-bx-values", type=str, default="-0.12,-0.08,-0.04")
    parser.set_defaults(reuse_scan_data=True)
    parser.add_argument("--reuse-scan-data", dest="reuse_scan_data", action="store_true")
    parser.add_argument("--no-reuse-scan-data", dest="reuse_scan_data", action="store_false")
    args = parser.parse_args()

    default_report_dir = Path(__file__).resolve().parents[4] / "reports" / "grid2d_rect_bimodality"
    report_dir = Path(os.environ.get("VK_REPORT_DIR", str(default_report_dir))).resolve()
    data_dir = report_dir / "data"
    fig_dir = report_dir / "figures"
    out_dir = report_dir / "outputs"
    table_dir = report_dir / "tables"
    for d in (data_dir, fig_dir, out_dir, table_dir):
        ensure_dir(d)
    purge_generated_artifacts(
        data_dir=data_dir,
        fig_dir=fig_dir,
        out_dir=out_dir,
        table_dir=table_dir,
        keep_scan_data=bool(args.reuse_scan_data),
    )

    Lx = int(args.Lx)
    q = float(args.q)
    if not (0.0 < q <= 1.0):
        raise ValueError("q must be in (0,1].")
    if Lx < 10:
        raise ValueError("Lx too small; need a long rectangle (>=10).")

    # Quick mode shrinks grids for iteration speed.
    if args.quick:
        args.scan_t_max = min(int(args.scan_t_max), 1200)
        args.t_max = min(int(args.t_max), 5000)
        args.tt_width_step = max(int(args.tt_width_step), 4)
        args.tt_xstart_step = max(int(args.tt_xstart_step), 4)
        args.ot_width_step = max(int(args.ot_width_step), 4)

    # ---- Shared legend ----
    plot_symbol_legend_panel(fig_dir / "symbol_legend_panel.pdf")

    # =========================
    # Part I: Two targets
    # =========================
    tt_widths = list(range(int(args.tt_width_min), int(args.tt_width_max) + 1, int(args.tt_width_step)))
    tt_xstarts = list(range(int(args.tt_xstart_min), int(args.tt_xstart_max) + 1, int(args.tt_xstart_step)))
    if not tt_widths or not tt_xstarts:
        raise ValueError("empty two-target scan grid")

    tt_phase = np.zeros((len(tt_widths), len(tt_xstarts)), dtype=np.int64)
    tt_sep = np.zeros_like(tt_phase, dtype=np.float64)
    tt_valley = np.zeros_like(tt_phase, dtype=np.float64)

    tt_rows: List[dict] = []
    tt_reused = False
    if bool(args.reuse_scan_data):
        tt_reused_data = try_reuse_tt_scan(
            data_dir=data_dir,
            widths=tt_widths,
            x_starts=tt_xstarts,
            Lx=Lx,
            q=q,
            args=args,
        )
        if tt_reused_data is not None:
            tt_rows, tt_phase, tt_sep, tt_valley = tt_reused_data
            tt_reused = True
            print("Reused two-target scan data from data/tt_scan_width_xstart.{csv,json}")

    if not tt_reused:
        for iW, Wy in enumerate(tt_widths):
            for jx, x0 in enumerate(tt_xstarts):
                spec = TTCaseSpec(
                    Wy=int(Wy),
                    x_start=int(x0),
                    w_fast=int(args.tt_w_fast),
                    w_slow=int(args.tt_w_slow),
                    fast_skip=int(args.tt_fast_skip),
                    slow_skip=int(args.tt_slow_skip),
                    delta_fast=float(args.tt_delta_fast),
                    delta_slow=float(args.tt_delta_slow),
                )
                start, m1, m2, fast_path, slow_path, local_bias_map, _, _, _ = build_tt_case_geometry(
                    Lx=Lx,
                    Wy=spec.Wy,
                    x_start=spec.x_start,
                    w_fast=spec.w_fast,
                    w_slow=spec.w_slow,
                    fast_skip=spec.fast_skip,
                    slow_skip=spec.slow_skip,
                    delta_fast=spec.delta_fast,
                    delta_slow=spec.delta_slow,
                    style=str(args.tt_style),
                )

                src_idx, dst_idx, probs = build_transition_arrays_general_rect(
                    Lx=Lx,
                    Wy=spec.Wy,
                    q=q,
                    local_bias_map=local_bias_map,
                    sticky_map={},
                    barrier_map={},
                    long_range_map={},
                    global_bias=(0.0, 0.0),
                )
                f_any, f_m1, f_m2, surv = run_exact_two_target_rect(
                    Lx=Lx,
                    Wy=spec.Wy,
                    start=start,
                    target1=m1,
                    target2=m2,
                    src_idx=src_idx,
                    dst_idx=dst_idx,
                    probs=probs,
                    t_max=int(args.scan_t_max),
                    surv_tol=float(args.scan_surv_tol),
                )
                validate_tt_series_consistency(case_id=spec.case_id, f_any=f_any, f_m1=f_m1, f_m2=f_m2, surv=surv)
                res = summarize_two_target(spec, f_any, f_m1, f_m2, surv)
                tt_phase[iW, jx] = int(res.phase)
                tt_sep[iW, jx] = float(res.sep_mode_width)
                tt_valley[iW, jx] = float(res.valley_over_max if res.valley_over_max is not None else 1.0)

                tt_rows.append(
                    {
                        "Wy": int(spec.Wy),
                        "x_start": int(spec.x_start),
                        "w_fast": int(spec.w_fast),
                        "w_slow": int(spec.w_slow),
                        "fast_skip": int(spec.fast_skip),
                        "slow_skip": int(spec.slow_skip),
                        "delta_fast": float(spec.delta_fast),
                        "delta_slow": float(spec.delta_slow),
                        "phase": int(res.phase),
                        "sep_mode_width": float(res.sep_mode_width),
                        "peak_ratio": (None if res.peak_ratio is None else float(res.peak_ratio)),
                        "valley_over_max": (None if res.valley_over_max is None else float(res.valley_over_max)),
                        "t_peak1": res.t_peak1,
                        "t_peak2": res.t_peak2,
                        "p_m1": float(res.p_m1),
                        "p_m2": float(res.p_m2),
                        "t_mode_m1": int(res.t_mode_m1),
                        "t_mode_m2": int(res.t_mode_m2),
                        "absorbed_mass": float(res.absorbed_mass),
                        "survival_tail": float(res.survival_tail),
                    }
                )

        # Save scan outputs
        tt_csv = data_dir / "tt_scan_width_xstart.csv"
        with tt_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(tt_rows[0].keys()))
            writer.writeheader()
            writer.writerows(tt_rows)
        (data_dir / "tt_scan_width_xstart.json").write_text(
            json.dumps(
                {
                    "meta": {
                        "Lx": Lx,
                        "q": q,
                        "tt_style": str(args.tt_style),
                        "scan_t_max": int(args.scan_t_max),
                        "scan_surv_tol": float(args.scan_surv_tol),
                        "t_max": int(args.t_max),
                        "surv_tol": float(args.surv_tol),
                    },
                    "widths": tt_widths,
                    "x_starts": tt_xstarts,
                    "phase_grid": tt_phase.tolist(),
                    "sep_grid": tt_sep.tolist(),
                    "valley_grid": tt_valley.tolist(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    plot_phase_map(
        fig_dir / "tt_phase_width_xstart.pdf",
        phase=tt_phase,
        x_ticks=tt_xstarts,
        y_ticks=tt_widths,
        xlabel="x_start",
        ylabel="Wy (rectangle width)",
        title="Two-target phase map (width vs start position)",
    )
    plot_scalar_map(
        fig_dir / "tt_sep_width_xstart.pdf",
        arr=tt_sep,
        x_ticks=tt_xstarts,
        y_ticks=tt_widths,
        xlabel="x_start",
        ylabel="Wy",
        title=r"Two-target separation map: $|\Delta t^*|/(w_{1/2}^{(1)}+w_{1/2}^{(2)})$",
        cbar_label="sep-score",
    )
    plot_scalar_map(
        fig_dir / "tt_valley_width_xstart.pdf",
        arr=tt_valley,
        x_ticks=tt_xstarts,
        y_ticks=tt_widths,
        xlabel="x_start",
        ylabel="Wy",
        title=r"Two-target valley depth: $p_v/\max(p_1,p_2)$",
        cbar_label="valley/max",
        cmap="magma",
    )
    render_tt_scan_overview(tt_rows, table_dir / "tt_scan_overview.tex")

    # Branch-wise critical-width extension: keep the main map compact while extending
    # selected x0 branches to find where clear-double actually disappears.
    critical_branches = (8, 10, 12)
    tt_critical_rows: List[dict] = list(tt_rows)
    max_scan_w = max(tt_widths)
    critical_w_max = int(max(args.tt_critical_width_max, max_scan_w))
    if critical_w_max > max_scan_w:
        width_step_ext = max(1, int(args.tt_width_step))
        x_valid = {int(x) for x in tt_xstarts}
        for Wy in range(int(max_scan_w) + width_step_ext, int(critical_w_max) + 1, width_step_ext):
            for x0 in critical_branches:
                if int(x0) not in x_valid:
                    continue
                spec = TTCaseSpec(
                    Wy=int(Wy),
                    x_start=int(x0),
                    w_fast=int(args.tt_w_fast),
                    w_slow=int(args.tt_w_slow),
                    fast_skip=int(args.tt_fast_skip),
                    slow_skip=int(args.tt_slow_skip),
                    delta_fast=float(args.tt_delta_fast),
                    delta_slow=float(args.tt_delta_slow),
                )
                start, m1, m2, fast_path, slow_path, local_bias_map, arrow_map, fast_cells, slow_cells = build_tt_case_geometry(
                    Lx=Lx,
                    Wy=spec.Wy,
                    x_start=spec.x_start,
                    w_fast=spec.w_fast,
                    w_slow=spec.w_slow,
                    fast_skip=spec.fast_skip,
                    slow_skip=spec.slow_skip,
                    delta_fast=spec.delta_fast,
                    delta_slow=spec.delta_slow,
                    style=str(args.tt_style),
                )
                src_idx, dst_idx, probs = build_transition_arrays_general_rect(
                    Lx=Lx,
                    Wy=spec.Wy,
                    q=q,
                    local_bias_map=local_bias_map,
                    sticky_map={},
                    barrier_map={},
                    long_range_map={},
                    global_bias=(0.0, 0.0),
                )
                f_any, f_m1, f_m2, surv = run_exact_two_target_rect(
                    Lx=Lx,
                    Wy=spec.Wy,
                    start=start,
                    target1=m1,
                    target2=m2,
                    src_idx=src_idx,
                    dst_idx=dst_idx,
                    probs=probs,
                    t_max=int(args.scan_t_max),
                    surv_tol=float(args.scan_surv_tol),
                )
                validate_tt_series_consistency(case_id=spec.case_id, f_any=f_any, f_m1=f_m1, f_m2=f_m2, surv=surv)
                res = summarize_two_target(spec, f_any, f_m1, f_m2, surv)
                tt_critical_rows.append(
                    {
                        "Wy": int(spec.Wy),
                        "x_start": int(spec.x_start),
                        "w_fast": int(spec.w_fast),
                        "w_slow": int(spec.w_slow),
                        "fast_skip": int(spec.fast_skip),
                        "slow_skip": int(spec.slow_skip),
                        "delta_fast": float(spec.delta_fast),
                        "delta_slow": float(spec.delta_slow),
                        "phase": int(res.phase),
                        "sep_mode_width": float(res.sep_mode_width),
                        "peak_ratio": (None if res.peak_ratio is None else float(res.peak_ratio)),
                        "valley_over_max": (None if res.valley_over_max is None else float(res.valley_over_max)),
                        "t_peak1": res.t_peak1,
                        "t_peak2": res.t_peak2,
                        "p_m1": float(res.p_m1),
                        "p_m2": float(res.p_m2),
                        "t_mode_m1": int(res.t_mode_m1),
                        "t_mode_m2": int(res.t_mode_m2),
                    }
                )

    render_tt_critical_width_table(tt_critical_rows, table_dir / "tt_critical_width_by_xstart.tex", branches=critical_branches)
    plot_tt_critical_vs_xstart(fig_dir / "tt_critical_vs_xstart.pdf", rows=tt_critical_rows, branches=critical_branches)

    # Representative runs (long t_max + detailed plots)
    tt_rep_specs = pick_representatives_tt(tt_rows, max_total=6)
    validate_tt_representative_branch_coverage(
        tt_rows=tt_rows,
        tt_rep_specs=tt_rep_specs,
        key_branches=critical_branches,
    )
    tt_rep_results: List[TTCaseResult] = []
    tt_series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    tt_layouts: Dict[str, dict] = {}

    tt_heat_paths: Dict[str, Path] = {}
    for k_rep, spec in enumerate(tt_rep_specs):
        start, m1, m2, fast_path, slow_path, local_bias_map, arrow_map, fast_cells, slow_cells = build_tt_case_geometry(
            Lx=Lx,
            Wy=spec.Wy,
            x_start=spec.x_start,
            w_fast=spec.w_fast,
            w_slow=spec.w_slow,
            fast_skip=spec.fast_skip,
            slow_skip=spec.slow_skip,
            delta_fast=spec.delta_fast,
            delta_slow=spec.delta_slow,
            style=str(args.tt_style),
        )
        src_idx, dst_idx, probs = build_transition_arrays_general_rect(
            Lx=Lx,
            Wy=spec.Wy,
            q=q,
            local_bias_map=local_bias_map,
            sticky_map={},
            barrier_map={},
            long_range_map={},
            global_bias=(0.0, 0.0),
        )
        f_any, f_m1, f_m2, surv = run_exact_two_target_rect(
            Lx=Lx,
            Wy=spec.Wy,
            start=start,
            target1=m1,
            target2=m2,
            src_idx=src_idx,
            dst_idx=dst_idx,
            probs=probs,
            t_max=int(args.t_max),
            surv_tol=float(args.surv_tol),
        )
        validate_tt_series_consistency(case_id=spec.case_id, f_any=f_any, f_m1=f_m1, f_m2=f_m2, surv=surv)
        res = summarize_two_target(spec, f_any, f_m1, f_m2, surv)
        tt_rep_results.append(res)
        tt_series_map[spec.case_id] = (f_any, f_m1, f_m2, surv)
        tt_layouts[spec.case_id] = {
            "Wy": int(spec.Wy),
            "start": start,
            "m1": m1,
            "m2": m2,
            "fast_path": fast_path,
            "slow_path": slow_path,
            "fast_cells": fast_cells,
            "slow_cells": slow_cells,
            "arrow_map": arrow_map,
            "fast_skip": int(spec.fast_skip),
            "slow_skip": int(spec.slow_skip),
        }

        # time-series csv
        out_csv = out_dir / f"{spec.case_id}_fpt.csv"
        with out_csv.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["t", "f_any", "f_m1_first", "f_m2_first", "survival"])
            for t in range(len(f_any)):
                w.writerow([t, f_any[t], f_m1[t], f_m2[t], surv[t]])

        # geometry + fpt
        fig_geo = fig_dir / f"{spec.case_id}_geometry.pdf"
        fig_fpt = fig_dir / f"{spec.case_id}_fpt.pdf"
        fig_heat = fig_dir / f"{spec.case_id}_env_heatmap.pdf"

        fig, ax = plt.subplots(figsize=(7.8, 4.6))
        _draw_environment_tt(
            ax,
            Lx=Lx,
            Wy=spec.Wy,
            fast_cells=fast_cells,
            slow_cells=slow_cells,
            start=start,
            m1=m1,
            m2=m2,
            fast_path=fast_path,
            slow_path=slow_path,
            fast_skip=spec.fast_skip,
            slow_skip=spec.slow_skip,
            title=f"{spec.case_id}: Wy={spec.Wy}, x0={spec.x_start}",
            draw_paths=False,
            draw_turns=False,
            arrow_map=arrow_map,
        )
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            wanted = ["start", "m1", "m2"]
            hl = {lab: h for h, lab in zip(handles, labels)}
            sel_h = [hl[k] for k in wanted if k in hl]
            sel_l = [k for k in wanted if k in hl]
            if sel_h:
                ax.legend(sel_h, sel_l, loc="upper right", fontsize=8, frameon=True)
        fig.tight_layout()
        fig.savefig(fig_geo)
        plt.close(fig)

        plot_tt_fpt(fig_fpt, f_any=f_any, f_m1=f_m1, f_m2=f_m2, res=res)

        heat_times = choose_heat_times(res.t_peak1, res.t_valley, res.t_peak2)
        snaps = conditional_snapshots_two_target_rect(
            Lx=Lx,
            Wy=spec.Wy,
            start=start,
            target1=m1,
            target2=m2,
            src_idx=src_idx,
            dst_idx=dst_idx,
            probs=probs,
            times=heat_times,
        )
        plot_tt_env_heatmaps(
            fig_heat,
            Lx=Lx,
            Wy=spec.Wy,
            start=start,
            m1=m1,
            m2=m2,
            fast_cells=fast_cells,
            slow_cells=slow_cells,
            fast_path=fast_path,
            slow_path=slow_path,
            fast_skip=spec.fast_skip,
            slow_skip=spec.slow_skip,
            case_title=f"{spec.case_id}: Wy={spec.Wy}, x0={spec.x_start}",
            snapshots=snaps,
            heat_times=heat_times,
            arrow_map=arrow_map,
        )
        tt_heat_paths[spec.case_id] = fig_heat

    # Pick two heatmap examples with stronger contrast:
    # A = strongest separation; B = strongest with different geometry branch if possible.
    if tt_rep_results:
        ranked = sorted(
            tt_rep_results,
            key=lambda r: (
                -float(r.sep_mode_width),
                -float(min(r.p_m1, r.p_m2)),
                float(r.valley_over_max if r.valley_over_max is not None else 1.0),
            ),
        )
        case_a_res = ranked[0]
        case_a = case_a_res.spec.case_id

        case_b = case_a
        best_b_score: Tuple[int, float] | None = None
        for r in ranked[1:]:
            diff = int(r.spec.x_start != case_a_res.spec.x_start) + int(r.spec.Wy != case_a_res.spec.Wy)
            score = (diff, float(r.sep_mode_width))
            if best_b_score is None or score > best_b_score:
                best_b_score = score
                case_b = r.spec.case_id
        if case_b == case_a and len(ranked) > 1:
            case_b = ranked[1].spec.case_id
        if case_a in tt_heat_paths:
            shutil.copyfile(tt_heat_paths[case_a], fig_dir / "tt_repA_env_heatmap.pdf")
        if case_b in tt_heat_paths:
            shutil.copyfile(tt_heat_paths[case_b], fig_dir / "tt_repB_env_heatmap.pdf")

    render_tt_representative_table(tt_rep_results, table_dir / "tt_representative_metrics.tex")
    plot_tt_hazard_grid(fig_dir / "tt_hazard_grid.pdf", reps=tt_rep_results, series_map=tt_series_map)
    plot_tt_rep_geometry_grid(
        fig_dir / "tt_representative_geometry_grid.pdf",
        Lx=Lx,
        layouts=tt_layouts,
        reps=tt_rep_results,
    )
    plot_tt_rep_fpt_grid(
        fig_dir / "tt_representative_fpt_grid.pdf",
        reps=tt_rep_results,
        series_map=tt_series_map,
    )

    # Width-focused set on a fixed x0 branch: show how bimodality changes and where clear-double is lost.
    tt_width_targets = parse_int_list(args.tt_width_sweep_target_widths) or [5, 6, 7, 8, 14, 24]
    tt_width_seed_specs = pick_clear_width_sweep_tt(
        tt_rows,
        target_widths=tuple(int(w) for w in tt_width_targets),
        preferred_xstart=int(args.tt_width_sweep_xstart),
        min_phase=0,
    )
    tt_width_specs: List[TTCaseSpec] = []
    tt_width_results: List[TTCaseResult] = []
    tt_width_series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    tt_width_layouts: Dict[str, dict] = {}

    for spec in tt_width_seed_specs:
        start, m1, m2, fast_path, slow_path, local_bias_map, arrow_map, fast_cells, slow_cells = build_tt_case_geometry(
            Lx=Lx,
            Wy=spec.Wy,
            x_start=spec.x_start,
            w_fast=spec.w_fast,
            w_slow=spec.w_slow,
            fast_skip=spec.fast_skip,
            slow_skip=spec.slow_skip,
            delta_fast=spec.delta_fast,
            delta_slow=spec.delta_slow,
            style=str(args.tt_style),
        )
        src_idx, dst_idx, probs = build_transition_arrays_general_rect(
            Lx=Lx,
            Wy=spec.Wy,
            q=q,
            local_bias_map=local_bias_map,
            sticky_map={},
            barrier_map={},
            long_range_map={},
            global_bias=(0.0, 0.0),
        )
        f_any, f_m1, f_m2, surv = run_exact_two_target_rect(
            Lx=Lx,
            Wy=spec.Wy,
            start=start,
            target1=m1,
            target2=m2,
            src_idx=src_idx,
            dst_idx=dst_idx,
            probs=probs,
            t_max=int(args.t_max),
            surv_tol=float(args.surv_tol),
        )
        validate_tt_series_consistency(case_id=spec.case_id, f_any=f_any, f_m1=f_m1, f_m2=f_m2, surv=surv)
        res = summarize_two_target(spec, f_any, f_m1, f_m2, surv)
        tt_width_specs.append(spec)
        tt_width_results.append(res)
        tt_width_series_map[spec.case_id] = (f_any, f_m1, f_m2, surv)
        tt_width_layouts[spec.case_id] = {
            "Wy": int(spec.Wy),
            "start": start,
            "m1": m1,
            "m2": m2,
            "fast_path": fast_path,
            "slow_path": slow_path,
            "fast_cells": fast_cells,
            "slow_cells": slow_cells,
            "arrow_map": arrow_map,
            "fast_skip": int(spec.fast_skip),
            "slow_skip": int(spec.slow_skip),
        }

    if tt_width_results:
        validate_tt_width_sweep_transition(tt_width_results)
        render_tt_width_sweep_table(tt_width_results, table_dir / "tt_width_sweep_metrics.tex")
        plot_tt_rep_geometry_grid(
            fig_dir / "tt_width_sweep_geometry_grid.pdf",
            Lx=Lx,
            layouts=tt_width_layouts,
            reps=tt_width_results,
        )
        plot_tt_rep_fpt_grid(
            fig_dir / "tt_width_sweep_fpt_grid.pdf",
            reps=tt_width_results,
            series_map=tt_width_series_map,
        )
        plot_tt_width_sweep_trend(
            fig_dir / "tt_width_sweep_trend.pdf",
            results=tt_width_results,
        )

    # =========================
    # Part II: One target corridor
    # =========================
    ot_widths = list(range(int(args.ot_width_min), int(args.ot_width_max) + 1, int(args.ot_width_step)))
    bx_values = parse_float_list(args.ot_global_bx_values)
    by_values = parse_float_list(args.ot_global_by_values)
    if not ot_widths or not bx_values or not by_values:
        raise ValueError("empty one-target scan grid")

    placement_w_target = int(args.ot_placement_width)
    ot_phase = np.zeros((len(ot_widths), len(bx_values)), dtype=np.int64)
    ot_valley = np.zeros_like(ot_phase, dtype=np.float64)
    ot_sep = np.zeros_like(ot_phase, dtype=np.float64)
    ot_rows: List[dict] = []
    best_anchor: dict | None = None
    ot_start_x = resolve_x_token(int(args.ot_start_x), Lx=Lx)
    ot_target_x = resolve_x_token(int(args.ot_target_x), Lx=Lx)
    ot_reused = False

    if bool(args.reuse_scan_data):
        ot_reused_data = try_reuse_ot_scan(
            data_dir=data_dir,
            widths=ot_widths,
            bx_values=bx_values,
            placement_width=placement_w_target,
            Lx=Lx,
            q=q,
            args=args,
        )
        if ot_reused_data is not None:
            ot_rows, ot_phase, ot_sep, ot_valley, ot_start_x, ot_target_x, best_anchor = ot_reused_data
            ot_reused = True
            print("Reused one-target scan data from data/ot_scan_width_globalbias.{csv,json}")

    if not ot_reused:
        # --- Anchor placement pre-scan (start/target) ---
        # We first test a small candidate set, then lock one placement and vary width/bx.
        start_cands_raw = parse_int_list(args.ot_start_x_candidates)
        target_cands_raw = parse_int_list(args.ot_target_x_candidates)
        start_cands = sorted({resolve_x_token(v, Lx=Lx) for v in (start_cands_raw or [int(args.ot_start_x)])})
        target_cands = sorted({resolve_x_token(v, Lx=Lx) for v in (target_cands_raw or [int(args.ot_target_x)])})
        placement_bx_values = parse_float_list(args.ot_placement_bx_values) or list(bx_values)
        # Evaluate anchor robustness on a compact width bundle around the reference width.
        placement_ws = sorted(
            {
                int(min(ot_widths, key=lambda w: (abs(int(w) - int(wt)), int(w))))
                for wt in (placement_w_target - 4, placement_w_target, placement_w_target + 4)
            }
        )
        placement_w = min(ot_widths, key=lambda w: (abs(int(w) - placement_w_target), int(w)))

        for sx in start_cands:
            for tx in target_cands:
                # Keep enough longitudinal distance so two timescales can separate.
                if int(tx) - int(sx) < 10:
                    continue

                per_width_best: Dict[int, dict] = {}
                for Wy_ref in placement_ws:
                    best_case_w: dict | None = None
                    for bx in placement_bx_values:
                        spec_a = OTCaseSpec(
                            Wy=int(Wy_ref),
                            bx=float(bx),
                            corridor_halfwidth=int(args.ot_corridor_halfwidth),
                            wall_margin=int(args.ot_wall_margin),
                            delta_core=float(args.ot_delta_core),
                            delta_open=float(args.ot_delta_open),
                        )
                        start_a, tgt_a, local_bias_a, barrier_a, corridor_mask_a, _ = build_ot_case_geometry(
                            Lx=Lx,
                            Wy=spec_a.Wy,
                            corridor_halfwidth=spec_a.corridor_halfwidth,
                            wall_margin=spec_a.wall_margin,
                            delta_core=spec_a.delta_core,
                            delta_open=spec_a.delta_open,
                            start_x=int(sx),
                            target_x=int(tx),
                        )
                        src_a, dst_a, prob_a = build_transition_arrays_general_rect(
                            Lx=Lx,
                            Wy=spec_a.Wy,
                            q=q,
                            local_bias_map=local_bias_a,
                            sticky_map={},
                            barrier_map=barrier_a,
                            long_range_map={},
                            global_bias=(spec_a.bx, 0.0),
                        )
                        f_a, f_a_ch1, f_a_ch2, surv_a = run_exact_one_target_rect(
                            Lx=Lx,
                            Wy=spec_a.Wy,
                            start=start_a,
                            target=tgt_a,
                            src_idx=src_a,
                            dst_idx=dst_a,
                            probs=prob_a,
                            t_max=int(args.scan_t_max),
                            surv_tol=float(args.scan_surv_tol),
                            channel_mask=corridor_mask_a,
                        )
                        validate_ot_series_consistency(
                            case_id=spec_a.case_id,
                            f_total=f_a,
                            f_corr=f_a_ch1,
                            f_outer=f_a_ch2,
                            surv=surv_a,
                        )
                        res_a = summarize_one_target(spec_a, f_a, surv_a)
                        valley_a = float(res_a.valley_over_max) if res_a.valley_over_max is not None else 1.0
                        bal_a = float(res_a.peak_balance) if res_a.peak_balance is not None else 0.0
                        score_case = (int(res_a.phase), float(res_a.sep_peaks), -valley_a, bal_a, -abs(float(bx)))
                        cand_case = {
                            "score_case": score_case,
                            "start_x": int(sx),
                            "target_x": int(tx),
                            "bx": float(bx),
                            "phase": int(res_a.phase),
                            "sep_peaks": float(res_a.sep_peaks),
                            "valley_over_max": (None if res_a.valley_over_max is None else float(res_a.valley_over_max)),
                            "peak_balance": (None if res_a.peak_balance is None else float(res_a.peak_balance)),
                            "t_peak1": res_a.t_peak1,
                            "t_peak2": res_a.t_peak2,
                            "Wy_ref": int(Wy_ref),
                        }
                        if best_case_w is None or cand_case["score_case"] > best_case_w["score_case"]:
                            best_case_w = cand_case
                    if best_case_w is not None:
                        per_width_best[int(Wy_ref)] = best_case_w

                if not per_width_best:
                    continue
                perw_vals = list(per_width_best.values())
                n_phase2 = int(sum(int(v["phase"]) >= 2 for v in perw_vals))
                n_phase1p = int(sum(int(v["phase"]) >= 1 for v in perw_vals))
                sep_vals = [float(v["sep_peaks"]) for v in perw_vals if int(v["phase"]) >= 1]
                bal_vals = [float(v["peak_balance"]) for v in perw_vals if v.get("peak_balance") is not None]
                valley_vals = [float(v["valley_over_max"]) for v in perw_vals if v.get("valley_over_max") is not None]
                anchor_score = (
                    n_phase2,
                    n_phase1p,
                    float(np.mean(sep_vals)) if sep_vals else 0.0,
                    float(np.mean(bal_vals)) if bal_vals else 0.0,
                    -float(np.mean(valley_vals)) if valley_vals else -1.0,
                    int(tx) - int(sx),
                )

                ref_case = per_width_best.get(int(placement_w))
                if ref_case is None:
                    ref_case = max(perw_vals, key=lambda v: v["score_case"])
                cand = dict(ref_case)
                cand.update(
                    {
                        "score": anchor_score,
                        "phase2_count": n_phase2,
                        "phase1plus_count": n_phase1p,
                        "placement_widths": [int(w) for w in placement_ws],
                    }
                )
                if best_anchor is None or cand["score"] > best_anchor["score"]:
                    best_anchor = cand

        if best_anchor is None:
            ot_start_x = resolve_x_token(int(args.ot_start_x), Lx=Lx)
            ot_target_x = resolve_x_token(int(args.ot_target_x), Lx=Lx)
            if ot_target_x - ot_start_x < 10:
                ot_start_x, ot_target_x = 1, Lx - 2
            best_anchor = {
                "score": (0, 0.0, -1.0, 0.0, 0.0),
                "start_x": int(ot_start_x),
                "target_x": int(ot_target_x),
                "bx": float(bx_values[0]),
                "phase": 0,
                "sep_peaks": 0.0,
                "valley_over_max": None,
                "peak_balance": None,
                "t_peak1": None,
                "t_peak2": None,
                "Wy_ref": int(placement_w),
                "phase2_count": 0,
                "phase1plus_count": 0,
                "placement_widths": [int(w) for w in placement_ws],
            }
        else:
            ot_start_x = int(best_anchor["start_x"])
            ot_target_x = int(best_anchor["target_x"])

        for iW, Wy in enumerate(ot_widths):
            for j, bx in enumerate(bx_values):
                spec = OTCaseSpec(
                    Wy=int(Wy),
                    bx=float(bx),
                    corridor_halfwidth=int(args.ot_corridor_halfwidth),
                    wall_margin=int(args.ot_wall_margin),
                    delta_core=float(args.ot_delta_core),
                    delta_open=float(args.ot_delta_open),
                )
                start, tgt, local_bias_map, barrier_map, corridor_mask, wall_span = build_ot_case_geometry(
                    Lx=Lx,
                    Wy=spec.Wy,
                    corridor_halfwidth=spec.corridor_halfwidth,
                    wall_margin=spec.wall_margin,
                    delta_core=spec.delta_core,
                    delta_open=spec.delta_open,
                    start_x=int(ot_start_x),
                    target_x=int(ot_target_x),
                )
                src_idx, dst_idx, probs = build_transition_arrays_general_rect(
                    Lx=Lx,
                    Wy=spec.Wy,
                    q=q,
                    local_bias_map=local_bias_map,
                    sticky_map={},
                    barrier_map=barrier_map,
                    long_range_map={},
                    global_bias=(spec.bx, 0.0),
                )
                f, f_ch1_scan, f_ch2_scan, surv = run_exact_one_target_rect(
                    Lx=Lx,
                    Wy=spec.Wy,
                    start=start,
                    target=tgt,
                    src_idx=src_idx,
                    dst_idx=dst_idx,
                    probs=probs,
                    # Use the long-horizon settings here so peak widths (and therefore the
                    # separation score) are not artificially inflated by truncation.
                    t_max=int(args.t_max),
                    surv_tol=float(args.surv_tol),
                    channel_mask=None,
                )
                validate_ot_series_consistency(
                    case_id=spec.case_id,
                    f_total=f,
                    f_corr=f_ch1_scan,
                    f_outer=f_ch2_scan,
                    surv=surv,
                )
                res = summarize_one_target(spec, f, surv)
                ot_phase[iW, j] = int(res.phase)
                ot_valley[iW, j] = float(res.valley_over_max if res.valley_over_max is not None else 1.0)
                ot_sep[iW, j] = float(res.sep_peaks)

                ot_rows.append(
                    {
                        "Wy": int(spec.Wy),
                        "bx": float(spec.bx),
                        "start_x": int(ot_start_x),
                        "target_x": int(ot_target_x),
                        "corridor_halfwidth": int(spec.corridor_halfwidth),
                        "wall_margin": int(spec.wall_margin),
                        "delta_core": float(spec.delta_core),
                        "delta_open": float(spec.delta_open),
                        "phase": int(res.phase),
                        "sep_peaks": float(res.sep_peaks),
                        "valley_over_max": (None if res.valley_over_max is None else float(res.valley_over_max)),
                        "t_peak1": res.t_peak1,
                        "t_peak2": res.t_peak2,
                        "absorbed_mass": float(res.absorbed_mass),
                        "survival_tail": float(res.survival_tail),
                    }
                )

        ot_csv = data_dir / "ot_scan_width_globalbias.csv"
        with ot_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(ot_rows[0].keys()))
            writer.writeheader()
            writer.writerows(ot_rows)
        (data_dir / "ot_scan_width_globalbias.json").write_text(
            json.dumps(
                {
                    "meta": {
                        "Lx": Lx,
                        "q": q,
                        "bx_values": bx_values,
                        "scan_t_max": int(args.scan_t_max),
                        "scan_surv_tol": float(args.scan_surv_tol),
                        "t_max": int(args.t_max),
                        "surv_tol": float(args.surv_tol),
                    },
                    "widths": ot_widths,
                    "phase_grid": ot_phase.tolist(),
                    "sep_grid": ot_sep.tolist(),
                    "valley_grid": ot_valley.tolist(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    plot_phase_map(
        fig_dir / "ot_phase_width_bx.pdf",
        phase=ot_phase,
        x_ticks=bx_values,
        y_ticks=ot_widths,
        xlabel="bx",
        ylabel="Wy",
        title=f"One-target corridor phase map (x_s={ot_start_x}, x_t={ot_target_x})",
    )
    plot_scalar_map(
        fig_dir / "ot_sep_width_bx.pdf",
        arr=ot_sep,
        x_ticks=bx_values,
        y_ticks=ot_widths,
        xlabel="bx",
        ylabel="Wy",
        title=rf"One-target separation map (x_s={ot_start_x}, x_t={ot_target_x})",
        cbar_label="sep-score",
    )

    # Valley ratio vs width (line plot)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for j, bx in enumerate(bx_values):
        ax.plot(ot_widths, ot_valley[:, j], marker="o", ms=3.5, lw=1.3, label=f"bx={bx:.3f}")
    ax.set_xlabel("Wy (rectangle width)")
    ax.set_ylabel("valley/max")
    ax.set_title(f"One-target valley depth vs width (x_s={ot_start_x}, x_t={ot_target_x})")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(fig_dir / "ot_valley_vs_width.pdf")
    plt.close(fig)

    render_ot_scan_overview(ot_rows, table_dir / "ot_scan_overview.tex")
    render_ot_anchor_table(
        ot_rows,
        table_dir / "ot_anchor_selection.tex",
        start_x=int(ot_start_x),
        target_x=int(ot_target_x),
        bx_ref=float(best_anchor["bx"]),
        wy_ref=int(best_anchor["Wy_ref"]),
        phase_ref=int(best_anchor["phase"]),
    )

    # Additional one-target scan: corridor thickness sensitivity at the fixed anchor.
    ot_corridor_halfwidth_values = sorted({max(0, int(v)) for v in (parse_int_list(args.ot_corridor_halfwidth_values) or [0, 1, 2, 3])})
    if int(args.ot_corridor_halfwidth) not in ot_corridor_halfwidth_values:
        ot_corridor_halfwidth_values.append(int(args.ot_corridor_halfwidth))
        ot_corridor_halfwidth_values = sorted(set(ot_corridor_halfwidth_values))
    if not ot_corridor_halfwidth_values:
        ot_corridor_halfwidth_values = [max(0, int(args.ot_corridor_halfwidth))]

    ot_corridor_rows: List[dict] = []
    ot_corridor_reused = False
    if bool(args.reuse_scan_data):
        reused_rows = try_reuse_ot_corridor_scan(
            data_dir=data_dir,
            widths=ot_widths,
            bx_values=bx_values,
            corridor_halfwidth_values=ot_corridor_halfwidth_values,
            Lx=Lx,
            q=q,
            args=args,
            start_x=int(ot_start_x),
            target_x=int(ot_target_x),
        )
        if reused_rows is not None:
            ot_corridor_rows = reused_rows
            ot_corridor_reused = True
            print("Reused one-target corridor-width scan data from data/ot_scan_corridor_halfwidth.{csv,json}")

    if not ot_corridor_reused:
        for h in ot_corridor_halfwidth_values:
            for Wy in ot_widths:
                start_h, tgt_h, local_bias_h, barrier_h, corridor_mask_h, _ = build_ot_case_geometry(
                    Lx=Lx,
                    Wy=int(Wy),
                    corridor_halfwidth=int(h),
                    wall_margin=int(args.ot_wall_margin),
                    delta_core=float(args.ot_delta_core),
                    delta_open=float(args.ot_delta_open),
                    start_x=int(ot_start_x),
                    target_x=int(ot_target_x),
                )
                for bx in bx_values:
                    src_h, dst_h, probs_h = build_transition_arrays_general_rect(
                        Lx=Lx,
                        Wy=int(Wy),
                        q=q,
                        local_bias_map=local_bias_h,
                        sticky_map={},
                        barrier_map=barrier_h,
                        long_range_map={},
                        global_bias=(float(bx), 0.0),
                    )
                    f_h, f_ch1_h, f_ch2_h, surv_h = run_exact_one_target_rect(
                        Lx=Lx,
                        Wy=int(Wy),
                        start=start_h,
                        target=tgt_h,
                        src_idx=src_h,
                        dst_idx=dst_h,
                        probs=probs_h,
                        t_max=int(args.scan_t_max),
                        surv_tol=float(args.scan_surv_tol),
                        channel_mask=corridor_mask_h,
                    )
                    spec_h = OTCaseSpec(
                        Wy=int(Wy),
                        bx=float(bx),
                        corridor_halfwidth=int(h),
                        wall_margin=int(args.ot_wall_margin),
                        delta_core=float(args.ot_delta_core),
                        delta_open=float(args.ot_delta_open),
                    )
                    validate_ot_series_consistency(
                        case_id=f"{spec_h.case_id}_corridor_h{int(h)}",
                        f_total=f_h,
                        f_corr=f_ch1_h,
                        f_outer=f_ch2_h,
                        surv=surv_h,
                    )
                    res_h = summarize_one_target(spec_h, f_h, surv_h)
                    ot_corridor_rows.append(
                        {
                            "Wy": int(Wy),
                            "bx": float(bx),
                            "corridor_halfwidth": int(h),
                            "corridor_band_width": int(2 * int(h) + 1),
                            "start_x": int(ot_start_x),
                            "target_x": int(ot_target_x),
                            "wall_margin": int(args.ot_wall_margin),
                            "delta_core": float(args.ot_delta_core),
                            "delta_open": float(args.ot_delta_open),
                            "phase": int(res_h.phase),
                            "sep_peaks": float(res_h.sep_peaks),
                            "valley_over_max": (None if res_h.valley_over_max is None else float(res_h.valley_over_max)),
                            "t_peak1": res_h.t_peak1,
                            "t_peak2": res_h.t_peak2,
                            "absorbed_mass": float(res_h.absorbed_mass),
                            "survival_tail": float(res_h.survival_tail),
                        }
                    )

        ot_corridor_csv = data_dir / "ot_scan_corridor_halfwidth.csv"
        with ot_corridor_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(ot_corridor_rows[0].keys()))
            writer.writeheader()
            writer.writerows(ot_corridor_rows)
        (data_dir / "ot_scan_corridor_halfwidth.json").write_text(
            json.dumps(
                {
                    "meta": {
                        "Lx": int(Lx),
                        "q": float(q),
                        "scan_t_max": int(args.scan_t_max),
                        "scan_surv_tol": float(args.scan_surv_tol),
                        "start_x": int(ot_start_x),
                        "target_x": int(ot_target_x),
                        "wall_margin": int(args.ot_wall_margin),
                        "delta_core": float(args.ot_delta_core),
                        "delta_open": float(args.ot_delta_open),
                    },
                    "widths": [int(v) for v in ot_widths],
                    "bx_values": [float(v) for v in bx_values],
                    "corridor_halfwidth_values": [int(v) for v in ot_corridor_halfwidth_values],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    bx_values_float = [float(v) for v in bx_values]
    bx_focus = -0.08 if any(_float_close(v, -0.08) for v in bx_values_float) else _nearest_in_list(bx_values_float, -0.08)
    bx_weak = -0.12 if any(_float_close(v, -0.12) for v in bx_values_float) else _nearest_in_list(bx_values_float, -0.12)
    bx_zero = 0.00 if any(_float_close(v, 0.0) for v in bx_values_float) else _nearest_in_list(bx_values_float, 0.0)
    ot_corr_phase_focus, ot_corr_sep_focus = build_ot_corridor_focus_grids(
        ot_corridor_rows,
        widths=ot_widths,
        corridor_halfwidth_values=ot_corridor_halfwidth_values,
        bx_focus=bx_focus,
    )
    plot_ot_corridor_phase_vs_width(
        fig_dir / "ot_corridor_phase_vs_width.pdf",
        phase=ot_corr_phase_focus,
        widths=ot_widths,
        corridor_halfwidth_values=ot_corridor_halfwidth_values,
        bx_focus=float(bx_focus),
    )
    plot_ot_corridor_sep_vs_width(
        fig_dir / "ot_corridor_sep_vs_width.pdf",
        sep=ot_corr_sep_focus,
        widths=ot_widths,
        corridor_halfwidth_values=ot_corridor_halfwidth_values,
        bx_focus=float(bx_focus),
    )
    render_ot_corridor_width_summary(
        ot_corridor_rows,
        table_dir / "ot_corridor_width_summary.tex",
        widths=ot_widths,
        corridor_halfwidth_values=ot_corridor_halfwidth_values,
        bx_focus=float(bx_focus),
        bx_weak=float(bx_weak),
        bx_zero=float(bx_zero),
    )

    # Additional one-target scan: global-bias vector map (bx, by) at fixed width.
    ot_bias_scan_w = int(min(ot_widths, key=lambda w: (abs(int(w) - int(args.ot_bias_scan_width)), int(w))))
    ot_bias_rows: List[dict] = []
    ot_bias_phase = np.zeros((len(by_values), len(bx_values)), dtype=np.int64)
    ot_bias_sep = np.zeros_like(ot_bias_phase, dtype=np.float64)
    ot_bias_valley = np.zeros_like(ot_bias_phase, dtype=np.float64)
    ot_bias_reused = False
    if bool(args.reuse_scan_data):
        ot_bias_reused_data = try_reuse_ot_bias2d_scan(
            data_dir=data_dir,
            bx_values=bx_values,
            by_values=by_values,
            Wy_ref=int(ot_bias_scan_w),
            Lx=Lx,
            q=q,
            args=args,
            start_x=int(ot_start_x),
            target_x=int(ot_target_x),
        )
        if ot_bias_reused_data is not None:
            ot_bias_rows, ot_bias_phase, ot_bias_sep, ot_bias_valley = ot_bias_reused_data
            ot_bias_reused = True
            print("Reused one-target bias2d scan data from data/ot_scan_bias2d.{csv,json}")

    if not ot_bias_reused:
        start_b, tgt_b, local_bias_b, barrier_b, corridor_mask_b, _ = build_ot_case_geometry(
            Lx=Lx,
            Wy=int(ot_bias_scan_w),
            corridor_halfwidth=int(args.ot_corridor_halfwidth),
            wall_margin=int(args.ot_wall_margin),
            delta_core=float(args.ot_delta_core),
            delta_open=float(args.ot_delta_open),
            start_x=int(ot_start_x),
            target_x=int(ot_target_x),
        )
        for by in by_values:
            for bx in bx_values:
                src_b, dst_b, probs_b = build_transition_arrays_general_rect(
                    Lx=Lx,
                    Wy=int(ot_bias_scan_w),
                    q=q,
                    local_bias_map=local_bias_b,
                    sticky_map={},
                    barrier_map=barrier_b,
                    long_range_map={},
                    global_bias=(float(bx), float(by)),
                )
                f_b, f_b_ch1, f_b_ch2, surv_b = run_exact_one_target_rect(
                    Lx=Lx,
                    Wy=int(ot_bias_scan_w),
                    start=start_b,
                    target=tgt_b,
                    src_idx=src_b,
                    dst_idx=dst_b,
                    probs=probs_b,
                    t_max=int(args.scan_t_max),
                    surv_tol=float(args.scan_surv_tol),
                    channel_mask=corridor_mask_b,
                )
                spec_b = OTCaseSpec(
                    Wy=int(ot_bias_scan_w),
                    bx=float(bx),
                    corridor_halfwidth=int(args.ot_corridor_halfwidth),
                    wall_margin=int(args.ot_wall_margin),
                    delta_core=float(args.ot_delta_core),
                    delta_open=float(args.ot_delta_open),
                )
                validate_ot_series_consistency(
                    case_id=f"{spec_b.case_id}_by{float(by):+.3f}",
                    f_total=f_b,
                    f_corr=f_b_ch1,
                    f_outer=f_b_ch2,
                    surv=surv_b,
                )
                res_b = summarize_one_target(spec_b, f_b, surv_b)
                ot_bias_rows.append(
                    {
                        "Wy": int(ot_bias_scan_w),
                        "bx": float(bx),
                        "by": float(by),
                        "start_x": int(ot_start_x),
                        "target_x": int(ot_target_x),
                        "corridor_halfwidth": int(args.ot_corridor_halfwidth),
                        "wall_margin": int(args.ot_wall_margin),
                        "delta_core": float(args.ot_delta_core),
                        "delta_open": float(args.ot_delta_open),
                        "phase": int(res_b.phase),
                        "sep_peaks": float(res_b.sep_peaks),
                        "valley_over_max": (None if res_b.valley_over_max is None else float(res_b.valley_over_max)),
                        "t_peak1": res_b.t_peak1,
                        "t_peak2": res_b.t_peak2,
                        "absorbed_mass": float(res_b.absorbed_mass),
                        "survival_tail": float(res_b.survival_tail),
                    }
                )

        ot_bias_phase, ot_bias_sep, ot_bias_valley = build_ot_bias2d_grids(
            ot_bias_rows,
            bx_values=bx_values,
            by_values=by_values,
        )
        ot_bias_csv = data_dir / "ot_scan_bias2d.csv"
        with ot_bias_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(ot_bias_rows[0].keys()))
            writer.writeheader()
            writer.writerows(ot_bias_rows)
        (data_dir / "ot_scan_bias2d.json").write_text(
            json.dumps(
                {
                    "meta": {
                        "Lx": int(Lx),
                        "q": float(q),
                        "Wy_ref": int(ot_bias_scan_w),
                        "scan_t_max": int(args.scan_t_max),
                        "scan_surv_tol": float(args.scan_surv_tol),
                        "start_x": int(ot_start_x),
                        "target_x": int(ot_target_x),
                        "corridor_halfwidth": int(args.ot_corridor_halfwidth),
                        "wall_margin": int(args.ot_wall_margin),
                        "delta_core": float(args.ot_delta_core),
                        "delta_open": float(args.ot_delta_open),
                    },
                    "bx_values": [float(v) for v in bx_values],
                    "by_values": [float(v) for v in by_values],
                    "phase_grid": ot_bias_phase.tolist(),
                    "sep_grid": ot_bias_sep.tolist(),
                    "valley_grid": ot_bias_valley.tolist(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    plot_phase_map(
        fig_dir / "ot_bias2d_phase_bx_by.pdf",
        phase=ot_bias_phase,
        x_ticks=[f"{float(v):.2f}" for v in bx_values],
        y_ticks=[f"{float(v):.2f}" for v in by_values],
        xlabel="bx",
        ylabel="by",
        title=f"One-target bias-vector phase map (Wy={ot_bias_scan_w}, x_s={ot_start_x}, x_t={ot_target_x})",
    )
    plot_scalar_map(
        fig_dir / "ot_bias2d_sep_bx_by.pdf",
        arr=ot_bias_sep,
        x_ticks=[f"{float(v):.2f}" for v in bx_values],
        y_ticks=[f"{float(v):.2f}" for v in by_values],
        xlabel="bx",
        ylabel="by",
        title=f"One-target bias-vector separation map (Wy={ot_bias_scan_w})",
        cbar_label="sep-score",
    )
    render_ot_bias2d_phase_table(
        ot_bias_rows,
        table_dir / "ot_bias2d_phase_overview.tex",
        bx_values=bx_values,
        by_values=by_values,
    )

    # Representative detailed runs
    ot_rep_specs = pick_representatives_ot(ot_rows, max_total=4)
    ot_rep_results: List[OTCaseResult] = []
    ot_series_map: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    ot_layouts: Dict[str, dict] = {}

    ot_heat_paths: Dict[str, Path] = {}
    for k_rep, spec in enumerate(ot_rep_specs):
        start, tgt, local_bias_map, barrier_map, corridor_mask, wall_span = build_ot_case_geometry(
            Lx=Lx,
            Wy=spec.Wy,
            corridor_halfwidth=spec.corridor_halfwidth,
            wall_margin=spec.wall_margin,
            delta_core=spec.delta_core,
            delta_open=spec.delta_open,
            start_x=int(ot_start_x),
            target_x=int(ot_target_x),
        )
        src_idx, dst_idx, probs = build_transition_arrays_general_rect(
            Lx=Lx,
            Wy=spec.Wy,
            q=q,
            local_bias_map=local_bias_map,
            sticky_map={},
            barrier_map=barrier_map,
            long_range_map={},
            global_bias=(spec.bx, 0.0),
        )
        f, f_ch1, f_ch2, surv = run_exact_one_target_rect(
            Lx=Lx,
            Wy=spec.Wy,
            start=start,
            target=tgt,
            src_idx=src_idx,
            dst_idx=dst_idx,
            probs=probs,
            t_max=int(args.t_max),
            surv_tol=float(args.surv_tol),
            channel_mask=corridor_mask,
        )
        validate_ot_series_consistency(case_id=spec.case_id, f_total=f, f_corr=f_ch1, f_outer=f_ch2, surv=surv)
        res = summarize_one_target(spec, f, surv)
        ot_rep_results.append(res)
        ot_series_map[spec.case_id] = (f, f_ch1, f_ch2, surv)
        ot_layouts[spec.case_id] = {
            "Wy": int(spec.Wy),
            "start": start,
            "target": tgt,
            "corridor_mask": corridor_mask,
            "barrier_map": barrier_map,
            "wall_span": wall_span,
        }

        # save series
        out_csv = out_dir / f"{spec.case_id}_fpt.csv"
        with out_csv.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["t", "f_total", "f_from_corridor", "f_from_outer", "survival"])
            for t in range(len(f)):
                w.writerow([t, f[t], f_ch1[t], f_ch2[t], surv[t]])

        plot_ot_geometry(
            fig_dir / f"{spec.case_id}_geometry.pdf",
            Lx=Lx,
            Wy=spec.Wy,
            start=start,
            target=tgt,
            corridor_mask=corridor_mask,
            barrier_map=barrier_map,
            wall_span=wall_span,
            title=f"{spec.case_id}: Wy={spec.Wy}, bx={spec.bx:.3f}, x_s={ot_start_x}, x_t={ot_target_x}",
        )
        plot_ot_fpt(fig_dir / f"{spec.case_id}_fpt.pdf", f=f, f_ch1=f_ch1, f_ch2=f_ch2, res=res)
        plot_ot_hazard(fig_dir / f"{spec.case_id}_hazard.pdf", f=f, f_ch1=f_ch1, f_ch2=f_ch2, surv=surv, res=res)

        heat_times = choose_heat_times(res.t_peak1, res.t_valley, res.t_peak2)
        snaps = conditional_snapshots_one_target_rect(
            Lx=Lx,
            Wy=spec.Wy,
            start=start,
            target=tgt,
            src_idx=src_idx,
            dst_idx=dst_idx,
            probs=probs,
            times=heat_times,
        )
        plot_ot_env_heatmaps(
            fig_dir / f"{spec.case_id}_env_heatmap.pdf",
            Lx=Lx,
            Wy=spec.Wy,
            start=start,
            target=tgt,
            corridor_mask=corridor_mask,
            barrier_map=barrier_map,
            wall_span=wall_span,
            case_title=f"{spec.case_id}: Wy={spec.Wy}, bx={spec.bx:.3f}, x_s={ot_start_x}, x_t={ot_target_x}",
            snapshots=snaps,
            heat_times=heat_times,
        )
        ot_heat_paths[spec.case_id] = fig_dir / f"{spec.case_id}_env_heatmap.pdf"

    # Pick A/B heatmaps with phase contrast when possible.
    if ot_rep_results:
        case_a = ot_rep_results[0].spec.case_id
        alt = [r for r in ot_rep_results if int(r.phase) != int(ot_rep_results[0].phase)]
        if alt:
            case_b = alt[0].spec.case_id
        elif len(ot_rep_results) > 1:
            case_b = ot_rep_results[1].spec.case_id
        else:
            case_b = case_a
        if case_a in ot_heat_paths:
            shutil.copyfile(ot_heat_paths[case_a], fig_dir / "ot_repA_env_heatmap.pdf")
        if case_b in ot_heat_paths:
            shutil.copyfile(ot_heat_paths[case_b], fig_dir / "ot_repB_env_heatmap.pdf")

    render_ot_representative_table(ot_rep_results, table_dir / "ot_representative_metrics.tex")
    plot_ot_rep_geometry_grid(
        fig_dir / "ot_representative_geometry_grid.pdf",
        Lx=Lx,
        layouts=ot_layouts,
        reps=ot_rep_results,
    )
    plot_ot_rep_fpt_grid(
        fig_dir / "ot_representative_fpt_grid.pdf",
        reps=ot_rep_results,
        series_map=ot_series_map,
    )
    plot_ot_rep_hazard_grid(
        fig_dir / "ot_representative_hazard_grid.pdf",
        reps=ot_rep_results,
        series_map=ot_series_map,
    )

    # Cross-check that all representative picks are phase-consistent with scan rows.
    validate_representative_phase_consistency(
        tt_rows=tt_rows,
        ot_rows=ot_rows,
        tt_rep_specs=tt_rep_specs,
        tt_width_specs=tt_width_specs,
        ot_rep_specs=ot_rep_specs,
    )

    # ---- Write a small JSON summary for the LaTeX report ----
    summary = {
        "meta": {
            "Lx": Lx,
            "q": q,
            "scan_t_max": int(args.scan_t_max),
            "scan_surv_tol": float(args.scan_surv_tol),
            "t_max": int(args.t_max),
            "surv_tol": float(args.surv_tol),
        },
        "two_target_scan": {
            "widths": tt_widths,
            "x_starts": tt_xstarts,
            "max_survival_tail_scan": float(max((float(r["survival_tail"]) for r in tt_rows), default=0.0)),
            "phase_map": "figures/tt_phase_width_xstart.pdf",
            "sep_map": "figures/tt_sep_width_xstart.pdf",
            "valley_map": "figures/tt_valley_width_xstart.pdf",
            "overview_table": "tables/tt_scan_overview.tex",
            "critical_table": "tables/tt_critical_width_by_xstart.tex",
            "critical_curve": "figures/tt_critical_vs_xstart.pdf",
            "representatives": [s.case_id for s in tt_rep_specs],
            "rep_series_csv": [f"outputs/{s.case_id}_fpt.csv" for s in tt_rep_specs],
            "rep_geometry_grid": "figures/tt_representative_geometry_grid.pdf",
            "rep_fpt_grid": "figures/tt_representative_fpt_grid.pdf",
            "rep_hazard_grid": "figures/tt_hazard_grid.pdf",
            "rep_env_heatmap_A": "figures/tt_repA_env_heatmap.pdf",
            "rep_env_heatmap_B": "figures/tt_repB_env_heatmap.pdf",
            "width_sweep_representatives": [s.case_id for s in tt_width_specs],
            "width_sweep_table": "tables/tt_width_sweep_metrics.tex",
            "width_sweep_geometry_grid": "figures/tt_width_sweep_geometry_grid.pdf",
            "width_sweep_fpt_grid": "figures/tt_width_sweep_fpt_grid.pdf",
            "width_sweep_trend": "figures/tt_width_sweep_trend.pdf",
        },
        "one_target_scan": {
            "widths": ot_widths,
            "bx_values": bx_values,
            "start_x": int(ot_start_x),
            "target_x": int(ot_target_x),
            "max_survival_tail_scan": float(max((float(r["survival_tail"]) for r in ot_rows), default=0.0)),
            "placement_ref": {
                "Wy": int(best_anchor["Wy_ref"]),
                "bx": float(best_anchor["bx"]),
                "phase": int(best_anchor["phase"]),
                "sep_peaks": float(best_anchor["sep_peaks"]),
                "valley_over_max": best_anchor["valley_over_max"],
                "peak_balance": best_anchor["peak_balance"],
                "t_peak1": best_anchor["t_peak1"],
                "t_peak2": best_anchor["t_peak2"],
                "phase2_count": int(best_anchor["phase2_count"]),
                "phase1plus_count": int(best_anchor["phase1plus_count"]),
                "placement_widths": [int(w) for w in best_anchor["placement_widths"]],
            },
            "phase_map": "figures/ot_phase_width_bx.pdf",
            "sep_map": "figures/ot_sep_width_bx.pdf",
            "valley_vs_width": "figures/ot_valley_vs_width.pdf",
            "overview_table": "tables/ot_scan_overview.tex",
            "anchor_table": "tables/ot_anchor_selection.tex",
            "representatives": [s.case_id for s in ot_rep_specs],
            "rep_series_csv": [f"outputs/{s.case_id}_fpt.csv" for s in ot_rep_specs],
            "rep_geometry_grid": "figures/ot_representative_geometry_grid.pdf",
            "rep_fpt_grid": "figures/ot_representative_fpt_grid.pdf",
            "rep_hazard_grid": "figures/ot_representative_hazard_grid.pdf",
            "rep_env_heatmap_A": "figures/ot_repA_env_heatmap.pdf",
            "rep_env_heatmap_B": "figures/ot_repB_env_heatmap.pdf",
            "corridor_halfwidth_values": [int(v) for v in ot_corridor_halfwidth_values],
            "corridor_scan_csv": "data/ot_scan_corridor_halfwidth.csv",
            "corridor_scan_json": "data/ot_scan_corridor_halfwidth.json",
            "corridor_phase_vs_width": "figures/ot_corridor_phase_vs_width.pdf",
            "corridor_sep_vs_width": "figures/ot_corridor_sep_vs_width.pdf",
            "corridor_summary_table": "tables/ot_corridor_width_summary.tex",
            "corridor_focus_bx": float(bx_focus),
            "bias2d_scan_width": int(ot_bias_scan_w),
            "bias2d_by_values": [float(v) for v in by_values],
            "bias2d_scan_csv": "data/ot_scan_bias2d.csv",
            "bias2d_scan_json": "data/ot_scan_bias2d.json",
            "bias2d_phase_map": "figures/ot_bias2d_phase_bx_by.pdf",
            "bias2d_sep_map": "figures/ot_bias2d_sep_bx_by.pdf",
            "bias2d_table": "tables/ot_bias2d_phase_overview.tex",
        },
    }
    validate_summary_artifact_paths(summary, report_dir=report_dir)
    (data_dir / "case_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
