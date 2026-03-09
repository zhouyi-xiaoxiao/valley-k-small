#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=str, required=True, help="beta_sweep_metrics_N*.csv")
    p.add_argument("--Ks", type=int, nargs="+", default=[2,4])
    p.add_argument("--macro_ratio", type=float, default=10.0, help="require t2/t1 >= macro_ratio")
    p.add_argument("--hv_over_max", type=float, default=0.6, help="require hv/max(h1,h2) <= this")
    p.add_argument("--min_h2_over_h1", type=float, default=0.05, help="require h2/h1 >= this (avoid invisible 2nd peak)")
    p.add_argument("--fallback_beta", type=float, default=0.02)
    p.add_argument("--out", type=str, default=None, help="write selected beta to text file")
    args = p.parse_args()

    df = pd.read_csv(args.csv)
    # basic sanity
    need_cols = {"beta","K","t1","t2","hv_over_max","h2_over_h1"}
    missing = need_cols - set(df.columns)
    if missing:
        raise RuntimeError(f"Missing columns {missing} in {args.csv}")

    # only consider rows with two peaks
    df2 = df.dropna(subset=["t1","t2"]).copy()
    df2["t2_over_t1"] = df2["t2"] / df2["t1"]

    # filter per K
    good = []
    for K in args.Ks:
        g = df2[df2["K"] == K].copy()
        g = g[(g["t2_over_t1"] >= args.macro_ratio) &
              (g["hv_over_max"] <= args.hv_over_max) &
              (g["h2_over_h1"] >= args.min_h2_over_h1)]
        good.append(g[["beta"]].drop_duplicates())

    if not good:
        sel = args.fallback_beta
    else:
        inter = good[0]
        for g in good[1:]:
            inter = inter.merge(g, on="beta", how="inner")
        if len(inter) == 0:
            sel = args.fallback_beta
        else:
            sel = float(np.min(inter["beta"].values))

    if args.out:
        Path(args.out).write_text(f"{sel:.12g}\n", encoding="utf-8")

    print(f"{sel:.12g}")

if __name__ == "__main__":
    main()
