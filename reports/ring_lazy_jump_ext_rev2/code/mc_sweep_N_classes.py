#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext_rev2
# -*- coding: utf-8 -*-

import argparse
import json
import re
import sys
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


CANON_CLASSES = ["class_C0J0", "class_C1pJ0", "class_C0J1p", "class_C1pJ1p"]
WINDOWS = ["peak1", "valley", "peak2", "other"]


def normalize_window(x: str) -> str:
    s = str(x).strip().lower()
    if "peak1" in s or s in ("t1", "p1", "first_peak"):
        return "peak1"
    if "peak2" in s or s in ("t2", "p2", "second_peak"):
        return "peak2"
    if "valley" in s or s in ("tv", "v"):
        return "valley"
    if "other" in s:
        return "other"
    return s


def normalize_class(x: str):
    s = str(x)
    if re.search(r"c0\s*j0", s, re.I) or "C0J0" in s or "c0j0" in s:
        return "class_C0J0"
    if "C1pJ0" in s or "c1pj0" in s:
        return "class_C1pJ0"
    if "C0J1p" in s or "c0j1p" in s or "C0J1" in s or "c0j1" in s:
        return "class_C0J1p"
    if "C1pJ1p" in s or "c1pj1p" in s or ("C1" in s and "J1" in s):
        return "class_C1pJ1p"
    return None


def find_summary(prefix: Path):
    cand = []
    cand += list(prefix.parent.glob(prefix.name + "*summary*.csv"))
    cand += list(prefix.parent.glob(prefix.name + "*summary*.json"))
    if not cand:
        cand += list(prefix.parent.glob("*summary*.csv"))
        cand += list(prefix.parent.glob("*summary*.json"))
    if not cand:
        return None
    cand_csv = [p for p in cand if p.suffix.lower() == ".csv"]
    if cand_csv:
        return sorted(cand_csv)[0]
    return sorted(cand)[0]


def extract_from_summary_csv(path: Path):
    df = pd.read_csv(path)
    cols_lower = {c.lower(): c for c in df.columns}

    window_col = None
    for key in ["window", "region", "bucket"]:
        if key in cols_lower:
            window_col = cols_lower[key]
            break
    if window_col is None:
        for c in df.columns:
            if "window" in c.lower():
                window_col = c
                break

    class_col = None
    prob_col = None
    for c in df.columns:
        if c.lower() in ("class", "traj_class", "trajectory_class") or "class" in c.lower():
            class_col = c
        if c.lower() in ("prob", "p", "fraction", "ratio", "share") or "prob" in c.lower():
            prob_col = c

    if window_col is not None and class_col is not None and prob_col is not None:
        out = []
        for _, r in df.iterrows():
            w = normalize_window(r[window_col])
            cl = normalize_class(r[class_col])
            if cl is None:
                continue
            out.append((w, cl, float(r[prob_col])))
        return out

    if window_col is not None:
        class_cols = []
        for c in df.columns:
            cl = normalize_class(c)
            if cl is not None:
                class_cols.append((c, cl))
        if class_cols:
            out = []
            for _, r in df.iterrows():
                w = normalize_window(r[window_col])
                vals = [float(r[c]) for c, _ in class_cols]
                s = float(np.sum(vals))
                norm = s if s > 1.5 else 1.0
                for (c, cl), v in zip(class_cols, vals):
                    out.append((w, cl, float(v / norm)))
            return out

    # one-row wide
    if len(df) >= 1:
        r0 = df.iloc[0].to_dict()
        out = []
        for c, v in r0.items():
            m = re.search(r"(peak1|valley|peak2|other).*?(C0J0|C1pJ0|C0J1p|C1pJ1p)", str(c), re.I)
            if m:
                w = normalize_window(m.group(1))
                cl = normalize_class(m.group(2))
                if cl:
                    out.append((w, cl, float(v)))
        if out:
            byw = {}
            for w, cl, v in out:
                byw.setdefault(w, []).append(v)
            normed = []
            for w, cl, v in out:
                s = sum(byw[w])
                norm = s if s > 1.5 else 1.0
                normed.append((w, cl, v / norm))
            return normed

    raise RuntimeError(f"Unrecognized summary CSV format: {path}")


def extract_from_summary_json(path: Path):
    obj = json.loads(path.read_text(encoding="utf-8"))
    flat = []

    def rec(x, path_):
        if isinstance(x, dict):
            for k, v in x.items():
                rec(v, path_ + [str(k)])
        elif isinstance(x, list):
            for i, v in enumerate(x):
                rec(v, path_ + [str(i)])
        else:
            if isinstance(x, (int, float)) and np.isfinite(x):
                flat.append((path_, float(x)))

    rec(obj, [])
    out = []
    for path_, val in flat:
        joined = "/".join(path_)
        w = None
        for ww in WINDOWS:
            if ww in joined.lower():
                w = ww
                break
        if w is None:
            continue
        cl = normalize_class(joined)
        if cl is None:
            for cc in CANON_CLASSES:
                token = cc.replace("class_", "")
                if token.lower() in joined.lower():
                    cl = cc
                    break
        if cl is None:
            continue
        out.append((w, cl, val))

    if not out:
        raise RuntimeError(f"Could not extract window/class from summary JSON: {path}")

    byw = {}
    for w, cl, v in out:
        byw.setdefault(w, []).append(v)
    normed = []
    for w, cl, v in out:
        s = sum(byw[w])
        norm = s if s > 1.5 else 1.0
        normed.append((w, cl, v / norm))
    return normed


