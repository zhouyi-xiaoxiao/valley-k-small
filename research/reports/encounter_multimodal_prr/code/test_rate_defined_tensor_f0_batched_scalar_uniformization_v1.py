from __future__ import annotations

import ast
import hashlib
import math
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import gmpy2
import numpy as np
import pytest
import rate_defined_tensor_f0_batched_scalar_uniformization_v1 as batched
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_interval_action as directed
import rate_defined_tensor_f0_packed_rate_action as rate_action
import verified_uniformization_enclosure as verified
from scipy import sparse
from scipy.linalg import expm
from test_rate_defined_tensor_f0_packed_uniformization import (
    MAXIMUM_WORKING_BYTES,
    PROVENANCE,
    _payload,
    _problem,
)

TAIL = Fraction(1, 2**80)
Q_DENSE = np.asarray([[-0.625, 0.5], [0.25, -0.5]], dtype=np.float64)
KILLING = np.asarray([0.125, 0.25], dtype=np.float64)
INITIAL = np.asarray([1.0, 0.0], dtype=np.float64)


def _run(
    *,
    times: tuple[Fraction, ...] = (Fraction(0), Fraction(3, 4)),
    horizon: Fraction | None = None,
) -> batched.BatchedScalarReceipt:
    kernel, initial, contract = _problem(killing=(0.125, 0.25))
    return batched.evaluate_batched_scalar_jets(
        kernel,
        initial,
        contract,
        times=times,
        series_horizon=horizon,
        tail_tolerance=TAIL,
    )


def _death_problem_with_rate(
    rate: Fraction,
) -> tuple[
    packed.PackedTensorKernel,
    rate_action.InternalPointBallInput,
    rate_action.RateActionContract,
]:
    axis_name = "negative_odd_jet_axis"
    zeros = ((0.0, 0.0), (0.0, 0.0))
    inputs = packed.PackedKernelInputs(
        axes=(
            packed.PackedAxisPayload(
                name=axis_name,
                size=2,
                periodic=False,
                forward=_payload(
                    zeros,
                    role=f"science_free_axis_{axis_name}_forward",
                    logical_shape=(2,),
                ),
                backward=_payload(
                    zeros,
                    role=f"science_free_axis_{axis_name}_backward",
                    logical_shape=(2,),
                ),
            ),
        ),
        killing=_payload(
            ((0.5, 0.5), (0.25, 0.25)),
            role="science_free_killing",
            logical_shape=(2,),
        ),
    )
    kernel = packed.build_packed_tensor_kernel(
        inputs,
        packed.KernelBuildContract(
            tensor_shape=(2,),
            block_size=2,
            maximum_working_bytes=MAXIMUM_WORKING_BYTES,
            uniformization_rate=rate,
        ),
    )
    directed_contract = directed.make_directed_action_contract(
        (2,),
        block_size=2,
        maximum_scratch_bytes=MAXIMUM_WORKING_BYTES,
    )
    contract = rate_action.make_rate_action_contract(
        directed_contract,
        maximum_numeric_payload_bytes=MAXIMUM_WORKING_BYTES,
        maximum_total_payload_bytes=MAXIMUM_WORKING_BYTES,
    )
    values = np.asarray((1.0, 0.0), dtype=np.float64)
    values.setflags(write=False)
    raw = hashlib.sha256(memoryview(values).cast("B")).hexdigest()
    vector = packed.CanonicalFloat64Vector(
        logical_shape=(2,),
        values=values,
        raw_sha256=raw,
        nonnegative=True,
        source_sha256=hashlib.sha256(
            b"negative-odd-jet-source\x00" + bytes.fromhex(raw)
        ).hexdigest(),
    )
    initial = rate_action.make_internal_point_ball_input(
        vector,
        input_l1_radius_upper=0.0,
        radius_provenance_sha256=PROVENANCE,
    )
    return kernel, initial, contract


def _jet_endpoints(
    evaluation: batched.AbsoluteTimeScalarJets,
) -> tuple[tuple[float, float], ...]:
    return tuple(
        (float.fromhex(row.lower_hex), float.fromhex(row.upper_hex))
        for row in evaluation.jets
    )


