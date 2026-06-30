#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Two-component reduced model for the double-peak window boundaries.

Components:
  capture wave  F_cap(t) = lam * W_free(d, t),  lam = beta(1-q),
                W_free = occupation of the shortcut site for a free lazy walk
                started at distance d (valid for t << N^2);
  around wave   F_arr(t) = exact slow-band mode sum of the beta=0 ring
                tilted by the (exact) shifted roots — evaluated through the
                full Chebyshev modes here, used in scaling form.

Derived constants (q = 2/3 fixed):
  c_w(d)  = d * max_t W_free(d, t)                 (discrete-lattice peak)
  C2(0)   = lim_N N^2 * max_t F0_{rho=L-d}(t)      (around-peak constant)
  A(d)    = C2(0) * d / (10 (1-q) c_w(d))          (lower edge, h2/h1 = 10)
  Asym(d) = 100 * A(d)                             (collapse branch, h2/h1 = 0.1)
  N*(d)   = 10 * C2(b_pl) * d / (q b_pl c_w(d))    (binding switch)

Validation targets (round-2 audit, bisection-refined):
  A(3) = 9.087(9), A(4) = 12.168(20), A(5) ~ 15.36
  collapse branch beta_hi N^2 -> ~917 (d=3, Richardson from N=400..800)
  h1*N = 0.0836 at b*N-fixed (beta N = 3.1, d=3); h2*N^2 = 3.00
  N*(3) ~ 360, N*(4) ~ 450
Writes artifacts/tables/dpma_reduced_model.txt
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from shortcut_double_peak_mode_attribution import Q_DEFAULT

q = Q_DEFAULT
OUT = []


def say(s=""):
    print(s, flush=True)
    OUT.append(s)


# ---------------------------------------------------------------- c_w(d)
def w_free_peak(d: int, tmax: int | None = None) -> tuple[float, int]:
    """max_t P(S_t = d) for the free lazy walk (stay 1-q, +-1 w.p. q/2)."""
    tmax = tmax or max(400, int(8 * d * d / q))
    M = d + int(7 * np.sqrt(q * tmax)) + 10
    p = np.zeros(2 * M + 1)
    p[M] = 1.0
    best, tbest = 0.0, 0
    for t in range(1, tmax + 1):
        p = (1 - q) * p + (q / 2) * (np.roll(p, 1) + np.roll(p, -1))
        p[0] = p[-1] = 0.0
        v = p[M + d]
        if v > best:
            best, tbest = v, t
    return best, tbest


