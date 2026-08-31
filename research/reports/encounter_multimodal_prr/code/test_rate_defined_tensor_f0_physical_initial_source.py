from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_target_uniformization as target_uniformization
import rate_defined_tensor_f0_physical_initial_replay as replay
import rate_defined_tensor_f0_physical_initial_source as source
from test_rate_defined_tensor_f0_packed_rate_action import _problem

SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "artifacts"
    / "data"
    / "physical_initial_analytic_source_v1.json"
)


@pytest.fixture(scope="module")
def source_bytes() -> bytes:
    return SOURCE_PATH.read_bytes()


@pytest.fixture(scope="module")
def derivation(source_bytes: bytes) -> source.PhysicalInitialDerivation:
    return source.derive_tiny_physical_initial_target(
        source_bytes,
        accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
        configuration_id=source.CONFIGURATION_ID,
    )


def test_canonical_source_is_control_free_and_exactly_hash_pinned(source_bytes: bytes) -> None:
    assert hashlib.sha256(source_bytes).hexdigest() == source.ACCEPTED_ANALYTIC_SOURCE_SHA256
    assert b"control_no_budget" in source_bytes
    for forbidden in (b"selector_results", b"killing", b"weights", b"budget_exact"):
        assert forbidden not in source_bytes
    parsed = source.parse_analytic_initial_source(
        source_bytes,
        accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
    )
    assert parsed.coordinate_order == (
        "midpoint",
        "relative_parallel",
        "relative_perpendicular",
    )
    assert parsed.centres == (
        Fraction.from_float(float.fromhex("0x1.1eb851eb851ecp-3")),
        Fraction.from_float(float.fromhex("-0x1.6666666666666p-2")),
        Fraction(0),
    )
    assert parsed.half_width == Fraction.from_float(float.fromhex("0x1.47ae147ae147bp-6"))
    assert parsed.analytic_total_mass == 1
    assert parsed.common_normalizer is True
    assert parsed.control_free is True


def test_source_rebuilds_exact_partition_marginals_component_box_and_target(
    derivation: source.PhysicalInitialDerivation,
) -> None:
    certificate = derivation.bound_target.certificate
    assert tuple(axis.name for axis in derivation.axes) == derivation.source.coordinate_order
    assert tuple(len(axis.cells) for axis in derivation.axes) == (4, 4, 4)
    assert tuple(profile.active_indices for profile in derivation.marginals) == (
        (0,),
        (1,),
        (0, 3),
    )
    assert certificate.active_component_count == 2
    assert certificate.logical_shape == (4, 4, 4)
    assert certificate.state_count == 64
    assert certificate.lower_mass_exact <= 1 <= certificate.upper_mass_exact
    assert certificate.lower_anchor_l1_radius_exact == Fraction(6051, 2**53)
    assert certificate.lower_anchor_l1_radius_exact < Fraction(1, 10**12)
    assert derivation.bound_target.target.l1_radius_exact_upper == (
        certificate.lower_anchor_l1_radius_exact
    )
    assert certificate.component_box_raw_sha256 == (
        "8f11fe01f350ccbabb88c325896795c269f02dbf8fa80b8cd9eeec3addd462f7"
    )
    assert certificate.source_certificate_sha256 == (
        "5d9e1e948a027debdfedbe1e06e4ac8aa36516744427598853dc4621b81514de"
    )
    assert certificate.analytic_source_rederived is True
    assert certificate.exact_partition_proved is True
    assert certificate.analytic_initial_unit_mass_proved is True
    assert certificate.analytic_initial_componentwise_contained is True
    assert certificate.control_values_read is False
    assert certificate.positive_budget_scientific_result_read is False
    assert certificate.fresh_process is False
    assert certificate.independent_semantic_replay_complete is False
    assert certificate.production_resource_gate is False
    assert certificate.f0_pass is False
    source.validate_bound_target_structure_only(derivation.bound_target)


def test_deterministic_source_verifier_rederives_exact_bytes(
    source_bytes: bytes,
    derivation: source.PhysicalInitialDerivation,
) -> None:
    verified = source.verify_claimed_tiny_physical_initial_derivation(
        source_bytes,
        derivation,
        accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
        configuration_id=source.CONFIGURATION_ID,
    )
    assert verified == derivation.bound_target.certificate


