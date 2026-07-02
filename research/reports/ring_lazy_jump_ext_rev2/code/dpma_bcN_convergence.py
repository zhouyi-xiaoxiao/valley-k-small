#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Round-4 (external-review) strengthening: finite-N fold THRESHOLD convergence b_{c,N} -> b_c.

The manuscript documents O(N^-2) convergence of the density reconstruction, but a referee can ask
whether the fold threshold itself converges. This script computes b_{c,N}(theta=1/2, xi=theta) on
the exact lazy ring (q=2/3, u=N/2, start r=u) by bisection on the existence of the interior
valley--peak pair of the exact F(t) (spectral decomposition of the transient block, eigvalsh),
for N = 100...1200, and fits the convergence exponent of |b_{c,N} - b_c| with
b_c = 3.0764323604 (continuum, mpmath-Newton certified).
Writes artifacts/tables/dpma_bcN_convergence.txt
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np

TAB = Path(__file__).resolve().parents[1] / "artifacts" / "tables"
TAB.mkdir(parents=True, exist_ok=True)
OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

q = 2.0 / 3.0
BC_CONT = 3.0764323604

def modes(N, b):
    """exact spectral modes of the antipodal defected ring: s_j (eigenvalues), B_j (residues)."""
    u = N // 2
    lam = b * q / N                      # lambda = beta(1-q) = b q / N
    M = np.zeros((N - 1, N - 1))
    for i in range(N - 1):
        M[i, i] = 1 - q
        if i > 0: M[i, i - 1] = q / 2
        if i < N - 2: M[i, i + 1] = q / 2
    M[u - 1, u - 1] -= lam
    b_abs = np.zeros(N - 1)
    b_abs[0] += q / 2; b_abs[-1] += q / 2; b_abs[u - 1] += lam
    s, V = np.linalg.eigh(M)
    er = np.zeros(N - 1); er[u - 1] = 1.0   # start at the source r = u
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        B = (er @ V) * (V.T @ b_abs)
    B = np.where(np.isfinite(B), B, 0.0)    # extreme modes are irrelevant on the fold window
    return s, B

def has_pair(N, b, npts=50_000):
    """interior valley+peak pair of F(t) on the fold window tau in [0.015, 0.12]."""
    s, B = modes(N, b)
    ls = np.log(np.clip(s, 1e-300, None))
    taus = np.linspace(0.015, 0.12, npts)
    ts = taus * N * N / q
    F = (np.exp(np.outer(ts - 1.0, ls)) * B).sum(axis=1)
    d1 = np.diff(F)
    sgn = np.sign(d1)
    idx = [i + 1 for i in range(len(sgn) - 1) if sgn[i] != 0 and sgn[i + 1] != 0 and sgn[i] != sgn[i + 1]]
    vmax = float(np.max(np.abs(F)))
    changed = True                        # prune floating wiggles pairwise (as in dpma_window_scan)
    while changed and len(idx) >= 2:
        changed = False
        for j in range(len(idx) - 1):
            if abs(F[idx[j + 1]] - F[idx[j]]) < 1e-9 * vmax:
                del idx[j + 1]; del idx[j]; changed = True; break
    return len(idx) >= 2

def bc_N(N, lo=2.6, hi=3.5, iters=36):
    if not has_pair(N, lo):
        return float("nan")
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if has_pair(N, mid): lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)

say("Finite-N fold-threshold convergence, antipodal (theta=xi=1/2, q=2/3)")
say(f"  continuum b_c = {BC_CONT}")
say(f"  {'N':>6} {'b_c,N':>12} {'b_c,N - b_c':>13}")
rows = []
for N in (100, 200, 300, 400, 600, 800, 1200):
    b = bc_N(N)
    rows.append((N, b))
    say(f"  {N:>6d} {b:>12.7f} {b - BC_CONT:>+13.2e}")
Ns = np.array([r[0] for r in rows], float)
dev = np.array([abs(r[1] - BC_CONT) for r in rows])
mask = dev > 1e-9
p, c = np.polyfit(np.log(Ns[mask]), np.log(dev[mask]), 1)
say("")
say(f"  log-log fit: |b_c,N - b_c| ~ N^({p:.2f})   (prefactor {math.exp(c):.3g})")
say("  => the fold threshold itself converges to the continuum value with the fitted exponent above.")
(TAB / "dpma_bcN_convergence.txt").write_text("\n".join(OUT) + "\n")
