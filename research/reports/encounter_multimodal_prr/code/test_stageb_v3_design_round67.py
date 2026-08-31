"""Small, science-free checks for the independent Round-67 Stage-B-v3 audit."""

from __future__ import annotations

import hashlib
import unittest
from fractions import Fraction
from pathlib import Path


REPORT = Path(__file__).resolve().parents[1]
DESIGN = REPORT / "notes" / "positive_b_stage_b_validation_design_v3.md"
EXPECTED_DESIGN_SHA256 = "0c7119870e173bfbe5042b3f1c19c7c5851061940cab66e7e0dab98f54becd58"


class StageBV3Round67Checks(unittest.TestCase):
    def test_attacked_design_snapshot_is_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(DESIGN.read_bytes()).hexdigest(),
            EXPECTED_DESIGN_SHA256,
        )

    def test_role_matrix_and_cell_arithmetic(self) -> None:
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
        self.assertEqual((8 + 7) * 8, 120)
        self.assertEqual(15 * sum(states), 394_997_850)
        self.assertEqual(2 * 15 * sum(states), 789_995_700)

    def test_exact_alpha_and_power_cardinalities(self) -> None:
        alpha = (
            12 * Fraction(1, 1200)
            + 78 * Fraction(1, 5200)
            + 84 * Fraction(1, 5600)
            + 116 * Fraction(1, 11600)
        )
        self.assertEqual(alpha, Fraction(1, 20))
        self.assertEqual(2 * (4 + 9 + 4 + 14), 62)
        self.assertEqual(
            (3 + 1 + 2 + 3, 5 + 1 + 3 + 5, 4 + 0 + 2 + 4),
            (9, 14, 10),
        )

    def test_max_of_mesh_difference_and_errors_is_not_an_error_envelope(self) -> None:
        """Exhibit admissible true values outside the current Sec. 6.3/7.1 E_FV."""

        reported_grid = 0.0
        reported_reference = 0.1
        grid_error = 0.08
        reference_error = 0.08

        current_e_fv = max(
            abs(reported_grid - reported_reference),
            grid_error,
            reference_error,
        )
        admissible_true_grid = reported_grid - grid_error
        admissible_true_reference = reported_reference + reference_error
        admissible_true_gap = abs(admissible_true_grid - admissible_true_reference)

        self.assertEqual(current_e_fv, 0.1)
        self.assertAlmostEqual(admissible_true_gap, 0.26)
        self.assertGreater(admissible_true_gap, current_e_fv)
        self.assertAlmostEqual(
            abs(reported_grid - reported_reference) + grid_error + reference_error,
            admissible_true_gap,
        )


if __name__ == "__main__":
    unittest.main()
