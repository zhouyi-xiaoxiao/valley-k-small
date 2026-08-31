"""Directed-roundoff interval actions for the science-free packed F0 backend.

This bounded stage encloses the centre-kernel ``P.T`` and ``Q.T`` actions from
``rate_defined_tensor_f0_packed``.  It deliberately does not implement
uniformization, time jets, topology, a separate verifier, F1, or any scientific
control.  The accepted input is one canonical, owned, native-binary64 interval
buffer and the output is another owned, native-binary64 interval buffer.

Every real multiplication is performed in binary64 round-to-nearest and then
widened by one ``nextafter`` toward the relevant infinity.  Every real addition
is widened in the same way.  The addition order is exactly the frozen stage-1
block/halo order: self, then forward incoming and backward incoming for each
axis in increasing dimension order.  Existing reflecting halo terms are set to
exact zero before their (still ordered) addition.
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

DIRECTED_ACTION_SCHEMA: Final = "rate_defined_tensor_f0_packed_directed_action_v2"
DIRECTED_RESULT_SCHEMA: Final = "rate_defined_tensor_f0_packed_directed_result_v2"
DIRECTED_MEMORY_SCHEMA: Final = "rate_defined_tensor_f0_packed_directed_memory_v2"
DIRECTED_BACKEND: Final = "numpy_binary64_nextafter_block_halo_interval_v2"
ROUNDING_PRIMITIVE: Final = "rn_then_one_nextafter_per_real_multiply_and_add_v1"
OUTPUT_BYTES_PER_STATE: Final = 16
WORKSPACE_BYTES_PER_BLOCK_STATE: Final = 81
VALIDATION_BYTES_PER_BLOCK_STATE: Final = 2
VECTORIZED_ROUNDING_PROBE_LENGTHS: Final = (16, 24, 64)
VECTORIZED_ROUNDING_PROBE_ARRAY_COUNT: Final = 4
VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES: Final = (
    VECTORIZED_ROUNDING_PROBE_ARRAY_COUNT
    * np.dtype(np.float64).itemsize
    * max(VECTORIZED_ROUNDING_PROBE_LENGTHS)
)
MAXIMUM_DIMENSIONS: Final = 3
HOLD_DIRECTED_SCHEMA: Final = "HOLD_F0_PACKED_DIRECTED_SCHEMA_INVALID"
HOLD_DIRECTED_BINDING: Final = "HOLD_F0_PACKED_DIRECTED_BACKEND_BINDING"
HOLD_DIRECTED_ARRAY: Final = "HOLD_F0_PACKED_DIRECTED_ARRAY_NONCANONICAL"
HOLD_DIRECTED_ACTION: Final = "HOLD_F0_PACKED_DIRECTED_ACTION_INVALID"
HOLD_DIRECTED_RESOURCE: Final = "HOLD_F0_PACKED_DIRECTED_RESOURCE_CAP_EXCEEDED"

_NEGATIVE_INFINITY: Final = np.float64(-math.inf)
_POSITIVE_INFINITY: Final = np.float64(math.inf)
_OPERATION_MODEL: Final = (
    "runtime-probes-scalar-and-contiguous-vectorized-binary64-rn-even-gradual-underflow",
    "centre-coefficients-are-exact-binary64-points",
    "nonnegative-coefficient-product-uses-input-lower-then-input-upper",
    "nonpositive-self-q-product-uses-input-upper-then-input-lower",
    "each-product-is-rn-then-nextafter-negative-or-positive-infinity",
    "reflecting-missing-incoming-term-is-exact-zero-before-addition",
    "each-addition-is-rn-then-nextafter-negative-or-positive-infinity",
    "addition-order-is-frozen-stage1-summation-order",
    "nonfinite-or-reversed-output-fails-closed",
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


def _source_sha256(path: str) -> str:
    return _sha256(Path(path).read_bytes())


def _is_hex_digest(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _operation_model_sha256() -> str:
    return _canonical_json_digest(list(_OPERATION_MODEL))


def _runtime_identity() -> str:
    return (
        f"python-{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        f"|numpy-{np.__version__}|machine-{platform.machine()}"
    )


def _fraction_contains(
    lower: float,
    exact: Fraction,
    upper: float,
) -> bool:
    return Fraction.from_float(lower) <= exact <= Fraction.from_float(upper)


def _validate_vectorized_rounding_length(length: int) -> None:
    minimum_subnormal = float(np.nextafter(np.float64(0.0), np.float64(1.0)))
    one = float(np.float64(1.0))
    next_one = float(np.nextafter(np.float64(1.0), _POSITIVE_INFINITY))
    half_ulp = float(np.float64(2.0**-53))
    three_quarter_ulp = float(np.float64(3.0 * 2.0**-54))
    left = np.empty(length, dtype=np.float64)
    right = np.empty(length, dtype=np.float64)
    rounded = np.empty(length, dtype=np.float64)
    bound = np.empty(length, dtype=np.float64)
    arrays = (left, right, rounded, bound)
    if any(
        type(array) is not np.ndarray
        or not array.flags.c_contiguous
        or not array.flags.owndata
        or array.base is not None
        for array in arrays
    ):
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_BINDING,
            "vectorized rounding probe arrays are not contiguous and owned",
        )
    if sum(array.nbytes for array in arrays) != 32 * length:
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_RESOURCE,
            "vectorized rounding probe payload changed",
        )

    multiply_patterns = (
        (minimum_subnormal, one),
        (-minimum_subnormal, one),
        (minimum_subnormal, 0.5),
        (-minimum_subnormal, 0.5),
        (next_one, next_one),
        (-next_one, next_one),
    )
    for index in range(length):
        left[index], right[index] = multiply_patterns[index % len(multiply_patterns)]
    np.multiply(left, right, out=rounded)
    if (
        rounded[0] != minimum_subnormal
        or rounded[1] != -minimum_subnormal
        or rounded[2] != 0.0
        or math.copysign(1.0, float(rounded[2])) < 0.0
        or rounded[3] != 0.0
        or math.copysign(1.0, float(rounded[3])) > 0.0
    ):
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_BINDING,
            "vectorized multiplication lost gradual signed underflow",
        )
    np.nextafter(rounded, _NEGATIVE_INFINITY, out=bound)
    for index in range(length):
        exact = Fraction.from_float(float(left[index])) * Fraction.from_float(float(right[index]))
        if Fraction.from_float(float(bound[index])) > exact:
            raise packed.PackedF0Failure(
                HOLD_DIRECTED_BINDING,
                "vectorized product lower nextafter is not outward",
            )
    np.nextafter(rounded, _POSITIVE_INFINITY, out=bound)
    for index in range(length):
        exact = Fraction.from_float(float(left[index])) * Fraction.from_float(float(right[index]))
        if Fraction.from_float(float(bound[index])) < exact:
            raise packed.PackedF0Failure(
                HOLD_DIRECTED_BINDING,
                "vectorized product upper nextafter is not outward",
            )

    add_patterns = (
        (one, half_ulp),
        (-one, -half_ulp),
        (one, three_quarter_ulp),
        (minimum_subnormal, 0.0),
        (-minimum_subnormal, 0.0),
        (one, -half_ulp),
    )
    for index in range(length):
        left[index], right[index] = add_patterns[index % len(add_patterns)]
    np.add(left, right, out=rounded)
    if (
        rounded[0] != one
        or rounded[1] != -one
        or rounded[2] != next_one
        or rounded[3] != minimum_subnormal
        or rounded[4] != -minimum_subnormal
    ):
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_BINDING,
            "vectorized addition is not binary64 RN-even with gradual underflow",
        )
    np.nextafter(rounded, _NEGATIVE_INFINITY, out=bound)
    lower_bounds = tuple(float(value) for value in bound)
    np.nextafter(rounded, _POSITIVE_INFINITY, out=bound)
    for index in range(length):
        exact = Fraction.from_float(float(left[index])) + Fraction.from_float(float(right[index]))
        if not _fraction_contains(lower_bounds[index], exact, float(bound[index])):
            raise packed.PackedF0Failure(
                HOLD_DIRECTED_BINDING,
                "vectorized addition nextafter bounds are not outward",
            )


def _validate_binary64_rounding_environment() -> None:
    one = np.float64(1.0)
    minus_one = np.float64(-1.0)
    half_ulp = np.float64(2.0**-53)
    three_quarter_ulp = np.float64(3.0 * 2.0**-54)
    next_one = np.nextafter(one, _POSITIVE_INFINITY)
    minimum_subnormal = np.nextafter(np.float64(0.0), np.float64(1.0))
    if (
        np.dtype(np.float64).itemsize != 8
        or np.finfo(np.float64).nmant != 52
        or np.add(one, half_ulp) != one
        or np.add(minus_one, -half_ulp) != minus_one
        or np.add(one, three_quarter_ulp) != next_one
        or minimum_subnormal == 0.0
        or np.multiply(minimum_subnormal, one) != minimum_subnormal
        or np.add(minimum_subnormal, np.float64(0.0)) != minimum_subnormal
    ):
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_BINDING,
            "runtime is not binary64 round-to-nearest-even with gradual underflow",
        )
    for length in VECTORIZED_ROUNDING_PROBE_LENGTHS:
        _validate_vectorized_rounding_length(length)


def _stage1_source_sha256() -> str:
    return _source_sha256(packed.__file__)


def _directed_source_sha256() -> str:
    return _source_sha256(__file__)


def _expected_order(shape: tuple[int, ...]) -> tuple[str, ...]:
    return ("self",) + tuple(
        role
        for dimension in range(len(shape))
        for role in (
            f"axis_{dimension}_forward_incoming",
            f"axis_{dimension}_backward_incoming",
        )
    )


def _require_shape(value: object) -> tuple[int, ...]:
    if (
        type(value) is not tuple
        or not value
        or len(value) > MAXIMUM_DIMENSIONS
        or any(type(entry) is not int or entry < 2 for entry in value)
    ):
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "tensor shape is invalid")
    return value


def _raw_sha256(array: np.ndarray) -> str:
    return _sha256(memoryview(array).cast("B"))


def _require_owned_readonly_intervals(
    array: object,
    *,
    states: int,
) -> np.ndarray:
    if type(array) is not np.ndarray:
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_ARRAY,
            "directed interval buffer must have exact numpy.ndarray type",
        )
    if (
        array.dtype != np.dtype(np.float64)
        or not array.dtype.isnative
        or array.shape != (states, 2)
        or not array.flags.c_contiguous
        or not array.flags.aligned
        or not array.flags.owndata
        or array.base is not None
        or array.flags.writeable
    ):
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_ARRAY,
            "directed interval buffer is not owned native readonly binary64",
        )
    return array


@dataclass(frozen=True, slots=True)
class DirectedActionContract:
    schema: str
    tensor_shape: tuple[int, ...]
    block_size: int
    maximum_scratch_bytes: int
    output_payload_bytes: int
    workspace_payload_bytes: int
    validation_scratch_payload_bytes: int
    runtime_probe_payload_bytes: int
    vectorized_rounding_probe_lengths: tuple[int, ...]
    summation_order: tuple[str, ...]
    backend: str
    rounding_primitive: str
    operation_model_sha256: str
    runtime: str
    stage1_kernel_construction: str
    stage1_kernel_backend: str
    stage1_action_backend: str
    stage1_source_sha256: str
    directed_source_sha256: str
    stage1_action_contract_sha256: str
    backend_binding_sha256: str
    single_threaded: bool
    science_free: bool
    directed_roundoff_stage_complete: bool


@dataclass(frozen=True, slots=True)
class DirectedMemoryLedger:
    schema: str
    state_count: int
    block_size: int
    block_capacity: int
    output_bytes_per_state: int
    workspace_bytes_per_block_state: int
    validation_bytes_per_block_state: int
    output_payload_bytes: int
    workspace_payload_bytes: int
    validation_scratch_payload_bytes: int
    runtime_probe_payload_bytes: int
    maximum_new_numeric_payload_bytes: int
    preowned_kernel_and_input_excluded: bool


@dataclass(frozen=True, slots=True)
class CanonicalDirectedIntervals:
    logical_shape: tuple[int, ...]
    intervals: np.ndarray
    raw_sha256: str
    input_raw_sha256: str
    exact_action_nonnegative: bool


@dataclass(frozen=True, slots=True)
class DirectedActionResult:
    schema: str
    operator: str
    enclosure: CanonicalDirectedIntervals
    input_raw_sha256: str
    kernel_replay_sha256: str
    action_contract_sha256: str
    backend_binding_sha256: str
    block_count: int
    multiplication_count_per_state: int
    addition_count_per_state: int
    memory: DirectedMemoryLedger
    consistency_sha256: str
    science_executed: bool
    f0_pass: bool


def _stage1_action_contract_sha256(
    shape: tuple[int, ...],
    *,
    block_size: int,
    maximum_scratch_bytes: int,
) -> str:
    stage1_contract = packed.make_block_action_contract(
        shape,
        block_size=block_size,
        maximum_scratch_bytes=maximum_scratch_bytes,
    )
    return packed._action_contract_digest(stage1_contract)


def _backend_binding_payload(
    *,
    shape: tuple[int, ...],
    block_size: int,
    maximum_scratch_bytes: int,
    stage1_source_sha256: str,
    directed_source_sha256: str,
    stage1_action_contract_sha256: str,
) -> dict[str, object]:
    return {
        "backend": DIRECTED_BACKEND,
        "block_size": block_size,
        "directed_source_sha256": directed_source_sha256,
        "maximum_scratch_bytes": maximum_scratch_bytes,
        "operation_model_sha256": _operation_model_sha256(),
        "rounding_primitive": ROUNDING_PRIMITIVE,
        "runtime": _runtime_identity(),
        "runtime_probe_payload_bytes": VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES,
        "stage1_action_backend": packed.ACTION_BACKEND,
        "stage1_action_contract_sha256": stage1_action_contract_sha256,
        "stage1_kernel_backend": packed.STREAMING_BACKEND,
        "stage1_kernel_construction": packed.KERNEL_CONSTRUCTION,
        "stage1_source_sha256": stage1_source_sha256,
        "summation_order": list(_expected_order(shape)),
        "tensor_shape": list(shape),
        "vectorized_rounding_probe_lengths": list(VECTORIZED_ROUNDING_PROBE_LENGTHS),
    }


def make_directed_action_contract(
    tensor_shape: tuple[int, ...],
    *,
    block_size: int,
    maximum_scratch_bytes: int,
) -> DirectedActionContract:
    """Bind a directed action to one shape, block size, and backend byte set."""

    _validate_binary64_rounding_environment()
    shape = _require_shape(tensor_shape)
    if type(block_size) is not int or block_size < 1:
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "block size is invalid")
    if type(maximum_scratch_bytes) is not int:
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "scratch cap is invalid")
    states = math.prod(shape)
    capacity = min(states, block_size)
    workspace = WORKSPACE_BYTES_PER_BLOCK_STATE * capacity
    if maximum_scratch_bytes < workspace:
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_RESOURCE,
            "scratch cap is smaller than the fixed directed workspace",
        )
    stage1_source = _stage1_source_sha256()
    directed_source = _directed_source_sha256()
    stage1_contract = _stage1_action_contract_sha256(
        shape,
        block_size=block_size,
        maximum_scratch_bytes=maximum_scratch_bytes,
    )
    binding = _canonical_json_digest(
        _backend_binding_payload(
            shape=shape,
            block_size=block_size,
            maximum_scratch_bytes=maximum_scratch_bytes,
            stage1_source_sha256=stage1_source,
            directed_source_sha256=directed_source,
            stage1_action_contract_sha256=stage1_contract,
        )
    )
    contract = DirectedActionContract(
        schema=DIRECTED_ACTION_SCHEMA,
        tensor_shape=shape,
        block_size=block_size,
        maximum_scratch_bytes=maximum_scratch_bytes,
        output_payload_bytes=OUTPUT_BYTES_PER_STATE * states,
        workspace_payload_bytes=workspace,
        validation_scratch_payload_bytes=VALIDATION_BYTES_PER_BLOCK_STATE * capacity,
        runtime_probe_payload_bytes=VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES,
        vectorized_rounding_probe_lengths=VECTORIZED_ROUNDING_PROBE_LENGTHS,
        summation_order=_expected_order(shape),
        backend=DIRECTED_BACKEND,
        rounding_primitive=ROUNDING_PRIMITIVE,
        operation_model_sha256=_operation_model_sha256(),
        runtime=_runtime_identity(),
        stage1_kernel_construction=packed.KERNEL_CONSTRUCTION,
        stage1_kernel_backend=packed.STREAMING_BACKEND,
        stage1_action_backend=packed.ACTION_BACKEND,
        stage1_source_sha256=stage1_source,
        directed_source_sha256=directed_source,
        stage1_action_contract_sha256=stage1_contract,
        backend_binding_sha256=binding,
        single_threaded=True,
        science_free=True,
        directed_roundoff_stage_complete=True,
    )
    validate_directed_action_contract(contract)
    return contract


def validate_directed_action_contract(contract: DirectedActionContract) -> None:
    _validate_binary64_rounding_environment()
    if type(contract) is not DirectedActionContract:
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "contract has wrong exact type")
    shape = _require_shape(contract.tensor_shape)
    states = math.prod(shape)
    if type(contract.block_size) is not int or contract.block_size < 1:
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "contract block size is invalid")
    capacity = min(states, contract.block_size)
    workspace = WORKSPACE_BYTES_PER_BLOCK_STATE * capacity
    validation = VALIDATION_BYTES_PER_BLOCK_STATE * capacity
    if (
        type(contract.schema) is not str
        or contract.schema != DIRECTED_ACTION_SCHEMA
        or type(contract.maximum_scratch_bytes) is not int
        or contract.maximum_scratch_bytes < workspace
        or type(contract.output_payload_bytes) is not int
        or contract.output_payload_bytes != OUTPUT_BYTES_PER_STATE * states
        or type(contract.workspace_payload_bytes) is not int
        or contract.workspace_payload_bytes != workspace
        or type(contract.validation_scratch_payload_bytes) is not int
        or contract.validation_scratch_payload_bytes != validation
        or type(contract.runtime_probe_payload_bytes) is not int
        or contract.runtime_probe_payload_bytes != VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES
        or type(contract.vectorized_rounding_probe_lengths) is not tuple
        or contract.vectorized_rounding_probe_lengths != VECTORIZED_ROUNDING_PROBE_LENGTHS
        or any(type(entry) is not int for entry in contract.vectorized_rounding_probe_lengths)
        or type(contract.summation_order) is not tuple
        or contract.summation_order != _expected_order(shape)
        or any(type(entry) is not str for entry in contract.summation_order)
        or type(contract.backend) is not str
        or contract.backend != DIRECTED_BACKEND
        or type(contract.rounding_primitive) is not str
        or contract.rounding_primitive != ROUNDING_PRIMITIVE
        or not _is_hex_digest(contract.operation_model_sha256)
        or contract.operation_model_sha256 != _operation_model_sha256()
        or type(contract.runtime) is not str
        or contract.runtime != _runtime_identity()
        or type(contract.stage1_kernel_construction) is not str
        or contract.stage1_kernel_construction != packed.KERNEL_CONSTRUCTION
        or type(contract.stage1_kernel_backend) is not str
        or contract.stage1_kernel_backend != packed.STREAMING_BACKEND
        or type(contract.stage1_action_backend) is not str
        or contract.stage1_action_backend != packed.ACTION_BACKEND
        or not _is_hex_digest(contract.stage1_source_sha256)
        or not _is_hex_digest(contract.directed_source_sha256)
        or not _is_hex_digest(contract.stage1_action_contract_sha256)
        or not _is_hex_digest(contract.backend_binding_sha256)
        or type(contract.single_threaded) is not bool
        or contract.single_threaded is not True
        or type(contract.science_free) is not bool
        or contract.science_free is not True
        or type(contract.directed_roundoff_stage_complete) is not bool
        or contract.directed_roundoff_stage_complete is not True
    ):
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "directed contract is inconsistent")
    current_stage1_source = _stage1_source_sha256()
    current_directed_source = _directed_source_sha256()
    expected_stage1_contract = _stage1_action_contract_sha256(
        shape,
        block_size=contract.block_size,
        maximum_scratch_bytes=contract.maximum_scratch_bytes,
    )
    expected_binding = _canonical_json_digest(
        _backend_binding_payload(
            shape=shape,
            block_size=contract.block_size,
            maximum_scratch_bytes=contract.maximum_scratch_bytes,
            stage1_source_sha256=current_stage1_source,
            directed_source_sha256=current_directed_source,
            stage1_action_contract_sha256=expected_stage1_contract,
        )
    )
    if (
        not hmac.compare_digest(contract.stage1_source_sha256, current_stage1_source)
        or not hmac.compare_digest(contract.directed_source_sha256, current_directed_source)
        or not hmac.compare_digest(
            contract.stage1_action_contract_sha256,
            expected_stage1_contract,
        )
        or not hmac.compare_digest(contract.backend_binding_sha256, expected_binding)
    ):
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_BINDING,
            "contract is not bound to the current stage1/directed backend bytes",
        )


def _contract_json(contract: DirectedActionContract) -> dict[str, object]:
    validate_directed_action_contract(contract)
    return {
        "backend": contract.backend,
        "backend_binding_sha256": contract.backend_binding_sha256,
        "block_size": contract.block_size,
        "directed_roundoff_stage_complete": contract.directed_roundoff_stage_complete,
        "directed_source_sha256": contract.directed_source_sha256,
        "maximum_scratch_bytes": contract.maximum_scratch_bytes,
        "operation_model_sha256": contract.operation_model_sha256,
        "output_payload_bytes": contract.output_payload_bytes,
        "rounding_primitive": contract.rounding_primitive,
        "runtime_probe_payload_bytes": contract.runtime_probe_payload_bytes,
        "runtime": contract.runtime,
        "schema": contract.schema,
        "science_free": contract.science_free,
        "single_threaded": contract.single_threaded,
        "stage1_action_backend": contract.stage1_action_backend,
        "stage1_action_contract_sha256": contract.stage1_action_contract_sha256,
        "stage1_kernel_backend": contract.stage1_kernel_backend,
        "stage1_kernel_construction": contract.stage1_kernel_construction,
        "stage1_source_sha256": contract.stage1_source_sha256,
        "summation_order": list(contract.summation_order),
        "tensor_shape": list(contract.tensor_shape),
        "validation_scratch_payload_bytes": contract.validation_scratch_payload_bytes,
        "vectorized_rounding_probe_lengths": list(contract.vectorized_rounding_probe_lengths),
        "workspace_payload_bytes": contract.workspace_payload_bytes,
    }


def directed_action_contract_sha256(contract: DirectedActionContract) -> str:
    return _canonical_json_digest(_contract_json(contract))


def _memory_ledger(contract: DirectedActionContract) -> DirectedMemoryLedger:
    validate_directed_action_contract(contract)
    states = math.prod(contract.tensor_shape)
    capacity = min(states, contract.block_size)
    ledger = DirectedMemoryLedger(
        schema=DIRECTED_MEMORY_SCHEMA,
        state_count=states,
        block_size=contract.block_size,
        block_capacity=capacity,
        output_bytes_per_state=OUTPUT_BYTES_PER_STATE,
        workspace_bytes_per_block_state=WORKSPACE_BYTES_PER_BLOCK_STATE,
        validation_bytes_per_block_state=VALIDATION_BYTES_PER_BLOCK_STATE,
        output_payload_bytes=contract.output_payload_bytes,
        workspace_payload_bytes=contract.workspace_payload_bytes,
        validation_scratch_payload_bytes=contract.validation_scratch_payload_bytes,
        runtime_probe_payload_bytes=contract.runtime_probe_payload_bytes,
        maximum_new_numeric_payload_bytes=contract.output_payload_bytes
        + max(
            contract.workspace_payload_bytes,
            contract.validation_scratch_payload_bytes,
            contract.runtime_probe_payload_bytes,
        ),
        preowned_kernel_and_input_excluded=True,
    )
    validate_directed_memory_ledger(ledger)
    return ledger


def validate_directed_memory_ledger(ledger: DirectedMemoryLedger) -> None:
    if type(ledger) is not DirectedMemoryLedger:
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "memory ledger has wrong exact type")
    if (
        type(ledger.schema) is not str
        or ledger.schema != DIRECTED_MEMORY_SCHEMA
        or type(ledger.state_count) is not int
        or ledger.state_count < 1
        or type(ledger.block_size) is not int
        or ledger.block_size < 1
        or type(ledger.block_capacity) is not int
        or ledger.block_capacity != min(ledger.state_count, ledger.block_size)
        or type(ledger.output_bytes_per_state) is not int
        or ledger.output_bytes_per_state != OUTPUT_BYTES_PER_STATE
        or type(ledger.workspace_bytes_per_block_state) is not int
        or ledger.workspace_bytes_per_block_state != WORKSPACE_BYTES_PER_BLOCK_STATE
        or type(ledger.validation_bytes_per_block_state) is not int
        or ledger.validation_bytes_per_block_state != VALIDATION_BYTES_PER_BLOCK_STATE
        or type(ledger.output_payload_bytes) is not int
        or ledger.output_payload_bytes != OUTPUT_BYTES_PER_STATE * ledger.state_count
        or type(ledger.workspace_payload_bytes) is not int
        or ledger.workspace_payload_bytes != WORKSPACE_BYTES_PER_BLOCK_STATE * ledger.block_capacity
        or type(ledger.validation_scratch_payload_bytes) is not int
        or ledger.validation_scratch_payload_bytes
        != VALIDATION_BYTES_PER_BLOCK_STATE * ledger.block_capacity
        or type(ledger.runtime_probe_payload_bytes) is not int
        or ledger.runtime_probe_payload_bytes != VECTORIZED_ROUNDING_PROBE_PAYLOAD_BYTES
        or type(ledger.maximum_new_numeric_payload_bytes) is not int
        or ledger.maximum_new_numeric_payload_bytes
        != ledger.output_payload_bytes
        + max(
            ledger.workspace_payload_bytes,
            ledger.validation_scratch_payload_bytes,
            ledger.runtime_probe_payload_bytes,
        )
        or type(ledger.preowned_kernel_and_input_excluded) is not bool
        or ledger.preowned_kernel_and_input_excluded is not True
    ):
        raise packed.PackedF0Failure(HOLD_DIRECTED_RESOURCE, "memory ledger is inconsistent")


def _memory_json(ledger: DirectedMemoryLedger) -> dict[str, object]:
    validate_directed_memory_ledger(ledger)
    return {
        "block_capacity": ledger.block_capacity,
        "block_size": ledger.block_size,
        "maximum_new_numeric_payload_bytes": ledger.maximum_new_numeric_payload_bytes,
        "output_bytes_per_state": ledger.output_bytes_per_state,
        "output_payload_bytes": ledger.output_payload_bytes,
        "preowned_kernel_and_input_excluded": ledger.preowned_kernel_and_input_excluded,
        "runtime_probe_payload_bytes": ledger.runtime_probe_payload_bytes,
        "schema": ledger.schema,
        "state_count": ledger.state_count,
        "validation_bytes_per_block_state": ledger.validation_bytes_per_block_state,
        "validation_scratch_payload_bytes": ledger.validation_scratch_payload_bytes,
        "workspace_bytes_per_block_state": ledger.workspace_bytes_per_block_state,
        "workspace_payload_bytes": ledger.workspace_payload_bytes,
    }


def _result_consistency_sha256(result: DirectedActionResult) -> str:
    """Hash result relationships; this is consistency metadata, not authentication."""

    return _canonical_json_digest(
        {
            "action_contract_sha256": result.action_contract_sha256,
            "addition_count_per_state": result.addition_count_per_state,
            "backend_binding_sha256": result.backend_binding_sha256,
            "block_count": result.block_count,
            "enclosure": {
                "exact_action_nonnegative": result.enclosure.exact_action_nonnegative,
                "input_raw_sha256": result.enclosure.input_raw_sha256,
                "logical_shape": list(result.enclosure.logical_shape),
                "raw_sha256": result.enclosure.raw_sha256,
            },
            "f0_pass": result.f0_pass,
            "input_raw_sha256": result.input_raw_sha256,
            "kernel_replay_sha256": result.kernel_replay_sha256,
            "memory": _memory_json(result.memory),
            "multiplication_count_per_state": result.multiplication_count_per_state,
            "operator": result.operator,
            "schema": result.schema,
            "science_executed": result.science_executed,
        }
    )


def validate_canonical_directed_intervals(
    enclosure: CanonicalDirectedIntervals,
    *,
    block_size: int,
) -> None:
    if type(enclosure) is not CanonicalDirectedIntervals:
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "enclosure has wrong exact type")
    shape = _require_shape(enclosure.logical_shape)
    if (
        type(block_size) is not int
        or block_size < 1
        or not _is_hex_digest(enclosure.raw_sha256)
        or not _is_hex_digest(enclosure.input_raw_sha256)
        or type(enclosure.exact_action_nonnegative) is not bool
    ):
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "enclosure metadata is invalid")
    intervals = _require_owned_readonly_intervals(enclosure.intervals, states=math.prod(shape))
    before = _raw_sha256(intervals)
    if not hmac.compare_digest(before, enclosure.raw_sha256):
        raise packed.PackedF0Failure(HOLD_DIRECTED_BINDING, "enclosure raw hash changed")
    capacity = min(intervals.shape[0], block_size)
    scratch = np.empty((2, capacity), dtype=np.bool_)
    for start in range(0, intervals.shape[0], block_size):
        stop = min(intervals.shape[0], start + block_size)
        count = stop - start
        block = intervals[start:stop]
        first = scratch[0, :count]
        invalid = False
        for endpoint in range(2):
            np.isfinite(block[:, endpoint], out=first)
            invalid = invalid or not bool(np.all(first))
        np.greater(block[:, 0], block[:, 1], out=first)
        invalid = invalid or bool(np.any(first))
        if invalid:
            raise packed.PackedF0Failure(
                HOLD_DIRECTED_ACTION,
                "directed enclosure contains nonfinite or reversed endpoints",
            )
    if not hmac.compare_digest(before, _raw_sha256(intervals)):
        raise packed.PackedF0Failure(HOLD_DIRECTED_BINDING, "enclosure changed during validation")


def _round_down(array: np.ndarray) -> None:
    np.nextafter(array, _NEGATIVE_INFINITY, out=array)


def _round_up(array: np.ndarray) -> None:
    np.nextafter(array, _POSITIVE_INFINITY, out=array)


def _add_outward(
    accumulator_lower: np.ndarray,
    accumulator_upper: np.ndarray,
    term_lower: np.ndarray,
    term_upper: np.ndarray,
) -> None:
    np.add(accumulator_lower, term_lower, out=accumulator_lower)
    _round_down(accumulator_lower)
    np.add(accumulator_upper, term_upper, out=accumulator_upper)
    _round_up(accumulator_upper)


def _directed_transpose_action(
    kernel: packed.PackedTensorKernel,
    vector: packed.CanonicalPackedIntervals,
    contract: DirectedActionContract,
    *,
    operator: str,
) -> DirectedActionResult:
    packed.validate_packed_tensor_kernel(kernel)
    packed.validate_canonical_packed_intervals(vector)
    validate_directed_action_contract(contract)
    if (
        type(operator) is not str
        or operator not in {"P", "Q"}
        or vector.manifest.logical_shape != kernel.contract.tensor_shape
        or contract.tensor_shape != kernel.contract.tensor_shape
        or contract.block_size != kernel.contract.block_size
        or vector.manifest.block_size != contract.block_size
    ):
        raise packed.PackedF0Failure(HOLD_DIRECTED_ACTION, "action inputs disagree")
    if operator == "P" and not vector.manifest.nonnegative:
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_ACTION,
            "P.T interval action requires a nonnegative input enclosure",
        )

    input_raw_sha256 = vector.manifest.raw_sha256
    kernel_replay_sha256 = packed._kernel_replay_digest(kernel)
    contract_sha256 = directed_action_contract_sha256(contract)
    states = kernel.states
    capacity = min(states, contract.block_size)

    base = np.arange(capacity, dtype=np.int64)
    flat = np.empty(capacity, dtype=np.int64)
    coordinate = np.empty(capacity, dtype=np.int64)
    source_index = np.empty(capacity, dtype=np.int64)
    rate_index = np.empty(capacity, dtype=np.int64)
    mask = np.empty(capacity, dtype=np.bool_)
    accumulator_lower = np.empty(capacity, dtype=np.float64)
    accumulator_upper = np.empty(capacity, dtype=np.float64)
    term_lower = np.empty(capacity, dtype=np.float64)
    term_upper = np.empty(capacity, dtype=np.float64)
    coefficient = np.empty(capacity, dtype=np.float64)
    output = np.empty((states, 2), dtype=np.float64, order="C")
    actual_workspace_payload_bytes = sum(
        array.nbytes
        for array in (
            base,
            flat,
            coordinate,
            source_index,
            rate_index,
            mask,
            accumulator_lower,
            accumulator_upper,
            term_lower,
            term_upper,
            coefficient,
        )
    )
    if (
        actual_workspace_payload_bytes != contract.workspace_payload_bytes
        or output.nbytes != contract.output_payload_bytes
    ):
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_RESOURCE,
            "actual NumPy payload disagrees with the fixed memory ledger",
        )

    values = vector.intervals
    self_values = kernel.p_self_center if operator == "P" else kernel.diagonal_center
    forward_values = kernel.p_forward_center if operator == "P" else kernel.forward_center
    backward_values = kernel.p_backward_center if operator == "P" else kernel.backward_center
    strides = packed._axis_strides(kernel.contract.tensor_shape)

    block_count = 0
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        for start in range(0, states, contract.block_size):
            stop = min(states, start + contract.block_size)
            count = stop - start
            block_count += 1
            np.add(base[:count], start, out=flat[:count])

            if operator == "P":
                np.less(self_values[start:stop], 0.0, out=mask[:count])
                if bool(np.any(mask[:count])):
                    raise packed.PackedF0Failure(
                        HOLD_DIRECTED_ACTION,
                        "P self coefficient lost nonnegativity",
                    )
                np.multiply(
                    values[start:stop, 0],
                    self_values[start:stop],
                    out=accumulator_lower[:count],
                )
                _round_down(accumulator_lower[:count])
                np.multiply(
                    values[start:stop, 1],
                    self_values[start:stop],
                    out=accumulator_upper[:count],
                )
                _round_up(accumulator_upper[:count])
            else:
                # Q diagonal coefficients are nonpositive, so endpoint roles reverse.
                np.greater(self_values[start:stop], 0.0, out=mask[:count])
                if bool(np.any(mask[:count])):
                    raise packed.PackedF0Failure(
                        HOLD_DIRECTED_ACTION,
                        "Q self coefficient lost nonpositivity",
                    )
                np.multiply(
                    values[start:stop, 1],
                    self_values[start:stop],
                    out=accumulator_lower[:count],
                )
                _round_down(accumulator_lower[:count])
                np.multiply(
                    values[start:stop, 0],
                    self_values[start:stop],
                    out=accumulator_upper[:count],
                )
                _round_up(accumulator_upper[:count])

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
                np.take(values[:, 0], source_index[:count], out=term_lower[:count], mode="clip")
                np.take(values[:, 1], source_index[:count], out=term_upper[:count], mode="clip")
                np.take(
                    forward_values[dimension],
                    rate_index[:count],
                    out=coefficient[:count],
                    mode="clip",
                )
                np.less(coefficient[:count], 0.0, out=mask[:count])
                if bool(np.any(mask[:count])):
                    raise packed.PackedF0Failure(
                        HOLD_DIRECTED_ACTION,
                        "forward incoming coefficient lost nonnegativity",
                    )
                np.equal(coordinate[:count], 0, out=mask[:count])
                np.multiply(term_lower[:count], coefficient[:count], out=term_lower[:count])
                _round_down(term_lower[:count])
                np.multiply(term_upper[:count], coefficient[:count], out=term_upper[:count])
                _round_up(term_upper[:count])
                if not axis.periodic:
                    np.copyto(term_lower[:count], 0.0, where=mask[:count])
                    np.copyto(term_upper[:count], 0.0, where=mask[:count])
                _add_outward(
                    accumulator_lower[:count],
                    accumulator_upper[:count],
                    term_lower[:count],
                    term_upper[:count],
                )

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
                np.take(values[:, 0], source_index[:count], out=term_lower[:count], mode="clip")
                np.take(values[:, 1], source_index[:count], out=term_upper[:count], mode="clip")
                np.take(
                    backward_values[dimension],
                    rate_index[:count],
                    out=coefficient[:count],
                    mode="clip",
                )
                np.less(coefficient[:count], 0.0, out=mask[:count])
                if bool(np.any(mask[:count])):
                    raise packed.PackedF0Failure(
                        HOLD_DIRECTED_ACTION,
                        "backward incoming coefficient lost nonnegativity",
                    )
                np.equal(coordinate[:count], axis.size - 1, out=mask[:count])
                np.multiply(term_lower[:count], coefficient[:count], out=term_lower[:count])
                _round_down(term_lower[:count])
                np.multiply(term_upper[:count], coefficient[:count], out=term_upper[:count])
                _round_up(term_upper[:count])
                if not axis.periodic:
                    np.copyto(term_lower[:count], 0.0, where=mask[:count])
                    np.copyto(term_upper[:count], 0.0, where=mask[:count])
                _add_outward(
                    accumulator_lower[:count],
                    accumulator_upper[:count],
                    term_lower[:count],
                    term_upper[:count],
                )

            output[start:stop, 0] = accumulator_lower[:count]
            output[start:stop, 1] = accumulator_upper[:count]

    output.setflags(write=False)
    enclosure = CanonicalDirectedIntervals(
        logical_shape=kernel.contract.tensor_shape,
        intervals=output,
        raw_sha256=_raw_sha256(output),
        input_raw_sha256=input_raw_sha256,
        exact_action_nonnegative=operator == "P",
    )
    del (
        accumulator_lower,
        accumulator_upper,
        base,
        coefficient,
        coordinate,
        flat,
        mask,
        rate_index,
        source_index,
        term_lower,
        term_upper,
    )
    # The vectorized runtime gate is part of contract validation.  Release the
    # action workspace before that gate is run with the output still live, so
    # the fixed payload ledger is output plus the maximum of the disjoint
    # action, validation, and runtime-probe workspaces.
    memory = _memory_ledger(contract)
    provisional_result = DirectedActionResult(
        schema=DIRECTED_RESULT_SCHEMA,
        operator=operator,
        enclosure=enclosure,
        input_raw_sha256=input_raw_sha256,
        kernel_replay_sha256=kernel_replay_sha256,
        action_contract_sha256=contract_sha256,
        backend_binding_sha256=contract.backend_binding_sha256,
        block_count=block_count,
        multiplication_count_per_state=1 + 2 * len(kernel.axes),
        addition_count_per_state=2 * len(kernel.axes),
        memory=memory,
        consistency_sha256="0" * 64,
        science_executed=False,
        f0_pass=False,
    )
    result = replace(
        provisional_result,
        consistency_sha256=_result_consistency_sha256(provisional_result),
    )
    packed.validate_packed_tensor_kernel(kernel)
    packed.validate_canonical_packed_intervals(vector)
    validate_directed_action_contract(contract)
    validate_directed_action_result(
        result,
        kernel=kernel,
        vector=vector,
        contract=contract,
    )
    return result


def directed_p_transpose(
    kernel: packed.PackedTensorKernel,
    vector: packed.CanonicalPackedIntervals,
    contract: DirectedActionContract,
) -> DirectedActionResult:
    """Enclose the centre ``P.T`` action for a nonnegative interval vector."""

    return _directed_transpose_action(kernel, vector, contract, operator="P")


def directed_q_transpose(
    kernel: packed.PackedTensorKernel,
    vector: packed.CanonicalPackedIntervals,
    contract: DirectedActionContract,
) -> DirectedActionResult:
    """Enclose the signed centre ``Q.T`` action for an arbitrary interval vector."""

    return _directed_transpose_action(kernel, vector, contract, operator="Q")


def validate_directed_action_result(
    result: DirectedActionResult,
    *,
    kernel: packed.PackedTensorKernel,
    vector: packed.CanonicalPackedIntervals,
    contract: DirectedActionContract,
) -> None:
    packed.validate_packed_tensor_kernel(kernel)
    packed.validate_canonical_packed_intervals(vector)
    validate_directed_action_contract(contract)
    if type(result) is not DirectedActionResult:
        raise packed.PackedF0Failure(HOLD_DIRECTED_SCHEMA, "result has wrong exact type")
    expected_terms = 1 + 2 * len(contract.tensor_shape)
    if (
        type(result.schema) is not str
        or result.schema != DIRECTED_RESULT_SCHEMA
        or type(result.operator) is not str
        or result.operator not in {"P", "Q"}
        or type(result.enclosure) is not CanonicalDirectedIntervals
        or not _is_hex_digest(result.input_raw_sha256)
        or not _is_hex_digest(result.kernel_replay_sha256)
        or not _is_hex_digest(result.action_contract_sha256)
        or result.action_contract_sha256 != directed_action_contract_sha256(contract)
        or not _is_hex_digest(result.backend_binding_sha256)
        or result.backend_binding_sha256 != contract.backend_binding_sha256
        or type(result.block_count) is not int
        or result.block_count != math.ceil(math.prod(contract.tensor_shape) / contract.block_size)
        or type(result.multiplication_count_per_state) is not int
        or result.multiplication_count_per_state != expected_terms
        or type(result.addition_count_per_state) is not int
        or result.addition_count_per_state != expected_terms - 1
        or type(result.memory) is not DirectedMemoryLedger
        or not _is_hex_digest(result.consistency_sha256)
        or type(result.science_executed) is not bool
        or result.science_executed is not False
        or type(result.f0_pass) is not bool
        or result.f0_pass is not False
    ):
        raise packed.PackedF0Failure(HOLD_DIRECTED_ACTION, "result schema is inconsistent")
    validate_canonical_directed_intervals(
        result.enclosure,
        block_size=contract.block_size,
    )
    validate_directed_memory_ledger(result.memory)
    if (
        result.enclosure.logical_shape != contract.tensor_shape
        or result.enclosure.input_raw_sha256 != result.input_raw_sha256
        or result.enclosure.exact_action_nonnegative is not (result.operator == "P")
        or result.memory.state_count != math.prod(contract.tensor_shape)
        or result.memory.block_size != contract.block_size
        or result.memory.output_payload_bytes != contract.output_payload_bytes
        or result.memory.workspace_payload_bytes != contract.workspace_payload_bytes
        or result.memory.validation_scratch_payload_bytes
        != contract.validation_scratch_payload_bytes
        or result.memory.runtime_probe_payload_bytes != contract.runtime_probe_payload_bytes
        or vector.manifest.logical_shape != contract.tensor_shape
        or vector.manifest.block_size != contract.block_size
        or result.input_raw_sha256 != vector.manifest.raw_sha256
        or result.kernel_replay_sha256 != packed._kernel_replay_digest(kernel)
        or kernel.contract.tensor_shape != contract.tensor_shape
        or kernel.contract.block_size != contract.block_size
    ):
        raise packed.PackedF0Failure(HOLD_DIRECTED_ACTION, "result bindings disagree")
    if not hmac.compare_digest(
        result.consistency_sha256,
        _result_consistency_sha256(result),
    ):
        raise packed.PackedF0Failure(
            HOLD_DIRECTED_BINDING,
            "result consistency digest disagrees with operator/kernel/input/contract/enclosure/ledger",
        )
