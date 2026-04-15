#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recompute / debug utilities for:
- 1D ring two-walker encounter FPT (Tenc = min{t>=1: X_t=Y_t})
- directed shortcut (selfloop mode): p_sc = beta*(1-q1) taken from walker-1 self-loop at src, injected to dst
- exact recursion (no Monte Carlo), plus optional channel decomposition:
    f_total(t) = f_no_shortcut_used(t) + f_shortcut_used(t)
- baseline cross-check: beta=0 reduces to 1D relative-coordinate hitting problem

This script reproduces the addendum CSV/plots generated in ChatGPT analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def build_step_probs(q: float, g: float):
    """Lazy biased NN walk on ring: stay prob 1-q, move ±1 prob split by drift g∈[-1,1]."""
    p_stay = 1.0 - q
    p_plus = q * (1.0 + g) / 2.0
    p_minus = q * (1.0 - g) / 2.0
    if min(p_stay, p_plus, p_minus) < -1e-15:
        raise ValueError(f"invalid probs: stay={p_stay}, plus={p_plus}, minus={p_minus}")
    return p_stay, p_plus, p_minus

def propagate_left_ring(J, p_stay, p_plus, p_minus):
    """K = P^T J for translation-invariant NN ring (axis=0)."""
    return p_stay * J + p_plus * np.roll(J, 1, axis=0) + p_minus * np.roll(J, -1, axis=0)

def propagate_right_ring(K, p_stay, p_plus, p_minus):
    """J_next = K P for translation-invariant NN ring (axis=1)."""
    return p_stay * K + p_plus * np.roll(K, 1, axis=1) + p_minus * np.roll(K, -1, axis=1)

def encounter_distribution_anywhere(
    N: int,
    q1: float, g1: float,
    q2: float, g2: float,
    n0: int, m0: int,
    src: int | None = None,
    dst: int | None = None,
    beta: float = 0.0,
    t_max: int = 1600,
    decompose_shortcut: bool = False,
):
    """
    Exact recursion for anywhere-encounter FPT:
        Tenc = min{t>=1 : X_t == Y_t}

    If src,dst are given, walker-1 has directed shortcut src->dst with selfloop mode:
        p_sc = beta*(1-q1),
        P1(src->src) = (1-q1) - p_sc,
        P1(src->dst) += p_sc.
    (So beta must satisfy 0 <= beta <= 1.)

    Return:
      - if not decompose_shortcut: f[t] (t=0..t_max; only t>=1 nonzero)
      - else: (f_no[t], f_yes[t]) where "yes" means shortcut has been used at least once by time t.
    """
    p1_stay, p1_plus, p1_minus = build_step_probs(q1, g1)
    p2_stay, p2_plus, p2_minus = build_step_probs(q2, g2)

    if src is None or dst is None:
        p_sc = 0.0
    else:
        src %= N
        dst %= N
        p_sc = beta * (1.0 - q1)
        if p_sc < -1e-15 or p_sc > p1_stay + 1e-12:
            raise ValueError("beta too large for selfloop shortcut: p_sc exceeds self-loop mass")

    if not decompose_shortcut:
        J = np.zeros((N, N), dtype=np.float64)
        J[n0 % N, m0 % N] = 1.0
        f = np.zeros(t_max + 1, dtype=np.float64)

        for t in range(1, t_max + 1):
            K = propagate_left_ring(J, p1_stay, p1_plus, p1_minus)
            if p_sc != 0.0:
                # fix src-row: remove p_sc from stay contribution, add to dst row
                K[src, :] -= p_sc * J[src, :]
                K[dst, :] += p_sc * J[src, :]
            J_next = propagate_right_ring(K, p2_stay, p2_plus, p2_minus)

            f[t] = np.trace(J_next)  # absorption at diagonal
            np.fill_diagonal(J_next, 0.0)
            J = J_next

        return f

    # channel decomposition
    J_no = np.zeros((N, N), dtype=np.float64)
    J_yes = np.zeros((N, N), dtype=np.float64)
    J_no[n0 % N, m0 % N] = 1.0
    f_no = np.zeros(t_max + 1, dtype=np.float64)
    f_yes = np.zeros(t_max + 1, dtype=np.float64)

    for t in range(1, t_max + 1):
        # (a) no-shortcut-used-yet: same NN propagation, but src self-loop reduced (exit to used-state)
        K_no = propagate_left_ring(J_no, p1_stay, p1_plus, p1_minus)
        if p_sc != 0.0:
            K_no[src, :] -= p_sc * J_no[src, :]

        # (b) used-already: full physical shortcut stays in used-state
        K_yes = propagate_left_ring(J_yes, p1_stay, p1_plus, p1_minus)
        if p_sc != 0.0:
            K_yes[src, :] -= p_sc * J_yes[src, :]
            K_yes[dst, :] += p_sc * J_yes[src, :]

        # (c) transfer from no->yes when shortcut taken for first time
        if p_sc != 0.0:
            K_transfer = np.zeros_like(K_no)
            K_transfer[dst, :] = p_sc * J_no[src, :]
        else:
            K_transfer = 0.0

        J_no_next = propagate_right_ring(K_no, p2_stay, p2_plus, p2_minus)
        J_yes_next = propagate_right_ring(K_yes + K_transfer, p2_stay, p2_plus, p2_minus)

        f_no[t] = np.trace(J_no_next)
        f_yes[t] = np.trace(J_yes_next)

        np.fill_diagonal(J_no_next, 0.0)
        np.fill_diagonal(J_yes_next, 0.0)
        J_no, J_yes = J_no_next, J_yes_next

    return f_no, f_yes

