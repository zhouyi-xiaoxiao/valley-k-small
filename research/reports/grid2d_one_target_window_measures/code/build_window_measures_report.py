#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "packages" / "vkcore" / "src"
SOURCE_REPORT_CODE = REPO_ROOT / "research" / "reports" / "grid2d_one_two_target_gating" / "code"
REPORT_ROOT = Path(__file__).resolve().parents[1]
FIG_ROOT = REPORT_ROOT / "artifacts" / "figures"
DATA_ROOT = REPORT_ROOT / "artifacts" / "data"
TABLE_ROOT = REPORT_ROOT / "artifacts" / "tables"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SOURCE_REPORT_CODE) not in sys.path:
    sys.path.insert(0, str(SOURCE_REPORT_CODE))

import one_target_mechanism_region_figures as mech


WINDOW_ORDER = ["peak1", "valley", "peak2"]
REGION_ORDER = ["target_funnel", "outer_reservoir", "left_outer", "left_shoulders", "left_core"]
REGION_LABELS = {name: mech.REGION_LABELS[name] for name in REGION_ORDER}
CASE_TITLE = "One-target corridor-only soft-bias variant"
WINDOW_MEASURE_CSV = DATA_ROOT / "window_measure_comparison.csv"
WINDOW_MEASURE_JSON = DATA_ROOT / "window_measure_comparison.json"
WINDOW_MEASURE_TEX = TABLE_ROOT / "window_measure_comparison.tex"
WINDOW_MEASURE_PNG = FIG_ROOT / "window_measure_comparison.png"
WINDOW_MEASURE_PDF = FIG_ROOT / "window_measure_comparison.pdf"
PROFILE_BAR_PNG = FIG_ROOT / "window_measure_bar_profiles.png"
PROFILE_BAR_PDF = FIG_ROOT / "window_measure_bar_profiles.pdf"
EVER_VISIT_BIMODAL_PNG = FIG_ROOT / "one_target_ever_visit_non_corridor.png"
EVER_VISIT_BIMODAL_PDF = FIG_ROOT / "one_target_ever_visit_non_corridor.pdf"
PROFILE_SIMILARITY_CSV = DATA_ROOT / "window_profile_similarity.csv"
PROFILE_SIMILARITY_TEX = TABLE_ROOT / "window_profile_similarity.tex"
PARTITION_PNG = FIG_ROOT / "one_target_partition.png"
PARTITION_PDF = FIG_ROOT / "one_target_partition.pdf"
BIMODAL_PNG = FIG_ROOT / "one_target_bimodal_non_corridor.png"
BIMODAL_PDF = FIG_ROOT / "one_target_bimodal_non_corridor.pdf"
SOURCE_COPY_CSV = DATA_ROOT / "source_window_region_summary.csv"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def copy_file(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)


def load_occupancy_summary(path: Path) -> dict[str, dict[str, float]]:
    rows = list(csv.DictReader(path.open("r", encoding="utf-8", newline="")))
    out: dict[str, dict[str, float]] = {window: {} for window in WINDOW_ORDER}
    for row in rows:
        window = str(row["window"])
        region = str(row["region"])
        if window not in out:
            continue
        out[window][region] = float(row["occupancy_share"])
    return out


