"""Science-free packed/streaming backend for the first F0 redesign stage.

This module is deliberately separate from :mod:`rate_defined_tensor_f0`.  It
does not read a selector, a prospective control, a positive budget, or an F1
result.  Its only inputs are immutable byte payloads whose roles begin with
``science_free_``.

The implementation closes a bounded first stage of Rounds 136 and 138:

* canonical ``(N, 2)`` native-binary64 interval bytes are copied into owned,
  plain, C-contiguous, aligned, read-only arrays and bound to an external
  shape/length/hash manifest;
* every public container boundary uses exact built-in/dataclass types;
* the kernel ledger is reduced to constant-size domain-separated chain roots
  without retaining per-block records or any per-state ``Fraction`` object;
* ``P.T`` and ``Q.T`` use one full output plus a bounded block/halo workspace,
  never ``numpy.roll`` or a list of full-state incoming terms; and
* the producer emits only hashes/ledgers.  Direct verification is rejected; a
  launcher-controlled spawn child reconstructs every array from immutable bytes
  and its receipt is checked against the launcher's actual ``Process.pid``.

This stage is **not** an F0 pass.  It does not implement the production
uniformization/jet/topology path or its new directed-roundoff proof.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import multiprocessing
import os
import struct
import sys
from dataclasses import dataclass
from fractions import Fraction
from typing import Final

import numpy as np


class PackedF0Failure(RuntimeError):
    """Fail-closed packed-backend outcome with a stable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


HOLD_PACKED_SCHEMA: Final = "HOLD_F0_PACKED_SCHEMA_INVALID"
HOLD_PACKED_HASH: Final = "HOLD_F0_PACKED_RAW_HASH_MISMATCH"
HOLD_PACKED_ARRAY: Final = "HOLD_F0_PACKED_ARRAY_NONCANONICAL"
HOLD_PACKED_ENDPOINT: Final = "HOLD_F0_PACKED_ENDPOINT_INVALID"
HOLD_PACKED_NESTED_TYPE: Final = "HOLD_F0_PACKED_NESTED_TYPE_INVALID"
HOLD_STREAMING_LEDGER: Final = "HOLD_F0_STREAMING_LEDGER_INVALID"
HOLD_RATE: Final = "HOLD_F0_PACKED_RATE_INVALID"
HOLD_ROW: Final = "HOLD_F0_PACKED_ROW_INVALID"
HOLD_ACTION: Final = "HOLD_F0_PACKED_BLOCK_ACTION_INVALID"
HOLD_RESOURCE: Final = "HOLD_F0_PACKED_RESOURCE_CAP_EXCEEDED"
HOLD_REPLAY: Final = "HOLD_F0_PACKED_REPLAY_MISMATCH"
HOLD_FRESH_PROCESS: Final = "HOLD_F0_PACKED_FRESH_PROCESS_REQUIRED"
HOLD_SCIENCE_BOUNDARY: Final = "HOLD_F0_PACKED_SCIENCE_BOUNDARY"

PACKED_INTERVAL_SCHEMA: Final = "rate_defined_tensor_f0_packed_interval_v1"
PACKED_KERNEL_SCHEMA: Final = "rate_defined_tensor_f0_packed_kernel_v1"
PACKED_ACTION_SCHEMA: Final = "rate_defined_tensor_f0_packed_action_v1"
PACKED_REPLAY_SCHEMA: Final = "rate_defined_tensor_f0_packed_replay_v1"
ENDPOINT_ORDER: Final = "lower_upper_c_order_native_float64"
KERNEL_CONSTRUCTION: Final = "rate_defined_tensor_f0_packed_streaming_stage1_v1"
STREAMING_BACKEND: Final = "python_fraction_scalar_scratch_no_retained_rows_v1"
ACTION_BACKEND: Final = "numpy_block_halo_gather_sequential_v1"
MAXIMUM_DIMENSIONS: Final = 3
INTERVAL_BYTES_PER_STATE: Final = 16
FLOAT64_BYTES: Final = 8
INTERVAL_VALIDATION_SCRATCH_BYTES_PER_STATE: Final = 2
STREAMING_DECLARED_WORKING_BYTES_PER_STATE: Final = 64
ACTION_WORKSPACE_BYTES_PER_STATE: Final = 65
DEFAULT_VALIDATION_BLOCK_SIZE: Final = 65_536
SOURCE_CHAIN_DOMAIN: Final = b"encounter-f0-packed-source-chain-v2\x00"
DERIVED_CHAIN_DOMAIN: Final = b"encounter-f0-packed-derived-chain-v2\x00"
COMBINED_CHAIN_DOMAIN: Final = b"encounter-f0-packed-combined-chain-v2\x00"
WITNESS_BINDING_DOMAIN: Final = b"encounter-f0-packed-witness-binding-v2\x00"
REPLAY_REQUEST_DOMAIN: Final = b"encounter-f0-packed-replay-request-v2\x00"
REPLAY_CAPABILITY_DOMAIN: Final = b"encounter-f0-packed-replay-capability-v2\x00"
SPAWN_REPLAY_TIMEOUT_SECONDS: Final = 30.0
EXPECTED_WITNESS_NAMES: Final = (
    "maximum_target_exit_upper",
    "maximum_center_exit",
    "delta_q",
    "delta_p_direct",
    "p_coefficient_rounding",
    "delta_p_via_q",
    "delta_p_selected",
    "maximum_center_row_sum",
    "maximum_qhat_abs_row_sum",
    "maximum_killing_upper",
    "maximum_killing_uncertainty",
)


def _is_hex_digest(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _sha256(payload: bytes | memoryview) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return _sha256(encoded)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _require_exact_shape(value: object, *, label: str) -> tuple[int, ...]:
    if type(value) is not tuple or not value:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, f"{label} must be a nonempty tuple")
    if any(type(entry) is not int or entry < 1 for entry in value):
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, f"{label} entries must be positive ints")
    return value


def _require_science_free_role(role: object) -> str:
    if type(role) is not str or not role.startswith("science_free_"):
        raise PackedF0Failure(
            HOLD_SCIENCE_BOUNDARY,
            "packed roles must be exact strings beginning science_free_",
        )
    return role


@dataclass(frozen=True, slots=True)
class PackedIntervalManifest:
    schema: str
    role: str
    logical_shape: tuple[int, ...]
    array_shape: tuple[int, int]
    state_count: int
    raw_byte_length: int
    raw_sha256: str
    endpoint_order: str
    nonnegative: bool
    block_size: int
    maximum_working_bytes: int


@dataclass(frozen=True, slots=True)
class PackedIntervalPayload:
    manifest: PackedIntervalManifest
    raw_bytes: bytes


@dataclass(frozen=True, slots=True)
class CanonicalPackedIntervals:
    manifest: PackedIntervalManifest
    intervals: np.ndarray


def _manifest_json(manifest: PackedIntervalManifest) -> dict[str, object]:
    validate_packed_interval_manifest(manifest)
    return {
        "array_shape": list(manifest.array_shape),
        "block_size": manifest.block_size,
        "endpoint_order": manifest.endpoint_order,
        "logical_shape": list(manifest.logical_shape),
        "maximum_working_bytes": manifest.maximum_working_bytes,
        "nonnegative": manifest.nonnegative,
        "raw_byte_length": manifest.raw_byte_length,
        "raw_sha256": manifest.raw_sha256,
        "role": manifest.role,
        "schema": manifest.schema,
        "state_count": manifest.state_count,
    }


def validate_packed_interval_manifest(manifest: PackedIntervalManifest) -> None:
    """Validate an external manifest without invoking NumPy."""

    if type(manifest) is not PackedIntervalManifest:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "manifest has the wrong exact type")
    shape = _require_exact_shape(manifest.logical_shape, label="logical shape")
    states = math.prod(shape)
    if (
        type(manifest.schema) is not str
        or manifest.schema != PACKED_INTERVAL_SCHEMA
        or _require_science_free_role(manifest.role) != manifest.role
        or type(manifest.array_shape) is not tuple
        or len(manifest.array_shape) != 2
        or any(type(value) is not int for value in manifest.array_shape)
        or manifest.array_shape != (states, 2)
        or type(manifest.state_count) is not int
        or manifest.state_count != states
        or type(manifest.raw_byte_length) is not int
        or manifest.raw_byte_length != states * INTERVAL_BYTES_PER_STATE
        or not _is_hex_digest(manifest.raw_sha256)
        or type(manifest.endpoint_order) is not str
        or manifest.endpoint_order != ENDPOINT_ORDER
        or type(manifest.nonnegative) is not bool
        or type(manifest.block_size) is not int
        or manifest.block_size < 1
        or type(manifest.maximum_working_bytes) is not int
        or manifest.maximum_working_bytes
        < INTERVAL_VALIDATION_SCRATCH_BYTES_PER_STATE * min(states, manifest.block_size)
    ):
        raise PackedF0Failure(HOLD_PACKED_SCHEMA, "packed interval manifest is inconsistent")


def validate_packed_interval_payload(payload: PackedIntervalPayload) -> None:
    """Validate immutable source bytes before creating any numerical object."""

    if type(payload) is not PackedIntervalPayload:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "payload has the wrong exact type")
    validate_packed_interval_manifest(payload.manifest)
    if type(payload.raw_bytes) is not bytes:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "raw payload must have exact bytes type")
    if len(payload.raw_bytes) != payload.manifest.raw_byte_length:
        raise PackedF0Failure(HOLD_PACKED_SCHEMA, "raw payload byte length disagrees with manifest")
    if not hmac.compare_digest(_sha256(payload.raw_bytes), payload.manifest.raw_sha256):
        raise PackedF0Failure(HOLD_PACKED_HASH, "raw payload hash disagrees with manifest")


def create_packed_interval_payload(
    endpoint_pairs: tuple[tuple[float, float], ...],
    *,
    role: str,
    logical_shape: tuple[int, ...],
    nonnegative: bool,
    block_size: int,
    maximum_working_bytes: int,
) -> PackedIntervalPayload:
    """Create canonical immutable bytes from strict built-in endpoint tuples.

    This is a trusted producer helper.  The verifier consumes only the returned
    immutable bytes and manifest; it never accepts the producer's array.
    """

    shape = _require_exact_shape(logical_shape, label="logical shape")
    _require_science_free_role(role)
    if type(endpoint_pairs) is not tuple or len(endpoint_pairs) != math.prod(shape):
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "endpoint tuple length is invalid")
    if type(nonnegative) is not bool:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "nonnegative flag must be an exact bool")
    raw = bytearray(len(endpoint_pairs) * INTERVAL_BYTES_PER_STATE)
    for index, pair in enumerate(endpoint_pairs):
        if (
            type(pair) is not tuple
            or len(pair) != 2
            or type(pair[0]) is not float
            or type(pair[1]) is not float
        ):
            raise PackedF0Failure(
                HOLD_PACKED_NESTED_TYPE,
                "each endpoint pair must contain two exact built-in floats",
            )
        lower, upper = pair
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or lower > upper
            or (lower == 0.0 and math.copysign(1.0, lower) < 0.0)
            or (upper == 0.0 and math.copysign(1.0, upper) < 0.0)
            or (nonnegative and lower < 0.0)
        ):
            raise PackedF0Failure(HOLD_PACKED_ENDPOINT, "endpoint pair is not canonical")
        struct.pack_into("=dd", raw, index * INTERVAL_BYTES_PER_STATE, lower, upper)
    raw_bytes = bytes(raw)
    manifest = PackedIntervalManifest(
        schema=PACKED_INTERVAL_SCHEMA,
        role=role,
        logical_shape=shape,
        array_shape=(len(endpoint_pairs), 2),
        state_count=len(endpoint_pairs),
        raw_byte_length=len(raw_bytes),
        raw_sha256=_sha256(raw_bytes),
        endpoint_order=ENDPOINT_ORDER,
        nonnegative=nonnegative,
        block_size=block_size,
        maximum_working_bytes=maximum_working_bytes,
    )
    payload = PackedIntervalPayload(manifest=manifest, raw_bytes=raw_bytes)
    validate_packed_interval_payload(payload)
    return payload


