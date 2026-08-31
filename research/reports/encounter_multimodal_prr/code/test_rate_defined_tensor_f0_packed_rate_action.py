from __future__ import annotations

import gc
import hashlib
import itertools
import math
import struct
import weakref
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_interval_action as directed
import rate_defined_tensor_f0_packed_rate_action as rate_action

MAXIMUM_WORKING_BYTES = 2_000_000
MAXIMUM_SCRATCH_BYTES = 2_000_000
PROVENANCE = hashlib.sha256(b"declared-method-precondition").hexdigest()


@dataclass(frozen=True)
class AxisBox:
    name: str
    size: int
    periodic: bool
    forward: tuple[tuple[float, float], ...]
    backward: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class SourceBox:
    shape: tuple[int, ...]
    axes: tuple[AxisBox, ...]
    killing: tuple[tuple[float, float], ...]


def _axis_box(
    dimension: int,
    size: int,
    *,
    periodic: bool,
) -> AxisBox:
    forward: list[tuple[float, float]] = []
    backward: list[tuple[float, float]] = []
    for position in range(size):
        forward_value = Fraction((dimension + 1) * (2 * position + 1), 2 ** (9 + dimension))
        backward_value = Fraction((dimension + 2) * (3 * position + 2), 2 ** (11 + dimension))
        forward_width = (
            Fraction(1, 2 ** (13 + dimension))
            if position == 0 and (periodic or position < size - 1)
            else Fraction(0)
        )
        backward_width = (
            Fraction(1, 2 ** (14 + dimension))
            if position == size - 1 and (periodic or position > 0)
            else Fraction(0)
        )
        forward.append((float(forward_value), float(forward_value + forward_width)))
        backward.append((float(backward_value), float(backward_value + backward_width)))
    if not periodic:
        forward[-1] = (0.0, 0.0)
        backward[0] = (0.0, 0.0)
    return AxisBox(
        name=f"heterogeneous_axis{dimension}",
        size=size,
        periodic=periodic,
        forward=tuple(forward),
        backward=tuple(backward),
    )


def _source_box(shape: tuple[int, ...], periodic: tuple[bool, ...]) -> SourceBox:
    axes = tuple(
        _axis_box(dimension, size, periodic=periodic[dimension])
        for dimension, size in enumerate(shape)
    )
    killing = []
    for flat in range(math.prod(shape)):
        lower = Fraction((flat % 5) + 1, 8192)
        # A deliberately larger uncertainty at one row separates the direct
        # and via-Q delta_P branches from the row carrying maximum coefficient
        # rounding; this makes branch swaps observable to the oracle.
        width = Fraction(1, 1024) if flat == 0 else Fraction(0)
        killing.append((float(lower), float(lower + width)))
    return SourceBox(shape=shape, axes=axes, killing=tuple(killing))


def _zero_source_box() -> SourceBox:
    return SourceBox(
        shape=(2,),
        axes=(
            AxisBox(
                name="zero_axis",
                size=2,
                periodic=False,
                forward=((0.0, 0.0), (0.0, 0.0)),
                backward=((0.0, 0.0), (0.0, 0.0)),
            ),
        ),
        killing=((0.0, 0.0), (0.0, 0.0)),
    )


def _subnormal_source_box() -> SourceBox:
    minimum = float(np.nextafter(np.float64(0.0), np.float64(1.0)))
    twice = float(np.float64(2.0) * np.float64(minimum))
    return SourceBox(
        shape=(2,),
        axes=(
            AxisBox(
                name="subnormal_periodic_axis",
                size=2,
                periodic=True,
                forward=((minimum, twice), (minimum, minimum)),
                backward=((minimum, minimum), (minimum, minimum)),
            ),
        ),
        killing=((0.0, minimum), (0.0, 0.0)),
    )


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


def _decode_payload_rows(payload: packed.PackedIntervalPayload) -> tuple[tuple[float, float], ...]:
    assert hashlib.sha256(payload.raw_bytes).hexdigest() == payload.manifest.raw_sha256
    return tuple(
        struct.unpack_from("=dd", payload.raw_bytes, 16 * index)
        for index in range(payload.manifest.state_count)
    )


def _decode_original_source_bytes(
    inputs: packed.PackedKernelInputs,
    shape: tuple[int, ...],
) -> SourceBox:
    return SourceBox(
        shape=shape,
        axes=tuple(
            AxisBox(
                name=axis.name,
                size=axis.size,
                periodic=axis.periodic,
                forward=_decode_payload_rows(axis.forward),
                backward=_decode_payload_rows(axis.backward),
            )
            for axis in inputs.axes
        ),
        killing=_decode_payload_rows(inputs.killing),
    )


def _packed_inputs_from_source(
    source: SourceBox,
    *,
    block_size: int,
) -> packed.PackedKernelInputs:
    axes = tuple(
        packed.PackedAxisPayload(
            name=axis.name,
            size=axis.size,
            periodic=axis.periodic,
            forward=_payload(
                axis.forward,
                role=f"science_free_axis_{axis.name}_forward",
                logical_shape=(axis.size,),
                block_size=block_size,
            ),
            backward=_payload(
                axis.backward,
                role=f"science_free_axis_{axis.name}_backward",
                logical_shape=(axis.size,),
                block_size=block_size,
            ),
        )
        for axis in source.axes
    )
    inputs = packed.PackedKernelInputs(
        axes=axes,
        killing=_payload(
            source.killing,
            role="science_free_killing",
            logical_shape=source.shape,
            block_size=block_size,
        ),
    )
    return inputs


def _problem_from_source(
    source: SourceBox,
    *,
    block_size: int,
    uniformization_rate: Fraction | None = None,
) -> tuple[SourceBox, packed.PackedTensorKernel, rate_action.RateActionContract]:
    inputs = _packed_inputs_from_source(source, block_size=block_size)
    decoded_source = _decode_original_source_bytes(inputs, source.shape)
    kernel_contract = packed.KernelBuildContract(
        tensor_shape=source.shape,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
        uniformization_rate=uniformization_rate,
    )
    kernel = packed.build_packed_tensor_kernel(inputs, kernel_contract)
    directed_contract = directed.make_directed_action_contract(
        source.shape,
        block_size=block_size,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    return (
        decoded_source,
        kernel,
        rate_action.make_rate_action_contract(
            directed_contract,
            maximum_numeric_payload_bytes=MAXIMUM_WORKING_BYTES,
            maximum_total_payload_bytes=MAXIMUM_WORKING_BYTES,
        ),
    )


def _problem(
    shape: tuple[int, ...],
    *,
    periodic: tuple[bool, ...],
    block_size: int,
) -> tuple[SourceBox, packed.PackedTensorKernel, rate_action.RateActionContract]:
    return _problem_from_source(
        _source_box(shape, periodic),
        block_size=block_size,
    )


def _canonical_vector(
    shape: tuple[int, ...],
    values: tuple[float, ...],
    *,
    nonnegative: bool,
) -> packed.CanonicalFloat64Vector:
    array = np.array(values, dtype=np.float64, order="C")
    array.setflags(write=False)
    raw = hashlib.sha256(memoryview(array).cast("B")).hexdigest()
    vector = packed.CanonicalFloat64Vector(
        logical_shape=shape,
        values=array,
        raw_sha256=raw,
        nonnegative=nonnegative,
        source_sha256=hashlib.sha256(b"independent-point-source" + bytes.fromhex(raw)).hexdigest(),
    )
    packed.validate_canonical_vector(vector)
    return vector


def _method_input(
    shape: tuple[int, ...],
    *,
    operator: str,
    radius: float = 1.0 / 32.0,
) -> rate_action.InternalPointBallInput:
    states = math.prod(shape)
    if operator == "P":
        values = tuple(float(Fraction((index % 5) + 1, 64)) for index in range(states))
        nonnegative = True
    else:
        # |c[0]| < e makes c+B_1(e) cross zero even though the point lift is [c,c].
        values = tuple(
            float(Fraction(1, 128)) if index == 0 else float(Fraction((index % 7) - 3, 64))
            for index in range(states)
        )
        nonnegative = False
    return rate_action.make_internal_point_ball_input(
        _canonical_vector(shape, values, nonnegative=nonnegative),
        input_l1_radius_upper=radius,
        radius_provenance_sha256=PROVENANCE,
    )


def _strides(shape: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(math.prod(shape[index + 1 :]) for index in range(len(shape)))


def _target_variables(source: SourceBox) -> tuple[tuple[str, int, int], ...]:
    variables: list[tuple[str, int, int]] = []
    for dimension, axis in enumerate(source.axes):
        for direction, rows in (("forward", axis.forward), ("backward", axis.backward)):
            variables.extend(
                (direction, dimension, position)
                for position, (lower, upper) in enumerate(rows)
                if lower != upper
            )
    variables.extend(
        ("killing", -1, flat)
        for flat, (lower, upper) in enumerate(source.killing)
        if lower != upper
    )
    return tuple(variables)


def _vertex_values(
    source: SourceBox,
    bits: tuple[int, ...],
) -> tuple[
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[Fraction, ...], ...],
    tuple[Fraction, ...],
]:
    selected = dict(zip(_target_variables(source), bits, strict=True))
    forward: list[tuple[Fraction, ...]] = []
    backward: list[tuple[Fraction, ...]] = []
    for dimension, axis in enumerate(source.axes):
        forward.append(
            tuple(
                Fraction.from_float(row[selected.get(("forward", dimension, position), 0)])
                for position, row in enumerate(axis.forward)
            )
        )
        backward.append(
            tuple(
                Fraction.from_float(row[selected.get(("backward", dimension, position), 0)])
                for position, row in enumerate(axis.backward)
            )
        )
    killing = tuple(
        Fraction.from_float(row[selected.get(("killing", -1, flat), 0)])
        for flat, row in enumerate(source.killing)
    )
    return tuple(forward), tuple(backward), killing


def _zero_matrix(states: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(states)] for _ in range(states)]


