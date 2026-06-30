#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
"""Generate the four DPMA report figures into artifacts/figures/.

F1 phase/feature diagram (N, beta) per d with refined boundaries + asymptotic laws
F2 spectrum flow: raw s_k(beta), parallel-lines collapse, uniformity residual
F3 amplitude flows + attribution (k_eps, channel-vs-time mass, example curve)
F4 boundary-law collapse (beta_lo*N^2 -> A(d); upper edge two-branch with N* switch; b-window)
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from shortcut_double_peak_mode_attribution import (
    Q_DEFAULT, chebyshev_modes, evaluate, spectral,
)

ART = Path(__file__).resolve().parents[1] / "artifacts"
FIG = ART / "figures"
FIG.mkdir(parents=True, exist_ok=True)
q = Q_DEFAULT

plt.rcParams.update({"font.size": 9.5, "axes.titlesize": 10, "legend.fontsize": 8,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 200})

C_TEAL, C_GRAY, C_BLUE, C_CORAL, C_PURPLE, C_AMBER = (
    "#0F6E56", "#444444", "#185FA5", "#D85A30", "#7F77DD", "#BA7517")


def load_csv(p):
    return list(csv.DictReader(open(p)))


# ----------------------------------------------------------- F1 phase diagram
def fig1():
    rows = load_csv(ART / "data" / "dpma_phase_scan_full.csv")
    ref = load_csv(ART / "data" / "dpma_boundary_refined.csv")
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.9), sharey=True)
    cmap = {"single": "#E8E6E0", "shoulder": "#F5C4B3", "bump": "#FAC775",
            "double": "#0F6E56"}
    for ax, d in zip(axes, (3, 4, 5)):
        sel = [r for r in rows if r["d"] == str(d)]
        for r in sel:
            N, beta = int(r["N"]), float(r["beta"])
            if r["clear"] == "1":
                c = cmap["double"]
            elif int(r["n_peaks"]) < 2:
                c = cmap["single"]
            elif float(r["valley_frac"] or 0) > 0.8:
                c = cmap["shoulder"]
            else:
                c = cmap["bump"]
            ax.scatter([N], [beta], s=13, c=c, marker="s", linewidths=0)
        rb = [r for r in ref if r["d"] == str(d) and r["window"] == "1"]
        Ns = np.array([int(r["N"]) for r in rb])
        blo = np.array([float(r["beta_lo"]) for r in rb])
        bhi = np.array([float(r["beta_hi"]) for r in rb])
        ax.plot(Ns, blo, "-", color=C_GRAY, lw=1.6)
        ax.plot(Ns, bhi, "-", color=C_GRAY, lw=1.6)
        Ng = np.linspace(30, 245, 200)
        A = {3: 9.087, 4: 12.168, 5: 15.36}[d]
        ax.plot(Ng, A / Ng**2, "--", color=C_BLUE, lw=1.4,
                label=r"$\beta=A(d)/N^2$ (fitted)")
        ax.plot(Ng, 3.1475 / Ng, "--", color=C_CORAL, lw=1.4,
                label=r"$\beta=3.1475/N$ (valley branch)")
        ax.plot(Ng, 4.0 / Ng, ":", color=C_PURPLE, lw=1.2,
                label=r"$\beta_c=2q/((1{-}q)N)$")
        ax.set_yscale("log")
        ax.set_xlim(10, 248); ax.set_ylim(8e-5, 0.25)
        ax.set_xlabel("$N$")
        ax.set_title(f"$d={d}$  (start offset from $u$)")
        if d == 3:
            ax.set_ylabel(r"$\beta$")
            ax.legend(frameon=False, loc="upper right")
    handles = [plt.Line2D([], [], marker="s", ls="", color=v, label=k)
               for k, v in [("double_peak (C.2 clear)", cmap["double"]),
                            ("local_bump", cmap["bump"]),
                            ("shoulder", cmap["shoulder"]),
                            ("single_peak", cmap["single"])]]
    axes[1].legend(handles=handles, frameon=False, loc="upper right", fontsize=7.5)
    fig.suptitle("F1  Clear-double-peak window in the $(N,\\beta)$ plane  "
                 "(lazy ring, $q=2/3$, antipodal shortcut $u\\to v$; classifier: C.2 five-condition rule)",
                 y=1.0, fontsize=10)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"dpma_fig1_phase_diagram.{ext}")
    plt.close(fig)
    print("F1 done")


# ----------------------------------------------------------- F2 spectrum flow
def fig2():
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.7))
    # (a) raw s_k(beta), N=100
    N = 100
    L = N // 2
    betas = np.logspace(-4, -0.85, 36)
    sflow = np.array([chebyshev_modes(N, q, b, L - 4)[0][:6] for b in betas])
    alpha = 1 - q + q * np.cos((2 * np.arange(1, 7) - 1) * np.pi / N)
    gam = 1 - q + q * np.cos(2 * np.arange(1, 7) * np.pi / N)
    ax = axes[0]
    for k in range(6):
        ax.semilogx(betas, sflow[:, k], "-", color=C_TEAL, lw=1.5)
        ax.axhline(alpha[k], color=C_BLUE, lw=0.7, ls=":")
        ax.axhline(gam[k], color=C_GRAY, lw=0.6, ls="--", alpha=0.6)
    ax.set_xlabel(r"$\beta$"); ax.set_ylabel(r"$s_k$")
    ax.set_ylim(0.975, 1.0005)
    ax.set_title(r"(a) root flow $s_k(\beta)$, $N=100$" "\n"
                 r"dotted $=\alpha_k$ (start), dashed $=\gamma_k$ (barrier)")
    # (b) parallel-lines collapse
    ax = axes[1]
    markers = {60: "o", 100: "s", 200: "^"}
    for N2 in (60, 100, 200):
        L2 = N2 // 2
        bs = np.logspace(-4, np.log10(0.5 * np.pi / 2 / (1 - q) * q / N2 * 2), 14)
        bvals = bs * (1 - q) * N2 / q
        s = np.array([chebyshev_modes(N2, q, b, L2 - 4)[0][:4] for b in bs])
        for k in range(4):
            ax.plot(bvals, N2**2 * (1 - s[:, k]) / q, markers[N2], ms=3.5,
                    color=C_TEAL, alpha=0.75,
                    label=f"$N={N2}$" if k == 0 else None)
    bg = np.linspace(0, 1.7, 50)
    for k in range(4):
        ax.plot(bg, (2 * k + 1)**2 * np.pi**2 / 2 + 2 * bg, "-", color=C_CORAL,
                lw=1.2, label="first-order law" if k == 0 else None)
    ax.set_xlabel(r"$b=\beta(1-q)N/q$")
    ax.set_ylabel(r"$N^2(1-s_k)/q$")
    ax.set_title("(b) parallel-lines collapse:\n"
                 r"$N^2(1-s_k)/q=(2k{-}1)^2\pi^2/2+2b$")
    ax.legend(frameon=True, framealpha=0.85, edgecolor="none", loc="center right")
    # (c) uniformity residual (second order)
    ax = axes[2]
    N3, L3 = 100, 50
    s0 = 1 - q + q * np.cos((2 * np.arange(1, 5) - 1) * np.pi / N3)
    bs = np.logspace(-4, -1.2, 24)
    for k in range(4):
        res = []
        for b in bs:
            s = chebyshev_modes(N3, q, b, L3 - 4)[0][k]
            res.append((s0[k] - s) * N3 / (2 * b * (1 - q)) - 1.0)
        ax.semilogx(bs * (1 - q) * N3 / q, res, "-", lw=1.4,
                    label=f"$k={k+1}$")
    ax.set_xlabel(r"$b$"); ax.set_ylabel("relative deviation from uniform shift")
    ax.set_title("(c) second-order (mode-dependent) part,\n$N=100$")
    ax.legend(frameon=False)
    fig.suptitle("F2  Spectral flow under the shortcut: uniform first-order shift "
                 r"$\delta s_k=-2\beta(1-q)/N$ and its corrections  ($q=2/3$, antipodal shortcut $u\to v$)", y=1.0, fontsize=10)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"dpma_fig2_spectrum_flow.{ext}")
    plt.close(fig)
    print("F2 done")


# ------------------------------------------- F3 amplitudes and attribution
def fig3():
    fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.6))
    N, d = 100, 4
    L = N // 2
    rho = L - d
    # (a) B_j(beta)
    ax = axes[0]
    betas = np.logspace(-4, -1.2, 30)
    Bflow = np.array([chebyshev_modes(N, q, b, rho)[1][:5] for b in betas])
    th = (2 * np.arange(1, 6) - 1) * np.pi / N
    fj = (2 * q / N) * np.sin(rho * th) * np.sin(th)
    for j in range(5):
        ax.semilogx(betas, Bflow[:, j] * 1e3, "-", lw=1.4, label=f"$j={j+1}$")
        ax.plot(betas[0], fj[j] * 1e3, "o", ms=4, color=C_GRAY)
    ax.set_xlabel(r"$\beta$"); ax.set_ylabel(r"$B_{\rho j}\times 10^3$")
    ax.set_title(f"(a) amplitude flow, $N={N}$, $d={d}$\n"
                 r"dots: $\beta\to0$ limits $f_j$ (no-shortcut residues)")
    ax.legend(frameon=False, fontsize=7)
    # (b) k_1% per feature vs beta
    ax = axes[1]
    bs = [0.002, 0.004, 0.008, 0.012, 0.018, 0.025]
    rows = []
    from dpma_attribution import kmin
    for b in bs:
        spec, F, f = evaluate(N, q, b, (L + d) % N)
        if f.t2 is None:
            continue
        rows.append((b, kmin(F, spec, f.t1, 0.01), kmin(F, spec, f.t_valley, 0.01),
                     kmin(F, spec, f.t2, 0.01)))
    arr = np.array(rows)
    ax.semilogx(arr[:, 0], arr[:, 1], "o-", color=C_CORAL, label="first peak $t_1$")
    ax.semilogx(arr[:, 0], arr[:, 2], "s-", color=C_AMBER, label="valley $t_v$")
    ax.semilogx(arr[:, 0], arr[:, 3], "^-", color=C_TEAL, label="second peak $t_2$")
    ax.set_xlabel(r"$\beta$"); ax.set_ylabel("modes needed for 1%")
    ax.set_ylim(0, 40)
    ax.set_title("(b) truncation certificates\n$k_{1\\%}$ per feature ($N=100$, $d=4$)")
    ax.legend(frameon=False)
    # (c) channel mass vs time-localized mass
    ax = axes[2]
    bs2 = np.logspace(-3, -1.45, 16)
    pis, masses = [], []
    for b in bs2:
        a = q / (b * (1 - q))
        pis.append(rho / (a + L))
        spec, F, f = evaluate(N, q, b, (L + d) % N)
        masses.append(float(F[: f.t_valley].sum()) if f.t_valley else np.nan)
    ax.semilogx(bs2, pis, "-", color=C_TEAL, lw=1.8,
                label=r"$\pi_{sc}=\rho/(a+L)$ (channel mass, exact)")
    ax.semilogx(bs2, masses, "o--", color=C_CORAL, ms=4,
                label="mass before valley (measured)")
    ax.set_xlabel(r"$\beta$"); ax.set_ylabel("probability mass")
    ax.set_title("(c) shortcut-channel mass vs\ntime-localized first-peak mass")
    ax.legend(frameon=False, fontsize=7.5)
    # (d) example curve with features
    ax = axes[3]
    b0 = 0.01
    spec, F, f = evaluate(N, q, b0, (L + d) % N)
    ts = np.arange(1, len(F) + 1)
    ax.loglog(ts, F, "-", color=C_TEAL, lw=1.6, label="$F(t)$ exact")
    order = np.argsort(spec.lams)[::-1]
    ax.loglog(ts, np.abs(spec.kappas[order][0]) * spec.lams[order][0] ** (ts - 1.0),
              "--", color=C_GRAY, lw=1.3, label=r"mode 1: $B_1 s_1^{t-1}$")
    for tt, mk, lab in ((f.t1, "o", "$t_1$"), (f.t_valley, "v", "$t_v$"), (f.t2, "^", "$t_2$")):
        ax.plot([tt], [F[tt - 1]], mk, ms=6, color=C_CORAL)
        ax.annotate(lab, (tt, F[tt - 1]), textcoords="offset points",
                    xytext=(4, 6), fontsize=8)
    ax.set_xlabel("$t$"); ax.set_ylabel("$F(t)$")
    ax.set_xlim(1, 2e4); ax.set_ylim(1e-7, 0.05)
    ax.set_title(f"(d) example: $N=100$, $\\beta={b0}$, $d=4$\n"
                 "capture peak / valley / diffusive peak")
    ax.legend(frameon=False, fontsize=7.5, loc="lower left")
    fig.suptitle("F3  Amplitude flows and feature-resolved attribution  ($q=2/3$, antipodal shortcut $u\\to v$, C.2 clear classifier)", y=1.0, fontsize=10)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"dpma_fig3_amplitudes_attribution.{ext}")
    plt.close(fig)
    print("F3 done")


# --------------------------------------------------- F4 boundary-law collapse
A_FIT = {3: 9.087, 4: 12.168}    # 1/N-extrapolated lower-edge constants (round-2 audit)
PLATEAU = 3.1475                 # valley-bound upper-edge plateau constant


def fig4():
    base = [r for r in load_csv(ART / "data" / "dpma_boundary_refined.csv")
            if r["window"] == "1"]
    large = []
    for nm in ("dpma_boundary_refined_largeN.csv", "dpma_boundary_refined_largeN2.csv"):
        pl = ART / "data" / nm
        if pl.exists():
            large += [r for r in load_csv(pl) if r["window"] == "1"]
    # largeN lower edges are left-censored at the coarse-grid floor (6.3e-5)
    # for N >= 400; use them ONLY for the upper-edge panel.
    ref = base
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6))
    colors = {3: C_TEAL, 4: C_CORAL, 5: C_PURPLE}

    def rows_for(d):
        rb = sorted((r for r in ref if int(r["d"]) == d), key=lambda r: int(r["N"]))
        Ns = np.array([int(r["N"]) for r in rb])
        blo = np.array([float(r["beta_lo"]) for r in rb])
        bhi = np.array([float(r["beta_hi"]) for r in rb])
        return Ns, blo, bhi

    ax = axes[0]
    for d in (3, 4, 5):
        Ns, blo, _ = rows_for(d)
        ax.plot(Ns, blo * Ns**2, "o-", color=colors[d], ms=4, label=f"$d={d}$")
        if d in A_FIT:
            ax.axhline(A_FIT[d], color=colors[d], ls="--", lw=1.0)
    ax.set_xlabel("$N$"); ax.set_ylabel(r"$\beta_{\rm lo}\,N^2$")
    ax.set_ylim(0, 60)
    ax.set_title("(a) lower edge: $\\beta_{\\rm lo}N^2\\to A(d)$ (1/N convergence)\n"
                 "dashed: fitted $A(3)=9.087$, $A(4)=12.168$; binding $h_2/h_1{=}10$\n"
                 "(near $N_{\\min}$ the valley condition binds first)", fontsize=8.5)
    ax.legend(frameon=False)

    ax = axes[1]
    for d in (3, 4):
        rb = sorted((r for r in base + large if int(r["d"]) == d),
                    key=lambda r: int(r["N"]))
        Ns = np.array([int(r["N"]) for r in rb])
        bhi = np.array([float(r["beta_hi"]) for r in rb])
        ax.plot(Ns, bhi * Ns, "o-", color=colors[d], ms=4, label=f"$d={d}$")
    ax.axhline(PLATEAU, color=C_GRAY, ls="--", lw=1.2)
    ax.annotate("plateau 3.1475(5)\n(valley-bound branch)", (90, PLATEAU),
                textcoords="offset points", xytext=(0, 8), fontsize=8)
    ax.annotate("$h_2/h_1{=}0.1$-bound branch:\nedge collapses beyond $N^*(d)$",
                (420, 2.55), fontsize=8)
    ax.set_xlabel("$N$"); ax.set_ylabel(r"$\beta_{\rm hi}\,N$")
    ax.set_title("(b) upper edge: two branches with binding switch at\n"
                 "$N^*(3)\\approx360$, $N^*(4)\\approx450$ "
                 "(beyond: $\\beta_{\\rm hi}N^2\\approx1.0$–$1.1\\times10^3$)", fontsize=8.5)
    ax.legend(frameon=False)

    ax = axes[2]
    for d in (3, 4, 5):
        Ns, blo, bhi = rows_for(d)
        ax.fill_between(Ns, blo * (1 - q) * Ns / q, bhi * (1 - q) * Ns / q,
                        color=colors[d], alpha=0.18)
        ax.plot(Ns, blo * (1 - q) * Ns / q, "-", color=colors[d], lw=1.2, label=f"$d={d}$")
        ax.plot(Ns, bhi * (1 - q) * Ns / q, "-", color=colors[d], lw=1.2)
    ax.axhline(PLATEAU / 2, color=C_GRAY, ls="--", lw=1.2)
    ax.annotate(r"$b=1.574$ (plateau)", (60, PLATEAU / 2),
                textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax.set_yscale("log")
    ax.set_xlabel("$N$"); ax.set_ylabel(r"$b=\beta(1-q)N/q$")
    ax.set_title("(c) the window in collapse units\n"
                 "$A(d)/(2N)\\lesssim b\\lesssim1.574$ for $N_{\\min}\\ll N<N^*$", fontsize=8.5)
    ax.legend(frameon=False)
    fig.suptitle("F4  Boundary laws of the clear-double-peak window "
                 "(bisection-refined edges, C.2 classifier; $q=2/3$, antipodal shortcut $u\\to v$)",
                 y=1.0, fontsize=10)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"dpma_fig4_boundary_collapse.{ext}")
    plt.close(fig)
    print("F4 done")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
