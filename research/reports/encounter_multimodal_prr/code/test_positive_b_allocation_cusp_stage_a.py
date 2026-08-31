from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import positive_b_allocation_cusp_stage_a as stage_a
import pytest
from numpy.testing import assert_allclose


@pytest.fixture(scope="module")
def model() -> stage_a.AllocationModel:
    return stage_a.build_small_grid_model(7)


@pytest.fixture(scope="module")
def snapshot(model: stage_a.AllocationModel) -> stage_a.CuspSnapshot:
    return stage_a.evaluate_point(
        model,
        stage_a.REFERENCE_CUSP_TIME,
        0.01,
        np.zeros(2),
    )


@pytest.fixture(scope="module")
def synthetic_cusp() -> stage_a.CuspSnapshot:
    jets = np.asarray((0.5, 0.0, 0.0, 0.0, -0.2))
    allocation_jets = np.asarray(
        (
            (0.0, 0.3, -0.2, 0.07, 0.0),
            (0.0, 0.1, 0.4, -0.05, 0.0),
        )
    )
    jacobian = np.asarray(
        (
            (jets[2], allocation_jets[0, 1], allocation_jets[1, 1]),
            (jets[3], allocation_jets[0, 2], allocation_jets[1, 2]),
            (jets[4], allocation_jets[0, 3], allocation_jets[1, 3]),
        )
    )
    return stage_a.CuspSnapshot(
        time=13.0,
        budget=0.01,
        theta=np.zeros(2),
        weights=stage_a.REFERENCE_WEIGHTS.copy(),
        state=np.ones(1),
        state_tangents=np.zeros((2, 1)),
        per_budget_time_jets=jets,
        allocation_time_jets=allocation_jets,
        cusp_map=jets[1:4],
        cusp_jacobian=jacobian,
        survival_identity_residuals=np.zeros(3),
    )


def mock_snapshot(
    time: float,
    budget: float,
    theta: np.ndarray,
    cusp_map: np.ndarray,
    cusp_jacobian: np.ndarray,
) -> stage_a.CuspSnapshot:
    return stage_a.CuspSnapshot(
        time=float(time),
        budget=float(budget),
        theta=np.asarray(theta, dtype=float).copy(),
        weights=stage_a.weights_from_theta(theta),
        state=np.ones(1),
        state_tangents=np.zeros((2, 1)),
        per_budget_time_jets=np.asarray((1.0, 0.0, 0.0, 0.0, -0.2)),
        allocation_time_jets=np.zeros((2, 5)),
        cusp_map=np.asarray(cusp_map, dtype=float),
        cusp_jacobian=np.asarray(cusp_jacobian, dtype=float),
        survival_identity_residuals=np.zeros(3),
    )


def test_basis_trust_box_and_dry_run_boundary_are_fail_closed(
    model: stage_a.AllocationModel,
) -> None:
    diagnostics = stage_a.basis_diagnostics()
    assert stage_a.BUDGET_SCHEDULE == (0.0, 0.0025, 0.0050, 0.0075, 0.0100)
    assert stage_a.TRUST_BOX == stage_a.TrustBox(
        minimum_time=9.0,
        maximum_time=18.0,
        maximum_theta_linf=0.15,
        minimum_weight=0.03,
        maximum_newton_iterations=12,
        maximum_step_halvings=8,
        scaled_residual_tolerance=1.0e-10,
    )
    assert diagnostics["budget_tangent_error"] <= 2.0e-15
    assert diagnostics["orthonormality_error"] <= 2.0e-15
    assert_allclose(np.sum(stage_a.REFERENCE_WEIGHTS), 1.0, atol=2.0e-15)

    inside, reason = stage_a.point_in_trust_box(13.0, np.zeros(2))
    assert inside and reason == "inside"
    assert not stage_a.point_in_trust_box(8.99, np.zeros(2))[0]
    assert not stage_a.point_in_trust_box(13.0, np.asarray((0.151, 0.0)))[0]
    with pytest.raises(ValueError, match="scientific Stage-A meshes"):
        stage_a.validate_dry_run_cells(65)
    with pytest.raises(ValueError, match="scientific Stage-A meshes"):
        stage_a.validate_dry_run_cells(97)
    with pytest.raises(ValueError, match="must not exceed"):
        stage_a.validate_dry_run_cells(26)
    with pytest.raises(ValueError, match="exact frozen trust-box"):
        stage_a.solve_cusp(
            model,
            budget=0.0,
            initial_time=13.0,
            initial_theta=np.zeros(2),
            trust_box=replace(stage_a.TRUST_BOX, maximum_time=19.0),
        )
    spoofed_scientific_mesh = replace(model, cells=65)
    with pytest.raises(ValueError, match="scientific Stage-A meshes"):
        stage_a.algebra_preflight(spoofed_scientific_mesh)


