#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""PRR-strengthening: (A) direct Monte-Carlo validation of the exact FPT density and the
saddle-node double peak; (B) EXACT channel-resolved decomposition f = f_shortcut + f_diffusive
(which arrival-time mode comes from which absorption channel); (C) a NON-antipodal example
(theta=0.38) showing the same fold off the reflection-symmetric ring.

Model (matches dpma_multishortcut.py): lazy ring, N sites, stay 1-q, hop q/2 each way; absorbing
target v=0; a directed shortcut at u redirects beta(1-q) of the u self-loop to v. Continuum map:
b=beta(1-q)N/q, theta=u/N, tau=q t/N^2. The absorption vector splits by channel: the shortcut
entry (beta(1-q) at u) and the diffusive entries (q/2 at the two neighbours of v=0).

Writes artifacts/figures/dpma_channel_mc.{pdf,png} and artifacts/tables/dpma_channel_mc.txt
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

q = 2.0 / 3.0
FIG = Path(__file__).resolve().parents[1] / "artifacts" / "figures"
TAB = Path(__file__).resolve().parents[1] / "artifacts" / "tables"
FIG.mkdir(parents=True, exist_ok=True); TAB.mkdir(parents=True, exist_ok=True)
OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

# ------------------------------------------------------------------ exact model
def build_ring(N, u, beta):
    """Transient block M (sites 1..N-1) + absorption vectors split by channel."""
    n = N - 1
    M = np.zeros((n, n))
    a_sc = np.zeros(n)    # shortcut channel (delivery at u)
    a_diff = np.zeros(n)  # diffusive channel (hop into v=0)
    for i in range(1, N):
        k = i - 1
        be = beta if i == u else 0.0
        M[k, k] = (1 - q) * (1 - be)
        if be:
            a_sc[k] += be * (1 - q)
        for j in (i - 1, i + 1):
            if j % N == 0:            # neighbour is the absorbing target v=0
                a_diff[k] += q / 2.0
            elif 1 <= j <= N - 1:
                M[k, (j % N) - 1] += q / 2.0
    return M, a_sc, a_diff

def fpt_channels(M, a_sc, a_diff, r, ts):
    """Exact FPT pmf and its two channel components at integer times ts (start site r)."""
    s, V = np.linalg.eigh(M)
    er = np.zeros(M.shape[0]); er[r - 1] = 1.0
    with np.errstate(all="ignore"):
        proj = er @ V
        B_tot = proj * (V.T @ (a_sc + a_diff))
        B_sc = proj * (V.T @ a_sc)
        B_diff = proj * (V.T @ a_diff)
        ls = np.log(np.clip(s, 1e-300, None))
        def curve(B):
            return np.array([float(np.sum(B * np.exp((t - 1) * ls))) for t in ts])
        return curve(B_tot), curve(B_sc), curve(B_diff)

