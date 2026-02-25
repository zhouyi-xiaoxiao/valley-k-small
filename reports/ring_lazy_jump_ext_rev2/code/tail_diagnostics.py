#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from beta_sweep_peaks_tail import build_params, aw_pmf, tail_gamma


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--K", type=int, default=4)
    p.add_argument("--beta", type=float, default=0.02)
    p.add_argument("--q", type=float, default=2/3)
    p.add_argument("--rho", type=float, default=1.0)
    p.add_argument("--mode", type=str, default="lazy_selfloop")
    p.add_argument("--max-steps-aw", type=int, default=8000)
    p.add_argument("--outdir", type=str, required=True)
    args = p.parse_args()

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    params = build_params(args.N, args.K, args.beta, args.q, args.rho, args.mode)
    f, meta = aw_pmf(params, max_steps=int(args.max_steps_aw))
    F = np.cumsum(f)
    S = 1.0 - F
    S = np.clip(S, 1e-300, 1.0)

    g = tail_gamma(params)

    t = np.arange(1, len(f) + 1)
    plt.figure(figsize=(8, 4.8), dpi=180)
    plt.plot(t, np.log(S), linewidth=1)
    plt.xlabel("t")
    plt.ylabel("log S(t)  where S(t)=P(T>t)")
    plt.title(f"log survival;  N={args.N} K={args.K} beta={args.beta:g}  gamma={g:.4g}")
    plt.grid(True, linestyle="--", linewidth=0.4, alpha=0.5)
    plt.tight_layout()
    plt.savefig(outdir / f"log_survival_N{args.N}_K{args.K}_beta{args.beta:g}.png")
    plt.close()

    print("gamma =", g)


if __name__ == "__main__":
    main()
