#!/usr/bin/env python3
"""Plotting utilities for FPT overlays and heatmaps."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from model_core import Coord, LatticeConfig, ConfigSpec
from plot_schematics import draw_schematic_on_ax


def smooth_curve(y: np.ndarray, window: int = 5) -> np.ndarray:
    if window <= 1 or y.size < window:
        return y.copy()
    kernel = np.ones(window, dtype=np.float64) / float(window)
    return np.convolve(y, kernel, mode="same")


def plot_fpt_overlay(
    *,
    t: np.ndarray,
    f_exact: np.ndarray,
    f_aw: Optional[np.ndarray],
    f_mc: np.ndarray,
    f_fast: Optional[np.ndarray],
    f_slow: Optional[np.ndarray],
    peaks: dict,
    out_linear,
    out_log,
    title: str,
) -> None:
    def plot_one(ax, logy: bool) -> None:
        ax.plot(t, f_exact, color="black", lw=1.4, label="Exact")
        if f_aw is not None:
            ax.plot(t, f_aw, color="#d95f02", lw=1.2, label="AW")
        ax.plot(t, f_mc, color="#1f78b4", lw=1.0, alpha=0.7, label="MC")
        if f_fast is not None:
            ax.plot(t, f_fast, color="#1b9e77", lw=0.9, alpha=0.8, label="MC fast")
        if f_slow is not None:
            ax.plot(t, f_slow, color="#7570b3", lw=0.9, alpha=0.8, label="MC slow")
        ax.set_xlabel("t")
        ax.set_ylabel("f(t)")
        if logy:
            ax.set_yscale("log")
        if peaks.get("t1") is not None:
            ax.axvline(peaks["t1"], color="0.4", ls="--", lw=0.8)
        if peaks.get("t2") is not None:
            ax.axvline(peaks["t2"], color="0.4", ls="--", lw=0.8)
        if peaks.get("tv") is not None:
            ax.axvline(peaks["tv"], color="0.6", ls=":", lw=0.8)
        ax.set_xlim(t[0], t[-1])
        ax.legend(frameon=False, fontsize=7, ncol=2)

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    plot_one(ax, logy=False)
    ax.set_title(title, fontsize=10)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.06, wspace=0.25, hspace=0.3)
    fig.savefig(out_linear, dpi=300)
    fig.savefig(Path(out_linear).with_suffix(".png"), dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    plot_one(ax, logy=True)
    ax.set_title(title, fontsize=10)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.06, wspace=0.25, hspace=0.3)
    fig.savefig(out_log, dpi=300)
    fig.savefig(Path(out_log).with_suffix(".png"), dpi=300)
    plt.close(fig)


def plot_heatmaps(
    *,
    heatmaps: Sequence[np.ndarray],
    times: Sequence[int],
    outpath,
    title: str,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
) -> None:
    n = len(heatmaps)
    fig, axes = plt.subplots(1, n, figsize=(3.2 * n, 3.2))
    if n == 1:
        axes = [axes]

    if vmin is None:
        vmin = 0.0
    if vmax is None:
        vmax = max(float(np.max(h)) for h in heatmaps)

    for ax, h, t in zip(axes, heatmaps, times):
        im = ax.imshow(h.T, origin="lower", cmap="viridis", vmin=vmin, vmax=vmax)
        ax.set_title(f"t={t}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(title, fontsize=10)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.06, wspace=0.25, hspace=0.3)
    fig.savefig(outpath, dpi=300)
    fig.savefig(Path(outpath).with_suffix(".png"), dpi=300)
    plt.close(fig)


def plot_candidate_panel(
    *,
    cfg: LatticeConfig,
    spec: ConfigSpec,
    path_fast: List[Coord],
    path_slow: List[Coord],
    heatmaps: Sequence[np.ndarray],
    times: Sequence[int],
    t: np.ndarray,
    f_exact: np.ndarray,
    f_aw: Optional[np.ndarray],
    f_mc: np.ndarray,
    peaks: dict,
    outpath,
    annotate_door: Optional[Tuple[Coord, Coord]] = None,
    sticky_block: Optional[Tuple[Coord, Coord]] = None,
) -> None:
    fig = plt.figure(figsize=(9.6, 8.4))
    gs = GridSpec(2, 2, figure=fig, wspace=0.25, hspace=0.25)

    ax_schem = fig.add_subplot(gs[0, 0])
    draw_schematic_on_ax(
        ax_schem,
        cfg=cfg,
        spec=spec,
        path_fast=path_fast,
        path_slow=path_slow,
        annotate_door=annotate_door,
        sticky_block=sticky_block,
        show_legend=False,
    )
    ax_schem.set_title("A. configuration", fontsize=10)

    ax_h1 = fig.add_subplot(gs[0, 1])
    ax_h2 = fig.add_subplot(gs[1, 0])
    vmax = max(float(np.max(h)) for h in heatmaps)
    ax_h1.imshow(heatmaps[0].T, origin="lower", cmap="viridis", vmin=0.0, vmax=vmax)
    ax_h1.set_title(f"B. P(n,t), t={times[0]}", fontsize=10)
    ax_h1.set_xticks([])
    ax_h1.set_yticks([])
    ax_h2.imshow(heatmaps[1].T, origin="lower", cmap="viridis", vmin=0.0, vmax=vmax)
    ax_h2.set_title(f"C. P(n,t), t={times[1]}", fontsize=10)
    ax_h2.set_xticks([])
    ax_h2.set_yticks([])

    sub_gs = gs[1, 1].subgridspec(2, 1, hspace=0.3)
    ax_lin = fig.add_subplot(sub_gs[0])
    ax_log = fig.add_subplot(sub_gs[1])

    ax_lin.plot(t, f_exact, color="black", lw=1.1, label="Exact")
    if f_aw is not None:
        ax_lin.plot(t, f_aw, color="#d95f02", lw=1.0, label="AW")
    ax_lin.plot(t, f_mc, color="#1f78b4", lw=0.9, alpha=0.7, label="MC")
    ax_lin.set_title("D. FPT (linear/log)", fontsize=10)
    ax_lin.set_ylabel("f(t)")
    ax_lin.set_xlim(t[0], t[-1])
    ax_lin.legend(frameon=False, fontsize=7, ncol=3)

    ax_log.plot(t, f_exact, color="black", lw=1.1)
    if f_aw is not None:
        ax_log.plot(t, f_aw, color="#d95f02", lw=1.0)
    ax_log.plot(t, f_mc, color="#1f78b4", lw=0.9, alpha=0.7)
    ax_log.set_yscale("log")
    ax_log.set_xlabel("t")
    ax_log.set_ylabel("f(t)")
    ax_log.set_xlim(t[0], t[-1])

    fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.06, wspace=0.25, hspace=0.3)
    fig.savefig(outpath, dpi=300)
    fig.savefig(Path(outpath).with_suffix(".png"), dpi=300)
    plt.close(fig)