def extract_probs(summary_path: Path):
    if summary_path.suffix.lower() == ".csv":
        triples = extract_from_summary_csv(summary_path)
    else:
        triples = extract_from_summary_json(summary_path)
    out = {(w, cl): 0.0 for w in WINDOWS for cl in CANON_CLASSES}
    for w, cl, v in triples:
        w = normalize_window(w)
        if w in WINDOWS and cl in CANON_CLASSES:
            out[(w, cl)] = float(v)
    return out


def discover_flag(help_text: str, candidates):
    for c in candidates:
        if c in help_text:
            return c
    return None


def build_analyze_cmd(python_exe: str, pipeline_path: Path, help_text: str, args_dict: dict):
    flagN = discover_flag(help_text, ["--N", "--n"])
    flagK = discover_flag(help_text, ["--K", "--k"])
    flagBeta = discover_flag(help_text, ["--beta"])
    flagQ = discover_flag(help_text, ["--q"])
    flagRho = discover_flag(help_text, ["--rho"])
    flagMode = discover_flag(help_text, ["--mode"])
    flagOut = discover_flag(help_text, ["--out-prefix", "--out_prefix", "--out"])
    flagWalkers = discover_flag(help_text, ["--n-walkers", "--n_walkers", "--walkers", "--nwalkers"])
    flagSeed = discover_flag(help_text, ["--seed"])
    flagExact = discover_flag(help_text, ["--exact-method", "--exact_method"])
    flagMaxSteps = discover_flag(help_text, ["--max-steps-aw", "--max_steps_aw", "--max-steps", "--max_steps"])
    flagDeltaFrac = discover_flag(help_text, ["--delta-frac", "--delta_frac"])
    flagHmin = discover_flag(help_text, ["--hmin"])
    flagSecond = discover_flag(help_text, ["--second-rel-height", "--second_rel_height"])

    if not all([flagN, flagK, flagBeta, flagQ, flagRho, flagMode, flagOut]):
        raise RuntimeError("Cannot auto-detect required flags from pipeline analyze --help.")

    cmd = [python_exe, str(pipeline_path), "analyze"]

    def add(flag, value):
        if flag and value is not None:
            cmd.extend([flag, str(value)])

    add(flagN, args_dict["N"])
    add(flagK, args_dict["K"])
    add(flagBeta, args_dict["beta"])
    add(flagQ, args_dict["q"])
    add(flagRho, args_dict["rho"])
    add(flagMode, args_dict["mode"])
    add(flagOut, args_dict["out_prefix"])

    add(flagWalkers, args_dict.get("n_walkers"))
    add(flagSeed, args_dict.get("seed"))
    add(flagExact, args_dict.get("exact_method"))
    add(flagMaxSteps, args_dict.get("max_steps"))
    add(flagDeltaFrac, args_dict.get("delta_frac"))
    add(flagHmin, args_dict.get("hmin"))
    add(flagSecond, args_dict.get("second_rel_height"))

    return cmd


def plot_window(df, window, outpath_prefix):
    sub = df[df["window"] == window].copy()
    sub = sub.sort_values(["N", "K", "class"])

    plt.figure(figsize=(8, 4.8), dpi=180)
    for (K, cl), g in sub.groupby(["K", "class"]):
        g = g.sort_values("N")
        plt.plot(g["N"], g["prob"], marker="o", linewidth=1, label=f"K={K} {cl}")
    plt.xlabel("N")
    plt.ylabel("P(class | window)")
    plt.ylim(-0.02, 1.02)
    plt.title(f"Trajectory class probabilities vs N   (window={window})")
    plt.grid(True, linestyle="--", linewidth=0.4, alpha=0.5)
    plt.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig(outpath_prefix.with_suffix(".png"))
    plt.close()


