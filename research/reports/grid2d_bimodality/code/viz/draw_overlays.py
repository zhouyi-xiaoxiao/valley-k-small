#!/usr/bin/env python3
"""Overlay primitives for lattice schematics and heatmaps."""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle

from model_core import Coord
from .case_data import CaseGeometry


COLOR_START = "#e41a1c"
COLOR_TARGET = "#377eb8"
COLOR_LOCAL_BIAS = "#d62728"
COLOR_GLOBAL_BIAS = "#444444"
COLOR_STICKY = "#bdbdbd"
COLOR_CORRIDOR = "#fdae6b"


def setup_lattice_axes(ax: Axes, N: int, *, show_grid: bool = True, grid_step: int = 5) -> None:
    ax.set_facecolor("white")
    if show_grid:
        for k in range(grid_step, N, grid_step):
            ax.axhline(k + 0.5, color="0.92", lw=0.5, zorder=0)
            ax.axvline(k + 0.5, color="0.92", lw=0.5, zorder=0)
    ax.add_patch(Rectangle((0.5, 0.5), N, N, fill=False, lw=1.2, edgecolor="0.25", zorder=1))
    ax.set_xlim(0.5, N + 0.5)
    ax.set_ylim(0.5, N + 0.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(0, N + 1, 10))
    ax.set_yticks(range(0, N + 1, 10))
    ax.tick_params(labelsize=8)
    ax.invert_yaxis()


def draw_boundaries(ax: Axes, case: CaseGeometry) -> None:
    if case.boundary_x == "reflecting":
        ax.plot([0.5, 0.5], [0.5, case.N + 0.5], color="k", lw=2.8)
        ax.plot([case.N + 0.5, case.N + 0.5], [0.5, case.N + 0.5], color="k", lw=2.8)
    if case.boundary_y == "reflecting":
        ax.plot([0.5, case.N + 0.5], [0.5, 0.5], color="k", lw=2.8)
        ax.plot([0.5, case.N + 0.5], [case.N + 0.5, case.N + 0.5], color="k", lw=2.8)


def draw_periodic_markers(ax: Axes, case: CaseGeometry) -> None:
    if case.boundary_x == "periodic":
        arrow = FancyArrowPatch(
            (0.6, case.N + 1.2),
            (case.N + 0.4, case.N + 1.2),
            connectionstyle="arc3,rad=0.25",
            arrowstyle="-|>",
            lw=1.2,
            color="0.35",
            clip_on=False,
        )
        ax.add_patch(arrow)
        ax.text(case.N / 2, case.N + 1.5, "periodic x", fontsize=8, color="0.35", ha="center")
    if case.boundary_y == "periodic":
        arrow = FancyArrowPatch(
            (case.N + 1.2, 0.6),
            (case.N + 1.2, case.N + 0.4),
            connectionstyle="arc3,rad=0.25",
            arrowstyle="-|>",
            lw=1.2,
            color="0.35",
            clip_on=False,
        )
        ax.add_patch(arrow)
        ax.text(case.N + 1.5, case.N / 2, "periodic y", fontsize=8, color="0.35", rotation=90, va="center")


def draw_global_bias(ax: Axes, case: CaseGeometry) -> None:
    if abs(case.g_x) < 1e-12 and abs(case.g_y) < 1e-12:
        return
    dx = -case.g_x
    dy = case.g_y
    norm = float(np.hypot(dx, dy))
    if norm <= 1e-12:
        return
    dx /= norm
    dy /= norm
    x0, y0 = 1.0, case.N + 2.0
    x1, y1 = x0 + 4.0 * dx, y0 + 4.0 * dy
    arrow = FancyArrowPatch(
        (x0, y0),
        (x1, y1),
        arrowstyle="-|>",
        mutation_scale=18,
        lw=2.0,
        color=COLOR_GLOBAL_BIAS,
        clip_on=False,
    )
    ax.add_patch(arrow)
    ax.text(
        x0,
        y0 + 0.6,
        f"global bias g=({case.g_x:+.2f},{case.g_y:+.2f})",
        fontsize=8,
        color="0.35",
    )