def _require_plain_native_owned_readonly_float64(
    array: object,
    *,
    expected_shape: tuple[int, ...],
    label: str,
) -> np.ndarray:
    """Check every non-dispatched structural property before NumPy arithmetic."""

    if type(array) is not np.ndarray:
        raise PackedF0Failure(HOLD_PACKED_ARRAY, f"{label} must have exact numpy.ndarray type")
    if (
        array.dtype != np.dtype(np.float64)
        or not array.dtype.isnative
        or array.shape != expected_shape
        or not array.flags.c_contiguous
        or not array.flags.aligned
        or not array.flags.owndata
        or array.base is not None
        or array.flags.writeable
    ):
        raise PackedF0Failure(HOLD_PACKED_ARRAY, f"{label} is not canonical owned float64")
    return array


def _array_raw_sha256(array: np.ndarray) -> str:
    return _sha256(memoryview(array).cast("B"))


def validate_canonical_packed_intervals(source: CanonicalPackedIntervals) -> None:
    """Recheck exact type, layout, endpoint semantics, and raw bytes."""

    if type(source) is not CanonicalPackedIntervals:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "canonical source has wrong exact type")
    validate_packed_interval_manifest(source.manifest)
    intervals = _require_plain_native_owned_readonly_float64(
        source.intervals,
        expected_shape=source.manifest.array_shape,
        label="packed interval array",
    )
    before = _array_raw_sha256(intervals)
    if not hmac.compare_digest(before, source.manifest.raw_sha256):
        raise PackedF0Failure(HOLD_PACKED_HASH, "owned interval bytes disagree with manifest")
    validation_size = min(source.manifest.state_count, source.manifest.block_size)
    # Keep both Boolean work rows contiguous.  NumPy 2.5.1 on arm64 can leave
    # stale entries when a vectorized unary ufunc writes to ``scratch[:, 1]``
    # (byte stride two).  The transposed scratch layout preserves the exact
    # 2 B/state payload ledger while removing every strided ufunc output.
    validation_scratch = np.empty((2, validation_size), dtype=np.bool_)
    for start in range(0, source.manifest.state_count, source.manifest.block_size):
        stop = min(source.manifest.state_count, start + source.manifest.block_size)
        count = stop - start
        block = intervals[start:stop]
        first = validation_scratch[0, :count]
        second = validation_scratch[1, :count]
        invalid = False
        for endpoint in range(2):
            np.isfinite(block[:, endpoint], out=first)
            invalid = invalid or not bool(np.all(first))
        np.greater(block[:, 0], block[:, 1], out=first)
        invalid = invalid or bool(np.any(first))
        for endpoint in range(2):
            np.equal(block[:, endpoint], 0.0, out=first)
            np.signbit(block[:, endpoint], out=second)
            np.logical_and(first, second, out=first)
            invalid = invalid or bool(np.any(first))
        if source.manifest.nonnegative:
            np.less(block[:, 0], 0.0, out=first)
            invalid = invalid or bool(np.any(first))
        if invalid:
            raise PackedF0Failure(HOLD_PACKED_ENDPOINT, "owned endpoint block is invalid")
    after = _array_raw_sha256(intervals)
    if not hmac.compare_digest(before, after):
        raise PackedF0Failure(HOLD_PACKED_HASH, "owned interval bytes changed during validation")


def load_canonical_packed_intervals(payload: PackedIntervalPayload) -> CanonicalPackedIntervals:
    """Copy immutable canonical bytes into a private owned read-only array."""

    validate_packed_interval_payload(payload)
    array = np.empty(payload.manifest.array_shape, dtype=np.float64, order="C")
    memoryview(array).cast("B")[:] = payload.raw_bytes
    array.setflags(write=False)
    source = CanonicalPackedIntervals(manifest=payload.manifest, intervals=array)
    validate_canonical_packed_intervals(source)
    return source


@dataclass(frozen=True, slots=True)
class PackedAxisPayload:
    name: str
    size: int
    periodic: bool
    forward: PackedIntervalPayload
    backward: PackedIntervalPayload


@dataclass(frozen=True, slots=True)
class CanonicalPackedAxis:
    name: str
    size: int
    periodic: bool
    forward: CanonicalPackedIntervals
    backward: CanonicalPackedIntervals


@dataclass(frozen=True, slots=True)
class PackedKernelInputs:
    axes: tuple[PackedAxisPayload, ...]
    killing: PackedIntervalPayload


@dataclass(frozen=True, slots=True)
class KernelBuildContract:
    tensor_shape: tuple[int, ...]
    block_size: int
    maximum_working_bytes: int
    uniformization_rate: Fraction | None
    single_threaded: bool = True
    science_free: bool = True


def validate_packed_axis_payload(axis: PackedAxisPayload) -> None:
    if type(axis) is not PackedAxisPayload:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "axis payload has wrong exact type")
    if (
        type(axis.name) is not str
        or not axis.name
        or type(axis.size) is not int
        or axis.size < 2
        or type(axis.periodic) is not bool
        or type(axis.forward) is not PackedIntervalPayload
        or type(axis.backward) is not PackedIntervalPayload
    ):
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "axis payload fields have wrong types")
    validate_packed_interval_payload(axis.forward)
    validate_packed_interval_payload(axis.backward)
    if (
        axis.forward.manifest.role != f"science_free_axis_{axis.name}_forward"
        or axis.backward.manifest.role != f"science_free_axis_{axis.name}_backward"
        or axis.forward.manifest.logical_shape != (axis.size,)
        or axis.backward.manifest.logical_shape != (axis.size,)
        or not axis.forward.manifest.nonnegative
        or not axis.backward.manifest.nonnegative
    ):
        raise PackedF0Failure(HOLD_PACKED_SCHEMA, "axis source roles/shapes are inconsistent")


def _load_canonical_axis(axis: PackedAxisPayload) -> CanonicalPackedAxis:
    validate_packed_axis_payload(axis)
    canonical = CanonicalPackedAxis(
        name=axis.name,
        size=axis.size,
        periodic=axis.periodic,
        forward=load_canonical_packed_intervals(axis.forward),
        backward=load_canonical_packed_intervals(axis.backward),
    )
    validate_canonical_axis(canonical)
    return canonical


def validate_canonical_axis(axis: CanonicalPackedAxis) -> None:
    if type(axis) is not CanonicalPackedAxis:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "canonical axis has wrong exact type")
    if (
        type(axis.name) is not str
        or not axis.name
        or type(axis.size) is not int
        or axis.size < 2
        or type(axis.periodic) is not bool
        or type(axis.forward) is not CanonicalPackedIntervals
        or type(axis.backward) is not CanonicalPackedIntervals
    ):
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "canonical axis fields have wrong types")
    validate_canonical_packed_intervals(axis.forward)
    validate_canonical_packed_intervals(axis.backward)
    if (
        axis.forward.manifest.role != f"science_free_axis_{axis.name}_forward"
        or axis.backward.manifest.role != f"science_free_axis_{axis.name}_backward"
        or axis.forward.manifest.logical_shape != (axis.size,)
        or axis.backward.manifest.logical_shape != (axis.size,)
        or not axis.forward.manifest.nonnegative
        or not axis.backward.manifest.nonnegative
    ):
        raise PackedF0Failure(HOLD_PACKED_SCHEMA, "canonical axis shape is inconsistent")
    if not axis.periodic and (
        float(axis.forward.intervals[-1, 1]) != 0.0 or float(axis.backward.intervals[0, 1]) != 0.0
    ):
        raise PackedF0Failure(HOLD_ROW, "reflecting axis crosses a boundary")


def validate_kernel_build_contract(contract: KernelBuildContract) -> None:
    if type(contract) is not KernelBuildContract:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "kernel contract has wrong exact type")
    shape = _require_exact_shape(contract.tensor_shape, label="kernel tensor shape")
    states = math.prod(shape)
    if (
        len(shape) > MAXIMUM_DIMENSIONS
        or type(contract.block_size) is not int
        or contract.block_size < 1
        or type(contract.maximum_working_bytes) is not int
        or contract.maximum_working_bytes
        < STREAMING_DECLARED_WORKING_BYTES_PER_STATE * min(states, contract.block_size)
        or (
            contract.uniformization_rate is not None
            and type(contract.uniformization_rate) is not Fraction
        )
        or type(contract.single_threaded) is not bool
        or contract.single_threaded is not True
        or type(contract.science_free) is not bool
        or contract.science_free is not True
    ):
        raise PackedF0Failure(HOLD_PACKED_SCHEMA, "kernel build contract is invalid")


def validate_kernel_inputs(inputs: PackedKernelInputs, contract: KernelBuildContract) -> None:
    if type(inputs) is not PackedKernelInputs:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "kernel inputs have wrong exact type")
    validate_kernel_build_contract(contract)
    if (
        type(inputs.axes) is not tuple
        or len(inputs.axes) != len(contract.tensor_shape)
        or not inputs.axes
        or any(type(axis) is not PackedAxisPayload for axis in inputs.axes)
        or type(inputs.killing) is not PackedIntervalPayload
    ):
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "kernel input nesting is invalid")
    for axis in inputs.axes:
        validate_packed_axis_payload(axis)
    validate_packed_interval_payload(inputs.killing)
    if (
        tuple(axis.size for axis in inputs.axes) != contract.tensor_shape
        or inputs.killing.manifest.role != "science_free_killing"
        or inputs.killing.manifest.logical_shape != contract.tensor_shape
        or not inputs.killing.manifest.nonnegative
        or any(axis.forward.manifest.block_size != contract.block_size for axis in inputs.axes)
        or any(axis.backward.manifest.block_size != contract.block_size for axis in inputs.axes)
        or inputs.killing.manifest.block_size != contract.block_size
    ):
        raise PackedF0Failure(HOLD_PACKED_SCHEMA, "kernel source bundle disagrees with contract")


def _contract_json(contract: KernelBuildContract) -> dict[str, object]:
    validate_kernel_build_contract(contract)
    return {
        "block_size": contract.block_size,
        "maximum_working_bytes": contract.maximum_working_bytes,
        "science_free": contract.science_free,
        "single_threaded": contract.single_threaded,
        "tensor_shape": list(contract.tensor_shape),
        "uniformization_rate": (
            None
            if contract.uniformization_rate is None
            else _fraction_text(contract.uniformization_rate)
        ),
    }


def _kernel_inputs_digest(inputs: PackedKernelInputs, contract: KernelBuildContract) -> str:
    validate_kernel_inputs(inputs, contract)
    return _canonical_json_digest(
        {
            "axes": [
                {
                    "backward": _manifest_json(axis.backward.manifest),
                    "forward": _manifest_json(axis.forward.manifest),
                    "name": axis.name,
                    "periodic": axis.periodic,
                    "size": axis.size,
                }
                for axis in inputs.axes
            ],
            "contract": _contract_json(contract),
            "killing": _manifest_json(inputs.killing.manifest),
        }
    )


def _fraction_lower(value: Fraction) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise PackedF0Failure(HOLD_PACKED_ENDPOINT, "exact value does not fit binary64")
    if Fraction.from_float(candidate) > value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(-math.inf)))
    return candidate


def _fraction_upper(value: Fraction) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise PackedF0Failure(HOLD_PACKED_ENDPOINT, "exact value does not fit binary64")
    if Fraction.from_float(candidate) < value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    return candidate


def _interval_centre(lower: float, upper: float) -> float:
    lower_exact = Fraction.from_float(lower)
    upper_exact = Fraction.from_float(upper)
    centre = float((lower_exact + upper_exact) / 2)
    if centre < lower:
        return lower
    if centre > upper:
        return upper
    return centre


def _interval_radius(lower: float, upper: float, centre: float) -> Fraction:
    point = Fraction.from_float(centre)
    return max(point - Fraction.from_float(lower), Fraction.from_float(upper) - point)


def _readonly(array: np.ndarray) -> np.ndarray:
    if type(array) is not np.ndarray or not array.flags.owndata or array.base is not None:
        raise PackedF0Failure(HOLD_PACKED_ARRAY, "internal array lost ownership")
    array.setflags(write=False)
    return array


@dataclass(frozen=True, slots=True)
class ExactWitness:
    name: str
    value: Fraction
    flat_index: int


@dataclass(frozen=True, slots=True)
class StreamingExactLedger:
    schema: str
    state_count: int
    block_size: int
    maximum_working_bytes: int
    construction_exact_pass_count: int
    witness_rebind_pass_count: int
    backend: str
    retained_per_state_fraction_objects: bool
    retained_fraction_witness_count: int
    block_count: int
    covered_state_count: int
    source_chain_sha256: str
    derived_chain_sha256: str
    combined_chain_sha256: str
    witness_binding_sha256: str
    witnesses: tuple[ExactWitness, ...]


