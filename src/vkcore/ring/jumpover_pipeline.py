#!/usr/bin/env python3
"""
jumpover_bimodality_pipeline.py

Purpose (for this repo):
  - Exact (time-domain) first-absorption pmf f(t) for a lazy K-neighbour ring with ONE
    directed shortcut under the "selfloop rule" (main), plus an optional "lazy_equal" rule.
  - Paper-style bimodality detection (same criterion used in existing reports):
      * strict local peaks: f(t) > f(t-1), f(t) > f(t+1), f(t) >= h_min (with boundary f(0)=f(T+1)=0)
      * paper bimodality: at least two peaks and the 2nd-highest peak >= 1% of the highest
      * macro bimodality (optional): for the top-2 peaks by height, require t2/t1 >= 10
  - Monte Carlo trajectory decomposition with two path events:
      * C = # of directed-shortcut traversals (sc_src -> sc_dst)
      * J = # of "jump-over target" events (ring move crosses target without landing)
    and window-conditional proportions around peak1 / valley / peak2.

Indexing:
  - CLI uses paper indexing 1..N
  - Internally use 0..N-1

This script is self-contained for the report in:
  reports/ring_lazy_jump_ext/
"""

from __future__ import annotations

import argparse
import csv
import json
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------
# Index helpers (paper <-> 0)
# ---------------------------


def wrap0(x: int, N: int) -> int:
    return int(x % N)


def wrap_paper(x_paper: int, N: int) -> int:
    return ((int(x_paper) - 1) % N) + 1


def paper_to0(x_paper: int, N: int) -> int:
    return wrap_paper(x_paper, N) - 1


def zero_to_paper(x0: int, N: int) -> int:
    return wrap0(x0, N) + 1


