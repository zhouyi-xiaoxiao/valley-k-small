"""Science-free mutation tests for the frozen Stage-B-v5 T0 package.

All payloads and numerical values in this file are hand-built synthetic
fixtures.  This test never imports or opens Stage-A, Stage-B, FV, off-lattice,
manifest, result, evidence, or manuscript objects.
"""

from __future__ import annotations

import copy
import hashlib
import inspect
import math
import os
import sys
import tempfile
import unittest
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from unittest import mock

selector = sys.modules.get("positive_b_stage_b_t1_selector_v5")
if selector is None:
    raise RuntimeError("tests require the isolated verified-selector bootstrap")

EXPECTED_SYNTHETIC_NORMALIZED_OUTPUT_SHA256 = (
    "ab4f95fec4ea085b91098604ca00c06d382e6b66913e183a7d7a9a14b1a236b6"
)
EXPECTED_SYNTHETIC_NORMALIZED_ROLE_RADIUS_OUTPUT_SHA256 = (
    "44152197d5e0fd16b4d95778169126b00489587c2c5022fb5030a20015d848f9"
)


def hx(value: float) -> str:
    return selector.float_hex(float(value))


def synthetic_selector_payload() -> dict[str, object]:
    """Return the fixed two-branch/count-pair hand fixture."""

    candidates = (
        (10, (-0.04, -0.01), (0.10, 0.20, 0.30, 0.40), 1),
        (11, (-0.04, +0.01), (0.11, 0.19, 0.30, 0.40), 2),
        (20, (+0.01, -0.04), (0.12, 0.18, 0.30, 0.40), 2),
        (21, (-0.01, -0.04), (0.13, 0.17, 0.30, 0.40), 3),
    )

    generation: list[dict[str, object]] = []
    evaluated: list[dict[str, object]] = []
    for index, theta, weights, count in candidates:
        common = {
            "index": index,
            "theta": [hx(theta[0]), hx(theta[1])],
            "weights": [hx(weight) for weight in weights],
        }
        generation.append(copy.deepcopy(common))
        evaluated.append(
            {
                **copy.deepcopy(common),
                "control_gates_passed": True,
                "retained_maximum_count": count,
                "saved_topology": f"synthetic-count-{count}",
                "status": "EVALUATED",
            }
        )

    def node(acceptance_index: int, time: float, theta: tuple[float, float]) -> dict[str, object]:
        return {
            "acceptance_index": acceptance_index,
            "t": hx(time),
            "theta": [hx(theta[0]), hx(theta[1])],
        }

    def branch(branch_id: str, points: tuple[tuple[float, float], ...]) -> dict[str, object]:
        return {
            "branch_id": branch_id,
            "comparison_records": [
                {
                    "acceptance_index": 1,
                    "normalized_fold_residual": hx(0.0),
                    "realized_signed_offset": hx(0.75),
                    "target_offset": hx(0.75),
                }
            ],
            "nodes": [
                node(0, 12.0, points[0]),
                node(1, 13.0, points[1]),
                node(2, 14.0, points[2]),
            ],
            "sigma": 1,
        }

    return {
        "advanced_mesh_97": copy.deepcopy(evaluated),
        "authorization": selector.AUTHORIZATION_NONE,
        "candidate_generation": generation,
        "saved_branches": [
            branch("synthetic-branch-a", ((-0.08, 0.0), (-0.04, 0.0), (0.0, 0.0))),
            branch("synthetic-branch-b", ((0.0, -0.08), (0.0, -0.04), (0.0, 0.0))),
        ],
        "schema": selector.INPUT_SCHEMA,
        "screened_mesh_65": copy.deepcopy(evaluated),
    }


def synthetic_payload_bytes() -> bytes:
    return selector.canonical_json_bytes(synthetic_selector_payload())


def synthetic_role_seeds() -> list[dict[str, object]]:
    points = (
        (13.00, 0.000, 0.000),
        (12.25, -0.080, -0.020),
        (12.50, -0.060, -0.010),
        (12.75, -0.040, 0.000),
        (13.25, 0.040, 0.000),
        (13.50, 0.060, 0.010),
        (13.75, 0.080, 0.020),
    )
    return [
        {"role_id": role_id, "t": hx(time), "theta": [hx(theta0), hx(theta1)]}
        for role_id, (time, theta0, theta1) in enumerate(points)
    ]


