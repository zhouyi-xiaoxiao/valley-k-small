"""Independent tiny replay of the physical initial source-to-box semantics.

The producer uses composite Simpson plus a global fourth-derivative bound.
This replay first derives the exact structural source witness for the frozen
grid (marginal masses 1, 1, and two periodic halves) and proves that every
claimed component interval contains it.  Separately, monotonic lower/upper
rectangle sums with an independent directed-MPFR exponential provide a broad
numerical consistency check.  The rectangle overlap is not used as the
containment proof.

The replay is a same-process, tiny-scope semantic/numerical implementation.
It proves source containment, not deterministic canonical endpoint identity;
the latter belongs to the producer's byte rederivation gate.  It is not a
clean serialized whole-result replay or a production resource gate.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass
from fractions import Fraction
from typing import Final

import gmpy2
import numpy as np
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_target_uniformization as target_uniformization
import rate_defined_tensor_f0_physical_initial_source as producer

ACCEPTED_ANALYTIC_SOURCE_SHA256: Final = (
    "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
)
CONFIGURATION_ID: Final = "tiny_physical_domain_periodic_cut_at_source_c4_v1"
REPLAY_SCHEMA: Final = "physical_initial_source_semantic_containment_replay_v2"
REPLAY_STATUS: Final = (
    "PASS_INDEPENDENT_TINY_SEMANTIC_CONTAINMENT_AND_RECTANGLE_CONSISTENCY_"
    "NOT_CANONICAL_BYTES_NOT_F0"
)
REPLAY_ALGORITHM_ID: Final = (
    "exact_support_symmetry_witness_plus_monotone_rectangle_mpfr_crosscheck_v2"
)
REPLAY_PANELS_PER_UNIT: Final = 8_192
REPLAY_PRECISION_BITS: Final = 224


class PhysicalInitialReplayFailure(RuntimeError):
    """Fail-closed error for the independent tiny replay."""


@dataclass(frozen=True, slots=True)
class ReplayInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if self.lower < 0 or self.lower > self.upper:
            raise PhysicalInitialReplayFailure("independent replay interval is invalid")

    def divide_positive(self, other: ReplayInterval) -> ReplayInterval:
        if other.lower <= 0:
            raise PhysicalInitialReplayFailure("independent replay denominator contains zero")
        return ReplayInterval(self.lower / other.upper, self.upper / other.lower)


@dataclass(frozen=True, slots=True)
class IndependentSourceReplayReceipt:
    schema: str
    status: str
    algorithm_id: str
    analytic_source_sha256: str
    configuration_id: str
    logical_shape: tuple[int, int, int]
    component_box_raw_sha256: str
    component_box_manifest_sha256: str
    claimed_certificate_sha256: str
    claimed_bound_target_sha256: str
    axis_geometry_sha256: str
    structural_witness_sha256: str
    claimed_marginal_endpoint_sha256s: tuple[str, str, str]
    replay_marginal_endpoint_sha256s: tuple[str, str, str]
    replay_component_endpoint_sha256: str
    producer_marginal_structural_containment_count: int
    producer_component_structural_containment_count: int
    producer_marginal_overlap_count: int
    producer_component_overlap_count: int
    lower_mass_replay: Fraction
    upper_mass_replay: Fraction
    receipt_sha256: str
    source_semantics_checked: bool
    semantic_source_containment_proved: bool
    canonical_box_identity_rederived: bool
    rectangle_overlap_used_only_as_consistency: bool
    independent_numerical_implementation: bool
    producer_quadrature_ledger_consumed: bool
    producer_certificate_flags_consumed: bool
    exact_partition_reconstructed: bool
    periodic_images_reconstructed: bool
    analytic_unit_mass_structural_proof_used: bool
    same_process: bool
    clean_serialized_whole_result_replay: bool
    production_resource_gate: bool
    f0_pass: bool


def _digest_fields(domain: bytes, *fields: object) -> str:
    digest = hashlib.sha256(domain)
    for field in fields:
        encoded = str(field).encode("ascii")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _manifest_sha256(manifest: packed.PackedIntervalManifest) -> str:
    packed.validate_packed_interval_manifest(manifest)
    return _digest_fields(
        b"physical-initial-independent-component-manifest-v1\x00",
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


def _replay_interval_sha256(
    domain: bytes,
    intervals: tuple[ReplayInterval, ...],
) -> str:
    fields: list[object] = [len(intervals)]
    for interval in intervals:
        fields.extend(
            (
                interval.lower.numerator,
                interval.lower.denominator,
                interval.upper.numerator,
                interval.upper.denominator,
            )
        )
    return _digest_fields(domain, *fields)


def _claimed_marginal_sha256(intervals: tuple[object, ...]) -> str:
    digest = hashlib.sha256(b"physical-initial-marginal-endpoints-v1\x00")
    for interval in intervals:
        digest.update(struct.pack(">dd", interval.lower, interval.upper))
    return digest.hexdigest()


def _axis_geometry_sha256(
    partitions: tuple[tuple[tuple[Fraction, Fraction], ...], ...],
) -> str:
    fields: list[object] = [CONFIGURATION_ID, len(partitions)]
    names = ("midpoint", "relative_parallel", "relative_perpendicular")
    for index, cells in enumerate(partitions):
        fields.extend((names[index], index == 2, len(cells)))
        for lower, upper in cells:
            fields.extend((_fraction_text(lower), _fraction_text(upper)))
    return _digest_fields(b"physical-initial-independent-axis-geometry-v1\x00", *fields)


def _structural_witness_sha256(
    marginals: tuple[tuple[Fraction, ...], ...],
    components: tuple[Fraction, ...],
) -> str:
    fields: list[object] = ["exact_support_and_even_periodic_cut_witness_v1"]
    for marginal in marginals:
        fields.append(len(marginal))
        for value in marginal:
            fields.extend((value.numerator, value.denominator))
    fields.append(len(components))
    for value in components:
        fields.extend((value.numerator, value.denominator))
    return _digest_fields(b"physical-initial-independent-structural-witness-v1\x00", *fields)


def _float_bound(value: gmpy2.mpfr, *, lower: bool) -> Fraction:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise PhysicalInitialReplayFailure("MPFR replay value does not fit binary64")
    with gmpy2.context(
        gmpy2.get_context(), precision=REPLAY_PRECISION_BITS + 64, round=gmpy2.RoundToNearest
    ):
        candidate_mpfr = gmpy2.mpfr(candidate)
    if lower and candidate_mpfr > value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(-math.inf)))
    if not lower and candidate_mpfr < value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    exact = Fraction.from_float(candidate)
    if exact < 0:
        raise PhysicalInitialReplayFailure("MPFR replay produced a negative bump value")
    with gmpy2.context(
        gmpy2.get_context(), precision=REPLAY_PRECISION_BITS + 64, round=gmpy2.RoundToNearest
    ):
        exact_mpfr = gmpy2.mpfr(exact.numerator) / gmpy2.mpfr(exact.denominator)
    if (lower and exact_mpfr > value) or (not lower and exact_mpfr < value):
        raise PhysicalInitialReplayFailure("binary64 replay conversion was not outward")
    return exact


def _bump_value_interval(value: Fraction) -> ReplayInterval:
    if value <= -1 or value >= 1:
        return ReplayInterval(Fraction(0), Fraction(0))
    exponent = -Fraction(1, 1 - value * value)
    with gmpy2.context(gmpy2.get_context(), precision=REPLAY_PRECISION_BITS, round=gmpy2.RoundDown):
        exponent_lower = gmpy2.mpfr(exponent.numerator) / gmpy2.mpfr(exponent.denominator)
        value_lower = gmpy2.exp(exponent_lower)
    with gmpy2.context(gmpy2.get_context(), precision=REPLAY_PRECISION_BITS, round=gmpy2.RoundUp):
        exponent_upper = gmpy2.mpfr(exponent.numerator) / gmpy2.mpfr(exponent.denominator)
        value_upper = gmpy2.exp(exponent_upper)
    return ReplayInterval(
        _float_bound(value_lower, lower=True),
        _float_bound(value_upper, lower=False),
    )


def _monotone_rectangle_interval(
    lower: Fraction,
    upper: Fraction,
    *,
    increasing: bool,
) -> ReplayInterval:
    if upper <= lower:
        return ReplayInterval(Fraction(0), Fraction(0))
    panels = max(1, math.ceil((upper - lower) * REPLAY_PANELS_PER_UNIT))
    step = (upper - lower) / panels
    lower_sum = Fraction(0)
    upper_sum = Fraction(0)
    for index in range(panels):
        left = _bump_value_interval(lower + index * step)
        right = _bump_value_interval(lower + (index + 1) * step)
        if increasing:
            lower_sum += left.lower
            upper_sum += right.upper
        else:
            lower_sum += right.lower
            upper_sum += left.upper
    return ReplayInterval(step * lower_sum, step * upper_sum)


def _bump_integral_interval(lower: Fraction, upper: Fraction) -> ReplayInterval:
    lo = max(Fraction(-1), lower)
    hi = min(Fraction(1), upper)
    if hi <= lo:
        return ReplayInterval(Fraction(0), Fraction(0))
    pieces: list[ReplayInterval] = []
    if lo < 0:
        pieces.append(_monotone_rectangle_interval(lo, min(hi, Fraction(0)), increasing=True))
    if hi > 0:
        pieces.append(_monotone_rectangle_interval(max(lo, Fraction(0)), hi, increasing=False))
    return ReplayInterval(
        sum((piece.lower for piece in pieces), Fraction(0)),
        sum((piece.upper for piece in pieces), Fraction(0)),
    )


def _parse_source_independently(
    source_bytes: bytes,
    *,
    accepted_source_sha256: str,
) -> tuple[tuple[Fraction, Fraction, Fraction], Fraction, Fraction]:
    if (
        type(source_bytes) is not bytes
        or accepted_source_sha256 != ACCEPTED_ANALYTIC_SOURCE_SHA256
        or hashlib.sha256(source_bytes).hexdigest() != accepted_source_sha256
    ):
        raise PhysicalInitialReplayFailure("independent replay source hash is not accepted")
    try:
        payload = json.loads(source_bytes.decode("ascii"))
        starts = payload["starts_binary64_hex"]
        if (
            payload["schema"] != "encounter_physical_initial_analytic_source_v1"
            or payload["physical_dimension"] != 2
            or payload["quotient_dimension"] != 3
            or payload["analytic_total_mass_exact"] != "1/1"
            or payload["construction"]
            != "independent_product_of_three_analytically_normalized_compact_bumps"
            or payload["shape_definition"] != "b(u)=indicator(abs(u)<1)*exp(-1/(1-u^2))"
            or payload["coordinate_order"]
            != ["midpoint", "relative_parallel", "relative_perpendicular"]
            or payload["marginal_density"] != "b((x-c)/h)/(h*I_b)"
            or payload["normalization"] != "I_b=integral_-1^1_b(u)_du"
            or payload["shared_normalizer_across_cells_and_axes"] is not True
            or payload["periodic_coordinate"] != "relative_perpendicular"
            or payload["periodic_wrap"] != "sum_over_periodic_images_before_cell_integration"
            or payload["scope"] != "physical_initial_law_only_no_control_no_budget"
            or payload["transverse_period_exact"] != "1/1"
        ):
            raise KeyError("source semantic contract")
        centre_hex = (
            starts["midpoint"],
            starts["relative_parallel"],
            starts["relative_perpendicular"],
        )
        if (
            centre_hex
            != (
                "0x1.1eb851eb851ecp-3",
                "-0x1.6666666666666p-2",
                "0x0.0p+0",
            )
            or payload["half_width_binary64_hex"] != "0x1.47ae147ae147bp-6"
        ):
            raise KeyError("source physical initial parameters")
        centre_floats = tuple(float.fromhex(value) for value in centre_hex)
        if tuple(value.hex() for value in centre_floats) != centre_hex:
            raise ValueError("noncanonical centre hex")
        centres = tuple(Fraction.from_float(value) for value in centre_floats)
        half_width_float = float.fromhex(payload["half_width_binary64_hex"])
        if half_width_float.hex() != payload["half_width_binary64_hex"]:
            raise ValueError("noncanonical half-width hex")
        half_width = Fraction.from_float(half_width_float)
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise PhysicalInitialReplayFailure(
            "independent replay source semantics are invalid"
        ) from error
    if half_width <= 0 or 2 * half_width >= 1:
        raise PhysicalInitialReplayFailure("independent replay source support is invalid")
    return centres, half_width, Fraction(1)


def _partitions() -> tuple[tuple[tuple[Fraction, Fraction], ...], ...]:
    domains = (
        (
            Fraction.from_float(float.fromhex("-0x1.0000000000000p-2")),
            Fraction.from_float(float.fromhex("0x1.d99999999999ap+0")),
        ),
        (
            Fraction.from_float(float.fromhex("-0x1.ccccccccccccdp+0")),
            Fraction.from_float(float.fromhex("0x1.ccccccccccccdp+0")),
        ),
        (Fraction(0), Fraction(1)),
    )
    result = []
    for lower, upper in domains:
        width = (upper - lower) / 4
        cells = tuple((lower + index * width, lower + (index + 1) * width) for index in range(4))
        if cells[0][0] != lower or cells[-1][1] != upper:
            raise PhysicalInitialReplayFailure("independent replay partition endpoint drifted")
        if any(left[1] != right[0] for left, right in zip(cells, cells[1:], strict=False)):
            raise PhysicalInitialReplayFailure("independent replay partition is not contiguous")
        result.append(cells)
    return tuple(result)


def _exact_structural_witness(
    partitions: tuple[tuple[tuple[Fraction, Fraction], ...], ...],
    centres: tuple[Fraction, Fraction, Fraction],
    half_width: Fraction,
    period: Fraction,
) -> tuple[tuple[tuple[Fraction, ...], ...], tuple[Fraction, ...]]:
    midpoint_cell = partitions[0][0]
    relative_cell = partitions[1][1]
    first_periodic_cell = partitions[2][0]
    last_periodic_cell = partitions[2][3]
    if not (
        midpoint_cell[0] < centres[0] - half_width
        and centres[0] + half_width < midpoint_cell[1]
        and relative_cell[0] < centres[1] - half_width
        and centres[1] + half_width < relative_cell[1]
        and centres[2] == 0
        and period == 1
        and partitions[2][0][0] == 0
        and partitions[2][-1][1] == period
        and half_width < first_periodic_cell[1]
        and period - half_width > last_periodic_cell[0]
    ):
        raise PhysicalInitialReplayFailure(
            "frozen tiny geometry does not support the exact structural witness"
        )
    # The first two supports lie wholly in one cell.  On the periodic cut,
    # b(u)=b(-u) splits the shared normalization exactly into two halves.
    marginal_witness = (
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(1, 2), Fraction(0), Fraction(0), Fraction(1, 2)),
    )
    component_witness = tuple(
        m * r * y
        for m in marginal_witness[0]
        for r in marginal_witness[1]
        for y in marginal_witness[2]
    )
    if (
        sum(component_witness, Fraction(0)) != 1
        or tuple(index for index, value in enumerate(component_witness) if value) != (4, 7)
        or component_witness[4] != Fraction(1, 2)
        or component_witness[7] != Fraction(1, 2)
    ):
        raise PhysicalInitialReplayFailure("exact structural witness tensor order drifted")
    return marginal_witness, component_witness


def _image_range(
    lower: Fraction,
    upper: Fraction,
    *,
    centre: Fraction,
    half_width: Fraction,
    period: Fraction,
) -> range:
    first = math.ceil((lower - centre - half_width) / period)
    last = math.floor((upper - centre + half_width) / period)
    return range(first, last + 1)


def _marginal_intervals(
    cells: tuple[tuple[Fraction, Fraction], ...],
    *,
    centre: Fraction,
    half_width: Fraction,
    period: Fraction | None,
    normalization: ReplayInterval,
) -> tuple[ReplayInterval, ...]:
    result = []
    for cell_lower, cell_upper in cells:
        raw_lower = Fraction(0)
        raw_upper = Fraction(0)
        images = (0,)
        if period is not None:
            images = _image_range(
                cell_lower,
                cell_upper,
                centre=centre,
                half_width=half_width,
                period=period,
            )
        for image_index in images:
            image_centre = centre if period is None else centre + image_index * period
            overlap_lower = max(cell_lower, image_centre - half_width)
            overlap_upper = min(cell_upper, image_centre + half_width)
            if overlap_upper <= overlap_lower:
                continue
            raw = _bump_integral_interval(
                (overlap_lower - image_centre) / half_width,
                (overlap_upper - image_centre) / half_width,
            )
            raw_lower += raw.lower
            raw_upper += raw.upper
        result.append(ReplayInterval(raw_lower, raw_upper).divide_positive(normalization))
    lower_mass = sum((entry.lower for entry in result), Fraction(0))
    upper_mass = sum((entry.upper for entry in result), Fraction(0))
    if not lower_mass <= 1 <= upper_mass:
        raise PhysicalInitialReplayFailure("independent marginal replay misses unit mass")
    return tuple(result)


def _overlaps(
    replay: ReplayInterval,
    producer_lower: Fraction,
    producer_upper: Fraction,
) -> bool:
    return max(replay.lower, producer_lower) <= min(replay.upper, producer_upper)


def _contains_exact(lower: Fraction, upper: Fraction, value: Fraction) -> bool:
    return lower <= value <= upper


def _receipt_digest(receipt: IndependentSourceReplayReceipt) -> str:
    return _digest_fields(
        b"physical-initial-independent-replay-receipt-v2\x00",
        receipt.schema,
        receipt.status,
        receipt.algorithm_id,
        REPLAY_PANELS_PER_UNIT,
        REPLAY_PRECISION_BITS,
        receipt.analytic_source_sha256,
        receipt.configuration_id,
        *receipt.logical_shape,
        receipt.component_box_raw_sha256,
        receipt.component_box_manifest_sha256,
        receipt.claimed_certificate_sha256,
        receipt.claimed_bound_target_sha256,
        receipt.axis_geometry_sha256,
        receipt.structural_witness_sha256,
        *receipt.claimed_marginal_endpoint_sha256s,
        *receipt.replay_marginal_endpoint_sha256s,
        receipt.replay_component_endpoint_sha256,
        receipt.producer_marginal_structural_containment_count,
        receipt.producer_component_structural_containment_count,
        receipt.producer_marginal_overlap_count,
        receipt.producer_component_overlap_count,
        receipt.lower_mass_replay.numerator,
        receipt.lower_mass_replay.denominator,
        receipt.upper_mass_replay.numerator,
        receipt.upper_mass_replay.denominator,
        receipt.source_semantics_checked,
        receipt.semantic_source_containment_proved,
        receipt.canonical_box_identity_rederived,
        receipt.rectangle_overlap_used_only_as_consistency,
        receipt.independent_numerical_implementation,
        receipt.producer_quadrature_ledger_consumed,
        receipt.producer_certificate_flags_consumed,
        receipt.exact_partition_reconstructed,
        receipt.periodic_images_reconstructed,
        receipt.analytic_unit_mass_structural_proof_used,
        receipt.same_process,
        receipt.clean_serialized_whole_result_replay,
        receipt.production_resource_gate,
        receipt.f0_pass,
    )


def validate_replay_receipt_structure_only(receipt: IndependentSourceReplayReceipt) -> None:
    """Validate the receipt ledger, not the source/box relation it reports."""

    if type(receipt) is not IndependentSourceReplayReceipt:
        raise PhysicalInitialReplayFailure("independent replay receipt has the wrong type")
    digests = (
        receipt.analytic_source_sha256,
        receipt.component_box_raw_sha256,
        receipt.component_box_manifest_sha256,
        receipt.claimed_certificate_sha256,
        receipt.claimed_bound_target_sha256,
        receipt.axis_geometry_sha256,
        receipt.structural_witness_sha256,
        *receipt.claimed_marginal_endpoint_sha256s,
        *receipt.replay_marginal_endpoint_sha256s,
        receipt.replay_component_endpoint_sha256,
        receipt.receipt_sha256,
    )
    if (
        receipt.schema != REPLAY_SCHEMA
        or receipt.status != REPLAY_STATUS
        or receipt.algorithm_id != REPLAY_ALGORITHM_ID
        or receipt.analytic_source_sha256 != ACCEPTED_ANALYTIC_SOURCE_SHA256
        or receipt.configuration_id != CONFIGURATION_ID
        or receipt.logical_shape != (4, 4, 4)
        or len(receipt.claimed_marginal_endpoint_sha256s) != 3
        or len(receipt.replay_marginal_endpoint_sha256s) != 3
        or any(not _is_sha256(value) for value in digests)
        or receipt.producer_marginal_structural_containment_count != 12
        or receipt.producer_component_structural_containment_count != 64
        or receipt.producer_marginal_overlap_count != 12
        or receipt.producer_component_overlap_count != 64
        or not receipt.lower_mass_replay <= 1 <= receipt.upper_mass_replay
        or receipt.receipt_sha256 != _receipt_digest(receipt)
        or receipt.source_semantics_checked is not True
        or receipt.semantic_source_containment_proved is not True
        or receipt.canonical_box_identity_rederived is not False
        or receipt.rectangle_overlap_used_only_as_consistency is not True
        or receipt.independent_numerical_implementation is not True
        or receipt.producer_quadrature_ledger_consumed is not False
        or receipt.producer_certificate_flags_consumed is not False
        or receipt.exact_partition_reconstructed is not True
        or receipt.periodic_images_reconstructed is not True
        or receipt.analytic_unit_mass_structural_proof_used is not True
        or receipt.same_process is not True
        or receipt.clean_serialized_whole_result_replay is not False
        or receipt.production_resource_gate is not False
        or receipt.f0_pass is not False
    ):
        raise PhysicalInitialReplayFailure("independent replay receipt ledger is invalid")


def replay_tiny_physical_initial_source_to_box(
    source_bytes: bytes,
    claimed: producer.PhysicalInitialDerivation,
    *,
    accepted_source_sha256: str,
    configuration_id: str,
) -> IndependentSourceReplayReceipt:
    """Prove tiny source containment and cross-check all 64 cells numerically."""

    if (
        configuration_id != CONFIGURATION_ID
        or type(claimed) is not producer.PhysicalInitialDerivation
    ):
        raise PhysicalInitialReplayFailure("independent replay configuration or claim is invalid")
    centres, half_width, period = _parse_source_independently(
        source_bytes,
        accepted_source_sha256=accepted_source_sha256,
    )
    packed.validate_canonical_packed_intervals(claimed.component_box)
    manifest = claimed.component_box.manifest
    if (
        manifest.role != target_uniformization.INITIAL_BOX_ROLE
        or manifest.logical_shape != (4, 4, 4)
        or manifest.array_shape != (64, 2)
        or manifest.state_count != 64
        or manifest.nonnegative is not True
        or claimed.bound_target.certificate.component_box_raw_sha256 != manifest.raw_sha256
        or claimed.bound_target.target.component_box_raw_sha256 != manifest.raw_sha256
        or claimed.bound_target.target.logical_shape != manifest.logical_shape
    ):
        raise PhysicalInitialReplayFailure(
            "claimed component manifest is not the tiny physical initial box"
        )
    partitions = _partitions()
    if not (
        partitions[0][0][0] <= centres[0] - half_width
        and centres[0] + half_width <= partitions[0][-1][1]
        and partitions[1][0][0] <= centres[1] - half_width
        and centres[1] + half_width <= partitions[1][-1][1]
    ):
        raise PhysicalInitialReplayFailure("independent replay nonperiodic support escapes")
    marginal_witness, component_witness = _exact_structural_witness(
        partitions,
        centres,
        half_width,
        period,
    )
    if (
        len(claimed.marginals) != 3
        or tuple(profile.coordinate for profile in claimed.marginals)
        != ("midpoint", "relative_parallel", "relative_perpendicular")
        or any(len(profile.intervals) != 4 for profile in claimed.marginals)
    ):
        raise PhysicalInitialReplayFailure("claimed marginal structure is invalid")
    claimed_marginal_digests = tuple(
        _claimed_marginal_sha256(profile.intervals) for profile in claimed.marginals
    )
    if claimed_marginal_digests != tuple(profile.raw_sha256 for profile in claimed.marginals):
        raise PhysicalInitialReplayFailure("claimed marginal endpoint digest is invalid")
    marginal_structural_count = 0
    for witness_values, claimed_profile in zip(marginal_witness, claimed.marginals, strict=True):
        for exact_value, claimed_value in zip(
            witness_values, claimed_profile.intervals, strict=True
        ):
            if not _contains_exact(
                claimed_value.lower_fraction,
                claimed_value.upper_fraction,
                exact_value,
            ):
                raise PhysicalInitialReplayFailure(
                    "claimed marginal excludes the exact structural source mass"
                )
            marginal_structural_count += 1
    producer_components = claimed.component_box.intervals
    component_structural_count = 0
    producer_lower_mass = Fraction(0)
    producer_upper_mass = Fraction(0)
    for index, exact_value in enumerate(component_witness):
        producer_lower = Fraction.from_float(float(producer_components[index, 0]))
        producer_upper = Fraction.from_float(float(producer_components[index, 1]))
        producer_lower_mass += producer_lower
        producer_upper_mass += producer_upper
        if not _contains_exact(producer_lower, producer_upper, exact_value):
            raise PhysicalInitialReplayFailure(
                "claimed component excludes the exact structural source mass"
            )
        component_structural_count += 1
    if not producer_lower_mass <= 1 <= producer_upper_mass:
        raise PhysicalInitialReplayFailure("claimed component box misses exact unit mass")
    normalization = _bump_integral_interval(Fraction(-1), Fraction(1))
    replay_marginals = tuple(
        _marginal_intervals(
            partitions[index],
            centre=centres[index],
            half_width=half_width,
            period=period if index == 2 else None,
            normalization=normalization,
        )
        for index in range(3)
    )

    marginal_overlap_count = 0
    for replay_values, claimed_profile in zip(replay_marginals, claimed.marginals, strict=True):
        for replay_value, claimed_value in zip(
            replay_values, claimed_profile.intervals, strict=True
        ):
            if not _overlaps(
                replay_value,
                claimed_value.lower_fraction,
                claimed_value.upper_fraction,
            ):
                raise PhysicalInitialReplayFailure(
                    "producer marginal misses independent rectangle enclosure"
                )
            marginal_overlap_count += 1

    replay_components = tuple(
        ReplayInterval(
            m.lower * r.lower * y.lower,
            m.upper * r.upper * y.upper,
        )
        for m in replay_marginals[0]
        for r in replay_marginals[1]
        for y in replay_marginals[2]
    )
    if len(replay_components) != producer_components.shape[0]:
        raise PhysicalInitialReplayFailure("independent replay component shape disagrees")
    for index, replay_value in enumerate(replay_components):
        producer_lower = Fraction.from_float(float(producer_components[index, 0]))
        producer_upper = Fraction.from_float(float(producer_components[index, 1]))
        if not _overlaps(
            replay_value,
            producer_lower,
            producer_upper,
        ):
            raise PhysicalInitialReplayFailure(
                "producer component misses independent rectangle enclosure"
            )
    lower_mass = sum((entry.lower for entry in replay_components), Fraction(0))
    upper_mass = sum((entry.upper for entry in replay_components), Fraction(0))
    if not lower_mass <= 1 <= upper_mass:
        raise PhysicalInitialReplayFailure("independent tensor replay misses unit mass")

    axis_digest = _axis_geometry_sha256(partitions)
    witness_digest = _structural_witness_sha256(
        marginal_witness,
        component_witness,
    )
    replay_marginal_digests = tuple(
        _replay_interval_sha256(
            b"physical-initial-independent-replay-marginal-v1\x00" + bytes((index,)),
            intervals,
        )
        for index, intervals in enumerate(replay_marginals)
    )
    replay_component_digest = _replay_interval_sha256(
        b"physical-initial-independent-replay-components-v1\x00",
        replay_components,
    )

    provisional = IndependentSourceReplayReceipt(
        schema=REPLAY_SCHEMA,
        status=REPLAY_STATUS,
        algorithm_id=REPLAY_ALGORITHM_ID,
        analytic_source_sha256=accepted_source_sha256,
        configuration_id=configuration_id,
        logical_shape=(4, 4, 4),
        component_box_raw_sha256=manifest.raw_sha256,
        component_box_manifest_sha256=_manifest_sha256(manifest),
        claimed_certificate_sha256=(claimed.bound_target.certificate.source_certificate_sha256),
        claimed_bound_target_sha256=claimed.bound_target.bound_target_binding_sha256,
        axis_geometry_sha256=axis_digest,
        structural_witness_sha256=witness_digest,
        claimed_marginal_endpoint_sha256s=claimed_marginal_digests,
        replay_marginal_endpoint_sha256s=replay_marginal_digests,
        replay_component_endpoint_sha256=replay_component_digest,
        producer_marginal_structural_containment_count=marginal_structural_count,
        producer_component_structural_containment_count=component_structural_count,
        producer_marginal_overlap_count=marginal_overlap_count,
        producer_component_overlap_count=len(replay_components),
        lower_mass_replay=lower_mass,
        upper_mass_replay=upper_mass,
        receipt_sha256="0" * 64,
        source_semantics_checked=True,
        semantic_source_containment_proved=True,
        canonical_box_identity_rederived=False,
        rectangle_overlap_used_only_as_consistency=True,
        independent_numerical_implementation=True,
        producer_quadrature_ledger_consumed=False,
        producer_certificate_flags_consumed=False,
        exact_partition_reconstructed=True,
        periodic_images_reconstructed=True,
        analytic_unit_mass_structural_proof_used=True,
        same_process=True,
        clean_serialized_whole_result_replay=False,
        production_resource_gate=False,
        f0_pass=False,
    )
    receipt = IndependentSourceReplayReceipt(
        **{
            field: getattr(provisional, field)
            for field in provisional.__dataclass_fields__
            if field != "receipt_sha256"
        },
        receipt_sha256=_receipt_digest(provisional),
    )
    validate_replay_receipt_structure_only(receipt)
    return receipt
