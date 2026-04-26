#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lazy_ring_aw_chebyshev import fpt_pmf_aw
from lazy_ring_flux_bimodality import fpt_pmf_flux_ring
from valley_study import build_graph, coarsegrain_two_steps, exact_first_absorption_aw
from valley_study import detect_peaks_fig3


def strict_local_peaks(f: np.ndarray, *, thresh: float) -> list[tuple[int, float]]:
    peaks: list[tuple[int, float]] = []
    T = int(f.size)
    for i in range(T):
        left = float(f[i - 1]) if i - 1 >= 0 else 0.0
        right = float(f[i + 1]) if i + 1 < T else 0.0
        fi = float(f[i])
        if fi > left and fi > right and fi >= thresh:
            peaks.append((i + 1, fi))
    return peaks


def main() -> None:
    outdir = REPO_ROOT / "figures" / "lazy_ring_flux_bimodality"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / "k2_valley_report_vs_lazy_contrast.pdf"

    # -----------------------
    # Left: valley_report model (non-lazy K-neighbour ring, add one directed edge and renormalize at source)
    # -----------------------
    # Paper convention in valley/ring_valley_en.tex: even N, start n0=1, target n=N/2, directed shortcut (n0+5)->(n+1).
    N_v = 100
    K_v = 2
    g = build_graph(N=N_v, K=K_v, directed_shortcut=True, shortcut_offset=5)
    A = exact_first_absorption_aw(g, rho=1.0, max_steps=2000)
    A_c = coarsegrain_two_steps(A)  # parity fix for K=2 in valley/ring_valley_en.tex
    peaks_c = detect_peaks_fig3(A_c, min_height=1e-7, second_rel_height=0.01)

    # -----------------------
    # Right: lazy-ring selfloop model used in this repo's k=1/K=2 report
    # -----------------------
    # Match the *geometry* of valley_report (u=n0+5 -> v=target+1), but keep the lazy/selfloop probability model.
    N = 100
    q = 2.0 / 3.0  # equal-prob baseline
    p_sc = 0.02 * (1.0 - q)  # beta=0.02
    start = 1
    target = N // 2  # 50
    u = start + 5  # 6
    v = target + 1  # 51

    t_plot = 2000
    f_aw, aw_params = fpt_pmf_aw(
        N=N, q=q, p=p_sc, start=start, target=target, u=u, v=v, t_max=t_plot, oversample=8, r_pow10=18.0
    )
    f_aw = np.maximum(f_aw, 0.0)
    f_flux, surv = fpt_pmf_flux_ring(
        N,
        q,
        start,
        target,
        model="selfloop",
        u=u,
        v=v,
        p=p_sc,
        Tmax=400_000,
        eps_surv=1e-14,
    )
    f_flux = f_flux[:t_plot]
    peaks_lazy = strict_local_peaks(f_flux, thresh=1e-7)
    top2_lazy = sorted(peaks_lazy, key=lambda x: -x[1])[:2]
    top2_lazy = sorted(top2_lazy, key=lambda x: x[0])

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(11.2, 3.6))

    # Left panel: coarse-grained A(t) from valley_report model
    x0 = np.arange(1, A_c.size + 1, dtype=int)
    ax0.plot(x0, A_c, ls="none", marker=".", ms=2.0, color="C0")
    if peaks_c:
        tpk, hpk = peaks_c[0]
        ax0.axvline(tpk, color="C3", ls="--", lw=1.2, alpha=0.8)
        ax0.scatter([tpk], [hpk], s=40, color="C3", zorder=4)
        ax0.text(tpk, hpk, f" peak bin={tpk}", ha="left", va="bottom", color="C3", fontsize=9)
    ax0.set_title(
        "valley_report model (non-lazy)\n"
        "K=2, directed shortcut 6→(N/2+1), peaks after 2-step coarsegrain",
        fontsize=10,
    )
    ax0.set_xlabel("coarse time bin (pairs of steps)")
    ax0.set_ylabel("A(t) (first absorption pmf)")
    ax0.grid(True, alpha=0.2)

    # Right panel: lazy model (AW vs flux) and annotate two dominant peaks
    x1 = np.arange(1, t_plot + 1, dtype=int)
    ax1.bar(x1, f_aw, width=1.0, color="C1", alpha=0.25, label="AW inversion (analytic $\\~F$)")
    ax1.plot(x1, f_flux, ls="none", marker="o", ms=1.8, color="C0", label="flux (time-domain)")
    for tpk, hpk in top2_lazy:
        ax1.axvline(tpk, color="C3", ls="--", lw=1.0, alpha=0.75)
        ax1.scatter([tpk], [hpk], s=36, color="C3", zorder=5)
        ax1.text(tpk, hpk, f" t={tpk}", ha="left", va="bottom", color="C3", fontsize=9)
    ax1.set_title(
        f"lazy selfloop model (equal-prob q=2/3)\n"
        f"N=100, u=6→v=51, p={p_sc:.6g} (AW m={aw_params.m}, r={aw_params.r:.5f})",
        fontsize=10,
    )
    ax1.set_xlabel("t")
    ax1.set_ylabel("f(t) (FPT pmf)")
    ax1.grid(True, alpha=0.2)
    ax1.legend(frameon=False, fontsize=9)

    fig.suptitle("K=2 contrast: same shortcut geometry, different probability model → bimodality can disappear/appear", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(outpath)
    plt.close(fig)

    print(f"wrote {outpath}")
    print(f"[valley_report] coarse_peaks={peaks_c[:3]}")
    print(f"[lazy model] mass≈{float(np.sum(f_flux)):.6f} surv={surv:.2e} top2={top2_lazy}")


if __name__ == '__main__':
    main()
