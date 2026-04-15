#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "packages" / "vkcore" / "src"
REPORT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPORT_CODE = REPORT_ROOT / "code"
DEFAULT_DATA_ROOT = REPORT_ROOT / "artifacts" / "data" / "sensitivity"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SOURCE_REPORT_CODE) not in sys.path:
    sys.path.insert(0, str(SOURCE_REPORT_CODE))

import one_target_sensitivity_scan as sens
from vkcore.grid2d.one_two_target_gating import (
    compute_one_target_first_event_statistics,
    window_fraction_dict,
)


CLASS_LABELS = ["none", "left_only", "mem_only", "both"]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def directed_membrane_c2o_edges(case: dict[str, Any]) -> set[tuple[int, int]]:
    lx = int(case["Lx"])
    return {
        (int(a[1]) * lx + int(a[0]), int(b[1]) * lx + int(b[0]))
        for a, b in case.get("membrane_c2o_edges", set())
    }


def directed_left_open_edges(case: dict[str, Any]) -> set[tuple[int, int]]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    n_states = lx * wy
    channel = np.asarray(case["channel_mask"], dtype=bool).reshape(n_states)
    _y_mid, _y_low, _y_high, x0, _x1 = case["wall_span"]
    target_idx = int(case["target"][1]) * lx + int(case["target"][0])
    edges: set[tuple[int, int]] = set()
    for src_i, dst_i in zip(case["src_idx"], case["dst_idx"]):
        s = int(src_i)
        d = int(dst_i)
        if d == target_idx:
            continue
        xs = s % lx
        xd = d % lx
        if xs < int(x0) and xd < int(x0) and channel[s] and (not channel[d]):
            edges.add((s, d))
    return edges


def exact_exit_route_class_fpt(
    case: dict[str, Any],
    *,
    left_edges: set[tuple[int, int]],
    mem_edges: set[tuple[int, int]],
    surv_tol: float = 1.0e-12,
) -> tuple[np.ndarray, np.ndarray]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    n_states = lx * wy
    target_idx = int(case["target"][1]) * lx + int(case["target"][0])
    start_idx = int(case["start"][1]) * lx + int(case["start"][0])

    src = np.asarray(case["src_idx"], dtype=np.int64)
    dst = np.asarray(case["dst_idx"], dtype=np.int64)
    pr = np.asarray(case["probs"], dtype=np.float64)
    t_max = len(case["f_total"]) - 1

    is_hit = dst == target_idx
    src_non = src[~is_hit]
    dst_non = dst[~is_hit]
    pr_non = pr[~is_hit]
    left_non = np.asarray(
        [(int(a), int(b)) in left_edges for a, b in zip(src_non, dst_non)],
        dtype=bool,
    )
    mem_non = np.asarray(
        [(int(a), int(b)) in mem_edges for a, b in zip(src_non, dst_non)],
        dtype=bool,
    )

    src_hit = src[is_hit]
    pr_hit = pr[is_hit]

    p = np.zeros(n_states * 4, dtype=np.float64)
    p[start_idx] = 1.0

    f_class = np.zeros((t_max + 1, 4), dtype=np.float64)
    surv = np.zeros(t_max + 1, dtype=np.float64)
    surv[0] = 1.0

    for t in range(1, t_max + 1):
        for flag in range(4):
            base = flag * n_states
            if src_hit.size > 0:
                f_class[t, flag] = float(np.sum(p[base + src_hit] * pr_hit))

        p_next = np.zeros_like(p)
        for flag in range(4):
            base = flag * n_states
            left_seen = bool(flag & 1)
            mem_seen = bool(flag & 2)
            next_flag = (
                np.logical_or(left_seen, left_non).astype(np.int64)
                + 2 * np.logical_or(mem_seen, mem_non).astype(np.int64)
            )
            np.add.at(
                p_next,
                dst_non + next_flag * n_states,
                p[base + src_non] * pr_non,
            )
        surv[t] = max(0.0, float(np.sum(p_next)))
        p = p_next
        if surv[t] < float(surv_tol):
            if t < t_max:
                surv[t + 1 :] = surv[t]
            break

    return f_class, surv


def summarize_class_masses(f_class: np.ndarray) -> dict[str, float]:
    masses = np.asarray(f_class, dtype=np.float64).sum(axis=0)
    total = float(np.sum(masses))
    if total <= 0.0:
        return {f"total_{label}": 0.0 for label in CLASS_LABELS}
    return {f"total_{label}": float(masses[i] / total) for i, label in enumerate(CLASS_LABELS)}


def split_event_masses(stat: dict[str, Any]) -> tuple[float, float, float]:
    mean_hit = float(stat["mean_hit_time_in_window"])
    density = np.asarray(stat["conditional_density"], dtype=np.float64)
    if not np.isfinite(mean_hit):
        return 0.0, 0.0, 1.0
    threshold = 0.5 * mean_hit
    ts = np.arange(len(density), dtype=np.float64)
    early_mass = float(np.sum(density[ts <= threshold]))
    exit_prob = float(stat["event_probability"])
    late_mass = max(0.0, exit_prob - early_mass)
    no_exit_mass = max(0.0, 1.0 - exit_prob)
    return early_mass, late_mass, no_exit_mass


