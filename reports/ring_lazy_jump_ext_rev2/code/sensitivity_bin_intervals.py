#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_MPL_CACHE = Path(__file__).resolve().parents[1] / "build" / "mpl_cache"
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))
_MPL_CACHE.mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
    print(f"[sensitivity_bin_intervals] {msg}", file=sys.stderr)


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


def _baseline_props(data: dict, k_label: str) -> Dict[str, Dict[str, float]]:
    counts = data.get("counts", {}).get(k_label, {})
    props: Dict[str, Dict[str, float]] = {}
    for window in WINDOWS:
        cls_counts = counts.get(window, {})
        total = sum(cls_counts.values())
        if total <= 0:
            props[window] = {cls: 0.0 for cls in CLASSES}
        else:
            props[window] = {cls: cls_counts.get(cls, 0) / float(total) for cls in CLASSES}
    return props


def _centers_from_intervals(bin_intervals: Dict[str, List[int]]) -> Dict[str, float]:
    return {w: 0.5 * (float(bin_intervals[w][0]) + float(bin_intervals[w][1])) for w in WINDOWS}


def _impute_class_probs(df: pd.DataFrame, centers: Dict[str, float], props: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    df = df.copy()
    class_cols = [f"class_{cls}" for cls in CLASSES]
    invalid = df[class_cols].isna().any(axis=1)
    if invalid.any():
        for idx in df[invalid].index:
            t = float(df.at[idx, "t"])
            nearest = min(WINDOWS, key=lambda w: abs(t - centers[w]))
            for cls in CLASSES:
                df.at[idx, f"class_{cls}"] = props[nearest][cls]
    row_sum = df[class_cols].sum(axis=1)
    ok = row_sum > 0
    if ok.any():
        df.loc[ok, class_cols] = df.loc[ok, class_cols].div(row_sum[ok], axis=0)
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
        counts[cls] = float((wdf["n"] * wdf[f"class_{cls}"].fillna(0)).sum())
    return counts, total_n


def main() -> None:
    parser = argparse.ArgumentParser(description="Window boundary sensitivity for fig2 bins.")
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
    deltas = [-5, -2, -1, 0, 1, 2, 5]
    centers = _centers_from_intervals(bin_intervals)
    base_props_k2 = _baseline_props(data, "K=2")
    base_props_k4 = _baseline_props(data, "K=4")

    root = args.input_json.parent.parent
    cond_k2 = args.cond_by_t_k2 or _find_case(root, args.beta, K=2, N=args.N)
    cond_k4 = args.cond_by_t_k4 or _find_case(root, args.beta, K=4, N=args.N)

    if cond_k2 is None or cond_k4 is None:
        _warn("Missing cond_by_t inputs; using baseline proportions without recomputation.")
        rows = []
        proportions = data.get("proportions", {})
        n_windows = data.get("n_windows", {})
        for k_label, win_map in proportions.items():
            for window in WINDOWS:
                base_props = win_map.get(window, {})
                base_n = int(n_windows.get(k_label, {}).get(window, 0))
                for delta in deltas:
                    for mode in ["shift", "width"]:
                        for cls in CLASSES:
                            base = float(base_props.get(cls, 0.0))
                            rows.append(
                                {
                                    "K": k_label,
                                    "window": window,
                                    "class": cls,
                                    "mode": mode,
                                    "delta": delta,
                                    "prop": base,
                                    "baseline_prop": base,
                                    "delta_prop": 0.0,
                                    "n": base_n,
                                }
                            )
        out_df = pd.DataFrame(rows)
        args.out_csv.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(args.out_csv, index=False)
        _plot_delta(out_df, args.out_fig)
        return

    df_k2 = _impute_class_probs(_load_cond_by_t(cond_k2), centers, base_props_k2)
    df_k4 = _impute_class_probs(_load_cond_by_t(cond_k4), centers, base_props_k4)

    rows = []
    for k_label, df in [("K=2", df_k2), ("K=4", df_k4)]:
        baseline_props: Dict[str, Dict[str, float]] = base_props_k2 if k_label == "K=2" else base_props_k4
        baseline_totals: Dict[str, int] = data.get("n_windows", {}).get(k_label, {})
        t_min = int(df["t"].min())
        t_max = int(df["t"].max())

        for window in WINDOWS:
            tL0, tR0 = bin_intervals[window]
            for delta in deltas:
                for mode in ["shift", "width"]:
                    if mode == "shift":
                        tL = int(tL0 + delta)
                        tR = int(tR0 + delta)
                    else:
                        tL = int(tL0 - delta)
                        tR = int(tR0 + delta)
                    tL = max(t_min, tL)
                    tR = min(t_max, tR)
                    if tL >= tR:
                        continue
                    counts, total_n = _window_counts(df, tL, tR)
                    for cls in CLASSES:
                        prop = counts[cls] / total_n if total_n > 0 else 0.0
                        base = baseline_props[window][cls]
                        rows.append(
                            {
                                "K": k_label,
                                "window": window,
                                "class": cls,
                                "mode": mode,
                                "delta": delta,
                                "prop": prop,
                                "baseline_prop": base,
                                "delta_prop": prop - base,
                                "n": total_n,
                            }
                        )

    out_df = pd.DataFrame(rows)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out_csv, index=False)

    _plot_delta(out_df, args.out_fig)


def _plot_delta(out_df: pd.DataFrame, out_fig: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(11.0, 5.6), dpi=160, sharex=True, sharey=True)
    axes = axes.reshape(2, 3)
    max_abs = float(out_df["delta_prop"].abs().max()) if not out_df.empty else 0.0
    y_lim = max(0.003, max_abs * 1.4)
    for r, k_label in enumerate(["K=2", "K=4"]):
        for c, window in enumerate(WINDOWS):
            ax = axes[r, c]
            sub = out_df[(out_df["K"] == k_label) & (out_df["window"] == window)]
            for cls in CLASSES:
                cls_df = sub[sub["class"] == cls]
                for mode, style, marker in [("shift", "-", "o"), ("width", "--", "s")]:
                    mode_df = cls_df[cls_df["mode"] == mode]
                    ax.plot(
                        mode_df["delta"],
                        mode_df["delta_prop"],
                        marker=marker,
                        lw=1.2,
                        ls=style,
                        color=CLASS_COLORS.get(cls, "0.4"),
                    )
            ax.axhline(0, color="0.5", lw=0.8)
            ax.set_title(f"{k_label} / {window}")
            ax.set_xlabel("delta")
            ax.set_ylabel("Δprop")
            ax.set_ylim(-y_lim, y_lim)
            ax.grid(True, alpha=0.2)
            if not sub.empty:
                ax.text(
                    0.02,
                    0.92,
                    f"max|Δ|={sub['delta_prop'].abs().max():.3g}",
                    transform=ax.transAxes,
                    fontsize=7,
                    color="0.25",
                )
    class_handles = [plt.Line2D([0], [0], color=CLASS_COLORS[c], lw=2, label=c) for c in CLASSES]
    mode_handles = [
        plt.Line2D([0], [0], color="0.2", lw=1.5, ls="-", marker="o", label="shift"),
        plt.Line2D([0], [0], color="0.2", lw=1.5, ls="--", marker="s", label="width"),
    ]
    fig.legend(handles=class_handles + mode_handles, loc="upper center", ncol=6, frameon=False)
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    out_fig.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_fig, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
