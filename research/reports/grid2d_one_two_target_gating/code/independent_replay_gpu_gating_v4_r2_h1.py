#!/usr/bin/env python3
"""Standalone v4-r2-h1 raw, reduction, TRES, and submission-chain replay."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping

import numpy as np

ROOT = Path("/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727")
V3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h1.json"
SUB = ROOT / "artifacts/submission_h1"
MANIFEST = ROOT / "artifacts/data/gating_v4_r2_production_manifest.json"
FIELD = ROOT / "artifacts/data/disorder_field_pack_v4_r2_reflect.npz"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h1_payload.sha256"
BASE_PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_payload.sha256"
CONTAINER = Path("/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif")
FIXED = {
    "manifest": "b939e38c1e504cfed73e9e4de3d084fabc80083e6b4bab3f03ed2381c27eaa5d",
    "field": "e0b61325fb531b51ef96c405e55da3c909999fb46b4e769b0ab693a49ee43e0d",
    "base_payload": "c6c77f62d05fb17c25160723f87324654041c2de484c3f4e12b2bf92bb8af404",
    "container": "aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4",
}
SUBMIT_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h1-submission-v1"
SUBMIT_STATUS = "SUBMITTED_WITH_EXACT_READBACK"
SUBMIT_KEYS = {
    "schema", "status", "phase", "job_id", "dependency_afterok",
    "payload_manifest_sha256", "phase_inputs", "script", "argv",
    "authorities", "scontrol_readback",
}
SCRIPTS = {
    "canary": "isambard_ai_gating_v4_r2_gpu_canary_h1.sbatch",
    "production": "isambard_ai_gating_v4_r2_fullnode_h1.sbatch",
    "reducer": "isambard_ai_gating_v4_r2_reduce_h1.sbatch",
    "replay": "isambard_ai_gating_v4_r2_replay_h1.sbatch",
}
OUTPUT_KEYS = {
    "schema", "status", "fixed_root", "jobs", "fixed_artifacts", "hashes",
    "raw", "reduction_inventory_digest", "extended_sacct", "submission_chain",
}
CSV_FIELDS = [
    "row_type", "condition_id", "comparison_id", "profile",
    "disorder_replicate", "walk_replicates", "steps", "target2_x",
    "target2_y", "amplitude", "gating_probability_drop",
    "gating_probability_drop_t_half", "gating_tail_delta",
    "one_unresolved_probability", "two_unresolved_probability",
    "diversion_probability", "acceleration_probability",
    "target2_first_probability", "primary_paired_effect",
]
HEX64 = re.compile(r"[0-9a-f]{64}")
DECIMAL = re.compile(r"[0-9]+")


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
        f"unsafe JSON file: {path}")
    if mode600:
        req(stat.st_mode & 0o777 == 0o600, f"authority JSON mode drift: {path}")

    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            req(key not in value, f"duplicate JSON key {key}: {path}")
            value[key] = item
        return value

    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=hook,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"nonfinite JSON token {token}: {path}")),
    )
    req(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def authority(path: Path, expected_sha: str) -> dict[str, Any]:
    req(HEX64.fullmatch(expected_sha) is not None and sha(path) == expected_sha,
        f"authority SHA drift: {path}")
    return strict_json(path, mode600=True)


def validate_v3_release(expected_sha: str) -> None:
    value = authority(V3_RELEASE, expected_sha)
    req(set(value) == {
        "schema", "status", "fixed_roots", "fixed_jobs", "fixed_contracts",
        "evidence_hashes", "inventory_digest", "raw_replay",
        "live_sacct_query_sha256", "secondary_result_schema",
        "secondary_result_status", "canary_reduction",
    } and value["schema"] == "grid2d-one-two-target-gating-v3-release-for-v4-r2-h1"
      and value["status"] == "PASS_AUTHORIZE_V4_R2_H1_HARDWARE_CANARY",
      "v3 release authority drift")


def receipt_path(phase: str) -> Path:
    return SUB / f"{phase}-submission.json"


def validate_submission(
    *, phase: str, path: Path, expected_sha: str, h1_sha: str,
    job: str, dependency: str, phase_inputs: Mapping[str, str],
    authorities: Mapping[str, Mapping[str, str]], script_args: list[str],
) -> dict[str, Any]:
    req(path == receipt_path(phase), f"{phase} receipt path is not fixed")
    value = authority(path, expected_sha)
    req(set(value) == SUBMIT_KEYS and value["schema"] == SUBMIT_SCHEMA
        and value["status"] == SUBMIT_STATUS and value["phase"] == phase
        and value["job_id"] == job and value["dependency_afterok"] == dependency
        and value["payload_manifest_sha256"] == h1_sha
        and value["phase_inputs"] == dict(phase_inputs)
        and value["authorities"] == dict(authorities),
        f"{phase} exact submission receipt drift")
    script = ROOT / "code" / SCRIPTS[phase]
    req(value["script"] == {
        "path": f"code/{SCRIPTS[phase]}", "sha256": sha(script)
    }, f"{phase} script hash/path drift")
    expected_argv = [
        "sbatch", "--parsable", f"--dependency=afterok:{dependency}",
        f"code/{SCRIPTS[phase]}", *script_args,
    ]
    req(value["argv"] == expected_argv, f"{phase} phase-specific argv drift")
    readback = value["scontrol_readback"]
    req(isinstance(readback, str) and f"JobId={job}" in readback
        and f"Dependency=afterok:{dependency}" in readback
        and f"WorkDir={ROOT}" in readback and SCRIPTS[phase] in readback,
        f"{phase} scontrol readback drift")
    return value


def validate_canary_receipt(job: str, expected_sha: str, release_sha: str) -> None:
    path = ROOT / f"artifacts/canary/canary-{job}/canary-receipt.json"
    value = authority(path, expected_sha)
    req(set(value) == {
        "schema", "status", "release_receipt_sha256", "lanes",
        "distinct_uuid_count", "distinct_pci_count",
        "distinct_cuda_visible_devices_count",
    } and value["schema"] == "grid2d-one-two-target-gating-v4-r2-gpu-canary-v1"
      and value["status"] == "PASS_AUTHORIZE_V4_R2_PRODUCTION"
      and value["release_receipt_sha256"] == release_sha
      and value["distinct_uuid_count"] == value["distinct_pci_count"]
        == value["distinct_cuda_visible_devices_count"] == 4,
      "GPU canary receipt drift")
    rows = value["lanes"]
    req(isinstance(rows, list) and len(rows) == 4
        and {row.get("lane") for row in rows} == set(range(4)),
        "GPU canary lane inventory drift")
    directory = path.parent
    req({member.name for member in directory.iterdir()} == {
        "canary-receipt.json", "lane-0.json", "lane-1.json", "lane-2.json", "lane-3.json"
    }, "GPU canary exact directory inventory drift")
    uuids: set[str] = set(); pci_ids: set[str] = set(); visible: set[str] = set()
    by_lane = {int(row["lane"]): row for row in rows}
    for lane in range(4):
        capture_path = directory / f"lane-{lane}.json"
        capture = strict_json(capture_path, mode600=True)
        req(set(capture) == {
            "schema", "lane", "cuda_visible_devices", "slurm_job_id",
            "slurm_step_id", "gpu",
        } and capture["schema"] == "grid2d-one-two-target-gating-v4-r2-gpu-lane-v1"
          and capture["lane"] == lane and capture["slurm_job_id"] == job,
          "GPU lane capture identity drift")
        gpu = capture["gpu"]
        req(isinstance(gpu, dict) and set(gpu) == {
            "index", "uuid", "pci_bus_id", "name", "driver_version"
        }, "GPU lane device schema drift")
        row = by_lane[lane]
        req(set(row) == {
            "lane", "cuda_visible_devices", "uuid", "pci_bus_id", "capture_sha256"
        } and row["capture_sha256"] == sha(capture_path)
          and row["cuda_visible_devices"] == capture["cuda_visible_devices"]
          and row["uuid"] == gpu["uuid"] and row["pci_bus_id"] == gpu["pci_bus_id"],
          "GPU canary/capture reverse bind drift")
        uuids.add(str(gpu["uuid"])); pci_ids.add(str(gpu["pci_bus_id"]))
        visible.add(str(capture["cuda_visible_devices"]))
    req(len(uuids) == len(pci_ids) == len(visible) == 4,
        "GPU canary captures do not prove four distinct devices")


def validate_submission_chain(
    *, array_job: str, reducer_job: str, h1_sha: str,
    production_path: Path, production_sha: str,
    reducer_path: Path, reducer_sha: str,
) -> dict[str, str]:
    req(production_path == receipt_path("production")
        and reducer_path == receipt_path("reducer"),
        "production/reducer submission paths are not fixed")
    production_preview = authority(production_path, production_sha)
    pi = production_preview.get("phase_inputs")
    req(isinstance(pi, dict) and set(pi) == {
        "v3_release_sha256", "canary_job_id", "canary_submission_sha256",
        "canary_receipt_sha256",
    }, "production phase input schema drift")
    release_sha = pi["v3_release_sha256"]
    canary_job = pi["canary_job_id"]
    canary_submit_sha = pi["canary_submission_sha256"]
    canary_receipt_sha = pi["canary_receipt_sha256"]
    req(all(isinstance(value, str) for value in pi.values())
        and DECIMAL.fullmatch(canary_job) is not None
        and all(HEX64.fullmatch(value) is not None for key, value in pi.items()
                if key.endswith("sha256")),
        "production lineage identifiers invalid")
    validate_v3_release(release_sha)
    canary_authorities = {
        "v3_release": {"path": str(V3_RELEASE), "sha256": release_sha},
    }
    validate_submission(
        phase="canary", path=receipt_path("canary"),
        expected_sha=canary_submit_sha, h1_sha=h1_sha, job=canary_job,
        dependency="5789031",
        phase_inputs={"v3_release_sha256": release_sha},
        authorities=canary_authorities,
        script_args=[h1_sha, release_sha, str(V3_RELEASE)],
    )
    canary_path = ROOT / f"artifacts/canary/canary-{canary_job}/canary-receipt.json"
    validate_canary_receipt(canary_job, canary_receipt_sha, release_sha)
    production_authorities = {
        "v3_release": {"path": str(V3_RELEASE), "sha256": release_sha},
        "canary_submission": {
            "path": str(receipt_path("canary")), "sha256": canary_submit_sha,
        },
        "canary_receipt": {"path": str(canary_path), "sha256": canary_receipt_sha},
    }
    validate_submission(
        phase="production", path=production_path, expected_sha=production_sha,
        h1_sha=h1_sha, job=array_job, dependency=canary_job, phase_inputs=pi,
        authorities=production_authorities,
        script_args=[h1_sha, str(V3_RELEASE), release_sha,
                     str(canary_path), canary_receipt_sha],
    )
    reducer_preview = authority(reducer_path, reducer_sha)
    ri = reducer_preview.get("phase_inputs")
    expected_ri = {
        "array_job_id": array_job,
        "production_submission_sha256": production_sha,
        "canary_job_id": canary_job,
        "canary_receipt_sha256": canary_receipt_sha,
    }
    reducer_authorities = {
        "production_submission": {
            "path": str(production_path), "sha256": production_sha,
        },
        "canary_receipt": {"path": str(canary_path), "sha256": canary_receipt_sha},
    }
    validate_submission(
        phase="reducer", path=reducer_path, expected_sha=reducer_sha,
        h1_sha=h1_sha, job=reducer_job, dependency=array_job,
        phase_inputs=expected_ri, authorities=reducer_authorities,
        script_args=[h1_sha, array_job, array_job, str(canary_path),
                     canary_receipt_sha, str(production_path), production_sha],
    )
    req(ri == expected_ri, "reducer phase input lineage drift")
    return {
        "v3_release_sha256": release_sha,
        "canary_job_id": canary_job,
        "canary_submission_receipt_sha256": canary_submit_sha,
        "canary_receipt_sha256": canary_receipt_sha,
        "production_submission_receipt_sha256": production_sha,
        "reducer_submission_receipt_sha256": reducer_sha,
    }


def exact_tree(root: Path) -> dict[str, Any]:
    req(root.is_dir() and not root.is_symlink(), "raw root missing/symlinked")
    children = list(root.iterdir())
    req(len(children) == 23040, "raw directory count drift")
    seen: set[int] = set(); lines: list[str] = []
    for directory in children:
        match = re.fullmatch(r"cell-([0-9]+)", directory.name)
        req(match is not None and directory.is_dir() and not directory.is_symlink(),
            "raw root contains an unexpected member")
        cell = int(match.group(1))
        req(0 <= cell < 23040 and cell not in seen, "raw cell ID drift")
        seen.add(cell)
        members = list(directory.iterdir())
        req({member.name for member in members} == {
            f"cell-{cell}.json", f"cell-{cell}.npz"
        }, f"raw cell {cell} exact member drift")
        for member in members:
            stat = member.lstat()
            req(member.is_file() and not member.is_symlink() and stat.st_nlink == 1
                and stat.st_mode & 0o777 == 0o600,
                f"raw cell {cell} unsafe mode/link/type")
            lines.append(f"{cell}\t{member.name}\t{sha(member)}\n")
    req(seen == set(range(23040)), "raw cell IDs are not exactly 0..23039")
    return {
        "exact_tree": True, "cell_directories": 23040, "files": 46080,
        "tree_digest": hashlib.sha256("".join(sorted(lines)).encode()).hexdigest(),
    }


def manifest_configs() -> tuple[dict[str, Any], dict[int, dict[str, Any]]]:
    req(sha(MANIFEST) == FIXED["manifest"], "manifest hash drift")
    manifest = strict_json(MANIFEST)
    req(set(manifest) == {
        "artifacts", "campaign", "cells", "defaults", "field_pack_sha256",
        "preregistration", "profiles", "schema",
    } and manifest["schema"] == "grid2d-one-two-target-gating-gpu-v4-r2-manifest"
      and manifest["campaign"].get("kind") == "production"
      and manifest["campaign"].get("cell_count") == 23040
      and manifest["field_pack_sha256"] == FIXED["field"],
      "manifest exact identity drift")
    defaults = manifest["defaults"]
    required_defaults = {
        "base_hold", "batch_size", "checkpoints", "seed_base", "start_x",
        "start_y", "steps", "target1_x", "target1_y", "target_radius", "walkers",
    }
    req(isinstance(defaults, dict) and set(defaults) == required_defaults
        and defaults["walkers"] == 1_000_000 and defaults["steps"] == 80_000
        and defaults["checkpoints"] == [5000, 10000, 20000, 40000, 80000],
        "manifest defaults drift")
    cells = manifest["cells"]
    req(isinstance(cells, list) and len(cells) == 23040, "manifest cell count drift")
    configs: dict[int, dict[str, Any]] = {}; identities: set[tuple[Any, ...]] = set()
    for item in cells:
        req(isinstance(item, dict) and set(item) == {
            "amplitude", "cell_id", "disorder_replicate", "target2_x",
            "target2_y", "walk_replicate", "walk_seed",
        }, "manifest cell exact keys drift")
        cell = item["cell_id"]
        req(isinstance(cell, int) and not isinstance(cell, bool)
            and 0 <= cell < 23040 and cell not in configs,
            "manifest cell ID drift")
        identity = (item["target2_x"], item["target2_y"], item["amplitude"],
                    item["disorder_replicate"], item["walk_replicate"])
        req(identity not in identities, "manifest duplicate scientific identity")
        identities.add(identity); configs[cell] = item
    expected = {
        (x, y, amplitude, block, walk)
        for x in (24, 32, 40) for y in (9, 16, 24, 31, 38)
        for amplitude in (0.0, 0.05, 0.1, 0.15, 0.2, 0.25)
        for block in range(128) for walk in (0, 1)
    }
    req(set(configs) == set(range(23040)) and identities == expected,
        "manifest exact scientific inventory drift")
    return manifest, configs


def gpu_count(tres: str) -> int:
    total = 0
    for token in tres.split(","):
        key, separator, value = token.partition("=")
        if separator and (key == "gres/gpu" or key.startswith("gres/gpu:") or key == "gpu"):
            total += int(value)
    return total


def replay_sacct(path: Path, array_job: str, inventory: list[dict[str, Any]]) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        rows = list(reader); header = reader.fieldnames
    expected_header = [
        "JobIDRaw", "JobID", "ArrayJobID", "ArrayTaskID", "State",
        "ExitCode", "ElapsedRaw", "AllocTRES", "ReqTRES", "NNodes",
    ]
    req(header == expected_header, "extended sacct exact header drift")
    task_jobs: dict[int, set[str]] = {}; task_cells = {task: set() for task in range(480)}
    for row in inventory:
        task = int(row["slurm_array_task_id"])
        req(row["slurm_array_job_id"] == array_job
            and task == row["cell_id"] % 480,
            "reduction inventory task mapping drift")
        task_cells[task].add(row["cell_id"])
        task_jobs.setdefault(task, set()).add(row["slurm_job_id"])
    for task in range(480):
        expected_cells = {task + 480 * (gpu + 4 * bundle)
                          for gpu in range(4) for bundle in range(12)}
        req(task_cells[task] == expected_cells and len(task_jobs[task]) == 1,
            f"task {task} exact 48-cell/allocation mapping drift")
    seen: dict[int, dict[str, str]] = {}; parent_rows = 0; elapsed = 0
    for row in rows:
        req(set(row) == set(expected_header)
            and all(value is not None for value in row.values()),
            "extended sacct row shape drift")
        if row["JobIDRaw"] == array_job and row["JobID"] == array_job:
            parent_rows += 1
            req(row["State"].split("+")[0] == "COMPLETED"
                and row["ExitCode"] == "0:0", "array parent did not complete")
            continue
        match = re.fullmatch(re.escape(array_job) + r"_([0-9]+)", row["JobID"])
        req(match is not None and "." not in row["JobID"],
            "unexpected extended sacct non-task row")
        task = int(match.group(1))
        req(0 <= task < 480 and task not in seen
            and row["ArrayJobID"] == array_job
            and row["ArrayTaskID"] == str(task)
            and row["JobIDRaw"] in task_jobs[task],
            "extended sacct task identity/bijection drift")
        seconds = int(row["ElapsedRaw"]); nodes = int(row["NNodes"])
        req(row["State"].split("+")[0] == "COMPLETED"
            and row["ExitCode"] == "0:0" and seconds > 0 and nodes == 1,
            f"task {task} completion/elapsed/node drift")
        req(gpu_count(row["AllocTRES"]) == gpu_count(row["ReqTRES"]) == 4,
            f"task {task} did not request and allocate four GPUs")
        seen[task] = row; elapsed += seconds
    req(parent_rows == 1 and set(seen) == set(range(480)) and len(rows) == 481,
        "extended sacct exact parent plus 480-task inventory drift")
    return {
        "independently_parsed": True, "array_job_id": array_job,
        "parent_rows": 1, "tasks": 480, "unique_allocations": 480,
        "cells_per_allocation": 48, "gpus_per_allocation": 4,
        "nodes_per_allocation": 1, "elapsed_raw_total_seconds": elapsed,
        "actual_full_node_nhr": elapsed / 3600.0,
        "receipt_sha256": sha(path),
    }


def replay_raw_cell(
    *, json_path: Path, npz_path: Path, manifest: dict[str, Any],
    config: dict[str, Any], inventory: dict[str, Any], array_job: str,
) -> float:
    cell = config["cell_id"]; payload = strict_json(json_path, mode600=True)
    req(set(payload) == {
        "schema", "manifest", "parameters", "domain", "rng", "field",
        "one_target", "two_targets", "paired_outcomes", "cumulative_counts",
        "histograms", "gates", "gating_probability_drop",
        "gating_probability_ratio", "target2_first_probability",
        "provenance", "runtime",
    }, f"raw cell {cell} exact JSON top keys drift")
    req(payload["schema"] == "grid2d-one-two-target-gating-fixed-mean-gpu-v4-r2",
        f"raw cell {cell} result schema drift")
    manifest_record = payload["manifest"]
    req(manifest_record == {
        "filename": MANIFEST.name, "sha256": FIXED["manifest"],
        "schema": "grid2d-one-two-target-gating-gpu-v4-r2-manifest",
        "cell_id": cell, "profile": None,
    }, f"raw cell {cell} manifest reverse binding drift")
    defaults = manifest["defaults"]
    parameters = payload["parameters"]
    expected_parameters = {
        "walkers": defaults["walkers"], "steps": defaults["steps"],
        "batch_size": defaults["batch_size"], "base_hold": defaults["base_hold"],
        "amplitude": config["amplitude"], "target_radius": defaults["target_radius"],
        "disorder_replicate": config["disorder_replicate"],
        "walk_replicate": config["walk_replicate"],
        "checkpoints": defaults["checkpoints"],
    }
    req(isinstance(parameters, dict)
        and set(parameters) == set(expected_parameters) | {"disorder_seed"}
        and all(parameters[key] == value for key, value in expected_parameters.items())
        and isinstance(parameters["disorder_seed"], int)
        and not isinstance(parameters["disorder_seed"], bool),
        f"raw cell {cell} parameter/config binding drift")
    domain = payload["domain"]
    req(domain.get("start") == {"x": defaults["start_x"], "y": defaults["start_y"]}
        and domain.get("target1") == {"x": defaults["target1_x"], "y": defaults["target1_y"]}
        and domain.get("target2") == {"x": config["target2_x"], "y": config["target2_y"]},
        f"raw cell {cell} domain/config binding drift")
    rng = payload["rng"]
    req(isinstance(rng, dict) and set(rng) == {
        "algorithm", "walk_seed", "walk_seed_origin", "disorder_stride",
        "walk_stride", "batch_seed_rule", "common_random_numbers",
        "deterministic_for_fixed_manifest_runtime_device",
    } and rng["walk_seed"] == config["walk_seed"]
      and rng["walk_seed_origin"] == "manifest_explicit"
      and rng["batch_seed_rule"] == "walk_seed_plus_batch_start"
      and rng["common_random_numbers"] is True,
      f"raw cell {cell} RNG/config binding drift")
    field = payload["field"]
    req(field.get("pack_filename") == FIELD.name
        and field.get("pack_sha256") == FIXED["field"]
        and field.get("expected_pack_sha256") == FIXED["field"],
        f"raw cell {cell} field-pack binding drift")
    provenance = payload["provenance"]; slurm = provenance.get("slurm", {})
    req(provenance.get("source") == "gpu_gating_mc_v4_r2.py"
        and provenance.get("source_sha256") == sha(ROOT / "code/gpu_gating_mc_v4_r2.py")
        and slurm.get("SLURM_ARRAY_JOB_ID") == array_job
        and slurm.get("SLURM_ARRAY_TASK_ID") == str(cell % 480)
        and slurm.get("SLURM_JOB_ID") == inventory["slurm_job_id"],
        f"raw cell {cell} source/Slurm binding drift")
    histograms = payload["histograms"]
    req(histograms.get("path") == npz_path.name
        and histograms.get("sha256") == sha(npz_path)
        and histograms.get("dtype") == "int64",
        f"raw cell {cell} NPZ reverse binding drift")
    req(payload["gates"].get("all_passed") is True,
        f"raw cell {cell} scientific gates failed")
    with np.load(npz_path, allow_pickle=False) as archive:
        keys = {
            "schema_version", "one_target1_fpt_histogram",
            "two_target1_fpt_histogram", "two_target2_fpt_histogram",
            "checkpoint_steps", "checkpoint_counts", "paired_outcome_counts",
        }
        req(set(archive.files) == keys, f"raw cell {cell} NPZ exact keys drift")
        arrays = {key: np.asarray(archive[key]) for key in keys}
    steps = defaults["steps"]; checkpoints = defaults["checkpoints"]
    shapes = {
        "schema_version": (), "one_target1_fpt_histogram": (steps + 1,),
        "two_target1_fpt_histogram": (steps + 1,),
        "two_target2_fpt_histogram": (steps + 1,),
        "checkpoint_steps": (len(checkpoints),),
        "checkpoint_counts": (len(checkpoints), 6),
        "paired_outcome_counts": (3, 3),
    }
    for key, array in arrays.items():
        req(array.dtype == np.dtype(np.int64) and array.shape == shapes[key]
            and bool(np.all(array >= 0)),
            f"raw cell {cell} {key} dtype/shape/sign drift")
    req(int(arrays["schema_version"]) == 3
        and arrays["checkpoint_steps"].tolist() == checkpoints,
        f"raw cell {cell} NPZ schema/checkpoint drift")
    walkers = defaults["walkers"]
    one = arrays["one_target1_fpt_histogram"]
    two1 = arrays["two_target1_fpt_histogram"]
    two2 = arrays["two_target2_fpt_histogram"]
    checkpoint_counts = arrays["checkpoint_counts"]
    paired = arrays["paired_outcome_counts"]
    for key in (
        "one_target1_fpt_histogram", "two_target1_fpt_histogram",
        "two_target2_fpt_histogram", "checkpoint_counts", "paired_outcome_counts",
    ):
        req(bool(np.all(arrays[key] <= walkers)),
            f"raw cell {cell} {key} exceeds walker mass")
    req(int(paired.sum(dtype=np.int64)) == walkers
        and int(paired[0, 1]) == 0 and bool(np.all(paired[2, :] == 0)),
        f"raw cell {cell} paired mass/state drift")
    one_hits = int(one.sum(dtype=np.int64)); two1_hits = int(two1.sum(dtype=np.int64))
    two2_hits = int(two2.sum(dtype=np.int64))
    req(one_hits == int(paired[1, :].sum(dtype=np.int64))
        and two1_hits == int(paired[:, 1].sum(dtype=np.int64))
        and two2_hits == int(paired[:, 2].sum(dtype=np.int64)),
        f"raw cell {cell} histogram/paired mass drift")
    req(bool(np.all(checkpoint_counts[:, 0] + checkpoint_counts[:, 1] == walkers))
        and bool(np.all(checkpoint_counts[:, 2] + checkpoint_counts[:, 3]
                        + checkpoint_counts[:, 4] == walkers))
        and bool(np.all(checkpoint_counts[:, 5] == walkers)),
        f"raw cell {cell} checkpoint mass drift")
    req(checkpoint_counts[-1].tolist() == [
        one_hits, walkers - one_hits, two1_hits, two2_hits,
        walkers - two1_hits - two2_hits, walkers,
    ], f"raw cell {cell} final checkpoint drift")
    req(int(one[:checkpoints[-1] + 1].sum(dtype=np.int64)) == one_hits
        and int(two1[:checkpoints[-1] + 1].sum(dtype=np.int64)) == two1_hits,
        f"raw cell {cell} histogram horizon drift")
    metric = (one_hits - two1_hits) / walkers
    req(payload["one_target"].get("target1", {}).get("hits") == one_hits
        and payload["two_targets"].get("target1", {}).get("hits") == two1_hits
        and payload["two_targets"].get("target2", {}).get("hits") == two2_hits
        and payload["gating_probability_drop"] == metric,
        f"raw cell {cell} JSON/NPZ statistic drift")
    return metric


def replay(
    *, run: str, array: str, reducer: str, reduction_sha: str, h1_sha: str,
    production_submit: Path, production_submit_sha: str,
    reducer_submit: Path, reducer_submit_sha: str,
) -> dict[str, Any]:
    req(run == array and all(DECIMAL.fullmatch(value) is not None
                             for value in (run, array, reducer)),
        "run token must equal decimal production array ID")
    req(HEX64.fullmatch(reduction_sha) is not None
        and HEX64.fullmatch(h1_sha) is not None
        and sha(PAYLOAD) == h1_sha and sha(MANIFEST) == FIXED["manifest"]
        and sha(FIELD) == FIXED["field"] and sha(BASE_PAYLOAD) == FIXED["base_payload"]
        and sha(CONTAINER) == FIXED["container"],
        "fixed artifact drift")
    submission_chain = validate_submission_chain(
        array_job=array, reducer_job=reducer, h1_sha=h1_sha,
        production_path=production_submit, production_sha=production_submit_sha,
        reducer_path=reducer_submit, reducer_sha=reducer_submit_sha,
    )
    raw_root = ROOT / f"artifacts/outputs/isambard_ai_v4_r2/production-{run}"
    reduction_dir = ROOT / f"artifacts/outputs/isambard_ai_v4_r2/reduction-{run}-{reducer}"
    req(reduction_dir.is_dir() and not reduction_dir.is_symlink()
        and {member.name for member in reduction_dir.iterdir()} == {
            "reduction_v4_r2.json", "reduction_v4_r2.csv", f"sacct-v4-r2-{array}.psv"
        }, "reduction exact directory inventory drift")
    reduction_json = reduction_dir / "reduction_v4_r2.json"
    reduction_csv = reduction_dir / "reduction_v4_r2.csv"
    sacct_path = reduction_dir / f"sacct-v4-r2-{array}.psv"
    for path in (reduction_json, reduction_csv, sacct_path):
        stat = path.lstat()
        req(path.is_file() and not path.is_symlink() and stat.st_nlink == 1
            and stat.st_mode & 0o777 == 0o600,
            "unsafe reduction artifact mode/link/type")
    req(sha(reduction_json) == reduction_sha, "reduction JSON pin drift")
    manifest, configs = manifest_configs(); tree = exact_tree(raw_root)
    reduction = strict_json(reduction_json, mode600=True)
    req(set(reduction) == {
        "schema", "mode", "audit", "inventory", "method", "conditions",
        "tail_gate", "primary", "evidence_decision", "csv",
    } and reduction["schema"] == "grid2d-one-two-target-gating-gpu-v4-r2-reduction-v1"
      and reduction["mode"] == "full", "reduction exact top-level contract drift")
    audit = reduction["audit"]
    req(isinstance(audit, dict) and set(audit) == {
        "pass", "fail_closed", "campaign_kind", "manifest_schema",
        "manifest_filename", "manifest_sha256", "field_pack_filename",
        "field_pack_sha256", "source_filename", "source_sha256", "cell_count",
        "inventory_digest", "sacct",
    } and audit["pass"] is True and audit["fail_closed"] is True
      and audit["campaign_kind"] == "production"
      and audit["manifest_schema"] == "grid2d-one-two-target-gating-gpu-v4-r2-manifest"
      and audit["manifest_filename"] == MANIFEST.name
      and audit["manifest_sha256"] == FIXED["manifest"]
      and audit["field_pack_filename"] == FIELD.name
      and audit["field_pack_sha256"] == FIXED["field"]
      and audit["source_filename"] == "gpu_gating_mc_v4_r2.py"
      and audit["source_sha256"] == sha(ROOT / "code/gpu_gating_mc_v4_r2.py")
      and audit["cell_count"] == 23040,
      "reduction exact audit contract drift")
    inventory = reduction["inventory"]
    inventory_keys = {
        "cell_id", "profile", "json_path", "json_sha256", "npz_path",
        "npz_sha256", "slurm_array_job_id", "slurm_array_task_id", "slurm_job_id",
    }
    req(isinstance(inventory, list) and len(inventory) == 23040
        and all(isinstance(row, dict) and set(row) == inventory_keys for row in inventory),
        "reduction inventory exact schema/count drift")
    inventory_by_id: dict[int, dict[str, Any]] = {}; inventory_lines: list[str] = []
    for row in inventory:
        cell = row["cell_id"]
        req(isinstance(cell, int) and not isinstance(cell, bool)
            and 0 <= cell < 23040 and cell not in inventory_by_id
            and row["profile"] is None
            and row["json_path"] == f"cell-{cell}/cell-{cell}.json"
            and row["npz_path"] == f"cell-{cell}/cell-{cell}.npz"
            and isinstance(row["json_sha256"], str)
            and HEX64.fullmatch(row["json_sha256"]) is not None
            and isinstance(row["npz_sha256"], str)
            and HEX64.fullmatch(row["npz_sha256"]) is not None
            and row["slurm_array_job_id"] == array
            and row["slurm_array_task_id"] == str(cell % 480)
            and isinstance(row["slurm_job_id"], str)
            and DECIMAL.fullmatch(row["slurm_job_id"]) is not None,
            f"reduction inventory cell {cell} field drift")
        inventory_by_id[cell] = row
        inventory_lines.append(
            f"{cell}\t{row['json_path']}\t{row['json_sha256']}\t"
            f"{row['npz_path']}\t{row['npz_sha256']}\n"
        )
    req(set(inventory_by_id) == set(range(23040)), "reduction inventory IDs drift")
    inventory_digest = hashlib.sha256("".join(inventory_lines).encode()).hexdigest()
    req(audit["inventory_digest"] == inventory_digest,
        "reduction inventory digest recomputation drift")
    sacct = replay_sacct(sacct_path, array, inventory)
    claimed_sacct = audit["sacct"]
    req(isinstance(claimed_sacct, dict) and set(claimed_sacct) == {
        "provided", "verified", "receipt_filename", "receipt_sha256",
        "allocations_verified", "cells_verified", "cells_per_allocation",
        "bundled_production", "full_node_gpus", "n_nodes_per_allocation",
        "elapsed_raw_total_seconds", "actual_full_node_nhr",
        "reservation_ceiling_nhr", "extended_fields",
    } and claimed_sacct["provided"] is True and claimed_sacct["verified"] is True
      and claimed_sacct["receipt_filename"] == sacct_path.name
      and claimed_sacct["receipt_sha256"] == sacct["receipt_sha256"]
      and claimed_sacct["allocations_verified"] == 480
      and claimed_sacct["cells_verified"] == 23040
      and claimed_sacct["cells_per_allocation"] == 48
      and claimed_sacct["bundled_production"] is True
      and claimed_sacct["full_node_gpus"] == 4
      and claimed_sacct["n_nodes_per_allocation"] == 1
      and claimed_sacct["elapsed_raw_total_seconds"] == sacct["elapsed_raw_total_seconds"]
      and claimed_sacct["actual_full_node_nhr"] == sacct["actual_full_node_nhr"],
      "reducer/independent extended sacct drift")
    csv_record = reduction["csv"]
    req(isinstance(csv_record, dict) and set(csv_record) == {
        "filename", "sha256", "rows"
    } and csv_record["filename"] == reduction_csv.name
      and csv_record["sha256"] == sha(reduction_csv)
      and csv_record["rows"] == 11648,
      "reduction CSV receipt drift")
    with reduction_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle); csv_rows = list(reader); header = reader.fieldnames
    req(header == CSV_FIELDS and len(csv_rows) == 11648,
        "reduction CSV exact header/row count drift")
    csv_blocks: dict[tuple[int, int, float, int], float] = {}; primary_rows = 0
    for row in csv_rows:
        req(set(row) == set(CSV_FIELDS) and all(value is not None for value in row.values()),
            "reduction CSV row shape drift")
        if row["row_type"] == "primary_pair":
            primary_rows += 1; continue
        req(row["row_type"] == "block_mean" and row["walk_replicates"] == "0;1",
            "reduction CSV row type/stream drift")
        key = (int(row["target2_x"]), int(row["target2_y"]),
               float(row["amplitude"]), int(row["disorder_replicate"]))
        value = float(row["gating_probability_drop"])
        req(key not in csv_blocks and math.isfinite(value),
            "duplicate/nonfinite reduction CSV block")
        csv_blocks[key] = value
    req(primary_rows == 128 and len(csv_blocks) == 11520,
        "reduction CSV scientific inventory drift")
    streams: dict[tuple[int, int, float, int], dict[int, float]] = {}
    for cell in range(23040):
        config = configs[cell]; row = inventory_by_id[cell]
        json_path = raw_root / row["json_path"]; npz_path = raw_root / row["npz_path"]
        req(sha(json_path) == row["json_sha256"] and sha(npz_path) == row["npz_sha256"],
            f"raw cell {cell} inventory reverse hash drift")
        metric = replay_raw_cell(
            json_path=json_path, npz_path=npz_path, manifest=manifest,
            config=config, inventory=row, array_job=array,
        )
        key = (config["target2_x"], config["target2_y"], config["amplitude"],
               config["disorder_replicate"])
        by_walk = streams.setdefault(key, {})
        walk = config["walk_replicate"]
        req(walk not in by_walk, f"duplicate raw walk stream at {key}")
        by_walk[walk] = metric
    blocks: dict[tuple[int, int, float, int], float] = {}
    for key, by_walk in streams.items():
        req(set(by_walk) == {0, 1}, f"raw walk pair drift at {key}")
        blocks[key] = math.fsum((by_walk[0], by_walk[1])) / 2.0
    req(len(blocks) == 11520 and set(blocks) == set(csv_blocks),
        "raw/CSV block inventory drift")
    for key, value in blocks.items():
        req(math.isclose(value, csv_blocks[key], rel_tol=0.0, abs_tol=1e-15),
            f"raw/CSV block value drift at {key}")
    block_digest = hashlib.sha256("".join(
        f"{x}\t{y}\t{amplitude.hex()}\t{block}\t{value.hex()}\n"
        for (x, y, amplitude, block), value in sorted(blocks.items())
    ).encode()).hexdigest()
    output = {
        "schema": "grid2d-one-two-target-gating-v4-r2-independent-replay-h1",
        "status": "PASS_AUTHORIZE_V3_V4_R2_H1_COMBINED",
        "fixed_root": str(ROOT),
        "jobs": {"run_token": run, "array": array, "reducer": reducer},
        "fixed_artifacts": {
            "manifest_sha256": FIXED["manifest"],
            "field_pack_sha256": FIXED["field"],
            "base_payload_sha256": FIXED["base_payload"],
            "h1_payload_sha256": h1_sha,
            "container_sha256": FIXED["container"],
        },
        "hashes": {
            "reduction_json": sha(reduction_json),
            "reduction_csv": sha(reduction_csv),
            "sacct_receipt": sha(sacct_path),
        },
        "raw": {
            "exact_tree": tree, "cells": 23040, "pairs": 23040,
            "blocks": 11520, "raw_inventory_digest": inventory_digest,
            "recomputed_block_digest": block_digest,
        },
        "reduction_inventory_digest": inventory_digest,
        "extended_sacct": sacct,
        "submission_chain": submission_chain,
    }
    req(set(output) == OUTPUT_KEYS, "internal replay receipt key drift")
    return output


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    req(not path.exists(), "replay receipt exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".h1-replay.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-token", required=True)
    parser.add_argument("--array-job", required=True)
    parser.add_argument("--reducer-job", required=True)
    parser.add_argument("--reduction-sha256", required=True)
    parser.add_argument("--h1-payload-sha256", required=True)
    parser.add_argument("--production-submit", type=Path, required=True)
    parser.add_argument("--production-submit-sha256", required=True)
    parser.add_argument("--reducer-submit", type=Path, required=True)
    parser.add_argument("--reducer-submit-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        expected_output = ROOT / f"artifacts/replay/v4-r2-replay-h1-{args.reducer_job}.json"
        req(args.output == expected_output, "replay output path drift")
        payload = replay(
            run=args.run_token, array=args.array_job, reducer=args.reducer_job,
            reduction_sha=args.reduction_sha256, h1_sha=args.h1_payload_sha256,
            production_submit=args.production_submit,
            production_submit_sha=args.production_submit_sha256,
            reducer_submit=args.reducer_submit,
            reducer_submit_sha=args.reducer_submit_sha256,
        )
        commit(args.output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": sha(args.output)},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