def plot_aux(df_aux, window, outpath_prefix):
    sub = df_aux[df_aux["window"] == window].copy()
    sub = sub.sort_values(["N", "K"])

    plt.figure(figsize=(8, 4.8), dpi=180)
    for (K, metric), g in sub.groupby(["K", "metric"]):
        g = g.sort_values("N")
        plt.plot(g["N"], g["value"], marker="o", linewidth=1, label=f"K={K} {metric}")
    plt.xlabel("N")
    plt.ylabel("conditional probability")
    plt.ylim(-0.02, 1.02)
    plt.title(f"P(C>=1|window), P(J>=1|window) vs N   (window={window})")
    plt.grid(True, linestyle="--", linewidth=0.4, alpha=0.5)
    plt.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig(outpath_prefix.with_suffix(".png"))
    plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--beta", type=float, required=True)
    p.add_argument("--Ks", type=int, nargs="+", default=[2, 4])
    p.add_argument("--q", type=float, default=2/3)
    p.add_argument("--rho", type=float, default=1.0)
    p.add_argument("--mode", type=str, default="lazy_selfloop")

    p.add_argument("--N-min", type=int, default=50)
    p.add_argument("--N-max", type=int, default=300)
    p.add_argument("--N-step", type=int, default=10)
    p.add_argument("--only-even", action="store_true")

    p.add_argument("--n-walkers", type=int, default=200000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--exact-method", type=str, default="aw")
    p.add_argument("--max-steps-aw", type=int, default=4000)
    p.add_argument("--delta-frac", type=float, default=0.05)
    p.add_argument("--hmin", type=float, default=1e-12)
    p.add_argument("--second-rel-height", type=float, default=0.01)

    p.add_argument("--outdir", type=str, required=True)
    args = p.parse_args()

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    cases_dir = outdir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    Ns = list(range(args.N_min, args.N_max + 1, args.N_step))
    if args.only_even:
        Ns = [N for N in Ns if N % 2 == 0]

    pipeline_path = Path(__file__).resolve().parent / "jumpover_bimodality_pipeline.py"
    if not pipeline_path.exists():
        raise RuntimeError(f"Cannot find pipeline at {pipeline_path}")

    help_run = subprocess.run([sys.executable, str(pipeline_path), "analyze", "--help"],
                              capture_output=True, text=True)
    help_text = help_run.stdout + "\n" + help_run.stderr

    rows_long = []
    rows_aux = []

    for K in args.Ks:
        for N in Ns:
            tag = f"N{N}_K{K}_beta{args.beta:g}"
            out_prefix = cases_dir / tag / tag
            out_prefix.parent.mkdir(parents=True, exist_ok=True)

            summ = find_summary(out_prefix)
            if summ is None:
                cmd = build_analyze_cmd(
                    sys.executable, pipeline_path, help_text,
                    dict(
                        N=N, K=K, beta=args.beta, q=args.q, rho=args.rho, mode=args.mode,
                        out_prefix=str(out_prefix),
                        n_walkers=args.n_walkers, seed=args.seed + 1000 * int(K) + int(N),
                        exact_method=args.exact_method,
                        max_steps=args.max_steps_aw,
                        delta_frac=args.delta_frac,
                        hmin=args.hmin,
                        second_rel_height=args.second_rel_height,
                    )
                )
                print("RUN:", " ".join(cmd))
                rr = subprocess.run(cmd)
                if rr.returncode != 0:
                    raise RuntimeError(f"pipeline analyze failed for {tag}")

                summ = find_summary(out_prefix)
                if summ is None:
                    raise RuntimeError(f"Cannot locate summary file for {tag}")

            probs = extract_probs(summ)
            for w in WINDOWS:
                for cl in CANON_CLASSES:
                    rows_long.append({
                        "N": int(N),
                        "K": int(K),
                        "beta": float(args.beta),
                        "window": w,
                        "class": cl,
                        "prob": float(probs[(w, cl)]),
                        "summary_file": str(summ),
                    })
                pC = float(probs[(w, "class_C1pJ0")] + probs[(w, "class_C1pJ1p")])
                pJ = float(probs[(w, "class_C0J1p")] + probs[(w, "class_C1pJ1p")])
                rows_aux.append(dict(N=int(N), K=int(K), beta=float(args.beta), window=w, metric="P(C>=1|window)", value=pC))
                rows_aux.append(dict(N=int(N), K=int(K), beta=float(args.beta), window=w, metric="P(J>=1|window)", value=pJ))

    df = pd.DataFrame(rows_long).sort_values(["window", "K", "N", "class"]).reset_index(drop=True)
    df_aux = pd.DataFrame(rows_aux).sort_values(["window", "K", "N", "metric"]).reset_index(drop=True)

    df.to_csv(outdir / f"mc_N_sweep_classes_beta{args.beta:g}.csv", index=False)
    df_aux.to_csv(outdir / f"mc_N_sweep_aux_beta{args.beta:g}.csv", index=False)

    for w in WINDOWS:
        plot_window(df, w, outdir / f"classes_{w}_vs_N")
        plot_aux(df_aux, w, outdir / f"aux_{w}_vs_N")

    print("Wrote:", outdir / f"mc_N_sweep_classes_beta{args.beta:g}.csv")
    print("Wrote:", outdir / f"mc_N_sweep_aux_beta{args.beta:g}.csv")


if __name__ == "__main__":
    main()
