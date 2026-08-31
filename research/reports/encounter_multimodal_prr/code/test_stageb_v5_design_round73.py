"""Independent, science-free adversarial checks for the Stage-B-v5 design.

This file never imports a scientific producer or opens a scientific result.
It reconstructs the exact-real directed odd-grid gate from the design and
checks the selector/provenance contract only against frozen text and hashes.
"""

from __future__ import annotations

import hashlib
import math
import unittest
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]
DESIGN = REPORT / "notes" / "positive_b_stage_b_validation_design_v5.md"
V4_DESIGN = REPORT / "notes" / "positive_b_stage_b_validation_design_v4.md"
V3_DESIGN = REPORT / "notes" / "positive_b_stage_b_validation_design_v3.md"
ROUND70 = REPORT / "audits" / "round_70_stageb_v4_independent_attack.md"
ROUND72 = REPORT / "audits" / "round_72_stageb_v5_design_resolution.md"
ROUND72_TEST = REPORT / "code" / "test_stageb_v5_design_resolution.py"

EXPECTED_SHA256 = {
    DESIGN: "136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd",
    V4_DESIGN: "e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691",
    V3_DESIGN: "0c7119870e173bfbe5042b3f1c19c7c5851061940cab66e7e0dab98f54becd58",
    ROUND70: "0fa94a3d94db356e81f62746f267743bbc3f431dc82959894d00b88a9bea9c62",
    ROUND72: "5653bc0a56df5ee4189f28814440c6c25198ee5d0774524d1099dde8facf9f89",
    ROUND72_TEST: "702c2bcd1e46191b30b8c8a4e723a1c4d84b6807db6f091e90fae64b62f1f334",
}

ODD_FLOOR = float.fromhex("0x1.ad7f29abcaf48p-25")
TIME_SCALE = float.fromhex("0x1.1400000000000p+5")
THETA_BOUND = float.fromhex("0x1.3333333333333p-3")
RHO_CAP = float.fromhex("0x1.0000000000000p-7")

Interval = tuple[float, float]
Point = tuple[float, float, float]


class Hold(ValueError):
    """The exact science-free fixture reaches a normative HOLD boundary."""


def canonical_float(value: float) -> float:
    if not math.isfinite(value):
        raise Hold("nonfinite binary64 input")
    return 0.0 if value == 0.0 else value


def exact(value: float) -> Fraction:
    return Fraction.from_float(canonical_float(value))


def down64(value: Fraction) -> float:
    try:
        rounded = float(value)
    except OverflowError as exc:
        raise Hold("directed endpoint overflow") from exc
    if not math.isfinite(rounded):
        raise Hold("nonfinite directed endpoint")
    if exact(rounded) > value:
        rounded = math.nextafter(rounded, -math.inf)
    if not math.isfinite(rounded):
        raise Hold("directed endpoint outside finite binary64")
    return canonical_float(rounded)


def up64(value: Fraction) -> float:
    try:
        rounded = float(value)
    except OverflowError as exc:
        raise Hold("directed endpoint overflow") from exc
    if not math.isfinite(rounded):
        raise Hold("nonfinite directed endpoint")
    if exact(rounded) < value:
        rounded = math.nextafter(rounded, math.inf)
    if not math.isfinite(rounded):
        raise Hold("directed endpoint outside finite binary64")
    return canonical_float(rounded)


def checked_interval(interval: Interval) -> tuple[Fraction, Fraction]:
    lower, upper = map(exact, interval)
    if lower > upper:
        raise Hold("malformed interval")
    return lower, upper


def dplus(left: Interval, right: Interval) -> float:
    left_lower, left_upper = checked_interval(left)
    right_lower, right_upper = checked_interval(right)
    exact_upper = max(
        abs(left_lower - right_upper),
        abs(left_upper - right_lower),
    )
    return up64(exact_upper)


def dminus(left: Interval, right: Interval) -> float:
    left_lower, left_upper = checked_interval(left)
    right_lower, right_upper = checked_interval(right)
    exact_lower = max(
        Fraction(0),
        left_lower - right_upper,
        right_lower - left_upper,
    )
    return down64(exact_lower)


def odd_gate(coarse: Interval, middle: Interval, fine: Interval) -> bool:
    coarse_plus = dplus(middle, coarse)
    fine_plus = dplus(fine, middle)
    coarse_minus = dminus(middle, coarse)
    return (
        max(coarse_plus, fine_plus) <= ODD_FLOOR
        or fine_plus < coarse_minus
    )


def native_rn_dplus(left: Interval, right: Interval) -> float:
    """The non-outward helper used in the Round-72 positive test."""
    return max(abs(left[0] - right[1]), abs(left[1] - right[0]))


