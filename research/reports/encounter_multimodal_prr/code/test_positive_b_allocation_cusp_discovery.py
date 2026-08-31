from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import positive_b_allocation_cusp_discovery as discovery
import pytest
from numpy.testing import assert_allclose


@pytest.fixture(scope="module")
def manifest() -> dict:
    return discovery.load_json(discovery.MANIFEST)


@pytest.fixture(scope="module")
def model(manifest: dict) -> discovery.AllocationModel:
    return discovery.build_model(5, manifest, formal=False)


def synthetic_snapshot(
    time: float,
    budget: float,
    theta: np.ndarray,
    cusp_map: np.ndarray,
    cusp_jacobian: np.ndarray,
) -> discovery.Snapshot:
    jets = np.asarray((1.0, *np.asarray(cusp_map, dtype=float), -0.2))
    allocation_jets = np.zeros((2, 5))
    allocation_jets[:, 1:4] = np.asarray(cusp_jacobian, dtype=float)[:, 1:].T
    return discovery.Snapshot(
        time=float(time),
        budget=float(budget),
        theta=np.asarray(theta, dtype=float).copy(),
        weights=discovery.weights_from_theta(theta),
        state=np.ones(1),
        state_tangents=np.zeros((2, 1)),
        jets=jets,
        allocation_jets=allocation_jets,
        cusp_map=np.asarray(cusp_map, dtype=float),
        cusp_jacobian=np.asarray(cusp_jacobian, dtype=float),
        survival_identity_residuals=np.zeros(3),
    )


def valid_preflight_hold_payload(
    manifest_hash: str, pins: dict[str, str] | None = None
) -> dict[str, object]:
    pin_snapshot = {} if pins is None else dict(pins)

    def metadata(path: str, digest: str) -> dict[str, object]:
        return {
            "path": path,
            "st_dev": 1,
            "st_ino": 1,
            "st_mode": 0o100600,
            "st_nlink": 1,
            "st_uid": 1,
            "st_gid": 1,
            "st_size": 1,
            "st_mtime_ns": 1,
            "sha256": digest,
        }

    lexical = {"manifest": metadata("manifest.json", manifest_hash)}
    lexical.update({role: metadata(f"pin/{role}", digest) for role, digest in pin_snapshot.items()})
    return {
        "schema_version": discovery.SCHEMA_VERSION,
        "stage": discovery.STAGE,
        "status": discovery.HOLD_STATUS,
        "evidence_timing": discovery.EVIDENCE_TIMING,
        "claim_scope": discovery.expected_manifest_contract()["claim_scope"],
        "manifest_sha256": manifest_hash,
        "small_explicit_csr_preflight": {
            "mesh": [7, 7, 7],
            "state_count": 343,
            "errors": {
                "column_action": 2.0e-11,
                "row_action": 2.0e-11,
                "augmented_column_action": 2.0e-11,
                "augmented_row_action": 2.0e-11,
            },
            "maximum_error": 2.0e-11,
            "passed": False,
        },
        "discovery_mesh_rows": [
            discovery.not_run_mesh_row(
                cells,
                "explicit_csr_preflight_held_before_scientific_construction",
                "NOT_RUN_AFTER_PREFLIGHT_HOLD",
            )
            for cells in discovery.DISCOVERY_MESHES
        ],
        "bounded_phase_discovery": None,
        "all_discovery_gates_passed": False,
        "required_claim_flags": discovery.CLAIM_FLAGS,
        "forbidden_claims": discovery.FORBIDDEN_CLAIMS,
        "pin_snapshots": {
            "before_formal": pin_snapshot,
            "after_formal": pin_snapshot,
        },
        "lexical_pin_snapshots": {
            "before_formal": lexical,
            "after_formal": lexical,
        },
        "pinned_file_hashes": pin_snapshot,
        "software": {"python": "test", "numpy": "test", "scipy": "test"},
        "limitations": discovery.LIMITATIONS,
    }


