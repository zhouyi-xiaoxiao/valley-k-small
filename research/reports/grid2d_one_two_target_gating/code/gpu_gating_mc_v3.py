#!/usr/bin/env python3
"""Run one frozen-manifest fixed-mean gating cell on CPU or CUDA.

Version 3 keeps the paired common-random-number construction of the executed
v2 source, but moves every scientific parameter into a content-hashed
manifest.  The command line selects only the manifest cell, execution device,
and fresh output paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import torch

MANIFEST_SCHEMA = "grid2d-one-two-target-gating-gpu-v3-manifest"
RESULT_SCHEMA = "grid2d-one-two-target-gating-fixed-mean-gpu-v3"
SIDECAR_SCHEMA_VERSION = 3
FIXED_MEAN_ATOL = 1.0e-12
DISORDER_SEED_STRIDE = 104_729
WALK_SEED_STRIDE = 1_009
MAX_TORCH_SEED = (1 << 63) - 1


@dataclass(frozen=True)
class CellConfig:
    """Fully resolved scientific configuration for one manifest cell."""

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
class SimulationArrays:
    """Integer sufficient statistics emitted by the paired simulation."""

    one_target1_fpt: np.ndarray
    two_target1_fpt: np.ndarray
    two_target2_fpt: np.ndarray
    checkpoint_steps: np.ndarray
    checkpoint_counts: np.ndarray
    paired_outcomes: np.ndarray


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--field-pack", type=Path, required=True)
    parser.add_argument("--cell-id", type=int, required=True)
    parser.add_argument("--device", choices=("cuda", "cpu"), required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-npz", type=Path, required=True)
    return parser.parse_args(argv)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key in manifest: {key!r}")
        result[key] = value
    return result


def load_manifest(path: Path) -> tuple[dict[str, Any], bytes, str]:
    raw = path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"manifest is not canonical UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("manifest root must be a JSON object")
    if payload.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(
            f"manifest schema must be {MANIFEST_SCHEMA!r}, got {payload.get('schema')!r}"
        )
    return payload, raw, _sha256_bytes(raw)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _integer(value: Any, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return value


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _coordinate_pair(
    parameters: Mapping[str, Any],
    prefix: str,
    *,
    required: bool = True,
) -> tuple[int, int] | None:
    direct_x = f"{prefix}_x"
    direct_y = f"{prefix}_y"
    nested = parameters.get(prefix)
    if nested is not None:
        nested_mapping = _mapping(nested, prefix)
        if direct_x in parameters or direct_y in parameters:
            raise ValueError(f"{prefix} must use either nested or x/y fields, not both")
        if "x" not in nested_mapping or "y" not in nested_mapping:
            raise ValueError(f"{prefix} requires x and y")
        return (
            _integer(nested_mapping["x"], f"{prefix}.x"),
            _integer(nested_mapping["y"], f"{prefix}.y"),
        )
    if direct_x in parameters or direct_y in parameters:
        if direct_x not in parameters or direct_y not in parameters:
            raise ValueError(f"{prefix}_x and {prefix}_y must appear together")
        return (
            _integer(parameters[direct_x], direct_x),
            _integer(parameters[direct_y], direct_y),
        )
    if required:
        raise ValueError(f"missing {prefix} coordinates")
    return None


def _merge_cell_parameters(
    manifest: Mapping[str, Any], cell_id: int
) -> tuple[dict[str, Any], Mapping[str, Any], str | None]:
    defaults = dict(_mapping(manifest.get("defaults"), "defaults"))
    cells = manifest.get("cells")
    if not isinstance(cells, list):
        raise ValueError("cells must be an array")
    matched: list[Mapping[str, Any]] = []
    for index, raw_cell in enumerate(cells):
        cell = _mapping(raw_cell, f"cells[{index}]")
        raw_id = cell.get("cell_id")
        if isinstance(raw_id, bool) or not isinstance(raw_id, int):
            raise ValueError(f"cells[{index}].cell_id must be an integer")
        if raw_id == cell_id:
            matched.append(cell)
    if len(matched) != 1:
        raise ValueError(f"cell_id {cell_id} occurs {len(matched)} times in manifest")
    cell = matched[0]

    profile_value = cell.get("profile", manifest.get("default_profile"))
    profile: str | None
    if profile_value is None:
        profile = None
    elif isinstance(profile_value, str) and profile_value:
        profile = profile_value
    else:
        raise ValueError("profile must be a nonempty string when present")

    parameters = defaults
    if profile is not None:
        profiles = _mapping(manifest.get("profiles"), "profiles")
        if profile not in profiles:
            raise ValueError(f"unknown manifest profile: {profile!r}")
        parameters.update(_mapping(profiles[profile], f"profiles.{profile}"))

    nested_parameters = cell.get("parameters")
    if nested_parameters is not None:
        parameters.update(_mapping(nested_parameters, f"cell {cell_id} parameters"))

    reserved = {"cell_id", "profile", "parameters", "label", "notes"}
    for key, value in cell.items():
        if key not in reserved:
            if nested_parameters is not None and key in nested_parameters:
                raise ValueError(f"cell field {key!r} is duplicated inside parameters")
            parameters[key] = value
    return parameters, cell, profile


def resolve_cell_config(
    manifest: Mapping[str, Any], cell_id: int, *, width: int, height: int
) -> CellConfig:
    parameters, _cell, profile = _merge_cell_parameters(manifest, cell_id)
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
    missing = [name for name in required if name not in parameters]
    if missing:
        raise ValueError(f"cell {cell_id} is missing parameters: {', '.join(missing)}")

    walkers = _integer(parameters["walkers"], "walkers", minimum=1)
    steps = _integer(parameters["steps"], "steps", minimum=1)
    batch_size = _integer(parameters["batch_size"], "batch_size", minimum=1)
    base_hold = _number(parameters["base_hold"], "base_hold")
    amplitude = _number(parameters["amplitude"], "amplitude")
    target_radius = _integer(parameters["target_radius"], "target_radius", minimum=0)
    disorder_replicate = _integer(
        parameters["disorder_replicate"], "disorder_replicate", minimum=0
    )
    walk_replicate = _integer(
        parameters["walk_replicate"], "walk_replicate", minimum=0
    )

    start = _coordinate_pair(parameters, "start")
    target1 = _coordinate_pair(parameters, "target1")
    target2 = _coordinate_pair(parameters, "target2")
    assert start is not None and target1 is not None and target2 is not None

    raw_checkpoints = parameters["checkpoints"]
    if not isinstance(raw_checkpoints, list) or not raw_checkpoints:
        raise ValueError("checkpoints must be a nonempty array")
    checkpoints = tuple(
        _integer(value, f"checkpoints[{index}]", minimum=0)
        for index, value in enumerate(raw_checkpoints)
    )
    if tuple(sorted(set(checkpoints))) != checkpoints:
        raise ValueError("checkpoints must be strictly increasing and unique")
    if checkpoints[-1] != steps:
        raise ValueError("the final checkpoint must equal steps")
    if checkpoints[-1] > steps:
        raise ValueError("checkpoint exceeds steps")

    for name, (x_value, y_value) in (
        ("start", start),
        ("target1", target1),
        ("target2", target2),
    ):
        if not (0 <= x_value < width and 0 <= y_value < height):
            raise ValueError(
                f"{name}=({x_value},{y_value}) is outside field-pack domain "
                f"width={width}, height={height}"
            )

    explicit_seed = parameters.get("walk_seed")
    if explicit_seed is not None:
        walk_seed = _integer(explicit_seed, "walk_seed", minimum=0)
        walk_seed_origin = "manifest_explicit"
    else:
        seed_base = _integer(parameters.get("seed_base"), "seed_base", minimum=0)
        walk_seed = (
            seed_base
            + disorder_replicate * DISORDER_SEED_STRIDE
            + walk_replicate * WALK_SEED_STRIDE
        )
        walk_seed_origin = "v2_common_random_number_formula"
    if walk_seed + walkers > MAX_TORCH_SEED:
        raise ValueError("walk seed plus batch offsets exceeds signed 63-bit range")

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


def expected_field_pack_sha256(manifest: Mapping[str, Any]) -> str:
    value = manifest.get("field_pack_sha256")
    if value is None and "field_pack" in manifest:
        value = _mapping(manifest["field_pack"], "field_pack").get("sha256")
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("manifest must pin field_pack_sha256 as 64 hexadecimal digits")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError("field_pack_sha256 is not hexadecimal") from exc
    return value.lower()


def load_field_pack(
    path: Path, expected_sha256: str
) -> tuple[np.ndarray, np.ndarray, str]:
    actual_sha256 = _sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"field-pack SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )
    try:
        with np.load(path, allow_pickle=False) as pack:
            contrasts = np.asarray(pack["contrasts"], dtype=np.float64)
            seeds = np.asarray(pack["seeds"], dtype=np.int64)
    except (KeyError, OSError, ValueError) as exc:
        raise ValueError(f"invalid field pack: {exc}") from exc
    if contrasts.ndim != 3 or contrasts.shape[0] < 1:
        raise ValueError("field-pack contrasts must have shape (replicate, height, width)")
    if contrasts.shape[1] < 1 or contrasts.shape[2] < 1:
        raise ValueError("field-pack domain must be nonempty")
    if seeds.shape != (contrasts.shape[0],):
        raise ValueError("field-pack seeds must have one entry per contrast field")
    if not np.isfinite(contrasts).all():
        raise ValueError("field-pack contrasts contain nonfinite values")
    return contrasts, seeds, actual_sha256


def construct_hold_field(contrast: np.ndarray, config: CellConfig) -> np.ndarray:
    hold = np.asarray(config.base_hold + config.amplitude * contrast, dtype="<f8")
    if not np.isfinite(hold).all():
        raise ValueError("holding probabilities contain nonfinite values")
    minimum = float(hold.min())
    maximum = float(hold.max())
    mean = float(hold.mean(dtype=np.float64))
    if minimum < 0.0 or maximum >= 1.0:
        raise ValueError(
            f"holding probabilities are outside [0,1): min={minimum}, max={maximum}"
        )
    if abs(mean - config.base_hold) > FIXED_MEAN_ATOL:
        raise ValueError(
            "fixed-mean hold invariant failed: "
            f"mean={mean:.17g}, base_hold={config.base_hold:.17g}, "
            f"tolerance={FIXED_MEAN_ATOL:.1e}"
        )
    return np.ascontiguousarray(hold)


def reflecting_trial_positions(
    x: torch.Tensor,
    y: torch.Tensor,
    direction: torch.Tensor,
    *,
    width: int,
    height: int,
    directions_x: torch.Tensor | None = None,
    directions_y: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Attempt a cardinal move; an out-of-domain attempt stays in place."""

    if directions_x is None or directions_y is None:
        directions_x = torch.tensor((1, -1, 0, 0), dtype=torch.long, device=x.device)
        directions_y = torch.tensor((0, 0, 1, -1), dtype=torch.long, device=x.device)
    trial_x = (x + directions_x[direction]).clamp(0, width - 1)
    trial_y = (y + directions_y[direction]).clamp(0, height - 1)
    return trial_x, trial_y