def compute_exact_ever_visit_summary(
    case: dict[str, Any],
    *,
    masks: dict[str, np.ndarray],
    windows: list[tuple[str, int, int]],
    region_names: list[str],
) -> dict[str, dict[str, float]]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    n_states = lx * wy
    target = case["target"]
    start = case["start"]
    start_idx = int(start[1]) * lx + int(start[0])
    target_idx = int(target[1]) * lx + int(target[0])

    src_idx = np.asarray(case["src_idx"], dtype=np.int64)
    dst_idx = np.asarray(case["dst_idx"], dtype=np.int64)
    probs = np.asarray(case["probs"], dtype=np.float64)
    hit_mask = dst_idx == target_idx
    nonhit_mask = ~hit_mask
    src_nonhit = src_idx[nonhit_mask]
    dst_nonhit = dst_idx[nonhit_mask]
    probs_nonhit = probs[nonhit_mask]
    src_hit = src_idx[hit_mask]
    probs_hit = probs[hit_mask]

    max_hi = max(int(hi) for _, _, hi in windows)
    hit_grid = np.zeros((max_hi + 1, len(region_names)), dtype=np.float64)

    for r_idx, region_name in enumerate(region_names):
        region_mask = masks[region_name].reshape(n_states)
        p = np.zeros((2, n_states), dtype=np.float64)
        p[int(region_mask[start_idx]), start_idx] = 1.0
        hit_by_t = np.zeros((max_hi + 1, 2), dtype=np.float64)
        for t in range(max_hi):
            hit_by_t[t + 1, 0] = float(np.sum(p[0, src_hit] * probs_hit))
            hit_by_t[t + 1, 1] = float(np.sum(p[1, src_hit] * probs_hit))
            p_next = np.zeros_like(p)
            w0 = p[0, src_nonhit] * probs_nonhit
            enters = region_mask[dst_nonhit]
            np.add.at(p_next[1], dst_nonhit[enters], w0[enters])
            np.add.at(p_next[0], dst_nonhit[~enters], w0[~enters])
            w1 = p[1, src_nonhit] * probs_nonhit
            np.add.at(p_next[1], dst_nonhit, w1)
            p = p_next
        hit_grid[:, r_idx] = hit_by_t[:, 1]

    out: dict[str, dict[str, float]] = {window: {} for window, _, _ in windows}
    for window_name, lo, hi in windows:
        total_hit = float(np.sum(case["f_total"][int(lo) : int(hi) + 1]))
        for r_idx, region_name in enumerate(region_names):
            out[window_name][region_name] = float(np.sum(hit_grid[int(lo) : int(hi) + 1, r_idx]) / total_hit)
    return out


