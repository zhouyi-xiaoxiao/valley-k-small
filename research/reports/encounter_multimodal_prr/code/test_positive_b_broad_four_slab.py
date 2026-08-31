from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from typing import Any

import continuum_broad_patch_b0_bridge as bridge
import numpy as np
import positive_b_broad_four_slab as positive
import pytest
from scipy import sparse
from scipy.optimize import brentq
from scipy.sparse.linalg import expm_multiply


def _small_manifest() -> dict[str, Any]:
    manifest = copy.deepcopy(bridge.load_json(bridge.MANIFEST))
    manifest["positive_budget"] = 0.01
    manifest["fixed_absolute_weights"] = positive.FROZEN_WEIGHTS.copy()
    manifest["event_mass"] = copy.deepcopy(positive.FROZEN_EVENT_MASS)
    manifest["tail_gates"] = copy.deepcopy(positive.FROZEN_TAIL_GATES)
    return manifest


def _agreement_row(
    mesh: int,
    root_times: list[float] | None,
    *,
    topology: list[str] | None = None,
    valleys: list[float] | None = None,
    masses: list[float] | None = None,
    peak_ratio: float | None = None,
    final_survival: float = 0.7,
    all_mesh_gates_passed: bool = False,
) -> dict[str, Any]:
    times = [] if root_times is None else root_times
    inferred_topology = [
        "maximum",
        "minimum",
        "maximum",
        "minimum",
        "maximum",
    ][: len(times)]
    return {
        "mesh": [mesh, mesh, mesh],
        "stationary_structure": {
            "roots": [{"time": value} for value in times],
            "topology": inferred_topology if topology is None else topology,
            "peak_minimum_to_maximum_ratio": peak_ratio,
            "valley_to_smaller_adjacent_peak_ratios": valleys,
        },
        "survival_and_event_mass": {
            "basin_reaction_masses": masses,
            "final_survival": final_survival,
            "basin_mass_sum_vs_total_reaction_difference": None,
        },
        "all_mesh_gates_passed": all_mesh_gates_passed,
    }


def _explicit_row_generator(
    model: positive.TensorKilledModel,
    budget: float | None = None,
) -> sparse.csr_matrix:
    value = model.budget if budget is None else float(budget)
    identity_midpoint = sparse.eye(model.factors.midpoint_generator.shape[0], format="csr")
    identity_relative = sparse.eye(model.factors.relative_generator.shape[0], format="csr")
    free = sparse.kron(
        model.factors.midpoint_generator,
        identity_relative,
        format="csr",
    ) + sparse.kron(
        identity_midpoint,
        model.factors.relative_generator,
        format="csr",
    )
    return (free - value * sparse.diags(model.killing_per_budget, format="csr")).tocsr()


def _assert_rng_states_equal(left: tuple[Any, ...], right: tuple[Any, ...]) -> None:
    assert left[0] == right[0]
    np.testing.assert_array_equal(left[1], right[1])
    assert left[2:] == right[2:]


def _time_jets(
    row_generator: sparse.csr_matrix,
    state: np.ndarray,
    killing_per_budget: np.ndarray,
    budget: float,
) -> np.ndarray:
    actions = [np.asarray(killing_per_budget, dtype=float)]
    for _ in range(3):
        actions.append(np.asarray(row_generator @ actions[-1], dtype=float))
    return np.asarray([budget * (state @ action) for action in actions])


