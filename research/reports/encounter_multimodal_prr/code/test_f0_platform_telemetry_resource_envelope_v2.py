#!/usr/bin/env python3
"""Result-free tests for the F0 v2 resource-envelope projection."""

from __future__ import annotations

import hashlib
import math
import unittest

import f0_platform_telemetry_resource_envelope_v2 as resource


GIB = 1024**3


def projection() -> dict[str, object]:
    return {
        "bindings": {
            "contract_sha256": "1" * 64,
            "executable_sha256": "2" * 64,
            "fixture_manifest_sha256": "3" * 64,
            "runtime_sha256": "4" * 64,
            "source_tree_sha256": "5" * 64,
        },
        "method_counts": {
            "canonical_scalar_record_count": 27_019,
            "compiled_power_stream_run_count": 1,
            "mandatory_tail_evaluation_count": 4,
            "maximum_power_index": 27_018,
            "p_action_call_count": 27_018,
            "repeated_p_actions_during_reevaluation": 0,
            "topology_evaluation_count": 512,
        },
        "schedule_sha256": "6" * 64,
        "schema": resource.COMPUTATIONAL_SCHEMA,
        "shape": [207, 215, 161],
        "state_count": 7_165_305,
    }


def measurement(
    *,
    platform: str = "darwin",
    architecture: str = "arm64",
    wall_seconds: float = resource.MAXIMUM_WORKER_SECONDS,
    peak_rss_bytes: int = resource.MAXIMUM_RSS_BYTES,
    process_swap_delta: int = 0,
    worker_exit_code: int = 0,
    worker_signal: int | None = None,
    host_peak_footprint_bytes: int | None = (
        resource.MAXIMUM_DARWIN_FOOTPRINT_BYTES
    ),
    host_peak_footprint_method: str = "darwin_phys_footprint_peak",
) -> resource.PlatformMeasurement:
    return resource.PlatformMeasurement(
        schema=resource.MEASUREMENT_SCHEMA,
        platform=platform,
        architecture=architecture,
        wall_seconds_hex=wall_seconds.hex(),
        peak_rss_bytes=peak_rss_bytes,
        process_swap_delta=process_swap_delta,
        worker_exit_code=worker_exit_code,
        worker_signal=worker_signal,
        host_peak_footprint_bytes=host_peak_footprint_bytes,
        host_peak_footprint_method=host_peak_footprint_method,
    )


def serialize(candidate: dict[str, object]) -> bytes:
    return resource.canonical_json_bytes(candidate)


def rebind(candidate: dict[str, object]) -> None:
    candidate["payload_binding_sha256"] = "0" * 64
    candidate["payload_binding_sha256"] = hashlib.sha256(
        serialize(candidate)
    ).hexdigest()


