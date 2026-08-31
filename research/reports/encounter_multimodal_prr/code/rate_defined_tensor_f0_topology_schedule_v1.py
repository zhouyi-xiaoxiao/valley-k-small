#!/usr/bin/env python3
"""Freeze the complete science-free 512-time F0 topology schedule.

The only numerical query sources are the zero-argument analytic and compiled
heterogeneous fixtures in ``rate_defined_tensor_f0_candidate_v1``.  The
remaining points are result-blind absolute dyadic padding generated
left-to-right, beginning with denominator four.  No control, budget,
production configuration, or prospective scientific value is accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Final, Sequence

_SOURCE_PATH: Final = Path(__file__).resolve(strict=True)
_CODE_DIR: Final = _SOURCE_PATH.parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

import rate_defined_tensor_f0_candidate_v1 as candidate  # noqa: E402


class TopologyScheduleFailure(RuntimeError):
    """Fail-closed schedule construction or validation error."""


SCHEMA: Final = "rate_defined_tensor_f0_topology_schedule_v1"
STATUS: Final = "PASS_F0_TOPOLOGY_SCHEDULE_FROZEN_NOT_F0"
STAGE: Final = "F0_SCIENCE_FREE_COMPLETE_QUERY_SCHEDULE"
TOPOLOGY_TIME_COUNT: Final = 512
ANALYTIC_TIME_COUNT: Final = 211
HETEROGENEOUS_TIME_COUNT: Final = 26
REQUIRED_UNION_COUNT: Final = 231
PADDING_COUNT: Final = 281
COMBINED_UNION_COUNT: Final = 515
WINDOW_LOWER: Final = Fraction(1, 2)
WINDOW_UPPER: Final = Fraction(35)
MANDATORY_TAIL_TIMES: Final = (
    Fraction(35),
    Fraction(50),
    Fraction(75),
    Fraction(100),
)
EXPECTED_HASHES: Final = {
    "analytic_times_sha256": (
        "de5841874cd971bb731df76215efd044d94f496ab17a9dbd433ed28c9189a3e2"
    ),
    "heterogeneous_times_sha256": (
        "87ee412ba94dbeb3bdb0b8aa8770ca66ee31f222e73c13b9846db9c2aa74a943"
    ),
    "required_union_sha256": (
        "e7ba95950573919b9ef462c6afb24e560357920cb7c07db9df9ec4f91a1bea1f"
    ),
    "padding_times_sha256": (
        "dd84e3003f3d839ddf3123db121ddc686dc97743846ff814c136de1d7aa1eaa7"
    ),
    "topology_times_sha256": (
        "77b42d12721f3508eb128e2f3866181b372b34fa0d06a8ad7ec9b1ed8f581561"
    ),
}
PROMOTION_FLAGS: Final = {
    "authorizes_f1": False,
    "authorizes_scientific_execution": False,
    "f0_accepted": False,
    "f0_pass": False,
    "positive_budget_primary_controls_evaluated": False,
    "production_resource_gate": False,
    "science_executed": False,
}


def _canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise TopologyScheduleFailure("canonical JSON encoding failed") from error


def _strict_json_loads(payload: bytes) -> object:
    if type(payload) is not bytes or len(payload) > 2_000_000:
        raise TopologyScheduleFailure("schedule byte type or size is invalid")
    try:
        payload.decode("ascii")
    except UnicodeDecodeError as error:
        raise TopologyScheduleFailure("schedule is not ASCII") from error

    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if type(key) is not str or key in result:
                raise TopologyScheduleFailure(
                    "schedule has a duplicate or non-string key"
                )
            result[key] = value
        return result

    try:
        return json.loads(
            payload,
            object_pairs_hook=object_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"nonfinite token {token}")
            ),
        )
    except TopologyScheduleFailure:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        raise TopologyScheduleFailure("schedule JSON is invalid") from error


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _fraction_payload(value: Fraction) -> dict[str, int]:
    if type(value) is not Fraction:
        raise TopologyScheduleFailure("schedule time is not an exact Fraction")
    return {
        "denominator": value.denominator,
        "numerator": value.numerator,
    }


def _parse_fraction_text(value: object) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise TopologyScheduleFailure("candidate query time is not rational text")
    numerator, denominator = value.split("/")
    if (
        not numerator.lstrip("-").isdigit()
        or not denominator.isdigit()
        or denominator.startswith("0")
    ):
        raise TopologyScheduleFailure("candidate rational text is malformed")
    result = Fraction(int(numerator), int(denominator))
    if result.denominator <= 0 or _fraction_text(result) != value:
        raise TopologyScheduleFailure("candidate rational text is not canonical")
    return result


def _times_hash(values: Sequence[Fraction]) -> str:
    return hashlib.sha256(
        _canonical_json_bytes([_fraction_payload(value) for value in values])
    ).hexdigest()


def _candidate_query_sets() -> tuple[
    tuple[Fraction, ...],
    tuple[Fraction, ...],
    bytes,
    dict[str, Any],
]:
    candidate_bytes = candidate.canonical_semantic_candidate_bytes()
    payload = candidate.parse_and_validate_semantic_candidate_bytes(
        candidate_bytes
    )
    try:
        analytic_raw = payload["analytic_topology_fixtures"][
            "union_unique_query_times"
        ]
        heterogeneous_raw = payload["integrated_compiled_fixture"][
            "unique_query_times"
        ]
    except (KeyError, TypeError) as error:
        raise TopologyScheduleFailure(
            "candidate query-set fields are missing"
        ) from error
    if type(analytic_raw) is not list or type(heterogeneous_raw) is not list:
        raise TopologyScheduleFailure("candidate query sets are not lists")
    analytic = tuple(_parse_fraction_text(value) for value in analytic_raw)
    heterogeneous = tuple(
        _parse_fraction_text(value) for value in heterogeneous_raw
    )
    if (
        len(analytic) != ANALYTIC_TIME_COUNT
        or len(heterogeneous) != HETEROGENEOUS_TIME_COUNT
        or tuple(sorted(set(analytic))) != analytic
        or tuple(sorted(set(heterogeneous))) != heterogeneous
        or _times_hash(analytic) != EXPECTED_HASHES["analytic_times_sha256"]
        or _times_hash(heterogeneous)
        != EXPECTED_HASHES["heterogeneous_times_sha256"]
    ):
        raise TopologyScheduleFailure("candidate query-set ledger drifted")
    return analytic, heterogeneous, candidate_bytes, payload


def _dyadic_padding(required: set[Fraction]) -> tuple[Fraction, ...]:
    """Return the first 281 unused absolute dyadic grid points."""

    discovered: list[Fraction] = []
    level = 2
    while len(discovered) < PADDING_COUNT:
        denominator = 2**level
        lower_numerator = (WINDOW_LOWER * denominator).numerator
        upper_numerator = (WINDOW_UPPER * denominator).numerator
        for numerator in range(lower_numerator, upper_numerator + 1):
            value = Fraction(numerator, denominator)
            if value in required or value in discovered:
                continue
            discovered.append(value)
            if len(discovered) == PADDING_COUNT:
                break
        level += 1
        if level > 30:
            raise TopologyScheduleFailure("dyadic padding did not terminate")
    result = tuple(sorted(discovered))
    if (
        len(result) != PADDING_COUNT
        or len(set(result)) != PADDING_COUNT
        or _times_hash(result) != EXPECTED_HASHES["padding_times_sha256"]
    ):
        raise TopologyScheduleFailure("dyadic padding ledger drifted")
    return result


def topology_schedule_times() -> tuple[Fraction, ...]:
    """Return the immutable complete 512-time schedule."""

    analytic, heterogeneous, _candidate_bytes, _payload = _candidate_query_sets()
    required = set(analytic) | set(heterogeneous)
    required_sorted = tuple(sorted(required))
    if (
        len(required_sorted) != REQUIRED_UNION_COUNT
        or _times_hash(required_sorted)
        != EXPECTED_HASHES["required_union_sha256"]
        or WINDOW_UPPER in required
    ):
        raise TopologyScheduleFailure("required query union drifted")
    padding = _dyadic_padding(required)
    schedule = tuple(sorted(required | set(padding)))
    if (
        len(schedule) != TOPOLOGY_TIME_COUNT
        or len(set(schedule)) != TOPOLOGY_TIME_COUNT
        or schedule[0] != WINDOW_LOWER
        or schedule[-1] != WINDOW_UPPER
        or WINDOW_UPPER not in padding
        or not required.issubset(schedule)
        or _times_hash(schedule) != EXPECTED_HASHES["topology_times_sha256"]
    ):
        raise TopologyScheduleFailure("complete topology schedule drifted")
    union = set(schedule) | set(MANDATORY_TAIL_TIMES)
    if len(union) != COMBINED_UNION_COUNT:
        raise TopologyScheduleFailure("topology/tail union drifted")
    return schedule


def _payload_without_binding() -> dict[str, object]:
    analytic, heterogeneous, candidate_bytes, candidate_payload = (
        _candidate_query_sets()
    )
    required = tuple(sorted(set(analytic) | set(heterogeneous)))
    padding = _dyadic_padding(set(required))
    schedule = topology_schedule_times()
    source_bindings = candidate_payload["source_bindings"]
    return {
        "candidate_binding": {
            "canonical_candidate_sha256": hashlib.sha256(
                candidate_bytes
            ).hexdigest(),
            "candidate_schema": candidate_payload["schema"],
            "candidate_source_sha256": source_bindings[
                "live_candidate_sources"
            ][0]["sha256"],
            "candidate_test_sha256": source_bindings[
                "live_candidate_sources"
            ][1]["sha256"],
        },
        "counts": {
            "analytic": len(analytic),
            "combined_with_tail": len(
                set(schedule) | set(MANDATORY_TAIL_TIMES)
            ),
            "heterogeneous": len(heterogeneous),
            "padding": len(padding),
            "required_union": len(required),
            "topology": len(schedule),
        },
        "hashes": dict(EXPECTED_HASHES),
        "mandatory_tail_times": [
            _fraction_payload(value) for value in MANDATORY_TAIL_TIMES
        ],
        "padding_recipe": {
            "enumeration": (
                "absolute_dyadic_grids_left_to_right_skip_required_and_seen"
            ),
            "first_denominator": 4,
            "padding_count": PADDING_COUNT,
            "result_order": "strict_fraction_ascending",
            "window": [
                _fraction_payload(WINDOW_LOWER),
                _fraction_payload(WINDOW_UPPER),
            ],
        },
        "padding_times": [_fraction_payload(value) for value in padding],
        "payload_binding_sha256": "0" * 64,
        "promotion_flags": dict(PROMOTION_FLAGS),
        "query_sets": {
            "analytic": [_fraction_payload(value) for value in analytic],
            "heterogeneous": [
                _fraction_payload(value) for value in heterogeneous
            ],
            "required_union": [
                _fraction_payload(value) for value in required
            ],
        },
        "schema": SCHEMA,
        "stage": STAGE,
        "status": STATUS,
        "topology_times": [
            _fraction_payload(value) for value in schedule
        ],
    }


def canonical_topology_schedule_payload() -> dict[str, object]:
    """Build the hash-bound schedule payload."""

    payload = _payload_without_binding()
    payload["payload_binding_sha256"] = hashlib.sha256(
        _canonical_json_bytes(payload)
    ).hexdigest()
    return payload


def canonical_topology_schedule_bytes() -> bytes:
    """Return canonical ASCII schedule bytes."""

    return _canonical_json_bytes(canonical_topology_schedule_payload())


def load_and_validate_canonical_topology_schedule_bytes(
    payload: bytes,
) -> dict[str, object]:
    """Strictly parse and replay the complete schedule."""

    parsed = _strict_json_loads(payload)
    if (
        type(parsed) is not dict
        or _canonical_json_bytes(parsed) != payload
        or parsed != canonical_topology_schedule_payload()
    ):
        raise TopologyScheduleFailure("schedule bytes differ from frozen replay")
    return parsed


def _write_exclusive(path: Path, payload: bytes) -> None:
    if not path.is_absolute() or not path.parent.is_dir():
        raise TopologyScheduleFailure(
            "output must be absolute with an existing parent"
        )
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise TopologyScheduleFailure("output reservation failed") from error
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise TopologyScheduleFailure("output write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    except BaseException:
        os.close(descriptor)
        path.unlink(missing_ok=True)
        raise
    os.close(descriptor)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args(argv)
    payload = canonical_topology_schedule_bytes()
    load_and_validate_canonical_topology_schedule_bytes(payload)
    _write_exclusive(arguments.output, payload)
    print(str(arguments.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
