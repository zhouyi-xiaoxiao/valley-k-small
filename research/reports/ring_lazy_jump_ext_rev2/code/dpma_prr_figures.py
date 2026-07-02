#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""PRR-grade figure suite for the directed-shortcut saddle-node (roadmap #4).

Six panels (all from the verified modules; NOTE: 'second peak'/'fold' are the certified
master-curve saddle-node quantities, not the C.2 classifier label):
  A: b_c(theta) saddle-node phase boundary (double-peak region), min@theta~0.381, endpoint 0.789/d
  B: master-curve morphology Phi(tau;b) at theta=1/2 across b straddling b_c (second peak dies)
  C: saddle-node normal-form scaling (gap ~ (b_c-b)^1/2, prominence ~ (b_c-b)^3/2)
  D: two-shortcut TRIPLE peak (exact ring, N=1500)
  E: 2D torus FPT density F(t) vs beta (capture + diffusive peaks)
  F: 2D diffusive-peak prominence vs beta (fold at beta_c^2D)
Writes artifacts/figures/dpma_prr_figures.{pdf,png} (panels a-c: the 1D fold result)
and artifacts/figures/dpma_prr_extensions.{pdf,png} (panels a-c: cusp/2D extensions)
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42   # TrueType, no Type 3 (APS/arXiv production)
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt

from dpma_saddle_node_bc_theta import phi_vals
from dpma_2d_finite_lattice import build_2d, fpt_curve
from dpma_multishortcut import build_ring_multi, fpt

q = 2.0/3.0

# ---- validated b_c(theta) table (rel-diff ~1e-6 vs numerics; symmetric) ----
BC = {0.05: 15.781, 0.10: 7.890, 0.15: 5.260, 0.20: 3.945, 0.25: 3.156,
      0.30: 2.630, 0.35: 2.266, 0.38: 2.165, 0.40: 2.224, 0.45: 2.772, 0.50: 3.076}

def interior_pair(xi, th, b, xlo=1e-4, xhi=1.5, n=8000):
    xs = np.exp(np.linspace(math.log(xlo), math.log(xhi), n))
    v = phi_vals(xs, xi, th, b)
    d1 = np.diff(v)
    mx = np.where((d1[:-1] > 0) & (d1[1:] <= 0))[0] + 1
    mn = np.where((d1[:-1] < 0) & (d1[1:] >= 0))[0] + 1
    if len(mx) and len(mn) and mn[0] < mx[-1]:
        return xs[mn[0]], xs[mx[-1]], v[mn[0]], v[mx[-1]]
    return None

