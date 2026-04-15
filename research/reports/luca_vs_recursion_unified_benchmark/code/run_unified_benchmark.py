#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

from common import (
    DATA_DIR,
    FAMILY_LABELS,
    FAMILY_LABELS_CN,
    FAMILY_LUCA,
    FAMILY_TIME,
    ensure_dirs,
    group_rows,
)

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
from vkcore.comparison import (  # noqa: E402
    build_c1_geometry,
    build_luca_fast_geometry,
    build_reflecting_s0_config,
    build_two_target_transition_arrays,
    run_exact_two_target,
    run_reflecting_exact_recursion,
    run_reflecting_full_aw,
    run_two_target_defect_reduced_aw,
)
from vkcore.ring.encounter import (  # noqa: E402
    encounter_gf_anywhere,
    encounter_gf_fixed_site,
    encounter_time_anywhere,
    encounter_time_fixed_site,
)
from vkcore.ring.jumpover_pipeline import (  # noqa: E402
    Params as RingSingleTargetParams,
    aw_first_absorption_pmf,
    exact_first_absorption_pmf,
)


@dataclass
class PreparedTwoTarget:
    N: int
    q: float
    delta: float
    start: Tuple[int, int]
    m1: Tuple[int, int]
    m2: Tuple[int, int]
    arrow_map: Dict[Tuple[int, int], str]
    src_idx: np.ndarray
    dst_idx: np.ndarray
    probs: np.ndarray


def _median(vals: List[float]) -> float:
    return float(np.median(np.asarray(vals, dtype=np.float64))) if vals else 0.0


def _p95(vals: List[float]) -> float:
    return float(np.percentile(np.asarray(vals, dtype=np.float64), 95.0)) if vals else 0.0


def _peak_signature(f: np.ndarray) -> List[int]:
    arr = np.asarray(f, dtype=np.float64)
    if arr.size <= 3:
        return [int(np.argmax(arr))] if arr.size else []
    peaks: List[int] = []
    for i in range(1, arr.size - 1):
        if arr[i] >= arr[i - 1] and arr[i] >= arr[i + 1]:
            peaks.append(i)
    if len(peaks) < 2:
        return sorted(np.argsort(arr)[-2:].tolist())
    peaks = sorted(peaks, key=lambda idx: float(arr[idx]), reverse=True)[:2]
    return sorted(int(i) for i in peaks)


def _peak_metrics_match(a: np.ndarray, b: np.ndarray) -> bool:
    pa = _peak_signature(a)
    pb = _peak_signature(b)
    if len(pa) != len(pb):
        return False
    tol = max(5, int(0.02 * max(len(a), len(b))))
    return all(abs(int(x) - int(y)) <= tol for x, y in zip(pa, pb))


def _l1_linf(a: np.ndarray, b: np.ndarray) -> Dict[str, float]:
    n = min(len(a), len(b))
    if n <= 0:
        return {"l1_error": 0.0, "linf_error": 0.0}
    d = np.abs(np.asarray(a[:n], dtype=np.float64) - np.asarray(b[:n], dtype=np.float64))
    return {"l1_error": float(d.sum()), "linf_error": float(d.max())}


def _prepare_two_target_c1(cfg: Dict[str, Any]) -> PreparedTwoTarget:
    start, m1, m2, arrow_map, delta = build_c1_geometry(N=int(cfg["N"]))
    src_idx, dst_idx, probs = build_two_target_transition_arrays(
        N=int(cfg["N"]),
        q=float(cfg["q"]),
        delta=float(delta),
        arrow_map=arrow_map,
    )
    return PreparedTwoTarget(
        N=int(cfg["N"]),
        q=float(cfg["q"]),
        delta=float(delta),
        start=start,
        m1=m1,
        m2=m2,
        arrow_map=arrow_map,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
    )


def _prepare_two_target_lf1(cfg: Dict[str, Any]) -> PreparedTwoTarget:
    start, m1, m2, arrow_map, q, delta = build_luca_fast_geometry(int(cfg["N"]))
    src_idx, dst_idx, probs = build_two_target_transition_arrays(
        N=int(cfg["N"]),
        q=float(q),
        delta=float(delta),
        arrow_map=arrow_map,
    )
    return PreparedTwoTarget(
        N=int(cfg["N"]),
        q=float(q),
        delta=float(delta),
        start=start,
        m1=m1,
        m2=m2,
        arrow_map=arrow_map,
        src_idx=src_idx,
        dst_idx=dst_idx,
        probs=probs,
    )


