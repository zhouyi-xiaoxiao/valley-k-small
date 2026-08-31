#!/usr/bin/env python3
"""Fail-closed, science-free largest-shape F0 resource runner.

The public runner has exactly one input: an absolute output path.  Every
numerical, topology, precision, and resource literal is internal.  The
largest-shape topology schedule is loaded from the independently frozen
canonical 512-time artifact and contains every analytic and heterogeneous
method-fixture query plus result-blind dyadic padding.

The private small-fixture entry point exists only so the persistence, cap, and
mutation boundaries can be tested without executing 27,018 full-state actions.
Neither the compiled method evidence nor the resource observation can
authorize science, F0, or F1.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
import re
import resource
import subprocess
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Final, Sequence

import numpy as np

_SOURCE_PATH_AT_IMPORT: Final = Path(__file__).resolve(strict=True)
_CODE_DIRECTORY: Final = _SOURCE_PATH_AT_IMPORT.parent
if str(_CODE_DIRECTORY) not in sys.path:
    # ``python -I /absolute/path/to/script.py`` omits the script directory.
    # This fixed insertion enables the required isolated resource process and
    # does not accept a caller-controlled import path.
    sys.path.insert(0, str(_CODE_DIRECTORY))

try:
    import rate_defined_tensor_f0_batched_scalar_uniformization_v1 as batched
    import rate_defined_tensor_f0_compiled_batch_v1 as integrated
    import rate_defined_tensor_f0_compiled_power_stream_v1 as compiled
except ImportError:  # pragma: no cover - package-style import fallback.
    from . import rate_defined_tensor_f0_batched_scalar_uniformization_v1 as batched
    from . import rate_defined_tensor_f0_compiled_batch_v1 as integrated
    from . import rate_defined_tensor_f0_compiled_power_stream_v1 as compiled


SCHEMA: Final = "rate_defined_tensor_f0_resource_v1"
CANONICAL_SCHEMA: Final = "rate_defined_tensor_f0_resource_canonical_v1"
OBSERVATION_SCHEMA: Final = "rate_defined_tensor_f0_resource_observation_v1"
CANONICAL_STATUS: Final = (
    "CANONICAL_METHOD_EVIDENCE_AWAITING_RESOURCE_EVALUATION"
)
PASS_CANDIDATE_STATUS: Final = "PASS_RESOURCE_CANDIDATE_NOT_F0"
HOLD_STATUS: Final = "HOLD_F0_METHOD_OR_RESOURCE"
PRIVATE_STATUS: Final = "PRIVATE_TEST_FIXTURE_COMPLETE_NOT_RESOURCE_CANDIDATE"
PROVISIONAL_SCHEDULE_STATUS: Final = (
    "PROVISIONAL_CONTROL_FREE_PADDING_INTEGRATED_QUERY_SET_NOT_FROZEN"
)
COMPLETE_SCHEDULE_STATUS: Final = "FIXED_COMPLETE_CONTROL_FREE_SCHEDULE"

FORMAL_SHAPE: Final = (207, 215, 161)
FORMAL_PERIODIC: Final = (False, False, True)
FORMAL_STATES: Final = 7_165_305
FORMAL_UNIFORMIZATION_RATE: Final = Fraction(256)
FORMAL_KILLING: Final = Fraction(1, 64)
FORMAL_SERIES_HORIZON: Final = Fraction(100)
FORMAL_TAIL_TOLERANCE: Final = Fraction(1, 10**18)
FORMAL_MPFR_PRECISION_BITS: Final = 192
FORMAL_MAXIMUM_POISSON_TERMS: Final = 200_000
FORMAL_REDUCTION_BLOCK_SIZE: Final = 65_536
FORMAL_EXPECTED_POISSON_MODE: Final = 25_600
FORMAL_EXPECTED_RIGHT_INDEX: Final = 27_014
FORMAL_EXPECTED_MAXIMUM_POWER: Final = 27_018
FORMAL_TOPOLOGY_TIME_COUNT: Final = 512
FORMAL_MANDATORY_TAIL_TIMES: Final = (
    Fraction(35),
    Fraction(50),
    Fraction(75),
    Fraction(100),
)
FORMAL_MAXIMUM_UNION_TIME_COUNT: Final = 515
FORMAL_MAXIMUM_WALL_SECONDS: Final = 3_600
FORMAL_MAXIMUM_RSS_BYTES: Final = 4_294_967_296
FORMAL_MAXIMUM_PEAK_FOOTPRINT_BYTES: Final = 8_589_934_592
FORMAL_MAXIMUM_PROCESS_SWAP_DELTA: Final = 0
FORMAL_MAXIMUM_STATE_RADIUS: Final = Fraction(1, 100_000_000)
FORMAL_TOPOLOGY_SCHEDULE_COMPLETE: Final = True
FORMAL_TOPOLOGY_SCHEDULE_ARTIFACT_SHA256: Final = (
    "b42aa67fa9aa85e4c3c46577e3725ca616ba3ff3de156d77f976a99d0b380344"
)
FORMAL_TOPOLOGY_TIMES_SHA256: Final = (
    "77b42d12721f3508eb128e2f3866181b372b34fa0d06a8ad7ec9b1ed8f581561"
)

MAXIMUM_CANONICAL_BYTES: Final = 768_000_000

_REPORT_DIRECTORY: Final = _CODE_DIRECTORY.parent
_DEPENDENCY_PATHS: Final = {
    "batched_scalar_source": (
        _CODE_DIRECTORY
        / "rate_defined_tensor_f0_batched_scalar_uniformization_v1.py"
    ),
    "batched_scalar_test": (
        _CODE_DIRECTORY
        / "test_rate_defined_tensor_f0_batched_scalar_uniformization_v1.py"
    ),
    "compiled_power_c_source": (
        _CODE_DIRECTORY / "rate_defined_tensor_f0_compiled_power_stream_v1.c"
    ),
    "compiled_power_python_source": (
        _CODE_DIRECTORY / "rate_defined_tensor_f0_compiled_power_stream_v1.py"
    ),
    "compiled_power_test": (
        _CODE_DIRECTORY / "test_rate_defined_tensor_f0_compiled_power_stream_v1.py"
    ),
    "compiled_batch_source": (
        _CODE_DIRECTORY / "rate_defined_tensor_f0_compiled_batch_v1.py"
    ),
    "compiled_batch_test": (
        _CODE_DIRECTORY / "test_rate_defined_tensor_f0_compiled_batch_v1.py"
    ),
    "candidate_freeze": (
        _REPORT_DIRECTORY / "notes/rate_defined_tensor_f0_candidate_v1_freeze.md"
    ),
    "topology_schedule_source": (
        _CODE_DIRECTORY / "rate_defined_tensor_f0_topology_schedule_v1.py"
    ),
    "topology_schedule_test": (
        _CODE_DIRECTORY / "test_rate_defined_tensor_f0_topology_schedule_v1.py"
    ),
    "topology_schedule_artifact": (
        _REPORT_DIRECTORY
        / "artifacts/data/rate_defined_tensor_f0_topology_schedule_v1.json"
    ),
}
_EXPECTED_DEPENDENCY_SHA256: Final = {
    "batched_scalar_source": (
        "56b783f073528146e6cdd3321f078a89978b5e5453b8fdfcabfe35412614b280"
    ),
    "batched_scalar_test": (
        "ddddb839f3b50c1dc2ca05fbce2ddad1b5e025d08f549665585b7a866159dac1"
    ),
    "compiled_power_c_source": (
        "9db8c672a04732b23dedb332854c4f4259911cfac32ec130d1d16b64db274917"
    ),
    "compiled_power_python_source": (
        "13c7fabd4118c3858b03d839dcfea037eb15eb6b64b08f7fb69f0757342eae55"
    ),
    "compiled_power_test": (
        "513c0ce06b4424c4a8c3cf6cfea3bb21cd588fc389af8a9e760e451fb9b6dd51"
    ),
    "compiled_batch_source": (
        "798d605d5cfc79319a633a5f9e487b4da34a55638b534f35804b3636cb402aa7"
    ),
    "compiled_batch_test": (
        "c1a378aa9851335391d3dfd016be8cf7943abfc388754eb9fb5d59c49d941e4e"
    ),
    "candidate_freeze": (
        "0f282f7227220c4a0dc6ae13996ee650759d0cf6679a6d360897929386796d9b"
    ),
    "topology_schedule_source": (
        "f188cbbf7c9e6c31e90ab01c21c9effd334e4ab449102c5501271f83723d2ca7"
    ),
    "topology_schedule_test": (
        "0deed13b23eec298047e290513232094c4ba3ca18db1c8177c6e7e0d7607fcaf"
    ),
    "topology_schedule_artifact": (
        "b42aa67fa9aa85e4c3c46577e3725ca616ba3ff3de156d77f976a99d0b380344"
    ),
}
_SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
_CANONICAL_KEYS: Final = {
    "compiled_batch_evidence",
    "dependencies",
    "fixture",
    "mandatory_tail_evaluations",
    "payload_binding_sha256",
    "promotion_flags",
    "schedule",
    "schema",
    "status",
}
_PROMOTION_FLAGS: Final = {
    "authorizes_f1": False,
    "authorizes_scientific_execution": False,
    "control_exclusion_proved": False,
    "f0_pass": False,
    "independent_audit_complete": False,
    "production_resource_gate": False,
    "production_scale_execution_classified": False,
    "resource_pass": False,
    "science_executed": False,
    "science_free_proved": False,
}


class ResourceRunnerFailure(RuntimeError):
    """Fail-closed resource-runner error."""


@dataclass(frozen=True, slots=True)
class _Fixture:
    name: str
    shape: tuple[int, ...]
    periodic: tuple[bool, ...]
    uniformization_rate: Fraction
    killing: Fraction
    series_horizon: Fraction
    tail_tolerance: Fraction
    mpfr_precision_bits: int
    maximum_poisson_terms: int
    reduction_block_size: int
    topology_times: tuple[Fraction, ...]
    mandatory_tail_times: tuple[Fraction, ...]
    topology_schedule_complete: bool
    expected_poisson_mode: int | None
    expected_right_index: int | None
    expected_maximum_power: int | None
    maximum_union_time_count: int
    maximum_wall_seconds: Fraction
    maximum_rss_bytes: int
    maximum_peak_footprint_bytes: int
    maximum_process_swap_delta: int
    maximum_state_radius: Fraction
    production_scale: bool


def _frozen_control_free_topology_schedule() -> tuple[Fraction, ...]:
    """Strictly load the canonical, hash-pinned complete query schedule."""

    path = _DEPENDENCY_PATHS["topology_schedule_artifact"]
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise ResourceRunnerFailure("frozen topology schedule is unavailable") from error
    if (
        hashlib.sha256(payload).hexdigest()
        != FORMAL_TOPOLOGY_SCHEDULE_ARTIFACT_SHA256
    ):
        raise ResourceRunnerFailure("frozen topology schedule hash drifted")

    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if type(key) is not str or key in result:
                raise ResourceRunnerFailure(
                    "frozen topology schedule has duplicate keys"
                )
            result[key] = value
        return result

    try:
        decoded = json.loads(
            payload,
            object_pairs_hook=object_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"nonfinite token {token}")
            ),
        )
    except ResourceRunnerFailure:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ResourceRunnerFailure("frozen topology schedule JSON is invalid") from error
    if (
        type(decoded) is not dict
        or json.dumps(
            decoded,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        != payload
        or decoded.get("schema")
        != "rate_defined_tensor_f0_topology_schedule_v1"
        or decoded.get("status")
        != "PASS_F0_TOPOLOGY_SCHEDULE_FROZEN_NOT_F0"
        or decoded.get("counts")
        != {
            "analytic": 211,
            "combined_with_tail": 515,
            "heterogeneous": 26,
            "padding": 281,
            "required_union": 231,
            "topology": 512,
        }
        or decoded.get("hashes", {}).get("topology_times_sha256")
        != FORMAL_TOPOLOGY_TIMES_SHA256
        or decoded.get("promotion_flags")
        != {
            "authorizes_f1": False,
            "authorizes_scientific_execution": False,
            "f0_accepted": False,
            "f0_pass": False,
            "positive_budget_primary_controls_evaluated": False,
            "production_resource_gate": False,
            "science_executed": False,
        }
    ):
        raise ResourceRunnerFailure("frozen topology schedule header drifted")
    observed_binding = decoded.get("payload_binding_sha256")
    provisional = dict(decoded)
    provisional["payload_binding_sha256"] = "0" * 64
    if (
        type(observed_binding) is not str
        or observed_binding
        != hashlib.sha256(
            json.dumps(
                provisional,
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("ascii")
        ).hexdigest()
    ):
        raise ResourceRunnerFailure("frozen topology schedule binding drifted")
    raw_times = decoded.get("topology_times")
    raw_tails = decoded.get("mandatory_tail_times")
    if type(raw_times) is not list or type(raw_tails) is not list:
        raise ResourceRunnerFailure("frozen topology schedule rows are invalid")

    def parse_time(value: object) -> Fraction:
        if (
            type(value) is not dict
            or set(value) != {"denominator", "numerator"}
            or type(value["numerator"]) is not int
            or type(value["denominator"]) is not int
            or value["denominator"] <= 0
        ):
            raise ResourceRunnerFailure("frozen topology time is invalid")
        return Fraction(value["numerator"], value["denominator"])

    result = tuple(parse_time(value) for value in raw_times)
    tails = tuple(parse_time(value) for value in raw_tails)
    if (
        len(result) != FORMAL_TOPOLOGY_TIME_COUNT
        or tuple(sorted(set(result))) != result
        or result[0] != Fraction(1, 2)
        or result[-1] != Fraction(35)
        or tails != FORMAL_MANDATORY_TAIL_TIMES
        or len(set(result) | set(tails)) != FORMAL_MAXIMUM_UNION_TIME_COUNT
    ):
        raise ResourceRunnerFailure("frozen topology schedule ledger drifted")
    return result


_FORMAL_FIXTURE: Final = _Fixture(
    name="largest_shape_identity_control_free_v1",
    shape=FORMAL_SHAPE,
    periodic=FORMAL_PERIODIC,
    uniformization_rate=FORMAL_UNIFORMIZATION_RATE,
    killing=FORMAL_KILLING,
    series_horizon=FORMAL_SERIES_HORIZON,
    tail_tolerance=FORMAL_TAIL_TOLERANCE,
    mpfr_precision_bits=FORMAL_MPFR_PRECISION_BITS,
    maximum_poisson_terms=FORMAL_MAXIMUM_POISSON_TERMS,
    reduction_block_size=FORMAL_REDUCTION_BLOCK_SIZE,
    topology_times=_frozen_control_free_topology_schedule(),
    mandatory_tail_times=FORMAL_MANDATORY_TAIL_TIMES,
    topology_schedule_complete=FORMAL_TOPOLOGY_SCHEDULE_COMPLETE,
    expected_poisson_mode=FORMAL_EXPECTED_POISSON_MODE,
    expected_right_index=FORMAL_EXPECTED_RIGHT_INDEX,
    expected_maximum_power=FORMAL_EXPECTED_MAXIMUM_POWER,
    maximum_union_time_count=FORMAL_MAXIMUM_UNION_TIME_COUNT,
    maximum_wall_seconds=Fraction(FORMAL_MAXIMUM_WALL_SECONDS),
    maximum_rss_bytes=FORMAL_MAXIMUM_RSS_BYTES,
    maximum_peak_footprint_bytes=FORMAL_MAXIMUM_PEAK_FOOTPRINT_BYTES,
    maximum_process_swap_delta=FORMAL_MAXIMUM_PROCESS_SWAP_DELTA,
    maximum_state_radius=FORMAL_MAXIMUM_STATE_RADIUS,
    production_scale=True,
)

_SMALL_TEST_FIXTURE: _Fixture = _Fixture(
    name="private_small_identity_fixture_v1",
    shape=(2, 3),
    periodic=(False, True),
    uniformization_rate=Fraction(1),
    killing=Fraction(1, 64),
    series_horizon=Fraction(1),
    tail_tolerance=Fraction(1, 10**12),
    mpfr_precision_bits=192,
    maximum_poisson_terms=2_000,
    reduction_block_size=4,
    topology_times=(Fraction(0), Fraction(1, 2), Fraction(1)),
    mandatory_tail_times=(Fraction(1),),
    topology_schedule_complete=True,
    expected_poisson_mode=None,
    expected_right_index=None,
    expected_maximum_power=None,
    maximum_union_time_count=3,
    maximum_wall_seconds=Fraction(120),
    maximum_rss_bytes=2_000_000_000,
    maximum_peak_footprint_bytes=4_000_000_000,
    maximum_process_swap_delta=0,
    maximum_state_radius=Fraction(1, 1_000_000),
    production_scale=False,
)


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
        raise ResourceRunnerFailure("canonical JSON encoding failed") from error


def _strict_json_loads(payload: bytes) -> object:
    if type(payload) is not bytes or len(payload) > MAXIMUM_CANONICAL_BYTES:
        raise ResourceRunnerFailure("canonical payload type or byte cap is invalid")
    try:
        payload.decode("ascii")
    except UnicodeDecodeError as error:
        raise ResourceRunnerFailure("canonical payload is not ASCII") from error

    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if type(key) is not str or key in result:
                raise ResourceRunnerFailure(
                    "canonical payload has a duplicate or non-string key"
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
    except ResourceRunnerFailure:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        raise ResourceRunnerFailure("canonical payload JSON is invalid") from error


def _builtin(value: object) -> object:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _builtin(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if type(value) is tuple:
        return [_builtin(item) for item in value]
    if type(value) is list:
        return [_builtin(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise ResourceRunnerFailure("built-in payload has a non-string key")
        return {key: _builtin(item) for key, item in value.items()}
    if type(value) is Fraction:
        return {
            "denominator": value.denominator,
            "numerator": value.numerator,
        }
    if type(value) in {str, int, bool} or value is None:
        return value
    raise ResourceRunnerFailure("built-in payload contains an invalid type")


def _stable_file_sha256(path: Path) -> str:
    try:
        before = path.stat()
        payload = path.read_bytes()
        after = path.stat()
    except OSError as error:
        raise ResourceRunnerFailure(f"cannot read pinned dependency {path.name}") from error
    before_identity = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    after_identity = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if (
        before_identity != after_identity
        or before.st_size != len(payload)
        or not path.is_file()
    ):
        raise ResourceRunnerFailure(f"pinned dependency {path.name} changed")
    return hashlib.sha256(payload).hexdigest()


def _observe_dependencies() -> dict[str, dict[str, object]]:
    if set(_DEPENDENCY_PATHS) != set(_EXPECTED_DEPENDENCY_SHA256):
        raise ResourceRunnerFailure("dependency registry key set drifted")
    result: dict[str, dict[str, object]] = {}
    for name in sorted(_DEPENDENCY_PATHS):
        expected = _EXPECTED_DEPENDENCY_SHA256[name]
        observed = _stable_file_sha256(_DEPENDENCY_PATHS[name])
        if (
            type(expected) is not str
            or _SHA256_PATTERN.fullmatch(expected) is None
            or observed != expected
        ):
            raise ResourceRunnerFailure(f"dependency hash mismatch: {name}")
        result[name] = {
            "accepted": True,
            "expected_sha256": expected,
            "observed_sha256": observed,
        }
    return result


def _fraction_payload(value: Fraction) -> dict[str, int]:
    if type(value) is not Fraction:
        raise ResourceRunnerFailure("fixture exact value is not a Fraction")
    return {
        "denominator": value.denominator,
        "numerator": value.numerator,
    }


def _fixture_payload(fixture: _Fixture) -> dict[str, object]:
    return {
        "identity_initial_flat_index": 0,
        "identity_kernel": True,
        "killing": _fraction_payload(fixture.killing),
        "maximum_peak_footprint_bytes": fixture.maximum_peak_footprint_bytes,
        "maximum_poisson_terms": fixture.maximum_poisson_terms,
        "maximum_process_swap_delta": fixture.maximum_process_swap_delta,
        "maximum_rss_bytes": fixture.maximum_rss_bytes,
        "maximum_state_radius": _fraction_payload(
            fixture.maximum_state_radius
        ),
        "maximum_wall_seconds": _fraction_payload(
            fixture.maximum_wall_seconds
        ),
        "mpfr_precision_bits": fixture.mpfr_precision_bits,
        "name": fixture.name,
        "periodic": list(fixture.periodic),
        "production_scale": fixture.production_scale,
        "reduction_block_size": fixture.reduction_block_size,
        "series_horizon": _fraction_payload(fixture.series_horizon),
        "shape": list(fixture.shape),
        "state_count": math.prod(fixture.shape),
        "tail_tolerance": _fraction_payload(fixture.tail_tolerance),
        "uniformization_rate": _fraction_payload(
            fixture.uniformization_rate
        ),
    }


def _schedule_payload(fixture: _Fixture) -> dict[str, object]:
    union = set(fixture.topology_times)
    union.update(fixture.mandatory_tail_times)
    return {
        "artifact_sha256": (
            FORMAL_TOPOLOGY_SCHEDULE_ARTIFACT_SHA256
            if fixture.production_scale
            else None
        ),
        "combined_union_count": len(union),
        "generator": (
            "rate_defined_tensor_f0_topology_schedule_v1"
            if fixture.production_scale
            else "private_small_fixed_schedule_v1"
        ),
        "integrated_query_set_frozen": fixture.topology_schedule_complete,
        "mandatory_tail_times": [
            _fraction_payload(value) for value in fixture.mandatory_tail_times
        ],
        "maximum_union_time_count": fixture.maximum_union_time_count,
        "provisional": not fixture.topology_schedule_complete,
        "status": (
            COMPLETE_SCHEDULE_STATUS
            if fixture.topology_schedule_complete
            else PROVISIONAL_SCHEDULE_STATUS
        ),
        "topology_time_count": len(fixture.topology_times),
        "topology_times": [
            _fraction_payload(value) for value in fixture.topology_times
        ],
    }


def _validate_fixture(fixture: _Fixture) -> None:
    union = set(fixture.topology_times)
    union.update(fixture.mandatory_tail_times)
    fraction_fields = (
        fixture.uniformization_rate,
        fixture.killing,
        fixture.series_horizon,
        fixture.tail_tolerance,
        fixture.maximum_wall_seconds,
        fixture.maximum_state_radius,
    )
    if (
        type(fixture) is not _Fixture
        or type(fixture.name) is not str
        or not fixture.name
        or type(fixture.shape) is not tuple
        or not fixture.shape
        or any(type(value) is not int or value < 2 for value in fixture.shape)
        or type(fixture.periodic) is not tuple
        or len(fixture.periodic) != len(fixture.shape)
        or any(type(value) is not bool for value in fixture.periodic)
        or any(type(value) is not Fraction for value in fraction_fields)
        or fixture.uniformization_rate <= 0
        or fixture.killing < 0
        or fixture.series_horizon <= 0
        or not 0 < fixture.tail_tolerance < 1
        or fixture.maximum_wall_seconds < 0
        or fixture.maximum_state_radius < 0
        or type(fixture.topology_times) is not tuple
        or not fixture.topology_times
        or tuple(sorted(set(fixture.topology_times)))
        != fixture.topology_times
        or type(fixture.mandatory_tail_times) is not tuple
        or not fixture.mandatory_tail_times
        or tuple(sorted(set(fixture.mandatory_tail_times)))
        != fixture.mandatory_tail_times
        or fixture.topology_times[-1] > fixture.series_horizon
        or fixture.mandatory_tail_times[-1] > fixture.series_horizon
        or len(fixture.topology_times) > batched.MAXIMUM_BATCH_TIMES
        or len(union) > fixture.maximum_union_time_count
        or any(
            type(value) is not int or value < 0
            for value in (
                fixture.mpfr_precision_bits,
                fixture.maximum_poisson_terms,
                fixture.reduction_block_size,
                fixture.maximum_union_time_count,
                fixture.maximum_rss_bytes,
                fixture.maximum_peak_footprint_bytes,
                fixture.maximum_process_swap_delta,
            )
        )
        or type(fixture.topology_schedule_complete) is not bool
        or type(fixture.production_scale) is not bool
    ):
        raise ResourceRunnerFailure("fixed fixture is invalid")
    if fixture.production_scale and (
        fixture.shape != FORMAL_SHAPE
        or fixture.periodic != FORMAL_PERIODIC
        or math.prod(fixture.shape) != FORMAL_STATES
        or len(fixture.topology_times) != FORMAL_TOPOLOGY_TIME_COUNT
        or fixture.mandatory_tail_times != FORMAL_MANDATORY_TAIL_TIMES
    ):
        raise ResourceRunnerFailure("production fixture literals drifted")


def _build_identity_backend_and_initial(
    fixture: _Fixture,
) -> tuple[compiled.CompiledPowerStreamBackend, np.ndarray]:
    states = math.prod(fixture.shape)
    p_self = np.ones(states, dtype=np.float64)
    killing = np.full(states, float(fixture.killing), dtype=np.float64)
    p_forward = tuple(
        np.zeros(size, dtype=np.float64) for size in fixture.shape
    )
    p_backward = tuple(
        np.zeros(size, dtype=np.float64) for size in fixture.shape
    )
    generic = compiled.GenericPackedTensorInput(
        tensor_shape=fixture.shape,
        periodic=fixture.periodic,
        p_self_center=p_self,
        p_forward_center=p_forward,
        p_backward_center=p_backward,
        killing_center=killing,
        reduction_block_size=fixture.reduction_block_size,
    )
    backend = compiled.build_compiled_power_stream_backend(generic)
    initial = np.zeros(states, dtype=np.float64)
    initial[0] = 1.0
    initial.setflags(write=False)
    return backend, initial


def _metadata(
    fixture: _Fixture,
) -> integrated.GenericCompiledBatchMethodMetadata:
    return integrated.GenericCompiledBatchMethodMetadata(
        uniformization_rate=fixture.uniformization_rate,
        coefficient_l1_uncertainty_upper=Fraction(0),
        maximum_center_row_sum=Fraction(1),
        maximum_killing_upper=fixture.killing,
        maximum_killing_uncertainty=Fraction(0),
        initial_l1_radius_upper=Fraction(0),
        initial_mass_cap=Fraction(1),
        series_horizon=fixture.series_horizon,
        tail_tolerance=fixture.tail_tolerance,
        mpfr_precision_bits=fixture.mpfr_precision_bits,
        maximum_poisson_terms=fixture.maximum_poisson_terms,
        evaluation_times=fixture.topology_times,
    )


def _peak_rss_bytes(usage: resource.struct_rusage) -> int:
    raw = usage.ru_maxrss
    if type(raw) is int:
        value = raw
    elif type(raw) is float and math.isfinite(raw) and raw.is_integer():
        value = int(raw)
    else:
        raise ResourceRunnerFailure("ru_maxrss is not a finite integer")
    if value < 0:
        raise ResourceRunnerFailure("ru_maxrss is negative")
    return value if sys.platform == "darwin" else value * 1_024


def _process_swap_count(usage: resource.struct_rusage) -> int:
    raw = usage.ru_nswap
    if type(raw) is int:
        value = raw
    elif type(raw) is float and math.isfinite(raw) and raw.is_integer():
        value = int(raw)
    else:
        raise ResourceRunnerFailure("ru_nswap is not a finite integer")
    if value < 0:
        raise ResourceRunnerFailure("ru_nswap is negative")
    return value


def _host_peak_footprint_bytes() -> tuple[int | None, str]:
    tool = Path("/usr/bin/footprint")
    if sys.platform != "darwin" or not tool.is_file():
        return None, "host_footprint_tool_unavailable"
    try:
        process = subprocess.run(
            [
                str(tool),
                "--pid",
                str(os.getpid()),
                "--format",
                "bytes",
                "--noCategories",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None, "host_footprint_observation_failed"
    text = process.stdout.decode("ascii", errors="replace")
    matches = re.findall(r"phys_footprint_peak:\s*([0-9]+)\s+B", text)
    if process.returncode != 0 or not matches:
        return None, "host_footprint_observation_failed"
    return max(int(value) for value in matches), "darwin_phys_footprint_peak"


def _canonical_payload_bytes(
    *,
    compiled_evidence: bytes,
    dependency_payload: dict[str, dict[str, object]],
    fixture: _Fixture,
    mandatory_tail_rows: tuple[batched.AbsoluteTimeScalarJets, ...],
) -> bytes:
    fragments = {
        "dependencies": _canonical_json_bytes(dependency_payload),
        "fixture": _canonical_json_bytes(_fixture_payload(fixture)),
        "mandatory_tail_evaluations": _canonical_json_bytes(
            _builtin(mandatory_tail_rows)
        ),
        "promotion_flags": _canonical_json_bytes(_PROMOTION_FLAGS),
        "schedule": _canonical_json_bytes(_schedule_payload(fixture)),
        "schema": _canonical_json_bytes(CANONICAL_SCHEMA),
        "status": _canonical_json_bytes(CANONICAL_STATUS),
    }

    def assemble(binding: str) -> bytes:
        return b"".join(
            (
                b'{"compiled_batch_evidence":',
                compiled_evidence,
                b',"dependencies":',
                fragments["dependencies"],
                b',"fixture":',
                fragments["fixture"],
                b',"mandatory_tail_evaluations":',
                fragments["mandatory_tail_evaluations"],
                b',"payload_binding_sha256":',
                _canonical_json_bytes(binding),
                b',"promotion_flags":',
                fragments["promotion_flags"],
                b',"schedule":',
                fragments["schedule"],
                b',"schema":',
                fragments["schema"],
                b',"status":',
                fragments["status"],
                b"}",
            )
        )

    provisional = assemble("0" * 64)
    payload = assemble(hashlib.sha256(provisional).hexdigest())
    if len(payload) > MAXIMUM_CANONICAL_BYTES:
        raise ResourceRunnerFailure("canonical resource payload exceeds byte cap")
    return payload


def _dataclass_field_names(value_type: type[object]) -> set[str]:
    return {field.name for field in dataclasses.fields(value_type)}


def _require_exact_dict(
    value: object,
    expected_keys: set[str],
    *,
    label: str,
) -> dict[str, object]:
    if type(value) is not dict or set(value) != expected_keys:
        raise ResourceRunnerFailure(f"{label} has a noncanonical key set")
    return value


def _parse_canonical_hex(
    value: object,
    *,
    label: str,
    nonnegative: bool = False,
) -> float:
    if type(value) is not str:
        raise ResourceRunnerFailure(f"{label} is not a binary64 hex string")
    try:
        parsed = float.fromhex(value)
    except ValueError as error:
        raise ResourceRunnerFailure(f"{label} is not binary64 hex") from error
    if (
        not math.isfinite(parsed)
        or parsed.hex() != value
        or (parsed == 0.0 and math.copysign(1.0, parsed) < 0)
        or (nonnegative and parsed < 0)
    ):
        raise ResourceRunnerFailure(f"{label} is not canonical")
    return parsed


def _binding_with_zero(
    payload: dict[str, object],
    field: str,
) -> str:
    if field not in payload:
        raise ResourceRunnerFailure(f"binding field {field} is absent")
    provisional = dict(payload)
    provisional[field] = "0" * 64
    return hashlib.sha256(_canonical_json_bytes(provisional)).hexdigest()


def _binding_without(
    payload: dict[str, object],
    field: str,
) -> str:
    if field not in payload:
        raise ResourceRunnerFailure(f"binding field {field} is absent")
    provisional = {
        key: value for key, value in payload.items() if key != field
    }
    return hashlib.sha256(_canonical_json_bytes(provisional)).hexdigest()


def _load_time_row(
    raw: object,
    fixture: _Fixture,
    *,
    expected_time: Fraction,
    series_maximum_power: int,
) -> batched.AbsoluteTimeScalarJets:
    row_payload = _require_exact_dict(
        raw,
        _dataclass_field_names(batched.AbsoluteTimeScalarJets),
        label="absolute-time row",
    )
    poisson_payload = _require_exact_dict(
        row_payload["poisson"],
        _dataclass_field_names(batched.CenteredPoissonLedger),
        label="Poisson row",
    )
    raw_jets = row_payload["jets"]
    raw_magnitudes = row_payload["magnitudes"]
    if type(raw_jets) is not list or type(raw_magnitudes) is not list:
        raise ResourceRunnerFailure("time-row intervals are not lists")
    try:
        poisson = batched.CenteredPoissonLedger(**poisson_payload)
        jets = tuple(
            batched.ScalarJetInterval(
                **_require_exact_dict(
                    raw_jet,
                    _dataclass_field_names(batched.ScalarJetInterval),
                    label="scalar jet",
                )
            )
            for raw_jet in raw_jets
        )
        magnitudes = tuple(
            batched.ScalarMagnitudeBound(
                **_require_exact_dict(
                    raw_bound,
                    _dataclass_field_names(batched.ScalarMagnitudeBound),
                    label="scalar magnitude",
                )
            )
            for raw_bound in raw_magnitudes
        )
        row = batched.AbsoluteTimeScalarJets(
            schema=row_payload["schema"],
            time_numerator=row_payload["time_numerator"],
            time_denominator=row_payload["time_denominator"],
            poisson=poisson,
            jets=jets,
            magnitudes=magnitudes,
            absolute_time_from_initial=row_payload[
                "absolute_time_from_initial"
            ],
            state_chaining_used=row_payload["state_chaining_used"],
            binding_sha256=row_payload["binding_sha256"],
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ResourceRunnerFailure("time row has invalid exact types") from error

    integer_fields = (
        row.time_numerator,
        row.time_denominator,
        poisson.mean_numerator,
        poisson.mean_denominator,
        poisson.mode,
        poisson.right_index,
        poisson.terms,
        poisson.requested_tail_numerator,
        poisson.requested_tail_denominator,
        poisson.precision_bits,
        poisson.mode_initialization_count,
        poisson.p0_back_recurrence_steps,
        poisson.right_tail_planning_steps,
        poisson.planning_recurrence_steps,
        poisson.forward_weight_recurrence_steps,
    )
    if any(type(value) is not int for value in integer_fields):
        raise ResourceRunnerFailure("time row has non-integer exact fields")
    try:
        time_value = Fraction(row.time_numerator, row.time_denominator)
        mean = Fraction(poisson.mean_numerator, poisson.mean_denominator)
        requested_tail = Fraction(
            poisson.requested_tail_numerator,
            poisson.requested_tail_denominator,
        )
    except (ValueError, ZeroDivisionError) as error:
        raise ResourceRunnerFailure("time row has an invalid rational") from error
    expected_mean = fixture.uniformization_rate * expected_time
    tail_upper = _parse_canonical_hex(
        poisson.tail_upper_hex,
        label="Poisson tail upper",
        nonnegative=True,
    )
    if (
        row.schema != batched.TIME_SCHEMA
        or time_value != expected_time
        or mean != expected_mean
        or row.absolute_time_from_initial is not True
        or row.state_chaining_used is not False
        or poisson.schema != batched.POISSON_SCHEMA
        or poisson.mode != expected_mean.numerator // expected_mean.denominator
        or poisson.right_index < poisson.mode
        or poisson.terms != poisson.right_index + 1
        or poisson.right_index + batched.MAXIMUM_JET_ORDER
        > series_maximum_power
        or requested_tail != fixture.tail_tolerance
        or poisson.precision_bits != fixture.mpfr_precision_bits
        or poisson.terms > fixture.maximum_poisson_terms
        or poisson.mode_initialization_count != 1
        or poisson.p0_back_recurrence_steps != poisson.mode
        or poisson.right_tail_planning_steps
        != (
            0
            if expected_mean == 0
            else poisson.right_index - poisson.mode + 1
        )
        or poisson.planning_recurrence_steps
        != (
            poisson.p0_back_recurrence_steps
            + poisson.right_tail_planning_steps
        )
        or poisson.forward_weight_recurrence_steps != poisson.right_index
        or poisson.mode_initialized is not True
        or poisson.p0_derived_from_mode is not True
        or poisson.right_tail_geometric is not True
        or poisson.starts_at_zero is not True
        or tail_upper > float(fixture.tail_tolerance) * (1 + 2**-48)
        or poisson.binding_sha256 != batched._poisson_binding(poisson)
        or tuple(jet.order for jet in jets) != (0, 1, 2, 3)
        or tuple(bound.order for bound in magnitudes) != (2, 3, 4)
    ):
        raise ResourceRunnerFailure("absolute-time row semantics failed")
    for jet in jets:
        lower = _parse_canonical_hex(jet.lower_hex, label="jet lower")
        upper = _parse_canonical_hex(jet.upper_hex, label="jet upper")
        if (
            jet.schema != batched.JET_SCHEMA
            or type(jet.order) is not int
            or lower > upper
            or jet.binding_sha256 != batched._jet_binding(jet)
        ):
            raise ResourceRunnerFailure("scalar jet binding failed")
    for bound in magnitudes:
        _parse_canonical_hex(
            bound.upper_hex,
            label="magnitude upper",
            nonnegative=True,
        )
        if (
            bound.schema != batched.MAGNITUDE_SCHEMA
            or type(bound.order) is not int
            or bound.formula != batched.MAGNITUDE_FORMULA
            or bound.binding_sha256 != batched._magnitude_binding(bound)
        ):
            raise ResourceRunnerFailure("scalar magnitude binding failed")
    if row.binding_sha256 != batched._time_binding(row):
        raise ResourceRunnerFailure("absolute-time row binding failed")
    return row


def _expected_dependencies_payload() -> dict[str, dict[str, object]]:
    return {
        name: {
            "accepted": True,
            "expected_sha256": expected,
            "observed_sha256": expected,
        }
        for name, expected in sorted(_EXPECTED_DEPENDENCY_SHA256.items())
    }


def _validate_compiled_evidence(
    raw: object,
    fixture: _Fixture,
) -> None:
    evidence = _require_exact_dict(
        raw,
        {
            "evidence_binding_sha256",
            "evaluations",
            "metadata",
            "receipt",
            "schema",
            "series",
        },
        label="compiled-batch evidence",
    )
    if (
        evidence["schema"] != integrated.EVIDENCE_SCHEMA
        or evidence["evidence_binding_sha256"]
        != _binding_with_zero(evidence, "evidence_binding_sha256")
        or evidence["metadata"] != integrated._metadata_payload(_metadata(fixture))
    ):
        raise ResourceRunnerFailure("compiled-batch evidence binding failed")

    series_payload = _require_exact_dict(
        evidence["series"],
        _dataclass_field_names(batched.CanonicalScalarPowerSeries),
        label="canonical scalar series",
    )
    try:
        series = batched.load_canonical_scalar_power_series_bytes(
            _canonical_json_bytes(series_payload)
        )
    except batched.BatchedScalarFailure as error:
        raise ResourceRunnerFailure("canonical scalar series failed replay") from error
    expected_maximum_power = fixture.expected_maximum_power
    if (
        Fraction(
            series.horizon_numerator,
            series.horizon_denominator,
        )
        != fixture.series_horizon
        or Fraction(
            series.uniformization_rate_numerator,
            series.uniformization_rate_denominator,
        )
        != fixture.uniformization_rate
        or Fraction(
            series.maximum_killing_upper_numerator,
            series.maximum_killing_upper_denominator,
        )
        != fixture.killing
        or (
            expected_maximum_power is not None
            and series.maximum_power_index != expected_maximum_power
        )
        or series.control_exclusion_proved is not False
        or series.science_free_proved is not False
        or series.f0_pass is not False
    ):
        raise ResourceRunnerFailure("canonical scalar series fixture drifted")

    raw_evaluations = evidence["evaluations"]
    if (
        type(raw_evaluations) is not list
        or len(raw_evaluations) != len(fixture.topology_times)
    ):
        raise ResourceRunnerFailure("compiled evaluation count drifted")
    for raw_row, expected_time in zip(
        raw_evaluations,
        fixture.topology_times,
        strict=True,
    ):
        _load_time_row(
            raw_row,
            fixture,
            expected_time=expected_time,
            series_maximum_power=series.maximum_power_index,
        )

    receipt = _require_exact_dict(
        evidence["receipt"],
        _dataclass_field_names(integrated.CompiledBatchReceipt),
        label="compiled-batch receipt",
    )
    if (
        receipt["receipt_sha256"]
        != _binding_without(receipt, "receipt_sha256")
        or receipt["schema"] != integrated.RECEIPT_SCHEMA
        or receipt["status"] != integrated.METHOD_STATUS
        or receipt["integration_source_sha256"]
        != _EXPECTED_DEPENDENCY_SHA256["compiled_batch_source"]
        or receipt["batched_scalar_source_sha256"]
        != _EXPECTED_DEPENDENCY_SHA256["batched_scalar_source"]
        or receipt["metadata_binding_sha256"]
        != integrated._metadata_binding(_metadata(fixture))
        or receipt["scalar_stream_sha256"]
        != series.scalar_stream_sha256
        or receipt["canonical_series_binding_sha256"]
        != series.series_binding_sha256
        or receipt["canonical_series_bytes_sha256"]
        != hashlib.sha256(
            batched.canonical_scalar_power_series_bytes(series)
        ).hexdigest()
        or receipt["returned_jet_orders"] != [0, 1, 2, 3]
        or receipt["maximum_finite_difference_order"]
        != batched.MAXIMUM_JET_ORDER
        or receipt["compiled_power_stream_run_count"] != 1
        or receipt["absolute_time_reevaluation_used"] is not True
        or receipt["repeated_p_actions_during_reevaluation"] != 0
        or receipt["input_provenance_classification"]
        != integrated.INPUT_PROVENANCE_CLASSIFICATION
    ):
        raise ResourceRunnerFailure("compiled-batch receipt binding failed")
    receipt_false_fields = (
        "integration_source_observation_authoritative",
        "independent_source_audit_complete",
        "method_metadata_preconditions_proved",
        "initial_mass_cap_independently_proved",
        "external_stream_replay_complete",
        "control_exclusion_proved",
        "science_free_proved",
        "authorizes_scientific_execution",
        "science_executed",
        "topology_pass",
        "production_scale_execution_classified",
        "resource_pass",
        "f0_pass",
    )
    if any(receipt[field] is not False for field in receipt_false_fields):
        raise ResourceRunnerFailure("compiled-batch receipt was promoted")
    _parse_canonical_hex(
        receipt["maximum_state_radius_upper_hex"],
        label="maximum state radius",
        nonnegative=True,
    )

    horizon_plan = integrated._make_plan_binding(
        _metadata(fixture),
        purpose="series_horizon",
        time=fixture.series_horizon,
    )
    if receipt["horizon_plan"] != _builtin(horizon_plan):
        raise ResourceRunnerFailure("horizon Poisson plan drifted")
    expected_plans = [
        _builtin(
            integrated._make_plan_binding(
                _metadata(fixture),
                purpose=f"evaluation_{index}",
                time=value,
            )
        )
        for index, value in enumerate(fixture.topology_times)
    ]
    if receipt["evaluation_plans"] != expected_plans:
        raise ResourceRunnerFailure("evaluation Poisson plans drifted")

    resources = _require_exact_dict(
        receipt["resources"],
        _dataclass_field_names(integrated.CompiledBatchResourceLedger),
        label="compiled resource ledger",
    )
    if (
        resources["states"] != math.prod(fixture.shape)
        or resources["maximum_power_index"] != series.maximum_power_index
        or resources["compiled_power_stream_run_count"] != 1
        or resources["p_action_call_count"] != series.maximum_power_index
        or resources["mass_reduction_call_count"]
        != series.maximum_power_index + 1
        or resources["killing_dot_call_count"]
        != series.maximum_power_index + 1
        or resources["evaluation_count"] != len(fixture.topology_times)
        or any(
            resources[field] is not False
            for field in (
                "complete_numeric_payload_ledger",
                "complete_process_peak_measured",
                "production_scale_execution_classified",
                "resource_pass",
                "f0_pass",
            )
        )
    ):
        raise ResourceRunnerFailure("compiled resource ledger was promoted")

    build = _require_exact_dict(
        receipt["compiled_build_receipt"],
        _dataclass_field_names(compiled.CompiledBuildReceipt),
        label="compiled build receipt",
    )
    backend = _require_exact_dict(
        receipt["compiled_backend_receipt"],
        _dataclass_field_names(compiled.CompiledBackendReceipt),
        label="compiled backend receipt",
    )
    stream = _require_exact_dict(
        receipt["compiled_stream_receipt"],
        _dataclass_field_names(compiled.CompiledPowerStreamReceipt),
        label="compiled stream receipt",
    )
    if (
        build != backend["build"]
        or build["schema"] != compiled.BUILD_RECEIPT_SCHEMA
        or build["status"] != compiled.METHOD_STATUS
        or build["python_wrapper_sha256"]
        != _EXPECTED_DEPENDENCY_SHA256["compiled_power_python_source"]
        or build["c_source_sha256"]
        != _EXPECTED_DEPENDENCY_SHA256["compiled_power_c_source"]
        or build["fast_math_enabled"] is not False
        or build["fp_contraction_enabled"] is not False
        or build["unsafe_fp_optimizations_enabled"] is not False
        or any(
            build[field] is not False
            for field in (
                "authorizes_scientific_execution",
                "science_executed",
                "resource_pass",
                "f0_pass",
            )
        )
        or backend["schema"] != compiled.BACKEND_RECEIPT_SCHEMA
        or backend["status"] != compiled.METHOD_STATUS
        or backend["tensor_shape"] != list(fixture.shape)
        or backend["periodic"] != list(fixture.periodic)
        or backend["states"] != math.prod(fixture.shape)
        or backend["receipt_sha256"]
        != _binding_with_zero(backend, "receipt_sha256")
        or receipt["compiled_backend_receipt_sha256"]
        != backend["receipt_sha256"]
        or any(
            backend[field] is not False
            for field in (
                "control_exclusion_proved",
                "science_free_proved",
                "authorizes_scientific_execution",
                "science_executed",
                "resource_pass",
                "f0_pass",
            )
        )
        or stream["schema"] != compiled.STREAM_RECEIPT_SCHEMA
        or stream["status"] != compiled.METHOD_STATUS
        or stream["backend_receipt_sha256"] != backend["receipt_sha256"]
        or stream["maximum_power_index"] != series.maximum_power_index
        or stream["p_action_call_count"] != series.maximum_power_index
        or stream["mass_reduction_call_count"]
        != series.maximum_power_index + 1
        or stream["killing_dot_call_count"]
        != series.maximum_power_index + 1
        or stream["stream_binding_sha256"]
        != _binding_with_zero(stream, "stream_binding_sha256")
        or any(
            stream[field] is not False
            for field in (
                "control_exclusion_proved",
                "science_free_proved",
                "authorizes_scientific_execution",
                "science_executed",
                "resource_pass",
                "f0_pass",
            )
        )
    ):
        raise ResourceRunnerFailure("compiled backend/stream binding failed")


def validate_canonical_resource_payload_bytes(payload: bytes) -> dict[str, object]:
    """Strictly validate a persisted deterministic resource payload."""

    parsed = _strict_json_loads(payload)
    if (
        type(parsed) is not dict
        or set(parsed) != _CANONICAL_KEYS
        or parsed.get("schema") != CANONICAL_SCHEMA
        or parsed.get("status") != CANONICAL_STATUS
        or parsed.get("promotion_flags") != _PROMOTION_FLAGS
        or type(parsed.get("payload_binding_sha256")) is not str
        or _SHA256_PATTERN.fullmatch(parsed["payload_binding_sha256"]) is None
        or parsed.get("dependencies") != _expected_dependencies_payload()
    ):
        raise ResourceRunnerFailure("canonical resource payload header is invalid")
    fixture_payload = parsed["fixture"]
    if fixture_payload == _fixture_payload(_FORMAL_FIXTURE):
        fixture = _FORMAL_FIXTURE
    elif fixture_payload == _fixture_payload(_SMALL_TEST_FIXTURE):
        fixture = _SMALL_TEST_FIXTURE
    else:
        raise ResourceRunnerFailure("canonical fixture literals drifted")
    if parsed["schedule"] != _schedule_payload(fixture):
        raise ResourceRunnerFailure("canonical schedule literals drifted")
    _validate_compiled_evidence(parsed["compiled_batch_evidence"], fixture)
    raw_tail_rows = parsed["mandatory_tail_evaluations"]
    series_maximum_power = parsed["compiled_batch_evidence"]["series"][
        "maximum_power_index"
    ]
    if (
        type(raw_tail_rows) is not list
        or len(raw_tail_rows) != len(fixture.mandatory_tail_times)
        or type(series_maximum_power) is not int
    ):
        raise ResourceRunnerFailure("mandatory tail rows drifted")
    for raw_row, expected_time in zip(
        raw_tail_rows,
        fixture.mandatory_tail_times,
        strict=True,
    ):
        _load_time_row(
            raw_row,
            fixture,
            expected_time=expected_time,
            series_maximum_power=series_maximum_power,
        )
    observed_binding = parsed["payload_binding_sha256"]
    provisional = dict(parsed)
    provisional["payload_binding_sha256"] = "0" * 64
    expected_binding = hashlib.sha256(
        _canonical_json_bytes(provisional)
    ).hexdigest()
    if observed_binding != expected_binding:
        raise ResourceRunnerFailure("canonical resource payload binding failed")
    if _canonical_json_bytes(parsed) != payload:
        raise ResourceRunnerFailure("resource payload bytes are not canonical")
    return parsed


def _resource_failures(
    fixture: _Fixture,
    result: integrated.CompiledCanonicalScalarSeriesResult,
    *,
    wall_seconds: float,
    peak_rss_bytes: int,
    peak_footprint_bytes: int | None,
    swap_delta: int,
    dependency_payload: dict[str, dict[str, object]],
    canonical_byte_count: int,
) -> list[str]:
    failures: list[str] = []
    receipt = result.receipt
    horizon = receipt.horizon_plan
    resources = receipt.resources
    maximum_state_radius = Fraction.from_float(
        float.fromhex(receipt.maximum_state_radius_upper_hex)
    )
    union = set(fixture.topology_times)
    union.update(fixture.mandatory_tail_times)
    checks = (
        (
            all(row.get("accepted") is True for row in dependency_payload.values()),
            "dependency_hashes_not_accepted",
        ),
        (wall_seconds <= float(fixture.maximum_wall_seconds), "wall_cap_exceeded"),
        (peak_rss_bytes <= fixture.maximum_rss_bytes, "rss_cap_exceeded"),
        (
            peak_footprint_bytes is not None,
            "peak_footprint_unavailable",
        ),
        (
            peak_footprint_bytes is not None
            and peak_footprint_bytes <= fixture.maximum_peak_footprint_bytes,
            "peak_footprint_cap_exceeded",
        ),
        (
            swap_delta <= fixture.maximum_process_swap_delta,
            "process_swap_cap_exceeded",
        ),
        (
            maximum_state_radius <= fixture.maximum_state_radius,
            "state_radius_cap_exceeded",
        ),
        (
            resources.compiled_power_stream_run_count == 1,
            "compiled_stream_count_drifted",
        ),
        (
            resources.p_action_call_count == resources.maximum_power_index,
            "p_action_count_drifted",
        ),
        (
            result.receipt.repeated_p_actions_during_reevaluation == 0,
            "reevaluation_repeated_p_actions",
        ),
        (
            resources.evaluation_count == len(fixture.topology_times),
            "topology_evaluation_count_drifted",
        ),
        (
            len(union) <= fixture.maximum_union_time_count,
            "combined_time_count_exceeded",
        ),
        (
            canonical_byte_count <= MAXIMUM_CANONICAL_BYTES,
            "canonical_byte_cap_exceeded",
        ),
    )
    failures.extend(label for passed, label in checks if not passed)
    if fixture.production_scale:
        production_checks = (
            (
                fixture.topology_schedule_complete,
                "integrated_topology_schedule_not_frozen",
            ),
            (
                resources.states == FORMAL_STATES,
                "formal_state_count_drifted",
            ),
            (
                resources.maximum_power_index
                == fixture.expected_maximum_power,
                "formal_maximum_power_drifted",
            ),
            (
                horizon.mode == fixture.expected_poisson_mode,
                "formal_poisson_mode_drifted",
            ),
            (
                horizon.right_index == fixture.expected_right_index,
                "formal_poisson_right_index_drifted",
            ),
            (
                len(fixture.topology_times) == FORMAL_TOPOLOGY_TIME_COUNT,
                "formal_topology_time_count_drifted",
            ),
        )
        failures.extend(
            label for passed, label in production_checks if not passed
        )
    return failures


def _sidecar_bytes(
    fixture: _Fixture,
    result: integrated.CompiledCanonicalScalarSeriesResult,
    *,
    output_path: Path,
    canonical_payload: bytes,
    dependencies_before: dict[str, dict[str, object]],
    dependencies_after: dict[str, dict[str, object]],
    wall_seconds: float,
    before_usage: resource.struct_rusage,
    after_usage: resource.struct_rusage,
    peak_footprint_bytes: int | None,
    footprint_method: str,
) -> bytes:
    peak_rss = _peak_rss_bytes(after_usage)
    swaps_before = _process_swap_count(before_usage)
    swaps_after = _process_swap_count(after_usage)
    swap_delta = swaps_after - swaps_before
    if swap_delta < 0:
        raise ResourceRunnerFailure("process swap counter moved backwards")
    failures = _resource_failures(
        fixture,
        result,
        wall_seconds=wall_seconds,
        peak_rss_bytes=peak_rss,
        peak_footprint_bytes=peak_footprint_bytes,
        swap_delta=swap_delta,
        dependency_payload=dependencies_after,
        canonical_byte_count=len(canonical_payload),
    )
    if fixture.production_scale:
        status = PASS_CANDIDATE_STATUS if not failures else HOLD_STATUS
    else:
        status = PRIVATE_STATUS
    sidecar = {
        "canonical_artifact": {
            "absolute_path": str(output_path),
            "byte_count": len(canonical_payload),
            "sha256": hashlib.sha256(canonical_payload).hexdigest(),
        },
        "dependencies_after": dependencies_after,
        "dependencies_before": dependencies_before,
        "failure_reasons": failures,
        "fixture": _fixture_payload(fixture),
        "measurement": {
            "host_peak_footprint_bytes": peak_footprint_bytes,
            "host_peak_footprint_method": footprint_method,
            "peak_rss_bytes": peak_rss,
            "process_swap_count_after": swaps_after,
            "process_swap_count_before": swaps_before,
            "process_swap_delta": swap_delta,
            "wall_seconds_hex": wall_seconds.hex(),
        },
        "method_counts": {
            "canonical_scalar_record_count": (
                result.receipt.resources.canonical_scalar_record_count
            ),
            "compiled_power_stream_run_count": (
                result.receipt.resources.compiled_power_stream_run_count
            ),
            "mandatory_tail_evaluation_count": len(
                fixture.mandatory_tail_times
            ),
            "maximum_power_index": (
                result.receipt.resources.maximum_power_index
            ),
            "p_action_call_count": result.receipt.resources.p_action_call_count,
            "repeated_p_actions_during_reevaluation": (
                result.receipt.repeated_p_actions_during_reevaluation
            ),
            "topology_evaluation_count": (
                result.receipt.resources.evaluation_count
            ),
        },
        "promotion_flags": _PROMOTION_FLAGS,
        "resource_caps_satisfied": not failures,
        "runner_source_sha256_same_process_observation": _stable_file_sha256(
            Path(__file__).resolve(strict=True)
        ),
        "runner_source_sha256_same_process_observation_authoritative": False,
        "schedule": _schedule_payload(fixture),
        "schema": OBSERVATION_SCHEMA,
        "status": status,
    }
    return json.dumps(
        sidecar,
        allow_nan=False,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ).encode("ascii") + b"\n"


def _stage_bytes(target: Path, payload: bytes) -> Path:
    parent = target.parent
    if not parent.is_dir():
        raise ResourceRunnerFailure("output parent is not an existing directory")
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    for attempt in range(32):
        stage = parent / (
            f".{target.name}.stage-{os.getpid()}-"
            f"{time.monotonic_ns()}-{attempt}"
        )
        try:
            descriptor = os.open(stage, flags, 0o600)
        except FileExistsError:
            continue
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise ResourceRunnerFailure("staged output write made no progress")
                view = view[written:]
            os.fsync(descriptor)
        except BaseException:
            os.close(descriptor)
            stage.unlink(missing_ok=True)
            raise
        os.close(descriptor)
        return stage
    raise ResourceRunnerFailure("cannot reserve a unique staged output path")


def _publish_pair_exclusive(
    output_path: Path,
    canonical_payload: bytes,
    sidecar_payload: bytes,
) -> Path:
    sidecar_path = output_path.with_name(output_path.name + ".resources.json")
    if os.path.lexists(output_path) or os.path.lexists(sidecar_path):
        raise ResourceRunnerFailure("output or resource sidecar already exists")
    canonical_stage = _stage_bytes(output_path, canonical_payload)
    sidecar_stage = _stage_bytes(sidecar_path, sidecar_payload)
    sidecar_published = False
    try:
        os.link(sidecar_stage, sidecar_path, follow_symlinks=False)
        sidecar_published = True
        try:
            os.link(canonical_stage, output_path, follow_symlinks=False)
        except BaseException:
            if sidecar_published:
                sidecar_path.unlink(missing_ok=True)
            raise
        directory_descriptor = os.open(
            output_path.parent,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0),
        )
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except FileExistsError as error:
        raise ResourceRunnerFailure(
            "exclusive output publication lost a race"
        ) from error
    except OSError as error:
        raise ResourceRunnerFailure("atomic output publication failed") from error
    finally:
        canonical_stage.unlink(missing_ok=True)
        sidecar_stage.unlink(missing_ok=True)
    return sidecar_path


def _validate_absolute_output_path(output_path: Path) -> None:
    if not isinstance(output_path, Path) or not output_path.is_absolute():
        raise ResourceRunnerFailure("output path must be an absolute pathlib.Path")
    if output_path.name in {"", ".", ".."}:
        raise ResourceRunnerFailure("output filename is invalid")


def _execute_fixture(fixture: _Fixture, output_path: Path) -> Path:
    _validate_fixture(fixture)
    _validate_absolute_output_path(output_path)
    sidecar_path = output_path.with_name(output_path.name + ".resources.json")
    if os.path.lexists(output_path) or os.path.lexists(sidecar_path):
        raise ResourceRunnerFailure("output or resource sidecar already exists")
    dependencies_before = _observe_dependencies()
    before_usage = resource.getrusage(resource.RUSAGE_SELF)
    started = time.perf_counter()
    backend, initial = _build_identity_backend_and_initial(fixture)
    result = integrated.build_compiled_canonical_scalar_series(
        backend,
        initial,
        _metadata(fixture),
    )
    tail_rows = batched.reevaluate_canonical_scalar_series(
        result.scalar_series,
        times=fixture.mandatory_tail_times,
        tail_tolerance=fixture.tail_tolerance,
        precision_bits=fixture.mpfr_precision_bits,
        maximum_terms=fixture.maximum_poisson_terms,
    )
    if (
        tuple(
            Fraction(row.time_numerator, row.time_denominator)
            for row in tail_rows
        )
        != fixture.mandatory_tail_times
        or any(
            row.absolute_time_from_initial is not True
            or row.state_chaining_used is not False
            or row.binding_sha256 != batched._time_binding(row)
            for row in tail_rows
        )
    ):
        raise ResourceRunnerFailure("mandatory tail reevaluation failed")
    compiled_evidence = integrated.compiled_batch_evidence_bytes(result)
    dependencies_after = _observe_dependencies()
    if dependencies_after != dependencies_before:
        raise ResourceRunnerFailure("dependency bytes changed during execution")
    canonical_payload = _canonical_payload_bytes(
        compiled_evidence=compiled_evidence,
        dependency_payload=dependencies_after,
        fixture=fixture,
        mandatory_tail_rows=tail_rows,
    )
    wall_seconds = time.perf_counter() - started
    peak_footprint, footprint_method = _host_peak_footprint_bytes()
    after_usage = resource.getrusage(resource.RUSAGE_SELF)
    sidecar_payload = _sidecar_bytes(
        fixture,
        result,
        output_path=output_path,
        canonical_payload=canonical_payload,
        dependencies_before=dependencies_before,
        dependencies_after=dependencies_after,
        wall_seconds=wall_seconds,
        before_usage=before_usage,
        after_usage=after_usage,
        peak_footprint_bytes=peak_footprint,
        footprint_method=footprint_method,
    )
    return _publish_pair_exclusive(
        output_path,
        canonical_payload,
        sidecar_payload,
    )


def _run_private_small_fixture(output_path: Path) -> Path:
    """Run the fixed bounded fixture used only by this module's tests."""

    return _execute_fixture(_SMALL_TEST_FIXTURE, output_path)


def run_resource_candidate(output_path: Path) -> Path:
    """Run the immutable formal fixture once its exact schedule is complete."""

    _validate_absolute_output_path(output_path)
    _observe_dependencies()
    if not _FORMAL_FIXTURE.topology_schedule_complete:
        raise ResourceRunnerFailure(
            "formal execution refused: integrated topology-query schedule "
            "is provisional"
        )
    return _execute_fixture(_FORMAL_FIXTURE, output_path)


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the immutable science-free F0 largest-shape resource fixture."
        )
    )
    parser.add_argument(
        "output",
        type=Path,
        help="absolute path for the canonical evidence JSON",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _argument_parser().parse_args(argv)
    try:
        sidecar = run_resource_candidate(arguments.output)
    except ResourceRunnerFailure as error:
        print(f"{HOLD_STATUS}: {error}", file=sys.stderr)
        return 2
    print(str(arguments.output))
    print(str(sidecar))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
