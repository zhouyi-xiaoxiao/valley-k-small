#!/usr/bin/env python3
"""Panel layout for v4 figures."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Tuple
import matplotlib.pyplot as plt

from .case_data import CaseGeometry
from .draw_env import draw_environment
from .draw_overlays import draw_barriers, draw_corridor_band, draw_local_bias, draw_start_target, draw_sticky
from .draw_paths import plot_trajectory
from .plot_heatmaps import compute_lognorm
from .plot_fpt import plot_fpt_axes
from .style import set_style


def plot_panel(
    *,
    case: CaseGeometry,
    traj: Optional[np.ndarray],
    traj_label: str,
    heatmaps: Sequence[np.ndarray],
    times: Sequence[int],
    t: np.ndarray,
    f_exact: np.ndarray,
    f_aw: np.ndarray,
    mc_times: np.ndarray,
    t_max_aw: int,
    peaks: Tuple[int, int, int],
    mc_bin_width: int,
    mc_smooth_window: int,
    log_eps: float,
    outpath: Path,
    roi: Optional[Tuple[int, int, int, int]] = None,
    dpi: int = 600,
) -> dict:
    set_style("fig3")
    fig = plt.figure(figsize=(12.5, 7.2))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.1, 1.0, 1.0], height_ratios=[1.0, 1.0], wspace=0.25, hspace=0.35)

    ax_env = fig.add_subplot(gs[:, 0])
    draw_environment(ax_env, case, show_grid=True, show_global_bias=True, legend=True)
    if traj is not None:
        plot_trajectory(ax_env, traj, color="#fdae61", lw=2.2, alpha=0.9, arrow_every=15, label=traj_label)
        ax_env.legend(frameon=False, fontsize=8, loc="lower left")

    gs_heat = gs[0, 1:].subgridspec(1, 3, wspace=0.12)
    heat_axes = [fig.add_subplot(gs_heat[0, i]) for i in range(3)]

    norm = compute_lognorm(heatmaps, vmin_floor=1e-12)
    for ax, mat, t_now in zip(heat_axes, heatmaps, times):
        im = ax.imshow(
            mat.T,
            origin="lower",
            cmap="magma",
            norm=norm,
            interpolation="nearest",
            extent=(0.5, case.N + 0.5, 0.5, case.N + 0.5),
        )
        draw_corridor_band(ax, case)
        draw_sticky(ax, case)
        draw_barriers(ax, case)
        draw_local_bias(ax, case)
        draw_start_target(ax, case)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")
        ax.invert_yaxis()
        ax.text(
            0.96,
            0.06,
            f"t={t_now}",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            color="white",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.35, linewidth=0.0),
        )

    cbar = fig.colorbar(im, ax=heat_axes, shrink=0.9, pad=0.02)
    cbar.set_label("P(n,t) (log scale)")

    gs_fpt = gs[1, 1:].subgridspec(1, 2, wspace=0.28)
    ax_lin = fig.add_subplot(gs_fpt[0, 0])
    ax_log = fig.add_subplot(gs_fpt[0, 1])
    plot_fpt_axes(
        t=t,
        f_exact=f_exact,
        f_aw=f_aw,
        mc_times=mc_times,
        t_max_aw=t_max_aw,
        peaks=peaks,
        mc_bin_width=mc_bin_width,
        mc_smooth_window=mc_smooth_window,
        log_eps=log_eps,
        ax_lin=ax_lin,
        ax_log=ax_log,
    )

    ax_lin.set_title("FPT (linear)")
    ax_log.set_title("FPT (log)")

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=dpi)
    fig.savefig(outpath.with_suffix(".png"), dpi=dpi)
    plt.close(fig)

    return {"heatmap_norm": {"vmin": float(norm.vmin), "vmax": float(norm.vmax)}}
