from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import rate_defined_tensor_f0_packed_target_uniformization as target_uniformization
import rate_defined_tensor_f0_tiny_semantic_replay as semantic_replay
from test_rate_defined_tensor_f0_packed_rate_action import _problem as _rate_box_problem
from test_rate_defined_tensor_f0_packed_target_uniformization import _component_box, _initial
from test_rate_defined_tensor_f0_packed_uniformization import _problem


def _bound_initial(
    rows: tuple[tuple[float, float], ...] = ((0.0, 0.1), (0.9, 1.0)),
    *,
    logical_shape: tuple[int, ...] = (2,),
) -> tuple[
    object,
    target_uniformization.CertifiedTargetBall,
]:
    box = _component_box(rows, logical_shape=logical_shape)
    return box, target_uniformization.make_initial_target_ball(box)


def _initial_binding(
    box: object,
    initial: target_uniformization.CertifiedTargetBall,
) -> dict[str, object]:
    return {
        "initial_component_box": box,
        "initial_nominal": initial.nominal,
        "initial_l1_radius_exact_upper": initial.l1_radius_exact_upper,
        "target_mass_cap": initial.target_mass_cap,
        "declared_component_box_raw_sha256": initial.component_box_raw_sha256,
        "declared_component_box_manifest_sha256": initial.component_box_manifest_sha256,
        "declared_unit_mass_witness_sha256": initial.unit_mass_witness_sha256,
    }


def _verify(
    *,
    time: Fraction = Fraction(1, 2),
) -> semantic_replay.IndependentSemanticReplayResult:
    kernel, _, contract = _problem()
    box, initial = _bound_initial()
    produced = target_uniformization.target_uniformize_transpose(
        kernel,
        initial,
        contract,
        time=time,
        tail_tolerance=Fraction(1, 2**36),
    )
    return semantic_replay.replay_tiny_uniformization_semantics(
        kernel,
        **_initial_binding(box, initial),
        time=time,
        tail_tolerance=produced.tail_tolerance,
        poisson_terms=produced.poisson_terms_used,
        producer_nominal=produced.nominal,
        producer_l1_radius_exact_upper=produced.l1_radius_exact_upper,
    )


def test_independent_semantic_replay_contains_target_aware_producer() -> None:
    replay = _verify()
    assert replay.producer_ball_contains_independent_replay is True
    assert replay.containment_margin >= 0
    assert replay.poisson.alternating_bracket_exact is True
    assert replay.poisson.producer_poisson_ledger_consumed is False
    assert replay.action.raw_interval_endpoints_consumed is True
    assert replay.action.producer_action_ledger_consumed is False
    assert replay.producer_ledgers_consumed is False
    assert replay.independent_code_path is True


def test_zero_time_replay_is_exact_apart_from_declared_initial_target_radius() -> None:
    replay = _verify(time=Fraction(0))
    assert replay.poisson.weights[0].lower == 1
    assert replay.poisson.weights[0].upper == 1
    assert replay.poisson.tail_probability_upper == 0
    assert replay.independent_l1_radius_upper == _initial().l1_radius_exact_upper
    assert replay.producer_centre_distance == 0


def test_periodic_mixed_rate_box_reconstructs_shared_neighbour_semantics() -> None:
    _, kernel, contract = _rate_box_problem(
        (3, 2),
        periodic=(False, True),
        block_size=2,
    )
    rows = tuple((1.0, 1.0) if index == 0 else (0.0, 0.0) for index in range(6))
    box, initial = _bound_initial(rows, logical_shape=(3, 2))
    produced = target_uniformization.target_uniformize_transpose(
        kernel,
        initial,
        contract,
        time=Fraction(1),
        tail_tolerance=Fraction(1, 2**40),
    )
    replay = semantic_replay.replay_tiny_uniformization_semantics(
        kernel,
        **_initial_binding(box, initial),
        time=produced.time,
        tail_tolerance=produced.tail_tolerance,
        poisson_terms=produced.poisson_terms_used,
        producer_nominal=produced.nominal,
        producer_l1_radius_exact_upper=produced.l1_radius_exact_upper,
    )
    assert replay.action.maximum_column_l1_deviation > 0
    assert replay.action.every_rate_box_column_subprobability is True
    assert replay.containment_margin >= 0


