#!/usr/bin/env python3
import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

import analyze_gpu_gating_v4_r2_combined_h1 as combined
import independent_replay_gpu_gating_v4_r2_h1 as replay
import submit_isambard_ai_gating_v4_r2_h1 as submit
import verify_v3_release_for_v4_r2_h1 as verify


HEX = "a" * 64


def write600(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text); os.chmod(path, 0o600)


class StrictCanaryTests(unittest.TestCase):
    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.json"; write600(path, '{"a":1,"a":2}\n')
            with self.assertRaises(ValueError): verify.strict_json(path, mode600=True)

    def inventory(self):
        return [{"cell_id": i, "slurm_array_task_id": str(i), "slurm_job_id": str(9000 + i)} for i in range(8)]

    def sacct(self, path: Path, *, state="COMPLETED", omit=None):
        lines = ["JobIDRaw|JobID|State|ExitCode", "5788354|5788354|COMPLETED|0:0"]
        for task in range(8):
            if task == omit: continue
            lines.append(f"{9000+task}|5788354_{task}|{state if task == 3 else 'COMPLETED'}|0:0")
        path.write_text("\n".join(lines) + "\n")

    def test_canary_sacct_exact_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "s.psv"; self.sacct(path)
            self.assertEqual(verify.replay_canary_sacct(path, self.inventory())["allocations"], 8)

    def test_canary_sacct_failed_task_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "s.psv"; self.sacct(path, state="FAILED")
            with self.assertRaises(ValueError): verify.replay_canary_sacct(path, self.inventory())

    def test_canary_sacct_missing_task_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "s.psv"; self.sacct(path, omit=7)
            with self.assertRaises(ValueError): verify.replay_canary_sacct(path, self.inventory())

    def raw_fixture(self, directory: Path, dtype=np.int64):
        npz = directory / "cell-0.npz"
        one = np.array([0, 2, 3], dtype=dtype); two1 = np.array([0, 2, 2], dtype=dtype); two2 = np.array([0, 0, 1], dtype=dtype)
        checks = np.array([[5, 5, 4, 1, 5, 10], [5, 5, 4, 1, 5, 10]], dtype=dtype)
        paired = np.array([[5, 0, 0], [0, 4, 1], [0, 0, 0]], dtype=dtype)
        np.savez_compressed(npz, schema_version=np.asarray(3, dtype=dtype), one_target1_fpt_histogram=one, two_target1_fpt_histogram=two1, two_target2_fpt_histogram=two2, checkpoint_steps=np.array([1, 2], dtype=dtype), checkpoint_counts=checks, paired_outcome_counts=paired); os.chmod(npz, 0o600)
        manifest = {"defaults": {"walkers": 10, "steps": 2, "batch_size": 4, "base_hold": .3, "target_radius": 3, "checkpoints": [1, 2], "start_x": 1, "start_y": 1, "target1_x": 3, "target1_y": 1, "seed_base": 1729}, "artifacts": {"runner_source": {"sha256": "b" * 64}}}
        config = {"cell_id": 0, "amplitude": 0.0, "disorder_replicate": 0, "walk_replicate": 0, "target2_x": 2, "target2_y": 1}
        payload = {key: {} for key in {"domain", "rng", "field", "one_target", "two_targets", "paired_outcomes", "cumulative_counts", "histograms", "gates", "provenance", "runtime"}}
        payload.update({"schema": "grid2d-one-two-target-gating-fixed-mean-gpu-v3", "manifest": {"filename": "gating_v3_canary_manifest.json", "sha256": verify.CANARY_MANIFEST_SHA, "schema": "grid2d-one-two-target-gating-gpu-v3-manifest", "cell_id": 0, "profile": None}, "parameters": {"walkers": 10, "steps": 2, "batch_size": 4, "base_hold": .3, "amplitude": 0.0, "target_radius": 3, "disorder_replicate": 0, "disorder_seed": 4, "walk_replicate": 0, "checkpoints": [1, 2]}, "domain": {"source":"field_pack_contrast_shape","width":4,"height":3,"boundary":"reflecting_attempted_outside_stays","start": {"x": 1, "y": 1}, "target1": {"x": 3, "y": 1}, "target2": {"x": 2, "y": 1},"absorbing_precedence":"target1_then_target2_then_stop"}, "rng": {"algorithm":"torch_generator_device_native","walk_seed": 1729, "walk_seed_origin": "v2_common_random_number_formula","disorder_stride":104729,"walk_stride":1009, "batch_seed_rule": "walk_seed_plus_batch_start", "common_random_numbers": True,"deterministic_for_fixed_manifest_runtime_device":True}, "field": {"pack_filename": "disorder_field_pack_v3.npz", "pack_sha256": "d7039cf68cd137729a3931f1265cad2735c67da3c436fc4f71d214f059f0e420", "expected_pack_sha256": "d7039cf68cd137729a3931f1265cad2735c67da3c436fc4f71d214f059f0e420"}, "one_target": {"target1": {"hits": 5}}, "two_targets": {"target1": {"hits": 4}, "target2": {"hits": 1}}, "histograms": {"format":"npz_compressed_integer_v3","path": npz.name, "sha256": verify.sha(npz), "dtype": "int64","fpt_index_range_inclusive":[0,2],"arrays":{}}, "gates": {"all_passed": True}, "gating_probability_drop": .1, "gating_probability_ratio": None, "target2_first_probability": .1, "provenance": {"source": "gpu_gating_mc_v3.py", "source_sha256": "b" * 64,"argv":[], "slurm": {"SLURM_ARRAY_JOB_ID": "5788354", "SLURM_ARRAY_TASK_ID": "0", "SLURM_JOB_ID": "9000","SLURM_JOB_NAME":None,"SLURM_NODELIST":None,"SLURM_CPUS_PER_TASK":None,"SLURM_JOB_ACCOUNT":None,"SLURM_JOB_PARTITION":None}}})
        path = directory / "cell-0.json"; write600(path, json.dumps(payload))
        inventory = {"slurm_job_id": "9000"}
        return path, npz, manifest, config, inventory

    def test_canary_raw_npz_int64_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.raw_fixture(Path(directory)); verify.replay_canary_raw(*args)

    def test_canary_raw_forged_dtype_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.raw_fixture(Path(directory), np.int32)
            with self.assertRaises(ValueError): verify.replay_canary_raw(*args)


