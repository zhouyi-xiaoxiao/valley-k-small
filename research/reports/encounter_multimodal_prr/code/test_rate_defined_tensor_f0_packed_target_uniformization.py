from __future__ import annotations

import ast
import hashlib
import math
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import rate_defined_tensor_f0_packed as packed
import rate_defined_tensor_f0_packed_rate_action as rate_action
import rate_defined_tensor_f0_packed_target_uniformization as target_uniformization
import rate_defined_tensor_f0_packed_uniformization as frozen
from test_rate_defined_tensor_f0_packed_rate_action import _problem as _rate_box_problem
from test_rate_defined_tensor_f0_packed_uniformization import _problem

MAXIMUM_WORKING_BYTES = 2_000_000


def _component_box(
    rows: tuple[tuple[float, float], ...],
    *,
    logical_shape: tuple[int, ...] = (2,),
) -> packed.CanonicalPackedIntervals:
    payload = packed.create_packed_interval_payload(
        rows,
        role=target_uniformization.INITIAL_BOX_ROLE,
        logical_shape=logical_shape,
        nonnegative=True,
        block_size=2,
        maximum_working_bytes=MAXIMUM_WORKING_BYTES,
    )
    return packed.load_canonical_packed_intervals(payload)


def _initial(
    rows: tuple[tuple[float, float], ...] = ((0.0, 0.1), (0.9, 1.0)),
) -> target_uniformization.CertifiedTargetBall:
    return target_uniformization.make_initial_target_ball(_component_box(rows))


def _run(
    target: target_uniformization.CertifiedTargetBall | None = None,
    *,
    time: Fraction = Fraction(1, 2),
) -> target_uniformization.TargetUniformizationResult:
    kernel, _, contract = _problem()
    return target_uniformization.target_uniformize_transpose(
        kernel,
        _initial() if target is None else target,
        contract,
        time=time,
        tail_tolerance=Fraction(1, 2**36),
    )


def _two_state_exact(initial: np.ndarray, time: float) -> np.ndarray:
    decay = math.exp(-0.75 * time)
    total = float(np.sum(initial))
    stationary = np.array([total / 3.0, 2.0 * total / 3.0])
    return stationary + decay * (initial - stationary)


def test_zero_centre_positive_radius_target_is_accepted_and_encloses_box_extremes() -> None:
    initial = _initial()
    assert initial.nominal[0] == 0.0
    assert initial.l1_radius_exact_upper == Fraction(1) - Fraction.from_float(0.9)
    assert initial.whole_symmetric_ball_nonnegative_required is False
    result = _run(initial)

    for first in np.linspace(0.0, 0.1, 33):
        exact = _two_state_exact(np.array([first, 1.0 - first]), 0.5)
        distance = sum(
            (
                abs(Fraction.from_float(float(left)) - Fraction.from_float(float(right)))
                for left, right in zip(result.nominal, exact, strict=True)
            ),
            Fraction(0),
        )
        assert distance <= result.l1_radius_exact_upper
    assert result.inherited_input_radius_exact_upper == initial.l1_radius_exact_upper
    assert result.anchor.input_to_anchor_l1_exact == 0
    assert result.anchor.signed_error_contraction_used is True


def test_current_frozen_ball_gate_rejects_same_enclosure_but_adapter_chunks_it() -> None:
    kernel, _, contract = _problem()
    initial = _initial()
    vector = packed.CanonicalFloat64Vector(
        logical_shape=(2,),
        values=initial.nominal,
        raw_sha256=initial.nominal_raw_sha256,
        nonnegative=True,
        source_sha256=hashlib.sha256(
            b"old-gate" + bytes.fromhex(initial.binding_sha256)
        ).hexdigest(),
    )
    old_input = rate_action.make_internal_point_ball_input(
        vector,
        input_l1_radius_upper=initial.l1_radius_upper,
        radius_provenance_sha256=initial.binding_sha256,
    )
    with pytest.raises(frozen.TinyUniformizationFailure, match="nonnegative subprobability"):
        frozen.tiny_uniformize_transpose(
            kernel,
            old_input,
            contract,
            time=Fraction(1, 2),
            tail_tolerance=Fraction(1, 2**36),
        )

    first = target_uniformization.target_uniformize_transpose(
        kernel,
        initial,
        contract,
        time=Fraction(1, 2),
        tail_tolerance=Fraction(1, 2**36),
    )
    second = target_uniformization.target_uniformize_transpose(
        kernel,
        first.target,
        contract,
        time=Fraction(1, 2),
        tail_tolerance=Fraction(1, 2**36),
    )
    for first_mass in (0.0, 0.025, 0.05, 0.075, 0.1):
        exact = _two_state_exact(np.array([first_mass, 1.0 - first_mass]), 1.0)
        assert float(np.sum(np.abs(second.nominal - exact))) <= second.l1_radius_upper
    assert second.inherited_input_radius_exact_upper >= first.l1_radius_exact_upper
    assert second.target.predecessor_binding_sha256 != first.target.predecessor_binding_sha256


