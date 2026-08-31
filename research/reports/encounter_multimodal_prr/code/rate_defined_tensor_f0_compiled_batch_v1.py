"""Caller-unclassified compiled power stream to canonical scalar series.

This module joins the strict compiled ``P.T`` power stream to the canonical
scalar-only persistence and absolute-time reevaluation layer.  It performs one
compiled stream call, retains no full power history, and reconstructs the same
conservative state/scalar radii used by the Python batched implementation.

The API deliberately accepts only numerical method metadata.  It has no role,
control, selector, scientific-budget, or authority argument.  Every input is
therefore caller supplied and unclassified.  In particular, a declared initial
mass cap and the coefficient witnesses are method preconditions, not facts
proved by this module.  No receipt produced here can authorize science,
topology, a resource PASS, or F0.
"""

from __future__ import annotations

import dataclasses
import hashlib
import hmac
import json
import math
import struct
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Final

import numpy as np

try:
    import rate_defined_tensor_f0_batched_scalar_uniformization_v1 as batched
    import rate_defined_tensor_f0_compiled_power_stream_v1 as compiled
except ImportError:  # pragma: no cover - package-style import fallback.
    from . import rate_defined_tensor_f0_batched_scalar_uniformization_v1 as batched
    from . import rate_defined_tensor_f0_compiled_power_stream_v1 as compiled


SCHEMA: Final = "rate_defined_tensor_f0_compiled_batch_v1"
METADATA_SCHEMA: Final = "rate_defined_tensor_f0_compiled_batch_metadata_v1"
PLAN_SCHEMA: Final = "rate_defined_tensor_f0_compiled_batch_poisson_plan_v1"
RESOURCE_SCHEMA: Final = "rate_defined_tensor_f0_compiled_batch_resources_v1"
RECEIPT_SCHEMA: Final = "rate_defined_tensor_f0_compiled_batch_receipt_v1"
EVIDENCE_SCHEMA: Final = "rate_defined_tensor_f0_compiled_batch_evidence_v1"
METHOD_STATUS: Final = "COMPILED_BATCH_METHOD_COMPLETE_NOT_F0"
INPUT_PROVENANCE_CLASSIFICATION: Final = (
    batched.INPUT_PROVENANCE_CLASSIFICATION
)
RETURNED_JET_ORDERS: Final = (0, 1, 2, 3)
MAXIMUM_FINITE_DIFFERENCE_ORDER: Final = batched.MAXIMUM_JET_ORDER
MAXIMUM_EVIDENCE_BYTES: Final = 512_000_000

_MODULE_PATH: Final = Path(__file__).resolve(strict=True)
_MODULE_SHA256_AT_IMPORT: Final = hashlib.sha256(
    _MODULE_PATH.read_bytes()
).hexdigest()
_BATCHED_SOURCE_PATH: Final = Path(batched.__file__).resolve(strict=True)
_BATCHED_SOURCE_SHA256_AT_IMPORT: Final = hashlib.sha256(
    _BATCHED_SOURCE_PATH.read_bytes()
).hexdigest()


class CompiledBatchFailure(RuntimeError):
    """Fail-closed method-layer error."""


@dataclass(frozen=True, slots=True)
class GenericCompiledBatchMethodMetadata:
    """Exact numerical preconditions with no authority-bearing vocabulary."""

    uniformization_rate: Fraction
    coefficient_l1_uncertainty_upper: Fraction
    maximum_center_row_sum: Fraction
    maximum_killing_upper: Fraction
    maximum_killing_uncertainty: Fraction
    initial_l1_radius_upper: Fraction
    initial_mass_cap: Fraction
    series_horizon: Fraction
    tail_tolerance: Fraction
    mpfr_precision_bits: int
    maximum_poisson_terms: int
    evaluation_times: tuple[Fraction, ...] = ()


@dataclass(frozen=True, slots=True)
class CompiledBatchPoissonPlanBinding:
    schema: str
    purpose: str
    time_numerator: int
    time_denominator: int
    mean_numerator: int
    mean_denominator: int
    mode: int
    right_index: int
    maximum_required_power_index: int
    tail_upper_hex: str
    requested_tail_numerator: int
    requested_tail_denominator: int
    precision_bits: int
    maximum_terms: int
    p0_back_recurrence_steps: int
    right_tail_planning_steps: int
    positive_mean_has_positive_tail: bool
    binding_sha256: str


