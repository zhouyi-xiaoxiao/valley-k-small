#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import platform
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_ROOT = REPO_ROOT / "reports" / "ring_valley_dst"

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from vkcore.ring import valley_study as vs

FIG_ROOT = REPORT_ROOT / "figures" / "bimodality_flux_scan"
DATA_ROOT = REPORT_ROOT / "data" / "bimodality_flux_scan"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def default_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def git_commit_hash(repo_root: Path) -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, stderr=subprocess.DEVNULL
        )
        return out.decode("utf-8").strip()
    except Exception:
        return None


def wrap_paper(i: int, N: int) -> int:
    return ((i - 1) % N) + 1


def ring_neighbors_paper(src_paper: int, N: int, K: int) -> List[int]:
    k = K // 2
    out: List[int] = []
    for r in range(1, k + 1):
        out.append(wrap_paper(src_paper + r, N))
        out.append(wrap_paper(src_paper - r, N))
    return out


def build_graph_directed_shortcut(
    *,
    N: int,
    K: int,
    n0_paper: int,
    target_paper: int,
    sc_src_paper: int,
    sc_dst_paper: int,
) -> vs.GraphData:
    """
    K-neighbour ring + one directed shortcut sc_src -> sc_dst.

    Matches the graph convention used by `valley_study.exact_first_absorption_aw`:
    the directed shortcut is encoded as sc_v -> sc_u.
    """
    if K % 2 != 0:
        raise ValueError("Model assumes K = 2k is even.")
    if sc_src_paper == sc_dst_paper:
        raise ValueError("Shortcut endpoints must be distinct.")
    if sc_dst_paper in set(ring_neighbors_paper(sc_src_paper, N, K)):
        raise ValueError(
            f"Invalid shortcut: dst={sc_dst_paper} is already a ring neighbour of src={sc_src_paper} for K={K}."
        )

    n0 = sc_wrap0(n0_paper, N)
    target = sc_wrap0(target_paper, N)
    sc_src = sc_wrap0(sc_src_paper, N)
    sc_dst = sc_wrap0(sc_dst_paper, N)

    k = K // 2
    neigh: List[set[int]] = [set() for _ in range(N)]
    for i in range(N):
        for r in range(1, k + 1):
            neigh[i].add((i + r) % N)
            neigh[i].add((i - r) % N)
    neigh[sc_src].add(sc_dst)

    deg = np.array([len(neigh[i]) for i in range(N)], dtype=np.int16)
    deg_max = int(deg.max())
    neigh_pad = -np.ones((N, deg_max), dtype=np.int16)
    for i in range(N):
        arr = np.fromiter(neigh[i], dtype=np.int16)
        neigh_pad[i, : arr.size] = arr

    src_list: List[int] = []
    dst_list: List[int] = []
    w_list: List[float] = []
    for i in range(N):
        p = 1.0 / float(deg[i])
        for j in neigh[i]:
            src_list.append(i)
            dst_list.append(j)
            w_list.append(p)

    return vs.GraphData(
        N=N,
        K=K,
        n0=n0,
        target=target,
        sc_u=sc_dst,
        sc_v=sc_src,
        neigh_pad=neigh_pad,
        deg=deg,
        src=np.asarray(src_list, dtype=np.int32),
        dst=np.asarray(dst_list, dtype=np.int32),
        w=np.asarray(w_list, dtype=np.float64),
    )


def sc_wrap0(i_paper: int, N: int) -> int:
    return wrap_paper(i_paper, N) - 1


def fpt_pmf_flux(
    graph: vs.GraphData,
    *,
    rho: float,
    max_steps: int,
    eps_stop: float,
) -> Tuple[np.ndarray, float, int]:
    """
    Forward (time-domain) flux algorithm for FPT.

    Returns:
      f : length max_steps, f[t-1] = P(T=t)
      remaining : total transient mass after last computed step (upper bound on tail mass)
      steps_computed : number of steps actually simulated (<= max_steps)
    """
    N = graph.N
    p = np.zeros(N, dtype=np.float64)
    p[graph.n0] = 1.0

    f = np.zeros(int(max_steps), dtype=np.float64)
    remaining = 1.0
    steps = 0
    for t in range(int(max_steps)):
        contrib = p[graph.src] * graph.w
        p_next = np.bincount(graph.dst, weights=contrib, minlength=N).astype(np.float64, copy=False)
        absorb = rho * float(p_next[graph.target])
        f[t] = absorb
        p_next[graph.target] *= (1.0 - rho)

        p = p_next
        remaining = float(p.sum())
        steps = t + 1
        if remaining < eps_stop:
            break
    return f, remaining, steps


