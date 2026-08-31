from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT_CODE = ROOT / "research" / "reports" / "grid2d_one_two_target_gating" / "code"
REDUCER_PATH = REPORT_CODE / "reduce_gpu_gating_v3.py"
RUNNER_PATH = REPORT_CODE / "gpu_gating_mc_v3.py"
SPEC = importlib.util.spec_from_file_location("reduce_gpu_gating_v3", REDUCER_PATH)
assert SPEC is not None and SPEC.loader is not None
REDUCER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = REDUCER
SPEC.loader.exec_module(REDUCER)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _summary(histogram: np.ndarray, walkers: int) -> dict[str, Any]:
    hits = int(histogram.sum())
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
    cumulative = np.cumsum(histogram)

    def quantile(level: float) -> int:
        return int(np.searchsorted(cumulative, math.ceil(level * hits), side="left"))

    return {
        "hits": hits,
        "probability": probability,
        "standard_error": math.sqrt(probability * (1.0 - probability) / walkers),
        "mean_fpt": float(np.dot(np.arange(histogram.size), histogram) / hits),
        "median_fpt": quantile(0.5),
        "q90_fpt": quantile(0.9),
    }


def _arrays(walkers: int, gating_final: float) -> dict[str, np.ndarray]:
    one_final = walkers - 100
    one_half = walkers - 1_000
    two_unresolved_final = 50
    two_unresolved_half = 950
    gating_hits_final = int(round(gating_final * walkers))
    gating_hits_half = int(round((gating_final - 0.001) * walkers))
    two1_final = one_final - gating_hits_final
    two1_half = one_half - gating_hits_half
    two2_final = walkers - two1_final - two_unresolved_final
    two2_half = walkers - two1_half - two_unresolved_half
    assert 0 <= two1_half <= two1_final
    assert 0 <= two2_half <= two2_final
    one_hist = np.zeros(11, dtype=np.int64)
    two1_hist = np.zeros(11, dtype=np.int64)
    two2_hist = np.zeros(11, dtype=np.int64)
    one_hist[5] = one_half
    one_hist[10] = one_final - one_half
    two1_hist[5] = two1_half
    two1_hist[10] = two1_final - two1_half
    two2_hist[5] = two2_half
    two2_hist[10] = two2_final - two2_half
    checkpoint_steps = np.asarray([0, 5, 10], dtype=np.int64)
    checkpoint_counts = np.asarray(
        [
            [0, walkers, 0, 0, walkers, walkers],
            [one_half, walkers - one_half, two1_half, two2_half, two_unresolved_half, walkers],
            [one_final, walkers - one_final, two1_final, two2_final, two_unresolved_final, walkers],
        ],
        dtype=np.int64,
    )
    paired = np.asarray(
        [
            [two_unresolved_final, 0, walkers - one_final - two_unresolved_final],
            [0, two1_final, one_final - two1_final],
            [0, 0, 0],
        ],
        dtype=np.int64,
    )
    return {
        "schema_version": np.asarray(3, dtype=np.int64),
        "one_target1_fpt_histogram": one_hist,
        "two_target1_fpt_histogram": two1_hist,
        "two_target2_fpt_histogram": two2_hist,
        "checkpoint_steps": checkpoint_steps,
        "checkpoint_counts": checkpoint_counts,
        "paired_outcome_counts": paired,
    }


