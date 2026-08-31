#!/usr/bin/env python3
"""Killing tests for the H5 post-release terminal authority boundary."""
from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import provision_gpu_gating_v4_r2_h5 as provision
import runtime_probe_v4_r2_h5 as runtime_h5
import submit_isambard_ai_gating_v4_r2_h5 as submit_h5
import terminal_audit_gpu_gating_v4_r2_h5 as terminal

HEX = "a" * 64
JOBS = {
    "array": "1001", "reducer": "1002", "replay": "1003",
    "combined": "1004", "release": "1005",
}


def submission() -> dict:
    return {"submit_line": "sbatch --parsable --dependency=afterok:1004 fixed"}


def sacct_row(state: str = "COMPLETED", exit_code: str = "0:0") -> dict[str, str]:
    return {
        "JobIDRaw": JOBS["release"], "JobID": JOBS["release"],
        "JobName": terminal.RELEASE_JOB_NAME, "Account": terminal.ACCOUNT,
        "Partition": terminal.PARTITION, "State": state,
        "ExitCode": exit_code, "ElapsedRaw": "61",
        "AllocTRES": "billing=32,cpu=32,mem=128G,node=1",
        "ReqTRES": "billing=32,cpu=32,mem=128G,node=1",
        "NNodes": "1", "WorkDir": str(terminal.ROOT),
        "SubmitLine": submission()["submit_line"],
    }


def sacct_text(row: dict[str, str]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=terminal.SACCT_FIELDS, delimiter="|",
        lineterminator="\n")
    writer.writeheader(); writer.writerow(row)
    return buffer.getvalue()


def full_tree() -> dict:
    value = {key: {} for key in provision.FULL_KEYS}
    value.update({
        "schema": provision.FULL_SCHEMA, "status": provision.FULL_STATUS,
        "h5_payload_manifest_sha256": HEX,
        "h4_payload_manifest_sha256": HEX,
        "jobs": dict(JOBS),
        "authorization": {"v4_primary_raw_replay_digest": "b" * 64},
        "primary": {"combined": {
            "statistics": {"mean": 0.01},
            "rope": {"lower": -0.002, "upper": 0.002},
        }},
        "surface": {"combined": {"rows": [{"mean_effect": 0.01}]}},
        "pack_heterogeneity": {"status": "PASS_NO_MATERIAL_PACK_HETEROGENEITY_DETECTED"},
        "authorizes_scientific_release": False,
    })
    return value


def candidate() -> dict:
    return {
        "schema": provision.CANDIDATE_SCHEMA,
        "status": provision.CANDIDATE_STATUS,
        "h5_payload_manifest_sha256": HEX,
        "h4_payload_manifest_sha256": HEX,
        "jobs": dict(JOBS), "full_recomputation": full_tree(),
        "candidate_writer": provision.provision_script_record(),
        "authorizes_scientific_release": False,
    }


class ReleaseTerminalStateKillingTests(unittest.TestCase):
    def gate(self, state: str, exit_code: str = "0:0"):
        return terminal.terminal_gate(
            sacct_text(sacct_row(state, exit_code)),
            release_job=JOBS["release"], submission=submission())

    def test_pending_is_canonical_wait(self):
        decision, row = self.gate("PENDING")
        self.assertEqual((decision, row["State"]), ("WAIT", "PENDING"))

    def test_running_is_canonical_wait(self):
        decision, row = self.gate("RUNNING")
        self.assertEqual((decision, row["State"]), ("WAIT", "RUNNING"))

    def test_exact_completed_parent_passes(self):
        decision, row = self.gate("COMPLETED")
        self.assertEqual(decision, "PASS")
        self.assertEqual(row["ExitCode"], "0:0")

    def test_terminal_failure_states_rejected(self):
        for state in (
            "FAILED", "TIMEOUT", "NODE_FAIL", "OUT_OF_MEMORY", "OOM",
            "CANCELLED", "CANCELLED by 1234",
        ):
            with self.subTest(state=state), self.assertRaisesRegex(
                    ValueError, "terminal failure"):
                self.gate(state, "1:0")

    def test_completed_nonzero_rejected(self):
        with self.assertRaisesRegex(ValueError, "not exact terminal"):
            self.gate("COMPLETED", "1:0")

    def test_candidate_already_exists_but_terminal_failed_never_read(self):
        failed = sacct_text(sacct_row("FAILED", "1:0"))
        with mock.patch.object(terminal.science, "sha", return_value=HEX), \
             mock.patch.object(provision, "validate_release_submission",
                               return_value=submission()), \
             mock.patch.object(terminal, "discover_candidate") as discover:
            with self.assertRaisesRegex(ValueError, "terminal failure"):
                terminal.audit(
                    h5_sha=HEX, h4_sha=HEX, array_job=JOBS["array"],
                    reducer_job=JOBS["reducer"], replay_job=JOBS["replay"],
                    combined_job=JOBS["combined"], release_job=JOBS["release"],
                    v3_sha=HEX, replay_sha=HEX, replay_submit_sha=HEX,
                    combined_submit_sha=HEX, combined_json_sha=HEX,
                    combined_csv_sha=HEX, query=lambda _job: failed)
            discover.assert_not_called()


