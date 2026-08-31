"""Science-free executable regressions for the Stage-B-v5 design repair."""

from __future__ import annotations

import hashlib
import math
import unittest
from fractions import Fraction
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]
DESIGN = REPORT / "notes" / "positive_b_stage_b_validation_design_v5.md"
V4_DESIGN = REPORT / "notes" / "positive_b_stage_b_validation_design_v4.md"
ROUND70 = REPORT / "audits" / "round_70_stageb_v4_independent_attack.md"

EXPECTED_DESIGN_SHA256 = "136085075ad23fc22a40cf03725c9151f11ff356cff4f6f39e5c5fbb24317ddd"
EXPECTED_V4_SHA256 = "e5ca55c8a63d72b8f1bb0ded4d6ebba29a75d94e96ce07a6b7ebf15dcf100691"
EXPECTED_ROUND70_SHA256 = "0fa94a3d94db356e81f62746f267743bbc3f431dc82959894d00b88a9bea9c62"

ODD_FLOOR = float.fromhex("0x1.ad7f29abcaf48p-25")
TIME_SCALE = float.fromhex("0x1.1400000000000p+5")
THETA_BOUND = float.fromhex("0x1.3333333333333p-3")
RHO_CAP = float.fromhex("0x1.0000000000000p-7")

Interval = tuple[float, float]
Point = tuple[float, float, float]
Theta = tuple[float, float]


class Hold(ValueError):
    """A science-free fixture reached a fail-closed selector boundary."""


def exact(value: float) -> Fraction:
    return Fraction.from_float(value)


def down64_fraction(value: Fraction) -> float:
    """Greatest finite binary64 not above an exact rational."""
    rounded = float(value)
    if not math.isfinite(rounded):
        raise Hold("nonfinite directed endpoint")
    if exact(rounded) > value:
        rounded = math.nextafter(rounded, -math.inf)
    return 0.0 if rounded == 0.0 else rounded


def up64_fraction(value: Fraction) -> float:
    """Least finite binary64 not below an exact rational."""
    rounded = float(value)
    if not math.isfinite(rounded):
        raise Hold("nonfinite directed endpoint")
    if exact(rounded) < value:
        rounded = math.nextafter(rounded, math.inf)
    return 0.0 if rounded == 0.0 else rounded


def discrepancy_upper(left: Interval, right: Interval) -> float:
    return max(abs(left[0] - right[1]), abs(left[1] - right[0]))


def distance_lower(left: Interval, right: Interval) -> float:
    return max(0.0, left[0] - right[1], right[0] - left[1])


def v5_odd_gate(coarse: Interval, middle: Interval, fine: Interval) -> bool:
    """The complete v5 production Boolean, including its floor branch."""
    coarse_plus = discrepancy_upper(middle, coarse)
    fine_plus = discrepancy_upper(fine, middle)
    coarse_minus = distance_lower(middle, coarse)
    return (
        max(coarse_plus, fine_plus) <= ODD_FLOOR
        or fine_plus < coarse_minus
    )


def dot2_rn(left: Theta, right: Theta) -> float:
    p0 = left[0] * right[0]
    p1 = left[1] * right[1]
    return p0 + p1


def norm2_rn(vector: Theta) -> float:
    p0 = vector[0] * vector[0]
    p1 = vector[1] * vector[1]
    return math.sqrt(p0 + p1)


def frame(
    previous: Point,
    branch: Point,
    following: Point,
    sigma: int,
) -> tuple[Theta, Theta, float]:
    if sigma not in (-1, 1):
        raise Hold("invalid orientation sign")
    c0 = following[1] - previous[1]
    c1 = following[2] - previous[2]
    dt = following[0] - previous[0]
    omega = float(sigma) * dt
    if not all(math.isfinite(x) for x in (c0, c1, dt, omega)) or omega == 0.0:
        raise Hold("orientation tie or nonfinite frame")
    if omega < 0.0:
        c0 = -c0
        c1 = -c1
    c_norm = norm2_rn((c0, c1))
    if not math.isfinite(c_norm) or c_norm == 0.0:
        raise Hold("zero secant")
    tangent = (c0 / c_norm, c1 / c_norm)
    normal = (-tangent[1], tangent[0])
    vp = (branch[1] - previous[1], branch[2] - previous[2])
    vn = (following[1] - branch[1], following[2] - branch[2])
    ell = min(norm2_rn(vp), norm2_rn(vn))
    if not math.isfinite(ell) or ell <= 0.0:
        raise Hold("nonpositive scale")
    return tangent, normal, ell


def measures(candidate: Theta, base: Theta, tangent: Theta, normal: Theta) -> tuple[float, ...]:
    displacement = (candidate[0] - base[0], candidate[1] - base[1])
    s_value = dot2_rn(normal, displacement)
    q_value = dot2_rn(tangent, displacement)
    radius = norm2_rn(displacement)
    return s_value, q_value, radius


