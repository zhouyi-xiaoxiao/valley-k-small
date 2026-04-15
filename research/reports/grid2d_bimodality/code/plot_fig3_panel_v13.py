#!/usr/bin/env python3
"""Fig.3-style panels and environment schematics for v13 (fig3v5)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plot_style_v13 import (
    ViewBox,
    add_time_tag,
    auto_strip_view,
    roi_bounds_strip,
    strip_view_full_width,
    anchored_box,
    safe_corner_box,
    apply_style_v13,
    draw_axes_indicator,
    draw_boundaries,
    draw_channel_path,
    draw_corridor_band,
    draw_door,
    draw_global_bias,
    draw_global_bias_axes,
    draw_local_bias,
    draw_start_target,
    draw_sticky,
    draw_walls,
    draw_base,
    heatmap_limits,
    plot_log_heatmap_P,
    save_clean,
)
from viz.case_data import CaseGeometry


def _bias_arrow_step(case: CaseGeometry, step_default: int) -> int:
    if not case.local_bias:
        return step_default
    return max(step_default, max(1, len(case.local_bias) // 6))


def _default_strip_view(case: CaseGeometry, corridor_rows: Sequence[int] | None) -> ViewBox:
    rows = list(corridor_rows) if corridor_rows else []
    if not rows and case.corridor:
        rows = [int(case.corridor["y"])]
    if rows:
        return roi_bounds_strip(
            case,
            corridor_rows=rows,
            pad_x=2,
            pad_y=2,
            min_width=12,
            min_height=6,
        )
    return ViewBox(1, case.N, max(1, case.N - 3), case.N)


def _candidate_B_strip_view(
    case: CaseGeometry,
    corridor_rows: Sequence[int],
    *,
    pad_x: int = 1,
    pad_y: int = 2,
    min_width: int = 12,
    min_height: int = 6,
) -> ViewBox:
    xs = [case.start[0], case.target[0]]
    if case.corridor:
        xs.extend([int(case.corridor["x_start"]), int(case.corridor["x_end"])])
    x0 = max(1, min(xs) - pad_x)
    x1 = min(case.N, max(xs) + pad_x)
    if corridor_rows:
        y_min = min(corridor_rows)
        y_max = max(corridor_rows)
    else:
        y_min = int(case.start[1])
        y_max = int(case.start[1])
    y0 = max(1, y_min - pad_y)
    y1 = min(case.N, y_max + pad_y)
    width = x1 - x0 + 1
    if width < min_width:
        extra = (min_width - width + 1) // 2
        x0 = max(1, x0 - extra)
        x1 = min(case.N, x1 + extra)
        if x1 - x0 + 1 < min_width and x0 == 1:
            x1 = min(case.N, x0 + min_width - 1)
        if x1 - x0 + 1 < min_width and x1 == case.N:
            x0 = max(1, x1 - min_width + 1)
    height = y1 - y0 + 1
    min_height = max(min_height, len(corridor_rows) if corridor_rows else 1)
    if height < min_height:
        extra = (min_height - height + 1) // 2
        y0 = max(1, y0 - extra)
        y1 = min(case.N, y1 + extra)
        if y1 - y0 + 1 < min_height and y0 == 1:
            y1 = min(case.N, y0 + min_height - 1)
        if y1 - y0 + 1 < min_height and y1 == case.N:
            y0 = max(1, y1 - min_height + 1)
    return ViewBox(x0, x1, y0, y1)


def _corridor_rows_from_case(case: CaseGeometry, corridor_rows: Sequence[int] | None) -> list[int]:
    if corridor_rows:
        return [int(y) for y in corridor_rows]
    rule = case.classification_rule or {}
    rows = rule.get("corridor_band_rows") or rule.get("band_rows")
    if rows:
        return [int(y) for y in rows]
    if case.corridor and "y" in case.corridor:
        return [int(case.corridor["y"])]
    return []


def _draw_candidate_B_strip(
    ax: plt.Axes,
    case: CaseGeometry,
    *,
    strip_view: ViewBox,
    corridor_halfwidth: int,
    corridor_rows: Sequence[int],
    fast_path: np.ndarray | None = None,
    slow_path: np.ndarray | None = None,
) -> None:
    corridor_rows = _corridor_rows_from_case(case, corridor_rows)

    def _in_view(x: int, y: int) -> bool:
        return strip_view.x0 <= x <= strip_view.x1 and strip_view.y0 <= y <= strip_view.y1

    draw_base(ax, case.N, view=strip_view, coarse_grid_step=10, aspect="auto")
    # Highlight the actual corridor segment.
    draw_corridor_band(
        ax,
        case.corridor,
        band_rows=corridor_rows,
        band_halfwidth=corridor_halfwidth,
        color="#fdae6b",
        alpha=0.35,
        x_span=None,
        zorder=0.9,
    )
    bias_pts = [(c["x"], c["y"], c["dir"]) for c in case.local_bias if _in_view(c["x"], c["y"])]
    if bias_pts:
        draw_local_bias(ax, bias_pts, step=_bias_arrow_step(case, 4))
    draw_start_target(ax, case.start, case.target)
    if fast_path is not None and fast_path.size:
        draw_channel_path(ax, fast_path, color="#2ca25f", label=None, alpha=0.9, lw=2.0)
    if slow_path is not None and slow_path.size:
        draw_channel_path(ax, slow_path, color="#756bb1", label=None, alpha=0.6, lw=1.8)
    # Boundaries are shown in the overview inset to avoid cluttering the strip view.
    draw_global_bias_axes(
        ax,
        case.g_x,
        case.g_y,
        anchor=(0.04, 0.18),
        length=0.12,
        label_offset=0.04,
        clip_on=False,
    )
    ax.set_xlim(strip_view.x0 - 0.5, strip_view.x1 + 0.5)
    ax.set_ylim(strip_view.y1 + 0.5, strip_view.y0 - 0.5)
    ax.set_aspect("auto")


def _draw_candidate_B_overview(
    ax: plt.Axes,
    case: CaseGeometry,
    *,
    strip_view: ViewBox,
    corridor_halfwidth: int,
    corridor_rows: Sequence[int],
) -> None:
    corridor_rows = _corridor_rows_from_case(case, corridor_rows)
    draw_environment_v13(
        ax,
        case,
        view=None,
        corridor_halfwidth=corridor_halfwidth,
        corridor_rows=corridor_rows,
        bias_step=6,
        show_global_bias=False,
        show_axes_indicator=False,
        use_axes_bias=False,
        show_boundary_box=True,
        boundary_loc="upper left",
        boundary_fontsize=8,
    )
    ax.add_patch(
        Rectangle(
            (strip_view.x0 - 0.5, strip_view.y0 - 0.5),
            strip_view.x1 - strip_view.x0 + 1,
            strip_view.y1 - strip_view.y0 + 1,
            fill=False,
            lw=1.1,
            ec="black",
        )
    )
    ax.set_xticks([])
    ax.set_yticks([])


def draw_environment_v13(
    ax: plt.Axes,
    case: CaseGeometry,
    *,
    view: Optional[ViewBox] = None,
    bias_step: int = 2,
    corridor_halfwidth: int = 1,
    corridor_rows: Sequence[int] | None = None,
    fast_path: np.ndarray | None = None,
    slow_path: np.ndarray | None = None,
    show_global_bias: bool = True,
    aspect: str | None = None,
    show_axes_indicator: bool = True,
    use_axes_bias: bool = False,
    show_boundaries: bool = True,
    bias_anchor: tuple[float, float] = (0.12, 0.30),
    bias_length: float = 0.12,
    bias_label_offset: float = 0.08,
    bias_clip_on: bool = True,
    show_boundary_box: bool = True,
    boundary_loc: str = "upper left",
    boundary_fontsize: int = 9,
    corridor_full_band: bool = False,
) -> None:
    base_aspect = aspect if aspect is not None else "equal"
    draw_base(ax, case.N, view=view, coarse_grid_step=8, aspect=base_aspect)
    if corridor_full_band and case.corridor:
        if corridor_rows:
            y_min = min(corridor_rows)
            y_max = max(corridor_rows)
        else:
            y_min = int(case.corridor["y"]) - corridor_halfwidth
            y_max = int(case.corridor["y"]) + corridor_halfwidth
        x0 = view.x0 if view else 1
        x1 = view.x1 if view else case.N
        # light band across the visible strip to avoid empty background
        if view is not None:
            full_rows = list(range(view.y0, view.y1 + 1))
        else:
            full_rows = [y_min, y_max]
        draw_corridor_band(
            ax,
            case.corridor,
            band_rows=full_rows,
            color="#fdd0a2",
            alpha=0.18,
            x_span=(x0, x1),
            zorder=0.7,
        )
        # highlight corridor segment
        draw_corridor_band(
            ax,
            case.corridor,
            band_rows=[y_min, y_max],
            color="#fdae6b",
            alpha=0.35,
            x_span=None,
            zorder=0.9,
        )
    if not corridor_full_band:
        draw_corridor_band(ax, case.corridor, band_rows=corridor_rows, band_halfwidth=corridor_halfwidth)
    draw_walls(ax, case.barriers_reflect)
    if case.barriers_perm:
        draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1])
    if case.sticky:
        draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
    if show_boundaries:
        draw_boundaries(ax, case, view=view)
    step = _bias_arrow_step(case, bias_step)
    draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=step)
    draw_start_target(ax, case.start, case.target)
    if fast_path is not None:
        draw_channel_path(ax, fast_path, color="#2ca25f", label=None)
    if slow_path is not None:
        draw_channel_path(ax, slow_path, color="#756bb1", label=None)
    if show_axes_indicator:
        if view is None:
            axis_anchor = (2, 2)
        else:
            axis_anchor = (view.x0 + 1, view.y0 + 1)
        draw_axes_indicator(ax, anchor=axis_anchor)
    if show_boundary_box:
        corner_map = {
            "upper left": "NW",
            "upper right": "NE",
            "lower left": "SW",
            "lower right": "SE",
        }
        corner = corner_map.get(boundary_loc.lower(), "NW")
        safe_corner_box(
            ax,
            f"x: {case.boundary_x}\ny: {case.boundary_y}",
            corner=corner,
            fontsize=boundary_fontsize,
        )
    if show_global_bias:
        if use_axes_bias:
            draw_global_bias_axes(
                ax,
                case.g_x,
                case.g_y,
                anchor=bias_anchor,
                length=bias_length,
                label_offset=bias_label_offset,
                clip_on=bias_clip_on,
            )
        elif view is None:
            anchor = (case.N - 7, 4)
            draw_global_bias(ax, case.g_x, case.g_y, anchor=anchor)
        else:
            anchor = (view.x0 + 1, view.y0 + 1)
            draw_global_bias(ax, case.g_x, case.g_y, anchor=anchor)
    if view is not None:
        ax.set_xlim(view.x0 - 0.5, view.x1 + 0.5)
        ax.set_ylim(view.y1 + 0.5, view.y0 - 0.5)
    if aspect:
        ax.set_aspect(aspect)


def _decimate_path(path: np.ndarray, *, step: int = 12) -> np.ndarray:
    if path is None or len(path) == 0:
        return np.array([])
    return path[::step].copy()


def plot_environment_v13(
    case: CaseGeometry,
    *,
    outpath: Path,
    dpi: int = 800,
    corridor_halfwidth: int = 1,
    corridor_rows: Sequence[int] | None = None,
    fast_path: np.ndarray | None = None,
    slow_path: np.ndarray | None = None,
) -> None:
    apply_style_v13()
    fig, ax = plt.subplots(figsize=(6.6, 6.2), constrained_layout=True)
    fast_path = _decimate_path(fast_path, step=12)
    slow_path = _decimate_path(slow_path, step=18)
    draw_environment_v13(
        ax,
        case,
        corridor_halfwidth=corridor_halfwidth,
        corridor_rows=corridor_rows,
        fast_path=fast_path,
        slow_path=slow_path,
    )
    save_clean(fig, outpath, dpi=dpi)


def _draw_candidate_B_env_inset(
    ax: plt.Axes,
    case: CaseGeometry,
    *,
    strip_view: ViewBox | None,
    corridor_halfwidth: int,
    corridor_rows: Sequence[int] | None,
    fast_path: np.ndarray | None = None,
    slow_path: np.ndarray | None = None,
) -> None:
    corridor_rows = _corridor_rows_from_case(case, corridor_rows)
    if strip_view is None:
        strip_view = _candidate_B_strip_view(case, corridor_rows, pad_x=2, pad_y=3, min_width=14, min_height=10)
    _draw_candidate_B_strip(
        ax,
        case,
        strip_view=strip_view,
        corridor_halfwidth=corridor_halfwidth,
        corridor_rows=corridor_rows or [],
        fast_path=fast_path,
        slow_path=None,
    )
    ax.set_xticks([])
    ax.set_yticks([])

    inset = inset_axes(ax, width="26%", height="30%", loc="upper right", borderpad=0.55)
    draw_environment_v13(
        inset,
        case,
        view=None,
        corridor_halfwidth=corridor_halfwidth,
        corridor_rows=corridor_rows,
        bias_step=6,
        fast_path=None,
        slow_path=None,
        show_global_bias=False,
        aspect="equal",
        show_axes_indicator=False,
        use_axes_bias=False,
        show_boundary_box=True,
        boundary_fontsize=7,
        boundary_loc="upper left",
    )
    # Outline the strip ROI inside the overview inset.
    inset.add_patch(
        Rectangle(
            (strip_view.x0 - 0.5, strip_view.y0 - 0.5),
            strip_view.x1 - strip_view.x0 + 1,
            strip_view.y1 - strip_view.y0 + 1,
            fill=False,
            lw=1.0,
            ec="black",
        )
    )
    inset.set_xticks([])
    inset.set_yticks([])
    inset.set_aspect("equal")
    inset.set_title("")


def plot_candidate_B_env_v13(
    case: CaseGeometry,
    *,
    outpath: Path,
    dpi: int = 800,
    corridor_halfwidth: int = 1,
    corridor_rows: Sequence[int] | None = None,
    strip_view: Optional[ViewBox] = None,
    fast_path: np.ndarray | None = None,
    slow_path: np.ndarray | None = None,
) -> None:
    apply_style_v13()
    corridor_rows = _corridor_rows_from_case(case, corridor_rows)
    fast_path = _decimate_path(fast_path, step=12)
    slow_path = _decimate_path(slow_path, step=18)
    if strip_view is None:
        strip_view = _candidate_B_strip_view(case, corridor_rows, pad_x=2, pad_y=2, min_width=14, min_height=6)

    fig, ax = plt.subplots(figsize=(7.4, 4.4), constrained_layout=True)
    fast_line = fast_path if fast_path is not None and fast_path.size else np.array([case.start, case.target])
    _draw_candidate_B_env_inset(
        ax,
        case,
        strip_view=strip_view,
        corridor_halfwidth=corridor_halfwidth,
        corridor_rows=corridor_rows,
        fast_path=fast_line,
        slow_path=None,
    )
    ax.set_title("")
    save_clean(fig, outpath, dpi=dpi)


def plot_symbol_legend_v13(*, outpath: Path, dpi: int = 800) -> None:
    apply_style_v13()
    import matplotlib.lines as mlines
    from matplotlib.patches import Patch

    fig, ax = plt.subplots(figsize=(4.2, 0.9), constrained_layout=False)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.10)
    ax.axis("off")

    handles = [
        mlines.Line2D([], [], color="black", lw=2.6, label="reflecting wall"),
        mlines.Line2D([], [], color="#b30000", lw=2.6, ls=(0, (3, 2)), label="permeable door"),
        Patch(facecolor="#9fb3b5", hatch="///", edgecolor="#6b7a78", label="sticky"),
        mlines.Line2D([], [], color="#d62728", lw=1.4, marker="|", label="local bias"),
        mlines.Line2D([], [], color="#2b2b2b", lw=2.0, label="global bias"),
        mlines.Line2D([], [], color="#2ca25f", lw=2.2, label="fast channel"),
        mlines.Line2D([], [], color="#756bb1", lw=2.2, label="slow channel"),
        mlines.Line2D([], [], color="#e41a1c", marker="s", markersize=8, lw=0, label="start"),
        mlines.Line2D([], [], color="#377eb8", marker="D", markersize=8, lw=0, label="target"),
    ]
    ax.legend(
        handles=handles,
        ncol=3,
        frameon=True,
        loc="center",
        fontsize=9,
        columnspacing=0.6,
        handlelength=1.1,
        handletextpad=0.4,
        borderpad=0.25,
        labelspacing=0.25,
    )
    save_clean(fig, outpath, dpi=dpi)


def plot_fig3_panel_v13(
    case: CaseGeometry,
    *,
    mats: Sequence[np.ndarray],
    times: Sequence[int],
    outpath: Path,
    dpi: int = 800,
    bias_step_env: int = 3,
    bias_step_heat: int = 1,
    corridor_halfwidth: int = 1,
    corridor_rows: Sequence[int] | None = None,
    env_strip: bool = False,
    strip_view: Optional[ViewBox] = None,
    heat_view: Optional[ViewBox] = None,
    fast_path: np.ndarray | None = None,
    slow_path: np.ndarray | None = None,
) -> None:
    apply_style_v13()
    env_strip = bool(env_strip or (case.corridor and case.boundary_y == "reflecting"))
    if env_strip:
        fig = plt.figure(figsize=(11.0, 6.0), constrained_layout=False)
        fig.subplots_adjust(left=0.055, right=0.95, bottom=0.07, top=0.96, wspace=0.12, hspace=0.12)
        gs = fig.add_gridspec(3, 3, width_ratios=[1.25, 1.2, 0.05], wspace=0.12, hspace=0.12)
        ax_env = fig.add_subplot(gs[:, 0])
        ax_heat = [fig.add_subplot(gs[i, 1]) for i in range(3)]
        cax = fig.add_subplot(gs[:, 2])

        corridor_rows = _corridor_rows_from_case(case, corridor_rows)
        if strip_view is None:
            strip_view = _candidate_B_strip_view(case, corridor_rows, pad_x=2, pad_y=4, min_width=16, min_height=10)
        if heat_view is None:
            heat_view = strip_view_full_width(case, corridor_rows, pad_y=8)

        fast_line = np.array([case.start, case.target], dtype=np.int64)
        _draw_candidate_B_env_inset(
            ax_env,
            case,
            strip_view=strip_view,
            corridor_halfwidth=corridor_halfwidth,
            corridor_rows=corridor_rows,
            fast_path=fast_line if fast_path is None or fast_path.size == 0 else _decimate_path(fast_path, step=10),
            slow_path=None,
        )
        ax_env.set_title("")
    else:
        fig = plt.figure(figsize=(11.0, 6.0), constrained_layout=False)
        wspace, hspace = 0.10, 0.12
        fig.subplots_adjust(left=0.055, right=0.95, bottom=0.07, top=0.96, wspace=wspace, hspace=hspace)
        gs = fig.add_gridspec(3, 3, width_ratios=[1.25, 1.2, 0.05], wspace=wspace, hspace=hspace)
        ax_env = fig.add_subplot(gs[:, 0])
        ax_heat = [fig.add_subplot(gs[i, 1]) for i in range(3)]
        cax = fig.add_subplot(gs[:, 2])

        draw_environment_v13(
            ax_env,
            case,
            bias_step=bias_step_env,
            corridor_halfwidth=corridor_halfwidth,
            corridor_rows=corridor_rows,
            fast_path=_decimate_path(fast_path, step=12),
            slow_path=_decimate_path(slow_path, step=18),
        )

    def _in_view(pt: tuple[int, int], view: ViewBox | None) -> bool:
        if view is None:
            return True
        return view.x0 <= pt[0] <= view.x1 and view.y0 <= pt[1] <= view.y1

    if heat_view is not None:
        heat_view = ViewBox(
            max(1, heat_view.x0),
            min(case.N, heat_view.x1),
            max(1, heat_view.y0),
            min(case.N, heat_view.y1),
        )
    mats_use = mats
    if heat_view is not None:
        mats_use = [
            mat[max(0, heat_view.x0 - 1) : min(case.N, heat_view.x1),
                max(0, heat_view.y0 - 1) : min(case.N, heat_view.y1)]
            for mat in mats
        ]
    vmin, vmax = heatmap_limits(mats_use, eps=1e-14, q=1e-4)
    show_overlay = not env_strip
    for ax, mat, t in zip(ax_heat, mats, times):
        plot_log_heatmap_P(ax, mat, N=case.N, vmin=vmin, vmax=vmax, eps=1e-14, view=heat_view)
        ax.set_aspect("auto")
        if _in_view(case.start, heat_view) and _in_view(case.target, heat_view):
            draw_start_target(ax, case.start, case.target)
        avoid_pts = [pt for pt in (case.start, case.target) if _in_view(pt, heat_view)]
        add_time_tag(ax, int(t), avoid_points=avoid_pts)
        if show_overlay and case.local_bias:
            bias_pts = [(c["x"], c["y"], c["dir"]) for c in case.local_bias]
            if heat_view is not None:
                bias_pts = [(x, y, d) for x, y, d in bias_pts if _in_view((x, y), heat_view)]
            draw_local_bias(ax, bias_pts, step=_bias_arrow_step(case, bias_step_heat))
        if show_overlay and case.barriers_reflect:
            walls = case.barriers_reflect
            if heat_view is not None:
                walls = [
                    edge
                    for edge in walls
                    if _in_view(edge[0], heat_view) or _in_view(edge[1], heat_view)
                ]
            draw_walls(ax, walls)
        if show_overlay and case.barriers_perm:
            doors = [edge for edge, _ in case.barriers_perm]
            if heat_view is not None:
                doors = [edge for edge in doors if _in_view(edge[0], heat_view) or _in_view(edge[1], heat_view)]
            draw_door(ax, doors, p_pass=case.barriers_perm[0][1], label=False)
        if show_overlay and case.sticky:
            sticky_pts = [(c["x"], c["y"]) for c in case.sticky]
            if heat_view is not None:
                sticky_pts = [pt for pt in sticky_pts if _in_view(pt, heat_view)]
            draw_sticky(ax, sticky_pts)
    fig.colorbar(ax_heat[0].images[0], cax=cax, label="P(n,t)")

    save_clean(fig, outpath, dpi=dpi)
