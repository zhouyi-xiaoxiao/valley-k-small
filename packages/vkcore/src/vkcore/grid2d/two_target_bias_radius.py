"""Exact 2D two-target first-passage scaffold with bias-radius geometry."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, hypot, pi, sin
from typing import Iterable, Sequence

import numpy as np

Coord = tuple[int, int]

DIR_VEC: dict[str, Coord] = {
    "E": (1, 0),
    "W": (-1, 0),
    "N": (0, 1),
    "S": (0, -1),
}

DIR_ANGLE: dict[str, float] = {
    "E": 0.0,
    "N": 0.5 * pi,
    "W": pi,
    "S": -0.5 * pi,
}


@dataclass(frozen=True)
class TransitionKernel:
    """Sparse row-stochastic transition kernel on a rectangular grid."""

    Lx: int
    Ly: int
    src: np.ndarray
    dst: np.ndarray
    prob: np.ndarray
    absorbing: frozenset[Coord]
    q: float
    bias_strength: float
    bias_direction: str
    bias_rule: str
    boundary_rule: str = "reflecting attempted-outside-stays"

    @property
    def n_states(self) -> int:
        return self.Lx * self.Ly

    def index(self, xy: Coord) -> int:
        x, y = xy
        if not (0 <= x < self.Lx and 0 <= y < self.Ly):
            raise ValueError(f"coordinate out of bounds: {xy}")
        return y * self.Lx + x

    def row_sums(self) -> np.ndarray:
        sums = np.zeros(self.n_states, dtype=np.float64)
        np.add.at(sums, self.src, self.prob)
        return sums


@dataclass(frozen=True)
class NearTargetCandidate:
    coord: Coord
    r_requested: float
    theta_requested: float
    r_actual: float
    theta_actual: float
    bias_direction: str


@dataclass(frozen=True)
class ChannelDecomposition:
    t: np.ndarray
    f_total: np.ndarray
    f_near: np.ndarray
    f_far: np.ndarray
    survival: np.ndarray

    @property
    def row_stochasticity_error(self) -> float:
        raise AttributeError("row-stochasticity is a kernel property, not a decomposition property")

    @property
    def mass_balance_error(self) -> float:
        absorbed = np.cumsum(self.f_total)
        return float(np.max(np.abs(1.0 - self.survival - absorbed)))

    @property
    def decomposition_error(self) -> float:
        return float(np.max(np.abs(self.f_total - self.f_near - self.f_far)))


def _canonical_direction(direction: str) -> str:
    d = direction.upper()
    if d not in DIR_VEC:
        raise ValueError(f"bias_direction must be one of {sorted(DIR_VEC)}")
    return d


def _check_coord(xy: Coord, Lx: int, Ly: int, *, name: str) -> None:
    x, y = xy
    if not (0 <= x < Lx and 0 <= y < Ly):
        raise ValueError(f"{name} out of bounds: {xy}")


def _wrap_angle(theta: float) -> float:
    return atan2(sin(theta), cos(theta))


def build_reflecting_kernel(
    *,
    Lx: int,
    Ly: int,
    q: float,
    bias_strength: float,
    bias_direction: str,
    absorbing: Iterable[Coord] = (),
) -> TransitionKernel:
    """Build a rectangular-grid transition kernel with absorbing self-loops.

    The global bias rule is deliberately simple for scans: start from four
    nearest-neighbour move probabilities q/4 and a stay probability 1-q, then
    move absolute probability mass b from stay to one global direction.
    Therefore 0 <= b <= 1-q is required and row sums remain exactly one up to
    floating-point arithmetic.
    """

    if Lx <= 0 or Ly <= 0:
        raise ValueError("Lx and Ly must be positive")
    if not (0.0 <= q <= 1.0):
        raise ValueError("q must be in [0, 1]")
    if not (0.0 <= bias_strength <= 1.0 - q + 1e-15):
        raise ValueError("bias_strength must satisfy 0 <= b <= 1-q")

    direction = _canonical_direction(bias_direction)
    absorbing_set = frozenset((int(x), int(y)) for x, y in absorbing)
    for target in absorbing_set:
        _check_coord(target, Lx, Ly, name="absorbing target")

    base_move = float(q) / 4.0
    stay = 1.0 - float(q) - float(bias_strength)
    moves = {d: base_move for d in DIR_VEC}
    moves[direction] += float(bias_strength)

    src: list[int] = []
    dst: list[int] = []
    prob: list[float] = []

    def idx(xy: Coord) -> int:
        return xy[1] * Lx + xy[0]

    for y in range(Ly):
        for x in range(Lx):
            xy = (x, y)
            i = idx(xy)
            if xy in absorbing_set:
                src.append(i)
                dst.append(i)
                prob.append(1.0)
                continue

            row: dict[int, float] = {i: stay}
            for d, p_move in moves.items():
                dx, dy = DIR_VEC[d]
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= Lx or ny < 0 or ny >= Ly:
                    row[i] = row.get(i, 0.0) + p_move
                else:
                    j = idx((nx, ny))
                    row[j] = row.get(j, 0.0) + p_move

            row_sum = float(sum(row.values()))
            if abs(row_sum - 1.0) > 1e-12:
                raise ValueError(f"row sum != 1 at {xy}: {row_sum}")
            if min(row.values()) < -1e-15:
                raise ValueError(f"negative probability at {xy}")
            for j, p in row.items():
                src.append(i)
                dst.append(j)
                prob.append(float(p))

    return TransitionKernel(
        Lx=Lx,
        Ly=Ly,
        src=np.asarray(src, dtype=np.int64),
        dst=np.asarray(dst, dtype=np.int64),
        prob=np.asarray(prob, dtype=np.float64),
        absorbing=absorbing_set,
        q=float(q),
        bias_strength=float(bias_strength),
        bias_direction=direction,
        bias_rule="global absolute stay-to-direction shift: p_dir=q/4+b, p_stay=1-q-b",
    )


def near_target_candidates(
    *,
    Lx: int,
    Ly: int,
    start: Coord,
    radii: Sequence[float],
    thetas: Sequence[float],
    bias_direction: str,
    exclude: Iterable[Coord] = (),
) -> list[NearTargetCandidate]:
    """Generate unique near-target candidates by radius and angle.

    theta is measured relative to the bias direction. Candidates that round
    outside the grid, equal the start, or fall in exclude are skipped; theta is
    not aggregated.
    """

    _check_coord(start, Lx, Ly, name="start")
    direction = _canonical_direction(bias_direction)
    base = DIR_ANGLE[direction]
    blocked = set(exclude)
    blocked.add(start)
    out: list[NearTargetCandidate] = []
    seen: set[Coord] = set()

    for r in radii:
        if r <= 0.0:
            raise ValueError("radii must be positive")
        for theta in thetas:
            angle = base + float(theta)
            x = int(round(start[0] + float(r) * cos(angle)))
            y = int(round(start[1] + float(r) * sin(angle)))
            coord = (x, y)
            if coord in blocked or coord in seen:
                continue
            if not (0 <= x < Lx and 0 <= y < Ly):
                continue
            dx = x - start[0]
            dy = y - start[1]
            actual_r = hypot(dx, dy)
            actual_theta = _wrap_angle(atan2(dy, dx) - base)
            out.append(
                NearTargetCandidate(
                    coord=coord,
                    r_requested=float(r),
                    theta_requested=float(theta),
                    r_actual=float(actual_r),
                    theta_actual=float(actual_theta),
                    bias_direction=direction,
                )
            )
            seen.add(coord)
    return out


def exact_near_far_decomposition(
    *,
    kernel: TransitionKernel,
    start: Coord,
    near_target: Coord,
    far_target: Coord,
    t_max: int,
    survival_tol: float = 0.0,
) -> ChannelDecomposition:
    """Compute exact first-passage mass split by near and far target channel."""

    if near_target == far_target:
        raise ValueError("near_target and far_target must differ")
    if t_max < 0:
        raise ValueError("t_max must be nonnegative")
    for name, xy in (("start", start), ("near_target", near_target), ("far_target", far_target)):
        _check_coord(xy, kernel.Lx, kernel.Ly, name=name)
    if start in {near_target, far_target}:
        raise ValueError("start must not be absorbing")
    if not {near_target, far_target}.issubset(kernel.absorbing):
        raise ValueError("kernel absorbing set must include near and far targets")

    near_idx = kernel.index(near_target)
    far_idx = kernel.index(far_target)

    p = np.zeros(kernel.n_states, dtype=np.float64)
    p[kernel.index(start)] = 1.0

    times = [0]
    f_near = [0.0]
    f_far = [0.0]
    f_total = [0.0]
    survival = [1.0]

    for t in range(1, t_max + 1):
        p_next = np.zeros_like(p)
        np.add.at(p_next, kernel.dst, p[kernel.src] * kernel.prob)

        hit_near = float(p_next[near_idx])
        hit_far = float(p_next[far_idx])
        p_next[near_idx] = 0.0
        p_next[far_idx] = 0.0
        s = float(p_next.sum())

        times.append(t)
        f_near.append(hit_near)
        f_far.append(hit_far)
        f_total.append(hit_near + hit_far)
        survival.append(s)

        p = p_next
        if s <= survival_tol:
            break

    return ChannelDecomposition(
        t=np.asarray(times, dtype=np.int64),
        f_total=np.asarray(f_total, dtype=np.float64),
        f_near=np.asarray(f_near, dtype=np.float64),
        f_far=np.asarray(f_far, dtype=np.float64),
        survival=np.asarray(survival, dtype=np.float64),
    )


def validation_errors(kernel: TransitionKernel, decomp: ChannelDecomposition) -> dict[str, float]:
    row_sums = kernel.row_sums()
    return {
        "nonnegative_min_probability": float(np.min(kernel.prob)),
        "row_stochasticity_error": float(np.max(np.abs(row_sums - 1.0))),
        "mass_balance_error": decomp.mass_balance_error,
        "decomposition_error": decomp.decomposition_error,
    }
