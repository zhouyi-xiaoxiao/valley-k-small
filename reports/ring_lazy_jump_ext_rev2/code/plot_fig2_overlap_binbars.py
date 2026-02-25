#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_MPL_CACHE = Path(__file__).resolve().parents[1] / "build" / "mpl_cache"
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))
_MPL_CACHE.mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch, Rectangle


WINDOW_ORDER = ["peak1", "valley", "peak2"]
CLASS_ORDER = ["C0J0", "C1pJ0", "C0J1p", "C1pJ1p"]
DEFAULT_CLASS_COLORS = {
    "C0J0": "#264653",
    "C1pJ0": "#D62828",
    "C0J1p": "#2A9D8F",
    "C1pJ1p": "#F2C14E",
}
LINE_COLORS = {
    "K=2": "#2B2D42",
    "K=4": "#D90429",
}


@dataclass
class UncertaintyEntry:
    ci_low: float
    ci_high: float


def _warn(msg: str) -> None:
    print(f"[plot_fig2_overlap_binbars] {msg}", file=sys.stderr)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_ft_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _collect_column_map(df_ft: pd.DataFrame, col_k2: Optional[str], col_k4: Optional[str]) -> Dict[str, str]:
    col_map: Dict[str, str] = {}
    if col_k2 and col_k2 in df_ft.columns:
        col_map["K=2"] = col_k2
    if col_k4 and col_k4 in df_ft.columns:
        col_map["K=4"] = col_k4
    for col in df_ft.columns:
        if not col.startswith("f_K"):
            continue
        suffix = col[3:]
        if not suffix.isdigit():
            continue
        label = f"K={int(suffix)}"
        col_map.setdefault(label, col)
    return col_map


def _compute_plot_bounds(t: np.ndarray, bin_intervals: Dict[str, Tuple[float, float]]) -> Tuple[float, float, float, float]:
    t_min, t_max = float(np.min(t)), float(np.max(t))
    window_min = min(bin_intervals[w][0] for w in WINDOW_ORDER)
    window_max = max(bin_intervals[w][1] for w in WINDOW_ORDER)
    margin = max(10.0, 0.15 * (window_max - window_min))
    plot_min = max(t_min, window_min - margin)
    plot_max = min(t_max, window_max + margin)
    return t_min, t_max, plot_min, plot_max


def _compute_plot_bounds_multi(
    t: np.ndarray, interval_sets: List[Dict[str, Tuple[float, float]]]
) -> Tuple[float, float, float, float]:
    t_min, t_max = float(np.min(t)), float(np.max(t))
    if not interval_sets:
        return t_min, t_max, t_min, t_max
    window_min = min(intervals[w][0] for intervals in interval_sets for w in WINDOW_ORDER)
    window_max = max(intervals[w][1] for intervals in interval_sets for w in WINDOW_ORDER)
    margin = max(10.0, 0.15 * (window_max - window_min))
    plot_min = max(t_min, window_min - margin)
    plot_max = min(t_max, window_max + margin)
    return t_min, t_max, plot_min, plot_max


def _get_bin_intervals(data: dict, k_label: str) -> Dict[str, Tuple[float, float]]:
    per_k = data.get("bin_intervals_by_k")
    if isinstance(per_k, dict) and k_label in per_k:
        return per_k[k_label]
    return data["bin_intervals"]


def _validate_bin_intervals(bin_intervals: Dict[str, Tuple[float, float]], t_min: float, t_max: float, label: str) -> None:
    for window in WINDOW_ORDER:
        tL, tR = bin_intervals[window]
        if tL < t_min or tR > t_max:
            raise ValueError(
                f"{label} bin_intervals[{window}] out of range: [{tL},{tR}] not within t=[{t_min},{t_max}]."
                " Fix by tightening windows or extending f(t) range."
            )


