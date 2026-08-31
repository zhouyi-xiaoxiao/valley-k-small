from __future__ import annotations

import hashlib
import math
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_interval_action as directed

MAXIMUM_WORKING_BYTES = 2_000_000
MAXIMUM_SCRATCH_BYTES = 2_000_000


def _axis_payload(
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


def _problem(
    shape: tuple[int, ...],
    *,
    periodic: tuple[bool, ...],
    block_size: int,
    rates: tuple[float, ...] | None = None,
    killing: float = 1.0 / 256.0,
) -> tuple[packed.PackedTensorKernel, directed.DirectedActionContract]:
    if rates is None:
        rates = tuple((dimension + 1) / 512.0 for dimension in range(len(shape)))
    axes = tuple(
        _axis_payload(
            f"axis{dimension}",
            size,
            periodic=periodic[dimension],
            block_size=block_size,
            rate=rates[dimension],
        )
        for dimension, size in enumerate(shape)
    )
    killing_payload = packed.create_packed_interval_payload(
        ((killing, killing),) * math.prod(shape),
        role="science_free_killing",
        logical_shape=shape,
        nonnegative=True,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )
    inputs = packed.PackedKernelInputs(axes=axes, killing=killing_payload)
    kernel_contract = packed.KernelBuildContract(
        tensor_shape=shape,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
        uniformization_rate=None,
    )
    kernel = packed.build_packed_tensor_kernel(inputs, kernel_contract)
    action_contract = directed.make_directed_action_contract(
        shape,
        block_size=block_size,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    return kernel, action_contract


def _heterogeneous_problem(
    shape: tuple[int, ...],
    *,
    periodic: tuple[bool, ...],
    block_size: int,
) -> tuple[packed.PackedTensorKernel, directed.DirectedActionContract]:
    axes: list[packed.PackedAxisPayload] = []
    for dimension, size in enumerate(shape):
        forward = [
            float(Fraction((dimension + 1) * (2 * position + 1), 2 ** (10 + dimension)))
            for position in range(size)
        ]
        backward = [
            float(Fraction((dimension + 2) * (3 * position + 2), 2 ** (12 + dimension)))
            for position in range(size)
        ]
        if not periodic[dimension]:
            forward[-1] = 0.0
            backward[0] = 0.0
        name = f"heterogeneous_axis{dimension}"
        axes.append(
            packed.PackedAxisPayload(
                name=name,
                size=size,
                periodic=periodic[dimension],
                forward=packed.create_packed_interval_payload(
                    tuple((value, value) for value in forward),
                    role=f"science_free_axis_{name}_forward",
                    logical_shape=(size,),
                    nonnegative=True,
                    block_size=block_size,
                    maximum_working_bytes=MAXIMUM_WORKING_BYTES,
                ),
                backward=packed.create_packed_interval_payload(
                    tuple((value, value) for value in backward),
                    role=f"science_free_axis_{name}_backward",
                    logical_shape=(size,),
                    nonnegative=True,
                    block_size=block_size,
                    maximum_working_bytes=MAXIMUM_WORKING_BYTES,
                ),
            )
        )
    killing_rows = tuple(
        (
            float(Fraction((index % 7) + 1, 8192)),
            float(Fraction((index % 7) + 1, 8192)),
        )
        for index in range(math.prod(shape))
    )
    inputs = packed.PackedKernelInputs(
        axes=tuple(axes),
        killing=packed.create_packed_interval_payload(
            killing_rows,
            role="science_free_killing",
            logical_shape=shape,
            nonnegative=True,
            block_size=block_size,
            maximum_working_bytes=MAXIMUM_WORKING_BYTES,
        ),
    )
    kernel_contract = packed.KernelBuildContract(
        tensor_shape=shape,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
        uniformization_rate=None,
    )
    kernel = packed.build_packed_tensor_kernel(inputs, kernel_contract)
    action_contract = directed.make_directed_action_contract(
        shape,
        block_size=block_size,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    return kernel, action_contract


def _vector(
    shape: tuple[int, ...],
    *,
    block_size: int,
    pairs: tuple[tuple[float, float], ...],
    nonnegative: bool,
) -> packed.CanonicalPackedIntervals:
    payload = packed.create_packed_interval_payload(
        pairs,
        role="science_free_initial",
        logical_shape=shape,
        nonnegative=nonnegative,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )
    return packed.load_canonical_packed_intervals(payload)


def _fraction_interval_product(
    coefficient: float,
    lower: float,
    upper: float,
) -> tuple[Fraction, Fraction]:
    exact_coefficient = Fraction.from_float(coefficient)
    products = (
        exact_coefficient * Fraction.from_float(lower),
        exact_coefficient * Fraction.from_float(upper),
    )
    return min(products), max(products)


def _fraction_oracle(
    kernel: packed.PackedTensorKernel,
    vector: packed.CanonicalPackedIntervals,
    *,
    operator: str,
) -> tuple[tuple[Fraction, Fraction], ...]:
    self_values = kernel.p_self_center if operator == "P" else kernel.diagonal_center
    forward_values = kernel.p_forward_center if operator == "P" else kernel.forward_center
    backward_values = kernel.p_backward_center if operator == "P" else kernel.backward_center
    shape = kernel.contract.tensor_shape
    strides = tuple(math.prod(shape[dimension + 1 :]) for dimension in range(len(shape)))
    rows: list[tuple[Fraction, Fraction]] = []
    for target in range(kernel.states):
        lower, upper = _fraction_interval_product(
            float(self_values[target]),
            float(vector.intervals[target, 0]),
            float(vector.intervals[target, 1]),
        )
        for dimension, (axis, stride) in enumerate(zip(kernel.axes, strides, strict=True)):
            coordinate = (target // stride) % axis.size
            if coordinate > 0 or axis.periodic:
                source = target - stride if coordinate > 0 else target + (axis.size - 1) * stride
                rate_index = coordinate - 1 if coordinate > 0 else axis.size - 1
                term_lower, term_upper = _fraction_interval_product(
                    float(forward_values[dimension][rate_index]),
                    float(vector.intervals[source, 0]),
                    float(vector.intervals[source, 1]),
                )
                lower += term_lower
                upper += term_upper
            if coordinate < axis.size - 1 or axis.periodic:
                source = (
                    target + stride
                    if coordinate < axis.size - 1
                    else target - (axis.size - 1) * stride
                )
                rate_index = coordinate + 1 if coordinate < axis.size - 1 else 0
                term_lower, term_upper = _fraction_interval_product(
                    float(backward_values[dimension][rate_index]),
                    float(vector.intervals[source, 0]),
                    float(vector.intervals[source, 1]),
                )
                lower += term_lower
                upper += term_upper
        rows.append((lower, upper))
    return tuple(rows)


def _assert_contains_fraction_oracle(
    result: directed.DirectedActionResult,
    oracle: tuple[tuple[Fraction, Fraction], ...],
) -> None:
    assert len(oracle) == result.enclosure.intervals.shape[0]
    for index, (exact_lower, exact_upper) in enumerate(oracle):
        saved_lower = Fraction.from_float(float(result.enclosure.intervals[index, 0]))
        saved_upper = Fraction.from_float(float(result.enclosure.intervals[index, 1]))
        assert saved_lower <= exact_lower, index
        assert saved_upper >= exact_upper, index


def _pairs(shape: tuple[int, ...], *, signed: bool) -> tuple[tuple[float, float], ...]:
    rows = []
    for index in range(math.prod(shape)):
        if signed:
            lower = (index % 7 - 3) / 32.0
            upper = lower + (index % 3 + 1) / 64.0
        else:
            lower = (index % 7 + 1) / 64.0
            upper = lower + (index % 3 + 1) / 128.0
        rows.append((lower, upper))
    return tuple(rows)


def test_contract_binds_frozen_order_sources_backends_block_size_and_memory() -> None:
    shape = (3, 4, 2)
    contract = directed.make_directed_action_contract(
        shape,
        block_size=5,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    stage1 = packed.make_block_action_contract(
        shape,
        block_size=5,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    directed.validate_directed_action_contract(contract)
    assert contract.summation_order == stage1.summation_order
    assert contract.stage1_action_contract_sha256 == packed._action_contract_digest(stage1)
    assert (
        contract.stage1_source_sha256
        == hashlib.sha256(Path(packed.__file__).read_bytes()).hexdigest()
    )
    assert (
        contract.directed_source_sha256
        == hashlib.sha256(Path(directed.__file__).read_bytes()).hexdigest()
    )
    assert contract.workspace_payload_bytes == 81 * 5
    assert contract.validation_scratch_payload_bytes == 2 * 5
    assert contract.runtime_probe_payload_bytes == 4 * 8 * 64
    assert contract.vectorized_rounding_probe_lengths == (16, 24, 64)
    assert contract.output_payload_bytes == 16 * math.prod(shape)
    assert contract.directed_roundoff_stage_complete
    assert contract.science_free


def test_runtime_gate_exercises_contiguous_vectorized_dispatch_lengths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, set[int]] = {"multiply": set(), "add": set(), "nextafter": set()}
    originals = {
        "multiply": np.multiply,
        "add": np.add,
        "nextafter": np.nextafter,
    }

    def monitor(name: str):
        original = originals[name]

        def wrapped(*args: object, **kwargs: object) -> object:
            first = args[0]
            out = kwargs.get("out")
            if type(first) is np.ndarray and first.ndim == 1:
                length = int(first.size)
                if length in directed.VECTORIZED_ROUNDING_PROBE_LENGTHS:
                    assert type(out) is np.ndarray
                    assert out.flags.c_contiguous
                    assert out.flags.owndata
                    observed[name].add(length)
            return original(*args, **kwargs)

        return wrapped

    monkeypatch.setattr(np, "multiply", monitor("multiply"))
    monkeypatch.setattr(np, "add", monitor("add"))
    monkeypatch.setattr(np, "nextafter", monitor("nextafter"))
    directed._validate_binary64_rounding_environment()
    expected = set(directed.VECTORIZED_ROUNDING_PROBE_LENGTHS)
    assert observed == {"multiply": expected, "add": expected, "nextafter": expected}


@pytest.mark.parametrize(
    ("shape", "periodic"),
    [
        ((3,), (False,)),
        ((3, 4), (False, True)),
        ((2, 3, 4), (True, False, True)),
    ],
)
@pytest.mark.parametrize("operator", ["P", "Q"])
def test_fraction_oracle_containment_in_1d_2d_3d(
    shape: tuple[int, ...],
    periodic: tuple[bool, ...],
    operator: str,
) -> None:
    block_size = 5
    kernel, contract = _problem(shape, periodic=periodic, block_size=block_size)
    signed = operator == "Q"
    vector = _vector(
        shape,
        block_size=block_size,
        pairs=_pairs(shape, signed=signed),
        nonnegative=not signed,
    )
    action = directed.directed_p_transpose if operator == "P" else directed.directed_q_transpose
    result = action(kernel, vector, contract)
    _assert_contains_fraction_oracle(
        result,
        _fraction_oracle(kernel, vector, operator=operator),
    )
    assert result.science_executed is False
    assert result.f0_pass is False
    assert result.multiplication_count_per_state == 1 + 2 * len(shape)
    assert result.addition_count_per_state == 2 * len(shape)


def test_signed_q_input_crossing_zero_is_enclosed() -> None:
    shape = (3, 4)
    kernel, contract = _problem(
        shape,
        periodic=(False, True),
        block_size=3,
    )
    pairs = tuple(
        (-0.25, 0.125) if index % 2 == 0 else (-0.0625, 0.375) for index in range(math.prod(shape))
    )
    vector = _vector(
        shape,
        block_size=3,
        pairs=pairs,
        nonnegative=False,
    )
    result = directed.directed_q_transpose(kernel, vector, contract)
    _assert_contains_fraction_oracle(
        result,
        _fraction_oracle(kernel, vector, operator="Q"),
    )
    assert np.any(result.enclosure.intervals[:, 0] < 0.0)
    assert np.any(result.enclosure.intervals[:, 1] > 0.0)


def test_heterogeneous_direction_position_rate_and_killing_fraction_oracle() -> None:
    cases = (
        ((4,), (False,)),
        ((3, 4), (True, False)),
        ((2, 3, 4), (False, True, False)),
    )
    outputs: dict[tuple[tuple[int, ...], str], list[bytes]] = {}
    checked_rows = 0
    for shape, periodic in cases:
        for block_size in (1, 3, 7, 99):
            kernel, contract = _heterogeneous_problem(
                shape,
                periodic=periodic,
                block_size=block_size,
            )
            if block_size == 1:
                assert len(set(float(value) for value in kernel.killing_center)) > 1
                for dimension, axis in enumerate(kernel.axes):
                    forward = tuple(float(value) for value in kernel.forward_center[dimension])
                    backward = tuple(float(value) for value in kernel.backward_center[dimension])
                    assert forward != backward
                    if axis.size >= 3:
                        assert len({value for value in forward if value != 0.0}) > 1
                        assert len({value for value in backward if value != 0.0}) > 1
            for operator, action, signed in (
                ("P", directed.directed_p_transpose, False),
                ("Q", directed.directed_q_transpose, True),
            ):
                vector = _vector(
                    shape,
                    block_size=block_size,
                    pairs=_pairs(shape, signed=signed),
                    nonnegative=not signed,
                )
                result = action(kernel, vector, contract)
                oracle = _fraction_oracle(kernel, vector, operator=operator)
                _assert_contains_fraction_oracle(result, oracle)
                checked_rows += len(oracle)
                outputs.setdefault((shape, operator), []).append(
                    memoryview(result.enclosure.intervals).cast("B").tobytes()
                )
    assert checked_rows == 320
    assert all(rows[0] == rows[1] == rows[2] == rows[3] for rows in outputs.values())


def test_subnormal_products_that_underflow_to_zero_remain_enclosed() -> None:
    minimum_subnormal = float(np.nextafter(np.float64(0.0), np.float64(1.0)))
    assert 0.5 * minimum_subnormal == 0.0
    assert Fraction(1, 2) * Fraction.from_float(minimum_subnormal) > 0
    shape = (2,)
    kernel, contract = _problem(
        shape,
        periodic=(True,),
        block_size=1,
        rates=(minimum_subnormal,),
        killing=0.0,
    )
    vector = _vector(
        shape,
        block_size=1,
        pairs=(
            (minimum_subnormal, 2.0 * minimum_subnormal),
            (2.0 * minimum_subnormal, 3.0 * minimum_subnormal),
        ),
        nonnegative=True,
    )
    for operator, action in (
        ("P", directed.directed_p_transpose),
        ("Q", directed.directed_q_transpose),
    ):
        result = action(kernel, vector, contract)
        _assert_contains_fraction_oracle(
            result,
            _fraction_oracle(kernel, vector, operator=operator),
        )
        assert np.all(np.isfinite(result.enclosure.intervals))


def test_periodic_and_reflecting_boundary_impulse_is_enclosed() -> None:
    shape = (3, 4, 2)
    kernel, contract = _problem(
        shape,
        periodic=(False, True, False),
        block_size=5,
    )
    pairs = [(0.0, 0.0) for _ in range(math.prod(shape))]
    pairs[0] = (1.0, 1.0)
    vector = _vector(
        shape,
        block_size=5,
        pairs=tuple(pairs),
        nonnegative=True,
    )
    result = directed.directed_p_transpose(kernel, vector, contract)
    oracle = _fraction_oracle(kernel, vector, operator="P")
    _assert_contains_fraction_oracle(result, oracle)
    assert oracle[2][0] > 0  # periodic axis-1 forward image
    assert oracle[6][0] > 0  # periodic axis-1 wrapped backward image
    assert oracle[16] == (Fraction(0), Fraction(0))  # no reflecting wrap on axis 0


def test_output_bytes_are_block_size_invariant() -> None:
    shape = (3, 4)
    outputs: dict[str, list[bytes]] = {"P": [], "Q": []}
    for block_size in (1, 5, 99):
        kernel, contract = _problem(
            shape,
            periodic=(False, True),
            block_size=block_size,
        )
        for operator, action, signed in (
            ("P", directed.directed_p_transpose, False),
            ("Q", directed.directed_q_transpose, True),
        ):
            vector = _vector(
                shape,
                block_size=block_size,
                pairs=_pairs(shape, signed=signed),
                nonnegative=not signed,
            )
            result = action(kernel, vector, contract)
            outputs[operator].append(memoryview(result.enclosure.intervals).cast("B").tobytes())
    assert outputs["P"][0] == outputs["P"][1] == outputs["P"][2]
    assert outputs["Q"][0] == outputs["Q"][1] == outputs["Q"][2]


def test_output_is_owned_native_readonly_hash_bound_with_fixed_memory_ledger() -> None:
    shape = (3, 4)
    kernel, contract = _problem(
        shape,
        periodic=(False, True),
        block_size=5,
    )
    vector = _vector(
        shape,
        block_size=5,
        pairs=_pairs(shape, signed=False),
        nonnegative=True,
    )
    result = directed.directed_p_transpose(kernel, vector, contract)
    output = result.enclosure.intervals
    assert type(output) is np.ndarray
    assert output.dtype == np.dtype(np.float64)
    assert output.dtype.isnative
    assert output.flags.c_contiguous
    assert output.flags.aligned
    assert output.flags.owndata
    assert output.base is None
    assert not output.flags.writeable
    assert result.enclosure.raw_sha256 == hashlib.sha256(memoryview(output).cast("B")).hexdigest()
    assert result.memory.output_payload_bytes == 16 * math.prod(shape)
    assert result.memory.workspace_payload_bytes == 81 * 5
    assert result.memory.validation_scratch_payload_bytes == 2 * 5
    assert result.memory.runtime_probe_payload_bytes == 4 * 8 * 64
    assert result.memory.maximum_new_numeric_payload_bytes == 16 * math.prod(shape) + 4 * 8 * 64
    assert result.memory.preowned_kernel_and_input_excluded is True
    assert len(result.consistency_sha256) == 64


def test_directed_enclosure_validator_uses_contiguous_two_row_boolean_scratch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shape = (3, 4, 2)
    kernel, contract = _problem(shape, periodic=(False, True, False), block_size=99)
    vector = _vector(
        shape,
        block_size=99,
        pairs=_pairs(shape, signed=False),
        nonnegative=True,
    )
    result = directed.directed_p_transpose(kernel, vector, contract)
    original_empty = np.empty
    boolean_layouts: list[tuple[tuple[int, ...], tuple[int, ...], bool]] = []

    def monitored_empty(*args: object, **kwargs: object) -> np.ndarray:
        array = original_empty(*args, **kwargs)
        if array.dtype == np.dtype(np.bool_):
            boolean_layouts.append(
                (
                    tuple(int(value) for value in array.shape),
                    tuple(int(value) for value in array.strides),
                    bool(array.flags.c_contiguous),
                )
            )
        return array

    monkeypatch.setattr(np, "empty", monitored_empty)
    directed.validate_canonical_directed_intervals(
        result.enclosure,
        block_size=contract.block_size,
    )
    assert boolean_layouts == [((2, math.prod(shape)), (math.prod(shape), 1), True)]


class _ArraySubclass(np.ndarray):
    pass


class _StringSubclass(str):
    pass


@pytest.mark.parametrize(
    "attack",
    ["writable", "alias", "subclass", "nonnative", "post_hash_mutation"],
)
def test_input_mutation_type_and_alias_attacks_fail_closed(attack: str) -> None:
    shape = (3,)
    kernel, contract = _problem(shape, periodic=(False,), block_size=2)
    vector = _vector(
        shape,
        block_size=2,
        pairs=_pairs(shape, signed=False),
        nonnegative=True,
    )
    if attack == "writable":
        attacked_array = vector.intervals.copy()
    elif attack == "alias":
        attacked_array = vector.intervals.view()
    elif attack == "subclass":
        attacked_array = vector.intervals.view(_ArraySubclass)
    elif attack == "nonnative":
        attacked_array = np.empty(vector.intervals.shape, dtype=">f8")
        attacked_array[:] = vector.intervals
        attacked_array.setflags(write=False)
    else:
        attacked_array = vector.intervals.copy()
        attacked_array.setflags(write=False)
        attacked = replace(vector, intervals=attacked_array)
        attacked_array.setflags(write=True)
        attacked_array[0, 0] += 1.0
        attacked_array.setflags(write=False)
        with pytest.raises(packed.PackedF0Failure):
            directed.directed_p_transpose(kernel, attacked, contract)
        return
    attacked = replace(vector, intervals=attacked_array)
    with pytest.raises(packed.PackedF0Failure):
        directed.directed_p_transpose(kernel, attacked, contract)


@pytest.mark.parametrize(
    "attack",
    ["writable", "alias", "subclass", "nonnative", "raw_mutation"],
)
def test_result_mutation_type_and_alias_attacks_fail_closed(attack: str) -> None:
    shape = (3,)
    kernel, contract = _problem(shape, periodic=(False,), block_size=2)
    vector = _vector(
        shape,
        block_size=2,
        pairs=_pairs(shape, signed=False),
        nonnegative=True,
    )
    result = directed.directed_p_transpose(kernel, vector, contract)
    if attack == "writable":
        attacked_array = result.enclosure.intervals.copy()
    elif attack == "alias":
        attacked_array = result.enclosure.intervals.view()
    elif attack == "subclass":
        attacked_array = result.enclosure.intervals.view(_ArraySubclass)
    elif attack == "nonnative":
        attacked_array = np.empty(result.enclosure.intervals.shape, dtype=">f8")
        attacked_array[:] = result.enclosure.intervals
        attacked_array.setflags(write=False)
    else:
        attacked_array = result.enclosure.intervals.copy()
        attacked_array[0, 0] = np.nextafter(attacked_array[0, 0], -math.inf)
        attacked_array.setflags(write=False)
    attacked = replace(result, enclosure=replace(result.enclosure, intervals=attacked_array))
    with pytest.raises(packed.PackedF0Failure):
        directed.validate_directed_action_result(
            attacked,
            kernel=kernel,
            vector=vector,
            contract=contract,
        )


@pytest.mark.parametrize(
    "field",
    [
        "stage1_source_sha256",
        "directed_source_sha256",
        "stage1_action_contract_sha256",
        "backend_binding_sha256",
        "backend",
        "stage1_action_backend",
        "runtime_probe_payload_bytes",
        "vectorized_rounding_probe_lengths",
        "summation_order",
        "block_size",
    ],
)
def test_contract_hash_backend_order_and_block_mutations_fail_closed(field: str) -> None:
    contract = directed.make_directed_action_contract(
        (3, 4),
        block_size=5,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    value: object
    if field.endswith("sha256"):
        value = "0" * 64
    elif field == "backend":
        value = "mutated_backend"
    elif field == "stage1_action_backend":
        value = _StringSubclass(contract.stage1_action_backend)
    elif field == "summation_order":
        value = tuple(reversed(contract.summation_order))
    elif field == "vectorized_rounding_probe_lengths":
        value = tuple(reversed(contract.vectorized_rounding_probe_lengths))
    else:
        value = 4
    with pytest.raises(packed.PackedF0Failure):
        directed.validate_directed_action_contract(replace(contract, **{field: value}))


def test_kernel_mutation_and_memory_ledger_mutation_fail_closed() -> None:
    shape = (3,)
    kernel, contract = _problem(shape, periodic=(False,), block_size=2)
    vector = _vector(
        shape,
        block_size=2,
        pairs=_pairs(shape, signed=False),
        nonnegative=True,
    )
    result = directed.directed_p_transpose(kernel, vector, contract)
    bad_memory = replace(result.memory, workspace_payload_bytes=1)
    with pytest.raises(packed.PackedF0Failure):
        directed.validate_directed_action_result(
            replace(result, memory=bad_memory),
            kernel=kernel,
            vector=vector,
            contract=contract,
        )
    kernel.diagonal_center.setflags(write=True)
    kernel.diagonal_center[0] -= 1.0
    kernel.diagonal_center.setflags(write=False)
    with pytest.raises(packed.PackedF0Failure):
        directed.directed_p_transpose(kernel, vector, contract)


def test_result_is_bound_to_actual_input_and_kernel_hashes() -> None:
    shape = (3,)
    kernel, contract = _problem(shape, periodic=(False,), block_size=2)
    vector = _vector(
        shape,
        block_size=2,
        pairs=_pairs(shape, signed=False),
        nonnegative=True,
    )
    result = directed.directed_p_transpose(kernel, vector, contract)
    with pytest.raises(packed.PackedF0Failure):
        directed.validate_directed_action_result(
            replace(result, kernel_replay_sha256="0" * 64),
            kernel=kernel,
            vector=vector,
            contract=contract,
        )
    falsified_input = replace(
        result,
        input_raw_sha256="0" * 64,
        enclosure=replace(result.enclosure, input_raw_sha256="0" * 64),
    )
    with pytest.raises(packed.PackedF0Failure):
        directed.validate_directed_action_result(
            falsified_input,
            kernel=kernel,
            vector=vector,
            contract=contract,
        )


def test_consistency_digest_rejects_simple_array_replacement_and_operator_relabel() -> None:
    shape = (3,)
    kernel, contract = _problem(shape, periodic=(False,), block_size=2)
    vector = _vector(
        shape,
        block_size=2,
        pairs=_pairs(shape, signed=False),
        nonnegative=True,
    )
    result = directed.directed_p_transpose(kernel, vector, contract)

    replacement = np.empty_like(result.enclosure.intervals)
    replacement[:, 0] = -123.0
    replacement[:, 1] = 456.0
    replacement.setflags(write=False)
    replacement_enclosure = replace(
        result.enclosure,
        intervals=replacement,
        raw_sha256=hashlib.sha256(memoryview(replacement).cast("B")).hexdigest(),
    )
    with pytest.raises(packed.PackedF0Failure) as array_error:
        directed.validate_directed_action_result(
            replace(result, enclosure=replacement_enclosure),
            kernel=kernel,
            vector=vector,
            contract=contract,
        )
    assert array_error.value.code == directed.HOLD_DIRECTED_BINDING

    with pytest.raises(packed.PackedF0Failure) as relabel_error:
        directed.validate_directed_action_result(
            replace(
                result,
                operator="Q",
                enclosure=replace(result.enclosure, exact_action_nonnegative=False),
            ),
            kernel=kernel,
            vector=vector,
            contract=contract,
        )
    assert relabel_error.value.code == directed.HOLD_DIRECTED_BINDING


def test_p_rejects_signed_input_and_q_overflow_fails_closed() -> None:
    shape = (2,)
    kernel, contract = _problem(
        shape,
        periodic=(True,),
        block_size=1,
        rates=(2.0,),
        killing=1.0,
    )
    signed = _vector(
        shape,
        block_size=1,
        pairs=((-1.0, 1.0), (-0.5, 0.5)),
        nonnegative=False,
    )
    with pytest.raises(packed.PackedF0Failure) as caught:
        directed.directed_p_transpose(kernel, signed, contract)
    assert caught.value.code == directed.HOLD_DIRECTED_ACTION

    maximum = float(np.finfo(np.float64).max)
    overflowing = _vector(
        shape,
        block_size=1,
        pairs=((maximum, maximum), (maximum, maximum)),
        nonnegative=False,
    )
    with pytest.raises(packed.PackedF0Failure) as caught:
        directed.directed_q_transpose(kernel, overflowing, contract)
    assert caught.value.code == directed.HOLD_DIRECTED_ACTION
