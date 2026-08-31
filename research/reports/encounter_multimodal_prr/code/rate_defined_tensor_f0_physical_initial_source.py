"""Bind the physical compact-bump initial law to a tiny packed target.

This successor closes one deliberately narrow provenance gap.  It accepts only
the frozen, control-free analytic-source bytes, reconstructs an exact tiny
finite-volume partition, rigorously encloses every compact-bump cell mass,
forms the C-order tensor component box, and then invokes the frozen Round-164
target adapter.  The returned wrapper retains the analytic certificate through
later uniformization chunks, but marks current-target lineage unreplayed after
the initial target; it also does not bind the packed operator to the same
physical axis geometry.

The scope is intentionally still tiny (at most 64 states) and same-process.
It is not the file-backed production constructor, a clean independent replay,
a topology certificate, a continuum limit, or an F0/F1/release decision.  It
does not read a prospective selector/control artifact or killing array and
does not evaluate positive-budget propagation or a positive-budget result.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import struct
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Final

import rate_defined_tensor_f0 as f0
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_rate_action as rate_action
import rate_defined_tensor_f0_packed_target_uniformization as target_uniformization

ANALYTIC_SOURCE_SCHEMA: Final = "encounter_physical_initial_analytic_source_v1"
ACCEPTED_ANALYTIC_SOURCE_SHA256: Final = (
    "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
)
ACCEPTED_F0_SOURCE_SHA256: Final = (
    "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5"
)
ACCEPTED_PACKED_SOURCE_SHA256: Final = (
    "447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4"
)
ACCEPTED_TARGET_SOURCE_SHA256: Final = (
    "5acd20fc227defc7573f4a54b2ab543f192719b3bd7be65de5620c2ef4491323"
)

CONFIGURATION_ID: Final = "tiny_physical_domain_periodic_cut_at_source_c4_v1"
DERIVATION_SCHEMA: Final = "physical_initial_source_to_packed_box_tiny_v1"
BOUND_TARGET_SCHEMA: Final = "physical_analytic_bound_target_tiny_v1"
TENSOR_ORDER: Final = "C:midpoint_outer_relative_parallel_middle_transverse_inner"
ALGORITHM_ID: Final = (
    "shared_normalizer_directed_mpfr_composite_simpson_"
    "exact_dyadic_triple_product_single_outward_round_v1"
)
METHOD_STATUS: Final = "PASS_PHYSICAL_INITIAL_SOURCE_BINDING_TINY_METHOD_ONLY_NOT_F0"
PANELS_PER_UNIT: Final = 16_384
PRECISION_BITS: Final = 192
MAXIMUM_STATES: Final = 64
BLOCK_SIZE: Final = 16
MAXIMUM_WORKING_BYTES: Final = 2_000_000

_COORDINATE_ORDER: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)

_EXPECTED_SOURCE_OBJECT: Final = {
    "analytic_total_mass_exact": "1/1",
    "construction": "independent_product_of_three_analytically_normalized_compact_bumps",
    "coordinate_order": list(_COORDINATE_ORDER),
    "half_width_binary64_hex": "0x1.47ae147ae147bp-6",
    "marginal_density": "b((x-c)/h)/(h*I_b)",
    "normalization": "I_b=integral_-1^1_b(u)_du",
    "periodic_coordinate": "relative_perpendicular",
    "periodic_wrap": "sum_over_periodic_images_before_cell_integration",
    "physical_dimension": 2,
    "quotient_dimension": 3,
    "schema": ANALYTIC_SOURCE_SCHEMA,
    "shared_normalizer_across_cells_and_axes": True,
    "scope": "physical_initial_law_only_no_control_no_budget",
    "shape_definition": "b(u)=indicator(abs(u)<1)*exp(-1/(1-u^2))",
    "starts_binary64_hex": {
        "midpoint": "0x1.1eb851eb851ecp-3",
        "relative_parallel": "-0x1.6666666666666p-2",
        "relative_perpendicular": "0x0.0p+0",
    },
    "transverse_period_exact": "1/1",
}


class PhysicalInitialSourceFailure(RuntimeError):
    """Fail-closed error for the tiny analytic-source binding layer."""


@dataclass(frozen=True, slots=True)
class AnalyticInitialSource:
    schema: str
    source_sha256: str
    coordinate_order: tuple[str, str, str]
    centres: tuple[Fraction, Fraction, Fraction]
    half_width: Fraction
    transverse_period: Fraction
    analytic_total_mass: Fraction
    common_normalizer: bool
    control_free: bool


@dataclass(frozen=True, slots=True)
class ExactAxisPartition:
    name: str
    lower: Fraction
    upper: Fraction
    periodic: bool
    cells: tuple[tuple[tuple[Fraction, Fraction], ...], ...]
    volumes: tuple[Fraction, ...]
    construction: str


@dataclass(frozen=True, slots=True)
class MarginalCellEnclosure:
    coordinate: str
    centre: Fraction
    half_width: Fraction
    period: Fraction | None
    intervals: tuple[f0.OutwardInterval, ...]
    analytic_total_mass: Fraction
    active_indices: tuple[int, ...]
    raw_sha256: str


@dataclass(frozen=True, slots=True)
class PhysicalInitialCertificate:
    schema: str
    status: str
    analytic_source_sha256: str
    axis_geometry_sha256: str
    derivation_contract_sha256: str
    dependency_source_sha256s: tuple[str, str, str]
    marginal_raw_sha256s: tuple[str, str, str]
    active_index_sha256: str
    active_component_count: int
    logical_shape: tuple[int, int, int]
    state_count: int
    component_box_raw_sha256: str
    component_box_manifest_sha256: str
    lower_mass_exact: Fraction
    upper_mass_exact: Fraction
    lower_anchor_l1_radius_exact: Fraction
    source_certificate_sha256: str
    analytic_source_rederived: bool
    exact_partition_proved: bool
    nonperiodic_support_contained: bool
    periodic_unit_mass_proved: bool
    analytic_initial_unit_mass_proved: bool
    analytic_initial_componentwise_contained: bool
    tensor_order_bound: bool
    control_values_read: bool
    positive_budget_scientific_result_read: bool
    fresh_process: bool
    independent_semantic_replay_complete: bool
    production_resource_gate: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class AnalyticBoundTarget:
    schema: str
    certificate: PhysicalInitialCertificate
    target: target_uniformization.CertifiedTargetBall
    current_target_binding_sha256: str
    bound_target_binding_sha256: str
    canonical_initial_source_bound: bool
    analytic_source_certificate_retained: bool
    independent_replay_receipt_retained: bool
    result_self_contained_source_provenance: bool
    current_target_lineage_replayed: bool
    operator_axis_geometry_bound: bool
    fresh_process: bool
    independent_semantic_replay_complete: bool
    production_resource_gate: bool
    f0_pass: bool


@dataclass(frozen=True, slots=True)
class PhysicalInitialDerivation:
    source: AnalyticInitialSource
    axes: tuple[ExactAxisPartition, ExactAxisPartition, ExactAxisPartition]
    marginals: tuple[MarginalCellEnclosure, MarginalCellEnclosure, MarginalCellEnclosure]
    component_box: packed.CanonicalPackedIntervals
    bound_target: AnalyticBoundTarget


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    scratch = bytearray(16_384)
    with path.open("rb", buffering=0) as source:
        while True:
            count = source.readinto(scratch)
            if count == 0:
                break
            digest.update(memoryview(scratch)[:count])
    return digest.hexdigest()


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


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise PhysicalInitialSourceFailure("analytic source has a duplicate or invalid key")
        result[key] = value
    return result


def _exact_dyadic_from_hex(value: object, *, label: str) -> Fraction:
    if type(value) is not str:
        raise PhysicalInitialSourceFailure(f"{label} is not a canonical hex float string")
    try:
        parsed = float.fromhex(value)
    except ValueError as error:
        raise PhysicalInitialSourceFailure(f"{label} is not a valid hex float") from error
    if not math.isfinite(parsed) or parsed.hex() != value:
        raise PhysicalInitialSourceFailure(f"{label} is not canonical finite binary64")
    if parsed == 0.0 and math.copysign(1.0, parsed) < 0:
        raise PhysicalInitialSourceFailure(f"{label} contains negative zero")
    return Fraction.from_float(parsed)


def _verify_dependency_bytes() -> tuple[str, str, str]:
    observed = (
        _sha256_file(Path(f0.__file__).resolve()),
        _sha256_file(Path(packed.__file__).resolve()),
        _sha256_file(Path(target_uniformization.__file__).resolve()),
    )
    accepted = (
        ACCEPTED_F0_SOURCE_SHA256,
        ACCEPTED_PACKED_SOURCE_SHA256,
        ACCEPTED_TARGET_SOURCE_SHA256,
    )
    if observed != accepted:
        raise PhysicalInitialSourceFailure("accepted source-to-box dependency bytes changed")
    return observed


def parse_analytic_initial_source(
    source_bytes: bytes,
    *,
    accepted_source_sha256: str,
) -> AnalyticInitialSource:
    """Parse only the internally accepted control-free analytic source bytes."""

    if type(source_bytes) is not bytes or not _is_sha256(accepted_source_sha256):
        raise PhysicalInitialSourceFailure("analytic source input types are invalid")
    if accepted_source_sha256 != ACCEPTED_ANALYTIC_SOURCE_SHA256:
        raise PhysicalInitialSourceFailure("analytic source digest is not in the accepted registry")
    observed = _sha256_bytes(source_bytes)
    if not hmac.compare_digest(observed, accepted_source_sha256):
        raise PhysicalInitialSourceFailure(
            "analytic source bytes disagree with the accepted digest"
        )
    try:
        payload = json.loads(source_bytes.decode("ascii"), object_pairs_hook=_strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PhysicalInitialSourceFailure("analytic source is not strict ASCII JSON") from error
    if type(payload) is not dict or payload != _EXPECTED_SOURCE_OBJECT:
        raise PhysicalInitialSourceFailure("analytic source semantics are not the accepted law")

    starts = payload["starts_binary64_hex"]
    if type(starts) is not dict:
        raise PhysicalInitialSourceFailure("analytic source starts object is invalid")
    centres = tuple(
        _exact_dyadic_from_hex(starts[name], label=f"{name} centre") for name in _COORDINATE_ORDER
    )
    half_width = _exact_dyadic_from_hex(
        payload["half_width_binary64_hex"], label="initial half width"
    )
    period = Fraction(1)
    if payload["transverse_period_exact"] != _fraction_text(period):
        raise PhysicalInitialSourceFailure("transverse period is not canonical")
    if half_width <= 0 or 2 * half_width >= period:
        raise PhysicalInitialSourceFailure("compact-bump support is invalid")
    return AnalyticInitialSource(
        schema=ANALYTIC_SOURCE_SCHEMA,
        source_sha256=observed,
        coordinate_order=_COORDINATE_ORDER,
        centres=centres,
        half_width=half_width,
        transverse_period=period,
        analytic_total_mass=Fraction(1),
        common_normalizer=True,
        control_free=True,
    )


def _uniform_partition(
    name: str,
    lower: Fraction,
    upper: Fraction,
    *,
    periodic: bool,
) -> ExactAxisPartition:
    width = (upper - lower) / 4
    cells = tuple(((lower + index * width, lower + (index + 1) * width),) for index in range(4))
    axis = ExactAxisPartition(
        name=name,
        lower=lower,
        upper=upper,
        periodic=periodic,
        cells=cells,
        volumes=(width,) * 4,
        construction="exact_uniform_cell_partition_periodic"
        if periodic
        else "exact_uniform_cell_partition_reflecting_domain",
    )
    _validate_exact_partition(axis)
    return axis


def _tiny_partitions() -> tuple[ExactAxisPartition, ExactAxisPartition, ExactAxisPartition]:
    # M and R use the frozen physical base domains.  The periodic quotient is
    # represented by [0,1], placing the physical Y0=0 source at the cut so the
    # tiny proof exercises periodic image unfolding instead of a special
    # interior-only case.
    return (
        _uniform_partition(
            "midpoint",
            Fraction.from_float(float.fromhex("-0x1.0000000000000p-2")),
            Fraction.from_float(float.fromhex("0x1.d99999999999ap+0")),
            periodic=False,
        ),
        _uniform_partition(
            "relative_parallel",
            Fraction.from_float(float.fromhex("-0x1.ccccccccccccdp+0")),
            Fraction.from_float(float.fromhex("0x1.ccccccccccccdp+0")),
            periodic=False,
        ),
        _uniform_partition(
            "relative_perpendicular",
            Fraction(0),
            Fraction(1),
            periodic=True,
        ),
    )


def _validate_exact_partition(axis: ExactAxisPartition) -> None:
    if (
        type(axis) is not ExactAxisPartition
        or not axis.name
        or axis.lower >= axis.upper
        or len(axis.cells) != len(axis.volumes)
        or not axis.cells
    ):
        raise PhysicalInitialSourceFailure("exact axis partition metadata is invalid")
    flattened: list[tuple[Fraction, Fraction]] = []
    for segments, volume in zip(axis.cells, axis.volumes, strict=True):
        if not segments or volume <= 0:
            raise PhysicalInitialSourceFailure("exact axis cell is empty")
        segment_mass = Fraction(0)
        for lower, upper in segments:
            if lower < axis.lower or upper > axis.upper or lower >= upper:
                raise PhysicalInitialSourceFailure("exact axis segment is outside the domain")
            segment_mass += upper - lower
            flattened.append((lower, upper))
        if segment_mass != volume:
            raise PhysicalInitialSourceFailure("exact axis cell volume disagrees with segments")
    flattened.sort()
    cursor = axis.lower
    for lower, upper in flattened:
        if lower != cursor:
            raise PhysicalInitialSourceFailure("exact axis partition has a gap or overlap")
        cursor = upper
    if cursor != axis.upper or sum(axis.volumes, Fraction(0)) != axis.upper - axis.lower:
        raise PhysicalInitialSourceFailure("exact axis partition does not cover its domain")


def _axis_geometry_sha256(axes: tuple[ExactAxisPartition, ...]) -> str:
    payload: list[object] = [CONFIGURATION_ID, len(axes)]
    for axis in axes:
        _validate_exact_partition(axis)
        payload.extend(
            (
                axis.name,
                _fraction_text(axis.lower),
                _fraction_text(axis.upper),
                axis.periodic,
                axis.construction,
                len(axis.cells),
            )
        )
        for segments, volume in zip(axis.cells, axis.volumes, strict=True):
            payload.extend((_fraction_text(volume), len(segments)))
            for lower, upper in segments:
                payload.extend((_fraction_text(lower), _fraction_text(upper)))
    return _digest_fields(b"physical-initial-tiny-axis-geometry-v1\x00", *payload)


def _image_indices(
    segment_lower: Fraction,
    segment_upper: Fraction,
    *,
    centre: Fraction,
    half_width: Fraction,
    period: Fraction,
) -> range:
    first = math.ceil((segment_lower - centre - half_width) / period)
    last = math.floor((segment_upper - centre + half_width) / period)
    return range(first, last + 1)


def _marginal_raw_sha256(intervals: tuple[f0.OutwardInterval, ...]) -> str:
    digest = hashlib.sha256(b"physical-initial-marginal-endpoints-v1\x00")
    for interval in intervals:
        digest.update(struct.pack(">dd", interval.lower, interval.upper))
    return digest.hexdigest()


def _build_marginal(
    axis: ExactAxisPartition,
    *,
    centre: Fraction,
    half_width: Fraction,
    period: Fraction | None,
    normalization: f0.OutwardInterval,
) -> MarginalCellEnclosure:
    _validate_exact_partition(axis)
    if axis.periodic != (period is not None):
        raise PhysicalInitialSourceFailure("axis periodicity disagrees with analytic source")
    if period is None and not (
        axis.lower <= centre - half_width and centre + half_width <= axis.upper
    ):
        raise PhysicalInitialSourceFailure("nonperiodic compact-bump support leaves the domain")
    if period is not None and axis.upper - axis.lower != period:
        raise PhysicalInitialSourceFailure("periodic partition width disagrees with source period")

    intervals: list[f0.OutwardInterval] = []
    for segments in axis.cells:
        raw = f0.ZERO_INTERVAL
        for segment_lower, segment_upper in segments:
            images = (0,)
            if period is not None:
                images = _image_indices(
                    segment_lower,
                    segment_upper,
                    centre=centre,
                    half_width=half_width,
                    period=period,
                )
            for image_index in images:
                image_centre = centre if period is None else centre + image_index * period
                overlap_lower = max(segment_lower, image_centre - half_width)
                overlap_upper = min(segment_upper, image_centre + half_width)
                if overlap_upper <= overlap_lower:
                    continue
                local = f0.compact_bump_integral_interval(
                    (overlap_lower - image_centre) / half_width,
                    (overlap_upper - image_centre) / half_width,
                    panels_per_unit=PANELS_PER_UNIT,
                    precision_bits=PRECISION_BITS,
                )
                raw = raw.add_nonnegative(local)
        intervals.append(raw.divide_positive(normalization))
    result = tuple(intervals)
    lower_mass = sum((entry.lower_fraction for entry in result), Fraction(0))
    upper_mass = sum((entry.upper_fraction for entry in result), Fraction(0))
    if not lower_mass <= 1 <= upper_mass:
        raise PhysicalInitialSourceFailure("marginal interval box misses analytic unit mass")
    active = tuple(index for index, entry in enumerate(result) if entry.upper > 0.0)
    if not active:
        raise PhysicalInitialSourceFailure("marginal compact-bump support is empty")
    return MarginalCellEnclosure(
        coordinate=axis.name,
        centre=centre,
        half_width=half_width,
        period=period,
        intervals=result,
        analytic_total_mass=Fraction(1),
        active_indices=active,
        raw_sha256=_marginal_raw_sha256(result),
    )


def _derivation_contract_sha256(
    dependencies: tuple[str, str, str],
    *,
    axis_geometry_sha256: str,
) -> str:
    return _digest_fields(
        b"physical-initial-derivation-contract-v1\x00",
        DERIVATION_SCHEMA,
        CONFIGURATION_ID,
        TENSOR_ORDER,
        ALGORITHM_ID,
        PANELS_PER_UNIT,
        PRECISION_BITS,
        MAXIMUM_STATES,
        BLOCK_SIZE,
        MAXIMUM_WORKING_BYTES,
        axis_geometry_sha256,
        *dependencies,
    )


def _active_index_sha256(active_indices: tuple[int, ...]) -> str:
    digest = hashlib.sha256(b"physical-initial-active-flat-indices-v1\x00")
    for index in active_indices:
        digest.update(index.to_bytes(8, "big"))
    return digest.hexdigest()


def _certificate_digest(certificate: PhysicalInitialCertificate) -> str:
    return _digest_fields(
        b"physical-initial-source-certificate-v1\x00",
        certificate.schema,
        certificate.status,
        certificate.analytic_source_sha256,
        certificate.axis_geometry_sha256,
        certificate.derivation_contract_sha256,
        *certificate.dependency_source_sha256s,
        *certificate.marginal_raw_sha256s,
        certificate.active_index_sha256,
        certificate.active_component_count,
        *certificate.logical_shape,
        certificate.state_count,
        certificate.component_box_raw_sha256,
        certificate.component_box_manifest_sha256,
        certificate.lower_mass_exact.numerator,
        certificate.lower_mass_exact.denominator,
        certificate.upper_mass_exact.numerator,
        certificate.upper_mass_exact.denominator,
        certificate.lower_anchor_l1_radius_exact.numerator,
        certificate.lower_anchor_l1_radius_exact.denominator,
        certificate.analytic_source_rederived,
        certificate.exact_partition_proved,
        certificate.nonperiodic_support_contained,
        certificate.periodic_unit_mass_proved,
        certificate.analytic_initial_unit_mass_proved,
        certificate.analytic_initial_componentwise_contained,
        certificate.tensor_order_bound,
        certificate.control_values_read,
        certificate.positive_budget_scientific_result_read,
        certificate.fresh_process,
        certificate.independent_semantic_replay_complete,
        certificate.production_resource_gate,
        certificate.f0_pass,
    )


def validate_certificate(certificate: PhysicalInitialCertificate) -> None:
    if type(certificate) is not PhysicalInitialCertificate:
        raise PhysicalInitialSourceFailure("physical initial certificate has the wrong type")
    if (
        certificate.schema != DERIVATION_SCHEMA
        or certificate.status != METHOD_STATUS
        or certificate.analytic_source_sha256 != ACCEPTED_ANALYTIC_SOURCE_SHA256
        or not _is_sha256(certificate.axis_geometry_sha256)
        or not _is_sha256(certificate.derivation_contract_sha256)
        or certificate.dependency_source_sha256s
        != (
            ACCEPTED_F0_SOURCE_SHA256,
            ACCEPTED_PACKED_SOURCE_SHA256,
            ACCEPTED_TARGET_SOURCE_SHA256,
        )
        or any(not _is_sha256(value) for value in certificate.marginal_raw_sha256s)
        or not _is_sha256(certificate.active_index_sha256)
        or certificate.active_component_count < 1
        or certificate.logical_shape != (4, 4, 4)
        or certificate.state_count != 64
        or not _is_sha256(certificate.component_box_raw_sha256)
        or not _is_sha256(certificate.component_box_manifest_sha256)
        or not certificate.lower_mass_exact <= 1 <= certificate.upper_mass_exact
        or certificate.lower_anchor_l1_radius_exact != 1 - certificate.lower_mass_exact
        or certificate.lower_anchor_l1_radius_exact < 0
        or certificate.source_certificate_sha256 != _certificate_digest(certificate)
        or certificate.analytic_source_rederived is not True
        or certificate.exact_partition_proved is not True
        or certificate.nonperiodic_support_contained is not True
        or certificate.periodic_unit_mass_proved is not True
        or certificate.analytic_initial_unit_mass_proved is not True
        or certificate.analytic_initial_componentwise_contained is not True
        or certificate.tensor_order_bound is not True
        or certificate.control_values_read is not False
        or certificate.positive_budget_scientific_result_read is not False
        or certificate.fresh_process is not False
        or certificate.independent_semantic_replay_complete is not False
        or certificate.production_resource_gate is not False
        or certificate.f0_pass is not False
    ):
        raise PhysicalInitialSourceFailure("physical initial certificate ledger is invalid")


def _bound_target_digest(bound: AnalyticBoundTarget) -> str:
    return _digest_fields(
        b"physical-analytic-bound-target-v1\x00",
        bound.schema,
        bound.certificate.source_certificate_sha256,
        bound.current_target_binding_sha256,
        bound.canonical_initial_source_bound,
        bound.analytic_source_certificate_retained,
        bound.independent_replay_receipt_retained,
        bound.result_self_contained_source_provenance,
        bound.current_target_lineage_replayed,
        bound.operator_axis_geometry_bound,
        bound.fresh_process,
        bound.independent_semantic_replay_complete,
        bound.production_resource_gate,
        bound.f0_pass,
    )


def validate_bound_target_structure_only(bound: AnalyticBoundTarget) -> None:
    """Check an in-memory ledger; this does not rederive analytic provenance."""

    if type(bound) is not AnalyticBoundTarget:
        raise PhysicalInitialSourceFailure("analytic bound target has the wrong type")
    validate_certificate(bound.certificate)
    target_uniformization.validate_target_ball_structure_only(bound.target)
    if (
        bound.schema != BOUND_TARGET_SCHEMA
        or bound.current_target_binding_sha256 != bound.target.binding_sha256
        or bound.certificate.component_box_raw_sha256 != bound.target.component_box_raw_sha256
        or bound.certificate.component_box_manifest_sha256
        != bound.target.component_box_manifest_sha256
        or bound.bound_target_binding_sha256 != _bound_target_digest(bound)
        or bound.canonical_initial_source_bound is not True
        or bound.analytic_source_certificate_retained is not True
        or bound.independent_replay_receipt_retained is not False
        or bound.result_self_contained_source_provenance is not False
        or type(bound.current_target_lineage_replayed) is not bool
        or bound.operator_axis_geometry_bound is not False
        or bound.fresh_process is not False
        or bound.independent_semantic_replay_complete is not False
        or bound.production_resource_gate is not False
        or bound.f0_pass is not False
    ):
        raise PhysicalInitialSourceFailure("analytic bound-target ledger is invalid")
    if (bound.target.cumulative_chunk_count == 0) != bound.current_target_lineage_replayed:
        raise PhysicalInitialSourceFailure(
            "current-target lineage flag exceeds the retained-receipt boundary"
        )


def _wrap_bound_target(
    certificate: PhysicalInitialCertificate,
    target: target_uniformization.CertifiedTargetBall,
    *,
    current_target_lineage_replayed: bool,
) -> AnalyticBoundTarget:
    provisional = AnalyticBoundTarget(
        schema=BOUND_TARGET_SCHEMA,
        certificate=certificate,
        target=target,
        current_target_binding_sha256=target.binding_sha256,
        bound_target_binding_sha256="0" * 64,
        canonical_initial_source_bound=True,
        analytic_source_certificate_retained=True,
        independent_replay_receipt_retained=False,
        result_self_contained_source_provenance=False,
        current_target_lineage_replayed=current_target_lineage_replayed,
        operator_axis_geometry_bound=False,
        fresh_process=False,
        independent_semantic_replay_complete=False,
        production_resource_gate=False,
        f0_pass=False,
    )
    bound = AnalyticBoundTarget(
        schema=provisional.schema,
        certificate=provisional.certificate,
        target=provisional.target,
        current_target_binding_sha256=provisional.current_target_binding_sha256,
        bound_target_binding_sha256=_bound_target_digest(provisional),
        canonical_initial_source_bound=provisional.canonical_initial_source_bound,
        analytic_source_certificate_retained=provisional.analytic_source_certificate_retained,
        independent_replay_receipt_retained=provisional.independent_replay_receipt_retained,
        result_self_contained_source_provenance=(
            provisional.result_self_contained_source_provenance
        ),
        current_target_lineage_replayed=provisional.current_target_lineage_replayed,
        operator_axis_geometry_bound=provisional.operator_axis_geometry_bound,
        fresh_process=provisional.fresh_process,
        independent_semantic_replay_complete=provisional.independent_semantic_replay_complete,
        production_resource_gate=provisional.production_resource_gate,
        f0_pass=provisional.f0_pass,
    )
    validate_bound_target_structure_only(bound)
    return bound


def derive_tiny_physical_initial_target(
    source_bytes: bytes,
    *,
    accepted_source_sha256: str,
    configuration_id: str,
) -> PhysicalInitialDerivation:
    """Rebuild the accepted analytic law and bind it to a 4x4x4 target box."""

    if configuration_id != CONFIGURATION_ID:
        raise PhysicalInitialSourceFailure("tiny source-binding configuration is not accepted")
    dependencies = _verify_dependency_bytes()
    source = parse_analytic_initial_source(
        source_bytes,
        accepted_source_sha256=accepted_source_sha256,
    )
    axes = _tiny_partitions()
    if tuple(axis.name for axis in axes) != source.coordinate_order:
        raise PhysicalInitialSourceFailure("axis order disagrees with analytic source")
    if math.prod(len(axis.cells) for axis in axes) > MAXIMUM_STATES:
        raise PhysicalInitialSourceFailure("tiny analytic-source state cap was exceeded")

    normalization = f0.compact_bump_integral_interval(
        -1,
        1,
        panels_per_unit=PANELS_PER_UNIT,
        precision_bits=PRECISION_BITS,
    )
    marginals = tuple(
        _build_marginal(
            axis,
            centre=source.centres[index],
            half_width=source.half_width,
            period=source.transverse_period if axis.periodic else None,
            normalization=normalization,
        )
        for index, axis in enumerate(axes)
    )
    midpoint, relative, transverse = (profile.intervals for profile in marginals)
    tensor_intervals: list[f0.OutwardInterval] = []
    active_indices: list[int] = []
    for m_index, m_value in enumerate(midpoint):
        for r_index, r_value in enumerate(relative):
            for y_index, y_value in enumerate(transverse):
                lower = m_value.lower_fraction * r_value.lower_fraction * y_value.lower_fraction
                upper = m_value.upper_fraction * r_value.upper_fraction * y_value.upper_fraction
                interval = f0.OutwardInterval.from_fraction_bounds(lower, upper)
                flat = (m_index * len(relative) + r_index) * len(transverse) + y_index
                if interval.upper > 0.0:
                    active_indices.append(flat)
                tensor_intervals.append(interval)
    endpoint_pairs = tuple((entry.lower, entry.upper) for entry in tensor_intervals)
    logical_shape = tuple(len(axis.cells) for axis in axes)
    payload = packed.create_packed_interval_payload(
        endpoint_pairs,
        role=target_uniformization.INITIAL_BOX_ROLE,
        logical_shape=logical_shape,
        nonnegative=True,
        block_size=BLOCK_SIZE,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )
    component_box = packed.load_canonical_packed_intervals(payload)
    target = target_uniformization.make_initial_target_ball(component_box)

    lower_mass = sum((entry.lower_fraction for entry in tensor_intervals), Fraction(0))
    upper_mass = sum((entry.upper_fraction for entry in tensor_intervals), Fraction(0))
    if not lower_mass <= 1 <= upper_mass:
        raise PhysicalInitialSourceFailure("tensor component box misses analytic unit mass")
    axis_digest = _axis_geometry_sha256(axes)
    contract_digest = _derivation_contract_sha256(
        dependencies,
        axis_geometry_sha256=axis_digest,
    )
    provisional = PhysicalInitialCertificate(
        schema=DERIVATION_SCHEMA,
        status=METHOD_STATUS,
        analytic_source_sha256=source.source_sha256,
        axis_geometry_sha256=axis_digest,
        derivation_contract_sha256=contract_digest,
        dependency_source_sha256s=dependencies,
        marginal_raw_sha256s=tuple(profile.raw_sha256 for profile in marginals),
        active_index_sha256=_active_index_sha256(tuple(active_indices)),
        active_component_count=len(active_indices),
        logical_shape=logical_shape,
        state_count=math.prod(logical_shape),
        component_box_raw_sha256=component_box.manifest.raw_sha256,
        component_box_manifest_sha256=target.component_box_manifest_sha256,
        lower_mass_exact=lower_mass,
        upper_mass_exact=upper_mass,
        lower_anchor_l1_radius_exact=Fraction(1) - lower_mass,
        source_certificate_sha256="0" * 64,
        analytic_source_rederived=True,
        exact_partition_proved=True,
        nonperiodic_support_contained=True,
        periodic_unit_mass_proved=True,
        analytic_initial_unit_mass_proved=True,
        analytic_initial_componentwise_contained=True,
        tensor_order_bound=True,
        control_values_read=False,
        positive_budget_scientific_result_read=False,
        fresh_process=False,
        independent_semantic_replay_complete=False,
        production_resource_gate=False,
        f0_pass=False,
    )
    certificate = PhysicalInitialCertificate(
        **{
            field: getattr(provisional, field)
            for field in provisional.__dataclass_fields__
            if field != "source_certificate_sha256"
        },
        source_certificate_sha256=_certificate_digest(provisional),
    )
    validate_certificate(certificate)
    bound = _wrap_bound_target(
        certificate,
        target,
        current_target_lineage_replayed=True,
    )
    return PhysicalInitialDerivation(
        source=source,
        axes=axes,
        marginals=marginals,
        component_box=component_box,
        bound_target=bound,
    )


def verify_claimed_tiny_physical_initial_derivation(
    source_bytes: bytes,
    claimed: PhysicalInitialDerivation,
    *,
    accepted_source_sha256: str,
    configuration_id: str,
) -> PhysicalInitialCertificate:
    """Rederive source-to-box bytes and reject any coherent substitute box."""

    if type(claimed) is not PhysicalInitialDerivation:
        raise PhysicalInitialSourceFailure("claimed physical derivation has the wrong type")
    expected = derive_tiny_physical_initial_target(
        source_bytes,
        accepted_source_sha256=accepted_source_sha256,
        configuration_id=configuration_id,
    )
    validate_bound_target_structure_only(claimed.bound_target)
    packed.validate_canonical_packed_intervals(claimed.component_box)
    expected_raw = memoryview(expected.component_box.intervals).cast("B")
    claimed_raw = memoryview(claimed.component_box.intervals).cast("B")
    if (
        claimed.source != expected.source
        or claimed.axes != expected.axes
        or claimed.marginals != expected.marginals
        or claimed.component_box.manifest != expected.component_box.manifest
        or not hmac.compare_digest(expected_raw, claimed_raw)
        or claimed.bound_target.certificate != expected.bound_target.certificate
        or claimed.bound_target.target.binding_sha256 != expected.bound_target.target.binding_sha256
        or claimed.bound_target.bound_target_binding_sha256
        != expected.bound_target.bound_target_binding_sha256
    ):
        raise PhysicalInitialSourceFailure(
            "claimed component box is not the deterministic analytic-source derivation"
        )
    return expected.bound_target.certificate


def propagate_bound_target(
    kernel: packed.PackedTensorKernel,
    bound: AnalyticBoundTarget,
    contract: rate_action.RateActionContract,
    *,
    source_bytes: bytes,
    initial_derivation: PhysicalInitialDerivation,
    accepted_source_sha256: str,
    configuration_id: str,
    time: Fraction,
    tail_tolerance: Fraction,
    maximum_terms: int = 64,
) -> tuple[target_uniformization.TargetUniformizationResult, AnalyticBoundTarget]:
    """Run one frozen tiny chunk while retaining the analytic initial receipt.

    The frozen operator is bound by its own replay digest.  A future successor
    must additionally prove that its axes/rates came from this certificate's
    physical geometry and replay the serialized predecessor history.  This
    wrapper keeps both authority claims false after propagation.
    """

    verified_certificate = verify_claimed_tiny_physical_initial_derivation(
        source_bytes,
        initial_derivation,
        accepted_source_sha256=accepted_source_sha256,
        configuration_id=configuration_id,
    )
    validate_bound_target_structure_only(bound)
    if bound.certificate != verified_certificate:
        raise PhysicalInitialSourceFailure(
            "propagated target is not attached to the rederived analytic source"
        )
    if bound.target.cumulative_chunk_count == 0 and (
        bound.current_target_binding_sha256
        != initial_derivation.bound_target.current_target_binding_sha256
        or bound.bound_target_binding_sha256
        != initial_derivation.bound_target.bound_target_binding_sha256
    ):
        raise PhysicalInitialSourceFailure(
            "initial propagated target is not the canonical rederived source target"
        )
    result = target_uniformization.target_uniformize_transpose(
        kernel,
        bound.target,
        contract,
        time=time,
        tail_tolerance=tail_tolerance,
        maximum_terms=maximum_terms,
    )
    if (
        result.target.component_box_raw_sha256 != bound.certificate.component_box_raw_sha256
        or result.target.component_box_manifest_sha256
        != bound.certificate.component_box_manifest_sha256
    ):
        raise PhysicalInitialSourceFailure("uniformization dropped analytic initial provenance")
    successor = _wrap_bound_target(
        bound.certificate,
        result.target,
        current_target_lineage_replayed=False,
    )
    return result, successor