def _result_payload(
    *,
    cell: dict[str, Any],
    profile: dict[str, Any],
    defaults: dict[str, Any],
    manifest_path: Path,
    field_pack: Path,
    contrasts: np.ndarray,
    seeds: np.ndarray,
    arrays: dict[str, np.ndarray],
    sidecar: Path,
) -> dict[str, Any]:
    merged = {**defaults, **profile, **{key: value for key, value in cell.items() if key not in {"cell_id", "profile"}}}
    cell_id = cell["cell_id"]
    disorder = merged["disorder_replicate"]
    walk = merged["walk_replicate"]
    walkers = merged["walkers"]
    contrast = np.ascontiguousarray(contrasts[disorder], dtype="<f8")
    hold = np.asarray(merged["base_hold"] + merged["amplitude"] * contrast, dtype="<f8")
    one_hist = arrays["one_target1_fpt_histogram"]
    two1_hist = arrays["two_target1_fpt_histogram"]
    two2_hist = arrays["two_target2_fpt_histogram"]
    checkpoints = arrays["checkpoint_counts"]
    paired = arrays["paired_outcome_counts"]
    one = _summary(one_hist, walkers)
    two1 = _summary(two1_hist, walkers)
    two2 = _summary(two2_hist, walkers)
    one_unresolved = walkers - one["hits"]
    two_unresolved = walkers - two1["hits"] - two2["hits"]
    source_sha256 = _sha256(RUNNER_PATH)
    field_sha256 = _sha256(field_pack)
    sidecar_sha256 = _sha256(sidecar)
    return {
        "schema": "grid2d-one-two-target-gating-fixed-mean-gpu-v3",
        "manifest": {
            "filename": manifest_path.name,
            "sha256": _sha256(manifest_path),
            "schema": "grid2d-one-two-target-gating-gpu-v3-manifest",
            "cell_id": cell_id,
            "profile": cell.get("profile"),
        },
        "parameters": {
            "walkers": walkers,
            "steps": merged["steps"],
            "batch_size": merged["batch_size"],
            "base_hold": merged["base_hold"],
            "amplitude": merged["amplitude"],
            "target_radius": merged["target_radius"],
            "disorder_replicate": disorder,
            "disorder_seed": int(seeds[disorder]),
            "walk_replicate": walk,
            "checkpoints": merged["checkpoints"],
        },
        "domain": {
            "source": "field_pack_contrast_shape",
            "width": int(contrasts.shape[2]),
            "height": int(contrasts.shape[1]),
            "boundary": "reflecting_attempted_outside_stays",
            "start": {"x": merged["start_x"], "y": merged["start_y"]},
            "target1": {"x": merged["target1_x"], "y": merged["target1_y"]},
            "target2": {"x": merged["target2_x"], "y": merged["target2_y"]},
            "absorbing_precedence": "target1_then_target2_then_stop",
        },
        "rng": {
            "algorithm": "torch_generator_device_native",
            "walk_seed": merged["seed_base"] + disorder * 104_729 + walk * 1_009,
            "walk_seed_origin": "v2_common_random_number_formula",
            "disorder_stride": 104_729,
            "walk_stride": 1_009,
            "batch_seed_rule": "walk_seed_plus_batch_start",
            "common_random_numbers": True,
            "deterministic_for_fixed_manifest_runtime_device": True,
        },
        "field": {
            "pack_filename": field_pack.name,
            "pack_sha256": field_sha256,
            "expected_pack_sha256": field_sha256,
            "contrast_sha256_float64_le": hashlib.sha256(contrast.tobytes()).hexdigest(),
            "hold_sha256_float64_le": hashlib.sha256(hold.tobytes()).hexdigest(),
            "minimum": float(hold.min()),
            "mean": float(hold.mean()),
            "maximum": float(hold.max()),
            "standard_deviation": float(hold.std()),
            "device_dtype": "torch.float32",
        },
        "one_target": {
            "target1": one,
            "unresolved": one_unresolved,
            "unresolved_probability": one_unresolved / walkers,
            "mass_balance": 1.0,
        },
        "two_targets": {
            "target1": two1,
            "target2": two2,
            "unresolved": two_unresolved,
            "unresolved_probability": two_unresolved / walkers,
            "mass_balance": 1.0,
        },
        "paired_outcomes": {
            "one_unresolved__two_unresolved": int(paired[0, 0]),
            "one_unresolved__two_target1": int(paired[0, 1]),
            "one_unresolved__two_target2": int(paired[0, 2]),
            "one_target1__two_unresolved": int(paired[1, 0]),
            "one_target1__two_target1": int(paired[1, 1]),
            "one_target1__two_target2": int(paired[1, 2]),
            "invalid_one_target_state2_total": int(paired[2, :].sum()),
        },
        "cumulative_counts": {
            str(step): {
                "one_target1": int(row[0]),
                "one_unresolved": int(row[1]),
                "two_target1": int(row[2]),
                "two_target2": int(row[3]),
                "two_unresolved": int(row[4]),
                "walkers": int(row[5]),
            }
            for step, row in zip(arrays["checkpoint_steps"].tolist(), checkpoints)
        },
        "histograms": {
            "format": "npz_compressed_integer_v3",
            "path": sidecar.name,
            "sha256": sidecar_sha256,
            "dtype": "int64",
            "fpt_index_range_inclusive": [0, merged["steps"]],
            "arrays": {
                "one_target1_fpt_histogram": [merged["steps"] + 1],
                "two_target1_fpt_histogram": [merged["steps"] + 1],
                "two_target2_fpt_histogram": [merged["steps"] + 1],
                "checkpoint_steps": [len(merged["checkpoints"])],
                "checkpoint_counts": [len(merged["checkpoints"]), 6],
                "paired_outcome_counts": [3, 3],
            },
        },
        "gates": {
            "mass": {"passed": True, "final_mass_passed": True, "checkpoint_mass_passed": True},
            "subset": {
                "passed": True,
                "invalid_two_target1_not_one_target1": int(paired[0, 1]),
                "histogram_elementwise_subset": True,
            },
            "monotone": {"passed": True},
            "in_range": {
                "passed": True,
                "integer_arrays": True,
                "nonnegative_arrays": True,
                "bounded_counts": True,
            },
            "fixed_mean": {
                "passed": True,
                "observed": float(hold.mean()),
                "expected": merged["base_hold"],
                "absolute_error": 0.0,
                "absolute_tolerance": 1e-12,
            },
            "checkpoint_histogram_consistency": {"passed": True},
            "absorbing_precedence": {
                "passed": True,
                "rule": "target1_before_target2_then_no_further_motion",
            },
            "all_passed": True,
        },
        "gating_probability_drop": one["probability"] - two1["probability"],
        "gating_probability_ratio": two1["probability"] / one["probability"],
        "target2_first_probability": two2["probability"],
        "provenance": {
            "source": RUNNER_PATH.name,
            "source_sha256": source_sha256,
            "argv": [RUNNER_PATH.name],
            "slurm": {
                "SLURM_JOB_ID": str(20_000 + cell_id),
                "SLURM_ARRAY_JOB_ID": "19000",
                "SLURM_ARRAY_TASK_ID": str(cell_id),
                "SLURM_JOB_NAME": "test",
                "SLURM_NODELIST": "nid-test",
                "SLURM_CPUS_PER_TASK": "8",
                "SLURM_JOB_ACCOUNT": "test",
                "SLURM_JOB_PARTITION": "workq",
            },
        },
        "runtime": {
            "elapsed_seconds": 1.0,
            "hostname": "nid-test",
            "python": "3.12",
            "numpy": np.__version__,
            "torch": "test",
            "cuda": "test",
            "device": "cuda",
            "gpu": "GH200",
        },
    }


