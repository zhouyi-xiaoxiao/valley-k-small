#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Refine the clear-double-peak beta window edges by bisection per (N, d),
and record the capture probability pi_sc = rho/(a+L) at each refined edge.
Tests the boundary-collapse hypothesis: edges at ~constant pi_sc.

Writes artifacts/data/dpma_boundary_refined.csv
"""

from __future__ import annotations

import csv
import time
from pathlib import Path

import numpy as np

from shortcut_double_peak_mode_attribution import (
    Q_DEFAULT, Spectral, classify, pmf_from_modes, tmax_for,
    transient_block, SURVIVAL_EPS,
)


def is_clear(N: int, q: float, beta: float, d: int) -> bool:
    A, b = transient_block(N, q, beta)
    w, V = np.linalg.eigh(A)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    Vb = V.T @ b
    n0 = (N // 2 + d) % N
    k0, ku = n0 - 1, N // 2 - 1
    spec = Spectral(w, V[k0, :] * Vb, V[k0, :] * V[ku, :], N, q, beta, n0)
    F = pmf_from_modes(spec.lams, spec.kappas, tmax_for(w))
    csum = np.cumsum(F)
    idx = int(np.searchsorted(csum, 1.0 - SURVIVAL_EPS))
    if idx + 1 < len(F):
        F = F[: idx + 1]
    return classify(F, spec).clear_double


def pi_sc(N: int, q: float, beta: float, d: int) -> float:
    L = N // 2
    a = q / (beta * (1.0 - q))
    return (L - d) / (a + L)


def bisect_edge(N, q, d, b_false, b_true, steps=14):
    """Bisect between a non-clear beta and a clear beta (log scale)."""
    lo, hi = b_false, b_true
    for _ in range(steps):
        mid = float(np.sqrt(lo * hi))
        if is_clear(N, q, mid, d):
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", type=int, nargs="+",
                    default=[16, 20, 24, 30, 36, 44, 52, 60, 70, 80, 100, 120, 140, 170, 200, 240])
    ap.add_argument("--ds", type=int, nargs="+", default=[3, 4, 5])
    ap.add_argument("--suffix", default="")
    args = ap.parse_args()
    q = Q_DEFAULT
    out = Path(__file__).resolve().parents[1] / "artifacts" / "data" / f"dpma_boundary_refined{args.suffix}.csv"
    Ns = args.ns
    ds = args.ds
    coarse = np.round(np.logspace(-4.2, -0.6, 40), 8)
    rows = []
    t0 = time.time()
    for d in ds:
        for N in Ns:
            if N // 2 <= d + 2:
                continue
            flags = [(float(b), is_clear(N, q, float(b), d)) for b in coarse]
            clear_bs = [b for b, c in flags if c]
            if not clear_bs:
                rows.append(dict(N=N, d=d, q=q, beta_lo=None, beta_hi=None,
                                 pi_lo=None, pi_hi=None, window=0))
                print(f"d={d} N={N}: no clear window ({time.time()-t0:.0f}s)", flush=True)
                continue
            b_first, b_last = min(clear_bs), max(clear_bs)
            below = [b for b, c in flags if not c and b < b_first]
            above = [b for b, c in flags if not c and b > b_last]
            beta_lo = bisect_edge(N, q, d, max(below), b_first) if below else b_first
            beta_hi = bisect_edge(N, q, d, min(above), b_last) if above else b_last
            rows.append(dict(N=N, d=d, q=q,
                             beta_lo=beta_lo, beta_hi=beta_hi,
                             pi_lo=pi_sc(N, q, beta_lo, d),
                             pi_hi=pi_sc(N, q, beta_hi, d), window=1))
            print(f"d={d} N={N}: beta=[{beta_lo:.6f},{beta_hi:.6f}] "
                  f"pi=[{pi_sc(N,q,beta_lo,d):.4f},{pi_sc(N,q,beta_hi,d):.4f}] "
                  f"({time.time()-t0:.0f}s)", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        wcsv = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(rows)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
