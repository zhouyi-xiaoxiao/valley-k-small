#!/usr/bin/env python3
"""Fail-closed mutation tests for the map/cut/killing contract validator."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
ARTIFACT = REPORT / "artifacts/data/continuum_c2_source_bound_map_cut_killing_contract_v1.json"
VALIDATOR = REPORT / "code/validate_continuum_c2_source_bound_map_cut_killing_contract_v1.py"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--artifact", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )


class SourceBoundContractMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = ARTIFACT.read_bytes()
        cls.payload = json.loads(cls.raw.decode("ascii"))

    def test_unmodified_baseline_passes_before_mutations(self) -> None:
        result = run_validator(ARTIFACT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS independent source/geometry", result.stdout)
        self.assertIn(
            f"validated_snapshot_sha256={hashlib.sha256(self.raw).hexdigest()}",
            result.stdout,
        )
        self.assertNotIn("Traceback", result.stderr)

    def assert_semantic_mutation_rejected(
        self,
        mutate: Callable[[dict[str, Any]], None],
    ) -> None:
        payload = copy.deepcopy(self.payload)
        mutate(payload)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.json"
            path.write_bytes(canonical(payload))
            result = run_validator(path)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ERROR ContractError:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("PASS independent", result.stdout)

    def test_promotion_and_scope_mutations_are_rejected(self) -> None:
        mutations: list[Callable[[dict[str, Any]], None]] = [
            lambda p: p["claim_boundary"].__setitem__("complete_C2", True),
            lambda p: p["claim_boundary"].__setitem__(
                "production_same_member_bridge_accepted", True
            ),
            lambda p: p["claim_boundary"].__setitem__(
                "production_n0_correlated_containment_receipt_present", True
            ),
            lambda p: p["claim_boundary"].__setitem__(
                "numerical_theorem_constants_evaluated", True
            ),
            lambda p: p["claim_boundary"].__setitem__("release_eligible", True),
            lambda p: p["symbolic_theorem_contract"]["round9_residual"].__setitem__(
                "budget_factor_selected", True
            ),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.assert_semantic_mutation_rejected(mutate)

    def test_mathematical_contract_mutations_are_rejected(self) -> None:
        def remove_delta_less_a(payload: dict[str, Any]) -> None:
            payload["symbolic_theorem_contract"]["cut_layer"]["tube_area_hypotheses"].remove(
                "delta<a"
            )

        def weaken_cut_exponent(payload: dict[str, Any]) -> None:
            payload["symbolic_theorem_contract"]["cut_layer"]["weighted_cut_bound"] = (
                "norm_Vh_minus_V_L2_pi<=C_V_cut*h+(L_Psi/W)*h"
            )

        mutations: list[Callable[[dict[str, Any]], None]] = [
            remove_delta_less_a,
            weaken_cut_exponent,
            lambda p: p["symbolic_theorem_contract"]["cut_layer"].__setitem__(
                "sharp_indicator_derivative_used", True
            ),
            lambda p: p["symbolic_theorem_contract"]["contact_profile"].__setitem__(
                "w_normalization_present", False
            ),
            lambda p: p["symbolic_theorem_contract"]["rho"].__setitem__(
                "physical_cell_mass_not_representative_mass", False
            ),
            lambda p: p["symbolic_theorem_contract"]["killing_multiplier"].__setitem__(
                "definition", "K_h_pc=V_h_pc"
            ),
            lambda p: p["symbolic_theorem_contract"]["map"].__setitem__(
                "exact_adjoint", "P_h_not_equal_J_h_star"
            ),
            lambda p: p["symbolic_theorem_contract"]["symbolic_constant_definitions"].__setitem__(
                "C_P", "C_av+Lambda_star*exp(Lambda_star*H_star)"
            ),
            lambda p: p["family_scope"].__setitem__("common_sufficient_tail_start_n", -1),
            lambda p: p["geometry_rows"][0].__setitem__("torus_cut_locus_margin_exact", "0/1"),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.assert_semantic_mutation_rejected(mutate)

    def test_unknown_key_and_bool_integer_confusion_are_rejected(self) -> None:
        mutations: list[Callable[[dict[str, Any]], None]] = [
            lambda p: p["symbolic_theorem_contract"]["cut_layer"].__setitem__("complete_C2", True),
            lambda p: p["family_scope"].__setitem__("common_sufficient_tail_start_n", False),
            lambda p: p["claim_boundary"].__setitem__("complete_C2", 0),
            lambda p: p["validation_scope"].__setitem__(
                "validator_is_independent_numerical_backend", True
            ),
            lambda p: p["build_provenance"].__setitem__(
                "executed_builder_bytes_authenticated", True
            ),
            lambda p: p["source_inventory"]["successor_theory_note"].__setitem__(
                "sha256", "0" * 64
            ),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.assert_semantic_mutation_rejected(mutate)

    def test_float_duplicate_and_noncanonical_json_are_rejected(self) -> None:
        malformed: list[bytes] = []
        text = self.raw.decode("ascii")
        malformed.append(
            text.replace(
                '"common_sufficient_tail_start_n": 0',
                '"common_sufficient_tail_start_n": 0.5',
                1,
            ).encode("ascii")
        )
        malformed.append(
            text.replace(
                '"schema": "encounter_continuum_c2_source_bound_map_cut_killing_contract_v1",',
                '"schema": "encounter_continuum_c2_source_bound_map_cut_killing_contract_v1",\n'
                '  "schema": "encounter_continuum_c2_source_bound_map_cut_killing_contract_v1",',
                1,
            ).encode("ascii")
        )
        malformed.append(self.raw.rstrip(b"\n"))
        for raw in malformed:
            with self.subTest(prefix=raw[:40]):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "malformed.json"
                    path.write_bytes(raw)
                    result = run_validator(path)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("ERROR ContractError:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
