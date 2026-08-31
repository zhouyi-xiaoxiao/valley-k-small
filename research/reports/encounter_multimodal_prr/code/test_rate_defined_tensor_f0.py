from __future__ import annotations

import hashlib
import json
import math
from dataclasses import replace
from fractions import Fraction
from itertools import product

import numpy as np
import pytest
import rate_defined_tensor_f0 as f0
import verified_uniformization_enclosure as reference
from scipy.linalg import expm


def synthetic_selector_bytes(weights: tuple[Fraction, ...]) -> bytes:
    payload = {
        "schema_version": 1,
        "stage": "method_only_b0_exact_rational_modal_selector",
        "status": "HOLD_METHOD_ONLY_NOT_A_CONTINUUM_OR_F0_CONTROL_CERTIFICATE",
        "selector_results": {
            "neutral": {
                "status": "PASS_EXACT_RATIONALIZED_SELECTOR",
                "selected": {
                    "weights": [
                        {
                            "exact": f"{value.numerator}/{value.denominator}",
                            "numerator": str(value.numerator),
                            "denominator": str(value.denominator),
                        }
                        for value in weights
                    ]
                },
            }
        },
        # Comparison-only historical fields may exist, but the parser has no
        # path from them to a v2 production control.
        "f0_control_compatibility": {"neutral": {"f0_raw_weight_hex": ["0x1p-2"]}},
    }
    return (json.dumps(payload, allow_nan=False, sort_keys=True) + "\n").encode()


def neutral_control(
    weights: tuple[Fraction, ...] = (Fraction(1, 2), Fraction(1, 2)),
) -> f0.RationalControl:
    payload = synthetic_selector_bytes(weights)
    return f0.parse_selector_rational_control(
        payload,
        expected_sha256=hashlib.sha256(payload).hexdigest(),
        control_id="neutral",
        source_kind=f0.SELECTOR_SOURCE_KIND,
    )


def reflecting_axis(*, potential: bool = False) -> f0.TensorAxis:
    energies = (Fraction(0), Fraction(1, 10), Fraction(1, 5)) if potential else (Fraction(0),) * 3
    return f0.build_reflecting_sg_axis(
        "reflecting",
        (Fraction(0), Fraction(1, 2), Fraction(1)),
        energies,
        Fraction(1, 100),
    )


def periodic_axis(*, shifted: bool = False, cells: int = 4) -> f0.TensorAxis:
    return f0.build_periodic_diffusion_axis(
        "periodic",
        cells,
        Fraction(1),
        Fraction(1, 200),
        half_cell_shift=shifted,
    )


def small_kernel(*, dimensions: int = 2) -> f0.RateDefinedTensorKernel:
    axes: tuple[f0.TensorAxis, ...]
    if dimensions == 1:
        axes = (reflecting_axis(),)
    elif dimensions == 2:
        axes = (reflecting_axis(potential=True), periodic_axis(shifted=True))
    elif dimensions == 3:
        axes = (
            reflecting_axis(potential=True),
            periodic_axis(shifted=False),
            periodic_axis(shifted=True),
        )
    else:
        raise AssertionError("unsupported fixture dimension")
    killing = (f0.OutwardInterval.from_fraction(Fraction(1, 100)),) * np.prod(
        [axis.size for axis in axes]
    )
    return f0.build_rate_defined_tensor_kernel(axes, killing)


def initial_for(kernel: f0.RateDefinedTensorKernel) -> f0.InitialStateEnclosure:
    intervals = (f0.OutwardInterval.from_fraction(Fraction(1, kernel.states)),) * kernel.states
    source = b"science-free-uniform-initial-law-v1"
    return f0.enclose_initial_state(
        intervals,
        source_payload_bytes=source,
        expected_source_sha256=hashlib.sha256(source).hexdigest(),
    )


def test_selector_rational_ingestion_is_exact_and_raw_sc_is_rejected() -> None:
    payload = synthetic_selector_bytes((Fraction(1, 4),) * 4)
    digest = hashlib.sha256(payload).hexdigest()
    control = f0.parse_selector_rational_control(
        payload,
        expected_sha256=digest,
        control_id="neutral",
        source_kind=f0.SELECTOR_SOURCE_KIND,
    )
    assert control.weights == (Fraction(1, 4),) * 4
    assert all(
        interval.contains_fraction(weight)
        for interval, weight in zip(control.weight_intervals, control.weights, strict=True)
    )

    with pytest.raises(f0.F0VerificationFailure) as raw_error:
        f0.parse_selector_rational_control(
            payload,
            expected_sha256=digest,
            control_id="neutral",
            source_kind="raw_S_c",
        )
    assert raw_error.value.code == f0.HOLD_CONTROL_SOURCE

    with pytest.raises(f0.F0VerificationFailure) as hash_error:
        f0.parse_selector_rational_control(
            payload,
            expected_sha256="f" * 64,
            control_id="neutral",
            source_kind=f0.SELECTOR_SOURCE_KIND,
        )
    assert hash_error.value.code == f0.HOLD_CONTROL_PARSE


