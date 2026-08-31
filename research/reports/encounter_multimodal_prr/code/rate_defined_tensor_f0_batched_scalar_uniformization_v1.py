"""Batched absolute-time scalar uniformization for the packed F0 method.

For one fixed killed tensor kernel and one fixed initial point-plus-``l1``
ball, this module streams

``v_k = (P.T)^k v_0`` and ``a_k = killing_center.T @ v_k``

exactly once.  It retains two full state vectors and a five-scalar ring.  All
requested exact times are evaluated directly from ``v_0`` with centered,
directed-MPFR Poisson weights.  Generator jets use the exact identity

``k.T (Q.T)^r P^k v_0 = lambda^r Delta^r a_k``.

The fast binary64 action has a fixed nonnegative operation model.  Its
coefficient, action-roundoff, reduction, input-ball, Poisson-weight,
accumulation, and right-tail errors are all included.  The returned object is
a bounded canonical method receipt.  It exposes no state arrays, but retains
canonical scalar power records so later dyadic or Newton times do not repeat
the full-state stream.

The generic API accepts caller-supplied kernels and initial states.  Absence of
a selector argument is not evidence that a control, budget, or scientific
input was excluded.  Receipts therefore mark provenance and science
classification as unclassified; a higher candidate layer may prove a neutral
origin.  This same-process layer is not an independent verifier and cannot make
F0 pass.
"""

from __future__ import annotations

import ctypes
import hashlib
import hmac
import json
import math
import platform
import struct
import sys
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Final

import gmpy2
import numpy as np
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_rate_action as rate_action

RECEIPT_SCHEMA: Final = "rate_defined_tensor_f0_batched_scalar_receipt_v1"
TIME_SCHEMA: Final = "rate_defined_tensor_f0_batched_scalar_time_v1"
POISSON_SCHEMA: Final = "rate_defined_tensor_f0_centered_poisson_v1"
JET_SCHEMA: Final = "rate_defined_tensor_f0_scalar_jet_interval_v1"
MAGNITUDE_SCHEMA: Final = "rate_defined_tensor_f0_scalar_magnitude_v1"
RESOURCE_SCHEMA: Final = "rate_defined_tensor_f0_batched_scalar_resources_v1"
SERIES_SCHEMA: Final = "rate_defined_tensor_f0_canonical_scalar_power_series_v1"
POWER_RECORD_SCHEMA: Final = "rate_defined_tensor_f0_scalar_power_record_v1"
METHOD_STATUS: Final = "BATCHED_SCALAR_METHOD_COMPLETE_NOT_F0"

MAXIMUM_BATCH_TIMES: Final = 512
MAXIMUM_POISSON_TERMS: Final = 1_000_000
MINIMUM_MPFR_PRECISION_BITS: Final = 128
MAXIMUM_MPFR_PRECISION_BITS: Final = 4_096
MAXIMUM_EXACT_INTEGER_BITS: Final = 16_384
MAXIMUM_SERIES_SERIALIZED_BYTES: Final = 256_000_000
SCALAR_RING_SIZE: Final = 5
MAXIMUM_JET_ORDER: Final = 4

FLOAT64_U: Final = Fraction(1, 2**53)
FLOAT64_ETA: Final = Fraction(1, 2**1074)

ACTION_ROUNDOFF_FORMULA: Final = (
    "gamma_(2d+1)*rho_P*nominal_l1_upper+N*(4d+1)*2^-1074_v1"
)
MASS_REDUCTION_FORMULA: Final = (
    "(computed+(N+B)*2^-1074)/(1-gamma_(N+B))_v1"
)
DOT_ROUNDOFF_FORMULA: Final = (
    "gamma_(2N+B)*exact_abs_upper+(2N+B)*2^-1074_v1"
)
TAIL_FORMULA: Final = (
    "lambda^r*2^r*Kmax*initial_mass_upper*right_poisson_tail_upper_v1"
)
MAGNITUDE_FORMULA: Final = (
    "Kmax*(2*lambda)^r*initial_mass_upper_by_submarkov_contraction_v1"
)
FINITE_DIFFERENCE_FORMULA: Final = (
    "lambda^r*sum_j((-1)^(r-j)*binom(r,j)*a_(k+j))_v1"
)

OPERATION_MODEL: Final = (
    "ieee754-binary64-round-to-nearest-subnormals-retained",
    "two-owned-full-state-vectors-ping-pong",
    "fixed-C-order-block-stencil-self-then-axis-forward-then-axis-backward",
    "nonnegative-products-and-additions-only-for-P-transpose",
    ACTION_ROUNDOFF_FORMULA,
    MASS_REDUCTION_FORMULA,
    DOT_ROUNDOFF_FORMULA,
    "blockwise-finite-nonnegative-validation-with-owned-bool-workspace",
    "one-five-entry-live-scalar-ring-plus-canonical-scalar-power-record-series",
    "centered-directed-mpfr-mode-and-right-tail",
    "poisson-mode-init-p0-back-right-tail-plan-and-forward-recurrence-counted",
    "direct-absolute-time-from-the-original-power-stream",
    FINITE_DIFFERENCE_FORMULA,
    "sign-aware-signed-accumulator-times-nonnegative-lambda-power-interval",
    TAIL_FORMULA,
    MAGNITUDE_FORMULA,
)

INPUT_PROVENANCE_CLASSIFICATION: Final = (
    "CALLER_SUPPLIED_UNCLASSIFIED_NO_CONTROL_OR_BUDGET_EXCLUSION_PROOF"
)


class BatchedScalarFailure(RuntimeError):
    """Fail-closed outcome for this bounded method layer."""


@dataclass(frozen=True, slots=True)
class ScalarJetInterval:
    schema: str
    order: int
    lower_hex: str
    upper_hex: str
    binding_sha256: str


@dataclass(frozen=True, slots=True)
class ScalarMagnitudeBound:
    schema: str
    order: int
    upper_hex: str
    formula: str
    binding_sha256: str


@dataclass(frozen=True, slots=True)
class ScalarPowerRecord:
    schema: str
    index: int
    lower_hex: str
    upper_hex: str
    binding_sha256: str


@dataclass(frozen=True, slots=True)
class CanonicalScalarPowerSeries:
    schema: str
    horizon_numerator: int
    horizon_denominator: int
    uniformization_rate_numerator: int
    uniformization_rate_denominator: int
    maximum_killing_upper_numerator: int
    maximum_killing_upper_denominator: int
    initial_mass_upper_numerator: int
    initial_mass_upper_denominator: int
    maximum_power_index: int
    records: tuple[ScalarPowerRecord, ...]
    scalar_stream_sha256: str
    series_binding_sha256: str
    state_arrays_retained: bool
    canonical_scalar_records_retained: bool
    input_provenance_classification: str
    control_exclusion_proved: bool
    science_free_proved: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class CenteredPoissonLedger:
    schema: str
    mean_numerator: int
    mean_denominator: int
    mode: int
    right_index: int
    terms: int
    tail_upper_hex: str
    requested_tail_numerator: int
    requested_tail_denominator: int
    precision_bits: int
    mode_initialization_count: int
    p0_back_recurrence_steps: int
    right_tail_planning_steps: int
    planning_recurrence_steps: int
    forward_weight_recurrence_steps: int
    mode_initialized: bool
    p0_derived_from_mode: bool
    right_tail_geometric: bool
    starts_at_zero: bool
    binding_sha256: str


@dataclass(frozen=True, slots=True)
class AbsoluteTimeScalarJets:
    schema: str
    time_numerator: int
    time_denominator: int
    poisson: CenteredPoissonLedger
    jets: tuple[ScalarJetInterval, ...]
    magnitudes: tuple[ScalarMagnitudeBound, ...]
    absolute_time_from_initial: bool
    state_chaining_used: bool
    binding_sha256: str


@dataclass(frozen=True, slots=True)
class BatchedScalarResources:
    schema: str
    state_count: int
    block_size: int
    block_capacity: int
    time_count: int
    maximum_time_count: int
    maximum_power_index: int
    p_action_calls: int
    scalar_observable_calls: int
    maximum_poisson_terms_requested: int
    maximum_poisson_terms_used: int
    poisson_plan_count: int
    poisson_p0_back_recurrence_steps_total: int
    poisson_right_tail_planning_steps_total: int
    poisson_forward_weight_recurrence_steps_total: int
    mpfr_precision_bits: int
    full_state_vector_count: int
    maximum_simultaneous_full_state_vectors: int
    retained_full_power_count: int
    scalar_ring_capacity: int
    retained_numpy_scalar_power_array: bool
    retained_scalar_power_record_count: int
    block_integer_workspace_bytes: int
    block_float_workspace_bytes: int
    block_boolean_workspace_bytes: int
    untracked_explicit_numpy_temporary_bytes: int
    fast_action_workspace_bytes: int
    state_vector_payload_bytes: int
    declared_peak_numeric_payload_bytes_excluding_preowned_kernel: int
    maximum_mpfr_object_count_upper: int
    mpfr_payload_bytes_measured: bool
    bounded_memory_by_declared_counts: bool
    action_roundoff_proof_complete: bool
    coefficient_error_included: bool
    reduction_roundoff_included: bool
    poisson_roundoff_included: bool
    poisson_tail_included: bool
    production_scale_execution_classified: bool
    production_resource_gate: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class BatchedScalarReceipt:
    schema: str
    kernel_replay_sha256: str
    initial_input_binding_sha256: str
    rate_action_contract_sha256: str
    operation_model_sha256: str
    scalar_stream_sha256: str
    final_power_raw_sha256: str
    uniformization_rate_numerator: int
    uniformization_rate_denominator: int
    maximum_killing_upper_numerator: int
    maximum_killing_upper_denominator: int
    initial_mass_upper_numerator: int
    initial_mass_upper_denominator: int
    maximum_state_radius_upper_hex: str
    scalar_series: CanonicalScalarPowerSeries
    evaluations: tuple[AbsoluteTimeScalarJets, ...]
    resources: BatchedScalarResources
    runtime: str
    status: str
    canonical_receipt: bool
    declared_initial_mass_cap_precondition: bool
    absolute_time_from_initial: bool
    state_chaining_used: bool
    input_provenance_classification: str
    control_exclusion_proved: bool
    science_free_proved: bool
    fresh_process: bool
    independent_audit_complete: bool
    production_scale_execution_classified: bool
    production_resource_gate: bool
    f0_pass: bool
    receipt_sha256: str


@dataclass(frozen=True, slots=True)
class _ScalarInterval:
    lower: float
    upper: float


@dataclass(frozen=True, slots=True)
class _PoissonPlan:
    mean: Fraction
    mode: int
    right_index: int
    tail_upper: gmpy2.mpfr
    p0_lower: gmpy2.mpfr
    p0_upper: gmpy2.mpfr
    p0_back_recurrence_steps: int
    right_tail_planning_steps: int


@dataclass(slots=True)
class _EvaluationState:
    plan: _PoissonPlan
    current_index: int
    current_weight_lower: gmpy2.mpfr
    current_weight_upper: gmpy2.mpfr
    weight_ring: list[tuple[int, gmpy2.mpfr, gmpy2.mpfr] | None]
    accumulator_lower: list[gmpy2.mpfr]
    accumulator_upper: list[gmpy2.mpfr]


@dataclass(slots=True)
class _FastWorkspace:
    capacity: int
    base: np.ndarray
    flat: np.ndarray
    coordinate: np.ndarray
    source_index: np.ndarray
    rate_index: np.ndarray
    mask: np.ndarray
    scratch: np.ndarray
    term: np.ndarray
    coefficient: np.ndarray

    @property
    def integer_payload_bytes(self) -> int:
        return sum(
            int(value.nbytes)
            for value in (
                self.base,
                self.flat,
                self.coordinate,
                self.source_index,
                self.rate_index,
            )
        )

    @property
    def float_payload_bytes(self) -> int:
        return sum(
            int(value.nbytes)
            for value in (
                self.scratch,
                self.term,
                self.coefficient,
            )
        )

    @property
    def boolean_payload_bytes(self) -> int:
        return int(self.mask.nbytes)

    @property
    def payload_bytes(self) -> int:
        return (
            self.integer_payload_bytes
            + self.float_payload_bytes
            + self.boolean_payload_bytes
        )


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _runtime_identity() -> str:
    return (
        f"python-{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        f"|numpy-{np.__version__}|gmpy2-{gmpy2.version()}"
        f"|machine-{platform.machine()}|byteorder-{sys.byteorder}"
    )


