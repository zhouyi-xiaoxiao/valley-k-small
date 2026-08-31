#!/usr/bin/env python3
"""Fail-closed mutation tests for the ideal fixed-box C1 composition."""

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
ARTIFACT = (
    REPORT / "artifacts/data/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.json"
)
VALIDATOR = REPORT / "code/validate_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(VALIDATOR), "--artifact", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )


class IdealFixedBoxC1CompositionMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = ARTIFACT.read_bytes()
        cls.payload = json.loads(cls.raw.decode("ascii"))

    def test_unmodified_baseline_passes_before_mutations(self) -> None:
        result = run_validator(ARTIFACT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_C1_COMPOSITION_INDEPENDENT_SOURCE_GEOMETRY", result.stdout)
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
        self.assertIn("ERROR CompositionContractError:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("PASS_C1_COMPOSITION", result.stdout)

    def test_promotion_mutations_are_rejected(self) -> None:
        mutations: list[Callable[[dict[str, Any]], None]] = [
            lambda p: p["claim_boundary"].__setitem__("complete_C1", True),
            lambda p: p["claim_boundary"].__setitem__("complete_C2", True),
            lambda p: p["claim_boundary"].__setitem__("production_complete_C1", True),
            lambda p: p["claim_boundary"].__setitem__(
                "production_same_member_bridge_accepted", True
            ),
            lambda p: p["claim_boundary"].__setitem__("root_or_topology_transfer_complete", True),
            lambda p: p["claim_boundary"].__setitem__("release_eligible", True),
            lambda p: p["claim_boundary"].__setitem__(
                "numerical_theorem_constants_evaluated", True
            ),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.assert_semantic_mutation_rejected(mutate)

    def test_quantifier_and_same_member_mutations_are_rejected(self) -> None:
        mutations: list[Callable[[dict[str, Any]], None]] = [
            lambda p: p["quantifiers"].__setitem__("sequence_count", 11),
            lambda p: p["quantifiers"].__setitem__("control_range", "for_one_selected_w"),
            lambda p: p["quantifiers"].__setitem__("budget_range", "for_one_positive_B"),
            lambda p: p["quantifiers"].__setitem__("derivative_orders", [0]),
            lambda p: p["single_ideal_member_definition"].__setitem__(
                "same_H_h_used_for_mosco_resolvent_rate_and_observable", False
            ),
            lambda p: p["single_ideal_member_definition"].__setitem__(
                "production_centres_substituted_at_any_step", True
            ),
            lambda p: p["single_ideal_member_definition"].__setitem__(
                "discrete_killing", "B*representative_sample_V"
            ),
            lambda p: p["single_ideal_member_definition"].__setitem__(
                "continuum_form_domain", "H1_without_periodic_trace"
            ),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.assert_semantic_mutation_rejected(mutate)

    def test_density_map_and_initial_mutations_are_rejected(self) -> None:
        def remove_h1(payload: dict[str, Any]) -> None:
            payload["initial_datum_contract"][
                "regularity_proved_from_flat_compact_bump_and_positive_smooth_pi"
            ].remove("u0_f_in_H1")

        mutations: list[Callable[[dict[str, Any]], None]] = [
            lambda p: p["density_and_map_contract"].__setitem__(
                "pi_h_pc_ratio_bound",
                "pi_h_pc(x)/pi(x)=1_exactly",
            ),
            lambda p: p["density_and_map_contract"].__setitem__(
                "J_h_P_h_operator_norm_on_all_H_claimed", True
            ),
            lambda p: p["density_and_map_contract"].__setitem__("P_h_J_h_defect", "zero"),
            remove_h1,
            lambda p: p["initial_datum_contract"].__setitem__(
                "discretization", "u0_h_f=representative_sampling"
            ),
            lambda p: p["initial_datum_contract"].__setitem__(
                "initial_H1_or_H2_norm_numerically_evaluated", True
            ),
            lambda p: p["source_reconstructed_facts"]["initial_support_and_equilibrium_rows"][
                0
            ].__setitem__("nonperiodic_initial_support_strictly_inside", False),
            lambda p: p["source_reconstructed_facts"].__setitem__(
                "global_initial_support_minimum_margin_exact", "0/1"
            ),
            lambda p: p["source_reconstructed_facts"].__setitem__(
                "initial_and_killing_profile_half_widths_are_distinct", False
            ),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.assert_semantic_mutation_rejected(mutate)

    def test_theorem_and_rate_mutations_are_rejected(self) -> None:
        mutations: list[Callable[[dict[str, Any]], None]] = [
            lambda p: p["theorem_conclusions"].__setitem__(
                "ideal_fixed_box_C1_composition_closed_at_theorem_layer", False
            ),
            lambda p: p["theorem_conclusions"].__setitem__("generalized_Mosco", "not_proved"),
            lambda p: p["theorem_conclusions"].__setitem__("positive_time_state", "r=0_only"),
            lambda p: p["theorem_conclusions"].__setitem__(
                "reaction_density_definition", "g_r(t)=F_r(t)"
            ),
            lambda p: p["existence_constant_half_order_corollary"].__setitem__(
                "resolvent",
                "norm_difference<=C*h_star(n)",
            ),
            lambda p: p["existence_constant_half_order_corollary"].__setitem__(
                "theorem_constants_numerically_evaluated", True
            ),
            lambda p: p["existence_constant_half_order_corollary"].__setitem__(
                "computable_C2_certificate", True
            ),
            lambda p: p["existence_constant_half_order_corollary"].__setitem__(
                "requires_tau_strictly_positive", False
            ),
            lambda p: p["existence_constant_half_order_corollary"].__setitem__(
                "production_or_evaluator_error_included", True
            ),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.assert_semantic_mutation_rejected(mutate)

    def test_provenance_validation_and_unknown_key_mutations_are_rejected(self) -> None:
        mutations: list[Callable[[dict[str, Any]], None]] = [
            lambda p: p["source_inventory"]["round5_note"].__setitem__("sha256", "0" * 64),
            lambda p: p["build_provenance"].__setitem__(
                "executed_builder_bytes_authenticated", True
            ),
            lambda p: p["validation_scope"].__setitem__(
                "validator_is_independent_numerical_backend", True
            ),
            lambda p: p["validation_scope"].__setitem__(
                "human_round174_mathematical_audit_separate_and_required", False
            ),
            lambda p: p["quantifiers"].__setitem__("undeclared_control", [1, 0, 0, 0]),
            lambda p: p["claim_boundary"].__setitem__("complete_C1", 0),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.assert_semantic_mutation_rejected(mutate)

    def test_float_duplicate_noncanonical_and_truncated_json_are_rejected(self) -> None:
        text = self.raw.decode("ascii")
        malformed = [
            text.replace('"sequence_count": 12', '"sequence_count": 12.0', 1).encode("ascii"),
            text.replace(
                (
                    '"schema": '
                    '"encounter_continuum_c1_twelve_family_ideal_fixed_box_'
                    'C1_composition_v1",'
                ),
                (
                    '"schema": '
                    '"encounter_continuum_c1_twelve_family_ideal_fixed_box_'
                    'C1_composition_v1",\n'
                    '  "schema": '
                    '"encounter_continuum_c1_twelve_family_ideal_fixed_box_'
                    'C1_composition_v1",'
                ),
                1,
            ).encode("ascii"),
            self.raw.rstrip(b"\n"),
            self.raw[: len(self.raw) // 2],
        ]
        for raw in malformed:
            with self.subTest(prefix=raw[:50]):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "malformed.json"
                    path.write_bytes(raw)
                    result = run_validator(path)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("ERROR CompositionContractError:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_symlink_artifact_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            link = Path(directory) / "artifact-link.json"
            link.symlink_to(ARTIFACT)
            result = run_validator(link)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ERROR CompositionContractError:", result.stderr)
        self.assertNotIn("PASS_C1_COMPOSITION", result.stdout)


if __name__ == "__main__":
    unittest.main()