class FrozenRuntimeAndProvenanceTests(unittest.TestCase):
    def test_v5_v4_round73_and_mpfr_bytes_are_exactly_pinned(self) -> None:
        self.assertEqual(
            selector.verify_normative_snapshots(),
            {
                "round_73_acceptance": selector.ROUND73_SHA256,
                "stage_b_v4_import": selector.DESIGN_V4_SHA256,
                "stage_b_v5_design": selector.DESIGN_V5_SHA256,
            },
        )
        runtime = selector.verify_mpfr_runtime()
        self.assertEqual(runtime["gmpy2"], "2.2.1")
        self.assertEqual(runtime["mpfr"], "MPFR 4.2.1")
        self.assertEqual(
            runtime["extension_sha256"],
            "9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b",
        )
        self.assertEqual(
            runtime["package_init_sha256"],
            "3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2",
        )
        self.assertEqual(
            runtime["bundled_libraries_sha256"],
            dict(selector.GMPY2_BUNDLED_LIBRARY_HASHES),
        )
        package = selector.verify_t0_package_runtime()
        self.assertEqual(package["implementation_filename"], Path(selector.__file__).name)
        self.assertEqual(
            package["implementation_sha256"],
            hashlib.sha256(Path(selector.__file__).read_bytes()).hexdigest(),
        )

    def test_final_and_component_symlinks_are_hold(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            target.write_bytes(b"fixed")
            digest = hashlib.sha256(b"fixed").hexdigest()
            link = root / "link"
            link.symlink_to(target)
            with self.assertRaisesRegex(selector.Hold, "symbolic link"):
                selector.snapshot_regular_file(root, link, digest)

            real_dir = root / "real"
            real_dir.mkdir()
            nested = real_dir / "payload"
            nested.write_bytes(b"fixed")
            dir_link = root / "dir-link"
            dir_link.symlink_to(real_dir, target_is_directory=True)
            with self.assertRaisesRegex(selector.Hold, "symbolic link"):
                selector.snapshot_regular_file(root, dir_link / "payload", digest)

    def test_descriptor_copy_replace_restore_attack_is_hold(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "payload"
            path.write_bytes(b"fixed")
            digest = hashlib.sha256(b"fixed").hexdigest()
            original_reader = selector._read_descriptor

            def replace_after_read(descriptor: int, size: int) -> bytes:
                payload = original_reader(descriptor, size)
                replacement = root / "replacement"
                replacement.write_bytes(b"fixed")
                os.replace(replacement, path)
                return payload

            with (
                mock.patch.object(selector, "_read_descriptor", replace_after_read),
                self.assertRaisesRegex(selector.Hold, "changed|replaced"),
            ):
                selector.snapshot_regular_file(root, path, digest)

    def test_hash_and_mpfr_version_drift_are_hold(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "payload"
            path.write_bytes(b"fixed")
            with self.assertRaisesRegex(selector.Hold, "SHA-256"):
                selector.snapshot_regular_file(root, path, "0" * 64)

        with (
            mock.patch.object(selector, "MPFR_VERSION", "MPFR 0.0.0"),
            self.assertRaisesRegex(selector.Hold, "MPFR version drift"),
        ):
            selector.verify_mpfr_runtime()
        selector.verify_mpfr_runtime()

    def test_no_scientific_or_command_entry_exists(self) -> None:
        source = inspect.getsource(selector)
        for forbidden in (
            "positive_b_allocation_cusp_stage_a",
            "positive_b_broad_four_slab",
            "subprocess",
            "numpy",
            "scipy",
            "if __name__",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)
        self.assertEqual(Path(selector.__file__).name, "positive_b_stage_b_t1_selector_v5.py")
        tombstone = Path(selector.__file__).with_name("positive_b_stage_b_t0_selector.py")
        self.assertIn("raise ImportError", tombstone.read_text(encoding="utf-8"))


class ExactBinary64Tests(unittest.TestCase):
    def test_fraction_directed_endpoints_enclose_and_are_adjacent(self) -> None:
        value = Fraction(1, 10)
        lower = selector.down64(value)
        upper = selector.up64(value)
        self.assertLessEqual(selector.exact(lower), value)
        self.assertGreaterEqual(selector.exact(upper), value)
        self.assertEqual(selector.next_up(lower), upper)
        self.assertEqual(selector.rn_fraction(value), upper)

    def test_subnormal_signed_zero_and_nonfinite_boundaries(self) -> None:
        minimum_subnormal = selector.next_up(0.0)
        positive_half = selector.exact(minimum_subnormal) / 2
        negative_half = -positive_half
        self.assertEqual(selector.down64(positive_half), 0.0)
        self.assertEqual(selector.up64(positive_half), minimum_subnormal)
        self.assertEqual(selector.down64(negative_half), -minimum_subnormal)
        self.assertEqual(selector.up64(negative_half), 0.0)
        self.assertEqual(math.copysign(1.0, selector.up64(negative_half)), 1.0)
        self.assertEqual(selector.float_hex(-0.0), "0x0.0p+0")
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(selector.Hold):
                selector.canonical_float(value)

    def test_halfway_ties_are_to_even_and_sqrt_uses_exact_midpoint_check(self) -> None:
        one = 1.0
        next_one = selector.next_up(one)
        midpoint = (selector.exact(one) + selector.exact(next_one)) / 2
        self.assertEqual(selector.rn_fraction(midpoint), one)
        sqrt_argument = midpoint * midpoint
        self.assertEqual(selector._validate_sqrt_candidate(sqrt_argument, one), one)

        odd_lower = next_one
        even_upper = selector.next_up(odd_lower)
        odd_midpoint = (selector.exact(odd_lower) + selector.exact(even_upper)) / 2
        self.assertEqual(selector.rn_fraction(odd_midpoint), even_upper)
        self.assertEqual(
            selector._validate_sqrt_candidate(odd_midpoint * odd_midpoint, odd_lower),
            even_upper,
        )

    def test_mpfr_sqrt_conformance_including_subnormal(self) -> None:
        fixtures = {
            0.0: "0x0.0p+0",
            1.0: "0x1.0000000000000p+0",
            2.0: "0x1.6a09e667f3bcdp+0",
            0.1: "0x1.43d136248490fp-2",
            selector.next_up(0.0): "0x1.0000000000000p-537",
        }
        for value, expected in fixtures.items():
            with self.subTest(value=value):
                self.assertEqual(selector.sqrt_rn(value).hex(), expected)
        with self.assertRaisesRegex(selector.Hold, "sqrt domain"):
            selector.sqrt_rn(-1.0)
        with self.assertRaisesRegex(selector.Hold, "outside finite"):
            selector.rn_fraction(Fraction(2) ** 2000)

    def test_mpfr_log_exp_rn_and_directed_endpoints_are_exercised(self) -> None:
        self.assertEqual(selector.log_rn(1.0), 0.0)
        self.assertEqual(selector.log_down64(1.0), 0.0)
        self.assertEqual(selector.log_up64(1.0), 0.0)
        self.assertEqual(selector.exp_rn(0.0), 1.0)
        self.assertEqual(selector.exp_down64(0.0), 1.0)
        self.assertEqual(selector.exp_up64(0.0), 1.0)

        log_lower = selector.log_down64(2.0)
        log_nearest = selector.log_rn(2.0)
        log_upper = selector.log_up64(2.0)
        self.assertEqual(log_nearest.hex(), "0x1.62e42fefa39efp-1")
        self.assertEqual(log_lower, log_nearest)
        self.assertEqual(selector.next_up(log_lower), log_upper)

        exp_lower = selector.exp_down64(1.0)
        exp_nearest = selector.exp_rn(1.0)
        exp_upper = selector.exp_up64(1.0)
        self.assertEqual(exp_nearest.hex(), "0x1.5bf0a8b145769p+1")
        self.assertEqual(exp_lower, exp_nearest)
        self.assertEqual(selector.next_up(exp_lower), exp_upper)

        with self.assertRaisesRegex(selector.Hold, "log domain"):
            selector.log_rn(0.0)
        with self.assertRaisesRegex(selector.Hold, "nonfinite endpoint|outside finite"):
            selector.exp_rn(1000.0)

        for value in (-1000.0, -1.0e20, -float.fromhex("0x1.fffffffffffffp+1023")):
            with self.subTest(value=value):
                self.assertEqual(selector.exp_rn(value), 0.0)
                self.assertEqual(selector.exp_down64(value), 0.0)
                self.assertEqual(selector.exp_up64(value), selector.MIN_SUBNORMAL)

        original_context = selector.gmpy2.context(selector.gmpy2.get_context())
        try:
            selector.gmpy2.get_context().precision = 17
            selector.gmpy2.get_context().round = selector.gmpy2.RoundUp
            self.assertEqual(selector.log_rn(2.0).hex(), "0x1.62e42fefa39efp-1")
            self.assertEqual(selector.exp_rn(1.0).hex(), "0x1.5bf0a8b145769p+1")
        finally:
            selector.gmpy2.set_context(original_context)

    def test_fma_sensitive_dot_uses_written_multiply_multiply_add_trace(self) -> None:
        left = (
            float.fromhex("0x1.ffffffa000000p-1"),
            float.fromhex("-0x1.000002e000000p+0"),
        )
        right = (
            float.fromhex("-0x1.0000057000000p+0"),
            float.fromhex("-0x1.fffffc6000000p-1"),
        )
        separate = selector.dot2_rn(left, right)
        fused = selector.rn_fraction(
            selector.exact(left[0]) * selector.exact(right[0])
            + selector.exact(left[1]) * selector.exact(right[1])
        )
        self.assertEqual(separate.hex(), "-0x1.0c00010c00000p-22")
        self.assertEqual(fused.hex(), "-0x1.0c00010c40000p-22")
        self.assertNotEqual(separate, fused)


class Round70AndRound73OddGateTests(unittest.TestCase):
    def test_round70_jump_is_rejected_and_two_positive_controls_pass(self) -> None:
        self.assertFalse(selector.odd_gate_scalar((0.300, 0.300), (0.300, 0.300), (0.304, 0.304)))
        self.assertTrue(selector.odd_gate_scalar((0.3, 0.3), (0.3, 0.3), (0.3, 0.3)))
        self.assertTrue(selector.odd_gate_scalar((0.0, 0.0), (0.4, 0.4), (0.5, 0.5)))

    def test_round73_half_ulp_native_rn_alias_is_rejected(self) -> None:
        half_floor = selector.ODD_FLOOR / 2.0
        next_half = selector.next_up(half_floor)
        coarse = (half_floor, half_floor)
        middle = (-next_half, -next_half)
        fine = coarse
        exact_gap = selector.exact(half_floor) + selector.exact(next_half)
        next_floor = selector.next_up(selector.ODD_FLOOR)
        self.assertEqual(
            exact_gap,
            (selector.exact(selector.ODD_FLOOR) + selector.exact(next_floor)) / 2,
        )
        self.assertEqual(selector.dplus(middle, coarse), next_floor)
        native_gap = abs(middle[0] - coarse[1])
        self.assertEqual(native_gap, selector.ODD_FLOOR)
        self.assertFalse(selector.odd_gate_scalar(coarse, middle, fine))

    def test_vector_bad_coordinate_and_grid_order_mutation_fail(self) -> None:
        coarse = ((0.1, 0.1), (0.300, 0.300))
        middle = ((0.1, 0.1), (0.300, 0.300))
        fine = ((0.1, 0.1), (0.304, 0.304))
        self.assertFalse(selector.odd_gate_vector(coarse, middle, fine))

        contraction = ((0.0, 0.0), (0.4, 0.4), (0.5, 0.5))
        self.assertTrue(selector.odd_gate_scalar(*contraction))
        self.assertFalse(selector.odd_gate_scalar(contraction[2], contraction[1], contraction[0]))
        with self.assertRaises(TypeError):
            selector.odd_gate_scalar(contraction[0], contraction[1])  # type: ignore[call-arg]

    def test_malformed_and_nonfinite_intervals_hold(self) -> None:
        for interval in ((1.0, 0.0), (0.0, math.nan), (0.0, math.inf)):
            with self.subTest(interval=interval), self.assertRaises(selector.Hold):
                selector.odd_gate_scalar(interval, (0.0, 0.0), (0.0, 0.0))
        with self.assertRaises(selector.Hold):
            selector.odd_gate_vector((), (), ())


class SavedSelectorTests(unittest.TestCase):
    def test_synthetic_selector_is_deterministic_and_byte_unique(self) -> None:
        output_one = selector.select_saved_controls_bytes(synthetic_payload_bytes())
        output_two = selector.select_saved_controls_bytes(synthetic_payload_bytes())
        self.assertEqual(output_one, output_two)
        decoded = selector.parse_canonical_json_bytes(output_one)
        self.assertEqual(decoded["authorization"], selector.AUTHORIZATION_NONE)
        self.assertEqual(decoded["schema"], selector.OUTPUT_SCHEMA)
        self.assertEqual([branch["count_pair"] for branch in decoded["branches"]], [[1, 2], [2, 3]])
        self.assertEqual(
            [[item["index"] for item in branch["selected"]] for branch in decoded["branches"]],
            [[10, 11], [20, 21]],
        )
        self.assertEqual(
            [[item["side"] for item in branch["selected"]] for branch in decoded["branches"]],
            [["minus", "plus"], ["minus", "plus"]],
        )
        decoded["package_runtime"]["entry"]["external_attestation_sha256"] = "0" * 64
        normalized = selector.canonical_json_bytes(decoded)
        self.assertEqual(
            hashlib.sha256(normalized).hexdigest(),
            EXPECTED_SYNTHETIC_NORMALIZED_OUTPUT_SHA256,
        )

    def test_displacement_is_from_comparison_node_not_any_other_base(self) -> None:
        payload = synthetic_selector_payload()
        candidates = selector._join_candidates(payload)
        frame = selector._comparison_frame(payload["saved_branches"][0], "branch-a")
        self.assertIsNotNone(selector._measure_candidate(candidates[10], frame))
        wrong_bases = (
            frame.previous,
            frame.following,
            (13.0, 0.0, 0.0),
            (13.0, 0.10, 0.10),
            (13.0, -0.10, -0.10),
        )
        for base in wrong_bases:
            with self.subTest(base=base):
                self.assertIsNone(
                    selector._measure_candidate(candidates[10], replace(frame, base=base))
                )

    def test_reversed_secant_and_omitted_orientation_flip_change_labels(self) -> None:
        payload = synthetic_selector_payload()
        candidates = selector._join_candidates(payload)
        branch = payload["saved_branches"][0]
        ordinary = selector._selected_branch(branch, candidates, "ordinary")

        reversed_branch = copy.deepcopy(branch)
        reversed_branch["nodes"][0]["theta"], reversed_branch["nodes"][2]["theta"] = (
            reversed_branch["nodes"][2]["theta"],
            reversed_branch["nodes"][0]["theta"],
        )
        reversed_result = selector._selected_branch(reversed_branch, candidates, "reversed")
        self.assertNotEqual(reversed_result["frame"], ordinary["frame"])
        self.assertEqual(
            [item["index"] for item in reversed_result["selected"]],
            [11, 10],
        )

        negative_sigma = copy.deepcopy(branch)
        negative_sigma["sigma"] = -1
        flipped = selector._selected_branch(negative_sigma, candidates, "negative-sigma")
        self.assertEqual([item["index"] for item in flipped["selected"]], [11, 10])
        no_flip_labels = [item["index"] for item in ordinary["selected"]]
        self.assertNotEqual(no_flip_labels, [item["index"] for item in flipped["selected"]])

    def test_zero_omega_and_one_sided_secant_are_rejected_or_different(self) -> None:
        payload = synthetic_selector_payload()
        branch = payload["saved_branches"][0]
        tied = copy.deepcopy(branch)
        tied["nodes"][2]["t"] = tied["nodes"][0]["t"]
        with self.assertRaisesRegex(selector.Hold, "omega"):
            selector._comparison_frame(tied, "tied")

        curved = copy.deepcopy(branch)
        curved["nodes"][0]["theta"][1] = hx(0.01)
        frame = selector._comparison_frame(curved, "curved")
        node_b = curved["nodes"][1]
        node_n = curved["nodes"][2]
        one_sided = (
            selector.rn_sub(
                selector.parse_float_hex(node_n["theta"][0], "n0"),
                selector.parse_float_hex(node_b["theta"][0], "b0"),
            ),
            selector.rn_sub(
                selector.parse_float_hex(node_n["theta"][1], "n1"),
                selector.parse_float_hex(node_b["theta"][1], "b1"),
            ),
        )
        one_norm = selector.norm2_rn(one_sided)
        one_tangent = (
            selector.rn_div(one_sided[0], one_norm),
            selector.rn_div(one_sided[1], one_norm),
        )
        self.assertNotEqual(frame.tangent, one_tangent)

    def test_ell_subtraction_and_one_ulp_boundary_are_observable(self) -> None:
        frame = selector.Frame(
            tangent=(1.0, 0.0),
            normal=(0.0, 1.0),
            ell=1.0,
            previous=(0.0, 0.0, 0.0),
            base=(1.0, 0.0, 0.0),
            following=(2.0, 0.0, 0.0),
            comparison_rank=(0.0, 0.0, 0),
            acceptance_index=0,
        )
        candidate = {
            "count": 1,
            "index": 1,
            "theta": (hx(0.0), hx(2.0)),
            "topology": "synthetic",
            "weights": (hx(0.1), hx(0.2), hx(0.3), hx(0.4)),
        }
        self.assertIsNotNone(selector._measure_candidate(candidate, frame))
        self.assertIsNone(
            selector._measure_candidate(candidate, replace(frame, ell=selector.next_down(1.0)))
        )
        self.assertEqual(selector.rn_sub(1.0, selector.next_down(1.0)), 2.0**-53)
        self.assertEqual(selector.rn_sub(selector.next_down(1.0), 1.0), -(2.0**-53))

    def test_duplicate_indices_controls_and_records_hold(self) -> None:
        mutations: list[tuple[str, object]] = []

        duplicate_index = synthetic_selector_payload()
        duplicate_index["candidate_generation"].append(
            copy.deepcopy(duplicate_index["candidate_generation"][0])
        )
        mutations.append(("duplicate index", duplicate_index))

        duplicate_controls = synthetic_selector_payload()
        duplicate_controls["candidate_generation"][1]["theta"] = copy.deepcopy(
            duplicate_controls["candidate_generation"][0]["theta"]
        )
        duplicate_controls["candidate_generation"][1]["weights"] = copy.deepcopy(
            duplicate_controls["candidate_generation"][0]["weights"]
        )
        for collection in ("screened_mesh_65", "advanced_mesh_97"):
            duplicate_controls[collection][1]["theta"] = copy.deepcopy(
                duplicate_controls[collection][0]["theta"]
            )
            duplicate_controls[collection][1]["weights"] = copy.deepcopy(
                duplicate_controls[collection][0]["weights"]
            )
        mutations.append(("physical-control bytes", duplicate_controls))

        repeated_record = synthetic_selector_payload()
        repeated_record["saved_branches"][0]["comparison_records"].append(
            copy.deepcopy(repeated_record["saved_branches"][0]["comparison_records"][0])
        )
        mutations.append(("acceptance index", repeated_record))

        for expected, payload in mutations:
            with self.subTest(expected=expected), self.assertRaisesRegex(selector.Hold, expected):
                selector._select_saved_controls(payload)

    def test_sparse_node_ids_use_array_predecessor_and_successor(self) -> None:
        payload = synthetic_selector_payload()
        for branch in payload["saved_branches"]:
            for node, acceptance_index in zip(branch["nodes"], (10, 20, 30), strict=True):
                node["acceptance_index"] = acceptance_index
            branch["comparison_records"][0]["acceptance_index"] = 20
        result = selector._select_saved_controls(payload)
        self.assertEqual(
            [branch["comparison_acceptance_index"] for branch in result["branches"]],
            [20, 20],
        )

    def test_comparison_target_tie_nonfinite_and_signed_zero_fail_closed(self) -> None:
        alternate_target = synthetic_selector_payload()
        alternate_target["saved_branches"][0]["comparison_records"][0]["target_offset"] = "0x1.8p-1"
        with self.assertRaises(selector.Hold):
            selector._select_saved_controls(alternate_target)

        signed_zero = synthetic_selector_payload()
        signed_zero["saved_branches"][0]["comparison_records"][0]["normalized_fold_residual"] = (
            "-0x0.0p+0"
        )
        with self.assertRaises(selector.Hold):
            selector._select_saved_controls(signed_zero)

        for nonfinite in ("inf", "-inf", "nan"):
            payload = synthetic_selector_payload()
            payload["saved_branches"][0]["comparison_records"][0]["realized_signed_offset"] = (
                nonfinite
            )
            with self.subTest(nonfinite=nonfinite), self.assertRaises(selector.Hold):
                selector._select_saved_controls(payload)

    def test_cross_branch_collision_holds_without_later_pair_fallback(self) -> None:
        payload = synthetic_selector_payload()
        # Make 20/21 a worse but still eligible alternative on the same frame.
        # A collision on the first 10/11 pair must HOLD rather than selecting it.
        replacements = {20: (-0.04, -0.015), 21: (-0.04, +0.015)}
        for collection in ("candidate_generation", "screened_mesh_65", "advanced_mesh_97"):
            for record in payload[collection]:
                if record["index"] in replacements:
                    theta = replacements[record["index"]]
                    record["theta"] = [hx(theta[0]), hx(theta[1])]
        second = copy.deepcopy(payload["saved_branches"][0])
        second["branch_id"] = "synthetic-branch-b"
        payload["saved_branches"][1] = second
        with self.assertRaisesRegex(selector.Hold, "cross-branch"):
            selector._select_saved_controls(payload)

    def test_source_join_schema_gates_topology_count_and_authorization_hold(self) -> None:
        cases: list[tuple[str, dict[str, object]]] = []

        missing = synthetic_selector_payload()
        missing["advanced_mesh_97"].pop()
        cases.append(("join", missing))

        mismatch = synthetic_selector_payload()
        mismatch["advanced_mesh_97"][0]["theta"][0] = hx(-0.03)
        cases.append(("theta/weights", mismatch))

        status = synthetic_selector_payload()
        status["screened_mesh_65"][0]["status"] = "SKIPPED"
        cases.append(("evaluated", status))

        gate = synthetic_selector_payload()
        gate["advanced_mesh_97"][0]["control_gates_passed"] = False
        cases.append(("evaluated", gate))

        topology = synthetic_selector_payload()
        topology["advanced_mesh_97"][0]["saved_topology"] = "drift"
        cases.append(("topology", topology))

        count = synthetic_selector_payload()
        count["advanced_mesh_97"][0]["retained_maximum_count"] = 2
        cases.append(("counts", count))

        authorization = synthetic_selector_payload()
        authorization["authorization"] = "GO-FV-STAGE-B"
        cases.append(("authorization", authorization))

        extra = synthetic_selector_payload()
        extra["unexpected"] = True
        cases.append(("schema mismatch", extra))

        for expected, payload in cases:
            with self.subTest(expected=expected), self.assertRaisesRegex(selector.Hold, expected):
                selector._select_saved_controls(payload)


class CanonicalJsonTests(unittest.TestCase):
    def test_duplicate_keys_json_floats_nonfinite_and_whitespace_are_rejected(self) -> None:
        bad_payloads = (
            b'{"a":1,"a":2}',
            b'{"a":1.0}',
            b'{"a":NaN}',
            b'{ "a":1}',
            b'{"a":1}\n',
        )
        for payload in bad_payloads:
            with self.subTest(payload=payload), self.assertRaises(selector.Hold):
                selector.parse_canonical_json_bytes(payload)

    def test_selector_input_and_output_are_unique_canonical_bytes(self) -> None:
        payload = synthetic_payload_bytes()
        self.assertEqual(
            selector.canonical_json_bytes(selector.parse_canonical_json_bytes(payload)), payload
        )
        output = selector.select_saved_controls_bytes(payload)
        self.assertEqual(
            selector.canonical_json_bytes(selector.parse_canonical_json_bytes(output)), output
        )
        self.assertNotIn(b"-0x0", output)
        self.assertNotIn(b"NaN", output)
        self.assertNotIn(b"Infinity", output)


class Round67RoleRadiusTests(unittest.TestCase):
    def test_seven_saved_role_radii_pass_both_outward_postchecks(self) -> None:
        role_input = selector.canonical_json_bytes(
            {
                "authorization": selector.AUTHORIZATION_NONE,
                "role_seeds": synthetic_role_seeds(),
                "schema": selector.ROLE_RADIUS_INPUT_SCHEMA,
            }
        )
        result = selector.parse_canonical_json_bytes(selector.compute_role_radii_bytes(role_input))
        self.assertEqual(result["schema"], selector.ROLE_RADIUS_SCHEMA)
        self.assertEqual(result["authorization"], selector.AUTHORIZATION_NONE)
        self.assertEqual([item["role_id"] for item in result["roles"]], list(range(7)))
        self.assertTrue(
            all(selector.parse_float_hex(item["rho"], "rho") > 0.0 for item in result["roles"])
        )

        promoted = selector.parse_canonical_json_bytes(
            selector.compute_role_radii_bytes(role_input)
        )
        self.assertEqual(promoted, result)
        normalized = copy.deepcopy(result)
        normalized["package_runtime"]["entry"]["external_attestation_sha256"] = "0" * 64
        normalized_bytes = selector.canonical_json_bytes(normalized)
        self.assertEqual(len(normalized_bytes), 5050)
        self.assertEqual(
            hashlib.sha256(normalized_bytes).hexdigest(),
            EXPECTED_SYNTHETIC_NORMALIZED_ROLE_RADIUS_OUTPUT_SHA256,
        )

        wrong_authorization = selector.parse_canonical_json_bytes(role_input)
        wrong_authorization["authorization"] = "GO-FV-STAGE-B"
        with self.assertRaisesRegex(selector.Hold, "authorization"):
            selector.compute_role_radii_bytes(selector.canonical_json_bytes(wrong_authorization))

    def test_one_ulp_pairwise_and_box_touch_mutations_fail(self) -> None:
        safe_radius = selector.next_down(selector.next_down(0.1))
        touching_radius = 0.1
        distance = Fraction(1, 5)
        self.assertLess(
            selector.up64(selector.exact(safe_radius) * 2),
            selector.down64(distance),
        )
        self.assertFalse(
            selector.up64(selector.exact(touching_radius) * 2) < selector.down64(distance)
        )

        theta0 = 0.14
        boundary_gap = selector.exact(selector.THETA_BOUND) - selector.exact(theta0)
        gap_lower = selector.down64(boundary_gap)
        safe_box_radius = gap_lower
        for _ in range(16):
            safe_box_radius = selector.next_down(safe_box_radius)
        self.assertTrue(selector._strictly_inside_role_ball((13.5, theta0, 0.0), safe_box_radius))
        self.assertFalse(
            selector._strictly_inside_role_ball(
                (13.5, theta0, 0.0),
                selector.next_up(safe_box_radius),
            )
        )

    def test_role_seed_schema_order_nonfinite_and_collision_hold(self) -> None:
        unordered = synthetic_role_seeds()
        unordered[0], unordered[1] = unordered[1], unordered[0]
        with self.assertRaisesRegex(selector.Hold, "ascending"):
            selector._compute_role_radii(unordered)

        nonfinite = synthetic_role_seeds()
        nonfinite[0]["t"] = "inf"
        with self.assertRaises(selector.Hold):
            selector._compute_role_radii(nonfinite)

        collision = synthetic_role_seeds()
        collision[1]["t"] = collision[0]["t"]
        collision[1]["theta"] = copy.deepcopy(collision[0]["theta"])
        with self.assertRaisesRegex(selector.Hold, "nonpositive"):
            selector._compute_role_radii(collision)


if __name__ == "__main__":
    unittest.main()
