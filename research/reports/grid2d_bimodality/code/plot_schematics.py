#!/usr/bin/env python3
"""Schematic plotting helpers (Fig.3 style) and representative paths."""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle

from model_core import Coord, LatticeConfig, ConfigSpec, DIRECTIONS, coord_to1


def draw_grid(ax: plt.Axes, N: int, step: int = 5) -> None:
    for k in range(step, N, step):
        ax.axhline(k + 0.5, color="0.90", lw=0.5, zorder=0)
        ax.axvline(k + 0.5, color="0.90", lw=0.5, zorder=0)
    ax.add_patch(Rectangle((0.5, 0.5), N, N, fill=False, lw=1.2, edgecolor="0.2", zorder=1))


def draw_barrier_edge(ax: plt.Axes, a: Coord, b: Coord, *, style: str, lw: float) -> None:
    x1, y1 = coord_to1(a)
    x2, y2 = coord_to1(b)
    if x1 == x2:
        y = max(y1, y2) - 0.5
        ax.plot([x1 - 0.5, x1 + 0.5], [y, y], style, lw=lw)
    elif y1 == y2:
        x = max(x1, x2) - 0.5
        ax.plot([x, x], [y1 - 0.5, y1 + 0.5], style, lw=lw)


def draw_periodic_marker(ax: plt.Axes, cfg: LatticeConfig) -> None:
    if cfg.boundary_x == "periodic":
        arrow = FancyArrowPatch(
            (0.4, cfg.N + 0.6),
            (cfg.N + 0.6, cfg.N + 0.6),
            connectionstyle="arc3,rad=0.3",
            arrowstyle="->",
            lw=1.0,
            color="0.35",
            clip_on=False,
        )
        ax.add_patch(arrow)
        ax.text(cfg.N / 2, cfg.N + 1.0, "periodic x", fontsize=8, color="0.35", ha="center")
    if cfg.boundary_y == "periodic":
        arrow = FancyArrowPatch(
            (cfg.N + 0.6, 0.4),
            (cfg.N + 0.6, cfg.N + 0.6),
            connectionstyle="arc3,rad=0.3",
            arrowstyle="->",
            lw=1.0,
            color="0.35",
            clip_on=False,
        )
        ax.add_patch(arrow)
        ax.text(cfg.N + 1.0, cfg.N / 2, "periodic y", fontsize=8, color="0.35", va="center", rotation=90)


def draw_global_bias(ax: plt.Axes, cfg: LatticeConfig) -> None:
    if abs(cfg.g_x) < 1e-9 and abs(cfg.g_y) < 1e-9:
        return
    dx = -cfg.g_x
    dy = cfg.g_y
    norm = float(np.hypot(dx, dy))
    if norm <= 1e-12:
        return
    dx /= norm
    dy /= norm
    x0, y0 = cfg.N - 6.0, cfg.N + 2.0
    x1, y1 = x0 + 4.0 * dx, y0 + 4.0 * dy
    arrow = FancyArrowPatch(
        (x0, y0),
        (x1, y1),
        arrowstyle="-|>",
        mutation_scale=14,
        lw=1.6,
        color="#4d4d4d",
        clip_on=False,
    )
    ax.add_patch(arrow)
    ax.text(x0, y0 + 0.6, f"global bias ({cfg.g_x:+.2f},{cfg.g_y:+.2f})", fontsize=8, color="0.35")


def draw_reflecting_boundaries(ax: plt.Axes, cfg: LatticeConfig) -> None:
    if cfg.boundary_x == "reflecting":
        ax.plot([0.5, 0.5], [0.5, cfg.N + 0.5], color="0.1", lw=2.2)
        ax.plot([cfg.N + 0.5, cfg.N + 0.5], [0.5, cfg.N + 0.5], color="0.1", lw=2.2)
    if cfg.boundary_y == "reflecting":
        ax.plot([0.5, cfg.N + 0.5], [0.5, 0.5], color="0.1", lw=2.2)
        ax.plot([0.5, cfg.N + 0.5], [cfg.N + 0.5, cfg.N + 0.5], color="0.1", lw=2.2)


