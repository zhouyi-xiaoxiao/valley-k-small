#!/usr/bin/env python3
"""Adversarial mutations for the genuine refinement-family authority v2."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve()
CODE = HERE.parent
REPORT = HERE.parents[1]
sys.path.insert(0, str(CODE))

import validate_continuum_c1_genuine_joint_refinement_family_v2 as verifier  # noqa: E402

ARTIFACT = REPORT / "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


class GenuineRefinementFamilyMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.original = json.loads(ARTIFACT.read_text(encoding="ascii"))

    def assert_mutation_rejected(self, mutation: Callable[[dict[str, Any]], None]) -> None:
        candidate = copy.deepcopy(self.original)
        mutation(candidate)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.json"
            path.write_bytes(canonical(candidate))
            with self.assertRaises(verifier.VerificationError):
                verifier.validate_artifact(path)

    def test_sequence_definition_cannot_be_demoted(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["established_scope"].__setitem__(
                "genuine_refinement_sequences_defined", False
            )
        )

    def test_complete_c1_cannot_be_promoted(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["claim_boundary"].__setitem__("complete_C1", True)
        )

    def test_release_cannot_be_promoted(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["claim_boundary"].__setitem__("release_eligible", True)
        )

    def test_production_same_member_cannot_be_promoted(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["claim_boundary"].__setitem__(
                "production_same_member_bridge_accepted", True
            )
        )

    def test_correlated_n0_receipt_cannot_be_invented(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["claim_boundary"].__setitem__(
                "production_n0_correlated_containment_receipt_present", True
            )
        )

    def test_policy_cannot_be_made_retrospective(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["anti_vacuity_and_production_boundary"].__setitem__(
                "policy_can_retroactively_seal_this_successor", True
            )
        )

    def test_source_hash_mutation_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["source_inventory"]["round5_audit"].__setitem__("sha256", "0" * 64)
        )

    def test_builder_hash_mutation_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["build_provenance"].__setitem__("builder_sha256", "f" * 64)
        )

    def test_row_reordering_is_rejected(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["sequences"][0], value["sequences"][1] = (
                value["sequences"][1],
                value["sequences"][0],
            )

        self.assert_mutation_rejected(mutate)

    def test_vertex_size_formula_mutation_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["sequences"][8]["axes"][0].__setitem__(
                "size_formula", "size(n)=size0*2^n"
            )
        )

    def test_half_shift_formula_mutation_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["sequences"][10]["axes"][2].__setitem__(
                "periodic_shift_at_n_formula", "sigma(n)=0"
            )
        )

    def test_spacing_mutation_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["sequences"][0]["axes"][1].__setitem__("spacing_h0_exact", "1/1")
        )

    def test_anchor_endpoint_mutation_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["sequences"][0]["axes"][0]["domain"].__setitem__(
                "lower_exact", "-1/8"
            )
        )

    def test_uniform_bound_mutation_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["uniform_geometry_certificate"].__setitem__(
                "global_max_h0_exact", "1/1"
            )
        )

    def test_killing_average_semantics_mutation_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value["physical_volume_killing_route"].__setitem__(
                "weighted_pi_average_used", True
            )
        )

    def test_unknown_key_is_rejected(self) -> None:
        self.assert_mutation_rejected(
            lambda value: value.__setitem__("unexpected_promotion", False)
        )

    def test_float_json_number_is_rejected(self) -> None:
        text = ARTIFACT.read_text(encoding="ascii")
        mutated = text.replace('"sequence_count": 12', '"sequence_count": 12.0', 1)
        self.assertNotEqual(text, mutated)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "float.json"
            path.write_text(mutated, encoding="ascii")
            with self.assertRaises(verifier.VerificationError):
                verifier.validate_artifact(path)

    def test_duplicate_json_key_is_rejected(self) -> None:
        text = ARTIFACT.read_text(encoding="ascii")
        mutated = text.replace(
            "{\n",
            '{\n  "schema": "encounter_continuum_c1_genuine_joint_refinement_family_v2",\n',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(mutated, encoding="ascii")
            with self.assertRaises(verifier.VerificationError):
                verifier.validate_artifact(path)

    def test_noncanonical_key_order_is_rejected(self) -> None:
        reversed_top_level = {key: self.original[key] for key in reversed(tuple(self.original))}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "noncanonical.json"
            path.write_text(
                json.dumps(reversed_top_level, indent=2, sort_keys=False) + "\n",
                encoding="ascii",
            )
            with self.assertRaises(verifier.VerificationError):
                verifier.validate_artifact(path)


if __name__ == "__main__":
    unittest.main()
