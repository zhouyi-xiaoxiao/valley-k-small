#!/usr/bin/env python3
"""Independent checkpoint, tail-gate, and allocation replay for v3/v4-r2 H2.

This module deliberately does not import the production reducer.  It rebuilds
the finite-horizon metrics directly from the integer NPZ sidecars and checks
the reducer's tail and evidence decisions against that reconstruction.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.stats import t as student_t

HEX64 = __import__("re").compile(r"[0-9a-f]{64}")
DECIMAL = __import__("re").compile(r"[0-9]+")
ARRAY_JOB = __import__("re").compile(r"([0-9]+)_([0-9]+)")
METRICS = (
    "gating_probability_drop",
    "gating_probability_drop_t_half",
    "gating_tail_delta",
    "one_unresolved_probability",
    "two_unresolved_probability",
    "diversion_probability",
    "acceleration_probability",
    "target2_first_probability",
)


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_json(path: Path, *, mode600: bool = False) -> dict[str, Any]:
    stat = path.lstat()
    req(path.is_file() and not path.is_symlink() and stat.st_nlink == 1,
        f"unsafe JSON evidence: {path}")
    if mode600:
        req(stat.st_mode & 0o777 == 0o600, f"JSON evidence mode drift: {path}")

    def pairs(pairs_: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs_:
            req(key not in result, f"duplicate JSON key {key}: {path}")
            result[key] = value
        return result

    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"nonfinite JSON token {token}: {path}")),
    )
    req(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def close_tree(actual: Any, expected: Any, label: str, *, atol: float = 1e-15) -> None:
    """Exact structural equality with a tight absolute tolerance for floats."""
    if isinstance(expected, bool) or expected is None or isinstance(expected, str):
        req(actual == expected, f"{label} drift")
    elif isinstance(expected, int):
        req(isinstance(actual, int) and not isinstance(actual, bool)
            and actual == expected, f"{label} integer drift")
    elif isinstance(expected, float):
        req(isinstance(actual, (int, float)) and not isinstance(actual, bool)
            and math.isfinite(float(actual))
            and math.isclose(float(actual), expected, rel_tol=0.0, abs_tol=atol),
            f"{label} float drift")
    elif isinstance(expected, list):
        req(isinstance(actual, list) and len(actual) == len(expected),
            f"{label} list shape drift")
        for index, value in enumerate(expected):
            close_tree(actual[index], value, f"{label}[{index}]", atol=atol)
    elif isinstance(expected, dict):
        req(isinstance(actual, dict) and set(actual) == set(expected),
            f"{label} object keys drift")
        for key, value in expected.items():
            close_tree(actual[key], value, f"{label}.{key}", atol=atol)
    else:
        req(actual == expected, f"{label} drift")


def replay_sacct_bijection(
    path: Path, array_job: str, inventory: Sequence[Mapping[str, Any]],
    *, task_count: int, cells_per_allocation: int, require_extended: bool,
) -> dict[str, Any]:
    """Prove a global JobIDRaw <-> array-task bijection.

    A task row must have both the exact Slurm array-form JobID and the exact
    allocation-unique JobIDRaw captured by every raw result assigned to it.
    Merely seeing 480 distinct task suffixes is intentionally insufficient.
    """
    req(DECIMAL.fullmatch(array_job) is not None, "array job is not decimal")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        rows = list(reader)
        header = reader.fieldnames
    short = ["JobIDRaw", "JobID", "State", "ExitCode"]
    extended = [
        "JobIDRaw", "JobID", "ArrayJobID", "ArrayTaskID", "State",
        "ExitCode", "ElapsedRaw", "AllocTRES", "ReqTRES", "NNodes",
    ]
    req(header == (extended if require_extended else short),
        "sacct exact header drift")
    jobs_by_task: dict[int, set[str]] = {task: set() for task in range(task_count)}
    cells_by_task: dict[int, set[int]] = {task: set() for task in range(task_count)}
    for row in inventory:
        task = int(str(row["slurm_array_task_id"]))
        cell = int(row["cell_id"])
        job = str(row["slurm_job_id"])
        req(row["slurm_array_job_id"] == array_job
            and 0 <= task < task_count and DECIMAL.fullmatch(job) is not None,
            "inventory array/task/allocation identity drift")
        jobs_by_task[task].add(job)
        cells_by_task[task].add(cell)
    expected_jobs: dict[int, str] = {}
    for task in range(task_count):
        req(len(jobs_by_task[task]) == 1
            and len(cells_by_task[task]) == cells_per_allocation,
            f"task {task} raw allocation/cell cardinality drift")
        expected_jobs[task] = next(iter(jobs_by_task[task]))
    req(len(set(expected_jobs.values())) == task_count,
        "JobIDRaw is not globally unique across array tasks")

    seen_tasks: set[int] = set()
    seen_raw: set[str] = set()
    parent_rows = 0
    elapsed = 0
    for row in rows:
        req(set(row) == set(header or ())
            and all(value is not None for value in row.values()),
            "sacct row shape drift")
        raw_id = row["JobIDRaw"]
        array_id = row["JobID"]
        if raw_id == array_job and array_id == array_job:
            parent_rows += 1
            req(row["State"].split("+")[0] == "COMPLETED"
                and row["ExitCode"] == "0:0", "array parent is not terminal success")
            continue
        match = ARRAY_JOB.fullmatch(array_id)
        req(match is not None and match.group(1) == array_job,
            "sacct task JobID is not the exact array-form identity")
        task = int(match.group(2))
        req(0 <= task < task_count and task not in seen_tasks,
            "duplicate/out-of-range sacct task row")
        req(raw_id == expected_jobs[task] and raw_id not in seen_raw,
            "JobIDRaw/JobID bidirectional allocation mapping drift")
        if require_extended:
            req(row["ArrayJobID"] == array_job and row["ArrayTaskID"] == str(task),
                "extended sacct array columns drift")
            seconds = int(row["ElapsedRaw"])
            req(seconds > 0 and int(row["NNodes"]) == 1,
                "extended sacct elapsed/node drift")
            elapsed += seconds
        req(row["State"].split("+")[0] == "COMPLETED"
            and row["ExitCode"] == "0:0", f"task {task} is not terminal success")
        seen_tasks.add(task)
        seen_raw.add(raw_id)
    req(parent_rows == 1 and seen_tasks == set(range(task_count))
        and seen_raw == set(expected_jobs.values()) and len(rows) == task_count + 1,
        "sacct is not exact parent plus globally unique task allocations")
    return {
        "independently_parsed": True,
        "parent_rows": 1,
        "tasks": task_count,
        "unique_job_id_raw": len(seen_raw),
        "cells_per_allocation": cells_per_allocation,
        "elapsed_raw_total_seconds": elapsed if require_extended else None,
        "receipt_sha256": sha(path),
        "bijection_digest": canonical_digest({str(k): expected_jobs[k]
                                               for k in sorted(expected_jobs)}),
    }


def raw_checkpoint_metrics(
    npz_path: Path, json_path: Path, defaults: Mapping[str, Any], cell: int,
) -> dict[str, float]:
    """Recompute all finite-horizon metrics directly from raw integer arrays."""
    payload = strict_json(json_path, mode600=True)
    with np.load(npz_path, allow_pickle=False) as archive:
        keys = {
            "schema_version", "one_target1_fpt_histogram",
            "two_target1_fpt_histogram", "two_target2_fpt_histogram",
            "checkpoint_steps", "checkpoint_counts", "paired_outcome_counts",
        }
        req(set(archive.files) == keys, f"cell {cell} NPZ exact keys drift")
        arrays = {key: np.asarray(archive[key]) for key in keys}
    steps = int(defaults["steps"])
    checkpoints = [int(value) for value in defaults["checkpoints"]]
    shapes = {
        "schema_version": (),
        "one_target1_fpt_histogram": (steps + 1,),
        "two_target1_fpt_histogram": (steps + 1,),
        "two_target2_fpt_histogram": (steps + 1,),
        "checkpoint_steps": (len(checkpoints),),
        "checkpoint_counts": (len(checkpoints), 6),
        "paired_outcome_counts": (3, 3),
    }
    for key, array in arrays.items():
        req(array.dtype == np.dtype(np.int64) and array.shape == shapes[key]
            and bool(np.all(array >= 0)),
            f"cell {cell} {key} dtype/shape/sign drift")
    req(int(arrays["schema_version"]) == 3
        and arrays["checkpoint_steps"].tolist() == checkpoints,
        f"cell {cell} checkpoint schedule drift")
    walkers = int(defaults["walkers"])
    one = arrays["one_target1_fpt_histogram"]
    two1 = arrays["two_target1_fpt_histogram"]
    two2 = arrays["two_target2_fpt_histogram"]
    counts = arrays["checkpoint_counts"]
    paired = arrays["paired_outcome_counts"]
    req(bool(np.all(two1 <= one)), f"cell {cell} first-target subset drift")
    req(int(paired.sum(dtype=np.int64)) == walkers
        and int(paired[0, 1]) == 0 and bool(np.all(paired[2, :] == 0)),
        f"cell {cell} paired outcome mass/state drift")
    one_hits = int(one.sum(dtype=np.int64))
    two1_hits = int(two1.sum(dtype=np.int64))
    two2_hits = int(two2.sum(dtype=np.int64))
    one_unresolved = walkers - one_hits
    two_unresolved = walkers - two1_hits - two2_hits
    req(one_unresolved >= 0 and two_unresolved >= 0
        and int(paired[0, :].sum(dtype=np.int64)) == one_unresolved
        and int(paired[1, :].sum(dtype=np.int64)) == one_hits
        and int(paired[:, 0].sum(dtype=np.int64)) == two_unresolved
        and int(paired[:, 1].sum(dtype=np.int64)) == two1_hits
        and int(paired[:, 2].sum(dtype=np.int64)) == two2_hits,
        f"cell {cell} histogram/paired reverse mass drift")
    req(bool(np.all(counts[:, 0] + counts[:, 1] == walkers))
        and bool(np.all(counts[:, 2] + counts[:, 3] + counts[:, 4] == walkers))
        and bool(np.all(counts[:, 5] == walkers))
        and bool(np.all(counts[:, 2] <= counts[:, 0])),
        f"cell {cell} checkpoint mass/subset drift")
    for column in (0, 2, 3):
        req(bool(np.all(np.diff(counts[:, column]) >= 0)),
            f"cell {cell} checkpoint hit monotonicity drift")
    for column in (1, 4):
        req(bool(np.all(np.diff(counts[:, column]) <= 0)),
            f"cell {cell} checkpoint unresolved monotonicity drift")
    expected_cumulative: dict[str, dict[str, int]] = {}
    for index, step in enumerate(checkpoints):
        expected = [
            int(one[:step + 1].sum(dtype=np.int64)),
            walkers - int(one[:step + 1].sum(dtype=np.int64)),
            int(two1[:step + 1].sum(dtype=np.int64)),
            int(two2[:step + 1].sum(dtype=np.int64)),
            walkers - int(two1[:step + 1].sum(dtype=np.int64))
                    - int(two2[:step + 1].sum(dtype=np.int64)),
            walkers,
        ]
        req(counts[index].tolist() == expected,
            f"cell {cell} raw histogram/checkpoint mismatch at {step}")
        expected_cumulative[str(step)] = {
            "one_target1": expected[0], "one_unresolved": expected[1],
            "two_target1": expected[2], "two_target2": expected[3],
            "two_unresolved": expected[4], "walkers": expected[5],
        }
    close_tree(payload.get("cumulative_counts"), expected_cumulative,
               f"cell {cell}.cumulative_counts")
    half = steps // 2
    req(half in checkpoints, f"cell {cell} lacks preregistered half horizon")
    half_index = checkpoints.index(half)
    gating = (one_hits - two1_hits) / walkers
    gating_half = (int(counts[half_index, 0]) - int(counts[half_index, 2])) / walkers
    metrics = {
        "gating_probability_drop": gating,
        "gating_probability_drop_t_half": gating_half,
        "gating_tail_delta": gating - gating_half,
        "one_unresolved_probability": one_unresolved / walkers,
        "two_unresolved_probability": two_unresolved / walkers,
        "diversion_probability": int(paired[1, 2]) / walkers,
        "acceleration_probability": int(paired[0, 2]) / walkers,
        "target2_first_probability": two2_hits / walkers,
    }
    close_tree(payload.get("gating_probability_drop"), gating,
               f"cell {cell}.gating_probability_drop")
    close_tree(payload.get("target2_first_probability"), metrics["target2_first_probability"],
               f"cell {cell}.target2_first_probability")
    return metrics


def _condition_parameters(defaults: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "profile": config.get("profile"),
        "walkers": defaults["walkers"], "steps": defaults["steps"],
        "base_hold": defaults["base_hold"], "amplitude": config["amplitude"],
        "target_radius": defaults["target_radius"],
        "start_x": defaults["start_x"], "start_y": defaults["start_y"],
        "target1_x": defaults["target1_x"], "target1_y": defaults["target1_y"],
        "target2_x": config["target2_x"], "target2_y": config["target2_y"],
        "checkpoints": defaults["checkpoints"],
    }


def _mean_ci(values: Sequence[float]) -> dict[str, float | int]:
    req(len(values) >= 2, "tail statistic needs at least two disorder blocks")
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    se = sd / math.sqrt(len(values))
    critical = float(student_t.ppf(0.975, len(values) - 1))
    half = critical * se
    return {
        "n_disorder_blocks": len(values), "mean": mean,
        "standard_deviation": sd, "standard_error": se,
        "t_critical": critical, "ci_half_width": half,
        "ci_lower": mean - half, "ci_upper": mean + half,
    }


def _tail_contract(manifest: Mapping[str, Any]) -> dict[str, Any]:
    prereg = manifest["preregistration"]
    tail = prereg["gates"]["tail"]
    stages = [stage for stage in prereg["stages"] if stage.get("stage_id") == "A"]
    req(len(stages) == 1, "manifest must have one preregistered stage A")
    selection = stages[0]["selection"]
    return {
        "anchors": [(int(row["x"]), int(row["y"])) for row in selection["target2"]],
        "amplitudes": [float(value) for value in selection["amplitudes"]],
        "one_limit": float(tail["one_target_unresolved_upper_max"]),
        "two_limit": float(tail["two_target_unresolved_upper_max"]),
        "stability_limit": float(tail["horizon_drift_abs_plus_tcrit_se_max"]),
        "primary_horizon": int(tail["primary_horizon"]),
        "escalation_horizon": int(tail["escalation_horizon"]),
    }


def recompute_tail_evidence(
    manifest_path: Path, raw_root: Path, reduction_path: Path,
    *, expected_cells: int, expected_blocks: int,
) -> dict[str, Any]:
    manifest = strict_json(manifest_path)
    reduction = strict_json(reduction_path, mode600=True)
    req(reduction.get("mode") == "full" and reduction.get("audit", {}).get("pass") is True,
        "full reduction did not pass its fail-closed audit")
    configs = manifest.get("cells")
    inventory = reduction.get("inventory")
    req(isinstance(configs, list) and len(configs) == expected_cells
        and isinstance(inventory, list) and len(inventory) == expected_cells,
        "manifest/reduction cell cardinality drift")
    by_config = {int(row["cell_id"]): row for row in configs}
    by_inventory = {int(row["cell_id"]): row for row in inventory}
    req(set(by_config) == set(by_inventory) == set(range(expected_cells)),
        "manifest/reduction cell ID inventory drift")
    defaults = manifest["defaults"]
    grouped: dict[str, dict[int, dict[int, dict[str, float]]]] = {}
    params_by_group: dict[str, dict[str, Any]] = {}
    raw_lines: list[str] = []
    for cell in range(expected_cells):
        config = by_config[cell]
        row = by_inventory[cell]
        req(row["json_path"] == f"cell-{cell}/cell-{cell}.json"
            and row["npz_path"] == f"cell-{cell}/cell-{cell}.npz",
            f"cell {cell} reduction raw path drift")
        json_path = raw_root / row["json_path"]
        npz_path = raw_root / row["npz_path"]
        req(sha(json_path) == row["json_sha256"]
            and sha(npz_path) == row["npz_sha256"],
            f"cell {cell} raw hash reverse binding drift")
        metrics = raw_checkpoint_metrics(npz_path, json_path, defaults, cell)
        params = _condition_parameters(defaults, config)
        canonical = json.dumps(params, sort_keys=True, separators=(",", ":"))
        block = int(config["disorder_replicate"])
        walk = int(config["walk_replicate"])
        streams = grouped.setdefault(canonical, {}).setdefault(block, {})
        req(walk not in streams, f"duplicate raw walk stream at cell {cell}")
        streams[walk] = metrics
        params_by_group[canonical] = params
        raw_lines.append(f"{cell}\t{row['json_sha256']}\t{row['npz_sha256']}\n")
    recomputed: dict[str, dict[str, Any]] = {}
    for canonical in sorted(grouped):
        params = params_by_group[canonical]
        condition_id = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        blocks: list[dict[str, Any]] = []
        for block, streams in sorted(grouped[canonical].items()):
            req(set(streams) == {0, 1}, f"condition {condition_id} walk pair drift")
            averaged = {metric: statistics.fmean(streams[walk][metric]
                                                  for walk in (0, 1))
                        for metric in METRICS}
            blocks.append({"disorder_replicate": block, **averaged})
        req(len(blocks) == expected_blocks,
            f"condition {condition_id} disorder block count drift")
        stats = {metric: _mean_ci([float(row[metric]) for row in blocks])
                 for metric in METRICS}
        one_upper = float(stats["one_unresolved_probability"]["ci_upper"])
        two_upper = float(stats["two_unresolved_probability"]["ci_upper"])
        delta = stats["gating_tail_delta"]
        stability = abs(float(delta["mean"])) + float(delta["ci_half_width"])
        recomputed[condition_id] = {
            "condition_id": condition_id, "parameters": params,
            "walk_replicates": [0, 1], "block_means": blocks,
            "statistics": stats,
            "tail_diagnostics": {
                "one_unresolved_ci_upper": one_upper,
                "two_unresolved_ci_upper": two_upper,
                "gating_stability_abs_ci_upper": stability,
                # The per-condition reducer uses the same frozen thresholds.
                "pass": one_upper <= 0.005 and two_upper <= 0.005
                        and stability <= 0.002,
            },
        }
    claimed_conditions = reduction.get("conditions")
    req(isinstance(claimed_conditions, list)
        and len(claimed_conditions) == len(recomputed),
        "reduction condition inventory drift")
    claimed_by_id = {str(row.get("condition_id")): row for row in claimed_conditions}
    req(set(claimed_by_id) == set(recomputed), "reduction condition IDs drift")
    for condition_id, expected in recomputed.items():
        actual = claimed_by_id[condition_id]
        close_tree(actual.get("parameters"), expected["parameters"],
                   f"condition {condition_id}.parameters")
        close_tree(actual.get("walk_replicates"), [0, 1],
                   f"condition {condition_id}.walk_replicates")
        close_tree(actual.get("tail_diagnostics"), expected["tail_diagnostics"],
                   f"condition {condition_id}.tail_diagnostics")
        # All eight raw-derived metrics are checked at the disorder-block level.
        close_tree(actual.get("block_means"), expected["block_means"],
                   f"condition {condition_id}.block_means")
    contract = _tail_contract(manifest)
    horizon = max(int(row["parameters"]["steps"]) for row in recomputed.values())
    req(horizon in {contract["primary_horizon"], contract["escalation_horizon"]},
        "observed horizon is not preregistered")
    anchors: list[dict[str, Any]] = []
    for x, y in contract["anchors"]:
        for amplitude in contract["amplitudes"]:
            candidates = [row for row in recomputed.values()
                          if row["parameters"]["steps"] == horizon
                          and row["parameters"]["target2_x"] == x
                          and row["parameters"]["target2_y"] == y
                          and math.isclose(float(row["parameters"]["amplitude"]),
                                           amplitude, rel_tol=0.0, abs_tol=1e-12)]
            req(len(candidates) == 1, "tail anchor/amplitude selection drift")
            selected = candidates[0]
            anchors.append({
                "condition_id": selected["condition_id"],
                "target2_x": x, "target2_y": y, "amplitude": amplitude,
                **selected["tail_diagnostics"],
            })
    tail = {
        "horizon": horizon, "anchors": anchors,
        "thresholds": {
            "one_unresolved_ci_upper": contract["one_limit"],
            "two_unresolved_ci_upper": contract["two_limit"],
            "gating_stability_abs_ci_upper": contract["stability_limit"],
        },
        "pass": all(
            row["one_unresolved_ci_upper"] <= contract["one_limit"]
            and row["two_unresolved_ci_upper"] <= contract["two_limit"]
            and row["gating_stability_abs_ci_upper"] <= contract["stability_limit"]
            for row in anchors
        ),
    }
    close_tree(reduction.get("tail_gate"), tail, "reduction.tail_gate")
    primary = reduction.get("primary")
    sacct = reduction.get("audit", {}).get("sacct", {})
    req(isinstance(primary, dict) and isinstance(primary.get("decision"), str),
        "reduction primary decision missing")
    sacct_ok = not bool(sacct.get("provided")) or sacct.get("verified") is True
    evidence = {
        "tail_gate_pass": tail["pass"],
        "primary_decision": primary["decision"],
        "sacct_verified_if_provided": sacct_ok,
        "ready": tail["pass"] and primary["decision"] != "inconclusive" and sacct_ok,
    }
    close_tree(reduction.get("evidence_decision"), evidence,
               "reduction.evidence_decision")
    selected_digest = canonical_digest({
        key: {"parameters": value["parameters"],
              "block_means": value["block_means"],
              "tail_diagnostics": value["tail_diagnostics"]}
        for key, value in sorted(recomputed.items())
    })
    return {
        "independently_recomputed_from_raw_npz": True,
        "cells": expected_cells, "conditions": len(recomputed),
        "disorder_blocks_per_condition": expected_blocks,
        "checkpoint_schedule": defaults["checkpoints"],
        "raw_pair_digest": hashlib.sha256("".join(raw_lines).encode()).hexdigest(),
        "condition_metric_digest": selected_digest,
        "tail_gate": tail, "evidence_decision": evidence,
        "status": "PASS_TAIL_EVIDENCE" if tail["pass"]
                  else "HOLD_STAGE_A2_160K",
    }
