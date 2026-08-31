#!/usr/bin/env python3
"""Killing tests for the H6 exact candidate-byte terminal boundary."""
from __future__ import annotations

import concurrent.futures
import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import build_isambard_ai_v4_r2_h6_payload as build_h6
import provision_gpu_gating_v4_r2_h5 as provision
import terminal_audit_gpu_gating_v4_r2_h5 as h5
import terminal_audit_gpu_gating_v4_r2_h6 as terminal
import test_isambard_ai_gating_v4_r2_h5 as fixtures

HEX = fixtures.HEX
JOBS = fixtures.JOBS


def full_tree() -> dict:
    value = fixtures.full_tree()
    value["primary"]["combined"]["statistics"]["label"] = "caf\u00e9"
    return value


def candidate(expected_full: dict) -> dict:
    return provision.candidate_payload(
        expected_full, h5_sha=HEX, h4_sha=HEX)


class RealCandidateFileMixin:
    def write_discover_validate(self, raw: bytes, expected_full: dict) -> None:
        digest = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as temporary, \
             mock.patch.object(provision, "ROOT", Path(temporary)):
            path = provision.candidate_path(
                digest=digest, array_job=JOBS["array"],
                reducer_job=JOBS["reducer"], replay_job=JOBS["replay"],
                combined_job=JOBS["combined"], release_job=JOBS["release"])
            path.parent.mkdir(parents=True, mode=0o700)
            path.write_bytes(raw)
            os.chmod(path, 0o600)
            discovered_path, discovered_sha, parsed = terminal.discover_candidate(
                array_job=JOBS["array"], reducer_job=JOBS["reducer"],
                replay_job=JOBS["replay"], combined_job=JOBS["combined"],
                release_job=JOBS["release"])
            self.assertEqual((discovered_path, discovered_sha), (path, digest))
            terminal.validate_candidate(
                parsed, candidate_path=discovered_path,
                candidate_sha=discovered_sha, expected_full=expected_full,
                h5_sha=HEX, h4_sha=HEX)


class CandidateCanonicalByteKillingTests(
        RealCandidateFileMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.expected_full = full_tree()
        self.payload = candidate(self.expected_full)
        self.canonical = provision.canonical_bytes(self.payload)

    def assert_rehashed_representation_rejected(self, raw: bytes) -> None:
        self.assertNotEqual(raw, self.canonical)
        with self.assertRaisesRegex(ValueError, "raw canonical-byte drift"):
            self.write_discover_validate(raw, self.expected_full)

    def test_real_canonical_file_discover_validate_passes(self):
        self.write_discover_validate(self.canonical, self.expected_full)

    def test_real_extra_newline_rehashed_file_rejected(self):
        self.assert_rehashed_representation_rejected(self.canonical + b"\n")

    def test_real_space_rehashed_file_rejected(self):
        self.assert_rehashed_representation_rejected(
            self.canonical.replace(b"{\n", b"{ \n", 1))

    def test_real_key_order_rehashed_file_rejected(self):
        raw = (json.dumps(
            self.payload, indent=2, sort_keys=False, ensure_ascii=True,
            allow_nan=False) + "\n").encode()
        self.assert_rehashed_representation_rejected(raw)

    def test_real_utf8_representation_rehashed_file_rejected(self):
        raw = (json.dumps(
            self.payload, indent=2, sort_keys=True, ensure_ascii=False,
            allow_nan=False) + "\n").encode("utf-8")
        self.assertIn("caf\u00e9".encode("utf-8"), raw)
        self.assert_rehashed_representation_rejected(raw)

    def test_semantic_validation_precedes_raw_byte_gate(self):
        forged = copy.deepcopy(candidate(self.expected_full))
        forged["full_recomputation"]["primary"]["combined"]["statistics"][
            "mean"] += 5e-16
        raw = provision.canonical_bytes(forged)
        with self.assertRaisesRegex(ValueError, "exact tree drift"):
            self.write_discover_validate(raw, self.expected_full)


class FrozenBoundaryTests(unittest.TestCase):
    def test_h6_reuses_exact_h5_terminal_scheduler_and_receipt_gates(self):
        self.assertIs(terminal.terminal_gate, h5.terminal_gate)
        self.assertIs(terminal.ensure_terminal_receipt,
                      h5.ensure_terminal_receipt)
        decision, row = terminal.terminal_gate(
            fixtures.sacct_text(fixtures.sacct_row()),
            release_job=JOBS["release"], submission=fixtures.submission())
        self.assertEqual((decision, row["State"]), ("PASS", "COMPLETED"))

    def test_h6_failed_terminal_never_discovers_candidate(self):
        failed = fixtures.sacct_text(fixtures.sacct_row("FAILED", "1:0"))
        with mock.patch.object(terminal.science, "sha", return_value=HEX), \
             mock.patch.object(provision, "validate_release_submission",
                               return_value=fixtures.submission()), \
             mock.patch.object(terminal, "discover_candidate") as discover:
            with self.assertRaisesRegex(ValueError, "terminal failure"):
                terminal.audit(
                    h6_sha=HEX, h5_sha=HEX, h4_sha=HEX,
                    array_job=JOBS["array"], reducer_job=JOBS["reducer"],
                    replay_job=JOBS["replay"], combined_job=JOBS["combined"],
                    release_job=JOBS["release"], v3_sha=HEX, replay_sha=HEX,
                    replay_submit_sha=HEX, combined_submit_sha=HEX,
                    combined_json_sha=HEX, combined_csv_sha=HEX,
                    query=lambda _job: failed)
            discover.assert_not_called()

    def test_h6_controller_is_single_shot_no_poll_zero_node_hours(self):
        text = Path(terminal.__file__).read_text()
        self.assertNotIn("time.sleep", text)
        self.assertEqual(text.count("query(release_job)"), 1)
        self.assertIn("provision.full_recomputation(", text)
        record = terminal.controller_record()
        self.assertEqual(record["slurm_node_hours"], 0.0)
        self.assertFalse(record["submits_slurm_job"])
        self.assertEqual(record["walltime_limit_seconds"], 1800)

    def test_h6_final_o_excl_concurrent_divergence_allows_one(self):
        variants = ({
            "jobs": dict(JOBS),
            "release_terminal_receipt": {"sha256": HEX},
            "stable": stable,
        } for stable in (True, False))
        with tempfile.TemporaryDirectory() as temporary, \
             mock.patch.object(terminal, "ROOT", Path(temporary)), \
             concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(terminal.write_final, item)
                       for item in variants]
            outcomes = []
            for future in futures:
                try:
                    outcomes.append(("pass", future.result()))
                except ValueError as error:
                    outcomes.append(("reject", str(error)))
            self.assertEqual([kind for kind, _ in outcomes].count("pass"), 1)
            self.assertEqual([kind for kind, _ in outcomes].count("reject"), 1)
            self.assertEqual(len(list(
                terminal.final_dir(JOBS).glob(
                    "final-terminal-*-authority-*.json"))), 1)

    def test_h6_payload_members_are_append_only_over_frozen_h5(self):
        self.assertEqual(build_h6.h5.verify(), build_h6.H5_PAYLOAD_SHA256)
        self.assertEqual(len(build_h6.MEMBERS), len(set(build_h6.MEMBERS)))
        self.assertTrue(set(build_h6.h5.MEMBERS).issubset(build_h6.MEMBERS))
        self.assertTrue(all("h6" in member or member.endswith(
            "isambard_ai_v4_r2_h5_payload.sha256")
            for member in build_h6.H6_MEMBERS))


if __name__ == "__main__":
    unittest.main()