def _dense_scalars(time: Fraction) -> tuple[tuple[float, ...], tuple[float, ...]]:
    state = expm(float(time) * Q_DENSE.T) @ INITIAL
    scalars: list[float] = []
    magnitudes: list[float] = []
    action = state
    for order in range(5):
        scalars.append(float(KILLING @ action))
        magnitudes.append(float(np.max(KILLING) * np.sum(np.abs(action))))
        action = Q_DENSE.T @ action
    return tuple(scalars), tuple(magnitudes)


def test_fast_recurrence_matches_the_frozen_packed_centre_action() -> None:
    kernel, initial, contract = _problem(killing=(0.125, 0.25))
    nominal_contract, _ = rate_action._reconstruct_subordinate_contracts(contract)
    vector = packed.CanonicalFloat64Vector(
        logical_shape=initial.logical_shape,
        values=initial.nominal,
        raw_sha256=initial.nominal_raw_sha256,
        nonnegative=True,
        source_sha256=initial.source_vector_raw_sha256,
    )
    expected = packed.block_p_transpose(kernel, vector, nominal_contract)
    source = np.array(initial.nominal, dtype=np.float64, copy=True)
    destination = np.empty_like(source)
    workspace = batched._make_fast_workspace(
        min(kernel.states, kernel.contract.block_size)
    )
    batched._fast_p_transpose_into(kernel, source, destination, workspace)
    assert np.array_equal(destination, expected.nominal.values)
    assert np.array_equal(destination, np.asarray([0.375, 0.5]))
    assert workspace.payload_bytes == 65 * workspace.capacity


def test_dense_oracle_is_enclosed_for_j0_to_j3_and_forward_m2_to_m4() -> None:
    receipt = _run()
    for evaluation in receipt.evaluations:
        time = Fraction(evaluation.time_numerator, evaluation.time_denominator)
        exact_jets, exact_magnitudes = _dense_scalars(time)
        for order, (lower, upper) in enumerate(_jet_endpoints(evaluation)):
            assert lower <= exact_jets[order] <= upper
        for row in evaluation.magnitudes:
            assert row.formula == batched.MAGNITUDE_FORMULA
            assert float.fromhex(row.upper_hex) >= exact_magnitudes[row.order]
    assert receipt.evaluations[0].jets[0].lower_hex != "-0x0.0p+0"
    assert receipt.f0_pass is False
    assert receipt.input_provenance_classification == (
        batched.INPUT_PROVENANCE_CLASSIFICATION
    )
    assert receipt.control_exclusion_proved is False
    assert receipt.science_free_proved is False


def test_near_two_rate_negative_odd_jets_use_sign_aware_scaling() -> None:
    rate_float = float.fromhex("0x1.fffffffffffffp+0")
    rate = Fraction.from_float(rate_float)
    kernel, initial, contract = _death_problem_with_rate(rate)
    time = Fraction(1, 2)
    receipt = batched.evaluate_batched_scalar_jets(
        kernel,
        initial,
        contract,
        times=(time,),
        series_horizon=time,
        tail_tolerance=TAIL,
        precision_bits=128,
    )
    evaluation = receipt.evaluations[0]
    decay = math.exp(-0.5 * float(time))
    exact = (0.5 * decay, -0.25 * decay, 0.125 * decay, -0.0625 * decay)
    endpoints = _jet_endpoints(evaluation)
    for order, truth in enumerate(exact):
        lower, upper = endpoints[order]
        assert lower <= truth <= upper
    assert endpoints[1][1] < 0.0
    assert endpoints[3][1] < 0.0
    queried = batched.reevaluate_canonical_scalar_series(
        receipt.scalar_series,
        times=(time,),
        tail_tolerance=TAIL,
        precision_bits=128,
    )
    assert queried == receipt.evaluations

    rate_lower = batched._mpfr_from_fraction(rate, 128, gmpy2.RoundDown)
    rate_upper = batched._mpfr_from_fraction(rate, 128, gmpy2.RoundUp)
    minus_one = gmpy2.mpfr(-1)
    for order in (1, 3):
        with gmpy2.context(
            gmpy2.get_context(),
            precision=128,
            round=gmpy2.RoundDown,
        ):
            scale_lower = rate_lower**order
        with gmpy2.context(
            gmpy2.get_context(),
            precision=128,
            round=gmpy2.RoundUp,
        ):
            scale_upper = rate_upper**order
        lower, upper = batched._multiply_signed_interval_by_nonnegative_interval(
            minus_one,
            minus_one,
            scale_lower,
            scale_upper,
            precision_bits=128,
        )
        with gmpy2.context(
            gmpy2.get_context(),
            precision=128,
            round=gmpy2.RoundDown,
        ):
            expected_lower = minus_one * scale_upper
        with gmpy2.context(
            gmpy2.get_context(),
            precision=128,
            round=gmpy2.RoundUp,
        ):
            expected_upper = minus_one * scale_lower
        assert lower == expected_lower
        assert upper == expected_upper
        assert lower <= upper < 0
    assert scale_lower < scale_upper


