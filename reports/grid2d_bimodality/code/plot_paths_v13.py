#!/usr/bin/env python3
"""Path density plots for v13 (density background + representative paths)."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from plot_style_v13 import (
    ViewBox,
    apply_style_v13,
    draw_corridor_band,
    draw_door,
    draw_local_bias,
    draw_start_target,
    draw_sticky,
    draw_walls,
    auto_strip_view,
    strip_view_full_width,
    roi_bounds_strip,
    roi_bounds_auto,
    save_clean,
    simplify_path,
)
from viz.case_data import CaseGeometry


def _path_density(paths: Sequence[np.ndarray], N: int) -> np.ndarray:
    density = np.zeros((N, N), dtype=np.float64)
    for path in paths:
        if path.size == 0:
            continue
        for x, y in path:
            if 1 <= x <= N and 1 <= y <= N:
                density[x - 1, y - 1] += 1.0
    return density


def _plot_density(
    ax: plt.Axes,
    density: np.ndarray,
    *,
    N: int,
    view: ViewBox | None = None,
    local_norm: bool = False,
) -> None:
    scaled = np.log1p(density)
    vmax = float(np.max(scaled)) if scaled.size else 1.0
    if view is not None:
        xs = slice(max(0, view.x0 - 1), min(N, view.x1))
        ys = slice(max(0, view.y0 - 1), min(N, view.y1))
        if local_norm:
            sub = scaled[xs, ys]
            if sub.size and float(np.max(sub)) > 0:
                vmax = float(np.max(sub))
        scaled = scaled[xs, ys]
        extent = (view.x0 - 0.5, view.x1 + 0.5, view.y0 - 0.5, view.y1 + 0.5)
    else:
        extent = (0.5, N + 0.5, 0.5, N + 0.5)
    if vmax <= 0:
        vmax = 1.0
    ax.imshow(
        scaled.T,
        origin="lower",
        cmap="viridis",
        interpolation="nearest",
        extent=extent,
        vmin=0.0,
        vmax=vmax,
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    ax.invert_yaxis()
    if view is not None:
        ax.set_aspect("auto")


def _plot_rep_paths(
    ax: plt.Axes,
    paths: Sequence[np.ndarray],
    *,
    color: str,
    step: int = 18,
    alpha: float = 0.45,
    max_paths: int = 2,
    view: ViewBox | None = None,
) -> None:
    def _in_view(pt: np.ndarray, view_box: ViewBox | None) -> bool:
        if view_box is None:
            return True
        return view_box.x0 <= pt[0] <= view_box.x1 and view_box.y0 <= pt[1] <= view_box.y1

    def _segment_path(path: np.ndarray, view_box: ViewBox | None) -> list[np.ndarray]:
        if path.size == 0:
            return []
        segments: list[list[np.ndarray]] = []
        current: list[np.ndarray] = []
        prev_pt = None
        for pt in path:
            if not _in_view(pt, view_box):
                if current:
                    segments.append(current)
                    current = []
                prev_pt = None
                continue
            if prev_pt is not None:
                if max(abs(int(pt[0] - prev_pt[0])), abs(int(pt[1] - prev_pt[1]))) > 2:
                    if current:
                        segments.append(current)
                    current = [pt]
                    prev_pt = pt
                    continue
            current.append(pt)
            prev_pt = pt
        if current:
            segments.append(current)
        return [np.array(seg) for seg in segments if len(seg) >= 2]

    def _coarsen_path(path: np.ndarray, max_points: int = 4) -> np.ndarray:
        if path.size == 0:
            return path
        if len(path) <= max_points:
            return path
        block = max(5, len(path) // max_points)
        pts = []
        for i in range(0, len(path), block):
            seg = path[i : i + block]
            if seg.size == 0:
                continue
            pts.append(seg.mean(axis=0))
        if pts:
            pts[0] = path[0].astype(float)
            pts[-1] = path[-1].astype(float)
        return np.array(pts, dtype=float)

    def _downsample_path(path: np.ndarray, step_size: int) -> np.ndarray:
        if path.size == 0:
            return path
        if len(path) <= 2:
            return path
        idx = list(range(0, len(path), step_size))
        if idx[-1] != len(path) - 1:
            idx.append(len(path) - 1)
        return path[idx]

    count = 0
    for path in paths:
        if count >= max_paths:
            break
        if path.size == 0:
            continue
        segments = _segment_path(path, view)
        if not segments:
            continue
        # Keep only the longest segment to avoid spaghetti overlays.
        segments = sorted(segments, key=len, reverse=True)[:1]
        for seg in segments:
            step_local = max(step, max(4, len(seg) // 4))
            simp = _downsample_path(seg, step_local)
            simp = simplify_path(simp, step=max(6, step_local // 3))
            simp = _coarsen_path(simp, max_points=4)
            if simp.size == 0:
                continue
            xs = simp[:, 0]
            ys = simp[:, 1]
            ax.plot(xs, ys, color=color, lw=1.2, alpha=alpha, zorder=6)
            if len(xs) > 1:
                ax.annotate(
                    "",
                    xy=(xs[-1], ys[-1]),
                    xytext=(xs[-2], ys[-2]),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=0.9, alpha=alpha),
                )
        count += 1


def plot_paths_density_v12(
    case: CaseGeometry,
    *,
    paths_density: Sequence[np.ndarray],
    rep_paths: Sequence[np.ndarray],
    outpath: Path,
    dpi: int = 800,
    corridor_halfwidth: int = 1,
    roi: ViewBox | None = None,
) -> None:
    apply_style_v13()
    density = _path_density(paths_density, case.N)

    roi = roi or roi_bounds_auto(case, margin=4, max_frac=0.6)
    full_view: ViewBox | None = None
    use_strip = False
    rows = None
    if case.corridor and case.classification_rule:
        rows = case.classification_rule.get("corridor_band_rows") or case.classification_rule.get("band_rows")
        if rows:
            if roi is None:
                roi = roi_bounds_strip(case, corridor_rows=rows, pad_x=2, pad_y=3, min_width=14, min_height=8)
            use_strip = True
            full_view = strip_view_full_width(case, rows, pad_y=4)

    fig_width = 10.5 if use_strip else 12.0
    fig_height = 4.0 if use_strip else 4.8
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(fig_width, fig_height),
        gridspec_kw={"width_ratios": [1.05, 1.0]},
        constrained_layout=False,
    )
    fig.subplots_adjust(left=0.055, right=0.98, bottom=0.08, top=0.96, wspace=0.12)

    is_slow = "slow" in outpath.stem
    step_roi = 140 if is_slow else 70

    def _in_view(pt: tuple[int, int], view_box: ViewBox | None) -> bool:
        if view_box is None:
            return True
        return view_box.x0 <= pt[0] <= view_box.x1 and view_box.y0 <= pt[1] <= view_box.y1

    def _filter_edges(edges: Sequence[tuple[tuple[int, int], tuple[int, int]]], view_box: ViewBox | None):
        if view_box is None:
            return list(edges)
        return [edge for edge in edges if _in_view(edge[0], view_box) or _in_view(edge[1], view_box)]

    _plot_density(axes[0], density, N=case.N, view=full_view, local_norm=False)
    draw_walls(axes[0], _filter_edges(case.barriers_reflect, full_view), lw=1.0)
    if case.barriers_perm:
        doors = _filter_edges([edge for edge, _ in case.barriers_perm], full_view)
        if doors:
            draw_door(axes[0], doors, p_pass=case.barriers_perm[0][1], label=False)
    if rows:
        if full_view is not None:
            full_rows = list(range(full_view.y0, full_view.y1 + 1))
            draw_corridor_band(
                axes[0],
                case.corridor,
                band_rows=full_rows,
                x_span=(full_view.x0, full_view.x1),
                color="#fdd0a2",
                alpha=0.18,
            )
        draw_corridor_band(axes[0], case.corridor, band_rows=rows, alpha=0.28)
    else:
        draw_corridor_band(axes[0], case.corridor, band_halfwidth=corridor_halfwidth, alpha=0.18)
    sticky_pts = [(c["x"], c["y"]) for c in case.sticky if _in_view((c["x"], c["y"]), full_view)]
    if sticky_pts:
        draw_sticky(axes[0], sticky_pts)
    bias_pts = [(c["x"], c["y"], c["dir"]) for c in case.local_bias if _in_view((c["x"], c["y"]), full_view)]
    if bias_pts:
        draw_local_bias(axes[0], bias_pts, step=16)
    if _in_view(case.start, full_view) and _in_view(case.target, full_view):
        draw_start_target(axes[0], case.start, case.target)
    # Full-domain panel: density only (no path overlays) to avoid line clutter.
    if not full_view or (roi.x0, roi.x1, roi.y0, roi.y1) != (full_view.x0, full_view.x1, full_view.y0, full_view.y1):
        axes[0].add_patch(
            Rectangle(
                (roi.x0 - 0.5, roi.y0 - 0.5),
                roi.x1 - roi.x0 + 1,
                roi.y1 - roi.y0 + 1,
                fill=False,
                lw=1.2,
                edgecolor="white",
                zorder=7,
            )
        )
    # keep the panel clean; no title text

    _plot_density(axes[1], density, N=case.N, view=roi, local_norm=True)
    draw_walls(axes[1], _filter_edges(case.barriers_reflect, roi), lw=1.0)
    if case.barriers_perm:
        doors = _filter_edges([edge for edge, _ in case.barriers_perm], roi)
        if doors:
            draw_door(axes[1], doors, p_pass=case.barriers_perm[0][1], label=False)
    if rows:
        draw_corridor_band(axes[1], case.corridor, band_rows=rows, alpha=0.25)
    else:
        draw_corridor_band(axes[1], case.corridor, band_halfwidth=corridor_halfwidth, alpha=0.2)
    sticky_pts = [(c["x"], c["y"]) for c in case.sticky if _in_view((c["x"], c["y"]), roi)]
    if sticky_pts:
        draw_sticky(axes[1], sticky_pts)
    bias_pts = [(c["x"], c["y"], c["dir"]) for c in case.local_bias if _in_view((c["x"], c["y"]), roi)]
    if bias_pts:
        draw_local_bias(axes[1], bias_pts, step=8)
    if _in_view(case.start, roi) and _in_view(case.target, roi):
        draw_start_target(axes[1], case.start, case.target)
    _plot_rep_paths(
        axes[1],
        rep_paths,
        color="#fdae61",
        step=step_roi,
        alpha=0.55,
        max_paths=3,
        view=roi,
    )
    # keep the panel clean; no title text

    save_clean(fig, outpath, dpi=dpi)
