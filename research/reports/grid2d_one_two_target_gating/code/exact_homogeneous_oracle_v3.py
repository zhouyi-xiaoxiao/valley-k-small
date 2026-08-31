#!/usr/bin/env python3
"""Deterministic homogeneous oracle for the v3 two-target gating campaign.

This is an independent, non-Monte-Carlo backend.  It propagates probability
mass with the exact sparse one-step transition operator at the manifest's
frozen checkpoints and solves sparse Dirichlet systems for eventual target
splitting.  Attempted moves outside the rectangular domain stay at the current
site, and target 1 has precedence wherever the two absorbing disks overlap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import scipy
from scipy import sparse
from scipy.sparse import linalg as sparse_linalg

GPU_MANIFEST_SCHEMA = "grid2d-one-two-target-gating-gpu-v3-manifest"
ORACLE_MANIFEST_SCHEMA = "grid2d-one-two-target-gating-exact-oracle-v3-manifest"
RESULT_SCHEMA = "grid2d-one-two-target-gating-exact-homogeneous-oracle-v3"
NUMERICAL_ATOL = 1.0e-11
ROW_STOCHASTIC_ATOL = 1.0e-14
FROZEN_TARGET2 = frozenset(
    (x_value, y_value)
    for x_value in (24, 32, 40)
    for y_value in (9, 16, 24, 31, 38)
)


@dataclass(frozen=True)
class Geometry:
    geometry_id: str
    target2_x: int
    target2_y: int


@dataclass(frozen=True)
class OracleConfig:
    source_mode: str
    width: int
    height: int
    normalization_walkers: int
    steps: int
    checkpoints: tuple[int, ...]
    base_hold: float
    target_radius: int
    start_x: int
    start_y: int
    target1_x: int
    target1_y: int
    geometries: tuple[Geometry, ...]


@dataclass(frozen=True)
class PropagationResult:
    checkpoint_steps: np.ndarray
    target1_cumulative: np.ndarray
    target2_cumulative: np.ndarray
    unresolved: np.ndarray
    minimum_probability: float
    maximum_mass_error: float


@dataclass(frozen=True)
class CommittorResult:
    target1_probability: float
    target2_probability: float
    residual_inf_norm: float
    minimum_solution_value: float
    maximum_solution_value: float
    transient_states: int


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    return parser.parse_args(argv)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        manifest = json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read canonical JSON manifest {path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("manifest root must be an object")
    return manifest, _sha256_bytes(raw)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _integer(value: Any, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _coordinate(parameters: Mapping[str, Any], prefix: str) -> tuple[int, int]:
    nested = parameters.get(prefix)
    direct_x = f"{prefix}_x"
    direct_y = f"{prefix}_y"
    if nested is not None:
        if direct_x in parameters or direct_y in parameters:
            raise ValueError(f"{prefix} must not mix nested and direct coordinates")
        nested_mapping = _mapping(nested, prefix)
        if "x" not in nested_mapping or "y" not in nested_mapping:
            raise ValueError(f"{prefix} must contain x and y")
        return (
            _integer(nested_mapping["x"], f"{prefix}.x"),
            _integer(nested_mapping["y"], f"{prefix}.y"),
        )
    if direct_x not in parameters or direct_y not in parameters:
        raise ValueError(f"missing {direct_x}/{direct_y}")
    return (
        _integer(parameters[direct_x], direct_x),
        _integer(parameters[direct_y], direct_y),
    )


def _validated_checkpoints(value: Any, *, steps: int) -> tuple[int, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("checkpoints must be a nonempty array")
    checkpoints = tuple(
        _integer(item, f"checkpoints[{index}]", minimum=0)
        for index, item in enumerate(value)
    )
    if tuple(sorted(set(checkpoints))) != checkpoints:
        raise ValueError("checkpoints must be strictly increasing and unique")
    if checkpoints[-1] != steps:
        raise ValueError("the final checkpoint must equal steps")
    return checkpoints


def _validate_coordinates(config: OracleConfig) -> None:
    coordinates = (
        ("start", config.start_x, config.start_y),
        ("target1", config.target1_x, config.target1_y),
        *(
            (f"target2[{geometry.geometry_id}]", geometry.target2_x, geometry.target2_y)
            for geometry in config.geometries
        ),
    )
    for name, x_value, y_value in coordinates:
        if not (0 <= x_value < config.width and 0 <= y_value < config.height):
            raise ValueError(
                f"{name}=({x_value},{y_value}) is outside "
                f"width={config.width}, height={config.height}"
            )


def _finalize_config(config: OracleConfig) -> OracleConfig:
    if config.width < 1 or config.height < 1:
        raise ValueError("domain dimensions must be positive")
    if config.normalization_walkers < 1:
        raise ValueError("normalization_walkers must be positive")
    if config.steps < 1:
        raise ValueError("steps must be positive")
    if not 0.0 <= config.base_hold < 1.0:
        raise ValueError("base_hold must be in [0,1)")
    if config.target_radius < 0:
        raise ValueError("target_radius must be nonnegative")
    if not config.geometries:
        raise ValueError("at least one target2 geometry is required")
    identifiers = [geometry.geometry_id for geometry in config.geometries]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("target2 geometry IDs must be unique")
    coordinates = [
        (geometry.target2_x, geometry.target2_y) for geometry in config.geometries
    ]
    if len(set(coordinates)) != len(coordinates):
        raise ValueError("target2 coordinates must be unique")
    _validate_coordinates(config)
    return config


def _dedicated_oracle_config(manifest: Mapping[str, Any]) -> OracleConfig:
    oracle = _mapping(manifest.get("oracle"), "oracle")
    domain = _mapping(oracle.get("domain"), "oracle.domain")
    width = _integer(domain.get("width"), "oracle.domain.width", minimum=1)
    height = _integer(domain.get("height"), "oracle.domain.height", minimum=1)
    steps = _integer(oracle.get("steps"), "oracle.steps", minimum=1)
    checkpoints = _validated_checkpoints(oracle.get("checkpoints"), steps=steps)
    start_x, start_y = _coordinate(oracle, "start")
    target1_x, target1_y = _coordinate(oracle, "target1")
    raw_geometries = oracle.get("target2_geometries")
    if not isinstance(raw_geometries, list):
        raise ValueError("oracle.target2_geometries must be an array")
    geometries: list[Geometry] = []
    for index, raw_geometry in enumerate(raw_geometries):
        geometry = _mapping(raw_geometry, f"oracle.target2_geometries[{index}]")
        if "target2" in geometry:
            target2_x, target2_y = _coordinate(geometry, "target2")
        else:
            target2_x = _integer(geometry.get("x"), f"geometry[{index}].x")
            target2_y = _integer(geometry.get("y"), f"geometry[{index}].y")
        geometry_id = geometry.get("geometry_id", f"target2_x{target2_x}_y{target2_y}")
        if not isinstance(geometry_id, str) or not geometry_id:
            raise ValueError(f"geometry[{index}].geometry_id must be a nonempty string")
        geometries.append(Geometry(geometry_id, target2_x, target2_y))
    return _finalize_config(
        OracleConfig(
            source_mode="dedicated_oracle_manifest",
            width=width,
            height=height,
            normalization_walkers=_integer(
                oracle.get("normalization_walkers"),
                "oracle.normalization_walkers",
                minimum=1,
            ),
            steps=steps,
            checkpoints=checkpoints,
            base_hold=_number(oracle.get("base_hold"), "oracle.base_hold"),
            target_radius=_integer(
                oracle.get("target_radius"), "oracle.target_radius", minimum=0
            ),
            start_x=start_x,
            start_y=start_y,
            target1_x=target1_x,
            target1_y=target1_y,
            geometries=tuple(geometries),
        )
    )


def _merge_gpu_cell(
    manifest: Mapping[str, Any], cell: Mapping[str, Any], index: int
) -> dict[str, Any]:
    parameters = dict(_mapping(manifest.get("defaults"), "defaults"))
    profile_value = cell.get("profile", manifest.get("default_profile"))
    if profile_value is not None:
        if not isinstance(profile_value, str) or not profile_value:
            raise ValueError(f"cells[{index}].profile must be a nonempty string")
        profiles = _mapping(manifest.get("profiles"), "profiles")
        if profile_value not in profiles:
            raise ValueError(f"cells[{index}] selects unknown profile {profile_value!r}")
        parameters.update(_mapping(profiles[profile_value], f"profiles.{profile_value}"))
    nested = cell.get("parameters")
    if nested is not None:
        parameters.update(_mapping(nested, f"cells[{index}].parameters"))
    reserved = {"cell_id", "profile", "parameters", "label", "notes"}
    for key, value in cell.items():
        if key not in reserved:
            if isinstance(nested, Mapping) and key in nested:
                raise ValueError(f"cells[{index}] duplicates parameter {key!r}")
            parameters[key] = value
    return parameters


def _gpu_manifest_config(manifest: Mapping[str, Any]) -> OracleConfig:
    campaign = _mapping(manifest.get("campaign"), "campaign")
    domain = _mapping(campaign.get("domain"), "campaign.domain")
    width = _integer(domain.get("width"), "campaign.domain.width", minimum=1)
    height = _integer(domain.get("height"), "campaign.domain.height", minimum=1)
    raw_cells = manifest.get("cells")
    if not isinstance(raw_cells, list) or not raw_cells:
        raise ValueError("cells must be a nonempty array")

    seen_cell_ids: set[int] = set()
    homogeneous: list[dict[str, Any]] = []
    for index, raw_cell in enumerate(raw_cells):
        cell = _mapping(raw_cell, f"cells[{index}]")
        cell_id = _integer(cell.get("cell_id"), f"cells[{index}].cell_id", minimum=0)
        if cell_id in seen_cell_ids:
            raise ValueError(f"duplicate cell_id {cell_id}")
        seen_cell_ids.add(cell_id)
        parameters = _merge_gpu_cell(manifest, cell, index)
        amplitude = _number(parameters.get("amplitude"), f"cells[{index}].amplitude")
        if amplitude == 0.0:
            homogeneous.append(parameters)
    if not homogeneous:
        raise ValueError("manifest contains no amplitude==0 cells")

    def scientific_signature(parameters: Mapping[str, Any]) -> tuple[Any, ...]:
        start = _coordinate(parameters, "start")
        target1 = _coordinate(parameters, "target1")
        steps = _integer(parameters.get("steps"), "steps", minimum=1)
        checkpoints = _validated_checkpoints(parameters.get("checkpoints"), steps=steps)
        return (
            _integer(parameters.get("walkers"), "walkers", minimum=1),
            steps,
            checkpoints,
            _number(parameters.get("base_hold"), "base_hold"),
            _integer(parameters.get("target_radius"), "target_radius", minimum=0),
            start,
            target1,
        )

    first_signature = scientific_signature(homogeneous[0])
    for index, parameters in enumerate(homogeneous[1:], start=1):
        if scientific_signature(parameters) != first_signature:
            raise ValueError(
                "amplitude==0 cells disagree on walkers, horizon, checkpoints, "
                f"base_hold, radius, start, or target1 (homogeneous index {index})"
            )

    geometry_coordinates = sorted({_coordinate(parameters, "target2") for parameters in homogeneous})
    geometries = tuple(
        Geometry(f"target2_x{x_value}_y{y_value}", x_value, y_value)
        for x_value, y_value in geometry_coordinates
    )
    walkers, steps, checkpoints, base_hold, radius, start, target1 = first_signature
    config = _finalize_config(
        OracleConfig(
            source_mode="gpu_manifest_amplitude_zero_projection",
            width=width,
            height=height,
            normalization_walkers=walkers,
            steps=steps,
            checkpoints=checkpoints,
            base_hold=base_hold,
            target_radius=radius,
            start_x=start[0],
            start_y=start[1],
            target1_x=target1[0],
            target1_y=target1[1],
            geometries=geometries,
        )
    )
    if campaign.get("kind") == "production":
        actual_geometries = {
            (geometry.target2_x, geometry.target2_y) for geometry in config.geometries
        }
        expected_core = (
            config.width == 64
            and config.height == 48
            and config.normalization_walkers == 1_000_000
            and config.steps == 80_000
            and config.checkpoints == (5_000, 10_000, 20_000, 40_000, 80_000)
            and config.base_hold == 0.30
            and config.target_radius == 3
            and (config.start_x, config.start_y) == (7, 24)
            and (config.target1_x, config.target1_y) == (54, 24)
        )
        if not expected_core or actual_geometries != FROZEN_TARGET2:
            raise ValueError(
                "production manifest amplitude==0 projection differs from the frozen "
                "64x48, 15-geometry homogeneous protocol"
            )
    return config


def resolve_config(manifest: Mapping[str, Any]) -> OracleConfig:
    schema = manifest.get("schema")
    if schema == ORACLE_MANIFEST_SCHEMA:
        return _dedicated_oracle_config(manifest)
    if schema == GPU_MANIFEST_SCHEMA:
        return _gpu_manifest_config(manifest)
    raise ValueError(
        f"manifest schema must be {ORACLE_MANIFEST_SCHEMA!r} or {GPU_MANIFEST_SCHEMA!r}"
    )


def build_transition_matrix(config: OracleConfig) -> sparse.csr_matrix:
    """Return the row-stochastic attempted-outside-stays transition matrix."""

    state_count = config.width * config.height
    move_probability = (1.0 - config.base_hold) / 4.0
    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []
    for y_value in range(config.height):
        for x_value in range(config.width):
            source = y_value * config.width + x_value
            rows.append(source)
            columns.append(source)
            values.append(config.base_hold)
            for delta_x, delta_y in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                target_x = min(max(x_value + delta_x, 0), config.width - 1)
                target_y = min(max(y_value + delta_y, 0), config.height - 1)
                rows.append(source)
                columns.append(target_y * config.width + target_x)
                values.append(move_probability)
    transition = sparse.coo_matrix(
        (np.asarray(values), (np.asarray(rows), np.asarray(columns))),
        shape=(state_count, state_count),
        dtype=np.float64,
    ).tocsr()
    transition.sum_duplicates()
    transition.sort_indices()
    return transition


def target_mask(
    *, width: int, height: int, center_x: int, center_y: int, radius: int
) -> np.ndarray:
    y_values, x_values = np.mgrid[0:height, 0:width]
    return np.asarray(
        (x_values - center_x) ** 2 + (y_values - center_y) ** 2 <= radius**2,
        dtype=bool,
    ).reshape(-1)


def _absorption_masks(config: OracleConfig) -> tuple[np.ndarray, np.ndarray]:
    target1 = target_mask(
        width=config.width,
        height=config.height,
        center_x=config.target1_x,
        center_y=config.target1_y,
        radius=config.target_radius,
    )
    column_count = 1 + len(config.geometries)
    target2 = np.zeros((target1.size, column_count), dtype=bool)
    for column, geometry in enumerate(config.geometries, start=1):
        raw_target2 = target_mask(
            width=config.width,
            height=config.height,
            center_x=geometry.target2_x,
            center_y=geometry.target2_y,
            radius=config.target_radius,
        )
        target2[:, column] = raw_target2 & ~target1
    return target1, target2


def propagate_checkpoints(
    config: OracleConfig, transition: sparse.csr_matrix
) -> PropagationResult:
    """Propagate one-target and every two-target condition in one sparse pass."""

    target1_mask, target2_masks = _absorption_masks(config)
    column_count = 1 + len(config.geometries)
    alive = np.zeros((config.width * config.height, column_count), dtype=np.float64)
    start_index = config.start_y * config.width + config.start_x
    alive[start_index, :] = 1.0
    target1_cumulative = np.zeros(column_count, dtype=np.float64)
    target2_cumulative = np.zeros(column_count, dtype=np.float64)

    if target1_mask[start_index]:
        target1_cumulative[:] = 1.0
        alive[start_index, :] = 0.0
    else:
        initial_target2 = target2_masks[start_index]
        target2_cumulative[initial_target2] = 1.0
        alive[start_index, initial_target2] = 0.0

    checkpoint_lookup = {step: index for index, step in enumerate(config.checkpoints)}
    target1_records = np.empty((len(config.checkpoints), column_count), dtype=np.float64)
    target2_records = np.empty_like(target1_records)
    unresolved_records = np.empty_like(target1_records)
    minimum_probability = min(
        0.0,
        float(alive.min(initial=0.0)),
        float(target1_cumulative.min(initial=0.0)),
        float(target2_cumulative.min(initial=0.0)),
    )
    maximum_mass_error = 0.0
    transition_transpose = transition.transpose().tocsr()

    def record(step: int) -> None:
        nonlocal minimum_probability, maximum_mass_error
        index = checkpoint_lookup.get(step)
        if index is None:
            return
        unresolved = alive.sum(axis=0, dtype=np.float64)
        mass = target1_cumulative + target2_cumulative + unresolved
        target1_records[index] = target1_cumulative
        target2_records[index] = target2_cumulative
        unresolved_records[index] = unresolved
        minimum_probability = min(
            minimum_probability,
            float(alive.min(initial=0.0)),
            float(target1_cumulative.min(initial=0.0)),
            float(target2_cumulative.min(initial=0.0)),
            float(unresolved.min(initial=0.0)),
        )
        maximum_mass_error = max(
            maximum_mass_error, float(np.max(np.abs(mass - 1.0), initial=0.0))
        )

    record(0)
    for step in range(1, config.steps + 1):
        alive = np.asarray(transition_transpose @ alive, dtype=np.float64)
        target1_hits = alive[target1_mask, :].sum(axis=0, dtype=np.float64)
        target1_cumulative += target1_hits
        alive[target1_mask, :] = 0.0
        target2_hits = np.sum(
            np.where(target2_masks, alive, 0.0), axis=0, dtype=np.float64
        )
        target2_cumulative += target2_hits
        alive[target2_masks] = 0.0
        record(step)

    return PropagationResult(
        checkpoint_steps=np.asarray(config.checkpoints, dtype=np.int64),
        target1_cumulative=target1_records,
        target2_cumulative=target2_records,
        unresolved=unresolved_records,
        minimum_probability=minimum_probability,
        maximum_mass_error=maximum_mass_error,
    )


def solve_committor(
    config: OracleConfig,
    transition: sparse.csr_matrix,
    geometry: Geometry,
) -> CommittorResult:
    """Solve the two-boundary eventual splitting Dirichlet problem."""

    target1 = target_mask(
        width=config.width,
        height=config.height,
        center_x=config.target1_x,
        center_y=config.target1_y,
        radius=config.target_radius,
    )
    target2 = target_mask(
        width=config.width,
        height=config.height,
        center_x=geometry.target2_x,
        center_y=geometry.target2_y,
        radius=config.target_radius,
    ) & ~target1
    transient = ~(target1 | target2)
    start_index = config.start_y * config.width + config.start_x
    if target1[start_index]:
        return CommittorResult(1.0, 0.0, 0.0, 0.0, 1.0, int(transient.sum()))
    if target2[start_index]:
        return CommittorResult(0.0, 1.0, 0.0, 0.0, 1.0, int(transient.sum()))

    transient_indices = np.flatnonzero(transient)
    start_position = int(np.searchsorted(transient_indices, start_index))
    if start_position >= transient_indices.size or transient_indices[start_position] != start_index:
        raise ArithmeticError("start state is missing from transient index")
    q_matrix = transition[transient][:, transient].tocsr()
    boundary_rhs = np.column_stack(
        (
            np.asarray(transition[transient][:, target1].sum(axis=1)).reshape(-1),
            np.asarray(transition[transient][:, target2].sum(axis=1)).reshape(-1),
        )
    )
    system = sparse.eye(q_matrix.shape[0], format="csc") - q_matrix.tocsc()
    solution = np.asarray(sparse_linalg.spsolve(system, boundary_rhs), dtype=np.float64)
    if solution.ndim == 1:
        solution = solution.reshape(-1, 2)
    residual = np.asarray(system @ solution - boundary_rhs, dtype=np.float64)
    return CommittorResult(
        target1_probability=float(solution[start_position, 0]),
        target2_probability=float(solution[start_position, 1]),
        residual_inf_norm=float(np.max(np.abs(residual), initial=0.0)),
        minimum_solution_value=float(solution.min(initial=0.0)),
        maximum_solution_value=float(solution.max(initial=0.0)),
        transient_states=int(transient_indices.size),
    )


def _probability_record(probability: float, walkers: int) -> dict[str, float]:
    return {
        "probability": float(probability),
        "expected_count_at_manifest_walkers": float(probability * walkers),
    }


def _checkpoint_records(
    config: OracleConfig,
    propagation: PropagationResult,
    column: int,
    *, include_target2: bool,
) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for index, step in enumerate(propagation.checkpoint_steps.tolist()):
        target1 = float(propagation.target1_cumulative[index, column])
        target2 = float(propagation.target2_cumulative[index, column])
        unresolved = float(propagation.unresolved[index, column])
        record: dict[str, Any] = {
            "target1_cumulative": _probability_record(
                target1, config.normalization_walkers
            ),
            "unresolved": _probability_record(unresolved, config.normalization_walkers),
            "mass": target1 + target2 + unresolved,
        }
        if include_target2:
            record["target2_cumulative"] = _probability_record(
                target2, config.normalization_walkers
            )
        records[str(step)] = record
    return records


def evaluate_gates(
    config: OracleConfig,
    transition: sparse.csr_matrix,
    propagation: PropagationResult,
    committors: Sequence[CommittorResult],
) -> dict[str, Any]:
    row_sums = np.asarray(transition.sum(axis=1)).reshape(-1)
    row_error = float(np.max(np.abs(row_sums - 1.0), initial=0.0))
    transition_minimum = float(transition.data.min(initial=0.0))
    committor_residual = max(
        (result.residual_inf_norm for result in committors), default=0.0
    )
    committor_minimum = min(
        (result.minimum_solution_value for result in committors), default=0.0
    )
    committor_maximum = max(
        (result.maximum_solution_value for result in committors), default=1.0
    )
    committor_mass_error = max(
        (
            abs(result.target1_probability + result.target2_probability - 1.0)
            for result in committors
        ),
        default=0.0,
    )
    monotone = bool(
        np.all(np.diff(propagation.target1_cumulative, axis=0) >= -NUMERICAL_ATOL)
        and np.all(np.diff(propagation.target2_cumulative, axis=0) >= -NUMERICAL_ATOL)
        and np.all(np.diff(propagation.unresolved, axis=0) <= NUMERICAL_ATOL)
    )
    _target1, target2_masks = _absorption_masks(config)
    precedence_overlap = int(np.count_nonzero(target2_masks[:, 1:] & _target1[:, None]))
    finite = bool(
        np.isfinite(propagation.target1_cumulative).all()
        and np.isfinite(propagation.target2_cumulative).all()
        and np.isfinite(propagation.unresolved).all()
        and all(
            math.isfinite(value)
            for result in committors
            for value in (
                result.target1_probability,
                result.target2_probability,
                result.residual_inf_norm,
                result.minimum_solution_value,
                result.maximum_solution_value,
            )
        )
    )
    gates: dict[str, Any] = {
        "mass_balance": {
            "passed": propagation.maximum_mass_error <= NUMERICAL_ATOL
            and committor_mass_error <= NUMERICAL_ATOL,
            "finite_checkpoint_max_abs_error": propagation.maximum_mass_error,
            "eventual_splitting_max_abs_error": committor_mass_error,
            "absolute_tolerance": NUMERICAL_ATOL,
        },
        "nonnegative_and_finite": {
            "passed": finite
            and transition_minimum >= -NUMERICAL_ATOL
            and propagation.minimum_probability >= -NUMERICAL_ATOL
            and committor_minimum >= -NUMERICAL_ATOL
            and committor_maximum <= 1.0 + NUMERICAL_ATOL,
            "transition_minimum": transition_minimum,
            "propagated_minimum": propagation.minimum_probability,
            "committor_minimum": committor_minimum,
            "committor_maximum": committor_maximum,
        },
        "row_stochastic": {
            "passed": row_error <= ROW_STOCHASTIC_ATOL,
            "maximum_absolute_row_sum_error": row_error,
            "absolute_tolerance": ROW_STOCHASTIC_ATOL,
        },
        "absorbing_precedence": {
            "passed": precedence_overlap == 0,
            "rule": "target1_then_target2_then_stop",
            "effective_target_mask_overlap_cells": precedence_overlap,
        },
        "checkpoint_monotonicity": {"passed": monotone},
        "committor_linear_system": {
            "passed": committor_residual <= NUMERICAL_ATOL,
            "maximum_residual_inf_norm": committor_residual,
            "absolute_tolerance": NUMERICAL_ATOL,
        },
    }
    gates["all_passed"] = all(
        bool(record["passed"])
        for name, record in gates.items()
        if name != "all_passed"
    )
    return gates


def build_payload(
    *,
    config: OracleConfig,
    manifest_path: Path,
    manifest_sha256: str,
    source_sha256: str,
    transition: sparse.csr_matrix,
    propagation: PropagationResult,
    committors: Sequence[CommittorResult],
    elapsed_seconds: float,
) -> dict[str, Any]:
    gates = evaluate_gates(config, transition, propagation, committors)
    if not gates["all_passed"]:
        failed = [
            name
            for name, record in gates.items()
            if name != "all_passed" and not record["passed"]
        ]
        raise ArithmeticError("oracle integrity gates failed: " + ", ".join(failed))
    geometries: list[dict[str, Any]] = []
    for column, (geometry, committor) in enumerate(
        zip(config.geometries, committors, strict=True), start=1
    ):
        geometries.append(
            {
                "geometry_id": geometry.geometry_id,
                "target2": {"x": geometry.target2_x, "y": geometry.target2_y},
                "checkpoint_cumulative": _checkpoint_records(
                    config, propagation, column, include_target2=True
                ),
                "eventual_two_target_splitting": {
                    "target1": _probability_record(
                        committor.target1_probability, config.normalization_walkers
                    ),
                    "target2": _probability_record(
                        committor.target2_probability, config.normalization_walkers
                    ),
                    "mass": committor.target1_probability
                    + committor.target2_probability,
                    "linear_residual_inf_norm": committor.residual_inf_norm,
                    "transient_states": committor.transient_states,
                },
            }
        )
    return {
        "schema": RESULT_SCHEMA,
        "created_utc": datetime.now(UTC).isoformat(),
        "manifest": {
            "filename": manifest_path.name,
            "sha256": manifest_sha256,
            "schema": GPU_MANIFEST_SCHEMA
            if config.source_mode == "gpu_manifest_amplitude_zero_projection"
            else ORACLE_MANIFEST_SCHEMA,
            "projection": config.source_mode,
        },
        "source": {
            "filename": Path(__file__).name,
            "sha256": source_sha256,
        },
        "backend": {
            "method": "sparse_probability_propagation_and_sparse_dirichlet_committor",
            "monte_carlo": False,
            "randomness": None,
            "deterministic": True,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "model": {
            "domain": {"width": config.width, "height": config.height},
            "state_count": config.width * config.height,
            "normalization_walkers": config.normalization_walkers,
            "steps": config.steps,
            "checkpoints": list(config.checkpoints),
            "base_hold": config.base_hold,
            "move_probability_per_direction": (1.0 - config.base_hold) / 4.0,
            "boundary_rule": "attempted_outside_stays",
            "start": {"x": config.start_x, "y": config.start_y},
            "target1": {"x": config.target1_x, "y": config.target1_y},
            "target_radius": config.target_radius,
            "absorbing_precedence": "target1_then_target2_then_stop",
            "geometry_count": len(config.geometries),
        },
        "transition": {
            "format": "csr_float64",
            "shape": list(transition.shape),
            "nonzero_entries": int(transition.nnz),
        },
        "one_target": {
            "checkpoint_cumulative": _checkpoint_records(
                config, propagation, 0, include_target2=False
            )
        },
        "two_target_geometries": geometries,
        "gates": gates,
        "runtime": {
            "elapsed_seconds": elapsed_seconds,
            "hostname": platform.node(),
        },
    }


def _atomic_write_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Atomically publish a new JSON file without replacing any existing path."""

    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    installed = False
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
            installed = True
        except FileExistsError as exc:
            raise FileExistsError(f"refusing to overwrite existing output: {path}") from exc
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary.exists():
            temporary.unlink()
        if not installed and path.exists():
            # A racing writer owns the path; it must never be removed here.
            pass


def run(manifest_path: Path, output_json: Path) -> dict[str, Any]:
    if output_json.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output_json}")
    source_path = Path(__file__).resolve()
    source_sha256 = _sha256_file(source_path)
    started = time.perf_counter()
    manifest, manifest_sha256 = load_manifest(manifest_path)
    config = resolve_config(manifest)
    transition = build_transition_matrix(config)
    propagation = propagate_checkpoints(config, transition)
    committors = tuple(
        solve_committor(config, transition, geometry) for geometry in config.geometries
    )
    if _sha256_file(source_path) != source_sha256:
        raise RuntimeError("oracle source changed while the calculation was running")
    payload = build_payload(
        config=config,
        manifest_path=manifest_path,
        manifest_sha256=manifest_sha256,
        source_sha256=source_sha256,
        transition=transition,
        propagation=propagation,
        committors=committors,
        elapsed_seconds=time.perf_counter() - started,
    )
    _atomic_write_new_json(output_json, payload)
    return payload


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    payload = run(args.manifest, args.output_json)
    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "manifest_sha256": payload["manifest"]["sha256"],
                "geometry_count": payload["model"]["geometry_count"],
                "all_gates_passed": payload["gates"]["all_passed"],
                "output_json": str(args.output_json),
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
