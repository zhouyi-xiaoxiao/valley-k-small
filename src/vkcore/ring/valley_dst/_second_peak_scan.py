#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import platform
import shutil
import subprocess
import sys
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

FIG_DIR = REPORT_ROOT / "figures" / "second_peak_scan"
DATA_DIR = REPORT_ROOT / "data" / "second_peak_scan"


def wrap_paper(i: int, N: int) -> int:
    """Wrap integer index into {1,..,N} using paper indexing."""
    return ((i - 1) % N) + 1


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


def copy_latest(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _ring_neighbors_internal(src: int, N: int, K: int) -> List[int]:
    k = K // 2
    out: List[int] = []
    for r in range(1, k + 1):
        out.append((src + r) % N)
        out.append((src - r) % N)
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
    Build a K-neighbour ring lattice with one directed shortcut sc_src -> sc_dst.

    Important: the shortcut must NOT duplicate an existing ring neighbour of sc_src,
    otherwise deg(sc_src) stays K and the AW/defect formula used here is not valid.
    """
    if K % 2 != 0:
        raise ValueError("Model assumes K = 2k is even.")
    if not (1 <= n0_paper <= N and 1 <= target_paper <= N):
        raise ValueError("n0_paper/target_paper must be in 1..N.")
    if not (1 <= sc_src_paper <= N and 1 <= sc_dst_paper <= N):
        raise ValueError("sc_src_paper/sc_dst_paper must be in 1..N.")
    if sc_src_paper == sc_dst_paper:
        raise ValueError("Shortcut endpoints must be distinct.")

    n0 = n0_paper - 1
    target = target_paper - 1
    sc_src = sc_src_paper - 1
    sc_dst = sc_dst_paper - 1

    k = K // 2
    neigh: List[set[int]] = [set() for _ in range(N)]
    for i in range(N):
        for r in range(1, k + 1):
            neigh[i].add((i + r) % N)
            neigh[i].add((i - r) % N)

    ring_neigh_src = set(_ring_neighbors_internal(sc_src, N, K))
    if sc_dst in ring_neigh_src:
        raise ValueError(
            f"Invalid shortcut: sc_dst (paper={sc_dst_paper}) is already a ring neighbour "
            f"of sc_src (paper={sc_src_paper}) for K={K}."
        )

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
        # Keep the same meaning as valley_study.exact_first_absorption_aw:
        # sc_v -> sc_u is the directed shortcut.
        sc_u=sc_dst,
        sc_v=sc_src,
        neigh_pad=neigh_pad,
        deg=deg,
        src=np.asarray(src_list, dtype=np.int32),
        dst=np.asarray(dst_list, dtype=np.int32),
        w=np.asarray(w_list, dtype=np.float64),
    )


def extract_peak_info(
    peaks: Sequence[Tuple[int, float]],
) -> Tuple[Optional[int], Optional[float], Optional[int], Optional[float]]:
    t1 = int(peaks[0][0]) if len(peaks) >= 1 else None
    h1 = float(peaks[0][1]) if len(peaks) >= 1 else None
    t2 = int(peaks[1][0]) if len(peaks) >= 2 else None
    h2 = float(peaks[1][1]) if len(peaks) >= 2 else None
    return t1, h1, t2, h2


def compute_A_and_peaks(
    graph: vs.GraphData,
    *,
    rho: float,
    max_steps: int,
    min_height: float,
    second_rel_height: float,
) -> Dict[str, object]:
    A = vs.exact_first_absorption_aw(graph, rho=rho, max_steps=max_steps)
    A = np.maximum(A, 0.0)
    A_use = vs.coarsegrain_two_steps(A) if graph.K == 2 else A

    peaks_all = vs.detect_peaks_fig3(A_use, min_height=min_height, second_rel_height=0.0)
    peaks_fig3 = vs.detect_peaks_fig3(
        A_use, min_height=min_height, second_rel_height=second_rel_height
    )

    t1_all, h1_all, t2_all, h2_all = extract_peak_info(peaks_all)
    t1, h1, t2, h2 = extract_peak_info(peaks_fig3)

    return {
        "A": A_use,
        "peaks_all": peaks_all,
        "peaks_fig3": peaks_fig3,
        "bimodal_fig3": bool(len(peaks_fig3) >= 2),
        "t1_all": t1_all,
        "h1_all": h1_all,
        "t2_all": t2_all,
        "h2_all": h2_all,
        "t1": t1,
        "h1": h1,
        "t2": t2,
        "h2": h2,
        "h2_over_h1": (float(h2 / h1) if (h1 is not None and h2 is not None and h1 > 0) else None),
    }


def _int_list_from_range_args(
    *,
    default_min: int,
    default_max: int,
    arg_list: Optional[List[int]],
    arg_min: Optional[int],
    arg_max: Optional[int],
    arg_step: int,
) -> List[int]:
    if arg_list:
        return [int(x) for x in arg_list]
    lo = default_min if arg_min is None else int(arg_min)
    hi = default_max if arg_max is None else int(arg_max)
    step = max(1, int(arg_step))
    if hi < lo:
        lo, hi = hi, lo
    return list(range(lo, hi + 1, step))


def plot_peak2_vs_x(
    *,
    xs: Sequence[int],
    h2s: Sequence[Optional[float]],
    is_bimodal: Sequence[bool],
    xlabel: str,
    title: str,
    baseline_x: Optional[int],
    outpath: Path,
) -> None:
    xs_arr = np.asarray(xs, dtype=np.int32)
    h2_arr = np.array([0.0 if v is None else float(v) for v in h2s], dtype=np.float64)
    mask = np.asarray(is_bimodal, dtype=bool)

    fig, ax = plt.subplots(figsize=(7.4, 3.8), dpi=170)
    if (~mask).any():
        ax.scatter(xs_arr[~mask], h2_arr[~mask], s=18, alpha=0.7, label="no 2nd peak (Fig.3 rule)")
    if mask.any():
        ax.scatter(xs_arr[mask], h2_arr[mask], s=22, alpha=0.9, label="2nd peak (Fig.3 rule)")
    if baseline_x is not None:
        ax.axvline(int(baseline_x), lw=1.2, ls="--", alpha=0.7, color="gray")
        ax.text(
            int(baseline_x),
            float(h2_arr.max() * 0.95) if h2_arr.size else 0.0,
            "baseline",
            rotation=90,
            va="top",
            ha="right",
            fontsize=8,
            color="gray",
        )
    ax.set_xlabel(xlabel)
    ax.set_ylabel("second peak height $A(t_2)$")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_peak_times_vs_x(
    *,
    xs: Sequence[int],
    t1s: Sequence[Optional[int]],
    t2s: Sequence[Optional[int]],
    is_bimodal: Sequence[bool],
    xlabel: str,
    title: str,
    baseline_x: Optional[int],
    outpath: Path,
) -> None:
    xs_arr = np.asarray(xs, dtype=np.int32)
    t1_arr = np.array([np.nan if v is None else float(v) for v in t1s], dtype=np.float64)
    t2_arr = np.array([np.nan if v is None else float(v) for v in t2s], dtype=np.float64)
    mask = np.asarray(is_bimodal, dtype=bool)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.4, 5.2), dpi=170, sharex=True)

    if mask.any():
        ax1.scatter(xs_arr[mask], t1_arr[mask], s=22, alpha=0.9, label="$t_1$ (1st peak)")
        ax2.scatter(
            xs_arr[mask],
            t2_arr[mask],
            s=22,
            alpha=0.9,
            color="tab:orange",
            label="$t_2$ (2nd peak)",
        )

    if baseline_x is not None:
        for ax in (ax1, ax2):
            ax.axvline(int(baseline_x), lw=1.2, ls="--", alpha=0.7, color="gray")

    ax1.set_ylabel("first peak time $t_1$")
    ax2.set_ylabel("second peak time $t_2$")
    ax2.set_xlabel(xlabel)
    ax1.grid(True, alpha=0.25)
    ax2.grid(True, alpha=0.25)
    ax1.legend(frameon=False, loc="best")
    ax2.legend(frameon=False, loc="best")

    fig.suptitle(title)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(outpath)
    plt.close(fig)


def plot_examples(
    *,
    curves: Dict[int, np.ndarray],
    peaks_by_x: Dict[int, Dict[str, object]],
    xlabel: str,
    title: str,
    max_t_plot: int,
    outpath: Path,
) -> None:
    """Gallery plot for many representative curves."""
    xs = list(curves.keys())
    if not xs:
        return

    n = len(xs)
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(ncols * 3.8, nrows * 2.6),
        dpi=170,
        squeeze=False,
    )
    axes_flat = axes.ravel()

    for ax, x in zip(axes_flat, xs):
        A = curves[x]
        t = np.arange(1, len(A) + 1, dtype=np.int32)
        info = peaks_by_x.get(x, {})
        t2 = info.get("t2")
        h2 = info.get("h2")
        subtitle = f"{xlabel}={x}"
        if t2 is not None and h2 is not None:
            subtitle += f"  ($t_2$={int(t2)}, $A(t_2)$={float(h2):.3g})"
        ax.plot(t[:max_t_plot], A[:max_t_plot], lw=1.8)
        ax.set_xscale("log")
        ax.grid(True, which="both", alpha=0.22)
        ax.set_title(subtitle, fontsize=8)

    for ax in axes_flat[len(xs) :]:
        ax.axis("off")

    fig.suptitle(title, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(outpath)
    plt.close(fig)


def select_example_xs(
    *,
    rows: Sequence[Dict[str, object]],
    x_field: str,
    baseline_x: Optional[int],
    n_examples: int,
    n_no_second: int,
) -> List[int]:
    if n_examples <= 0:
        return []

    xs_all = [int(r[x_field]) for r in rows]
    xs_set = set(xs_all)

    selected: List[int] = []
    if baseline_x is not None and int(baseline_x) in xs_set:
        selected.append(int(baseline_x))

    with_second = [r for r in rows if r.get("h2") is not None]
    without_second = [r for r in rows if r.get("h2") is None]

    with_second.sort(key=lambda r: float(r["h2"]))
    without_second.sort(key=lambda r: int(r[x_field]))

    remaining = max(0, int(n_examples) - len(selected))
    take_no = min(int(n_no_second), remaining, len(without_second))
    take_yes = max(0, remaining - take_no)

    if with_second and take_yes > 0:
        idxs = np.linspace(0, len(with_second) - 1, num=min(take_yes, len(with_second)))
        for i in idxs.astype(int):
            selected.append(int(with_second[int(i)][x_field]))

    for r in without_second[:take_no]:
        selected.append(int(r[x_field]))

    # Deduplicate while preserving order
    out: List[int] = []
    seen: set[int] = set()
    for x in selected:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def write_top_table_tex(
    *,
    rows: Sequence[Dict[str, object]],
    x_field: str,
    x_label: str,
    outpath: Path,
    top_n: int = 10,
) -> None:
    have_second = [r for r in rows if r.get("t2") is not None and r.get("h2") is not None]
    have_second.sort(key=lambda r: float(r["h2"]), reverse=True)
    have_second = have_second[: int(top_n)]

    lines: List[str] = []
    lines.append(r"\begin{tabular}{r r r r r}")
    lines.append(r"\hline")
    lines.append(rf"{x_label} & $t_1$ & $A(t_1)$ & $t_2$ & $A(t_2)$ \\")
    lines.append(r"\hline")
    for r in have_second:
        x = int(r[x_field])
        t1 = int(r["t1"])
        h1 = float(r["h1"])
        t2 = int(r["t2"])
        h2 = float(r["h2"])
        lines.append(f"{x} & {t1} & {h1:.6g} & {t2} & {h2:.6g} \\\\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    outpath.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Scan second-peak height while fixing start node n0, using AW inversion (exact). "
            "Default: N=100, K=6, n0=1, target=N/2, source=n0+5, scan shortcut destination."
        )
    )
    p.add_argument("--run-id", type=str, default=None, help="run identifier; default is a timestamp")
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--K", type=int, default=6)
    p.add_argument("--n0", type=int, default=1, help="start node n0 (paper indexing, 1..N)")
    p.add_argument("--target", type=int, default=None, help="absorbing target (paper indexing, 1..N)")
    p.add_argument("--rho", type=float, default=1.0)
    p.add_argument("--max-steps", type=int, default=2000)
    p.add_argument("--min-height", type=float, default=1e-7)
    p.add_argument("--second-rel-height", type=float, default=0.01)
    p.add_argument("--shortcut-offset", type=int, default=5, help="source = wrap(n0 + offset)")
    p.add_argument("--sc-src", type=int, default=None, help="override shortcut source (paper)")
    p.add_argument("--n-examples", type=int, default=12, help="number of example curves in the gallery plot")
    p.add_argument("--n-no-second-examples", type=int, default=2, help="include up to this many non-bimodal examples")
    p.add_argument("--no-curves", action="store_true", help="do not save full A(t) curves to npz")
    p.add_argument("--no-latest", action="store_true", help="do not update top-level *_results.* and figure PDFs")

    p.add_argument(
        "--scan",
        type=str,
        choices=("shortcut-dst", "target"),
        default="shortcut-dst",
        help="what to scan: shortcut destination or absorbing target",
    )

    # Scan ranges
    p.add_argument("--dst", type=int, nargs="*", default=None, help="explicit shortcut destinations (paper)")
    p.add_argument("--dst-min", type=int, default=None)
    p.add_argument("--dst-max", type=int, default=None)
    p.add_argument("--dst-step", type=int, default=1)

    p.add_argument("--target-list", type=int, nargs="*", default=None, help="explicit targets (paper)")
    p.add_argument("--target-min", type=int, default=None)
    p.add_argument("--target-max", type=int, default=None)
    p.add_argument("--target-step", type=int, default=1)
    p.add_argument(
        "--sc-dst-fixed",
        type=int,
        default=None,
        help="when scanning targets: keep shortcut destination fixed (paper); default is wrap(target+1).",
    )

    p.add_argument("--max-t-plot", type=int, default=500, help="time horizon shown in the example overlay plot")

    args = p.parse_args()

    N = int(args.N)
    K = int(args.K)
    n0_paper = wrap_paper(int(args.n0), N)
    target_paper = wrap_paper(N // 2 if args.target is None else int(args.target), N)
    rho = float(args.rho)
    max_steps = int(args.max_steps)

    if args.sc_src is None:
        sc_src_paper = wrap_paper(n0_paper + int(args.shortcut_offset), N)
    else:
        sc_src_paper = wrap_paper(int(args.sc_src), N)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    prefix = f"N{N}K{K}_n0_{n0_paper}_target_{target_paper}_scsrc_{sc_src_paper}"
    run_id = str(args.run_id).strip() if args.run_id is not None else default_run_id()
    run_prefix = f"{prefix}__{run_id}"

    fig_run_dir = FIG_DIR / prefix / run_id
    data_run_dir = DATA_DIR / prefix / run_id
    fig_run_dir.mkdir(parents=True, exist_ok=True)
    data_run_dir.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, object]] = []
    rows_json: List[Dict[str, object]] = []
    A_by_x: Dict[int, np.ndarray] = {}
    peak_info_by_x: Dict[int, Dict[str, object]] = {}
    skipped: List[Dict[str, object]] = []

    if args.scan == "shortcut-dst":
        dsts = _int_list_from_range_args(
            default_min=1,
            default_max=N,
            arg_list=args.dst,
            arg_min=args.dst_min,
            arg_max=args.dst_max,
            arg_step=args.dst_step,
        )

        baseline_dst_paper = wrap_paper(target_paper + 1, N)
        xlabel = "shortcut dst (paper index)"
        x_field = "sc_dst_paper"
        baseline_x = baseline_dst_paper

        for sc_dst_paper_raw in dsts:
            sc_dst_paper = wrap_paper(int(sc_dst_paper_raw), N)
            try:
                g = build_graph_directed_shortcut(
                    N=N,
                    K=K,
                    n0_paper=n0_paper,
                    target_paper=target_paper,
                    sc_src_paper=sc_src_paper,
                    sc_dst_paper=sc_dst_paper,
                )
            except ValueError as e:
                skipped.append({"sc_dst_paper": sc_dst_paper, "reason": str(e)})
                continue

            out = compute_A_and_peaks(
                g,
                rho=rho,
                max_steps=max_steps,
                min_height=float(args.min_height),
                second_rel_height=float(args.second_rel_height),
            )

            row = {
                "sc_dst_paper": sc_dst_paper,
                "target_paper": target_paper,
                "n0_paper": n0_paper,
                "sc_src_paper": sc_src_paper,
                "bimodal_fig3": bool(out["bimodal_fig3"]),
                "t1": out["t1"],
                "h1": out["h1"],
                "t2": out["t2"],
                "h2": out["h2"],
                "h2_over_h1": out["h2_over_h1"],
                "t1_all": out["t1_all"],
                "h1_all": out["h1_all"],
                "t2_all": out["t2_all"],
                "h2_all": out["h2_all"],
            }
            rows.append(row)
            row_json = dict(row)
            row_json["peaks_all"] = out["peaks_all"]
            row_json["peaks_fig3"] = out["peaks_fig3"]
            rows_json.append(row_json)
            A_by_x[sc_dst_paper] = out["A"]
            peak_info_by_x[sc_dst_paper] = out

        rows.sort(key=lambda r: int(r["sc_dst_paper"]))
        rows_json.sort(key=lambda r: int(r["sc_dst_paper"]))

        xs = [int(r["sc_dst_paper"]) for r in rows]
        h2s = [r["h2"] for r in rows]
        t1s = [r["t1"] for r in rows]
        t2s = [r["t2"] for r in rows]
        bim = [bool(r["bimodal_fig3"]) for r in rows]

        plot_peak2_vs_x(
            xs=xs,
            h2s=h2s,
            is_bimodal=bim,
            xlabel=xlabel,
            title=f"Second-peak height vs shortcut destination (N={N}, K={K}, n0={n0_paper}, src={sc_src_paper}, target={target_paper})",
            baseline_x=baseline_dst_paper,
            outpath=fig_run_dir / f"{run_prefix}_peak2_vs_dst.pdf",
        )

        plot_peak_times_vs_x(
            xs=xs,
            t1s=t1s,
            t2s=t2s,
            is_bimodal=bim,
            xlabel=xlabel,
            title="Peak times among bimodal cases (Fig.3 rule)",
            baseline_x=baseline_dst_paper,
            outpath=fig_run_dir / f"{run_prefix}_peak_times_vs_dst.pdf",
        )

        selected_unique = select_example_xs(
            rows=rows,
            x_field=x_field,
            baseline_x=baseline_dst_paper,
            n_examples=int(args.n_examples),
            n_no_second=int(args.n_no_second_examples),
        )
        curves = {x: A_by_x[x] for x in selected_unique if x in A_by_x}
        plot_examples(
            curves=curves,
            peaks_by_x=peak_info_by_x,
            xlabel="dst",
            title=f"Example $A(t)$ curves (fixed n0={n0_paper}, target={target_paper}, src={sc_src_paper})",
            max_t_plot=max(10, int(args.max_t_plot)),
            outpath=fig_run_dir / f"{run_prefix}_examples.pdf",
        )

        write_top_table_tex(
            rows=rows,
            x_field=x_field,
            x_label="dst",
            outpath=data_run_dir / f"{run_prefix}_top_table.tex",
            top_n=10,
        )

    else:
        targets = _int_list_from_range_args(
            default_min=1,
            default_max=N,
            arg_list=args.target_list,
            arg_min=args.target_min,
            arg_max=args.target_max,
            arg_step=args.target_step,
        )
        xlabel = "target (paper index)"
        x_field = "target_paper"
        baseline_x = target_paper

        for target_paper_raw in targets:
            target_here = wrap_paper(int(target_paper_raw), N)
            if args.sc_dst_fixed is None:
                sc_dst_paper = wrap_paper(target_here + 1, N)
            else:
                sc_dst_paper = wrap_paper(int(args.sc_dst_fixed), N)

            try:
                g = build_graph_directed_shortcut(
                    N=N,
                    K=K,
                    n0_paper=n0_paper,
                    target_paper=target_here,
                    sc_src_paper=sc_src_paper,
                    sc_dst_paper=sc_dst_paper,
                )
            except ValueError as e:
                skipped.append({"target_paper": target_here, "reason": str(e)})
                continue

            out = compute_A_and_peaks(
                g,
                rho=rho,
                max_steps=max_steps,
                min_height=float(args.min_height),
                second_rel_height=float(args.second_rel_height),
            )

            row = {
                "target_paper": target_here,
                "sc_dst_paper": sc_dst_paper,
                "n0_paper": n0_paper,
                "sc_src_paper": sc_src_paper,
                "bimodal_fig3": bool(out["bimodal_fig3"]),
                "t1": out["t1"],
                "h1": out["h1"],
                "t2": out["t2"],
                "h2": out["h2"],
                "h2_over_h1": out["h2_over_h1"],
                "t1_all": out["t1_all"],
                "h1_all": out["h1_all"],
                "t2_all": out["t2_all"],
                "h2_all": out["h2_all"],
            }
            rows.append(row)
            row_json = dict(row)
            row_json["peaks_all"] = out["peaks_all"]
            row_json["peaks_fig3"] = out["peaks_fig3"]
            rows_json.append(row_json)
            A_by_x[target_here] = out["A"]
            peak_info_by_x[target_here] = out

        rows.sort(key=lambda r: int(r["target_paper"]))
        rows_json.sort(key=lambda r: int(r["target_paper"]))
        xs = [int(r["target_paper"]) for r in rows]
        h2s = [r["h2"] for r in rows]
        bim = [bool(r["bimodal_fig3"]) for r in rows]

        plot_peak2_vs_x(
            xs=xs,
            h2s=h2s,
            is_bimodal=bim,
            xlabel=xlabel,
            title=f"Second-peak height vs absorbing target (N={N}, K={K}, n0={n0_paper}, src={sc_src_paper})",
            baseline_x=target_paper,
            outpath=fig_run_dir / f"{run_prefix}_peak2_vs_target.pdf",
        )

        selected_unique = select_example_xs(
            rows=rows,
            x_field=x_field,
            baseline_x=target_paper,
            n_examples=int(args.n_examples),
            n_no_second=int(args.n_no_second_examples),
        )
        curves = {x: A_by_x[x] for x in selected_unique if x in A_by_x}
        plot_examples(
            curves=curves,
            peaks_by_x=peak_info_by_x,
            xlabel="target",
            title=f"Example $A(t)$ curves (fixed n0={n0_paper}, src={sc_src_paper}; shortcut dst rule applied)",
            max_t_plot=max(10, int(args.max_t_plot)),
            outpath=fig_run_dir / f"{run_prefix}_examples.pdf",
        )

        write_top_table_tex(
            rows=rows,
            x_field=x_field,
            x_label="target",
            outpath=data_run_dir / f"{run_prefix}_top_table_targets.tex",
            top_n=10,
        )

    # Save curves (AW-exact A(t)) so the run is reproducible without recomputation.
    if rows and not args.no_curves:
        xs_sorted = [int(r[x_field]) for r in rows]
        xs_have: List[int] = []
        curves_list: List[np.ndarray] = []
        for x in xs_sorted:
            a = A_by_x.get(int(x))
            if a is None:
                continue
            xs_have.append(int(x))
            curves_list.append(a)
        if curves_list:
            lens = {int(a.size) for a in curves_list}
            if len(lens) == 1:
                A_mat = np.stack(curves_list, axis=0).astype(np.float64, copy=False)
            else:
                max_len = max(lens)
                A_mat = np.full((len(curves_list), max_len), np.nan, dtype=np.float64)
                for i, a in enumerate(curves_list):
                    A_mat[i, : a.size] = a
            np.savez_compressed(
                data_run_dir / f"{run_prefix}_curves.npz",
                x=np.asarray(xs_have, dtype=np.int32),
                A=A_mat,
            )

    # Structured JSON record for every run.
    payload = {
        "run": {
            "id": run_id,
            "created_at_utc": utc_timestamp(),
            "platform": platform.platform(),
            "python": sys.version.splitlines()[0],
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
            "git_commit": git_commit_hash(REPO_ROOT),
        },
        "params": {
            "N": N,
            "K": K,
            "rho": rho,
            "max_steps": max_steps,
            "min_height": float(args.min_height),
            "second_rel_height": float(args.second_rel_height),
            "n0_paper": n0_paper,
            "target_paper": target_paper,
            "sc_src_paper": sc_src_paper,
            "scan": str(args.scan),
            "x_field": x_field,
            "x_label": xlabel,
            "baseline_x": baseline_x,
            "selected_examples": selected_unique if rows else [],
        },
        "rows": rows_json,
        "skipped": skipped,
    }
    (data_run_dir / f"{run_prefix}_results.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    if rows:
        fieldnames = sorted(rows[0].keys())
        with (data_run_dir / f"{run_prefix}_results.csv").open(
            "w", encoding="utf-8", newline=""
        ) as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow(r)

    if not args.no_latest:
        # Stable "latest" copies for convenience / existing report links.
        for fp in fig_run_dir.glob(f"{run_prefix}_*.pdf"):
            copy_latest(fp, FIG_DIR / fp.name.replace(f"{run_prefix}_", f"{prefix}_"))
        for fp in data_run_dir.glob(f"{run_prefix}_*"):
            copy_latest(fp, DATA_DIR / fp.name.replace(f"{run_prefix}_", f"{prefix}_"))

    print(f"Saved figures to: {fig_run_dir}")
    print(f"Saved data to: {data_run_dir}")


if __name__ == "__main__":
    main()
