#!/usr/bin/env python3
"""Environment schematic drawing for v4 figures."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt

from .case_data import CaseGeometry
from .draw_overlays import (
    build_legend_handles,
    draw_barriers,
    draw_boundaries,
    draw_corridor_band,
    draw_global_bias,
    draw_local_bias,
    draw_periodic_markers,
    draw_start_target,
    draw_sticky,
    setup_lattice_axes,
)
from .style import set_style
from .draw_paths import plot_trajectory


def draw_environment(
    ax: plt.Axes,
    case: CaseGeometry,
    *,
    show_grid: bool = True,
    show_global_bias: bool = True,
    legend: bool = True,
) -> None:
    setup_lattice_axes(ax, case.N, show_grid=show_grid)
    draw_boundaries(ax, case)
    draw_periodic_markers(ax, case)
    if show_global_bias:
        draw_global_bias(ax, case)
    draw_corridor_band(ax, case)
    draw_sticky(ax, case)
    draw_barriers(ax, case)
    draw_local_bias(ax, case)
    draw_start_target(ax, case)

    if legend:
        handles = build_legend_handles(case)
        ax.legend(handles=handles, frameon=False, fontsize=8, loc="upper right", ncol=2, handlelength=1.4)


def save_environment_figure(case: CaseGeometry, outpath: Path, *, dpi: int = 600) -> None:
    set_style("fig3")
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    draw_environment(ax, case, show_grid=True, show_global_bias=True, legend=True)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=dpi)
    fig.savefig(outpath.with_suffix(".png"), dpi=dpi)
    plt.close(fig)


def save_symbol_legend(case: CaseGeometry, outpath: Path, *, dpi: int = 600) -> None:
    set_style("fig3")
    fig, ax = plt.subplots(figsize=(6.0, 1.6))
    ax.axis("off")
    handles = build_legend_handles(case)
    ax.legend(
        handles=handles,
        ncol=3,
        frameon=False,
        loc="center",
        handlelength=1.4,
        columnspacing=1.2,
    )
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=dpi)
    fig.savefig(outpath.with_suffix(".png"), dpi=dpi)
    plt.close(fig)


def save_path_figure(
    case: CaseGeometry,
    *,
    traj,
    label: str,
    color: str,
    outpath: Path,
    dpi: int = 600,
) -> None:
    set_style("fig3")
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    draw_environment(ax, case, show_grid=True, show_global_bias=True, legend=False)
    if traj is not None and len(traj) > 0:
        plot_trajectory(ax, traj, color=color, lw=2.3, alpha=0.9, arrow_every=12, label=label)
        ax.legend(frameon=False, fontsize=8, loc="lower left")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=dpi)
    fig.savefig(outpath.with_suffix(".png"), dpi=dpi)
    plt.close(fig)