def main():
    figA, axA = plt.subplots(1, 3, figsize=(15, 4.6))
    figB, axB = plt.subplots(1, 3, figsize=(15, 4.6))

    # -- A: b_c(theta) phase boundary --
    # solid points = bisection-located thresholds ONLY (theta in [0.2,0.5] + mirror); the
    # small-theta entries of BC are asymptote values and are NOT plotted as data points.
    th = sorted(t for t in BC if 0.2 <= t <= 0.5); bcv = [BC[t] for t in th]
    th_full = th + [1-t for t in reversed(th) if (1-t) not in th]
    bc_full = bcv + [BC[t] for t in reversed(th) if (1-t) not in th]
    order = np.argsort(th_full); th_full = np.array(th_full)[order]; bc_full = np.array(bc_full)[order]
    a = axA[0]
    a.plot(th_full, bc_full, 'o-', color='C0', label=r'$b_c(\theta)$ (numerically located)')
    a.fill_between(th_full, 0, bc_full, alpha=0.15, color='C0')
    tt = np.linspace(0.03, 0.30, 100)
    a.plot(tt, 0.7890/tt, '--', color='C3', label=r'endpoint $0.789/\min(\theta,1-\theta)$')
    a.plot(1-tt, 0.7890/tt, '--', color='C3')
    a.axvline(0.381, ls=':', color='gray'); a.text(0.381, 12, r'$\theta_{\min}\approx0.381$', rotation=90, va='top', fontsize=8)
    a.set_xlabel(r'sink position $\theta=u/N$'); a.set_ylabel(r'shortcut strength $b$')
    a.set_title('(a) saddle-node phase boundary $b_c(\\theta)$\n(finite-time interior peak exists for $0<b<b_c$)')
    a.text(0.5, 1.3, 'interior peak exists', ha='center', color='C0', fontsize=9)
    a.set_ylim(0, 16); a.legend(fontsize=8)

    # -- B: morphology Phi(tau;b) at theta=1/2 --
    a = axA[1]
    xs = np.exp(np.linspace(math.log(1e-3), math.log(0.3), 3000))
    for b, c in [(2.5, 'C0'), (3.0, 'C1'), (3.076, 'C2'), (3.3, 'C3')]:
        a.plot(xs, phi_vals(xs, 0.5, 0.5, b), color=c, label=f'b={b}')
    a.set_xscale('log'); a.set_xlabel(r'$\tau=qt/N^2$'); a.set_ylabel(r'$\Phi(\tau;b)$')
    a.set_title(r'(b) master curve $\theta=\xi=1/2$: second peak'+'\n'+r'annihilates at $b_c=3.0764$')
    a.legend(fontsize=8, loc='upper left')
    # inset: the fold region (valley+peak merging), invisible at full scale
    axins = a.inset_axes([0.40, 0.42, 0.57, 0.52])
    for b, c in [(2.5, 'C0'), (3.0, 'C1'), (3.076, 'C2'), (3.3, 'C3')]:
        axins.plot(xs, phi_vals(xs, 0.5, 0.5, b), color=c)
    rB = interior_pair(0.5, 0.5, 2.5)                          # widest fold: sets the zoom window
    tmn, tmx, vmn, vmx = rB
    axins.set_xlim(0.55*tmn, 1.7*tmx); axins.set_ylim(vmn-0.35, vmx+0.35)  # linear x: clean ticks
    axins.tick_params(labelsize=6)
    a.indicate_inset_zoom(axins, edgecolor='gray')

    # -- C: normal-form scaling --
    a = axA[2]
    bc0 = 3.0764323604
    bs = [3.00, 3.03, 3.05, 3.06, 3.065, 3.07, 3.073, 3.075]
    dd, gg, pp = [], [], []
    for b in bs:
        r = interior_pair(0.5, 0.5, b)
        if r:
            tmn, tmx, vmn, vmx = r
            dd.append(bc0-b); gg.append(tmx-tmn); pp.append(vmx-vmn)
    dd = np.array(dd); gg = np.array(gg); pp = np.array(pp)
    a.loglog(dd, gg, 'o', color='C0', label='gap $\\tau_+-\\tau_-$')
    a.loglog(dd, pp, 's', color='C1', label='prominence')
    # analytic normal-form prefactors (dpma_normal_form.py): 2*sqrt(2*S1b/S3), (4*sqrt2/3)*S1b^1.5/sqrt(S3)
    a.loglog(dd, 0.0247518*dd**0.5, '--', color='C0', label=r'$0.02475\,\delta^{1/2}$ (analytic)')
    a.loglog(dd, 0.357444*dd**1.5, '--', color='C1', label=r'$0.35744\,\delta^{3/2}$ (analytic)')
    a.set_xlabel(r'$b_c-b$'); a.set_ylabel('gap / prominence')
    a.set_title('(c) normal-form fold scaling\n($\\delta^{1/2}$, $\\delta^{3/2}$)')
    a.legend(fontsize=8)

    # -- D: two-shortcut triple peak --
    a = axB[0]
    N = 1500; b1, b2 = 1.35, 0.14
    u1, u2, rr = round(0.38*N), round(0.48*N), round(0.463*N)
    be1 = b1*q/((1-q)*N); be2 = b2*q/((1-q)*N)
    M, babs = build_ring_multi(N, [(u1, be1), (u2, be2)])
    ts, F = fpt(M, babs, rr, T_tau=0.12, N=N)
    taus = q*ts/(N*N)
    a.plot(taus, F, color='C4')
    a.set_xscale('log'); a.set_xlim(1e-5, 0.12); a.set_xlabel(r'$\tau=qt/N^2$'); a.set_ylabel('F(t)')
    a.set_title('(a) two shortcuts, three peaks\n(exact ring, $N=1500$)')
    # mark the three predicted peaks
    for tp in (3.0e-4, 5.3e-3, 6.1e-2):
        a.axvline(tp, ls=':', color='gray', lw=0.8)

    # -- E: 2D torus F(t) vs beta --
    a = axB[1]
    L = 31; v = (0, 0); u = (15, 15); r2 = (15, 13); T = 6000
    tsE = np.arange(1, T)
    for be, c in [(0.0, 'C0'), (0.10, 'C1'), (0.30, 'C2'), (0.60, 'C3')]:
        M2, babs2, idx = build_2d(L, be, v, u)
        F2 = fpt_curve(M2, babs2, idx[r2], tsE)
        a.plot(tsE, F2, color=c, label=f'β={be}')
    a.set_xscale('log'); a.set_yscale('log'); a.set_ylim(2e-6, 8e-3)
    a.set_xlabel('t'); a.set_ylabel('F(t)')
    a.set_title('(b) 2D torus ($31\\times31$):\ncapture + late interior peaks')
    a.legend(fontsize=8)

    # -- F: 2D diffusive-peak prominence vs beta (fold) --
    a = axB[2]
    betas = [0.0, 0.06, 0.15, 0.30, 0.40, 0.52, 0.60, 0.65, 0.68, 0.70, 0.72]
    proms = []
    for be in betas:
        M2, babs2, idx = build_2d(L, be, v, u)
        F2 = fpt_curve(M2, babs2, idx[r2], tsE)
        thr = 1e-3*F2.max()
        lm = [(k+1, F2[k+1]) for k in range(len(F2)-2) if F2[k+1] > F2[k] and F2[k+1] >= F2[k+2] and F2[k+1] > thr]
        dif = [(t, h) for t, h in lm if t >= 120]
        pr = 0.0
        if dif:
            dt = max(dif, key=lambda x: x[1])[0]
            seg = F2[max(0, 0):dt]
            capreg = [h for t, h in lm if t < 120]
            if capreg:
                ct = max([(t, h) for t, h in lm if t < 120], key=lambda x: x[1])[0]
                pr = F2[dt] - F2[ct:dt].min()
        proms.append(pr)
    a.plot(betas, proms, 'o-', color='C3')
    a.axhline(0, ls=':', color='gray')
    a.set_xlabel(r'shortcut strength $\beta$'); a.set_ylabel('late-peak prominence')
    a.set_title('(c) 2D fold: late-peak prominence\n$\\to0$ at $\\beta_c^{2D}\\approx0.68$')

    figA.tight_layout(); figB.tight_layout()
    outdir = Path(__file__).resolve().parents[1] / "artifacts" / "figures"
    outdir.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        figA.savefig(outdir / f"dpma_prr_figures.{ext}", dpi=140)
        figB.savefig(outdir / f"dpma_prr_extensions.{ext}", dpi=140)
    print("wrote", outdir / "dpma_prr_figures.pdf", "+ dpma_prr_extensions.pdf")

if __name__ == "__main__":
    main()