def _campaign(tmp_path: Path, *, campaign_kind: str = "production") -> dict[str, Path]:
    campaign = tmp_path / "campaign"
    campaign.mkdir(parents=True)
    results = campaign / "results"
    results.mkdir()
    contrasts = np.zeros((2, 48, 64), dtype=np.float64)
    seeds = np.asarray([20260727, 20268646], dtype=np.int64)
    field_pack = campaign / "field-pack-v3.npz"
    np.savez_compressed(field_pack, contrasts=contrasts, seeds=seeds)
    defaults = {
        "base_hold": 0.3,
        "target_radius": 3,
        "start_x": 7,
        "start_y": 24,
        "target1_x": 54,
        "target1_y": 24,
        "seed_base": 1729,
    }
    profile = {
        "walkers": 100_000,
        "steps": 10,
        "batch_size": 10_000,
        "checkpoints": [0, 5, 10],
    }
    defaults.update(profile)
    conditions = (
        [(32, 24, 0.0), (32, 24, 0.2)]
        if campaign_kind == "canary"
        else [
            (24, 24, 0.0),
            (24, 24, 0.2),
            (32, 24, 0.0),
            (32, 24, 0.2),
            (40, 24, 0.0),
            (40, 24, 0.2),
        ]
    )
    cells: list[dict[str, Any]] = []
    cell_id = 0
    for target2_x, target2_y, amplitude in conditions:
        for disorder in (0, 1):
            for walk in (0, 1):
                cells.append(
                    {
                        "cell_id": cell_id,
                        "target2_x": target2_x,
                        "target2_y": target2_y,
                        "amplitude": amplitude,
                        "disorder_replicate": disorder,
                        "walk_replicate": walk,
                    }
                )
                cell_id += 1
    manifest = {
        "schema": "grid2d-one-two-target-gating-gpu-v3-manifest",
        "campaign": {
            "kind": campaign_kind,
            "created_utc": "2026-07-27T00:00:00+00:00",
            "domain": {"width": 64, "height": 48},
            "cell_count": len(cells),
        },
        "defaults": defaults,
        "profiles": {"tail_160k": {"steps": 20, "checkpoints": [0, 10, 20]}},
        "cells": cells,
        "field_pack_sha256": _sha256(field_pack),
        "artifacts": {
            "field_pack": {"filename": field_pack.name, "sha256": _sha256(field_pack)},
            "runner_source": {"filename": RUNNER_PATH.name, "sha256": _sha256(RUNNER_PATH)},
        },
        "preregistration": {
            "primary_inference": {
                "primary_geometry": {"target2_x": 32, "target2_y": 24},
                "primary_amplitude_contrast": {"high": 0.2, "low": 0.0, "contrast": "high - low"},
                "confidence_level": 0.95,
                "rope_absolute_probability": 0.002,
            },
            "gates": {
                "tail": {
                    "confidence_level": 0.95,
                    "one_target_unresolved_upper_max": 0.005,
                    "two_target_unresolved_upper_max": 0.005,
                    "horizon_drift_abs_plus_tcrit_se_max": 0.002,
                    "primary_horizon": 10,
                    "escalation_horizon": 20,
                }
            },
            "stages": [
                {
                    "stage_id": "A",
                    "selection": {
                        "target2": [{"x": 24, "y": 24}, {"x": 32, "y": 24}, {"x": 40, "y": 24}],
                        "amplitudes": [0.0, 0.2],
                    },
                }
            ],
        },
    }
    manifest_path = campaign / "manifest-v3.json"
    _write_json(manifest_path, manifest)
    geometry_offsets = {24: -0.003, 32: 0.0, 40: 0.003}
    for cell in cells:
        disorder = cell["disorder_replicate"]
        walk = cell["walk_replicate"]
        gating = (
            0.498
            + geometry_offsets[cell["target2_x"]]
            - 0.02 * cell["amplitude"]
            + 0.001 * disorder
            + 0.0004 * (2 * walk - 1)
        )
        arrays = _arrays(profile["walkers"], gating)
        cell_dir = results / "production-19000" / f"cell-{cell['cell_id']}"
        cell_dir.mkdir(parents=True)
        sidecar = cell_dir / f"cell-{cell['cell_id']}.npz"
        np.savez_compressed(sidecar, **arrays)
        payload = _result_payload(
            cell=cell,
            profile=profile,
            defaults=defaults,
            manifest_path=manifest_path,
            field_pack=field_pack,
            contrasts=contrasts,
            seeds=seeds,
            arrays=arrays,
            sidecar=sidecar,
        )
        _write_json(cell_dir / f"cell-{cell['cell_id']}.json", payload)
    receipt = campaign / "sacct.psv"
    receipt.write_text(
        "JobIDRaw|JobID|State|ExitCode\n"
        + "".join(
            f"{20_000 + cell['cell_id']}|19000_{cell['cell_id']}|COMPLETED|0:0\n"
            for cell in cells
        ),
        encoding="utf-8",
    )
    return {
        "manifest": manifest_path,
        "field_pack": field_pack,
        "results": results,
        "receipt": receipt,
        "output_json": campaign / "reduced.json",
        "output_csv": campaign / "reduced.csv",
    }