def _exact_target_q(
    source: SourceBox,
    vertex: tuple[
        tuple[tuple[Fraction, ...], ...],
        tuple[tuple[Fraction, ...], ...],
        tuple[Fraction, ...],
    ],
) -> tuple[tuple[Fraction, ...], ...]:
    forward, backward, killing = vertex
    states = math.prod(source.shape)
    matrix = _zero_matrix(states)
    strides = _strides(source.shape)
    for row in range(states):
        exit_rate = killing[row]
        for dimension, (axis, stride) in enumerate(zip(source.axes, strides, strict=True)):
            coordinate = (row // stride) % axis.size
            f_rate = forward[dimension][coordinate]
            b_rate = backward[dimension][coordinate]
            exit_rate += f_rate + b_rate
            if coordinate < axis.size - 1:
                forward_target = row + stride
            elif axis.periodic:
                forward_target = row - (axis.size - 1) * stride
            else:
                forward_target = None
            if coordinate > 0:
                backward_target = row - stride
            elif axis.periodic:
                backward_target = row + (axis.size - 1) * stride
            else:
                backward_target = None
            if forward_target is not None:
                matrix[row][forward_target] += f_rate
            if backward_target is not None:
                # ``+=`` is essential for periodic size two: both directions
                # can land on the same neighbour.
                matrix[row][backward_target] += b_rate
        matrix[row][row] = -exit_rate
    return tuple(tuple(row) for row in matrix)


def _exact_centre_matrix(
    kernel: packed.PackedTensorKernel,
    *,
    operator: str,
) -> tuple[tuple[Fraction, ...], ...]:
    states = kernel.states
    matrix = _zero_matrix(states)
    strides = _strides(kernel.contract.tensor_shape)
    self_values = kernel.p_self_center if operator == "P" else kernel.diagonal_center
    forward = kernel.p_forward_center if operator == "P" else kernel.forward_center
    backward = kernel.p_backward_center if operator == "P" else kernel.backward_center
    for row in range(states):
        matrix[row][row] = Fraction.from_float(float(self_values[row]))
        for dimension, (axis, stride) in enumerate(zip(kernel.axes, strides, strict=True)):
            coordinate = (row // stride) % axis.size
            if coordinate < axis.size - 1:
                target = row + stride
                matrix[row][target] += Fraction.from_float(float(forward[dimension][coordinate]))
            elif axis.periodic:
                target = row - (axis.size - 1) * stride
                matrix[row][target] += Fraction.from_float(float(forward[dimension][coordinate]))
            if coordinate > 0:
                target = row - stride
                matrix[row][target] += Fraction.from_float(float(backward[dimension][coordinate]))
            elif axis.periodic:
                target = row + (axis.size - 1) * stride
                matrix[row][target] += Fraction.from_float(float(backward[dimension][coordinate]))
    return tuple(tuple(row) for row in matrix)


def _uniformized(
    q: tuple[tuple[Fraction, ...], ...],
    rate: Fraction,
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(
            (Fraction(1) if row == column else Fraction(0)) + q[row][column] / rate
            for column in range(len(q))
        )
        for row in range(len(q))
    )


def _transpose_action(
    matrix: tuple[tuple[Fraction, ...], ...],
    vector: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    return tuple(
        sum((matrix[row][column] * vector[row] for row in range(len(matrix))), Fraction(0))
        for column in range(len(matrix))
    )


def _row_norm(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    return max(sum((abs(value) for value in row), Fraction(0)) for row in matrix)


def _difference(
    left: tuple[tuple[Fraction, ...], ...],
    right: tuple[tuple[Fraction, ...], ...],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(a - b for a, b in zip(left_row, right_row, strict=True))
        for left_row, right_row in zip(left, right, strict=True)
    )


def _ball_extremes(states: int, radius: Fraction) -> tuple[tuple[Fraction, ...], ...]:
    rows = [tuple(Fraction(0) for _ in range(states))]
    for index in range(states):
        for sign in (-1, 1):
            row = [Fraction(0) for _ in range(states)]
            row[index] = sign * radius
            rows.append(tuple(row))
    return tuple(rows)


def _witness(kernel: packed.PackedTensorKernel, name: str) -> Fraction:
    return next(witness.value for witness in kernel.ledger.witnesses if witness.name == name)


def _fraction_lower(value: Fraction) -> float:
    candidate = float(value)
    if Fraction.from_float(candidate) > value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(-math.inf)))
    return candidate


def _fraction_upper(value: Fraction) -> float:
    candidate = float(value)
    if Fraction.from_float(candidate) < value:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    assert Fraction.from_float(candidate) >= value
    return candidate


def _add_up(left: float, right: float) -> float:
    rounded = float(np.add(np.float64(left), np.float64(right)))
    return float(np.nextafter(np.float64(rounded), np.float64(math.inf)))


def _mul_up(left: float, right: float) -> float:
    rounded = float(np.multiply(np.float64(left), np.float64(right)))
    return float(np.nextafter(np.float64(rounded), np.float64(math.inf)))


def _sub_up(left: float, right: float) -> float:
    assert left >= right
    rounded = float(np.subtract(np.float64(left), np.float64(right)))
    return float(np.nextafter(np.float64(rounded), np.float64(math.inf)))


def _independent_nominal_l1_upper(values: np.ndarray) -> float:
    result = 0.0
    for value in values:
        result = _add_up(result, abs(float(value)))
    return result


def _independent_centre_roundoff_upper(
    nominal: np.ndarray,
    enclosure: np.ndarray,
) -> float:
    result = 0.0
    for value, row in zip(nominal, enclosure, strict=True):
        point = float(value)
        lower = float(row[0])
        upper = float(row[1])
        assert lower <= point <= upper
        result = _add_up(result, max(_sub_up(point, lower), _sub_up(upper, point)))
    return result


def _distance_to_box(
    values: tuple[Fraction, ...],
    enclosure: np.ndarray,
) -> Fraction:
    distance = Fraction(0)
    for value, row in zip(values, enclosure, strict=True):
        lower = Fraction.from_float(float(row[0]))
        upper = Fraction.from_float(float(row[1]))
        distance += max(lower - value, Fraction(0), value - upper)
    return distance


def _independent_point_lift(
    state: rate_action.InternalPointBallInput,
    *,
    block_size: int,
) -> packed.CanonicalPackedIntervals:
    rows = tuple(
        (0.0, 0.0) if float(value) == 0.0 else (float(value), float(value))
        for value in state.nominal
    )
    payload = packed.create_packed_interval_payload(
        rows,
        role="science_free_independent_test_point_lift",
        logical_shape=state.logical_shape,
        nonnegative=state.nonnegative_nominal,
        block_size=block_size,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )
    return packed.load_canonical_packed_intervals(payload)


def _centre_float(lower: float, upper: float) -> float:
    centre = float((Fraction.from_float(lower) + Fraction.from_float(upper)) / 2)
    return min(max(centre, lower), upper)


def _interval_radius(lower: float, upper: float, centre: float) -> Fraction:
    point = Fraction.from_float(centre)
    return max(point - Fraction.from_float(lower), Fraction.from_float(upper) - point)


def _independent_uniformization_rate(source: SourceBox) -> Fraction:
    maximum_exit = Fraction(0)
    maximum_centre_exit = Fraction(0)
    strides = _strides(source.shape)
    for flat in range(math.prod(source.shape)):
        kill_lower, kill_upper = source.killing[flat]
        exit_upper = Fraction.from_float(kill_upper)
        centre_exit = Fraction.from_float(_centre_float(kill_lower, kill_upper))
        for axis, stride in zip(source.axes, strides, strict=True):
            coordinate = (flat // stride) % axis.size
            for rows in (axis.forward, axis.backward):
                lower, upper = rows[coordinate]
                exit_upper += Fraction.from_float(upper)
                centre_exit += Fraction.from_float(_centre_float(lower, upper))
        maximum_exit = max(maximum_exit, exit_upper)
        maximum_centre_exit = max(maximum_centre_exit, centre_exit)
    minimum = max(maximum_exit, maximum_centre_exit)
    candidate = float(minimum)
    if Fraction.from_float(candidate) < minimum:
        candidate = float(np.nextafter(np.float64(candidate), np.float64(math.inf)))
    return Fraction.from_float(candidate)


def _independent_exact_witnesses(
    source: SourceBox,
    rate: Fraction,
) -> tuple[tuple[str, Fraction, int], ...]:
    maxima: dict[str, tuple[Fraction, int]] = {
        "maximum_target_exit_upper": (Fraction(0), 0),
        "maximum_center_exit": (Fraction(0), 0),
        "delta_q": (Fraction(0), 0),
        "delta_p_direct": (Fraction(0), 0),
        "p_coefficient_rounding": (Fraction(0), 0),
        "maximum_center_row_sum": (Fraction(0), 0),
        "maximum_qhat_abs_row_sum": (Fraction(0), 0),
        "maximum_killing_upper": (Fraction(0), 0),
        "maximum_killing_uncertainty": (Fraction(0), 0),
    }

    def update(name: str, candidate: Fraction, flat: int) -> None:
        if candidate > maxima[name][0]:
            maxima[name] = candidate, flat

    strides = _strides(source.shape)
    for flat in range(math.prod(source.shape)):
        kill_lower_float, kill_upper_float = source.killing[flat]
        kill_lower = Fraction.from_float(kill_lower_float)
        kill_upper = Fraction.from_float(kill_upper_float)
        kill_centre_float = _centre_float(kill_lower_float, kill_upper_float)
        kill_centre = Fraction.from_float(kill_centre_float)
        rate_lower = Fraction(0)
        rate_upper = Fraction(0)
        rate_centre = Fraction(0)
        off_diagonal_error = Fraction(0)
        p_direct_error = Fraction(0)
        p_rounding = Fraction(0)
        p_row_sum = Fraction(0)
        for dimension, (axis, stride) in enumerate(zip(source.axes, strides, strict=True)):
            coordinate = (flat // stride) % axis.size
            for rows in (axis.forward, axis.backward):
                lower_float, upper_float = rows[coordinate]
                lower = Fraction.from_float(lower_float)
                upper = Fraction.from_float(upper_float)
                centre_float = _centre_float(lower_float, upper_float)
                centre = Fraction.from_float(centre_float)
                p_float = _fraction_lower(centre / rate)
                p_value = Fraction.from_float(p_float)
                rate_lower += lower
                rate_upper += upper
                rate_centre += centre
                off_diagonal_error += _interval_radius(
                    lower_float,
                    upper_float,
                    centre_float,
                )
                p_direct_error += max(
                    p_value - lower / rate,
                    upper / rate - p_value,
                )
                p_rounding += abs(centre / rate - p_value)
                p_row_sum += p_value

        exit_lower = rate_lower + kill_lower
        exit_upper = rate_upper + kill_upper
        centre_exit = rate_centre + kill_centre
        diagonal = Fraction.from_float(_fraction_lower(-centre_exit))
        diagonal_error = max(
            diagonal - (-exit_upper),
            -exit_lower - diagonal,
        )
        q_error = off_diagonal_error + diagonal_error
        self_value = Fraction.from_float(_fraction_lower(Fraction(1) + diagonal / rate))
        target_self_lower = Fraction(1) - exit_upper / rate
        target_self_upper = Fraction(1) - exit_lower / rate
        p_direct_error += max(
            self_value - target_self_lower,
            target_self_upper - self_value,
        )
        p_rounding += abs(Fraction(1) + diagonal / rate - self_value)
        p_row_sum += self_value
        candidates = {
            "maximum_target_exit_upper": exit_upper,
            "maximum_center_exit": centre_exit,
            "delta_q": q_error,
            "delta_p_direct": p_direct_error,
            "p_coefficient_rounding": p_rounding,
            "maximum_center_row_sum": p_row_sum,
            "maximum_qhat_abs_row_sum": -diagonal + rate_centre,
            "maximum_killing_upper": kill_upper,
            "maximum_killing_uncertainty": _interval_radius(
                kill_lower_float,
                kill_upper_float,
                kill_centre_float,
            ),
        }
        for name, candidate in candidates.items():
            update(name, candidate, flat)

    delta_q = maxima["delta_q"][0]
    p_rounding = maxima["p_coefficient_rounding"][0]
    delta_p_via_q = delta_q / rate + p_rounding
    delta_p_selected = min(maxima["delta_p_direct"][0], delta_p_via_q)
    return (
        ("maximum_target_exit_upper", *maxima["maximum_target_exit_upper"]),
        ("maximum_center_exit", *maxima["maximum_center_exit"]),
        ("delta_q", *maxima["delta_q"]),
        ("delta_p_direct", *maxima["delta_p_direct"]),
        ("p_coefficient_rounding", *maxima["p_coefficient_rounding"]),
        ("delta_p_via_q", delta_p_via_q, -1),
        ("delta_p_selected", delta_p_selected, -1),
        ("maximum_center_row_sum", *maxima["maximum_center_row_sum"]),
        ("maximum_qhat_abs_row_sum", *maxima["maximum_qhat_abs_row_sum"]),
        ("maximum_killing_upper", *maxima["maximum_killing_upper"]),
        ("maximum_killing_uncertainty", *maxima["maximum_killing_uncertainty"]),
    )


def _independent_scalar_bounds(
    source: SourceBox,
    kernel: packed.PackedTensorKernel,
    state: rate_action.InternalPointBallInput,
    contract: rate_action.RateActionContract,
    result: rate_action.InternalRateActionState,
    *,
    operator: str,
    rate: Fraction,
) -> tuple[np.ndarray, float, float, float, float, dict[str, float]]:
    nominal_contract = packed.make_block_action_contract(
        source.shape,
        block_size=contract.block_size,
        maximum_scratch_bytes=contract.maximum_scratch_bytes,
    )
    directed_contract = directed.make_directed_action_contract(
        source.shape,
        block_size=contract.block_size,
        maximum_scratch_bytes=contract.maximum_scratch_bytes,
    )
    point_lift = _independent_point_lift(state, block_size=contract.block_size)
    directed_result = (
        directed.directed_p_transpose if operator == "P" else directed.directed_q_transpose
    )(kernel, point_lift, directed_contract)
    independent_vector = _canonical_vector(
        source.shape,
        tuple(float(value) for value in state.nominal),
        nonnegative=state.nonnegative_nominal,
    )
    nominal_result = (packed.block_p_transpose if operator == "P" else packed.block_q_transpose)(
        kernel, independent_vector, nominal_contract
    )
    assert np.array_equal(nominal_result.nominal.values, result.nominal)
    enclosure = directed_result.enclosure.intervals
    nominal_l1 = _independent_nominal_l1_upper(state.nominal)
    centre_roundoff = _independent_centre_roundoff_upper(
        nominal_result.nominal.values,
        enclosure,
    )
    witness_uppers = {
        name: _fraction_upper(value)
        for name, value, _ in _independent_exact_witnesses(source, rate)
    }
    if operator == "P":
        coefficient = _mul_up(witness_uppers["delta_p_selected"], nominal_l1)
        base_radius = _add_up(state.input_l1_radius_upper, coefficient)
    else:
        q_norm = _add_up(
            witness_uppers["maximum_qhat_abs_row_sum"],
            witness_uppers["delta_q"],
        )
        propagated = _mul_up(q_norm, state.input_l1_radius_upper)
        coefficient = _mul_up(witness_uppers["delta_q"], nominal_l1)
        base_radius = _add_up(propagated, coefficient)
    final_radius = _add_up(base_radius, centre_roundoff)
    return (
        enclosure,
        nominal_l1,
        centre_roundoff,
        base_radius,
        final_radius,
        witness_uppers,
    )


def _column_norm(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    return max(
        sum((abs(matrix[row][column]) for row in range(len(matrix))), Fraction(0))
        for column in range(len(matrix))
    )


@pytest.mark.parametrize(
    ("shape", "periodic"),
    [
        ((3,), (False,)),
        ((2, 2), (True, False)),
        ((2, 2, 2), (False, True, False)),
    ],
)
@pytest.mark.parametrize("operator", ["P", "Q"])
@pytest.mark.parametrize("block_selector", ["one", "interior", "large"])
def test_independent_endpoint_vertex_and_l1_ball_fraction_oracle(
    shape: tuple[int, ...],
    periodic: tuple[bool, ...],
    operator: str,
    block_selector: str,
) -> None:
    states = math.prod(shape)
    block_size = {"one": 1, "interior": max(2, states - 1), "large": states + 7}[block_selector]
    source, kernel, contract = _problem(
        shape,
        periodic=periodic,
        block_size=block_size,
    )
    expected_rate = _independent_uniformization_rate(source)
    assert kernel.rate_fraction == expected_rate
    method_input = _method_input(shape, operator=operator)
    action = (
        rate_action._rate_defined_p_transpose
        if operator == "P"
        else rate_action._rate_defined_q_transpose
    )
    result = action(kernel, method_input, contract)
    centre_q = _exact_centre_matrix(kernel, operator="Q")
    c = tuple(Fraction.from_float(float(value)) for value in method_input.nominal)
    d = tuple(Fraction.from_float(float(value)) for value in result.nominal)
    radius = Fraction.from_float(method_input.input_l1_radius_upper)
    saved_radius = Fraction.from_float(result.l1_radius_upper)
    assert c[0] - radius < 0 < c[0] + radius if operator == "Q" else True

    variables = _target_variables(source)
    for bits in itertools.product((0, 1), repeat=len(variables)):
        vertex = _vertex_values(source, bits)
        q = _exact_target_q(source, vertex)
        # Lambda is built once from the whole source box.  It is never selected
        # separately for an endpoint vertex.
        assert max(-q[row][row] for row in range(states)) <= expected_rate
        p = _uniformized(q, expected_rate)
        assert all(value >= 0 for row in p for value in row)
        assert all(sum(row, Fraction(0)) <= 1 for row in p)

        assert _row_norm(_difference(q, centre_q)) <= _witness(kernel, "delta_q")
        assert _row_norm(_difference(p, _exact_centre_matrix(kernel, operator="P"))) <= _witness(
            kernel, "delta_p_selected"
        )
        # The saved row-norm witnesses can be conservative when periodic size
        # two combines forward/backward contributions into one matrix entry.
        assert _row_norm(centre_q) <= _witness(kernel, "maximum_qhat_abs_row_sum")

        target = p if operator == "P" else q
        for perturbation in _ball_extremes(states, radius):
            x = tuple(value + delta for value, delta in zip(c, perturbation, strict=True))
            exact = _transpose_action(target, x)
            distance = sum(
                (abs(value - nominal) for value, nominal in zip(exact, d, strict=True)),
                Fraction(0),
            )
            assert distance <= saved_radius

    assert result.status == rate_action.METHOD_STATUS
    assert result.authoritative is False
    assert result.arrays_exposed is True
    assert result.fresh_process is False
    assert result.science_executed is False
    assert result.f0_pass is False
    assert result.derivation.point_lift_rechecked_after_actions is True
    assert result.derivation.nominal_inside_directed_box is True


def test_round157_z_c_s_two_layer_point_plus_ball_containment() -> None:
    minimum = float(np.nextafter(np.float64(0.0), np.float64(1.0)))
    cases = (
        ("Z", _zero_source_box(), Fraction(1), 1.0 / 32.0),
        ("C", _source_box((2,), (True,)), None, 1.0 / 32.0),
        ("S", _subnormal_source_box(), None, minimum),
    )
    for label, source_fixture, explicit_rate, radius in cases:
        source, kernel, contract = _problem_from_source(
            source_fixture,
            block_size=1,
            uniformization_rate=explicit_rate,
        )
        expected_rate = explicit_rate or _independent_uniformization_rate(source)
        assert kernel.rate_fraction == expected_rate
        states = math.prod(source.shape)
        variables = _target_variables(source)
        for operator in ("P", "Q"):
            state = _method_input(source.shape, operator=operator, radius=radius)
            result = (
                rate_action._rate_defined_p_transpose
                if operator == "P"
                else rate_action._rate_defined_q_transpose
            )(kernel, state, contract)
            enclosure, _, centre_roundoff, base_radius, combined_radius, _ = (
                _independent_scalar_bounds(
                    source,
                    kernel,
                    state,
                    contract,
                    result,
                    operator=operator,
                    rate=expected_rate,
                )
            )
            c = tuple(Fraction.from_float(float(value)) for value in state.nominal)
            d = tuple(Fraction.from_float(float(value)) for value in result.nominal)
            ball_radius = Fraction.from_float(state.input_l1_radius_upper)
            saved_radius = Fraction.from_float(result.l1_radius_upper)
            assert combined_radius == result.l1_radius_upper
            assert Fraction.from_float(_add_up(base_radius, centre_roundoff)) <= saved_radius

            for bits in itertools.product((0, 1), repeat=len(variables)):
                q = _exact_target_q(source, _vertex_values(source, bits))
                p = _uniformized(q, expected_rate)
                if label == "Z":
                    assert q == tuple(
                        tuple(Fraction(0) for _ in range(states)) for _ in range(states)
                    )
                    assert p == tuple(
                        tuple(
                            Fraction(1) if row == column else Fraction(0)
                            for column in range(states)
                        )
                        for row in range(states)
                    )
                target = p if operator == "P" else q
                for perturbation in _ball_extremes(states, ball_radius):
                    x = tuple(value + delta for value, delta in zip(c, perturbation, strict=True))
                    z = _transpose_action(target, x)
                    assert _distance_to_box(z, enclosure) <= Fraction.from_float(base_radius)
                    distance_to_nominal = sum(
                        (abs(value - nominal) for value, nominal in zip(z, d, strict=True)),
                        Fraction(0),
                    )
                    assert distance_to_nominal <= Fraction.from_float(combined_radius)
                    assert Fraction.from_float(combined_radius) <= saved_radius


def test_periodic_size_two_oracle_accumulates_shared_neighbour_and_reuses_axis_vertex() -> None:
    source = _source_box((2, 3), (True, True))
    variables = _target_variables(source)
    bits = tuple(1 for _ in variables)
    forward, backward, _ = _vertex_values(source, bits)
    q = _exact_target_q(source, (forward, backward, _vertex_values(source, bits)[2]))
    # Rows 0 and 1 have the same axis-0 coordinate and therefore reuse exactly
    # one selected rate vertex across tensor-product rows.
    expected = forward[0][0] + backward[0][0]
    assert q[0][3] == expected
    assert q[1][4] == expected


def test_independent_source_reconstruction_matches_all_saved_exact_witnesses() -> None:
    source, kernel, contract = _problem(
        (3, 2),
        periodic=(False, True),
        block_size=4,
    )
    result = rate_action._rate_defined_q_transpose(
        kernel,
        _method_input(source.shape, operator="Q"),
        contract,
    )
    expected_rate = _independent_uniformization_rate(source)
    assert kernel.rate_fraction == expected_rate
    expected = _independent_exact_witnesses(source, expected_rate)
    saved = tuple(
        (
            witness.name,
            Fraction(witness.numerator, witness.denominator),
            witness.flat_index,
        )
        for witness in result.derivation.witnesses
    )
    assert saved == expected
    assert tuple(witness.name for witness in result.derivation.witnesses) == (
        packed.EXPECTED_WITNESS_NAMES
    )
    assert result.derivation.fraction_upper_conversion_count == len(expected)
    expected_adjustments = sum(
        Fraction.from_float(float(value)) < value for _, value, _ in expected
    )
    assert result.derivation.fraction_upper_nextafter_count == expected_adjustments

    values = {name: value for name, value, _ in expected}
    assert values["delta_p_direct"] != values["delta_p_via_q"]
    assert values["delta_p_selected"] == min(
        values["delta_p_direct"],
        values["delta_p_via_q"],
    )

    variables = _target_variables(source)
    row_column_pairs = []
    centre_q = _exact_centre_matrix(kernel, operator="Q")
    for bits in itertools.product((0, 1), repeat=len(variables)):
        error = _difference(
            _exact_target_q(source, _vertex_values(source, bits)),
            centre_q,
        )
        row_column_pairs.append((_row_norm(error), _column_norm(error)))
    assert any(row_norm != column_norm for row_norm, column_norm in row_column_pairs)


def test_independent_whole_box_lambda_and_one_ulp_below_rejection() -> None:
    source = _source_box((3, 2), (False, True))
    inputs = _packed_inputs_from_source(source, block_size=4)
    expected = _independent_uniformization_rate(_decode_original_source_bytes(inputs, source.shape))
    accepted = packed.build_packed_tensor_kernel(
        inputs,
        packed.KernelBuildContract(
            tensor_shape=source.shape,
            block_size=4,
            maximum_working_bytes=MAXIMUM_WORKING_BYTES,
            uniformization_rate=expected,
        ),
    )
    assert accepted.rate_fraction == expected
    below_float = float(np.nextafter(np.float64(float(expected)), np.float64(-math.inf)))
    below = Fraction.from_float(below_float)
    assert below < expected
    with pytest.raises(packed.PackedF0Failure, match=packed.HOLD_RATE):
        packed.build_packed_tensor_kernel(
            inputs,
            packed.KernelBuildContract(
                tensor_shape=source.shape,
                block_size=4,
                maximum_working_bytes=MAXIMUM_WORKING_BYTES,
                uniformization_rate=below,
            ),
        )


def test_contract_reconstructs_nominal_contract_and_binds_three_sources() -> None:
    _, kernel, contract = _problem((3, 2), periodic=(False, True), block_size=2)
    nominal, directed_contract = rate_action._reconstruct_subordinate_contracts(contract)
    assert packed._action_contract_digest(nominal) == contract.stage1_action_contract_sha256
    assert (
        directed.directed_action_contract_sha256(directed_contract)
        == contract.directed_action_contract_sha256
    )
    assert (
        contract.stage1_source_sha256
        == hashlib.sha256(Path(packed.__file__).read_bytes()).hexdigest()
    )
    assert (
        contract.directed_source_sha256
        == hashlib.sha256(Path(directed.__file__).read_bytes()).hexdigest()
    )
    assert (
        contract.composition_source_sha256
        == hashlib.sha256(Path(rate_action.__file__).read_bytes()).hexdigest()
    )
    assert kernel.science_executed is False


def test_numeric_preflight_rejects_before_composition_full_size_allocation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shape = (3, 4)
    directed_contract = directed.make_directed_action_contract(
        shape,
        block_size=5,
        maximum_scratch_bytes=MAXIMUM_SCRATCH_BYTES,
    )
    required = rate_action._required_peak_numeric_payload_bytes(shape, block_size=5)
    required_total = rate_action._required_peak_total_payload_bytes(
        shape,
        block_size=5,
        maximum_subordinate_source_read_payload_bytes=max(
            Path(packed.__file__).stat().st_size,
            Path(directed.__file__).stat().st_size,
        ),
    )
    full_shapes: list[tuple[int, ...]] = []
    original_empty = np.empty

    def tracked_empty(*args: object, **kwargs: object) -> np.ndarray:
        shape_arg = args[0] if args else kwargs.get("shape")
        if type(shape_arg) is tuple and shape_arg in {(12, 2), (12,)}:
            full_shapes.append(shape_arg)
        return original_empty(*args, **kwargs)

    monkeypatch.setattr(np, "empty", tracked_empty)
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_RESOURCE):
        rate_action.make_rate_action_contract(
            directed_contract,
            maximum_numeric_payload_bytes=required - 1,
            maximum_total_payload_bytes=required_total,
        )
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_RESOURCE):
        rate_action.make_rate_action_contract(
            directed_contract,
            maximum_numeric_payload_bytes=required,
            maximum_total_payload_bytes=required_total - 1,
        )
    assert full_shapes == []
    contract = rate_action.make_rate_action_contract(
        directed_contract,
        maximum_numeric_payload_bytes=required,
        maximum_total_payload_bytes=required_total,
    )
    assert contract.state_count == 12
    assert contract.block_capacity == 5
    assert contract.required_peak_numeric_payload_bytes == required
    assert contract.maximum_numeric_payload_bytes == required
    assert contract.required_peak_total_payload_bytes == required_total
    assert contract.maximum_total_payload_bytes == required_total


def test_subordinate_json_token_bound_is_preflighted_before_frozen_kernel_replay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _source_box((2,), (True,))
    source = replace(
        source,
        axes=(replace(source.axes[0], name="x" * 4097),),
    )
    _, kernel, contract = _problem_from_source(source, block_size=1)
    state = _method_input(source.shape, operator="Q")

    def replay_must_not_start(*_: object, **__: object) -> None:
        raise AssertionError("frozen replay started before serialization preflight")

    monkeypatch.setattr(packed, "validate_packed_tensor_kernel", replay_must_not_start)
    with pytest.raises(packed.PackedF0Failure) as failure:
        rate_action._rate_defined_q_transpose(kernel, state, contract)
    assert failure.value.code == rate_action.HOLD_RATE_ACTION_RESOURCE


def test_composition_source_is_rechecked_after_subordinate_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shape = (3,)
    _, kernel, contract = _problem(shape, periodic=(False,), block_size=2)
    state = _method_input(shape, operator="Q")
    changed = False
    original_action = directed.directed_q_transpose
    original_source_sha256 = rate_action._source_sha256

    def mark_changed(*args: object, **kwargs: object) -> directed.DirectedActionResult:
        nonlocal changed
        result = original_action(*args, **kwargs)
        changed = True
        return result

    def attacked_source_sha256(path: str) -> str:
        if changed and path == rate_action.__file__:
            return "0" * 64
        return original_source_sha256(path)

    monkeypatch.setattr(directed, "directed_q_transpose", mark_changed)
    monkeypatch.setattr(rate_action, "_source_sha256", attacked_source_sha256)
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_BINDING):
        rate_action._rate_defined_q_transpose(kernel, state, contract)


def test_point_lift_is_exact_degenerate_and_canonicalizes_both_zero_signs() -> None:
    shape = (3,)
    positive = _canonical_vector(shape, (0.0, 0.25, 0.0), nonnegative=False)
    negative = _canonical_vector(shape, (-0.0, 0.25, -0.0), nonnegative=False)
    assert positive.raw_sha256 != negative.raw_sha256
    states = [
        rate_action.make_internal_point_ball_input(
            vector,
            input_l1_radius_upper=1.0 / 16.0,
            radius_provenance_sha256=PROVENANCE,
        )
        for vector in (positive, negative)
    ]
    lifts = [rate_action._build_point_lift(state, block_size=2) for state in states]
    assert lifts[0][0].manifest.raw_sha256 == lifts[1][0].manifest.raw_sha256
    assert lifts[0][1] != lifts[1][1]  # source-vector provenance remains distinct
    for lift, _ in lifts:
        assert np.array_equal(lift.intervals[:, 0], lift.intervals[:, 1])
        zeros = lift.intervals == 0.0
        assert not bool(np.any(np.signbit(lift.intervals)[zeros]))


def test_point_lift_builder_releases_one_row_scratch_before_two_row_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _method_input((4,), operator="Q")
    original_empty = np.empty
    scratch_refs: list[weakref.ReferenceType[np.ndarray]] = []

    def tracked_empty(*args: object, **kwargs: object) -> np.ndarray:
        array = original_empty(*args, **kwargs)
        if array.dtype == np.dtype(np.bool_) and array.shape == (3,):
            scratch_refs.append(weakref.ref(array))
        return array

    original_validate = rate_action._validate_point_lift_binding

    def checked_validate(*args: object, **kwargs: object) -> None:
        gc.collect()
        assert not any(reference() is not None for reference in scratch_refs)
        original_validate(*args, **kwargs)

    monkeypatch.setattr(np, "empty", tracked_empty)
    monkeypatch.setattr(rate_action, "_validate_point_lift_binding", checked_validate)
    rate_action._build_point_lift(state, block_size=3)


@pytest.mark.parametrize("operator", ["P", "Q"])
def test_frozen_scalar_trace_replays_independently(operator: str) -> None:
    shape = (3, 2)
    source, kernel, contract = _problem(shape, periodic=(False, True), block_size=4)
    expected_rate = _independent_uniformization_rate(source)
    assert kernel.rate_fraction == expected_rate
    state = _method_input(shape, operator=operator)
    result = (
        rate_action._rate_defined_p_transpose
        if operator == "P"
        else rate_action._rate_defined_q_transpose
    )(kernel, state, contract)
    trace = {entry.name: float.fromhex(entry.value_hex) for entry in result.derivation.scalar_trace}
    _, nominal_l1, centre_roundoff, base_radius, output, witnesses = _independent_scalar_bounds(
        source,
        kernel,
        state,
        contract,
        result,
        operator=operator,
        rate=expected_rate,
    )
    assert trace["input_l1_radius_upper"] == state.input_l1_radius_upper
    assert trace["input_nominal_l1_upper"] == nominal_l1
    assert trace["centre_action_roundoff_upper"] == centre_roundoff

    if operator == "P":
        coefficient = _mul_up(witnesses["delta_p_selected"], nominal_l1)
        temporary = _add_up(state.input_l1_radius_upper, coefficient)
        assert coefficient == trace["delta_p_selected_times_nominal_l1"]
        assert temporary == trace["input_radius_plus_coefficient"]
    else:
        q_norm = _add_up(witnesses["maximum_qhat_abs_row_sum"], witnesses["delta_q"])
        propagated = _mul_up(q_norm, state.input_l1_radius_upper)
        coefficient = _mul_up(witnesses["delta_q"], nominal_l1)
        temporary = _add_up(propagated, coefficient)
        assert q_norm == trace["qhat_plus_delta_q"]
        assert propagated == trace["q_norm_times_input_radius"]
        assert coefficient == trace["delta_q_times_nominal_l1"]
        assert temporary == trace["propagated_plus_coefficient"]
    assert temporary == base_radius
    assert output == trace["output_l1_radius_upper"] == result.l1_radius_upper


def test_conservative_simultaneous_lifetime_memory_ledger_for_block_variants() -> None:
    shape = (2, 3, 4)
    states = math.prod(shape)
    for block_size in (1, 7, 99):
        _, kernel, contract = _problem(
            shape,
            periodic=(False, True, False),
            block_size=block_size,
        )
        result = rate_action._rate_defined_q_transpose(
            kernel,
            _method_input(shape, operator="Q"),
            contract,
        )
        ledger = result.memory
        capacity = min(states, block_size)
        source_read = max(
            contract.stage1_source_byte_length,
            contract.directed_source_byte_length,
        )
        input_default = min(states, packed.DEFAULT_VALIDATION_BLOCK_SIZE)
        subordinate_serialization = 131_072
        scalar_binding = max(
            8192,
            4096,
            2048,
            source_read,
            subordinate_serialization,
        )
        assert ledger.point_lift_builder_zero_scratch_payload_bytes == capacity
        assert ledger.input_default_validation_scratch_payload_bytes == input_default
        assert ledger.kernel_interval_validation_scratch_payload_bytes == 2 * capacity
        assert ledger.directed_output_validation_scratch_payload_bytes == 2 * capacity
        assert ledger.nominal_output_validation_scratch_payload_bytes == capacity
        assert ledger.canonical_json_stream_text_payload_bytes == 4096
        assert ledger.canonical_json_stream_encoded_payload_bytes == 4096
        assert ledger.canonical_json_stream_chunk_scratch_payload_bytes == 8192
        assert ledger.maximum_subordinate_serialization_payload_bytes == subordinate_serialization
        assert ledger.subordinate_serialization_is_conservative_bound is True
        assert ledger.preflight_binding_phase_payload_bytes == 8 * states + scalar_binding
        assert ledger.point_lift_build_validate_phase_bytes == 24 * states + max(
            2 * capacity,
            capacity,
            input_default,
            8192,
        )
        assert ledger.directed_action_phase_bytes == 40 * states + max(
            81 * capacity,
            2 * capacity,
            2048,
            source_read,
            2 * capacity,
            2 * capacity,
            subordinate_serialization,
            8192,
        )
        assert ledger.nominal_action_phase_bytes == 48 * states + max(
            65 * capacity,
            2 * capacity,
            capacity,
            subordinate_serialization,
        )
        assert ledger.final_binding_revalidation_phase_bytes == 48 * states + max(
            2 * capacity,
            input_default,
            2 * capacity,
            2 * capacity,
            capacity,
            scalar_binding,
        )
        assert ledger.declared_peak_numeric_payload_bytes == max(
            24 * states + 2 * capacity,
            40 * states + max(81 * capacity, 2 * capacity, 2048),
            48 * states + 65 * capacity,
            48 * states + 2 * capacity,
        )
        assert (
            ledger.required_peak_numeric_payload_bytes
            == ledger.declared_peak_numeric_payload_bytes
            == contract.required_peak_numeric_payload_bytes
        )
        assert ledger.maximum_numeric_payload_bytes == contract.maximum_numeric_payload_bytes
        assert ledger.result_consistency_serialization_payload_bytes == 8192
        assert ledger.result_consistency_phase_payload_bytes == (
            48 * states + ledger.result_consistency_serialization_payload_bytes
        )
        assert ledger.declared_peak_total_payload_bytes == max(
            ledger.preflight_binding_phase_payload_bytes,
            ledger.point_lift_build_validate_phase_bytes,
            ledger.directed_action_phase_bytes,
            ledger.nominal_action_phase_bytes,
            ledger.final_binding_revalidation_phase_bytes,
            ledger.result_consistency_phase_payload_bytes,
        )
        assert (
            ledger.required_peak_total_payload_bytes
            == ledger.declared_peak_total_payload_bytes
            == contract.required_peak_total_payload_bytes
        )
        assert ledger.maximum_total_payload_bytes == contract.maximum_total_payload_bytes
        assert ledger.retained_output_numeric_payload_bytes == 8 * states
        assert (
            ledger.raw_serialization_payload_bytes
            == ledger.result_consistency_serialization_payload_bytes
            == 8192
        )
        assert ledger.full_serialization_payload_materialized is False
        assert ledger.total_payload_is_conservative_upper_bound is True
        assert ledger.production_memory_exact is False


def test_fail_closed_mutations_and_same_process_authority_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shape = (3, 2)
    _, kernel, contract = _problem(shape, periodic=(False, True), block_size=3)
    state = _method_input(shape, operator="Q")
    result = rate_action._rate_defined_q_transpose(kernel, state, contract)

    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_BINDING):
        rate_action.validate_rate_action_contract(
            replace(contract, stage1_action_contract_sha256="0" * 64)
        )
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_RESOURCE):
        rate_action.validate_internal_rate_action_state(
            replace(
                result,
                memory=replace(
                    result.memory,
                    nominal_action_phase_bytes=result.memory.nominal_action_phase_bytes - 1,
                ),
            )
        )
    lowered = float(np.nextafter(result.l1_radius_upper, np.float64(-math.inf)))
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_BINDING):
        rate_action.validate_internal_rate_action_state(
            replace(result, l1_radius_upper=lowered, l1_radius_upper_hex=lowered.hex())
        )
    changed_trace = list(result.derivation.scalar_trace)
    changed_trace[-2] = replace(
        changed_trace[-2],
        value_hex=float(
            np.nextafter(
                np.float64(float.fromhex(changed_trace[-2].value_hex)),
                np.float64(-math.inf),
            )
        ).hex(),
    )
    mutated_derivation = replace(result.derivation, scalar_trace=tuple(changed_trace))
    provisional = replace(result, derivation=mutated_derivation, consistency_sha256="0" * 64)
    forged = replace(
        provisional,
        consistency_sha256=rate_action._result_consistency_sha256(provisional),
    )
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_RADIUS):
        rate_action.validate_internal_rate_action_state(forged)
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_AUTHORITY):
        rate_action.require_fresh_process_rate_action_receipt(result)

    original = directed.directed_q_transpose

    def mutate_after_first_hash(*args: object, **kwargs: object) -> directed.DirectedActionResult:
        produced = original(*args, **kwargs)
        state.nominal.setflags(write=True)
        state.nominal[0] = float(state.nominal[0]) + 1.0 / 1024.0
        state.nominal.setflags(write=False)
        return produced

    monkeypatch.setattr(directed, "directed_q_transpose", mutate_after_first_hash)
    with pytest.raises(packed.PackedF0Failure):
        rate_action._rate_defined_q_transpose(kernel, state, contract)