def local_peaks_strict(f: np.ndarray, *, thresh: float) -> List[Tuple[int, float]]:
    peaks: List[Tuple[int, float]] = []
    if f.size < 3:
        return peaks
    for i in range(1, f.size - 1):
        if f[i] > f[i - 1] and f[i] > f[i + 1] and f[i] > thresh:
            peaks.append((i + 1, float(f[i])))
    return peaks


@dataclass(frozen=True)
class RobustBimodality:
    ok: bool
    t1: Optional[int]
    h1: Optional[float]
    t2: Optional[int]
    h2: Optional[float]
    sep: Optional[int]
    ratio: Optional[float]
    valley: Optional[float]
    valley_ratio: Optional[float]
    reason: Optional[str]


def bimodality_test_robust(
    f: np.ndarray,
    *,
    min_height: float,
    second_frac: float,
    min_separation: int,
    require_valley: bool,
    valley_frac: float,
) -> RobustBimodality:
    """
    Robust bimodality check:
      1) strict local peaks above min_height
      2) take two highest peaks by height
      3) enforce height ratio, minimal separation, and optional valley depth
    """
    peaks = local_peaks_strict(f, thresh=float(min_height))
    if len(peaks) < 2:
        return RobustBimodality(
            ok=False,
            t1=None,
            h1=None,
            t2=None,
            h2=None,
            sep=None,
            ratio=None,
            valley=None,
            valley_ratio=None,
            reason="fewer than 2 local peaks",
        )

    # Pick peak1 as the highest; pick peak2 as the highest that is sufficiently separated
    peak1 = max(peaks, key=lambda x: x[1])
    candidates = [p for p in peaks if abs(int(p[0]) - int(peak1[0])) >= int(min_separation)]
    if not candidates:
        return RobustBimodality(
            ok=False,
            t1=int(peak1[0]),
            h1=float(peak1[1]),
            t2=None,
            h2=None,
            sep=None,
            ratio=None,
            valley=None,
            valley_ratio=None,
            reason="no sufficiently separated second peak candidate",
        )
    peak2 = max(candidates, key=lambda x: x[1])

    (t1, h1), (t2, h2) = sorted([peak1, peak2], key=lambda x: x[0])

    hmax = max(h1, h2)
    hmin = min(h1, h2)
    if hmin < float(second_frac) * hmax:
        return RobustBimodality(
            ok=False,
            t1=t1,
            h1=h1,
            t2=t2,
            h2=h2,
            sep=t2 - t1,
            ratio=h2 / h1 if h1 > 0 else None,
            valley=None,
            valley_ratio=None,
            reason="second peak too small",
        )

    sep = int(t2 - t1)

    valley: Optional[float] = None
    valley_ratio: Optional[float] = None
    if sep >= 2:
        # open interval (t1, t2) => times t1+1..t2-1 => indices t1..t2-2
        seg = f[t1 : t2 - 1]
        valley = float(np.min(seg)) if seg.size else float(min(h1, h2))
        valley_ratio = float(valley / hmin) if hmin > 0 else None
        if require_valley and valley > float(valley_frac) * hmin:
            return RobustBimodality(
                ok=False,
                t1=t1,
                h1=h1,
                t2=t2,
                h2=h2,
                sep=sep,
                ratio=h2 / h1 if h1 > 0 else None,
                valley=valley,
                valley_ratio=valley_ratio,
                reason="valley not deep enough",
            )

    return RobustBimodality(
        ok=True,
        t1=t1,
        h1=h1,
        t2=t2,
        h2=h2,
        sep=sep,
        ratio=h2 / h1 if h1 > 0 else None,
        valley=valley,
        valley_ratio=valley_ratio,
        reason=None,
    )


