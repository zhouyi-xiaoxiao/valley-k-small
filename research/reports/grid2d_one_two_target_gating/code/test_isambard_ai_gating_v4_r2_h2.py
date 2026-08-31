#!/usr/bin/env python3
"""Adversarial unit tests for the append-only v4-r2 H2 authority layer."""
from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

import analyze_gpu_gating_v4_r2_combined_h2 as combined
import runtime_probe_v4_r2_h2 as runtime
import scientific_tail_replay_v4_r2_h2 as science

HEX = "a" * 64


def write600(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    os.chmod(path, 0o600)


class AllocationBijectionTests(unittest.TestCase):
    def inventory(self, tasks: int, cells_per_task: int, array: str):
        return [
            {
                "cell_id": task + tasks * bundle,
                "slurm_array_task_id": str(task),
                "slurm_array_job_id": array,
                "slurm_job_id": str(900000 + task),
            }
            for task in range(tasks) for bundle in range(cells_per_task)
        ]

    def receipt(self, path: Path, tasks: int, array: str,
                *, duplicate_raw: bool = False, extended: bool = True):
        header = (["JobIDRaw", "JobID", "ArrayJobID", "ArrayTaskID", "State",
                   "ExitCode", "ElapsedRaw", "AllocTRES", "ReqTRES", "NNodes"]
                  if extended else ["JobIDRaw", "JobID", "State", "ExitCode"])
        rows = ["|".join(header)]
        rows.append((f"{array}|{array}|||COMPLETED|0:0|0|||0" if extended
                     else f"{array}|{array}|COMPLETED|0:0"))
        for task in range(tasks):
            raw = 900000 if duplicate_raw else 900000 + task
            rows.append((f"{raw}|{array}_{task}|{array}|{task}|COMPLETED|0:0|3600|"
                         "billing=1,gres/gpu=4|billing=1,gres/gpu=4|1")
                        if extended else
                        f"{raw}|{array}_{task}|COMPLETED|0:0")
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    def test_exact_480_global_bijection_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sacct.psv"
            self.receipt(path, 480, "8000")
            result = science.replay_sacct_bijection(
                path, "8000", self.inventory(480, 48, "8000"),
                task_count=480, cells_per_allocation=48, require_extended=True,
            )
            self.assertEqual(result["unique_job_id_raw"], 480)

    def test_duplicate_production_job_id_raw_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sacct.psv"
            self.receipt(path, 480, "8000", duplicate_raw=True)
            with self.assertRaisesRegex(ValueError, "JobIDRaw"):
                science.replay_sacct_bijection(
                    path, "8000", self.inventory(480, 48, "8000"),
                    task_count=480, cells_per_allocation=48,
                    require_extended=True,
                )

    def test_duplicate_canary_job_id_raw_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "canary.psv"
            self.receipt(path, 8, "7000", duplicate_raw=True, extended=False)
            with self.assertRaises(ValueError):
                science.replay_sacct_bijection(
                    path, "7000", self.inventory(8, 1, "7000"),
                    task_count=8, cells_per_allocation=1,
                    require_extended=False,
                )

    def test_jobid_task_swap_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sacct.psv"
            self.receipt(path, 8, "7000", extended=False)
            text = path.read_text().replace("900000|7000_0", "900000|7000_1", 1)
            path.write_text(text)
            with self.assertRaises(ValueError):
                science.replay_sacct_bijection(
                    path, "7000", self.inventory(8, 1, "7000"),
                    task_count=8, cells_per_allocation=1,
                    require_extended=False,
                )


class RawCheckpointTests(unittest.TestCase):
    def fixture(self, root: Path, *, mutate_checkpoint: bool = False):
        walkers = 10
        one = np.zeros(3, dtype=np.int64); one[1] = 5
        two1 = np.zeros(3, dtype=np.int64); two1[1] = 4
        two2 = np.zeros(3, dtype=np.int64); two2[2] = 1
        counts = np.asarray([[5, 5, 4, 0, 6, 10],
                             [5, 5, 4, 1, 5, 10]], dtype=np.int64)
        if mutate_checkpoint:
            counts[0, 0] += 1
            counts[0, 1] -= 1
        paired = np.asarray([[5, 0, 0], [0, 4, 1], [0, 0, 0]], dtype=np.int64)
        npz = root / "cell-0.npz"
        np.savez_compressed(
            npz, schema_version=np.asarray(3, dtype=np.int64),
            one_target1_fpt_histogram=one,
            two_target1_fpt_histogram=two1,
            two_target2_fpt_histogram=two2,
            checkpoint_steps=np.asarray([1, 2], dtype=np.int64),
            checkpoint_counts=counts, paired_outcome_counts=paired,
        )
        cumulative = {
            "1": {"one_target1": 5, "one_unresolved": 5, "two_target1": 4,
                  "two_target2": 0, "two_unresolved": 6, "walkers": 10},
            "2": {"one_target1": 5, "one_unresolved": 5, "two_target1": 4,
                  "two_target2": 1, "two_unresolved": 5, "walkers": 10},
        }
        js = root / "cell-0.json"
        write600(js, json.dumps({"cumulative_counts": cumulative,
                                  "gating_probability_drop": 0.1,
                                  "target2_first_probability": 0.1}))
        os.chmod(npz, 0o600)
        defaults = {"steps": 2, "checkpoints": [1, 2], "walkers": walkers}
        return npz, js, defaults

    def test_exact_raw_checkpoint_replay_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            result = science.raw_checkpoint_metrics(
                *self.fixture(Path(directory)), cell=0)
            self.assertAlmostEqual(result["gating_tail_delta"], 0.0)

    def test_checkpoint_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "checkpoint"):
                science.raw_checkpoint_metrics(
                    *self.fixture(Path(directory), mutate_checkpoint=True), cell=0)


