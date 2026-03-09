#!/usr/bin/env python3
"""Build report assets for 2D membrane corridor + near-start two-target study."""

from __future__ import annotations

import csv
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from vkcore.grid2d.rect_bimodality.cli import (
    build_ot_case_geometry,
    build_transition_arrays_general_rect,
    classify_phase_one_target,
    classify_phase_two_target,
    run_exact_one_target_rect,
    run_exact_two_target_rect,
    summarize_one_target,
    summarize_two_target,
)

Coord = Tuple[int, int]
Edge = Tuple[Coord, Coord]


def idx(x: int, y: int, Lx: int) -> int:
    return y * Lx + x


def _edge_key(a: Coord, b: Coord) -> Edge:
    return (a, b) if a <= b else (b, a)


def _edge_idx_key(a: int, b: int) -> Tuple[int, int]:
    return (a, b) if a <= b else (b, a)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_csv(path: Path, rows: Sequence[dict], fieldnames: Sequence[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def save_time_series(path: Path, f_total: np.ndarray, f_a: np.ndarray, f_b: np.ndarray) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["t", "f_total", "f_a", "f_b"])
        n = int(len(f_total))
        for t in range(n):
            w.writerow([t, float(f_total[t]), float(f_a[t]), float(f_b[t])])


def save_figure(fig: plt.Figure, out_path: Path) -> None:
    ensure_dir(out_path.parent)
    fig.savefig(out_path, dpi=220, bbox_inches="tight", pad_inches=0.03)
    if out_path.suffix.lower() == ".pdf":
        png_path = out_path.with_suffix(".png")
        fig.savefig(png_path, dpi=220, bbox_inches="tight", pad_inches=0.03)


def smooth_series(y: np.ndarray, window: int = 7) -> np.ndarray:
    w = int(max(1, window))
    if w <= 1 or y.size < w:
        return y.astype(np.float64, copy=True)
    if w % 2 == 0:
        w += 1
    pad = w // 2
    ypad = np.pad(y.astype(np.float64), (pad, pad), mode="edge")
    kernel = np.ones(w, dtype=np.float64) / float(w)
    return np.convolve(ypad, kernel, mode="valid")


def plot_heatmap(
    out_path: Path,
    data: np.ndarray,
    *,
    x_labels: Sequence[str],
    y_labels: Sequence[str],
    title: str,
    cmap: str,
    cbar_label: str,
    annotate_fmt: str = "{:.0f}",
) -> None:
    ensure_dir(out_path.parent)
    fig_w = max(7.2, 3.0 + 0.42 * len(x_labels))
    fig_h = max(4.8, 2.6 + 0.34 * len(y_labels))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    im = ax.imshow(data, origin="lower", cmap=cmap, aspect="auto")
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)
    if len(x_labels) > 8:
        plt.setp(ax.get_xticklabels(), rotation=35, ha="right", rotation_mode="anchor", fontsize=8)
    if len(y_labels) > 10:
        plt.setp(ax.get_yticklabels(), fontsize=8)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title)
    cell_count = int(data.shape[0] * data.shape[1])
    if cell_count <= 120:
        ann_font = 6 if cell_count >= 90 else 7
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                val = float(data[i, j])
                txt = annotate_fmt.format(val)
                ax.text(j, i, txt, ha="center", va="center", fontsize=ann_font, color="black")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(cbar_label)
    fig.tight_layout()
    save_figure(fig, out_path)
    plt.close(fig)


def plot_fpt_overlay(
    out_path: Path,
    *,
    t: np.ndarray,
    f_total: np.ndarray,
    f_a: np.ndarray,
    f_b: np.ndarray,
    label_a: str,
    label_b: str,
    title: str,
    peaks: Tuple[int | None, int | None, int | None],
) -> None:
    ensure_dir(out_path.parent)
    fs = smooth_series(f_total, window=7)
    fa = smooth_series(f_a, window=7)
    fb = smooth_series(f_b, window=7)

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.plot(t, fs, color="#111111", lw=1.8, label="total")
    ax.plot(t, fa, color="#1f77b4", lw=1.5, label=label_a)
    ax.plot(t, fb, color="#ff7f0e", lw=1.5, label=label_b)

    tp1, tv, tp2 = peaks
    if tp1 is not None:
        ax.axvline(int(tp1), color="#1f77b4", ls="--", lw=1.0, alpha=0.7)
        ax.text(int(tp1), float(np.max(fs)) * 0.96, "p1", color="#1f77b4", fontsize=8, ha="left", va="top")
    if tv is not None:
        ax.axvline(int(tv), color="#666666", ls=":", lw=1.0, alpha=0.8)
        ax.text(int(tv), float(np.max(fs)) * 0.88, "valley", color="#444444", fontsize=8, ha="left", va="top")
    if tp2 is not None:
        ax.axvline(int(tp2), color="#ff7f0e", ls="--", lw=1.0, alpha=0.7)
        ax.text(int(tp2), float(np.max(fs)) * 0.80, "p2", color="#ff7f0e", fontsize=8, ha="left", va="top")

    ax.set_xlim(0, min(len(t) - 1, max(350, int(np.argmax(fs) * 4 + 150))))
    ax.set_xlabel("t")
    ax.set_ylabel("FPT pmf")
    ax.set_title(title)
    ax.grid(alpha=0.22)
    ax.legend(loc="upper right", fontsize=8)
    save_figure(fig, out_path)
    plt.close(fig)


def plot_two_target_doublepeak_example(
    out_path: Path,
    *,
    t: np.ndarray,
    f_total: np.ndarray,
    f_near: np.ndarray,
    f_far: np.ndarray,
    peaks: Tuple[int | None, int | None, int | None],
    title: str,
    sep_score: float | None = None,
    valley_ratio: float | None = None,
    p_near: float | None = None,
    p_far: float | None = None,
    peak_ratio: float | None = None,
    peak_margin: float | None = None,
    min_margin: float | None = None,
    selection_gate: str | None = None,
) -> None:
    ensure_dir(out_path.parent)
    fs = smooth_series(f_total, window=7)
    fn = smooth_series(f_near, window=7)
    ff = smooth_series(f_far, window=7)
    tp1, tv, tp2 = peaks

    xmax = len(t) - 1
    if tp1 is not None and tp2 is not None:
        gap = max(220, int(tp2) - int(tp1))
        xmax = min(xmax, max(900, int(tp2) + max(160, gap // 3)))
    elif tp2 is not None:
        xmax = min(xmax, max(900, int(tp2) + 220))
    else:
        xmax = min(xmax, 900)

    # Improve readability: keep linear panel focused on valley/second-peak structure.
    tail_start = max(60, int(tp1) + 40 if tp1 is not None else 120)
    tail_start = min(max(1, tail_start), len(t) - 1)
    tail_peak = float(max(np.max(fs[tail_start:]), np.max(fn[tail_start:]), np.max(ff[tail_start:])))
    lin_ymax = max(6.0e-4, 1.35 * tail_peak)
    log_ymin = 1.0e-6
    log_ymax = max(1.0e-2, 1.6 * float(max(np.max(fs), np.max(fn), np.max(ff))))

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.6), sharex=True)
    specs = [
        (axes[0], False, "pmf (linear, zoomed)"),
        (axes[1], True, "pmf (log)"),
    ]
    for ax, use_log, ylab in specs:
        y_total = np.maximum(fs, 1e-15) if use_log else fs
        y_near = np.maximum(fn, 1e-15) if use_log else fn
        y_far = np.maximum(ff, 1e-15) if use_log else ff

        if use_log:
            ax.semilogy(t, y_total, color="#111111", lw=1.7, label="total")
            ax.semilogy(t, y_near, color="#1f77b4", lw=1.4, label="near target")
            ax.semilogy(t, y_far, color="#ff7f0e", lw=1.4, label="far target")
        else:
            ax.plot(t, y_total, color="#111111", lw=1.7, label="total")
            ax.plot(t, y_near, color="#1f77b4", lw=1.4, label="near target")
            ax.plot(t, y_far, color="#ff7f0e", lw=1.4, label="far target")

        for mark_x, color, label in [
            (tp1, "#1f77b4", "p1"),
            (tv, "#666666", "valley"),
            (tp2, "#ff7f0e", "p2"),
        ]:
            if mark_x is None:
                continue
            ax.axvline(int(mark_x), color=color, ls="--" if label != "valley" else ":", lw=1.0, alpha=0.75)
            y_raw = float(y_total[min(int(mark_x), len(y_total) - 1)])
            if use_log:
                y_ref = max(y_raw, log_ymin * 1.05)
                y_txt = min(y_ref * 1.20, log_ymax * 0.92)
                label_txt = label
            else:
                clipped = y_raw > lin_ymax
                y_ref = min(y_raw, lin_ymax * 0.985)
                y_txt = min(y_ref * 1.06, lin_ymax * 0.99)
                label_txt = f"{label}*" if clipped else label
            ax.scatter([int(mark_x)], [y_ref], s=16, color=color, zorder=5)
            ax.text(int(mark_x) + 10, y_txt, label_txt, fontsize=8, color=color)

        for w_name, lo, hi in window_ranges(tp1, tv, tp2, len(t)):
            lo_i = max(1, int(lo))
            hi_i = min(len(t) - 1, int(hi))
            shade = "#dceef8" if w_name != "valley" else "#f4eadc"
            ax.axvspan(lo_i, hi_i, color=shade, alpha=0.25, lw=0)

        ax.set_xlim(0, xmax)
        if use_log:
            ax.set_ylim(log_ymin, log_ymax)
        else:
            ax.set_ylim(0.0, lin_ymax)
            if tp1 is not None and fs[min(int(tp1), len(fs) - 1)] > lin_ymax:
                clip_note_y = 0.93
                if any(
                    v is not None
                    for v in (
                        sep_score,
                        valley_ratio,
                        p_near,
                        p_far,
                        peak_ratio,
                        peak_margin,
                        min_margin,
                        selection_gate,
                    )
                ):
                    clip_note_y = 0.66
                ax.text(
                    0.02,
                    clip_note_y,
                    f"* p1 clipped (true p1={fs[min(int(tp1), len(fs) - 1)]:.2e})",
                    transform=ax.transAxes,
                    fontsize=7,
                    color="#1f77b4",
                    va="top",
                )
        ax.set_xlabel("t")
        ax.set_ylabel(ylab)
        ax.grid(alpha=0.20)

    if any(v is not None for v in (sep_score, valley_ratio, p_near, p_far)):
        items: List[str] = []
        if sep_score is not None:
            items.append(f"sep={float(sep_score):.2f}")
        if valley_ratio is not None:
            items.append(f"valley/max={float(valley_ratio):.3f}")
        if p_near is not None and p_far is not None:
            items.append(f"Pnear={float(p_near):.3f}, Pfar={float(p_far):.3f}")
        if peak_ratio is not None:
            items.append(f"peak-ratio={float(peak_ratio):.3f}")
        if peak_margin is not None:
            items.append(f"peak-margin={float(peak_margin):.3f}")
        if min_margin is not None:
            items.append(f"min-margin={float(min_margin):.3f}")
        if selection_gate is not None and str(selection_gate).strip():
            items.append(f"gate={str(selection_gate)}")
        axes[0].text(
            0.02,
            0.98,
            "\n".join(items),
            transform=axes[0].transAxes,
            ha="left",
            va="top",
            fontsize=8,
            color="#202020",
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#666666", lw=0.7, alpha=0.93),
        )

    axes[0].set_title("Linear view (tail emphasis)", fontsize=10)
    axes[1].set_title("Same case (log scale, y>=1e-6)", fontsize=10)
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=3, fontsize=8)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    save_figure(fig, out_path)
    plt.close(fig)


def _draw_lattice(ax: plt.Axes, *, Lx: int, Wy: int, major_step: int = 5) -> None:
    for x in range(Lx + 1):
        lw = 0.55 if x % major_step == 0 else 0.28
        color = "#9aa0a6" if x % major_step == 0 else "#d4d7db"
        ax.plot([x - 0.5, x - 0.5], [-0.5, Wy - 0.5], color=color, lw=lw, zorder=1)
    for y in range(Wy + 1):
        lw = 0.55 if y % major_step == 0 else 0.28
        color = "#9aa0a6" if y % major_step == 0 else "#d4d7db"
        ax.plot([-0.5, Lx - 0.5], [y - 0.5, y - 0.5], color=color, lw=lw, zorder=1)


def plot_membrane_geometry(
    out_path: Path,
    *,
    Lx: int,
    case: dict,
    title: str,
) -> None:
    ensure_dir(out_path.parent)
    Wy = int(case["Wy"])
    start = case["start"]
    target = case["target"]
    y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    k_top = float(case["kappa_top"])
    k_bottom = float(case["kappa_bottom"])

    fig, ax = plt.subplots(figsize=(10.8, 4.4))
    ax.set_facecolor("#f5f3eb")

    # Corridor band shading.
    for y in range(y_low, y_high + 1):
        ax.add_patch(
            plt.Rectangle(
                (-0.5, y - 0.5),
                float(Lx),
                1.0,
                facecolor="#cde8f3",
                edgecolor="none",
                alpha=0.45,
                zorder=0,
            )
        )
    ax.add_patch(
        plt.Rectangle(
            (x0 - 0.5, y_low - 0.5),
            float(x1 - x0 + 1),
            float(y_high - y_low + 1),
            facecolor="#9ecae1",
            edgecolor="none",
            alpha=0.35,
            zorder=0,
        )
    )

    _draw_lattice(ax, Lx=Lx, Wy=Wy)

    # Membrane boundaries with width proportional to reflection strength.
    def _line_alpha(kappa: float) -> float:
        return 0.35 + 0.55 * (1.0 - max(0.0, min(1.0, kappa)))

    if y_low > 0:
        ax.plot(
            [x0 - 0.5, x1 + 0.5],
            [y_low - 0.5, y_low - 0.5],
            color="#2d2d2d",
            lw=2.1,
            linestyle=(0, (4, 2)),
            alpha=_line_alpha(k_bottom),
            zorder=4,
        )
    if y_high < Wy - 1:
        ax.plot(
            [x0 - 0.5, x1 + 0.5],
            [y_high + 0.5, y_high + 0.5],
            color="#111111",
            lw=2.1,
            alpha=_line_alpha(k_top),
            zorder=4,
        )

    # Eastward local-bias hints along the centerline.
    for x in range(max(1, x0 + 1), min(Lx - 2, x1), 5):
        ax.annotate(
            "",
            xy=(x + 0.45, y_mid),
            xytext=(x - 0.45, y_mid),
            arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#ff5b4f", alpha=0.88, mutation_scale=10),
            zorder=5,
            clip_on=False,
        )

    ax.scatter([start[0]], [start[1]], s=66, marker="s", color="#e53935", zorder=6)
    ax.scatter([target[0]], [target[1]], s=80, marker="D", color="#1565c0", zorder=6)
    start_text_x = max(0.6, float(start[0]) - 2.0)
    start_text_y = min(float(Wy) - 1.0, float(start[1]) + 1.9)
    target_text_x = max(0.8, float(target[0]) - 5.5)
    target_text_y = min(float(Wy) - 1.0, float(target[1]) + 1.9)
    ax.annotate(
        "start",
        xy=(start[0], start[1]),
        xytext=(start_text_x, start_text_y),
        fontsize=8,
        color="#b71c1c",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#b71c1c", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#b71c1c", mutation_scale=9),
        zorder=8,
    )
    ax.annotate(
        "target",
        xy=(target[0], target[1]),
        xytext=(target_text_x, target_text_y),
        fontsize=8,
        color="#0d47a1",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#0d47a1", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#0d47a1", mutation_scale=9),
        zorder=8,
    )

    info_text = (
        f"Wy={Wy}, bx={float(case['bx']):+.2f}, h={int(case.get('corridor_halfwidth', 1))}, m={int(case.get('wall_margin', 5))}\n"
        f"k_up={k_top:.3f}, k_dn={k_bottom:.3f}"
    )
    ax.text(
        0.01,
        0.98,
        info_text,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#222222",
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#777777", lw=0.7, alpha=0.92),
        zorder=8,
    )

    ax.set_xlim(-0.5, Lx - 0.5)
    ax.set_ylim(-0.5, Wy - 0.5)
    ax.set_aspect("equal")
    ax.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)
    for s in ax.spines.values():
        s.set_linewidth(1.4)
        s.set_color("#000000")
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    save_figure(fig, out_path)
    plt.close(fig)


