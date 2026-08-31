#!/usr/bin/env python3
"""Fail-closed secondary max-t analysis of the frozen GPU gating v3 reduction.

This program discovers and independently replays all 5,760 raw JSON/NPZ cells
committed before reducer job 5788358, but never mutates upstream artifacts.
All 75 amplitude-versus-zero contrasts share every field-block bootstrap draw,
preserving their joint dependence for simultaneous inference.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


OUTPUT_SCHEMA = "grid2d-one-two-target-gating-secondary-max-t-r1"
CONTRACT_SCHEMA = "grid2d-one-two-target-gating-secondary-analysis-contract-r1"
CSV_FIELDS = (
    "contrast_index",
    "target2_x",
    "target2_y",
    "control_amplitude",
    "treatment_amplitude",
    "n_disorder_blocks",
    "mean_effect",
    "standard_error",
    "observed_t",
    "simultaneous_ci_lower",
    "simultaneous_ci_upper",
    "adjusted_p_value",
)
UPSTREAM_CSV_FIELDS = (
    "row_type",
    "condition_id",
    "comparison_id",
    "profile",
    "disorder_replicate",
    "walk_replicates",
    "steps",
    "target2_x",
    "target2_y",
    "amplitude",
    "gating_probability_drop",
    "gating_probability_drop_t_half",
    "gating_tail_delta",
    "one_unresolved_probability",
    "two_unresolved_probability",
    "diversion_probability",
    "acceleration_probability",
    "target2_first_probability",
    "primary_paired_effect",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
UPSTREAM_ROOT = Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-20260726-r3")
SECONDARY_ROOT = Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-secondary-r1-20260727")
PAYLOAD_MANIFEST_RELATIVE = "notes/isambard_ai_v3_secondary_r1.sha256"
PAYLOAD_MEMBERS = (
    "code/analyze_gpu_gating_v3_secondary_r1.py",
    "code/isambard_ai_gating_v3_secondary_r1.sbatch",
    "code/test_gpu_gating_v3_secondary_r1.py",
    "notes/isambard_ai_v3_secondary_analysis_contract_r1.json",
)


class AuditError(RuntimeError):
    """An integrity or statistical precondition failed closed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _load_json(path: Path, label: str) -> dict[str, Any]:
    _require(path.is_file() and not path.is_symlink(), f"{label} must be a regular non-symlink file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"cannot parse {label}: {exc}") from exc
    _require(isinstance(value, dict), f"{label} root must be an object")
    return value


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{label} must be an object")
    return value


def _integer(value: Any, label: str, *, minimum: int | None = None) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool), f"{label} must be an integer")
    result = int(value)
    if minimum is not None:
        _require(result >= minimum, f"{label} must be at least {minimum}")
    return result


def _number(value: Any, label: str) -> float:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} must be numeric")
    result = float(value)
    _require(math.isfinite(result), f"{label} must be finite")
    return result


def _sha(value: Any, label: str) -> str:
    _require(isinstance(value, str) and HEX64.fullmatch(value) is not None, f"{label} must be lowercase SHA-256")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _expected_contract() -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA,
        "status": "frozen-before-upstream-production-results",
        "roots": {
            "upstream_read_only_root": str(UPSTREAM_ROOT),
            "secondary_write_root": str(SECONDARY_ROOT),
        },
        "payload": {
            "manifest_relative": PAYLOAD_MANIFEST_RELATIVE,
            "manifest_sha256_source": "frozen_sbatch_positional_argument",
        },
        "upstream": {
            "production_array_job_id": "5788357",
            "production_reducer_job_id": "5788358",
            "run_token": "5788353",
            "raw_results_dir_relative": "artifacts/outputs/isambard_ai_v3/production-5788353",
            "reduction_dir_relative": "artifacts/outputs/isambard_ai_v3/reductions/production-5788353-reduce-5788358",
            "reduction_json_filename": "reduction.json",
            "reduction_csv_filename": "reduction.csv",
            "sacct_receipt_filename": "sacct-production-5788353.psv",
            "manifest_relative": "artifacts/data/gating_v3_production_manifest.json",
            "manifest_sha256": "419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f",
            "reduction_schema": "grid2d-one-two-target-gating-gpu-v3-reduction-v1",
            "manifest_schema": "grid2d-one-two-target-gating-gpu-v3-manifest",
            "cell_count": 5760,
            "allocation_count": 480,
            "cells_per_allocation": 12,
            "block_csv_row_count": 2880,
            "primary_csv_row_count": 32,
            "total_csv_row_count": 2912,
        },
        "estimand": {
            "metric": "gating_probability_drop",
            "effect_direction": "amplitude_minus_zero_within_geometry_and_disorder_block",
            "geometry_order": [[x, y] for x in (24, 32, 40) for y in (9, 16, 24, 31, 38)],
            "control_amplitude": 0.0,
            "treatment_amplitudes": [0.05, 0.1, 0.15, 0.2, 0.25],
            "contrast_count": 75,
            "disorder_blocks": 32,
            "walk_replicates_already_averaged": [0, 1],
        },
        "bootstrap": {
            "bit_generator": "PCG64",
            "seed": 20260726,
            "resamples": 10000,
            "joint_resampling_unit": "disorder_field_block_shared_across_all_75_contrasts",
            "studentization": "centered_resample_mean_divided_by_resample_standard_error_ddof_1",
            "maximum_statistic": "maximum_absolute_studentized_statistic_across_75_contrasts",
            "confidence_level": 0.95,
            "critical_order_statistic_one_indexed": 9501,
            "adjusted_p_value": "(1 + count(max_abs_t_resample >= abs(observed_t))) / 10001",
        },
        "integrity": {
            "policy": "fail_closed",
            "require_reducer_audit_pass": True,
            "require_independent_sacct_parse": True,
            "require_sacct_inventory_bijection": True,
            "require_independent_raw_cell_replay": True,
            "require_raw_recomputed_block_match": True,
            "require_exact_manifest_hash": True,
            "require_exact_inventory_digest": True,
            "require_exact_csv_hash_and_row_count": True,
            "reject_missing_duplicate_unexpected_zero_or_nonfinite_values": True,
            "outputs": "atomic_no_overwrite_json_and_csv_under_secondary_write_root_only",
        },
    }