def test_verified_uniformization_oracle_overlaps_and_agrees_with_dense_truth() -> None:
    receipt = _run(times=(Fraction(3, 4),))
    ours = receipt.evaluations[0]
    kernel = verified.build_exact_dyadic_kernel(
        sparse.csr_matrix(Q_DENSE),
        rate=1.0,
    )
    state = verified.propagate_verified(
        kernel,
        INITIAL,
        0.75,
        mean_cap=0.5,
        total_tail_tolerance=2.0**-70,
    )
    reference = verified.enclose_actions_and_scalars(
        kernel,
        state,
        KILLING,
        maximum_order=4,
    )
    exact_jets, _ = _dense_scalars(Fraction(3, 4))
    for order, row in enumerate(ours.jets):
        lower = float.fromhex(row.lower_hex)
        upper = float.fromhex(row.upper_hex)
        assert lower <= exact_jets[order] <= upper
        assert reference[order].scalar_lower <= exact_jets[order]
        assert exact_jets[order] <= reference[order].scalar_upper
        assert max(lower, reference[order].scalar_lower) <= min(
            upper,
            reference[order].scalar_upper,
        )
    for bound, reference_row in zip(ours.magnitudes, reference[2:], strict=True):
        assert float.fromhex(bound.upper_hex) >= reference_row.m_upper


def test_scalar_series_requeries_new_absolute_times_without_power_actions() -> None:
    receipt = _run(
        times=(Fraction(1, 4), Fraction(3, 4)),
        horizon=Fraction(1),
    )
    series = receipt.scalar_series
    assert series.state_arrays_retained is False
    assert series.canonical_scalar_records_retained is True
    assert len(series.records) == receipt.resources.maximum_power_index + 1
    queried = batched.reevaluate_canonical_scalar_series(
        series,
        times=(Fraction(1, 2), Fraction(3, 4)),
        tail_tolerance=TAIL,
    )
    assert queried[1] == receipt.evaluations[1]
    exact, _ = _dense_scalars(Fraction(1, 2))
    for order, (lower, upper) in enumerate(_jet_endpoints(queried[0])):
        assert lower <= exact[order] <= upper
    direct = _run(times=(Fraction(3, 4),), horizon=Fraction(1))
    assert direct.scalar_stream_sha256 == receipt.scalar_stream_sha256
    assert direct.evaluations[0] == receipt.evaluations[1]
    assert all(row.absolute_time_from_initial for row in queried)
    assert all(row.state_chaining_used is False for row in queried)
    with pytest.raises(batched.BatchedScalarFailure, match="horizon"):
        batched.reevaluate_canonical_scalar_series(
            series,
            times=(Fraction(5, 4),),
            tail_tolerance=TAIL,
        )


