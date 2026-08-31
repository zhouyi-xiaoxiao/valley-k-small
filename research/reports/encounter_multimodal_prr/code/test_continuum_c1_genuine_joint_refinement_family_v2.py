#!/usr/bin/env python3
"""Static and formula checks for the genuine refinement-family authority v2."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
REPORT = HERE.parents[1]
sys.path.insert(0, str(CODE))

import build_continuum_c1_genuine_joint_refinement_family_v2 as builder  # noqa: E402
import validate_continuum_c1_genuine_joint_refinement_family_v2 as validator  # noqa: E402

ARTIFACT = REPORT / "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json"
CONFIG = REPORT / "artifacts/data/physical_configuration_family_control_free_v1.json"
EXPECTED_ARTIFACT_SHA256 = "1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational(text: str) -> Fraction:
    numerator, denominator = text.split("/", 1)
    return Fraction(int(numerator), int(denominator))


def level(axis: dict[str, object], n: int) -> tuple[int, int, Fraction, Fraction | None]:
    size0 = axis["anchor_size"]
    if not isinstance(size0, int):
        raise TypeError("anchor_size must be int")
    alignment = axis["alignment"]
    if alignment == "vertex_centred_reflecting_dual":
        intervals = (size0 - 1) * 2**n
        size = intervals + 1
    else:
        intervals = size0 * 2**n
        size = intervals
    h = rational(str(axis["spacing_h0_exact"])) / 2**n
    shift: Fraction | None = None
    if alignment == "cell_centred_periodic_base":
        shift = Fraction(0)
    elif alignment == "cell_centred_periodic_half_shift":
        shift = h / 2
    return size, intervals, h, shift


class GenuineRefinementFamilyV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="ascii"))
        cls.config = json.loads(CONFIG.read_text(encoding="ascii"))

    def test_canonical_hash_and_full_independent_validation(self) -> None:
        self.assertEqual(sha256(ARTIFACT), EXPECTED_ARTIFACT_SHA256)
        self.assertEqual(ARTIFACT.read_bytes(), builder.canonical_bytes(self.payload))
        self.assertEqual(validator.validate_artifact(ARTIFACT), self.payload)

    def test_builder_reconstructs_byte_identical_payload(self) -> None:
        self.assertEqual(builder.build_payload(), self.payload)

    def test_exact_twelve_sequence_order_and_n0_anchor(self) -> None:
        self.assertEqual(self.payload["sequence_count"], 12)
        self.assertEqual(self.payload["sequence_order"], self.config["configuration_order"])
        for index, (sequence, source_row) in enumerate(
            zip(
                self.payload["sequences"],
                self.config["configurations"],
                strict=True,
            )
        ):
            self.assertEqual(sequence["source_row_index"], index)
            self.assertEqual(sequence["label"], source_row["label"])
            self.assertTrue(sequence["anchor_geometry_exactly_reproduced_at_n0"])
            self.assertEqual(sequence["anchor_shape"], source_row["shape"])
            for axis, coordinate in zip(
                sequence["axes"], self.config["coordinate_order"], strict=True
            ):
                size, intervals, _h, shift = level(axis, 0)
                source_axis = source_row[coordinate]
                self.assertEqual(axis["coordinate"], coordinate)
                self.assertEqual(axis["alignment"], source_axis["alignment"])
                self.assertEqual(size, source_axis["size"])
                self.assertEqual(intervals, axis["anchor_interval_count"])
                if shift is not None:
                    self.assertEqual(
                        shift,
                        rational(source_axis["periodic_shift_exact"]),
                    )

    def test_dyadic_size_spacing_and_half_shift_rules(self) -> None:
        half_shift_axes = 0
        vertex_axes = 0
        for sequence in self.payload["sequences"]:
            for axis in sequence["axes"]:
                size0, intervals0, h0, shift0 = level(axis, 0)
                for n in (1, 2, 7):
                    size, intervals, h, shift = level(axis, n)
                    self.assertEqual(intervals, intervals0 * 2**n)
                    self.assertEqual(h, h0 / 2**n)
                    if axis["alignment"] == "vertex_centred_reflecting_dual":
                        vertex_axes += int(n == 1)
                        self.assertEqual(size, (size0 - 1) * 2**n + 1)
                    else:
                        self.assertEqual(size, size0 * 2**n)
                    if axis["alignment"] == "cell_centred_periodic_half_shift":
                        half_shift_axes += int(n == 1)
                        self.assertEqual(shift, h / 2)
                    elif axis["alignment"] == "cell_centred_periodic_base":
                        self.assertEqual(shift, Fraction(0))
                if shift0 is not None:
                    self.assertEqual(rational(axis["periodic_shift_n0_exact"]), shift0)
        self.assertEqual(vertex_axes, 4)
        self.assertEqual(half_shift_axes, 2)

    def test_uniform_mesh_certificate_recomputes_exactly(self) -> None:
        row_maxima: list[Fraction] = []
        row_aspects: list[Fraction] = []
        for sequence in self.payload["sequences"]:
            spacings = [rational(axis["spacing_h0_exact"]) for axis in sequence["axes"]]
            minimum_sides = [
                rational(axis["spacing_h0_exact"]) * rational(axis["minimum_axis_volume_factor"])
                for axis in sequence["axes"]
            ]
            row_maximum = max(spacings)
            row_maxima.append(row_maximum)
            row_aspects.append(row_maximum / min(minimum_sides))
            self.assertEqual(rational(sequence["row_max_h0_exact"]), row_maximum)
            self.assertEqual(
                rational(sequence["row_cartesian_side_aspect_bound_exact"]),
                row_aspects[-1],
            )
        certificate = self.payload["uniform_geometry_certificate"]
        self.assertEqual(rational(certificate["global_max_h0_exact"]), max(row_maxima))
        self.assertEqual(
            rational(certificate["global_cartesian_side_aspect_bound_exact"]),
            max(row_aspects),
        )
        for n in (0, 1, 9):
            observed = max(row_maximum / 2**n for row_maximum in row_maxima)
            expected = rational(certificate["global_max_h0_exact"]) / 2**n
            self.assertEqual(observed, expected)
        self.assertTrue(certificate["maximum_axis_spacing_tends_to_zero_uniformly_over_12"])

    def test_only_narrow_established_scope_is_true(self) -> None:
        established = self.payload["established_scope"]
        self.assertTrue(established["genuine_refinement_sequences_defined"])
        self.assertTrue(established["maximum_axis_spacing_limit_proved"])
        self.assertTrue(established["shape_regularity_proved"])
        self.assertEqual(established["sequence_count"], 12)
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary)
        self.assertTrue(all(value is False for value in boundary.values()))
        self.assertFalse(boundary["production_n0_correlated_containment_receipt_present"])
        self.assertFalse(boundary["production_same_member_bridge_accepted"])
        self.assertFalse(boundary["fixed_row_anti_vacuity_policy_retrospectively_seals_successor"])
        self.assertFalse(boundary["uniform_operator_or_mosco_constants_proved_for_12_families"])

    def test_sources_and_build_are_exactly_pinned(self) -> None:
        inventory = self.payload["source_inventory"]
        self.assertEqual(set(inventory), set(builder.SOURCES))
        for role, (relative, expected_sha) in builder.SOURCES.items():
            self.assertEqual(inventory[role]["path"], relative)
            self.assertEqual(inventory[role]["sha256"], expected_sha)
            self.assertEqual(sha256(REPORT / relative), expected_sha)
        provenance = self.payload["build_provenance"]
        self.assertEqual(
            provenance["builder_sha256"],
            sha256(REPORT / provenance["builder_path"]),
        )
        self.assertEqual(
            provenance["arithmetic"],
            "python_stdlib_Fraction_exact_rational_only",
        )
        self.assertFalse(provenance["project_module_imports_used"])

    def test_builder_and_validator_import_only_standard_library(self) -> None:
        allowed_roots = {
            "__future__",
            "argparse",
            "fractions",
            "hashlib",
            "json",
            "pathlib",
            "re",
            "sys",
            "typing",
        }
        for path in (
            REPORT / "code/build_continuum_c1_genuine_joint_refinement_family_v2.py",
            REPORT / "code/validate_continuum_c1_genuine_joint_refinement_family_v2.py",
        ):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            roots: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots.add(node.module.split(".", 1)[0])
            self.assertLessEqual(roots, allowed_roots)

    def test_anti_vacuity_and_killing_boundaries_are_explicit(self) -> None:
        anti = self.payload["anti_vacuity_and_production_boundary"]
        self.assertFalse(anti["current_policy_predecessor_order_independently_sealed"])
        self.assertFalse(anti["policy_can_retroactively_seal_this_successor"])
        self.assertTrue(anti["independent_correlated_n0_receipt_still_required"])
        killing = self.payload["physical_volume_killing_route"]
        self.assertFalse(killing["concrete_control_combination_present"])
        self.assertFalse(killing["weighted_pi_average_used"])
        self.assertIn("physical_volume(cell)", killing["definition"])


if __name__ == "__main__":
    unittest.main()
