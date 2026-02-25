#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lazy_ring_aw_chebyshev import fpt_pmf_aw, fpt_pmf_aw_equal4
from lazy_ring_flux_bimodality import fpt_pmf_flux_ring, local_peaks_strict


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Compare the paper-like shortcut geometry under two probability rules:\n"
            "  (A) selfloop model: take p from the self-loop at u and add to u->v\n"
            "  (B) equal4 model: at u, stay/left/right/shortcut each 1/4\n"
            "Plots AW inversion (analytic) with flux cross-check."
        )
    )
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--q", type=float, default=2.0 / 3.0)
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--u-offset", type=int, default=5)
    p.add_argument("--v-offset", type=int, default=1)
    p.add_argument("--beta", type=float, default=0.02, help="selfloop uses p = beta*(1-q)")
    p.add_argument("--tplot", type=int, default=2000)
    p.add_argument("--thresh", type=float, default=1e-7, help="peak threshold for marking")
    return p.parse_args()


def mark_top2(ax: plt.Axes, f: np.ndarray, *, thresh: float, color: str) -> None:
    peaks = local_peaks_strict(f, thresh=thresh)
    top2 = sorted(peaks, key=lambda x: -x[1])[:2]
    for t, h in sorted(top2, key=lambda x: x[0]):
        ax.scatter([t], [h], s=46, color=color, zorder=4)
        ax.axvline(t, color=color, ls="--", lw=1.0, alpha=0.7)
        ax.text(t, h, f" t={t}", va="bottom", ha="left", color=color, fontsize=9)


def main() -> None:
    args = parse_args()
    N = int(args.N)
    q = float(args.q)
    start = int(args.start) % N
    target = (N // 2) % N
    u = (start + int(args.u_offset)) % N
    v = (target + int(args.v_offset)) % N

    p_selfloop = float(args.beta) * (1.0 - q)
    tplot = int(args.tplot)
    thresh = float(args.thresh)

    # --- selfloop model
    f_flux_sl, _ = fpt_pmf_flux_ring(N, q, start, target, model="selfloop", u=u, v=v, p=p_selfloop, Tmax=200_000, eps_surv=1e-14)
    f_aw_sl, aw_sl = fpt_pmf_aw(
        N=N,
        q=q,
        p=p_selfloop,
        start=start,
        target=target,
        u=u,
        v=v,
        t_max=tplot,
        oversample=16,
        r_pow10=18.0,
    )
    f_aw_sl = np.maximum(f_aw_sl, 0.0)

    # --- equal4 model
    f_flux_eq, _ = fpt_pmf_flux_ring(N, q, start, target, model="equal4", u=u, v=v, Tmax=200_000, eps_surv=1e-14)
    f_aw_eq, aw_eq = fpt_pmf_aw_equal4(
        N=N, q=q, start=start, target=target, u=u, v=v, t_max=tplot, oversample=16, r_pow10=18.0
    )
    f_aw_eq = np.maximum(f_aw_eq, 0.0)

    x = np.arange(1, tplot + 1, dtype=int)
    y_sl = f_aw_sl[:tplot]
    y_eq = f_aw_eq[:tplot]

    outdir = REPO_ROOT / "figures" / "lazy_ring_flux_bimodality"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"lazy_K2_paper_geometry_selfloop_vs_equal4_N{N}.pdf"

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12.5, 3.6), sharex=True)

    ax = axes[0]
    ax.bar(x, y_sl, width=0.85, color="C1", alpha=0.35, label="AW (analytic)")
    ax.plot(x, f_flux_sl[:tplot], ls="none", marker=".", ms=2.0, color="C0", label="flux")
    mark_top2(ax, y_sl, thresh=thresh, color="C3")
    ax.set_title(
        f"selfloop model: q={q:.6g}, beta={float(args.beta):.4g} (p={p_selfloop:.4g})\n"
        f"AW(m={aw_sl.m}, r={aw_sl.r:.6f})",
        fontsize=10,
    )
    ax.set_xlabel("t")
    ax.set_ylabel("f(t)")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, fontsize=9, loc="upper right")

    ax = axes[1]
    ax.bar(x, y_eq, width=0.85, color="C1", alpha=0.35, label="AW (analytic)")
    ax.plot(x, f_flux_eq[:tplot], ls="none", marker=".", ms=2.0, color="C0", label="flux")
    mark_top2(ax, y_eq, thresh=thresh, color="C3")
    ax.set_title(
        f"equal4 at u: stay/left/right/shortcut each 1/4\nAW(m={aw_eq.m}, r={aw_eq.r:.6f})",
        fontsize=10,
    )
    ax.set_xlabel("t")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, fontsize=9, loc="upper right")

    fig.suptitle(f"paper geometry: N={N}, start={start}, target={target}, u={u}, v={v}", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(outpath)
    plt.close(fig)

    print(f"wrote {outpath}")


if __name__ == "__main__":
    main()
