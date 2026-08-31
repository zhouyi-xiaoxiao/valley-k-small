#!/usr/bin/env python3
"""Killing tests for H4 canonical-path and semantic release authority."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

import analyze_gpu_gating_v4_r2_combined_h4 as combined_h4
import finalize_gpu_gating_v4_r2_h4 as final_h4
import runtime_probe_v4_r2_h4 as runtime_h4


HEX = "a" * 64


class CombinedFixture:
    def __init__(self) -> None:
        self.array = "1001"; self.reducer = "1002"
        self.replay = "1003"; self.combined_job = "1004"
        self.json_path, self.csv_path = combined_h4.combined_paths(
            self.replay, self.combined_job)
        self.authorization = {
            "h4_payload_manifest_sha256": HEX,
            "v3_release_receipt_path": str(combined_h4.v3_release_path()),
            "v3_release_receipt_sha256": HEX,
            "v4_replay_receipt_path": str(
                combined_h4.replay_receipt_path(self.reducer)),
            "v4_replay_receipt_sha256": HEX,
            "replay_submission_receipt_path": str(
                combined_h4.submission_path("replay")),
            "replay_submission_receipt_sha256": HEX,
            "v3_primary_raw_replay_status": "PASS_PRIMARY_ROPE_EVIDENCE",
            "v3_primary_raw_replay_digest": "b" * 64,
            "v4_primary_raw_replay_status": "PASS_PRIMARY_ROPE_EVIDENCE",
            "v4_primary_raw_replay_digest": "c" * 64,
            "v3_reduction_csv_path": "/fixed/v3/reduction.csv",
            "v3_reduction_csv_sha256": "d" * 64,
            "v4_reduction_csv_path": "/fixed/v4/reduction.csv",
            "v4_reduction_csv_sha256": "e" * 64,
            "array_job_id": self.array, "reducer_job_id": self.reducer,
            "replay_job_id": self.replay,
            "combined_job_id": self.combined_job,
        }
        self.submission = {
            "combined_job_id": self.combined_job,
            "combined_submission_receipt_path": str(
                combined_h4.submission_path("combined")),
            "combined_submission_receipt_sha256": "f" * 64,
            "replay_job_id": self.replay,
            "replay_submission_receipt_path": str(
                combined_h4.submission_path("replay")),
            "replay_submission_receipt_sha256": HEX,
            "script": {"path": "code/fixed.sbatch", "sha256": HEX},
            "argv": ["sbatch", "--parsable", "fixed"],
            "scontrol_readback_sha256": HEX,
        }
        self.runtime = {
            "path": str(combined_h4.runtime_path("combined", self.combined_job)),
            "sha256": HEX,
            "receipt": self.runtime_receipt("combined", self.combined_job),
        }
        self.primary = {
            "v3_only": {"mean": 0.01}, "v4_only": {"mean": 0.02},
            "combined": {
                "statistics": {"mean": 0.018, "standard_error": 0.001},
                "rope": {"lower": -0.002, "upper": 0.002},
                "decision": "positive_change",
            },
        }
        self.surface = {
            "v3_only": {"rows": [{"mean_effect": 0.01}]},
            "v4_only": {"rows": [{"mean_effect": 0.02}]},
            "combined": {"rows": [{"mean_effect": 0.018}]},
        }
        self.heterogeneity = {
            "status": "PASS_NO_MATERIAL_PACK_HETEROGENEITY_DETECTED",
            "primary": {"ci_lower": -0.001, "ci_upper": 0.001},
            "flagged_contrast_indices": [],
        }
        self.csv = {
            "path": str(self.csv_path), "filename": self.csv_path.name,
            "sha256": HEX, "rows": 75, "fieldnames": ["mean_effect"],
        }
        self.combined = {
            "schema": combined_h4.COMBINED_SCHEMA,
            "status": combined_h4.COMBINED_STATUS,
            "authorization": copy.deepcopy(self.authorization),
            "submission_binding": copy.deepcopy(self.submission),
            "runtime_binding": copy.deepcopy(self.runtime),
            "primary": copy.deepcopy(self.primary),
            "surface": copy.deepcopy(self.surface),
            "pack_heterogeneity": copy.deepcopy(self.heterogeneity),
            "csv": copy.deepcopy(self.csv),
            "authorizes_scientific_release": False,
        }

    @staticmethod
    def runtime_receipt(phase: str, job_id: str) -> dict:
        return {
            "schema": runtime_h4.SCHEMA, "status": runtime_h4.STATUS,
            "phase": phase, "slurm_job_id": job_id,
            "host_python": {
                "module": runtime_h4.HOST_MODULE,
                "version": runtime_h4.HOST_VERSION,
                "executable": "/opt/cray/pe/python/3.11.7/bin/python3",
                "loaded_modules_exact_contains_pin": True,
            },
            "container_python": {
                "version": runtime_h4.CONTAINER_VERSION,
                "implementation": runtime_h4.CONTAINER_IMPLEMENTATION,
                "executable": "/usr/local/bin/python3",
            },
            "container": {
                "path": str(runtime_h4.CONTAINER_PATH),
                "sha256": runtime_h4.CONTAINER_SHA256,
            },
        }

    def check(self, value: dict, *, json_path: Path | None = None) -> None:
        final_h4.validate_combined_payload(
            value, combined_path=json_path or self.json_path,
            csv_path=self.csv_path, replay_job=self.replay,
            combined_job=self.combined_job,
            expected_authorization=self.authorization,
            expected_submission=self.submission,
            expected_runtime=self.runtime, expected_primary=self.primary,
            expected_surface=self.surface,
            expected_heterogeneity=self.heterogeneity,
            expected_csv=self.csv,
        )


class H4CanonicalAndSemanticKillingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = CombinedFixture()

    def test_exact_fixture_passes(self):
        self.fx.check(copy.deepcopy(self.fx.combined))

    def test_arbitrary_combined_path_rejected(self):
        with self.assertRaisesRegex(ValueError, "not canonical"):
            self.fx.check(copy.deepcopy(self.fx.combined),
                          json_path=Path("/tmp/attacker/forged.json"))

    def test_deleted_authorization_rejected(self):
        forged = copy.deepcopy(self.fx.combined); del forged["authorization"]
        with self.assertRaisesRegex(ValueError, "exact schema"):
            self.fx.check(forged)

    def test_deleted_primary_rejected(self):
        forged = copy.deepcopy(self.fx.combined); del forged["primary"]
        with self.assertRaisesRegex(ValueError, "exact schema"):
            self.fx.check(forged)

    def test_deleted_surface_rejected(self):
        forged = copy.deepcopy(self.fx.combined); del forged["surface"]
        with self.assertRaisesRegex(ValueError, "exact schema"):
            self.fx.check(forged)

    def test_extra_combined_key_rejected(self):
        forged = copy.deepcopy(self.fx.combined); forged["looks_harmless"] = True
        with self.assertRaisesRegex(ValueError, "exact schema"):
            self.fx.check(forged)

    def test_rope_mutation_rejected(self):
        forged = copy.deepcopy(self.fx.combined)
        forged["primary"]["combined"]["rope"]["upper"] = 0.2
        with self.assertRaisesRegex(ValueError, "rope.upper"):
            self.fx.check(forged)

    def test_primary_statistics_mutation_rejected(self):
        forged = copy.deepcopy(self.fx.combined)
        forged["primary"]["combined"]["statistics"]["mean"] = -0.5
        with self.assertRaisesRegex(ValueError, "statistics.mean"):
            self.fx.check(forged)

    def test_raw_primary_digest_mutation_rejected(self):
        forged = copy.deepcopy(self.fx.combined)
        forged["authorization"]["v4_primary_raw_replay_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "raw_replay_digest"):
            self.fx.check(forged)

    def test_heterogeneity_mutation_rejected(self):
        forged = copy.deepcopy(self.fx.combined)
        forged["pack_heterogeneity"]["status"] = "PASS_FORGED"
        with self.assertRaisesRegex(ValueError, "pack_heterogeneity.status"):
            self.fx.check(forged)

    def test_csv_path_mutation_rejected(self):
        forged = copy.deepcopy(self.fx.combined)
        forged["csv"]["path"] = "/tmp/attacker/combined.csv"
        with self.assertRaisesRegex(ValueError, "combined.csv.path"):
            self.fx.check(forged)

    def test_deleted_csv_path_rejected(self):
        forged = copy.deepcopy(self.fx.combined); del forged["csv"]["path"]
        with self.assertRaisesRegex(ValueError, "CSV exact-key"):
            self.fx.check(forged)

    def test_synchronized_combined_sha_and_release_receipt_attack_rejected(self):
        forged = copy.deepcopy(self.fx.combined)
        forged["primary"]["combined"]["statistics"]["mean"] = -99.0
        forged_bytes = json.dumps(forged, sort_keys=True).encode()
        forged_sha = hashlib.sha256(forged_bytes).hexdigest()
        forged_release_receipt = {
            "phase_inputs": {"combined_json_sha256": forged_sha},
            "authorities": {"combined_json": {
                "path": str(self.fx.json_path), "sha256": forged_sha,
            }},
        }
        self.assertEqual(
            forged_release_receipt["phase_inputs"]["combined_json_sha256"],
            forged_release_receipt["authorities"]["combined_json"]["sha256"],
        )
        with self.assertRaisesRegex(ValueError, "statistics.mean"):
            self.fx.check(forged)


class H4RuntimeKillingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = CombinedFixture.runtime_receipt("release", "2001")

    def test_exact_runtime_passes(self):
        runtime_h4.validate(copy.deepcopy(self.value), phase="release", job_id="2001")

    def assert_mutation_fails(self, mutate, pattern):
        forged = copy.deepcopy(self.value); mutate(forged)
        with self.assertRaisesRegex(ValueError, pattern):
            runtime_h4.validate(forged, phase="release", job_id="2001")

    def test_host_version_mutation_rejected(self):
        self.assert_mutation_fails(
            lambda x: x["host_python"].__setitem__("version", "3.6.15"),
            "host Python")

    def test_host_module_mutation_rejected(self):
        self.assert_mutation_fails(
            lambda x: x["host_python"].__setitem__("module", "cray-python/3.10"),
            "host Python")

    def test_sif_python_mutation_rejected(self):
        self.assert_mutation_fails(
            lambda x: x["container_python"].__setitem__("version", "3.11.9"),
            "SIF Python")

    def test_sif_path_mutation_rejected(self):
        self.assert_mutation_fails(
            lambda x: x["container"].__setitem__("path", "/tmp/forged.sif"),
            "SIF path/SHA")

    def test_sif_sha_mutation_rejected(self):
        self.assert_mutation_fails(
            lambda x: x["container"].__setitem__("sha256", "0" * 64),
            "SIF path/SHA")

    def test_phase_mutation_rejected(self):
        self.assert_mutation_fails(
            lambda x: x.__setitem__("phase", "combined"), "envelope")

    def test_slurm_job_mutation_rejected(self):
        self.assert_mutation_fails(
            lambda x: x.__setitem__("slurm_job_id", "9999"), "envelope")


class H4StaticClosureTests(unittest.TestCase):
    def test_every_h4_sbatch_has_exact_runtime_pin(self):
        code = Path(__file__).resolve().parent
        scripts = sorted(code.glob("isambard_ai_gating_v4_r2_*_h4.sbatch"))
        self.assertEqual(len(scripts), 7)
        for path in scripts:
            text = path.read_text(encoding="utf-8")
            self.assertIn("module load cray-python/3.11.7", text, path.name)
            self.assertIn("runtime_probe_v4_r2_h4.py", text, path.name)
            self.assertIn("--host-python-executable", text, path.name)
            self.assertIn("--loaded-modules", text, path.name)
            self.assertIn("apptainer exec", text, path.name)

    def test_release_derives_canonical_paths_and_never_accepts_them_as_argv(self):
        code = Path(__file__).resolve().parent
        text = (code / "isambard_ai_gating_v4_r2_release_h4.sbatch").read_text()
        self.assertIn("combined_h4/replay-$REPLAY_JOB-combined-$COMBINED_JOB", text)
        self.assertNotIn('COMBINED_JSON="$3"', text)
        self.assertNotIn('COMBINED_CSV="$5"', text)
        finalizer = (code / "finalize_gpu_gating_v4_r2_h4.py").read_text()
        self.assertNotIn('add_argument("--combined-json"', finalizer)
        self.assertNotIn('add_argument("--combined-csv"', finalizer)

    def test_combined_analyzer_has_exact_top_and_authorization_keys(self):
        self.assertEqual(len(combined_h4.COMBINED_KEYS), 10)
        self.assertEqual(len(combined_h4.AUTHORIZATION_KEYS), 19)
        self.assertIn("primary", combined_h4.COMBINED_KEYS)
        self.assertIn("surface", combined_h4.COMBINED_KEYS)
        self.assertIn("v4_primary_raw_replay_digest",
                      combined_h4.AUTHORIZATION_KEYS)


if __name__ == "__main__":
    unittest.main()
