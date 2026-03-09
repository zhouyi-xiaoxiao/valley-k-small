#!/usr/bin/env python3
"""Fig.3-style plotting utilities for v5 figures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

from .case_data import CaseGeometry


@dataclass(frozen=True)
class ViewBox:
    x0: int
    x1: int
    y0: int
    y1: int


def setup_mpl() -> None:
    """Paper-style mpl defaults with larger fonts and clean output."""
    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "0.2",
            "axes.linewidth": 1.0,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "font.size": 11,
            "lines.linewidth": 1.8,
            "lines.markersize": 4.5,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _save(fig: plt.Figure, outpath: str, *, dpi: int = 300) -> None:
    fig.savefig(outpath, dpi=dpi)
    if not outpath.endswith(".png"):
        fig.savefig(outpath.replace(".pdf", ".png"), dpi=dpi)


def draw_base(
    ax: plt.Axes,
    N: int,
    *,
    view: Optional[ViewBox] = None,
    coarse_grid_step: int = 5,
    fine_grid: bool = False,
) -> None:
    ax.set_facecolor("white")
    x0 = view.x0 if view else 1
    x1 = view.x1 if view else N
    y0 = view.y0 if view else 1
    y1 = view.y1 if view else N

    if coarse_grid_step > 0:
        for k in range(((x0 - 1) // coarse_grid_step + 1) * coarse_grid_step, x1, coarse_grid_step):
            ax.axvline(k + 0.5, color="0.90", lw=0.6, zorder=0)
        for k in range(((y0 - 1) // coarse_grid_step + 1) * coarse_grid_step, y1, coarse_grid_step):
            ax.axhline(k + 0.5, color="0.90", lw=0.6, zorder=0)

    if fine_grid:
        for k in range(x0, x1):
            ax.axvline(k + 0.5, color="0.95", lw=0.4, zorder=0)
        for k in range(y0, y1):
            ax.axhline(k + 0.5, color="0.95", lw=0.4, zorder=0)

    ax.add_patch(Rectangle((x0 - 0.5, y0 - 0.5), x1 - x0 + 1, y1 - y0 + 1, fill=False, lw=1.2, edgecolor="0.2"))
    ax.set_xlim(x0 - 0.5, x1 + 0.5)
    ax.set_ylim(y0 - 0.5, y1 + 0.5)
    ax.set_aspect("equal")
    ax.invert_yaxis()


def _edge_segment(edge: Tuple[Tuple[int, int], Tuple[int, int]]) -> Tuple[List[float], List[float]]:
    (x1, y1), (x2, y2) = edge
    if x1 == x2:
        y = max(y1, y2) - 0.5
        return [x1 - 0.5, x1 + 0.5], [y, y]
    x = max(x1, x2) - 0.5
    return [x, x], [y1 - 0.5, y1 + 0.5]


def draw_walls(ax: plt.Axes, wall_segments: Sequence[Tuple[Tuple[int, int], Tuple[int, int]]]) -> None:
    for edge in wall_segments:
        xs, ys = _edge_segment(edge)
        ax.plot(xs, ys, color="k", lw=2.8, zorder=4)


def draw_door(
    ax: plt.Axes,
    door_segments: Sequence[Tuple[Tuple[int, int], Tuple[int, int]]],
    *,
    p_pass: float,
) -> None:
    for edge in door_segments:
        xs, ys = _edge_segment(edge)
        ax.plot(xs, ys, color="#d95f0e", lw=3.0, ls=(0, (4, 2)), zorder=5)
        mid_x = float(sum(xs)) / 2.0
        mid_y = float(sum(ys)) / 2.0
        ax.annotate(
            f"p={p_pass:.2f}",
            xy=(mid_x, mid_y),
            xytext=(mid_x + 1.5, mid_y - 1.5),
            textcoords="data",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7, linewidth=0.0),
            arrowprops=dict(arrowstyle="->", color="0.2", lw=0.8),
        )


def draw_sticky(ax: plt.Axes, sticky_cells: Sequence[Tuple[int, int]], *, alpha: float = 0.25) -> None:
    for x, y in sticky_cells:
        ax.add_patch(
            Rectangle(
                (x - 0.5, y - 0.5),
                1.0,
                1.0,
                facecolor="#bdbdbd",
                edgecolor="0.5",
                lw=0.6,
                alpha=alpha,
                hatch="///",
                zorder=3,
            )
        )


def draw_local_bias(
    ax: plt.Axes,
    bias_edges: Sequence[Tuple[int, int, str]],
    *,
    step: int = 1,
) -> None:
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
            lw=1.8,
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
            (x0 - 0.5, y - 0.8),
            x1 - x0 + 1,
            1.6,
            facecolor="#fdae6b",
            alpha=0.25,
            edgecolor="#f16913",
            lw=1.0,
            zorder=2,
        )
    )


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
    x1, y1 = x0 + 4.0 * dx, y0 + 4.0 * dy
    arrow = FancyArrowPatch(
        (x0, y0),
        (x1, y1),
        arrowstyle="-|>",
        mutation_scale=18,
        lw=2.2,
        color="#333333",
        clip_on=False,
    )
    ax.add_patch(arrow)
    ax.text(x0, y0 + 0.6, f"g=({gx:+.2f},{gy:+.2f})", fontsize=9, color="0.35")


def draw_boundaries(ax: plt.Axes, *, bc_x: str, bc_y: str, N: int) -> None:
    if bc_x == "periodic":
        arrow = FancyArrowPatch(
            (0.6, N + 1.2),
            (N + 0.4, N + 1.2),
            connectionstyle="arc3,rad=0.25",
            arrowstyle="-|>",
            lw=1.4,
            color="0.35",
            clip_on=False,
        )
        ax.add_patch(arrow)
        ax.text(N / 2, N + 1.6, "periodic x", fontsize=9, color="0.35", ha="center")
    if bc_y == "periodic":
        arrow = FancyArrowPatch(
            (N + 1.2, 0.6),
            (N + 1.2, N + 0.4),
            connectionstyle="arc3,rad=0.25",
            arrowstyle="-|>",
            lw=1.4,
            color="0.35",
            clip_on=False,
        )
        ax.add_patch(arrow)
        ax.text(N + 1.6, N / 2, "periodic y", fontsize=9, color="0.35", rotation=90, va="center")

    if bc_x == "reflecting":
        ax.plot([0.5, 0.5], [0.5, N + 0.5], color="k", lw=3.0, zorder=4)
        ax.plot([N + 0.5, N + 0.5], [0.5, N + 0.5], color="k", lw=3.0, zorder=4)
    if bc_y == "reflecting":
        ax.plot([0.5, N + 0.5], [0.5, 0.5], color="k", lw=3.0, zorder=4)
        ax.plot([0.5, N + 0.5], [N + 0.5, N + 0.5], color="k", lw=3.0, zorder=4)


def draw_start_target(
    ax: plt.Axes,
    start: Tuple[int, int],
    target: Tuple[int, int],
    *,
    annotate: bool = True,
) -> None:
    sx, sy = start
    tx, ty = target
    ax.scatter([sx], [sy], s=90, c="#e41a1c", marker="s", zorder=7, edgecolors="white", linewidths=0.6)
    ax.scatter([tx], [ty], s=90, c="#377eb8", marker="D", zorder=7, edgecolors="white", linewidths=0.6)
    if annotate:
        ax.annotate("start", xy=(sx, sy), xytext=(sx + 1.5, sy + 1.5), fontsize=9,
                    arrowprops=dict(arrowstyle="->", lw=0.8, color="0.3"), color="0.2")
        ax.annotate("target", xy=(tx, ty), xytext=(tx + 1.5, ty - 1.5), fontsize=9,
                    arrowprops=dict(arrowstyle="->", lw=0.8, color="0.3"), color="0.2")


def legend_handles(case: CaseGeometry) -> List:
    handles: List = [
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#e41a1c", markersize=8, label="start"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#377eb8", markersize=8, label="target"),
    ]
    if case.local_bias:
        handles.append(Line2D([0], [0], color="#d62728", lw=2.0, label=f"local bias (δ={case.local_bias_delta:.2f})"))
    if case.corridor:
        handles.append(Patch(facecolor="#fdae6b", alpha=0.25, edgecolor="#f16913", label="corridor"))
    if case.barriers_reflect:
        handles.append(Line2D([0], [0], color="k", lw=2.8, label="reflecting wall"))
    if case.barriers_perm:
        handles.append(Line2D([0], [0], color="#d95f0e", lw=2.8, ls=(0, (4, 2)), label="door (p_pass)"))
    if case.sticky:
        alpha_val = float(case.sticky[0]["factor"]) if case.sticky else 0.0
        handles.append(Patch(facecolor="#bdbdbd", alpha=0.25, hatch="///", label=f"sticky (α={alpha_val:.2f})"))
    return handles


def plot_symbol_legend(case: CaseGeometry, *, outpath: str, dpi: int) -> None:
    setup_mpl()
    fig, ax = plt.subplots(figsize=(8.0, 1.8), constrained_layout=True)
    ax.axis("off")
    handles = legend_handles(case)
    ax.legend(handles=handles, ncol=3, frameon=False, loc="center", handlelength=1.6, columnspacing=1.2)
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def _turning_points(path: np.ndarray) -> np.ndarray:
    if path.shape[0] <= 2:
        return path
    pts = [path[0]]
    prev = path[1] - path[0]
    for i in range(2, path.shape[0]):
        cur = path[i] - path[i - 1]
        if not np.array_equal(cur, prev):
            pts.append(path[i - 1])
        prev = cur
    pts.append(path[-1])
    return np.asarray(pts)


def draw_paths(
    ax: plt.Axes,
    paths: Sequence[np.ndarray],
    *,
    mode: str = "turning",
    subsample: int = 5,
    max_steps: Optional[int] = None,
    alpha: float = 0.08,
    color: str = "#2c7fb8",
    gradient_cmap: str = "viridis",
) -> None:
    for path in paths:
        if path.size == 0:
            continue
        pts = path
        if max_steps is not None and pts.shape[0] > max_steps:
            pts = pts[:max_steps]
        if mode == "turning":
            pts = _turning_points(pts)
        elif mode == "subsample" and subsample > 1:
            pts = pts[::subsample]
        if pts.shape[0] < 2:
            continue
        if mode == "gradient":
            segments = np.stack([pts[:-1], pts[1:]], axis=1)
            lc = LineCollection(segments, cmap=gradient_cmap, linewidths=1.2, alpha=alpha)
            lc.set_array(np.linspace(0, 1, segments.shape[0]))
            ax.add_collection(lc)
        else:
            ax.plot(pts[:, 0], pts[:, 1], color=color, alpha=alpha, lw=1.2)


def draw_rep_path(
    ax: plt.Axes,
    path: np.ndarray,
    *,
    color: str = "#fdae61",
    lw: float = 2.6,
    arrow_every: int = 15,
    label: Optional[str] = None,
) -> None:
    if path.size == 0:
        return
    ax.plot(path[:, 0], path[:, 1], color=color, lw=lw, alpha=0.95, label=label, zorder=6)
    for i in range(0, max(path.shape[0] - 1, 1), arrow_every):
        if i + 1 >= path.shape[0]:
            break
        x0, y0 = path[i]
        x1, y1 = path[i + 1]
        if x0 == x1 and y0 == y1:
            continue
        arrow = FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle="-|>",
            mutation_scale=10,
            lw=lw * 0.6,
            color=color,
            alpha=0.95,
        )
        ax.add_patch(arrow)


def plot_environment(
    case: CaseGeometry,
    *,
    outpath: str,
    view: Optional[ViewBox],
    view_roi: Optional[ViewBox],
    dpi: int,
) -> None:
    setup_mpl()
    fig, ax = plt.subplots(figsize=(8.5, 7.5), constrained_layout=True)
    draw_base(ax, case.N, view=view, coarse_grid_step=5)
    draw_boundaries(ax, bc_x=case.boundary_x, bc_y=case.boundary_y, N=case.N)
    draw_corridor(ax, case.corridor)
    draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
    draw_walls(ax, case.barriers_reflect)
    draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1] if case.barriers_perm else 0.0)
    draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
    draw_start_target(ax, case.start, case.target, annotate=True)
    draw_global_bias(ax, case.g_x, case.g_y, anchor=(1.0, case.N + 2.0))

    if view_roi is not None:
        inset = inset_axes(ax, width="38%", height="38%", loc="upper right", borderpad=1.2)
        draw_base(inset, case.N, view=view_roi, coarse_grid_step=1, fine_grid=True)
        draw_boundaries(inset, bc_x=case.boundary_x, bc_y=case.boundary_y, N=case.N)
        draw_corridor(inset, case.corridor)
        draw_sticky(inset, [(c["x"], c["y"]) for c in case.sticky])
        draw_walls(inset, case.barriers_reflect)
        if case.barriers_perm:
            draw_door(inset, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1])
        draw_local_bias(inset, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
        draw_start_target(inset, case.start, case.target, annotate=False)
        mark_inset(ax, inset, loc1=2, loc2=4, fc="none", ec="0.5", lw=0.8)

    handles = legend_handles(case)
    ax.legend(handles=handles, frameon=False, loc="upper right", ncol=2, handlelength=1.5)
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def plot_paths_figure(
    case: CaseGeometry,
    *,
    paths: Sequence[np.ndarray],
    rep_path: np.ndarray,
    title: str,
    outpath: str,
    mode: str,
    dpi: int,
) -> None:
    setup_mpl()
    fig, ax = plt.subplots(figsize=(8.5, 7.5), constrained_layout=True)
    draw_base(ax, case.N, view=None, coarse_grid_step=5)
    draw_boundaries(ax, bc_x=case.boundary_x, bc_y=case.boundary_y, N=case.N)
    draw_corridor(ax, case.corridor)
    draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
    draw_walls(ax, case.barriers_reflect)
    draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1] if case.barriers_perm else 0.0)
    draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
    draw_start_target(ax, case.start, case.target, annotate=False)

    draw_paths(ax, paths, mode=mode, alpha=0.08, color="#3182bd")
    if rep_path.size:
        draw_rep_path(ax, rep_path, color="#fdae61", label="representative")
    ax.set_title(title)
    if rep_path.size:
        ax.legend(frameon=False, loc="lower left")
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def _quantile_vmin(mats: Sequence[np.ndarray], q: float, floor: float) -> float:
    vals = np.concatenate([m[m > 0] for m in mats if np.any(m > 0)])
    if vals.size == 0:
        return floor
    return max(float(np.quantile(vals, q)), floor)


def plot_prob_snapshots(
    *,
    case: CaseGeometry,
    mats: Sequence[np.ndarray],
    t_list: Sequence[int],
    outpath: str,
    view_main: Optional[ViewBox],
    view_roi: Optional[ViewBox],
    dpi: int,
) -> dict:
    setup_mpl()
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 5.2), constrained_layout=True)
    vmin = _quantile_vmin(mats, q=0.01, floor=1e-12)
    vmax = max(float(np.max(m)) for m in mats)
    norm = LogNorm(vmin=vmin, vmax=vmax)

    ims = []
    for ax, P, t in zip(axes, mats, t_list):
        im = ax.imshow(
            P.T,
            origin="lower",
            cmap="magma",
            norm=norm,
            interpolation="nearest",
            extent=(0.5, case.N + 0.5, 0.5, case.N + 0.5),
        )
        ims.append(im)
        draw_corridor(ax, case.corridor)
        draw_sticky(ax, [(c["x"], c["y"]) for c in case.sticky])
        draw_walls(ax, case.barriers_reflect)
        if case.barriers_perm:
            draw_door(ax, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1])
        draw_local_bias(ax, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
        draw_start_target(ax, case.start, case.target, annotate=False)
        ax.text(
            0.96,
            0.06,
            f"t={t}",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=10,
            color="white",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.35, linewidth=0.0),
        )
        if view_main is not None:
            ax.set_xlim(view_main.x0 - 0.5, view_main.x1 + 0.5)
            ax.set_ylim(view_main.y0 - 0.5, view_main.y1 + 0.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")
        ax.invert_yaxis()

        if view_roi is not None:
            inset = inset_axes(ax, width="42%", height="42%", loc="lower right", borderpad=1.2)
            inset.imshow(
                P.T,
                origin="lower",
                cmap="magma",
                norm=norm,
                interpolation="nearest",
                extent=(0.5, case.N + 0.5, 0.5, case.N + 0.5),
            )
            draw_corridor(inset, case.corridor)
            draw_sticky(inset, [(c["x"], c["y"]) for c in case.sticky])
            draw_walls(inset, case.barriers_reflect)
            if case.barriers_perm:
                draw_door(inset, [edge for edge, _ in case.barriers_perm], p_pass=case.barriers_perm[0][1])
            draw_local_bias(inset, [(c["x"], c["y"], c["dir"]) for c in case.local_bias], step=1)
            draw_start_target(inset, case.start, case.target, annotate=False)
            draw_base(inset, case.N, view=view_roi, coarse_grid_step=1, fine_grid=True)
            inset.set_xlim(view_roi.x0 - 0.5, view_roi.x1 + 0.5)
            inset.set_ylim(view_roi.y0 - 0.5, view_roi.y1 + 0.5)
            inset.invert_yaxis()
            inset.set_xticks([])
            inset.set_yticks([])
            mark_inset(ax, inset, loc1=2, loc2=4, fc="none", ec="0.5", lw=0.8)

    cbar = fig.colorbar(ims[-1], ax=axes, shrink=0.92, pad=0.02)
    cbar.set_label("P(n,t) (log scale)")
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)
    return {"vmin": float(vmin), "vmax": float(vmax)}


def _bin_hist(times: np.ndarray, *, t_max: int, bin_width: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if times.size == 0:
        t = np.arange(1, t_max + 1)
        return t, np.zeros_like(t, dtype=np.float64), np.zeros_like(t, dtype=np.float64)
    bins = np.arange(1, t_max + bin_width + 1, bin_width)
    counts, edges = np.histogram(times, bins=bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    pmf = counts / float(times.size) / float(bin_width)
    err = np.sqrt(counts) / float(times.size) / float(bin_width)
    return centers, pmf, err


def plot_fpt_big(
    *,
    t: np.ndarray,
    f_exact: np.ndarray,
    f_aw: np.ndarray,
    mc_times: np.ndarray,
    t_max_aw: int,
    marks: Tuple[int, int, int],
    outpath: str,
    bin_width: int,
    log_eps: float,
    dpi: int,
) -> None:
    setup_mpl()
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8), constrained_layout=True)
    ax_lin, ax_log = axes

    ax_lin.plot(t, f_exact, color="black", lw=2.0, label="Exact")
    ax_lin.plot(t[:t_max_aw], f_aw, color="#d95f02", lw=1.8, ls="--", label="AW")
    ax_lin.axvspan(t[0], t_max_aw, color="#fdb462", alpha=0.12, label="AW window")

    ax_log.plot(t, np.where(f_exact >= log_eps, f_exact, np.nan), color="black", lw=2.0)
    ax_log.plot(
        t[:t_max_aw],
        np.where(f_aw >= log_eps, f_aw, np.nan),
        color="#d95f02",
        lw=1.8,
        ls="--",
    )
    ax_log.axvspan(t[0], t_max_aw, color="#fdb462", alpha=0.12)

    centers, pmf, err = _bin_hist(mc_times, t_max=int(t[-1]), bin_width=bin_width)
    ax_lin.errorbar(centers, pmf, yerr=err, fmt="o", ms=3.2, color="#1f78b4", alpha=0.7, label="MC (binned)")
    ax_log.plot(centers, np.where(pmf >= log_eps, pmf, np.nan), "o", ms=3.0, color="#1f78b4", alpha=0.7)

    t1, tv, t2 = marks
    for ax in (ax_lin, ax_log):
        for tt, lab in zip((t1, tv, t2), ("t1", "tv", "t2")):
            ax.axvline(tt, color="0.4", ls="--", lw=1.0)
            ax.annotate(lab, xy=(tt, 0.92), xycoords=("data", "axes fraction"), fontsize=9, color="0.35")
        ax.set_xlim(t[0], t[-1])

    ax_lin.set_title("FPT (linear)")
    ax_log.set_title("FPT (log)")
    ax_log.set_yscale("log")
    ax_lin.set_xlabel("t")
    ax_log.set_xlabel("t")
    ax_lin.set_ylabel("f(t)")
    ax_log.set_ylabel("f(t)")

    ax_lin.legend(frameon=False, bbox_to_anchor=(1.02, 1.0), loc="upper left")
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)


def plot_channel_decomp(
    *,
    t: np.ndarray,
    f_fast: np.ndarray,
    f_slow: np.ndarray,
    p_fast: float,
    p_slow: float,
    outpath: str,
    dpi: int,
) -> None:
    setup_mpl()
    fig, ax = plt.subplots(figsize=(8.0, 4.6), constrained_layout=True)
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
    outpath: str,
    xlabel: str,
    title: str,
    dpi: int,
) -> None:
    setup_mpl()
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.6), constrained_layout=True)
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


def plot_periodic_unwrapped(
    *,
    case: CaseGeometry,
    outpath: str,
    dpi: int,
) -> None:
    setup_mpl()
    fig, ax = plt.subplots(figsize=(11.5, 4.2), constrained_layout=True)
    N = case.N
    draw_base(ax, N * 2, view=ViewBox(1, 2 * N, 1, N), coarse_grid_step=10)

    # Repeat environment in two tiles
    for tile in [0, 1]:
        offset = tile * N
        # walls
        walls = [((a[0] + offset, a[1]), (b[0] + offset, b[1])) for a, b in case.barriers_reflect]
        draw_walls(ax, walls)
        if case.barriers_perm:
            doors = [((a[0] + offset, a[1]), (b[0] + offset, b[1])) for a, b in [edge for edge, _ in case.barriers_perm]]
            draw_door(ax, doors, p_pass=case.barriers_perm[0][1])
        draw_sticky(ax, [(c["x"] + offset, c["y"]) for c in case.sticky])
        draw_corridor(ax, None)
        draw_local_bias(ax, [(c["x"] + offset, c["y"], c["dir"]) for c in case.local_bias])

    # start and target images
    sx, sy = case.start
    tx, ty = case.target
    ax.scatter([sx], [sy], s=90, c="#e41a1c", marker="s", zorder=7)
    ax.scatter([tx, tx + N], [ty, ty], s=90, c="#377eb8", marker="D", zorder=7)
    ax.annotate("start", xy=(sx, sy), xytext=(sx + 2, sy + 2), fontsize=9, color="0.2",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="0.3"))
    ax.annotate("target", xy=(tx, ty), xytext=(tx + 2, ty - 2), fontsize=9, color="0.2",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="0.3"))
    ax.annotate("target image", xy=(tx + N, ty), xytext=(tx + N - 6, ty - 2), fontsize=9, color="0.2",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="0.3"))

    # annotate distances
    delta = (tx - sx) % N
    short = min(delta, N - delta)
    wrap = max(delta, N - delta)
    # arrow to short image
    if delta <= N - delta:
        target_short = tx
        target_wrap = tx + N
    else:
        target_short = tx + N
        target_wrap = tx

    ax.annotate(
        "Δx_short",
        xy=(target_short, sy),
        xytext=(sx + short / 2, sy - 3),
        arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#2ca25f"),
        color="#2ca25f",
    )
    ax.annotate(
        "Δx_wrap",
        xy=(target_wrap, sy),
        xytext=(sx + wrap / 2, sy + 3),
        arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#756bb1"),
        color="#756bb1",
    )

    draw_global_bias(ax, case.g_x, case.g_y, anchor=(1.0, N + 2.0))
    ax.set_title("Periodic unwrapped view (two tiles)")
    _save(fig, outpath, dpi=dpi)
    plt.close(fig)
