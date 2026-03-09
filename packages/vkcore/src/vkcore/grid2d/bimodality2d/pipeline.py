#!/usr/bin/env python3
"""
2D biased/lazy random walk bimodality pipeline (v2/v3/v4).

Produces exact recursion, analytic AW inversion, MC overlays, and paper-style figures
for candidates A/B/C, plus scan results for minimal corridor length / minimal bias count.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_DIR = Path(os.environ.get("VK_REPORT_DIR", str(REPO_ROOT / "reports" / "grid2d_bimodality"))).resolve()
CODE_DIR = REPORT_DIR / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from configs_candidates import (
    corridor_set_from_spec,
    find_bimodality,
    scan_bias_sites,
    scan_corridor_lengths,
    sticky_set_from_spec,
)
from fpt_aw_inversion import fpt_pmf_aw, fpt_pmf_aw_with_grid
from fpt_exact_mc import (
    distributions_at_times,
    exact_fpt,
    hist_pmf,
    mc_candidate_A,
    mc_candidate_B,
    mc_candidate_C,
    sample_path_candidate_A,
    sample_path_candidate_B,
    sample_path_candidate_C,
)
from model_core import ConfigSpec, LatticeConfig, build_mc_arrays, config_to_dict, spec_to_internal
from plot_results import plot_candidate_panel, plot_fpt_overlay, plot_heatmaps, smooth_curve
from plot_schematics import (
    find_paths_candidate_A,
    find_paths_candidate_B,
    find_paths_candidate_C,
    plot_schematic,
)
import plot_style_fig3v2 as fig3v2
import plot_style_v8 as fig3v8
from plot_fig3_panel_v8 import plot_environment_v8, plot_fig3_panel_v8, plot_symbol_legend_v8
from plot_fpt_v8 import plot_bimodality_proof_B, plot_channel_decomp_v8, plot_fpt_multiscale_v8
from plot_paths_v8 import plot_paths_density_v8
import plot_style_v9 as fig3v9
from plot_fig3_panel_v9 import plot_environment_v9, plot_fig3_panel_v9, plot_symbol_legend_v9
from plot_fpt_v9 import (
    plot_bimodality_proof_B as plot_bimodality_proof_B_v9,
    plot_channel_decomp_v9,
    plot_fpt_multiscale_v9,
)
from plot_paths_v9 import plot_paths_density_v9
import plot_style_v10 as fig3v10
from plot_fig3_panel_v10 import (
    plot_candidate_B_env_v10,
    plot_environment_v10,
    plot_fig3_panel_v10,
    plot_symbol_legend_v10,
)
from plot_fpt_v10 import (
    plot_bimodality_proof_B_v10,
    plot_channel_decomp_v10,
    plot_fpt_multiscale_v10,
)
from plot_paths_v10 import plot_paths_density_v10
import plot_style_v11 as fig3v11
from plot_fig3_panel_v11 import (
    plot_candidate_B_env_v11,
    plot_environment_v11,
    plot_fig3_panel_v11,
    plot_symbol_legend_v11,
)
from plot_fpt_v11 import (
    plot_bimodality_diagnostic_B_v11,
    plot_bimodality_proof_B_v11,
    plot_channel_decomp_v11,
    plot_fpt_multiscale_v11,
)
from plot_paths_v11 import plot_paths_density_v11
import plot_style_v12 as fig3v12
from plot_fig3_panel_v12 import (
    plot_candidate_B_env_v12,
    plot_environment_v12,
    plot_fig3_panel_v12,
    plot_symbol_legend_v12,
)
from plot_fpt_v12 import (
    plot_bimodality_diagnostic_v12,
    plot_bimodality_proof_B,
    plot_channel_decomp_v12,
    plot_fpt_multiscale_v12,
)
from plot_paths_v12 import plot_paths_density_v12
from plot_v3 import plot_environment_figure, plot_fpt_figure, plot_heatmap_figure, plot_panel as plot_panel_v3
from viz.case_data import CaseGeometry, case_to_spec, load_cases_v3, scale_case_geometry
from viz.draw_env import save_environment_figure, save_path_figure, save_symbol_legend
from viz.layout_panels import plot_panel as plot_panel_v4
from viz.plot_fpt import plot_channel_mix, plot_fpt
from viz.plot_heatmaps import plot_heatmap_triplet
from viz.fig3_style import (
    ViewBox,
    plot_channel_decomp,
    plot_environment,
    plot_fpt_big,
    plot_paths_figure,
    plot_periodic_unwrapped,
    plot_prob_snapshots,
    plot_scan as plot_scan_v5,
    plot_symbol_legend,
)
FIG_DIR = REPORT_DIR / "figures"
DATA_DIR = REPORT_DIR / "data"
OUTPUTS_DIR = REPORT_DIR / "outputs"


def ensure_dirs(fig_dir: Path) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ensure_v6_dirs(fig_root: Path) -> Dict[str, Path]:
    fig_root.mkdir(parents=True, exist_ok=True)
    subdirs = {
        "env": fig_root / "env",
        "fig3_panels": fig_root / "fig3_panels",
        "paths": fig_root / "paths",
        "heatmaps": fig_root / "heatmaps",
        "fpt": fig_root / "fpt",
        "channel_decomp": fig_root / "channel_decomp",
        "unwrapped": fig_root / "unwrapped",
    }
    for path in subdirs.values():
        path.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return subdirs


def plot_scan(results: List[dict], x_key: str, outpath: Path, title: str) -> None:
    xs = [row[x_key] for row in results]
    h2_over_h1 = [row.get("h2_over_h1", np.nan) for row in results]
    hv_over_max = [row.get("hv_over_max", np.nan) for row in results]
    bimodal = [row.get("paper_bimodal", False) for row in results]

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ax = axes[0]
    ax.plot(xs, h2_over_h1, "o-", color="tab:blue")
    ax.axhline(0.01, color="0.5", ls="--", lw=1.0)
    ax.set_xlabel(x_key)
    ax.set_ylabel("h2/h1")
    for x, flag in zip(xs, bimodal):
        if flag:
            ax.scatter([x], [0.01], color="tab:green", s=20)

    ax = axes[1]
    ax.plot(xs, hv_over_max, "o-", color="tab:purple")
    ax.set_xlabel(x_key)
    ax.set_ylabel("hv/max(h1,h2)")

    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    fig.savefig(outpath.with_suffix(".png"), dpi=300)
    plt.close(fig)


def _aw_errors(f_aw: np.ndarray, f_exact: np.ndarray) -> Dict[str, float]:
    diff = np.abs(f_aw - f_exact)
    l1 = float(np.sum(diff))
    linf = float(np.max(diff)) if diff.size else 0.0
    base = float(np.sum(np.abs(f_exact))) if f_exact.size else 1.0
    rel = float(l1 / base) if base > 0 else 0.0
    return {"l1": l1, "linf": linf, "rel_l1": rel}


def _select_heatmap_times(peaks: dict, t_max: int) -> List[int]:
    times: List[int] = []
    for key in ("t1", "tv", "t2"):
        val = peaks.get(key)
        if val is not None and 1 <= int(val) <= t_max:
            times.append(int(val))
    if not times:
        times = [max(1, min(t_max, 10)), max(1, min(t_max, 30))]
    if len(times) == 1:
        times.append(min(t_max, times[0] + 10))
    return times


def _moving_average(y: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or y.size < window:
        return y.copy()
    kernel = np.ones(window, dtype=np.float64) / float(window)
    return np.convolve(y, kernel, mode="same")


def _select_peak_times_v3(
    f_exact: np.ndarray,
    *,
    t_max: int,
    smooth_window: int,
    min_height: float = 1e-7,
    min_sep: int = 5,
    min_gap: int = 20,
) -> Tuple[int, int, int]:
    y = _moving_average(f_exact[:t_max], smooth_window)
    y_raw = f_exact[:t_max]

    peaks: List[int] = []
    try:
        from scipy.signal import find_peaks

        idx_s, _ = find_peaks(y, height=min_height, distance=min_sep)
        idx_r, _ = find_peaks(y_raw, height=min_height, distance=min_sep)
        peaks = list(set(idx_s) | set(idx_r))
    except Exception:
        for i in range(1, len(y_raw) - 1):
            if y_raw[i] > y_raw[i - 1] and y_raw[i] > y_raw[i + 1] and y_raw[i] >= min_height:
                peaks.append(i)
        for i in range(1, len(y) - 1):
            if y[i] > y[i - 1] and y[i] > y[i + 1] and y[i] >= min_height:
                peaks.append(i)

    if not peaks:
        t1 = max(1, min(t_max, 2))
        t2 = max(2, min(t_max, 4))
        tv = max(1, min(t_max, 3))
        return t1, tv, t2

    peaks = [p for p in peaks if y_raw[p] >= min_height]
    peaks.sort()
    t1_idx = peaks[0]
    later = [p for p in peaks if p - t1_idx >= min_gap]
    if later:
        t2_idx = max(later, key=lambda i: y[i])
    elif len(peaks) > 1:
        t2_idx = peaks[1]
    else:
        t2_idx = t1_idx

    t1 = int(t1_idx + 1)
    t2 = int(t2_idx + 1)
    if t2 <= t1:
        t2 = min(t_max, t1 + min_gap)

    seg = f_exact[t1 - 1 : t2 - 1] if t2 > t1 + 1 else f_exact[t1 - 1 : t1]
    if seg.size == 0:
        tv = t1
    else:
        idx_min = int(seg.argmin())
        tv = t1 + idx_min
    return t1, tv, t2


def _median_time(times: np.ndarray, labels: np.ndarray, label: int) -> int | None:
    subset = times[labels == label]
    if subset.size == 0:
        return None
    return int(np.median(subset))


def _pick_representative_path(
    sample_func,
    *,
    label: int,
    target_time: int,
    rng: np.random.Generator,
    max_attempts: int,
) -> tuple[np.ndarray, int] | None:
    if target_time <= 0:
        return None
    tol = max(3, int(0.05 * target_time))
    best = None
    best_diff = None
    for _ in range(max_attempts):
        path, time, lab = sample_func(rng)
        if lab != label:
            continue
        diff = abs(int(time) - target_time)
        if best is None or diff < best_diff:
            best = (path, int(time))
            best_diff = diff
        if diff <= tol:
            break
    return best


def _to_one_based(path: np.ndarray) -> np.ndarray:
    if path.size == 0:
        return path
    return path.astype(np.int64) + 1


def _collect_paths(
    sample_func,
    *,
    label: int,
    n_paths: int,
    rng: np.random.Generator,
    max_attempts: int,
) -> List[np.ndarray]:
    paths: List[np.ndarray] = []
    attempts = 0
    while len(paths) < n_paths and attempts < max_attempts:
        path, _, lab = sample_func(rng)
        attempts += 1
        if lab != label:
            continue
        paths.append(_to_one_based(path))
    return paths


def _corridor_band(
    case: CaseGeometry, *, halfwidth: int = 1, x_span: tuple[int, int] | None = None
) -> set[tuple[int, int]]:
    if not case.corridor:
        return set()
    y0 = int(case.corridor["y"])
    if x_span is None:
        x0 = int(case.corridor["x_start"])
        x1 = int(case.corridor["x_end"])
    else:
        x0, x1 = x_span
    band: set[tuple[int, int]] = set()
    for x in range(x0, x1 + 1):
        for dy in range(-halfwidth, halfwidth + 1):
            y = y0 + dy
            if 1 <= y <= case.N:
                band.add((x, y))
    return band


def _corridor_band_rows_from_case(case: CaseGeometry, *, default_halfwidth: int = 1) -> List[int]:
    if not case.corridor:
        return []
    rule = case.classification_rule or {}
    rows = rule.get("corridor_band_rows") or rule.get("band_rows")
    if rows:
        rows_list = [int(y) for y in rows]
    else:
        halfwidth = int(rule.get("band_halfwidth", default_halfwidth))
        y0 = int(case.corridor["y"])
        rows_list = list(range(y0 - halfwidth, y0 + halfwidth + 1))
    rows_list = [y for y in rows_list if 1 <= y <= case.N]
    if not rows_list:
        return []
    return rows_list


def _corridor_band_from_rows(
    case: CaseGeometry, *, rows: Sequence[int], x_span: tuple[int, int] | None = None
) -> set[tuple[int, int]]:
    if not case.corridor or not rows:
        return set()
    if x_span is None:
        x0 = int(case.corridor["x_start"])
        x1 = int(case.corridor["x_end"])
    else:
        x0, x1 = x_span
    band: set[tuple[int, int]] = set()
    for x in range(x0, x1 + 1):
        for y in rows:
            if 1 <= y <= case.N:
                band.add((x, int(y)))
    return band


def _mc_histogram(
    times: np.ndarray,
    *,
    t_max: int,
    bin_width: int,
    smooth_window: int,
    tail_start: int | None = None,
    tail_bin_width: int | None = None,
    tail_smooth_window: int | None = None,
    censor: bool = True,
    n_total: int | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    if times.size == 0:
        centers = np.arange(1, t_max + 1, max(1, bin_width))
        return centers, np.zeros_like(centers, dtype=np.float64)
    valid = times < t_max if censor else times <= t_max
    times_use = times[valid]
    use_tail = (
        tail_start is not None
        and tail_bin_width is not None
        and tail_bin_width > bin_width
        and 1 < tail_start < t_max
    )
    if use_tail:
        early_end = min(t_max, int(tail_start))
        edges_early = np.arange(1, early_end + bin_width, bin_width)
        if edges_early.size == 0:
            edges_early = np.array([1], dtype=np.int64)
        tail_edge = int(edges_early[-1])
        edges_tail = np.arange(tail_edge, t_max + tail_bin_width + 1, tail_bin_width)
        edges = np.concatenate([edges_early, edges_tail[1:]]) if edges_tail.size > 1 else edges_early
    else:
        edges = np.arange(1, t_max + bin_width + 1, bin_width)
    counts, _ = np.histogram(times_use, bins=edges)
    total = float(n_total) if n_total is not None else float(times.size)
    if total <= 0:
        centers = (edges[:-1] + edges[1:] - 1) / 2.0
        return centers, np.zeros_like(centers, dtype=np.float64)
    widths = np.diff(edges).astype(np.float64)
    pmf = counts / total / widths
    centers = edges[:-1] + (widths - 1.0) / 2.0
    if smooth_window > 1:
        pmf_base = _moving_average(pmf, smooth_window)
    else:
        pmf_base = pmf.copy()
    pmf_out = pmf_base
    if tail_smooth_window is None:
        tail_smooth_window = smooth_window
    if use_tail and tail_smooth_window > smooth_window:
        pmf_tail = _moving_average(pmf, tail_smooth_window)
        tail_mask = centers >= float(tail_start)
        if np.any(tail_mask):
            pmf_out = pmf_base.copy()
            pmf_out[tail_mask] = pmf_tail[tail_mask]
    return centers, pmf_out


def _build_corridor_case(
    base: CaseGeometry,
    *,
    gx: float,
    gy: float,
    delta: float,
    start_x: int,
    length: int,
    boundary_x: str | None = None,
    boundary_y: str | None = None,
) -> CaseGeometry:
    y = int(base.start[1])
    x_end = int(start_x)
    x_start = int(start_x - length + 1)
    target_x = int(start_x - length)
    if x_start < 1 or target_x < 1:
        raise ValueError("Corridor range out of bounds.")
    corridor = dict(base.corridor) if base.corridor else {}
    corridor.update(
        {
            "x_start": x_start,
            "x_end": x_end,
            "y": y,
            "direction": "left",
            "delta": float(delta),
        }
    )
    local_bias = [{"x": x, "y": y, "dir": "left"} for x in range(x_start, x_end + 1)]
    return replace(
        base,
        g_x=float(gx),
        g_y=float(gy),
        start=(x_end, y),
        target=(target_x, y),
        local_bias=local_bias,
        local_bias_delta=float(delta),
        corridor=corridor,
        boundary_x=boundary_x if boundary_x is not None else base.boundary_x,
        boundary_y=boundary_y if boundary_y is not None else base.boundary_y,
    )


def _evaluate_bimodality_metrics(
    f_exact: np.ndarray,
    *,
    smooth_w: int,
    min_sep: int,
    min_gap: int,
) -> dict:
    detect = fig3v9.detect_bimodality(f_exact, smooth_w=smooth_w, min_sep=min_sep)
    p1, p2, v = int(detect["p1"]), int(detect["p2"]), int(detect["v"])
    h1 = float(detect["h1"])
    h2 = float(detect["h2"])
    hv = float(detect["hv"])
    gap = int(p2 - p1)
    if gap < min_gap:
        raise RuntimeError("Peak separation too small.")
    peak_ratio = min(h1, h2) / max(h1, h2) if max(h1, h2) > 0 else 0.0
    valley_rel = hv / max(h1, h2) if max(h1, h2) > 0 else 1.0
    return {
        "detect": detect,
        "t_p1": p1,
        "t_p2": p2,
        "t_v": v,
        "h1": h1,
        "h2": h2,
        "hv": hv,
        "peak_ratio": peak_ratio,
        "valley_rel": valley_rel,
        "gap": gap,
    }


def _tune_candidate_B_v2(
    base: CaseGeometry,
    *,
    t_max: int,
    t_max_mc: int,
    n_mc: int,
    seed: int,
    smooth_w: int,
    min_sep: int,
    min_gap: int,
) -> Tuple[CaseGeometry, dict]:
    delta_grid = [0.70, 0.75, 0.80, 0.85]
    gx_grid = [-0.20, -0.15, -0.10, -0.05, 0.00]
    gy_grid = [0.20, 0.35, 0.50]
    length = int(base.corridor["x_end"]) - int(base.corridor["x_start"]) + 1 if base.corridor else 10
    start_x = int(base.start[0])

    band_hw = 1
    if base.classification_rule and "band_halfwidth" in base.classification_rule:
        band_hw = int(base.classification_rule["band_halfwidth"])

    results: List[dict] = []
    best: dict | None = None

    def eval_combo(
        gx: float,
        gy: float,
        delta: float,
        length_local: int,
        *,
        boundary_x: str,
    ) -> dict | None:
        try:
            case = _build_corridor_case(
                base,
                gx=gx,
                gy=gy,
                delta=delta,
                start_x=start_x,
                length=length_local,
                boundary_x=boundary_x,
            )
        except ValueError:
            return None
        spec = case_to_spec(case)
        cfg = spec_to_internal(spec)
        f_exact, mass = exact_fpt(cfg, t_max=t_max)
        try:
            metrics = _evaluate_bimodality_metrics(
                f_exact, smooth_w=smooth_w, min_sep=min_sep, min_gap=min_gap
            )
        except RuntimeError:
            return None
        corridor_set = corridor_set_from_spec(spec)
        corridor_band_1 = _corridor_band(
            case,
            halfwidth=band_hw,
            x_span=(min(case.start[0], case.target[0]), max(case.start[0], case.target[0])),
        )
        corridor_band = {(x - 1, y - 1) for x, y in corridor_band_1}
        times, labels, stats = mc_candidate_B(
            cfg,
            corridor_set,
            n_walkers=n_mc,
            seed=seed,
            max_steps=t_max_mc,
            corridor_band=corridor_band,
        )
        p_fast = float((labels == 0).mean()) if labels.size else 0.0
        score = metrics["peak_ratio"] - metrics["valley_rel"]
        ok = (
            metrics["peak_ratio"] >= 0.15
            and metrics["valley_rel"] <= 0.25
            and 0.05 <= p_fast <= 0.40
        )
        return {
            "gx": gx,
            "gy": gy,
            "delta": delta,
            "length": length_local,
            "start": case.start,
            "target": case.target,
            "boundary_x": boundary_x,
            "mass": mass,
            "p_fast": p_fast,
            "ok": ok,
            "score": score,
            **metrics,
        }

    for delta in delta_grid:
        for gx in gx_grid:
            for gy in gy_grid:
                res = eval_combo(gx, gy, delta, length, boundary_x=base.boundary_x)
                if res is None:
                    continue
                results.append(res)
                if res["ok"] and (best is None or res["score"] > best["score"]):
                    best = res

    if best is None:
        delta_grid = [0.70, 0.75, 0.80, 0.85, 0.90]
        for delta in delta_grid:
            for gx in gx_grid:
                for gy in gy_grid:
                    res = eval_combo(gx, gy, delta, length, boundary_x=base.boundary_x)
                    if res is None:
                        continue
                    results.append(res)
                    if res["ok"] and (best is None or res["score"] > best["score"]):
                        best = res

    if best is None:
        for delta in delta_grid:
            for gx in gx_grid:
                for gy in gy_grid:
                    res = eval_combo(gx, gy, delta, length, boundary_x="periodic")
                    if res is None:
                        continue
                    results.append(res)
                    if res["ok"] and (best is None or res["score"] > best["score"]):
                        best = res

    if best is None and results:
        best = max(results, key=lambda r: r["score"])
        for length_local in range(10, 15):
            res = eval_combo(
                best["gx"],
                best["gy"],
                best["delta"],
                length_local,
                boundary_x=best.get("boundary_x", base.boundary_x),
            )
            if res is None:
                continue
            results.append(res)
            if res["ok"] and (best is None or res["score"] > best["score"]):
                best = res

    if best is None:
        raise RuntimeError("B_v2 tuning failed to produce any candidate.")

    tuned_case = _build_corridor_case(
        base,
        gx=best["gx"],
        gy=best["gy"],
        delta=best["delta"],
        start_x=int(best["start"][0]),
        length=int(best["length"]),
        boundary_x=str(best.get("boundary_x", base.boundary_x)),
    )
    return tuned_case, {"best": best, "grid": results}


def _tune_candidate_B_v10(
    base: CaseGeometry,
    *,
    t_max: int,
    t_max_mc: int,
    n_mc: int,
    seed: int,
    smooth_w: int,
    min_sep: int,
    min_gap: int,
) -> Tuple[CaseGeometry, dict]:
    gx_grid = [-0.35, -0.25, -0.20, -0.15, -0.10]
    gy_grid = [0.30, 0.50, 0.70]
    delta_grid = [0.60, 0.70, 0.80, 0.90]
    length_grid = list(range(8, 15))
    band_hw_grid = [1, 2]

    start_x = int(base.start[0])

    results: List[dict] = []
    best: dict | None = None

    def eval_combo(
        gx: float,
        gy: float,
        delta: float,
        length_local: int,
        band_hw: int,
    ) -> dict | None:
        try:
            case = _build_corridor_case(
                base,
                gx=gx,
                gy=gy,
                delta=delta,
                start_x=start_x,
                length=length_local,
                boundary_x=base.boundary_x,
            )
        except ValueError:
            return None
        rule = dict(case.classification_rule) if case.classification_rule else {}
        rule["band_halfwidth"] = int(band_hw)
        case = replace(case, classification_rule=rule)

        spec = case_to_spec(case)
        cfg = spec_to_internal(spec)
        f_exact, mass = exact_fpt(cfg, t_max=t_max)
        try:
            metrics = fig3v10.compute_bimodality_metrics(
                f_exact[:t_max],
                smooth_w=smooth_w,
                min_sep=min_sep,
                min_gap=min_gap,
            )
        except RuntimeError:
            return None

        peak_ratio = float(metrics["peak_ratio"])
        valley_ratio = float(metrics["valley_ratio"])
        gap = int(metrics["gap"])
        if not (0.35 <= peak_ratio <= 0.85 and valley_ratio <= 0.35 and gap >= min_gap):
            return None

        corridor_set = corridor_set_from_spec(spec)
        corridor_band_1 = _corridor_band(
            case,
            halfwidth=band_hw,
            x_span=(min(case.start[0], case.target[0]), max(case.start[0], case.target[0])),
        )
        corridor_band = {(x - 1, y - 1) for x, y in corridor_band_1}
        times, labels, stats = mc_candidate_B(
            cfg,
            corridor_set,
            n_walkers=n_mc,
            seed=seed,
            max_steps=t_max_mc,
            corridor_band=corridor_band,
        )
        p_fast = float((labels == 0).mean()) if labels.size else 0.0
        ok = 0.03 <= p_fast <= 0.30
        score = peak_ratio - valley_ratio
        return {
            "gx": gx,
            "gy": gy,
            "delta": delta,
            "length": length_local,
            "band_halfwidth": band_hw,
            "start": case.start,
            "target": case.target,
            "mass": mass,
            "p_fast": p_fast,
            "ok": ok,
            "score": score,
            **metrics,
        }

    for band_hw in band_hw_grid:
        for length_local in length_grid:
            for delta in delta_grid:
                for gx in gx_grid:
                    for gy in gy_grid:
                        res = eval_combo(gx, gy, delta, length_local, band_hw)
                        if res is None:
                            continue
                        results.append(res)
                        if res["ok"] and (best is None or res["score"] > best["score"]):
                            best = res

    if best is None and results:
        best = max(results, key=lambda r: r["score"])

    if best is None:
        raise RuntimeError("B_v10 tuning failed to produce any candidate.")

    tuned_case = _build_corridor_case(
        base,
        gx=best["gx"],
        gy=best["gy"],
        delta=best["delta"],
        start_x=int(best["start"][0]),
        length=int(best["length"]),
        boundary_x=base.boundary_x,
    )
    rule = dict(tuned_case.classification_rule) if tuned_case.classification_rule else {}
    rule["band_halfwidth"] = int(best.get("band_halfwidth", 1))
    tuned_case = replace(tuned_case, classification_rule=rule)
    return tuned_case, {"best": best, "grid": results}


def _tune_candidate_B_v11(
    base: CaseGeometry,
    *,
    t_max: int,
    t_max_mc: int,
    n_mc: int,
    seed: int,
    smooth_w: int,
    min_sep: int,
    min_gap: int,
    bin_width: int,
) -> Tuple[CaseGeometry, dict]:
    gx_grid = [-0.35, -0.30, -0.25, -0.20, -0.15, -0.10]
    gy_grid = [0.30, 0.40, 0.50, 0.60, 0.70]
    delta_grid = [0.60, 0.70, 0.80, 0.90]
    length_grid = list(range(8, 15))
    band_hw_grid = [1, 2]

    start_x = int(base.start[0])
    sep_min = max(min_gap, 8 * bin_width)

    results: List[dict] = []
    best: dict | None = None

    def eval_combo(
        gx: float,
        gy: float,
        delta: float,
        length_local: int,
        band_hw: int,
    ) -> dict | None:
        try:
            case = _build_corridor_case(
                base,
                gx=gx,
                gy=gy,
                delta=delta,
                start_x=start_x,
                length=length_local,
                boundary_x=base.boundary_x,
            )
        except ValueError:
            return None
        rule = dict(case.classification_rule) if case.classification_rule else {}
        rule["band_halfwidth"] = int(band_hw)
        y0 = int(case.corridor["y"])
        rule["corridor_band_rows"] = [
            y for y in range(y0 - band_hw, y0 + band_hw + 1) if 1 <= y <= case.N
        ]
        if rule.get("corridor_band_rows"):
            rows_str = ",".join(str(y) for y in rule["corridor_band_rows"])
            rule["fast"] = f"stay in corridor band (y in {{{rows_str}}}) until hit target"
            rule["slow"] = "leave corridor band before hit"
        case = replace(case, classification_rule=rule)

        spec = case_to_spec(case)
        cfg = spec_to_internal(spec)
        f_exact, mass = exact_fpt(cfg, t_max=t_max)
        try:
            metrics = fig3v11.compute_bimodality_metrics(
                f_exact[:t_max],
                smooth_w=smooth_w,
                min_sep=min_sep,
                min_gap=sep_min,
            )
        except RuntimeError:
            return None

        valley_ratio = float(metrics["valley_ratio"])
        if valley_ratio > 0.10:
            return None

        corridor_set = corridor_set_from_spec(spec)
        corridor_rows = _corridor_band_rows_from_case(case, default_halfwidth=band_hw)
        corridor_band_1 = _corridor_band_from_rows(
            case,
            rows=corridor_rows,
            x_span=(min(case.start[0], case.target[0]), max(case.start[0], case.target[0])),
        )
        corridor_band = {(x - 1, y - 1) for x, y in corridor_band_1}
        times, labels, stats = mc_candidate_B(
            cfg,
            corridor_set,
            n_walkers=n_mc,
            seed=seed,
            max_steps=t_max_mc,
            corridor_band=corridor_band,
        )
        p_fast = float((labels == 0).mean()) if labels.size else 0.0
        if not (0.03 <= p_fast <= 0.30):
            return None

        peak_ratio = float(metrics["peak_ratio"])
        score = (1.0 - valley_ratio) + 0.6 * peak_ratio - 0.03 * float(length_local)
        return {
            "gx": gx,
            "gy": gy,
            "delta": delta,
            "length": length_local,
            "band_halfwidth": band_hw,
            "start": case.start,
            "target": case.target,
            "mass": mass,
            "p_fast": p_fast,
            "score": score,
            **metrics,
        }

    for band_hw in band_hw_grid:
        for length_local in length_grid:
            for delta in delta_grid:
                for gx in gx_grid:
                    for gy in gy_grid:
                        res = eval_combo(gx, gy, delta, length_local, band_hw)
                        if res is None:
                            continue
                        results.append(res)
                        if best is None or res["score"] > best["score"]:
                            best = res

    if best is None:
        raise RuntimeError("B_v11 tuning failed to meet thresholds.")

    tuned_case = _build_corridor_case(
        base,
        gx=best["gx"],
        gy=best["gy"],
        delta=best["delta"],
        start_x=int(best["start"][0]),
        length=int(best["length"]),
        boundary_x=base.boundary_x,
    )
    rule = dict(tuned_case.classification_rule) if tuned_case.classification_rule else {}
    rule["band_halfwidth"] = int(best.get("band_halfwidth", 1))
    y0 = int(tuned_case.corridor["y"])
    rule["corridor_band_rows"] = [
        y for y in range(y0 - rule["band_halfwidth"], y0 + rule["band_halfwidth"] + 1) if 1 <= y <= tuned_case.N
    ]
    if rule.get("corridor_band_rows"):
        rows_str = ",".join(str(y) for y in rule["corridor_band_rows"])
        rule["fast"] = f"stay in corridor band (y in {{{rows_str}}}) until hit target"
        rule["slow"] = "leave corridor band before hit"
    tuned_case = replace(tuned_case, classification_rule=rule)
    return tuned_case, {"best": best, "grid": results}


def _event_point_wrap(path: np.ndarray, *, N: int) -> Tuple[int, int] | None:
    if path.size == 0:
        return None
    for idx in range(len(path) - 1):
        x0, y0 = path[idx]
        x1, y1 = path[idx + 1]
        if (x0 == 1 and x1 == N) or (x0 == N and x1 == 1):
            return int(x1), int(y1)
    return None


def _event_point_corridor_exit(path: np.ndarray, corridor_band: set[tuple[int, int]]) -> Tuple[int, int] | None:
    if path.size == 0 or not corridor_band:
        return None
    for idx in range(1, len(path)):
        x1, y1 = path[idx]
        if (int(x1), int(y1)) not in corridor_band:
            return int(x1), int(y1)
    return None


def _event_point_door(path: np.ndarray, door_edge: tuple[tuple[int, int], tuple[int, int]]) -> Tuple[int, int] | None:
    if path.size == 0:
        return None
    (x0, y0), (x1, y1) = door_edge
    for idx in range(len(path) - 1):
        a = (int(path[idx][0]), int(path[idx][1]))
        b = (int(path[idx + 1][0]), int(path[idx + 1][1]))
        if (a == (x0, y0) and b == (x1, y1)) or (a == (x1, y1) and b == (x0, y0)):
            return int(b[0]), int(b[1])
    return None


def run_pipeline(
    *,
    cases_json: str | None,
    quick: bool,
    t_max: int,
    t_max_scan: int,
    t_max_aw: int,
    mc_samples: int,
    seed: int,
    aw_oversample: int,
    aw_r_pow10: float,
    fpt_method: str,
    fig_version: str,
    plot_style: str,
    png_dpi: int,
    mc_bin_width: int,
    mc_smooth_window: int,
    peak_smooth_window: int,
    log_eps: float,
    tune_B: bool,
) -> dict:
    fig_subdirs: Dict[str, Path] | None = None
    outputs_dir: Path | None = None
    if fig_version == "v2":
        fig_dir = FIG_DIR
        ensure_dirs(fig_dir)
    elif fig_version == "v5":
        fig_dir = REPORT_DIR / "figures_v5"
        ensure_dirs(fig_dir)
    elif fig_version == "v6":
        fig_dir = REPORT_DIR / "figures_v6"
        fig_subdirs = ensure_v6_dirs(fig_dir)
    elif fig_version == "v7":
        fig_dir = REPORT_DIR / "figures_v7"
        fig_subdirs = ensure_v6_dirs(fig_dir)
    elif fig_version == "v8":
        fig_dir = REPORT_DIR / "figures_v8"
        fig_subdirs = ensure_v6_dirs(fig_dir)
    elif fig_version == "v9":
        fig_dir = REPORT_DIR / "figures" / "v9"
        fig_subdirs = ensure_v6_dirs(fig_dir)
        outputs_dir = OUTPUTS_DIR / "v9"
        outputs_dir.mkdir(parents=True, exist_ok=True)
    elif fig_version == "v10":
        fig_dir = REPORT_DIR / "figures" / "v10"
        fig_subdirs = ensure_v6_dirs(fig_dir)
        outputs_dir = OUTPUTS_DIR / "v10"
        outputs_dir.mkdir(parents=True, exist_ok=True)
    elif fig_version == "v11":
        fig_dir = REPORT_DIR / "figures" / "v11"
        fig_subdirs = ensure_v6_dirs(fig_dir)
        outputs_dir = OUTPUTS_DIR / "v11"
        outputs_dir.mkdir(parents=True, exist_ok=True)
    elif fig_version == "main":
        fig_dir = REPORT_DIR / "figures"
        fig_subdirs = ensure_v6_dirs(fig_dir)
        outputs_dir = OUTPUTS_DIR
        outputs_dir.mkdir(parents=True, exist_ok=True)
    elif fig_version == "v12":
        fig_dir = REPORT_DIR / "figures" / "v12"
        fig_subdirs = ensure_v6_dirs(fig_dir)
        outputs_dir = OUTPUTS_DIR / "v12"
        outputs_dir.mkdir(parents=True, exist_ok=True)
    else:
        fig_dir = FIG_DIR / fig_version
        ensure_dirs(fig_dir)

    N = 40 if quick else 60

    scan_B, L_min = scan_corridor_lengths(
        exact_solver=exact_fpt, t_max=t_max_scan, N=N, quick=quick, seed=seed
    )
    scan_C, n_min = scan_bias_sites(
        exact_solver=exact_fpt, t_max=t_max_scan, N=N, quick=quick, seed=seed
    )

    (DATA_DIR / "scan_candidate_B_corridor.json").write_text(json.dumps(scan_B, indent=2), encoding="utf-8")
    (DATA_DIR / "scan_candidate_C_bias.json").write_text(json.dumps(scan_C, indent=2), encoding="utf-8")

    if fig_version == "v5":
        xs = [row["L"] for row in scan_B]
        h2 = [row.get("h2_over_h1", np.nan) for row in scan_B]
        hv = [row.get("hv_over_max", np.nan) for row in scan_B]
        plot_scan_v5(
            xs=xs,
            h2_over_h1=h2,
            hv_over_max=hv,
            xmin_label=int(L_min) if L_min > 0 else -1,
            outpath=str(fig_dir / "candidate_B_scan.pdf"),
            xlabel="L",
            title="Candidate B scan",
            dpi=png_dpi,
        )
        xs = [row["n_bias"] for row in scan_C]
        h2 = [row.get("h2_over_h1", np.nan) for row in scan_C]
        hv = [row.get("hv_over_max", np.nan) for row in scan_C]
        plot_scan_v5(
            xs=xs,
            h2_over_h1=h2,
            hv_over_max=hv,
            xmin_label=int(n_min) if n_min >= 0 else -1,
            outpath=str(fig_dir / "candidate_C_scan.pdf"),
            xlabel="n_bias",
            title="Candidate C scan",
            dpi=png_dpi,
        )
    elif fig_version in ("main", "v6", "v7", "v8", "v9", "v10", "v11", "v12"):
        fig3v2.plot_scan(
            xs=[row["L"] for row in scan_B],
            h2_over_h1=[row.get("h2_over_h1", np.nan) for row in scan_B],
            hv_over_max=[row.get("hv_over_max", np.nan) for row in scan_B],
            xmin_label=int(L_min) if L_min > 0 else -1,
            outpath=fig_subdirs["channel_decomp"] / "candidate_B_scan.pdf",
            xlabel="L",
            title="Candidate B scan",
            dpi=png_dpi,
        )
        fig3v2.plot_scan(
            xs=[row["n_bias"] for row in scan_C],
            h2_over_h1=[row.get("h2_over_h1", np.nan) for row in scan_C],
            hv_over_max=[row.get("hv_over_max", np.nan) for row in scan_C],
            xmin_label=int(n_min) if n_min >= 0 else -1,
            outpath=fig_subdirs["channel_decomp"] / "candidate_C_scan.pdf",
            xlabel="n_bias",
            title="Candidate C scan",
            dpi=png_dpi,
        )
    else:
        plot_scan(scan_B, "L", fig_dir / "candidate_B_scan.pdf", "Candidate B scan")
        plot_scan(scan_C, "n_bias", fig_dir / "candidate_C_scan.pdf", "Candidate C scan")

    cases_path = Path(cases_json) if cases_json else (REPORT_DIR / "config" / "cases_v3.json")
    cases_v3 = load_cases_v3(cases_path)
    case_A = cases_v3["A"]
    case_B = cases_v3["B"]
    case_C = cases_v3["C"]
    case_B_v2 = cases_v3.get("B_v2")
    case_B_v10 = cases_v3.get("B_v10")
    case_B_v11 = cases_v3.get("B_v11")
    if quick:
        case_A = scale_case_geometry(case_A, N)
        case_B = scale_case_geometry(case_B, N)
        case_C = scale_case_geometry(case_C, N)
        if case_B_v2 is not None:
            case_B_v2 = scale_case_geometry(case_B_v2, N)
        if case_B_v10 is not None:
            case_B_v10 = scale_case_geometry(case_B_v10, N)
        if case_B_v11 is not None:
            case_B_v11 = scale_case_geometry(case_B_v11, N)

    case_B_main = case_B
    prefix_B = "candidate_B"
    case_B_id = "B"
    tune_report: dict | None = None
    if fig_version == "v9" and case_B_v2 is not None:
        case_B_main = case_B_v2
        prefix_B = "candidate_B_v2"
        if tune_B:
            tuned_case, tune_report = _tune_candidate_B_v2(
                case_B_v2,
                t_max=min(t_max_aw, 600),
                t_max_mc=min(t_max, 600),
                n_mc=min(mc_samples, 6000),
                seed=seed + 99,
                smooth_w=5,
                min_sep=5,
                min_gap=10,
            )
            case_B_main = tuned_case
            if outputs_dir is not None:
                (outputs_dir / "tune_B_v2.json").write_text(
                    json.dumps(tune_report, indent=2), encoding="utf-8"
                )
    if fig_version == "v10" and case_B_v10 is not None:
        case_B_main = case_B_v10
        prefix_B = "candidate_B_v10"
        if tune_B:
            tuned_case, tune_report = _tune_candidate_B_v10(
                case_B_v10,
                t_max=min(t_max_aw, 800),
                t_max_mc=min(t_max, 800),
                n_mc=min(mc_samples, 8000),
                seed=seed + 199,
                smooth_w=7,
                min_sep=5,
                min_gap=150,
            )
            case_B_main = tuned_case
            if outputs_dir is not None:
                (outputs_dir / "tune_B_v10.json").write_text(
                    json.dumps(tune_report, indent=2), encoding="utf-8"
                )
    if fig_version == "v11" and case_B_v11 is not None:
        case_B_main = case_B_v11
        prefix_B = "candidate_B_v11"
        if tune_B:
            tuned_case, tune_report = _tune_candidate_B_v11(
                case_B_v11,
                t_max=min(t_max_aw, 1000),
                t_max_mc=min(t_max, 1000),
                n_mc=min(mc_samples, 10000),
                seed=seed + 299,
                smooth_w=peak_smooth_window,
                min_sep=5,
                min_gap=20,
                bin_width=mc_bin_width,
            )
            case_B_main = tuned_case
            if outputs_dir is not None:
                (outputs_dir / "tune_B_v11.json").write_text(
                    json.dumps(tune_report, indent=2), encoding="utf-8"
                )
    if fig_version in ("v12", "main"):
        case_B_main = case_B
        prefix_B = "candidate_B"
        case_B_id = "B"
        if tune_B:
            tuned_case, tune_report = _tune_candidate_B_v11(
                case_B,
                t_max=min(t_max_aw, 1000),
                t_max_mc=min(t_max, 1000),
                n_mc=min(mc_samples, 10000),
                seed=seed + 399,
                smooth_w=peak_smooth_window,
                min_sep=5,
                min_gap=20,
                bin_width=mc_bin_width,
            )
            case_B_main = tuned_case
            if outputs_dir is not None:
                (outputs_dir / "tune_B.json").write_text(
                    json.dumps(tune_report, indent=2), encoding="utf-8"
                )

    spec_A = case_to_spec(case_A)
    spec_B = case_to_spec(case_B_main)
    spec_C = case_to_spec(case_C)

    cfg_A = spec_to_internal(spec_A)
    cfg_B = spec_to_internal(spec_B)
    cfg_C = spec_to_internal(spec_C)

    f_A, mass_A = exact_fpt(cfg_A, t_max=t_max)
    f_B, mass_B = exact_fpt(cfg_B, t_max=t_max)
    f_C, mass_C = exact_fpt(cfg_C, t_max=t_max)

    peaks_A = find_bimodality(f_A)
    peaks_B = find_bimodality(f_B)
    peaks_C = find_bimodality(f_C)

    compute_aw = fpt_method in ("aw", "both")
    if fig_version in ("main", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12") and not compute_aw:
        raise ValueError("main/v3/v4/v5/v6/v7/v8/v9/v10/v11/v12 figures require AW; use --fpt-method aw or both.")
    aw_inputs: Dict[str, dict] = {}
    if compute_aw:
        if fig_version in ("main", "v4", "v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12"):
            f_A_aw, aw_A, z_A, Fz_A = fpt_pmf_aw_with_grid(
                cfg_A, t_max=t_max_aw, oversample=aw_oversample, r_pow10=aw_r_pow10
            )
            f_B_aw, aw_B, z_B, Fz_B = fpt_pmf_aw_with_grid(
                cfg_B, t_max=t_max_aw, oversample=aw_oversample, r_pow10=aw_r_pow10
            )
            f_C_aw, aw_C, z_C, Fz_C = fpt_pmf_aw_with_grid(
                cfg_C, t_max=t_max_aw, oversample=aw_oversample, r_pow10=aw_r_pow10
            )
            aw_inputs = {
                "candidate_A": {"z": z_A, "Fz": Fz_A},
                prefix_B: {"z": z_B, "Fz": Fz_B},
                "candidate_C": {"z": z_C, "Fz": Fz_C},
            }
        else:
            f_A_aw, aw_A = fpt_pmf_aw(cfg_A, t_max=t_max_aw, oversample=aw_oversample, r_pow10=aw_r_pow10)
            f_B_aw, aw_B = fpt_pmf_aw(cfg_B, t_max=t_max_aw, oversample=aw_oversample, r_pow10=aw_r_pow10)
            f_C_aw, aw_C = fpt_pmf_aw(cfg_C, t_max=t_max_aw, oversample=aw_oversample, r_pow10=aw_r_pow10)
    else:
        f_A_aw = f_B_aw = f_C_aw = None
        aw_A = aw_B = aw_C = None

    mc_seed = seed + 10
    times_A, labels_A, stats_A = mc_candidate_A(cfg_A, n_walkers=mc_samples, seed=mc_seed, max_steps=t_max)
    mc_seed += 1

    corridor_set = corridor_set_from_spec(spec_B)
    corridor_band_1: set[tuple[int, int]] | None = None
    corridor_band_rows: List[int] | None = None
    if fig_version in ("main", "v6", "v7", "v8", "v9", "v10", "v11", "v12"):
        band_hw = 1
        if case_B_main.classification_rule and "band_halfwidth" in case_B_main.classification_rule:
            band_hw = int(case_B_main.classification_rule["band_halfwidth"])
        corridor_band_rows = _corridor_band_rows_from_case(case_B_main, default_halfwidth=band_hw)
        x_span = (min(case_B_main.start[0], case_B_main.target[0]), max(case_B_main.start[0], case_B_main.target[0]))
        if corridor_band_rows:
            corridor_band_1 = _corridor_band_from_rows(case_B_main, rows=corridor_band_rows, x_span=x_span)
        else:
            corridor_band_1 = _corridor_band(case_B_main, halfwidth=band_hw, x_span=x_span)
        corridor_band = {(x - 1, y - 1) for x, y in corridor_band_1}
    else:
        corridor_band = None
    times_B, labels_B, stats_B = mc_candidate_B(
        cfg_B,
        corridor_set,
        n_walkers=mc_samples,
        seed=mc_seed,
        max_steps=t_max,
        corridor_band=corridor_band,
    )
    mc_seed += 1

    door_edge = list(cfg_C.barriers_perm.keys())[0]
    sticky_set = sticky_set_from_spec(spec_C)
    t_valley_C = peaks_C.get("tv") or 1
    times_C, labels_C, stats_C = mc_candidate_C(
        cfg_C,
        door_edge=door_edge,
        sticky_set=sticky_set,
        t_valley=int(t_valley_C),
        n_walkers=mc_samples,
        seed=mc_seed,
        max_steps=t_max,
    )

    t_exact = np.arange(1, t_max + 1)
    t_aw = np.arange(1, t_max_aw + 1)

    def process_case(
        prefix: str,
        spec: ConfigSpec,
        cfg: LatticeConfig,
        f_exact: np.ndarray,
        f_aw: np.ndarray,
        peaks: dict,
        times: np.ndarray,
        labels: np.ndarray,
        stats: dict,
        aw_params,
    ) -> dict:
        pmf_all, tail = hist_pmf(times, t_plot=t_max)
        pmf_fast, _ = hist_pmf(times[labels == 0], t_plot=t_max)
        pmf_slow, _ = hist_pmf(times[labels == 1], t_plot=t_max)

        pmf_all_s = smooth_curve(pmf_all)
        pmf_fast_s = smooth_curve(pmf_fast)
        pmf_slow_s = smooth_curve(pmf_slow)

        err = _aw_errors(f_aw, f_exact[: t_max_aw]) if (compute_aw and f_aw is not None) else {
            "l1": 0.0,
            "linf": 0.0,
            "rel_l1": 0.0,
        }
        err["max_abs_error"] = err["linf"]

        if fig_version == "v2":
            plot_fpt_overlay(
                t=t_aw,
                f_exact=f_exact[: t_max_aw],
                f_aw=f_aw,
                f_mc=pmf_all_s[: t_max_aw],
                f_fast=pmf_fast_s[: t_max_aw],
                f_slow=pmf_slow_s[: t_max_aw],
                peaks=peaks,
                out_linear=fig_dir / f"{prefix}_fpt_linear.pdf",
                out_log=fig_dir / f"{prefix}_fpt_log.pdf",
                title=f"{prefix}: AW vs exact vs MC",
            )

        npz_payload = {
            "t_exact": t_exact,
            "f_exact": f_exact,
            "t_aw": t_aw,
            "pmf_all": pmf_all,
            "pmf_fast": pmf_fast,
            "pmf_slow": pmf_slow,
        }
        if f_aw is not None:
            npz_payload["f_aw"] = f_aw
        np.savez(DATA_DIR / f"{prefix}_curves.npz", **npz_payload)
        np.save(DATA_DIR / f"{prefix}_fpt_flux.npy", f_exact)
        if f_aw is not None:
            np.save(DATA_DIR / f"{prefix}_fpt_aw.npy", f_aw)
        np.save(DATA_DIR / f"{prefix}_fpt_mc.npy", pmf_all)

        return {
            "tail_mass": tail,
            "aw": {
                "enabled": bool(f_aw is not None),
                "m": int(aw_params.m) if aw_params is not None else 0,
                "r": float(aw_params.r) if aw_params is not None else 0.0,
                "oversample": int(aw_params.oversample) if aw_params is not None else 0,
                "r_pow10": float(aw_params.r_pow10) if aw_params is not None else 0.0,
                **err,
            },
        }

    extra_A = process_case("candidate_A", spec_A, cfg_A, f_A, f_A_aw, peaks_A, times_A, labels_A, stats_A, aw_A)
    extra_B = process_case(prefix_B, spec_B, cfg_B, f_B, f_B_aw, peaks_B, times_B, labels_B, stats_B, aw_B)
    extra_C = process_case("candidate_C", spec_C, cfg_C, f_C, f_C_aw, peaks_C, times_C, labels_C, stats_C, aw_C)

    path_A_fast, path_A_slow = find_paths_candidate_A(cfg_A, seed=seed + 100, max_steps=t_max)
    path_B_fast, path_B_slow = find_paths_candidate_B(cfg_B, corridor_set, seed=seed + 101, max_steps=t_max)
    path_C_fast, path_C_slow = find_paths_candidate_C(
        cfg_C, door_edge, int(t_valley_C), seed=seed + 102, max_steps=t_max
    )

    sticky_block = None
    if spec_C.sticky_sites:
        xs = [x for x, _ in spec_C.sticky_sites]
        ys = [y for _, y in spec_C.sticky_sites]
        sticky_block = ((min(xs), min(ys)), (max(xs), max(ys)))

    if fig_version == "v2":
        plot_schematic(
            cfg=cfg_A,
            spec=spec_A,
            path_fast=path_A_fast,
            path_slow=path_A_slow,
            outpath=fig_dir / "candidate_A_config.pdf",
        )
        plot_schematic(
            cfg=cfg_B,
            spec=spec_B,
            path_fast=path_B_fast,
            path_slow=path_B_slow,
            outpath=fig_dir / "candidate_B_config.pdf",
        )
        plot_schematic(
            cfg=cfg_C,
            spec=spec_C,
            path_fast=path_C_fast,
            path_slow=path_C_slow,
            outpath=fig_dir / "candidate_C_config.pdf",
            annotate_door=door_edge,
            sticky_block=sticky_block,
        )

    def add_heatmaps(prefix: str, cfg: LatticeConfig, spec: ConfigSpec, peaks: dict, path_fast, path_slow):
        times = _select_heatmap_times(peaks, t_max)
        dist = distributions_at_times(cfg, times, conditional=True)
        mats = [dist[t] for t in times]

        plot_heatmaps(
            heatmaps=mats,
            times=times,
            outpath=fig_dir / f"{prefix}_heatmaps.pdf",
            title=f"{prefix}: P(n,t) snapshots",
        )

        panel_times = times[:2]
        panel_mats = mats[:2]
        plot_candidate_panel(
            cfg=cfg,
            spec=spec,
            path_fast=path_fast,
            path_slow=path_slow,
            heatmaps=panel_mats,
            times=panel_times,
            t=t_aw,
            f_exact=dist_t_slice(f_exact=f_exact_map[prefix], t_aw=t_max_aw),
            f_aw=f_aw_map[prefix],
            f_mc=pmf_map[prefix],
            peaks=peaks,
            outpath=fig_dir / f"{prefix}_panel.pdf",
            annotate_door=door_edge if prefix == "candidate_C" else None,
            sticky_block=sticky_block if prefix == "candidate_C" else None,
        )

    f_exact_map = {
        "candidate_A": f_A,
        "candidate_B": f_B,
        "candidate_C": f_C,
    }
    f_aw_map = {
        "candidate_A": f_A_aw,
        "candidate_B": f_B_aw,
        "candidate_C": f_C_aw,
    }
    pmf_map = {
        "candidate_A": smooth_curve(hist_pmf(times_A, t_plot=t_max)[0])[: t_max_aw],
        "candidate_B": smooth_curve(hist_pmf(times_B, t_plot=t_max)[0])[: t_max_aw],
        "candidate_C": smooth_curve(hist_pmf(times_C, t_plot=t_max)[0])[: t_max_aw],
    }

    def dist_t_slice(*, f_exact: np.ndarray, t_aw: int) -> np.ndarray:
        return f_exact[:t_aw]

    if fig_version == "v2":
        add_heatmaps("candidate_A", cfg_A, spec_A, peaks_A, path_A_fast, path_A_slow)
        add_heatmaps("candidate_B", cfg_B, spec_B, peaks_B, path_B_fast, path_B_slow)
        add_heatmaps("candidate_C", cfg_C, spec_C, peaks_C, path_C_fast, path_C_slow)

    v3_meta: Dict[str, dict] = {}
    if fig_version == "v3":
        def plot_case_v3(
            prefix: str,
            cfg: LatticeConfig,
            spec: ConfigSpec,
            f_exact: np.ndarray,
            f_aw: np.ndarray,
            times: np.ndarray,
        ) -> dict:
            t1, tv, t2 = _select_peak_times_v3(
                f_exact,
                t_max=t_max_aw,
                smooth_window=peak_smooth_window,
            )
            heatmap_times = [t1, tv, t2]
            dist = distributions_at_times(cfg, heatmap_times, conditional=True)
            mats = [dist[t] for t in heatmap_times]

            plot_environment_figure(
                cfg=cfg,
                spec=spec,
                outpath=fig_dir / f"{prefix}_environment.pdf",
                png_dpi=png_dpi,
            )
            heatmap_info = plot_heatmap_figure(
                heatmaps=mats,
                times=heatmap_times,
                start=spec.start,
                target=spec.target,
                outpath=fig_dir / f"{prefix}_heatmaps.pdf",
                png_dpi=png_dpi,
            )
            plot_fpt_figure(
                t=t_aw,
                f_exact=f_exact[: t_max_aw],
                f_aw=f_aw,
                mc_times=times,
                t_max_aw=t_max_aw,
                peaks=(t1, tv, t2),
                mc_bin_width=mc_bin_width,
                mc_smooth_window=mc_smooth_window,
                log_eps=log_eps,
                outpath=fig_dir / f"{prefix}_fpt.pdf",
                png_dpi=png_dpi,
            )
            panel_info = plot_panel_v3(
                cfg=cfg,
                spec=spec,
                heatmaps=mats,
                times=heatmap_times,
                t=t_aw,
                f_exact=f_exact[: t_max_aw],
                f_aw=f_aw,
                mc_times=times,
                t_max_aw=t_max_aw,
                peaks=(t1, tv, t2),
                outpath=fig_dir / f"{prefix}_panel.pdf",
                png_dpi=png_dpi,
                mc_bin_width=mc_bin_width,
                mc_smooth_window=mc_smooth_window,
                log_eps=log_eps,
            )

            return {
                "t1": int(t1),
                "tv": int(tv),
                "t2": int(t2),
                "h1": float(f_exact[t1 - 1]),
                "hv": float(f_exact[tv - 1]),
                "h2": float(f_exact[t2 - 1]),
                "h2_over_h1": float(f_exact[t2 - 1] / f_exact[t1 - 1]) if f_exact[t1 - 1] > 0 else 0.0,
                "hv_over_max": float(f_exact[tv - 1] / max(f_exact[t1 - 1], f_exact[t2 - 1])),
                "heatmap_norm": panel_info["heatmap_norm"],
                "heatmap_times": panel_info["heatmap_times"],
                "heatmap_norm_fig": heatmap_info["heatmap_norm"],
            }

        v3_meta["candidate_A"] = plot_case_v3("candidate_A", cfg_A, spec_A, f_A, f_A_aw, times_A)
        v3_meta["candidate_B"] = plot_case_v3("candidate_B", cfg_B, spec_B, f_B, f_B_aw, times_B)
        v3_meta["candidate_C"] = plot_case_v3("candidate_C", cfg_C, spec_C, f_C, f_C_aw, times_C)

    v4_meta: Dict[str, dict] = {}
    if fig_version == "v4":
        legend_case = CaseGeometry(
            case_id="legend",
            name="legend",
            N=case_B.N,
            boundary_x=case_B.boundary_x,
            boundary_y=case_B.boundary_y,
            g_x=case_B.g_x,
            g_y=case_B.g_y,
            q=case_B.q,
            start=case_B.start,
            target=case_B.target,
            local_bias=case_B.local_bias,
            local_bias_delta=case_B.local_bias_delta,
            sticky=case_C.sticky,
            barriers_reflect=case_C.barriers_reflect,
            barriers_perm=case_C.barriers_perm,
            corridor=case_B.corridor,
            classification_rule=None,
        )
        save_symbol_legend(legend_case, fig_dir / "symbol_legend.pdf", dpi=png_dpi)

        def plot_case_v4(
            prefix: str,
            case: CaseGeometry,
            cfg: LatticeConfig,
            spec: ConfigSpec,
            f_exact: np.ndarray,
            f_aw: np.ndarray,
            times: np.ndarray,
            labels: np.ndarray,
            stats: dict,
        ) -> dict:
            t1, tv, t2 = _select_peak_times_v3(
                f_exact,
                t_max=t_max_aw,
                smooth_window=peak_smooth_window,
            )
            heatmap_times = [t1, tv, t2]
            dist = distributions_at_times(cfg, heatmap_times, conditional=True)
            mats = [dist[t] for t in heatmap_times]

            np.savez(
                DATA_DIR / f"{prefix}_Pt_times.npz",
                times=np.array(heatmap_times, dtype=np.int64),
                P=np.stack(mats, axis=0),
            )

            if prefix in aw_inputs:
                np.savez(
                    DATA_DIR / f"{prefix}_aw_input.npz",
                    z=aw_inputs[prefix]["z"],
                    Ftilde=aw_inputs[prefix]["Fz"],
                )
                np.savez(
                    DATA_DIR / f"{prefix}_aw_output.npz",
                    t=np.arange(1, t_max_aw + 1),
                    f_aw=f_aw,
                )

            roi = None
            if case.corridor:
                y = int(case.corridor["y"])
                x0 = int(case.corridor["x_start"])
                x1 = int(case.corridor["x_end"])
                roi = (
                    max(1, x0 - 2),
                    min(case.N, x1 + 2),
                    max(1, y - 3),
                    min(case.N, y + 3),
                )

            save_environment_figure(case, fig_dir / f"{prefix}_env.pdf", dpi=png_dpi)

            neighbors, cum_probs = build_mc_arrays(cfg)
            seed_offset = {"candidate_A": 301, "candidate_B": 302, "candidate_C": 303}.get(prefix, 300)
            rng = np.random.default_rng(seed + seed_offset)

            median_fast = _median_time(times, labels, 0)
            median_slow = _median_time(times, labels, 1)

            path_max_steps = min(t_max, 1200)

            if prefix == "candidate_A":
                def sample_fn(rng_local):
                    return sample_path_candidate_A(
                        cfg, max_steps=path_max_steps, rng=rng_local, neighbors=neighbors, cum_probs=cum_probs
                    )
            elif prefix == "candidate_B":
                corridor_set = corridor_set_from_spec(spec)

                def sample_fn(rng_local):
                    return sample_path_candidate_B(
                        cfg,
                        corridor_set,
                        max_steps=path_max_steps,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )
            else:
                door_edge = list(cfg.barriers_perm.keys())[0]

                def sample_fn(rng_local):
                    return sample_path_candidate_C(
                        cfg,
                        door_edge,
                        t_valley=tv,
                        max_steps=path_max_steps,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )

            rep_fast = _pick_representative_path(
                sample_fn, label=0, target_time=median_fast or 0, rng=rng, max_attempts=8000
            )
            rep_slow = _pick_representative_path(
                sample_fn, label=1, target_time=median_slow or 0, rng=rng, max_attempts=8000
            )

            path_fast = _to_one_based(rep_fast[0]) if rep_fast is not None else np.empty((0, 2), dtype=np.int64)
            path_slow = _to_one_based(rep_slow[0]) if rep_slow is not None else np.empty((0, 2), dtype=np.int64)
            t_fast = int(rep_fast[1]) if rep_fast is not None else -1
            t_slow = int(rep_slow[1]) if rep_slow is not None else -1

            np.savez(
                DATA_DIR / f"{prefix}_rep_trajs.npz",
                fast_traj=path_fast,
                slow_traj=path_slow,
                t_fast=t_fast,
                t_slow=t_slow,
                median_fast=median_fast or -1,
                median_slow=median_slow or -1,
            )

            save_path_figure(
                case,
                traj=path_fast,
                label="fast channel",
                color="#fdae61",
                outpath=fig_dir / f"{prefix}_path_fast.pdf",
                dpi=png_dpi,
            )
            save_path_figure(
                case,
                traj=path_slow,
                label="slow channel",
                color="#66c2a5",
                outpath=fig_dir / f"{prefix}_path_slow.pdf",
                dpi=png_dpi,
            )

            heatmap_norm = plot_heatmap_triplet(
                case,
                mats,
                heatmap_times,
                outpath=fig_dir / f"{prefix}_heatmaps.pdf",
                roi=roi,
                dpi=png_dpi,
            )

            plot_fpt(
                t=t_aw,
                f_exact=f_exact[: t_max_aw],
                f_aw=f_aw,
                mc_times=times,
                t_max_aw=t_max_aw,
                peaks=(t1, tv, t2),
                mc_bin_width=mc_bin_width,
                mc_smooth_window=mc_smooth_window,
                log_eps=log_eps,
                outpath=fig_dir / f"{prefix}_fpt.pdf",
                dpi=png_dpi,
            )

            pmf_fast, _ = hist_pmf(times[labels == 0], t_plot=t_max)
            pmf_slow, _ = hist_pmf(times[labels == 1], t_plot=t_max)
            pmf_fast_s = _moving_average(pmf_fast, mc_smooth_window)
            pmf_slow_s = _moving_average(pmf_slow, mc_smooth_window)

            p_fast = float((labels == 0).mean()) if labels.size else 0.0
            p_slow = float(1.0 - p_fast)

            plot_channel_mix(
                t=t_exact,
                f_fast=pmf_fast_s,
                f_slow=pmf_slow_s,
                p_fast=p_fast,
                p_slow=p_slow,
                outpath=fig_dir / f"{prefix}_channels.pdf",
                dpi=png_dpi,
            )

            panel_info = plot_panel_v4(
                case=case,
                traj=path_fast if path_fast.size else None,
                traj_label="fast channel",
                heatmaps=mats,
                times=heatmap_times,
                t=t_aw,
                f_exact=f_exact[: t_max_aw],
                f_aw=f_aw,
                mc_times=times,
                t_max_aw=t_max_aw,
                peaks=(t1, tv, t2),
                mc_bin_width=mc_bin_width,
                mc_smooth_window=mc_smooth_window,
                log_eps=log_eps,
                outpath=fig_dir / f"{prefix}_panel.pdf",
                roi=roi,
                dpi=png_dpi,
            )

            return {
                "t1": int(t1),
                "tv": int(tv),
                "t2": int(t2),
                "h1": float(f_exact[t1 - 1]),
                "hv": float(f_exact[tv - 1]),
                "h2": float(f_exact[t2 - 1]),
                "h2_over_h1": float(f_exact[t2 - 1] / f_exact[t1 - 1]) if f_exact[t1 - 1] > 0 else 0.0,
                "hv_over_max": float(f_exact[tv - 1] / max(f_exact[t1 - 1], f_exact[t2 - 1])),
                "p_fast": p_fast,
                "p_slow": p_slow,
                "heatmap_norm": heatmap_norm,
                "heatmap_times": [int(t) for t in heatmap_times],
            }

        v4_meta["candidate_A"] = plot_case_v4("candidate_A", case_A, cfg_A, spec_A, f_A, f_A_aw, times_A, labels_A, stats_A)
        v4_meta["candidate_B"] = plot_case_v4("candidate_B", case_B, cfg_B, spec_B, f_B, f_B_aw, times_B, labels_B, stats_B)
        v4_meta["candidate_C"] = plot_case_v4("candidate_C", case_C, cfg_C, spec_C, f_C, f_C_aw, times_C, labels_C, stats_C)

    def save_metrics(
        prefix: str,
        spec: ConfigSpec,
        f: np.ndarray,
        mass: float,
        peaks: dict,
        stats: dict,
        extra: dict,
    ) -> None:
        payload = {
            "config": config_to_dict(spec),
            "mass": float(mass),
            **peaks,
            "mc": stats | {"tail_mass": extra["tail_mass"]},
            "aw": extra["aw"],
        }
        (DATA_DIR / f"{prefix}_metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    save_metrics("candidate_A", spec_A, f_A, mass_A, peaks_A, stats_A, extra_A)
    save_metrics(prefix_B, spec_B, f_B, mass_B, peaks_B, stats_B, extra_B)
    save_metrics("candidate_C", spec_C, f_C, mass_C, peaks_C, stats_C, extra_C)

    if fig_version == "v3":
        def save_metrics_v3(prefix: str, spec: ConfigSpec, f: np.ndarray, stats: dict, extra: dict) -> None:
            v3_payload = {
                "config": config_to_dict(spec),
                "peaks": v3_meta[prefix],
                "mc": stats | {"tail_mass": extra["tail_mass"]},
                "aw": extra["aw"],
                "plot_params": {
                    "fig_version": fig_version,
                    "plot_style": plot_style,
                    "png_dpi": int(png_dpi),
                    "mc_bin_width": int(mc_bin_width),
                    "mc_smooth_window": int(mc_smooth_window),
                    "peak_smooth_window": int(peak_smooth_window),
                    "log_eps": float(log_eps),
                },
            }
            (DATA_DIR / f"{prefix}_metrics_v3.json").write_text(
                json.dumps(v3_payload, indent=2), encoding="utf-8"
            )

        save_metrics_v3("candidate_A", spec_A, f_A, stats_A, extra_A)
        save_metrics_v3("candidate_B", spec_B, f_B, stats_B, extra_B)
        save_metrics_v3("candidate_C", spec_C, f_C, stats_C, extra_C)

    if fig_version == "v4":
        def save_metrics_v4(prefix: str, spec: ConfigSpec, stats: dict, extra: dict) -> None:
            v4_payload = {
                "config": config_to_dict(spec),
                "peaks": v4_meta[prefix],
                "mc": stats | {"tail_mass": extra["tail_mass"]},
                "aw": extra["aw"],
                "plot_params": {
                    "fig_version": fig_version,
                    "plot_style": plot_style,
                    "png_dpi": int(png_dpi),
                    "mc_bin_width": int(mc_bin_width),
                    "mc_smooth_window": int(mc_smooth_window),
                    "peak_smooth_window": int(peak_smooth_window),
                    "log_eps": float(log_eps),
                },
            }
            (DATA_DIR / f"{prefix}_metrics_v4.json").write_text(
                json.dumps(v4_payload, indent=2), encoding="utf-8"
            )

        save_metrics_v4("candidate_A", spec_A, stats_A, extra_A)
        save_metrics_v4("candidate_B", spec_B, stats_B, extra_B)
        save_metrics_v4("candidate_C", spec_C, stats_C, extra_C)

    if fig_version == "v5":
        legend_case = CaseGeometry(
            case_id="legend",
            name="legend",
            N=case_B.N,
            boundary_x=case_B.boundary_x,
            boundary_y=case_B.boundary_y,
            g_x=case_B.g_x,
            g_y=case_B.g_y,
            q=case_B.q,
            start=case_B.start,
            target=case_B.target,
            local_bias=case_B.local_bias,
            local_bias_delta=case_B.local_bias_delta,
            sticky=case_C.sticky,
            barriers_reflect=case_C.barriers_reflect,
            barriers_perm=case_C.barriers_perm,
            corridor=case_B.corridor,
            classification_rule=None,
        )
        plot_symbol_legend(legend_case, outpath=str(fig_dir / "symbol_legend.pdf"), dpi=png_dpi)

        def case_roi(case: CaseGeometry) -> Tuple[ViewBox, ViewBox]:
            main = ViewBox(1, case.N, 1, case.N)
            if case.corridor:
                y = int(case.corridor["y"])
                x0 = int(case.corridor["x_start"])
                x1 = int(case.corridor["x_end"])
                roi = ViewBox(
                    max(1, x0 - 3),
                    min(case.N, x1 + 3),
                    max(1, y - 4),
                    min(case.N, y + 4),
                )
                return main, roi
            if case.sticky or case.barriers_perm:
                xs = [c["x"] for c in case.sticky] if case.sticky else [case.start[0], case.target[0]]
                ys = [c["y"] for c in case.sticky] if case.sticky else [case.start[1], case.target[1]]
                if case.barriers_perm:
                    (a, b), _ = case.barriers_perm[0]
                    xs.extend([a[0], b[0]])
                    ys.extend([a[1], b[1]])
                roi = ViewBox(
                    max(1, min(xs) - 4),
                    min(case.N, max(xs) + 4),
                    max(1, min(ys) - 4),
                    min(case.N, max(ys) + 4),
                )
                return main, roi
            roi = ViewBox(
                max(1, min(case.start[0], case.target[0]) - 5),
                min(case.N, max(case.start[0], case.target[0]) + 5),
                max(1, min(case.start[1], case.target[1]) - 5),
                min(case.N, max(case.start[1], case.target[1]) + 5),
            )
            return main, roi

        def plot_case_v5(
            prefix: str,
            case: CaseGeometry,
            cfg: LatticeConfig,
            spec: ConfigSpec,
            f_exact: np.ndarray,
            f_aw: np.ndarray,
            times: np.ndarray,
            labels: np.ndarray,
        ) -> dict:
            t1, tv, t2 = _select_peak_times_v3(
                f_exact,
                t_max=t_max_aw,
                smooth_window=peak_smooth_window,
            )
            heatmap_times = [t1, tv, t2]
            dist = distributions_at_times(cfg, heatmap_times, conditional=True)
            mats = [dist[t] for t in heatmap_times]
            np.savez(
                DATA_DIR / f"{prefix}_Pt_times_v5.npz",
                times=np.array(heatmap_times, dtype=np.int64),
                P=np.stack(mats, axis=0),
            )

            if prefix in aw_inputs:
                np.savez(
                    DATA_DIR / f"{prefix}_aw_input_v5.npz",
                    z=aw_inputs[prefix]["z"],
                    Ftilde=aw_inputs[prefix]["Fz"],
                )
                np.savez(
                    DATA_DIR / f"{prefix}_aw_output_v5.npz",
                    t=np.arange(1, t_max_aw + 1),
                    f_aw=f_aw,
                )

            main_view, roi_view = case_roi(case)

            plot_environment(
                case,
                outpath=str(fig_dir / f"{prefix}_env.pdf"),
                view=main_view,
                view_roi=roi_view,
                dpi=png_dpi,
            )

            neighbors, cum_probs = build_mc_arrays(cfg)
            seed_offset = {"candidate_A": 401, "candidate_B": 402, "candidate_C": 403}.get(prefix, 400)
            rng = np.random.default_rng(seed + seed_offset)

            median_fast = _median_time(times, labels, 0) or 1
            median_slow = _median_time(times, labels, 1) or 1

            if prefix == "candidate_A":
                def sample_fn(rng_local):
                    return sample_path_candidate_A(
                        cfg, max_steps=t_max, rng=rng_local, neighbors=neighbors, cum_probs=cum_probs
                    )
            elif prefix == "candidate_B":
                corridor_set = corridor_set_from_spec(spec)

                def sample_fn(rng_local):
                    return sample_path_candidate_B(
                        cfg,
                        corridor_set,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )
            else:
                door_edge = list(cfg.barriers_perm.keys())[0]

                def sample_fn(rng_local):
                    return sample_path_candidate_C(
                        cfg,
                        door_edge,
                        t_valley=tv,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )

            rep_fast = _pick_representative_path(
                sample_fn, label=0, target_time=median_fast, rng=rng, max_attempts=8000
            )
            rep_slow = _pick_representative_path(
                sample_fn, label=1, target_time=median_slow, rng=rng, max_attempts=8000
            )
            rep_fast_path = _to_one_based(rep_fast[0]) if rep_fast else np.empty((0, 2), dtype=np.int64)
            rep_slow_path = _to_one_based(rep_slow[0]) if rep_slow else np.empty((0, 2), dtype=np.int64)

            paths_fast = _collect_paths(sample_fn, label=0, n_paths=25, rng=rng, max_attempts=15000)
            paths_slow = _collect_paths(sample_fn, label=1, n_paths=25, rng=rng, max_attempts=15000)

            np.savez(
                DATA_DIR / f"{prefix}_paths_v5.npz",
                paths_fast=np.array(paths_fast, dtype=object),
                paths_slow=np.array(paths_slow, dtype=object),
                rep_fast=rep_fast_path,
                rep_slow=rep_slow_path,
                t_fast=int(rep_fast[1]) if rep_fast else -1,
                t_slow=int(rep_slow[1]) if rep_slow else -1,
            )

            plot_paths_figure(
                case,
                paths=paths_fast,
                rep_path=rep_fast_path,
                title="Fast-channel trajectories",
                outpath=str(fig_dir / f"{prefix}_paths_fast.pdf"),
                mode="gradient",
                dpi=png_dpi,
            )
            plot_paths_figure(
                case,
                paths=paths_slow,
                rep_path=rep_slow_path,
                title="Slow-channel trajectories",
                outpath=str(fig_dir / f"{prefix}_paths_slow.pdf"),
                mode="turning",
                dpi=png_dpi,
            )

            heatmap_norm = plot_prob_snapshots(
                case=case,
                mats=mats,
                t_list=heatmap_times,
                outpath=str(fig_dir / f"{prefix}_heatmaps.pdf"),
                view_main=main_view,
                view_roi=roi_view,
                dpi=png_dpi,
            )

            plot_fpt_big(
                t=t_exact,
                f_exact=f_exact,
                f_aw=f_aw,
                mc_times=times,
                t_max_aw=t_max_aw,
                marks=(t1, tv, t2),
                outpath=str(fig_dir / f"{prefix}_fpt.pdf"),
                bin_width=mc_bin_width,
                log_eps=log_eps,
                dpi=png_dpi,
            )

            pmf_fast, _ = hist_pmf(times[labels == 0], t_plot=t_max)
            pmf_slow, _ = hist_pmf(times[labels == 1], t_plot=t_max)
            pmf_fast_s = _moving_average(pmf_fast, mc_smooth_window)
            pmf_slow_s = _moving_average(pmf_slow, mc_smooth_window)

            p_fast = float((labels == 0).mean()) if labels.size else 0.0
            p_slow = float(1.0 - p_fast)
            plot_channel_decomp(
                t=t_exact,
                f_fast=pmf_fast_s,
                f_slow=pmf_slow_s,
                p_fast=p_fast,
                p_slow=p_slow,
                outpath=str(fig_dir / f"{prefix}_channel_decomp.pdf"),
                dpi=png_dpi,
            )

            if case.boundary_x == "periodic":
                plot_periodic_unwrapped(case=case, outpath=str(fig_dir / f"{prefix}_unwrapped.pdf"), dpi=png_dpi)

            return {
                "t1": int(t1),
                "tv": int(tv),
                "t2": int(t2),
                "h1": float(f_exact[t1 - 1]),
                "hv": float(f_exact[tv - 1]),
                "h2": float(f_exact[t2 - 1]),
                "h2_over_h1": float(f_exact[t2 - 1] / f_exact[t1 - 1]) if f_exact[t1 - 1] > 0 else 0.0,
                "hv_over_max": float(f_exact[tv - 1] / max(f_exact[t1 - 1], f_exact[t2 - 1])),
                "p_fast": p_fast,
                "p_slow": p_slow,
                "heatmap_norm": heatmap_norm,
            }

        v5_meta = {
            "candidate_A": plot_case_v5("candidate_A", case_A, cfg_A, spec_A, f_A, f_A_aw, times_A, labels_A),
            "candidate_B": plot_case_v5("candidate_B", case_B, cfg_B, spec_B, f_B, f_B_aw, times_B, labels_B),
            "candidate_C": plot_case_v5("candidate_C", case_C, cfg_C, spec_C, f_C, f_C_aw, times_C, labels_C),
        }

        def save_metrics_v5(prefix: str, spec: ConfigSpec, stats: dict, extra: dict) -> None:
            v5_payload = {
                "config": config_to_dict(spec),
                "peaks": v5_meta[prefix],
                "mc": stats | {"tail_mass": extra["tail_mass"]},
                "aw": extra["aw"],
                "plot_params": {
                    "fig_version": fig_version,
                    "plot_style": plot_style,
                    "png_dpi": int(png_dpi),
                    "mc_bin_width": int(mc_bin_width),
                    "mc_smooth_window": int(mc_smooth_window),
                    "peak_smooth_window": int(peak_smooth_window),
                    "log_eps": float(log_eps),
                },
            }
            (DATA_DIR / f"{prefix}_metrics_v5.json").write_text(
                json.dumps(v5_payload, indent=2), encoding="utf-8"
            )

        save_metrics_v5("candidate_A", spec_A, stats_A, extra_A)
        save_metrics_v5("candidate_B", spec_B, stats_B, extra_B)
        save_metrics_v5("candidate_C", spec_C, stats_C, extra_C)

    if fig_version in ("v6", "v7", "v8"):
        if fig_subdirs is None:
            raise RuntimeError("v6 figure directories not initialized.")

        version_tag = fig_version
        fig3v2.plot_cartoon_channels(outpath=fig_subdirs["fig3_panels"] / "channel_cartoon.pdf", dpi=png_dpi)
        fig3v2.plot_symbol_legend(outpath=fig_subdirs["env"] / "symbol_legend.pdf", dpi=png_dpi)

        def _sanity_check_fpt(f: np.ndarray, *, name: str) -> None:
            if np.any(f < -1e-15):
                raise ValueError(f"{name} has negative entries below tolerance.")
            mass = float(np.sum(f))
            if not (0.0 <= mass <= 1.0 + 1e-3):
                raise ValueError(f"{name} mass out of bounds (sum={mass:.6f}).")

        _sanity_check_fpt(f_A, name="f_exact_A")
        _sanity_check_fpt(f_B, name="f_exact_B")
        _sanity_check_fpt(f_C, name="f_exact_C")

        if f_A_aw is not None and np.min(f_A_aw) < -1e-12:
            raise ValueError("f_aw_A has negative entries beyond tolerance.")
        if f_B_aw is not None and np.min(f_B_aw) < -1e-12:
            raise ValueError("f_aw_B has negative entries beyond tolerance.")
        if f_C_aw is not None and np.min(f_C_aw) < -1e-12:
            raise ValueError("f_aw_C has negative entries beyond tolerance.")

        def plot_case_v6(
            prefix: str,
            case: CaseGeometry,
            cfg: LatticeConfig,
            spec: ConfigSpec,
            f_exact: np.ndarray,
            f_aw: np.ndarray,
            times: np.ndarray,
            labels: np.ndarray,
            *,
            corridor_band: set[tuple[int, int]] | None = None,
        ) -> dict:
            t1, tv, t2 = _select_peak_times_v3(
                f_exact,
                t_max=t_max_aw,
                smooth_window=peak_smooth_window,
            )
            heatmap_times = [t1, tv, t2]
            dist = distributions_at_times(cfg, heatmap_times, conditional=True)
            mats = [dist[t] for t in heatmap_times]
            np.savez(
                DATA_DIR / f"{prefix}_Pt_times_{version_tag}.npz",
                times=np.array(heatmap_times, dtype=np.int64),
                P=np.stack(mats, axis=0),
            )

            if prefix in aw_inputs:
                np.savez(
                    DATA_DIR / f"{prefix}_aw_input_{version_tag}.npz",
                    z=aw_inputs[prefix]["z"],
                    Ftilde=aw_inputs[prefix]["Fz"],
                )
                np.savez(
                    DATA_DIR / f"{prefix}_aw_output_{version_tag}.npz",
                    t=np.arange(1, t_max_aw + 1),
                    f_aw=f_aw,
                )

            roi = fig3v2.compute_roi(case, include_barriers=False)
            fig3v2.plot_environment(
                case,
                outpath=fig_subdirs["env"] / f"{prefix}_env.pdf",
                view=None,
                roi=roi,
                dpi=png_dpi,
            )

            fig3v2.plot_fig3_panel(
                case,
                mats=mats,
                times=heatmap_times,
                outpath=fig_subdirs["fig3_panels"] / f"{prefix}_fig3_panel.pdf",
                dpi=png_dpi,
            )

            fig3v2.plot_heatmap_triplet(
                case,
                mats=mats,
                times=heatmap_times,
                outpath=fig_subdirs["heatmaps"] / f"{prefix}_heatmaps.pdf",
                dpi=png_dpi,
            )

            neighbors, cum_probs = build_mc_arrays(cfg)
            seed_offset = {"candidate_A": 501, "candidate_B": 502, "candidate_C": 503}.get(prefix, 500)
            rng = np.random.default_rng(seed + seed_offset)

            median_fast = _median_time(times, labels, 0) or 1
            median_slow = _median_time(times, labels, 1) or 1

            if prefix == "candidate_A":
                def sample_fn(rng_local):
                    return sample_path_candidate_A(
                        cfg, max_steps=t_max, rng=rng_local, neighbors=neighbors, cum_probs=cum_probs
                    )
            elif prefix == "candidate_B":
                corridor_set = corridor_set_from_spec(spec)

                def sample_fn(rng_local):
                    return sample_path_candidate_B(
                        cfg,
                        corridor_set,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                        corridor_band=corridor_band,
                    )
            else:
                door_edge = list(cfg.barriers_perm.keys())[0]

                def sample_fn(rng_local):
                    return sample_path_candidate_C(
                        cfg,
                        door_edge,
                        t_valley=tv,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )

            rep_fast = _pick_representative_path(
                sample_fn, label=0, target_time=median_fast, rng=rng, max_attempts=12000
            )
            rep_slow = _pick_representative_path(
                sample_fn, label=1, target_time=median_slow, rng=rng, max_attempts=12000
            )
            rep_fast_path = _to_one_based(rep_fast[0]) if rep_fast else np.empty((0, 2), dtype=np.int64)
            rep_slow_path = _to_one_based(rep_slow[0]) if rep_slow else np.empty((0, 2), dtype=np.int64)

            paths_fast = _collect_paths(sample_fn, label=0, n_paths=50, rng=rng, max_attempts=40000)
            paths_slow = _collect_paths(sample_fn, label=1, n_paths=50, rng=rng, max_attempts=40000)

            np.savez(
                DATA_DIR / f"{prefix}_paths_{version_tag}.npz",
                paths_fast=np.array(paths_fast, dtype=object),
                paths_slow=np.array(paths_slow, dtype=object),
                rep_fast=rep_fast_path,
                rep_slow=rep_slow_path,
                t_fast=int(rep_fast[1]) if rep_fast else -1,
                t_slow=int(rep_slow[1]) if rep_slow else -1,
            )

            event_fast: list[tuple[int, int, str]] = []
            event_slow: list[tuple[int, int, str]] = []
            if prefix == "candidate_A":
                pt = _event_point_wrap(rep_fast_path, N=case.N)
                if pt:
                    event_fast.append((pt[0], pt[1], "wrap"))
                pt = _event_point_wrap(rep_slow_path, N=case.N)
                if pt:
                    event_slow.append((pt[0], pt[1], "wrap"))
            elif prefix == "candidate_B":
                if corridor_band_1 is not None:
                    pt = _event_point_corridor_exit(rep_slow_path, corridor_band_1)
                    if pt:
                        event_slow.append((pt[0], pt[1], "exit"))
            else:
                door_edge = list(cfg.barriers_perm.keys())[0]
                pt = _event_point_door(rep_fast_path, door_edge)
                if pt:
                    event_fast.append((pt[0], pt[1], "door"))
                pt = _event_point_door(rep_slow_path, door_edge)
                if pt:
                    event_slow.append((pt[0], pt[1], "door"))

            fig3v2.plot_paths_density(
                case,
                paths=paths_fast,
                rep_path=rep_fast_path,
                event_points=event_fast,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_fast.pdf",
                title=f"{case.name}: fast channel density",
                dpi=png_dpi,
            )
            fig3v2.plot_paths_density(
                case,
                paths=paths_slow,
                rep_path=rep_slow_path,
                event_points=event_slow,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_slow.pdf",
                title=f"{case.name}: slow channel density",
                dpi=png_dpi,
            )

            p_fast = float((labels == 0).mean()) if labels.size else 0.0
            p_slow = float((labels == 1).mean()) if labels.size else 0.0

            pmf_full, _ = hist_pmf(times, t_plot=t_max)
            if abs(float(pmf_full.sum()) - 1.0) > 5e-3:
                raise ValueError(f"{prefix} MC pmf sum check failed: {pmf_full.sum():.6f}")

            tail_start = max(int(tv + 30), 200)
            tail_bin_width = max(int(mc_bin_width) * 3, 6)
            tail_smooth_window = max(int(mc_smooth_window) + 6, int(mc_smooth_window) * 2)

            t_centers, pmf_all = _mc_histogram(
                times,
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(times.size),
            )

            fig3v2.plot_fpt_multiscale(
                t_exact=t_exact,
                f_exact=f_exact,
                t_aw=t_aw,
                f_aw=f_aw if f_aw is not None else np.array([]),
                mc_centers=t_centers,
                mc_pmf=pmf_all,
                peaks=(t1, tv, t2),
                outpath=fig_subdirs["fpt"] / f"{prefix}_fpt.pdf",
                log_eps=log_eps,
                dpi=png_dpi,
            )

            _, pmf_fast = _mc_histogram(
                times[labels == 0],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 0)),
            )
            _, pmf_slow = _mc_histogram(
                times[labels == 1],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 1)),
            )

            fig3v2.plot_channel_decomp(
                t=t_centers,
                f_fast=pmf_fast,
                f_slow=pmf_slow,
                p_fast=p_fast,
                p_slow=p_slow,
                outpath=fig_subdirs["channel_decomp"] / f"{prefix}_channel_decomp.pdf",
                dpi=png_dpi,
            )

            if case.boundary_x == "periodic":
                fig3v2.plot_periodic_unwrapped_two_tiles(
                    case,
                    outpath=fig_subdirs["unwrapped"] / f"{prefix}_unwrapped.pdf",
                    dpi=png_dpi,
                )

            return {
                "t1": int(t1),
                "tv": int(tv),
                "t2": int(t2),
                "h1": float(f_exact[t1 - 1]),
                "hv": float(f_exact[tv - 1]),
                "h2": float(f_exact[t2 - 1]),
                "h2_over_h1": float(f_exact[t2 - 1] / f_exact[t1 - 1]) if f_exact[t1 - 1] > 0 else 0.0,
                "hv_over_max": float(f_exact[tv - 1] / max(f_exact[t1 - 1], f_exact[t2 - 1])),
                "p_fast": p_fast,
                "p_slow": p_slow,
                "heatmap_times": [int(t) for t in heatmap_times],
            }

        v6_meta = {
            "candidate_A": plot_case_v6("candidate_A", case_A, cfg_A, spec_A, f_A, f_A_aw, times_A, labels_A),
            "candidate_B": plot_case_v6(
                "candidate_B", case_B, cfg_B, spec_B, f_B, f_B_aw, times_B, labels_B, corridor_band=corridor_band
            ),
            "candidate_C": plot_case_v6("candidate_C", case_C, cfg_C, spec_C, f_C, f_C_aw, times_C, labels_C),
        }

        def save_metrics_v6(prefix: str, spec: ConfigSpec, stats: dict, extra: dict) -> None:
            v6_payload = {
                "config": config_to_dict(spec),
                "peaks": v6_meta[prefix],
                "mc": stats | {"tail_mass": extra["tail_mass"]},
                "aw": extra["aw"],
                "plot_params": {
                    "fig_version": fig_version,
                    "plot_style": plot_style,
                    "png_dpi": int(png_dpi),
                    "mc_bin_width": int(mc_bin_width),
                    "mc_smooth_window": int(mc_smooth_window),
                    "peak_smooth_window": int(peak_smooth_window),
                    "log_eps": float(log_eps),
                },
            }
            (DATA_DIR / f"{prefix}_metrics_{version_tag}.json").write_text(
                json.dumps(v6_payload, indent=2), encoding="utf-8"
            )

        save_metrics_v6("candidate_A", spec_A, stats_A, extra_A)
        save_metrics_v6("candidate_B", spec_B, stats_B, extra_B)
        save_metrics_v6("candidate_C", spec_C, stats_C, extra_C)

        fig3v2.write_gallery_html(fig_dir)

    if fig_version == "v8":
        if fig_subdirs is None:
            raise RuntimeError("v8 figure directories not initialized.")

        fig3v8.apply_style_v8()
        plot_symbol_legend_v8(outpath=fig_subdirs["env"] / "symbol_legend.pdf", dpi=png_dpi)

        def _sanity_check_fpt(f: np.ndarray, *, name: str) -> None:
            if np.any(f < -1e-15):
                raise ValueError(f"{name} has negative entries below tolerance.")
            mass = float(np.sum(f))
            if not (0.0 <= mass <= 1.0 + 1e-3):
                raise ValueError(f"{name} mass out of bounds (sum={mass:.6f}).")

        _sanity_check_fpt(f_A, name="f_exact_A")
        _sanity_check_fpt(f_B, name="f_exact_B")
        _sanity_check_fpt(f_C, name="f_exact_C")

        if f_A_aw is not None and np.min(f_A_aw) < -1e-12:
            raise ValueError("f_aw_A has negative entries beyond tolerance.")
        if f_B_aw is not None and np.min(f_B_aw) < -1e-12:
            raise ValueError("f_aw_B has negative entries beyond tolerance.")
        if f_C_aw is not None and np.min(f_C_aw) < -1e-12:
            raise ValueError("f_aw_C has negative entries beyond tolerance.")

        def plot_case_v8(
            prefix: str,
            case: CaseGeometry,
            cfg: LatticeConfig,
            spec: ConfigSpec,
            f_exact: np.ndarray,
            f_aw: np.ndarray | None,
            times: np.ndarray,
            labels: np.ndarray,
            *,
            corridor_band: set[tuple[int, int]] | None = None,
        ) -> dict:
            try:
                detect = fig3v8.detect_bimodality(
                    f_exact[:t_max_aw], smooth_w=peak_smooth_window, min_sep=5
                )
                t1, tv, t2 = int(detect["p1"]), int(detect["v"]), int(detect["p2"])
            except RuntimeError:
                t1, tv, t2 = _select_peak_times_v3(
                    f_exact,
                    t_max=t_max_aw,
                    smooth_window=peak_smooth_window,
                )
                detect = {
                    "p1": t1,
                    "v": tv,
                    "p2": t2,
                    "h1": float(f_exact[t1 - 1]),
                    "h2": float(f_exact[t2 - 1]),
                    "hv": float(f_exact[tv - 1]),
                    "ratio": float(f_exact[t2 - 1] / f_exact[t1 - 1]) if f_exact[t1 - 1] > 0 else np.nan,
                    "valley": float(f_exact[tv - 1] / max(f_exact[t1 - 1], f_exact[t2 - 1])),
                    "fallback": True,
                }
            heatmap_times = [t1, tv, t2]
            dist = distributions_at_times(cfg, heatmap_times, conditional=True)
            mats = [dist[t] for t in heatmap_times]
            np.savez(
                DATA_DIR / f"{prefix}_Pt_times_v8.npz",
                times=np.array(heatmap_times, dtype=np.int64),
                P=np.stack(mats, axis=0),
            )

            f_aw_arr = f_aw if f_aw is not None else np.array([])
            if prefix in aw_inputs:
                np.savez(
                    DATA_DIR / f"{prefix}_aw_input_v8.npz",
                    z=aw_inputs[prefix]["z"],
                    Ftilde=aw_inputs[prefix]["Fz"],
                )
                np.savez(
                    DATA_DIR / f"{prefix}_aw_output_v8.npz",
                    t=np.arange(1, t_max_aw + 1),
                    f_aw=f_aw_arr,
                )

            band_hw = 1
            if case.classification_rule and "band_halfwidth" in case.classification_rule:
                band_hw = int(case.classification_rule["band_halfwidth"])

            roi = fig3v8.roi_bounds_auto(case, margin=6)

            extra_text = None
            if case.corridor:
                y0 = int(case.corridor["y"])
                band_vals = [y0 - band_hw, y0, y0 + band_hw]
                L = abs(int(case.corridor["x_end"]) - int(case.corridor["x_start"])) + 1
                extra_text = f"corridor y={band_vals}\nL={L}, delta={case.local_bias_delta:.2f}"

            plot_environment_v8(
                case,
                outpath=fig_subdirs["env"] / f"{prefix}_env.pdf",
                dpi=png_dpi,
                roi=roi,
                bias_step_main=4 if prefix == "candidate_B" else 2,
                bias_step_zoom=1,
                corridor_halfwidth=band_hw,
                extra_text=extra_text,
            )

            plot_fig3_panel_v8(
                case,
                mats=mats,
                times=heatmap_times,
                outpath=fig_subdirs["fig3_panels"] / f"{prefix}_fig3_panel.pdf",
                dpi=png_dpi,
                bias_step_env=4 if prefix == "candidate_B" else 2,
                bias_step_heat=1,
                corridor_halfwidth=band_hw,
            )

            neighbors, cum_probs = build_mc_arrays(cfg)
            seed_offset = {"candidate_A": 701, "candidate_B": 702, "candidate_C": 703}.get(prefix, 700)
            rng = np.random.default_rng(seed + seed_offset)

            median_fast = _median_time(times, labels, 0) or 1
            median_slow = _median_time(times, labels, 1) or 1

            if prefix == "candidate_A":

                def sample_fn(rng_local):
                    return sample_path_candidate_A(
                        cfg, max_steps=t_max, rng=rng_local, neighbors=neighbors, cum_probs=cum_probs
                    )

            elif prefix == "candidate_B":
                corridor_set = corridor_set_from_spec(spec)

                def sample_fn(rng_local):
                    return sample_path_candidate_B(
                        cfg,
                        corridor_set,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                        corridor_band=corridor_band,
                    )

            else:
                door_edge = list(cfg.barriers_perm.keys())[0]

                def sample_fn(rng_local):
                    return sample_path_candidate_C(
                        cfg,
                        door_edge,
                        t_valley=tv,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )

            rep_fast = _pick_representative_path(
                sample_fn, label=0, target_time=median_fast, rng=rng, max_attempts=12000
            )
            rep_slow = _pick_representative_path(
                sample_fn, label=1, target_time=median_slow, rng=rng, max_attempts=12000
            )
            rep_fast_path = _to_one_based(rep_fast[0]) if rep_fast else np.empty((0, 2), dtype=np.int64)
            rep_slow_path = _to_one_based(rep_slow[0]) if rep_slow else np.empty((0, 2), dtype=np.int64)

            paths_fast = _collect_paths(sample_fn, label=0, n_paths=50, rng=rng, max_attempts=40000)
            paths_slow = _collect_paths(sample_fn, label=1, n_paths=50, rng=rng, max_attempts=40000)

            np.savez(
                DATA_DIR / f"{prefix}_paths_v8.npz",
                paths_fast=np.array(paths_fast, dtype=object),
                paths_slow=np.array(paths_slow, dtype=object),
                rep_fast=rep_fast_path,
                rep_slow=rep_slow_path,
                t_fast=int(rep_fast[1]) if rep_fast else -1,
                t_slow=int(rep_slow[1]) if rep_slow else -1,
            )

            plot_paths_density_v8(
                case,
                paths=paths_fast,
                rep_path=rep_fast_path,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_fast.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
            )
            plot_paths_density_v8(
                case,
                paths=paths_slow,
                rep_path=rep_slow_path,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_slow.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
            )

            p_fast = float((labels == 0).mean()) if labels.size else 0.0
            p_slow = float((labels == 1).mean()) if labels.size else 0.0

            pmf_full, _ = hist_pmf(times, t_plot=t_max)
            if abs(float(pmf_full.sum()) - 1.0) > 5e-3:
                raise ValueError(f"{prefix} MC pmf sum check failed: {pmf_full.sum():.6f}")

            tail_start = max(int(tv + 30), 200)
            tail_bin_width = max(int(mc_bin_width) * 6, 12)
            tail_smooth_window = max(int(mc_smooth_window) * 4, int(mc_smooth_window) + 20)
            slow_mc_window = max(tail_smooth_window + 6, int(mc_smooth_window) * 6)

            t_centers, pmf_all = _mc_histogram(
                times,
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(times.size),
            )

            plot_fpt_multiscale_v8(
                t_exact=t_exact,
                f_exact=f_exact,
                t_aw=t_aw,
                f_aw=f_aw_arr,
                mc_centers=t_centers,
                mc_pmf=pmf_all,
                peaks=(t1, tv, t2),
                outpath=fig_subdirs["fpt"] / f"{prefix}_fpt.pdf",
                log_eps=log_eps,
                dpi=png_dpi,
                tail_zoom=(prefix == "candidate_C"),
            )

            _, pmf_fast = _mc_histogram(
                times[labels == 0],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 0)),
            )
            _, pmf_slow = _mc_histogram(
                times[labels == 1],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 1)),
            )

            plot_channel_decomp_v8(
                t=t_centers,
                f_fast=pmf_fast,
                f_slow=pmf_slow,
                p_fast=p_fast,
                p_slow=p_slow,
                outpath=fig_subdirs["channel_decomp"] / f"{prefix}_channel_decomp.pdf",
                dpi=png_dpi,
                tail_zoom=(prefix == "candidate_C"),
            )

            proof = None
            if prefix == "candidate_B":
                proof = plot_bimodality_proof_B(
                    t=t_exact,
                    f_exact=f_exact,
                    f_aw=f_aw_arr,
                    t_max_zoom=80,
                    smooth_w=peak_smooth_window,
                    min_sep=5,
                    outpath=fig_subdirs["fpt"] / "bimodality_proof_B.png",
                    log_eps=log_eps,
                    dpi=png_dpi,
                    detect=detect,
                )

            if case.boundary_x == "periodic":
                fig3v2.plot_periodic_unwrapped_two_tiles(
                    case,
                    outpath=fig_subdirs["unwrapped"] / f"{prefix}_unwrapped.pdf",
                    dpi=png_dpi,
                )

            return {
                "t1": int(t1),
                "tv": int(tv),
                "t2": int(t2),
                "h1": float(f_exact[t1 - 1]),
                "hv": float(f_exact[tv - 1]),
                "h2": float(f_exact[t2 - 1]),
                "h2_over_h1": float(f_exact[t2 - 1] / f_exact[t1 - 1]) if f_exact[t1 - 1] > 0 else 0.0,
                "hv_over_max": float(f_exact[tv - 1] / max(f_exact[t1 - 1], f_exact[t2 - 1])),
                "p_fast": p_fast,
                "p_slow": p_slow,
                "heatmap_times": [int(t) for t in heatmap_times],
                "bimodality_detect": detect,
                "bimodality_proof": proof,
            }

        v8_meta = {
            "candidate_A": plot_case_v8("candidate_A", case_A, cfg_A, spec_A, f_A, f_A_aw, times_A, labels_A),
            "candidate_B": plot_case_v8(
                "candidate_B", case_B, cfg_B, spec_B, f_B, f_B_aw, times_B, labels_B, corridor_band=corridor_band
            ),
            "candidate_C": plot_case_v8("candidate_C", case_C, cfg_C, spec_C, f_C, f_C_aw, times_C, labels_C),
        }

        def save_metrics_v8(prefix: str, spec: ConfigSpec, stats: dict, extra: dict) -> None:
            payload = {
                "config": config_to_dict(spec),
                "peaks": v8_meta[prefix],
                "mc": stats | {"tail_mass": extra["tail_mass"]},
                "aw": extra["aw"],
                "plot_params": {
                    "fig_version": fig_version,
                    "plot_style": plot_style,
                    "png_dpi": int(png_dpi),
                    "mc_bin_width": int(mc_bin_width),
                    "mc_smooth_window": int(mc_smooth_window),
                    "peak_smooth_window": int(peak_smooth_window),
                    "log_eps": float(log_eps),
                },
            }
            (DATA_DIR / f"{prefix}_metrics_v8.json").write_text(
                json.dumps(payload, indent=2), encoding="utf-8"
            )

        save_metrics_v8("candidate_A", spec_A, stats_A, extra_A)
        save_metrics_v8("candidate_B", spec_B, stats_B, extra_B)
        save_metrics_v8("candidate_C", spec_C, stats_C, extra_C)

        fig3v8.write_gallery_html(fig_dir)

    if fig_version == "v9":
        if fig_subdirs is None:
            raise RuntimeError("v9 figure directories not initialized.")

        fig3v9.apply_style_v9()
        fig3v2.plot_cartoon_channels(outpath=fig_subdirs["fig3_panels"] / "channel_cartoon.pdf", dpi=png_dpi)
        plot_symbol_legend_v9(outpath=fig_subdirs["env"] / "symbol_legend.pdf", dpi=png_dpi)

        def _sanity_check_fpt(f: np.ndarray, *, name: str) -> None:
            if np.any(f < -1e-15):
                raise ValueError(f"{name} has negative entries below tolerance.")
            mass = float(np.sum(f))
            if not (0.0 <= mass <= 1.0 + 1e-3):
                raise ValueError(f"{name} mass out of bounds (sum={mass:.6f}).")

        _sanity_check_fpt(f_A, name="f_exact_A")
        _sanity_check_fpt(f_B, name="f_exact_B")
        _sanity_check_fpt(f_C, name="f_exact_C")

        if f_A_aw is not None and np.min(f_A_aw) < -1e-12:
            raise ValueError("f_aw_A has negative entries beyond tolerance.")
        if f_B_aw is not None and np.min(f_B_aw) < -1e-12:
            raise ValueError("f_aw_B has negative entries beyond tolerance.")
        if f_C_aw is not None and np.min(f_C_aw) < -1e-12:
            raise ValueError("f_aw_C has negative entries beyond tolerance.")

        def plot_case_v9(
            prefix: str,
            case: CaseGeometry,
            cfg: LatticeConfig,
            spec: ConfigSpec,
            f_exact: np.ndarray,
            f_aw: np.ndarray | None,
            times: np.ndarray,
            labels: np.ndarray,
            *,
            corridor_band: set[tuple[int, int]] | None = None,
        ) -> dict:
            try:
                detect = fig3v9.detect_bimodality(
                    f_exact[:t_max_aw], smooth_w=peak_smooth_window, min_sep=5
                )
                t1, tv, t2 = int(detect["p1"]), int(detect["v"]), int(detect["p2"])
            except RuntimeError:
                t1, tv, t2 = _select_peak_times_v3(
                    f_exact,
                    t_max=t_max_aw,
                    smooth_window=peak_smooth_window,
                )
                detect = {
                    "p1": t1,
                    "v": tv,
                    "p2": t2,
                    "h1": float(f_exact[t1 - 1]),
                    "h2": float(f_exact[t2 - 1]),
                    "hv": float(f_exact[tv - 1]),
                    "ratio": float(f_exact[t2 - 1] / f_exact[t1 - 1]) if f_exact[t1 - 1] > 0 else np.nan,
                    "valley": float(f_exact[tv - 1] / max(f_exact[t1 - 1], f_exact[t2 - 1])),
                    "fallback": True,
                }
            heatmap_times = [t1, tv, t2]
            dist = distributions_at_times(cfg, heatmap_times, conditional=True)
            mats = [dist[t] for t in heatmap_times]
            np.savez(
                DATA_DIR / f"{prefix}_Pt_times_v9.npz",
                times=np.array(heatmap_times, dtype=np.int64),
                P=np.stack(mats, axis=0),
            )

            f_aw_arr = f_aw if f_aw is not None else np.array([])
            if prefix in aw_inputs:
                np.savez(
                    DATA_DIR / f"{prefix}_aw_input_v9.npz",
                    z=aw_inputs[prefix]["z"],
                    Ftilde=aw_inputs[prefix]["Fz"],
                )
                np.savez(
                    DATA_DIR / f"{prefix}_aw_output_v9.npz",
                    t=np.arange(1, t_max_aw + 1),
                    f_aw=f_aw_arr,
                )

            band_hw = 1
            if case.classification_rule and "band_halfwidth" in case.classification_rule:
                band_hw = int(case.classification_rule["band_halfwidth"])

            roi = fig3v9.roi_bounds_auto(case, margin=6)

            extra_text = None
            if case.corridor:
                y0 = int(case.corridor["y"])
                band_vals = [y0 - band_hw, y0, y0 + band_hw]
                L = abs(int(case.corridor["x_end"]) - int(case.corridor["x_start"])) + 1
                extra_text = f"corridor y={band_vals}\nL={L}, delta={case.local_bias_delta:.2f}"

            plot_environment_v9(
                case,
                outpath=fig_subdirs["env"] / f"{prefix}_env.pdf",
                dpi=png_dpi,
                roi=roi,
                bias_step_main=4 if prefix == prefix_B else 2,
                bias_step_zoom=1,
                corridor_halfwidth=band_hw,
                extra_text=extra_text,
            )

            plot_fig3_panel_v9(
                case,
                mats=mats,
                times=heatmap_times,
                outpath=fig_subdirs["fig3_panels"] / f"{prefix}_fig3_panel.pdf",
                dpi=png_dpi,
                bias_step_env=4 if prefix == prefix_B else 2,
                bias_step_heat=1,
                corridor_halfwidth=band_hw,
            )

            neighbors, cum_probs = build_mc_arrays(cfg)
            seed_offset = {"candidate_A": 901, prefix_B: 902, "candidate_C": 903}.get(prefix, 900)
            rng = np.random.default_rng(seed + seed_offset)

            median_fast = _median_time(times, labels, 0) or 1
            median_slow = _median_time(times, labels, 1) or 1

            if prefix == "candidate_A":

                def sample_fn(rng_local):
                    return sample_path_candidate_A(
                        cfg, max_steps=t_max, rng=rng_local, neighbors=neighbors, cum_probs=cum_probs
                    )

            elif prefix == prefix_B:
                corridor_set = corridor_set_from_spec(spec)

                def sample_fn(rng_local):
                    return sample_path_candidate_B(
                        cfg,
                        corridor_set,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                        corridor_band=corridor_band,
                    )

            else:
                door_edge = list(cfg.barriers_perm.keys())[0]

                def sample_fn(rng_local):
                    return sample_path_candidate_C(
                        cfg,
                        door_edge,
                        t_valley=tv,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )

            rep_fast = _pick_representative_path(
                sample_fn, label=0, target_time=median_fast, rng=rng, max_attempts=12000
            )
            rep_slow = _pick_representative_path(
                sample_fn, label=1, target_time=median_slow, rng=rng, max_attempts=12000
            )
            rep_fast_path = _to_one_based(rep_fast[0]) if rep_fast else np.empty((0, 2), dtype=np.int64)
            rep_slow_path = _to_one_based(rep_slow[0]) if rep_slow else np.empty((0, 2), dtype=np.int64)

            paths_fast = _collect_paths(sample_fn, label=0, n_paths=50, rng=rng, max_attempts=40000)
            paths_slow = _collect_paths(sample_fn, label=1, n_paths=50, rng=rng, max_attempts=40000)

            np.savez(
                DATA_DIR / f"{prefix}_paths_v9.npz",
                paths_fast=np.array(paths_fast, dtype=object),
                paths_slow=np.array(paths_slow, dtype=object),
                rep_fast=rep_fast_path,
                rep_slow=rep_slow_path,
                t_fast=int(rep_fast[1]) if rep_fast else -1,
                t_slow=int(rep_slow[1]) if rep_slow else -1,
            )

            plot_paths_density_v9(
                case,
                paths=paths_fast,
                rep_path=rep_fast_path,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_fast.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
            )
            plot_paths_density_v9(
                case,
                paths=paths_slow,
                rep_path=rep_slow_path,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_slow.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
            )

            p_fast = float((labels == 0).mean()) if labels.size else 0.0
            p_slow = float((labels == 1).mean()) if labels.size else 0.0

            pmf_full, _ = hist_pmf(times, t_plot=t_max)
            if abs(float(pmf_full.sum()) - 1.0) > 5e-3:
                raise ValueError(f"{prefix} MC pmf sum check failed: {pmf_full.sum():.6f}")

            tail_start = max(int(tv + 30), 200)
            tail_bin_width = max(int(mc_bin_width) * 6, 12)
            tail_smooth_window = max(int(mc_smooth_window) * 4, int(mc_smooth_window) + 20)
            slow_mc_window = max(tail_smooth_window + 6, int(mc_smooth_window) * 6)

            t_centers, pmf_all = _mc_histogram(
                times,
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(times.size),
            )

            plot_fpt_multiscale_v9(
                t_exact=t_exact,
                f_exact=f_exact,
                t_aw=t_aw,
                f_aw=f_aw_arr,
                mc_centers=t_centers,
                mc_pmf=pmf_all,
                peaks=(t1, tv, t2),
                outpath=fig_subdirs["fpt"] / f"{prefix}_fpt.pdf",
                log_eps=log_eps,
                dpi=png_dpi,
                tail_zoom=(prefix == "candidate_C"),
                early_inset=(prefix == prefix_B),
            )

            _, pmf_fast = _mc_histogram(
                times[labels == 0],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 0)),
            )
            _, pmf_slow = _mc_histogram(
                times[labels == 1],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 1)),
            )

            plot_channel_decomp_v9(
                t=t_centers,
                f_fast=pmf_fast,
                f_slow=pmf_slow,
                p_fast=p_fast,
                p_slow=p_slow,
                outpath=fig_subdirs["channel_decomp"] / f"{prefix}_channel_decomp.pdf",
                dpi=png_dpi,
                tail_zoom=(prefix == "candidate_C"),
            )

            proof = None
            if prefix == prefix_B:
                proof = plot_bimodality_proof_B_v9(
                    t=t_exact,
                    f_exact=f_exact,
                    f_aw=f_aw_arr,
                    t_max_zoom=120,
                    smooth_w=peak_smooth_window,
                    min_sep=5,
                    outpath=fig_subdirs["fpt"] / "bimodality_proof_B_v2.png",
                    log_eps=log_eps,
                    dpi=png_dpi,
                    detect=detect,
                )

            if case.boundary_x == "periodic":
                fig3v2.plot_periodic_unwrapped_two_tiles(
                    case,
                    outpath=fig_subdirs["unwrapped"] / f"{prefix}_unwrapped.pdf",
                    dpi=png_dpi,
                )

            return {
                "t1": int(t1),
                "tv": int(tv),
                "t2": int(t2),
                "h1": float(f_exact[t1 - 1]),
                "hv": float(f_exact[tv - 1]),
                "h2": float(f_exact[t2 - 1]),
                "h2_over_h1": float(f_exact[t2 - 1] / f_exact[t1 - 1]) if f_exact[t1 - 1] > 0 else 0.0,
                "hv_over_max": float(f_exact[tv - 1] / max(f_exact[t1 - 1], f_exact[t2 - 1])),
                "p_fast": p_fast,
                "p_slow": p_slow,
                "heatmap_times": [int(t) for t in heatmap_times],
                "bimodality_detect": detect,
                "bimodality_proof": proof,
            }

        v9_meta = {
            "candidate_A": plot_case_v9("candidate_A", case_A, cfg_A, spec_A, f_A, f_A_aw, times_A, labels_A),
            prefix_B: plot_case_v9(
                prefix_B, case_B_main, cfg_B, spec_B, f_B, f_B_aw, times_B, labels_B, corridor_band=corridor_band
            ),
            "candidate_C": plot_case_v9("candidate_C", case_C, cfg_C, spec_C, f_C, f_C_aw, times_C, labels_C),
        }

        def save_metrics_v9(prefix: str, spec: ConfigSpec, stats: dict, extra: dict) -> None:
            payload = {
                "config": config_to_dict(spec),
                "peaks": v9_meta[prefix],
                "mc": stats | {"tail_mass": extra["tail_mass"]},
                "aw": extra["aw"],
                "plot_params": {
                    "fig_version": fig_version,
                    "plot_style": plot_style,
                    "png_dpi": int(png_dpi),
                    "mc_bin_width": int(mc_bin_width),
                    "mc_smooth_window": int(mc_smooth_window),
                    "peak_smooth_window": int(peak_smooth_window),
                    "log_eps": float(log_eps),
                },
            }
            if prefix == prefix_B and tune_report is not None:
                payload["tuning"] = tune_report.get("best", {})
            (DATA_DIR / f"{prefix}_metrics_v9.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

        save_metrics_v9("candidate_A", spec_A, stats_A, extra_A)
        save_metrics_v9(prefix_B, spec_B, stats_B, extra_B)
        save_metrics_v9("candidate_C", spec_C, stats_C, extra_C)

        fig3v9.write_gallery_html(fig_dir)

    if fig_version == "v10":
        if fig_subdirs is None:
            raise RuntimeError("v10 figure directories not initialized.")

        fig3v10.apply_style_v10()
        fig3v2.plot_cartoon_channels(outpath=fig_subdirs["fig3_panels"] / "channel_cartoon.pdf", dpi=png_dpi)
        plot_symbol_legend_v10(outpath=fig_subdirs["env"] / "symbol_legend.pdf", dpi=png_dpi)

        def _sanity_check_fpt(f: np.ndarray, *, name: str) -> None:
            if np.any(f < -1e-15):
                raise ValueError(f"{name} has negative entries below tolerance.")
            mass = float(np.sum(f))
            if not (0.0 <= mass <= 1.0 + 1e-3):
                raise ValueError(f"{name} mass out of bounds (sum={mass:.6f}).")

        _sanity_check_fpt(f_A, name="f_exact_A")
        _sanity_check_fpt(f_B, name="f_exact_B")
        _sanity_check_fpt(f_C, name="f_exact_C")

        if f_A_aw is not None and np.min(f_A_aw) < -1e-12:
            raise ValueError("f_aw_A has negative entries beyond tolerance.")
        if f_B_aw is not None and np.min(f_B_aw) < -1e-12:
            raise ValueError("f_aw_B has negative entries beyond tolerance.")
        if f_C_aw is not None and np.min(f_C_aw) < -1e-12:
            raise ValueError("f_aw_C has negative entries beyond tolerance.")

        def _update_cases_file(case_path: Path, case_id: str, tuned_case: CaseGeometry) -> None:
            data = json.loads(case_path.read_text(encoding="utf-8"))
            updated = False
            for entry in data.get("cases", []):
                if str(entry.get("id")) != case_id:
                    continue
                entry["boundary"]["x"] = tuned_case.boundary_x
                entry["boundary"]["y"] = tuned_case.boundary_y
                entry["global_bias"]["gx"] = float(tuned_case.g_x)
                entry["global_bias"]["gy"] = float(tuned_case.g_y)
                entry["start"] = [int(tuned_case.start[0]), int(tuned_case.start[1])]
                entry["target"] = [int(tuned_case.target[0]), int(tuned_case.target[1])]
                entry["local_bias"] = list(tuned_case.local_bias)
                if tuned_case.corridor is not None:
                    entry["corridor"] = dict(tuned_case.corridor)
                if tuned_case.classification_rule is not None:
                    entry["classification_rule"] = dict(tuned_case.classification_rule)
                updated = True
                break
            if updated:
                case_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        if tune_B and prefix_B == "candidate_B_v10" and cases_json and not quick:
            case_path = Path(cases_json)
            if case_path.exists():
                _update_cases_file(case_path, "B_v10", case_B_main)

        def plot_case_v10(
            prefix: str,
            case: CaseGeometry,
            cfg: LatticeConfig,
            spec: ConfigSpec,
            f_exact: np.ndarray,
            f_aw: np.ndarray | None,
            times: np.ndarray,
            labels: np.ndarray,
            *,
            corridor_band: set[tuple[int, int]] | None = None,
        ) -> dict:
            metrics = fig3v10.compute_bimodality_metrics(
                f_exact[:t_max_aw],
                smooth_w=peak_smooth_window,
                min_sep=5,
                min_gap=20,
            )
            t1, tv, t2 = int(metrics["t_p1"]), int(metrics["t_v"]), int(metrics["t_p2"])
            heatmap_times = [t1, tv, t2]
            dist = distributions_at_times(cfg, heatmap_times, conditional=True)
            mats = [dist[t] for t in heatmap_times]
            np.savez(
                DATA_DIR / f"{prefix}_Pt_times_v10.npz",
                times=np.array(heatmap_times, dtype=np.int64),
                P=np.stack(mats, axis=0),
            )

            f_aw_arr = f_aw if f_aw is not None else np.array([])
            if prefix in aw_inputs:
                np.savez(
                    DATA_DIR / f"{prefix}_aw_input_v10.npz",
                    z=aw_inputs[prefix]["z"],
                    Ftilde=aw_inputs[prefix]["Fz"],
                )
                np.savez(
                    DATA_DIR / f"{prefix}_aw_output_v10.npz",
                    t=np.arange(1, t_max_aw + 1),
                    f_aw=f_aw_arr,
                )

            band_hw = 1
            if case.classification_rule and "band_halfwidth" in case.classification_rule:
                band_hw = int(case.classification_rule["band_halfwidth"])

            roi = fig3v10.roi_bounds_auto(case, margin=6)
            strip_view = None
            extra_text = None
            if case.corridor:
                y0 = int(case.corridor["y"])
                band_vals = [y0 - band_hw, y0, y0 + band_hw]
                L = abs(int(case.corridor["x_end"]) - int(case.corridor["x_start"])) + 1
                extra_text = f"corridor y={band_vals}\nL={L}, delta={case.local_bias_delta:.2f}"
                x0 = int(case.corridor["x_start"])
                x1 = int(case.corridor["x_end"])
                strip_view = fig3v10.ViewBox(
                    max(1, x0 - 6),
                    min(case.N, x1 + 6),
                    max(1, y0 - (band_hw + 2)),
                    min(case.N, y0 + band_hw + 2),
                )

            if prefix == prefix_B:
                plot_candidate_B_env_v10(
                    case,
                    outpath=fig_subdirs["env"] / f"{prefix}_env.pdf",
                    dpi=png_dpi,
                    corridor_halfwidth=band_hw,
                )
            else:
                plot_environment_v10(
                    case,
                    outpath=fig_subdirs["env"] / f"{prefix}_env.pdf",
                    dpi=png_dpi,
                    roi=roi,
                    bias_step_main=3,
                    bias_step_zoom=1,
                    corridor_halfwidth=band_hw,
                    extra_text=extra_text,
                    strip_main=False,
                )

            plot_fig3_panel_v10(
                case,
                mats=mats,
                times=heatmap_times,
                outpath=fig_subdirs["fig3_panels"] / f"{prefix}_fig3_panel.pdf",
                dpi=png_dpi,
                bias_step_env=4 if prefix == prefix_B else 2,
                bias_step_heat=1,
                corridor_halfwidth=band_hw,
                env_strip=(prefix == prefix_B),
                strip_view=strip_view if prefix == prefix_B else None,
            )

            neighbors, cum_probs = build_mc_arrays(cfg)
            seed_offset = {"candidate_A": 1001, prefix_B: 1002, "candidate_C": 1003}.get(prefix, 1000)
            rng = np.random.default_rng(seed + seed_offset)

            median_fast = _median_time(times, labels, 0) or 1
            median_slow = _median_time(times, labels, 1) or 1

            if prefix == "candidate_A":

                def sample_fn(rng_local):
                    return sample_path_candidate_A(
                        cfg, max_steps=t_max, rng=rng_local, neighbors=neighbors, cum_probs=cum_probs
                    )

            elif prefix == prefix_B:
                corridor_set = corridor_set_from_spec(spec)

                def sample_fn(rng_local):
                    return sample_path_candidate_B(
                        cfg,
                        corridor_set,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                        corridor_band=corridor_band,
                    )

            else:
                door_edge = list(cfg.barriers_perm.keys())[0]

                def sample_fn(rng_local):
                    return sample_path_candidate_C(
                        cfg,
                        door_edge,
                        t_valley=tv,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )

            rep_fast = _pick_representative_path(
                sample_fn, label=0, target_time=median_fast, rng=rng, max_attempts=12000
            )
            rep_slow = _pick_representative_path(
                sample_fn, label=1, target_time=median_slow, rng=rng, max_attempts=12000
            )
            rep_fast_path = _to_one_based(rep_fast[0]) if rep_fast else np.empty((0, 2), dtype=np.int64)
            rep_slow_path = _to_one_based(rep_slow[0]) if rep_slow else np.empty((0, 2), dtype=np.int64)

            paths_fast = _collect_paths(sample_fn, label=0, n_paths=30, rng=rng, max_attempts=30000)
            paths_slow = _collect_paths(sample_fn, label=1, n_paths=30, rng=rng, max_attempts=30000)

            np.savez(
                DATA_DIR / f"{prefix}_paths_v10.npz",
                paths_fast=np.array(paths_fast, dtype=object),
                paths_slow=np.array(paths_slow, dtype=object),
                rep_fast=rep_fast_path,
                rep_slow=rep_slow_path,
                t_fast=int(rep_fast[1]) if rep_fast else -1,
                t_slow=int(rep_slow[1]) if rep_slow else -1,
            )

            plot_paths_density_v10(
                case,
                paths=paths_fast,
                rep_path=rep_fast_path,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_fast.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
                roi=roi,
            )
            plot_paths_density_v10(
                case,
                paths=paths_slow,
                rep_path=rep_slow_path,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_slow.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
                roi=roi,
            )

            p_fast = float((labels == 0).mean()) if labels.size else 0.0
            p_slow = float((labels == 1).mean()) if labels.size else 0.0

            pmf_full, _ = hist_pmf(times, t_plot=t_max)
            if abs(float(pmf_full.sum()) - 1.0) > 5e-3:
                raise ValueError(f"{prefix} MC pmf sum check failed: {pmf_full.sum():.6f}")

            tail_start = max(int(tv + 30), 200)
            tail_bin_width = max(int(mc_bin_width) * 6, 12)
            tail_smooth_window = max(int(mc_smooth_window) * 4, int(mc_smooth_window) + 20)
            slow_mc_window = max(tail_smooth_window + 6, int(mc_smooth_window) * 6)

            t_centers, pmf_all = _mc_histogram(
                times,
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(times.size),
            )

            plot_fpt_multiscale_v10(
                t_exact=t_exact,
                f_exact=f_exact,
                t_aw=t_aw,
                f_aw=f_aw_arr,
                mc_centers=t_centers,
                mc_pmf=pmf_all,
                peaks=(t1, tv, t2),
                outpath=fig_subdirs["fpt"] / f"{prefix}_fpt.pdf",
                log_eps=log_eps,
                dpi=png_dpi,
                tail_zoom=(prefix == "candidate_C"),
                early_inset=(prefix == prefix_B),
            )

            _, pmf_fast = _mc_histogram(
                times[labels == 0],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 0)),
            )
            _, pmf_slow = _mc_histogram(
                times[labels == 1],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 1)),
            )

            plot_channel_decomp_v10(
                t=t_centers,
                f_fast=pmf_fast,
                f_slow=pmf_slow,
                p_fast=p_fast,
                p_slow=p_slow,
                outpath=fig_subdirs["channel_decomp"] / f"{prefix}_channel_decomp.pdf",
                dpi=png_dpi,
                tail_zoom=(prefix == "candidate_C"),
            )

            proof = None
            if prefix == prefix_B:
                t_zoom = int(min(t_max_aw, max(200, t2 + 20)))
                proof = plot_bimodality_proof_B_v10(
                    t=t_exact,
                    f_exact=f_exact,
                    f_aw=f_aw_arr,
                    metrics=metrics,
                    t_max_zoom=t_zoom,
                    outpath=fig_subdirs["fpt"] / "bimodality_proof_B_v10.png",
                    log_eps=log_eps,
                    dpi=png_dpi,
                )

            if case.boundary_x == "periodic":
                fig3v2.plot_periodic_unwrapped_two_tiles(
                    case,
                    outpath=fig_subdirs["unwrapped"] / f"{prefix}_unwrapped.pdf",
                    dpi=png_dpi,
                )

            return {
                **metrics,
                "p_fast": p_fast,
                "p_slow": p_slow,
                "heatmap_times": [int(t) for t in heatmap_times],
                "bimodality_proof": proof,
            }

        v10_meta = {
            "candidate_A": plot_case_v10("candidate_A", case_A, cfg_A, spec_A, f_A, f_A_aw, times_A, labels_A),
            prefix_B: plot_case_v10(
                prefix_B,
                case_B_main,
                cfg_B,
                spec_B,
                f_B,
                f_B_aw,
                times_B,
                labels_B,
                corridor_band=corridor_band,
            ),
            "candidate_C": plot_case_v10("candidate_C", case_C, cfg_C, spec_C, f_C, f_C_aw, times_C, labels_C),
        }

        def save_metrics_v10(prefix: str, spec: ConfigSpec, stats: dict, extra: dict) -> None:
            payload = {
                "config": config_to_dict(spec),
                "peaks": v10_meta[prefix],
                "mc": stats | {"tail_mass": extra["tail_mass"]},
                "aw": extra["aw"],
                "plot_params": {
                    "fig_version": fig_version,
                    "plot_style": plot_style,
                    "png_dpi": int(png_dpi),
                    "mc_bin_width": int(mc_bin_width),
                    "mc_smooth_window": int(mc_smooth_window),
                    "peak_smooth_window": int(peak_smooth_window),
                    "log_eps": float(log_eps),
                },
            }
            if prefix == prefix_B and tune_report is not None:
                payload["tuning"] = tune_report.get("best", {})
            (DATA_DIR / f"{prefix}_metrics_v10.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

        save_metrics_v10("candidate_A", spec_A, stats_A, extra_A)
        save_metrics_v10(prefix_B, spec_B, stats_B, extra_B)
        save_metrics_v10("candidate_C", spec_C, stats_C, extra_C)

        fig3v10.write_gallery_html(fig_dir)

    if fig_version == "v11":
        if fig_subdirs is None:
            raise RuntimeError("v11 figure directories not initialized.")

        fig3v11.apply_style_v11()
        fig3v2.plot_cartoon_channels(outpath=fig_subdirs["fig3_panels"] / "channel_cartoon.pdf", dpi=png_dpi)
        plot_symbol_legend_v11(outpath=fig_subdirs["env"] / "symbol_legend.pdf", dpi=png_dpi)

        def _sanity_check_fpt(f: np.ndarray, *, name: str) -> None:
            if np.any(f < -1e-15):
                raise ValueError(f"{name} has negative entries below tolerance.")
            mass = float(np.sum(f))
            if not (0.0 <= mass <= 1.0 + 1e-3):
                raise ValueError(f"{name} mass out of bounds (sum={mass:.6f}).")

        _sanity_check_fpt(f_A, name="f_exact_A")
        _sanity_check_fpt(f_B, name="f_exact_B")
        _sanity_check_fpt(f_C, name="f_exact_C")

        if f_A_aw is not None and np.min(f_A_aw) < -1e-12:
            raise ValueError("f_aw_A has negative entries beyond tolerance.")
        if f_B_aw is not None and np.min(f_B_aw) < -1e-12:
            raise ValueError("f_aw_B has negative entries beyond tolerance.")
        if f_C_aw is not None and np.min(f_C_aw) < -1e-12:
            raise ValueError("f_aw_C has negative entries beyond tolerance.")

        def _update_cases_file(case_path: Path, case_id: str, tuned_case: CaseGeometry) -> None:
            data = json.loads(case_path.read_text(encoding="utf-8"))
            updated = False
            for entry in data.get("cases", []):
                if str(entry.get("id")) != case_id:
                    continue
                entry["boundary"]["x"] = tuned_case.boundary_x
                entry["boundary"]["y"] = tuned_case.boundary_y
                entry["global_bias"]["gx"] = float(tuned_case.g_x)
                entry["global_bias"]["gy"] = float(tuned_case.g_y)
                entry["start"] = [int(tuned_case.start[0]), int(tuned_case.start[1])]
                entry["target"] = [int(tuned_case.target[0]), int(tuned_case.target[1])]
                entry["local_bias"] = list(tuned_case.local_bias)
                if tuned_case.corridor is not None:
                    entry["corridor"] = dict(tuned_case.corridor)
                if tuned_case.classification_rule is not None:
                    entry["classification_rule"] = dict(tuned_case.classification_rule)
                updated = True
                break
            if updated:
                case_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        if tune_B and prefix_B == "candidate_B_v11" and cases_json and not quick:
            case_path = Path(cases_json)
            if case_path.exists():
                _update_cases_file(case_path, "B_v11", case_B_main)

        def plot_case_v11(
            prefix: str,
            case: CaseGeometry,
            cfg: LatticeConfig,
            spec: ConfigSpec,
            f_exact: np.ndarray,
            f_aw: np.ndarray | None,
            times: np.ndarray,
            labels: np.ndarray,
            *,
            corridor_band: set[tuple[int, int]] | None = None,
            corridor_rows: Sequence[int] | None = None,
        ) -> dict:
            metrics = fig3v11.compute_bimodality_metrics(
                f_exact[:t_max_aw],
                smooth_w=peak_smooth_window,
                min_sep=5,
                min_gap=20,
            )
            t1, tv, t2 = int(metrics["t_p1"]), int(metrics["t_v"]), int(metrics["t_p2"])
            heatmap_times = [t1, tv, t2]
            dist = distributions_at_times(cfg, heatmap_times, conditional=True)
            mats = [dist[t] for t in heatmap_times]
            np.savez(
                DATA_DIR / f"{prefix}_Pt_times_v11.npz",
                times=np.array(heatmap_times, dtype=np.int64),
                P=np.stack(mats, axis=0),
            )

            f_aw_arr = f_aw if f_aw is not None else np.array([])
            if prefix in aw_inputs:
                np.savez(
                    DATA_DIR / f"{prefix}_aw_input_v11.npz",
                    z=aw_inputs[prefix]["z"],
                    Ftilde=aw_inputs[prefix]["Fz"],
                )
                np.savez(
                    DATA_DIR / f"{prefix}_aw_output_v11.npz",
                    t=np.arange(1, t_max_aw + 1),
                    f_aw=f_aw_arr,
                )

            band_hw = 1
            if case.classification_rule and "band_halfwidth" in case.classification_rule:
                band_hw = int(case.classification_rule["band_halfwidth"])

            roi = fig3v11.roi_bounds_auto(case, margin=6)
            extra_text = None
            strip_view = None
            if case.corridor and corridor_rows:
                label = fig3v11.format_corridor_band_label(corridor_rows)
                L = abs(int(case.corridor["x_end"]) - int(case.corridor["x_start"])) + 1
                extra_text = f"{label}\nL={L}, delta={case.local_bias_delta:.2f}"
                x0 = int(case.corridor["x_start"])
                x1 = int(case.corridor["x_end"])
                y_min = min(corridor_rows)
                y_max = max(corridor_rows)
                strip_view = fig3v11.ViewBox(
                    max(1, x0 - 6),
                    min(case.N, x1 + 6),
                    max(1, y_min - 2),
                    min(case.N, y_max + 2),
                )

            if prefix == prefix_B:
                plot_candidate_B_env_v11(
                    case,
                    corridor_rows=corridor_rows or [],
                    outpath=fig_subdirs["env"] / f"{prefix}_env.pdf",
                    dpi=png_dpi,
                    corridor_halfwidth=band_hw,
                )
            else:
                plot_environment_v11(
                    case,
                    outpath=fig_subdirs["env"] / f"{prefix}_env.pdf",
                    dpi=png_dpi,
                    roi=roi,
                    bias_step_main=3,
                    bias_step_zoom=1,
                    corridor_halfwidth=band_hw,
                    corridor_rows=corridor_rows,
                    extra_text=extra_text,
                    strip_main=False,
                )

            plot_fig3_panel_v11(
                case,
                mats=mats,
                times=heatmap_times,
                outpath=fig_subdirs["fig3_panels"] / f"{prefix}_fig3_panel.pdf",
                dpi=png_dpi,
                bias_step_env=4 if prefix == prefix_B else 2,
                bias_step_heat=1,
                corridor_halfwidth=band_hw,
                corridor_rows=corridor_rows,
                env_strip=(prefix == prefix_B),
                strip_view=strip_view if prefix == prefix_B else None,
            )

            neighbors, cum_probs = build_mc_arrays(cfg)
            seed_offset = {"candidate_A": 1101, prefix_B: 1102, "candidate_C": 1103}.get(prefix, 1100)
            rng = np.random.default_rng(seed + seed_offset)

            median_fast = _median_time(times, labels, 0) or 1
            median_slow = _median_time(times, labels, 1) or 1

            if prefix == "candidate_A":

                def sample_fn(rng_local):
                    return sample_path_candidate_A(
                        cfg, max_steps=t_max, rng=rng_local, neighbors=neighbors, cum_probs=cum_probs
                    )

            elif prefix == prefix_B:
                corridor_set = corridor_set_from_spec(spec)

                def sample_fn(rng_local):
                    return sample_path_candidate_B(
                        cfg,
                        corridor_set,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                        corridor_band=corridor_band,
                    )

            else:
                door_edge = list(cfg.barriers_perm.keys())[0]

                def sample_fn(rng_local):
                    return sample_path_candidate_C(
                        cfg,
                        door_edge,
                        t_valley=tv,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )

            rep_fast = _pick_representative_path(
                sample_fn, label=0, target_time=median_fast, rng=rng, max_attempts=12000
            )
            rep_slow = _pick_representative_path(
                sample_fn, label=1, target_time=median_slow, rng=rng, max_attempts=12000
            )
            rep_slowest = _pick_representative_path(
                sample_fn, label=1, target_time=int(min(t_max, max(median_slow + 100, median_slow))), rng=rng, max_attempts=12000
            )
            rep_fast_path = _to_one_based(rep_fast[0]) if rep_fast else np.empty((0, 2), dtype=np.int64)
            rep_slow_path = _to_one_based(rep_slow[0]) if rep_slow else np.empty((0, 2), dtype=np.int64)
            rep_slowest_path = _to_one_based(rep_slowest[0]) if rep_slowest else np.empty((0, 2), dtype=np.int64)

            paths_fast_density = _collect_paths(sample_fn, label=0, n_paths=200, rng=rng, max_attempts=60000)
            paths_slow_density = _collect_paths(sample_fn, label=1, n_paths=200, rng=rng, max_attempts=60000)

            np.savez(
                DATA_DIR / f"{prefix}_paths_v11.npz",
                paths_fast=np.array(paths_fast_density, dtype=object),
                paths_slow=np.array(paths_slow_density, dtype=object),
                rep_fast=rep_fast_path,
                rep_slow=rep_slow_path,
                rep_slowest=rep_slowest_path,
                t_fast=int(rep_fast[1]) if rep_fast else -1,
                t_slow=int(rep_slow[1]) if rep_slow else -1,
            )

            plot_paths_density_v11(
                case,
                paths_density=paths_fast_density,
                rep_paths=[rep_fast_path],
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_fast.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
                roi=roi,
            )
            plot_paths_density_v11(
                case,
                paths_density=paths_slow_density,
                rep_paths=[rep_slow_path, rep_slowest_path],
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_slow.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
                roi=roi,
            )

            p_fast = float((labels == 0).mean()) if labels.size else 0.0
            p_slow = float((labels == 1).mean()) if labels.size else 0.0

            pmf_full, _ = hist_pmf(times, t_plot=t_max)
            if abs(float(pmf_full.sum()) - 1.0) > 5e-3:
                raise ValueError(f"{prefix} MC pmf sum check failed: {pmf_full.sum():.6f}")

            t_centers, pmf_all = _mc_histogram(
                times,
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                censor=True,
                n_total=int(times.size),
            )

            plot_fpt_multiscale_v11(
                t_exact=t_exact,
                f_exact=f_exact,
                t_aw=t_aw,
                f_aw=f_aw_arr,
                mc_centers=t_centers,
                mc_pmf=pmf_all,
                peaks=(t1, tv, t2),
                outpath=fig_subdirs["fpt"] / f"{prefix}_fpt.pdf",
                log_eps=log_eps,
                dpi=png_dpi,
            )

            _, pmf_fast = _mc_histogram(
                times[labels == 0],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 0)),
            )
            _, pmf_slow = _mc_histogram(
                times[labels == 1],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 1)),
            )

            plot_channel_decomp_v11(
                t=t_centers,
                f_fast=pmf_fast,
                f_slow=pmf_slow,
                p_fast=p_fast,
                p_slow=p_slow,
                outpath=fig_subdirs["channel_decomp"] / f"{prefix}_channel_decomp.pdf",
                dpi=png_dpi,
                tail_zoom=(prefix == "candidate_C"),
            )

            proof = None
            diagnostic = None
            if prefix == prefix_B:
                t_zoom = int(min(t_max_aw, max(200, t2 + 60)))
                proof = plot_bimodality_proof_B_v11(
                    t=t_exact,
                    f_exact=f_exact,
                    f_aw=f_aw_arr,
                    metrics=metrics,
                    t_max_zoom=t_zoom,
                    outpath=fig_subdirs["fpt"] / "bimodality_proof_B_v11.png",
                    log_eps=log_eps,
                    dpi=png_dpi,
                )
                diagnostic = plot_bimodality_diagnostic_B_v11(
                    t=t_exact,
                    f_exact=f_exact,
                    smooth_window=peak_smooth_window,
                    outpath=fig_subdirs["fpt"] / "bimodality_diagnostic_B_v11.pdf",
                    prominence=max(1e-6, float(metrics["h1"]) * 0.1),
                    distance=max(5, int(0.4 * (t2 - t1))),
                    valley_ratio=float(metrics["valley_ratio"]),
                    min_gap=int(metrics["gap"]),
                    dpi=png_dpi,
                )

            if case.boundary_x == "periodic":
                fig3v2.plot_periodic_unwrapped_two_tiles(
                    case,
                    outpath=fig_subdirs["unwrapped"] / f"{prefix}_unwrapped.pdf",
                    dpi=png_dpi,
                )

            return {
                **metrics,
                "p_fast": p_fast,
                "p_slow": p_slow,
                "heatmap_times": [int(t) for t in heatmap_times],
                "bimodality_proof": proof,
                "bimodality_diagnostic": diagnostic,
            }

        v11_meta = {
            "candidate_A": plot_case_v11("candidate_A", case_A, cfg_A, spec_A, f_A, f_A_aw, times_A, labels_A),
            prefix_B: plot_case_v11(
                prefix_B,
                case_B_main,
                cfg_B,
                spec_B,
                f_B,
                f_B_aw,
                times_B,
                labels_B,
                corridor_band=corridor_band,
                corridor_rows=corridor_band_rows,
            ),
            "candidate_C": plot_case_v11("candidate_C", case_C, cfg_C, spec_C, f_C, f_C_aw, times_C, labels_C),
        }

        def _scan_B_v11(base_case: CaseGeometry) -> List[dict]:
            results: List[dict] = []
            length_grid = list(range(6, 15))
            for L in length_grid:
                try:
                    case_scan = _build_corridor_case(
                        base_case,
                        gx=base_case.g_x,
                        gy=base_case.g_y,
                        delta=base_case.local_bias_delta,
                        start_x=int(base_case.start[0]),
                        length=L,
                        boundary_x=base_case.boundary_x,
                    )
                except ValueError:
                    continue
                spec_scan = case_to_spec(case_scan)
                cfg_scan = spec_to_internal(spec_scan)
                f_scan, _ = exact_fpt(cfg_scan, t_max=min(t_max_scan, t_max_aw))
                try:
                    metrics_scan = fig3v11.compute_bimodality_metrics(
                        f_scan,
                        smooth_w=peak_smooth_window,
                        min_sep=5,
                        min_gap=20,
                    )
                except RuntimeError:
                    continue
                corridor_set = corridor_set_from_spec(spec_scan)
                rows = _corridor_band_rows_from_case(case_scan, default_halfwidth=1)
                band = _corridor_band_from_rows(
                    case_scan,
                    rows=rows,
                    x_span=(min(case_scan.start[0], case_scan.target[0]), max(case_scan.start[0], case_scan.target[0])),
                )
                band_0 = {(x - 1, y - 1) for x, y in band}
                times_scan, labels_scan, _ = mc_candidate_B(
                    cfg_scan,
                    corridor_set,
                    n_walkers=min(4000, mc_samples),
                    seed=seed + 500 + L,
                    max_steps=min(t_max_scan, t_max),
                    corridor_band=band_0,
                )
                p_fast = float((labels_scan == 0).mean()) if labels_scan.size else 0.0
                results.append(
                    {
                        "L": int(L),
                        "valley_ratio": float(metrics_scan["valley_ratio"]),
                        "peak_ratio": float(metrics_scan["peak_ratio"]),
                        "p_fast": float(p_fast),
                    }
                )
            return results

        if prefix_B == "candidate_B_v11":
            scan_results = _scan_B_v11(case_B_main)
            if outputs_dir is not None:
                (outputs_dir / "scan_B_v11.json").write_text(
                    json.dumps(scan_results, indent=2), encoding="utf-8"
                )
            if scan_results:
                fig3v11.apply_style_v11()
                xs = [row["L"] for row in scan_results]
                vals = [row["valley_ratio"] for row in scan_results]
                pfast = [row["p_fast"] for row in scan_results]
                fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4), constrained_layout=True)
                axes[0].plot(xs, vals, "o-", color="#6a3d9a")
                axes[0].set_xlabel("L")
                axes[0].set_ylabel("valley ratio")
                axes[1].plot(xs, pfast, "o-", color="#1f78b4")
                axes[1].set_xlabel("L")
                axes[1].set_ylabel("P_fast")
                fig3v11.save_clean(fig, fig_subdirs["channel_decomp"] / "candidate_B_v11_scan.pdf", dpi=png_dpi)

        def save_metrics_v11(prefix: str, spec: ConfigSpec, stats: dict, extra: dict) -> None:
            payload = {
                "config": config_to_dict(spec),
                "peaks": v11_meta[prefix],
                "mc": stats | {"tail_mass": extra["tail_mass"]},
                "aw": extra["aw"],
                "plot_params": {
                    "fig_version": fig_version,
                    "plot_style": plot_style,
                    "png_dpi": int(png_dpi),
                    "mc_bin_width": int(mc_bin_width),
                    "mc_smooth_window": int(mc_smooth_window),
                    "peak_smooth_window": int(peak_smooth_window),
                    "log_eps": float(log_eps),
                },
            }
            if prefix == prefix_B and tune_report is not None:
                payload["tuning"] = tune_report.get("best", {})
            (DATA_DIR / f"{prefix}_metrics_v11.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

        save_metrics_v11("candidate_A", spec_A, stats_A, extra_A)
        save_metrics_v11(prefix_B, spec_B, stats_B, extra_B)
        save_metrics_v11("candidate_C", spec_C, stats_C, extra_C)

        fig3v11.write_gallery_html(fig_dir)

    if fig_version in ("v12", "main"):
        if fig_subdirs is None:
            raise RuntimeError("main/v12 figure directories not initialized.")

        version_suffix = "" if fig_version == "main" else "_v12"
        fig3v12.apply_style_v12()
        fig3v2.plot_cartoon_channels(outpath=fig_subdirs["fig3_panels"] / "channel_cartoon.pdf", dpi=png_dpi)
        plot_symbol_legend_v12(outpath=fig_subdirs["env"] / "symbol_legend.pdf", dpi=png_dpi)

        def _sanity_check_fpt(f: np.ndarray, *, name: str) -> None:
            if np.any(f < -1e-15):
                raise ValueError(f"{name} has negative entries below tolerance.")
            mass = float(np.sum(f))
            if not (0.0 <= mass <= 1.0 + 1e-3):
                raise ValueError(f"{name} mass out of bounds (sum={mass:.6f}).")

        _sanity_check_fpt(f_A, name="f_exact_A")
        _sanity_check_fpt(f_B, name="f_exact_B")
        _sanity_check_fpt(f_C, name="f_exact_C")

        if f_A_aw is not None and np.min(f_A_aw) < -1e-12:
            raise ValueError("f_aw_A has negative entries beyond tolerance.")
        if f_B_aw is not None and np.min(f_B_aw) < -1e-12:
            raise ValueError("f_aw_B has negative entries beyond tolerance.")
        if f_C_aw is not None and np.min(f_C_aw) < -1e-12:
            raise ValueError("f_aw_C has negative entries beyond tolerance.")

        def _update_cases_file(case_path: Path, case_id: str, tuned_case: CaseGeometry) -> None:
            data = json.loads(case_path.read_text(encoding="utf-8"))
            updated = False
            for entry in data.get("cases", []):
                if str(entry.get("id")) != case_id:
                    continue
                entry["boundary"]["x"] = tuned_case.boundary_x
                entry["boundary"]["y"] = tuned_case.boundary_y
                entry["global_bias"]["gx"] = float(tuned_case.g_x)
                entry["global_bias"]["gy"] = float(tuned_case.g_y)
                entry["start"] = [int(tuned_case.start[0]), int(tuned_case.start[1])]
                entry["target"] = [int(tuned_case.target[0]), int(tuned_case.target[1])]
                entry["local_bias"] = list(tuned_case.local_bias)
                if tuned_case.corridor is not None:
                    entry["corridor"] = dict(tuned_case.corridor)
                if tuned_case.classification_rule is not None:
                    entry["classification_rule"] = dict(tuned_case.classification_rule)
                updated = True
                break
            if updated:
                case_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        if tune_B and fig_version in ("v12", "main") and case_B_id == "B" and cases_json and not quick:
            case_path = Path(cases_json)
            if case_path.exists():
                _update_cases_file(case_path, "B", case_B_main)

        def _pick_rep_paths(
            sample_fn,
            *,
            label: int,
            target_times: List[int],
            rng: np.random.Generator,
        ) -> List[np.ndarray]:
            reps: List[np.ndarray] = []
            for t_target in target_times:
                rep = _pick_representative_path(sample_fn, label=label, target_time=t_target, rng=rng, max_attempts=12000)
                if rep is None:
                    continue
                reps.append(rep[0])
            return reps

        def plot_case_v12(
            prefix: str,
            case: CaseGeometry,
            cfg: LatticeConfig,
            spec: ConfigSpec,
            f_exact: np.ndarray,
            f_aw: np.ndarray | None,
            times: np.ndarray,
            labels: np.ndarray,
            *,
            corridor_band: set[tuple[int, int]] | None = None,
            corridor_rows: Sequence[int] | None = None,
        ) -> dict:
            metrics = fig3v12.compute_bimodality_metrics(
                f_exact[:t_max_aw],
                smooth_w=peak_smooth_window,
                min_sep=5,
                min_gap=20,
            )
            t1, tv, t2 = int(metrics["t_p1"]), int(metrics["t_v"]), int(metrics["t_p2"])
            heatmap_times = [t1, tv, t2]
            dist = distributions_at_times(cfg, heatmap_times, conditional=True)
            mats = [dist[t] for t in heatmap_times]
            np.savez(
                DATA_DIR / f"{prefix}_Pt_times{version_suffix}.npz",
                times=np.array(heatmap_times, dtype=np.int64),
                P=np.stack(mats, axis=0),
            )

            f_aw_arr = f_aw if f_aw is not None else np.array([])
            if prefix in aw_inputs:
                np.savez(
                    DATA_DIR / f"{prefix}_aw_input{version_suffix}.npz",
                    z=aw_inputs[prefix]["z"],
                    Ftilde=aw_inputs[prefix]["Fz"],
                )
                np.savez(
                    DATA_DIR / f"{prefix}_aw_output{version_suffix}.npz",
                    t=np.arange(1, t_max_aw + 1),
                    f_aw=f_aw_arr,
                )

            band_hw = 1
            if case.classification_rule and "band_halfwidth" in case.classification_rule:
                band_hw = int(case.classification_rule["band_halfwidth"])

            if prefix == prefix_B and not corridor_rows and case.corridor:
                corridor_rows = _corridor_band_rows_from_case(case, default_halfwidth=band_hw)

            heat_view = None
            if prefix == prefix_B and corridor_rows:
                # B: emphasize the corridor strip; heatmaps use a banded view to avoid large blank areas.
                strip_view = fig3v12.roi_bounds_strip(
                    case,
                    corridor_rows=corridor_rows,
                    pad_x=1,
                    pad_y=0,
                    min_width=12,
                    min_height=3,
                )
                heat_view = fig3v12.strip_view_full_width(case, corridor_rows, pad_y=1)
                roi = fig3v12.roi_bounds_strip(
                    case,
                    corridor_rows=corridor_rows,
                    pad_x=1,
                    pad_y=1,
                    min_width=12,
                    min_height=4,
                )
            else:
                roi = fig3v12.roi_bounds_auto(case, margin=6)
                strip_view = None

            neighbors, cum_probs = build_mc_arrays(cfg)
            seed_offset = {"candidate_A": 1101, prefix_B: 1102, "candidate_C": 1103}.get(prefix, 1100)
            rng = np.random.default_rng(seed + seed_offset)

            if prefix == "candidate_A":

                def sample_fn(rng_local):
                    return sample_path_candidate_A(
                        cfg, max_steps=t_max, rng=rng_local, neighbors=neighbors, cum_probs=cum_probs
                    )

            elif prefix == prefix_B:
                corridor_set = corridor_set_from_spec(spec)

                def sample_fn(rng_local):
                    return sample_path_candidate_B(
                        cfg,
                        corridor_set,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                        corridor_band=corridor_band,
                    )

            else:
                door_edge = list(cfg.barriers_perm.keys())[0]

                def sample_fn(rng_local):
                    return sample_path_candidate_C(
                        cfg,
                        door_edge,
                        t_valley=tv,
                        max_steps=t_max,
                        rng=rng_local,
                        neighbors=neighbors,
                        cum_probs=cum_probs,
                    )

            fast_targets = [max(1, min(t_max, t1 + dt)) for dt in (0, 10, 20)]
            slow_targets = [max(1, min(t_max, t2 + dt)) for dt in (-20, 0, 20)]
            rep_fast_paths = _pick_rep_paths(sample_fn, label=0, target_times=fast_targets, rng=rng)
            rep_slow_paths = _pick_rep_paths(sample_fn, label=1, target_times=slow_targets, rng=rng)

            rep_fast = [ _to_one_based(p) for p in rep_fast_paths if p is not None ]
            rep_slow = [ _to_one_based(p) for p in rep_slow_paths if p is not None ]
            fast_main = rep_fast[0] if rep_fast else np.empty((0, 2), dtype=np.int64)
            slow_main = rep_slow[0] if rep_slow else np.empty((0, 2), dtype=np.int64)

            paths_fast_density = _collect_paths(sample_fn, label=0, n_paths=200, rng=rng, max_attempts=60000)
            paths_slow_density = _collect_paths(sample_fn, label=1, n_paths=200, rng=rng, max_attempts=60000)

            np.savez(
                DATA_DIR / f"{prefix}_paths{version_suffix}.npz",
                paths_fast=np.array(paths_fast_density, dtype=object),
                paths_slow=np.array(paths_slow_density, dtype=object),
                rep_fast=np.array(rep_fast, dtype=object),
                rep_slow=np.array(rep_slow, dtype=object),
            )

            if prefix == prefix_B:
                plot_candidate_B_env_v12(
                    case,
                    corridor_rows=corridor_rows or [],
                    outpath=fig_subdirs["env"] / f"{prefix}_env.pdf",
                    dpi=png_dpi,
                    corridor_halfwidth=band_hw,
                    strip_view=strip_view,
                    fast_path=fast_main,
                    slow_path=slow_main,
                )
            else:
                plot_environment_v12(
                    case,
                    outpath=fig_subdirs["env"] / f"{prefix}_env.pdf",
                    dpi=png_dpi,
                    corridor_halfwidth=band_hw,
                    corridor_rows=corridor_rows,
                    fast_path=fast_main,
                    slow_path=slow_main,
                )

            plot_fig3_panel_v12(
                case,
                mats=mats,
                times=heatmap_times,
                outpath=fig_subdirs["fig3_panels"] / f"{prefix}_fig3_panel.pdf",
                dpi=png_dpi,
                bias_step_env=4 if prefix == prefix_B else 2,
                bias_step_heat=4 if prefix == prefix_B else 1,
                corridor_halfwidth=band_hw,
                corridor_rows=corridor_rows,
                env_strip=(prefix == prefix_B),
                strip_view=strip_view if prefix == prefix_B else None,
                heat_view=heat_view if prefix == prefix_B else None,
                fast_path=fast_main,
                slow_path=slow_main,
            )

            plot_paths_density_v12(
                case,
                paths_density=paths_fast_density,
                rep_paths=rep_fast,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_fast.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
                roi=roi,
            )
            plot_paths_density_v12(
                case,
                paths_density=paths_slow_density,
                rep_paths=rep_slow,
                outpath=fig_subdirs["paths"] / f"{prefix}_paths_slow.pdf",
                dpi=png_dpi,
                corridor_halfwidth=band_hw,
                roi=roi,
            )

            p_fast = float((labels == 0).mean()) if labels.size else 0.0
            p_slow = float((labels == 1).mean()) if labels.size else 0.0

            pmf_full, _ = hist_pmf(times, t_plot=t_max)
            if abs(float(pmf_full.sum()) - 1.0) > 5e-3:
                raise ValueError(f"{prefix} MC pmf sum check failed: {pmf_full.sum():.6f}")

            tail_start = max(int(tv + 30), 200)
            tail_bin_width = max(int(mc_bin_width) * 6, 12)
            tail_smooth_window = max(int(mc_smooth_window) * 4, int(mc_smooth_window) + 20)
            slow_mc_window = max(tail_smooth_window + 6, int(mc_smooth_window) * 6)

            t_centers, pmf_all = _mc_histogram(
                times,
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(times.size),
            )

            plot_fpt_multiscale_v12(
                t_exact=t_exact,
                f_exact=f_exact,
                t_aw=t_aw,
                f_aw=f_aw_arr,
                mc_centers=t_centers,
                mc_pmf=pmf_all,
                peaks=(t1, tv, t2),
                outpath=fig_subdirs["fpt"] / f"{prefix}_fpt.pdf",
                log_eps=log_eps,
                dpi=png_dpi,
                auto_slow_ylim=(prefix == "candidate_C"),
                mc_smooth_window_slow=slow_mc_window,
            )

            _, pmf_fast = _mc_histogram(
                times[labels == 0],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 0)),
            )
            _, pmf_slow = _mc_histogram(
                times[labels == 1],
                t_max=t_max,
                bin_width=mc_bin_width,
                smooth_window=mc_smooth_window,
                tail_start=tail_start,
                tail_bin_width=tail_bin_width,
                tail_smooth_window=tail_smooth_window,
                censor=True,
                n_total=int(np.sum(labels == 1)),
            )

            plot_channel_decomp_v12(
                t=t_centers,
                f_fast=pmf_fast,
                f_slow=pmf_slow,
                p_fast=p_fast,
                p_slow=p_slow,
                outpath=fig_subdirs["channel_decomp"] / f"{prefix}_channel_decomp.pdf",
                dpi=png_dpi,
                tail_zoom=(prefix == "candidate_C"),
            )

            proof = None
            diagnostic = None
            if prefix == prefix_B:
                t_zoom = int(min(t_max_aw, max(200, t2 + 60)))
                proof = plot_bimodality_proof_B(
                    t=t_exact,
                    f_exact=f_exact,
                    f_aw=f_aw_arr,
                    metrics=metrics,
                    t_max_zoom=t_zoom,
                    outpath=fig_subdirs["fpt"] / "bimodality_proof_B.png",
                    log_eps=log_eps,
                    dpi=png_dpi,
                )
                diagnostic = plot_bimodality_diagnostic_v12(
                    t=t_exact,
                    f_exact=f_exact,
                    smooth_window=peak_smooth_window,
                    outpath=fig_subdirs["fpt"] / "bimodality_diagnostic_B.pdf",
                    prominence=max(1e-6, float(metrics["h1"]) * 0.1),
                    distance=max(5, int(0.4 * (t2 - t1))),
                    min_gap=int(metrics["gap"]),
                    dpi=png_dpi,
                )
            if prefix == "candidate_C":
                diagnostic = plot_bimodality_diagnostic_v12(
                    t=t_exact,
                    f_exact=f_exact,
                    smooth_window=peak_smooth_window,
                    outpath=fig_subdirs["fpt"] / "bimodality_diagnostic_C.pdf",
                    prominence=max(1e-6, float(metrics["h1"]) * 0.1),
                    distance=max(5, int(0.4 * (t2 - t1))),
                    min_gap=int(metrics["gap"]),
                    method="windowed",
                    early_window=(1, 200),
                    late_window=(200, 1200),
                    dpi=png_dpi,
                )

            if case.boundary_x == "periodic":
                fig3v2.plot_periodic_unwrapped_two_tiles(
                    case,
                    outpath=fig_subdirs["unwrapped"] / f"{prefix}_unwrapped.pdf",
                    dpi=png_dpi,
                )

            return {
                **metrics,
                "p_fast": p_fast,
                "p_slow": p_slow,
                "heatmap_times": [int(t) for t in heatmap_times],
                "bimodality_proof": proof,
                "bimodality_diagnostic": diagnostic,
            }

        v12_meta = {
            "candidate_A": plot_case_v12("candidate_A", case_A, cfg_A, spec_A, f_A, f_A_aw, times_A, labels_A),
            prefix_B: plot_case_v12(
                prefix_B,
                case_B_main,
                cfg_B,
                spec_B,
                f_B,
                f_B_aw,
                times_B,
                labels_B,
                corridor_band=corridor_band,
                corridor_rows=corridor_band_rows,
            ),
            "candidate_C": plot_case_v12("candidate_C", case_C, cfg_C, spec_C, f_C, f_C_aw, times_C, labels_C),
        }

        def _scan_B_v12(base_case: CaseGeometry) -> List[dict]:
            results: List[dict] = []
            length_grid = list(range(6, 15))
            for L in length_grid:
                try:
                    case_scan = _build_corridor_case(
                        base_case,
                        gx=base_case.g_x,
                        gy=base_case.g_y,
                        delta=base_case.local_bias_delta,
                        start_x=int(base_case.start[0]),
                        length=L,
                        boundary_x=base_case.boundary_x,
                    )
                except ValueError:
                    continue
                spec_scan = case_to_spec(case_scan)
                cfg_scan = spec_to_internal(spec_scan)
                f_scan, _ = exact_fpt(cfg_scan, t_max=min(t_max_scan, t_max_aw))
                try:
                    metrics_scan = fig3v12.compute_bimodality_metrics(
                        f_scan,
                        smooth_w=peak_smooth_window,
                        min_sep=5,
                        min_gap=20,
                    )
                except RuntimeError:
                    continue
                corridor_set = corridor_set_from_spec(spec_scan)
                rows = _corridor_band_rows_from_case(case_scan, default_halfwidth=1)
                band = _corridor_band_from_rows(
                    case_scan,
                    rows=rows,
                    x_span=(min(case_scan.start[0], case_scan.target[0]), max(case_scan.start[0], case_scan.target[0])),
                )
                band_0 = {(x - 1, y - 1) for x, y in band}
                times_scan, labels_scan, _ = mc_candidate_B(
                    cfg_scan,
                    corridor_set,
                    n_walkers=min(4000, mc_samples),
                    seed=seed + 500 + L,
                    max_steps=min(t_max_scan, t_max),
                    corridor_band=band_0,
                )
                p_fast = float((labels_scan == 0).mean()) if labels_scan.size else 0.0
                results.append(
                    {
                        "L": int(L),
                        "valley_ratio": float(metrics_scan["valley_ratio"]),
                        "peak_ratio": float(metrics_scan["peak_ratio"]),
                        "p_fast": float(p_fast),
                    }
                )
            return results

        if fig_version in ("v12", "main"):
            scan_results = _scan_B_v12(case_B_main)
            if outputs_dir is not None:
                (outputs_dir / "scan_B.json").write_text(
                    json.dumps(scan_results, indent=2), encoding="utf-8"
                )
            if scan_results:
                fig3v12.apply_style_v12()
                xs = [row["L"] for row in scan_results]
                vals = [row["valley_ratio"] for row in scan_results]
                pfast = [row["p_fast"] for row in scan_results]
                fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4), constrained_layout=True)
                axes[0].plot(xs, vals, "o-", color="#6a3d9a")
                axes[0].set_xlabel("L")
                axes[0].set_ylabel("valley ratio")
                axes[1].plot(xs, pfast, "o-", color="#1f78b4")
                axes[1].set_xlabel("L")
                axes[1].set_ylabel("P_fast")
                fig3v12.save_clean(fig, fig_subdirs["channel_decomp"] / "candidate_B_scan.pdf", dpi=png_dpi)

        def save_metrics_v12(prefix: str, spec: ConfigSpec, stats: dict, extra: dict) -> None:
            payload = {
                "config": config_to_dict(spec),
                "peaks": v12_meta[prefix],
                "mc": stats | {"tail_mass": extra["tail_mass"]},
                "aw": extra["aw"],
                "plot_params": {
                    "fig_version": fig_version,
                    "plot_style": plot_style,
                    "png_dpi": int(png_dpi),
                    "mc_bin_width": int(mc_bin_width),
                    "mc_smooth_window": int(mc_smooth_window),
                    "peak_smooth_window": int(peak_smooth_window),
                    "log_eps": float(log_eps),
                },
            }
            if prefix == prefix_B and tune_report is not None:
                payload["tuning"] = tune_report.get("best", {})
            (DATA_DIR / f"{prefix}_metrics{version_suffix}.json").write_text(
                json.dumps(payload, indent=2), encoding="utf-8"
            )

        save_metrics_v12("candidate_A", spec_A, stats_A, extra_A)
        save_metrics_v12(prefix_B, spec_B, stats_B, extra_B)
        save_metrics_v12("candidate_C", spec_C, stats_C, extra_C)

        fig3v12.write_gallery_html(fig_dir)

    summary = {
        "quick": bool(quick),
        "N": int(N),
        "t_max": int(t_max),
        "t_max_scan": int(t_max_scan),
        "t_max_aw": int(t_max_aw),
        "L_min": int(L_min),
        "n_bias_min": int(n_min),
        "aw_oversample": int(aw_oversample),
        "aw_r_pow10": float(aw_r_pow10),
        "fpt_method": str(fpt_method),
        "fig_version": str(fig_version),
        "plot_style": str(plot_style),
        "png_dpi": int(png_dpi),
        "mc_bin_width": int(mc_bin_width),
        "mc_smooth_window": int(mc_smooth_window),
        "peak_smooth_window": int(peak_smooth_window),
        "log_eps": float(log_eps),
        "seed": int(seed),
        "tune_B": bool(tune_B),
    }
    (DATA_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="2D bimodality pipeline (AW inversion + exact recursion)")
    p.add_argument("--cases-json", type=str, default=None, help="Path to cases.json (optional).")
    p.add_argument("--quick", action="store_true", help="Use a smaller N=40 quick mode (scaled geometry)")
    p.add_argument("--t-max", type=int, default=3000, help="Max time for exact recursion / MC")
    p.add_argument("--t-max-scan", type=int, default=1500, help="Max time for scan recursion")
    p.add_argument("--t-max-aw", type=int, default=2000, help="Max time for AW inversion coefficients")
    p.add_argument("--mc-samples", type=int, default=5000, help="MC walkers per candidate")
    p.add_argument("--seed", type=int, default=0, help="Base RNG seed")
    p.add_argument("--aw-oversample", type=int, default=4, help="AW oversample factor for FFT length")
    p.add_argument("--aw-r-pow10", type=float, default=12.0, help="Set r so r^m = 10^(-r_pow10)")
    p.add_argument(
        "--fpt-method",
        type=str,
        default="both",
        choices=("aw", "flux", "both"),
        help="Primary FPT method to report (aw, flux, or both).",
    )
    p.add_argument(
        "--fig-version",
        type=str,
        default="main",
        choices=("main", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12"),
        help="Figure style tag (main emits versionless outputs).",
    )
    p.add_argument("--plot-style", type=str, default="v2", help="Plot style tag for figures.")
    p.add_argument("--png-dpi", type=int, default=300, help="PNG dpi for v3 outputs.")
    p.add_argument("--mc-bin-width", type=int, default=10, help="MC histogram bin width for v3 plots.")
    p.add_argument("--mc-smooth-window", type=int, default=5, help="MC smoothing window for display.")
    p.add_argument("--peak-smooth-window", type=int, default=5, help="Smoothing window for peak detection.")
    p.add_argument("--log-eps", type=float, default=1e-14, help="Epsilon floor for log-scale plots.")
    p.add_argument("--tune_B", type=int, default=1, help="Enable auto tuning for B variants (main/v9/v10/v11/v12).")
    args = p.parse_args()

    run_pipeline(
        cases_json=str(args.cases_json) if args.cases_json else None,
        quick=bool(args.quick),
        t_max=int(args.t_max),
        t_max_scan=int(args.t_max_scan),
        t_max_aw=int(args.t_max_aw),
        mc_samples=int(args.mc_samples),
        seed=int(args.seed),
        aw_oversample=int(args.aw_oversample),
        aw_r_pow10=float(args.aw_r_pow10),
        fpt_method=str(args.fpt_method),
        fig_version=str(args.fig_version),
        plot_style=str(args.plot_style),
        png_dpi=int(args.png_dpi),
        mc_bin_width=int(args.mc_bin_width),
        mc_smooth_window=int(args.mc_smooth_window),
        peak_smooth_window=int(args.peak_smooth_window),
        log_eps=float(args.log_eps),
        tune_B=bool(args.tune_B),
    )


if __name__ == "__main__":
    main()