@pytest.mark.parametrize(
    ("upper", "upper_hex"),
    [
        (math.inf, "inf"),
        (math.nan, "nan"),
        (-1.0, (-1.0).hex()),
        (-0.0, (-0.0).hex()),
        ("not-a-float", "not-a-float"),
    ],
)
def test_mutated_witness_upper_always_returns_stable_hold(
    upper: object,
    upper_hex: str,
) -> None:
    _, kernel, contract = _problem((3,), periodic=(False,), block_size=2)
    result = rate_action._rate_defined_q_transpose(
        kernel,
        _method_input((3,), operator="Q"),
        contract,
    )
    witnesses = list(result.derivation.witnesses)
    witnesses[0] = replace(witnesses[0], upper=upper, upper_hex=upper_hex)
    attacked = replace(
        result,
        derivation=replace(result.derivation, witnesses=tuple(witnesses)),
    )
    with pytest.raises(packed.PackedF0Failure) as failure:
        rate_action.validate_internal_rate_action_state(attacked)
    assert failure.value.code in {
        rate_action.HOLD_RATE_ACTION_BINDING,
        rate_action.HOLD_RATE_ACTION_RADIUS,
    }


@pytest.mark.parametrize(
    "value_hex",
    [
        "invalid-hex",
        "0x1p+999999999999999999999",
        "inf",
        "nan",
        "-0x0.0p+0",
        "-0x1.0p+0",
        "0x1." + "0" * 10_000 + "p+0",
        7,
    ],
)
def test_mutated_scalar_trace_hex_always_returns_stable_hold(value_hex: object) -> None:
    _, kernel, contract = _problem((3,), periodic=(False,), block_size=2)
    result = rate_action._rate_defined_q_transpose(
        kernel,
        _method_input((3,), operator="Q"),
        contract,
    )
    trace = list(result.derivation.scalar_trace)
    trace[0] = replace(trace[0], value_hex=value_hex)
    attacked = replace(
        result,
        derivation=replace(result.derivation, scalar_trace=tuple(trace)),
    )
    with pytest.raises(packed.PackedF0Failure) as failure:
        rate_action.validate_internal_rate_action_state(attacked)
    assert failure.value.code in {
        rate_action.HOLD_RATE_ACTION_BINDING,
        rate_action.HOLD_RATE_ACTION_RADIUS,
    }


