from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from fractions import Fraction

import numpy as np
import pytest
import rate_defined_tensor_f0_batched_scalar_uniformization_v1 as batched
import rate_defined_tensor_f0_compiled_batch_v1 as integrated
import rate_defined_tensor_f0_compiled_power_stream_v1 as compiled
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_interval_action as directed
import rate_defined_tensor_f0_packed_rate_action as rate_action

MAXIMUM_WORKING_BYTES = 32 * 1024 * 1024
PROVENANCE = hashlib.sha256(b"compiled-batch-test-radius-v1").hexdigest()
TAIL = Fraction(1, 2**48)


def _payload(
    rows: tuple[tuple[float, float], ...],
    *,
    role: str,
    logical_shape: tuple[int, ...],
    block_size: int,
) -> packed.PackedIntervalPayload:
    return packed.create_packed_interval_payload(
        rows,
        role=role,
        logical_shape=logical_shape,
        nonnegative=True,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )


def _problem(
    shape: tuple[int, ...],
    periodic: tuple[bool, ...],
) -> tuple[
    packed.PackedTensorKernel,
    rate_action.InternalPointBallInput,
    rate_action.RateActionContract,
]:
    states = math.prod(shape)
    block_size = states
    axes: list[packed.PackedAxisPayload] = []
    for dimension, (size, is_periodic) in enumerate(
        zip(shape, periodic, strict=True)
    ):
        name = f"compiled_batch_axis_{dimension}"
        forward = [Fraction(dimension + 1, 64) for _ in range(size)]
        backward = [Fraction(dimension + 2, 128) for _ in range(size)]
        if not is_periodic:
            forward[-1] = Fraction(0)
            backward[0] = Fraction(0)
        axes.append(
            packed.PackedAxisPayload(
                name=name,
                size=size,
                periodic=is_periodic,
                forward=_payload(
                    tuple((float(value), float(value)) for value in forward),
                    role=f"science_free_axis_{name}_forward",
                    logical_shape=(size,),
                    block_size=block_size,
                ),
                backward=_payload(
                    tuple((float(value), float(value)) for value in backward),
                    role=f"science_free_axis_{name}_backward",
                    logical_shape=(size,),
                    block_size=block_size,
                ),
            )
        )
    killing = tuple(
        Fraction(2 + index % 3, 64) for index in range(states)
    )
    inputs = packed.PackedKernelInputs(
        axes=tuple(axes),
        killing=_payload(
            tuple((float(value), float(value)) for value in killing),
            role="science_free_killing",
            logical_shape=shape,
            block_size=block_size,
        ),
    )
    kernel = packed.build_packed_tensor_kernel(
        inputs,
        packed.KernelBuildContract(
            tensor_shape=shape,
            block_size=block_size,
            maximum_working_bytes=MAXIMUM_WORKING_BYTES,
            uniformization_rate=Fraction(1),
        ),
    )
    directed_contract = directed.make_directed_action_contract(
        shape,
        block_size=block_size,
        maximum_scratch_bytes=MAXIMUM_WORKING_BYTES,
    )
    contract = rate_action.make_rate_action_contract(
        directed_contract,
        maximum_numeric_payload_bytes=MAXIMUM_WORKING_BYTES,
        maximum_total_payload_bytes=MAXIMUM_WORKING_BYTES,
    )
    values = np.zeros(states, dtype=np.float64)
    values[states // 2] = 1.0
    values.setflags(write=False)
    raw = hashlib.sha256(memoryview(values).cast("B")).hexdigest()
    vector = packed.CanonicalFloat64Vector(
        logical_shape=shape,
        values=values,
        raw_sha256=raw,
        nonnegative=True,
        source_sha256=hashlib.sha256(
            b"compiled-batch-test-initial-v1\x00" + bytes.fromhex(raw)
        ).hexdigest(),
    )
    initial = rate_action.make_internal_point_ball_input(
        vector,
        input_l1_radius_upper=0.0,
        radius_provenance_sha256=PROVENANCE,
    )
    return kernel, initial, contract


def _metadata(
    kernel: packed.PackedTensorKernel,
    initial: rate_action.InternalPointBallInput,
    *,
    horizon: Fraction = Fraction(3, 4),
    times: tuple[Fraction, ...] = (
        Fraction(0),
        Fraction(1, 3),
        Fraction(3, 4),
    ),
) -> integrated.GenericCompiledBatchMethodMetadata:
    witnesses = {row.name: row.value for row in kernel.ledger.witnesses}
    return integrated.GenericCompiledBatchMethodMetadata(
        uniformization_rate=kernel.rate_fraction,
        coefficient_l1_uncertainty_upper=witnesses["delta_p_selected"],
        maximum_center_row_sum=witnesses["maximum_center_row_sum"],
        maximum_killing_upper=witnesses["maximum_killing_upper"],
        maximum_killing_uncertainty=witnesses[
            "maximum_killing_uncertainty"
        ],
        initial_l1_radius_upper=Fraction.from_float(
            initial.input_l1_radius_upper
        ),
        initial_mass_cap=Fraction(1),
        series_horizon=horizon,
        tail_tolerance=TAIL,
        mpfr_precision_bits=192,
        maximum_poisson_terms=2_000,
        evaluation_times=times,
    )


@pytest.mark.parametrize(
    ("shape", "periodic"),
    [
        ((3,), (False,)),
        ((2, 3), (False, True)),
        ((2, 2, 2), (True, False, True)),
    ],
)
def test_compiled_records_and_j0_to_j3_match_python_canonical_path(
    shape: tuple[int, ...],
    periodic: tuple[bool, ...],
) -> None:
    kernel, initial, contract = _problem(shape, periodic)
    metadata = _metadata(kernel, initial)
    python_receipt = batched.evaluate_batched_scalar_jets(
        kernel,
        initial,
        contract,
        times=metadata.evaluation_times,
        tail_tolerance=metadata.tail_tolerance,
        initial_mass_cap=metadata.initial_mass_cap,
        series_horizon=metadata.series_horizon,
        precision_bits=metadata.mpfr_precision_bits,
        maximum_terms=metadata.maximum_poisson_terms,
    )
    backend = compiled.build_compiled_power_stream_backend(kernel)
    result = integrated.build_compiled_canonical_scalar_series(
        backend,
        initial.nominal,
        metadata,
    )
    assert len(result.scalar_series.records) == len(
        python_receipt.scalar_series.records
    )
    for compiled_row, python_row in zip(
        result.scalar_series.records,
        python_receipt.scalar_series.records,
        strict=True,
    ):
        compiled_interval = (
            float.fromhex(compiled_row.lower_hex),
            float.fromhex(compiled_row.upper_hex),
        )
        python_interval = (
            float.fromhex(python_row.lower_hex),
            float.fromhex(python_row.upper_hex),
        )
        assert max(compiled_interval[0], python_interval[0]) <= min(
            compiled_interval[1],
            python_interval[1],
        )
    for compiled_evaluation, python_evaluation in zip(
        result.evaluations,
        python_receipt.evaluations,
        strict=True,
    ):
        for compiled_jet, python_jet in zip(
            compiled_evaluation.jets,
            python_evaluation.jets,
            strict=True,
        ):
            assert compiled_jet.order == python_jet.order
            assert max(
                float.fromhex(compiled_jet.lower_hex),
                float.fromhex(python_jet.lower_hex),
            ) <= min(
                float.fromhex(compiled_jet.upper_hex),
                float.fromhex(python_jet.upper_hex),
            )
    assert tuple(
        row.order for row in result.evaluations[0].jets
    ) == integrated.RETURNED_JET_ORDERS
    assert result.compiled_stream.final_power.flags.owndata
    assert result.compiled_stream.final_power.base is None
    assert not result.compiled_stream.final_power.flags.writeable
    integrated.validate_compiled_canonical_scalar_series_result(result)


def test_exactly_one_compiled_run_and_reevaluation_reuses_scalar_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel, initial, _ = _problem((2, 3), (False, True))
    metadata = _metadata(kernel, initial)
    backend = compiled.build_compiled_power_stream_backend(kernel)
    original = compiled.CompiledPowerStreamBackend.run_power_stream
    calls = 0

    def counted(
        self: compiled.CompiledPowerStreamBackend,
        source: np.ndarray,
        *,
        maximum_power: int,
    ) -> compiled.CompiledPowerStreamResult:
        nonlocal calls
        calls += 1
        return original(self, source, maximum_power=maximum_power)

    monkeypatch.setattr(
        compiled.CompiledPowerStreamBackend,
        "run_power_stream",
        counted,
    )
    result = integrated.build_compiled_canonical_scalar_series(
        backend,
        initial.nominal,
        metadata,
    )
    assert calls == 1
    extra = batched.reevaluate_canonical_scalar_series(
        result.scalar_series,
        times=(Fraction(1, 8), Fraction(1, 2)),
        tail_tolerance=metadata.tail_tolerance,
        precision_bits=metadata.mpfr_precision_bits,
        maximum_terms=metadata.maximum_poisson_terms,
    )
    integrated.validate_compiled_canonical_scalar_series_result(result)
    assert calls == 1
    assert len(extra) == 2
    assert result.receipt.repeated_p_actions_during_reevaluation == 0


def test_arbitrary_generic_metadata_never_promotes_authority() -> None:
    kernel, initial, _ = _problem((3,), (False,))
    backend = compiled.build_compiled_power_stream_backend(kernel)
    declared = dataclasses.replace(
        _metadata(
            kernel,
            initial,
            horizon=Fraction(1, 16),
            times=(Fraction(1, 16),),
        ),
        uniformization_rate=Fraction(2),
        coefficient_l1_uncertainty_upper=Fraction(1, 8),
        maximum_center_row_sum=Fraction(1),
        maximum_killing_upper=Fraction(1),
        maximum_killing_uncertainty=Fraction(1, 2),
        initial_l1_radius_upper=Fraction(1, 4),
        initial_mass_cap=Fraction(3, 4),
    )
    result = integrated.build_compiled_canonical_scalar_series(
        backend,
        initial.nominal,
        declared,
    )
    receipt = result.receipt
    assert receipt.input_provenance_classification == (
        batched.INPUT_PROVENANCE_CLASSIFICATION
    )
    assert receipt.method_metadata_preconditions_proved is False
    assert receipt.initial_mass_cap_independently_proved is False
    assert receipt.external_stream_replay_complete is False
    assert receipt.control_exclusion_proved is False
    assert receipt.science_free_proved is False
    assert receipt.authorizes_scientific_execution is False
    assert receipt.science_executed is False
    assert receipt.topology_pass is False
    assert receipt.production_scale_execution_classified is False
    assert receipt.resource_pass is False
    assert receipt.f0_pass is False
    field_names = {
        field.name
        for field in dataclasses.fields(
            integrated.GenericCompiledBatchMethodMetadata
        )
    }
    assert not any(
        token in name
        for name in field_names
        for token in ("role", "control", "selector", "science", "budget")
    )


def test_512_evaluations_and_resource_payload_ledger_remain_nonpromoting() -> None:
    kernel, initial, _ = _problem((3,), (False,))
    times = tuple(Fraction(index, 1024) for index in range(512))
    metadata = _metadata(
        kernel,
        initial,
        horizon=Fraction(1, 2),
        times=times,
    )
    result = integrated.build_compiled_canonical_scalar_series(
        compiled.build_compiled_power_stream_backend(kernel),
        initial.nominal,
        metadata,
    )
    ledger = result.receipt.resources
    assert len(result.evaluations) == 512
    assert len(result.receipt.evaluation_plans) == 512
    assert ledger.evaluation_count == 512
    assert ledger.evaluation_jet_count == 4 * 512
    assert ledger.evaluation_magnitude_count == 3 * 512
    assert ledger.evaluation_float_endpoint_payload_bytes == 88 * 512
    assert ledger.compiled_power_stream_run_count == 1
    assert ledger.float64_stream_payload_formula_complete is True
    assert ledger.validation_temporary_payload_bytes_measured is False
    assert ledger.complete_numeric_payload_ledger is False
    assert ledger.complete_process_peak_measured is False
    assert ledger.resource_pass is False
    assert ledger.f0_pass is False


def test_horizon_100_rate_256_plan_binds_required_power_without_promotion() -> None:
    source = compiled.GenericPackedTensorInput(
        tensor_shape=(2,),
        periodic=(False,),
        p_self_center=np.ones(2, dtype=np.float64),
        p_forward_center=(np.zeros(2, dtype=np.float64),),
        p_backward_center=(np.zeros(2, dtype=np.float64),),
        killing_center=np.full(2, 1 / 64, dtype=np.float64),
        reduction_block_size=2,
    )
    initial = np.asarray((1.0, 0.0), dtype=np.float64)
    initial.setflags(write=False)
    metadata = integrated.GenericCompiledBatchMethodMetadata(
        uniformization_rate=Fraction(256),
        coefficient_l1_uncertainty_upper=Fraction(0),
        maximum_center_row_sum=Fraction(1),
        maximum_killing_upper=Fraction(1, 64),
        maximum_killing_uncertainty=Fraction(0),
        initial_l1_radius_upper=Fraction(0),
        initial_mass_cap=Fraction(1),
        series_horizon=Fraction(100),
        tail_tolerance=Fraction(1, 10**18),
        mpfr_precision_bits=192,
        maximum_poisson_terms=50_000,
        evaluation_times=(),
    )
    result = integrated.build_compiled_canonical_scalar_series(
        compiled.build_compiled_power_stream_backend(source),
        initial,
        metadata,
    )
    plan = result.receipt.horizon_plan
    assert plan.mean_numerator == 25_600
    assert plan.mean_denominator == 1
    assert plan.mode == 25_600
    assert plan.right_index == 27_014
    assert plan.maximum_required_power_index == 27_018
    assert result.scalar_series.maximum_power_index == 27_018
    assert result.receipt.resources.p_action_call_count == 27_018
    assert result.receipt.compiled_power_stream_run_count == 1
    assert result.receipt.absolute_time_reevaluation_used is False
    assert result.receipt.resource_pass is False
    assert result.receipt.f0_pass is False


def test_receipt_binds_complete_build_stream_plans_and_canonical_evidence() -> None:
    kernel, initial, _ = _problem((2, 2, 2), (True, False, True))
    result = integrated.build_compiled_canonical_scalar_series(
        compiled.build_compiled_power_stream_backend(kernel),
        initial.nominal,
        _metadata(kernel, initial),
    )
    receipt = result.receipt
    build = result.backend.receipt.build
    assert receipt.compiled_backend_receipt == result.backend.receipt
    assert receipt.compiled_build_receipt == build
    assert receipt.compiled_stream_receipt == result.compiled_stream.receipt
    assert receipt.batched_scalar_source_sha256 == hashlib.sha256(
        integrated._BATCHED_SOURCE_PATH.read_bytes()
    ).hexdigest()
    assert receipt.batched_scalar_runtime_identity == batched._runtime_identity()
    assert receipt.compiled_build_receipt.c_source_sha256 == build.c_source_sha256
    assert (
        receipt.compiled_build_receipt.python_wrapper_sha256
        == build.python_wrapper_sha256
    )
    assert (
        receipt.compiled_build_receipt.compiler_binary_sha256
        == build.compiler_binary_sha256
    )
    assert (
        receipt.compiled_build_receipt.compiler_identity_sha256
        == build.compiler_identity_sha256
    )
    assert (
        receipt.compiled_build_receipt.compiled_binary_sha256
        == build.compiled_binary_sha256
    )
    evidence = integrated.compiled_batch_evidence_bytes(result)
    assert len(evidence) <= integrated.MAXIMUM_EVIDENCE_BYTES
    assert evidence.decode("ascii").encode("ascii") == evidence
    parsed = json.loads(evidence)
    assert set(parsed) == {
        "evidence_binding_sha256",
        "evaluations",
        "metadata",
        "receipt",
        "schema",
        "series",
    }
    assert parsed["receipt"]["compiled_build_receipt"][
        "compiled_binary_sha256"
    ] == build.compiled_binary_sha256
    assert parsed["receipt"]["compiled_backend_receipt"][
        "action_operations"
    ]["maximum_dependency_operation_count"] == 7
    assert parsed["series"]["records"]
    assert len(parsed["evaluations"]) == 3
    assert evidence == json.dumps(
        parsed,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def test_forged_compiled_operation_ledgers_fail_independent_replay() -> None:
    kernel, initial, _ = _problem((2, 3), (False, True))
    metadata = _metadata(kernel, initial)
    backend = compiled.build_compiled_power_stream_backend(kernel)
    original = backend.receipt
    forged_action = dataclasses.replace(
        original.action_operations,
        maximum_dependency_operation_count=0,
        underflow_event_operation_budget=0,
    )
    forged_mass = dataclasses.replace(
        original.mass_reduction_operations,
        upstream_enclosure_operation_count=0,
        underflow_event_operation_budget=0,
    )
    forged_dot = dataclasses.replace(
        original.killing_dot_operations,
        upstream_enclosure_operation_count=0,
        underflow_event_operation_budget=0,
    )
    provisional = dataclasses.replace(
        original,
        action_operations=forged_action,
        mass_reduction_operations=forged_mass,
        killing_dot_operations=forged_dot,
        receipt_sha256="0" * 64,
    )
    forged = dataclasses.replace(
        provisional,
        receipt_sha256=compiled._canonical_json_sha256(
            compiled._dataclass_payload(provisional)
        ),
    )
    object.__setattr__(backend, "_receipt", forged)
    try:
        backend.validate()
        with pytest.raises(
            integrated.CompiledBatchFailure,
            match="operation ledgers failed independent replay",
        ):
            integrated.build_compiled_canonical_scalar_series(
                backend,
                initial.nominal,
                metadata,
            )
    finally:
        object.__setattr__(backend, "_receipt", original)
    backend.validate()


def test_strict_types_plan_tail_and_nested_receipt_tampering_fail_closed() -> None:
    kernel, initial, _ = _problem((3,), (False,))
    metadata = _metadata(kernel, initial)
    backend = compiled.build_compiled_power_stream_backend(kernel)
    with pytest.raises(integrated.CompiledBatchFailure):
        integrated.build_compiled_canonical_scalar_series(
            backend,
            initial.nominal,
            dataclasses.replace(metadata, mpfr_precision_bits=True),
        )
    result = integrated.build_compiled_canonical_scalar_series(
        backend,
        initial.nominal,
        metadata,
    )
    zero_tail_plan = dataclasses.replace(
        result.receipt.horizon_plan,
        tail_upper_hex="0x0.0p+0",
    )
    with pytest.raises(integrated.CompiledBatchFailure):
        integrated.validate_compiled_canonical_scalar_series_result(
            dataclasses.replace(
                result,
                receipt=dataclasses.replace(
                    result.receipt,
                    horizon_plan=zero_tail_plan,
                ),
            )
        )
    short_plan = dataclasses.replace(
        result.receipt.horizon_plan,
        maximum_required_power_index=(
            result.scalar_series.maximum_power_index + 1
        ),
    )
    with pytest.raises(integrated.CompiledBatchFailure):
        integrated.validate_compiled_canonical_scalar_series_result(
            dataclasses.replace(
                result,
                receipt=dataclasses.replace(
                    result.receipt,
                    horizon_plan=short_plan,
                ),
            )
        )
    forged_build = dataclasses.replace(
        result.receipt.compiled_build_receipt,
        compiler_binary_sha256="0" * 64,
    )
    with pytest.raises(integrated.CompiledBatchFailure):
        integrated.validate_compiled_canonical_scalar_series_result(
            dataclasses.replace(
                result,
                receipt=dataclasses.replace(
                    result.receipt,
                    compiled_build_receipt=forged_build,
                ),
            )
        )