def _canonical_json_digest(payload: object) -> str:
    try:
        encoded = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise BatchedScalarFailure("canonical receipt encoding failed") from error
    return hashlib.sha256(encoded).hexdigest()


def _operation_model_sha256() -> str:
    return _canonical_json_digest(list(OPERATION_MODEL))


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _raw_sha256(values: np.ndarray) -> str:
    return hashlib.sha256(memoryview(values).cast("B")).hexdigest()


def _validate_fraction(value: object, *, label: str, nonnegative: bool = True) -> Fraction:
    if type(value) is not Fraction:
        raise BatchedScalarFailure(f"{label} must be an exact Fraction")
    if nonnegative and value < 0:
        raise BatchedScalarFailure(f"{label} must be nonnegative")
    if (
        abs(value.numerator).bit_length() > MAXIMUM_EXACT_INTEGER_BITS
        or value.denominator.bit_length() > MAXIMUM_EXACT_INTEGER_BITS
    ):
        raise BatchedScalarFailure(f"{label} exceeds the exact-integer cap")
    return value


def _require_exact_int(
    value: object,
    *,
    label: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    if type(value) is not int:
        raise BatchedScalarFailure(f"{label} must be an exact int")
    if minimum is not None and value < minimum:
        raise BatchedScalarFailure(f"{label} is below its minimum")
    if maximum is not None and value > maximum:
        raise BatchedScalarFailure(f"{label} exceeds its maximum")
    if abs(value).bit_length() > MAXIMUM_EXACT_INTEGER_BITS:
        raise BatchedScalarFailure(f"{label} exceeds the exact-integer cap")
    return value


def _fraction_from_metadata(
    numerator: object,
    denominator: object,
    *,
    label: str,
) -> Fraction:
    exact_numerator = _require_exact_int(
        numerator,
        label=f"{label} numerator",
    )
    exact_denominator = _require_exact_int(
        denominator,
        label=f"{label} denominator",
        minimum=1,
    )
    return Fraction(exact_numerator, exact_denominator)


def _parse_hex(value: object, *, label: str, nonnegative: bool = False) -> float:
    if type(value) is not str or len(value) > 32:
        raise BatchedScalarFailure(f"{label} has a noncanonical hex token")
    try:
        parsed = float.fromhex(value)
    except (OverflowError, ValueError) as error:
        raise BatchedScalarFailure(f"{label} has an invalid hex token") from error
    if (
        not math.isfinite(parsed)
        or parsed.hex() != value
        or (nonnegative and parsed < 0.0)
        or (parsed == 0.0 and math.copysign(1.0, parsed) < 0.0)
    ):
        raise BatchedScalarFailure(f"{label} has an invalid binary64 endpoint")
    return parsed


def _verify_binary64_runtime() -> None:
    info = np.finfo(np.float64)
    if np.dtype(np.float64).itemsize != 8 or info.nmant != 52:
        raise BatchedScalarFailure("runtime is not IEEE binary64")
    try:
        fegetround = ctypes.CDLL(None).fegetround
        fegetround.restype = ctypes.c_int
        if int(fegetround()) != 0:
            raise BatchedScalarFailure("runtime rounding mode is not round-to-nearest")
    except AttributeError as error:
        raise BatchedScalarFailure("fegetround is unavailable") from error
    eta = np.nextafter(np.float64(0.0), np.float64(1.0))
    if eta == 0.0 or np.float64(eta + eta) == 0.0:
        raise BatchedScalarFailure("binary64 subnormals are flushed")


def _gamma(index: int) -> Fraction:
    if type(index) is not int or index < 0 or index >= 2**53:
        raise BatchedScalarFailure("roundoff gamma index is invalid")
    return Fraction(index, 2**53 - index) if index else Fraction(0)


def _fraction_to_float_upper(value: Fraction) -> float:
    if value < 0:
        raise BatchedScalarFailure("upper endpoint received a negative radius")
    try:
        candidate = float(value)
    except OverflowError as error:
        raise BatchedScalarFailure("upper endpoint does not fit binary64") from error
    if not math.isfinite(candidate):
        raise BatchedScalarFailure("upper endpoint does not fit binary64")
    if Fraction.from_float(candidate) < value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    if not math.isfinite(candidate) or Fraction.from_float(candidate) < value:
        raise BatchedScalarFailure("upper endpoint conversion was not outward")
    return candidate


def _fraction_to_float_lower(value: Fraction) -> float:
    try:
        candidate = float(value)
    except OverflowError as error:
        raise BatchedScalarFailure("lower endpoint does not fit binary64") from error
    if not math.isfinite(candidate):
        raise BatchedScalarFailure("lower endpoint does not fit binary64")
    if Fraction.from_float(candidate) > value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(-math.inf)))
    if not math.isfinite(candidate) or Fraction.from_float(candidate) > value:
        raise BatchedScalarFailure("lower endpoint conversion was not outward")
    if candidate == 0.0:
        return 0.0
    return candidate


def _mpfr_from_fraction(value: Fraction, precision: int, rounding: int) -> gmpy2.mpfr:
    with gmpy2.context(gmpy2.get_context(), precision=precision, round=rounding):
        return gmpy2.mpfr(value.numerator) / gmpy2.mpfr(value.denominator)


def _mpfr_from_float(value: float, precision: int, rounding: int) -> gmpy2.mpfr:
    if not math.isfinite(value):
        raise BatchedScalarFailure("nonfinite binary64 cannot enter MPFR")
    with gmpy2.context(gmpy2.get_context(), precision=precision, round=rounding):
        return gmpy2.mpfr(value)


def _mpfr_to_float_lower(value: gmpy2.mpfr, precision: int) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise BatchedScalarFailure("MPFR lower endpoint does not fit binary64")
    with gmpy2.context(
        gmpy2.get_context(),
        precision=max(precision, 128),
        round=gmpy2.RoundToNearest,
    ):
        if gmpy2.mpfr(candidate) > value:
            candidate = float(np.nextafter(np.float64(candidate), np.float64(-math.inf)))
    if candidate == 0.0:
        return 0.0
    return candidate


def _mpfr_to_float_upper(value: gmpy2.mpfr, precision: int) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise BatchedScalarFailure("MPFR upper endpoint does not fit binary64")
    with gmpy2.context(
        gmpy2.get_context(),
        precision=max(precision, 128),
        round=gmpy2.RoundToNearest,
    ):
        if gmpy2.mpfr(candidate) < value:
            candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    if candidate == 0.0:
        return 0.0
    return candidate


def _make_fast_workspace(capacity: int) -> _FastWorkspace:
    if type(capacity) is not int or capacity < 1:
        raise BatchedScalarFailure("fast-action capacity is invalid")
    return _FastWorkspace(
        capacity=capacity,
        base=np.arange(capacity, dtype=np.int64),
        flat=np.empty(capacity, dtype=np.int64),
        coordinate=np.empty(capacity, dtype=np.int64),
        source_index=np.empty(capacity, dtype=np.int64),
        rate_index=np.empty(capacity, dtype=np.int64),
        mask=np.empty(capacity, dtype=np.bool_),
        scratch=np.empty(capacity, dtype=np.float64),
        term=np.empty(capacity, dtype=np.float64),
        coefficient=np.empty(capacity, dtype=np.float64),
    )


def _axis_strides(shape: tuple[int, ...]) -> tuple[int, ...]:
    strides: list[int] = []
    for dimension in range(len(shape)):
        strides.append(math.prod(shape[dimension + 1 :]))
    return tuple(strides)


def _fast_p_transpose_into(
    kernel: packed.PackedTensorKernel,
    source: np.ndarray,
    destination: np.ndarray,
    workspace: _FastWorkspace,
) -> None:
    """Apply the fixed packed centre ``P.T`` without per-power allocation.

    Every output is a sum of nonnegative terms.  A contribution encounters one
    multiplication and at most ``2*d`` additions, giving ``gamma_(2*d+1)``.
    The separate recurrence adds the conservative ``N*(4*d+1)*eta``
    underflow allowance and the exact ``delta_p_selected`` coefficient bound.
    """

    states = kernel.states
    if (
        type(source) is not np.ndarray
        or type(destination) is not np.ndarray
        or source.dtype != np.dtype(np.float64)
        or destination.dtype != np.dtype(np.float64)
        or source.shape != (states,)
        or destination.shape != (states,)
        or not source.flags.c_contiguous
        or not destination.flags.c_contiguous
        or workspace.capacity != min(states, kernel.contract.block_size)
    ):
        raise BatchedScalarFailure("fast-action buffers are inconsistent")
    strides = _axis_strides(kernel.contract.tensor_shape)
    block_size = kernel.contract.block_size
    for start in range(0, states, block_size):
        stop = min(states, start + block_size)
        count = stop - start
        np.add(workspace.base[:count], start, out=workspace.flat[:count])
        np.multiply(
            source[start:stop],
            kernel.p_self_center[start:stop],
            out=workspace.scratch[:count],
        )
        for dimension, (axis, stride) in enumerate(
            zip(kernel.axes, strides, strict=True)
        ):
            np.floor_divide(
                workspace.flat[:count],
                stride,
                out=workspace.coordinate[:count],
            )
            np.remainder(
                workspace.coordinate[:count],
                axis.size,
                out=workspace.coordinate[:count],
            )

            np.equal(workspace.coordinate[:count], 0, out=workspace.mask[:count])
            np.subtract(
                workspace.flat[:count],
                stride,
                out=workspace.source_index[:count],
            )
            np.subtract(
                workspace.coordinate[:count],
                1,
                out=workspace.rate_index[:count],
            )
            if axis.periodic:
                np.add(
                    workspace.flat[:count],
                    (axis.size - 1) * stride,
                    out=workspace.source_index[:count],
                    where=workspace.mask[:count],
                )
                np.copyto(
                    workspace.rate_index[:count],
                    axis.size - 1,
                    where=workspace.mask[:count],
                )
            else:
                np.copyto(
                    workspace.source_index[:count],
                    0,
                    where=workspace.mask[:count],
                )
                np.copyto(
                    workspace.rate_index[:count],
                    0,
                    where=workspace.mask[:count],
                )
            np.take(
                source,
                workspace.source_index[:count],
                out=workspace.term[:count],
                mode="clip",
            )
            np.take(
                kernel.p_forward_center[dimension],
                workspace.rate_index[:count],
                out=workspace.coefficient[:count],
                mode="clip",
            )
            np.multiply(
                workspace.term[:count],
                workspace.coefficient[:count],
                out=workspace.term[:count],
            )
            if not axis.periodic:
                np.copyto(
                    workspace.term[:count],
                    0.0,
                    where=workspace.mask[:count],
                )
            np.add(
                workspace.scratch[:count],
                workspace.term[:count],
                out=workspace.scratch[:count],
            )

            np.equal(
                workspace.coordinate[:count],
                axis.size - 1,
                out=workspace.mask[:count],
            )
            np.add(
                workspace.flat[:count],
                stride,
                out=workspace.source_index[:count],
            )
            np.add(
                workspace.coordinate[:count],
                1,
                out=workspace.rate_index[:count],
            )
            if axis.periodic:
                np.subtract(
                    workspace.flat[:count],
                    (axis.size - 1) * stride,
                    out=workspace.source_index[:count],
                    where=workspace.mask[:count],
                )
                np.copyto(
                    workspace.rate_index[:count],
                    0,
                    where=workspace.mask[:count],
                )
            else:
                np.copyto(
                    workspace.source_index[:count],
                    0,
                    where=workspace.mask[:count],
                )
                np.copyto(
                    workspace.rate_index[:count],
                    0,
                    where=workspace.mask[:count],
                )
            np.take(
                source,
                workspace.source_index[:count],
                out=workspace.term[:count],
                mode="clip",
            )
            np.take(
                kernel.p_backward_center[dimension],
                workspace.rate_index[:count],
                out=workspace.coefficient[:count],
                mode="clip",
            )
            np.multiply(
                workspace.term[:count],
                workspace.coefficient[:count],
                out=workspace.term[:count],
            )
            if not axis.periodic:
                np.copyto(
                    workspace.term[:count],
                    0.0,
                    where=workspace.mask[:count],
                )
            np.add(
                workspace.scratch[:count],
                workspace.term[:count],
                out=workspace.scratch[:count],
            )
        destination[start:stop] = workspace.scratch[:count]
        np.isfinite(destination[start:stop], out=workspace.mask[:count])
        if not bool(np.all(workspace.mask[:count])):
            raise BatchedScalarFailure("fast P action produced a nonfinite value")
        np.less(destination[start:stop], 0.0, out=workspace.mask[:count])
        if bool(np.any(workspace.mask[:count])):
            raise BatchedScalarFailure("fast P action lost nonnegativity")


