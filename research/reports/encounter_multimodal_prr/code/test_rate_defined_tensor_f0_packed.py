from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import multiprocessing
import os
import struct
from dataclasses import replace
from fractions import Fraction

import numpy as np
import pytest
import rate_defined_tensor_f0 as legacy
import rate_defined_tensor_f0_packed as packed

MAXIMUM_WORKING_BYTES = 2_000_000
MAXIMUM_SCRATCH_BYTES = 2_000_000
ZERO_SEQUENCE_SHAPE = (2, 3, 4)
ZERO_SEQUENCE_BLOCK_SIZES = tuple(range(1, 16)) + (16, 24, 99)


def _zero_sequence_payload(
    *,
    block_size: int,
    negative_zero: bool,
) -> packed.PackedIntervalPayload:
    rows: list[tuple[float, float]] = []
    for index in range(math.prod(ZERO_SEQUENCE_SHAPE)):
        if index % 3 == 0:
            rows.append((0.0, 0.0))
        elif index % 3 == 1:
            rows.append((0.0, float(Fraction(index + 1, 256))))
        else:
            rows.append((float(Fraction(-(index + 1), 256)), 0.0))
    payload = packed.create_packed_interval_payload(
        tuple(rows),
        role="science_free_zero_endpoint_sequence",
        logical_shape=ZERO_SEQUENCE_SHAPE,
        nonnegative=False,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )
    if not negative_zero:
        return payload
    raw = bytearray(payload.raw_bytes)
    for flat_index, endpoint in ((0, 0), (3, 1), (15, 0), (16, 0), (23, 1)):
        struct.pack_into(
            "=d",
            raw,
            flat_index * packed.INTERVAL_BYTES_PER_STATE + endpoint * packed.FLOAT64_BYTES,
            -0.0,
        )
    raw_bytes = bytes(raw)
    return replace(
        payload,
        manifest=replace(payload.manifest, raw_sha256=hashlib.sha256(raw_bytes).hexdigest()),
        raw_bytes=raw_bytes,
    )


def _zero_sequence_statuses() -> tuple[tuple[int, str, str], ...]:
    statuses: list[tuple[int, str, str]] = []
    for block_size in ZERO_SEQUENCE_BLOCK_SIZES:
        for label, negative_zero in (("positive", False), ("negative", True)):
            payload = _zero_sequence_payload(
                block_size=block_size,
                negative_zero=negative_zero,
            )
            try:
                packed.load_canonical_packed_intervals(payload)
            except packed.PackedF0Failure as error:
                status = error.code
            else:
                status = "PASS"
            statuses.append((block_size, label, status))
    return tuple(statuses)


def _fresh_zero_sequence_worker(queue: object) -> None:
    queue.put(_zero_sequence_statuses())  # type: ignore[attr-defined]


def _payload_from_legacy_intervals(
    intervals: tuple[legacy.OutwardInterval, ...],
    *,
    role: str,
    logical_shape: tuple[int, ...],
    block_size: int,
    nonnegative: bool = True,
) -> packed.PackedIntervalPayload:
    return packed.create_packed_interval_payload(
        tuple((float(interval.lower), float(interval.upper)) for interval in intervals),
        role=role,
        logical_shape=logical_shape,
        nonnegative=nonnegative,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )


def _payload_from_values(
    values: np.ndarray,
    *,
    role: str,
    logical_shape: tuple[int, ...],
    block_size: int,
    nonnegative: bool,
) -> packed.PackedIntervalPayload:
    return packed.create_packed_interval_payload(
        tuple((float(value), float(value)) for value in values),
        role=role,
        logical_shape=logical_shape,
        nonnegative=nonnegative,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )


def _legacy_axes() -> tuple[legacy.TensorAxis, ...]:
    reflecting = legacy.build_reflecting_sg_axis(
        "reflecting",
        (Fraction(0), Fraction(1, 2), Fraction(1)),
        (Fraction(0), Fraction(1, 10), Fraction(1, 5)),
        Fraction(1, 100),
    )
    periodic_y = legacy.build_periodic_diffusion_axis(
        "periodic_y",
        4,
        Fraction(1),
        Fraction(1, 200),
    )
    periodic_z = legacy.build_periodic_diffusion_axis(
        "periodic_z",
        5,
        Fraction(1),
        Fraction(1, 250),
        half_cell_shift=True,
    )
    return reflecting, periodic_y, periodic_z


def _packed_problem_from_legacy(
    *,
    block_size: int,
    dimensions: int = 3,
) -> tuple[
    packed.PackedKernelInputs,
    packed.KernelBuildContract,
    legacy.RateDefinedTensorKernel,
]:
    axes = _legacy_axes()[:dimensions]
    shape = tuple(axis.size for axis in axes)
    killing = (legacy.OutwardInterval.from_fraction(Fraction(1, 256)),) * math.prod(shape)
    legacy_kernel = legacy.build_rate_defined_tensor_kernel(axes, killing)
    axis_payloads = tuple(
        packed.PackedAxisPayload(
            name=axis.name,
            size=axis.size,
            periodic=axis.periodic,
            forward=_payload_from_legacy_intervals(
                axis.forward_rates,
                role=f"science_free_axis_{axis.name}_forward",
                logical_shape=(axis.size,),
                block_size=block_size,
            ),
            backward=_payload_from_legacy_intervals(
                axis.backward_rates,
                role=f"science_free_axis_{axis.name}_backward",
                logical_shape=(axis.size,),
                block_size=block_size,
            ),
        )
        for axis in axes
    )
    inputs = packed.PackedKernelInputs(
        axes=axis_payloads,
        killing=_payload_from_legacy_intervals(
            killing,
            role="science_free_killing",
            logical_shape=shape,
            block_size=block_size,
        ),
    )
    contract = packed.KernelBuildContract(
        tensor_shape=shape,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
        uniformization_rate=None,
    )
    return inputs, contract, legacy_kernel