def compute_normalized_visit_profile(
    ever_visit_summary: dict[str, dict[str, float]],
    *,
    region_order: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    raw = np.asarray(
        [[ever_visit_summary[window].get(region, 0.0) for region in region_order] for window in WINDOW_ORDER],
        dtype=np.float64,
    )
    totals = np.sum(raw, axis=1)
    normalized = np.divide(
        raw,
        totals[:, None],
        out=np.zeros_like(raw),
        where=totals[:, None] > 0.0,
    )
    return raw, totals, normalized


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denom = float(np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom <= 0.0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


def compute_profile_similarity_rows(
    *,
    occupancy_profile: np.ndarray,
    visit_profile: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, window_name in enumerate(WINDOW_ORDER):
        occ = occupancy_profile[idx]
        vis = visit_profile[idx]
        rows.append(
            {
                "window": window_name,
                "cosine_similarity": _cosine_similarity(occ, vis),
                "total_variation_distance": 0.5 * float(np.sum(np.abs(occ - vis))),
            }
        )
    return rows


def write_profile_similarity_table(rows: list[dict[str, Any]]) -> None:
    write_csv(
        PROFILE_SIMILARITY_CSV,
        rows,
        ["window", "cosine_similarity", "total_variation_distance"],
    )
    lines = [
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r"Window & Cosine similarity & Total variation distance \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['window']} & {float(row['cosine_similarity']):.4f} & {float(row['total_variation_distance']):.4f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    ensure_dir(TABLE_ROOT)
    PROFILE_SIMILARITY_TEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_window_measure_comparison(
    *,
    occupancy_summary: dict[str, dict[str, float]],
    ever_visit_summary: dict[str, dict[str, float]],
) -> None:
    occ_mat = np.asarray(
        [[occupancy_summary[window].get(region, 0.0) for window in WINDOW_ORDER] for region in REGION_ORDER],
        dtype=np.float64,
    )
    visit_mat = np.asarray(
        [[ever_visit_summary[window].get(region, 0.0) for window in WINDOW_ORDER] for region in REGION_ORDER],
        dtype=np.float64,
    )

    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.7), sharey=True)
    configs = [
        (axes[0], occ_mat, "Occupancy share", "time-weighted window occupancy", 0.0, float(max(0.36, np.max(occ_mat)))),
        (axes[1], visit_mat, "Ever-visit probability", "pathwise visit event before hit", 0.0, 1.0),
    ]
    for ax, mat, title, cbar_label, vmin, vmax in configs:
        im = ax.imshow(mat, origin="upper", aspect="auto", cmap="YlGnBu", vmin=vmin, vmax=vmax)
        ax.set_xticks(np.arange(len(WINDOW_ORDER)))
        ax.set_xticklabels(WINDOW_ORDER)
        ax.set_yticks(np.arange(len(REGION_ORDER)))
        ax.set_yticklabels([REGION_LABELS[r] for r in REGION_ORDER])
        ax.set_title(title, fontsize=11)
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                val = float(mat[i, j])
                ax.text(
                    j,
                    i,
                    f"{100.0 * val:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if val > 0.18 else "#111111",
                    fontweight="bold" if val > 0.08 else None,
                )
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label(cbar_label)
    fig.suptitle("Window-conditioned measures are not the same observable", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    ensure_dir(FIG_ROOT)
    fig.savefig(WINDOW_MEASURE_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(WINDOW_MEASURE_PDF, bbox_inches="tight")
    plt.close(fig)


def plot_single_measure_bimodal_distribution(
    *,
    case: dict[str, Any],
    windows: list[tuple[str, int, int]],
    profile: np.ndarray,
    region_order: list[str],
    value_labels: dict[str, str] | None,
    figure_title: str,
    right_title: str,
    right_ylabel: str,
    output_png: Path,
    output_pdf: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), gridspec_kw={"width_ratios": [1.15, 1.0]})
    ax_curve, ax_bar = axes

    f_total = np.asarray(case["f_total"], dtype=np.float64)
    t = np.arange(f_total.size, dtype=np.int64)
    ax_curve.plot(t, f_total, color="#111111", lw=1.9)

    top_labels = {
        "peak1": f"t1={int(case['res'].t_peak1)}",
        "valley": f"t_v={int(case['res'].t_valley)}",
        "peak2": f"t2={int(case['res'].t_peak2)}",
    }
    window_note_labels = {
        window_name: f"{window_name}\n[{int(lo)},{int(hi)}]"
        for window_name, lo, hi in windows
    }
    mech.draw_window_composition_bars(
        ax_curve,
        windows=windows,
        proportions=profile,
        region_order=region_order,
        value_labels=value_labels,
        window_note_labels=window_note_labels,
        top_labels=top_labels,
        top_label_y=1.006,
        note_y_cycle=(0.78, 0.55),
    )

    ax_curve.set_xlim(0, min(int(f_total.size - 1), 2300))
    ax_curve.set_ylim(0.0, 1.15 * float(np.max(f_total)))
    ax_curve.set_xlabel("t")
    ax_curve.set_ylabel("first-passage pmf")
    ax_curve.grid(alpha=0.24)

    x = np.arange(len(WINDOW_ORDER), dtype=np.float64)
    bottom = np.zeros(len(WINDOW_ORDER), dtype=np.float64)
    for region_idx, region in enumerate(region_order):
        vals = profile[:, region_idx]
        bars = ax_bar.bar(
            x,
            vals,
            bottom=bottom,
            width=0.66,
            color=mech.REGION_COLORS[region],
            edgecolor="white",
            linewidth=0.8,
            label=REGION_LABELS[region],
        )
        for i, (bar, val) in enumerate(zip(bars, vals, strict=False)):
            if val < 0.07:
                continue
            ax_bar.text(
                bar.get_x() + bar.get_width() / 2.0,
                bottom[i] + 0.5 * val,
                f"{100.0 * val:.1f}%",
                ha="center",
                va="center",
                fontsize=7.6,
                color="white",
                fontweight="bold",
            )
        bottom += vals

    ax_bar.set_xticks(x, WINDOW_ORDER)
    ax_bar.set_ylim(0.0, 1.0)
    ax_bar.set_ylabel(right_ylabel)
    ax_bar.set_title(right_title, fontsize=11, pad=10)
    ax_bar.grid(axis="y", alpha=0.24)
    ax_bar.set_axisbelow(True)
    if value_labels is not None:
        for idx, window_name in enumerate(WINDOW_ORDER):
            ax_bar.text(
                x[idx],
                0.992,
                value_labels[window_name],
                ha="center",
                va="top",
                fontsize=8.0,
                color="#444444",
            )

    handles = [Patch(facecolor=mech.REGION_COLORS[r], edgecolor="none", label=REGION_LABELS[r]) for r in region_order]
    fig.legend(handles, [REGION_LABELS[r] for r in region_order], loc="upper center", bbox_to_anchor=(0.5, 0.97), ncol=3, frameon=False, fontsize=8.2)
    fig.suptitle(figure_title, fontsize=12, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    ensure_dir(FIG_ROOT)
    fig.savefig(output_png, dpi=180, bbox_inches="tight")
    fig.savefig(output_pdf, bbox_inches="tight")
    plt.close(fig)


def plot_window_measure_profiles(
    *,
    case: dict[str, Any],
    windows: list[tuple[str, int, int]],
    occupancy_profile: np.ndarray,
    non_corridor_mass: np.ndarray,
    visit_profile: np.ndarray,
) -> None:
    f_total = np.asarray(case["f_total"], dtype=np.float64)
    t = np.arange(f_total.size, dtype=np.int64)
    x_max = min(int(f_total.size - 1), 2300)
    y_max = 1.15 * float(np.max(f_total))
    top_labels = {
        "peak1": f"t1={int(case['res'].t_peak1)}",
        "valley": f"t_v={int(case['res'].t_valley)}",
        "peak2": f"t2={int(case['res'].t_peak2)}",
    }
    window_note_labels = {
        window_name: f"{window_name}\n[{int(lo)},{int(hi)}]"
        for window_name, lo, hi in windows
    }

    fig, axes = plt.subplots(2, 1, figsize=(10.2, 7.2), dpi=180, sharex=True)
    panel_configs = [
        (
            axes[0],
            occupancy_profile,
            {window: f"remaining={100.0 * non_corridor_mass[idx]:.1f}%" for idx, window in enumerate(WINDOW_ORDER)},
            "(a) Occupancy profile",
        ),
        (
            axes[1],
            visit_profile,
            None,
            "(b) Ever-visit profile (renorm.)",
        ),
    ]

    for ax, profile, value_labels, title in panel_configs:
        ax.plot(t, f_total, color="#111111", lw=1.85, zorder=6)
        mech.draw_window_composition_bars(
            ax,
            windows=windows,
            proportions=profile,
            region_order=REGION_ORDER,
            value_labels=value_labels,
            window_note_labels=window_note_labels,
            top_labels=top_labels,
            top_label_y=1.004,
            note_y_cycle=(0.77, 0.55),
        )
        ax.set_xlim(0, x_max)
        ax.set_ylim(0.0, y_max)
        ax.set_ylabel("first-passage pmf")
        ax.grid(alpha=0.24)
        ax.set_axisbelow(True)
        ax.text(
            0.015,
            0.965,
            title,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=9.1,
            color="#111111",
            bbox=dict(facecolor="white", alpha=0.82, edgecolor="none", pad=1.0),
        )

    axes[-1].set_xlabel("t")
    handles = [Patch(facecolor=mech.REGION_COLORS[r], edgecolor="none", label=REGION_LABELS[r]) for r in REGION_ORDER]
    fig.legend(handles, [REGION_LABELS[r] for r in REGION_ORDER], loc="upper center", bbox_to_anchor=(0.5, 0.992), ncol=3, frameon=False, fontsize=8.4)
    fig.suptitle("One-target window bars in the same ring-style layout", fontsize=12, y=0.997)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
    ensure_dir(FIG_ROOT)
    fig.savefig(PROFILE_BAR_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(PROFILE_BAR_PDF, bbox_inches="tight")
    plt.close(fig)


def write_measure_table(
    *,
    occupancy_summary: dict[str, dict[str, float]],
    ever_visit_summary: dict[str, dict[str, float]],
) -> None:
    lines = [
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r"Region & Occ. p1 & Visit p1 & Occ. valley & Visit valley & Occ. p2 & Visit p2 \\",
        r"\midrule",
    ]
    for region_name in REGION_ORDER:
        vals = []
        for window in WINDOW_ORDER:
            vals.append(f"{100.0 * occupancy_summary[window].get(region_name, 0.0):.1f}\\%")
            vals.append(f"{100.0 * ever_visit_summary[window].get(region_name, 0.0):.1f}\\%")
        line = REGION_LABELS[region_name] + " & " + " & ".join(vals) + r" \\"
        lines.append(line)
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    ensure_dir(TABLE_ROOT)
    WINDOW_MEASURE_TEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    base_outputs = mech.run_scan_and_plot()
    copy_file(Path(base_outputs["schematic_png"]), PARTITION_PNG)
    copy_file(Path(base_outputs["schematic_pdf"]), PARTITION_PDF)
    copy_file(Path(base_outputs["bimodal_png"]), BIMODAL_PNG)
    copy_file(Path(base_outputs["bimodal_pdf"]), BIMODAL_PDF)
    copy_file(Path(base_outputs["summary"]), SOURCE_COPY_CSV)

    case = mech.build_case()
    masks = mech.region_masks(case)
    windows = mech.windows_payload(case)
    occupancy_summary = load_occupancy_summary(Path(base_outputs["summary"]))
    _occupancy_raw, non_corridor_mass, occupancy_profile = mech.compute_conditional_profile(
        occupancy_summary,
        region_order=REGION_ORDER,
    )
    ever_visit_summary = compute_exact_ever_visit_summary(
        case,
        masks=masks,
        windows=windows,
        region_names=REGION_ORDER,
    )
    _visit_raw, visit_totals, visit_profile = compute_normalized_visit_profile(
        ever_visit_summary,
        region_order=REGION_ORDER,
    )
    profile_similarity_rows = compute_profile_similarity_rows(
        occupancy_profile=occupancy_profile,
        visit_profile=visit_profile,
    )

    rows: list[dict[str, Any]] = []
    for window in WINDOW_ORDER:
        for region in REGION_ORDER:
            rows.append(
                {
                    "window": window,
                    "region": region,
                    "region_label": REGION_LABELS[region],
                    "occupancy_share": float(occupancy_summary[window].get(region, 0.0)),
                    "ever_visit_probability": float(ever_visit_summary[window].get(region, 0.0)),
                }
            )

    write_csv(
        WINDOW_MEASURE_CSV,
        rows,
        ["window", "region", "region_label", "occupancy_share", "ever_visit_probability"],
    )
    write_json(
        WINDOW_MEASURE_JSON,
        {
            "window_order": WINDOW_ORDER,
            "region_order": REGION_ORDER,
            "rows": rows,
        },
    )
    plot_window_measure_comparison(
        occupancy_summary=occupancy_summary,
        ever_visit_summary=ever_visit_summary,
    )
    plot_single_measure_bimodal_distribution(
        case=case,
        windows=windows,
        profile=visit_profile,
        region_order=REGION_ORDER,
        value_labels=None,
        figure_title=f"{CASE_TITLE}: renormalized ever-visit mechanism-region distribution",
        right_title="Renormalized ever-visit composition",
        right_ylabel="share within renorm. visit profile",
        output_png=EVER_VISIT_BIMODAL_PNG,
        output_pdf=EVER_VISIT_BIMODAL_PDF,
    )
    plot_window_measure_profiles(
        case=case,
        windows=windows,
        occupancy_profile=occupancy_profile,
        non_corridor_mass=non_corridor_mass,
        visit_profile=visit_profile,
    )
    write_measure_table(
        occupancy_summary=occupancy_summary,
        ever_visit_summary=ever_visit_summary,
    )
    write_profile_similarity_table(profile_similarity_rows)
    write_json(
        DATA_ROOT / "window_profile_similarity.json",
        {
            "window_order": WINDOW_ORDER,
            "region_order": REGION_ORDER,
            "visit_profile_normalization": {
                "raw_overlap_sums": {
                    window: float(visit_totals[idx])
                    for idx, window in enumerate(WINDOW_ORDER)
                }
            },
            "rows": profile_similarity_rows,
        },
    )

    for path in [
        PARTITION_PNG,
        PARTITION_PDF,
        BIMODAL_PNG,
        BIMODAL_PDF,
        EVER_VISIT_BIMODAL_PNG,
        EVER_VISIT_BIMODAL_PDF,
        PROFILE_BAR_PNG,
        PROFILE_BAR_PDF,
        WINDOW_MEASURE_PNG,
        WINDOW_MEASURE_PDF,
        WINDOW_MEASURE_CSV,
        WINDOW_MEASURE_JSON,
        WINDOW_MEASURE_TEX,
        PROFILE_SIMILARITY_CSV,
        PROFILE_SIMILARITY_TEX,
        SOURCE_COPY_CSV,
    ]:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
