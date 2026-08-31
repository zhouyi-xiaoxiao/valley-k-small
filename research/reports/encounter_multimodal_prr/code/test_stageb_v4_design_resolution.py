"""Science-free positive regressions for the Stage-B-v4 design resolution."""

from __future__ import annotations

import hashlib
import math
import unittest
from fractions import Fraction
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]
DESIGN = REPORT / "notes" / "positive_b_stage_b_validation_design_v4.md"
EXPECTED_DESIGN_SHA256 = "e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691"


def interval(reported: float, radius: float) -> tuple[float, float]:
    return reported - radius, reported + radius


def discrepancy_upper(left: tuple[float, float], right: tuple[float, float]) -> float:
    return max(abs(left[0] - right[1]), abs(left[1] - right[0]))


def distance_lower(left: tuple[float, float], right: tuple[float, float]) -> float:
    return max(0.0, left[0] - right[1], right[0] - left[1])


def metric(left: tuple[float, float, float], right: tuple[float, float, float]) -> float:
    return max(
        abs(left[0] - right[0]) / 34.5,
        abs(left[1] - right[1]),
        abs(left[2] - right[2]),
    )


def role_radii(seeds: tuple[tuple[float, float, float], ...]) -> tuple[float, ...]:
    radii = []
    for index, seed in enumerate(seeds):
        time, theta_1, theta_2 = seed
        boundary = min(
            (time - 9.0) / 34.5,
            (18.0 - time) / 34.5,
            0.15 - abs(theta_1),
            0.15 - abs(theta_2),
        )
        separation = min(metric(seed, other) for j, other in enumerate(seeds) if j != index)
        radii.append(min(1.0 / 128.0, boundary / 4.0, separation / 4.0))
    return tuple(radii)


class StageBV4DesignResolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DESIGN.read_text(encoding="utf-8")

    def test_v4_snapshot_and_positive_interval_envelope(self) -> None:
        self.assertEqual(hashlib.sha256(DESIGN.read_bytes()).hexdigest(), EXPECTED_DESIGN_SHA256)

        grid = interval(0.0, 0.08)
        reference = interval(0.1, 0.08)
        repaired_e_fv = discrepancy_upper(grid, reference)
        self.assertAlmostEqual(repaired_e_fv, 0.26)
        self.assertGreaterEqual(repaired_e_fv, abs(0.0 - 0.1) + 0.08 + 0.08)
        self.assertIn("abs(qhat_g-qhat_ref) + r_g + r_ref", self.text)
        self.assertIn("Every absolute cap, quarter-margin rule", self.text)

    def test_complete_implicit_certificate_terms_are_mandatory(self) -> None:
        for term in (
            "six-variable joint system",
            "t_F-t_C-\\sigma a",
            "rho_lin",
            "eps_F",
            "eps_J",
            "interval-Newton/Krawczyk",
            "E_FV,S <= rho_role/4",
        ):
            self.assertIn(term, self.text)
        self.assertIn("cusp-time error", self.text)

    def test_saved_field_radius_algorithm_is_positive_and_disjoint(self) -> None:
        seeds = (
            (13.00, 0.000, 0.000),
            (12.25, -0.080, -0.020),
            (12.50, -0.060, -0.010),
            (12.75, -0.040, 0.000),
            (13.25, 0.040, 0.000),
            (13.50, 0.060, 0.010),
            (13.75, 0.080, 0.020),
        )
        radii = role_radii(seeds)
        self.assertTrue(all(0.0 < radius <= 1.0 / 128.0 for radius in radii))
        for i, left in enumerate(seeds):
            for j, right in enumerate(seeds):
                if i < j:
                    self.assertLessEqual(radii[i] + radii[j], metric(left, right) / 2.0)
        self.assertNotIn("exact upstream cusp trust radius", self.text)
        self.assertIn("FP_CONTRACT=OFF", self.text)
        self.assertIn("intentional **cross-collection join**", self.text)

    def test_absolute_caps_and_interval_odd_contraction_are_restored(self) -> None:
        expected_caps = ("`0.05`", "`0.005`", "`0.02`", "`0.001`", "`0.01`", "`0.50`")
        for cap in expected_caps:
            self.assertIn(cap, self.text)
        self.assertIn("E_{FV}(q)\\le\\min(E_{abs,q},d/4)", self.text)
        self.assertIn("D+(I_O161,I_O129) < D-(I_O129,I_O113)", self.text)
        self.assertIn("5e-8", self.text)

        coarse = interval(0.0, 0.0)
        middle = interval(0.4, 0.0)
        fine = interval(0.5, 0.0)
        self.assertLess(discrepancy_upper(fine, middle), distance_lower(middle, coarse))

        noncontracting = interval(0.9, 0.0)
        self.assertFalse(discrepancy_upper(noncontracting, middle) < distance_lower(middle, coarse))

    def test_workload_alpha_power_and_rate_remain_exact(self) -> None:
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
        self.assertEqual(15 * 8, 120)
        self.assertEqual(15 * sum(states), 394_997_850)
        self.assertEqual(2 * 15 * sum(states), 789_995_700)

        alpha = (
            12 * Fraction(1, 1200)
            + 78 * Fraction(1, 5200)
            + 84 * Fraction(1, 5600)
            + 116 * Fraction(1, 11600)
        )
        self.assertEqual(alpha, Fraction(1, 20))
        self.assertEqual(2 * (4 + 9 + 4 + 14), 62)
        rate = (0.01 / 0.04) * (1.0 + 2.0**-48) * math.exp(1.0 / 3.0)
        self.assertAlmostEqual(rate, 0.3489031062715236)
        self.assertLess(rate, 0.35)

    def test_pool_wording_endpoints_and_freeze_graph_are_unambiguous(self) -> None:
        self.assertIn("pool_statistical_equivalence_verified = false", self.text)
        self.assertIn("not statistical equivalence", self.text)
        self.assertIn("both_pools_compatible_with_common_target", self.text)
        self.assertIn("fv_acceptance.lower", self.text)
        self.assertIn("fv_acceptance.upper", self.text)
        self.assertNotIn(",,", self.text)
        self.assertIn("positive-b-stage-b-v4-off-lattice-sha256-counter-v1", self.text)
        self.assertIn("u64be(i) || u64be(j)", self.text)
        self.assertIn("Only **after** `M_B` has an immutable hash", self.text)
        self.assertIn("`M_B` never\npins `A_B`", self.text)
        self.assertIn("AUTHORIZED-SCIENTIFIC-COMMAND: NONE", self.text)


if __name__ == "__main__":
    unittest.main()