def _edge_segment(edge: Tuple[Coord, Coord]) -> Tuple[List[float], List[float]]:
    (x1, y1), (x2, y2) = edge
    if x1 == x2:
        y = max(y1, y2) - 0.5
        return [x1 - 0.5, x1 + 0.5], [y, y]
    x = max(x1, x2) - 0.5
    return [x, x], [y1 - 0.5, y1 + 0.5]


def draw_barriers(ax: Axes, case: CaseGeometry) -> None:
    for edge in case.barriers_reflect:
        xs, ys = _edge_segment(edge)
        ax.plot(xs, ys, color="k", lw=2.8, zorder=3)
    for edge, p in case.barriers_perm:
        xs, ys = _edge_segment(edge)
        ax.plot(xs, ys, color="k", lw=2.8, ls=(0, (4, 2)), zorder=3)
        mid_x = float(sum(xs)) / 2.0
        mid_y = float(sum(ys)) / 2.0
        ax.text(mid_x, mid_y + 0.6, f"p={p:.2f}", fontsize=8, ha="center", color="0.1")


def draw_sticky(ax: Axes, case: CaseGeometry) -> None:
    if not case.sticky:
        return
    for cell in case.sticky:
        x = int(cell["x"])
        y = int(cell["y"])
        ax.add_patch(
            Rectangle(
                (x - 0.5, y - 0.5),
                1.0,
                1.0,
                facecolor=COLOR_STICKY,
                edgecolor="0.4",
                lw=0.6,
                alpha=0.35,
                hatch="///",
                zorder=2,
            )
        )


def draw_corridor_band(ax: Axes, case: CaseGeometry) -> None:
    if not case.corridor:
        return
    y = int(case.corridor["y"])
    x0 = int(case.corridor["x_start"])
    x1 = int(case.corridor["x_end"])
    ax.add_patch(
        Rectangle(
            (x0 - 0.5, y - 0.8),
            x1 - x0 + 1,
            1.6,
            facecolor=COLOR_CORRIDOR,
            alpha=0.18,
            edgecolor="none",
            zorder=1,
        )
    )


def draw_local_bias(ax: Axes, case: CaseGeometry) -> None:
    for item in case.local_bias:
        x = int(item["x"])
        y = int(item["y"])
        direction = item["dir"]
        dx, dy = 0, 0
        if direction == "left":
            dx = -0.8
        elif direction == "right":
            dx = 0.8
        elif direction == "down":
            dy = 0.8
        elif direction == "up":
            dy = -0.8
        arrow = FancyArrowPatch(
            (x, y),
            (x + dx, y + dy),
            arrowstyle="-|>",
            mutation_scale=12,
            lw=1.8,
            color=COLOR_LOCAL_BIAS,
            zorder=4,
        )
        ax.add_patch(arrow)


def draw_start_target(ax: Axes, case: CaseGeometry) -> None:
    sx, sy = case.start
    tx, ty = case.target
    ax.scatter([sx], [sy], s=80, c=COLOR_START, marker="s", zorder=5, edgecolors="white", linewidths=0.6)
    ax.scatter([tx], [ty], s=80, c=COLOR_TARGET, marker="D", zorder=5, edgecolors="white", linewidths=0.6)


def build_legend_handles(case: CaseGeometry) -> List:
    handles: List = [
        Line2D([0], [0], marker="s", color="w", markerfacecolor=COLOR_START, markersize=8, label="start"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor=COLOR_TARGET, markersize=8, label="target"),
    ]
    if case.local_bias:
        handles.append(Line2D([0], [0], color=COLOR_LOCAL_BIAS, lw=2.0, label=f"local bias (δ={case.local_bias_delta:.2f})"))
    if case.corridor:
        handles.append(Patch(facecolor=COLOR_CORRIDOR, alpha=0.2, label="corridor"))
    if case.barriers_reflect:
        handles.append(Line2D([0], [0], color="k", lw=2.6, label="reflecting wall"))
    if case.barriers_perm:
        handles.append(Line2D([0], [0], color="k", lw=2.6, ls=(0, (4, 2)), label="door (p_pass)"))
    if case.sticky:
        alpha_val = float(case.sticky[0]["factor"]) if case.sticky else 0.0
        handles.append(Patch(facecolor=COLOR_STICKY, alpha=0.35, hatch="///", label=f"sticky (α={alpha_val:.2f})"))
    return handles