def _prepare_reflecting_s0(_cfg: Dict[str, Any]):
    return build_reflecting_s0_config()


def _ring_single_target_payload(cfg: Dict[str, Any], horizon: int, solver_variant: str) -> Dict[str, Any]:
    params = RingSingleTargetParams(
        N=int(cfg["N"]),
        K=2,
        n0=int(cfg["start"]),
        target=int(cfg["target"]),
        sc_src=int(cfg["shortcut_src"]),
        sc_dst=int(cfg["shortcut_dst"]),
        mode="lazy_selfloop",
        q=float(cfg["q"]),
        beta=float(cfg["beta"]),
        rho=1.0,
        jumpover_absorbs=False,
    )
    if solver_variant == "ring_analytic_aw":
        f, meta = aw_first_absorption_pmf(
            params,
            max_steps=int(horizon),
            hmin_clip=0.0,
        )
        out = np.concatenate([[0.0], np.asarray(f, dtype=np.float64)])
        return {
            "f": out,
            "reported_seconds": 0.0,
            "breakdown": meta,
        }
    if solver_variant != "ring_time_absorption":
        raise ValueError(f"unknown ring solver: {solver_variant}")
    f, surv = exact_first_absorption_pmf(
        params,
        tmax=int(horizon),
        survival_eps=float(cfg["survival_eps"]),
    )
    out = np.concatenate([[0.0], np.asarray(f, dtype=np.float64)])
    return {
        "f": out,
        "reported_seconds": 0.0,
        "breakdown": {"survival_tail": float(surv)},
    }


def _two_target_payload(prep: PreparedTwoTarget, cfg: Dict[str, Any], horizon: int, solver_variant: str) -> Dict[str, Any]:
    if solver_variant == "two_target_sparse_exact":
        f_any, _f1, _f2, surv = run_exact_two_target(
            N=prep.N,
            start=prep.start,
            target1=prep.m1,
            target2=prep.m2,
            src_idx=prep.src_idx,
            dst_idx=prep.dst_idx,
            probs=prep.probs,
            t_max=int(horizon),
            surv_tol=float(cfg["time_surv_tol"]),
        )
        return {
            "f": np.asarray(f_any, dtype=np.float64),
            "reported_seconds": 0.0,
            "breakdown": {"survival_tail": float(surv[-1])},
        }
    if solver_variant != "two_target_defect_reduced_aw":
        raise ValueError(f"unknown two-target solver: {solver_variant}")
    out = run_two_target_defect_reduced_aw(
        N=prep.N,
        q=float(prep.q),
        start=prep.start,
        m1=prep.m1,
        m2=prep.m2,
        arrow_map=prep.arrow_map,
        delta=float(prep.delta),
        t_max_aw=int(horizon),
        oversample=int(cfg["aw_oversample"]),
        r_pow10=float(cfg["aw_r_pow10"]),
    )
    return {
        "f": np.concatenate([[0.0], np.asarray(out["f_any"], dtype=np.float64)]),
        "reported_seconds": 0.0,
        "breakdown": {
            "defect_pairs": int(out["defect_pairs"]),
            "defect_nodes": int(out["defect_nodes"]),
            "local_bias_sites": int(out["local_bias_sites"]),
            "aw_grid": out["grid"],
        },
    }


def _reflecting_payload(cfg_internal, cfg: Dict[str, Any], horizon: int, solver_variant: str) -> Dict[str, Any]:
    if solver_variant == "reflecting_exact_recursion":
        f, p_abs = run_reflecting_exact_recursion(cfg_internal, t_max=int(horizon))
        return {
            "f": np.concatenate([[0.0], np.asarray(f, dtype=np.float64)]),
            "reported_seconds": 0.0,
            "breakdown": {"absorbed_mass": float(p_abs)},
        }
    if solver_variant != "reflecting_full_aw":
        raise ValueError(f"unknown reflecting solver: {solver_variant}")
    f_aw, params = run_reflecting_full_aw(
        cfg_internal,
        t_max=int(horizon),
        oversample=int(cfg["aw_oversample"]),
        r_pow10=float(cfg["aw_r_pow10"]),
    )
    return {
        "f": np.concatenate([[0.0], np.asarray(f_aw, dtype=np.float64)]),
        "reported_seconds": 0.0,
        "breakdown": {"aw_grid": {"m": int(params.m), "r": float(params.r)}},
    }


