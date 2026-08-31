"""Round-50 red-team contracts retained as ordinary v2 regression tests."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import positive_b_allocation_cusp_discovery as discovery
import pytest
from numpy.testing import assert_allclose

REPORT = Path(__file__).resolve().parents[1]


def _fold_snapshot(time: float) -> discovery.Snapshot:
    jets = np.asarray((1.0, 0.0, 0.0, 1.0, -1.0))
    cusp_jacobian = np.asarray(
        (
            (0.0, 1.0, 0.0),
            (1.0, 0.0, 1.0),
            (-1.0, 0.0, 0.0),
        )
    )
    allocation_jets = np.zeros((2, 5))
    allocation_jets[:, 1:4] = cusp_jacobian[:, 1:].T
    theta = np.zeros(2)
    return discovery.Snapshot(
        time=float(time),
        budget=0.01,
        theta=theta,
        weights=discovery.weights_from_theta(theta),
        state=np.ones(1),
        state_tangents=np.zeros((2, 1)),
        jets=jets,
        allocation_jets=allocation_jets,
        cusp_map=jets[1:4],
        cusp_jacobian=cusp_jacobian,
        survival_identity_residuals=np.zeros(3),
    )


def _passing_control_law(maximum_count: int) -> dict[str, object]:
    return {
        "retained_maximum_count": maximum_count,
        "robustness_score": 1.0,
        "gates": {"alternating_topology": True, "endpoint_signs": True},
        "all_gates_passed": True,
    }


def test_same_physical_family_budget_box_and_b0_svd_chart_are_exact() -> None:
    allocation = discovery.load_json(discovery.MANIFEST)
    positive_b = discovery.load_json(
        REPORT / "artifacts" / "data" / "positive_b_broad_four_slab_manifest.json"
    )
    assert allocation["physical_parameters"] == positive_b["physical_parameters"]
    assert allocation["finite_volume"] == positive_b["finite_volume"]
    assert allocation["budget_homotopy"]["target_budget"] == positive_b["positive_budget"]

    helmert = np.asarray(
        (
            (1 / np.sqrt(2), 1 / np.sqrt(6), 1 / np.sqrt(12)),
            (-1 / np.sqrt(2), 1 / np.sqrt(6), 1 / np.sqrt(12)),
            (0.0, -2 / np.sqrt(6), 1 / np.sqrt(12)),
            (0.0, 0.0, -3 / np.sqrt(12)),
        )
    )
    response = np.asarray(
        (
            (3.07036526, -2.09946043, -4.00539310),
            (-11.35829709, 26.40000057, -6.05167654),
        )
    )
    _left, singular, right = np.linalg.svd(response, full_matrices=True)
    chart = helmert @ right[:2].T
    for column in range(2):
        largest = int(np.argmax(np.abs(chart[:, column])))
        if chart[largest, column] < 0.0:
            chart[:, column] *= -1.0
    assert_allclose(
        singular,
        allocation["allocation_chart"]["source_nonzero_singular_values"],
        rtol=2.0e-10,
        atol=2.0e-9,
    )
    assert_allclose(chart, discovery.TANGENT_BASIS, rtol=2.0e-8, atol=5.0e-9)
    assert_allclose(np.ones(4) @ chart, 0.0, atol=2.0e-15)
    assert_allclose(chart.T @ chart, np.eye(2), atol=2.0e-15)


def test_mesh_97_is_honestly_discovery_not_heldout_and_outputs_are_absent() -> None:
    manifest = discovery.load_json(discovery.MANIFEST)
    assert manifest["execution_boundary"]["scientific_meshes"] == [65, 97]
    assert manifest["phase_search"]["centre"] == "mesh_97 positive-B cusp theta"
    assert manifest["required_claim_flags"]["heldout_mesh_confirmation_verified"] is False
    assert "held-out mesh confirmation" in manifest["forbidden_claims"]
    assert not discovery.OUTPUT.exists()
    assert not discovery.REPRODUCIBILITY_OUTPUT.exists()
    assert all(not path.exists() for path in discovery.replica_paths())


def test_no_candidate_is_a_legitimate_bounded_hold(monkeypatch: pytest.MonkeyPatch) -> None:
    candidates = [
        {
            "candidate_index": index,
            "radius": 0.02,
            "direction": [1.0, 0.0],
            "theta": [0.0, 0.0],
            "weights": discovery.REFERENCE_WEIGHTS.tolist(),
            "eligible_geometry": False,
        }
        for index in range(32)
    ]
    monkeypatch.setattr(discovery, "candidate_controls", lambda _theta: candidates)
    phase = discovery.phase_discovery(
        SimpleNamespace(cells=65), SimpleNamespace(cells=97), np.zeros(2)
    )
    assert phase["all_three_regions_found"] is False
    assert phase["search_expanded"] is False
    assert phase["representatives"] == {"1": None, "2": None, "3": None}
    assert phase["advanced_mesh_97"] == []


def test_final_survival_and_final_state_must_be_positive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scan = {
        "roots": [
            {
                "time": 2.0,
                "density_per_budget": 1.0,
                "scaled_root_residual": 0.0,
                "scaled_curvature": -1.0,
                "type": "maximum",
            }
        ],
        "topology": ["maximum"],
        "endpoint_signs_passed": True,
        "minimum_sampled_state": 0.0,
        "maximum_sampled_survival_increase": 0.0,
    }
    monkeypatch.setattr(discovery, "stationary_scan", lambda *_args, **_kwargs: scan)
    monkeypatch.setattr(
        discovery,
        "evaluate_without_tangents",
        lambda *_args, **_kwargs: (np.asarray((-0.5,)), np.zeros(5)),
    )
    row = discovery.evaluate_control_law(SimpleNamespace(), np.zeros(2), 0.05)
    assert row["final_survival"] is None
    assert row["all_gates_passed"] is False
    assert row["gates"]["positive_density_and_survival"] is False
    assert row["gates"]["final_state_nonnegative"] is False


def test_nonfinite_control_evaluation_must_be_a_finite_structural_hold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scan = {
        "roots": [
            {
                "time": 2.0,
                "density_per_budget": float("nan"),
                "scaled_root_residual": 0.0,
                "scaled_curvature": -1.0,
                "type": "maximum",
            }
        ],
        "topology": ["maximum"],
        "endpoint_signs_passed": True,
        "minimum_sampled_state": 0.0,
        "maximum_sampled_survival_increase": 0.0,
    }
    monkeypatch.setattr(discovery, "stationary_scan", lambda *_args, **_kwargs: scan)
    monkeypatch.setattr(
        discovery,
        "evaluate_without_tangents",
        lambda *_args, **_kwargs: (np.asarray((0.5,)), np.zeros(5)),
    )
    row = discovery.evaluate_control_law(SimpleNamespace(), np.zeros(2), 0.05)
    discovery.require_finite_json(row)
    assert row["all_gates_passed"] is False


def test_preflight_hold_must_abort_before_any_scientific_mesh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = discovery.load_json(discovery.MANIFEST)
    manifest_hash = discovery.sha256(discovery.MANIFEST)
    builds: list[tuple[int, bool]] = []

    def fake_build(cells: int, _manifest: dict, *, formal: bool) -> SimpleNamespace:
        builds.append((cells, formal))
        return SimpleNamespace(cells=cells)

    def fake_solve(model: SimpleNamespace) -> tuple[dict[str, object], SimpleNamespace]:
        return (
            {
                "mesh": [model.cells] * 3,
                "status": "PASS_MESH_DISCOVERY",
                "all_mesh_discovery_gates_passed": True,
            },
            SimpleNamespace(theta=np.zeros(2)),
        )

    monkeypatch.setattr(
        discovery,
        "validate_manifest",
        lambda _manifest, **_kwargs: {"runner": "hash"},
    )
    monkeypatch.setattr(discovery, "require_loaded_native_phase", lambda *_args: None)
    monkeypatch.setattr(discovery, "build_model", fake_build)
    monkeypatch.setattr(discovery, "explicit_csr_preflight", lambda _model: {"passed": False})
    monkeypatch.setattr(discovery, "solve_discovery_mesh", fake_solve)
    monkeypatch.setattr(
        discovery,
        "phase_discovery",
        lambda *_args: {"all_three_regions_found": True},
    )
    result = discovery.run_formal(manifest, manifest_hash)
    assert result["status"] == discovery.HOLD_STATUS
    assert builds == [(7, False)]


def test_fold_branch_must_keep_signed_orientation_and_distinct_comparison_nodes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cusp = _fold_snapshot(13.0)
    branch_times = iter((13.05, 13.0, 12.9, 12.7, 12.45, 12.2))
    remote_call = {"value": 0}

    monkeypatch.setattr(
        discovery,
        "fold_predictor",
        lambda _cusp, _offset: np.asarray((13.1, 0.0, 0.0)),
    )
    monkeypatch.setattr(
        discovery,
        "correct_fold_fixed_time",
        lambda *_args, **_kwargs: {
            "status": "PASS_BRANCH_NODE",
            "snapshot": _fold_snapshot(13.1),
            "iterations": 1,
        },
    )
    monkeypatch.setattr(
        discovery,
        "fold_null_direction",
        lambda *_args, **_kwargs: np.asarray((1.0, 0.0, 0.0)),
    )

    def fake_correct(*_args: object, **_kwargs: object) -> dict[str, object]:
        try:
            time = next(branch_times)
        except StopIteration:
            return {"status": "HOLD_BRANCH", "snapshot": None, "iterations": 4}
        return {
            "status": "PASS_BRANCH_NODE",
            "snapshot": _fold_snapshot(time),
            "iterations": 4,
        }

    def fake_remote(*_args: object, **_kwargs: object) -> dict[str, object]:
        index = remote_call["value"]
        remote_call["value"] += 1
        return {
            "remote_pair_present": True,
            "pair": {
                "maximum": {"time": 2.0 + index},
                "minimum": {"time": 2.5 + index},
            },
            "candidate_search_bounded_to_frozen_window": True,
        }

    monkeypatch.setattr(discovery, "pseudo_arclength_correct", fake_correct)
    monkeypatch.setattr(discovery, "stationary_scan", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(discovery, "assess_remote_pair", fake_remote)
    branch = discovery.continue_branch(SimpleNamespace(), cusp, 0.1)
    assert branch["status"] == "HOLD_BRANCH"
    assert branch["comparison_nodes"] is None
    assert branch["gates"]["required_reach"] is False
    assert branch["gates"]["comparison_nodes_present"] is False


def test_phase_search_must_hold_if_any_eligible_screen_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidates = []
    for index, marker in enumerate((1.0, 2.0, 3.0, 9.0)):
        candidates.append(
            {
                "candidate_index": index,
                "radius": 0.02,
                "direction": [1.0, 0.0],
                "theta": [marker, 0.0],
                "weights": [0.1 + 0.01 * index, 0.2, 0.3, 0.4 - 0.01 * index],
                "eligible_geometry": True,
            }
        )

    def fake_evaluate(
        model: SimpleNamespace, theta: np.ndarray, _spacing: float
    ) -> dict[str, object]:
        marker = int(round(float(theta[0])))
        if model.cells == 65 and marker == 9:
            raise RuntimeError("injected eligible-control failure")
        return _passing_control_law(marker)

    monkeypatch.setattr(discovery, "candidate_controls", lambda _theta: candidates)
    monkeypatch.setattr(discovery, "evaluate_control_law", fake_evaluate)
    phase = discovery.phase_discovery(
        SimpleNamespace(cells=65), SimpleNamespace(cells=97), np.zeros(2)
    )
    assert any(
        row["mesh_65_evaluation_status"] == "HOLD_CONTROL_EVALUATION"
        for row in phase["screened_mesh_65"]
    )
    assert phase["all_three_regions_found"] is False


def test_phase_search_must_hold_if_any_selected_mesh_97_row_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidates = [
        {
            "candidate_index": index,
            "radius": 0.02,
            "direction": [1.0, 0.0],
            "theta": [float(index + 1), 0.0],
            "weights": [0.1, 0.2, 0.3, 0.4],
            "eligible_geometry": True,
        }
        for index in range(3)
    ]

    def fake_evaluate(
        model: SimpleNamespace, theta: np.ndarray, _spacing: float
    ) -> dict[str, object]:
        count = int(round(float(theta[0])))
        if model.cells == 97 and count == 2:
            raise RuntimeError("injected selected mesh-97 failure")
        return _passing_control_law(count)

    monkeypatch.setattr(discovery, "candidate_controls", lambda _theta: candidates)
    monkeypatch.setattr(discovery, "evaluate_control_law", fake_evaluate)
    phase = discovery.phase_discovery(
        SimpleNamespace(cells=65), SimpleNamespace(cells=97), np.zeros(2)
    )
    assert phase["phase_complete"] is False
    assert phase["all_three_regions_found"] is False
    assert phase["representatives"] == {"1": None, "2": None, "3": None}


def test_remote_pair_identity_is_deterministic_and_order_preserving() -> None:
    roots = [
        {
            "time": 2.0,
            "type": "maximum",
            "bracket_index": 4,
        },
        {
            "time": 2.5,
            "type": "minimum",
            "bracket_index": 5,
        },
        {
            "time": 15.0,
            "type": "maximum",
            "bracket_index": 8,
        },
        {
            "time": 15.5,
            "type": "minimum",
            "bracket_index": 9,
        },
    ]
    remote = discovery.assess_remote_pair({"roots": roots}, 13.0)
    assert remote["remote_pair_present"] is True
    assert remote["pair_identity"] == (
        "negative_time:maximum_minimum:global_0_1:origin_brackets_4_5"
    )
    assert remote["pair"]["selected_global_root_indices"] == [0, 1]
    assert remote["root_lineage"][0]["origin_bracket_index"] == 4
    assert remote["pair"]["maximum_bracket_index"] == 4
    assert remote["pair"]["minimum_bracket_index"] == 5


def test_phase_score_contract_must_exactly_match_the_pinned_design() -> None:
    manifest = discovery.load_json(discovery.MANIFEST)
    phase = manifest["phase_search"]
    assert phase["score_terms"] == [
        "peak_ratio",
        "valley_ratio",
        "absolute_scaled_curvature",
        "event_basin_mass",
    ]
    assert phase["root_residual_role"] == "eligibility_gate_not_ranking_term"
    formulas = phase["score_formulas"]
    assert set(formulas) == {
        "lower_bound_margin",
        "upper_bound_margin",
        "worst_control_score",
    }


def test_replica_must_revalidate_all_pins_after_scientific_calculation() -> None:
    source = Path(discovery.__file__).read_text(encoding="utf-8")
    replica_source = source[
        source.index("def execute_replica(") : source.index("def execute_frozen(")
    ]
    calculation = replica_source.index("result = run_formal")
    assert "pinned_after = validate_manifest(" in replica_source[calculation:]
    assert "capture_complete_freeze_snapshot(MANIFEST, manifest)" in replica_source[calculation:]


def test_replica_harness_must_validate_full_result_and_negative_claim_schema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text('{"frozen":true}\n', encoding="utf-8")
    manifest_hash = discovery.sha256(manifest_path)
    replicas = (tmp_path / ".replica_1.json", tmp_path / ".replica_2.json")
    canonical = tmp_path / "canonical.json"
    evidence = tmp_path / "evidence.json"
    malformed = {
        "status": discovery.PASS_STATUS,
        "all_discovery_gates_passed": True,
        "manifest_sha256": manifest_hash,
        "discovery_mesh_rows": [],
        "required_claim_flags": {
            "heldout_mesh_confirmation_verified": True,
            "publication_gate_passed": True,
        },
        "forbidden_claims": [],
    }
    payload = discovery.canonical_json_bytes(malformed)
    calls = {"value": 0}

    def fake_run(*_args: object, **_kwargs: object) -> SimpleNamespace:
        replicas[calls["value"]].write_bytes(payload)
        calls["value"] += 1
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(discovery.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="result contract"):
        discovery.run_replica_commands(
            (("one",), ("two",)),
            replicas,
            manifest_path,
            manifest_hash,
            {},
            canonical,
            evidence,
        )


def test_atomic_promotion_must_detect_postreplace_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    canonical = tmp_path / "result.json"
    evidence = tmp_path / "evidence.json"
    result_bytes = discovery.canonical_json_bytes({"result": True})
    evidence_bytes = discovery.canonical_json_bytes({"evidence": True})
    original = discovery.fsync_directory
    calls = {"value": 0}

    def mutate_after_sync(path: Path) -> None:
        original(path)
        calls["value"] += 1
        if calls["value"] == 2:
            canonical.write_bytes(b"corrupted-after-replace\n")

    monkeypatch.setattr(discovery, "fsync_directory", mutate_after_sync)
    with pytest.raises(RuntimeError, match="post-replace canonical byte verification"):
        discovery.promote_replica_bytes(result_bytes, evidence_bytes, canonical, evidence)
    assert not canonical.exists()
    assert not evidence.exists()


def test_representative_contract_must_include_all_frozen_conservation_gates() -> None:
    manifest = discovery.load_json(discovery.MANIFEST)
    required_manifest_gates = {
        "minimum_survival",
        "maximum_survival_identity_error",
        "maximum_generator_killing_identity_error",
        "maximum_differential_mass_balance_error",
        "maximum_event_partition_closure_error",
    }
    assert required_manifest_gates <= set(manifest["representative_gates"])
    runner = Path(discovery.__file__).read_text(encoding="utf-8")
    for required_result_gate in (
        '"positive_density_and_survival"',
        '"survival_density_identity"',
        '"generator_killing_identity"',
        '"differential_mass_balance"',
        '"event_partition_closure"',
        '"final_state_nonnegative"',
    ):
        assert required_result_gate in runner