def test_matrix_free_actions_adjoint_dtype_shape_and_traces_match_explicit_csr() -> None:
    model = positive.build_model(9, _small_manifest())
    row_generator = _explicit_row_generator(model)
    column_generator = row_generator.T.tocsr()
    states = model.initial.size
    vector = np.sin(np.arange(states, dtype=float) + 0.3)
    probe = np.column_stack(
        (
            vector,
            np.cos(np.arange(states, dtype=float) / 7.0),
            np.linspace(-0.7, 0.9, states),
        )
    )

    assert model.operator.shape == (states, states)
    assert model.operator.dtype == np.dtype(np.float64)
    np.testing.assert_allclose(
        model.operator.matvec(vector),
        column_generator @ vector,
        rtol=3.0e-14,
        atol=3.0e-13,
    )
    np.testing.assert_allclose(
        model.operator.rmatvec(vector),
        row_generator @ vector,
        rtol=3.0e-14,
        atol=3.0e-13,
    )
    np.testing.assert_allclose(
        model.operator.matmat(probe),
        column_generator @ probe,
        rtol=3.0e-14,
        atol=3.0e-13,
    )
    np.testing.assert_allclose(
        model.operator.rmatmat(probe),
        row_generator @ probe,
        rtol=3.0e-14,
        atol=3.0e-13,
    )
    left = np.cos(np.arange(states, dtype=float) + 0.1)
    np.testing.assert_allclose(
        left @ model.operator.matvec(vector),
        model.operator.rmatvec(left) @ vector,
        rtol=3.0e-14,
        atol=3.0e-12,
    )
    np.testing.assert_allclose(
        model.operator.trace_value,
        np.sum(row_generator.diagonal()),
        rtol=3.0e-15,
        atol=3.0e-10,
    )

    tangent_operator = positive.BudgetTangentColumnOperator(model.operator)
    derivative = -sparse.diags(model.killing_per_budget, format="csr")
    zero = sparse.csr_matrix((states, states))
    explicit_augmented = sparse.bmat(
        (
            (column_generator, zero),
            (derivative, column_generator),
        ),
        format="csr",
    )
    augmented_vector = np.concatenate((vector, left))
    augmented_probe = np.column_stack((augmented_vector, augmented_vector[::-1]))
    assert tangent_operator.shape == (2 * states, 2 * states)
    assert tangent_operator.dtype == np.dtype(np.float64)
    np.testing.assert_allclose(
        tangent_operator.matvec(augmented_vector),
        explicit_augmented @ augmented_vector,
        rtol=3.0e-14,
        atol=3.0e-13,
    )
    np.testing.assert_allclose(
        tangent_operator.rmatvec(augmented_vector),
        explicit_augmented.T @ augmented_vector,
        rtol=3.0e-14,
        atol=3.0e-13,
    )
    np.testing.assert_allclose(
        tangent_operator.matmat(augmented_probe),
        explicit_augmented @ augmented_probe,
        rtol=3.0e-14,
        atol=3.0e-13,
    )
    np.testing.assert_allclose(
        tangent_operator.rmatmat(augmented_probe),
        explicit_augmented.T @ augmented_probe,
        rtol=3.0e-14,
        atol=3.0e-13,
    )
    np.testing.assert_allclose(
        tangent_operator.trace_value,
        np.sum(explicit_augmented.diagonal()),
        rtol=3.0e-15,
        atol=6.0e-10,
    )


def test_matrix_free_forward_law_p_f_and_all_time_jets_match_explicit_csr() -> None:
    model = positive.build_model(9, _small_manifest())
    row_generator = _explicit_row_generator(model)
    time_value = 0.73
    with positive.pinned_numpy_global_seed(271828):
        observed_state = positive.propagate(
            model.operator,
            model.initial,
            time_value,
            model.operator.trace_value,
        )
    explicit_state = np.asarray(
        expm_multiply(time_value * row_generator.T, model.initial),
        dtype=float,
    )
    np.testing.assert_allclose(observed_state, explicit_state, rtol=3.0e-12, atol=3.0e-14)

    observed_projection = positive.project_state(model, observed_state)
    explicit_jets = _time_jets(
        row_generator,
        explicit_state,
        model.killing_per_budget,
        model.budget,
    )
    np.testing.assert_allclose(
        observed_projection[:4],
        explicit_jets,
        rtol=4.0e-12,
        atol=4.0e-13,
    )
    np.testing.assert_allclose(
        observed_projection[4], np.sum(explicit_state), rtol=0.0, atol=2.0e-14
    )


