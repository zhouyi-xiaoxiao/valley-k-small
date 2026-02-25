#!/usr/bin/env python3
"""Path density plots for v11 (density + simplified rep paths)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from plot_style_v11 import (
    ViewBox,
    apply_style_v11,
    draw_corridor_band,
    draw_door,
    draw_local_bias,
    draw_start_target,
    draw_sticky,
    draw_walls,
    roi_bounds_auto,
    save_clean,
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


def _gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    ax = np.arange(-(size // 2), size // 2 + 1)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    kernel /= kernel.sum()
    return kernel


def _smooth_density(density: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    if sigma <= 0:
        return density
    size = 5
    kernel = _gaussian_kernel(size, sigma)
    pad = size // 2
    padded = np.pad(density, pad, mode="edge")
    out = np.zeros_like(density, dtype=np.float64)
    for i in range(density.shape[0]):
        for j in range(density.shape[1]):
            window = padded[i : i + size, j : j + size]
            out[i, j] = float(np.sum(window * kernel))
    return out


def _plot_density(ax: plt.Axes, density: np.ndarray, *, N: int, view: ViewBox | None = None) -> None:
    scaled = np.sqrt(density)
    ax.imshow(
        scaled.T,
        origin="lower",
        cmap="viridis",
        interpolation="nearest",
        extent=(0.5, N + 0.5, 0.5, N + 0.5),
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    ax.invert_yaxis()
    if view is not None:
        ax.set_xlim(view.x0 - 0.5, view.x1 + 0.5)
        ax.set_ylim(view.y0 - 0.5, view.y1 + 0.5)
        ax.invert_yaxis()


def _simplify_path(path: np.ndarray, *, step: int = 6) -> np.ndarray:
    if path.size == 0:
        return path
    if len(path) <= 2:
        return path
    keep = [0]
    prev_dx, prev_dy = None, None
    for i in range(1, len(path)):
        dx = int(path[i][0] - path[i - 1][0])
        dy = int(path[i][1] - path[i - 1][1])
        if prev_dx is None:
            prev_dx, prev_dy = dx, dy
        if (dx, dy) != (prev_dx, prev_dy) or i % step == 0:
            keep.append(i)
            prev_dx, prev_dy = dx, dy
    if keep[-1] != len(path) - 1:
        keep.append(len(path) - 1)
    return path[keep]


def _plot_rep_paths(ax: plt.Axes, paths: Sequence[np.ndarray], *, color: str) -> None:
    for path in paths:
        if path.size == 0:
            continue
        simp = _simplify_path(path, step=6)
        xs = simp[:, 0]
        ys = simp[:, 1]
        ax.plot(xs, ys, color=color, lw=2.0, alpha=0.9, zorder=6)
        if len(xs) > 1:
            ax.annotate(
                "",
                xy=(xs[-1], ys[-1]),
                xytext=(xs[-2], ys[-2]),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2),
            )


def plot_paths_density_v11(
    case: CaseGeometry,
    *,
    paths_density: Sequence[np.ndarray],
    rep_paths: Sequence[np.ndarray],
    outpath: Path,
    dpi: int = 900,
    corridor_halfwidth: int = 1,
    roi: ViewBox | None = None,
) -> None:
    apply_style_v11()
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.4), constrained_layout=True)

    density = _path_density(paths_density, case.N)
    density = _smooth_density(density, sigma=1.0)

    roi = roi or roi_bounds_auto(case, margin=6)

    _plot_density(axes[0], density, N=case.N)
    draw_walls(axes[0], case.barriers_reflect)
    if case.barriers_perm:
        draw_door(axes[0], [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1], label=False)
    draw_corridor_band(axes[0], case.corridor, band_halfwidth=corridor_halfwidth)
    draw_sticky(axes[0], [(c["x"], c["y"]) for c in case.sticky])
    draw_local_bias(axes[0], [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=6)
    draw_start_target(axes[0], case.start, case.target)
    _plot_rep_paths(axes[0], rep_paths, color="#fdae61")
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
    axes[0].set_title("full domain")

    _plot_density(axes[1], density, N=case.N, view=roi)
    draw_walls(axes[1], case.barriers_reflect)
    if case.barriers_perm:
        draw_door(axes[1], [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1], label=False)
    draw_corridor_band(axes[1], case.corridor, band_halfwidth=corridor_halfwidth)
    draw_sticky(axes[1], [(c["x"], c["y"]) for c in case.sticky])
    draw_local_bias(axes[1], [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=2)
    draw_start_target(axes[1], case.start, case.target)
    _plot_rep_paths(axes[1], rep_paths, color="#fdae61")
    axes[1].set_title("ROI zoom")

    save_clean(fig, outpath, dpi=dpi)
