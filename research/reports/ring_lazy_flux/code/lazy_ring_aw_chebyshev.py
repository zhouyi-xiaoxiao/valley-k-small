#!/usr/bin/env python3
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


def ring_distance(a: int, b: int, N: int) -> int:
    a %= N
    b %= N
    d = abs(a - b)
    return min(d, N - d)


def chebyshev_T_all(x: np.ndarray, n_max: int) -> list[np.ndarray]:
    """
    Chebyshev T_n(x) for n=0..n_max by 3-term recurrence.
    Works for complex x (vectorized).
    """
    if n_max < 0:
        raise ValueError("n_max must be >= 0.")

    T: list[np.ndarray] = [np.ones_like(x, dtype=np.complex128)]
    if n_max == 0:
        return T
    T.append(x.astype(np.complex128, copy=False))
    for n in range(1, n_max):
        T.append(2.0 * x * T[n] - T[n - 1])
    return T


def chebyshev_U_n(x: np.ndarray, n: int) -> np.ndarray:
    """
    Chebyshev U_n(x) by 3-term recurrence.
    Works for complex x (vectorized).
    """
    if n < 0:
        raise ValueError("n must be >= 0.")
    U0 = np.ones_like(x, dtype=np.complex128)
    if n == 0:
        return U0
    U1 = 2.0 * x
    if n == 1:
        return U1
    for _ in range(1, n):
        U0, U1 = U1, (2.0 * x * U1 - U0)
    return U1


def sigma_of_z(z: np.ndarray, q: float) -> np.ndarray:
    if not (0.0 < q < 1.0):
        raise ValueError("q must be in (0,1) for the lazy walk baseline.")
    return (1.0 - z * (1.0 - q)) / (q * z)


def N_d_from_T(T: list[np.ndarray], *, d: int, N: int) -> np.ndarray:
    """N_d(σ) = T_d(σ) + T_{N-d}(σ) with d as ring distance."""
    if not (0 <= d <= N):
        raise ValueError("d must be within [0,N].")
    return T[d] + T[N - d]


def fpt_genfun_cheb(
    z: np.ndarray,
    *,
    N: int,
    q: float,
    p: float,
    start: int,
    target: int,
    u: int,
    v: int,
) -> np.ndarray:
    """
    Closed-form FPT generating function \\tilde F_{start->target}(z) from:
      `research/reports/ring_deriv_k2/manuscript/extras/note_k2.tex`, Eq. (F_cheb_closed).

    Model:
      - lazy NN ring baseline with jump prob q and self-loop 1-q
      - directed shortcut u->v with probability p taken from the self-loop at u
    """
    if N <= 1:
        raise ValueError("N must be >= 2.")
    if not (0.0 < q < 1.0):
        raise ValueError("q must be in (0,1).")
    if not (0.0 <= p <= (1.0 - q) + 1e-15):
        raise ValueError("p must satisfy 0 <= p <= 1-q.")

    start %= N
    target %= N
    u %= N
    v %= N
    if start == target:
        raise ValueError("FPT generating function is defined for start != target in this helper.")

    z = np.asarray(z, dtype=np.complex128)
    sig = sigma_of_z(z, q)

    # Chebyshev packaging
    T = chebyshev_T_all(sig, N)
    U_Nm1 = chebyshev_U_n(sig, N - 1)

    # C(z) = q z (σ^2 - 1) U_{N-1}(σ)
    C = (q * z) * ((sig * sig) - 1.0) * U_Nm1

    # N_d(σ) = T_d + T_{N-d}
    d_nn0 = ring_distance(target, start, N)
    d_nu = ring_distance(target, u, N)
    d_nv = ring_distance(target, v, N)
    d_un0 = ring_distance(u, start, N)
    d_un = ring_distance(u, target, N)
    d_uv = ring_distance(u, v, N)

    N0 = N_d_from_T(T, d=0, N=N)
    N_nn0 = N_d_from_T(T, d=d_nn0, N=N)
    N_nu = N_d_from_T(T, d=d_nu, N=N)
    N_nv = N_d_from_T(T, d=d_nv, N=N)
    N_un0 = N_d_from_T(T, d=d_un0, N=N)
    N_un = N_d_from_T(T, d=d_un, N=N)
    N_uv = N_d_from_T(T, d=d_uv, N=N)

    # D(z) = C(z) + z p (N_0 - N_{d(u,v)})
    D = C + (z * p) * (N0 - N_uv)

    Delta_n = N_nu - N_nv

    num = (N_nn0 * D) - (z * p) * Delta_n * N_un0
    den = (N0 * D) - (z * p) * Delta_n * N_un

    # Avoid division by tiny denominators (rare for r<1, but safe)
    den = np.where(np.abs(den) < 1e-30, 1e-30 + 0j, den)
    return num / den