def _plain_axis_payload(
    name: str,
    size: int,
    *,
    periodic: bool,
    block_size: int,
    rate: float,
) -> packed.PackedAxisPayload:
    forward = [(rate, rate) for _ in range(size)]
    backward = [(rate, rate) for _ in range(size)]
    if not periodic:
        forward[-1] = (0.0, 0.0)
        backward[0] = (0.0, 0.0)
    return packed.PackedAxisPayload(
        name=name,
        size=size,
        periodic=periodic,
        forward=packed.create_packed_interval_payload(
            tuple(forward),
            role=f"science_free_axis_{name}_forward",
            logical_shape=(size,),
            nonnegative=True,
            block_size=block_size,
            maximum_working_bytes=MAXIMUM_WORKING_BYTES,
        ),
        backward=packed.create_packed_interval_payload(
            tuple(backward),
            role=f"science_free_axis_{name}_backward",
            logical_shape=(size,),
            nonnegative=True,
            block_size=block_size,
            maximum_working_bytes=MAXIMUM_WORKING_BYTES,
        ),
    )


def _plain_problem(
    shape: tuple[int, ...],
    *,
    block_size: int,
) -> tuple[packed.PackedKernelInputs, packed.KernelBuildContract]:
    axes = tuple(
        _plain_axis_payload(
            f"axis{dimension}",
            size,
            periodic=dimension != 0,
            block_size=block_size,
            rate=float(Fraction(dimension + 1, 512)),
        )
        for dimension, size in enumerate(shape)
    )
    killing_value = float(Fraction(1, 256))
    killing = packed.create_packed_interval_payload(
        ((killing_value, killing_value),) * math.prod(shape),
        role="science_free_killing",
        logical_shape=shape,
        nonnegative=True,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )
    return (
        packed.PackedKernelInputs(axes=axes, killing=killing),
        packed.KernelBuildContract(
            tensor_shape=shape,
            block_size=block_size,
            maximum_working_bytes=MAXIMUM_WORKING_BYTES,
            uniformization_rate=None,
        ),
    )


def _initial_payload(
    shape: tuple[int, ...],
    *,
    block_size: int,
) -> packed.PackedIntervalPayload:
    states = math.prod(shape)
    values = np.full(states, 1.0 / states, dtype=np.float64)
    return _payload_from_values(
        values,
        role="science_free_initial",
        logical_shape=shape,
        block_size=block_size,
        nonnegative=True,
    )


def _run_fresh_verify(
    inputs: packed.PackedKernelInputs,
    initial: packed.PackedIntervalPayload,
    kernel_contract: packed.KernelBuildContract,
    action_contract: packed.BlockActionContract,
    artifact: packed.ProducerActionArtifact,
) -> tuple[object, ...]:
    try:
        receipt = packed.spawn_verify_action_artifact(
            inputs,
            initial,
            kernel_contract,
            action_contract,
            artifact,
        )
    except packed.PackedF0Failure as error:
        return "error", error.code
    return (
        "ok",
        receipt.status,
        receipt.producer_pid,
        receipt.verifier_pid,
        receipt.fresh_process,
        receipt.verifier_owned_replay,
        receipt.producer_arrays_accepted,
        receipt.science_executed,
        receipt.f0_pass,
        receipt.launch_capability_sha256,
        receipt.request_sha256,
        receipt.artifact_body_sha256,
    )


def _witness_map(kernel: packed.PackedTensorKernel) -> dict[str, packed.ExactWitness]:
    return {witness.name: witness for witness in kernel.ledger.witnesses}


def _count_retained_fractions(value: object, seen: set[int] | None = None) -> int:
    if seen is None:
        seen = set()
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    if type(value) is Fraction:
        return 1
    if type(value) in {str, bytes, int, float, bool, type(None), np.ndarray}:
        return 0
    if type(value) is tuple:
        return sum(_count_retained_fractions(entry, seen) for entry in value)
    if dataclasses.is_dataclass(value):
        return sum(
            _count_retained_fractions(getattr(value, field.name), seen)
            for field in dataclasses.fields(value)
        )
    return 0