@dataclass(frozen=True, slots=True)
class CompiledBatchResourceLedger:
    schema: str
    states: int
    dimensions: int
    maximum_power_index: int
    compiled_power_stream_run_count: int
    p_action_call_count: int
    mass_reduction_call_count: int
    killing_dot_call_count: int
    retained_full_power_history_count: int
    retained_final_full_state_vector_count: int
    maximum_simultaneous_float64_full_state_vectors_excluding_backend_and_caller: int
    compiled_scalar_stream_float64_payload_bytes: int
    compiled_final_state_float64_payload_bytes: int
    declared_compiled_peak_float64_payload_bytes_excluding_backend_and_caller: int
    canonical_scalar_record_count: int
    canonical_scalar_endpoint_payload_bytes: int
    evaluation_count: int
    evaluation_jet_count: int
    evaluation_magnitude_count: int
    evaluation_float_endpoint_payload_bytes: int
    maximum_evaluation_count: int
    python_object_overhead_measured: bool
    mpfr_payload_bytes_measured: bool
    validation_temporary_payload_bytes_measured: bool
    float64_stream_payload_formula_complete: bool
    complete_numeric_payload_ledger: bool
    complete_process_peak_measured: bool
    production_scale_execution_classified: bool
    resource_pass: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class CompiledBatchReceipt:
    schema: str
    status: str
    integration_source_sha256: str
    integration_source_observation_authoritative: bool
    independent_source_audit_complete: bool
    batched_scalar_source_sha256: str
    batched_scalar_runtime_identity: str
    metadata_binding_sha256: str
    initial_raw_sha256: str
    compiled_backend_receipt_sha256: str
    compiled_backend_receipt: compiled.CompiledBackendReceipt
    compiled_build_receipt: compiled.CompiledBuildReceipt
    compiled_stream_receipt: compiled.CompiledPowerStreamReceipt
    horizon_plan: CompiledBatchPoissonPlanBinding
    evaluation_plans: tuple[CompiledBatchPoissonPlanBinding, ...]
    scalar_stream_sha256: str
    canonical_series_binding_sha256: str
    canonical_series_bytes_sha256: str
    final_power_raw_sha256: str
    maximum_state_radius_upper_hex: str
    returned_jet_orders: tuple[int, ...]
    maximum_finite_difference_order: int
    compiled_power_stream_run_count: int
    absolute_time_reevaluation_used: bool
    repeated_p_actions_during_reevaluation: int
    resources: CompiledBatchResourceLedger
    input_provenance_classification: str
    method_metadata_preconditions_proved: bool
    initial_mass_cap_independently_proved: bool
    external_stream_replay_complete: bool
    control_exclusion_proved: bool
    science_free_proved: bool
    authorizes_scientific_execution: bool
    science_executed: bool
    topology_pass: bool
    production_scale_execution_classified: bool
    resource_pass: bool
    f0_pass: bool
    receipt_sha256: str


@dataclass(frozen=True, slots=True)
class CompiledCanonicalScalarSeriesResult:
    backend: compiled.CompiledPowerStreamBackend
    compiled_stream: compiled.CompiledPowerStreamResult
    metadata: GenericCompiledBatchMethodMetadata
    scalar_series: batched.CanonicalScalarPowerSeries
    evaluations: tuple[batched.AbsoluteTimeScalarJets, ...]
    receipt: CompiledBatchReceipt


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _raw_sha256(array: np.ndarray) -> str:
    return hashlib.sha256(memoryview(array).cast("B")).hexdigest()


def _canonical_json_bytes(payload: object) -> bytes:
    try:
        return json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise CompiledBatchFailure("canonical JSON encoding failed") from error