def _validate_nonnegative_vector_blocks(
    values: np.ndarray,
    workspace: _FastWorkspace,
    *,
    block_size: int,
    label: str,
) -> None:
    if (
        type(values) is not np.ndarray
        or values.dtype != np.dtype(np.float64)
        or values.ndim != 1
        or not values.flags.c_contiguous
        or type(block_size) is not int
        or block_size < 1
        or workspace.capacity != min(values.size, block_size)
    ):
        raise BatchedScalarFailure(f"{label} is malformed")
    for start in range(0, values.size, block_size):
        stop = min(values.size, start + block_size)
        count = stop - start
        block = values[start:stop]
        np.isfinite(block, out=workspace.mask[:count])
        if not bool(np.all(workspace.mask[:count])):
            raise BatchedScalarFailure(f"{label} contains a nonfinite value")
        np.less(block, 0.0, out=workspace.mask[:count])
        if bool(np.any(workspace.mask[:count])):
            raise BatchedScalarFailure(f"{label} contains a negative value")


def _positive_reduction_upper(
    values: np.ndarray,
    workspace: _FastWorkspace,
    *,
    block_size: int,
) -> tuple[float, Fraction]:
    if (
        type(values) is not np.ndarray
        or values.dtype != np.dtype(np.float64)
        or values.ndim != 1
        or not values.flags.c_contiguous
    ):
        raise BatchedScalarFailure("positive reduction input is malformed")
    _validate_nonnegative_vector_blocks(
        values,
        workspace,
        block_size=block_size,
        label="positive reduction input",
    )
    total = np.float64(0.0)
    blocks = 0
    for start in range(0, values.size, block_size):
        stop = min(values.size, start + block_size)
        block = values[start:stop]
        block_sum = np.add.reduce(block, dtype=np.float64)
        total = np.add(total, block_sum, dtype=np.float64)
        blocks += 1
    nominal = float(total)
    if not math.isfinite(nominal) or nominal < 0.0:
        raise BatchedScalarFailure("positive reduction overflowed")
    operations = values.size + blocks
    gamma = _gamma(operations)
    if gamma >= 1:
        raise BatchedScalarFailure("positive reduction gamma is unresolved")
    underflow = operations * FLOAT64_ETA
    exact_upper = (Fraction.from_float(nominal) + underflow) / (1 - gamma)
    return nominal, exact_upper


def _positive_dot_with_roundoff(
    left: np.ndarray,
    right: np.ndarray,
    workspace: _FastWorkspace,
    *,
    block_size: int,
) -> tuple[float, Fraction]:
    if (
        type(left) is not np.ndarray
        or type(right) is not np.ndarray
        or left.dtype != np.dtype(np.float64)
        or right.dtype != np.dtype(np.float64)
        or left.shape != right.shape
        or left.ndim != 1
    ):
        raise BatchedScalarFailure("positive dot inputs are malformed")
    _validate_nonnegative_vector_blocks(
        left,
        workspace,
        block_size=block_size,
        label="positive dot left input",
    )
    _validate_nonnegative_vector_blocks(
        right,
        workspace,
        block_size=block_size,
        label="positive dot right input",
    )
    total = np.float64(0.0)
    blocks = 0
    for start in range(0, left.size, block_size):
        stop = min(left.size, start + block_size)
        count = stop - start
        left_block = left[start:stop]
        right_block = right[start:stop]
        np.multiply(left_block, right_block, out=workspace.term[:count])
        block_sum = np.add.reduce(workspace.term[:count], dtype=np.float64)
        total = np.add(total, block_sum, dtype=np.float64)
        blocks += 1
    nominal = float(total)
    if not math.isfinite(nominal) or nominal < 0.0:
        raise BatchedScalarFailure("positive dot overflowed")
    operations = 2 * left.size + blocks
    gamma = _gamma(operations)
    if gamma >= 1:
        raise BatchedScalarFailure("positive dot gamma is unresolved")
    underflow = operations * FLOAT64_ETA
    exact_absolute_upper = (
        Fraction.from_float(abs(nominal)) + underflow
    ) / (1 - gamma)
    radius = gamma * exact_absolute_upper + underflow
    return nominal, radius


def _centered_poisson_plan(
    mean: Fraction,
    tail_tolerance: Fraction,
    *,
    precision_bits: int,
    maximum_terms: int,
) -> _PoissonPlan:
    mean = _validate_fraction(mean, label="Poisson mean")
    tolerance = _validate_fraction(tail_tolerance, label="tail tolerance")
    _require_exact_int(
        precision_bits,
        label="Poisson precision bits",
        minimum=MINIMUM_MPFR_PRECISION_BITS,
        maximum=MAXIMUM_MPFR_PRECISION_BITS,
    )
    _require_exact_int(
        maximum_terms,
        label="Poisson maximum terms",
        minimum=1,
        maximum=MAXIMUM_POISSON_TERMS,
    )
    if tolerance <= 0 or tolerance >= 1:
        raise BatchedScalarFailure("tail tolerance must lie strictly between zero and one")
    mode = mean.numerator // mean.denominator
    if mode >= maximum_terms:
        raise BatchedScalarFailure(
            "Poisson mode reaches or exceeds the term cap before MPFR planning"
        )
    if mean == 0:
        one = _mpfr_from_fraction(Fraction(1), precision_bits, gmpy2.RoundToNearest)
        zero = _mpfr_from_fraction(Fraction(0), precision_bits, gmpy2.RoundToNearest)
        return _PoissonPlan(
            mean=mean,
            mode=0,
            right_index=0,
            tail_upper=zero,
            p0_lower=one,
            p0_upper=one,
            p0_back_recurrence_steps=0,
            right_tail_planning_steps=0,
        )

    x_lower = _mpfr_from_fraction(mean, precision_bits, gmpy2.RoundDown)
    x_upper = _mpfr_from_fraction(mean, precision_bits, gmpy2.RoundUp)
    tolerance_lower = _mpfr_from_fraction(
        tolerance,
        precision_bits,
        gmpy2.RoundDown,
    )
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundDown,
    ):
        log_lower = gmpy2.log(x_lower)
        gamma_lower = gmpy2.lngamma(gmpy2.mpfr(mode + 1))
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundUp,
    ):
        log_upper = gmpy2.log(x_upper)
        gamma_upper = gmpy2.lngamma(gmpy2.mpfr(mode + 1))
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundDown,
    ):
        exponent_lower = -x_upper + mode * log_lower - gamma_upper
        mode_lower = gmpy2.exp(exponent_lower)
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundUp,
    ):
        exponent_upper = -x_lower + mode * log_upper - gamma_lower
        mode_upper = gmpy2.exp(exponent_upper)
    if not (0 <= mode_lower <= mode_upper <= 1):
        raise BatchedScalarFailure("centered Poisson mode enclosure is invalid")

    current_lower = mode_lower
    current_upper = mode_upper
    right_index = mode
    while True:
        if right_index + 1 >= maximum_terms:
            raise BatchedScalarFailure("Poisson term cap was reached before tail closure")
        denominator = right_index + 1
        with gmpy2.context(
            gmpy2.get_context(),
            precision=precision_bits,
            round=gmpy2.RoundDown,
        ):
            next_lower = current_lower * x_lower / denominator
        with gmpy2.context(
            gmpy2.get_context(),
            precision=precision_bits,
            round=gmpy2.RoundUp,
        ):
            next_upper = current_upper * x_upper / denominator
            ratio_upper = x_upper / (right_index + 2)
            if ratio_upper < 1:
                tail_upper = next_upper / (1 - ratio_upper)
            else:
                tail_upper = gmpy2.mpfr(1)
        if ratio_upper < 1 and tail_upper <= tolerance_lower:
            break
        current_lower = next_lower
        current_upper = next_upper
        right_index += 1

    p0_lower = mode_lower
    p0_upper = mode_upper
    for index in range(mode, 0, -1):
        with gmpy2.context(
            gmpy2.get_context(),
            precision=precision_bits,
            round=gmpy2.RoundDown,
        ):
            p0_lower = p0_lower * index / x_upper
        with gmpy2.context(
            gmpy2.get_context(),
            precision=precision_bits,
            round=gmpy2.RoundUp,
        ):
            p0_upper = p0_upper * index / x_lower
    if not (0 <= p0_lower <= p0_upper <= 1):
        raise BatchedScalarFailure("centered-to-zero Poisson recurrence is invalid")
    return _PoissonPlan(
        mean=mean,
        mode=mode,
        right_index=right_index,
        tail_upper=tail_upper,
        p0_lower=p0_lower,
        p0_upper=p0_upper,
        p0_back_recurrence_steps=mode,
        right_tail_planning_steps=right_index - mode + 1,
    )


def _new_evaluation_state(plan: _PoissonPlan, precision_bits: int) -> _EvaluationState:
    zero_lower = _mpfr_from_fraction(Fraction(0), precision_bits, gmpy2.RoundDown)
    zero_upper = _mpfr_from_fraction(Fraction(0), precision_bits, gmpy2.RoundUp)
    return _EvaluationState(
        plan=plan,
        current_index=0,
        current_weight_lower=plan.p0_lower,
        current_weight_upper=plan.p0_upper,
        weight_ring=[None for _ in range(SCALAR_RING_SIZE)],
        accumulator_lower=[gmpy2.mpfr(zero_lower) for _ in range(MAXIMUM_JET_ORDER + 1)],
        accumulator_upper=[gmpy2.mpfr(zero_upper) for _ in range(MAXIMUM_JET_ORDER + 1)],
    )


def _advance_weight(state: _EvaluationState, precision_bits: int) -> None:
    next_index = state.current_index + 1
    x_lower = _mpfr_from_fraction(state.plan.mean, precision_bits, gmpy2.RoundDown)
    x_upper = _mpfr_from_fraction(state.plan.mean, precision_bits, gmpy2.RoundUp)
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundDown,
    ):
        state.current_weight_lower = (
            state.current_weight_lower * x_lower / next_index
        )
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundUp,
    ):
        state.current_weight_upper = (
            state.current_weight_upper * x_upper / next_index
        )
    state.current_index = next_index