def test_coherent_same_process_rehash_remains_possible_and_non_authoritative() -> None:
    _, kernel, contract = _problem((3,), periodic=(False,), block_size=2)
    result = rate_action._rate_defined_q_transpose(
        kernel,
        _method_input((3,), operator="Q"),
        contract,
    )
    changed = np.array(result.nominal, copy=True)
    changed[0] += 1.0 / 1024.0
    changed.setflags(write=False)
    raw = hashlib.sha256(memoryview(changed).cast("B")).hexdigest()
    derivation = replace(result.derivation, nominal_output_raw_sha256=raw)
    provisional = replace(
        result,
        nominal=changed,
        nominal_raw_sha256=raw,
        derivation=derivation,
        consistency_sha256="0" * 64,
    )
    coherently_rehashed = replace(
        provisional,
        consistency_sha256=rate_action._result_consistency_sha256(provisional),
    )
    rate_action.validate_internal_rate_action_state(coherently_rehashed)
    assert coherently_rehashed.authoritative is False
    assert coherently_rehashed.arrays_exposed is True
    assert coherently_rehashed.fresh_process is False


def test_wrong_scalar_types_in_nested_ledgers_fail_with_hold_not_native_exception() -> None:
    _, kernel, contract = _problem((3,), periodic=(False,), block_size=2)
    result = rate_action._rate_defined_q_transpose(
        kernel,
        _method_input((3,), operator="Q"),
        contract,
    )
    attacks = (
        replace(result, memory=replace(result.memory, state_count="3")),
        replace(
            result,
            derivation=replace(result.derivation, block_size="2"),
        ),
    )
    for attacked in attacks:
        with pytest.raises(packed.PackedF0Failure):
            rate_action.validate_internal_rate_action_state(attacked)