@dataclass
class ScanRow:
    dst: int
    valid: bool
    reason_invalid: Optional[str]
    mass: Optional[float]
    remaining: Optional[float]
    steps: Optional[int]
    fig3_bimodal: Optional[bool]
    fig3_t1: Optional[int]
    fig3_h1: Optional[float]
    fig3_t2: Optional[int]
    fig3_h2: Optional[float]
    robust_bimodal: Optional[bool]
    robust_t1: Optional[int]
    robust_h1: Optional[float]
    robust_t2: Optional[int]
    robust_h2: Optional[float]
    robust_sep: Optional[int]
    robust_ratio: Optional[float]
    robust_valley: Optional[float]
    robust_valley_ratio: Optional[float]


def write_scan_csv(rows: Sequence[ScanRow], outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with outpath.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))


def write_bimodal_table_tex(rows: Sequence[ScanRow], outpath: Path) -> None:
    bimodal = [r for r in rows if r.valid and r.robust_bimodal]
    lines: List[str] = []
    lines.append(r"\begin{tabular}{r r r r r r r}")
    lines.append(r"\toprule")
    lines.append(r"$\mathrm{dst}$ & $t_1$ & $t_2$ & $t_2-t_1$ & $A(t_1)$ & $A(t_2)$ & $V$ \\")
    lines.append(r"\midrule")
    for r in sorted(bimodal, key=lambda x: x.dst):
        v = r.robust_valley_ratio
        v_str = f"{v:.3f}" if v is not None else r"--"
        lines.append(
            f"{r.dst} & {r.robust_t1} & {r.robust_t2} & {r.robust_sep} & {r.robust_h1:.6g} & {r.robust_h2:.6g} & {v_str} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("\n".join(lines) + "\n", encoding="utf-8")


def select_examples(dsts: Sequence[int], *, n: int) -> List[int]:
    if not dsts or n <= 0:
        return []
    if len(dsts) <= n:
        return list(dsts)
    idx = np.linspace(0, len(dsts) - 1, n, dtype=int)
    return [int(dsts[i]) for i in idx]


def plot_bimodality_scan(rows: Sequence[ScanRow], *, N: int, K: int, src: int, target: int, outpath: Path) -> None:
    dst_all = np.array([r.dst for r in rows], dtype=int)
    y = np.array([r.robust_h2 if (r.valid and r.robust_bimodal) else 0.0 for r in rows], dtype=float)
    ok = np.array([r.valid and r.robust_bimodal for r in rows], dtype=bool)
    valid = np.array([r.valid for r in rows], dtype=bool)

    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    ax.scatter(dst_all[valid & ~ok], y[valid & ~ok], s=14, label="not bimodal (robust)", alpha=0.9)
    ax.scatter(dst_all[ok], y[ok], s=26, label="bimodal (robust)", alpha=0.95)
    ax.scatter(dst_all[~valid], np.zeros_like(dst_all[~valid]), s=14, label="invalid dst", alpha=0.5)

    ax.axvline(target, color="k", lw=1.0, ls="--", alpha=0.6)
    ax.set_xlabel(r"shortcut destination $\mathrm{dst}$ (paper index)")
    ax.set_ylabel(r"later-peak height $A(t_2)$")
    ax.set_title(f"Bimodality scan via flux (N={N}, K={K}, src={src}, target={target})")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, ncol=3, fontsize=9)

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_peak_times(rows: Sequence[ScanRow], *, N: int, K: int, src: int, target: int, outpath: Path) -> None:
    bimodal = [r for r in rows if r.valid and r.robust_bimodal]
    if not bimodal:
        fig, ax = plt.subplots(figsize=(7.0, 2.4))
        ax.axis("off")
        ax.text(
            0.5,
            0.5,
            "No robust-bimodal dst found under current criteria.",
            ha="center",
            va="center",
            fontsize=11,
        )
        outpath.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(outpath)
        plt.close(fig)
        return
    dst = np.array([r.dst for r in bimodal], dtype=int)
    t1 = np.array([r.robust_t1 for r in bimodal], dtype=int)
    t2 = np.array([r.robust_t2 for r in bimodal], dtype=int)

    fig, axes = plt.subplots(2, 1, figsize=(7.5, 4.5), sharex=True)
    axes[0].scatter(dst, t1, s=22)
    axes[0].set_ylabel(r"$t_1$")
    axes[0].grid(True, alpha=0.25)
    axes[1].scatter(dst, t2, s=22)
    axes[1].set_ylabel(r"$t_2$")
    axes[1].set_xlabel(r"shortcut destination $\mathrm{dst}$ (paper index)")
    axes[1].grid(True, alpha=0.25)
    axes[0].axvline(target, color="k", lw=1.0, ls="--", alpha=0.6)
    axes[1].axvline(target, color="k", lw=1.0, ls="--", alpha=0.6)
    fig.suptitle(f"Peak times among robust-bimodal dst (N={N}, K={K}, src={src}, target={target})")

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_example_curves(
    *,
    exact_by_dst: Dict[int, np.ndarray],
    rows_by_dst: Dict[int, ScanRow],
    dsts: Sequence[int],
    max_t_plot: int,
    N: int,
    K: int,
    src: int,
    target: int,
    outpath: Path,
) -> None:
    if not dsts:
        fig, ax = plt.subplots(figsize=(8.5, 2.4))
        ax.axis("off")
        ax.text(0.5, 0.5, "No examples to plot.", ha="center", va="center", fontsize=11)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(outpath)
        plt.close(fig)
        return
    n = len(dsts)
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(9.5, 2.4 * nrows), squeeze=False)
    for idx, d in enumerate(dsts):
        r = idx // ncols
        c = idx % ncols
        ax = axes[r][c]
        f = exact_by_dst[d][:max_t_plot]
        t = np.arange(1, f.size + 1, dtype=int)
        ax.plot(t, f, lw=1.6)
        row = rows_by_dst[d]
        if row.robust_t1 is not None:
            ax.axvline(row.robust_t1, color="#ff7f0e", lw=1.0, ls="--", alpha=0.9)
        if row.robust_t2 is not None:
            ax.axvline(row.robust_t2, color="#ff7f0e", lw=1.0, ls="--", alpha=0.9)
        ax.set_title(f"dst={d} (t1={row.robust_t1}, t2={row.robust_t2})", fontsize=9)
        ax.set_xlabel("t")
        ax.set_ylabel("f(t)")
        ax.grid(True, alpha=0.2)
        ax.set_xlim(1, max_t_plot)

    for j in range(n, nrows * ncols):
        axes[j // ncols][j % ncols].axis("off")

    fig.suptitle(f"Example f(t) curves (flux) (N={N}, K={K}, src={src}, target={target})", y=0.995)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_aw_vs_flux_overlay(
    *,
    curves: Dict[int, Dict[str, np.ndarray]],
    max_t_plot: int,
    N: int,
    K: int,
    src: int,
    target: int,
    outpath: Path,
) -> None:
    if not curves:
        fig, ax = plt.subplots(figsize=(8.5, 2.4))
        ax.axis("off")
        ax.text(0.5, 0.5, "No AW-vs-flux curves to plot.", ha="center", va="center", fontsize=11)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(outpath)
        plt.close(fig)
        return
    dsts = sorted(curves.keys())
    n = len(dsts)
    ncols = 2
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(9.2, 2.8 * nrows), squeeze=False)
    for idx, d in enumerate(dsts):
        ax = axes[idx // ncols][idx % ncols]
        f_flux = curves[d]["flux"][:max_t_plot]
        f_aw = curves[d]["aw"][:max_t_plot]
        t = np.arange(1, f_flux.size + 1, dtype=int)
        ax.plot(t, f_flux, lw=1.7, label="flux (master eq.)")
        ax.plot(t, f_aw, lw=1.0, ls="--", label="AW inversion")
        err = float(np.max(np.abs(f_aw - f_flux)))
        ax.set_title(f"dst={d}, max|Δ|={err:.2e}", fontsize=9)
        ax.set_xlabel("t")
        ax.set_ylabel("f(t)")
        ax.grid(True, alpha=0.2)
        ax.set_xlim(1, max_t_plot)
        ax.legend(frameon=False, fontsize=8)

    for j in range(n, nrows * ncols):
        axes[j // ncols][j % ncols].axis("off")

    fig.suptitle(f"AW vs flux overlay (N={N}, K={K}, src={src}, target={target})", y=0.995)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Deterministic bimodality scan via time-domain flux (master equation), with optional AW spot-check."
    )
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--K", type=int, default=6)
    p.add_argument("--n0", type=int, default=1)
    p.add_argument("--target", type=int, default=None)
    p.add_argument("--sc-src", type=int, required=True, help="paper shortcut source (src)")
    p.add_argument("--rho", type=float, default=1.0)
    p.add_argument("--max-steps", type=int, default=2000)
    p.add_argument("--eps-stop", type=float, default=1e-14)
    p.add_argument("--dst", type=int, nargs="*", default=None, help="explicit dst list (paper)")
    p.add_argument("--dst-min", type=int, default=1)
    p.add_argument("--dst-max", type=int, default=None)

    p.add_argument("--min-height", type=float, default=1e-7)
    p.add_argument("--second-rel-height", type=float, default=0.01, help="Fig.3 rule: second peak must be >= this fraction of the highest")
    p.add_argument("--second-frac", type=float, default=0.01)
    p.add_argument("--min-sep", type=int, default=None, help="minimum separation (t2-t1); default 2*K")
    p.add_argument("--require-valley", action="store_true", help="enable valley depth check")
    p.add_argument("--valley-frac", type=float, default=0.8, help="require valley <= frac*min(peak heights)")

    p.add_argument("--n-examples", type=int, default=12)
    p.add_argument("--max-t-plot", type=int, default=600)
    p.add_argument("--aw-check", action="store_true", help="compute AW curves for example dsts and plot overlay")
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--no-latest", action="store_true")
    args = p.parse_args()

    N = int(args.N)
    K = int(args.K)
    n0_paper = wrap_paper(int(args.n0), N)
    target_paper = wrap_paper(N // 2 if args.target is None else int(args.target), N)
    sc_src_paper = wrap_paper(int(args.sc_src), N)

    dst_max = N if args.dst_max is None else int(args.dst_max)
    dst_candidates = [wrap_paper(d, N) for d in (args.dst if args.dst else range(int(args.dst_min), dst_max + 1))]
    dst_seen: set[int] = set()
    dst_list: List[int] = []
    for d in dst_candidates:
        if d in dst_seen:
            continue
        dst_seen.add(d)
        dst_list.append(d)

    min_sep = int(args.min_sep) if args.min_sep is not None else int(2 * K)
    require_valley = bool(args.require_valley)

    run_id = str(args.run_id).strip() if args.run_id is not None else default_run_id()
    prefix = f"N{N}K{K}_n0_{n0_paper}_target_{target_paper}_src_{sc_src_paper}"
    fig_run_dir = FIG_ROOT / prefix / "runs" / run_id
    data_run_dir = DATA_ROOT / prefix / "runs" / run_id
    fig_run_dir.mkdir(parents=True, exist_ok=True)
    data_run_dir.mkdir(parents=True, exist_ok=True)

    rows: List[ScanRow] = []
    exact_by_dst: Dict[int, np.ndarray] = {}
    for d in dst_list:
        try:
            g = build_graph_directed_shortcut(
                N=N,
                K=K,
                n0_paper=n0_paper,
                target_paper=target_paper,
                sc_src_paper=sc_src_paper,
                sc_dst_paper=d,
            )
        except ValueError as e:
            rows.append(
                ScanRow(
                    dst=int(d),
                    valid=False,
                    reason_invalid=str(e),
                    mass=None,
                    remaining=None,
                    steps=None,
                    fig3_bimodal=None,
                    fig3_t1=None,
                    fig3_h1=None,
                    fig3_t2=None,
                    fig3_h2=None,
                    robust_bimodal=None,
                    robust_t1=None,
                    robust_h1=None,
                    robust_t2=None,
                    robust_h2=None,
                    robust_sep=None,
                    robust_ratio=None,
                    robust_valley=None,
                    robust_valley_ratio=None,
                )
            )
            continue

        f_flux, remaining, steps = fpt_pmf_flux(g, rho=float(args.rho), max_steps=int(args.max_steps), eps_stop=float(args.eps_stop))
        exact_by_dst[int(d)] = f_flux
        mass = float(f_flux.sum())

        peaks_fig3 = vs.detect_peaks_fig3(
            f_flux, min_height=float(args.min_height), second_rel_height=float(args.second_rel_height)
        )
        fig3_bimodal = len(peaks_fig3) >= 2
        fig3_t1 = int(peaks_fig3[0][0]) if len(peaks_fig3) >= 1 else None
        fig3_h1 = float(peaks_fig3[0][1]) if len(peaks_fig3) >= 1 else None
        fig3_t2 = int(peaks_fig3[1][0]) if len(peaks_fig3) >= 2 else None
        fig3_h2 = float(peaks_fig3[1][1]) if len(peaks_fig3) >= 2 else None

        robust = bimodality_test_robust(
            f_flux,
            min_height=float(args.min_height),
            second_frac=float(args.second_frac),
            min_separation=min_sep,
            require_valley=require_valley,
            valley_frac=float(args.valley_frac),
        )

        rows.append(
            ScanRow(
                dst=int(d),
                valid=True,
                reason_invalid=None,
                mass=mass,
                remaining=float(remaining),
                steps=int(steps),
                fig3_bimodal=bool(fig3_bimodal),
                fig3_t1=fig3_t1,
                fig3_h1=fig3_h1,
                fig3_t2=fig3_t2,
                fig3_h2=fig3_h2,
                robust_bimodal=bool(robust.ok),
                robust_t1=robust.t1,
                robust_h1=robust.h1,
                robust_t2=robust.t2,
                robust_h2=robust.h2,
                robust_sep=robust.sep,
                robust_ratio=robust.ratio,
                robust_valley=robust.valley,
                robust_valley_ratio=robust.valley_ratio,
            )
        )

    if not rows:
        raise SystemExit("No dst rows produced.")

    rows_by_dst = {r.dst: r for r in rows if r.valid}
    robust_bimodal_dsts = sorted([r.dst for r in rows if r.valid and r.robust_bimodal])
    fig3_bimodal_dsts = sorted([r.dst for r in rows if r.valid and r.fig3_bimodal])
    example_dsts = select_examples(robust_bimodal_dsts, n=int(args.n_examples))

    scan_csv = data_run_dir / f"scan__{run_id}.csv"
    write_scan_csv(rows, scan_csv)
    tex_table = data_run_dir / f"bimodal_table__{run_id}.tex"
    write_bimodal_table_tex(rows, tex_table)

    fig_scan = fig_run_dir / f"bimodality_scan__{run_id}.pdf"
    plot_bimodality_scan(rows, N=N, K=K, src=sc_src_paper, target=target_paper, outpath=fig_scan)
    fig_times = fig_run_dir / f"peak_times__{run_id}.pdf"
    plot_peak_times(rows, N=N, K=K, src=sc_src_paper, target=target_paper, outpath=fig_times)
    fig_examples = fig_run_dir / f"example_curves__{run_id}.pdf"
    plot_example_curves(
        exact_by_dst=exact_by_dst,
        rows_by_dst=rows_by_dst,
        dsts=example_dsts,
        max_t_plot=int(args.max_t_plot),
        N=N,
        K=K,
        src=sc_src_paper,
        target=target_paper,
        outpath=fig_examples,
    )

    aw_checks: Dict[int, Dict[str, float]] = {}
    aw_overlay_curves: Dict[int, Dict[str, np.ndarray]] = {}
    fig_aw: Optional[Path] = None
    if bool(args.aw_check) and example_dsts:
        check_dsts = sorted(set(example_dsts + [wrap_paper(target_paper + 1, N), target_paper]))
        for d in check_dsts:
            try:
                g = build_graph_directed_shortcut(
                    N=N,
                    K=K,
                    n0_paper=n0_paper,
                    target_paper=target_paper,
                    sc_src_paper=sc_src_paper,
                    sc_dst_paper=d,
                )
            except ValueError:
                continue
            f_aw = vs.exact_first_absorption_aw(g, rho=float(args.rho), max_steps=int(args.max_steps))
            f_flux = exact_by_dst[d]
            m = min(f_aw.size, f_flux.size)
            err_max = float(np.max(np.abs(f_aw[:m] - f_flux[:m])))
            err_l1 = float(np.sum(np.abs(f_aw[:m] - f_flux[:m])))
            aw_checks[int(d)] = {"max_abs": err_max, "l1": err_l1}
            aw_overlay_curves[int(d)] = {"aw": f_aw, "flux": f_flux}

        fig_aw = fig_run_dir / f"aw_vs_flux__{run_id}.pdf"
        plot_aw_vs_flux_overlay(
            curves=aw_overlay_curves,
            max_t_plot=min(int(args.max_t_plot), int(args.max_steps)),
            N=N,
            K=K,
            src=sc_src_paper,
            target=target_paper,
            outpath=fig_aw,
        )

    results = {
        "run": {
            "id": run_id,
            "created_at_utc": utc_timestamp(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
            "git_commit": git_commit_hash(REPO_ROOT),
        },
        "params": {
            "N": N,
            "K": K,
            "n0_paper": n0_paper,
            "target_paper": target_paper,
            "sc_src_paper": sc_src_paper,
            "rho": float(args.rho),
            "max_steps": int(args.max_steps),
            "eps_stop": float(args.eps_stop),
            "min_height": float(args.min_height),
            "second_rel_height": float(args.second_rel_height),
            "second_frac": float(args.second_frac),
            "min_separation": int(min_sep),
            "require_valley": bool(require_valley),
            "valley_frac": float(args.valley_frac),
        },
        "summary": {
            "n_dst_total": len(dst_list),
            "n_valid": sum(1 for r in rows if r.valid),
            "n_fig3_bimodal": len(fig3_bimodal_dsts),
            "n_robust_bimodal": len(robust_bimodal_dsts),
            "fig3_bimodal_dsts": fig3_bimodal_dsts,
            "robust_bimodal_dsts": robust_bimodal_dsts,
            "example_dsts": example_dsts,
        },
        "aw_check": aw_checks,
        "files": {
            "scan_csv": str(scan_csv.relative_to(REPO_ROOT)),
            "bimodal_table_tex": str(tex_table.relative_to(REPO_ROOT)),
            "fig_bimodality_scan": str(fig_scan.relative_to(REPO_ROOT)),
            "fig_peak_times": str(fig_times.relative_to(REPO_ROOT)),
            "fig_examples": str(fig_examples.relative_to(REPO_ROOT)),
        },
    }
    if bool(args.aw_check) and fig_aw is not None:
        results["files"]["fig_aw_vs_flux"] = str(fig_aw.relative_to(REPO_ROOT))

    results_json = data_run_dir / f"results__{run_id}.json"
    results_json.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    if not args.no_latest:
        latest_fig = FIG_ROOT / prefix / "latest"
        latest_data = DATA_ROOT / prefix / "latest"
        latest_fig.mkdir(parents=True, exist_ok=True)
        latest_data.mkdir(parents=True, exist_ok=True)
        (latest_fig / "bimodality_scan.pdf").write_bytes(fig_scan.read_bytes())
        (latest_fig / "peak_times.pdf").write_bytes(fig_times.read_bytes())
        (latest_fig / "example_curves.pdf").write_bytes(fig_examples.read_bytes())
        if bool(args.aw_check) and fig_aw is not None:
            (latest_fig / "aw_vs_flux.pdf").write_bytes(fig_aw.read_bytes())

        (latest_data / "scan.csv").write_bytes(scan_csv.read_bytes())
        (latest_data / "bimodal_table.tex").write_bytes(tex_table.read_bytes())
        (latest_data / "results.json").write_bytes(results_json.read_bytes())

    print(json.dumps(results["summary"], indent=2))
    print(f"Wrote figures: {fig_run_dir}")
    print(f"Wrote data:    {data_run_dir}")


if __name__ == "__main__":
    main()
