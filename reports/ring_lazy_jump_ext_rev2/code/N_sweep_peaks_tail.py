#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import jumpover_bimodality_pipeline as jp
from beta_sweep_peaks_tail import build_params, detect_peaks_and_valley, tail_gamma, aw_pmf


def compute_one(N, K, beta, q, rho, mode, max_steps_aw, hmin, second_rel_height):
    params = build_params(N, K, beta, q, rho, mode)
    max_steps = int(max_steps_aw)
    f, meta = aw_pmf(params, max_steps=max_steps)
    t1, tv, t2 = detect_peaks_and_valley(f, hmin=float(hmin), second_rel_height=float(second_rel_height))
    if t2 is None or (t2 is not None and t2 >= int(0.9 * max_steps)):
        max_steps = int(max_steps * 3)
        f, meta = aw_pmf(params, max_steps=max_steps)
        t1, tv, t2 = detect_peaks_and_valley(f, hmin=float(hmin), second_rel_height=float(second_rel_height))
    h1 = float(f[t1 - 1]) if t1 is not None else np.nan
    h2 = float(f[t2 - 1]) if t2 is not None else np.nan
    hv = float(f[tv - 1]) if tv is not None else np.nan

    g = tail_gamma(params)
    paper_bimodal = (t2 is not None)

    return {
        "N": int(N),
        "K": int(K),
        "beta": float(beta),
        "t1": t1, "tv": tv, "t2": t2,
        "h1": h1, "hv": hv, "h2": h2,
        "tail_gamma": float(g),
        "aw_mass_in_window": float(np.sum(f)),
        "paper_bimodal": bool(paper_bimodal),
    }


def plot_vs_N(df, ycol, outpath, title, logy=True):
    plt.figure(figsize=(8, 4.5), dpi=180)
    for K, g in df.groupby("K"):
        plt.plot(g["N"], g[ycol], marker="o", linewidth=1, label=f"K={K}")
    plt.xlabel("N")
    plt.ylabel(ycol)
    plt.title(title)
    if logy:
        plt.yscale("log")
    plt.grid(True, which="both", linestyle="--", linewidth=0.4, alpha=0.5)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--K", type=int, nargs="+", default=[2, 4])
    p.add_argument("--beta", type=float, required=True)
    p.add_argument("--q", type=float, default=2/3)
    p.add_argument("--rho", type=float, default=1.0)
    p.add_argument("--mode", type=str, default="lazy_selfloop", choices=["lazy_selfloop", "lazy_equal"])

    p.add_argument("--N-min", type=int, default=50)
    p.add_argument("--N-max", type=int, default=300)
    p.add_argument("--N-step", type=int, default=2)
    p.add_argument("--only-even", action="store_true")

    p.add_argument("--max-steps-aw", type=int, default=4000)
    p.add_argument("--hmin", type=float, default=1e-12)
    p.add_argument("--second-rel-height", type=float, default=0.01)

    p.add_argument("--outdir", type=str, required=True)
    args = p.parse_args()

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    Ns = list(range(args.N_min, args.N_max + 1, args.N_step))
    if args.only_even:
        Ns = [N for N in Ns if N % 2 == 0]

    rows = []
    for K in args.K:
        for N in Ns:
            rows.append(compute_one(N, K, args.beta, args.q, args.rho, args.mode,
                                    args.max_steps_aw, args.hmin, args.second_rel_height))

    df = pd.DataFrame(rows).sort_values(["K", "N"]).reset_index(drop=True)
    csv_path = outdir / f"N_sweep_metrics_beta{args.beta:g}.csv"
    df.to_csv(csv_path, index=False)

    plot_vs_N(df, "t1", outdir / f"t1_vs_N_beta{args.beta:g}.png", "t1 vs N", logy=True)
    plot_vs_N(df, "t2", outdir / f"t2_vs_N_beta{args.beta:g}.png", "t2 vs N", logy=True)
    plot_vs_N(df, "h1", outdir / f"h1_vs_N_beta{args.beta:g}.png", "peak1 height vs N", logy=True)
    plot_vs_N(df, "h2", outdir / f"h2_vs_N_beta{args.beta:g}.png", "peak2 height vs N", logy=True)
    plot_vs_N(df, "tail_gamma", outdir / f"tail_gamma_vs_N_beta{args.beta:g}.png", "tail gamma vs N", logy=True)

    print(f"Wrote: {csv_path}")


if __name__ == "__main__":
    main()
