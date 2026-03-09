from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Sequence

from .types import Coord, Edge


def ensure_report_dirs(report_dir: Path) -> dict[str, Path]:
    fig_root = report_dir / "figures"
    fig_dirs = {
        "env": fig_root / "env",
        "fig3_panels": fig_root / "fig3_panels",
        "paths": fig_root / "paths",
        "fpt": fig_root / "fpt",
        "channel_decomp": fig_root / "channel_decomp",
    }
    for path in fig_dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    (report_dir / "data").mkdir(parents=True, exist_ok=True)
    (report_dir / "outputs").mkdir(parents=True, exist_ok=True)
    (report_dir / "config").mkdir(parents=True, exist_ok=True)
    return fig_dirs


def write_case_config(
    case,
    config_dir: Path,
    *,
    config_filenames: dict[str, str],
    build_barriers: Callable[[set[Coord], int], Sequence[Edge]],
    include_extra_barriers: bool = False,
) -> Path:
    barriers = set(build_barriers(case.allowed, case.N))
    if include_extra_barriers:
        barriers.update(getattr(case, "extra_barriers", set()))

    local_bias_list = [
        {"x": x, "y": y, "dir": d, "delta": float(delta)}
        for (x, y), (d, delta) in case.local_bias.items()
    ]
    local_bias_list.sort(key=lambda item: (item["y"], item["x"]))

    sticky_list = [
        {"x": x, "y": y, "factor": float(f)} for (x, y), f in case.sticky.items()
    ]
    sticky_list.sort(key=lambda item: (item["y"], item["x"]))

    doors_list = [
        {"a": [a[0], a[1]], "b": [b[0], b[1]], "p_pass": float(p)}
        for (a, b), p in sorted(case.doors.items(), key=lambda item: (item[0][0][1], item[0][0][0]))
    ]
    barriers_list = [
        {"a": [a[0], a[1]], "b": [b[0], b[1]]}
        for (a, b) in sorted(barriers, key=lambda e: (e[0][1], e[0][0], e[1][1], e[1][0]))
    ]

    payload = {
        "name": case.name,
        "N": case.N,
        "q": case.q,
        "gx": case.gx,
        "gy": case.gy,
        "boundary": "reflecting",
        "start": [case.start[0], case.start[1]],
        "target": [case.target[0], case.target[1]],
        "local_bias": local_bias_list,
        "sticky": sticky_list,
        "doors": doors_list,
        "barriers": barriers_list,
    }

    filename = config_filenames.get(case.case_id, f"{case.case_id}_config.json")
    path = config_dir / filename
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_metrics_payload(
    report_dir: Path,
    *,
    case,
    metrics: dict,
    absorption_prob: float,
    aw_params: dict,
    aw_err: dict,
    mc_stats: dict,
) -> Path:
    payload = {
        "case_id": case.case_id,
        "name": case.name,
        "params": {
            "N": case.N,
            "q": case.q,
            "g_x": case.gx,
            "g_y": case.gy,
            "start": list(case.start),
            "target": list(case.target),
        },
        "metrics": metrics,
        "absorption_prob": float(absorption_prob),
        "aw": {"params": aw_params, "errors": aw_err},
        "mc": mc_stats,
    }
    out = report_dir / "data" / f"{case.case_id}_metrics.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out


__all__ = [
    "ensure_report_dirs",
    "write_case_config",
    "write_metrics_payload",
]