def _canonical_json_sha256(payload: object) -> str:
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def _builtin(value: object) -> object:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _builtin(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if type(value) is tuple:
        return [_builtin(item) for item in value]
    if type(value) is Fraction:
        return {
            "denominator": value.denominator,
            "numerator": value.numerator,
        }
    if type(value) in {str, int, bool} or value is None:
        return value
    raise CompiledBatchFailure("evidence contains a noncanonical value")


def _fraction_payload(value: Fraction) -> dict[str, int]:
    return {
        "denominator": value.denominator,
        "numerator": value.numerator,
    }


def _metadata_payload(
    metadata: GenericCompiledBatchMethodMetadata,
) -> dict[str, object]:
    return {
        "coefficient_l1_uncertainty_upper": _fraction_payload(
            metadata.coefficient_l1_uncertainty_upper
        ),
        "evaluation_times": [
            _fraction_payload(value) for value in metadata.evaluation_times
        ],
        "initial_l1_radius_upper": _fraction_payload(
            metadata.initial_l1_radius_upper
        ),
        "initial_mass_cap": _fraction_payload(metadata.initial_mass_cap),
        "maximum_center_row_sum": _fraction_payload(
            metadata.maximum_center_row_sum
        ),
        "maximum_killing_uncertainty": _fraction_payload(
            metadata.maximum_killing_uncertainty
        ),
        "maximum_killing_upper": _fraction_payload(
            metadata.maximum_killing_upper
        ),
        "maximum_poisson_terms": metadata.maximum_poisson_terms,
        "mpfr_precision_bits": metadata.mpfr_precision_bits,
        "schema": METADATA_SCHEMA,
        "series_horizon": _fraction_payload(metadata.series_horizon),
        "tail_tolerance": _fraction_payload(metadata.tail_tolerance),
        "uniformization_rate": _fraction_payload(
            metadata.uniformization_rate
        ),
    }


def _metadata_binding(metadata: GenericCompiledBatchMethodMetadata) -> str:
    return _canonical_json_sha256(_metadata_payload(metadata))


def _validate_fraction(
    value: object,
    *,
    label: str,
    nonnegative: bool = True,
) -> Fraction:
    if type(value) is not Fraction:
        raise CompiledBatchFailure(f"{label} must be an exact Fraction")
    if nonnegative and value < 0:
        raise CompiledBatchFailure(f"{label} must be nonnegative")
    if (
        abs(value.numerator).bit_length() > batched.MAXIMUM_EXACT_INTEGER_BITS
        or value.denominator.bit_length() > batched.MAXIMUM_EXACT_INTEGER_BITS
    ):
        raise CompiledBatchFailure(f"{label} exceeds the exact-integer cap")
    return value


def validate_generic_compiled_batch_metadata(
    metadata: GenericCompiledBatchMethodMetadata,
) -> None:
    """Validate syntax and bounded method preconditions without promoting them."""

    if type(metadata) is not GenericCompiledBatchMethodMetadata:
        raise CompiledBatchFailure("compiled batch metadata has the wrong exact type")
    exact_fields = (
        ("uniformization rate", metadata.uniformization_rate),
        (
            "coefficient l1 uncertainty",
            metadata.coefficient_l1_uncertainty_upper,
        ),
        ("maximum center row sum", metadata.maximum_center_row_sum),
        ("maximum killing upper", metadata.maximum_killing_upper),
        (
            "maximum killing uncertainty",
            metadata.maximum_killing_uncertainty,
        ),
        ("initial l1 radius", metadata.initial_l1_radius_upper),
        ("initial mass cap", metadata.initial_mass_cap),
        ("series horizon", metadata.series_horizon),
        ("tail tolerance", metadata.tail_tolerance),
    )
    for label, value in exact_fields:
        _validate_fraction(value, label=label)
    if (
        metadata.uniformization_rate <= 0
        or Fraction.from_float(float(metadata.uniformization_rate))
        != metadata.uniformization_rate
        or not 0 <= metadata.maximum_center_row_sum <= 1
        or metadata.maximum_killing_uncertainty
        > metadata.maximum_killing_upper
        or not 0 < metadata.initial_mass_cap <= 1
        or metadata.initial_l1_radius_upper > metadata.initial_mass_cap
        or not 0 < metadata.tail_tolerance < 1
        or type(metadata.mpfr_precision_bits) is not int
        or not batched.MINIMUM_MPFR_PRECISION_BITS
        <= metadata.mpfr_precision_bits
        <= batched.MAXIMUM_MPFR_PRECISION_BITS
        or type(metadata.maximum_poisson_terms) is not int
        or not 1
        <= metadata.maximum_poisson_terms
        <= batched.MAXIMUM_POISSON_TERMS
        or type(metadata.evaluation_times) is not tuple
        or len(metadata.evaluation_times) > batched.MAXIMUM_BATCH_TIMES
        or any(
            type(value) is not Fraction or value < 0
            for value in metadata.evaluation_times
        )
        or tuple(sorted(set(metadata.evaluation_times)))
        != metadata.evaluation_times
        or (
            metadata.evaluation_times
            and metadata.evaluation_times[-1] > metadata.series_horizon
        )
    ):
        raise CompiledBatchFailure("compiled batch metadata is invalid")
    for index, value in enumerate(metadata.evaluation_times):
        _validate_fraction(value, label=f"evaluation time {index}")


def _plan_payload(
    row: CompiledBatchPoissonPlanBinding,
) -> dict[str, object]:
    return {
        field.name: getattr(row, field.name)
        for field in dataclasses.fields(row)
        if field.name != "binding_sha256"
    }


def _plan_binding(row: CompiledBatchPoissonPlanBinding) -> str:
    return _canonical_json_sha256(_plan_payload(row))


def _make_plan_binding(
    metadata: GenericCompiledBatchMethodMetadata,
    *,
    purpose: str,
    time: Fraction,
) -> CompiledBatchPoissonPlanBinding:
    mean = metadata.uniformization_rate * time
    plan = batched._centered_poisson_plan(
        mean,
        metadata.tail_tolerance,
        precision_bits=metadata.mpfr_precision_bits,
        maximum_terms=metadata.maximum_poisson_terms,
    )
    if (
        plan.mean != mean
        or type(plan.mode) is not int
        or type(plan.right_index) is not int
        or plan.right_index < plan.mode
        or plan.right_index + MAXIMUM_FINITE_DIFFERENCE_ORDER
        > compiled.MAXIMUM_POWER_INDEX
        or plan.tail_upper < 0
        or (mean > 0 and plan.tail_upper <= 0)
    ):
        raise CompiledBatchFailure("Poisson plan failed integration invariants")
    tail_upper = batched._mpfr_to_float_upper(
        plan.tail_upper,
        metadata.mpfr_precision_bits,
    )
    provisional = CompiledBatchPoissonPlanBinding(
        schema=PLAN_SCHEMA,
        purpose=purpose,
        time_numerator=time.numerator,
        time_denominator=time.denominator,
        mean_numerator=mean.numerator,
        mean_denominator=mean.denominator,
        mode=plan.mode,
        right_index=plan.right_index,
        maximum_required_power_index=(
            plan.right_index + MAXIMUM_FINITE_DIFFERENCE_ORDER
        ),
        tail_upper_hex=tail_upper.hex(),
        requested_tail_numerator=metadata.tail_tolerance.numerator,
        requested_tail_denominator=metadata.tail_tolerance.denominator,
        precision_bits=metadata.mpfr_precision_bits,
        maximum_terms=metadata.maximum_poisson_terms,
        p0_back_recurrence_steps=plan.p0_back_recurrence_steps,
        right_tail_planning_steps=plan.right_tail_planning_steps,
        positive_mean_has_positive_tail=(mean == 0 or plan.tail_upper > 0),
        binding_sha256="0" * 64,
    )
    return replace(provisional, binding_sha256=_plan_binding(provisional))


def _gamma(index: int) -> Fraction:
    if type(index) is not int or not 0 <= index < 2**53:
        raise CompiledBatchFailure("roundoff gamma index is invalid")
    return Fraction(index, 2**53 - index) if index else Fraction(0)


def _validate_backend_method_ledgers(
    backend: compiled.CompiledPowerStreamBackend,
) -> None:
    """Independently reconstruct every formula-critical compiled ledger field."""

    if type(backend) is not compiled.CompiledPowerStreamBackend:
        raise CompiledBatchFailure("compiled backend has the wrong exact type")
    receipt = backend.receipt
    shape = receipt.tensor_shape
    periodic = receipt.periodic
    block_size = receipt.reduction_block_size
    if (
        type(shape) is not tuple
        or not shape
        or any(type(size) is not int or size < 2 for size in shape)
        or type(periodic) is not tuple
        or len(periodic) != len(shape)
        or any(type(value) is not bool for value in periodic)
        or type(receipt.states) is not int
        or receipt.states != math.prod(shape)
        or type(receipt.dimensions) is not int
        or receipt.dimensions != len(shape)
        or type(block_size) is not int
        or block_size < 1
    ):
        raise CompiledBatchFailure("compiled backend topology header is invalid")
    private_shape = backend._shape
    private_periodic = backend._periodic
    private_arrays = (
        backend._p_self,
        backend._killing,
        *backend._p_forward,
        *backend._p_backward,
    )
    if (
        type(private_shape) is not np.ndarray
        or private_shape.dtype != np.dtype(np.uintp)
        or tuple(int(value) for value in private_shape) != shape
        or type(private_periodic) is not np.ndarray
        or private_periodic.dtype != np.dtype(np.uint8)
        or tuple(bool(value) for value in private_periodic) != periodic
        or len(backend._p_forward) != len(shape)
        or len(backend._p_backward) != len(shape)
        or any(type(value) is not np.ndarray for value in private_arrays)
        or backend._p_self.shape != (receipt.states,)
        or backend._killing.shape != (receipt.states,)
        or tuple(value.shape for value in backend._p_forward)
        != tuple((size,) for size in shape)
        or tuple(value.shape for value in backend._p_backward)
        != tuple((size,) for size in shape)
    ):
        raise CompiledBatchFailure("compiled backend private topology drifted")
    states = receipt.states
    dimensions = receipt.dimensions
    present_edges = (
        sum(
            states if is_periodic else states - states // size
            for size, is_periodic in zip(shape, periodic, strict=True)
        )
        * 2
    )
    additions = 2 * dimensions * states
    conservative = states * (4 * dimensions + 1)
    expected_action = compiled.ActionOperationLedger(
        schema=compiled.ACTION_LEDGER_SCHEMA,
        states=states,
        dimensions=dimensions,
        self_multiplication_count=states,
        present_incoming_edge_count=present_edges,
        present_incoming_multiplication_count=present_edges,
        accumulator_addition_count=additions,
        actual_arithmetic_operation_count=states + present_edges + additions,
        conservative_arithmetic_operation_budget=conservative,
        maximum_dependency_operation_count=2 * dimensions + 1,
        underflow_event_operation_budget=conservative,
        underflow_unit_hex="0x0.0000000000001p-1022",
        accumulation_order=compiled.ACCUMULATION_ORDER,
        relative_error_model=(
            "gamma_(2*d+1)_per_nonnegative_contribution_path_v1"
        ),
        underflow_error_model="N*(4*d+1)*2^-1074_v1",
        changes_upstream_enclosure=False,
    )
    blocks = (states + block_size - 1) // block_size
    expected_mass = compiled.ReductionOperationLedger(
        schema=compiled.REDUCTION_LEDGER_SCHEMA,
        reduction="positive_mass",
        states=states,
        block_size=block_size,
        block_count=blocks,
        multiplication_count=0,
        addition_count=states,
        actual_arithmetic_operation_count=states,
        upstream_enclosure_operation_count=states + blocks,
        maximum_dependency_operation_count=states,
        underflow_event_operation_budget=states + blocks,
        underflow_unit_hex="0x0.0000000000001p-1022",
        accumulation_order="strict_flat_index_left_to_right_v1",
        changes_upstream_enclosure=False,
    )
    expected_dot = compiled.ReductionOperationLedger(
        schema=compiled.REDUCTION_LEDGER_SCHEMA,
        reduction="positive_killing_dot",
        states=states,
        block_size=block_size,
        block_count=blocks,
        multiplication_count=states,
        addition_count=states,
        actual_arithmetic_operation_count=2 * states,
        upstream_enclosure_operation_count=2 * states + blocks,
        maximum_dependency_operation_count=states + 1,
        underflow_event_operation_budget=2 * states + blocks,
        underflow_unit_hex="0x0.0000000000001p-1022",
        accumulation_order="strict_flat_index_multiply_then_left_to_right_add_v1",
        changes_upstream_enclosure=False,
    )
    if (
        type(receipt.action_operations) is not compiled.ActionOperationLedger
        or receipt.action_operations != expected_action
        or type(receipt.mass_reduction_operations)
        is not compiled.ReductionOperationLedger
        or receipt.mass_reduction_operations != expected_mass
        or type(receipt.killing_dot_operations)
        is not compiled.ReductionOperationLedger
        or receipt.killing_dot_operations != expected_dot
    ):
        raise CompiledBatchFailure(
            "compiled backend operation ledgers failed independent replay"
        )


def _positive_reduction_upper(nominal: float, operations: int) -> Fraction:
    if (
        type(nominal) is not float
        or not math.isfinite(nominal)
        or nominal < 0
        or type(operations) is not int
        or operations < 0
    ):
        raise CompiledBatchFailure("positive reduction row is invalid")
    gamma = _gamma(operations)
    underflow = operations * batched.FLOAT64_ETA
    return (Fraction.from_float(nominal) + underflow) / (1 - gamma)


def _positive_dot_radius(nominal: float, operations: int) -> Fraction:
    exact_upper = _positive_reduction_upper(nominal, operations)
    gamma = _gamma(operations)
    underflow = operations * batched.FLOAT64_ETA
    return gamma * exact_upper + underflow


def _construct_scalar_series(
    backend: compiled.CompiledPowerStreamBackend,
    stream: compiled.CompiledPowerStreamResult,
    metadata: GenericCompiledBatchMethodMetadata,
    *,
    metadata_binding_sha256: str,
) -> tuple[batched.CanonicalScalarPowerSeries, Fraction]:
    compiled.validate_compiled_power_stream_result(backend, stream)
    _validate_backend_method_ledgers(backend)
    maximum_power = stream.receipt.maximum_power_index
    horizon_plan = _make_plan_binding(
        metadata,
        purpose="series_horizon",
        time=metadata.series_horizon,
    )
    if horizon_plan.maximum_required_power_index != maximum_power:
        raise CompiledBatchFailure("compiled stream length does not match horizon plan")
    backend_receipt = backend.receipt
    mass_operations = (
        backend_receipt.mass_reduction_operations.upstream_enclosure_operation_count
    )
    dot_operations = (
        backend_receipt.killing_dot_operations.upstream_enclosure_operation_count
    )
    action_gamma = _gamma(
        backend_receipt.action_operations.maximum_dependency_operation_count
    )
    action_underflow = (
        backend_receipt.action_operations.underflow_event_operation_budget
        * batched.FLOAT64_ETA
    )
    state_radius = metadata.initial_l1_radius_upper
    maximum_state_radius = state_radius
    scalar_global_upper = (
        metadata.maximum_killing_upper * metadata.initial_mass_cap
    )
    records: list[batched.ScalarPowerRecord] = []
    stream_chain = hashlib.sha256(b"compiled-batch-scalar-power-stream-v1\x00")
    stream_chain.update(bytes.fromhex(backend_receipt.receipt_sha256))
    stream_chain.update(bytes.fromhex(stream.receipt.stream_binding_sha256))
    stream_chain.update(bytes.fromhex(metadata_binding_sha256))
    stream_chain.update(
        f"{metadata.uniformization_rate.numerator}/"
        f"{metadata.uniformization_rate.denominator}".encode("ascii")
    )
    for power_index in range(maximum_power + 1):
        mass_nominal = float(stream.mass_by_power[power_index])
        dot_nominal = float(stream.killing_dot_by_power[power_index])
        nominal_mass_upper = _positive_reduction_upper(
            mass_nominal,
            mass_operations,
        )
        dot_radius = _positive_dot_radius(dot_nominal, dot_operations)
        scalar_radius = (
            metadata.maximum_killing_upper * state_radius
            + metadata.maximum_killing_uncertainty * nominal_mass_upper
            + dot_radius
        )
        scalar_centre = Fraction.from_float(dot_nominal)
        lower_exact = max(Fraction(0), scalar_centre - scalar_radius)
        upper_exact = min(
            scalar_global_upper,
            scalar_centre + scalar_radius,
        )
        if upper_exact < lower_exact:
            raise CompiledBatchFailure("compiled scalar enclosure became empty")
        lower = batched._fraction_to_float_lower(lower_exact)
        upper = batched._fraction_to_float_upper(upper_exact)
        provisional_record = batched.ScalarPowerRecord(
            schema=batched.POWER_RECORD_SCHEMA,
            index=power_index,
            lower_hex=lower.hex(),
            upper_hex=upper.hex(),
            binding_sha256="0" * 64,
        )
        records.append(
            replace(
                provisional_record,
                binding_sha256=batched._power_record_binding(
                    provisional_record
                ),
            )
        )
        stream_chain.update(
            struct.pack(
                ">Qdd",
                power_index,
                lower,
                upper,
            )
        )
        stream_chain.update(
            (
                f"{state_radius.numerator}/{state_radius.denominator}"
            ).encode("ascii")
        )
        stream_chain.update(
            (
                f"{nominal_mass_upper.numerator}/"
                f"{nominal_mass_upper.denominator}"
            ).encode("ascii")
        )
        if power_index < maximum_power:
            action_roundoff = (
                action_gamma
                * metadata.maximum_center_row_sum
                * nominal_mass_upper
                + action_underflow
            )
            state_radius = (
                state_radius
                + metadata.coefficient_l1_uncertainty_upper
                * nominal_mass_upper
                + action_roundoff
            )
            maximum_state_radius = max(maximum_state_radius, state_radius)
    provisional_series = batched.CanonicalScalarPowerSeries(
        schema=batched.SERIES_SCHEMA,
        horizon_numerator=metadata.series_horizon.numerator,
        horizon_denominator=metadata.series_horizon.denominator,
        uniformization_rate_numerator=metadata.uniformization_rate.numerator,
        uniformization_rate_denominator=metadata.uniformization_rate.denominator,
        maximum_killing_upper_numerator=(
            metadata.maximum_killing_upper.numerator
        ),
        maximum_killing_upper_denominator=(
            metadata.maximum_killing_upper.denominator
        ),
        initial_mass_upper_numerator=metadata.initial_mass_cap.numerator,
        initial_mass_upper_denominator=metadata.initial_mass_cap.denominator,
        maximum_power_index=maximum_power,
        records=tuple(records),
        scalar_stream_sha256=stream_chain.hexdigest(),
        series_binding_sha256="0" * 64,
        state_arrays_retained=False,
        canonical_scalar_records_retained=True,
        input_provenance_classification=INPUT_PROVENANCE_CLASSIFICATION,
        control_exclusion_proved=False,
        science_free_proved=False,
        f0_pass=False,
    )
    series = replace(
        provisional_series,
        series_binding_sha256=batched._series_binding(provisional_series),
    )
    batched.validate_canonical_scalar_power_series(series)
    return series, maximum_state_radius


def _make_resource_ledger(
    backend: compiled.CompiledPowerStreamBackend,
    stream: compiled.CompiledPowerStreamResult,
    series: batched.CanonicalScalarPowerSeries,
    evaluations: tuple[batched.AbsoluteTimeScalarJets, ...],
) -> CompiledBatchResourceLedger:
    states = backend.states
    maximum_power = stream.receipt.maximum_power_index
    scalar_stream_bytes = 2 * (maximum_power + 1) * np.dtype(np.float64).itemsize
    final_state_bytes = states * np.dtype(np.float64).itemsize
    jet_count = sum(len(row.jets) for row in evaluations)
    magnitude_count = sum(len(row.magnitudes) for row in evaluations)
    return CompiledBatchResourceLedger(
        schema=RESOURCE_SCHEMA,
        states=states,
        dimensions=backend.receipt.dimensions,
        maximum_power_index=maximum_power,
        compiled_power_stream_run_count=1,
        p_action_call_count=stream.receipt.p_action_call_count,
        mass_reduction_call_count=stream.receipt.mass_reduction_call_count,
        killing_dot_call_count=stream.receipt.killing_dot_call_count,
        retained_full_power_history_count=0,
        retained_final_full_state_vector_count=1,
        maximum_simultaneous_float64_full_state_vectors_excluding_backend_and_caller=4,
        compiled_scalar_stream_float64_payload_bytes=scalar_stream_bytes,
        compiled_final_state_float64_payload_bytes=final_state_bytes,
        declared_compiled_peak_float64_payload_bytes_excluding_backend_and_caller=(
            4 * final_state_bytes + scalar_stream_bytes
        ),
        canonical_scalar_record_count=len(series.records),
        canonical_scalar_endpoint_payload_bytes=16 * len(series.records),
        evaluation_count=len(evaluations),
        evaluation_jet_count=jet_count,
        evaluation_magnitude_count=magnitude_count,
        evaluation_float_endpoint_payload_bytes=(
            16 * jet_count + 8 * magnitude_count
        ),
        maximum_evaluation_count=batched.MAXIMUM_BATCH_TIMES,
        python_object_overhead_measured=False,
        mpfr_payload_bytes_measured=False,
        validation_temporary_payload_bytes_measured=False,
        float64_stream_payload_formula_complete=True,
        complete_numeric_payload_ledger=False,
        complete_process_peak_measured=False,
        production_scale_execution_classified=False,
        resource_pass=False,
        f0_pass=False,
    )


def _receipt_payload(receipt: CompiledBatchReceipt) -> dict[str, object]:
    return {
        field.name: _builtin(getattr(receipt, field.name))
        for field in dataclasses.fields(receipt)
        if field.name != "receipt_sha256"
    }


def _receipt_binding(receipt: CompiledBatchReceipt) -> str:
    return _canonical_json_sha256(_receipt_payload(receipt))


def build_compiled_canonical_scalar_series(
    backend: compiled.CompiledPowerStreamBackend,
    initial: np.ndarray,
    metadata: GenericCompiledBatchMethodMetadata,
) -> CompiledCanonicalScalarSeriesResult:
    """Run one compiled stream and construct reusable J0--J3 evidence."""

    if type(backend) is not compiled.CompiledPowerStreamBackend:
        raise CompiledBatchFailure("compiled backend has the wrong exact type")
    if (
        type(initial) is not np.ndarray
        or initial.dtype != np.dtype(np.float64)
        or not initial.dtype.isnative
        or initial.shape != (backend.states,)
        or not initial.flags.c_contiguous
        or not initial.flags.aligned
        or not bool(np.all(np.isfinite(initial)))
        or bool(np.any(initial < 0))
    ):
        raise CompiledBatchFailure(
            "initial must be a finite nonnegative contiguous native float64 ndarray"
        )
    validate_generic_compiled_batch_metadata(metadata)
    backend.validate()
    _validate_backend_method_ledgers(backend)
    if (
        hashlib.sha256(_MODULE_PATH.read_bytes()).hexdigest()
        != _MODULE_SHA256_AT_IMPORT
        or hashlib.sha256(_BATCHED_SOURCE_PATH.read_bytes()).hexdigest()
        != _BATCHED_SOURCE_SHA256_AT_IMPORT
    ):
        raise CompiledBatchFailure(
            "integration or batched dependency changed after module import"
        )
    initial_hash = _raw_sha256(initial)
    metadata_hash = _metadata_binding(metadata)
    horizon_plan = _make_plan_binding(
        metadata,
        purpose="series_horizon",
        time=metadata.series_horizon,
    )
    evaluation_plans = tuple(
        _make_plan_binding(
            metadata,
            purpose=f"evaluation_{index}",
            time=time,
        )
        for index, time in enumerate(metadata.evaluation_times)
    )
    maximum_power = horizon_plan.maximum_required_power_index
    stream = backend.run_power_stream(
        initial,
        maximum_power=maximum_power,
    )
    if _raw_sha256(initial) != initial_hash:
        raise CompiledBatchFailure("caller initial changed during compiled execution")
    series, maximum_state_radius = _construct_scalar_series(
        backend,
        stream,
        metadata,
        metadata_binding_sha256=metadata_hash,
    )
    evaluations = (
        batched.reevaluate_canonical_scalar_series(
            series,
            times=metadata.evaluation_times,
            tail_tolerance=metadata.tail_tolerance,
            precision_bits=metadata.mpfr_precision_bits,
            maximum_terms=metadata.maximum_poisson_terms,
        )
        if metadata.evaluation_times
        else ()
    )
    resources = _make_resource_ledger(
        backend,
        stream,
        series,
        evaluations,
    )
    series_bytes = batched.canonical_scalar_power_series_bytes(series)
    provisional_receipt = CompiledBatchReceipt(
        schema=RECEIPT_SCHEMA,
        status=METHOD_STATUS,
        integration_source_sha256=_MODULE_SHA256_AT_IMPORT,
        integration_source_observation_authoritative=False,
        independent_source_audit_complete=False,
        batched_scalar_source_sha256=_BATCHED_SOURCE_SHA256_AT_IMPORT,
        batched_scalar_runtime_identity=batched._runtime_identity(),
        metadata_binding_sha256=metadata_hash,
        initial_raw_sha256=initial_hash,
        compiled_backend_receipt_sha256=backend.receipt.receipt_sha256,
        compiled_backend_receipt=backend.receipt,
        compiled_build_receipt=backend.receipt.build,
        compiled_stream_receipt=stream.receipt,
        horizon_plan=horizon_plan,
        evaluation_plans=evaluation_plans,
        scalar_stream_sha256=series.scalar_stream_sha256,
        canonical_series_binding_sha256=series.series_binding_sha256,
        canonical_series_bytes_sha256=hashlib.sha256(series_bytes).hexdigest(),
        final_power_raw_sha256=stream.receipt.final_power_raw_sha256,
        maximum_state_radius_upper_hex=(
            batched._fraction_to_float_upper(maximum_state_radius).hex()
        ),
        returned_jet_orders=RETURNED_JET_ORDERS,
        maximum_finite_difference_order=MAXIMUM_FINITE_DIFFERENCE_ORDER,
        compiled_power_stream_run_count=1,
        absolute_time_reevaluation_used=bool(metadata.evaluation_times),
        repeated_p_actions_during_reevaluation=0,
        resources=resources,
        input_provenance_classification=INPUT_PROVENANCE_CLASSIFICATION,
        method_metadata_preconditions_proved=False,
        initial_mass_cap_independently_proved=False,
        external_stream_replay_complete=False,
        control_exclusion_proved=False,
        science_free_proved=False,
        authorizes_scientific_execution=False,
        science_executed=False,
        topology_pass=False,
        production_scale_execution_classified=False,
        resource_pass=False,
        f0_pass=False,
        receipt_sha256="0" * 64,
    )
    receipt = replace(
        provisional_receipt,
        receipt_sha256=_receipt_binding(provisional_receipt),
    )
    result = CompiledCanonicalScalarSeriesResult(
        backend=backend,
        compiled_stream=stream,
        metadata=metadata,
        scalar_series=series,
        evaluations=evaluations,
        receipt=receipt,
    )
    validate_compiled_canonical_scalar_series_result(result)
    return result


def _validate_plan_binding(
    actual: CompiledBatchPoissonPlanBinding,
    expected: CompiledBatchPoissonPlanBinding,
    *,
    series_maximum_power: int,
) -> None:
    if (
        type(actual) is not CompiledBatchPoissonPlanBinding
        or actual != expected
        or not _is_sha256(actual.binding_sha256)
        or not hmac.compare_digest(actual.binding_sha256, _plan_binding(actual))
        or actual.positive_mean_has_positive_tail is not True
        or actual.maximum_required_power_index
        != actual.right_index + MAXIMUM_FINITE_DIFFERENCE_ORDER
        or actual.maximum_required_power_index > series_maximum_power
        or (
            Fraction(actual.mean_numerator, actual.mean_denominator) > 0
            and float.fromhex(actual.tail_upper_hex) <= 0
        )
    ):
        raise CompiledBatchFailure("Poisson plan binding is invalid")


def validate_compiled_canonical_scalar_series_result(
    result: CompiledCanonicalScalarSeriesResult,
) -> None:
    """Recompute the stream radii, plans, evaluations, and complete receipt."""

    if (
        type(result) is not CompiledCanonicalScalarSeriesResult
        or type(result.backend) is not compiled.CompiledPowerStreamBackend
        or type(result.compiled_stream) is not compiled.CompiledPowerStreamResult
        or type(result.metadata) is not GenericCompiledBatchMethodMetadata
        or type(result.scalar_series) is not batched.CanonicalScalarPowerSeries
        or type(result.evaluations) is not tuple
        or type(result.receipt) is not CompiledBatchReceipt
    ):
        raise CompiledBatchFailure("compiled batch result has wrong exact types")
    validate_generic_compiled_batch_metadata(result.metadata)
    compiled.validate_compiled_power_stream_result(
        result.backend,
        result.compiled_stream,
    )
    _validate_backend_method_ledgers(result.backend)
    batched.validate_canonical_scalar_power_series(result.scalar_series)
    if (
        hashlib.sha256(_MODULE_PATH.read_bytes()).hexdigest()
        != _MODULE_SHA256_AT_IMPORT
        or hashlib.sha256(_BATCHED_SOURCE_PATH.read_bytes()).hexdigest()
        != _BATCHED_SOURCE_SHA256_AT_IMPORT
    ):
        raise CompiledBatchFailure(
            "integration or batched dependency changed after module import"
        )
    metadata_hash = _metadata_binding(result.metadata)
    rebuilt_series, maximum_state_radius = _construct_scalar_series(
        result.backend,
        result.compiled_stream,
        result.metadata,
        metadata_binding_sha256=metadata_hash,
    )
    if rebuilt_series != result.scalar_series:
        raise CompiledBatchFailure("canonical scalar records failed replay")
    expected_horizon_plan = _make_plan_binding(
        result.metadata,
        purpose="series_horizon",
        time=result.metadata.series_horizon,
    )
    expected_evaluation_plans = tuple(
        _make_plan_binding(
            result.metadata,
            purpose=f"evaluation_{index}",
            time=time,
        )
        for index, time in enumerate(result.metadata.evaluation_times)
    )
    receipt = result.receipt
    _validate_plan_binding(
        receipt.horizon_plan,
        expected_horizon_plan,
        series_maximum_power=result.scalar_series.maximum_power_index,
    )
    if (
        type(receipt.evaluation_plans) is not tuple
        or len(receipt.evaluation_plans) != len(expected_evaluation_plans)
    ):
        raise CompiledBatchFailure("evaluation plan tuple is invalid")
    for actual, expected in zip(
        receipt.evaluation_plans,
        expected_evaluation_plans,
        strict=True,
    ):
        _validate_plan_binding(
            actual,
            expected,
            series_maximum_power=result.scalar_series.maximum_power_index,
        )
    expected_evaluations = (
        batched.reevaluate_canonical_scalar_series(
            result.scalar_series,
            times=result.metadata.evaluation_times,
            tail_tolerance=result.metadata.tail_tolerance,
            precision_bits=result.metadata.mpfr_precision_bits,
            maximum_terms=result.metadata.maximum_poisson_terms,
        )
        if result.metadata.evaluation_times
        else ()
    )
    if result.evaluations != expected_evaluations or any(
        type(row) is not batched.AbsoluteTimeScalarJets
        or tuple(jet.order for jet in row.jets) != RETURNED_JET_ORDERS
        for row in result.evaluations
    ):
        raise CompiledBatchFailure("absolute-time evaluation replay failed")
    expected_resources = _make_resource_ledger(
        result.backend,
        result.compiled_stream,
        result.scalar_series,
        result.evaluations,
    )
    series_bytes = batched.canonical_scalar_power_series_bytes(
        result.scalar_series
    )
    false_flags = (
        receipt.integration_source_observation_authoritative,
        receipt.independent_source_audit_complete,
        receipt.method_metadata_preconditions_proved,
        receipt.initial_mass_cap_independently_proved,
        receipt.external_stream_replay_complete,
        receipt.control_exclusion_proved,
        receipt.science_free_proved,
        receipt.authorizes_scientific_execution,
        receipt.science_executed,
        receipt.topology_pass,
        receipt.production_scale_execution_classified,
        receipt.resource_pass,
        receipt.f0_pass,
    )
    integer_fields = (
        receipt.maximum_finite_difference_order,
        receipt.compiled_power_stream_run_count,
        receipt.repeated_p_actions_during_reevaluation,
    )
    if (
        receipt.schema != RECEIPT_SCHEMA
        or receipt.status != METHOD_STATUS
        or receipt.integration_source_sha256 != _MODULE_SHA256_AT_IMPORT
        or not _is_sha256(receipt.integration_source_sha256)
        or receipt.batched_scalar_source_sha256
        != _BATCHED_SOURCE_SHA256_AT_IMPORT
        or not _is_sha256(receipt.batched_scalar_source_sha256)
        or type(receipt.batched_scalar_runtime_identity) is not str
        or receipt.batched_scalar_runtime_identity != batched._runtime_identity()
        or receipt.metadata_binding_sha256 != metadata_hash
        or receipt.initial_raw_sha256
        != result.compiled_stream.receipt.initial_raw_sha256
        or receipt.compiled_backend_receipt_sha256
        != result.backend.receipt.receipt_sha256
        or type(receipt.compiled_backend_receipt)
        is not compiled.CompiledBackendReceipt
        or receipt.compiled_backend_receipt != result.backend.receipt
        or type(receipt.compiled_build_receipt)
        is not compiled.CompiledBuildReceipt
        or receipt.compiled_build_receipt != result.backend.receipt.build
        or type(receipt.compiled_stream_receipt)
        is not compiled.CompiledPowerStreamReceipt
        or receipt.compiled_stream_receipt != result.compiled_stream.receipt
        or receipt.scalar_stream_sha256
        != result.scalar_series.scalar_stream_sha256
        or receipt.canonical_series_binding_sha256
        != result.scalar_series.series_binding_sha256
        or receipt.canonical_series_bytes_sha256
        != hashlib.sha256(series_bytes).hexdigest()
        or receipt.final_power_raw_sha256
        != result.compiled_stream.receipt.final_power_raw_sha256
        or float.fromhex(receipt.maximum_state_radius_upper_hex)
        != batched._fraction_to_float_upper(maximum_state_radius)
        or type(receipt.returned_jet_orders) is not tuple
        or receipt.returned_jet_orders != RETURNED_JET_ORDERS
        or any(type(value) is not int for value in integer_fields)
        or receipt.maximum_finite_difference_order
        != MAXIMUM_FINITE_DIFFERENCE_ORDER
        or receipt.compiled_power_stream_run_count != 1
        or receipt.absolute_time_reevaluation_used
        is not bool(result.metadata.evaluation_times)
        or receipt.repeated_p_actions_during_reevaluation != 0
        or type(receipt.resources) is not CompiledBatchResourceLedger
        or receipt.resources != expected_resources
        or receipt.input_provenance_classification
        != INPUT_PROVENANCE_CLASSIFICATION
        or any(value is not False for value in false_flags)
        or not _is_sha256(receipt.receipt_sha256)
        or not hmac.compare_digest(
            receipt.receipt_sha256,
            _receipt_binding(receipt),
        )
    ):
        raise CompiledBatchFailure("compiled batch receipt is invalid")


def compiled_batch_evidence_builtin_payload(
    result: CompiledCanonicalScalarSeriesResult,
) -> dict[str, object]:
    """Return explicit complete built-ins for independent persistence/replay."""

    validate_compiled_canonical_scalar_series_result(result)
    series_payload = json.loads(
        batched.canonical_scalar_power_series_bytes(result.scalar_series)
    )
    provisional: dict[str, object] = {
        "evidence_binding_sha256": "0" * 64,
        "evaluations": _builtin(result.evaluations),
        "metadata": _metadata_payload(result.metadata),
        "receipt": _builtin(result.receipt),
        "schema": EVIDENCE_SCHEMA,
        "series": series_payload,
    }
    provisional["evidence_binding_sha256"] = _canonical_json_sha256(
        provisional
    )
    return provisional


def compiled_batch_evidence_bytes(
    result: CompiledCanonicalScalarSeriesResult,
) -> bytes:
    """Return bounded canonical ASCII JSON containing all persisted evidence."""

    payload = _canonical_json_bytes(
        compiled_batch_evidence_builtin_payload(result)
    )
    if len(payload) > MAXIMUM_EVIDENCE_BYTES:
        raise CompiledBatchFailure("compiled batch evidence exceeds its byte cap")
    return payload
