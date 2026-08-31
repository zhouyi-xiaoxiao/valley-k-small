from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest
import torch

RUNNER_PATH = Path(__file__).with_name("gpu_gating_mc_v3.py")


def _load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gpu_gating_mc_v3", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def runner() -> ModuleType:
    return _load_runner()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_inputs(
    tmp_path: Path,
    *,
    contrast: np.ndarray | None = None,
    start: tuple[int, int] = (0, 3),
    target1: tuple[int, int] = (6, 3),
    target2: tuple[int, int] = (2, 5),
    profile: str | None = None,
) -> tuple[Path, Path]:
    if contrast is None:
        contrast = (np.arange(49, dtype=np.float64).reshape(7, 7) - 24.0) / 24.0
    field_pack = tmp_path / "field-pack.npz"
    np.savez_compressed(
        field_pack,
        contrasts=np.asarray([contrast], dtype=np.float64),
        seeds=np.asarray([20260727], dtype=np.int64),
    )
    defaults = {
        "walkers": 96,
        "steps": 12,
        "batch_size": 31,
        "base_hold": 0.25,
        "target_radius": 0,
        "start_x": start[0],
        "start_y": start[1],
        "target1_x": target1[0],
        "target1_y": target1[1],
        "checkpoints": [0, 3, 6, 12],
        "seed_base": 1729,
    }
    cell: dict[str, object] = {
        "cell_id": 17,
        "disorder_replicate": 0,
        "walk_replicate": 2,
        "amplitude": 0.10,
        "target2_x": target2[0],
        "target2_y": target2[1],
    }
    manifest: dict[str, object] = {
        "schema": "grid2d-one-two-target-gating-gpu-v3-manifest",
        "field_pack_sha256": _sha256(field_pack),
        "defaults": defaults,
        "cells": [cell],
    }
    if profile is not None:
        manifest["profiles"] = {
            profile: {
                "walkers": 24,
                "steps": 4,
                "batch_size": 7,
                "checkpoints": [0, 2, 4],
            }
        }
        cell["profile"] = profile
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest_path, field_pack


def _run(
    runner: ModuleType,
    manifest: Path,
    field_pack: Path,
    output_json: Path,
    output_npz: Path,
) -> dict[str, object]:
    exit_code = runner.main(
        [
            "--manifest",
            str(manifest),
            "--field-pack",
            str(field_pack),
            "--cell-id",
            "17",
            "--device",
            "cpu",
            "--output-json",
            str(output_json),
            "--output-npz",
            str(output_npz),
        ]
    )
    assert exit_code == 0
    return json.loads(output_json.read_text())


def test_cpu_cell_is_deterministic_complete_and_hash_pinned(
    runner: ModuleType, tmp_path: Path
) -> None:
    manifest, field_pack = _write_inputs(tmp_path)
    first_json = tmp_path / "first.json"
    first_npz = tmp_path / "first.npz"
    second_json = tmp_path / "second.json"
    second_npz = tmp_path / "second.npz"

    first = _run(runner, manifest, field_pack, first_json, first_npz)
    second = _run(runner, manifest, field_pack, second_json, second_npz)

    assert first["schema"] == "grid2d-one-two-target-gating-fixed-mean-gpu-v3"
    assert first["manifest"]["sha256"] == _sha256(manifest)
    assert first["field"]["pack_sha256"] == _sha256(field_pack)
    assert first["provenance"]["source_sha256"] == _sha256(RUNNER_PATH)
    assert first["domain"]["width"] == 7
    assert first["domain"]["height"] == 7
    assert first["domain"]["target2"] == {"x": 2, "y": 5}
    assert first["domain"]["boundary"] == "reflecting_attempted_outside_stays"
    assert first["domain"]["absorbing_precedence"] == "target1_then_target2_then_stop"
    assert first["rng"]["walk_seed"] == 1729 + 2 * 1009
    assert first["rng"]["deterministic_for_fixed_manifest_runtime_device"] is True
    assert second["rng"] == first["rng"]
    assert second["gating_probability_drop"] == first["gating_probability_drop"]
    assert first["gates"]["all_passed"] is True
    for gate_name in (
        "mass",
        "subset",
        "monotone",
        "in_range",
        "fixed_mean",
        "checkpoint_histogram_consistency",
        "absorbing_precedence",
    ):
        assert first["gates"][gate_name]["passed"] is True
    assert first["histograms"]["sha256"] == _sha256(first_npz)

    with np.load(first_npz, allow_pickle=False) as first_arrays, np.load(
        second_npz, allow_pickle=False
    ) as second_arrays:
        expected_keys = {
            "schema_version",
            "one_target1_fpt_histogram",
            "two_target1_fpt_histogram",
            "two_target2_fpt_histogram",
            "checkpoint_steps",
            "checkpoint_counts",
            "paired_outcome_counts",
        }
        assert set(first_arrays.files) == expected_keys
        for key in expected_keys:
            assert first_arrays[key].dtype == np.int64
            np.testing.assert_array_equal(first_arrays[key], second_arrays[key])
        assert first_arrays["one_target1_fpt_histogram"].shape == (13,)
        assert first_arrays["two_target1_fpt_histogram"].shape == (13,)
        assert first_arrays["two_target2_fpt_histogram"].shape == (13,)
        np.testing.assert_array_equal(
            first_arrays["checkpoint_steps"], np.asarray([0, 3, 6, 12])
        )
        final = first_arrays["checkpoint_counts"][-1]
        assert int(final[0] + final[1]) == 96
        assert int(final[2] + final[3] + final[4]) == 96
        assert int(first_arrays["paired_outcome_counts"].sum()) == 96