def _annotate_windows(
    ax: plt.Axes,
    bin_intervals: Dict[str, Tuple[float, float]],
    *,
    x_span: Optional[float] = None,
    x_limits: Optional[Tuple[float, float]] = None,
) -> None:
    centers = {w: int(round((bin_intervals[w][0] + bin_intervals[w][1]) / 2)) for w in WINDOW_ORDER}
    center_labels = {"peak1": "t1", "valley": "t_v", "peak2": "t2"}
    trans = ax.get_xaxis_transform()
    centers_list = [centers[w] for w in WINDOW_ORDER]
    labels = [f"{center_labels[w]}={centers[w]}" for w in WINDOW_ORDER]
    x_pos = [float(c) for c in centers_list]
    y_offsets = [0.0 for _ in centers_list]
    halign = ["center" for _ in centers_list]
    if x_span is not None:
        min_gap = max(60.0, min(140.0, 0.10 * float(x_span)))
        char_w = 0.009
        widths = [char_w * float(x_span) * max(3, len(lbl)) for lbl in labels]
        pad = 0.01 * float(x_span)
        for i in range(1, len(x_pos)):
            gap = x_pos[i] - x_pos[i - 1]
            min_allowed = (widths[i] + widths[i - 1]) / 2.0 + pad
            if gap < min_allowed:
                shift = 0.5 * (min_allowed - gap)
                x_pos[i - 1] -= shift
                x_pos[i] += shift
                y_offsets[i] = max(y_offsets[i], y_offsets[i - 1] + 0.08)
        if x_limits is not None:
            x_min, x_max = x_limits
            for i in range(len(x_pos)):
                if x_pos[i] < x_min:
                    x_pos[i] = x_min
                    y_offsets[i] = max(y_offsets[i], 0.1)
                elif x_pos[i] > x_max:
                    x_pos[i] = x_max
                    y_offsets[i] = max(y_offsets[i], 0.1)
        for i in range(1, len(x_pos)):
            gap = abs(x_pos[i] - x_pos[i - 1])
            if gap < min_gap:
                y_offsets[i] = max(y_offsets[i], y_offsets[i - 1] + 0.08)
    for window in WINDOW_ORDER:
        center = centers[window]
        idx = WINDOW_ORDER.index(window)
        x_loc = x_pos[idx]
        if x_loc < center:
            halign[idx] = "right"
        elif x_loc > center:
            halign[idx] = "left"
        ax.axvline(center, color="0.25", lw=0.9, ls=":", zorder=7)
        ax.text(
            x_loc,
            1.01 + y_offsets[idx],
            labels[idx],
            transform=trans,
            ha=halign[idx],
            va="bottom",
            fontsize=8,
            color="0.2",
            clip_on=False,
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=1.0),
        )
        tL, tR = bin_intervals[window]
        label = f"{window}\n[{tL},{tR}]"
        base_y = 0.82
        alt_y = 0.54
        label_y = base_y if (idx % 2 == 0) else alt_y
        ax.text(
            (tL + tR) / 2.0,
            label_y,
            label,
            transform=trans,
            ha="center",
            va="bottom",
            fontsize=7,
            color="0.2",
            bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=0.6),
        )


def _annotate_line_label(
    ax: plt.Axes,
    t: np.ndarray,
    y: np.ndarray,
    label: str,
    color: str,
    plot_min: float,
    plot_max: float,
    frac: float,
) -> None:
    y_min, y_max = ax.get_ylim()
    y_pad = 0.02 * (y_max - y_min)
    x_pos = plot_min + frac * (plot_max - plot_min)
    idx = int(np.argmin(np.abs(t - x_pos)))
    y_val = float(y[idx])
    y_text = min(y_val + y_pad, y_max * 0.98)
    ax.text(
        float(t[idx]),
        y_text,
        label,
        color=color,
        fontsize=8,
        ha="left",
        va="bottom",
        bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", pad=0.8),
    )


def _draw_window_bars(
    ax: plt.Axes,
    *,
    k_label: str,
    proportions: Dict[str, Dict[str, Dict[str, float]]],
    class_colors: Dict[str, str],
    bin_intervals: Dict[str, Tuple[float, float]],
    y0: float,
    row_h: float,
    show_ci: bool,
    ci_entries: Optional[Dict[Tuple[str, str, str], UncertaintyEntry]],
) -> None:
    trans = ax.get_xaxis_transform()
    for window in WINDOW_ORDER:
        tL, tR = bin_intervals[window]
        width = float(tR - tL)
        cum_prop = 0.0
        for cls in CLASS_ORDER:
            prop = float(proportions[k_label][window][cls])
            height = prop * row_h
            rect = Rectangle(
                (tL, y0 + cum_prop * row_h),
                width,
                height,
                transform=trans,
                facecolor=class_colors.get(cls, DEFAULT_CLASS_COLORS[cls]),
                alpha=0.6,
                edgecolor="white",
                linewidth=0.4,
                zorder=2,
            )
            ax.add_patch(rect)

            if show_ci and ci_entries is not None:
                key = (k_label, window, cls)
                if key in ci_entries:
                    ci = ci_entries[key]
                    y_low = y0 + (cum_prop + float(ci.ci_low)) * row_h
                    y_high = y0 + (cum_prop + float(ci.ci_high)) * row_h
                    x_center = tL + width / 2.0
                    ax.plot([x_center, x_center], [y_low, y_high], transform=trans, color="0.2", lw=0.8, zorder=4)
                    cap = width * 0.08
                    ax.plot(
                        [x_center - cap / 2.0, x_center + cap / 2.0],
                        [y_low, y_low],
                        transform=trans,
                        color="0.2",
                        lw=0.8,
                        zorder=4,
                    )
                    ax.plot(
                        [x_center - cap / 2.0, x_center + cap / 2.0],
                        [y_high, y_high],
                        transform=trans,
                        color="0.2",
                        lw=0.8,
                        zorder=4,
                    )

            cum_prop += prop

        outline = Rectangle(
            (tL, y0),
            width,
            row_h,
            transform=trans,
            fill=False,
            edgecolor="0.2",
            linewidth=0.6,
            zorder=3,
        )
        ax.add_patch(outline)


