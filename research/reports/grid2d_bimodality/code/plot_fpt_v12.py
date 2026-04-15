#!/usr/bin/env python3
"""FPT plots for v12 (multiscale + bimodality proof + diagnostics)."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plot_style_v12 import apply_style_v12, compute_bimodality_metrics, save_clean, smooth_ma

VALLEY_RATIO_MAX = 0.07


def _windowed_peak_indices(
    t: np.ndarray,
    f_s: np.ndarray,
    *,
    early_window: Tuple[int, int],
    late_window: Tuple[int, int],
) -> Tuple[int, int]:
    early_idx = np.where((t >= early_window[0]) & (t <= early_window[1]))[0]
    late_idx = np.where((t >= late_window[0]) & (t <= late_window[1]))[0]
    if early_idx.size == 0 or late_idx.size == 0:
        raise ValueError("Empty window for windowed peak detection.")
    p1 = int(early_idx[np.argmax(f_s[early_idx])])
    p2 = int(late_idx[np.argmax(f_s[late_idx])])
    if p2 <= p1:
        raise ValueError("Late peak index is not after early peak; adjust windows.")
    return p1, p2


def _annotate_peaks(ax: plt.Axes, peaks: Tuple[int, int, int], *, xlim: Tuple[int, int]) -> None:
    t1, tv, t2 = peaks
    y1 = 0.90
    yv = 0.78 if abs(tv - t1) < 3 else 0.84
    y2 = 0.66 if abs(t2 - tv) < 3 else 0.74
    labels = [(t1, "t1", "#2ca25f", y1), (tv, "tv", "#636363", yv), (t2, "t2", "#756bb1", y2)]
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


def plot_fpt_multiscale_v12(
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
    dpi: int = 800,
    early_window: Tuple[int, int] | None = None,
    slow_window: Tuple[int, int] | None = None,
    auto_slow_ylim: bool = False,
    mc_smooth_window_slow: int | None = None,
) -> None:
    apply_style_v12()
    fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.2), constrained_layout=True)
    t1, tv, t2 = peaks
    t_max = int(t_exact[-1])

    if early_window is None:
        w_pre, w_post = 20, 40
        early_window = (max(1, t1 - w_pre), min(t_max, t1 + w_post))
    if slow_window is None:
        W_pre, W_post = 40, 80
        slow_window = (max(1, t2 - W_pre), min(t_max, t2 + W_post))

    mc_pmf_slow = None
    if mc_smooth_window_slow is not None and mc_smooth_window_slow > 1:
        mc_pmf_slow = smooth_ma(mc_pmf, int(mc_smooth_window_slow))

    def _plot(
        ax: plt.Axes,
        xlim: Tuple[int, int],
        logy: bool,
        auto_ylim: bool = False,
        mc_override: np.ndarray | None = None,
    ) -> None:
        mc_source = mc_override if mc_override is not None else mc_pmf
        if logy:
            f_exact_plot = np.where(f_exact > log_eps, f_exact, np.nan)
            f_aw_plot = np.where(f_aw > log_eps, f_aw, np.nan) if f_aw.size else f_aw
            mc_plot = np.where(mc_source > log_eps, mc_source, np.nan)
        else:
            f_exact_plot = f_exact
            f_aw_plot = f_aw
            mc_plot = mc_source
        ax.plot(t_exact, f_exact_plot, color="black", lw=1.8, label="Exact")
        if f_aw.size:
            ax.plot(t_aw, f_aw_plot, color="#d95f02", lw=1.6, ls="--", label="AW")
        ax.plot(mc_centers, mc_plot, color="#1f78b4", lw=1.2, alpha=0.85, label="MC")
        ax.set_xlim(xlim)
        ax.set_xlabel("t")
        ax.set_ylabel("f(t)")
        if logy:
            ax.set_yscale("log")
            positive = f_exact[f_exact > 0]
            y_min = max(log_eps, float(np.min(positive)) if positive.size else log_eps)
            ax.set_ylim(y_min, float(np.max(f_exact)) * 1.2)
        elif auto_ylim:
            mask = (t_exact >= xlim[0]) & (t_exact <= xlim[1])
            if np.any(mask):
                y_max = float(np.max(f_exact[mask]))
                ax.set_ylim(0.0, 1.15 * y_max if y_max > 0 else 1.0)
        _annotate_peaks(ax, peaks, xlim=xlim)

    _plot(axes[0], (1, t_max), logy=True)
    axes[0].set_title("global (log-y)")

    _plot(axes[1], early_window, logy=False)
    axes[1].set_title("early peak window")

    _plot(axes[2], slow_window, logy=False, auto_ylim=auto_slow_ylim, mc_override=mc_pmf_slow)
    axes[2].set_title("slow peak window")

    axes[0].legend(frameon=False, loc="upper right")

    save_clean(fig, outpath, dpi=dpi)


def plot_channel_decomp_v12(
    *,
    t: np.ndarray,
    f_fast: np.ndarray,
    f_slow: np.ndarray,
    p_fast: float,
    p_slow: float,
    outpath: Path,
    dpi: int = 800,
    tail_zoom: bool = False,
) -> None:
    apply_style_v12()
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
    metrics: dict,
    t_max_zoom: int,
    outpath: Path,
    log_eps: float,
    dpi: int = 800,
) -> dict:
    apply_style_v12()
    t_p1 = int(metrics["t_p1"])
    t_v = int(metrics["t_v"])
    t_p2 = int(metrics["t_p2"])

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.6), constrained_layout=True)
    t_mask = t <= t_max_zoom

    def _plot(ax: plt.Axes, logy: bool, xlim: Tuple[int, int]) -> None:
        if logy:
            f_plot = np.where(f_exact > log_eps, f_exact, np.nan)
            f_aw_plot = np.where(f_aw > log_eps, f_aw, np.nan) if f_aw.size else f_aw
        else:
            f_plot = f_exact
            f_aw_plot = f_aw
        ax.plot(t[t_mask], f_plot[t_mask], color="black", lw=1.8, label="Exact")
        if f_aw.size:
            ax.plot(t[t_mask], f_aw_plot[t_mask], color="#d95f02", lw=1.4, ls="--", label="AW")
        _annotate_peaks(ax, (t_p1, t_v, t_p2), xlim=xlim)
        ax.set_xlim(*xlim)
        ax.set_xlabel("t")
        ax.set_ylabel("f(t)")
        if logy:
            ax.set_yscale("log")
            ax.set_title("early window (semilogy)")
        else:
            ax.set_title("valley + slow peak")

    left_max = min(t_max_zoom, t_p1 + 40)
    _plot(axes[0], logy=True, xlim=(max(1, t_p1 - 20), left_max))

    right_left = max(1, t_v - 60)
    right_right = min(t_max_zoom, t_p2 + 80)
    _plot(axes[1], logy=False, xlim=(right_left, right_right))

    axes[0].legend(frameon=False, loc="upper right")

    axes[1].text(
        0.02,
        0.98,
        f"t_p1={t_p1}, t_v={t_v}, t_p2={t_p2}\n"
        f"h2/h1={metrics['h2_over_h1']:.3g}\n"
        f"valley_ratio={metrics['valley_ratio']:.3g}",
        transform=axes[1].transAxes,
        ha="left",
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7", alpha=0.85),
    )

    save_clean(fig, outpath, dpi=dpi)
    return metrics


def plot_bimodality_diagnostic_v12(
    *,
    t: np.ndarray,
    f_exact: np.ndarray,
    smooth_window: int,
    outpath: Path,
    prominence: float,
    distance: int,
    min_gap: int,
    valley_ratio_max: float = VALLEY_RATIO_MAX,
    method: str = "peaks",
    early_window: Tuple[int, int] | None = None,
    late_window: Tuple[int, int] | None = None,
    dpi: int = 800,
) -> dict:
    apply_style_v12()
    f_s = smooth_ma(f_exact, smooth_window)
    if method == "windowed":
        if early_window is None or late_window is None:
            raise ValueError("windowed method requires early_window and late_window.")
        p1, p2 = _windowed_peak_indices(t, f_s, early_window=early_window, late_window=late_window)
        peak_marks = np.array([p1, p2], dtype=int)
        header = "method=windowed"
    else:
        try:
            from scipy.signal import find_peaks

            peaks, _ = find_peaks(f_s, prominence=prominence, distance=distance)
        except Exception:
            peaks = np.where((f_s[1:-1] > f_s[:-2]) & (f_s[1:-1] > f_s[2:]))[0] + 1
        peaks = peaks[np.argsort(f_s[peaks])[::-1]]
        if peaks.size < 2:
            raise ValueError("Failed to find two peaks for diagnostic.")
        p1, p2 = sorted(peaks[:2].tolist())
        peak_marks = peaks
        header = f"prominence>={prominence:.1e}"
    v = int(p1 + np.argmin(f_s[p1 : p2 + 1]))
    h1 = float(f_s[p1])
    h2 = float(f_s[p2])
    hv = float(f_s[v])
    valley_ratio = hv / min(h1, h2) if min(h1, h2) > 0 else 1.0
    gap = int(t[p2] - t[p1])
    passes = (gap >= min_gap) and (valley_ratio <= valley_ratio_max)

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), constrained_layout=True)

    axes[0].plot(t, f_exact, color="black", lw=1.6, label="Exact")
    axes[0].plot(t, f_s, color="#1f78b4", lw=1.4, label="Smoothed")
    axes[0].set_title("raw vs smoothed")
    axes[0].set_xlabel("t")
    axes[0].set_ylabel("f(t)")
    axes[0].legend(frameon=False, loc="upper right")

    axes[1].plot(t, f_s, color="#1f78b4", lw=1.4)
    axes[1].scatter(t[peak_marks], f_s[peak_marks], color="#e31a1c", s=30, zorder=5)
    axes[1].axvline(t[p1], color="#2ca25f", ls=":", lw=1.2)
    axes[1].axvline(t[p2], color="#756bb1", ls=":", lw=1.2)
    axes[1].set_title("peaks on smoothed")
    axes[1].set_xlabel("t")

    axes[2].plot(t, f_s, color="#1f78b4", lw=1.4)
    axes[2].axvline(t[p1], color="#2ca25f", ls=":", lw=1.0)
    axes[2].axvline(t[p2], color="#756bb1", ls=":", lw=1.0)
    axes[2].axvline(t[v], color="#636363", ls="--", lw=1.2)
    axes[2].set_title("valley diagnostic")
    axes[2].set_xlabel("t")

    conclusion = (
        f"{header}\n"
        f"valley_ratio<={valley_ratio_max:.2f}, Δt>={min_gap}\n"
        f"t_p1={t[p1]}, t_v={t[v]}, t_p2={t[p2]}"
    )
    axes[2].text(
        0.02,
        0.98,
        conclusion,
        transform=axes[2].transAxes,
        ha="left",
        va="top",
        fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7", alpha=0.85),
    )

    save_clean(fig, outpath, dpi=dpi)
    return {
        "t_p1": int(t[p1]),
        "t_v": int(t[v]),
        "t_p2": int(t[p2]),
        "gap": gap,
        "valley_ratio": float(valley_ratio),
        "passes": bool(passes),
        "method": str(method),
    }
