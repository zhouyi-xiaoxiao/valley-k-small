from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class EncounterAWGrid:
    m: int
    r: float
    oversample: int
    r_pow10: float


def next_pow2(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (int(n) - 1).bit_length()


def choose_aw_grid(t_max: int, oversample: int = 8, r_pow10: float = 8.0) -> EncounterAWGrid:
    if t_max <= 0:
        raise ValueError("t_max must be positive")
    if oversample < 2:
        raise ValueError("oversample must be >= 2")
    m = next_pow2(int(oversample * (t_max + 1)))
    r = float(10.0 ** (-float(r_pow10) / float(m)))
    return EncounterAWGrid(m=m, r=r, oversample=int(oversample), r_pow10=float(r_pow10))


def finite_clamp(value: float, low: float, high: float, *, name: str) -> float:
    x = float(value)
    if not np.isfinite(x):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return min(max(x, float(low)), float(high))


def repair_stochastic_row(row: np.ndarray, *, tol: float = 1e-12) -> None:
    row[:] = np.nan_to_num(row, nan=0.0, posinf=0.0, neginf=0.0)
    row[row < 0.0] = 0.0
    s = float(np.sum(row))
    if s <= tol:
        row[:] = 0.0
        row[0] = 1.0
        return
    row[:] = row / s
    row[np.abs(row) < tol] = 0.0
    s2 = float(np.sum(row))
    if s2 <= tol:
        row[:] = 0.0
        row[0] = 1.0
        return
    row[:] = row / s2


def ring_step_probabilities(q: float, g: float) -> Dict[int, float]:
    q_safe = finite_clamp(q, 0.0, 1.0, name="q")
    g_safe = finite_clamp(g, -1.0, 1.0, name="g")
    p_plus = q_safe * (1.0 + g_safe) / 2.0
    p_minus = q_safe * (1.0 - g_safe) / 2.0
    p_stay = 1.0 - q_safe
    return {-1: float(p_minus), 0: float(p_stay), 1: float(p_plus)}


def ring_mode_eigenvalues(N: int, q: float, g: float) -> np.ndarray:
    probs = ring_step_probabilities(q, g)
    k = np.arange(int(N), dtype=np.float64)
    omega = np.exp(1j * 2.0 * np.pi * k / float(N))
    return (
        probs[0]
        + probs[1] * omega
        + probs[-1] * np.conjugate(omega)
    ).astype(np.complex128, copy=False)


def build_ring_transition(
    N: int,
    q: float,
    g: float,
    *,
    shortcut_src: int,
    shortcut_dst: int,
    beta: float,
) -> np.ndarray:
    if int(N) <= 0:
        raise ValueError(f"N must be positive, got {N}")

    q_safe = finite_clamp(q, 0.0, 1.0, name="q")
    g_safe = finite_clamp(g, -1.0, 1.0, name="g")
    beta_safe = finite_clamp(beta, 0.0, 1.0, name="beta")
    src = int(shortcut_src) % int(N)
    dst = int(shortcut_dst) % int(N)

    P = np.zeros((int(N), int(N)), dtype=np.float64)
    p_plus = q_safe * (1.0 + g_safe) / 2.0
    p_minus = q_safe * (1.0 - g_safe) / 2.0
    p_stay = 1.0 - q_safe

    for i in range(int(N)):
        P[i, i] += p_stay
        P[i, (i + 1) % int(N)] += p_plus
        P[i, (i - 1) % int(N)] += p_minus
        if i == src:
            shift = min(max(beta_safe * (1.0 - q_safe), 0.0), P[i, i])
            P[i, i] -= shift
            P[i, dst] += shift
        repair_stochastic_row(P[i])
    return P


def first_encounter_any(P1: np.ndarray, P2: np.ndarray, n0: int, m0: int, t_max: int) -> tuple[np.ndarray, np.ndarray]:
    N = int(P1.shape[0])
    P1T = P1.T
    J = np.zeros((N, N), dtype=np.float64)
    J[int(n0) % N, int(m0) % N] = 1.0
    f = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv[0] = 1.0
    for t in range(1, int(t_max) + 1):
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            J = P1T @ J @ P2
        if not np.isfinite(J).all():
            raise FloatingPointError("non-finite value detected in encounter propagation")
        f[t] = float(np.trace(J))
        np.fill_diagonal(J, 0.0)
        surv[t] = float(np.sum(J))
    return f, surv


def first_encounter_fixed_site(
    P1: np.ndarray,
    P2: np.ndarray,
    n0: int,
    m0: int,
    delta: int,
    t_max: int,
) -> tuple[np.ndarray, np.ndarray]:
    N = int(P1.shape[0])
    d = int(delta) % N
    P1T = P1.T
    J = np.zeros((N, N), dtype=np.float64)
    J[int(n0) % N, int(m0) % N] = 1.0
    f = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv[0] = 1.0
    for t in range(1, int(t_max) + 1):
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            J = P1T @ J @ P2
        if not np.isfinite(J).all():
            raise FloatingPointError("non-finite value detected in fixed-site encounter propagation")
        f[t] = float(J[d, d])
        J[d, d] = 0.0
        surv[t] = float(np.sum(J))
    return f, surv


def encounter_time_anywhere(
    *,
    N: int,
    q1: float,
    g1: float,
    q2: float,
    g2: float,
    n0: int,
    m0: int,
    shortcut_src: int,
    shortcut_dst: int,
    beta: float,
    t_max: int,
) -> Dict[str, Any]:
    P1 = build_ring_transition(
        N,
        q1,
        g1,
        shortcut_src=shortcut_src,
        shortcut_dst=shortcut_dst,
        beta=beta,
    )
    P2 = build_ring_transition(
        N,
        q2,
        g2,
        shortcut_src=shortcut_src,
        shortcut_dst=shortcut_dst,
        beta=0.0,
    )
    t0 = time.perf_counter()
    f, surv = first_encounter_any(P1, P2, n0, m0, t_max)
    elapsed = time.perf_counter() - t0
    return {
        "f": f,
        "survival": surv,
        "reported_seconds": float(elapsed),
        "state_size": int(N) * int(N),
        "defect_pairs": int(N),
        "target_count": int(N),
        "solver_variant": "pair_time_recursion",
    }


def encounter_time_fixed_site(
    *,
    N: int,
    q1: float,
    g1: float,
    q2: float,
    g2: float,
    n0: int,
    m0: int,
    delta: int,
    shortcut_src: int,
    shortcut_dst: int,
    beta: float,
    t_max: int,
) -> Dict[str, Any]:
    P1 = build_ring_transition(
        N,
        q1,
        g1,
        shortcut_src=shortcut_src,
        shortcut_dst=shortcut_dst,
        beta=beta,
    )
    P2 = build_ring_transition(
        N,
        q2,
        g2,
        shortcut_src=shortcut_src,
        shortcut_dst=shortcut_dst,
        beta=0.0,
    )
    t0 = time.perf_counter()
    f, surv = first_encounter_fixed_site(P1, P2, n0, m0, delta, t_max)
    elapsed = time.perf_counter() - t0
    return {
        "f": f,
        "survival": surv,
        "reported_seconds": float(elapsed),
        "state_size": int(N) * int(N),
        "defect_pairs": int(N),
        "target_count": 1,
        "solver_variant": "pair_fixedsite_time_recursion",
    }


def _pair_kernel_from_modes(z: complex, lam1: np.ndarray, lam2: np.ndarray) -> np.ndarray:
    denom = 1.0 - complex(z) * lam1[:, None] * lam2[None, :]
    denom = np.where(np.abs(denom) < 1e-30, 1e-30 + 0j, denom)
    return np.fft.ifft2(1.0 / denom).astype(np.complex128, copy=False)


def _pair_kernel_entry(g: np.ndarray, dx: int, dy: int) -> complex:
    N = int(g.shape[0])
    return complex(g[int(dx) % N, int(dy) % N])


def _target_a_row(g: np.ndarray, src_x: int, x0: int, y0: int) -> np.ndarray:
    N = int(g.shape[0])
    dx = (int(x0) - int(src_x)) % N
    y = np.arange(N, dtype=np.int64)
    return np.asarray(g[dx, (int(y0) - y) % N], dtype=np.complex128)


def _target_b_row(
    g: np.ndarray,
    *,
    end_x: int,
    end_y: int,
    src_x: int,
    dst_x: int,
    shift: float,
    p2_steps: Dict[int, float],
) -> np.ndarray:
    N = int(g.shape[0])
    dx_dst = (int(dst_x) - int(end_x)) % N
    dx_src = (int(src_x) - int(end_x)) % N
    y = np.arange(N, dtype=np.int64)
    out = np.zeros(N, dtype=np.complex128)
    for step, prob in p2_steps.items():
        idx = (y + int(step) - int(end_y)) % N
        out += float(prob) * (g[dx_dst, idx] - g[dx_src, idx])
    return complex(shift) * out


def _k_matrix(
    g: np.ndarray,
    *,
    z: complex,
    src_x: int,
    dst_x: int,
    shift: float,
    p2_steps: Dict[int, float],
) -> np.ndarray:
    N = int(g.shape[0])
    dx = (int(dst_x) - int(src_x)) % N
    ii = np.arange(N, dtype=np.int64)[:, None]
    jj = np.arange(N, dtype=np.int64)[None, :]
    diff = (ii - jj) % N
    kernel = np.zeros((N, N), dtype=np.complex128)
    for step, prob in p2_steps.items():
        idx = (diff + int(step)) % N
        kernel += float(prob) * (g[dx, idx] - g[0, idx])
    K = np.eye(N, dtype=np.complex128) - complex(z) * complex(shift) * kernel
    return K


def _defected_resolvent_to_targets(
    *,
    g: np.ndarray,
    z: complex,
    start_x: int,
    start_y: int,
    target_pairs: Sequence[tuple[int, int]],
    src_x: int,
    dst_x: int,
    shift: float,
    p2_steps: Dict[int, float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    N = int(g.shape[0])
    K = _k_matrix(g, z=z, src_x=src_x, dst_x=dst_x, shift=shift, p2_steps=p2_steps)
    a_start = _target_a_row(g, src_x, start_x, start_y)
    diag_targets = len(target_pairs) == N and all(int(x) == i and int(y) == i for i, (x, y) in enumerate(target_pairs))

    if diag_targets:
        idx = np.arange(N, dtype=np.int64)
        start_dx = np.asarray(g[(int(start_x) - idx) % N, (int(start_y) - idx) % N], dtype=np.complex128)
        y = np.arange(N, dtype=np.int64)[None, :]
        i = idx[:, None]
        A_targets = np.asarray(g[(i - int(src_x)) % N, (i - y) % N], dtype=np.complex128)
        B_targets = np.zeros((N, N), dtype=np.complex128)
        for step, prob in p2_steps.items():
            idx_shift = (y + int(step) - i) % N
            B_targets += float(prob) * (
                g[(int(dst_x) - i) % N, idx_shift]
                - g[(int(src_x) - i) % N, idx_shift]
            )
        B_targets *= complex(shift)
        d = (idx[:, None] - idx[None, :]) % N
        G_targets = np.asarray(g[d, d], dtype=np.complex128)
    else:
        start_dx = np.asarray(
            [_pair_kernel_entry(g, int(start_x) - tx, int(start_y) - ty) for tx, ty in target_pairs],
            dtype=np.complex128,
        )
        A_targets = np.zeros((len(target_pairs), N), dtype=np.complex128)
        B_targets = np.zeros((len(target_pairs), N), dtype=np.complex128)
        G_targets = np.zeros((len(target_pairs), len(target_pairs)), dtype=np.complex128)
        for i, (xi, yi) in enumerate(target_pairs):
            A_targets[i, :] = _target_a_row(g, src_x, xi, yi)
            B_targets[i, :] = _target_b_row(
                g,
                end_x=xi,
                end_y=yi,
                src_x=src_x,
                dst_x=dst_x,
                shift=shift,
                p2_steps=p2_steps,
            )
            for j, (xj, yj) in enumerate(target_pairs):
                G_targets[i, j] = _pair_kernel_entry(g, xi - xj, yi - yj)

    X = np.linalg.solve(K, B_targets.T)
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        start_to_targets = start_dx + complex(z) * (a_start @ X)
        G_targets = G_targets + complex(z) * (A_targets @ X)
    if not np.isfinite(start_to_targets).all() or not np.isfinite(G_targets).all():
        raise FloatingPointError("non-finite value detected in defected resolvent recovery")
    return start_to_targets, G_targets, K, X


def _coefficient_recovery(values: np.ndarray, grid: EncounterAWGrid, t_max: int) -> np.ndarray:
    coeffs = np.fft.fft(values) / float(grid.m)
    t = np.arange(int(grid.m), dtype=np.float64)
    series = (coeffs * (grid.r ** (-t))).real.astype(np.float64, copy=False)
    series[np.abs(series) < 1e-13] = 0.0
    out = np.zeros(int(t_max) + 1, dtype=np.float64)
    upto = min(int(t_max), int(grid.m) - 1)
    out[1 : upto + 1] = np.maximum(series[1 : upto + 1], 0.0)
    return out


def _encounter_gf_core(
    *,
    N: int,
    q1: float,
    g1: float,
    q2: float,
    g2: float,
    n0: int,
    m0: int,
    shortcut_src: int,
    shortcut_dst: int,
    beta: float,
    t_max: int,
    oversample: int,
    r_pow10: float,
    target_pairs: Sequence[tuple[int, int]],
    mode: str,
) -> Dict[str, Any]:
    grid = choose_aw_grid(t_max=t_max, oversample=oversample, r_pow10=r_pow10)
    lam1 = ring_mode_eigenvalues(N, q1, g1)
    lam2 = ring_mode_eigenvalues(N, q2, g2)
    shift = float(finite_clamp(beta, 0.0, 1.0, name="beta") * (1.0 - finite_clamp(q1, 0.0, 1.0, name="q1")))
    p2_steps = ring_step_probabilities(q2, g2)

    z_grid = grid.r * np.exp(1j * 2.0 * np.pi * np.arange(grid.m, dtype=np.float64) / float(grid.m))
    Fz = np.zeros(grid.m, dtype=np.complex128)

    t_setup = 0.0
    t_eval = 0.0
    t_renewal = 0.0

    for i, z in enumerate(z_grid):
        t0 = time.perf_counter()
        g = _pair_kernel_from_modes(complex(z), lam1, lam2)
        t_eval += time.perf_counter() - t0

        t1 = time.perf_counter()
        start_to_targets, G_targets, _K, _X = _defected_resolvent_to_targets(
            g=g,
            z=complex(z),
            start_x=n0,
            start_y=m0,
            target_pairs=target_pairs,
            src_x=shortcut_src,
            dst_x=shortcut_dst,
            shift=shift,
            p2_steps=p2_steps,
        )
        if mode == "fixed":
            denom = G_targets[0, 0]
            denom = denom if abs(denom) > 1e-30 else (1e-30 + 0j)
            Fz[i] = start_to_targets[0] / denom
        elif mode == "anywhere":
            weights = np.linalg.solve(G_targets.T, start_to_targets)
            Fz[i] = np.sum(weights)
        else:
            raise ValueError(f"unknown mode: {mode}")
        t_renewal += time.perf_counter() - t1

    t2 = time.perf_counter()
    f = _coefficient_recovery(Fz, grid, t_max)
    t_fft = time.perf_counter() - t2

    return {
        "f": f,
        "reported_seconds": float(t_setup + t_eval + t_renewal + t_fft),
        "state_size": int(N) * int(N),
        "defect_pairs": int(N),
        "target_count": int(len(target_pairs)),
        "aw_grid": {
            "m": int(grid.m),
            "r": float(grid.r),
            "oversample": int(grid.oversample),
            "r_pow10": float(grid.r_pow10),
        },
        "solver_breakdown": {
            "setup_seconds": float(t_setup),
            "resolvent_seconds": float(t_eval),
            "renewal_seconds": float(t_renewal),
            "fft_seconds": float(t_fft),
        },
        "solver_variant": "encounter_gf_aw",
    }


def encounter_gf_fixed_site(
    *,
    N: int,
    q1: float,
    g1: float,
    q2: float,
    g2: float,
    n0: int,
    m0: int,
    delta: int,
    shortcut_src: int,
    shortcut_dst: int,
    beta: float,
    t_max: int,
    oversample: int = 8,
    r_pow10: float = 8.0,
) -> Dict[str, Any]:
    target = (int(delta) % int(N), int(delta) % int(N))
    out = _encounter_gf_core(
        N=N,
        q1=q1,
        g1=g1,
        q2=q2,
        g2=g2,
        n0=n0,
        m0=m0,
        shortcut_src=shortcut_src,
        shortcut_dst=shortcut_dst,
        beta=beta,
        t_max=t_max,
        oversample=oversample,
        r_pow10=r_pow10,
        target_pairs=[target],
        mode="fixed",
    )
    out["solver_variant"] = "encounter_fixedsite_gf_aw"
    return out


def encounter_gf_anywhere(
    *,
    N: int,
    q1: float,
    g1: float,
    q2: float,
    g2: float,
    n0: int,
    m0: int,
    shortcut_src: int,
    shortcut_dst: int,
    beta: float,
    t_max: int,
    oversample: int = 8,
    r_pow10: float = 8.0,
) -> Dict[str, Any]:
    targets = [(i, i) for i in range(int(N))]
    out = _encounter_gf_core(
        N=N,
        q1=q1,
        g1=g1,
        q2=q2,
        g2=g2,
        n0=n0,
        m0=m0,
        shortcut_src=shortcut_src,
        shortcut_dst=shortcut_dst,
        beta=beta,
        t_max=t_max,
        oversample=oversample,
        r_pow10=r_pow10,
        target_pairs=targets,
        mode="anywhere",
    )
    out["solver_variant"] = "encounter_anywhere_gf_aw"
    return out


__all__ = [
    "EncounterAWGrid",
    "build_ring_transition",
    "choose_aw_grid",
    "encounter_gf_anywhere",
    "encounter_gf_fixed_site",
    "encounter_time_anywhere",
    "encounter_time_fixed_site",
    "first_encounter_any",
    "first_encounter_fixed_site",
    "ring_mode_eigenvalues",
]