def test_independent_rectangle_replay_reconstructs_all_cells_without_producer_ledgers(
    source_bytes: bytes,
    derivation: source.PhysicalInitialDerivation,
) -> None:
    receipt = replay.replay_tiny_physical_initial_source_to_box(
        source_bytes,
        derivation,
        accepted_source_sha256=replay.ACCEPTED_ANALYTIC_SOURCE_SHA256,
        configuration_id=replay.CONFIGURATION_ID,
    )
    assert receipt.status == replay.REPLAY_STATUS
    assert receipt.algorithm_id == replay.REPLAY_ALGORITHM_ID
    assert receipt.producer_marginal_structural_containment_count == 12
    assert receipt.producer_component_structural_containment_count == 64
    assert receipt.producer_marginal_overlap_count == 12
    assert receipt.producer_component_overlap_count == 64
    assert receipt.lower_mass_replay <= 1 <= receipt.upper_mass_replay
    assert receipt.structural_witness_sha256 == (
        "352eeaf670564e7d2231fb5210bf04dd52cfd52d657ff1d58610ad9ffbc46f17"
    )
    assert receipt.source_semantics_checked is True
    assert receipt.semantic_source_containment_proved is True
    assert receipt.canonical_box_identity_rederived is False
    assert receipt.rectangle_overlap_used_only_as_consistency is True
    assert receipt.independent_numerical_implementation is True
    assert receipt.producer_quadrature_ledger_consumed is False
    assert receipt.producer_certificate_flags_consumed is False
    assert receipt.exact_partition_reconstructed is True
    assert receipt.periodic_images_reconstructed is True
    assert receipt.same_process is True
    assert receipt.clean_serialized_whole_result_replay is False
    assert receipt.production_resource_gate is False
    assert receipt.f0_pass is False
    replay.validate_replay_receipt_structure_only(receipt)
    with pytest.raises(replay.PhysicalInitialReplayFailure, match="receipt ledger"):
        replay.validate_replay_receipt_structure_only(
            replace(receipt, semantic_source_containment_proved=False)
        )


def test_source_hash_registry_and_configuration_mutations_fail_before_derivation(
    source_bytes: bytes,
) -> None:
    mutated = bytearray(source_bytes)
    mutated[0] ^= 1
    with pytest.raises(source.PhysicalInitialSourceFailure, match="bytes disagree"):
        source.derive_tiny_physical_initial_target(
            bytes(mutated),
            accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=source.CONFIGURATION_ID,
        )
    attacker_digest = hashlib.sha256(bytes(mutated)).hexdigest()
    with pytest.raises(source.PhysicalInitialSourceFailure, match="accepted registry"):
        source.derive_tiny_physical_initial_target(
            bytes(mutated),
            accepted_source_sha256=attacker_digest,
            configuration_id=source.CONFIGURATION_ID,
        )
    with pytest.raises(source.PhysicalInitialSourceFailure, match="configuration"):
        source.derive_tiny_physical_initial_target(
            source_bytes,
            accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id="tiny_physical_domain_periodic_cut_at_source_c5_v1",
        )


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("coordinate_order", ["relative_parallel", "midpoint", "relative_perpendicular"]),
        ("half_width_binary64_hex", "0x1.47ae147ae147cp-6"),
        ("transverse_period_exact", "2/1"),
        ("periodic_wrap", "drop_periodic_images"),
        ("midpoint_start", "0x1.1eb851eb851edp-3"),
    ),
)
def test_semantic_source_mutations_fail_even_under_a_temporarily_rebound_registry(
    monkeypatch: pytest.MonkeyPatch,
    source_bytes: bytes,
    field: str,
    replacement: object,
) -> None:
    payload = json.loads(source_bytes)
    if field == "midpoint_start":
        payload["starts_binary64_hex"]["midpoint"] = replacement
    else:
        payload[field] = replacement
    mutated = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii")
    digest = hashlib.sha256(mutated).hexdigest()
    monkeypatch.setattr(source, "ACCEPTED_ANALYTIC_SOURCE_SHA256", digest)
    with pytest.raises(source.PhysicalInitialSourceFailure, match="semantics"):
        source.parse_analytic_initial_source(mutated, accepted_source_sha256=digest)
    monkeypatch.setattr(replay, "ACCEPTED_ANALYTIC_SOURCE_SHA256", digest)
    with pytest.raises(replay.PhysicalInitialReplayFailure, match="semantics"):
        replay._parse_source_independently(mutated, accepted_source_sha256=digest)