@pytest.mark.parametrize("bad_operator", [[], {}], ids=["list", "dict"])
def test_unhashable_result_operator_fails_with_stable_hold(bad_operator: object) -> None:
    _, kernel, contract = _problem((3,), periodic=(False,), block_size=2)
    result = rate_action._rate_defined_q_transpose(
        kernel,
        _method_input((3,), operator="Q"),
        contract,
    )
    with pytest.raises(packed.PackedF0Failure) as failure:
        rate_action.validate_internal_rate_action_state(replace(result, operator=bad_operator))
    assert failure.value.code == rate_action.HOLD_RATE_ACTION_BINDING


def test_array_valued_string_fields_and_nested_names_fail_with_stable_hold() -> None:
    _, kernel, contract = _problem((3,), periodic=(False,), block_size=2)
    state = _method_input((3,), operator="Q")
    result = rate_action._rate_defined_q_transpose(kernel, state, contract)
    array_value = np.array(["x", "y"])
    witnesses = list(result.derivation.witnesses)
    witnesses[0] = replace(witnesses[0], name=array_value)
    trace = list(result.derivation.scalar_trace)
    trace[0] = replace(trace[0], name=array_value)
    attacks = (
        replace(result, schema=array_value),
        replace(
            result,
            derivation=replace(result.derivation, witnesses=tuple(witnesses)),
        ),
        replace(
            result,
            derivation=replace(result.derivation, scalar_trace=tuple(trace)),
        ),
    )
    for attacked in attacks:
        with pytest.raises(packed.PackedF0Failure):
            rate_action.validate_internal_rate_action_state(attacked)
    with pytest.raises(packed.PackedF0Failure):
        rate_action.validate_internal_point_ball_input(replace(state, status=array_value))
    with pytest.raises(packed.PackedF0Failure):
        rate_action.validate_rate_action_contract(replace(contract, runtime=array_value))


