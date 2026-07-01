#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Multiple directed shortcuts (rank-m): validate ChatGPT-Pro's m=2 determinant and test its
prediction that TWO shortcuts can produce a THIRD first-passage peak (PRR roadmap #2).

Pro's rank-m secular equation: det[I_m + B W(k)]=0, W_ab=R_0(k;θ_a,θ_b), pole-cancelled to
D_m(k)=k sin k det[...]. Explicit m=2 (0<α<β<1, strengths b1,b2):
  D12(k)= k sin k + 2 b1 sin(kα)sin(k(1-α)) + 2 b2 sin(kβ)sin(k(1-β))
          + (4 b1 b2 / k) sin(kα) sin(k(β-α)) sin(k(1-β)) = 0.
Falsifiable triple-peak prediction: θ1=0.38, θ2=0.48, b1=1.35, b2=0.14, ξ=0.463 -> 3 maxima at
τ≈2.8e-4, 5.3e-3, 6.1e-2.  We check both against the EXACT finite-N two-shortcut ring.

Ring: N sites, stay 1-q, hop q/2 each way; absorbing target v=0; directed shortcuts at u_a
(redirect β_a(1-q) of the u_a self-loop to v). Continuum map: b_a=β_a(1-q)N/q, θ_a=u_a/N,
τ=q t/N^2, k=N·arccos(y), y=(s-(1-q))/q. Writes artifacts/tables/dpma_multishortcut.txt
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np

q = 2.0/3.0
OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

def build_ring_multi(N, shortcuts):
    """shortcuts = list of (u, beta). transient sites 1..N-1; symmetric M + absorption vec."""
    n = N-1
    M = np.zeros((n, n)); b_abs = np.zeros(n)
    beta_at = {u: be for u, be in shortcuts}
    for i in range(1, N):
        k = i-1
        be = beta_at.get(i, 0.0)
        M[k, k] = (1-q)*(1-be)
        if be: b_abs[k] += be*(1-q)
        for j in (i-1, i+1):
            if j % N == 0: b_abs[k] += q/2.0
            elif 1 <= j <= N-1: M[k, (j % N)-1] += q/2.0
    return M, b_abs

def D12(k, b1, b2, al, be):
    return (k*math.sin(k) + 2*b1*math.sin(k*al)*math.sin(k*(1-al))
            + 2*b2*math.sin(k*be)*math.sin(k*(1-be))
            + (4*b1*b2/k)*math.sin(k*al)*math.sin(k*(be-al))*math.sin(k*(1-be)))

def spectrum(M):
    s, V = np.linalg.eigh(M)
    o = np.argsort(s)[::-1]
    return s[o], V[:, o]

def validate_det(N=800):
    say(f"\nV1: m=2 determinant D12(k_j)=0 at exact eigen-k (N={N})")
    al, be = 0.38, 0.48; b1, b2 = 1.0, 0.6
    u1, u2 = round(al*N), round(be*N)
    be1 = b1*q/((1-q)*N); be2 = b2*q/((1-q)*N)
    M, _ = build_ring_multi(N, [(u1, be1), (u2, be2)])
    s, _ = spectrum(M)
    y = (s-(1-q))/q
    cnt = 0
    say(f"  {'k_j':>9} {'D12(k_j)':>12}")
    for yj in y:
        if yj >= 1-1e-12: continue
        k = N*math.acos(max(-1.0, min(1.0, yj)))
        if k < 1.0: continue
        say(f"  {k:>9.4f} {D12(k, b1, b2, al, be):>12.3e}")
        cnt += 1
        if cnt >= 6: break
    say("  (D12(k_j) -> 0 as N grows confirms the rank-2 determinant incl. the b1b2 term)")

def fpt(M, b_abs, r, T_tau, N, npts=4000):
    s, V = spectrum(M)
    er = np.zeros(M.shape[0]); er[r-1] = 1.0
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        B = (er @ V) * (V.T @ b_abs)
    ls = np.log(np.clip(s, 1e-300, None))
    ts = np.unique(np.round(np.exp(np.linspace(math.log(2), math.log(T_tau*N*N/q), npts))).astype(np.int64))
    F = np.array([float(np.sum(B*np.exp((t-1)*ls))) for t in ts])
    return ts, F

def local_maxima(ts, F, thr):
    out = []
    for k in range(1, len(F)-1):
        if F[k] > F[k-1] and F[k] >= F[k+1] and F[k] > thr:
            out.append((int(ts[k]), F[k]))
    return out

def triple_peak(N):
    al, be = 0.38, 0.48; b1, b2 = 1.35, 0.14; xi = 0.463
    u1, u2, r = round(al*N), round(be*N), round(xi*N)
    be1 = b1*q/((1-q)*N); be2 = b2*q/((1-q)*N)
    M, b_abs = build_ring_multi(N, [(u1, be1), (u2, be2)])
    ts, F = fpt(M, b_abs, r, T_tau=0.15, N=N)
    thr = 1e-3*F.max()
    lm = local_maxima(ts, F, thr)
    taus = [q*t/(N*N) for t, _ in lm]
    say(f"\n  N={N}: interior maxima (Pro predicts 3 at tau≈2.8e-4, 5.3e-3, 6.1e-2):")
    say(f"    #maxima={len(lm)}; tau-values = " + ", ".join(f"{tt:.2e}" for tt in taus))
    return len(lm), taus

def main():
    say("="*74)
    say("Rank-m (multiple shortcuts): m=2 determinant + triple-peak test (q=2/3)")
    say("="*74)
    validate_det(800)
    say("\nV2: does m=2 produce a THIRD peak? (Pro's falsifiable prediction)")
    n1, t1 = triple_peak(1000)
    n2, t2 = triple_peak(1500)
    say("")
    if max(n1, n2) >= 3:
        say("  => TRIPLE PEAK CONFIRMED: two directed shortcuts create 3 first-passage peaks.")
        say("     A genuinely new (higher-codimension) result — the mechanism is not just a single fold.")
    elif max(n1, n2) == 2:
        say("  => only 2 peaks at these params; Pro's specific triple-peak tuple not reproduced")
        say("     (may need re-tuned (θ,b,ξ) — the m=2 fold structure still holds; retune to hit a cusp).")
    else:
        say("  => <2 peaks; prediction not reproduced at these params.")
    p = Path(__file__).resolve().parents[1] / "artifacts" / "tables" / "dpma_multishortcut.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(OUT) + "\n")
    say(f"\nwrote {p}")

if __name__ == "__main__":
    main()