def test_centered_mpfr_large_mean_8428_does_not_underflow_or_chain() -> None:
    kernel, initial, contract = _problem(
        forward=(0.0, 0.0),
        backward=(0.0, 0.0),
        killing=(0.5, 0.5),
    )
    receipt = batched.evaluate_batched_scalar_jets(
        kernel,
        initial,
        contract,
        times=(Fraction(8428),),
        series_horizon=Fraction(8428),
        tail_tolerance=Fraction(1, 2**60),
        maximum_terms=20_000,
    )
    evaluation = receipt.evaluations[0]
    assert evaluation.poisson.mode == 8428
    assert evaluation.poisson.terms > 8428
    assert 8_428 < len(receipt.scalar_series.records) < 20_000
    assert float.fromhex(evaluation.poisson.tail_upper_hex) <= 2.0**-60
    assert all(math.isfinite(value) for pair in _jet_endpoints(evaluation) for value in pair)
    assert receipt.resources.maximum_simultaneous_full_state_vectors == 2
    assert receipt.resources.retained_full_power_count == 1
    assert receipt.resources.retained_numpy_scalar_power_array is False
    assert receipt.state_chaining_used is False


def test_nested_mutations_hash_swaps_and_scope_promotions_fail_closed() -> None:
    receipt = _run(horizon=Fraction(1))
    first = receipt.scalar_series.records[0]
    changed_record = replace(
        first,
        upper_hex=np.nextafter(
            np.float64(float.fromhex(first.upper_hex)),
            np.float64(math.inf),
        ).item().hex(),
    )
    changed_series = replace(
        receipt.scalar_series,
        records=(changed_record, *receipt.scalar_series.records[1:]),
    )
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_canonical_scalar_power_series(changed_series)
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            replace(receipt, scalar_series=changed_series)
        )
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(replace(receipt, f0_pass=True))
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            replace(receipt, control_exclusion_proved=True)
        )
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            replace(receipt, science_free_proved=True)
        )
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            replace(receipt, scalar_stream_sha256="0" * 64)
        )
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            replace(receipt, state_chaining_used=True)
        )


