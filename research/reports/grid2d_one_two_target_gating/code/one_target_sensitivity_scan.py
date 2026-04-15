#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any, Iterable

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

import one_two_target_gating_report as report_mod
from vkcore.grid2d.one_two_target_gating import (
    build_membrane_case_directional,
    compute_one_target_first_event_statistics,
    compute_one_target_window_path_statistics,
    window_ranges,
)


WIDTH_VALUES = [0, 1, 2, 3, 4, 5]
BX_VALUES = [-0.16, -0.12, -0.08, -0.04, 0.00, 0.04, 0.08]
DELTA_CORE_VALUES = [0.40, 0.60, 0.80, 0.95, 1.00]
DELTA_OPEN_VALUES = [0.00, 0.20, 0.40, 0.55, 0.80]
BASE_KAPPA_C2O = 0.002
BASE_KAPPA_O2C = 0.002
T_MAX_TOTAL = 5000

REGION_ORDER = [
    "left_core",
    "left_shoulders",
    "left_outer",
    "corridor",
    "outer_reservoir",
    "target_funnel",
]
WINDOW_PRIORITY = ("peak2", "late")
OBSERVABLES = ("tau_out", "tau_mem")


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


def safe_tag(value: float) -> str:
    return f"{value:+.2f}".replace("+", "p").replace("-", "m").replace(".", "p")


def base_payload() -> dict[str, Any]:
    return {
        "corridor_halfwidth": int(report_mod.ONE_TARGET_BASE_ARGS["corridor_halfwidth"]),
        "bx": float(report_mod.ONE_TARGET_BASE_ARGS["bx"]),
        "delta_core": float(report_mod.ONE_TARGET_BASE_ARGS["delta_core"]),
        "delta_open": float(report_mod.ONE_TARGET_BASE_ARGS["delta_open"]),
        "kappa_c2o": float(BASE_KAPPA_C2O),
        "kappa_o2c": float(BASE_KAPPA_O2C),
        "t_max_total": int(T_MAX_TOTAL),
    }


def build_payloads(scan_name: str) -> list[dict[str, Any]]:
    base = base_payload()
    rows: list[dict[str, Any]] = []
    if scan_name == "width_bx":
        for corridor_halfwidth in WIDTH_VALUES:
            for bx in BX_VALUES:
                rows.append(
                    {
                        **base,
                        "scan_name": scan_name,
                        "case_id": f"width_h{int(corridor_halfwidth)}_bx_{safe_tag(float(bx))}",
                        "corridor_halfwidth": int(corridor_halfwidth),
                        "bx": float(bx),
                    }
                )
    elif scan_name == "delta":
        for delta_core in DELTA_CORE_VALUES:
            for delta_open in DELTA_OPEN_VALUES:
                rows.append(
                    {
                        **base,
                        "scan_name": scan_name,
                        "case_id": f"delta_core_{safe_tag(float(delta_core))}_open_{safe_tag(float(delta_open))}",
                        "delta_core": float(delta_core),
                        "delta_open": float(delta_open),
                    }
                )
    else:
        raise ValueError(f"unsupported scan: {scan_name}")
    return rows


def region_masks(case: dict[str, Any]) -> dict[str, np.ndarray]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    start_y = int(case["start"][1])
    _y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    yy, xx = np.meshgrid(np.arange(wy), np.arange(lx), indexing="ij")
    left = xx < int(x0)
    in_corridor = (yy >= int(y_low)) & (yy <= int(y_high))
    center_strip = np.abs(yy - int(start_y)) <= 1
    return {
        "left_core": left & center_strip,
        "left_shoulders": left & in_corridor & (~center_strip),
        "left_outer": left & (~in_corridor),
        "corridor": (xx >= int(x0)) & (xx <= int(x1)) & in_corridor,
        "outer_reservoir": (xx >= int(x0)) & (xx <= int(x1)) & (~in_corridor),
        "target_funnel": xx > int(x1),
    }


def event_state_mask_outside(case: dict[str, Any]) -> np.ndarray:
    return ~np.asarray(case["channel_mask"], dtype=bool)


def event_edge_pairs_membrane(case: dict[str, Any]) -> set[tuple[int, int]]:
    lx = int(case["Lx"])
    return {
        (int(a[1]) * lx + int(a[0]), int(b[1]) * lx + int(b[0]))
        for a, b in case.get("membrane_c2o_edges", set())
    }


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