@dataclass(frozen=True, slots=True)
class ArrayDigest:
    name: str
    shape: tuple[int, ...]
    raw_byte_length: int
    raw_sha256: str


@dataclass(frozen=True, slots=True)
class PackedTensorKernel:
    schema: str
    construction: str
    contract: KernelBuildContract
    axes: tuple[CanonicalPackedAxis, ...]
    killing: CanonicalPackedIntervals
    forward_center: tuple[np.ndarray, ...]
    backward_center: tuple[np.ndarray, ...]
    p_forward_center: tuple[np.ndarray, ...]
    p_backward_center: tuple[np.ndarray, ...]
    killing_center: np.ndarray
    diagonal_center: np.ndarray
    p_self_center: np.ndarray
    rate: float
    rate_fraction: Fraction
    ledger: StreamingExactLedger
    array_digests: tuple[ArrayDigest, ...]
    f0_pass: bool
    science_executed: bool
    action_roundoff_proof_complete: bool
    batched_scalar_topology_complete: bool

    @property
    def states(self) -> int:
        return math.prod(self.contract.tensor_shape)


def _validate_exact_witness(witness: ExactWitness, *, states: int) -> None:
    if (
        type(witness) is not ExactWitness
        or type(witness.name) is not str
        or type(witness.value) is not Fraction
        or witness.value < 0
        or type(witness.flat_index) is not int
        or not (-1 <= witness.flat_index < states)
    ):
        raise PackedF0Failure(HOLD_STREAMING_LEDGER, "exact witness schema is invalid")


def validate_streaming_exact_ledger(ledger: StreamingExactLedger) -> None:
    if type(ledger) is not StreamingExactLedger:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "streaming ledger has wrong exact type")
    if (
        type(ledger.schema) is not str
        or ledger.schema != PACKED_KERNEL_SCHEMA
        or type(ledger.state_count) is not int
        or ledger.state_count < 1
        or type(ledger.block_size) is not int
        or ledger.block_size < 1
        or type(ledger.maximum_working_bytes) is not int
        or ledger.maximum_working_bytes < 1
        or type(ledger.construction_exact_pass_count) is not int
        or ledger.construction_exact_pass_count != 2
        or type(ledger.witness_rebind_pass_count) is not int
        or ledger.witness_rebind_pass_count != 1
        or type(ledger.backend) is not str
        or ledger.backend != STREAMING_BACKEND
        or type(ledger.retained_per_state_fraction_objects) is not bool
        or ledger.retained_per_state_fraction_objects is not False
        or type(ledger.retained_fraction_witness_count) is not int
        or type(ledger.block_count) is not int
        or ledger.block_count != math.ceil(ledger.state_count / ledger.block_size)
        or type(ledger.covered_state_count) is not int
        or ledger.covered_state_count != ledger.state_count
        or not _is_hex_digest(ledger.source_chain_sha256)
        or not _is_hex_digest(ledger.derived_chain_sha256)
        or not _is_hex_digest(ledger.combined_chain_sha256)
        or not _is_hex_digest(ledger.witness_binding_sha256)
        or type(ledger.witnesses) is not tuple
        or ledger.retained_fraction_witness_count != len(ledger.witnesses)
        or tuple(witness.name for witness in ledger.witnesses) != EXPECTED_WITNESS_NAMES
    ):
        raise PackedF0Failure(HOLD_STREAMING_LEDGER, "streaming ledger header is invalid")
    for witness in ledger.witnesses:
        _validate_exact_witness(witness, states=ledger.state_count)


def _ledger_json(ledger: StreamingExactLedger) -> dict[str, object]:
    validate_streaming_exact_ledger(ledger)
    return {
        "backend": ledger.backend,
        "block_count": ledger.block_count,
        "block_size": ledger.block_size,
        "combined_chain_sha256": ledger.combined_chain_sha256,
        "construction_exact_pass_count": ledger.construction_exact_pass_count,
        "covered_state_count": ledger.covered_state_count,
        "derived_chain_sha256": ledger.derived_chain_sha256,
        "maximum_working_bytes": ledger.maximum_working_bytes,
        "retained_fraction_witness_count": ledger.retained_fraction_witness_count,
        "retained_per_state_fraction_objects": ledger.retained_per_state_fraction_objects,
        "schema": ledger.schema,
        "source_chain_sha256": ledger.source_chain_sha256,
        "state_count": ledger.state_count,
        "witness_binding_sha256": ledger.witness_binding_sha256,
        "witness_rebind_pass_count": ledger.witness_rebind_pass_count,
        "witnesses": [
            {
                "flat_index": witness.flat_index,
                "name": witness.name,
                "value": _fraction_text(witness.value),
            }
            for witness in ledger.witnesses
        ],
    }


def _array_digest(name: str, array: np.ndarray) -> ArrayDigest:
    if type(name) is not str or not name:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "array digest name is invalid")
    return ArrayDigest(
        name=name,
        shape=tuple(int(value) for value in array.shape),
        raw_byte_length=int(array.nbytes),
        raw_sha256=_array_raw_sha256(array),
    )


def _validate_array_digest(digest: ArrayDigest) -> None:
    if (
        type(digest) is not ArrayDigest
        or type(digest.name) is not str
        or not digest.name
        or type(digest.shape) is not tuple
        or not digest.shape
        or any(type(value) is not int or value < 1 for value in digest.shape)
        or type(digest.raw_byte_length) is not int
        or digest.raw_byte_length != math.prod(digest.shape) * FLOAT64_BYTES
        or not _is_hex_digest(digest.raw_sha256)
    ):
        raise PackedF0Failure(HOLD_STREAMING_LEDGER, "array digest is invalid")


def _update_maximum(
    current_value: Fraction,
    current_index: int,
    candidate: Fraction,
    candidate_index: int,
) -> tuple[Fraction, int]:
    if candidate > current_value:
        return candidate, candidate_index
    return current_value, current_index