class ResourceEnvelopeV2Tests(unittest.TestCase):
    def build(
        self,
        observed: resource.PlatformMeasurement | None = None,
        **legacy: str | None,
    ) -> dict[str, object]:
        return resource.build_resource_envelope_candidate(
            projection(),
            observed if observed is not None else measurement(),
            **legacy,
        )

    def verify(self, candidate: dict[str, object]) -> dict[str, object]:
        return resource.verify_resource_envelope_candidate_bytes(
            serialize(candidate),
            expected_computational_projection_sha256=hashlib.sha256(
                resource.canonical_json_bytes(projection())
            ).hexdigest(),
        )

    def test_exact_boundaries_are_candidate_only_and_nonauthorizing(self) -> None:
        candidate = self.build()
        verified = self.verify(candidate)
        self.assertEqual(candidate, verified)
        self.assertEqual(candidate["status"], resource.STATUS_CANDIDATE)
        self.assertEqual(candidate["failure_reasons"], [])
        self.assertTrue(candidate["post_job_accounting_required"])
        self.assertTrue(
            all(value is False for value in candidate["authority"].values())
        )
        self.assertFalse(candidate["promotion_flags"]["production_resource_gate"])
        self.assertFalse(candidate["promotion_flags"]["independent_audit_complete"])

    def test_every_resource_boundary_fails_closed_one_unit_above(self) -> None:
        cases = (
            (
                measurement(
                    wall_seconds=math.nextafter(
                        resource.MAXIMUM_WORKER_SECONDS,
                        math.inf,
                    )
                ),
                "wall_cap_exceeded",
            ),
            (
                measurement(peak_rss_bytes=resource.MAXIMUM_RSS_BYTES + 1),
                "rss_cap_exceeded",
            ),
            (
                measurement(
                    host_peak_footprint_bytes=(
                        resource.MAXIMUM_DARWIN_FOOTPRINT_BYTES + 1
                    )
                ),
                "darwin_footprint_cap_exceeded",
            ),
            (
                measurement(process_swap_delta=1),
                "process_swap_cap_exceeded",
            ),
            (
                measurement(worker_exit_code=1),
                "worker_exit_nonzero",
            ),
            (
                measurement(worker_signal=9),
                "worker_signal_observed",
            ),
        )
        for observed, expected_reason in cases:
            with self.subTest(expected_reason=expected_reason):
                candidate = self.build(observed)
                self.assertEqual(candidate["status"], resource.STATUS_HOLD)
                self.assertIn(expected_reason, candidate["failure_reasons"])
                self.verify(candidate)

    def test_historical_v1_observations_cannot_be_promoted(self) -> None:
        historical = (
            (2_802.02, 22_913_613_824),
            (2_803.42, 22_932_488_192),
            (2_907.50, 22_941_138_944),
            (2_879.74, 22_907_387_904),
        )
        for wall_seconds, peak_rss_bytes in historical:
            with self.subTest(wall_seconds=wall_seconds):
                candidate = self.build(
                    measurement(
                        wall_seconds=wall_seconds,
                        peak_rss_bytes=peak_rss_bytes,
                        host_peak_footprint_bytes=8 * GIB,
                    ),
                    legacy_source_schema="f0_resource_observation_v1",
                    legacy_source_status="HOLD_F0_METHOD_OR_RESOURCE",
                )
                self.assertEqual(candidate["status"], resource.STATUS_HOLD)
                self.assertEqual(
                    candidate["failure_reasons"],
                    ["legacy_v1_observation_not_reinterpretable"],
                )
                self.verify(candidate)

    def test_linux_telemetry_method_value_relation_is_exact(self) -> None:
        unavailable = measurement(
            platform="linux",
            architecture="aarch64",
            host_peak_footprint_bytes=None,
            host_peak_footprint_method="host_footprint_tool_unavailable",
        )
        cgroup = measurement(
            platform="linux",
            architecture="aarch64",
            host_peak_footprint_bytes=31 * GIB,
            host_peak_footprint_method="linux_cgroup_v2_memory_peak",
        )
        self.verify(self.build(unavailable))
        self.verify(self.build(cgroup))
        invalid_cases = (
            measurement(
                platform="linux",
                architecture="aarch64",
                host_peak_footprint_bytes=1,
                host_peak_footprint_method="host_footprint_tool_unavailable",
            ),
            measurement(
                platform="linux",
                architecture="aarch64",
                host_peak_footprint_bytes=None,
                host_peak_footprint_method="linux_cgroup_v2_memory_peak",
            ),
        )
        for observed in invalid_cases:
            with self.subTest(observed=observed):
                with self.assertRaises(resource.ResourceEnvelopeError):
                    self.build(observed)

    def test_projection_and_measurement_types_are_fail_closed(self) -> None:
        invalid_projection = projection()
        invalid_projection["shape"] = [207, 215, 160]
        with self.assertRaises(resource.ResourceEnvelopeError):
            resource.build_resource_envelope_candidate(
                invalid_projection,
                measurement(),
            )
        with self.assertRaises(resource.ResourceEnvelopeError):
            self.build(measurement(peak_rss_bytes=True))
        invalid_wall = measurement()
        invalid_wall = resource.PlatformMeasurement(
            **{
                **{
                    field: getattr(invalid_wall, field)
                    for field in invalid_wall.__dataclass_fields__
                },
                "wall_seconds_hex": "4500.0",
            }
        )
        with self.assertRaises(resource.ResourceEnvelopeError):
            self.build(invalid_wall)
        with self.assertRaises(resource.ResourceEnvelopeError):
            self.build(legacy_source_schema=True)

    def test_strict_json_rejects_noncanonical_and_duplicate_inputs(self) -> None:
        candidate = self.build()
        payload = serialize(candidate)
        with self.assertRaises(resource.ResourceEnvelopeError):
            resource.verify_resource_envelope_candidate_bytes(
                payload + b"\n",
                expected_computational_projection_sha256=hashlib.sha256(
                    resource.canonical_json_bytes(projection())
                ).hexdigest(),
            )
        duplicate = b'{"schema":"a","schema":"b"}'
        with self.assertRaises(resource.ResourceEnvelopeError):
            resource.strict_json_loads(duplicate)
        with self.assertRaises(resource.ResourceEnvelopeError):
            resource.strict_json_loads(b'{"value":NaN}')
        with self.assertRaises(resource.ResourceEnvelopeError):
            resource.strict_json_loads(b'{"value":"\xc3\xa9"}')

    def test_rebound_finding_status_and_telemetry_tampering_is_rejected(self) -> None:
        candidate = self.build()
        candidate["failure_reasons"] = ["invented"]
        candidate["status"] = resource.STATUS_HOLD
        rebind(candidate)
        with self.assertRaisesRegex(
            resource.ResourceEnvelopeError,
            "findings were not recomputed",
        ):
            self.verify(candidate)

        candidate = self.build()
        candidate["platform_telemetry"]["peak_rss_bytes"] = (
            resource.MAXIMUM_RSS_BYTES + 1
        )
        rebind(candidate)
        with self.assertRaisesRegex(
            resource.ResourceEnvelopeError,
            "platform telemetry binding failed",
        ):
            self.verify(candidate)

        candidate = self.build()
        candidate["computational_projection_sha256"] = "f" * 64
        rebind(candidate)
        with self.assertRaisesRegex(
            resource.ResourceEnvelopeError,
            "computational projection binding failed",
        ):
            self.verify(candidate)

        candidate = self.build()
        candidate["computational_projection"]["bindings"][
            "runtime_sha256"
        ] = "9" * 64
        candidate["computational_projection_sha256"] = hashlib.sha256(
            resource.canonical_json_bytes(
                candidate["computational_projection"]
            )
        ).hexdigest()
        rebind(candidate)
        with self.assertRaisesRegex(
            resource.ResourceEnvelopeError,
            "external computational projection binding failed",
        ):
            self.verify(candidate)

    def test_serialization_is_deterministic_and_does_not_execute_science(self) -> None:
        first = serialize(self.build())
        second = serialize(self.build())
        self.assertEqual(first, second)
        self.assertFalse(first.endswith(b"\n"))
        self.assertNotIn(b"science_executed\":true", first)
        self.assertNotIn(b"authorizes_remote\":true", first)


if __name__ == "__main__":
    unittest.main(verbosity=2)
