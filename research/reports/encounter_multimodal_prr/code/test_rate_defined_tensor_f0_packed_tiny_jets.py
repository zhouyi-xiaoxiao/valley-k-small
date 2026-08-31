from __future__ import annotations

import ast
import itertools
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import rate_defined_tensor_f0_packed_target_uniformization as target_uniformization
import rate_defined_tensor_f0_packed_tiny_jets as tiny_jets
from test_rate_defined_tensor_f0_packed_rate_action import (
    SourceBox,
    _exact_centre_matrix,
    _exact_target_q,
    _problem_from_source,
    _source_box,
    _target_variables,
    _transpose_action,
)
from test_rate_defined_tensor_f0_packed_target_uniformization import _component_box
from test_rate_defined_tensor_f0_packed_uniformization import _problem


def _bound_target(
    kernel: object,
    contract: object,
    rows: tuple[tuple[float, float], ...],
) -> target_uniformization.CertifiedTargetBall:
    initial = target_uniformization.make_initial_target_ball(_component_box(rows))
    return target_uniformization.target_uniformize_transpose(
        kernel,
        initial,
        contract,
        time=Fraction(0),
        tail_tolerance=Fraction(1, 2**36),
    ).target


def _fraction_vector(values: np.ndarray) -> tuple[Fraction, ...]:
    return tuple(Fraction.from_float(float(value)) for value in values)


def _assert_state_contains(
    exact: tuple[Fraction, ...],
    state: tiny_jets.TinyQJetState,
) -> None:
    centre = _fraction_vector(state.nominal)
    distance = sum(
        (abs(left - right) for left, right in zip(exact, centre, strict=True)),
        Fraction(0),
    )
    assert distance <= state.l1_radius_exact_upper


def _selected_vertex(
    source: SourceBox,
    levels: tuple[int, ...],
) -> tuple[
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[Fraction, ...], ...],
    tuple[Fraction, ...],
]:
    selected = dict(zip(_target_variables(source), levels, strict=True))

    def choose(row: tuple[float, float], key: tuple[str, int, int]) -> Fraction:
        lower = Fraction.from_float(row[0])
        upper = Fraction.from_float(row[1])
        level = selected.get(key, 0)
        if level == 0:
            return lower
        if level == 1:
            return (lower + upper) / 2
        if level == 2:
            return upper
        raise AssertionError("invalid local test level")

    forward = tuple(
        tuple(
            choose(row, ("forward", dimension, position))
            for position, row in enumerate(axis.forward)
        )
        for dimension, axis in enumerate(source.axes)
    )
    backward = tuple(
        tuple(
            choose(row, ("backward", dimension, position))
            for position, row in enumerate(axis.backward)
        )
        for dimension, axis in enumerate(source.axes)
    )
    killing = tuple(choose(row, ("killing", -1, flat)) for flat, row in enumerate(source.killing))
    return forward, backward, killing


def test_fixed_two_state_fraction_powers_and_killing_jets() -> None:
    kernel, _, contract = _problem(killing=(0.125, 0.25))
    target = _bound_target(kernel, contract, ((0.25, 0.25), (0.75, 0.75)))
    result = tiny_jets.compute_tiny_q_jets(kernel, target, contract)

    q = _exact_centre_matrix(kernel, operator="Q")
    killing = tuple(Fraction.from_float(float(value)) for value in kernel.killing_center)
    exact = (Fraction(1, 4), Fraction(3, 4))
    for order in range(5):
        _assert_state_contains(exact, result.states[order])
        if order <= 3:
            observable = sum(
                (coefficient * value for coefficient, value in zip(killing, exact, strict=True)),
                Fraction(0),
            )
            interval = result.observable_jets[order]
            assert interval.lower <= observable <= interval.upper
        if order >= 2:
            observable = sum(
                (coefficient * value for coefficient, value in zip(killing, exact, strict=True)),
                Fraction(0),
            )
            assert abs(observable) <= result.magnitude_bounds[order - 2].upper
        if order < 4:
            exact = _transpose_action(q, exact)