def _inside_target(
    x: torch.Tensor,
    y: torch.Tensor,
    target_x: int,
    target_y: int,
    radius_squared: int,
) -> torch.Tensor:
    return (x - target_x).square() + (y - target_y).square() <= radius_squared


def _scalar_inside_target(
    x: int, y: int, target_x: int, target_y: int, radius_squared: int
) -> bool:
    return (x - target_x) ** 2 + (y - target_y) ** 2 <= radius_squared


@torch.inference_mode()
def simulate_pair(
    config: CellConfig,
    device: torch.device,
    hold: torch.Tensor,
) -> SimulationArrays:
    height, width = int(hold.shape[0]), int(hold.shape[1])
    radius_squared = config.target_radius * config.target_radius
    one_hist1 = torch.zeros(config.steps + 1, dtype=torch.int64)
    two_hist1 = torch.zeros(config.steps + 1, dtype=torch.int64)
    two_hist2 = torch.zeros(config.steps + 1, dtype=torch.int64)
    pair_counts = torch.zeros(9, dtype=torch.int64)
    checkpoint_steps = np.asarray(config.checkpoints, dtype=np.int64)
    checkpoint_index = {step: index for index, step in enumerate(config.checkpoints)}
    checkpoint_counts = np.zeros((len(config.checkpoints), 6), dtype=np.int64)
    directions_x = torch.tensor((1, -1, 0, 0), dtype=torch.long, device=device)
    directions_y = torch.tensor((0, 0, 1, -1), dtype=torch.long, device=device)

    start_at_target1 = _scalar_inside_target(
        config.start_x,
        config.start_y,
        config.target1_x,
        config.target1_y,
        radius_squared,
    )
    start_at_target2 = _scalar_inside_target(
        config.start_x,
        config.start_y,
        config.target2_x,
        config.target2_y,
        radius_squared,
    )

    for batch_start in range(0, config.walkers, config.batch_size):
        count = min(config.batch_size, config.walkers - batch_start)
        generator = torch.Generator(device=device).manual_seed(config.walk_seed + batch_start)
        x_one = torch.full((count,), config.start_x, dtype=torch.long, device=device)
        y_one = torch.full((count,), config.start_y, dtype=torch.long, device=device)
        x_two = x_one.clone()
        y_two = y_one.clone()
        hit_one = torch.zeros(count, dtype=torch.int8, device=device)
        hit_two = torch.zeros(count, dtype=torch.int8, device=device)
        fpt_one = torch.zeros(count, dtype=torch.int32, device=device)
        fpt_two = torch.zeros(count, dtype=torch.int32, device=device)

        if start_at_target1:
            hit_one.fill_(1)
            hit_two.fill_(1)
        elif start_at_target2:
            # Target 1 is tested first.  Target 2 absorbs only walkers that are
            # still active, including at time zero.
            hit_two.fill_(2)

        def accumulate_checkpoint(step: int) -> None:
            index = checkpoint_index.get(step)
            if index is None:
                return
            checkpoint_counts[index] += np.asarray(
                (
                    int((hit_one == 1).sum().item()),
                    int((hit_one == 0).sum().item()),
                    int((hit_two == 1).sum().item()),
                    int((hit_two == 2).sum().item()),
                    int((hit_two == 0).sum().item()),
                    count,
                ),
                dtype=np.int64,
            )

        accumulate_checkpoint(0)
        for step in range(1, config.steps + 1):
            random_move = torch.rand(count, generator=generator, device=device)
            direction = torch.randint(0, 4, (count,), generator=generator, device=device)

            active_one = hit_one == 0
            moving_one = active_one & (random_move >= hold[y_one, x_one])
            trial_x, trial_y = reflecting_trial_positions(
                x_one,
                y_one,
                direction,
                width=width,
                height=height,
                directions_x=directions_x,
                directions_y=directions_y,
            )
            x_one = torch.where(moving_one, trial_x, x_one)
            y_one = torch.where(moving_one, trial_y, y_one)
            at1_one = active_one & _inside_target(
                x_one,
                y_one,
                config.target1_x,
                config.target1_y,
                radius_squared,
            )
            hit_one[at1_one] = 1
            fpt_one[at1_one] = step

            active_two = hit_two == 0
            moving_two = active_two & (random_move >= hold[y_two, x_two])
            trial_x, trial_y = reflecting_trial_positions(
                x_two,
                y_two,
                direction,
                width=width,
                height=height,
                directions_x=directions_x,
                directions_y=directions_y,
            )
            x_two = torch.where(moving_two, trial_x, x_two)
            y_two = torch.where(moving_two, trial_y, y_two)
            at1_two = active_two & _inside_target(
                x_two,
                y_two,
                config.target1_x,
                config.target1_y,
                radius_squared,
            )
            hit_two[at1_two] = 1
            fpt_two[at1_two] = step
            still_active = hit_two == 0
            at2_two = still_active & _inside_target(
                x_two,
                y_two,
                config.target2_x,
                config.target2_y,
                radius_squared,
            )
            hit_two[at2_two] = 2
            fpt_two[at2_two] = step
            accumulate_checkpoint(step)

        one_hist1 += torch.bincount(
            fpt_one[hit_one == 1].long(), minlength=config.steps + 1
        )[: config.steps + 1].cpu()
        two_hist1 += torch.bincount(
            fpt_two[hit_two == 1].long(), minlength=config.steps + 1
        )[: config.steps + 1].cpu()
        two_hist2 += torch.bincount(
            fpt_two[hit_two == 2].long(), minlength=config.steps + 1
        )[: config.steps + 1].cpu()
        pair_codes = hit_one.long().cpu() * 3 + hit_two.long().cpu()
        pair_counts += torch.bincount(pair_codes, minlength=9)[:9]

    return SimulationArrays(
        one_target1_fpt=np.asarray(one_hist1.numpy(), dtype=np.int64),
        two_target1_fpt=np.asarray(two_hist1.numpy(), dtype=np.int64),
        two_target2_fpt=np.asarray(two_hist2.numpy(), dtype=np.int64),
        checkpoint_steps=checkpoint_steps,
        checkpoint_counts=checkpoint_counts,
        paired_outcomes=np.asarray(pair_counts.numpy(), dtype=np.int64).reshape(3, 3),
    )