def test_bool_metadata_and_invalid_planner_limits_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    receipt = _run(times=(Fraction(0),), horizon=Fraction(0))

    def bind_series(
        series: batched.CanonicalScalarPowerSeries,
    ) -> batched.CanonicalScalarPowerSeries:
        provisional = replace(series, series_binding_sha256="0" * 64)
        return replace(
            provisional,
            series_binding_sha256=batched._series_binding(provisional),
        )

    def bind_time(
        row: batched.AbsoluteTimeScalarJets,
    ) -> batched.AbsoluteTimeScalarJets:
        provisional = replace(row, binding_sha256="0" * 64)
        return replace(provisional, binding_sha256=batched._time_binding(provisional))

    def bind_receipt(
        row: batched.BatchedScalarReceipt,
    ) -> batched.BatchedScalarReceipt:
        provisional = replace(row, receipt_sha256="0" * 64)
        return replace(
            provisional,
            receipt_sha256=batched._receipt_binding(provisional),
        )

    first_record = receipt.scalar_series.records[0]
    provisional_record = replace(
        first_record,
        index=False,
        binding_sha256="0" * 64,
    )
    bool_record = replace(
        provisional_record,
        binding_sha256=batched._power_record_binding(provisional_record),
    )
    bool_record_series = bind_series(
        replace(receipt.scalar_series, records=(bool_record,))
    )
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_canonical_scalar_power_series(bool_record_series)

    bool_fraction_series = bind_series(
        replace(receipt.scalar_series, initial_mass_upper_numerator=True)
    )
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_canonical_scalar_power_series(bool_fraction_series)

    evaluation = receipt.evaluations[0]
    bool_time = bind_time(replace(evaluation, time_numerator=False))
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            bind_receipt(replace(receipt, evaluations=(bool_time,)))
        )

    provisional_poisson = replace(
        evaluation.poisson,
        mode_initialization_count=True,
        binding_sha256="0" * 64,
    )
    bool_poisson = replace(
        provisional_poisson,
        binding_sha256=batched._poisson_binding(provisional_poisson),
    )
    bool_poisson_time = bind_time(replace(evaluation, poisson=bool_poisson))
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            bind_receipt(replace(receipt, evaluations=(bool_poisson_time,)))
        )

    bool_resources = replace(receipt.resources, time_count=True)
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            bind_receipt(replace(receipt, resources=bool_resources))
        )

    with pytest.raises(batched.BatchedScalarFailure, match="exact int"):
        batched._centered_poisson_plan(
            Fraction(0),
            TAIL,
            precision_bits=True,
            maximum_terms=64,
        )
    with pytest.raises(batched.BatchedScalarFailure, match="exact int"):
        batched._centered_poisson_plan(
            Fraction(0),
            TAIL,
            precision_bits=128,
            maximum_terms=True,
        )

    def forbidden_mpfr_planning(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("MPFR planning ran before the mode-cap preflight")

    monkeypatch.setattr(batched, "_mpfr_from_fraction", forbidden_mpfr_planning)
    with pytest.raises(batched.BatchedScalarFailure, match="mode"):
        batched._centered_poisson_plan(
            Fraction(5),
            TAIL,
            precision_bits=128,
            maximum_terms=5,
        )


def test_receipt_rejects_out_of_range_precision_and_tail_metadata() -> None:
    receipt = _run(times=(Fraction(0),), horizon=Fraction(0))

    def bind_poisson(
        row: batched.CenteredPoissonLedger,
    ) -> batched.CenteredPoissonLedger:
        provisional = replace(row, binding_sha256="0" * 64)
        return replace(
            provisional,
            binding_sha256=batched._poisson_binding(provisional),
        )

    def bind_time(
        row: batched.AbsoluteTimeScalarJets,
    ) -> batched.AbsoluteTimeScalarJets:
        provisional = replace(row, binding_sha256="0" * 64)
        return replace(provisional, binding_sha256=batched._time_binding(provisional))

    def bind_receipt(
        row: batched.BatchedScalarReceipt,
    ) -> batched.BatchedScalarReceipt:
        provisional = replace(row, receipt_sha256="0" * 64)
        return replace(
            provisional,
            receipt_sha256=batched._receipt_binding(provisional),
        )

    evaluation = receipt.evaluations[0]
    low_precision_poisson = bind_poisson(
        replace(evaluation.poisson, precision_bits=1)
    )
    low_precision_time = bind_time(
        replace(evaluation, poisson=low_precision_poisson)
    )
    low_precision_receipt = bind_receipt(
        replace(
            receipt,
            evaluations=(low_precision_time,),
            resources=replace(receipt.resources, mpfr_precision_bits=1),
        )
    )
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(low_precision_receipt)

    zero_tail_poisson = bind_poisson(
        replace(
            evaluation.poisson,
            requested_tail_numerator=0,
            requested_tail_denominator=1,
        )
    )
    zero_tail_time = bind_time(replace(evaluation, poisson=zero_tail_poisson))
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            bind_receipt(replace(receipt, evaluations=(zero_tail_time,)))
        )

    multi = _run(
        times=(Fraction(0), Fraction(1, 2)),
        horizon=Fraction(1, 2),
    )
    second = multi.evaluations[1]
    looser_tail = 2 * TAIL
    inconsistent_poisson = bind_poisson(
        replace(
            second.poisson,
            requested_tail_numerator=looser_tail.numerator,
            requested_tail_denominator=looser_tail.denominator,
        )
    )
    inconsistent_time = bind_time(replace(second, poisson=inconsistent_poisson))
    with pytest.raises(batched.BatchedScalarFailure):
        batched.validate_batched_scalar_receipt(
            bind_receipt(
                replace(
                    multi,
                    evaluations=(multi.evaluations[0], inconsistent_time),
                )
            )
        )


