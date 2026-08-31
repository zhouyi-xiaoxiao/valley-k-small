"""Round-61 result-blind mutations retained as ordinary v3 regressions."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import audit_positive_b_allocation_cusp_discovery_result as auditor
import numpy as np
import positive_b_allocation_cusp_discovery as discovery
import pytest
import test_audit_positive_b_allocation_cusp_discovery_result as auditor_tests
import test_positive_b_allocation_cusp_discovery as discovery_tests


def test_full_scan_minimum_density_and_survival_must_gate_control(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = {
        "bracket_index": 0,
        "bracket": [1.95, 2.0],
        "time": 2.0,
        "density_per_budget": 1.0,
        "scaled_root_residual": 0.0,
        "scaled_curvature": -1.0,
        "type": "maximum",
        "survival": 0.8,
        "minimum_state_component": 0.0,
        "differential_mass_balance_error": 0.0,
        "density_eligible": True,
        "residual_eligible": True,
        "curvature_eligible": True,
        "duplicate_refined_root": False,
        "eligible": True,
        "separation_eligible": True,
        "eligibility_reasons": [],
    }
    saved = {
        "time": 0.5,
        "density": 0.01,
        "density_per_budget": 1.0,
        "first_derivative_per_budget": 1.0,
        "second_derivative_per_budget": -1.0,
        "survival": 0.99,
        "minimum_state_component": 0.0,
        "differential_mass_balance_error": 0.0,
    }
    scan = {
        "spacing": 0.05,
        "time_window": [0.5, 35.0],
        "endpoint_first_derivatives_per_budget": [1.0, -1.0],
        "endpoint_signs_passed": True,
        "minimum_sampled_state": 0.0,
        "minimum_sampled_density": -1.0,
        "minimum_sampled_survival": -0.1,
        "maximum_sampled_survival_increase": 0.0,
        "maximum_sampled_differential_mass_balance_error": 0.0,
        "full_scan_trace": [saved],
        "saved_trace": [saved],
        "roots": [root],
        "all_bracketed_roots": [root],
        "topology": ["maximum"],
    }
    tail_values = iter(((0.70, 0.8), (0.60, 0.7), (0.50, 0.6), (0.40, 0.5)))

    def evaluate_tail(*_args: object) -> tuple[np.ndarray, np.ndarray]:
        survival, density = next(tail_values)
        return np.asarray((survival,)), np.asarray((density, 0.0, 0.0, 0.0, 0.0))

    def state_law(
        _model: object,
        _budget: float,
        _theta: np.ndarray,
        state: np.ndarray,
        _jets: np.ndarray | None = None,
    ) -> dict[str, float]:
        return {
            "density": 0.01,
            "density_per_budget": 1.0,
            "survival": float(np.sum(state)),
            "minimum_state_component": 0.0,
            "survival_derivative": -0.01,
            "survival_density_identity_error": 0.0,
            "differential_mass_balance_error": 0.0,
        }

    model_diagnostics = {
        "generator_killing_identity_error": 0.0,
        "initial_mass_error": 0.0,
        "physical_installed_budget_absolute_error": 0.0,
        "factor_diagnostics": {},
    }
    monkeypatch.setattr(discovery, "stationary_scan", lambda *_args, **_kwargs: scan)
    monkeypatch.setattr(discovery, "evaluate_without_tangents", evaluate_tail)
    monkeypatch.setattr(discovery, "state_law_diagnostics", state_law)
    monkeypatch.setattr(
        discovery, "allocation_model_diagnostics", lambda *_args, **_kwargs: model_diagnostics
    )
    row = discovery.evaluate_control_law(SimpleNamespace(), np.zeros(2), 0.05)
    assert row["all_gates_passed"] is False
    assert row["gates"]["positive_density_and_survival"] is False


def test_remote_pair_identity_must_change_when_the_root_pair_changes() -> None:
    first = discovery.assess_remote_pair(
        {
            "roots": [
                {"time": 2.0, "type": "maximum", "bracket_index": 4},
                {"time": 2.5, "type": "minimum", "bracket_index": 5},
            ]
        },
        13.0,
    )
    replacement = discovery.assess_remote_pair(
        {
            "roots": [
                {"time": 8.0, "type": "maximum", "bracket_index": 40},
                {"time": 8.5, "type": "minimum", "bracket_index": 41},
            ]
        },
        13.0,
    )
    assert first["pair_identity"] != replacement["pair_identity"]


def test_replica_validator_must_reject_false_scope_and_malformed_nested_hold() -> None:
    manifest = discovery.load_json(discovery.MANIFEST)
    manifest_hash = discovery.sha256(discovery.MANIFEST)
    pins = {role: row["sha256"] for role, row in manifest["pinned_files"].items()}
    result = discovery_tests.valid_preflight_hold_payload(manifest_hash, pins)
    result["claim_scope"] = "continuum cusp verified"
    result["discovery_mesh_rows"][0]["homotopy"] = {"unexpected": True}
    with pytest.raises(RuntimeError, match="result contract"):
        discovery.validate_result_contract(result, manifest_hash, pins)


def test_auditor_control_reconstruction_must_reject_inconsistent_fields() -> None:
    manifest = auditor.load_json(auditor.MANIFEST)
    control = auditor_tests._passing_control(manifest)
    control["minimum_final_state_component"] = -9.0
    control["unexpected_extra_key"] = True
    control["event_basin_masses"] = [0.30, 0.30]
    rules = manifest["representative_gates"]
    control["score_term_margins"]["event_basin_mass"] = (
        0.30 / rules["minimum_each_event_basin_mass"] - 1.0
    )
    control["robustness_score"] = min(control["score_term_margins"].values())
    assert auditor.reconstruct_control(control, manifest) is False


def test_postresult_audit_must_validate_scope_limitations_and_hold_schema() -> None:
    manifest = auditor.load_json(auditor.MANIFEST)
    result = auditor_tests._hold_result(manifest)
    result["claim_scope"] = "continuum cusp verified"
    result["limitations"] = ["none"]
    result["discovery_mesh_rows"][0]["homotopy"] = {"unexpected": True}
    result_bytes = auditor.canonical_json_bytes(result)
    evidence = auditor_tests._evidence(manifest, result, result_bytes)
    audit = auditor.audit_payload(manifest, result, evidence, result_bytes)
    assert audit["audit_integrity_passed"] is False


def test_every_bracketed_root_is_inside_the_physical_gate() -> None:
    scan = auditor_tests._scan(
        [
            auditor_tests._root(0, 2.0, "maximum", 0.95),
            auditor_tests._root(1, 3.0, "minimum", -0.10),
        ]
    )
    scan["roots"] = [scan["all_bracketed_roots"][0]]
    scan["all_bracketed_roots"][1]["eligible"] = False
    scan["all_bracketed_roots"][1]["density_eligible"] = False
    scan["all_bracketed_roots"][1]["eligibility_reasons"] = ["density"]
    diagnostics = auditor_tests._model_diagnostics(65)
    gates = discovery.scan_physical_gate_results(scan, diagnostics)
    assert gates["positive_density_and_survival"] is False
    assert gates["all_bracketed_roots_physical"] is False


def test_remote_lineage_birth_and_excess_drift_are_hold() -> None:
    anchor = discovery.assess_remote_pair(
        {
            "roots": [
                {"time": 2.0, "type": "maximum", "bracket_index": 0},
                {"time": 3.0, "type": "minimum", "bracket_index": 1},
            ]
        },
        13.0,
    )
    born = discovery.continue_remote_pair_lineage(
        {
            "roots": [
                {"time": 2.1, "type": "maximum", "bracket_index": 0},
                {"time": 3.1, "type": "minimum", "bracket_index": 1},
                {"time": 4.1, "type": "maximum", "bracket_index": 2},
            ]
        },
        13.0,
        anchor,
        anchor,
    )
    assert born["lineage_passed"] is False
    assert "eligible_root_birth_or_death" in born["lineage_hold_reasons"]
    drifted = discovery.continue_remote_pair_lineage(
        {
            "roots": [
                {"time": 4.0, "type": "maximum", "bracket_index": 0},
                {"time": 5.0, "type": "minimum", "bracket_index": 1},
            ]
        },
        13.0,
        anchor,
        anchor,
    )
    assert drifted["lineage_passed"] is False
    assert "excess_adjacent_root_time_drift" in drifted["lineage_hold_reasons"]


def test_duplicate_json_noncanonical_evidence_and_symlink_inputs_fail_closed(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="duplicate JSON key"):
        discovery.parse_json_object_bytes(
            b'{"same": 1, "same": 2}', "duplicate", require_canonical=False
        )
    target = tmp_path / "target.json"
    target.write_bytes(b"{}\n")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(RuntimeError, match="non-symlink"):
        discovery.stable_regular_file_bytes(link)

    manifest = auditor.load_json(auditor.MANIFEST)
    result = auditor_tests._hold_result(manifest)
    result_bytes = auditor.canonical_json_bytes(result)
    evidence = auditor_tests._evidence(manifest, result, result_bytes)
    noncanonical = auditor.canonical_json_bytes(evidence).replace(b"\n", b"", 1)
    audit = auditor.audit_payload(manifest, result, evidence, result_bytes, noncanonical)
    assert audit["checks"]["canonical_evidence_bytes"] is False


def test_mutations_are_local_and_do_not_create_scientific_outputs() -> None:
    assert all(
        not discovery.lexical_path_exists(path) for path in discovery.scientific_output_paths()
    )