def summarize_histogram(histogram: np.ndarray, walkers: int) -> dict[str, Any]:
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
    times = np.arange(histogram.size, dtype=np.float64)
    cumulative = np.cumsum(histogram, dtype=np.int64)

    def quantile(value: float) -> int:
        rank = math.ceil(value * hits)
        return int(np.searchsorted(cumulative, rank, side="left"))

    return {
        "hits": hits,
        "probability": probability,
        "standard_error": math.sqrt(probability * (1.0 - probability) / walkers),
        "mean_fpt": float(np.dot(times, histogram.astype(np.float64)) / hits),
        "median_fpt": quantile(0.5),
        "q90_fpt": quantile(0.9),
    }


def evaluate_gates(
    config: CellConfig,
    hold: np.ndarray,
    arrays: SimulationArrays,
) -> dict[str, Any]:
    one_hist = arrays.one_target1_fpt
    two_hist1 = arrays.two_target1_fpt
    two_hist2 = arrays.two_target2_fpt
    checkpoints = arrays.checkpoint_counts
    paired = arrays.paired_outcomes
    one_hits = int(one_hist.sum(dtype=np.int64))
    two_hits1 = int(two_hist1.sum(dtype=np.int64))
    two_hits2 = int(two_hist2.sum(dtype=np.int64))
    one_unresolved = config.walkers - one_hits
    two_unresolved = config.walkers - two_hits1 - two_hits2

    checkpoint_mass = bool(
        np.all(checkpoints[:, 0] + checkpoints[:, 1] == config.walkers)
        and np.all(
            checkpoints[:, 2] + checkpoints[:, 3] + checkpoints[:, 4]
            == config.walkers
        )
        and np.all(checkpoints[:, 5] == config.walkers)
    )
    final_mass = bool(
        one_hits + one_unresolved == config.walkers
        and two_hits1 + two_hits2 + two_unresolved == config.walkers
        and int(paired.sum(dtype=np.int64)) == config.walkers
    )

    subset_invalid = int(paired[0, 1])
    subset_passed = bool(
        subset_invalid == 0
        and np.all(two_hist1 <= one_hist)
        and two_hits1 <= one_hits
    )

    monotone_passed = True
    if checkpoints.shape[0] > 1:
        monotone_passed = bool(
            np.all(np.diff(checkpoints[:, 0]) >= 0)
            and np.all(np.diff(checkpoints[:, 1]) <= 0)
            and np.all(np.diff(checkpoints[:, 2]) >= 0)
            and np.all(np.diff(checkpoints[:, 3]) >= 0)
            and np.all(np.diff(checkpoints[:, 4]) <= 0)
        )

    prefix_passed = True
    for index, step in enumerate(arrays.checkpoint_steps.tolist()):
        prefix_passed = prefix_passed and (
            int(one_hist[: step + 1].sum(dtype=np.int64)) == int(checkpoints[index, 0])
            and int(two_hist1[: step + 1].sum(dtype=np.int64))
            == int(checkpoints[index, 2])
            and int(two_hist2[: step + 1].sum(dtype=np.int64))
            == int(checkpoints[index, 3])
        )

    arrays_to_check = (
        one_hist,
        two_hist1,
        two_hist2,
        arrays.checkpoint_steps,
        checkpoints,
        paired,
    )
    integer_arrays = all(array.dtype == np.int64 for array in arrays_to_check)
    nonnegative_arrays = all(bool(np.all(array >= 0)) for array in arrays_to_check)
    bounded_counts = bool(
        max(
            one_hits,
            two_hits1,
            two_hits2,
            one_unresolved,
            two_unresolved,
            int(checkpoints.max(initial=0)),
            int(paired.max(initial=0)),
        )
        <= config.walkers
    )
    in_range_passed = bool(
        integer_arrays
        and nonnegative_arrays
        and bounded_counts
        and one_unresolved >= 0
        and two_unresolved >= 0
        and float(hold.min()) >= 0.0
        and float(hold.max()) < 1.0
    )

    mean_error = abs(float(hold.mean(dtype=np.float64)) - config.base_hold)
    fixed_mean_passed = bool(mean_error <= FIXED_MEAN_ATOL)
    precedence_passed = bool(np.all(paired[2, :] == 0))

    gates: dict[str, Any] = {
        "mass": {
            "passed": final_mass and checkpoint_mass,
            "final_mass_passed": final_mass,
            "checkpoint_mass_passed": checkpoint_mass,
        },
        "subset": {
            "passed": subset_passed,
            "invalid_two_target1_not_one_target1": subset_invalid,
            "histogram_elementwise_subset": bool(np.all(two_hist1 <= one_hist)),
        },
        "monotone": {"passed": monotone_passed},
        "in_range": {
            "passed": in_range_passed,
            "integer_arrays": integer_arrays,
            "nonnegative_arrays": nonnegative_arrays,
            "bounded_counts": bounded_counts,
        },
        "fixed_mean": {
            "passed": fixed_mean_passed,
            "observed": float(hold.mean(dtype=np.float64)),
            "expected": config.base_hold,
            "absolute_error": mean_error,
            "absolute_tolerance": FIXED_MEAN_ATOL,
        },
        "checkpoint_histogram_consistency": {"passed": bool(prefix_passed)},
        "absorbing_precedence": {
            "passed": precedence_passed,
            "rule": "target1_before_target2_then_no_further_motion",
        },
    }
    gates["all_passed"] = all(bool(value["passed"]) for value in gates.values())
    return gates


