from __future__ import annotations

import dataclasses
import inspect
import math
import time
import types
from fractions import Fraction

import numpy as np
import pytest
import rate_defined_tensor_f0_batched_scalar_uniformization_v1 as batched
import rate_defined_tensor_f0_compiled_power_stream_v1 as compiled


def _fixture(
    shape: tuple[int, ...],
    periodic: tuple[bool, ...],
    *,
    block_size: int = 3,
) -> compiled.GenericPackedTensorInput:
    states = math.prod(shape)
    p_self = np.asarray(
        [float(Fraction(1, 4) + Fraction(index % 5, 32)) for index in range(states)],
        dtype=np.float64,
    )
    forward: list[np.ndarray] = []
    backward: list[np.ndarray] = []
    for dimension, (size, is_periodic) in enumerate(
        zip(shape, periodic, strict=True)
    ):
        forward_row = np.asarray(
            [
                float(Fraction(1 + dimension + coordinate, 64))
                for coordinate in range(size)
            ],
            dtype=np.float64,
        )
        backward_row = np.asarray(
            [
                float(Fraction(2 + dimension + coordinate, 64))
                for coordinate in range(size)
            ],
            dtype=np.float64,
        )
        if not is_periodic:
            forward_row[-1] = 0.0
            backward_row[0] = 0.0
        forward.append(forward_row)
        backward.append(backward_row)
    killing = np.asarray(
        [float(Fraction(index + 1, 128)) for index in range(states)],
        dtype=np.float64,
    )
    return compiled.GenericPackedTensorInput(
        tensor_shape=shape,
        periodic=periodic,
        p_self_center=p_self,
        p_forward_center=tuple(forward),
        p_backward_center=tuple(backward),
        killing_center=killing,
        reduction_block_size=block_size,
    )


def _python_kernel(source: compiled.GenericPackedTensorInput) -> object:
    states = math.prod(source.tensor_shape)

    class Kernel:
        pass

    kernel = Kernel()
    kernel.states = states
    kernel.contract = types.SimpleNamespace(
        tensor_shape=source.tensor_shape,
        block_size=source.reduction_block_size,
    )
    kernel.axes = tuple(
        types.SimpleNamespace(size=size, periodic=is_periodic)
        for size, is_periodic in zip(
            source.tensor_shape,
            source.periodic,
            strict=True,
        )
    )
    kernel.p_self_center = source.p_self_center
    kernel.p_forward_center = source.p_forward_center
    kernel.p_backward_center = source.p_backward_center
    kernel.killing_center = source.killing_center
    return kernel


def _python_action(
    source: compiled.GenericPackedTensorInput,
    vector: np.ndarray,
) -> np.ndarray:
    kernel = _python_kernel(source)
    destination = np.empty_like(vector)
    workspace = batched._make_fast_workspace(
        min(kernel.states, source.reduction_block_size)
    )
    batched._fast_p_transpose_into(
        kernel,
        np.array(vector, dtype=np.float64, copy=True),
        destination,
        workspace,
    )
    return destination