class SacctIdentityKillingTests(unittest.TestCase):
    def reject(self, field: str, value: str, pattern: str):
        row = sacct_row(); row[field] = value
        with self.assertRaisesRegex(ValueError, pattern):
            terminal.terminal_gate(
                sacct_text(row), release_job=JOBS["release"],
                submission=submission())

    def test_wrong_job_rejected(self):
        self.reject("JobIDRaw", "9999", "wrong job")

    def test_wrong_script_job_name_rejected(self):
        self.reject("JobName", "forged-release", "job/account/partition")

    def test_wrong_account_rejected(self):
        self.reject("Account", "other", "job/account/partition")

    def test_wrong_partition_rejected(self):
        self.reject("Partition", "debug", "job/account/partition")

    def test_wrong_workdir_rejected(self):
        self.reject("WorkDir", "/tmp/forged", "WorkDir")

    def test_wrong_submit_line_rejected(self):
        self.reject("SubmitLine", "sbatch forged.sbatch", "SubmitLine")

    def test_wrong_terminal_resource_fields_rejected(self):
        mutations = (
            ("AllocTRES", "billing=32,cpu=16,mem=128G,node=1", "TRES"),
            ("AllocTRES", "billing=32,cpu=32,mem=128G,node=1,gres/gpu=1", "TRES"),
            ("ElapsedRaw", "0", "elapsed/node"),
            ("NNodes", "2", "elapsed/node"),
        )
        for field, value, pattern in mutations:
            with self.subTest(field=field, value=value):
                self.reject(field, value, pattern)

    def test_wrong_req_tres_rejected(self):
        self.reject("ReqTRES", "cpu=32,mem=64G,node=1", "TRES")

    def test_duplicate_parent_row_rejected(self):
        raw = sacct_text(sacct_row()) + sacct_text(sacct_row()).split("\n", 1)[1]
        with self.assertRaisesRegex(ValueError, "parent-row"):
            terminal.terminal_gate(
                raw, release_job=JOBS["release"], submission=submission())


class CandidateAndContentAddressKillingTests(unittest.TestCase):
    def test_exact_false_candidate_passes(self):
        terminal.validate_candidate(
            candidate(), expected_full=full_tree(), h5_sha=HEX, h4_sha=HEX)

    def test_candidate_true_authority_rejected(self):
        forged = candidate(); forged["authorizes_scientific_release"] = True
        with self.assertRaisesRegex(ValueError, "envelope"):
            terminal.validate_candidate(
                forged, expected_full=full_tree(), h5_sha=HEX, h4_sha=HEX)

    def test_modified_candidate_and_rehash_still_rejected(self):
        forged = candidate()
        forged["full_recomputation"]["primary"]["combined"]["statistics"]["mean"] += 5e-16
        forged_sha = hashlib.sha256(
            provision.canonical_bytes(forged)).hexdigest()
        self.assertRegex(forged_sha, r"^[0-9a-f]{64}$")
        with self.assertRaisesRegex(ValueError, "exact tree drift"):
            terminal.validate_candidate(
                forged, expected_full=full_tree(), h5_sha=HEX, h4_sha=HEX)

    def test_candidate_path_contains_all_jobs_and_content_hash(self):
        path = provision.candidate_path(
            digest=HEX, array_job=JOBS["array"], reducer_job=JOBS["reducer"],
            replay_job=JOBS["replay"], combined_job=JOBS["combined"],
            release_job=JOBS["release"])
        for value in JOBS.values():
            self.assertIn(value, str(path))
        self.assertTrue(path.name.endswith(f"{HEX}.json"))

    def test_final_o_excl_repeat_does_not_overwrite(self):
        payload = {
            "jobs": dict(JOBS),
            "release_terminal_receipt": {"sha256": HEX},
            "stable": True,
        }
        with tempfile.TemporaryDirectory() as directory, \
             mock.patch.object(terminal, "ROOT", Path(directory)):
            first, digest, created = terminal.write_final(payload)
            before = first.stat()
            second, digest2, created2 = terminal.write_final(payload)
            after = second.stat()
            self.assertTrue(created); self.assertFalse(created2)
            self.assertEqual((first, digest), (second, digest2))
            self.assertEqual((before.st_ino, before.st_mtime_ns),
                             (after.st_ino, after.st_mtime_ns))
            self.assertIn(f"terminal-{HEX}-authority-{digest}", first.name)
            for value in JOBS.values():
                self.assertIn(value, str(first))

        divergent = ({
            "jobs": dict(JOBS),
            "release_terminal_receipt": {"sha256": HEX},
            "stable": value,
        } for value in (True, False))
        with tempfile.TemporaryDirectory() as directory, \
             mock.patch.object(terminal, "ROOT", Path(directory)), \
             ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(terminal.write_final, item)
                       for item in divergent]
            outcomes = []
            for future in futures:
                try:
                    outcomes.append(("pass", future.result()))
                except ValueError as error:
                    outcomes.append(("reject", str(error)))
            self.assertEqual([kind for kind, _ in outcomes].count("pass"), 1)
            self.assertEqual([kind for kind, _ in outcomes].count("reject"), 1)
            directory_path = terminal.final_dir(JOBS)
            self.assertEqual(
                len(list(directory_path.glob(
                    "final-terminal-*-authority-*.json"))), 1)

    def test_terminal_receipt_repeat_is_idempotent(self):
        row = sacct_row()
        with tempfile.TemporaryDirectory() as directory, \
             mock.patch.object(terminal, "ROOT", Path(directory)):
            first = terminal.ensure_terminal_receipt(
                row, array_job=JOBS["array"], reducer_job=JOBS["reducer"],
                replay_job=JOBS["replay"], combined_job=JOBS["combined"],
                release_job=JOBS["release"])
            before = first[0].stat()
            second = terminal.ensure_terminal_receipt(
                row, array_job=JOBS["array"], reducer_job=JOBS["reducer"],
                replay_job=JOBS["replay"], combined_job=JOBS["combined"],
                release_job=JOBS["release"])
            after = second[0].stat()
            self.assertEqual(first, second)
            self.assertEqual((before.st_ino, before.st_mtime_ns),
                             (after.st_ino, after.st_mtime_ns))


