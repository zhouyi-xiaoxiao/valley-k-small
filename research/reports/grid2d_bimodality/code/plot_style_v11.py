#!/usr/bin/env python3
"""Shared Fig.3-style drawing utilities for v11 (fig3v4)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib import patheffects as pe

from plotting_utils import savefig_clean, savefig_clean_pair
from viz.case_data import CaseGeometry

Coord = Tuple[int, int]


@dataclass(frozen=True)
class ViewBox:
    x0: int
    x1: int
    y0: int
    y1: int


def apply_style_v11() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 200,
            "savefig.dpi": 600,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "axes.linewidth": 0.9,
            "lines.linewidth": 1.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_clean(fig: plt.Figure, outpath: Path, *, dpi: int = 900) -> None:
    if outpath.suffix.lower() == ".png":
        savefig_clean(fig, outpath, dpi=dpi)
    else:
        savefig_clean_pair(fig, outpath.with_suffix(""), dpi=dpi)


def anchored_box(ax: plt.Axes, text: str, *, loc: str, fontsize: int = 9) -> None:
    at = AnchoredText(text, loc=loc, prop=dict(size=fontsize), frameon=True, pad=0.2, borderpad=0.3)
    at.patch.set_alpha(0.88)
    at.patch.set_facecolor("white")
    at.patch.set_edgecolor("0.7")
    ax.add_artist(at)


def _view_limits(N: int, view: Optional[ViewBox]) -> Tuple[int, int, int, int]:
    if view is None:
        return 1, N, 1, N
    return view.x0, view.x1, view.y0, view.y1


def draw_base(
    ax: plt.Axes,
    N: int,
    *,
    view: Optional[ViewBox] = None,
    coarse_grid_step: int = 8,
    fine_grid: bool = False,
    show_axes: bool = False,
) -> None:
    x0, x1, y0, y1 = _view_limits(N, view)
    ax.set_facecolor("#f6f2ea")

    if coarse_grid_step > 0:
        for k in range(((x0 - 1) // coarse_grid_step + 1) * coarse_grid_step, x1, coarse_grid_step):
            ax.axvline(k + 0.5, color="0.92", lw=0.6, zorder=0)
        for k in range(((y0 - 1) // coarse_grid_step + 1) * coarse_grid_step, y1, coarse_grid_step):
            ax.axhline(k + 0.5, color="0.92", lw=0.6, zorder=0)

    if fine_grid:
        for k in range(x0, x1):
            ax.axvline(k + 0.5, color="0.95", lw=0.4, zorder=0)
        for k in range(y0, y1):
            ax.axhline(k + 0.5, color="0.95", lw=0.4, zorder=0)

    ax.add_patch(Rectangle((x0 - 0.5, y0 - 0.5), x1 - x0 + 1, y1 - y0 + 1, fill=False, lw=1.2))
    ax.set_xlim(x0 - 0.5, x1 + 0.5)
    ax.set_ylim(y0 - 0.5, y1 + 0.5)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    if not show_axes:
        ax.set_xticks([])
        ax.set_yticks([])


def _edge_segment(edge: Tuple[Coord, Coord]) -> Tuple[Sequence[float], Sequence[float]]:
    (x1, y1), (x2, y2) = edge
    if x1 == x2:
        y = max(y1, y2) - 0.5
        return [x1 - 0.5, x1 + 0.5], [y, y]
    x = max(x1, x2) - 0.5
    return [x, x], [y1 - 0.5, y1 + 0.5]


def draw_walls(ax: plt.Axes, wall_segments: Sequence[Tuple[Coord, Coord]]) -> None:
    for edge in wall_segments:
        xs, ys = _edge_segment(edge)
        ax.plot(xs, ys, color="black", lw=2.6, zorder=5)


def draw_door(
    ax: plt.Axes,
    door_segments: Sequence[Tuple[Coord, Coord]],
    *,
    p_pass: float,
    label: bool = True,
) -> None:
    for edge in door_segments:
        xs, ys = _edge_segment(edge)
        ax.plot(xs, ys, color="#b30000", lw=2.6, ls=(0, (3, 2)), zorder=6)
    if label and door_segments:
        (a, b) = door_segments[0]
        x_mid = 0.5 * (a[0] + b[0])
        y_mid = 0.5 * (a[1] + b[1])
        ax.text(
            x_mid + 0.6,
            y_mid - 0.6,
            f"p={p_pass:.2f}",
            fontsize=9,
            color="black",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="0.6", alpha=0.85),
        )


def draw_sticky(ax: plt.Axes, sticky_cells: Sequence[Coord]) -> None:
    for (x, y) in sticky_cells:
        rect = Rectangle(
            (x - 0.5, y - 0.5),
            1.0,
            1.0,
            facecolor="#9fb3b5",
            edgecolor="#6b7a78",
            hatch="///",
            alpha=0.35,
            lw=0.6,
            zorder=2,
        )
        ax.add_patch(rect)


def draw_corridor_band(
    ax: plt.Axes,
    corridor: Optional[dict],
    *,
    band_rows: Sequence[int] | None = None,
    band_halfwidth: int = 1,
    color: str = "#fdb462",
    alpha: float = 0.25,
) -> None:
    if not corridor:
        return
    x0 = int(corridor["x_start"])
    x1 = int(corridor["x_end"])
    if band_rows:
        y_min = min(band_rows)
        y_max = max(band_rows)
    else:
        y_min = int(corridor["y"]) - band_halfwidth
        y_max = int(corridor["y"]) + band_halfwidth
    height = y_max - y_min + 1
    rect = Rectangle(
        (x0 - 0.5, y_min - 0.5),
        (x1 - x0 + 1),
        height,
        facecolor=color,
        edgecolor="#b35806",
        alpha=alpha,
        lw=0.8,
        zorder=1,
    )
    ax.add_patch(rect)


def draw_local_bias(
    ax: plt.Axes, bias_arrows: Sequence[Tuple[int, int, str]], *, step: int = 1
) -> None:
    if step <= 0:
        step = 1
    for idx, (x, y, direction) in enumerate(bias_arrows):
        if idx % step != 0:
            continue
        dx, dy = 0.0, 0.0
        if direction == "left":
            dx = -0.65
        elif direction == "right":
            dx = 0.65
        elif direction == "up":
            dy = -0.65
        elif direction == "down":
            dy = 0.65
        arrow = FancyArrowPatch(
            (x, y),
            (x + dx, y + dy),
            arrowstyle="-|>",
            mutation_scale=12,
            lw=1.4,
            color="#d62728",
            zorder=6,
        )
        ax.add_patch(arrow)


def draw_start_target(ax: plt.Axes, start: Coord, target: Coord) -> None:
    ax.scatter([start[0]], [start[1]], s=90, c="#e41a1c", marker="s", edgecolors="black", zorder=7)
    ax.scatter([target[0]], [target[1]], s=90, c="#377eb8", marker="D", edgecolors="black", zorder=7)


def draw_global_bias(ax: plt.Axes, gx: float, gy: float, *, anchor: Coord) -> None:
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
        lw=2.0,
        color="#2b2b2b",
        clip_on=False,
    )
    ax.add_patch(arrow)
    ax.text(
        x0 + 0.2,
        y0 + 0.4,
        f"global bias\n g=({gx:.2f},{gy:.2f})",
        fontsize=9,
        color="0.2",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.7", alpha=0.85),
    )


def draw_axes_indicator(ax: plt.Axes, *, anchor: Coord = (2, 2)) -> None:
    x0, y0 = anchor
    ax.annotate(
        "",
        xy=(x0 + 2.0, y0),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="-|>", lw=1.2, color="0.3"),
    )
    ax.annotate(
        "",
        xy=(x0, y0 + 2.0),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="-|>", lw=1.2, color="0.3"),
    )
    ax.text(x0 + 2.1, y0, "x", fontsize=8, color="0.25", va="center")
    ax.text(x0, y0 + 2.1, "y", fontsize=8, color="0.25", ha="center")


def draw_boundaries(ax: plt.Axes, case: CaseGeometry, *, view: Optional[ViewBox]) -> None:
    x0, x1, y0, y1 = _view_limits(case.N, view)
    y_mid = 0.5 * (y0 + y1)
    if case.boundary_x == "periodic":
        ax.annotate(
            "",
            xy=(x0 + 0.4, y_mid),
            xytext=(x0 + 1.4, y_mid),
            arrowprops=dict(arrowstyle="-|>", lw=1.0, color="0.25"),
        )
        ax.annotate(
            "",
            xy=(x1 - 0.4, y_mid),
            xytext=(x1 - 1.4, y_mid),
            arrowprops=dict(arrowstyle="-|>", lw=1.0, color="0.25"),
        )


def collect_roi_points(case: CaseGeometry, *, include_start_target: bool = True) -> List[Coord]:
    pts: List[Coord] = []
    if include_start_target:
        pts.extend([case.start, case.target])
    for item in case.local_bias:
        pts.append((int(item["x"]), int(item["y"])))
    for item in case.sticky:
        pts.append((int(item["x"]), int(item["y"])))
    if case.corridor:
        pts.append((int(case.corridor["x_start"]), int(case.corridor["y"])))
        pts.append((int(case.corridor["x_end"]), int(case.corridor["y"])))
    for edge, _ in case.barriers_perm:
        pts.append(edge[0])
        pts.append(edge[1])
    return pts


def roi_bounds(points: Sequence[Coord], N: int, *, margin: int = 6) -> ViewBox:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0 = max(1, min(xs) - margin)
    x1 = min(N, max(xs) + margin)
    y0 = max(1, min(ys) - margin)
    y1 = min(N, max(ys) + margin)
    return ViewBox(x0, x1, y0, y1)


def roi_bounds_auto(case: CaseGeometry, *, margin: int = 6, max_frac: float = 0.7) -> ViewBox:
    points = collect_roi_points(case, include_start_target=True)
    roi = roi_bounds(points, case.N, margin=margin)
    width = roi.x1 - roi.x0 + 1
    height = roi.y1 - roi.y0 + 1
    if max(width, height) >= int(max_frac * case.N):
        feature_pts = collect_roi_points(case, include_start_target=False)
        if feature_pts:
            roi_feature = roi_bounds(feature_pts, case.N, margin=max(3, margin - 2))
            width_f = roi_feature.x1 - roi_feature.x0 + 1
            height_f = roi_feature.y1 - roi_feature.y0 + 1
            if max(width_f, height_f) < max(width, height):
                return roi_feature
    return roi


def smooth_ma(y: np.ndarray, w: int) -> np.ndarray:
    if w <= 1:
        return y
    k = np.ones(w, dtype=np.float64) / float(w)
    return np.convolve(y, k, mode="same")


def local_maxima(y: np.ndarray) -> np.ndarray:
    return np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1


def pick_two_peaks(y: np.ndarray, idx: np.ndarray, *, min_sep: int) -> Optional[Tuple[int, int]]:
    if idx.size < 2:
        return None
    order = idx[np.argsort(y[idx])[::-1]]
    p1 = int(order[0])
    for p2 in order[1:]:
        if abs(int(p2) - p1) >= min_sep:
            return tuple(sorted((p1, int(p2))))
    return None


def compute_bimodality_metrics(
    f: np.ndarray,
    *,
    smooth_w: int = 9,
    min_sep: int = 5,
    min_gap: int = 20,
    min_height: float = 1e-12,
) -> dict:
    f = np.asarray(f, dtype=np.float64)
    ys = smooth_ma(f, smooth_w)
    peaks = local_maxima(ys)
    peaks = peaks[ys[peaks] >= min_height]
    pair = pick_two_peaks(ys, peaks, min_sep=min_sep)
    if pair is None:
        raise RuntimeError("Failed to find two separated peaks.")
    p1, p2 = pair
    if (p2 - p1) < min_gap:
        raise RuntimeError("Peak separation too small.")
    v = int(p1 + np.argmin(ys[p1 : p2 + 1]))
    h1, h2, hv = float(ys[p1]), float(ys[p2]), float(ys[v])
    t_p1, t_p2, t_v = int(p1 + 1), int(p2 + 1), int(v + 1)
    peak_ratio = min(h1, h2) / max(h1, h2) if max(h1, h2) > 0 else 0.0
    valley_ratio = hv / min(h1, h2) if min(h1, h2) > 0 else 1.0
    return {
        "t_p1": t_p1,
        "t_p2": t_p2,
        "t_v": t_v,
        "h1": h1,
        "h2": h2,
        "hv": hv,
        "h2_over_h1": h2 / h1 if h1 > 0 else np.nan,
        "peak_ratio": peak_ratio,
        "valley_ratio": valley_ratio,
        "valley_depth": 1.0 - valley_ratio,
        "gap": int(t_p2 - t_p1),
        "smooth_window": int(smooth_w),
        "min_sep": int(min_sep),
        "min_gap": int(min_gap),
    }


def corridor_band_rows(
    *, y0: int, band_halfwidth: int, N: int, band_rows: Sequence[int] | None = None
) -> List[int]:
    if band_rows:
        rows = [int(y) for y in band_rows]
    else:
        rows = list(range(int(y0) - band_halfwidth, int(y0) + band_halfwidth + 1))
    rows = [y for y in rows if 1 <= y <= N]
    if not rows:
        raise ValueError("corridor band rows empty.")
    return rows


def format_corridor_band_label(rows: Sequence[int]) -> str:
    if not rows:
        return "corridor y=∅"
    rows = sorted(set(int(y) for y in rows))
    if rows == list(range(rows[0], rows[-1] + 1)):
        return f"corridor y ∈ [{rows[0]},{rows[-1]}]"
    return "corridor y ∈ {" + ",".join(str(y) for y in rows) + "}"


def heatmap_limits(mats: Sequence[np.ndarray], *, eps: float = 1e-14, q: float = 1e-4) -> Tuple[float, float]:
    vals = np.concatenate([m.ravel() for m in mats])
    vals = vals[np.isfinite(vals)]
    vals = vals[vals > eps]
    vmin = eps if vals.size == 0 else max(eps, float(np.quantile(vals, q)))
    vmax = max(float(np.max(m)) for m in mats)
    return vmin, vmax


def plot_log_heatmap_P(
    ax: plt.Axes,
    P: np.ndarray,
    *,
    N: int,
    vmin: float,
    vmax: float,
    eps: float = 1e-14,
    cmap_name: str = "magma",
) -> None:
    P2 = np.array(P, dtype=np.float64)
    P2[P2 <= eps] = np.nan
    cmap = plt.get_cmap(cmap_name).copy()
    cmap.set_under("#0b1b3b")
    cmap.set_bad("#f6f2ea")
    ax.imshow(
        P2.T,
        origin="lower",
        interpolation="nearest",
        extent=(0.5, N + 0.5, 0.5, N + 0.5),
        cmap=cmap,
        norm=LogNorm(vmin=vmin, vmax=vmax),
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    ax.invert_yaxis()


def pick_text_corner(points_xy: Sequence[Coord], xlim: Tuple[float, float], ylim: Tuple[float, float]) -> str:
    corners = {
        "SW": (xlim[0], ylim[0]),
        "SE": (xlim[1], ylim[0]),
        "NW": (xlim[0], ylim[1]),
        "NE": (xlim[1], ylim[1]),
    }
    best = "NE"
    best_score = -1.0
    for name, (cx, cy) in corners.items():
        d2 = [(cx - x) ** 2 + (cy - y) ** 2 for (x, y) in points_xy]
        score = min(d2) if d2 else float("inf")
        if score > best_score:
            best_score = score
            best = name
    return best


def add_time_tag(ax: plt.Axes, t: int, *, avoid_points: Sequence[Coord] | None = None) -> None:
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    corner = "NE"
    if avoid_points:
        corner = pick_text_corner(avoid_points, xlim, ylim)
    pos_map = {
        "NE": (0.97, 0.96, "right", "top"),
        "NW": (0.03, 0.96, "left", "top"),
        "SE": (0.97, 0.06, "right", "bottom"),
        "SW": (0.03, 0.06, "left", "bottom"),
    }
    x, y, ha, va = pos_map.get(corner, pos_map["NE"])
    txt = ax.text(
        x,
        y,
        f"t={t}",
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=10,
        color="white",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="black", alpha=0.35, linewidth=0.0),
        clip_on=True,
    )
    txt.set_path_effects([pe.withStroke(linewidth=2, foreground="black")])


def write_gallery_html(fig_root: Path) -> None:
    items = []
    for path in sorted(fig_root.rglob("*.png")):
        rel = path.relative_to(fig_root)
        items.append((rel.as_posix(), rel.stem))
    title = fig_root.name
    html_lines = [
        "<!doctype html>",
        f"<html><head><meta charset='utf-8'><title>{title} gallery</title>",
        "<style>body{font-family:Arial,Helvetica,sans-serif;} .item{margin:12px 0;} img{max-width:520px;border:1px solid #ccc;}</style>",
        "</head><body>",
        f"<h1>{title} gallery</h1>",
    ]
    for rel, name in items:
        html_lines.append("<div class='item'>")
        html_lines.append(f"<div><strong>{name}</strong></div>")
        html_lines.append(f"<div><img src='{rel}' alt='{name}'></div>")
        html_lines.append(f"<div><code>{rel}</code></div>")
        html_lines.append("</div>")
    html_lines.append("</body></html>")
    (fig_root / "gallery.html").write_text("\n".join(html_lines), encoding="utf-8")
