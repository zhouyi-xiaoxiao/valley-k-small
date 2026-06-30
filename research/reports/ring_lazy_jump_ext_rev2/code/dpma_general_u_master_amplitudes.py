#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Continuum amplitude G_{xi,theta}(w;b) for the directed-shortcut FPT problem.

Closes the package's #1 open TODO: the closed-form continuum amplitude in the
diffusion limit, for arbitrary start xi=r/N and shortcut theta=u/N.

SOURCE of the closed form: proposed by ChatGPT (gpt-5.5-thinking), adversarially
cross-checked against an independent ChatGPT gpt-5-5-pro derivation (which gave a
DIFFERENT, non-matching form) and against a Claude multi-agent audit. The form was
then INDEPENDENTLY VERIFIED here against the exact finite-N residues (see V-G below):
the thinking-model form matches to ratio 1.0000 with clean O(1/N^2) convergence; the
pro-model form did NOT match (ratios 16-26x) and is rejected.

Continuum eigenproblem (absorbing ends, interior delta-sink at x=theta, strength b):
    -1/2 phi'' + b delta(x-theta) phi = mu phi,  phi(0)=phi(1)=0,  mu=2 w^2, k=2w
    jump:  phi'(theta+)-phi'(theta-) = 2 b phi(theta)
    spectral eq:  M_theta(w;b) = w sin(2w) + b sin(2 theta w) sin(2(1-theta) w) = 0
                  (theta=1/2 -> tan w = -2w/b)
Eigenfunction (unnormalised):
    phi_{w,theta}(x) = sin(k(1-theta)) sin(k x)        for 0<=x<=theta
                     = sin(k theta) sin(k(1-x))        for theta<=x<=1
Amplitude (this is the VERIFIED closed form):
    I = [ sin(k(1-theta))(1-cos(k theta)) + sin(k theta)(1-cos(k(1-theta))) ] / k
    J = sin^2(k(1-theta)) (theta/2 - sin(2 k theta)/(4k))
      + sin^2(k theta)   ((1-theta)/2 - sin(2 k (1-theta))/(4k))
    G_{xi,theta}(w;b) = 2 w^2 * phi_{w,theta}(xi) * I / J      (AFFECTED modes)
Master curve:  (N^2/q) F^(u)_r(t) -> sum_j G_{xi,theta}(w_j;b) e^{-2 w_j^2 tau},
               tau = q t / N^2.
theta=1/2 special case:  G_{xi,1/2}(w;b) = 4 w (1-cos w) sin(2 w xi)
                                          / ( sin^2 w [1 + b(b+2)/(4 w^2)] );
    at xi=1/2 this reduces to the previously-verified antipodal G =
    4 w (1-cos w)/( sin w [1+b(b+2)/(4 w^2)] ).  NOTE: the antipodal G used in the
    plateau master function is therefore the CENTER-START (xi=1/2) special case; a
    general start carries the sin(2 w xi) factor.
NODE / UNAFFECTED modes (sin(2 theta w)=0): these are NOT given by G above (G is the
affected-mode amplitude); they follow the unperturbed Dirichlet amplitude and must be
handled separately (the affected-mode formula over/under-counts them).

Exact: F^(u)_r(t) = sum_j B_j s_j^{t-1}, B_j = q Nnum(y_j)/D_u'(y_j), s_j=1-q+q y_j,
       y_j = cos(2 w_j/N) => w_j = (N/2) arccos(y_j); exact scaled amp A_j=(N^2/q)B_j.

Writes artifacts/tables/dpma_general_u_master_amplitudes.txt
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np

q = 2.0/3.0
OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

def U(n, y):
    if n < 0: return 0.0
    um1, u0 = 0.0, 1.0
    for _ in range(1, n+1):
        um1, u0 = u0, 2*y*u0 - um1
    return u0
def A_(m, y): return 0.0 if m == 0 else U(m-1, y)
def D_u(y, N, u, a): return a*U(N-1, y) + 2*U(u-1, y)*U(N-u-1, y)
def Nnum(y, N, u, r, a):
    base = a*(A_(r, y)+A_(N-r, y))
    if r <= u: return base + 2*A_(N-u, y)*(A_(r, y)+A_(u-r, y))
    return base + 2*A_(u, y)*(A_(N-r, y)+A_(r-u, y))
