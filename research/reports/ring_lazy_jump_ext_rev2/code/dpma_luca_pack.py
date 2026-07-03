#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Luca progress pack: the THREE agreed plots (meeting plan), plus the answer plot.

Agreed at the last meeting (numerics -> theory):
  (1) x=N, y=beta: where does the double peak live?           [numerical window]
  (2) x=beta, y=s_k for scanned N: how do the roots move?     [numerical -> trivial law]
  (3) x=beta, y=rho_i (amplitudes): where is the b-dependence? [analytic closed form]
Answer plot:
  (4) which terms contribute the tail / valley / peaks of F(t) [attribution]

Geometry: C.2 (lazy ring, q=2/3, absorbing v=0, shortcut source u=N/2, start r=u+d, d=4),
matching the June-12 window/attribution program. Data reused from
artifacts/data/dpma_phase_scan_full.csv; laws from notes/dpma_final_report_20260612.md
(A(4)=12.168; plateau beta*N=3.1475 for N_min~14d < N < N*~450; beyond this scan the
d=4 collapse branch is beta*N^2 ~ 1.4e3 measured at N=520-640, asymptote 100*A(4)=1216.8).
Writes artifacts/figures/dpma_luca_pack.{pdf,png} + artifacts/tables/dpma_luca_pack.txt
"""
from __future__ import annotations
import csv
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt

q = 2.0 / 3.0

def build_ring(N, u, beta):
    """transient block + channel-split absorption vectors (local copy: importing
    dpma_channel_mc would execute its whole panel build at import time)."""
    n = N - 1
    M = np.zeros((n, n)); a_sc = np.zeros(n); a_diff = np.zeros(n)
    for i in range(1, N):
        k = i - 1
        be = beta if i == u else 0.0
        M[k, k] = (1 - q) * (1 - be)
        if be:
            a_sc[k] += be * (1 - q)
        for j in (i - 1, i + 1):
            if j % N == 0:
                a_diff[k] += q / 2.0
            elif 1 <= j <= N - 1:
                M[k, (j % N) - 1] += q / 2.0
    return M, a_sc, a_diff

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "artifacts" / "figures"
TAB = ROOT / "artifacts" / "tables"
OUT = []
def say(s=""):
    print(s, flush=True); OUT.append(s)

D = 4                                   # C.2 start offset
A4 = 12.168                             # lower-boundary constant A(d=4), June report
PLATEAU = 3.1475                        # upper boundary beta*N (N < N*)
NSTAR = 450                             # binding switch for d=4 (collapse branch beyond scan)

def modes_lattice(N, beta, r):
    """exact eigen-modes: eigenvalues s (desc) and residues B_j for start r (total channel)."""
    M, a_sc, a_diff = build_ring(N, N // 2, beta)
    s, V = np.linalg.eigh(M)
    er = np.zeros(N - 1); er[r - 1] = 1.0
    with np.errstate(all="ignore"):
        B = (er @ V) * (V.T @ (a_sc + a_diff))
    B = np.where(np.isfinite(B), B, 0.0)
    order = np.argsort(s)[::-1]
    return s[order], B[order]

# ---- closed-form residues (App. A of the manuscript): N_{r,u}(y)/D_u(y), B_j=q N/D' -------
def U(m, y):
    """Chebyshev U_m(y) by recurrence (m can be 0..N)."""
    if m < 0: return 0.0
    um1, um = 1.0, 2.0 * y
    if m == 0: return 1.0
    if m == 1: return um
    for _ in range(m - 1):
        um1, um = um, 2.0 * y * um - um1
    return um

def closed_form_modes(N, beta, r, nroots=6):
    """top slowest roots y_j of D_u and closed-form residues B_j (u=N/2, r>=u mirror formula)."""
    u = N // 2
    lam = beta * (1 - q); a = q / lam
    A = lambda m, y: U(m - 1, y)                     # A_m := U_{m-1}
    Du = lambda y: a * U(N - 1, y) + 2 * U(u - 1, y) * U(N - u - 1, y)
    # slowest modes: y near 1; scan y in (cos(8*pi/N), 1)
    ys = np.linspace(math.cos(8 * math.pi / N), 1 - 1e-12, 4000)
    vals = np.array([Du(t) for t in ys])
    sgn = np.sign(vals)
    idx = np.where(sgn[:-1] * sgn[1:] < 0)[0]
    roots = []
    for i in idx[::-1][:nroots]:                     # from y~1 downward = slowest first
        lo, hi = ys[i], ys[i + 1]
        flo = Du(lo)
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if flo * Du(mid) <= 0: hi = mid
            else: lo, flo = mid, Du(mid)
        roots.append(0.5 * (lo + hi))
    out_s, out_B = [], []
    for y in roots:
        # mirror numerator for r >= u:  a[A_r+A_{N-r}] + 2 A_u [A_{N-r} + A_{r-u}]
        Nru = a * (A(r, y) + A(N - r, y)) + 2 * A(u, y) * (A(N - r, y) + A(r - u, y))
        h = 1e-7
        Dp = (Du(y + h) - Du(y - h)) / (2 * h)
        out_s.append(1 - q + q * y)
        out_B.append(q * Nru / Dp)
    return np.array(out_s), np.array(out_B)

def main():
    fig, ax = plt.subplots(2, 2, figsize=(12.5, 9.2))

    # ---------- (1) N-beta double-peak window (C.2 classifier, d=4) ----------
    a = ax[0, 0]
    rows = [r for r in csv.DictReader(open(ROOT / "artifacts" / "data" / "dpma_phase_scan_full.csv"))
            if int(r["d"]) == D]
    Ny = np.array([int(r["N"]) for r in rows]); By = np.array([float(r["beta"]) for r in rows])
    cl = np.array([int(r["clear"]) for r in rows])
    a.scatter(Ny[cl == 0], By[cl == 0], s=9, c="0.8", label="single/unclear")
    a.scatter(Ny[cl == 1], By[cl == 1], s=11, c="C0", label="double peak (C.2)")
    NMIN = 14 * D                                    # finite-size onset N_min ~ 14 d (June law)
    NN = np.geomspace(NMIN, Ny.max(), 200)
    a.plot(NN, A4 / NN**2, "C3--", lw=1.4, label=r"lower: $\beta N^2=A(4)=12.17$")
    a.plot(NN, PLATEAU / NN, "C2--", lw=1.4,
           label=r"upper ($N<N^*{\approx}450$): $\beta N=3.148$")
    a.axvline(NMIN, color="0.5", ls=":", lw=0.9)
    a.text(NMIN * 1.05, 2.5e-4, r"onset $N_{\min}{\approx}14d$", fontsize=7, rotation=90)
    a.text(0.44, 0.86, "beyond this scan ($N>N^*$):\n$\\beta N^2\\to1.4{\\times}10^3$ (meas.\\ $N$=520--640),\n"
           r"$\to100A(4)=1.22{\times}10^3$ (asympt.)", transform=a.transAxes, fontsize=7)
    a.set_xscale("log"); a.set_yscale("log")
    a.set_xlabel("N"); a.set_ylabel(r"$\beta$")
    a.set_title(f"(1) where the double peak lives (d={D})")
    a.legend(fontsize=7, loc="lower left")
    say(f"(1) window map: {int((cl==1).sum())} double-peak cells of {len(rows)} (d={D})")

    # ---------- (2) roots s_k(beta): numerical dots -> trivial uniform-shift law ----------
    a = ax[0, 1]
    KS = 6
    betas = np.linspace(0.0005, 0.032, 12)
    N = 100; r0 = N // 2 + D
    shifts100 = None
    for NN2, mk, fill in ((100, "o", True), (200, "s", False)):
        alph = np.array([1 - q + q * math.cos(k * math.pi / NN2) for k in range(1, KS + 1)])
        shifts = np.zeros((len(betas), KS))
        for i, be in enumerate(betas):
            s, _ = modes_lattice(NN2, be, NN2 // 2 + D)
            shifts[i] = s[:KS] - alph[:KS]
        if NN2 == 100:
            shifts100 = shifts.copy()
        for k in range(KS):
            a.plot(betas, shifts[:, k] * NN2 * 1e2, mk, ms=4, color=f"C{k}",
                   mfc=(f"C{k}" if fill else "none"),
                   label=(f"$s_{k+1}$" if NN2 == 100 else None))
    bb = np.linspace(0, 0.033, 50)
    a.plot(bb, -2 * bb * (1 - q) * 1e2, "k--", lw=1.2,
           label=r"law: $N\,\delta s=-2\beta(1-q)$ (odd $k$)")
    a.axhline(0, color="k", lw=0.8, ls=":")
    a.text(0.019, -0.45, "even $k$: frozen (top row)", fontsize=8)
    a.text(0.0007, -1.85, "filled: $N{=}100$; hollow: $N{=}200$ (collapse)", fontsize=7)
    a.set_xlabel(r"$\beta$"); a.set_ylabel(r"$N\,(s_k(\beta)-s_k(0))\times10^2$")
    a.set_title("(2) the roots move TRIVIALLY ($N$-collapse)")
    a.legend(fontsize=7, ncol=2)
    r_small = abs(shifts100[0, 0] - (-2 * betas[0] * (1 - q) / 100)) / (2 * betas[0] * (1 - q) / 100)
    r_large = abs(shifts100[-1, 0] - (-2 * betas[-1] * (1 - q) / 100)) / (2 * betas[-1] * (1 - q) / 100)
    say(f"(2) uniform-shift law (first order in beta): rel residual {r_small:.1e} at "
        f"beta={betas[0]:.4f}; second-order correction grows to {r_large:.0%} at the window edge "
        f"beta={betas[-1]:.3f} (visible as the departure of the dots from the dashed line)")

    # ---------- (3) amplitudes rho_i(beta): closed form (lines) vs eigh (dots) ----------
    a = ax[1, 0]
    bdense = np.linspace(0.001, 0.032, 40)
    JSHOW = 4
    lines = np.zeros((len(bdense), JSHOW))
    for i, be in enumerate(bdense):
        _, Bcf = closed_form_modes(N, be, r0, nroots=JSHOW)
        lines[i] = Bcf[:JSHOW]
    for j in range(JSHOW):
        a.plot(bdense, lines[:, j] * 1e3, "-", color=f"C{j}", lw=1.4,
               label=rf"$\rho_{j+1}$ (closed form)")
    for be in betas[::2]:
        s, B = modes_lattice(N, be, r0)
        a.plot([be] * JSHOW, B[:JSHOW] * 1e3, "k.", ms=5)
    # cross-check closed form vs eigh at one beta -- only modes with NONZERO amplitude
    # (even-k modes have B identically 0: the two boundary fluxes cancel in antiphase AND the
    #  shortcut sits on their node, so they decouple from the absorption channel entirely).
    s_cf, B_cf = closed_form_modes(N, 0.01, r0, nroots=JSHOW)
    s_ex, B_ex = modes_lattice(N, 0.01, r0)
    live = [j for j in range(JSHOW) if abs(B_ex[j]) > 1e-8]
    err = max(abs(B_cf[j] - B_ex[j]) / abs(B_ex[j]) for j in live)
    say(f"(3) closed-form residues vs eigh at beta=0.01 (live modes {[(j+1) for j in live]}): "
        f"max rel diff {err:.1e}; even-k modes have exactly zero amplitude (decoupled)")
    a.text(0.012, -0.55, "even $k$: $\\rho\\equiv0$ (decoupled)", fontsize=8)
    a.axhline(0, color="k", lw=0.8, ls=":")
    a.set_xlabel(r"$\beta$"); a.set_ylabel(r"$\rho_j\times10^3$")
    a.set_title(f"(3) the amplitudes carry ALL the $\\beta$-dependence (N={N}, start $u{{+}}{D}$)")
    a.legend(fontsize=7)

    # ---------- (4) which terms contribute the tail / peaks ----------
    a = ax[1, 1]
    be = 0.01
    s, B = modes_lattice(N, be, r0)
    ts = np.unique(np.round(np.geomspace(2, 4000, 900)).astype(int))
    ls = np.log(np.clip(s, 1e-300, None))
    def curve(kmax):
        return (np.exp(np.outer(ts - 1.0, ls[:kmax])) * B[:kmax]).sum(axis=1)
    full = (np.exp(np.outer(ts - 1.0, ls)) * B).sum(axis=1)
    a.plot(ts, full, "k-", lw=2.0, label="full $F(t)$")
    for kmax, c, lab in ((1, "C3", "mode 1"), (3, "C1", "modes 1–3"),
                         (9, "C0", "modes 1–9 (5 live)"), (31, "C2", "modes 1–31 (17 live)")):
        a.plot(ts, curve(kmax), "--", color=c, lw=1.3, label=lab)
    a.set_ylim(-7.5e-4, 1.05e-3)
    # attribution markers (June table, N=100 beta=0.01 d=4: t1=24, tv=239, t2=1091)
    for t_mark, txt in ((24, "peak 1\n(~31 modes,\n17 live)"), (239, "valley\n(~9 modes,\n5 live)"),
                        (1091, "peak 2\n(3 modes;\nmode 1 = 115%)")):
        a.axvline(t_mark, color="0.6", ls=":", lw=0.9)
        a.text(t_mark * 1.1, a.get_ylim()[1] * 0.02 if t_mark > 100 else 0.0006, txt, fontsize=7)
    i2 = np.argmin(abs(ts - 1091))
    say(f"(4) at t2=1091: mode-1 share {curve(1)[i2]/full[i2]*100:.0f}%, "
        f"modes 1-3 share {curve(3)[i2]/full[i2]*100:.1f}%")
    itail = np.argmin(abs(ts - 3000))
    say(f"(4) deep tail t=3000: mode-1 share {curve(1)[itail]/full[itail]*100:.2f}%")
    a.set_xscale("log")
    a.set_xlabel("t"); a.set_ylabel("F(t)")
    a.set_title(f"(4) which terms build the curve (N={N}, $\\beta$={be}, d={D})")
    a.legend(fontsize=7)

    fig.tight_layout()
    FIG.mkdir(parents=True, exist_ok=True); TAB.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"dpma_luca_pack.{ext}", dpi=140)
    (TAB / "dpma_luca_pack.txt").write_text("\n".join(OUT) + "\n")
    print("wrote", FIG / "dpma_luca_pack.pdf")

if __name__ == "__main__":
    main()