def test_exact_partition_gap_overlap_and_volume_mutations_fail_closed(
    derivation: source.PhysicalInitialDerivation,
) -> None:
    axis = derivation.axes[0]
    first = axis.cells[0][0]
    gap = replace(
        axis,
        cells=(((first[0], first[1] - Fraction(1, 2**20)),), *axis.cells[1:]),
        volumes=(first[1] - first[0] - Fraction(1, 2**20), *axis.volumes[1:]),
    )
    with pytest.raises(source.PhysicalInitialSourceFailure, match="gap or overlap"):
        source._validate_exact_partition(gap)
    wrong_volume = replace(axis, volumes=(axis.volumes[0] + Fraction(1, 2**20), *axis.volumes[1:]))
    with pytest.raises(source.PhysicalInitialSourceFailure, match="volume disagrees"):
        source._validate_exact_partition(wrong_volume)


def _coherent_derivation_for_rows(
    derivation: source.PhysicalInitialDerivation,
    rows: tuple[tuple[float, float], ...],
) -> source.PhysicalInitialDerivation:
    payload = packed.create_packed_interval_payload(
        rows,
        role=target_uniformization.INITIAL_BOX_ROLE,
        logical_shape=(4, 4, 4),
        nonnegative=True,
        block_size=source.BLOCK_SIZE,
        maximum_working_bytes=source.MAXIMUM_WORKING_BYTES,
    )
    alternative_box = packed.load_canonical_packed_intervals(payload)
    alternative_target = target_uniformization.make_initial_target_ball(alternative_box)
    lower_mass = sum((Fraction.from_float(row[0]) for row in rows), Fraction(0))
    upper_mass = sum((Fraction.from_float(row[1]) for row in rows), Fraction(0))
    active_indices = tuple(index for index, row in enumerate(rows) if row[1] > 0.0)
    old = derivation.bound_target.certificate
    provisional = replace(
        old,
        active_index_sha256=source._active_index_sha256(active_indices),
        active_component_count=len(active_indices),
        component_box_raw_sha256=alternative_box.manifest.raw_sha256,
        component_box_manifest_sha256=alternative_target.component_box_manifest_sha256,
        lower_mass_exact=lower_mass,
        upper_mass_exact=upper_mass,
        lower_anchor_l1_radius_exact=Fraction(1) - lower_mass,
        source_certificate_sha256="0" * 64,
    )
    alternative_certificate = replace(
        provisional,
        source_certificate_sha256=source._certificate_digest(provisional),
    )
    source.validate_certificate(alternative_certificate)
    alternative_bound = source._wrap_bound_target(
        alternative_certificate,
        alternative_target,
        current_target_lineage_replayed=True,
    )
    return replace(
        derivation,
        component_box=alternative_box,
        bound_target=alternative_bound,
    )


def _coherent_alternative_derivation(
    derivation: source.PhysicalInitialDerivation,
) -> source.PhysicalInitialDerivation:
    rows = tuple((1.0, 1.0) if index == 0 else (0.0, 0.0) for index in range(64))
    return _coherent_derivation_for_rows(derivation, rows)


def test_fully_coherent_unit_mass_substitute_box_is_rejected_by_source_rederivation(
    source_bytes: bytes,
    derivation: source.PhysicalInitialDerivation,
) -> None:
    alternative = _coherent_alternative_derivation(derivation)
    packed.validate_canonical_packed_intervals(alternative.component_box)
    source.validate_bound_target_structure_only(alternative.bound_target)
    with pytest.raises(source.PhysicalInitialSourceFailure, match="deterministic analytic-source"):
        source.verify_claimed_tiny_physical_initial_derivation(
            source_bytes,
            alternative,
            accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=source.CONFIGURATION_ID,
        )
    with pytest.raises(replay.PhysicalInitialReplayFailure, match="exact structural source mass"):
        replay.replay_tiny_physical_initial_source_to_box(
            source_bytes,
            alternative,
            accepted_source_sha256=replay.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=replay.CONFIGURATION_ID,
        )