def test_selector_rejects_nonunit_or_inconsistent_rational_fields() -> None:
    nonunit = synthetic_selector_bytes((Fraction(1, 3), Fraction(1, 3)))
    with pytest.raises(f0.F0VerificationFailure) as error:
        f0.parse_selector_rational_control(
            nonunit,
            expected_sha256=hashlib.sha256(nonunit).hexdigest(),
            control_id="neutral",
            source_kind=f0.SELECTOR_SOURCE_KIND,
        )
    assert error.value.code == f0.HOLD_CONTROL_PARSE

    payload = json.loads(synthetic_selector_bytes((Fraction(1, 2), Fraction(1, 2))))
    payload["selector_results"]["neutral"]["selected"]["weights"][0]["exact"] = "1/3"
    malformed = (json.dumps(payload, allow_nan=False, sort_keys=True) + "\n").encode()
    with pytest.raises(f0.F0VerificationFailure) as mismatch:
        f0.parse_selector_rational_control(
            malformed,
            expected_sha256=hashlib.sha256(malformed).hexdigest(),
            control_id="neutral",
            source_kind=f0.SELECTOR_SOURCE_KIND,
        )
    assert mismatch.value.code == f0.HOLD_CONTROL_PARSE

    boundary_payload = json.loads(synthetic_selector_bytes((Fraction(1, 2), Fraction(1, 2))))
    boundary_payload["stage"] = "positive_budget_result"
    wrong_stage = (json.dumps(boundary_payload, allow_nan=False, sort_keys=True) + "\n").encode()
    with pytest.raises(f0.F0VerificationFailure) as boundary:
        f0.parse_selector_rational_control(
            wrong_stage,
            expected_sha256=hashlib.sha256(wrong_stage).hexdigest(),
            control_id="neutral",
            source_kind=f0.SELECTOR_SOURCE_KIND,
        )
    assert boundary.value.code == f0.HOLD_CONTROL_PARSE


def test_reflecting_sg_half_volumes_and_detailed_balance() -> None:
    axis = reflecting_axis()
    assert axis.cell_volumes == (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))
    assert axis.has_half_boundary_volumes
    assert axis.forward_rates[-1].upper == 0.0
    assert axis.backward_rates[0].upper == 0.0
    f0.verify_axis_detailed_balance(axis)

    # At zero potential, boundary-to-interior rates are doubled exactly by
    # the half cell volume, while conductances remain equal in both directions.
    assert axis.forward_rates[0].contains_fraction(Fraction(2, 25))
    assert axis.backward_rates[1].contains_fraction(Fraction(1, 25))
    left_conductance = axis.stationary_masses[0].multiply_nonnegative(axis.forward_rates[0])
    right_conductance = axis.stationary_masses[1].multiply_nonnegative(axis.backward_rates[1])
    assert left_conductance.contains_fraction(Fraction(1, 50))
    assert right_conductance.contains_fraction(Fraction(1, 50))


def test_periodic_half_shift_recomputes_exact_cell_overlaps() -> None:
    base = periodic_axis(shifted=False)
    shifted = periodic_axis(shifted=True)
    assert base.periodic_shift == 0
    assert shifted.periodic_shift == Fraction(1, 8)
    assert len(set(base.positions)) == base.size
    assert len(set(shifted.positions)) == shifted.size

    base_overlap = f0.cell_overlap_fractions(base, Fraction(0), Fraction(1, 4))
    shifted_overlap = f0.cell_overlap_fractions(shifted, Fraction(0), Fraction(1, 4))
    assert base_overlap != shifted_overlap
    assert sum(
        (
            fraction * volume
            for fraction, volume in zip(base_overlap, base.cell_volumes, strict=True)
        ),
        Fraction(0),
    ) == Fraction(1, 4)
    assert sum(
        (
            fraction * volume
            for fraction, volume in zip(shifted_overlap, shifted.cell_volumes, strict=True)
        ),
        Fraction(0),
    ) == Fraction(1, 4)


def test_all_twelve_v2_physical_axis_constructors_and_workload_identity() -> None:
    rows = f0.build_all_physical_axes_v2()
    assert tuple(spec.label for spec, _axes in rows) == f0.PHYSICAL_CONFIGURATION_ORDER_V2
    assert len(rows) == 12
    assert sum(spec.expected_states for spec, _axes in rows) == 34_787_462
    for spec, axes in rows:
        assert tuple(axis.size for axis in axes) == (
            spec.midpoint_size,
            spec.relative_size,
            spec.transverse_size,
        )
        assert math.prod(axis.size for axis in axes) == spec.expected_states
        assert axes[0].has_half_boundary_volumes == spec.midpoint_vertex_centred
        assert axes[1].has_half_boundary_volumes == spec.relative_vertex_centred
        expected_shift = (
            Fraction(1, 2 * spec.transverse_size) if spec.transverse_half_shift else Fraction(0)
        )
        assert axes[2].periodic_shift == expected_shift
        for axis in axes:
            f0.verify_axis_detailed_balance(axis)