def native_rn_dminus(left: Interval, right: Interval) -> float:
    """The non-outward helper used in the Round-72 positive test."""
    return max(0.0, left[0] - right[1], right[0] - left[1])


def native_rn_odd_gate(coarse: Interval, middle: Interval, fine: Interval) -> bool:
    coarse_plus = native_rn_dplus(middle, coarse)
    fine_plus = native_rn_dplus(fine, middle)
    coarse_minus = native_rn_dminus(middle, coarse)
    return (
        max(coarse_plus, fine_plus) <= ODD_FLOOR
        or fine_plus < coarse_minus
    )


def exact_metric(left: Point, right: Point) -> Fraction:
    return max(
        abs(exact(left[0]) - exact(right[0])) / exact(TIME_SCALE),
        abs(exact(left[1]) - exact(right[1])),
        abs(exact(left[2]) - exact(right[2])),
    )


def role_radii(seeds: tuple[Point, ...]) -> tuple[float, ...]:
    if len(seeds) != 7:
        raise Hold("the v5 role schema requires seven seeds")
    radii: list[float] = []
    for index, seed in enumerate(seeds):
        boundary_components = (
            down64((exact(seed[0]) - exact(9.0)) / exact(TIME_SCALE)),
            down64((exact(18.0) - exact(seed[0])) / exact(TIME_SCALE)),
            down64(exact(THETA_BOUND) - abs(exact(seed[1]))),
            down64(exact(THETA_BOUND) - abs(exact(seed[2]))),
        )
        boundary_lower = min(boundary_components)
        separation_lower = min(
            down64(exact_metric(seed, other))
            for other_index, other in enumerate(seeds)
            if other_index != index
        )
        radius = down64(
            min(
                exact(RHO_CAP),
                exact(boundary_lower) / 4,
                exact(separation_lower) / 4,
            )
        )
        if min(boundary_lower, separation_lower, radius) <= 0.0:
            raise Hold("nonpositive role radius")
        radii.append(radius)
    return tuple(radii)


def strictly_inside(seed: Point, radius: float) -> bool:
    time_displacement = exact(TIME_SCALE) * exact(radius)
    return (
        exact(seed[0]) - time_displacement > exact(9.0)
        and exact(seed[0]) + time_displacement < exact(18.0)
        and exact(seed[1]) - exact(radius) > -exact(THETA_BOUND)
        and exact(seed[1]) + exact(radius) < exact(THETA_BOUND)
        and exact(seed[2]) - exact(radius) > -exact(THETA_BOUND)
        and exact(seed[2]) + exact(radius) < exact(THETA_BOUND)
    )


def pairwise_disjoint(seeds: tuple[Point, ...], radii: tuple[float, ...]) -> bool:
    for left_index, left in enumerate(seeds):
        for right_index in range(left_index + 1, len(seeds)):
            radius_upper = up64(
                exact(radii[left_index]) + exact(radii[right_index])
            )
            distance_lower = down64(exact_metric(left, seeds[right_index]))
            if not radius_upper < distance_lower:
                return False
    return True