def _checkpoint_payload(arrays: SimulationArrays) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for step, row in zip(arrays.checkpoint_steps.tolist(), arrays.checkpoint_counts):
        result[str(int(step))] = {
            "one_target1": int(row[0]),
            "one_unresolved": int(row[1]),
            "two_target1": int(row[2]),
            "two_target2": int(row[3]),
            "two_unresolved": int(row[4]),
            "walkers": int(row[5]),
        }
    return result


def _paired_payload(paired: np.ndarray) -> dict[str, int]:
    return {
        "one_unresolved__two_unresolved": int(paired[0, 0]),
        "one_unresolved__two_target1": int(paired[0, 1]),
        "one_unresolved__two_target2": int(paired[0, 2]),
        "one_target1__two_unresolved": int(paired[1, 0]),
        "one_target1__two_target1": int(paired[1, 1]),
        "one_target1__two_target2": int(paired[1, 2]),
        "invalid_one_target_state2_total": int(paired[2, :].sum(dtype=np.int64)),
    }


def _ensure_fresh_outputs(output_json: Path, output_npz: Path) -> None:
    if os.path.abspath(output_json) == os.path.abspath(output_npz):
        raise ValueError("JSON and NPZ output paths must be different")
    existing = [str(path) for path in (output_json, output_npz) if path.exists()]
    if existing:
        raise FileExistsError("refusing to overwrite output: " + ", ".join(existing))