def test_canonical_packed_source_is_owned_native_readonly_and_raw_hash_bound() -> None:
    payload = packed.create_packed_interval_payload(
        ((0.0, 0.0), (0.25, 0.5), (1.0, 1.0)),
        role="science_free_initial",
        logical_shape=(3,),
        nonnegative=True,
        block_size=2,
        maximum_working_bytes=128,
    )
    source = packed.load_canonical_packed_intervals(payload)
    assert type(source) is packed.CanonicalPackedIntervals
    assert type(source.intervals) is np.ndarray
    assert source.intervals.dtype == np.dtype(np.float64)
    assert source.intervals.dtype.isnative
    assert source.intervals.flags.c_contiguous
    assert source.intervals.flags.aligned
    assert source.intervals.flags.owndata
    assert source.intervals.base is None
    assert not source.intervals.flags.writeable
    assert source.manifest.logical_shape == (3,)
    assert source.manifest.array_shape == (3, 2)
    assert source.manifest.state_count == 3
    assert source.manifest.raw_byte_length == 48
    packed.validate_canonical_packed_intervals(source)


def test_interval_validation_boolean_scratch_is_block_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    states = 101
    block_size = 7
    payload = packed.create_packed_interval_payload(
        ((0.0, 0.0),) * states,
        role="science_free_initial",
        logical_shape=(states,),
        nonnegative=True,
        block_size=block_size,
        maximum_working_bytes=(packed.INTERVAL_VALIDATION_SCRATCH_BYTES_PER_STATE * block_size),
    )
    source = packed.load_canonical_packed_intervals(payload)
    original_empty = np.empty
    boolean_layouts: list[tuple[tuple[int, ...], tuple[int, ...], bool]] = []

    def monitored_empty(*args: object, **kwargs: object) -> np.ndarray:
        result = original_empty(*args, **kwargs)
        if result.dtype == np.dtype(np.bool_):
            boolean_layouts.append(
                (
                    tuple(int(value) for value in result.shape),
                    tuple(int(value) for value in result.strides),
                    bool(result.flags.c_contiguous),
                )
            )
        return result

    monkeypatch.setattr(np, "empty", monitored_empty)
    packed.validate_canonical_packed_intervals(source)
    assert packed.INTERVAL_VALIDATION_SCRATCH_BYTES_PER_STATE == 2
    assert boolean_layouts == [((2, block_size), (block_size, 1), True)]


def test_contiguous_boolean_validator_accepts_positive_zero_and_rejects_negative_zero() -> None:
    statuses = _zero_sequence_statuses()
    assert len(statuses) == 2 * len(ZERO_SEQUENCE_BLOCK_SIZES)
    assert {block_size for block_size, _, _ in statuses} == set(ZERO_SEQUENCE_BLOCK_SIZES)
    assert all(status == "PASS" for _, label, status in statuses if label == "positive")
    assert all(
        status == packed.HOLD_PACKED_ENDPOINT
        for _, label, status in statuses
        if label == "negative"
    )
    positive_hashes = {
        _zero_sequence_payload(block_size=block_size, negative_zero=False).manifest.raw_sha256
        for block_size in ZERO_SEQUENCE_BLOCK_SIZES
    }
    negative_hashes = {
        _zero_sequence_payload(block_size=block_size, negative_zero=True).manifest.raw_sha256
        for block_size in ZERO_SEQUENCE_BLOCK_SIZES
    }
    assert len(positive_hashes) == 1
    assert len(negative_hashes) == 1
    assert positive_hashes != negative_hashes


def test_zero_endpoint_threshold_regression_is_stable_in_fresh_processes() -> None:
    expected = _zero_sequence_statuses()
    context = multiprocessing.get_context("spawn")
    for _ in range(4):
        queue = context.Queue()
        process = context.Process(target=_fresh_zero_sequence_worker, args=(queue,))
        process.start()
        observed = queue.get(timeout=30.0)
        process.join(timeout=30.0)
        assert process.exitcode == 0
        assert observed == expected
        process.close()
        queue.close()


def test_payload_manifest_hash_length_shape_role_and_endpoint_mutations_fail_closed() -> None:
    payload = packed.create_packed_interval_payload(
        ((0.0, 0.0), (0.5, 0.5)),
        role="science_free_initial",
        logical_shape=(2,),
        nonnegative=True,
        block_size=1,
        maximum_working_bytes=64,
    )
    mutations = (
        replace(payload, raw_bytes=payload.raw_bytes[:-1]),
        replace(payload, raw_bytes=bytes([payload.raw_bytes[0] ^ 1]) + payload.raw_bytes[1:]),
        replace(payload, manifest=replace(payload.manifest, logical_shape=(3,))),
        replace(payload, manifest=replace(payload.manifest, array_shape=(1, 4))),
        replace(payload, manifest=replace(payload.manifest, state_count=3)),
        replace(payload, manifest=replace(payload.manifest, raw_byte_length=16)),
        replace(payload, manifest=replace(payload.manifest, role="prospective_control")),
        replace(payload, manifest=replace(payload.manifest, raw_sha256="f" * 64)),
        replace(payload, manifest=replace(payload.manifest, nonnegative=1)),
        replace(payload, manifest=replace(payload.manifest, block_size=True)),
    )
    for mutation in mutations:
        with pytest.raises(packed.PackedF0Failure):
            packed.validate_packed_interval_payload(mutation)

    invalid_pairs = (
        ((-0.0, 0.0),),
        ((0.0, -0.0),),
        ((math.nan, 1.0),),
        ((0.0, math.inf),),
        ((1.0, 0.0),),
        ((-1.0, 0.0),),
    )
    for pairs in invalid_pairs:
        with pytest.raises(packed.PackedF0Failure) as error:
            packed.create_packed_interval_payload(
                pairs,
                role="science_free_initial",
                logical_shape=(1,),
                nonnegative=True,
                block_size=1,
                maximum_working_bytes=64,
            )
        assert error.value.code == packed.HOLD_PACKED_ENDPOINT