def test_augmented_orientation_and_control_jets_match_B_plus_minus_h() -> None:
    model = positive.build_model(9, _small_manifest())
    row_generator = _explicit_row_generator(model)
    column_generator = row_generator.T.tocsr()
    states = model.initial.size
    tangent_operator = positive.BudgetTangentColumnOperator(model.operator)
    augmented_initial = np.concatenate((model.initial, np.zeros_like(model.initial)))
    time_value = 0.7
    with positive.pinned_numpy_global_seed(271828):
        observed_augmented = positive.propagate(
            tangent_operator,
            augmented_initial,
            time_value,
            tangent_operator.trace_value,
        )
    explicit_augmented_operator = sparse.bmat(
        (
            (column_generator, sparse.csr_matrix((states, states))),
            (
                -sparse.diags(model.killing_per_budget, format="csr"),
                column_generator,
            ),
        ),
        format="csr",
    )
    explicit_augmented_state = np.asarray(
        expm_multiply(time_value * explicit_augmented_operator, augmented_initial),
        dtype=float,
    )
    np.testing.assert_allclose(
        observed_augmented,
        explicit_augmented_state,
        rtol=4.0e-12,
        atol=4.0e-14,
    )

    step = 1.0e-5

    def explicit_state_and_observables(budget: float) -> tuple[np.ndarray, np.ndarray]:
        generator = _explicit_row_generator(model, budget)
        state = np.asarray(
            expm_multiply(time_value * generator.T, model.initial),
            dtype=float,
        )
        jets = _time_jets(generator, state, model.killing_per_budget, budget)
        return state, np.concatenate((jets[:3], (np.sum(state),)))

    plus_state, plus_observables = explicit_state_and_observables(model.budget + step)
    minus_state, minus_observables = explicit_state_and_observables(model.budget - step)
    finite_difference_state = (plus_state - minus_state) / (2.0 * step)
    np.testing.assert_allclose(
        observed_augmented[states:],
        finite_difference_state,
        rtol=2.0e-7,
        atol=3.0e-10,
    )

    direct_state = observed_augmented[:states]
    direct_jets = _time_jets(
        row_generator,
        direct_state,
        model.killing_per_budget,
        model.budget,
    )
    fake_root = {
        "time": time_value,
        "density": float(direct_jets[0]),
        "f_t": float(direct_jets[1]),
        "f_tt": float(direct_jets[2]),
        "f_ttt": float(direct_jets[3]),
    }
    control = positive.budget_control_jets(model, [fake_root], [direct_state])
    observed_control = control["rows"][0]["budget_control_jets"]
    finite_difference_observables = (plus_observables - minus_observables) / (2.0 * step)
    np.testing.assert_allclose(
        (
            observed_control["f_B"],
            observed_control["f_tB"],
            observed_control["f_ttB"],
            observed_control["survival_B"],
        ),
        finite_difference_observables,
        rtol=3.0e-7,
        atol=5.0e-10,
    )
    assert control["maximum_direct_vs_tangent_state_relative_l1"] <= 2.0e-12
    assert control["maximum_direct_vs_tangent_time_jet_absolute_difference"] <= 2.0e-12