def _finite_difference_interval(
    scalar_ring: list[tuple[int, _ScalarInterval] | None],
    *,
    power_index: int,
    order: int,
    precision_bits: int,
) -> tuple[gmpy2.mpfr, gmpy2.mpfr]:
    base = power_index - order
    if base < 0:
        raise BatchedScalarFailure("finite difference requested before its base index")
    lower = _mpfr_from_fraction(Fraction(0), precision_bits, gmpy2.RoundDown)
    upper = _mpfr_from_fraction(Fraction(0), precision_bits, gmpy2.RoundUp)
    for offset in range(order + 1):
        index = base + offset
        row = scalar_ring[index % SCALAR_RING_SIZE]
        if row is None or row[0] != index:
            raise BatchedScalarFailure("scalar ring lost a finite-difference predecessor")
        scalar = row[1]
        coefficient = ((-1) ** (order - offset)) * math.comb(order, offset)
        with gmpy2.context(
            gmpy2.get_context(),
            precision=precision_bits,
            round=gmpy2.RoundDown,
        ):
            if coefficient >= 0:
                lower += coefficient * _mpfr_from_float(
                    scalar.lower,
                    precision_bits,
                    gmpy2.RoundDown,
                )
            else:
                lower += coefficient * _mpfr_from_float(
                    scalar.upper,
                    precision_bits,
                    gmpy2.RoundUp,
                )
        with gmpy2.context(
            gmpy2.get_context(),
            precision=precision_bits,
            round=gmpy2.RoundUp,
        ):
            if coefficient >= 0:
                upper += coefficient * _mpfr_from_float(
                    scalar.upper,
                    precision_bits,
                    gmpy2.RoundUp,
                )
            else:
                upper += coefficient * _mpfr_from_float(
                    scalar.lower,
                    precision_bits,
                    gmpy2.RoundDown,
                )
    if lower > upper:
        raise BatchedScalarFailure("finite-difference interval reversed")
    return lower, upper


def _accumulate_weighted_interval(
    state: _EvaluationState,
    *,
    order: int,
    weight_lower: gmpy2.mpfr,
    weight_upper: gmpy2.mpfr,
    value_lower: gmpy2.mpfr,
    value_upper: gmpy2.mpfr,
    precision_bits: int,
) -> None:
    if weight_lower < 0 or weight_upper < weight_lower or value_upper < value_lower:
        raise BatchedScalarFailure("weighted interval operands are invalid")
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundDown,
    ):
        if value_lower >= 0:
            product_lower = weight_lower * value_lower
        else:
            product_lower = weight_upper * value_lower
        state.accumulator_lower[order] += product_lower
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundUp,
    ):
        if value_upper <= 0:
            product_upper = weight_lower * value_upper
        else:
            product_upper = weight_upper * value_upper
        state.accumulator_upper[order] += product_upper


def _multiply_signed_interval_by_nonnegative_interval(
    value_lower: gmpy2.mpfr,
    value_upper: gmpy2.mpfr,
    factor_lower: gmpy2.mpfr,
    factor_upper: gmpy2.mpfr,
    *,
    precision_bits: int,
) -> tuple[gmpy2.mpfr, gmpy2.mpfr]:
    """Directed product of a signed interval and a nonnegative interval."""

    if (
        value_lower > value_upper
        or factor_lower < 0
        or factor_lower > factor_upper
    ):
        raise BatchedScalarFailure("signed scaling interval operands are invalid")
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundDown,
    ):
        if value_lower >= 0:
            lower = value_lower * factor_lower
        else:
            lower = value_lower * factor_upper
    with gmpy2.context(
        gmpy2.get_context(),
        precision=precision_bits,
        round=gmpy2.RoundUp,
    ):
        if value_upper <= 0:
            upper = value_upper * factor_lower
        else:
            upper = value_upper * factor_upper
    if lower > upper:
        raise BatchedScalarFailure("signed scaling interval reversed")
    return lower, upper


def _power_record_payload(row: ScalarPowerRecord) -> dict[str, object]:
    return {
        "index": row.index,
        "lower_hex": row.lower_hex,
        "schema": row.schema,
        "upper_hex": row.upper_hex,
    }


def _power_record_binding(row: ScalarPowerRecord) -> str:
    return _canonical_json_digest(_power_record_payload(row))


def _series_payload(row: CanonicalScalarPowerSeries) -> dict[str, object]:
    return {
        "canonical_scalar_records_retained": row.canonical_scalar_records_retained,
        "control_exclusion_proved": row.control_exclusion_proved,
        "f0_pass": row.f0_pass,
        "horizon_denominator": row.horizon_denominator,
        "horizon_numerator": row.horizon_numerator,
        "initial_mass_upper_denominator": row.initial_mass_upper_denominator,
        "initial_mass_upper_numerator": row.initial_mass_upper_numerator,
        "maximum_killing_upper_denominator": row.maximum_killing_upper_denominator,
        "maximum_killing_upper_numerator": row.maximum_killing_upper_numerator,
        "maximum_power_index": row.maximum_power_index,
        "record_bindings": [record.binding_sha256 for record in row.records],
        "scalar_stream_sha256": row.scalar_stream_sha256,
        "schema": row.schema,
        "science_free_proved": row.science_free_proved,
        "state_arrays_retained": row.state_arrays_retained,
        "input_provenance_classification": row.input_provenance_classification,
        "uniformization_rate_denominator": row.uniformization_rate_denominator,
        "uniformization_rate_numerator": row.uniformization_rate_numerator,
    }


def _series_binding(row: CanonicalScalarPowerSeries) -> str:
    return _canonical_json_digest(_series_payload(row))


def validate_canonical_scalar_power_series(
    series: CanonicalScalarPowerSeries,
) -> None:
    """Validate one scalar-only cache before any later absolute-time query."""

    if type(series) is not CanonicalScalarPowerSeries:
        raise BatchedScalarFailure("scalar series has the wrong exact type")
    integer_fields = (
        series.horizon_numerator,
        series.horizon_denominator,
        series.uniformization_rate_numerator,
        series.uniformization_rate_denominator,
        series.maximum_killing_upper_numerator,
        series.maximum_killing_upper_denominator,
        series.initial_mass_upper_numerator,
        series.initial_mass_upper_denominator,
        series.maximum_power_index,
    )
    if (
        series.schema != SERIES_SCHEMA
        or any(type(value) is not int for value in integer_fields)
        or not _is_sha256(series.scalar_stream_sha256)
        or not _is_sha256(series.series_binding_sha256)
        or type(series.records) is not tuple
        or not series.records
        or series.maximum_power_index != len(series.records) - 1
        or series.state_arrays_retained is not False
        or series.canonical_scalar_records_retained is not True
        or series.input_provenance_classification
        != INPUT_PROVENANCE_CLASSIFICATION
        or series.control_exclusion_proved is not False
        or series.science_free_proved is not False
        or series.f0_pass is not False
    ):
        raise BatchedScalarFailure("scalar series header is invalid")
    horizon = _fraction_from_metadata(
        series.horizon_numerator,
        series.horizon_denominator,
        label="series horizon",
    )
    rate = _fraction_from_metadata(
        series.uniformization_rate_numerator,
        series.uniformization_rate_denominator,
        label="series rate",
    )
    killing_upper = _fraction_from_metadata(
        series.maximum_killing_upper_numerator,
        series.maximum_killing_upper_denominator,
        label="series killing upper",
    )
    mass_upper = _fraction_from_metadata(
        series.initial_mass_upper_numerator,
        series.initial_mass_upper_denominator,
        label="series initial mass upper",
    )
    if horizon < 0 or rate <= 0 or killing_upper < 0 or not 0 < mass_upper <= 1:
        raise BatchedScalarFailure("scalar series exact metadata is invalid")
    for index, record in enumerate(series.records):
        if (
            type(record) is not ScalarPowerRecord
            or record.schema != POWER_RECORD_SCHEMA
            or type(record.index) is not int
            or record.index != index
        ):
            raise BatchedScalarFailure("scalar power record order is invalid")
        lower = _parse_hex(record.lower_hex, label="scalar record lower", nonnegative=True)
        upper = _parse_hex(record.upper_hex, label="scalar record upper", nonnegative=True)
        if lower > upper or record.binding_sha256 != _power_record_binding(record):
            raise BatchedScalarFailure("scalar power record binding is invalid")
    if not hmac.compare_digest(
        series.series_binding_sha256,
        _series_binding(series),
    ):
        raise BatchedScalarFailure("scalar series content hash is invalid")


def canonical_scalar_power_series_bytes(
    series: CanonicalScalarPowerSeries,
) -> bytes:
    """Return canonical ASCII JSON bytes suitable for scalar-only persistence."""

    validate_canonical_scalar_power_series(series)
    payload = {
        **{
            key: value
            for key, value in _series_payload(series).items()
            if key != "record_bindings"
        },
        "records": [
            {
                **_power_record_payload(record),
                "binding_sha256": record.binding_sha256,
            }
            for record in series.records
        ],
        "series_binding_sha256": series.series_binding_sha256,
    }
    try:
        encoded = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise BatchedScalarFailure("scalar series serialization failed") from error
    if len(encoded) > MAXIMUM_SERIES_SERIALIZED_BYTES:
        raise BatchedScalarFailure("scalar series serialization exceeds its byte cap")
    return encoded


def _reject_duplicate_json_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise BatchedScalarFailure("scalar series JSON contains a duplicate key")
        result[key] = value
    return result


