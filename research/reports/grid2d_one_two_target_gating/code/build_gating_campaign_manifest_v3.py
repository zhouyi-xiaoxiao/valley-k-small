#!/usr/bin/env python3
"""Build frozen canary and production manifests for the v3 gating campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

MANIFEST_SCHEMA = "grid2d-one-two-target-gating-gpu-v3-manifest"
PACK_SCHEMA = "grid2d-one-two-target-gating-disorder-field-pack-v3"
MAX_FIELD_COUNT = 128
TARGET2_X_VALUES = (24, 32, 40)
TARGET2_Y_VALUES = (9, 16, 24, 31, 38)
AMPLITUDES = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25)
WALK_STREAMS = (0, 1)
PRIMARY_TARGET2 = (32, 24)
ANCHOR_TARGET2 = ((24, 24), (32, 24), (40, 24))
ANCHOR_AMPLITUDES = (0.0, 0.20)
PRIMARY_CHECKPOINTS = (5_000, 10_000, 20_000, 40_000, 80_000)
TAIL_CHECKPOINTS = (10_000, 20_000, 40_000, 80_000, 160_000)
WALK_SEED_BASE = 1_729
DISORDER_SEED_STRIDE = 104_729
WALK_STREAM_SEED_STRIDE = 1_009
ROPE_ABSOLUTE_PROBABILITY = 0.002

REPORT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPORT_ROOT / "artifacts" / "data"
DEFAULT_FIELD_PACK = DATA_DIR / "disorder_field_pack_v3.npz"
DEFAULT_FIELD_PACK_MANIFEST = DATA_DIR / "disorder_field_pack_v3.manifest.json"
DEFAULT_CANARY_MANIFEST = DATA_DIR / "gating_v3_canary_manifest.json"
DEFAULT_PRODUCTION_MANIFEST = DATA_DIR / "gating_v3_production_manifest.json"
DEFAULT_TAIL_MANIFEST = DATA_DIR / "gating_v3_tail160k_manifest.json"
DEFAULT_RUNNER_SOURCE = Path(__file__).with_name("gpu_gating_mc_v3.py")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--field-pack", type=Path, default=DEFAULT_FIELD_PACK)
    parser.add_argument(
        "--field-pack-manifest", type=Path, default=DEFAULT_FIELD_PACK_MANIFEST
    )
    parser.add_argument("--runner-source", type=Path, default=DEFAULT_RUNNER_SOURCE)
    parser.add_argument("--container-reference", required=True)
    parser.add_argument("--container-sha256", required=True)
    parser.add_argument("--output-canary", type=Path, default=DEFAULT_CANARY_MANIFEST)
    parser.add_argument(
        "--output-production", type=Path, default=DEFAULT_PRODUCTION_MANIFEST
    )
    parser.add_argument("--output-tail", type=Path, default=DEFAULT_TAIL_MANIFEST)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing manifests only after all inputs validate.",
    )
    return parser.parse_args(argv)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read canonical JSON from {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root in {path} must be an object")
    return payload


def validate_sha256(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be exactly 64 hexadecimal digits")
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    if raw == bytes(32):
        raise ValueError(f"{name} may not be the all-zero placeholder hash")
    return value.lower()


def _validate_reference(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("container_reference must be a nonempty string")
    lowered = value.casefold()
    forbidden = ("placeholder", "changeme", "replace_me", "todo", "tbd", "<", ">")
    if any(token in lowered for token in forbidden):
        raise ValueError("container_reference contains a placeholder token")
    return value


def geometry_index(target2_x: int, target2_y: int) -> int:
    try:
        x_index = TARGET2_X_VALUES.index(target2_x)
        y_index = TARGET2_Y_VALUES.index(target2_y)
    except ValueError as exc:
        raise ValueError("target2 coordinate is outside the frozen geometry grid") from exc
    return x_index * len(TARGET2_Y_VALUES) + y_index


def encode_production_cell_id(
    *,
    geometry_index_value: int,
    amplitude_index: int,
    field_index: int,
    stream_index: int,
    field_count: int,
) -> int:
    if not 0 <= geometry_index_value < len(TARGET2_X_VALUES) * len(TARGET2_Y_VALUES):
        raise ValueError("geometry index is outside the frozen grid")
    if not 0 <= amplitude_index < len(AMPLITUDES):
        raise ValueError("amplitude index is outside the frozen grid")
    if not 0 <= field_index < field_count:
        raise ValueError("field index is outside the field pack")
    if not 0 <= stream_index < len(WALK_STREAMS):
        raise ValueError("stream index is outside the frozen stream set")
    return (
        ((geometry_index_value * len(AMPLITUDES) + amplitude_index) * field_count + field_index)
        * len(WALK_STREAMS)
        + stream_index
    )


def decode_production_cell_id(cell_id: int, *, field_count: int) -> dict[str, int]:
    task_count = (
        len(TARGET2_X_VALUES)
        * len(TARGET2_Y_VALUES)
        * len(AMPLITUDES)
        * field_count
        * len(WALK_STREAMS)
    )
    if not 0 <= cell_id < task_count:
        raise ValueError("production cell_id is outside the campaign")
    quotient, stream_index = divmod(cell_id, len(WALK_STREAMS))
    quotient, field_index = divmod(quotient, field_count)
    geometry_index_value, amplitude_index = divmod(quotient, len(AMPLITUDES))
    x_index, y_index = divmod(geometry_index_value, len(TARGET2_Y_VALUES))
    return {
        "geometry_index": geometry_index_value,
        "x_index": x_index,
        "y_index": y_index,
        "amplitude_index": amplitude_index,
        "field_index": field_index,
        "stream_index": stream_index,
    }


def walk_seed(field_index: int, stream_index: int) -> int:
    return (
        WALK_SEED_BASE
        + field_index * DISORDER_SEED_STRIDE
        + stream_index * WALK_STREAM_SEED_STRIDE
    )


def _load_field_pack(
    field_pack: Path, field_pack_manifest: Path
) -> tuple[np.ndarray, np.ndarray, str, dict[str, Any]]:
    actual_pack_hash = sha256_file(field_pack)
    pack_manifest = load_json(field_pack_manifest)
    if pack_manifest.get("schema") != PACK_SCHEMA:
        raise ValueError(f"field-pack manifest schema must be {PACK_SCHEMA!r}")
    recorded_pack = pack_manifest.get("pack")
    if not isinstance(recorded_pack, dict):
        raise ValueError("field-pack manifest pack must be an object")
    recorded_hash = validate_sha256(recorded_pack.get("sha256"), "pack.sha256")
    if recorded_hash != actual_pack_hash:
        raise ValueError(
            f"field-pack hash mismatch: sidecar={recorded_hash}, actual={actual_pack_hash}"
        )
    try:
        with np.load(field_pack, allow_pickle=False) as pack:
            contrasts = np.asarray(pack["contrasts"], dtype="<f8")
            seeds = np.asarray(pack["seeds"], dtype="<i8")
    except (KeyError, OSError, ValueError) as exc:
        raise ValueError(f"invalid field pack: {exc}") from exc
    if contrasts.ndim != 3:
        raise ValueError("field-pack contrasts must have shape (field, height, width)")
    field_count, height, width = contrasts.shape
    if not 2 <= field_count <= MAX_FIELD_COUNT:
        raise ValueError(f"field pack must contain between 2 and {MAX_FIELD_COUNT} fields")
    if height < 1 or width < 1:
        raise ValueError("field-pack domain must be nonempty")
    if seeds.shape != (field_count,):
        raise ValueError("field-pack seeds must have one entry per field")
    if not np.isfinite(contrasts).all():
        raise ValueError("field pack contains nonfinite contrasts")

    definition = pack_manifest.get("definition")
    if not isinstance(definition, dict) or definition.get("shape") != list(contrasts.shape):
        raise ValueError("field-pack sidecar shape does not match NPZ contrasts")
    records = pack_manifest.get("fields")
    if not isinstance(records, list) or len(records) != field_count:
        raise ValueError("field-pack sidecar must contain one record per field")
    for index in range(field_count):
        contrast = contrasts[index]
        record = records[index]
        if not isinstance(record, dict):
            raise ValueError(f"fields[{index}] must be an object")
        if record.get("index") != index or record.get("seed") != int(seeds[index]):
            raise ValueError(f"fields[{index}] index/seed does not match the NPZ")
        if math.fsum(float(value) for value in contrast.reshape(-1)) != 0.0:
            raise ValueError(f"field {index} does not have exact zero mean under math.fsum")
        if float(np.max(np.abs(contrast))) != 1.0:
            raise ValueError(f"field {index} does not have exact maxabs=1")
        field_hash = sha256_bytes(contrast.tobytes(order="C"))
        if validate_sha256(
            record.get("sha256_float64_le"), f"fields[{index}].sha256_float64_le"
        ) != field_hash:
            raise ValueError(f"fields[{index}] hash does not match the NPZ")
    return contrasts, seeds, actual_pack_hash, pack_manifest


def _production_cells(field_count: int) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for target2_x in TARGET2_X_VALUES:
        for target2_y in TARGET2_Y_VALUES:
            geometry = geometry_index(target2_x, target2_y)
            for amplitude_index, amplitude in enumerate(AMPLITUDES):
                for field_index in range(field_count):
                    for stream_index in WALK_STREAMS:
                        cell_id = encode_production_cell_id(
                            geometry_index_value=geometry,
                            amplitude_index=amplitude_index,
                            field_index=field_index,
                            stream_index=stream_index,
                            field_count=field_count,
                        )
                        cells.append(
                            {
                                "cell_id": cell_id,
                                "disorder_replicate": field_index,
                                "walk_replicate": stream_index,
                                "amplitude": amplitude,
                                "target2_x": target2_x,
                                "target2_y": target2_y,
                            }
                        )
    return cells


def _canary_cells(field_count: int) -> list[dict[str, Any]]:
    if field_count < 2:
        raise ValueError("the frozen eight-cell canary requires at least two fields")
    cells: list[dict[str, Any]] = []
    geometry = geometry_index(*PRIMARY_TARGET2)
    for amplitude_subset_index, amplitude in enumerate(ANCHOR_AMPLITUDES):
        amplitude_index = AMPLITUDES.index(amplitude)
        for field_index in (0, 1):
            for stream_index in WALK_STREAMS:
                local_id = ((amplitude_subset_index * 2 + field_index) * 2) + stream_index
                production_id = encode_production_cell_id(
                    geometry_index_value=geometry,
                    amplitude_index=amplitude_index,
                    field_index=field_index,
                    stream_index=stream_index,
                    field_count=field_count,
                )
                cells.append(
                    {
                        "cell_id": local_id,
                        "disorder_replicate": field_index,
                        "walk_replicate": stream_index,
                        "amplitude": amplitude,
                        "target2_x": PRIMARY_TARGET2[0],
                        "target2_y": PRIMARY_TARGET2[1],
                        "notes": {"production_cell_id": production_id},
                    }
                )
    return cells


def _tail_cells(field_count: int) -> list[dict[str, Any]]:
    """Return the independently indexed conditional 160k anchor campaign."""

    cells: list[dict[str, Any]] = []
    for target2_x, target2_y in ANCHOR_TARGET2:
        geometry = geometry_index(target2_x, target2_y)
        for amplitude in ANCHOR_AMPLITUDES:
            amplitude_index = AMPLITUDES.index(amplitude)
            for field_index in range(field_count):
                for stream_index in WALK_STREAMS:
                    production_id = encode_production_cell_id(
                        geometry_index_value=geometry,
                        amplitude_index=amplitude_index,
                        field_index=field_index,
                        stream_index=stream_index,
                        field_count=field_count,
                    )
                    cells.append(
                        {
                            "cell_id": len(cells),
                            "profile": "tail_160k",
                            "disorder_replicate": field_index,
                            "walk_replicate": stream_index,
                            "amplitude": amplitude,
                            "target2_x": target2_x,
                            "target2_y": target2_y,
                            "notes": {"production_cell_id": production_id},
                        }
                    )
    return cells


def _default_parameters(width: int, height: int) -> dict[str, Any]:
    expected_domain = (64, 48)
    if (width, height) != expected_domain:
        raise ValueError(
            "the frozen v3 geometry requires a 64x48 field pack; "
            f"received width={width}, height={height}"
        )
    return {
        "walkers": 1_000_000,
        "steps": 80_000,
        "batch_size": 131_072,
        "base_hold": 0.30,
        "target_radius": 3,
        "start_x": 7,
        "start_y": 24,
        "target1_x": 54,
        "target1_y": 24,
        "checkpoints": list(PRIMARY_CHECKPOINTS),
        "seed_base": WALK_SEED_BASE,
    }


def _selection(
    *, geometries: Iterable[tuple[int, int]], amplitudes: Iterable[float], fields: Any
) -> dict[str, Any]:
    return {
        "target2": [{"x": x, "y": y} for x, y in geometries],
        "amplitudes": list(amplitudes),
        "field_indices": fields,
        "walk_streams": list(WALK_STREAMS),
    }


def _allocated_seconds(*, walkers: int, steps: int) -> float:
    return 17.628323 + 9.311070539 * (walkers / 500_000) * (steps / 5_000)


def _stage_plan(field_count: int) -> list[dict[str, Any]]:
    all_geometries = tuple(
        (x_value, y_value)
        for x_value in TARGET2_X_VALUES
        for y_value in TARGET2_Y_VALUES
    )
    b1_geometries = tuple(value for value in all_geometries if value not in ANCHOR_TARGET2)
    b2_geometries = tuple(
        (PRIMARY_TARGET2[0], y_value) for y_value in TARGET2_Y_VALUES
    )
    b3_geometries = tuple(value for value in all_geometries if value not in b2_geometries)
    non_anchor_amplitudes = tuple(
        value for value in AMPLITUDES if value not in ANCHOR_AMPLITUDES
    )
    canary_count = 8
    counts = {
        "G0": canary_count,
        "A": len(ANCHOR_TARGET2) * len(ANCHOR_AMPLITUDES) * field_count * 2,
        "A2": len(ANCHOR_TARGET2) * len(ANCHOR_AMPLITUDES) * field_count * 2,
        "B1": len(b1_geometries) * len(ANCHOR_AMPLITUDES) * field_count * 2,
        "B2": len(b2_geometries) * len(non_anchor_amplitudes) * field_count * 2,
        "B3": len(b3_geometries) * len(non_anchor_amplitudes) * field_count * 2,
    }
    default_counts = {"G0": 8, "A": 384, "A2": 384, "B1": 1_536, "B2": 1_280, "B3": 2_560}
    default_caps = {"G0": 2.0, "A": 45.0, "A2": 85.0, "B1": 170.0, "B2": 140.0, "B3": 270.0}
    primary_seconds = _allocated_seconds(walkers=1_000_000, steps=80_000)
    tail_seconds = _allocated_seconds(walkers=1_000_000, steps=160_000)

    specifications = (
        (
            "G0",
            1,
            "canary",
            _selection(
                geometries=(PRIMARY_TARGET2,),
                amplitudes=ANCHOR_AMPLITUDES,
                fields=[0, 1],
            ),
            "default",
            primary_seconds,
            "all integrity gates pass before expanding",
        ),
        (
            "A",
            2,
            "anchor horizon and second-stream block",
            _selection(
                geometries=ANCHOR_TARGET2,
                amplitudes=ANCHOR_AMPLITUDES,
                fields="all",
            ),
            "default",
            primary_seconds,
            "included in post-G0 parallel production; its tail gate decides whether A2 is required",
        ),
        (
            "A2",
            3,
            "conditional 160k tail escalation",
            _selection(
                geometries=ANCHOR_TARGET2,
                amplitudes=ANCHOR_AMPLITUDES,
                fields="all",
            ),
            "tail_160k",
            tail_seconds,
            "run only if the 80k tail gate fails",
        ),
        (
            "B1",
            4,
            "remaining geometries at anchor amplitudes",
            _selection(
                geometries=b1_geometries,
                amplitudes=ANCHOR_AMPLITUDES,
                fields="all",
            ),
            "default",
            primary_seconds,
            "included in post-G0 parallel production; joint integrity is evaluated by the full reducer",
        ),
        (
            "B2",
            5,
            "remaining amplitudes at the central x slice",
            _selection(
                geometries=b2_geometries,
                amplitudes=non_anchor_amplitudes,
                fields="all",
            ),
            "default",
            primary_seconds,
            "included in post-G0 parallel production; joint integrity is evaluated by the full reducer",
        ),
        (
            "B3",
            6,
            "remaining geometry-by-amplitude interactions",
            _selection(
                geometries=b3_geometries,
                amplitudes=non_anchor_amplitudes,
                fields="all",
            ),
            "default",
            primary_seconds,
            "included in post-G0 parallel production; joint integrity is evaluated by the full reducer",
        ),
    )
    stages: list[dict[str, Any]] = []
    for stage_id, priority, role, selection, profile, seconds, advance_gate in specifications:
        task_count = counts[stage_id]
        expected_node_hours = task_count * seconds / 3_600.0
        cap = default_caps[stage_id] * task_count / default_counts[stage_id]
        stages.append(
            {
                "stage_id": stage_id,
                "priority": priority,
                "role": role,
                "selection": selection,
                "profile": profile,
                "task_count": task_count,
                "expected_node_hours": round(expected_node_hours, 3),
                "hard_cap_node_hours": round(cap, 3),
                "advance_gate": advance_gate,
            }
        )
    return stages


def _preregistration(field_count: int) -> dict[str, Any]:
    production_task_count = 15 * 6 * field_count * 2
    scale = field_count / 32.0
    stages = _stage_plan(field_count)
    stage_caps = sum(float(stage["hard_cap_node_hours"]) for stage in stages)
    precision_cap = round(160.0 * scale, 3)
    reserve = round(50.0 * scale, 3)
    unallocated_margin = round(28.0 * scale, 3)
    campaign_cap = round(
        stage_caps + precision_cap + reserve + unallocated_margin, 3
    )
    return {
        "status": "frozen-before-production-execution",
        "boundary_rule": "an attempted step outside the rectangle stays at the current site",
        "domain_source": "contrasts.shape in the SHA-256-pinned field pack",
        "geometry_grid": {
            "target2_x": list(TARGET2_X_VALUES),
            "target2_y": list(TARGET2_Y_VALUES),
            "geometry_count": 15,
        },
        "amplitudes": list(AMPLITUDES),
        "field_count": field_count,
        "walk_streams": list(WALK_STREAMS),
        "production_task_count": production_task_count,
        "task_mapping": {
            "geometry_index": "x_index * 5 + y_index",
            "production_cell_id": "((((geometry_index * 6) + amplitude_index) * field_count + field_index) * 2 + stream_index)",
            "loop_order": [
                "target2_x",
                "target2_y",
                "amplitude",
                "disorder_replicate",
                "walk_replicate",
            ],
        },
        "randomness": {
            "walk_seed_formula": "1729 + disorder_replicate * 104729 + walk_replicate * 1009",
            "common_random_numbers": "same disorder and walk stream across every amplitude, geometry, and target condition",
            "independent_inference_unit": "disorder field block",
            "stream_aggregation": "average the two walk streams within each field before inference",
            "effective_field_blocks": field_count,
            "forbidden_pseudoreplication": "do not treat two streams as twice as many independent fields",
        },
        "primary_inference": {
            "estimand": "paired gating probability drop p(one-target hits target1) - p(two-target hits target1)",
            "primary_geometry": {"target2_x": 32, "target2_y": 24},
            "primary_amplitude_contrast": {"high": 0.20, "low": 0.0, "contrast": "high - low"},
            "confidence_level": 0.95,
            "rope_absolute_probability": ROPE_ABSOLUTE_PROBABILITY,
            "decision_rules": {
                "negative": "CI_high < -0.002",
                "positive": "CI_low > 0.002",
                "equivalent": "CI_low >= -0.002 and CI_high <= 0.002",
                "inconclusive": "otherwise",
            },
        },
        "gates": {
            "integrity": {
                "missing_tasks": 0,
                "duplicate_tasks": 0,
                "hash_mismatches": 0,
                "nonfinite_values": 0,
                "holding_probability_interval": "[0,1)",
                "fixed_mean_absolute_error_max": 1.0e-12,
                "mass_balance_absolute_error_max": 1.0e-12,
                "paired_subset_violations": 0,
                "checkpoint_counts_must_be_monotone": True,
                "task_mapping_mismatches": 0,
                "runtime_parameter_mismatches": 0,
            },
            "tail": {
                "confidence_level": 0.95,
                "one_target_unresolved_upper_max": 0.005,
                "two_target_unresolved_upper_max": 0.005,
                "horizon_drift_abs_plus_tcrit_se_max": 0.002,
                "primary_horizon": 80_000,
                "escalation_horizon": 160_000,
                "on_primary_failure": "run stage A2 with profile tail_160k",
                "on_escalation_failure": "make finite-horizon and tail-bound claims only; no asymptotic claim",
            },
        },
        "stages": stages,
        "budget": {
            "units": "node-hours",
            "calibration": {
                "observed_node_seconds": 889.0,
                "observed_tasks": 33,
                "observed_gpu_runtime_mean_seconds": 9.311070539,
                "allocated_seconds_formula": "17.628323 + 9.311070539 * (walkers / 500000) * (steps / 5000)",
            },
            "optional_precision_expected_range": [
                round(34.0 * scale, 3),
                round(129.0 * scale, 3),
            ],
            "optional_precision_hard_cap": precision_cap,
            "reserve": reserve,
            "stage_hard_cap_total": round(stage_caps, 3),
            "campaign_hard_cap": campaign_cap,
            "unallocated_margin": unallocated_margin,
        },
    }


def _base_manifest(
    *,
    campaign_kind: str,
    contrasts: np.ndarray,
    pack_hash: str,
    pack_path: Path,
    pack_manifest_path: Path,
    runner_source: Path,
    container_reference: str,
    container_sha256: str,
    created_utc: str,
) -> dict[str, Any]:
    field_count, height, width = contrasts.shape
    source = Path(__file__).resolve()
    validator_source = source.with_name("validate_gating_campaign_manifest_v3.py")
    if not validator_source.is_file():
        raise FileNotFoundError(f"validator source does not exist: {validator_source}")
    return {
        "schema": MANIFEST_SCHEMA,
        "campaign": {
            "kind": campaign_kind,
            "created_utc": created_utc,
            "domain": {"width": width, "height": height},
        },
        "defaults": _default_parameters(width, height),
        "profiles": {
            "tail_160k": {
                "steps": 160_000,
                "checkpoints": list(TAIL_CHECKPOINTS),
            }
        },
        "field_pack_sha256": pack_hash,
        "artifacts": {
            "field_pack": {
                "filename": pack_path.name,
                "sha256": pack_hash,
                "sidecar_filename": pack_manifest_path.name,
                "sidecar_sha256": sha256_file(pack_manifest_path),
            },
            "runner_source": {
                "filename": runner_source.name,
                "sha256": sha256_file(runner_source),
            },
            "container": {
                "reference": container_reference,
                "sha256": container_sha256,
            },
            "manifest_builder": {
                "filename": source.name,
                "sha256": sha256_file(source),
            },
            "manifest_validator": {
                "filename": validator_source.name,
                "sha256": sha256_file(validator_source),
            },
        },
        "preregistration": _preregistration(field_count),
        "cells": [],
    }


def _atomic_json_write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def build_manifests(
    *,
    field_pack: Path,
    field_pack_manifest: Path,
    runner_source: Path,
    container_reference: str,
    container_sha256: str,
    output_canary: Path,
    output_production: Path,
    output_tail: Path,
    overwrite: bool = False,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Build all frozen manifests after validating every hashed input."""

    container_reference = _validate_reference(container_reference)
    container_sha256 = validate_sha256(container_sha256, "container_sha256")
    if not runner_source.is_file():
        raise FileNotFoundError(f"runner source does not exist: {runner_source}")
    resolved_outputs = {
        output_canary.resolve(),
        output_production.resolve(),
        output_tail.resolve(),
    }
    if len(resolved_outputs) != 3:
        raise ValueError("canary, production, and tail output paths must differ")
    existing = [
        path for path in (output_canary, output_production, output_tail) if path.exists()
    ]
    if existing and not overwrite:
        raise FileExistsError(
            "refusing to replace existing manifest(s): "
            + ", ".join(str(path) for path in existing)
        )
    contrasts, _seeds, pack_hash, _pack_manifest = _load_field_pack(
        field_pack, field_pack_manifest
    )
    created_utc = datetime.now(UTC).isoformat()
    common = {
        "contrasts": contrasts,
        "pack_hash": pack_hash,
        "pack_path": field_pack,
        "pack_manifest_path": field_pack_manifest,
        "runner_source": runner_source,
        "container_reference": container_reference,
        "container_sha256": container_sha256,
        "created_utc": created_utc,
    }
    canary = _base_manifest(campaign_kind="canary", **common)
    production = _base_manifest(campaign_kind="production", **common)
    tail = _base_manifest(campaign_kind="tail160k", **common)
    field_count = int(contrasts.shape[0])
    canary["cells"] = _canary_cells(field_count)
    production["cells"] = _production_cells(field_count)
    tail["cells"] = _tail_cells(field_count)
    canary["campaign"]["cell_count"] = len(canary["cells"])
    production["campaign"]["cell_count"] = len(production["cells"])
    tail["campaign"]["cell_count"] = len(tail["cells"])
    tail["campaign"]["activation_gate"] = (
        "submit only when the verified 80k reducer tail gate is FAIL"
    )

    _atomic_json_write(output_canary, canary)
    _atomic_json_write(output_production, production)
    _atomic_json_write(output_tail, tail)

    # Full post-write validation is deliberately late-bound to avoid an import
    # cycle while keeping the validator usable as a standalone CLI.
    from validate_gating_campaign_manifest_v3 import validate_manifest_file

    validate_manifest_file(
        output_canary,
        field_pack=field_pack,
        field_pack_manifest=field_pack_manifest,
        runner_source=runner_source,
    )
    validate_manifest_file(
        output_production,
        field_pack=field_pack,
        field_pack_manifest=field_pack_manifest,
        runner_source=runner_source,
    )
    validate_manifest_file(
        output_tail,
        field_pack=field_pack,
        field_pack_manifest=field_pack_manifest,
        runner_source=runner_source,
    )
    return canary, production, tail


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    canary, production, tail = build_manifests(
        field_pack=args.field_pack,
        field_pack_manifest=args.field_pack_manifest,
        runner_source=args.runner_source,
        container_reference=args.container_reference,
        container_sha256=args.container_sha256,
        output_canary=args.output_canary,
        output_production=args.output_production,
        output_tail=args.output_tail,
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "schema": MANIFEST_SCHEMA,
                "field_pack_sha256": production["field_pack_sha256"],
                "canary": {
                    "path": str(args.output_canary),
                    "cells": len(canary["cells"]),
                    "sha256": sha256_file(args.output_canary),
                },
                "production": {
                    "path": str(args.output_production),
                    "cells": len(production["cells"]),
                    "sha256": sha256_file(args.output_production),
                },
                "tail160k": {
                    "path": str(args.output_tail),
                    "cells": len(tail["cells"]),
                    "sha256": sha256_file(args.output_tail),
                    "activation": "only after verified 80k tail-gate failure",
                },
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