def _write_npz_temp(parent: Path, name: str, arrays: SimulationArrays) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_path = tempfile.mkstemp(prefix=f".{name}.", suffix=".tmp", dir=parent)
    temp_path = Path(raw_path)
    try:
        with os.fdopen(descriptor, "w+b") as handle:
            np.savez_compressed(
                handle,
                schema_version=np.asarray(SIDECAR_SCHEMA_VERSION, dtype=np.int64),
                one_target1_fpt_histogram=arrays.one_target1_fpt,
                two_target1_fpt_histogram=arrays.two_target1_fpt,
                two_target2_fpt_histogram=arrays.two_target2_fpt,
                checkpoint_steps=arrays.checkpoint_steps,
                checkpoint_counts=arrays.checkpoint_counts,
                paired_outcome_counts=arrays.paired_outcomes,
            )
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise
    return temp_path


def _write_json_temp(parent: Path, name: str, payload: Mapping[str, Any]) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    descriptor, raw_path = tempfile.mkstemp(prefix=f".{name}.", suffix=".tmp", dir=parent)
    temp_path = Path(raw_path)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise
    return temp_path


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _install_output_pair(
    npz_temp: Path,
    output_npz: Path,
    json_temp: Path,
    output_json: Path,
) -> None:
    npz_installed = False
    try:
        os.link(npz_temp, output_npz)
        npz_installed = True
        _fsync_directory(output_npz.parent)
        os.link(json_temp, output_json)
        _fsync_directory(output_json.parent)
    except BaseException:
        if npz_installed:
            try:
                if os.path.samefile(npz_temp, output_npz):
                    output_npz.unlink()
                    _fsync_directory(output_npz.parent)
            except FileNotFoundError:
                pass
        raise
    finally:
        npz_temp.unlink(missing_ok=True)
        json_temp.unlink(missing_ok=True)