# ------------------------------------------------- around-wave constants
def around_peak_const(d: int, N: int, b: float = 0.0) -> float:
    """N^2 * max_t F(t) of the around wave for start rho = L-d.

    b = 0: plain absorbing ring (path modes, exact).
    b > 0: exact shortcut chain (full Chebyshev modes) — used to get C2(b).
    """
    if b == 0.0:
        # Dirichlet path modes: alpha'_k = 1-q+q cos(k pi/N), phi_k ~ sin
        L = N // 2
        rho = L - d
        n0 = rho                      # site index measured from v
        ks = np.arange(1, N)
        lam = 1 - q + q * np.cos(ks * np.pi / N)
        phi_n0 = np.sin(ks * np.pi * n0 / N)
        # absorption vector: site 1 and site N-1 each connect to v with q/2
        phi_b = (q / 2) * (np.sin(ks * np.pi * 1 / N) + np.sin(ks * np.pi * (N - 1) / N))
        kap = (2.0 / N) * phi_n0 * phi_b
        ts = np.unique(np.round(np.logspace(0, np.log10(40 * N * N), 4000)).astype(int))
        F = (kap[None, :] * lam[None, :] ** (ts[:, None] - 1.0)).sum(axis=1)
        return float(N * N * F.max())
    else:
        from shortcut_double_peak_mode_attribution import evaluate
        beta = q * b / ((1 - q) * N)
        spec, F, feats = evaluate(N, q, beta, (N // 2 + d) % N)
        if feats.t2 is None:
            return float("nan")
        return float(N * N * feats.h2)


def main():
    say("=" * 76)
    say("Reduced-model constants (q = 2/3)")
    say("=" * 76)
    cw = {}
    for d in (3, 4, 5, 6):
        peak, tpk = w_free_peak(d)
        cw[d] = d * peak
        say(f"  c_w({d}) = d*max_t W_free = {cw[d]:.6f}   (peak at t = {tpk}, "
            f"continuum limit e^-0.5/sqrt(2 pi) = {np.exp(-0.5)/np.sqrt(2*np.pi):.6f})")

    say()
    say("Around-wave peak constant C2(0) = lim N^2 max F0 (rho = L-d):")
    C2 = {}
    for d in (3, 4, 5):
        vals = [(N, around_peak_const(d, N)) for N in (400, 800, 1600)]
        # empirical convergence is ~1/N^2: Richardson in 1/N^2
        (N1, v1), (N2, v2), (N3, v3) = vals
        slope = (v2 - v3) / (1 / N2**2 - 1 / N3**2)
        lim = v3 - slope / N3**2
        C2[d] = lim
        say(f"  d={d}: " + ", ".join(f"N={N}: {v:.6f}" for N, v in vals)
            + f"  -> 1/N^2-extrapolated C2(0) = {lim:.6f}")
    say()
    say("Theta-series characterization: M = max_x 2 pi sum_j (-1)^j (2j+1) e^{-(2j+1)^2 x}")
    from mpmath import mp, mpf, exp as mexp, findroot
    mp.dps = 30
    def theta(x):
        return 2 * mp.pi * mp.nsum(lambda j: (-1)**j * (2*j+1) * mexp(-(2*j+1)**2 * x), [0, mp.inf])
    xs = [mpf(i) / 1000 for i in range(300, 600)]
    vt = [theta(x) for x in xs]
    i0 = max(range(len(vt)), key=lambda i: vt[i])
    # golden refine
    import math as _m
    a_, b_ = float(xs[max(i0-1,0)]), float(xs[min(i0+1,len(xs)-1)])
    for _ in range(60):
        m1 = a_ + 0.382*(b_-a_); m2 = a_ + 0.618*(b_-a_)
        if theta(m1) < theta(m2): a_ = m1
        else: b_ = m2
    xstar = 0.5*(a_+b_); M = float(theta(xstar))
    say(f"  x* = {xstar:.5f}, M = {M:.6f},  q*M = {q*M:.6f}  "
        f"(vs C2(0) 1/N^2-extrapolated above)")

    say()
    say("=" * 76)
    say("Predictions vs measured")
    say("=" * 76)
    import csv as _csv
    ref = list(_csv.DictReader(open(Path(__file__).resolve().parents[1] / "artifacts" / "data" / "dpma_boundary_refined.csv")))
    say("  measured beta_lo*N^2 from dpma_boundary_refined.csv, two-point 1/N Richardson (N=200,240):")
    measured_A = {}
    for d in (3, 4, 5):
        pts = {int(r["N"]): float(r["beta_lo"]) * int(r["N"])**2
               for r in ref if r["window"] == "1" and int(r["d"]) == d and int(r["N"]) in (200, 240)}
        slope = (pts[200] - pts[240]) / (1/200 - 1/240)
        measured_A[d] = pts[240] - slope / 240
        say(f"    d={d}: raw N=200: {pts[200]:.3f}, N=240: {pts[240]:.3f} -> extrapolated {measured_A[d]:.3f}")
    for d in (3, 4, 5):
        A_pred = C2[d] * d / (10 * (1 - q) * cw[d])
        say(f"  A({d}): predicted = {A_pred:.3f}   measured(extrap) = {measured_A[d]:.3f}"
            f"   ratio = {A_pred / measured_A[d]:.4f}")
    say()
    say("  Collapse-branch asymptote: beta_hi N^2 -> 100*A(d)  [edge(h2/h1=0.1)/edge(h2/h1=10) = 100]")
    meas_note = {3: "(measured Richardson ~917 from N=400..800, see dpma_boundary_refined_largeN*.csv)",
                 4: "(no extrapolated measurement yet; raw N=640 edge beta_hi*N^2 = 1433)"}
    for d in (3, 4):
        say(f"    d={d}: predicted limit = {100 * C2[d] * d / (10 * (1 - q) * cw[d]):.0f}   {meas_note[d]}")

    say()
    say("  h1 check at fixed beta*N = 3.1, d=3: h1*N predicted = "
        f"{3.1 * (1 - q) * cw[3] / 3:.4f}   (audit measured 0.0836)")

    say()
    say("  C2(b) (tilted around-peak constant) and N*(d) = 10 C2(b_pl) d /(q b_pl c_w):")
    b_pl = 1.574
    for d in (3, 4):
        c2b = around_peak_const(d, 240, b=b_pl)
        Nstar = 10 * c2b * d / (q * b_pl * cw[d])
        say(f"    d={d}: C2(b_pl) at N=240 = {c2b:.4f}  ->  N*({d}) predicted = {Nstar:.0f}"
            f"   (audit: ~{360 if d == 3 else 450})")

    say()
    say("Leading-order plateau from the reduced valley equation")
    say("  T(x;b) = b/sqrt(2 pi x) + Theta_b(x),  Theta_b = 2 pi sum (-1)^j (2j+1) e^{-[(2j+1)^2 pi^2/2 + 2b] x}")
    import numpy as _np
    def Tfun(x, b, jmax=80):
        j = _np.arange(jmax)
        return b/_np.sqrt(2*_np.pi*x) + 2*_np.pi*_np.sum((-1)**j*(2*j+1)*_np.exp(-(((2*j+1)**2)*_np.pi**2/2 + 2*b)*x))
    def feats(b):
        xs = _np.logspace(-4, 1.2, 20000)
        vals = _np.array([Tfun(x, b) for x in xs])
        d1 = _np.diff(vals)
        mx = _np.where((d1[:-1] > 0) & (d1[1:] <= 0))[0] + 1
        if len(mx) == 0:
            return None
        p2 = mx[-1]; v = int(_np.argmin(vals[:p2+1]))
        if v == 0:
            return None
        return vals[v]/vals[p2], xs[p2]
    lo_, hi_ = 0.5, 4.0
    xpk0 = None
    for _ in range(50):
        mid = 0.5*(lo_+hi_); ff = feats(mid)
        if ff is None:
            hi_ = mid; continue
        if ff[0] < 0.8: lo_ = mid
        else: hi_ = mid
    say(f"  b_pl (leading order) = {0.5*(lo_+hi_):.4f}   (measured plateau 1.5738; gap = capture/around overlap region)")
    xpk0 = xstar / (np.pi**2 / 2)   # Theta_0 max position in x = q*tau units
    fpl = feats(0.5*(lo_+hi_))
    say(f"  around-peak position: x_peak2(b->0) = x*/(pi^2/2) = {xpk0:.4f}; at b_pl: {fpl[1]:.4f}")
    say(f"  -> fixed-x family peak-time ratio t2/t1 = {xpk0:.4f}/x^2 at b->0 "
        f"(shrinking to {fpl[1]:.4f}/x^2 at the plateau)")

    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_reduced_model.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(OUT) + "\n")
    say(f"\nwrote {p}")


if __name__ == "__main__":
    main()
