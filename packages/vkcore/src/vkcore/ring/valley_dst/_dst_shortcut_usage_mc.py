#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
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

FIG_ROOT = REPORT_ROOT / "figures" / "second_peak_dst_shortcut_usage"
DATA_ROOT = REPORT_ROOT / "data" / "second_peak_dst_shortcut_usage"


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

    The AW/defect formula in valley_study assumes the shortcut adds a new outgoing
    neighbor to sc_src, changing deg(sc_src) from K to K+1. Hence we forbid sc_dst
    being an existing ring neighbor of sc_src.
    """
    if K % 2 != 0:
        raise ValueError("Model assumes K = 2k is even.")
    if not (1 <= n0_paper <= N and 1 <= target_paper <= N):
        raise ValueError("n0_paper/target_paper must be in 1..N.")
    if not (1 <= sc_src_paper <= N and 1 <= sc_dst_paper <= N):
        raise ValueError("sc_src_paper/sc_dst_paper must be in 1..N.")
    if sc_src_paper == sc_dst_paper:
        raise ValueError("Shortcut endpoints must be distinct.")

    if sc_dst_paper in set(ring_neighbors_paper(sc_src_paper, N, K)):
        raise ValueError(
            f"Invalid shortcut: dst={sc_dst_paper} is already a ring neighbour of src={sc_src_paper} for K={K}."
        )

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


def exact_A_and_peaks(
    graph: vs.GraphData,
    *,
    rho: float,
    max_steps: int,
    min_height: float,
    second_rel_height: float,
) -> Tuple[np.ndarray, List[Tuple[int, float]]]:
    A = vs.exact_first_absorption_aw(graph, rho=rho, max_steps=max_steps)
    A = np.maximum(A, 0.0)
    peaks = vs.detect_peaks_fig3(A, min_height=min_height, second_rel_height=second_rel_height)
    return A, peaks


def second_peak_window(
    peaks: Sequence[Tuple[int, float]],
    *,
    delta_frac: float,
) -> Tuple[int, int, int]:
    peaks_t = sorted(peaks, key=lambda x: int(x[0]))
    (t1, _), (t2, _) = peaks_t[0], peaks_t[1]
    delta = max(1, int(delta_frac * (t2 - t1)))
    lo = max(1, int(t2) - delta)
    hi = int(t2) + delta
    return lo, hi, delta


@dataclass(frozen=True)
class ScanRow:
    dst: int
    valid: bool
    reason_invalid: Optional[str]
    bimodal: bool
    t1: Optional[int]
    h1: Optional[float]
    t2: Optional[int]
    h2: Optional[float]
    h2_over_h1: Optional[float]
    delta: Optional[int]
    window_lo: Optional[int]
    window_hi: Optional[int]


def simulate_batch(
    graph: vs.GraphData,
    *,
    n_walkers: int,
    rho: float,
    seed: int,
    track_crossings: bool = True,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    rng = np.random.default_rng(seed)
    pos = np.full(n_walkers, graph.n0, dtype=np.int32)
    active = np.ones(n_walkers, dtype=bool)
    fp_times = np.full(n_walkers, -1, dtype=np.int32)
    crossings = np.zeros(n_walkers, dtype=np.int32) if track_crossings else None

    t = 0
    while active.any():
        idx = np.nonzero(active)[0]
        cur = pos[idx]
        degs = graph.deg[cur].astype(np.float64)
        r = (rng.random(size=idx.size) * degs).astype(np.int32)
        nxt = graph.neigh_pad[cur, r].astype(np.int32, copy=False)
        if track_crossings and crossings is not None:
            cross_mask = (cur == graph.sc_v) & (nxt == graph.sc_u)
            if cross_mask.any():
                crossings[idx[cross_mask]] += 1
        pos[idx] = nxt
        t += 1

        hit = pos[idx] == graph.target
        if hit.any():
            hit_idx = idx[hit]
            if rho >= 1.0:
                absorbed = hit_idx
            else:
                u = rng.random(size=hit_idx.size)
                absorbed = hit_idx[u < rho]
            fp_times[absorbed] = t
            active[absorbed] = False

    return fp_times, crossings


def mc_first_passage_crossings(
    graph: vs.GraphData,
    *,
    n_walkers: int,
    rho: float,
    seed: int,
    batch_size: int = 50_000,
) -> Tuple[np.ndarray, np.ndarray]:
    n_batches = int(np.ceil(n_walkers / batch_size))
    ss = np.random.SeedSequence(seed)
    child_seeds = ss.spawn(n_batches)

    times_list: List[np.ndarray] = []
    crosses_list: List[np.ndarray] = []
    remaining = n_walkers
    for i in range(n_batches):
        n_b = batch_size if remaining > batch_size else remaining
        remaining -= n_b
        s = int(child_seeds[i].generate_state(1, dtype=np.uint64)[0])
        t, c = simulate_batch(graph, n_walkers=n_b, rho=rho, seed=s, track_crossings=True)
        if c is None:
            raise RuntimeError("Expected crossings array.")
        times_list.append(t)
        crosses_list.append(c.astype(np.int32, copy=False))

    return np.concatenate(times_list, axis=0), np.concatenate(crosses_list, axis=0)


def crossing_stats_in_window(times: np.ndarray, crosses: np.ndarray, *, lo: int, hi: int) -> Dict[str, object]:
    mask = (times >= int(lo)) & (times <= int(hi))
    n_in = int(mask.sum())
    if n_in == 0:
        return {
            "n_in_window": 0,
            "frac_in_window": 0.0,
            "frac_no": None,
            "frac_one": None,
            "frac_multi": None,
        }
    c = crosses[mask]
    return {
        "n_in_window": n_in,
        "frac_in_window": float(n_in / float(times.size)),
        "frac_no": float(np.mean(c == 0)),
        "frac_one": float(np.mean(c == 1)),
        "frac_multi": float(np.mean(c >= 2)),
    }


def wilson_interval(phat: float, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    denom = 1.0 + (z * z) / float(n)
    center = (phat + (z * z) / (2.0 * float(n))) / denom
    half = (z / denom) * np.sqrt((phat * (1.0 - phat)) / float(n) + (z * z) / (4.0 * float(n * n)))
    lo = float(max(0.0, center - half))
    hi = float(min(1.0, center + half))
    return lo, hi


def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.size < 2 or y.size < 2:
        return float("nan")
    x = x - x.mean()
    y = y - y.mean()
    denom = float(np.sqrt(np.sum(x * x) * np.sum(y * y)))
    if denom == 0.0:
        return float("nan")
    return float(np.sum(x * y) / denom)


def spearman_r(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.size < 2 or y.size < 2:
        return float("nan")
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    return pearson_r(rx, ry)


def select_representative_dsts(
    *,
    bimodal_rows: Sequence[ScanRow],
    baseline_dst: int,
    target_dst: int,
    n_select: int,
) -> List[int]:
    if not bimodal_rows:
        return []
    rows = list(bimodal_rows)
    rows.sort(key=lambda r: r.dst)

    selected: List[int] = []
    have = {r.dst for r in rows}
    if baseline_dst in have:
        selected.append(int(baseline_dst))
    if target_dst in have:
        selected.append(int(target_dst))

    rows_by_h2 = [r for r in rows if r.h2 is not None]
    rows_by_h2.sort(key=lambda r: float(r.h2))
    if rows_by_h2:
        selected.append(int(rows_by_h2[0].dst))  # min h2
        selected.append(int(rows_by_h2[-1].dst))  # max h2

    rows_by_ratio = [r for r in rows if r.h2_over_h1 is not None]
    rows_by_ratio.sort(key=lambda r: float(r.h2_over_h1))
    if rows_by_ratio:
        selected.append(int(rows_by_ratio[0].dst))  # min ratio
        selected.append(int(rows_by_ratio[-1].dst))  # max ratio

    # Deduplicate while preserving order
    out: List[int] = []
    seen: set[int] = set()
    for d in selected:
        if d in seen:
            continue
        if d in have:
            seen.add(d)
            out.append(d)

    if len(out) >= n_select:
        return out[:n_select]

    # Fill remaining with evenly spaced dst across the bimodal range
    candidates = [r.dst for r in rows if r.dst not in set(out)]
    if not candidates:
        return out
    n_need = n_select - len(out)
    idxs = np.linspace(0, len(candidates) - 1, num=min(n_need, len(candidates)))
    for i in idxs.astype(int):
        out.append(int(candidates[int(i)]))
    return out


def plot_peak2_scan(
    *,
    scan_rows: Sequence[ScanRow],
    selected_dsts: Sequence[int],
    baseline_dst: int,
    title: str,
    outpath: Path,
) -> None:
    rows = list(scan_rows)
    rows.sort(key=lambda r: r.dst)
    xs = np.array([r.dst for r in rows], dtype=np.int32)
    h2 = np.array([0.0 if r.h2 is None else float(r.h2) for r in rows], dtype=np.float64)
    bim = np.array([bool(r.bimodal) for r in rows], dtype=bool)

    fig, ax = plt.subplots(figsize=(7.6, 3.8), dpi=170)
    if (~bim).any():
        ax.scatter(xs[~bim], h2[~bim], s=18, alpha=0.7, label="no 2nd peak (Fig.3 rule)")
    if bim.any():
        ax.scatter(xs[bim], h2[bim], s=22, alpha=0.9, label="2nd peak (Fig.3 rule)")

    for d in selected_dsts:
        ax.scatter([d], [float(h2[rows.index(next(r for r in rows if r.dst == d))])], s=70, facecolors="none", edgecolors="black", linewidths=1.4)

    ax.axvline(int(baseline_dst), lw=1.2, ls="--", alpha=0.75, color="gray")
    ax.text(int(baseline_dst), float(h2.max() * 0.98) if h2.size else 0.0, "baseline", rotation=90, va="top", ha="right", fontsize=8, color="gray")

    ax.set_xlabel("shortcut dst (paper index)")
    ax.set_ylabel("second peak height $A(t_2)$")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, loc="best", fontsize=9)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_peak_times_scan(
    *,
    scan_rows: Sequence[ScanRow],
    selected_dsts: Sequence[int],
    baseline_dst: int,
    title: str,
    outpath: Path,
) -> None:
    rows = [r for r in scan_rows if r.valid]
    rows.sort(key=lambda r: r.dst)

    xs = np.array([r.dst for r in rows], dtype=np.int32)
    bim = np.array([bool(r.bimodal) for r in rows], dtype=bool)
    t1 = np.array([np.nan if r.t1 is None else float(r.t1) for r in rows], dtype=np.float64)
    t2 = np.array([np.nan if r.t2 is None else float(r.t2) for r in rows], dtype=np.float64)

    dst_to_row = {r.dst: r for r in rows}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.6, 5.2), dpi=170, sharex=True)
    if bim.any():
        ax1.scatter(xs[bim], t1[bim], s=22, alpha=0.9, label="$t_1$ (bimodal)")
        ax2.scatter(
            xs[bim],
            t2[bim],
            s=22,
            alpha=0.9,
            color="tab:orange",
            label="$t_2$ (bimodal)",
        )

    # Highlight selected dsts among bimodal set
    for d in selected_dsts:
        r = dst_to_row.get(int(d))
        if r is None or not r.bimodal:
            continue
        ax1.scatter([r.dst], [float(r.t1)], s=70, facecolors="none", edgecolors="black", linewidths=1.4)
        ax2.scatter([r.dst], [float(r.t2)], s=70, facecolors="none", edgecolors="black", linewidths=1.4)

    for ax in (ax1, ax2):
        ax.axvline(int(baseline_dst), lw=1.2, ls="--", alpha=0.75, color="gray")
        ax.grid(True, alpha=0.25)

    ax1.set_ylabel("first peak time $t_1$")
    ax2.set_ylabel("second peak time $t_2$")
    ax2.set_xlabel("shortcut dst (paper index)")
    ax1.legend(frameon=False, loc="best", fontsize=9)
    ax2.legend(frameon=False, loc="best", fontsize=9)
    fig.suptitle(title, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(outpath)
    plt.close(fig)


def plot_exact_gallery(
    *,
    dsts: Sequence[int],
    exact_by_dst: Dict[int, Dict[str, object]],
    outpath: Path,
    max_t_plot: int,
    title: str,
) -> None:
    n = len(dsts)
    if n == 0:
        return
    # Use more columns for larger n so the resulting PDF is not extremely tall
    # when embedded into a LaTeX report.
    ncols = 3 if n >= 9 else 2
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(ncols * 4.4, nrows * 2.6),
        dpi=170,
        squeeze=False,
    )
    axes_flat = axes.ravel()

    for i, (ax, dst) in enumerate(zip(axes_flat, dsts)):
        info = exact_by_dst[dst]
        A = info["A"]
        peaks = info["peaks"]
        (t1, _), (t2, h2) = peaks[0], peaks[1]
        lo, hi = info["window"]
        t = np.arange(1, len(A) + 1, dtype=np.int32)
        ax.plot(t[:max_t_plot], A[:max_t_plot], lw=2.0)
        ax.set_xscale("log")
        ax.grid(True, which="both", alpha=0.22)
        ax.axvline(int(t1), lw=1.2, ls="--", alpha=0.7, color="gray")
        ax.axvline(int(t2), lw=1.2, ls="--", alpha=0.85, color="tab:orange")
        ax.axvspan(int(lo), int(hi), color="tab:orange", alpha=0.12)
        ax.set_title(f"dst={dst}  $t_2$={t2}, $A(t_2)$={float(h2):.4g}", fontsize=9)
        row = int(i // ncols)
        col = int(i % ncols)
        if row == nrows - 1:
            ax.set_xlabel("time $t$ (log)")
        if col == 0:
            ax.set_ylabel("$A(t)$")

    for ax in axes_flat[len(dsts) :]:
        ax.axis("off")

    fig.suptitle(title, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(outpath)
    plt.close(fig)


def plot_crossing_fractions(
    *,
    dsts: Sequence[int],
    mc_by_dst: Dict[int, Dict[str, object]],
    outpath: Path,
    title: str,
) -> None:
    def fmt_n(n: int) -> str:
        if n >= 1000:
            s = f"{n/1000.0:.1f}k"
            return s.replace(".0k", "k")
        return str(n)

    dsts_sorted = list(sorted(dsts))
    x = np.arange(len(dsts_sorted), dtype=np.int32)
    labels = [str(d) for d in dsts_sorted]

    frac_no = np.array([mc_by_dst[d]["frac_no"] for d in dsts_sorted], dtype=np.float64)
    frac_one = np.array([mc_by_dst[d]["frac_one"] for d in dsts_sorted], dtype=np.float64)
    frac_multi = np.array([mc_by_dst[d]["frac_multi"] for d in dsts_sorted], dtype=np.float64)

    fig, ax = plt.subplots(figsize=(9.6, 3.9), dpi=170)
    ax.bar(x, frac_no, label="0 crossings", color="#4C78A8")
    ax.bar(x, frac_one, bottom=frac_no, label="1 crossing", color="#F58518")
    ax.bar(x, frac_multi, bottom=frac_no + frac_one, label=">=2 crossings", color="#54A24B")

    for i, d in enumerate(dsts_sorted):
        n_in = int(mc_by_dst[d]["n_in_window"])
        ax.text(
            i,
            1.005 + 0.02 * (i % 2),
            f"n={fmt_n(n_in)}",
            ha="center",
            va="bottom",
            fontsize=7,
            clip_on=False,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    if len(labels) > 10:
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
            tick.set_ha("right")
    ax.set_ylim(0, 1.10)
    ax.set_xlabel("shortcut dst (paper index)")
    ax.set_ylabel("fraction (conditioned on $T$ in 2nd-peak window)")
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=3, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_pcross_relationships(
    *,
    dsts: Sequence[int],
    scan_by_dst: Dict[int, ScanRow],
    mc_by_dst: Dict[int, Dict[str, object]],
    baseline_dst: int,
    target_dst: int,
    outpath: Path,
    title: str,
    early_t2_max: int,
) -> None:
    rows: List[Tuple[int, float, float, float, int]] = []
    for d in sorted(dsts):
        sr = scan_by_dst.get(int(d))
        mc = mc_by_dst.get(int(d))
        if sr is None or mc is None:
            continue
        if sr.h2_over_h1 is None or sr.h2 is None or mc.get("frac_no") is None:
            continue
        if sr.t2 is None:
            continue
        p_cross = 1.0 - float(mc["frac_no"])
        rows.append((int(d), float(sr.h2_over_h1), float(sr.h2), float(p_cross), int(sr.t2)))

    if not rows:
        return

    d_arr = np.array([r[0] for r in rows], dtype=np.int32)
    ratio_arr = np.array([r[1] for r in rows], dtype=np.float64)
    h2_arr = np.array([r[2] for r in rows], dtype=np.float64)
    p_arr = np.array([r[3] for r in rows], dtype=np.float64)
    t2_arr = np.array([r[4] for r in rows], dtype=np.int32)
    n_arr = np.array([int(mc_by_dst[int(d)]["n_in_window"]) for d in d_arr], dtype=np.int32)

    ci_lo = np.zeros_like(p_arr)
    ci_hi = np.zeros_like(p_arr)
    for i in range(p_arr.size):
        lo, hi = wilson_interval(float(p_arr[i]), int(n_arr[i]))
        ci_lo[i], ci_hi[i] = lo, hi

    is_early = t2_arr <= int(early_t2_max)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 5.4), dpi=170)

    def _scatter(ax, x, xlabel):
        # Highlight target dst (direct-to-target) separately.
        is_target = d_arr == int(target_dst)
        is_baseline = d_arr == int(baseline_dst)
        is_early_non_target = is_early & (~is_target)
        is_late_non_target = (~is_early) & (~is_target)

        if is_late_non_target.any():
            ax.vlines(
                x[is_late_non_target],
                ci_lo[is_late_non_target],
                ci_hi[is_late_non_target],
                color="tab:blue",
                alpha=0.65,
                linewidth=1.0,
            )
            ax.scatter(
                x[is_late_non_target],
                p_arr[is_late_non_target],
                s=28,
                alpha=0.9,
                color="tab:blue",
                label=f"late bimodal ($t_2>{early_t2_max}$)",
            )

        if is_early_non_target.any():
            ax.vlines(
                x[is_early_non_target],
                ci_lo[is_early_non_target],
                ci_hi[is_early_non_target],
                color="#54A24B",
                alpha=0.75,
                linewidth=1.0,
            )
            ax.scatter(
                x[is_early_non_target],
                p_arr[is_early_non_target],
                s=28,
                alpha=0.9,
                color="#54A24B",
                label=f"early bimodal ($t_2\\leq{early_t2_max}$)",
            )
        if is_target.any():
            ax.vlines(
                x[is_target],
                ci_lo[is_target],
                ci_hi[is_target],
                color="tab:red",
                alpha=0.80,
                linewidth=1.0,
            )
            ax.scatter(
                x[is_target],
                p_arr[is_target],
                marker="*",
                s=120,
                alpha=0.95,
                color="tab:red",
                label=f"dst=target={target_dst}",
            )
        if is_baseline.any():
            ax.scatter(
                x[is_baseline],
                p_arr[is_baseline],
                s=90,
                facecolors="none",
                edgecolors="black",
                linewidths=1.4,
                label=f"baseline dst={baseline_dst}",
            )

        ax.set_xlabel(xlabel)
        ax.set_ylabel(r"$P(C\geq 1\mid T\in[t_2-\Delta,t_2+\Delta])$")
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.25)

    _scatter(ax1, ratio_arr, r"peak ratio $R=A(t_2)/A(t_1)$")
    _scatter(ax2, h2_arr, r"second peak height $A(t_2)$")

    # Correlations (all points and excluding the special target case)
    r_ratio_all = pearson_r(ratio_arr, p_arr)
    r_h2_all = pearson_r(h2_arr, p_arr)
    s_ratio_all = spearman_r(ratio_arr, p_arr)

    mask_non_target = d_arr != int(target_dst)
    r_ratio_nt = pearson_r(ratio_arr[mask_non_target], p_arr[mask_non_target])
    r_h2_nt = pearson_r(h2_arr[mask_non_target], p_arr[mask_non_target])
    s_ratio_nt = spearman_r(ratio_arr[mask_non_target], p_arr[mask_non_target])

    ax1.set_title(
        "vs peak ratio\n"
        + f"Pearson r={r_ratio_all:.3f} (all), {r_ratio_nt:.3f} (exclude dst=target)\n"
        + f"Spearman ρ={s_ratio_all:.3f} (all), {s_ratio_nt:.3f} (exclude dst=target)",
        fontsize=9,
    )
    ax2.set_title(
        "vs $A(t_2)$\n"
        + f"Pearson r={r_h2_all:.3f} (all), {r_h2_nt:.3f} (exclude dst=target)",
        fontsize=9,
    )

    handles, labels = ax1.get_legend_handles_labels()
    if handles:
        fig.legend(
            handles,
            labels,
            frameon=False,
            ncol=3,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.95),
            fontsize=9,
        )

    fig.suptitle(title, fontsize=12, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.84))
    fig.savefig(outpath)
    plt.close(fig)


def write_table_tex(
    *,
    dsts: Sequence[int],
    exact_by_dst: Dict[int, Dict[str, object]],
    mc_by_dst: Dict[int, Dict[str, object]],
    outpath: Path,
) -> None:
    lines: List[str] = []
    lines.append(r"\begin{tabular}{r r r r r r r r r}")
    lines.append(r"\toprule")
    lines.append(
        r"$\mathrm{dst}$ & $t_1$ & $t_2$ & $\Delta$ & $R$ & $A(t_1)$ & $A(t_2)$ & $P(C=0)$ & $P(C\ge1)$ \\"
    )
    lines.append(r"\midrule")
    for d in sorted(dsts):
        info = exact_by_dst[d]
        peaks = info["peaks"]
        (t1, _), (t2, h2) = peaks[0], peaks[1]
        delta = int(info["delta"])
        mc = mc_by_dst[d]
        p0 = float(mc["frac_no"])
        h1 = float(peaks[0][1])
        ratio = float(h2 / h1) if h1 > 0 else float("nan")
        lines.append(
            f"{d} & {int(t1)} & {int(t2)} & {delta} & {ratio:.3f} & {h1:.6g} & {float(h2):.6g} & {p0:.3f} & {1.0 - p0:.3f} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    outpath.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Fix (N,K) and paper start/target; vary shortcut destination dst; run AW exact + MC crossing stats near 2nd peak."
    )
    p.add_argument("--N", type=int, default=100)
    p.add_argument("--K", type=int, default=6)
    p.add_argument("--n0", type=int, default=1)
    p.add_argument("--target", type=int, default=None, help="paper target; default N/2")
    p.add_argument("--shortcut-offset", type=int, default=5, help="paper: src = n0 + offset")
    p.add_argument("--sc-src", type=int, default=None, help="paper shortcut source; default wrap(n0+offset)")
    p.add_argument("--rho", type=float, default=1.0)
    p.add_argument("--max-steps", type=int, default=2000)
    p.add_argument("--delta-frac", type=float, default=0.05)
    p.add_argument("--min-height", type=float, default=1e-7)
    p.add_argument("--second-rel-height", type=float, default=0.01)
    p.add_argument(
        "--early-t2-max",
        type=int,
        default=None,
        help="classification threshold for early vs late second peak (early: t2 <= threshold); default 2*K",
    )
    p.add_argument("--run-id", type=str, default=None)

    p.add_argument("--dst", type=int, nargs="*", default=None, help="explicit dst list (paper)")
    p.add_argument("--dst-min", type=int, default=1)
    p.add_argument("--dst-max", type=int, default=None)
    p.add_argument("--n-mc-dsts", type=int, default=8, help="number of representative dsts for MC (when --dst not set)")
    p.add_argument(
        "--mc-all-bimodal",
        action="store_true",
        help="run MC for all dst that satisfy the bimodal (Fig.3) rule in the scan (only when --dst is not set)",
    )
    p.add_argument("--n-walkers", type=int, default=500_000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--batch-size", type=int, default=50_000)
    p.add_argument("--max-t-plot", type=int, default=600)
    p.add_argument("--no-latest", action="store_true")
    args = p.parse_args()

    N = int(args.N)
    K = int(args.K)
    n0_paper = wrap_paper(int(args.n0), N)
    target_paper = wrap_paper(N // 2 if args.target is None else int(args.target), N)
    if args.sc_src is None:
        sc_src_paper = wrap_paper(n0_paper + int(args.shortcut_offset), N)
    else:
        sc_src_paper = wrap_paper(int(args.sc_src), N)

    baseline_dst = wrap_paper(target_paper + 1, N)
    early_t2_max = int(args.early_t2_max) if args.early_t2_max is not None else int(2 * K)

    run_id = str(args.run_id).strip() if args.run_id is not None else default_run_id()
    prefix = f"N{N}K{K}_n0_{n0_paper}_target_{target_paper}_src_{sc_src_paper}"
    fig_run_dir = FIG_ROOT / prefix / "runs" / run_id
    data_run_dir = DATA_ROOT / prefix / "runs" / run_id
    fig_run_dir.mkdir(parents=True, exist_ok=True)
    data_run_dir.mkdir(parents=True, exist_ok=True)

    # Scan all dst (or explicit list) with AW to find bimodal configs and peak2 heights.
    dst_max = N if args.dst_max is None else int(args.dst_max)
    dst_candidates = [wrap_paper(d, N) for d in (args.dst if args.dst else range(int(args.dst_min), dst_max + 1))]
    # Deduplicate preserving order
    dst_seen: set[int] = set()
    dst_list: List[int] = []
    for d in dst_candidates:
        if d in dst_seen:
            continue
        dst_seen.add(d)
        dst_list.append(int(d))

    scan_rows: List[ScanRow] = []
    exact_by_dst: Dict[int, Dict[str, object]] = {}
    for dst in dst_list:
        try:
            g = build_graph_directed_shortcut(
                N=N,
                K=K,
                n0_paper=n0_paper,
                target_paper=target_paper,
                sc_src_paper=sc_src_paper,
                sc_dst_paper=dst,
            )
        except ValueError as e:
            scan_rows.append(
                ScanRow(
                    dst=int(dst),
                    valid=False,
                    reason_invalid=str(e),
                    bimodal=False,
                    t1=None,
                    h1=None,
                    t2=None,
                    h2=None,
                    h2_over_h1=None,
                    delta=None,
                    window_lo=None,
                    window_hi=None,
                )
            )
            continue

        A, peaks = exact_A_and_peaks(
            g,
            rho=float(args.rho),
            max_steps=int(args.max_steps),
            min_height=float(args.min_height),
            second_rel_height=float(args.second_rel_height),
        )
        if len(peaks) >= 2:
            (t1, h1), (t2, h2) = peaks[0], peaks[1]
            lo, hi, delta = second_peak_window(peaks, delta_frac=float(args.delta_frac))
            h2_over_h1 = float(h2 / h1) if h1 > 0 else None
            scan_rows.append(
                ScanRow(
                    dst=int(dst),
                    valid=True,
                    reason_invalid=None,
                    bimodal=True,
                    t1=int(t1),
                    h1=float(h1),
                    t2=int(t2),
                    h2=float(h2),
                    h2_over_h1=h2_over_h1,
                    delta=int(delta),
                    window_lo=int(lo),
                    window_hi=int(hi),
                )
            )
            exact_by_dst[int(dst)] = {
                "A": A,
                "peaks": peaks[:2],
                "delta": int(delta),
                "window": [int(lo), int(hi)],
            }
        else:
            t1 = int(peaks[0][0]) if peaks else None
            h1 = float(peaks[0][1]) if peaks else None
            scan_rows.append(
                ScanRow(
                    dst=int(dst),
                    valid=True,
                    reason_invalid=None,
                    bimodal=False,
                    t1=t1,
                    h1=h1,
                    t2=None,
                    h2=None,
                    h2_over_h1=None,
                    delta=None,
                    window_lo=None,
                    window_hi=None,
                )
            )
            exact_by_dst[int(dst)] = {"A": A, "peaks": peaks, "delta": None, "window": None}

    bimodal_rows = [r for r in scan_rows if r.valid and r.bimodal]
    if args.dst:
        if len(bimodal_rows) != len([r for r in scan_rows if r.valid]):
            bad = [r.dst for r in scan_rows if r.valid and not r.bimodal]
            raise SystemExit(f"Some requested dst are not bimodal under Fig.3 rule: {bad}")
        mc_dsts = [r.dst for r in bimodal_rows]
    elif args.mc_all_bimodal:
        mc_dsts = [r.dst for r in bimodal_rows]
    else:
        mc_dsts = select_representative_dsts(
            bimodal_rows=bimodal_rows,
            baseline_dst=baseline_dst,
            target_dst=target_paper,
            n_select=int(args.n_mc_dsts),
        )

    # Run MC for selected dsts
    mc_by_dst: Dict[int, Dict[str, object]] = {}
    rows_mc_csv: List[Dict[str, object]] = []
    scan_by_dst: Dict[int, ScanRow] = {r.dst: r for r in scan_rows if r.valid}
    for dst in mc_dsts:
        row = next(r for r in bimodal_rows if r.dst == dst)
        g = build_graph_directed_shortcut(
            N=N,
            K=K,
            n0_paper=n0_paper,
            target_paper=target_paper,
            sc_src_paper=sc_src_paper,
            sc_dst_paper=dst,
        )
        seed_case = int(args.seed) + int(dst) * 100
        times, crosses = mc_first_passage_crossings(
            g,
            n_walkers=int(args.n_walkers),
            rho=float(args.rho),
            seed=seed_case,
            batch_size=int(args.batch_size),
        )
        stats = crossing_stats_in_window(times, crosses, lo=int(row.window_lo), hi=int(row.window_hi))
        mc_by_dst[int(dst)] = {
            **stats,
            "dst": int(dst),
            "t1": int(row.t1),
            "t2": int(row.t2),
            "delta": int(row.delta),
            "window": [int(row.window_lo), int(row.window_hi)],
        }
        rows_mc_csv.append(
            {
                "dst": int(dst),
                "t1": int(row.t1),
                "h1": float(row.h1),
                "t2": int(row.t2),
                "h2": float(row.h2),
                "h2_over_h1": float(row.h2_over_h1),
                "delta": int(row.delta),
                "window_lo": int(row.window_lo),
                "window_hi": int(row.window_hi),
                "n_walkers": int(args.n_walkers),
                "n_in_window": int(stats["n_in_window"]),
                "frac_in_window": float(stats["frac_in_window"]),
                "frac_no": stats["frac_no"],
                "frac_one": stats["frac_one"],
                "frac_multi": stats["frac_multi"],
            }
        )

    # Figures
    fig_peak2 = fig_run_dir / f"peak2_vs_dst__{run_id}.pdf"
    plot_peak2_scan(
        scan_rows=scan_rows,
        selected_dsts=mc_dsts,
        baseline_dst=baseline_dst,
        title=f"Second-peak height vs shortcut destination (N={N}, K={K}, src={sc_src_paper}, target={target_paper})",
        outpath=fig_peak2,
    )

    fig_times = fig_run_dir / f"peak_times_vs_dst__{run_id}.pdf"
    plot_peak_times_scan(
        scan_rows=scan_rows,
        selected_dsts=mc_dsts,
        baseline_dst=baseline_dst,
        title=f"Peak times among bimodal cases (N={N}, K={K}, src={sc_src_paper}, target={target_paper})",
        outpath=fig_times,
    )

    fig_exact = fig_run_dir / f"exact_selected_cases__{run_id}.pdf"
    plot_exact_gallery(
        dsts=mc_dsts,
        exact_by_dst=exact_by_dst,
        outpath=fig_exact,
        max_t_plot=max(30, int(args.max_t_plot)),
        title="Selected bimodal cases (AW exact) with 2nd-peak windows",
    )

    fig_frac = fig_run_dir / f"second_peak_crossing_fractions__{run_id}.pdf"
    plot_crossing_fractions(
        dsts=mc_dsts,
        mc_by_dst=mc_by_dst,
        outpath=fig_frac,
        title="Shortcut crossings conditioned on absorption near the 2nd peak",
    )

    fig_rel = fig_run_dir / f"pcross_relationships__{run_id}.pdf"
    plot_pcross_relationships(
        dsts=mc_dsts,
        scan_by_dst=scan_by_dst,
        mc_by_dst=mc_by_dst,
        baseline_dst=baseline_dst,
        target_dst=target_paper,
        outpath=fig_rel,
        title="How shortcut usage varies with peak heights",
        early_t2_max=early_t2_max,
    )

    # Save scan CSV
    scan_csv = data_run_dir / f"scan__{run_id}.csv"
    scan_fields = list(ScanRow.__annotations__.keys())
    with scan_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=scan_fields)
        w.writeheader()
        for r in sorted(scan_rows, key=lambda rr: rr.dst):
            w.writerow(r.__dict__)

    # Save MC CSV
    mc_csv = data_run_dir / f"mc__{run_id}.csv"
    mc_fields = list(rows_mc_csv[0].keys()) if rows_mc_csv else []
    if mc_fields:
        with mc_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=mc_fields)
            w.writeheader()
            for row in rows_mc_csv:
                w.writerow(row)

    # Save a TeX table for report
    tex_table = data_run_dir / f"selected_table__{run_id}.tex"
    write_table_tex(dsts=mc_dsts, exact_by_dst=exact_by_dst, mc_by_dst=mc_by_dst, outpath=tex_table)

    # Small TeX snippet with the scope of bimodal dsts (for report text).
    bimodal_dsts = sorted([r.dst for r in bimodal_rows])
    if bimodal_dsts:
        dst_min = int(bimodal_dsts[0])
        dst_max = int(bimodal_dsts[-1])
        scope_lines: List[str] = []
        scope_lines.append(r"\begin{itemize}")
        scope_lines.append(
            rf"  \item 本次参数：$N={N},\;K={K},\;n_0={n0_paper},\;\mathrm{{target}}={target_paper},\;\mathrm{{src}}={sc_src_paper}$。"
        )
        scope_lines.append(
            rf"  \item 满足双峰判据（Fig.~3 规则）的 $\mathrm{{dst}}$：共 {len(bimodal_dsts)} 个，范围 {dst_min}--{dst_max}。"
        )
        if int(target_paper) in set(bimodal_dsts):
            scope_lines.append(
                rf"  \item 特殊点：$\mathrm{{dst}}=\mathrm{{target}}={target_paper}$ 会使 shortcut 直接连到吸收点，导致窗口很早且 $P(C\geq 1)$ 接近 1。"
            )
        scope_lines.append(r"\end{itemize}")
        (data_run_dir / f"scope_summary__{run_id}.tex").write_text(
            "\n".join(scope_lines) + "\n", encoding="utf-8"
        )

    # Small TeX snippet with correlations for report text
    if mc_dsts:
        dst_arr = np.asarray(sorted(mc_dsts), dtype=np.int32)
        ratio_arr = np.asarray([float(scan_by_dst[int(d)].h2_over_h1) for d in dst_arr], dtype=np.float64)
        h2_arr = np.asarray([float(scan_by_dst[int(d)].h2) for d in dst_arr], dtype=np.float64)
        p_cross_arr = np.asarray([1.0 - float(mc_by_dst[int(d)]["frac_no"]) for d in dst_arr], dtype=np.float64)
        p0_arr = 1.0 - p_cross_arr
        mask_non_target = dst_arr != int(target_paper)
        t2_arr = np.asarray([int(scan_by_dst[int(d)].t2) for d in dst_arr], dtype=np.int32)
        mask_late = t2_arr > int(early_t2_max)
        have_early_and_late = bool(mask_late.any() and (~mask_late).any())
        stats_tex = "\n".join(
            [
                r"\begin{itemize}",
                rf"  \item Pearson $r(R,\;P(C\ge1))$：{pearson_r(ratio_arr, p_cross_arr):.3f}（全体），{pearson_r(ratio_arr[mask_non_target], p_cross_arr[mask_non_target]):.3f}（去掉 $\mathrm{{dst}}=\mathrm{{target}}$）。",
                rf"  \item Spearman $\rho(R,\;P(C\ge1))$：{spearman_r(ratio_arr, p_cross_arr):.3f}（全体），{spearman_r(ratio_arr[mask_non_target], p_cross_arr[mask_non_target]):.3f}（去掉 $\mathrm{{dst}}=\mathrm{{target}}$）。",
                rf"  \item Pearson $r(A(t_2),\;P(C\ge1))$：{pearson_r(h2_arr, p_cross_arr):.3f}（全体），{pearson_r(h2_arr[mask_non_target], p_cross_arr[mask_non_target]):.3f}（去掉 $\mathrm{{dst}}=\mathrm{{target}}$）。",
                rf"  \item （等价）Pearson $r(A(t_2),\;P(C=0))$：{pearson_r(h2_arr, p0_arr):.3f}（全体），{pearson_r(h2_arr[mask_non_target], p0_arr[mask_non_target]):.3f}（去掉 $\mathrm{{dst}}=\mathrm{{target}}$）。",
                rf"  \item （late-only：$t_2>{early_t2_max}$）Pearson $r(A(t_2),\;P(C\ge1))$：{pearson_r(h2_arr[mask_late], p_cross_arr[mask_late]):.3f}；Pearson $r(R,\;P(C\ge1))$：{pearson_r(ratio_arr[mask_late], p_cross_arr[mask_late]):.3f}。"
                if have_early_and_late
                else "",
                r"\end{itemize}",
            ]
        )
        (data_run_dir / f"analysis_summary__{run_id}.tex").write_text(stats_tex + "\n", encoding="utf-8")

    # Store curves for selected dsts (AW exact)
    A_mat = np.stack([exact_by_dst[d]["A"] for d in mc_dsts], axis=0).astype(np.float64, copy=False)
    np.savez_compressed(
        data_run_dir / f"exact_curves_selected__{run_id}.npz",
        dst=np.asarray(mc_dsts, dtype=np.int32),
        A=A_mat,
    )

    # Structured JSON record
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
            "rho": float(args.rho),
            "max_steps": int(args.max_steps),
            "min_height": float(args.min_height),
            "second_rel_height": float(args.second_rel_height),
            "delta_frac": float(args.delta_frac),
            "early_t2_max": int(early_t2_max),
            "n_walkers": int(args.n_walkers),
            "seed": int(args.seed),
            "batch_size": int(args.batch_size),
            "n0_paper": int(n0_paper),
            "target_paper": int(target_paper),
            "sc_src_paper": int(sc_src_paper),
            "baseline_dst": int(baseline_dst),
        },
        "scan_rows": [r.__dict__ for r in sorted(scan_rows, key=lambda rr: rr.dst)],
        "selected_dsts": mc_dsts,
        "mc_by_dst": mc_by_dst,
        "files": {
            "peak2_scan": str(fig_peak2.relative_to(REPO_ROOT)),
            "peak_times": str(fig_times.relative_to(REPO_ROOT)),
            "exact_selected": str(fig_exact.relative_to(REPO_ROOT)),
            "crossing_fractions": str(fig_frac.relative_to(REPO_ROOT)),
            "pcross_relationships": str(fig_rel.relative_to(REPO_ROOT)),
            "scan_csv": str(scan_csv.relative_to(REPO_ROOT)),
            "mc_csv": str(mc_csv.relative_to(REPO_ROOT)) if mc_fields else None,
            "table_tex": str(tex_table.relative_to(REPO_ROOT)),
            "analysis_summary_tex": str((data_run_dir / f"analysis_summary__{run_id}.tex").relative_to(REPO_ROOT))
            if mc_dsts
            else None,
            "scope_summary_tex": str((data_run_dir / f"scope_summary__{run_id}.tex").relative_to(REPO_ROOT))
            if bimodal_dsts
            else None,
            "exact_curves_selected": str((data_run_dir / f"exact_curves_selected__{run_id}.npz").relative_to(REPO_ROOT)),
        },
    }
    (data_run_dir / f"results__{run_id}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    if not args.no_latest:
        latest_fig = FIG_ROOT / prefix / "latest"
        latest_data = DATA_ROOT / prefix / "latest"
        latest_fig.mkdir(parents=True, exist_ok=True)
        latest_data.mkdir(parents=True, exist_ok=True)
        copy_latest(fig_peak2, latest_fig / "peak2_vs_dst.pdf")
        copy_latest(fig_times, latest_fig / "peak_times_vs_dst.pdf")
        copy_latest(fig_exact, latest_fig / "exact_selected_cases.pdf")
        copy_latest(fig_frac, latest_fig / "second_peak_crossing_fractions.pdf")
        copy_latest(fig_rel, latest_fig / "pcross_relationships.pdf")
        copy_latest(scan_csv, latest_data / "scan.csv")
        if mc_fields:
            copy_latest(mc_csv, latest_data / "mc.csv")
        copy_latest(tex_table, latest_data / "selected_table.tex")
        if mc_dsts:
            copy_latest(data_run_dir / f"analysis_summary__{run_id}.tex", latest_data / "analysis_summary.tex")
        if bimodal_dsts:
            copy_latest(data_run_dir / f"scope_summary__{run_id}.tex", latest_data / "scope_summary.tex")
        copy_latest(data_run_dir / f"results__{run_id}.json", latest_data / "results.json")
        copy_latest(
            data_run_dir / f"exact_curves_selected__{run_id}.npz", latest_data / "exact_curves_selected.npz"
        )

    print(f"Prefix: {prefix}")
    print(f"Saved figures to: {fig_run_dir}")
    print(f"Saved data to: {data_run_dir}")


if __name__ == "__main__":
    main()
