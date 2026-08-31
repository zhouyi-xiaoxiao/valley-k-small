#!/usr/bin/env python3
"""Strict v4 reducer with exact 480-allocation/48-cell Slurm accounting."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import reduce_gpu_gating_v3 as _core

MANIFEST_SCHEMA = "grid2d-one-two-target-gating-gpu-v4-manifest"
RESULT_SCHEMA = "grid2d-one-two-target-gating-fixed-mean-gpu-v4"
REDUCTION_SCHEMA = "grid2d-one-two-target-gating-gpu-v4-reduction-v1"


def _validate_sacct_v4(path: Path | None, cells: Sequence[Any]) -> dict[str, Any]:
    _core._require(path is not None and path.is_file() and not path.is_symlink(), "v4 sacct receipt is mandatory and must be a regular file")
    _core._require(len(cells) == 23040, "v4 reducer requires exactly 23,040 validated cells")
    groups: dict[tuple[str, str, int], list[Any]] = {}
    for cell in cells:
        array = cell.slurm_array_job_id; task = cell.slurm_array_task_id; job = cell.slurm_job_id
        _core._require(isinstance(array, str) and array.isdigit(), f"cell {cell.config.cell_id} invalid array id")
        _core._require(isinstance(task, str) and task.isdigit() and 0 <= int(task) < 480, f"cell {cell.config.cell_id} invalid task id")
        _core._require(isinstance(job, str) and job.isdigit(), f"cell {cell.config.cell_id} invalid allocation id")
        groups.setdefault((array, job, int(task)), []).append(cell)
    _core._require(len(groups) == 480, "v4 must contain 480 unique allocations")
    _core._require(len({key[0] for key in groups}) == 1, "v4 must originate from one array job")
    _core._require({key[2] for key in groups} == set(range(480)), "v4 tasks must be exactly 0..479")
    for key, group in groups.items():
        task = key[2]
        expected = {task + 480 * (g + 4 * k) for g in range(4) for k in range(12)}
        actual = {item.config.cell_id for item in group}
        _core._require(len(group) == 48 and actual == expected, f"task {task} exact 48-cell mapping drift")
    aliases: dict[str, tuple[str, str, int]] = {}
    for key in groups:
        array, job, task = key
        for alias in (job, f"{array}_{task}"):
            _core._require(alias not in aliases or aliases[alias] == key, f"ambiguous Slurm alias {alias}")
            aliases[alias] = key
    matches: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    parent = {key[0] for key in groups}
    for record in _core._parse_sacct(path):
        identifiers = {str(v) for v in (_core._record_value(record, "JobIDRaw"), _core._record_value(record, "JobID")) if v not in (None, "")}
        identifiers = {v for v in identifiers if "." not in v and (v not in parent or "_" in v)}
        found = {aliases[v] for v in identifiers if v in aliases}
        _core._require(len(found) <= 1, "ambiguous sacct row")
        if not found:
            continue
        key = next(iter(found))
        _core._require(key not in matches, f"duplicate sacct row for task {key[2]}")
        state = str(_core._record_value(record, "State") or "").split("+")[0]
        exit_code = str(_core._record_value(record, "ExitCode") or "")
        _core._require(state == "COMPLETED" and exit_code == "0:0", f"task {key[2]} is not COMPLETED/0:0")
        matches[key] = record
    _core._require(set(matches) == set(groups), f"sacct coverage is {len(matches)}/480")
    return {"provided": True, "verified": True, "receipt_filename": path.name, "receipt_sha256": _core._sha256_file(path), "allocations_verified": 480, "cells_verified": 23040, "cells_per_allocation": 48, "bundled_production": True, "full_node_gpus": 4}


def main(argv: Sequence[str] | None = None) -> int:
    _core.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    _core.RESULT_SCHEMA = RESULT_SCHEMA
    _core.REDUCTION_SCHEMA = REDUCTION_SCHEMA
    _core._validate_sacct = _validate_sacct_v4
    args = _core._parse_args(argv)
    try:
        payload = _core.reduce_campaign(manifest_path=args.manifest, field_pack_path=args.field_pack, results_dir=args.results_dir, source_path=args.source or Path(__file__).with_name("gpu_gating_mc_v4.py"), sacct_receipt=args.sacct_receipt, output_json=args.output_json, output_csv=args.output_csv, mode=args.mode)
    except _core.AuditError as exc:
        print(f"FAIL-CLOSED: {exc}", file=sys.stderr); return 2
    print(json.dumps({"status": "PASS", "cells": payload["audit"]["cell_count"], "sacct": payload["audit"]["sacct"]["verified"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