def _axis_strides(shape: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(math.prod(shape[index + 1 :]) for index in range(len(shape)))


def _axis_index(flat: int, *, size: int, stride: int) -> int:
    return (flat // stride) % size


def _canonical_kernel_sources_digest(
    axes: tuple[CanonicalPackedAxis, ...],
    killing: CanonicalPackedIntervals,
    contract: KernelBuildContract,
) -> str:
    return _canonical_json_digest(
        {
            "axes": [
                {
                    "backward": _manifest_json(axis.backward.manifest),
                    "forward": _manifest_json(axis.forward.manifest),
                    "name": axis.name,
                    "periodic": axis.periodic,
                    "size": axis.size,
                }
                for axis in axes
            ],
            "contract": _contract_json(contract),
            "killing": _manifest_json(killing.manifest),
        }
    )


def _update_block_chains(
    source_chain: object,
    derived_chain: object,
    killing: CanonicalPackedIntervals,
    start: int,
    stop: int,
    killing_center: np.ndarray,
    diagonal_center: np.ndarray,
    p_self_center: np.ndarray,
) -> None:
    header = struct.pack(">QQ", start, stop - start)
    source_chain.update(header)
    killing_raw = memoryview(killing.intervals).cast("B")
    source_chain.update(
        killing_raw[start * INTERVAL_BYTES_PER_STATE : stop * INTERVAL_BYTES_PER_STATE]
    )
    derived_chain.update(header)
    for array in (killing_center, diagonal_center, p_self_center):
        raw = memoryview(array).cast("B")
        derived_chain.update(raw[start * FLOAT64_BYTES : stop * FLOAT64_BYTES])


def _build_axis_centres(
    axes: tuple[CanonicalPackedAxis, ...],
    rate_fraction: Fraction,
) -> tuple[
    tuple[np.ndarray, ...],
    tuple[np.ndarray, ...],
    tuple[np.ndarray, ...],
    tuple[np.ndarray, ...],
]:
    forward_centres: list[np.ndarray] = []
    backward_centres: list[np.ndarray] = []
    p_forward_centres: list[np.ndarray] = []
    p_backward_centres: list[np.ndarray] = []
    for axis in axes:
        forward = np.empty(axis.size, dtype=np.float64)
        backward = np.empty(axis.size, dtype=np.float64)
        p_forward = np.empty(axis.size, dtype=np.float64)
        p_backward = np.empty(axis.size, dtype=np.float64)
        for index in range(axis.size):
            forward[index] = _interval_centre(
                float(axis.forward.intervals[index, 0]),
                float(axis.forward.intervals[index, 1]),
            )
            backward[index] = _interval_centre(
                float(axis.backward.intervals[index, 0]),
                float(axis.backward.intervals[index, 1]),
            )
            p_forward[index] = _fraction_lower(
                Fraction.from_float(float(forward[index])) / rate_fraction
            )
            p_backward[index] = _fraction_lower(
                Fraction.from_float(float(backward[index])) / rate_fraction
            )
        forward_centres.append(_readonly(forward))
        backward_centres.append(_readonly(backward))
        p_forward_centres.append(_readonly(p_forward))
        p_backward_centres.append(_readonly(p_backward))
    return (
        tuple(forward_centres),
        tuple(backward_centres),
        tuple(p_forward_centres),
        tuple(p_backward_centres),
    )


def _witness_binding_digest(
    *,
    source_sha256: str,
    array_digests: tuple[ArrayDigest, ...],
    rate_fraction: Fraction,
    source_chain_sha256: str,
    derived_chain_sha256: str,
    witnesses: tuple[ExactWitness, ...],
) -> str:
    payload = {
        "array_digests": [
            {
                "name": digest.name,
                "raw_byte_length": digest.raw_byte_length,
                "raw_sha256": digest.raw_sha256,
                "shape": list(digest.shape),
            }
            for digest in array_digests
        ],
        "derived_chain_sha256": derived_chain_sha256,
        "rate_fraction": _fraction_text(rate_fraction),
        "source_chain_sha256": source_chain_sha256,
        "source_sha256": source_sha256,
        "witnesses": [
            {
                "flat_index": witness.flat_index,
                "name": witness.name,
                "value": _fraction_text(witness.value),
            }
            for witness in witnesses
        ],
    }
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return _sha256(WITNESS_BINDING_DOMAIN + encoded)


def _recompute_exact_witnesses_from_owned_kernel(
    kernel: PackedTensorKernel,
) -> tuple[ExactWitness, ...]:
    """Recompute every saved exact witness without consulting the ledger."""

    states = kernel.states
    strides = _axis_strides(kernel.contract.tensor_shape)
    maximum_exit = Fraction(0)
    maximum_exit_index = 0
    maximum_center_exit = Fraction(0)
    maximum_center_exit_index = 0
    maxima: dict[str, tuple[Fraction, int]] = {
        "delta_q": (Fraction(0), 0),
        "delta_p_direct": (Fraction(0), 0),
        "p_coefficient_rounding": (Fraction(0), 0),
        "maximum_center_row_sum": (Fraction(0), 0),
        "maximum_qhat_abs_row_sum": (Fraction(0), 0),
        "maximum_killing_upper": (Fraction(0), 0),
        "maximum_killing_uncertainty": (Fraction(0), 0),
    }
    rate_fraction = kernel.rate_fraction

    for start in range(0, states, kernel.contract.block_size):
        stop = min(states, start + kernel.contract.block_size)
        for flat in range(start, stop):
            kill_lower_float = float(kernel.killing.intervals[flat, 0])
            kill_upper_float = float(kernel.killing.intervals[flat, 1])
            kill_lower = Fraction.from_float(kill_lower_float)
            kill_upper = Fraction.from_float(kill_upper_float)
            kill_centre_float = _interval_centre(kill_lower_float, kill_upper_float)
            if float(kernel.killing_center[flat]) != kill_centre_float:
                raise PackedF0Failure(
                    HOLD_STREAMING_LEDGER,
                    "owned killing centre is not bound to its interval bytes",
                )
            kill_centre = Fraction.from_float(kill_centre_float)
            rate_lower = Fraction(0)
            rate_upper = Fraction(0)
            rate_center = Fraction(0)
            off_diagonal_error = Fraction(0)
            p_direct_error = Fraction(0)
            p_rounding = Fraction(0)
            p_row_sum = Fraction(0)
            for dimension, (axis, stride) in enumerate(zip(kernel.axes, strides, strict=True)):
                coordinate = _axis_index(flat, size=axis.size, stride=stride)
                for source, q_values, p_values in (
                    (
                        axis.forward,
                        kernel.forward_center[dimension],
                        kernel.p_forward_center[dimension],
                    ),
                    (
                        axis.backward,
                        kernel.backward_center[dimension],
                        kernel.p_backward_center[dimension],
                    ),
                ):
                    lower_float = float(source.intervals[coordinate, 0])
                    upper_float = float(source.intervals[coordinate, 1])
                    lower = Fraction.from_float(lower_float)
                    upper = Fraction.from_float(upper_float)
                    expected_q_float = _interval_centre(lower_float, upper_float)
                    q_value_float = float(q_values[coordinate])
                    if q_value_float != expected_q_float:
                        raise PackedF0Failure(
                            HOLD_STREAMING_LEDGER,
                            "owned rate centre is not bound to its interval bytes",
                        )
                    q_value = Fraction.from_float(q_value_float)
                    expected_p_float = _fraction_lower(q_value / rate_fraction)
                    p_value_float = float(p_values[coordinate])
                    if p_value_float != expected_p_float:
                        raise PackedF0Failure(
                            HOLD_STREAMING_LEDGER,
                            "owned P coefficient is not bound to its rate centre",
                        )
                    p_value = Fraction.from_float(p_value_float)
                    rate_lower += lower
                    rate_upper += upper
                    rate_center += q_value
                    off_diagonal_error += _interval_radius(
                        lower_float,
                        upper_float,
                        q_value_float,
                    )
                    p_direct_error += max(
                        p_value - lower / rate_fraction,
                        upper / rate_fraction - p_value,
                    )
                    p_rounding += abs(q_value / rate_fraction - p_value)
                    p_row_sum += p_value

            exit_upper = rate_upper + kill_upper
            center_exit = rate_center + kill_centre
            maximum_exit, maximum_exit_index = _update_maximum(
                maximum_exit,
                maximum_exit_index,
                exit_upper,
                flat,
            )
            maximum_center_exit, maximum_center_exit_index = _update_maximum(
                maximum_center_exit,
                maximum_center_exit_index,
                center_exit,
                flat,
            )
            target_diagonal_lower = -exit_upper
            target_diagonal_upper = -(rate_lower + kill_lower)
            expected_diagonal_float = _fraction_lower(-center_exit)
            diagonal_float = float(kernel.diagonal_center[flat])
            if diagonal_float != expected_diagonal_float:
                raise PackedF0Failure(
                    HOLD_STREAMING_LEDGER,
                    "owned diagonal is not bound to its source bytes",
                )
            diagonal = Fraction.from_float(diagonal_float)
            diagonal_error = max(
                diagonal - target_diagonal_lower,
                target_diagonal_upper - diagonal,
            )
            q_error = off_diagonal_error + diagonal_error
            expected_self_float = _fraction_lower(Fraction(1) + diagonal / rate_fraction)
            self_float = float(kernel.p_self_center[flat])
            if self_float != expected_self_float:
                raise PackedF0Failure(
                    HOLD_STREAMING_LEDGER,
                    "owned self coefficient is not bound to its diagonal",
                )
            self_value = Fraction.from_float(self_float)
            target_self_lower = Fraction(1) + target_diagonal_lower / rate_fraction
            target_self_upper = Fraction(1) + target_diagonal_upper / rate_fraction
            p_direct_error += max(
                self_value - target_self_lower,
                target_self_upper - self_value,
            )
            p_rounding += abs(Fraction(1) + diagonal / rate_fraction - self_value)
            p_row_sum += self_value
            qhat_abs_row_sum = -diagonal + rate_center
            killing_uncertainty = _interval_radius(
                kill_lower_float,
                kill_upper_float,
                kill_centre_float,
            )
            candidates = {
                "delta_q": q_error,
                "delta_p_direct": p_direct_error,
                "p_coefficient_rounding": p_rounding,
                "maximum_center_row_sum": p_row_sum,
                "maximum_qhat_abs_row_sum": qhat_abs_row_sum,
                "maximum_killing_upper": kill_upper,
                "maximum_killing_uncertainty": killing_uncertainty,
            }
            for name, candidate in candidates.items():
                maxima[name] = _update_maximum(*maxima[name], candidate, flat)

    delta_q, delta_q_index = maxima["delta_q"]
    p_rounding_exact, p_rounding_index = maxima["p_coefficient_rounding"]
    delta_p_direct, delta_p_direct_index = maxima["delta_p_direct"]
    delta_p_via_q = delta_q / rate_fraction + p_rounding_exact
    delta_p_selected = min(delta_p_direct, delta_p_via_q)
    return (
        ExactWitness("maximum_target_exit_upper", maximum_exit, maximum_exit_index),
        ExactWitness("maximum_center_exit", maximum_center_exit, maximum_center_exit_index),
        ExactWitness("delta_q", delta_q, delta_q_index),
        ExactWitness("delta_p_direct", delta_p_direct, delta_p_direct_index),
        ExactWitness("p_coefficient_rounding", p_rounding_exact, p_rounding_index),
        ExactWitness("delta_p_via_q", delta_p_via_q, -1),
        ExactWitness("delta_p_selected", delta_p_selected, -1),
        ExactWitness("maximum_center_row_sum", *maxima["maximum_center_row_sum"]),
        ExactWitness("maximum_qhat_abs_row_sum", *maxima["maximum_qhat_abs_row_sum"]),
        ExactWitness("maximum_killing_upper", *maxima["maximum_killing_upper"]),
        ExactWitness(
            "maximum_killing_uncertainty",
            *maxima["maximum_killing_uncertainty"],
        ),
    )


def build_packed_tensor_kernel(
    inputs: PackedKernelInputs,
    contract: KernelBuildContract,
) -> PackedTensorKernel:
    """Build with two exact passes, then one owned-byte witness rebind pass."""

    validate_kernel_inputs(inputs, contract)
    if contract.maximum_working_bytes < (
        STREAMING_DECLARED_WORKING_BYTES_PER_STATE
        * min(math.prod(contract.tensor_shape), contract.block_size)
    ):
        raise PackedF0Failure(HOLD_RESOURCE, "streaming builder working-byte cap is too small")
    axes = tuple(_load_canonical_axis(axis) for axis in inputs.axes)
    killing = load_canonical_packed_intervals(inputs.killing)
    shape = contract.tensor_shape
    states = math.prod(shape)
    strides = _axis_strides(shape)

    # Pass one: exact maximum exit and exact maximum centre exit.  Fraction
    # objects are scalar scratch and are discarded every row; only two maxima
    # and their witnesses remain live.
    maximum_exit = Fraction(0)
    maximum_exit_index = 0
    maximum_center_exit = Fraction(0)
    maximum_center_exit_index = 0
    for start in range(0, states, contract.block_size):
        stop = min(states, start + contract.block_size)
        for flat in range(start, stop):
            kill_lower = float(killing.intervals[flat, 0])
            kill_upper = float(killing.intervals[flat, 1])
            exit_upper = Fraction.from_float(kill_upper)
            center_exit = Fraction.from_float(_interval_centre(kill_lower, kill_upper))
            for axis, stride in zip(axes, strides, strict=True):
                coordinate = _axis_index(flat, size=axis.size, stride=stride)
                for source in (axis.forward, axis.backward):
                    lower = float(source.intervals[coordinate, 0])
                    upper = float(source.intervals[coordinate, 1])
                    exit_upper += Fraction.from_float(upper)
                    center_exit += Fraction.from_float(_interval_centre(lower, upper))
            maximum_exit, maximum_exit_index = _update_maximum(
                maximum_exit,
                maximum_exit_index,
                exit_upper,
                flat,
            )
            maximum_center_exit, maximum_center_exit_index = _update_maximum(
                maximum_center_exit,
                maximum_center_exit_index,
                center_exit,
                flat,
            )
    minimum_rate = max(maximum_exit, maximum_center_exit)
    if contract.uniformization_rate is None:
        rate = _fraction_upper(minimum_rate)
        rate_fraction = Fraction.from_float(rate)
    else:
        rate_fraction = contract.uniformization_rate
        rate = float(rate_fraction)
        if Fraction.from_float(rate) != rate_fraction:
            raise PackedF0Failure(HOLD_RATE, "uniformization rate is not binary64-exact")
    if rate_fraction <= 0 or rate_fraction < minimum_rate:
        raise PackedF0Failure(HOLD_RATE, "uniformization rate misses an exact exit bound")

    forward, backward, p_forward, p_backward = _build_axis_centres(axes, rate_fraction)
    killing_center = np.empty(states, dtype=np.float64)
    diagonal_center = np.empty(states, dtype=np.float64)
    p_self_center = np.empty(states, dtype=np.float64)

    maxima: dict[str, tuple[Fraction, int]] = {
        "delta_q": (Fraction(0), 0),
        "delta_p_direct": (Fraction(0), 0),
        "p_coefficient_rounding": (Fraction(0), 0),
        "maximum_center_row_sum": (Fraction(0), 0),
        "maximum_qhat_abs_row_sum": (Fraction(0), 0),
        "maximum_killing_upper": (Fraction(0), 0),
        "maximum_killing_uncertainty": (Fraction(0), 0),
    }
    canonical_sources_sha256 = _canonical_kernel_sources_digest(axes, killing, contract)
    if not hmac.compare_digest(
        canonical_sources_sha256,
        _kernel_inputs_digest(inputs, contract),
    ):
        raise PackedF0Failure(HOLD_STREAMING_LEDGER, "owned source digest changed during load")
    source_chain = hashlib.sha256()
    source_chain.update(SOURCE_CHAIN_DOMAIN)
    source_chain.update(bytes.fromhex(canonical_sources_sha256))
    derived_chain = hashlib.sha256()
    derived_chain.update(DERIVED_CHAIN_DOMAIN)
    derived_chain.update(bytes.fromhex(canonical_sources_sha256))
    block_count = 0

    # Pass two: regenerate every exact row, fill the three full numerical
    # arrays, and reduce all exact ledgers immediately.
    for start in range(0, states, contract.block_size):
        stop = min(states, start + contract.block_size)
        for flat in range(start, stop):
            kill_lower_float = float(killing.intervals[flat, 0])
            kill_upper_float = float(killing.intervals[flat, 1])
            kill_lower = Fraction.from_float(kill_lower_float)
            kill_upper = Fraction.from_float(kill_upper_float)
            kill_centre_float = _interval_centre(kill_lower_float, kill_upper_float)
            kill_centre = Fraction.from_float(kill_centre_float)
            killing_center[flat] = kill_centre_float

            rate_lower = Fraction(0)
            rate_upper = Fraction(0)
            rate_center = Fraction(0)
            off_diagonal_error = Fraction(0)
            p_direct_error = Fraction(0)
            p_rounding = Fraction(0)
            p_row_sum = Fraction(0)
            for dimension, (axis, stride) in enumerate(zip(axes, strides, strict=True)):
                coordinate = _axis_index(flat, size=axis.size, stride=stride)
                for source, q_values, p_values in (
                    (axis.forward, forward[dimension], p_forward[dimension]),
                    (axis.backward, backward[dimension], p_backward[dimension]),
                ):
                    lower_float = float(source.intervals[coordinate, 0])
                    upper_float = float(source.intervals[coordinate, 1])
                    lower = Fraction.from_float(lower_float)
                    upper = Fraction.from_float(upper_float)
                    q_value_float = float(q_values[coordinate])
                    q_value = Fraction.from_float(q_value_float)
                    p_value = Fraction.from_float(float(p_values[coordinate]))
                    rate_lower += lower
                    rate_upper += upper
                    rate_center += q_value
                    off_diagonal_error += _interval_radius(
                        lower_float,
                        upper_float,
                        q_value_float,
                    )
                    p_direct_error += max(
                        p_value - lower / rate_fraction,
                        upper / rate_fraction - p_value,
                    )
                    p_rounding += abs(q_value / rate_fraction - p_value)
                    p_row_sum += p_value

            exit_lower = rate_lower + kill_lower
            exit_upper = rate_upper + kill_upper
            center_exit = rate_center + kill_centre
            target_diagonal_lower = -exit_upper
            target_diagonal_upper = -exit_lower
            diagonal_float = _fraction_lower(-center_exit)
            diagonal = Fraction.from_float(diagonal_float)
            diagonal_center[flat] = diagonal_float
            diagonal_error = max(
                diagonal - target_diagonal_lower,
                target_diagonal_upper - diagonal,
            )
            if diagonal_error < 0:
                raise PackedF0Failure(HOLD_STREAMING_LEDGER, "diagonal missed exact interval")
            q_error = off_diagonal_error + diagonal_error

            self_float = _fraction_lower(Fraction(1) + diagonal / rate_fraction)
            self_value = Fraction.from_float(self_float)
            p_self_center[flat] = self_float
            if self_value < 0:
                raise PackedF0Failure(HOLD_ROW, "uniformized self coefficient is negative")
            target_self_lower = Fraction(1) + target_diagonal_lower / rate_fraction
            target_self_upper = Fraction(1) + target_diagonal_upper / rate_fraction
            p_direct_error += max(
                self_value - target_self_lower,
                target_self_upper - self_value,
            )
            p_rounding += abs(Fraction(1) + diagonal / rate_fraction - self_value)
            p_row_sum += self_value
            if p_row_sum < 0 or p_row_sum > 1:
                raise PackedF0Failure(HOLD_ROW, "uniformized centre row is not substochastic")
            qhat_abs_row_sum = -diagonal + rate_center
            killing_uncertainty = _interval_radius(
                kill_lower_float,
                kill_upper_float,
                kill_centre_float,
            )
            candidates = {
                "delta_q": q_error,
                "delta_p_direct": p_direct_error,
                "p_coefficient_rounding": p_rounding,
                "maximum_center_row_sum": p_row_sum,
                "maximum_qhat_abs_row_sum": qhat_abs_row_sum,
                "maximum_killing_upper": kill_upper,
                "maximum_killing_uncertainty": killing_uncertainty,
            }
            for name, candidate in candidates.items():
                maxima[name] = _update_maximum(*maxima[name], candidate, flat)
        _update_block_chains(
            source_chain,
            derived_chain,
            killing,
            start,
            stop,
            killing_center,
            diagonal_center,
            p_self_center,
        )
        block_count += 1

    _readonly(killing_center)
    _readonly(diagonal_center)
    _readonly(p_self_center)
    source_chain_sha256 = source_chain.hexdigest()
    derived_chain_sha256 = derived_chain.hexdigest()
    combined_chain = hashlib.sha256()
    combined_chain.update(COMBINED_CHAIN_DOMAIN)
    combined_chain.update(struct.pack(">QQQ", states, contract.block_size, block_count))
    combined_chain.update(bytes.fromhex(source_chain_sha256))
    combined_chain.update(bytes.fromhex(derived_chain_sha256))
    combined_chain_sha256 = combined_chain.hexdigest()
    delta_q, delta_q_index = maxima["delta_q"]
    p_rounding_exact, p_rounding_index = maxima["p_coefficient_rounding"]
    delta_p_direct, delta_p_direct_index = maxima["delta_p_direct"]
    delta_p_via_q = delta_q / rate_fraction + p_rounding_exact
    delta_p_selected = min(delta_p_direct, delta_p_via_q)
    witnesses = (
        ExactWitness("maximum_target_exit_upper", maximum_exit, maximum_exit_index),
        ExactWitness("maximum_center_exit", maximum_center_exit, maximum_center_exit_index),
        ExactWitness("delta_q", delta_q, delta_q_index),
        ExactWitness("delta_p_direct", delta_p_direct, delta_p_direct_index),
        ExactWitness("p_coefficient_rounding", p_rounding_exact, p_rounding_index),
        ExactWitness("delta_p_via_q", delta_p_via_q, -1),
        ExactWitness("delta_p_selected", delta_p_selected, -1),
        ExactWitness("maximum_center_row_sum", *maxima["maximum_center_row_sum"]),
        ExactWitness("maximum_qhat_abs_row_sum", *maxima["maximum_qhat_abs_row_sum"]),
        ExactWitness("maximum_killing_upper", *maxima["maximum_killing_upper"]),
        ExactWitness("maximum_killing_uncertainty", *maxima["maximum_killing_uncertainty"]),
    )
    named_arrays: list[tuple[str, np.ndarray]] = []
    for dimension in range(len(axes)):
        named_arrays.extend(
            (
                (f"axis_{dimension}_forward_center", forward[dimension]),
                (f"axis_{dimension}_backward_center", backward[dimension]),
                (f"axis_{dimension}_p_forward_center", p_forward[dimension]),
                (f"axis_{dimension}_p_backward_center", p_backward[dimension]),
            )
        )
    named_arrays.extend(
        (
            ("killing_center", killing_center),
            ("diagonal_center", diagonal_center),
            ("p_self_center", p_self_center),
        )
    )
    array_digests = tuple(_array_digest(name, array) for name, array in named_arrays)
    witness_binding_sha256 = _witness_binding_digest(
        source_sha256=canonical_sources_sha256,
        array_digests=array_digests,
        rate_fraction=rate_fraction,
        source_chain_sha256=source_chain_sha256,
        derived_chain_sha256=derived_chain_sha256,
        witnesses=witnesses,
    )
    ledger = StreamingExactLedger(
        schema=PACKED_KERNEL_SCHEMA,
        state_count=states,
        block_size=contract.block_size,
        maximum_working_bytes=contract.maximum_working_bytes,
        construction_exact_pass_count=2,
        witness_rebind_pass_count=1,
        backend=STREAMING_BACKEND,
        retained_per_state_fraction_objects=False,
        retained_fraction_witness_count=len(witnesses),
        block_count=block_count,
        covered_state_count=states,
        source_chain_sha256=source_chain_sha256,
        derived_chain_sha256=derived_chain_sha256,
        combined_chain_sha256=combined_chain_sha256,
        witness_binding_sha256=witness_binding_sha256,
        witnesses=witnesses,
    )
    validate_streaming_exact_ledger(ledger)
    kernel = PackedTensorKernel(
        schema=PACKED_KERNEL_SCHEMA,
        construction=KERNEL_CONSTRUCTION,
        contract=contract,
        axes=axes,
        killing=killing,
        forward_center=forward,
        backward_center=backward,
        p_forward_center=p_forward,
        p_backward_center=p_backward,
        killing_center=killing_center,
        diagonal_center=diagonal_center,
        p_self_center=p_self_center,
        rate=rate,
        rate_fraction=rate_fraction,
        ledger=ledger,
        array_digests=array_digests,
        f0_pass=False,
        science_executed=False,
        action_roundoff_proof_complete=False,
        batched_scalar_topology_complete=False,
    )
    validate_packed_tensor_kernel(kernel)
    return kernel


def _kernel_named_arrays(kernel: PackedTensorKernel) -> tuple[tuple[str, np.ndarray], ...]:
    rows: list[tuple[str, np.ndarray]] = []
    for dimension in range(len(kernel.axes)):
        rows.extend(
            (
                (f"axis_{dimension}_forward_center", kernel.forward_center[dimension]),
                (f"axis_{dimension}_backward_center", kernel.backward_center[dimension]),
                (f"axis_{dimension}_p_forward_center", kernel.p_forward_center[dimension]),
                (f"axis_{dimension}_p_backward_center", kernel.p_backward_center[dimension]),
            )
        )
    rows.extend(
        (
            ("killing_center", kernel.killing_center),
            ("diagonal_center", kernel.diagonal_center),
            ("p_self_center", kernel.p_self_center),
        )
    )
    return tuple(rows)


def _recompute_block_chain_digests(kernel: PackedTensorKernel) -> tuple[str, str, str]:
    source_sha256 = _canonical_kernel_sources_digest(
        kernel.axes,
        kernel.killing,
        kernel.contract,
    )
    source_chain = hashlib.sha256()
    source_chain.update(SOURCE_CHAIN_DOMAIN)
    source_chain.update(bytes.fromhex(source_sha256))
    derived_chain = hashlib.sha256()
    derived_chain.update(DERIVED_CHAIN_DOMAIN)
    derived_chain.update(bytes.fromhex(source_sha256))
    block_count = 0
    for start in range(0, kernel.states, kernel.contract.block_size):
        stop = min(kernel.states, start + kernel.contract.block_size)
        _update_block_chains(
            source_chain,
            derived_chain,
            kernel.killing,
            start,
            stop,
            kernel.killing_center,
            kernel.diagonal_center,
            kernel.p_self_center,
        )
        block_count += 1
    source_chain_sha256 = source_chain.hexdigest()
    derived_chain_sha256 = derived_chain.hexdigest()
    combined_chain = hashlib.sha256()
    combined_chain.update(COMBINED_CHAIN_DOMAIN)
    combined_chain.update(
        struct.pack(">QQQ", kernel.states, kernel.contract.block_size, block_count)
    )
    combined_chain.update(bytes.fromhex(source_chain_sha256))
    combined_chain.update(bytes.fromhex(derived_chain_sha256))
    return source_chain_sha256, derived_chain_sha256, combined_chain.hexdigest()


def validate_packed_tensor_kernel(kernel: PackedTensorKernel) -> None:
    """Reject nested subtypes, mutated arrays, and mutated exact ledgers."""

    if type(kernel) is not PackedTensorKernel:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "kernel has wrong exact type")
    validate_kernel_build_contract(kernel.contract)
    if (
        type(kernel.schema) is not str
        or kernel.schema != PACKED_KERNEL_SCHEMA
        or type(kernel.construction) is not str
        or kernel.construction != KERNEL_CONSTRUCTION
        or type(kernel.axes) is not tuple
        or len(kernel.axes) != len(kernel.contract.tensor_shape)
        or any(type(axis) is not CanonicalPackedAxis for axis in kernel.axes)
        or type(kernel.killing) is not CanonicalPackedIntervals
        or type(kernel.forward_center) is not tuple
        or type(kernel.backward_center) is not tuple
        or type(kernel.p_forward_center) is not tuple
        or type(kernel.p_backward_center) is not tuple
        or type(kernel.rate) is not float
        or type(kernel.rate_fraction) is not Fraction
        or Fraction.from_float(kernel.rate) != kernel.rate_fraction
        or type(kernel.ledger) is not StreamingExactLedger
        or type(kernel.array_digests) is not tuple
        or type(kernel.f0_pass) is not bool
        or kernel.f0_pass is not False
        or type(kernel.science_executed) is not bool
        or kernel.science_executed is not False
        or type(kernel.action_roundoff_proof_complete) is not bool
        or kernel.action_roundoff_proof_complete is not False
        or type(kernel.batched_scalar_topology_complete) is not bool
        or kernel.batched_scalar_topology_complete is not False
    ):
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "kernel boundary fields are invalid")
    for axis in kernel.axes:
        validate_canonical_axis(axis)
    validate_canonical_packed_intervals(kernel.killing)
    validate_streaming_exact_ledger(kernel.ledger)
    if (
        tuple(axis.size for axis in kernel.axes) != kernel.contract.tensor_shape
        or kernel.killing.manifest.logical_shape != kernel.contract.tensor_shape
        or kernel.ledger.state_count != kernel.states
        or kernel.ledger.block_size != kernel.contract.block_size
        or kernel.ledger.maximum_working_bytes != kernel.contract.maximum_working_bytes
        or len(kernel.forward_center) != len(kernel.axes)
        or len(kernel.backward_center) != len(kernel.axes)
        or len(kernel.p_forward_center) != len(kernel.axes)
        or len(kernel.p_backward_center) != len(kernel.axes)
    ):
        raise PackedF0Failure(HOLD_PACKED_SCHEMA, "kernel shapes disagree")
    named_arrays = _kernel_named_arrays(kernel)
    if len(named_arrays) != len(kernel.array_digests):
        raise PackedF0Failure(HOLD_STREAMING_LEDGER, "kernel array digest count changed")
    for (name, array), digest in zip(named_arrays, kernel.array_digests, strict=True):
        _validate_array_digest(digest)
        expected_shape = (
            (kernel.axes[int(name.split("_")[1])].size,)
            if name.startswith("axis_")
            else (kernel.states,)
        )
        trusted = _require_plain_native_owned_readonly_float64(
            array,
            expected_shape=expected_shape,
            label=name,
        )
        if (
            digest.name != name
            or digest.shape != expected_shape
            or digest.raw_byte_length != trusted.nbytes
            or not hmac.compare_digest(digest.raw_sha256, _array_raw_sha256(trusted))
        ):
            raise PackedF0Failure(HOLD_STREAMING_LEDGER, f"{name} raw digest changed")
    witnesses = {witness.name: witness for witness in kernel.ledger.witnesses}
    if (
        kernel.rate_fraction < witnesses["maximum_target_exit_upper"].value
        or kernel.rate_fraction < witnesses["maximum_center_exit"].value
        or witnesses["delta_p_via_q"].value
        != witnesses["delta_q"].value / kernel.rate_fraction
        + witnesses["p_coefficient_rounding"].value
        or witnesses["delta_p_selected"].value
        != min(
            witnesses["delta_p_direct"].value,
            witnesses["delta_p_via_q"].value,
        )
        or witnesses["maximum_center_row_sum"].value > 1
    ):
        raise PackedF0Failure(HOLD_STREAMING_LEDGER, "exact witness relations changed")
    rebound_witnesses = _recompute_exact_witnesses_from_owned_kernel(kernel)
    if rebound_witnesses != kernel.ledger.witnesses:
        raise PackedF0Failure(
            HOLD_STREAMING_LEDGER,
            "exact witnesses are not bound to the owned kernel bytes",
        )
    source_chain, derived_chain, combined_chain = _recompute_block_chain_digests(kernel)
    if (
        not hmac.compare_digest(source_chain, kernel.ledger.source_chain_sha256)
        or not hmac.compare_digest(derived_chain, kernel.ledger.derived_chain_sha256)
        or not hmac.compare_digest(combined_chain, kernel.ledger.combined_chain_sha256)
    ):
        raise PackedF0Failure(HOLD_STREAMING_LEDGER, "streaming chain disagrees with owned bytes")
    expected_binding = _witness_binding_digest(
        source_sha256=_canonical_kernel_sources_digest(
            kernel.axes,
            kernel.killing,
            kernel.contract,
        ),
        array_digests=kernel.array_digests,
        rate_fraction=kernel.rate_fraction,
        source_chain_sha256=source_chain,
        derived_chain_sha256=derived_chain,
        witnesses=rebound_witnesses,
    )
    if not hmac.compare_digest(expected_binding, kernel.ledger.witness_binding_sha256):
        raise PackedF0Failure(HOLD_STREAMING_LEDGER, "witness binding digest changed")