class TailAndReceiptMutationTests(unittest.TestCase):
    def test_tail_pass_mutation_rejected(self):
        expected = {"horizon": 80000, "pass": False,
                    "thresholds": {"one": 0.005}}
        actual = copy.deepcopy(expected); actual["pass"] = True
        with self.assertRaises(ValueError):
            science.close_tree(actual, expected, "tail_gate")

    def combined_fixture(self, root: Path):
        script = root / "code" / combined.COMBINED_SCRIPT
        write600(script, "#!/bin/bash\n")
        sub = root / "artifacts/submission_h2/combined-submission.json"
        v3 = root / "v3.json"; replay = root / "replay.json"; rs = root / "r.json"
        for path in (v3, replay, rs): write600(path, "{}\n")
        job = "9001"; replay_job = "9000"; h2 = "1" * 64
        v3_sha, replay_sha, rs_sha = "2" * 64, "3" * 64, "4" * 64
        args = [h2, str(v3), v3_sha, str(replay), replay_sha, replay_job,
                str(rs), rs_sha, str(sub)]
        value = {
            "schema": combined.SUBMIT_SCHEMA,
            "status": combined.SUBMIT_STATUS, "phase": "combined",
            "job_id": job, "dependency_afterok": replay_job,
            "payload_manifest_sha256": h2,
            "phase_inputs": {"v3_release_sha256": v3_sha,
                             "v4_replay_receipt_sha256": replay_sha,
                             "replay_job_id": replay_job,
                             "replay_submission_sha256": rs_sha},
            "script": {"path": f"code/{combined.COMBINED_SCRIPT}",
                       "sha256": science.sha(script)},
            "argv": ["sbatch", "--parsable", f"--dependency=afterok:{replay_job}",
                     f"code/{combined.COMBINED_SCRIPT}", *args],
            "authorities": {
                "v3_release": {"path": str(v3), "sha256": v3_sha},
                "v4_replay": {"path": str(replay), "sha256": replay_sha},
                "replay_submission": {"path": str(rs), "sha256": rs_sha},
            },
            "scontrol_readback": (f"JobId={job} Dependency=afterok:{replay_job} "
                                  f"Command={script} WorkDir={root}"),
        }
        write600(sub, json.dumps(value))
        return sub, value, job, replay_job, h2, v3, v3_sha, replay, replay_sha, rs, rs_sha

    def validate(self, root: Path, fixture):
        sub, _, job, replay_job, h2, v3, v3_sha, replay, replay_sha, rs, rs_sha = fixture
        with mock.patch.object(combined, "ROOT", root), \
             mock.patch.object(combined, "SUB", root / "artifacts/submission_h2"):
            return combined.validate_combined_submission(
                sub, job_id=job, replay_job=replay_job, h2_sha=h2,
                v3_path=v3, v3_sha=v3_sha, replay_path=replay,
                replay_sha=replay_sha, replay_submit=rs,
                replay_submit_sha=rs_sha)

    def test_exact_combined_submission_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); fixture = self.combined_fixture(root)
            self.validate(root, fixture)

    def test_combined_argv_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); fixture = self.combined_fixture(root)
            fixture[1]["argv"].append("--forged")
            write600(fixture[0], json.dumps(fixture[1]))
            with self.assertRaisesRegex(ValueError, "argv"):
                self.validate(root, fixture)

    def test_combined_readback_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); fixture = self.combined_fixture(root)
            fixture[1]["scontrol_readback"] = "forged"
            write600(fixture[0], json.dumps(fixture[1]))
            with self.assertRaisesRegex(ValueError, "readback"):
                self.validate(root, fixture)


class RuntimeAndHeterogeneityTests(unittest.TestCase):
    def test_host_python_below_310_rejected(self):
        with mock.patch.object(runtime, "sha", return_value=runtime.CONTAINER_SHA256):
            with self.assertRaisesRegex(ValueError, "host Python"):
                runtime.build("replay", "9000", "3.9.99", Path("/container"))

    def test_fixed_container_runtime_passes(self):
        with mock.patch.object(runtime, "sha", return_value=runtime.CONTAINER_SHA256), \
             mock.patch.object(runtime.platform, "python_version", return_value="3.11.8"):
            value = runtime.build("replay", "9000", "3.10.1", Path("/container"))
            self.assertEqual(value["status"], "PASS_FIXED_CONTAINER_PYTHON_GE_3_10")

    def test_pack_diagnostic_is_deterministic(self):
        rng = np.random.Generator(np.random.PCG64(5))
        a3 = rng.normal(0, 0.01, (32, 75)); a4 = rng.normal(0, 0.01, (128, 75))
        contract = {
            "surface_method": {"resamples": 250, "seed": 7,
                               "critical_order_statistic_one_indexed": 238},
            "compatibility_band_absolute_probability": 0.002,
            "primary_contrast": {"target2_x": 32, "target2_y": 24,
                                 "amplitude_high": 0.2},
            "estimand": "test",
            "decision_rule": {"pooling_policy": "test"},
        }
        with mock.patch.object(combined.science, "sha", return_value=HEX):
            left = combined.pack_heterogeneity(a3, a4, contract)
            right = combined.pack_heterogeneity(a3, a4, contract)
        self.assertEqual(science.canonical_digest(left),
                         science.canonical_digest(right))


if __name__ == "__main__":
    unittest.main()