def test_strict_builtin_and_nested_dataclass_types_are_required() -> None:
    with pytest.raises(packed.PackedF0Failure):
        packed.create_packed_interval_payload(
            ((np.float64(0.0), 0.0),),
            role="science_free_initial",
            logical_shape=(1,),
            nonnegative=True,
            block_size=1,
            maximum_working_bytes=64,
        )
    with pytest.raises(packed.PackedF0Failure):
        packed.create_packed_interval_payload(
            [(0.0, 0.0)],  # type: ignore[arg-type]
            role="science_free_initial",
            logical_shape=(1,),
            nonnegative=True,
            block_size=1,
            maximum_working_bytes=64,
        )

    payload = packed.create_packed_interval_payload(
        ((0.0, 0.0),),
        role="science_free_initial",
        logical_shape=(1,),
        nonnegative=True,
        block_size=1,
        maximum_working_bytes=64,
    )

    class ManifestSubclass(packed.PackedIntervalManifest):
        __slots__ = ()

    subclass = ManifestSubclass(
        *[getattr(payload.manifest, field.name) for field in dataclasses.fields(payload.manifest)]
    )
    with pytest.raises(packed.PackedF0Failure) as error:
        packed.validate_packed_interval_payload(replace(payload, manifest=subclass))
    assert error.value.code == packed.HOLD_PACKED_NESTED_TYPE


def test_ndarray_subclass_alias_layout_endian_writeability_and_toctou_fail_pre_dispatch() -> None:
    payload = packed.create_packed_interval_payload(
        ((0.0, 0.0), (0.5, 0.5), (1.0, 1.0)),
        role="science_free_initial",
        logical_shape=(3,),
        nonnegative=True,
        block_size=2,
        maximum_working_bytes=128,
    )
    source = packed.load_canonical_packed_intervals(payload)

    class HostileArray(np.ndarray):
        dispatch_count = 0

        def __array_function__(
            self, _function: object, _types: object, _args: object, _kwargs: object
        ) -> object:
            type(self).dispatch_count += 1
            raise AssertionError("array function dispatch occurred")

        def __array_ufunc__(
            self, _ufunc: object, _method: object, *_args: object, **_kwargs: object
        ) -> object:
            type(self).dispatch_count += 1
            raise AssertionError("array ufunc dispatch occurred")

        def __eq__(self, _other: object) -> object:
            type(self).dispatch_count += 1
            raise AssertionError("array equality dispatch occurred")

    hostile = source.intervals.view(HostileArray)
    hostile.setflags(write=False)
    with pytest.raises(packed.PackedF0Failure) as hostile_error:
        packed.validate_canonical_packed_intervals(replace(source, intervals=hostile))
    assert hostile_error.value.code == packed.HOLD_PACKED_ARRAY
    assert HostileArray.dispatch_count == 0

    writable = source.intervals.copy()
    with pytest.raises(packed.PackedF0Failure):
        packed.validate_canonical_packed_intervals(replace(source, intervals=writable))

    owner = source.intervals.copy()
    view = owner.view()
    view.setflags(write=False)
    with pytest.raises(packed.PackedF0Failure):
        packed.validate_canonical_packed_intervals(replace(source, intervals=view))

    fortran = np.asfortranarray(source.intervals)
    fortran.setflags(write=False)
    with pytest.raises(packed.PackedF0Failure):
        packed.validate_canonical_packed_intervals(replace(source, intervals=fortran))

    nonnative = source.intervals.astype(">f8")
    nonnative.setflags(write=False)
    with pytest.raises(packed.PackedF0Failure):
        packed.validate_canonical_packed_intervals(replace(source, intervals=nonnative))

    source.intervals.setflags(write=True)
    source.intervals[1, 0] = np.nextafter(source.intervals[1, 0], math.inf)
    source.intervals.setflags(write=False)
    with pytest.raises(packed.PackedF0Failure) as mutation_error:
        packed.validate_canonical_packed_intervals(source)
    assert mutation_error.value.code == packed.HOLD_PACKED_HASH


