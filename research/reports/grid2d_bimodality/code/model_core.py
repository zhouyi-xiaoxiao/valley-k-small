#!/usr/bin/env python3
"""
Core model definitions for the 2D biased/lazy random walk on an N x N lattice.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

Coord = Tuple[int, int]
Edge = Tuple[Coord, Coord]

DIRECTIONS: dict[str, Coord] = {
    "left": (-1, 0),
    "right": (1, 0),
    "down": (0, 1),
    "up": (0, -1),
}


@dataclass(frozen=True)
class ConfigSpec:
    """1-based configuration for report-level specs."""

    N: int
    q: float
    g_x: float
    g_y: float
    boundary_x: str
    boundary_y: str
    start: Coord
    target: Coord
    local_bias_arrows: Dict[Coord, str] = field(default_factory=dict)
    local_bias_delta: float = 0.2
    sticky_sites: Dict[Coord, float] = field(default_factory=dict)
    barriers_reflect: set[Edge] = field(default_factory=set)
    barriers_perm: Dict[Edge, float] = field(default_factory=dict)


@dataclass(frozen=True)
class LatticeConfig:
    """0-based internal configuration."""

    N: int
    q: float
    g_x: float
    g_y: float
    boundary_x: str
    boundary_y: str
    start: Coord
    target: Coord
    local_bias_arrows: Dict[Coord, str] = field(default_factory=dict)
    local_bias_delta: float = 0.2
    sticky_sites: Dict[Coord, float] = field(default_factory=dict)
    barriers_reflect: set[Edge] = field(default_factory=set)
    barriers_perm: Dict[Edge, float] = field(default_factory=dict)


@dataclass(frozen=True)
class TransitionOperator:
    """Cached transition arrays for exact recursion and MC."""

    src_idx: np.ndarray
    dst_idx: np.ndarray
    probs: np.ndarray
    r: np.ndarray
    index: Dict[Coord, int]
    neighbors: np.ndarray
    cum_probs: np.ndarray


def coord_to0(xy: Coord) -> Coord:
    return (int(xy[0]) - 1, int(xy[1]) - 1)


def coord_to1(xy: Coord) -> Coord:
    return (int(xy[0]) + 1, int(xy[1]) + 1)


def edge_key(a: Coord, b: Coord) -> Edge:
    return (a, b) if a <= b else (b, a)


def scale_coord(xy: Coord, scale: float, N_new: int) -> Coord:
    x = int(round(float(xy[0]) * scale))
    y = int(round(float(xy[1]) * scale))
    x = max(1, min(N_new, x))
    y = max(1, min(N_new, y))
    return (x, y)


def scale_spec(spec: ConfigSpec, N_new: int) -> ConfigSpec:
    scale = float(N_new) / float(spec.N)

    local_bias = {scale_coord(k, scale, N_new): v for k, v in spec.local_bias_arrows.items()}
    sticky = {scale_coord(k, scale, N_new): v for k, v in spec.sticky_sites.items()}

    barriers_reflect: set[Edge] = set()
    for a, b in spec.barriers_reflect:
        a_s = scale_coord(a, scale, N_new)
        b_s = scale_coord(b, scale, N_new)
        barriers_reflect.add(edge_key(a_s, b_s))

    barriers_perm: Dict[Edge, float] = {}
    for (a, b), prob in spec.barriers_perm.items():
        a_s = scale_coord(a, scale, N_new)
        b_s = scale_coord(b, scale, N_new)
        barriers_perm[edge_key(a_s, b_s)] = float(prob)

    return ConfigSpec(
        N=N_new,
        q=spec.q,
        g_x=spec.g_x,
        g_y=spec.g_y,
        boundary_x=spec.boundary_x,
        boundary_y=spec.boundary_y,
        start=scale_coord(spec.start, scale, N_new),
        target=scale_coord(spec.target, scale, N_new),
        local_bias_arrows=local_bias,
        local_bias_delta=spec.local_bias_delta,
        sticky_sites=sticky,
        barriers_reflect=barriers_reflect,
        barriers_perm=barriers_perm,
    )


def spec_to_internal(spec: ConfigSpec) -> LatticeConfig:
    local_bias = {coord_to0(k): v for k, v in spec.local_bias_arrows.items()}
    sticky = {coord_to0(k): float(v) for k, v in spec.sticky_sites.items()}
    barriers_reflect = {edge_key(coord_to0(a), coord_to0(b)) for a, b in spec.barriers_reflect}
    barriers_perm = {edge_key(coord_to0(a), coord_to0(b)): float(p) for (a, b), p in spec.barriers_perm.items()}
    return LatticeConfig(
        N=spec.N,
        q=spec.q,
        g_x=spec.g_x,
        g_y=spec.g_y,
        boundary_x=spec.boundary_x,
        boundary_y=spec.boundary_y,
        start=coord_to0(spec.start),
        target=coord_to0(spec.target),
        local_bias_arrows=local_bias,
        local_bias_delta=spec.local_bias_delta,
        sticky_sites=sticky,
        barriers_reflect=barriers_reflect,
        barriers_perm=barriers_perm,
    )


def config_to_dict(spec: ConfigSpec) -> dict:
    return {
        "N": spec.N,
        "q": spec.q,
        "g_x": spec.g_x,
        "g_y": spec.g_y,
        "boundary": {"x": spec.boundary_x, "y": spec.boundary_y},
        "start": list(spec.start),
        "target": list(spec.target),
        "local_bias_delta": spec.local_bias_delta,
        "n_local_bias": int(len(spec.local_bias_arrows)),
        "n_sticky": int(len(spec.sticky_sites)),
        "n_barriers_reflect": int(len(spec.barriers_reflect)),
        "n_barriers_perm": int(len(spec.barriers_perm)),
    }


def validate_config(cfg: LatticeConfig) -> None:
    if not (0.0 < cfg.q <= 1.0):
        raise ValueError("q must be in (0,1].")
    for g in (cfg.g_x, cfg.g_y):
        if g < -1.0 or g > 1.0:
            raise ValueError("g_x and g_y must be in [-1,1].")
    for name in (cfg.boundary_x, cfg.boundary_y):
        if name not in ("periodic", "reflecting"):
            raise ValueError("boundary must be periodic or reflecting.")


def global_move_probs(cfg: LatticeConfig) -> Tuple[float, float, float, float, float]:
    """Global move probabilities without local heterogeneities."""
    q = cfg.q
    p_left = 0.25 * q * (1.0 + cfg.g_x)
    p_right = 0.25 * q * (1.0 - cfg.g_x)
    p_down = 0.25 * q * (1.0 + cfg.g_y)
    p_up = 0.25 * q * (1.0 - cfg.g_y)
    p_stay = 1.0 - q
    return p_left, p_right, p_down, p_up, p_stay


def move_probs(cfg: LatticeConfig, xy: Coord, include_local: bool = True) -> Tuple[float, float, float, float, float]:
    p_left, p_right, p_down, p_up, p_stay = global_move_probs(cfg)

    if include_local:
        factor = cfg.sticky_sites.get(xy, 1.0)
        if factor != 1.0:
            p_left *= factor
            p_right *= factor
            p_down *= factor
            p_up *= factor
            p_stay = 1.0 - factor * cfg.q

        arrow = cfg.local_bias_arrows.get(xy)
        if arrow is not None and cfg.local_bias_delta > 0.0 and p_stay > 0.0:
            shift = cfg.local_bias_delta * p_stay
            p_stay -= shift
            if arrow == "left":
                p_left += shift
            elif arrow == "right":
                p_right += shift
            elif arrow == "down":
                p_down += shift
            elif arrow == "up":
                p_up += shift
            else:
                raise ValueError(f"Unknown arrow direction: {arrow}")

    if min(p_left, p_right, p_down, p_up, p_stay) < -1e-12:
        raise ValueError("Negative probability detected; check q/g/bias/sticky settings.")

    return p_left, p_right, p_down, p_up, p_stay


def neighbor_with_boundary(x: int, y: int, dx: int, dy: int, cfg: LatticeConfig) -> Optional[Coord]:
    N = cfg.N
    nx = x + dx
    ny = y + dy

    if cfg.boundary_x == "periodic":
        nx = nx % N
    else:
        if nx < 0 or nx >= N:
            return None

    if cfg.boundary_y == "periodic":
        ny = ny % N
    else:
        if ny < 0 or ny >= N:
            return None

    return (nx, ny)


def state_transitions(
    cfg: LatticeConfig,
    xy: Coord,
    *,
    include_local: bool = True,
    include_barriers: bool = True,
) -> List[Tuple[Coord, float]]:
    p_left, p_right, p_down, p_up, p_stay = move_probs(cfg, xy, include_local=include_local)
    probs = {
        "left": p_left,
        "right": p_right,
        "down": p_down,
        "up": p_up,
    }
    stay = p_stay
    out: Dict[Coord, float] = {}

    for direction, p_move in probs.items():
        if p_move <= 0.0:
            continue
        dx, dy = DIRECTIONS[direction]
        nxt = neighbor_with_boundary(xy[0], xy[1], dx, dy, cfg)
        if nxt is None:
            stay += p_move
            continue
        edge = edge_key(xy, nxt)
        if include_barriers:
            if edge in cfg.barriers_reflect:
                stay += p_move
                continue
            if edge in cfg.barriers_perm:
                p_pass = cfg.barriers_perm[edge]
                out[nxt] = out.get(nxt, 0.0) + p_move * p_pass
                stay += p_move * (1.0 - p_pass)
                continue
        out[nxt] = out.get(nxt, 0.0) + p_move

    out[xy] = out.get(xy, 0.0) + stay

    total = sum(out.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"Transition probabilities do not sum to 1 (sum={total}).")
    return list(out.items())


def build_transition_map(cfg: LatticeConfig) -> Dict[Coord, List[Tuple[Coord, float]]]:
    validate_config(cfg)
    trans: Dict[Coord, List[Tuple[Coord, float]]] = {}
    for x in range(cfg.N):
        for y in range(cfg.N):
            xy = (x, y)
            if xy == cfg.target:
                trans[xy] = []
            else:
                trans[xy] = state_transitions(cfg, xy, include_local=True, include_barriers=True)
    return trans


def build_exact_arrays(cfg: LatticeConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[Coord, int]]:
    trans_map = build_transition_map(cfg)
    coords = [(x, y) for x in range(cfg.N) for y in range(cfg.N) if (x, y) != cfg.target]
    index = {xy: i for i, xy in enumerate(coords)}
    transitions: List[List[Tuple[int, float]]] = [[] for _ in range(len(coords))]
    r = np.zeros(len(coords), dtype=np.float64)

    for xy, i in index.items():
        for nxt, prob in trans_map[xy]:
            if nxt == cfg.target:
                r[i] += prob
            else:
                transitions[i].append((index[nxt], prob))

    src_idx: List[int] = []
    dst_idx: List[int] = []
    probs: List[float] = []
    for i, row in enumerate(transitions):
        for j, prob in row:
            src_idx.append(i)
            dst_idx.append(j)
            probs.append(prob)

    return (
        np.asarray(src_idx, dtype=np.int64),
        np.asarray(dst_idx, dtype=np.int64),
        np.asarray(probs, dtype=np.float64),
        r,
        index,
    )


def build_mc_arrays(cfg: LatticeConfig) -> Tuple[np.ndarray, np.ndarray]:
    trans_map = build_transition_map(cfg)
    n_states = cfg.N * cfg.N
    max_deg = max(len(v) for v in trans_map.values())
    neighbors = -np.ones((n_states, max_deg), dtype=np.int64)
    cum_probs = np.zeros((n_states, max_deg), dtype=np.float64)

    def idx(xy: Coord) -> int:
        return xy[0] * cfg.N + xy[1]

    for x in range(cfg.N):
        for y in range(cfg.N):
            s = idx((x, y))
            trans = trans_map[(x, y)]
            cum = 0.0
            for k, (nxt, prob) in enumerate(trans):
                neighbors[s, k] = idx(nxt)
                cum += prob
                cum_probs[s, k] = cum
            if len(trans) < max_deg:
                cum_probs[s, len(trans) :] = 1.0
    return neighbors, cum_probs


def build_sampler(cfg: LatticeConfig) -> Dict[Coord, Tuple[List[Coord], np.ndarray]]:
    trans_map = build_transition_map(cfg)
    sampler: Dict[Coord, Tuple[List[Coord], np.ndarray]] = {}
    for xy, trans in trans_map.items():
        if not trans:
            sampler[xy] = ([], np.zeros(0, dtype=np.float64))
            continue
        coords, probs = zip(*trans)
        cum = np.cumsum(np.asarray(probs, dtype=np.float64))
        sampler[xy] = (list(coords), cum)
    return sampler


def build_transition_operator(cfg: LatticeConfig) -> TransitionOperator:
    src_idx, dst_idx, probs, r, index = build_exact_arrays(cfg)
    neighbors, cum_probs = build_mc_arrays(cfg)
    return TransitionOperator(
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        r=r,
        index=index,
        neighbors=neighbors,
        cum_probs=cum_probs,
    )