def metric_ratio(stat: dict[str, Any]) -> float:
    mean_event = float(stat["mean_event_time_given_event"])
    mean_hit = float(stat["mean_hit_time_in_window"])
    if not np.isfinite(mean_event) or not np.isfinite(mean_hit) or mean_hit <= 0.0:
        return float("nan")
    return float(mean_event / mean_hit)


def all_payloads() -> list[dict[str, Any]]:
    return sens.build_payloads("width_bx") + sens.build_payloads("delta")


def summarize_case(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    case = sens.build_case(payload)
    windows = sens.window_ranges(
        case["res"].t_peak1,
        case["res"].t_valley,
        case["res"].t_peak2,
        len(case["f_total"]),
    )
    left_edges = directed_left_open_edges(case)
    mem_edges = directed_membrane_c2o_edges(case)
    f_class, surv = exact_exit_route_class_fpt(case, left_edges=left_edges, mem_edges=mem_edges)
    window_props = window_fraction_dict(f_class, windows, list(CLASS_LABELS))
    totals = summarize_class_masses(f_class)

    tau_left = compute_one_target_first_event_statistics(
        case,
        Lx=int(case["Lx"]),
        windows=windows,
        event_edge_pairs=left_edges,
    )
    tau_mem = compute_one_target_first_event_statistics(
        case,
        Lx=int(case["Lx"]),
        windows=windows,
        event_edge_pairs=mem_edges,
    )

    late_window = sens.select_late_window(
        [
            {
                "window": name,
                "lo": lo,
                "hi": hi,
            }
            for name, lo, hi in windows
        ]
    )
    late_name = str(late_window["window"])
    left_stat = tau_left[late_name]
    mem_stat = tau_mem[late_name]
    left_early, left_late, left_no = split_event_masses(left_stat)
    mem_early, mem_late, mem_no = split_event_masses(mem_stat)

    summary = {
        "scan_name": str(payload["scan_name"]),
        "case_id": str(payload["case_id"]),
        "corridor_halfwidth": int(payload["corridor_halfwidth"]),
        "bx": float(payload["bx"]),
        "delta_core": float(payload["delta_core"]),
        "delta_open": float(payload["delta_open"]),
        "kappa_c2o": float(payload["kappa_c2o"]),
        "kappa_o2c": float(payload["kappa_o2c"]),
        "phase": int(case["res"].phase),
        "t_peak1": case["res"].t_peak1,
        "t_valley": case["res"].t_valley,
        "t_peak2": case["res"].t_peak2,
        "sep_peaks": float(case["res"].sep_peaks or 0.0),
        "left_edge_count": len(left_edges),
        "mem_edge_count": len(mem_edges),
        **totals,
        "late_window_name": late_name,
        **{f"late_{label}": float(window_props[late_name][label]) for label in CLASS_LABELS},
        "late_tau_left_prob": float(left_stat["event_probability"]),
        "late_tau_left_mean_event_time": float(left_stat["mean_event_time_given_event"]),
        "late_tau_left_mean_hit_time": float(left_stat["mean_hit_time_in_window"]),
        "late_tau_left_ratio": metric_ratio(left_stat),
        "late_tau_left_early_mass": left_early,
        "late_tau_left_late_mass": left_late,
        "late_tau_left_no_exit_mass": left_no,
        "late_tau_mem_prob": float(mem_stat["event_probability"]),
        "late_tau_mem_mean_event_time": float(mem_stat["mean_event_time_given_event"]),
        "late_tau_mem_mean_hit_time": float(mem_stat["mean_hit_time_in_window"]),
        "late_tau_mem_ratio": metric_ratio(mem_stat),
        "late_tau_mem_early_mass": mem_early,
        "late_tau_mem_late_mass": mem_late,
        "late_tau_mem_no_exit_mass": mem_no,
        "survival_tail": float(surv[-1]),
    }

    window_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    for name, lo, hi in windows:
        row_base = {
            "scan_name": str(payload["scan_name"]),
            "case_id": str(payload["case_id"]),
            "corridor_halfwidth": int(payload["corridor_halfwidth"]),
            "bx": float(payload["bx"]),
            "delta_core": float(payload["delta_core"]),
            "delta_open": float(payload["delta_open"]),
            "kappa_c2o": float(payload["kappa_c2o"]),
            "kappa_o2c": float(payload["kappa_o2c"]),
            "window": str(name),
            "lo": int(lo),
            "hi": int(hi),
        }
        window_rows.append(
            {
                **row_base,
                **{label: float(window_props[str(name)][label]) for label in CLASS_LABELS},
            }
        )
        for observable, stat in (("tau_left", tau_left[str(name)]), ("tau_mem", tau_mem[str(name)])):
            early_mass, late_mass, no_exit_mass = split_event_masses(stat)
            event_rows.append(
                {
                    **row_base,
                    "observable": observable,
                    "event_probability": float(stat["event_probability"]),
                    "mean_event_time_given_event": float(stat["mean_event_time_given_event"]),
                    "mean_hit_time_in_window": float(stat["mean_hit_time_in_window"]),
                    "ratio": metric_ratio(stat),
                    "early_mass": early_mass,
                    "late_mass": late_mass,
                    "no_exit_mass": no_exit_mass,
                    "consistency_gap": float(stat["consistency_gap"]),
                }
            )
    return summary, window_rows, event_rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split one-target trajectories by left-open-only versus membrane-assisted outside excursions."
    )
    parser.add_argument("--index-start", type=int, default=0)
    parser.add_argument("--index-stop", type=int, default=-1)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--suffix", default="")
    parser.add_argument("--out-dir", default=str(DEFAULT_DATA_ROOT))
    args = parser.parse_args()

    payloads = all_payloads()
    start = max(0, int(args.index_start))
    stop = len(payloads) if int(args.index_stop) < 0 else min(len(payloads), int(args.index_stop))
    payloads = payloads[start:stop]
    if int(args.limit) > 0:
        payloads = payloads[: int(args.limit)]

    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)

    summary_rows: list[dict[str, Any]] = []
    window_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []

    t0 = time.time()
    for payload in payloads:
        summary, case_windows, case_events = summarize_case(payload)
        summary_rows.append(summary)
        window_rows.extend(case_windows)
        event_rows.extend(case_events)

    suffix = f"_{args.suffix}" if args.suffix else ""
    summary_path = out_dir / f"one_target_left_open_split_cases{suffix}.csv"
    windows_path = out_dir / f"one_target_left_open_split_windows{suffix}.csv"
    events_path = out_dir / f"one_target_left_open_split_events{suffix}.csv"
    meta_path = out_dir / f"one_target_left_open_split_metadata{suffix}.json"

    summary_fields = [
        "scan_name",
        "case_id",
        "corridor_halfwidth",
        "bx",
        "delta_core",
        "delta_open",
        "kappa_c2o",
        "kappa_o2c",
        "phase",
        "t_peak1",
        "t_valley",
        "t_peak2",
        "sep_peaks",
        "left_edge_count",
        "mem_edge_count",
        "total_none",
        "total_left_only",
        "total_mem_only",
        "total_both",
        "late_window_name",
        "late_none",
        "late_left_only",
        "late_mem_only",
        "late_both",
        "late_tau_left_prob",
        "late_tau_left_mean_event_time",
        "late_tau_left_mean_hit_time",
        "late_tau_left_ratio",
        "late_tau_left_early_mass",
        "late_tau_left_late_mass",
        "late_tau_left_no_exit_mass",
        "late_tau_mem_prob",
        "late_tau_mem_mean_event_time",
        "late_tau_mem_mean_hit_time",
        "late_tau_mem_ratio",
        "late_tau_mem_early_mass",
        "late_tau_mem_late_mass",
        "late_tau_mem_no_exit_mass",
        "survival_tail",
    ]
    window_fields = [
        "scan_name",
        "case_id",
        "corridor_halfwidth",
        "bx",
        "delta_core",
        "delta_open",
        "kappa_c2o",
        "kappa_o2c",
        "window",
        "lo",
        "hi",
        "none",
        "left_only",
        "mem_only",
        "both",
    ]
    event_fields = [
        "scan_name",
        "case_id",
        "corridor_halfwidth",
        "bx",
        "delta_core",
        "delta_open",
        "kappa_c2o",
        "kappa_o2c",
        "window",
        "lo",
        "hi",
        "observable",
        "event_probability",
        "mean_event_time_given_event",
        "mean_hit_time_in_window",
        "ratio",
        "early_mass",
        "late_mass",
        "no_exit_mass",
        "consistency_gap",
    ]
    write_csv(summary_path, summary_rows, summary_fields)
    write_csv(windows_path, window_rows, window_fields)
    write_csv(events_path, event_rows, event_fields)
    write_json(
        meta_path,
        {
            "generated_at_epoch": time.time(),
            "duration_seconds": time.time() - t0,
            "case_count": len(summary_rows),
            "class_labels": list(CLASS_LABELS),
            "notes": {
                "left_open_only": "trajectory reaches target after at least one left-mouth corridor-to-outside exit and no membrane corridor-to-outside crossing",
                "mem_only": "trajectory reaches target after at least one membrane corridor-to-outside crossing and no left-mouth corridor-to-outside exit",
                "both": "trajectory uses both left-mouth and membrane corridor-to-outside exits before hitting the target",
                "none": "trajectory hits the target without any corridor-to-outside exit of either type",
            },
        },
    )
    print(f"WROTE_CASES={summary_path}")
    print(f"WROTE_WINDOWS={windows_path}")
    print(f"WROTE_EVENTS={events_path}")
    print(f"WROTE_METADATA={meta_path}")
    print(f"CASE_COUNT={len(summary_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