def draw_schematic_on_ax(
    ax: plt.Axes,
    *,
    cfg: LatticeConfig,
    spec: ConfigSpec,
    path_fast: List[Coord],
    path_slow: List[Coord],
    annotate_door: Optional[Tuple[Coord, Coord]] = None,
    sticky_block: Optional[Tuple[Coord, Coord]] = None,
    show_legend: bool = True,
) -> None:
    draw_grid(ax, cfg.N, step=5)
    draw_reflecting_boundaries(ax, cfg)
    draw_periodic_marker(ax, cfg)
    draw_global_bias(ax, cfg)

    if sticky_block is not None:
        (x0, y0), (x1, y1) = sticky_block
        ax.add_patch(
            Rectangle(
                (x0 - 0.5, y0 - 0.5),
                x1 - x0 + 1,
                y1 - y0 + 1,
                facecolor="#8da0cb",
                alpha=0.25,
                edgecolor="none",
                zorder=2,
            )
        )

    for edge in cfg.barriers_reflect:
        draw_barrier_edge(ax, edge[0], edge[1], style="k-", lw=2.2)
    for edge, p in cfg.barriers_perm.items():
        draw_barrier_edge(ax, edge[0], edge[1], style="k--", lw=2.2)
        if annotate_door is not None and edge == annotate_door:
            a, b = edge
            x1, y1 = coord_to1(a)
            x2, y2 = coord_to1(b)
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.6, f"p_pass={p:.2f}", fontsize=8, ha="center")

    corridor_band = False
    if cfg.local_bias_arrows:
        xs = [xy[0] for xy in cfg.local_bias_arrows]
        ys = [xy[1] for xy in cfg.local_bias_arrows]
        if len(set(ys)) == 1:
            x0 = min(xs) + 1
            x1 = max(xs) + 1
            y0 = ys[0] + 1
            ax.add_patch(
                Rectangle(
                    (x0 - 0.5, y0 - 0.8),
                    x1 - x0 + 1,
                    1.6,
                    facecolor="#fdb462",
                    alpha=0.15,
                    edgecolor="none",
                    zorder=1,
                )
            )
            corridor_band = True

    for xy, direction in cfg.local_bias_arrows.items():
        dx, dy = DIRECTIONS[direction]
        x, y = coord_to1(xy)
        arrow = FancyArrowPatch(
            (x, y),
            (x + 0.8 * dx, y + 0.8 * dy),
            arrowstyle="-|>",
            mutation_scale=10,
            lw=1.4,
            color="#d95f02",
        )
        ax.add_patch(arrow)

    if path_fast:
        xs = [coord_to1(xy)[0] for xy in path_fast]
        ys = [coord_to1(xy)[1] for xy in path_fast]
        ax.plot(xs, ys, color="#e6550d", lw=1.2, alpha=0.75)
    if path_slow:
        xs = [coord_to1(xy)[0] for xy in path_slow]
        ys = [coord_to1(xy)[1] for xy in path_slow]
        ax.plot(xs, ys, color="#1b9e77", lw=1.2, alpha=0.75)

    sx, sy = spec.start
    tx, ty = spec.target
    ax.scatter([sx], [sy], s=70, c="#e41a1c", marker="s", zorder=5)
    ax.scatter([tx], [ty], s=70, c="#377eb8", marker="D", zorder=5)

    ax.set_xlim(0.5, cfg.N + 0.5)
    ax.set_ylim(0.5, cfg.N + 0.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(0, cfg.N + 1, 10))
    ax.set_yticks(range(0, cfg.N + 1, 10))
    ax.tick_params(labelsize=8)

    if show_legend:
        handles = [
            Line2D([0], [0], marker="s", color="w", markerfacecolor="#e41a1c", markersize=7, label="start"),
            Line2D([0], [0], marker="D", color="w", markerfacecolor="#377eb8", markersize=7, label="target"),
        ]
        if cfg.local_bias_arrows:
            handles.append(
                Line2D(
                    [0],
                    [0],
                    color="#d95f02",
                    lw=1.4,
                    label=f"local bias (delta={spec.local_bias_delta:.2f})",
                )
            )
            if corridor_band:
                handles.append(Patch(facecolor="#fdb462", alpha=0.2, label="corridor"))
        if cfg.barriers_reflect:
            handles.append(Line2D([0], [0], color="k", lw=2.2, label="reflecting wall"))
        if cfg.barriers_perm:
            handles.append(Line2D([0], [0], color="k", lw=2.2, ls="--", label="door (p_pass)"))
        if sticky_block is not None:
            alpha_val = None
            if spec.sticky_sites:
                alpha_val = list(spec.sticky_sites.values())[0]
            label = "sticky region" if alpha_val is None else f"sticky (alpha={alpha_val:.2f})"
            handles.append(Patch(facecolor="#8da0cb", alpha=0.25, label=label))
        if path_fast:
            handles.append(Line2D([0], [0], color="#e6550d", lw=1.2, label="fast channel"))
        if path_slow:
            handles.append(Line2D([0], [0], color="#1b9e77", lw=1.2, label="slow channel"))
        ax.legend(
            handles=handles,
            frameon=False,
            fontsize=7,
            loc="upper right",
            ncol=2,
            handlelength=1.4,
        )