def plot_two_target_geometry(
    out_path: Path,
    *,
    Lx: int,
    case: dict,
    title: str,
) -> None:
    ensure_dir(out_path.parent)
    Wy = int(case["Wy"])
    start = case["start"]
    near = case["near"]
    far = case["far"]
    bx = float(case["bx"])

    fig, ax = plt.subplots(figsize=(10.8, 4.2))
    ax.set_facecolor("#f5f3eb")
    _draw_lattice(ax, Lx=Lx, Wy=Wy)

    # Drift guide arrows.
    y_mid = int((Wy - 1) // 2)
    arrow_color = "#ff5b4f" if bx >= 0 else "#4f79ff"
    for x in range(1, Lx - 2, 6):
        dx = 1.0 if bx >= 0 else -1.0
        ax.annotate(
            "",
            xy=(x + 0.5 * dx, y_mid),
            xytext=(x - 0.5 * dx, y_mid),
            arrowprops=dict(arrowstyle="-|>", lw=1.0, color=arrow_color, alpha=0.82, mutation_scale=10),
            zorder=4,
            clip_on=False,
        )

    ax.scatter([start[0]], [start[1]], s=66, marker="s", color="#e53935", zorder=6)
    ax.scatter([near[0]], [near[1]], s=80, marker="D", color="#1f77b4", zorder=6)
    ax.scatter([far[0]], [far[1]], s=80, marker="o", color="#ff7f0e", zorder=6)
    start_text_x = max(0.6, float(start[0]) - 2.0)
    start_text_y = min(float(Wy) - 1.0, float(start[1]) + 1.8)
    near_text_x = min(float(Lx) - 2.5, float(near[0]) + 1.0)
    near_text_y = min(float(Wy) - 1.0, float(near[1]) + 1.6)
    far_text_x = max(0.8, float(far[0]) - 3.8)
    far_text_y = min(float(Wy) - 1.0, float(far[1]) + 1.7)

    ax.annotate(
        "start",
        xy=(start[0], start[1]),
        xytext=(start_text_x, start_text_y),
        fontsize=8,
        color="#b71c1c",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#b71c1c", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#b71c1c", mutation_scale=9),
        zorder=8,
    )
    ax.annotate(
        "near",
        xy=(near[0], near[1]),
        xytext=(near_text_x, near_text_y),
        fontsize=8,
        color="#0d47a1",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#0d47a1", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#0d47a1", mutation_scale=9),
        zorder=8,
    )
    ax.annotate(
        "far",
        xy=(far[0], far[1]),
        xytext=(far_text_x, far_text_y),
        fontsize=8,
        color="#a84300",
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#a84300", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#a84300", mutation_scale=9),
        zorder=8,
    )
    ax.text(
        0.01,
        0.98,
        f"Wy={Wy}, bx={bx:+.2f}, near_dx={int(case['near_dx'])}, near_dy={int(case['near_dy'])}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#222222",
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#777777", lw=0.7, alpha=0.92),
    )

    ax.set_xlim(-0.5, Lx - 0.5)
    ax.set_ylim(-0.5, Wy - 0.5)
    ax.set_aspect("equal")
    ax.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)
    for s in ax.spines.values():
        s.set_linewidth(1.4)
        s.set_color("#000000")
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    save_figure(fig, out_path)
    plt.close(fig)


def plot_stacked_windows(
    out_path: Path,
    *,
    windows: Sequence[str],
    categories: Sequence[str],
    proportions: np.ndarray,
    title: str,
    palette: Sequence[str],
) -> None:
    ensure_dir(out_path.parent)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    x = np.arange(len(windows))
    bottom = np.zeros(len(windows), dtype=float)
    for k, cat in enumerate(categories):
        vals = proportions[:, k]
        ax.bar(x, vals, bottom=bottom, label=cat, color=palette[k], alpha=0.90)
        bottom += vals
    ax.set_xticks(x)
    ax.set_xticklabels(windows)
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("fraction")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    save_figure(fig, out_path)
    plt.close(fig)


