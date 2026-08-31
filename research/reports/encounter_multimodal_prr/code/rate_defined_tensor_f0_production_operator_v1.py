"""Production-operator method candidates built on the canonical packed core.

There are deliberately two different input boundaries.

``build_caller_supplied_production_operator`` accepts arbitrary endpoint
tuples.  Those inputs are always classified ``CALLER_SUPPLIED_UNCLASSIFIED``:
neither a role string nor numerical values can prove that a caller did not
derive them from a physical control or a scientific budget.

``build_fixed_neutral_synthetic_operator`` is closed over its numerical
content.  It accepts only a tensor shape and resource caps, and internally
constructs exact neutral rates, unit stationary masses, and fixed synthetic
killing.  Only closed internal paths record control/budget exclusion by
construction and a constructive global detailed-balance witness.

``build_fixed_heterogeneous_two_state_operator`` is another closed path with
no numerical or semantic inputs.  It provides a fixed reversible two-state
operator with heterogeneous killing for later integrated one-root method
tests.  Suitability is a fixture design property, not a topology PASS.

All paths remain F0 method candidates only.  They derive the diagonal, check
killed-row and sub-Markov identities, and bind their owned bytes, but they
never propagate a state, execute science, authorize F1, or self-declare F0.
The repeated-killing helper avoids an O(N) Python tuple but still materializes
the canonical O(N) packed bytes.  Nothing here is measured runtime/RSS evidence
or a largest-shape resource gate.

The packed core's legacy schema requires role strings beginning
``science_free_`` and a true ``KernelBuildContract.science_free`` field.
Those compatibility labels are explicitly non-evidentiary here; only the
closed constructor can establish input provenance.
"""

from __future__ import annotations

import dataclasses
import hashlib
import hmac
import json
import math
import re
import struct
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Final

import numpy as np
import rate_defined_tensor_f0_packed as packed

_SOURCE_MODULE_PATH_AT_IMPORT: Final = Path(__file__).resolve(strict=True)
_PACKED_CORE_PATH_AT_IMPORT: Final = Path(packed.__file__).resolve(strict=True)
_SOURCE_MODULE_SHA256_AT_IMPORT: Final = hashlib.sha256(
    _SOURCE_MODULE_PATH_AT_IMPORT.read_bytes()
).hexdigest()
_PACKED_CORE_SHA256_AT_IMPORT: Final = hashlib.sha256(
    _PACKED_CORE_PATH_AT_IMPORT.read_bytes()
).hexdigest()


