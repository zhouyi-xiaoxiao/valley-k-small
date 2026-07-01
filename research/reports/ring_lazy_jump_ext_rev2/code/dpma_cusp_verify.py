#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Independently VERIFY ChatGPT-Pro's located cusp of the two-shortcut FPT density (roadmap #2).

Pro (multi-round) located a codim-2 cusp S1=S2=S3=0 (nondeg S4!=0, unfolding det!=0) at
  (alpha,beta,b1,b2,tau_c) = (0.38, 0.489580512568, 1.35, 1.08389352452, 0.00123657668735), xi=0.463.
Here we implement Pro's rank-2 continuum amplitudes from scratch and check the cusp condition +
the reported (k_j, G_j) table + the unfolding determinant. (Replaces the earlier peak-count
locator, which over-counted.)  Continuum, m=2 shortcuts at theta_1=alpha<theta_2=beta.
Writes artifacts/tables/dpma_cusp_verify.txt
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np

OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

def r0(k, x, y):
    xl, xg = (x, y) if x <= y else (y, x)
    return 2*math.sin(k*xl)*math.sin(k*(1-xg))/(k*math.sin(k))

def D12(k, b1, b2, al, be):
    return (k*math.sin(k) + 2*b1*math.sin(k*al)*math.sin(k*(1-al))
            + 2*b2*math.sin(k*be)*math.sin(k*(1-be))
            + (4*b1*b2/k)*math.sin(k*al)*math.sin(k*(be-al))*math.sin(k*(1-be)))

def roots(b1, b2, al, be, kmax=240.0, step=0.002):
    out = []; x0 = 1e-3; f0 = D12(x0, b1, b2, al, be); x = x0+step
    while x <= kmax:
        f1 = D12(x, b1, b2, al, be)
        if f0*f1 < 0:
            a, fa, bb = x0, f0, x
            for _ in range(80):
                m = .5*(a+bb); fm = D12(m, b1, b2, al, be)
                if fa*fm <= 0: bb = m
                else: a, fa = m, fm
            out.append(.5*(a+bb))
        x0, f0 = x, f1; x += step
    return [r for i, r in enumerate(out) if i == 0 or abs(r-out[i-1]) > 1e-4]

def Itheta(k, th):
    return (2/(k*k*math.sin(k)))*(math.sin(k*(1-th))*(1-math.cos(k*th))
                                  + math.sin(k*th)*(1-math.cos(k*(1-th))))

def Aq(p, q, k): return (q-p)/2 - (math.sin(2*k*q)-math.sin(2*k*p))/(4*k)
def Bq(p, q, k): return (math.sin(k*(1-2*p))-math.sin(k*(1-2*q)))/(4*k) - (q-p)/2*math.cos(k)

def Cab(k, ta, tb):
    if ta > tb: ta, tb = tb, ta
    pref = (2/(k*math.sin(k)))**2
    return pref*(math.sin(k*(1-ta))*math.sin(k*(1-tb))*Aq(0, ta, k)
                 + math.sin(k*ta)*math.sin(k*(1-tb))*Bq(ta, tb, k)
                 + math.sin(k*ta)*math.sin(k*tb)*Aq(0, 1-tb, k))

def amps(b1, b2, al, be, xi):
    """return arrays mu_j, G_j over affected roots (Pro's rank-2 recipe)."""
    ks = roots(b1, b2, al, be)
    th = [al, be]; B = [b1, b2]
    mus, Gs = [], []
    for k in ks:
        # W(k) 2x2, M = I + W B ; null vector c
        W = [[r0(k, th[a], th[b]) for b in range(2)] for a in range(2)]
        M = [[(1 if a==b else 0) + W[a][b]*B[b] for b in range(2)] for a in range(2)]
        # null vector of singular 2x2: (M01, -M00) (fallback (-M11,M10))
        c = (M[0][1], -M[0][0])
        if abs(c[0])+abs(c[1]) < 1e-9: c = (-M[1][1], M[1][0])
        d = [B[0]*c[0], B[1]*c[1]]
        psi_xi = -(d[0]*r0(k, xi, th[0]) + d[1]*r0(k, xi, th[1]))
        integ = -(d[0]*Itheta(k, th[0]) + d[1]*Itheta(k, th[1]))
        norm = sum(d[a]*d[b]*Cab(k, th[a], th[b]) for a in range(2) for b in range(2))
        mu = k*k/2
        if abs(norm) < 1e-300: continue
        mus.append(mu); Gs.append(mu*psi_xi*integ/norm)
    return np.array(mus), np.array(Gs)