class StageBV5Round73IndependentAttack(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DESIGN.read_text(encoding="utf-8")
        cls.flat_text = " ".join(cls.text.split())
        cls.round72_test_text = ROUND72_TEST.read_text(encoding="utf-8")

    def test_hash_closed_snapshots_are_current(self) -> None:
        for path, expected in EXPECTED_SHA256.items():
            with self.subTest(path=path.relative_to(REPORT)):
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_round70_bypass_is_rejected_by_exact_directed_gate(self) -> None:
        coarse = (0.300, 0.300)
        middle = (0.300, 0.300)
        fine = (0.304, 0.304)
        self.assertFalse(odd_gate(coarse, middle, fine))
        self.assertTrue(odd_gate((0.3, 0.3), (0.3, 0.3), (0.3, 0.3)))
        self.assertTrue(odd_gate((0.0, 0.0), (0.4, 0.4), (0.5, 0.5)))

    def test_half_ulp_floor_boundary_requires_outward_rounding(self) -> None:
        half_floor = ODD_FLOOR / 2.0
        next_half = math.nextafter(half_floor, math.inf)
        coarse = (half_floor, half_floor)
        middle = (-next_half, -next_half)
        fine = coarse

        exact_gap = exact(half_floor) + exact(next_half)
        floor_exact = exact(ODD_FLOOR)
        next_floor = math.nextafter(ODD_FLOOR, math.inf)
        midpoint = (floor_exact + exact(next_floor)) / 2

        self.assertEqual(exact_gap, midpoint)
        self.assertEqual(native_rn_dplus(middle, coarse), ODD_FLOOR)
        self.assertEqual(dplus(middle, coarse), next_floor)
        self.assertTrue(native_rn_odd_gate(coarse, middle, fine))
        self.assertFalse(odd_gate(coarse, middle, fine))

        # The Round-72 helper is useful for its finite fixtures but is not the
        # exact outward production operation.  This independent test closes
        # that evidence-only boundary before any T0 implementation exists.
        self.assertIn("def discrepancy_upper", self.round72_test_text)
        self.assertNotIn("def discrepancy_upper_directed", self.round72_test_text)

    def test_vector_gate_rejects_one_bad_coordinate(self) -> None:
        coarse = ((0.1, 0.1), (0.300, 0.300))
        middle = ((0.1, 0.1), (0.300, 0.300))
        fine = ((0.1, 0.1), (0.304, 0.304))

        coarse_plus = max(dplus(m, c) for m, c in zip(middle, coarse))
        fine_plus = max(dplus(f, m) for f, m in zip(fine, middle))
        coarse_minus = max(dminus(m, c) for m, c in zip(middle, coarse))
        vector_gate = (
            max(coarse_plus, fine_plus) <= ODD_FLOOR
            or fine_plus < coarse_minus
        )
        self.assertFalse(vector_gate)

    def test_directed_rounding_zero_subnormal_and_nonfinite_boundaries(self) -> None:
        minimum_subnormal = math.nextafter(0.0, math.inf)
        positive_half = exact(minimum_subnormal) / 2
        negative_half = -positive_half

        self.assertEqual(down64(positive_half), 0.0)
        self.assertEqual(up64(positive_half), minimum_subnormal)
        self.assertEqual(down64(negative_half), -minimum_subnormal)
        self.assertEqual(up64(negative_half), 0.0)
        self.assertEqual(math.copysign(1.0, up64(negative_half)), 1.0)

        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(Hold):
                exact(value)

    def test_role_radius_formula_has_both_outward_properties(self) -> None:
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
        self.assertTrue(all(0.0 < radius <= RHO_CAP for radius in radii))
        self.assertTrue(all(strictly_inside(seed, radius) for seed, radius in zip(seeds, radii)))
        self.assertTrue(pairwise_disjoint(seeds, radii))

    def test_selector_ties_nonfinite_and_byte_uniqueness_are_fail_closed(self) -> None:
        required_terms = (
            "duplicate-key-rejecting canonical JSON",
            "Any nonfinite input or nonfinite intermediate is HOLD",
            "negative zero produced anywhere is",
            "Repeated acceptance indices or duplicate full ranks are HOLD",
            "Duplicate indices/objects/ranks are HOLD",
            "A cross-branch candidate collision is HOLD",
            "omega==+0.0",
            "totalOrder",
        )
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, self.flat_text)

    def test_normative_cross_references_and_authorization_are_closed(self) -> None:
        required_terms = (
            "v4 Section 4 is replaced in full by Sections 3--5 below",
            "v4 Section 8.2 is replaced in full by Section 6 below",
            "No imported clause may resolve a reference back into the superseded",
            "The package must pin both the v5 hash and the imported v4 hash",
            "recorded by an external protocol",
            "`M_B` and `M_MC` never pin their respective auditors",
            "AUTHORIZED-SCIENTIFIC-COMMAND: NONE",
            "An independent v5 audit must still confirm `P0=0,P1=0`",
        )
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, self.flat_text)

    def test_mandatory_mutation_decision_table_is_complete_at_design_level(self) -> None:
        required_families = (
            "0.300,0.300,0.304",
            "theta_i-theta_b",
            "reversing `theta_n-theta_p`",
            "one-sided secant",
            "one-ulp boundary fixture",
            "exact rational halfway/one-ulp fixtures",
            "global-box containment and all-pair",
            "FMA-sensitive, signed-zero, subnormal",
            "comparison-record tie",
            "cross-branch collision",
            "Round-67, Round-69, and Round-70",
        )
        for family in required_families:
            with self.subTest(family=family):
                self.assertIn(family, self.text)

    def test_inherited_workload_alpha_power_and_rate_recompute(self) -> None:
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
        self.assertEqual(30 * sum(states), 789_995_700)
        self.assertEqual(
            Fraction(12, 1200)
            + Fraction(78, 5200)
            + Fraction(84, 5600)
            + Fraction(116, 11600),
            Fraction(1, 20),
        )
        self.assertEqual(2 * (4 + 9 + 4 + 14), 62)

        with localcontext() as context:
            context.prec = 80
            rate = (
                (Decimal("0.01") / Decimal("0.04"))
                * (Decimal(1) + Decimal(2) ** -48)
                * (Decimal(1) / Decimal(3)).exp()
            )
        self.assertLess(rate, Decimal("0.35"))


if __name__ == "__main__":
    unittest.main()