def test_independent_semantic_containment_is_distinct_from_canonical_byte_identity(
    source_bytes: bytes,
    derivation: source.PhysicalInitialDerivation,
) -> None:
    broad = _coherent_derivation_for_rows(derivation, ((0.0, 1.0),) * 64)
    receipt = replay.replay_tiny_physical_initial_source_to_box(
        source_bytes,
        broad,
        accepted_source_sha256=replay.ACCEPTED_ANALYTIC_SOURCE_SHA256,
        configuration_id=replay.CONFIGURATION_ID,
    )
    assert receipt.semantic_source_containment_proved is True
    assert receipt.canonical_box_identity_rederived is False
    with pytest.raises(source.PhysicalInitialSourceFailure, match="deterministic analytic-source"):
        source.verify_claimed_tiny_physical_initial_derivation(
            source_bytes,
            broad,
            accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=source.CONFIGURATION_ID,
        )


def test_exact_half_zero_and_tensor_order_exclusion_mutations_fail_semantic_replay(
    source_bytes: bytes,
    derivation: source.PhysicalInitialDerivation,
) -> None:
    narrow_rows = [(0.0, 0.0)] * 64
    narrow_rows[4] = (0.4997, 0.4999)
    narrow_rows[7] = (0.5001, 0.5003)
    wrong_halves = _coherent_derivation_for_rows(derivation, tuple(narrow_rows))
    with pytest.raises(replay.PhysicalInitialReplayFailure, match="exact structural source mass"):
        replay.replay_tiny_physical_initial_source_to_box(
            source_bytes,
            wrong_halves,
            accepted_source_sha256=replay.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=replay.CONFIGURATION_ID,
        )

    positive_zero_rows = [(0.0, 1.0)] * 64
    positive_zero_rows[0] = (1.0e-6, 1.0)
    wrong_zero = _coherent_derivation_for_rows(derivation, tuple(positive_zero_rows))
    with pytest.raises(replay.PhysicalInitialReplayFailure, match="exact structural source mass"):
        replay.replay_tiny_physical_initial_source_to_box(
            source_bytes,
            wrong_zero,
            accepted_source_sha256=replay.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=replay.CONFIGURATION_ID,
        )

    swapped_rows = [(0.0, 0.0)] * 64
    swapped_rows[5] = (0.5, 0.5)
    swapped_rows[6] = (0.5, 0.5)
    wrong_order = _coherent_derivation_for_rows(derivation, tuple(swapped_rows))
    with pytest.raises(replay.PhysicalInitialReplayFailure, match="exact structural source mass"):
        replay.replay_tiny_physical_initial_source_to_box(
            source_bytes,
            wrong_order,
            accepted_source_sha256=replay.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=replay.CONFIGURATION_ID,
        )


def test_repackaged_raw_bytes_with_wrong_role_and_shape_fail_replay_manifest_gate(
    source_bytes: bytes,
    derivation: source.PhysicalInitialDerivation,
) -> None:
    rows = tuple((float(row[0]), float(row[1])) for row in derivation.component_box.intervals)
    payload = packed.create_packed_interval_payload(
        rows,
        role="science_free_unrelated_shape",
        logical_shape=(8, 8),
        nonnegative=True,
        block_size=source.BLOCK_SIZE,
        maximum_working_bytes=source.MAXIMUM_WORKING_BYTES,
    )
    repackaged = replace(
        derivation,
        component_box=packed.load_canonical_packed_intervals(payload),
    )
    with pytest.raises(replay.PhysicalInitialReplayFailure, match="manifest"):
        replay.replay_tiny_physical_initial_source_to_box(
            source_bytes,
            repackaged,
            accepted_source_sha256=replay.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=replay.CONFIGURATION_ID,
        )


