#!/usr/bin/env python3
"""
Publication-grade plotting for v3 (Fig.3-like visuals).

Dev log (v2 audit):
- Config plots: reports/grid2d_bimodality/code/plot_schematics.py (too thin, weak bias cues).
- Heatmaps: reports/grid2d_bimodality/code/plot_results.py::plot_heatmaps (single norm per panel but low contrast).
- FPT: reports/grid2d_bimodality/code/plot_results.py::plot_fpt_overlay (log-axis spikes due to zeros).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle

from model_core import Coord, ConfigSpec, LatticeConfig, DIRECTIONS, coord_to1


def set_paper_style() -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "legend.fontsize": 8,
            "lines.linewidth": 1.6,
            "figure.figsize": (11.5, 6.8),
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
        }
    )


def save_figure(fig: plt.Figure, outpath: Path, *, dpi: int = 300) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=dpi)
    fig.savefig(outpath.with_suffix(".png"), dpi=dpi)


def _draw_grid(ax: plt.Axes, N: int, step: int = 5) -> None:
    ax.set_facecolor("white")
    for k in range(step, N, step):
        ax.axhline(k + 0.5, color="0.92", lw=0.5, zorder=0)
        ax.axvline(k + 0.5, color="0.92", lw=0.5, zorder=0)
    ax.add_patch(Rectangle((0.5, 0.5), N, N, fill=False, lw=1.2, edgecolor="0.2", zorder=1))


def _draw_boundaries(ax: plt.Axes, cfg: LatticeConfig) -> None:
    if cfg.boundary_x == "reflecting":
        ax.plot([0.5, 0.5], [0.5, cfg.N + 0.5], color="0.1", lw=2.2)
        ax.plot([cfg.N + 0.5, cfg.N + 0.5], [0.5, cfg.N + 0.5], color="0.1", lw=2.2)
    if cfg.boundary_y == "reflecting":
        ax.plot([0.5, cfg.N + 0.5], [0.5, 0.5], color="0.1", lw=2.2)
        ax.plot([0.5, cfg.N + 0.5], [cfg.N + 0.5, cfg.N + 0.5], color="0.1", lw=2.2)


def _draw_periodic_markers(ax: plt.Axes, cfg: LatticeConfig) -> None:
    if cfg.boundary_x == "periodic":
        arrow = FancyArrowPatch(
            (0.4, cfg.N + 0.8),
            (cfg.N + 0.6, cfg.N + 0.8),
            connectionstyle="arc3,rad=0.25",
            arrowstyle="->",
            lw=1.0,
            color="0.35",
            clip_on=False,
        )
        ax.add_patch(arrow)
        ax.text(cfg.N / 2, cfg.N + 1.1, "periodic x", fontsize=8, color="0.35", ha="center")
    if cfg.boundary_y == "periodic":
        arrow = FancyArrowPatch(
            (cfg.N + 0.8, 0.4),
            (cfg.N + 0.8, cfg.N + 0.6),
            connectionstyle="arc3,rad=0.25",
            arrowstyle="->",
            lw=1.0,
            color="0.35",
            clip_on=False,
        )
        ax.add_patch(arrow)
        ax.text(cfg.N + 1.1, cfg.N / 2, "periodic y", fontsize=8, color="0.35", rotation=90, va="center")


def _draw_global_bias(ax: plt.Axes, cfg: LatticeConfig) -> None:
    if abs(cfg.g_x) < 1e-12 and abs(cfg.g_y) < 1e-12:
        return
    dx = -cfg.g_x
    dy = cfg.g_y
    norm = float(np.hypot(dx, dy))
    if norm <= 1e-12:
        return
    dx /= norm
    dy /= norm
    x0, y0 = 1.0, cfg.N + 2.0
    x1, y1 = x0 + 4.0 * dx, y0 + 4.0 * dy
    arrow = FancyArrowPatch(
        (x0, y0),
        (x1, y1),
        arrowstyle="-|>",
        mutation_scale=16,
        lw=1.8,
        color="0.25",
        clip_on=False,
    )
    ax.add_patch(arrow)
    ax.text(x0, y0 + 0.6, f"global bias ({cfg.g_x:+.2f},{cfg.g_y:+.2f})", fontsize=8, color="0.35")


def draw_environment(
    ax: plt.Axes,
    *,
    cfg: LatticeConfig,
    spec: ConfigSpec,
    title: Optional[str] = None,
) -> None:
    _draw_grid(ax, cfg.N, step=5)
    _draw_boundaries(ax, cfg)
    _draw_periodic_markers(ax, cfg)
    _draw_global_bias(ax, cfg)

    # Sticky region
    if spec.sticky_sites:
        xs = [x for x, _ in spec.sticky_sites]
        ys = [y for _, y in spec.sticky_sites]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        ax.add_patch(
            Rectangle(
                (x0 - 0.5, y0 - 0.5),
                x1 - x0 + 1,
                y1 - y0 + 1,
                facecolor="#9e9ac8",
                alpha=0.25,
                edgecolor="none",
                zorder=2,
            )
        )

    # Barriers and door
    for edge in cfg.barriers_reflect:
        a, b = edge
        x1, y1 = coord_to1(a)
        x2, y2 = coord_to1(b)
        if x1 == x2:
            y = max(y1, y2) - 0.5
            ax.plot([x1 - 0.5, x1 + 0.5], [y, y], color="k", lw=2.4)
        else:
            x = max(x1, x2) - 0.5
            ax.plot([x, x], [y1 - 0.5, y1 + 0.5], color="k", lw=2.4)
    for edge, p in cfg.barriers_perm.items():
        a, b = edge
        x1, y1 = coord_to1(a)
        x2, y2 = coord_to1(b)
        if x1 == x2:
            y = max(y1, y2) - 0.5
            ax.plot([x1 - 0.5, x1 + 0.5], [y, y], color="k", lw=2.4, ls="--")
        else:
            x = max(x1, x2) - 0.5
            ax.plot([x, x], [y1 - 0.5, y1 + 0.5], color="k", lw=2.4, ls="--")
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.6, f"p={p:.2f}", fontsize=8, ha="center")

    # Corridor band (if single y)
    corridor_band = False
    if spec.local_bias_arrows:
        xs = [xy[0] for xy in spec.local_bias_arrows]
        ys = [xy[1] for xy in spec.local_bias_arrows]
        if len(set(ys)) == 1:
            x0, x1 = min(xs), max(xs)
            y0 = ys[0]
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

    # Local bias arrows
    for xy, direction in spec.local_bias_arrows.items():
        dx, dy = DIRECTIONS[direction]
        x, y = xy
        arrow = FancyArrowPatch(
            (x, y),
            (x + 0.8 * dx, y + 0.8 * dy),
            arrowstyle="-|>",
            mutation_scale=11,
            lw=1.5,
            color="#d95f02",
        )
        ax.add_patch(arrow)

    # Start/target
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
    ax.invert_yaxis()
    if title:
        ax.set_title(title, fontsize=10)

    handles = [
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#e41a1c", markersize=7, label="start"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#377eb8", markersize=7, label="target"),
    ]
    if spec.local_bias_arrows:
        handles.append(Line2D([0], [0], color="#d95f02", lw=1.5, label=f"local bias (δ={spec.local_bias_delta:.2f})"))
        if corridor_band:
            handles.append(Patch(facecolor="#fdb462", alpha=0.2, label="corridor"))
    if cfg.barriers_reflect:
        handles.append(Line2D([0], [0], color="k", lw=2.2, label="reflecting wall"))
    if cfg.barriers_perm:
        handles.append(Line2D([0], [0], color="k", lw=2.2, ls="--", label="door (p_pass)"))
    if spec.sticky_sites:
        alpha_val = list(spec.sticky_sites.values())[0]
        handles.append(Patch(facecolor="#9e9ac8", alpha=0.25, label=f"sticky (α={alpha_val:.2f})"))
    ax.legend(handles=handles, frameon=False, fontsize=7, loc="upper right", ncol=2, handlelength=1.4)


def plot_heatmaps(
    axes: Sequence[plt.Axes],
    heatmaps: Sequence[np.ndarray],
    times: Sequence[int],
    *,
    start: Coord,
    target: Coord,
    norm: LogNorm,
    cmap: str = "magma",
) -> None:
    N = heatmaps[0].shape[0]
    extent = (0.5, N + 0.5, 0.5, N + 0.5)
    for ax, h, t in zip(axes, heatmaps, times):
        im = ax.imshow(
            h.T,
            origin="lower",
            cmap=cmap,
            norm=norm,
            interpolation="nearest",
            extent=extent,
        )
        ax.scatter([start[0]], [start[1]], s=26, c="#e41a1c", marker="s", edgecolors="white", linewidths=0.4)
        ax.scatter([target[0]], [target[1]], s=26, c="#377eb8", marker="D", edgecolors="white", linewidths=0.4)
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


def compute_log_norm(mats: Sequence[np.ndarray], *, vmin_floor: float = 1e-12) -> LogNorm:
    vmax = max(float(np.max(m)) for m in mats)
    positive = [m[m > 0] for m in mats if np.any(m > 0)]
    vmin = min(float(np.min(p)) for p in positive) if positive else vmin_floor
    vmin = max(vmin, vmin_floor)
    return LogNorm(vmin=vmin, vmax=vmax)


def _bin_hist(times: np.ndarray, *, t_max: int, bin_width: int) -> Tuple[np.ndarray, np.ndarray]:
    if bin_width <= 1:
        t = np.arange(1, t_max + 1)
        counts = np.bincount(times, minlength=t_max + 1)[1:]
        return t, counts / float(times.size)
    bins = np.arange(1, t_max + bin_width + 1, bin_width)
    counts, edges = np.histogram(times, bins=bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    pmf = counts / float(times.size) / float(bin_width)
    return centers, pmf


def _smooth(y: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or y.size < window:
        return y.copy()
    kernel = np.ones(window, dtype=np.float64) / float(window)
    return np.convolve(y, kernel, mode="same")


def plot_fpt_axes(
    ax_lin: plt.Axes,
    ax_log: plt.Axes,
    *,
    t: np.ndarray,
    f_exact: np.ndarray,
    f_aw: np.ndarray,
    mc_times: np.ndarray,
    t_max_aw: int,
    peaks: Tuple[int, int, int],
    mc_bin_width: int,
    mc_smooth_window: int,
    log_eps: float,
) -> None:
    t1, tv, t2 = peaks

    # Exact and AW
    ax_lin.step(t, f_exact, where="mid", color="black", lw=1.6, label="Exact")
    ax_lin.plot(t, f_aw, color="#d95f02", lw=1.4, label="AW")
    ax_lin.axvspan(t[0], t_max_aw, color="#fdb462", alpha=0.12, label="AW window")

    ax_log.step(t, np.where(f_exact >= log_eps, f_exact, np.nan), where="mid", color="black", lw=1.6)
    ax_log.plot(t, np.where(f_aw >= log_eps, f_aw, np.nan), color="#d95f02", lw=1.4)
    ax_log.axvspan(t[0], t_max_aw, color="#fdb462", alpha=0.12)

    # MC (binned + smooth for display)
    centers, pmf = _bin_hist(mc_times, t_max=t[-1], bin_width=mc_bin_width)
    pmf_s = _smooth(pmf, mc_smooth_window)
    ax_lin.plot(centers, pmf_s, color="#1f78b4", lw=1.1, alpha=0.8, label="MC (binned)")
    ax_log.plot(
        centers,
        np.where(pmf_s >= log_eps, pmf_s, np.nan),
        color="#1f78b4",
        lw=1.1,
        alpha=0.8,
    )

    for ax in (ax_lin, ax_log):
        for tt, lab in zip((t1, tv, t2), ("t1", "tv", "t2")):
            ax.axvline(tt, color="0.4", ls="--", lw=0.9)
            ax.annotate(lab, xy=(tt, 0.9), xycoords=("data", "axes fraction"), fontsize=8, color="0.35")
        ax.set_xlim(t[0], t[-1])

    ax_lin.set_ylabel("f(t)")
    ax_log.set_ylabel("f(t)")
    ax_log.set_yscale("log")
    ax_log.set_xlabel("t")
    ax_lin.legend(frameon=False, fontsize=8, loc="upper right")


def plot_panel(
    *,
    cfg: LatticeConfig,
    spec: ConfigSpec,
    heatmaps: Sequence[np.ndarray],
    times: Sequence[int],
    t: np.ndarray,
    f_exact: np.ndarray,
    f_aw: np.ndarray,
    mc_times: np.ndarray,
    t_max_aw: int,
    peaks: Tuple[int, int, int],
    outpath: Path,
    png_dpi: int,
    mc_bin_width: int,
    mc_smooth_window: int,
    log_eps: float,
) -> dict:
    set_paper_style()
    fig = plt.figure(figsize=(12.0, 6.8), constrained_layout=False)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.2, 1.0, 1.0], height_ratios=[1.0, 1.0], wspace=0.25, hspace=0.25)

    ax_env = fig.add_subplot(gs[:, 0])
    draw_environment(ax_env, cfg=cfg, spec=spec, title="Environment")

    gs_heat = gs[0, 1:].subgridspec(1, 3, wspace=0.12)
    heat_axes = [fig.add_subplot(gs_heat[0, i]) for i in range(3)]

    norm = compute_log_norm(heatmaps, vmin_floor=1e-12)
    plot_heatmaps(
        heat_axes,
        heatmaps,
        times,
        start=spec.start,
        target=spec.target,
        norm=norm,
        cmap="magma",
    )
    cbar = fig.colorbar(heat_axes[-1].images[0], ax=heat_axes, shrink=0.92, pad=0.02)
    cbar.set_label("P(n,t) (log scale)")

    gs_fpt = gs[1, 1:].subgridspec(1, 2, wspace=0.28)
    ax_lin = fig.add_subplot(gs_fpt[0, 0])
    ax_log = fig.add_subplot(gs_fpt[0, 1])
    plot_fpt_axes(
        ax_lin,
        ax_log,
        t=t,
        f_exact=f_exact,
        f_aw=f_aw,
        mc_times=mc_times,
        t_max_aw=t_max_aw,
        peaks=peaks,
        mc_bin_width=mc_bin_width,
        mc_smooth_window=mc_smooth_window,
        log_eps=log_eps,
    )
    ax_lin.set_title("FPT (linear)")
    ax_log.set_title("FPT (log)")

    fig.suptitle(f"{spec.N}x{spec.N} case", fontsize=12)
    save_figure(fig, outpath, dpi=png_dpi)
    plt.close(fig)

    return {
        "heatmap_norm": {"vmin": float(norm.vmin), "vmax": float(norm.vmax)},
        "heatmap_times": [int(t) for t in times],
    }


def plot_environment_figure(
    *,
    cfg: LatticeConfig,
    spec: ConfigSpec,
    outpath: Path,
    png_dpi: int,
) -> None:
    set_paper_style()
    fig, ax = plt.subplots(figsize=(5.8, 5.6))
    draw_environment(ax, cfg=cfg, spec=spec, title="Environment")
    save_figure(fig, outpath, dpi=png_dpi)
    plt.close(fig)


def plot_heatmap_figure(
    *,
    heatmaps: Sequence[np.ndarray],
    times: Sequence[int],
    start: Coord,
    target: Coord,
    outpath: Path,
    png_dpi: int,
) -> dict:
    set_paper_style()
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.4), constrained_layout=True)
    norm = compute_log_norm(heatmaps, vmin_floor=1e-12)
    plot_heatmaps(
        axes,
        heatmaps,
        times,
        start=start,
        target=target,
        norm=norm,
        cmap="magma",
    )
    cbar = fig.colorbar(axes[-1].images[0], ax=axes, shrink=0.88, pad=0.02)
    cbar.set_label("P(n,t) (log scale)")
    save_figure(fig, outpath, dpi=png_dpi)
    plt.close(fig)
    return {"heatmap_norm": {"vmin": float(norm.vmin), "vmax": float(norm.vmax)}}


def plot_fpt_figure(
    *,
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
    png_dpi: int,
) -> None:
    set_paper_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 3.4), constrained_layout=True)
    plot_fpt_axes(
        axes[0],
        axes[1],
        t=t,
        f_exact=f_exact,
        f_aw=f_aw,
        mc_times=mc_times,
        t_max_aw=t_max_aw,
        peaks=peaks,
        mc_bin_width=mc_bin_width,
        mc_smooth_window=mc_smooth_window,
        log_eps=log_eps,
    )
    axes[0].set_title("FPT (linear)")
    axes[1].set_title("FPT (log)")
    save_figure(fig, outpath, dpi=png_dpi)
    plt.close(fig)