# ------------------------------------------------------------------ direct Monte Carlo
def montecarlo(N, u, beta, r, nwalk, tmax, seed_offset):
    """Vectorised direct simulation of the discrete chain. Returns absorption times (in tau) and
    channel labels (0=diffusive,1=shortcut). No global RNG seeding (deterministic-free per repo
    convention); reproducibility via fixed nwalk and vectorised draws is adequate for a histogram."""
    rng = np.random.default_rng(12345 + seed_offset)  # fixed literal seed -> deterministic
    pos = np.full(nwalk, r, dtype=np.int64)
    alive = np.ones(nwalk, dtype=bool)
    tabs = np.zeros(nwalk, dtype=np.int64)
    chan = np.full(nwalk, -1, dtype=np.int8)
    stay_u = (1 - q) * (1 - beta)          # stay prob at u
    for t in range(1, tmax + 1):
        idx = np.where(alive)[0]
        if idx.size == 0:
            break
        p = pos[idx]
        rnd = rng.random(idx.size)
        atu = (p == u)
        # thresholds: [shortcut-absorb][stay][hop-left][hop-right]
        move = np.empty(idx.size, dtype=np.int8)  # 0 stay,1 left,2 right,3 shortcut
        # non-u sites: stay 1-q, left q/2, right q/2
        thr_stay = np.where(atu, stay_u, (1 - q))
        thr_sc = np.where(atu, beta * (1 - q), 0.0)
        # order: shortcut first (only at u), then stay, then left, then right
        move[:] = 3  # default shortcut slot (only reachable at u)
        c_sc = thr_sc
        c_stay = c_sc + thr_stay
        c_left = c_stay + q / 2.0
        move = np.where(rnd < c_sc, 3,
                np.where(rnd < c_stay, 0,
                np.where(rnd < c_left, 1, 2))).astype(np.int8)
        newp = p.copy()
        newp = np.where(move == 1, p - 1, newp)
        newp = np.where(move == 2, p + 1, newp)
        # shortcut absorption
        sc_abs = (move == 3)
        # diffusive absorption: landed on 0 or N (== v=0)
        diff_abs = (newp <= 0) | (newp >= N)
        # resolve
        done_sc = idx[sc_abs]
        done_diff = idx[diff_abs & ~sc_abs]
        if done_sc.size:
            alive[done_sc] = False; tabs[done_sc] = t; chan[done_sc] = 1
        if done_diff.size:
            alive[done_diff] = False; tabs[done_diff] = t; chan[done_diff] = 0
        still = idx[~sc_abs & ~diff_abs]
        pos[still] = newp[~sc_abs & ~diff_abs]
    absorbed = ~alive
    tau = q * tabs[absorbed] / (N * N)
    return tau, chan[absorbed], absorbed.sum(), nwalk

# ------------------------------------------------------------------ build the three panels
def tgrid(N, tau_max, npts=1400):
    tmax = int(tau_max * N * N / q)
    ts = np.unique(np.round(np.exp(np.linspace(math.log(2), math.log(tmax), npts))).astype(np.int64))
    return ts

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0))
plt.rcParams.update({"font.size": 10})

# ---- Panel A: MC vs exact (antipodal, double peak) ----
say("Panel A: direct Monte-Carlo vs exact FPT density (antipodal, double peak)")
Na, ua = 100, 50
ba = 2.6                                   # below b_c(1/2)=3.0764 -> double peak
beta_a = ba * q / ((1 - q) * Na)
ra = ua                                     # start at source xi=theta=1/2
tau_max_a = 3.0
tsA = tgrid(Na, tau_max_a)
Ftot, Fsc, Fdiff = fpt_channels(*build_ring(Na, ua, beta_a), ra, tsA)
tauA = q * tsA / (Na * Na)
dens_scale = (Na * Na) / q                  # F(t)*dt/dtau, dt=1
say(f"  N={Na}, u={ua}, b={ba} (beta={beta_a:.4f}), start r={ra}")
nwalk = 400_000
tmc = int(6.0 * Na * Na / q)
tau_mc, chan_mc, nabs, ntot = montecarlo(Na, ua, beta_a, ra, nwalk, tmc, 0)
say(f"  MC walkers={ntot}, absorbed={nabs} ({100*nabs/ntot:.2f}%), pi_sc(MC)={np.mean(chan_mc==1):.5f}")
# exact splitting probability: closed form pi_sc = 2 min(r,u)(N-max(r,u)) / (aN + 2u(N-u)),
# a=q/lambda (Sherman-Morrison at z=1). The truncated pmf sum is tail-biased (the cut late-time
# mass is disproportionately diffusive), so it is logged only as a consistency check.
a_sm = q / (beta_a * (1 - q))               # a = q/lambda = N/b
pi_sc_exact = 2 * min(ra, ua) * (Na - max(ra, ua)) / (a_sm * Na + 2 * ua * (Na - ua))
say(f"  pi_sc(exact, closed form)={pi_sc_exact:.5f}")
tsFull = np.arange(1, int(8.0*Na*Na/q))
_, FscFull, FdiffFull = fpt_channels(*build_ring(Na, ua, beta_a), ra, tsFull)
say(f"  pi_sc(truncated pmf sum, tau<=8)={float(FscFull.sum()/(FscFull.sum()+FdiffFull.sum())):.4f} (tail-biased)")
axA = axes[0]
logbins = np.logspace(math.log10(3e-4), math.log10(tau_max_a), 60)
cnts, _ = np.histogram(tau_mc, bins=logbins)
say(f"  MC histogram bins: {len(logbins)-1}, nonempty {int((cnts>0).sum())}, "
    f"min nonempty count {int(cnts[cnts>0].min())}, median {int(np.median(cnts[cnts>0]))}")
