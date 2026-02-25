#!/usr/bin/env python3
"""Plot figures and tables for Luca regime map study."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[3]
TT_CODE = ROOT / "reports" / "2d_two_target_double_peak" / "code"

sys.path.insert(0, str(TT_CODE))

from two_target_2d_report import ExternalCaseSpec, _draw_external_config_panel  # noqa: E402

DEFECT_BINS = ["[0,20]", "[21,60]", "[61,120]", "[121,300]", "[301,700]", "[701,+inf)"]


def _load_runtime_raw(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for r in rd:
            rows.append(
                {
                    "workload_id": r["workload_id"],
                    "family": r["family"],
                    "geometry_id": r["geometry_id"],
                    "geometry_kind": r["geometry_kind"],
                    "t_max": int(r["t_max"]),
                    "defect_pairs": int(r["defect_pairs"]),
                    "local_bias_sites": int(r["local_bias_sites"]),
                    "defect_bin": r["defect_bin"],
                    "sparse_seconds": float(r["sparse_seconds"]),
                    "luca_seconds": float(r["luca_seconds"]),
                    "linear_mfpt_seconds": float(r["linear_mfpt_seconds"]),
                    "luca_mode": r["luca_mode"],
                    "speedup_sparse_over_luca": float(r["speedup_sparse_over_luca"]),
                    "winner_fullfpt": r["winner_fullfpt"],
                    "l1_error": None if r["l1_error"] in {"", "None"} else float(r["l1_error"]),
                    "linf_error": None if r["linf_error"] in {"", "None"} else float(r["linf_error"]),
                }
            )
    return rows


def _load_summary(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_manifest_map(path: Path) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        for r in rd:
            out[r["workload_id"]] = {
                "family": r["family"],
                "config_json": r["config_json"],
                "geometry_kind": r["geometry_kind"],
            }
    return out


def _winner_heatmap(rows: List[Dict[str, Any]], *, family: str, out_path: Path) -> None:
    fr = [r for r in rows if r["family"] == family]
    t_vals = sorted({int(r["t_max"]) for r in fr})
    y_labels = list(DEFECT_BINS)
    Z = -np.ones((len(y_labels), len(t_vals)), dtype=np.int64)
    Txt = [["" for _ in t_vals] for __ in y_labels]

    for i, b in enumerate(y_labels):
        for j, t in enumerate(t_vals):
            cell = [r for r in fr if r["defect_bin"] == b and int(r["t_max"]) == t]
            if not cell:
                continue
            p = float(np.mean([float(r["speedup_sparse_over_luca"]) > 1.0 for r in cell]))
            # 0=sparse wins/majority, 1=luca wins/majority
            Z[i, j] = 1 if p > 0.5 else 0
            Txt[i][j] = f"n={len(cell)}\np={p:.2f}"

    cmap = ListedColormap(["#8fb8de", "#e8a5a0", "#f0f0f0"])
    Z_plot = Z.copy()
    Z_plot[Z_plot < 0] = 2

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    im = ax.imshow(Z_plot, origin="lower", cmap=cmap, vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(range(len(t_vals)))
    ax.set_xticklabels([str(t) for t in t_vals])
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("T (fixed full-FPT horizon)")
    ax.set_ylabel("defect_pairs bin")
    ax.set_title(f"Winner Heatmap ({family}): sparse vs Luca")

    for i in range(len(y_labels)):
        for j in range(len(t_vals)):
            if Txt[i][j]:
                ax.text(j, i, Txt[i][j], ha="center", va="center", fontsize=8)

    legend_handles = [
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor="#8fb8de", markersize=10, label="Sparse wins/majority"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor="#e8a5a0", markersize=10, label="Luca wins/majority"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor="#f0f0f0", markersize=10, label="No samples"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", frameon=True, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _speedup_scatter(rows: List[Dict[str, Any]], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    family_color = {"two_target": "#1f77b4", "reflecting": "#d62728"}
    mode_marker = {"full": "o", "estimate": "^"}

    for fam in ("two_target", "reflecting"):
        fam_rows = [r for r in rows if r["family"] == fam]
        for mode in ("full", "estimate"):
            sub = [r for r in fam_rows if r["luca_mode"] == mode]
            if not sub:
                continue
            x = np.array([float(r["defect_pairs"]) for r in sub], dtype=np.float64)
            y = np.array([float(r["speedup_sparse_over_luca"]) for r in sub], dtype=np.float64)
            ax.scatter(
                x,
                y,
                s=26,
                alpha=0.78,
                c=family_color[fam],
                marker=mode_marker[mode],
                label=f"{fam}-{mode}",
            )

    ax.axhline(1.0, color="#333333", lw=1.2, ls="--")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("defect_pairs")
    ax.set_ylabel("R = sparse_seconds / luca_seconds")
    ax.set_title("Speedup Scatter Across All Workloads")
    ax.grid(alpha=0.25, which="both")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _speedup_box_by_t(rows: List[Dict[str, Any]], out_path: Path) -> None:
    t_vals = sorted({int(r["t_max"]) for r in rows})
    data = []
    labels = []
    for t in t_vals:
        vals = [float(r["speedup_sparse_over_luca"]) for r in rows if int(r["t_max"]) == t]
        if vals:
            data.append(vals)
            labels.append(str(t))

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.boxplot(data, tick_labels=labels, showfliers=True)
    ax.axhline(1.0, color="#333333", lw=1.2, ls="--")
    ax.set_yscale("log")
    ax.set_xlabel("T")
    ax.set_ylabel("R = sparse_seconds / luca_seconds")
    ax.set_title("Speedup Distribution by T")
    ax.grid(axis="y", alpha=0.25, which="both")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _estimation_error_anchor(summary: Dict[str, Any], out_path: Path) -> None:
    checks = summary.get("estimation_validation", {}).get("checks", [])
    if not checks:
        fig, ax = plt.subplots(figsize=(6.0, 3.6))
        ax.text(0.5, 0.5, "No estimation checks", ha="center", va="center")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(out_path)
        plt.close(fig)
        return

    xs = np.arange(len(checks))
    errs = np.array([float(c["relative_error"]) for c in checks], dtype=np.float64)
    fam = [str(c["family"]) for c in checks]
    colors = ["#1f77b4" if f == "two_target" else "#d62728" for f in fam]

    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    ax.bar(xs, errs, color=colors, alpha=0.85)
    ax.axhline(0.25, color="#333333", lw=1.2, ls="--", label="25% threshold")
    ax.set_xticks(xs)
    ax.set_xticklabels([str(c["workload_id"]) for c in checks], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Relative error |est-full|/full")
    ax.set_title("Estimation Error on Anchor Workloads")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _config_examples(rows: List[Dict[str, Any]], manifest_map: Dict[str, Dict[str, Any]], out_path: Path) -> None:
    # Representative low/medium/high defect examples from two_target at T=300.
    pool = [r for r in rows if r["family"] == "two_target" and int(r["t_max"]) == 300]
    if not pool:
        return

    targets = [2, 80, 600]
    chosen: List[Dict[str, Any]] = []
    used_ids = set()
    for t_def in targets:
        cand = sorted(pool, key=lambda r: (abs(int(r["defect_pairs"]) - t_def), int(r["defect_pairs"])))
        pick = None
        for c in cand:
            if c["workload_id"] not in used_ids:
                pick = c
                break
        if pick is not None:
            chosen.append(pick)
            used_ids.add(str(pick["workload_id"]))

    n = len(chosen)
    fig, axes = plt.subplots(1, n, figsize=(5.6 * n, 5.6))
    if n == 1:
        axes_arr = [axes]
    else:
        axes_arr = list(np.asarray(axes).reshape(-1))

    for ax, row in zip(axes_arr, chosen):
        cfg = json.loads(manifest_map[str(row["workload_id"])]["config_json"])
        N = int(cfg["N"])
        start = tuple(cfg["start_0_based"])
        m1 = tuple(cfg["m1_0_based"])
        m2 = tuple(cfg["m2_0_based"])
        local_bias_map = {(int(x), int(y)): (str(d), float(cfg["delta"])) for x, y, d in cfg["arrow_sites"]}

        spec = ExternalCaseSpec(
            case_id=str(row["geometry_id"]),
            name=f"defects={row['defect_pairs']}",
            type_name=str(row["geometry_kind"]),
            expected="regime example",
            note="",
            local_bias_map=local_bias_map,
            sticky_map={},
            barrier_map={},
            long_range_map={},
            global_bias=(0.0, 0.0),
        )
        _draw_external_config_panel(
            ax,
            N=N,
            start=start,
            m1=m1,
            m2=m2,
            spec=spec,
            title=f"{row['geometry_id']}\nM={row['defect_pairs']}, R={row['speedup_sparse_over_luca']:.3g}",
            show_legend=(ax is axes_arr[0]),
        )

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _write_table_summary_by_bin(summary: Dict[str, Any], out_path: Path) -> None:
    rows = summary.get("aggregates", {}).get("pooled_bin_t", [])
    lines = [
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "Defect bin & T & n & Median $R$ & Mean $R$ & $P(R>1)$ \\\\",
        "\\midrule",
    ]
    for r in rows:
        key = r.get("key", [])
        if len(key) != 3:
            continue
        _pooled, b, t = key
        b_tex = f"\\texttt{{{str(b)}}}"
        lines.append(
            f"{b_tex} & {int(t)} & {int(r['count'])} & {float(r['median_R']):.4f} & {float(r['mean_R']):.4f} & {float(r['p_luca_faster']):.3f} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_table_anchor_baselines(summary: Dict[str, Any], out_path: Path) -> None:
    rows = summary.get("anchor_baselines", [])
    lines = [
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        "Anchor & Defects & Sparse(s) & Dense(s) & Full AW(s) & Luca(s) & Linear(s) \\\\",
        "\\midrule",
    ]
    for r in rows:
        anchor = str(r["anchor_label"]).replace("_", "\\_")
        wid = str(r["workload_id"]).replace("_", "\\_")
        lines.append(
            f"{anchor} ({wid}) & {int(r['defect_pairs'])} & {float(r['sparse_seconds']):.4f} & {float(r['dense_seconds']):.4f} & {float(r['full_aw_seconds']):.4f} & {float(r['luca_seconds']):.4f} & {float(r['linear_seconds']):.4f} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Plot regime-map figures and export TeX tables.")
    p.add_argument(
        "--manifest",
        type=str,
        default=str(ROOT / "reports" / "luca_regime_map" / "data" / "manifest.csv"),
    )
    p.add_argument(
        "--runtime-raw",
        type=str,
        default=str(ROOT / "reports" / "luca_regime_map" / "data" / "runtime_raw.csv"),
    )
    p.add_argument(
        "--runtime-summary",
        type=str,
        default=str(ROOT / "reports" / "luca_regime_map" / "data" / "runtime_summary.json"),
    )
    p.add_argument(
        "--fig-dir",
        type=str,
        default=str(ROOT / "reports" / "luca_regime_map" / "figures"),
    )
    p.add_argument(
        "--table-dir",
        type=str,
        default=str(ROOT / "reports" / "luca_regime_map" / "tables"),
    )
    args = p.parse_args()

    manifest_path = Path(args.manifest)
    raw_path = Path(args.runtime_raw)
    summary_path = Path(args.runtime_summary)
    fig_dir = Path(args.fig_dir)
    tbl_dir = Path(args.table_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)
    tbl_dir.mkdir(parents=True, exist_ok=True)

    rows = _load_runtime_raw(raw_path)
    summary = _load_summary(summary_path)
    manifest_map = _load_manifest_map(manifest_path)

    _winner_heatmap(rows, family="two_target", out_path=fig_dir / "regime_winner_heatmap_two_target.pdf")
    _winner_heatmap(rows, family="reflecting", out_path=fig_dir / "regime_winner_heatmap_reflecting.pdf")
    _speedup_scatter(rows, out_path=fig_dir / "regime_speedup_scatter_all.pdf")
    _speedup_box_by_t(rows, out_path=fig_dir / "regime_speedup_box_by_T.pdf")
    _estimation_error_anchor(summary, out_path=fig_dir / "regime_estimation_error_anchor.pdf")
    _config_examples(rows, manifest_map, out_path=fig_dir / "regime_config_examples.pdf")

    _write_table_summary_by_bin(summary, out_path=tbl_dir / "regime_summary_by_bin.tex")
    _write_table_anchor_baselines(summary, out_path=tbl_dir / "regime_anchor_baselines.tex")

    print(
        json.dumps(
            {
                "figures": [
                    "regime_winner_heatmap_two_target.pdf",
                    "regime_winner_heatmap_reflecting.pdf",
                    "regime_speedup_scatter_all.pdf",
                    "regime_speedup_box_by_T.pdf",
                    "regime_estimation_error_anchor.pdf",
                    "regime_config_examples.pdf",
                ],
                "tables": ["regime_summary_by_bin.tex", "regime_anchor_baselines.tex"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