def test_actual_stationary_root_checkpoint_matches_direct_propagation_from_zero() -> None:
    model = positive.build_model(9, _small_manifest())
    times = np.linspace(0.5, 35.0, 139)
    with positive.pinned_numpy_global_seed(271828):
        states = np.asarray(
            expm_multiply(
                model.operator,
                model.initial,
                start=times[0],
                stop=times[-1],
                num=times.size,
                endpoint=True,
                traceA=model.operator.trace_value,
            ),
            dtype=float,
        )
    derivatives = model.budget * (states @ model.q1)
    sign_changes = np.flatnonzero(derivatives[:-1] * derivatives[1:] < 0.0)
    assert sign_changes.size >= 1
    index = int(sign_changes[0])
    left = float(times[index])
    right = float(times[index + 1])
    checkpoint = states[index]

    def local_derivative(time_value: float) -> float:
        state = positive.propagate(
            model.operator,
            checkpoint,
            time_value - left,
            model.operator.trace_value,
        )
        return float(model.budget * (state @ model.q1))

    with positive.pinned_numpy_global_seed(271828):
        root = float(brentq(local_derivative, left, right, xtol=3.0e-12, rtol=1.0e-13))
        local_state = positive.propagate(
            model.operator,
            checkpoint,
            root - left,
            model.operator.trace_value,
        )
        direct_state = positive.propagate(
            model.operator,
            model.initial,
            root,
            model.operator.trace_value,
        )
    np.testing.assert_allclose(local_state, direct_state, rtol=2.0e-10, atol=2.0e-13)
    assert abs(model.budget * (local_state @ model.q1)) <= 2.0e-12


def test_survival_derivative_generator_identity_and_three_basin_closure() -> None:
    model = positive.build_model(9, _small_manifest())
    row_generator = _explicit_row_generator(model)
    np.testing.assert_allclose(
        row_generator @ np.ones(model.initial.size),
        -model.budget * model.killing_per_budget,
        rtol=2.0e-14,
        atol=2.0e-13,
    )
    state = np.asarray(expm_multiply(3.0 * row_generator.T, model.initial), dtype=float)
    survival_derivative = float(np.sum(row_generator.T @ state))
    density = float(model.budget * (state @ model.killing_per_budget))
    np.testing.assert_allclose(survival_derivative, -density, rtol=2.0e-13, atol=2.0e-14)

    states = [
        np.asarray(expm_multiply(time * row_generator.T, model.initial), dtype=float)
        for time in (5.0, 15.0, 100.0)
    ]
    survivals = [float(np.sum(value)) for value in states]
    masses = (
        1.0 - survivals[0],
        survivals[0] - survivals[1],
        survivals[1] - survivals[2],
    )
    assert min(masses) > 0.0
    assert abs(sum(masses) - (1.0 - survivals[2])) <= 3.0e-15


def test_tail_checkpoints_match_direct_propagation_and_fail_closed_gates() -> None:
    manifest = _small_manifest()
    model = positive.build_model(9, manifest)
    row_generator = _explicit_row_generator(model)
    scan_end_state = np.asarray(
        expm_multiply(35.0 * row_generator.T, model.initial),
        dtype=float,
    )
    scan = {"time_grid": {"stop": 35.0}}
    with positive.pinned_numpy_global_seed(271828):
        tail, final_state, final_projection = positive.propagate_tail(
            model,
            scan_end_state,
            scan,
            manifest,
        )
    for row in tail["trace"]:
        direct = np.asarray(
            expm_multiply(float(row["time"]) * row_generator.T, model.initial),
            dtype=float,
        )
        np.testing.assert_allclose(
            row["density"],
            model.budget * (direct @ model.q0),
            rtol=3.0e-10,
            atol=3.0e-13,
        )
        np.testing.assert_allclose(
            row["survival"],
            np.sum(direct),
            rtol=3.0e-10,
            atol=3.0e-13,
        )
    np.testing.assert_allclose(final_state, direct, rtol=3.0e-10, atol=3.0e-13)
    np.testing.assert_allclose(final_projection[4], np.sum(direct), rtol=0.0, atol=2.0e-14)
    assert tail["survival_decrease_from_scan_stop"] > 0.0
    assert all(positive.tail_gate_results(tail, manifest).values())

    bad_survival = copy.deepcopy(tail)
    bad_survival["maximum_checkpoint_survival_increase"] = 1.0e-4
    assert not positive.tail_gate_results(bad_survival, manifest)[
        "tail_checkpoint_survival_nonincreasing"
    ]
    bad_density = copy.deepcopy(tail)
    bad_density["minimum_checkpoint_density"] = -1.0e-8
    assert not positive.tail_gate_results(bad_density, manifest)["tail_checkpoint_density_positive"]
    bad_state = copy.deepcopy(tail)
    bad_state["minimum_tail_state_component"] = -1.0e-5
    assert not positive.tail_gate_results(bad_state, manifest)["tail_state_positivity_tolerance"]