def test_pathological_witness_integer_fails_before_decimal_json_conversion() -> None:
    _, kernel, contract = _problem((3,), periodic=(False,), block_size=2)
    result = rate_action._rate_defined_q_transpose(
        kernel,
        _method_input((3,), operator="Q"),
        contract,
    )
    witnesses = list(result.derivation.witnesses)
    # More than 4,300 decimal digits: CPython's default integer-to-string guard
    # would raise natively if the bounded prewalk did not run before JSONEncoder.
    witnesses[0] = replace(witnesses[0], numerator=10**5000)
    attacked = replace(
        result,
        derivation=replace(result.derivation, witnesses=tuple(witnesses)),
    )
    with pytest.raises(packed.PackedF0Failure) as validation_failure:
        rate_action.validate_internal_rate_action_state(attacked)
    assert validation_failure.value.code == rate_action.HOLD_RATE_ACTION_BINDING
    with pytest.raises(packed.PackedF0Failure) as digest_failure:
        rate_action._result_consistency_sha256(attacked)
    assert digest_failure.value.code == rate_action.HOLD_RATE_ACTION_RESOURCE


@pytest.mark.parametrize(
    "error_type",
    [ValueError, OverflowError, TypeError, UnicodeError],
)
def test_json_iterator_native_errors_are_wrapped_as_stable_hold(
    monkeypatch: pytest.MonkeyPatch,
    error_type: type[Exception],
) -> None:
    def fail_iterencode(*_: object, **__: object) -> object:
        raise error_type("forced JSON iterator failure")

    monkeypatch.setattr(rate_action.json.JSONEncoder, "iterencode", fail_iterencode)
    with pytest.raises(packed.PackedF0Failure) as failure:
        rate_action._canonical_json_digest({"bounded": 1})
    assert failure.value.code == rate_action.HOLD_RATE_ACTION_RESOURCE