def test_streaming_kernel_matches_frozen_small_legacy_exact_ledgers() -> None:
    inputs, contract, legacy_kernel = _packed_problem_from_legacy(block_size=7)
    kernel = packed.build_packed_tensor_kernel(inputs, contract)
    witnesses = _witness_map(kernel)
    assert kernel.rate_fraction == legacy_kernel.rate_fraction
    assert witnesses["delta_q"].value == legacy_kernel.delta_q_exact
    assert witnesses["delta_p_direct"].value == legacy_kernel.delta_p_direct_exact
    assert witnesses["p_coefficient_rounding"].value == (legacy_kernel.p_coefficient_rounding_exact)
    assert witnesses["delta_p_via_q"].value == legacy_kernel.delta_p_via_q_exact
    assert witnesses["delta_p_selected"].value == legacy_kernel.delta_p_exact
    assert witnesses["maximum_qhat_abs_row_sum"].value == (
        legacy_kernel.maximum_qhat_abs_row_sum_exact
    )
    assert witnesses["maximum_killing_uncertainty"].value == (
        legacy_kernel.killing_inf_uncertainty_exact
    )
    np.testing.assert_array_equal(kernel.killing_center, legacy_kernel.killing_center)
    np.testing.assert_array_equal(kernel.diagonal_center, legacy_kernel.diagonal_center)
    np.testing.assert_array_equal(kernel.p_self_center, legacy_kernel.p_self_center)
    for actual, expected in zip(
        kernel.p_forward_center,
        legacy_kernel.p_forward_center,
        strict=True,
    ):
        np.testing.assert_array_equal(actual, expected)
    assert kernel.ledger.construction_exact_pass_count == 2
    assert kernel.ledger.witness_rebind_pass_count == 1
    assert not kernel.ledger.retained_per_state_fraction_objects
    assert kernel.ledger.retained_fraction_witness_count == len(packed.EXPECTED_WITNESS_NAMES)
    assert not kernel.f0_pass
    assert not kernel.science_executed
    assert not kernel.action_roundoff_proof_complete
    assert not kernel.batched_scalar_topology_complete


def test_streaming_block_sizes_preserve_exact_witnesses_and_tie_break_lowest_index() -> None:
    kernels: list[packed.PackedTensorKernel] = []
    shape = (7, 8, 5)
    for block_size in (1, 17, math.prod(shape)):
        inputs, contract = _plain_problem(shape, block_size=block_size)
        kernels.append(packed.build_packed_tensor_kernel(inputs, contract))
    reference = kernels[0]
    reference_witnesses = tuple(
        (witness.name, witness.value, witness.flat_index) for witness in reference.ledger.witnesses
    )
    for kernel in kernels[1:]:
        assert kernel.rate_fraction == reference.rate_fraction
        assert (
            tuple(
                (witness.name, witness.value, witness.flat_index)
                for witness in kernel.ledger.witnesses
            )
            == reference_witnesses
        )
        np.testing.assert_array_equal(kernel.diagonal_center, reference.diagonal_center)
        np.testing.assert_array_equal(kernel.p_self_center, reference.p_self_center)
    assert _witness_map(reference)["maximum_killing_upper"].flat_index == 0
    assert kernels[0].ledger.block_count == math.prod(shape)
    assert kernels[1].ledger.block_count == math.ceil(math.prod(shape) / 17)
    assert kernels[2].ledger.block_count == 1
    assert all(kernel.ledger.covered_state_count == math.prod(shape) for kernel in kernels)
    assert all(not hasattr(kernel.ledger, "blocks") for kernel in kernels)


def test_retained_fraction_count_is_fixed_not_per_state() -> None:
    small_inputs, small_contract = _plain_problem((3, 4, 5), block_size=13)
    medium_inputs, medium_contract = _plain_problem((17, 18, 19), block_size=257)
    small = packed.build_packed_tensor_kernel(small_inputs, small_contract)
    medium = packed.build_packed_tensor_kernel(medium_inputs, medium_contract)
    assert small.states == 60
    assert medium.states == 5_814
    assert _count_retained_fractions(small) == _count_retained_fractions(medium)
    assert _count_retained_fractions(small) <= 1 + len(packed.EXPECTED_WITNESS_NAMES)
    assert small.ledger.retained_fraction_witness_count == (
        medium.ledger.retained_fraction_witness_count
    )