def plot_dual_window_panels(
    out_path: Path,
    *,
    windows: Sequence[str],
    categories: Sequence[str],
    left_props: np.ndarray,
    right_props: np.ndarray,
    left_title: str,
    right_title: str,
) -> None:
    ensure_dir(out_path.parent)
    palette = ["#2a9d8f", "#8ab17d", "#e9c46a", "#e76f51"]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2), sharey=True)
    for ax, props, title in [
        (axes[0], left_props, left_title),
        (axes[1], right_props, right_title),
    ]:
        x = np.arange(len(windows))
        bottom = np.zeros(len(windows), dtype=float)
        for k, cat in enumerate(categories):
            vals = props[:, k]
            ax.bar(x, vals, bottom=bottom, label=cat, color=palette[k], alpha=0.90)
            bottom += vals
        ax.set_xticks(x)
        ax.set_xticklabels(windows)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("fraction")
    axes[0].set_ylim(0.0, 1.0)
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=4, fontsize=8)
    fig.suptitle("Window-wise class composition", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    save_figure(fig, out_path)
    plt.close(fig)


def plot_membrane_class_legend(
    out_path: Path,
    *,
    window_names: Sequence[str] | None = None,
    dominant_classes: Sequence[str] | None = None,
) -> None:
    ensure_dir(out_path.parent)
    palette = {
        "L0R0": "#2a9d8f",
        "L0R1": "#8ab17d",
        "L1R0": "#e9c46a",
        "L1R1": "#e76f51",
    }

    fig, (ax_l, ax_r) = plt.subplots(
        1,
        2,
        figsize=(11.0, 4.2),
        gridspec_kw={"width_ratios": [1.05, 1.35]},
    )

    # Left panel: 2x2 class cells.
    ax_l.set_title("L x R class legend", fontsize=10)
    ax_l.set_xlim(0.0, 2.0)
    ax_l.set_ylim(0.0, 2.0)
    ax_l.set_aspect("equal")
    ax_l.set_xticks([0.5, 1.5])
    ax_l.set_xticklabels(["L=0\nno leak", "L=1\nleak"], fontsize=8)
    ax_l.set_yticks([1.5, 0.5])
    ax_l.set_yticklabels(["R=0\nno recross", "R=1\nrecross"], fontsize=8)

    cell_spec = [
        (0.0, 1.0, "L0R0", "direct"),
        (1.0, 1.0, "L1R0", "leak only"),
        (0.0, 0.0, "L0R1", "recross only"),
        (1.0, 0.0, "L1R1", "leak + recross"),
    ]
    for x0, y0, cls, desc in cell_spec:
        rect = plt.Rectangle(
            (x0, y0),
            1.0,
            1.0,
            facecolor=palette[cls],
            edgecolor="#ffffff",
            linewidth=1.6,
            alpha=0.92,
        )
        ax_l.add_patch(rect)
        ax_l.text(x0 + 0.5, y0 + 0.63, cls, ha="center", va="center", fontsize=9, color="#111111", weight="bold")
        ax_l.text(x0 + 0.5, y0 + 0.33, desc, ha="center", va="center", fontsize=8, color="#111111")

    for s in ax_l.spines.values():
        s.set_color("#666666")
        s.set_linewidth(1.0)

    # Right panel: representative window transfer.
    ax_r.set_title("Representative window transfer", fontsize=10)
    ax_r.set_xlim(0.0, 3.0)
    ax_r.set_ylim(0.0, 1.0)
    ax_r.axis("off")

    window_colors = ["#eef4f3", "#f5efe6", "#eef4f3"]
    wnames = list(window_names) if window_names is not None else ["peak1", "valley", "peak2"]
    dominant = list(dominant_classes) if dominant_classes is not None else ["L0R0", "L1R1", "L1R1"]
    if len(dominant) != len(wnames):
        dominant = ["L0R0", "L1R1", "L1R1"]
    if len(wnames) == 3:
        wcols = window_colors
    else:
        wcols = ["#eef4f3" for _ in wnames]
    ax_r.set_xlim(0.0, float(len(wnames)))
    for i, wn in enumerate(wnames):
        ax_r.add_patch(plt.Rectangle((i, 0.12), 1.0, 0.76, facecolor=wcols[i], edgecolor="#d0d0d0", lw=1.0))
        ax_r.text(i + 0.5, 0.82, wn, ha="center", va="center", fontsize=9, color="#222222")
        cls = dominant[i]
        ax_r.scatter(i + 0.5, 0.50, s=420, color=palette[cls], edgecolor="#222222", linewidth=0.7, zorder=3)
        ax_r.text(i + 0.5, 0.50, cls, ha="center", va="center", fontsize=8, color="#111111", weight="bold")

    arrow_kw = dict(arrowstyle="->", lw=1.5, color="#444444")
    for i in range(max(0, len(wnames) - 1)):
        ax_r.annotate("", xy=(i + 1.34, 0.50), xytext=(i + 0.68, 0.50), arrowprops=arrow_kw)
    ax_r.text(
        0.5 * float(len(wnames)),
        0.22,
        "Data-driven dominant classes across peak/valley windows",
        ha="center",
        va="center",
        fontsize=8,
        color="#333333",
    )

    fig.tight_layout()
    save_figure(fig, out_path)
    plt.close(fig)


def window_ranges(tp1: int | None, tv: int | None, tp2: int | None, n: int) -> List[Tuple[str, int, int]]:
    if tp1 is None or tv is None or tp2 is None:
        return [("early", 10, 60), ("middle", 120, 200), ("late", 260, 360)]
    gap = max(20, int(tp2) - int(tp1))
    half = int(max(8, min(26, gap // 7)))
    windows = [
        ("peak1", max(1, int(tp1) - half), min(n - 1, int(tp1) + half)),
        ("valley", max(1, int(tv) - half), min(n - 1, int(tv) + half)),
        ("peak2", max(1, int(tp2) - half), min(n - 1, int(tp2) + half)),
    ]
    return windows


def build_row_sampler(
    *,
    n_states: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    order = np.argsort(src_idx, kind="stable")
    src = src_idx[order]
    dst = dst_idx[order]
    p = probs[order]
    counts = np.bincount(src, minlength=n_states)
    offsets = np.zeros(n_states + 1, dtype=np.int64)
    offsets[1:] = np.cumsum(counts)

    dst_rows: List[np.ndarray] = []
    cdf_rows: List[np.ndarray] = []
    for i in range(n_states):
        a = int(offsets[i])
        b = int(offsets[i + 1])
        d = dst[a:b]
        pr = p[a:b]
        if d.size == 0:
            d = np.asarray([i], dtype=np.int64)
            pr = np.asarray([1.0], dtype=np.float64)
        cdf = np.cumsum(pr)
        cdf[-1] = 1.0
        dst_rows.append(d)
        cdf_rows.append(cdf)
    return dst_rows, cdf_rows


def sample_next_state(state: int, dst_rows: List[np.ndarray], cdf_rows: List[np.ndarray], rng: np.random.Generator) -> int:
    u = float(rng.random())
    cdf = cdf_rows[state]
    pos = int(np.searchsorted(cdf, u, side="left"))
    d = dst_rows[state]
    if pos >= d.size:
        pos = d.size - 1
    return int(d[pos])


def solve_committor(
    *,
    n_states: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    set_A: np.ndarray,
    set_B: np.ndarray,
    max_iter: int = 20000,
    tol: float = 1e-11,
) -> np.ndarray:
    q = np.zeros(n_states, dtype=np.float64)
    q[set_B] = 1.0
    fixed = np.zeros(n_states, dtype=bool)
    fixed[set_A] = True
    fixed[set_B] = True

    for _ in range(max_iter):
        acc = np.bincount(src_idx, weights=probs * q[dst_idx], minlength=n_states)
        acc[set_A] = 0.0
        acc[set_B] = 1.0
        diff = float(np.max(np.abs(acc - q)))
        q = acc
        if diff < tol:
            break
    return q


def committor_residual_stats(
    *,
    n_states: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    q_values: np.ndarray,
    set_A: np.ndarray,
    set_B: np.ndarray,
) -> dict:
    """Return Bellman residual and boundary mismatch diagnostics for q."""
    q_next = np.bincount(src_idx, weights=probs * q_values[dst_idx], minlength=int(n_states))
    interior = np.logical_not(np.logical_or(set_A, set_B))

    if np.any(interior):
        interior_res_inf = float(np.max(np.abs(q_values[interior] - q_next[interior])))
    else:
        interior_res_inf = 0.0

    if np.any(set_A):
        boundary_a_res_inf = float(np.max(np.abs(q_values[set_A])))
    else:
        boundary_a_res_inf = 0.0

    if np.any(set_B):
        boundary_b_res_inf = float(np.max(np.abs(q_values[set_B] - 1.0)))
    else:
        boundary_b_res_inf = 0.0

    return {
        "interior_residual_inf": interior_res_inf,
        "boundary_A_residual_inf": boundary_a_res_inf,
        "boundary_B_residual_inf": boundary_b_res_inf,
    }


def build_start_basin_mask(*, Lx: int, Wy: int, start_x: int, y_mid: int) -> np.ndarray:
    """Start basin A used by committor and strict recross definition."""
    n_states = int(Lx * Wy)
    A = np.zeros(n_states, dtype=bool)
    for y in range(Wy):
        for x in range(Lx):
            if x <= int(start_x) + 1 and abs(y - int(y_mid)) <= 1:
                A[idx(x, y, Lx)] = True
    return A


def _build_lr_exact_edges(
    *,
    n_states: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    q_values: np.ndarray,
    q_star: float,
    membrane_idx_edges: set[Tuple[int, int]],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build sparse transitions for augmented state (x,l,s,r), exact (non-MC)."""
    src = src_idx.astype(np.int64, copy=False)
    dst = dst_idx.astype(np.int64, copy=False)
    pr = probs.astype(np.float64, copy=False)

    is_hit = (dst == int(target_idx))
    is_mem = np.fromiter((_edge_idx_key(int(a), int(b)) in membrane_idx_edges for a, b in zip(src, dst)), dtype=bool, count=src.size)
    is_A_dst = set_A[dst]
    is_sigma_dst = q_values[dst] >= float(q_star)

    src_non = src[~is_hit]
    dst_non = dst[~is_hit]
    pr_non = pr[~is_hit]
    mem_non = is_mem[~is_hit]
    A_non = is_A_dst[~is_hit]
    sigma_non = is_sigma_dst[~is_hit]

    src_hit = src[is_hit]
    pr_hit = pr[is_hit]
    mem_hit = is_mem[is_hit]

    ext_src_parts: List[np.ndarray] = []
    ext_dst_parts: List[np.ndarray] = []
    ext_pr_parts: List[np.ndarray] = []
    hit_src_parts: List[np.ndarray] = []
    hit_cls_parts: List[np.ndarray] = []
    hit_pr_parts: List[np.ndarray] = []

    for flag in range(8):
        l = (flag & 1)
        s = ((flag >> 1) & 1)
        r = ((flag >> 2) & 1)
        base = int(flag * n_states)

        l2_non = np.logical_or(bool(l), mem_non)
        s2_non = np.logical_or(bool(s), sigma_non)
        r2_non = np.logical_or(bool(r), np.logical_and(bool(s), A_non))
        flag2_non = l2_non.astype(np.int64) + 2 * s2_non.astype(np.int64) + 4 * r2_non.astype(np.int64)

        ext_src_parts.append(base + src_non)
        ext_dst_parts.append(dst_non + flag2_non * int(n_states))
        ext_pr_parts.append(pr_non)

        l2_hit = np.logical_or(bool(l), mem_hit)
        cls_hit = (2 * l2_hit.astype(np.int64) + int(r)).astype(np.int64)  # 0:L0R0,1:L0R1,2:L1R0,3:L1R1
        hit_src_parts.append(base + src_hit)
        hit_cls_parts.append(cls_hit)
        hit_pr_parts.append(pr_hit)

    ext_src = np.concatenate(ext_src_parts) if ext_src_parts else np.empty(0, dtype=np.int64)
    ext_dst = np.concatenate(ext_dst_parts) if ext_dst_parts else np.empty(0, dtype=np.int64)
    ext_pr = np.concatenate(ext_pr_parts) if ext_pr_parts else np.empty(0, dtype=np.float64)
    hit_src_ext = np.concatenate(hit_src_parts) if hit_src_parts else np.empty(0, dtype=np.int64)
    hit_cls = np.concatenate(hit_cls_parts) if hit_cls_parts else np.empty(0, dtype=np.int64)
    hit_pr = np.concatenate(hit_pr_parts) if hit_pr_parts else np.empty(0, dtype=np.float64)

    return ext_src, ext_dst, ext_pr, hit_src_ext, hit_cls, hit_pr


def exact_lr_class_fpt(
    *,
    n_states: int,
    start_idx: int,
    src_idx: np.ndarray,
    dst_idx: np.ndarray,
    probs: np.ndarray,
    target_idx: int,
    set_A: np.ndarray,
    q_values: np.ndarray,
    q_star: float,
    membrane_idx_edges: set[Tuple[int, int]],
    t_max: int,
    surv_tol: float = 1e-12,
) -> Tuple[np.ndarray, np.ndarray]:
    """Exact class-resolved FPT pmf for classes [L0R0, L0R1, L1R0, L1R1]."""
    n_ext = int(n_states * 8)
    ext_src, ext_dst, ext_pr, hit_src_ext, hit_cls, hit_pr = _build_lr_exact_edges(
        n_states=n_states,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        target_idx=target_idx,
        set_A=set_A,
        q_values=q_values,
        q_star=q_star,
        membrane_idx_edges=membrane_idx_edges,
    )

    p = np.zeros(n_ext, dtype=np.float64)
    p[int(start_idx)] = 1.0  # (l,s,r)=(0,0,0)

    f_class = np.zeros((int(t_max) + 1, 4), dtype=np.float64)
    surv = np.zeros(int(t_max) + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, int(t_max) + 1):
        if hit_src_ext.size > 0:
            h = p[hit_src_ext] * hit_pr
            for cls in range(4):
                mask = (hit_cls == cls)
                if np.any(mask):
                    f_class[t, cls] = float(np.sum(h[mask]))

        p_next = np.zeros_like(p)
        if ext_src.size > 0:
            np.add.at(p_next, ext_dst, p[ext_src] * ext_pr)

        s = float(np.sum(p_next))
        if s < 0.0:
            s = 0.0
        surv[t] = s
        p = p_next

        if s < float(surv_tol):
            if t < int(t_max):
                surv[t + 1 :] = s
            break

    return f_class, surv


def window_fractions_from_fclass(
    *,
    f_class: np.ndarray,
    windows: Sequence[Tuple[str, int, int]],
) -> Dict[str, Dict[str, float]]:
    cats = ["L0R0", "L0R1", "L1R0", "L1R1"]
    out: Dict[str, Dict[str, float]] = {}
    tmax = int(f_class.shape[0] - 1)
    for name, lo, hi in windows:
        lo_i = max(1, int(lo))
        hi_i = min(tmax, int(hi))
        mass = np.sum(f_class[lo_i : hi_i + 1, :], axis=0) if hi_i >= lo_i else np.zeros(4, dtype=np.float64)
        tot = float(np.sum(mass))
        if tot <= 0.0:
            out[name] = {c: 0.0 for c in cats}
        else:
            out[name] = {c: float(mass[i] / tot) for i, c in enumerate(cats)}
    return out


def classify_membrane_recross(
    *,
    n_samples: int,
    max_steps: int,
    start_idx: int,
    target_idx: int,
    dst_rows: List[np.ndarray],
    cdf_rows: List[np.ndarray],
    q_values: np.ndarray,
    q_star: float,
    membrane_idx_edges: set[Tuple[int, int]],
    windows: Sequence[Tuple[str, int, int]],
    rng: np.random.Generator,
) -> Dict[str, Dict[str, float]]:
    cats = ["L0R0", "L0R1", "L1R0", "L1R1"]
    counts: Dict[str, Dict[str, int]] = {
        w[0]: {c: 0 for c in cats} for w in windows
    }
    totals: Dict[str, int] = {w[0]: 0 for w in windows}

    for _ in range(int(n_samples)):
        s = int(start_idx)
        t_hit: int | None = None
        leak = False
        entered = bool(q_values[s] >= q_star)
        recross = False
        for t in range(1, int(max_steps) + 1):
            nxt = sample_next_state(s, dst_rows, cdf_rows, rng)
            if nxt != s and _edge_idx_key(s, nxt) in membrane_idx_edges:
                leak = True
            s = nxt
            if q_values[s] >= q_star:
                entered = True
            elif entered:
                recross = True
            if s == target_idx:
                t_hit = t
                break

        if t_hit is None:
            continue
        cat = "L1R1" if leak and recross else "L1R0" if leak else "L0R1" if recross else "L0R0"
        for name, lo, hi in windows:
            if int(lo) <= int(t_hit) <= int(hi):
                counts[name][cat] += 1
                totals[name] += 1

    out: Dict[str, Dict[str, float]] = {}
    for name, _, _ in windows:
        total = max(1, int(totals[name]))
        out[name] = {cat: float(counts[name][cat]) / float(total) for cat in cats}
    return out


def build_membrane_case(
    *,
    Lx: int,
    Wy: int,
    bx: float,
    corridor_halfwidth: int,
    wall_margin: int,
    delta_core: float,
    delta_open: float,
    start_x: int,
    target_x: int,
    kappa_top: float,
    kappa_bottom: float,
) -> dict:
    start, target, local_bias_map, barrier_map, channel_mask, wall_span = build_ot_case_geometry(
        Lx=Lx,
        Wy=Wy,
        corridor_halfwidth=corridor_halfwidth,
        wall_margin=wall_margin,
        delta_core=delta_core,
        delta_open=delta_open,
        start_x=start_x,
        target_x=target_x,
    )
    y_mid, y_low, y_high, _, _ = wall_span

    membrane_edges: set[Edge] = set()
    for edge in list(barrier_map.keys()):
        (x0, y0), (x1, y1) = edge
        if x0 == x1 and abs(y1 - y0) == 1:
            lowy = min(y0, y1)
            highy = max(y0, y1)
            if lowy == y_low - 1 and highy == y_low:
                barrier_map[edge] = float(kappa_bottom)
                membrane_edges.add(edge)
            elif lowy == y_high and highy == y_high + 1:
                barrier_map[edge] = float(kappa_top)
                membrane_edges.add(edge)

    src_idx, dst_idx, probs = build_transition_arrays_general_rect(
        Lx=Lx,
        Wy=Wy,
        q=0.8,
        local_bias_map=local_bias_map,
        sticky_map={},
        barrier_map=barrier_map,
        long_range_map={},
        global_bias=(float(bx), 0.0),
    )

    f, f_corr, f_outer, surv = run_exact_one_target_rect(
        Lx=Lx,
        Wy=Wy,
        start=start,
        target=target,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        t_max=5000,
        surv_tol=1e-12,
        channel_mask=channel_mask,
    )

    spec = type("Spec", (), {
        "Wy": Wy,
        "bx": bx,
        "corridor_halfwidth": corridor_halfwidth,
        "wall_margin": wall_margin,
        "delta_core": delta_core,
        "delta_open": delta_open,
    })()
    res = summarize_one_target(spec, f, surv)
    res.phase = classify_phase_one_target(res)

    return {
        "start": start,
        "target": target,
        "wall_span": wall_span,
        "y_mid": y_mid,
        "channel_mask": channel_mask,
        "barrier_map": barrier_map,
        "membrane_edges": membrane_edges,
        "src_idx": src_idx,
        "dst_idx": dst_idx,
        "probs": probs,
        "f_total": f,
        "f_corr": f_corr,
        "f_outer": f_outer,
        "surv": surv,
        "res": res,
        "kappa_top": float(kappa_top),
        "kappa_bottom": float(kappa_bottom),
        "corridor_halfwidth": int(corridor_halfwidth),
        "wall_margin": int(wall_margin),
        "Wy": int(Wy),
        "bx": float(bx),
    }


def build_two_target_case(
    *,
    Lx: int,
    Wy: int,
    start_x: int,
    far_target_x: int,
    near_dx: int,
    near_dy: int,
    bx: float,
) -> dict:
    y_mid = int((Wy - 1) // 2)
    start = (int(start_x), y_mid)
    near = (min(Lx - 2, int(start_x + near_dx)), max(0, min(Wy - 1, y_mid + int(near_dy))))
    far = (int(far_target_x), y_mid)

    src_idx, dst_idx, probs = build_transition_arrays_general_rect(
        Lx=Lx,
        Wy=Wy,
        q=0.8,
        local_bias_map={},
        sticky_map={},
        barrier_map={},
        long_range_map={},
        global_bias=(float(bx), 0.0),
    )

    f_any, f_near, f_far, surv = run_exact_two_target_rect(
        Lx=Lx,
        Wy=Wy,
        start=start,
        target1=near,
        target2=far,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        t_max=5000,
        surv_tol=1e-12,
    )

    spec = type("Spec", (), {
        "Wy": Wy,
        "x_start": start_x,
        "w_fast": 0,
        "w_slow": 0,
        "fast_skip": 0,
        "slow_skip": 0,
        "delta_fast": 0.0,
        "delta_slow": 0.0,
    })()
    res = summarize_two_target(spec, f_any, f_near, f_far, surv)
    res.phase = classify_phase_two_target(res)

    return {
        "start": start,
        "near": near,
        "far": far,
        "src_idx": src_idx,
        "dst_idx": dst_idx,
        "probs": probs,
        "f_any": f_any,
        "f_near": f_near,
        "f_far": f_far,
        "surv": surv,
        "res": res,
        "bx": float(bx),
        "near_dx": int(near_dx),
        "near_dy": int(near_dy),
        "Wy": int(Wy),
    }


def intervals_to_tex(intervals: Sequence[int]) -> str:
    if not intervals:
        return "-"
    vals = sorted(int(v) for v in intervals)
    out: List[str] = []
    s = vals[0]
    p = vals[0]
    for v in vals[1:]:
        if v == p + 1:
            p = v
            continue
        out.append(f"{s}" if s == p else f"{s}-{p}")
        s = p = v
    out.append(f"{s}" if s == p else f"{s}-{p}")
    return ",".join(out)


def fmt_scan_float(x: float) -> str:
    v = float(x)
    if abs(v) < 1e-12:
        return "0"
    if abs(v) < 0.01:
        return f"{v:.4f}".rstrip("0").rstrip(".")
    if abs(v) < 0.1:
        return f"{v:.3f}".rstrip("0").rstrip(".")
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _row_exists(rows: Sequence[dict], ref: dict, keys: Sequence[str], tol: float = 1e-12) -> bool:
    for row in rows:
        ok = True
        for key in keys:
            a = row[key]
            b = ref[key]
            if isinstance(a, (int, float)) or isinstance(b, (int, float)):
                if abs(float(a) - float(b)) > tol:
                    ok = False
                    break
            else:
                if a != b:
                    ok = False
                    break
        if ok:
            return True
    return False


def two_target_clear_score(row: dict) -> float:
    """Emphasize visibly clean double-peaks while keeping both branches non-negligible."""
    if int(row.get("phase", 0)) < 2:
        return -1.0
    sep = float(row.get("sep_mode_width", 0.0))
    valley = row.get("valley_over_max")
    valley_term = 1.0 - float(valley) if valley is not None else 0.0
    valley_term = max(0.0, min(1.0, valley_term))
    balance = min(float(row.get("p_near", 0.0)), float(row.get("p_far", 0.0)))
    return sep * valley_term * (0.30 + max(0.0, balance))


def two_target_phase2_margins(row: dict) -> dict:
    """Margins to phase=2 thresholds used for quality control and reporting."""
    sep = float(row.get("sep_mode_width", 0.0))
    valley_raw = row.get("valley_over_max")
    valley = None if valley_raw is None else float(valley_raw)
    p_min = min(float(row.get("p_near", 0.0)), float(row.get("p_far", 0.0)))
    peak_ratio_raw = row.get("peak_ratio")
    peak_ratio = None if peak_ratio_raw is None else float(peak_ratio_raw)
    contrast = None if (peak_ratio is None or valley is None) else float(peak_ratio - valley)

    sep_margin = float(sep - 1.0)
    mass_margin = float(p_min - 0.15)
    valley_margin = None if valley is None else float(0.35 - valley)
    peak_margin = None if peak_ratio is None else float(peak_ratio - 0.10)
    contrast_margin = None if contrast is None else float(contrast - 0.01)

    finite_margins = [sep_margin, mass_margin]
    for v in (valley_margin, peak_margin, contrast_margin):
        if v is not None:
            finite_margins.append(float(v))
    min_margin = float(min(finite_margins)) if finite_margins else float("-inf")

    return {
        "sep_margin": sep_margin,
        "mass_margin": mass_margin,
        "valley_margin": valley_margin,
        "peak_margin": peak_margin,
        "contrast_margin": contrast_margin,
        "min_margin": min_margin,
        "p_min": p_min,
        "peak_ratio": peak_ratio,
        "contrast": contrast,
    }


def evaluate_two_target_gate(
    row: dict,
    *,
    peak_margin_min: float,
    min_margin_min: float,
    valley_max: float | None = None,
) -> dict:
    """Evaluate clear-double gate pass/fail and report per-threshold slacks."""
    m = two_target_phase2_margins(row)
    peak_margin = m.get("peak_margin")
    valley_raw = row.get("valley_over_max")
    valley = None if valley_raw is None else float(valley_raw)

    peak_slack = None if peak_margin is None else float(float(peak_margin) - float(peak_margin_min))
    min_slack = float(float(m["min_margin"]) - float(min_margin_min))

    if valley_max is None:
        valley_slack = None
        valley_ok = True
    elif valley is None:
        valley_slack = None
        valley_ok = False
    else:
        valley_slack = float(float(valley_max) - float(valley))
        valley_ok = valley_slack >= 0.0

    peak_ok = peak_slack is not None and float(peak_slack) >= 0.0
    min_ok = float(min_slack) >= 0.0
    passes = bool(peak_ok and min_ok and valley_ok)

    finite_threshold_slacks = [float(min_slack)]
    if peak_slack is not None:
        finite_threshold_slacks.append(float(peak_slack))
    if valley_slack is not None:
        finite_threshold_slacks.append(float(valley_slack))

    finite_gate_slacks = [float(m["min_margin"])]
    if peak_margin is not None:
        finite_gate_slacks.append(float(peak_margin))
    if valley_slack is not None:
        finite_gate_slacks.append(float(valley_slack))

    return {
        "passes": passes,
        "peak_margin_min": float(peak_margin_min),
        "min_margin_min": float(min_margin_min),
        "valley_max": None if valley_max is None else float(valley_max),
        "peak_margin": None if peak_margin is None else float(peak_margin),
        "min_margin": float(m["min_margin"]),
        "valley_over_max": valley,
        "peak_slack": peak_slack,
        "min_slack": float(min_slack),
        "valley_slack": valley_slack,
        # Gate slack used in report tables: absolute quality margin under the gate.
        "min_slack_all": float(min(finite_gate_slacks)),
        # Extra diagnostic: strict slack above gate thresholds.
        "threshold_slack_min": float(min(finite_threshold_slacks)),
    }


def two_target_showcase_score(row: dict) -> float:
    """Score dedicated to selecting a visually clear no-corridor instance figure."""
    if int(row.get("phase", 0)) < 2:
        return -1.0
    base = float(two_target_clear_score(row))
    m = two_target_phase2_margins(row)
    bonus = 0.20 * max(0.0, float(m["sep_margin"])) + 0.16 * max(0.0, float(m["mass_margin"]))
    if m["valley_margin"] is not None:
        bonus += 0.18 * max(0.0, float(m["valley_margin"]))
    if m["contrast_margin"] is not None:
        bonus += 0.10 * max(0.0, float(m["contrast_margin"]))
    return base + bonus


def enrich_two_target_quality(row: dict) -> dict:
    """Attach clear/showcase scores and phase=2 margins for downstream QC/reporting."""
    out = dict(row)
    m = two_target_phase2_margins(out)
    out["clear_score"] = float(two_target_clear_score(out))
    out["showcase_score"] = float(two_target_showcase_score(out))
    out["sep_margin"] = float(m["sep_margin"])
    out["mass_margin"] = float(m["mass_margin"])
    out["valley_margin"] = None if m["valley_margin"] is None else float(m["valley_margin"])
    out["peak_margin"] = None if m["peak_margin"] is None else float(m["peak_margin"])
    out["contrast_margin"] = None if m["contrast_margin"] is None else float(m["contrast_margin"])
    out["min_margin"] = float(m["min_margin"])
    return out


def select_two_target_representative(rows: Sequence[dict]) -> dict:
    clear_rows = [r for r in rows if int(r["phase"]) >= 2]
    if not clear_rows:
        return max(
            rows,
            key=lambda r: (
                int(r["phase"]),
                float(r["sep_mode_width"]),
                min(float(r["p_near"]), float(r["p_far"])),
            ),
        )

    for r in clear_rows:
        r["clear_score"] = float(two_target_clear_score(r))

    balanced_rows = [r for r in clear_rows if min(float(r["p_near"]), float(r["p_far"])) >= 0.25]
    pool = balanced_rows if balanced_rows else clear_rows
    return max(
        pool,
        key=lambda r: (
            float(r.get("clear_score", 0.0)),
            float(r["sep_mode_width"]),
            -abs(float(r["bx"]) - 0.07),
            -abs(int(r["near_dx"]) - 2),
            min(float(r["p_near"]), float(r["p_far"])),
        ),
    )


def select_two_target_clear_instance(rows: Sequence[dict]) -> dict | None:
    clear_rows = [r for r in rows if int(r.get("phase", 0)) >= 2]
    if not clear_rows:
        return None

    # Prefer rows that are not merely phase=2 by threshold crossing, but retain
    # visible second-peak margin. Relax gates only when needed.
    gate_specs = [
        {"name": "peak>=0.07,min>=0.07,valley<=0.10", "peak_margin_min": 0.07, "min_margin_min": 0.07, "valley_max": 0.10},
        {"name": "peak>=0.05,min>=0.05,valley<=0.12", "peak_margin_min": 0.05, "min_margin_min": 0.05, "valley_max": 0.12},
        {"name": "peak>=0.05,min>=0.05,valley<=0.18", "peak_margin_min": 0.05, "min_margin_min": 0.05, "valley_max": 0.18},
        {"name": "peak>=0.05,min>=0.05", "peak_margin_min": 0.05, "min_margin_min": 0.05, "valley_max": None},
        {"name": "peak>=0.03,min>=0.03", "peak_margin_min": 0.03, "min_margin_min": 0.03, "valley_max": None},
        {"name": "peak>=0.02,min>=0.02", "peak_margin_min": 0.02, "min_margin_min": 0.02, "valley_max": None},
    ]
    selected_pool = clear_rows
    selected_gate = {
        "name": "phase2-only",
        "peak_margin_min": 0.0,
        "min_margin_min": 0.0,
        "valley_max": None,
        "candidate_count": int(len(clear_rows)),
    }
    for gate in gate_specs:
        cand: List[dict] = []
        for row in clear_rows:
            m = two_target_phase2_margins(row)
            peak_margin = m.get("peak_margin")
            if peak_margin is None:
                continue
            valley_raw = row.get("valley_over_max")
            valley_max = gate.get("valley_max")
            if valley_max is not None:
                if valley_raw is None or float(valley_raw) > float(valley_max):
                    continue
            if float(peak_margin) >= float(gate["peak_margin_min"]) and float(m["min_margin"]) >= float(gate["min_margin_min"]):
                cand.append(row)
        if cand:
            selected_pool = cand
            selected_gate = {
                "name": str(gate["name"]),
                "peak_margin_min": float(gate["peak_margin_min"]),
                "min_margin_min": float(gate["min_margin_min"]),
                "valley_max": None if gate.get("valley_max") is None else float(gate["valley_max"]),
                "candidate_count": int(len(cand)),
            }
            break

    def rank_key(row: dict) -> Tuple[float, float, float, float, float, float, float, float]:
        m = two_target_phase2_margins(row)
        peak_margin = float(m["peak_margin"]) if m["peak_margin"] is not None else -1.0
        valley_raw = row.get("valley_over_max")
        valley_rank = -float(valley_raw) if valley_raw is not None else -1.0
        return (
            float(two_target_showcase_score(row)),
            float(m["min_margin"]),
            peak_margin,
            float(row.get("sep_mode_width", 0.0)),
            valley_rank,
            min(float(row.get("p_near", 0.0)), float(row.get("p_far", 0.0))),
            -abs(float(row.get("bx", 0.0)) - 0.07),
            -abs(int(row.get("near_dx", 0)) - 2),
        )

    best = max(selected_pool, key=rank_key)
    out = enrich_two_target_quality(best)
    out["_selection_gate"] = selected_gate
    return out


def write_table_symmetric(path: Path, rows: Sequence[dict], wy_focus: int) -> List[dict]:
    focus = [r for r in rows if int(r["Wy"]) == int(wy_focus)]
    focus = sorted(focus, key=lambda r: float(r["kappa"]))
    lines = [
        r"\begin{tabular}{@{}cccccc@{}}",
        r"\toprule",
        r"$\kappa$ & phase & $t_{p1}$ & $t_{p2}$ & valley/max & sep-score \\",
        r"\midrule",
    ]
    for r in focus:
        tp1 = "-" if r["t_peak1"] is None else str(int(r["t_peak1"]))
        tp2 = "-" if r["t_peak2"] is None else str(int(r["t_peak2"]))
        vm = "-" if r["valley_over_max"] is None else f"{float(r['valley_over_max']):.3f}"
        lines.append(
            f"{fmt_scan_float(float(r['kappa']))} & {int(r['phase'])} & {tp1} & {tp2} & {vm} & {float(r['sep_peaks']):.2f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    ensure_dir(path.parent)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return focus


def write_table_asymmetric(path: Path, rows: Sequence[dict], *, representative: dict | None = None, top_n: int = 10) -> List[dict]:
    # Keep this table genuinely asymmetric so caption and table content stay aligned.
    rows_pool = [r for r in rows if abs(float(r["kappa_top"]) - float(r["kappa_bottom"])) > 1e-12]
    if not rows_pool:
        rows_pool = list(rows)

    rows_s = sorted(
        rows_pool,
        key=lambda r: (
            -int(r["phase"]),
            -float(r["sep_peaks"]),
            -abs(float(r["kappa_top"]) - float(r["kappa_bottom"])),
            float(r["kappa_top"]) + float(r["kappa_bottom"]),
        ),
    )
    rows_s = rows_s[: max(1, int(top_n))]

    if representative is not None and not _row_exists(rows_s, representative, keys=["kappa_top", "kappa_bottom"]):
        rep_match = None
        for r in rows_pool:
            if _row_exists([r], representative, keys=["kappa_top", "kappa_bottom"]):
                rep_match = r
                break
        if rep_match is not None:
            rows_s[-1] = rep_match

    lines = [
        r"\begin{tabular}{@{}cccccc@{}}",
        r"\toprule",
        r"$\kappa_{\uparrow}$ & $\kappa_{\downarrow}$ & phase & $t_{p1}$ & $t_{p2}$ & sep-score \\",
        r"\midrule",
    ]
    for r in rows_s:
        tp1 = "-" if r["t_peak1"] is None else str(int(r["t_peak1"]))
        tp2 = "-" if r["t_peak2"] is None else str(int(r["t_peak2"]))
        lines.append(
            f"{fmt_scan_float(float(r['kappa_top']))} & {fmt_scan_float(float(r['kappa_bottom']))} & {int(r['phase'])} & {tp1} & {tp2} & {float(r['sep_peaks']):.2f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    ensure_dir(path.parent)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows_s


def write_table_two_target(path: Path, rows: Sequence[dict], bx_vals: Sequence[float]) -> List[dict]:
    lines = [
        r"\begin{tabular}{@{}cccccc@{}}",
        r"\toprule",
        r"$b_x$ & clear $d$ interval & best $d$ & phase(best) & $P(\mathrm{near})$ & $P(\mathrm{far})$ \\",
        r"\midrule",
    ]
    best_rows: List[dict] = []
    for bx in bx_vals:
        group = [r for r in rows if abs(float(r["bx"]) - float(bx)) < 1e-12]
        clear_d = [int(r["near_dx"]) for r in group if int(r["phase"]) >= 2]
        best = max(
            group,
            key=lambda r: (
                int(r["phase"]),
                float(two_target_clear_score(r)),
                float(r["sep_mode_width"]),
                min(float(r["p_near"]), float(r["p_far"])),
            ),
        )
        best_rows.append(best)
        lines.append(
            f"{float(bx):+.2f} & {intervals_to_tex(clear_d)} & {int(best['near_dx'])} & {int(best['phase'])} & {float(best['p_near']):.3f} & {float(best['p_far']):.3f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    ensure_dir(path.parent)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return best_rows


def write_table_two_target_representative(path: Path, row: dict) -> None:
    tp1 = "-" if row["t_peak1"] is None else str(int(row["t_peak1"]))
    tv = "-" if row["t_valley"] is None else str(int(row["t_valley"]))
    tp2 = "-" if row["t_peak2"] is None else str(int(row["t_peak2"]))
    lines = [
        r"\begin{tabular}{@{}cccccccccc@{}}",
        r"\toprule",
        r"$b_x$ & $d$ & phase & $t_{p1}$ & $t_v$ & $t_{p2}$ & $P(\mathrm{near})$ & $P(\mathrm{far})$ & sep-score & clear-score \\",
        r"\midrule",
        (
            f"{float(row['bx']):+.2f} & {int(row['near_dx'])} & {int(row['phase'])} & "
            f"{tp1} & {tv} & {tp2} & {float(row['p_near']):.3f} & {float(row['p_far']):.3f} & "
            f"{float(row['sep_mode_width']):.2f} & {float(two_target_clear_score(row)):.2f} \\\\"
        ),
        r"\bottomrule",
        r"\end{tabular}",
    ]
    ensure_dir(path.parent)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt_sci_tex(v: float | None) -> str:
    if v is None:
        return "-"
    x = float(v)
    if not math.isfinite(x):
        return "-"
    if abs(x) < 1e-300:
        return "0"
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / (10.0**exp)
    return f"{mant:.2f}\\times 10^{{{exp}}}"


def write_table_two_target_clear_instance(
    path: Path,
    row: dict,
    *,
    split_gap: float | None = None,
    primary_gate_audit: dict | None = None,
) -> None:
    m = two_target_phase2_margins(row)
    valley_txt = "-" if row.get("valley_over_max") is None else f"{float(row['valley_over_max']):.3f}"
    peak_ratio_txt = "-" if m["peak_ratio"] is None else f"{float(m['peak_ratio']):.3f}"
    peak_margin_txt = "-" if m["peak_margin"] is None else f"{float(m['peak_margin']):.3f}"
    split_gap_txt = _fmt_sci_tex(split_gap)
    show_score = float(two_target_showcase_score(row))
    spec_txt = str(row.get("spec", "-")).replace("_", r"\_")
    gate_pass = "-"
    gate_slack_txt = "-"
    if primary_gate_audit is not None:
        gate_pass = "yes" if bool(primary_gate_audit.get("passes", False)) else "no"
        gate_slack = primary_gate_audit.get("min_slack_all")
        if gate_slack is not None and math.isfinite(float(gate_slack)):
            gate_slack_txt = f"{float(gate_slack):.3f}"
    lines = [
        r"\begin{tabular}{@{}cccccccccccccccc@{}}",
        r"\toprule",
        r"spec & $b_x$ & $d$ & $\Delta y$ & phase & sep-score & valley/max & $p_{\min}$ & peak-ratio & peak-margin & min-margin & gate-pass & gate-slack & clear-score & showcase & $\varepsilon_{\mathrm{split}}$ \\",
        r"\midrule",
        (
            f"{spec_txt}"
            f" & {float(row['bx']):+.2f}"
            f" & {int(row['near_dx'])}"
            f" & {int(row['near_dy'])}"
            f" & {int(row['phase'])}"
            f" & {float(row['sep_mode_width']):.2f}"
            f" & {valley_txt}"
            f" & {float(m['p_min']):.3f}"
            f" & {peak_ratio_txt}"
            f" & {peak_margin_txt}"
            f" & {float(m['min_margin']):.3f}"
            f" & {gate_pass}"
            f" & {gate_slack_txt}"
            f" & {float(two_target_clear_score(row)):.2f}"
            f" & {show_score:.2f}"
            f" & ${split_gap_txt}$ \\\\"
        ),
        r"\bottomrule",
        r"\end{tabular}",
    ]
    ensure_dir(path.parent)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_table_two_target_splitting_qc(path: Path, *, rep: dict, clear: dict) -> None:
    def _fmt_fixed(v: float | None, ndigits: int = 6) -> str:
        if v is None:
            return "-"
        x = float(v)
        if not math.isfinite(x):
            return "-"
        return f"{x:.{ndigits}f}"

    def _fmt_sci_cell(v: float | None) -> str:
        txt = _fmt_sci_tex(v)
        return "-" if txt == "-" else f"${txt}$"

    rows = [("representative", rep), ("clear-instance", clear)]
    lines = [
        r"\begin{tabular}{@{}lcccccc@{}}",
        r"\toprule",
        r"case & $q_{\mathrm{far}}(x_s)$ & $P_{\mathrm{far}}$ & $\varepsilon_{\mathrm{split}}$ & $\|r_{\mathrm{int}}\|_\infty$ & $\|r_{\mathrm{near}}\|_\infty$ & $\|r_{\mathrm{far}}\|_\infty$ \\",
        r"\midrule",
    ]
    for name, payload in rows:
        lines.append(
            f"{name}"
            f" & {_fmt_fixed(payload.get('q_far_start'), ndigits=6)}"
            f" & {_fmt_fixed(payload.get('p_far_mass'), ndigits=6)}"
            f" & {_fmt_sci_cell(payload.get('consistency_gap_vs_f_far_mass'))}"
            f" & {_fmt_sci_cell(payload.get('interior_residual_inf'))}"
            f" & {_fmt_sci_cell(payload.get('boundary_near_residual_inf'))}"
            f" & {_fmt_sci_cell(payload.get('boundary_far_residual_inf'))} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    ensure_dir(path.parent)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compute_two_target_splitting_committor(case: dict, *, Lx: int) -> dict:
    n_states = int(int(Lx) * int(case["Wy"]))
    start = case["start"]
    near = case["near"]
    far = case["far"]

    start_i = idx(start[0], start[1], int(Lx))
    near_i = idx(near[0], near[1], int(Lx))
    far_i = idx(far[0], far[1], int(Lx))

    set_near = np.zeros(n_states, dtype=bool)
    set_far = np.zeros(n_states, dtype=bool)
    set_near[near_i] = True
    set_far[far_i] = True

    q_far = solve_committor(
        n_states=n_states,
        src_idx=case["src_idx"],
        dst_idx=case["dst_idx"],
        probs=case["probs"],
        set_A=set_near,
        set_B=set_far,
    )
    q_stats = committor_residual_stats(
        n_states=n_states,
        src_idx=case["src_idx"],
        dst_idx=case["dst_idx"],
        probs=case["probs"],
        q_values=q_far,
        set_A=set_near,
        set_B=set_far,
    )
    q_far_start = float(q_far[start_i])
    p_far = float(np.sum(case["f_far"]))
    p_near = float(np.sum(case["f_near"]))

    return {
        "q_far_start": q_far_start,
        "q_far_min": float(np.min(q_far)),
        "q_far_max": float(np.max(q_far)),
        "p_far_mass": p_far,
        "p_near_mass": p_near,
        "consistency_gap_vs_f_far_mass": float(abs(q_far_start - p_far)),
        "interior_residual_inf": float(q_stats["interior_residual_inf"]),
        "boundary_near_residual_inf": float(q_stats["boundary_A_residual_inf"]),
        "boundary_far_residual_inf": float(q_stats["boundary_B_residual_inf"]),
    }


@dataclass(frozen=True)
class TwoTargetGridSpec:
    name: str
    near_dy: int
    near_dx_vals: Tuple[int, ...]
    bx_vals: Tuple[float, ...]


def run_with_retry(builder: Any, kwargs: dict, *, retries: int = 2) -> dict:
    last_err: Exception | None = None
    for _ in range(max(1, int(retries))):
        try:
            return builder(**kwargs)
        except Exception as exc:  # pragma: no cover - runtime guard for long scans
            last_err = exc
    if last_err is None:
        raise RuntimeError("run_with_retry exhausted retries without an exception state.")
    raise last_err


def _two_target_scan_row(
    *,
    case: dict,
    Wy_two_target: int,
    bx: float,
    near_dx: int,
    near_dy: int,
) -> dict:
    res = case["res"]
    p_near = float(np.sum(case["f_near"]))
    p_far = float(np.sum(case["f_far"]))
    peak_ratio = None if res.peak_ratio is None else float(res.peak_ratio)
    valley_over_max = None if res.valley_over_max is None else float(res.valley_over_max)
    row = {
        "Wy": int(Wy_two_target),
        "bx": float(bx),
        "near_dx": int(near_dx),
        "near_dy": int(near_dy),
        "phase": int(res.phase),
        "t_peak1": None if res.t_peak1 is None else int(res.t_peak1),
        "t_peak2": None if res.t_peak2 is None else int(res.t_peak2),
        "t_valley": None if res.t_valley is None else int(res.t_valley),
        "valley_over_max": valley_over_max,
        "peak_ratio": peak_ratio,
        "peak_minus_valley": None if (peak_ratio is None or valley_over_max is None) else float(peak_ratio - valley_over_max),
        "p_near": p_near,
        "p_far": p_far,
        "sep_mode_width": float(res.sep_mode_width),
        "t_mode_near": int(res.t_mode_m1),
        "t_mode_far": int(res.t_mode_m2),
    }
    row["clear_score"] = float(two_target_clear_score(row))
    return row


def scan_two_target_grid(
    *,
    spec: TwoTargetGridSpec,
    Lx: int,
    Wy_two_target: int,
    start_x: int,
    far_target_x: int,
    retries: int = 2,
) -> dict:
    tt_rows: List[dict] = []
    tt_phase = np.zeros((len(spec.bx_vals), len(spec.near_dx_vals)), dtype=float)
    tt_sep = np.zeros_like(tt_phase)
    for i, bx in enumerate(spec.bx_vals):
        for j, nd in enumerate(spec.near_dx_vals):
            case = run_with_retry(
                build_two_target_case,
                kwargs={
                    "Lx": Lx,
                    "Wy": Wy_two_target,
                    "start_x": start_x,
                    "far_target_x": far_target_x,
                    "near_dx": int(nd),
                    "near_dy": int(spec.near_dy),
                    "bx": float(bx),
                },
                retries=retries,
            )
            row = _two_target_scan_row(
                case=case,
                Wy_two_target=Wy_two_target,
                bx=float(bx),
                near_dx=int(nd),
                near_dy=int(spec.near_dy),
            )
            tt_rows.append(row)
            tt_phase[i, j] = int(row["phase"])
            tt_sep[i, j] = float(row["sep_mode_width"])

    clear_count = int(sum(int(r["phase"]) >= 2 for r in tt_rows))
    scan_size = int(len(tt_rows))
    clear_ratio = float(clear_count) / float(max(1, scan_size))
    return {
        "spec": spec,
        "rows": tt_rows,
        "phase_map": tt_phase,
        "sep_map": tt_sep,
        "clear_count": clear_count,
        "scan_size": scan_size,
        "clear_ratio": clear_ratio,
    }


def build_two_target_refinement_points(
    rows: Sequence[dict],
    *,
    top_k: int = 8,
    bx_step: float = 0.005,
    bx_radius_steps: int = 2,
    bx_bounds: Tuple[float, float] = (0.0, 0.20),
    near_dx_bounds: Tuple[int, int] = (2, 12),
    near_dy_bounds: Tuple[int, int] = (0, 6),
) -> List[Tuple[float, int, int]]:
    if not rows:
        return []

    clear_rows = [r for r in rows if int(r.get("phase", 0)) >= 2]
    pool = clear_rows if clear_rows else list(rows)
    ranked = sorted(
        pool,
        key=lambda r: (
            float(two_target_showcase_score(r)),
            float(two_target_phase2_margins(r)["min_margin"]) if int(r.get("phase", 0)) >= 2 else float("-inf"),
            float(two_target_clear_score(r)),
            float(r.get("sep_mode_width", 0.0)),
            min(float(r.get("p_near", 0.0)), float(r.get("p_far", 0.0))),
        ),
        reverse=True,
    )

    seen_seed: set[Tuple[int, int, int]] = set()
    seeds: List[dict] = []
    for row in ranked:
        key = (
            int(round(float(row.get("bx", 0.0)) * 1000)),
            int(row.get("near_dx", 0)),
            int(row.get("near_dy", 0)),
        )
        if key in seen_seed:
            continue
        seen_seed.add(key)
        seeds.append(row)
        if len(seeds) >= max(1, int(top_k)):
            break

    pts: set[Tuple[float, int, int]] = set()
    bx_lo, bx_hi = float(bx_bounds[0]), float(bx_bounds[1])
    dx_lo, dx_hi = int(near_dx_bounds[0]), int(near_dx_bounds[1])
    dy_lo, dy_hi = int(near_dy_bounds[0]), int(near_dy_bounds[1])
    for seed in seeds:
        bx0 = float(seed.get("bx", 0.0))
        dx0 = int(seed.get("near_dx", 0))
        dy0 = int(seed.get("near_dy", 0))
        for dy in range(dy0 - 1, dy0 + 2):
            if dy < dy_lo or dy > dy_hi:
                continue
            for dx in range(dx0 - 1, dx0 + 2):
                if dx < dx_lo or dx > dx_hi:
                    continue
                for k in range(-int(bx_radius_steps), int(bx_radius_steps) + 1):
                    bx = bx0 + float(k) * float(bx_step)
                    if bx < bx_lo - 1e-12 or bx > bx_hi + 1e-12:
                        continue
                    pts.add((float(round(bx, 6)), int(dx), int(dy)))
    return sorted(pts, key=lambda v: (v[2], v[0], v[1]))


def scan_two_target_points(
    *,
    points: Sequence[Tuple[float, int, int]],
    Lx: int,
    Wy_two_target: int,
    start_x: int,
    far_target_x: int,
    retries: int = 2,
) -> dict:
    tt_rows: List[dict] = []
    for bx, near_dx, near_dy in points:
        case = run_with_retry(
            build_two_target_case,
            kwargs={
                "Lx": Lx,
                "Wy": Wy_two_target,
                "start_x": start_x,
                "far_target_x": far_target_x,
                "near_dx": int(near_dx),
                "near_dy": int(near_dy),
                "bx": float(bx),
            },
            retries=retries,
        )
        row = _two_target_scan_row(
            case=case,
            Wy_two_target=Wy_two_target,
            bx=float(bx),
            near_dx=int(near_dx),
            near_dy=int(near_dy),
        )
        tt_rows.append(row)

    clear_count = int(sum(int(r["phase"]) >= 2 for r in tt_rows))
    scan_size = int(len(tt_rows))
    clear_ratio = float(clear_count) / float(max(1, scan_size))
    return {
        "rows": tt_rows,
        "clear_count": clear_count,
        "scan_size": scan_size,
        "clear_ratio": clear_ratio,
    }


def main() -> int:
    report_dir = Path(__file__).resolve().parents[1]
    fig_dir = report_dir / "figures"
    data_dir = report_dir / "data"
    out_dir = report_dir / "outputs"
    table_dir = report_dir / "tables"
    for p in (fig_dir, data_dir, out_dir, table_dir):
        ensure_dir(p)

    # Shared baseline from existing rect_bimodality anchor.
    Lx = 60
    start_x = 7
    target_x = 58
    corridor_halfwidth = 2
    wall_margin = 5
    delta_core = 1.00
    delta_open = 0.55
    bx_base = -0.08

    # ----- Study A: one-target corridor with semi-permeable membranes -----
    wy_vals = [8, 10, 12, 14, 16, 20, 24]
    # Densify ultra-low leakage region while preserving weak/single transition columns.
    kappa_vals = [
        0.00,
        0.00025,
        0.0005,
        0.00075,
        0.0010,
        0.00125,
        0.0015,
        0.00175,
        0.0020,
        0.00225,
        0.0025,
        0.00275,
        0.0030,
        0.00325,
        0.0035,
        0.00375,
        0.0040,
        0.0045,
        0.0050,
        0.0060,
        0.0075,
        0.0100,
        0.0150,
        0.0200,
        0.0300,
        0.0500,
        0.1000,
        0.2000,
    ]

    sym_rows: List[dict] = []
    sym_phase = np.zeros((len(wy_vals), len(kappa_vals)), dtype=float)
    sym_sep = np.zeros_like(sym_phase)

    for i, Wy in enumerate(wy_vals):
        for j, kappa in enumerate(kappa_vals):
            case = build_membrane_case(
                Lx=Lx,
                Wy=Wy,
                bx=bx_base,
                corridor_halfwidth=corridor_halfwidth,
                wall_margin=wall_margin,
                delta_core=delta_core,
                delta_open=delta_open,
                start_x=start_x,
                target_x=target_x,
                kappa_top=kappa,
                kappa_bottom=kappa,
            )
            res = case["res"]
            row = {
                "Wy": Wy,
                "kappa": float(kappa),
                "phase": int(res.phase),
                "t_peak1": None if res.t_peak1 is None else int(res.t_peak1),
                "t_peak2": None if res.t_peak2 is None else int(res.t_peak2),
                "t_valley": None if res.t_valley is None else int(res.t_valley),
                "valley_over_max": None if res.valley_over_max is None else float(res.valley_over_max),
                "peak_balance": None if res.peak_balance is None else float(res.peak_balance),
                "sep_peaks": float(res.sep_peaks),
                "absorbed_mass": float(res.absorbed_mass),
                "survival_tail": float(res.survival_tail),
            }
            sym_rows.append(row)
            sym_phase[i, j] = int(res.phase)
            sym_sep[i, j] = float(res.sep_peaks)

    save_csv(
        data_dir / "corridor_membrane_symmetric_scan.csv",
        sym_rows,
        fieldnames=[
            "Wy",
            "kappa",
            "phase",
            "t_peak1",
            "t_peak2",
            "t_valley",
            "valley_over_max",
            "peak_balance",
            "sep_peaks",
            "absorbed_mass",
            "survival_tail",
        ],
    )

    plot_heatmap(
        fig_dir / "membrane_symmetric_phase_map.pdf",
        sym_phase,
        x_labels=[fmt_scan_float(k) for k in kappa_vals],
        y_labels=[str(w) for w in wy_vals],
        title="Symmetric membrane phase map (phase: 0/1/2)",
        cmap="RdYlBu_r",
        cbar_label="phase",
        annotate_fmt="{:.0f}",
    )

    plot_heatmap(
        fig_dir / "membrane_symmetric_sep_map.pdf",
        sym_sep,
        x_labels=[fmt_scan_float(k) for k in kappa_vals],
        y_labels=[str(w) for w in wy_vals],
        title="Symmetric membrane separation map",
        cmap="viridis",
        cbar_label="sep-score",
        annotate_fmt="{:.2f}",
    )

    # Representative symmetric case: enforce semi-permeable membrane (kappa>0).
    sym_rows_rep = [r for r in sym_rows if int(r["Wy"]) == 16 and float(r["kappa"]) > 0.0]
    if not sym_rows_rep:
        sym_rows_rep = [r for r in sym_rows if float(r["kappa"]) > 0.0]
    if not sym_rows_rep:
        sym_rows_rep = list(sym_rows)
    rep_sym_row = max(
        sym_rows_rep,
        key=lambda r: (
            int(r["phase"]),
            -abs(float(r["kappa"]) - 0.002),
            float(r["sep_peaks"]),
        ),
    )

    rep_sym = build_membrane_case(
        Lx=Lx,
        Wy=int(rep_sym_row["Wy"]),
        bx=bx_base,
        corridor_halfwidth=corridor_halfwidth,
        wall_margin=wall_margin,
        delta_core=delta_core,
        delta_open=delta_open,
        start_x=start_x,
        target_x=target_x,
        kappa_top=float(rep_sym_row["kappa"]),
        kappa_bottom=float(rep_sym_row["kappa"]),
    )

    # Asymmetric scan (fixed Wy focus)
    asym_wy = 16
    # Focus asymmetry map on the transition window to maximize clear-double coverage.
    k_top_vals = [
        0.00,
        0.00025,
        0.0005,
        0.00075,
        0.0010,
        0.00125,
        0.0015,
        0.00175,
        0.0020,
        0.0025,
        0.0030,
        0.0035,
        0.0040,
        0.0045,
        0.0050,
    ]
    k_bottom_vals = list(k_top_vals)

    asym_rows: List[dict] = []
    asym_phase = np.zeros((len(k_bottom_vals), len(k_top_vals)), dtype=float)
    asym_sep = np.zeros_like(asym_phase)

    for i, k_bottom in enumerate(k_bottom_vals):
        for j, k_top in enumerate(k_top_vals):
            case = build_membrane_case(
                Lx=Lx,
                Wy=asym_wy,
                bx=bx_base,
                corridor_halfwidth=corridor_halfwidth,
                wall_margin=wall_margin,
                delta_core=delta_core,
                delta_open=delta_open,
                start_x=start_x,
                target_x=target_x,
                kappa_top=k_top,
                kappa_bottom=k_bottom,
            )
            res = case["res"]
            row = {
                "Wy": asym_wy,
                "kappa_top": float(k_top),
                "kappa_bottom": float(k_bottom),
                "phase": int(res.phase),
                "t_peak1": None if res.t_peak1 is None else int(res.t_peak1),
                "t_peak2": None if res.t_peak2 is None else int(res.t_peak2),
                "t_valley": None if res.t_valley is None else int(res.t_valley),
                "valley_over_max": None if res.valley_over_max is None else float(res.valley_over_max),
                "peak_balance": None if res.peak_balance is None else float(res.peak_balance),
                "sep_peaks": float(res.sep_peaks),
            }
            asym_rows.append(row)
            asym_phase[i, j] = int(res.phase)
            asym_sep[i, j] = float(res.sep_peaks)

    save_csv(
        data_dir / "corridor_membrane_asymmetric_scan.csv",
        asym_rows,
        fieldnames=[
            "Wy",
            "kappa_top",
            "kappa_bottom",
            "phase",
            "t_peak1",
            "t_peak2",
            "t_valley",
            "valley_over_max",
            "peak_balance",
            "sep_peaks",
        ],
    )

    plot_heatmap(
        fig_dir / "membrane_asymmetric_phase_map.pdf",
        asym_phase,
        x_labels=[fmt_scan_float(k) for k in k_top_vals],
        y_labels=[fmt_scan_float(k) for k in k_bottom_vals],
        title="Asymmetric membrane phase map (top vs bottom)",
        cmap="RdYlBu_r",
        cbar_label="phase",
        annotate_fmt="{:.0f}",
    )

    plot_heatmap(
        fig_dir / "membrane_asymmetric_sep_map.pdf",
        asym_sep,
        x_labels=[fmt_scan_float(k) for k in k_top_vals],
        y_labels=[fmt_scan_float(k) for k in k_bottom_vals],
        title="Asymmetric membrane separation map",
        cmap="viridis",
        cbar_label="sep-score",
        annotate_fmt="{:.2f}",
    )

    asym_rows_non_sym = [
        r for r in asym_rows if abs(float(r["kappa_top"]) - float(r["kappa_bottom"])) > 1e-12
    ]
    rep_asym_pref = [
        r for r in asym_rows_non_sym
        if abs(float(r["kappa_top"]) - 0.002) < 1e-12 and abs(float(r["kappa_bottom"]) - 0.0) < 1e-12
    ]
    if rep_asym_pref and int(rep_asym_pref[0]["phase"]) >= 2:
        rep_asym_row = rep_asym_pref[0]
    else:
        rep_asym_row = max(
            asym_rows_non_sym,
            key=lambda r: (
                int(r["phase"]),
                -abs(float(r["kappa_top"]) - 0.002) - abs(float(r["kappa_bottom"]) - 0.0),
                float(r["sep_peaks"]),
                abs(float(r["kappa_top"]) - float(r["kappa_bottom"])),
            ),
        )

    rep_asym = build_membrane_case(
        Lx=Lx,
        Wy=asym_wy,
        bx=bx_base,
        corridor_halfwidth=corridor_halfwidth,
        wall_margin=wall_margin,
        delta_core=delta_core,
        delta_open=delta_open,
        start_x=start_x,
        target_x=target_x,
        kappa_top=float(rep_asym_row["kappa_top"]),
        kappa_bottom=float(rep_asym_row["kappa_bottom"]),
    )

    plot_membrane_geometry(
        fig_dir / "membrane_rep_sym_geometry.pdf",
        Lx=Lx,
        case=rep_sym,
        title=f"Symmetric membrane representative geometry (k={rep_sym['kappa_top']:.3f})",
    )
    plot_membrane_geometry(
        fig_dir / "membrane_rep_asym_geometry.pdf",
        Lx=Lx,
        case=rep_asym,
        title=(
            "Asymmetric membrane representative geometry "
            f"(k_up={rep_asym['kappa_top']:.3f}, k_dn={rep_asym['kappa_bottom']:.3f})"
        ),
    )

    # Plot representative FPT overlays.
    t_sym = np.arange(len(rep_sym["f_total"]))
    plot_fpt_overlay(
        fig_dir / "membrane_rep_sym_fpt.pdf",
        t=t_sym,
        f_total=rep_sym["f_total"],
        f_a=rep_sym["f_corr"],
        f_b=rep_sym["f_outer"],
        label_a="corridor-source flux",
        label_b="outer-source flux",
        title=f"Symmetric membrane representative (Wy={rep_sym['Wy']}, k={rep_sym['kappa_top']:.2f})",
        peaks=(rep_sym["res"].t_peak1, rep_sym["res"].t_valley, rep_sym["res"].t_peak2),
    )

    t_asym = np.arange(len(rep_asym["f_total"]))
    plot_fpt_overlay(
        fig_dir / "membrane_rep_asym_fpt.pdf",
        t=t_asym,
        f_total=rep_asym["f_total"],
        f_a=rep_asym["f_corr"],
        f_b=rep_asym["f_outer"],
        label_a="corridor-source flux",
        label_b="outer-source flux",
        title=(
            "Asymmetric membrane representative "
            f"(Wy={rep_asym['Wy']}, k_up={rep_asym['kappa_top']:.2f}, k_dn={rep_asym['kappa_bottom']:.2f})"
        ),
        peaks=(rep_asym["res"].t_peak1, rep_asym["res"].t_valley, rep_asym["res"].t_peak2),
    )

    # 4-class window composition using exact augmented-state decomposition.
    q_star_values = (0.4, 0.5, 0.6)

    def _membrane_window_props_exact(
        case: dict,
        *,
        q_star: float,
    ) -> Tuple[List[str], np.ndarray, np.ndarray, dict]:
        start = case["start"]
        target = case["target"]
        Lx_loc = Lx
        Wy_loc = int(case["Wy"])
        y_mid = int(case["y_mid"])
        n_states = int(Lx_loc * Wy_loc)
        start_i = idx(start[0], start[1], Lx_loc)
        target_i = idx(target[0], target[1], Lx_loc)

        A = build_start_basin_mask(Lx=Lx_loc, Wy=Wy_loc, start_x=start_x, y_mid=y_mid)
        B = np.zeros(n_states, dtype=bool)
        B[target_i] = True

        q_values = solve_committor(
            n_states=n_states,
            src_idx=case["src_idx"],
            dst_idx=case["dst_idx"],
            probs=case["probs"],
            set_A=A,
            set_B=B,
        )
        q_stats = committor_residual_stats(
            n_states=n_states,
            src_idx=case["src_idx"],
            dst_idx=case["dst_idx"],
            probs=case["probs"],
            q_values=q_values,
            set_A=A,
            set_B=B,
        )

        membrane_idx_edges = {
            _edge_idx_key(idx(a[0], a[1], Lx_loc), idx(b[0], b[1], Lx_loc))
            for (a, b) in case["membrane_edges"]
        }

        t_max_lr = min(4000, len(case["f_total"]) - 1)
        f_class, _surv_lr = exact_lr_class_fpt(
            n_states=n_states,
            start_idx=start_i,
            src_idx=case["src_idx"],
            dst_idx=case["dst_idx"],
            probs=case["probs"],
            target_idx=target_i,
            set_A=A,
            q_values=q_values,
            q_star=float(q_star),
            membrane_idx_edges=membrane_idx_edges,
            t_max=t_max_lr,
        )

        windows = window_ranges(case["res"].t_peak1, case["res"].t_valley, case["res"].t_peak2, len(case["f_total"]))
        window_props = window_fractions_from_fclass(f_class=f_class, windows=windows)

        cats = ["L0R0", "L0R1", "L1R0", "L1R1"]
        win_names = [w[0] for w in windows]
        arr = np.zeros((len(win_names), len(cats)), dtype=float)
        for i_w, wn in enumerate(win_names):
            for i_c, c in enumerate(cats):
                arr[i_w, i_c] = float(window_props[wn][c])
        return win_names, arr, q_values, q_stats

    win_names_sym, props_sym, q_sym, q_sym_stats = _membrane_window_props_exact(rep_sym, q_star=0.5)
    win_names_asym, props_asym, q_asym, q_asym_stats = _membrane_window_props_exact(rep_asym, q_star=0.5)

    # Align windows names for plotting.
    win_names = ["peak1", "valley", "peak2"]
    def _align(win_src: List[str], arr: np.ndarray) -> np.ndarray:
        out = np.zeros((len(win_names), arr.shape[1]), dtype=float)
        map_idx = {name: i for i, name in enumerate(win_src)}
        for i, n in enumerate(win_names):
            j = map_idx.get(n)
            if j is None:
                continue
            out[i, :] = arr[j, :]
        row_sums = np.sum(out, axis=1)
        for i in range(out.shape[0]):
            if row_sums[i] > 0:
                out[i, :] /= row_sums[i]
        return out

    props_sym = _align(win_names_sym, props_sym)
    props_asym = _align(win_names_asym, props_asym)

    plot_dual_window_panels(
        fig_dir / "membrane_class_window_bars.pdf",
        windows=win_names,
        categories=["L0R0", "L0R1", "L1R0", "L1R1"],
        left_props=props_sym,
        right_props=props_asym,
        left_title="Symmetric representative",
        right_title="Asymmetric representative",
    )
    cats_lr = ["L0R0", "L0R1", "L1R0", "L1R1"]
    dominant_sym = [cats_lr[int(np.argmax(props_sym[i, :]))] for i in range(len(win_names))]
    plot_membrane_class_legend(
        fig_dir / "membrane_class_legend.pdf",
        window_names=win_names,
        dominant_classes=dominant_sym,
    )

    # q* sensitivity (same exact decomposition, different commitment thresholds).
    qstar_rows: List[dict] = []
    for qstar in q_star_values:
        w_sym, arr_sym, _, _ = _membrane_window_props_exact(rep_sym, q_star=float(qstar))
        w_asy, arr_asy, _, _ = _membrane_window_props_exact(rep_asym, q_star=float(qstar))
        for i_w, wn in enumerate(w_sym):
            qstar_rows.append(
                {
                    "case": "sym",
                    "q_star": float(qstar),
                    "window": wn,
                    "L0R0": float(arr_sym[i_w, 0]),
                    "L0R1": float(arr_sym[i_w, 1]),
                    "L1R0": float(arr_sym[i_w, 2]),
                    "L1R1": float(arr_sym[i_w, 3]),
                }
            )
        for i_w, wn in enumerate(w_asy):
            qstar_rows.append(
                {
                    "case": "asym",
                    "q_star": float(qstar),
                    "window": wn,
                    "L0R0": float(arr_asy[i_w, 0]),
                    "L0R1": float(arr_asy[i_w, 1]),
                    "L1R0": float(arr_asy[i_w, 2]),
                    "L1R1": float(arr_asy[i_w, 3]),
                }
            )

    # ----- Study B: no-corridor two-target with near-start target -----
    Wy_two_target = 16
    base_near_dx_vals = (2, 3, 4, 5, 6, 7, 8, 9, 10)
    dense_bx_vals = (0.00, 0.02, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.14, 0.16)
    candidate_specs = [
        TwoTargetGridSpec(
            name="baseline",
            near_dy=2,
            near_dx_vals=base_near_dx_vals,
            bx_vals=(0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16),
        ),
        TwoTargetGridSpec(
            name="dense_bx_near_dy3",
            near_dy=3,
            near_dx_vals=base_near_dx_vals,
            bx_vals=dense_bx_vals,
        ),
        TwoTargetGridSpec(
            name="dense_bx_near_dy4",
            near_dy=4,
            near_dx_vals=base_near_dx_vals,
            bx_vals=dense_bx_vals,
        ),
    ]
    optimization_rounds: List[dict] = []
    tt_candidate_rows: List[dict] = []
    best_scan: dict | None = None
    for i_round, spec in enumerate(candidate_specs, start=1):
        try:
            scan = scan_two_target_grid(
                spec=spec,
                Lx=Lx,
                Wy_two_target=Wy_two_target,
                start_x=start_x,
                far_target_x=target_x,
                retries=2,
            )
            optimization_rounds.append(
                {
                    "round": i_round,
                    "spec": spec.name,
                    "status": "ok",
                    "near_dy": int(spec.near_dy),
                    "scan_size": int(scan["scan_size"]),
                    "phase2_count": int(scan["clear_count"]),
                    "phase2_ratio": float(scan["clear_ratio"]),
                }
            )
            for row in scan["rows"]:
                row_aug = dict(row)
                row_aug["spec"] = spec.name
                row_aug["round"] = int(i_round)
                tt_candidate_rows.append(enrich_two_target_quality(row_aug))
            if best_scan is None or (
                float(scan["clear_ratio"]),
                int(scan["clear_count"]),
            ) > (
                float(best_scan["clear_ratio"]),
                int(best_scan["clear_count"]),
            ):
                best_scan = scan
        except Exception as exc:  # pragma: no cover - runtime guard for long scans
            optimization_rounds.append(
                {
                    "round": i_round,
                    "spec": spec.name,
                    "status": "failed",
                    "near_dy": int(spec.near_dy),
                    "error": str(exc),
                }
            )
            continue

    if best_scan is None:
        fallback_spec = TwoTargetGridSpec(
            name="fallback_smoke",
            near_dy=2,
            near_dx_vals=(4, 6, 8),
            bx_vals=(0.04, 0.08, 0.12),
        )
        best_scan = scan_two_target_grid(
            spec=fallback_spec,
            Lx=Lx,
            Wy_two_target=Wy_two_target,
            start_x=start_x,
            far_target_x=target_x,
            retries=1,
        )
        optimization_rounds.append(
            {
                "round": len(optimization_rounds) + 1,
                "spec": fallback_spec.name,
                "status": "ok-fallback",
                "near_dy": int(fallback_spec.near_dy),
                "scan_size": int(best_scan["scan_size"]),
                "phase2_count": int(best_scan["clear_count"]),
                "phase2_ratio": float(best_scan["clear_ratio"]),
            }
        )
        for row in best_scan["rows"]:
            row_aug = dict(row)
            row_aug["spec"] = fallback_spec.name
            row_aug["round"] = len(optimization_rounds)
            tt_candidate_rows.append(enrich_two_target_quality(row_aug))

    # Adaptive local refinement around top candidate rows to improve
    # no-corridor clear-instance visual sharpness while keeping runtime bounded.
    if tt_candidate_rows:
        existing_points = {
            (
                float(round(float(r.get("bx", 0.0)), 6)),
                int(r.get("near_dx", 0)),
                int(r.get("near_dy", 0)),
            )
            for r in tt_candidate_rows
        }
        refine_points = [
            p
            for p in build_two_target_refinement_points(
                tt_candidate_rows,
                top_k=8,
                bx_step=0.005,
                bx_radius_steps=2,
                bx_bounds=(0.0, 0.20),
                near_dx_bounds=(2, 12),
                near_dy_bounds=(0, 6),
            )
            if p not in existing_points
        ]
        if refine_points:
            refine_round_id = len(optimization_rounds) + 1
            try:
                refine_scan = scan_two_target_points(
                    points=refine_points,
                    Lx=Lx,
                    Wy_two_target=Wy_two_target,
                    start_x=start_x,
                    far_target_x=target_x,
                    retries=2,
                )
                optimization_rounds.append(
                    {
                        "round": refine_round_id,
                        "spec": "adaptive_refine",
                        "status": "ok",
                        "near_dy": "mixed",
                        "scan_size": int(refine_scan["scan_size"]),
                        "phase2_count": int(refine_scan["clear_count"]),
                        "phase2_ratio": float(refine_scan["clear_ratio"]),
                    }
                )
                for row in refine_scan["rows"]:
                    row_aug = dict(row)
                    row_aug["spec"] = "adaptive_refine"
                    row_aug["round"] = int(refine_round_id)
                    tt_candidate_rows.append(enrich_two_target_quality(row_aug))
            except Exception as exc:  # pragma: no cover - runtime guard for long scans
                optimization_rounds.append(
                    {
                        "round": refine_round_id,
                        "spec": "adaptive_refine",
                        "status": "failed",
                        "near_dy": "mixed",
                        "scan_size": int(len(refine_points)),
                        "error": str(exc),
                    }
                )

    selected_spec: TwoTargetGridSpec = best_scan["spec"]
    near_dx_vals = list(selected_spec.near_dx_vals)
    bx_vals = list(selected_spec.bx_vals)
    near_dy = int(selected_spec.near_dy)
    tt_rows = [enrich_two_target_quality(r) for r in list(best_scan["rows"])]
    tt_phase = np.asarray(best_scan["phase_map"], dtype=float)
    tt_sep = np.asarray(best_scan["sep_map"], dtype=float)
    if not tt_candidate_rows:
        for row in tt_rows:
            row_aug = dict(row)
            row_aug["spec"] = selected_spec.name
            row_aug["round"] = 0
            tt_candidate_rows.append(enrich_two_target_quality(row_aug))

    save_csv(
        data_dir / "two_target_nearstart_scan.csv",
        tt_rows,
        fieldnames=[
            "Wy",
            "bx",
            "near_dx",
            "near_dy",
            "phase",
            "t_peak1",
            "t_peak2",
            "t_valley",
            "valley_over_max",
            "peak_ratio",
            "peak_minus_valley",
            "p_near",
            "p_far",
            "sep_mode_width",
            "t_mode_near",
            "t_mode_far",
            "clear_score",
            "showcase_score",
            "sep_margin",
            "mass_margin",
            "valley_margin",
            "peak_margin",
            "contrast_margin",
            "min_margin",
        ],
    )
    save_csv(
        data_dir / "two_target_candidate_scans.csv",
        tt_candidate_rows,
        fieldnames=[
            "spec",
            "round",
            "Wy",
            "bx",
            "near_dx",
            "near_dy",
            "phase",
            "t_peak1",
            "t_peak2",
            "t_valley",
            "valley_over_max",
            "peak_ratio",
            "peak_minus_valley",
            "p_near",
            "p_far",
            "sep_mode_width",
            "t_mode_near",
            "t_mode_far",
            "clear_score",
            "showcase_score",
            "sep_margin",
            "mass_margin",
            "valley_margin",
            "peak_margin",
            "contrast_margin",
            "min_margin",
        ],
    )

    plot_heatmap(
        fig_dir / "two_target_nearstart_phase_map.pdf",
        tt_phase,
        x_labels=[str(v) for v in near_dx_vals],
        y_labels=[f"{v:+.2f}" for v in bx_vals],
        title="No-corridor two-target phase map (near-target distance vs bx)",
        cmap="RdYlBu_r",
        cbar_label="phase",
        annotate_fmt="{:.0f}",
    )

    plot_heatmap(
        fig_dir / "two_target_nearstart_sep_map.pdf",
        tt_sep,
        x_labels=[str(v) for v in near_dx_vals],
        y_labels=[f"{v:+.2f}" for v in bx_vals],
        title="No-corridor two-target separation map",
        cmap="viridis",
        cbar_label="sep-score",
        annotate_fmt="{:.2f}",
    )

    rep_tt_row = select_two_target_representative(tt_rows)
    clear_tt_row = select_two_target_clear_instance(tt_candidate_rows)
    if clear_tt_row is None:
        clear_tt_row = enrich_two_target_quality(rep_tt_row)
        clear_tt_row["spec"] = selected_spec.name
    clear_selection_gate: str | None = None
    if isinstance(clear_tt_row.get("_selection_gate"), dict):
        clear_selection_gate = str(clear_tt_row.get("_selection_gate", {}).get("name", "")).strip() or None
    clear_tt_margins = two_target_phase2_margins(clear_tt_row)
    rep_tt_margins = two_target_phase2_margins(rep_tt_row)
    clear_primary_gate = {
        "name": "peak>=0.07,min>=0.07,valley<=0.10",
        "peak_margin_min": 0.07,
        "min_margin_min": 0.07,
        "valley_max": 0.10,
    }
    clear_primary_gate_audit = evaluate_two_target_gate(
        clear_tt_row,
        peak_margin_min=float(clear_primary_gate["peak_margin_min"]),
        min_margin_min=float(clear_primary_gate["min_margin_min"]),
        valley_max=float(clear_primary_gate["valley_max"]),
    )

    rep_tt = build_two_target_case(
        Lx=Lx,
        Wy=Wy_two_target,
        start_x=start_x,
        far_target_x=target_x,
        near_dx=int(rep_tt_row["near_dx"]),
        near_dy=int(rep_tt_row["near_dy"]),
        bx=float(rep_tt_row["bx"]),
    )
    clear_tt = build_two_target_case(
        Lx=Lx,
        Wy=Wy_two_target,
        start_x=start_x,
        far_target_x=target_x,
        near_dx=int(clear_tt_row["near_dx"]),
        near_dy=int(clear_tt_row["near_dy"]),
        bx=float(clear_tt_row["bx"]),
    )

    plot_two_target_geometry(
        fig_dir / "two_target_rep_geometry.pdf",
        Lx=Lx,
        case=rep_tt,
        title="No-corridor representative geometry",
    )

    t_tt = np.arange(len(rep_tt["f_any"]))
    plot_fpt_overlay(
        fig_dir / "two_target_rep_fpt.pdf",
        t=t_tt,
        f_total=rep_tt["f_any"],
        f_a=rep_tt["f_near"],
        f_b=rep_tt["f_far"],
        label_a="hit near target",
        label_b="hit far target",
        title=(
            "No-corridor representative "
            f"(d={rep_tt['near_dx']}, bx={rep_tt['bx']:+.2f}, near={rep_tt['near']}, far={rep_tt['far']})"
        ),
        peaks=(rep_tt["res"].t_peak1, rep_tt["res"].t_valley, rep_tt["res"].t_peak2),
    )
    plot_two_target_doublepeak_example(
        fig_dir / "two_target_rep_doublepeak_example.pdf",
        t=t_tt,
        f_total=rep_tt["f_any"],
        f_near=rep_tt["f_near"],
        f_far=rep_tt["f_far"],
        peaks=(rep_tt["res"].t_peak1, rep_tt["res"].t_valley, rep_tt["res"].t_peak2),
        title=(
            "No-corridor clear-double representative "
            f"(phase={rep_tt['res'].phase}, d={rep_tt['near_dx']}, bx={rep_tt['bx']:+.2f})"
        ),
        sep_score=float(rep_tt["res"].sep_mode_width),
        valley_ratio=None if rep_tt["res"].valley_over_max is None else float(rep_tt["res"].valley_over_max),
        p_near=float(np.sum(rep_tt["f_near"])),
        p_far=float(np.sum(rep_tt["f_far"])),
        peak_ratio=None if rep_tt["res"].peak_ratio is None else float(rep_tt["res"].peak_ratio),
        peak_margin=None if rep_tt_margins["peak_margin"] is None else float(rep_tt_margins["peak_margin"]),
        min_margin=float(rep_tt_margins["min_margin"]),
    )
    t_clear = np.arange(len(clear_tt["f_any"]))
    clear_fig_path = fig_dir / "two_target_no_corridor_clear_instance.pdf"
    plot_two_target_doublepeak_example(
        clear_fig_path,
        t=t_clear,
        f_total=clear_tt["f_any"],
        f_near=clear_tt["f_near"],
        f_far=clear_tt["f_far"],
        peaks=(clear_tt["res"].t_peak1, clear_tt["res"].t_valley, clear_tt["res"].t_peak2),
        title=(
            "No-corridor clear-double instance "
            f"(spec={clear_tt_row.get('spec', selected_spec.name)}, d={clear_tt['near_dx']}, "
            f"dy={clear_tt['near_dy']}, bx={clear_tt['bx']:+.2f})"
        ),
        sep_score=float(clear_tt["res"].sep_mode_width),
        valley_ratio=None if clear_tt["res"].valley_over_max is None else float(clear_tt["res"].valley_over_max),
        p_near=float(np.sum(clear_tt["f_near"])),
        p_far=float(np.sum(clear_tt["f_far"])),
        peak_ratio=None if clear_tt["res"].peak_ratio is None else float(clear_tt["res"].peak_ratio),
        peak_margin=None if clear_tt_margins["peak_margin"] is None else float(clear_tt_margins["peak_margin"]),
        min_margin=float(clear_tt_margins["min_margin"]),
        selection_gate=clear_selection_gate,
    )
    if (not clear_fig_path.exists()) or clear_fig_path.stat().st_size < 2048:
        raise ValueError("No-corridor clear-instance figure missing or too small after generation.")

    # Window-wise near/far mass fractions in representative two-target case.
    windows_tt = window_ranges(rep_tt["res"].t_peak1, rep_tt["res"].t_valley, rep_tt["res"].t_peak2, len(rep_tt["f_any"]))
    mass_rows: List[dict] = []
    win_names_tt: List[str] = []
    arr_nf = np.zeros((len(windows_tt), 2), dtype=float)
    for i_w, (name, lo, hi) in enumerate(windows_tt):
        lo_i = max(1, int(lo))
        hi_i = min(len(rep_tt["f_any"]) - 1, int(hi))
        near_mass = float(np.sum(rep_tt["f_near"][lo_i : hi_i + 1]))
        far_mass = float(np.sum(rep_tt["f_far"][lo_i : hi_i + 1]))
        total = max(1e-15, near_mass + far_mass)
        arr_nf[i_w, 0] = near_mass / total
        arr_nf[i_w, 1] = far_mass / total
        win_names_tt.append(name)
        mass_rows.append({
            "window": name,
            "t_lo": lo_i,
            "t_hi": hi_i,
            "near_fraction": arr_nf[i_w, 0],
            "far_fraction": arr_nf[i_w, 1],
        })

    save_csv(
        data_dir / "two_target_rep_window_split.csv",
        mass_rows,
        fieldnames=["window", "t_lo", "t_hi", "near_fraction", "far_fraction"],
    )
    save_csv(
        data_dir / "membrane_qstar_sensitivity.csv",
        qstar_rows,
        fieldnames=["case", "q_star", "window", "L0R0", "L0R1", "L1R0", "L1R1"],
    )

    plot_stacked_windows(
        fig_dir / "two_target_rep_window_split.pdf",
        windows=win_names_tt,
        categories=["near target", "far target"],
        proportions=arr_nf,
        title="Window-wise splitting composition (representative no-corridor case)",
        palette=["#1f77b4", "#ff7f0e"],
    )

    # Splitting committor closure for representative and dedicated clear-instance.
    split_rep = compute_two_target_splitting_committor(rep_tt, Lx=Lx)
    split_clear = compute_two_target_splitting_committor(clear_tt, Lx=Lx)
    p_far_rep = float(split_rep["p_far_mass"])
    p_near_rep = float(split_rep["p_near_mass"])

    # Write representative time series outputs.
    save_time_series(out_dir / "membrane_rep_sym_fpt.csv", rep_sym["f_total"], rep_sym["f_corr"], rep_sym["f_outer"])
    save_time_series(out_dir / "membrane_rep_asym_fpt.csv", rep_asym["f_total"], rep_asym["f_corr"], rep_asym["f_outer"])
    save_time_series(out_dir / "two_target_rep_fpt.csv", rep_tt["f_any"], rep_tt["f_near"], rep_tt["f_far"])

    # Tables used by TeX.
    sym_table_rows = write_table_symmetric(table_dir / "membrane_symmetric_w16.tex", sym_rows, wy_focus=16)
    asym_table_rows = write_table_asymmetric(
        table_dir / "membrane_asymmetric_topcases.tex",
        asym_rows,
        representative=rep_asym_row,
    )
    tt_table_rows = write_table_two_target(table_dir / "two_target_nearstart_summary.tex", tt_rows, bx_vals)
    write_table_two_target_representative(table_dir / "two_target_rep_case.tex", rep_tt_row)
    write_table_two_target_clear_instance(
        table_dir / "two_target_no_corridor_clear_instance.tex",
        clear_tt_row,
        split_gap=float(split_clear["consistency_gap_vs_f_far_mass"]),
        primary_gate_audit=clear_primary_gate_audit,
    )
    write_table_two_target_splitting_qc(
        table_dir / "two_target_splitting_committor_qc.tex",
        rep=split_rep,
        clear=split_clear,
    )

    if not _row_exists(sym_table_rows, rep_sym_row, keys=["Wy", "kappa"]):
        raise ValueError("Representative symmetric case is missing from membrane_symmetric_w16.tex.")
    if not _row_exists(asym_table_rows, rep_asym_row, keys=["kappa_top", "kappa_bottom"]):
        raise ValueError("Representative asymmetric case is missing from membrane_asymmetric_topcases.tex.")
    if not _row_exists(tt_table_rows, rep_tt_row, keys=["bx", "near_dx"]):
        raise ValueError("Representative two-target case is missing from two_target_nearstart_summary.tex.")
    if int(clear_tt_row.get("phase", 0)) < 2:
        raise ValueError("Failed to obtain a phase=2 no-corridor clear instance.")

    # Window class table for membrane representative pair.
    lines = [
        r"\begin{tabular}{@{}lccccc@{}}",
        r"\toprule",
        r"Window & Case & L0R0 & L0R1 & L1R0 & L1R1 \\",
        r"\midrule",
    ]
    for i, w in enumerate(win_names):
        lines.append(
            f"{w} & sym & {props_sym[i,0]:.3f} & {props_sym[i,1]:.3f} & {props_sym[i,2]:.3f} & {props_sym[i,3]:.3f} \\\\"
        )
        lines.append(
            f"{w} & asym & {props_asym[i,0]:.3f} & {props_asym[i,1]:.3f} & {props_asym[i,2]:.3f} & {props_asym[i,3]:.3f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    (table_dir / "membrane_window_classes.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # q* sensitivity table (compact: show dominant class + L1R1 fraction).
    lines_q = [
        r"\begin{tabular}{@{}lllc c@{}}",
        r"\toprule",
        r"Case & $q^*$ & Window & dominant class & $w_{\mathrm{L1R1}}$ \\",
        r"\midrule",
    ]
    for row in qstar_rows:
        vals = [float(row["L0R0"]), float(row["L0R1"]), float(row["L1R0"]), float(row["L1R1"])]
        dom = ["L0R0", "L0R1", "L1R0", "L1R1"][int(np.argmax(vals))]
        lines_q.append(
            f"{row['case']} & {float(row['q_star']):.1f} & {row['window']} & {dom} & {float(row['L1R1']):.3f} \\\\"
        )
    lines_q += [r"\bottomrule", r"\end{tabular}"]
    (table_dir / "membrane_qstar_sensitivity.tex").write_text("\n".join(lines_q) + "\n", encoding="utf-8")

    # Global summary json for report text.
    summary = {
        "baseline": {
            "Lx": Lx,
            "bx_base": bx_base,
            "start_x": start_x,
            "target_x": target_x,
            "corridor_halfwidth": corridor_halfwidth,
            "wall_margin": wall_margin,
            "delta_core": delta_core,
            "delta_open": delta_open,
        },
        "symmetric": {
            "scan_size": len(sym_rows),
            "phase2_count": int(sum(int(r["phase"]) >= 2 for r in sym_rows)),
            "phase2_positive_kappa_count": int(
                sum(int(r["phase"]) >= 2 and float(r["kappa"]) > 0.0 for r in sym_rows)
            ),
            "rep": {
                "Wy": int(rep_sym["Wy"]),
                "kappa": float(rep_sym["kappa_top"]),
                "phase": int(rep_sym["res"].phase),
                "t_peak1": None if rep_sym["res"].t_peak1 is None else int(rep_sym["res"].t_peak1),
                "t_peak2": None if rep_sym["res"].t_peak2 is None else int(rep_sym["res"].t_peak2),
                "t_valley": None if rep_sym["res"].t_valley is None else int(rep_sym["res"].t_valley),
                "sep": float(rep_sym["res"].sep_peaks),
                "valley_over_max": None if rep_sym["res"].valley_over_max is None else float(rep_sym["res"].valley_over_max),
                "in_symmetric_table": True,
            },
            "committor_stats": {
                "q_min": float(np.min(q_sym)),
                "q_max": float(np.max(q_sym)),
                "interior_residual_inf": float(q_sym_stats["interior_residual_inf"]),
                "boundary_A_residual_inf": float(q_sym_stats["boundary_A_residual_inf"]),
                "boundary_B_residual_inf": float(q_sym_stats["boundary_B_residual_inf"]),
            },
        },
        "asymmetric": {
            "scan_size": len(asym_rows),
            "phase2_count": int(sum(int(r["phase"]) >= 2 for r in asym_rows)),
            "phase2_nonsymmetric_count": int(
                sum(
                    int(r["phase"]) >= 2
                    and abs(float(r["kappa_top"]) - float(r["kappa_bottom"])) > 1e-12
                    for r in asym_rows
                )
            ),
            "phase2_positive_kappa_count": int(
                sum(
                    int(r["phase"]) >= 2
                    and (float(r["kappa_top"]) > 0.0 or float(r["kappa_bottom"]) > 0.0)
                    for r in asym_rows
                )
            ),
            "rep": {
                "Wy": int(rep_asym["Wy"]),
                "kappa_top": float(rep_asym["kappa_top"]),
                "kappa_bottom": float(rep_asym["kappa_bottom"]),
                "phase": int(rep_asym["res"].phase),
                "t_peak1": None if rep_asym["res"].t_peak1 is None else int(rep_asym["res"].t_peak1),
                "t_peak2": None if rep_asym["res"].t_peak2 is None else int(rep_asym["res"].t_peak2),
                "t_valley": None if rep_asym["res"].t_valley is None else int(rep_asym["res"].t_valley),
                "sep": float(rep_asym["res"].sep_peaks),
                "valley_over_max": None if rep_asym["res"].valley_over_max is None else float(rep_asym["res"].valley_over_max),
                "in_asymmetric_table": True,
            },
            "committor_stats": {
                "q_min": float(np.min(q_asym)),
                "q_max": float(np.max(q_asym)),
                "interior_residual_inf": float(q_asym_stats["interior_residual_inf"]),
                "boundary_A_residual_inf": float(q_asym_stats["boundary_A_residual_inf"]),
                "boundary_B_residual_inf": float(q_asym_stats["boundary_B_residual_inf"]),
            },
        },
        "membrane_lr_exact": {
            "method": "augmented_state_exact",
            "q_star_values": [float(v) for v in q_star_values],
            "window_names": [str(w) for w in win_names],
            "dominant_sym_q05": [cats_lr[int(np.argmax(props_sym[i, :]))] for i in range(len(win_names))],
            "dominant_asym_q05": [cats_lr[int(np.argmax(props_asym[i, :]))] for i in range(len(win_names))],
            "qstar_rows": qstar_rows,
        },
        "two_target_no_corridor": {
            "scan_size": len(tt_rows),
            "phase2_count": int(sum(int(r["phase"]) >= 2 for r in tt_rows)),
            "phase2_ratio": float(sum(int(r["phase"]) >= 2 for r in tt_rows)) / float(max(1, len(tt_rows))),
            "candidate_scan_size": int(len(tt_candidate_rows)),
            "candidate_phase2_count": int(sum(int(r.get("phase", 0)) >= 2 for r in tt_candidate_rows)),
            "candidate_phase2_ratio": float(sum(int(r.get("phase", 0)) >= 2 for r in tt_candidate_rows))
            / float(max(1, len(tt_candidate_rows))),
            "selected_grid": {
                "spec": selected_spec.name,
                "near_dy": int(near_dy),
                "near_dx_vals": [int(v) for v in near_dx_vals],
                "bx_vals": [float(v) for v in bx_vals],
            },
            "optimization_rounds": optimization_rounds,
            "adaptive_refine_enabled": True,
            "primary_clear_gate": clear_primary_gate,
            "selection_rule": (
                "maximize clear_score = sep_mode * (1 - valley/max) * (0.30 + min(Pnear,Pfar)) "
                "among phase=2 rows with min(Pnear,Pfar)>=0.25 when available; "
                "then run adaptive local refinement around top candidates and apply robust gating "
                "before clear-instance showcase selection (first gate: peak-margin>=0.07, "
                "min-margin>=0.07, valley/max<=0.10)"
            ),
            "rep": {
                "Wy": int(rep_tt["Wy"]),
                "bx": float(rep_tt["bx"]),
                "near_dx": int(rep_tt["near_dx"]),
                "near_dy": int(rep_tt["near_dy"]),
                "phase": int(rep_tt["res"].phase),
                "p_near": p_near_rep,
                "p_far": p_far_rep,
                "t_peak1": None if rep_tt["res"].t_peak1 is None else int(rep_tt["res"].t_peak1),
                "t_peak2": None if rep_tt["res"].t_peak2 is None else int(rep_tt["res"].t_peak2),
                "t_valley": None if rep_tt["res"].t_valley is None else int(rep_tt["res"].t_valley),
                "sep_mode": float(rep_tt["res"].sep_mode_width),
                "valley_over_max": None if rep_tt["res"].valley_over_max is None else float(rep_tt["res"].valley_over_max),
                "peak_ratio": None if rep_tt["res"].peak_ratio is None else float(rep_tt["res"].peak_ratio),
                "clear_score": float(two_target_clear_score(rep_tt_row)),
                "in_summary_table": True,
            },
            "clear_instance": {
                "spec": str(clear_tt_row.get("spec", selected_spec.name)),
                "bx": float(clear_tt_row["bx"]),
                "near_dx": int(clear_tt_row["near_dx"]),
                "near_dy": int(clear_tt_row["near_dy"]),
                "phase": int(clear_tt_row["phase"]),
                "p_near": float(np.sum(clear_tt["f_near"])),
                "p_far": float(np.sum(clear_tt["f_far"])),
                "sep_mode": float(clear_tt["res"].sep_mode_width),
                "valley_over_max": None if clear_tt["res"].valley_over_max is None else float(clear_tt["res"].valley_over_max),
                "peak_ratio": None if clear_tt["res"].peak_ratio is None else float(clear_tt["res"].peak_ratio),
                "clear_score": float(two_target_clear_score(clear_tt_row)),
                "showcase_score": float(two_target_showcase_score(clear_tt_row)),
                "phase2_margins": clear_tt_margins,
                "primary_gate_audit": clear_primary_gate_audit,
                "primary_gate_pass": bool(clear_primary_gate_audit["passes"]),
                "primary_gate_min_slack": float(clear_primary_gate_audit["min_slack_all"]),
                "from_selected_grid": bool(
                    str(clear_tt_row.get("spec", selected_spec.name)) == str(selected_spec.name)
                ),
                "selection_gate": clear_tt_row.get("_selection_gate", {}),
                "figure": {
                    "path": str(clear_fig_path.relative_to(report_dir)),
                    "exists": bool(clear_fig_path.exists()),
                    "size_bytes": int(clear_fig_path.stat().st_size) if clear_fig_path.exists() else 0,
                },
            },
            "splitting_committor": split_rep,
            "splitting_committor_rep": split_rep,
            "splitting_committor_clear_instance": split_clear,
        },
    }
    (data_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("[done] generated membrane + near-target report assets")
    print(f"[summary] {data_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
