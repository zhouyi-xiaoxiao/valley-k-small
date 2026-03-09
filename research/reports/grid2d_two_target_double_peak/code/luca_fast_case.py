#!/usr/bin/env python3
"""Construct and benchmark a case where Luca/Giuggioli defect-reduced AW is fastest."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from compare_numeric_methods import (
    build_transient_system,
    l1_and_max_abs,
    plot_fpt_overlay,
    plot_runtime_bar,
    run_aw_defect_giuggioli,
    run_aw_fft,
    run_dense_recursion,
    run_linear_mfpt,
    summarize_series,
)
from two_target_2d_report import (
    ExternalCaseSpec,
    build_transition_arrays,
    plot_external_case_detailed_config,
    run_exact_two_target,
)

Coord = Tuple[int, int]


def build_luca_fast_geometry(N: int) -> Tuple[Coord, Coord, Coord, Dict[Coord, str], float, float]:
    """A sparse-defect setup that favors Luca-style defect reduction."""
    if N < 21:
        raise ValueError("N must be >= 21 for the default geometry.")
    q = 0.2
    delta = 0.2
    start = (N // 2, N // 2)
    m1 = (N // 2 + 8, N // 2)
    m2 = (N // 2 - 8, N // 2 - 8)
    # Single local-bias site => very small defect dimension.
    arrow_map = {(start[0], start[1] - 1): "E"}
    return start, m1, m2, arrow_map, q, delta


def write_report_markdown(
    out_path: Path,
    *,
    payload: dict,
    json_rel: str,
    fig_cfg_rel: str,
    fig_fpt_rel: str,
    fig_runtime_rel: str,
) -> None:
    cfg = payload["config"]
    rt = payload["runtime_seconds"]
    err_dense = payload["error_dense_vs_sparse"]
    err_aw = payload["error_full_aw_vs_sparse_aw"]
    err_luca = payload["error_luca_vs_sparse_aw"]
    sparse = payload["sparse_exact"]
    sparse_aw = payload["sparse_exact_on_aw_horizon"]
    dense = payload["dense_recursion"]
    full_aw = payload["full_aw"]
    luca = payload["luca_defect_reduced"]
    linear = payload["linear_mfpt"]
    win = payload["winner"]

    lines = []
    lines.append("# Luca Fast Case (Constructed Benchmark)")
    lines.append("")
    lines.append("## 1. Goal")
    lines.append("Construct a reproducible setup where Luca/Giuggioli defect-reduced inversion is faster than all comparison methods in this benchmark file.")
    lines.append("")
    lines.append("## 2. Configuration")
    lines.append(f"- Grid: `N={cfg['N']}` (reflecting boundaries).")
    lines.append(f"- Start/targets (0-based): start={cfg['start_0_based']}, m1={cfg['m1_0_based']}, m2={cfg['m2_0_based']}.")
    lines.append(f"- Motion: `q={cfg['q']}`, local-bias `delta={cfg['delta']}`.")
    lines.append(f"- Local-bias sites: `{cfg['local_bias_sites']}` (single-site defect setup).")
    lines.append(f"- Time windows: `t_max_main={cfg['t_max_main']}`, `t_max_aw={cfg['t_max_aw']}`.")
    lines.append("")
    lines.append("## 3. Runtime")
    lines.append("")
    lines.append("| Method | Runtime (s) |")
    lines.append("|---|---:|")
    lines.append(f"| Luca defect-reduced AW | {rt['luca_defect_reduced']:.4f} |")
    lines.append(f"| Linear MFPT/splitting | {rt['linear_mfpt']:.4f} |")
    lines.append(f"| Sparse exact recursion | {rt['sparse_exact']:.4f} |")
    lines.append(f"| Dense recursion | {rt['dense_recursion']:.4f} |")
    lines.append(f"| Full AW/Cauchy | {rt['full_aw']:.4f} |")
    lines.append("")
    lines.append(f"Winner: **{win['method']}** (`{win['runtime_seconds']:.4f}s`).")
    lines.append("")
    lines.append("## 4. Accuracy Checks")
    lines.append("")
    lines.append("| Comparison | L1 error | Linf error |")
    lines.append("|---|---:|---:|")
    lines.append(f"| Dense vs Sparse (main horizon) | {err_dense['l1']:.3e} | {err_dense['linf']:.3e} |")
    lines.append(f"| Full AW vs Sparse (AW horizon) | {err_aw['l1']:.3e} | {err_aw['linf']:.3e} |")
    lines.append(f"| Luca vs Sparse (AW horizon) | {err_luca['l1']:.3e} | {err_luca['linf']:.3e} |")
    lines.append("")
    lines.append("## 5. Why Luca Is Fast Here")
    lines.append(f"- Defect pairs = `{luca['defect_pairs']}`, defect nodes = `{luca['defect_nodes']}`, while transient size is `n_T={cfg['n_transient']}`.")
    lines.append("- This pushes the defect solve core to a tiny system compared with full AW's dense solve scale.")
    lines.append("- At the same time, long main-horizon recursion (`t_max_main`) makes sparse/dense iteration less competitive.")
    lines.append("")
    lines.append("## 6. Figures")
    lines.append(f"- Configuration (same visual family as external detailed config): `{fig_cfg_rel}`")
    lines.append(f"- FPT overlay: `{fig_fpt_rel}`")
    lines.append(f"- Runtime bar: `{fig_runtime_rel}`")
    lines.append("")
    lines.append("## 7. Artifacts")
    lines.append(f"- JSON summary: `{json_rel}`")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Construct a Luca-fast benchmark case and export figures/data.")
    p.add_argument("--N", type=int, default=41)
    p.add_argument("--t-max-main", type=int, default=12000)
    p.add_argument("--t-max-aw", type=int, default=80)
    p.add_argument("--surv-tol", type=float, default=1e-13)
    p.add_argument("--aw-oversample", type=int, default=2)
    p.add_argument("--aw-r-pow10", type=float, default=8.0)
    args = p.parse_args()

    report_dir = Path(__file__).resolve().parent.parent
    data_dir = report_dir / "data"
    fig_dir = report_dir / "figures"
    data_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    start, m1, m2, arrow_map, q, delta = build_luca_fast_geometry(args.N)
    src_idx, dst_idx, probs = build_transition_arrays(
        N=args.N,
        q=q,
        delta=delta,
        arrow_map=arrow_map,
    )

    t0 = time.perf_counter()
    f_any_sparse, f1_sparse, f2_sparse, surv_sparse = run_exact_two_target(
        N=args.N,
        start=start,
        target1=m1,
        target2=m2,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        t_max=args.t_max_main,
        surv_tol=args.surv_tol,
    )
    rt_sparse = time.perf_counter() - t0

    sys_data = build_transient_system(
        N=args.N,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
        start=start,
        m1=m1,
        m2=m2,
    )
    Q = sys_data["Q"]
    r1 = sys_data["r1"]
    r2 = sys_data["r2"]
    alpha = sys_data["alpha"]
    i_start_t = int(sys_data["i_start_t"][0])

    t0 = time.perf_counter()
    f_any_dense, f1_dense, f2_dense, surv_dense = run_dense_recursion(
        Q=Q,
        r1=r1,
        r2=r2,
        alpha=alpha,
        t_max=args.t_max_main,
        surv_tol=args.surv_tol,
    )
    rt_dense = time.perf_counter() - t0

    t0 = time.perf_counter()
    linear = run_linear_mfpt(Q=Q, r1=r1, r2=r2, i_start_t=i_start_t)
    rt_linear = time.perf_counter() - t0

    t0 = time.perf_counter()
    aw = run_aw_fft(
        Q=Q,
        r1=r1,
        r2=r2,
        alpha=alpha,
        t_max_aw=args.t_max_aw,
        oversample=args.aw_oversample,
        r_pow10=args.aw_r_pow10,
    )
    rt_aw = time.perf_counter() - t0

    t0 = time.perf_counter()
    luca = run_aw_defect_giuggioli(
        N=args.N,
        q=q,
        start=start,
        m1=m1,
        m2=m2,
        arrow_map=arrow_map,
        delta=delta,
        t_max_aw=args.t_max_aw,
        oversample=args.aw_oversample,
        r_pow10=args.aw_r_pow10,
    )
    rt_luca = time.perf_counter() - t0

    sparse_aw = np.asarray(f_any_sparse[: args.t_max_aw + 1], dtype=np.float64)
    f1_sparse_aw = np.asarray(f1_sparse[: args.t_max_aw + 1], dtype=np.float64)
    f2_sparse_aw = np.asarray(f2_sparse[: args.t_max_aw + 1], dtype=np.float64)
    surv_sparse_aw = np.asarray(surv_sparse[: args.t_max_aw + 1], dtype=np.float64)

    sparse_sum = summarize_series(f_any_sparse, f1_sparse, f2_sparse, surv_sparse)
    sparse_aw_sum = summarize_series(sparse_aw, f1_sparse_aw, f2_sparse_aw, surv_sparse_aw)
    dense_sum = summarize_series(f_any_dense, f1_dense, f2_dense, surv_dense)
    aw_sum = summarize_series(
        np.concatenate([[0.0], aw["f_any"]]),
        np.concatenate([[0.0], aw["f1"]]),
        np.concatenate([[0.0], aw["f2"]]),
        np.concatenate([[1.0], 1.0 - np.cumsum(aw["f_any"])])
    )
    luca_sum = summarize_series(
        np.concatenate([[0.0], luca["f_any"]]),
        np.concatenate([[0.0], luca["f1"]]),
        np.concatenate([[0.0], luca["f2"]]),
        np.concatenate([[1.0], 1.0 - np.cumsum(luca["f_any"])])
    )
    luca_sum["defect_pairs"] = int(luca["defect_pairs"])
    luca_sum["defect_nodes"] = int(luca["defect_nodes"])
    luca_sum["local_bias_sites"] = int(luca["local_bias_sites"])

    runtime_rows = [
        ("Luca defect", rt_luca),
        ("Linear", rt_linear),
        ("Sparse", rt_sparse),
        ("Dense", rt_dense),
        ("Full AW", rt_aw),
    ]
    winner_name, winner_time = min(runtime_rows, key=lambda x: x[1])

    fig_cfg = fig_dir / "luca_fast_case_config_detailed.pdf"
    fig_fpt = fig_dir / "luca_fast_case_fpt_overlay.pdf"
    fig_rt = fig_dir / "luca_fast_case_runtime.pdf"
    out_json = data_dir / "luca_fast_case.json"
    out_md = report_dir / "luca_fast_case_cn.md"

    spec = ExternalCaseSpec(
        case_id="LF1",
        name="single-defect Luca-fast setup",
        type_name="local_bias_only",
        expected="Luca fastest",
        note="Constructed sparse-defect benchmark",
        local_bias_map={k: (v, delta) for k, v in arrow_map.items()},
        sticky_map={},
        barrier_map={},
        long_range_map={},
        global_bias=(0.0, 0.0),
    )
    plot_external_case_detailed_config(
        fig_cfg,
        N=args.N,
        start=start,
        m1=m1,
        m2=m2,
        spec=spec,
    )

    plot_fpt_overlay(
        out_path=fig_fpt,
        f_exact=sparse_aw,
        f_dense=f_any_dense[: args.t_max_aw + 1],
        f_aw=np.concatenate([[0.0], aw["f_any"]]),
        f_aw_defect=np.concatenate([[0.0], luca["f_any"]]),
        t_show=args.t_max_aw,
    )
    plot_runtime_bar(out_path=fig_rt, runtime_rows=runtime_rows)

    payload = {
        "config": {
            "N": args.N,
            "q": q,
            "delta": delta,
            "start_0_based": [int(start[0]), int(start[1])],
            "m1_0_based": [int(m1[0]), int(m1[1])],
            "m2_0_based": [int(m2[0]), int(m2[1])],
            "local_bias_sites": int(len(arrow_map)),
            "t_max_main": int(args.t_max_main),
            "t_max_aw": int(args.t_max_aw),
            "aw_oversample": int(args.aw_oversample),
            "aw_r_pow10": float(args.aw_r_pow10),
            "n_transient": int(Q.shape[0]),
        },
        "runtime_seconds": {
            "sparse_exact": float(rt_sparse),
            "dense_recursion": float(rt_dense),
            "linear_mfpt": float(rt_linear),
            "full_aw": float(rt_aw),
            "luca_defect_reduced": float(rt_luca),
        },
        "winner": {
            "method": winner_name,
            "runtime_seconds": float(winner_time),
        },
        "sparse_exact": sparse_sum,
        "sparse_exact_on_aw_horizon": sparse_aw_sum,
        "dense_recursion": dense_sum,
        "full_aw": aw_sum,
        "luca_defect_reduced": luca_sum,
        "linear_mfpt": linear,
        "error_dense_vs_sparse": l1_and_max_abs(f_any_dense, f_any_sparse),
        "error_full_aw_vs_sparse_aw": l1_and_max_abs(np.concatenate([[0.0], aw["f_any"]]), sparse_aw),
        "error_luca_vs_sparse_aw": l1_and_max_abs(np.concatenate([[0.0], luca["f_any"]]), sparse_aw),
        "artifacts": {
            "config_figure": str(fig_cfg.relative_to(report_dir)),
            "fpt_overlay_figure": str(fig_fpt.relative_to(report_dir)),
            "runtime_figure": str(fig_rt.relative_to(report_dir)),
            "report_markdown": str(out_md.relative_to(report_dir)),
        },
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    write_report_markdown(
        out_md,
        payload=payload,
        json_rel=str(out_json.relative_to(report_dir)),
        fig_cfg_rel=str(fig_cfg.relative_to(report_dir)),
        fig_fpt_rel=str(fig_fpt.relative_to(report_dir)),
        fig_runtime_rel=str(fig_rt.relative_to(report_dir)),
    )

    print(json.dumps({"winner": payload["winner"], "json": str(out_json)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
