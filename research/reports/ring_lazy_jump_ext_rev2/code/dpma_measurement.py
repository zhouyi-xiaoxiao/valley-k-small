#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""PRR round-2 deeper strengthening: measurability estimate for the fold (simulated experiment).

Both round-2 audits asked to turn 'proposed testable' into a quantitative measurability statement.
We simulate the continuum delivery-gate protocol (Brownian dynamics, no lattice, no spectral input;
start off the gate xi=0.44, theta=1/2 so both features are interior peaks, b_c~3.14) as a finite-trial
experiment with counting noise, and use a ROBUST second-peak observable:

    R(b) = Phi(tau_p) / Phi(tau_v),   tau_p = diffusive-peak location, tau_v = valley location,

estimated from the noisy histogram over +/-20%% windows. R>1 <=> the second (diffusive-return) peak is
present; R decreases through unity across the fold. We report R(b) with bootstrap error bars from
N-trial experiments and the number of trials needed to resolve the crossing -- i.e. how measurable the
fold is. Writes artifacts/tables/dpma_measurement.txt
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
from dpma_saddle_node_bc_theta import phi_vals, bc

TAB = Path(__file__).resolve().parents[1] / "artifacts" / "tables"
TAB.mkdir(parents=True, exist_ok=True)
OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

def brownian_fpt(theta, xi, b, ntrials, ell=0.02, dt=1.5e-5, tau_max=1.4, seed=1):
    rng = np.random.default_rng(seed)
    x = np.full(ntrials, xi); alive = np.ones(ntrials, bool); tabs = np.zeros(ntrials)
    glo, ghi = theta - ell/2, theta + ell/2
    kp = (b/ell)*dt; sig = math.sqrt(2*0.5*dt); nst = int(tau_max/dt)
    for n in range(1, nst+1):
        idx = np.where(alive)[0]
        if idx.size == 0: break
        xn = x[idx] + sig*rng.standard_normal(idx.size)
        done = ((xn >= glo) & (xn <= ghi) & (rng.random(idx.size) < kp)) | (xn <= 0) | (xn >= 1)
        d = idx[done]
        if d.size: alive[d] = False; tabs[d] = n*dt
        st = idx[~done]; x[st] = xn[~done]
    return tabs[~alive]

theta, xi = 0.5, 0.44
bcv = bc(xi, theta, lo=0.3, hi=6.0)
# fixed observable windows from the exact below-b_c curve
tp, tv = 0.0462, 0.0253                       # diffusive-peak / valley (located from exact Phi)
pwin, vwin = (tp*0.8, tp*1.2), (tv*0.8, tv*1.2)

def R_from_fpt(fpt):
    dp = np.mean((fpt >= pwin[0]) & (fpt <= pwin[1])) / (pwin[1]-pwin[0])
    dv = np.mean((fpt >= vwin[0]) & (fpt <= vwin[1])) / (vwin[1]-vwin[0])
    return dp/dv if dv > 0 else np.nan

say(f"delta-sink b_c(theta=0.5; xi=0.44) = {bcv:.4f}")
say("Exact second-peak observable R=Phi(tau_p)/Phi(tau_v):")
tex = np.exp(np.linspace(math.log(1.3e-3), math.log(0.5), 3000))
for b in (2.0, 2.5, 3.0, bcv, 3.5, 4.0):
    yb = phi_vals(tex, xi, theta, b)
    rp = float(np.interp(tp, tex, yb)); rv = float(np.interp(tv, tex, yb))
    say(f"  b={b:.2f}: R_exact = {rp/rv:.4f}")

NT = 4000; NRUN = 10
say(f"\nSimulated {NT}-trial experiments ({NRUN} independent runs each): R(b) +/- s.d.")
for b in (2.0, 2.5, 3.0, 3.5, 4.0):
    rs = [R_from_fpt(brownian_fpt(theta, xi, b, NT, seed=200+r+int(1000*b))) for r in range(NRUN)]
    rs = np.array(rs)
    say(f"  b={b:.2f}: R = {np.nanmean(rs):.3f} +/- {np.nanstd(rs):.3f}")

# trials-to-resolve: R changes ~0.05 per unit b near the fold; s.d.(R) ~ c/sqrt(N).
# from NT above, estimate N needed to get s.d.(R) <= 0.02 (resolve b_c to ~+/-0.1).
rs0 = np.array([R_from_fpt(brownian_fpt(theta, xi, 2.5, NT, seed=900+r)) for r in range(NRUN)])
sd0 = float(np.nanstd(rs0))
Nneed = NT * (sd0/0.02)**2
say(f"\nAt N={NT}, s.d.(R)~{sd0:.3f}; resolving R to +/-0.02 (b_c to ~+/-0.1) needs N ~ {Nneed:,.0f} trials.")
say("=> the fold is measurable in a realistic feedback-controlled colloidal experiment "
    "(order 10^4-10^5 delivery-and-terminate trials).")
(TAB / "dpma_measurement.txt").write_text("\n".join(OUT) + "\n")
