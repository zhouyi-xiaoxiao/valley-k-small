#!/usr/bin/env python3
"""Red-team and deterministic synthetic tests for secondary max-t r1."""

from __future__ import annotations

import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Iterator
from unittest import mock

import numpy as np


HERE = Path(__file__).resolve().parent
REPORT_ROOT = HERE.parent
MODULE_PATH = HERE / "analyze_gpu_gating_v3_secondary_r1.py"
SPEC = importlib.util.spec_from_file_location("secondary_r1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
secondary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(secondary)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fake_sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def inventory_digest(rows: list[dict[str, object]]) -> str:
    raw = "".join(
        f"{row['cell_id']}\t{row['json_path']}\t{row['json_sha256']}\t{row['npz_path']}\t{row['npz_sha256']}\n"
        for row in rows
    ).encode("utf-8")
    return sha_bytes(raw)


def refresh_payload_manifest(fixture: dict[str, Any]) -> None:
    lines = []
    for relative in secondary.PAYLOAD_MEMBERS:
        path = secondary.SECONDARY_ROOT / relative
        lines.append(f"{sha_bytes(path.read_bytes())}  {relative}\n")
    fixture["payload_manifest"].write_text("".join(lines), encoding="utf-8")
    fixture["payload_manifest_sha"] = sha_bytes(fixture["payload_manifest"].read_bytes())


def refresh_reduction_receipts(fixture: dict[str, Any], *, inventory: bool = False) -> None:
    payload = json.loads(fixture["reduction_json"].read_text(encoding="utf-8"))
    payload["audit"]["sacct"]["receipt_sha256"] = sha_bytes(fixture["sacct"].read_bytes())
    if inventory:
        payload["audit"]["inventory_digest"] = inventory_digest(payload["inventory"])
    fixture["reduction_json"].write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def make_fixture(upstream_root: Path, secondary_root: Path) -> dict[str, Any]:
    source_manifest = REPORT_ROOT / "artifacts/data/gating_v3_production_manifest.json"
    secondary.UPSTREAM_ROOT = upstream_root
    secondary.SECONDARY_ROOT = secondary_root

    for relative in secondary.PAYLOAD_MEMBERS:
        destination = secondary_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative.endswith("isambard_ai_v3_secondary_analysis_contract_r1.json"):
            destination.write_text(
                json.dumps(secondary._expected_contract(), sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
        else:
            source = REPORT_ROOT / relative
            shutil.copyfile(source, destination)
    payload_manifest = secondary_root / secondary.PAYLOAD_MANIFEST_RELATIVE
    fixture: dict[str, Any] = {
        "contract": secondary_root / "notes/isambard_ai_v3_secondary_analysis_contract_r1.json",
        "payload_manifest": payload_manifest,
    }
    refresh_payload_manifest(fixture)

    manifest = upstream_root / "artifacts/data/gating_v3_production_manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_manifest, manifest)
    reduction_dir = upstream_root / "artifacts/outputs/isambard_ai_v3/reductions/production-5788353-reduce-5788358"
    reduction_dir.mkdir(parents=True)
    sacct = reduction_dir / "sacct-production-5788353.psv"
    sacct_lines = ["JobIDRaw|JobID|State|ExitCode|\n", "5788357|5788357|COMPLETED|0:0|\n"]
    sacct_lines.extend(
        f"{6000000 + task}|5788357_{task}|COMPLETED|0:0|\n" for task in range(480)
    )
    sacct.write_text("".join(sacct_lines), encoding="utf-8")

    geometries = [(x, y) for x in (24, 32, 40) for y in (9, 16, 24, 31, 38)]
    amplitudes = (0.0, 0.05, 0.1, 0.15, 0.2, 0.25)
    conditions: list[dict[str, object]] = []
    csv_rows: list[dict[str, object]] = []
    raw_anchor: dict[tuple[int, int, float, int], float] = {}
    for geometry_index, (x, y) in enumerate(geometries):
        for amplitude_index, amplitude in enumerate(amplitudes):
            condition_id = fake_sha(f"condition-{x}-{y}-{amplitude}")[:16]
            blocks: list[dict[str, object]] = []
            for block in range(32):
                centered = block - 15.5
                control = 0.04 + geometry_index * 0.0003 + centered * 0.000013
                effect = amplitude * (0.012 + geometry_index * 0.0002) + amplitude * centered * (0.000071 + amplitude_index * 0.000003)
                value = control + effect
                raw_anchor[(x, y, amplitude, block)] = value
                blocks.append({"disorder_replicate": block, "gating_probability_drop": value})
                csv_rows.append(
                    {
                        "row_type": "block_mean",
                        "condition_id": condition_id,
                        "comparison_id": "",
                        "profile": "",
                        "disorder_replicate": block,
                        "walk_replicates": "0;1",
                        "steps": 80000,
                        "target2_x": x,
                        "target2_y": y,
                        "amplitude": amplitude,
                        "gating_probability_drop": value,
                        "gating_probability_drop_t_half": value - 0.0001,
                        "gating_tail_delta": 0.0001,
                        "one_unresolved_probability": 0.001,
                        "two_unresolved_probability": 0.001,
                        "diversion_probability": 0.01,
                        "acceleration_probability": 0.02,
                        "target2_first_probability": 0.03,
                        "primary_paired_effect": "",
                    }
                )
            conditions.append(
                {
                    "condition_id": condition_id,
                    "parameters": {"target2_x": x, "target2_y": y, "amplitude": amplitude},
                    "walk_replicates": [0, 1],
                    "block_means": blocks,
                }
            )
    for block in range(32):
        row = {field: "" for field in secondary.UPSTREAM_CSV_FIELDS}
        row.update(
            {
                "row_type": "primary_pair",
                "comparison_id": "synthetic-primary",
                "disorder_replicate": block,
                "walk_replicates": "0;1",
                "steps": 80000,
                "target2_x": 32,
                "target2_y": 24,
                "amplitude": "0.0->0.2",
                "primary_paired_effect": 0.002 + block * 1e-6,
            }
        )
        csv_rows.append(row)
    csv_rows.sort(
        key=lambda row: (
            str(row["row_type"]),
            str(row["condition_id"]),
            str(row["comparison_id"]),
            int(row["disorder_replicate"]),
        )
    )
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=secondary.UPSTREAM_CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(csv_rows)
    csv_data = buffer.getvalue().encode("utf-8")
    reduction_csv = reduction_dir / "reduction.csv"
    reduction_csv.write_bytes(csv_data)

    inventory: list[dict[str, object]] = []
    for cell_id in range(5760):
        task = cell_id % 480
        inventory.append(
            {
                "cell_id": cell_id,
                "profile": None,
                "json_path": f"cell-{cell_id}/cell-{cell_id}.json",
                "json_sha256": fake_sha(f"json-{cell_id}"),
                "npz_path": f"cell-{cell_id}/cell-{cell_id}.npz",
                "npz_sha256": fake_sha(f"npz-{cell_id}"),
                "slurm_array_job_id": "5788357",
                "slurm_array_task_id": str(task),
                "slurm_job_id": str(6000000 + task),
            }
        )
    reduction = {
        "schema": "grid2d-one-two-target-gating-gpu-v3-reduction-v1",
        "mode": "full",
        "audit": {
            "pass": True,
            "fail_closed": True,
            "campaign_kind": "production",
            "manifest_sha256": "419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f",
            "cell_count": 5760,
            "inventory_digest": inventory_digest(inventory),
            "sacct": {
                "provided": True,
                "verified": True,
                "receipt_filename": sacct.name,
                "receipt_sha256": sha_bytes(sacct.read_bytes()),
                "allocations_verified": 480,
                "cells_verified": 5760,
                "cells_per_allocation": 12,
                "bundled_production": True,
            },
        },
        "inventory": inventory,
        "conditions": conditions,
        "csv": {
            "kind": "block_statistics",
            "filename": reduction_csv.name,
            "sha256": sha_bytes(csv_data),
            "rows": 2912,
        },
    }
    reduction_json = reduction_dir / "reduction.json"
    reduction_json.write_text(
        json.dumps(reduction, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    fixture.update(
        {
            "manifest": manifest,
            "sacct": sacct,
            "reduction_csv": reduction_csv,
            "reduction_json": reduction_json,
            "upstream_root": upstream_root,
            "secondary_root": secondary_root,
            "raw_anchor": raw_anchor,
        }
    )
    return fixture


def make_small_raw_cell(root: Path) -> tuple[Path, Path, dict[str, Any], dict[str, Any]]:
    cell_dir = root / "cell-0"
    cell_dir.mkdir(parents=True)
    json_path = cell_dir / "cell-0.json"
    npz_path = cell_dir / "cell-0.npz"
    one_hist = np.array([0, 20, 20, 15, 20], dtype=np.int64)
    two_hist1 = np.array([0, 15, 20, 10, 15], dtype=np.int64)
    two_hist2 = np.array([0, 0, 5, 0, 5], dtype=np.int64)
    paired = np.array([[20, 0, 5], [10, 60, 5], [0, 0, 0]], dtype=np.int64)
    checkpoint_steps = np.array([2, 4], dtype=np.int64)
    checkpoint_counts = np.array(
        [[40, 60, 35, 5, 60, 100], [75, 25, 60, 10, 30, 100]], dtype=np.int64
    )
    np.savez_compressed(
        npz_path,
        schema_version=np.asarray(3, dtype=np.int64),
        one_target1_fpt_histogram=one_hist,
        two_target1_fpt_histogram=two_hist1,
        two_target2_fpt_histogram=two_hist2,
        checkpoint_steps=checkpoint_steps,
        checkpoint_counts=checkpoint_counts,
        paired_outcome_counts=paired,
    )
    npz_sha = sha_bytes(npz_path.read_bytes())
    payload = {
        "schema": "grid2d-one-two-target-gating-fixed-mean-gpu-v3",
        "manifest": {
            "filename": "gating_v3_production_manifest.json",
            "sha256": "419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f",
            "schema": "grid2d-one-two-target-gating-gpu-v3-manifest",
            "cell_id": 0,
            "profile": None,
        },
        "parameters": {
            "walkers": 100,
            "steps": 4,
            "batch_size": 64,
            "base_hold": 0.3,
            "amplitude": 0.05,
            "target_radius": 3,
            "disorder_replicate": 0,
            "disorder_seed": 1729,
            "walk_replicate": 0,
            "checkpoints": [2, 4],
        },
        "domain": {"target2": {"x": 24, "y": 9}},
        "provenance": {
            "slurm": {
                "SLURM_ARRAY_JOB_ID": "5788357",
                "SLURM_ARRAY_TASK_ID": "0",
                "SLURM_JOB_ID": "6000000",
            }
        },
        "histograms": {"path": "cell-0.npz", "sha256": npz_sha},
        "gates": {"all_passed": True},
        "gating_probability_drop": 0.15,
    }
    json_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    config = {
        "cell_id": 0,
        "target2_x": 24,
        "target2_y": 9,
        "amplitude": 0.05,
        "disorder_replicate": 0,
        "walk_replicate": 0,
        "walkers": 100,
        "steps": 4,
        "batch_size": 64,
        "base_hold": 0.3,
        "target_radius": 3,
        "checkpoints": (2, 4),
    }
    inventory = {
        "json_sha256": sha_bytes(json_path.read_bytes()),
        "npz_sha256": npz_sha,
        "slurm_job_id": "6000000",
        "slurm_array_task_id": "0",
    }
    return json_path, npz_path, config, inventory


@contextlib.contextmanager
def fixture_context() -> Iterator[tuple[Path, dict[str, Any]]]:
    old_upstream = secondary.UPSTREAM_ROOT
    old_secondary = secondary.SECONDARY_ROOT
    with tempfile.TemporaryDirectory() as name:
        base = Path(name)
        upstream = base / "upstream-read-only"
        write_root = base / "secondary-write"
        write_root.mkdir()
        try:
            yield base, make_fixture(upstream, write_root)
        finally:
            secondary.UPSTREAM_ROOT = old_upstream
            secondary.SECONDARY_ROOT = old_secondary


class SecondaryR1Tests(unittest.TestCase):
    maxDiff = None

    def run_analysis(
        self, fixture: dict[str, Any], suffix: str
    ) -> tuple[dict[str, object], Path, Path]:
        output_dir = fixture["secondary_root"] / "artifacts/outputs/isambard_ai_v3/secondary_r1" / suffix
        output_dir.mkdir(parents=True)
        output_json = output_dir / f"secondary-{suffix}.json"
        output_csv = output_dir / f"secondary-{suffix}.csv"
        raw_audit = {
            "independently_verified": True,
            "raw_cells": 5760,
            "json_npz_pairs": 5760,
            "block_means": 2880,
            "raw_inventory_digest": fake_sha("synthetic-raw-inventory"),
            "recomputed_block_digest": fake_sha("synthetic-blocks"),
        }
        with mock.patch.object(
            secondary,
            "_independent_raw_replay",
            return_value=(dict(fixture["raw_anchor"]), raw_audit),
        ):
            payload = secondary.analyze(
                contract_path=fixture["contract"],
                payload_manifest_path=fixture["payload_manifest"],
                expected_payload_manifest_sha256=str(fixture["payload_manifest_sha"]),
                manifest_path=fixture["manifest"],
                reduction_json=fixture["reduction_json"],
                reduction_csv=fixture["reduction_csv"],
                sacct_receipt=fixture["sacct"],
                output_json=output_json,
                output_csv=output_csv,
            )
        return payload, output_json, output_csv

    def test_deterministic_golden_75_rows_and_independent_sacct(self) -> None:
        with fixture_context() as (_base, fixture):
            first, first_json, first_csv = self.run_analysis(fixture, "a")
            second, second_json, second_csv = self.run_analysis(fixture, "b")
            self.assertEqual(first["method"]["simultaneous_critical_value"], second["method"]["simultaneous_critical_value"])
            self.assertEqual(first["contrasts"], second["contrasts"])
            self.assertEqual(first_csv.read_bytes(), second_csv.read_bytes())
            self.assertEqual(len(first["contrasts"]), 75)
            self.assertEqual(first["audit"]["independent_sacct"]["tasks_verified"], 480)
            self.assertEqual(first["audit"]["independent_sacct"]["unique_allocations"], 480)
            self.assertEqual(first_json.stat().st_mode & 0o777, 0o600)
            self.assertEqual(first_csv.stat().st_mode & 0o777, 0o600)
            self.assertEqual(sha_bytes(first_csv.read_bytes()), "acd967972760520ac7ca419287497f932ac0cf358c4a690c5b69268c33326dc6")
            self.assertNotEqual(first_json.read_bytes(), second_json.read_bytes())

    def test_joint_resampling_matches_manual_shared_indices(self) -> None:
        blocks = np.arange(32, dtype=np.float64)[:, None]
        slopes = np.linspace(0.5, 2.0, 75, dtype=np.float64)[None, :]
        effects = 0.01 + (blocks - 15.5) * slopes * 1e-4 + np.sin(blocks + np.arange(75)[None, :]) * 2e-5
        means, ses, observed, critical, adjusted = secondary._max_t(effects, seed=20260726, resamples=10000, critical_index=9500)
        rng = np.random.Generator(np.random.PCG64(20260726))
        maxima = []
        for _ in range(10000):
            sample = effects[rng.integers(0, 32, size=32), :]
            sample_se = np.std(sample, axis=0, ddof=1) / math.sqrt(32.0)
            maxima.append(float(np.max(np.abs((np.mean(sample, axis=0) - means) / sample_se))))
        self.assertEqual(critical, sorted(maxima)[9500])
        self.assertEqual(float(adjusted[0]), (1 + sum(value >= abs(observed[0]) for value in maxima)) / 10001)
        self.assertTrue(np.all(ses > 0.0))

    def test_payload_manifest_and_member_drift_fail_closed(self) -> None:
        with fixture_context() as (_base, fixture):
            fixture["payload_manifest"].write_bytes(fixture["payload_manifest"].read_bytes() + b"\n")
            with self.assertRaisesRegex(secondary.AuditError, "payload manifest SHA-256 drift"):
                self.run_analysis(fixture, "manifest-drift")
        with fixture_context() as (_base, fixture):
            member = fixture["secondary_root"] / "code/analyze_gpu_gating_v3_secondary_r1.py"
            member.write_bytes(member.read_bytes() + b"\n")
            with self.assertRaisesRegex(secondary.AuditError, "payload member SHA-256 drift"):
                self.run_analysis(fixture, "member-drift")

    def test_contract_exact_rejects_extra_field_and_malformed_geometry(self) -> None:
        for mutation in ("extra", "geometry"):
            with self.subTest(mutation=mutation), fixture_context() as (_base, fixture):
                contract = json.loads(fixture["contract"].read_text(encoding="utf-8"))
                if mutation == "extra":
                    contract["unexpected"] = True
                else:
                    contract["estimand"]["geometry_order"][0] = [24, 9, 99]
                fixture["contract"].write_text(json.dumps(contract), encoding="utf-8")
                refresh_payload_manifest(fixture)
                with self.assertRaisesRegex(secondary.AuditError, "contract exact schema/field/value drift"):
                    self.run_analysis(fixture, mutation)

    def test_sacct_requires_exact_480_task_bijection(self) -> None:
        for mutation, pattern in (
            ("missing", "tasks are not exactly"),
            ("duplicate", "duplicate sacct task"),
            ("extra", "outside 0..479"),
        ):
            with self.subTest(mutation=mutation), fixture_context() as (_base, fixture):
                lines = fixture["sacct"].read_text(encoding="utf-8").splitlines(keepends=True)
                if mutation == "missing":
                    lines.pop()
                elif mutation == "duplicate":
                    lines.append(lines[2])
                else:
                    lines.append("7000000|5788357_480|COMPLETED|0:0|\n")
                fixture["sacct"].write_text("".join(lines), encoding="utf-8")
                refresh_reduction_receipts(fixture)
                with self.assertRaisesRegex(secondary.AuditError, pattern):
                    self.run_analysis(fixture, mutation)

    def test_sacct_rejects_state_exit_and_allocation_mismatch(self) -> None:
        for mutation, pattern in (
            ("state", "state is not exactly COMPLETED"),
            ("exit", "exit code is not 0:0"),
            ("allocation", "sacct/inventory allocation mismatch"),
        ):
            with self.subTest(mutation=mutation), fixture_context() as (_base, fixture):
                text = fixture["sacct"].read_text(encoding="utf-8")
                if mutation == "state":
                    text = text.replace("6000000|5788357_0|COMPLETED|0:0|", "6000000|5788357_0|FAILED|0:0|", 1)
                elif mutation == "exit":
                    text = text.replace("6000000|5788357_0|COMPLETED|0:0|", "6000000|5788357_0|COMPLETED|1:0|", 1)
                else:
                    text = text.replace("6000000|5788357_0|COMPLETED|0:0|", "7999999|5788357_0|COMPLETED|0:0|", 1)
                fixture["sacct"].write_text(text, encoding="utf-8")
                refresh_reduction_receipts(fixture)
                with self.assertRaisesRegex(secondary.AuditError, pattern):
                    self.run_analysis(fixture, mutation)

    def test_inventory_requires_exact_bundle_and_unique_allocation(self) -> None:
        for mutation, pattern in (
            ("bundle", "array task mapping drift"),
            ("allocation", "allocations are not 480 unique"),
        ):
            with self.subTest(mutation=mutation), fixture_context() as (_base, fixture):
                payload = json.loads(fixture["reduction_json"].read_text(encoding="utf-8"))
                if mutation == "bundle":
                    payload["inventory"][480]["slurm_array_task_id"] = "1"
                else:
                    for cell_id in range(1, 5760, 480):
                        payload["inventory"][cell_id]["slurm_job_id"] = "6000000"
                payload["audit"]["inventory_digest"] = inventory_digest(payload["inventory"])
                fixture["reduction_json"].write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaisesRegex(secondary.AuditError, pattern):
                    self.run_analysis(fixture, mutation)

    def test_csv_manifest_hash_and_missing_block_fail_closed(self) -> None:
        with fixture_context() as (_base, fixture):
            fixture["reduction_csv"].write_bytes(fixture["reduction_csv"].read_bytes() + b"\n")
            with self.assertRaisesRegex(secondary.AuditError, "CSV content hash drift"):
                self.run_analysis(fixture, "csv-drift")
        with fixture_context() as (_base, fixture):
            fixture["manifest"].write_bytes(fixture["manifest"].read_bytes() + b"\n")
            with self.assertRaisesRegex(secondary.AuditError, "manifest SHA-256 drift"):
                self.run_analysis(fixture, "upstream-manifest-drift")
        with fixture_context() as (_base, fixture):
            payload = json.loads(fixture["reduction_json"].read_text(encoding="utf-8"))
            payload["conditions"][0]["block_means"].pop()
            fixture["reduction_json"].write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(secondary.AuditError, "32 block means"):
                self.run_analysis(fixture, "missing")

    def test_coordinated_reduction_json_csv_sha_mutation_fails_raw_anchor(self) -> None:
        with fixture_context() as (_base, fixture):
            payload = json.loads(fixture["reduction_json"].read_text(encoding="utf-8"))
            condition = payload["conditions"][1]
            condition_id = condition["condition_id"]
            original = float(condition["block_means"][0]["gating_probability_drop"])
            condition["block_means"][0]["gating_probability_drop"] = original + 0.123
            with fixture["reduction_csv"].open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            changed = 0
            for row in rows:
                if (
                    row["row_type"] == "block_mean"
                    and row["condition_id"] == condition_id
                    and row["disorder_replicate"] == "0"
                ):
                    row["gating_probability_drop"] = str(original + 0.123)
                    changed += 1
            self.assertEqual(changed, 1)
            buffer = io.StringIO(newline="")
            writer = csv.DictWriter(buffer, fieldnames=secondary.UPSTREAM_CSV_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            csv_data = buffer.getvalue().encode("utf-8")
            fixture["reduction_csv"].write_bytes(csv_data)
            payload["csv"]["sha256"] = sha_bytes(csv_data)
            fixture["reduction_json"].write_text(
                json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(secondary.AuditError, "raw/reduction block mean mismatch"):
                self.run_analysis(fixture, "coordinated-exploit")

    def test_raw_pair_discovery_rejects_missing_duplicate_and_extra(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            for cell_id in (0, 1):
                cell_dir = root / f"cell-{cell_id}"
                cell_dir.mkdir()
                (cell_dir / f"cell-{cell_id}.json").write_text("{}", encoding="utf-8")
                (cell_dir / f"cell-{cell_id}.npz").write_bytes(b"npz")
            self.assertEqual(set(secondary._discover_raw_pairs(root, {0, 1})), {0, 1})
            shutil.rmtree(root / "cell-1")
            with self.assertRaisesRegex(secondary.AuditError, "missing or incomplete"):
                secondary._discover_raw_pairs(root, {0, 1})
            cell_one = root / "cell-1"
            cell_one.mkdir()
            (cell_one / "cell-1.json").write_text("{}", encoding="utf-8")
            (cell_one / "cell-1.npz").write_bytes(b"npz")
            duplicate = root / "cell-00"
            duplicate.mkdir()
            (duplicate / "cell-0.json").write_text("{}", encoding="utf-8")
            (duplicate / "cell-0.npz").write_bytes(b"npz")
            with self.assertRaisesRegex(secondary.AuditError, "duplicate raw cell"):
                secondary._discover_raw_pairs(root, {0, 1})
            shutil.rmtree(duplicate)
            (root / "unexpected.txt").write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(secondary.AuditError, "unexpected raw-root member"):
                secondary._discover_raw_pairs(root, {0, 1})

    def test_raw_pair_discovery_rejects_external_hardlink(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            raw_root = base / "raw"
            cell_dir = raw_root / "cell-0"
            cell_dir.mkdir(parents=True)
            json_path = cell_dir / "cell-0.json"
            json_path.write_text("{}", encoding="utf-8")
            (cell_dir / "cell-0.npz").write_bytes(b"npz")
            os.link(json_path, base / "outside-hardlink.json")
            self.assertEqual(json_path.stat().st_nlink, 2)
            with self.assertRaisesRegex(secondary.AuditError, "external or internal hardlinks"):
                secondary._discover_raw_pairs(raw_root, {0})

    def test_raw_cell_replay_hash_npz_keys_shape_dtype_and_mass(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            json_path, npz_path, config, inventory = make_small_raw_cell(Path(name))
            metric, _json_sha, _npz_sha = secondary._replay_one_raw_cell(
                json_path=json_path,
                npz_path=npz_path,
                config=config,
                inventory=inventory,
                manifest_sha256="419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f",
                array_job_id="5788357",
            )
            self.assertEqual(metric, 0.15)
            npz_path.write_bytes(npz_path.read_bytes() + b"mutation")
            with self.assertRaisesRegex(secondary.AuditError, "NPZ hash/inventory mismatch"):
                secondary._replay_one_raw_cell(
                    json_path=json_path,
                    npz_path=npz_path,
                    config=config,
                    inventory=inventory,
                    manifest_sha256="419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f",
                    array_job_id="5788357",
                )

        with tempfile.TemporaryDirectory() as name:
            json_path, npz_path, config, inventory = make_small_raw_cell(Path(name))
            with np.load(npz_path, allow_pickle=False) as archive:
                arrays = {key: archive[key] for key in archive.files if key != "paired_outcome_counts"}
            np.savez_compressed(npz_path, **arrays)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            payload["histograms"]["sha256"] = sha_bytes(npz_path.read_bytes())
            json_path.write_text(json.dumps(payload), encoding="utf-8")
            inventory["npz_sha256"] = sha_bytes(npz_path.read_bytes())
            inventory["json_sha256"] = sha_bytes(json_path.read_bytes())
            with self.assertRaisesRegex(secondary.AuditError, "NPZ keys drift"):
                secondary._replay_one_raw_cell(
                    json_path=json_path,
                    npz_path=npz_path,
                    config=config,
                    inventory=inventory,
                    manifest_sha256="419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f",
                    array_job_id="5788357",
                )

        with tempfile.TemporaryDirectory() as name:
            json_path, npz_path, config, inventory = make_small_raw_cell(Path(name))
            with np.load(npz_path, allow_pickle=False) as archive:
                arrays = {key: archive[key] for key in archive.files}
            arrays["schema_version"] = np.asarray(2, dtype=np.int64)
            np.savez_compressed(npz_path, **arrays)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            payload["histograms"]["sha256"] = sha_bytes(npz_path.read_bytes())
            json_path.write_text(json.dumps(payload), encoding="utf-8")
            inventory["npz_sha256"] = sha_bytes(npz_path.read_bytes())
            inventory["json_sha256"] = sha_bytes(json_path.read_bytes())
            with self.assertRaisesRegex(secondary.AuditError, "schema_version is not 3"):
                secondary._replay_one_raw_cell(
                    json_path=json_path,
                    npz_path=npz_path,
                    config=config,
                    inventory=inventory,
                    manifest_sha256="419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f",
                    array_job_id="5788357",
                )

    def test_zero_and_nonfinite_fail_closed(self) -> None:
        with self.assertRaisesRegex(secondary.AuditError, "zero or nonfinite observed"):
            secondary._max_t(np.zeros((32, 75)), seed=20260726, resamples=10000, critical_index=9500)
        bad = np.ones((32, 75), dtype=np.float64)
        bad[0, 0] = np.nan
        with self.assertRaisesRegex(secondary.AuditError, "nonfinite"):
            secondary._max_t(bad, seed=20260726, resamples=10000, critical_index=9500)

    def test_atomic_no_overwrite_and_upstream_output_rejected(self) -> None:
        with fixture_context() as (_base, fixture):
            output_dir = fixture["secondary_root"] / "artifacts/outputs/isambard_ai_v3/secondary_r1/occupied"
            output_dir.mkdir(parents=True)
            output_json = output_dir / "occupied.json"
            output_csv = output_dir / "must-not-appear.csv"
            output_json.write_text("sentinel", encoding="utf-8")
            with self.assertRaisesRegex(secondary.AuditError, "refusing to overwrite"):
                secondary.analyze(
                    contract_path=fixture["contract"],
                    payload_manifest_path=fixture["payload_manifest"],
                    expected_payload_manifest_sha256=str(fixture["payload_manifest_sha"]),
                    manifest_path=fixture["manifest"],
                    reduction_json=fixture["reduction_json"],
                    reduction_csv=fixture["reduction_csv"],
                    sacct_receipt=fixture["sacct"],
                    output_json=output_json,
                    output_csv=output_csv,
                )
            self.assertEqual(output_json.read_text(encoding="utf-8"), "sentinel")
            self.assertFalse(output_csv.exists())

            bad_dir = fixture["upstream_root"] / "forbidden-output"
            bad_dir.mkdir()
            with self.assertRaisesRegex(secondary.AuditError, "output path must remain"):
                secondary.analyze(
                    contract_path=fixture["contract"],
                    payload_manifest_path=fixture["payload_manifest"],
                    expected_payload_manifest_sha256=str(fixture["payload_manifest_sha"]),
                    manifest_path=fixture["manifest"],
                    reduction_json=fixture["reduction_json"],
                    reduction_csv=fixture["reduction_csv"],
                    sacct_receipt=fixture["sacct"],
                    output_json=bad_dir / "bad.json",
                    output_csv=bad_dir / "bad.csv",
                )

    def test_static_sbatch_dependency_payload_freeze_and_write_root(self) -> None:
        text = (REPORT_ROOT / "code/isambard_ai_gating_v3_secondary_r1.sbatch").read_text(encoding="utf-8")
        self.assertIn("#SBATCH --dependency=afterok:5788358", text)
        self.assertIn("#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v3-secondary-r1-20260727", text)
        self.assertIn("EXPECTED_PAYLOAD_MANIFEST_SHA256=\"$1\"", text)
        self.assertIn("sha256sum -c \"${PAYLOAD_MANIFEST}\"", text)
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("mkdir ", "--output-json ", "--output-csv ")):
                self.assertNotIn("${UPSTREAM_ROOT}", stripped)
                self.assertIn("${OUTPUT", stripped)


if __name__ == "__main__":
    unittest.main()
