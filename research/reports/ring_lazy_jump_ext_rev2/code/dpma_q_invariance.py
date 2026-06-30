#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Residual q-dependence of the clear-double-peak window in b units.

Bisects both window edges at q = 1/2 and q = 2/3 (N=240, d=3,4) and reports
b-edges and their relative differences.  Archives the round-2 audit's
q-invariance observation as a reproducible artifact.
Writes artifacts/tables/dpma_q_invariance.csv
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from shortcut_double_peak_mode_attribution import (
    Spectral, classify, pmf_from_modes, tmax_for, transient_block, SURVIVAL_EPS,
)


def is_clear(N, q, beta, d):
    A, b = transient_block(N, q, beta)
    w, V = np.linalg.eigh(A)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    Vb = V.T @ b
    n0 = (N // 2 + d) % N
    spec = Spectral(w, V[n0 - 1, :] * Vb, V[n0 - 1, :] * V[N // 2 - 1, :], N, q, beta, n0)
    F = pmf_from_modes(spec.lams, spec.kappas, tmax_for(w))
    csum = np.cumsum(F)
    idx = int(np.searchsorted(csum, 1.0 - SURVIVAL_EPS))
    if idx + 1 < len(F):
        F = F[: idx + 1]
    return classify(F, spec).clear_double


def edges(N, q, d):
    coarse = np.round(np.logspace(-4.2, -0.6, 40), 8)
    flags = [(float(b), is_clear(N, q, float(b), d)) for b in coarse]
    clear = [b for b, c in flags if c]
    lo_brk = (max(b for b, c in flags if not c and b < min(clear)), min(clear))
    hi_brk = (max(clear), min(b for b, c in flags if not c and b > max(clear)))
    def bisect(b0, b1, want_first_clear):
        lo, hi = b0, b1
        for _ in range(14):
            mid = float(np.sqrt(lo * hi))
            if is_clear(N, q, mid, d) == want_first_clear:
                hi = mid
            else:
                lo = mid
        return float(np.sqrt(lo * hi))
    return bisect(*lo_brk, True), bisect(*hi_brk, False)


def main():
    rows = []
    N = 240
    for d in (3, 4):
        res = {}
        for q in (0.5, 2.0 / 3.0):
            blo, bhi = edges(N, q, d)
            res[q] = (blo * (1 - q) * N / q, bhi * (1 - q) * N / q)
            print(f"N={N} d={d} q={q:.4f}: b_lo={res[q][0]:.6f} b_hi={res[q][1]:.6f}", flush=True)
        rel_lo = abs(res[0.5][0] - res[2/3][0]) / res[2/3][0]
        rel_hi = abs(res[0.5][1] - res[2/3][1]) / res[2/3][1]
        rows.append(dict(N=N, d=d, b_lo_q12=res[0.5][0], b_lo_q23=res[2/3][0],
                         b_hi_q12=res[0.5][1], b_hi_q23=res[2/3][1],
                         rel_dev_lo=rel_lo, rel_dev_hi=rel_hi))
        print(f"  -> relative q-dependence: lower {rel_lo:.4%}, upper {rel_hi:.4%}")
    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_q_invariance.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("wrote", p)


if __name__ == "__main__":
    main()
