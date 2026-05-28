from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv

import numpy as np

from vkcore.validation import (
    check_channel_decomposition,
    check_nonnegative,
    check_row_stochastic,
    decomposition_error,
    mass_balance_error,
)


@dataclass(frozen=True)
class RingTwoTargetConfig:
    """Exact 1D periodic-ring first-passage configuration with two targets."""

    L: int
    start: int
    target1: int
    target2: int
    K: int = 2
    q: float = 1.0
    drift: float = 0.0
    beta: float = 0.0
    shortcut_src: int | None = None
    shortcut_dst: int | None = None
    max_steps: int = 1000
    eps_survival: float = 0.0


@dataclass(frozen=True)
class RingTwoTargetResult:
    config: RingTwoTargetConfig
    t: np.ndarray
    f_total: np.ndarray
    f_target1: np.ndarray
    f_target2: np.ndarray
    survival: np.ndarray
    transition_matrix: np.ndarray

    def row_stochasticity_error(self) -> float:
        row_sums = self.transition_matrix.sum(axis=1)
        return float(np.max(np.abs(row_sums - 1.0))) if row_sums.size else 0.0

    def mass_balance_error(self) -> float:
        # This report stores f(0)=0 and survival(0)=1. The balance identity is
        # f(t)=S(t-1)-S(t) for t>=1, so skip the leading zero density.
        return mass_balance_error(self.f_total[1:], self.survival)

    def channel_decomposition_error(self) -> float:
        return decomposition_error(self.f_total, [self.f_target1, self.f_target2])


def _mod_index(value: int, L: int) -> int:
    return int(value) % int(L)


def validate_config(cfg: RingTwoTargetConfig) -> None:
    if cfg.L < 3:
        raise ValueError("L must be at least 3")
    if cfg.K not in (2, 4):
        raise ValueError(f"unsupported K={cfg.K}; expected 2 or 4")
    if not (0.0 <= cfg.q <= 1.0):
        raise ValueError("q must lie in [0, 1]")
    if not (-1.0 <= cfg.drift <= 1.0):
        raise ValueError("drift must lie in [-1, 1]")
    if not (0.0 <= cfg.beta <= 1.0):
        raise ValueError("beta must lie in [0, 1]")
    if cfg.max_steps < 0:
        raise ValueError("max_steps must be nonnegative")
    if cfg.eps_survival < 0:
        raise ValueError("eps_survival must be nonnegative")

    t1 = _mod_index(cfg.target1, cfg.L)
    t2 = _mod_index(cfg.target2, cfg.L)
    start = _mod_index(cfg.start, cfg.L)
    if t1 == t2:
        raise ValueError("target1 and target2 must be distinct")
    if start in {t1, t2}:
        raise ValueError("initial condition must satisfy start not in absorbing targets")
    if (cfg.shortcut_src is None) != (cfg.shortcut_dst is None):
        raise ValueError("shortcut_src and shortcut_dst must be provided together")


def build_transition_matrix(cfg: RingTwoTargetConfig) -> np.ndarray:
    """Build a row-stochastic transition matrix with absorbing target rows."""

    validate_config(cfg)
    L = int(cfg.L)
    t1 = _mod_index(cfg.target1, L)
    t2 = _mod_index(cfg.target2, L)
    targets = {t1, t2}

    P = np.zeros((L, L), dtype=float)
    p_plus = cfg.q * (1.0 + cfg.drift) / 2.0
    p_minus = cfg.q * (1.0 - cfg.drift) / 2.0
    p_stay = 1.0 - cfg.q

    for x in range(L):
        if x in targets:
            P[x, x] = 1.0
            continue

        P[x, x] += p_stay
        if cfg.K == 2:
            P[x, (x + 1) % L] += p_plus
            P[x, (x - 1) % L] += p_minus
        else:
            P[x, (x + 1) % L] += p_plus / 2.0
            P[x, (x + 2) % L] += p_plus / 2.0
            P[x, (x - 1) % L] += p_minus / 2.0
            P[x, (x - 2) % L] += p_minus / 2.0

    if cfg.beta > 0 and cfg.shortcut_src is not None and cfg.shortcut_dst is not None:
        src = _mod_index(cfg.shortcut_src, L)
        dst = _mod_index(cfg.shortcut_dst, L)
        if src not in targets:
            p_shortcut = cfg.beta * p_stay
            P[src, src] -= p_shortcut
            P[src, dst] += p_shortcut

    check_nonnegative(P)
    check_row_stochastic(P)
    return P


def exact_two_target_fpt(cfg: RingTwoTargetConfig) -> RingTwoTargetResult:
    """Propagate the exact two-target first-passage distribution by channels."""

    P = build_transition_matrix(cfg)
    L = int(cfg.L)
    start = _mod_index(cfg.start, L)
    target1 = _mod_index(cfg.target1, L)
    target2 = _mod_index(cfg.target2, L)

    p = np.zeros(L, dtype=float)
    p[start] = 1.0

    f_total: list[float] = [0.0]
    f_target1: list[float] = [0.0]
    f_target2: list[float] = [0.0]
    survival: list[float] = [1.0]

    for _step in range(1, int(cfg.max_steps) + 1):
        p_next = p @ P
        hit1 = float(p_next[target1])
        hit2 = float(p_next[target2])

        f_target1.append(hit1)
        f_target2.append(hit2)
        f_total.append(hit1 + hit2)

        # Absorbing targets stop the first-passage process immediately.
        p_next[target1] = 0.0
        p_next[target2] = 0.0
        p = p_next
        survival.append(float(p.sum()))
        if survival[-1] <= cfg.eps_survival:
            break

    t = np.arange(len(f_total), dtype=int)
    return RingTwoTargetResult(
        config=cfg,
        t=t,
        f_total=np.asarray(f_total, dtype=float),
        f_target1=np.asarray(f_target1, dtype=float),
        f_target2=np.asarray(f_target2, dtype=float),
        survival=np.asarray(survival, dtype=float),
        transition_matrix=P,
    )


def validate_result(
    result: RingTwoTargetResult,
    *,
    row_tol: float = 1e-12,
    mass_tol: float = 1e-10,
    decomposition_tol: float = 1e-10,
) -> dict[str, float]:
    """Validate stochasticity, mass balance, and target-channel decomposition."""

    check_row_stochastic(result.transition_matrix, tol=row_tol)
    mass_err = result.mass_balance_error()
    if mass_err > mass_tol:
        raise ValueError(f"mass balance failed: error={mass_err:g}")
    check_channel_decomposition(
        result.f_total,
        [result.f_target1, result.f_target2],
        tol=decomposition_tol,
    )
    return {
        "row_stochasticity_error": result.row_stochasticity_error(),
        "mass_balance_error": mass_err,
        "channel_decomposition_error": result.channel_decomposition_error(),
    }


def save_decomposition_csv(path: Path, result: RingTwoTargetResult) -> None:
    """Save t, total FPT, target-channel FPTs, and survival."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["t", "f_total", "f_target1", "f_target2", "survival"])
        for row in zip(
            result.t,
            result.f_total,
            result.f_target1,
            result.f_target2,
            result.survival,
            strict=True,
        ):
            writer.writerow(row)