def test_block_halo_p_and_q_actions_match_dense_legacy_without_numpy_roll(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs, kernel_contract, legacy_kernel = _packed_problem_from_legacy(block_size=7)
    kernel = packed.build_packed_tensor_kernel(inputs, kernel_contract)
    rng = np.random.default_rng(20260714)
    state = rng.uniform(0.0, 1.0, size=kernel.states)
    state /= np.sum(state)
    state_payload = _payload_from_values(
        state,
        role="science_free_initial",
        logical_shape=kernel.contract.tensor_shape,
        block_size=kernel.contract.block_size,
        nonnegative=True,
    )
    vector = packed.interval_centres_as_vector(
        packed.load_canonical_packed_intervals(state_payload)
    )
    action_contract = packed.make_block_action_contract(
        kernel.contract.tensor_shape,
        block_size=kernel.contract.block_size,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    expected_p = np.asarray(legacy.explicit_p_csr(legacy_kernel).T @ state).reshape(-1)
    expected_q = np.asarray(legacy.explicit_q_csr(legacy_kernel).T @ state).reshape(-1)

    def forbidden_roll(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("np.roll must not be used by block/halo action")

    original_take = np.take
    original_empty = np.empty
    take_modes: list[object] = []
    boolean_allocation_sizes: list[int] = []

    def monitored_take(*args: object, **kwargs: object) -> object:
        take_modes.append(kwargs.get("mode"))
        return original_take(*args, **kwargs)

    def monitored_empty(*args: object, **kwargs: object) -> np.ndarray:
        result = original_empty(*args, **kwargs)
        if result.dtype == np.dtype(np.bool_):
            boolean_allocation_sizes.append(int(result.size))
        return result

    monkeypatch.setattr(np, "roll", forbidden_roll)
    monkeypatch.setattr(np, "take", monitored_take)
    monkeypatch.setattr(np, "empty", monitored_empty)
    actual_p = packed.block_p_transpose(kernel, vector, action_contract)
    actual_q = packed.block_q_transpose(kernel, vector, action_contract)
    assert float(np.sum(np.abs(actual_p.nominal.values - expected_p))) <= 5.0e-15
    assert float(np.sum(np.abs(actual_q.nominal.values - expected_q))) <= 5.0e-15
    assert np.min(actual_p.nominal.values) >= 0.0
    assert actual_p.scratch_payload_bytes == 65 * kernel.contract.block_size
    assert actual_q.scratch_payload_bytes == actual_p.scratch_payload_bytes
    assert actual_p.block_count == math.ceil(kernel.states / kernel.contract.block_size)
    assert take_modes and set(take_modes) == {"clip"}
    assert boolean_allocation_sizes
    assert max(boolean_allocation_sizes) <= 2 * kernel.contract.block_size
    assert not actual_p.f0_pass


@pytest.mark.parametrize("dimensions", [1, 2, 3])
def test_block_action_boundary_impulses_match_legacy_in_each_dimension(dimensions: int) -> None:
    inputs, kernel_contract, legacy_kernel = _packed_problem_from_legacy(
        block_size=2,
        dimensions=dimensions,
    )
    kernel = packed.build_packed_tensor_kernel(inputs, kernel_contract)
    action_contract = packed.make_block_action_contract(
        kernel.contract.tensor_shape,
        block_size=kernel.contract.block_size,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    for source_index in (0, kernel.states - 1):
        state = np.zeros(kernel.states, dtype=np.float64)
        state[source_index] = 1.0
        vector = packed.interval_centres_as_vector(
            packed.load_canonical_packed_intervals(
                _payload_from_values(
                    state,
                    role="science_free_initial",
                    logical_shape=kernel.contract.tensor_shape,
                    block_size=kernel.contract.block_size,
                    nonnegative=True,
                )
            )
        )
        actual = packed.block_p_transpose(kernel, vector, action_contract)
        expected = np.asarray(legacy.explicit_p_csr(legacy_kernel).T @ state).reshape(-1)
        assert float(np.sum(np.abs(actual.nominal.values - expected))) <= 2.0e-15


def test_action_scratch_payload_depends_on_block_not_full_state_count() -> None:
    results: list[packed.BlockActionResult] = []
    for shape in ((5, 6), (13, 11)):
        inputs, kernel_contract = _plain_problem(shape, block_size=7)
        kernel = packed.build_packed_tensor_kernel(inputs, kernel_contract)
        initial = packed.interval_centres_as_vector(
            packed.load_canonical_packed_intervals(_initial_payload(shape, block_size=7))
        )
        action_contract = packed.make_block_action_contract(
            shape,
            block_size=7,
            maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
        )
        results.append(packed.block_p_transpose(kernel, initial, action_contract))
    assert results[0].nominal.values.size != results[1].nominal.values.size
    assert results[0].scratch_payload_bytes == results[1].scratch_payload_bytes == 65 * 7


def test_action_bytes_are_deterministic_across_block_sizes() -> None:
    shape = (5, 6)
    output_hashes: list[str] = []
    output_values: list[np.ndarray] = []
    for block_size in (1, 7, math.prod(shape) + 11):
        inputs, kernel_contract = _plain_problem(shape, block_size=block_size)
        kernel = packed.build_packed_tensor_kernel(inputs, kernel_contract)
        initial = packed.interval_centres_as_vector(
            packed.load_canonical_packed_intervals(_initial_payload(shape, block_size=block_size))
        )
        action_contract = packed.make_block_action_contract(
            shape,
            block_size=block_size,
            maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
        )
        result = packed.block_p_transpose(kernel, initial, action_contract)
        output_hashes.append(result.nominal.raw_sha256)
        output_values.append(result.nominal.values)
    assert len(set(output_hashes)) == 1
    for values in output_values[1:]:
        np.testing.assert_array_equal(values, output_values[0])


def test_action_rejects_hostile_state_subclass_kernel_mutation_and_contract_mutation() -> None:
    inputs, kernel_contract = _plain_problem((5, 6), block_size=7)
    kernel = packed.build_packed_tensor_kernel(inputs, kernel_contract)
    initial = packed.interval_centres_as_vector(
        packed.load_canonical_packed_intervals(_initial_payload((5, 6), block_size=7))
    )
    action_contract = packed.make_block_action_contract(
        (5, 6),
        block_size=7,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )

    class HostileArray(np.ndarray):
        dispatch_count = 0

        def __array_function__(
            self, _function: object, _types: object, _args: object, _kwargs: object
        ) -> object:
            type(self).dispatch_count += 1
            raise AssertionError("unexpected dispatch")

        def __array_ufunc__(
            self, _ufunc: object, _method: object, *_args: object, **_kwargs: object
        ) -> object:
            type(self).dispatch_count += 1
            raise AssertionError("unexpected dispatch")

    hostile_values = initial.values.view(HostileArray)
    hostile_values.setflags(write=False)
    hostile = replace(initial, values=hostile_values)
    with pytest.raises(packed.PackedF0Failure) as hostile_error:
        packed.block_p_transpose(kernel, hostile, action_contract)
    assert hostile_error.value.code == packed.HOLD_PACKED_ARRAY
    assert HostileArray.dispatch_count == 0

    kernel.p_self_center.setflags(write=True)
    kernel.p_self_center[0] = np.nextafter(kernel.p_self_center[0], math.inf)
    kernel.p_self_center.setflags(write=False)
    with pytest.raises(packed.PackedF0Failure) as kernel_error:
        packed.block_p_transpose(kernel, initial, action_contract)
    assert kernel_error.value.code == packed.HOLD_STREAMING_LEDGER

    inputs, kernel_contract = _plain_problem((5, 6), block_size=7)
    kernel = packed.build_packed_tensor_kernel(inputs, kernel_contract)
    with pytest.raises(packed.PackedF0Failure):
        packed.block_p_transpose(
            kernel,
            initial,
            replace(action_contract, summation_order=list(action_contract.summation_order)),  # type: ignore[arg-type]
        )


def test_streaming_ledger_chains_witness_values_indices_and_caps_fail_closed() -> None:
    inputs, contract = _plain_problem((5, 6), block_size=7)
    kernel = packed.build_packed_tensor_kernel(inputs, contract)
    mutated_ledger = replace(kernel.ledger, source_chain_sha256="f" * 64)
    with pytest.raises(packed.PackedF0Failure) as hash_error:
        packed.validate_packed_tensor_kernel(replace(kernel, ledger=mutated_ledger))
    assert hash_error.value.code == packed.HOLD_STREAMING_LEDGER

    with pytest.raises(packed.PackedF0Failure) as cap_error:
        packed.validate_packed_tensor_kernel(
            replace(
                kernel,
                ledger=replace(kernel.ledger, maximum_working_bytes=1),
            )
        )
    assert cap_error.value.code == packed.HOLD_PACKED_SCHEMA

    names = tuple(witness.name for witness in kernel.ledger.witnesses)
    killing_index = names.index("maximum_killing_upper")
    original_killing = kernel.ledger.witnesses[killing_index]
    for forged_killing in (
        replace(original_killing, value=original_killing.value / 2),
        replace(original_killing, flat_index=1),
    ):
        forged_witnesses = list(kernel.ledger.witnesses)
        forged_witnesses[killing_index] = forged_killing
        forged_ledger = replace(kernel.ledger, witnesses=tuple(forged_witnesses))
        with pytest.raises(packed.PackedF0Failure) as witness_error:
            packed.validate_packed_tensor_kernel(replace(kernel, ledger=forged_ledger))
        assert witness_error.value.code == packed.HOLD_STREAMING_LEDGER

    class WitnessSubclass(packed.ExactWitness):
        __slots__ = ()

    original = kernel.ledger.witnesses[0]
    forged = WitnessSubclass(original.name, original.value, original.flat_index)
    with pytest.raises(packed.PackedF0Failure) as error:
        packed.validate_streaming_exact_ledger(
            replace(
                kernel.ledger,
                witnesses=(forged,) + kernel.ledger.witnesses[1:],
            )
        )
    assert error.value.code == packed.HOLD_STREAMING_LEDGER


def test_streaming_ledger_json_is_constant_size_not_per_block() -> None:
    ledgers: list[packed.StreamingExactLedger] = []
    for shape in ((3, 4, 5), (17, 18, 19)):
        inputs, contract = _plain_problem(shape, block_size=1)
        ledgers.append(packed.build_packed_tensor_kernel(inputs, contract).ledger)
    encoded_lengths = [
        len(
            json.dumps(
                packed._ledger_json(ledger),
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("ascii")
        )
        for ledger in ledgers
    ]
    assert ledgers[0].block_count == 60
    assert ledgers[1].block_count == 5_814
    assert max(encoded_lengths) < 4_096
    assert abs(encoded_lengths[1] - encoded_lengths[0]) < 128


def test_producer_artifact_exposes_no_array_and_same_process_verification_is_forbidden() -> None:
    inputs, kernel_contract = _plain_problem((5, 6), block_size=7)
    initial = _initial_payload((5, 6), block_size=7)
    action_contract = packed.make_block_action_contract(
        (5, 6),
        block_size=7,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    artifact = packed.produce_action_artifact(
        inputs,
        initial,
        kernel_contract,
        action_contract,
    )
    assert not any(
        isinstance(getattr(artifact, field.name), np.ndarray)
        for field in dataclasses.fields(artifact)
    )
    assert type(artifact.action_output_bytes) is bytes
    assert len(artifact.action_output_bytes) == artifact.action_output_byte_length
    assert artifact.status == "PRODUCER_METHOD_ARTIFACT_NOT_AUTHORITY"
    assert not artifact.science_executed
    assert not artifact.f0_pass
    with pytest.raises(packed.PackedF0Failure) as error:
        packed.verify_action_artifact_fresh_process(
            inputs,
            initial,
            kernel_contract,
            action_contract,
            artifact,
        )
    assert error.value.code == packed.HOLD_FRESH_PROCESS


def test_fresh_process_verifier_reconstructs_owned_bytes_and_returns_not_f0_receipt() -> None:
    inputs, kernel_contract = _plain_problem((5, 6), block_size=7)
    initial = _initial_payload((5, 6), block_size=7)
    action_contract = packed.make_block_action_contract(
        (5, 6),
        block_size=7,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    artifact = packed.produce_action_artifact(
        inputs,
        initial,
        kernel_contract,
        action_contract,
    )
    result = _run_fresh_verify(
        inputs,
        initial,
        kernel_contract,
        action_contract,
        artifact,
    )
    assert result[0] == "ok"
    assert result[1] == "PASS_METHOD_REPLAY_ONLY_NOT_F0"
    assert result[2] == os.getpid()
    assert result[2] != result[3]
    assert result[4] is True
    assert result[5] is True
    assert result[6] is False
    assert result[7] is False
    assert result[8] is False
    assert all(type(result[index]) is str and len(result[index]) == 64 for index in (9, 10, 11))


def test_spawn_launcher_ignores_mutated_artifact_pid_and_uses_actual_process_ids() -> None:
    inputs, kernel_contract = _plain_problem((3, 4), block_size=5)
    initial = _initial_payload((3, 4), block_size=5)
    action_contract = packed.make_block_action_contract(
        (3, 4),
        block_size=5,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    artifact = packed.produce_action_artifact(
        inputs,
        initial,
        kernel_contract,
        action_contract,
    )
    mutated_pid = artifact.producer_pid + 1_000_000
    receipt = packed.spawn_verify_action_artifact(
        inputs,
        initial,
        kernel_contract,
        action_contract,
        replace(artifact, producer_pid=mutated_pid),
    )
    assert receipt.producer_pid == os.getpid()
    assert receipt.producer_pid != mutated_pid
    assert receipt.verifier_pid != receipt.producer_pid
    assert receipt.fresh_process


def test_fresh_verifier_rejects_validly_typed_artifact_and_source_byte_mutations() -> None:
    inputs, kernel_contract = _plain_problem((5, 6), block_size=7)
    initial = _initial_payload((5, 6), block_size=7)
    action_contract = packed.make_block_action_contract(
        (5, 6),
        block_size=7,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    artifact = packed.produce_action_artifact(
        inputs,
        initial,
        kernel_contract,
        action_contract,
    )
    mutated_output = bytearray(artifact.action_output_bytes)
    mutated_output[0] ^= 1
    mutated_output_bytes = bytes(mutated_output)
    mutated_artifact = replace(
        artifact,
        action_output_bytes=mutated_output_bytes,
        action_output_sha256=hashlib.sha256(mutated_output_bytes).hexdigest(),
    )
    packed.validate_producer_action_artifact(mutated_artifact)
    assert _run_fresh_verify(
        inputs,
        initial,
        kernel_contract,
        action_contract,
        mutated_artifact,
    ) == ("error", packed.HOLD_REPLAY)

    raw = bytearray(initial.raw_bytes)
    raw[0] ^= 1
    mutated_initial = replace(initial, raw_bytes=bytes(raw))
    with pytest.raises(packed.PackedF0Failure) as error:
        packed.validate_packed_interval_payload(mutated_initial)
    assert error.value.code == packed.HOLD_PACKED_HASH

    mutated_manifest = replace(
        initial.manifest,
        block_size=1,
        maximum_working_bytes=packed.INTERVAL_VALIDATION_SCRATCH_BYTES_PER_STATE,
    )
    mutated_manifest_initial = replace(initial, manifest=mutated_manifest)
    packed.validate_packed_interval_payload(mutated_manifest_initial)
    assert _run_fresh_verify(
        inputs,
        mutated_manifest_initial,
        kernel_contract,
        action_contract,
        artifact,
    ) == ("error", packed.HOLD_REPLAY)


def test_replay_artifact_and_receipt_nested_subclasses_are_rejected() -> None:
    inputs, kernel_contract = _plain_problem((3, 4), block_size=5)
    initial = _initial_payload((3, 4), block_size=5)
    action_contract = packed.make_block_action_contract(
        (3, 4),
        block_size=5,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    artifact = packed.produce_action_artifact(
        inputs,
        initial,
        kernel_contract,
        action_contract,
    )

    class ArtifactSubclass(packed.ProducerActionArtifact):
        __slots__ = ()

    forged = ArtifactSubclass(
        *[getattr(artifact, field.name) for field in dataclasses.fields(artifact)]
    )
    with pytest.raises(packed.PackedF0Failure) as error:
        packed.validate_producer_action_artifact(forged)
    assert error.value.code == packed.HOLD_PACKED_NESTED_TYPE


def test_science_boundary_rejects_control_roles_and_non_science_free_kernel_sources() -> None:
    with pytest.raises(packed.PackedF0Failure) as role_error:
        packed.create_packed_interval_payload(
            ((0.0, 0.0),),
            role="positive_budget_control",
            logical_shape=(1,),
            nonnegative=True,
            block_size=1,
            maximum_working_bytes=64,
        )
    assert role_error.value.code == packed.HOLD_SCIENCE_BOUNDARY

    inputs, contract = _plain_problem((3, 4), block_size=5)
    wrong_role = replace(
        inputs.killing,
        manifest=replace(inputs.killing.manifest, role="science_free_initial"),
    )
    with pytest.raises(packed.PackedF0Failure) as source_error:
        packed.build_packed_tensor_kernel(replace(inputs, killing=wrong_role), contract)
    assert source_error.value.code == packed.HOLD_PACKED_SCHEMA
