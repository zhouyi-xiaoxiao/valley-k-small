"""Science-free target-aware adapter for the frozen tiny uniformization.

The Round-162 primitive requires the *whole* symmetric ``l1`` input ball to
lie in the nonnegative subprobability simplex.  That is stronger than the
physical initial-law statement: the true target is nonnegative and has mass
one, but a convenient symmetric enclosure may include signed vectors (and a
compactly supported target necessarily has zero nominal components).

This successor layer keeps those statements separate.  From a canonical
nonnegative component box intersecting the unit simplex it constructs and
binds one deterministic exact unit-mass witness, chooses the lower box
endpoint as a nonnegative subprobability anchor, runs the frozen zero-radius
primitive on that anchor, and adds the complete input-anchor ``l1`` distance
to the returned radius.  Sub-Markov ``l1`` contraction makes that addition
rigorous, including for repeated time chunks.  Binding a future physical
box to its analytic source is a separate, still-open F0 task.

The module remains deliberately tiny, same-process, science-free, and
non-authoritative.  It does not implement jets, topology, a clean replay, a
production resource gate, or F0 acceptance.
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
import rate_defined_tensor_f0_packed_rate_action as rate_action
import rate_defined_tensor_f0_packed_uniformization as frozen

ACCEPTED_UNIFORMIZATION_SOURCE_SHA256: Final = (
    "20c95975b5e43fcd5ed2ccd91c578c32524f6a3b2cc4ab5133da36fc3eddb72c"
)
ACCEPTED_UNIFORMIZATION_TEST_SHA256: Final = (
    "dcd3d1c6ae36059a13f98fc9ee9e7409b512ac72e59a25274a3df0e4bdcbd4cd"
)
ACCEPTED_UNIFORMIZATION_TEST_NAME: Final = "test_rate_defined_tensor_f0_packed_uniformization.py"

TARGET_BALL_SCHEMA: Final = "science_free_nonnegative_target_l1_ball_v1"
TARGET_RESULT_SCHEMA: Final = "science_free_target_uniformization_result_v1"
INITIAL_BOX_ROLE: Final = "science_free_initial_target_component_box"
UNIT_MASS_CONSTRUCTION: Final = "lexicographic_lower_fill_exact_unit_mass_v1"
METHOD_STATUS: Final = "PASS_TARGET_AWARE_TINY_METHOD_ONLY_NOT_F0"
MAX_EXACT_INTEGER_BITS: Final = 4_096


class TargetUniformizationFailure(RuntimeError):
    """Fail-closed error for the bounded target-aware method layer."""


@dataclass(frozen=True, slots=True)
class CertifiedTargetBall:
    """A ball enclosing one target with separate positivity/mass facts."""

    schema: str
    logical_shape: tuple[int, ...]
    nominal: np.ndarray
    nominal_raw_sha256: str
    l1_radius_exact_upper: Fraction
    l1_radius_upper: float
    l1_radius_upper_hex: str
    target_nonnegative: bool
    target_mass_cap: Fraction
    canonical_unit_mass_witness_proved: bool
    component_box_raw_sha256: str
    component_box_manifest_sha256: str
    unit_mass_witness_sha256: str
    unit_mass_construction: str
    operator_binding_established: bool
    kernel_replay_sha256: str
    rate_action_contract_sha256: str
    cumulative_time: Fraction
    cumulative_chunk_count: int
    predecessor_binding_sha256: str
    binding_sha256: str
    whole_symmetric_ball_nonnegative_required: bool
    whole_symmetric_ball_subprobability_required: bool
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class TargetAnchorLedger:
    input_nominal_mass: Fraction
    anchor_nominal_mass: Fraction
    target_mass_cap: Fraction
    input_to_anchor_l1_exact: Fraction
    anchor_scale_exact: Fraction
    anchor_was_mass_projected: bool
    anchor_nonnegative: bool
    anchor_subprobability: bool
    signed_error_contraction_used: bool
    target_nonnegativity_used_only_as_invariant: bool


@dataclass(frozen=True, slots=True)
class TargetUniformizationResult:
    schema: str
    nominal: np.ndarray
    nominal_raw_sha256: str
    l1_radius_exact_upper: Fraction
    l1_radius_upper: float
    l1_radius_upper_hex: str
    time: Fraction
    tail_tolerance: Fraction
    uniformization_rate: Fraction
    poisson_terms_used: int
    maximum_terms_requested: int
    target: CertifiedTargetBall
    anchor: TargetAnchorLedger
    frozen_method_radius_exact_upper: Fraction
    inherited_input_radius_exact_upper: Fraction
    frozen_source_sha256: str
    frozen_test_sha256: str
    frozen_exact_bytes_matched: bool
    frozen_result_status: str
    status: str
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    science_executed: bool
    jets_complete: bool
    topology_complete: bool
    independent_semantic_replay_complete: bool
    production_resource_gate: bool
    f0_pass: bool


def _sha256_raw(array: np.ndarray) -> str:
    return hashlib.sha256(memoryview(array).cast("B")).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _stream_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    scratch = bytearray(4_096)
    with path.open("rb", buffering=0) as source:
        while True:
            count = source.readinto(scratch)
            if not count:
                break
            digest.update(memoryview(scratch)[:count])
    return digest.hexdigest()


def _verify_frozen_bytes() -> tuple[str, str]:
    source = Path(frozen.__file__).resolve()
    test = source.with_name(ACCEPTED_UNIFORMIZATION_TEST_NAME)
    source_digest = _stream_sha256(source)
    test_digest = _stream_sha256(test)
    if (
        source_digest != ACCEPTED_UNIFORMIZATION_SOURCE_SHA256
        or test_digest != ACCEPTED_UNIFORMIZATION_TEST_SHA256
    ):
        raise TargetUniformizationFailure("frozen uniformization byte binding changed")
    return source_digest, test_digest


def _bounded_fraction(value: object, *, label: str) -> Fraction:
    if type(value) is not Fraction:
        raise TargetUniformizationFailure(f"{label} must be an exact Fraction")
    if (
        value.numerator.bit_length() > MAX_EXACT_INTEGER_BITS
        or value.denominator.bit_length() > MAX_EXACT_INTEGER_BITS
    ):
        raise TargetUniformizationFailure(f"{label} exceeds the exact-integer cap")
    return value


def _float_upper(value: Fraction) -> float:
    if value < 0:
        raise TargetUniformizationFailure("cannot round a negative radius upward")
    candidate = float(value)
    if not math.isfinite(candidate):
        raise TargetUniformizationFailure("radius does not fit binary64")
    if Fraction.from_float(candidate) < value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    if Fraction.from_float(candidate) < value:
        raise TargetUniformizationFailure("radius conversion was not outward")
    return candidate


def _float_lower(value: Fraction) -> float:
    if value < 0:
        raise TargetUniformizationFailure("cannot round a negative anchor downward")
    candidate = float(value)
    if not math.isfinite(candidate):
        raise TargetUniformizationFailure("anchor does not fit binary64")
    if Fraction.from_float(candidate) > value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(-math.inf)))
    if candidate < 0 or Fraction.from_float(candidate) > value:
        raise TargetUniformizationFailure("anchor conversion was not downward")
    if candidate == 0.0:
        candidate = 0.0
    return candidate


def _digest_fields(domain: bytes, *fields: object) -> str:
    digest = hashlib.sha256(domain)
    for field in fields:
        encoded = str(field).encode("ascii")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _target_binding(target: CertifiedTargetBall) -> str:
    return _digest_fields(
        b"science-free-target-ball-v1\x00",
        target.schema,
        *target.logical_shape,
        target.nominal_raw_sha256,
        target.l1_radius_exact_upper.numerator,
        target.l1_radius_exact_upper.denominator,
        target.l1_radius_upper_hex,
        target.target_nonnegative,
        target.target_mass_cap.numerator,
        target.target_mass_cap.denominator,
        target.canonical_unit_mass_witness_proved,
        target.component_box_raw_sha256,
        target.component_box_manifest_sha256,
        target.unit_mass_witness_sha256,
        target.unit_mass_construction,
        target.operator_binding_established,
        target.kernel_replay_sha256,
        target.rate_action_contract_sha256,
        target.cumulative_time.numerator,
        target.cumulative_time.denominator,
        target.cumulative_chunk_count,
        target.predecessor_binding_sha256,
        target.whole_symmetric_ball_nonnegative_required,
        target.whole_symmetric_ball_subprobability_required,
    )


def _canonical_nominal(values: np.ndarray, *, shape: tuple[int, ...]) -> np.ndarray:
    if (
        type(values) is not np.ndarray
        or values.dtype != np.dtype(np.float64)
        or values.shape != (math.prod(shape),)
        or not values.dtype.isnative
        or not values.flags.c_contiguous
        or not values.flags.aligned
        or not values.flags.owndata
        or values.base is not None
        or values.flags.writeable
    ):
        raise TargetUniformizationFailure("target nominal is not canonical owned float64")
    if not bool(np.all(np.isfinite(values))) or bool(np.any(values < 0.0)):
        raise TargetUniformizationFailure("target nominal is not nonnegative finite")
    if any(value == 0.0 and math.copysign(1.0, float(value)) < 0.0 for value in values):
        raise TargetUniformizationFailure("target nominal contains negative zero")
    return values


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


def _unit_mass_witness(
    exact_lower: tuple[Fraction, ...],
    exact_upper: tuple[Fraction, ...],
) -> tuple[tuple[Fraction, ...], str]:
    residual = Fraction(1) - sum(exact_lower, Fraction(0))
    witness = list(exact_lower)
    for index, (lower, upper) in enumerate(zip(exact_lower, exact_upper, strict=True)):
        increment = min(residual, upper - lower)
        witness[index] += increment
        residual -= increment
    if residual != 0 or sum(witness, Fraction(0)) != 1:
        raise TargetUniformizationFailure("component box has no canonical unit-mass witness")
    digest_fields: list[object] = [UNIT_MASS_CONSTRUCTION, len(witness)]
    for value in witness:
        _bounded_fraction(value, label="unit-mass witness entry")
        digest_fields.extend((value.numerator, value.denominator))
    return tuple(witness), _digest_fields(
        b"science-free-exact-unit-mass-witness-v1\x00",
        *digest_fields,
    )


def validate_target_ball_structure_only(target: CertifiedTargetBall) -> None:
    """Validate in-memory schema relations, not external target provenance."""
    if type(target) is not CertifiedTargetBall:
        raise TargetUniformizationFailure("target ball has the wrong exact type")
    nominal = _canonical_nominal(target.nominal, shape=target.logical_shape)
    radius = _bounded_fraction(target.l1_radius_exact_upper, label="target radius")
    cap = _bounded_fraction(target.target_mass_cap, label="target mass cap")
    cumulative_time = _bounded_fraction(target.cumulative_time, label="cumulative time")
    if (
        target.schema != TARGET_BALL_SCHEMA
        or radius < 0
        or target.nominal_raw_sha256 != _sha256_raw(nominal)
        or target.l1_radius_upper_hex != target.l1_radius_upper.hex()
        or not math.isfinite(target.l1_radius_upper)
        or target.l1_radius_upper < 0
        or Fraction.from_float(target.l1_radius_upper) < radius
        or target.target_nonnegative is not True
        or cap != 1
        or target.canonical_unit_mass_witness_proved is not True
        or not _is_sha256(target.component_box_raw_sha256)
        or not _is_sha256(target.component_box_manifest_sha256)
        or not _is_sha256(target.unit_mass_witness_sha256)
        or target.component_box_raw_sha256 == "0" * 64
        or target.component_box_manifest_sha256 == "0" * 64
        or target.unit_mass_witness_sha256 == "0" * 64
        or target.unit_mass_construction != UNIT_MASS_CONSTRUCTION
        or type(target.operator_binding_established) is not bool
        or not _is_sha256(target.kernel_replay_sha256)
        or not _is_sha256(target.rate_action_contract_sha256)
        or cumulative_time < 0
        or type(target.cumulative_chunk_count) is not int
        or target.cumulative_chunk_count < 0
        or not _is_sha256(target.predecessor_binding_sha256)
        or not _is_sha256(target.binding_sha256)
        or target.binding_sha256 != _target_binding(target)
        or target.whole_symmetric_ball_nonnegative_required is not False
        or target.whole_symmetric_ball_subprobability_required is not False
        or target.non_authoritative is not True
        or target.science_free is not True
        or target.fresh_process is not False
        or target.f0_pass is not False
    ):
        raise TargetUniformizationFailure("target ball ledger is invalid")
    if target.operator_binding_established:
        if (
            target.kernel_replay_sha256 == "0" * 64
            or target.rate_action_contract_sha256 == "0" * 64
            or target.cumulative_chunk_count < 1
        ):
            raise TargetUniformizationFailure("established target operator binding is invalid")
    elif (
        target.kernel_replay_sha256 != "0" * 64
        or target.rate_action_contract_sha256 != "0" * 64
        or cumulative_time != 0
        or target.cumulative_chunk_count != 0
    ):
        raise TargetUniformizationFailure("unbound initial target has operator history")
    nominal_mass = sum(
        (Fraction.from_float(float(value)) for value in nominal),
        Fraction(0),
    )
    if nominal_mass > cap + radius:
        raise TargetUniformizationFailure("target ball cannot contain the declared mass cap")


def make_initial_target_ball(
    component_box: packed.CanonicalPackedIntervals,
) -> CertifiedTargetBall:
    """Bind a nonnegative component box containing an exact unit-mass target."""

    packed.validate_canonical_packed_intervals(component_box)
    if (
        component_box.manifest.role != INITIAL_BOX_ROLE
        or component_box.manifest.nonnegative is not True
    ):
        raise TargetUniformizationFailure("initial component-box metadata is invalid")

    exact_lower = tuple(
        Fraction.from_float(float(value)) for value in component_box.intervals[:, 0]
    )
    exact_upper = tuple(
        Fraction.from_float(float(value)) for value in component_box.intervals[:, 1]
    )
    lower_mass = sum(exact_lower, Fraction(0))
    upper_mass = sum(exact_upper, Fraction(0))
    if not lower_mass <= 1 <= upper_mass:
        raise TargetUniformizationFailure("component box does not contain unit total mass")
    _, witness_digest = _unit_mass_witness(exact_lower, exact_upper)

    nominal = np.array(component_box.intervals[:, 0], dtype=np.float64, copy=True, order="C")
    nominal.setflags(write=False)
    box_diameter_from_lower = sum(
        (upper - lower for lower, upper in zip(exact_lower, exact_upper, strict=True)),
        Fraction(0),
    )
    # The target has exact mass one and is componentwise above the lower
    # endpoint.  Hence its exact l1 distance from the lower anchor is
    # ``1-sum(lower)``, not the generally wider independent-box diameter.
    radius = Fraction(1) - lower_mass
    if radius < 0 or radius > box_diameter_from_lower:
        raise TargetUniformizationFailure("unit-mass target radius escaped component box")
    _bounded_fraction(radius, label="component-box l1 radius")
    radius_float = _float_upper(radius)
    raw = _sha256_raw(nominal)
    predecessor = _digest_fields(
        b"science-free-initial-target-source-v1\x00",
        component_box.manifest.raw_sha256,
        _component_manifest_sha256(component_box.manifest),
        witness_digest,
        1,
    )
    provisional = CertifiedTargetBall(
        schema=TARGET_BALL_SCHEMA,
        logical_shape=component_box.manifest.logical_shape,
        nominal=nominal,
        nominal_raw_sha256=raw,
        l1_radius_exact_upper=radius,
        l1_radius_upper=radius_float,
        l1_radius_upper_hex=radius_float.hex(),
        target_nonnegative=True,
        target_mass_cap=Fraction(1),
        canonical_unit_mass_witness_proved=True,
        component_box_raw_sha256=component_box.manifest.raw_sha256,
        component_box_manifest_sha256=_component_manifest_sha256(component_box.manifest),
        unit_mass_witness_sha256=witness_digest,
        unit_mass_construction=UNIT_MASS_CONSTRUCTION,
        operator_binding_established=False,
        kernel_replay_sha256="0" * 64,
        rate_action_contract_sha256="0" * 64,
        cumulative_time=Fraction(0),
        cumulative_chunk_count=0,
        predecessor_binding_sha256=predecessor,
        binding_sha256="0" * 64,
        whole_symmetric_ball_nonnegative_required=False,
        whole_symmetric_ball_subprobability_required=False,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        f0_pass=False,
    )
    target = CertifiedTargetBall(
        **{
            field: getattr(provisional, field)
            for field in provisional.__dataclass_fields__
            if field != "binding_sha256"
        },
        binding_sha256=_target_binding(provisional),
    )
    validate_target_ball_structure_only(target)
    return target


def _subprobability_anchor(
    target: CertifiedTargetBall,
) -> tuple[np.ndarray, TargetAnchorLedger]:
    nominal_mass = sum(
        (Fraction.from_float(float(value)) for value in target.nominal),
        Fraction(0),
    )
    cap = target.target_mass_cap
    scale = Fraction(1) if nominal_mass <= cap or nominal_mass == 0 else cap / nominal_mass
    anchor = np.empty_like(target.nominal)
    for index, value in enumerate(target.nominal):
        anchor[index] = _float_lower(Fraction.from_float(float(value)) * scale)
    anchor.setflags(write=False)
    anchor_mass = sum(
        (Fraction.from_float(float(value)) for value in anchor),
        Fraction(0),
    )
    shift = sum(
        (
            abs(Fraction.from_float(float(left)) - Fraction.from_float(float(right)))
            for left, right in zip(target.nominal, anchor, strict=True)
        ),
        Fraction(0),
    )
    if anchor_mass > cap:
        raise TargetUniformizationFailure("downward anchor projection exceeded mass cap")
    ledger = TargetAnchorLedger(
        input_nominal_mass=nominal_mass,
        anchor_nominal_mass=anchor_mass,
        target_mass_cap=cap,
        input_to_anchor_l1_exact=shift,
        anchor_scale_exact=scale,
        anchor_was_mass_projected=nominal_mass > cap,
        anchor_nonnegative=True,
        anchor_subprobability=True,
        signed_error_contraction_used=True,
        target_nonnegativity_used_only_as_invariant=True,
    )
    return anchor, ledger


def _next_target(
    *,
    nominal: np.ndarray,
    radius: Fraction,
    predecessor: CertifiedTargetBall,
    kernel_replay_sha256: str,
    rate_action_contract_sha256: str,
    time: Fraction,
    tail_tolerance: Fraction,
    maximum_terms: int,
) -> CertifiedTargetBall:
    radius_float = _float_upper(radius)
    raw = _sha256_raw(nominal)
    predecessor_binding = _digest_fields(
        b"science-free-target-chunk-v1\x00",
        predecessor.binding_sha256,
        kernel_replay_sha256,
        rate_action_contract_sha256,
        time.numerator,
        time.denominator,
        tail_tolerance.numerator,
        tail_tolerance.denominator,
        maximum_terms,
        raw,
        radius.numerator,
        radius.denominator,
    )
    provisional = CertifiedTargetBall(
        schema=TARGET_BALL_SCHEMA,
        logical_shape=predecessor.logical_shape,
        nominal=nominal,
        nominal_raw_sha256=raw,
        l1_radius_exact_upper=radius,
        l1_radius_upper=radius_float,
        l1_radius_upper_hex=radius_float.hex(),
        target_nonnegative=True,
        target_mass_cap=predecessor.target_mass_cap,
        canonical_unit_mass_witness_proved=predecessor.canonical_unit_mass_witness_proved,
        component_box_raw_sha256=predecessor.component_box_raw_sha256,
        component_box_manifest_sha256=predecessor.component_box_manifest_sha256,
        unit_mass_witness_sha256=predecessor.unit_mass_witness_sha256,
        unit_mass_construction=predecessor.unit_mass_construction,
        operator_binding_established=True,
        kernel_replay_sha256=kernel_replay_sha256,
        rate_action_contract_sha256=rate_action_contract_sha256,
        cumulative_time=predecessor.cumulative_time + time,
        cumulative_chunk_count=predecessor.cumulative_chunk_count + 1,
        predecessor_binding_sha256=predecessor_binding,
        binding_sha256="0" * 64,
        whole_symmetric_ball_nonnegative_required=False,
        whole_symmetric_ball_subprobability_required=False,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        f0_pass=False,
    )
    target = CertifiedTargetBall(
        **{
            field: getattr(provisional, field)
            for field in provisional.__dataclass_fields__
            if field != "binding_sha256"
        },
        binding_sha256=_target_binding(provisional),
    )
    validate_target_ball_structure_only(target)
    return target


def target_uniformize_transpose(
    kernel: packed.PackedTensorKernel,
    target: CertifiedTargetBall,
    contract: rate_action.RateActionContract,
    *,
    time: Fraction,
    tail_tolerance: Fraction,
    maximum_terms: int = frozen.MAX_TINY_POISSON_TERMS,
) -> TargetUniformizationResult:
    """Propagate one certified target through one frozen tiny time chunk."""

    source_digest, test_digest = _verify_frozen_bytes()
    validate_target_ball_structure_only(target)
    packed.validate_packed_tensor_kernel(kernel)
    rate_action.validate_rate_action_contract(contract)
    kernel_replay = packed._kernel_replay_digest(kernel)
    contract_digest = rate_action.rate_action_contract_sha256(contract)
    time = _bounded_fraction(time, label="time")
    tail_tolerance = _bounded_fraction(tail_tolerance, label="tail tolerance")
    if (
        time < 0
        or target.logical_shape != kernel.contract.tensor_shape
        or target.logical_shape != contract.tensor_shape
    ):
        raise TargetUniformizationFailure("target, kernel, contract, or time disagrees")
    if target.operator_binding_established and (
        target.kernel_replay_sha256 != kernel_replay
        or target.rate_action_contract_sha256 != contract_digest
    ):
        raise TargetUniformizationFailure("target chunk changed its fixed operator binding")

    anchor_values, anchor_ledger = _subprobability_anchor(target)
    raw = _sha256_raw(anchor_values)
    vector = packed.CanonicalFloat64Vector(
        logical_shape=target.logical_shape,
        values=anchor_values,
        raw_sha256=raw,
        nonnegative=True,
        source_sha256=_digest_fields(
            b"science-free-target-anchor-vector-v1\x00",
            target.binding_sha256,
            raw,
        ),
    )
    packed.validate_canonical_vector(vector, block_size=contract.block_size)
    zero_input = rate_action.make_internal_point_ball_input(
        vector,
        input_l1_radius_upper=0.0,
        radius_provenance_sha256=_digest_fields(
            b"science-free-zero-anchor-radius-v1\x00",
            target.binding_sha256,
            raw,
        ),
    )
    base = frozen.tiny_uniformize_transpose(
        kernel,
        zero_input,
        contract,
        time=time,
        tail_tolerance=tail_tolerance,
        maximum_terms=maximum_terms,
    )

    inherited = target.l1_radius_exact_upper + anchor_ledger.input_to_anchor_l1_exact
    total_radius = base.l1_radius_exact_upper + inherited
    _bounded_fraction(total_radius, label="target output radius")
    next_target = _next_target(
        nominal=base.nominal,
        radius=total_radius,
        predecessor=target,
        kernel_replay_sha256=kernel_replay,
        rate_action_contract_sha256=contract_digest,
        time=time,
        tail_tolerance=tail_tolerance,
        maximum_terms=maximum_terms,
    )
    result = TargetUniformizationResult(
        schema=TARGET_RESULT_SCHEMA,
        nominal=base.nominal,
        nominal_raw_sha256=base.nominal_raw_sha256,
        l1_radius_exact_upper=total_radius,
        l1_radius_upper=next_target.l1_radius_upper,
        l1_radius_upper_hex=next_target.l1_radius_upper_hex,
        time=time,
        tail_tolerance=tail_tolerance,
        uniformization_rate=base.uniformization_rate,
        poisson_terms_used=len(base.poisson.weights),
        maximum_terms_requested=maximum_terms,
        target=next_target,
        anchor=anchor_ledger,
        frozen_method_radius_exact_upper=base.l1_radius_exact_upper,
        inherited_input_radius_exact_upper=inherited,
        frozen_source_sha256=source_digest,
        frozen_test_sha256=test_digest,
        frozen_exact_bytes_matched=True,
        frozen_result_status=base.status,
        status=METHOD_STATUS,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        science_executed=False,
        jets_complete=False,
        topology_complete=False,
        independent_semantic_replay_complete=False,
        production_resource_gate=False,
        f0_pass=False,
    )
    _validate_result_structure_only(result)
    if _verify_frozen_bytes() != (source_digest, test_digest):
        raise TargetUniformizationFailure("frozen bytes changed during target propagation")
    return result


def _validate_result_structure_only(result: TargetUniformizationResult) -> None:
    """Check schema relations only; numerical authority requires semantic replay."""

    if type(result) is not TargetUniformizationResult:
        raise TargetUniformizationFailure("target result has the wrong exact type")
    validate_target_ball_structure_only(result.target)
    if (
        result.schema != TARGET_RESULT_SCHEMA
        or result.nominal is not result.target.nominal
        or result.nominal_raw_sha256 != result.target.nominal_raw_sha256
        or result.l1_radius_exact_upper != result.target.l1_radius_exact_upper
        or result.l1_radius_upper != result.target.l1_radius_upper
        or result.l1_radius_upper_hex != result.target.l1_radius_upper_hex
        or result.l1_radius_exact_upper
        != result.frozen_method_radius_exact_upper + result.inherited_input_radius_exact_upper
        or result.time < 0
        or result.tail_tolerance <= 0
        or result.uniformization_rate <= 0
        or result.poisson_terms_used < 1
        or result.poisson_terms_used > result.maximum_terms_requested
        or result.maximum_terms_requested > frozen.MAX_TINY_POISSON_TERMS
        or result.inherited_input_radius_exact_upper < result.anchor.input_to_anchor_l1_exact
        or result.anchor.target_mass_cap != result.target.target_mass_cap
        or result.anchor.anchor_nominal_mass > result.anchor.target_mass_cap
        or result.anchor.anchor_nonnegative is not True
        or result.anchor.anchor_subprobability is not True
        or result.anchor.signed_error_contraction_used is not True
        or result.anchor.target_nonnegativity_used_only_as_invariant is not True
        or result.frozen_source_sha256 != ACCEPTED_UNIFORMIZATION_SOURCE_SHA256
        or result.frozen_test_sha256 != ACCEPTED_UNIFORMIZATION_TEST_SHA256
        or result.frozen_exact_bytes_matched is not True
        or result.frozen_result_status != frozen.METHOD_STATUS
        or result.status != METHOD_STATUS
        or result.non_authoritative is not True
        or result.science_free is not True
        or result.fresh_process is not False
        or result.science_executed is not False
        or result.jets_complete is not False
        or result.topology_complete is not False
        or result.independent_semantic_replay_complete is not False
        or result.production_resource_gate is not False
        or result.f0_pass is not False
    ):
        raise TargetUniformizationFailure("target uniformization result ledger is invalid")
