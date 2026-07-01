#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""PRR-strengthening (round 2): an INDEPENDENT, structurally different instance of the fold.

Both round-2 audits (Claude + ChatGPT Extended Pro) named this the single highest-leverage addition:
demonstrate the saddle-node in a model that is NOT the lazy ring and uses NO spectral input, to turn
Woodbury 'model-independence' from algebra into a realized second instance.

Here: a direct continuum Brownian-dynamics (Euler-Maruyama) simulation of the delivery-gate protocol.
A particle diffuses on [0,1] (D=1/2, so d_tau p = 1/2 p_xx), absorbed at the ends x=0,1 (the target),
and killed at rate b/ell while inside a narrow gate of width ell centred at theta (-> a delta-sink of
strength b as ell->0). No lattice, no eigen-decomposition. Started off the gate (xi != theta) so both
arrival-time features are genuine interior peaks. We overlay the BD first-passage histogram on the
EXACT continuum density Phi(tau) (from dpma_saddle_node_bc_theta.phi_vals) below and above b_c(theta;xi):
the independent BD reproduces the interior second peak and its annihilation at the fold.

Writes artifacts/figures/dpma_brownian_fold.{pdf,png} and artifacts/tables/dpma_brownian_fold.txt
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

def brownian_fpt(theta, xi, b, ell=0.02, dt=1.5e-5, nwalk=60000, tau_max=1.4, seed=7):
    """Euler-Maruyama BD; returns first-passage times tau (absorbed at ends OR killed in the gate)."""
    rng = np.random.default_rng(seed)         # fixed literal seed -> deterministic
    x = np.full(nwalk, xi)
    alive = np.ones(nwalk, dtype=bool)
    tabs = np.zeros(nwalk)
    glo, ghi = theta - ell / 2, theta + ell / 2
    kill_p = (b / ell) * dt                   # per-step kill prob inside the gate
    sig = math.sqrt(2 * 0.5 * dt)             # D=1/2
    nsteps = int(tau_max / dt)
    for n in range(1, nsteps + 1):
        idx = np.where(alive)[0]
        if idx.size == 0:
            break
        xi_ = x[idx] + sig * rng.standard_normal(idx.size)
        # gate kill (before boundary check): those inside the gate, with prob kill_p
        ingate = (xi_ >= glo) & (xi_ <= ghi)
        killed = ingate & (rng.random(idx.size) < kill_p)
        # boundary absorption
        absorbed_end = (xi_ <= 0.0) | (xi_ >= 1.0)
        done = killed | absorbed_end
        d = idx[done]
        if d.size:
            alive[d] = False; tabs[d] = n * dt
        still = idx[~done]
        x[still] = xi_[~done]
    return tabs[~alive]

# ---- setup: start off the gate so both features are interior peaks ----
theta, xi, ell = 0.5, 0.44, 0.02
bcv = bc(xi, theta, lo=0.3, hi=6.0)
say(f"delta-sink b_c(theta=0.5; xi=0.44) = {bcv:.4f}; BD gate width ell={ell}")

fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.0))
plt.rcParams.update({"font.size": 10})
taus_exact = np.exp(np.linspace(math.log(1.3e-3), math.log(0.6), 1200))

for ax, b, tag in [(axes[0], 2.5, "below"), (axes[1], 3.8, "above")]:
    say(f"\nBD at b={b} ({tag} b_c):")
    fpt = brownian_fpt(theta, xi, b, ell=ell)
    say(f"  absorbed {len(fpt)} walkers; median tau={np.median(fpt):.4f}")
    bins = np.logspace(math.log10(1.3e-3), math.log10(0.6), 60)
    ax.hist(fpt, bins=bins, density=True, color="0.82", edgecolor="0.6", lw=0.3,
            label="Brownian dynamics")
    ye = phi_vals(taus_exact, xi, theta, b)
    # normalise the exact density over the same support for overlay
    ax.plot(taus_exact, ye, color="#c1121f", lw=1.8, label=r"exact $\Phi(\tau)$")
    nmax = int(np.sum((ye[1:-1] > ye[:-2]) & (ye[1:-1] > ye[2:])))
    ax.set_xscale("log"); ax.set_xlim(1.3e-3, 0.6)
    ax.set_xlabel(r"$\tau$"); ax.set_ylabel("FPT density")
    ax.set_title(fr"$b={b}$ ({'two' if nmax>=2 else 'one'} interior peak{'s' if nmax>=2 else ''}, {tag} $b_c\simeq{bcv:.2f}$)",
                 fontsize=10)
    ax.legend(frameon=False, fontsize=9)

fig.suptitle(r"Independent continuum Brownian-dynamics instance (no lattice, no spectral input)",
             fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.96])
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"dpma_brownian_fold.{ext}", dpi=200, bbox_inches="tight")
say(f"\nwrote {FIG / 'dpma_brownian_fold.pdf'}")
(TAB / "dpma_brownian_fold.txt").write_text("\n".join(OUT) + "\n")