class RuntimeAndDagStaticTests(unittest.TestCase):
    def runtime_receipt(self) -> dict:
        return {
            "schema": runtime_h5.SCHEMA, "status": runtime_h5.STATUS,
            "phase": "release", "slurm_job_id": JOBS["release"],
            "host_python": {
                "module": runtime_h5.HOST_MODULE,
                "version": runtime_h5.HOST_VERSION,
                "executable": "/opt/cray/pe/python/3.11.7/bin/python3",
                "loaded_modules_exact_contains_pin": True,
            },
            "container_python": {
                "version": runtime_h5.CONTAINER_VERSION,
                "implementation": runtime_h5.CONTAINER_IMPLEMENTATION,
                "executable": "/usr/local/bin/python3",
            },
            "container": {"path": str(runtime_h5.CONTAINER_PATH),
                          "sha256": runtime_h5.CONTAINER_SHA256},
        }

    def test_h5_runtime_exact_pass(self):
        runtime_h5.validate(
            self.runtime_receipt(), phase="release", job_id=JOBS["release"])

    def test_h5_runtime_phase_mutation_rejected(self):
        forged = self.runtime_receipt(); forged["phase"] = "combined"
        with self.assertRaisesRegex(ValueError, "envelope"):
            runtime_h5.validate(
                forged, phase="release", job_id=JOBS["release"])

    def test_dag_has_exactly_eight_phases(self):
        self.assertEqual(submit_h5.DAG_PHASES, (
            "v3_authority", "canary", "production", "reducer", "replay",
            "combined", "release", "terminal_audit"))

    def test_terminal_audit_command_is_not_sbatch(self):
        args = mock.Mock(
            h5_payload_sha256=HEX, h4_payload_sha256=HEX,
            array_job=JOBS["array"], reducer_job=JOBS["reducer"],
            replay_job=JOBS["replay"], combined_job=JOBS["combined"],
            release_job=JOBS["release"], v3_release_sha256=HEX,
            v4_replay_sha256=HEX, replay_submission_sha256=HEX,
            combined_submission_sha256=HEX, combined_json_sha256=HEX,
            combined_csv_sha256=HEX)
        command = submit_h5.terminal_command(args)
        self.assertNotIn("sbatch", command)
        self.assertNotIn("--dependency", " ".join(command))

    def test_release_job_only_invokes_false_candidate_writer(self):
        code = Path(__file__).resolve().parent
        sbatch = (code / "isambard_ai_gating_v4_r2_release_h5.sbatch").read_text()
        self.assertIn("provision_gpu_gating_v4_r2_h5.py", sbatch)
        self.assertNotIn("finalize_gpu_gating_v4_r2_h4.py", sbatch)
        self.assertNotIn("terminal_audit_gpu_gating_v4_r2_h5.py", sbatch)
        provision_text = (code / "provision_gpu_gating_v4_r2_h5.py").read_text()
        self.assertNotIn('"authorizes_scientific_release": True', provision_text)

    def test_controller_single_query_no_poll_and_zero_slurm_nhr(self):
        code = Path(__file__).resolve().parent
        text = (code / "terminal_audit_gpu_gating_v4_r2_h5.py").read_text()
        self.assertNotIn("time.sleep", text)
        self.assertEqual(terminal.CONTROLLER_WALLTIME_LIMIT_SECONDS, 1800)
        record = terminal.controller_record()
        self.assertEqual(record["slurm_node_hours"], 0.0)
        self.assertFalse(record["submits_slurm_job"])


if __name__ == "__main__":
    unittest.main()