def test_receipt_is_deterministic_bounded_and_canonical() -> None:
    first = _run(horizon=Fraction(2))
    second = _run(horizon=Fraction(2))
    assert first == second
    batched.validate_batched_scalar_receipt(first)
    resources = first.resources
    assert resources.p_action_calls == resources.maximum_power_index
    assert resources.scalar_observable_calls == resources.maximum_power_index + 1
    assert resources.retained_scalar_power_record_count == len(
        first.scalar_series.records
    )
    horizon = Fraction(
        first.scalar_series.horizon_numerator,
        first.scalar_series.horizon_denominator,
    )
    horizon_mean = Fraction(
        first.uniformization_rate_numerator,
        first.uniformization_rate_denominator,
    ) * horizon
    horizon_mode = horizon_mean.numerator // horizon_mean.denominator
    horizon_right_index = resources.maximum_power_index - batched.MAXIMUM_JET_ORDER
    assert resources.poisson_plan_count == len(first.evaluations) + 1
    assert resources.poisson_p0_back_recurrence_steps_total == (
        sum(row.poisson.mode for row in first.evaluations) + horizon_mode
    )
    assert resources.poisson_right_tail_planning_steps_total == (
        sum(row.poisson.right_tail_planning_steps for row in first.evaluations)
        + horizon_right_index
        - horizon_mode
        + 1
    )
    assert resources.poisson_forward_weight_recurrence_steps_total == sum(
        row.poisson.right_index for row in first.evaluations
    )
    assert resources.block_integer_workspace_bytes == 40 * resources.block_capacity
    assert resources.block_float_workspace_bytes == 24 * resources.block_capacity
    assert resources.block_boolean_workspace_bytes == resources.block_capacity
    assert resources.untracked_explicit_numpy_temporary_bytes == 0
    assert resources.fast_action_workspace_bytes == (
        resources.block_integer_workspace_bytes
        + resources.block_float_workspace_bytes
        + resources.block_boolean_workspace_bytes
    )
    assert resources.declared_peak_numeric_payload_bytes_excluding_preowned_kernel == (
        resources.state_vector_payload_bytes + resources.fast_action_workspace_bytes
    )
    assert resources.bounded_memory_by_declared_counts is True
    assert resources.action_roundoff_proof_complete is True
    assert resources.coefficient_error_included is True
    assert resources.reduction_roundoff_included is True
    assert resources.poisson_roundoff_included is True
    assert resources.poisson_tail_included is True
    assert resources.production_resource_gate is False
    assert resources.f0_pass is False


def test_scalar_series_canonical_persistence_round_trip_and_mutation_rejection() -> None:
    receipt = _run(horizon=Fraction(2))
    encoded = batched.canonical_scalar_power_series_bytes(receipt.scalar_series)
    restored = batched.load_canonical_scalar_power_series_bytes(encoded)
    assert restored == receipt.scalar_series
    queried = batched.reevaluate_canonical_scalar_series(
        restored,
        times=(Fraction(1, 2),),
        tail_tolerance=TAIL,
    )
    exact, _ = _dense_scalars(Fraction(1, 2))
    for order, (lower, upper) in enumerate(_jet_endpoints(queried[0])):
        assert lower <= exact[order] <= upper
    mutated = encoded.replace(
        b'"science_free_proved":false',
        b'"science_free_proved":true',
        1,
    )
    assert mutated != encoded
    with pytest.raises(batched.BatchedScalarFailure):
        batched.load_canonical_scalar_power_series_bytes(mutated)


def test_no_control_surface_and_narrow_local_imports() -> None:
    source = Path(batched.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= {
        "__future__",
        "ctypes",
        "dataclasses",
        "fractions",
        "gmpy2",
        "hashlib",
        "hmac",
        "json",
        "math",
        "numpy",
        "platform",
        "rate_defined_tensor_f0_packed",
        "rate_defined_tensor_f0_packed_rate_action",
        "struct",
        "sys",
        "typing",
    }
    assert "lp_m1" not in source
    assert "lp_m2" not in source
    assert "lp_m3" not in source
    assert "subprocess" not in source
    assert "socket" not in source
    assert source.count("_finalize_absolute_time_rows(") == 3
    assert "np.all(np.isfinite(current))" not in source
    assert "np.any(current < 0.0)" not in source
    assert "np.isfinite(left_block)" not in source
    assert "np.isfinite(right_block)" not in source
