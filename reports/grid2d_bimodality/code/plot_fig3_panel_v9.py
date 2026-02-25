#!/usr/bin/env python3
"""Fig.3-style panels and environment schematics for v9."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plot_style_v9 import (
    ViewBox,
    add_time_tag,
    anchored_box,
    apply_style_v9,
    collect_roi_points,
    draw_base,
    draw_boundaries,
    draw_corridor_band,
    draw_door,
    draw_global_bias,
    draw_local_bias,
    draw_start_target,
    draw_sticky,
    draw_walls,
    heatmap_limits,
    plot_log_heatmap_P,
    roi_bounds,
    save_clean,
)
from viz.case_data import CaseGeometry


def _info_boxes(ax: plt.Axes, case: CaseGeometry) -> None:
    boundary = f"x: {case.boundary_x}\ny: {case.boundary_y}"
    anchored_box(ax, boundary, loc="upper left", fontsize=9)


def draw_environment_v9(
    ax: plt.Axes,
    case: CaseGeometry,
    *,
    view: Optional[ViewBox] = None,
    show_grid: bool = True,
    show_global_bias: bool = True,
    show_boundaries: bool = True,
    bias_step: int = 1,
    corridor_halfwidth: int = 1,
    extra_text: Optional[str] = None,
) -> None:
    draw_base(ax, case.N, view=view, coarse_grid_step=5 if show_grid else 0)
    draw_corridor_band(ax, case.corridor, band_halfwidth=corridor_halfwidth)
    draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
    draw_walls(ax, case.barriers_reflect)
    if case.barriers_perm:
        draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1], label=True)
    draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=bias_step)
    draw_start_target(ax, case.start, case.target)
    if show_global_bias:
        x0, x1, y0, y1 = (view.x0, view.x1, view.y0, view.y1) if view else (1, case.N, 1, case.N)
        draw_global_bias(ax, case.g_x, case.g_y, anchor=(x0 + 1, y1 - 2))
    if show_boundaries:
        draw_boundaries(ax, case, view=view)
        _info_boxes(ax, case)
    if extra_text:
        anchored_box(ax, extra_text, loc="lower right", fontsize=9)


def plot_environment_v9(
    case: CaseGeometry,
    *,
    outpath: Path,
    dpi: int = 600,
    roi: Optional[ViewBox] = None,
    bias_step_main: int = 3,
    bias_step_zoom: int = 1,
    corridor_halfwidth: int = 1,
    extra_text: Optional[str] = None,
) -> None:
    apply_style_v9()
    fig, ax = plt.subplots(figsize=(9.2, 6.2), constrained_layout=True)
    draw_environment_v9(
        ax,
        case,
        bias_step=bias_step_main,
        corridor_halfwidth=corridor_halfwidth,
        extra_text=extra_text,
    )

    if roi is not None:
        inset = inset_axes(ax, width="40%", height="40%", loc="lower right", borderpad=1.2)
        draw_environment_v9(
            inset,
            case,
            view=roi,
            show_grid=False,
            show_global_bias=False,
            show_boundaries=False,
            bias_step=bias_step_zoom,
            corridor_halfwidth=corridor_halfwidth,
        )
        draw_base(inset, case.N, view=roi, coarse_grid_step=1, fine_grid=True)
        anchored_box(inset, "zoom", loc="upper right", fontsize=8)

    save_clean(fig, outpath, dpi=dpi)


def plot_symbol_legend_v9(*, outpath: Path, dpi: int = 600) -> None:
    apply_style_v9()
    fig, ax = plt.subplots(figsize=(7.6, 3.4), constrained_layout=True)
    ax.axis("off")
    ax.text(0.05, 0.8, "global bias", fontsize=10)
    ax.annotate(
        "",
        xy=(0.22, 0.82),
        xytext=(0.10, 0.82),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", lw=1.8, color="0.25"),
    )
    ax.text(0.05, 0.6, "start", color="#e41a1c", fontsize=10)
    ax.text(0.24, 0.6, "target", color="#377eb8", fontsize=10)
    ax.scatter([0.18], [0.6], s=80, c="#e41a1c", marker="s", edgecolors="black", transform=ax.transAxes)
    ax.scatter([0.37], [0.6], s=80, c="#377eb8", marker="D", edgecolors="black", transform=ax.transAxes)
    ax.plot([0.05, 0.18], [0.42, 0.42], color="black", lw=2.4, transform=ax.transAxes)
    ax.text(0.21, 0.4, "wall", fontsize=10)
    ax.plot([0.05, 0.18], [0.26, 0.26], color="black", lw=2.4, ls=(0, (3, 2)), transform=ax.transAxes)
    ax.text(0.21, 0.24, "door", fontsize=10)
    ax.add_patch(
        Rectangle(
            (0.05, 0.08),
            0.08,
            0.08,
            transform=ax.transAxes,
            facecolor="#9fb3b5",
            edgecolor="#6b7a78",
            hatch="///",
            alpha=0.35,
        )
    )
    ax.text(0.21, 0.08, "sticky", fontsize=10)
    ax.annotate(
        "",
        xy=(0.12, 0.14),
        xytext=(0.20, 0.14),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#d62728"),
    )
    ax.text(0.24, 0.13, "local bias", fontsize=10, color="#d62728")
    save_clean(fig, outpath, dpi=dpi)


def plot_fig3_panel_v9(
    case: CaseGeometry,
    *,
    mats: Sequence[np.ndarray],
    times: Sequence[int],
    outpath: Path,
    dpi: int = 600,
    eps: float = 1e-14,
    bias_step_env: int = 3,
    bias_step_heat: int = 1,
    corridor_halfwidth: int = 1,
) -> None:
    apply_style_v9()
    fig = plt.figure(figsize=(12.5, 8.4), constrained_layout=True)
    gs = fig.add_gridspec(3, 3, width_ratios=[1.1, 1.0, 0.06], wspace=0.06)

    ax_env = fig.add_subplot(gs[:, 0])
    draw_environment_v9(
        ax_env,
        case,
        bias_step=bias_step_env,
        corridor_halfwidth=corridor_halfwidth,
        extra_text=None,
    )

    vmin, vmax = heatmap_limits(mats, eps=eps)
    ax_h = [fig.add_subplot(gs[i, 1]) for i in range(3)]
    for ax, P, t in zip(ax_h, mats, times):
        plot_log_heatmap_P(ax, P, N=case.N, vmin=vmin, vmax=vmax, eps=eps)
        draw_walls(ax, case.barriers_reflect)
        if case.barriers_perm:
            draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1], label=False)
        draw_corridor_band(ax, case.corridor, band_halfwidth=corridor_halfwidth)
        draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
        draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=bias_step_heat)
        draw_start_target(ax, case.start, case.target)
        add_time_tag(ax, int(t))

    cax = fig.add_subplot(gs[:, 2])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=LogNorm(vmin=vmin, vmax=vmax), cmap="magma"), cax=cax)
    cb.set_label("P(n,t)")

    save_clean(fig, outpath, dpi=dpi)