def run(args: argparse.Namespace, *, argv: Sequence[str]) -> dict[str, Any]:
    _ensure_fresh_outputs(args.output_json, args.output_npz)
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    device = torch.device(args.device)

    manifest, _manifest_bytes, manifest_sha256 = load_manifest(args.manifest)
    expected_pack_hash = expected_field_pack_sha256(manifest)
    contrasts, disorder_seeds, field_pack_sha256 = load_field_pack(
        args.field_pack, expected_pack_hash
    )
    height, width = int(contrasts.shape[1]), int(contrasts.shape[2])
    config = resolve_cell_config(manifest, args.cell_id, width=width, height=height)
    if config.disorder_replicate >= contrasts.shape[0]:
        raise ValueError("disorder_replicate is outside field pack")
    contrast = np.ascontiguousarray(
        contrasts[config.disorder_replicate], dtype="<f8"
    )
    hold_np = construct_hold_field(contrast, config)
    hold = torch.from_numpy(hold_np.astype(np.float32, copy=True)).to(device)

    source = Path(__file__).resolve()
    source_sha256 = _sha256_file(source)
    started = time.monotonic()
    arrays = simulate_pair(config, device, hold)
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elapsed_seconds = time.monotonic() - started

    gates = evaluate_gates(config, hold_np, arrays)
    if not gates["all_passed"]:
        failed = [
            name
            for name, value in gates.items()
            if name != "all_passed" and not value["passed"]
        ]
        raise AssertionError("v3 scientific gates failed: " + ", ".join(failed))

    args.output_npz.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    npz_temp = _write_npz_temp(args.output_npz.parent, args.output_npz.name, arrays)
    try:
        sidecar_sha256 = _sha256_file(npz_temp)
        one_target1 = summarize_histogram(arrays.one_target1_fpt, config.walkers)
        two_target1 = summarize_histogram(arrays.two_target1_fpt, config.walkers)
        two_target2 = summarize_histogram(arrays.two_target2_fpt, config.walkers)
        one_unresolved = config.walkers - one_target1["hits"]
        two_unresolved = config.walkers - two_target1["hits"] - two_target2["hits"]
        payload: dict[str, Any] = {
            "schema": RESULT_SCHEMA,
            "manifest": {
                "filename": args.manifest.name,
                "sha256": manifest_sha256,
                "schema": manifest["schema"],
                "cell_id": config.cell_id,
                "profile": config.profile,
            },
            "parameters": {
                "walkers": config.walkers,
                "steps": config.steps,
                "batch_size": config.batch_size,
                "base_hold": config.base_hold,
                "amplitude": config.amplitude,
                "target_radius": config.target_radius,
                "disorder_replicate": config.disorder_replicate,
                "disorder_seed": int(disorder_seeds[config.disorder_replicate]),
                "walk_replicate": config.walk_replicate,
                "checkpoints": list(config.checkpoints),
            },
            "domain": {
                "source": "field_pack_contrast_shape",
                "width": width,
                "height": height,
                "boundary": "reflecting_attempted_outside_stays",
                "start": {"x": config.start_x, "y": config.start_y},
                "target1": {"x": config.target1_x, "y": config.target1_y},
                "target2": {"x": config.target2_x, "y": config.target2_y},
                "absorbing_precedence": "target1_then_target2_then_stop",
            },
            "rng": {
                "algorithm": "torch_generator_device_native",
                "walk_seed": config.walk_seed,
                "walk_seed_origin": config.walk_seed_origin,
                "disorder_stride": DISORDER_SEED_STRIDE,
                "walk_stride": WALK_SEED_STRIDE,
                "batch_seed_rule": "walk_seed_plus_batch_start",
                "common_random_numbers": True,
                "deterministic_for_fixed_manifest_runtime_device": True,
            },
            "field": {
                "pack_filename": args.field_pack.name,
                "pack_sha256": field_pack_sha256,
                "expected_pack_sha256": expected_pack_hash,
                "contrast_sha256_float64_le": _sha256_bytes(contrast.tobytes(order="C")),
                "hold_sha256_float64_le": _sha256_bytes(hold_np.tobytes(order="C")),
                "minimum": float(hold_np.min()),
                "mean": float(hold_np.mean(dtype=np.float64)),
                "maximum": float(hold_np.max()),
                "standard_deviation": float(hold_np.std(dtype=np.float64)),
                "device_dtype": str(hold.dtype),
            },
            "one_target": {
                "target1": one_target1,
                "unresolved": one_unresolved,
                "unresolved_probability": one_unresolved / config.walkers,
                "mass_balance": (one_target1["hits"] + one_unresolved)
                / config.walkers,
            },
            "two_targets": {
                "target1": two_target1,
                "target2": two_target2,
                "unresolved": two_unresolved,
                "unresolved_probability": two_unresolved / config.walkers,
                "mass_balance": (
                    two_target1["hits"] + two_target2["hits"] + two_unresolved
                )
                / config.walkers,
            },
            "paired_outcomes": _paired_payload(arrays.paired_outcomes),
            "cumulative_counts": _checkpoint_payload(arrays),
            "histograms": {
                "format": "npz_compressed_integer_v3",
                "path": args.output_npz.name,
                "sha256": sidecar_sha256,
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
            },
            "gates": gates,
            "gating_probability_drop": (
                one_target1["probability"] - two_target1["probability"]
            ),
            "gating_probability_ratio": (
                two_target1["probability"] / one_target1["probability"]
                if one_target1["probability"]
                else None
            ),
            "target2_first_probability": two_target2["probability"],
            "provenance": {
                "source": source.name,
                "source_sha256": source_sha256,
                "argv": [source.name, *argv],
                "slurm": {
                    key: os.environ.get(key)
                    for key in (
                        "SLURM_JOB_ID",
                        "SLURM_ARRAY_JOB_ID",
                        "SLURM_ARRAY_TASK_ID",
                        "SLURM_JOB_NAME",
                        "SLURM_NODELIST",
                        "SLURM_CPUS_PER_TASK",
                        "SLURM_JOB_ACCOUNT",
                        "SLURM_JOB_PARTITION",
                    )
                },
            },
            "runtime": {
                "elapsed_seconds": elapsed_seconds,
                "hostname": platform.node(),
                "python": platform.python_version(),
                "numpy": np.__version__,
                "torch": torch.__version__,
                "cuda": torch.version.cuda,
                "device": str(device),
                "gpu": (
                    torch.cuda.get_device_name(device)
                    if device.type == "cuda"
                    else None
                ),
            },
        }
        json_temp = _write_json_temp(args.output_json.parent, args.output_json.name, payload)
    except BaseException:
        npz_temp.unlink(missing_ok=True)
        raise

    _install_output_pair(npz_temp, args.output_npz, json_temp, args.output_json)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(effective_argv)
    payload = run(args, argv=effective_argv)
    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "cell_id": payload["manifest"]["cell_id"],
                "elapsed_seconds": payload["runtime"]["elapsed_seconds"],
                "gating_probability_drop": payload["gating_probability_drop"],
                "manifest_sha256": payload["manifest"]["sha256"],
                "source_sha256": payload["provenance"]["source_sha256"],
                "field_pack_sha256": payload["field"]["pack_sha256"],
                "all_gates_passed": payload["gates"]["all_passed"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