def _kernel_replay_digest(kernel: PackedTensorKernel) -> str:
    validate_packed_tensor_kernel(kernel)
    return _canonical_json_digest(
        {
            "array_digests": [
                {
                    "name": digest.name,
                    "raw_byte_length": digest.raw_byte_length,
                    "raw_sha256": digest.raw_sha256,
                    "shape": list(digest.shape),
                }
                for digest in kernel.array_digests
            ],
            "construction": kernel.construction,
            "contract": _contract_json(kernel.contract),
            "ledger": _ledger_json(kernel.ledger),
            "rate": kernel.rate.hex(),
            "rate_fraction": _fraction_text(kernel.rate_fraction),
            "schema": kernel.schema,
        }
    )


@dataclass(frozen=True, slots=True)
class CanonicalFloat64Vector:
    logical_shape: tuple[int, ...]
    values: np.ndarray
    raw_sha256: str
    nonnegative: bool
    source_sha256: str


def interval_centres_as_vector(source: CanonicalPackedIntervals) -> CanonicalFloat64Vector:
    """Create a private owned nominal vector from one canonical interval source."""

    validate_canonical_packed_intervals(source)
    values = np.empty(source.manifest.state_count, dtype=np.float64)
    for start in range(0, source.manifest.state_count, source.manifest.block_size):
        stop = min(source.manifest.state_count, start + source.manifest.block_size)
        for index in range(start, stop):
            values[index] = _interval_centre(
                float(source.intervals[index, 0]),
                float(source.intervals[index, 1]),
            )
    _readonly(values)
    vector = CanonicalFloat64Vector(
        logical_shape=source.manifest.logical_shape,
        values=values,
        raw_sha256=_array_raw_sha256(values),
        nonnegative=source.manifest.nonnegative,
        source_sha256=source.manifest.raw_sha256,
    )
    validate_canonical_vector(vector)
    return vector