def test_periodic_size_two_global_rate_samples_and_initial_targets_are_enclosed() -> None:
    source = _source_box((2,), (True,))
    _, kernel, contract = _problem_from_source(source, block_size=2)
    target = _bound_target(kernel, contract, ((0.125, 0.25), (0.625, 0.875)))
    result = tiny_jets.compute_tiny_q_jets(kernel, target, contract)
    variables = _target_variables(source)

    # Lower/mid/upper samples are an exact independent stress grid.  For
    # repeated Q powers they are not claimed to exhaust the continuous box;
    # the full-box guarantee comes from the operator-norm recurrence.
    for levels in itertools.product((0, 1, 2), repeat=len(variables)):
        vertex = _selected_vertex(source, levels)
        q = _exact_target_q(source, vertex)
        killing = vertex[2]
        for first_mass in (Fraction(1, 8), Fraction(3, 16), Fraction(1, 4)):
            exact = (first_mass, Fraction(1) - first_mass)
            for order in range(5):
                _assert_state_contains(exact, result.states[order])
                observable = sum(
                    (
                        coefficient * value
                        for coefficient, value in zip(killing, exact, strict=True)
                    ),
                    Fraction(0),
                )
                if order <= 3:
                    interval = result.observable_jets[order]
                    assert interval.lower <= observable <= interval.upper
                if order >= 2:
                    assert abs(observable) <= result.magnitude_bounds[order - 2].upper
                if order < 4:
                    exact = _transpose_action(q, exact)

    # In a periodic two-state axis both directions land on the same neighbour.
    selected = _selected_vertex(source, tuple(2 for _ in variables))
    q = _exact_target_q(source, selected)
    assert q[0][1] == selected[0][0][0] + selected[1][0][0]


def test_propagated_target_rejects_a_different_kernel() -> None:
    first_kernel, _, first_contract = _problem(killing=(0.125, 0.25))
    target = _bound_target(
        first_kernel,
        first_contract,
        ((0.25, 0.25), (0.75, 0.75)),
    )
    second_kernel, _, second_contract = _problem(
        forward=(0.25, 0.0),
        backward=(0.0, 0.125),
        killing=(0.125, 0.25),
    )
    with pytest.raises(tiny_jets.TinyQJetFailure, match="fixed kernel"):
        tiny_jets.compute_tiny_q_jets(second_kernel, target, second_contract)


def test_scalar_or_chain_mutations_fail_structural_revalidation() -> None:
    kernel, _, contract = _problem(killing=(0.125, 0.25))
    target = _bound_target(kernel, contract, ((0.25, 0.25), (0.75, 0.75)))
    result = tiny_jets.compute_tiny_q_jets(kernel, target, contract)
    first = result.observable_jets[0]
    changed_observable = replace(first, lower=first.lower - 1)
    with pytest.raises(tiny_jets.TinyQJetFailure):
        tiny_jets.validate_tiny_q_jets_structure_only(
            replace(
                result,
                observable_jets=(changed_observable, *result.observable_jets[1:]),
            ),
            kernel=kernel,
            target=target,
            contract=contract,
        )
    with pytest.raises(tiny_jets.TinyQJetFailure):
        tiny_jets.validate_tiny_q_jets_structure_only(
            replace(result, tiny_q_jets_complete=False),
            kernel=kernel,
            target=target,
            contract=contract,
        )


def test_method_scope_flags_dependency_bindings_and_local_import_surface() -> None:
    kernel, _, contract = _problem(killing=(0.125, 0.25))
    target = _bound_target(kernel, contract, ((0.25, 0.25), (0.75, 0.75)))
    result = tiny_jets.compute_tiny_q_jets(kernel, target, contract)
    assert tuple(state.order for state in result.states) == (0, 1, 2, 3, 4)
    assert tuple(jet.order for jet in result.observable_jets) == (0, 1, 2, 3)
    assert tuple(bound.order for bound in result.magnitude_bounds) == (2, 3, 4)
    assert result.tiny_q_jets_complete is True
    assert result.full_window_topology_complete is False
    assert result.physical_initial_source_bound is False
    assert result.clean_independent_implementation is False
    assert result.endpoint_oracle_is_external_test_only is True
    assert result.production_resource_gate is False
    assert result.non_authoritative is True
    assert result.science_free is True
    assert result.fresh_process is False
    assert result.science_executed is False
    assert result.f0_pass is False
    assert len(result.dependency_bindings) == 6
    assert all(binding.exact_bytes_matched for binding in result.dependency_bindings)

    source = Path(tiny_jets.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= {
        "__future__",
        "dataclasses",
        "fractions",
        "hashlib",
        "math",
        "numpy",
        "pathlib",
        "rate_defined_tensor_f0_packed",
        "rate_defined_tensor_f0_packed_interval_action",
        "rate_defined_tensor_f0_packed_rate_action",
        "rate_defined_tensor_f0_packed_target_uniformization",
        "typing",
    }
    assert "socket" not in source
    assert "subprocess" not in source
