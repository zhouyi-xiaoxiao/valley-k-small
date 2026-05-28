#!/usr/bin/env python3
"""Sweep Luca's K=2 fixed-shortcut first-passage setup."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

REPO_ROOT = Path(__file__).resolve().parents[4]
VKCORE_SRC = REPO_ROOT / "packages" / "vkcore" / "src"
if str(VKCORE_SRC) not in sys.path:
    sys.path.insert(0, str(VKCORE_SRC))

import jumpover_bimodality_pipeline as jp


def default_beta_grid(beta_max: float, step: float, beta_c: float) -> list[float]:
    vals = list(np.arange(0.0, beta_max + 0.5 * step, step, dtype=float))
    vals.extend([0.001, 0.005, 0.01, beta_c, 0.75 * beta_c, 1.25 * beta_c])
    out = sorted({round(float(x), 10) for x in vals if 0.0 <= float(x) <= beta_max})
    return out


def parse_float_list(text: str | None) -> list[float] | None:
    if text is None:
        return None
    vals = [v.strip() for v in text.split(",") if v.strip()]
    return [float(v) for v in vals]


def parse_int_list(text: str | None) -> list[int] | None:
    if text is None:
        return None
    vals = [v.strip() for v in text.split(",") if v.strip()]
    return [int(v) for v in vals]


def make_params(
    *,
    N: int,
    K: int,
    q: float,
    beta: float,
    rho: float,
    n0_paper: int,
    target_paper: int,
    sc_src_paper: int,
    sc_dst_paper: int,
) -> "jp.Params":
    return jp.Params(
        N=int(N),
        K=int(K),
        n0=jp.paper_to0(int(n0_paper), int(N)),
        target=jp.paper_to0(int(target_paper), int(N)),
        sc_src=jp.paper_to0(int(sc_src_paper), int(N)),
        sc_dst=jp.paper_to0(int(sc_dst_paper), int(N)),
        mode="lazy_selfloop",
        q=float(q),
        beta=float(beta),
        rho=float(rho),
        jumpover_absorbs=False,
    )


def analyze_curve(
    f: np.ndarray,
    *,
    hmin: float,
    second_rel_height: float,
    min_peak_separation: int,
    max_valley_ratio: float,
) -> dict[str, object]:
    peaks = jp.detect_peaks_paper(f, hmin=float(hmin), second_rel_height=float(second_rel_height))
    t1, tv, t2 = jp.first_two_peaks_and_valley(f, peaks)
    h1 = float(f[t1 - 1]) if t1 is not None else math.nan
    h2 = float(f[t2 - 1]) if t2 is not None else math.nan
    hv = float(f[tv - 1]) if tv is not None else math.nan
    peak_sep = (int(t2) - int(t1)) if (t1 is not None and t2 is not None) else math.nan
    hmax = max(h1, h2) if (not math.isnan(h1) and not math.isnan(h2)) else math.nan
    valley_ratio = (hv / hmax) if (not math.isnan(hv) and hmax > 0.0) else math.nan
    paper_double_peak = len(peaks) >= 2
    clear_double_peak = bool(
        paper_double_peak
        and not math.isnan(peak_sep)
        and peak_sep >= int(min_peak_separation)
        and not math.isnan(valley_ratio)
        and valley_ratio <= float(max_valley_ratio)
    )
    return {
        "n_peaks": int(len(peaks)),
        "paper_double_peak": bool(paper_double_peak),
        "clear_double_peak": bool(clear_double_peak),
        "t1": t1,
        "tv": tv,
        "t2": t2,
        "h1": h1,
        "hv": hv,
        "h2": h2,
        "h2_over_h1": (h2 / h1) if (not math.isnan(h1) and h1 > 0.0 and not math.isnan(h2)) else math.nan,
        "valley_ratio": valley_ratio,
        "peak_separation": peak_sep,
    }


def compute_rows(
    *,
    N: int,
    K: int,
    q: float,
    rho: float,
    n0_values: Iterable[int],
    target_paper: int,
    sc_src_paper: int,
    sc_dst_paper: int,
    betas: Iterable[float],
    tmax: int,
    survival_eps: float,
    hmin: float,
    second_rel_height: float,
    min_peak_separation: int,
    max_valley_ratio: float,
    selected_betas: set[float],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    beta_c = 2.0 * float(q) / ((1.0 - float(q)) * float(N))
    rows: list[dict[str, object]] = []
    selected_curve_rows: list[dict[str, object]] = []

    for n0_paper in n0_values:
        for beta in betas:
            params = make_params(
                N=N,
                K=K,
                q=q,
                beta=float(beta),
                rho=rho,
                n0_paper=int(n0_paper),
                target_paper=target_paper,
                sc_src_paper=sc_src_paper,
                sc_dst_paper=sc_dst_paper,
            )
            f, survival = jp.exact_first_absorption_pmf(
                params,
                tmax=int(tmax),
                survival_eps=float(survival_eps),
            )
            metrics = analyze_curve(
                f,
                hmin=hmin,
                second_rel_height=second_rel_height,
                min_peak_separation=min_peak_separation,
                max_valley_ratio=max_valley_ratio,
            )
            beta_below_luca = float(beta) < beta_c - 1e-12
            beta_at_luca = abs(float(beta) - beta_c) <= 1e-12
            rows.append(
                {
                    "N": int(N),
                    "K": int(K),
                    "q": float(q),
                    "rho": float(rho),
                    "n0_paper": int(n0_paper),
                    "target_paper": int(target_paper),
                    "sc_src_paper": int(sc_src_paper),
                    "sc_dst_paper": int(sc_dst_paper),
                    "beta": float(beta),
                    "p_shortcut": float(beta) * (1.0 - float(q)),
                    "luca_beta_c": beta_c,
                    "beta_over_luca": float(beta) / beta_c if beta_c > 0 else math.nan,
                    "beta_below_luca": beta_below_luca,
                    "beta_at_luca": beta_at_luca,
                    "mass": float(np.sum(f)),
                    "survival_tail": float(survival),
                    "tmax_used": int(f.size),
                    **metrics,
                }
            )
            if any(abs(float(beta) - b) <= 1e-12 for b in selected_betas):
                for t, val in enumerate(f, start=1):
                    selected_curve_rows.append(
                        {
                            "n0_paper": int(n0_paper),
                            "target_paper": int(target_paper),
                            "beta": float(beta),
                            "t": int(t),
                            "f_t": float(val),
                        }
                    )

    return rows, selected_curve_rows


def write_dict_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def transition_summary(rows_in: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    n0_values = sorted({int(r["n0_paper"]) for r in rows_in})
    for n0 in n0_values:
        g = sorted([r for r in rows_in if int(r["n0_paper"]) == n0], key=lambda r: float(r["beta"]))
        yes = [r for r in g if bool(r["clear_double_peak"])]
        below = [r for r in g if bool(r["beta_below_luca"])]
        above = [r for r in g if not bool(r["beta_below_luca"])]
        first_no_after_yes = math.nan
        if yes:
            max_yes = max(float(r["beta"]) for r in yes)
            later_no = [r for r in g if float(r["beta"]) > max_yes and not bool(r["clear_double_peak"])]
            if later_no:
                first_no_after_yes = float(later_no[0]["beta"])
        rows.append(
            {
                "n0_paper": int(n0),
                "target_paper": int(g[0]["target_paper"]),
                "sc_src_paper": int(g[0]["sc_src_paper"]),
                "sc_dst_paper": int(g[0]["sc_dst_paper"]),
                "luca_beta_c": float(g[0]["luca_beta_c"]),
                "any_clear_double_peak": bool(any(bool(r["clear_double_peak"]) for r in g)),
                "max_beta_clear_double_peak": max(float(r["beta"]) for r in yes) if yes else math.nan,
                "first_beta_no_after_clear": first_no_after_yes,
                "clear_below_luca_count": sum(1 for r in below if bool(r["clear_double_peak"])),
                "clear_at_or_above_luca_count": sum(1 for r in above if bool(r["clear_double_peak"])),
                "grid_points": int(len(g)),
            }
        )
    return rows


def valley_over_min_peak(row: dict[str, object]) -> float:
    h1 = float(row["h1"])
    h2 = float(row["h2"])
    hv = float(row["hv"])
    if math.isnan(h1) or math.isnan(h2) or math.isnan(hv) or min(h1, h2) <= 0.0:
        return math.nan
    return hv / min(h1, h2)


def passes_definition(row: dict[str, object], definition: str) -> bool:
    if not bool(row["paper_double_peak"]):
        return False
    if float(row["peak_separation"]) < 10.0:
        return False
    h2_over_h1 = float(row["h2_over_h1"])
    if math.isnan(h2_over_h1) or h2_over_h1 < 0.1 or h2_over_h1 > 10.0:
        return False
    if definition == "local_maxima":
        return True
    if definition == "permissive":
        return float(row["valley_ratio"]) <= 0.9
    if definition == "visual":
        return valley_over_min_peak(row) <= 0.8
    if definition == "strong_visual":
        return valley_over_min_peak(row) <= 0.6
    raise ValueError(f"Unknown definition: {definition}")


def definition_comparison(rows_in: list[dict[str, object]]) -> list[dict[str, object]]:
    definitions = [
        (
            "local_maxima",
            "two local maxima",
            "two filtered peaks; peak separation $\\geq 10$; $0.1 \\leq h_2/h_1 \\leq 10$",
        ),
        (
            "permissive",
            "permissive valley",
            "local-maxima rule plus $h_v/\\max(h_1,h_2) \\leq 0.9$",
        ),
        (
            "visual",
            "visual double peak",
            "local-maxima rule plus $h_v/\\min(h_1,h_2) \\leq 0.8$",
        ),
        (
            "strong_visual",
            "strong visual double peak",
            "local-maxima rule plus $h_v/\\min(h_1,h_2) \\leq 0.6$",
        ),
    ]
    out = []
    for key, label, rule in definitions:
        passing = [r for r in rows_in if passes_definition(r, key)]
        at_or_above = [r for r in passing if float(r["beta"]) >= float(r["luca_beta_c"]) - 1e-12]
        max_beta_by_n0 = []
        for n0 in sorted({int(r["n0_paper"]) for r in rows_in}):
            g = [r for r in passing if int(r["n0_paper"]) == n0]
            max_beta_by_n0.append(f"n0={n0}: {max(float(r['beta']) for r in g):.3f}" if g else f"n0={n0}: none")
        beta_c_rows = [
            r
            for r in rows_in
            if abs(float(r["beta"]) - float(r["luca_beta_c"])) <= 1e-12 and int(r["n0_paper"]) in (1, 2, 3)
        ]
        beta_c_min_valley = [valley_over_min_peak(r) for r in beta_c_rows]
        beta_c_range = (
            f"{min(beta_c_min_valley):.3f}-{max(beta_c_min_valley):.3f}"
            if beta_c_min_valley
            else "--"
        )
        out.append(
            {
                "definition": key,
                "label": label,
                "rule": rule,
                "max_beta_by_n0": "; ".join(max_beta_by_n0),
                "count_at_or_above_beta_c": int(len(at_or_above)),
                "beta_c_valley_over_min_range_n0_1_3": beta_c_range,
            }
        )
    return out


def write_definition_comparison_tex(rows: list[dict[str, object]], outpath: Path) -> None:
    lines = [
        r"\begin{tabular}{L{0.21\linewidth} c L{0.39\linewidth} c}",
        r"\toprule",
        r"Definition & Cases with $\beta\geq\beta_c$ & Maximum passing $\beta$ & $\rho_c$ \\",
        r"\midrule",
    ]
    for row in rows:
        max_short = row["max_beta_by_n0"]
        if row["definition"] in ("visual", "strong_visual"):
            max_short = "; ".join(str(max_short).split("; ")[:3])
        lines.append(
            f"{row['label']} & {int(row['count_at_or_above_beta_c'])} & "
            f"{max_short} & {row['beta_c_valley_over_min_range_n0_1_3']} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    outpath.write_text("\n".join(lines), encoding="utf-8")


def write_selected_curves(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["n0_paper", "target_paper", "beta", "t", "f_t"])
        writer.writeheader()
        writer.writerows(rows)


def plot_double_peak_map(rows: list[dict[str, object]], outpath: Path) -> None:
    betas = np.asarray(sorted({float(r["beta"]) for r in rows}), dtype=float)
    n0s = np.asarray(sorted({int(r["n0_paper"]) for r in rows}), dtype=float)
    grid = np.zeros((len(n0s), len(betas)), dtype=float)
    row_idx = {int(n0): i for i, n0 in enumerate(n0s)}
    col_idx = {float(beta): j for j, beta in enumerate(betas)}
    for r in rows:
        grid[row_idx[int(r["n0_paper"])], col_idx[float(r["beta"])]] = 1.0 if bool(r["clear_double_peak"]) else 0.0

    fig, ax = plt.subplots(figsize=(9, 3.8), dpi=180)
    im = ax.imshow(
        grid,
        aspect="auto",
        origin="lower",
        interpolation="nearest",
        extent=[betas.min(), betas.max(), n0s.min() - 0.5, n0s.max() + 0.5],
        cmap=matplotlib.colors.ListedColormap(["#f2f2f2", "#2a9d8f"]),
        vmin=0,
        vmax=1,
    )
    beta_c = float(rows[0]["luca_beta_c"])
    ax.axvline(beta_c, color="#b00020", linewidth=1.4, linestyle="--", label=rf"proposed $\beta_c={beta_c:.3f}$")
    ax.set_xlabel(r"$\beta$")
    ax.set_ylabel(r"$n_0$ (paper index)")
    ax.set_title("Clear double-peak flag for fixed shortcut 6 -> 56")
    ax.set_yticks(n0s)
    ax.legend(loc="upper right", fontsize=8)
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1], pad=0.02)
    cbar.ax.set_yticklabels(["no", "yes"])
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_peak_times(rows: list[dict[str, object]], outpath: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 5.6), dpi=180, sharex=True)
    beta_c = float(rows[0]["luca_beta_c"])
    for ax, n0 in zip(axes.flat, sorted({int(r["n0_paper"]) for r in rows})):
        g = sorted([r for r in rows if int(r["n0_paper"]) == n0], key=lambda r: float(r["beta"]))
        beta_vals = [float(r["beta"]) for r in g]
        t1_vals = [float(r["t1"]) if r["t1"] is not None else math.nan for r in g]
        t2_vals = [float(r["t2"]) if r["t2"] is not None else math.nan for r in g]
        ax.plot(beta_vals, t1_vals, color="#264653", marker=".", linewidth=1, label=r"$t_1$")
        ax.plot(beta_vals, t2_vals, color="#e76f51", marker=".", linewidth=1, label=r"$t_2$")
        ax.axvline(beta_c, color="#b00020", linewidth=1, linestyle="--")
        ax.set_title(rf"$n_0={int(n0)}$", fontsize=9)
        ax.set_yscale("log")
        ax.grid(True, which="both", linewidth=0.35, alpha=0.35)
    for ax in axes[-1, :]:
        ax.set_xlabel(r"$\beta$")
    for ax in axes[:, 0]:
        ax.set_ylabel("peak time")
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Peak locations across beta", y=0.995, fontsize=11)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_representative_curves(rows: list[dict[str, object]], outpath: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(11, 6), dpi=180, sharex=True, sharey=True)
    max_t = max(int(r["t"]) for r in rows)
    for ax, n0 in zip(axes.flat, sorted({int(r["n0_paper"]) for r in rows})):
        g0 = [r for r in rows if int(r["n0_paper"]) == n0]
        for beta in sorted({float(r["beta"]) for r in g0}):
            g = sorted([r for r in g0 if float(r["beta"]) == beta], key=lambda r: int(r["t"]))
            label = rf"$\beta={float(beta):.3g}$"
            ax.plot([int(r["t"]) for r in g], [float(r["f_t"]) for r in g], linewidth=0.9, label=label)
        ax.set_title(rf"$n_0={int(n0)}$", fontsize=9)
        ax.set_yscale("log")
        ax.set_xlim(1, min(3000, max_t))
        ax.grid(True, which="both", linewidth=0.35, alpha=0.35)
    for ax in axes[-1, :]:
        ax.set_xlabel("t")
    for ax in axes[:, 0]:
        ax.set_ylabel(r"$f(t)$")
    axes[0, 0].legend(fontsize=7)
    fig.suptitle("Representative first-passage curves", y=0.995, fontsize=11)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_ring_geometry(
    *,
    N: int,
    n0_values: list[int],
    sc_src_paper: int,
    sc_dst_paper: int,
    target_paper: int,
    outpath: Path,
) -> None:
    theta = np.linspace(0.0, 2.0 * np.pi, int(N), endpoint=False)
    x = np.cos(theta)
    y = np.sin(theta)

    def xy(paper_idx: int) -> tuple[float, float]:
        idx = (int(paper_idx) - 1) % int(N)
        return float(x[idx]), float(y[idx])

    fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=180)
    ax.plot(np.r_[x, x[0]], np.r_[y, y[0]], color="#c9c9c9", linewidth=1.2, zorder=1)
    ax.scatter(x, y, s=12, color="#d9d9d9", edgecolor="white", linewidth=0.25, zorder=2)

    # Show the n0 sweep as a small arc of candidate starts.
    start_xy = np.asarray([xy(v) for v in n0_values], dtype=float)
    ax.scatter(
        start_xy[:, 0],
        start_xy[:, 1],
        s=72,
        facecolor="#fff7bc",
        edgecolor="#d89c00",
        linewidth=1.2,
        zorder=4,
        label=r"$n_0=1,\ldots,6$",
    )

    ux, uy = xy(sc_src_paper)
    vx, vy = xy(sc_dst_paper)
    tx, ty = xy(target_paper)
    ax.scatter([ux], [uy], s=130, color="#264653", edgecolor="white", linewidth=0.9, zorder=6, label=r"$u=6$")
    ax.scatter([vx], [vy], s=145, marker="*", color="#e76f51", edgecolor="white", linewidth=0.7, zorder=7, label=r"$v=56$")
    if target_paper != sc_dst_paper:
        ax.scatter([tx], [ty], s=110, marker="s", color="#2a9d8f", edgecolor="white", linewidth=0.7, zorder=7, label="target")

    shortcut_arrow = FancyArrowPatch(
        (ux, uy),
        (vx, vy),
        connectionstyle="arc3,rad=0.28",
        arrowstyle="-|>",
        mutation_scale=18,
        linewidth=2.1,
        color="#b00020",
        shrinkA=13,
        shrinkB=13,
        zorder=5,
    )
    ax.add_patch(shortcut_arrow)
    ax.text(0.02, 0.24, r"directed shortcut", ha="center", va="bottom", color="#b00020", fontsize=10)
    ax.text(0.02, 0.13, r"$P(u\to v)=\beta(1-q)$", ha="center", va="top", color="#b00020", fontsize=10)
    ax.text(
        -0.05,
        -0.18,
        r"$|u-v|=50=N/2$",
        ha="center",
        va="center",
        color="#b00020",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.8),
    )

    for paper_idx, label, offset in [
        (1, "1", (0.10, 0.08)),
        (sc_src_paper, "u=6", (0.10, 0.09)),
        (sc_dst_paper, "v=56 / target", (-0.44, -0.02)),
    ]:
        px, py = xy(paper_idx)
        ax.text(px + offset[0], py + offset[1], label, fontsize=9, weight="bold")

    ax.set_title("N=100, K=2 ring with fixed shortcut u=6 -> v=56", fontsize=12)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_xlim(-1.22, 1.22)
    ax.set_ylim(-1.22, 1.22)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.04), ncol=3, frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def plot_annotated_double_peak(
    metrics: list[dict[str, object]],
    curves: list[dict[str, object]],
    *,
    n0_paper: int,
    beta: float,
    outpath: Path,
) -> None:
    case_rows = [
        r
        for r in metrics
        if int(r["n0_paper"]) == int(n0_paper) and abs(float(r["beta"]) - float(beta)) <= 1e-12
    ]
    if not case_rows:
        return
    case = case_rows[0]
    curve = sorted(
        [
            r
            for r in curves
            if int(r["n0_paper"]) == int(n0_paper) and abs(float(r["beta"]) - float(beta)) <= 1e-12
        ],
        key=lambda r: int(r["t"]),
    )
    if not curve:
        return

    t = np.asarray([int(r["t"]) for r in curve], dtype=int)
    f = np.asarray([float(r["f_t"]) for r in curve], dtype=float)
    tmax_plot = min(1800, int(t.max()))
    keep = t <= tmax_plot

    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=180)
    ax.plot(t[keep], f[keep], color="#264653", linewidth=1.4)
    markers = [
        ("first peak", int(case["t1"]), float(case["h1"]), "#2a9d8f", (8, 14)),
        ("valley", int(case["tv"]), float(case["hv"]), "#6c757d", (8, -32)),
        ("second peak", int(case["t2"]), float(case["h2"]), "#e76f51", (24, -36)),
    ]
    for label, tt, hh, color, offset in markers:
        ax.scatter([tt], [hh], s=48, color=color, edgecolor="white", linewidth=0.7, zorder=4)
        ax.axvline(tt, color=color, linewidth=0.9, linestyle="--", alpha=0.65)
        ax.annotate(
            f"{label}\n$t={tt}$",
            xy=(tt, hh),
            xytext=offset,
            textcoords="offset points",
            fontsize=8,
            color=color,
            arrowprops=dict(arrowstyle="->", color=color, lw=0.8),
        )

    beta_c = float(case["luca_beta_c"])
    visual_rho = valley_over_min_peak(case)
    r3_status = "yes" if visual_rho <= 0.8 else "no"
    ax.text(
        0.98,
        0.96,
        rf"$n_0={n0_paper}$, $\beta={beta:.3f}$, $\beta_c={beta_c:.3f}$" "\n"
        rf"$h_2/h_1={float(case['h2_over_h1']):.2f}$, "
        rf"$\rho=h_v/\min(h_1,h_2)={visual_rho:.2f}$" "\n"
        rf"R3 satisfied: {r3_status}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="#cccccc", alpha=0.92),
    )
    ax.set_xlabel("first-passage time $t$")
    ax.set_ylabel(r"$f(t)$")
    ax.set_title("Annotated double peak for the reference case")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.set_xlim(1, tmax_plot)
    ax.set_ylim(bottom=0.0)
    fig.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)


def write_tex_summary(rows: list[dict[str, object]], outpath: Path) -> None:
    lines = [
        r"\begin{tabular}{rrrrrr}",
        r"\toprule",
        r"$n_0$ & target & $\beta_c$ & any double & max $\beta$ double & double at/above $\beta_c$ \\",
        r"\midrule",
    ]
    for row in rows:
        any_flag = "yes" if bool(row["any_clear_double_peak"]) else "no"
        max_beta_val = float(row["max_beta_clear_double_peak"])
        max_beta = "--" if math.isnan(max_beta_val) else f"{max_beta_val:.3f}"
        lines.append(
            f"{int(row['n0_paper'])} & {int(row['target_paper'])} & "
            f"{float(row['luca_beta_c']):.3f} & {any_flag} & {max_beta} & "
            f"{int(row['clear_at_or_above_luca_count'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    outpath.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--N", type=int, default=100)
    parser.add_argument("--K", type=int, default=2)
    parser.add_argument("--q", type=float, default=2.0 / 3.0)
    parser.add_argument("--rho", type=float, default=1.0)
    parser.add_argument("--n0-values", type=str, default="1,2,3,4,5,6")
    parser.add_argument("--target-paper", type=int, default=None)
    parser.add_argument("--sc-src-paper", type=int, default=6)
    parser.add_argument("--sc-dst-paper", type=int, default=56)
    parser.add_argument("--betas", type=str, default=None, help="Comma-separated beta list; default is a refined 0..beta-max grid.")
    parser.add_argument("--beta-max", type=float, default=0.08)
    parser.add_argument("--beta-step", type=float, default=0.002)
    parser.add_argument("--selected-betas", type=str, default="0,0.01,0.04,0.06")
    parser.add_argument("--tmax", type=int, default=12000)
    parser.add_argument("--survival-eps", type=float, default=1e-13)
    parser.add_argument("--hmin", type=float, default=1e-12)
    parser.add_argument("--second-rel-height", type=float, default=0.01)
    parser.add_argument("--min-peak-separation", type=int, default=10)
    parser.add_argument("--max-valley-ratio", type=float, default=0.9)
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parents[1] / "artifacts")
    args = parser.parse_args()

    if args.K != 2:
        raise ValueError("This Luca sweep is defined for K=2.")
    if not (0.0 < args.q < 1.0):
        raise ValueError("q must be in (0,1).")

    outdir = args.outdir.resolve()
    data_dir = outdir / "data"
    figures_dir = outdir / "figures"
    tables_dir = outdir / "tables"
    for d in (data_dir, figures_dir, tables_dir):
        d.mkdir(parents=True, exist_ok=True)

    target_paper = int(args.target_paper) if args.target_paper is not None else int(args.sc_dst_paper)
    beta_c = 2.0 * float(args.q) / ((1.0 - float(args.q)) * float(args.N))
    n0_values = parse_int_list(args.n0_values) or [1, 2, 3, 4, 5, 6]
    betas = parse_float_list(args.betas)
    if betas is None:
        betas = default_beta_grid(args.beta_max, args.beta_step, beta_c)
    selected_betas = set(parse_float_list(args.selected_betas) or [])
    selected_betas.add(round(beta_c, 10))

    rows, selected_curve_rows = compute_rows(
        N=args.N,
        K=args.K,
        q=args.q,
        rho=args.rho,
        n0_values=n0_values,
        target_paper=target_paper,
        sc_src_paper=args.sc_src_paper,
        sc_dst_paper=args.sc_dst_paper,
        betas=betas,
        tmax=args.tmax,
        survival_eps=args.survival_eps,
        hmin=args.hmin,
        second_rel_height=args.second_rel_height,
        min_peak_separation=args.min_peak_separation,
        max_valley_ratio=args.max_valley_ratio,
        selected_betas=selected_betas,
    )

    metrics = sorted(rows, key=lambda r: (int(r["n0_paper"]), float(r["beta"])))
    summary = transition_summary(metrics)
    curves = sorted(selected_curve_rows, key=lambda r: (int(r["n0_paper"]), float(r["beta"]), int(r["t"])))

    metrics_path = data_dir / "luca_k2_fixed_shortcut_metrics.csv"
    summary_path = data_dir / "luca_k2_fixed_shortcut_summary.csv"
    criteria_path = data_dir / "luca_k2_fixed_shortcut_definition_comparison.csv"
    curves_path = data_dir / "luca_k2_fixed_shortcut_selected_curves.csv"
    config_path = data_dir / "luca_k2_fixed_shortcut_config.json"
    tex_path = tables_dir / "luca_k2_fixed_shortcut_summary.tex"
    criteria_tex_path = tables_dir / "luca_k2_fixed_shortcut_definition_comparison.tex"

    write_dict_csv(metrics_path, metrics)
    write_dict_csv(summary_path, summary)
    criteria = definition_comparison(metrics)
    write_dict_csv(criteria_path, criteria)
    write_selected_curves(curves_path, curves)
    write_tex_summary(summary, tex_path)
    write_definition_comparison_tex(criteria, criteria_tex_path)

    config = {
        "description": "Luca K=2 fixed one-way shortcut beta/n0 sweep.",
        "model": "lazy ring, nearest-neighbour only, one-way shortcut from self-loop mass",
        "N": int(args.N),
        "K": int(args.K),
        "q": float(args.q),
        "rho": float(args.rho),
        "n0_values_paper": n0_values,
        "target_paper": target_paper,
        "sc_src_paper": int(args.sc_src_paper),
        "sc_dst_paper": int(args.sc_dst_paper),
        "shortcut_rule": "P(u->v)=beta*(1-q), P(u->u)=(1-beta)*(1-q)",
        "luca_beta_c": beta_c,
        "betas": betas,
        "selected_betas": sorted(selected_betas),
        "tmax": int(args.tmax),
        "survival_eps": float(args.survival_eps),
        "bimodality": {
            "hmin": float(args.hmin),
            "second_rel_height": float(args.second_rel_height),
            "min_peak_separation": int(args.min_peak_separation),
            "max_valley_ratio": float(args.max_valley_ratio),
        },
        "outputs": {
            "metrics_csv": str(metrics_path.relative_to(outdir.parents[0])),
            "summary_csv": str(summary_path.relative_to(outdir.parents[0])),
            "definition_comparison_csv": str(criteria_path.relative_to(outdir.parents[0])),
            "selected_curves_csv": str(curves_path.relative_to(outdir.parents[0])),
            "summary_tex": str(tex_path.relative_to(outdir.parents[0])),
            "definition_comparison_tex": str(criteria_tex_path.relative_to(outdir.parents[0])),
        },
    }
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    plot_double_peak_map(metrics, figures_dir / "luca_k2_fixed_shortcut_double_peak_map.pdf")
    plot_peak_times(metrics, figures_dir / "luca_k2_fixed_shortcut_peak_times.pdf")
    plot_ring_geometry(
        N=args.N,
        n0_values=n0_values,
        sc_src_paper=args.sc_src_paper,
        sc_dst_paper=args.sc_dst_paper,
        target_paper=target_paper,
        outpath=figures_dir / "luca_k2_fixed_shortcut_ring_geometry.pdf",
    )
    if curves:
        plot_representative_curves(curves, figures_dir / "luca_k2_fixed_shortcut_representative_fpt.pdf")
        plot_annotated_double_peak(
            metrics,
            curves,
            n0_paper=1,
            beta=0.01,
            outpath=figures_dir / "luca_k2_fixed_shortcut_annotated_double_peak.pdf",
        )

    print(f"Wrote {metrics_path}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {curves_path}")
    print(f"Wrote {config_path}")
    print(f"Wrote {tex_path}")


if __name__ == "__main__":
    main()