def eligible(values: tuple[float, float, float], ell: float) -> bool:
    s_value, q_value, radius = values
    return (
        radius > 0.0
        and radius <= 2.0 * ell
        and abs(q_value) <= ell / 2.0
        and abs(s_value) >= ell / 16.0
    )


def exact_metric(left: Point, right: Point) -> Fraction:
    return max(
        abs(exact(left[0]) - exact(right[0])) / exact(TIME_SCALE),
        abs(exact(left[1]) - exact(right[1])),
        abs(exact(left[2]) - exact(right[2])),
    )


def directed_role_radii(seeds: tuple[Point, ...]) -> tuple[float, ...]:
    if len(seeds) < 2:
        raise Hold("separation needs at least two seeds")
    radii: list[float] = []
    for index, seed in enumerate(seeds):
        boundary_exact = min(
            (exact(seed[0]) - exact(9.0)) / exact(TIME_SCALE),
            (exact(18.0) - exact(seed[0])) / exact(TIME_SCALE),
            exact(THETA_BOUND) - abs(exact(seed[1])),
            exact(THETA_BOUND) - abs(exact(seed[2])),
        )
        boundary_lo = down64_fraction(boundary_exact)
        separation_lo = min(
            down64_fraction(exact_metric(seed, other))
            for other_index, other in enumerate(seeds)
            if other_index != index
        )
        radius_exact = min(
            exact(RHO_CAP),
            exact(boundary_lo) / 4,
            exact(separation_lo) / 4,
        )
        radius = down64_fraction(radius_exact)
        if min(boundary_lo, separation_lo, radius) <= 0.0:
            raise Hold("nonpositive role radius")
        radii.append(radius)
    return tuple(radii)


def strict_pairwise_disjoint(seeds: tuple[Point, ...], radii: tuple[float, ...]) -> bool:
    for i, left in enumerate(seeds):
        for j in range(i + 1, len(seeds)):
            radius_upper = up64_fraction(exact(radii[i]) + exact(radii[j]))
            separation_lower = down64_fraction(exact_metric(left, seeds[j]))
            if not radius_upper < separation_lower:
                return False
    return True


def strictly_inside_global_box(seed: Point, radius: float) -> bool:
    time_delta = exact(TIME_SCALE) * exact(radius)
    return (
        exact(seed[0]) - time_delta > exact(9.0)
        and exact(seed[0]) + time_delta < exact(18.0)
        and exact(seed[1]) - exact(radius) > -exact(THETA_BOUND)
        and exact(seed[1]) + exact(radius) < exact(THETA_BOUND)
        and exact(seed[2]) - exact(radius) > -exact(THETA_BOUND)
        and exact(seed[2]) + exact(radius) < exact(THETA_BOUND)
    )