def test_v2_control_blind_geometry_has_rigorous_profiles_contact_and_budget() -> None:
    spec = f0.physical_configuration_specs_v2()[1]
    geometry = f0.build_physical_geometry_v2(spec, panels_per_unit=512)
    geometry.validate()
    assert geometry.spec.label == "E128/Base"
    assert geometry.installed_budget_exact == f0.PhysicalParametersV2().budget
    assert geometry.installed_budget_relative_radius == 0
    assert not geometry.prospective_control_values_read
    assert not geometry.positive_budget_primary_control_evaluated
    for profile in (*geometry.support_profiles, *geometry.initial_profiles):
        lower = sum(entry.lower_fraction for entry in profile.mass_intervals)
        upper = sum(entry.upper_fraction for entry in profile.mass_intervals)
        assert lower <= 1 <= upper
        assert profile.analytic_total_mass == 1

    relative, transverse = geometry.axes[1:]
    area_lower = sum(
        entry.lower_fraction
        * relative.cell_volumes[index // transverse.size]
        * transverse.cell_volumes[index % transverse.size]
        for index, entry in enumerate(geometry.contact_fractions_relative)
    )
    area_upper = sum(
        entry.upper_fraction
        * relative.cell_volumes[index // transverse.size]
        * transverse.cell_volumes[index % transverse.size]
        for index, entry in enumerate(geometry.contact_fractions_relative)
    )
    disk_area_oracle = math.pi * float(geometry.parameters.contact_radius) ** 2
    assert float(area_lower) <= disk_area_oracle <= float(area_upper)


def test_directed_disk_rectangle_formula_and_contact_axis_mutation() -> None:
    radius = Fraction(1, 4)
    quadrant = f0.disk_rectangle_area_interval(0, radius, 0, radius, radius)
    assert quadrant.lower <= math.pi / 64 <= quadrant.upper
    assert quadrant.upper - quadrant.lower <= 2.0e-17

    periodic = f0.build_periodic_diffusion_axis(
        "wrong_parallel",
        8,
        Fraction(2),
        Fraction(1, 10),
    )
    transverse = f0.build_periodic_diffusion_axis(
        "transverse",
        8,
        Fraction(1),
        Fraction(1, 10),
        domain_start=Fraction(-1, 2),
    )
    with pytest.raises(f0.F0VerificationFailure) as error:
        f0.build_contact_fraction_intervals_v2(periodic, transverse, radius=radius)
    assert error.value.code == f0.HOLD_INTERVAL_INVALID


def test_doi_killing_uses_control_support_and_contact_intervals() -> None:
    axes = (reflecting_axis(), periodic_axis(shifted=True))
    control = neutral_control()
    # Each density is identically one on a unit-width midpoint domain.
    supports = tuple((f0.OutwardInterval.from_fraction(1),) * axes[0].size for _ in control.weights)
    contact = (f0.OutwardInterval.from_fraction(Fraction(1, 2)),) * (axes[0].size * axes[1].size)
    killing = f0.build_doi_killing_intervals(
        axes,
        midpoint_axis=0,
        control=control,
        budget=Fraction(1, 10),
        support_density_intervals=supports,
        contact_fractions=contact,
    )
    assert len(killing) == axes[0].size * axes[1].size
    assert all(interval.contains_fraction(Fraction(1, 20)) for interval in killing)

    bad_supports = (
        (f0.OutwardInterval.from_fraction(Fraction(1, 2)),) * axes[0].size,
        supports[1],
    )
    with pytest.raises(f0.F0VerificationFailure) as error:
        f0.build_doi_killing_intervals(
            axes,
            midpoint_axis=0,
            control=control,
            budget=Fraction(1, 10),
            support_density_intervals=bad_supports,
            contact_fractions=contact,
        )
    assert error.value.code == f0.HOLD_SUPPORT_NORMALIZATION


def test_initial_state_mass_enclosure_and_failure() -> None:
    intervals = (f0.OutwardInterval.from_fraction(Fraction(1, 12)),) * 12
    source = b"science-free-twelve-state-initial-law-v1"
    digest = hashlib.sha256(source).hexdigest()
    initial = f0.enclose_initial_state(
        intervals,
        source_payload_bytes=source,
        expected_source_sha256=digest,
    )
    assert initial.mass_lower <= 1.0 <= initial.mass_upper
    assert initial.exact_mass_cap == 1
    assert initial.l1_error <= 1.0e-12
    assert abs(float(np.sum(initial.nominal)) - 1.0) <= initial.l1_error + 2.0e-16

    bad = (f0.OutwardInterval.from_fraction(Fraction(1, 24)),) * 12
    with pytest.raises(f0.F0VerificationFailure) as error:
        f0.enclose_initial_state(
            bad,
            source_payload_bytes=source,
            expected_source_sha256=digest,
        )
    assert error.value.code == f0.HOLD_INITIAL_MASS
    with pytest.raises(f0.F0VerificationFailure) as hash_error:
        f0.enclose_initial_state(
            intervals,
            source_payload_bytes=source,
            expected_source_sha256="f" * 64,
        )
    assert hash_error.value.code == f0.HOLD_INITIAL_MASS


def test_stored_diagonal_and_negative_rate_mutations_fail_closed() -> None:
    axis = reflecting_axis()
    killing = (f0.OutwardInterval.from_fraction(Fraction(1, 100)),) * axis.size
    with pytest.raises(f0.F0VerificationFailure) as diagonal_error:
        f0.build_rate_defined_tensor_kernel(
            (axis,),
            killing,
            stored_diagonal=[0.0] * axis.size,
        )
    assert diagonal_error.value.code == f0.HOLD_STORED_DIAGONAL

    rates = list(axis.forward_rates)
    rates[0] = f0.OutwardInterval(-0.01, 0.02)
    corrupted_axis = replace(axis, forward_rates=tuple(rates))
    with pytest.raises(f0.F0VerificationFailure) as sign_error:
        f0.build_rate_defined_tensor_kernel((corrupted_axis,), killing)
    assert sign_error.value.code == f0.HOLD_NEGATIVE_RATE


def test_kernel_derives_submarkov_rows_delta_ledgers_and_degree_contract() -> None:
    kernel = small_kernel(dimensions=3)
    assert kernel.maximum_incoming_terms == 7
    assert kernel.maximum_floating_ops_per_output == 13
    assert kernel.roundoff_gamma_index == 14
    assert kernel.delta_q > 0.0
    assert kernel.delta_p > 0.0
    assert kernel.delta_p_exact <= kernel.delta_p_direct_exact
    assert kernel.delta_p_exact <= kernel.delta_p_via_q_exact
    assert kernel.maximum_center_row_sum <= 1.0
    f0.validate_rate_defined_tensor_kernel(kernel)

    q = f0.explicit_q_csr(kernel)
    p = f0.explicit_p_csr(kernel)
    q_off = q - q.diagonal()[:, None]
    assert np.min(q_off.data, initial=0.0) >= 0.0
    assert np.max(np.asarray(q.sum(axis=1)).reshape(-1)) <= 0.0
    assert np.min(p.data, initial=0.0) >= 0.0
    assert np.max(np.asarray(p.sum(axis=1)).reshape(-1)) <= 1.0


def test_delta_q_and_delta_p_cover_every_small_row_interval_corner() -> None:
    kernel = small_kernel(dimensions=1)
    qhat = f0.explicit_q_csr(kernel).toarray()
    phat = f0.explicit_p_csr(kernel).toarray()
    axis = kernel.axes[0]
    for row in range(kernel.states):
        transitions: list[tuple[int, f0.OutwardInterval]] = []
        if axis.forward_rates[row].upper > 0.0:
            transitions.append((row + 1, axis.forward_rates[row]))
        if axis.backward_rates[row].upper > 0.0:
            transitions.append((row - 1, axis.backward_rates[row]))
        intervals = [interval for _, interval in transitions] + [kernel.killing_intervals[row]]
        endpoints = [(interval.lower_fraction, interval.upper_fraction) for interval in intervals]
        for corner in product(*endpoints):
            target_q = np.zeros(kernel.states, dtype=float)
            outgoing = Fraction(0)
            for (column, _), exact_rate in zip(transitions, corner[:-1], strict=True):
                target_q[column] += float(exact_rate)
                outgoing += exact_rate
            target_q[row] = -float(outgoing + corner[-1])
            target_p = target_q / kernel.rate
            target_p[row] += 1.0
            q_distance = float(np.sum(np.abs(target_q - qhat[row])))
            p_distance = float(np.sum(np.abs(target_p - phat[row])))
            assert q_distance <= kernel.delta_q
            assert p_distance <= kernel.delta_p


def test_matrix_free_action_matches_explicit_csr_oracle_within_roundoff() -> None:
    kernel = small_kernel(dimensions=3)
    rng = np.random.default_rng(20260714)
    state = rng.uniform(0.0, 1.0, size=kernel.states)
    state /= np.sum(state)
    first = f0.matrix_free_p_transpose(kernel, state)
    second = f0.matrix_free_p_transpose(kernel, state)
    explicit = np.asarray(f0.explicit_p_csr(kernel).transpose() @ state).reshape(-1)
    assert np.array_equal(first, second)
    distance = float(np.sum(np.abs(first - explicit)))
    assert distance <= 2.0 * f0.matrix_free_action_roundoff_bound(kernel, state)
    assert np.min(first) >= 0.0

    signed = rng.normal(size=kernel.states)
    matrix_free_q = f0.matrix_free_q_transpose(kernel, signed)
    explicit_q = np.asarray(f0.explicit_q_csr(kernel).transpose() @ signed).reshape(-1)
    q_distance = float(np.sum(np.abs(matrix_free_q - explicit_q)))
    assert q_distance <= 2.0 * f0.matrix_free_q_action_roundoff_bound(kernel, signed)


def test_matrix_free_uniformization_contains_small_dense_target() -> None:
    axis = reflecting_axis()
    killing_value = Fraction(1, 10)
    killing = (f0.OutwardInterval.from_fraction(killing_value),) * axis.size
    kernel = f0.build_rate_defined_tensor_kernel((axis,), killing)
    initial = f0.enclose_initial_state(
        (
            f0.OutwardInterval.from_fraction(1),
            f0.OutwardInterval.from_fraction(0),
            f0.OutwardInterval.from_fraction(0),
        ),
        source_payload_bytes=b"science-free-delta-initial-law-v1",
        expected_source_sha256=hashlib.sha256(b"science-free-delta-initial-law-v1").hexdigest(),
    )
    target_time = Fraction(7, 5)
    enclosed = f0.propagate_matrix_free_absolute(
        kernel,
        initial,
        target_time,
        mean_cap=Fraction(1, 4),
        total_tail_tolerance=Fraction(1, 10**18),
    )

    # Exact zero-potential SG rates for the half-volume three-cell grid.
    target = np.asarray(
        [
            [-(0.08 + 0.1), 0.08, 0.0],
            [0.04, -(0.04 + 0.04 + 0.1), 0.04],
            [0.0, 0.08, -(0.08 + 0.1)],
        ]
    )
    reference_state = expm(float(target_time) * target.T) @ np.asarray([1.0, 0.0, 0.0])
    assert np.sum(np.abs(enclosed.nominal - reference_state)) <= enclosed.l1_error + 2.0e-14
    assert enclosed.elapsed_time == target_time
    assert enclosed.target_time == target_time
    f0.audit_matrix_free_propagation(
        kernel,
        initial,
        enclosed,
        expected_target_time=target_time,
        expected_mean_cap=Fraction(1, 4),
        expected_total_tail_tolerance=Fraction(1, 10**18),
        expected_precision_bits=192,
        expected_maximum_terms=200_000,
        expected_maximum_chunks=100_000,
    )

    jets = f0.enclose_matrix_free_jets(
        kernel,
        initial,
        enclosed,
        expected_target_time=target_time,
        expected_mean_cap=Fraction(1, 4),
        expected_total_tail_tolerance=Fraction(1, 10**18),
        expected_precision_bits=192,
        expected_maximum_terms=200_000,
        expected_maximum_chunks=100_000,
        maximum_order=4,
    )
    exact_action = reference_state.copy()
    exact_killing = np.full(axis.size, float(killing_value))
    for order, row in enumerate(jets):
        exact_scalar = float(exact_killing @ exact_action)
        assert row.order == order
        assert np.sum(np.abs(row.nominal_action - exact_action)) <= row.action_l1_error + 3.0e-13
        assert row.scalar_lower <= exact_scalar <= row.scalar_upper
        assert row.m_upper >= float(np.max(exact_killing) * np.sum(np.abs(exact_action)))
        exact_action = target.T @ exact_action


def test_row_delta_rate_mutations_fail_closed() -> None:
    kernel = small_kernel()
    altered_self = kernel.p_self_center.copy()
    altered_self[0] = 1.1
    with pytest.raises(f0.F0VerificationFailure) as row_error:
        f0.validate_rate_defined_tensor_kernel(replace(kernel, p_self_center=altered_self))
    assert row_error.value.code == f0.HOLD_ROW_STRUCTURE

    with pytest.raises(f0.F0VerificationFailure) as delta_error:
        f0.validate_rate_defined_tensor_kernel(replace(kernel, delta_q=0.0))
    assert delta_error.value.code == f0.HOLD_DELTA_LEDGER

    with pytest.raises(f0.F0VerificationFailure) as delta_p_error:
        f0.validate_rate_defined_tensor_kernel(replace(kernel, delta_p=0.0))
    assert delta_p_error.value.code == f0.HOLD_DELTA_LEDGER

    killing = (f0.OutwardInterval.from_fraction(Fraction(1, 100)),) * kernel.states
    with pytest.raises(f0.F0VerificationFailure) as rate_error:
        f0.build_rate_defined_tensor_kernel(
            kernel.axes,
            killing,
            uniformization_rate=Fraction(1, 1000),
        )
    assert rate_error.value.code == f0.HOLD_RATE_TOO_LOW


def test_tail_time_and_rounding_mutations_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    kernel = small_kernel(dimensions=1)
    initial = initial_for(kernel)
    propagation = f0.propagate_matrix_free_absolute(
        kernel,
        initial,
        Fraction(3, 2),
        mean_cap=Fraction(1, 5),
        total_tail_tolerance=Fraction(1, 10**15),
    )
    chunks = list(propagation.chunks)
    chunks[0] = replace(chunks[0], poisson_tail_upper=1.0)
    with pytest.raises(f0.F0VerificationFailure) as tail_error:
        f0.audit_matrix_free_propagation(
            kernel,
            initial,
            replace(propagation, chunks=tuple(chunks)),
            expected_target_time=Fraction(3, 2),
            expected_mean_cap=Fraction(1, 5),
            expected_total_tail_tolerance=Fraction(1, 10**15),
            expected_precision_bits=192,
            expected_maximum_terms=200_000,
            expected_maximum_chunks=100_000,
        )
    assert tail_error.value.code == f0.HOLD_TAIL

    with pytest.raises(f0.F0VerificationFailure) as time_error:
        f0.audit_matrix_free_propagation(
            kernel,
            initial,
            replace(propagation, elapsed_time=propagation.elapsed_time + 1),
            expected_target_time=Fraction(3, 2),
            expected_mean_cap=Fraction(1, 5),
            expected_total_tail_tolerance=Fraction(1, 10**15),
            expected_precision_bits=192,
            expected_maximum_terms=200_000,
            expected_maximum_chunks=100_000,
        )
    assert time_error.value.code == f0.HOLD_TIME

    with pytest.raises(f0.F0VerificationFailure) as field_error:
        f0.audit_matrix_free_propagation(
            kernel,
            initial,
            replace(propagation, runtime_rounding_mode="FE_UPWARD"),
            expected_target_time=Fraction(3, 2),
            expected_mean_cap=Fraction(1, 5),
            expected_total_tail_tolerance=Fraction(1, 10**15),
            expected_precision_bits=192,
            expected_maximum_terms=200_000,
            expected_maximum_chunks=100_000,
        )
    assert field_error.value.code == f0.HOLD_ROUNDING

    def corrupted_runtime() -> None:
        raise reference.VerificationFailure("runtime rounding mode is not round-to-nearest")

    monkeypatch.setattr(reference, "verify_binary64_runtime", corrupted_runtime)
    with pytest.raises(f0.F0VerificationFailure) as runtime_error:
        f0.validate_rate_defined_tensor_kernel(kernel)
    assert runtime_error.value.code == f0.HOLD_ROUNDING


def test_zero_time_and_multichunk_saved_propagations_replay_exactly() -> None:
    kernel = small_kernel(dimensions=1)
    initial = initial_for(kernel)
    zero = f0.propagate_matrix_free_absolute(
        kernel,
        initial,
        Fraction(0),
        mean_cap=Fraction(1, 100),
        total_tail_tolerance=Fraction(1, 10**12),
    )
    assert zero.chunk_count == 1
    assert zero.elapsed_time == 0
    f0.audit_matrix_free_propagation(
        kernel,
        initial,
        zero,
        expected_target_time=Fraction(0),
        expected_mean_cap=Fraction(1, 100),
        expected_total_tail_tolerance=Fraction(1, 10**12),
        expected_precision_bits=192,
        expected_maximum_terms=200_000,
        expected_maximum_chunks=100_000,
    )

    multiple = f0.propagate_matrix_free_absolute(
        kernel,
        initial,
        Fraction(3, 2),
        mean_cap=Fraction(1, 100),
        total_tail_tolerance=Fraction(1, 10**12),
    )
    assert multiple.chunk_count > 1
    assert len(multiple.chunks) == multiple.chunk_count
    f0.audit_matrix_free_propagation(
        kernel,
        initial,
        multiple,
        expected_target_time=Fraction(3, 2),
        expected_mean_cap=Fraction(1, 100),
        expected_total_tail_tolerance=Fraction(1, 10**12),
        expected_precision_bits=192,
        expected_maximum_terms=200_000,
        expected_maximum_chunks=100_000,
    )


def test_every_saved_propagation_contract_and_chunk_field_is_replayed() -> None:
    kernel = small_kernel(dimensions=1)
    initial = initial_for(kernel)
    propagation = f0.propagate_matrix_free_absolute(
        kernel,
        initial,
        Fraction(3, 2),
        mean_cap=Fraction(1, 100),
        total_tail_tolerance=Fraction(1, 10**12),
    )
    assert propagation.chunk_count > 1

    def must_reject(candidate: f0.MatrixFreePropagation) -> None:
        with pytest.raises(f0.F0VerificationFailure):
            f0.audit_matrix_free_propagation(
                kernel,
                initial,
                candidate,
                expected_target_time=Fraction(3, 2),
                expected_mean_cap=Fraction(1, 100),
                expected_total_tail_tolerance=Fraction(1, 10**12),
                expected_precision_bits=192,
                expected_maximum_terms=200_000,
                expected_maximum_chunks=100_000,
            )

    changed_nominal = propagation.nominal.copy()
    changed_nominal[0] = np.nextafter(changed_nominal[0], math.inf)
    top_level_mutations = (
        replace(propagation, exact_mass_cap=1),
        replace(propagation, target_time=propagation.target_time + 1),
        replace(propagation, elapsed_time=propagation.elapsed_time + 1),
        replace(propagation, mean_cap=propagation.mean_cap * 2),
        replace(
            propagation,
            total_tail_tolerance=propagation.total_tail_tolerance * 2,
        ),
        replace(propagation, precision_bits=193),
        replace(propagation, maximum_terms=199_999),
        replace(propagation, maximum_chunks=99_999),
        replace(propagation, chunk_count=propagation.chunk_count + 1),
        replace(propagation, chunks=propagation.chunks[:-1]),
        replace(propagation, chunks=list(propagation.chunks)),
        replace(propagation, initial_source_sha256="0" * 64),
        replace(
            propagation,
            initial_l1_error=np.nextafter(propagation.initial_l1_error, math.inf),
        ),
        replace(propagation, kernel_construction="forged"),
        replace(propagation, rate_fraction=propagation.rate_fraction + 1),
        replace(propagation, runtime_rounding_mode="FE_UPWARD"),
        replace(propagation, nominal=changed_nominal),
        replace(propagation, nominal=propagation.nominal.astype(np.float32)),
        replace(
            propagation,
            l1_error=np.nextafter(propagation.l1_error, math.inf),
        ),
    )
    for candidate in top_level_mutations:
        must_reject(candidate)

    chunk = propagation.chunks[0]

    def with_first_chunk(mutated: f0.MatrixFreeChunkLedger) -> f0.MatrixFreePropagation:
        return replace(propagation, chunks=(mutated,) + propagation.chunks[1:])

    chunk_mutations = (
        replace(chunk, duration=chunk.duration + Fraction(1, 10**9)),
        replace(chunk, mean=chunk.mean + Fraction(1, 10**9)),
        replace(
            chunk,
            allocated_tail_tolerance=chunk.allocated_tail_tolerance * 2,
        ),
        replace(chunk, terms=chunk.terms + 1),
        replace(
            chunk,
            poisson_tail_upper=np.nextafter(chunk.poisson_tail_upper, math.inf),
        ),
        replace(chunk, precision_bits=chunk.precision_bits + 1),
        replace(chunk, maximum_terms_cap=chunk.maximum_terms_cap + 1),
        replace(chunk, roundoff_gamma_index=chunk.roundoff_gamma_index + 1),
        replace(chunk, delta_p_used=np.nextafter(chunk.delta_p_used, math.inf)),
        replace(
            chunk,
            propagated_power_error=np.nextafter(chunk.propagated_power_error, math.inf),
        ),
        replace(chunk, weight_error=np.nextafter(chunk.weight_error, math.inf)),
        replace(
            chunk,
            accumulation_roundoff=np.nextafter(chunk.accumulation_roundoff, math.inf),
        ),
        replace(
            chunk,
            output_l1_error=np.nextafter(chunk.output_l1_error, math.inf),
        ),
        replace(chunk, roundoff_gamma_index=np.int64(chunk.roundoff_gamma_index)),
        replace(chunk, poisson_tail_upper=np.float64(chunk.poisson_tail_upper)),
    )
    for mutated in chunk_mutations:
        must_reject(with_first_chunk(mutated))


def test_poisson_term_cap_and_negative_action_fail_closed() -> None:
    kernel = small_kernel(dimensions=1)
    initial = initial_for(kernel)
    with pytest.raises(f0.F0VerificationFailure) as tail_error:
        f0.propagate_matrix_free_absolute(
            kernel,
            initial,
            Fraction(10),
            mean_cap=Fraction(10),
            maximum_terms=1,
        )
    assert tail_error.value.code == f0.HOLD_TAIL

    state = np.full(kernel.states, 1.0 / kernel.states)
    state[0] = -0.1
    with pytest.raises(f0.F0VerificationFailure) as action_error:
        f0.matrix_free_p_transpose(kernel, state)
    assert action_error.value.code == f0.HOLD_ACTION


def test_round111_batch_context_values_are_not_silently_identified() -> None:
    first = Fraction.from_float(0.2674801474024189)
    second = Fraction.from_float(0.2674801474024188)
    assert first != second
    first_point = f0.OutwardInterval(0.2674801474024189, 0.2674801474024189)
    assert not first_point.contains_fraction(second)
    combined = f0.OutwardInterval.from_fraction_bounds(min(first, second), max(first, second))
    assert combined.contains_fraction(first)
    assert combined.contains_fraction(second)


def test_science_free_summary_cannot_authorize_science() -> None:
    kernel = small_kernel()
    summary = f0.canonical_science_free_summary(kernel, label="science_free_neutral_small")
    assert summary["positive_budget_primary_control_evaluated"] is False
    assert summary["prospective_control_values_read"] is False
    assert summary["authorized_scientific_command"] is None
    with pytest.raises(f0.F0VerificationFailure) as error:
        f0.canonical_science_free_summary(kernel, label="lp_m1")
    assert error.value.code == f0.HOLD_CONTROL_SOURCE


def _synthetic_three_root_oracle(time: Fraction) -> f0.TimeJetSample:
    roots = (Fraction(8, 5), Fraction(31, 10), Fraction(23, 5))
    uncertainty = Fraction(1, 10**9)
    first_sum = sum(roots, Fraction(0))
    pair_sum = roots[0] * roots[1] + roots[0] * roots[2] + roots[1] * roots[2]
    derivative = -(time - roots[0]) * (time - roots[1]) * (time - roots[2])
    curvature = -3 * time * time + 2 * first_sum * time - pair_sum
    third = -6 * time + 2 * first_sum
    return f0.TimeJetSample(
        time=time,
        jets=(
            f0.OutwardInterval.from_fraction(0),
            f0.OutwardInterval.from_fraction_bounds(
                derivative - uncertainty,
                derivative + uncertainty,
            ),
            f0.OutwardInterval.from_fraction(curvature),
            f0.OutwardInterval.from_fraction(third),
        ),
        m2=Fraction(50),
        m3=Fraction(25),
        m4=Fraction(6),
    )


def test_matrix_free_absolute_time_oracle_is_connected_to_tile_engine() -> None:
    kernel = small_kernel(dimensions=1)
    initial = initial_for(kernel)
    oracle = f0.MatrixFreeAbsoluteTimeJetOracle(
        kernel,
        initial,
        mean_cap=Fraction(1, 5),
        total_tail_tolerance=Fraction(1, 10**15),
    )
    sample = oracle(Fraction(1, 10))
    assert sample.time == Fraction(1, 10)
    assert sample.direct_from_initial
    assert min(sample.m2, sample.m3, sample.m4) >= 0
    tile = f0.enclose_time_tile(oracle, Fraction(1, 10), Fraction(11, 100))
    assert tile.derivative.upper < 0
    assert tile.curvature.lower > 0


def test_quarter_grid_interval_newton_and_complete_three_root_window() -> None:
    bands = (
        f0.RootBand("P1", Fraction(1), Fraction(9, 4), "maximum"),
        f0.RootBand("Q1", Fraction(5, 2), Fraction(15, 4), "minimum"),
        f0.RootBand("P2", Fraction(4), Fraction(11, 2), "maximum"),
    )
    certificate = f0.certify_full_window_topology(
        _synthetic_three_root_oracle,
        window_lower=Fraction(1, 2),
        window_upper=Fraction(6),
        root_bands=bands,
    )
    assert certificate.complete_window_covered
    assert certificate.unresolved_tiles == 0
    assert tuple(root.role for root in certificate.roots) == ("P1", "Q1", "P2")
    exact_roots = (Fraction(8, 5), Fraction(31, 10), Fraction(23, 5))
    for root, exact in zip(certificate.roots, exact_roots, strict=True):
        assert root.final_lower <= exact <= root.final_upper
        assert root.final_upper - root.final_lower <= Fraction(1, 20)
        assert len(root.newton_steps) == 12
        assert root.inclusion_observed
    assert certificate.tiles[0].lower == Fraction(1, 2)
    assert certificate.tiles[-1].upper == Fraction(6)
    assert all(
        left.upper == right.lower
        for left, right in zip(certificate.tiles, certificate.tiles[1:], strict=False)
    )
    f0.audit_full_window_topology(
        certificate,
        oracle=_synthetic_three_root_oracle,
        expected_window_lower=Fraction(1, 2),
        expected_window_upper=Fraction(6),
        expected_root_bands=bands,
        expected_initial_derivative_sign=1,
    )


def test_v2_physical_window_wrapper_uses_frozen_role_bands_only() -> None:
    assert tuple(
        len(f0.physical_root_bands_v2(label)) for label in ("lp_m1", "lp_m2", "lp_m3")
    ) == (
        1,
        3,
        5,
    )
    root = Fraction(8)
    uncertainty = Fraction(1, 10**9)

    def neutral_role_oracle(time: Fraction) -> f0.TimeJetSample:
        return f0.TimeJetSample(
            time=time,
            jets=(
                f0.OutwardInterval.from_fraction(0),
                f0.OutwardInterval.from_fraction_bounds(
                    root - time - uncertainty,
                    root - time + uncertainty,
                ),
                f0.OutwardInterval.from_fraction(-1),
                f0.OutwardInterval.from_fraction(0),
            ),
            m2=Fraction(1),
            m3=Fraction(0),
            m4=Fraction(0),
        )

    certificate = f0.certify_physical_full_window_topology_v2(
        neutral_role_oracle,
        control_id="lp_m1",
    )
    assert certificate.window_lower == Fraction(1, 2)
    assert certificate.window_upper == Fraction(35)
    assert len(certificate.roots) == 1
    assert certificate.roots[0].band_lower == Fraction(11, 2)
    assert certificate.roots[0].band_upper == Fraction(12)
    assert not certificate.prospective_control_values_read
    assert not certificate.positive_budget_primary_control_evaluated
    f0.audit_physical_full_window_topology_v2(
        certificate,
        oracle=neutral_role_oracle,
        control_id="lp_m1",
    )


def test_topology_mutations_fail_closed_on_limits_coverage_newton_and_time_source() -> None:
    bands = (
        f0.RootBand("P1", Fraction(1), Fraction(9, 4), "maximum"),
        f0.RootBand("Q1", Fraction(5, 2), Fraction(15, 4), "minimum"),
        f0.RootBand("P2", Fraction(4), Fraction(11, 2), "maximum"),
    )
    certificate = f0.certify_full_window_topology(
        _synthetic_three_root_oracle,
        window_lower=Fraction(1, 2),
        window_upper=Fraction(6),
        root_bands=bands,
    )
    with pytest.raises(f0.F0VerificationFailure) as limit_error:
        f0.certify_full_window_topology(
            _synthetic_three_root_oracle,
            window_lower=Fraction(1, 2),
            window_upper=Fraction(6),
            root_bands=bands,
            maximum_newton_steps=11,
        )
    assert limit_error.value.code == f0.HOLD_TOPOLOGY

    with pytest.raises(f0.F0VerificationFailure) as coverage_error:
        f0.audit_full_window_topology(
            replace(certificate, tiles=certificate.tiles[1:]),
            oracle=_synthetic_three_root_oracle,
            expected_window_lower=Fraction(1, 2),
            expected_window_upper=Fraction(6),
            expected_root_bands=bands,
            expected_initial_derivative_sign=1,
        )
    assert coverage_error.value.code == f0.HOLD_COVERAGE

    first_root = certificate.roots[0]
    corrupted_step = replace(first_root.newton_steps[0], index=7)
    corrupted_root = replace(
        first_root,
        newton_steps=(corrupted_step,) + first_root.newton_steps[1:],
    )
    with pytest.raises(f0.F0VerificationFailure) as newton_error:
        f0.audit_full_window_topology(
            replace(certificate, roots=(corrupted_root,) + certificate.roots[1:]),
            oracle=_synthetic_three_root_oracle,
            expected_window_lower=Fraction(1, 2),
            expected_window_upper=Fraction(6),
            expected_root_bands=bands,
            expected_initial_derivative_sign=1,
        )
    assert newton_error.value.code == f0.HOLD_NEWTON

    def sequential_oracle(time: Fraction) -> f0.TimeJetSample:
        return replace(_synthetic_three_root_oracle(time), direct_from_initial=False)

    with pytest.raises(f0.F0VerificationFailure) as time_error:
        f0.enclose_time_tile(sequential_oracle, Fraction(1, 2), Fraction(3, 4))
    assert time_error.value.code == f0.HOLD_TIME


def test_saved_topology_rejects_every_semantic_schema_and_oracle_attack() -> None:
    bands = (
        f0.RootBand("P1", Fraction(1), Fraction(9, 4), "maximum"),
        f0.RootBand("Q1", Fraction(5, 2), Fraction(15, 4), "minimum"),
        f0.RootBand("P2", Fraction(4), Fraction(11, 2), "maximum"),
    )
    certificate = f0.certify_full_window_topology(
        _synthetic_three_root_oracle,
        window_lower=Fraction(1, 2),
        window_upper=Fraction(6),
        root_bands=bands,
    )

    def must_reject(
        candidate: f0.FullWindowTopologyCertificate,
        *,
        oracle: object = _synthetic_three_root_oracle,
        expected_bands: tuple[f0.RootBand, ...] = bands,
    ) -> None:
        with pytest.raises(f0.F0VerificationFailure):
            f0.audit_full_window_topology(
                candidate,
                oracle=oracle,
                expected_window_lower=Fraction(1, 2),
                expected_window_upper=Fraction(6),
                expected_root_bands=expected_bands,
                expected_initial_derivative_sign=1,
            )

    first_root = certificate.roots[0]
    first_candidate_index = next(
        index for index, tile in enumerate(certificate.tiles) if tile.candidate
    )
    first_candidate = certificate.tiles[first_candidate_index]
    first_step = first_root.newton_steps[0]
    zero = f0.OutwardInterval.from_fraction(0)

    root_mutations = (
        replace(first_root, role="forged"),
        replace(first_root, kind="minimum"),
        replace(first_root, band_lower=1),
        replace(first_root, band_upper=first_root.band_upper + Fraction(1, 4)),
        replace(first_root, required_curvature_sign=1),
        replace(first_root, inclusion_observed=1),
        replace(
            first_root,
            newton_steps=(replace(first_step, index=np.int64(0)),) + first_root.newton_steps[1:],
        ),
        replace(
            first_root,
            newton_steps=(replace(first_step, derivative_at_midpoint=zero),)
            + first_root.newton_steps[1:],
        ),
    )
    for mutated_root in root_mutations:
        must_reject(
            replace(
                certificate,
                roots=(mutated_root,) + certificate.roots[1:],
            )
        )

    coherent_fake_candidate = replace(
        first_candidate,
        derivative=zero,
        derivative_sign=0,
        candidate=True,
        local_lipschitz_derivative=zero,
        local_taylor_derivative=zero,
    )
    tile_mutations = (
        replace(first_candidate, candidate=1),
        replace(first_candidate, depth=np.int64(first_candidate.depth)),
        coherent_fake_candidate,
    )
    for mutated_tile in tile_mutations:
        tiles = list(certificate.tiles)
        tiles[first_candidate_index] = mutated_tile
        must_reject(replace(certificate, tiles=tuple(tiles)))

    must_reject(replace(certificate, initial_derivative_sign=True))
    must_reject(replace(certificate, window_lower=Fraction(1, 4)))
    must_reject(replace(certificate, complete_window_covered=1))
    must_reject(replace(certificate, unresolved_tiles=False))
    must_reject(
        certificate,
        expected_bands=(replace(bands[0], role="X1"),) + bands[1:],
    )

    def shifted_oracle(time: Fraction) -> f0.TimeJetSample:
        sample = _synthetic_three_root_oracle(time)
        shifted_derivative = f0.OutwardInterval(
            sample.jets[1].lower + 1.0e-6,
            sample.jets[1].upper + 1.0e-6,
        )
        return replace(
            sample,
            jets=(sample.jets[0], shifted_derivative, sample.jets[2], sample.jets[3]),
        )

    must_reject(certificate, oracle=shifted_oracle)
