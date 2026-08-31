#!/usr/bin/env python3
"""Static, source-chain, and formula tests for the map/cut/killing contract."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve()
CODE = HERE.parent
REPORT = HERE.parents[1]
sys.path.insert(0, str(CODE))

import build_continuum_c2_source_bound_map_cut_killing_contract_v1 as builder  # noqa: E402
import validate_continuum_c2_source_bound_map_cut_killing_contract_v1 as validator  # noqa: E402

ARTIFACT = REPORT / "artifacts/data/continuum_c2_source_bound_map_cut_killing_contract_v1.json"
REFINEMENT = REPORT / "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json"
GEOMETRY = REPORT / "artifacts/data/physical_killing_geometry_source_v1.json"
THEORY = REPORT / "notes/continuum_c2_source_bound_map_cut_killing_lemma_v1.md"
EXPECTED_ARTIFACT_SHA256 = "f977939e97651e1d45d83bc4d80acd3d19e6fac7d4ae90c2803090c25cfa9ee3"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction(text: str) -> Fraction:
    numerator, denominator = text.split("/", 1)
    return Fraction(int(numerator), int(denominator))


class SourceBoundMapCutKillingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="ascii"))
        cls.refinement = json.loads(REFINEMENT.read_text(encoding="ascii"))
        cls.geometry = json.loads(GEOMETRY.read_text(encoding="ascii"))

    def test_canonical_hash_builder_and_source_geometry_validator(self) -> None:
        self.assertEqual(sha256(ARTIFACT), EXPECTED_ARTIFACT_SHA256)
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
        mismatched_path_state = SimpleNamespace(
            st_dev=state.st_dev + 1,
            st_ino=state.st_ino,
        )
        with (
            patch.object(validator.os, "stat", return_value=mismatched_path_state),
            self.assertRaises(validator.ContractError),
        ):
            validator.descriptor_snapshot(ARTIFACT)

    def test_exact_source_hash_chain_including_round10_and_round11(self) -> None:
        inventory = self.payload["source_inventory"]
        self.assertEqual(set(inventory), set(builder.SOURCES))
        for role, (relative, expected) in builder.SOURCES.items():
            self.assertEqual(inventory[role], {"path": relative, "sha256": expected})
            self.assertEqual(sha256(REPORT / relative), expected)
        self.assertEqual(
            inventory["round10_free_residual_note"]["sha256"],
            "ba3d41da0f16ab4ceb0f2f0c8eceeb29214b0b5b765c9300f373a3513bb21fc4",
        )
        self.assertEqual(
            inventory["round10_free_residual_audit"]["sha256"],
            "c00351acc5ff3be67cbb579ccab768e8e226bd29bc730f5d9acb15c5dcc3163d",
        )
        self.assertEqual(
            inventory["round11_sector_note"]["sha256"],
            "4339385e8489984701aabedbd4ab0a28d69db5b2ffd7e2d1c91d1d4ba63564d9",
        )
        self.assertEqual(
            inventory["round11_sector_audit"]["sha256"],
            "d3b0aca6203999ba18f08a380847f7253e41fc72272d28f4c4fcde92dbb89a2c",
        )

    def test_quantifier_is_exactly_twelve_genuine_dyadic_sequences(self) -> None:
        scope = self.payload["family_scope"]
        self.assertEqual(scope["finite_family_cardinality"], 12)
        self.assertEqual(scope["labels"], self.refinement["sequence_order"])
        self.assertEqual(scope["common_sufficient_tail_start_n"], 0)
        self.assertEqual(
            scope["quantifier"],
            "for_each_of_exactly_12_families_for_every_integer_n_at_or_above_common_tail_start",
        )
        self.assertEqual(scope["mesh_rule"], "h_f(n)=h_f(0)*2^-n")

    def test_circle_tube_conditions_hold_from_every_n0_anchor(self) -> None:
        radius = fraction(self.geometry["contact_geometry"]["radius_exact"])
        period = fraction(self.geometry["contact_geometry"]["transverse_period_exact"])
        self.assertLess(2 * radius, period)
        global_clearance = fraction(
            self.payload["family_scope"]["global_strict_tube_clearance_exact"]
        )
        for row in self.payload["geometry_rows"]:
            h0 = fraction(row["row_max_h0_exact"])
            clearance = fraction(row["strict_tube_clearance_exact"])
            lower_margin = fraction(row["relative_lower_margin_exact"])
            upper_margin = fraction(row["relative_upper_margin_exact"])
            torus_margin = fraction(row["torus_cut_locus_margin_exact"])
            self.assertGreater(clearance, 0)
            self.assertGreaterEqual(clearance, global_clearance)
            self.assertLessEqual(2 * h0 * h0, global_clearance * global_clearance)
            self.assertLessEqual(global_clearance, radius / 2)
            self.assertLessEqual(global_clearance, torus_margin / 2)
            self.assertLessEqual(global_clearance, lower_margin / 2)
            self.assertLessEqual(global_clearance, upper_margin / 2)
        cut = self.payload["symbolic_theorem_contract"]["cut_layer"]
        self.assertEqual(
            cut["tube_area_hypotheses"],
            [
                "delta<a",
                "a+delta<W/2",
                "R_lower<-a-delta",
                "R_upper>a+delta",
            ],
        )
        self.assertIn("4*pi_circle*a*delta", cut["tube_area"])

    def test_vertex_half_cells_and_wrapped_periodic_cells_are_in_scope(self) -> None:
        counts = self.refinement["uniform_geometry_certificate"]["alignment_counts_across_36_axes"]
        self.assertEqual(counts["vertex_centred_reflecting_dual"], 4)
        self.assertEqual(counts["cell_centred_periodic_half_shift"], 2)
        preflight = self.payload["adversarial_preflight"]
        self.assertTrue(preflight["vertex_endpoint_half_cells_included"])
        self.assertTrue(preflight["wrapped_periodic_cells_included"])
        self.assertTrue(preflight["contact_tube_away_from_periodic_cut_locus_on_common_tail"])

    def test_rho_uses_physical_integrals_not_representative_masses(self) -> None:
        rho = self.payload["symbolic_theorem_contract"]["rho"]
        self.assertTrue(rho["physical_cell_mass_not_representative_mass"])
        self.assertIn("integral_C_exp_minus_Phi_a_dx", rho["axis_cell_integral_ratio"])
        self.assertIn(
            "cell_volume_i*exp_minus_Phi_a_at_representative", rho["axis_cell_integral_ratio"]
        )
        self.assertEqual(
            rho["tensor_factorization"],
            "rho_ijk=(r_M_i/bar_r_M)*(r_R_j/bar_r_R)",
        )
        self.assertEqual(
            rho["global_gauge"],
            "G=Z^-1*bar_r_M*bar_r_R=M_L/(S_M*S_R*S_Y)",
        )

    def test_j_p_and_k_definitions_are_mutually_consistent(self) -> None:
        contract = self.payload["symbolic_theorem_contract"]
        self.assertEqual(contract["map"]["exact_adjoint"], "P_h=J_h_star")
        self.assertEqual(
            contract["map"]["exact_compositions"],
            ["P_h*J_h=diag(rho)", "J_h*P_h=rho_h_pc*E_h"],
        )
        self.assertEqual(
            contract["killing_multiplier"]["definition"],
            "K_h_pc=V_h_pc/rho_h_pc",
        )
        self.assertTrue(contract["contact_profile"]["w_normalization_present"])
        self.assertEqual(
            contract["contact_profile"]["field"],
            "V=W^-1*psi(M)*indicator_Da(R,Y)",
        )

    def test_sharp_cut_exponent_and_round9_hypotheses_are_exact(self) -> None:
        contract = self.payload["symbolic_theorem_contract"]
        self.assertIn("h^(1/2)", contract["cut_layer"]["weighted_cut_bound"])
        self.assertFalse(contract["cut_layer"]["sharp_indicator_derivative_used"])
        residual = contract["round9_residual"]
        self.assertEqual(
            residual["bound"],
            "abs_R_h_kill<=C_kill*h^(1/2)*norm_u_H2*norm_v_h_1h",
        )
        self.assertEqual(
            residual["authoritative_complex_convention"],
            "complex_inner_product_conjugate_first_factor",
        )
        self.assertEqual(
            residual["hypotheses"],
            [
                "quotient_dimension_is_3_for_H2_to_Linfinity",
                "u_in_H2_on_fixed_mixed_boundary_box",
                "J_hP_h_map_bound",
                "K_h_linfinity_bound",
                "K_h_minus_V_weighted_L2_bound",
                "uniform_J_h_norm",
                "h<=1",
            ],
        )
        self.assertFalse(residual["budget_factor_selected"])

    def test_symbolic_constants_are_declared_but_not_numerically_evaluated(self) -> None:
        constants = self.payload["symbolic_theorem_contract"]["symbolic_constant_definitions"]
        self.assertFalse(constants["theorem_constants_numerically_evaluated"])
        for name in (
            "C_K",
            "C_K_cut",
            "C_K_map",
            "C_P",
            "C_V_cut",
            "C_av",
            "C_kill",
            "L_M_f",
            "L_R_f",
            "Lambda_star",
        ):
            self.assertIs(type(constants[name]), str)
            self.assertTrue(constants[name])
        self.assertEqual(
            constants["C_P"],
            "sqrt(pi_plus_star)*(C_av+Lambda_star*exp(Lambda_star*H_star))",
        )
        self.assertIn("C_K*C_P", constants["C_kill"])

    def test_validation_scope_does_not_overclaim_mathematical_replication(self) -> None:
        scope = self.payload["validation_scope"]
        self.assertTrue(scope["exact_geometry_and_source_pins_independently_reconstructible"])
        self.assertEqual(
            scope["symbolic_analysis_representation"],
            "exact_string_contract_not_backend_or_machine_proof_replication",
        )
        self.assertTrue(scope["human_mathematical_referee_separate_and_required"])
        self.assertFalse(scope["validator_is_independent_numerical_backend"])
        self.assertFalse(scope["authenticated_execution_attested"])
        provenance = self.payload["build_provenance"]
        self.assertFalse(provenance["executed_builder_bytes_authenticated"])
        self.assertFalse(provenance["source_snapshots_atomic_against_hostile_writer"])
        self.assertIn("O_NOFOLLOW", provenance["snapshot_model"])

    def test_every_promotion_and_release_flag_is_false(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary)
        self.assertTrue(all(value is False for value in boundary.values()))
        for key in (
            "complete_C1",
            "complete_C2",
            "production_n0_correlated_containment_receipt_present",
            "production_same_member_bridge_accepted",
            "production_raw_acceptance",
            "release_eligible",
        ):
            self.assertFalse(boundary[key])

    def test_theory_note_carries_the_exact_edge_case_and_scope_language(self) -> None:
        text = THEORY.read_text(encoding="utf-8")
        for required in (
            "vertex endpoint half cells",
            "Wrapped periodic cells",
            "4\\pi_{\\rm circ}a\\delta",
            "No derivative of the sharp indicator is taken",
            "globally normalized, unconditioned density",
            "production same-member map/killing receipt",
            "complete C0 / C1 / C2 / C3",
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
        for path in (
            REPORT / f"code/{Path(builder.__file__).name}",
            REPORT / f"code/{Path(validator.__file__).name}",
        ):
            source = path.read_text(encoding="utf-8")
            self.assertNotIn(".read_bytes(", source)
            roots: set[str] = set()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots.add(node.module.split(".", 1)[0])
            self.assertLessEqual(roots, allowed)


if __name__ == "__main__":
    unittest.main()