def test_reflection_and_target1_absorbing_precedence(
    runner: ModuleType, tmp_path: Path
) -> None:
    x = torch.tensor([0, 6, 3, 3], dtype=torch.long)
    y = torch.tensor([3, 3, 0, 6], dtype=torch.long)
    direction = torch.tensor([1, 0, 3, 2], dtype=torch.long)
    trial_x, trial_y = runner.reflecting_trial_positions(
        x, y, direction, width=7, height=7
    )
    torch.testing.assert_close(trial_x, x)
    torch.testing.assert_close(trial_y, y)

    manifest, field_pack = _write_inputs(
        tmp_path,
        start=(3, 3),
        target1=(3, 3),
        target2=(3, 3),
        profile="canary",
    )
    output_json = tmp_path / "precedence.json"
    output_npz = tmp_path / "precedence.npz"
    payload = _run(runner, manifest, field_pack, output_json, output_npz)
    assert payload["parameters"]["walkers"] == 24
    assert payload["parameters"]["steps"] == 4
    assert payload["one_target"]["target1"]["hits"] == 24
    assert payload["two_targets"]["target1"]["hits"] == 24
    assert payload["two_targets"]["target2"]["hits"] == 0
    with np.load(output_npz, allow_pickle=False) as arrays:
        assert int(arrays["one_target1_fpt_histogram"][0]) == 24
        assert int(arrays["two_target1_fpt_histogram"][0]) == 24
        assert int(arrays["two_target2_fpt_histogram"].sum()) == 0


@pytest.mark.parametrize("preexisting", ["json", "npz"])
def test_refuses_to_overwrite_either_output(
    runner: ModuleType, tmp_path: Path, preexisting: str
) -> None:
    case_dir = tmp_path / preexisting
    case_dir.mkdir()
    manifest, field_pack = _write_inputs(case_dir)
    output_json = case_dir / "result.json"
    output_npz = case_dir / "result.npz"
    existing_path = output_json if preexisting == "json" else output_npz
    existing_path.write_bytes(b"sentinel")
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        _run(runner, manifest, field_pack, output_json, output_npz)
    assert existing_path.read_bytes() == b"sentinel"
    other_path = output_npz if preexisting == "json" else output_json
    assert not other_path.exists()


def test_fixed_mean_and_target_range_fail_closed(
    runner: ModuleType, tmp_path: Path
) -> None:
    nonzero_mean = np.ones((7, 7), dtype=np.float64)
    mean_dir = tmp_path / "mean"
    mean_dir.mkdir()
    manifest, field_pack = _write_inputs(mean_dir, contrast=nonzero_mean)
    with pytest.raises(ValueError, match="fixed-mean hold invariant failed"):
        _run(
            runner,
            manifest,
            field_pack,
            mean_dir / "result.json",
            mean_dir / "result.npz",
        )
    assert not (mean_dir / "result.json").exists()
    assert not (mean_dir / "result.npz").exists()

    range_dir = tmp_path / "range"
    range_dir.mkdir()
    manifest, field_pack = _write_inputs(range_dir, target2=(7, 2))
    with pytest.raises(ValueError, match="outside field-pack domain"):
        _run(
            runner,
            manifest,
            field_pack,
            range_dir / "result.json",
            range_dir / "result.npz",
        )
    assert not (range_dir / "result.json").exists()
    assert not (range_dir / "result.npz").exists()
