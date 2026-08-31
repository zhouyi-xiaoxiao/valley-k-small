#!/usr/bin/env python3
"""Result-free F0 v2 resource-envelope and telemetry projection.

This module does not run the numerical worker and cannot authorize F0 or any
science.  It defines the append-only v2 split between deterministic
computational bindings and platform-specific resource telemetry.  A later
sealed wrapper must supply fixed bindings and a later independent verifier
must add authenticated post-job Slurm/cgroup accounting.

Legacy v1 observations are deliberately not accepted as v2 inputs.  In
particular, a historical ``HOLD_F0_METHOD_OR_RESOURCE`` cannot be reinterpreted
as a v2 candidate merely because the v2 limits are larger.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from typing import Final, Mapping


SCHEMA: Final = "f0_platform_telemetry_resource_envelope_v2"
COMPUTATIONAL_SCHEMA: Final = "f0_computational_projection_v2"
MEASUREMENT_SCHEMA: Final = "f0_platform_measurement_v2"
STATUS_CANDIDATE: Final = "PASS_RESOURCE_ENVELOPE_CANDIDATE_NOT_F0"
STATUS_HOLD: Final = "HOLD_F0_RESOURCE_ENVELOPE_V2"

FORMAL_SHAPE: Final = (207, 215, 161)
FORMAL_STATE_COUNT: Final = 7_165_305
FORMAL_TOPOLOGY_EVALUATIONS: Final = 512
FORMAL_TAIL_EVALUATIONS: Final = 4
FORMAL_ACTION_CALLS: Final = 27_018
FORMAL_SCALAR_RECORDS: Final = 27_019
FORMAL_MAXIMUM_POWER: Final = 27_018

MAXIMUM_RSS_BYTES: Final = 32 * 1024**3
MAXIMUM_WORKER_SECONDS: Final = 4_500.0
MAXIMUM_DARWIN_FOOTPRINT_BYTES: Final = 24 * 1024**3
MAXIMUM_SWAP_DELTA: Final = 0

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ARCHITECTURE = re.compile(r"^[a-z0-9_+-]{1,32}$")
_LEGACY_LABEL = re.compile(r"^[A-Za-z0-9_.+-]{1,128}$")
_BINDING_KEYS: Final = frozenset(
    {
        "contract_sha256",
        "executable_sha256",
        "fixture_manifest_sha256",
        "runtime_sha256",
        "source_tree_sha256",
    }
)
_METHOD_COUNTS: Final = {
    "canonical_scalar_record_count": FORMAL_SCALAR_RECORDS,
    "compiled_power_stream_run_count": 1,
    "mandatory_tail_evaluation_count": FORMAL_TAIL_EVALUATIONS,
    "maximum_power_index": FORMAL_MAXIMUM_POWER,
    "p_action_call_count": FORMAL_ACTION_CALLS,
    "repeated_p_actions_during_reevaluation": 0,
    "topology_evaluation_count": FORMAL_TOPOLOGY_EVALUATIONS,
}
_PROMOTION_FLAGS: Final = {
    "authorizes_f0": False,
    "authorizes_f1": False,
    "authorizes_f2": False,
    "authorizes_f3": False,
    "authorizes_manuscript": False,
    "authorizes_remote": False,
    "authorizes_science": False,
    "independent_audit_complete": False,
    "production_resource_gate": False,
    "resource_candidate_only": True,
    "science_executed": False,
}


class ResourceEnvelopeError(ValueError):
    """Canonical v2 input is malformed and must fail closed."""


@dataclass(frozen=True, slots=True)
class PlatformMeasurement:
    """One in-process worker measurement, before post-job accounting."""

    schema: str
    platform: str
    architecture: str
    wall_seconds_hex: str
    peak_rss_bytes: int
    process_swap_delta: int
    worker_exit_code: int
    worker_signal: int | None
    host_peak_footprint_bytes: int | None
    host_peak_footprint_method: str


def canonical_json_bytes(value: object) -> bytes:
    """Return strict ASCII canonical JSON with no trailing newline."""

    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise ResourceEnvelopeError("canonical JSON encoding failed") from error


def strict_json_loads(payload: bytes) -> object:
    """Parse exact canonical JSON and reject duplicate keys/nonfinite values."""

    if type(payload) is not bytes or not payload or len(payload) > 16 * 1024**2:
        raise ResourceEnvelopeError("canonical JSON byte shape is invalid")
    try:
        payload.decode("ascii")
    except UnicodeDecodeError as error:
        raise ResourceEnvelopeError("canonical JSON is not ASCII") from error

    def pairs_hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if type(key) is not str or key in result:
                raise ResourceEnvelopeError("duplicate or non-string JSON key")
            result[key] = value
        return result

    try:
        decoded = json.loads(
            payload,
            object_pairs_hook=pairs_hook,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ResourceEnvelopeError(f"nonfinite JSON token {token}")
            ),
        )
    except ResourceEnvelopeError:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
        raise ResourceEnvelopeError("canonical JSON parse failed") from error
    if canonical_json_bytes(decoded) != payload:
        raise ResourceEnvelopeError("JSON bytes are not canonical")
    return decoded


def _require_plain_int(value: object, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ResourceEnvelopeError(f"{label} is not a bounded plain integer")
    return value


def _require_sha256(value: object, label: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise ResourceEnvelopeError(f"{label} is not lowercase SHA-256")
    return value


def _validate_legacy_label(value: object, label: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str or _LEGACY_LABEL.fullmatch(value) is None:
        raise ResourceEnvelopeError(f"{label} is invalid")
    return value


def _validate_computational_projection(value: object) -> dict[str, object]:
    if type(value) is not dict or set(value) != {
        "bindings",
        "method_counts",
        "schedule_sha256",
        "schema",
        "shape",
        "state_count",
    }:
        raise ResourceEnvelopeError("computational projection key set drifted")
    if value["schema"] != COMPUTATIONAL_SCHEMA:
        raise ResourceEnvelopeError("computational projection schema drifted")
    if value["shape"] != list(FORMAL_SHAPE):
        raise ResourceEnvelopeError("formal shape drifted")
    if value["state_count"] != FORMAL_STATE_COUNT:
        raise ResourceEnvelopeError("formal state count drifted")
    _require_sha256(value["schedule_sha256"], "schedule_sha256")
    bindings = value["bindings"]
    if type(bindings) is not dict or set(bindings) != _BINDING_KEYS:
        raise ResourceEnvelopeError("computational binding key set drifted")
    for key in sorted(_BINDING_KEYS):
        _require_sha256(bindings[key], key)
    if value["method_counts"] != _METHOD_COUNTS:
        raise ResourceEnvelopeError("formal method counts drifted")
    canonical_json_bytes(value)
    return value


def _parse_wall_seconds(value: object) -> float:
    if type(value) is not str:
        raise ResourceEnvelopeError("wall seconds must be hexadecimal text")
    try:
        parsed = float.fromhex(value)
    except ValueError as error:
        raise ResourceEnvelopeError("wall seconds hexadecimal text is invalid") from error
    if (
        not math.isfinite(parsed)
        or parsed < 0
        or parsed.hex() != value
        or value.startswith(("+", "-"))
    ):
        raise ResourceEnvelopeError("wall seconds is noncanonical or unbounded")
    return parsed


def _validate_measurement(value: PlatformMeasurement) -> float:
    if type(value) is not PlatformMeasurement:
        raise ResourceEnvelopeError("measurement type is invalid")
    if value.schema != MEASUREMENT_SCHEMA:
        raise ResourceEnvelopeError("measurement schema drifted")
    if value.platform not in {"darwin", "linux"}:
        raise ResourceEnvelopeError("platform is unsupported")
    if (
        type(value.architecture) is not str
        or _ARCHITECTURE.fullmatch(value.architecture) is None
    ):
        raise ResourceEnvelopeError("architecture is noncanonical")
    wall_seconds = _parse_wall_seconds(value.wall_seconds_hex)
    _require_plain_int(value.peak_rss_bytes, "peak_rss_bytes")
    _require_plain_int(value.process_swap_delta, "process_swap_delta")
    _require_plain_int(value.worker_exit_code, "worker_exit_code")
    if value.worker_signal is not None:
        _require_plain_int(value.worker_signal, "worker_signal", minimum=1)
    if value.host_peak_footprint_bytes is not None:
        _require_plain_int(
            value.host_peak_footprint_bytes,
            "host_peak_footprint_bytes",
        )
    if (
        type(value.host_peak_footprint_method) is not str
        or not value.host_peak_footprint_method
        or len(value.host_peak_footprint_method) > 96
    ):
        raise ResourceEnvelopeError("footprint method is invalid")
    if value.platform == "darwin":
        if (
            value.host_peak_footprint_bytes is None
            or value.host_peak_footprint_method != "darwin_phys_footprint_peak"
        ):
            raise ResourceEnvelopeError(
                "Darwin requires its exact physical-footprint measurement"
            )
    elif value.host_peak_footprint_method not in {
        "host_footprint_tool_unavailable",
        "linux_cgroup_v2_memory_peak",
    }:
        raise ResourceEnvelopeError("Linux footprint method is invalid")
    elif (
        value.host_peak_footprint_method == "host_footprint_tool_unavailable"
        and value.host_peak_footprint_bytes is not None
    ) or (
        value.host_peak_footprint_method == "linux_cgroup_v2_memory_peak"
        and value.host_peak_footprint_bytes is None
    ):
        raise ResourceEnvelopeError("Linux footprint value/method relation drifted")
    return wall_seconds


def _measurement_failures(
    value: PlatformMeasurement,
    wall_seconds: float,
) -> list[str]:
    checks = (
        (wall_seconds <= MAXIMUM_WORKER_SECONDS, "wall_cap_exceeded"),
        (value.peak_rss_bytes <= MAXIMUM_RSS_BYTES, "rss_cap_exceeded"),
        (
            value.process_swap_delta <= MAXIMUM_SWAP_DELTA,
            "process_swap_cap_exceeded",
        ),
        (value.worker_exit_code == 0, "worker_exit_nonzero"),
        (value.worker_signal is None, "worker_signal_observed"),
    )
    failures = [label for passed, label in checks if not passed]
    if (
        value.platform == "darwin"
        and value.host_peak_footprint_bytes is not None
        and value.host_peak_footprint_bytes
        > MAXIMUM_DARWIN_FOOTPRINT_BYTES
    ):
        failures.append("darwin_footprint_cap_exceeded")
    return failures


def build_resource_envelope_candidate(
    computational_projection: Mapping[str, object],
    measurement: PlatformMeasurement,
    *,
    legacy_source_schema: str | None = None,
    legacy_source_status: str | None = None,
) -> dict[str, object]:
    """Build one nonauthorizing result-free v2 envelope candidate.

    Supplying any legacy schema or status forces HOLD.  The caller cannot use
    this function to promote a historical v1 observation.
    """

    projection = _validate_computational_projection(
        dict(computational_projection)
        if isinstance(computational_projection, Mapping)
        else computational_projection
    )
    wall_seconds = _validate_measurement(measurement)
    failures = _measurement_failures(measurement, wall_seconds)
    _validate_legacy_label(legacy_source_schema, "legacy_source_schema")
    _validate_legacy_label(legacy_source_status, "legacy_source_status")
    if legacy_source_schema is not None or legacy_source_status is not None:
        failures.append("legacy_v1_observation_not_reinterpretable")
    failures = sorted(set(failures))

    computational_bytes = canonical_json_bytes(projection)
    telemetry = asdict(measurement)
    telemetry["wall_seconds_upper_bound"] = MAXIMUM_WORKER_SECONDS
    telemetry["rss_bytes_upper_bound"] = MAXIMUM_RSS_BYTES
    telemetry["darwin_footprint_bytes_upper_bound"] = (
        MAXIMUM_DARWIN_FOOTPRINT_BYTES
        if measurement.platform == "darwin"
        else None
    )
    telemetry_bytes = canonical_json_bytes(telemetry)

    result: dict[str, object] = {
        "authority": {
            "certificate": False,
            "execution": False,
            "f0": False,
            "f1": False,
            "f2": False,
            "f3": False,
            "manuscript": False,
            "network": False,
            "remote": False,
            "science": False,
            "slurm": False,
            "ssh": False,
        },
        "computational_projection": projection,
        "computational_projection_sha256": hashlib.sha256(
            computational_bytes
        ).hexdigest(),
        "envelope": {
            "maximum_darwin_footprint_bytes": (
                MAXIMUM_DARWIN_FOOTPRINT_BYTES
            ),
            "maximum_process_swap_delta": MAXIMUM_SWAP_DELTA,
            "maximum_rss_bytes": MAXIMUM_RSS_BYTES,
            "maximum_worker_seconds_hex": MAXIMUM_WORKER_SECONDS.hex(),
            "scheduler_memory_request_bytes": 64 * 1024**3,
            "scheduler_wall_request_seconds": 7_200,
        },
        "failure_reasons": failures,
        "legacy_source_schema": legacy_source_schema,
        "legacy_source_status": legacy_source_status,
        "payload_binding_sha256": "0" * 64,
        "platform_telemetry": telemetry,
        "platform_telemetry_sha256": hashlib.sha256(telemetry_bytes).hexdigest(),
        "post_job_accounting_required": True,
        "promotion_flags": dict(_PROMOTION_FLAGS),
        "schema": SCHEMA,
        "status": STATUS_CANDIDATE if not failures else STATUS_HOLD,
    }
    result["payload_binding_sha256"] = hashlib.sha256(
        canonical_json_bytes(result)
    ).hexdigest()
    return result


def verify_resource_envelope_candidate_bytes(
    payload: bytes,
    *,
    expected_computational_projection_sha256: str,
) -> dict[str, object]:
    """Verify a candidate against one externally frozen projection digest."""

    _require_sha256(
        expected_computational_projection_sha256,
        "expected_computational_projection_sha256",
    )
    decoded = strict_json_loads(payload)
    if type(decoded) is not dict or set(decoded) != {
        "authority",
        "computational_projection",
        "computational_projection_sha256",
        "envelope",
        "failure_reasons",
        "legacy_source_schema",
        "legacy_source_status",
        "payload_binding_sha256",
        "platform_telemetry",
        "platform_telemetry_sha256",
        "post_job_accounting_required",
        "promotion_flags",
        "schema",
        "status",
    }:
        raise ResourceEnvelopeError("candidate key set drifted")
    if (
        decoded["schema"] != SCHEMA
        or decoded["promotion_flags"] != _PROMOTION_FLAGS
        or decoded["post_job_accounting_required"] is not True
        or type(decoded["failure_reasons"]) is not list
        or decoded["failure_reasons"]
        != sorted(set(decoded["failure_reasons"]))
        or any(type(value) is not str for value in decoded["failure_reasons"])
    ):
        raise ResourceEnvelopeError("candidate header drifted")
    if decoded["authority"] != {
        "certificate": False,
        "execution": False,
        "f0": False,
        "f1": False,
        "f2": False,
        "f3": False,
        "manuscript": False,
        "network": False,
        "remote": False,
        "science": False,
        "slurm": False,
        "ssh": False,
    }:
        raise ResourceEnvelopeError("candidate authority drifted")
    _require_sha256(
        decoded["computational_projection_sha256"],
        "computational_projection_sha256",
    )
    computational_projection = _validate_computational_projection(
        decoded["computational_projection"]
    )
    if (
        hashlib.sha256(
            canonical_json_bytes(computational_projection)
        ).hexdigest()
        != decoded["computational_projection_sha256"]
    ):
        raise ResourceEnvelopeError("computational projection binding failed")
    if (
        decoded["computational_projection_sha256"]
        != expected_computational_projection_sha256
    ):
        raise ResourceEnvelopeError(
            "external computational projection binding failed"
        )
    _require_sha256(
        decoded["platform_telemetry_sha256"],
        "platform_telemetry_sha256",
    )
    if decoded["envelope"] != {
        "maximum_darwin_footprint_bytes": MAXIMUM_DARWIN_FOOTPRINT_BYTES,
        "maximum_process_swap_delta": MAXIMUM_SWAP_DELTA,
        "maximum_rss_bytes": MAXIMUM_RSS_BYTES,
        "maximum_worker_seconds_hex": MAXIMUM_WORKER_SECONDS.hex(),
        "scheduler_memory_request_bytes": 64 * 1024**3,
        "scheduler_wall_request_seconds": 7_200,
    }:
        raise ResourceEnvelopeError("candidate envelope drifted")
    telemetry = decoded["platform_telemetry"]
    measurement_keys = {
        "architecture",
        "host_peak_footprint_bytes",
        "host_peak_footprint_method",
        "peak_rss_bytes",
        "platform",
        "process_swap_delta",
        "schema",
        "wall_seconds_hex",
        "worker_exit_code",
        "worker_signal",
    }
    if type(telemetry) is not dict or set(telemetry) != measurement_keys | {
        "darwin_footprint_bytes_upper_bound",
        "rss_bytes_upper_bound",
        "wall_seconds_upper_bound",
    }:
        raise ResourceEnvelopeError("platform telemetry key set drifted")
    if (
        telemetry["rss_bytes_upper_bound"] != MAXIMUM_RSS_BYTES
        or telemetry["wall_seconds_upper_bound"] != MAXIMUM_WORKER_SECONDS
        or telemetry["darwin_footprint_bytes_upper_bound"]
        != (
            MAXIMUM_DARWIN_FOOTPRINT_BYTES
            if telemetry["platform"] == "darwin"
            else None
        )
    ):
        raise ResourceEnvelopeError("platform telemetry envelope drifted")
    measurement = PlatformMeasurement(
        **{key: telemetry[key] for key in measurement_keys}
    )
    wall_seconds = _validate_measurement(measurement)
    if (
        hashlib.sha256(
            canonical_json_bytes(telemetry)
        ).hexdigest()
        != decoded["platform_telemetry_sha256"]
    ):
        raise ResourceEnvelopeError("platform telemetry binding failed")
    observed_binding = _require_sha256(
        decoded["payload_binding_sha256"],
        "payload_binding_sha256",
    )
    provisional = dict(decoded)
    provisional["payload_binding_sha256"] = "0" * 64
    if hashlib.sha256(canonical_json_bytes(provisional)).hexdigest() != observed_binding:
        raise ResourceEnvelopeError("candidate payload binding failed")
    expected_failures = _measurement_failures(measurement, wall_seconds)
    _validate_legacy_label(
        decoded["legacy_source_schema"],
        "legacy_source_schema",
    )
    _validate_legacy_label(
        decoded["legacy_source_status"],
        "legacy_source_status",
    )
    if (
        decoded["legacy_source_schema"] is not None
        or decoded["legacy_source_status"] is not None
    ):
        expected_failures.append("legacy_v1_observation_not_reinterpretable")
    expected_failures = sorted(set(expected_failures))
    if decoded["failure_reasons"] != expected_failures:
        raise ResourceEnvelopeError("candidate findings were not recomputed")
    expected_status = STATUS_CANDIDATE if not expected_failures else STATUS_HOLD
    if decoded["status"] != expected_status:
        raise ResourceEnvelopeError("candidate status/finding relation drifted")
    if (
        decoded["legacy_source_schema"] is not None
        or decoded["legacy_source_status"] is not None
    ) and "legacy_v1_observation_not_reinterpretable" not in decoded[
        "failure_reasons"
    ]:
        raise ResourceEnvelopeError("legacy v1 input was promoted")
    return decoded


__all__ = [
    "COMPUTATIONAL_SCHEMA",
    "FORMAL_SHAPE",
    "FORMAL_STATE_COUNT",
    "MAXIMUM_DARWIN_FOOTPRINT_BYTES",
    "MAXIMUM_RSS_BYTES",
    "MAXIMUM_WORKER_SECONDS",
    "MEASUREMENT_SCHEMA",
    "PlatformMeasurement",
    "ResourceEnvelopeError",
    "SCHEMA",
    "STATUS_CANDIDATE",
    "STATUS_HOLD",
    "build_resource_envelope_candidate",
    "canonical_json_bytes",
    "strict_json_loads",
    "verify_resource_envelope_candidate_bytes",
]
