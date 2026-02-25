#!/usr/bin/env python3
"""Heatmap plotting for v4 figures."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

from .case_data import CaseGeometry
from .draw_overlays import draw_barriers, draw_corridor_band, draw_local_bias, draw_start_target, draw_sticky
from .style import set_style


def compute_lognorm(mats: Sequence[np.ndarray], *, vmin_floor: float = 1e-12) -> LogNorm:
    vmax = max(float(np.max(m)) for m in mats)
    positive = [m[m > 0] for m in mats if np.any(m > 0)]
    vmin = min(float(np.min(p)) for p in positive) if positive else vmin_floor
    vmin = max(vmin, vmin_floor)
    return LogNorm(vmin=vmin, vmax=vmax)


def _plot_single_heatmap(
    ax: plt.Axes,
    P: np.ndarray,
    *,
    case: CaseGeometry,
    norm: LogNorm,
    t: int,
    cmap: str = "magma",
    overlay: bool = True,
) -> None:
    N = case.N
    extent = (0.5, N + 0.5, 0.5, N + 0.5)
    im = ax.imshow(
        P.T,
        origin="lower",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
        extent=extent,
    )

    if overlay:
        draw_corridor_band(ax, case)
        draw_sticky(ax, case)
        draw_barriers(ax, case)
        draw_local_bias(ax, case)
        draw_start_target(ax, case)

    ax.text(
        0.96,
        0.06,
        f"t={t}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color="white",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.35, linewidth=0.0),
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    ax.invert_yaxis()
    return im


def _add_roi_inset(
    ax: plt.Axes,
    P: np.ndarray,
    *,
    case: CaseGeometry,
    norm: LogNorm,
    roi: Tuple[int, int, int, int],
    cmap: str = "magma",
) -> None:
    x0, x1, y0, y1 = roi
    inset = inset_axes(ax, width="40%", height="40%", loc="lower right", borderpad=1.2)
    N = case.N
    extent = (0.5, N + 0.5, 0.5, N + 0.5)
    inset.imshow(
        P.T,
        origin="lower",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
        extent=extent,
    )
    draw_sticky(inset, case)
    draw_corridor_band(inset, case)
    draw_barriers(inset, case)
    draw_local_bias(inset, case)
    draw_start_target(inset, case)
    inset.set_xlim(x0 - 0.5, x1 + 0.5)
    inset.set_ylim(y0 - 0.5, y1 + 0.5)
    inset.invert_yaxis()
    inset.set_xticks([])
    inset.set_yticks([])
    mark_inset(ax, inset, loc1=2, loc2=4, fc="none", ec="0.5", lw=0.8)


def plot_heatmap_triplet(
    case: CaseGeometry,
    mats: Sequence[np.ndarray],
    times: Sequence[int],
    *,
    outpath: Path,
    cmap: str = "magma",
    vmin_floor: float = 1e-12,
    overlay: bool = True,
    roi: Optional[Tuple[int, int, int, int]] = None,
    dpi: int = 600,
) -> dict:
    set_style("fig3")
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.6), constrained_layout=True)
    norm = compute_lognorm(mats, vmin_floor=vmin_floor)

    images = []
    for ax, P, t in zip(axes, mats, times):
        im = _plot_single_heatmap(ax, P, case=case, norm=norm, t=int(t), cmap=cmap, overlay=overlay)
        images.append(im)
        if roi is not None:
            _add_roi_inset(ax, P, case=case, norm=norm, roi=roi, cmap=cmap)

    cbar = fig.colorbar(images[-1], ax=axes, shrink=0.9, pad=0.02)
    cbar.set_label("P(n,t) (log scale)")

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=dpi)
    fig.savefig(outpath.with_suffix(".png"), dpi=dpi)
    plt.close(fig)
    return {"vmin": float(norm.vmin), "vmax": float(norm.vmax)}