def test_frozen_chart_homotopy_search_and_claim_boundaries() -> None:
    assert discovery.DISCOVERY_MESHES == (65, 97)
    assert discovery.BUDGET_HOMOTOPY["schedule"] == [0.0, 0.0025, 0.005, 0.0075, 0.01]
    assert discovery.BUDGET_HOMOTOPY["map"] == ["F_t", "F_tt", "F_ttt"]
    assert discovery.FOLD_CONTINUATION["predictor_time_offsets"] == [-0.1, 0.1]
    assert discovery.PHASE_SEARCH["candidate_count"] == 32
    assert discovery.PHASE_SEARCH["radii"] == [0.02, 0.05, 0.09, 0.13]
    assert discovery.PREFLIGHT["small_explicit_csr_cells"] == 7
    assert discovery.CLAIM_FLAGS == {
        "low_mesh_discovery_completed": False,
        "heldout_mesh_confirmation_verified": False,
        "parity_verified": False,
        "box_robustness_verified": False,
        "continuum_interval_verified": False,
        "unbounded_domain_verified": False,
        "independent_solver_verified": False,
        "publication_gate_passed": False,
    }
    assert_allclose(np.ones(4) @ discovery.TANGENT_BASIS, 0.0, atol=2.0e-15)
    assert_allclose(discovery.TANGENT_BASIS.T @ discovery.TANGENT_BASIS, np.eye(2), atol=2e-15)
    assert_allclose(np.sum(discovery.REFERENCE_WEIGHTS), 1.0, atol=2.0e-15)
    controls = discovery.candidate_controls(np.zeros(2))
    assert len(controls) == 32
    assert [row["candidate_index"] for row in controls] == list(range(32))
    assert not discovery.OUTPUT.exists()
    assert not discovery.REPRODUCIBILITY_OUTPUT.exists()

    for cells in discovery.DISCOVERY_MESHES:
        with pytest.raises(ValueError, match="dry-run cells"):
            discovery.validate_cells(cells, formal=False)
    for cells in (64, 98, 113, 129):
        with pytest.raises(ValueError, match="exactly meshes 65 and 97"):
            discovery.validate_cells(cells, formal=True)


def test_small_explicit_csr_and_mixed_observable_jets(
    model: discovery.AllocationModel,
) -> None:
    preflight = discovery.explicit_csr_preflight(model)
    assert preflight["passed"]
    assert preflight["maximum_error"] <= 1.0e-11

    time = 1.3
    budget = 0.01
    theta = np.asarray((0.013, -0.009))
    snapshot = discovery.evaluate_point(model, time, budget, theta)
    step = 2.0e-5
    for index in range(2):
        increment = np.zeros(2)
        increment[index] = step
        plus_state, plus_jets = discovery.evaluate_without_tangents(
            model, time, budget, theta + increment
        )
        minus_state, minus_jets = discovery.evaluate_without_tangents(
            model, time, budget, theta - increment
        )
        assert_allclose(
            snapshot.state_tangents[index],
            (plus_state - minus_state) / (2.0 * step),
            rtol=3.0e-6,
            atol=3.0e-11,
        )
        assert_allclose(
            snapshot.allocation_jets[index, :4],
            (plus_jets[:4] - minus_jets[:4]) / (2.0 * step),
            rtol=3.0e-6,
            atol=3.0e-10,
        )
    assert np.max(snapshot.survival_identity_residuals) <= 2.0e-14

    ambient = np.random.get_state()
    try:
        np.random.seed(9127)
        before = np.random.get_state()
        discovery.evaluate_without_tangents(model, 0.25, budget, theta)
        observed = np.random.random(5)
        np.random.set_state(before)
        expected = np.random.random(5)
        assert_allclose(observed, expected, rtol=0.0, atol=0.0)
    finally:
        np.random.set_state(ambient)


def test_small_grid_physical_law_and_factor_diagnostics(
    model: discovery.AllocationModel,
) -> None:
    theta = np.asarray((0.013, -0.009))
    diagnostics = discovery.allocation_model_diagnostics(model, 0.01, theta)
    snapshot = discovery.evaluate_point(model, 1.3, 0.01, theta)
    law = discovery.state_law_diagnostics(model, 0.01, theta, snapshot.state, snapshot.jets)
    gates = discovery.law_gate_results(diagnostics, [law])
    discovery.require_finite_json(diagnostics)
    discovery.require_finite_json(law)
    assert diagnostics["initial_mass_error"] <= 1.0e-12
    assert diagnostics["physical_installed_budget_absolute_error"] <= 1.0e-12
    assert diagnostics["generator_killing_identity_error"] <= 1.0e-11
    assert law["density"] > 0.0
    assert law["survival"] > 0.0
    assert law["survival_density_identity_error"] <= 1.0e-11
    assert all(gates.values())


