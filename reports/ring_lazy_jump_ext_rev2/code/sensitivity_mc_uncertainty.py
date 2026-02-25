#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

_MPL_CACHE = Path(__file__).resolve().parents[1] / "build" / "mpl_cache"
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))
_MPL_CACHE.mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

WINDOWS = ["peak1", "valley", "peak2"]
CLASSES = ["C0J0", "C1pJ0", "C0J1p", "C1pJ1p"]
CLASS_COLORS = {
    "C0J0": "#264653",
    "C1pJ0": "#E76F51",
    "C0J1p": "#2A9D8F",
    "C1pJ1p": "#F4A261",
}


def _warn(msg: str) -> None:
    print(f"[sensitivity_mc_uncertainty] {msg}", file=sys.stderr)


def _load_cond_by_t(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["t", "n"]:
        if col not in df.columns:
            raise ValueError(f"cond_by_t missing column: {col}")
    for cls in CLASSES:
        col = f"class_{cls}"
        if col not in df.columns:
            raise ValueError(f"cond_by_t missing column: {col}")
    df = df.copy()
    df["n"] = df["n"].fillna(0)
    return df


def _find_case(root: Path, beta: float, K: int, N: int) -> Optional[Path]:
    cases_dir = root / "outputs" / "mc_beta_sweep_N100" / "cases"
    if not cases_dir.exists():
        return None
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
        if abs(float(params.get("beta", -999)) - beta) > 1e-6:
            continue
        case_dir = summary_path.parent
        cond = next(iter(case_dir.glob("*.cond_by_t.csv")), None)
        if cond is not None:
            return cond
    return None


def _window_counts(df: pd.DataFrame, tL: int, tR: int) -> Tuple[Dict[str, float], int]:
    wdf = df[(df["t"] >= tL) & (df["t"] <= tR)]
    total_n = int(wdf["n"].sum())
    counts: Dict[str, float] = {}
    for cls in CLASSES:
        counts[cls] = float((wdf["n"] * wdf[f"class_{cls}"]).sum())
    return counts, total_n


def _fallback_props(counts: Dict[str, int]) -> Dict[str, float]:
    total = sum(counts.values())
    if total <= 0:
        return {cls: 0.0 for cls in CLASSES}
    return {cls: counts.get(cls, 0) / float(total) for cls in CLASSES}


def _window_counts_imputed(
    df: pd.DataFrame,
    tL: int,
    tR: int,
    fallback_props: Dict[str, float],
) -> Tuple[Dict[str, float], int]:
    wdf = df[(df["t"] >= tL) & (df["t"] <= tR)].copy()
    if wdf.empty:
        return {cls: 0.0 for cls in CLASSES}, 0
    class_cols = [f"class_{cls}" for cls in CLASSES]
    invalid = wdf[class_cols].isna().any(axis=1)
    if invalid.any():
        for cls in CLASSES:
            wdf.loc[invalid, f"class_{cls}"] = fallback_props.get(cls, 0.0)
    # normalize rows to sum 1 where possible
    row_sum = wdf[class_cols].sum(axis=1)
    ok = row_sum > 0
    if ok.any():
        wdf.loc[ok, class_cols] = wdf.loc[ok, class_cols].div(row_sum[ok], axis=0)
    total_n = int(wdf["n"].sum())
    counts: Dict[str, float] = {}
    for cls in CLASSES:
        counts[cls] = float((wdf["n"] * wdf[f"class_{cls}"]).sum())
    return counts, total_n


def _normal_ci(p: float, n: int, z: float = 1.96) -> Tuple[float, float, float]:
    if n <= 0:
        return (p, p, 0.0)
    se = float(np.sqrt(max(p * (1 - p), 0.0) / n))
    lo = max(0.0, p - z * se)
    hi = min(1.0, p + z * se)
    return (lo, hi, se)


def main() -> None:
    parser = argparse.ArgumentParser(description="MC uncertainty estimates for fig2 proportions.")
    parser.add_argument("--input-json", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    parser.add_argument("--out-fig", required=True, type=Path)
    parser.add_argument("--cond-by-t-k2", type=Path, default=None)
    parser.add_argument("--cond-by-t-k4", type=Path, default=None)
    parser.add_argument("--beta", type=float, default=0.01)
    parser.add_argument("--N", type=int, default=100)
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text())
    bin_intervals = data["bin_intervals"]

    root = args.input_json.parent.parent
    cond_k2 = args.cond_by_t_k2 or _find_case(root, args.beta, K=2, N=args.N)
    cond_k4 = args.cond_by_t_k4 or _find_case(root, args.beta, K=4, N=args.N)

    if cond_k2 is None or cond_k4 is None:
        _warn("Missing cond_by_t inputs; falling back to counts in JSON if available.")

    rows = []
    for k_label, cond in [("K=2", cond_k2), ("K=4", cond_k4)]:
        json_counts = data.get("counts", {}).get(k_label, {})
        if cond is not None:
            df = _load_cond_by_t(cond)
            for window in WINDOWS:
                tL, tR = bin_intervals[window]
                fallback_props = _fallback_props(json_counts.get(window, {}))
                counts, total_n = _window_counts_imputed(df, tL, tR, fallback_props)
                if total_n <= 0:
                    counts = {cls: float(json_counts.get(window, {}).get(cls, 0.0)) for cls in CLASSES}
                    total_n = int(sum(counts.values()))
                for cls in CLASSES:
                    prop = counts[cls] / total_n if total_n > 0 else 0.0
                    ci_low, ci_high, se = _normal_ci(prop, total_n)
                    rows.append(
                        {
                            "K": k_label,
                            "window": window,
                            "class": cls,
                            "prop": prop,
                            "SE": se,
                            "ci_low": ci_low,
                            "ci_high": ci_high,
                            "n": total_n,
                        }
                    )
        elif "counts" in data:
            counts_data = json_counts
            for window in WINDOWS:
                cls_counts = counts_data.get(window, {})
                total_n = int(sum(cls_counts.values()))
                for cls in CLASSES:
                    prop = (cls_counts.get(cls, 0) / total_n) if total_n > 0 else 0.0
                    ci_low, ci_high, se = _normal_ci(prop, total_n)
                    rows.append(
                        {
                            "K": k_label,
                            "window": window,
                            "class": cls,
                            "prop": prop,
                            "SE": se,
                            "ci_low": ci_low,
                            "ci_high": ci_high,
                            "n": total_n,
                        }
                    )
        else:
            _warn(f"No counts available for {k_label}; skipping.")

    out_df = pd.DataFrame(rows)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out_csv, index=False)

    k_labels = [k for k in ["K=2", "K=4"] if k in out_df["K"].unique()]
    if not k_labels:
        _warn("No rows available to plot.")
        return

    max_ci = float(out_df["ci_high"].max()) if not out_df.empty else 0.4
    y_max = min(1.0, max(0.4, max_ci * 1.15))

    fig, axes = plt.subplots(len(k_labels), len(WINDOWS), figsize=(11.2, 5.6), dpi=160, sharey=True)
    if len(k_labels) == 1:
        axes = np.array([axes])

    for r, k_label in enumerate(k_labels):
        for c, window in enumerate(WINDOWS):
            ax = axes[r, c]
            sub = out_df[(out_df["K"] == k_label) & (out_df["window"] == window)]
            heights = []
            errors = []
            for cls in CLASSES:
                row = sub[sub["class"] == cls]
                if row.empty:
                    heights.append(0.0)
                    errors.append((0.0, 0.0))
                    continue
                prop = float(row["prop"].iloc[0])
                ci_low = float(row["ci_low"].iloc[0])
                ci_high = float(row["ci_high"].iloc[0])
                heights.append(prop)
                errors.append((prop - ci_low, ci_high - prop))
            x = np.arange(len(CLASSES))
            ax.bar(
                x,
                heights,
                yerr=np.array(errors).T,
                color=[CLASS_COLORS[c] for c in CLASSES],
                edgecolor="white",
                capsize=3,
            )
            if r == 0:
                ax.set_title(window)
            ax.set_xticks(x)
            ax.set_xticklabels(CLASSES, rotation=35, ha="right", fontsize=7)
            if c == 0:
                ax.set_ylabel(f"{k_label}\nprop")
            ax.set_ylim(0, y_max)
            ax.grid(axis="y", alpha=0.2)

    fig.suptitle("MC uncertainty (normal approx, 95% CI)")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    args.out_fig.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out_fig, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
