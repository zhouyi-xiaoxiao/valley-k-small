#!/usr/bin/env python3
"""FPT plotting for v4 figures."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Tuple

import numpy as np
import matplotlib.pyplot as plt

from .style import set_style


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


def _smooth(y: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or y.size < window:
        return y.copy()
    kernel = np.ones(window, dtype=np.float64) / float(window)
    return np.convolve(y, kernel, mode="same")


def plot_fpt_axes(
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
    ax_lin: plt.Axes,
    ax_log: plt.Axes,
) -> None:
    ax_lin.plot(t, f_exact, color="black", lw=1.8, label="Exact")
    ax_lin.plot(t[:t_max_aw], f_aw, color="#d95f02", lw=1.6, ls="--", label="AW")
    ax_lin.axvspan(t[0], t_max_aw, color="#fdb462", alpha=0.12, label="AW window")

    ax_log.plot(t, np.where(f_exact >= log_eps, f_exact, np.nan), color="black", lw=1.8)
    ax_log.plot(
        t[:t_max_aw],
        np.where(f_aw >= log_eps, f_aw, np.nan),
        color="#d95f02",
        lw=1.6,
        ls="--",
    )
    ax_log.axvspan(t[0], t_max_aw, color="#fdb462", alpha=0.12)

    centers, pmf, err = _bin_hist(mc_times, t_max=int(t[-1]), bin_width=mc_bin_width)
    pmf_s = _smooth(pmf, mc_smooth_window)
    err_s = _smooth(err, mc_smooth_window)

    ax_lin.errorbar(centers, pmf_s, yerr=err_s, fmt="o", ms=3.2, color="#1f78b4", alpha=0.75, label="MC (binned)")
    ax_log.plot(centers, np.where(pmf_s >= log_eps, pmf_s, np.nan), "o", ms=3.0, color="#1f78b4", alpha=0.75)

    t1, tv, t2 = peaks
    for ax in (ax_lin, ax_log):
        for tt, lab in zip((t1, tv, t2), ("t1", "tv", "t2")):
            ax.axvline(tt, color="0.4", ls="--", lw=0.9)
            ax.annotate(lab, xy=(tt, 0.9), xycoords=("data", "axes fraction"), fontsize=8, color="0.35")
        ax.set_xlim(t[0], t[-1])

    ax_lin.set_ylabel("f(t)")
    ax_log.set_ylabel("f(t)")
    ax_log.set_yscale("log")
    ax_lin.set_xlabel("t")
    ax_log.set_xlabel("t")
    ax_lin.set_title("FPT (linear)")
    ax_log.set_title("FPT (log)")
    ax_lin.legend(frameon=False, fontsize=8, loc="upper right")


def plot_fpt(
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
    dpi: int = 600,
) -> None:
    set_style("fig3")
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 3.6), constrained_layout=True)
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
        ax_lin=axes[0],
        ax_log=axes[1],
    )

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=dpi)
    fig.savefig(outpath.with_suffix(".png"), dpi=dpi)
    plt.close(fig)


def plot_channel_mix(
    *,
    t: np.ndarray,
    f_fast: np.ndarray,
    f_slow: np.ndarray,
    p_fast: float,
    p_slow: float,
    outpath: Path,
    dpi: int = 600,
) -> None:
    set_style("fig3")
    fig, ax = plt.subplots(figsize=(6.4, 3.6), constrained_layout=True)

    f_mix = p_fast * f_fast + p_slow * f_slow
    ax.fill_between(t, p_fast * f_fast, color="#fdae61", alpha=0.35, label=f"fast (P={p_fast:.2f})")
    ax.fill_between(t, p_slow * f_slow, color="#66c2a5", alpha=0.35, label=f"slow (P={p_slow:.2f})")
    ax.plot(t, f_mix, color="black", lw=1.6, label="mixture")

    ax.set_xlabel("t")
    ax.set_ylabel("weighted f(t)")
    ax.set_title("Channel decomposition")
    ax.legend(frameon=False, fontsize=8, loc="upper right")

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=dpi)
    fig.savefig(outpath.with_suffix(".png"), dpi=dpi)
    plt.close(fig)
