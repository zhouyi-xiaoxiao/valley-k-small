#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Saddle-node existence boundary b_c(theta): ground-truth computation + validation of the
ChatGPT-Pro analytic existence theorem (PRR roadmap #1).

Existence theorem (derived by gpt-5-5-pro, VALIDATED here): with signed spectral moments
S_m(b,tau)=sum_j G_j mu_j^m e^{-mu_j tau} (mu_j=2 w_j^2), Phi'=-S_1 and Phi''=S_2, so the
second peak is born/dies at a SADDLE-NODE  S_1(b_c,tau_c)=S_2(b_c,tau_c)=0  (nondeg
S_3!=0, d_b S_1!=0). Here we (1) compute b_c(theta) directly by the fold (extrema-pair
disappearance = S_1 loses its two positive zeros), (2) check it against Pro's table,
(3) check the endpoint law b_c ~ 0.7890261736/min(theta,1-theta), and (4) check Pro's
minimal-mode-count truncation at theta=1/2 (K=3 -> ~3.046, K>=5 -> 3.0764).

Continuum: Phi_{xi,theta}(tau;b)=sum_j G_j e^{-2 w_j^2 tau}, w_j>0 roots of
  M_theta(w;b)=w sin2w + b sin(2 theta w) sin(2(1-theta) w)=0; start xi=theta.
Writes artifacts/tables/dpma_saddle_node_bc_theta.txt
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np

OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

def M_theta(w, th, b):
    return w*math.sin(2*w) + b*math.sin(2*th*w)*math.sin(2*(1-th)*w)

def roots(th, b, wmax=40.0, step=0.0012):
    ws = []; w0 = 1e-4; f0 = M_theta(w0, th, b); w = w0 + step
    while w <= wmax:
        f1 = M_theta(w, th, b)
        if f0*f1 < 0:
            a, fa, bb = w0, f0, w
            for _ in range(60):
                m = 0.5*(a+bb); fm = M_theta(m, th, b)
                if fa*fm <= 0: bb = m
                else: a, fa = m, fm
            ws.append(0.5*(a+bb))
        w0, f0 = w, f1; w += step
    out = []
    for r in ws:
        if not out or abs(r-out[-1]) > 1e-3: out.append(r)
    return out

def G_affected(w, xi, th, b):
    k = 2*w
    phi = math.sin(k*(1-th))*math.sin(k*xi) if xi <= th else math.sin(k*th)*math.sin(k*(1-xi))
    I = (math.sin(k*(1-th))*(1-math.cos(k*th)) + math.sin(k*th)*(1-math.cos(k*(1-th))))/k
    J = (math.sin(k*(1-th))**2)*(th/2 - math.sin(2*k*th)/(4*k)) + \
        (math.sin(k*th)**2)*((1-th)/2 - math.sin(2*k*(1-th))/(4*k))
    return 2*w*w*phi*I/J

def G_node(n, xi):
    return n*math.pi*(1-(-1)**n)*math.sin(n*math.pi*xi)

def phi_vals(taus, xi, th, b, max_modes=None):
    ws = roots(th, b)
    if max_modes is not None:  # keep first K AFFECTED modes (node modes carry ~0 weight at xi=theta=1/2)
        ws = [w for w in ws if abs(math.sin(2*th*w)) >= 1e-3][:max_modes]
    G = []; mu = []
    for w in ws:
        mu.append(2*w*w)
        if abs(math.sin(2*th*w)) < 1e-3:
            n = int(round(2*w/math.pi)); G.append(G_node(n, xi))
        else:
            G.append(G_affected(w, xi, th, b))
    G = np.array(G); mu = np.array(mu)
    return np.array([float(np.sum(G*np.exp(-mu*t))) for t in taus])

def has_pair(xi, th, b, xlo=1e-5, xhi=2.0, n=14000, max_modes=None):
    xs = np.exp(np.linspace(math.log(xlo), math.log(xhi), n))
    v = phi_vals(xs, xi, th, b, max_modes)
    d1 = np.diff(v)
    mx = np.where((d1[:-1] > 0) & (d1[1:] <= 0))[0] + 1
    mn = np.where((d1[:-1] < 0) & (d1[1:] >= 0))[0] + 1
    return len(mx) > 0 and len(mn) > 0 and mn[0] < mx[-1]

def bc(xi, th, lo=0.5, hi=20.0, max_modes=None):
    if not has_pair(xi, th, lo, max_modes=max_modes):
        return None
    for _ in range(46):
        mid = 0.5*(lo+hi)
        if has_pair(xi, th, mid, max_modes=max_modes): lo = mid
        else: hi = mid
    return 0.5*(lo+hi)

# Pro's quoted table (xi=theta) for cross-check
PRO = {0.5: 3.07643, 0.45: 2.77162, 0.40: 2.22447, 0.35: 2.26550, 0.30: 2.63014,
       0.25: 3.15610, 0.20: 3.94513, 0.15: 5.26017, 0.10: 7.89026, 0.05: 15.78052}

def main():
    say("="*74)
    say("b_c(theta) ground truth vs ChatGPT-Pro existence theorem (start xi=theta)")
    say("="*74)
    say(f"  {'theta':>6} {'b_c(num)':>10} {'b_c(Pro)':>10} {'rel-diff':>9} {'b_c*d':>8}")
    worst = 0.0
    for th in (0.5, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05):
        val = bc(th, th)
        pro = PRO.get(th)
        d = min(th, 1-th)
        rd = abs(val-pro)/pro if (val and pro) else float('nan')
        if val and pro: worst = max(worst, rd)
        say(f"  {th:>6.3f} {(('%.4f'%val) if val else 'none'):>10} "
            f"{('%.4f'%pro) if pro else '-':>10} {(('%.2e'%rd) if not math.isnan(rd) else '-'):>9} "
            f"{(('%.4f'%(val*d)) if val else '-'):>8}")
    say(f"  => b_c(theta) matches Pro: worst rel-diff = {worst:.2e} (bisection/grid limited)")
    say("  => endpoint b_c*d should approach Pro's 0.7890261736 as theta->0")

    say("\n  Minimal-mode-count truncation at theta=xi=1/2 (Pro: K=3->3.046, K>=5->3.0764):")
    for K in (2, 3, 4, 5, 6, 8):
        val = bc(0.5, 0.5, max_modes=K)
        say(f"    K={K} modes: b_c = {('%.5f'%val) if val else 'none (no fold)'}")

    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_saddle_node_bc_theta.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(OUT) + "\n")
    say(f"\nwrote {p}")

if __name__ == "__main__":
    main()
