"""Tiny science-free uniformization on the accepted packed rate action.

This module is intentionally a bounded method fixture.  It propagates a
nonnegative subprobability point-plus-``l1``-ball with one fixed whole-box
uniformization rate, exact-rational Poisson recurrences, and a conservative
truncation tail.  It is not a scientific result and cannot make F0 pass.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Final

import numpy as np
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_interval_action as directed
import rate_defined_tensor_f0_packed_rate_action as rate_action

ACCEPTED_PACKED_SOURCE_SHA256: Final = (
    "447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4"
)
ACCEPTED_DIRECTED_SOURCE_SHA256: Final = (
    "2f3201a9eb1b6fbe577b43c3b046ad5f7f369816a7d4a32f4381506e63494f2a"
)
ACCEPTED_RATE_ACTION_SOURCE_SHA256: Final = (
    "7c1586e54bac2008ac910d5c2b910cee5206dab8c19948f5b5857db6563813c9"
)
ACCEPTED_RATE_ACTION_TEST_SHA256: Final = (
    "b5127aa26ab3179986b5ad5cafbcae55c3dd6768217a2b500ea496f1f833939f"
)
ACCEPTED_RATE_ACTION_TEST_NAME: Final = "test_rate_defined_tensor_f0_packed_rate_action.py"

MAX_TINY_STATES: Final = 64
MAX_TINY_POISSON_MEAN: Final = Fraction(1)
MAX_TINY_POISSON_TERMS: Final = 64
MAX_EXP_TAYLOR_DEGREE: Final = 512
MIN_TAIL_TOLERANCE: Final = Fraction(1, 2**80)
MAX_TAIL_TOLERANCE: Final = Fraction(1, 4)
MAX_EXACT_INTEGER_BITS: Final = 4_096
MAX_TINY_NUMPY_PAYLOAD_BYTES: Final = 5_000_000

METHOD_STATUS: Final = "PASS_TINY_UNIFORMIZATION_METHOD_ONLY_NOT_F0"


class TinyUniformizationFailure(RuntimeError):
    """Fail-closed error for the deliberately tiny method layer."""


@dataclass(frozen=True, slots=True)
class AcceptedRateActionBinding:
    packed_source_sha256: str
    directed_source_sha256: str
    source_sha256: str
    test_sha256: str
    exact_bytes_matched: bool
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class _PoissonWeightInterval:
    index: int
    lower: Fraction
    upper: Fraction


@dataclass(frozen=True, slots=True)
class PoissonRecurrenceLedger:
    mean: Fraction
    requested_tail_tolerance: Fraction
    weights: tuple[_PoissonWeightInterval, ...]
    exp_taylor_degree: int
    exp_mu_lower: Fraction
    exp_mu_upper: Fraction
    exp_remainder_relative_upper: Fraction
    included_probability_lower: Fraction
    included_probability_upper: Fraction
    tail_probability_lower: Fraction
    tail_probability_upper: Fraction
    normalization_tail_probability_upper: Fraction
    first_omitted_probability_upper: Fraction
    geometric_tail_ratio_upper: Fraction
    geometric_tail_probability_upper: Fraction
    recurrence_exact: bool
    tail_bound_conservative: bool
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class _PowerStep:
    action_index: int
    predecessor_chain_sha256: str
    input_nominal_raw_sha256: str
    input_radius_hex: str
    output_nominal_raw_sha256: str
    output_radius_hex: str
    action_consistency_sha256: str
    kernel_replay_sha256: str
    chain_sha256: str


@dataclass(frozen=True, slots=True)
class PowerRecurrenceLedger:
    initial_input_binding_sha256: str
    initial_nominal_raw_sha256: str
    initial_radius_hex: str
    initial_chain_sha256: str
    steps: tuple[_PowerStep, ...]
    final_chain_sha256: str
    predecessor_chain_complete: bool
    caller_continuation_inputs_accepted: bool
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class MassNonnegativityLedger:
    input_mass_lower: Fraction
    input_mass_upper: Fraction
    maximum_target_exit_upper: Fraction
    uniformization_slack: Fraction
    returned_nominal_mass: Fraction
    enclosed_output_mass_lower: Fraction
    enclosed_output_mass_upper: Fraction
    input_ball_nonnegative: bool
    fixed_uniformized_operator_substochastic: bool
    returned_nominal_nonnegative: bool
    conditional_target_nonnegative: bool
    authoritative_target_nonnegative_proved: bool
    mass_interval_conditional_on_declared_input_radius: bool
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class TinyResourceLedger:
    state_count: int
    state_cap: int
    poisson_terms_used: int
    poisson_term_cap: int
    maximum_terms_requested: int
    poisson_mean_cap: Fraction
    p_action_calls: int
    exact_state_accumulator_count: int
    exact_weight_interval_count: int
    retained_fraction_slots_count: int
    maximum_fraction_integer_bits_observed: int
    temporary_python_object_peak_proved: bool
    retained_power_state_count: int
    maximum_simultaneous_power_vectors: int
    all_powers_retained: bool
    returned_numpy_payload_bytes: int
    bridge_validation_scratch_bytes: int
    declared_peak_excluding_preowned_kernel_upper_bytes: int
    preowned_kernel_numpy_payload_bytes: int
    declared_peak_including_preowned_kernel_upper_bytes: int
    numpy_payload_hard_cap_bytes: int
    subordinate_peak_excludes_preowned_kernel: bool
    python_object_payload_measured: bool
    method_diagnostic_only: bool
    exact_memory_claim: bool
    production_memory_exact: bool
    production_resource_gate: bool
    production_scale_executed: bool
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class TinyUniformizationResult:
    nominal: np.ndarray
    nominal_raw_sha256: str
    l1_radius_upper: float
    l1_radius_upper_hex: str
    l1_radius_exact_upper: Fraction
    time: Fraction
    uniformization_rate: Fraction
    poisson_mean: Fraction
    fixed_rate_rechecked_count: int
    rate_action_contract_sha256: str
    accepted_rate_action: AcceptedRateActionBinding
    poisson: PoissonRecurrenceLedger
    powers: PowerRecurrenceLedger
    mass: MassNonnegativityLedger
    resources: TinyResourceLedger
    status: str
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    science_executed: bool
    jets_complete: bool
    topology_complete: bool
    production_resource_gate: bool
    f0_pass: bool


def _stream_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    scratch = bytearray(4096)
    with path.open("rb", buffering=0) as source:
        while True:
            count = source.readinto(scratch)
            if not count:
                break
            digest.update(memoryview(scratch)[:count])
    return digest.hexdigest()


def _verify_accepted_rate_action_bytes() -> AcceptedRateActionBinding:
    source = Path(rate_action.__file__).resolve()
    test = source.with_name(ACCEPTED_RATE_ACTION_TEST_NAME)
    packed_digest = _stream_sha256(Path(packed.__file__).resolve())
    directed_digest = _stream_sha256(Path(directed.__file__).resolve())
    source_digest = _stream_sha256(source)
    test_digest = _stream_sha256(test)
    if (
        packed_digest != ACCEPTED_PACKED_SOURCE_SHA256
        or directed_digest != ACCEPTED_DIRECTED_SOURCE_SHA256
        or source_digest != ACCEPTED_RATE_ACTION_SOURCE_SHA256
        or test_digest != ACCEPTED_RATE_ACTION_TEST_SHA256
    ):
        raise TinyUniformizationFailure("accepted rate-action byte binding changed")
    return AcceptedRateActionBinding(
        packed_source_sha256=packed_digest,
        directed_source_sha256=directed_digest,
        source_sha256=source_digest,
        test_sha256=test_digest,
        exact_bytes_matched=True,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        f0_pass=False,
    )


def _digest_ascii_fields(domain: bytes, *fields: object) -> str:
    digest = hashlib.sha256(domain)
    for field in fields:
        encoded = str(field).encode("ascii")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _power_step_digest(step: _PowerStep) -> str:
    return _digest_ascii_fields(
        b"tiny-uniformization-power-step-v1\x00",
        step.action_index,
        step.predecessor_chain_sha256,
        step.input_nominal_raw_sha256,
        step.input_radius_hex,
        step.output_nominal_raw_sha256,
        step.output_radius_hex,
        step.action_consistency_sha256,
        step.kernel_replay_sha256,
    )


def _kernel_numpy_payload_bytes(kernel: packed.PackedTensorKernel) -> int:
    arrays = [
        kernel.killing.intervals,
        kernel.killing_center,
        kernel.diagonal_center,
        kernel.p_self_center,
    ]
    for axis_index, axis in enumerate(kernel.axes):
        arrays.extend(
            (
                axis.forward.intervals,
                axis.backward.intervals,
                kernel.forward_center[axis_index],
                kernel.backward_center[axis_index],
                kernel.p_forward_center[axis_index],
                kernel.p_backward_center[axis_index],
            )
        )
    measured = sum(int(array.nbytes) for array in arrays)
    formula = 40 * kernel.states + 64 * sum(axis.size for axis in kernel.axes)
    if measured != formula:
        raise TinyUniformizationFailure("packed-kernel NumPy payload formula changed")
    return measured


def _maximum_fraction_bits(values: tuple[Fraction, ...]) -> int:
    return max(
        max(value.numerator.bit_length(), value.denominator.bit_length()) for value in values
    )


def _require_bounded_fraction(value: object, *, label: str) -> Fraction:
    if type(value) is not Fraction:
        raise TinyUniformizationFailure(f"{label} must be an exact Fraction")
    if (
        value.numerator.bit_length() > MAX_EXACT_INTEGER_BITS
        or value.denominator.bit_length() > MAX_EXACT_INTEGER_BITS
    ):
        raise TinyUniformizationFailure(f"{label} exceeds the exact-integer cap")
    return value


def _exp_positive_enclosure(
    mean: Fraction,
    *,
    relative_remainder_target: Fraction,
) -> tuple[Fraction, Fraction, Fraction, int]:
    """Enclose ``exp(mean)`` using a positive Taylor sum and geometric tail."""

    partial = Fraction(1)
    term = Fraction(1)
    for degree in range(MAX_EXP_TAYLOR_DEGREE + 1):
        first_omitted = term * mean / (degree + 1)
        ratio_upper = mean / (degree + 2)
        if ratio_upper < 1:
            remainder = first_omitted / (1 - ratio_upper)
            upper = partial + remainder
            relative = remainder / upper
            if relative <= relative_remainder_target:
                return partial, upper, relative, degree
        term = first_omitted
        partial += term
        if (
            partial.numerator.bit_length() > MAX_EXACT_INTEGER_BITS
            or partial.denominator.bit_length() > MAX_EXACT_INTEGER_BITS
        ):
            raise TinyUniformizationFailure("Taylor enclosure exceeds exact-integer cap")
    raise TinyUniformizationFailure("Taylor enclosure did not meet its bounded target")


def _poisson_recurrence(
    mean: Fraction,
    *,
    tail_tolerance: Fraction,
    maximum_terms: int,
) -> PoissonRecurrenceLedger:
    mean = _require_bounded_fraction(mean, label="Poisson mean")
    tolerance = _require_bounded_fraction(tail_tolerance, label="tail tolerance")
    if mean < 0 or mean > MAX_TINY_POISSON_MEAN:
        raise TinyUniformizationFailure("Poisson mean is outside the tiny-method cap")
    if tolerance < MIN_TAIL_TOLERANCE or tolerance > MAX_TAIL_TOLERANCE:
        raise TinyUniformizationFailure("tail tolerance is outside the bounded range")
    if (
        type(maximum_terms) is not int
        or maximum_terms < 1
        or maximum_terms > MAX_TINY_POISSON_TERMS
    ):
        raise TinyUniformizationFailure("Poisson term limit is invalid")

    exp_lower, exp_upper, relative, degree = _exp_positive_enclosure(
        mean,
        relative_remainder_target=tolerance / 8,
    )
    lower = Fraction(1, 1) / exp_upper
    upper = Fraction(1, 1) / exp_lower
    weights: list[_PoissonWeightInterval] = []
    included_lower = Fraction(0)
    included_upper = Fraction(0)

    for index in range(maximum_terms):
        if index:
            factor = mean / index
            lower *= factor
            upper *= factor
        weights.append(_PoissonWeightInterval(index=index, lower=lower, upper=upper))
        included_lower += lower
        included_upper += upper
        if included_lower > 1:
            raise TinyUniformizationFailure("lower Poisson mass exceeded one")
        normalization_tail_upper = 1 - included_lower
        first_omitted_upper = upper * mean / (index + 1)
        geometric_ratio_upper = mean / (index + 2)
        geometric_tail_upper = first_omitted_upper / (1 - geometric_ratio_upper)
        tail_upper = min(normalization_tail_upper, geometric_tail_upper)
        tail_lower = max(Fraction(0), 1 - included_upper)
        if tail_upper <= tolerance:
            ledger = PoissonRecurrenceLedger(
                mean=mean,
                requested_tail_tolerance=tolerance,
                weights=tuple(weights),
                exp_taylor_degree=degree,
                exp_mu_lower=exp_lower,
                exp_mu_upper=exp_upper,
                exp_remainder_relative_upper=relative,
                included_probability_lower=included_lower,
                included_probability_upper=included_upper,
                tail_probability_lower=tail_lower,
                tail_probability_upper=tail_upper,
                normalization_tail_probability_upper=normalization_tail_upper,
                first_omitted_probability_upper=first_omitted_upper,
                geometric_tail_ratio_upper=geometric_ratio_upper,
                geometric_tail_probability_upper=geometric_tail_upper,
                recurrence_exact=True,
                tail_bound_conservative=True,
                non_authoritative=True,
                science_free=True,
                fresh_process=False,
                f0_pass=False,
            )
            _validate_poisson_ledger(ledger)
            return ledger
    raise TinyUniformizationFailure("Poisson term cap was insufficient for the tail target")


def _validate_poisson_ledger(ledger: PoissonRecurrenceLedger) -> None:
    if (
        type(ledger) is not PoissonRecurrenceLedger
        or not ledger.weights
        or ledger.non_authoritative is not True
        or ledger.science_free is not True
        or ledger.fresh_process is not False
        or ledger.f0_pass is not False
        or ledger.recurrence_exact is not True
        or ledger.tail_bound_conservative is not True
        or ledger.tail_probability_upper > ledger.requested_tail_tolerance
        or ledger.tail_probability_lower < 0
        or ledger.tail_probability_lower > ledger.tail_probability_upper
    ):
        raise TinyUniformizationFailure("Poisson ledger header is invalid")
    lower_sum = Fraction(0)
    upper_sum = Fraction(0)
    previous: _PoissonWeightInterval | None = None
    for index, weight in enumerate(ledger.weights):
        if (
            type(weight) is not _PoissonWeightInterval
            or weight.index != index
            or weight.lower < 0
            or weight.upper < weight.lower
        ):
            raise TinyUniformizationFailure("Poisson weight interval is invalid")
        if previous is not None:
            factor = ledger.mean / index
            if weight.lower != previous.lower * factor or weight.upper != previous.upper * factor:
                raise TinyUniformizationFailure("Poisson recurrence no longer replays exactly")
        lower_sum += weight.lower
        upper_sum += weight.upper
        previous = weight
    if (
        lower_sum != ledger.included_probability_lower
        or upper_sum != ledger.included_probability_upper
        or ledger.normalization_tail_probability_upper != 1 - lower_sum
        or ledger.tail_probability_lower != max(Fraction(0), 1 - upper_sum)
        or ledger.first_omitted_probability_upper
        != ledger.weights[-1].upper * ledger.mean / len(ledger.weights)
        or ledger.geometric_tail_ratio_upper != ledger.mean / (len(ledger.weights) + 1)
        or ledger.geometric_tail_probability_upper
        != ledger.first_omitted_probability_upper / (1 - ledger.geometric_tail_ratio_upper)
        or ledger.tail_probability_upper
        != min(
            ledger.normalization_tail_probability_upper,
            ledger.geometric_tail_probability_upper,
        )
    ):
        raise TinyUniformizationFailure("Poisson mass ledger no longer balances")


def _raw_sha256(values: np.ndarray) -> str:
    return hashlib.sha256(memoryview(values).cast("B")).hexdigest()


def _fraction_to_float_upper(value: Fraction) -> float:
    if value < 0:
        raise TinyUniformizationFailure("cannot round a negative radius upward")
    candidate = float(value)
    if not math.isfinite(candidate):
        raise TinyUniformizationFailure("radius does not fit binary64")
    if Fraction.from_float(candidate) < value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    if Fraction.from_float(candidate) < value:
        raise TinyUniformizationFailure("radius conversion was not outward")
    return candidate


def _next_rate_input(
    result: rate_action.InternalRateActionState,
) -> rate_action.InternalPointBallInput:
    vector = packed.CanonicalFloat64Vector(
        logical_shape=result.logical_shape,
        values=result.nominal,
        raw_sha256=result.nominal_raw_sha256,
        nonnegative=True,
        source_sha256=result.nominal_raw_sha256,
    )
    packed.validate_canonical_vector(vector, block_size=result.memory.block_size)
    return rate_action.make_internal_point_ball_input(
        vector,
        input_l1_radius_upper=result.l1_radius_upper,
        radius_provenance_sha256=result.radius_provenance_sha256,
    )


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_power_ledger(ledger: PowerRecurrenceLedger) -> None:
    if (
        type(ledger) is not PowerRecurrenceLedger
        or not all(
            _is_sha256(value)
            for value in (
                ledger.initial_input_binding_sha256,
                ledger.initial_nominal_raw_sha256,
                ledger.initial_chain_sha256,
                ledger.final_chain_sha256,
            )
        )
        or type(ledger.initial_radius_hex) is not str
        or ledger.predecessor_chain_complete is not True
        or ledger.caller_continuation_inputs_accepted is not False
        or ledger.non_authoritative is not True
        or ledger.science_free is not True
        or ledger.fresh_process is not False
        or ledger.f0_pass is not False
    ):
        raise TinyUniformizationFailure("power recurrence ledger header is invalid")
    try:
        initial_radius = float.fromhex(ledger.initial_radius_hex)
    except ValueError as error:
        raise TinyUniformizationFailure("initial power radius is invalid") from error
    if not math.isfinite(initial_radius) or initial_radius < 0:
        raise TinyUniformizationFailure("initial power radius is invalid")

    predecessor = ledger.initial_chain_sha256
    previous_output_hash: str | None = None
    previous_output_radius: str | None = None
    for action_index, step in enumerate(ledger.steps):
        if (
            type(step) is not _PowerStep
            or step.action_index != action_index
            or step.predecessor_chain_sha256 != predecessor
            or not all(
                _is_sha256(value)
                for value in (
                    step.predecessor_chain_sha256,
                    step.input_nominal_raw_sha256,
                    step.output_nominal_raw_sha256,
                    step.action_consistency_sha256,
                    step.kernel_replay_sha256,
                    step.chain_sha256,
                )
            )
            or step.chain_sha256 != _power_step_digest(step)
        ):
            raise TinyUniformizationFailure("power recurrence predecessor chain is invalid")
        if action_index == 0:
            if (
                step.input_nominal_raw_sha256 != ledger.initial_nominal_raw_sha256
                or step.input_radius_hex != ledger.initial_radius_hex
            ):
                raise TinyUniformizationFailure("first power does not bind the initial state")
        elif (
            step.input_nominal_raw_sha256 != previous_output_hash
            or step.input_radius_hex != previous_output_radius
        ):
            raise TinyUniformizationFailure("power recurrence skipped or reset a predecessor")
        predecessor = step.chain_sha256
        previous_output_hash = step.output_nominal_raw_sha256
        previous_output_radius = step.output_radius_hex
    if ledger.final_chain_sha256 != predecessor:
        raise TinyUniformizationFailure("final power chain digest is invalid")


def tiny_uniformize_transpose(
    kernel: packed.PackedTensorKernel,
    initial: rate_action.InternalPointBallInput,
    contract: rate_action.RateActionContract,
    *,
    time: Fraction,
    tail_tolerance: Fraction,
    maximum_terms: int = MAX_TINY_POISSON_TERMS,
) -> TinyUniformizationResult:
    """Enclose a tiny ``exp(time * Q.T)`` action by fixed-rate uniformization."""

    if type(kernel) is not packed.PackedTensorKernel:
        raise TinyUniformizationFailure("kernel has the wrong exact type")
    states = kernel.states
    if states < 1 or states > MAX_TINY_STATES:
        raise TinyUniformizationFailure("state count is outside the tiny-method cap")

    accepted = _verify_accepted_rate_action_bytes()
    packed.validate_packed_tensor_kernel(kernel)
    rate_action.validate_internal_point_ball_input(initial)
    rate_action.validate_rate_action_contract(contract)
    time = _require_bounded_fraction(time, label="time")
    tolerance = _require_bounded_fraction(tail_tolerance, label="tail tolerance")
    if time < 0:
        raise TinyUniformizationFailure("time must be nonnegative")
    if (
        kernel.contract.tensor_shape != contract.tensor_shape
        or initial.logical_shape != contract.tensor_shape
        or states != contract.state_count
    ):
        raise TinyUniformizationFailure("kernel, input, and contract shapes disagree")

    kernel_bytes = _kernel_numpy_payload_bytes(kernel)
    bridge_validation_scratch_bytes = min(states, contract.block_size)
    preflight_peak_without_kernel = max(
        3 * initial.nominal.nbytes + bridge_validation_scratch_bytes,
        contract.required_peak_numeric_payload_bytes + initial.nominal.nbytes,
    )
    if preflight_peak_without_kernel + kernel_bytes > MAX_TINY_NUMPY_PAYLOAD_BYTES:
        raise TinyUniformizationFailure("tiny NumPy payload hard cap is insufficient")

    rate = kernel.rate_fraction
    if rate <= 0 or Fraction.from_float(kernel.rate) != rate:
        raise TinyUniformizationFailure("uniformization rate is not a fixed exact binary64")
    witness_map = {witness.name: witness.value for witness in kernel.ledger.witnesses}
    maximum_target_exit_upper = witness_map.get("maximum_target_exit_upper")
    if (
        type(maximum_target_exit_upper) is not Fraction
        or maximum_target_exit_upper < 0
        or rate < maximum_target_exit_upper
    ):
        raise TinyUniformizationFailure("uniformization rate misses the whole-box exit bound")
    uniformization_slack = rate - maximum_target_exit_upper
    mean = rate * time
    poisson = _poisson_recurrence(
        mean,
        tail_tolerance=tolerance,
        maximum_terms=maximum_terms,
    )

    nominal_fractions = tuple(Fraction.from_float(float(value)) for value in initial.nominal)
    if any(value == 0.0 and math.copysign(1.0, float(value)) < 0.0 for value in initial.nominal):
        raise TinyUniformizationFailure("initial nominal contains noncanonical negative zero")
    input_radius = Fraction.from_float(initial.input_l1_radius_upper)
    minimum_nominal = min(nominal_fractions)
    input_mass_centre = sum(nominal_fractions, Fraction(0))
    input_mass_lower = max(Fraction(0), input_mass_centre - input_radius)
    input_mass_upper = input_mass_centre + input_radius
    if (
        initial.nonnegative_nominal is not True
        or input_radius > minimum_nominal
        or input_mass_upper > 1
    ):
        raise TinyUniformizationFailure(
            "initial ball must be a certified nonnegative subprobability set"
        )

    exact_nominal = [Fraction(0) for _ in range(states)]
    partial_radius = Fraction(0)
    current = initial
    p_action_calls = 0
    fixed_rate_rechecked_count = 1
    action_peak_with_input = 0
    contract_digest = rate_action.rate_action_contract_sha256(contract)
    kernel_replay = packed._kernel_replay_digest(kernel)
    initial_input_binding = initial.input_binding_sha256
    initial_nominal_raw = initial.nominal_raw_sha256
    initial_radius_hex = initial.input_l1_radius_upper_hex
    initial_chain = _digest_ascii_fields(
        b"tiny-uniformization-initial-power-v1\x00",
        initial_input_binding,
        initial_nominal_raw,
        initial_radius_hex,
        kernel_replay,
        contract_digest,
        rate.numerator,
        rate.denominator,
        time.numerator,
        time.denominator,
        tolerance.numerator,
        tolerance.denominator,
    )
    predecessor_chain = initial_chain
    power_steps: list[_PowerStep] = []
    del initial

    for term_position, weight in enumerate(poisson.weights):
        centre_l1 = Fraction(0)
        for index in range(states):
            centre = Fraction.from_float(float(current.nominal[index]))
            exact_nominal[index] += weight.lower * centre
            centre_l1 += abs(centre)
        current_radius = Fraction.from_float(current.input_l1_radius_upper)
        partial_radius += weight.upper * current_radius
        partial_radius += (weight.upper - weight.lower) * centre_l1

        if term_position + 1 < len(poisson.weights):
            input_nominal_raw = current.nominal_raw_sha256
            input_radius_hex = current.input_l1_radius_upper_hex
            action = rate_action._rate_defined_p_transpose(kernel, current, contract)
            p_action_calls += 1
            action_peak_with_input = max(
                action_peak_with_input,
                action.memory.declared_peak_numeric_payload_bytes + current.nominal.nbytes,
            )
            if (
                kernel.rate_fraction != rate
                or action.contract_sha256 != contract_digest
                or action.derivation.kernel_replay_sha256 != kernel_replay
                or action.derivation.input_nominal_raw_sha256 != input_nominal_raw
                or action.l1_radius_upper_hex != action.derivation.scalar_trace[-1].value_hex
            ):
                raise TinyUniformizationFailure("fixed-rate action binding changed")
            fixed_rate_rechecked_count += 1
            chain_digest = _digest_ascii_fields(
                b"tiny-uniformization-power-step-v1\x00",
                term_position,
                predecessor_chain,
                input_nominal_raw,
                input_radius_hex,
                action.nominal_raw_sha256,
                action.l1_radius_upper_hex,
                action.consistency_sha256,
                kernel_replay,
            )
            step = _PowerStep(
                action_index=term_position,
                predecessor_chain_sha256=predecessor_chain,
                input_nominal_raw_sha256=input_nominal_raw,
                input_radius_hex=input_radius_hex,
                output_nominal_raw_sha256=action.nominal_raw_sha256,
                output_radius_hex=action.l1_radius_upper_hex,
                action_consistency_sha256=action.consistency_sha256,
                kernel_replay_sha256=kernel_replay,
                chain_sha256=chain_digest,
            )
            if _power_step_digest(step) != chain_digest:
                raise TinyUniformizationFailure("power-step chain did not self-replay")
            next_input = _next_rate_input(action)
            if (
                next_input.nominal_raw_sha256 != action.nominal_raw_sha256
                or next_input.input_l1_radius_upper_hex != action.l1_radius_upper_hex
                or next_input.radius_provenance_sha256 != action.radius_provenance_sha256
            ):
                raise TinyUniformizationFailure("power continuation reset predecessor state")
            power_steps.append(step)
            predecessor_chain = chain_digest
            current = next_input
            del action

    if kernel.rate_fraction != rate:
        raise TinyUniformizationFailure("uniformization rate changed after recurrence")
    fixed_rate_rechecked_count += 1

    powers = PowerRecurrenceLedger(
        initial_input_binding_sha256=initial_input_binding,
        initial_nominal_raw_sha256=initial_nominal_raw,
        initial_radius_hex=initial_radius_hex,
        initial_chain_sha256=initial_chain,
        steps=tuple(power_steps),
        final_chain_sha256=predecessor_chain,
        predecessor_chain_complete=True,
        caller_continuation_inputs_accepted=False,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        f0_pass=False,
    )
    _validate_power_ledger(powers)

    tail_radius = poisson.tail_probability_upper * input_mass_upper
    rounded = np.empty(states, dtype=np.float64)
    conversion_radius = Fraction(0)
    for index, exact in enumerate(exact_nominal):
        rounded[index] = float(exact)
        if not math.isfinite(float(rounded[index])):
            raise TinyUniformizationFailure("uniformized nominal does not fit binary64")
        conversion_radius += abs(Fraction.from_float(float(rounded[index])) - exact)
    rounded.setflags(write=False)
    exact_radius = partial_radius + tail_radius + conversion_radius
    radius = _fraction_to_float_upper(exact_radius)
    raw = _raw_sha256(rounded)

    returned_mass = sum(
        (Fraction.from_float(float(value)) for value in rounded),
        Fraction(0),
    )
    enclosed_mass_lower = max(Fraction(0), returned_mass - exact_radius)
    enclosed_mass_upper = min(input_mass_upper, returned_mass + exact_radius)
    mass = MassNonnegativityLedger(
        input_mass_lower=input_mass_lower,
        input_mass_upper=input_mass_upper,
        maximum_target_exit_upper=maximum_target_exit_upper,
        uniformization_slack=uniformization_slack,
        returned_nominal_mass=returned_mass,
        enclosed_output_mass_lower=enclosed_mass_lower,
        enclosed_output_mass_upper=enclosed_mass_upper,
        input_ball_nonnegative=True,
        fixed_uniformized_operator_substochastic=True,
        returned_nominal_nonnegative=bool(np.all(rounded >= 0.0)),
        conditional_target_nonnegative=True,
        authoritative_target_nonnegative_proved=False,
        mass_interval_conditional_on_declared_input_radius=True,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        f0_pass=False,
    )

    returned_bytes = int(rounded.nbytes)
    peak_without_kernel = max(
        returned_bytes,
        3 * returned_bytes + bridge_validation_scratch_bytes,
        action_peak_with_input,
    )
    retained_fraction_values = (
        time,
        rate,
        mean,
        exact_radius,
        input_mass_lower,
        input_mass_upper,
        maximum_target_exit_upper,
        uniformization_slack,
        returned_mass,
        enclosed_mass_lower,
        enclosed_mass_upper,
        poisson.mean,
        poisson.requested_tail_tolerance,
        poisson.exp_mu_lower,
        poisson.exp_mu_upper,
        poisson.exp_remainder_relative_upper,
        poisson.included_probability_lower,
        poisson.included_probability_upper,
        poisson.tail_probability_lower,
        poisson.tail_probability_upper,
        poisson.normalization_tail_probability_upper,
        poisson.first_omitted_probability_upper,
        poisson.geometric_tail_ratio_upper,
        poisson.geometric_tail_probability_upper,
        MAX_TINY_POISSON_MEAN,
        *(weight.lower for weight in poisson.weights),
        *(weight.upper for weight in poisson.weights),
    )
    maximum_fraction_bits_observed = _maximum_fraction_bits(tuple(retained_fraction_values))
    if maximum_fraction_bits_observed > MAX_EXACT_INTEGER_BITS:
        raise TinyUniformizationFailure("retained exact values exceed the integer-bit cap")
    resources = TinyResourceLedger(
        state_count=states,
        state_cap=MAX_TINY_STATES,
        poisson_terms_used=len(poisson.weights),
        poisson_term_cap=MAX_TINY_POISSON_TERMS,
        maximum_terms_requested=maximum_terms,
        poisson_mean_cap=MAX_TINY_POISSON_MEAN,
        p_action_calls=p_action_calls,
        exact_state_accumulator_count=states,
        exact_weight_interval_count=len(poisson.weights),
        retained_fraction_slots_count=25 + 2 * len(poisson.weights),
        maximum_fraction_integer_bits_observed=maximum_fraction_bits_observed,
        temporary_python_object_peak_proved=False,
        retained_power_state_count=1,
        maximum_simultaneous_power_vectors=3 if p_action_calls else 1,
        all_powers_retained=False,
        returned_numpy_payload_bytes=returned_bytes,
        bridge_validation_scratch_bytes=bridge_validation_scratch_bytes,
        declared_peak_excluding_preowned_kernel_upper_bytes=peak_without_kernel,
        preowned_kernel_numpy_payload_bytes=kernel_bytes,
        declared_peak_including_preowned_kernel_upper_bytes=(peak_without_kernel + kernel_bytes),
        numpy_payload_hard_cap_bytes=MAX_TINY_NUMPY_PAYLOAD_BYTES,
        subordinate_peak_excludes_preowned_kernel=True,
        python_object_payload_measured=False,
        method_diagnostic_only=True,
        exact_memory_claim=False,
        production_memory_exact=False,
        production_resource_gate=False,
        production_scale_executed=False,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        f0_pass=False,
    )

    if _verify_accepted_rate_action_bytes() != accepted:
        raise TinyUniformizationFailure("accepted rate-action bytes changed during the method")
    result = TinyUniformizationResult(
        nominal=rounded,
        nominal_raw_sha256=raw,
        l1_radius_upper=radius,
        l1_radius_upper_hex=radius.hex(),
        l1_radius_exact_upper=exact_radius,
        time=time,
        uniformization_rate=rate,
        poisson_mean=mean,
        fixed_rate_rechecked_count=fixed_rate_rechecked_count,
        rate_action_contract_sha256=contract_digest,
        accepted_rate_action=accepted,
        poisson=poisson,
        powers=powers,
        mass=mass,
        resources=resources,
        status=METHOD_STATUS,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        science_executed=False,
        jets_complete=False,
        topology_complete=False,
        production_resource_gate=False,
        f0_pass=False,
    )
    _validate_result(result)
    return result


def _validate_result(result: TinyUniformizationResult) -> None:
    _validate_poisson_ledger(result.poisson)
    _validate_power_ledger(result.powers)
    if (
        type(result) is not TinyUniformizationResult
        or result.status != METHOD_STATUS
        or result.non_authoritative is not True
        or result.science_free is not True
        or result.fresh_process is not False
        or result.science_executed is not False
        or result.jets_complete is not False
        or result.topology_complete is not False
        or result.production_resource_gate is not False
        or result.f0_pass is not False
        or result.accepted_rate_action.packed_source_sha256 != ACCEPTED_PACKED_SOURCE_SHA256
        or result.accepted_rate_action.directed_source_sha256 != ACCEPTED_DIRECTED_SOURCE_SHA256
        or result.accepted_rate_action.source_sha256 != ACCEPTED_RATE_ACTION_SOURCE_SHA256
        or result.accepted_rate_action.test_sha256 != ACCEPTED_RATE_ACTION_TEST_SHA256
        or result.accepted_rate_action.exact_bytes_matched is not True
        or result.accepted_rate_action.non_authoritative is not True
        or result.accepted_rate_action.science_free is not True
        or result.accepted_rate_action.fresh_process is not False
        or result.accepted_rate_action.f0_pass is not False
        or result.powers.non_authoritative is not True
        or result.powers.science_free is not True
        or result.powers.fresh_process is not False
        or result.powers.f0_pass is not False
        or result.mass.non_authoritative is not True
        or result.mass.science_free is not True
        or result.mass.fresh_process is not False
        or result.mass.f0_pass is not False
        or result.resources.non_authoritative is not True
        or result.resources.science_free is not True
        or result.resources.fresh_process is not False
        or result.resources.f0_pass is not False
        or result.resources.method_diagnostic_only is not True
        or result.resources.exact_memory_claim is not False
        or result.resources.production_memory_exact is not False
        or result.resources.production_resource_gate is not False
        or result.resources.production_scale_executed is not False
        or result.nominal.dtype != np.dtype(np.float64)
        or result.nominal.flags.writeable
        or not result.nominal.flags.owndata
        or result.nominal.ndim != 1
        or result.nominal_raw_sha256 != _raw_sha256(result.nominal)
        or result.l1_radius_upper_hex != result.l1_radius_upper.hex()
        or Fraction.from_float(result.l1_radius_upper) < result.l1_radius_exact_upper
        or result.poisson_mean != result.uniformization_rate * result.time
        or result.resources.state_count != result.nominal.size
        or result.resources.p_action_calls != len(result.poisson.weights) - 1
        or result.resources.p_action_calls != len(result.powers.steps)
        or not (
            1
            <= result.resources.poisson_terms_used
            <= result.resources.maximum_terms_requested
            <= result.resources.poisson_term_cap
        )
        or result.poisson_mean > result.resources.poisson_mean_cap
        or result.fixed_rate_rechecked_count != result.resources.p_action_calls + 2
        or result.mass.input_ball_nonnegative is not True
        or result.mass.fixed_uniformized_operator_substochastic is not True
        or result.mass.returned_nominal_nonnegative is not True
        or result.mass.conditional_target_nonnegative is not True
        or result.mass.authoritative_target_nonnegative_proved is not False
        or result.mass.mass_interval_conditional_on_declared_input_radius is not True
        or result.mass.uniformization_slack < 0
        or result.uniformization_rate
        != result.mass.maximum_target_exit_upper + result.mass.uniformization_slack
        or result.resources.declared_peak_excluding_preowned_kernel_upper_bytes
        + result.resources.preowned_kernel_numpy_payload_bytes
        != result.resources.declared_peak_including_preowned_kernel_upper_bytes
        or result.resources.declared_peak_including_preowned_kernel_upper_bytes
        > result.resources.numpy_payload_hard_cap_bytes
        or result.resources.python_object_payload_measured is not False
        or result.resources.subordinate_peak_excludes_preowned_kernel is not True
        or not (
            1 <= result.resources.bridge_validation_scratch_bytes <= result.resources.state_count
        )
        or result.resources.declared_peak_excluding_preowned_kernel_upper_bytes
        < (
            3 * result.resources.returned_numpy_payload_bytes
            + result.resources.bridge_validation_scratch_bytes
        )
        or result.resources.temporary_python_object_peak_proved is not False
        or result.resources.all_powers_retained is not False
        or result.resources.retained_power_state_count != 1
        or result.resources.maximum_simultaneous_power_vectors
        != (3 if result.resources.p_action_calls else 1)
        or result.resources.maximum_fraction_integer_bits_observed > MAX_EXACT_INTEGER_BITS
        or result.resources.retained_fraction_slots_count != 25 + 2 * len(result.poisson.weights)
        or not (
            0
            <= result.mass.enclosed_output_mass_lower
            <= result.mass.enclosed_output_mass_upper
            <= result.mass.input_mass_upper
            <= 1
        )
    ):
        raise TinyUniformizationFailure("uniformization result ledger is invalid")
