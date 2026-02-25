#!/usr/bin/env python3
"""FPT plots for v9 (multiscale + bimodality proof)."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plot_style_v9 import apply_style_v9, detect_bimodality, save_clean


def _annotate_peaks(ax: plt.Axes, peaks: Tuple[int, int, int], *, xlim: Tuple[int, int]) -> None:
    t1, tv, t2 = peaks
    labels = [(t1, "t1", "#2ca25f", 0.90), (tv, "tv", "#636363", 0.82), (t2, "t2", "#756bb1", 0.74)]
    if abs(tv - t1) < 3:
        labels = [(t1, "t1", "#2ca25f", 0.90), (tv, "tv", "#636363", 0.70), (t2, "t2", "#756bb1", 0.58)]
    for t, lab, col, y_pos in labels:
        if xlim[0] <= t <= xlim[1]:
            ax.axvline(t, color=col, lw=1.0, ls=":")
            ax.annotate(
                lab,
                xy=(t, y_pos),
                xycoords=("data", "axes fraction"),
                ha="left",
                va="center",
                fontsize=9,
                color=col,
                clip_on=True,
            )


def plot_fpt_multiscale_v9(
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
    tail_zoom: bool = False,
    early_inset: bool = False,
) -> None:
    apply_style_v9()
    fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.2), constrained_layout=True)
    t1, tv, t2 = peaks
    t_max = int(t_exact[-1])

    def _plot(ax: plt.Axes, xlim: Tuple[int, int], logy: bool) -> None:
        if logy:
            f_exact_plot = np.where(f_exact > log_eps, f_exact, np.nan)
            f_aw_plot = np.where(f_aw > log_eps, f_aw, np.nan) if f_aw.size else f_aw
            mc_plot = np.where(mc_pmf > log_eps, mc_pmf, np.nan)
        else:
            f_exact_plot = f_exact
            f_aw_plot = f_aw
            mc_plot = mc_pmf
        ax.plot(t_exact, f_exact_plot, color="black", lw=1.8, label="Exact")
        if f_aw.size:
            ax.plot(t_aw, f_aw_plot, color="#d95f02", lw=1.6, ls="--", label="AW")
        ax.plot(mc_centers, mc_plot, color="#1f78b4", lw=1.0, marker="o", ms=3.0, alpha=0.8, label="MC")
        ax.set_xlim(xlim)
        ax.set_xlabel("t")
        ax.set_ylabel("f(t)")
        if logy:
            ax.set_yscale("log")
            positive = f_exact[f_exact > 0]
            y_min = max(log_eps, float(np.min(positive)) if positive.size else log_eps)
            ax.set_ylim(y_min, float(np.max(f_exact)) * 1.2)
        _annotate_peaks(ax, peaks, xlim=xlim)

    gap = max(1, t2 - tv)
    fast_max = min(t_max, max(t1 + 4 * max(1, t1), int(0.35 * max(1, tv))))
    slow_min = max(1, int(max(tv - 0.2 * gap, 1)))
    slow_max = min(t_max, int(t2 + 0.4 * gap))

    _plot(axes[0], (1, t_max), logy=True)
    axes[0].set_title("global (log-y)")

    if early_inset:
        fast_left = max(1, t1 - 2)
        fast_right = min(t_max, tv + 5)
        _plot(axes[1], (fast_left, fast_right), logy=False)
        axes[1].set_ylim(0.0, float(f_exact[t1 - 1]) * 1.2)
        axes[1].set_title("early peak window")
        inset = inset_axes(axes[0], width="42%", height="42%", loc="lower left", borderpad=1.1)
        _plot(inset, (fast_left, fast_right), logy=False)
        inset.set_ylim(0.0, float(f_exact[t1 - 1]) * 1.2)
        inset.set_title("early inset", fontsize=9)
    else:
        _plot(axes[1], (1, fast_max), logy=False)
        axes[1].set_title("fast window")

    _plot(axes[2], (slow_min, slow_max), logy=False)
    axes[2].set_title("slow window")

    axes[0].legend(frameon=False, loc="upper right")

    if tail_zoom:
        inset = inset_axes(axes[0], width="40%", height="40%", loc="lower left", borderpad=1.1)
        _plot(inset, (slow_min, slow_max), logy=False)
        inset.set_title("tail zoom", fontsize=9)

    save_clean(fig, outpath, dpi=dpi)


def plot_channel_decomp_v9(
    *,
    t: np.ndarray,
    f_fast: np.ndarray,
    f_slow: np.ndarray,
    p_fast: float,
    p_slow: float,
    outpath: Path,
    dpi: int = 600,
    tail_zoom: bool = False,
) -> None:
    apply_style_v9()
    fig, ax = plt.subplots(figsize=(9.6, 4.8), constrained_layout=True)
    f_mix = p_fast * f_fast + p_slow * f_slow
    ax.fill_between(t, p_fast * f_fast, color="#fdae61", alpha=0.35, label=f"fast (P={p_fast:.2f})")
    ax.fill_between(t, p_slow * f_slow, color="#66c2a5", alpha=0.35, label=f"slow (P={p_slow:.2f})")
    ax.plot(t, f_mix, color="black", lw=1.8, label="mixture")
    ax.set_xlabel("t")
    ax.set_ylabel("weighted f(t)")
    ax.legend(frameon=False, loc="upper right")

    if tail_zoom:
        t_min = int(max(1, 0.6 * t.max()))
        t_max = int(t.max())
        inset = inset_axes(ax, width="38%", height="38%", loc="upper left", borderpad=1.1)
        inset.plot(t, f_mix, color="black", lw=1.4)
        inset.set_xlim(t_min, t_max)
        inset.set_title("tail zoom", fontsize=9)
        inset.set_xticks([])
        inset.set_yticks([])

    save_clean(fig, outpath, dpi=dpi)


def plot_bimodality_proof_B(
    *,
    t: np.ndarray,
    f_exact: np.ndarray,
    f_aw: np.ndarray,
    t_max_zoom: int,
    smooth_w: int,
    min_sep: int,
    outpath: Path,
    log_eps: float,
    dpi: int = 600,
    detect: dict | None = None,
) -> dict:
    apply_style_v9()
    info = detect if detect is not None else detect_bimodality(f_exact, smooth_w=smooth_w, min_sep=min_sep)
    t_p1, t_v, t_p2 = int(info["p1"]), int(info["v"]), int(info["p2"])

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.4), constrained_layout=True)
    t_mask = t <= t_max_zoom

    def _plot(ax: plt.Axes, logy: bool) -> None:
        if logy:
            f_plot = np.where(f_exact > log_eps, f_exact, np.nan)
            f_aw_plot = np.where(f_aw > log_eps, f_aw, np.nan) if f_aw.size else f_aw
        else:
            f_plot = f_exact
            f_aw_plot = f_aw
        ax.plot(t[t_mask], f_plot[t_mask], color="black", lw=1.8, label="Exact")
        if f_aw.size:
            ax.plot(t[t_mask], f_aw_plot[t_mask], color="#d95f02", lw=1.4, ls="--", label="AW")
        _annotate_peaks(ax, (t_p1, t_v, t_p2), xlim=(1, t_max_zoom))
        ax.set_xlim(1, t_max_zoom)
        ax.set_xlabel("t")
        ax.set_ylabel("f(t)")
        if logy:
            ax.set_yscale("log")
            ax.set_title("semilogy")
        else:
            ax.set_title("linear")

    _plot(axes[0], logy=True)
    _plot(axes[1], logy=False)

    axes[0].legend(frameon=False, loc="upper right")

    axes[1].text(
        0.02,
        0.98,
        f"t_p1={t_p1}, t_v={t_v}, t_p2={t_p2}\n"
        f"h2/h1={info['ratio']:.3g}\n"
        f"valley_depth={info['valley']:.3g}",
        transform=axes[1].transAxes,
        ha="left",
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7", alpha=0.85),
    )

    save_clean(fig, outpath, dpi=dpi)
    return info
