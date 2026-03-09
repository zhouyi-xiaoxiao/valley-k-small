#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_jump_ext
# -*- coding: utf-8 -*-

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Adapt if module name differs
import jumpover_bimodality_pipeline as jp


# -----------------------------
# Params helpers (prefer repo)
# -----------------------------
def build_params(N, K, beta, q, rho, mode,
                 n0_paper=1, target_expr="auto",
                 sc_src_expr="auto+5", sc_dst_expr="auto_target+1",
                 jumpover_absorbs=False):
    """
    Build Params using the repo's paper-index convention.
    If repo lacks these helpers, implement local equivalents matching the report's convention.
    """
    N = int(N)
    n0_paper = int(n0_paper)

    if hasattr(jp, "auto_target_paper") and hasattr(jp, "parse_auto_expr") and hasattr(jp, "paper_to0"):
        auto_target = jp.auto_target_paper(N, n0_paper)
        target_paper = jp.parse_auto_expr(target_expr, N=N, n0_paper=n0_paper, target_paper=auto_target)
        sc_src_paper = jp.parse_auto_expr(sc_src_expr, N=N, n0_paper=n0_paper, target_paper=target_paper)
        sc_dst_paper = jp.parse_auto_expr(sc_dst_expr, N=N, n0_paper=n0_paper, target_paper=target_paper)

        params = jp.Params(
            N=N,
            K=int(K),
            n0=jp.paper_to0(n0_paper, N),
            target=jp.paper_to0(target_paper, N),
            sc_src=jp.paper_to0(sc_src_paper, N),
            sc_dst=jp.paper_to0(sc_dst_paper, N),
            mode=str(mode),
            q=float(q),
            beta=float(beta),
            rho=float(rho),
            jumpover_absorbs=bool(jumpover_absorbs),
        )
        return params

    # Fallback: assume paper index equals 0-index+1 and target at N/2+1 (even N)
    def paper_to0(x, N_):
        return (int(x) - 1) % int(N_)

    # If target_expr == "auto": mimic common convention target = N/2 + 1 (paper indexing)
    if str(target_expr).strip().lower() == "auto":
        target_paper = (N // 2) + 1
    else:
        raise RuntimeError("Repo helper parse_auto_expr missing; please adapt build_params to repo convention.")

    if str(sc_src_expr).startswith("auto+"):
        sc_src_paper = target_paper + int(str(sc_src_expr).split("+", 1)[1])
    else:
        raise RuntimeError("Repo helper parse_auto_expr missing; please adapt sc_src_expr parsing.")

    if str(sc_dst_expr).startswith("auto_target+"):
        sc_dst_paper = target_paper + int(str(sc_dst_expr).split("+", 1)[1])
    else:
        raise RuntimeError("Repo helper parse_auto_expr missing; please adapt sc_dst_expr parsing.")

    params = jp.Params(
        N=N,
        K=int(K),
        n0=paper_to0(n0_paper, N),
        target=paper_to0(target_paper, N),
        sc_src=paper_to0(sc_src_paper, N),
        sc_dst=paper_to0(sc_dst_paper, N),
        mode=str(mode),
        q=float(q),
        beta=float(beta),
        rho=float(rho),
        jumpover_absorbs=bool(jumpover_absorbs),
    )
    return params


# -----------------------------
# Transition / transient Q
# -----------------------------
def build_transition_matrix_dense(params: "jp.Params") -> np.ndarray:
    """
    Prefer repo's builder if available. Otherwise implement dense P for lazy_selfloop.
    """
    for name in ["build_transition_matrix", "build_P", "transition_matrix", "make_transition_matrix"]:
        if hasattr(jp, name):
            return getattr(jp, name)(params)

    N = int(params.N)
    K = int(params.K)
    k = K // 2
    q = float(params.q)
    beta = float(params.beta)
    mode = str(params.mode)

    P = np.zeros((N, N), dtype=float)

    base_self = 1.0 - q
    ring_each = q / float(K)

    sc_src = int(params.sc_src)
    sc_dst = int(params.sc_dst)

    if mode == "lazy_selfloop":
        p = beta * (1.0 - q)
        p = max(0.0, min(p, 1.0 - q))

        # baseline
        for i in range(N):
            P[i, i] += base_self
            for r in range(1, k + 1):
                P[i, (i + r) % N] += ring_each
                P[i, (i - r) % N] += ring_each

        # modify src row
        P[sc_src, sc_src] -= p
        P[sc_src, sc_dst] += p

    elif mode == "lazy_equal":
        # Placeholder fallback; prefer repo definition if present
        p = beta * (1.0 - q)
        p = max(0.0, min(p, 1.0 - q))

        for i in range(N):
            P[i, i] += base_self
            for r in range(1, k + 1):
                P[i, (i + r) % N] += ring_each
                P[i, (i - r) % N] += ring_each

        P[sc_src, sc_src] -= p
        P[sc_src, sc_dst] += p

    else:
        raise ValueError(f"Unknown mode: {mode}")

    # numerical safety
    P[P < 0] = 0.0
    row_sums = P.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    P = P / row_sums
    return P


def transient_Q(params: "jp.Params") -> np.ndarray:
    P = build_transition_matrix_dense(params)
    N = P.shape[0]
    target = int(params.target)
    rho = float(params.rho)

    if rho >= 1.0 - 1e-15:
        keep = [i for i in range(N) if i != target]
        return P[np.ix_(keep, keep)].copy()
    else:
        Q = P.copy()
        Q[target, :] *= (1.0 - rho)
        return Q


def spectral_radius_power_iteration(Q: np.ndarray, iters: int = 2000, tol: float = 1e-12) -> float:
    n = Q.shape[0]
    v = np.ones(n, dtype=float) / n
    lam_old = 0.0
    for _ in range(iters):
        w = Q @ v
        s = float(np.sum(w))
        if s <= 0:
            return 0.0
        v = w / s
        lam = s
        if abs(lam - lam_old) < tol * max(1.0, abs(lam)):
            return float(lam)
        lam_old = lam
    return float(lam_old)


def tail_gamma(params: "jp.Params") -> float:
    Q = transient_Q(params)
    n = Q.shape[0]
    if n <= 600:
        eig = np.linalg.eigvals(Q)
        lam = float(np.max(np.abs(eig)))
    else:
        lam = spectral_radius_power_iteration(Q)
    lam = max(min(lam, 1.0 - 1e-15), 1e-300)
    return -math.log(lam)


# -----------------------------
# Peaks / valley
# -----------------------------
def detect_peaks_and_valley(f: np.ndarray, hmin: float, second_rel_height: float):
    """
    Prefer repo's peak logic. Fallback local.
    f indexed so that f[t-1] = P(T=t).
    Return (t1, tv, t2) with 1-based times.
    """
    if hasattr(jp, "detect_peaks_paper") and hasattr(jp, "first_two_peaks_and_valley"):
        peaks = jp.detect_peaks_paper(f, hmin=hmin, second_rel_height=second_rel_height)
        return jp.first_two_peaks_and_valley(f, peaks)

    T = len(f)
    fp = np.zeros(T + 2, dtype=float)
    fp[1:T+1] = f
    cand = []
    for t in range(1, T+1):
        if fp[t] >= hmin and fp[t] > fp[t-1] and fp[t] > fp[t+1]:
            cand.append(t)
    if not cand:
        return None, None, None

    heights = np.array([f[t-1] for t in cand], dtype=float)
    m = float(np.max(heights))
    cand2 = [t for t in cand if f[t-1] >= second_rel_height * m]
    cand2.sort()
    if len(cand2) < 2:
        return cand2[0], None, None
    t1, t2 = cand2[0], cand2[1]
    if (t2 - t1) >= 2:
        tv = int(np.argmin(f[t1:t2-1]) + (t1+1))
    else:
        tv = None
    return t1, tv, t2


def parse_beta_list(args):
    if args.betas is not None and len(args.betas) > 0:
        return [float(x) for x in args.betas]
    return list(np.linspace(args.beta_min, args.beta_max, args.beta_num))


def aw_pmf(params: "jp.Params", max_steps: int):
    """
    Require repo to expose aw_first_absorption_pmf(params, max_steps).
    If missing, you must refactor repo pipeline to expose it (see adaptation rules).
    """
    if hasattr(jp, "aw_first_absorption_pmf"):
        f, meta = jp.aw_first_absorption_pmf(params, max_steps=int(max_steps))
        return np.asarray(f, dtype=float), meta
    raise RuntimeError("Missing aw_first_absorption_pmf; you must expose it from the repo pipeline.")


def compute_one(N, K, beta, q, rho, mode, max_steps_aw, hmin, second_rel_height):
    params = build_params(N, K, beta, q, rho, mode)
    f, meta = aw_pmf(params, max_steps=int(max_steps_aw))

    t1, tv, t2 = detect_peaks_and_valley(f, hmin=float(hmin), second_rel_height=float(second_rel_height))
    h1 = float(f[t1 - 1]) if t1 is not None else math.nan
    h2 = float(f[t2 - 1]) if t2 is not None else math.nan
    hv = float(f[tv - 1]) if tv is not None else math.nan

    g = tail_gamma(params)

    return {
        "N": int(N),
        "K": int(K),
        "beta": float(beta),
        "t1": t1,
        "tv": tv,
        "t2": t2,
        "h1": h1,
        "hv": hv,
        "h2": h2,
        "h2_over_h1": (h2 / h1) if (not math.isnan(h2) and h1 > 0) else math.nan,
        "hv_over_max": (hv / max(h1, h2)) if (not math.isnan(hv) and max(h1, h2) > 0) else math.nan,
        "tail_gamma": float(g),
        "aw_mass_in_window": float(np.sum(f)),
    }


def plot_peak_heights(df, outpath):
    plt.figure(figsize=(8, 4.5), dpi=180)
    dd = df.melt(id_vars=["beta", "K"], value_vars=["h1", "h2"], var_name="which", value_name="h")
    for (K, which), g in dd.groupby(["K", "which"]):
        g = g.sort_values("beta")
        g_line = g[g["beta"] > 0]
        g_zero = g[g["beta"] == 0]
        line = None
        if not g_line.empty:
            (line,) = plt.plot(g_line["beta"], g_line["h"], marker="o", linewidth=1, label=f"K={K} {which}")
        if not g_zero.empty and g_zero["h"].notna().any():
            color = line.get_color() if line is not None else None
            plt.plot(
                g_zero["beta"],
                g_zero["h"],
                marker="s",
                linestyle="None",
                markersize=5,
                color=color,
                markerfacecolor="none",
                markeredgewidth=1.2,
                label="_nolegend_",
            )
    plt.yscale("log")
    plt.xlabel("beta")
    plt.ylabel(r"peak height $f(t_{\mathrm{peak}})$")
    plt.title("Peak heights vs beta")
    plt.grid(True, which="both", linestyle="--", linewidth=0.4, alpha=0.5)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_peak_times(df, outpath):
    plt.figure(figsize=(8, 4.5), dpi=180)
    dd = df.melt(id_vars=["beta", "K"], value_vars=["t1", "t2"], var_name="which", value_name="t")
    for (K, which), g in dd.groupby(["K", "which"]):
        g = g.sort_values("beta")
        g_line = g[g["beta"] > 0]
        g_zero = g[g["beta"] == 0]
        line = None
        if not g_line.empty:
            (line,) = plt.plot(g_line["beta"], g_line["t"], marker="o", linewidth=1, label=f"K={K} {which}")
        if not g_zero.empty and g_zero["t"].notna().any():
            color = line.get_color() if line is not None else None
            plt.plot(
                g_zero["beta"],
                g_zero["t"],
                marker="s",
                linestyle="None",
                markersize=5,
                color=color,
                markerfacecolor="none",
                markeredgewidth=1.2,
                label="_nolegend_",
            )
    plt.yscale("log")
    plt.xlabel("beta")
    plt.ylabel("peak time (t)")
    plt.title("Peak times vs beta")
    plt.grid(True, which="both", linestyle="--", linewidth=0.4, alpha=0.5)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_tail_gamma(df, outpath):
    plt.figure(figsize=(8, 4.5), dpi=180)
    for K, g in df.groupby("K"):
        plt.plot(g["beta"], g["tail_gamma"], marker="o", linewidth=1, label=f"K={K}")
    plt.yscale("log")
    plt.xlabel("beta")
    plt.ylabel(r"tail decay $\gamma=-\log(\lambda_{\max})$")
    plt.title("Asymptotic tail decay rate vs beta")
    plt.grid(True, which="both", linestyle="--", linewidth=0.4, alpha=0.5)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--Ks", type=int, nargs="+", default=[2, 4])
    p.add_argument("--q", type=float, default=2/3)
    p.add_argument("--rho", type=float, default=1.0)
    p.add_argument("--mode", type=str, default="lazy_selfloop", choices=["lazy_selfloop", "lazy_equal"])

    p.add_argument("--betas", type=float, nargs="*", default=None)
    p.add_argument("--beta-min", type=float, default=0.0)
    p.add_argument("--beta-max", type=float, default=0.2)
    p.add_argument("--beta-num", type=int, default=21)

    p.add_argument("--max-steps-aw", type=int, default=4000)
    p.add_argument("--hmin", type=float, default=1e-12)
    p.add_argument("--second-rel-height", type=float, default=0.01)

    p.add_argument("--outdir", type=str, required=True)
    args = p.parse_args()

    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    betas = parse_beta_list(args)

    rows = []
    for K in args.Ks:
        for beta in betas:
            rows.append(compute_one(args.N, K, beta, args.q, args.rho, args.mode,
                                    args.max_steps_aw, args.hmin, args.second_rel_height))

    df = pd.DataFrame(rows).sort_values(["K", "beta"]).reset_index(drop=True)
    csv_path = outdir / f"beta_sweep_metrics_N{args.N}.csv"
    df.to_csv(csv_path, index=False)

    plot_peak_heights(df, outdir / f"peak_heights_vs_beta_N{args.N}.png")
    plot_peak_times(df, outdir / f"peak_times_vs_beta_N{args.N}.png")
    plot_tail_gamma(df, outdir / f"tail_gamma_vs_beta_N{args.N}.png")

    print(f"Wrote: {csv_path}")


if __name__ == "__main__":
    main()