def test_negative_zero_radius_signed_p_and_noncanonical_sources_fail_closed() -> None:
    shape = (3,)
    _, kernel, contract = _problem(shape, periodic=(False,), block_size=2)
    signed = _canonical_vector(shape, (-0.25, 0.125, 0.25), nonnegative=False)
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_RADIUS):
        rate_action.make_internal_point_ball_input(
            signed,
            input_l1_radius_upper=-0.0,
            radius_provenance_sha256=PROVENANCE,
        )
    state = rate_action.make_internal_point_ball_input(
        signed,
        input_l1_radius_upper=0.0,
        radius_provenance_sha256=PROVENANCE,
    )
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_POINT_LIFT):
        rate_action._rate_defined_p_transpose(kernel, state, contract)

    payload = packed.create_packed_interval_payload(
        ((0.0, 0.0), (0.125, 0.125), (0.0, 0.0)),
        role="science_free_negative_zero_attack",
        logical_shape=shape,
        nonnegative=True,
        block_size=2,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )
    raw = bytearray(payload.raw_bytes)
    struct.pack_into("=d", raw, 0, -0.0)
    raw_bytes = bytes(raw)
    attacked = replace(
        payload,
        manifest=replace(
            payload.manifest,
            raw_sha256=hashlib.sha256(raw_bytes).hexdigest(),
        ),
        raw_bytes=raw_bytes,
    )
    with pytest.raises(packed.PackedF0Failure, match=packed.HOLD_PACKED_ENDPOINT):
        packed.load_canonical_packed_intervals(attacked)