def _reduce(paths: dict[str, Path], *, mode: str = "full") -> dict[str, Any]:
    return REDUCER.reduce_campaign(
        manifest_path=paths["manifest"],
        field_pack_path=paths["field_pack"],
        results_dir=paths["results"],
        source_path=RUNNER_PATH,
        sacct_receipt=paths["receipt"],
        output_json=paths["output_json"],
        output_csv=paths["output_csv"],
        mode=mode,
    )


def test_reducer_validates_sidecars_averages_streams_then_pairs(tmp_path: Path) -> None:
    paths = _campaign(tmp_path)

    reduced = _reduce(paths)

    assert reduced["audit"]["pass"] is True
    assert reduced["audit"]["cell_count"] == 24
    assert reduced["audit"]["sacct"]["verified"] is True
    assert reduced["tail_gate"]["pass"] is True
    assert len(reduced["tail_gate"]["anchors"]) == 6
    assert reduced["primary"]["statistics"]["n_disorder_blocks"] == 2
    assert reduced["primary"]["statistics"]["mean"] == pytest.approx(-0.004)
    assert reduced["primary"]["decision"] == "negative_change"
    assert all(condition["walk_replicates"] == [0, 1] for condition in reduced["conditions"])
    assert _sha256(paths["output_csv"]) == reduced["csv"]["sha256"]