def _encounter_payload(cfg: Dict[str, Any], horizon: int, solver_variant: str) -> Dict[str, Any]:
    common = dict(
        N=int(cfg["N"]),
        q1=float(cfg["q1"]),
        g1=float(cfg["g1"]),
        q2=float(cfg["q2"]),
        g2=float(cfg["g2"]),
        n0=int(cfg["n0"]),
        m0=int(cfg["m0"]),
        shortcut_src=int(cfg["shortcut_src"]),
        shortcut_dst=int(cfg["shortcut_dst"]),
        beta=float(cfg["beta"]),
        t_max=int(horizon),
    )
    if solver_variant == "pair_time_recursion":
        return encounter_time_anywhere(**common)
    if solver_variant == "encounter_anywhere_gf_aw":
        return encounter_gf_anywhere(
            **common,
            oversample=int(cfg["aw_oversample"]),
            r_pow10=float(cfg["aw_r_pow10"]),
        )
    if solver_variant == "pair_fixedsite_time_recursion":
        return encounter_time_fixed_site(**common, delta=int(cfg["delta"]))
    if solver_variant == "encounter_fixedsite_gf_aw":
        return encounter_gf_fixed_site(
            **common,
            delta=int(cfg["delta"]),
            oversample=int(cfg["aw_oversample"]),
            r_pow10=float(cfg["aw_r_pow10"]),
        )
    raise ValueError(f"unknown encounter solver: {solver_variant}")


def _build_runner(row: Dict[str, Any], caches: Dict[str, Any]) -> Callable[[], Dict[str, Any]]:
    cfg = json.loads(str(row["config_json"]))
    solver_variant = str(row["solver_variant"])
    horizon = int(row["effective_horizon"])
    kind = str(cfg["kind"])

    if kind == "ring_single_target":
        return lambda: _ring_single_target_payload(cfg, horizon, solver_variant)
    if kind == "encounter_fixed" or kind == "encounter_any":
        return lambda: _encounter_payload(cfg, horizon, solver_variant)
    if kind == "two_target_c1":
        prep = caches.setdefault("two_target_c1", _prepare_two_target_c1(cfg))
        return lambda: _two_target_payload(prep, cfg, horizon, solver_variant)
    if kind == "two_target_lf1":
        prep = caches.setdefault("two_target_lf1", _prepare_two_target_lf1(cfg))
        return lambda: _two_target_payload(prep, cfg, horizon, solver_variant)
    if kind == "reflecting_s0":
        prep = caches.setdefault("reflecting_s0", _prepare_reflecting_s0(cfg))
        return lambda: _reflecting_payload(prep, cfg, horizon, solver_variant)
    raise ValueError(f"unknown manifest kind: {kind}")


def _run_timed(
    row: Dict[str, Any],
    fn: Callable[[], Dict[str, Any]],
    *,
    warmup: int,
    repeats: int,
) -> tuple[List[Dict[str, Any]], List[float], Dict[str, Any]]:
    raw_rows: List[Dict[str, Any]] = []
    measured: List[float] = []
    last_payload: Dict[str, Any] = {}

    for idx in range(int(warmup)):
        t0 = time.perf_counter()
        payload = fn()
        wall = time.perf_counter() - t0
        raw_rows.append(
            {
                **row,
                "phase": "warmup",
                "run_index": idx,
                "runtime_seconds": float(wall),
                "reported_seconds": float(payload.get("reported_seconds", wall)),
                "breakdown_json": json.dumps(payload.get("breakdown", {}), ensure_ascii=False, sort_keys=True),
            }
        )

    for idx in range(int(repeats)):
        t0 = time.perf_counter()
        payload = fn()
        wall = time.perf_counter() - t0
        measured.append(float(wall))
        raw_rows.append(
            {
                **row,
                "phase": "measured",
                "run_index": idx,
                "runtime_seconds": float(wall),
                "reported_seconds": float(payload.get("reported_seconds", wall)),
                "breakdown_json": json.dumps(payload.get("breakdown", {}), ensure_ascii=False, sort_keys=True),
            }
        )
        last_payload = payload

    return raw_rows, measured, last_payload