def test_matrix_free_actions_and_augmented_orientation_match_explicit_csr(
    model: stage_a.AllocationModel,
) -> None:
    theta = np.asarray((0.013, -0.009))
    budget = 0.01
    base = stage_a.AllocationKilledColumnOperator(model, budget, theta)
    augmented = stage_a.AllocationTangentColumnOperator(base)
    explicit_row = stage_a.explicit_row_generator(model, budget, theta)
    explicit_augmented = stage_a.explicit_augmented_column_generator(model, budget, theta)

    vector = np.sin(np.arange(model.state_count) + 0.3)
    block_vector = np.cos(np.arange(3 * model.state_count) + 0.7)
    assert_allclose(base.matvec(vector), explicit_row.T @ vector, rtol=0.0, atol=2.0e-15)
    assert_allclose(base.rmatvec(vector), explicit_row @ vector, rtol=0.0, atol=2.0e-15)
    assert_allclose(
        augmented.matvec(block_vector),
        explicit_augmented @ block_vector,
        rtol=0.0,
        atol=3.0e-15,
    )
    assert_allclose(
        augmented.rmatvec(block_vector),
        explicit_augmented.T @ block_vector,
        rtol=0.0,
        atol=3.0e-15,
    )


def test_state_tangents_and_direct_observable_recurrences_match_finite_differences(
    model: stage_a.AllocationModel,
    snapshot: stage_a.CuspSnapshot,
) -> None:
    step = 2.0e-5
    for index in range(2):
        increment = np.zeros(2)
        increment[index] = step
        plus_state, plus_jets = stage_a.evaluate_without_tangents(
            model, snapshot.time, snapshot.budget, snapshot.theta + increment
        )
        minus_state, minus_jets = stage_a.evaluate_without_tangents(
            model, snapshot.time, snapshot.budget, snapshot.theta - increment
        )
        state_difference = (plus_state - minus_state) / (2.0 * step)
        jet_difference = (plus_jets - minus_jets) / (2.0 * step)
        assert_allclose(
            snapshot.state_tangents[index],
            state_difference,
            rtol=2.0e-6,
            atol=2.0e-11,
        )
        # Orders 0--3 exercise the direct observable term and f_ttt,theta.
        assert_allclose(
            snapshot.allocation_time_jets[index, :4],
            jet_difference[:4],
            rtol=2.0e-6,
            atol=2.0e-10,
        )
    assert np.max(snapshot.survival_identity_residuals) <= 2.0e-15

    ambient_state = np.random.get_state()
    try:
        np.random.seed(12345)
        state_before = np.random.get_state()
        stage_a.evaluate_without_tangents(model, 0.25, 0.01, np.zeros(2))
        observed_after = np.random.random(4)
        np.random.set_state(state_before)
        expected_after = np.random.random(4)
        assert_allclose(observed_after, expected_after, rtol=0.0, atol=0.0)
    finally:
        np.random.set_state(ambient_state)


def test_complete_H_jacobian_including_fourth_time_jet(
    model: stage_a.AllocationModel,
    snapshot: stage_a.CuspSnapshot,
) -> None:
    _states, finite_difference = stage_a._finite_difference_snapshot(  # noqa: SLF001
        model,
        snapshot.time,
        snapshot.budget,
        snapshot.theta,
        allocation_step=2.0e-5,
        relative_time_step=2.0e-5,
    )
    assert_allclose(
        snapshot.cusp_jacobian,
        finite_difference,
        rtol=3.0e-6,
        atol=3.0e-10,
    )
    # The time column must be exactly f_tt, f_ttt, f_tttt analytically.
    assert_allclose(snapshot.cusp_jacobian[:, 0], snapshot.per_budget_time_jets[2:5])


