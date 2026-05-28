"""Exact validation utilities for 1D reflecting two-walker encounters.

The one-dimensional two-walker process is represented as a product-chain
process on states ``(x1, x2)``. Encounter states are the diagonal ``x1 == x2``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv

import numpy as np


@dataclass(frozen=True)
class EncounterCase:
    L: int
    x1_0: int
    x2_0: int
    q0: float
    rho: float
    tail_mass_tol: float = 1e-14
    mean_tol: float = 1e-10
    max_steps: int = 200_000


@dataclass(frozen=True)
class DistributionResult:
    times: np.ndarray
    probabilities: np.ndarray
    survival: np.ndarray
    mean: float
    mass_balance_error: float
    tail_mass: float


@dataclass(frozen=True)
class EncounterValidationResult:
    case: EncounterCase
    Q1: float
    Q2: float
    exact_mean: float
    distribution_mean: float
    mean_difference: float
    p1_row_error: float
    p2_row_error: float
    p1_min_entry: float
    p2_min_entry: float
    joint_row_error: float
    absorbing_row_error: float
    mass_balance_error: float
    tail_mass: float
    distribution_steps: int


@dataclass(frozen=True)
class ContributionWindow:
    name: str
    start_t: int
    end_t: int
    center_t: int
    total_mass: float
    by_position: np.ndarray


@dataclass(frozen=True)
class DiagonalDecompositionResult:
    case: EncounterCase
    Q1: float
    Q2: float
    times: np.ndarray
    f_total: np.ndarray
    f_by_position: np.ndarray
    survival: np.ndarray
    mean: float
    p1_row_error: float
    p2_row_error: float
    joint_row_error: float
    decomposition_error: float
    mass_balance_error: float
    tail_mass: float
    windows: tuple[ContributionWindow, ...]


def fixed_total_mobility(q0: float, rho: float) -> tuple[float, float]:
    """Return ``(Q1, Q2)`` under fixed total mobility for a mobility ratio."""

    q0_f = float(q0)
    rho_f = float(rho)
    if not np.isfinite(q0_f) or q0_f <= 0.0:
        raise ValueError(f"q0 must be positive and finite, got {q0!r}")
    if not np.isfinite(rho_f) or rho_f <= 0.0:
        raise ValueError(f"rho must be positive and finite, got {rho!r}")

    q1 = 2.0 * q0_f * rho_f / (1.0 + rho_f)
    q2 = 2.0 * q0_f / (1.0 + rho_f)
    if q1 > 1.0 + 1e-15 or q2 > 1.0 + 1e-15:
        raise ValueError(
            "fixed-total mobility produced Q_i > 1: "
            f"q0={q0_f:g}, rho={rho_f:g}, Q1={q1:g}, Q2={q2:g}"
        )
    return min(q1, 1.0), min(q2, 1.0)


def build_reflecting_lazy_transition(L: int, Q: float) -> np.ndarray:
    """Build a 1D lazy nearest-neighbor transition matrix with reflecting ends.

    The reflecting rule is attempted-outside-stays: at ``0`` the left attempt
    remains at ``0``; at ``L-1`` the right attempt remains at ``L-1``.
    """

    L_i = int(L)
    Q_f = float(Q)
    if L_i < 2:
        raise ValueError(f"L must be at least 2, got {L!r}")
    if not np.isfinite(Q_f) or Q_f < 0.0 or Q_f > 1.0:
        raise ValueError(f"Q must lie in [0, 1], got {Q!r}")

    P = np.zeros((L_i, L_i), dtype=float)
    for x in range(L_i):
        P[x, x] += 1.0 - Q_f
        left = x - 1
        right = x + 1
        if left < 0:
            P[x, x] += Q_f / 2.0
        else:
            P[x, left] += Q_f / 2.0
        if right >= L_i:
            P[x, x] += Q_f / 2.0
        else:
            P[x, right] += Q_f / 2.0
    return P


def row_stochastic_error(P: np.ndarray) -> float:
    arr = np.asarray(P, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"transition matrix must be 2D, got ndim={arr.ndim}")
    return float(np.max(np.abs(arr.sum(axis=1) - 1.0))) if arr.size else 0.0


def min_entry(P: np.ndarray) -> float:
    arr = np.asarray(P, dtype=float)
    return float(np.min(arr)) if arr.size else 0.0


def state_index(L: int, x1: int, x2: int) -> int:
    return int(x1) * int(L) + int(x2)


def state_pair(L: int, idx: int) -> tuple[int, int]:
    return divmod(int(idx), int(L))


def diagonal_indices(L: int) -> np.ndarray:
    return np.array([state_index(L, k, k) for k in range(int(L))], dtype=int)


def transient_indices(L: int) -> np.ndarray:
    return np.array(
        [state_index(L, x1, x2) for x1 in range(int(L)) for x2 in range(int(L)) if x1 != x2],
        dtype=int,
    )


def build_joint_transition(P1: np.ndarray, P2: np.ndarray) -> np.ndarray:
    """Build the synchronous independent product-chain transition matrix."""

    if P1.shape != P2.shape or P1.ndim != 2 or P1.shape[0] != P1.shape[1]:
        raise ValueError(f"P1 and P2 must be square matrices with the same shape, got {P1.shape}, {P2.shape}")
    return np.kron(P1, P2)


def build_absorbing_joint_transition(P1: np.ndarray, P2: np.ndarray) -> np.ndarray:
    """Build the full joint matrix with diagonal encounter states absorbing."""

    L = int(P1.shape[0])
    joint = build_joint_transition(P1, P2)
    absorbing = joint.copy()
    for idx in diagonal_indices(L):
        absorbing[idx, :] = 0.0
        absorbing[idx, idx] = 1.0
    return absorbing


def fundamental_mean(P1: np.ndarray, P2: np.ndarray, x1_0: int, x2_0: int) -> tuple[float, np.ndarray, np.ndarray]:
    """Return exact encounter mean and the transient block used to compute it."""

    L = int(P1.shape[0])
    if int(x1_0) == int(x2_0):
        raise ValueError("initial positions must satisfy x1_0 != x2_0")
    if not (0 <= int(x1_0) < L and 0 <= int(x2_0) < L):
        raise ValueError(f"initial positions must lie in {{0, ..., L-1}}, got {(x1_0, x2_0)} for L={L}")

    joint = build_joint_transition(P1, P2)
    transient = transient_indices(L)
    start_state = state_index(L, x1_0, x2_0)
    start_pos = int(np.where(transient == start_state)[0][0])
    M = joint[np.ix_(transient, transient)]
    expected = np.linalg.solve(np.eye(M.shape[0]) - M, np.ones(M.shape[0], dtype=float))
    return float(expected[start_pos]), M, transient


def forward_distribution(
    M: np.ndarray,
    transient: np.ndarray,
    L: int,
    x1_0: int,
    x2_0: int,
    *,
    exact_mean: float | None = None,
    tail_mass_tol: float = 1e-14,
    mean_tol: float = 1e-10,
    max_steps: int = 200_000,
) -> DistributionResult:
    """Compute the encounter distribution by forward propagation."""

    start_state = state_index(L, x1_0, x2_0)
    matches = np.where(transient == start_state)[0]
    if matches.size != 1:
        raise ValueError("initial transient state not found")

    p = np.zeros(M.shape[0], dtype=float)
    p[int(matches[0])] = 1.0
    ones = np.ones(M.shape[0], dtype=float)
    row_hit = 1.0 - M.sum(axis=1)

    times: list[int] = []
    probabilities: list[float] = []
    survival: list[float] = [1.0]
    mean = 0.0
    mass_err = 0.0

    for step in range(1, int(max_steps) + 1):
        hit = float(np.dot(p, row_hit))
        p_next = np.dot(p, M)
        next_survival = float(np.dot(p_next, ones))

        times.append(step)
        probabilities.append(hit)
        survival.append(next_survival)
        mean += float(step) * hit
        mass_err = max(mass_err, abs(hit - (survival[-2] - next_survival)))

        p = p_next
        mean_ok = exact_mean is None or abs(mean - float(exact_mean)) <= float(mean_tol)
        if next_survival <= float(tail_mass_tol) and mean_ok:
            break
    else:
        raise RuntimeError(
            "forward propagation did not meet tail/mean tolerance within "
            f"{max_steps} steps; tail={survival[-1]:.3e}, mean={mean:.12g}"
        )

    return DistributionResult(
        times=np.array(times, dtype=int),
        probabilities=np.array(probabilities, dtype=float),
        survival=np.array(survival, dtype=float),
        mean=float(mean),
        mass_balance_error=float(mass_err),
        tail_mass=float(survival[-1]),
    )


def forward_diagonal_decomposition(
    P1: np.ndarray,
    P2: np.ndarray,
    x1_0: int,
    x2_0: int,
    *,
    tail_mass_tol: float = 1e-14,
    max_steps: int = 200_000,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float, float]:
    """Compute ``f_k(t)`` by recording diagonal mass before clearing it.

    The update follows the report algorithm literally: propagate the full joint
    distribution, record the diagonal entries of the next joint array as
    position-resolved encounter mass, sum them as ``f_E(t)``, then clear the
    diagonal before the next transient step.
    """

    L = int(P1.shape[0])
    if int(x1_0) == int(x2_0):
        raise ValueError("initial positions must satisfy x1_0 != x2_0")
    if not (0 <= int(x1_0) < L and 0 <= int(x2_0) < L):
        raise ValueError(f"initial positions out of range for L={L}: {(x1_0, x2_0)}")

    joint = build_joint_transition(P1, P2)
    p = np.zeros(L * L, dtype=float)
    p[state_index(L, x1_0, x2_0)] = 1.0

    times: list[int] = []
    f_total: list[float] = []
    f_by_position: list[np.ndarray] = []
    survival: list[float] = [1.0]
    mean = 0.0
    mass_err = 0.0
    decomp_err = 0.0

    for step in range(1, int(max_steps) + 1):
        p_next = np.dot(p, joint)
        J_next = p_next.reshape((L, L)).copy()
        diag_mass = np.diag(J_next).copy()
        hit = float(np.sum(diag_mass))

        diag = np.diag_indices(L)
        J_next[diag] = 0.0
        p = J_next.reshape(L * L)
        next_survival = float(np.sum(p))

        times.append(step)
        f_total.append(hit)
        f_by_position.append(diag_mass)
        survival.append(next_survival)
        mean += float(step) * hit
        mass_err = max(mass_err, abs(hit - (survival[-2] - next_survival)))
        decomp_err = max(decomp_err, abs(hit - float(np.sum(diag_mass))))

        if next_survival <= float(tail_mass_tol):
            break
    else:
        raise RuntimeError(
            "diagonal decomposition did not meet tail tolerance within "
            f"{max_steps} steps; tail={survival[-1]:.3e}, mean={mean:.12g}"
        )

    return (
        np.array(times, dtype=int),
        np.array(f_total, dtype=float),
        np.vstack(f_by_position) if f_by_position else np.empty((0, L), dtype=float),
        np.array(survival, dtype=float),
        float(mean),
        float(mass_err),
        float(decomp_err),
    )


def candidate_windows(
    times: np.ndarray,
    f_total: np.ndarray,
    f_by_position: np.ndarray,
    *,
    radius: int = 3,
    min_late_ratio: float = 0.02,
) -> tuple[ContributionWindow, ...]:
    """Return early and optional candidate-late contribution windows."""

    if times.size == 0 or f_total.size == 0:
        return ()

    first_peak_idx = int(np.argmax(f_total))
    windows: list[ContributionWindow] = [
        _contribution_window("early", times, f_total, f_by_position, first_peak_idx, radius)
    ]

    if f_total.size >= 3:
        maxima = np.where((f_total[1:-1] > f_total[:-2]) & (f_total[1:-1] >= f_total[2:]))[0] + 1
        late_candidates = [
            int(idx)
            for idx in maxima
            if int(idx) > first_peak_idx + radius
            and float(f_total[idx]) >= float(min_late_ratio) * float(f_total[first_peak_idx])
        ]
        if late_candidates:
            late_idx = max(late_candidates, key=lambda idx: float(f_total[idx]))
            windows.append(
                _contribution_window("candidate_late", times, f_total, f_by_position, late_idx, radius)
            )

    return tuple(windows)


def _contribution_window(
    name: str,
    times: np.ndarray,
    f_total: np.ndarray,
    f_by_position: np.ndarray,
    center_idx: int,
    radius: int,
) -> ContributionWindow:
    lo = max(0, int(center_idx) - int(radius))
    hi = min(f_total.size - 1, int(center_idx) + int(radius))
    by_position = np.sum(f_by_position[lo : hi + 1, :], axis=0)
    return ContributionWindow(
        name=name,
        start_t=int(times[lo]),
        end_t=int(times[hi]),
        center_t=int(times[int(center_idx)]),
        total_mass=float(np.sum(f_total[lo : hi + 1])),
        by_position=by_position,
    )


def validate_diagonal_case(case: EncounterCase) -> DiagonalDecompositionResult:
    """Run diagonal-position decomposition and validation diagnostics."""

    Q1, Q2 = fixed_total_mobility(case.q0, case.rho)
    P1 = build_reflecting_lazy_transition(case.L, Q1)
    P2 = build_reflecting_lazy_transition(case.L, Q2)
    joint = build_joint_transition(P1, P2)
    times, f_total, f_by_position, survival, mean, mass_err, decomp_err = forward_diagonal_decomposition(
        P1,
        P2,
        case.x1_0,
        case.x2_0,
        tail_mass_tol=case.tail_mass_tol,
        max_steps=case.max_steps,
    )

    direct_decomp_err = (
        float(np.max(np.abs(f_total - np.sum(f_by_position, axis=1)))) if f_total.size else 0.0
    )
    decomp_err = max(decomp_err, direct_decomp_err)

    return DiagonalDecompositionResult(
        case=case,
        Q1=Q1,
        Q2=Q2,
        times=times,
        f_total=f_total,
        f_by_position=f_by_position,
        survival=survival,
        mean=mean,
        p1_row_error=row_stochastic_error(P1),
        p2_row_error=row_stochastic_error(P2),
        joint_row_error=row_stochastic_error(joint),
        decomposition_error=decomp_err,
        mass_balance_error=mass_err,
        tail_mass=float(survival[-1]) if survival.size else 0.0,
        windows=candidate_windows(times, f_total, f_by_position),
    )


def validate_case(case: EncounterCase) -> EncounterValidationResult:
    """Run all exact-mean, forward-mean, stochasticity, and mass-balance checks."""

    if case.x1_0 == case.x2_0:
        raise ValueError("initial positions must satisfy x1_0 != x2_0")
    if not (0 <= case.x1_0 < case.L and 0 <= case.x2_0 < case.L):
        raise ValueError(f"initial positions out of range for L={case.L}: {(case.x1_0, case.x2_0)}")

    Q1, Q2 = fixed_total_mobility(case.q0, case.rho)
    P1 = build_reflecting_lazy_transition(case.L, Q1)
    P2 = build_reflecting_lazy_transition(case.L, Q2)
    joint = build_joint_transition(P1, P2)
    absorbing = build_absorbing_joint_transition(P1, P2)

    exact_mean, M, transient = fundamental_mean(P1, P2, case.x1_0, case.x2_0)
    dist = forward_distribution(
        M,
        transient,
        case.L,
        case.x1_0,
        case.x2_0,
        exact_mean=exact_mean,
        tail_mass_tol=case.tail_mass_tol,
        mean_tol=case.mean_tol,
        max_steps=case.max_steps,
    )
    mean_diff = abs(exact_mean - dist.mean)

    return EncounterValidationResult(
        case=case,
        Q1=Q1,
        Q2=Q2,
        exact_mean=exact_mean,
        distribution_mean=dist.mean,
        mean_difference=mean_diff,
        p1_row_error=row_stochastic_error(P1),
        p2_row_error=row_stochastic_error(P2),
        p1_min_entry=min_entry(P1),
        p2_min_entry=min_entry(P2),
        joint_row_error=row_stochastic_error(joint),
        absorbing_row_error=row_stochastic_error(absorbing),
        mass_balance_error=dist.mass_balance_error,
        tail_mass=dist.tail_mass,
        distribution_steps=int(dist.times[-1]) if dist.times.size else 0,
    )


def assert_validation_thresholds(
    result: EncounterValidationResult,
    *,
    row_tol: float = 1e-12,
    mass_tol: float = 1e-10,
    mean_tol: float = 1e-8,
) -> None:
    """Raise ``AssertionError`` if the report-level validation thresholds fail."""

    if result.p1_row_error >= row_tol:
        raise AssertionError(f"P1 row-stochasticity error {result.p1_row_error:.3e} >= {row_tol:.3e}")
    if result.p2_row_error >= row_tol:
        raise AssertionError(f"P2 row-stochasticity error {result.p2_row_error:.3e} >= {row_tol:.3e}")
    if result.joint_row_error >= row_tol:
        raise AssertionError(f"joint row-stochasticity error {result.joint_row_error:.3e} >= {row_tol:.3e}")
    if result.absorbing_row_error >= row_tol:
        raise AssertionError(f"absorbing row-stochasticity error {result.absorbing_row_error:.3e} >= {row_tol:.3e}")
    if result.p1_min_entry < -row_tol:
        raise AssertionError(f"P1 has negative entry {result.p1_min_entry:.3e}")
    if result.p2_min_entry < -row_tol:
        raise AssertionError(f"P2 has negative entry {result.p2_min_entry:.3e}")
    if result.mass_balance_error >= mass_tol:
        raise AssertionError(f"mass-balance error {result.mass_balance_error:.3e} >= {mass_tol:.3e}")
    if result.mean_difference >= mean_tol:
        raise AssertionError(f"mean difference {result.mean_difference:.3e} >= {mean_tol:.3e}")


def assert_diagonal_thresholds(
    result: DiagonalDecompositionResult,
    *,
    row_tol: float = 1e-12,
    mass_tol: float = 1e-10,
    decomposition_tol: float = 1e-10,
) -> None:
    """Raise ``AssertionError`` if diagonal-decomposition validation fails."""

    if result.p1_row_error >= row_tol:
        raise AssertionError(f"P1 row-stochasticity error {result.p1_row_error:.3e} >= {row_tol:.3e}")
    if result.p2_row_error >= row_tol:
        raise AssertionError(f"P2 row-stochasticity error {result.p2_row_error:.3e} >= {row_tol:.3e}")
    if result.joint_row_error >= row_tol:
        raise AssertionError(f"joint row-stochasticity error {result.joint_row_error:.3e} >= {row_tol:.3e}")
    if result.mass_balance_error >= mass_tol:
        raise AssertionError(f"mass-balance error {result.mass_balance_error:.3e} >= {mass_tol:.3e}")
    if result.decomposition_error >= decomposition_tol:
        raise AssertionError(
            f"diagonal decomposition error {result.decomposition_error:.3e} >= {decomposition_tol:.3e}"
        )


def write_results_csv(results: list[EncounterValidationResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "L",
                "x1_0",
                "x2_0",
                "q0",
                "rho",
                "Q1",
                "Q2",
                "exact_mean",
                "distribution_mean",
                "mean_difference",
                "p1_row_error",
                "p2_row_error",
                "joint_row_error",
                "absorbing_row_error",
                "mass_balance_error",
                "tail_mass",
                "distribution_steps",
            ],
        )
        writer.writeheader()
        for result in results:
            c = result.case
            writer.writerow(
                {
                    "L": c.L,
                    "x1_0": c.x1_0,
                    "x2_0": c.x2_0,
                    "q0": c.q0,
                    "rho": c.rho,
                    "Q1": result.Q1,
                    "Q2": result.Q2,
                    "exact_mean": f"{result.exact_mean:.16g}",
                    "distribution_mean": f"{result.distribution_mean:.16g}",
                    "mean_difference": f"{result.mean_difference:.6e}",
                    "p1_row_error": f"{result.p1_row_error:.6e}",
                    "p2_row_error": f"{result.p2_row_error:.6e}",
                    "joint_row_error": f"{result.joint_row_error:.6e}",
                    "absorbing_row_error": f"{result.absorbing_row_error:.6e}",
                    "mass_balance_error": f"{result.mass_balance_error:.6e}",
                    "tail_mass": f"{result.tail_mass:.6e}",
                    "distribution_steps": result.distribution_steps,
                }
            )


def write_total_distribution_csv(result: DiagonalDecompositionResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["t", "f_total", "survival_before", "survival_after"],
        )
        writer.writeheader()
        for i, t in enumerate(result.times):
            writer.writerow(
                {
                    "t": int(t),
                    "f_total": f"{result.f_total[i]:.16e}",
                    "survival_before": f"{result.survival[i]:.16e}",
                    "survival_after": f"{result.survival[i + 1]:.16e}",
                }
            )


def write_diagonal_contribution_csv(result: DiagonalDecompositionResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["t", "f_total", *[f"k_{k}" for k in range(result.case.L)]]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for i, t in enumerate(result.times):
            row = {"t": int(t), "f_total": f"{result.f_total[i]:.16e}"}
            row.update({f"k_{k}": f"{result.f_by_position[i, k]:.16e}" for k in range(result.case.L)})
            writer.writerow(row)


def write_window_contribution_csv(result: DiagonalDecompositionResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "window",
        "start_t",
        "end_t",
        "center_t",
        "total_mass",
        *[f"C_k_{k}" for k in range(result.case.L)],
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for window in result.windows:
            row = {
                "window": window.name,
                "start_t": window.start_t,
                "end_t": window.end_t,
                "center_t": window.center_t,
                "total_mass": f"{window.total_mass:.16e}",
            }
            row.update({f"C_k_{k}": f"{window.by_position[k]:.16e}" for k in range(result.case.L)})
            writer.writerow(row)
