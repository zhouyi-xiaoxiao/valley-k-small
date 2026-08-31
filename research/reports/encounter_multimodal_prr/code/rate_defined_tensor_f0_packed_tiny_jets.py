"""Tiny same-process generator jets for the packed rate-defined F0 method.

This successor consumes one operator-bound CertifiedTargetBall and applies the
accepted signed Q-transpose point-plus-l1-ball action four times.  It encloses

    z_r = (Q.T)^r p,                     r = 0,...,4,
    J_r = k.T z_r,                       r = 0,...,3,
    M_r = ||k||_infinity ||z_r||_1,      r = 2,...,4.

The killing reduction is exact over the saved binary64 centres.  Its radius is

    K_infinity e_r + delta_k ||c_r||_1,

where z_r lies in c_r + B_1(e_r), K_infinity bounds every admissible killing
coefficient, and delta_k bounds its componentwise centre uncertainty.

This is a bounded method layer, not an authority boundary.  It is same-process,
exposes NumPy arrays, does not bind the physical origin of the initial component
box, and does not implement full-window topology or a production resource gate.
Consequently every F0 and publication-promotion flag remains false.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Final

import numpy as np
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_interval_action as directed
import rate_defined_tensor_f0_packed_rate_action as rate_action
import rate_defined_tensor_f0_packed_target_uniformization as target_uniformization

JET_STATE_SCHEMA: Final = "science_free_tiny_q_jet_state_v1"
OBSERVABLE_SCHEMA: Final = "science_free_tiny_killing_observable_jet_v1"
MAGNITUDE_SCHEMA: Final = "science_free_tiny_killing_magnitude_bound_v1"
RESULT_SCHEMA: Final = "science_free_tiny_q_jets_result_v1"
METHOD_STATUS: Final = "PASS_TINY_Q_JETS_METHOD_ONLY_NOT_F0"
OBSERVABLE_FORMULA: Final = "K_inf*e+delta_k*nominal_l1_exact_v1"
MAGNITUDE_FORMULA: Final = "K_inf*(nominal_l1_exact+e)_v1"
MAX_TINY_STATES: Final = 64

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
ACCEPTED_TARGET_SOURCE_SHA256: Final = (
    "5acd20fc227defc7573f4a54b2ab543f192719b3bd7be65de5620c2ef4491323"
)
ACCEPTED_TARGET_TEST_SHA256: Final = (
    "72d50b1a1fe711ef95b451238050ccea3f291f7dca98a779ca3887b3380e5878"
)

_RATE_ACTION_TEST_NAME: Final = "test_rate_defined_tensor_f0_packed_rate_action.py"
_TARGET_TEST_NAME: Final = "test_rate_defined_tensor_f0_packed_target_uniformization.py"


class TinyQJetFailure(RuntimeError):
    """Fail-closed error for the bounded tiny-jet method."""


@dataclass(frozen=True, slots=True)
class DependencyByteBinding:
    name: str
    accepted_sha256: str
    observed_sha256: str
    exact_bytes_matched: bool


@dataclass(frozen=True, slots=True)
class TinyQJetState:
    schema: str
    order: int
    nominal: np.ndarray
    nominal_raw_sha256: str
    l1_radius_exact_upper: Fraction
    l1_radius_upper: float
    l1_radius_upper_hex: str
    nominal_nonnegative_proved: bool
    signed_nominal_allowed: bool
    predecessor_binding_sha256: str
    action_input_binding_sha256: str
    action_output_consistency_sha256: str
    state_binding_sha256: str


@dataclass(frozen=True, slots=True)
class KillingObservableJet:
    schema: str
    order: int
    centre_exact: Fraction
    radius_exact_upper: Fraction
    lower: Fraction
    upper: Fraction
    nominal_l1_exact: Fraction
    state_radius_exact_upper: Fraction
    maximum_killing_upper: Fraction
    maximum_killing_uncertainty: Fraction
    formula: str
    binding_sha256: str


@dataclass(frozen=True, slots=True)
class KillingMagnitudeBound:
    schema: str
    order: int
    upper: Fraction
    nominal_l1_exact: Fraction
    state_radius_exact_upper: Fraction
    maximum_killing_upper: Fraction
    formula: str
    binding_sha256: str


@dataclass(frozen=True, slots=True)
class TinyQJetsResult:
    schema: str
    logical_shape: tuple[int, ...]
    target_binding_sha256: str
    kernel_replay_sha256: str
    rate_action_contract_sha256: str
    states: tuple[TinyQJetState, ...]
    observable_jets: tuple[KillingObservableJet, ...]
    magnitude_bounds: tuple[KillingMagnitudeBound, ...]
    dependency_bindings: tuple[DependencyByteBinding, ...]
    result_binding_sha256: str
    status: str
    tiny_q_jets_complete: bool
    full_window_topology_complete: bool
    physical_initial_source_bound: bool
    clean_independent_implementation: bool
    endpoint_oracle_is_external_test_only: bool
    production_resource_gate: bool
    non_authoritative: bool
    science_free: bool
    fresh_process: bool
    science_executed: bool
    f0_pass: bool


def _stream_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    scratch = bytearray(4_096)
    try:
        with path.open("rb", buffering=0) as source:
            while True:
                count = source.readinto(scratch)
                if count == 0:
                    break
                digest.update(memoryview(scratch)[:count])
    except OSError as error:
        raise TinyQJetFailure("accepted dependency bytes cannot be streamed") from error
    return digest.hexdigest()


def _dependency_paths() -> tuple[tuple[str, Path, str], ...]:
    rate_source = Path(rate_action.__file__).resolve()
    target_source = Path(target_uniformization.__file__).resolve()
    return (
        ("packed_source", Path(packed.__file__).resolve(), ACCEPTED_PACKED_SOURCE_SHA256),
        (
            "directed_source",
            Path(directed.__file__).resolve(),
            ACCEPTED_DIRECTED_SOURCE_SHA256,
        ),
        ("rate_action_source", rate_source, ACCEPTED_RATE_ACTION_SOURCE_SHA256),
        (
            "rate_action_test",
            rate_source.with_name(_RATE_ACTION_TEST_NAME),
            ACCEPTED_RATE_ACTION_TEST_SHA256,
        ),
        ("target_source", target_source, ACCEPTED_TARGET_SOURCE_SHA256),
        (
            "target_test",
            target_source.with_name(_TARGET_TEST_NAME),
            ACCEPTED_TARGET_TEST_SHA256,
        ),
    )


def _verify_dependency_bytes() -> tuple[DependencyByteBinding, ...]:
    rows: list[DependencyByteBinding] = []
    for name, path, accepted in _dependency_paths():
        observed = _stream_sha256(path)
        rows.append(
            DependencyByteBinding(
                name=name,
                accepted_sha256=accepted,
                observed_sha256=observed,
                exact_bytes_matched=observed == accepted,
            )
        )
    bindings = tuple(rows)
    if any(not binding.exact_bytes_matched for binding in bindings):
        raise TinyQJetFailure("accepted tiny-jet dependency bytes changed")
    return bindings


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _digest_fields(domain: bytes, *fields: object) -> str:
    digest = hashlib.sha256(domain)
    for field in fields:
        encoded = str(field).encode("ascii")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _raw_sha256(values: np.ndarray) -> str:
    return hashlib.sha256(memoryview(values).cast("B")).hexdigest()


def _float_upper(value: Fraction) -> float:
    if type(value) is not Fraction or value < 0:
        raise TinyQJetFailure("jet radius must be a nonnegative exact Fraction")
    candidate = float(value)
    if not math.isfinite(candidate):
        raise TinyQJetFailure("jet radius does not fit binary64")
    if Fraction.from_float(candidate) < value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    if Fraction.from_float(candidate) < value:
        raise TinyQJetFailure("jet radius conversion was not outward")
    return candidate


def _canonical_nominal(values: object, *, states: int) -> np.ndarray:
    if (
        type(values) is not np.ndarray
        or values.dtype != np.dtype(np.float64)
        or values.shape != (states,)
        or not values.dtype.isnative
        or not values.flags.c_contiguous
        or not values.flags.aligned
        or not values.flags.owndata
        or values.base is not None
        or values.flags.writeable
        or not bool(np.all(np.isfinite(values)))
    ):
        raise TinyQJetFailure("jet nominal is not canonical finite owned float64")
    if any(value == 0.0 and math.copysign(1.0, float(value)) < 0.0 for value in values):
        raise TinyQJetFailure("jet nominal contains negative zero")
    return values


def _state_binding(state: TinyQJetState) -> str:
    return _digest_fields(
        b"science-free-tiny-q-jet-state-v1\x00",
        state.schema,
        state.order,
        state.nominal_raw_sha256,
        state.l1_radius_exact_upper.numerator,
        state.l1_radius_exact_upper.denominator,
        state.l1_radius_upper_hex,
        state.nominal_nonnegative_proved,
        state.signed_nominal_allowed,
        state.predecessor_binding_sha256,
        state.action_input_binding_sha256,
        state.action_output_consistency_sha256,
    )


def _make_state(
    *,
    order: int,
    nominal: np.ndarray,
    radius: Fraction,
    radius_float: float,
    predecessor_binding_sha256: str,
    action_input_binding_sha256: str,
    action_output_consistency_sha256: str,
) -> TinyQJetState:
    raw = _raw_sha256(nominal)
    provisional = TinyQJetState(
        schema=JET_STATE_SCHEMA,
        order=order,
        nominal=nominal,
        nominal_raw_sha256=raw,
        l1_radius_exact_upper=radius,
        l1_radius_upper=radius_float,
        l1_radius_upper_hex=radius_float.hex(),
        nominal_nonnegative_proved=order == 0,
        signed_nominal_allowed=order > 0,
        predecessor_binding_sha256=predecessor_binding_sha256,
        action_input_binding_sha256=action_input_binding_sha256,
        action_output_consistency_sha256=action_output_consistency_sha256,
        state_binding_sha256="0" * 64,
    )
    return replace(provisional, state_binding_sha256=_state_binding(provisional))


def _witnesses(kernel: packed.PackedTensorKernel) -> dict[str, Fraction]:
    values = {witness.name: witness.value for witness in kernel.ledger.witnesses}
    required = {"maximum_killing_upper", "maximum_killing_uncertainty"}
    if not required <= values.keys():
        raise TinyQJetFailure("required killing witnesses are absent")
    return values


def _nominal_l1_exact(state: TinyQJetState) -> Fraction:
    return sum(
        (abs(Fraction.from_float(float(value))) for value in state.nominal),
        Fraction(0),
    )


def _observable_binding(jet: KillingObservableJet) -> str:
    return _digest_fields(
        b"science-free-tiny-killing-observable-v1\x00",
        jet.schema,
        jet.order,
        jet.centre_exact.numerator,
        jet.centre_exact.denominator,
        jet.radius_exact_upper.numerator,
        jet.radius_exact_upper.denominator,
        jet.lower.numerator,
        jet.lower.denominator,
        jet.upper.numerator,
        jet.upper.denominator,
        jet.nominal_l1_exact.numerator,
        jet.nominal_l1_exact.denominator,
        jet.state_radius_exact_upper.numerator,
        jet.state_radius_exact_upper.denominator,
        jet.maximum_killing_upper.numerator,
        jet.maximum_killing_upper.denominator,
        jet.maximum_killing_uncertainty.numerator,
        jet.maximum_killing_uncertainty.denominator,
        jet.formula,
    )


def _make_observable(
    kernel: packed.PackedTensorKernel,
    state: TinyQJetState,
) -> KillingObservableJet:
    witnesses = _witnesses(kernel)
    nominal_l1 = _nominal_l1_exact(state)
    centre = sum(
        (
            Fraction.from_float(float(killing)) * Fraction.from_float(float(value))
            for killing, value in zip(kernel.killing_center, state.nominal, strict=True)
        ),
        Fraction(0),
    )
    k_upper = witnesses["maximum_killing_upper"]
    delta_k = witnesses["maximum_killing_uncertainty"]
    radius = k_upper * state.l1_radius_exact_upper + delta_k * nominal_l1
    provisional = KillingObservableJet(
        schema=OBSERVABLE_SCHEMA,
        order=state.order,
        centre_exact=centre,
        radius_exact_upper=radius,
        lower=centre - radius,
        upper=centre + radius,
        nominal_l1_exact=nominal_l1,
        state_radius_exact_upper=state.l1_radius_exact_upper,
        maximum_killing_upper=k_upper,
        maximum_killing_uncertainty=delta_k,
        formula=OBSERVABLE_FORMULA,
        binding_sha256="0" * 64,
    )
    return replace(provisional, binding_sha256=_observable_binding(provisional))


def _magnitude_binding(bound: KillingMagnitudeBound) -> str:
    return _digest_fields(
        b"science-free-tiny-killing-magnitude-v1\x00",
        bound.schema,
        bound.order,
        bound.upper.numerator,
        bound.upper.denominator,
        bound.nominal_l1_exact.numerator,
        bound.nominal_l1_exact.denominator,
        bound.state_radius_exact_upper.numerator,
        bound.state_radius_exact_upper.denominator,
        bound.maximum_killing_upper.numerator,
        bound.maximum_killing_upper.denominator,
        bound.formula,
    )


def _make_magnitude(
    kernel: packed.PackedTensorKernel,
    state: TinyQJetState,
) -> KillingMagnitudeBound:
    k_upper = _witnesses(kernel)["maximum_killing_upper"]
    nominal_l1 = _nominal_l1_exact(state)
    provisional = KillingMagnitudeBound(
        schema=MAGNITUDE_SCHEMA,
        order=state.order,
        upper=k_upper * (nominal_l1 + state.l1_radius_exact_upper),
        nominal_l1_exact=nominal_l1,
        state_radius_exact_upper=state.l1_radius_exact_upper,
        maximum_killing_upper=k_upper,
        formula=MAGNITUDE_FORMULA,
        binding_sha256="0" * 64,
    )
    return replace(provisional, binding_sha256=_magnitude_binding(provisional))


def _result_binding(result: TinyQJetsResult) -> str:
    fields: list[object] = [
        result.schema,
        *result.logical_shape,
        result.target_binding_sha256,
        result.kernel_replay_sha256,
        result.rate_action_contract_sha256,
    ]
    fields.extend(state.state_binding_sha256 for state in result.states)
    fields.extend(jet.binding_sha256 for jet in result.observable_jets)
    fields.extend(bound.binding_sha256 for bound in result.magnitude_bounds)
    for binding in result.dependency_bindings:
        fields.extend(
            (
                binding.name,
                binding.accepted_sha256,
                binding.observed_sha256,
                binding.exact_bytes_matched,
            )
        )
    fields.extend(
        (
            result.status,
            result.tiny_q_jets_complete,
            result.full_window_topology_complete,
            result.physical_initial_source_bound,
            result.clean_independent_implementation,
            result.endpoint_oracle_is_external_test_only,
            result.production_resource_gate,
            result.non_authoritative,
            result.science_free,
            result.fresh_process,
            result.science_executed,
            result.f0_pass,
        )
    )
    return _digest_fields(b"science-free-tiny-q-jets-result-v1\x00", *fields)


def compute_tiny_q_jets(
    kernel: packed.PackedTensorKernel,
    target: target_uniformization.CertifiedTargetBall,
    contract: rate_action.RateActionContract,
) -> TinyQJetsResult:
    """Build z_0,...,z_4 and the tiny killing-observable enclosures."""

    dependencies = _verify_dependency_bytes()
    target_uniformization.validate_target_ball_structure_only(target)
    packed.validate_packed_tensor_kernel(kernel)
    rate_action.validate_rate_action_contract(contract)
    kernel_replay = packed._kernel_replay_digest(kernel)
    contract_digest = rate_action.rate_action_contract_sha256(contract)
    if (
        target.operator_binding_established is not True
        or kernel.states < 1
        or kernel.states > MAX_TINY_STATES
        or target.logical_shape != kernel.contract.tensor_shape
        or target.logical_shape != contract.tensor_shape
        or target.kernel_replay_sha256 != kernel_replay
        or target.rate_action_contract_sha256 != contract_digest
    ):
        raise TinyQJetFailure("target does not bind this fixed kernel and contract")

    states = [
        _make_state(
            order=0,
            nominal=target.nominal,
            radius=target.l1_radius_exact_upper,
            radius_float=target.l1_radius_upper,
            predecessor_binding_sha256=target.binding_sha256,
            action_input_binding_sha256="0" * 64,
            action_output_consistency_sha256="0" * 64,
        )
    ]
    for order in range(1, 5):
        previous = states[-1]
        vector = packed.CanonicalFloat64Vector(
            logical_shape=target.logical_shape,
            values=previous.nominal,
            raw_sha256=previous.nominal_raw_sha256,
            nonnegative=order == 1,
            source_sha256=_digest_fields(
                b"science-free-tiny-q-jet-vector-v1\x00",
                target.binding_sha256,
                previous.state_binding_sha256,
                order,
            ),
        )
        method_input = rate_action.make_internal_point_ball_input(
            vector,
            input_l1_radius_upper=previous.l1_radius_upper,
            radius_provenance_sha256=_digest_fields(
                b"science-free-tiny-q-jet-radius-v1\x00",
                target.binding_sha256,
                previous.state_binding_sha256,
                order,
            ),
        )
        action = rate_action._rate_defined_q_transpose(kernel, method_input, contract)
        rate_action.validate_internal_rate_action_state(action)
        if (
            action.operator != "Q"
            or action.derivation.kernel_replay_sha256 != kernel_replay
            or action.contract_sha256 != contract_digest
        ):
            raise TinyQJetFailure("signed Q action changed the fixed operator binding")
        exact_radius = Fraction.from_float(action.l1_radius_upper)
        states.append(
            _make_state(
                order=order,
                nominal=action.nominal,
                radius=exact_radius,
                radius_float=action.l1_radius_upper,
                predecessor_binding_sha256=previous.state_binding_sha256,
                action_input_binding_sha256=method_input.input_binding_sha256,
                action_output_consistency_sha256=action.consistency_sha256,
            )
        )

    state_tuple = tuple(states)
    observable_jets = tuple(_make_observable(kernel, state) for state in state_tuple[:4])
    magnitude_bounds = tuple(_make_magnitude(kernel, state_tuple[order]) for order in (2, 3, 4))
    provisional = TinyQJetsResult(
        schema=RESULT_SCHEMA,
        logical_shape=target.logical_shape,
        target_binding_sha256=target.binding_sha256,
        kernel_replay_sha256=kernel_replay,
        rate_action_contract_sha256=contract_digest,
        states=state_tuple,
        observable_jets=observable_jets,
        magnitude_bounds=magnitude_bounds,
        dependency_bindings=dependencies,
        result_binding_sha256="0" * 64,
        status=METHOD_STATUS,
        tiny_q_jets_complete=True,
        full_window_topology_complete=False,
        physical_initial_source_bound=False,
        clean_independent_implementation=False,
        endpoint_oracle_is_external_test_only=True,
        production_resource_gate=False,
        non_authoritative=True,
        science_free=True,
        fresh_process=False,
        science_executed=False,
        f0_pass=False,
    )
    result = replace(provisional, result_binding_sha256=_result_binding(provisional))
    validate_tiny_q_jets_structure_only(result, kernel=kernel, target=target, contract=contract)
    if _verify_dependency_bytes() != dependencies:
        raise TinyQJetFailure("accepted dependency bytes changed during tiny-jet construction")
    return result


def validate_tiny_q_jets_structure_only(
    result: TinyQJetsResult,
    *,
    kernel: packed.PackedTensorKernel,
    target: target_uniformization.CertifiedTargetBall,
    contract: rate_action.RateActionContract,
) -> None:
    """Validate in-memory relations; this is not an independent authority."""

    if type(result) is not TinyQJetsResult:
        raise TinyQJetFailure("tiny-jet result has the wrong exact type")
    target_uniformization.validate_target_ball_structure_only(target)
    packed.validate_packed_tensor_kernel(kernel)
    rate_action.validate_rate_action_contract(contract)
    kernel_replay = packed._kernel_replay_digest(kernel)
    contract_digest = rate_action.rate_action_contract_sha256(contract)
    if (
        result.schema != RESULT_SCHEMA
        or kernel.states < 1
        or kernel.states > MAX_TINY_STATES
        or result.logical_shape != target.logical_shape
        or result.target_binding_sha256 != target.binding_sha256
        or result.kernel_replay_sha256 != kernel_replay
        or result.rate_action_contract_sha256 != contract_digest
        or type(result.states) is not tuple
        or len(result.states) != 5
        or type(result.observable_jets) is not tuple
        or len(result.observable_jets) != 4
        or type(result.magnitude_bounds) is not tuple
        or len(result.magnitude_bounds) != 3
        or result.dependency_bindings != _verify_dependency_bytes()
        or not _is_sha256(result.result_binding_sha256)
        or result.result_binding_sha256 != _result_binding(result)
        or result.status != METHOD_STATUS
        or result.tiny_q_jets_complete is not True
        or result.full_window_topology_complete is not False
        or result.physical_initial_source_bound is not False
        or result.clean_independent_implementation is not False
        or result.endpoint_oracle_is_external_test_only is not True
        or result.production_resource_gate is not False
        or result.non_authoritative is not True
        or result.science_free is not True
        or result.fresh_process is not False
        or result.science_executed is not False
        or result.f0_pass is not False
    ):
        raise TinyQJetFailure("tiny-jet result ledger is invalid")

    for order, state in enumerate(result.states):
        if type(state) is not TinyQJetState:
            raise TinyQJetFailure("tiny-jet state has the wrong exact type")
        nominal = _canonical_nominal(state.nominal, states=kernel.states)
        if (
            state.schema != JET_STATE_SCHEMA
            or state.order != order
            or state.nominal_raw_sha256 != _raw_sha256(nominal)
            or type(state.l1_radius_exact_upper) is not Fraction
            or state.l1_radius_exact_upper < 0
            or state.l1_radius_upper != _float_upper(state.l1_radius_exact_upper)
            or state.l1_radius_upper_hex != state.l1_radius_upper.hex()
            or state.nominal_nonnegative_proved is not (order == 0)
            or state.signed_nominal_allowed is not (order > 0)
            or not all(
                _is_sha256(value)
                for value in (
                    state.predecessor_binding_sha256,
                    state.action_input_binding_sha256,
                    state.action_output_consistency_sha256,
                    state.state_binding_sha256,
                )
            )
            or state.state_binding_sha256 != _state_binding(state)
        ):
            raise TinyQJetFailure("tiny-jet state ledger is invalid")
        if order == 0:
            if (
                state.nominal is not target.nominal
                or state.l1_radius_exact_upper != target.l1_radius_exact_upper
                or state.predecessor_binding_sha256 != target.binding_sha256
                or state.action_input_binding_sha256 != "0" * 64
                or state.action_output_consistency_sha256 != "0" * 64
                or bool(np.any(state.nominal < 0.0))
            ):
                raise TinyQJetFailure("zeroth tiny-jet state changed the target")
        elif (
            state.predecessor_binding_sha256 != result.states[order - 1].state_binding_sha256
            or state.action_input_binding_sha256 == "0" * 64
            or state.action_output_consistency_sha256 == "0" * 64
        ):
            raise TinyQJetFailure("tiny-jet action chain is broken")

    expected_observables = tuple(_make_observable(kernel, state) for state in result.states[:4])
    expected_magnitudes = tuple(
        _make_magnitude(kernel, result.states[order]) for order in (2, 3, 4)
    )
    if (
        result.observable_jets != expected_observables
        or result.magnitude_bounds != expected_magnitudes
    ):
        raise TinyQJetFailure("tiny-jet scalar reductions changed")