def test_cusp_determinant_factorization_requires_a_verified_cusp(
    synthetic_cusp: stage_a.CuspSnapshot,
) -> None:
    diagnostics = stage_a.cusp_nondegeneracy(synthetic_cusp)
    assert diagnostics["maximum_scaled_cusp_residual"] == 0.0
    assert diagnostics["determinant_factorization_relative_residual"] <= 2.0e-15

    noncusp_jets = synthetic_cusp.per_budget_time_jets.copy()
    noncusp_jets[1] = 0.01
    noncusp = replace(
        synthetic_cusp,
        per_budget_time_jets=noncusp_jets,
        cusp_map=noncusp_jets[1:4],
    )
    with pytest.raises(ValueError, match="verified near-cusp"):
        stage_a.cusp_nondegeneracy(noncusp)

    rank_zero = replace(
        synthetic_cusp,
        allocation_time_jets=np.zeros((2, 5)),
        cusp_jacobian=np.asarray(
            (
                (0.0, 0.0, 0.0),
                (0.0, 0.0, 0.0),
                (synthetic_cusp.per_budget_time_jets[4], 0.0, 0.0),
            )
        ),
    )
    rank_zero_diagnostics = stage_a.cusp_nondegeneracy(rank_zero)
    stage_a.require_finite_json(rank_zero_diagnostics)
    assert rank_zero_diagnostics["projected_singular_value_ratio"] == 0.0
    assert rank_zero_diagnostics["projected_singular_values"] == [0.0, 0.0]


def test_fold_and_remote_pair_interfaces_do_not_search(
    snapshot: stage_a.CuspSnapshot,
    synthetic_cusp: stage_a.CuspSnapshot,
) -> None:
    with pytest.raises(ValueError, match="verified near-cusp"):
        stage_a.fold_predictor(snapshot, 0.10)

    response = synthetic_cusp.cusp_jacobian[:2, 1:]
    assert np.linalg.matrix_rank(response) == 2
    fourth = synthetic_cusp.per_budget_time_jets[4]
    for offset in (-0.1, 0.1):
        predicted_theta = stage_a.fold_predictor(synthetic_cusp, offset)
        eta = predicted_theta - synthetic_cusp.theta
        assert_allclose(
            response @ eta,
            np.asarray((fourth * offset**3 / 3.0, -fourth * offset**2 / 2.0)),
            rtol=2.0e-14,
            atol=2.0e-16,
        )
    canonical = stage_a.canonical_outgoing_fold_predictors(synthetic_cusp)
    assert canonical["negative"][0] == synthetic_cusp.time - 0.10
    assert canonical["positive"][0] == synthetic_cusp.time + 0.10
    assert_allclose(canonical["negative"][1:], stage_a.fold_predictor(synthetic_cusp, -0.10))
    assert_allclose(canonical["positive"][1:], stage_a.fold_predictor(synthetic_cusp, 0.10))

    assert stage_a.validate_arclength_step(0.05) == 0.05
    with pytest.raises(ValueError, match="frozen interval"):
        stage_a.validate_arclength_step(0.21)

    with pytest.raises(ValueError, match="verified near-fold"):
        stage_a.fold_null_direction(snapshot)
    assert np.linalg.matrix_rank(synthetic_cusp.fold_jacobian) == 2
    direction = stage_a.fold_null_direction(synthetic_cusp)
    assert_allclose(np.linalg.norm(direction), 1.0, atol=2.0e-15)
    assert np.linalg.norm(synthetic_cusp.fold_jacobian @ direction) <= 2.0e-13
    assert np.dot(stage_a.fold_null_direction(synthetic_cusp, -direction), -direction) > 0.0
    with pytest.raises(ValueError, match="must be nonzero"):
        stage_a.fold_null_direction(synthetic_cusp, np.zeros(3))
    orthogonal = np.cross(direction, np.asarray((1.0, 0.0, 0.0)))
    if np.linalg.norm(orthogonal) <= 1.0e-14:
        orthogonal = np.cross(direction, np.asarray((0.0, 1.0, 0.0)))
    with pytest.raises(ValueError, match="cannot orient"):
        stage_a.fold_null_direction(synthetic_cusp, orthogonal)

    candidates = (
        stage_a.StationaryPoint(4.0, 0.2, 0.0, -0.01),
        stage_a.StationaryPoint(7.0, 0.1, 0.0, 0.004),
    )
    gate = stage_a.assess_supplied_remote_pair(
        snapshot.time,
        candidates,
        reference_density=0.2,
    )
    assert gate["remote_pair_present"]
    assert gate["candidate_search_performed"] is False
    assert gate["frozen_thresholds"] == {
        "cusp_neighborhood": 0.25,
        "relative_density_floor": 1.0e-8,
        "scaled_curvature_floor": 0.05,
        "scaled_root_residual_cap": 1.0e-8,
        "minimum_root_separation": 0.25,
    }

    cross_cusp = (
        stage_a.StationaryPoint(snapshot.time - 1.0, 0.2, 0.0, -0.01),
        stage_a.StationaryPoint(snapshot.time + 1.0, 0.1, 0.0, 0.004),
    )
    assert not stage_a.assess_supplied_remote_pair(
        snapshot.time,
        cross_cusp,
        reference_density=0.2,
    )["remote_pair_present"]
    outside_window = (
        stage_a.StationaryPoint(40.0, 0.2, 0.0, -0.01),
        stage_a.StationaryPoint(41.0, 0.1, 0.0, 0.004),
    )
    assert not stage_a.assess_supplied_remote_pair(
        snapshot.time,
        outside_window,
        reference_density=0.2,
    )["remote_pair_present"]
    with pytest.raises(ValueError, match="cusp time"):
        stage_a.assess_supplied_remote_pair(
            math.nan,
            candidates,
            reference_density=0.2,
        )
    zero_density = (
        stage_a.StationaryPoint(4.0, 0.0, 0.0, -0.01),
        stage_a.StationaryPoint(7.0, 0.1, 0.0, 0.004),
    )
    assert not stage_a.assess_supplied_remote_pair(
        snapshot.time,
        zero_density,
        reference_density=0.2,
    )["remote_pair_present"]