def load_canonical_scalar_power_series_bytes(
    payload: bytes,
) -> CanonicalScalarPowerSeries:
    """Strictly reconstruct canonical scalar-only persistence bytes."""

    if (
        type(payload) is not bytes
        or not payload
        or len(payload) > MAXIMUM_SERIES_SERIALIZED_BYTES
    ):
        raise BatchedScalarFailure("serialized scalar series has an invalid byte envelope")
    try:
        parsed = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(
                BatchedScalarFailure(f"invalid JSON constant {token}")
            ),
        )
    except BatchedScalarFailure:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        raise BatchedScalarFailure("serialized scalar series is not valid ASCII JSON") from error
    expected_keys = {
        "canonical_scalar_records_retained",
        "control_exclusion_proved",
        "f0_pass",
        "horizon_denominator",
        "horizon_numerator",
        "initial_mass_upper_denominator",
        "initial_mass_upper_numerator",
        "maximum_killing_upper_denominator",
        "maximum_killing_upper_numerator",
        "maximum_power_index",
        "records",
        "scalar_stream_sha256",
        "schema",
        "science_free_proved",
        "series_binding_sha256",
        "state_arrays_retained",
        "input_provenance_classification",
        "uniformization_rate_denominator",
        "uniformization_rate_numerator",
    }
    if type(parsed) is not dict or set(parsed) != expected_keys:
        raise BatchedScalarFailure("serialized scalar series keys are invalid")
    record_keys = {
        "binding_sha256",
        "index",
        "lower_hex",
        "schema",
        "upper_hex",
    }
    raw_records = parsed["records"]
    if type(raw_records) is not list or not raw_records:
        raise BatchedScalarFailure("serialized scalar records are invalid")
    records: list[ScalarPowerRecord] = []
    for raw in raw_records:
        if type(raw) is not dict or set(raw) != record_keys:
            raise BatchedScalarFailure("serialized scalar record keys are invalid")
        records.append(
            ScalarPowerRecord(
                schema=raw["schema"],
                index=raw["index"],
                lower_hex=raw["lower_hex"],
                upper_hex=raw["upper_hex"],
                binding_sha256=raw["binding_sha256"],
            )
        )
    try:
        series = CanonicalScalarPowerSeries(
            schema=parsed["schema"],
            horizon_numerator=parsed["horizon_numerator"],
            horizon_denominator=parsed["horizon_denominator"],
            uniformization_rate_numerator=parsed["uniformization_rate_numerator"],
            uniformization_rate_denominator=parsed["uniformization_rate_denominator"],
            maximum_killing_upper_numerator=parsed[
                "maximum_killing_upper_numerator"
            ],
            maximum_killing_upper_denominator=parsed[
                "maximum_killing_upper_denominator"
            ],
            initial_mass_upper_numerator=parsed["initial_mass_upper_numerator"],
            initial_mass_upper_denominator=parsed["initial_mass_upper_denominator"],
            maximum_power_index=parsed["maximum_power_index"],
            records=tuple(records),
            scalar_stream_sha256=parsed["scalar_stream_sha256"],
            series_binding_sha256=parsed["series_binding_sha256"],
            state_arrays_retained=parsed["state_arrays_retained"],
            canonical_scalar_records_retained=parsed[
                "canonical_scalar_records_retained"
            ],
            input_provenance_classification=parsed[
                "input_provenance_classification"
            ],
            control_exclusion_proved=parsed["control_exclusion_proved"],
            science_free_proved=parsed["science_free_proved"],
            f0_pass=parsed["f0_pass"],
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise BatchedScalarFailure("serialized scalar series types are invalid") from error
    validate_canonical_scalar_power_series(series)
    if not hmac.compare_digest(
        payload,
        canonical_scalar_power_series_bytes(series),
    ):
        raise BatchedScalarFailure("serialized scalar series bytes are not canonical")
    return series


def _jet_payload(row: ScalarJetInterval) -> dict[str, object]:
    return {
        "lower_hex": row.lower_hex,
        "order": row.order,
        "schema": row.schema,
        "upper_hex": row.upper_hex,
    }


def _jet_binding(row: ScalarJetInterval) -> str:
    return _canonical_json_digest(_jet_payload(row))


def _magnitude_payload(row: ScalarMagnitudeBound) -> dict[str, object]:
    return {
        "formula": row.formula,
        "order": row.order,
        "schema": row.schema,
        "upper_hex": row.upper_hex,
    }


def _magnitude_binding(row: ScalarMagnitudeBound) -> str:
    return _canonical_json_digest(_magnitude_payload(row))


def _poisson_payload(row: CenteredPoissonLedger) -> dict[str, object]:
    return {
        "mean_denominator": row.mean_denominator,
        "mean_numerator": row.mean_numerator,
        "mode": row.mode,
        "mode_initialization_count": row.mode_initialization_count,
        "mode_initialized": row.mode_initialized,
        "p0_derived_from_mode": row.p0_derived_from_mode,
        "p0_back_recurrence_steps": row.p0_back_recurrence_steps,
        "planning_recurrence_steps": row.planning_recurrence_steps,
        "precision_bits": row.precision_bits,
        "requested_tail_denominator": row.requested_tail_denominator,
        "requested_tail_numerator": row.requested_tail_numerator,
        "right_index": row.right_index,
        "right_tail_geometric": row.right_tail_geometric,
        "right_tail_planning_steps": row.right_tail_planning_steps,
        "schema": row.schema,
        "starts_at_zero": row.starts_at_zero,
        "tail_upper_hex": row.tail_upper_hex,
        "terms": row.terms,
        "forward_weight_recurrence_steps": row.forward_weight_recurrence_steps,
    }


def _poisson_binding(row: CenteredPoissonLedger) -> str:
    return _canonical_json_digest(_poisson_payload(row))


def _time_payload(row: AbsoluteTimeScalarJets) -> dict[str, object]:
    return {
        "absolute_time_from_initial": row.absolute_time_from_initial,
        "jets": [
            {**_jet_payload(jet), "binding_sha256": jet.binding_sha256}
            for jet in row.jets
        ],
        "magnitudes": [
            {**_magnitude_payload(bound), "binding_sha256": bound.binding_sha256}
            for bound in row.magnitudes
        ],
        "poisson": {
            **_poisson_payload(row.poisson),
            "binding_sha256": row.poisson.binding_sha256,
        },
        "schema": row.schema,
        "state_chaining_used": row.state_chaining_used,
        "time_denominator": row.time_denominator,
        "time_numerator": row.time_numerator,
    }


def _time_binding(row: AbsoluteTimeScalarJets) -> str:
    return _canonical_json_digest(_time_payload(row))


def _resources_payload(row: BatchedScalarResources) -> dict[str, object]:
    return {
        field: getattr(row, field)
        for field in (
            "schema",
            "state_count",
            "block_size",
            "block_capacity",
            "time_count",
            "maximum_time_count",
            "maximum_power_index",
            "p_action_calls",
            "scalar_observable_calls",
            "maximum_poisson_terms_requested",
            "maximum_poisson_terms_used",
            "poisson_plan_count",
            "poisson_p0_back_recurrence_steps_total",
            "poisson_right_tail_planning_steps_total",
            "poisson_forward_weight_recurrence_steps_total",
            "mpfr_precision_bits",
            "full_state_vector_count",
            "maximum_simultaneous_full_state_vectors",
            "retained_full_power_count",
            "scalar_ring_capacity",
            "retained_numpy_scalar_power_array",
            "retained_scalar_power_record_count",
            "block_integer_workspace_bytes",
            "block_float_workspace_bytes",
            "block_boolean_workspace_bytes",
            "untracked_explicit_numpy_temporary_bytes",
            "fast_action_workspace_bytes",
            "state_vector_payload_bytes",
            "declared_peak_numeric_payload_bytes_excluding_preowned_kernel",
            "maximum_mpfr_object_count_upper",
            "mpfr_payload_bytes_measured",
            "bounded_memory_by_declared_counts",
            "action_roundoff_proof_complete",
            "coefficient_error_included",
            "reduction_roundoff_included",
            "poisson_roundoff_included",
            "poisson_tail_included",
            "production_scale_execution_classified",
            "production_resource_gate",
            "f0_pass",
        )
    }


def _receipt_payload(row: BatchedScalarReceipt) -> dict[str, object]:
    return {
        "absolute_time_from_initial": row.absolute_time_from_initial,
        "canonical_receipt": row.canonical_receipt,
        "declared_initial_mass_cap_precondition": (
            row.declared_initial_mass_cap_precondition
        ),
        "evaluations": [
            {**_time_payload(evaluation), "binding_sha256": evaluation.binding_sha256}
            for evaluation in row.evaluations
        ],
        "f0_pass": row.f0_pass,
        "final_power_raw_sha256": row.final_power_raw_sha256,
        "fresh_process": row.fresh_process,
        "independent_audit_complete": row.independent_audit_complete,
        "initial_input_binding_sha256": row.initial_input_binding_sha256,
        "input_provenance_classification": row.input_provenance_classification,
        "initial_mass_upper_denominator": row.initial_mass_upper_denominator,
        "initial_mass_upper_numerator": row.initial_mass_upper_numerator,
        "kernel_replay_sha256": row.kernel_replay_sha256,
        "maximum_killing_upper_denominator": row.maximum_killing_upper_denominator,
        "maximum_killing_upper_numerator": row.maximum_killing_upper_numerator,
        "maximum_state_radius_upper_hex": row.maximum_state_radius_upper_hex,
        "operation_model_sha256": row.operation_model_sha256,
        "control_exclusion_proved": row.control_exclusion_proved,
        "production_resource_gate": row.production_resource_gate,
        "production_scale_execution_classified": (
            row.production_scale_execution_classified
        ),
        "rate_action_contract_sha256": row.rate_action_contract_sha256,
        "resources": _resources_payload(row.resources),
        "runtime": row.runtime,
        "scalar_series": {
            "series_binding_sha256": row.scalar_series.series_binding_sha256,
            "scalar_stream_sha256": row.scalar_series.scalar_stream_sha256,
            "maximum_power_index": row.scalar_series.maximum_power_index,
            "schema": row.scalar_series.schema,
        },
        "scalar_stream_sha256": row.scalar_stream_sha256,
        "schema": row.schema,
        "science_free_proved": row.science_free_proved,
        "state_chaining_used": row.state_chaining_used,
        "status": row.status,
        "uniformization_rate_denominator": row.uniformization_rate_denominator,
        "uniformization_rate_numerator": row.uniformization_rate_numerator,
    }


def _receipt_binding(row: BatchedScalarReceipt) -> str:
    return _canonical_json_digest(_receipt_payload(row))


def _finalize_absolute_time_rows(
    *,
    times: tuple[Fraction, ...],
    states: list[_EvaluationState],
    rate: Fraction,
    killing_upper: Fraction,
    initial_mass_upper: Fraction,
    tolerance: Fraction,
    precision_bits: int,
) -> tuple[AbsoluteTimeScalarJets, ...]:
    rows: list[AbsoluteTimeScalarJets] = []
    rate_lower = _mpfr_from_fraction(rate, precision_bits, gmpy2.RoundDown)
    rate_upper = _mpfr_from_fraction(rate, precision_bits, gmpy2.RoundUp)
    scalar_global_upper = killing_upper * initial_mass_upper
    global_upper_upper = _mpfr_from_fraction(
        scalar_global_upper,
        precision_bits,
        gmpy2.RoundUp,
    )
    for time, state in zip(times, states, strict=True):
        jet_rows_all: list[ScalarJetInterval] = []
        magnitude_rows: list[ScalarMagnitudeBound] = []
        for order in range(MAXIMUM_JET_ORDER + 1):
            with gmpy2.context(
                gmpy2.get_context(),
                precision=precision_bits,
                round=gmpy2.RoundDown,
            ):
                scale_lower = rate_lower**order
            with gmpy2.context(
                gmpy2.get_context(),
                precision=precision_bits,
                round=gmpy2.RoundUp,
            ):
                scale_upper = rate_upper**order
                tail_upper_factor = (
                    scale_upper * (2**order) * global_upper_upper
                )
                tail_radius = tail_upper_factor * state.plan.tail_upper
            lower, upper = _multiply_signed_interval_by_nonnegative_interval(
                state.accumulator_lower[order],
                state.accumulator_upper[order],
                scale_lower,
                scale_upper,
                precision_bits=precision_bits,
            )
            with gmpy2.context(
                gmpy2.get_context(),
                precision=precision_bits,
                round=gmpy2.RoundUp,
            ):
                upper += tail_radius
            with gmpy2.context(
                gmpy2.get_context(),
                precision=precision_bits,
                round=gmpy2.RoundDown,
            ):
                lower -= tail_radius
                if order == 0 and lower < 0:
                    lower = gmpy2.mpfr(0)
            if order == 0:
                upper = min(upper, global_upper_upper)
            if lower > upper:
                raise BatchedScalarFailure("final scalar jet interval reversed")
            lower_float = _mpfr_to_float_lower(lower, precision_bits)
            upper_float = _mpfr_to_float_upper(upper, precision_bits)
            provisional_jet = ScalarJetInterval(
                schema=JET_SCHEMA,
                order=order,
                lower_hex=lower_float.hex(),
                upper_hex=upper_float.hex(),
                binding_sha256="0" * 64,
            )
            jet = replace(
                provisional_jet,
                binding_sha256=_jet_binding(provisional_jet),
            )
            jet_rows_all.append(jet)
            if order >= 2:
                magnitude_exact = (
                    killing_upper
                    * (2 * rate) ** order
                    * initial_mass_upper
                )
                magnitude = _fraction_to_float_upper(magnitude_exact)
                provisional_magnitude = ScalarMagnitudeBound(
                    schema=MAGNITUDE_SCHEMA,
                    order=order,
                    upper_hex=magnitude.hex(),
                    formula=MAGNITUDE_FORMULA,
                    binding_sha256="0" * 64,
                )
                magnitude_rows.append(
                    replace(
                        provisional_magnitude,
                        binding_sha256=_magnitude_binding(provisional_magnitude),
                    )
                )

        tail_float = _mpfr_to_float_upper(state.plan.tail_upper, precision_bits)
        provisional_poisson = CenteredPoissonLedger(
            schema=POISSON_SCHEMA,
            mean_numerator=state.plan.mean.numerator,
            mean_denominator=state.plan.mean.denominator,
            mode=state.plan.mode,
            right_index=state.plan.right_index,
            terms=state.plan.right_index + 1,
            tail_upper_hex=tail_float.hex(),
            requested_tail_numerator=tolerance.numerator,
            requested_tail_denominator=tolerance.denominator,
            precision_bits=precision_bits,
            mode_initialization_count=1,
            p0_back_recurrence_steps=state.plan.p0_back_recurrence_steps,
            right_tail_planning_steps=state.plan.right_tail_planning_steps,
            planning_recurrence_steps=(
                state.plan.p0_back_recurrence_steps
                + state.plan.right_tail_planning_steps
            ),
            forward_weight_recurrence_steps=state.plan.right_index,
            mode_initialized=True,
            p0_derived_from_mode=True,
            right_tail_geometric=True,
            starts_at_zero=True,
            binding_sha256="0" * 64,
        )
        poisson = replace(
            provisional_poisson,
            binding_sha256=_poisson_binding(provisional_poisson),
        )
        provisional_time = AbsoluteTimeScalarJets(
            schema=TIME_SCHEMA,
            time_numerator=time.numerator,
            time_denominator=time.denominator,
            poisson=poisson,
            jets=tuple(jet_rows_all[:4]),
            magnitudes=tuple(magnitude_rows),
            absolute_time_from_initial=True,
            state_chaining_used=False,
            binding_sha256="0" * 64,
        )
        rows.append(
            replace(
                provisional_time,
                binding_sha256=_time_binding(provisional_time),
            )
        )
    return tuple(rows)


def reevaluate_canonical_scalar_series(
    series: CanonicalScalarPowerSeries,
    *,
    times: tuple[Fraction, ...],
    tail_tolerance: Fraction,
    precision_bits: int = 192,
    maximum_terms: int = 200_000,
) -> tuple[AbsoluteTimeScalarJets, ...]:
    """Evaluate new exact times without repeating any full-state P action."""

    validate_canonical_scalar_power_series(series)
    if (
        type(times) is not tuple
        or not times
        or len(times) > MAXIMUM_BATCH_TIMES
        or any(type(time) is not Fraction or time < 0 for time in times)
        or tuple(sorted(set(times))) != times
    ):
        raise BatchedScalarFailure(
            "times must be a nonempty, unique, strictly increasing Fraction tuple"
        )
    for index, time in enumerate(times):
        _validate_fraction(time, label=f"reevaluation time {index}")
    horizon = _fraction_from_metadata(
        series.horizon_numerator,
        series.horizon_denominator,
        label="series horizon",
    )
    if times[-1] > horizon:
        raise BatchedScalarFailure("reevaluation time exceeds the frozen series horizon")
    tolerance = _validate_fraction(tail_tolerance, label="tail tolerance")
    if tolerance <= 0 or tolerance >= 1:
        raise BatchedScalarFailure("tail tolerance must lie strictly between zero and one")
    if (
        type(precision_bits) is not int
        or not MINIMUM_MPFR_PRECISION_BITS
        <= precision_bits
        <= MAXIMUM_MPFR_PRECISION_BITS
        or type(maximum_terms) is not int
        or not 1 <= maximum_terms <= MAXIMUM_POISSON_TERMS
    ):
        raise BatchedScalarFailure("MPFR precision or Poisson term cap is invalid")
    rate = _fraction_from_metadata(
        series.uniformization_rate_numerator,
        series.uniformization_rate_denominator,
        label="series rate",
    )
    killing_upper = _fraction_from_metadata(
        series.maximum_killing_upper_numerator,
        series.maximum_killing_upper_denominator,
        label="series killing upper",
    )
    initial_mass_upper = _fraction_from_metadata(
        series.initial_mass_upper_numerator,
        series.initial_mass_upper_denominator,
        label="series initial mass upper",
    )
    plans = tuple(
        _centered_poisson_plan(
            rate * time,
            tolerance,
            precision_bits=precision_bits,
            maximum_terms=maximum_terms,
        )
        for time in times
    )
    required_power = max(plan.right_index for plan in plans) + MAXIMUM_JET_ORDER
    if required_power > series.maximum_power_index:
        raise BatchedScalarFailure(
            "frozen scalar series is too short for the requested tail tolerance"
        )
    states = [_new_evaluation_state(plan, precision_bits) for plan in plans]
    scalar_ring: list[tuple[int, _ScalarInterval] | None] = [
        None for _ in range(SCALAR_RING_SIZE)
    ]
    for power_index in range(required_power + 1):
        record = series.records[power_index]
        scalar = _ScalarInterval(
            lower=_parse_hex(
                record.lower_hex,
                label="reevaluation scalar lower",
                nonnegative=True,
            ),
            upper=_parse_hex(
                record.upper_hex,
                label="reevaluation scalar upper",
                nonnegative=True,
            ),
        )
        scalar_ring[power_index % SCALAR_RING_SIZE] = (power_index, scalar)
        differences = tuple(
            _finite_difference_interval(
                scalar_ring,
                power_index=power_index,
                order=order,
                precision_bits=precision_bits,
            )
            for order in range(min(power_index, MAXIMUM_JET_ORDER) + 1)
        )
        for state in states:
            if power_index <= state.plan.right_index:
                if state.current_index != power_index:
                    raise BatchedScalarFailure("Poisson cursor lost its absolute index")
                state.weight_ring[power_index % SCALAR_RING_SIZE] = (
                    power_index,
                    gmpy2.mpfr(state.current_weight_lower),
                    gmpy2.mpfr(state.current_weight_upper),
                )
                if power_index < state.plan.right_index:
                    _advance_weight(state, precision_bits)
            for order, difference in enumerate(differences):
                base = power_index - order
                if base > state.plan.right_index:
                    continue
                weight_row = state.weight_ring[base % SCALAR_RING_SIZE]
                if weight_row is None or weight_row[0] != base:
                    raise BatchedScalarFailure("Poisson weight ring lost a predecessor")
                _accumulate_weighted_interval(
                    state,
                    order=order,
                    weight_lower=weight_row[1],
                    weight_upper=weight_row[2],
                    value_lower=difference[0],
                    value_upper=difference[1],
                    precision_bits=precision_bits,
                )
    return _finalize_absolute_time_rows(
        times=times,
        states=states,
        rate=rate,
        killing_upper=killing_upper,
        initial_mass_upper=initial_mass_upper,
        tolerance=tolerance,
        precision_bits=precision_bits,
    )


def validate_batched_scalar_receipt(receipt: BatchedScalarReceipt) -> None:
    """Revalidate all canonical method fields and nested content hashes."""

    if type(receipt) is not BatchedScalarReceipt:
        raise BatchedScalarFailure("receipt has the wrong exact type")
    digest_fields = (
        receipt.kernel_replay_sha256,
        receipt.initial_input_binding_sha256,
        receipt.rate_action_contract_sha256,
        receipt.operation_model_sha256,
        receipt.scalar_stream_sha256,
        receipt.final_power_raw_sha256,
        receipt.receipt_sha256,
    )
    receipt_integer_fields = (
        receipt.uniformization_rate_numerator,
        receipt.uniformization_rate_denominator,
        receipt.maximum_killing_upper_numerator,
        receipt.maximum_killing_upper_denominator,
        receipt.initial_mass_upper_numerator,
        receipt.initial_mass_upper_denominator,
    )
    if (
        receipt.schema != RECEIPT_SCHEMA
        or any(type(value) is not int for value in receipt_integer_fields)
        or any(not _is_sha256(value) for value in digest_fields)
        or receipt.operation_model_sha256 != _operation_model_sha256()
        or type(receipt.evaluations) is not tuple
        or not receipt.evaluations
        or type(receipt.scalar_series) is not CanonicalScalarPowerSeries
        or type(receipt.resources) is not BatchedScalarResources
        or receipt.runtime != _runtime_identity()
        or receipt.status != METHOD_STATUS
        or receipt.canonical_receipt is not True
        or receipt.declared_initial_mass_cap_precondition is not True
        or receipt.absolute_time_from_initial is not True
        or receipt.state_chaining_used is not False
        or receipt.input_provenance_classification
        != INPUT_PROVENANCE_CLASSIFICATION
        or receipt.control_exclusion_proved is not False
        or receipt.science_free_proved is not False
        or receipt.fresh_process is not False
        or receipt.independent_audit_complete is not False
        or receipt.production_scale_execution_classified is not False
        or receipt.production_resource_gate is not False
        or receipt.f0_pass is not False
    ):
        raise BatchedScalarFailure("receipt header is invalid")
    rate = _fraction_from_metadata(
        receipt.uniformization_rate_numerator,
        receipt.uniformization_rate_denominator,
        label="receipt rate",
    )
    killing_upper = _fraction_from_metadata(
        receipt.maximum_killing_upper_numerator,
        receipt.maximum_killing_upper_denominator,
        label="receipt killing upper",
    )
    initial_mass_upper = _fraction_from_metadata(
        receipt.initial_mass_upper_numerator,
        receipt.initial_mass_upper_denominator,
        label="receipt initial mass upper",
    )
    if rate <= 0 or killing_upper < 0 or not 0 <= initial_mass_upper <= 1:
        raise BatchedScalarFailure("receipt exact bounds are invalid")
    _parse_hex(
        receipt.maximum_state_radius_upper_hex,
        label="maximum state radius",
        nonnegative=True,
    )
    validate_canonical_scalar_power_series(receipt.scalar_series)
    if (
        receipt.scalar_series.scalar_stream_sha256 != receipt.scalar_stream_sha256
        or receipt.scalar_series.uniformization_rate_numerator != rate.numerator
        or receipt.scalar_series.uniformization_rate_denominator != rate.denominator
        or receipt.scalar_series.maximum_killing_upper_numerator
        != killing_upper.numerator
        or receipt.scalar_series.maximum_killing_upper_denominator
        != killing_upper.denominator
        or receipt.scalar_series.initial_mass_upper_numerator
        != initial_mass_upper.numerator
        or receipt.scalar_series.initial_mass_upper_denominator
        != initial_mass_upper.denominator
    ):
        raise BatchedScalarFailure("receipt and scalar series bindings disagree")

    previous_time: Fraction | None = None
    common_requested_tail: Fraction | None = None
    for row in receipt.evaluations:
        if type(row) is not AbsoluteTimeScalarJets or row.schema != TIME_SCHEMA:
            raise BatchedScalarFailure("time evaluation has the wrong exact type")
        time = _fraction_from_metadata(
            row.time_numerator,
            row.time_denominator,
            label="evaluation time",
        )
        if type(row.poisson) is not CenteredPoissonLedger:
            raise BatchedScalarFailure("Poisson ledger has the wrong exact type")
        poisson_integer_fields = (
            row.poisson.mean_numerator,
            row.poisson.mean_denominator,
            row.poisson.mode,
            row.poisson.right_index,
            row.poisson.terms,
            row.poisson.requested_tail_numerator,
            row.poisson.requested_tail_denominator,
            row.poisson.precision_bits,
            row.poisson.mode_initialization_count,
            row.poisson.p0_back_recurrence_steps,
            row.poisson.right_tail_planning_steps,
            row.poisson.planning_recurrence_steps,
            row.poisson.forward_weight_recurrence_steps,
        )
        if time < 0 or (previous_time is not None and time <= previous_time):
            raise BatchedScalarFailure("time evaluations are not strictly canonical")
        previous_time = time
        if (
            row.absolute_time_from_initial is not True
            or row.state_chaining_used is not False
            or row.poisson.schema != POISSON_SCHEMA
            or any(type(value) is not int for value in poisson_integer_fields)
            or row.poisson.mean_numerator != (rate * time).numerator
            or row.poisson.mean_denominator != (rate * time).denominator
            or row.poisson.mode != (rate * time).numerator // (rate * time).denominator
            or row.poisson.mode >= receipt.resources.maximum_poisson_terms_requested
            or row.poisson.right_index < row.poisson.mode
            or row.poisson.terms != row.poisson.right_index + 1
            or not MINIMUM_MPFR_PRECISION_BITS
            <= row.poisson.precision_bits
            <= MAXIMUM_MPFR_PRECISION_BITS
            or row.poisson.precision_bits != receipt.resources.mpfr_precision_bits
            or row.poisson.mode_initialization_count != 1
            or row.poisson.p0_back_recurrence_steps != row.poisson.mode
            or row.poisson.right_tail_planning_steps
            != (
                0
                if rate * time == 0
                else row.poisson.right_index - row.poisson.mode + 1
            )
            or row.poisson.planning_recurrence_steps
            != (
                row.poisson.p0_back_recurrence_steps
                + row.poisson.right_tail_planning_steps
            )
            or row.poisson.forward_weight_recurrence_steps
            != row.poisson.right_index
            or row.poisson.mode_initialized is not True
            or row.poisson.p0_derived_from_mode is not True
            or row.poisson.right_tail_geometric is not True
            or row.poisson.starts_at_zero is not True
            or row.poisson.binding_sha256 != _poisson_binding(row.poisson)
        ):
            raise BatchedScalarFailure("Poisson ledger is invalid")
        tail_upper = _parse_hex(
            row.poisson.tail_upper_hex,
            label="Poisson tail upper",
            nonnegative=True,
        )
        requested_tail = _fraction_from_metadata(
            row.poisson.requested_tail_numerator,
            row.poisson.requested_tail_denominator,
            label="Poisson requested tail",
        )
        if common_requested_tail is None:
            common_requested_tail = requested_tail
        if (
            not 0 < requested_tail < 1
            or requested_tail != common_requested_tail
            or Fraction.from_float(tail_upper) < 0
            or tail_upper > float(requested_tail) * (1 + 2**-48)
        ):
            raise BatchedScalarFailure("Poisson tail ledger is inconsistent")
        if (
            type(row.jets) is not tuple
            or tuple(jet.order for jet in row.jets) != (0, 1, 2, 3)
            or type(row.magnitudes) is not tuple
            or tuple(bound.order for bound in row.magnitudes) != (2, 3, 4)
        ):
            raise BatchedScalarFailure("scalar jet orders are invalid")
        for jet in row.jets:
            if (
                type(jet) is not ScalarJetInterval
                or jet.schema != JET_SCHEMA
                or type(jet.order) is not int
            ):
                raise BatchedScalarFailure("scalar jet has the wrong exact type")
            lower = _parse_hex(jet.lower_hex, label="jet lower")
            upper = _parse_hex(jet.upper_hex, label="jet upper")
            if lower > upper or jet.binding_sha256 != _jet_binding(jet):
                raise BatchedScalarFailure("scalar jet binding is invalid")
        for bound in row.magnitudes:
            if (
                type(bound) is not ScalarMagnitudeBound
                or bound.schema != MAGNITUDE_SCHEMA
                or type(bound.order) is not int
            ):
                raise BatchedScalarFailure("magnitude bound has the wrong exact type")
            _parse_hex(bound.upper_hex, label="magnitude upper", nonnegative=True)
            if (
                bound.formula != MAGNITUDE_FORMULA
                or bound.binding_sha256 != _magnitude_binding(bound)
            ):
                raise BatchedScalarFailure("magnitude binding is invalid")
        if row.binding_sha256 != _time_binding(row):
            raise BatchedScalarFailure("time evaluation binding is invalid")

    resources = receipt.resources
    resource_integer_fields = (
        resources.state_count,
        resources.block_size,
        resources.block_capacity,
        resources.time_count,
        resources.maximum_time_count,
        resources.maximum_power_index,
        resources.p_action_calls,
        resources.scalar_observable_calls,
        resources.maximum_poisson_terms_requested,
        resources.maximum_poisson_terms_used,
        resources.poisson_plan_count,
        resources.poisson_p0_back_recurrence_steps_total,
        resources.poisson_right_tail_planning_steps_total,
        resources.poisson_forward_weight_recurrence_steps_total,
        resources.mpfr_precision_bits,
        resources.full_state_vector_count,
        resources.maximum_simultaneous_full_state_vectors,
        resources.retained_full_power_count,
        resources.scalar_ring_capacity,
        resources.retained_scalar_power_record_count,
        resources.block_integer_workspace_bytes,
        resources.block_float_workspace_bytes,
        resources.block_boolean_workspace_bytes,
        resources.untracked_explicit_numpy_temporary_bytes,
        resources.fast_action_workspace_bytes,
        resources.state_vector_payload_bytes,
        resources.declared_peak_numeric_payload_bytes_excluding_preowned_kernel,
        resources.maximum_mpfr_object_count_upper,
    )
    if any(type(value) is not int for value in resource_integer_fields):
        raise BatchedScalarFailure("resource integer metadata has the wrong exact type")
    expected_capacity = min(resources.state_count, resources.block_size)
    horizon = _fraction_from_metadata(
        receipt.scalar_series.horizon_numerator,
        receipt.scalar_series.horizon_denominator,
        label="resource horizon",
    )
    horizon_mean = rate * horizon
    horizon_mode = horizon_mean.numerator // horizon_mean.denominator
    horizon_right_index = resources.maximum_power_index - MAXIMUM_JET_ORDER
    evaluation_p0_steps = sum(
        row.poisson.p0_back_recurrence_steps for row in receipt.evaluations
    )
    evaluation_right_steps = sum(
        row.poisson.right_tail_planning_steps for row in receipt.evaluations
    )
    evaluation_forward_steps = sum(
        row.poisson.forward_weight_recurrence_steps for row in receipt.evaluations
    )
    horizon_right_steps = (
        0 if horizon_mean == 0 else horizon_right_index - horizon_mode + 1
    )
    if (
        resources.schema != RESOURCE_SCHEMA
        or resources.state_count < 1
        or resources.block_size < 1
        or resources.block_capacity != expected_capacity
        or resources.time_count != len(receipt.evaluations)
        or not 1 <= resources.time_count <= resources.maximum_time_count
        or resources.maximum_time_count != MAXIMUM_BATCH_TIMES
        or resources.maximum_power_index != receipt.scalar_series.maximum_power_index
        or resources.p_action_calls != resources.maximum_power_index
        or resources.scalar_observable_calls != resources.maximum_power_index + 1
        or resources.maximum_poisson_terms_used
        != resources.maximum_power_index - MAXIMUM_JET_ORDER + 1
        or resources.poisson_plan_count != resources.time_count + 1
        or resources.poisson_p0_back_recurrence_steps_total
        != evaluation_p0_steps + horizon_mode
        or resources.poisson_right_tail_planning_steps_total
        != evaluation_right_steps + horizon_right_steps
        or resources.poisson_forward_weight_recurrence_steps_total
        != evaluation_forward_steps
        or not (
            resources.maximum_poisson_terms_used
            <= resources.maximum_poisson_terms_requested
            <= MAXIMUM_POISSON_TERMS
        )
        or resources.full_state_vector_count != 2
        or resources.maximum_simultaneous_full_state_vectors != 2
        or resources.retained_full_power_count != 1
        or resources.scalar_ring_capacity != SCALAR_RING_SIZE
        or resources.retained_numpy_scalar_power_array is not False
        or resources.retained_scalar_power_record_count
        != resources.maximum_power_index + 1
        or resources.retained_scalar_power_record_count
        != len(receipt.scalar_series.records)
        or receipt.scalar_series.maximum_power_index
        != resources.maximum_power_index
        or resources.fast_action_workspace_bytes <= 0
        or resources.block_integer_workspace_bytes != 40 * expected_capacity
        or resources.block_float_workspace_bytes != 24 * expected_capacity
        or resources.block_boolean_workspace_bytes != expected_capacity
        or resources.untracked_explicit_numpy_temporary_bytes != 0
        or resources.fast_action_workspace_bytes
        != (
            resources.block_integer_workspace_bytes
            + resources.block_float_workspace_bytes
            + resources.block_boolean_workspace_bytes
        )
        or resources.state_vector_payload_bytes != 16 * resources.state_count
        or resources.declared_peak_numeric_payload_bytes_excluding_preowned_kernel
        != resources.state_vector_payload_bytes + resources.fast_action_workspace_bytes
        or resources.maximum_mpfr_object_count_upper < 32 * resources.time_count
        or resources.mpfr_payload_bytes_measured is not False
        or resources.bounded_memory_by_declared_counts is not True
        or resources.action_roundoff_proof_complete is not True
        or resources.coefficient_error_included is not True
        or resources.reduction_roundoff_included is not True
        or resources.poisson_roundoff_included is not True
        or resources.poisson_tail_included is not True
        or resources.production_scale_execution_classified is not False
        or resources.production_resource_gate is not False
        or resources.f0_pass is not False
    ):
        raise BatchedScalarFailure("resource ledger is invalid")
    if not hmac.compare_digest(receipt.receipt_sha256, _receipt_binding(receipt)):
        raise BatchedScalarFailure("receipt content hash is invalid")


def evaluate_batched_scalar_jets(
    kernel: packed.PackedTensorKernel,
    initial: rate_action.InternalPointBallInput,
    contract: rate_action.RateActionContract,
    *,
    times: tuple[Fraction, ...],
    tail_tolerance: Fraction,
    initial_mass_cap: Fraction = Fraction(1),
    series_horizon: Fraction | None = None,
    precision_bits: int = 192,
    maximum_terms: int = 200_000,
) -> BatchedScalarReceipt:
    """Evaluate killing-observable jets at exact absolute times in one stream."""

    _verify_binary64_runtime()
    packed.validate_packed_tensor_kernel(kernel)
    rate_action.validate_internal_point_ball_input(initial)
    rate_action.validate_rate_action_contract(contract)
    if (
        kernel.contract.tensor_shape != contract.tensor_shape
        or kernel.contract.block_size != contract.block_size
        or initial.logical_shape != contract.tensor_shape
    ):
        raise BatchedScalarFailure("kernel, initial state, and contract disagree")
    if initial.nonnegative_nominal is not True:
        raise BatchedScalarFailure("the scalar power stream requires nonnegative nominal input")
    if (
        type(times) is not tuple
        or not times
        or len(times) > MAXIMUM_BATCH_TIMES
        or any(type(time) is not Fraction or time < 0 for time in times)
        or tuple(sorted(set(times))) != times
    ):
        raise BatchedScalarFailure(
            "times must be a nonempty, unique, strictly increasing Fraction tuple"
        )
    for index, time in enumerate(times):
        _validate_fraction(time, label=f"time {index}")
    horizon = times[-1] if series_horizon is None else _validate_fraction(
        series_horizon,
        label="scalar series horizon",
    )
    if horizon < times[-1]:
        raise BatchedScalarFailure("scalar series horizon precedes a requested time")
    tolerance = _validate_fraction(tail_tolerance, label="tail tolerance")
    declared_mass_cap = _validate_fraction(
        initial_mass_cap,
        label="declared initial mass cap",
    )
    if tolerance <= 0 or tolerance >= 1:
        raise BatchedScalarFailure("tail tolerance must lie strictly between zero and one")
    if declared_mass_cap <= 0 or declared_mass_cap > 1:
        raise BatchedScalarFailure("declared initial mass cap must lie in (0,1]")
    if (
        type(precision_bits) is not int
        or not MINIMUM_MPFR_PRECISION_BITS
        <= precision_bits
        <= MAXIMUM_MPFR_PRECISION_BITS
        or type(maximum_terms) is not int
        or not 1 <= maximum_terms <= MAXIMUM_POISSON_TERMS
    ):
        raise BatchedScalarFailure("MPFR precision or Poisson term cap is invalid")

    rate = kernel.rate_fraction
    if rate <= 0 or Fraction.from_float(kernel.rate) != rate:
        raise BatchedScalarFailure("uniformization rate is not a positive exact binary64")
    witnesses = {witness.name: witness.value for witness in kernel.ledger.witnesses}
    required_witnesses = (
        "delta_p_selected",
        "maximum_center_row_sum",
        "maximum_killing_upper",
        "maximum_killing_uncertainty",
    )
    if any(name not in witnesses for name in required_witnesses):
        raise BatchedScalarFailure("packed kernel is missing a scalar-stream witness")
    delta_p = witnesses["delta_p_selected"]
    center_row_sum = witnesses["maximum_center_row_sum"]
    killing_upper = witnesses["maximum_killing_upper"]
    killing_uncertainty = witnesses["maximum_killing_uncertainty"]
    if (
        delta_p < 0
        or not 0 <= center_row_sum <= 1
        or killing_upper < 0
        or killing_uncertainty < 0
    ):
        raise BatchedScalarFailure("packed scalar-stream witnesses are invalid")

    evaluation_plans = tuple(
        _centered_poisson_plan(
            rate * time,
            tolerance,
            precision_bits=precision_bits,
            maximum_terms=maximum_terms,
        )
        for time in times
    )
    horizon_plan = _centered_poisson_plan(
        rate * horizon,
        tolerance,
        precision_bits=precision_bits,
        maximum_terms=maximum_terms,
    )
    all_plans = (*evaluation_plans, horizon_plan)
    maximum_right = max(plan.right_index for plan in all_plans)
    maximum_power = maximum_right + MAXIMUM_JET_ORDER
    evaluation_states = [
        _new_evaluation_state(plan, precision_bits) for plan in evaluation_plans
    ]

    capacity = min(kernel.states, kernel.contract.block_size)
    workspace = _make_fast_workspace(capacity)
    current = np.array(initial.nominal, dtype=np.float64, copy=True, order="C")
    following = np.empty_like(current)
    if current.shape != (kernel.states,):
        raise BatchedScalarFailure("initial nominal state is invalid")
    _validate_nonnegative_vector_blocks(
        current,
        workspace,
        block_size=kernel.contract.block_size,
        label="initial nominal state",
    )
    initial_raw_before = _raw_sha256(initial.nominal)
    kernel_replay = packed._kernel_replay_digest(kernel)
    contract_digest = rate_action.rate_action_contract_sha256(contract)

    _positive_reduction_upper(
        current,
        workspace,
        block_size=kernel.contract.block_size,
    )
    state_radius = Fraction.from_float(initial.input_l1_radius_upper)
    # ``InternalPointBallInput`` is itself a declared method precondition, not
    # an authority object.  Its binary64 reduction interval can straddle an
    # exact cap (notably unit mass), so this layer records and uses the caller's
    # exact cap rather than silently inflating it above one.  A later F0
    # verifier must reconstruct that cap from the physical initial source.
    if state_radius > declared_mass_cap:
        raise BatchedScalarFailure("initial radius exceeds its declared mass cap")
    initial_mass_upper = declared_mass_cap
    scalar_global_upper = killing_upper * initial_mass_upper
    maximum_state_radius = state_radius

    dimensions = len(kernel.axes)
    action_gamma = _gamma(2 * dimensions + 1)
    action_underflow = kernel.states * (4 * dimensions + 1) * FLOAT64_ETA
    scalar_ring: list[tuple[int, _ScalarInterval] | None] = [
        None for _ in range(SCALAR_RING_SIZE)
    ]
    scalar_records: list[ScalarPowerRecord] = []
    stream_chain = hashlib.sha256(b"batched-scalar-power-stream-v1\x00")
    stream_chain.update(bytes.fromhex(kernel_replay))
    stream_chain.update(bytes.fromhex(initial.input_binding_sha256))
    stream_chain.update(bytes.fromhex(contract_digest))
    stream_chain.update(_fraction_text(rate).encode("ascii"))

    for power_index in range(maximum_power + 1):
        _, nominal_mass_upper = _positive_reduction_upper(
            current,
            workspace,
            block_size=kernel.contract.block_size,
        )
        scalar_nominal, scalar_dot_roundoff = _positive_dot_with_roundoff(
            kernel.killing_center,
            current,
            workspace,
            block_size=kernel.contract.block_size,
        )
        scalar_radius = (
            killing_upper * state_radius
            + killing_uncertainty * nominal_mass_upper
            + scalar_dot_roundoff
        )
        scalar_centre = Fraction.from_float(scalar_nominal)
        scalar_lower_exact = max(Fraction(0), scalar_centre - scalar_radius)
        scalar_upper_exact = min(
            scalar_global_upper,
            scalar_centre + scalar_radius,
        )
        if scalar_upper_exact < scalar_lower_exact:
            raise BatchedScalarFailure("scalar enclosure became empty")
        scalar = _ScalarInterval(
            lower=_fraction_to_float_lower(scalar_lower_exact),
            upper=_fraction_to_float_upper(scalar_upper_exact),
        )
        provisional_record = ScalarPowerRecord(
            schema=POWER_RECORD_SCHEMA,
            index=power_index,
            lower_hex=scalar.lower.hex(),
            upper_hex=scalar.upper.hex(),
            binding_sha256="0" * 64,
        )
        scalar_records.append(
            replace(
                provisional_record,
                binding_sha256=_power_record_binding(provisional_record),
            )
        )
        scalar_ring[power_index % SCALAR_RING_SIZE] = (power_index, scalar)
        stream_chain.update(
            struct.pack(
                ">Qdd",
                power_index,
                scalar.lower,
                scalar.upper,
            )
        )
        stream_chain.update(_fraction_text(state_radius).encode("ascii"))
        stream_chain.update(_fraction_text(nominal_mass_upper).encode("ascii"))

        differences = tuple(
            _finite_difference_interval(
                scalar_ring,
                power_index=power_index,
                order=order,
                precision_bits=precision_bits,
            )
            for order in range(min(power_index, MAXIMUM_JET_ORDER) + 1)
        )
        for state in evaluation_states:
            if power_index <= state.plan.right_index:
                if state.current_index != power_index:
                    raise BatchedScalarFailure("Poisson cursor lost its absolute index")
                state.weight_ring[power_index % SCALAR_RING_SIZE] = (
                    power_index,
                    gmpy2.mpfr(state.current_weight_lower),
                    gmpy2.mpfr(state.current_weight_upper),
                )
                if power_index < state.plan.right_index:
                    _advance_weight(state, precision_bits)
            for order, difference in enumerate(differences):
                base = power_index - order
                if base > state.plan.right_index:
                    continue
                weight_row = state.weight_ring[base % SCALAR_RING_SIZE]
                if weight_row is None or weight_row[0] != base:
                    raise BatchedScalarFailure("Poisson weight ring lost a predecessor")
                _accumulate_weighted_interval(
                    state,
                    order=order,
                    weight_lower=weight_row[1],
                    weight_upper=weight_row[2],
                    value_lower=difference[0],
                    value_upper=difference[1],
                    precision_bits=precision_bits,
                )

        if power_index < maximum_power:
            action_roundoff = (
                action_gamma * center_row_sum * nominal_mass_upper
                + action_underflow
            )
            state_radius = (
                state_radius
                + delta_p * nominal_mass_upper
                + action_roundoff
            )
            maximum_state_radius = max(maximum_state_radius, state_radius)
            _fast_p_transpose_into(kernel, current, following, workspace)
            current, following = following, current

    scalar_stream_sha256 = stream_chain.hexdigest()
    final_power_raw_sha256 = _raw_sha256(current)
    provisional_series = CanonicalScalarPowerSeries(
        schema=SERIES_SCHEMA,
        horizon_numerator=horizon.numerator,
        horizon_denominator=horizon.denominator,
        uniformization_rate_numerator=rate.numerator,
        uniformization_rate_denominator=rate.denominator,
        maximum_killing_upper_numerator=killing_upper.numerator,
        maximum_killing_upper_denominator=killing_upper.denominator,
        initial_mass_upper_numerator=initial_mass_upper.numerator,
        initial_mass_upper_denominator=initial_mass_upper.denominator,
        maximum_power_index=maximum_power,
        records=tuple(scalar_records),
        scalar_stream_sha256=scalar_stream_sha256,
        series_binding_sha256="0" * 64,
        state_arrays_retained=False,
        canonical_scalar_records_retained=True,
        input_provenance_classification=INPUT_PROVENANCE_CLASSIFICATION,
        control_exclusion_proved=False,
        science_free_proved=False,
        f0_pass=False,
    )
    scalar_series = replace(
        provisional_series,
        series_binding_sha256=_series_binding(provisional_series),
    )
    validate_canonical_scalar_power_series(scalar_series)
    evaluation_rows = _finalize_absolute_time_rows(
        times=times,
        states=evaluation_states,
        rate=rate,
        killing_upper=killing_upper,
        initial_mass_upper=initial_mass_upper,
        tolerance=tolerance,
        precision_bits=precision_bits,
    )

    resources = BatchedScalarResources(
        schema=RESOURCE_SCHEMA,
        state_count=kernel.states,
        block_size=kernel.contract.block_size,
        block_capacity=capacity,
        time_count=len(times),
        maximum_time_count=MAXIMUM_BATCH_TIMES,
        maximum_power_index=maximum_power,
        p_action_calls=maximum_power,
        scalar_observable_calls=maximum_power + 1,
        maximum_poisson_terms_requested=maximum_terms,
        maximum_poisson_terms_used=max(plan.right_index + 1 for plan in all_plans),
        mpfr_precision_bits=precision_bits,
        poisson_plan_count=len(all_plans),
        poisson_p0_back_recurrence_steps_total=sum(
            plan.p0_back_recurrence_steps for plan in all_plans
        ),
        poisson_right_tail_planning_steps_total=sum(
            plan.right_tail_planning_steps for plan in all_plans
        ),
        poisson_forward_weight_recurrence_steps_total=sum(
            plan.right_index for plan in evaluation_plans
        ),
        full_state_vector_count=2,
        maximum_simultaneous_full_state_vectors=2,
        retained_full_power_count=1,
        scalar_ring_capacity=SCALAR_RING_SIZE,
        retained_numpy_scalar_power_array=False,
        retained_scalar_power_record_count=len(scalar_records),
        fast_action_workspace_bytes=workspace.payload_bytes,
        block_integer_workspace_bytes=workspace.integer_payload_bytes,
        block_float_workspace_bytes=workspace.float_payload_bytes,
        block_boolean_workspace_bytes=workspace.boolean_payload_bytes,
        untracked_explicit_numpy_temporary_bytes=0,
        state_vector_payload_bytes=16 * kernel.states,
        declared_peak_numeric_payload_bytes_excluding_preowned_kernel=(
            16 * kernel.states + workspace.payload_bytes
        ),
        maximum_mpfr_object_count_upper=64 + 64 * len(times),
        mpfr_payload_bytes_measured=False,
        bounded_memory_by_declared_counts=True,
        action_roundoff_proof_complete=True,
        coefficient_error_included=True,
        reduction_roundoff_included=True,
        poisson_roundoff_included=True,
        poisson_tail_included=True,
        production_scale_execution_classified=False,
        production_resource_gate=False,
        f0_pass=False,
    )

    packed.validate_packed_tensor_kernel(kernel)
    rate_action.validate_internal_point_ball_input(initial)
    rate_action.validate_rate_action_contract(contract)
    if (
        not hmac.compare_digest(initial_raw_before, _raw_sha256(initial.nominal))
        or not hmac.compare_digest(kernel_replay, packed._kernel_replay_digest(kernel))
        or not hmac.compare_digest(
            contract_digest,
            rate_action.rate_action_contract_sha256(contract),
        )
    ):
        raise BatchedScalarFailure("caller-owned method inputs changed during the stream")
    provisional_receipt = BatchedScalarReceipt(
        schema=RECEIPT_SCHEMA,
        kernel_replay_sha256=kernel_replay,
        initial_input_binding_sha256=initial.input_binding_sha256,
        rate_action_contract_sha256=contract_digest,
        operation_model_sha256=_operation_model_sha256(),
        scalar_stream_sha256=scalar_stream_sha256,
        final_power_raw_sha256=final_power_raw_sha256,
        uniformization_rate_numerator=rate.numerator,
        uniformization_rate_denominator=rate.denominator,
        maximum_killing_upper_numerator=killing_upper.numerator,
        maximum_killing_upper_denominator=killing_upper.denominator,
        initial_mass_upper_numerator=initial_mass_upper.numerator,
        initial_mass_upper_denominator=initial_mass_upper.denominator,
        maximum_state_radius_upper_hex=_fraction_to_float_upper(
            maximum_state_radius
        ).hex(),
        scalar_series=scalar_series,
        evaluations=tuple(evaluation_rows),
        resources=resources,
        runtime=_runtime_identity(),
        status=METHOD_STATUS,
        canonical_receipt=True,
        declared_initial_mass_cap_precondition=True,
        absolute_time_from_initial=True,
        state_chaining_used=False,
        input_provenance_classification=INPUT_PROVENANCE_CLASSIFICATION,
        control_exclusion_proved=False,
        science_free_proved=False,
        fresh_process=False,
        independent_audit_complete=False,
        production_scale_execution_classified=False,
        production_resource_gate=False,
        f0_pass=False,
        receipt_sha256="0" * 64,
    )
    receipt = replace(
        provisional_receipt,
        receipt_sha256=_receipt_binding(provisional_receipt),
    )
    validate_batched_scalar_receipt(receipt)
    return receipt
