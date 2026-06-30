#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""General-u master function for the directed-shortcut first-passage problem.

SOURCE: derivation proposed by ChatGPT Pro (shared conversation
https://chatgpt.com/share/6a4273c0-dbc8-83eb-8495-b6ba6fd3dcff, 2026-06-12),
INDEPENDENTLY VERIFIED here against the exact transient matrix.  This is the
PRR-lever generalisation of the antipodal master function: the shortcut may
sit at any site u, not only u=N/2.

Model: lazy ring, stay 1-q, hop q/2; absorbing target v=0; directed shortcut
u->v moving lam=beta(1-q) off the u self-loop.  Deleting v leaves a Dirichlet
path 1..N-1 with a rank-one diagonal killing defect at u.

Claimed exact finite-N results (A_m(y):=U_{m-1}(y), A_0:=0, y=1+(1/z-1)/q,
a=q/(beta(1-q))):
  spectral determinant   D_u(y) = a U_{N-1}(y) + 2 U_{u-1}(y) U_{N-u-1}(y)
  generating function    F^(u)_r(z) = N_{r,u}(y)/D_u(y)
    r<=u:  N_{r,u} = a[A_r+A_{N-r}] + 2 A_{N-u}[A_r + A_{u-r}]
    r>=u:  N_{r,u} = a[A_r+A_{N-r}] + 2 A_u [A_{N-r} + A_{r-u}]
  time domain            F^(u)_r(t) = sum_j B^(u)_rj s_j^{t-1},
                         B^(u)_rj = q N_{r,u}(y_j)/D_u'(y_j),  s_j=1-q+q y_j
  channel-mass law       pi_sc^(u)(r) = 2 min(r,u)[N-max(r,u)] / (aN+2u(N-u))
  spectral shift (1st)   delta s_k = -2 beta(1-q)/N * sin^2(k pi u/N)
  continuum master       M_theta(w;b) = w sin2w + b sin(2 th w) sin(2(1-th)w),
                         th=u/N, b=beta(1-q)N/q; antipodal th=1/2 -> tan w=-2w/b

VERIFIED here (vs exact (N-1)x(N-1) transient matrix), q=2/3:
  V1 D_u vanishes at every exact eigen-y           (~1e-10, poly roundoff)
  V2 F^(u)_r(t) = sum_j B_rj s_j^{t-1} vs matrix    (max|diff| < 1e-12)
  V3 channel-mass law pi_sc^(u)(r)                  (< 1e-15)
  V4 spectral-shift law (beta->0 ratios -> 1; node modes frozen)
  V5 antipodal reduction D_{N/2} ∝ a T_L + U_{L-1}
NOT yet verified (stated by source, left as TODO): closed-form continuum
amplitudes G_{xi,theta}(w;b); the macroscopic two-peak window W_{xi,theta}.
Writes artifacts/tables/dpma_general_u_master.txt
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

q = 2.0 / 3.0
OUT = []


def say(s=""):
    print(s, flush=True)
    OUT.append(s)


def U(n: int, y: float) -> float:
    if n < 0:
        return 0.0
    um1, u0 = 0.0, 1.0
    for _ in range(1, n + 1):
        um1, u0 = u0, 2 * y * u0 - um1
    return u0


def A(m: int, y: float) -> float:
    return 0.0 if m == 0 else U(m - 1, y)


def transient_block(N, beta, u):
    n = N - 1
    M = np.zeros((n, n))
    b = np.zeros(n)
    lam = beta * (1 - q)
    for i in range(1, N):
        k = i - 1
        stay = (1 - q) * (1 - beta) if i == u else (1 - q)
        M[k, k] = stay
        if i == u:
            b[k] += lam
        for j in (i - 1, i + 1):
            if j % N == 0:
                b[k] += q / 2
            elif 1 <= j <= N - 1:
                M[k, (j % N) - 1] += q / 2
    return M, b


def D_u(y, N, u, a):
    return a * U(N - 1, y) + 2 * U(u - 1, y) * U(N - u - 1, y)


def Nnum(y, N, u, r, a):
    base = a * (A(r, y) + A(N - r, y))
    if r <= u:
        return base + 2 * A(N - u, y) * (A(r, y) + A(u - r, y))
    return base + 2 * A(u, y) * (A(N - r, y) + A(r - u, y))


def main():
    say("=" * 74)
    say("General-u master function verification (q=2/3); source: ChatGPT Pro,")
    say("independently checked vs exact transient matrix.")
    say("=" * 74)

    say("\nV1: D_u(y)=aU_{N-1}+2U_{u-1}U_{N-u-1} vanishes at exact eigen-y")
    cases = [(40, 13, 0.05), (60, 17, 0.03), (50, 25, 0.02), (41, 9, 0.08), (80, 20, 0.01)]
    for N, u, beta in cases:
        a = q / (beta * (1 - q))
        M, _ = transient_block(N, beta, u)
        s = np.sort(np.linalg.eigvalsh(M))[::-1]
        ys = (s - (1 - q)) / q
        dmax = max(abs(D_u(y, N, u, a)) for y in ys)
        say(f"  N={N} u={u} beta={beta}: max|D_u(y_exact)| = {dmax:.2e}")

    say("\nV2: time-domain F^(u)_r(t)=sum_j B_rj s_j^{t-1} vs exact matrix iteration")
    for N, u, r, beta in [(40, 13, 10, 0.05), (60, 17, 45, 0.03), (50, 25, 28, 0.02)]:
        a = q / (beta * (1 - q))
        M, b = transient_block(N, beta, u)
        # exact F(t)
        n = N - 1
        p = np.zeros(n); p[r - 1] = 1.0
        Fex = []
        for _ in range(150):
            Fex.append(float(p @ b))
            p = p @ M
        Fex = np.array(Fex)
        # closed form: roots of D_u, residues B_rj = q N/D'
        s = np.sort(np.linalg.eigvalsh(M))[::-1]
        ys = (s - (1 - q)) / q
        h = 1e-6
        B = np.array([q * Nnum(y, N, u, r, a) / ((D_u(y + h, N, u, a) - D_u(y - h, N, u, a)) / (2 * h)) for y in ys])
        ts = np.arange(1, 151)
        Fcf = np.array([float(np.sum(B * s ** (t - 1))) for t in ts])
        say(f"  N={N} u={u} r={r} beta={beta}: max|F_closedform - F_matrix| = {np.max(np.abs(Fcf - Fex)):.2e}")

    say("\nV3: channel-mass law pi_sc^(u)(r) = 2 min(r,u)[N-max]/(aN+2u(N-u))")
    for N, u, r, beta in [(40, 13, 10, 0.05), (60, 17, 25, 0.03), (50, 25, 28, 0.02)]:
        a = q / (beta * (1 - q))
        M, b = transient_block(N, beta, u)
        n = N - 1
        Ginv = np.linalg.solve(np.eye(n) - M, np.eye(n))
        exact = beta * (1 - q) * Ginv[r - 1, u - 1]
        formula = 2 * min(r, u) * (N - max(r, u)) / (a * N + 2 * u * (N - u))
        say(f"  N={N} u={u} r={r} beta={beta}: exact={exact:.10f} formula={formula:.10f} |d|={abs(exact-formula):.1e}")

    say("\nV4: 1st-order spectral shift delta s_k = -2 beta(1-q)/N sin^2(k pi u/N)")
    N, u = 160, 40
    M0, _ = transient_block(N, 0.0, u)
    w0 = np.sort(np.linalg.eigvalsh(M0))[::-1]
    for beta in (1e-5, 1e-4):
        M1, _ = transient_block(N, beta, u)
        w1 = np.sort(np.linalg.eigvalsh(M1))[::-1]
        ks = np.arange(1, 7)
        pred = -2 * beta * (1 - q) / N * np.sin(ks * np.pi * u / N) ** 2
        got = w1[:6] - w0[:6]
        items = []
        for g, pp in zip(got, pred):
            items.append(f"frozen|{abs(g):.0e}|" if abs(pp) < 1e-18 else f"{g/pp:.5f}")
        say(f"  beta={beta:.0e} ratios got/pred (k=1..6): " + ", ".join(items))

    say("\nV5: antipodal reduction  D_{N/2}(y) = 2 U_{L-1}(y) [a T_L(y)+U_{L-1}(y)]")
    from numpy.polynomial import chebyshev as C
    N = 60; L = 30; a = 3.0
    for y in (0.3, -0.4, 0.95):
        lhs = D_u(y, N, L, a)
        TL = C.chebval(y, [0] * L + [1])
        rhs = 2 * U(L - 1, y) * (a * TL + U(L - 1, y))
        say(f"  y={y}: D_u={lhs:.6f}  2U_(L-1)(aT_L+U_(L-1))={rhs:.6f}  |d|={abs(lhs-rhs):.1e}")

    say("\nV6: continuum master M_theta(w;b)=w sin2w + b sin(2thw)sin(2(1-th)w);")
    say("    theta=1/2 reduces to tan w = -2w/b")
    b = 1.5
    for w in (1.0, 2.0, 3.5):
        Mhalf = w * math.sin(2 * w) + b * math.sin(w) ** 2
        # tan w = -2w/b  <=>  2w cos w + b sin w = 0
        red = 2 * w * math.cos(w) + b * math.sin(w)
        say(f"  w={w}: M_(1/2)={Mhalf:.6f}  sin w * (2w cos w + b sin w)={math.sin(w)*red:.6f}")

    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_general_u_master.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(OUT) + "\n")
    say(f"\nwrote {p}")


if __name__ == "__main__":
    main()
