#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

_MPL_CACHE = Path(__file__).resolve().parents[1] / "build" / "mpl_cache"
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))
_MPL_CACHE.mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass
class Metrics:
    t1: float
    t2: float
    h1: float
    h2: float
    hv_over_max: float


def _warn(msg: str) -> None:
    print(f"[sensitivity_thresholds] {msg}", file=sys.stderr)


def _local_maxima(f: np.ndarray) -> List[int]:
    idxs = []
    for i in range(1, len(f) - 1):
        if f[i] >= f[i - 1] and f[i] > f[i + 1]:
            idxs.append(i)
    return idxs


def _pair_metrics(t: np.ndarray, f: np.ndarray) -> Optional[Metrics]:
    peaks = _local_maxima(f)
    if len(peaks) < 2:
        return None
    top2 = sorted(peaks, key=lambda idx: f[idx], reverse=True)[:2]
    if len(top2) < 2:
        return None
    p1, p2 = sorted(top2)
    t1 = float(t[p1])
    t2 = float(t[p2])
    if t2 <= t1:
        return None
    h1 = float(f[p1])
    h2 = float(f[p2])
    valley = float(np.min(f[p1:p2 + 1]))
    hv_over_max = valley / max(h1, h2) if max(h1, h2) > 0 else math.inf
    return Metrics(t1=t1, t2=t2, h1=h1, h2=h2, hv_over_max=hv_over_max)


def _metrics_from_case(summary_path: Path, exact_path: Path) -> Optional[Metrics]:
    f = np.load(exact_path)["f"]
    t = np.arange(1, f.size + 1)
    try:
        summary = json.loads(summary_path.read_text())
        pv = summary.get("peaks_valley", {})
        t1 = int(pv.get("t1", -1))
        t2 = int(pv.get("t2", -1))
        if t1 > 0 and t2 > 0 and t2 > t1 and t2 <= f.size:
            idx1 = t1 - 1
            idx2 = t2 - 1
            h1 = float(f[idx1])
            h2 = float(f[idx2])
            valley = float(np.min(f[idx1:idx2 + 1]))
            hv_over_max = valley / max(h1, h2) if max(h1, h2) > 0 else math.inf
            return Metrics(t1=float(t1), t2=float(t2), h1=h1, h2=h2, hv_over_max=hv_over_max)
    except Exception:
        pass
    return _pair_metrics(t, f)


def _discover_cases(cases_dir: Path, K: int, N: int) -> List[Tuple[float, Path, Path]]:
    results: List[Tuple[float, Path, Path]] = []
    if not cases_dir.exists():
        return results
    for summary_path in cases_dir.glob("**/*.summary.json"):
        try:
            data = json.loads(summary_path.read_text())
        except json.JSONDecodeError:
            continue
        params = data.get("params", {})
        if int(params.get("K", -1)) != int(K):
            continue
        if int(params.get("N", -1)) != int(N):
            continue
        beta = float(params.get("beta", -999))
        exact_path = next(summary_path.parent.glob("*.exact.npz"), None)
        if exact_path is None:
            continue
        results.append((beta, summary_path, exact_path))
    results.sort(key=lambda x: x[0])
    return results


def _evaluate(metrics: Optional[Metrics], h_min: float, second_frac: float, t2_over_t1: float, hv_over_max: float) -> bool:
    if metrics is None:
        return False
    if min(metrics.h1, metrics.h2) < h_min:
        return False
    if metrics.h1 <= 0:
        return False
    if (metrics.h2 / metrics.h1) < second_frac:
        return False
    if (metrics.t2 / metrics.t1) < t2_over_t1:
        return False
    if metrics.hv_over_max > hv_over_max:
        return False
    return True


