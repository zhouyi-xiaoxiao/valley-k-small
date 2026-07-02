#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""FULL general-theta master CURVE: affected-mode + NODE-mode amplitudes together.

Closes the gap found by the 2026-06-30 triangulated PRR audit: the affected-only
amplitude G_{xi,theta}=2w^2 phi I/J (dpma_general_u_master_amplitudes.py) SKIPS the
node/unaffected modes (sin(2 theta w)=0), which carry a large low-frequency share
(~33% at theta=1/3) and dominate the early/intermediate-tau morphology. Without them
the master CURVE cannot be assembled. Here we add the node-mode amplitude and verify
the FULL curve reproduces the exact (N^2/q) F^(u)_r(t).

Node modes: the delta-sink sits on a node of an unperturbed Dirichlet mode sin(n pi x)
(sin(n pi theta)=0, i.e. n theta integer), w_n = n pi/2, mu_n = 2 w_n^2 = n^2 pi^2/2.
Unperturbed Dirichlet FPT residue (same 2w^2 phi(xi) I/J with the unperturbed
eigenfunction sin(n pi x): I=[1-(-1)^n]/(n pi), J=1/2):
    G_node(n; xi) = n pi [1 - (-1)^n] sin(n pi xi)     (even n vanish; odd n contribute)

Master curve:  (N^2/q) F^(u)_r(t) -> sum_j G_j e^{-2 w_j^2 tau},  tau = q t / N^2,
  G_j = G_affected(w_j;xi,theta,b)  if sin(2 theta w_j) != 0,  else  G_node(n_j; xi).

Test: per-mode A_j=(N^2/q)B_j vs closed form (affected AND node), and the full-curve
reconstruction vs exact (N^2/q)F across tau in [0.01,0.2], error -> 0 as N grows.
Writes artifacts/tables/dpma_general_u_master_curve.txt
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np

q = 2.0/3.0
OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

def transient_and_absorb(N, beta, u):
    n = N-1; M = np.zeros((n, n)); b_abs = np.zeros(n)
    lam = beta*(1-q)
    for i in range(1, N):
        k = i-1
        M[k, k] = (1-q)*(1-beta) if i == u else (1-q)
        if i == u: b_abs[k] += lam
        for j in (i-1, i+1):
            if j % N == 0: b_abs[k] += q/2.0
            elif 1 <= j <= N-1: M[k, (j % N)-1] += q/2.0
    return M, b_abs

def G_affected(w, xi, th, b):
    k = 2*w
    phi = math.sin(k*(1-th))*math.sin(k*xi) if xi <= th else math.sin(k*th)*math.sin(k*(1-xi))
    I = (math.sin(k*(1-th))*(1-math.cos(k*th)) + math.sin(k*th)*(1-math.cos(k*(1-th))))/k
    J = (math.sin(k*(1-th))**2)*(th/2 - math.sin(2*k*th)/(4*k)) + \
        (math.sin(k*th)**2)*((1-th)/2 - math.sin(2*k*(1-th))/(4*k))
    return 2*w*w*phi*I/J

def G_node(n, xi):
    return n*math.pi*(1-(-1)**n)*math.sin(n*math.pi*xi)

def modes(N, beta, u, r):
    M, b_abs = transient_and_absorb(N, beta, u)
    s, V = np.linalg.eigh(M)
    er = np.zeros(N-1); er[r-1] = 1.0
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        B = (er @ V) * (V.T @ b_abs)
    order = np.argsort(s)[::-1]
    return s[order], B[order]

def run(th, xi, b, Ns=(400, 800, 1200)):
    say(f"\n=== theta={th} xi={xi} b={b} ===")
    taus = [0.01, 0.03, 0.05, 0.1, 0.2]
    allerrs = {}
    for N in Ns:
        u = int(round(th*N)); r = int(round(xi*N))
        beta = b*q/((1-q)*N)
        s, B = modes(N, beta, u, r)
        # build closed-form per-mode amplitudes for low modes
        node_err = 0.0; aff_err = 0.0; n_node = 0; n_aff = 0
        Gcl = np.zeros(len(s)); W = np.zeros(len(s))
        for j, sj in enumerate(s):
            yj = (sj-(1-q))/q
            if yj >= 1-1e-14 or yj <= -1+1e-14:
                W[j] = float('nan'); continue
            w = (N/2.0)*math.acos(max(-1.0, min(1.0, yj))); W[j] = w
            Aj = (N*N/q)*B[j]
            if abs(math.sin(2*th*w)) < 5e-3:           # node / unaffected
                nn = int(round(2*w/math.pi))
                g = G_node(nn, xi)
                if w < 15 and nn % 2 == 1 and abs(g) > 1e-6:   # low, contributing node modes
                    node_err = max(node_err, abs(Aj-g)/abs(g)); n_node += 1
                Gcl[j] = g
            else:                                       # affected
                g = G_affected(w, xi, th, b)
                if w < 25 and abs(Aj) > 1e-6:
                    aff_err = max(aff_err, abs(Aj-g)/abs(g)); n_aff += 1
                Gcl[j] = g
        # full-curve reconstruction vs exact, across tau
        errs = []
        for tau in taus:
            t = tau*N*N/q
            exact = (N*N/q)*float(np.sum(B*np.exp((t-1)*np.log(np.clip(s, 1e-300, None)))))
            mask = np.isfinite(W)
            curve = float(np.sum(Gcl[mask]*np.exp(-2*W[mask]**2*tau)))
            rel = abs(curve-exact)/max(1e-12, abs(exact))
            errs.append(rel)
        say(f"  N={N}: per-mode max|A/G-1| affected={aff_err:.2e}({n_aff}) node={node_err:.2e}({n_node}); "
            f"FULL-curve rel-err @tau{taus} = " + ", ".join(f"{e:.1e}" for e in errs))
        allerrs[N] = errs
    return allerrs

def main():
    say("="*78)
    say("FULL general-theta master curve (affected + node modes), q=2/3")
    say("="*78)
    e1 = run(1.0/3.0, 0.2, 1.5)
    e2 = run(2.0/5.0, 0.3, 1.5)
    e3 = run(0.5, 0.3, 1.5)
    Ns = sorted(e3.keys())
    worst = max(e[Ns[-1]][0] for e in (e1, e2, e3))  # hardest point (early tau, largest N)
    # empirical convergence exponent p (rel-err ~ N^-p) from successive-N log-ratios at fixed tau
    rates = []
    for e in (e1, e2, e3):
        for a, b in zip(Ns[:-1], Ns[1:]):
            for ea, eb in zip(e[a], e[b]):
                if ea > 1e-12 and eb > 1e-12:
                    rates.append(math.log(ea/eb) / math.log(b/a))
    p_med = float(np.median(rates))
    say(f"\nVERDICT: full master curve {'LANDS' if worst < 0.05 else 'does NOT yet land'} "
        f"(worst early-tau rel-err at largest N ~ {worst:.1e}; measured convergence "
        f"rel-err ~ N^(-{p_med:.2f}), median over cases/taus/N-pairs).")
    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_general_u_master_curve.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(OUT) + "\n")
    say(f"wrote {p}")

if __name__ == "__main__":
    main()