def test_certificate_and_bound_target_coherent_field_mutations_fail_closed(
    derivation: source.PhysicalInitialDerivation,
) -> None:
    certificate = derivation.bound_target.certificate
    with pytest.raises(source.PhysicalInitialSourceFailure, match="certificate ledger"):
        source.validate_certificate(replace(certificate, analytic_source_rederived=False))
    with pytest.raises(source.PhysicalInitialSourceFailure, match="certificate ledger"):
        source.validate_certificate(replace(certificate, source_certificate_sha256="0" * 64))
    with pytest.raises(source.PhysicalInitialSourceFailure, match="bound-target ledger"):
        source.validate_bound_target_structure_only(
            replace(
                derivation.bound_target,
                canonical_initial_source_bound=False,
                bound_target_binding_sha256="0" * 64,
            )
        )


def test_two_uniformization_chunks_preserve_analytic_source_certificate(
    source_bytes: bytes,
    derivation: source.PhysicalInitialDerivation,
) -> None:
    _, kernel, contract = _problem(
        (4, 4, 4),
        periodic=(False, False, True),
        block_size=16,
    )
    forged_values = np.zeros(64, dtype=np.float64)
    forged_values[0] = 1.0
    forged_values.setflags(write=False)
    forged_target_provisional = replace(
        derivation.bound_target.target,
        nominal=forged_values,
        nominal_raw_sha256=hashlib.sha256(memoryview(forged_values).cast("B")).hexdigest(),
        l1_radius_exact_upper=Fraction(0),
        l1_radius_upper=0.0,
        l1_radius_upper_hex=(0.0).hex(),
        binding_sha256="0" * 64,
    )
    forged_target = replace(
        forged_target_provisional,
        binding_sha256=target_uniformization._target_binding(forged_target_provisional),
    )
    forged_bound = source._wrap_bound_target(
        derivation.bound_target.certificate,
        forged_target,
        current_target_lineage_replayed=True,
    )
    source.validate_bound_target_structure_only(forged_bound)
    with pytest.raises(source.PhysicalInitialSourceFailure, match="canonical rederived source"):
        source.propagate_bound_target(
            kernel,
            forged_bound,
            contract,
            source_bytes=source_bytes,
            initial_derivation=derivation,
            accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=source.CONFIGURATION_ID,
            time=Fraction(1, 64),
            tail_tolerance=Fraction(1, 2**36),
        )
    substitute = _coherent_alternative_derivation(derivation)
    with pytest.raises(source.PhysicalInitialSourceFailure, match="not attached"):
        source.propagate_bound_target(
            kernel,
            substitute.bound_target,
            contract,
            source_bytes=source_bytes,
            initial_derivation=derivation,
            accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
            configuration_id=source.CONFIGURATION_ID,
            time=Fraction(1, 64),
            tail_tolerance=Fraction(1, 2**36),
        )
    first_result, first = source.propagate_bound_target(
        kernel,
        derivation.bound_target,
        contract,
        source_bytes=source_bytes,
        initial_derivation=derivation,
        accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
        configuration_id=source.CONFIGURATION_ID,
        time=Fraction(1, 64),
        tail_tolerance=Fraction(1, 2**36),
    )
    second_result, second = source.propagate_bound_target(
        kernel,
        first,
        contract,
        source_bytes=source_bytes,
        initial_derivation=derivation,
        accepted_source_sha256=source.ACCEPTED_ANALYTIC_SOURCE_SHA256,
        configuration_id=source.CONFIGURATION_ID,
        time=Fraction(1, 64),
        tail_tolerance=Fraction(1, 2**36),
    )
    assert first.certificate == derivation.bound_target.certificate
    assert second.certificate == derivation.bound_target.certificate
    assert first_result.target.binding_sha256 == first.current_target_binding_sha256
    assert first.current_target_lineage_replayed is False
    assert second_result.target.binding_sha256 == second.current_target_binding_sha256
    assert second.target.cumulative_time == Fraction(1, 32)
    assert second.target.cumulative_chunk_count == 2
    assert second.canonical_initial_source_bound is True
    assert second.analytic_source_certificate_retained is True
    assert second.independent_replay_receipt_retained is False
    assert second.result_self_contained_source_provenance is False
    assert second.current_target_lineage_replayed is False
    assert second.operator_axis_geometry_bound is False
    assert second.fresh_process is False
    assert second.independent_semantic_replay_complete is False
    assert second.production_resource_gate is False
    assert second.f0_pass is False
    assert not hasattr(second_result, "analytic_source_sha256")
    source.validate_bound_target_structure_only(second)
