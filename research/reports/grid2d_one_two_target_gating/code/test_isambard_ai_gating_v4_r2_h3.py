#!/usr/bin/env python3
"""P0/P1 killing tests for the append-only H3 authority overlay."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import runtime_probe_v4_r2_h3 as runtime
import scientific_primary_replay_v4_r2_h3 as primary


def parameters(amplitude: float) -> dict:
    return {
        "profile": None, "walkers": 10, "steps": 80000,
        "base_hold": 0.3, "amplitude": amplitude, "target_radius": 3,
        "start_x": 7, "start_y": 24, "target1_x": 54, "target1_y": 24,
        "target2_x": 32, "target2_y": 24,
        "checkpoints": [5000, 10000, 20000, 40000, 80000],
    }


CONTRACT = {"target2_x": 32, "target2_y": 24, "control": 0.0,
            "treatment": 0.2, "rope_half_width": 0.002,
            "confidence_level": 0.95}


class IndependentPrimaryMutationTests(unittest.TestCase):
    def derive(self, effects):
        control = {index: 0.0 for index in range(len(effects))}
        treatment = {index: value for index, value in enumerate(effects)}
        return primary.derive_primary(
            control_blocks=control, treatment_blocks=treatment,
            control_parameters=parameters(0.0),
            treatment_parameters=parameters(0.2), contract=CONTRACT)

    def test_raw_derived_positive_rejects_forged_negative(self):
        expected = self.derive([0.0100, 0.0101])
        self.assertEqual(expected["decision"], "positive_change")
        forged = copy.deepcopy(expected); forged["decision"] = "negative_change"
        with self.assertRaisesRegex(ValueError, "reduction.primary"):
            primary.validate_primary_claim(forged, expected)

    def test_raw_derived_negative_rejects_forged_positive(self):
        expected = self.derive([-0.0100, -0.0101])
        self.assertEqual(expected["decision"], "negative_change")
        forged = copy.deepcopy(expected); forged["decision"] = "positive_change"
        with self.assertRaisesRegex(ValueError, "reduction.primary"):
            primary.validate_primary_claim(forged, expected)

    def test_primary_statistics_mutation_rejected(self):
        expected = self.derive([0.0100, 0.0101])
        forged = copy.deepcopy(expected); forged["statistics"]["mean"] = -0.5
        with self.assertRaisesRegex(ValueError, "statistics.mean"):
            primary.validate_primary_claim(forged, expected)

    def test_rope_mutation_rejected(self):
        expected = self.derive([0.0100, 0.0101])
        forged = copy.deepcopy(expected); forged["rope"]["upper"] = 0.2
        with self.assertRaisesRegex(ValueError, "rope.upper"):
            primary.validate_primary_claim(forged, expected)

    def test_equivalence_and_inconclusive_are_independently_derived(self):
        equivalent = self.derive([0.0001, 0.0001])
        inconclusive = self.derive([-0.003, 0.003])
        self.assertEqual(equivalent["decision"], "practical_equivalence")
        self.assertEqual(inconclusive["decision"], "inconclusive")


class PinnedRuntimeTests(unittest.TestCase):
    def build(self, host_version="3.11.7", modules="cray-python/3.11.7",
              container_version="3.12.11"):
        with mock.patch.object(runtime, "sha", return_value=runtime.CONTAINER_SHA256), \
             mock.patch.object(runtime.platform, "python_version",
                               return_value=container_version):
            return runtime.build(
                phase="replay", job_id="9000",
                host_executable="/opt/cray/pe/python/3.11.7/bin/python3",
                host_version=host_version, loaded_modules=modules,
                container=Path("/fixed.sif"))

    def test_live_default_host_python_3615_rejected(self):
        with self.assertRaisesRegex(ValueError, "pinned cray-python"):
            self.build(host_version="3.6.15", modules="")

    def test_version_without_module_rejected(self):
        with self.assertRaisesRegex(ValueError, "pinned cray-python"):
            self.build(modules="PrgEnv-cray/8.6.0")

    def test_wrong_sif_python_rejected(self):
        with self.assertRaisesRegex(ValueError, "3.12.11"):
            self.build(container_version="3.11.9")

    def test_exact_host_and_sif_runtime_pass(self):
        value = self.build(modules="PrgEnv-cray/8.6.0:cray-python/3.11.7")
        self.assertEqual(value["status"], "PASS_PINNED_HOST_AND_SIF_PYTHON")
        self.assertEqual(value["host_python"]["version"], "3.11.7")
        self.assertEqual(value["container_python"]["version"], "3.12.11")

    def test_every_h3_sbatch_pins_cray_module_and_sif_probe(self):
        code = Path(__file__).resolve().parent
        scripts = sorted(code.glob("isambard_ai_gating_v4_r2_*_h3.sbatch"))
        self.assertEqual(len(scripts), 7)
        for path in scripts:
            text = path.read_text(encoding="utf-8")
            self.assertIn("module load cray-python/3.11.7", text, path.name)
            self.assertIn("runtime_probe_v4_r2_h3.py", text, path.name)
            self.assertIn("--host-python-executable", text, path.name)
            self.assertIn("--loaded-modules", text, path.name)
            self.assertIn("apptainer exec", text, path.name)


if __name__ == "__main__": unittest.main()
