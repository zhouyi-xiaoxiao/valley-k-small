#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "packages" / "vkcore" / "src"
REPORT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPORT_ROOT / "artifacts" / "data" / "region_scans" / "one_target_sym_shared_left_top_bottom"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import one_two_target_gating_report as report_mod
from vkcore.grid2d.one_two_target_gating import (
    build_membrane_case_directional,
    compute_one_target_window_path_statistics,
    window_ranges,
)


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


def build_case() -> dict[str, Any]:
    base_args = dict(report_mod.ONE_TARGET_BASE_ARGS)
    case = build_membrane_case_directional(
        **base_args,
        kappa_c2o=0.002,
        kappa_o2c=0.002,
        t_max_total=int(report_mod.ONE_TARGET_REP_T_MAX),
    )
    case["case_name"] = "sym_shared"
    case["display_name"] = str(report_mod.ONE_TARGET_CASE_TITLES["sym_shared"])
    return case


def region_masks(case: dict[str, Any]) -> dict[str, np.ndarray]:
    lx = int(case["Lx"])
    wy = int(case["Wy"])
    _y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    yy, xx = np.meshgrid(np.arange(wy), np.arange(lx), indexing="ij")
    return {
        "left_full": xx < int(x0),
        "top_full": (xx >= int(x0)) & (xx <= int(x1)) & (yy > int(y_high)),
        "bottom_full": (xx >= int(x0)) & (xx <= int(x1)) & (yy < int(y_low)),
    }


def region_formulas(case: dict[str, Any]) -> dict[str, str]:
    _y_mid, y_low, y_high, x0, x1 = case["wall_span"]
    return {
        "left_full": f"x < {int(x0)}",
        "top_full": f"{int(x0)} <= x <= {int(x1)} and y > {int(y_high)}",
        "bottom_full": f"{int(x0)} <= x <= {int(x1)} and y < {int(y_low)}",
    }


def windows_payload(case: dict[str, Any]) -> list[tuple[str, int, int]]:
    return window_ranges(
        case["res"].t_peak1,
        case["res"].t_valley,
        case["res"].t_peak2,
        len(case["f_total"]),
    )


def run_scan() -> dict[str, Path]:
    case = build_case()
    windows = windows_payload(case)
    stats = compute_one_target_window_path_statistics(case, Lx=int(case["Lx"]), windows=windows)
    masks = region_masks(case)

    summary_rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    arrays_payload: dict[str, np.ndarray] = {}
    top_bottom_diff: list[dict[str, Any]] = []

    for window_name, lo, hi in windows:
        payload = stats[window_name]
        occ = np.asarray(payload["occupancy"], dtype=np.float64)
        arrays_payload[f"{window_name}_occupancy"] = occ
        selected_share = 0.0
        region_shares: dict[str, float] = {}

        for region_name, mask in masks.items():
            arrays_payload[f"{region_name}_mask"] = mask.astype(np.uint8)
            coords = np.argwhere(mask)
            values = occ[mask]
            region_share = float(np.sum(values))
            selected_share += region_share
            region_shares[region_name] = region_share
            max_val = float(np.max(values)) if values.size else 0.0
            mean_val = float(np.mean(values)) if values.size else 0.0
            summary_rows.append(
                {
                    "case": case["case_name"],
                    "window": window_name,
                    "t_lo": int(lo),
                    "t_hi": int(hi),
                    "region": region_name,
                    "region_formula": region_formulas(case)[region_name],
                    "cell_count": int(mask.sum()),
                    "occupancy_share": region_share,
                    "mean_cell_occupancy": mean_val,
                    "max_cell_occupancy": max_val,
                    "hit_mass": float(payload["hit_mass"]),
                    "window_flux_c2o": float(payload["flux_c2o"]),
                    "window_flux_o2c": float(payload["flux_o2c"]),
                }
            )

            order = np.argsort(-values, kind="stable")
            for rank, idx_in_order in enumerate(order, start=1):
                y, x = coords[int(idx_in_order)]
                detail_rows.append(
                    {
                        "case": case["case_name"],
                        "window": window_name,
                        "t_lo": int(lo),
                        "t_hi": int(hi),
                        "region": region_name,
                        "x": int(x),
                        "y": int(y),
                        "occupancy": float(values[int(idx_in_order)]),
                        "rank_in_region": int(rank),
                    }
                )

        top_bottom_diff.append(
            {
                "case": case["case_name"],
                "window": window_name,
                "top_share": float(region_shares["top_full"]),
                "bottom_share": float(region_shares["bottom_full"]),
                "top_minus_bottom": float(region_shares["top_full"] - region_shares["bottom_full"]),
                "selected_region_share": float(selected_share),
            }
        )

    metadata = {
        "case": case["case_name"],
        "display_name": case["display_name"],
        "geometry": {
            "Lx": int(case["Lx"]),
            "Wy": int(case["Wy"]),
            "start": [int(case["start"][0]), int(case["start"][1])],
            "target": [int(case["target"][0]), int(case["target"][1])],
            "wall_span": [int(v) for v in case["wall_span"]],
            "x_gate_star": int((int(report_mod.ONE_TARGET_BASE_ARGS["start_x"]) + int(report_mod.ONE_TARGET_BASE_ARGS["target_x"])) // 2),
        },
        "region_formulas": region_formulas(case),
        "windows": [
            {
                "window": str(window_name),
                "t_lo": int(lo),
                "t_hi": int(hi),
                "hit_mass": float(stats[window_name]["hit_mass"]),
                "flux_c2o": float(stats[window_name]["flux_c2o"]),
                "flux_o2c": float(stats[window_name]["flux_o2c"]),
            }
            for window_name, lo, hi in windows
        ],
        "top_bottom_comparison": top_bottom_diff,
    }

    ensure_dir(DATA_ROOT)
    summary_path = DATA_ROOT / "window_region_summary.csv"
    detail_path = DATA_ROOT / "window_region_cells.csv"
    meta_path = DATA_ROOT / "scan_metadata.json"
    arrays_path = DATA_ROOT / "window_region_arrays.npz"

    write_csv(
        summary_path,
        summary_rows,
        [
            "case",
            "window",
            "t_lo",
            "t_hi",
            "region",
            "region_formula",
            "cell_count",
            "occupancy_share",
            "mean_cell_occupancy",
            "max_cell_occupancy",
            "hit_mass",
            "window_flux_c2o",
            "window_flux_o2c",
        ],
    )
    write_csv(
        detail_path,
        detail_rows,
        [
            "case",
            "window",
            "t_lo",
            "t_hi",
            "region",
            "x",
            "y",
            "occupancy",
            "rank_in_region",
        ],
    )
    write_json(meta_path, metadata)
    np.savez_compressed(arrays_path, **arrays_payload)

    return {
        "summary": summary_path,
        "detail": detail_path,
        "metadata": meta_path,
        "arrays": arrays_path,
    }


def main() -> int:
    outputs = run_scan()
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
