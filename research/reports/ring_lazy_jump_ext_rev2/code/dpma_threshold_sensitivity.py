#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Threshold sensitivity of the clear-double-peak window edges
(sensitivity_thresholds.py conventions, adapted to the C.2 rule).

Varies, one at a time around the C.2 defaults (N=100, d=4):
  min_ratio   in {0.005, 0.01, 0.02}     (secondary vs largest peak)
  min_sep     in {8, 10, 12}             (peak separation, steps)
  hratio band [1/H, H] for H in {8, 10, 12}
  valley_frac in {0.7, 0.8, 0.9}
and reports the bisected (beta_lo, beta_hi) per variant.
Writes artifacts/tables/dpma_threshold_sensitivity.csv
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from shortcut_double_peak_mode_attribution import (
    Spectral, detect_peaks, pmf_from_modes, tmax_for, transient_block,
    Q_DEFAULT, SURVIVAL_EPS, MIN_RATIO, MIN_SEP, HRATIO_HI, VALLEY_FRAC,
)

q = Q_DEFAULT


def clear_with(N, beta, d, min_ratio, min_sep, H, vfrac_max):
    A, b = transient_block(N, q, beta)
    w, V = np.linalg.eigh(A)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    n0 = (N // 2 + d) % N
    kap = V[n0 - 1, :] * (V.T @ b)
    F = pmf_from_modes(w, kap, tmax_for(w))
    csum = np.cumsum(F)
    idx = int(np.searchsorted(csum, 1.0 - SURVIVAL_EPS))
    if idx + 1 < len(F):
        F = F[: idx + 1]
    peaks = detect_peaks(F)
    if peaks.size < 2:
        return False
    pa, pb = int(peaks[0]), int(peaks[1])
    h_max = float(F[peaks].max())
    lo, hi = sorted((pa, pb))
    valley = int(lo + np.argmin(F[lo:hi + 1]))
    h_early, h_late = float(F[lo]), float(F[hi])
    hr = h_late / max(h_early, 1e-300)
    vf = float(F[valley] / max(min(h_early, h_late), 1e-300))
    return (float(F[pb]) / h_max >= min_ratio and (hi - lo) >= min_sep
            and (1.0 / H) <= hr <= H and vf <= vfrac_max)


def edges(N, d, **kw):
    coarse = np.round(np.logspace(-4.0, -0.8, 34), 8)
    flags = [(float(b), clear_with(N, float(b), d, **kw)) for b in coarse]
    clear = [b for b, c in flags if c]
    if not clear:
        return None, None
    lo0 = max([b for b, c in flags if not c and b < min(clear)], default=min(clear))
    hi0 = min([b for b, c in flags if not c and b > max(clear)], default=max(clear))
    def bis(b_out, b_in):
        lo, hi = b_out, b_in
        for _ in range(12):
            mid = float(np.sqrt(lo * hi))
            if clear_with(N, mid, d, **kw):
                hi = mid
            else:
                lo = mid
        return float(np.sqrt(lo * hi))
    return bis(lo0, min(clear)), bis(hi0, max(clear))


def main():
    N, d = 100, 4
    base = dict(min_ratio=MIN_RATIO, min_sep=MIN_SEP, H=HRATIO_HI, vfrac_max=VALLEY_FRAC)
    variants = [("baseline", dict(base))]
    for v in (0.005, 0.02):
        variants.append((f"min_ratio={v}", dict(base, min_ratio=v)))
    for v in (8, 12):
        variants.append((f"min_sep={v}", dict(base, min_sep=v)))
    for v in (8.0, 12.0):
        variants.append((f"H={v}", dict(base, H=v)))
    for v in (0.7, 0.9):
        variants.append((f"valley_frac={v}", dict(base, vfrac_max=v)))
    rows = []
    for name, kw in variants:
        blo, bhi = edges(N, d, **kw)
        rows.append(dict(variant=name, beta_lo=blo, beta_hi=bhi,
                         beta_lo_N2=None if blo is None else blo * N * N,
                         beta_hi_N=None if bhi is None else bhi * N))
        print(f"{name:18s}: beta_lo={blo:.6f} ({blo*N*N:.2f}/N^2)  "
              f"beta_hi={bhi:.6f} ({bhi*N:.3f}/N)" if blo else f"{name}: no window",
              flush=True)
    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_threshold_sensitivity.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("wrote", p)


if __name__ == "__main__":
    main()