def test_inventory_mode_accepts_eight_cell_canary_without_inference(tmp_path: Path) -> None:
    paths = _campaign(tmp_path, campaign_kind="canary")

    reduced = _reduce(paths, mode="inventory")

    assert reduced["mode"] == "inventory"
    assert reduced["audit"]["campaign_kind"] == "canary"
    assert reduced["audit"]["cell_count"] == 8
    assert reduced["inventory_decision"]["pass"] is True
    assert reduced["csv"]["kind"] == "inventory"
    assert "conditions" not in reduced
    assert "tail_gate" not in reduced
    assert "primary" not in reduced
    header = paths["output_csv"].read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("cell_id,profile,json_path,json_sha256,npz_path,npz_sha256")


def test_duplicate_cell_fails_before_atomic_outputs(tmp_path: Path) -> None:
    paths = _campaign(tmp_path)
    paths["output_json"].write_text("old-json\n", encoding="utf-8")
    paths["output_csv"].write_text("old-csv\n", encoding="utf-8")
    source = next(paths["results"].rglob("cell-0.json"))
    retry = paths["results"] / "recovery-2" / "cell-0" / "cell-0.json"
    retry.parent.mkdir(parents=True)
    retry.write_bytes(source.read_bytes())

    with pytest.raises(REDUCER.AuditError, match="duplicate result cell_id 0"):
        _reduce(paths)

    assert paths["output_json"].read_text(encoding="utf-8") == "old-json\n"
    assert paths["output_csv"].read_text(encoding="utf-8") == "old-csv\n"


def test_manifest_and_npz_hash_mismatches_fail_closed(tmp_path: Path) -> None:
    paths = _campaign(tmp_path)
    result = next(paths["results"].rglob("cell-0.json"))
    payload = json.loads(result.read_text(encoding="utf-8"))
    payload["manifest"]["sha256"] = "0" * 64
    _write_json(result, payload)
    with pytest.raises(REDUCER.AuditError, match="manifest SHA-256 mismatch"):
        _reduce(paths)

    second = _campaign(tmp_path / "second")
    sidecar = next(second["results"].rglob("cell-0.npz"))
    data = bytearray(sidecar.read_bytes())
    data[-1] ^= 1
    sidecar.write_bytes(data)
    with pytest.raises(REDUCER.AuditError, match="sidecar SHA-256 mismatch"):
        _reduce(second)


def test_failed_sacct_cell_is_rejected(tmp_path: Path) -> None:
    paths = _campaign(tmp_path)
    receipt = paths["receipt"]
    receipt.write_text(
        receipt.read_text(encoding="utf-8").replace(
            "20003|19000_3|COMPLETED|0:0", "20003|19000_3|FAILED|1:0"
        ),
        encoding="utf-8",
    )

    with pytest.raises(REDUCER.AuditError, match="cell 3 is not COMPLETED"):
        _reduce(paths)


def test_bundled_sacct_maps_480_allocations_to_5760_cells(tmp_path: Path) -> None:
    array_job_id = "39000"
    cells = []
    for cell_id in range(5_760):
        task_id = cell_id % 480
        config = REDUCER.CellConfig(
            cell_id=cell_id,
            profile=None,
            walkers=1,
            steps=1,
            batch_size=1,
            base_hold=0.3,
            amplitude=0.0,
            target_radius=0,
            start_x=0,
            start_y=0,
            target1_x=1,
            target1_y=0,
            target2_x=2,
            target2_y=0,
            disorder_replicate=0,
            walk_replicate=0,
            checkpoints=(1,),
            walk_seed=1,
            walk_seed_origin="test",
        )
        cells.append(
            REDUCER.ValidatedCell(
                config=config,
                json_path=tmp_path / f"cell-{cell_id}.json",
                json_sha256=f"json-{cell_id}",
                npz_path=tmp_path / f"cell-{cell_id}.npz",
                npz_sha256=f"npz-{cell_id}",
                slurm_array_job_id=array_job_id,
                slurm_array_task_id=str(task_id),
                slurm_job_id=str(40_000 + task_id),
                metrics={},
            )
        )
    receipt = tmp_path / "bundled-sacct.psv"
    receipt.write_text(
        "JobIDRaw|JobID|State|ExitCode\n"
        + "".join(
            f"{40_000 + task}|{array_job_id}_{task}|COMPLETED|0:0\n"
            for task in range(480)
        ),
        encoding="utf-8",
    )

    result = REDUCER._validate_sacct(receipt, cells)

    assert result["verified"] is True
    assert result["bundled_production"] is True
    assert result["allocations_verified"] == 480
    assert result["cells_verified"] == 5_760
    assert result["cells_per_allocation"] == 12