def validate_canonical_vector(
    vector: CanonicalFloat64Vector,
    *,
    block_size: int = DEFAULT_VALIDATION_BLOCK_SIZE,
) -> None:
    if type(vector) is not CanonicalFloat64Vector:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "vector has wrong exact type")
    shape = _require_exact_shape(vector.logical_shape, label="vector logical shape")
    if (
        not _is_hex_digest(vector.raw_sha256)
        or type(vector.nonnegative) is not bool
        or not _is_hex_digest(vector.source_sha256)
        or type(block_size) is not int
        or block_size < 1
    ):
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "vector metadata is invalid")
    values = _require_plain_native_owned_readonly_float64(
        vector.values,
        expected_shape=(math.prod(shape),),
        label="canonical vector",
    )
    before = _array_raw_sha256(values)
    if not hmac.compare_digest(before, vector.raw_sha256):
        raise PackedF0Failure(HOLD_PACKED_HASH, "vector raw bytes changed")
    validation_size = min(values.size, block_size)
    validation_scratch = np.empty(validation_size, dtype=np.bool_)
    for start in range(0, values.size, block_size):
        stop = min(values.size, start + block_size)
        count = stop - start
        block = values[start:stop]
        scratch = validation_scratch[:count]
        np.isfinite(block, out=scratch)
        if not bool(np.all(scratch)):
            raise PackedF0Failure(HOLD_ACTION, "vector contains a nonfinite value")
        if vector.nonnegative:
            np.less(block, 0.0, out=scratch)
            if bool(np.any(scratch)):
                raise PackedF0Failure(
                    HOLD_ACTION,
                    "nonnegative vector contains a negative value",
                )
    if not hmac.compare_digest(before, _array_raw_sha256(values)):
        raise PackedF0Failure(HOLD_PACKED_HASH, "vector changed during validation")


@dataclass(frozen=True, slots=True)
class BlockActionContract:
    schema: str
    tensor_shape: tuple[int, ...]
    block_size: int
    maximum_scratch_bytes: int
    scratch_payload_bytes: int
    summation_order: tuple[str, ...]
    backend: str
    runtime: str
    single_threaded: bool
    directed_roundoff_proof_complete: bool


@dataclass(frozen=True, slots=True)
class BlockActionResult:
    schema: str
    operator: str
    nominal: CanonicalFloat64Vector
    input_raw_sha256: str
    kernel_replay_sha256: str
    action_contract_sha256: str
    block_count: int
    scratch_payload_bytes: int
    f0_pass: bool


def make_block_action_contract(
    tensor_shape: tuple[int, ...],
    *,
    block_size: int,
    maximum_scratch_bytes: int,
) -> BlockActionContract:
    shape = _require_exact_shape(tensor_shape, label="action tensor shape")
    if len(shape) > MAXIMUM_DIMENSIONS or type(block_size) is not int or block_size < 1:
        raise PackedF0Failure(HOLD_PACKED_SCHEMA, "action shape/block size is invalid")
    scratch = ACTION_WORKSPACE_BYTES_PER_STATE * min(math.prod(shape), block_size)
    order = ("self",) + tuple(
        role
        for dimension in range(len(shape))
        for role in (
            f"axis_{dimension}_forward_incoming",
            f"axis_{dimension}_backward_incoming",
        )
    )
    contract = BlockActionContract(
        schema=PACKED_ACTION_SCHEMA,
        tensor_shape=shape,
        block_size=block_size,
        maximum_scratch_bytes=maximum_scratch_bytes,
        scratch_payload_bytes=scratch,
        summation_order=order,
        backend=ACTION_BACKEND,
        runtime=f"python-{sys.version_info.major}.{sys.version_info.minor}|numpy-{np.__version__}",
        single_threaded=True,
        directed_roundoff_proof_complete=False,
    )
    validate_block_action_contract(contract)
    return contract


def validate_block_action_contract(contract: BlockActionContract) -> None:
    if type(contract) is not BlockActionContract:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "action contract has wrong exact type")
    shape = _require_exact_shape(contract.tensor_shape, label="action tensor shape")
    expected_order = ("self",) + tuple(
        role
        for dimension in range(len(shape))
        for role in (
            f"axis_{dimension}_forward_incoming",
            f"axis_{dimension}_backward_incoming",
        )
    )
    required = ACTION_WORKSPACE_BYTES_PER_STATE * min(math.prod(shape), contract.block_size)
    if (
        type(contract.schema) is not str
        or contract.schema != PACKED_ACTION_SCHEMA
        or len(shape) > MAXIMUM_DIMENSIONS
        or type(contract.block_size) is not int
        or contract.block_size < 1
        or type(contract.maximum_scratch_bytes) is not int
        or type(contract.scratch_payload_bytes) is not int
        or contract.scratch_payload_bytes != required
        or contract.maximum_scratch_bytes < required
        or type(contract.summation_order) is not tuple
        or any(type(value) is not str for value in contract.summation_order)
        or contract.summation_order != expected_order
        or type(contract.backend) is not str
        or contract.backend != ACTION_BACKEND
        or type(contract.runtime) is not str
        or contract.runtime
        != f"python-{sys.version_info.major}.{sys.version_info.minor}|numpy-{np.__version__}"
        or type(contract.single_threaded) is not bool
        or contract.single_threaded is not True
        or type(contract.directed_roundoff_proof_complete) is not bool
        or contract.directed_roundoff_proof_complete is not False
    ):
        raise PackedF0Failure(HOLD_RESOURCE, "block action contract is invalid")


def _action_contract_json(contract: BlockActionContract) -> dict[str, object]:
    validate_block_action_contract(contract)
    return {
        "backend": contract.backend,
        "block_size": contract.block_size,
        "directed_roundoff_proof_complete": contract.directed_roundoff_proof_complete,
        "maximum_scratch_bytes": contract.maximum_scratch_bytes,
        "runtime": contract.runtime,
        "schema": contract.schema,
        "scratch_payload_bytes": contract.scratch_payload_bytes,
        "single_threaded": contract.single_threaded,
        "summation_order": list(contract.summation_order),
        "tensor_shape": list(contract.tensor_shape),
    }


def _action_contract_digest(contract: BlockActionContract) -> str:
    return _canonical_json_digest(_action_contract_json(contract))