def Sn(mu, G, tau, n):
    return float(np.sum(G*(mu**n)*np.exp(-mu*tau)))

def main():
    al, be, b1, b2, tau, xi = 0.38, 0.489580512568, 1.35, 1.08389352452, 0.00123657668735, 0.463
    say("="*72)
    say("Independent verification of Pro's two-shortcut CUSP")
    say(f"(alpha,beta,b1,b2,tau_c)=({al},{be},{b1},{b2},{tau})  xi={xi}")
    say("="*72)
    mu, G = amps(b1, b2, al, be, xi)
    Phi = Sn(mu, G, tau, 0)
    S1, S2, S3, S4 = (Sn(mu, G, tau, n) for n in (1, 2, 3, 4))
    say(f"\n#modes={len(mu)}, Phi(tau_c)={Phi:.6f}")
    say(f" normalized cusp residuals (should be ~0 for S1,S2,S3; S4 nonzero):")
    say(f"   tau*S1/Phi   = {tau*S1/Phi:.3e}   (Pro: 7.3e-12)")
    say(f"   tau^2*S2/Phi = {tau**2*S2/Phi:.3e}   (Pro: 4.4e-11)")
    say(f"   tau^3*S3/Phi = {tau**3*S3/Phi:.3e}   (Pro: 6.8e-11)")
    say(f"   tau^4*S4/Phi = {tau**4*S4/Phi:.4f}    (Pro: -1.672, must be != 0)")
    say("\n first roots/amplitudes vs Pro's table:")
    say(f"   {'k_j':>10} {'mu_j':>12} {'G_j':>12}  (Pro k_j: 4.17334,6.49307,9.71020,...)")
    for i in range(min(6, len(mu))):
        say(f"   {math.sqrt(2*mu[i]):>10.5f} {mu[i]:>12.5f} {G[i]:>12.5f}")
    # unfolding determinant via finite diff in b1,b2 at fixed tau
    h = 1e-5
    def s12(bb1, bb2):
        m, g = amps(bb1, bb2, al, be, xi); return Sn(m, g, tau, 1), Sn(m, g, tau, 2)
    s1p1, s2p1 = s12(b1+h, b2); s1m1, s2m1 = s12(b1-h, b2)
    s1p2, s2p2 = s12(b1, b2+h); s1m2, s2m2 = s12(b1, b2-h)
    J = np.array([[(s1p1-s1m1)/(2*h), (s1p2-s1m2)/(2*h)],
                  [(s2p1-s2m1)/(2*h), (s2p2-s2m2)/(2*h)]])
    det = float(np.linalg.det(J))
    say(f"\n unfolding det d(S1,S2)/d(b1,b2) = {det:.4e}  (must be != 0; Pro raw ~ -6.9e7)")
    ok = (abs(tau*S1/Phi) < 1e-6 and abs(tau**2*S2/Phi) < 1e-6 and abs(tau**3*S3/Phi) < 1e-6
          and abs(tau**4*S4/Phi) > 1e-2 and abs(det) > 1e2)
    say(f"\n VERDICT: cusp {'CONFIRMED' if ok else 'NOT confirmed'} "
        f"(S1=S2=S3=0, S4!=0, unfolding det!=0).")
    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_cusp_verify.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(OUT) + "\n")
    say(f"wrote {p}")

if __name__ == "__main__":
    main()
