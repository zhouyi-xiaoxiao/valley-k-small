"""Method-only tests for the isolated compiled off-lattice Doi core."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path

import off_lattice_doi_compiled_core_harness as harness


class CompiledCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="odt-compiled-core-tests-")
        cls.directory = Path(cls._temporary.name)
        cls.binary_o3 = cls.directory / "core_o3"
        cls.binary_o0 = cls.directory / "core_o0"
        cls.build_o3 = harness.build_core(cls.binary_o3, optimization="-O3")
        cls.build_o0 = harness.build_core(cls.binary_o0, optimization="-O0")
        cls.fixtures_o3 = harness.run_fixtures(cls.binary_o3)
        cls.fixtures_o0 = harness.run_fixtures(cls.binary_o0)
        cls.reference = harness.fixture_reference()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def assert_close_ulp(self, observed: float, expected: float, ulps: int = 3) -> None:
        tolerance = ulps * max(math.ulp(observed), math.ulp(expected))
        self.assertLessEqual(abs(observed - expected), tolerance)

    def run_and_summarize(
        self, spec: harness.ChunkSpec, raw: Path, *, binary: Path | None = None
    ) -> tuple[dict, dict]:
        _completed, operational = harness.run_chunk(binary or self.binary_o3, spec, raw)
        self.assertFalse(operational["statistical_estimates_released"])
        forbidden = {
            "reaction_count",
            "censored_count",
            "basin_counts",
            "window_counts",
            "candidate_count_sum",
        }
        self.assertFalse(forbidden.intersection(operational))
        parsed = harness.parse_raw_chunk(raw)
        return operational, harness.summarize_parsed_chunk(parsed)

    def test_compiler_and_source_boundary_are_explicit(self) -> None:
        self.assertEqual(self.build_o3["compiler"]["path"], "/usr/bin/clang++")
        self.assertEqual(
            self.build_o3["compiler"]["sha256"],
            "179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818",
        )
        source = harness.SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "valley_partition",
            "6000000",
            "scientific_seed",
            "scientific_window",
            "mass_detection_power",
            "StageB",
        ):
            self.assertNotIn(forbidden, source)
        harness_source = Path(harness.__file__).read_text(encoding="utf-8")
        self.assertNotIn("6_000_000", harness_source)
        self.assertNotIn("linear_projection_to_6M", harness_source)
        self.assertIn("METHOD_ONLY_OFF_LATTICE_COMPILED_CORE", source)
        self.assertIn("broad-four-slab", source)
        self.assertIn("No clipping to Lambda is permitted", source)
        self.assertIn('production_run_authorized\\":false', source)
        self.assertEqual(
            self.fixtures_o3["core_boundary"],
            "METHOD_ONLY_OFF_LATTICE_COMPILED_CORE",
        )
        self.assertEqual(self.fixtures_o3["schema_version"], 2)

    def test_random123_zero_vector_and_python_raw_reference_match_exactly(self) -> None:
        observed_zero = tuple(
            int(value, 16) for value in self.fixtures_o3["philox_known_zero_vector"]
        )
        self.assertEqual(observed_zero, harness.KNOWN_PHILOX_ZERO_VECTOR)
        self.assertEqual(observed_zero, tuple(self.reference["known_zero"]))
        observed_blocks = [
            tuple(int(value, 16) for value in block) for block in self.fixtures_o3["philox_blocks"]
        ]
        self.assertEqual(observed_blocks, self.reference["blocks"])
        self.assertEqual(
            [int(value, 16) for value in self.fixtures_o3["raw_words"]],
            self.reference["raw_words"],
        )
        self.assertEqual(
            self.fixtures_o3["sha256_abc"],
            hashlib.sha256(b"abc").hexdigest(),
        )

    def test_fixed_transforms_bump_and_exact_transition_match_reference(self) -> None:
        self.assertEqual(self.fixtures_o3["uniform_open_bits"], self.reference["uniform_bits"])
        for bits, expected in zip(
            self.fixtures_o3["exponential_0p13_bits"],
            self.reference["exponentials"],
        ):
            self.assert_close_ulp(harness.bits_hex_to_double(bits), expected)
        for bits, expected in zip(self.fixtures_o3["normal_bits"], self.reference["normals"]):
            self.assert_close_ulp(harness.bits_hex_to_double(bits), expected, ulps=5)
        for observed, (expected_value, expected_attempts) in zip(
            self.fixtures_o3["bump_samples"], self.reference["bumps"]
        ):
            self.assertEqual(observed["attempts"], expected_attempts)
            self.assertEqual(observed["value_bits"], harness.double_bits_hex(expected_value))
            self.assertLess(abs(expected_value), 1.0)
        for bits, expected in zip(
            self.fixtures_o3["fixed_transition_bits"], self.reference["transition"]
        ):
            self.assert_close_ulp(harness.bits_hex_to_double(bits), expected, ulps=4)

    def test_broad_hazard_fixtures_match_independent_scalar_reference(self) -> None:
        observed = self.fixtures_o3["hazard_fixtures"]
        expected = self.reference["hazard_fixtures"]
        self.assertEqual(observed, expected)
        simplex_bound = harness.bits_hex_to_double(
            observed["analytic_simplex_bound_bits"]
        )
        lambda_rate = harness.bits_hex_to_double(observed["broad_lambda_bits"])
        self.assertLess(simplex_bound, lambda_rate)
        self.assertEqual(
            lambda_rate - simplex_bound,
            harness.bits_hex_to_double(observed["simplex_margin_bits"]),
        )
        self.assertGreater(harness.bits_hex_to_double(observed["center_rate_bits"]), 0.0)
        center_rates = [
            harness.bits_hex_to_double(bits) for bits in observed["all_center_rate_bits"]
        ]
        self.assertTrue(all(rate > 0.0 for rate in center_rates))
        for rate, weight in zip(center_rates, (0.4, 0.3, 0.2, 0.1)):
            self.assertAlmostEqual(rate / center_rates[0], weight / 0.4, places=14)
        self.assertGreater(
            harness.bits_hex_to_double(observed["contact_inside_rate_bits"]), 0.0
        )
        for key in (
            "contact_edge_rate_bits",
            "contact_outside_rate_bits",
            "bump_edge_rate_bits",
            "zero_rate_bits",
        ):
            self.assertEqual(observed[key], "0000000000000000")
        self.assertTrue(observed["minimum_image_equal"])
        self.assertEqual(
            observed["near_lambda_guard_bits"],
            harness.double_bits_hex(math.nextafter(harness.BROAD_LAMBDA, 0.0)),
        )
        violation = harness.run_hazard_bound_violation_fixture(self.binary_o3)
        self.assertEqual(violation.returncode, 2)
        self.assertEqual(violation.stdout, "")
        self.assertIn("does not dominate an evaluated hazard", violation.stderr)
        self.assertNotIn("clip", violation.stderr.lower())

    def test_bump_normalization_and_elementary_dominating_bound_are_independent(self) -> None:
        # Composite Simpson quadrature is deliberately independent of the
        # pinned normalizer used by both runtime hazard implementations.
        subintervals = 10_000
        step = 2.0 / subintervals
        weighted_values = []
        for index in range(1, subintervals):
            coordinate = -1.0 + index * step
            value = math.exp(-1.0 / (1.0 - coordinate * coordinate))
            weighted_values.append((4.0 if index % 2 else 2.0) * value)
        quadrature = step * math.fsum(weighted_values) / 3.0
        self.assertLessEqual(abs(quadrature - harness.BASE_BUMP_INTEGRAL), 2.0e-15)

        elementary_lower_bound = math.exp(-4.0 / 3.0)
        self.assertGreaterEqual(harness.BASE_BUMP_INTEGRAL, elementary_lower_bound)
        actual_simplex_peak = (
            harness.BROAD_BUDGET
            * math.exp(-1.0)
            / (
                harness.PATCH_HALF_WIDTH
                * harness.BASE_BUMP_INTEGRAL
                * harness.TRANSVERSE_WIDTH
            )
        )
        elementary_bound = harness.broad_analytic_bound_reference((1.0, 0.0, 0.0, 0.0))
        self.assertLess(actual_simplex_peak, elementary_bound)
        self.assertLess(elementary_bound, harness.BROAD_LAMBDA)

    def test_same_clang_o0_and_o3_fixtures_are_byte_identical(self) -> None:
        self.assertEqual(self.fixtures_o0, self.fixtures_o3)
        spec = harness.synthetic_method_spec(id_count=256, chunk_id=43)
        raw_o0 = self.directory / "optimization_o0.raw"
        raw_o3 = self.directory / "optimization_o3.raw"
        _completed_o0, summary_o0 = harness.run_chunk(self.binary_o0, spec, raw_o0)
        _completed_o3, summary_o3 = harness.run_chunk(self.binary_o3, spec, raw_o3)
        self.assertEqual(summary_o0, summary_o3)
        self.assertEqual(raw_o0.read_bytes(), raw_o3.read_bytes())

    def test_broad_paths_match_python_replay_and_o0_o3_bytes(self) -> None:
        spec = harness.synthetic_broad_spec(id_count=128, chunk_id=49)
        raw_o0 = self.directory / "broad_o0.raw"
        raw_o3 = self.directory / "broad_o3.raw"
        _completed_o0, summary_o0 = harness.run_chunk(self.binary_o0, spec, raw_o0)
        _completed_o3, summary_o3 = harness.run_chunk(self.binary_o3, spec, raw_o3)
        self.assertEqual(summary_o0, summary_o3)
        self.assertEqual(raw_o0.read_bytes(), raw_o3.read_bytes())
        parsed = harness.parse_raw_chunk(raw_o3)
        harness.attest_parsed_chunk(parsed, spec)
        for trajectory_id, event_bits, candidate_count, reacted in parsed["records"]:
            expected_time, expected_candidates, expected_reacted = (
                harness.simulate_trajectory_reference(spec, trajectory_id)
            )
            self.assertEqual(candidate_count, expected_candidates)
            self.assertEqual(reacted, expected_reacted)
            if reacted:
                self.assert_close_ulp(
                    harness.bits_hex_to_double("{:016x}".format(event_bits)),
                    expected_time,
                    ulps=12,
                )
            else:
                self.assertEqual(event_bits, harness.POSITIVE_INFINITY_BITS)

    def test_arbitrary_simplex_weight_inputs_roundtrip_exactly(self) -> None:
        weight_fixtures = (
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
            (0.25, 0.25, 0.25, 0.25),
        )
        for index, weights in enumerate(weight_fixtures):
            spec = harness.synthetic_broad_spec(
                id_count=4,
                chunk_id=100 + index,
                weights=weights,
            )
            raw = self.directory / "arbitrary_weights_{}.raw".format(index)
            _completed, operational = harness.run_chunk(self.binary_o3, spec, raw)
            self.assertFalse(operational["statistical_estimates_released"])
            parsed = harness.parse_raw_chunk(raw)
            harness.attest_parsed_chunk(parsed, spec)
            self.assertEqual(parsed["weights"], list(weights))

    def test_same_ids_exact_rerun_has_identical_raw_bytes_and_hash(self) -> None:
        spec = harness.synthetic_method_spec(id_count=512, chunk_id=44)
        first = self.directory / "same_ids_first.raw"
        second = self.directory / "same_ids_second.raw"
        completed_first, summary_first = harness.run_chunk(self.binary_o3, spec, first)
        completed_second, summary_second = harness.run_chunk(self.binary_o3, spec, second)
        self.assertEqual(completed_first.returncode, completed_second.returncode, 0)
        self.assertEqual(summary_first, summary_second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        parsed = harness.parse_raw_chunk(first)
        self.assertEqual(parsed["sha256"], summary_first["raw_sha256"])
        self.assertEqual(parsed["byte_count"], summary_first["raw_byte_count"])
        self.assertEqual(parsed["id_count"], 512)

    def test_complete_synthetic_paths_match_independent_python_replay(self) -> None:
        spec = harness.synthetic_method_spec(id_count=128, chunk_id=48)
        raw = self.directory / "python_replay.raw"
        harness.run_chunk(self.binary_o3, spec, raw)
        records = harness.parse_raw_chunk(raw)["records"]
        for trajectory_id, event_bits, candidate_count, reacted in records:
            expected_time, expected_candidates, expected_reacted = (
                harness.simulate_constant_hazard_reference(spec, trajectory_id)
            )
            self.assertEqual(candidate_count, expected_candidates)
            self.assertEqual(reacted, expected_reacted)
            if reacted:
                self.assert_close_ulp(
                    harness.bits_hex_to_double("{:016x}".format(event_bits)),
                    expected_time,
                    ulps=12,
                )
            else:
                self.assertEqual(event_bits, harness.POSITIVE_INFINITY_BITS)

    def test_master_seed_and_replicate_id_select_distinct_path_streams(self) -> None:
        base = harness.synthetic_method_spec(id_count=256, chunk_id=45)
        changed_seed = dataclasses.replace(base, master_seed=base.master_seed + 1, chunk_id=46)
        changed_replicate = dataclasses.replace(
            base, replicate_id=base.replicate_id + 1, chunk_id=47
        )
        paths = []
        for label, spec in (
            ("base", base),
            ("seed", changed_seed),
            ("replicate", changed_replicate),
        ):
            raw = self.directory / (label + "_stream.raw")
            harness.run_chunk(self.binary_o3, spec, raw)
            paths.append(harness.parse_raw_chunk(raw)["records"])
        self.assertNotEqual(paths[0], paths[1])
        self.assertNotEqual(paths[0], paths[2])
        self.assertNotEqual(paths[1], paths[2])

    def test_chunk_split_reverse_resume_preserves_every_trajectory(self) -> None:
        whole_spec = harness.synthetic_method_spec(id_count=1000, chunk_id=9)
        first_spec = dataclasses.replace(whole_spec, id_count=333, chunk_id=10)
        second_spec = dataclasses.replace(whole_spec, id_start=333, id_count=667, chunk_id=11)
        whole_path = self.directory / "whole.raw"
        first_path = self.directory / "resume_first.raw"
        second_path = self.directory / "resume_second.raw"
        _whole_operational, whole_summary = self.run_and_summarize(whole_spec, whole_path)
        # Execute the later ID range first to model schedule-independent resume.
        _second_operational, second_summary = self.run_and_summarize(
            second_spec, second_path
        )
        _first_operational, first_summary = self.run_and_summarize(first_spec, first_path)
        whole_records = harness.parse_raw_chunk(whole_path)["records"]
        resumed_records = sorted(
            harness.parse_raw_chunk(first_path)["records"]
            + harness.parse_raw_chunk(second_path)["records"]
        )
        self.assertEqual(whole_records, resumed_records)
        for key in ("reaction_count", "censored_count", "candidate_count_sum"):
            self.assertEqual(whole_summary[key], first_summary[key] + second_summary[key])
        for key in ("basin_counts", "window_counts"):
            combined = [
                left + right for left, right in zip(first_summary[key], second_summary[key])
            ]
            self.assertEqual(whole_summary[key], combined)

    def test_right_censor_and_integer_basin_window_counts_close(self) -> None:
        spec = harness.synthetic_method_spec(id_count=4096, chunk_id=51)
        raw = self.directory / "integer_counts.raw"
        _operational, summary = self.run_and_summarize(spec, raw)
        self.assertEqual(summary["reaction_count"] + summary["censored_count"], spec.id_count)
        self.assertEqual(sum(summary["basin_counts"]), summary["reaction_count"])
        self.assertTrue(all(type(value) is int for value in summary["basin_counts"]))
        self.assertTrue(all(type(value) is int for value in summary["window_counts"]))
        parsed = harness.parse_raw_chunk(raw)
        censored = sum(record[3] == 0 for record in parsed["records"])
        self.assertEqual(censored, summary["censored_count"])

    def test_constant_hazard_survival_matches_analytic_dkw_invariant(self) -> None:
        spec = harness.synthetic_method_spec(id_count=50_000, chunk_id=52)
        raw = self.directory / "constant_invariant.raw"
        _operational, summary = self.run_and_summarize(spec, raw)
        first, second, third = summary["basin_counts"]
        observed = (
            (spec.id_count - first) / spec.id_count,
            (spec.id_count - first - second) / spec.id_count,
            summary["censored_count"] / spec.id_count,
        )
        expected = tuple(math.exp(-spec.constant_hazard * time) for time in (10.0, 30.0, 100.0))
        maximum_error = max(abs(left - right) for left, right in zip(observed, expected))
        dkw_radius = harness.dkw_half_width(spec.id_count, 1.0e-6)
        self.assertLess(maximum_error, dkw_radius)
        event_times = sorted(
            harness.bits_hex_to_double("{:016x}".format(record[1]))
            for record in harness.parse_raw_chunk(raw)["records"]
            if record[3]
        )
        full_ks = 0.0
        for rank, event_time in enumerate(event_times, start=1):
            analytic_cdf = 1.0 - math.exp(-spec.constant_hazard * event_time)
            full_ks = max(
                full_ks,
                rank / spec.id_count - analytic_cdf,
                analytic_cdf - (rank - 1) / spec.id_count,
            )
        full_ks = max(
            full_ks,
            1.0
            - math.exp(-spec.constant_hazard * spec.horizon)
            - len(event_times) / spec.id_count,
        )
        self.assertLess(full_ks, dkw_radius)
        self.assertEqual(first + second + third, summary["reaction_count"])

    def test_zero_hazard_candidate_process_has_poisson_mean_and_variance(self) -> None:
        spec = harness.synthetic_method_spec(
            id_count=10_000,
            chunk_id=53,
            constant_hazard=0.0,
            lambda_rate=0.13,
        )
        raw = self.directory / "candidate_poisson.raw"
        harness.run_chunk(self.binary_o3, spec, raw)
        counts = [record[2] for record in harness.parse_raw_chunk(raw)["records"]]
        observed_mean = sum(counts) / len(counts)
        observed_variance = sum((value - observed_mean) ** 2 for value in counts) / (
            len(counts) - 1
        )
        expected = spec.lambda_rate * spec.horizon
        mean_six_sigma = 6.0 * math.sqrt(expected / spec.id_count)
        variance_six_sigma = 6.0 * expected * math.sqrt(2.0 / (spec.id_count - 1))
        self.assertLess(abs(observed_mean - expected), mean_six_sigma)
        self.assertLess(abs(observed_variance - expected), variance_six_sigma)

    def test_raw_parser_rejects_corrupt_sentinels_times_counts_ids_and_cuts(self) -> None:
        reacting = harness.synthetic_method_spec(
            id_count=8,
            chunk_id=54,
            constant_hazard=0.13,
            lambda_rate=0.13,
        )
        reacting_raw = self.directory / "reacting_for_corruption.raw"
        harness.run_chunk(self.binary_o3, reacting, reacting_raw)
        parsed = harness.parse_raw_chunk(reacting_raw)
        reacted_index = next(index for index, record in enumerate(parsed["records"]) if record[3])
        header_bytes = (
            harness.RAW_FIXED_HEADER_BYTES
            + 8 * len(reacting.weights)
            + 8 * len(reacting.basin_cuts)
            + 16 * len(reacting.windows)
        )
        record_offset = header_bytes + harness.RAW_RECORD_BYTES * reacted_index
        original = reacting_raw.read_bytes()

        corruptions = {
            "nan_event": (record_offset + 8, "<Q", 0x7FF8000000000001),
            "zero_candidate": (record_offset + 16, "<I", 0),
            "wrong_id": (record_offset, "<Q", parsed["records"][reacted_index][0] + 1),
            "nan_cut": (
                harness.RAW_FIXED_HEADER_BYTES + 8 * len(reacting.weights),
                "<Q",
                0x7FF8000000000001,
            ),
        }
        for label, (offset, format_string, value) in corruptions.items():
            payload = bytearray(original)
            struct.pack_into(format_string, payload, offset, value)
            path = self.directory / (label + ".raw")
            path.write_bytes(payload)
            with self.assertRaises(ValueError, msg=label):
                harness.parse_raw_chunk(path)

        censored = dataclasses.replace(reacting, chunk_id=55, constant_hazard=0.0)
        censored_raw = self.directory / "censored_for_corruption.raw"
        harness.run_chunk(self.binary_o3, censored, censored_raw)
        payload = bytearray(censored_raw.read_bytes())
        struct.pack_into("<Q", payload, header_bytes + 8, 0xFFF0000000000000)
        negative_infinity = self.directory / "negative_infinity_sentinel.raw"
        negative_infinity.write_bytes(payload)
        with self.assertRaisesRegex(ValueError, "exact \\+infinity"):
            harness.parse_raw_chunk(negative_infinity)

    def test_raw_parser_rejects_corrupt_broad_mode_bound_and_weights(self) -> None:
        spec = harness.synthetic_broad_spec(id_count=8, chunk_id=56)
        raw = self.directory / "broad_for_corruption.raw"
        harness.run_chunk(self.binary_o3, spec, raw)
        original = raw.read_bytes()
        corruptions = {
            "hazard_mode": (72, "<I", 9),
            "lambda": (
                56,
                "<Q",
                struct.unpack("<Q", struct.pack("<d", 0.34))[0],
            ),
            "constant_field": (
                64,
                "<Q",
                struct.unpack("<Q", struct.pack("<d", 0.01))[0],
            ),
            "negative_weight": (
                harness.RAW_FIXED_HEADER_BYTES,
                "<Q",
                struct.unpack("<Q", struct.pack("<d", -0.1))[0],
            ),
        }
        for label, (offset, format_string, value) in corruptions.items():
            payload = bytearray(original)
            struct.pack_into(format_string, payload, offset, value)
            path = self.directory / ("corrupt_broad_" + label + ".raw")
            path.write_bytes(payload)
            with self.assertRaises(ValueError, msg=label):
                harness.parse_raw_chunk(path)

    def test_bound_violation_and_overwrite_fail_without_partial_estimate(self) -> None:
        invalid = dataclasses.replace(
            harness.synthetic_method_spec(id_count=8, chunk_id=60),
            constant_hazard=0.14,
        )
        invalid_raw = self.directory / "invalid_bound.raw"
        completed, payload = harness.run_chunk(
            self.binary_o3, invalid, invalid_raw, expect_success=False
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(payload, {})
        self.assertIn("does not dominate", completed.stderr)
        self.assertFalse(invalid_raw.exists())
        self.assertEqual(list(self.directory.glob("invalid_bound.raw.partial.*")), [])

        spec = harness.synthetic_method_spec(id_count=32, chunk_id=61)
        existing = self.directory / "append_only.raw"
        _first_completed, first_summary = harness.run_chunk(self.binary_o3, spec, existing)
        original = existing.read_bytes()
        second_completed, second_payload = harness.run_chunk(
            self.binary_o3, spec, existing, expect_success=False
        )
        self.assertEqual(second_completed.returncode, 2)
        self.assertEqual(second_completed.stdout, "")
        self.assertEqual(second_payload, {})
        self.assertEqual(existing.read_bytes(), original)
        self.assertEqual(hashlib.sha256(original).hexdigest(), first_summary["raw_sha256"])
        self.assertEqual(list(self.directory.glob("append_only.raw.partial.*")), [])

    def test_invalid_configs_and_plans_fail_before_any_estimate(self) -> None:
        base = harness.synthetic_method_spec(id_count=8, chunk_id=62)
        invalid_specs = (
            dataclasses.replace(base, chunk_id=63, constant_hazard=math.nan),
            dataclasses.replace(base, chunk_id=64, id_start=harness.UINT64_MAX, id_count=2),
            dataclasses.replace(
                base,
                chunk_id=65,
                windows=((2.0, 4.0), (3.0, 5.0)),
            ),
        )
        for index, spec in enumerate(invalid_specs):
            raw = self.directory / "invalid_config_{}.raw".format(index)
            completed, payload = harness.run_chunk(
                self.binary_o3, spec, raw, expect_success=False
            )
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(payload, {})
            self.assertFalse(raw.exists())
            self.assertEqual(list(self.directory.glob(raw.name + ".partial.*")), [])

        broad = harness.synthetic_broad_spec(id_count=8, chunk_id=80)
        invalid_broad_specs = (
            dataclasses.replace(broad, chunk_id=81, weights=()),
            dataclasses.replace(broad, chunk_id=82, weights=(0.5, 0.3, 0.2)),
            dataclasses.replace(
                broad, chunk_id=83, weights=(-0.1, 0.4, 0.4, 0.3)
            ),
            dataclasses.replace(
                broad, chunk_id=84, weights=(math.nan, 0.3, 0.3, 0.4)
            ),
            dataclasses.replace(broad, chunk_id=85, weights=(0.3, 0.3, 0.2, 0.1)),
            dataclasses.replace(
                broad,
                chunk_id=86,
                lambda_rate=math.nextafter(harness.BROAD_LAMBDA, 0.0),
            ),
            dataclasses.replace(
                broad,
                chunk_id=87,
                lambda_rate=math.nextafter(harness.BROAD_LAMBDA, math.inf),
            ),
            dataclasses.replace(broad, chunk_id=88, constant_hazard=0.01),
            dataclasses.replace(broad, chunk_id=89, constant_hazard=-0.0),
            dataclasses.replace(broad, chunk_id=90, hazard_mode="unknown"),
            dataclasses.replace(
                base,
                chunk_id=91,
                weights=(0.4, 0.3, 0.2, 0.1),
            ),
        )
        for index, spec in enumerate(invalid_broad_specs):
            raw = self.directory / "invalid_broad_config_{}.raw".format(index)
            completed, payload = harness.run_chunk(
                self.binary_o3, spec, raw, expect_success=False
            )
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(payload, {})
            self.assertFalse(raw.exists())
            self.assertEqual(list(self.directory.glob(raw.name + ".partial.*")), [])

        with self.assertRaises(ValueError):
            harness.validate_plan((dataclasses.replace(base, replicate_id=-1),))
        with self.assertRaises(ValueError):
            harness.validate_plan((dataclasses.replace(base, id_count=True),))
        with self.assertRaises(ValueError):
            harness.validate_plan((dataclasses.replace(broad, weights=(1.0, 0.0)),))
        next_chunk = dataclasses.replace(base, chunk_id=66, id_start=9)
        with self.assertRaisesRegex(ValueError, "contiguous"):
            harness.validate_plan((base, next_chunk))
        with self.assertRaises(ValueError):
            harness.dkw_half_width(0, 0.05)
        with self.assertRaises(ValueError):
            harness.dkw_half_width(10, 1.0)

    def test_resume_ledger_releases_counts_only_after_complete_exact_plan(self) -> None:
        first = harness.synthetic_method_spec(id_count=64, chunk_id=70)
        second = dataclasses.replace(first, chunk_id=71, id_start=64)
        specs = (first, second)
        directory = self.directory / "resume_plan"
        ledger = directory / "ledger.json"

        partial = harness.execute_resume_plan(
            self.binary_o3,
            specs,
            directory,
            ledger,
            selected_chunk_ids=(71,),
        )
        self.assertEqual(partial["completed_chunk_ids"], [71])
        self.assertEqual(partial["missing_chunk_ids"], [70])
        self.assertFalse(partial["statistical_estimates_released"])
        with self.assertRaisesRegex(ValueError, "all frozen chunks"):
            harness.finalize_resume_plan(specs, directory, ledger)

        harness.execute_resume_plan(
            self.binary_o3,
            specs,
            directory,
            ledger,
            selected_chunk_ids=(70,),
        )
        complete = harness.finalize_resume_plan(specs, directory, ledger)
        self.assertTrue(complete["statistical_estimates_released"])
        self.assertFalse(complete["scientific_run_authorized"])
        self.assertEqual(complete["trajectory_count"], 128)
        self.assertEqual(
            complete["reaction_count"] + complete["censored_count"],
            complete["trajectory_count"],
        )

        first_raw = harness.raw_path_for_chunk(directory, first.chunk_id)
        original_hash = hashlib.sha256(first_raw.read_bytes()).hexdigest()
        first_raw.unlink()
        resumed = harness.execute_resume_plan(
            self.binary_o3,
            specs,
            directory,
            ledger,
            selected_chunk_ids=(70,),
        )
        self.assertEqual(resumed["missing_chunk_ids"], [])
        self.assertEqual(hashlib.sha256(first_raw.read_bytes()).hexdigest(), original_hash)
        self.assertEqual(harness.finalize_resume_plan(specs, directory, ledger), complete)

        tampered = json.loads(ledger.read_bytes())
        tampered["unexpected"] = True
        harness.atomic_write_json(ledger, tampered)
        with self.assertRaisesRegex(ValueError, "plan changed"):
            harness.finalize_resume_plan(specs, directory, ledger)

    def test_broad_resume_plan_attests_mode_and_weight_bits(self) -> None:
        first = harness.synthetic_broad_spec(id_count=32, chunk_id=90)
        second = dataclasses.replace(first, chunk_id=91, id_start=32)
        specs = (first, second)
        directory = self.directory / "broad_resume_plan"
        ledger = directory / "ledger.json"
        partial = harness.execute_resume_plan(
            self.binary_o3,
            specs,
            directory,
            ledger,
            selected_chunk_ids=(91,),
        )
        self.assertEqual(partial["completed_chunk_ids"], [91])
        self.assertFalse(partial["statistical_estimates_released"])
        harness.execute_resume_plan(
            self.binary_o3,
            specs,
            directory,
            ledger,
            selected_chunk_ids=(90,),
        )
        complete = harness.finalize_resume_plan(specs, directory, ledger)
        self.assertEqual(complete["trajectory_count"], 64)
        self.assertFalse(complete["scientific_run_authorized"])
        ledger_payload = json.loads(ledger.read_bytes())
        self.assertEqual(ledger_payload["schema_version"], 2)
        for chunk in ledger_payload["plan"]["chunks"]:
            self.assertEqual(chunk["hazard_mode"], "broad-four-slab")
            self.assertEqual(
                chunk["weight_bits"],
                [harness.double_bits_hex(weight) for weight in first.weights],
            )

    def test_small_benchmark_is_method_only_and_bounded(self) -> None:
        result = harness.benchmark_core(self.binary_o3, 20_000)
        self.assertEqual(result["stage"], "SMALL_SYNTHETIC_CONSTANT_HAZARD_BENCHMARK_ONLY")
        self.assertGreater(result["trajectories_per_second"], 0.0)
        spec = harness.synthetic_method_spec(id_count=20_000)
        expected_bytes = (
            harness.RAW_FIXED_HEADER_BYTES
            + 8 * len(spec.weights)
            + 8 * len(spec.basin_cuts)
            + 16 * len(spec.windows)
            + 20_000 * harness.RAW_RECORD_BYTES
        )
        self.assertEqual(result["raw_bytes"], expected_bytes)
        self.assertIn("no production-size projection", result["claim_boundary"])
        full_horizon = harness.benchmark_core(
            self.binary_o3,
            2_000,
            constant_hazard=0.0,
            lambda_rate=0.35,
        )
        self.assertEqual(full_horizon["constant_hazard"], 0.0)
        self.assertEqual(full_horizon["lambda"], 0.35)
        self.assertGreater(full_horizon["candidate_count_sum"], result["candidate_count_sum"] // 20)


if __name__ == "__main__":
    unittest.main()
