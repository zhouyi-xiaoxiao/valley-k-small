"""Independent exact semantic replay for the tiny packed uniformization.

This verifier does not import or consume the producer's rate-action,
uniformization, Poisson, power-chain, mass, or resource ledgers.  Starting
from the canonical packed kernel and primitive run arguments, it

* reconstructs the central dense ``P.T`` action with exact ``Fraction``
  arithmetic;
* recomputes a whole-rate-box ``l1`` perturbation bound directly from the raw
  interval endpoints;
* encloses ``exp(-mu)`` with an independent alternating series rather than the
  producer's reciprocal positive series; and
* checks that the reported point-plus-radius output contains the resulting
  exact semantic enclosure.

The scope remains ``N <= 64`` and ``mu <= 1``.  This is an independent
same-process method replay, not a serialized clean-process verifier, a
production resource result, a topology calculation, or F0 acceptance.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Final

import numpy as np
import rate_defined_tensor_f0_packed as packed

MAX_STATES: Final = 64
MAX_MEAN: Final = Fraction(1)
MAX_TERMS: Final = 64
MAX_ALTERNATING_DEGREE: Final = 512
MAX_EXACT_INTEGER_BITS: Final = 8_192
STATUS: Final = "PASS_INDEPENDENT_TINY_SEMANTIC_REPLAY_ONLY_NOT_F0"
INITIAL_BOX_ROLE: Final = "science_free_initial_target_component_box"
UNIT_MASS_CONSTRUCTION: Final = "lexicographic_lower_fill_exact_unit_mass_v1"


class SemanticReplayFailure(RuntimeError):
    """Fail-closed error for the independent mathematical replay."""


@dataclass(frozen=True, slots=True)
class ExactWeightInterval:
    index: int
    lower: Fraction
    upper: Fraction


@dataclass(frozen=True, slots=True)
class IndependentPoissonReplay:
    mean: Fraction
    alternating_degree: int
    exp_minus_mean_lower: Fraction
    exp_minus_mean_upper: Fraction
    weights: tuple[ExactWeightInterval, ...]
    tail_probability_upper: Fraction
    requested_tail_tolerance: Fraction
    recurrence_exact: bool
    alternating_bracket_exact: bool
    producer_poisson_ledger_consumed: bool


@dataclass(frozen=True, slots=True)
class IndependentDenseActionReplay:
    state_count: int
    maximum_column_l1_deviation: Fraction
    central_columns_subprobability: bool
    every_rate_box_column_subprobability: bool
    raw_interval_endpoints_consumed: bool
    producer_action_ledger_consumed: bool


@dataclass(frozen=True, slots=True)
class IndependentInitialTargetReplay:
    component_box_raw_sha256: str
    component_box_manifest_sha256: str
    unit_mass_witness_sha256: str
    exact_lower_mass: Fraction
    exact_upper_mass: Fraction
    exact_anchor_radius: Fraction
    nominal_is_component_lower_endpoint: bool
    canonical_unit_mass_witness_recomputed: bool
    producer_target_binding_consumed: bool


@dataclass(frozen=True, slots=True)
class IndependentSemanticReplayResult:
    state_count: int
    time: Fraction
    exact_accumulator: tuple[Fraction, ...]
    independent_l1_radius_upper: Fraction
    producer_centre_distance: Fraction
    required_producer_radius: Fraction
    supplied_producer_radius: Fraction
    containment_margin: Fraction
    poisson: IndependentPoissonReplay
    action: IndependentDenseActionReplay
    initial_target: IndependentInitialTargetReplay
    producer_ball_contains_independent_replay: bool
    independent_code_path: bool
    producer_ledgers_consumed: bool
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    topology_complete: bool
    production_resource_gate: bool
    f0_pass: bool
    status: str


@dataclass(frozen=True, slots=True)
class _Transition:
    target: int
    coefficient: Fraction


def _bounded_fraction(value: object, *, label: str) -> Fraction:
    if type(value) is not Fraction:
        raise SemanticReplayFailure(f"{label} must be an exact Fraction")
    if (
        value.numerator.bit_length() > MAX_EXACT_INTEGER_BITS
        or value.denominator.bit_length() > MAX_EXACT_INTEGER_BITS
    ):
        raise SemanticReplayFailure(f"{label} exceeds the exact-integer cap")
    return value


def _digest_fields(domain: bytes, *fields: object) -> str:
    digest = hashlib.sha256(domain)
    for field in fields:
        encoded = str(field).encode("ascii")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _component_manifest_sha256(manifest: packed.PackedIntervalManifest) -> str:
    return _digest_fields(
        b"science-free-initial-component-manifest-v1\x00",
        manifest.schema,
        manifest.role,
        *manifest.logical_shape,
        *manifest.array_shape,
        manifest.state_count,
        manifest.raw_byte_length,
        manifest.raw_sha256,
        manifest.endpoint_order,
        manifest.nonnegative,
        manifest.block_size,
        manifest.maximum_working_bytes,
    )


def _unit_mass_witness_sha256(
    exact_lower: tuple[Fraction, ...],
    exact_upper: tuple[Fraction, ...],
) -> str:
    residual = Fraction(1) - sum(exact_lower, Fraction(0))
    witness = list(exact_lower)
    for index, (lower, upper) in enumerate(zip(exact_lower, exact_upper, strict=True)):
        increment = min(residual, upper - lower)
        witness[index] += increment
        residual -= increment
    if residual != 0 or sum(witness, Fraction(0)) != 1:
        raise SemanticReplayFailure("component box has no exact unit-mass witness")
    fields: list[object] = [UNIT_MASS_CONSTRUCTION, len(witness)]
    for value in witness:
        _bounded_fraction(value, label="unit-mass witness entry")
        fields.extend((value.numerator, value.denominator))
    return _digest_fields(b"science-free-exact-unit-mass-witness-v1\x00", *fields)


def _replay_initial_target(
    component_box: packed.CanonicalPackedIntervals,
    *,
    initial_nominal: np.ndarray,
    initial_radius: Fraction,
    declared_component_box_raw_sha256: str,
    declared_component_box_manifest_sha256: str,
    declared_unit_mass_witness_sha256: str,
) -> IndependentInitialTargetReplay:
    packed.validate_canonical_packed_intervals(component_box)
    if (
        component_box.manifest.role != INITIAL_BOX_ROLE
        or component_box.manifest.nonnegative is not True
        or component_box.manifest.raw_sha256 != declared_component_box_raw_sha256
    ):
        raise SemanticReplayFailure("initial component-box binding is invalid")
    manifest_digest = _component_manifest_sha256(component_box.manifest)
    if manifest_digest != declared_component_box_manifest_sha256:
        raise SemanticReplayFailure("initial component-box manifest binding changed")
    exact_lower = tuple(
        Fraction.from_float(float(value)) for value in component_box.intervals[:, 0]
    )
    exact_upper = tuple(
        Fraction.from_float(float(value)) for value in component_box.intervals[:, 1]
    )
    lower_mass = sum(exact_lower, Fraction(0))
    upper_mass = sum(exact_upper, Fraction(0))
    if not lower_mass <= 1 <= upper_mass:
        raise SemanticReplayFailure("initial component box misses exact unit mass")
    witness_digest = _unit_mass_witness_sha256(exact_lower, exact_upper)
    if witness_digest != declared_unit_mass_witness_sha256:
        raise SemanticReplayFailure("initial unit-mass witness binding changed")
    expected_nominal = np.asarray(component_box.intervals[:, 0], dtype=np.float64)
    if not np.array_equal(initial_nominal, expected_nominal):
        raise SemanticReplayFailure("initial nominal is not the component lower endpoint")
    expected_radius = Fraction(1) - lower_mass
    if initial_radius != expected_radius:
        raise SemanticReplayFailure("initial radius is not the exact unit-mass anchor radius")
    return IndependentInitialTargetReplay(
        component_box_raw_sha256=component_box.manifest.raw_sha256,
        component_box_manifest_sha256=manifest_digest,
        unit_mass_witness_sha256=witness_digest,
        exact_lower_mass=lower_mass,
        exact_upper_mass=upper_mass,
        exact_anchor_radius=expected_radius,
        nominal_is_component_lower_endpoint=True,
        canonical_unit_mass_witness_recomputed=True,
        producer_target_binding_consumed=False,
    )


def _exact_float(value: object, *, label: str, nonnegative: bool = True) -> Fraction:
    if type(value) is not float or not math.isfinite(value):
        raise SemanticReplayFailure(f"{label} is not a finite built-in float")
    if nonnegative and (value < 0 or (value == 0.0 and math.copysign(1.0, value) < 0.0)):
        raise SemanticReplayFailure(f"{label} is not canonical nonnegative binary64")
    return Fraction.from_float(value)


def _strides(shape: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(math.prod(shape[index + 1 :]) for index in range(len(shape)))


def _edge_target(
    source: int,
    *,
    coordinate: int,
    size: int,
    stride: int,
    periodic: bool,
    forward: bool,
) -> int | None:
    if forward:
        if coordinate + 1 < size:
            return source + stride
        if periodic:
            return source - (size - 1) * stride
        return None
    if coordinate > 0:
        return source - stride
    if periodic:
        return source + (size - 1) * stride
    return None


def _coefficient_deviation(
    centre: Fraction,
    lower: Fraction,
    upper: Fraction,
    *,
    label: str,
) -> Fraction:
    if not 0 <= lower <= upper or centre < 0:
        raise SemanticReplayFailure(f"{label} interval or centre is invalid")
    # The packed centre is deliberately rounded in a fixed direction and can
    # sit one ulp just outside the physical coefficient interval.  Distance
    # to both endpoints, rather than membership, is the correct perturbation
    # bound for that independently reconstructed centre.
    return max(abs(centre - lower), abs(upper - centre))


def _reconstruct_dense_p(
    kernel: packed.PackedTensorKernel,
) -> tuple[tuple[tuple[_Transition, ...], ...], IndependentDenseActionReplay]:
    packed.validate_packed_tensor_kernel(kernel)
    states = kernel.states
    if states < 1 or states > MAX_STATES:
        raise SemanticReplayFailure("kernel state count is outside the replay cap")
    rate = _bounded_fraction(kernel.rate_fraction, label="uniformization rate")
    if rate <= 0:
        raise SemanticReplayFailure("uniformization rate must be positive")

    shape = kernel.contract.tensor_shape
    strides = _strides(shape)
    transitions: list[tuple[_Transition, ...]] = []
    maximum_deviation = Fraction(0)
    central_subprobability = True
    box_subprobability = True

    for source in range(states):
        entries: list[_Transition] = []
        self_centre = _exact_float(
            float(kernel.p_self_center[source]),
            label="central P self coefficient",
        )
        exit_lower = _exact_float(
            float(kernel.killing.intervals[source, 0]),
            label="killing lower",
        )
        exit_upper = _exact_float(
            float(kernel.killing.intervals[source, 1]),
            label="killing upper",
        )
        off_centre_sum = Fraction(0)
        column_deviation = Fraction(0)

        for dimension, (axis, stride) in enumerate(zip(kernel.axes, strides, strict=True)):
            coordinate = (source // stride) % axis.size
            for forward, interval_source, centre_source in (
                (True, axis.forward, kernel.p_forward_center[dimension]),
                (False, axis.backward, kernel.p_backward_center[dimension]),
            ):
                lower_rate = _exact_float(
                    float(interval_source.intervals[coordinate, 0]),
                    label="edge-rate lower",
                )
                upper_rate = _exact_float(
                    float(interval_source.intervals[coordinate, 1]),
                    label="edge-rate upper",
                )
                centre = _exact_float(
                    float(centre_source[coordinate]),
                    label="central P edge coefficient",
                )
                lower = lower_rate / rate
                upper = upper_rate / rate
                column_deviation += _coefficient_deviation(
                    centre,
                    lower,
                    upper,
                    label="P edge",
                )
                exit_lower += lower_rate
                exit_upper += upper_rate
                off_centre_sum += centre
                target = _edge_target(
                    source,
                    coordinate=coordinate,
                    size=axis.size,
                    stride=stride,
                    periodic=axis.periodic,
                    forward=forward,
                )
                if target is None:
                    if lower != 0 or upper != 0 or centre != 0:
                        raise SemanticReplayFailure("reflecting boundary has a nonzero edge")
                else:
                    entries.append(_Transition(target=target, coefficient=centre))

        self_lower = 1 - exit_upper / rate
        self_upper = 1 - exit_lower / rate
        if self_lower < 0 or self_upper > 1:
            box_subprobability = False
            raise SemanticReplayFailure("rate box is not uniformly substochastic")
        column_deviation += _coefficient_deviation(
            self_centre,
            self_lower,
            self_upper,
            label="P self",
        )
        entries.insert(0, _Transition(target=source, coefficient=self_centre))
        central_column_sum = self_centre + off_centre_sum
        if not 0 <= central_column_sum <= 1:
            central_subprobability = False
            raise SemanticReplayFailure("central P column is not substochastic")
        maximum_deviation = max(maximum_deviation, column_deviation)
        transitions.append(tuple(entries))

    replay = IndependentDenseActionReplay(
        state_count=states,
        maximum_column_l1_deviation=maximum_deviation,
        central_columns_subprobability=central_subprobability,
        every_rate_box_column_subprobability=box_subprobability,
        raw_interval_endpoints_consumed=True,
        producer_action_ledger_consumed=False,
    )
    return tuple(transitions), replay


def _alternating_exp_minus(
    mean: Fraction,
    *,
    width_target: Fraction,
) -> tuple[Fraction, Fraction, int]:
    if mean == 0:
        return Fraction(1), Fraction(1), 0
    partial = Fraction(1)
    term = Fraction(1)
    upper = Fraction(1)
    lower = Fraction(0)
    for degree in range(1, MAX_ALTERNATING_DEGREE + 1):
        term *= -mean / degree
        partial += term
        if degree % 2:
            lower = partial
        else:
            upper = partial
        if lower >= 0 and upper >= lower and upper - lower <= width_target:
            _bounded_fraction(lower, label="alternating exponential lower")
            _bounded_fraction(upper, label="alternating exponential upper")
            return lower, upper, degree
    raise SemanticReplayFailure("alternating exponential did not meet its exact target")


def _independent_poisson(
    mean: Fraction,
    *,
    terms: int,
    tail_tolerance: Fraction,
) -> IndependentPoissonReplay:
    mean = _bounded_fraction(mean, label="Poisson mean")
    tolerance = _bounded_fraction(tail_tolerance, label="tail tolerance")
    if mean < 0 or mean > MAX_MEAN:
        raise SemanticReplayFailure("Poisson mean is outside the replay cap")
    if type(terms) is not int or terms < 1 or terms > MAX_TERMS:
        raise SemanticReplayFailure("Poisson term count is outside the replay cap")
    if tolerance <= 0 or tolerance > Fraction(1, 4):
        raise SemanticReplayFailure("tail tolerance is outside the replay range")

    width_target = tolerance / (4_096 * (terms + 1))
    lower_zero, upper_zero, degree = _alternating_exp_minus(
        mean,
        width_target=width_target,
    )
    weights: list[ExactWeightInterval] = []
    factor = Fraction(1)
    included_lower = Fraction(0)
    for index in range(terms):
        if index:
            factor *= mean / index
        lower = lower_zero * factor
        upper = upper_zero * factor
        _bounded_fraction(lower, label="independent Poisson weight lower")
        _bounded_fraction(upper, label="independent Poisson weight upper")
        weights.append(ExactWeightInterval(index=index, lower=lower, upper=upper))
        included_lower += lower
    normalization_tail = 1 - included_lower
    if normalization_tail < 0:
        raise SemanticReplayFailure("independent lower Poisson mass exceeded one")
    first_omitted = weights[-1].upper * mean / terms
    ratio = mean / (terms + 1)
    geometric_tail = first_omitted / (1 - ratio)
    tail = min(normalization_tail, geometric_tail)
    _bounded_fraction(tail, label="independent Poisson tail")
    if tail > tolerance:
        raise SemanticReplayFailure("producer term count misses independent tail tolerance")
    return IndependentPoissonReplay(
        mean=mean,
        alternating_degree=degree,
        exp_minus_mean_lower=lower_zero,
        exp_minus_mean_upper=upper_zero,
        weights=tuple(weights),
        tail_probability_upper=tail,
        requested_tail_tolerance=tolerance,
        recurrence_exact=True,
        alternating_bracket_exact=True,
        producer_poisson_ledger_consumed=False,
    )


def _exact_vector(values: np.ndarray, *, states: int, label: str) -> tuple[Fraction, ...]:
    if (
        type(values) is not np.ndarray
        or values.dtype != np.dtype(np.float64)
        or values.shape != (states,)
        or not values.dtype.isnative
        or not values.flags.c_contiguous
        or not bool(np.all(np.isfinite(values)))
        or bool(np.any(values < 0.0))
    ):
        raise SemanticReplayFailure(f"{label} is not canonical nonnegative float64")
    if any(value == 0.0 and math.copysign(1.0, float(value)) < 0.0 for value in values):
        raise SemanticReplayFailure(f"{label} contains negative zero")
    return tuple(Fraction.from_float(float(value)) for value in values)


def _apply_central_p(
    transitions: tuple[tuple[_Transition, ...], ...],
    vector: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    output = [Fraction(0) for _ in vector]
    for source, value in enumerate(vector):
        for transition in transitions[source]:
            output[transition.target] += transition.coefficient * value
    for value in output:
        _bounded_fraction(value, label="dense central action entry")
    return tuple(output)


def replay_tiny_uniformization_semantics(
    kernel: packed.PackedTensorKernel,
    *,
    initial_component_box: packed.CanonicalPackedIntervals,
    initial_nominal: np.ndarray,
    initial_l1_radius_exact_upper: Fraction,
    target_mass_cap: Fraction,
    declared_component_box_raw_sha256: str,
    declared_component_box_manifest_sha256: str,
    declared_unit_mass_witness_sha256: str,
    time: Fraction,
    tail_tolerance: Fraction,
    poisson_terms: int,
    producer_nominal: np.ndarray,
    producer_l1_radius_exact_upper: Fraction,
) -> IndependentSemanticReplayResult:
    """Recompute a semantic enclosure and require producer-ball containment."""

    transitions, action = _reconstruct_dense_p(kernel)
    states = action.state_count
    initial = _exact_vector(initial_nominal, states=states, label="initial nominal")
    producer = _exact_vector(producer_nominal, states=states, label="producer nominal")
    initial_radius = _bounded_fraction(
        initial_l1_radius_exact_upper,
        label="initial l1 radius",
    )
    initial_target = _replay_initial_target(
        initial_component_box,
        initial_nominal=initial_nominal,
        initial_radius=initial_radius,
        declared_component_box_raw_sha256=declared_component_box_raw_sha256,
        declared_component_box_manifest_sha256=declared_component_box_manifest_sha256,
        declared_unit_mass_witness_sha256=declared_unit_mass_witness_sha256,
    )
    mass_cap = _bounded_fraction(target_mass_cap, label="target mass cap")
    run_time = _bounded_fraction(time, label="time")
    producer_radius = _bounded_fraction(
        producer_l1_radius_exact_upper,
        label="producer l1 radius",
    )
    if initial_radius < 0 or mass_cap != 1 or run_time < 0 or producer_radius < 0:
        raise SemanticReplayFailure("primitive target or run bounds are invalid")
    initial_mass = sum(initial, Fraction(0))
    if initial_mass > mass_cap + initial_radius:
        raise SemanticReplayFailure("initial ball cannot contain the mass-capped target")

    mean = kernel.rate_fraction * run_time
    poisson = _independent_poisson(
        mean,
        terms=poisson_terms,
        tail_tolerance=tail_tolerance,
    )
    accumulator = [Fraction(0) for _ in range(states)]
    accumulated_radius = Fraction(0)
    current = initial
    current_radius = initial_radius
    for position, weight in enumerate(poisson.weights):
        centre_mass = sum(current, Fraction(0))
        for index in range(states):
            accumulator[index] += weight.lower * current[index]
        accumulated_radius += weight.upper * current_radius
        accumulated_radius += (weight.upper - weight.lower) * centre_mass
        _bounded_fraction(accumulated_radius, label="accumulated semantic radius")
        for value in accumulator:
            _bounded_fraction(value, label="semantic accumulator entry")
        if position + 1 < len(poisson.weights):
            current_radius += action.maximum_column_l1_deviation * centre_mass
            _bounded_fraction(current_radius, label="propagated semantic radius")
            current = _apply_central_p(transitions, current)
    accumulated_radius += poisson.tail_probability_upper * mass_cap

    exact_accumulator = tuple(accumulator)
    centre_distance = sum(
        (abs(left - right) for left, right in zip(producer, exact_accumulator, strict=True)),
        Fraction(0),
    )
    required = centre_distance + accumulated_radius
    if required > producer_radius:
        raise SemanticReplayFailure(
            "producer ball does not contain the independent semantic replay"
        )
    return IndependentSemanticReplayResult(
        state_count=states,
        time=run_time,
        exact_accumulator=exact_accumulator,
        independent_l1_radius_upper=accumulated_radius,
        producer_centre_distance=centre_distance,
        required_producer_radius=required,
        supplied_producer_radius=producer_radius,
        containment_margin=producer_radius - required,
        poisson=poisson,
        action=action,
        initial_target=initial_target,
        producer_ball_contains_independent_replay=True,
        independent_code_path=True,
        producer_ledgers_consumed=False,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        topology_complete=False,
        production_resource_gate=False,
        f0_pass=False,
        status=STATUS,
    )
