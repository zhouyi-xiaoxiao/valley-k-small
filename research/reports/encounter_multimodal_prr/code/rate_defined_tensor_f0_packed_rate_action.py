"""Point-plus-``l1``-ball rate-action composition for the packed F0 work.

This module is a deliberately bounded, science-free method layer.  It binds
the repaired stage-1 nominal action to the repaired directed centre action and
maps ``c + B_1(e)`` to an owned nominal point plus an outward binary64 radius.
It does not implement uniformization, Poisson weights, time propagation,
topology, F1, or a fresh-process verifier.

The returned :class:`InternalRateActionState` contains a NumPy array.  It is
therefore explicitly non-authoritative: read-only NumPy ownership is useful
for method testing, but it is not an authority boundary.  A later producer
and separate-implementation verifier must serialize/reconstruct immutable
payloads in a fresh process and expose no arrays.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import platform
import sys
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Final

import numpy as np
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_interval_action as directed

RATE_ACTION_CONTRACT_SCHEMA: Final = "rate_defined_tensor_f0_packed_rate_action_contract_v1"
RATE_ACTION_INPUT_SCHEMA: Final = "rate_defined_tensor_f0_packed_rate_action_input_v1"
RATE_ACTION_STATE_SCHEMA: Final = "rate_defined_tensor_f0_packed_rate_action_state_v1"
RATE_ACTION_DERIVATION_SCHEMA: Final = "rate_defined_tensor_f0_packed_rate_action_derivation_v1"
RATE_ACTION_MEMORY_SCHEMA: Final = "rate_defined_tensor_f0_packed_rate_action_memory_v1"
POINT_LIFT_SCHEMA: Final = "rate_defined_tensor_f0_packed_point_lift_v1"
POINT_LIFT_ZERO_POLICY: Final = "canonicalize_both_zero_signs_to_positive_zero_v1"
INPUT_RADIUS_AUTHORITY: Final = "DECLARED_METHOD_PRECONDITION_ONLY_NOT_AUTHORITATIVE"
METHOD_STATUS: Final = "PASS_RATE_ACTION_METHOD_ONLY_NOT_F0"
INPUT_STATUS: Final = "RATE_ACTION_METHOD_INPUT_ONLY_NOT_F0"

P_FORMULA_ID: Final = "e_plus=e+delta_p_selected*m+a_ordered_up_v1"
Q_FORMULA_ID: Final = "e_plus=(qhat_norm+delta_q)*e+delta_q*m+a_ordered_up_v1"
SCALAR_OPERATION_MODEL: Final = (
    "all-scalars-exact-built-in-nonnegative-finite-binary64",
    "fraction-witness-to-least-binary64-upper-by-exact-comparison",
    "m-increasing-flat-index-nextafter-after-every-add",
    "a-increasing-flat-index-two-subtractions-and-add-nextafter-up",
    "p-trace-mul-delta-p-m-add-e-add-a",
    "q-trace-add-qhat-delta-q-mul-input-radius-mul-delta-q-m-add-add-a",
    "nonfinite-intermediate-fails-closed",
)

SOURCE_NOMINAL_BYTES_PER_STATE: Final = 8
POINT_LIFT_BYTES_PER_STATE: Final = 16
DIRECTED_OUTPUT_BYTES_PER_STATE: Final = 16
NOMINAL_OUTPUT_BYTES_PER_STATE: Final = 8
POINT_LIFT_VALIDATION_BYTES_PER_BLOCK_STATE: Final = 2
RETAINED_OUTPUT_BYTES_PER_STATE: Final = 8

HOLD_RATE_ACTION_SCHEMA: Final = "HOLD_F0_RATE_ACTION_SCHEMA_INVALID"
HOLD_RATE_ACTION_BINDING: Final = "HOLD_F0_RATE_ACTION_BINDING_MISMATCH"
HOLD_RATE_ACTION_ARRAY: Final = "HOLD_F0_RATE_ACTION_ARRAY_NONCANONICAL"
HOLD_RATE_ACTION_RADIUS: Final = "HOLD_F0_RATE_ACTION_RADIUS_INVALID"
HOLD_RATE_ACTION_POINT_LIFT: Final = "HOLD_F0_RATE_ACTION_POINT_LIFT_INVALID"
HOLD_RATE_ACTION_CENTRE: Final = "HOLD_F0_RATE_ACTION_CENTRE_ACTION_MISMATCH"
HOLD_RATE_ACTION_RESOURCE: Final = "HOLD_F0_RATE_ACTION_RESOURCE_LEDGER_INVALID"
HOLD_RATE_ACTION_AUTHORITY: Final = "HOLD_F0_RATE_ACTION_FRESH_PROCESS_REQUIRED"

_POSITIVE_INFINITY: Final = np.float64(math.inf)
_CANONICAL_JSON_STREAM_CHUNK_LIMIT: Final = 4096
_CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES: Final = 2 * _CANONICAL_JSON_STREAM_CHUNK_LIMIT
_SOURCE_HASH_STREAM_CHUNK_BYTES: Final = 4096
_MAXIMUM_EXACT_WITNESS_INTEGER_BITS: Final = 4096
_MAXIMUM_SUBORDINATE_SERIALIZATION_PAYLOAD_BYTES: Final = 131_072


def _sha256(payload: bytes | memoryview) -> str:
    return hashlib.sha256(payload).hexdigest()


def _validate_json_scalar_bounds(payload: object) -> None:
    """Reject pathological tokens before ``JSONEncoder`` converts them."""

    pending = [payload]
    while pending:
        value = pending.pop()
        if type(value) is dict:
            for key, entry in value.items():
                if type(key) is not str or len(key) > _CANONICAL_JSON_STREAM_CHUNK_LIMIT:
                    raise packed.PackedF0Failure(
                        HOLD_RATE_ACTION_RESOURCE,
                        "canonical JSON key exceeds the fixed token cap",
                    )
                pending.append(entry)
        elif type(value) in {list, tuple}:
            pending.extend(value)
        elif type(value) is str:
            if len(value) > _CANONICAL_JSON_STREAM_CHUNK_LIMIT:
                raise packed.PackedF0Failure(
                    HOLD_RATE_ACTION_RESOURCE,
                    "canonical JSON string exceeds the fixed token cap",
                )
        elif type(value) is int:
            if abs(value).bit_length() > _MAXIMUM_EXACT_WITNESS_INTEGER_BITS:
                raise packed.PackedF0Failure(
                    HOLD_RATE_ACTION_RESOURCE,
                    "canonical JSON integer exceeds the exact-witness bit cap",
                )
        elif type(value) is float:
            if not math.isfinite(value):
                raise packed.PackedF0Failure(
                    HOLD_RATE_ACTION_RESOURCE,
                    "canonical JSON float is nonfinite",
                )
        elif value is not None and type(value) is not bool:
            raise packed.PackedF0Failure(
                HOLD_RATE_ACTION_RESOURCE,
                "canonical JSON contains an unsupported exact type",
            )


def _canonical_json_digest(payload: object) -> str:
    """Hash canonical JSON without materializing one full encoded payload."""

    _validate_json_scalar_bounds(payload)
    encoder = json.JSONEncoder(
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    digest = hashlib.sha256()
    try:
        for text in encoder.iterencode(payload):
            if len(text) > _CANONICAL_JSON_STREAM_CHUNK_LIMIT:
                raise packed.PackedF0Failure(
                    HOLD_RATE_ACTION_RESOURCE,
                    "canonical JSON stream chunk exceeded its fixed scalar cap",
                )
            encoded = text.encode("ascii")
            if len(encoded) > _CANONICAL_JSON_STREAM_CHUNK_LIMIT:
                raise packed.PackedF0Failure(
                    HOLD_RATE_ACTION_RESOURCE,
                    "canonical JSON encoded chunk exceeded its fixed scalar cap",
                )
            # Both ``text`` and ``encoded`` are live here; the memory ledger
            # therefore records twice the token cap, not one chunk.
            digest.update(encoded)
    except packed.PackedF0Failure:
        raise
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RESOURCE,
            "canonical JSON encoding failed closed",
        ) from error
    return digest.hexdigest()


def _require_bounded_subordinate_json_string(value: object, *, label: str) -> None:
    """Preflight an ``ensure_ascii`` token without allocating its encoding."""

    if type(value) is not str:
        return  # The frozen subordinate exact-type validator will reject it.
    encoded_length = 2  # Opening and closing JSON quotes.
    for character in value:
        codepoint = ord(character)
        if character in {'"', "\\"} or codepoint < 0x20:
            encoded_length += 6  # Conservative for short two-byte escapes.
        elif codepoint < 0x80:
            encoded_length += 1
        elif codepoint <= 0xFFFF:
            encoded_length += 6
        else:
            encoded_length += 12  # JSON surrogate-pair escapes.
        if encoded_length > _CANONICAL_JSON_STREAM_CHUNK_LIMIT:
            raise packed.PackedF0Failure(
                HOLD_RATE_ACTION_RESOURCE,
                f"{label} exceeds the frozen subordinate JSON token cap",
            )


def _preflight_subordinate_serialization_bounds(kernel: object) -> None:
    """Keep the fixed full-serialization allowance conservative before replay."""

    if type(kernel) is not packed.PackedTensorKernel or type(kernel.axes) is not tuple:
        return  # Frozen validation supplies the stable structural HOLD.
    for dimension, axis in enumerate(kernel.axes):
        if type(axis) is not packed.CanonicalPackedAxis:
            continue
        _require_bounded_subordinate_json_string(
            axis.name,
            label=f"axis {dimension} name",
        )
        for direction, source in (
            ("forward", axis.forward),
            ("backward", axis.backward),
        ):
            if (
                type(source) is packed.CanonicalPackedIntervals
                and type(source.manifest) is packed.PackedIntervalManifest
            ):
                _require_bounded_subordinate_json_string(
                    source.manifest.role,
                    label=f"axis {dimension} {direction} role",
                )
    if (
        type(kernel.killing) is packed.CanonicalPackedIntervals
        and type(kernel.killing.manifest) is packed.PackedIntervalManifest
    ):
        _require_bounded_subordinate_json_string(
            kernel.killing.manifest.role,
            label="killing role",
        )


def _source_sha256(path: str) -> str:
    digest = hashlib.sha256()
    scratch = bytearray(_SOURCE_HASH_STREAM_CHUNK_BYTES)
    try:
        with Path(path).open("rb", buffering=0) as source:
            while True:
                count = source.readinto(scratch)
                if count == 0:
                    break
                digest.update(memoryview(scratch)[:count])
    except OSError as error:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "bound source file cannot be streamed",
        ) from error
    return digest.hexdigest()


def _source_byte_length(path: str) -> int:
    try:
        length = Path(path).stat().st_size
    except OSError as error:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "bound source length cannot be read",
        ) from error
    if type(length) is not int or length < 1:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, "bound source is empty")
    return length


def _raw_sha256(array: np.ndarray) -> str:
    return _sha256(memoryview(array).cast("B"))


def _is_hex_digest(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _runtime_identity() -> str:
    return (
        f"python-{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        f"|numpy-{np.__version__}|machine-{platform.machine()}|byteorder-{sys.byteorder}"
    )


def _operation_model_sha256() -> str:
    return _canonical_json_digest(list(SCALAR_OPERATION_MODEL))


def _require_nonnegative_finite_float(value: object, *, label: str) -> float:
    if (
        type(value) is not float
        or not math.isfinite(value)
        or value < 0.0
        or (value == 0.0 and math.copysign(1.0, value) < 0.0)
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RADIUS,
            f"{label} must be an exact nonnegative finite built-in float",
        )
    return value


def _parse_nonnegative_finite_hex(value: object, *, label: str) -> float:
    if type(value) is not str or len(value) > 32:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_RADIUS, f"{label} hex has wrong type")
    try:
        parsed = float.fromhex(value)
    except (OverflowError, ValueError) as error:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RADIUS,
            f"{label} scalar hex is invalid",
        ) from error
    parsed = _require_nonnegative_finite_float(parsed, label=label)
    if parsed.hex() != value:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RADIUS,
            f"{label} hex is not canonical",
        )
    return parsed


def _next_up(value: float, *, label: str) -> float:
    result = float(np.nextafter(np.float64(value), _POSITIVE_INFINITY))
    if not math.isfinite(result) or result < 0.0:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RADIUS,
            f"{label} outward result is invalid",
        )
    return result


def _add_up(left: float, right: float, *, label: str) -> float:
    _require_nonnegative_finite_float(left, label=f"{label} left")
    _require_nonnegative_finite_float(right, label=f"{label} right")
    with np.errstate(over="ignore", invalid="ignore"):
        rounded = float(np.add(np.float64(left), np.float64(right)))
    if not math.isfinite(rounded) or rounded < 0.0:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_RADIUS, f"{label} overflowed")
    return _next_up(rounded, label=label)


def _mul_up(left: float, right: float, *, label: str) -> float:
    _require_nonnegative_finite_float(left, label=f"{label} left")
    _require_nonnegative_finite_float(right, label=f"{label} right")
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        rounded = float(np.multiply(np.float64(left), np.float64(right)))
    if not math.isfinite(rounded) or rounded < 0.0:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_RADIUS, f"{label} overflowed")
    return _next_up(rounded, label=label)


def _sub_up(left: float, right: float, *, label: str) -> float:
    if (
        type(left) is not float
        or type(right) is not float
        or not math.isfinite(left)
        or not math.isfinite(right)
        or left < right
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_CENTRE, f"{label} is not nonnegative")
    with np.errstate(over="ignore", invalid="ignore"):
        rounded = float(np.subtract(np.float64(left), np.float64(right)))
    if not math.isfinite(rounded) or rounded < 0.0:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_RADIUS, f"{label} overflowed")
    return _next_up(rounded, label=label)


def _fraction_upper(value: Fraction, *, label: str) -> float:
    if type(value) is not Fraction or value < 0:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, f"{label} witness is invalid")
    try:
        candidate = float(value)
    except OverflowError as error:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RADIUS,
            f"{label} does not fit binary64",
        ) from error
    if not math.isfinite(candidate):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_RADIUS, f"{label} does not fit binary64")
    if Fraction.from_float(candidate) < value:
        candidate = _next_up(candidate, label=f"{label} conversion")
    if Fraction.from_float(candidate) < value:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_RADIUS, f"{label} is not outward")
    return candidate


@dataclass(frozen=True, slots=True)
class RateActionContract:
    schema: str
    tensor_shape: tuple[int, ...]
    state_count: int
    block_size: int
    block_capacity: int
    maximum_scratch_bytes: int
    maximum_numeric_payload_bytes: int
    required_peak_numeric_payload_bytes: int
    maximum_total_payload_bytes: int
    required_peak_total_payload_bytes: int
    runtime: str
    point_lift_schema: str
    point_lift_zero_policy: str
    scalar_operation_model_sha256: str
    p_formula_id: str
    q_formula_id: str
    stage1_source_sha256: str
    stage1_source_byte_length: int
    directed_source_sha256: str
    directed_source_byte_length: int
    composition_source_sha256: str
    composition_source_byte_length: int
    maximum_subordinate_serialization_payload_bytes: int
    stage1_action_contract_sha256: str
    directed_action_contract_sha256: str
    directed_backend_binding_sha256: str
    stage1_kernel_construction: str
    stage1_kernel_backend: str
    stage1_action_backend: str
    directed_backend: str
    worker_private: bool
    same_process_non_authoritative: bool
    total_payload_preflight_is_conservative_upper_bound: bool
    science_free: bool


@dataclass(frozen=True, slots=True)
class InternalPointBallInput:
    schema: str
    logical_shape: tuple[int, ...]
    nominal: np.ndarray
    nominal_raw_sha256: str
    source_vector_raw_sha256: str
    input_l1_radius_upper: float
    input_l1_radius_upper_hex: str
    radius_provenance_sha256: str
    input_binding_sha256: str
    nonnegative_nominal: bool
    input_radius_authority: str
    status: str
    worker_private: bool
    arrays_exposed: bool
    authoritative: bool
    fresh_process: bool
    science_executed: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class ExactWitnessUpper:
    name: str
    numerator: int
    denominator: int
    flat_index: int
    upper: float
    upper_hex: str


@dataclass(frozen=True, slots=True)
class ScalarTraceEntry:
    name: str
    value_hex: str


@dataclass(frozen=True, slots=True)
class RateActionMemoryLedger:
    schema: str
    state_count: int
    block_size: int
    block_capacity: int
    source_nominal_payload_bytes: int
    point_lift_payload_bytes: int
    directed_output_payload_bytes: int
    nominal_output_payload_bytes: int
    point_lift_validation_scratch_payload_bytes: int
    directed_workspace_payload_bytes: int
    directed_validation_scratch_payload_bytes: int
    directed_runtime_probe_payload_bytes: int
    nominal_workspace_payload_bytes: int
    point_lift_builder_zero_scratch_payload_bytes: int
    input_default_validation_scratch_payload_bytes: int
    kernel_interval_validation_scratch_payload_bytes: int
    directed_output_validation_scratch_payload_bytes: int
    nominal_output_validation_scratch_payload_bytes: int
    canonical_json_stream_text_payload_bytes: int
    canonical_json_stream_encoded_payload_bytes: int
    canonical_json_stream_chunk_scratch_payload_bytes: int
    source_hash_stream_scratch_payload_bytes: int
    maximum_subordinate_source_read_payload_bytes: int
    maximum_subordinate_serialization_payload_bytes: int
    subordinate_serialization_is_conservative_bound: bool
    preflight_binding_phase_payload_bytes: int
    point_lift_build_validate_phase_bytes: int
    directed_action_phase_bytes: int
    nominal_action_phase_bytes: int
    final_binding_revalidation_phase_bytes: int
    declared_peak_numeric_payload_bytes: int
    maximum_numeric_payload_bytes: int
    required_peak_numeric_payload_bytes: int
    result_consistency_serialization_payload_bytes: int
    result_consistency_phase_payload_bytes: int
    declared_peak_total_payload_bytes: int
    maximum_total_payload_bytes: int
    required_peak_total_payload_bytes: int
    retained_output_numeric_payload_bytes: int
    raw_serialization_payload_bytes: int
    full_serialization_payload_materialized: bool
    total_payload_is_conservative_upper_bound: bool
    production_memory_exact: bool
    caller_array_excluded: bool
    preowned_kernel_excluded: bool


@dataclass(frozen=True, slots=True)
class RateActionDerivationLedger:
    schema: str
    operator: str
    formula_id: str
    tensor_shape: tuple[int, ...]
    block_size: int
    block_count: int
    covered_state_count: int
    flat_index_first: int
    flat_index_stop: int
    nominal_l1_reduction_count: int
    centre_radius_reduction_count: int
    centre_subtraction_count: int
    fraction_upper_conversion_count: int
    fraction_upper_nextafter_count: int
    scalar_add_up_count: int
    scalar_mul_up_count: int
    scalar_sub_up_count: int
    scalar_nextafter_count: int
    kernel_replay_sha256: str
    source_chain_sha256: str
    derived_chain_sha256: str
    combined_chain_sha256: str
    witness_binding_sha256: str
    composition_contract_sha256: str
    directed_action_contract_sha256: str
    nominal_action_contract_sha256: str
    input_nominal_raw_sha256: str
    source_vector_raw_sha256: str
    point_lift_raw_sha256: str
    point_lift_binding_sha256: str
    directed_output_raw_sha256: str
    nominal_output_raw_sha256: str
    radius_provenance_sha256: str
    point_lift_zero_policy: str
    witnesses: tuple[ExactWitnessUpper, ...]
    scalar_trace: tuple[ScalarTraceEntry, ...]
    input_and_kernel_rechecked_after_actions: bool
    contract_and_sources_rechecked_after_actions: bool
    point_lift_rechecked_after_actions: bool
    nominal_inside_directed_box: bool
    science_executed: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class InternalRateActionState:
    schema: str
    operator: str
    logical_shape: tuple[int, ...]
    nominal: np.ndarray
    nominal_raw_sha256: str
    l1_radius_upper: float
    l1_radius_upper_hex: str
    radius_provenance_sha256: str
    contract_sha256: str
    derivation: RateActionDerivationLedger
    memory: RateActionMemoryLedger
    consistency_sha256: str
    status: str
    nonnegative_nominal: bool
    worker_private: bool
    arrays_exposed: bool
    authoritative: bool
    fresh_process: bool
    verifier_owned_reconstruction: bool
    science_executed: bool
    f0_pass: bool


def _required_peak_numeric_payload_bytes(
    shape: tuple[int, ...],
    *,
    block_size: int,
) -> int:
    states = math.prod(shape)
    capacity = min(states, block_size)
    return max(
        24 * states + 2 * capacity,
        40 * states
        + max(
            directed.WORKSPACE_BYTES_PER_BLOCK_STATE * capacity,
            directed.VALIDATION_BYTES_PER_BLOCK_STATE * capacity,
            directed.VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES,
        ),
        48 * states + packed.ACTION_WORKSPACE_BYTES_PER_STATE * capacity,
        48 * states + 2 * capacity,
    )


def _required_peak_total_payload_bytes(
    shape: tuple[int, ...],
    *,
    block_size: int,
    maximum_subordinate_source_read_payload_bytes: int,
    maximum_subordinate_serialization_payload_bytes: int = (
        _MAXIMUM_SUBORDINATE_SERIALIZATION_PAYLOAD_BYTES
    ),
) -> int:
    states = math.prod(shape)
    capacity = min(states, block_size)
    scalar_binding = max(
        _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES,
        _SOURCE_HASH_STREAM_CHUNK_BYTES,
        directed.VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES,
        maximum_subordinate_source_read_payload_bytes,
        maximum_subordinate_serialization_payload_bytes,
    )
    return max(
        8 * states + scalar_binding,
        24 * states
        + max(
            2 * capacity,
            min(states, packed.DEFAULT_VALIDATION_BLOCK_SIZE),
            _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES,
        ),
        40 * states
        + max(
            directed.WORKSPACE_BYTES_PER_BLOCK_STATE * capacity,
            directed.VALIDATION_BYTES_PER_BLOCK_STATE * capacity,
            directed.VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES,
            maximum_subordinate_source_read_payload_bytes,
            maximum_subordinate_serialization_payload_bytes,
            _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES,
        ),
        48 * states
        + max(
            packed.ACTION_WORKSPACE_BYTES_PER_STATE * capacity,
            2 * capacity,
            capacity,
            maximum_subordinate_serialization_payload_bytes,
        ),
        48 * states + max(2 * capacity, scalar_binding),
        48 * states + _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES,
    )


def _contract_json(contract: RateActionContract) -> dict[str, object]:
    return {
        "block_size": contract.block_size,
        "block_capacity": contract.block_capacity,
        "composition_source_sha256": contract.composition_source_sha256,
        "directed_action_contract_sha256": contract.directed_action_contract_sha256,
        "directed_backend": contract.directed_backend,
        "directed_backend_binding_sha256": contract.directed_backend_binding_sha256,
        "directed_source_sha256": contract.directed_source_sha256,
        "maximum_scratch_bytes": contract.maximum_scratch_bytes,
        "maximum_numeric_payload_bytes": contract.maximum_numeric_payload_bytes,
        "maximum_total_payload_bytes": contract.maximum_total_payload_bytes,
        "maximum_subordinate_serialization_payload_bytes": contract.maximum_subordinate_serialization_payload_bytes,
        "p_formula_id": contract.p_formula_id,
        "point_lift_schema": contract.point_lift_schema,
        "point_lift_zero_policy": contract.point_lift_zero_policy,
        "q_formula_id": contract.q_formula_id,
        "runtime": contract.runtime,
        "same_process_non_authoritative": contract.same_process_non_authoritative,
        "total_payload_preflight_is_conservative_upper_bound": contract.total_payload_preflight_is_conservative_upper_bound,
        "scalar_operation_model_sha256": contract.scalar_operation_model_sha256,
        "schema": contract.schema,
        "science_free": contract.science_free,
        "stage1_action_backend": contract.stage1_action_backend,
        "stage1_action_contract_sha256": contract.stage1_action_contract_sha256,
        "stage1_kernel_backend": contract.stage1_kernel_backend,
        "stage1_kernel_construction": contract.stage1_kernel_construction,
        "stage1_source_sha256": contract.stage1_source_sha256,
        "stage1_source_byte_length": contract.stage1_source_byte_length,
        "state_count": contract.state_count,
        "tensor_shape": list(contract.tensor_shape),
        "required_peak_numeric_payload_bytes": contract.required_peak_numeric_payload_bytes,
        "required_peak_total_payload_bytes": contract.required_peak_total_payload_bytes,
        "directed_source_byte_length": contract.directed_source_byte_length,
        "composition_source_byte_length": contract.composition_source_byte_length,
        "worker_private": contract.worker_private,
    }


def rate_action_contract_sha256(contract: RateActionContract) -> str:
    validate_rate_action_contract(contract)
    return _canonical_json_digest(_contract_json(contract))


def _reconstruct_subordinate_contracts(
    contract: RateActionContract,
) -> tuple[packed.BlockActionContract, directed.DirectedActionContract]:
    nominal_contract = packed.make_block_action_contract(
        contract.tensor_shape,
        block_size=contract.block_size,
        maximum_scratch_bytes=contract.maximum_scratch_bytes,
    )
    directed_contract = directed.make_directed_action_contract(
        contract.tensor_shape,
        block_size=contract.block_size,
        maximum_scratch_bytes=contract.maximum_scratch_bytes,
    )
    if (
        not hmac.compare_digest(
            packed._action_contract_digest(nominal_contract),
            contract.stage1_action_contract_sha256,
        )
        or not hmac.compare_digest(
            directed.directed_action_contract_sha256(directed_contract),
            contract.directed_action_contract_sha256,
        )
        or not hmac.compare_digest(
            directed_contract.backend_binding_sha256,
            contract.directed_backend_binding_sha256,
        )
        or not hmac.compare_digest(
            directed_contract.stage1_action_contract_sha256,
            contract.stage1_action_contract_sha256,
        )
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "internally reconstructed nominal/directed contracts changed",
        )
    return nominal_contract, directed_contract


def make_rate_action_contract(
    directed_contract: directed.DirectedActionContract,
    *,
    maximum_numeric_payload_bytes: int,
    maximum_total_payload_bytes: int,
) -> RateActionContract:
    """Create a composition contract from one accepted directed contract.

    The stage-1 nominal contract is not caller supplied.  It is reconstructed
    here and again on every validation/action.
    """

    directed.validate_directed_action_contract(directed_contract)
    nominal_contract = packed.make_block_action_contract(
        directed_contract.tensor_shape,
        block_size=directed_contract.block_size,
        maximum_scratch_bytes=directed_contract.maximum_scratch_bytes,
    )
    nominal_digest = packed._action_contract_digest(nominal_contract)
    if not hmac.compare_digest(
        nominal_digest,
        directed_contract.stage1_action_contract_sha256,
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "directed contract does not bind the reconstructed nominal contract",
        )
    states = math.prod(directed_contract.tensor_shape)
    capacity = min(states, directed_contract.block_size)
    required_peak = _required_peak_numeric_payload_bytes(
        directed_contract.tensor_shape,
        block_size=directed_contract.block_size,
    )
    stage1_source_byte_length = _source_byte_length(packed.__file__)
    directed_source_byte_length = _source_byte_length(directed.__file__)
    source_read_peak = max(stage1_source_byte_length, directed_source_byte_length)
    required_total_peak = _required_peak_total_payload_bytes(
        directed_contract.tensor_shape,
        block_size=directed_contract.block_size,
        maximum_subordinate_source_read_payload_bytes=source_read_peak,
    )
    if (
        type(maximum_numeric_payload_bytes) is not int
        or maximum_numeric_payload_bytes < required_peak
        or type(maximum_total_payload_bytes) is not int
        or maximum_total_payload_bytes < required_total_peak
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RESOURCE,
            "declared composition numeric/total cap misses the preflight peak",
        )
    contract = RateActionContract(
        schema=RATE_ACTION_CONTRACT_SCHEMA,
        tensor_shape=directed_contract.tensor_shape,
        state_count=states,
        block_size=directed_contract.block_size,
        block_capacity=capacity,
        maximum_scratch_bytes=directed_contract.maximum_scratch_bytes,
        maximum_numeric_payload_bytes=maximum_numeric_payload_bytes,
        required_peak_numeric_payload_bytes=required_peak,
        maximum_total_payload_bytes=maximum_total_payload_bytes,
        required_peak_total_payload_bytes=required_total_peak,
        runtime=_runtime_identity(),
        point_lift_schema=POINT_LIFT_SCHEMA,
        point_lift_zero_policy=POINT_LIFT_ZERO_POLICY,
        scalar_operation_model_sha256=_operation_model_sha256(),
        p_formula_id=P_FORMULA_ID,
        q_formula_id=Q_FORMULA_ID,
        stage1_source_sha256=directed_contract.stage1_source_sha256,
        stage1_source_byte_length=stage1_source_byte_length,
        directed_source_sha256=directed_contract.directed_source_sha256,
        directed_source_byte_length=directed_source_byte_length,
        composition_source_sha256=_source_sha256(__file__),
        composition_source_byte_length=_source_byte_length(__file__),
        maximum_subordinate_serialization_payload_bytes=_MAXIMUM_SUBORDINATE_SERIALIZATION_PAYLOAD_BYTES,
        stage1_action_contract_sha256=nominal_digest,
        directed_action_contract_sha256=directed.directed_action_contract_sha256(directed_contract),
        directed_backend_binding_sha256=directed_contract.backend_binding_sha256,
        stage1_kernel_construction=packed.KERNEL_CONSTRUCTION,
        stage1_kernel_backend=packed.STREAMING_BACKEND,
        stage1_action_backend=packed.ACTION_BACKEND,
        directed_backend=directed.DIRECTED_BACKEND,
        worker_private=True,
        same_process_non_authoritative=True,
        total_payload_preflight_is_conservative_upper_bound=True,
        science_free=True,
    )
    validate_rate_action_contract(contract)
    return contract


def validate_rate_action_contract(contract: RateActionContract) -> None:
    if type(contract) is not RateActionContract:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_SCHEMA, "contract has wrong exact type")
    string_fields = (
        contract.schema,
        contract.runtime,
        contract.point_lift_schema,
        contract.point_lift_zero_policy,
        contract.scalar_operation_model_sha256,
        contract.p_formula_id,
        contract.q_formula_id,
        contract.stage1_source_sha256,
        contract.directed_source_sha256,
        contract.composition_source_sha256,
        contract.stage1_action_contract_sha256,
        contract.directed_action_contract_sha256,
        contract.directed_backend_binding_sha256,
        contract.stage1_kernel_construction,
        contract.stage1_kernel_backend,
        contract.stage1_action_backend,
        contract.directed_backend,
    )
    if any(type(value) is not str for value in string_fields):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "composition contract string fields changed type",
        )
    if (
        contract.schema != RATE_ACTION_CONTRACT_SCHEMA
        or type(contract.tensor_shape) is not tuple
        or not contract.tensor_shape
        or len(contract.tensor_shape) > packed.MAXIMUM_DIMENSIONS
        or any(type(entry) is not int or entry < 2 for entry in contract.tensor_shape)
        or type(contract.state_count) is not int
        or contract.state_count != math.prod(contract.tensor_shape)
        or type(contract.block_size) is not int
        or contract.block_size < 1
        or type(contract.block_capacity) is not int
        or contract.block_capacity != min(contract.state_count, contract.block_size)
        or type(contract.maximum_scratch_bytes) is not int
        or contract.maximum_scratch_bytes < 1
        or type(contract.maximum_numeric_payload_bytes) is not int
        or type(contract.required_peak_numeric_payload_bytes) is not int
        or contract.required_peak_numeric_payload_bytes
        != _required_peak_numeric_payload_bytes(
            contract.tensor_shape,
            block_size=contract.block_size,
        )
        or contract.maximum_numeric_payload_bytes < contract.required_peak_numeric_payload_bytes
        or contract.runtime != _runtime_identity()
        or contract.point_lift_schema != POINT_LIFT_SCHEMA
        or contract.point_lift_zero_policy != POINT_LIFT_ZERO_POLICY
        or contract.scalar_operation_model_sha256 != _operation_model_sha256()
        or contract.p_formula_id != P_FORMULA_ID
        or contract.q_formula_id != Q_FORMULA_ID
        or not all(
            _is_hex_digest(value)
            for value in (
                contract.stage1_source_sha256,
                contract.directed_source_sha256,
                contract.composition_source_sha256,
                contract.stage1_action_contract_sha256,
                contract.directed_action_contract_sha256,
                contract.directed_backend_binding_sha256,
            )
        )
        or contract.stage1_source_sha256 != _source_sha256(packed.__file__)
        or type(contract.stage1_source_byte_length) is not int
        or contract.stage1_source_byte_length != _source_byte_length(packed.__file__)
        or contract.directed_source_sha256 != _source_sha256(directed.__file__)
        or type(contract.directed_source_byte_length) is not int
        or contract.directed_source_byte_length != _source_byte_length(directed.__file__)
        or contract.composition_source_sha256 != _source_sha256(__file__)
        or type(contract.composition_source_byte_length) is not int
        or contract.composition_source_byte_length != _source_byte_length(__file__)
        or type(contract.maximum_subordinate_serialization_payload_bytes) is not int
        or contract.maximum_subordinate_serialization_payload_bytes
        != _MAXIMUM_SUBORDINATE_SERIALIZATION_PAYLOAD_BYTES
        or type(contract.maximum_total_payload_bytes) is not int
        or type(contract.required_peak_total_payload_bytes) is not int
        or contract.required_peak_total_payload_bytes
        != _required_peak_total_payload_bytes(
            contract.tensor_shape,
            block_size=contract.block_size,
            maximum_subordinate_source_read_payload_bytes=max(
                contract.stage1_source_byte_length,
                contract.directed_source_byte_length,
            ),
        )
        or contract.maximum_total_payload_bytes < contract.required_peak_total_payload_bytes
        or contract.stage1_kernel_construction != packed.KERNEL_CONSTRUCTION
        or contract.stage1_kernel_backend != packed.STREAMING_BACKEND
        or contract.stage1_action_backend != packed.ACTION_BACKEND
        or contract.directed_backend != directed.DIRECTED_BACKEND
        or type(contract.worker_private) is not bool
        or contract.worker_private is not True
        or type(contract.same_process_non_authoritative) is not bool
        or contract.same_process_non_authoritative is not True
        or type(contract.total_payload_preflight_is_conservative_upper_bound) is not bool
        or contract.total_payload_preflight_is_conservative_upper_bound is not True
        or type(contract.science_free) is not bool
        or contract.science_free is not True
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "composition contract is inconsistent with current sources/runtime",
        )
    _reconstruct_subordinate_contracts(contract)


def _require_owned_readonly_vector(array: object, *, states: int, label: str) -> np.ndarray:
    if type(array) is not np.ndarray:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_ARRAY, f"{label} has wrong exact type")
    if (
        array.dtype != np.dtype(np.float64)
        or not array.dtype.isnative
        or array.shape != (states,)
        or not array.flags.c_contiguous
        or not array.flags.aligned
        or not array.flags.owndata
        or array.base is not None
        or array.flags.writeable
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_ARRAY,
            f"{label} is not owned native readonly binary64",
        )
    return array


def _input_binding_payload(state: InternalPointBallInput) -> dict[str, object]:
    return {
        "arrays_exposed": state.arrays_exposed,
        "authoritative": state.authoritative,
        "f0_pass": state.f0_pass,
        "fresh_process": state.fresh_process,
        "input_l1_radius_upper_hex": state.input_l1_radius_upper_hex,
        "input_radius_authority": state.input_radius_authority,
        "logical_shape": list(state.logical_shape),
        "nominal_raw_sha256": state.nominal_raw_sha256,
        "nonnegative_nominal": state.nonnegative_nominal,
        "radius_provenance_sha256": state.radius_provenance_sha256,
        "schema": state.schema,
        "science_executed": state.science_executed,
        "source_vector_raw_sha256": state.source_vector_raw_sha256,
        "status": state.status,
        "worker_private": state.worker_private,
    }


def make_internal_point_ball_input(
    vector: packed.CanonicalFloat64Vector,
    *,
    input_l1_radius_upper: float,
    radius_provenance_sha256: str,
) -> InternalPointBallInput:
    """Deep-copy a method-only input into worker-private numerical storage."""

    packed.validate_canonical_vector(vector)
    radius = _require_nonnegative_finite_float(
        input_l1_radius_upper,
        label="input l1 radius upper",
    )
    if not _is_hex_digest(radius_provenance_sha256):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "input radius provenance must be a SHA-256 digest",
        )
    private = np.empty(vector.values.shape, dtype=np.float64)
    memoryview(private).cast("B")[:] = memoryview(vector.values).cast("B")
    private.setflags(write=False)
    raw = _raw_sha256(private)
    provisional = InternalPointBallInput(
        schema=RATE_ACTION_INPUT_SCHEMA,
        logical_shape=vector.logical_shape,
        nominal=private,
        nominal_raw_sha256=raw,
        source_vector_raw_sha256=vector.raw_sha256,
        input_l1_radius_upper=radius,
        input_l1_radius_upper_hex=radius.hex(),
        radius_provenance_sha256=radius_provenance_sha256,
        input_binding_sha256="0" * 64,
        nonnegative_nominal=vector.nonnegative,
        input_radius_authority=INPUT_RADIUS_AUTHORITY,
        status=INPUT_STATUS,
        worker_private=True,
        arrays_exposed=True,
        authoritative=False,
        fresh_process=False,
        science_executed=False,
        f0_pass=False,
    )
    state = replace(
        provisional,
        input_binding_sha256=_canonical_json_digest(_input_binding_payload(provisional)),
    )
    validate_internal_point_ball_input(state)
    return state


def validate_internal_point_ball_input(state: InternalPointBallInput) -> None:
    if type(state) is not InternalPointBallInput:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_SCHEMA, "input state has wrong exact type")
    if (
        type(state.logical_shape) is not tuple
        or not state.logical_shape
        or any(type(entry) is not int or entry < 2 for entry in state.logical_shape)
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_SCHEMA, "input shape is invalid")
    nominal = _require_owned_readonly_vector(
        state.nominal,
        states=math.prod(state.logical_shape),
        label="input nominal",
    )
    if (
        type(state.schema) is not str
        or state.schema != RATE_ACTION_INPUT_SCHEMA
        or not _is_hex_digest(state.nominal_raw_sha256)
        or not hmac.compare_digest(state.nominal_raw_sha256, _raw_sha256(nominal))
        or not _is_hex_digest(state.source_vector_raw_sha256)
        or _require_nonnegative_finite_float(
            state.input_l1_radius_upper,
            label="input l1 radius upper",
        )
        != state.input_l1_radius_upper
        or type(state.input_l1_radius_upper_hex) is not str
        or len(state.input_l1_radius_upper_hex) > 32
        or state.input_l1_radius_upper_hex != state.input_l1_radius_upper.hex()
        or not _is_hex_digest(state.radius_provenance_sha256)
        or not _is_hex_digest(state.input_binding_sha256)
        or type(state.nonnegative_nominal) is not bool
        or type(state.input_radius_authority) is not str
        or state.input_radius_authority != INPUT_RADIUS_AUTHORITY
        or type(state.status) is not str
        or state.status != INPUT_STATUS
        or state.worker_private is not True
        or state.arrays_exposed is not True
        or state.authoritative is not False
        or state.fresh_process is not False
        or state.science_executed is not False
        or state.f0_pass is not False
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, "input state binding changed")
    wrapper = packed.CanonicalFloat64Vector(
        logical_shape=state.logical_shape,
        values=nominal,
        raw_sha256=state.nominal_raw_sha256,
        nonnegative=state.nonnegative_nominal,
        source_sha256=state.source_vector_raw_sha256,
    )
    packed.validate_canonical_vector(wrapper)
    if not hmac.compare_digest(
        state.input_binding_sha256,
        _canonical_json_digest(_input_binding_payload(state)),
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, "input digest changed")


def _point_lift_binding_sha256(
    *,
    state: InternalPointBallInput,
    point_lift_raw_sha256: str,
    block_size: int,
) -> str:
    return _canonical_json_digest(
        {
            "block_size": block_size,
            "logical_shape": list(state.logical_shape),
            "point_lift_raw_sha256": point_lift_raw_sha256,
            "schema": POINT_LIFT_SCHEMA,
            "source_nominal_raw_sha256": state.nominal_raw_sha256,
            "source_vector_raw_sha256": state.source_vector_raw_sha256,
            "zero_policy": POINT_LIFT_ZERO_POLICY,
        }
    )


def _validate_point_lift_binding(
    point_lift: packed.CanonicalPackedIntervals,
    state: InternalPointBallInput,
    *,
    block_size: int,
) -> None:
    packed.validate_canonical_packed_intervals(point_lift)
    validate_internal_point_ball_input(state)
    if (
        point_lift.manifest.logical_shape != state.logical_shape
        or point_lift.manifest.block_size != block_size
        or point_lift.manifest.nonnegative is not state.nonnegative_nominal
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_POINT_LIFT, "point-lift metadata changed")
    states = math.prod(state.logical_shape)
    capacity = min(states, block_size)
    scratch = np.empty((2, capacity), dtype=np.bool_)
    for start in range(0, states, block_size):
        stop = min(states, start + block_size)
        count = stop - start
        source = state.nominal[start:stop]
        block = point_lift.intervals[start:stop]
        first = scratch[0, :count]
        second = scratch[1, :count]
        np.equal(block[:, 0], source, out=first)
        np.equal(block[:, 1], source, out=second)
        if not bool(np.all(first)) or not bool(np.all(second)):
            raise packed.PackedF0Failure(
                HOLD_RATE_ACTION_POINT_LIFT,
                "point lift differs from its source nominal",
            )
        np.equal(source, 0.0, out=first)
        for endpoint in range(2):
            np.signbit(block[:, endpoint], out=second)
            np.logical_and(first, second, out=second)
            if bool(np.any(second)):
                raise packed.PackedF0Failure(
                    HOLD_RATE_ACTION_POINT_LIFT,
                    "point lift retained a negative zero",
                )


def _build_point_lift(
    state: InternalPointBallInput,
    *,
    block_size: int,
) -> tuple[packed.CanonicalPackedIntervals, str]:
    validate_internal_point_ball_input(state)
    states = math.prod(state.logical_shape)
    capacity = min(states, block_size)
    lift = np.empty((states, 2), dtype=np.float64, order="C")
    zero_scratch = np.empty(capacity, dtype=np.bool_)
    for start in range(0, states, block_size):
        stop = min(states, start + block_size)
        count = stop - start
        source = state.nominal[start:stop]
        lift[start:stop, 0] = source
        lift[start:stop, 1] = source
        np.equal(source, 0.0, out=zero_scratch[:count])
        np.copyto(lift[start:stop, 0], 0.0, where=zero_scratch[:count])
        np.copyto(lift[start:stop, 1], 0.0, where=zero_scratch[:count])
    del zero_scratch
    lift.setflags(write=False)
    raw = _raw_sha256(lift)
    manifest = packed.PackedIntervalManifest(
        schema=packed.PACKED_INTERVAL_SCHEMA,
        role="science_free_rate_action_point_lift",
        logical_shape=state.logical_shape,
        array_shape=(states, 2),
        state_count=states,
        raw_byte_length=lift.nbytes,
        raw_sha256=raw,
        endpoint_order=packed.ENDPOINT_ORDER,
        nonnegative=state.nonnegative_nominal,
        block_size=block_size,
        maximum_working_bytes=POINT_LIFT_VALIDATION_BYTES_PER_BLOCK_STATE * capacity,
    )
    point_lift = packed.CanonicalPackedIntervals(manifest=manifest, intervals=lift)
    _validate_point_lift_binding(point_lift, state, block_size=block_size)
    return point_lift, _point_lift_binding_sha256(
        state=state,
        point_lift_raw_sha256=raw,
        block_size=block_size,
    )


def _memory_ledger(
    contract: RateActionContract,
    *,
    nominal_contract: packed.BlockActionContract,
    directed_contract: directed.DirectedActionContract,
) -> RateActionMemoryLedger:
    states = math.prod(contract.tensor_shape)
    capacity = min(states, contract.block_size)
    source = SOURCE_NOMINAL_BYTES_PER_STATE * states
    lift = POINT_LIFT_BYTES_PER_STATE * states
    directed_output = DIRECTED_OUTPUT_BYTES_PER_STATE * states
    nominal_output = NOMINAL_OUTPUT_BYTES_PER_STATE * states
    lift_validation = POINT_LIFT_VALIDATION_BYTES_PER_BLOCK_STATE * capacity
    input_default_validation = min(states, packed.DEFAULT_VALIDATION_BLOCK_SIZE)
    point_lift_builder_zero_scratch = capacity
    kernel_interval_validation = 2 * capacity
    directed_output_validation = 2 * capacity
    nominal_output_validation = capacity
    source_read = max(
        contract.stage1_source_byte_length,
        contract.directed_source_byte_length,
    )
    scalar_binding_scratch = max(
        _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES,
        _SOURCE_HASH_STREAM_CHUNK_BYTES,
        directed.VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES,
        source_read,
        contract.maximum_subordinate_serialization_payload_bytes,
    )
    preflight_phase = source + scalar_binding_scratch
    point_phase = (
        source
        + lift
        + max(
            lift_validation,
            point_lift_builder_zero_scratch,
            input_default_validation,
            _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES,
        )
    )
    directed_phase = (
        source
        + lift
        + directed_output
        + max(
            directed_contract.workspace_payload_bytes,
            directed_contract.validation_scratch_payload_bytes,
            directed_contract.runtime_probe_payload_bytes,
            source_read,
            kernel_interval_validation,
            directed_output_validation,
            contract.maximum_subordinate_serialization_payload_bytes,
            _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES,
        )
    )
    nominal_phase = (
        source
        + lift
        + directed_output
        + nominal_output
        + max(
            nominal_contract.scratch_payload_bytes,
            kernel_interval_validation,
            nominal_output_validation,
            contract.maximum_subordinate_serialization_payload_bytes,
        )
    )
    final_phase = (
        source
        + lift
        + directed_output
        + nominal_output
        + max(
            lift_validation,
            input_default_validation,
            kernel_interval_validation,
            directed_output_validation,
            nominal_output_validation,
            scalar_binding_scratch,
        )
    )
    numeric_peak = _required_peak_numeric_payload_bytes(
        contract.tensor_shape,
        block_size=contract.block_size,
    )
    result_consistency_phase = (
        source
        + lift
        + directed_output
        + nominal_output
        + _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES
    )
    ledger = RateActionMemoryLedger(
        schema=RATE_ACTION_MEMORY_SCHEMA,
        state_count=states,
        block_size=contract.block_size,
        block_capacity=capacity,
        source_nominal_payload_bytes=source,
        point_lift_payload_bytes=lift,
        directed_output_payload_bytes=directed_output,
        nominal_output_payload_bytes=nominal_output,
        point_lift_validation_scratch_payload_bytes=lift_validation,
        directed_workspace_payload_bytes=directed_contract.workspace_payload_bytes,
        directed_validation_scratch_payload_bytes=directed_contract.validation_scratch_payload_bytes,
        directed_runtime_probe_payload_bytes=directed_contract.runtime_probe_payload_bytes,
        nominal_workspace_payload_bytes=nominal_contract.scratch_payload_bytes,
        point_lift_builder_zero_scratch_payload_bytes=point_lift_builder_zero_scratch,
        input_default_validation_scratch_payload_bytes=input_default_validation,
        kernel_interval_validation_scratch_payload_bytes=kernel_interval_validation,
        directed_output_validation_scratch_payload_bytes=directed_output_validation,
        nominal_output_validation_scratch_payload_bytes=nominal_output_validation,
        canonical_json_stream_text_payload_bytes=_CANONICAL_JSON_STREAM_CHUNK_LIMIT,
        canonical_json_stream_encoded_payload_bytes=_CANONICAL_JSON_STREAM_CHUNK_LIMIT,
        canonical_json_stream_chunk_scratch_payload_bytes=(
            _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES
        ),
        source_hash_stream_scratch_payload_bytes=_SOURCE_HASH_STREAM_CHUNK_BYTES,
        maximum_subordinate_source_read_payload_bytes=source_read,
        maximum_subordinate_serialization_payload_bytes=(
            contract.maximum_subordinate_serialization_payload_bytes
        ),
        subordinate_serialization_is_conservative_bound=True,
        preflight_binding_phase_payload_bytes=preflight_phase,
        point_lift_build_validate_phase_bytes=point_phase,
        directed_action_phase_bytes=directed_phase,
        nominal_action_phase_bytes=nominal_phase,
        final_binding_revalidation_phase_bytes=final_phase,
        declared_peak_numeric_payload_bytes=numeric_peak,
        maximum_numeric_payload_bytes=contract.maximum_numeric_payload_bytes,
        required_peak_numeric_payload_bytes=contract.required_peak_numeric_payload_bytes,
        result_consistency_serialization_payload_bytes=(
            _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES
        ),
        result_consistency_phase_payload_bytes=result_consistency_phase,
        declared_peak_total_payload_bytes=max(
            preflight_phase,
            point_phase,
            directed_phase,
            nominal_phase,
            final_phase,
            result_consistency_phase,
        ),
        maximum_total_payload_bytes=contract.maximum_total_payload_bytes,
        required_peak_total_payload_bytes=contract.required_peak_total_payload_bytes,
        retained_output_numeric_payload_bytes=RETAINED_OUTPUT_BYTES_PER_STATE * states,
        raw_serialization_payload_bytes=_CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES,
        full_serialization_payload_materialized=False,
        total_payload_is_conservative_upper_bound=True,
        production_memory_exact=False,
        caller_array_excluded=True,
        preowned_kernel_excluded=True,
    )
    validate_rate_action_memory_ledger(ledger)
    return ledger


def validate_rate_action_memory_ledger(ledger: RateActionMemoryLedger) -> None:
    if type(ledger) is not RateActionMemoryLedger:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_SCHEMA, "memory ledger type changed")
    integer_fields = (
        ledger.state_count,
        ledger.block_size,
        ledger.block_capacity,
        ledger.source_nominal_payload_bytes,
        ledger.point_lift_payload_bytes,
        ledger.directed_output_payload_bytes,
        ledger.nominal_output_payload_bytes,
        ledger.point_lift_validation_scratch_payload_bytes,
        ledger.directed_workspace_payload_bytes,
        ledger.directed_validation_scratch_payload_bytes,
        ledger.directed_runtime_probe_payload_bytes,
        ledger.nominal_workspace_payload_bytes,
        ledger.point_lift_builder_zero_scratch_payload_bytes,
        ledger.input_default_validation_scratch_payload_bytes,
        ledger.kernel_interval_validation_scratch_payload_bytes,
        ledger.directed_output_validation_scratch_payload_bytes,
        ledger.nominal_output_validation_scratch_payload_bytes,
        ledger.canonical_json_stream_text_payload_bytes,
        ledger.canonical_json_stream_encoded_payload_bytes,
        ledger.canonical_json_stream_chunk_scratch_payload_bytes,
        ledger.source_hash_stream_scratch_payload_bytes,
        ledger.maximum_subordinate_source_read_payload_bytes,
        ledger.maximum_subordinate_serialization_payload_bytes,
        ledger.preflight_binding_phase_payload_bytes,
        ledger.point_lift_build_validate_phase_bytes,
        ledger.directed_action_phase_bytes,
        ledger.nominal_action_phase_bytes,
        ledger.final_binding_revalidation_phase_bytes,
        ledger.declared_peak_numeric_payload_bytes,
        ledger.maximum_numeric_payload_bytes,
        ledger.required_peak_numeric_payload_bytes,
        ledger.result_consistency_serialization_payload_bytes,
        ledger.result_consistency_phase_payload_bytes,
        ledger.declared_peak_total_payload_bytes,
        ledger.maximum_total_payload_bytes,
        ledger.required_peak_total_payload_bytes,
        ledger.retained_output_numeric_payload_bytes,
        ledger.raw_serialization_payload_bytes,
    )
    if (
        type(ledger.schema) is not str
        or any(type(value) is not int or value < 0 for value in integer_fields)
        or ledger.state_count < 1
        or ledger.block_size < 1
        or type(ledger.full_serialization_payload_materialized) is not bool
        or type(ledger.subordinate_serialization_is_conservative_bound) is not bool
        or type(ledger.total_payload_is_conservative_upper_bound) is not bool
        or type(ledger.production_memory_exact) is not bool
        or type(ledger.caller_array_excluded) is not bool
        or type(ledger.preowned_kernel_excluded) is not bool
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RESOURCE,
            "memory ledger scalar types are invalid",
        )
    n = ledger.state_count
    c = ledger.block_capacity
    expected_source = 8 * n
    expected_lift = 16 * n
    expected_directed = 16 * n
    expected_nominal = 8 * n
    expected_validation = 2 * c
    scalar_binding_scratch = max(
        ledger.canonical_json_stream_chunk_scratch_payload_bytes,
        ledger.source_hash_stream_scratch_payload_bytes,
        ledger.directed_runtime_probe_payload_bytes,
        ledger.maximum_subordinate_source_read_payload_bytes,
        ledger.maximum_subordinate_serialization_payload_bytes,
    )
    preflight_phase = 8 * n + scalar_binding_scratch
    point_phase = 24 * n + max(
        2 * c,
        ledger.point_lift_builder_zero_scratch_payload_bytes,
        ledger.input_default_validation_scratch_payload_bytes,
        ledger.canonical_json_stream_chunk_scratch_payload_bytes,
    )
    directed_phase = 40 * n + max(
        ledger.directed_workspace_payload_bytes,
        ledger.directed_validation_scratch_payload_bytes,
        ledger.directed_runtime_probe_payload_bytes,
        ledger.maximum_subordinate_source_read_payload_bytes,
        ledger.kernel_interval_validation_scratch_payload_bytes,
        ledger.directed_output_validation_scratch_payload_bytes,
        ledger.maximum_subordinate_serialization_payload_bytes,
        ledger.canonical_json_stream_chunk_scratch_payload_bytes,
    )
    nominal_phase = 48 * n + max(
        ledger.nominal_workspace_payload_bytes,
        ledger.kernel_interval_validation_scratch_payload_bytes,
        ledger.nominal_output_validation_scratch_payload_bytes,
        ledger.maximum_subordinate_serialization_payload_bytes,
    )
    final_phase = 48 * n + max(
        2 * c,
        ledger.input_default_validation_scratch_payload_bytes,
        ledger.kernel_interval_validation_scratch_payload_bytes,
        ledger.directed_output_validation_scratch_payload_bytes,
        ledger.nominal_output_validation_scratch_payload_bytes,
        scalar_binding_scratch,
    )
    numeric_peak = _required_peak_numeric_payload_bytes(
        (n,),
        block_size=ledger.block_size,
    )
    # The helper above depends only on N and C, not on tensor rank.
    if type(ledger.result_consistency_serialization_payload_bytes) is not int:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RESOURCE,
            "result serialization length has the wrong type",
        )
    result_consistency_phase = 48 * n + ledger.result_consistency_serialization_payload_bytes
    if (
        ledger.schema != RATE_ACTION_MEMORY_SCHEMA
        or type(n) is not int
        or n < 1
        or type(ledger.block_size) is not int
        or ledger.block_size < 1
        or type(c) is not int
        or c != min(n, ledger.block_size)
        or ledger.source_nominal_payload_bytes != expected_source
        or ledger.point_lift_payload_bytes != expected_lift
        or ledger.directed_output_payload_bytes != expected_directed
        or ledger.nominal_output_payload_bytes != expected_nominal
        or ledger.point_lift_validation_scratch_payload_bytes != expected_validation
        or ledger.directed_workspace_payload_bytes != directed.WORKSPACE_BYTES_PER_BLOCK_STATE * c
        or ledger.directed_validation_scratch_payload_bytes
        != directed.VALIDATION_BYTES_PER_BLOCK_STATE * c
        or ledger.directed_runtime_probe_payload_bytes
        != directed.VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES
        or ledger.nominal_workspace_payload_bytes != packed.ACTION_WORKSPACE_BYTES_PER_STATE * c
        or ledger.point_lift_builder_zero_scratch_payload_bytes != c
        or ledger.input_default_validation_scratch_payload_bytes
        != min(n, packed.DEFAULT_VALIDATION_BLOCK_SIZE)
        or ledger.kernel_interval_validation_scratch_payload_bytes != 2 * c
        or ledger.directed_output_validation_scratch_payload_bytes != 2 * c
        or ledger.nominal_output_validation_scratch_payload_bytes != c
        or ledger.canonical_json_stream_text_payload_bytes != _CANONICAL_JSON_STREAM_CHUNK_LIMIT
        or ledger.canonical_json_stream_encoded_payload_bytes != _CANONICAL_JSON_STREAM_CHUNK_LIMIT
        or ledger.canonical_json_stream_chunk_scratch_payload_bytes
        != _CANONICAL_JSON_STREAM_SIMULTANEOUS_PAYLOAD_BYTES
        or ledger.source_hash_stream_scratch_payload_bytes != _SOURCE_HASH_STREAM_CHUNK_BYTES
        or type(ledger.maximum_subordinate_source_read_payload_bytes) is not int
        or ledger.maximum_subordinate_source_read_payload_bytes < 1
        or ledger.maximum_subordinate_serialization_payload_bytes
        != _MAXIMUM_SUBORDINATE_SERIALIZATION_PAYLOAD_BYTES
        or ledger.subordinate_serialization_is_conservative_bound is not True
        or ledger.preflight_binding_phase_payload_bytes != preflight_phase
        or ledger.point_lift_build_validate_phase_bytes != point_phase
        or ledger.directed_action_phase_bytes != directed_phase
        or ledger.nominal_action_phase_bytes != nominal_phase
        or ledger.final_binding_revalidation_phase_bytes != final_phase
        or ledger.declared_peak_numeric_payload_bytes != numeric_peak
        or type(ledger.maximum_numeric_payload_bytes) is not int
        or type(ledger.required_peak_numeric_payload_bytes) is not int
        or ledger.required_peak_numeric_payload_bytes != numeric_peak
        or ledger.maximum_numeric_payload_bytes < ledger.required_peak_numeric_payload_bytes
        or ledger.result_consistency_serialization_payload_bytes < 0
        or ledger.result_consistency_phase_payload_bytes != result_consistency_phase
        or ledger.declared_peak_total_payload_bytes
        != max(
            preflight_phase,
            point_phase,
            directed_phase,
            nominal_phase,
            final_phase,
            result_consistency_phase,
        )
        or type(ledger.maximum_total_payload_bytes) is not int
        or type(ledger.required_peak_total_payload_bytes) is not int
        or ledger.required_peak_total_payload_bytes != ledger.declared_peak_total_payload_bytes
        or ledger.maximum_total_payload_bytes < ledger.required_peak_total_payload_bytes
        or ledger.retained_output_numeric_payload_bytes != 8 * n
        or ledger.raw_serialization_payload_bytes
        != ledger.result_consistency_serialization_payload_bytes
        or ledger.full_serialization_payload_materialized is not False
        or ledger.total_payload_is_conservative_upper_bound is not True
        or ledger.production_memory_exact is not False
        or ledger.caller_array_excluded is not True
        or ledger.preowned_kernel_excluded is not True
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RESOURCE,
            "composition simultaneous-lifetime ledger changed",
        )


def _memory_json(ledger: RateActionMemoryLedger) -> dict[str, object]:
    validate_rate_action_memory_ledger(ledger)
    return {
        field: getattr(ledger, field)
        for field in (
            "schema",
            "state_count",
            "block_size",
            "block_capacity",
            "source_nominal_payload_bytes",
            "point_lift_payload_bytes",
            "directed_output_payload_bytes",
            "nominal_output_payload_bytes",
            "point_lift_validation_scratch_payload_bytes",
            "directed_workspace_payload_bytes",
            "directed_validation_scratch_payload_bytes",
            "directed_runtime_probe_payload_bytes",
            "nominal_workspace_payload_bytes",
            "point_lift_builder_zero_scratch_payload_bytes",
            "input_default_validation_scratch_payload_bytes",
            "kernel_interval_validation_scratch_payload_bytes",
            "directed_output_validation_scratch_payload_bytes",
            "nominal_output_validation_scratch_payload_bytes",
            "canonical_json_stream_text_payload_bytes",
            "canonical_json_stream_encoded_payload_bytes",
            "canonical_json_stream_chunk_scratch_payload_bytes",
            "source_hash_stream_scratch_payload_bytes",
            "maximum_subordinate_source_read_payload_bytes",
            "maximum_subordinate_serialization_payload_bytes",
            "subordinate_serialization_is_conservative_bound",
            "preflight_binding_phase_payload_bytes",
            "point_lift_build_validate_phase_bytes",
            "directed_action_phase_bytes",
            "nominal_action_phase_bytes",
            "final_binding_revalidation_phase_bytes",
            "declared_peak_numeric_payload_bytes",
            "maximum_numeric_payload_bytes",
            "required_peak_numeric_payload_bytes",
            "result_consistency_serialization_payload_bytes",
            "result_consistency_phase_payload_bytes",
            "declared_peak_total_payload_bytes",
            "maximum_total_payload_bytes",
            "required_peak_total_payload_bytes",
            "retained_output_numeric_payload_bytes",
            "raw_serialization_payload_bytes",
            "full_serialization_payload_materialized",
            "total_payload_is_conservative_upper_bound",
            "production_memory_exact",
            "caller_array_excluded",
            "preowned_kernel_excluded",
        )
    }


def _witness_upper(witness: packed.ExactWitness) -> ExactWitnessUpper:
    if (
        abs(witness.value.numerator).bit_length() > _MAXIMUM_EXACT_WITNESS_INTEGER_BITS
        or witness.value.denominator.bit_length() > _MAXIMUM_EXACT_WITNESS_INTEGER_BITS
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RESOURCE,
            "exact witness exceeds the bounded rational token model",
        )
    upper = _fraction_upper(witness.value, label=witness.name)
    return ExactWitnessUpper(
        name=witness.name,
        numerator=witness.value.numerator,
        denominator=witness.value.denominator,
        flat_index=witness.flat_index,
        upper=upper,
        upper_hex=upper.hex(),
    )


def _witness_json(witness: ExactWitnessUpper) -> dict[str, object]:
    return {
        "denominator": witness.denominator,
        "flat_index": witness.flat_index,
        "name": witness.name,
        "numerator": witness.numerator,
        "upper_hex": witness.upper_hex,
    }


def _trace_json(trace: tuple[ScalarTraceEntry, ...]) -> list[dict[str, str]]:
    return [{"name": entry.name, "value_hex": entry.value_hex} for entry in trace]


def _derivation_json(ledger: RateActionDerivationLedger) -> dict[str, object]:
    return {
        "block_count": ledger.block_count,
        "block_size": ledger.block_size,
        "centre_radius_reduction_count": ledger.centre_radius_reduction_count,
        "centre_subtraction_count": ledger.centre_subtraction_count,
        "combined_chain_sha256": ledger.combined_chain_sha256,
        "composition_contract_sha256": ledger.composition_contract_sha256,
        "covered_state_count": ledger.covered_state_count,
        "derived_chain_sha256": ledger.derived_chain_sha256,
        "directed_action_contract_sha256": ledger.directed_action_contract_sha256,
        "directed_output_raw_sha256": ledger.directed_output_raw_sha256,
        "f0_pass": ledger.f0_pass,
        "flat_index_first": ledger.flat_index_first,
        "flat_index_stop": ledger.flat_index_stop,
        "formula_id": ledger.formula_id,
        "fraction_upper_conversion_count": ledger.fraction_upper_conversion_count,
        "fraction_upper_nextafter_count": ledger.fraction_upper_nextafter_count,
        "input_and_kernel_rechecked_after_actions": ledger.input_and_kernel_rechecked_after_actions,
        "contract_and_sources_rechecked_after_actions": ledger.contract_and_sources_rechecked_after_actions,
        "input_nominal_raw_sha256": ledger.input_nominal_raw_sha256,
        "kernel_replay_sha256": ledger.kernel_replay_sha256,
        "nominal_action_contract_sha256": ledger.nominal_action_contract_sha256,
        "nominal_inside_directed_box": ledger.nominal_inside_directed_box,
        "nominal_l1_reduction_count": ledger.nominal_l1_reduction_count,
        "nominal_output_raw_sha256": ledger.nominal_output_raw_sha256,
        "operator": ledger.operator,
        "point_lift_binding_sha256": ledger.point_lift_binding_sha256,
        "point_lift_raw_sha256": ledger.point_lift_raw_sha256,
        "point_lift_rechecked_after_actions": ledger.point_lift_rechecked_after_actions,
        "point_lift_zero_policy": ledger.point_lift_zero_policy,
        "radius_provenance_sha256": ledger.radius_provenance_sha256,
        "scalar_add_up_count": ledger.scalar_add_up_count,
        "scalar_mul_up_count": ledger.scalar_mul_up_count,
        "scalar_nextafter_count": ledger.scalar_nextafter_count,
        "scalar_sub_up_count": ledger.scalar_sub_up_count,
        "scalar_trace": _trace_json(ledger.scalar_trace),
        "schema": ledger.schema,
        "science_executed": ledger.science_executed,
        "source_chain_sha256": ledger.source_chain_sha256,
        "source_vector_raw_sha256": ledger.source_vector_raw_sha256,
        "tensor_shape": list(ledger.tensor_shape),
        "witness_binding_sha256": ledger.witness_binding_sha256,
        "witnesses": [_witness_json(witness) for witness in ledger.witnesses],
    }


def _result_consistency_payload(state: InternalRateActionState) -> dict[str, object]:
    return {
        "arrays_exposed": state.arrays_exposed,
        "authoritative": state.authoritative,
        "contract_sha256": state.contract_sha256,
        "derivation": _derivation_json(state.derivation),
        "f0_pass": state.f0_pass,
        "fresh_process": state.fresh_process,
        "l1_radius_upper_hex": state.l1_radius_upper_hex,
        "logical_shape": list(state.logical_shape),
        "memory": _memory_json(state.memory),
        "nominal_raw_sha256": state.nominal_raw_sha256,
        "nonnegative_nominal": state.nonnegative_nominal,
        "operator": state.operator,
        "radius_provenance_sha256": state.radius_provenance_sha256,
        "schema": state.schema,
        "science_executed": state.science_executed,
        "status": state.status,
        "verifier_owned_reconstruction": state.verifier_owned_reconstruction,
        "worker_private": state.worker_private,
    }


def _result_consistency_sha256(state: InternalRateActionState) -> str:
    return _canonical_json_digest(_result_consistency_payload(state))


def _compute_nominal_l1_upper(values: np.ndarray) -> float:
    result = 0.0
    for index in range(values.size):
        result = _add_up(result, abs(float(values[index])), label="nominal l1 reduction")
    return result


def _compute_centre_roundoff_upper(
    nominal: np.ndarray,
    enclosure: np.ndarray,
) -> float:
    result = 0.0
    for index in range(nominal.size):
        value = float(nominal[index])
        lower = float(enclosure[index, 0])
        upper = float(enclosure[index, 1])
        if not lower <= value <= upper:
            raise packed.PackedF0Failure(
                HOLD_RATE_ACTION_CENTRE,
                f"nominal centre result escaped directed enclosure at flat index {index}",
            )
        lower_gap = _sub_up(value, lower, label="nominal minus directed lower")
        upper_gap = _sub_up(upper, value, label="directed upper minus nominal")
        result = _add_up(
            result,
            max(lower_gap, upper_gap),
            label="centre roundoff l1 reduction",
        )
    return result


def _apply_rate_defined_transpose(
    kernel: packed.PackedTensorKernel,
    state: InternalPointBallInput,
    contract: RateActionContract,
    *,
    operator: str,
) -> InternalRateActionState:
    validate_rate_action_contract(contract)
    _preflight_subordinate_serialization_bounds(kernel)
    validate_internal_point_ball_input(state)
    packed.validate_packed_tensor_kernel(kernel)
    if (
        type(operator) is not str
        or operator not in {"P", "Q"}
        or kernel.contract.tensor_shape != contract.tensor_shape
        or kernel.contract.block_size != contract.block_size
        or state.logical_shape != contract.tensor_shape
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_SCHEMA, "kernel/state/contract disagree")
    if operator == "P" and not state.nonnegative_nominal:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_POINT_LIFT,
            "P composition requires a nonnegative nominal point",
        )

    nominal_contract, directed_contract = _reconstruct_subordinate_contracts(contract)
    contract_digest = rate_action_contract_sha256(contract)
    input_raw_before = _raw_sha256(state.nominal)
    kernel_replay = packed._kernel_replay_digest(kernel)
    point_lift, point_lift_binding = _build_point_lift(
        state,
        block_size=contract.block_size,
    )
    point_lift_raw_before = point_lift.manifest.raw_sha256

    directed_action = (
        directed.directed_p_transpose if operator == "P" else directed.directed_q_transpose
    )
    nominal_action = packed.block_p_transpose if operator == "P" else packed.block_q_transpose
    directed_result = directed_action(kernel, point_lift, directed_contract)
    nominal_vector = packed.CanonicalFloat64Vector(
        logical_shape=state.logical_shape,
        values=state.nominal,
        raw_sha256=state.nominal_raw_sha256,
        nonnegative=state.nonnegative_nominal,
        source_sha256=state.source_vector_raw_sha256,
    )
    nominal_result = nominal_action(kernel, nominal_vector, nominal_contract)

    if (
        directed_result.operator != operator
        or nominal_result.operator != operator
        or directed_result.kernel_replay_sha256 != kernel_replay
        or nominal_result.kernel_replay_sha256 != kernel_replay
        or directed_result.input_raw_sha256 != point_lift_raw_before
        or nominal_result.input_raw_sha256 != input_raw_before
        or directed_result.action_contract_sha256 != contract.directed_action_contract_sha256
        or nominal_result.action_contract_sha256 != contract.stage1_action_contract_sha256
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "subordinate action result bindings disagree",
        )

    nominal_l1_upper = _compute_nominal_l1_upper(state.nominal)
    centre_roundoff_upper = _compute_centre_roundoff_upper(
        nominal_result.nominal.values,
        directed_result.enclosure.intervals,
    )
    witnesses = {witness.name: witness for witness in kernel.ledger.witnesses}
    required_witnesses = (
        "delta_q",
        "delta_p_selected",
        "maximum_qhat_abs_row_sum",
    )
    if tuple(name for name in required_witnesses if name not in witnesses):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, "required witness is absent")
    witness_uppers = tuple(_witness_upper(witness) for witness in kernel.ledger.witnesses)
    upper_map = {witness.name: witness.upper for witness in witness_uppers}
    fraction_upper_nextafter_count = sum(
        Fraction.from_float(float(Fraction(witness.numerator, witness.denominator)))
        < Fraction(witness.numerator, witness.denominator)
        for witness in witness_uppers
    )
    input_radius = state.input_l1_radius_upper

    if operator == "P":
        coefficient = _mul_up(
            upper_map["delta_p_selected"],
            nominal_l1_upper,
            label="delta p times nominal l1",
        )
        temporary = _add_up(input_radius, coefficient, label="input radius plus coefficient")
        output_radius = _add_up(
            temporary,
            centre_roundoff_upper,
            label="P output radius",
        )
        formula_id = P_FORMULA_ID
        formula_add_count = 2
        formula_mul_count = 1
        scalar_trace = (
            ScalarTraceEntry("input_l1_radius_upper", input_radius.hex()),
            ScalarTraceEntry("input_nominal_l1_upper", nominal_l1_upper.hex()),
            ScalarTraceEntry("centre_action_roundoff_upper", centre_roundoff_upper.hex()),
            ScalarTraceEntry("delta_p_selected_times_nominal_l1", coefficient.hex()),
            ScalarTraceEntry("input_radius_plus_coefficient", temporary.hex()),
            ScalarTraceEntry("output_l1_radius_upper", output_radius.hex()),
        )
    else:
        q_norm = _add_up(
            upper_map["maximum_qhat_abs_row_sum"],
            upper_map["delta_q"],
            label="Q norm upper",
        )
        propagated = _mul_up(q_norm, input_radius, label="Q propagated input radius")
        coefficient = _mul_up(
            upper_map["delta_q"],
            nominal_l1_upper,
            label="delta Q times nominal l1",
        )
        temporary = _add_up(propagated, coefficient, label="Q propagated plus coefficient")
        output_radius = _add_up(
            temporary,
            centre_roundoff_upper,
            label="Q output radius",
        )
        formula_id = Q_FORMULA_ID
        formula_add_count = 3
        formula_mul_count = 2
        scalar_trace = (
            ScalarTraceEntry("input_l1_radius_upper", input_radius.hex()),
            ScalarTraceEntry("input_nominal_l1_upper", nominal_l1_upper.hex()),
            ScalarTraceEntry("centre_action_roundoff_upper", centre_roundoff_upper.hex()),
            ScalarTraceEntry("qhat_plus_delta_q", q_norm.hex()),
            ScalarTraceEntry("q_norm_times_input_radius", propagated.hex()),
            ScalarTraceEntry("delta_q_times_nominal_l1", coefficient.hex()),
            ScalarTraceEntry("propagated_plus_coefficient", temporary.hex()),
            ScalarTraceEntry("output_l1_radius_upper", output_radius.hex()),
        )

    # Recheck every caller-influenced and subordinate byte after both actions.
    validate_internal_point_ball_input(state)
    packed.validate_packed_tensor_kernel(kernel)
    _validate_point_lift_binding(point_lift, state, block_size=contract.block_size)
    directed.validate_directed_action_result(
        directed_result,
        kernel=kernel,
        vector=point_lift,
        contract=directed_contract,
    )
    packed.validate_block_action_result(
        nominal_result,
        validation_block_size=contract.block_size,
    )
    if (
        not hmac.compare_digest(input_raw_before, _raw_sha256(state.nominal))
        or not hmac.compare_digest(point_lift_raw_before, _raw_sha256(point_lift.intervals))
        or not hmac.compare_digest(
            point_lift_binding,
            _point_lift_binding_sha256(
                state=state,
                point_lift_raw_sha256=point_lift_raw_before,
                block_size=contract.block_size,
            ),
        )
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, "input/point-lift bytes changed")
    # Source bytes and every subordinate contract are authority-sensitive and
    # must still match after the actions, not merely at method entry.
    validate_rate_action_contract(contract)
    if not hmac.compare_digest(contract_digest, rate_action_contract_sha256(contract)):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "composition contract/source binding changed during the actions",
        )

    derivation = RateActionDerivationLedger(
        schema=RATE_ACTION_DERIVATION_SCHEMA,
        operator=operator,
        formula_id=formula_id,
        tensor_shape=contract.tensor_shape,
        block_size=contract.block_size,
        block_count=math.ceil(kernel.states / contract.block_size),
        covered_state_count=kernel.states,
        flat_index_first=0,
        flat_index_stop=kernel.states,
        nominal_l1_reduction_count=kernel.states,
        centre_radius_reduction_count=kernel.states,
        centre_subtraction_count=2 * kernel.states,
        fraction_upper_conversion_count=len(witness_uppers),
        fraction_upper_nextafter_count=fraction_upper_nextafter_count,
        scalar_add_up_count=2 * kernel.states + formula_add_count,
        scalar_mul_up_count=formula_mul_count,
        scalar_sub_up_count=2 * kernel.states,
        scalar_nextafter_count=(
            4 * kernel.states
            + formula_add_count
            + formula_mul_count
            + fraction_upper_nextafter_count
        ),
        kernel_replay_sha256=kernel_replay,
        source_chain_sha256=kernel.ledger.source_chain_sha256,
        derived_chain_sha256=kernel.ledger.derived_chain_sha256,
        combined_chain_sha256=kernel.ledger.combined_chain_sha256,
        witness_binding_sha256=kernel.ledger.witness_binding_sha256,
        composition_contract_sha256=contract_digest,
        directed_action_contract_sha256=directed_result.action_contract_sha256,
        nominal_action_contract_sha256=nominal_result.action_contract_sha256,
        input_nominal_raw_sha256=input_raw_before,
        source_vector_raw_sha256=state.source_vector_raw_sha256,
        point_lift_raw_sha256=point_lift_raw_before,
        point_lift_binding_sha256=point_lift_binding,
        directed_output_raw_sha256=directed_result.enclosure.raw_sha256,
        nominal_output_raw_sha256=nominal_result.nominal.raw_sha256,
        radius_provenance_sha256=state.radius_provenance_sha256,
        point_lift_zero_policy=POINT_LIFT_ZERO_POLICY,
        witnesses=witness_uppers,
        scalar_trace=scalar_trace,
        input_and_kernel_rechecked_after_actions=True,
        contract_and_sources_rechecked_after_actions=True,
        point_lift_rechecked_after_actions=True,
        nominal_inside_directed_box=True,
        science_executed=False,
        f0_pass=False,
    )
    memory = _memory_ledger(
        contract,
        nominal_contract=nominal_contract,
        directed_contract=directed_contract,
    )
    provisional = InternalRateActionState(
        schema=RATE_ACTION_STATE_SCHEMA,
        operator=operator,
        logical_shape=contract.tensor_shape,
        nominal=nominal_result.nominal.values,
        nominal_raw_sha256=nominal_result.nominal.raw_sha256,
        l1_radius_upper=output_radius,
        l1_radius_upper_hex=output_radius.hex(),
        radius_provenance_sha256=state.radius_provenance_sha256,
        contract_sha256=contract_digest,
        derivation=derivation,
        memory=memory,
        consistency_sha256="0" * 64,
        status=METHOD_STATUS,
        nonnegative_nominal=operator == "P",
        worker_private=True,
        arrays_exposed=True,
        authoritative=False,
        fresh_process=False,
        verifier_owned_reconstruction=False,
        science_executed=False,
        f0_pass=False,
    )
    result = replace(
        provisional,
        consistency_sha256=_result_consistency_sha256(provisional),
    )
    validate_internal_rate_action_state(result)
    return result


def _rate_defined_p_transpose(
    private_kernel: packed.PackedTensorKernel,
    private_state: InternalPointBallInput,
    contract: RateActionContract,
) -> InternalRateActionState:
    """Non-authoritative same-process method for ``P.T(c+B_1(e))``."""

    return _apply_rate_defined_transpose(
        private_kernel,
        private_state,
        contract,
        operator="P",
    )


def _rate_defined_q_transpose(
    private_kernel: packed.PackedTensorKernel,
    private_state: InternalPointBallInput,
    contract: RateActionContract,
) -> InternalRateActionState:
    """Non-authoritative same-process method for ``Q.T(c+B_1(e))``."""

    return _apply_rate_defined_transpose(
        private_kernel,
        private_state,
        contract,
        operator="Q",
    )


def validate_internal_rate_action_state(state: InternalRateActionState) -> None:
    if type(state) is not InternalRateActionState:
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_SCHEMA, "result state has wrong type")
    if (
        type(state.logical_shape) is not tuple
        or not state.logical_shape
        or any(type(entry) is not int or entry < 2 for entry in state.logical_shape)
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_SCHEMA, "result shape is invalid")
    nominal = _require_owned_readonly_vector(
        state.nominal,
        states=math.prod(state.logical_shape),
        label="output nominal",
    )
    if (
        type(state.schema) is not str
        or state.schema != RATE_ACTION_STATE_SCHEMA
        or type(state.operator) is not str
        or state.operator not in {"P", "Q"}
        or not _is_hex_digest(state.nominal_raw_sha256)
        or not hmac.compare_digest(state.nominal_raw_sha256, _raw_sha256(nominal))
        or _require_nonnegative_finite_float(
            state.l1_radius_upper,
            label="output l1 radius upper",
        )
        != state.l1_radius_upper
        or type(state.l1_radius_upper_hex) is not str
        or len(state.l1_radius_upper_hex) > 32
        or state.l1_radius_upper_hex != state.l1_radius_upper.hex()
        or not _is_hex_digest(state.radius_provenance_sha256)
        or not _is_hex_digest(state.contract_sha256)
        or type(state.derivation) is not RateActionDerivationLedger
        or type(state.memory) is not RateActionMemoryLedger
        or not _is_hex_digest(state.consistency_sha256)
        or type(state.status) is not str
        or state.status != METHOD_STATUS
        or state.nonnegative_nominal is not (state.operator == "P")
        or state.worker_private is not True
        or state.arrays_exposed is not True
        or state.authoritative is not False
        or state.fresh_process is not False
        or state.verifier_owned_reconstruction is not False
        or state.science_executed is not False
        or state.f0_pass is not False
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, "result fields changed")
    wrapper = packed.CanonicalFloat64Vector(
        logical_shape=state.logical_shape,
        values=nominal,
        raw_sha256=state.nominal_raw_sha256,
        nonnegative=state.nonnegative_nominal,
        source_sha256=state.derivation.input_nominal_raw_sha256,
    )
    packed.validate_canonical_vector(wrapper, block_size=state.memory.block_size)
    validate_rate_action_memory_ledger(state.memory)
    ledger = state.derivation
    derivation_integer_fields = (
        ledger.block_size,
        ledger.block_count,
        ledger.covered_state_count,
        ledger.flat_index_first,
        ledger.flat_index_stop,
        ledger.nominal_l1_reduction_count,
        ledger.centre_radius_reduction_count,
        ledger.centre_subtraction_count,
        ledger.fraction_upper_conversion_count,
        ledger.fraction_upper_nextafter_count,
        ledger.scalar_add_up_count,
        ledger.scalar_mul_up_count,
        ledger.scalar_sub_up_count,
        ledger.scalar_nextafter_count,
    )
    if (
        type(ledger.schema) is not str
        or type(ledger.operator) is not str
        or type(ledger.formula_id) is not str
        or type(ledger.point_lift_zero_policy) is not str
        or type(ledger.tensor_shape) is not tuple
        or any(type(entry) is not int or entry < 2 for entry in ledger.tensor_shape)
        or any(type(value) is not int or value < 0 for value in derivation_integer_fields)
        or ledger.block_size < 1
        or type(ledger.input_and_kernel_rechecked_after_actions) is not bool
        or type(ledger.contract_and_sources_rechecked_after_actions) is not bool
        or type(ledger.point_lift_rechecked_after_actions) is not bool
        or type(ledger.nominal_inside_directed_box) is not bool
        or type(ledger.science_executed) is not bool
        or type(ledger.f0_pass) is not bool
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "derivation ledger scalar types are invalid",
        )
    expected_trace_names = (
        (
            "input_l1_radius_upper",
            "input_nominal_l1_upper",
            "centre_action_roundoff_upper",
            "delta_p_selected_times_nominal_l1",
            "input_radius_plus_coefficient",
            "output_l1_radius_upper",
        )
        if state.operator == "P"
        else (
            "input_l1_radius_upper",
            "input_nominal_l1_upper",
            "centre_action_roundoff_upper",
            "qhat_plus_delta_q",
            "q_norm_times_input_radius",
            "delta_q_times_nominal_l1",
            "propagated_plus_coefficient",
            "output_l1_radius_upper",
        )
    )
    if (
        ledger.schema != RATE_ACTION_DERIVATION_SCHEMA
        or ledger.operator != state.operator
        or ledger.formula_id != (P_FORMULA_ID if state.operator == "P" else Q_FORMULA_ID)
        or ledger.tensor_shape != state.logical_shape
        or ledger.block_size != state.memory.block_size
        or ledger.block_count != math.ceil(math.prod(state.logical_shape) / ledger.block_size)
        or ledger.covered_state_count != math.prod(state.logical_shape)
        or ledger.flat_index_first != 0
        or ledger.flat_index_stop != math.prod(state.logical_shape)
        or ledger.nominal_l1_reduction_count != math.prod(state.logical_shape)
        or ledger.centre_radius_reduction_count != math.prod(state.logical_shape)
        or ledger.centre_subtraction_count != 2 * math.prod(state.logical_shape)
        or ledger.fraction_upper_conversion_count != len(packed.EXPECTED_WITNESS_NAMES)
        or type(ledger.fraction_upper_nextafter_count) is not int
        or ledger.fraction_upper_nextafter_count < 0
        or ledger.scalar_add_up_count
        != 2 * math.prod(state.logical_shape) + (2 if state.operator == "P" else 3)
        or ledger.scalar_mul_up_count != (1 if state.operator == "P" else 2)
        or ledger.scalar_sub_up_count != 2 * math.prod(state.logical_shape)
        or ledger.scalar_nextafter_count
        != (
            4 * math.prod(state.logical_shape)
            + (3 if state.operator == "P" else 5)
            + ledger.fraction_upper_nextafter_count
        )
        or not all(
            _is_hex_digest(value)
            for value in (
                ledger.kernel_replay_sha256,
                ledger.source_chain_sha256,
                ledger.derived_chain_sha256,
                ledger.combined_chain_sha256,
                ledger.witness_binding_sha256,
                ledger.composition_contract_sha256,
                ledger.directed_action_contract_sha256,
                ledger.nominal_action_contract_sha256,
                ledger.input_nominal_raw_sha256,
                ledger.source_vector_raw_sha256,
                ledger.point_lift_raw_sha256,
                ledger.point_lift_binding_sha256,
                ledger.directed_output_raw_sha256,
                ledger.nominal_output_raw_sha256,
                ledger.radius_provenance_sha256,
            )
        )
        or ledger.composition_contract_sha256 != state.contract_sha256
        or ledger.nominal_output_raw_sha256 != state.nominal_raw_sha256
        or ledger.radius_provenance_sha256 != state.radius_provenance_sha256
        or ledger.point_lift_zero_policy != POINT_LIFT_ZERO_POLICY
        or type(ledger.witnesses) is not tuple
        or any(type(witness) is not ExactWitnessUpper for witness in ledger.witnesses)
        or any(type(witness.name) is not str for witness in ledger.witnesses)
        or tuple(witness.name for witness in ledger.witnesses) != packed.EXPECTED_WITNESS_NAMES
        or type(ledger.scalar_trace) is not tuple
        or any(type(entry) is not ScalarTraceEntry for entry in ledger.scalar_trace)
        or any(
            type(entry.name) is not str or type(entry.value_hex) is not str
            for entry in ledger.scalar_trace
        )
        or tuple(entry.name for entry in ledger.scalar_trace) != expected_trace_names
        or ledger.scalar_trace[-1].value_hex != state.l1_radius_upper_hex
        or ledger.input_and_kernel_rechecked_after_actions is not True
        or ledger.contract_and_sources_rechecked_after_actions is not True
        or ledger.point_lift_rechecked_after_actions is not True
        or ledger.nominal_inside_directed_box is not True
        or ledger.science_executed is not False
        or ledger.f0_pass is not False
    ):
        raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, "derivation ledger changed")
    for witness in ledger.witnesses:
        if (
            type(witness.name) is not str
            or type(witness.numerator) is not int
            or type(witness.denominator) is not int
            or witness.denominator < 1
            or abs(witness.numerator).bit_length() > _MAXIMUM_EXACT_WITNESS_INTEGER_BITS
            or witness.denominator.bit_length() > _MAXIMUM_EXACT_WITNESS_INTEGER_BITS
            or type(witness.flat_index) is not int
            or not (-1 <= witness.flat_index < math.prod(state.logical_shape))
            or type(witness.upper) is not float
            or not math.isfinite(witness.upper)
            or witness.upper < 0.0
            or (witness.upper == 0.0 and math.copysign(1.0, witness.upper) < 0.0)
            or type(witness.upper_hex) is not str
            or len(witness.upper_hex) > 32
            or witness.upper_hex != witness.upper.hex()
            or Fraction.from_float(witness.upper) < Fraction(witness.numerator, witness.denominator)
            or witness.upper
            != _fraction_upper(
                Fraction(witness.numerator, witness.denominator),
                label=witness.name,
            )
        ):
            raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, "witness upper changed")
    expected_fraction_nextafters = sum(
        Fraction.from_float(float(Fraction(witness.numerator, witness.denominator)))
        < Fraction(witness.numerator, witness.denominator)
        for witness in ledger.witnesses
    )
    if ledger.fraction_upper_nextafter_count != expected_fraction_nextafters:
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "fraction-to-upper operation count changed",
        )
    trace: dict[str, float] = {}
    for entry in ledger.scalar_trace:
        if type(entry.value_hex) is not str:
            raise packed.PackedF0Failure(HOLD_RATE_ACTION_BINDING, "scalar trace changed")
        trace[entry.name] = _parse_nonnegative_finite_hex(
            entry.value_hex,
            label=entry.name,
        )
    witness_upper = {witness.name: witness.upper for witness in ledger.witnesses}
    if state.operator == "P":
        coefficient = _mul_up(
            witness_upper["delta_p_selected"],
            trace["input_nominal_l1_upper"],
            label="validate delta p times nominal l1",
        )
        temporary = _add_up(
            trace["input_l1_radius_upper"],
            coefficient,
            label="validate input radius plus coefficient",
        )
        output = _add_up(
            temporary,
            trace["centre_action_roundoff_upper"],
            label="validate P output radius",
        )
        expected_values = {
            "delta_p_selected_times_nominal_l1": coefficient,
            "input_radius_plus_coefficient": temporary,
            "output_l1_radius_upper": output,
        }
    else:
        q_norm = _add_up(
            witness_upper["maximum_qhat_abs_row_sum"],
            witness_upper["delta_q"],
            label="validate Q norm upper",
        )
        propagated = _mul_up(
            q_norm,
            trace["input_l1_radius_upper"],
            label="validate Q propagated radius",
        )
        coefficient = _mul_up(
            witness_upper["delta_q"],
            trace["input_nominal_l1_upper"],
            label="validate delta Q times nominal l1",
        )
        temporary = _add_up(
            propagated,
            coefficient,
            label="validate Q propagated plus coefficient",
        )
        output = _add_up(
            temporary,
            trace["centre_action_roundoff_upper"],
            label="validate Q output radius",
        )
        expected_values = {
            "qhat_plus_delta_q": q_norm,
            "q_norm_times_input_radius": propagated,
            "delta_q_times_nominal_l1": coefficient,
            "propagated_plus_coefficient": temporary,
            "output_l1_radius_upper": output,
        }
    if any(trace[name] != value for name, value in expected_values.items()):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_RADIUS,
            "saved scalar trace does not replay the frozen formula",
        )
    if not hmac.compare_digest(
        state.consistency_sha256,
        _result_consistency_sha256(state),
    ):
        raise packed.PackedF0Failure(
            HOLD_RATE_ACTION_BINDING,
            "result digest is consistency metadata only and no longer agrees",
        )


def require_fresh_process_rate_action_receipt(_: InternalRateActionState) -> None:
    """Make the unimplemented authority boundary explicit and fail closed."""

    raise packed.PackedF0Failure(
        HOLD_RATE_ACTION_AUTHORITY,
        "same-process array-bearing state cannot satisfy independent replay",
    )