class SubmissionReceiptTests(unittest.TestCase):
    def fixture(self, root: Path):
        sub = root / "artifacts/submission_h1"; script = root / "code/isambard_ai_gating_v4_r2_gpu_canary_h1.sbatch"
        write600(script, "#!/bin/bash\n")
        h1 = "1" * 64; release = "2" * 64; job = "7001"; dependency = "5789031"
        authorities = {"v3_release": {"path": str(root / "artifacts/releases/v3-release-for-v4-r2-h1.json"), "sha256": release}}
        args = [h1, release, authorities["v3_release"]["path"]]
        value = {"schema": replay.SUBMIT_SCHEMA, "status": replay.SUBMIT_STATUS, "phase": "canary", "job_id": job, "dependency_afterok": dependency, "payload_manifest_sha256": h1, "phase_inputs": {"v3_release_sha256": release}, "script": {"path": "code/isambard_ai_gating_v4_r2_gpu_canary_h1.sbatch", "sha256": replay.sha(script)}, "argv": ["sbatch", "--parsable", f"--dependency=afterok:{dependency}", "code/isambard_ai_gating_v4_r2_gpu_canary_h1.sbatch", *args], "authorities": authorities, "scontrol_readback": f"JobId={job} Dependency=afterok:{dependency} Command={script} WorkDir={root}"}
        path = sub / "canary-submission.json"; write600(path, json.dumps(value)); return path, value, h1, release, job, dependency, authorities, args

    def validate(self, root, path, value, h1, release, job, dependency, authorities, args):
        with mock.patch.object(replay, "ROOT", root), mock.patch.object(replay, "SUB", root / "artifacts/submission_h1"):
            return replay.validate_submission(phase="canary", path=path, expected_sha=replay.sha(path), h1_sha=h1, job=job, dependency=dependency, phase_inputs={"v3_release_sha256": release}, authorities=authorities, script_args=args)

    def test_exact_submission_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(Path(directory)); self.validate(Path(directory), *fixture)

    def forged(self, mutate):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path, value, *rest = self.fixture(root); expected = copy.deepcopy(rest); mutate(value); write600(path, json.dumps(value))
            with self.assertRaises(ValueError): self.validate(root, path, value, *expected)

    def test_forged_phase_argv_rejected(self): self.forged(lambda value: value["argv"].append("--forged"))
    def test_forged_authority_rejected(self): self.forged(lambda value: value["authorities"].update({"extra": {"path": "/tmp/x", "sha256": HEX}}))
    def test_forged_script_hash_rejected(self): self.forged(lambda value: value["script"].update({"sha256": HEX}))
    def test_forged_scontrol_rejected(self): self.forged(lambda value: value.update({"scontrol_readback": "forged"}))


