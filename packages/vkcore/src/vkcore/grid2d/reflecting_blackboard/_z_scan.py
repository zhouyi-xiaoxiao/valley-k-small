#!/usr/bin/env python3
"""Scan variants of the wall-endpoint geometry (case Z)."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Dict

from vkcore.grid2d.bimod_legacy_imports import exact_fpt
from vkcore.grid2d.model_core_reflecting import spec_to_internal

from . import io as io_helpers
from .cases_blackboard import DIR_MAP, CaseDef, build_barriers, build_z
from .model import case_to_spec
from .scans import compute_metrics_with_fallback
from .types import Coord, LocalBias

REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_DIR = REPO_ROOT / "reports" / "grid2d_blackboard_bimodality"
OUT_JSON = REPORT_DIR / "data" / "Z_scan.json"


def _sticky_belt(alpha: float, *, n: int = 60) -> Dict[Coord, float]:
    sticky: Dict[Coord, float] = {}
    for x in range(1, n + 1):
        sticky[(x, 1)] = alpha
        sticky[(x, n)] = alpha
    for y in range(1, n + 1):
        sticky[(1, y)] = alpha
        sticky[(n, y)] = alpha
    return sticky


def _clockwise_bias(delta: float, *, n: int = 60) -> LocalBias:
    bias: LocalBias = {}
    for x in range(1, n):
        bias[(x, 1)] = ("R", delta)
    for y in range(1, n):
        bias[(n, y)] = ("D", delta)
    for x in range(2, n + 1):
        bias[(x, n)] = ("L", delta)
    for y in range(2, n + 1):
        bias[(1, y)] = ("U", delta)
    return bias


def _corridor_bias(
    *,
    delta_core: float,
    delta_open: float,
    y0: int = 15,
    y1: int = 45,
) -> LocalBias:
    local_bias: LocalBias = {}
    for x in range(29, 32):
        for y in range(y0, y1 + 1):
            local_bias[(x, y)] = ("U", delta_core)
    for x in range(29, 32):
        for y in range(y1 + 1, 51):
            local_bias[(x, y)] = ("U", delta_open)
        for y in range(10, y0):
            local_bias[(x, y)] = ("U", delta_open)
    return local_bias


def _merge_bias(base: LocalBias, extra: LocalBias | None) -> LocalBias:
    if not extra:
        return dict(base)
    merged = dict(base)
    merged.update(extra)
    return merged


def _variant_case(
    *,
    gx: float,
    gy: float,
    delta_core: float,
    delta_open: float,
    t_max: int,
    sticky: Dict[Coord, float] | None = None,
    boundary_bias: LocalBias | None = None,
) -> CaseDef:
    base = build_z()
    return replace(
        base,
        gx=float(gx),
        gy=float(gy),
        t_max=int(t_max),
        local_bias=_merge_bias(
            _corridor_bias(delta_core=delta_core, delta_open=delta_open),
            boundary_bias,
        ),
        sticky=dict(sticky or {}),
    )


def main() -> None:
    io_helpers.ensure_report_dirs(REPORT_DIR)

    variants = [
        {
            "variant_id": "Z0",
            "label": "base",
            "gx": 0.0,
            "gy": -0.2,
            "delta_core": 0.95,
            "delta_open": 0.6,
            "t_max": 3000,
            "sticky": None,
            "boundary_bias": None,
            "sticky_alpha": None,
            "boundary_bias_delta": None,
        },
        {
            "variant_id": "Z1",
            "label": "no global bias",
            "gx": 0.0,
            "gy": 0.0,
            "delta_core": 0.95,
            "delta_open": 0.6,
            "t_max": 3000,
            "sticky": None,
            "boundary_bias": None,
            "sticky_alpha": None,
            "boundary_bias_delta": None,
        },
        {
            "variant_id": "Z2",
            "label": "strong global bias",
            "gx": 0.0,
            "gy": -0.4,
            "delta_core": 0.95,
            "delta_open": 0.6,
            "t_max": 3000,
            "sticky": None,
            "boundary_bias": None,
            "sticky_alpha": None,
            "boundary_bias_delta": None,
        },
        {
            "variant_id": "Z3",
            "label": "weaker opening bias",
            "gx": 0.0,
            "gy": -0.2,
            "delta_core": 0.95,
            "delta_open": 0.2,
            "t_max": 3000,
            "sticky": None,
            "boundary_bias": None,
            "sticky_alpha": None,
            "boundary_bias_delta": None,
        },
        {
            "variant_id": "Z4",
            "label": "sticky belt",
            "gx": 0.0,
            "gy": -0.2,
            "delta_core": 0.95,
            "delta_open": 0.6,
            "t_max": 3000,
            "sticky": _sticky_belt(0.2),
            "boundary_bias": None,
            "sticky_alpha": 0.2,
            "boundary_bias_delta": None,
        },
        {
            "variant_id": "Z5",
            "label": "sticky belt + clockwise bias",
            "gx": 0.0,
            "gy": -0.2,
            "delta_core": 0.95,
            "delta_open": 0.6,
            "t_max": 3000,
            "sticky": _sticky_belt(0.2),
            "boundary_bias": _clockwise_bias(0.1),
            "sticky_alpha": 0.2,
            "boundary_bias_delta": 0.1,
        },
        {
            "variant_id": "Z6",
            "label": "strong sticky belt + clockwise bias",
            "gx": 0.0,
            "gy": -0.2,
            "delta_core": 0.95,
            "delta_open": 0.6,
            "t_max": 3000,
            "sticky": _sticky_belt(0.05),
            "boundary_bias": _clockwise_bias(0.1),
            "sticky_alpha": 0.05,
            "boundary_bias_delta": 0.1,
        },
    ]

    results = []
    for variant in variants:
        case = _variant_case(
            gx=variant["gx"],
            gy=variant["gy"],
            delta_core=variant["delta_core"],
            delta_open=variant["delta_open"],
            t_max=variant["t_max"],
            sticky=variant["sticky"],
            boundary_bias=variant["boundary_bias"],
        )
        spec = case_to_spec(
            case,
            dir_map=DIR_MAP,
            build_barriers=build_barriers,
            include_extra_barriers=True,
        )
        cfg = spec_to_internal(spec)
        f_exact, p_abs = exact_fpt(cfg, t_max=case.t_max)
        metrics, mode = compute_metrics_with_fallback(
            f_exact,
            t_max=case.t_max,
            peak_smooth_window=9,
            min_gap=20,
        )
        results.append(
            {
                "variant_id": variant["variant_id"],
                "label": variant["label"],
                "gx": variant["gx"],
                "gy": variant["gy"],
                "delta_core": variant["delta_core"],
                "delta_open": variant["delta_open"],
                "sticky_alpha": variant["sticky_alpha"],
                "boundary_bias_delta": variant["boundary_bias_delta"],
                "t_max": case.t_max,
                "absorption": float(p_abs),
                "t_p1": int(metrics["t_p1"]),
                "t_v": int(metrics["t_v"]),
                "t_p2": int(metrics["t_p2"]),
                "valley_ratio": float(metrics.get("valley_ratio", 1.0)),
                "gap": int(metrics.get("gap", 0)),
                "bimodal": bool(metrics.get("bimodal", False)),
                "method": str(metrics.get("method", mode)),
            }
        )

    OUT_JSON.write_text(
        json.dumps({"variants": results}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