def _block_transpose_action(
    kernel: PackedTensorKernel,
    vector: CanonicalFloat64Vector,
    contract: BlockActionContract,
    *,
    operator: str,
) -> BlockActionResult:
    validate_packed_tensor_kernel(kernel)
    validate_block_action_contract(contract)
    validate_canonical_vector(vector, block_size=contract.block_size)
    kernel_replay_sha256 = _kernel_replay_digest(kernel)
    action_contract_sha256 = _action_contract_digest(contract)
    if (
        type(operator) is not str
        or operator not in {"P", "Q"}
        or vector.logical_shape != kernel.contract.tensor_shape
        or contract.tensor_shape != kernel.contract.tensor_shape
        or contract.block_size != kernel.contract.block_size
    ):
        raise PackedF0Failure(HOLD_ACTION, "block action inputs disagree")
    if operator == "P" and not vector.nonnegative:
        raise PackedF0Failure(HOLD_ACTION, "P action requires a nonnegative canonical vector")

    block = min(kernel.states, contract.block_size)
    base = np.arange(block, dtype=np.int64)
    flat = np.empty(block, dtype=np.int64)
    coordinate = np.empty(block, dtype=np.int64)
    source_index = np.empty(block, dtype=np.int64)
    rate_index = np.empty(block, dtype=np.int64)
    mask = np.empty(block, dtype=np.bool_)
    scratch = np.empty(block, dtype=np.float64)
    term = np.empty(block, dtype=np.float64)
    coefficient = np.empty(block, dtype=np.float64)
    output = np.empty(kernel.states, dtype=np.float64)
    values = vector.values
    self_values = kernel.p_self_center if operator == "P" else kernel.diagonal_center
    forward_values = kernel.p_forward_center if operator == "P" else kernel.forward_center
    backward_values = kernel.p_backward_center if operator == "P" else kernel.backward_center
    strides = _axis_strides(kernel.contract.tensor_shape)

    block_count = 0
    for start in range(0, kernel.states, contract.block_size):
        stop = min(kernel.states, start + contract.block_size)
        count = stop - start
        block_count += 1
        np.add(base[:count], start, out=flat[:count])
        np.multiply(values[start:stop], self_values[start:stop], out=scratch[:count])
        for dimension, (axis, stride) in enumerate(zip(kernel.axes, strides, strict=True)):
            np.floor_divide(flat[:count], stride, out=coordinate[:count])
            np.remainder(coordinate[:count], axis.size, out=coordinate[:count])

            # Incoming forward edge: source coordinate is target-1.
            np.equal(coordinate[:count], 0, out=mask[:count])
            np.subtract(flat[:count], stride, out=source_index[:count])
            np.subtract(coordinate[:count], 1, out=rate_index[:count])
            if axis.periodic:
                np.add(
                    flat[:count],
                    (axis.size - 1) * stride,
                    out=source_index[:count],
                    where=mask[:count],
                )
                np.copyto(rate_index[:count], axis.size - 1, where=mask[:count])
            else:
                np.copyto(source_index[:count], 0, where=mask[:count])
                np.copyto(rate_index[:count], 0, where=mask[:count])
            np.take(values, source_index[:count], out=term[:count], mode="clip")
            np.take(
                forward_values[dimension],
                rate_index[:count],
                out=coefficient[:count],
                mode="clip",
            )
            np.multiply(term[:count], coefficient[:count], out=term[:count])
            if not axis.periodic:
                np.copyto(term[:count], 0.0, where=mask[:count])
            np.add(scratch[:count], term[:count], out=scratch[:count])

            # Incoming backward edge: source coordinate is target+1.
            np.equal(coordinate[:count], axis.size - 1, out=mask[:count])
            np.add(flat[:count], stride, out=source_index[:count])
            np.add(coordinate[:count], 1, out=rate_index[:count])
            if axis.periodic:
                np.subtract(
                    flat[:count],
                    (axis.size - 1) * stride,
                    out=source_index[:count],
                    where=mask[:count],
                )
                np.copyto(rate_index[:count], 0, where=mask[:count])
            else:
                np.copyto(source_index[:count], 0, where=mask[:count])
                np.copyto(rate_index[:count], 0, where=mask[:count])
            np.take(values, source_index[:count], out=term[:count], mode="clip")
            np.take(
                backward_values[dimension],
                rate_index[:count],
                out=coefficient[:count],
                mode="clip",
            )
            np.multiply(term[:count], coefficient[:count], out=term[:count])
            if not axis.periodic:
                np.copyto(term[:count], 0.0, where=mask[:count])
            np.add(scratch[:count], term[:count], out=scratch[:count])
        output[start:stop] = scratch[:count]

    for start in range(0, kernel.states, contract.block_size):
        stop = min(kernel.states, start + contract.block_size)
        count = stop - start
        block_output = output[start:stop]
        np.isfinite(block_output, out=mask[:count])
        invalid = not bool(np.all(mask[:count]))
        if operator == "P":
            np.less(block_output, 0.0, out=mask[:count])
            invalid = invalid or bool(np.any(mask[:count]))
        if invalid:
            raise PackedF0Failure(HOLD_ACTION, "block action output is invalid")
    _readonly(output)
    result_vector = CanonicalFloat64Vector(
        logical_shape=kernel.contract.tensor_shape,
        values=output,
        raw_sha256=_array_raw_sha256(output),
        nonnegative=operator == "P",
        source_sha256=vector.raw_sha256,
    )
    result = BlockActionResult(
        schema=PACKED_ACTION_SCHEMA,
        operator=operator,
        nominal=result_vector,
        input_raw_sha256=vector.raw_sha256,
        kernel_replay_sha256=kernel_replay_sha256,
        action_contract_sha256=action_contract_sha256,
        block_count=block_count,
        scratch_payload_bytes=contract.scratch_payload_bytes,
        f0_pass=False,
    )
    del base, coefficient, coordinate, flat, mask, rate_index, scratch, source_index, term
    # Recheck every consumed byte after the action.  The production boundary
    # additionally owns these objects in a fresh process and exposes no array.
    validate_packed_tensor_kernel(kernel)
    validate_canonical_vector(vector, block_size=contract.block_size)
    validate_block_action_result(result, validation_block_size=contract.block_size)
    return result


def block_p_transpose(
    kernel: PackedTensorKernel,
    vector: CanonicalFloat64Vector,
    contract: BlockActionContract,
) -> BlockActionResult:
    """Apply the packed centre ``P.T`` with fixed block/halo storage."""

    return _block_transpose_action(kernel, vector, contract, operator="P")


def block_q_transpose(
    kernel: PackedTensorKernel,
    vector: CanonicalFloat64Vector,
    contract: BlockActionContract,
) -> BlockActionResult:
    """Apply the packed centre ``Q.T`` with fixed block/halo storage."""

    return _block_transpose_action(kernel, vector, contract, operator="Q")


def validate_block_action_result(
    result: BlockActionResult,
    *,
    validation_block_size: int = DEFAULT_VALIDATION_BLOCK_SIZE,
) -> None:
    if type(result) is not BlockActionResult:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "action result has wrong exact type")
    if (
        type(result.schema) is not str
        or result.schema != PACKED_ACTION_SCHEMA
        or type(result.operator) is not str
        or result.operator not in {"P", "Q"}
        or type(result.nominal) is not CanonicalFloat64Vector
        or not _is_hex_digest(result.input_raw_sha256)
        or not _is_hex_digest(result.kernel_replay_sha256)
        or not _is_hex_digest(result.action_contract_sha256)
        or type(result.block_count) is not int
        or result.block_count < 1
        or type(result.scratch_payload_bytes) is not int
        or result.scratch_payload_bytes < 1
        or type(result.f0_pass) is not bool
        or result.f0_pass is not False
    ):
        raise PackedF0Failure(HOLD_ACTION, "action result schema is invalid")
    validate_canonical_vector(result.nominal, block_size=validation_block_size)
    if result.nominal.nonnegative is not (result.operator == "P"):
        raise PackedF0Failure(HOLD_ACTION, "action result sign contract changed")


@dataclass(frozen=True, slots=True)
class ProducerActionArtifact:
    schema: str
    status: str
    producer_pid: int
    producer_runtime: str
    kernel_inputs_sha256: str
    initial_source_sha256: str
    initial_manifest_sha256: str
    kernel_contract_sha256: str
    kernel_replay_sha256: str
    kernel_ledger_sha256: str
    witness_binding_sha256: str
    action_contract_sha256: str
    action_output_bytes: bytes
    action_output_sha256: str
    action_output_byte_length: int
    action_block_count: int
    action_scratch_payload_bytes: int
    science_executed: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class VerifierReplayReceipt:
    schema: str
    status: str
    producer_pid: int
    verifier_pid: int
    fresh_process: bool
    verifier_owned_replay: bool
    producer_arrays_accepted: bool
    launch_capability_sha256: str
    request_sha256: str
    artifact_body_sha256: str
    initial_manifest_sha256: str
    witness_binding_sha256: str
    kernel_replay_sha256: str
    action_output_sha256: str
    science_executed: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class _VerifierAuthorization:
    launch_parent_pid: int
    capability: bytes
    request_sha256: str
    artifact_body_sha256: str


def _producer_runtime() -> str:
    return f"python-{sys.version_info.major}.{sys.version_info.minor}|numpy-{np.__version__}"


def validate_producer_action_artifact(artifact: ProducerActionArtifact) -> None:
    if type(artifact) is not ProducerActionArtifact:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "producer artifact has wrong exact type")
    digests = (
        artifact.kernel_inputs_sha256,
        artifact.initial_source_sha256,
        artifact.initial_manifest_sha256,
        artifact.kernel_contract_sha256,
        artifact.kernel_replay_sha256,
        artifact.kernel_ledger_sha256,
        artifact.witness_binding_sha256,
        artifact.action_contract_sha256,
        artifact.action_output_sha256,
    )
    if (
        type(artifact.schema) is not str
        or artifact.schema != PACKED_REPLAY_SCHEMA
        or type(artifact.status) is not str
        or artifact.status != "PRODUCER_METHOD_ARTIFACT_NOT_AUTHORITY"
        or type(artifact.producer_pid) is not int
        or artifact.producer_pid < 1
        or type(artifact.producer_runtime) is not str
        or artifact.producer_runtime != _producer_runtime()
        or any(not _is_hex_digest(value) for value in digests)
        or type(artifact.action_output_bytes) is not bytes
        or type(artifact.action_output_byte_length) is not int
        or artifact.action_output_byte_length != len(artifact.action_output_bytes)
        or artifact.action_output_byte_length < 1
        or not hmac.compare_digest(
            _sha256(artifact.action_output_bytes),
            artifact.action_output_sha256,
        )
        or type(artifact.action_block_count) is not int
        or artifact.action_block_count < 1
        or type(artifact.action_scratch_payload_bytes) is not int
        or artifact.action_scratch_payload_bytes < 1
        or type(artifact.science_executed) is not bool
        or artifact.science_executed is not False
        or type(artifact.f0_pass) is not bool
        or artifact.f0_pass is not False
    ):
        raise PackedF0Failure(HOLD_REPLAY, "producer artifact schema is invalid")


def _initial_manifest_digest(payload: PackedIntervalPayload) -> str:
    validate_packed_interval_payload(payload)
    return _canonical_json_digest(_manifest_json(payload.manifest))


def _artifact_body_digest(artifact: ProducerActionArtifact) -> str:
    validate_producer_action_artifact(artifact)
    payload = {
        "action_block_count": artifact.action_block_count,
        "action_contract_sha256": artifact.action_contract_sha256,
        "action_output_byte_length": artifact.action_output_byte_length,
        "action_output_sha256": artifact.action_output_sha256,
        "action_scratch_payload_bytes": artifact.action_scratch_payload_bytes,
        "f0_pass": artifact.f0_pass,
        "initial_manifest_sha256": artifact.initial_manifest_sha256,
        "initial_source_sha256": artifact.initial_source_sha256,
        "kernel_contract_sha256": artifact.kernel_contract_sha256,
        "kernel_inputs_sha256": artifact.kernel_inputs_sha256,
        "kernel_ledger_sha256": artifact.kernel_ledger_sha256,
        "kernel_replay_sha256": artifact.kernel_replay_sha256,
        "producer_runtime": artifact.producer_runtime,
        "schema": artifact.schema,
        "science_executed": artifact.science_executed,
        "status": artifact.status,
        "witness_binding_sha256": artifact.witness_binding_sha256,
    }
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return _sha256(REPLAY_REQUEST_DOMAIN + encoded)


def _replay_request_digest(
    inputs: PackedKernelInputs,
    initial_payload: PackedIntervalPayload,
    kernel_contract: KernelBuildContract,
    action_contract: BlockActionContract,
    artifact: ProducerActionArtifact,
) -> str:
    validate_kernel_inputs(inputs, kernel_contract)
    validate_packed_interval_payload(initial_payload)
    validate_block_action_contract(action_contract)
    validate_producer_action_artifact(artifact)
    payload = {
        "action_contract_sha256": _action_contract_digest(action_contract),
        "artifact_body_sha256": _artifact_body_digest(artifact),
        "initial_manifest_sha256": _initial_manifest_digest(initial_payload),
        "kernel_contract_sha256": _canonical_json_digest(_contract_json(kernel_contract)),
        "kernel_inputs_sha256": _kernel_inputs_digest(inputs, kernel_contract),
    }
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return _sha256(REPLAY_REQUEST_DOMAIN + encoded)


def _capability_digest(capability: bytes) -> str:
    return _sha256(REPLAY_CAPABILITY_DOMAIN + capability)


