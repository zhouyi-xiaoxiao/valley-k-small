#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm, colors

from beta_sweep_peaks_tail import build_params, aw_pmf


def parse_beta_list(args):
    if args.betas is not None and len(args.betas) > 0:
        return [float(x) for x in args.betas]
    return list(np.linspace(args.beta_min, args.beta_max, args.beta_num))


def plot_all_betas(N, Ks, betas, q, rho, mode, max_steps_aw, max_t_plot, outpath):
    Ks = list(Ks)
    betas = list(betas)
    nrows = len(Ks)
    fig, axes = plt.subplots(nrows, 1, figsize=(8.2, 3.6 * nrows), dpi=180, sharex=True)
    if nrows == 1:
        axes = [axes]

    norm = colors.Normalize(vmin=min(betas), vmax=max(betas)) if betas else None
    cmap = cm.get_cmap("viridis")

    for ax, K in zip(axes, Ks):
        f_max = 0.0
        for beta in betas:
            params = build_params(N, K, beta, q, rho, mode)
            f, meta = aw_pmf(params, max_steps=int(max_steps_aw))
            max_t = min(int(max_t_plot), len(f))
            t = np.arange(1, max_t + 1)
            f_plot = f[:max_t]
            f_max = max(f_max, float(np.max(f_plot)))
            color = cmap(norm(beta)) if norm else None
            ax.plot(t, f_plot, lw=1.1, alpha=0.9, color=color, label=f"{beta:g}")
        ax.set_yscale("log")
        ax.set_ylabel("f(t)")
        ax.set_title(f"Exact AW pmf across betas (N={N}, K={K}, q={q:.3g}, rho={rho:.3g})")
        ax.grid(True, which="both", linestyle="--", linewidth=0.4, alpha=0.5)
        if f_max > 0:
            ax.set_ylim(max(f_max * 1e-3, 1e-12), f_max * 1.2)

    axes[-1].set_xlabel("t")

    if norm:
        sm = cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=axes, fraction=0.02, pad=0.02)
        cbar.set_label("beta")

    fig.tight_layout()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--Ks", type=int, nargs="+", default=[2, 4])
    p.add_argument("--q", type=float, default=2/3)
    p.add_argument("--rho", type=float, default=1.0)
    p.add_argument("--mode", type=str, default="lazy_selfloop")
    p.add_argument("--betas", type=float, nargs="*", default=None)
    p.add_argument("--beta-min", type=float, default=0.0)
    p.add_argument("--beta-max", type=float, default=0.2)
    p.add_argument("--beta-num", type=int, default=21)
    p.add_argument("--max-steps-aw", type=int, default=4000)
    p.add_argument("--max-t-plot", type=int, default=2000)
    p.add_argument("--out", type=str, required=True)
    args = p.parse_args()

    betas = parse_beta_list(args)
    outpath = Path(args.out).expanduser().resolve()
    plot_all_betas(
        N=int(args.N),
        Ks=args.Ks,
        betas=betas,
        q=float(args.q),
        rho=float(args.rho),
        mode=str(args.mode),
        max_steps_aw=int(args.max_steps_aw),
        max_t_plot=int(args.max_t_plot),
        outpath=outpath,
    )
    print(f"Wrote: {outpath}")


if __name__ == "__main__":
    main()