def relative_chain_fpt(N, q1,g1,q2,g2, r0, t_max):
    """
    beta=0 baseline: translation invariance => relative coordinate R_t=X_t-Y_t is a Markov chain on Z_N.
    Encounter <=> hit R=0. This recursion is O(N t_max).
    """
    p1 = {-1: q1*(1-g1)/2, 0: 1-q1, 1: q1*(1+g1)/2}
    p2 = {-1: q2*(1-g2)/2, 0: 1-q2, 1: q2*(1+g2)/2}
    pdelta={}
    for s1,a in p1.items():
        for s2,b in p2.items():
            d=s1 - s2
            pdelta[d]=pdelta.get(d,0.0)+a*b

    p = np.zeros(N, dtype=np.float64)
    p[r0 % N] = 1.0
    f = np.zeros(t_max+1, dtype=np.float64)

    for t in range(1, t_max+1):
        p_next = np.zeros_like(p)
        for d,prob in pdelta.items():
            p_next += prob * np.roll(p, d)  # new[r] += prob*old[r-d]
        f[t] = p_next[0]
        p_next[0] = 0.0
        p = p_next

    return f

def moving_average(x, w: int):
    if w <= 1:
        return x.copy()
    kernel = np.ones(w)/w
    return np.convolve(x, kernel, mode='same')

def local_maxima_indices(y):
    return np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1

def peak_valley_metrics(y, t1, t2):
    seg = y[t1:t2+1]
    tv = t1 + int(np.argmin(seg))
    peak_ratio = min(y[t1], y[t2]) / max(y[t1], y[t2])
    valley_ratio = y[tv] / max(y[t1], y[t2])
    return tv, peak_ratio, valley_ratio

def choose_t2_score(y, t1, peaks, eps=1e-12):
    """
    Timescale-oriented peak-pair selector:
      score(t2) ∝ (t2-t1) * (peak balance) / (valley ratio)
    """
    best=None
    for t2 in peaks:
        if t2 <= t1: 
            continue
        tv, peak_ratio, valley_ratio = peak_valley_metrics(y, t1, t2)
        score = (t2 - t1) * peak_ratio / (valley_ratio + eps)
        if best is None or score > best[0]:
            best = (score, t2, tv, peak_ratio, valley_ratio)
    return best

def detector_timescale_bimodality(f, w=11, t_ignore=80, t_end=400, min_ratio=0.20, valley_cap=0.90, abs_thr=1e-12):
    """
    Return dict with phase∈{0,1,2}, peak count, and selected (t1,t2,tv, ratios).
    """
    y = moving_average(f, w)
    peaks = local_maxima_indices(y)
    peaks = peaks[(peaks>=t_ignore) & (peaks<=t_end) & (y[peaks] > abs_thr)]
    if len(peaks) < 2:
        return dict(phase=0, n_peaks=int(len(peaks)), t1=None, t2=None, tv=None, peak_ratio=None, valley_ratio=None)
    t1 = int(peaks[0])
    best = choose_t2_score(y, t1, peaks[1:])
    if best is None:
        return dict(phase=0, n_peaks=int(len(peaks)), t1=t1, t2=None, tv=None, peak_ratio=None, valley_ratio=None)
    _, t2, tv, peak_ratio, valley_ratio = best
    phase = 1
    if peak_ratio >= min_ratio and valley_ratio <= valley_cap:
        phase = 2
    return dict(phase=int(phase), n_peaks=int(len(peaks)), t1=int(t1), t2=int(t2), tv=int(tv),
                peak_ratio=float(peak_ratio), valley_ratio=float(valley_ratio))

def main():
    # representative config (same as report)
    N=101; q=0.70; g1=0.70; g2=-0.40
    n0=5; m0=55
    src=5; dst=70
    t_max=1600

    # sanity: beta=0 cross-check with relative chain
    f0 = encounter_distribution_anywhere(N,q,g1,q,g2,n0,m0,None,None,0.0,t_max,False)
    r0 = (n0 - m0) % N
    f_rel = relative_chain_fpt(N,q,g1,q,g2,r0,t_max)
    print("beta=0 max|diff|:", float(np.max(np.abs(f0 - f_rel))))

    # beta scan + plots
    beta_grid = np.round(np.arange(0.0, 0.30+1e-9, 0.02), 2)
    rows=[]
    for beta in beta_grid:
        f_no, f_yes = encounter_distribution_anywhere(N,q,g1,q,g2,n0,m0,src,dst,float(beta),t_max,True)
        f = f_no + f_yes
        met = detector_timescale_bimodality(f, w=11, t_ignore=80, t_end=400, min_ratio=0.20, valley_cap=0.90)
        met["beta"] = float(beta)
        met["mass"] = float(f.sum())
        rows.append(met)

    df = pd.DataFrame(rows).sort_values("beta")
    df.to_csv("beta_scan_timescale_detector.csv", index=False)

    # plot: peak count vs beta
    plt.figure()
    plt.plot(df["beta"], df["n_peaks"], marker='o')
    plt.xlabel("beta")
    plt.ylabel("n_peaks (t in [80,400], smoothed w=11)")
    plt.grid(True, ls='--', alpha=0.4)
    plt.savefig("peakcount_vs_beta.png", dpi=200, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    main()