def plot_schematic(
    *,
    cfg: LatticeConfig,
    spec: ConfigSpec,
    outpath,
    path_fast: List[Coord],
    path_slow: List[Coord],
    annotate_door: Optional[Tuple[Coord, Coord]] = None,
    sticky_block: Optional[Tuple[Coord, Coord]] = None,
) -> None:
    fig, ax = plt.subplots(figsize=(5.8, 5.6))
    draw_schematic_on_ax(
        ax,
        cfg=cfg,
        spec=spec,
        path_fast=path_fast,
        path_slow=path_slow,
        annotate_door=annotate_door,
        sticky_block=sticky_block,
        show_legend=True,
    )
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    fig.savefig(str(outpath).replace(".pdf", ".png"), dpi=300)
    plt.close(fig)


def _walk_line(cfg: LatticeConfig, start: Coord, step: Coord, n_steps: int) -> List[Coord]:
    x, y = start
    path = [(x, y)]
    dx, dy = step
    for _ in range(n_steps):
        x = (x + dx) % cfg.N if cfg.boundary_x == "periodic" else x + dx
        y = (y + dy) % cfg.N if cfg.boundary_y == "periodic" else y + dy
        path.append((x, y))
    return path


def find_paths_candidate_A(
    cfg: LatticeConfig, seed: int, max_steps: int, max_trials: int = 2000
) -> Tuple[List[Coord], List[Coord]]:
    start = cfg.start
    target = cfg.target
    y = start[1]

    # Fast: direct (no wrap) along x toward target.
    step_fast = 1 if target[0] > start[0] else -1
    n_fast = abs(target[0] - start[0])
    fast_path = _walk_line(cfg, (start[0], y), (step_fast, 0), n_fast)

    # Slow: wrap-around along bias direction in x.
    step_slow = -1 if cfg.g_x >= 0 else 1
    n_slow = (cfg.N - n_fast) % cfg.N
    slow_path = _walk_line(cfg, (start[0], y), (step_slow, 0), n_slow)
    return fast_path, slow_path


def find_paths_candidate_B(
    cfg: LatticeConfig, corridor_set: set[Coord], seed: int, max_steps: int, max_trials: int = 2000
) -> Tuple[List[Coord], List[Coord]]:
    start = cfg.start
    target = cfg.target
    y = start[1]

    # Fast: follow corridor to its end, then continue left to target.
    xs = [xy[0] for xy in corridor_set] if corridor_set else [start[0]]
    x_min = min(xs)
    path_fast = []
    x = start[0]
    path_fast.append((x, y))
    while x > x_min:
        x -= 1
        path_fast.append((x, y))
    while x > target[0]:
        x -= 1
        path_fast.append((x, y))

    # Slow: detour off the corridor and re-approach target.
    path_slow = [(start[0], y), (start[0], min(cfg.N - 1, y + 2))]
    x = start[0]
    y_detour = path_slow[-1][1]
    while x > target[0]:
        x -= 1
        path_slow.append((x, y_detour))
    if y_detour != y:
        path_slow.append((x, y))
    return path_fast, path_slow


def find_paths_candidate_C(
    cfg: LatticeConfig,
    door_edge: Tuple[Coord, Coord],
    t_valley: int,
    seed: int,
    max_steps: int,
    max_trials: int = 2000,
) -> Tuple[List[Coord], List[Coord]]:
    start = cfg.start
    target = cfg.target
    y = start[1]
    door_x = min(door_edge[0][0], door_edge[1][0])

    # Fast: wrap-around along bias direction (left if g_x>0).
    step_fast = -1 if cfg.g_x >= 0 else 1
    n_fast = (cfg.N - (target[0] - start[0]) % cfg.N) % cfg.N
    fast_path = _walk_line(cfg, (start[0], y), (step_fast, 0), n_fast)

    # Slow: move against bias, cross the door, then proceed to target.
    path_slow = [(start[0], y)]
    x = start[0]
    while x < door_x:
        x += 1
        path_slow.append((x, y))
    # Cross the door edge.
    path_slow.append((door_x + 1, y))
    x = door_x + 1
    while x < target[0]:
        x += 1
        path_slow.append((x, y))
    return fast_path, path_slow
    if cfg.local_bias_arrows:
        xs = [xy[0] for xy in cfg.local_bias_arrows]
        ys = [xy[1] for xy in cfg.local_bias_arrows]
        if len(set(ys)) == 1:
            x0 = min(xs) + 1
            x1 = max(xs) + 1
            y0 = ys[0] + 1
            ax.add_patch(
                Rectangle(
                    (x0 - 0.5, y0 - 0.8),
                    x1 - x0 + 1,
                    1.6,
                    facecolor="#fdb462",
                    alpha=0.15,
                    edgecolor="none",
                    zorder=1,
                )
            )
