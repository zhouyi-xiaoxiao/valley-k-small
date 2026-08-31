from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import continuum_g1d_fold_confirmation as fold
import numpy as np
import pytest
from scipy import sparse


def test_selected_segment_preserves_the_budget_simplex() -> None:
    for control in (0.0, 0.6388077420868951, 1.0):
        weights = fold.selected_weights(control)
        assert weights == pytest.approx((0.2, 0.1 * control, 0.8 - 0.1 * control))
        assert float(np.sum(weights)) == pytest.approx(1.0, abs=2.0e-15)
    assert float(np.sum(fold.WEIGHT_DERIVATIVE)) == pytest.approx(0.0, abs=1.0e-16)


def test_frozen_generator_tangent_is_diagonal_and_transpose_invariant() -> None:
    config = fold.configuration()
    _model, _weights, generator_derivative = fold.assemble_float_model(
        config,
        0.6388077420868951,
    )
    difference = (generator_derivative - generator_derivative.T).tocsr()
    assert difference.nnz == 0


def test_general_forward_sensitivity_requires_the_tangent_transpose() -> None:
    generator = np.asarray(((-2.0, 2.0), (1.0, -1.0)))
    tangent = np.asarray(((0.0, 1.0), (-2.0, 0.0)))
    state = np.asarray((0.3, 0.7))
    sensitivity = np.asarray((-0.1, 0.1))
    correct = generator.T @ sensitivity + tangent.T @ state
    untransposed = generator.T @ sensitivity + tangent @ state
    assert not np.allclose(correct, untransposed)


def test_action_jet_tangent_matches_centered_matrix_difference() -> None:
    generator = np.asarray(((-1.7, 1.7), (0.4, -0.4)))
    tangent = np.asarray(((-0.2, 0.0), (0.0, 0.3)))
    killing = np.asarray((0.8, 0.2))
    killing_tangent = np.asarray((0.1, -0.1))
    model = SimpleNamespace(
        killed_generator=sparse.csr_matrix(generator),
        killing=killing,
        killing_derivative=killing_tangent,
    )
    values, derivatives = fold.action_jets(
        model,
        sparse.csr_matrix(tangent),
        maximum_order=3,
    )

    def direct(parameter: float, order: int) -> np.ndarray:
        matrix = generator + parameter * tangent
        vector = killing + parameter * killing_tangent
        for _ in range(order):
            vector = matrix @ vector
        return vector

    step = 1.0e-5
    for order in range(4):
        assert values[order] == pytest.approx(direct(0.0, order), abs=2.0e-15)
        centered = (direct(step, order) - direct(-step, order)) / (2.0 * step)
        assert derivatives[order] == pytest.approx(centered, rel=2.0e-9, abs=2.0e-10)


def test_formal_artifact_is_fail_closed_outside_one_finite_grid_fold() -> None:
    payload = json.loads(Path(fold.OUTPUT).read_text(encoding="utf-8"))
    assert payload["status"] == fold.PASS_STATUS
    assert payload["finite_grid_fold_confirmed"] is True
    assert payload["finite_B_Doi_fold"] is True
    assert payload["continuum_verified"] is False
    assert payload["project_gate_passed"] is False
    assert payload["evidence_timing"] == ("POST_RESULT_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY")
    assert [row["root_count"] for row in payload["side_topology"]] == [3, 1]
    assert payload["side_topology"][0]["topology"] == [
        "maximum",
        "minimum",
        "maximum",
    ]