class ProductionOperatorFailure(RuntimeError):
    """Fail-closed structural outcome with a stable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


HOLD_SCHEMA: Final = "HOLD_F0_PRODUCTION_OPERATOR_SCHEMA"
HOLD_SCIENCE_BOUNDARY: Final = "HOLD_F0_PRODUCTION_OPERATOR_SCIENCE_BOUNDARY"
HOLD_DETAILED_BALANCE: Final = "HOLD_F0_PRODUCTION_OPERATOR_DETAILED_BALANCE"
HOLD_STRUCTURAL_WITNESS: Final = "HOLD_F0_PRODUCTION_OPERATOR_STRUCTURAL_WITNESS"
HOLD_SOURCE_BINDING: Final = "HOLD_F0_PRODUCTION_OPERATOR_SOURCE_BINDING"

OPERATOR_SCHEMA: Final = "rate_defined_tensor_f0_production_operator_v1"
OPAQUE_ANALYSIS_SCHEMA: Final = (
    "rate_defined_tensor_f0_opaque_caller_operator_analysis_v1"
)
RECEIPT_SCHEMA: Final = "rate_defined_tensor_f0_production_operator_receipt_v1"
CALLER_SUPPLIED_METHOD_STATUS: Final = (
    "PASS_CALLER_SUPPLIED_UNCLASSIFIED_OPERATOR_METHOD_CANDIDATE_ONLY_NOT_F0"
)
FIXED_NEUTRAL_METHOD_STATUS: Final = (
    "PASS_FIXED_NEUTRAL_SYNTHETIC_OPERATOR_METHOD_CANDIDATE_ONLY_NOT_F0"
)
FIXED_HETEROGENEOUS_METHOD_STATUS: Final = (
    "PASS_FIXED_HETEROGENEOUS_TWO_STATE_METHOD_CANDIDATE_ONLY_NOT_F0"
)
METHOD_STATUS: Final = CALLER_SUPPLIED_METHOD_STATUS
METHOD_STAGE: Final = "F0_METHOD_CANDIDATE"
CALLER_SUPPLIED_UNCLASSIFIED: Final = "CALLER_SUPPLIED_UNCLASSIFIED"
INTERNAL_FIXED_NEUTRAL_SYNTHETIC_V1: Final = (
    "INTERNAL_FIXED_NEUTRAL_SYNTHETIC_V1"
)
INTERNAL_FIXED_HETEROGENEOUS_TWO_STATE_V1: Final = (
    "INTERNAL_FIXED_HETEROGENEOUS_TWO_STATE_V1"
)
FIXED_NEUTRAL_FIXTURE_ROLE: Final = "fixed_neutral_synthetic_v1"
FIXED_HETEROGENEOUS_FIXTURE_ROLE: Final = (
    "fixed_heterogeneous_two_state_one_root_design_v1"
)
SOURCE_HASH_OBSERVATION_SCOPE: Final = (
    "SAME_PROCESS_SELF_OBSERVED_NON_AUTHORITATIVE"
)
MAXIMUM_DIMENSIONS: Final = 3
DEFAULT_BLOCK_SIZE: Final = 64
DEFAULT_MAXIMUM_WORKING_BYTES: Final = 2_000_000
_FIXED_NEUTRAL_RATE: Final = Fraction(1, 16)
_FIXED_NEUTRAL_MASS: Final = Fraction(1)
_FIXED_NEUTRAL_KILLING: Final = Fraction(1, 64)

_SAFE_NAME = re.compile(r"[a-z][a-z0-9_]*\Z")


@dataclass(frozen=True, slots=True)
class CallerSuppliedAxisSpec:
    """One unclassified caller-supplied axis and mass enclosure."""

    name: str
    periodic: bool
    forward: tuple[tuple[float, float], ...]
    backward: tuple[tuple[float, float], ...]
    stationary_mass: tuple[tuple[float, float], ...]

    @property
    def size(self) -> int:
        return len(self.forward)


@dataclass(frozen=True, slots=True)
class RepeatedCallerSuppliedInterval:
    """Repeated interval descriptor; packing still materializes O(N) bytes."""

    lower: float
    upper: float


@dataclass(frozen=True, slots=True)
class CallerSuppliedOperatorSpec:
    """Unclassified endpoint specification; a diagonal is intentionally absent."""

    fixture_role: str
    tensor_shape: tuple[int, ...]
    axes: tuple[CallerSuppliedAxisSpec, ...]
    killing: tuple[tuple[float, float], ...] | RepeatedCallerSuppliedInterval
    block_size: int = DEFAULT_BLOCK_SIZE
    maximum_working_bytes: int = DEFAULT_MAXIMUM_WORKING_BYTES
    uniformization_rate: Fraction | None = None


@dataclass(frozen=True, slots=True)
class OperatorStructuralReceipt:
    """Hash-bound structural witnesses for one canonical packed kernel."""

    schema: str
    status: str
    stage: str
    input_provenance: str
    fixture_role: str
    tensor_shape: tuple[int, ...]
    state_count: int
    source_module_sha256: str
    packed_core_source_sha256: str
    source_hash_observation_scope: str
    source_hashes_authoritative: bool
    external_exact_byte_audit_required: bool
    external_exact_byte_audit_complete: bool
    input_manifest_sha256: str
    stationary_binding_sha256: str
    kernel_binding_sha256: str
    pairwise_balance_overlap_chain_sha256: str
    global_detailed_balance_witness_sha256: str
    killing_binding_sha256: str
    axis_template_edge_count: int
    possible_positive_killing_state_count: int
    guaranteed_positive_killing_state_count: int
    minimum_killing_lower: Fraction
    maximum_killing_upper: Fraction
    maximum_q_row_rounding_deficit: Fraction
    minimum_p_row_deficit: Fraction
    maximum_p_row_deficit: Fraction
    exact_type_and_owned_bytes: bool
    diagonal_derived_not_supplied: bool
    q_killed_row_identity_enclosed: bool
    p_submarkov: bool
    pairwise_balance_interval_overlap: bool
    global_detailed_balance_witness: bool
    killing_nonnegative: bool
    packed_science_free_labels_are_backend_schema_only: bool
    caller_supplied_unclassified_inputs: bool
    science_free_input_provenance: bool
    primary_control_excluded_by_construction: bool
    budget_excluded_by_construction: bool
    integrated_one_root_fixture_design: bool
    topology_executed: bool
    authorizes_scientific_execution: bool
    science_executed: bool
    measured_resource_evidence: bool
    production_resource_gate: bool
    f0_pass: bool
    receipt_sha256: str


@dataclass(frozen=True, slots=True)
class ProductionOperatorCandidate:
    """Closed internal fixture candidate; never a scientific or F0 PASS object."""

    schema: str
    input_provenance: str
    kernel: packed.PackedTensorKernel
    stationary_masses: tuple[packed.CanonicalPackedIntervals, ...]
    receipt: OperatorStructuralReceipt
    science_executed: bool
    production_resource_gate: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class OpaqueCallerOperatorAnalysis:
    """Digest-only caller analysis that intentionally exposes no packed kernel."""

    schema: str
    receipt: OperatorStructuralReceipt
    packed_kernel_exposed: bool
    science_executed: bool
    production_resource_gate: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class _StructuralAnalysis:
    pairwise_balance_overlap_chain_sha256: str
    global_detailed_balance_witness_sha256: str
    killing_binding_sha256: str
    axis_template_edge_count: int
    possible_positive_killing_state_count: int
    guaranteed_positive_killing_state_count: int
    minimum_killing_lower: Fraction
    maximum_killing_upper: Fraction
    maximum_q_row_rounding_deficit: Fraction
    minimum_p_row_deficit: Fraction
    maximum_p_row_deficit: Fraction


def _sha256(payload: bytes | memoryview) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _canonical_json_sha256(payload: object) -> str:
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


def _validate_frozen_source_bindings() -> None:
    """Reject path rebinding or byte drift after this module was imported."""

    try:
        live_source_path = Path(__file__).resolve(strict=True)
        live_packed_path = Path(packed.__file__).resolve(strict=True)
    except (OSError, TypeError) as error:
        raise ProductionOperatorFailure(
            HOLD_SOURCE_BINDING,
            "an implementation source path is unavailable",
        ) from error
    if (
        live_source_path != _SOURCE_MODULE_PATH_AT_IMPORT
        or live_packed_path != _PACKED_CORE_PATH_AT_IMPORT
        or _sha256(_SOURCE_MODULE_PATH_AT_IMPORT.read_bytes())
        != _SOURCE_MODULE_SHA256_AT_IMPORT
        or _sha256(_PACKED_CORE_PATH_AT_IMPORT.read_bytes())
        != _PACKED_CORE_SHA256_AT_IMPORT
    ):
        raise ProductionOperatorFailure(
            HOLD_SOURCE_BINDING,
            "an implementation source path or digest changed after import",
        )


def _require_safe_metadata(value: object, *, label: str) -> str:
    if type(value) is not str or not _SAFE_NAME.fullmatch(value):
        raise ProductionOperatorFailure(HOLD_SCHEMA, f"{label} is not a canonical name")
    return value


def _is_internal_fixed_provenance(value: object) -> bool:
    return value in (
        "INTERNAL_FIXED_NEUTRAL_SYNTHETIC_V1",
        "INTERNAL_FIXED_HETEROGENEOUS_TWO_STATE_V1",
    )


def _validate_endpoint_tuple(
    endpoints: object,
    *,
    expected_size: int,
    label: str,
    strictly_positive_lower: bool,
) -> tuple[tuple[float, float], ...]:
    if type(endpoints) is not tuple or len(endpoints) != expected_size:
        raise ProductionOperatorFailure(HOLD_SCHEMA, f"{label} has the wrong exact shape")
    for pair in endpoints:
        if (
            type(pair) is not tuple
            or len(pair) != 2
            or type(pair[0]) is not float
            or type(pair[1]) is not float
        ):
            raise ProductionOperatorFailure(
                HOLD_SCHEMA,
                f"{label} endpoint pairs must contain exact built-in floats",
            )
        lower, upper = pair
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or lower > upper
            or lower < 0.0
            or (lower == 0.0 and math.copysign(1.0, lower) < 0.0)
            or (upper == 0.0 and math.copysign(1.0, upper) < 0.0)
            or (strictly_positive_lower and lower <= 0.0)
        ):
            raise ProductionOperatorFailure(HOLD_SCHEMA, f"{label} endpoint is invalid")
    return endpoints


def validate_caller_supplied_operator_spec(spec: CallerSuppliedOperatorSpec) -> None:
    """Validate exact types without classifying caller-supplied provenance."""

    if type(spec) is not CallerSuppliedOperatorSpec:
        raise ProductionOperatorFailure(HOLD_SCHEMA, "operator spec has the wrong exact type")
    _require_safe_metadata(spec.fixture_role, label="fixture role")
    if (
        type(spec.tensor_shape) is not tuple
        or not spec.tensor_shape
        or len(spec.tensor_shape) > MAXIMUM_DIMENSIONS
        or any(type(size) is not int or size < 2 for size in spec.tensor_shape)
        or type(spec.axes) is not tuple
        or len(spec.axes) != len(spec.tensor_shape)
        or any(type(axis) is not CallerSuppliedAxisSpec for axis in spec.axes)
        or type(spec.block_size) is not int
        or spec.block_size < 1
        or type(spec.maximum_working_bytes) is not int
        or spec.maximum_working_bytes < 1
        or (
            spec.uniformization_rate is not None
            and type(spec.uniformization_rate) is not Fraction
        )
    ):
        raise ProductionOperatorFailure(HOLD_SCHEMA, "operator spec header is invalid")
    if len({axis.name for axis in spec.axes}) != len(spec.axes):
        raise ProductionOperatorFailure(HOLD_SCHEMA, "axis names are not unique")
    for size, axis in zip(spec.tensor_shape, spec.axes, strict=True):
        _require_safe_metadata(axis.name, label="axis name")
        if type(axis.periodic) is not bool or axis.size != size:
            raise ProductionOperatorFailure(HOLD_SCHEMA, "axis header disagrees with shape")
        _validate_endpoint_tuple(
            axis.forward,
            expected_size=size,
            label=f"{axis.name} forward rates",
            strictly_positive_lower=False,
        )
        _validate_endpoint_tuple(
            axis.backward,
            expected_size=size,
            label=f"{axis.name} backward rates",
            strictly_positive_lower=False,
        )
        _validate_endpoint_tuple(
            axis.stationary_mass,
            expected_size=size,
            label=f"{axis.name} stationary masses",
            strictly_positive_lower=True,
        )
        if not axis.periodic and (
            axis.forward[-1] != (0.0, 0.0) or axis.backward[0] != (0.0, 0.0)
        ):
            raise ProductionOperatorFailure(
                HOLD_SCHEMA,
                "reflecting axis contains a boundary transition",
            )
    if type(spec.killing) is tuple:
        _validate_endpoint_tuple(
            spec.killing,
            expected_size=math.prod(spec.tensor_shape),
            label="killing",
            strictly_positive_lower=False,
        )
    elif type(spec.killing) is RepeatedCallerSuppliedInterval:
        _validate_endpoint_tuple(
            ((spec.killing.lower, spec.killing.upper),),
            expected_size=1,
            label="repeated killing",
            strictly_positive_lower=False,
        )
    else:
        raise ProductionOperatorFailure(
            HOLD_SCHEMA,
            "killing must be an exact endpoint tuple or repeated interval",
        )


def _create_repeated_payload(
    interval: RepeatedCallerSuppliedInterval,
    *,
    role: str,
    logical_shape: tuple[int, ...],
    block_size: int,
    maximum_working_bytes: int,
) -> packed.PackedIntervalPayload:
    """Create one immutable repeated source without materializing Python pairs."""

    if type(interval) is not RepeatedCallerSuppliedInterval:
        raise ProductionOperatorFailure(HOLD_SCHEMA, "repeated interval has wrong type")
    states = math.prod(logical_shape)
    pattern = struct.pack("=dd", interval.lower, interval.upper)
    raw_bytes = pattern * states
    manifest = packed.PackedIntervalManifest(
        schema=packed.PACKED_INTERVAL_SCHEMA,
        role=role,
        logical_shape=logical_shape,
        array_shape=(states, 2),
        state_count=states,
        raw_byte_length=len(raw_bytes),
        raw_sha256=_sha256(raw_bytes),
        endpoint_order=packed.ENDPOINT_ORDER,
        nonnegative=True,
        block_size=block_size,
        maximum_working_bytes=maximum_working_bytes,
    )
    payload = packed.PackedIntervalPayload(manifest=manifest, raw_bytes=raw_bytes)
    packed.validate_packed_interval_payload(payload)
    return payload


def _manifest_payload(manifest: packed.PackedIntervalManifest) -> dict[str, object]:
    packed.validate_packed_interval_manifest(manifest)
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


def _contract_payload(contract: packed.KernelBuildContract) -> dict[str, object]:
    packed.validate_kernel_build_contract(contract)
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


def _input_manifest_payload(
    kernel: packed.PackedTensorKernel,
    stationary_masses: tuple[packed.CanonicalPackedIntervals, ...],
    *,
    input_provenance: str,
    fixture_role: str,
) -> dict[str, object]:
    return {
        "axes": [
            {
                "backward": _manifest_payload(axis.backward.manifest),
                "forward": _manifest_payload(axis.forward.manifest),
                "name": axis.name,
                "periodic": axis.periodic,
                "size": axis.size,
                "stationary_mass": _manifest_payload(mass.manifest),
            }
            for axis, mass in zip(kernel.axes, stationary_masses, strict=True)
        ],
        "contract": _contract_payload(kernel.contract),
        "fixture_role": fixture_role,
        "input_provenance": input_provenance,
        "killing": _manifest_payload(kernel.killing.manifest),
    }


def _stationary_binding_sha256(
    stationary_masses: tuple[packed.CanonicalPackedIntervals, ...],
) -> str:
    return _canonical_json_sha256(
        [_manifest_payload(source.manifest) for source in stationary_masses]
    )


def _kernel_binding_sha256(kernel: packed.PackedTensorKernel) -> str:
    packed.validate_packed_tensor_kernel(kernel)
    return _canonical_json_sha256(
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
            "contract": _contract_payload(kernel.contract),
            "ledger": {
                "combined_chain_sha256": kernel.ledger.combined_chain_sha256,
                "derived_chain_sha256": kernel.ledger.derived_chain_sha256,
                "source_chain_sha256": kernel.ledger.source_chain_sha256,
                "witness_binding_sha256": kernel.ledger.witness_binding_sha256,
                "witnesses": [
                    {
                        "flat_index": witness.flat_index,
                        "name": witness.name,
                        "value": _fraction_text(witness.value),
                    }
                    for witness in kernel.ledger.witnesses
                ],
            },
            "rate": kernel.rate.hex(),
            "rate_fraction": _fraction_text(kernel.rate_fraction),
            "schema": kernel.schema,
        }
    )


def _product_interval(
    left: np.ndarray,
    left_index: int,
    right: np.ndarray,
    right_index: int,
) -> tuple[Fraction, Fraction]:
    return (
        Fraction.from_float(float(left[left_index, 0]))
        * Fraction.from_float(float(right[right_index, 0])),
        Fraction.from_float(float(left[left_index, 1]))
        * Fraction.from_float(float(right[right_index, 1])),
    )


def _coordinate(flat: int, shape: tuple[int, ...], dimension: int) -> int:
    stride = math.prod(shape[dimension + 1 :])
    return (flat // stride) % shape[dimension]


def _analyse_structure(
    kernel: packed.PackedTensorKernel,
    stationary_masses: tuple[packed.CanonicalPackedIntervals, ...],
    *,
    input_provenance: str,
) -> _StructuralAnalysis:
    packed.validate_packed_tensor_kernel(kernel)
    if (
        type(stationary_masses) is not tuple
        or len(stationary_masses) != len(kernel.axes)
        or any(type(source) is not packed.CanonicalPackedIntervals for source in stationary_masses)
    ):
        raise ProductionOperatorFailure(HOLD_SCHEMA, "stationary source nesting is invalid")
    for axis, source in zip(kernel.axes, stationary_masses, strict=True):
        packed.validate_canonical_packed_intervals(source)
        if (
            source.manifest.role != f"science_free_stationary_mass_{axis.name}"
            or source.manifest.logical_shape != (axis.size,)
            or not source.manifest.nonnegative
            or bool(np.any(source.intervals[:, 0] <= 0.0))
        ):
            raise ProductionOperatorFailure(HOLD_SCHEMA, "stationary source is inconsistent")

    edge_rows: list[dict[str, object]] = []
    constructive_rows: list[dict[str, object]] = []
    for dimension, (axis, mass) in enumerate(
        zip(kernel.axes, stationary_masses, strict=True)
    ):
        edge_indices = range(axis.size) if axis.periodic else range(axis.size - 1)
        for left in edge_indices:
            right = (left + 1) % axis.size
            lhs = _product_interval(
                mass.intervals,
                left,
                axis.forward.intervals,
                left,
            )
            rhs = _product_interval(
                mass.intervals,
                right,
                axis.backward.intervals,
                right,
            )
            overlap_lower = max(lhs[0], rhs[0])
            overlap_upper = min(lhs[1], rhs[1])
            if overlap_lower > overlap_upper:
                raise ProductionOperatorFailure(
                    HOLD_DETAILED_BALANCE,
                    f"detailed-balance intervals are disjoint on axis {dimension}, edge {left}",
                )
            edge_rows.append(
                {
                    "dimension": dimension,
                    "left": left,
                    "overlap_lower": _fraction_text(overlap_lower),
                    "overlap_upper": _fraction_text(overlap_upper),
                    "right": right,
                }
            )
            if _is_internal_fixed_provenance(input_provenance):
                mass_left_lower = Fraction.from_float(
                    float(mass.intervals[left, 0])
                )
                mass_left_upper = Fraction.from_float(
                    float(mass.intervals[left, 1])
                )
                mass_right_lower = Fraction.from_float(
                    float(mass.intervals[right, 0])
                )
                mass_right_upper = Fraction.from_float(
                    float(mass.intervals[right, 1])
                )
                forward_lower = Fraction.from_float(
                    float(axis.forward.intervals[left, 0])
                )
                forward_upper = Fraction.from_float(
                    float(axis.forward.intervals[left, 1])
                )
                backward_lower = Fraction.from_float(
                    float(axis.backward.intervals[right, 0])
                )
                backward_upper = Fraction.from_float(
                    float(axis.backward.intervals[right, 1])
                )
                exact_values = (
                    mass_left_lower,
                    mass_left_upper,
                    mass_right_lower,
                    mass_right_upper,
                    forward_lower,
                    forward_upper,
                    backward_lower,
                    backward_upper,
                )
                if (
                    mass_left_lower != mass_left_upper
                    or mass_right_lower != mass_right_upper
                    or forward_lower != forward_upper
                    or backward_lower != backward_upper
                    or lhs[0] != lhs[1]
                    or rhs[0] != rhs[1]
                    or lhs[0] != rhs[0]
                ):
                    raise ProductionOperatorFailure(
                        HOLD_DETAILED_BALANCE,
                        "fixed-neutral path lacks an exact constructive balance witness",
                    )
                constructive_rows.append(
                    {
                        "backward_rate": _fraction_text(exact_values[6]),
                        "conductance": _fraction_text(lhs[0]),
                        "dimension": dimension,
                        "forward_rate": _fraction_text(exact_values[4]),
                        "left": left,
                        "left_mass": _fraction_text(exact_values[0]),
                        "right": right,
                        "right_mass": _fraction_text(exact_values[2]),
                    }
                )

    witness_by_name = {witness.name: witness.value for witness in kernel.ledger.witnesses}
    delta_q = witness_by_name["delta_q"]
    minimum_killing_lower: Fraction | None = None
    maximum_killing_upper = Fraction(0)
    possible_positive_killing_state_count = 0
    guaranteed_positive_killing_state_count = 0
    maximum_q_deficit = Fraction(0)
    minimum_p_deficit: Fraction | None = None
    maximum_p_deficit = Fraction(0)
    killing_chain = hashlib.sha256(b"science-free-killing-witness-v1\x00")

    for flat in range(kernel.states):
        kill_lower = Fraction.from_float(float(kernel.killing.intervals[flat, 0]))
        kill_upper = Fraction.from_float(float(kernel.killing.intervals[flat, 1]))
        kill_center = Fraction.from_float(float(kernel.killing_center[flat]))
        minimum_killing_lower = (
            kill_lower
            if minimum_killing_lower is None
            else min(minimum_killing_lower, kill_lower)
        )
        maximum_killing_upper = max(maximum_killing_upper, kill_upper)
        if kill_upper > 0:
            possible_positive_killing_state_count += 1
        if kill_lower > 0:
            guaranteed_positive_killing_state_count += 1
        if kill_lower < 0 or kill_center < 0:
            raise ProductionOperatorFailure(
                HOLD_STRUCTURAL_WITNESS,
                "killing lost nonnegativity",
            )

        q_off_diagonal = Fraction(0)
        p_row_sum = Fraction.from_float(float(kernel.p_self_center[flat]))
        for dimension in range(len(kernel.axes)):
            coordinate = _coordinate(flat, kernel.contract.tensor_shape, dimension)
            q_off_diagonal += Fraction.from_float(
                float(kernel.forward_center[dimension][coordinate])
            )
            q_off_diagonal += Fraction.from_float(
                float(kernel.backward_center[dimension][coordinate])
            )
            p_row_sum += Fraction.from_float(
                float(kernel.p_forward_center[dimension][coordinate])
            )
            p_row_sum += Fraction.from_float(
                float(kernel.p_backward_center[dimension][coordinate])
            )

        diagonal = Fraction.from_float(float(kernel.diagonal_center[flat]))
        q_killed_residual = diagonal + q_off_diagonal + kill_center
        if q_killed_residual > 0 or -q_killed_residual > delta_q:
            raise ProductionOperatorFailure(
                HOLD_STRUCTURAL_WITNESS,
                "derived Q row does not enclose the killed-row identity",
            )
        maximum_q_deficit = max(maximum_q_deficit, -q_killed_residual)

        p_deficit = Fraction(1) - p_row_sum
        if p_deficit < 0:
            raise ProductionOperatorFailure(
                HOLD_STRUCTURAL_WITNESS,
                "uniformized row is not substochastic",
            )
        minimum_p_deficit = (
            p_deficit if minimum_p_deficit is None else min(minimum_p_deficit, p_deficit)
        )
        maximum_p_deficit = max(maximum_p_deficit, p_deficit)
        killing_chain.update(
            (
                f"{flat}:{_fraction_text(kill_lower)}:{_fraction_text(kill_upper)}:"
                f"{_fraction_text(kill_center)}\n"
            ).encode("ascii")
        )

    if minimum_killing_lower is None or minimum_p_deficit is None:
        raise ProductionOperatorFailure(HOLD_STRUCTURAL_WITNESS, "operator has no states")
    global_witness_payload: dict[str, object]
    if _is_internal_fixed_provenance(input_provenance):
        global_witness_payload = {
            "constructive_axis_edge_witnesses": constructive_rows,
            "factorized_measure": [
                [
                    _fraction_text(
                        Fraction.from_float(float(source.intervals[index, 0]))
                    )
                    for index in range(source.manifest.state_count)
                ]
                for source in stationary_masses
            ],
            "witness": "exact_factorized_stationary_measure_and_shared_edge_conductance",
        }
    else:
        global_witness_payload = {
            "available": False,
            "reason": (
                "pairwise_interval_overlap_does_not_construct_one_shared_measure"
            ),
        }
    return _StructuralAnalysis(
        pairwise_balance_overlap_chain_sha256=_canonical_json_sha256(edge_rows),
        global_detailed_balance_witness_sha256=_canonical_json_sha256(
            global_witness_payload
        ),
        killing_binding_sha256=killing_chain.hexdigest(),
        axis_template_edge_count=len(edge_rows),
        possible_positive_killing_state_count=possible_positive_killing_state_count,
        guaranteed_positive_killing_state_count=(
            guaranteed_positive_killing_state_count
        ),
        minimum_killing_lower=minimum_killing_lower,
        maximum_killing_upper=maximum_killing_upper,
        maximum_q_row_rounding_deficit=maximum_q_deficit,
        minimum_p_row_deficit=minimum_p_deficit,
        maximum_p_row_deficit=maximum_p_deficit,
    )


def _receipt_payload(receipt: OperatorStructuralReceipt) -> dict[str, object]:
    if type(receipt) is not OperatorStructuralReceipt:
        raise ProductionOperatorFailure(HOLD_SCHEMA, "receipt has the wrong exact type")
    return {
        field.name: (
            _fraction_text(value)
            if type(value) is Fraction
            else list(value)
            if field.name == "tensor_shape"
            else value
        )
        for field in dataclasses.fields(receipt)
        if field.name != "receipt_sha256"
        for value in (getattr(receipt, field.name),)
    }


def _validate_internal_fixed_template(
    kernel: packed.PackedTensorKernel,
    stationary_masses: tuple[packed.CanonicalPackedIntervals, ...],
    *,
    input_provenance: str,
) -> None:
    """Prove owned bytes against literals independent of constructor globals."""

    if kernel.contract.uniformization_rate is not None:
        raise ProductionOperatorFailure(
            HOLD_SCIENCE_BOUNDARY,
            "an internal fixed constructor cannot accept a supplied rate",
        )
    if len(stationary_masses) != len(kernel.axes):
        raise ProductionOperatorFailure(
            HOLD_STRUCTURAL_WITNESS,
            "internal fixed stationary source count is inconsistent",
        )
    if input_provenance == "INTERNAL_FIXED_NEUTRAL_SYNTHETIC_V1":
        point_rate = float(Fraction(1, 16))
        point_mass = float(Fraction(1))
        point_killing = float(Fraction(1, 64))
        for dimension, (axis, mass) in enumerate(
            zip(kernel.axes, stationary_masses, strict=True)
        ):
            if axis.name != f"fixed_neutral_axis_{dimension}" or axis.periodic:
                raise ProductionOperatorFailure(
                    HOLD_STRUCTURAL_WITNESS,
                    "fixed-neutral axis header is inconsistent",
                )
            expected_forward = np.full((axis.size, 2), point_rate, dtype=np.float64)
            expected_backward = np.full((axis.size, 2), point_rate, dtype=np.float64)
            expected_forward[-1, :] = 0.0
            expected_backward[0, :] = 0.0
            expected_mass = np.full((axis.size, 2), point_mass, dtype=np.float64)
            if (
                not np.array_equal(axis.forward.intervals, expected_forward)
                or not np.array_equal(axis.backward.intervals, expected_backward)
                or not np.array_equal(mass.intervals, expected_mass)
            ):
                raise ProductionOperatorFailure(
                    HOLD_STRUCTURAL_WITNESS,
                    "fixed-neutral axis bytes disagree with literal template values",
                )
        if not bool(
            np.all(kernel.killing.intervals[:, 0] == point_killing)
            and np.all(kernel.killing.intervals[:, 1] == point_killing)
        ):
            raise ProductionOperatorFailure(
                HOLD_STRUCTURAL_WITNESS,
                "fixed-neutral killing bytes disagree with literal template values",
            )
        return

    if input_provenance == "INTERNAL_FIXED_HETEROGENEOUS_TWO_STATE_V1":
        if (
            kernel.contract.tensor_shape != (2,)
            or len(kernel.axes) != 1
            or len(stationary_masses) != 1
        ):
            raise ProductionOperatorFailure(
                HOLD_STRUCTURAL_WITNESS,
                "fixed heterogeneous fixture must have exactly two states",
            )
        axis = kernel.axes[0]
        mass = stationary_masses[0]
        expected_forward = np.array(
            ((0.5, 0.5), (0.0, 0.0)),
            dtype=np.float64,
        )
        expected_backward = np.array(
            ((0.0, 0.0), (0.25, 0.25)),
            dtype=np.float64,
        )
        expected_mass = np.array(
            ((1.0, 1.0), (2.0, 2.0)),
            dtype=np.float64,
        )
        expected_killing = np.array(
            ((0.125, 0.125), (0.5, 0.5)),
            dtype=np.float64,
        )
        if (
            axis.name != "fixed_heterogeneous_axis"
            or axis.periodic
            or not np.array_equal(axis.forward.intervals, expected_forward)
            or not np.array_equal(axis.backward.intervals, expected_backward)
            or not np.array_equal(mass.intervals, expected_mass)
            or not np.array_equal(kernel.killing.intervals, expected_killing)
        ):
            raise ProductionOperatorFailure(
                HOLD_STRUCTURAL_WITNESS,
                "fixed heterogeneous bytes disagree with literal template values",
            )
        return

    raise ProductionOperatorFailure(
        HOLD_SCIENCE_BOUNDARY,
        "input provenance is not an internal fixed template",
    )


def _make_receipt(
    kernel: packed.PackedTensorKernel,
    stationary_masses: tuple[packed.CanonicalPackedIntervals, ...],
    *,
    input_provenance: str,
    fixture_role: str,
) -> OperatorStructuralReceipt:
    _validate_frozen_source_bindings()
    if input_provenance not in (
        "CALLER_SUPPLIED_UNCLASSIFIED",
        "INTERNAL_FIXED_NEUTRAL_SYNTHETIC_V1",
        "INTERNAL_FIXED_HETEROGENEOUS_TWO_STATE_V1",
    ):
        raise ProductionOperatorFailure(HOLD_SCHEMA, "input provenance is invalid")
    is_internal_fixed = _is_internal_fixed_provenance(input_provenance)
    is_heterogeneous = (
        input_provenance == "INTERNAL_FIXED_HETEROGENEOUS_TWO_STATE_V1"
    )
    if is_internal_fixed:
        expected_role = (
            "fixed_heterogeneous_two_state_one_root_design_v1"
            if is_heterogeneous
            else "fixed_neutral_synthetic_v1"
        )
        if fixture_role != expected_role:
            raise ProductionOperatorFailure(
                HOLD_SCIENCE_BOUNDARY,
                "internal fixed fixture role is not the literal template value",
            )
        _validate_internal_fixed_template(
            kernel,
            stationary_masses,
            input_provenance=input_provenance,
        )
    analysis = _analyse_structure(
        kernel,
        stationary_masses,
        input_provenance=input_provenance,
    )
    receipt = OperatorStructuralReceipt(
        schema=RECEIPT_SCHEMA,
        status=(
            "PASS_FIXED_HETEROGENEOUS_TWO_STATE_METHOD_CANDIDATE_ONLY_NOT_F0"
            if is_heterogeneous
            else "PASS_FIXED_NEUTRAL_SYNTHETIC_OPERATOR_METHOD_CANDIDATE_ONLY_NOT_F0"
            if is_internal_fixed
            else "PASS_CALLER_SUPPLIED_UNCLASSIFIED_OPERATOR_METHOD_CANDIDATE_ONLY_NOT_F0"
        ),
        stage=METHOD_STAGE,
        input_provenance=input_provenance,
        fixture_role=fixture_role,
        tensor_shape=kernel.contract.tensor_shape,
        state_count=kernel.states,
        source_module_sha256=_SOURCE_MODULE_SHA256_AT_IMPORT,
        packed_core_source_sha256=_PACKED_CORE_SHA256_AT_IMPORT,
        source_hash_observation_scope=(
            "SAME_PROCESS_SELF_OBSERVED_NON_AUTHORITATIVE"
        ),
        source_hashes_authoritative=False,
        external_exact_byte_audit_required=True,
        external_exact_byte_audit_complete=False,
        input_manifest_sha256=_canonical_json_sha256(
            _input_manifest_payload(
                kernel,
                stationary_masses,
                input_provenance=input_provenance,
                fixture_role=fixture_role,
            )
        ),
        stationary_binding_sha256=_stationary_binding_sha256(stationary_masses),
        kernel_binding_sha256=_kernel_binding_sha256(kernel),
        pairwise_balance_overlap_chain_sha256=(
            analysis.pairwise_balance_overlap_chain_sha256
        ),
        global_detailed_balance_witness_sha256=(
            analysis.global_detailed_balance_witness_sha256
        ),
        killing_binding_sha256=analysis.killing_binding_sha256,
        axis_template_edge_count=analysis.axis_template_edge_count,
        possible_positive_killing_state_count=(
            analysis.possible_positive_killing_state_count
        ),
        guaranteed_positive_killing_state_count=(
            analysis.guaranteed_positive_killing_state_count
        ),
        minimum_killing_lower=analysis.minimum_killing_lower,
        maximum_killing_upper=analysis.maximum_killing_upper,
        maximum_q_row_rounding_deficit=analysis.maximum_q_row_rounding_deficit,
        minimum_p_row_deficit=analysis.minimum_p_row_deficit,
        maximum_p_row_deficit=analysis.maximum_p_row_deficit,
        exact_type_and_owned_bytes=True,
        diagonal_derived_not_supplied=True,
        q_killed_row_identity_enclosed=True,
        p_submarkov=True,
        pairwise_balance_interval_overlap=True,
        global_detailed_balance_witness=is_internal_fixed,
        killing_nonnegative=True,
        packed_science_free_labels_are_backend_schema_only=True,
        caller_supplied_unclassified_inputs=not is_internal_fixed,
        science_free_input_provenance=is_internal_fixed,
        primary_control_excluded_by_construction=is_internal_fixed,
        budget_excluded_by_construction=is_internal_fixed,
        integrated_one_root_fixture_design=is_heterogeneous,
        topology_executed=False,
        authorizes_scientific_execution=False,
        science_executed=False,
        measured_resource_evidence=False,
        production_resource_gate=False,
        f0_pass=False,
        receipt_sha256="",
    )
    return dataclasses.replace(
        receipt,
        receipt_sha256=_canonical_json_sha256(_receipt_payload(receipt)),
    )


def validate_production_operator_candidate(candidate: ProductionOperatorCandidate) -> None:
    """Recompute a closed internal fixture from its owned kernel bytes."""

    if type(candidate) is not ProductionOperatorCandidate:
        raise ProductionOperatorFailure(HOLD_SCHEMA, "candidate has the wrong exact type")
    if (
        type(candidate.schema) is not str
        or candidate.schema != OPERATOR_SCHEMA
        or type(candidate.input_provenance) is not str
        or not _is_internal_fixed_provenance(candidate.input_provenance)
        or type(candidate.kernel) is not packed.PackedTensorKernel
        or type(candidate.stationary_masses) is not tuple
        or type(candidate.receipt) is not OperatorStructuralReceipt
        or type(candidate.science_executed) is not bool
        or candidate.science_executed is not False
        or type(candidate.production_resource_gate) is not bool
        or candidate.production_resource_gate is not False
        or type(candidate.f0_pass) is not bool
        or candidate.f0_pass is not False
    ):
        raise ProductionOperatorFailure(HOLD_SCHEMA, "candidate boundary fields are invalid")
    packed.validate_packed_tensor_kernel(candidate.kernel)
    _require_safe_metadata(candidate.receipt.fixture_role, label="fixture role")
    expected = _make_receipt(
        candidate.kernel,
        candidate.stationary_masses,
        input_provenance=candidate.input_provenance,
        fixture_role=candidate.receipt.fixture_role,
    )
    if not _is_sha256(candidate.receipt.receipt_sha256):
        raise ProductionOperatorFailure(HOLD_SOURCE_BINDING, "receipt digest is invalid")
    if candidate.receipt != expected or not hmac.compare_digest(
        candidate.receipt.receipt_sha256,
        _canonical_json_sha256(_receipt_payload(candidate.receipt)),
    ):
        raise ProductionOperatorFailure(
            HOLD_SOURCE_BINDING,
            "operator receipt disagrees with owned bytes or source hashes",
        )


def validate_opaque_caller_operator_analysis(
    analysis: OpaqueCallerOperatorAnalysis,
) -> None:
    """Validate a digest-only caller analysis without recovering a kernel."""

    _validate_frozen_source_bindings()
    if type(analysis) is not OpaqueCallerOperatorAnalysis:
        raise ProductionOperatorFailure(HOLD_SCHEMA, "opaque analysis has wrong type")
    if (
        analysis.schema != OPAQUE_ANALYSIS_SCHEMA
        or type(analysis.receipt) is not OperatorStructuralReceipt
        or type(analysis.packed_kernel_exposed) is not bool
        or analysis.packed_kernel_exposed is not False
        or type(analysis.science_executed) is not bool
        or analysis.science_executed is not False
        or type(analysis.production_resource_gate) is not bool
        or analysis.production_resource_gate is not False
        or type(analysis.f0_pass) is not bool
        or analysis.f0_pass is not False
    ):
        raise ProductionOperatorFailure(HOLD_SCHEMA, "opaque boundary fields are invalid")
    receipt = analysis.receipt
    digest_fields = (
        receipt.source_module_sha256,
        receipt.packed_core_source_sha256,
        receipt.input_manifest_sha256,
        receipt.stationary_binding_sha256,
        receipt.kernel_binding_sha256,
        receipt.pairwise_balance_overlap_chain_sha256,
        receipt.global_detailed_balance_witness_sha256,
        receipt.killing_binding_sha256,
        receipt.receipt_sha256,
    )
    if (
        receipt.schema != RECEIPT_SCHEMA
        or receipt.status
        != "PASS_CALLER_SUPPLIED_UNCLASSIFIED_OPERATOR_METHOD_CANDIDATE_ONLY_NOT_F0"
        or receipt.stage != METHOD_STAGE
        or receipt.input_provenance != "CALLER_SUPPLIED_UNCLASSIFIED"
        or _require_safe_metadata(receipt.fixture_role, label="fixture role")
        != receipt.fixture_role
        or type(receipt.tensor_shape) is not tuple
        or not receipt.tensor_shape
        or receipt.state_count != math.prod(receipt.tensor_shape)
        or receipt.state_count < 1
        or receipt.source_module_sha256 != _SOURCE_MODULE_SHA256_AT_IMPORT
        or receipt.packed_core_source_sha256 != _PACKED_CORE_SHA256_AT_IMPORT
        or receipt.source_hash_observation_scope
        != "SAME_PROCESS_SELF_OBSERVED_NON_AUTHORITATIVE"
        or receipt.source_hashes_authoritative is not False
        or receipt.external_exact_byte_audit_required is not True
        or receipt.external_exact_byte_audit_complete is not False
        or any(not _is_sha256(value) for value in digest_fields)
        or type(receipt.axis_template_edge_count) is not int
        or receipt.axis_template_edge_count < 1
        or type(receipt.possible_positive_killing_state_count) is not int
        or not 0
        <= receipt.possible_positive_killing_state_count
        <= receipt.state_count
        or type(receipt.guaranteed_positive_killing_state_count) is not int
        or not 0
        <= receipt.guaranteed_positive_killing_state_count
        <= receipt.possible_positive_killing_state_count
        or receipt.exact_type_and_owned_bytes is not True
        or receipt.diagonal_derived_not_supplied is not True
        or receipt.q_killed_row_identity_enclosed is not True
        or receipt.p_submarkov is not True
        or receipt.pairwise_balance_interval_overlap is not True
        or receipt.global_detailed_balance_witness is not False
        or receipt.killing_nonnegative is not True
        or receipt.packed_science_free_labels_are_backend_schema_only is not True
        or receipt.caller_supplied_unclassified_inputs is not True
        or receipt.science_free_input_provenance is not False
        or receipt.primary_control_excluded_by_construction is not False
        or receipt.budget_excluded_by_construction is not False
        or receipt.integrated_one_root_fixture_design is not False
        or receipt.topology_executed is not False
        or receipt.authorizes_scientific_execution is not False
        or receipt.science_executed is not False
        or receipt.measured_resource_evidence is not False
        or receipt.production_resource_gate is not False
        or receipt.f0_pass is not False
        or not hmac.compare_digest(
            receipt.receipt_sha256,
            _canonical_json_sha256(_receipt_payload(receipt)),
        )
    ):
        raise ProductionOperatorFailure(
            HOLD_SOURCE_BINDING,
            "opaque caller analysis receipt is invalid or promoted",
        )


def _build_production_operator(
    spec: CallerSuppliedOperatorSpec,
    *,
    input_provenance: str,
) -> ProductionOperatorCandidate | OpaqueCallerOperatorAnalysis:
    """Internal shared byte-packing path after provenance is classified."""

    validate_caller_supplied_operator_spec(spec)
    axis_payloads: list[packed.PackedAxisPayload] = []
    stationary_masses: list[packed.CanonicalPackedIntervals] = []
    for axis in spec.axes:
        forward = packed.create_packed_interval_payload(
            axis.forward,
            role=f"science_free_axis_{axis.name}_forward",
            logical_shape=(axis.size,),
            nonnegative=True,
            block_size=spec.block_size,
            maximum_working_bytes=spec.maximum_working_bytes,
        )
        backward = packed.create_packed_interval_payload(
            axis.backward,
            role=f"science_free_axis_{axis.name}_backward",
            logical_shape=(axis.size,),
            nonnegative=True,
            block_size=spec.block_size,
            maximum_working_bytes=spec.maximum_working_bytes,
        )
        stationary_payload = packed.create_packed_interval_payload(
            axis.stationary_mass,
            role=f"science_free_stationary_mass_{axis.name}",
            logical_shape=(axis.size,),
            nonnegative=True,
            block_size=spec.block_size,
            maximum_working_bytes=spec.maximum_working_bytes,
        )
        axis_payloads.append(
            packed.PackedAxisPayload(
                name=axis.name,
                size=axis.size,
                periodic=axis.periodic,
                forward=forward,
                backward=backward,
            )
        )
        stationary_masses.append(
            packed.load_canonical_packed_intervals(stationary_payload)
        )
    killing = (
        packed.create_packed_interval_payload(
            spec.killing,
            role="science_free_killing",
            logical_shape=spec.tensor_shape,
            nonnegative=True,
            block_size=spec.block_size,
            maximum_working_bytes=spec.maximum_working_bytes,
        )
        if type(spec.killing) is tuple
        else _create_repeated_payload(
            spec.killing,
            role="science_free_killing",
            logical_shape=spec.tensor_shape,
            block_size=spec.block_size,
            maximum_working_bytes=spec.maximum_working_bytes,
        )
    )
    contract = packed.KernelBuildContract(
        tensor_shape=spec.tensor_shape,
        block_size=spec.block_size,
        maximum_working_bytes=spec.maximum_working_bytes,
        uniformization_rate=spec.uniformization_rate,
    )
    kernel = packed.build_packed_tensor_kernel(
        packed.PackedKernelInputs(axes=tuple(axis_payloads), killing=killing),
        contract,
    )
    stationary_tuple = tuple(stationary_masses)
    receipt = _make_receipt(
        kernel,
        stationary_tuple,
        input_provenance=input_provenance,
        fixture_role=spec.fixture_role,
    )
    if input_provenance == "CALLER_SUPPLIED_UNCLASSIFIED":
        opaque = OpaqueCallerOperatorAnalysis(
            schema=OPAQUE_ANALYSIS_SCHEMA,
            receipt=receipt,
            packed_kernel_exposed=False,
            science_executed=False,
            production_resource_gate=False,
            f0_pass=False,
        )
        validate_opaque_caller_operator_analysis(opaque)
        return opaque
    candidate = ProductionOperatorCandidate(
        schema=OPERATOR_SCHEMA,
        input_provenance=input_provenance,
        kernel=kernel,
        stationary_masses=stationary_tuple,
        receipt=receipt,
        science_executed=False,
        production_resource_gate=False,
        f0_pass=False,
    )
    validate_production_operator_candidate(candidate)
    return candidate


def build_caller_supplied_production_operator(
    spec: CallerSuppliedOperatorSpec,
) -> OpaqueCallerOperatorAnalysis:
    """Analyse caller endpoints, returning only an opaque digest receipt."""

    analysis = _build_production_operator(
        spec,
        input_provenance="CALLER_SUPPLIED_UNCLASSIFIED",
    )
    if type(analysis) is not OpaqueCallerOperatorAnalysis:
        raise ProductionOperatorFailure(HOLD_SCHEMA, "caller analysis leaked a kernel")
    return analysis


def build_fixed_neutral_synthetic_operator(
    tensor_shape: tuple[int, ...],
    *,
    block_size: int = DEFAULT_BLOCK_SIZE,
    maximum_working_bytes: int = DEFAULT_MAXIMUM_WORKING_BYTES,
) -> ProductionOperatorCandidate:
    """Build the one closed exact-neutral synthetic operator candidate.

    No numerical endpoint, fixture-role, file-path, physical-control, or
    scientific-budget argument exists on this public surface.
    This canonical semantic construction is not a measured resource gate.
    """

    if (
        type(tensor_shape) is not tuple
        or not tensor_shape
        or len(tensor_shape) > MAXIMUM_DIMENSIONS
        or any(type(size) is not int or size < 2 for size in tensor_shape)
        or type(block_size) is not int
        or block_size < 1
        or type(maximum_working_bytes) is not int
        or maximum_working_bytes < 1
    ):
        raise ProductionOperatorFailure(
            HOLD_SCHEMA,
            "fixed-neutral shape or resource cap is invalid",
        )
    rate = float(_FIXED_NEUTRAL_RATE)
    mass = float(_FIXED_NEUTRAL_MASS)
    killing = float(_FIXED_NEUTRAL_KILLING)
    point_rate = (rate, rate)
    point_mass = (mass, mass)
    zero = (0.0, 0.0)
    axes = tuple(
        CallerSuppliedAxisSpec(
            name=f"fixed_neutral_axis_{dimension}",
            periodic=False,
            forward=(point_rate,) * (size - 1) + (zero,),
            backward=(zero,) + (point_rate,) * (size - 1),
            stationary_mass=(point_mass,) * size,
        )
        for dimension, size in enumerate(tensor_shape)
    )
    spec = CallerSuppliedOperatorSpec(
        fixture_role=FIXED_NEUTRAL_FIXTURE_ROLE,
        tensor_shape=tensor_shape,
        axes=axes,
        killing=RepeatedCallerSuppliedInterval(killing, killing),
        block_size=block_size,
        maximum_working_bytes=maximum_working_bytes,
        uniformization_rate=None,
    )
    candidate = _build_production_operator(
        spec,
        input_provenance="INTERNAL_FIXED_NEUTRAL_SYNTHETIC_V1",
    )
    if type(candidate) is not ProductionOperatorCandidate:
        raise ProductionOperatorFailure(HOLD_SCHEMA, "fixed constructor lost its kernel")
    return candidate


def build_fixed_heterogeneous_two_state_operator(
    *,
    block_size: int = 2,
    maximum_working_bytes: int = DEFAULT_MAXIMUM_WORKING_BYTES,
) -> ProductionOperatorCandidate:
    """Build the closed heterogeneous two-state one-root design fixture.

    The exact literal template is ``q01=1/2``, ``q10=1/4``, reversible masses
    ``(1,2)``, and killing ``(1/8,1/2)``.  Starting later from state zero makes
    the integrated killing density initially rise and eventually decay, which
    is useful for a one-root topology method test.  This constructor itself
    executes neither propagation nor topology and remains non-authoritative.
    """

    if (
        type(block_size) is not int
        or block_size < 1
        or type(maximum_working_bytes) is not int
        or maximum_working_bytes < 1
    ):
        raise ProductionOperatorFailure(
            HOLD_SCHEMA,
            "fixed heterogeneous resource cap is invalid",
        )
    axis = CallerSuppliedAxisSpec(
        name="fixed_heterogeneous_axis",
        periodic=False,
        forward=((0.5, 0.5), (0.0, 0.0)),
        backward=((0.0, 0.0), (0.25, 0.25)),
        stationary_mass=((1.0, 1.0), (2.0, 2.0)),
    )
    spec = CallerSuppliedOperatorSpec(
        fixture_role="fixed_heterogeneous_two_state_one_root_design_v1",
        tensor_shape=(2,),
        axes=(axis,),
        killing=((0.125, 0.125), (0.5, 0.5)),
        block_size=block_size,
        maximum_working_bytes=maximum_working_bytes,
        uniformization_rate=None,
    )
    candidate = _build_production_operator(
        spec,
        input_provenance="INTERNAL_FIXED_HETEROGENEOUS_TWO_STATE_V1",
    )
    if type(candidate) is not ProductionOperatorCandidate:
        raise ProductionOperatorFailure(
            HOLD_SCHEMA,
            "fixed heterogeneous constructor lost its kernel",
        )
    return candidate