def _normalize_props(props: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, Dict[str, Dict[str, float]]]:
    normalized: Dict[str, Dict[str, Dict[str, float]]] = {}
    for k_label, windows in props.items():
        normalized[k_label] = {}
        for window, class_map in windows.items():
            total = float(sum(class_map.values()))
            if total <= 0:
                raise ValueError(f"proportions sum <= 0 for {k_label}/{window}")
            if abs(total - 1.0) > 1e-3:
                _warn(f"{k_label}/{window} proportions sum={total:.6f}; renormalizing")
            normalized[k_label][window] = {c: float(v) / total for c, v in class_map.items()}
    return normalized


def _check_keys(data: dict) -> None:
    required = ["windows", "bin_colors", "classes", "class_colors", "bin_intervals", "proportions"]
    for key in required:
        if key not in data:
            raise KeyError(f"missing key: {key}")
    for window in WINDOW_ORDER:
        if window not in data["bin_intervals"]:
            raise KeyError(f"missing bin_intervals for window: {window}")
    for cls in CLASS_ORDER:
        if cls not in data["class_colors"]:
            raise KeyError(f"missing class_colors for class: {cls}")

    for k_label, win_map in data["proportions"].items():
        for window in WINDOW_ORDER:
            if window not in win_map:
                raise KeyError(f"missing proportions[{k_label}][{window}]")
            for cls in CLASS_ORDER:
                if cls not in win_map[window]:
                    raise KeyError(f"missing proportions[{k_label}][{window}][{cls}]")


def _load_uncertainty(path: Path) -> Dict[Tuple[str, str, str], UncertaintyEntry]:
    entries: Dict[Tuple[str, str, str], UncertaintyEntry] = {}
    df = pd.read_csv(path)
    required_cols = {"K", "window", "class", "ci_low", "ci_high"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"mc_uncertainty.csv missing columns: {sorted(missing)}")
    for _, row in df.iterrows():
        key = (str(row["K"]), str(row["window"]), str(row["class"]))
        entries[key] = UncertaintyEntry(ci_low=float(row["ci_low"]), ci_high=float(row["ci_high"]))
    return entries