def produce_action_artifact(
    inputs: PackedKernelInputs,
    initial_payload: PackedIntervalPayload,
    kernel_contract: KernelBuildContract,
    action_contract: BlockActionContract,
) -> ProducerActionArtifact:
    """Produce a method-only action artifact without exposing numerical arrays."""

    validate_kernel_inputs(inputs, kernel_contract)
    validate_packed_interval_payload(initial_payload)
    validate_block_action_contract(action_contract)
    if (
        initial_payload.manifest.role != "science_free_initial"
        or initial_payload.manifest.logical_shape != kernel_contract.tensor_shape
        or not initial_payload.manifest.nonnegative
        or action_contract.tensor_shape != kernel_contract.tensor_shape
    ):
        raise PackedF0Failure(HOLD_SCIENCE_BOUNDARY, "initial/action source contract is invalid")
    kernel = build_packed_tensor_kernel(inputs, kernel_contract)
    initial = interval_centres_as_vector(load_canonical_packed_intervals(initial_payload))
    action = block_p_transpose(kernel, initial, action_contract)
    action_output_bytes = bytes(memoryview(action.nominal.values).cast("B"))
    artifact = ProducerActionArtifact(
        schema=PACKED_REPLAY_SCHEMA,
        status="PRODUCER_METHOD_ARTIFACT_NOT_AUTHORITY",
        producer_pid=os.getpid(),
        producer_runtime=_producer_runtime(),
        kernel_inputs_sha256=_kernel_inputs_digest(inputs, kernel_contract),
        initial_source_sha256=initial_payload.manifest.raw_sha256,
        initial_manifest_sha256=_initial_manifest_digest(initial_payload),
        kernel_contract_sha256=_canonical_json_digest(_contract_json(kernel_contract)),
        kernel_replay_sha256=_kernel_replay_digest(kernel),
        kernel_ledger_sha256=_canonical_json_digest(_ledger_json(kernel.ledger)),
        witness_binding_sha256=kernel.ledger.witness_binding_sha256,
        action_contract_sha256=_action_contract_digest(action_contract),
        action_output_bytes=action_output_bytes,
        action_output_sha256=action.nominal.raw_sha256,
        action_output_byte_length=len(action_output_bytes),
        action_block_count=action.block_count,
        action_scratch_payload_bytes=action.scratch_payload_bytes,
        science_executed=False,
        f0_pass=False,
    )
    validate_producer_action_artifact(artifact)
    return artifact


def _verify_action_artifact_owned(
    inputs: PackedKernelInputs,
    initial_payload: PackedIntervalPayload,
    kernel_contract: KernelBuildContract,
    action_contract: BlockActionContract,
    artifact: ProducerActionArtifact,
    authorization: _VerifierAuthorization,
) -> VerifierReplayReceipt:
    """Private verifier body entered only by the launcher-controlled spawn child."""

    if (
        type(authorization) is not _VerifierAuthorization
        or type(authorization.launch_parent_pid) is not int
        or authorization.launch_parent_pid < 1
        or authorization.launch_parent_pid == os.getpid()
        or type(authorization.capability) is not bytes
        or len(authorization.capability) != 32
        or not _is_hex_digest(authorization.request_sha256)
        or not _is_hex_digest(authorization.artifact_body_sha256)
    ):
        raise PackedF0Failure(HOLD_FRESH_PROCESS, "spawn verifier authorization is invalid")
    validate_producer_action_artifact(artifact)
    validate_kernel_inputs(inputs, kernel_contract)
    validate_packed_interval_payload(initial_payload)
    validate_block_action_contract(action_contract)
    if (
        initial_payload.manifest.role != "science_free_initial"
        or initial_payload.manifest.logical_shape != kernel_contract.tensor_shape
        or not initial_payload.manifest.nonnegative
    ):
        raise PackedF0Failure(HOLD_SCIENCE_BOUNDARY, "verifier initial source is invalid")
    actual_artifact_body = _artifact_body_digest(artifact)
    actual_request = _replay_request_digest(
        inputs,
        initial_payload,
        kernel_contract,
        action_contract,
        artifact,
    )
    if not hmac.compare_digest(
        actual_artifact_body, authorization.artifact_body_sha256
    ) or not hmac.compare_digest(actual_request, authorization.request_sha256):
        raise PackedF0Failure(HOLD_REPLAY, "spawn replay request binding changed")
    kernel = build_packed_tensor_kernel(inputs, kernel_contract)
    initial = interval_centres_as_vector(load_canonical_packed_intervals(initial_payload))
    action = block_p_transpose(kernel, initial, action_contract)
    comparisons = (
        (_kernel_inputs_digest(inputs, kernel_contract), artifact.kernel_inputs_sha256),
        (initial_payload.manifest.raw_sha256, artifact.initial_source_sha256),
        (_initial_manifest_digest(initial_payload), artifact.initial_manifest_sha256),
        (
            _canonical_json_digest(_contract_json(kernel_contract)),
            artifact.kernel_contract_sha256,
        ),
        (_kernel_replay_digest(kernel), artifact.kernel_replay_sha256),
        (
            _canonical_json_digest(_ledger_json(kernel.ledger)),
            artifact.kernel_ledger_sha256,
        ),
        (kernel.ledger.witness_binding_sha256, artifact.witness_binding_sha256),
        (_action_contract_digest(action_contract), artifact.action_contract_sha256),
        (action.nominal.raw_sha256, artifact.action_output_sha256),
    )
    if any(not hmac.compare_digest(actual, expected) for actual, expected in comparisons):
        raise PackedF0Failure(HOLD_REPLAY, "fresh verifier replay disagrees with producer bytes")
    verifier_output = memoryview(action.nominal.values).cast("B")
    comparison_block = max(FLOAT64_BYTES, action_contract.maximum_scratch_bytes)
    for start in range(0, len(artifact.action_output_bytes), comparison_block):
        stop = min(len(artifact.action_output_bytes), start + comparison_block)
        if not hmac.compare_digest(
            verifier_output[start:stop],
            artifact.action_output_bytes[start:stop],
        ):
            raise PackedF0Failure(HOLD_REPLAY, "fresh verifier raw output bytes disagree")
    if (
        action.nominal.values.nbytes != artifact.action_output_byte_length
        or action.block_count != artifact.action_block_count
        or action.scratch_payload_bytes != artifact.action_scratch_payload_bytes
    ):
        raise PackedF0Failure(HOLD_REPLAY, "fresh verifier resource ledger disagrees")
    receipt = VerifierReplayReceipt(
        schema=PACKED_REPLAY_SCHEMA,
        status="PASS_METHOD_REPLAY_ONLY_NOT_F0",
        producer_pid=authorization.launch_parent_pid,
        verifier_pid=os.getpid(),
        fresh_process=True,
        verifier_owned_replay=True,
        producer_arrays_accepted=False,
        launch_capability_sha256=_capability_digest(authorization.capability),
        request_sha256=authorization.request_sha256,
        artifact_body_sha256=authorization.artifact_body_sha256,
        initial_manifest_sha256=artifact.initial_manifest_sha256,
        witness_binding_sha256=artifact.witness_binding_sha256,
        kernel_replay_sha256=artifact.kernel_replay_sha256,
        action_output_sha256=artifact.action_output_sha256,
        science_executed=False,
        f0_pass=False,
    )
    validate_verifier_replay_receipt(receipt)
    return receipt


def _spawn_verifier_entry(
    send_connection: object,
    inputs: PackedKernelInputs,
    initial_payload: PackedIntervalPayload,
    kernel_contract: KernelBuildContract,
    action_contract: BlockActionContract,
    artifact: ProducerActionArtifact,
    authorization: _VerifierAuthorization,
) -> None:
    try:
        receipt = _verify_action_artifact_owned(
            inputs,
            initial_payload,
            kernel_contract,
            action_contract,
            artifact,
            authorization,
        )
    except PackedF0Failure as error:
        send_connection.send(("error", error.code, error.args[0]))
    else:
        send_connection.send(("ok", receipt))
    finally:
        send_connection.close()


def spawn_verify_action_artifact(
    inputs: PackedKernelInputs,
    initial_payload: PackedIntervalPayload,
    kernel_contract: KernelBuildContract,
    action_contract: BlockActionContract,
    artifact: ProducerActionArtifact,
) -> VerifierReplayReceipt:
    """Launch and attest one method-only replay in a controlled spawn child."""

    request_sha256 = _replay_request_digest(
        inputs,
        initial_payload,
        kernel_contract,
        action_contract,
        artifact,
    )
    artifact_body_sha256 = _artifact_body_digest(artifact)
    capability = os.urandom(32)
    authorization = _VerifierAuthorization(
        launch_parent_pid=os.getpid(),
        capability=capability,
        request_sha256=request_sha256,
        artifact_body_sha256=artifact_body_sha256,
    )
    context = multiprocessing.get_context("spawn")
    receive_connection, send_connection = context.Pipe(duplex=False)
    process = context.Process(
        target=_spawn_verifier_entry,
        args=(
            send_connection,
            inputs,
            initial_payload,
            kernel_contract,
            action_contract,
            artifact,
            authorization,
        ),
    )
    process.start()
    send_connection.close()
    launched_pid = process.pid
    process.join(timeout=SPAWN_REPLAY_TIMEOUT_SECONDS)
    if process.is_alive():
        process.terminate()
        process.join(timeout=5.0)
        receive_connection.close()
        raise PackedF0Failure(HOLD_FRESH_PROCESS, "spawn verifier exceeded its deadline")
    if process.exitcode != 0 or launched_pid is None or not receive_connection.poll(1.0):
        receive_connection.close()
        raise PackedF0Failure(HOLD_FRESH_PROCESS, "spawn verifier did not return a receipt")
    message = receive_connection.recv()
    receive_connection.close()
    if type(message) is not tuple or not message:
        raise PackedF0Failure(HOLD_REPLAY, "spawn verifier response is malformed")
    if message[0] == "error" and len(message) == 3:
        raise PackedF0Failure(message[1], message[2])
    if message[0] != "ok" or len(message) != 2:
        raise PackedF0Failure(HOLD_REPLAY, "spawn verifier response is malformed")
    receipt = message[1]
    validate_verifier_replay_receipt(receipt)
    if (
        receipt.producer_pid != os.getpid()
        or receipt.verifier_pid != launched_pid
        or not hmac.compare_digest(
            receipt.launch_capability_sha256,
            _capability_digest(capability),
        )
        or not hmac.compare_digest(receipt.request_sha256, request_sha256)
        or not hmac.compare_digest(receipt.artifact_body_sha256, artifact_body_sha256)
    ):
        raise PackedF0Failure(HOLD_FRESH_PROCESS, "spawn receipt provenance disagrees")
    return receipt


def verify_action_artifact_fresh_process(
    inputs: PackedKernelInputs,
    initial_payload: PackedIntervalPayload,
    kernel_contract: KernelBuildContract,
    action_contract: BlockActionContract,
    artifact: ProducerActionArtifact,
) -> VerifierReplayReceipt:
    """Fail closed: public callers must use :func:`spawn_verify_action_artifact`."""

    del inputs, initial_payload, kernel_contract, action_contract, artifact
    raise PackedF0Failure(
        HOLD_FRESH_PROCESS,
        "direct verifier calls are forbidden; use the launcher-controlled spawn API",
    )


def validate_verifier_replay_receipt(receipt: VerifierReplayReceipt) -> None:
    if type(receipt) is not VerifierReplayReceipt:
        raise PackedF0Failure(HOLD_PACKED_NESTED_TYPE, "verifier receipt has wrong exact type")
    if (
        type(receipt.schema) is not str
        or receipt.schema != PACKED_REPLAY_SCHEMA
        or type(receipt.status) is not str
        or receipt.status != "PASS_METHOD_REPLAY_ONLY_NOT_F0"
        or type(receipt.producer_pid) is not int
        or type(receipt.verifier_pid) is not int
        or receipt.producer_pid == receipt.verifier_pid
        or type(receipt.fresh_process) is not bool
        or receipt.fresh_process is not True
        or type(receipt.verifier_owned_replay) is not bool
        or receipt.verifier_owned_replay is not True
        or type(receipt.producer_arrays_accepted) is not bool
        or receipt.producer_arrays_accepted is not False
        or not _is_hex_digest(receipt.launch_capability_sha256)
        or not _is_hex_digest(receipt.request_sha256)
        or not _is_hex_digest(receipt.artifact_body_sha256)
        or not _is_hex_digest(receipt.initial_manifest_sha256)
        or not _is_hex_digest(receipt.witness_binding_sha256)
        or not _is_hex_digest(receipt.kernel_replay_sha256)
        or not _is_hex_digest(receipt.action_output_sha256)
        or type(receipt.science_executed) is not bool
        or receipt.science_executed is not False
        or type(receipt.f0_pass) is not bool
        or receipt.f0_pass is not False
    ):
        raise PackedF0Failure(HOLD_REPLAY, "verifier receipt schema is invalid")