def _heatmap_avg(
    df: pd.DataFrame,
    k_label: str,
    x_col: str,
    x_vals: List[float],
    y_col: str,
    y_vals: List[float],
) -> np.ndarray:
    mat = np.zeros((len(y_vals), len(x_vals)))
    sub = df[df["K"] == k_label]
    for i, y in enumerate(y_vals):
        for j, x in enumerate(x_vals):
            cell = sub[(sub[x_col] == x) & (sub[y_col] == y)]
            mat[i, j] = cell["is_bimodal"].mean() if not cell.empty else 0.0
    return mat


def main() -> None:
    parser = argparse.ArgumentParser(description="Threshold sensitivity scan for bimodality criteria.")
    parser.add_argument("--ft-csv", required=True, type=Path)
    parser.add_argument("--col-t", default="t")
    parser.add_argument("--col-k2", default="f_K2")
    parser.add_argument("--col-k4", default="f_K4")
    parser.add_argument("--beta", type=float, default=0.01)
    parser.add_argument("--beta-list", type=str, default=None)
    parser.add_argument("--cases-dir", type=Path, default=None)
    parser.add_argument("--use-cases", action="store_true")
    parser.add_argument("--N", type=int, default=100)
    parser.add_argument("--out-csv", required=True, type=Path)
    parser.add_argument("--out-fig", required=True, type=Path)
    args = parser.parse_args()

    df = pd.read_csv(args.ft_csv)
    t = df[args.col_t].to_numpy()

    series: Dict[str, Optional[np.ndarray]] = {}
    if args.col_k2 in df.columns:
        series["K=2"] = df[args.col_k2].to_numpy()
    if args.col_k4 in df.columns:
        series["K=4"] = df[args.col_k4].to_numpy()
    if not series:
        raise ValueError("No f(t) columns found for K=2 or K=4")

    thresholds_h_min = [1e-8, 1e-7, 1e-6]
    thresholds_second_frac = [0.005, 0.01, 0.02]
    thresholds_t2_over_t1 = [8, 10, 12]
    thresholds_hv = [0.10, 0.20, 0.30]

    rows = []
    root = Path(__file__).resolve().parents[1]
    cases_dir = args.cases_dir or (root / "outputs" / "mc_beta_sweep_N100" / "cases")
    beta_list: Optional[List[float]] = None
    if args.beta_list:
        beta_list = [float(b) for b in args.beta_list.split(",") if b.strip()]

    use_cases = bool(args.use_cases or beta_list or cases_dir.exists())

    if use_cases:
        for k_label in series.keys():
            K = int(k_label.split("=")[1])
            cases = _discover_cases(cases_dir, K=K, N=args.N)
            if beta_list is not None:
                cases = [c for c in cases if c[0] in beta_list]
            if not cases:
                _warn(f"No cases found for {k_label}; falling back to ft-csv.")
                use_cases = False
                break
            for beta, summary_path, exact_path in cases:
                metrics = _metrics_from_case(summary_path, exact_path)
                for h_min, second_frac, t2_over_t1, hv_over_max in itertools.product(
                    thresholds_h_min, thresholds_second_frac, thresholds_t2_over_t1, thresholds_hv
                ):
                    is_bimodal = _evaluate(metrics, h_min, second_frac, t2_over_t1, hv_over_max)
                    rows.append(
                        {
                            "K": k_label,
                            "beta": beta,
                            "h_min": h_min,
                            "second_frac": second_frac,
                            "t2_over_t1": t2_over_t1,
                            "hv_over_max_thresh": hv_over_max,
                            "t1": None if metrics is None else metrics.t1,
                            "t2": None if metrics is None else metrics.t2,
                            "h1": None if metrics is None else metrics.h1,
                            "h2": None if metrics is None else metrics.h2,
                            "hv_over_max": None if metrics is None else metrics.hv_over_max,
                            "is_bimodal": int(is_bimodal),
                            "source": "cases",
                        }
                    )

    if not use_cases:
        for k_label, f in series.items():
            if f is None:
                continue
            metrics = _pair_metrics(t, f)
            for h_min, second_frac, t2_over_t1, hv_over_max in itertools.product(
                thresholds_h_min, thresholds_second_frac, thresholds_t2_over_t1, thresholds_hv
            ):
                is_bimodal = _evaluate(metrics, h_min, second_frac, t2_over_t1, hv_over_max)
                rows.append(
                    {
                        "K": k_label,
                        "beta": args.beta,
                        "h_min": h_min,
                        "second_frac": second_frac,
                        "t2_over_t1": t2_over_t1,
                        "hv_over_max_thresh": hv_over_max,
                        "t1": None if metrics is None else metrics.t1,
                        "t2": None if metrics is None else metrics.t2,
                        "h1": None if metrics is None else metrics.h1,
                        "h2": None if metrics is None else metrics.h2,
                        "hv_over_max": None if metrics is None else metrics.hv_over_max,
                        "is_bimodal": int(is_bimodal),
                        "source": "ft_csv",
                    }
                )

    out_df = pd.DataFrame(rows)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out_csv, index=False)

    second_fracs = thresholds_second_frac
    hv_thresholds = thresholds_hv

    k_labels = [k for k in ["K=2", "K=4"] if k in series] + [k for k in series.keys() if k not in ["K=2", "K=4"]]
    fig, axes = plt.subplots(len(k_labels), 2, figsize=(10.8, 6.2), dpi=160, sharex=False, sharey=False)
    if len(k_labels) == 1:
        axes = np.array([axes])

    for r, k_label in enumerate(k_labels):
        ax0 = axes[r, 0]
        ax1 = axes[r, 1]

        mat_hv = _heatmap_avg(out_df, k_label, "hv_over_max_thresh", hv_thresholds, "second_frac", second_fracs)
        im0 = ax0.imshow(mat_hv, origin="lower", cmap="Blues", vmin=0, vmax=1)
        ax0.set_title(f"{k_label}: hv_over_max vs second_frac", fontsize=10)
        ax0.set_xticks(range(len(hv_thresholds)))
        ax0.set_xticklabels([f"{v:.2f}" for v in hv_thresholds])
        ax0.set_yticks(range(len(second_fracs)))
        ax0.set_yticklabels([f"{v:.3f}" for v in second_fracs])
        ax0.set_xlabel("hv_over_max", fontsize=9)
        ax0.set_ylabel("second_frac", fontsize=9)
        ax0.tick_params(labelsize=8)

        mat_t = _heatmap_avg(out_df, k_label, "t2_over_t1", thresholds_t2_over_t1, "h_min", thresholds_h_min)
        im1 = ax1.imshow(mat_t, origin="lower", cmap="Blues", vmin=0, vmax=1)
        ax1.set_title(f"{k_label}: t2/t1 vs h_min", fontsize=10)
        ax1.set_xticks(range(len(thresholds_t2_over_t1)))
        ax1.set_xticklabels([str(v) for v in thresholds_t2_over_t1])
        ax1.set_yticks(range(len(thresholds_h_min)))
        ax1.set_yticklabels([f"{v:.0e}" for v in thresholds_h_min])
        ax1.set_xlabel("t2/t1", fontsize=9)
        ax1.set_ylabel("h_min", fontsize=9)
        ax1.tick_params(labelsize=8)

        for i in range(mat_hv.shape[0]):
            for j in range(mat_hv.shape[1]):
                val = mat_hv[i, j]
                ax0.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7, color="white" if val > 0.5 else "black")
        for i in range(mat_t.shape[0]):
            for j in range(mat_t.shape[1]):
                val = mat_t[i, j]
                ax1.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7, color="white" if val > 0.5 else "black")

    fig.subplots_adjust(wspace=0.3, hspace=0.35, right=0.9)
    cax = fig.add_axes([0.92, 0.16, 0.02, 0.68])
    fig.colorbar(im0, cax=cax, label="pass rate")
    args.out_fig.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out_fig, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