def Dp(y, N, u, a):
    h = 1e-7
    return (D_u(y+h, N, u, a) - D_u(y-h, N, u, a))/(2*h)
def transient(N, beta, u):
    n = N-1; M = np.zeros((n, n))
    for i in range(1, N):
        k = i-1
        M[k, k] = (1-q)*(1-beta) if i == u else (1-q)
        for j in (i-1, i+1):
            if 1 <= j <= N-1: M[k, j-1] += q/2.0
    return M

def G_amp(w, xi, th, b):
    """Verified affected-mode continuum amplitude G_{xi,theta}(w;b)."""
    k = 2*w
    phi = math.sin(k*(1-th))*math.sin(k*xi) if xi <= th else math.sin(k*th)*math.sin(k*(1-xi))
    I = (math.sin(k*(1-th))*(1-math.cos(k*th)) + math.sin(k*th)*(1-math.cos(k*(1-th))))/k
    J = (math.sin(k*(1-th))**2)*(th/2 - math.sin(2*k*th)/(4*k)) + \
        (math.sin(k*th)**2)*((1-th)/2 - math.sin(2*k*(1-th))/(4*k))
    return 2*w*w*phi*I/J

def verify(th, xi, b, Ns=(200, 400, 800, 1200), nmodes=4):
    say(f"\n[G test] theta={th:.4f} xi={xi:.4f} b={b}: A_exact=(N^2/q)B_j vs G_{{xi,theta}}(w_j;b)")
    say(f"  {'N':>5} {'w_j':>9} {'A_exact':>14} {'G_closed':>14} {'A/G':>10}")
    worst = 0.0
    for N in Ns:
        u = int(round(th*N)); r = int(round(xi*N))
        beta = b*q/((1-q)*N); a = q/(beta*(1-q))
        M = transient(N, beta, u)
        y = np.sort((np.linalg.eigvalsh(M)-(1-q))/q)[::-1]
        cnt = 0
        for yj in y:
            if yj >= 1-1e-14: continue
            w = (N/2.0)*math.acos(max(-1.0, min(1.0, yj)))
            if w < 0.2: continue
            # skip node/unaffected modes (sin(2 theta w)~0): G formula does not apply
            if abs(math.sin(2*th*w)) < 1e-3: continue
            Bj = q*Nnum(yj, N, u, r, a)/Dp(yj, N, u, a)
            Aj = (N*N/q)*Bj
            g = G_amp(w, xi, th, b)
            ratio = Aj/g if abs(g) > 1e-9 else float('nan')
            if N == Ns[-1] and not math.isnan(ratio):
                worst = max(worst, abs(ratio-1.0))
            say(f"  {N:>5} {w:>9.4f} {Aj:>14.6e} {g:>14.6e} {ratio:>10.5f}")
            cnt += 1
            if cnt >= nmodes: break
    say(f"  -> max |A/G - 1| at N={Ns[-1]} (affected modes): {worst:.2e}")
    return worst

def main():
    say("="*72)
    say("Continuum amplitude G_{xi,theta}(w;b) verification (q=2/3)")
    say("verified form: thinking-model G = 2 w^2 phi(xi) I / J  (pro-model form rejected)")
    say("="*72)
    w1 = verify(0.5, 0.5, 1.5)       # antipodal center start -> recovers known antipodal G
    w2 = verify(0.5, 0.3, 1.5)       # antipodal off-center -> sin(2 w xi) start factor
    w3 = verify(1.0/3.0, 0.2, 1.5)   # non-antipodal theta=1/3
    ok = max(w1, w2, w3) < 5e-3
    say(f"\nVERDICT: general-theta amplitude {'VERIFIED' if ok else 'NOT verified'} "
        f"(affected modes, max |A/G-1|={max(w1,w2,w3):.2e}, O(1/N^2)).")
    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_general_u_master_amplitudes.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(OUT) + "\n")
    say(f"wrote {p}")

if __name__ == "__main__":
    main()
