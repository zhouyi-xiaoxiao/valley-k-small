"""Science-free counterexamples for the independent Round-70 v4 attack."""

from __future__ import annotations

import hashlib
import math
import unittest
from fractions import Fraction
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]
DESIGN = REPORT / "notes" / "positive_b_stage_b_validation_design_v4.md"
ROUND69_TEST = REPORT / "code" / "test_stageb_v4_design_resolution.py"
EXPECTED_DESIGN_SHA256 = "e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691"

Interval = tuple[float, float]


def discrepancy_upper(left: Interval, right: Interval) -> float:
    """The v4 D+ / scalar interval-discrepancy formula."""
    return max(abs(left[0] - right[1]), abs(left[1] - right[0]))


def distance_lower(left: Interval, right: Interval) -> float:
    """The v4 D- formula."""
    return max(0.0, left[0] - right[1], right[0] - left[1])


def v4_odd_gate(coarse: Interval, middle: Interval, fine: Interval) -> bool:
    """The literal OR gate in v4 Section 8.2."""
    coarse_at_floor = discrepancy_upper(middle, coarse) <= 5.0e-8
    certified_contraction = discrepancy_upper(fine, middle) < distance_lower(middle, coarse)
    return coarse_at_floor or certified_contraction


class StageBV4Round70Attack(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DESIGN.read_text(encoding="utf-8")
        cls.round69_test = ROUND69_TEST.read_text(encoding="utf-8")

    def test_attacked_snapshot_and_round67_interval_repair(self) -> None:
        self.assertEqual(hashlib.sha256(DESIGN.read_bytes()).hexdigest(), EXPECTED_DESIGN_SHA256)
        grid = (-0.08, 0.08)
        reference = (0.02, 0.18)
        self.assertAlmostEqual(discrepancy_upper(grid, reference), 0.26)

    def test_roundoff_exception_admits_a_noncontracting_fine_jump(self) -> None:
        # A physically admissible allocation-weight example.  The complete
        # reference-centred envelope is 0.002 <= E_abs=0.005, yet the fine odd
        # level jumps by 0.004 after two exactly agreeing coarser levels.
        coarse = (0.300, 0.300)
        middle = (0.300, 0.300)
        fine = (0.304, 0.304)
        reference = (0.302, 0.302)

        coarse_difference = discrepancy_upper(middle, coarse)
        fine_difference = discrepancy_upper(fine, middle)
        coarse_separation_lower = distance_lower(middle, coarse)
        e_fv = max(
            discrepancy_upper(interval, reference)
            for interval in (coarse, middle, fine, reference)
        )

        self.assertEqual(coarse_difference, 0.0)
        self.assertGreater(fine_difference, 5.0e-8)
        self.assertFalse(fine_difference < coarse_separation_lower)
        self.assertLessEqual(e_fv, 0.005)
        self.assertTrue(v4_odd_gate(coarse, middle, fine))

    def test_round69_positive_test_never_applies_the_full_odd_or_gate(self) -> None:
        # Round 69 checks only the contraction sub-expression.  It never joins
        # it to the roundoff-floor exception, which is where the bypass lives.
        self.assertIn(
            "self.assertFalse(discrepancy_upper(noncontracting, middle) <",
            self.round69_test,
        )
        self.assertNotIn("coarse_at_floor or certified_contraction", self.round69_test)

    def test_t0_selector_still_has_undefined_operands_and_rounding(self) -> None:
        self.assertIn("For saved candidate displacement `d`", self.text)
        self.assertNotIn("d = theta_candidate - theta_branch", self.text)
        self.assertNotIn("d = theta_i - theta_b", self.text)
        self.assertIn("compute the central chart secant", self.text)
        self.assertNotIn("theta_next}-\\theta_{previous", self.text)

        # V4 uses down64/up64 throughout, including the T0 role radii, but no
        # v4 clause defines either operator.  Section 4.1 instead prescribes RN
        # for every displayed operation, leaving the directed conversion and
        # intermediate-error policy to the future implementation.
        self.assertIn("rho_i=down64", self.text)
        self.assertNotIn("`down64(x)` is the greatest finite binary64", self.text)
        self.assertNotIn("`up64(x)` is the least finite binary64", self.text)

    def test_closed_arithmetic_remains_correct(self) -> None:
        states = (
            113**3,
            128**3,
            129**3,
            161**3,
            166 * 129 * 129,
            129 * 172 * 129,
            166 * 172 * 129,
            207 * 215 * 161,
        )
        self.assertEqual(sum(states), 26_333_190)
        self.assertEqual(15 * sum(states), 394_997_850)
        self.assertEqual(30 * sum(states), 789_995_700)
        self.assertEqual(
            12 * Fraction(1, 1200)
            + 78 * Fraction(1, 5200)
            + 84 * Fraction(1, 5600)
            + 116 * Fraction(1, 11600),
            Fraction(1, 20),
        )
        self.assertEqual(8 + (13 + 14) * 2 * 2, 116)
        self.assertEqual(2 * (4 + 9 + 4 + 14), 62)
        rate = (0.01 / 0.04) * (1.0 + 2.0**-48) * math.exp(1.0 / 3.0)
        self.assertAlmostEqual(rate, 0.3489031062715236)
        self.assertLess(rate, 0.35)


if __name__ == "__main__":
    unittest.main()