def test_bounded_newton_is_deterministic_and_fails_closed() -> None:
    target = np.asarray((13.0, 0.01, -0.02))

    def evaluator(time: float, budget: float, theta: np.ndarray) -> discovery.Snapshot:
        point = np.asarray((time, *theta))
        return synthetic_snapshot(time, budget, theta, point - target, np.eye(3))

    solved = discovery.solve_cusp(evaluator, 0.01, np.asarray((12.8, 0.0, 0.0)))
    assert solved.converged
    assert solved.status == "PASS_CUSP_SOLVE"
    assert solved.iterations == 1
    assert_allclose(
        np.asarray((solved.snapshot.time, *solved.snapshot.theta)), target, atol=2.0e-15
    )

    def singular(time: float, budget: float, theta: np.ndarray) -> discovery.Snapshot:
        return synthetic_snapshot(time, budget, theta, np.ones(3), np.zeros((3, 3)))

    held = discovery.solve_cusp(singular, 0.01, np.asarray((13.0, 0.0, 0.0)))
    assert not held.converged
    assert held.status == discovery.HOLD_STATUS
    assert held.reason == "singular_jacobian"

    outside = discovery.solve_cusp(evaluator, 0.01, np.asarray((18.1, 0.0, 0.0)))
    assert not outside.converged
    assert outside.reason == "time_outside_trust_box"


def test_fold_predictor_equations_and_fixed_failure_schema() -> None:
    jets = np.asarray((1.0, 0.0, 0.0, 0.0, -0.2))
    allocation_jets = np.asarray(((0.0, 0.3, -0.2, 0.07, 0.0), (0.0, 0.1, 0.4, -0.05, 0.0)))
    jacobian = np.asarray(
        (
            (0.0, allocation_jets[0, 1], allocation_jets[1, 1]),
            (0.0, allocation_jets[0, 2], allocation_jets[1, 2]),
            (jets[4], allocation_jets[0, 3], allocation_jets[1, 3]),
        )
    )
    snapshot = discovery.Snapshot(
        13.0,
        0.01,
        np.zeros(2),
        discovery.REFERENCE_WEIGHTS.copy(),
        np.ones(1),
        np.zeros((2, 1)),
        jets,
        allocation_jets,
        jets[1:4],
        jacobian,
        np.zeros(3),
    )
    response = jacobian[:2, 1:]
    for offset in (-0.1, 0.1):
        predicted = discovery.fold_predictor(snapshot, offset)
        eta = predicted[1:] - snapshot.theta
        assert_allclose(
            response @ eta,
            np.asarray((jets[4] * offset**3 / 3.0, -jets[4] * offset**2 / 2.0)),
            atol=3.0e-18,
        )
    row = discovery.not_run_mesh_row(97, "mesh_65_held")
    assert row["status"] == "NOT_RUN_AFTER_HOLD"
    assert row["cusp"] is None
    assert row["branches"] is None
    assert row["all_mesh_discovery_gates_passed"] is False
    discovery.require_finite_json(row)


def test_manifest_is_exact_hash_pinned_and_result_blind(manifest: dict) -> None:
    observed = discovery.validate_manifest(manifest)
    assert set(observed) == set(discovery.PIN_PATHS)
    assert manifest["evidence_timing"] == discovery.EVIDENCE_TIMING
    assert manifest["known_before_freeze"]["allocation_cusp_mesh_65_evaluated"] is False
    assert manifest["known_before_freeze"]["allocation_cusp_mesh_97_evaluated"] is False
    assert manifest["known_before_freeze"]["formal_result_file_present"] is False

    mutation = copy.deepcopy(manifest)
    mutation["phase_search"]["radii"].append(0.14)
    with pytest.raises(ValueError, match="phase_search contract changed"):
        discovery.validate_manifest(mutation)
    mutation = copy.deepcopy(manifest)
    mutation["pinned_files"]["runner"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="runner hash mismatch"):
        discovery.validate_manifest(mutation)


