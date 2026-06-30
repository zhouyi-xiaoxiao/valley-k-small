#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Exact N->infinity master function of the shortcut first-passage problem,
and the EXACT plateau constant b_pl (closing the 1.375 vs 1.5738 gap).

Diffusion limit of the Chebyshev characteristic D(y)=a T_L(y)+U_{L-1}(y)=0
with a=N/b, 1-s = q*mu/N^2, w=sqrt(mu/2):

  root equation   :  tan(w) = -2w/b      (one root w_j per ((j-1/2)pi, j pi))
  scaled rates    :  mu_j(b) = 2 w_j^2
  scaled residues :  G_j(b) = 4 w_j (1-cos w_j) / ( sin w_j * [1 + b(b+2)/(4w_j^2)] )
  master function :  N^2 F(t=xN^2/q) -> Phi(x;b) = q * sum_j G_j e^{-2 w_j^2 x}

Limits: b->0: w_j -> (2j-1)pi/2, mu_j -> (2j-1)^2 pi^2/2 + 2b (parallel-lines
law), G_j -> (-1)^{j-1} 2 pi (2j-1) (the theta series; max = M = 3.700260).

The C.2 valley-bound upper edge in the diffusion limit is the EXACT scalar
equation  Phi(x_valley) = 0.8 * Phi(x_peak2) (interior valley local minimum
vs last local maximum), giving b_pl with no free input.

Validations performed here:
  V1 mode-by-mode: mu_j, G_j vs exact Chebyshev modes at N=800, b=1.5
  V2 curve-level: Phi(x;b) vs N^2 F(xN^2/q) at N=800
  V3 b->0: max Phi/q -> M = 3.700260
  V4 b_pl(exact master) vs measured plateau 1.5738@N=240..320 and its
     1/N extrapolation ~1.573
Writes artifacts/tables/dpma_master_function.txt
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from shortcut_double_peak_mode_attribution import Q_DEFAULT, chebyshev_modes, evaluate

q = Q_DEFAULT
OUT = []


def say(s=""):
    print(s, flush=True)
    OUT.append(s)


def roots_w(b: float, J: int) -> np.ndarray:
    """w_j solving 2w cos w + b sin w = 0 in ((j-1/2)pi, j pi), j=1..J."""
    ws = np.empty(J)
    h = lambda w: 2 * w * math.cos(w) + b * math.sin(w)
    for j in range(1, J + 1):
        lo, hi = (j - 0.5) * math.pi + 1e-12, j * math.pi - 1e-12
        flo = h(lo)
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            fm = h(mid)
            if flo * fm <= 0:
                hi = mid
            else:
                lo, flo = mid, fm
        ws[j - 1] = 0.5 * (lo + hi)
    return ws


def G_of(ws: np.ndarray, b: float) -> np.ndarray:
    return 4 * ws * (1 - np.cos(ws)) / (np.sin(ws) * (1 + b * (b + 2) / (4 * ws**2)))


def phi(xs: np.ndarray, b: float, J: int = 400):
    ws = roots_w(b, J)
    G = G_of(ws, b)
    mu = 2 * ws**2
    return q * (G[None, :] * np.exp(-np.outer(xs, mu))).sum(axis=1)


def features_phi(b: float, xlo=2e-3, xhi=2.0, n=24000):
    xs = np.exp(np.linspace(math.log(xlo), math.log(xhi), n))
    vals = phi(xs, b)
    d1 = np.diff(vals)
    maxima = np.where((d1[:-1] > 0) & (d1[1:] <= 0))[0] + 1
    if len(maxima) == 0:
        return None
    p2 = int(maxima[-1])
    v = int(np.argmin(vals[: p2 + 1]))
    if v == 0:
        return None
    return vals[v], vals[p2], xs[v], xs[p2]


