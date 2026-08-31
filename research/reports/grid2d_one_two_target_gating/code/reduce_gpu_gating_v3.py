#!/usr/bin/env python3
"""Strict independent reducer for the frozen Isambard-AI gating v3 campaign.

The manifest is the inventory authority, while result identity comes only from
``payload["manifest"]["cell_id"]``.  Every JSON/NPZ pair is independently
recomputed and cross-checked before block-level statistics are produced.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import statistics
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

MANIFEST_SCHEMA = "grid2d-one-two-target-gating-gpu-v3-manifest"
RESULT_SCHEMA = "grid2d-one-two-target-gating-fixed-mean-gpu-v3"
REDUCTION_SCHEMA = "grid2d-one-two-target-gating-gpu-v3-reduction-v1"
SIDECAR_SCHEMA_VERSION = 3
REQUIRED_MANIFEST_KEYS = {
    "schema",
    "defaults",
    "profiles",
    "cells",
    "field_pack_sha256",
}
DISORDER_SEED_STRIDE = 104_729
WALK_SEED_STRIDE = 1_009
FIXED_MEAN_ATOL = 1.0e-12
FLOAT_ATOL = 1.0e-12
CONFIDENCE_LEVEL = 0.95
FROZEN_PRIMARY_TARGET2 = (32, 24)
FROZEN_PRIMARY_AMPLITUDES = (0.0, 0.2)
FROZEN_PRIMARY_ROPE = (-0.002, 0.002)
FROZEN_TAIL_ANCHORS = ((24, 24), (32, 24), (40, 24))
FROZEN_TAIL_AMPLITUDES = (0.0, 0.2)
FROZEN_TAIL_UNRESOLVED_LIMIT = 0.005
FROZEN_TAIL_STABILITY_LIMIT = 0.002
SIDECAR_KEYS = {
    "schema_version",
    "one_target1_fpt_histogram",
    "two_target1_fpt_histogram",
    "two_target2_fpt_histogram",
    "checkpoint_steps",
    "checkpoint_counts",
    "paired_outcome_counts",
}


class AuditError(RuntimeError):
    """Raised whenever the reducer must fail closed."""


@dataclass(frozen=True)
class CellConfig:
    cell_id: int
    profile: str | None
    walkers: int
    steps: int
    batch_size: int
    base_hold: float
    amplitude: float
    target_radius: int
    start_x: int
    start_y: int
    target1_x: int
    target1_y: int
    target2_x: int
    target2_y: int
    disorder_replicate: int
    walk_replicate: int
    checkpoints: tuple[int, ...]
    walk_seed: int
    walk_seed_origin: str


@dataclass(frozen=True)
class DiscoveredResult:
    path: Path
    raw: bytes
    payload: dict[str, Any]
    cell_id: int
    sidecar_path: Path


@dataclass(frozen=True)
class ValidatedCell:
    config: CellConfig
    json_path: Path
    json_sha256: str
    npz_path: Path
    npz_sha256: str
    slurm_array_job_id: str | None
    slurm_array_task_id: str | None
    slurm_job_id: str | None
    metrics: dict[str, float]


def _fail(message: str) -> None:
    raise AuditError(message)


def _require(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def _integer(value: Any, label: str, *, minimum: int | None = None) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool), f"{label} must be an integer")
    result = int(value)
    if minimum is not None:
        _require(result >= minimum, f"{label} must be >= {minimum}")
    return result


def _number(value: Any, label: str) -> float:
    _require(
        isinstance(value, (int, float)) and not isinstance(value, bool),
        f"{label} must be numeric",
    )
    result = float(value)
    _require(math.isfinite(result), f"{label} must be finite")
    return result


def _close(actual: Any, expected: Any, label: str, *, atol: float = FLOAT_ATOL) -> None:
    left = _number(actual, f"{label} actual")
    right = _number(expected, f"{label} expected")
    _require(
        math.isclose(left, right, rel_tol=atol, abs_tol=atol),
        f"{label} mismatch: expected {right!r}, got {left!r}",
    )


def _count(value: Any, label: str) -> int:
    return _integer(value, label, minimum=0)


def _mapping(value: Any, label: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{label} must be an object")
    return dict(value)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256(value: Any, label: str) -> str:
    _require(isinstance(value, str), f"{label} must be a SHA-256 string")
    normalized = value.lower()
    _require(
        len(normalized) == 64 and all(character in "0123456789abcdef" for character in normalized),
        f"{label} must contain 64 hexadecimal digits",
    )
    return normalized


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _load_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"{label} is not valid UTF-8 JSON: {exc}")
    _require(isinstance(payload, dict), f"{label} root must be an object")
    _finite_tree(payload, label)
    return payload


def _finite_tree(value: Any, label: str) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        _require(math.isfinite(value), f"{label} contains a non-finite scalar")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _finite_tree(item, f"{label}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _finite_tree(item, f"{label}.{key}")
        return
    _fail(f"{label} contains unsupported JSON type {type(value).__name__}")


def _coordinate(parameters: Mapping[str, Any], prefix: str) -> tuple[int, int]:
    nested = parameters.get(prefix)
    direct_x = f"{prefix}_x"
    direct_y = f"{prefix}_y"
    if nested is not None:
        _require(direct_x not in parameters and direct_y not in parameters, f"{prefix} is duplicated")
        nested_map = _mapping(nested, prefix)
        return (
            _integer(nested_map.get("x"), f"{prefix}.x"),
            _integer(nested_map.get("y"), f"{prefix}.y"),
        )
    _require(direct_x in parameters and direct_y in parameters, f"missing {prefix} coordinates")
    return (
        _integer(parameters[direct_x], direct_x),
        _integer(parameters[direct_y], direct_y),
    )


def _resolve_cell(
    manifest: Mapping[str, Any], raw_cell: Mapping[str, Any], width: int, height: int
) -> CellConfig:
    cell_id = _integer(raw_cell.get("cell_id"), "cell_id", minimum=0)
    defaults = _mapping(manifest.get("defaults"), "defaults")
    profiles = _mapping(manifest.get("profiles"), "profiles")
    profile_value = raw_cell.get("profile", manifest.get("default_profile"))
    if profile_value is None:
        profile: str | None = None
    else:
        _require(isinstance(profile_value, str) and profile_value, f"cell {cell_id} profile is invalid")
        _require(profile_value in profiles, f"cell {cell_id} has unknown profile {profile_value!r}")
        profile = profile_value
    parameters = dict(defaults)
    if profile is not None:
        parameters.update(_mapping(profiles[profile], f"profiles.{profile}"))
    nested = raw_cell.get("parameters")
    if nested is not None:
        parameters.update(_mapping(nested, f"cell {cell_id}.parameters"))
    reserved = {"cell_id", "profile", "parameters", "label", "notes"}
    for key, value in raw_cell.items():
        if key in reserved:
            continue
        if nested is not None:
            _require(key not in nested, f"cell {cell_id} duplicates {key!r} inside parameters")
        parameters[key] = value
    required = (
        "walkers",
        "steps",
        "batch_size",
        "base_hold",
        "amplitude",
        "target_radius",
        "disorder_replicate",
        "walk_replicate",
        "checkpoints",
    )
    missing = [key for key in required if key not in parameters]
    _require(not missing, f"cell {cell_id} missing parameters: {missing}")
    walkers = _integer(parameters["walkers"], "walkers", minimum=1)
    steps = _integer(parameters["steps"], "steps", minimum=1)
    batch_size = _integer(parameters["batch_size"], "batch_size", minimum=1)
    base_hold = _number(parameters["base_hold"], "base_hold")
    amplitude = _number(parameters["amplitude"], "amplitude")
    target_radius = _integer(parameters["target_radius"], "target_radius", minimum=0)
    disorder_replicate = _integer(
        parameters["disorder_replicate"], "disorder_replicate", minimum=0
    )
    walk_replicate = _integer(parameters["walk_replicate"], "walk_replicate", minimum=0)
    start = _coordinate(parameters, "start")
    target1 = _coordinate(parameters, "target1")
    target2 = _coordinate(parameters, "target2")
    for name, (x_value, y_value) in (("start", start), ("target1", target1), ("target2", target2)):
        _require(
            0 <= x_value < width and 0 <= y_value < height,
            f"cell {cell_id} {name}=({x_value},{y_value}) outside {width}x{height}",
        )
    raw_checkpoints = parameters["checkpoints"]
    _require(isinstance(raw_checkpoints, list) and raw_checkpoints, "checkpoints must be nonempty")
    checkpoints = tuple(
        _integer(value, f"checkpoints[{index}]", minimum=0)
        for index, value in enumerate(raw_checkpoints)
    )
    _require(tuple(sorted(set(checkpoints))) == checkpoints, "checkpoints must be strictly increasing")
    _require(checkpoints[-1] == steps, "final checkpoint must equal steps")
    _require(steps // 2 in checkpoints, f"cell {cell_id} lacks the T/2 checkpoint")
    explicit_seed = parameters.get("walk_seed")
    if explicit_seed is None:
        seed_base = _integer(parameters.get("seed_base"), "seed_base", minimum=0)
        walk_seed = seed_base + disorder_replicate * DISORDER_SEED_STRIDE + walk_replicate * WALK_SEED_STRIDE
        walk_seed_origin = "v2_common_random_number_formula"
    else:
        walk_seed = _integer(explicit_seed, "walk_seed", minimum=0)
        walk_seed_origin = "manifest_explicit"
    return CellConfig(
        cell_id=cell_id,
        profile=profile,
        walkers=walkers,
        steps=steps,
        batch_size=batch_size,
        base_hold=base_hold,
        amplitude=amplitude,
        target_radius=target_radius,
        start_x=start[0],
        start_y=start[1],
        target1_x=target1[0],
        target1_y=target1[1],
        target2_x=target2[0],
        target2_y=target2[1],
        disorder_replicate=disorder_replicate,
        walk_replicate=walk_replicate,
        checkpoints=checkpoints,
        walk_seed=walk_seed,
        walk_seed_origin=walk_seed_origin,
    )


def _load_manifest(path: Path, width: int, height: int) -> tuple[dict[str, Any], bytes, dict[int, CellConfig]]:
    _require(path.is_file(), f"manifest does not exist: {path}")
    raw = path.read_bytes()
    manifest = _load_json(raw, "manifest")
    missing = sorted(REQUIRED_MANIFEST_KEYS - set(manifest))
    _require(not missing, f"manifest missing top-level keys: {missing}")
    _require(manifest.get("schema") == MANIFEST_SCHEMA, "manifest schema mismatch")
    _mapping(manifest["defaults"], "defaults")
    profiles = _mapping(manifest["profiles"], "profiles")
    _require(profiles, "profiles must not be empty")
    campaign = _mapping(manifest.get("campaign"), "campaign")
    _require(
        campaign.get("kind") in {"canary", "production"},
        "campaign.kind must be canary or production",
    )
    domain = _mapping(campaign.get("domain"), "campaign.domain")
    _require(
        domain == {"width": width, "height": height},
        "manifest campaign domain does not match the field pack",
    )
    _mapping(manifest.get("artifacts"), "artifacts")
    _mapping(manifest.get("preregistration"), "preregistration")
    cells = manifest["cells"]
    _require(isinstance(cells, list) and cells, "cells must be a nonempty array")
    _require(campaign.get("cell_count") == len(cells), "campaign.cell_count does not match cells")
    configs: dict[int, CellConfig] = {}
    scientific_keys: set[str] = set()
    for index, raw_cell_value in enumerate(cells):
        raw_cell = _mapping(raw_cell_value, f"cells[{index}]")
        config = _resolve_cell(manifest, raw_cell, width, height)
        _require(config.cell_id not in configs, f"duplicate manifest cell_id {config.cell_id}")
        scientific = _condition_payload(config, include_replicates=True)
        key = json.dumps(scientific, sort_keys=True, separators=(",", ":"))
        _require(key not in scientific_keys, f"duplicate scientific cell at cell_id {config.cell_id}")
        scientific_keys.add(key)
        configs[config.cell_id] = config
    expected_ids = set(range(len(cells)))
    _require(
        set(configs) == expected_ids,
        f"production cell IDs are not exact/contiguous; missing={sorted(expected_ids - set(configs))[:8]}, "
        f"extra={sorted(set(configs) - expected_ids)[:8]}",
    )
    return manifest, raw, configs


def _load_field_pack(path: Path, expected_sha256: str) -> tuple[np.ndarray, np.ndarray, str]:
    _require(path.is_file(), f"field pack does not exist: {path}")
    actual = _sha256_file(path)
    _require(actual == expected_sha256, "field-pack SHA-256 does not match manifest")
    try:
        with np.load(path, allow_pickle=False) as pack:
            _require(set(pack.files) >= {"contrasts", "seeds"}, "field pack lacks contrasts/seeds")
            contrasts = np.asarray(pack["contrasts"], dtype=np.float64)
            seeds = np.asarray(pack["seeds"], dtype=np.int64)
    except (OSError, ValueError, EOFError) as exc:
        _fail(f"invalid field-pack NPZ: {exc}")
    _require(contrasts.ndim == 3 and contrasts.shape[0] > 0, "contrasts must be replicate x height x width")
    _require(seeds.shape == (contrasts.shape[0],), "field-pack seed shape mismatch")
    _require(bool(np.isfinite(contrasts).all()), "field pack contains non-finite contrasts")
    return contrasts, seeds, actual


def _condition_payload(config: CellConfig, *, include_replicates: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "profile": config.profile,
        "walkers": config.walkers,
        "steps": config.steps,
        "base_hold": config.base_hold,
        "amplitude": config.amplitude,
        "target_radius": config.target_radius,
        "start_x": config.start_x,
        "start_y": config.start_y,
        "target1_x": config.target1_x,
        "target1_y": config.target1_y,
        "target2_x": config.target2_x,
        "target2_y": config.target2_y,
        "checkpoints": list(config.checkpoints),
    }
    if include_replicates:
        payload.update(
            {
                "batch_size": config.batch_size,
                "disorder_replicate": config.disorder_replicate,
                "walk_replicate": config.walk_replicate,
                "walk_seed": config.walk_seed,
            }
        )
    return payload


def _discover_results(results_dir: Path, manifest_sha256: str, expected_ids: set[int]) -> list[DiscoveredResult]:
    _require(results_dir.is_dir(), f"results directory does not exist: {results_dir}")
    json_paths = sorted(path for path in results_dir.rglob("*.json") if path.is_file())
    _require(json_paths, "results directory contains no JSON results")
    discovered: list[DiscoveredResult] = []
    seen_ids: dict[int, Path] = {}
    referenced_sidecars: set[Path] = set()
    for path in json_paths:
        raw = path.read_bytes()
        payload = _load_json(raw, str(path))
        _require(payload.get("schema") == RESULT_SCHEMA, f"unexpected JSON result schema at {path}")
        manifest_block = _mapping(payload.get("manifest"), f"{path}.manifest")
        cell_id = _integer(manifest_block.get("cell_id"), f"{path}.manifest.cell_id", minimum=0)
        _require(cell_id in expected_ids, f"unexpected result cell_id {cell_id} at {path}")
        _require(cell_id not in seen_ids, f"duplicate result cell_id {cell_id}: {seen_ids.get(cell_id)} and {path}")
        seen_ids[cell_id] = path
        _require(path.name == f"cell-{cell_id}.json", f"cell {cell_id} JSON filename is not canonical")
        _require(manifest_block.get("sha256") == manifest_sha256, f"cell {cell_id} manifest SHA-256 mismatch")
        histogram_block = _mapping(payload.get("histograms"), f"{path}.histograms")
        sidecar_name = histogram_block.get("path")
        _require(isinstance(sidecar_name, str) and sidecar_name, f"cell {cell_id} lacks sidecar path")
        sidecar_relative = Path(sidecar_name)
        _require(
            not sidecar_relative.is_absolute()
            and len(sidecar_relative.parts) == 1
            and sidecar_relative.name == f"cell-{cell_id}.npz",
            f"cell {cell_id} sidecar path is not canonical",
        )
        sidecar_path = (path.parent / sidecar_relative).resolve()
        _require(sidecar_path.is_file(), f"cell {cell_id} sidecar is missing: {sidecar_path}")
        _require(sidecar_path not in referenced_sidecars, f"duplicate sidecar binding: {sidecar_path}")
        referenced_sidecars.add(sidecar_path)
        discovered.append(
            DiscoveredResult(
                path=path.resolve(), raw=raw, payload=payload, cell_id=cell_id, sidecar_path=sidecar_path
            )
        )
    missing = sorted(expected_ids - set(seen_ids))
    _require(not missing, f"missing result cells: {missing}")
    actual_sidecars = {path.resolve() for path in results_dir.rglob("*.npz") if path.is_file()}
    missing_sidecars = sorted(str(path) for path in referenced_sidecars - actual_sidecars)
    extra_sidecars = sorted(str(path) for path in actual_sidecars - referenced_sidecars)
    _require(
        not missing_sidecars and not extra_sidecars,
        f"NPZ inventory mismatch; missing={missing_sidecars}, extra={extra_sidecars}",
    )
    return sorted(discovered, key=lambda item: item.cell_id)


def _load_sidecar(path: Path, config: CellConfig, expected_sha256: str) -> tuple[dict[str, np.ndarray], str]:
    actual_sha256 = _sha256_file(path)
    _require(actual_sha256 == expected_sha256, f"cell {config.cell_id} sidecar SHA-256 mismatch")
    try:
        with np.load(path, allow_pickle=False) as archive:
            _require(set(archive.files) == SIDECAR_KEYS, f"cell {config.cell_id} sidecar keys mismatch")
            arrays = {name: np.asarray(archive[name]) for name in archive.files}
    except (OSError, ValueError, EOFError) as exc:
        _fail(f"cell {config.cell_id} sidecar cannot be read safely: {exc}")
    for name, array in arrays.items():
        _require(array.dtype == np.int64, f"cell {config.cell_id} sidecar {name} is not int64")
    schema_version = arrays["schema_version"]
    _require(schema_version.shape == (), f"cell {config.cell_id} schema_version must be scalar")
    _require(int(schema_version) == SIDECAR_SCHEMA_VERSION, f"cell {config.cell_id} sidecar schema mismatch")
    expected_shapes = {
        "one_target1_fpt_histogram": (config.steps + 1,),
        "two_target1_fpt_histogram": (config.steps + 1,),
        "two_target2_fpt_histogram": (config.steps + 1,),
        "checkpoint_steps": (len(config.checkpoints),),
        "checkpoint_counts": (len(config.checkpoints), 6),
        "paired_outcome_counts": (3, 3),
    }
    for name, shape in expected_shapes.items():
        _require(arrays[name].shape == shape, f"cell {config.cell_id} sidecar {name} shape mismatch")
        _require(bool(np.all(arrays[name] >= 0)), f"cell {config.cell_id} sidecar {name} is negative")
    _require(
        bool(
            np.array_equal(
                arrays["checkpoint_steps"],
                np.asarray(config.checkpoints, dtype=np.int64),
            )
        ),
        f"cell {config.cell_id} checkpoint schedule mismatch",
    )
    return arrays, actual_sha256


def _histogram_summary(histogram: np.ndarray, walkers: int) -> dict[str, Any]:
    hits = int(histogram.sum(dtype=np.int64))
    probability = hits / walkers
    if hits == 0:
        return {
            "hits": 0,
            "probability": 0.0,
            "standard_error": 0.0,
            "mean_fpt": None,
            "median_fpt": None,
            "q90_fpt": None,
        }
    cumulative = np.cumsum(histogram, dtype=np.int64)
    times = np.arange(histogram.size, dtype=np.float64)

    def quantile(level: float) -> int:
        return int(np.searchsorted(cumulative, math.ceil(level * hits), side="left"))

    return {
        "hits": hits,
        "probability": probability,
        "standard_error": math.sqrt(probability * (1.0 - probability) / walkers),
        "mean_fpt": float(np.dot(times, histogram.astype(np.float64)) / hits),
        "median_fpt": quantile(0.5),
        "q90_fpt": quantile(0.9),
    }


def _check_summary(actual_value: Any, expected: Mapping[str, Any], label: str) -> None:
    actual = _mapping(actual_value, label)
    _require(set(actual) == set(expected), f"{label} fields mismatch")
    for key, expected_value in expected.items():
        actual_value = actual[key]
        if expected_value is None:
            _require(actual_value is None, f"{label}.{key} must be null")
        elif isinstance(expected_value, int):
            _require(_integer(actual_value, f"{label}.{key}") == expected_value, f"{label}.{key} mismatch")
        else:
            _close(actual_value, expected_value, f"{label}.{key}")


def _check_mapping_exact(actual: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    _require(set(actual) == set(expected), f"{label} fields mismatch")
    for key, expected_value in expected.items():
        actual_value = actual[key]
        if isinstance(expected_value, float):
            _close(actual_value, expected_value, f"{label}.{key}")
        else:
            _require(actual_value == expected_value, f"{label}.{key} mismatch")


def _check_gate_payload(payload: Mapping[str, Any], paired: np.ndarray, hold: np.ndarray, config: CellConfig) -> None:
    gates = _mapping(payload.get("gates"), f"cell {config.cell_id}.gates")
    expected_names = {
        "mass",
        "subset",
        "monotone",
        "in_range",
        "fixed_mean",
        "checkpoint_histogram_consistency",
        "absorbing_precedence",
        "all_passed",
    }
    _require(set(gates) == expected_names, f"cell {config.cell_id} gate fields mismatch")
    _require(gates["all_passed"] is True, f"cell {config.cell_id} runner gates did not all pass")
    for name in expected_names - {"all_passed"}:
        gate = _mapping(gates[name], f"cell {config.cell_id}.gates.{name}")
        _require(gate.get("passed") is True, f"cell {config.cell_id} gate {name} failed")
    subset = _mapping(gates["subset"], "subset gate")
    _require(
        subset.get("invalid_two_target1_not_one_target1") == int(paired[0, 1]),
        f"cell {config.cell_id} subset gate count mismatch",
    )
    fixed_mean = _mapping(gates["fixed_mean"], "fixed_mean gate")
    _close(fixed_mean.get("observed"), float(hold.mean(dtype=np.float64)), "fixed_mean observed")
    _close(fixed_mean.get("expected"), config.base_hold, "fixed_mean expected")


def _validate_arrays_and_payload(
    payload: Mapping[str, Any], arrays: Mapping[str, np.ndarray], config: CellConfig
) -> dict[str, float]:
    walkers = config.walkers
    one_hist = arrays["one_target1_fpt_histogram"]
    two_hist1 = arrays["two_target1_fpt_histogram"]
    two_hist2 = arrays["two_target2_fpt_histogram"]
    checkpoint_steps = arrays["checkpoint_steps"]
    checkpoints = arrays["checkpoint_counts"]
    paired = arrays["paired_outcome_counts"]
    _require(bool(np.all(two_hist1 <= one_hist)), f"cell {config.cell_id} histogram subset violation")
    _require(int(paired[0, 1]) == 0, f"cell {config.cell_id} paired subset violation")
    _require(bool(np.all(paired[2, :] == 0)), f"cell {config.cell_id} invalid one-target state 2")
    _require(int(paired.sum(dtype=np.int64)) == walkers, f"cell {config.cell_id} paired mass mismatch")
    one_summary = _histogram_summary(one_hist, walkers)
    two_summary1 = _histogram_summary(two_hist1, walkers)
    two_summary2 = _histogram_summary(two_hist2, walkers)
    one_hits = int(one_summary["hits"])
    two_hits1 = int(two_summary1["hits"])
    two_hits2 = int(two_summary2["hits"])
    one_unresolved = walkers - one_hits
    two_unresolved = walkers - two_hits1 - two_hits2
    _require(one_unresolved >= 0 and two_unresolved >= 0, f"cell {config.cell_id} negative unresolved count")
    _require(int(paired[0, :].sum()) == one_unresolved, f"cell {config.cell_id} paired one-unresolved mismatch")
    _require(int(paired[1, :].sum()) == one_hits, f"cell {config.cell_id} paired one-hit mismatch")
    _require(int(paired[:, 0].sum()) == two_unresolved, f"cell {config.cell_id} paired two-unresolved mismatch")
    _require(int(paired[:, 1].sum()) == two_hits1, f"cell {config.cell_id} paired two-target1 mismatch")
    _require(int(paired[:, 2].sum()) == two_hits2, f"cell {config.cell_id} paired two-target2 mismatch")
    _require(
        bool(np.all(checkpoints[:, 0] + checkpoints[:, 1] == walkers)),
        f"cell {config.cell_id} one-target checkpoint mass mismatch",
    )
    _require(
        bool(np.all(checkpoints[:, 2] + checkpoints[:, 3] + checkpoints[:, 4] == walkers)),
        f"cell {config.cell_id} two-target checkpoint mass mismatch",
    )
    _require(bool(np.all(checkpoints[:, 5] == walkers)), f"cell {config.cell_id} checkpoint walkers mismatch")
    _require(bool(np.all(checkpoints[:, 2] <= checkpoints[:, 0])), f"cell {config.cell_id} checkpoint subset violation")
    if len(checkpoints) > 1:
        for column in (0, 2, 3):
            _require(bool(np.all(np.diff(checkpoints[:, column]) >= 0)), f"cell {config.cell_id} checkpoint hit count is not monotone")
        for column in (1, 4):
            _require(bool(np.all(np.diff(checkpoints[:, column]) <= 0)), f"cell {config.cell_id} checkpoint unresolved is not monotone")
    for index, step in enumerate(checkpoint_steps.tolist()):
        _require(
            int(one_hist[: step + 1].sum()) == int(checkpoints[index, 0]),
            f"cell {config.cell_id} one histogram/checkpoint mismatch at {step}",
        )
        _require(
            int(two_hist1[: step + 1].sum()) == int(checkpoints[index, 2]),
            f"cell {config.cell_id} two-target1 histogram/checkpoint mismatch at {step}",
        )
        _require(
            int(two_hist2[: step + 1].sum()) == int(checkpoints[index, 3]),
            f"cell {config.cell_id} two-target2 histogram/checkpoint mismatch at {step}",
        )
    final = checkpoints[-1]
    _require(
        final.tolist() == [one_hits, one_unresolved, two_hits1, two_hits2, two_unresolved, walkers],
        f"cell {config.cell_id} final checkpoint mismatch",
    )

    one_payload = _mapping(payload.get("one_target"), f"cell {config.cell_id}.one_target")
    two_payload = _mapping(payload.get("two_targets"), f"cell {config.cell_id}.two_targets")
    _check_summary(one_payload.get("target1"), one_summary, f"cell {config.cell_id}.one_target.target1")
    _check_summary(two_payload.get("target1"), two_summary1, f"cell {config.cell_id}.two_targets.target1")
    _check_summary(two_payload.get("target2"), two_summary2, f"cell {config.cell_id}.two_targets.target2")
    _require(_count(one_payload.get("unresolved"), "one unresolved") == one_unresolved, "one unresolved mismatch")
    _require(_count(two_payload.get("unresolved"), "two unresolved") == two_unresolved, "two unresolved mismatch")
    _close(one_payload.get("unresolved_probability"), one_unresolved / walkers, "one unresolved probability")
    _close(two_payload.get("unresolved_probability"), two_unresolved / walkers, "two unresolved probability")
    _close(one_payload.get("mass_balance"), 1.0, "one mass balance")
    _close(two_payload.get("mass_balance"), 1.0, "two mass balance")

    paired_payload = _mapping(payload.get("paired_outcomes"), f"cell {config.cell_id}.paired_outcomes")
    expected_paired = {
        "one_unresolved__two_unresolved": int(paired[0, 0]),
        "one_unresolved__two_target1": int(paired[0, 1]),
        "one_unresolved__two_target2": int(paired[0, 2]),
        "one_target1__two_unresolved": int(paired[1, 0]),
        "one_target1__two_target1": int(paired[1, 1]),
        "one_target1__two_target2": int(paired[1, 2]),
        "invalid_one_target_state2_total": int(paired[2, :].sum()),
    }
    _check_mapping_exact(paired_payload, expected_paired, f"cell {config.cell_id}.paired_outcomes")
    cumulative_payload = _mapping(payload.get("cumulative_counts"), f"cell {config.cell_id}.cumulative_counts")
    expected_cumulative = {
        str(int(step)): {
            "one_target1": int(row[0]),
            "one_unresolved": int(row[1]),
            "two_target1": int(row[2]),
            "two_target2": int(row[3]),
            "two_unresolved": int(row[4]),
            "walkers": int(row[5]),
        }
        for step, row in zip(checkpoint_steps.tolist(), checkpoints)
    }
    _check_mapping_exact(cumulative_payload, expected_cumulative, f"cell {config.cell_id}.cumulative_counts")
    gating_final = (one_hits - two_hits1) / walkers
    half_index = config.checkpoints.index(config.steps // 2)
    gating_half = (int(checkpoints[half_index, 0]) - int(checkpoints[half_index, 2])) / walkers
    _close(payload.get("gating_probability_drop"), gating_final, "gating_probability_drop")
    expected_ratio = two_hits1 / one_hits if one_hits else None
    if expected_ratio is None:
        _require(payload.get("gating_probability_ratio") is None, "gating ratio must be null")
    else:
        _close(payload.get("gating_probability_ratio"), expected_ratio, "gating_probability_ratio")
    _close(payload.get("target2_first_probability"), two_hits2 / walkers, "target2_first_probability")
    return {
        "gating_probability_drop": gating_final,
        "gating_probability_drop_t_half": gating_half,
        "gating_tail_delta": gating_final - gating_half,
        "one_unresolved_probability": one_unresolved / walkers,
        "two_unresolved_probability": two_unresolved / walkers,
        "diversion_probability": int(paired[1, 2]) / walkers,
        "acceleration_probability": int(paired[0, 2]) / walkers,
        "target2_first_probability": two_hits2 / walkers,
    }


def _validate_one(
    discovered: DiscoveredResult,
    config: CellConfig,
    manifest_path: Path,
    manifest_sha256: str,
    source_path: Path,
    source_sha256: str,
    field_pack_path: Path,
    field_pack_sha256: str,
    contrasts: np.ndarray,
    seeds: np.ndarray,
) -> ValidatedCell:
    payload = discovered.payload
    cell_id = config.cell_id
    manifest_block = _mapping(payload["manifest"], f"cell {cell_id}.manifest")
    expected_manifest = {
        "filename": manifest_path.name,
        "sha256": manifest_sha256,
        "schema": MANIFEST_SCHEMA,
        "cell_id": cell_id,
        "profile": config.profile,
    }
    _check_mapping_exact(manifest_block, expected_manifest, f"cell {cell_id}.manifest")
    provenance = _mapping(payload.get("provenance"), f"cell {cell_id}.provenance")
    _require(provenance.get("source") == source_path.name, f"cell {cell_id} source filename mismatch")
    _require(provenance.get("source_sha256") == source_sha256, f"cell {cell_id} source SHA-256 mismatch")
    expected_parameters = {
        "walkers": config.walkers,
        "steps": config.steps,
        "batch_size": config.batch_size,
        "base_hold": config.base_hold,
        "amplitude": config.amplitude,
        "target_radius": config.target_radius,
        "disorder_replicate": config.disorder_replicate,
        "disorder_seed": int(seeds[config.disorder_replicate]),
        "walk_replicate": config.walk_replicate,
        "checkpoints": list(config.checkpoints),
    }
    _check_mapping_exact(
        _mapping(payload.get("parameters"), f"cell {cell_id}.parameters"),
        expected_parameters,
        f"cell {cell_id}.parameters",
    )
    expected_domain = {
        "source": "field_pack_contrast_shape",
        "width": int(contrasts.shape[2]),
        "height": int(contrasts.shape[1]),
        "boundary": "reflecting_attempted_outside_stays",
        "start": {"x": config.start_x, "y": config.start_y},
        "target1": {"x": config.target1_x, "y": config.target1_y},
        "target2": {"x": config.target2_x, "y": config.target2_y},
        "absorbing_precedence": "target1_then_target2_then_stop",
    }
    _check_mapping_exact(_mapping(payload.get("domain"), f"cell {cell_id}.domain"), expected_domain, f"cell {cell_id}.domain")
    rng = _mapping(payload.get("rng"), f"cell {cell_id}.rng")
    expected_rng = {
        "algorithm": "torch_generator_device_native",
        "walk_seed": config.walk_seed,
        "walk_seed_origin": config.walk_seed_origin,
        "disorder_stride": DISORDER_SEED_STRIDE,
        "walk_stride": WALK_SEED_STRIDE,
        "batch_seed_rule": "walk_seed_plus_batch_start",
        "common_random_numbers": True,
        "deterministic_for_fixed_manifest_runtime_device": True,
    }
    _check_mapping_exact(rng, expected_rng, f"cell {cell_id}.rng")

    contrast = np.ascontiguousarray(contrasts[config.disorder_replicate], dtype="<f8")
    hold = np.asarray(config.base_hold + config.amplitude * contrast, dtype="<f8")
    _require(bool(np.isfinite(hold).all()), f"cell {cell_id} hold field is non-finite")
    _require(float(hold.min()) >= 0.0 and float(hold.max()) < 1.0, f"cell {cell_id} hold field outside [0,1)")
    _require(abs(float(hold.mean(dtype=np.float64)) - config.base_hold) <= FIXED_MEAN_ATOL, f"cell {cell_id} fixed-mean failure")
    field = _mapping(payload.get("field"), f"cell {cell_id}.field")
    _require(field.get("pack_filename") == field_pack_path.name, f"cell {cell_id} field-pack filename mismatch")
    _require(field.get("pack_sha256") == field_pack_sha256, f"cell {cell_id} field-pack SHA mismatch")
    _require(field.get("expected_pack_sha256") == field_pack_sha256, f"cell {cell_id} expected field-pack SHA mismatch")
    _require(
        field.get("contrast_sha256_float64_le") == _sha256_bytes(contrast.tobytes(order="C")),
        f"cell {cell_id} contrast SHA mismatch",
    )
    _require(
        field.get("hold_sha256_float64_le") == _sha256_bytes(hold.tobytes(order="C")),
        f"cell {cell_id} hold SHA mismatch",
    )
    for key, expected in (
        ("minimum", float(hold.min())),
        ("mean", float(hold.mean(dtype=np.float64))),
        ("maximum", float(hold.max())),
        ("standard_deviation", float(hold.std(dtype=np.float64))),
    ):
        _close(field.get(key), expected, f"cell {cell_id}.field.{key}")

    histograms = _mapping(payload.get("histograms"), f"cell {cell_id}.histograms")
    sidecar_sha = _sha256(histograms.get("sha256"), f"cell {cell_id}.histograms.sha256")
    arrays, actual_sidecar_sha = _load_sidecar(discovered.sidecar_path, config, sidecar_sha)
    _require(actual_sidecar_sha == sidecar_sha, f"cell {cell_id} sidecar hash mismatch")
    expected_histograms = {
        "format": "npz_compressed_integer_v3",
        "path": discovered.sidecar_path.name,
        "sha256": sidecar_sha,
        "dtype": "int64",
        "fpt_index_range_inclusive": [0, config.steps],
        "arrays": {
            "one_target1_fpt_histogram": [config.steps + 1],
            "two_target1_fpt_histogram": [config.steps + 1],
            "two_target2_fpt_histogram": [config.steps + 1],
            "checkpoint_steps": [len(config.checkpoints)],
            "checkpoint_counts": [len(config.checkpoints), 6],
            "paired_outcome_counts": [3, 3],
        },
    }
    _check_mapping_exact(histograms, expected_histograms, f"cell {cell_id}.histograms")
    metrics = _validate_arrays_and_payload(payload, arrays, config)
    _check_gate_payload(payload, arrays["paired_outcome_counts"], hold, config)
    slurm = _mapping(provenance.get("slurm"), f"cell {cell_id}.provenance.slurm")
    array_job_id = slurm.get("SLURM_ARRAY_JOB_ID")
    array_task_id = slurm.get("SLURM_ARRAY_TASK_ID")
    job_id = slurm.get("SLURM_JOB_ID")
    for value, label in (
        (array_job_id, "array job id"),
        (array_task_id, "array task id"),
        (job_id, "job id"),
    ):
        if value is not None:
            _require(isinstance(value, str) and value, f"cell {cell_id} {label} is invalid")
    return ValidatedCell(
        config=config,
        json_path=discovered.path,
        json_sha256=_sha256_bytes(discovered.raw),
        npz_path=discovered.sidecar_path,
        npz_sha256=actual_sidecar_sha,
        slurm_array_job_id=array_job_id,
        slurm_array_task_id=array_task_id,
        slurm_job_id=job_id,
        metrics=metrics,
    )


def _mean_ci(values: Sequence[float], label: str) -> dict[str, float | int]:
    _require(len(values) >= 2, f"{label} requires at least two disorder blocks")
    mean = statistics.fmean(values)
    standard_deviation = statistics.stdev(values)
    standard_error = standard_deviation / math.sqrt(len(values))
    try:
        from scipy.stats import t as student_t
    except ImportError as exc:  # pragma: no cover
        _fail(f"SciPy is required for Student-t intervals: {exc}")
    critical = float(student_t.ppf(0.5 + CONFIDENCE_LEVEL / 2.0, len(values) - 1))
    _require(math.isfinite(critical), f"{label} Student-t critical value is non-finite")
    half_width = critical * standard_error
    return {
        "n_disorder_blocks": len(values),
        "mean": mean,
        "standard_deviation": standard_deviation,
        "standard_error": standard_error,
        "t_critical": critical,
        "ci_half_width": half_width,
        "ci_lower": mean - half_width,
        "ci_upper": mean + half_width,
    }


def _condition_id(parameters: Mapping[str, Any]) -> str:
    raw = json.dumps(parameters, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _aggregate(cells: Sequence[ValidatedCell]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[str, list[ValidatedCell]] = {}
    condition_parameters: dict[str, dict[str, Any]] = {}
    for cell in cells:
        parameters = _condition_payload(cell.config)
        canonical = json.dumps(parameters, sort_keys=True, separators=(",", ":"))
        grouped.setdefault(canonical, []).append(cell)
        condition_parameters[canonical] = parameters
    conditions: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    for canonical in sorted(grouped):
        group = grouped[canonical]
        parameters = condition_parameters[canonical]
        condition_id = _condition_id(parameters)
        by_block: dict[int, dict[int, ValidatedCell]] = {}
        for cell in group:
            streams = by_block.setdefault(cell.config.disorder_replicate, {})
            _require(
                cell.config.walk_replicate not in streams,
                f"condition {condition_id} duplicates a disorder/walk stream",
            )
            streams[cell.config.walk_replicate] = cell
        stream_sets = {tuple(sorted(streams)) for streams in by_block.values()}
        _require(len(stream_sets) == 1, f"condition {condition_id} walk inventory differs by disorder block")
        walk_replicates = list(next(iter(stream_sets)))
        block_means: list[dict[str, Any]] = []
        for disorder, streams in sorted(by_block.items()):
            averaged = {
                metric: statistics.fmean(item.metrics[metric] for item in streams.values())
                for metric in next(iter(streams.values())).metrics
            }
            record = {"disorder_replicate": disorder, **averaged}
            block_means.append(record)
            csv_rows.append(
                {
                    "row_type": "block_mean",
                    "condition_id": condition_id,
                    "comparison_id": "",
                    "profile": parameters["profile"],
                    "disorder_replicate": disorder,
                    "walk_replicates": ";".join(map(str, walk_replicates)),
                    "steps": parameters["steps"],
                    "target2_x": parameters["target2_x"],
                    "target2_y": parameters["target2_y"],
                    "amplitude": parameters["amplitude"],
                    **averaged,
                    "primary_paired_effect": "",
                }
            )
        metric_names = sorted(set(block_means[0]) - {"disorder_replicate"})
        metric_statistics = {
            metric: _mean_ci(
                [float(block[metric]) for block in block_means],
                f"condition {condition_id} {metric}",
            )
            for metric in metric_names
        }
        one_upper = float(metric_statistics["one_unresolved_probability"]["ci_upper"])
        two_upper = float(metric_statistics["two_unresolved_probability"]["ci_upper"])
        tail_delta = metric_statistics["gating_tail_delta"]
        stability_upper = abs(float(tail_delta["mean"])) + float(tail_delta["ci_half_width"])
        conditions.append(
            {
                "condition_id": condition_id,
                "parameters": parameters,
                "walk_replicates": walk_replicates,
                "block_means": block_means,
                "statistics": metric_statistics,
                "tail_diagnostics": {
                    "one_unresolved_ci_upper": one_upper,
                    "two_unresolved_ci_upper": two_upper,
                    "gating_stability_abs_ci_upper": stability_upper,
                    "pass": one_upper <= FROZEN_TAIL_UNRESOLVED_LIMIT
                    and two_upper <= FROZEN_TAIL_UNRESOLVED_LIMIT
                    and stability_upper <= FROZEN_TAIL_STABILITY_LIMIT,
                },
            }
        )
    return conditions, csv_rows


def _campaign_contract(manifest: Mapping[str, Any]) -> dict[str, Any]:
    preregistration = _mapping(manifest.get("preregistration"), "preregistration")
    primary = _mapping(preregistration.get("primary_inference"), "primary_inference")
    geometry = _mapping(primary.get("primary_geometry"), "primary_geometry")
    target2 = (
        _integer(geometry.get("target2_x"), "primary target2_x"),
        _integer(geometry.get("target2_y"), "primary target2_y"),
    )
    amplitude = _mapping(
        primary.get("primary_amplitude_contrast"), "primary_amplitude_contrast"
    )
    control = _number(amplitude.get("low"), "primary amplitude low")
    treatment = _number(amplitude.get("high"), "primary amplitude high")
    rope_half_width = _number(
        primary.get("rope_absolute_probability"), "rope_absolute_probability"
    )
    confidence = _number(primary.get("confidence_level"), "primary confidence level")
    _require(target2 == FROZEN_PRIMARY_TARGET2, "manifest primary geometry drifted")
    _require(
        math.isclose(control, FROZEN_PRIMARY_AMPLITUDES[0], rel_tol=0.0, abs_tol=FLOAT_ATOL)
        and math.isclose(
            treatment, FROZEN_PRIMARY_AMPLITUDES[1], rel_tol=0.0, abs_tol=FLOAT_ATOL
        ),
        "manifest primary amplitude contrast drifted",
    )
    _require(
        math.isclose(rope_half_width, FROZEN_PRIMARY_ROPE[1], rel_tol=0.0, abs_tol=FLOAT_ATOL),
        "manifest primary ROPE drifted",
    )
    _require(
        math.isclose(confidence, CONFIDENCE_LEVEL, rel_tol=0.0, abs_tol=FLOAT_ATOL),
        "manifest primary confidence level drifted",
    )

    gates = _mapping(preregistration.get("gates"), "preregistration.gates")
    tail = _mapping(gates.get("tail"), "preregistration.gates.tail")
    tail_confidence = _number(tail.get("confidence_level"), "tail confidence level")
    one_limit = _number(
        tail.get("one_target_unresolved_upper_max"), "one-target unresolved limit"
    )
    two_limit = _number(
        tail.get("two_target_unresolved_upper_max"), "two-target unresolved limit"
    )
    stability_limit = _number(
        tail.get("horizon_drift_abs_plus_tcrit_se_max"), "tail stability limit"
    )
    primary_horizon = _integer(tail.get("primary_horizon"), "primary horizon", minimum=1)
    escalation_horizon = _integer(
        tail.get("escalation_horizon"), "escalation horizon", minimum=primary_horizon
    )
    _require(
        math.isclose(tail_confidence, CONFIDENCE_LEVEL, rel_tol=0.0, abs_tol=FLOAT_ATOL),
        "manifest tail confidence level drifted",
    )
    _require(
        math.isclose(one_limit, FROZEN_TAIL_UNRESOLVED_LIMIT, rel_tol=0.0, abs_tol=FLOAT_ATOL)
        and math.isclose(two_limit, FROZEN_TAIL_UNRESOLVED_LIMIT, rel_tol=0.0, abs_tol=FLOAT_ATOL)
        and math.isclose(
            stability_limit, FROZEN_TAIL_STABILITY_LIMIT, rel_tol=0.0, abs_tol=FLOAT_ATOL
        ),
        "manifest tail thresholds drifted",
    )
    stages = preregistration.get("stages")
    _require(isinstance(stages, list), "preregistration.stages must be an array")
    anchor_stages = [
        _mapping(stage, "stage")
        for stage in stages
        if isinstance(stage, dict) and stage.get("stage_id") == "A"
    ]
    _require(len(anchor_stages) == 1, "preregistration must define exactly one stage A")
    selection = _mapping(anchor_stages[0].get("selection"), "stage A selection")
    raw_targets = selection.get("target2")
    raw_amplitudes = selection.get("amplitudes")
    _require(isinstance(raw_targets, list), "stage A target2 selection must be an array")
    _require(isinstance(raw_amplitudes, list), "stage A amplitudes must be an array")
    anchors = tuple(
        (
            _integer(_mapping(value, "stage A target2").get("x"), "stage A target2.x"),
            _integer(_mapping(value, "stage A target2").get("y"), "stage A target2.y"),
        )
        for value in raw_targets
    )
    amplitudes = tuple(_number(value, "stage A amplitude") for value in raw_amplitudes)
    _require(anchors == FROZEN_TAIL_ANCHORS, "manifest stage-A tail anchors drifted")
    _require(
        len(amplitudes) == len(FROZEN_TAIL_AMPLITUDES)
        and all(
            math.isclose(left, right, rel_tol=0.0, abs_tol=FLOAT_ATOL)
            for left, right in zip(amplitudes, FROZEN_TAIL_AMPLITUDES, strict=True)
        ),
        "manifest stage-A tail amplitudes drifted",
    )
    return {
        "primary_target2": target2,
        "primary_control": control,
        "primary_treatment": treatment,
        "primary_rope": (-rope_half_width, rope_half_width),
        "tail_anchors": anchors,
        "tail_amplitudes": amplitudes,
        "tail_one_limit": one_limit,
        "tail_two_limit": two_limit,
        "tail_stability_limit": stability_limit,
        "primary_horizon": primary_horizon,
        "escalation_horizon": escalation_horizon,
    }


def _select_one(conditions: Sequence[dict[str, Any]], predicate: Any, label: str) -> dict[str, Any]:
    matches = [condition for condition in conditions if predicate(condition["parameters"])]
    _require(len(matches) == 1, f"{label} expected exactly one condition, found {len(matches)}")
    return matches[0]


def _tail_gate(
    conditions: Sequence[dict[str, Any]], contract: Mapping[str, Any]
) -> dict[str, Any]:
    maximum_horizon = max(int(condition["parameters"]["steps"]) for condition in conditions)
    _require(
        maximum_horizon in {contract["primary_horizon"], contract["escalation_horizon"]},
        "result horizon is not preregistered for the tail gate",
    )
    selected: list[dict[str, Any]] = []
    for target2_x, target2_y in contract["tail_anchors"]:
        for amplitude in contract["tail_amplitudes"]:
            selected.append(
                _select_one(
                    conditions,
                    lambda parameters, x=target2_x, y=target2_y, a=amplitude: (
                        parameters["steps"] == maximum_horizon
                        and parameters["target2_x"] == x
                        and parameters["target2_y"] == y
                        and math.isclose(parameters["amplitude"], a, rel_tol=0.0, abs_tol=FLOAT_ATOL)
                    ),
                    f"tail anchor ({target2_x},{target2_y}) amplitude {amplitude}",
                )
            )
    records = [
        {
            "condition_id": condition["condition_id"],
            "target2_x": condition["parameters"]["target2_x"],
            "target2_y": condition["parameters"]["target2_y"],
            "amplitude": condition["parameters"]["amplitude"],
            **condition["tail_diagnostics"],
        }
        for condition in selected
    ]
    return {
        "horizon": maximum_horizon,
        "anchors": records,
        "thresholds": {
            "one_unresolved_ci_upper": contract["tail_one_limit"],
            "two_unresolved_ci_upper": contract["tail_two_limit"],
            "gating_stability_abs_ci_upper": contract["tail_stability_limit"],
        },
        "pass": all(
            record["one_unresolved_ci_upper"] <= contract["tail_one_limit"]
            and record["two_unresolved_ci_upper"] <= contract["tail_two_limit"]
            and record["gating_stability_abs_ci_upper"]
            <= contract["tail_stability_limit"]
            for record in records
        ),
    }


def _primary_decision(
    conditions: Sequence[dict[str, Any]],
    csv_rows: list[dict[str, Any]],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    maximum_horizon = max(int(condition["parameters"]["steps"]) for condition in conditions)
    primary_target2 = tuple(contract["primary_target2"])
    control_amplitude = float(contract["primary_control"])
    treatment_amplitude = float(contract["primary_treatment"])
    rope = tuple(contract["primary_rope"])
    control = _select_one(
        conditions,
        lambda parameters: parameters["steps"] == maximum_horizon
        and (parameters["target2_x"], parameters["target2_y"]) == primary_target2
        and math.isclose(parameters["amplitude"], control_amplitude, rel_tol=0.0, abs_tol=FLOAT_ATOL),
        "primary control",
    )
    treatment = _select_one(
        conditions,
        lambda parameters: parameters["steps"] == maximum_horizon
        and (parameters["target2_x"], parameters["target2_y"]) == primary_target2
        and math.isclose(parameters["amplitude"], treatment_amplitude, rel_tol=0.0, abs_tol=FLOAT_ATOL),
        "primary treatment",
    )
    control_other = dict(control["parameters"])
    treatment_other = dict(treatment["parameters"])
    control_other.pop("amplitude")
    treatment_other.pop("amplitude")
    _require(control_other == treatment_other, "primary control/treatment differ beyond amplitude")
    _require(control["walk_replicates"] == treatment["walk_replicates"], "primary walk streams mismatch")
    control_blocks = {row["disorder_replicate"]: row for row in control["block_means"]}
    treatment_blocks = {row["disorder_replicate"]: row for row in treatment["block_means"]}
    _require(set(control_blocks) == set(treatment_blocks), "primary disorder blocks mismatch")
    comparison_id = hashlib.sha256(
        json.dumps(control_other, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    effects: list[float] = []
    for disorder in sorted(control_blocks):
        effect = float(treatment_blocks[disorder]["gating_probability_drop"]) - float(
            control_blocks[disorder]["gating_probability_drop"]
        )
        effects.append(effect)
        csv_rows.append(
            {
                "row_type": "primary_pair",
                "condition_id": "",
                "comparison_id": comparison_id,
                "profile": control["parameters"]["profile"],
                "disorder_replicate": disorder,
                "walk_replicates": ";".join(map(str, control["walk_replicates"])),
                "steps": maximum_horizon,
                "target2_x": primary_target2[0],
                "target2_y": primary_target2[1],
                "amplitude": f"{control_amplitude}->{treatment_amplitude}",
                "gating_probability_drop": "",
                "gating_probability_drop_t_half": "",
                "gating_tail_delta": "",
                "one_unresolved_probability": "",
                "two_unresolved_probability": "",
                "diversion_probability": "",
                "acceleration_probability": "",
                "target2_first_probability": "",
                "primary_paired_effect": effect,
            }
        )
    stats = _mean_ci(effects, "primary paired contrast")
    lower = float(stats["ci_lower"])
    upper = float(stats["ci_upper"])
    if upper < rope[0]:
        decision = "negative_change"
    elif lower > rope[1]:
        decision = "positive_change"
    elif lower >= rope[0] and upper <= rope[1]:
        decision = "practical_equivalence"
    else:
        decision = "inconclusive"
    return {
        "horizon": maximum_horizon,
        "target2": {"x": primary_target2[0], "y": primary_target2[1]},
        "estimand": "gating_probability_drop(amplitude=0.20)-gating_probability_drop(amplitude=0.00)",
        "control_condition_id": control["condition_id"],
        "treatment_condition_id": treatment["condition_id"],
        "comparison_id": comparison_id,
        "rope": {"lower": rope[0], "upper": rope[1]},
        "statistics": stats,
        "decision": decision,
    }


def _parse_sacct(path: Path) -> list[dict[str, Any]]:
    _require(path.is_file(), f"sacct receipt does not exist: {path}")
    raw = path.read_text(encoding="utf-8")
    _require(raw.strip(), "sacct receipt is empty")
    stripped = raw.lstrip()
    if stripped.startswith("["):
        try:
            records = json.loads(raw, object_pairs_hook=_strict_object)
        except json.JSONDecodeError as exc:
            _fail(f"invalid sacct JSON: {exc}")
        _require(isinstance(records, list), "sacct JSON array invalid")
        return [_mapping(record, "sacct record") for record in records]
    if stripped.startswith("{"):
        payload = _load_json(raw.encode("utf-8"), "sacct receipt")
        records = payload.get("records", payload.get("jobs"))
        _require(isinstance(records, list), "sacct JSON object needs records/jobs")
        return [_mapping(record, "sacct record") for record in records]
    lines = [line for line in raw.splitlines() if line.strip()]
    delimiter = "|" if "|" in lines[0] else ("\t" if "\t" in lines[0] else ",")
    rows = list(csv.reader(lines, delimiter=delimiter))
    rows = [[field.strip() for field in row] for row in rows]
    if rows and rows[0] and rows[0][-1] == "":
        rows = [row[:-1] if row and row[-1] == "" else row for row in rows]
    known = {"JobIDRaw", "JobID", "State", "ExitCode", "ArrayTaskID"}
    if set(rows[0]) & known:
        header = rows.pop(0)
    else:
        _require(len(rows[0]) >= 3, "headerless sacct receipt needs JobIDRaw|State|ExitCode")
        header = ["JobIDRaw", "State", "ExitCode"] + [f"column_{i}" for i in range(3, len(rows[0]))]
    records = []
    for row in rows:
        _require(len(row) <= len(header), "sacct row has more columns than its header")
        records.append(dict(zip(header, row + [""] * (len(header) - len(row)))))
    return records


def _record_value(record: Mapping[str, Any], *names: str) -> Any:
    lowered = {str(key).lower(): value for key, value in record.items()}
    for name in names:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


def _validate_sacct(path: Path | None, cells: Sequence[ValidatedCell]) -> dict[str, Any]:
    if path is None:
        return {"provided": False, "verified": False, "receipt_sha256": None}
    records = _parse_sacct(path)
    _require(bool(cells), "cannot validate sacct without cells")

    allocation_cells: dict[tuple[str, str, int], list[ValidatedCell]] = {}
    for cell in cells:
        array_job_id = cell.slurm_array_job_id
        array_task_id = cell.slurm_array_task_id
        job_id = cell.slurm_job_id
        _require(
            isinstance(array_job_id, str) and array_job_id.isdigit(),
            f"cell {cell.config.cell_id} lacks a decimal SLURM_ARRAY_JOB_ID",
        )
        _require(
            isinstance(array_task_id, str) and array_task_id.isdigit(),
            f"cell {cell.config.cell_id} lacks a decimal SLURM_ARRAY_TASK_ID",
        )
        _require(
            isinstance(job_id, str) and job_id.isdigit(),
            f"cell {cell.config.cell_id} lacks a decimal SLURM_JOB_ID",
        )
        key = (array_job_id, job_id, int(array_task_id))
        allocation_cells.setdefault(key, []).append(cell)

    bundled_production = len(cells) == 5_760
    if bundled_production:
        _require(
            len(allocation_cells) == 480,
            f"bundled production must have 480 allocations, got {len(allocation_cells)}",
        )
        _require(
            len({key[0] for key in allocation_cells}) == 1,
            "bundled production must come from exactly one Slurm array job",
        )
        _require(
            {key[2] for key in allocation_cells} == set(range(480)),
            "bundled production array tasks must be exactly 0..479",
        )
        for key, grouped_cells in allocation_cells.items():
            task_id = key[2]
            actual_ids = {cell.config.cell_id for cell in grouped_cells}
            expected_ids = {task_id + 480 * bundle for bundle in range(12)}
            _require(
                len(grouped_cells) == 12 and actual_ids == expected_ids,
                f"allocation task {task_id} does not map to its exact 12-cell bundle",
            )
    else:
        for key, grouped_cells in allocation_cells.items():
            _require(
                len(grouped_cells) == 1,
                f"non-production allocation {key} unexpectedly owns multiple cells",
            )
            _require(
                grouped_cells[0].config.cell_id == key[2],
                f"cell {grouped_cells[0].config.cell_id} array-task mapping mismatch",
            )

    identifier_to_allocation: dict[str, tuple[str, str, int]] = {}
    for key in allocation_cells:
        array_job_id, job_id, task_id = key
        for identifier in (job_id, f"{array_job_id}_{task_id}"):
            previous = identifier_to_allocation.get(identifier)
            _require(
                previous is None or previous == key,
                f"Slurm identifier {identifier} maps to multiple allocations",
            )
            identifier_to_allocation[identifier] = key

    array_parent_ids = {key[0] for key in allocation_cells}
    matches: dict[tuple[str, str, int], Mapping[str, Any]] = {}
    for record in records:
        raw_ids = {
            str(value)
            for value in (
                _record_value(record, "JobIDRaw", "job_id_raw"),
                _record_value(record, "JobID", "job_id"),
            )
            if value not in (None, "")
        }
        raw_ids = {
            value
            for value in raw_ids
            if "." not in value and (value not in array_parent_ids or "_" in value)
        }
        if not raw_ids:
            continue
        matched_allocations = {
            identifier_to_allocation[identifier]
            for identifier in raw_ids
            if identifier in identifier_to_allocation
        }
        _require(
            len(matched_allocations) <= 1,
            f"sacct row ambiguously matches allocations {sorted(matched_allocations)}",
        )
        if not matched_allocations:
            continue
        allocation = next(iter(matched_allocations))
        _require(
            allocation not in matches,
            f"duplicate sacct row for allocation {allocation}",
        )
        matches[allocation] = record
    _require(
        set(matches) == set(allocation_cells),
        f"sacct allocation coverage mismatch; got {len(matches)} of {len(allocation_cells)}",
    )
    for allocation, record in sorted(matches.items()):
        grouped_cells = allocation_cells[allocation]
        subject = (
            f"cell {grouped_cells[0].config.cell_id}"
            if len(grouped_cells) == 1
            else f"allocation {allocation}"
        )
        state = str(_record_value(record, "State", "state") or "").split("+")[0]
        exit_code = str(_record_value(record, "ExitCode", "exit_code") or "")
        _require(
            state == "COMPLETED",
            f"sacct {subject} is not COMPLETED: {state!r}",
        )
        _require(
            exit_code == "0:0",
            f"sacct {subject} exit code is not 0:0: {exit_code!r}",
        )
    allocation_sizes = {len(group) for group in allocation_cells.values()}
    return {
        "provided": True,
        "verified": True,
        "receipt_filename": path.name,
        "receipt_sha256": _sha256_file(path),
        "allocations_verified": len(matches),
        "cells_verified": len(cells),
        "cells_per_allocation": (
            next(iter(allocation_sizes)) if len(allocation_sizes) == 1 else sorted(allocation_sizes)
        ),
        "bundled_production": bundled_production,
    }


CSV_FIELDS = (
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
INVENTORY_CSV_FIELDS = (
    "cell_id",
    "profile",
    "json_path",
    "json_sha256",
    "npz_path",
    "npz_sha256",
    "slurm_array_job_id",
    "slurm_array_task_id",
    "slurm_job_id",
)


def _csv_bytes(
    rows: Sequence[Mapping[str, Any]], fields: Sequence[str] = CSV_FIELDS
) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fields})
    return buffer.getvalue().encode("utf-8")


def _stage(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _atomic_outputs(json_path: Path, csv_path: Path, payload: Mapping[str, Any], csv_data: bytes) -> None:
    _require(json_path.resolve() != csv_path.resolve(), "JSON and CSV outputs must differ")
    json_data = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    csv_temp: Path | None = None
    json_temp: Path | None = None
    try:
        csv_temp = _stage(csv_path, csv_data)
        json_temp = _stage(json_path, json_data)
        os.replace(csv_temp, csv_path)
        csv_temp = None
        os.replace(json_temp, json_path)
        json_temp = None
        for directory in {csv_path.parent.resolve(), json_path.parent.resolve()}:
            descriptor = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    finally:
        if csv_temp is not None:
            csv_temp.unlink(missing_ok=True)
        if json_temp is not None:
            json_temp.unlink(missing_ok=True)


def reduce_campaign(
    *,
    manifest_path: Path,
    field_pack_path: Path,
    results_dir: Path,
    output_json: Path,
    output_csv: Path,
    source_path: Path | None = None,
    sacct_receipt: Path | None = None,
    mode: str = "full",
) -> dict[str, Any]:
    _require(mode in {"inventory", "full"}, "mode must be inventory or full")
    manifest_path = manifest_path.resolve()
    field_pack_path = field_pack_path.resolve()
    results_dir = results_dir.resolve()
    source_path = (
        source_path.resolve()
        if source_path is not None
        else Path(__file__).with_name("gpu_gating_mc_v3.py").resolve()
    )
    _require(source_path.is_file(), f"executed source does not exist: {source_path}")
    source_sha256 = _sha256_file(source_path)

    # The field hash is top-level manifest content, so read it before loading the pack.
    manifest_preview_raw = manifest_path.read_bytes()
    manifest_preview = _load_json(manifest_preview_raw, "manifest")
    expected_field_sha256 = _sha256(
        manifest_preview.get("field_pack_sha256"), "manifest.field_pack_sha256"
    )
    contrasts, seeds, field_pack_sha256 = _load_field_pack(field_pack_path, expected_field_sha256)
    manifest, manifest_raw, configs = _load_manifest(
        manifest_path, int(contrasts.shape[2]), int(contrasts.shape[1])
    )
    manifest_sha256 = _sha256_bytes(manifest_raw)
    artifacts = _mapping(manifest["artifacts"], "artifacts")
    field_record = _mapping(artifacts.get("field_pack"), "artifacts.field_pack")
    _require(
        field_record.get("filename") == field_pack_path.name,
        "manifest field-pack artifact filename mismatch",
    )
    _require(
        _sha256(field_record.get("sha256"), "artifacts.field_pack.sha256")
        == field_pack_sha256,
        "manifest field-pack artifact SHA mismatch",
    )
    source_record = _mapping(artifacts.get("runner_source"), "artifacts.runner_source")
    _require(
        source_record.get("filename") == source_path.name,
        "manifest runner-source filename mismatch",
    )
    _require(
        _sha256(source_record.get("sha256"), "artifacts.runner_source.sha256")
        == source_sha256,
        "manifest runner-source SHA mismatch",
    )
    for config in configs.values():
        _require(
            config.disorder_replicate < contrasts.shape[0],
            f"cell {config.cell_id} disorder replicate outside field pack",
        )
    discovered = _discover_results(results_dir, manifest_sha256, set(configs))
    validated = [
        _validate_one(
            item,
            configs[item.cell_id],
            manifest_path,
            manifest_sha256,
            source_path,
            source_sha256,
            field_pack_path,
            field_pack_sha256,
            contrasts,
            seeds,
        )
        for item in discovered
    ]
    json_hashes: dict[str, int] = {}
    for cell in validated:
        _require(cell.json_sha256 not in json_hashes, f"byte-duplicate JSON cells {json_hashes.get(cell.json_sha256)} and {cell.config.cell_id}")
        json_hashes[cell.json_sha256] = cell.config.cell_id
    sacct = _validate_sacct(sacct_receipt.resolve() if sacct_receipt else None, validated)
    inventory = [
        {
            "cell_id": cell.config.cell_id,
            "profile": cell.config.profile,
            "json_path": cell.json_path.relative_to(results_dir).as_posix(),
            "json_sha256": cell.json_sha256,
            "npz_path": cell.npz_path.relative_to(results_dir).as_posix(),
            "npz_sha256": cell.npz_sha256,
            "slurm_array_job_id": cell.slurm_array_job_id,
            "slurm_array_task_id": cell.slurm_array_task_id,
            "slurm_job_id": cell.slurm_job_id,
        }
        for cell in validated
    ]
    inventory_digest = _sha256_bytes(
        "".join(
            f"{row['cell_id']}\t{row['json_path']}\t{row['json_sha256']}\t{row['npz_path']}\t{row['npz_sha256']}\n"
            for row in inventory
        ).encode("utf-8")
    )
    payload: dict[str, Any] = {
        "schema": REDUCTION_SCHEMA,
        "mode": mode,
        "audit": {
            "pass": True,
            "fail_closed": True,
            "campaign_kind": _mapping(manifest["campaign"], "campaign")["kind"],
            "manifest_schema": manifest["schema"],
            "manifest_filename": manifest_path.name,
            "manifest_sha256": manifest_sha256,
            "field_pack_filename": field_pack_path.name,
            "field_pack_sha256": field_pack_sha256,
            "source_filename": source_path.name,
            "source_sha256": source_sha256,
            "cell_count": len(validated),
            "inventory_digest": inventory_digest,
            "sacct": sacct,
        },
        "inventory": inventory,
    }
    if mode == "inventory":
        csv_data = _csv_bytes(inventory, INVENTORY_CSV_FIELDS)
        payload["inventory_decision"] = {
            "exact_inventory": True,
            "all_cells_validated": True,
            "sacct_verified_if_provided": not sacct["provided"] or sacct["verified"],
            "pass": not sacct["provided"] or sacct["verified"],
        }
        payload["csv"] = {
            "kind": "inventory",
            "filename": output_csv.name,
            "sha256": _sha256_bytes(csv_data),
            "rows": len(inventory),
        }
    else:
        campaign_kind = _mapping(manifest["campaign"], "campaign")["kind"]
        _require(campaign_kind == "production", "full mode requires a production manifest")
        conditions, csv_rows = _aggregate(validated)
        contract = _campaign_contract(manifest)
        tail = _tail_gate(conditions, contract)
        primary = _primary_decision(conditions, csv_rows, contract)
        csv_rows.sort(
            key=lambda row: (
                str(row["row_type"]),
                str(row["condition_id"]),
                str(row["comparison_id"]),
                int(row["disorder_replicate"]),
            )
        )
        csv_data = _csv_bytes(csv_rows)
        payload.update(
            {
                "method": {
                    "confidence_level": CONFIDENCE_LEVEL,
                    "interval": "two-sided Student-t over disorder-block means",
                    "replication_order": "average walk streams within disorder block, then infer and pair across blocks",
                },
                "conditions": conditions,
                "tail_gate": tail,
                "primary": primary,
                "evidence_decision": {
                    "tail_gate_pass": tail["pass"],
                    "primary_decision": primary["decision"],
                    "sacct_verified_if_provided": not sacct["provided"] or sacct["verified"],
                    "ready": tail["pass"]
                    and primary["decision"] != "inconclusive"
                    and (not sacct["provided"] or sacct["verified"]),
                },
                "csv": {
                    "kind": "block_statistics",
                    "filename": output_csv.name,
                    "sha256": _sha256_bytes(csv_data),
                    "rows": len(csv_rows),
                },
            }
        )
    _atomic_outputs(output_json, output_csv, payload, csv_data)
    return payload


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("inventory", "full"),
        default="full",
        help="inventory validates canary/raw artifacts only; full also performs preregistered inference",
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--field-pack", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--sacct-receipt", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        payload = reduce_campaign(
            manifest_path=args.manifest,
            field_pack_path=args.field_pack,
            results_dir=args.results_dir,
            source_path=args.source,
            sacct_receipt=args.sacct_receipt,
            output_json=args.output_json,
            output_csv=args.output_csv,
            mode=args.mode,
        )
    except AuditError as exc:
        print(f"FAIL-CLOSED: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "mode": payload["mode"],
                "cell_count": payload["audit"]["cell_count"],
                "tail_gate_pass": payload.get("tail_gate", {}).get("pass"),
                "primary_decision": payload.get("primary", {}).get("decision"),
                "output_json": str(args.output_json),
                "output_csv": str(args.output_csv),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