def _write_runtime_raw(path: Path, rows: List[Dict[str, Any]]) -> None:
    fields = [
        "workload_id",
        "task_kind",
        "source_report",
        "model_family",
        "geometry_kind",
        "method_family",
        "solver_variant",
        "native_horizon",
        "curve_horizon",
        "effective_horizon",
        "state_size",
        "defect_pairs",
        "target_count",
        "common_error_horizon",
        "title_en",
        "title_cn",
        "note_en",
        "note_cn",
        "math_object_en",
        "math_object_cn",
        "theory_basis_en",
        "theory_basis_cn",
        "implementation_anchor_en",
        "implementation_anchor_cn",
        "primary_refs_json",
        "config_figure_id",
        "historical_source",
        "display_params_json",
        "config_json",
        "phase",
        "run_index",
        "runtime_seconds",
        "reported_seconds",
        "breakdown_json",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _row_core(row: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in row.items() if k not in {"phase", "run_index", "runtime_seconds", "reported_seconds", "breakdown_json"}}


def _summarize_pair(
    key: tuple[Any, ...],
    rows: List[Dict[str, Any]],
    outputs: Dict[tuple[str, str, str], Dict[str, Any]],
) -> Dict[str, Any]:
    workload_id, task_kind = key
    by_family = {row["method_family"]: row for row in rows}
    luca_row = by_family[FAMILY_LUCA]
    time_row = by_family[FAMILY_TIME]
    luca_key = (str(workload_id), str(task_kind), FAMILY_LUCA)
    time_key = (str(workload_id), str(task_kind), FAMILY_TIME)
    luca_out = outputs[luca_key]
    time_out = outputs[time_key]
    common_horizon = int(rows[0]["common_error_horizon"])
    a = np.asarray(luca_out["f"][: common_horizon + 1], dtype=np.float64)
    b = np.asarray(time_out["f"][: common_horizon + 1], dtype=np.float64)
    errs = _l1_linf(a, b)
    luca_median = float(luca_row["runtime_median_seconds"])
    time_median = float(time_row["runtime_median_seconds"])
    recommended = FAMILY_LUCA if luca_median <= time_median else FAMILY_TIME
    speedup = (time_median / luca_median) if luca_median > 0 else float("inf")
    return {
        "workload_id": str(workload_id),
        "task_kind": str(task_kind),
        "source_report": rows[0]["source_report"],
        "model_family": rows[0]["model_family"],
        "geometry_kind": rows[0]["geometry_kind"],
        "title_en": rows[0]["title_en"],
        "title_cn": rows[0]["title_cn"],
        "note_en": rows[0]["note_en"],
        "note_cn": rows[0]["note_cn"],
        "math_object_en": rows[0]["math_object_en"],
        "math_object_cn": rows[0]["math_object_cn"],
        "theory_basis_en": rows[0]["theory_basis_en"],
        "theory_basis_cn": rows[0]["theory_basis_cn"],
        "implementation_anchor_en": rows[0]["implementation_anchor_en"],
        "implementation_anchor_cn": rows[0]["implementation_anchor_cn"],
        "primary_refs_json": rows[0]["primary_refs_json"],
        "config_figure_id": rows[0]["config_figure_id"],
        "historical_source": rows[0]["historical_source"],
        "display_params_json": rows[0]["display_params_json"],
        "state_size": int(rows[0]["state_size"]),
        "defect_pairs": int(rows[0]["defect_pairs"]),
        "target_count": int(rows[0]["target_count"]),
        "common_error_horizon": common_horizon,
        "median_seconds_luca": luca_median,
        "median_seconds_time": time_median,
        "p95_seconds_luca": float(luca_row["runtime_p95_seconds"]),
        "p95_seconds_time": float(time_row["runtime_p95_seconds"]),
        "effective_horizon_luca": int(luca_row["effective_horizon"]),
        "effective_horizon_time": int(time_row["effective_horizon"]),
        "solver_variant_luca": luca_row["solver_variant"],
        "solver_variant_time": time_row["solver_variant"],
        "l1_error": errs["l1_error"],
        "linf_error": errs["linf_error"],
        "peak_metrics_match": bool(_peak_metrics_match(a, b)),
        "recommended_family": recommended,
        "recommended_label_en": FAMILY_LABELS[recommended],
        "recommended_label_cn": FAMILY_LABELS_CN[recommended],
        "speedup_time_over_luca": float(speedup),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run unified Luca-vs-recursion benchmark.")
    parser.add_argument("--manifest", type=str, default=str(DATA_DIR / "manifest.csv"))
    parser.add_argument("--runtime-raw", type=str, default=str(DATA_DIR / "runtime_raw.csv"))
    parser.add_argument("--runtime-summary", type=str, default=str(DATA_DIR / "runtime_summary.json"))
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    ensure_dirs()
    manifest_path = Path(args.manifest)
    runtime_raw_path = Path(args.runtime_raw)
    runtime_summary_path = Path(args.runtime_summary)

    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")

    with manifest_path.open("r", encoding="utf-8") as fh:
        manifest = list(csv.DictReader(fh))

    caches: Dict[str, Any] = {}
    runtime_raw_rows: List[Dict[str, Any]] = []
    summary_family_rows: List[Dict[str, Any]] = []
    outputs: Dict[tuple[str, str, str], Dict[str, Any]] = {}

    for row in manifest:
        runner = _build_runner(row, caches)
        raw_rows, measured, payload = _run_timed(
            row,
            runner,
            warmup=int(args.warmup),
            repeats=int(args.repeats),
        )
        runtime_raw_rows.extend(raw_rows)
        outputs[(str(row["workload_id"]), str(row["task_kind"]), str(row["method_family"]))] = payload
        summary_family_rows.append(
            {
                **_row_core(row),
                "runtime_median_seconds": _median(measured),
                "runtime_p95_seconds": _p95(measured),
                "runtime_mean_seconds": float(statistics.mean(measured)),
                "measured_samples": [float(x) for x in measured],
            }
        )

    _write_runtime_raw(runtime_raw_path, runtime_raw_rows)

    pair_groups = group_rows(summary_family_rows, "workload_id", "task_kind")
    pair_rows = [_summarize_pair(key, rows, outputs) for key, rows in sorted(pair_groups.items())]

    agg_by_task: List[Dict[str, Any]] = []
    for task_kind, rows in sorted(group_rows(pair_rows, "task_kind").items()):
        speedups = np.asarray([float(r["speedup_time_over_luca"]) for r in rows], dtype=np.float64)
        agg_by_task.append(
            {
                "task_kind": task_kind[0],
                "count": int(len(rows)),
                "median_speedup_time_over_luca": float(np.median(speedups)),
                "luca_faster_fraction": float(np.mean(speedups > 1.0)),
                "time_faster_fraction": float(np.mean(speedups < 1.0)),
            }
        )

    summary = {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "manifest": str(manifest_path),
            "runtime_raw": str(runtime_raw_path),
            "thread_env": {
                "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
                "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
                "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
            },
        },
        "policy": {
            "fairness": "practical_native_task",
            "benchmark_protocol": f"warmup={int(args.warmup)} measured={int(args.repeats)} median",
            "family_axes": [FAMILY_LUCA, FAMILY_TIME],
            "historical_full_fpt_reference": "appendix_f_embedded",
        },
        "counts": {
            "manifest_rows": int(len(manifest)),
            "runtime_rows": int(len(runtime_raw_rows)),
            "pair_rows": int(len(pair_rows)),
        },
        "family_rows": summary_family_rows,
        "pair_rows": pair_rows,
        "aggregates": {
            "by_task_kind": agg_by_task,
        },
        "references": {"historical_full_fpt_reference": "appendix_f_embedded"},
    }

    runtime_summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"runtime_summary": str(runtime_summary_path), "pair_rows": len(pair_rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