def test_dry_run_never_executes_scientific_meshes(
    manifest: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    called = []
    original = discovery.build_model

    def guarded(cells: int, supplied: dict, *, formal: bool) -> discovery.AllocationModel:
        called.append((cells, formal))
        assert cells not in discovery.DISCOVERY_MESHES
        assert formal is False
        return original(cells, supplied, formal=formal)

    monkeypatch.setattr(discovery, "build_model", guarded)
    result = discovery.run_algebra_dry_run(manifest, 5)
    assert called == [(5, False)]
    assert result["status"] == "PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE"
    assert result["scientific_meshes_executed"] == []
    assert result["all_discovery_gates_passed"] is False
    assert result["required_claim_flags"] == discovery.CLAIM_FLAGS


def test_formal_sequence_stops_before_building_mesh_97_after_mesh_65_hold(
    manifest: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_hash = discovery.sha256(discovery.MANIFEST)
    calls = []

    def fake_build(cells: int, _manifest: dict, *, formal: bool) -> SimpleNamespace:
        calls.append((cells, formal))
        return SimpleNamespace(cells=cells)

    def fake_solve(model: SimpleNamespace) -> tuple[dict, None]:
        assert model.cells == 65
        return (
            {
                "mesh": [65, 65, 65],
                "status": discovery.HOLD_STATUS,
                "reason": "injected_structural_hold",
                "homotopy": None,
                "cusp": None,
                "cusp_diagnostics": None,
                "remote_pair": None,
                "branches": None,
                "all_mesh_discovery_gates_passed": False,
            },
            None,
        )

    monkeypatch.setattr(
        discovery,
        "validate_manifest",
        lambda _manifest, **_kwargs: {"runner": "hash"},
    )
    monkeypatch.setattr(discovery, "require_loaded_native_phase", lambda *_args: None)
    monkeypatch.setattr(discovery, "build_model", fake_build)
    monkeypatch.setattr(
        discovery,
        "explicit_csr_preflight",
        lambda _model: {"passed": True, "maximum_error": 0.0},
    )
    monkeypatch.setattr(discovery, "solve_discovery_mesh", fake_solve)
    result = discovery.run_formal(manifest, manifest_hash)
    assert calls == [(7, False), (65, True)]
    assert len(result["discovery_mesh_rows"]) == 2
    assert result["discovery_mesh_rows"][1]["status"] == "NOT_RUN_AFTER_HOLD"
    assert result["status"] == discovery.HOLD_STATUS
    assert result["all_discovery_gates_passed"] is False

    with pytest.raises(ValueError, match="external manifest"):
        discovery.run_formal(manifest, "0" * 64)


def test_atomic_promotion_is_append_only(tmp_path: Path) -> None:
    result = {"status": discovery.HOLD_STATUS, "all_discovery_gates_passed": False}
    evidence = {"byte_identical": True}
    result_path = tmp_path / "result.json"
    evidence_path = tmp_path / "evidence.json"
    result_bytes = discovery.canonical_json_bytes(result)
    evidence_bytes = discovery.canonical_json_bytes(evidence)
    discovery.promote_replica_bytes(result_bytes, evidence_bytes, result_path, evidence_path)
    assert result_path.read_bytes() == result_bytes
    assert evidence_path.read_bytes() == evidence_bytes
    assert not list(tmp_path.glob("*.staging"))
    with pytest.raises(RuntimeError, match="append-only"):
        discovery.promote_replica_bytes(result_bytes, evidence_bytes, result_path, evidence_path)


def test_promotion_never_deletes_a_preexisting_staging_path(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    evidence_path = tmp_path / "evidence.json"
    preexisting = tmp_path / ".result.json.staging"
    preexisting.write_bytes(b"foreign-stage\n")
    with pytest.raises(RuntimeError, match="staging boundary"):
        discovery.promote_replica_bytes(
            discovery.canonical_json_bytes({"result": True}),
            discovery.canonical_json_bytes({"evidence": True}),
            result_path,
            evidence_path,
        )
    assert preexisting.read_bytes() == b"foreign-stage\n"
    assert not result_path.exists()
    assert not evidence_path.exists()


def test_atomic_promotion_rolls_back_if_directory_sync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result_path = tmp_path / "result.json"
    evidence_path = tmp_path / "evidence.json"
    calls = {"value": 0}
    original = discovery.fsync_directory

    def fail_after_result_replace(path: Path) -> None:
        calls["value"] += 1
        if calls["value"] == 2:
            raise OSError("injected directory sync failure")
        original(path)

    monkeypatch.setattr(discovery, "fsync_directory", fail_after_result_replace)
    with pytest.raises(OSError, match="injected"):
        discovery.promote_replica_bytes(
            discovery.canonical_json_bytes({"result": True}),
            discovery.canonical_json_bytes({"evidence": True}),
            result_path,
            evidence_path,
        )
    assert not result_path.exists()
    assert not evidence_path.exists()
    assert not list(tmp_path.glob("*.staging"))


def test_atomic_promotion_rolls_back_if_final_pin_check_fails(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    evidence_path = tmp_path / "evidence.json"

    def drifted_pin_snapshot() -> None:
        raise RuntimeError("injected final pin drift")

    with pytest.raises(RuntimeError, match="injected final pin drift"):
        discovery.promote_replica_bytes(
            discovery.canonical_json_bytes({"result": True}),
            discovery.canonical_json_bytes({"evidence": True}),
            result_path,
            evidence_path,
            post_promotion_check=drifted_pin_snapshot,
        )
    assert not result_path.exists()
    assert not evidence_path.exists()


def test_two_replica_harness_requires_external_hash_and_byte_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text('{"frozen":true}\n', encoding="utf-8")
    manifest_hash = discovery.sha256(manifest_path)
    replicas = (tmp_path / ".replica_1.json", tmp_path / ".replica_2.json")
    canonical = tmp_path / "canonical.json"
    evidence = tmp_path / "reproducibility.json"
    payload = valid_preflight_hold_payload(manifest_hash)
    payload_bytes = discovery.canonical_json_bytes(payload)
    counter = {"value": 0}

    def fake_run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        replicas[counter["value"]].write_bytes(payload_bytes)
        counter["value"] += 1
        return SimpleNamespace(returncode=2)

    monkeypatch.setattr(discovery.subprocess, "run", fake_run)
    result = discovery.run_replica_commands(
        (("replica-one",), ("replica-two",)),
        replicas,
        manifest_path,
        manifest_hash,
        {},
        canonical,
        evidence,
    )
    assert result == payload
    assert canonical.read_bytes() == payload_bytes
    reproducibility = json.loads(evidence.read_text())
    assert reproducibility["byte_identical"] is True
    assert reproducibility["replica_exit_codes"] == [2, 2]
    assert not replicas[0].exists() and not replicas[1].exists()

    with pytest.raises(ValueError, match="external manifest"):
        discovery.run_replica_commands(
            (("one",), ("two",)),
            replicas,
            manifest_path,
            "0" * 64,
            {},
            tmp_path / "unused-result.json",
            tmp_path / "unused-evidence.json",
        )


def test_replica_harness_rejects_disagreement_without_promotion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text('{"frozen":true}\n', encoding="utf-8")
    manifest_hash = discovery.sha256(manifest_path)
    replicas = (tmp_path / ".replica_1.json", tmp_path / ".replica_2.json")
    canonical = tmp_path / "canonical.json"
    evidence = tmp_path / "reproducibility.json"
    counter = {"value": 0}

    def fake_run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        payload = {
            "status": discovery.HOLD_STATUS,
            "all_discovery_gates_passed": False,
            "manifest_sha256": manifest_hash,
            "replica": counter["value"],
        }
        replicas[counter["value"]].write_bytes(discovery.canonical_json_bytes(payload))
        counter["value"] += 1
        return SimpleNamespace(returncode=2)

    monkeypatch.setattr(discovery.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="not byte-identical"):
        discovery.run_replica_commands(
            (("one",), ("two",)),
            replicas,
            manifest_path,
            manifest_hash,
            {},
            canonical,
            evidence,
        )
    assert not canonical.exists()
    assert not evidence.exists()
    assert not replicas[0].exists() and not replicas[1].exists()