def test_anchor_projection_handles_a_nominal_mass_rounding_overshoot() -> None:
    initial = _initial(((0.5, 0.5), (0.5, 0.5)))
    values = np.array([0.5, float(np.nextafter(0.5, math.inf))], dtype=np.float64)
    values.setflags(write=False)
    overshoot = (
        sum(
            (Fraction.from_float(float(value)) for value in values),
            Fraction(0),
        )
        - 1
    )
    radius = initial.l1_radius_exact_upper + overshoot
    radius_float = target_uniformization._float_upper(radius)
    provisional = replace(
        initial,
        nominal=values,
        nominal_raw_sha256=hashlib.sha256(memoryview(values).cast("B")).hexdigest(),
        l1_radius_exact_upper=radius,
        l1_radius_upper=radius_float,
        l1_radius_upper_hex=radius_float.hex(),
        binding_sha256="0" * 64,
    )
    target = replace(
        provisional,
        binding_sha256=target_uniformization._target_binding(provisional),
    )
    target_uniformization.validate_target_ball_structure_only(target)
    result = _run(target, time=Fraction(0))
    assert result.anchor.anchor_was_mass_projected is True
    assert result.anchor.anchor_nominal_mass <= 1
    assert result.anchor.input_to_anchor_l1_exact >= overshoot
    assert float(np.sum(np.abs(result.nominal - np.array([0.5, 0.5])))) <= (result.l1_radius_upper)


def test_chunk_chain_binds_one_kernel_contract_and_cumulative_time() -> None:
    first_kernel, _, first_contract = _problem()
    initial = _initial()
    first = target_uniformization.target_uniformize_transpose(
        first_kernel,
        initial,
        first_contract,
        time=Fraction(1, 2),
        tail_tolerance=Fraction(1, 2**36),
    )
    assert first.target.operator_binding_established is True
    assert first.target.cumulative_time == Fraction(1, 2)
    assert first.target.cumulative_chunk_count == 1

    _, different_kernel, different_contract = _rate_box_problem(
        (2,),
        periodic=(False,),
        block_size=2,
    )
    with pytest.raises(
        target_uniformization.TargetUniformizationFailure,
        match="fixed operator binding",
    ):
        target_uniformization.target_uniformize_transpose(
            different_kernel,
            first.target,
            different_contract,
            time=Fraction(1, 2),
            tail_tolerance=Fraction(1, 2**36),
        )


def test_component_box_and_unit_mass_witness_mutations_fail_closed() -> None:
    with pytest.raises(target_uniformization.TargetUniformizationFailure, match="unit total"):
        target_uniformization.make_initial_target_ball(
            _component_box(((0.0, 0.1), (0.8, 0.85))),
        )
    target = _initial()
    with pytest.raises(target_uniformization.TargetUniformizationFailure, match="ledger"):
        target_uniformization.validate_target_ball_structure_only(
            replace(target, target_mass_cap=Fraction(2))
        )
    with pytest.raises(target_uniformization.TargetUniformizationFailure, match="ledger"):
        target_uniformization.validate_target_ball_structure_only(
            replace(target, component_box_raw_sha256="0" * 64)
        )
    with pytest.raises(target_uniformization.TargetUniformizationFailure, match="ledger"):
        target_uniformization.validate_target_ball_structure_only(
            replace(target, unit_mass_witness_sha256="0" * 64)
        )


def test_frozen_hash_binding_and_all_promotion_flags_remain_false() -> None:
    result = _run()
    assert result.frozen_source_sha256 == (
        target_uniformization.ACCEPTED_UNIFORMIZATION_SOURCE_SHA256
    )
    assert result.frozen_test_sha256 == (target_uniformization.ACCEPTED_UNIFORMIZATION_TEST_SHA256)
    assert result.frozen_exact_bytes_matched is True
    assert result.status == target_uniformization.METHOD_STATUS
    for output in (result, result.target):
        assert output.non_authoritative is True
        assert output.science_free is True
        assert output.fresh_process is False
        assert output.f0_pass is False
    assert result.science_executed is False
    assert result.jets_complete is False
    assert result.topology_complete is False
    assert result.independent_semantic_replay_complete is False
    assert result.production_resource_gate is False


def test_adapter_import_surface_has_no_network_or_custom_protocol_module() -> None:
    source = Path(target_uniformization.__file__).read_text(encoding="utf-8")
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
        "rate_defined_tensor_f0_packed_rate_action",
        "rate_defined_tensor_f0_packed_uniformization",
        "typing",
    }
    assert "socket" not in source
    assert "subprocess" not in source
    assert "hmac" not in source