def auto_target_paper(N: int, n0_paper: int) -> int:
    """
    "Farthest-ish" target relative to n0 on the ring:
      target = n0 + floor(N/2)   (paper indexing, wrapped).
    """
    n0_0 = paper_to0(n0_paper, N)
    target0 = wrap0(n0_0 + (N // 2), N)
    return zero_to_paper(target0, N)


def ring_distance(a: int, b: int, N: int) -> int:
    a %= N
    b %= N
    d = abs(a - b)
    return int(min(d, N - d))


def parse_auto_expr(expr: str, *, N: int, n0_paper: int, target_paper: int) -> int:
    """
    Support minimal expressions used in this repo's report scripts:
      - "auto"             (only meaningful for target)
      - "auto+5"           => n0 + 5
      - "auto_target+1"    => target + 1
      - integer literal
    Returns a wrapped paper index in 1..N.
    """
    s = str(expr).strip()
    if s == "auto":
        return auto_target_paper(N, n0_paper)
    if s.startswith("auto+"):
        off = int(s[len("auto+") :])
        return wrap_paper(n0_paper + off, N)
    if s.startswith("auto_target+"):
        off = int(s[len("auto_target+") :])
        return wrap_paper(target_paper + off, N)
    return wrap_paper(int(s), N)


# ---------------------------
# Model parameters
# ---------------------------


@dataclass(frozen=True)
class Params:
    N: int
    K: int  # even, K=2k
    n0: int  # 0-based
    target: int  # 0-based
    sc_src: int  # 0-based
    sc_dst: int  # 0-based
    mode: str  # "lazy_selfloop" | "lazy_equal"
    q: float  # ring-move probability
    beta: float  # shortcut strength (selfloop rule)
    rho: float  # absorption probability upon landing on target
    jumpover_absorbs: bool = False  # if True: ring jump-over counts as (imperfect) absorption

    @property
    def k(self) -> int:
        return int(self.K // 2)


def p_shortcut(params: Params) -> float:
    """
    Map beta -> p under the "selfloop rule":
      p = beta * (1-q), taken from the self-loop at sc_src.
    """
    if params.mode != "lazy_selfloop":
        return 0.0
    return float(params.beta) * float(1.0 - params.q)


# ---------------------------
# AW inversion (analytic generating function + FFT inversion)
# ---------------------------


def lazy_ring_eigenvalues(*, N: int, K: int, q: float) -> np.ndarray:
    """
    Eigenvalues for the lazy K-neighbour ring transition matrix (column/row identical by symmetry):
      lambda_l = (1-q) + (2q/K) * sum_{r=1}^{K/2} cos(2π r l / N),  l=0..N-1
    """
    if K <= 0 or K % 2 != 0:
        raise ValueError("K must be a positive even integer.")
    if not (0.0 < q < 1.0):
        raise ValueError("q must be in (0,1).")
    k = K // 2
    l = np.arange(N, dtype=np.float64)
    cos_sum = np.zeros(N, dtype=np.float64)
    for r in range(1, k + 1):
        cos_sum += np.cos(2.0 * np.pi * float(r) * l / float(N))
    lam = (1.0 - q) + (2.0 * q / float(K)) * cos_sum
    return lam.astype(np.float64, copy=False)


def _next_pow2(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (int(n) - 1).bit_length()


def choose_aw_r_L(max_steps: int, *, r: Optional[float] = None, pad: int = 100) -> Tuple[float, int]:
    """
    Match the AW-style setup used elsewhere in this repo:
      r = 10^(-4/max_steps)  (so that r^{-max_steps}≈10^4), and
      L = next power of two > max_steps + pad.
    """
    if max_steps <= 0:
        raise ValueError("max_steps must be positive.")
    if r is None:
        r = float(10.0 ** (-4.0 / float(max_steps)))
    if not (0.0 < float(r) < 1.0):
        raise ValueError("AW radius r must be in (0,1).")
    L = _next_pow2(int(max_steps + int(pad) + 1))
    return r, int(L)


def defect_column_x(params: Params) -> Dict[int, float]:
    """
    Return x = A[:,u] - B[:,u] for the shortcut source column u, under the chosen mode.
    This sign convention matches the Sherman-Morrison update used in aw_first_absorption_pmf.
    Uses internal 0-based indices.
    """
    if params.mode not in ("lazy_selfloop", "lazy_equal"):
        raise ValueError("Unsupported mode for AW defect construction.")
    if params.sc_src == params.sc_dst:
        raise ValueError("Shortcut endpoints must be distinct.")
    N = int(params.N)
    K = int(params.K)
    k = int(params.k)
    q = float(params.q)
    s = float(1.0 - q)
    u = int(params.sc_src) % N
    v = int(params.sc_dst) % N

    base: Dict[int, float] = {u: s}
    move_each = q / float(K)
    for r in range(1, k + 1):
        base[(u + r) % N] = base.get((u + r) % N, 0.0) + move_each
        base[(u - r) % N] = base.get((u - r) % N, 0.0) + move_each

    if params.mode == "lazy_selfloop":
        p = p_shortcut(params)
        if abs(p) <= 0.0:
            return {}
        if p < 0.0 or p > s + 1e-15:
            raise ValueError(f"Invalid p=beta*(1-q)={p} for q={q}: need 0<=p<=1-q.")
        x = {u: float(p), v: float(-p)}
    else:
        prob = 1.0 / float(K + 2)
        new: Dict[int, float] = {u: prob, v: prob}
        for r in range(1, k + 1):
            new[(u + r) % N] = new.get((u + r) % N, 0.0) + prob
            new[(u - r) % N] = new.get((u - r) % N, 0.0) + prob
        x = {}
        for node in set(base) | set(new):
            val = float(base.get(node, 0.0) - new.get(node, 0.0))
            if abs(val) > 1e-15:
                x[int(node)] = val

    # remove any exact zeros / merge
    x2: Dict[int, float] = {}
    for node, val in x.items():
        if abs(val) <= 1e-15:
            continue
        x2[int(node) % N] = x2.get(int(node) % N, 0.0) + float(val)
    x2 = {n: v for n, v in x2.items() if abs(v) > 1e-15}
    return x2


def aw_first_absorption_pmf(
    params: Params,
    *,
    max_steps: int,
    r: Optional[float] = None,
    L: Optional[int] = None,
    hmin_clip: float = 0.0,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """
    First-absorption pmf via AW inversion for the lazy ring with a single-column defect (shortcut),
    for rho in (0,1]. Not supported when jumpover_absorbs=True (that is not a node-hitting event).

    Returns:
      f[0..max_steps-1] where f[t-1]=P(T=t),
      and a small metadata dict with AW parameters.
    """
    if params.jumpover_absorbs:
        raise ValueError("AW inversion is not supported for jumpover_absorbs=True (non-local absorption event).")
    if max_steps <= 0:
        raise ValueError("max_steps must be positive.")
    N = int(params.N)
    K = int(params.K)
    q = float(params.q)
    rho = float(params.rho)
    if not (0.0 < rho <= 1.0):
        raise ValueError("rho must be in (0,1].")

    if L is None or r is None:
        rr, LL = choose_aw_r_L(max_steps, r=r)
        if r is None:
            r = rr
        if L is None:
            L = LL
    r = float(r)
    L = int(L)
    if L <= max_steps:
        raise ValueError("Need L > max_steps for AW inversion.")

    lam = lazy_ring_eigenvalues(N=N, K=K, q=q)  # (N,)

    # z_k on the circle |z|=r, k=0..L-1
    k_idx = np.arange(L, dtype=np.float64)
    z = r * np.exp(1j * 2.0 * np.pi * k_idx / float(L))  # (L,)

    # Defect vector x (sparse)
    x = defect_column_x(params)
    u = int(params.sc_src) % N
    start = int(params.n0) % N
    target = int(params.target) % N

    # Required distances for Q(d,z)
    dists: List[int] = [0]
    dists.append(ring_distance(target, start, N))
    dists.append(ring_distance(u, start, N))
    dists.append(ring_distance(u, target, N))
    for node in x.keys():
        dists.append(ring_distance(u, node, N))
        dists.append(ring_distance(target, node, N))
    dists_u = sorted({int(d) for d in dists})

    l = np.arange(N, dtype=np.float64)  # mode index
    cos_mat = np.cos((2.0 * np.pi / float(N)) * (np.outer(dists_u, l)))  # (D,N)

    denom = 1.0 - z[:, None] * lam[None, :]  # (L,N) complex
    denom = np.where(np.abs(denom) < 1e-30, 1e-30 + 0j, denom)
    g = 1.0 / denom  # (L,N) complex
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        Q_all = (g @ cos_mat.T) / float(N)  # (L,D) complex
    Q_by_d = {d: Q_all[:, i] for i, d in enumerate(dists_u)}

    Q_tt = Q_by_d[0]
    Q_t0 = Q_by_d[ring_distance(target, start, N)]
    Q_u0 = Q_by_d[ring_distance(u, start, N)]
    Q_ut = Q_by_d[ring_distance(u, target, N)]

    Qx_u = np.zeros(L, dtype=np.complex128)
    Qx_t = np.zeros(L, dtype=np.complex128)
    for node, val in x.items():
        Qx_u += complex(val) * Q_by_d[ring_distance(u, node, N)]
        Qx_t += complex(val) * Q_by_d[ring_distance(target, node, N)]

    denom_sm = 1.0 + z * Qx_u
    denom_sm = np.where(np.abs(denom_sm) < 1e-30, 1e-30 + 0j, denom_sm)

    S_t0 = Q_t0 - (z * Qx_t * Q_u0) / denom_sm
    S_tt = Q_tt - (z * Qx_t * Q_ut) / denom_sm
    S_tt = np.where(np.abs(S_tt) < 1e-30, 1e-30 + 0j, S_tt)

    denom_abs = (1.0 - rho) + rho * S_tt
    denom_abs = np.where(np.abs(denom_abs) < 1e-30, 1e-30 + 0j, denom_abs)
    A_z = rho * S_t0 / denom_abs

    fft_res = np.fft.fft(A_z)
    t = np.arange(1, max_steps + 1, dtype=np.float64)
    f = ((1.0 / float(L)) * (r ** (-t)) * fft_res[1 : (max_steps + 1)]).real.astype(np.float64, copy=False)
    if hmin_clip is not None and float(hmin_clip) >= 0.0:
        f = np.maximum(f, float(hmin_clip))

    meta: Dict[str, object] = {
        "method": "aw",
        "r": float(r),
        "L": int(L),
        "max_steps": int(max_steps),
        "x_nnz": int(len(x)),
    }
    return f, meta


# ---------------------------
# Exact f(t): time-domain propagation (matrix-free)
# ---------------------------


def exact_first_absorption_pmf(
    params: Params,
    *,
    tmax: int,
    survival_eps: float,
) -> Tuple[np.ndarray, float]:
    """
    Compute exact first-absorption pmf f(t), t=1..T by time-domain propagation.

    State is the distribution of ALIVE walkers over nodes (including target when rho<1).
    Each step:
      dist_next = dist @ P
      f(t)      = rho * dist_next[target]
      dist_next[target] *= (1-rho)
    """
    N = int(params.N)
    K = int(params.K)
    if K <= 0 or K % 2 != 0:
        raise ValueError("K must be a positive even integer (K=2k).")

    q = float(params.q)
    if not (0.0 < q < 1.0):
        raise ValueError("q must be in (0,1).")
    rho = float(params.rho)
    if not (0.0 < rho <= 1.0):
        raise ValueError("rho must be in (0,1].")
    if tmax <= 0:
        raise ValueError("tmax must be positive.")
    if survival_eps <= 0.0:
        raise ValueError("survival_eps must be positive.")
    if params.mode not in ("lazy_selfloop", "lazy_equal"):
        raise ValueError("mode must be lazy_selfloop or lazy_equal.")

    s = 1.0 - q
    move_each = q / float(K)

    if params.mode == "lazy_selfloop":
        p = p_shortcut(params)
        if p < 0.0 or p > s + 1e-15:
            raise ValueError(f"Invalid p=beta*(1-q)={p} for q={q}: need 0<=p<=1-q.")

    dist = np.zeros(N, dtype=np.float64)
    dist[int(params.n0)] = 1.0

    f = np.zeros(int(tmax), dtype=np.float64)
    steps = 0

    target = int(params.target)
    sc_src = int(params.sc_src)
    sc_dst = int(params.sc_dst)

    for t in range(int(tmax)):
        # Baseline lazy ring update:
        # stay
        nxt = s * dist
        # ring moves: ±1..±k, each with prob q/K
        for r in range(1, params.k + 1):
            nxt += move_each * np.roll(dist, r)
            nxt += move_each * np.roll(dist, -r)

        # Defect at sc_src
        mu = float(dist[sc_src])
        if mu != 0.0:
            if params.mode == "lazy_selfloop":
                p = p_shortcut(params)
                if p != 0.0:
                    nxt[sc_src] -= mu * p
                    nxt[sc_dst] += mu * p
            else:
                # lazy_equal: at sc_src choose uniformly among {stay, K ring moves, shortcut}
                prob = 1.0 / float(K + 2)
                nxt[sc_src] += mu * (prob - s)
                delta_ring = prob - move_each
                if delta_ring != 0.0:
                    u = sc_src
                    for r in range(1, params.k + 1):
                        nxt[(u + r) % N] += mu * delta_ring
                        nxt[(u - r) % N] += mu * delta_ring
                nxt[sc_dst] += mu * prob

        # Optional control model: treat ring jump-over of target as absorption.
        # For rho<1, we interpret this as an absorption attempt: with prob rho absorb,
        # otherwise survive and still land at the chosen destination.
        flux_jump = 0.0
        if params.jumpover_absorbs and params.k >= 2:
            rho_jump = rho
            tgt = target
            # For a +r move, jump-over occurs when departure i is within r-1 steps behind target
            # along + direction: d=(tgt-i) mod N in {1,..,r-1}. Those departures land in
            # {tgt+1,..,tgt+r-1}. Symmetrically for -r moves.
            for r in range(2, params.k + 1):
                offs = np.arange(1, r, dtype=np.int32)
                dep_pos = (tgt - offs) % N
                dep_neg = (tgt + offs) % N

                mass_pos = move_each * dist[dep_pos]
                mass_neg = move_each * dist[dep_neg]

                absorbed_pos = rho_jump * mass_pos
                absorbed_neg = rho_jump * mass_neg

                dest_pos = (dep_pos + r) % N  # == dep_neg
                dest_neg = (dep_neg - r) % N  # == dep_pos

                nxt[dest_pos] -= absorbed_pos
                nxt[dest_neg] -= absorbed_neg
                flux_jump += float(absorbed_pos.sum() + absorbed_neg.sum())

                # Correct for lazy_equal at sc_src (its ring-move prob is prob_src, not move_each).
                if params.mode == "lazy_equal" and mu != 0.0:
                    prob_src = 1.0 / float(K + 2)
                    delta = rho_jump * (prob_src - move_each) * mu
                    if delta != 0.0:
                        d_pos = (tgt - sc_src) % N
                        if 1 <= int(d_pos) < r:
                            nxt[(sc_src + r) % N] -= delta
                            flux_jump += float(delta)
                        d_neg = (sc_src - tgt) % N
                        if 1 <= int(d_neg) < r:
                            nxt[(sc_src - r) % N] -= delta
                            flux_jump += float(delta)

        # Numerical hygiene: clip tiny negatives (roundoff)
        if float(nxt.min()) < 0.0:
            nxt = np.maximum(nxt, 0.0)

        # Absorption on landing at target
        flux = flux_jump + rho * float(nxt[target])
        nxt[target] *= (1.0 - rho)

        f[t] = flux
        dist = nxt
        steps = t + 1

        if float(dist.sum()) < survival_eps:
            break

    return f[:steps].copy(), float(dist.sum())


# ---------------------------
# Bimodality detection (paper criterion + macro)
# ---------------------------


def strict_local_peaks(
    f: np.ndarray,
    *,
    hmin: float,
) -> List[Tuple[int, float]]:
    """
    Strict local peaks, with boundary convention f(0)=f(T+1)=0.
    Return list of (t, f(t)) with t starting at 1.
    """
    f = np.asarray(f, dtype=np.float64)
    T = int(f.size)
    out: List[Tuple[int, float]] = []
    for i in range(T):
        left = float(f[i - 1]) if i - 1 >= 0 else 0.0
        right = float(f[i + 1]) if i + 1 < T else 0.0
        if float(f[i]) > left and float(f[i]) > right and float(f[i]) >= float(hmin):
            out.append((i + 1, float(f[i])))
    return out


def detect_peaks_paper(
    f: np.ndarray,
    *,
    hmin: float,
    second_rel_height: float,
) -> List[Tuple[int, float]]:
    """
    "Fig.3-style" peak list:
      - strict local peaks above hmin
      - filter out peaks whose height is < second_rel_height * max_peak_height
    Returned list is sorted by time.
    """
    peaks = strict_local_peaks(f, hmin=hmin)
    if not peaks:
        return []
    hmax = max(h for _, h in peaks)
    thresh = float(second_rel_height) * float(hmax)
    return [(t, h) for (t, h) in peaks if h >= thresh]


def paper_bimodal(peaks_paper: Sequence[Tuple[int, float]]) -> bool:
    return len(peaks_paper) >= 2


def macro_bimodal(
    peaks_paper: Sequence[Tuple[int, float]],
    *,
    macro_ratio: float,
) -> bool:
    if len(peaks_paper) < 2:
        return False
    top2 = sorted(peaks_paper, key=lambda x: -float(x[1]))[:2]
    t1, t2 = sorted([int(top2[0][0]), int(top2[1][0])])
    if t1 <= 0:
        return False
    return (t2 / t1) >= float(macro_ratio)


def first_two_peaks_and_valley(
    f: np.ndarray,
    peaks_paper: Sequence[Tuple[int, float]],
) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Using the first two peaks in time order (after paper filtering), return (t1, tv, t2),
    where tv is argmin over the open interval (t1, t2). Times are 1-based.
    """
    if len(peaks_paper) < 1:
        return None, None, None
    t1 = int(peaks_paper[0][0])
    if len(peaks_paper) < 2:
        return t1, None, None
    t2 = int(peaks_paper[1][0])
    if t2 - t1 < 2:
        return t1, None, t2
    seg = np.asarray(f, dtype=np.float64)[t1 : (t2 - 1)]
    if seg.size == 0:
        return t1, None, t2
    j = int(np.argmin(seg))
    tv = (t1 + j) + 1
    return t1, tv, t2


def window_labels(
    times: np.ndarray,
    *,
    centers: Dict[str, int],
    delta: int,
) -> np.ndarray:
    """
    Assign each time to the closest center among {peak1,valley,peak2} if within |t-center|<=delta.
    Ties (equal distance to >=2 centers) and out-of-range points are labelled "other".
    """
    times = np.asarray(times, dtype=np.int32)
    labels = np.full(times.shape, "other", dtype=object)
    if not centers:
        return labels
    names = list(centers.keys())
    cvals = np.asarray([int(centers[n]) for n in names], dtype=np.int32)
    dist = np.abs(times[:, None] - cvals[None, :])
    min_dist = dist.min(axis=1)
    tie = (dist == min_dist[:, None]).sum(axis=1) > 1
    ok = (min_dist <= int(delta)) & (~tie)
    if ok.any():
        arg = dist[ok].argmin(axis=1)
        labels[ok] = np.asarray([names[i] for i in arg], dtype=object)
    return labels


# ---------------------------
# Monte Carlo with C/J tracking
# ---------------------------


@dataclass
class MCResult:
    T: np.ndarray
    C: np.ndarray
    J: np.ndarray
    tau_sc: np.ndarray
    tau_jo: np.ndarray


def simulate_mc(
    params: Params,
    *,
    n_walkers: int,
    seed: int,
    tmax: int,
) -> MCResult:
    """
    Vectorized MC for the lazy ring with one directed shortcut. Tracks:
      - T: absorption time (1..tmax), or -1 if not absorbed by tmax
      - C: shortcut traversals count (sc_src -> sc_dst)
      - J: jumpover count (ring move crosses target without landing)
      - tau_sc/tau_jo: first times of those events, -1 if never
    """
    if params.mode not in ("lazy_selfloop", "lazy_equal"):
        raise ValueError("simulate_mc supports lazy_selfloop and lazy_equal.")
    if n_walkers <= 0:
        raise ValueError("n_walkers must be positive.")
    if tmax <= 0:
        raise ValueError("tmax must be positive.")

    rng = np.random.default_rng(int(seed))

    N = int(params.N)
    K = int(params.K)
    k = int(params.k)

    q = float(params.q)
    s = float(1.0 - q)
    rho = float(params.rho)

    p_sc = p_shortcut(params) if params.mode == "lazy_selfloop" else 0.0
    if params.mode == "lazy_selfloop":
        if p_sc < 0.0 or p_sc > s + 1e-15:
            raise ValueError(f"Invalid p=beta*(1-q)={p_sc} for q={q}: need 0<=p<=1-q.")
        s_src = s - p_sc
    else:
        s_src = None  # type: ignore[assignment]

    # walker state
    pos = np.full(int(n_walkers), int(params.n0), dtype=np.int32)
    active = np.ones(int(n_walkers), dtype=bool)

    T = np.full(int(n_walkers), -1, dtype=np.int32)
    C = np.zeros(int(n_walkers), dtype=np.int32)
    J = np.zeros(int(n_walkers), dtype=np.int32)
    tau_sc = np.full(int(n_walkers), -1, dtype=np.int32)
    tau_jo = np.full(int(n_walkers), -1, dtype=np.int32)

    target = int(params.target)
    sc_src = int(params.sc_src)
    sc_dst = int(params.sc_dst)

    for t in range(1, int(tmax) + 1):
        if not active.any():
            break
        idx = np.nonzero(active)[0]
        cur = pos[idx]
        u = rng.random(size=idx.size)

        nxt = cur.copy()
        ring_choice = np.full(idx.size, -1, dtype=np.int16)  # 0..K-1 for ring moves, else -1

        is_src = cur == sc_src

        # non-src updates
        non_src_idx = np.nonzero(~is_src)[0]
        if non_src_idx.size:
            uu = u[non_src_idx]
            cc = cur[non_src_idx]
            stay = uu < s
            move_idx = non_src_idx[~stay]
            if move_idx.size:
                rr = np.floor((uu[~stay] - s) / q * K).astype(np.int16)
                rr = np.clip(rr, 0, K - 1)
                step_len = (rr // 2) + 1
                dir_sign = np.where((rr % 2) == 0, 1, -1).astype(np.int32)
                nxt[move_idx] = (cc[~stay] + dir_sign * step_len.astype(np.int32)) % N
                ring_choice[move_idx] = rr

        # src updates
        src_idx = np.nonzero(is_src)[0]
        if src_idx.size:
            uu = u[src_idx]
            cc = cur[src_idx]
            if params.mode == "lazy_selfloop":
                go_sc = uu < p_sc
                sc_idx = src_idx[go_sc]
                if sc_idx.size:
                    nxt[sc_idx] = sc_dst
                    glob = idx[sc_idx]
                    C[glob] += 1
                    first = tau_sc[glob] < 0
                    tau_sc[glob[first]] = t

                stay = (uu >= p_sc) & (uu < (p_sc + s_src))
                move_idx = src_idx[~go_sc & ~stay]
                if move_idx.size:
                    rr = np.floor((uu[~go_sc & ~stay] - (p_sc + s_src)) / q * K).astype(np.int16)
                    rr = np.clip(rr, 0, K - 1)
                    step_len = (rr // 2) + 1
                    dir_sign = np.where((rr % 2) == 0, 1, -1).astype(np.int32)
                    nxt[move_idx] = (cc[~go_sc & ~stay] + dir_sign * step_len.astype(np.int32)) % N
                    ring_choice[move_idx] = rr
            else:
                # lazy_equal: uniform among K+2 actions: stay + K ring + shortcut
                a = np.floor(uu * (K + 2)).astype(np.int16)
                a = np.clip(a, 0, K + 1)
                stay = a == 0
                go_sc = a == (K + 1)
                move = (~stay) & (~go_sc)

                sc_idx = src_idx[go_sc]
                if sc_idx.size:
                    nxt[sc_idx] = sc_dst
                    glob = idx[sc_idx]
                    C[glob] += 1
                    first = tau_sc[glob] < 0
                    tau_sc[glob[first]] = t

                move_idx = src_idx[move]
                if move_idx.size:
                    rr = (a[move] - 1).astype(np.int16)  # 0..K-1
                    step_len = (rr // 2) + 1
                    dir_sign = np.where((rr % 2) == 0, 1, -1).astype(np.int32)
                    nxt[move_idx] = (cc[move] + dir_sign * step_len.astype(np.int32)) % N
                    ring_choice[move_idx] = rr

        # jumpover tracking for ring moves
        ring_move_idx = np.nonzero(ring_choice >= 0)[0]
        if ring_move_idx.size:
            rr = ring_choice[ring_move_idx].astype(np.int32)
            step_len = (rr // 2) + 1
            big = step_len >= 2
            if big.any():
                cc = cur[ring_move_idx].astype(np.int32)
                dir_pos = (rr % 2) == 0
                d = np.empty_like(step_len, dtype=np.int32)
                d[dir_pos] = (target - cc[dir_pos]) % N
                d[~dir_pos] = (cc[~dir_pos] - target) % N
                jm = big & (d > 0) & (d < step_len)
                if jm.any():
                    glob = idx[ring_move_idx[jm]]
                    J[glob] += 1
                    first = tau_jo[glob] < 0
                    tau_jo[glob[first]] = t
                    if params.jumpover_absorbs:
                        if rho >= 1.0:
                            absorbed = glob
                        else:
                            u3 = rng.random(size=glob.size)
                            absorbed = glob[u3 < rho]
                        if absorbed.size:
                            T[absorbed] = t
                            active[absorbed] = False

        # apply move
        pos[idx] = nxt.astype(np.int32)

        # absorption check
        hit_local = pos[idx] == target
        if hit_local.any():
            hit_glob = idx[hit_local]
            if rho >= 1.0:
                absorbed = hit_glob
            else:
                u2 = rng.random(size=hit_glob.size)
                absorbed = hit_glob[u2 < rho]
            T[absorbed] = t
            active[absorbed] = False

    return MCResult(T=T, C=C, J=J, tau_sc=tau_sc, tau_jo=tau_jo)


# ---------------------------
# Proportion stats (Wilson CI)
# ---------------------------


def wilson_interval(phat: float, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    denom = 1.0 + (z * z) / float(n)
    center = (phat + (z * z) / (2.0 * float(n))) / denom
    half = (z / denom) * np.sqrt((phat * (1.0 - phat)) / float(n) + (z * z) / (4.0 * float(n * n)))
    lo = float(max(0.0, center - half))
    hi = float(min(1.0, center + half))
    return lo, hi


def summarize_window(mc: MCResult, labels: np.ndarray, window: str) -> Dict[str, object]:
    mask = labels == window
    n = int(mask.sum())
    out: Dict[str, object] = {
        "window": window,
        "n": n,
        "frac": float(n / float(labels.size)) if labels.size else 0.0,
    }
    if n == 0:
        return out

    C = mc.C[mask]
    J = mc.J[mask]

    out["P_sc_ge1"] = float(np.mean(C >= 1))
    out["P_jo_ge1"] = float(np.mean(J >= 1))
    out["P_sc_ge1_ci95"] = wilson_interval(out["P_sc_ge1"], n)
    out["P_jo_ge1_ci95"] = wilson_interval(out["P_jo_ge1"], n)

    out["C0"] = float(np.mean(C == 0))
    out["C1"] = float(np.mean(C == 1))
    out["C2p"] = float(np.mean(C >= 2))
    out["J0"] = float(np.mean(J == 0))
    out["J1"] = float(np.mean(J == 1))
    out["J2p"] = float(np.mean(J >= 2))

    sc = C >= 1
    jo = J >= 1
    out["class_C0J0"] = float(np.mean((~sc) & (~jo)))
    out["class_C1pJ0"] = float(np.mean((sc) & (~jo)))
    out["class_C0J1p"] = float(np.mean((~sc) & (jo)))
    out["class_C1pJ1p"] = float(np.mean((sc) & (jo)))

    # (optional) order in the both-event class
    both = (mc.tau_sc[mask] >= 0) & (mc.tau_jo[mask] >= 0)
    if bool(both.any()):
        ts = mc.tau_sc[mask][both]
        tj = mc.tau_jo[mask][both]
        out["class_D_taujo_lt_tausc"] = float(np.mean(tj < ts))
        out["class_D_tausc_lt_taujo"] = float(np.mean(ts < tj))
        out["class_D_tie"] = float(np.mean(ts == tj))
    else:
        out["class_D_taujo_lt_tausc"] = None
        out["class_D_tausc_lt_taujo"] = None
        out["class_D_tie"] = None

    return out


# ---------------------------
# Time-conditional curves
# ---------------------------


def _bincount_bool_by_time(T: np.ndarray, x: np.ndarray, *, tmax: int) -> np.ndarray:
    """
    Count of x==True among samples with absorption time T=t, for t=0..tmax.
    T must be non-negative ints.
    """
    T = np.asarray(T, dtype=np.int32)
    x = np.asarray(x, dtype=bool)
    return np.bincount(T, weights=x.astype(np.int32), minlength=int(tmax) + 1).astype(np.float64)


def _smooth_counts(y: np.ndarray, window: int) -> np.ndarray:
    y = np.asarray(y, dtype=np.float64)
    w = int(window)
    if w <= 1:
        return y
    if w % 2 == 0:
        w += 1
    ker = np.ones(w, dtype=np.float64)
    return np.convolve(y, ker, mode="same")


def conditional_by_time(
    mc: MCResult,
    *,
    tmax: int,
    min_n: int,
    smooth_window: int,
) -> Dict[str, np.ndarray]:
    """
    For each t=1..tmax, compute conditional proportions like P(C>=1 | T=t), etc.
    Output arrays are length tmax, aligned with t=1..tmax.
    """
    if tmax <= 0:
        raise ValueError("tmax must be positive.")
    T_all = np.asarray(mc.T, dtype=np.int32)
    if T_all.size == 0:
        raise ValueError("empty MC sample")

    tmax_eff = int(min(int(tmax), int(T_all.max(initial=0))))
    keep = (T_all >= 0) & (T_all <= tmax_eff)
    T = T_all[keep]
    if T.size == 0:
        raise ValueError("no samples within requested tmax")
    n_t = np.bincount(T, minlength=tmax_eff + 1).astype(np.float64)

    sc_ge1 = mc.C[keep] >= 1
    jo_ge1 = mc.J[keep] >= 1
    class_a = (~sc_ge1) & (~jo_ge1)
    class_b = (sc_ge1) & (~jo_ge1)
    class_c = (~sc_ge1) & (jo_ge1)
    class_d = (sc_ge1) & (jo_ge1)

    num_sc = _bincount_bool_by_time(T, sc_ge1, tmax=tmax_eff)
    num_jo = _bincount_bool_by_time(T, jo_ge1, tmax=tmax_eff)
    num_a = _bincount_bool_by_time(T, class_a, tmax=tmax_eff)
    num_b = _bincount_bool_by_time(T, class_b, tmax=tmax_eff)
    num_c = _bincount_bool_by_time(T, class_c, tmax=tmax_eff)
    num_d = _bincount_bool_by_time(T, class_d, tmax=tmax_eff)

    # optional smoothing (weighted): smooth numerators and denominators then divide
    n_s = _smooth_counts(n_t, smooth_window)
    num_sc_s = _smooth_counts(num_sc, smooth_window)
    num_jo_s = _smooth_counts(num_jo, smooth_window)
    num_a_s = _smooth_counts(num_a, smooth_window)
    num_b_s = _smooth_counts(num_b, smooth_window)
    num_c_s = _smooth_counts(num_c, smooth_window)
    num_d_s = _smooth_counts(num_d, smooth_window)

    with np.errstate(divide="ignore", invalid="ignore"):
        p_sc = num_sc_s / n_s
        p_jo = num_jo_s / n_s
        p_a = num_a_s / n_s
        p_b = num_b_s / n_s
        p_c = num_c_s / n_s
        p_d = num_d_s / n_s

    # drop t=0 and apply min_n threshold on the UNSMOOTHED counts
    t = np.arange(1, tmax_eff + 1, dtype=np.int32)
    n_out = n_t[1:]
    mask = n_out >= float(min_n)

    def _mask(arr: np.ndarray) -> np.ndarray:
        out = arr[1:].copy()
        out[~mask] = np.nan
        return out

    return {
        "t": t,
        "n": n_out.astype(np.int32),
        "P_sc_ge1": _mask(p_sc),
        "P_jo_ge1": _mask(p_jo),
        "class_C0J0": _mask(p_a),
        "class_C1pJ0": _mask(p_b),
        "class_C0J1p": _mask(p_c),
        "class_C1pJ1p": _mask(p_d),
    }


# ---------------------------
# Plotting
# ---------------------------


def plot_f(
    f: np.ndarray,
    *,
    centers: Dict[str, int],
    delta: int,
    title: str,
    outpath: Path,
    max_t: Optional[int],
) -> None:
    T = int(f.size)
    if max_t is None:
        max_t = T
    max_t = min(int(max_t), T)

    t_start = 1
    t_end = max_t
    t1 = centers.get("peak1")
    t2 = centers.get("peak2")
    if t1 is not None:
        pre = max(3 * int(delta), int(0.1 * float(t1)))
        t_start = max(1, int(t1) - pre)
    if t2 is not None:
        post = max(6 * int(delta), int(0.2 * float(t2)))
        t_end = min(max_t, int(t2) + post)
    if t_end <= t_start:
        t_start = 1
        t_end = max_t

    t = np.arange(t_start, t_end + 1)
    f_plot = f[t_start - 1 : t_end]

    fig, ax = plt.subplots(figsize=(7.8, 4.4), dpi=170)
    ax.plot(t, f_plot, lw=1.6, color="0.2", zorder=3)
    peak_colors = {"peak1": "#D55E00", "valley": "#0072B2", "peak2": "#009E73"}
    span_alpha = {"peak1": 0.2, "valley": 0.28, "peak2": 0.2}
    label_y = {"peak1": 0.97, "valley": 0.86, "peak2": 0.97}
    markers = {"peak1": "^", "valley": "v", "peak2": "o"}
    legend_handles = []
    for name, c in centers.items():
        if c is None:
            continue
        if 1 <= int(c) <= t_end:
            color = peak_colors.get(str(name), "0.4")
            vline = ax.axvline(int(c), ls="--", lw=1.4, alpha=0.9, color=color, zorder=2, label=str(name))
            lo = max(t_start, int(c) - int(delta))
            hi = min(t_end, int(c) + int(delta))
            ax.axvspan(lo, hi, alpha=span_alpha.get(str(name), 0.16), color=color, zorder=1)
            y = float(f[int(c) - 1])
            ax.scatter(
                [int(c)],
                [y],
                s=56,
                color=color,
                marker=markers.get(str(name), "o"),
                edgecolor="white",
                linewidth=0.7,
                zorder=4,
            )
            ax.text(
                int(c),
                label_y.get(str(name), 0.97),
                f"{name}\n t={int(c)}",
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=7,
                color=color,
                bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=0.3),
            )
            legend_handles.append(vline)
    ax.set_yscale("log")
    if f_plot.size:
        f_pos = f_plot[f_plot > 0]
        if f_pos.size:
            f_max = float(np.nanmax(f_pos))
            f_min = float(np.nanmin(f_pos))
            valley = centers.get("valley")
            if valley is not None and t_start <= int(valley) <= t_end:
                vval = float(f[int(valley) - 1])
                if vval > 0:
                    f_min = max(f_min, vval * 0.7)
            floor = max(f_min, f_max * 1e-6)
            ax.set_ylim(floor, f_max * 1.2)
    ax.set_xlabel("t")
    ax.set_ylabel("f(t) (log)")
    title_lines = []
    for line in str(title).splitlines():
        title_lines.append(textwrap.fill(line, width=90))
    ax.set_title("\n".join(title_lines), fontsize=9)
    ax.grid(True, which="both", alpha=0.2)
    ax.set_xlim(t_start, t_end)
    if legend_handles:
        ax.legend(
            handles=legend_handles,
            labels=[h.get_label() for h in legend_handles],
            frameon=False,
            fontsize=8,
            loc="upper right",
            ncol=1,
        )
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_window_classes(
    summaries: Sequence[Dict[str, object]],
    *,
    title: str,
    outpath: Path,
) -> None:
    order = ["peak1", "valley", "peak2"]
    rows = [d for d in summaries if d.get("window") in order]
    rows.sort(key=lambda d: order.index(str(d["window"])))
    if not rows:
        return

    x = np.arange(len(rows))
    a = np.array([float(d.get("class_C0J0", 0.0) or 0.0) for d in rows], dtype=float)
    b = np.array([float(d.get("class_C1pJ0", 0.0) or 0.0) for d in rows], dtype=float)
    c = np.array([float(d.get("class_C0J1p", 0.0) or 0.0) for d in rows], dtype=float)
    d = np.array([float(d.get("class_C1pJ1p", 0.0) or 0.0) for d in rows], dtype=float)

    fig, ax = plt.subplots(figsize=(7.6, 4.1), dpi=170)
    ax.bar(x, a, label="C=0, J=0")
    ax.bar(x, b, bottom=a, label="C>=1, J=0")
    ax.bar(x, c, bottom=a + b, label="C=0, J>=1")
    ax.bar(x, d, bottom=a + b + c, label="C>=1, J>=1")

    for i, row in enumerate(rows):
        n = int(row.get("n", 0) or 0)
        ax.text(i, 1.04, f"n={n}", ha="center", va="bottom", fontsize=8, clip_on=False)

    ax.set_ylim(0, 1.12)
    ax.set_xticks(x, [str(r["window"]) for r in rows])
    ax.set_ylabel("fraction within window")
    ax.set_title(title)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        fig.legend(
            handles=handles,
            labels=labels,
            frameon=False,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.98),
            fontsize=8,
            ncol=2,
        )
    ax.grid(True, axis="y", alpha=0.2)
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.9])
    fig.savefig(outpath)
    plt.close(fig)


def plot_window_counts_012(
    summaries: Sequence[Dict[str, object]],
    *,
    title: str,
    outpath: Path,
) -> None:
    order = ["peak1", "valley", "peak2"]
    rows = [d for d in summaries if d.get("window") in order]
    rows.sort(key=lambda d: order.index(str(d["window"])))
    if not rows:
        return

    x = np.arange(len(rows))

    c0 = np.array([float(d.get("C0", 0.0) or 0.0) for d in rows], dtype=float)
    c1 = np.array([float(d.get("C1", 0.0) or 0.0) for d in rows], dtype=float)
    c2p = np.array([float(d.get("C2p", 0.0) or 0.0) for d in rows], dtype=float)
    j0 = np.array([float(d.get("J0", 0.0) or 0.0) for d in rows], dtype=float)
    j1 = np.array([float(d.get("J1", 0.0) or 0.0) for d in rows], dtype=float)
    j2p = np.array([float(d.get("J2p", 0.0) or 0.0) for d in rows], dtype=float)

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.9), dpi=170, sharey=True)
    axc, axj = axes

    axc.bar(x, c0, label="C=0")
    axc.bar(x, c1, bottom=c0, label="C=1")
    axc.bar(x, c2p, bottom=c0 + c1, label="C>=2")
    axc.set_title("shortcut count C (0/1/2+)")
    axc.set_xticks(x, [str(r["window"]) for r in rows])
    axc.set_ylabel("fraction within window")
    axc.grid(True, axis="y", alpha=0.2)

    axj.bar(x, j0, label="J=0")
    axj.bar(x, j1, bottom=j0, label="J=1")
    axj.bar(x, j2p, bottom=j0 + j1, label="J>=2")
    axj.set_title("jumpover count J (0/1/2+)")
    axj.set_xticks(x, [str(r["window"]) for r in rows])
    axj.grid(True, axis="y", alpha=0.2)

    for i, row in enumerate(rows):
        n = int(row.get("n", 0) or 0)
        axc.text(i, 1.04, f"n={n}", ha="center", va="bottom", fontsize=8, clip_on=False)
        axj.text(i, 1.04, f"n={n}", ha="center", va="bottom", fontsize=8, clip_on=False)

    axc.set_ylim(0, 1.12)
    axj.set_ylim(0, 1.12)
    fig.suptitle(title, y=0.98)
    handles_c, labels_c = axc.get_legend_handles_labels()
    handles_j, labels_j = axj.get_legend_handles_labels()
    if handles_c:
        fig.legend(
            handles=handles_c,
            labels=labels_c,
            frameon=False,
            fontsize=8,
            loc="lower center",
            bbox_to_anchor=(0.26, 0.05),
            ncol=3,
        )
    if handles_j:
        fig.legend(
            handles=handles_j,
            labels=labels_j,
            frameon=False,
            fontsize=8,
            loc="lower center",
            bbox_to_anchor=(0.74, 0.05),
            ncol=3,
        )
    fig.tight_layout(rect=[0.0, 0.14, 1.0, 0.9])
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath)
    plt.close(fig)


def plot_conditional_by_time(
    cond: Dict[str, np.ndarray],
    *,
    centers: Dict[str, int],
    delta: int,
    title: str,
    outpath: Path,
) -> None:
    t = cond["t"].astype(np.int32)
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 5.8), dpi=170, sharex=True)

    ax = axes[0]
    ax.plot(t, cond["P_sc_ge1"], lw=1.2, label=r"$P(C\geq 1\mid T=t)$", zorder=3)
    ax.plot(t, cond["P_jo_ge1"], lw=1.2, label=r"$P(J\geq 1\mid T=t)$", zorder=3)
    ax.set_ylim(-0.02, 1.02)
    ax.set_ylabel("probability")
    ax.grid(True, alpha=0.2)
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1.02, 1.0))

    ax2 = axes[1]
    ax2.plot(t, cond["class_C0J0"], lw=1.0, label="A: C=0,J=0", zorder=3)
    ax2.plot(t, cond["class_C1pJ0"], lw=1.0, label="B: C>=1,J=0", zorder=3)
    ax2.plot(t, cond["class_C0J1p"], lw=1.0, label="C: C=0,J>=1", zorder=3)
    ax2.plot(t, cond["class_C1pJ1p"], lw=1.0, label="D: C>=1,J>=1", zorder=3)
    ax2.set_ylim(-0.02, 1.02)
    ax2.set_xlabel("t")
    ax2.set_ylabel("class fraction")
    ax2.grid(True, alpha=0.2)
    ax2.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1.0))

    for a in axes:
        for name, c in centers.items():
            if c is None:
                continue
            lo = max(int(t[0]), int(c) - int(delta))
            hi = min(int(t[-1]), int(c) + int(delta))
            if lo > hi:
                continue
            a.axvline(int(c), ls="--", lw=0.9, alpha=0.6, color="0.45", zorder=1)
            a.axvspan(lo, hi, alpha=0.06, color="0.8", zorder=0)

    fig.suptitle(title, y=0.99)
    fig.tight_layout(rect=[0.0, 0.0, 0.82, 0.94])
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath)
    plt.close(fig)


# ---------------------------
# Commands
# ---------------------------


def default_tmax(N: int, tmax_mult: float) -> int:
    return int(max(2000, float(tmax_mult) * float(N * N)))


def cmd_scan_n(args: argparse.Namespace) -> None:
    out_csv = Path(args.out).expanduser().resolve()
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, object]] = []
    for N in range(int(args.N_min), int(args.N_max) + 1, int(args.N_step)):
        if args.only_even and (N % 2 != 0):
            continue

        n0_paper = wrap_paper(int(args.n0), N)
        target_paper = (
            auto_target_paper(N, n0_paper) if str(args.target) == "auto" else wrap_paper(int(args.target), N)
        )
        sc_src_paper = parse_auto_expr(str(args.sc_src), N=N, n0_paper=n0_paper, target_paper=target_paper)
        sc_dst_paper = parse_auto_expr(str(args.sc_dst), N=N, n0_paper=n0_paper, target_paper=target_paper)

        params = Params(
            N=N,
            K=int(args.K),
            n0=paper_to0(n0_paper, N),
            target=paper_to0(target_paper, N),
            sc_src=paper_to0(sc_src_paper, N),
            sc_dst=paper_to0(sc_dst_paper, N),
            mode=str(args.mode),
            q=float(args.q),
            beta=float(args.beta),
            rho=float(args.rho),
            jumpover_absorbs=bool(args.jumpover_absorbs),
        )

        tmax = int(args.tmax) if args.tmax is not None else default_tmax(N, float(args.tmax_mult))
        f, surv = exact_first_absorption_pmf(params, tmax=tmax, survival_eps=float(args.survival_eps))
        peaks = detect_peaks_paper(f, hmin=float(args.hmin), second_rel_height=float(args.second_rel_height))
        t1, tv, t2 = first_two_peaks_and_valley(f, peaks)

        rows.append(
            {
                "N": N,
                "K": int(args.K),
                "mode": str(args.mode),
                "q": float(args.q),
                "beta": float(args.beta),
                "p_shortcut": p_shortcut(params),
                "rho": float(args.rho),
                "jumpover_absorbs": bool(args.jumpover_absorbs),
                "n0": n0_paper,
                "target": target_paper,
                "sc_src": sc_src_paper,
                "sc_dst": sc_dst_paper,
                "T_len": int(f.size),
                "survival_end": float(surv),
                "n_peaks_paper": int(len(peaks)),
                "t1": t1,
                "tv": tv,
                "t2": t2,
                "paper_bimodal": bool(paper_bimodal(peaks)),
                "macro_bimodal": bool(macro_bimodal(peaks, macro_ratio=float(args.macro_ratio))),
            }
        )

    if not rows:
        raise SystemExit("No rows produced. Check N range / filters.")

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"[scan-n] wrote {out_csv}")


def _parse_beta_list(args: argparse.Namespace) -> List[float]:
    if args.betas:
        return [float(x) for x in args.betas]
    bmin = float(args.beta_min)
    bmax = float(args.beta_max)
    n = int(args.beta_num)
    if n < 2:
        return [bmin]
    return list(np.linspace(bmin, bmax, num=n, dtype=float))


def cmd_scan_beta(args: argparse.Namespace) -> None:
    out_csv = Path(args.out).expanduser().resolve()
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    N = int(args.N)
    n0_paper = wrap_paper(int(args.n0), N)
    target_paper = auto_target_paper(N, n0_paper) if str(args.target) == "auto" else wrap_paper(int(args.target), N)
    sc_src_paper = parse_auto_expr(str(args.sc_src), N=N, n0_paper=n0_paper, target_paper=target_paper)
    sc_dst_paper = parse_auto_expr(str(args.sc_dst), N=N, n0_paper=n0_paper, target_paper=target_paper)

    betas = _parse_beta_list(args)
    rows: List[Dict[str, object]] = []

    for beta in betas:
        params = Params(
            N=N,
            K=int(args.K),
            n0=paper_to0(n0_paper, N),
            target=paper_to0(target_paper, N),
            sc_src=paper_to0(sc_src_paper, N),
            sc_dst=paper_to0(sc_dst_paper, N),
            mode=str(args.mode),
            q=float(args.q),
            beta=float(beta),
            rho=float(args.rho),
            jumpover_absorbs=bool(args.jumpover_absorbs),
        )
        tmax = int(args.tmax) if args.tmax is not None else default_tmax(N, float(args.tmax_mult))
        f, surv = exact_first_absorption_pmf(params, tmax=tmax, survival_eps=float(args.survival_eps))
        peaks = detect_peaks_paper(f, hmin=float(args.hmin), second_rel_height=float(args.second_rel_height))
        t1, tv, t2 = first_two_peaks_and_valley(f, peaks)
        rows.append(
            {
                "N": N,
                "K": int(args.K),
                "mode": str(args.mode),
                "q": float(args.q),
                "beta": float(beta),
                "p_shortcut": p_shortcut(params),
                "rho": float(args.rho),
                "jumpover_absorbs": bool(args.jumpover_absorbs),
                "n0": n0_paper,
                "target": target_paper,
                "sc_src": sc_src_paper,
                "sc_dst": sc_dst_paper,
                "T_len": int(f.size),
                "survival_end": float(surv),
                "n_peaks_paper": int(len(peaks)),
                "t1": t1,
                "tv": tv,
                "t2": t2,
                "paper_bimodal": bool(paper_bimodal(peaks)),
                "macro_bimodal": bool(macro_bimodal(peaks, macro_ratio=float(args.macro_ratio))),
            }
        )

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"[scan-beta] wrote {out_csv}")


def cmd_analyze(args: argparse.Namespace) -> None:
    out_prefix = Path(args.out_prefix).expanduser().resolve()
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    N = int(args.N)
    n0_paper = wrap_paper(int(args.n0), N)
    target_paper = auto_target_paper(N, n0_paper) if str(args.target) == "auto" else wrap_paper(int(args.target), N)
    sc_src_paper = parse_auto_expr(str(args.sc_src), N=N, n0_paper=n0_paper, target_paper=target_paper)
    sc_dst_paper = parse_auto_expr(str(args.sc_dst), N=N, n0_paper=n0_paper, target_paper=target_paper)

    params = Params(
        N=N,
        K=int(args.K),
        n0=paper_to0(n0_paper, N),
        target=paper_to0(target_paper, N),
        sc_src=paper_to0(sc_src_paper, N),
        sc_dst=paper_to0(sc_dst_paper, N),
        mode=str(args.mode),
        q=float(args.q),
        beta=float(args.beta),
        rho=float(args.rho),
        jumpover_absorbs=bool(args.jumpover_absorbs),
    )

    exact_method = str(args.exact_method)
    exact_meta: Dict[str, object] = {"method": exact_method}
    tmax_base = int(args.tmax) if args.tmax is not None else default_tmax(N, float(args.tmax_mult))
    tmax_for_mc_default = int(tmax_base)

    if exact_method == "aw":
        if params.jumpover_absorbs:
            raise SystemExit("exact-method=aw is not supported for --jumpover-absorbs (use exact-method=time).")
        aw_steps = int(args.aw_steps) if args.aw_steps is not None else int(args.max_t_plot)
        f, aw_meta = aw_first_absorption_pmf(
            params,
            max_steps=aw_steps,
            r=float(args.aw_r) if args.aw_r is not None else None,
            L=int(args.aw_L) if args.aw_L is not None else None,
            hmin_clip=0.0,
        )
        surv = float("nan")
        exact_meta.update(aw_meta)
    elif exact_method == "time":
        tmax_exact = int(tmax_base)
        f, surv = exact_first_absorption_pmf(params, tmax=tmax_exact, survival_eps=float(args.survival_eps))
        exact_meta.update({"tmax": int(tmax_exact), "survival_eps": float(args.survival_eps)})
    else:
        raise SystemExit(f"Unknown exact method: {exact_method}")

    peaks = detect_peaks_paper(f, hmin=float(args.hmin), second_rel_height=float(args.second_rel_height))
    t1, tv, t2 = first_two_peaks_and_valley(f, peaks)

    if t1 is None or t2 is None or tv is None:
        print("[analyze] WARNING: fewer than 2 peaks (or missing valley) under paper criterion; window stats may be uninformative.")

    if t1 is not None and t2 is not None:
        delta = max(1, int(float(args.delta_frac) * float(t2 - t1)))
    else:
        delta = int(args.delta_fallback)

    centers: Dict[str, int] = {}
    if t1 is not None:
        centers["peak1"] = int(t1)
    if tv is not None:
        centers["valley"] = int(tv)
    if t2 is not None:
        centers["peak2"] = int(t2)

    title = (
        f"Exact f(t): N={N}, K={int(args.K)}, mode={params.mode}, q={params.q:.3g}, beta={params.beta:.3g}, rho={params.rho:.3g}, "
        f"jumpover_absorbs={params.jumpover_absorbs}, method={exact_method}\n"
        f"n0={n0_paper}, target={target_paper}, shortcut {sc_src_paper}->{sc_dst_paper}, p={p_shortcut(params):.4g}, "
        f"paper_peaks={len(peaks)}, delta={delta}, surv_end={'NA' if not np.isfinite(surv) else f'{surv:.2e}'}"
    )

    fig_f = out_prefix.with_suffix(".f_t.pdf")
    plot_f(f, centers=centers, delta=delta, title=title, outpath=fig_f, max_t=args.max_t_plot)

    # Save exact arrays for reproducibility
    exact_npz = out_prefix.with_suffix(".exact.npz")
    np.savez_compressed(
        exact_npz,
        f=f,
        surv_end=float(surv),
        peaks=np.asarray(peaks, dtype=np.float64) if peaks else np.zeros((0, 2), dtype=np.float64),
        t1=-1 if t1 is None else int(t1),
        tv=-1 if tv is None else int(tv),
        t2=-1 if t2 is None else int(t2),
        delta=int(delta),
        jumpover_absorbs=bool(params.jumpover_absorbs),
        exact_method=np.asarray(exact_method),
        aw_r=np.asarray(exact_meta.get("r", np.nan), dtype=np.float64),
        aw_L=np.asarray(exact_meta.get("L", -1), dtype=np.int64),
    )

    # MC
    tmax_mc = int(args.tmax_mc) if args.tmax_mc is not None else int(args.tmax_mc_mult * max(1, tmax_for_mc_default))
    mc = simulate_mc(params, n_walkers=int(args.n_walkers), seed=int(args.seed), tmax=tmax_mc)
    ok = mc.T >= 1
    if not bool(ok.all()):
        frac_miss = float(np.mean(~ok))
        print(f"[analyze] WARNING: {frac_miss:.4%} walkers not absorbed by tmax_mc; excluded from window stats.")

    mc_f = MCResult(
        T=mc.T[ok],
        C=mc.C[ok],
        J=mc.J[ok],
        tau_sc=mc.tau_sc[ok],
        tau_jo=mc.tau_jo[ok],
    )
    labels = window_labels(mc_f.T, centers=centers, delta=delta)

    summaries: List[Dict[str, object]] = []
    for name in ("peak1", "valley", "peak2", "other"):
        if name == "other" and ("other" not in set(labels.tolist())):
            continue
        summaries.append(summarize_window(mc_f, labels, name))

    out_json = out_prefix.with_suffix(".summary.json")
    with out_json.open("w", encoding="utf-8") as fjs:
        json.dump(
            {
                "params": {
                    **params.__dict__,
                    "n0_paper": n0_paper,
                    "target_paper": target_paper,
                    "sc_src_paper": sc_src_paper,
                    "sc_dst_paper": sc_dst_paper,
                    "p_shortcut": p_shortcut(params),
                },
                "paper_peaks": peaks,
                "peaks_valley": {"t1": t1, "tv": tv, "t2": t2, "delta": delta},
                "exact_meta": exact_meta,
                "cond_by_time": {
                    "max_t": int(args.cond_max_t) if args.cond_max_t is not None else int(args.max_t_plot),
                    "min_n": int(args.cond_min_n),
                    "smooth_window": int(args.cond_smooth_window),
                },
                "summaries": summaries,
            },
            fjs,
            ensure_ascii=False,
            indent=2,
        )

    out_csv = out_prefix.with_suffix(".summary.csv")
    fieldnames: List[str] = []
    flat_rows: List[Dict[str, object]] = []
    for d in summaries:
        d2 = dict(d)
        if "P_sc_ge1_ci95" in d2:
            lo, hi = d2.pop("P_sc_ge1_ci95")
            d2["P_sc_ge1_ci95_lo"] = lo
            d2["P_sc_ge1_ci95_hi"] = hi
        if "P_jo_ge1_ci95" in d2:
            lo, hi = d2.pop("P_jo_ge1_ci95")
            d2["P_jo_ge1_ci95_lo"] = lo
            d2["P_jo_ge1_ci95_hi"] = hi
        flat_rows.append(d2)
        for k_ in d2.keys():
            if k_ not in fieldnames:
                fieldnames.append(k_)

    with out_csv.open("w", newline="", encoding="utf-8") as fc:
        w = csv.DictWriter(fc, fieldnames=fieldnames)
        w.writeheader()
        for r in flat_rows:
            w.writerow(r)

    fig_cls = out_prefix.with_suffix(".classes.pdf")
    plot_window_classes(summaries, title=f"Window-conditional classes (N={N}, K={int(args.K)})", outpath=fig_cls)

    fig_counts = out_prefix.with_suffix(".counts.pdf")
    plot_window_counts_012(summaries, title=f"Window-conditional count breakdown (N={N}, K={int(args.K)})", outpath=fig_counts)

    cond_max_t = int(args.cond_max_t) if args.cond_max_t is not None else int(args.max_t_plot)
    cond = conditional_by_time(
        mc_f,
        tmax=cond_max_t,
        min_n=int(args.cond_min_n),
        smooth_window=int(args.cond_smooth_window),
    )
    out_cond_csv = out_prefix.with_suffix(".cond_by_t.csv")
    with out_cond_csv.open("w", newline="", encoding="utf-8") as fc:
        cols = [
            "t",
            "n",
            "P_sc_ge1",
            "P_jo_ge1",
            "class_C0J0",
            "class_C1pJ0",
            "class_C0J1p",
            "class_C1pJ1p",
        ]
        w = csv.DictWriter(fc, fieldnames=cols)
        w.writeheader()
        for i in range(int(cond["t"].size)):
            w.writerow({k: cond[k][i] for k in cols})

    fig_cond = out_prefix.with_suffix(".cond_by_t.pdf")
    plot_conditional_by_time(
        cond,
        centers=centers,
        delta=delta,
        title=f"Time-conditional curves (N={N}, K={int(args.K)}, beta={params.beta:g}, min_n={int(args.cond_min_n)}, smooth={int(args.cond_smooth_window)})",
        outpath=fig_cond,
    )

    print(f"[analyze] wrote:\n  {fig_f}\n  {fig_cls}\n  {fig_counts}\n  {fig_cond}\n  {exact_npz}\n  {out_json}\n  {out_csv}\n  {out_cond_csv}")


def cmd_compare_jumpover(args: argparse.Namespace) -> None:
    """
    Exact-only comparison between:
      (i) baseline model (jumpover_absorbs=False)
      (ii) control model  (jumpover_absorbs=True)
    under the same (N,K,beta,...) configuration.
    """
    out_prefix = Path(args.out_prefix).expanduser().resolve()
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    N = int(args.N)
    n0_paper = wrap_paper(int(args.n0), N)
    target_paper = auto_target_paper(N, n0_paper) if str(args.target) == "auto" else wrap_paper(int(args.target), N)
    sc_src_paper = parse_auto_expr(str(args.sc_src), N=N, n0_paper=n0_paper, target_paper=target_paper)
    sc_dst_paper = parse_auto_expr(str(args.sc_dst), N=N, n0_paper=n0_paper, target_paper=target_paper)

    def build_params(jumpover_absorbs: bool) -> Params:
        return Params(
            N=N,
            K=int(args.K),
            n0=paper_to0(n0_paper, N),
            target=paper_to0(target_paper, N),
            sc_src=paper_to0(sc_src_paper, N),
            sc_dst=paper_to0(sc_dst_paper, N),
            mode=str(args.mode),
            q=float(args.q),
            beta=float(args.beta),
            rho=float(args.rho),
            jumpover_absorbs=bool(jumpover_absorbs),
        )

    tmax_exact = int(args.tmax) if args.tmax is not None else default_tmax(N, float(args.tmax_mult))

    p0 = build_params(False)
    f0, surv0 = exact_first_absorption_pmf(p0, tmax=tmax_exact, survival_eps=float(args.survival_eps))
    peaks0 = detect_peaks_paper(f0, hmin=float(args.hmin), second_rel_height=float(args.second_rel_height))
    t10, tv0, t20 = first_two_peaks_and_valley(f0, peaks0)

    p1 = build_params(True)
    f1, surv1 = exact_first_absorption_pmf(p1, tmax=tmax_exact, survival_eps=float(args.survival_eps))
    peaks1 = detect_peaks_paper(f1, hmin=float(args.hmin), second_rel_height=float(args.second_rel_height))
    t11, tv1, t21 = first_two_peaks_and_valley(f1, peaks1)

    max_t = int(args.max_t_plot)
    max_t = min(max_t, int(max(f0.size, f1.size)))
    t = np.arange(1, max_t + 1, dtype=np.int32)

    fig, ax = plt.subplots(figsize=(9.2, 3.8), dpi=170)
    ax.plot(t, f0[:max_t], lw=1.2, label="baseline: allow jumpover")
    ax.plot(t, f1[:max_t], lw=1.2, ls="--", label="control: jumpover -> absorb")
    ax.set_yscale("log")
    ax.set_xlabel("t")
    ax.set_ylabel("f(t) (log)")
    ax.grid(True, alpha=0.2)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.set_title(
        f"Exact f(t) comparison (N={N}, K={int(args.K)}, q={float(args.q):.3g}, beta={float(args.beta):.3g}, rho={float(args.rho):.3g})"
    )
    fig.tight_layout()
    out_fig = out_prefix.with_suffix(".compare_f_t.pdf")
    fig.savefig(out_fig)
    plt.close(fig)

    out_json = out_prefix.with_suffix(".compare.json")
    with out_json.open("w", encoding="utf-8") as fjs:
        json.dump(
            {
                "baseline": {
                    "params": {**p0.__dict__, "p_shortcut": p_shortcut(p0)},
                    "survival_end": float(surv0),
                    "peaks_paper": peaks0,
                    "t1_tv_t2": {"t1": t10, "tv": tv0, "t2": t20},
                    "paper_bimodal": bool(paper_bimodal(peaks0)),
                    "macro_bimodal": bool(macro_bimodal(peaks0, macro_ratio=float(args.macro_ratio))),
                },
                "control": {
                    "params": {**p1.__dict__, "p_shortcut": p_shortcut(p1)},
                    "survival_end": float(surv1),
                    "peaks_paper": peaks1,
                    "t1_tv_t2": {"t1": t11, "tv": tv1, "t2": t21},
                    "paper_bimodal": bool(paper_bimodal(peaks1)),
                    "macro_bimodal": bool(macro_bimodal(peaks1, macro_ratio=float(args.macro_ratio))),
                },
            },
            fjs,
            ensure_ascii=False,
            indent=2,
        )

    out_npz = out_prefix.with_suffix(".compare_exact.npz")
    np.savez_compressed(out_npz, f_baseline=f0, f_control=f1, surv_baseline=float(surv0), surv_control=float(surv1))

    print(f"[compare-jumpover] wrote:\n  {out_fig}\n  {out_json}\n  {out_npz}")


# ---------------------------
# CLI
# ---------------------------


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Exact bimodality + jumpover trajectory decomposition (lazy ring)")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("scan-n", help="scan N for paper/macro bimodality (exact)")
    ps.add_argument("--K", type=int, required=True)
    ps.add_argument("--N-min", dest="N_min", type=int, required=True)
    ps.add_argument("--N-max", dest="N_max", type=int, required=True)
    ps.add_argument("--N-step", dest="N_step", type=int, default=1)
    ps.add_argument("--only-even", action="store_true")
    ps.add_argument("--beta", type=float, required=True)
    ps.add_argument("--q", type=float, default=2 / 3)
    ps.add_argument("--rho", type=float, default=1.0)
    ps.add_argument("--mode", type=str, default="lazy_selfloop", choices=["lazy_selfloop", "lazy_equal"])
    ps.add_argument(
        "--jumpover-absorbs",
        dest="jumpover_absorbs",
        action="store_true",
        help="Control model: if a ring move jump-overs target, count it as absorption (uses the same rho).",
    )
    ps.add_argument("--n0", type=int, default=1)
    ps.add_argument("--target", type=str, default="auto")
    ps.add_argument("--sc-src", dest="sc_src", type=str, default="auto+5")
    ps.add_argument("--sc-dst", dest="sc_dst", type=str, default="auto_target+1")
    ps.add_argument("--tmax", type=int, default=None)
    ps.add_argument("--tmax-mult", dest="tmax_mult", type=float, default=10.0)
    ps.add_argument("--survival-eps", dest="survival_eps", type=float, default=1e-14)
    ps.add_argument("--hmin", type=float, default=1e-7)
    ps.add_argument("--second-rel-height", dest="second_rel_height", type=float, default=0.01)
    ps.add_argument("--macro-ratio", dest="macro_ratio", type=float, default=10.0)
    ps.add_argument("--out", type=str, required=True)

    pb = sub.add_parser("scan-beta", help="scan beta for paper/macro bimodality (exact)")
    pb.add_argument("--N", type=int, required=True)
    pb.add_argument("--K", type=int, required=True)
    pb.add_argument("--q", type=float, default=2 / 3)
    pb.add_argument("--rho", type=float, default=1.0)
    pb.add_argument("--mode", type=str, default="lazy_selfloop", choices=["lazy_selfloop", "lazy_equal"])
    pb.add_argument(
        "--jumpover-absorbs",
        dest="jumpover_absorbs",
        action="store_true",
        help="Control model: if a ring move jump-overs target, count it as absorption (uses the same rho).",
    )
    pb.add_argument("--n0", type=int, default=1)
    pb.add_argument("--target", type=str, default="auto")
    pb.add_argument("--sc-src", dest="sc_src", type=str, default="auto+5")
    pb.add_argument("--sc-dst", dest="sc_dst", type=str, default="auto_target+1")
    pb.add_argument("--betas", type=float, nargs="*", default=None, help="Explicit beta list; overrides beta-min/max/num")
    pb.add_argument("--beta-min", dest="beta_min", type=float, default=0.0)
    pb.add_argument("--beta-max", dest="beta_max", type=float, default=0.2)
    pb.add_argument("--beta-num", dest="beta_num", type=int, default=21)
    pb.add_argument("--tmax", type=int, default=None)
    pb.add_argument("--tmax-mult", dest="tmax_mult", type=float, default=10.0)
    pb.add_argument("--survival-eps", dest="survival_eps", type=float, default=1e-14)
    pb.add_argument("--hmin", type=float, default=1e-7)
    pb.add_argument("--second-rel-height", dest="second_rel_height", type=float, default=0.01)
    pb.add_argument("--macro-ratio", dest="macro_ratio", type=float, default=10.0)
    pb.add_argument("--out", type=str, required=True)

    pa = sub.add_parser("analyze", help="analyze one case: exact f(t) + MC window stats")
    pa.add_argument("--N", type=int, required=True)
    pa.add_argument("--K", type=int, required=True)
    pa.add_argument("--beta", type=float, required=True)
    pa.add_argument("--q", type=float, default=2 / 3)
    pa.add_argument("--rho", type=float, default=1.0)
    pa.add_argument("--mode", type=str, default="lazy_selfloop", choices=["lazy_selfloop", "lazy_equal"])
    pa.add_argument(
        "--jumpover-absorbs",
        dest="jumpover_absorbs",
        action="store_true",
        help="Control model: if a ring move jump-overs target, count it as absorption (uses the same rho).",
    )
    pa.add_argument("--n0", type=int, default=1)
    pa.add_argument("--target", type=str, default="auto")
    pa.add_argument("--sc-src", dest="sc_src", type=str, default="auto+5")
    pa.add_argument("--sc-dst", dest="sc_dst", type=str, default="auto_target+1")
    pa.add_argument("--tmax", type=int, default=None)
    pa.add_argument("--tmax-mult", dest="tmax_mult", type=float, default=10.0)
    pa.add_argument("--tmax-mc", dest="tmax_mc", type=int, default=None)
    pa.add_argument("--tmax-mc-mult", dest="tmax_mc_mult", type=float, default=1.0)
    pa.add_argument("--survival-eps", dest="survival_eps", type=float, default=1e-14)
    pa.add_argument(
        "--exact-method",
        dest="exact_method",
        type=str,
        default="aw",
        choices=["aw", "time"],
        help="How to compute the 'exact' f(t) curve: AW inversion (default) or time-domain propagation.",
    )
    pa.add_argument("--aw-steps", dest="aw_steps", type=int, default=None, help="Max steps t for AW inversion output.")
    pa.add_argument("--aw-r", dest="aw_r", type=float, default=None, help="AW circle radius r (optional).")
    pa.add_argument("--aw-L", dest="aw_L", type=int, default=None, help="AW FFT length L (power of two, optional).")
    pa.add_argument("--hmin", type=float, default=1e-7)
    pa.add_argument("--second-rel-height", dest="second_rel_height", type=float, default=0.01)
    pa.add_argument("--delta-frac", dest="delta_frac", type=float, default=0.05)
    pa.add_argument("--delta-fallback", dest="delta_fallback", type=int, default=2)
    pa.add_argument("--n-walkers", dest="n_walkers", type=int, default=200_000)
    pa.add_argument("--seed", type=int, default=0)
    pa.add_argument("--max-t-plot", dest="max_t_plot", type=int, default=4000)
    pa.add_argument("--cond-max-t", dest="cond_max_t", type=int, default=None, help="Max t for conditional curves/CSV.")
    pa.add_argument("--cond-min-n", dest="cond_min_n", type=int, default=50, help="Min count at time t to report P(·|T=t).")
    pa.add_argument(
        "--cond-smooth-window",
        dest="cond_smooth_window",
        type=int,
        default=21,
        help="Odd moving window for smoothing conditional curves (applied to counts).",
    )
    pa.add_argument("--out-prefix", dest="out_prefix", type=str, required=True)

    pc = sub.add_parser(
        "compare-jumpover",
        help="exact comparison: baseline allow-jumpover vs control jumpover->absorb",
    )
    pc.add_argument("--N", type=int, required=True)
    pc.add_argument("--K", type=int, required=True)
    pc.add_argument("--beta", type=float, required=True)
    pc.add_argument("--q", type=float, default=2 / 3)
    pc.add_argument("--rho", type=float, default=1.0)
    pc.add_argument("--mode", type=str, default="lazy_selfloop", choices=["lazy_selfloop", "lazy_equal"])
    pc.add_argument("--n0", type=int, default=1)
    pc.add_argument("--target", type=str, default="auto")
    pc.add_argument("--sc-src", dest="sc_src", type=str, default="auto+5")
    pc.add_argument("--sc-dst", dest="sc_dst", type=str, default="auto_target+1")
    pc.add_argument("--tmax", type=int, default=None)
    pc.add_argument("--tmax-mult", dest="tmax_mult", type=float, default=10.0)
    pc.add_argument("--survival-eps", dest="survival_eps", type=float, default=1e-14)
    pc.add_argument("--hmin", type=float, default=1e-7)
    pc.add_argument("--second-rel-height", dest="second_rel_height", type=float, default=0.01)
    pc.add_argument("--macro-ratio", dest="macro_ratio", type=float, default=10.0)
    pc.add_argument("--max-t-plot", dest="max_t_plot", type=int, default=4000)
    pc.add_argument("--out-prefix", dest="out_prefix", type=str, required=True)

    return p


def main() -> None:
    p = build_argparser()
    args = p.parse_args()

    if args.cmd == "scan-n":
        cmd_scan_n(args)
    elif args.cmd == "scan-beta":
        cmd_scan_beta(args)
    elif args.cmd == "analyze":
        cmd_analyze(args)
    elif args.cmd == "compare-jumpover":
        cmd_compare_jumpover(args)
    else:
        raise SystemExit("Unknown command")


if __name__ == "__main__":
    main()