def next_pow2(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


@dataclass(frozen=True)
class AWParams:
    m: int
    r: float


def choose_aw_params(t_max: int, *, oversample: int = 8, r_pow10: float = 14.0) -> AWParams:
    """
    Choose (m,r) for discrete Cauchy/AW inversion.

    We set r = 10^(-r_pow10 / m) so that r^m = 10^(-r_pow10).
    Larger `oversample` reduces aliasing at fixed r_pow10.
    """
    if t_max <= 0:
        raise ValueError("t_max must be positive.")
    if oversample <= 1:
        raise ValueError("oversample must be >= 2.")
    m = next_pow2(int(oversample * (t_max + 1)))
    r = float(10.0 ** (-float(r_pow10) / float(m)))
    return AWParams(m=m, r=r)


def aw_invert_coeffs(Fz: np.ndarray, *, r: float) -> np.ndarray:
    """
    Given samples Fz[k] = F(r*exp(2π i k/m)), return coefficients a_t for t=0..m-1:
      a_t ≈ r^{-t} * (1/m) * Σ_k Fz[k] exp(-2π i k t / m)
    """
    m = int(Fz.size)
    fft = np.fft.fft(Fz) / float(m)
    t = np.arange(m, dtype=np.float64)
    a = (r ** (-t)) * fft
    return a


def fpt_pmf_aw(
    *,
    N: int,
    q: float,
    p: float,
    start: int,
    target: int,
    u: int,
    v: int,
    t_max: int,
    m: Optional[int] = None,
    r: Optional[float] = None,
    oversample: int = 8,
    r_pow10: float = 14.0,
) -> Tuple[np.ndarray, AWParams]:
    """
    Compute f(t)=P(T=t), t=1..t_max, by AW inversion of the closed-form generating function.
    """
    if t_max <= 0:
        raise ValueError("t_max must be positive.")
    if m is None or r is None:
        params = choose_aw_params(t_max, oversample=oversample, r_pow10=r_pow10)
        if m is None:
            m = params.m
        if r is None:
            r = params.r
    params = AWParams(m=int(m), r=float(r))

    k = np.arange(params.m, dtype=np.float64)
    z = params.r * np.exp(1j * 2.0 * math.pi * k / float(params.m))
    Fz = fpt_genfun_cheb(z, N=N, q=q, p=p, start=start, target=target, u=u, v=v)
    a = aw_invert_coeffs(Fz, r=params.r)
    f = a[1 : (t_max + 1)].real.astype(np.float64, copy=False)
    return f, params


def _qtilde_from_chebyshev(*, T: list[np.ndarray], C: np.ndarray, N: int, d: int) -> np.ndarray:
    """
    Defect-free ring propagator generating function:
      \\tilde Q(d,z) = [T_d(σ(z)) + T_{N-d}(σ(z))] / [q z (σ(z)^2-1) U_{N-1}(σ(z))].
    """
    if not (0 <= d <= N):
        raise ValueError("d must be within [0,N].")
    Nd = T[d] + T[N - d]
    C = np.where(np.abs(C) < 1e-30, 1e-30 + 0j, C)
    return Nd / C


def _column_defect_x_from_new_outgoing(
    *, N: int, q: float, u: int, new_outgoing: dict[int, float]
) -> tuple[list[int], list[float]]:
    """
    Build the (column-stochastic) defect vector x = (B[:,u] - A[:,u]) from a desired new outgoing
    distribution at the source node u.

    Baseline (defect-free) column u has mass:
      to u: 1-q, to u±1: q/2.
    """
    u %= N
    base: dict[int, float] = {
        u: 1.0 - q,
        (u + 1) % N: 0.5 * q,
        (u - 1) % N: 0.5 * q,
    }

    x: dict[int, float] = {}
    for dest, prob in base.items():
        x[dest] = x.get(dest, 0.0) + float(prob)
    for dest, prob in new_outgoing.items():
        dest %= N
        x[dest] = x.get(dest, 0.0) - float(prob)

    nodes: list[int] = []
    vals: list[float] = []
    for dest, val in x.items():
        if abs(val) > 1e-15:
            nodes.append(int(dest))
            vals.append(float(val))
    return nodes, vals


def fpt_genfun_column_defect(
    z: np.ndarray,
    *,
    N: int,
    q: float,
    start: int,
    target: int,
    u: int,
    x_nodes: list[int],
    x_vals: list[float],
) -> np.ndarray:
    """
    First-passage generating function via a rank-1 (single-column) defect update.

    Conventions match `research/reports/ring_deriv_k2/manuscript/extras/note_k2.tex`:
      - B and A are column-stochastic, and only column u is modified
      - x = X[:,u] = B[:,u] - A[:,u]
      - Q(z) = (I - z B)^{-1} is the defect-free propagator generating function
      - S(z) = (I - z A)^{-1} is the defective propagator generating function

    Sherman–Morrison gives, for any (a,b),
      S_{a,b} = Q_{a,b} - [ z * (Q x)_a * Q_{u,b} ] / [ 1 + z * (Q x)_u ].
    The first-passage generating function is
      \\tilde F_{start->target}(z) = S_{target,start}(z) / S_{target,target}(z),  start != target.
    """
    if start == target:
        raise ValueError("start must differ from target for FPT generating function.")
    if len(x_nodes) != len(x_vals):
        raise ValueError("x_nodes and x_vals must have the same length.")

    start %= N
    target %= N
    u %= N

    z = np.asarray(z, dtype=np.complex128)
    sig = sigma_of_z(z, q)
    T = chebyshev_T_all(sig, N)
    U_Nm1 = chebyshev_U_n(sig, N - 1)
    C = (q * z) * ((sig * sig) - 1.0) * U_Nm1

    def Q_of_d(d: int) -> np.ndarray:
        return _qtilde_from_chebyshev(T=T, C=C, N=N, d=d)

    # Required baseline entries
    Q_tt = Q_of_d(0)
    Q_t0 = Q_of_d(ring_distance(target, start, N))
    Q_u0 = Q_of_d(ring_distance(u, start, N))
    Q_ut = Q_of_d(ring_distance(u, target, N))

    # Compute (Q x)_u and (Q x)_target as short linear combinations
    Qx_u = np.zeros_like(z, dtype=np.complex128)
    Qx_t = np.zeros_like(z, dtype=np.complex128)
    for node, val in zip(x_nodes, x_vals):
        node %= N
        Qx_u += complex(val) * Q_of_d(ring_distance(u, node, N))
        Qx_t += complex(val) * Q_of_d(ring_distance(target, node, N))

    denom = 1.0 + z * Qx_u
    denom = np.where(np.abs(denom) < 1e-30, 1e-30 + 0j, denom)

    S_t0 = Q_t0 - (z * Qx_t * Q_u0) / denom
    S_tt = Q_tt - (z * Qx_t * Q_ut) / denom
    S_tt = np.where(np.abs(S_tt) < 1e-30, 1e-30 + 0j, S_tt)
    return S_t0 / S_tt


def fpt_genfun_equal4(
    z: np.ndarray,
    *,
    N: int,
    q: float,
    start: int,
    target: int,
    u: int,
    v: int,
) -> np.ndarray:
    """
    Equal-4 model at the shortcut source u:
      outgoing distribution at u is uniform over {stay, left, right, shortcut u->v}, each 1/4.
    Baseline elsewhere remains the defect-free lazy ring with parameter q.
    """
    u %= N
    v %= N
    new_outgoing: dict[int, float] = {}
    for dest, prob in [
        (u, 0.25),
        ((u + 1) % N, 0.25),
        ((u - 1) % N, 0.25),
        (v, 0.25),
    ]:
        new_outgoing[dest] = new_outgoing.get(dest, 0.0) + prob
    x_nodes, x_vals = _column_defect_x_from_new_outgoing(N=N, q=q, u=u, new_outgoing=new_outgoing)
    return fpt_genfun_column_defect(
        z, N=N, q=q, start=start, target=target, u=u, x_nodes=x_nodes, x_vals=x_vals
    )


def fpt_pmf_aw_equal4(
    *,
    N: int,
    q: float,
    start: int,
    target: int,
    u: int,
    v: int,
    t_max: int,
    m: Optional[int] = None,
    r: Optional[float] = None,
    oversample: int = 8,
    r_pow10: float = 14.0,
) -> Tuple[np.ndarray, AWParams]:
    """
    Compute f(t)=P(T=t), t=1..t_max, by AW inversion for the equal-4 shortcut-source model.
    """
    if t_max <= 0:
        raise ValueError("t_max must be positive.")
    if m is None or r is None:
        params = choose_aw_params(t_max, oversample=oversample, r_pow10=r_pow10)
        if m is None:
            m = params.m
        if r is None:
            r = params.r
    params = AWParams(m=int(m), r=float(r))

    k = np.arange(params.m, dtype=np.float64)
    z = params.r * np.exp(1j * 2.0 * math.pi * k / float(params.m))
    Fz = fpt_genfun_equal4(z, N=N, q=q, start=start, target=target, u=u, v=v)
    a = aw_invert_coeffs(Fz, r=params.r)
    f = a[1 : (t_max + 1)].real.astype(np.float64, copy=False)
    return f, params
