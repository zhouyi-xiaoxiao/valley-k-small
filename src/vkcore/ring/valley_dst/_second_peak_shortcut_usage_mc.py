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

FIG_ROOT = REPORT_ROOT / "figures" / "second_peak_shortcut_usage"
DATA_ROOT = REPORT_ROOT / "data" / "second_peak_shortcut_usage"


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


@dataclass(frozen=True)
class Case:
    N: int
    K: int

    def label(self) -> str:
        return f"N={self.N}, K={self.K}"

    def key(self) -> str:
        return f"N{self.N}K{self.K}"


def parse_cases(items: Sequence[str]) -> List[Case]:
    out: List[Case] = []
    for item in items:
        s = item.strip()
        if not s:
            continue
        if "," not in s:
            raise ValueError(f"Invalid case '{item}'; expected 'N,K'.")
        a, b = s.split(",", 1)
        out.append(Case(N=int(a), K=int(b)))
    return out


def detect_two_peaks(A: np.ndarray, *, min_height: float, second_rel_height: float) -> List[Tuple[int, float]]:
    A_use = vs.coarsegrain_two_steps(A) if len(A) and False else A
    return vs.detect_peaks_fig3(A_use, min_height=min_height, second_rel_height=second_rel_height)


def second_peak_window(
    peaks: Sequence[Tuple[int, float]],
    *,
    delta_frac: float,
) -> Tuple[int, int, int]:
    (t1, _), (t2, _) = peaks[0], peaks[1]
    delta = max(1, int(delta_frac * (t2 - t1)))
    lo = max(1, int(t2) - delta)
    hi = int(t2) + delta
    return lo, hi, delta


def shortcut_endpoints_paper(N: int, *, n0_paper: int = 1, shortcut_offset: int = 5) -> Tuple[int, int, int]:
    """
    Paper convention (directed shortcut):
      src = n0 + offset
      dst = (target + 1) = N/2 + 1   (N even)
    Returns (target_paper, sc_src_paper, sc_dst_paper).
    """
    if N % 2 != 0:
        raise ValueError("Paper setting uses target N/2; please use even N.")
    target_paper = N // 2
    sc_src_paper = vs._wrap_paper(n0_paper + shortcut_offset, N)
    sc_dst_paper = vs._wrap_paper(target_paper + 1, N)
    return target_paper, sc_src_paper, sc_dst_paper


def compute_exact_A(
    *,
    N: int,
    K: int,
    rho: float,
    max_steps: int,
    n0_paper: int,
    shortcut_offset: int,
    directed_shortcut: bool,
) -> np.ndarray:
    g = vs.build_graph(
        N,
        K,
        n0_paper=n0_paper,
        target_paper=None,
        shortcut_offset=shortcut_offset,
        directed_shortcut=directed_shortcut,
    )
    A = vs.exact_first_absorption_aw(g, rho=rho, max_steps=max_steps)
    return np.maximum(A, 0.0)


def mc_shortcut_crossings_near_second_peak(
    *,
    N: int,
    K: int,
    rho: float,
    n_walkers: int,
    seed: int,
    mc_n_jobs: int,
    n0_paper: int,
    shortcut_offset: int,
    directed_shortcut: bool,
    t2: int,
    delta: int,
) -> Dict[str, object]:
    times, crosses = vs.mc_first_passage_times_joblib(
        N,
        K,
        n_walkers,
        rho=rho,
        seed=seed,
        batch_size=50_000,
        n_jobs=mc_n_jobs,
        track_crossings=True,
        directed_shortcut=directed_shortcut,
        shortcut_offset=shortcut_offset,
    )
    if crosses is None:
        raise RuntimeError("Expected crossings array (track_crossings=True).")

    lo = max(1, int(t2) - int(delta))
    hi = int(t2) + int(delta)
    mask = (times >= lo) & (times <= hi)
    n_in = int(mask.sum())
    if n_in == 0:
        return {
            "t2": int(t2),
            "delta": int(delta),
            "window": [lo, hi],
            "n_in_window": 0,
            "frac_in_window": 0.0,
            "frac_no": None,
            "frac_one": None,
            "frac_multi": None,
        }

    c = crosses[mask]
    frac_no = float(np.mean(c == 0))
    frac_one = float(np.mean(c == 1))
    frac_multi = float(np.mean(c >= 2))
    return {
        "t2": int(t2),
        "delta": int(delta),
        "window": [lo, hi],
        "n_in_window": n_in,
        "frac_in_window": float(n_in / float(n_walkers)),
        "frac_no": frac_no,
        "frac_one": frac_one,
        "frac_multi": frac_multi,
    }