def test_wholesale_output_time_and_radius_forgeries_are_rejected() -> None:
    kernel, _, contract = _problem()
    box, initial = _bound_initial()
    produced = target_uniformization.target_uniformize_transpose(
        kernel,
        initial,
        contract,
        time=Fraction(1, 2),
        tail_tolerance=Fraction(1, 2**36),
    )
    common = dict(
        kernel=kernel,
        **_initial_binding(box, initial),
        tail_tolerance=produced.tail_tolerance,
        poisson_terms=produced.poisson_terms_used,
    )
    forged_zero = np.zeros_like(produced.nominal)
    forged_zero.setflags(write=False)
    with pytest.raises(semantic_replay.SemanticReplayFailure, match="does not contain"):
        semantic_replay.replay_tiny_uniformization_semantics(
            **common,
            time=produced.time,
            producer_nominal=forged_zero,
            producer_l1_radius_exact_upper=produced.l1_radius_exact_upper,
        )
    with pytest.raises(semantic_replay.SemanticReplayFailure, match="does not contain"):
        semantic_replay.replay_tiny_uniformization_semantics(
            **common,
            time=produced.time,
            producer_nominal=produced.nominal,
            producer_l1_radius_exact_upper=Fraction(0),
        )
    with pytest.raises(semantic_replay.SemanticReplayFailure):
        semantic_replay.replay_tiny_uniformization_semantics(
            **common,
            time=Fraction(3, 4),
            producer_nominal=produced.nominal,
            producer_l1_radius_exact_upper=produced.l1_radius_exact_upper,
        )


def test_too_few_terms_and_invalid_target_mass_fail_independently() -> None:
    kernel, _, contract = _problem()
    box, initial = _bound_initial()
    produced = target_uniformization.target_uniformize_transpose(
        kernel,
        initial,
        contract,
        time=Fraction(1, 2),
        tail_tolerance=Fraction(1, 2**36),
    )
    with pytest.raises(semantic_replay.SemanticReplayFailure, match="term count"):
        semantic_replay.replay_tiny_uniformization_semantics(
            kernel,
            **_initial_binding(box, initial),
            time=produced.time,
            tail_tolerance=produced.tail_tolerance,
            poisson_terms=1,
            producer_nominal=produced.nominal,
            producer_l1_radius_exact_upper=produced.l1_radius_exact_upper,
        )
    with pytest.raises(semantic_replay.SemanticReplayFailure, match="bounds"):
        semantic_replay.replay_tiny_uniformization_semantics(
            kernel,
            **{
                **_initial_binding(box, initial),
                "target_mass_cap": Fraction(2),
            },
            time=produced.time,
            tail_tolerance=produced.tail_tolerance,
            poisson_terms=produced.poisson_terms_used,
            producer_nominal=produced.nominal,
            producer_l1_radius_exact_upper=produced.l1_radius_exact_upper,
        )


def test_component_source_nominal_and_witness_rewrites_are_rejected() -> None:
    kernel, _, contract = _problem()
    box, initial = _bound_initial()
    produced = target_uniformization.target_uniformize_transpose(
        kernel,
        initial,
        contract,
        time=Fraction(1, 2),
        tail_tolerance=Fraction(1, 2**36),
    )
    run = {
        "kernel": kernel,
        **_initial_binding(box, initial),
        "time": produced.time,
        "tail_tolerance": produced.tail_tolerance,
        "poisson_terms": produced.poisson_terms_used,
        "producer_nominal": produced.nominal,
        "producer_l1_radius_exact_upper": produced.l1_radius_exact_upper,
    }
    rewritten = np.zeros_like(initial.nominal)
    rewritten.setflags(write=False)
    with pytest.raises(semantic_replay.SemanticReplayFailure, match="component lower"):
        semantic_replay.replay_tiny_uniformization_semantics(
            **{**run, "initial_nominal": rewritten}
        )
    with pytest.raises(semantic_replay.SemanticReplayFailure, match="manifest binding"):
        semantic_replay.replay_tiny_uniformization_semantics(
            **{**run, "declared_component_box_manifest_sha256": "0" * 64}
        )
    with pytest.raises(semantic_replay.SemanticReplayFailure, match="witness binding"):
        semantic_replay.replay_tiny_uniformization_semantics(
            **{**run, "declared_unit_mass_witness_sha256": "0" * 64}
        )


def test_replay_flags_and_import_surface_remain_nonauthoritative_local_only() -> None:
    replay = _verify()
    assert replay.status == semantic_replay.STATUS
    assert replay.non_authoritative is True
    assert replay.science_free is True
    assert replay.fresh_process is False
    assert replay.topology_complete is False
    assert replay.production_resource_gate is False
    assert replay.f0_pass is False

    source = Path(semantic_replay.__file__).read_text(encoding="utf-8")
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
        "rate_defined_tensor_f0_packed",
        "typing",
    }
    assert "socket" not in source
    assert "subprocess" not in source
    assert "hmac" not in source