def _plot(
    data: dict,
    df_ft: pd.DataFrame,
    outpath: Path,
    col_t: str,
    col_k2: Optional[str],
    col_k4: Optional[str],
    band_y0: float,
    band_h: float,
    bar_k: str,
    layout: str,
    xlim: Optional[Tuple[float, float]],
    show_ci: bool,
    ci_entries: Optional[Dict[Tuple[str, str, str], UncertaintyEntry]],
) -> None:
    t = df_ft[col_t].to_numpy()
    bin_intervals = data["bin_intervals"]

    proportions = _normalize_props(data["proportions"])
    col_map = _collect_column_map(df_ft, col_k2, col_k4)

    k_labels = list(proportions.keys())
    k_labels_sorted = [k for k in ["K=2", "K=4"] if k in k_labels] + [k for k in k_labels if k not in ["K=2", "K=4"]]

    class_handles = [
        Patch(facecolor=data["class_colors"].get(cls, DEFAULT_CLASS_COLORS[cls]), edgecolor="0.2", label=cls)
        for cls in CLASS_ORDER
    ]

    layout_labels = k_labels_sorted
    if bar_k != "both":
        if bar_k not in proportions:
            raise KeyError(f"--bar-k {bar_k} not found in proportions keys: {sorted(proportions.keys())}")
        layout_labels = [bar_k]

    interval_sets = []
    for label in layout_labels:
        interval_sets.append(_get_bin_intervals(data, label))
    t_min, t_max, plot_min, plot_max = _compute_plot_bounds_multi(t, interval_sets)
    if xlim is not None:
        x_min, x_max = xlim
        plot_min = max(t_min, float(x_min))
        plot_max = min(t_max, float(x_max))
        if plot_min >= plot_max:
            raise ValueError(f"--xlim {xlim} yields empty range within t=[{t_min},{t_max}].")
    for label, intervals in zip(layout_labels, interval_sets):
        _validate_bin_intervals(intervals, t_min, t_max, label)

    if layout == "overlap":
        fig, ax = plt.subplots(figsize=(8.6, 4.8), dpi=160)
        line_data: Dict[str, np.ndarray] = {}
        if col_k2 and col_k2 in df_ft.columns:
            y_k2 = df_ft[col_k2].to_numpy()
            ax.plot(t, y_k2, lw=1.8, color=LINE_COLORS.get("K=2", "#2B2D42"), zorder=6)
            line_data["K=2"] = y_k2
        if col_k4 and col_k4 in df_ft.columns:
            y_k4 = df_ft[col_k4].to_numpy()
            ax.plot(t, y_k4, lw=1.8, color=LINE_COLORS.get("K=4", "#D90429"), zorder=6)
            line_data["K=4"] = y_k4

        ax.set_xlabel("t (time steps)")
        ax.set_ylabel("f(t)")
        ax.set_xlim(plot_min, plot_max)
        ax.set_ylim(bottom=0)

        bar_labels = layout_labels
        n_k = len(bar_labels)
        row_gap = band_h * 0.05 if n_k > 1 else 0.0
        row_h = (band_h - row_gap * (n_k - 1)) / max(n_k, 1)
        if n_k > 1:
            for k_idx, k_label in enumerate(bar_labels):
                y0 = band_y0 + (n_k - 1 - k_idx) * (row_h + row_gap)
                ax.text(
                    0.01,
                    y0 + row_h / 2.0,
                    k_label,
                    transform=ax.transAxes,
                    ha="left",
                    va="center",
                    fontsize=8,
                    color="0.2",
                )
        for k_idx, k_label in enumerate(bar_labels):
            y0 = band_y0 + (n_k - 1 - k_idx) * (row_h + row_gap)
            _draw_window_bars(
                ax,
                k_label=k_label,
                proportions=proportions,
                class_colors=data["class_colors"],
                bin_intervals=_get_bin_intervals(data, k_label),
                y0=y0,
                row_h=row_h,
                show_ci=show_ci,
                ci_entries=ci_entries,
            )
        if bar_k == "both":
            _annotate_windows(
                ax,
                bin_intervals,
                x_span=plot_max - plot_min,
                x_limits=(plot_min, plot_max),
            )
        else:
            _annotate_windows(
                ax,
                _get_bin_intervals(data, bar_k),
                x_span=plot_max - plot_min,
                x_limits=(plot_min, plot_max),
            )

        for label, frac in [("K=2", 0.70), ("K=4", 0.45)]:
            if label not in line_data:
                continue
            _annotate_line_label(
                ax,
                t,
                line_data[label],
                f"{label} f(t)",
                LINE_COLORS.get(label, "0.2"),
                plot_min,
                plot_max,
                frac,
            )

        legend_classes = ax.legend(handles=class_handles, loc="upper right", fontsize=8, frameon=True)
        ax.add_artist(legend_classes)
        ax.set_title("f(t) + windowed class composition bars")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        outpath.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(outpath, bbox_inches="tight")
        plt.close(fig)
        return

    if layout != "stacked":
        raise ValueError(f"Unknown layout: {layout}")

    panel_labels = layout_labels

    nrows = max(1, len(panel_labels))
    fig, axes = plt.subplots(nrows=nrows, ncols=1, figsize=(8.6, 4.2 * nrows), dpi=160, sharex=True)
    if nrows == 1:
        axes = [axes]
    for idx, k_label in enumerate(panel_labels):
        ax = axes[idx]
        line_color = LINE_COLORS.get(k_label, "0.2")
        col = col_map.get(k_label)
        if col and col in df_ft.columns:
            y = df_ft[col].to_numpy()
            ax.plot(t, y, lw=1.8, color=line_color, zorder=6)
        else:
            _warn(f"Missing f(t) column for {k_label}; expected {col!r}.")

        ax.set_xlim(plot_min, plot_max)
        ax.set_ylim(bottom=0)
        ax.set_ylabel("f(t)")
        if idx == nrows - 1:
            ax.set_xlabel("t (time steps)")
        ax.text(
            0.01,
            0.92,
            k_label,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=9,
            color=line_color,
            bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", pad=0.6),
        )

        panel_intervals = _get_bin_intervals(data, k_label)
        _draw_window_bars(
            ax,
            k_label=k_label,
            proportions=proportions,
            class_colors=data["class_colors"],
            bin_intervals=panel_intervals,
            y0=band_y0,
            row_h=band_h,
            show_ci=show_ci,
            ci_entries=ci_entries,
        )
        _annotate_windows(
            ax,
            panel_intervals,
            x_span=plot_max - plot_min,
            x_limits=(plot_min, plot_max),
        )
        ax.label_outer()

    axes[0].legend(handles=class_handles, loc="upper right", fontsize=8, frameon=True)
    fig.suptitle("f(t) + windowed class composition bars", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def _write_meta(outpath: Path, input_json: Path, ft_csv: Path, args: argparse.Namespace, ci_csv: Optional[Path]) -> None:
    meta = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "output": str(outpath),
        "inputs": {
            "fig2_json": str(input_json),
            "ft_csv": str(ft_csv),
            "fig2_json_sha256": _sha256(input_json),
            "ft_csv_sha256": _sha256(ft_csv),
        },
        "params": {
            "col_t": args.col_t,
            "col_k2": args.col_k2,
            "col_k4": args.col_k4,
            "band_y0": args.band_y0,
            "band_h": args.band_h,
            "bar_k": args.bar_k,
            "layout": args.layout,
            "xlim": args.xlim,
            "show_ci": bool(args.show_ci),
        },
    }
    if ci_csv is not None and ci_csv.exists():
        meta["inputs"]["mc_uncertainty_csv"] = str(ci_csv)
        meta["inputs"]["mc_uncertainty_sha256"] = _sha256(ci_csv)
    meta_path = outpath.with_suffix(".meta.json")
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot fig2 with stacked class bars aligned to windows.")
    parser.add_argument("--input-json", required=True, type=Path)
    parser.add_argument("--ft-csv", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--col-t", dest="col_t", default="t")
    parser.add_argument("--col-k2", dest="col_k2", default="f_K2")
    parser.add_argument("--col-k4", dest="col_k4", default="f_K4")
    parser.add_argument("--band-y0", dest="band_y0", type=float, default=0.0)
    parser.add_argument("--band-h", dest="band_h", type=float, default=1.0)
    parser.add_argument(
        "--bar-k",
        dest="bar_k",
        default="both",
        help="Which K to use for bars (overlap) or which panels to keep (stacked): K=2, K=4, or both.",
    )
    parser.add_argument(
        "--layout",
        dest="layout",
        default="stacked",
        choices=["stacked", "overlap"],
        help="Panel layout: stacked (K=2/K=4 panels) or overlap (single axis).",
    )
    parser.add_argument(
        "--xlim",
        dest="xlim",
        nargs=2,
        type=float,
        default=None,
        metavar=("XMIN", "XMAX"),
        help="Override x-axis limits (e.g. --xlim 1 4000).",
    )
    parser.add_argument("--show-ci", dest="show_ci", action="store_true")
    parser.add_argument("--ci-csv", dest="ci_csv", type=Path, default=None)
    args = parser.parse_args()

    data = _load_json(args.input_json)
    _check_keys(data)
    df_ft = _load_ft_csv(args.ft_csv)

    ci_entries = None
    ci_path = args.ci_csv
    if args.show_ci:
        if ci_path is None:
            ci_path = args.input_json.parent.parent / "outputs" / "sensitivity" / "mc_uncertainty.csv"
        if not ci_path.exists():
            raise FileNotFoundError(f"--show-ci requested but mc_uncertainty.csv not found at {ci_path}")
        ci_entries = _load_uncertainty(ci_path)

    _plot(
        data,
        df_ft,
        args.out,
        col_t=args.col_t,
        col_k2=args.col_k2,
        col_k4=args.col_k4,
        band_y0=args.band_y0,
        band_h=args.band_h,
        bar_k=args.bar_k,
        layout=args.layout,
        xlim=tuple(args.xlim) if args.xlim is not None else None,
        show_ci=args.show_ci,
        ci_entries=ci_entries,
    )
    _write_meta(args.out, args.input_json, args.ft_csv, args, ci_path)


if __name__ == "__main__":
    main()
