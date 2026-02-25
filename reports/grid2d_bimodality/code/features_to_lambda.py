#!/usr/bin/env python3
"""Feature-to-lambda mapping helpers (local bias, sticky, barriers, doors)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from model_core import Coord


@dataclass(frozen=True)
class LambdaEdge:
    """Lambda-encoding for a directed edge (u -> v) with baseline probability."""

    u: Coord
    v: Coord
    lambda_uv: float
    p_base: float

    def eta(self) -> float:
        """Convert lambda to eta = B - A = -lambda * p_base (used in defect formula)."""
        return -self.lambda_uv * self.p_base


def local_bias_lambda(
    *,
    u: Coord,
    v: Coord,
    p_stay_base: float,
    p_move_base: float,
    delta: float,
) -> List[LambdaEdge]:
    """Move delta*p_stay from stay to (u->v). Returns lambda for move + stay."""
    if p_stay_base <= 0.0 or p_move_base <= 0.0:
        return []
    shift = delta * p_stay_base
    lam_move = -shift / p_move_base
    lam_stay = shift / p_stay_base
    return [
        LambdaEdge(u=u, v=v, lambda_uv=lam_move, p_base=p_move_base),
        LambdaEdge(u=u, v=u, lambda_uv=lam_stay, p_base=p_stay_base),
    ]


def sticky_lambda(u: Coord, p_moves: Dict[Coord, float], factor: float, p_stay_base: float) -> List[LambdaEdge]:
    """Scale all outgoing moves by factor; return lambda edges + stay compensation."""
    out: List[LambdaEdge] = []
    for v, p_base in p_moves.items():
        lam = 1.0 - factor
        out.append(LambdaEdge(u=u, v=v, lambda_uv=lam, p_base=p_base))
    delta_stay = (1.0 - factor) * (1.0 - p_stay_base)
    if p_stay_base > 0.0 and abs(delta_stay) > 0.0:
        lam_stay = -delta_stay / p_stay_base
        out.append(LambdaEdge(u=u, v=u, lambda_uv=lam_stay, p_base=p_stay_base))
    return out


def barrier_lambda(u: Coord, v: Coord, p_base: float) -> LambdaEdge:
    """Fully reflecting barrier: crossing prob set to zero -> lambda = 1."""
    return LambdaEdge(u=u, v=v, lambda_uv=1.0, p_base=p_base)


def door_lambda(u: Coord, v: Coord, p_base: float, p_pass: float) -> LambdaEdge:
    """Permeable door: crossing prob multiplied by p_pass -> lambda = 1 - p_pass."""
    return LambdaEdge(u=u, v=v, lambda_uv=(1.0 - p_pass), p_base=p_base)
