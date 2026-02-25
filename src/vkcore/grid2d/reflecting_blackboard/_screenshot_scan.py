#!/usr/bin/env python3
"""Small parameter scan for screenshot-style corridor settings."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from vkcore.grid2d.bimod_legacy_imports import exact_fpt
from vkcore.grid2d.model_core_reflecting import spec_to_internal

from . import io as io_helpers
from .cases_blackboard import DIR_MAP, CaseDef, build_barriers, build_x
from .model import case_to_spec
from .scans import compute_metrics_with_fallback
from .types import LocalBias

REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_DIR = REPO_ROOT / "reports" / "grid2d_blackboard_bimodality"
OUT_JSON = REPORT_DIR / "outputs" / "screenshot_scan.json"


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


def _variant_case(*, g_y: float, delta_core: float, delta_open: float, t_max: int) -> CaseDef:
    base = build_x()
    return replace(
        base,
        gy=float(g_y),
        t_max=int(t_max),
        local_bias=_corridor_bias(delta_core=delta_core, delta_open=delta_open),
    )


def _project_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    # Keep key shape stable for downstream notebooks that consume screenshot_scan.json.
    out: dict[str, Any] = {
        "t_p1": int(metrics["t_p1"]),
        "t_p2": int(metrics["t_p2"]),
        "t_v": int(metrics["t_v"]),
        "h1": float(metrics["h1"]),
        "h2": float(metrics["h2"]),
        "hv": float(metrics["hv"]),
        "peak_ratio": float(metrics.get("peak_ratio", 0.0)),
        "valley_ratio": float(metrics.get("valley_ratio", 1.0)),
        "gap": int(metrics.get("gap", 0)),
        "smooth_window": int(metrics.get("smooth_window", 0)),
        "bimodal": bool(metrics.get("bimodal", False)),
        "passes": bool(metrics.get("passes", False)),
    }
    if "early_window" in metrics:
        out["early_window"] = metrics["early_window"]
    if "late_window" in metrics:
        out["late_window"] = metrics["late_window"]
    return out


def main() -> None:
    io_helpers.ensure_report_dirs(REPORT_DIR)

    t_max = 4000
    records = []
    for g_y in (-0.4, -0.2, 0.0):
        for delta_core in (0.6, 0.8, 0.95):
            for delta_open in (0.3, 0.6):
                case = _variant_case(
                    g_y=g_y,
                    delta_core=delta_core,
                    delta_open=delta_open,
                    t_max=t_max,
                )
                spec = case_to_spec(
                    case,
                    dir_map=DIR_MAP,
                    build_barriers=build_barriers,
                    include_extra_barriers=True,
                )
                cfg = spec_to_internal(spec)
                f_exact, p_abs = exact_fpt(cfg, t_max=t_max)
                metrics, _ = compute_metrics_with_fallback(
                    f_exact,
                    t_max=t_max,
                    peak_smooth_window=9,
                    min_gap=20,
                )
                records.append(
                    {
                        "g_y": g_y,
                        "delta_core": delta_core,
                        "delta_open": delta_open,
                        "absorption_prob": float(p_abs),
                        "metrics": _project_metrics(metrics),
                    }
                )

    OUT_JSON.write_text(
        json.dumps({"t_max": t_max, "records": records}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