class ExtendedSacctTests(unittest.TestCase):
    def inventory(self):
        return [{"cell_id": cell, "slurm_array_task_id": str(cell % 480), "slurm_array_job_id": "8000", "slurm_job_id": str(9000 + cell % 480)} for cell in range(23040)]

    def write(self, path: Path, *, gpu=4, extra=False):
        lines = ["JobIDRaw|JobID|ArrayJobID|ArrayTaskID|State|ExitCode|ElapsedRaw|AllocTRES|ReqTRES|NNodes", "8000|8000|||COMPLETED|0:0|0|||0"]
        for task in range(480): lines.append(f"{9000+task}|8000_{task}|8000|{task}|COMPLETED|0:0|3600|billing=1,gres/gpu={gpu}|billing=1,gres/gpu={gpu}|1")
        if extra: lines.append("99999|foreign||||||||")
        path.write_text("\n".join(lines) + "\n")

    def test_exact_480_fullnode_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"s"; self.write(path); self.assertEqual(replay.replay_sacct(path,"8000",self.inventory())["actual_full_node_nhr"],480.0)

    def test_three_gpu_forgery_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"s"; self.write(path,gpu=3)
            with self.assertRaises(ValueError): replay.replay_sacct(path,"8000",self.inventory())

    def test_extra_sacct_row_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"s"; self.write(path,extra=True)
            with self.assertRaises(ValueError): replay.replay_sacct(path,"8000",self.inventory())


def replay_shape():
    hashes={"reduction_json":"1"*64,"reduction_csv":"2"*64,"sacct_receipt":"3"*64}
    return {"schema":"grid2d-one-two-target-gating-v4-r2-independent-replay-h1","status":"PASS_AUTHORIZE_V3_V4_R2_H1_COMBINED","fixed_root":str(replay.ROOT),"jobs":{"run_token":"8000","array":"8000","reducer":"8001"},"fixed_artifacts":{"manifest_sha256":replay.FIXED["manifest"],"field_pack_sha256":replay.FIXED["field"],"base_payload_sha256":replay.FIXED["base_payload"],"h1_payload_sha256":"4"*64,"container_sha256":replay.FIXED["container"]},"hashes":hashes,"raw":{"exact_tree":{"exact_tree":True,"cell_directories":23040,"files":46080,"tree_digest":"5"*64},"cells":23040,"pairs":23040,"blocks":11520,"raw_inventory_digest":"6"*64,"recomputed_block_digest":"7"*64},"reduction_inventory_digest":"6"*64,"extended_sacct":{"independently_parsed":True,"array_job_id":"8000","parent_rows":1,"tasks":480,"unique_allocations":480,"cells_per_allocation":48,"gpus_per_allocation":4,"nodes_per_allocation":1,"elapsed_raw_total_seconds":1728000,"actual_full_node_nhr":480.0,"receipt_sha256":"3"*64},"submission_chain":{"v3_release_sha256":"8"*64,"canary_job_id":"7000","canary_submission_receipt_sha256":"9"*64,"canary_receipt_sha256":"a"*64,"production_submission_receipt_sha256":"b"*64,"reducer_submission_receipt_sha256":"c"*64}}


class CombinedForgedReceiptTests(unittest.TestCase):
    def test_exact_replay_shape_pass(self): combined.validate_replay_shape(replay_shape(), "4"*64)
    def reject(self, mutate):
        value=replay_shape(); mutate(value)
        with self.assertRaises(ValueError): combined.validate_replay_shape(value,"4"*64)
    def test_forged_status_rejected(self): self.reject(lambda x:x.update(status="PASS"))
    def test_forged_raw_count_rejected(self): self.reject(lambda x:x["raw"].update(cells=1))
    def test_forged_gpu_count_rejected(self): self.reject(lambda x:x["extended_sacct"].update(gpus_per_allocation=3))
    def test_forged_chain_hash_rejected(self): self.reject(lambda x:x["submission_chain"].update(canary_receipt_sha256="bad"))
    def test_extra_top_key_rejected(self): self.reject(lambda x:x.update(forged=True))


if __name__ == "__main__": unittest.main()
