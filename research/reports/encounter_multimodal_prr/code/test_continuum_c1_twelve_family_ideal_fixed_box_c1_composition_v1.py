#!/usr/bin/env python3
"""Static and currentness tests for the ideal fixed-box C1 composition."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

import build_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1 as builder  # noqa: E402
import validate_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1 as validator  # noqa: E402

ARTIFACT = (
    REPORT / "artifacts/data/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.json"
)
FAMILY = REPORT / "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json"
THEORY = REPORT / "notes/continuum_c1_twelve_family_ideal_fixed_box_C1_composition_v1.md"
BUILDER = REPORT / "code/build_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py"
VALIDATOR = REPORT / "code/validate_continuum_c1_twelve_family_ideal_fixed_box_c1_composition_v1.py"
EXPECTED_ARTIFACT_SHA256 = "ffbd822e8a3649405f27d9d22f21688049df6a7cc045b0899ac5b38540b4cb70"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IdealFixedBoxC1CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="ascii"))
        cls.family = json.loads(FAMILY.read_text(encoding="ascii"))

    def test_canonical_artifact_rebuild_and_independent_validation(self) -> None:
        self.assertEqual(file_sha256(ARTIFACT), EXPECTED_ARTIFACT_SHA256)
        self.assertEqual(ARTIFACT.read_bytes(), builder.canonical_bytes(self.payload))
        self.assertEqual(builder.build_payload(), self.payload)
        self.assertEqual(validator.validate_artifact(ARTIFACT), self.payload)

    def test_validator_hashes_exactly_its_single_artifact_snapshot(self) -> None:
        original_snapshot = validator.descriptor_snapshot
        artifact_snapshots: list[bytes] = []

        def tracked_snapshot(path: Path) -> bytes:
            data = original_snapshot(path)
            if Path(path) == ARTIFACT:
                artifact_snapshots.append(data)
            return data

        with patch.object(validator, "descriptor_snapshot", tracked_snapshot):
            payload, validated_digest = validator.validate_artifact_snapshot(ARTIFACT)
        self.assertEqual(payload, self.payload)
        self.assertEqual(len(artifact_snapshots), 1)
        self.assertEqual(
            validated_digest,
            hashlib.sha256(artifact_snapshots[0]).hexdigest(),
        )
        self.assertEqual(validated_digest, EXPECTED_ARTIFACT_SHA256)

    def test_descriptor_snapshot_rejects_symlink_and_path_identity_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            symlink = Path(directory) / "artifact-link.json"
            symlink.symlink_to(ARTIFACT)
            with self.assertRaises(OSError):
                validator.descriptor_snapshot(symlink)

        state = ARTIFACT.stat()
        mismatched = SimpleNamespace(st_dev=state.st_dev + 1, st_ino=state.st_ino)
        with (
            patch.object(validator.os, "stat", return_value=mismatched),
            self.assertRaises(validator.CompositionContractError),
        ):
            validator.descriptor_snapshot(ARTIFACT)

    def test_exact_source_chain_pins_round4_round5_round172_round173_and_initial(self) -> None:
        inventory = self.payload["source_inventory"]
        self.assertEqual(set(inventory), set(builder.SOURCES))
        for role, (relative, expected) in builder.SOURCES.items():
            self.assertEqual(inventory[role], {"path": relative, "sha256": expected})
            self.assertEqual(file_sha256(REPORT / relative), expected)
        self.assertEqual(
            inventory["initial_source"]["sha256"],
            "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f",
        )
        self.assertEqual(
            inventory["source_bound_artifact"]["sha256"],
            "f977939e97651e1d45d83bc4d80acd3d19e6fac7d4ae90c2803090c25cfa9ee3",
        )

    def test_full_quantifier_has_no_hidden_concrete_control_or_budget(self) -> None:
        quantifiers = self.payload["quantifiers"]
        self.assertEqual(quantifiers["sequence_count"], 12)
        self.assertEqual(quantifiers["sequence_labels"], self.family["sequence_order"])
        self.assertIn("for_every_real_w_in_Delta3", quantifiers["control_range"])
        self.assertIn("[0,B_star]", quantifiers["budget_range"])
        self.assertIn("arbitrary_fixed_and_finite", quantifiers["budget_cap"])
        self.assertIn("n_to_infinity", quantifiers["mesh_limit"])
        self.assertEqual(quantifiers["derivative_orders"], [0, 1, 2])

    def test_exact_initial_support_and_ou_interior_reconstruction(self) -> None:
        facts = self.payload["source_reconstructed_facts"]
        self.assertEqual(
            facts["global_initial_support_minimum_margin_exact"],
            "106645239176133349/288230376151711744",
        )
        self.assertEqual(
            facts["global_ou_equilibrium_minimum_margin_exact"],
            "4053239664633447/4503599627370496",
        )
        self.assertEqual(
            facts["initial_half_width_exact"],
            "5764607523034235/288230376151711744",
        )
        self.assertEqual(
            facts["killing_profile_half_width_exact"],
            "5764607523034235/144115188075855872",
        )
        self.assertTrue(facts["initial_and_killing_profile_half_widths_are_distinct"])
        self.assertEqual(len(facts["initial_support_and_equilibrium_rows"]), 12)
        for row in facts["initial_support_and_equilibrium_rows"]:
            self.assertTrue(row["nonperiodic_initial_support_strictly_inside"])
            self.assertTrue(row["ou_equilibria_strictly_inside"])
            self.assertTrue(row["periodic_initial_image_sum_smooth_on_torus"])

    def test_alignment_inventory_includes_endpoint_and_wrap_cases(self) -> None:
        counts = self.payload["source_reconstructed_facts"]["alignment_counts"]
        self.assertEqual(
            counts,
            {
                "cell_centred_periodic_base": 10,
                "cell_centred_periodic_half_shift": 2,
                "cell_centred_reflecting": 20,
                "vertex_centred_reflecting_dual": 4,
            },
        )
        self.assertTrue(
            self.payload["source_reconstructed_facts"]["vertex_endpoint_half_cells_included"]
        )
        self.assertTrue(
            self.payload["source_reconstructed_facts"]["wrapped_periodic_cells_included"]
        )

    def test_pi_h_pc_over_pi_convergence_is_explicit(self) -> None:
        contract = self.payload["density_and_map_contract"]
        self.assertIn("bar_r_M*bar_r_R", contract["pi_h_pc_ratio_exact"])
        self.assertEqual(
            contract["pi_h_pc_ratio_bound"],
            "exp(-eta_f(n))<=pi_h_pc(x)/pi(x)<=exp(eta_f(n))",
        )
        self.assertIn("_to_0", contract["pi_h_pc_uniform_convergence"])
        self.assertFalse(contract["J_h_P_h_operator_norm_on_all_H_claimed"])

    def test_initial_regularities_support_only_the_claimed_projection_rate(self) -> None:
        initial = self.payload["initial_datum_contract"]
        self.assertEqual(initial["definition"], "u0_f=q0/pi_on_Omega_f")
        self.assertEqual(initial["discretization"], "u0_h_f=P_h*u0_f")
        self.assertEqual(
            initial["regularity_proved_from_flat_compact_bump_and_positive_smooth_pi"],
            [
                "u0_f_in_C_infinity",
                "u0_f_in_H2",
                "u0_f_in_H1",
                "u0_f_in_H_f",
            ],
        )
        self.assertIn("ordinary_H1", initial["initial_projection_bound"])
        self.assertFalse(initial["initial_H1_or_H2_norm_numerically_evaluated"])
        self.assertEqual(
            initial["initial_quantitative_rate_claim_scope"],
            "existence_constant_ideal_projection_only",
        )

    def test_one_ideal_operator_is_used_for_every_step(self) -> None:
        member = self.payload["single_ideal_member_definition"]
        self.assertTrue(member["same_H_h_used_for_mosco_resolvent_rate_and_observable"])
        self.assertFalse(member["production_centres_substituted_at_any_step"])
        self.assertEqual(member["discrete_killing"], "B*V_h_C")
        self.assertIn("J_h_star", member["exact_adjoint_map"])
        self.assertIn("trace_Y=0_u=trace_Y=W_u", member["continuum_form_domain"])
        self.assertEqual(
            member["continuum_boundary_conditions"],
            "natural_Neumann_on_M_and_R_faces_and_periodic_trace_in_Y",
        )
        self.assertIn("finite_dimensional_H_h_f", member["discrete_form_domain"])
        self.assertTrue(
            self.payload["theorem_conclusions"]["discrete_observable_uses_same_V_h_and_same_H_h"]
        )

    def test_each_composition_layer_names_its_exact_predecessor(self) -> None:
        composition = self.payload["premise_composition"]
        self.assertEqual(composition["one_axis"]["genuine_sequences"], "Round172_v2")
        self.assertEqual(
            composition["tensor"]["free_generalized_Mosco"],
            "Round5_Theorem_1_1",
        )
        self.assertEqual(
            composition["bounded_killing"]["convergence_and_uniform_bound"],
            "Round173",
        )
        self.assertEqual(
            composition["half_order_corollary"]["free_residual"],
            "Round10",
        )
        self.assertEqual(
            composition["half_order_corollary"]["mixed_boundary_sector_and_contour"],
            "Round11",
        )

    def test_qualitative_c1_conclusions_and_positive_time_orders_are_exact(self) -> None:
        theorem = self.payload["theorem_conclusions"]
        self.assertTrue(theorem["ideal_fixed_box_C1_composition_closed_at_theorem_layer"])
        self.assertIn("generalized_Mosco", theorem["generalized_Mosco"])
        self.assertIn("alpha>0", theorem["strong_resolvent"])
        self.assertIn("r=0,1,2", theorem["positive_time_state"])
        self.assertIn("r=0,1,2", theorem["positive_time_contact_observable"])
        self.assertIn("r=0,1,2", theorem["positive_time_reaction_density"])
        self.assertEqual(theorem["reaction_density_definition"], "g_r(t)=B*F_r(t)")

    def test_half_order_is_existence_constant_only(self) -> None:
        rate = self.payload["existence_constant_half_order_corollary"]
        self.assertTrue(rate["ideal_only"])
        self.assertIn("h_star(n)^(1/2)", rate["resolvent"])
        self.assertIn("h_star(n)^(1/2)", rate["positive_time_operator"])
        self.assertIn("h_star(n)^(1/2)", rate["positive_time_observable"])
        self.assertIn("B_star*C_F_r", rate["positive_time_reaction_density"])
        self.assertTrue(rate["theorem_constants_finite_symbolically"])
        self.assertFalse(rate["theorem_constants_numerically_evaluated"])
        self.assertFalse(rate["theorem_constants_outwardly_enclosed"])
        self.assertFalse(rate["computable_C2_certificate"])
        self.assertFalse(rate["production_or_evaluator_error_included"])

    def test_all_project_production_and_release_flags_remain_false(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary)
        self.assertTrue(all(value is False for value in boundary.values()))
        for key in (
            "complete_C1",
            "complete_C2",
            "production_complete_C1",
            "production_same_member_bridge_accepted",
            "root_or_topology_transfer_complete",
            "release_eligible",
        ):
            self.assertFalse(boundary[key])

    def test_validation_scope_does_not_overclaim_machine_or_backend_proof(self) -> None:
        scope = self.payload["validation_scope"]
        self.assertTrue(
            scope["source_hashes_and_exact_support_geometry_independently_reconstructible"]
        )
        self.assertTrue(scope["single_artifact_descriptor_snapshot_validated_and_hashed"])
        self.assertTrue(scope["human_round174_mathematical_audit_separate_and_required"])
        self.assertFalse(scope["validator_is_independent_numerical_backend"])
        self.assertFalse(scope["authenticated_execution_attested"])
        provenance = self.payload["build_provenance"]
        self.assertFalse(provenance["executed_builder_bytes_authenticated"])
        self.assertFalse(provenance["source_snapshots_atomic_against_hostile_writer"])

    def test_theory_note_carries_required_quantifiers_formulae_and_boundaries(self) -> None:
        text = THEORY.read_text(encoding="utf-8")
        for required in (
            "f\\in\\mathcal F_{12}",
            "w=(w_1,\\ldots,w_4)\\in\\Delta_3",
            "0\\le B\\le B_*<\\infty",
            "\\frac{\\pi_{h,f}^{\\rm pc}(x)}{\\pi(x)}",
            "u_{0,f}:=\\frac{q_0}{\\pi}",
            "u_{0,h,f}:=P_hu_{0,f}",
            "\\mathcal V_f",
            "generalized\\ Mosco",
            "r=0,1,2",
            "g_{f,w,B}^{(r)}(t)=B F_{f,w,B}^{(r)}(t)",
            "existence-constant ideal rates",
            "production complete_C1 or project complete_C1",
            "computable C2",
        ):
            self.assertIn(required, text)

    def test_builder_and_validator_use_standard_library_only(self) -> None:
        allowed = {
            "__future__",
            "argparse",
            "fractions",
            "hashlib",
            "json",
            "os",
            "pathlib",
            "re",
            "stat",
            "sys",
            "typing",
        }
        for path in (BUILDER, VALIDATOR):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imported: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".", 1)[0])
            self.assertLessEqual(imported, allowed)

    def test_pinned_source_registry_drift_fails_closed(self) -> None:
        original = validator.PINNED["round4_note"]
        with patch.dict(
            validator.PINNED,
            {"round4_note": (original[0], "0" * 64)},
            clear=False,
        ):
            with self.assertRaises(validator.CompositionContractError):
                validator.validate_artifact(ARTIFACT)


if __name__ == "__main__":
    unittest.main()
