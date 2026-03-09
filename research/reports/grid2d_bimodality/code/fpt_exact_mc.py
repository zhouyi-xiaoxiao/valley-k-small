#!/usr/bin/env python3
"""Exact recursion and Monte Carlo helpers."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from model_core import Coord, LatticeConfig, build_exact_arrays, build_mc_arrays, build_transition_map


def exact_fpt(cfg: LatticeConfig, t_max: int, stop_tol: float = 1e-12) -> Tuple[np.ndarray, float]:
    src_idx, dst_idx, probs, r, index = build_exact_arrays(cfg)
    n = len(r)
    p = np.zeros(n, dtype=np.float64)
    p[index[cfg.start]] = 1.0

    f = np.zeros(t_max, dtype=np.float64)
    for t in range(t_max):
        f[t] = float(np.dot(p, r))
        if t == t_max - 1:
            break
        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_idx, p[src_idx] * probs)
        p = p_next
        if p.sum() < stop_tol:
            break
    return f, float(f.sum())


def build_full_transition_arrays(cfg: LatticeConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    trans_map = build_transition_map(cfg)
    n_states = cfg.N * cfg.N
    src_idx: List[int] = []
    dst_idx: List[int] = []
    probs: List[float] = []

    def idx(xy: Coord) -> int:
        return xy[0] * cfg.N + xy[1]

    for x in range(cfg.N):
        for y in range(cfg.N):
            xy = (x, y)
            s = idx(xy)
            if xy == cfg.target:
                src_idx.append(s)
                dst_idx.append(s)
                probs.append(1.0)
                continue
            for nxt, prob in trans_map[xy]:
                src_idx.append(s)
                dst_idx.append(idx(nxt))
                probs.append(prob)

    return (
        np.asarray(src_idx, dtype=np.int64),
        np.asarray(dst_idx, dtype=np.int64),
        np.asarray(probs, dtype=np.float64),
    )


def distributions_at_times(
    cfg: LatticeConfig, times: List[int], *, conditional: bool = True
) -> Dict[int, np.ndarray]:
    max_t = max(times)
    src_idx, dst_idx, probs = build_full_transition_arrays(cfg)
    n_states = cfg.N * cfg.N
    p = np.zeros(n_states, dtype=np.float64)
    p[cfg.start[0] * cfg.N + cfg.start[1]] = 1.0

    out: Dict[int, np.ndarray] = {}
    target_idx = cfg.target[0] * cfg.N + cfg.target[1]
    times_set = set(times)

    for t in range(1, max_t + 1):
        p_next = np.zeros_like(p)
        np.add.at(p_next, dst_idx, p[src_idx] * probs)
        p = p_next
        if t in times_set:
            if conditional:
                surv = float(p.sum() - p[target_idx])
                snap = p.copy()
                snap[target_idx] = 0.0
                if surv > 0:
                    snap = snap / surv
            else:
                snap = p.copy()
            out[t] = snap.reshape(cfg.N, cfg.N)
    return out


# -------------------------
# Monte Carlo
# -------------------------


def mc_candidate_A(
    cfg: LatticeConfig, n_walkers: int, seed: int, max_steps: int
) -> Tuple[np.ndarray, np.ndarray, dict]:
    rng = np.random.default_rng(seed)
    neighbors, cum_probs = build_mc_arrays(cfg)
    start_idx = cfg.start[0] * cfg.N + cfg.start[1]
    target_idx = cfg.target[0] * cfg.N + cfg.target[1]

    states = np.full(n_walkers, start_idx, dtype=np.int64)
    times = np.zeros(n_walkers, dtype=np.int64)
    wrapped = np.zeros(n_walkers, dtype=bool)

    alive = states != target_idx
    steps = 0
    while np.any(alive) and steps < max_steps:
        idx_alive = np.nonzero(alive)[0]
        s = states[idx_alive]
        u = rng.random(size=s.size)
        cum = cum_probs[s]
        move_idx = (u[:, None] > cum).sum(axis=1)
        s_next = neighbors[s, move_idx]

        x = s // cfg.N
        x_next = s_next // cfg.N
        wrap_step = ((x == 0) & (x_next == cfg.N - 1)) | ((x == cfg.N - 1) & (x_next == 0))
        wrapped[idx_alive] |= wrap_step

        states[idx_alive] = s_next
        times[idx_alive] += 1
        alive = states != target_idx
        steps += 1

    truncated = alive
    if np.any(truncated):
        times[truncated] = max_steps

    labels = wrapped.astype(np.int64)
    stats = {
        "n_walkers": int(n_walkers),
        "wrap_fraction": float(labels.mean()),
        "truncated_fraction": float(truncated.mean()) if n_walkers > 0 else 0.0,
    }
    return times, labels, stats


def mc_candidate_B(
    cfg: LatticeConfig,
    corridor_set: set[Coord],
    n_walkers: int,
    seed: int,
    max_steps: int,
    corridor_band: set[Coord] | None = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    rng = np.random.default_rng(seed)
    neighbors, cum_probs = build_mc_arrays(cfg)
    start_idx = cfg.start[0] * cfg.N + cfg.start[1]
    target_idx = cfg.target[0] * cfg.N + cfg.target[1]

    band = corridor_band if corridor_band is not None else corridor_set
    corridor_mask = np.zeros(cfg.N * cfg.N, dtype=bool)
    for xy in band:
        corridor_mask[xy[0] * cfg.N + xy[1]] = True

    states = np.full(n_walkers, start_idx, dtype=np.int64)
    times = np.zeros(n_walkers, dtype=np.int64)
    left_corridor = np.zeros(n_walkers, dtype=bool)

    alive = states != target_idx
    steps = 0
    while np.any(alive) and steps < max_steps:
        idx_alive = np.nonzero(alive)[0]
        s = states[idx_alive]
        u = rng.random(size=s.size)
        cum = cum_probs[s]
        move_idx = (u[:, None] > cum).sum(axis=1)
        s_next = neighbors[s, move_idx]

        left_corridor[idx_alive] |= ~corridor_mask[s_next]
        states[idx_alive] = s_next
        times[idx_alive] += 1
        alive = states != target_idx
        steps += 1

    truncated = alive
    if np.any(truncated):
        times[truncated] = max_steps

    labels = left_corridor.astype(np.int64)
    stats = {
        "n_walkers": int(n_walkers),
        "corridor_fraction": float(1.0 - labels.mean()),
        "truncated_fraction": float(truncated.mean()) if n_walkers > 0 else 0.0,
    }
    return times, labels, stats


def mc_candidate_C(
    cfg: LatticeConfig,
    door_edge: Tuple[Coord, Coord],
    sticky_set: set[Coord],
    t_valley: int,
    n_walkers: int,
    seed: int,
    max_steps: int,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    rng = np.random.default_rng(seed)
    neighbors, cum_probs = build_mc_arrays(cfg)
    start_idx = cfg.start[0] * cfg.N + cfg.start[1]
    target_idx = cfg.target[0] * cfg.N + cfg.target[1]

    sticky_mask = np.zeros(cfg.N * cfg.N, dtype=bool)
    for xy in sticky_set:
        sticky_mask[xy[0] * cfg.N + xy[1]] = True

    door_x0 = min(door_edge[0][0], door_edge[1][0])
    door_x1 = max(door_edge[0][0], door_edge[1][0])
    door_y = door_edge[0][1]

    states = np.full(n_walkers, start_idx, dtype=np.int64)
    times = np.zeros(n_walkers, dtype=np.int64)
    first_cross = np.zeros(n_walkers, dtype=np.int64)
    cross_count = np.zeros(n_walkers, dtype=np.int64)
    sticky_hit = np.zeros(n_walkers, dtype=bool)

    alive = states != target_idx
    steps = 0
    while np.any(alive) and steps < max_steps:
        idx_alive = np.nonzero(alive)[0]
        s = states[idx_alive]
        u = rng.random(size=s.size)
        cum = cum_probs[s]
        move_idx = (u[:, None] > cum).sum(axis=1)
        s_next = neighbors[s, move_idx]

        x = s // cfg.N
        y = s % cfg.N
        x_next = s_next // cfg.N
        y_next = s_next % cfg.N

        door_cross = ((x == door_x0) & (x_next == door_x1) & (y == door_y) & (y_next == door_y)) | (
            (x == door_x1) & (x_next == door_x0) & (y == door_y) & (y_next == door_y)
        )
        step_time = times[idx_alive] + 1
        newly_crossed = door_cross & (first_cross[idx_alive] == 0)
        if np.any(newly_crossed):
            first_cross[idx_alive[newly_crossed]] = step_time[newly_crossed]
        cross_count[idx_alive] += door_cross.astype(np.int64)

        sticky_hit[idx_alive] |= sticky_mask[s_next]
        states[idx_alive] = s_next
        times[idx_alive] += 1
        alive = states != target_idx
        steps += 1

    truncated = alive
    if np.any(truncated):
        times[truncated] = max_steps

    first_cross[first_cross == 0] = times[first_cross == 0]
    labels = (first_cross > int(t_valley)).astype(np.int64)

    stats = {
        "n_walkers": int(n_walkers),
        "early_fraction": float(1.0 - labels.mean()),
        "mean_first_cross": float(np.mean(first_cross)),
        "sticky_fraction": float(sticky_hit.mean()),
        "mean_cross_count": float(np.mean(cross_count)),
        "truncated_fraction": float(truncated.mean()) if n_walkers > 0 else 0.0,
    }
    return times, labels, stats


def hist_pmf(times: np.ndarray, t_plot: int) -> Tuple[np.ndarray, float]:
    if times.size == 0:
        return np.zeros(t_plot, dtype=np.float64), 0.0
    max_time = int(times.max())
    counts = np.bincount(times, minlength=max_time + 1)
    if t_plot >= len(counts):
        counts = np.pad(counts, (0, t_plot + 1 - len(counts)), mode="constant")
    tail = counts[t_plot + 1 :].sum() if t_plot + 1 < len(counts) else 0.0
    pmf = counts[1 : t_plot + 1] / float(times.size)
    tail_mass = float(tail / float(times.size))
    return pmf, tail_mass


# -------------------------
# Representative trajectories
# -------------------------


def sample_path_candidate_A(
    cfg: LatticeConfig,
    *,
    max_steps: int,
    rng: np.random.Generator,
    neighbors: np.ndarray | None = None,
    cum_probs: np.ndarray | None = None,
) -> Tuple[np.ndarray, int, int]:
    if neighbors is None or cum_probs is None:
        neighbors, cum_probs = build_mc_arrays(cfg)

    start_idx = cfg.start[0] * cfg.N + cfg.start[1]
    target_idx = cfg.target[0] * cfg.N + cfg.target[1]

    s = start_idx
    path = [(cfg.start[0], cfg.start[1])]
    wrapped = False

    for t in range(1, max_steps + 1):
        u = rng.random()
        move_idx = int((u > cum_probs[s]).sum())
        s_next = neighbors[s, move_idx]

        x = s // cfg.N
        x_next = s_next // cfg.N
        wrap_step = ((x == 0) & (x_next == cfg.N - 1)) | ((x == cfg.N - 1) & (x_next == 0))
        wrapped = wrapped or bool(wrap_step)

        s = int(s_next)
        path.append((s // cfg.N, s % cfg.N))
        if s == target_idx:
            return np.asarray(path, dtype=np.int64), t, int(wrapped)

    return np.asarray(path, dtype=np.int64), max_steps, int(wrapped)


def sample_path_candidate_B(
    cfg: LatticeConfig,
    corridor_set: set[Coord],
    *,
    max_steps: int,
    rng: np.random.Generator,
    neighbors: np.ndarray | None = None,
    cum_probs: np.ndarray | None = None,
    corridor_band: set[Coord] | None = None,
) -> Tuple[np.ndarray, int, int]:
    if neighbors is None or cum_probs is None:
        neighbors, cum_probs = build_mc_arrays(cfg)

    start_idx = cfg.start[0] * cfg.N + cfg.start[1]
    target_idx = cfg.target[0] * cfg.N + cfg.target[1]

    band = corridor_band if corridor_band is not None else corridor_set
    corridor_mask = np.zeros(cfg.N * cfg.N, dtype=bool)
    for xy in band:
        corridor_mask[xy[0] * cfg.N + xy[1]] = True

    s = start_idx
    path = [(cfg.start[0], cfg.start[1])]
    left_corridor = False

    for t in range(1, max_steps + 1):
        u = rng.random()
        move_idx = int((u > cum_probs[s]).sum())
        s_next = neighbors[s, move_idx]
        left_corridor = left_corridor or (not corridor_mask[s_next])

        s = int(s_next)
        path.append((s // cfg.N, s % cfg.N))
        if s == target_idx:
            return np.asarray(path, dtype=np.int64), t, int(left_corridor)

    return np.asarray(path, dtype=np.int64), max_steps, int(left_corridor)


def sample_path_candidate_C(
    cfg: LatticeConfig,
    door_edge: Tuple[Coord, Coord],
    t_valley: int,
    *,
    max_steps: int,
    rng: np.random.Generator,
    neighbors: np.ndarray | None = None,
    cum_probs: np.ndarray | None = None,
) -> Tuple[np.ndarray, int, int]:
    if neighbors is None or cum_probs is None:
        neighbors, cum_probs = build_mc_arrays(cfg)

    start_idx = cfg.start[0] * cfg.N + cfg.start[1]
    target_idx = cfg.target[0] * cfg.N + cfg.target[1]

    door_x0 = min(door_edge[0][0], door_edge[1][0])
    door_x1 = max(door_edge[0][0], door_edge[1][0])
    door_y = door_edge[0][1]

    s = start_idx
    path = [(cfg.start[0], cfg.start[1])]
    first_cross = 0

    for t in range(1, max_steps + 1):
        u = rng.random()
        move_idx = int((u > cum_probs[s]).sum())
        s_next = neighbors[s, move_idx]

        x = s // cfg.N
        y = s % cfg.N
        x_next = s_next // cfg.N
        y_next = s_next % cfg.N
        door_cross = ((x == door_x0) & (x_next == door_x1) & (y == door_y) & (y_next == door_y)) | (
            (x == door_x1) & (x_next == door_x0) & (y == door_y) & (y_next == door_y)
        )
        if door_cross and first_cross == 0:
            first_cross = t

        s = int(s_next)
        path.append((s // cfg.N, s % cfg.N))
        if s == target_idx:
            if first_cross == 0:
                first_cross = t
            label = int(first_cross > int(t_valley))
            return np.asarray(path, dtype=np.int64), t, label

    if first_cross == 0:
        first_cross = max_steps
    label = int(first_cross > int(t_valley))
    return np.asarray(path, dtype=np.int64), max_steps, label
