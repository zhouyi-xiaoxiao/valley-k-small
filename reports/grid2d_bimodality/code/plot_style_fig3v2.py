#!/usr/bin/env python3
"""Fig.3-style plotting utilities for v6 (clean + readable)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from viz.case_data import CaseGeometry
from plotting_utils import savefig_clean, savefig_clean_pair


@dataclass(frozen=True)
class ViewBox:
    x0: int
    x1: int
    y0: int
    y1: int


def set_style_fig3v2() -> None:
    """Matplotlib defaults to match Fig.3-like visual language."""
    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "#f7f0e6",
            "axes.edgecolor": "0.2",
            "axes.linewidth": 1.2,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "font.size": 10,
            "lines.linewidth": 1.8,
            "lines.markersize": 4.5,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
            "figure.constrained_layout.use": True,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _save(fig: plt.Figure, outpath: Path, *, dpi: int = 600) -> None:
    if outpath.suffix.lower() == ".png":
        savefig_clean(fig, outpath, dpi=dpi)
    else:
        savefig_clean_pair(fig, outpath.with_suffix(""), dpi=dpi)


def _view_limits(N: int, view: Optional[ViewBox]) -> Tuple[int, int, int, int]:
    if view is None:
        return 1, N, 1, N
    return view.x0, view.x1, view.y0, view.y1


def draw_base(
    ax: plt.Axes,
    N: int,
    *,
    view: Optional[ViewBox] = None,
    coarse_grid_step: int = 5,
    fine_grid: bool = False,
    show_axes: bool = False,
) -> None:
    x0, x1, y0, y1 = _view_limits(N, view)
    ax.set_facecolor("#f7f0e6")

    if coarse_grid_step > 0:
        for k in range(((x0 - 1) // coarse_grid_step + 1) * coarse_grid_step, x1, coarse_grid_step):
            ax.axvline(k + 0.5, color="0.88", lw=0.6, zorder=0)
        for k in range(((y0 - 1) // coarse_grid_step + 1) * coarse_grid_step, y1, coarse_grid_step):
            ax.axhline(k + 0.5, color="0.88", lw=0.6, zorder=0)

    if fine_grid:
        for k in range(x0, x1):
            ax.axvline(k + 0.5, color="0.93", lw=0.4, zorder=0)
        for k in range(y0, y1):
            ax.axhline(k + 0.5, color="0.93", lw=0.4, zorder=0)

    ax.add_patch(Rectangle((x0 - 0.5, y0 - 0.5), x1 - x0 + 1, y1 - y0 + 1, fill=False, lw=1.4))
    ax.set_xlim(x0 - 0.5, x1 + 0.5)
    ax.set_ylim(y0 - 0.5, y1 + 0.5)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    if not show_axes:
        ax.set_xticks([])
        ax.set_yticks([])


def _edge_segment(edge: Tuple[Tuple[int, int], Tuple[int, int]]) -> Tuple[Sequence[float], Sequence[float]]:
    (x1, y1), (x2, y2) = edge
    if x1 == x2:
        y = max(y1, y2) - 0.5
        return [x1 - 0.5, x1 + 0.5], [y, y]
    x = max(x1, x2) - 0.5
    return [x, x], [y1 - 0.5, y1 + 0.5]


def draw_walls(ax: plt.Axes, wall_segments: Sequence[Tuple[Tuple[int, int], Tuple[int, int]]]) -> None:
    for edge in wall_segments:
        xs, ys = _edge_segment(edge)
        ax.plot(xs, ys, color="black", lw=2.6, zorder=5)


def draw_door(
    ax: plt.Axes,
    door_segments: Sequence[Tuple[Tuple[int, int], Tuple[int, int]]],
    *,
    p_pass: float,
    label: bool = True,
) -> None:
    for edge in door_segments:
        xs, ys = _edge_segment(edge)
        ax.plot(xs, ys, color="black", lw=2.8, ls=(0, (3, 2)), zorder=6)
        if label:
            mid_x = float(sum(xs)) / 2.0
            mid_y = float(sum(ys)) / 2.0
            ax.text(
                mid_x + 1.2,
                mid_y - 1.2,
                f"p={p_pass:.2f}",
                fontsize=9,
                color="0.1",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, linewidth=0.0),
            )


def draw_sticky(ax: plt.Axes, sticky_cells: Sequence[Tuple[int, int]]) -> None:
    for x, y in sticky_cells:
        ax.add_patch(
            Rectangle(
                (x - 0.5, y - 0.5),
                1.0,
                1.0,
                facecolor="#9fb3b5",
                edgecolor="#6b7a78",
                lw=0.6,
                alpha=0.35,
                hatch="///",
                zorder=3,
            )
        )


def draw_local_bias(ax: plt.Axes, bias_edges: Sequence[Tuple[int, int, str]], *, step: int = 1) -> None:
    if step < 1:
        step = 1
    for idx, (x, y, direction) in enumerate(bias_edges):
        if idx % step != 0:
            continue
        dx, dy = 0.0, 0.0
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
            lw=1.6,
            color="#d62728",
            zorder=6,
        )
        ax.add_patch(arrow)


def draw_corridor(ax: plt.Axes, corridor: Optional[dict]) -> None:
    if not corridor:
        return
    y = int(corridor["y"])
    x0 = int(corridor["x_start"])
    x1 = int(corridor["x_end"])
    ax.add_patch(
        Rectangle(
            (x0 - 0.5, y - 0.9),
            x1 - x0 + 1,
            1.8,
            facecolor="#fdb462",
            alpha=0.25,
            edgecolor="#b35806",
            lw=1.0,
            zorder=2,
        )
    )


def draw_start_target(ax: plt.Axes, start: Tuple[int, int], target: Tuple[int, int]) -> None:
    ax.scatter([start[0]], [start[1]], s=90, c="#e41a1c", marker="s", edgecolors="black", zorder=7)
    ax.scatter([target[0]], [target[1]], s=90, c="#377eb8", marker="D", edgecolors="black", zorder=7)


def draw_global_bias(ax: plt.Axes, gx: float, gy: float, *, anchor: Tuple[float, float]) -> None:
    if abs(gx) < 1e-12 and abs(gy) < 1e-12:
        return
    dx = -gx
    dy = gy
    norm = float(np.hypot(dx, dy))
    if norm <= 1e-12:
        return
    dx /= norm
    dy /= norm
    x0, y0 = anchor
    x1, y1 = x0 + 4.5 * dx, y0 + 4.5 * dy
    arrow = FancyArrowPatch(
        (x0, y0),
        (x1, y1),
        arrowstyle="-|>",
        mutation_scale=18,
        lw=2.0,
        color="#2b2b2b",
        clip_on=False,
    )
    ax.add_patch(arrow)


def draw_boundaries(ax: plt.Axes, case: CaseGeometry, *, view: Optional[ViewBox]) -> None:
    x0, x1, y0, y1 = _view_limits(case.N, view)
    y_mid = 0.5 * (y0 + y1)
    if case.boundary_x == "periodic":
        ax.annotate(
            "",
            xy=(x0 + 0.4, y_mid),
            xytext=(x0 + 1.4, y_mid),
            arrowprops=dict(arrowstyle="-|>", lw=1.0, color="0.25"),
        )
        ax.annotate(
            "",
            xy=(x1 - 0.4, y_mid),
            xytext=(x1 - 1.4, y_mid),
            arrowprops=dict(arrowstyle="-|>", lw=1.0, color="0.25"),
        )
    if case.boundary_y == "periodic":
        ax.annotate(
            "",
            xy=(0.5 * (x0 + x1), y0 + 0.4),
            xytext=(0.5 * (x0 + x1), y0 + 1.4),
            arrowprops=dict(arrowstyle="-|>", lw=1.0, color="0.25"),
        )
        ax.annotate(
            "",
            xy=(0.5 * (x0 + x1), y1 - 0.4),
            xytext=(0.5 * (x0 + x1), y1 - 1.4),
            arrowprops=dict(arrowstyle="-|>", lw=1.0, color="0.25"),
        )


def anchored_box(ax: plt.Axes, text: str, *, loc: str = "upper left", fontsize: int = 9) -> None:
    at = AnchoredText(text, loc=loc, prop=dict(size=fontsize), frameon=True, pad=0.2, borderpad=0.3)
    at.patch.set_alpha(0.85)
    at.patch.set_facecolor("white")
    at.patch.set_edgecolor("0.7")
    ax.add_artist(at)


def add_info_boxes(ax: plt.Axes, case: CaseGeometry) -> None:
    boundary_text = f"x: {case.boundary_x}\\ny: {case.boundary_y}"
    anchored_box(ax, boundary_text, loc="upper left", fontsize=9)
    if abs(case.g_x) > 1e-12 or abs(case.g_y) > 1e-12:
        anchored_box(ax, f"g=({case.g_x:.2f},{case.g_y:.2f})", loc="upper right", fontsize=9)


def compute_roi(case: CaseGeometry, *, margin: int = 6, include_barriers: bool = True) -> ViewBox:
    xs = [case.start[0], case.target[0]]
    ys = [case.start[1], case.target[1]]
    for item in case.local_bias:
        xs.append(int(item["x"]))
        ys.append(int(item["y"]))
    for item in case.sticky:
        xs.append(int(item["x"]))
        ys.append(int(item["y"]))
    if case.corridor:
        xs.extend([int(case.corridor["x_start"]), int(case.corridor["x_end"])])
        ys.append(int(case.corridor["y"]))
    if include_barriers:
        for edge in case.barriers_reflect:
            xs.extend([edge[0][0], edge[1][0]])
            ys.extend([edge[0][1], edge[1][1]])
    for (edge, _) in case.barriers_perm:
        xs.extend([edge[0][0], edge[1][0]])
        ys.extend([edge[0][1], edge[1][1]])

    x0 = max(1, min(xs) - margin)
    x1 = min(case.N, max(xs) + margin)
    y0 = max(1, min(ys) - margin)
    y1 = min(case.N, max(ys) + margin)
    return ViewBox(x0, x1, y0, y1)


def draw_environment(
    ax: plt.Axes,
    case: CaseGeometry,
    *,
    view: Optional[ViewBox] = None,
    show_grid: bool = True,
    show_global_bias: bool = True,
    show_boundaries: bool = True,
) -> None:
    draw_base(ax, case.N, view=view, coarse_grid_step=5 if show_grid else 0)
    draw_corridor(ax, case.corridor)
    draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
    draw_walls(ax, case.barriers_reflect)
    if case.barriers_perm:
        draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1])
    draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
    draw_start_target(ax, case.start, case.target)
    if show_global_bias:
        x0, x1, y0, y1 = _view_limits(case.N, view)
        draw_global_bias(ax, case.g_x, case.g_y, anchor=(x0 + 2.0, y1 - 2.0))
    if show_boundaries:
        draw_boundaries(ax, case, view=view)


def plot_environment(
    case: CaseGeometry,
    *,
    outpath: Path,
    view: Optional[ViewBox] = None,
    roi: Optional[ViewBox] = None,
    dpi: int = 600,
) -> None:
    set_style_fig3v2()
    fig, ax = plt.subplots(figsize=(8.0, 6.2))
    draw_environment(ax, case, view=view)
    add_info_boxes(ax, case)
    if roi is not None and (roi.x0 > 1 or roi.y0 > 1 or roi.x1 < case.N or roi.y1 < case.N):
        inset = inset_axes(ax, width="40%", height="40%", loc="lower right", borderpad=1.2)
        draw_environment(inset, case, view=roi, show_grid=False, show_global_bias=False, show_boundaries=False)
        draw_base(inset, case.N, view=roi, coarse_grid_step=1, fine_grid=True)
        anchored_box(inset, "zoom", loc="upper right", fontsize=8)
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def _quantile_vmin(mats: Sequence[np.ndarray], q: float, floor: float) -> float:
    vals = np.concatenate([m[m > 0] for m in mats if np.any(m > 0)])
    if vals.size == 0:
        return floor
    return max(float(np.quantile(vals, q)), floor)


def _plot_heat(ax: plt.Axes, P: np.ndarray, norm: LogNorm, N: int) -> None:
    cmap = plt.get_cmap("magma").copy()
    cmap.set_bad("#f7f0e6")
    ax.imshow(
        np.ma.masked_where(P <= 0, P).T,
        origin="lower",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
        extent=(0.5, N + 0.5, 0.5, N + 0.5),
    )
    ax.set_facecolor("#f7f0e6")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    ax.invert_yaxis()


def plot_fig3_panel(
    case: CaseGeometry,
    *,
    mats: Sequence[np.ndarray],
    times: Sequence[int],
    outpath: Path,
    dpi: int = 600,
) -> None:
    set_style_fig3v2()
    fig = plt.figure(figsize=(12.0, 8.4), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.05, 1.0, 0.05], height_ratios=[1.0, 1.0], wspace=0.05)

    ax_env = fig.add_subplot(gs[0, 0])
    draw_environment(ax_env, case)
    add_info_boxes(ax_env, case)

    vmin = _quantile_vmin(mats, q=0.01, floor=1e-14)
    vmax = max(float(np.max(m)) for m in mats)
    norm = LogNorm(vmin=vmin, vmax=vmax)

    ax_h1 = fig.add_subplot(gs[0, 1])
    ax_h2 = fig.add_subplot(gs[1, 0])
    ax_h3 = fig.add_subplot(gs[1, 1])
    cax = fig.add_subplot(gs[:, 2])

    for ax, P, t in zip([ax_h1, ax_h2, ax_h3], mats, times):
        _plot_heat(ax, P, norm, case.N)
        draw_walls(ax, case.barriers_reflect)
        if case.barriers_perm:
            draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1])
        draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
        draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
        draw_start_target(ax, case.start, case.target)
        ax.text(
            0.95,
            0.06,
            f"t={t}",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=10,
            color="white",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="black", alpha=0.35, linewidth=0.0),
        )

    cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap="magma"), cax=cax)
    cb.ax.tick_params(labelsize=8)
    cb.set_label("P(n,t)", fontsize=9)

    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def plot_heatmap_triplet(
    case: CaseGeometry,
    *,
    mats: Sequence[np.ndarray],
    times: Sequence[int],
    outpath: Path,
    dpi: int = 600,
) -> None:
    set_style_fig3v2()
    fig = plt.figure(figsize=(10.8, 3.4), constrained_layout=True)
    gs = fig.add_gridspec(1, 4, width_ratios=[1.0, 1.0, 1.0, 0.05], wspace=0.05)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    cax = fig.add_subplot(gs[0, 3])
    vmin = _quantile_vmin(mats, q=0.01, floor=1e-14)
    vmax = max(float(np.max(m)) for m in mats)
    norm = LogNorm(vmin=vmin, vmax=vmax)

    for ax, P, t in zip(axes, mats, times):
        _plot_heat(ax, P, norm, case.N)
        draw_walls(ax, case.barriers_reflect)
        if case.barriers_perm:
            draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1])
        draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
        draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
        draw_start_target(ax, case.start, case.target)
        ax.text(
            0.94,
            0.08,
            f"t={t}",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=10,
            color="white",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="black", alpha=0.35, linewidth=0.0),
        )

    cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap="magma"), cax=cax)
    cb.ax.tick_params(labelsize=8)
    cb.set_label("P(n,t)", fontsize=9)
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def plot_periodic_unwrapped_two_tiles(case: CaseGeometry, *, outpath: Path, dpi: int = 600) -> None:
    set_style_fig3v2()
    N = case.N
    fig, ax = plt.subplots(figsize=(12.0, 4.6))
    draw_base(ax, 2 * N, view=ViewBox(1, 2 * N, 1, N), coarse_grid_step=10)

    for tile in [0, 1]:
        offset = tile * N
        walls = [((a[0] + offset, a[1]), (b[0] + offset, b[1])) for a, b in case.barriers_reflect]
        draw_walls(ax, walls)
        if case.barriers_perm:
            doors = [
                ((a[0] + offset, a[1]), (b[0] + offset, b[1]))
                for a, b in [edge for edge, _ in case.barriers_perm]
            ]
            draw_door(ax, doors, p_pass=case.barriers_perm[0][1], label=False)
        draw_sticky(ax, [(c["x"] + offset, c["y"]) for c in case.sticky])
        draw_local_bias(ax, [(c["x"] + offset, c["y"], c["dir"]) for c in case.local_bias], step=3)

    sx, sy = case.start
    tx, ty = case.target
    draw_start_target(ax, (sx, sy), (tx, ty))
    ax.scatter([tx + N], [ty], s=90, c="#377eb8", marker="D", edgecolors="black", zorder=7)

    ax.axvline(N + 0.5, color="0.2", lw=1.0)

    delta = (tx - sx) % N
    short = min(delta, N - delta)
    wrap = max(delta, N - delta)
    if delta <= N - delta:
        target_short = tx
        target_wrap = tx + N
    else:
        target_short = tx + N
        target_wrap = tx

    y_short = max(2.0, min(float(N) - 2.0, 0.78 * float(N)))
    y_wrap = max(2.0, min(float(N) - 2.0, 0.60 * float(N)))
    if abs(y_short - y_wrap) < 12.0:
        y_wrap = max(2.0, y_short - 14.0)

    ax.annotate(
        "",
        xy=(target_short, y_short),
        xytext=(sx, y_short),
        arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#2ca25f"),
        clip_on=True,
    )
    ax.annotate(
        "",
        xy=(target_wrap, y_wrap),
        xytext=(sx, y_wrap),
        arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#756bb1"),
        clip_on=True,
    )
    def _shift_if_close(x_val: float, avoid: float, delta: float = 0.15 * float(N)) -> float:
        if abs(x_val - avoid) < delta:
            return x_val + (delta if x_val < avoid else -delta)
        return x_val

    x_mid_short = sx + 0.5 * (target_short - sx)
    x_mid_wrap = sx + 0.5 * (target_wrap - sx)
    for avoid in (sx, tx, tx + N):
        x_mid_short = _shift_if_close(x_mid_short, avoid)
        x_mid_wrap = _shift_if_close(x_mid_wrap, avoid)
    y_offset = max(2.0, 0.06 * float(N))
    y_short_label = min(float(N) - 1.5, y_short + y_offset)
    y_wrap_label = max(1.5, y_wrap - y_offset)
    ax.text(
        x_mid_short,
        y_short_label,
        "Dx_short",
        ha="center",
        va="bottom",
        color="#2ca25f",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.9, linewidth=0.0),
        zorder=8,
    )
    ax.text(
        x_mid_wrap,
        y_wrap_label,
        "Dx_wrap",
        ha="center",
        va="top",
        color="#756bb1",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.9, linewidth=0.0),
        zorder=8,
    )

    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def _path_density(paths: Sequence[np.ndarray], N: int) -> np.ndarray:
    density = np.zeros((N, N), dtype=np.float64)
    for path in paths:
        if path.size == 0:
            continue
        for x, y in path:
            if 1 <= x <= N and 1 <= y <= N:
                density[x - 1, y - 1] += 1.0
    return density


def _plot_density(ax: plt.Axes, density: np.ndarray, N: int) -> None:
    if np.all(density == 0):
        ax.text(0.5, 0.5, "no paths", transform=ax.transAxes, ha="center", va="center")
        return
    scaled = np.log1p(density)
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


def _plot_rep_path(ax: plt.Axes, path: np.ndarray, *, color: str = "#fdae61") -> None:
    if path.size == 0:
        return
    xs = path[:, 0]
    ys = path[:, 1]
    ax.plot(xs, ys, color=color, lw=2.2, zorder=7)
    if len(xs) > 1:
        ax.annotate(
            "",
            xy=(xs[-1], ys[-1]),
            xytext=(xs[-2], ys[-2]),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6),
        )


def plot_paths_density(
    case: CaseGeometry,
    *,
    paths: Sequence[np.ndarray],
    rep_path: np.ndarray,
    event_points: Sequence[Tuple[int, int, str]] | None,
    outpath: Path,
    title: str,
    dpi: int = 600,
) -> None:
    set_style_fig3v2()
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.2))
    roi = compute_roi(case, include_barriers=False)

    density = _path_density(paths, case.N)

    _plot_density(axes[0], density, case.N)
    draw_walls(axes[0], case.barriers_reflect)
    if case.barriers_perm:
        draw_door(axes[0], [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1])
    draw_sticky(axes[0], [(c["x"], c["y"]) for c in case.sticky])
    draw_local_bias(axes[0], [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
    draw_start_target(axes[0], case.start, case.target)
    _plot_rep_path(axes[0], rep_path)
    axes[0].set_title("full domain")

    _plot_density(axes[1], density, case.N)
    draw_walls(axes[1], case.barriers_reflect)
    if case.barriers_perm:
        draw_door(axes[1], [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1])
    draw_sticky(axes[1], [(c["x"], c["y"]) for c in case.sticky])
    draw_local_bias(axes[1], [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
    draw_start_target(axes[1], case.start, case.target)
    _plot_rep_path(axes[1], rep_path)
    axes[1].set_xlim(roi.x0 - 0.5, roi.x1 + 0.5)
    axes[1].set_ylim(roi.y0 - 0.5, roi.y1 + 0.5)
    axes[1].invert_yaxis()
    axes[1].set_title("ROI zoom")

    if event_points:
        for x, y, label in event_points:
            axes[0].scatter([x], [y], s=45, c="#ff7f00", marker="o", edgecolors="black", zorder=8)
            axes[1].scatter([x], [y], s=45, c="#ff7f00", marker="o", edgecolors="black", zorder=8)
            axes[1].text(x + 0.6, y + 0.6, label, fontsize=9, color="#5f3d00")

    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def plot_fpt_multiscale(
    *,
    t_exact: np.ndarray,
    f_exact: np.ndarray,
    t_aw: np.ndarray,
    f_aw: np.ndarray,
    mc_centers: np.ndarray,
    mc_pmf: np.ndarray,
    peaks: Tuple[int, int, int],
    outpath: Path,
    log_eps: float,
    dpi: int = 600,
) -> None:
    set_style_fig3v2()
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.2))
    t1, tv, t2 = peaks

    def _plot(ax: plt.Axes, xlim: Tuple[int, int], logy: bool) -> None:
        if logy:
            f_exact_plot = np.where(f_exact > log_eps, f_exact, np.nan)
            f_aw_plot = np.where(f_aw > log_eps, f_aw, np.nan) if f_aw.size else f_aw
            mc_plot = np.where(mc_pmf > log_eps, mc_pmf, np.nan)
        else:
            f_exact_plot = f_exact
            f_aw_plot = f_aw
            mc_plot = mc_pmf
        ax.plot(t_exact, f_exact_plot, color="black", lw=1.9, label="Exact")
        if f_aw.size:
            ax.plot(t_aw, f_aw_plot, color="#d95f02", lw=1.7, ls="--", label="AW")
        ax.plot(mc_centers, mc_plot, color="#1f78b4", lw=1.2, marker="o", ms=3.0, alpha=0.8, label="MC")
        ax.set_xlim(xlim)
        ax.set_xlabel("t")
        ax.set_ylabel("f(t)")
        if logy:
            ax.set_yscale("log")
            positive = f_exact[f_exact > 0]
            y_min = max(log_eps, float(np.min(positive)) if positive.size else log_eps)
            ax.set_ylim(y_min, float(np.max(f_exact)) * 1.2)
        for t_mark, lab, col in [(t1, "t1", "#2ca25f"), (tv, "tv", "#636363"), (t2, "t2", "#756bb1")]:
            if xlim[0] <= t_mark <= xlim[1]:
                ax.axvline(t_mark, color=col, lw=1.0, ls=":")
                ax.annotate(
                    lab,
                    xy=(t_mark, 0.9),
                    xycoords=("data", "axes fraction"),
                    ha="left",
                    va="center",
                    fontsize=8,
                    color=col,
                    clip_on=True,
                )

    t_max = int(t_exact[-1])
    fast_max = min(t_max, max(t1 + 40, int(0.35 * max(1, tv))))
    slow_min = max(1, int(max(tv - 0.25 * max(1, t2 - tv), 1)))
    slow_max = min(t_max, int(t2 + 0.25 * max(1, t2 - tv)))

    _plot(axes[0], (1, t_max), logy=True)
    axes[0].set_title("global (log-y)")

    _plot(axes[1], (1, fast_max), logy=False)
    axes[1].set_title("fast peak window")

    _plot(axes[2], (slow_min, slow_max), logy=False)
    axes[2].set_title("slow peak window")

    axes[0].legend(frameon=False, loc="upper right")
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def plot_channel_decomp(
    *,
    t: np.ndarray,
    f_fast: np.ndarray,
    f_slow: np.ndarray,
    p_fast: float,
    p_slow: float,
    outpath: Path,
    dpi: int = 600,
) -> None:
    set_style_fig3v2()
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    f_mix = p_fast * f_fast + p_slow * f_slow
    ax.fill_between(t, p_fast * f_fast, color="#fdae61", alpha=0.35, label=f"fast (P={p_fast:.2f})")
    ax.fill_between(t, p_slow * f_slow, color="#66c2a5", alpha=0.35, label=f"slow (P={p_slow:.2f})")
    ax.plot(t, f_mix, color="black", lw=1.8, label="mixture")
    ax.set_xlabel("t")
    ax.set_ylabel("weighted f(t)")
    ax.set_title("Channel mixture")
    ax.legend(frameon=False, loc="upper right")
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def plot_scan(
    *,
    xs: Sequence[int],
    h2_over_h1: Sequence[float],
    hv_over_max: Sequence[float],
    xmin_label: int,
    outpath: Path,
    xlabel: str,
    title: str,
    dpi: int = 600,
) -> None:
    set_style_fig3v2()
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.6))
    ax = axes[0]
    ax.plot(xs, h2_over_h1, "o-", color="#2171b5", lw=1.8, ms=4)
    ax.axhline(0.01, color="0.4", ls="--", lw=1.0)
    if xmin_label in xs:
        ax.axvline(xmin_label, color="#ef3b2c", ls=":", lw=1.2)
        ax.annotate("min", xy=(xmin_label, 0.012), xycoords="data", fontsize=9, color="#ef3b2c")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("h2/h1")

    ax = axes[1]
    ax.plot(xs, hv_over_max, "o-", color="#6a51a3", lw=1.8, ms=4)
    if xmin_label in xs:
        ax.axvline(xmin_label, color="#ef3b2c", ls=":", lw=1.2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("hv/max(h1,h2)")

    fig.suptitle(title)
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def plot_symbol_legend(*, outpath: Path, dpi: int = 600) -> None:
    set_style_fig3v2()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    fig.set_constrained_layout(False)
    ax.axis("off")
    handles = [
        Line2D([0], [0], color="black", lw=2.6, label="reflecting wall"),
        Line2D([0], [0], color="black", lw=2.6, ls=(0, (3, 2)), label="door (p_pass)"),
        Patch(facecolor="#9fb3b5", edgecolor="#6b7a78", hatch="///", alpha=0.35, label="sticky"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#e41a1c", markeredgecolor="black", markersize=9, label="start"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#377eb8", markeredgecolor="black", markersize=9, label="target"),
        Line2D([0], [0], color="#d62728", lw=1.6, marker=">", markersize=8, label="local bias"),
        Patch(facecolor="#fdb462", edgecolor="#b35806", alpha=0.25, label="corridor"),
    ]
    ax.legend(handles=handles, ncol=2, frameon=False, loc="center")
    ax.annotate(
        "global bias",
        xy=(0.12, 0.22),
        xytext=(0.05, 0.22),
        xycoords="axes fraction",
        textcoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", lw=1.6, color="0.25"),
        fontsize=9,
        color="0.25",
    )
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def plot_cartoon_channels(*, outpath: Path, dpi: int = 600) -> None:
    set_style_fig3v2()
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    fig.set_constrained_layout(False)
    ax.set_facecolor("white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.scatter([1], [3], s=120, c="#e41a1c", marker="s", edgecolors="black", zorder=5)
    ax.scatter([9], [3], s=120, c="#377eb8", marker="D", edgecolors="black", zorder=5)
    ax.text(0.8, 2.2, "start", fontsize=9)
    ax.text(8.6, 2.2, "target", fontsize=9)

    ax.plot([1, 9], [3, 3], color="#2ca25f", lw=3.0)
    ax.text(4.6, 3.4, "fast", color="#2ca25f", fontsize=10)

    ax.plot([1, 3, 5, 7, 9], [3, 5, 1, 5, 3], color="#756bb1", lw=3.0)
    ax.text(4.2, 5.2, "slow", color="#756bb1", fontsize=10)

    ax.text(2.8, 1.0, "t_fast << t_slow", fontsize=10)
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def write_gallery_html(fig_root: Path) -> None:
    items = []
    for path in sorted(fig_root.rglob("*.png")):
        rel = path.relative_to(fig_root)
        items.append((rel.as_posix(), rel.stem))

    title = fig_root.name
    html_lines = [
        "<!doctype html>",
        f"<html><head><meta charset='utf-8'><title>{title} gallery</title>",
        "<style>body{font-family:Arial,Helvetica,sans-serif;} .item{margin:12px 0;} img{max-width:480px;border:1px solid #ccc;}</style>",
        "</head><body>",
        f"<h1>{title} gallery</h1>",
    ]
    for rel, title in items:
        html_lines.append(f"<div class='item'><div><code>{rel}</code></div><img src='{rel}' alt='{title}'></div>")
    html_lines.append("</body></html>")

    (fig_root / "gallery.html").write_text("\n".join(html_lines), encoding="utf-8")
