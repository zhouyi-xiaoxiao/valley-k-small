#!/usr/bin/env python3
"""Defect (heterogeneity) determinant formula for the z-domain propagator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np

from model_core import Coord, LatticeConfig, DIRECTIONS, global_move_probs, neighbor_with_boundary, state_transitions
from propagator_z_analytic import DefectFreePropagator2D


@dataclass(frozen=True)
class DefectPair:
    u: Coord
    v: Coord
    eta_uv: float
    eta_vu: float = 0.0


def base_transition_dict(cfg: LatticeConfig, xy: Coord) -> Dict[Coord, float]:
    p_left, p_right, p_down, p_up, p_stay = global_move_probs(cfg)
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
        out[nxt] = out.get(nxt, 0.0) + p_move

    out[xy] = out.get(xy, 0.0) + stay
    return out


def defect_pairs_from_config(cfg: LatticeConfig, *, tol: float = 1e-12) -> List[DefectPair]:
    defects: List[DefectPair] = []
    for x in range(cfg.N):
        for y in range(cfg.N):
            xy = (x, y)
            if xy == cfg.target:
                continue
            base = base_transition_dict(cfg, xy)
            mod_list = state_transitions(cfg, xy, include_local=True, include_barriers=True)
            modified: Dict[Coord, float] = {nxt: prob for nxt, prob in mod_list}

            keys = set(base) | set(modified)
            for dest in keys:
                p_base = base.get(dest, 0.0)
                p_mod = modified.get(dest, 0.0)
                delta = p_mod - p_base
                if abs(delta) > tol:
                    eta = -delta
                    defects.append(DefectPair(u=xy, v=dest, eta_uv=eta))
    return defects


class DefectSystem:
    def __init__(
        self,
        *,
        base: DefectFreePropagator2D,
        defects: Sequence[DefectPair],
        start: Coord,
        target: Coord,
    ) -> None:
        self.base = base
        self.defects = list(defects)
        self.start = start
        self.target = target

        nodes = {start, target}
        for d in self.defects:
            nodes.add(d.u)
            nodes.add(d.v)
        self.nodes = sorted(nodes)
        self.node_index = {node: i for i, node in enumerate(self.nodes)}

        self.start_idx = self.node_index[start]
        self.target_idx = self.node_index[target]

        self.u_idx = np.array([self.node_index[d.u] for d in self.defects], dtype=np.int64)
        self.v_idx = np.array([self.node_index[d.v] for d in self.defects], dtype=np.int64)
        self.eta_uv = np.array([d.eta_uv for d in self.defects], dtype=np.complex128)
        self.eta_vu = np.array([d.eta_vu for d in self.defects], dtype=np.complex128)

        self.pair_eval = base.prepare_pair_evaluator(self.nodes, self.nodes)

    def propagators(self, z: complex) -> Tuple[complex, complex]:
        if not self.defects:
            p_start = self.base.propagator(self.start, self.target, z)
            p_target = self.base.propagator(self.target, self.target, z)
            return p_start, p_target

        Q = self.pair_eval.evaluate(z)
        base_start_target = Q[self.start_idx, self.target_idx]
        base_target_target = Q[self.target_idx, self.target_idx]

        U = self.u_idx
        V = self.v_idx
        delta = (-self.eta_uv).astype(np.complex128)

        Q_su = Q[self.start_idx, U]
        Q_tu = Q[self.target_idx, U]
        Q_vu = Q[np.ix_(V, U)]
        Q_vt = Q[V, self.target_idx]

        M = len(self.defects)
        eye = np.eye(M, dtype=np.complex128)
        # Solve the defect system via a linear solve (equivalent to the determinant formula).
        A = eye - z * (Q_vu * delta[None, :])
        b = Q_vt

        try:
            x = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            A_reg = A + 1e-12 * eye
            x = np.linalg.solve(A_reg, b)

        p_start = base_start_target + z * np.dot(Q_su * delta, x)
        p_target = base_target_target + z * np.dot(Q_tu * delta, x)
        return p_start, p_target