def test_structural_hold_agreements_use_null_and_write_canonical_json(tmp_path: Path) -> None:
    manifest = positive.load_json(positive.MANIFEST)
    good_times = [3.0, 5.0, 9.0, 14.0, 23.0]
    expected_topology = ["maximum", "minimum", "maximum", "minimum", "maximum"]
    cases = [
        (
            _agreement_row(113, [], topology=[], valleys=None, masses=None),
            _agreement_row(
                129,
                good_times,
                topology=expected_topology,
                valleys=[0.8, 0.82],
                masses=[0.01, 0.02, 0.15],
                peak_ratio=0.5,
            ),
        ),
        (
            _agreement_row(113, [3.0, 5.0, 9.0], valleys=None, masses=None),
            _agreement_row(
                129,
                good_times,
                topology=expected_topology,
                valleys=[0.8, 0.82],
                masses=[0.01, 0.02, 0.15],
                peak_ratio=0.5,
            ),
        ),
        (
            _agreement_row(
                113,
                good_times,
                topology=["minimum", "maximum", "minimum", "maximum", "minimum"],
                valleys=[0.8, 0.82],
                masses=[0.01, 0.02, 0.15],
                peak_ratio=0.5,
            ),
            _agreement_row(
                129,
                good_times,
                topology=expected_topology,
                valleys=[0.8, 0.82],
                masses=[0.01, 0.02, 0.15],
                peak_ratio=0.5,
            ),
        ),
        (
            _agreement_row(
                113,
                good_times,
                topology=expected_topology,
                valleys=None,
                masses=None,
                peak_ratio=0.5,
            ),
            _agreement_row(
                129,
                good_times,
                topology=expected_topology,
                valleys=[0.8, 0.82],
                masses=[0.01, 0.02, 0.15],
                peak_ratio=0.5,
            ),
        ),
    ]
    for index, rows in enumerate(cases):
        agreement = positive.mesh_agreement(list(rows), manifest)
        assert agreement["all_agreement_gates_passed"] is False
        assert not all(agreement["gates"].values())
        assert (
            agreement["maximum_paired_root_time_difference"] is None
            or agreement["maximum_valley_ratio_absolute_difference"] is None
            or agreement["maximum_event_mass_absolute_difference"] is None
        )
        payload = {"all_gates_passed": False, "mesh_agreement": agreement}
        positive.require_finite_json(payload)
        left = tmp_path / f"hold_{index}_left.json"
        right = tmp_path / f"hold_{index}_right.json"
        positive.write_json(left, payload)
        positive.write_json(right, payload)
        assert left.read_bytes() == right.read_bytes()
        assert b"Infinity" not in left.read_bytes()
        assert b"NaN" not in left.read_bytes()
        assert None in json.loads(left.read_text(encoding="utf-8"))["mesh_agreement"].values()


def test_seed_context_restores_rng_and_sparse_exponential_probe_is_bitwise_stable() -> None:
    outer_state = np.random.get_state()
    try:
        np.random.seed(20260713)
        before = np.random.get_state()
        with positive.pinned_numpy_global_seed(271828):
            _ = np.random.randint(0, 2, size=1000)
        after = np.random.get_state()
        _assert_rng_states_equal(before, after)

        model = positive.build_model(9, _small_manifest())

        def probe() -> bytes:
            with positive.pinned_numpy_global_seed(271828):
                state = positive.propagate(
                    model.operator,
                    model.initial,
                    0.7,
                    model.operator.trace_value,
                )
                tangent_operator = positive.BudgetTangentColumnOperator(model.operator)
                augmented = positive.propagate(
                    tangent_operator,
                    np.concatenate((model.initial, np.zeros_like(model.initial))),
                    0.7,
                    tangent_operator.trace_value,
                )
            return (
                np.ascontiguousarray(state, dtype="<f8").tobytes()
                + np.ascontiguousarray(augmented, dtype="<f8").tobytes()
            )

        assert probe() == probe()
    finally:
        np.random.set_state(outer_state)