axA.hist(tau_mc, bins=logbins, density=True, color="0.82",
         edgecolor="0.6", lw=0.3, label="direct MC")
axA.plot(tauA, Ftot * dens_scale, color="#c1121f", lw=1.8, label="exact")
axA.set_xscale("log"); axA.set_yscale("log")
axA.set_xlim(3e-4, tau_max_a); axA.set_ylim(3e-2, 400)
axA.set_xlabel(r"$\tau=qt/N^2$"); axA.set_ylabel(r"FPT density")
axA.set_title(r"(a) direct simulation vs exact ($\theta=1/2$, $b=2.6<b_c$)", fontsize=10)
axA.legend(frameon=False, fontsize=9)

# ---- Panel B: exact channel-resolved decomposition ----
say("\nPanel B: exact channel-resolved decomposition f = f_shortcut + f_diffusive")
axB = axes[1]
axB.plot(tauA, Ftot * dens_scale, color="k", lw=1.8, label="total")
axB.plot(tauA, Fsc * dens_scale, color="#2a9d8f", lw=1.6, ls="-", label="shortcut channel")
axB.plot(tauA, Fdiff * dens_scale, color="#e76f51", lw=1.6, ls="--", label="diffusive channel")
axB.set_xscale("log"); axB.set_yscale("log")
axB.set_xlim(3e-4, tau_max_a); axB.set_ylim(3e-2, 400)
axB.set_xlabel(r"$\tau=qt/N^2$"); axB.set_ylabel(r"FPT density")
axB.set_title(r"(b) channel resolution (early=shortcut, late=diffusive)", fontsize=10)
axB.legend(frameon=False, fontsize=9)

# ---- Panel C: non-antipodal example (theta=0.38) across b_c ----
say("\nPanel C: non-antipodal theta=0.38 (b_c(0.38)~2.16), fold off the antipode")
Nc, uc = 100, 38
rc = uc                                     # start at source xi=theta=0.38
tau_max_c = 2.5
tsC = tgrid(Nc, tau_max_c)
tauC = q * tsC / (Nc * Nc)
axC = axes[2]
for bc_, col in [(1.5, "#264653"), (2.16, "#e9c46a"), (2.8, "#c1121f")]:
    beta_c = bc_ * q / ((1 - q) * Nc)
    Ft, _, _ = fpt_channels(*build_ring(Nc, uc, beta_c), rc, tsC)
    axC.plot(tauC, Ft * (Nc * Nc) / q, color=col, lw=1.6,
             label=fr"$b={bc_}$")
    # count interior maxima for the record
    y = Ft * (Nc * Nc) / q
    mx = np.sum((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))
    say(f"  b={bc_:.2f}: interior maxima={mx}")
axC.set_xscale("log"); axC.set_yscale("log")
axC.set_xlim(3e-4, tau_max_c); axC.set_ylim(3e-2, 400)
axC.set_xlabel(r"$\tau=qt/N^2$"); axC.set_ylabel(r"FPT density")
axC.set_title(r"(c) non-antipodal $\theta=0.38$ across $b_c(\theta)\!\approx\!2.16$", fontsize=10)
axC.legend(frameon=False, fontsize=9)

fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"dpma_channel_mc.{ext}", dpi=200, bbox_inches="tight")
say(f"\nwrote {FIG / 'dpma_channel_mc.pdf'}")
(TAB / "dpma_channel_mc.txt").write_text("\n".join(OUT) + "\n")