def plot_exact_gallery(
    *,
    cases: Sequence[Case],
    exact: Dict[str, Dict[str, object]],
    outpath: Path,
    max_t_plot: int,
) -> None:
    n = len(cases)
    ncols = 2
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(ncols * 6.4, nrows * 3.6),
        dpi=170,
        squeeze=False,
    )
    axes_flat = axes.ravel()

    for ax, case in zip(axes_flat, cases):
        info = exact[case.key()]
        A = info["A"]
        peaks = info["peaks"]
        (t1, h1), (t2, h2) = peaks[0], peaks[1]
        lo, hi = info["second_window"]

        t = np.arange(1, len(A) + 1, dtype=np.int32)
        ax.plot(t[:max_t_plot], A[:max_t_plot], lw=2.0)
        ax.set_xscale("log")
        ax.grid(True, which="both", alpha=0.22)
        ax.axvline(int(t1), lw=1.2, ls="--", alpha=0.7, color="gray")
        ax.axvline(int(t2), lw=1.2, ls="--", alpha=0.85, color="tab:orange")
        ax.axvspan(int(lo), int(hi), color="tab:orange", alpha=0.12)
        ax.set_title(
            f"{case.label()}  $t_1$={t1}, $t_2$={t2}, $A(t_2)$={h2:.4g}",
            fontsize=9,
        )
        ax.set_xlabel("time $t$ (log)")
        ax.set_ylabel("$A(t)$")

    for ax in axes_flat[len(cases) :]:
        ax.axis("off")

    fig.suptitle("Exact first-absorption curves (AW inversion) with 2nd-peak window", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(outpath)
    plt.close(fig)


def plot_crossing_fractions(
    *,
    cases: Sequence[Case],
    mc_stats: Dict[str, Dict[str, object]],
    outpath: Path,
    title: str,
) -> None:
    def fmt_n(n: int) -> str:
        if n >= 1000:
            s = f"{n/1000.0:.1f}k"
            return s.replace(".0k", "k")
        return str(n)

    labels = [case.key().replace("N", "N=").replace("K", ", K=") for case in cases]
    x = np.arange(len(cases), dtype=np.int32)

    frac_no = np.array([mc_stats[case.key()]["frac_no"] for case in cases], dtype=np.float64)
    frac_one = np.array([mc_stats[case.key()]["frac_one"] for case in cases], dtype=np.float64)
    frac_multi = np.array([mc_stats[case.key()]["frac_multi"] for case in cases], dtype=np.float64)

    fig, ax = plt.subplots(figsize=(8.6, 3.8), dpi=170)
    ax.bar(x, frac_no, label="0 crossings", color="#4C78A8")
    ax.bar(x, frac_one, bottom=frac_no, label="1 crossing", color="#F58518")
    ax.bar(x, frac_multi, bottom=frac_no + frac_one, label=">=2 crossings", color="#54A24B")

    for i, case in enumerate(cases):
        n_in = int(mc_stats[case.key()]["n_in_window"])
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
    ax.set_xticklabels(labels, rotation=0)
    ax.set_ylim(0, 1.10)
    ax.set_ylabel("fraction within 2nd-peak window")
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=3, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def write_table_tex(
    *,
    cases: Sequence[Case],
    exact: Dict[str, Dict[str, object]],
    mc: Dict[str, Dict[str, object]],
    outpath: Path,
) -> None:
    lines: List[str] = []
    lines.append(r"\begin{tabular}{r r r r r r r r r}")
    lines.append(r"\toprule")
    lines.append(r"$N$ & $K$ & $t_1$ & $t_2$ & $\Delta$ & $A(t_1)$ & $A(t_2)$ & $P(C=0)$ & $P(C\ge1)$ \\")
    lines.append(r"\midrule")
    for case in cases:
        info = exact[case.key()]
        peaks = info["peaks"]
        (t1, _), (t2, h2) = peaks[0], peaks[1]
        delta = int(info["delta"])
        mc_info = mc[case.key()]
        p0 = float(mc_info["frac_no"])
        pge1 = float(1.0 - p0)
        h1 = float(peaks[0][1])
        lines.append(
            f"{case.N} & {case.K} & {int(t1)} & {int(t2)} & {delta} & {h1:.6g} & {float(h2):.6g} & {p0:.3f} & {pge1:.3f} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    outpath.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Paper-setting Monte Carlo: shortcut crossings conditioned on first-passage times near the 2nd peak. "
            "Uses AW-inverted exact A(t) to locate peaks."
        )
    )
    p.add_argument(
        "--cases",
        nargs="*",
        default=["50,4", "70,6", "100,6", "100,8"],
        help="cases as 'N,K' (default: 50,4 70,6 100,6 100,8)",
    )
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--n-walkers", type=int, default=500_000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--rho", type=float, default=1.0)
    p.add_argument("--max-steps", type=int, default=2000)
    p.add_argument("--delta-frac", type=float, default=0.05, help="window half-width relative to (t2-t1)")
    p.add_argument("--min-height", type=float, default=1e-7)
    p.add_argument("--second-rel-height", type=float, default=0.01)
    p.add_argument("--mc-n-jobs", type=int, default=-1)
    p.add_argument("--n0", type=int, default=1, help="paper start node n0")
    p.add_argument("--shortcut-offset", type=int, default=5)
    p.add_argument("--max-t-plot", type=int, default=600)
    p.add_argument("--no-latest", action="store_true")
    args = p.parse_args()

    cases = parse_cases(args.cases)
    if not cases:
        raise SystemExit("No cases specified.")

    run_id = str(args.run_id).strip() if args.run_id is not None else default_run_id()
    fig_run_dir = FIG_ROOT / "runs" / run_id
    data_run_dir = DATA_ROOT / "runs" / run_id
    fig_run_dir.mkdir(parents=True, exist_ok=True)
    data_run_dir.mkdir(parents=True, exist_ok=True)

    rho = float(args.rho)
    max_steps = int(args.max_steps)
    n_walkers = int(args.n_walkers)
    base_seed = int(args.seed)
    delta_frac = float(args.delta_frac)

    exact: Dict[str, Dict[str, object]] = {}
    mc: Dict[str, Dict[str, object]] = {}
    rows_csv: List[Dict[str, object]] = []

    for case in cases:
        A = compute_exact_A(
            N=case.N,
            K=case.K,
            rho=rho,
            max_steps=max_steps,
            n0_paper=int(args.n0),
            shortcut_offset=int(args.shortcut_offset),
            directed_shortcut=True,
        )
        peaks = vs.detect_peaks_fig3(
            A, min_height=float(args.min_height), second_rel_height=float(args.second_rel_height)
        )
        if len(peaks) < 2:
            raise RuntimeError(f"Case {case.label()} is not bimodal under Fig.3 rule.")

        lo, hi, delta = second_peak_window(peaks, delta_frac=delta_frac)
        target_paper, sc_src_paper, sc_dst_paper = shortcut_endpoints_paper(
            case.N, n0_paper=int(args.n0), shortcut_offset=int(args.shortcut_offset)
        )

        exact[case.key()] = {
            "case": {"N": case.N, "K": case.K},
            "A": A,
            "peaks": peaks[:2],
            "delta": delta,
            "second_window": [lo, hi],
            "paper": {
                "n0": int(args.n0),
                "target": int(target_paper),
                "shortcut_src": int(sc_src_paper),
                "shortcut_dst": int(sc_dst_paper),
            },
        }

        (t1, h1), (t2, h2) = peaks[0], peaks[1]
        seed_case = base_seed + case.N * 10_000 + case.K * 100
        mc_stats = mc_shortcut_crossings_near_second_peak(
            N=case.N,
            K=case.K,
            rho=rho,
            n_walkers=n_walkers,
            seed=seed_case,
            mc_n_jobs=int(args.mc_n_jobs),
            n0_paper=int(args.n0),
            shortcut_offset=int(args.shortcut_offset),
            directed_shortcut=True,
            t2=int(t2),
            delta=int(delta),
        )
        mc[case.key()] = mc_stats

        rows_csv.append(
            {
                "N": case.N,
                "K": case.K,
                "n0_paper": int(args.n0),
                "target_paper": int(target_paper),
                "shortcut_src_paper": int(sc_src_paper),
                "shortcut_dst_paper": int(sc_dst_paper),
                "t1": int(t1),
                "h1": float(h1),
                "t2": int(t2),
                "h2": float(h2),
                "delta": int(delta),
                "window_lo": int(mc_stats["window"][0]),
                "window_hi": int(mc_stats["window"][1]),
                "n_walkers": n_walkers,
                "n_in_window": int(mc_stats["n_in_window"]),
                "frac_in_window": float(mc_stats["frac_in_window"]),
                "frac_no": mc_stats["frac_no"],
                "frac_one": mc_stats["frac_one"],
                "frac_multi": mc_stats["frac_multi"],
            }
        )

    # Figures
    fig_exact = fig_run_dir / f"exact_cases__{run_id}.pdf"
    plot_exact_gallery(
        cases=cases,
        exact=exact,
        outpath=fig_exact,
        max_t_plot=max(30, int(args.max_t_plot)),
    )

    fig_frac = fig_run_dir / f"second_peak_crossing_fractions__{run_id}.pdf"
    plot_crossing_fractions(
        cases=cases,
        mc_stats=mc,
        outpath=fig_frac,
        title="Shortcut crossings among walkers absorbed near the 2nd peak",
    )

    # Save structured results (without duplicating the full A(t) arrays in JSON)
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
            "cases": [c.key() for c in cases],
            "n0_paper": int(args.n0),
            "shortcut_offset": int(args.shortcut_offset),
            "directed_shortcut": True,
            "rho": rho,
            "max_steps": max_steps,
            "delta_frac": delta_frac,
            "min_height": float(args.min_height),
            "second_rel_height": float(args.second_rel_height),
            "n_walkers": n_walkers,
            "seed": base_seed,
        },
        "exact_summary": {
            k: {
                "case": exact[k]["case"],
                "paper": exact[k]["paper"],
                "peaks": exact[k]["peaks"],
                "delta": exact[k]["delta"],
                "second_window": exact[k]["second_window"],
            }
            for k in exact
        },
        "mc_second_peak_window": mc,
        "files": {
            "exact_cases_fig": str(fig_exact.relative_to(REPO_ROOT)),
            "crossing_fractions_fig": str(fig_frac.relative_to(REPO_ROOT)),
        },
    }
    (data_run_dir / f"results__{run_id}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    # Save full curves in a compact npz (one row per case)
    cases_sorted = [c.key() for c in cases]
    A_mat = np.stack([exact[k]["A"] for k in cases_sorted], axis=0).astype(np.float64, copy=False)
    np.savez_compressed(
        data_run_dir / f"exact_curves__{run_id}.npz",
        cases=np.array(cases_sorted),
        A=A_mat,
    )

    # CSV + TeX table for the report
    csv_path = data_run_dir / f"results__{run_id}.csv"
    fieldnames = list(rows_csv[0].keys())
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows_csv:
            w.writerow(row)

    tex_table = data_run_dir / f"cases_table__{run_id}.tex"
    write_table_tex(cases=cases, exact=exact, mc=mc, outpath=tex_table)

    if not args.no_latest:
        latest_fig_dir = FIG_ROOT / "latest"
        latest_data_dir = DATA_ROOT / "latest"
        latest_fig_dir.mkdir(parents=True, exist_ok=True)
        latest_data_dir.mkdir(parents=True, exist_ok=True)
        copy_latest(fig_exact, latest_fig_dir / "exact_cases.pdf")
        copy_latest(fig_frac, latest_fig_dir / "second_peak_crossing_fractions.pdf")
        copy_latest(csv_path, latest_data_dir / "results.csv")
        copy_latest(data_run_dir / f"results__{run_id}.json", latest_data_dir / "results.json")
        copy_latest(data_run_dir / f"exact_curves__{run_id}.npz", latest_data_dir / "exact_curves.npz")
        copy_latest(tex_table, latest_data_dir / "cases_table.tex")

    print(f"Saved figures to: {fig_run_dir}")
    print(f"Saved data to: {data_run_dir}")


if __name__ == "__main__":
    main()