def test_frozen_manifest_is_fail_closed_and_pins_every_dependency() -> None:
    if not positive.MANIFEST.exists():
        return
    manifest = positive.load_json(positive.MANIFEST)
    observed = positive.validate_manifest(manifest)
    assert manifest["heldout_meshes"] == [113, 129]
    assert manifest["positive_budget"] == 0.01
    assert manifest["fixed_absolute_weights"] == positive.FROZEN_WEIGHTS
    assert manifest["time_scan"] == positive.FROZEN_TIME_SCAN
    assert manifest["root_gates"] == positive.FROZEN_ROOT_GATES
    assert manifest["event_mass"] == positive.FROZEN_EVENT_MASS
    assert manifest["tail_gates"] == positive.FROZEN_TAIL_GATES
    assert manifest["mesh_agreement"] == positive.FROZEN_MESH_AGREEMENT
    assert manifest["claim_scope"] == positive.CLAIM_SCOPE
    assert manifest["physical_parameters"] == positive.FROZEN_PHYSICAL_PARAMETERS
    assert manifest["preflight_validation"] == positive.FROZEN_PREFLIGHT
    assert manifest["execution_boundary"] == positive.FROZEN_EXECUTION_BOUNDARY
    assert manifest["forbidden_promotions"] == positive.FROZEN_FORBIDDEN_PROMOTIONS
    assert manifest["required_claim_flags"] == positive.FROZEN_NEGATIVE_FLAGS
    assert manifest["numerical_reproducibility"] == positive.FROZEN_REPRODUCIBILITY
    assert set(observed) == {
        "producer",
        "tests",
        "protocol",
        "operational_erratum",
        "B0_bridge_result",
        "B0_bridge_manifest",
        "B0_bridge_producer",
        "exact_continuum_dependency",
        "finite_volume_dependency",
        "grid_dependency",
        "feasibility_producer",
        "feasibility_N65_all_budgets",
        "feasibility_N97_B001",
        "feasibility_N97_B002",
    }


def test_manifest_rejects_scope_provenance_parameter_and_pin_mutations() -> None:
    manifest = positive.load_json(positive.MANIFEST)
    positive.validate_manifest(manifest)
    mutations: list[dict[str, Any]] = []

    changed = copy.deepcopy(manifest)
    changed["physical_parameters"]["contact_radius"] = 0.17
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["claim_scope"] = "continuum theorem verified"
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["known_before_freeze"]["positive_B_mesh_113_evaluated"] = True
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["selection_record"]["other_budget_forbidden_on_heldout_meshes"] = False
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["preflight_validation"]["structural_HOLD_null_serialization"] = False
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["execution_boundary"]["canonical_result_promoted_only_after_byte_identity"] = False
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["forbidden_promotions"] = []
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    del changed["pinned_files"]["tests"]
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["pinned_files"]["extra"] = copy.deepcopy(changed["pinned_files"]["producer"])
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["pinned_files"]["tests"]["path"] = changed["pinned_files"]["protocol"]["path"]
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["pinned_files"]["tests"]["path"] = "/etc/passwd"
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["pinned_files"]["tests"]["path"] = "../AGENTS.md"
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["pinned_files"]["tests"]["sha256"] = "A" * 64
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["continuum_theorem_verified"] = True
    mutations.append(changed)
    changed = copy.deepcopy(manifest)
    changed["tail_gates"]["checkpoints"] = [35.0, 100.0]
    mutations.append(changed)

    for changed in mutations:
        with pytest.raises(ValueError):
            positive.validate_manifest(changed)