def main():
    say("=" * 76)
    say("V1: scaled rates/residues vs exact Chebyshev modes (N=800, b=1.5, d=3)")
    say("=" * 76)
    N, d, b = 800, 3, 1.5
    L = N // 2
    beta = q * b / ((1 - q) * N)
    s_ex, B_ex = chebyshev_modes(N, q, beta, L - d)
    ws = roots_w(b, 8)
    G = G_of(ws, b)
    mu = 2 * ws**2
    for j in range(6):
        mu_N = (1 - s_ex[j]) * N * N / q
        G_N = B_ex[j] * N * N / q
        say(f"  j={j+1}: mu = {mu[j]:.6f} vs N-exact {mu_N:.6f} "
            f"(rel {abs(mu[j]/mu_N-1):.2e});  G = {G[j]:.6f} vs {G_N:.6f} "
            f"(rel {abs(G[j]/G_N-1):.2e})")

    say(); say("=" * 76)
    say("V2: Phi(x;b) vs N^2 F(x N^2/q) at N=800, b=1.5, d=3")
    say("=" * 76)
    spec, F, _ = evaluate(N, q, beta, (L + d) % N)
    for x in (0.01, 0.02, 0.05, 0.1, 0.2):
        t = int(round(x * N * N / q))
        lhs = float(phi(np.array([x]), b)[0])
        rhs = N * N * F[t - 1]
        say(f"  x={x:5.2f}: Phi = {lhs:.6f}   N^2 F = {rhs:.6f}   rel diff = {abs(lhs/rhs-1):.2e}")

    say(); say("=" * 76)
    say("V3: b->0 limit: max_x Phi/q vs theta maximum M = 3.700260")
    say("=" * 76)
    for bb in (1e-4, 1e-3):
        f = features_phi(bb)
        # at b->0 there is no capture tail in Phi? (G_j ~ alternating) ->
        # just report the max
        xs = np.exp(np.linspace(math.log(2e-3), math.log(2.0), 24000))
        vals = phi(xs, bb)
        say(f"  b={bb:.0e}: max Phi/q = {vals.max()/q:.6f}")

    say(); say("=" * 76)
    say("V4: EXACT plateau constant from the master valley equation")
    say("=" * 76)
    lo, hi = 0.8, 3.5
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        f = features_phi(mid)
        if f is None:
            hi = mid
            continue
        vv, h2, xv, xp = f
        if vv / h2 < 0.8:
            lo = mid
        else:
            hi = mid
    b_pl = 0.5 * (lo + hi)
    f = features_phi(b_pl)
    say(f"  b_pl(exact master) = {b_pl:.5f}")
    say(f"    at b_pl: valley/h2 = {f[0]/f[1]:.5f}, x_valley = {f[2]:.4f}, x_peak2 = {f[3]:.4f}")
    say(f"    measured plateau: 1.57384 (N=240), 1.5736 (N=320); 1/N extrapolation ~1.573")
    say(f"    leading-order (frozen amplitudes) was 1.3746")
    # threshold sensitivity of the exact constant
    for thr in (0.75, 0.85):
        lo2, hi2 = 0.8, 3.5
        for _ in range(50):
            mid = 0.5 * (lo2 + hi2)
            ff = features_phi(mid)
            if ff is None:
                hi2 = mid
                continue
            if ff[0] / ff[1] < thr:
                lo2 = mid
            else:
                hi2 = mid
        say(f"    threshold {thr}: b_pl = {0.5*(lo2+hi2):.5f}")
    # exact C2(b_pl) and N*(d)
    h2 = f[1] / q
    say(f"  C2(b_pl)/q = max-side peak of Phi/q at b_pl = {h2:.5f} -> C2 = {q*h2:.5f}")
    cw = {3: 0.244324, 4: 0.243269}
    for d2 in (3, 4):
        Nstar = 10 * (q * h2) * d2 / (q * b_pl * cw[d2])
        say(f"  N*({d2}) with exact constants = {Nstar:.0f}   (measured ~360 / ~450)")

    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_master_function.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(OUT) + "\n")
    say(f"\nwrote {p}")


if __name__ == "__main__":
    main()
