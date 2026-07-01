#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""PRR-strengthening (round 2): start-position dependence of the fold, b_c(theta;xi).

Extended Pro's single most important remaining ask. Under the source-started convention xi=theta the
shortcut-capture feature is a short-time BOUNDARY mode (weight -> 0 as b -> 0), not a clean interior
maximum. This figure shows the saddle-node is NOT a knife-edge artifact of releasing exactly at the
gate: (a) for a start displaced off the gate (xi != theta) the capture feature becomes a genuine
interior maximum, giving two interior peaks that annihilate through the fold; (b) the fold threshold
b_c(theta=1/2; xi) varies smoothly and symmetrically about xi=theta over a neighborhood of the source.
Far from the gate the morphology changes and the simple two-mode window is lost (stated honestly).

Uses the VERIFIED continuum amplitude machinery (dpma_saddle_node_bc_theta.py): the smooth continuum
density Phi(tau)=sum_j G_j exp(-mu_j tau), free of the discrete-lattice short-time oscillations that a
finite-N ring shows away from the gate. Writes artifacts/figures/dpma_start_dependence.{pdf,png} and
artifacts/tables/dpma_start_dependence.txt
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dpma_saddle_node_bc_theta import phi_vals, bc

FIG = Path(__file__).resolve().parents[1] / "artifacts" / "figures"
TAB = Path(__file__).resolve().parents[1] / "artifacts" / "tables"
FIG.mkdir(parents=True, exist_ok=True); TAB.mkdir(parents=True, exist_ok=True)
OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

TH = 0.5
fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.4, 4.0))
plt.rcParams.update({"font.size": 10})

# ---- Panel A: continuum Phi(tau) for a start OFF the gate, across the fold ----
say("Panel A: continuum Phi(tau;b) for a start off the gate (xi=0.44, theta=1/2)")
XI = 0.44
bcA = bc(XI, TH, lo=0.3, hi=6.0)
say(f"  b_c(theta=1/2; xi=0.44) = {bcA:.4f}")
# restrict to the physical positive-density range: a finite signed-mode sum dips slightly negative
# below tau ~ 1e-3 (truncation/Gibbs artifact); the two-peak structure lives at tau in [1e-3, 0.2].
taus = np.exp(np.linspace(math.log(1.3e-3), math.log(0.5), 1400))
for b, col in [(2.5, "#264653"), (round(bcA, 2), "#e9c46a"), (3.8, "#c1121f")]:
    y = phi_vals(taus, XI, TH, b)
    # count interior maxima (continuum -> smooth)
    nmax = int(np.sum((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:])))
    lab = fr"$b={b}$" + (r" $(\approx b_c)$" if abs(b - bcA) < 0.05 else "") + f"  [{nmax} int. max.]"
    axA.plot(taus, y, color=col, lw=1.6, label=lab)
axA.set_xscale("log")
axA.set_xlim(1.3e-3, 0.5); axA.set_ylim(bottom=0)
axA.set_xlabel(r"$\tau=qt/N^2$"); axA.set_ylabel(r"$\Phi(\tau;b)$")
axA.set_title(r"(a) start off the gate: two interior peaks fold", fontsize=10)
axA.legend(frameon=False, fontsize=8.5)

# ---- Panel B: b_c(theta=1/2; xi) vs xi (neighborhood of the source) ----
say("\nPanel B: fold boundary b_c(theta=1/2; xi) vs start xi")
xis, bcs = [], []
for xi in np.linspace(0.43, 0.57, 15):
    b = bc(round(xi, 4), TH, lo=0.3, hi=6.0)
    ok = b is not None and b < 5.999
    say(f"  xi={xi:.3f}: b_c = {('%.4f' % b) if ok else 'outside clean window'}")
    if ok:
        xis.append(xi); bcs.append(b)
axB.plot(xis, bcs, "o-", color="#2a9d8f", lw=1.5, ms=4)
axB.axvline(TH, color="0.7", ls=":", lw=1.0)
axB.annotate(r"$\xi=\theta$ (source-started)", (TH, min(bcs)), xytext=(TH + 0.005, min(bcs) + 0.012),
             fontsize=8.5, color="0.4")
axB.set_xlabel(r"start position $\xi$ (gate at $\theta=1/2$)")
axB.set_ylabel(r"fold threshold $b_c(\theta{=}1/2;\,\xi)$")
axB.set_title(r"(b) the fold is robust to the release position", fontsize=10)

fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"dpma_start_dependence.{ext}", dpi=200, bbox_inches="tight")
say(f"\nwrote {FIG / 'dpma_start_dependence.pdf'}")
say("Note: for starts far from the gate (|xi-theta| large) the density morphology changes and the "
    "simple two-mode window is lost; the clean fold is a near-source feature.")
(TAB / "dpma_start_dependence.txt").write_text("\n".join(OUT) + "\n")