def _exact_action(
    source: compiled.GenericPackedTensorInput,
    vector: np.ndarray,
) -> tuple[Fraction, ...]:
    shape = source.tensor_shape
    strides = tuple(
        math.prod(shape[dimension + 1 :])
        for dimension in range(len(shape))
    )
    result: list[Fraction] = []
    for flat in range(math.prod(shape)):
        accumulator = (
            Fraction.from_float(float(vector[flat]))
            * Fraction.from_float(float(source.p_self_center[flat]))
        )
        for dimension, (size, stride, is_periodic) in enumerate(
            zip(shape, strides, source.periodic, strict=True)
        ):
            coordinate = (flat // stride) % size
            if coordinate > 0:
                accumulator += (
                    Fraction.from_float(float(vector[flat - stride]))
                    * Fraction.from_float(
                        float(source.p_forward_center[dimension][coordinate - 1])
                    )
                )
            elif is_periodic:
                accumulator += (
                    Fraction.from_float(
                        float(vector[flat + (size - 1) * stride])
                    )
                    * Fraction.from_float(
                        float(source.p_forward_center[dimension][size - 1])
                    )
                )
            if coordinate + 1 < size:
                accumulator += (
                    Fraction.from_float(float(vector[flat + stride]))
                    * Fraction.from_float(
                        float(source.p_backward_center[dimension][coordinate + 1])
                    )
                )
            elif is_periodic:
                accumulator += (
                    Fraction.from_float(
                        float(vector[flat - (size - 1) * stride])
                    )
                    * Fraction.from_float(
                        float(source.p_backward_center[dimension][0])
                    )
                )
        result.append(accumulator)
    return tuple(result)


@pytest.mark.parametrize(
    ("shape", "periodic"),
    [
        ((5,), (False,)),
        ((4,), (True,)),
        ((2, 3), (False, True)),
        ((2, 3, 2), (True, False, True)),
    ],
)
def test_action_matches_current_python_bytes_and_fraction_enclosure(
    shape: tuple[int, ...],
    periodic: tuple[bool, ...],
) -> None:
    source = _fixture(shape, periodic)
    backend = compiled.build_compiled_power_stream_backend(source)
    vector = np.asarray(
        [
            float(Fraction((index % 7) + 1, 32))
            for index in range(math.prod(shape))
        ],
        dtype=np.float64,
    )
    actual = backend.apply_p_transpose(vector)
    expected_bytes = _python_action(source, vector)
    assert actual.tobytes() == expected_bytes.tobytes()
    exact = _exact_action(source, vector)
    operations = backend.receipt.action_operations
    gamma = compiled._gamma(operations.maximum_dependency_operation_count)
    local_underflow = (
        (4 * len(shape) + 1) * compiled.FLOAT64_ETA
    )
    for nominal, truth in zip(actual, exact, strict=True):
        error = abs(Fraction.from_float(float(nominal)) - truth)
        assert error <= gamma * truth + local_underflow
    assert actual.flags.owndata
    assert actual.base is None
    assert not actual.flags.writeable


def test_reductions_contain_exact_fraction_truth_and_bind_operation_counts() -> None:
    source = _fixture((2, 3), (False, True), block_size=2)
    backend = compiled.build_compiled_power_stream_backend(source)
    vector = np.asarray(
        [float(Fraction(index + 1, 16)) for index in range(6)],
        dtype=np.float64,
    )
    mass = backend.positive_mass(vector)
    dot = backend.killing_dot(vector)
    exact_mass = sum(
        (Fraction.from_float(float(value)) for value in vector),
        Fraction(0),
    )
    exact_dot = sum(
        (
            Fraction.from_float(float(left))
            * Fraction.from_float(float(right))
            for left, right in zip(
                source.killing_center,
                vector,
                strict=True,
            )
        ),
        Fraction(0),
    )
    assert (
        abs(Fraction.from_float(mass.nominal) - exact_mass)
        <= mass.roundoff_radius
    )
    assert (
        abs(Fraction.from_float(dot.nominal) - exact_dot)
        <= dot.roundoff_radius
    )
    assert mass.exact_upper >= exact_mass
    assert dot.exact_upper >= exact_dot
    assert mass.ledger.actual_arithmetic_operation_count == 6
    assert mass.ledger.upstream_enclosure_operation_count == 9
    assert dot.ledger.actual_arithmetic_operation_count == 12
    assert dot.ledger.upstream_enclosure_operation_count == 15
    assert not mass.ledger.changes_upstream_enclosure
    assert not dot.ledger.changes_upstream_enclosure


def test_stream_is_byte_repeatable_matches_python_powers_and_is_rebound() -> None:
    source = _fixture((2, 3, 2), (True, False, True), block_size=4)
    backend = compiled.build_compiled_power_stream_backend(source)
    initial = np.zeros(12, dtype=np.float64)
    initial[5] = 1.0
    first = backend.run_power_stream(initial, maximum_power=11)
    second = backend.run_power_stream(initial, maximum_power=11)
    assert first.receipt == second.receipt
    assert first.mass_by_power.tobytes() == second.mass_by_power.tobytes()
    assert (
        first.killing_dot_by_power.tobytes()
        == second.killing_dot_by_power.tobytes()
    )
    assert first.final_power.tobytes() == second.final_power.tobytes()
    current = initial.copy()
    for _ in range(11):
        current = _python_action(source, current)
    assert first.final_power.tobytes() == current.tobytes()
    compiled.validate_compiled_power_stream_result(backend, first)
    changed = np.array(first.mass_by_power, copy=True)
    changed[0] = np.nextafter(changed[0], math.inf)
    changed.setflags(write=False)
    with pytest.raises(compiled.CompiledPowerStreamFailure):
        compiled.validate_compiled_power_stream_result(
            backend,
            dataclasses.replace(first, mass_by_power=changed),
        )


def test_owned_input_copy_runtime_probe_hashes_and_scope_ceiling() -> None:
    source = _fixture((3,), (False,))
    original_self = source.p_self_center.copy()
    backend = compiled.build_compiled_power_stream_backend(source)
    vector = np.asarray([0.25, 0.5, 0.25], dtype=np.float64)
    before = backend.apply_p_transpose(vector)
    source.p_self_center[:] = 0.0
    after = backend.apply_p_transpose(vector)
    assert before.tobytes() == after.tobytes()
    assert bool(np.any(original_self != source.p_self_center))
    receipt = backend.receipt
    build = receipt.build
    for digest in (
        build.c_source_sha256,
        build.python_wrapper_sha256,
        build.compiler_binary_sha256,
        build.compiler_identity_sha256,
        build.normalized_compile_command_sha256,
        build.post_link_normalization_sha256,
        build.compiled_binary_sha256,
        build.target_identity_sha256,
        receipt.input_binding_sha256,
        receipt.receipt_sha256,
    ):
        assert len(digest) == 64
        int(digest, 16)
    assert build.optimization_level == "O3"
    assert not build.fast_math_enabled
    assert not build.fp_contraction_enabled
    assert not build.unsafe_fp_optimizations_enabled
    assert build.runtime_probe.binary64_layout
    assert build.runtime_probe.tonearest_active
    assert build.runtime_probe.smallest_subnormal_preserved
    assert build.runtime_probe.subnormal_arithmetic_preserved
    assert receipt.input_provenance_classification == (
        compiled.INPUT_PROVENANCE_CLASSIFICATION
    )
    assert not receipt.control_exclusion_proved
    assert not receipt.science_free_proved
    assert not receipt.authorizes_scientific_execution
    assert not receipt.science_executed
    assert not receipt.resource_pass
    assert not receipt.f0_pass
    public_parameters = set(
        inspect.signature(compiled.build_compiled_power_stream_backend).parameters
    )
    assert not any(
        token in name
        for name in public_parameters
        for token in ("path", "control", "selector", "budget")
    )


def test_subnormal_is_preserved_and_invalid_inputs_fail_closed() -> None:
    source = compiled.GenericPackedTensorInput(
        tensor_shape=(2,),
        periodic=(False,),
        p_self_center=np.asarray([1.0, 1.0], dtype=np.float64),
        p_forward_center=(np.asarray([0.0, 0.0], dtype=np.float64),),
        p_backward_center=(np.asarray([0.0, 0.0], dtype=np.float64),),
        killing_center=np.asarray([1.0, 1.0], dtype=np.float64),
        reduction_block_size=2,
    )
    backend = compiled.build_compiled_power_stream_backend(source)
    smallest = float.fromhex("0x0.0000000000001p-1022")
    vector = np.asarray([smallest, 0.0], dtype=np.float64)
    result = backend.apply_p_transpose(vector)
    assert result[0] == smallest
    assert backend.positive_mass(vector).nominal == smallest
    assert backend.killing_dot(vector).nominal == smallest
    with pytest.raises(compiled.CompiledPowerStreamFailure):
        backend.apply_p_transpose(np.asarray([-1.0, 0.0], dtype=np.float64))
    with pytest.raises(compiled.CompiledPowerStreamFailure):
        backend.run_power_stream(vector, maximum_power=-1)
    with pytest.raises(compiled.CompiledPowerStreamFailure):
        backend.apply_p_transpose(np.asarray([1.0, 2.0, 3.0])[::2])


def test_compiled_binary_is_byte_reproducible_in_fresh_build_directories() -> None:
    first = compiled._compile_artifact()
    first_bytes = first.binary_path.read_bytes()
    compiled._ARTIFACT = None
    second = compiled._compile_artifact()
    second_bytes = second.binary_path.read_bytes()
    assert first_bytes == second_bytes
    assert (
        first.receipt.compiled_binary_sha256
        == second.receipt.compiled_binary_sha256
    )
    assert (
        first.receipt.normalized_compile_command_sha256
        == second.receipt.normalized_compile_command_sha256
    )


def test_100k_neutral_shape_matches_current_python_and_is_materially_faster() -> None:
    shape = (100, 1000)
    states = math.prod(shape)
    source = compiled.GenericPackedTensorInput(
        tensor_shape=shape,
        periodic=(False, False),
        p_self_center=np.full(states, 0.75, dtype=np.float64),
        p_forward_center=(
            np.concatenate(
                (np.full(99, 0.05, dtype=np.float64), np.asarray([0.0]))
            ),
            np.concatenate(
                (np.full(999, 0.025, dtype=np.float64), np.asarray([0.0]))
            ),
        ),
        p_backward_center=(
            np.concatenate(
                (np.asarray([0.0]), np.full(99, 0.05, dtype=np.float64))
            ),
            np.concatenate(
                (np.asarray([0.0]), np.full(999, 0.025, dtype=np.float64))
            ),
        ),
        killing_center=np.full(states, 0.01, dtype=np.float64),
        reduction_block_size=64,
    )
    backend = compiled.build_compiled_power_stream_backend(source)
    initial = np.zeros(states, dtype=np.float64)
    initial[states // 2] = 1.0
    started = time.perf_counter()
    result = backend.run_power_stream(initial, maximum_power=4)
    compiled_seconds = time.perf_counter() - started

    kernel = _python_kernel(source)
    workspace = batched._make_fast_workspace(64)
    current = initial.copy()
    following = np.empty_like(current)
    started = time.perf_counter()
    for _ in range(4):
        batched._fast_p_transpose_into(
            kernel,
            current,
            following,
            workspace,
        )
        current, following = following, current
    python_seconds = time.perf_counter() - started
    assert result.final_power.tobytes() == current.tobytes()
    assert python_seconds / compiled_seconds >= 5.0
    assert result.receipt.resource_pass is False
    assert backend.receipt.resource_pass is False