def test_two_independent_process_harness_promotes_only_identical_results(
    tmp_path: Path,
) -> None:
    writer = tmp_path / "replica_writer.py"
    writer.write_text(
        "\n".join(
            (
                "import json, os, sys",
                "from pathlib import Path",
                "output, log, variant, manifest_hash, outcome = sys.argv[1:]",
                "passed = outcome == 'PASS'",
                "status = ('PASS_RESULT_INFORMED_POSITIVE_B_EVENT_MASS_SHAPE_CONFIRMATION' "
                "if passed else 'HOLD_RESULT_INFORMED_POSITIVE_B_CONFIRMATION')",
                "payload = {'all_gates_passed': passed, 'manifest_sha256': manifest_hash, "
                "'status': status, 'variant': variant}",
                "Path(output).write_text(json.dumps(payload, indent=2, sort_keys=True, "
                "allow_nan=False) + '\\n', encoding='utf-8')",
                "with Path(log).open('a', encoding='utf-8') as handle: "
                "handle.write(str(os.getpid()) + '\\n')",
                "raise SystemExit(0 if passed else 2)",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    frozen_manifest = tmp_path / "frozen_manifest.json"
    frozen_manifest.write_text("{}\n", encoding="utf-8")
    manifest_hash = positive.sha256(frozen_manifest)
    environment = os.environ.copy()

    observed_pids: list[int] = []
    for outcome in ("HOLD", "PASS"):
        canonical = tmp_path / f"{outcome.lower()}_canonical.json"
        evidence = tmp_path / f"{outcome.lower()}_evidence.json"
        replicas = (
            tmp_path / f"{outcome.lower()}_replica_1.json",
            tmp_path / f"{outcome.lower()}_replica_2.json",
        )
        log = tmp_path / f"{outcome.lower()}_pids.txt"
        commands = [
            [
                sys.executable,
                str(writer),
                str(replica),
                str(log),
                "same",
                manifest_hash,
                outcome,
            ]
            for replica in replicas
        ]
        result = positive.run_replica_commands(
            commands,
            replicas,
            canonical,
            evidence,
            frozen_manifest,
            manifest_hash,
            environment,
        )
        assert result["all_gates_passed"] is (outcome == "PASS")
        assert canonical.is_file()
        audit = positive.load_json(evidence)
        assert audit["byte_identical"] is True
        assert audit["independent_process_count"] == 2
        pids = [int(value) for value in log.read_text(encoding="utf-8").splitlines()]
        assert len(pids) == len(set(pids)) == 2
        observed_pids.extend(pids)
    assert len(observed_pids) == len(set(observed_pids)) == 4

    mismatch_canonical = tmp_path / "mismatch_canonical.json"
    mismatch_evidence = tmp_path / "mismatch_evidence.json"
    old_canonical = b"old canonical sentinel\n"
    old_evidence = b"old evidence sentinel\n"
    mismatch_canonical.write_bytes(old_canonical)
    mismatch_evidence.write_bytes(old_evidence)
    mismatch_replicas = (
        tmp_path / "mismatch_replica_1.json",
        tmp_path / "mismatch_replica_2.json",
    )
    mismatch_log = tmp_path / "mismatch_pids.txt"
    mismatch_commands = [
        [
            sys.executable,
            str(writer),
            str(replica),
            str(mismatch_log),
            variant,
            manifest_hash,
            "HOLD",
        ]
        for replica, variant in zip(mismatch_replicas, ("left", "right"), strict=True)
    ]
    with pytest.raises(RuntimeError, match="not byte-identical"):
        positive.run_replica_commands(
            mismatch_commands,
            mismatch_replicas,
            mismatch_canonical,
            mismatch_evidence,
            frozen_manifest,
            manifest_hash,
            environment,
        )
    assert mismatch_canonical.read_bytes() == old_canonical
    assert mismatch_evidence.read_bytes() == old_evidence


def test_formal_hold_schema_has_no_nondeterministic_metadata_and_retains_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = positive.load_json(positive.MANIFEST)
    monkeypatch.setattr(positive, "validate_manifest", lambda _manifest: {"producer": "fixed"})
    monkeypatch.setattr(
        positive,
        "solve_mesh",
        lambda cells, _manifest: _agreement_row(
            int(cells),
            [],
            topology=[],
            valleys=None,
            masses=None,
            peak_ratio=None,
        ),
    )
    result = positive._run_with_seed_active(manifest)  # noqa: SLF001

    def keys(value: Any) -> set[str]:
        if isinstance(value, dict):
            return set(value).union(*(keys(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(keys(item) for item in value))
        return set()

    forbidden = {
        "elapsed_seconds",
        "timestamp",
        "temporary_path",
        "temp_path",
        "output_path",
    }
    assert keys(result).isdisjoint(forbidden)
    assert result["positive_budget"] == 0.01
    assert [row["mesh"][0] for row in result["heldout_mesh_rows"]] == [113, 129]
    assert result["weights_refit"] is False
    assert result["preregistered_discovery"] is False
    assert result["continuum_interval_verified"] is False
    assert result["unbounded_domain_FV_limit_verified"] is False
    assert result["independent_solver_verified"] is False
    assert result["project_gate_passed"] is False
    assert result["status"] == "HOLD_RESULT_INFORMED_POSITIVE_B_CONFIRMATION"
    assert result["all_gates_passed"] is False
    assert result["mesh_agreement"]["maximum_paired_root_time_difference"] is None
    assert result["mesh_agreement"]["maximum_valley_ratio_absolute_difference"] is None
    assert result["mesh_agreement"]["maximum_event_mass_absolute_difference"] is None
    positive.require_finite_json(result)
    assert positive.canonical_json_bytes(result)


def test_no_tex_or_temporary_output_is_pinned() -> None:
    if not positive.MANIFEST.exists():
        return
    manifest = positive.load_json(positive.MANIFEST)
    paths = [item["path"] for item in manifest["pinned_files"].values()]
    paths.extend(
        (
            str(Path(positive.MANIFEST).relative_to(positive.REPORT)),
            str(Path(positive.OUTPUT).relative_to(positive.REPORT)),
        )
    )
    assert not any(path.endswith(".tex") for path in paths)
    assert not any("tmp" in path.lower() or "temp" in path.lower() for path in paths)


def test_formal_json_writer_is_canonical_and_byte_stable(tmp_path: Path) -> None:
    payload = {
        "z": [3.0, 2.0, 1.0],
        "a": {"value": 0.01, "flag": False},
    }
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    positive.write_json(left, payload)
    positive.write_json(right, payload)
    assert left.read_bytes() == right.read_bytes()
    assert json.loads(left.read_text(encoding="utf-8")) == payload


def test_gate_normalization_accepts_only_boolean_scalars_and_serializes_numpy_bool(
    tmp_path: Path,
) -> None:
    gates = positive.native_json_boolean_gates(
        {
            "native_true": True,
            "native_false": False,
            "numpy_true": np.float64(1.0) > 0.0,
            "numpy_false": np.float64(-1.0) > 0.0,
        }
    )
    assert gates == {
        "native_true": True,
        "native_false": False,
        "numpy_true": True,
        "numpy_false": False,
    }
    assert all(type(value) is bool for value in gates.values())
    target = tmp_path / "boolean_gates.json"
    positive.write_json(target, {"gates": gates})
    assert json.loads(target.read_text(encoding="utf-8"))["gates"] == gates

    for forbidden in (0, 1, 0.0, 1.0, "true", None):
        with pytest.raises(TypeError, match="must be a Boolean scalar"):
            positive.native_json_boolean_gates({"bad": forbidden})


def test_recursive_nonfinite_json_is_rejected_before_write(tmp_path: Path) -> None:
    for value in (float("inf"), float("-inf"), float("nan")):
        target = tmp_path / "forbidden.json"
        with pytest.raises(ValueError, match="non-finite"):
            positive.write_json(target, {"outer": [{"inner": value}]})
        assert not target.exists()
