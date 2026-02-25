#!/usr/bin/env python3
"""Fig.3-style panels and environment schematics for v11."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plot_style_v11 import (
    ViewBox,
    add_time_tag,
    anchored_box,
    apply_style_v11,
    collect_roi_points,
    corridor_band_rows,
    draw_axes_indicator,
    draw_base,
    draw_boundaries,
    draw_corridor_band,
    draw_door,
    draw_global_bias,
    draw_local_bias,
    draw_start_target,
    draw_sticky,
    draw_walls,
    format_corridor_band_label,
    heatmap_limits,
    plot_log_heatmap_P,
    roi_bounds,
    save_clean,
)
from viz.case_data import CaseGeometry


def _info_boxes(ax: plt.Axes, case: CaseGeometry, *, extra_text: Optional[str] = None) -> None:
    boundary = f"x: {case.boundary_x}\ny: {case.boundary_y}"
    anchored_box(ax, boundary, loc="upper left", fontsize=9)
    if extra_text:
        anchored_box(ax, extra_text, loc="lower right", fontsize=9)


def draw_environment_v11(
    ax: plt.Axes,
    case: CaseGeometry,
    *,
    view: Optional[ViewBox] = None,
    show_grid: bool = True,
    show_global_bias: bool = True,
    show_boundaries: bool = True,
    bias_step: int = 1,
    corridor_halfwidth: int = 1,
    corridor_rows: Sequence[int] | None = None,
    extra_text: Optional[str] = None,
) -> None:
    draw_base(ax, case.N, view=view, coarse_grid_step=8 if show_grid else 0)
    draw_corridor_band(ax, case.corridor, band_rows=corridor_rows, band_halfwidth=corridor_halfwidth)
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
        _info_boxes(ax, case, extra_text=extra_text)
    draw_axes_indicator(ax, anchor=(1 if view is None else view.x0, 1 if view is None else view.y0))


def _corridor_strip_view(case: CaseGeometry, *, band_rows: Sequence[int], pad_x: int = 6, pad_y: int = 2) -> ViewBox:
    if not case.corridor:
        return ViewBox(1, case.N, 1, case.N)
    x0 = int(case.corridor["x_start"])
    x1 = int(case.corridor["x_end"])
    y_min = min(band_rows)
    y_max = max(band_rows)
    x0 = max(1, x0 - pad_x)
    x1 = min(case.N, x1 + pad_x)
    y0 = max(1, y_min - pad_y)
    y1 = min(case.N, y_max + pad_y)
    return ViewBox(x0, x1, y0, y1)


def plot_environment_v11(
    case: CaseGeometry,
    *,
    outpath: Path,
    dpi: int = 900,
    roi: Optional[ViewBox] = None,
    bias_step_main: int = 3,
    bias_step_zoom: int = 1,
    corridor_halfwidth: int = 1,
    corridor_rows: Sequence[int] | None = None,
    extra_text: Optional[str] = None,
    strip_main: bool = False,
) -> None:
    apply_style_v11()
    fig, ax = plt.subplots(figsize=(9.6, 6.0), constrained_layout=True)

    main_view = roi if strip_main and roi is not None else None
    draw_environment_v11(
        ax,
        case,
        view=main_view,
        bias_step=bias_step_main,
        corridor_halfwidth=corridor_halfwidth,
        corridor_rows=corridor_rows,
        extra_text=extra_text,
    )

    if roi is not None and strip_main:
        inset = inset_axes(ax, width="38%", height="38%", loc="upper right", borderpad=1.0)
        draw_environment_v11(
            inset,
            case,
            view=None,
            show_grid=False,
            show_global_bias=False,
            show_boundaries=False,
            bias_step=max(3, bias_step_main),
            corridor_halfwidth=corridor_halfwidth,
            corridor_rows=corridor_rows,
        )
        draw_base(inset, case.N, view=None, coarse_grid_step=12, fine_grid=False)
        inset.add_patch(
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
        anchored_box(inset, "overview", loc="lower left", fontsize=8)

    save_clean(fig, outpath, dpi=dpi)


def plot_candidate_B_env_v11(
    case: CaseGeometry,
    *,
    corridor_rows: Sequence[int],
    outpath: Path,
    dpi: int = 900,
    corridor_halfwidth: int = 1,
) -> None:
    apply_style_v11()
    if not all(1 <= int(y) <= case.N for y in corridor_rows):
        raise ValueError("corridor band rows out of bounds.")
    fig, ax = plt.subplots(figsize=(10.6, 4.8), constrained_layout=True)
    strip_view = _corridor_strip_view(case, band_rows=corridor_rows)
    label = format_corridor_band_label(corridor_rows)
    extra_text = None
    if case.corridor:
        L = abs(int(case.corridor["x_end"]) - int(case.corridor["x_start"])) + 1
        extra_text = f"{label}\nL={L}, delta={case.local_bias_delta:.2f}"
    draw_environment_v11(
        ax,
        case,
        view=strip_view,
        bias_step=2,
        corridor_halfwidth=corridor_halfwidth,
        corridor_rows=corridor_rows,
        extra_text=extra_text,
    )

    inset = inset_axes(ax, width="30%", height="42%", loc="upper right", borderpad=1.0)
    draw_environment_v11(
        inset,
        case,
        view=None,
        show_grid=False,
        show_global_bias=False,
        show_boundaries=False,
        bias_step=6,
        corridor_halfwidth=corridor_halfwidth,
        corridor_rows=corridor_rows,
    )
    draw_base(inset, case.N, view=None, coarse_grid_step=12, fine_grid=False)
    inset.add_patch(
        Rectangle(
            (strip_view.x0 - 0.5, strip_view.y0 - 0.5),
            strip_view.x1 - strip_view.x0 + 1,
            strip_view.y1 - strip_view.y0 + 1,
            fill=False,
            lw=1.2,
            edgecolor="white",
            zorder=7,
        )
    )
    anchored_box(inset, "overview", loc="lower left", fontsize=8)

    save_clean(fig, outpath, dpi=dpi)


def plot_symbol_legend_v11(*, outpath: Path, dpi: int = 900) -> None:
    apply_style_v11()
    fig, ax = plt.subplots(figsize=(7.6, 3.4), constrained_layout=True)
    ax.axis("off")
    handles = [
        Line2D([0], [0], color="0.2", lw=2.0, marker=">", markersize=8, label="global bias"),
        Line2D([0], [0], marker="s", markersize=10, color="#e41a1c", markeredgecolor="black", lw=0, label="start"),
        Line2D([0], [0], marker="D", markersize=10, color="#377eb8", markeredgecolor="black", lw=0, label="target"),
        Line2D([0], [0], color="black", lw=2.4, label="wall"),
        Line2D([0], [0], color="#b30000", lw=2.4, ls=(0, (3, 2)), label="door (p_pass)"),
        Patch(facecolor="#9fb3b5", edgecolor="#6b7a78", hatch="///", alpha=0.35, label="sticky"),
        Line2D([0], [0], color="#d62728", lw=1.6, marker=">", markersize=7, label="local bias"),
    ]
    ax.legend(
        handles=handles,
        labels=[h.get_label() for h in handles],
        ncol=2,
        frameon=True,
        loc="center",
        borderaxespad=0.6,
    )
    save_clean(fig, outpath, dpi=dpi)


def plot_fig3_panel_v11(
    case: CaseGeometry,
    *,
    mats: Sequence[np.ndarray],
    times: Sequence[int],
    outpath: Path,
    dpi: int = 900,
    eps: float = 1e-14,
    bias_step_env: int = 3,
    bias_step_heat: int = 1,
    corridor_halfwidth: int = 1,
    corridor_rows: Sequence[int] | None = None,
    env_strip: bool = False,
    strip_view: Optional[ViewBox] = None,
) -> None:
    apply_style_v11()
    fig = plt.figure(figsize=(12.8, 8.2), constrained_layout=True)
    gs = fig.add_gridspec(3, 3, width_ratios=[1.1, 1.0, 0.06], wspace=0.06)

    ax_env = fig.add_subplot(gs[:, 0])
    draw_environment_v11(
        ax_env,
        case,
        view=strip_view if env_strip else None,
        bias_step=bias_step_env,
        corridor_halfwidth=corridor_halfwidth,
        corridor_rows=corridor_rows,
        extra_text=None,
    )
    if env_strip and strip_view is not None:
        inset = inset_axes(ax_env, width="40%", height="40%", loc="upper right", borderpad=1.0)
        draw_environment_v11(
            inset,
            case,
            view=None,
            show_grid=False,
            show_global_bias=False,
            show_boundaries=False,
            bias_step=max(4, bias_step_env),
            corridor_halfwidth=corridor_halfwidth,
            corridor_rows=corridor_rows,
        )
        draw_base(inset, case.N, view=None, coarse_grid_step=12, fine_grid=False)
        inset.add_patch(
            Rectangle(
                (strip_view.x0 - 0.5, strip_view.y0 - 0.5),
                strip_view.x1 - strip_view.x0 + 1,
                strip_view.y1 - strip_view.y0 + 1,
                fill=False,
                lw=1.2,
                edgecolor="white",
                zorder=7,
            )
        )
        anchored_box(inset, "overview", loc="lower left", fontsize=8)

    vmin, vmax = heatmap_limits(mats, eps=eps)
    ax_h = [fig.add_subplot(gs[i, 1]) for i in range(3)]
    avoid_pts = collect_roi_points(case, include_start_target=True)
    for ax, P, t in zip(ax_h, mats, times):
        plot_log_heatmap_P(ax, P, N=case.N, vmin=vmin, vmax=vmax, eps=eps)
        draw_walls(ax, case.barriers_reflect)
        if case.barriers_perm:
            draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1], label=False)
        draw_corridor_band(ax, case.corridor, band_rows=corridor_rows, band_halfwidth=corridor_halfwidth)
        draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
        draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=bias_step_heat)
        draw_start_target(ax, case.start, case.target)
        add_time_tag(ax, int(t), avoid_points=avoid_pts)

    cax = fig.add_subplot(gs[:, 2])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=LogNorm(vmin=vmin, vmax=vmax), cmap="magma"), cax=cax)
    cb.set_label("P(n,t)")

    save_clean(fig, outpath, dpi=dpi)
