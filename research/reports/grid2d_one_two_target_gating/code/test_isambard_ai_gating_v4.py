#!/usr/bin/env python3
"""Contract and adversarial unit tests for the append-only v4 package."""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

import build_gating_campaign_manifest_v4 as manifest
import generate_disorder_field_pack_v4 as fields
import reduce_gpu_gating_v4 as reducer


class FakeConfig:
    def __init__(self, cell_id: int): self.cell_id = cell_id


class FakeCell:
    def __init__(self, cell_id: int, array: str = "8000"):
        self.config = FakeConfig(cell_id)
        self.slurm_array_job_id = array
        self.slurm_array_task_id = str(cell_id % 480)
        self.slurm_job_id = str(9000 + cell_id % 480)


def receipt(path: Path, *, failed_task: int | None = None, omit_task: int | None = None) -> None:
    lines = ["JobIDRaw|JobID|State|ExitCode"]
    for task in range(480):
        if task == omit_task: continue
        state, code = ("FAILED", "1:0") if task == failed_task else ("COMPLETED", "0:0")
        lines.append(f"{9000+task}|8000_{task}|{state}|{code}")
    path.write_text("\n".join(lines) + "\n")


class V4Tests(unittest.TestCase):
    def test_cell_inventory_and_seeds(self):
        cells = manifest.cells()
        self.assertEqual(len(cells), 23040)
        self.assertEqual([row["cell_id"] for row in cells], list(range(23040)))
        self.assertEqual(cells[0]["walk_seed"], 12_000_000_000)
        self.assertEqual(cells[-1]["walk_seed"], 12_000_000_000 + 104729 * 127 + 1009)

    def test_full_node_map_bijection(self):
        values = [t + 480 * (g + 4*k) for t in range(480) for g in range(4) for k in range(12)]
        self.assertEqual(sorted(values), list(range(23040)))

    def test_field_seed_and_normalization(self):
        seed, value = fields.generate_field(0)
        self.assertEqual(seed, 8_202_607_270_000)
        self.assertEqual(value.shape, (48, 64))
        self.assertEqual(math.fsum(float(x) for x in value.reshape(-1)), 0.0)
        self.assertEqual(float(np.max(np.abs(value))), 1.0)

    def test_exact_sacct_pass(self):
        cells = [FakeCell(i) for i in range(23040)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sacct.psv"; receipt(path)
            result = reducer._validate_sacct_v4(path, cells)
        self.assertTrue(result["verified"]); self.assertEqual(result["cells_per_allocation"], 48)

    def test_sacct_failed_task_rejected(self):
        cells = [FakeCell(i) for i in range(23040)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sacct.psv"; receipt(path, failed_task=17)
            with self.assertRaises(Exception): reducer._validate_sacct_v4(path, cells)

    def test_sacct_missing_task_rejected(self):
        cells = [FakeCell(i) for i in range(23040)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sacct.psv"; receipt(path, omit_task=479)
            with self.assertRaises(Exception): reducer._validate_sacct_v4(path, cells)

    def test_wrong_cell_task_mapping_rejected(self):
        cells = [FakeCell(i) for i in range(23040)]
        cells[480].slurm_array_task_id = "1"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sacct.psv"; receipt(path)
            with self.assertRaises(Exception): reducer._validate_sacct_v4(path, cells)

    def test_second_array_rejected(self):
        cells = [FakeCell(i) for i in range(23040)]
        cells[-1].slurm_array_job_id = "8001"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sacct.psv"; receipt(path)
            with self.assertRaises(Exception): reducer._validate_sacct_v4(path, cells)

    def test_manifest_pack_collision_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); same = root / "same"; same.write_bytes(b"same")
            with self.assertRaises(ValueError):
                manifest.build(pack=same, sidecar=root/"missing", runner=same, engine=same, output=root/"out", v3_pack=same)


if __name__ == "__main__":
    unittest.main()