def _fixed_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    expected = _expected_contract()
    observed_canonical = json.dumps(contract, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    expected_canonical = json.dumps(expected, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    _require(observed_canonical == expected_canonical, "contract exact schema/field/value drift")
    upstream = _mapping(contract["upstream"], "contract.upstream")
    geometries = tuple((x, y) for x in (24, 32, 40) for y in (9, 16, 24, 31, 38))
    treatments = (0.05, 0.1, 0.15, 0.2, 0.25)
    return {
        "upstream": upstream,
        "geometries": geometries,
        "treatments": treatments,
        "blocks": 32,
        "resamples": 10000,
        "seed": 20260726,
        "critical_index": 9500,
    }


def _validate_payload_manifest(
    manifest_path: Path, expected_manifest_sha256: str
) -> dict[str, str]:
    expected_sha = _sha(expected_manifest_sha256, "expected payload-manifest SHA")
    _require(
        manifest_path.absolute() == (SECONDARY_ROOT / PAYLOAD_MANIFEST_RELATIVE).absolute(),
        "payload manifest path drift",
    )
    _require(
        manifest_path.is_file() and not manifest_path.is_symlink(),
        "payload manifest missing or symlinked",
    )
    _require(_sha256_file(manifest_path) == expected_sha, "payload manifest SHA-256 drift")
    try:
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise AuditError(f"cannot read payload manifest: {exc}") from exc
    _require(len(lines) == len(PAYLOAD_MEMBERS), "payload manifest member count drift")
    receipts: dict[str, str] = {}
    for index, line in enumerate(lines):
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)", line)
        _require(match is not None, f"malformed payload manifest line {index + 1}")
        digest, relative = match.groups()
        _require(relative not in receipts, f"duplicate payload member {relative}")
        _require(relative == PAYLOAD_MEMBERS[index], "payload manifest order/member drift")
        path = SECONDARY_ROOT / relative
        _require(path.is_file() and not path.is_symlink(), f"payload member missing or symlinked: {relative}")
        _require(_sha256_file(path) == digest, f"payload member SHA-256 drift: {relative}")
        receipts[relative] = digest
    _require(tuple(receipts) == PAYLOAD_MEMBERS, "payload manifest exact inventory drift")
    return receipts


def _validate_manifest(path: Path, fixed: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    upstream = _mapping(fixed["upstream"], "fixed.upstream")
    _require(_sha256_file(path) == upstream["manifest_sha256"], "production manifest SHA-256 drift")
    manifest = _load_json(path, "production manifest")
    _require(manifest.get("schema") == upstream["manifest_schema"], "production manifest schema mismatch")
    campaign = _mapping(manifest.get("campaign"), "manifest.campaign")
    _require(campaign.get("kind") == "production" and campaign.get("cell_count") == 5760, "production campaign identity mismatch")
    cells = manifest.get("cells")
    _require(isinstance(cells, list) and len(cells) == 5760, "manifest must contain 5760 cells")
    defaults = _mapping(manifest.get("defaults"), "manifest.defaults")
    walkers = _integer(defaults.get("walkers"), "manifest walkers", minimum=1)
    steps = _integer(defaults.get("steps"), "manifest steps", minimum=1)
    batch_size = _integer(defaults.get("batch_size"), "manifest batch_size", minimum=1)
    base_hold = _number(defaults.get("base_hold"), "manifest base_hold")
    target_radius = _integer(defaults.get("target_radius"), "manifest target_radius", minimum=1)
    checkpoints_raw = defaults.get("checkpoints")
    _require(isinstance(checkpoints_raw, list), "manifest checkpoints must be an array")
    checkpoints = tuple(_integer(value, "manifest checkpoint", minimum=1) for value in checkpoints_raw)
    _require(checkpoints[-1] == steps and steps // 2 in checkpoints, "manifest checkpoint schedule drift")
    observed: set[tuple[int, int, float, int, int]] = set()
    ids: set[int] = set()
    configs: dict[int, dict[str, Any]] = {}
    for index, raw in enumerate(cells):
        cell = _mapping(raw, f"manifest.cells[{index}]")
        _require(
            set(cell)
            == {
                "amplitude",
                "cell_id",
                "disorder_replicate",
                "target2_x",
                "target2_y",
                "walk_replicate",
            },
            f"manifest cell {index} fields drift",
        )
        cell_id = _integer(cell.get("cell_id"), "manifest cell_id", minimum=0)
        ids.add(cell_id)
        identity = (
            _integer(cell.get("target2_x"), "manifest target2_x"),
            _integer(cell.get("target2_y"), "manifest target2_y"),
            _number(cell.get("amplitude"), "manifest amplitude"),
            _integer(cell.get("disorder_replicate"), "manifest disorder", minimum=0),
            _integer(cell.get("walk_replicate"), "manifest walk", minimum=0),
        )
        _require(identity not in observed, f"duplicate manifest identity {identity}")
        observed.add(identity)
        configs[cell_id] = {
            "cell_id": cell_id,
            "target2_x": identity[0],
            "target2_y": identity[1],
            "amplitude": identity[2],
            "disorder_replicate": identity[3],
            "walk_replicate": identity[4],
            "walkers": walkers,
            "steps": steps,
            "batch_size": batch_size,
            "base_hold": base_hold,
            "target_radius": target_radius,
            "checkpoints": checkpoints,
        }
    expected = {
        (x, y, amplitude, block, walk)
        for x, y in fixed["geometries"]
        for amplitude in (0.0, *fixed["treatments"])
        for block in range(32)
        for walk in (0, 1)
    }
    _require(ids == set(range(5760)), "manifest cell IDs are not exactly 0..5759")
    _require(observed == expected, "manifest scientific cell inventory drift")
    return configs


def _inventory_digest(
    inventory: list[Any], upstream: Mapping[str, Any]
) -> tuple[str, dict[int, str], dict[int, dict[str, Any]]]:
    _require(len(inventory) == 5760, "reduction inventory must contain 5760 cells")
    lines: list[str] = []
    ids: set[int] = set()
    cells_by_task: dict[int, set[int]] = {task: set() for task in range(480)}
    allocations_by_task: dict[int, set[str]] = {task: set() for task in range(480)}
    inventory_by_id: dict[int, dict[str, Any]] = {}
    for index, raw in enumerate(inventory):
        row = _mapping(raw, f"inventory[{index}]")
        cell_id = _integer(row.get("cell_id"), "inventory cell_id", minimum=0)
        _require(cell_id == index, "reduction inventory is not in canonical cell-id order")
        _require(cell_id not in ids, f"duplicate inventory cell {cell_id}")
        ids.add(cell_id)
        inventory_by_id[cell_id] = dict(row)
        for key in ("json_path", "npz_path"):
            value = row.get(key)
            _require(isinstance(value, str) and value and not value.startswith("/") and ".." not in Path(value).parts, f"unsafe inventory {key}")
        _require(row.get("json_path") == f"cell-{cell_id}/cell-{cell_id}.json", "noncanonical inventory JSON path")
        _require(row.get("npz_path") == f"cell-{cell_id}/cell-{cell_id}.npz", "noncanonical inventory NPZ path")
        json_sha = _sha(row.get("json_sha256"), "inventory json SHA")
        npz_sha = _sha(row.get("npz_sha256"), "inventory npz SHA")
        _require(row.get("slurm_array_job_id") == upstream["production_array_job_id"], "inventory array job drift")
        task = row.get("slurm_array_task_id")
        job = row.get("slurm_job_id")
        _require(isinstance(task, str) and task.isdigit() and int(task) == cell_id % 480, "inventory array task mapping drift")
        _require(isinstance(job, str) and job.isdigit(), "inventory SLURM_JOB_ID invalid")
        task_id = int(task)
        cells_by_task[task_id].add(cell_id)
        allocations_by_task[task_id].add(job)
        lines.append(f"{cell_id}\t{row['json_path']}\t{json_sha}\t{row['npz_path']}\t{npz_sha}\n")
    _require(ids == set(range(5760)), "inventory cell IDs are not exactly 0..5759")
    task_allocations: dict[int, str] = {}
    for task in range(480):
        expected_cells = {task + 480 * bundle for bundle in range(12)}
        _require(cells_by_task[task] == expected_cells, f"inventory task {task} bundle mapping drift")
        _require(len(allocations_by_task[task]) == 1, f"inventory task {task} spans allocations")
        task_allocations[task] = next(iter(allocations_by_task[task]))
    _require(len(set(task_allocations.values())) == 480, "inventory allocations are not 480 unique IDs")
    return (
        _sha256_bytes("".join(lines).encode("utf-8")),
        task_allocations,
        inventory_by_id,
    )


def _independent_sacct_audit(
    path: Path, task_allocations: Mapping[int, str], upstream: Mapping[str, Any]
) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise AuditError(f"cannot read sacct receipt: {exc}") from exc
    _require(raw.strip() != "", "sacct receipt is empty")
    parsed = list(csv.reader(raw.splitlines(), delimiter="|"))
    normalized = [row[:-1] if row and row[-1] == "" else row for row in parsed]
    _require(bool(normalized), "sacct receipt has no rows")
    _require(normalized[0] == ["JobIDRaw", "JobID", "State", "ExitCode"], "sacct header drift")
    array_job_id = str(upstream["production_array_job_id"])
    receipt_tasks: dict[int, str] = {}
    receipt_allocations: set[str] = set()
    parent_rows = 0
    for row_index, row in enumerate(normalized[1:], start=2):
        _require(len(row) == 4, f"sacct row {row_index} field count drift")
        job_id_raw, job_id, state, exit_code = row
        _require(job_id_raw.isdigit(), f"sacct row {row_index} JobIDRaw is not decimal")
        if job_id == array_job_id and job_id_raw == array_job_id:
            parent_rows += 1
            _require(parent_rows == 1, "duplicate sacct array-parent row")
            _require(state == "COMPLETED" and exit_code == "0:0", "sacct array parent did not complete 0:0")
            continue
        match = re.fullmatch(re.escape(array_job_id) + r"_([0-9]+)", job_id)
        _require(match is not None, f"unexpected sacct JobID {job_id!r}")
        task = int(match.group(1))
        _require(0 <= task < 480, f"sacct task {task} outside 0..479")
        _require(task not in receipt_tasks, f"duplicate sacct task {task}")
        _require(state == "COMPLETED", f"sacct task {task} state is not exactly COMPLETED")
        _require(exit_code == "0:0", f"sacct task {task} exit code is not 0:0")
        expected_allocation = task_allocations.get(task)
        _require(expected_allocation is not None, f"sacct task {task} has no inventory allocation")
        _require(job_id_raw == expected_allocation, f"sacct/inventory allocation mismatch for task {task}")
        _require(job_id_raw not in receipt_allocations, f"duplicate sacct allocation {job_id_raw}")
        receipt_tasks[task] = job_id_raw
        receipt_allocations.add(job_id_raw)
    _require(set(receipt_tasks) == set(range(480)), "sacct tasks are not exactly 0..479")
    _require(len(receipt_allocations) == 480, "sacct does not contain 480 unique allocations")
    _require(dict(receipt_tasks) == dict(task_allocations), "sacct/inventory task-allocation bijection drift")
    _require(receipt_allocations == set(task_allocations.values()), "sacct/inventory allocation reverse mapping drift")
    mapping_digest = _sha256_bytes(
        "".join(f"{task}\t{receipt_tasks[task]}\n" for task in range(480)).encode("utf-8")
    )
    return {
        "independently_verified": True,
        "array_job_id": array_job_id,
        "tasks_verified": 480,
        "task_range": [0, 479],
        "unique_allocations": 480,
        "cells_per_allocation": 12,
        "bundle_mapping": "cell_id=task+480*k for k=0..11",
        "state": "COMPLETED",
        "exit_code": "0:0",
        "parent_row_present": parent_rows == 1,
        "task_allocation_mapping_sha256": mapping_digest,
    }


def _discover_raw_pairs(
    raw_root: Path, expected_ids: set[int]
) -> dict[int, tuple[Path, Path]]:
    _require(raw_root.is_dir() and not raw_root.is_symlink(), "raw production root missing or symlinked")
    pairs: dict[int, tuple[Path, Path]] = {}
    observed_names: set[str] = set()
    observed_inodes: set[tuple[int, int]] = set()
    for child in raw_root.iterdir():
        _require(child.is_dir() and not child.is_symlink(), f"unexpected raw-root member {child.name}")
        match = re.fullmatch(r"cell-([0-9]+)", child.name)
        _require(match is not None, f"noncanonical raw cell directory {child.name}")
        cell_id = int(match.group(1))
        _require(cell_id in expected_ids, f"unexpected raw cell ID {cell_id}")
        _require(child.name not in observed_names and cell_id not in pairs, f"duplicate raw cell {cell_id}")
        observed_names.add(child.name)
        members = list(child.iterdir())
        expected_names = {f"cell-{cell_id}.json", f"cell-{cell_id}.npz"}
        _require({member.name for member in members} == expected_names, f"raw cell {cell_id} member inventory drift")
        _require(
            all(member.is_file() and not member.is_symlink() for member in members),
            f"raw cell {cell_id} contains non-regular or symlinked members",
        )
        for member in members:
            stat = member.stat()
            _require(stat.st_nlink == 1, f"raw artifact has external or internal hardlinks: {member}")
            inode = (stat.st_dev, stat.st_ino)
            _require(inode not in observed_inodes, f"raw artifact hardlink/duplicate inode at {member}")
            observed_inodes.add(inode)
        pairs[cell_id] = (
            child / f"cell-{cell_id}.json",
            child / f"cell-{cell_id}.npz",
        )
    _require(set(pairs) == expected_ids, "raw cell directory inventory is missing or incomplete")
    return pairs


def _replay_one_raw_cell(
    *,
    json_path: Path,
    npz_path: Path,
    config: Mapping[str, Any],
    inventory: Mapping[str, Any],
    manifest_sha256: str,
    array_job_id: str,
) -> tuple[float, str, str]:
    cell_id = int(config["cell_id"])
    json_sha = _sha256_file(json_path)
    npz_sha = _sha256_file(npz_path)
    _require(json_sha == inventory.get("json_sha256"), f"raw cell {cell_id} JSON hash/inventory mismatch")
    _require(npz_sha == inventory.get("npz_sha256"), f"raw cell {cell_id} NPZ hash/inventory mismatch")
    payload = _load_json(json_path, f"raw cell {cell_id} JSON")
    _require(payload.get("schema") == "grid2d-one-two-target-gating-fixed-mean-gpu-v3", f"raw cell {cell_id} schema drift")
    manifest = _mapping(payload.get("manifest"), f"raw cell {cell_id}.manifest")
    _require(
        set(manifest) == {"filename", "sha256", "schema", "cell_id", "profile"},
        f"raw cell {cell_id} manifest fields drift",
    )
    _require(manifest.get("filename") == "gating_v3_production_manifest.json", f"raw cell {cell_id} manifest filename drift")
    _require(manifest.get("sha256") == manifest_sha256, f"raw cell {cell_id} manifest SHA drift")
    _require(manifest.get("schema") == "grid2d-one-two-target-gating-gpu-v3-manifest", f"raw cell {cell_id} manifest schema drift")
    _require(manifest.get("cell_id") == cell_id and manifest.get("profile") is None, f"raw cell {cell_id} manifest identity drift")

    parameters = _mapping(payload.get("parameters"), f"raw cell {cell_id}.parameters")
    expected_parameters = {
        "walkers": config["walkers"],
        "steps": config["steps"],
        "batch_size": config["batch_size"],
        "base_hold": config["base_hold"],
        "amplitude": config["amplitude"],
        "target_radius": config["target_radius"],
        "disorder_replicate": config["disorder_replicate"],
        "walk_replicate": config["walk_replicate"],
        "checkpoints": list(config["checkpoints"]),
    }
    for key, expected in expected_parameters.items():
        _require(parameters.get(key) == expected, f"raw cell {cell_id} parameter {key} drift")
    _require(isinstance(parameters.get("disorder_seed"), int) and not isinstance(parameters.get("disorder_seed"), bool), f"raw cell {cell_id} disorder seed invalid")

    domain = _mapping(payload.get("domain"), f"raw cell {cell_id}.domain")
    target2 = _mapping(domain.get("target2"), f"raw cell {cell_id}.domain.target2")
    _require(
        target2.get("x") == config["target2_x"] and target2.get("y") == config["target2_y"],
        f"raw cell {cell_id} geometry drift",
    )
    provenance = _mapping(payload.get("provenance"), f"raw cell {cell_id}.provenance")
    slurm = _mapping(provenance.get("slurm"), f"raw cell {cell_id}.provenance.slurm")
    expected_task = str(cell_id % 480)
    _require(slurm.get("SLURM_ARRAY_JOB_ID") == array_job_id, f"raw cell {cell_id} array job drift")
    _require(slurm.get("SLURM_ARRAY_TASK_ID") == expected_task, f"raw cell {cell_id} array task drift")
    _require(slurm.get("SLURM_JOB_ID") == inventory.get("slurm_job_id"), f"raw cell {cell_id} allocation drift")
    _require(inventory.get("slurm_array_task_id") == expected_task, f"raw cell {cell_id} inventory task drift")

    histograms = _mapping(payload.get("histograms"), f"raw cell {cell_id}.histograms")
    _require(histograms.get("path") == npz_path.name, f"raw cell {cell_id} NPZ filename drift")
    _require(histograms.get("sha256") == npz_sha, f"raw cell {cell_id} JSON/NPZ hash mismatch")
    gates = _mapping(payload.get("gates"), f"raw cell {cell_id}.gates")
    _require(gates.get("all_passed") is True, f"raw cell {cell_id} runner gates did not pass")

    try:
        with np.load(npz_path, allow_pickle=False) as archive:
            expected_keys = {
                "schema_version",
                "one_target1_fpt_histogram",
                "two_target1_fpt_histogram",
                "two_target2_fpt_histogram",
                "checkpoint_steps",
                "checkpoint_counts",
                "paired_outcome_counts",
            }
            _require(set(archive.files) == expected_keys, f"raw cell {cell_id} NPZ keys drift")
            arrays = {key: np.asarray(archive[key]) for key in expected_keys}
    except (OSError, ValueError, EOFError) as exc:
        raise AuditError(f"cannot parse raw cell {cell_id} NPZ: {exc}") from exc
    steps = int(config["steps"])
    checkpoints = tuple(config["checkpoints"])
    expected_shapes = {
        "schema_version": (),
        "one_target1_fpt_histogram": (steps + 1,),
        "two_target1_fpt_histogram": (steps + 1,),
        "two_target2_fpt_histogram": (steps + 1,),
        "checkpoint_steps": (len(checkpoints),),
        "checkpoint_counts": (len(checkpoints), 6),
        "paired_outcome_counts": (3, 3),
    }
    for key, array in arrays.items():
        _require(array.dtype == np.dtype(np.int64), f"raw cell {cell_id} {key} dtype is not int64")
        _require(array.shape == expected_shapes[key], f"raw cell {cell_id} {key} shape drift")
        _require(bool(np.all(array >= 0)), f"raw cell {cell_id} {key} contains negative counts")
    _require(int(arrays["schema_version"]) == 3, f"raw cell {cell_id} NPZ schema_version is not 3")
    checkpoint_steps = arrays["checkpoint_steps"]
    checkpoint_counts = arrays["checkpoint_counts"]
    paired = arrays["paired_outcome_counts"]
    one_hist = arrays["one_target1_fpt_histogram"]
    two_hist1 = arrays["two_target1_fpt_histogram"]
    two_hist2 = arrays["two_target2_fpt_histogram"]
    walkers = int(config["walkers"])
    for key in (
        "one_target1_fpt_histogram",
        "two_target1_fpt_histogram",
        "two_target2_fpt_histogram",
        "checkpoint_counts",
        "paired_outcome_counts",
    ):
        _require(bool(np.all(arrays[key] <= walkers)), f"raw cell {cell_id} {key} exceeds walker mass")
    _require(checkpoint_steps.tolist() == list(checkpoints), f"raw cell {cell_id} checkpoint steps drift")
    _require(
        bool(np.all(checkpoint_counts[:, 0] + checkpoint_counts[:, 1] == walkers)),
        f"raw cell {cell_id} one-target checkpoint mass drift",
    )
    _require(
        bool(
            np.all(
                checkpoint_counts[:, 2]
                + checkpoint_counts[:, 3]
                + checkpoint_counts[:, 4]
                == walkers
            )
        )
        and bool(np.all(checkpoint_counts[:, 5] == walkers)),
        f"raw cell {cell_id} two-target checkpoint mass drift",
    )
    _require(int(paired.sum(dtype=np.int64)) == walkers, f"raw cell {cell_id} paired mass drift")
    _require(int(paired[0, 1]) == 0 and bool(np.all(paired[2, :] == 0)), f"raw cell {cell_id} paired subset/state drift")
    one_hits = int(one_hist.sum(dtype=np.int64))
    two_hits1 = int(two_hist1.sum(dtype=np.int64))
    two_hits2 = int(two_hist2.sum(dtype=np.int64))
    _require(one_hits == int(paired[1, :].sum(dtype=np.int64)), f"raw cell {cell_id} one-hit mass drift")
    _require(two_hits1 == int(paired[:, 1].sum(dtype=np.int64)), f"raw cell {cell_id} two-target1 mass drift")
    _require(two_hits2 == int(paired[:, 2].sum(dtype=np.int64)), f"raw cell {cell_id} two-target2 mass drift")
    final = checkpoint_counts[-1].tolist()
    _require(
        final == [one_hits, walkers - one_hits, two_hits1, two_hits2, walkers - two_hits1 - two_hits2, walkers],
        f"raw cell {cell_id} final checkpoint mass drift",
    )
    _require(int(one_hist[: checkpoints[-1] + 1].sum(dtype=np.int64)) == one_hits, f"raw cell {cell_id} one histogram drift")
    _require(int(two_hist1[: checkpoints[-1] + 1].sum(dtype=np.int64)) == two_hits1, f"raw cell {cell_id} two-target1 histogram drift")
    metric = (one_hits - two_hits1) / walkers
    reported = _number(payload.get("gating_probability_drop"), f"raw cell {cell_id} gating_probability_drop")
    _require(reported == metric, f"raw cell {cell_id} JSON gating value differs from NPZ replay")
    return metric, json_sha, npz_sha


def _independent_raw_replay(
    *,
    raw_root: Path,
    configs: Mapping[int, Mapping[str, Any]],
    inventory_by_id: Mapping[int, Mapping[str, Any]],
    upstream: Mapping[str, Any],
) -> tuple[
    dict[tuple[int, int, float, int], float],
    dict[str, Any],
]:
    expected_ids = set(range(5760))
    _require(set(configs) == expected_ids and set(inventory_by_id) == expected_ids, "raw replay input inventory drift")
    pairs = _discover_raw_pairs(raw_root, expected_ids)
    streams: dict[tuple[int, int, float, int], dict[int, float]] = {}
    raw_lines: list[str] = []
    for cell_id in range(5760):
        json_path, npz_path = pairs[cell_id]
        inventory = inventory_by_id[cell_id]
        _require(inventory.get("json_path") == json_path.relative_to(raw_root).as_posix(), f"raw cell {cell_id} JSON path/inventory drift")
        _require(inventory.get("npz_path") == npz_path.relative_to(raw_root).as_posix(), f"raw cell {cell_id} NPZ path/inventory drift")
        metric, json_sha, npz_sha = _replay_one_raw_cell(
            json_path=json_path,
            npz_path=npz_path,
            config=configs[cell_id],
            inventory=inventory,
            manifest_sha256=str(upstream["manifest_sha256"]),
            array_job_id=str(upstream["production_array_job_id"]),
        )
        config = configs[cell_id]
        key = (
            int(config["target2_x"]),
            int(config["target2_y"]),
            float(config["amplitude"]),
            int(config["disorder_replicate"]),
        )
        walk = int(config["walk_replicate"])
        by_walk = streams.setdefault(key, {})
        _require(walk not in by_walk, f"raw replay duplicate walk stream at {key}")
        by_walk[walk] = metric
        raw_lines.append(f"{cell_id}\t{json_sha}\t{npz_sha}\n")
    block_means: dict[tuple[int, int, float, int], float] = {}
    for key in sorted(streams):
        _require(set(streams[key]) == {0, 1}, f"raw replay walk inventory drift at {key}")
        block_means[key] = math.fsum((streams[key][0], streams[key][1])) / 2.0
    _require(len(block_means) == 2880, "raw replay did not produce exactly 2880 block means")
    block_digest = _sha256_bytes(
        "".join(
            f"{x}\t{y}\t{amplitude.hex()}\t{block}\t{value.hex()}\n"
            for (x, y, amplitude, block), value in sorted(block_means.items())
        ).encode("utf-8")
    )
    return block_means, {
        "independently_verified": True,
        "raw_cells": 5760,
        "json_npz_pairs": 5760,
        "block_means": 2880,
        "raw_inventory_digest": _sha256_bytes("".join(raw_lines).encode("utf-8")),
        "recomputed_block_digest": block_digest,
    }


def _validate_reduction(
    reduction_json: Path,
    reduction_csv: Path,
    sacct_receipt: Path,
    fixed: Mapping[str, Any],
) -> tuple[
    dict[tuple[int, int, float, int], float],
    dict[str, Any],
    dict[int, dict[str, Any]],
]:
    upstream = _mapping(fixed["upstream"], "fixed.upstream")
    payload = _load_json(reduction_json, "upstream reduction JSON")
    _require(payload.get("schema") == upstream["reduction_schema"], "upstream reduction schema mismatch")
    _require(payload.get("mode") == "full", "upstream reduction mode is not full")
    audit = _mapping(payload.get("audit"), "reduction.audit")
    _require(audit.get("pass") is True and audit.get("fail_closed") is True, "upstream reducer audit did not pass fail-closed")
    _require(audit.get("campaign_kind") == "production", "upstream campaign kind mismatch")
    _require(audit.get("manifest_sha256") == upstream["manifest_sha256"], "reduction manifest hash drift")
    _require(audit.get("cell_count") == upstream["cell_count"], "reduction cell count drift")
    sacct = _mapping(audit.get("sacct"), "reduction.audit.sacct")
    _require(sacct.get("provided") is True and sacct.get("verified") is True, "sacct was not provided and verified")
    _require(sacct.get("receipt_filename") == upstream["sacct_receipt_filename"], "sacct filename drift")
    _require(sacct.get("allocations_verified") == upstream["allocation_count"], "sacct allocation count drift")
    _require(sacct.get("cells_verified") == upstream["cell_count"], "sacct cell count drift")
    _require(sacct.get("cells_per_allocation") == upstream["cells_per_allocation"], "sacct bundle size drift")
    _require(sacct.get("bundled_production") is True, "sacct is not bundled production")
    sacct_sha = _sha(sacct.get("receipt_sha256"), "sacct receipt SHA")
    _require(sacct_receipt.name == upstream["sacct_receipt_filename"], "live sacct filename drift")
    _require(_sha256_file(sacct_receipt) == sacct_sha, "live sacct receipt hash drift")

    inventory = payload.get("inventory")
    _require(isinstance(inventory, list), "reduction.inventory must be an array")
    inventory_sha, task_allocations, inventory_by_id = _inventory_digest(inventory, upstream)
    _require(inventory_sha == _sha(audit.get("inventory_digest"), "inventory digest"), "inventory digest drift")
    independent_sacct = _independent_sacct_audit(sacct_receipt, task_allocations, upstream)

    csv_block = _mapping(payload.get("csv"), "reduction.csv")
    _require(csv_block.get("kind") == "block_statistics", "upstream CSV kind mismatch")
    _require(csv_block.get("filename") == reduction_csv.name, "upstream CSV filename mismatch")
    _require(csv_block.get("rows") == upstream["total_csv_row_count"], "upstream CSV row count receipt drift")
    csv_sha = _sha(csv_block.get("sha256"), "upstream CSV SHA")
    _require(_sha256_file(reduction_csv) == csv_sha, "upstream CSV content hash drift")

    conditions = payload.get("conditions")
    _require(isinstance(conditions, list) and len(conditions) == 90, "reduction must contain 90 conditions")
    json_blocks: dict[tuple[int, int, float, int], tuple[str, float]] = {}
    for index, raw in enumerate(conditions):
        condition = _mapping(raw, f"conditions[{index}]")
        condition_id = condition.get("condition_id")
        _require(isinstance(condition_id, str) and condition_id, "condition_id invalid")
        parameters = _mapping(condition.get("parameters"), "condition.parameters")
        x = _integer(parameters.get("target2_x"), "condition target2_x")
        y = _integer(parameters.get("target2_y"), "condition target2_y")
        amplitude = _number(parameters.get("amplitude"), "condition amplitude")
        _require((x, y) in fixed["geometries"] and amplitude in (0.0, *fixed["treatments"]), "unexpected condition")
        _require(condition.get("walk_replicates") == [0, 1], "condition walk streams were not [0,1]")
        blocks = condition.get("block_means")
        _require(isinstance(blocks, list) and len(blocks) == 32, "condition must contain 32 block means")
        for block_raw in blocks:
            block = _mapping(block_raw, "condition block mean")
            disorder = _integer(block.get("disorder_replicate"), "condition disorder", minimum=0)
            value = _number(block.get("gating_probability_drop"), "condition gating_probability_drop")
            key = (x, y, amplitude, disorder)
            _require(disorder < 32 and key not in json_blocks, f"duplicate or invalid JSON block {key}")
            json_blocks[key] = (condition_id, value)

    try:
        with reduction_csv.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            _require(tuple(reader.fieldnames or ()) == UPSTREAM_CSV_FIELDS, "upstream CSV header drift")
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise AuditError(f"cannot parse upstream CSV: {exc}") from exc
    _require(len(rows) == upstream["total_csv_row_count"], "upstream CSV physical row count drift")
    block_rows = [row for row in rows if row.get("row_type") == "block_mean"]
    primary_rows = [row for row in rows if row.get("row_type") == "primary_pair"]
    _require(len(block_rows) == upstream["block_csv_row_count"], "block CSV row count drift")
    _require(len(primary_rows) == upstream["primary_csv_row_count"], "primary CSV row count drift")
    _require(len(block_rows) + len(primary_rows) == len(rows), "unexpected CSV row type")
    csv_values: dict[tuple[int, int, float, int], float] = {}
    for row in block_rows:
        try:
            x = int(row["target2_x"])
            y = int(row["target2_y"])
            amplitude = float(row["amplitude"])
            disorder = int(row["disorder_replicate"])
            value = float(row["gating_probability_drop"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AuditError(f"invalid block CSV scalar: {exc}") from exc
        _require(math.isfinite(amplitude) and math.isfinite(value), "nonfinite block CSV scalar")
        _require(row.get("walk_replicates") == "0;1", "block row is not the within-field average of walk streams 0 and 1")
        key = (x, y, amplitude, disorder)
        _require(key not in csv_values and key in json_blocks, f"duplicate or unexpected CSV block {key}")
        condition_id, json_value = json_blocks[key]
        _require(row.get("condition_id") == condition_id and row.get("comparison_id") == "", "CSV condition identity drift")
        _require(value == json_value, f"CSV/JSON block value drift at {key}")
        csv_values[key] = value
    _require(set(csv_values) == set(json_blocks), "CSV/JSON block inventory mismatch")
    expected_keys = {
        (x, y, amplitude, block)
        for x, y in fixed["geometries"]
        for amplitude in (0.0, *fixed["treatments"])
        for block in range(32)
    }
    _require(set(csv_values) == expected_keys, "secondary scientific block inventory mismatch")
    return (
        csv_values,
        {
            "reduction_json_sha256": _sha256_file(reduction_json),
            "reduction_csv_sha256": csv_sha,
            "sacct_receipt_sha256": sacct_sha,
            "inventory_digest": inventory_sha,
            "sacct_task_allocation_mapping_sha256": independent_sacct[
                "task_allocation_mapping_sha256"
            ],
            "independent_sacct": independent_sacct,
        },
        inventory_by_id,
    )


def _max_t(effect_matrix: np.ndarray, *, seed: int, resamples: int, critical_index: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, np.ndarray]:
    _require(effect_matrix.shape == (32, 75), "effect matrix must be exactly 32x75")
    _require(bool(np.isfinite(effect_matrix).all()), "effect matrix contains nonfinite values")
    means = np.mean(effect_matrix, axis=0)
    standard_errors = np.std(effect_matrix, axis=0, ddof=1) / math.sqrt(32.0)
    _require(bool(np.isfinite(standard_errors).all()) and bool(np.all(standard_errors > 0.0)), "zero or nonfinite observed standard error")
    observed_t = means / standard_errors
    generator = np.random.Generator(np.random.PCG64(seed))
    maxima = np.empty(resamples, dtype=np.float64)
    batch_size = 250
    for start in range(0, resamples, batch_size):
        stop = min(start + batch_size, resamples)
        indices = generator.integers(0, 32, size=(stop - start, 32), dtype=np.int64)
        sampled = effect_matrix[indices, :]
        sampled_means = np.mean(sampled, axis=1)
        sampled_se = np.std(sampled, axis=1, ddof=1) / math.sqrt(32.0)
        _require(bool(np.isfinite(sampled_se).all()) and bool(np.all(sampled_se > 0.0)), "zero or nonfinite bootstrap standard error")
        centered_t = (sampled_means - means[None, :]) / sampled_se
        _require(bool(np.isfinite(centered_t).all()), "nonfinite studentized bootstrap statistic")
        maxima[start:stop] = np.max(np.abs(centered_t), axis=1)
    ordered = np.sort(maxima)
    critical = float(ordered[critical_index])
    adjusted_p = (1.0 + np.sum(maxima[:, None] >= np.abs(observed_t)[None, :], axis=0)) / (resamples + 1.0)
    _require(bool(np.isfinite(adjusted_p).all()), "nonfinite adjusted p-value")
    return means, standard_errors, observed_t, critical, adjusted_p


def _output_csv(rows: Sequence[Mapping[str, Any]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row[field] for field in CSV_FIELDS})
    return buffer.getvalue().encode("utf-8")


def _commit_no_overwrite(path: Path, data: bytes) -> tuple[Path, tuple[int, int]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        inode = (temporary.stat().st_dev, temporary.stat().st_ino)
        os.link(temporary, path)
        return temporary, inode
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _atomic_pair_no_overwrite(json_path: Path, csv_path: Path, json_data: bytes, csv_data: bytes) -> None:
    _require(json_path != csv_path, "JSON and CSV outputs must differ")
    _require(not json_path.exists() and not csv_path.exists(), "output exists; refusing to overwrite")
    committed: list[tuple[Path, tuple[int, int]]] = []
    temporaries: list[Path] = []
    try:
        for path, data in ((csv_path, csv_data), (json_path, json_data)):
            temporary, inode = _commit_no_overwrite(path, data)
            temporaries.append(temporary)
            committed.append((path, inode))
        for directory in {json_path.parent.resolve(), csv_path.parent.resolve()}:
            descriptor = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    except BaseException:
        for path, inode in reversed(committed):
            try:
                stat = path.stat()
                if (stat.st_dev, stat.st_ino) == inode:
                    path.unlink()
            except FileNotFoundError:
                pass
        raise
    finally:
        for temporary in temporaries:
            temporary.unlink(missing_ok=True)


def analyze(
    *,
    contract_path: Path,
    payload_manifest_path: Path,
    expected_payload_manifest_sha256: str,
    manifest_path: Path,
    reduction_json: Path,
    reduction_csv: Path,
    sacct_receipt: Path,
    output_json: Path,
    output_csv: Path,
) -> dict[str, Any]:
    _require(output_json != output_csv, "JSON and CSV outputs must differ")
    _require(not output_json.exists() and not output_csv.exists(), "output exists; refusing to overwrite")
    for label, path in (
        ("contract", contract_path),
        ("payload manifest", payload_manifest_path),
        ("manifest", manifest_path),
        ("reduction JSON", reduction_json),
        ("reduction CSV", reduction_csv),
        ("sacct receipt", sacct_receipt),
    ):
        _require(path.is_file() and not path.is_symlink(), f"{label} input missing or symlinked")
    contract = _load_json(contract_path, "secondary contract")
    fixed = _fixed_contract(contract)
    upstream = _mapping(fixed["upstream"], "fixed.upstream")
    reduction_dir = UPSTREAM_ROOT / str(upstream["reduction_dir_relative"])
    expected_paths = {
        contract_path: SECONDARY_ROOT / "notes/isambard_ai_v3_secondary_analysis_contract_r1.json",
        payload_manifest_path: SECONDARY_ROOT / PAYLOAD_MANIFEST_RELATIVE,
        manifest_path: UPSTREAM_ROOT / str(upstream["manifest_relative"]),
        reduction_json: reduction_dir / str(upstream["reduction_json_filename"]),
        reduction_csv: reduction_dir / str(upstream["reduction_csv_filename"]),
        sacct_receipt: reduction_dir / str(upstream["sacct_receipt_filename"]),
    }
    for actual, expected in expected_paths.items():
        _require(actual.absolute() == expected.absolute(), f"input path drift: expected {expected}")
    output_parent = SECONDARY_ROOT / "artifacts/outputs/isambard_ai_v3/secondary_r1"
    _require(SECONDARY_ROOT.is_dir() and not SECONDARY_ROOT.is_symlink(), "secondary write root missing or symlinked")
    secondary_real = SECONDARY_ROOT.resolve(strict=True)
    for output in (output_json, output_csv):
        _require(output.parent.is_dir() and not output.parent.is_symlink(), "output directory missing or symlinked")
        try:
            output.absolute().relative_to(output_parent.absolute())
            output.parent.resolve(strict=True).relative_to(secondary_real)
        except ValueError as exc:
            raise AuditError(f"output path must remain under {output_parent}") from exc
    payload_receipts = _validate_payload_manifest(
        payload_manifest_path, expected_payload_manifest_sha256
    )
    configs = _validate_manifest(manifest_path, fixed)
    values, input_hashes, inventory_by_id = _validate_reduction(
        reduction_json, reduction_csv, sacct_receipt, fixed
    )
    raw_root = UPSTREAM_ROOT / str(upstream["raw_results_dir_relative"])
    raw_values, raw_audit = _independent_raw_replay(
        raw_root=raw_root,
        configs=configs,
        inventory_by_id=inventory_by_id,
        upstream=upstream,
    )
    _require(set(raw_values) == set(values), "raw/reduction block inventory mismatch")
    for key, raw_value in raw_values.items():
        _require(
            math.isclose(raw_value, values[key], rel_tol=0.0, abs_tol=1.0e-15),
            f"raw/reduction block mean mismatch at {key}",
        )
    input_hashes["independent_raw_replay"] = raw_audit

    columns: list[tuple[int, int, float]] = [
        (x, y, amplitude)
        for x, y in fixed["geometries"]
        for amplitude in fixed["treatments"]
    ]
    effects = np.empty((32, 75), dtype=np.float64)
    for column, (x, y, amplitude) in enumerate(columns):
        for block in range(32):
            effects[block, column] = values[(x, y, amplitude, block)] - values[(x, y, 0.0, block)]
    means, standard_errors, observed_t, critical, adjusted_p = _max_t(
        effects,
        seed=fixed["seed"],
        resamples=fixed["resamples"],
        critical_index=fixed["critical_index"],
    )
    rows: list[dict[str, Any]] = []
    for index, (x, y, amplitude) in enumerate(columns):
        rows.append(
            {
                "contrast_index": index,
                "target2_x": x,
                "target2_y": y,
                "control_amplitude": 0.0,
                "treatment_amplitude": amplitude,
                "n_disorder_blocks": 32,
                "mean_effect": float(means[index]),
                "standard_error": float(standard_errors[index]),
                "observed_t": float(observed_t[index]),
                "simultaneous_ci_lower": float(means[index] - critical * standard_errors[index]),
                "simultaneous_ci_upper": float(means[index] + critical * standard_errors[index]),
                "adjusted_p_value": float(adjusted_p[index]),
            }
        )
    csv_data = _output_csv(rows)
    payload = {
        "schema": OUTPUT_SCHEMA,
        "status": "PASS_SECONDARY_MAX_T_R1",
        "audit": {
            "pass": True,
            "fail_closed": True,
            "contract_filename": contract_path.name,
            "contract_sha256": _sha256_file(contract_path),
            "payload_manifest_filename": payload_manifest_path.name,
            "payload_manifest_sha256": _sha256_file(payload_manifest_path),
            "payload_members": payload_receipts,
            "manifest_filename": manifest_path.name,
            "manifest_sha256": _sha256_file(manifest_path),
            **input_hashes,
        },
        "method": {
            "contrast_count": 75,
            "disorder_blocks": 32,
            "walk_stream_operation": "already averaged within each disorder block upstream",
            "bit_generator": "PCG64",
            "seed": 20260726,
            "joint_field_block_resamples": 10000,
            "studentization": "centered resample mean / resample SE (ddof=1)",
            "maximum_statistic": "max absolute t over all 75 contrasts",
            "confidence_level": 0.95,
            "critical_order_statistic_one_indexed": 9501,
            "simultaneous_critical_value": critical,
            "adjusted_p_value": "(1 + exceedance count) / 10001",
        },
        "contrasts": rows,
        "csv": {
            "filename": output_csv.name,
            "sha256": _sha256_bytes(csv_data),
            "rows": 75,
        },
    }
    json_data = (json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    _atomic_pair_no_overwrite(output_json, output_csv, json_data, csv_data)
    return payload


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--payload-manifest", type=Path, required=True)
    parser.add_argument("--expected-payload-manifest-sha256", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--reduction-json", type=Path, required=True)
    parser.add_argument("--reduction-csv", type=Path, required=True)
    parser.add_argument("--sacct-receipt", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        payload = analyze(
            contract_path=args.contract.absolute(),
            payload_manifest_path=args.payload_manifest.absolute(),
            expected_payload_manifest_sha256=args.expected_payload_manifest_sha256,
            manifest_path=args.manifest.absolute(),
            reduction_json=args.reduction_json.absolute(),
            reduction_csv=args.reduction_csv.absolute(),
            sacct_receipt=args.sacct_receipt.absolute(),
            output_json=args.output_json.absolute(),
            output_csv=args.output_csv.absolute(),
        )
    except (AuditError, OSError, ValueError) as exc:
        print(f"secondary max-t audit failed closed: {exc}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "csv": payload["csv"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
