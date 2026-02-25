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

from lazy_ring_aw_chebyshev import fpt_pmf_aw
from lazy_ring_flux_bimodality import bimodality_paper, fpt_pmf_flux_ring, local_peaks_strict


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Plot pmf curves for a range of beta values (p = beta*(1-q)) under the selfloop shortcut model.\n"
            "Uses paper-like geometry: start=n0, target=floor(N/2), u=n0+u_offset, v=target+v_offset.\n"
            "Each panel overlays AW inversion (analytic) and flux for validation."
        )
    )
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--q", type=float, default=2.0 / 3.0)
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--u-offset", type=int, default=5)
    p.add_argument("--v-offset", type=int, default=1)
    p.add_argument("--betas", type=str, default="0.002,0.005,0.01,0.02,0.05,0.1")
    p.add_argument("--thresh", type=float, default=1e-7)
    p.add_argument("--tplot", type=int, default=2500)
    p.add_argument("--oversample", type=int, default=8)
    p.add_argument("--r-pow10", type=float, default=18.0)
    return p.parse_args()


def parse_float_list(s: str) -> list[float]:
    out: list[float] = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(float(part))
    return out


def top2_by_height(peaks: list[tuple[int, float]]) -> list[tuple[int, float]]:
    top2 = sorted(peaks, key=lambda x: -x[1])[:2]
    return sorted(top2, key=lambda x: x[0])


def main() -> None:
    args = parse_args()
    N = int(args.N)
    if N < 3:
        raise ValueError("N must be >= 3.")

    q = float(args.q)
    betas = parse_float_list(str(args.betas))
    if len(betas) == 0:
        raise ValueError("Empty --betas list.")

    start = int(args.start) % N
    target = (N // 2) % N
    u = (start + int(args.u_offset)) % N
    v = (target + int(args.v_offset)) % N

    tplot = int(args.tplot)
    thresh = float(args.thresh)

    n = len(betas)
    ncols = 3
    nrows = int(np.ceil(n / ncols))

    outdir = REPO_ROOT / "figures" / "lazy_ring_flux_bimodality"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"lazy_K2_selfloop_beta_sensitivity_N{N}.pdf"

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(4.2 * ncols, 2.9 * nrows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")

    for idx, beta in enumerate(betas):
        ax = axes.flat[idx]
        ax.axis("on")
        p_sc = float(beta) * (1.0 - q)
        if p_sc < 0.0 or p_sc > (1.0 - q) + 1e-15:
            ax.set_title(f"beta={beta:g} (invalid p)", fontsize=9)
            continue

        f_flux, _ = fpt_pmf_flux_ring(
            N,
            q,
            start,
            target,
            model="selfloop",
            u=u,
            v=v,
            p=p_sc,
            Tmax=200_000,
            eps_surv=1e-14,
        )

        f_aw, aw_params = fpt_pmf_aw(
            N=N,
            q=q,
            p=p_sc,
            start=start,
            target=target,
            u=u,
            v=v,
            t_max=tplot,
            oversample=int(args.oversample),
            r_pow10=float(args.r_pow10),
        )
        f_aw = np.maximum(f_aw, 0.0)

        x = np.arange(1, tplot + 1, dtype=int)
        y_aw = f_aw[:tplot]
        y_flux = f_flux[:tplot] if f_flux.size >= tplot else np.pad(f_flux, (0, tplot - f_flux.size))

        ax.bar(x, y_aw, width=0.8, color="C1", alpha=0.35)
        ax.plot(x, y_flux, ls="none", marker=".", ms=1.8, color="C0")
        ax.grid(True, alpha=0.18)

        paper_ok, peaks = bimodality_paper(f_aw, thresh=thresh, second_frac=0.01)
        peaks2 = top2_by_height(local_peaks_strict(f_aw, thresh=thresh)) if paper_ok else None
        if peaks2 is not None:
            for t, h in peaks2:
                if t <= tplot:
                    ax.axvline(t, color="C3", ls="--", lw=1.0, alpha=0.7)

        ax.set_title(
            f"beta={beta:g}, p={p_sc:.4g}, paper={int(paper_ok)}\nAW(m={aw_params.m}, r={aw_params.r:.6f})",
            fontsize=9,
        )
        ax.set_xlabel("t", fontsize=9)
        ax.set_ylabel("f(t)", fontsize=9)

    fig.suptitle(f"paper geometry: N={N}, q={q:.6g}, start={start}, target={target}, u={u}, v={v}", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(outpath)
    plt.close(fig)

    print(f"wrote {outpath}")


if __name__ == "__main__":
    main()