def test_homotopy_stops_at_first_hold_and_never_changes_schedule(
    model: stage_a.AllocationModel,
) -> None:
    # A deliberately out-of-box starting time must fail before any propagation.
    result = stage_a.run_budget_homotopy(model, initial_time=8.0)
    assert result["status"] == "HOLD_DISCOVERY"
    assert not result["completed_budget_schedule"]
    assert [row["budget"] for row in result["rows"]] == [stage_a.BUDGET_SCHEDULE[0]]
    assert result["rows"][0]["reason"] == "time_outside_trust_box"


def test_homotopy_executes_the_exact_five_budget_schedule_when_solves_pass(
    model: stage_a.AllocationModel,
    synthetic_cusp: stage_a.CuspSnapshot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[float] = []

    def pass_solve(
        _model: stage_a.AllocationModel,
        budget: float,
        initial_time: float,
        initial_theta: np.ndarray,
    ) -> stage_a.CuspSolve:
        calls.append(budget)
        value = replace(
            synthetic_cusp,
            budget=budget,
            time=float(initial_time),
            theta=np.asarray(initial_theta, dtype=float).copy(),
            weights=stage_a.weights_from_theta(initial_theta),
        )
        return stage_a.CuspSolve(
            "PASS_DISCOVERY_SOLVE",
            True,
            0,
            value,
            "converged",
        )

    monkeypatch.setattr(stage_a, "solve_cusp", pass_solve)
    result = stage_a.run_budget_homotopy(model)
    assert tuple(calls) == (0.0, 0.0025, 0.0050, 0.0075, 0.0100)
    assert result["status"] == "PASS_DRY_RUN_HOMOTOPY_ONLY"
    assert result["completed_budget_schedule"]


def test_newton_and_both_branch_correctors_take_the_analytic_direction(
    model: stage_a.AllocationModel,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cusp_target = np.asarray((13.1, 0.01, -0.02))

    def cusp_map(
        _model: stage_a.AllocationModel,
        time: float,
        budget: float,
        theta: np.ndarray,
    ) -> stage_a.CuspSnapshot:
        point = np.asarray((time, *theta))
        return mock_snapshot(time, budget, theta, point - cusp_target, np.eye(3))

    monkeypatch.setattr(stage_a, "evaluate_point", cusp_map)
    cusp = stage_a.solve_cusp(model, 0.01, 13.0, np.zeros(2))
    assert cusp.converged and cusp.iterations == 1
    assert cusp.snapshot is not None
    assert_allclose(
        np.asarray((cusp.snapshot.time, *cusp.snapshot.theta)),
        cusp_target,
    )

    def wrong_cusp_jacobian(
        _model: stage_a.AllocationModel,
        time: float,
        budget: float,
        theta: np.ndarray,
    ) -> stage_a.CuspSnapshot:
        point = np.asarray((time, *theta))
        return mock_snapshot(time, budget, theta, point - cusp_target, -np.eye(3))

    monkeypatch.setattr(stage_a, "evaluate_point", wrong_cusp_jacobian)
    rejected = stage_a.solve_cusp(model, 0.01, 13.0, np.zeros(2))
    assert not rejected.converged
    assert rejected.reason == "bounded_line_search_failed"

    fold_target = np.asarray((0.01, -0.02))

    def fold_map(
        _model: stage_a.AllocationModel,
        time: float,
        budget: float,
        theta: np.ndarray,
    ) -> stage_a.CuspSnapshot:
        residual = np.asarray((theta[0] - fold_target[0], theta[1] - fold_target[1], 0.0))
        jacobian = np.asarray(((0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (-0.2, 0.0, 0.0)))
        return mock_snapshot(time, budget, theta, residual, jacobian)

    monkeypatch.setattr(stage_a, "evaluate_point", fold_map)
    fixed = stage_a.correct_fold_at_fixed_time(model, 0.01, 13.0, np.zeros(2))
    assert fixed["converged"] and fixed["iterations"] == 1
    assert_allclose(fixed["snapshot"].theta, fold_target)

    arclength = stage_a.pseudo_arclength_corrector(
        model,
        0.01,
        predicted_point=np.asarray((13.0, 0.0, 0.0)),
        branch_direction=np.asarray((1.0, 0.0, 0.0)),
    )
    assert arclength["converged"] and arclength["iterations"] == 1
    assert arclength["snapshot"].time == 13.0
    assert_allclose(arclength["snapshot"].theta, fold_target)


def test_branch_correctors_serialize_evaluation_failures_as_hold(
    model: stage_a.AllocationModel,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_evaluation(*_args: object, **_kwargs: object) -> stage_a.CuspSnapshot:
        raise RuntimeError("injected evaluation failure")

    monkeypatch.setattr(stage_a, "evaluate_point", fail_evaluation)
    fixed_time = stage_a.correct_fold_at_fixed_time(
        model,
        budget=0.01,
        time=13.0,
        initial_theta=np.zeros(2),
    )
    assert fixed_time == {
        "status": "HOLD_BRANCH",
        "converged": False,
        "reason": "evaluation_failed",
    }
    arclength = stage_a.pseudo_arclength_corrector(
        model,
        budget=0.01,
        predicted_point=np.asarray((13.0, 0.0, 0.0)),
        branch_direction=np.asarray((1.0, 0.0, 0.0)),
    )
    assert arclength == {
        "status": "HOLD_BRANCH",
        "converged": False,
        "reason": "evaluation_failed",
    }


def test_small_grid_algebra_preflight_is_finite_and_scientifically_negative(
    model: stage_a.AllocationModel,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    preflight = stage_a.algebra_preflight(model)
    stage_a.require_finite_json(preflight)
    assert preflight["all_gates_passed"], preflight["gates"]
    assert all(preflight["gates"].values())

    # Exercise the real packaging path without repeating either expensive
    # numerical component.
    monkeypatch.setattr(stage_a, "build_small_grid_model", lambda _cells: model)
    monkeypatch.setattr(stage_a, "algebra_preflight", lambda _model: preflight)
    monkeypatch.setattr(
        stage_a,
        "run_budget_homotopy",
        lambda _model: {
            "status": "HOLD_DISCOVERY",
            "completed_budget_schedule": False,
            "rows": [],
        },
    )
    packaged = stage_a.run_algebra_dry_run(model.cells)
    stage_a.require_finite_json(packaged)
    assert packaged["status"] == "PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE"
    assert packaged["scientific_stage_a_meshes_executed"] == []
    assert not any(packaged["claim_flags"].values())