class StageBV5DesignResolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = DESIGN.read_text(encoding="utf-8")

    def test_pinned_inputs_and_hash_closed_v4_import(self) -> None:
        self.assertEqual(hashlib.sha256(DESIGN.read_bytes()).hexdigest(), EXPECTED_DESIGN_SHA256)
        self.assertEqual(hashlib.sha256(V4_DESIGN.read_bytes()).hexdigest(), EXPECTED_V4_SHA256)
        self.assertEqual(hashlib.sha256(ROUND70.read_bytes()).hexdigest(), EXPECTED_ROUND70_SHA256)
        self.assertIn("hash-closed normative repair", self.text)
        self.assertIn("v4 Section 4 is replaced in full", self.text)
        self.assertIn("v4 Section 8.2 is replaced in full", self.text)

    def test_round70_floor_bypass_is_rejected_by_complete_gate(self) -> None:
        coarse = (0.300, 0.300)
        middle = (0.300, 0.300)
        fine = (0.304, 0.304)
        reference = (0.302, 0.302)
        e_fv = max(
            discrepancy_upper(interval, reference)
            for interval in (coarse, middle, fine, reference)
        )
        self.assertLessEqual(e_fv, 0.005)
        self.assertFalse(v5_odd_gate(coarse, middle, fine))

        both_at_floor = ((0.3, 0.3), (0.3, 0.3), (0.3, 0.3))
        self.assertTrue(v5_odd_gate(*both_at_floor))

        strict_contraction = ((0.0, 0.0), (0.4, 0.4), (0.5, 0.5))
        self.assertTrue(v5_odd_gate(*strict_contraction))
        self.assertIn("max(D_coarse_plus,D_fine_plus) <= ODD_FLOOR", self.text)

    def test_displacement_base_is_branch_node_not_predecessor(self) -> None:
        previous = (0.0, -1.0, 0.0)
        branch = (1.0, 0.0, 0.0)
        following = (2.0, 1.0, 0.0)
        tangent, normal, ell = frame(previous, branch, following, sigma=1)
        candidate = (0.1, 0.2)

        correct = measures(candidate, branch[1:], tangent, normal)
        mutated = measures(candidate, previous[1:], tangent, normal)
        self.assertTrue(eligible(correct, ell))
        self.assertFalse(eligible(mutated, ell))
        self.assertIn("d0_i = RN(theta_i[0] - theta_b[0])", self.text)

    def test_orientation_sign_and_tie_are_byte_unique(self) -> None:
        previous = (0.0, -1.0, 0.0)
        branch = (1.0, 0.0, 0.0)
        following = (2.0, 1.0, 0.0)
        tangent, normal, _ = frame(previous, branch, following, sigma=-1)
        self.assertEqual(tangent, (-1.0, 0.0))
        self.assertEqual(normal, (-0.0, -1.0))
        self.assertLess(measures((0.0, 0.2), branch[1:], tangent, normal)[0], 0.0)

        tied_following = (0.0, 1.0, 0.0)
        with self.assertRaises(Hold):
            frame(previous, branch, tied_following, sigma=1)
        self.assertIn("omega = RN(float64(sigma) * dt)", self.text)
        self.assertIn("If `omega==+0.0`, return HOLD", self.text)

    def test_exact_ell_operands_reject_a_wrong_long_scale(self) -> None:
        previous = (0.0, -1.0, 0.0)
        branch = (1.0, 0.0, 0.0)
        following = (2.0, 2.0, 0.0)
        tangent, normal, ell = frame(previous, branch, following, sigma=1)
        values = measures((0.8, 0.2), branch[1:], tangent, normal)
        mutated_long_scale = norm2_rn((following[1] - previous[1], 0.0))
        self.assertEqual(ell, 1.0)
        self.assertFalse(eligible(values, ell))
        self.assertTrue(eligible(values, mutated_long_scale))
        self.assertIn("vp0 = RN(theta_b[0] - theta_p[0])", self.text)
        self.assertIn("vn0 = RN(theta_n[0] - theta_b[0])", self.text)

    def test_directed_rounding_is_an_enclosure_not_rn_alias(self) -> None:
        value = Fraction(1, 10)
        rounded = float(value)
        lower = down64_fraction(value)
        upper = up64_fraction(value)
        self.assertLessEqual(exact(lower), value)
        self.assertGreaterEqual(exact(upper), value)
        self.assertEqual(math.nextafter(lower, math.inf), upper)
        self.assertEqual(rounded, upper)
        self.assertGreater(exact(rounded), value)
        self.assertNotEqual(lower, rounded)
        self.assertIn("down64(x) = max {b in B_f : b <= x}", self.text)
        self.assertIn("up64(x)   = min {b in B_f : b >= x}", self.text)
        self.assertIn("Host `libm` is forbidden", self.text)
        self.assertIn("exact integer/rational square comparison", self.text)
        self.assertIn("`log(1)=0` and `exp(0)=1`", self.text)

    def test_directed_role_radii_are_inside_and_pairwise_disjoint(self) -> None:
        seeds = (
            (13.00, 0.000, 0.000),
            (12.25, -0.080, -0.020),
            (12.50, -0.060, -0.010),
            (12.75, -0.040, 0.000),
            (13.25, 0.040, 0.000),
            (13.50, 0.060, 0.010),
            (13.75, 0.080, 0.020),
        )
        radii = directed_role_radii(seeds)
        self.assertTrue(all(0.0 < radius <= RHO_CAP for radius in radii))
        self.assertTrue(all(strictly_inside_global_box(seed, radius) for seed, radius in zip(seeds, radii)))
        self.assertTrue(strict_pairwise_disjoint(seeds, radii))

        # Strictness is observable at a one-ulp boundary: two next-down radii
        # pass, while changing each to the rounded 0.1 touches the separation.
        boundary_seeds = ((13.0, 0.0, 0.0), (13.0, 0.2, 0.0))
        safe_radius = math.nextafter(0.1, 0.0)
        self.assertTrue(strict_pairwise_disjoint(boundary_seeds, (safe_radius, safe_radius)))
        self.assertFalse(strict_pairwise_disjoint(boundary_seeds, (0.1, 0.1)))
        self.assertIn("strictly inside the global box", self.text)

    def test_all_v4_closures_and_arithmetic_are_frozen(self) -> None:
        for term in (
            "abs(qhat_g-qhat_ref)+r_g+r_ref",
            "six-variable joint system",
            "rho_inv",
            "rho_lin",
            "interval-Newton/Krawczyk",
            "E_FV <= min(E_abs,d/4)",
            "not statistical equivalence",
            "fv_acceptance.lower",
            "positive-b-stage-b-v4-off-lattice-sha256-counter-v1",
            "u64be(i) || u64be(j)",
            "AUTHORIZED-SCIENTIFIC-COMMAND: NONE",
        ):
            self.assertIn(term, self.text)

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
        alpha = (
            12 * Fraction(1, 1200)
            + 78 * Fraction(1, 5200)
            + 84 * Fraction(1, 5600)
            + 116 * Fraction(1, 11600)
        )
        self.assertEqual(alpha, Fraction(1, 20))
        self.assertEqual(2 * (4 + 9 + 4 + 14), 62)
        rate = (0.01 / 0.04) * (1.0 + 2.0**-48) * math.exp(1.0 / 3.0)
        self.assertLess(rate, 0.35)


if __name__ == "__main__":
    unittest.main()
