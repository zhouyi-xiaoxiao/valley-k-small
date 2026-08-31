from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

MODULE_PATH = Path(__file__).with_name("exact_homogeneous_oracle_v3.py")
SPEC = importlib.util.spec_from_file_location("exact_homogeneous_oracle_v3", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
oracle = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = oracle
SPEC.loader.exec_module(oracle)


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def _dedicated_manifest(
    *,
    width: int = 4,
    height: int = 3,
    steps: int = 4,
    checkpoints: list[int] | None = None,
    start: tuple[int, int] = (0, 0),
    target1: tuple[int, int] = (3, 2),
    geometries: list[tuple[int, int]] | None = None,
    radius: int = 0,
) -> dict:
    if checkpoints is None:
        checkpoints = [0, 1, steps]
    if geometries is None:
        geometries = [(0, 2), (2, 1)]
    return {
        "schema": oracle.ORACLE_MANIFEST_SCHEMA,
        "oracle": {
            "domain": {"width": width, "height": height},
            "normalization_walkers": 1_000,
            "steps": steps,
            "checkpoints": checkpoints,
            "base_hold": 0.30,
            "target_radius": radius,
            "start": {"x": start[0], "y": start[1]},
            "target1": {"x": target1[0], "y": target1[1]},
            "target2_geometries": [
                {
                    "geometry_id": f"g{index}",
                    "target2": {"x": x_value, "y": y_value},
                }
                for index, (x_value, y_value) in enumerate(geometries)
            ],
        },
    }


def _dense_reference(config, transition, geometry):
    matrix = transition.toarray()
    target1 = oracle.target_mask(
        width=config.width,
        height=config.height,
        center_x=config.target1_x,
        center_y=config.target1_y,
        radius=config.target_radius,
    )
    raw_target2 = oracle.target_mask(
        width=config.width,
        height=config.height,
        center_x=geometry.target2_x,
        center_y=geometry.target2_y,
        radius=config.target_radius,
    )
    target2 = raw_target2 & ~target1
    start = config.start_y * config.width + config.start_x
    alive = np.zeros(config.width * config.height)
    alive[start] = 1.0
    hit1 = 0.0
    hit2 = 0.0
    if target1[start]:
        hit1 = 1.0
        alive[start] = 0.0
    elif target2[start]:
        hit2 = 1.0
        alive[start] = 0.0
    records = {}
    if 0 in config.checkpoints:
        records[0] = (hit1, hit2, float(alive.sum()))
    for step in range(1, config.steps + 1):
        alive = alive @ matrix
        hit1 += float(alive[target1].sum())
        alive[target1] = 0.0
        hit2 += float(alive[target2].sum())
        alive[target2] = 0.0
        if step in config.checkpoints:
            records[step] = (hit1, hit2, float(alive.sum()))

    transient = ~(target1 | target2)
    if target1[start]:
        eventual = (1.0, 0.0)
    elif target2[start]:
        eventual = (0.0, 1.0)
    else:
        indices = np.flatnonzero(transient)
        q_matrix = matrix[np.ix_(transient, transient)]
        rhs = np.column_stack(
            (
                matrix[np.ix_(transient, target1)].sum(axis=1),
                matrix[np.ix_(transient, target2)].sum(axis=1),
            )
        )
        solution = np.linalg.solve(np.eye(indices.size) - q_matrix, rhs)
        position = int(np.flatnonzero(indices == start)[0])
        eventual = tuple(solution[position])
    return records, eventual


def test_corner_transition_is_attempted_outside_stays() -> None:
    manifest = _dedicated_manifest()
    config = oracle.resolve_config(manifest)
    transition = oracle.build_transition_matrix(config).toarray()
    move = (1.0 - config.base_hold) / 4.0

    assert transition[0, 0] == pytest.approx(config.base_hold + 2.0 * move)
    assert transition[0, 1] == pytest.approx(move)
    assert transition[0, config.width] == pytest.approx(move)
    assert np.count_nonzero(transition[0]) == 3
    np.testing.assert_allclose(transition.sum(axis=1), 1.0, atol=1e-15)


def test_tiny_sparse_oracle_matches_independent_dense_backend(tmp_path: Path) -> None:
    manifest_path = _write_json(tmp_path / "oracle.json", _dedicated_manifest())
    output_path = tmp_path / "result.json"
    payload = oracle.run(manifest_path, output_path)
    manifest, _ = oracle.load_manifest(manifest_path)
    config = oracle.resolve_config(manifest)
    transition = oracle.build_transition_matrix(config)
    propagation = oracle.propagate_checkpoints(config, transition)

    assert payload["gates"]["all_passed"] is True
    assert payload["backend"]["monte_carlo"] is False
    assert payload["source"]["sha256"] == hashlib.sha256(MODULE_PATH.read_bytes()).hexdigest()
    assert json.loads(output_path.read_text(encoding="utf-8")) == payload

    for column, geometry in enumerate(config.geometries, start=1):
        records, eventual = _dense_reference(config, transition, geometry)
        for index, step in enumerate(config.checkpoints):
            np.testing.assert_allclose(
                (
                    propagation.target1_cumulative[index, column],
                    propagation.target2_cumulative[index, column],
                    propagation.unresolved[index, column],
                ),
                records[step],
                rtol=0.0,
                atol=1e-14,
            )
        computed = oracle.solve_committor(config, transition, geometry)
        np.testing.assert_allclose(
            (computed.target1_probability, computed.target2_probability),
            eventual,
            rtol=0.0,
            atol=2e-14,
        )

    one = payload["one_target"]["checkpoint_cumulative"][str(config.steps)]
    assert one["target1_cumulative"]["expected_count_at_manifest_walkers"] == pytest.approx(
        1_000 * one["target1_cumulative"]["probability"]
    )


def test_overlapping_start_uses_target1_precedence(tmp_path: Path) -> None:
    manifest = _dedicated_manifest(
        width=3,
        height=3,
        steps=2,
        checkpoints=[0, 2],
        start=(1, 1),
        target1=(1, 1),
        geometries=[(1, 1)],
        radius=1,
    )
    payload = oracle.run(
        _write_json(tmp_path / "overlap.json", manifest), tmp_path / "result.json"
    )
    checkpoint = payload["two_target_geometries"][0]["checkpoint_cumulative"]["0"]
    splitting = payload["two_target_geometries"][0]["eventual_two_target_splitting"]

    assert checkpoint["target1_cumulative"]["probability"] == 1.0
    assert checkpoint["target2_cumulative"]["probability"] == 0.0
    assert checkpoint["unresolved"]["probability"] == 0.0
    assert splitting["target1"]["probability"] == 1.0
    assert splitting["target2"]["probability"] == 0.0
    assert payload["gates"]["absorbing_precedence"]["passed"] is True


def _gpu_manifest(*, inconsistent_zero_cell: bool = False) -> dict:
    defaults = {
        "walkers": 2_000,
        "steps": 3,
        "batch_size": 100,
        "base_hold": 0.30,
        "target_radius": 0,
        "start_x": 0,
        "start_y": 0,
        "target1_x": 4,
        "target1_y": 3,
        "checkpoints": [1, 3],
        "seed_base": 1_729,
    }
    cells = [
        {
            "cell_id": 0,
            "amplitude": 0.0,
            "target2_x": 1,
            "target2_y": 3,
            "disorder_replicate": 0,
            "walk_replicate": 0,
        },
        {
            "cell_id": 1,
            "amplitude": 0.0,
            "target2_x": 1,
            "target2_y": 3,
            "disorder_replicate": 1,
            "walk_replicate": 1,
        },
        {
            "cell_id": 2,
            "amplitude": 0.0,
            "target2_x": 2,
            "target2_y": 2,
            "disorder_replicate": 0,
            "walk_replicate": 0,
        },
        {
            # This deliberately inconsistent nonzero-amplitude cell is ignored.
            "cell_id": 3,
            "amplitude": 0.2,
            "steps": 99,
            "checkpoints": [99],
            "target2_x": 2,
            "target2_y": 2,
            "disorder_replicate": 0,
            "walk_replicate": 0,
        },
    ]
    if inconsistent_zero_cell:
        cells[2]["base_hold"] = 0.31
    return {
        "schema": oracle.GPU_MANIFEST_SCHEMA,
        "campaign": {"kind": "test", "domain": {"width": 5, "height": 4}},
        "defaults": defaults,
        "profiles": {},
        "cells": cells,
    }


def test_gpu_manifest_filters_zero_amplitude_and_deduplicates_geometry() -> None:
    config = oracle.resolve_config(_gpu_manifest())

    assert config.source_mode == "gpu_manifest_amplitude_zero_projection"
    assert config.normalization_walkers == 2_000
    assert [(item.target2_x, item.target2_y) for item in config.geometries] == [
        (1, 3),
        (2, 2),
    ]
    assert config.steps == 3


def test_gpu_manifest_rejects_inconsistent_zero_amplitude_model() -> None:
    with pytest.raises(ValueError, match="amplitude==0 cells disagree"):
        oracle.resolve_config(_gpu_manifest(inconsistent_zero_cell=True))


def test_output_overwrite_is_refused_before_recomputation(tmp_path: Path) -> None:
    manifest_path = _write_json(
        tmp_path / "oracle.json", _dedicated_manifest(steps=1, checkpoints=[0, 1])
    )
    output_path = tmp_path / "result.json"
    oracle.run(manifest_path, output_path)
    original = output_path.read_bytes()

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        oracle.run(manifest_path, output_path)
    assert output_path.read_bytes() == original


def test_duplicate_manifest_keys_fail_closed(tmp_path: Path) -> None:
    manifest_path = tmp_path / "duplicate.json"
    manifest_path.write_text(
        '{"schema":"a","schema":"b"}', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="duplicate JSON key"):
        oracle.load_manifest(manifest_path)