def build_case(payload: dict[str, Any]) -> dict[str, Any]:
    base_args = dict(report_mod.ONE_TARGET_BASE_ARGS)
    return build_membrane_case_directional(
        Lx=int(base_args["Lx"]),
        Wy=int(base_args["Wy"]),
        bx=float(payload["bx"]),
        corridor_halfwidth=int(payload["corridor_halfwidth"]),
        wall_margin=int(base_args["wall_margin"]),
        delta_core=float(payload["delta_core"]),
        delta_open=float(payload["delta_open"]),
        start_x=int(base_args["start_x"]),
        target_x=int(base_args["target_x"]),
        kappa_c2o=float(payload["kappa_c2o"]),
        kappa_o2c=float(payload["kappa_o2c"]),
        t_max_total=int(payload["t_max_total"]),
    )


def select_late_window(window_rows: list[dict[str, Any]]) -> dict[str, Any]:
    lookup = {str(row["window"]): row for row in window_rows}
    for window_name in WINDOW_PRIORITY:
        if window_name in lookup:
            return lookup[window_name]
    return window_rows[-1]


def summarize_case(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    case = build_case(payload)
    windows = window_ranges(case["res"].t_peak1, case["res"].t_valley, case["res"].t_peak2, len(case["f_total"]))
    rollback_exact = report_mod.one_target_rollback_exact(case)
    path_stats = compute_one_target_window_path_statistics(case, Lx=int(case["Lx"]), windows=windows)
    tau_out = compute_one_target_first_event_statistics(
        case,
        Lx=int(case["Lx"]),
        windows=windows,
        event_state_mask=event_state_mask_outside(case),
    )
    tau_mem = compute_one_target_first_event_statistics(
        case,
        Lx=int(case["Lx"]),
        windows=windows,
        event_edge_pairs=event_edge_pairs_membrane(case),
    )
    masks = region_masks(case)

    window_rows: list[dict[str, Any]] = []
    region_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []

    for window_name, lo, hi in windows:
        path = path_stats.get(window_name)
        lr = rollback_exact["lr_window_props"].get(window_name, {})
        base_row = {
            "scan_name": str(payload["scan_name"]),
            "case_id": str(payload["case_id"]),
            "corridor_halfwidth": int(payload["corridor_halfwidth"]),
            "bx": float(payload["bx"]),
            "delta_core": float(payload["delta_core"]),
            "delta_open": float(payload["delta_open"]),
            "kappa_c2o": float(payload["kappa_c2o"]),
            "kappa_o2c": float(payload["kappa_o2c"]),
            "window": str(window_name),
            "lo": int(lo),
            "hi": int(hi),
            "hit_mass": float(path["hit_mass"]) if path is not None else float("nan"),
            "flux_c2o": float(path["flux_c2o"]) if path is not None else float("nan"),
            "flux_o2c": float(path["flux_o2c"]) if path is not None else float("nan"),
            "occupancy_mass": float(path["occupancy_mass"]) if path is not None else float("nan"),
            "L0R0": float(lr.get("L0R0", float("nan"))),
            "L0R1": float(lr.get("L0R1", float("nan"))),
            "L1R0": float(lr.get("L1R0", float("nan"))),
            "L1R1": float(lr.get("L1R1", float("nan"))),
            "rollback_share": float(lr.get("L0R1", 0.0) + lr.get("L1R1", 0.0)),
        }
        window_rows.append(base_row)

        if path is not None:
            occ = np.asarray(path["occupancy"], dtype=np.float64)
            for region in REGION_ORDER:
                region_rows.append(
                    {
                        **{k: base_row[k] for k in ("scan_name", "case_id", "corridor_halfwidth", "bx", "delta_core", "delta_open", "kappa_c2o", "kappa_o2c", "window")},
                        "region": region,
                        "occupancy_share": float(np.sum(occ[masks[region]])),
                    }
                )

        for observable, stats_map in (("tau_out", tau_out), ("tau_mem", tau_mem)):
            stat = stats_map.get(window_name)
            if stat is None:
                continue
            early_mass, late_mass, no_exit_mass = split_event_masses(stat)
            event_rows.append(
                {
                    **{k: base_row[k] for k in ("scan_name", "case_id", "corridor_halfwidth", "bx", "delta_core", "delta_open", "kappa_c2o", "kappa_o2c", "window", "lo", "hi")},
                    "observable": observable,
                    "exit_prob": float(stat["event_probability"]),
                    "mean_event_time": float(stat["mean_event_time_given_event"]),
                    "mean_hit_time": float(stat["mean_hit_time_in_window"]),
                    "event_time_ratio": metric_ratio(stat),
                    "early_mass": early_mass,
                    "late_mass": late_mass,
                    "no_exit_mass": no_exit_mass,
                }
            )

    late_row = select_late_window(window_rows)
    late_regions = {
        row["region"]: float(row["occupancy_share"])
        for row in region_rows
        if str(row["window"]) == str(late_row["window"])
    }
    late_events = {
        str(row["observable"]): row
        for row in event_rows
        if str(row["window"]) == str(late_row["window"])
    }

    summary_row = {
        "scan_name": str(payload["scan_name"]),
        "case_id": str(payload["case_id"]),
        "corridor_halfwidth": int(payload["corridor_halfwidth"]),
        "bx": float(payload["bx"]),
        "delta_core": float(payload["delta_core"]),
        "delta_open": float(payload["delta_open"]),
        "kappa_c2o": float(payload["kappa_c2o"]),
        "kappa_o2c": float(payload["kappa_o2c"]),
        "phase": int(case["res"].phase),
        "t_peak1": None if case["res"].t_peak1 is None else int(case["res"].t_peak1),
        "t_valley": None if case["res"].t_valley is None else int(case["res"].t_valley),
        "t_peak2": None if case["res"].t_peak2 is None else int(case["res"].t_peak2),
        "valley_over_max": None if case["res"].valley_over_max is None else float(case["res"].valley_over_max),
        "sep_peaks": float(case["res"].sep_peaks),
        "no_leak_total": float(rollback_exact["totals"]["no_leak_total"]),
        "leak_total": float(rollback_exact["totals"]["leak_total"]),
        "rollback_total": float(rollback_exact["totals"]["rollback_total"]),
        "late_window_name": str(late_row["window"]),
        "late_window_lo": int(late_row["lo"]),
        "late_window_hi": int(late_row["hi"]),
        "late_hit_mass": float(late_row["hit_mass"]),
        "late_flux_c2o": float(late_row["flux_c2o"]),
        "late_flux_o2c": float(late_row["flux_o2c"]),
        "late_L0R0": float(late_row["L0R0"]),
        "late_L0R1": float(late_row["L0R1"]),
        "late_L1R0": float(late_row["L1R0"]),
        "late_L1R1": float(late_row["L1R1"]),
        "late_rollback_share": float(late_row["rollback_share"]),
    }

    for observable in OBSERVABLES:
        event = late_events.get(observable)
        prefix = f"late_{observable}"
        summary_row[f"{prefix}_prob"] = float(event["exit_prob"]) if event is not None else float("nan")
        summary_row[f"{prefix}_mean_event_time"] = float(event["mean_event_time"]) if event is not None else float("nan")
        summary_row[f"{prefix}_mean_hit_time"] = float(event["mean_hit_time"]) if event is not None else float("nan")
        summary_row[f"{prefix}_ratio"] = float(event["event_time_ratio"]) if event is not None else float("nan")
        summary_row[f"{prefix}_early_mass"] = float(event["early_mass"]) if event is not None else float("nan")
        summary_row[f"{prefix}_late_mass"] = float(event["late_mass"]) if event is not None else float("nan")
        summary_row[f"{prefix}_no_exit_mass"] = float(event["no_exit_mass"]) if event is not None else float("nan")

    for region in REGION_ORDER:
        summary_row[f"late_{region}_share"] = float(late_regions.get(region, float("nan")))

    return summary_row, window_rows, event_rows, region_rows


def baseline_signature(scan_name: str) -> tuple[int, float, float, float]:
    base = base_payload()
    return (
        int(base["corridor_halfwidth"]),
        float(base["bx"]),
        float(base["delta_core"]),
        float(base["delta_open"]),
    )


def summarize_highlights(case_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics = [
        "sep_peaks",
        "t_peak2",
        "late_rollback_share",
        "late_tau_mem_prob",
        "late_tau_out_prob",
        "late_corridor_share",
        "late_outer_reservoir_share",
        "late_target_funnel_share",
    ]
    rows: list[dict[str, Any]] = []
    for scan_name in sorted({str(row["scan_name"]) for row in case_rows}):
        scan_rows = [row for row in case_rows if str(row["scan_name"]) == scan_name]
        sig = baseline_signature(scan_name)
        baseline = next(
            (
                row
                for row in scan_rows
                if (
                    int(row["corridor_halfwidth"]),
                    float(row["bx"]),
                    float(row["delta_core"]),
                    float(row["delta_open"]),
                )
                == sig
            ),
            None,
        )
        if baseline is None:
            continue
        rows.append(
            {
                "scan_name": scan_name,
                "metric": "baseline",
                "case_id": str(baseline["case_id"]),
                "value": float(baseline["sep_peaks"]),
                "delta_from_baseline": 0.0,
                "phase": int(baseline["phase"]),
            }
        )
        for metric in metrics:
            baseline_value = baseline.get(metric)
            if baseline_value is None or not np.isfinite(float(baseline_value)):
                continue
            comparable = []
            for row in scan_rows:
                value = row.get(metric)
                if value is None:
                    continue
                value_f = float(value)
                if not np.isfinite(value_f):
                    continue
                comparable.append((abs(value_f - float(baseline_value)), value_f, row))
            if not comparable:
                continue
            delta_abs, value_f, winner = max(comparable, key=lambda item: item[0])
            rows.append(
                {
                    "scan_name": scan_name,
                    "metric": metric,
                    "case_id": str(winner["case_id"]),
                    "value": value_f,
                    "delta_from_baseline": float(value_f - float(baseline_value)),
                    "phase": int(winner["phase"]),
                }
            )
    return rows


def run_scan(
    *,
    scan_name: str,
    index_start: int,
    index_stop: int | None,
    limit: int | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    payloads = build_payloads(scan_name)
    stop = len(payloads) if index_stop is None else min(len(payloads), int(index_stop))
    payloads = payloads[int(index_start) : stop]
    if limit is not None:
        payloads = payloads[: int(limit)]

    case_rows: list[dict[str, Any]] = []
    window_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    region_rows: list[dict[str, Any]] = []
    started = time.time()

    for idx, payload in enumerate(payloads, start=1):
        t0 = time.time()
        case_row, window_rows_one, event_rows_one, region_rows_one = summarize_case(payload)
        case_rows.append(case_row)
        window_rows.extend(window_rows_one)
        event_rows.extend(event_rows_one)
        region_rows.extend(region_rows_one)
        print(
            f"[{scan_name} {idx}/{len(payloads)}] {payload['case_id']} "
            f"phase={case_row['phase']} sep={case_row['sep_peaks']:.4f} "
            f"late={case_row['late_window_name']} dt={time.time() - t0:.2f}s",
            flush=True,
        )

    metadata = {
        "scan_name": scan_name,
        "count": len(payloads),
        "elapsed_seconds": time.time() - started,
        "parameter_ranges": {
            "width_bx": {
                "corridor_halfwidth": WIDTH_VALUES,
                "bx": BX_VALUES,
            },
            "delta": {
                "delta_core": DELTA_CORE_VALUES,
                "delta_open": DELTA_OPEN_VALUES,
            },
        },
        "baseline_parameters": base_payload(),
        "notes": {
            "late_window_name": "peak2 when a detected second peak exists; otherwise the final fallback window returned by window_ranges().",
            "tau_out": "first time the chain enters any outside state",
            "tau_mem": "first time the chain crosses a membrane corridor-to-outside edge",
            "delta_clipping": "local delta values are clipped into [0, 1] by the transition kernel",
            "kappa_protocol": {
                "kappa_c2o": BASE_KAPPA_C2O,
                "kappa_o2c": BASE_KAPPA_O2C,
                "interpretation": "hold the already-scanned symmetric directional permeability fixed while sweeping unswept geometry/bias parameters",
            },
        },
        "phase_counts": {
            str(phase): sum(1 for row in case_rows if int(row["phase"]) == phase)
            for phase in sorted({int(row["phase"]) for row in case_rows})
        },
    }
    return case_rows, window_rows, event_rows, region_rows, metadata


def output_paths(scan_name: str, suffix: str | None, *, data_root: Path) -> dict[str, Path]:
    tag = scan_name if suffix is None else f"{scan_name}_{suffix}"
    return {
        "cases": data_root / f"one_target_{tag}_cases.csv",
        "windows": data_root / f"one_target_{tag}_windows.csv",
        "events": data_root / f"one_target_{tag}_events.csv",
        "regions": data_root / f"one_target_{tag}_regions.csv",
        "highlights": data_root / f"one_target_{tag}_highlights.csv",
        "metadata": data_root / f"one_target_{tag}_metadata.json",
    }


def case_fieldnames() -> list[str]:
    fields = [
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
        "valley_over_max",
        "sep_peaks",
        "no_leak_total",
        "leak_total",
        "rollback_total",
        "late_window_name",
        "late_window_lo",
        "late_window_hi",
        "late_hit_mass",
        "late_flux_c2o",
        "late_flux_o2c",
        "late_L0R0",
        "late_L0R1",
        "late_L1R0",
        "late_L1R1",
        "late_rollback_share",
    ]
    for observable in OBSERVABLES:
        prefix = f"late_{observable}"
        fields.extend(
            [
                f"{prefix}_prob",
                f"{prefix}_mean_event_time",
                f"{prefix}_mean_hit_time",
                f"{prefix}_ratio",
                f"{prefix}_early_mass",
                f"{prefix}_late_mass",
                f"{prefix}_no_exit_mass",
            ]
        )
    fields.extend([f"late_{region}_share" for region in REGION_ORDER])
    return fields


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan unswept one-target sensitivity parameters for the gating report.")
    parser.add_argument("--scan", choices=["all", "width_bx", "delta"], default="all")
    parser.add_argument("--index-start", type=int, default=0)
    parser.add_argument("--index-stop", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--suffix", type=str, default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_DATA_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_root = Path(args.out_dir).expanduser().resolve()
    ensure_dir(data_root)
    scans = ["width_bx", "delta"] if args.scan == "all" else [str(args.scan)]
    all_case_rows: list[dict[str, Any]] = []
    all_window_rows: list[dict[str, Any]] = []
    all_event_rows: list[dict[str, Any]] = []
    all_region_rows: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {"scans": {}, "generated_at_root": str(data_root)}

    for scan_name in scans:
        case_rows, window_rows, event_rows, region_rows, scan_meta = run_scan(
            scan_name=scan_name,
            index_start=int(args.index_start),
            index_stop=args.index_stop,
            limit=args.limit,
        )
        highlights = summarize_highlights(case_rows)
        paths = output_paths(scan_name, args.suffix, data_root=data_root)
        write_csv(paths["cases"], case_rows, case_fieldnames())
        write_csv(
            paths["windows"],
            window_rows,
            [
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
                "hit_mass",
                "flux_c2o",
                "flux_o2c",
                "occupancy_mass",
                "L0R0",
                "L0R1",
                "L1R0",
                "L1R1",
                "rollback_share",
            ],
        )
        write_csv(
            paths["events"],
            event_rows,
            [
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
                "exit_prob",
                "mean_event_time",
                "mean_hit_time",
                "event_time_ratio",
                "early_mass",
                "late_mass",
                "no_exit_mass",
            ],
        )
        write_csv(
            paths["regions"],
            region_rows,
            [
                "scan_name",
                "case_id",
                "corridor_halfwidth",
                "bx",
                "delta_core",
                "delta_open",
                "kappa_c2o",
                "kappa_o2c",
                "window",
                "region",
                "occupancy_share",
            ],
        )
        write_csv(
            paths["highlights"],
            highlights,
            ["scan_name", "metric", "case_id", "value", "delta_from_baseline", "phase"],
        )
        write_json(paths["metadata"], scan_meta)

        all_case_rows.extend(case_rows)
        all_window_rows.extend(window_rows)
        all_event_rows.extend(event_rows)
        all_region_rows.extend(region_rows)
        metadata["scans"][scan_name] = {**scan_meta, "outputs": {k: str(v) for k, v in paths.items()}}

    if len(scans) > 1:
        merged_paths = output_paths("all", args.suffix, data_root=data_root)
        write_csv(merged_paths["cases"], all_case_rows, case_fieldnames())
        write_csv(
            merged_paths["windows"],
            all_window_rows,
            [
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
                "hit_mass",
                "flux_c2o",
                "flux_o2c",
                "occupancy_mass",
                "L0R0",
                "L0R1",
                "L1R0",
                "L1R1",
                "rollback_share",
            ],
        )
        write_csv(
            merged_paths["events"],
            all_event_rows,
            [
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
                "exit_prob",
                "mean_event_time",
                "mean_hit_time",
                "event_time_ratio",
                "early_mass",
                "late_mass",
                "no_exit_mass",
            ],
        )
        write_csv(
            merged_paths["regions"],
            all_region_rows,
            [
                "scan_name",
                "case_id",
                "corridor_halfwidth",
                "bx",
                "delta_core",
                "delta_open",
                "kappa_c2o",
                "kappa_o2c",
                "window",
                "region",
                "occupancy_share",
            ],
        )
        write_csv(
            merged_paths["highlights"],
            summarize_highlights(all_case_rows),
            ["scan_name", "metric", "case_id", "value", "delta_from_baseline", "phase"],
        )
        write_json(merged_paths["metadata"], metadata)


if __name__ == "__main__":
    main()