def test_centre_nominal_escape_is_rejected_even_with_self_consistent_nominal_hash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shape = (3,)
    _, kernel, contract = _problem(shape, periodic=(False,), block_size=2)
    state = _method_input(shape, operator="P")
    original_directed = directed.directed_p_transpose
    original_nominal = packed.block_p_transpose
    saved: dict[str, directed.DirectedActionResult] = {}

    def capture(*args: object, **kwargs: object) -> directed.DirectedActionResult:
        output = original_directed(*args, **kwargs)
        saved["directed"] = output
        return output

    def escape(*args: object, **kwargs: object) -> packed.BlockActionResult:
        output = original_nominal(*args, **kwargs)
        values = np.array(output.nominal.values, copy=True)
        values[0] = np.nextafter(
            saved["directed"].enclosure.intervals[0, 1],
            np.float64(math.inf),
        )
        values.setflags(write=False)
        raw = hashlib.sha256(memoryview(values).cast("B")).hexdigest()
        nominal = replace(output.nominal, values=values, raw_sha256=raw)
        return replace(output, nominal=nominal)

    monkeypatch.setattr(directed, "directed_p_transpose", capture)
    monkeypatch.setattr(packed, "block_p_transpose", escape)
    with pytest.raises(packed.PackedF0Failure, match=rate_action.HOLD_RATE_ACTION_CENTRE):
        rate_action._rate_defined_p_transpose(kernel, state, contract)


def test_subnormal_source_and_324_digit_witness_serialize_within_fixed_cap() -> None:
    source, kernel, contract = _problem_from_source(
        _subnormal_source_box(),
        block_size=1,
    )
    minimum = float(np.nextafter(np.float64(0.0), np.float64(1.0)))
    assert source.killing[0][1] == minimum
    assert 0.0 < source.axes[0].forward[0][0] < np.finfo(np.float64).tiny
    expected_rate = _independent_uniformization_rate(source)
    assert kernel.rate_fraction == expected_rate
    result = rate_action._rate_defined_q_transpose(
        kernel,
        _method_input(source.shape, operator="Q", radius=minimum),
        contract,
    )
    denominators = tuple(witness.denominator for witness in result.derivation.witnesses)
    assert max(denominator.bit_length() for denominator in denominators) >= 1075
    assert max(len(str(denominator)) for denominator in denominators) >= 324
    assert result.memory.canonical_json_stream_text_payload_bytes == 4096
    assert result.memory.canonical_json_stream_encoded_payload_bytes == 4096
    assert result.memory.canonical_json_stream_chunk_scratch_payload_bytes == 8192
    rate_action.validate_internal_rate_action_state(result)


def test_subnormal_point_and_zero_radius_remain_finite_and_nonpromoting() -> None:
    shape = (2,)
    _, kernel, contract = _problem(shape, periodic=(True,), block_size=1)
    minimum = float(np.nextafter(np.float64(0.0), np.float64(1.0)))
    state = rate_action.make_internal_point_ball_input(
        _canonical_vector(shape, (minimum, -minimum), nonnegative=False),
        input_l1_radius_upper=0.0,
        radius_provenance_sha256=PROVENANCE,
    )
    result = rate_action._rate_defined_q_transpose(kernel, state, contract)
    assert math.isfinite(result.l1_radius_upper)
    assert result.l1_radius_upper > 0.0
    assert result.science_executed is False
    assert result.f0_pass is False
