from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import continuum_g1_discovery as discovery
import continuum_g1_smoke as smoke
import numpy as np
import pytest
from scipy.sparse.linalg import expm_multiply


def test_frozen_manifest_is_strict_and_internally_consistent(tmp_path: Path) -> None:
    manifest, digest = discovery.load_and_validate_manifest(discovery.DEFAULT_MANIFEST)

    assert manifest == discovery.EXPECTED_MANIFEST
    assert digest == hashlib.sha256(discovery.DEFAULT_MANIFEST.read_bytes()).hexdigest()
    configuration = discovery.RunConfiguration.from_manifest(manifest)
    assert configuration.state_count == 207_025
    assert configuration.time_points == 321
    assert configuration.chunk_points == 41
    assert manifest["required_g1a_foundation"] == {
        "artifact": "artifacts/data/continuum_g1_smoke.json",
        "schema_version": 3,
        "stage": "G1a_pre_fold_foundations",
        "status": "PASS",
        "continuum_verified": False,
        "gate_count": 42,
        "all_gates_true": True,
        "sha256": "a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3",
        "producer_code": "code/continuum_g1_smoke.py",
        "producer_code_sha256": (
            "e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701"
        ),
    }

    mutated = json.loads(discovery.DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    mutated["unexpected_protocol_change"] = True
    mutated_path = tmp_path / "mutated_manifest.json"
    mutated_path.write_text(json.dumps(mutated), encoding="utf-8")
    with pytest.raises(ValueError, match="does not exactly match"):
        discovery.load_and_validate_manifest(mutated_path)


@pytest.mark.parametrize(
    ("section", "field", "coerced_value"),
    (
        (None, "schema_version", 1.0),
        ("candidate_rules", "adjacent_theta_sign_change", 1),
        ("time_grid", "start", 0),
    ),
)
def test_manifest_rejects_python_equal_but_json_type_mismatched_values(
    tmp_path: Path,
    section: str | None,
    field: str,
    coerced_value: object,
) -> None:
    manifest = json.loads(discovery.DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    target = manifest if section is None else manifest[section]
    target[field] = coerced_value
    path = tmp_path / "type_coerced_manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="does not exactly match"):
        discovery.load_and_validate_manifest(path)


def _expected_g1a_preflight() -> dict[str, object]:
    contract = discovery._current_model_contract()
    return {
        "validation_status": "PASS",
        **discovery.EXPECTED_MANIFEST["required_g1a_foundation"],
        "model_contract": contract,
        "model_contract_sha256": discovery._json_sha256(contract),
    }


def test_pinned_g1a_foundation_artifact_validates_exactly() -> None:
    requirement = discovery.EXPECTED_MANIFEST["required_g1a_foundation"]
    observed = discovery.validate_g1a_foundation_artifact(requirement)

    assert observed == _expected_g1a_preflight()


def test_g1a_foundation_preflight_rejects_tamper_and_semantic_mismatch(
    tmp_path: Path,
) -> None:
    source = discovery.REPORT / "artifacts/data/continuum_g1_smoke.json"
    producer_source = discovery.REPORT / "code/continuum_g1_smoke.py"
    artifact = tmp_path / "foundation.json"
    artifact.write_bytes(source.read_bytes())
    producer = tmp_path / "code/continuum_g1_smoke.py"
    producer.parent.mkdir()
    producer.write_bytes(producer_source.read_bytes())
    requirement = {
        **discovery.EXPECTED_MANIFEST["required_g1a_foundation"],
        "artifact": "foundation.json",
    }

    artifact.write_bytes(source.read_bytes() + b" ")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        discovery.validate_g1a_foundation_artifact(requirement, report_root=tmp_path)

    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["status"] = "FAIL"
    artifact.write_text(json.dumps(payload), encoding="utf-8")
    status_requirement = {
        **requirement,
        "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
    }
    with pytest.raises(ValueError, match="status disagrees"):
        discovery.validate_g1a_foundation_artifact(
            status_requirement,
            report_root=tmp_path,
        )

    payload["status"] = "PASS"
    first_gate = next(iter(payload["gates"]))
    payload["gates"][first_gate] = False
    artifact.write_text(json.dumps(payload), encoding="utf-8")
    gate_requirement = {
        **requirement,
        "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
    }
    with pytest.raises(ValueError, match="failed gates"):
        discovery.validate_g1a_foundation_artifact(
            gate_requirement,
            report_root=tmp_path,
        )


def test_g1a_preflight_rejects_producer_code_drift(tmp_path: Path) -> None:
    artifact_source = discovery.REPORT / "artifacts/data/continuum_g1_smoke.json"
    producer_source = discovery.REPORT / "code/continuum_g1_smoke.py"
    artifact = tmp_path / "artifacts/data/continuum_g1_smoke.json"
    producer = tmp_path / "code/continuum_g1_smoke.py"
    artifact.parent.mkdir(parents=True)
    producer.parent.mkdir(parents=True)
    artifact.write_bytes(artifact_source.read_bytes())
    producer.write_bytes(producer_source.read_bytes() + b"\n# one-byte-drift")

    with pytest.raises(ValueError, match="producer-code SHA-256 mismatch"):
        discovery.validate_g1a_foundation_artifact(
            discovery.EXPECTED_MANIFEST["required_g1a_foundation"],
            report_root=tmp_path,
        )


def test_g1a_preflight_rejects_current_parameter_contract_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_parameters = smoke.PilotParameters
    drifted = replace(original_parameters(), diffusion=0.009)
    monkeypatch.setattr(smoke, "PilotParameters", lambda: drifted)

    with pytest.raises(ValueError, match="current PilotParameters disagree"):
        discovery.validate_g1a_foundation_artifact(
            discovery.EXPECTED_MANIFEST["required_g1a_foundation"]
        )


def test_g1a_preflight_rejects_current_control_endpoint_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    drifted = smoke.LOWER_WEIGHTS.copy()
    drifted[0] += 0.01
    monkeypatch.setattr(smoke, "LOWER_WEIGHTS", drifted)

    with pytest.raises(ValueError, match="current control endpoints disagree"):
        discovery.validate_g1a_foundation_artifact(
            discovery.EXPECTED_MANIFEST["required_g1a_foundation"]
        )


def test_chunked_observables_match_full_history_on_asymmetric_grid() -> None:
    parameters = smoke.PilotParameters()
    grid = smoke.QuotientGrid2D(
        midpoint_cells=7,
        relative_parallel_cells=9,
        relative_perp_cells=5,
        midpoint_bounds=parameters.midpoint_bounds,
        relative_parallel_bounds=parameters.relative_parallel_bounds,
        transverse_width=parameters.transverse_width,
    )
    model = smoke.build_model(grid, theta=0.37, parameters=parameters)
    times = np.linspace(0.0, 0.6, 7)

    observed, diagnostics = discovery.evaluate_observables_chunked(
        model,
        times,
        chunk_points=3,
    )
    full_states = np.asarray(
        expm_multiply(
            model.killed_generator.T,
            model.initial,
            start=0.0,
            stop=0.6,
            num=7,
            endpoint=True,
        )
    )
    first = model.killed_generator @ model.killing
    second = model.killed_generator @ first
    third = model.killed_generator @ second
    expected = {
        "time": times,
        "f": full_states @ model.killing,
        "f_t": full_states @ first,
        "f_tt": full_states @ second,
        "f_ttt": full_states @ third,
        "survival": np.sum(full_states, axis=1),
    }

    for name, reference in expected.items():
        assert np.allclose(observed[name], reference, rtol=3.0e-12, atol=3.0e-13)
    assert diagnostics["maximum_chunk_state_rows"] <= 3
    assert diagnostics["full_state_history_stored"] is False
    assert "states" not in observed


def _synthetic_curves(interior_height: float) -> dict[str, np.ndarray]:
    return {
        "time": np.asarray((0.0, 1.0, 2.0, 3.0)),
        "f": np.ones(4),
        "f_t": np.asarray((0.4, interior_height, interior_height, 0.4)),
        "f_tt": np.asarray((-1.0, -0.5, 0.5, 1.0)),
        "f_ttt": np.zeros(4),
        "survival": np.asarray((1.0, 0.9, 0.8, 0.7)),
    }


def test_synthetic_candidate_logic_retains_brackets_and_matches_adjacent_theta() -> None:
    left = discovery.analyze_control_curves(
        _synthetic_curves(-0.02),
        dimensionless_extremum_height_max=0.05,
        minimum_analysis_time=0.5,
        relative_density_floor=1.0e-12,
    )
    right = discovery.analyze_control_curves(
        _synthetic_curves(0.02),
        dimensionless_extremum_height_max=0.05,
        minimum_analysis_time=0.5,
        relative_density_floor=1.0e-12,
    )

    assert left["raw_f_t_bracket_count_before_filter"] == 2
    assert left["f_t_root_bracket_count"] == 1
    assert left["excluded_f_t_bracket_count"] == 1
    assert left["f_tt_extremum_count"] == 1
    assert left["f_tt_extrema"][0]["linear_extremum_time"] == pytest.approx(1.5)
    assert left["f_tt_extrema"][0]["dimensionless_abs_t_f_t_over_f"] == pytest.approx(0.03)
    assert left["f_tt_extrema"][0]["near_zero_candidate"]

    left_line_analysis = _manual_extremum_analysis(
        (left["f_tt_extrema"][0]["linear_extremum_time"],),
        (left["f_tt_extrema"][0]["interpolated_f_t"],),
        near_zero=(True,),
    )
    right_line_analysis = _manual_extremum_analysis(
        (right["f_tt_extrema"][0]["linear_extremum_time"],),
        (right["f_tt_extrema"][0]["interpolated_f_t"],),
        near_zero=(True,),
    )
    line = discovery.analyze_control_line(
        (
            {"theta_index": 0, "theta": 0.4, "candidate_analysis": left_line_analysis},
            {"theta_index": 1, "theta": 0.5, "candidate_analysis": right_line_analysis},
        ),
        time_match_tolerance=2.0,
        adjacent_theta_sign_change=True,
    )
    assert line["near_zero_extremum_count"] == 2
    assert line["adjacent_theta_extremum_match_count"] == 1
    assert line["adjacent_theta_sign_bracket_count"] == 1
    assert line["adjacent_theta_sign_brackets"][0]["strict_opposite_sign"]
    assert line["adjacent_theta_sign_brackets"][0]["exact_zero_theta_locations"] == []
    assert line["adjacent_theta_sign_brackets"][0]["interior_root_evidence"]
    assert line["line_has_discovery_flag"]
    assert line["interior_discovery_flag"]
    assert line["continuum_verified"] is False
    assert line["project_gate_passed"] is False


def _manual_extremum_analysis(
    times: tuple[float, ...],
    heights: tuple[float, ...],
    *,
    root_topologies: tuple[str, ...] = (),
    near_zero: tuple[bool, ...] | None = None,
) -> dict[str, object]:
    near_zero_flags = near_zero or tuple(False for _ in times)
    return {
        "f_t_root_brackets": [{"sampled_topology": topology} for topology in root_topologies],
        "f_t_root_bracket_count": len(root_topologies),
        "excluded_f_t_brackets": [],
        "excluded_f_t_bracket_count": 0,
        "f_tt_extrema": [
            {
                "extremum_index": index,
                "linear_extremum_time": time,
                "interpolated_f_t": height,
                "extremum_kind": "minimum_of_f_t",
                "near_zero_candidate": near_zero_flags[index],
            }
            for index, (time, height) in enumerate(zip(times, heights, strict=True))
        ],
        "excluded_f_tt_extrema": [],
        "excluded_f_tt_extremum_count": 0,
    }


def test_order_preserving_matching_prevents_crossing_false_negative() -> None:
    line = discovery.analyze_control_line(
        (
            {
                "theta_index": 4,
                "theta": 0.4,
                "candidate_analysis": _manual_extremum_analysis(
                    (1.0, 2.0),
                    (0.2, -0.2),
                ),
            },
            {
                "theta_index": 5,
                "theta": 0.5,
                "candidate_analysis": _manual_extremum_analysis(
                    (1.6, 3.0),
                    (-0.2, 0.2),
                ),
            },
        ),
        time_match_tolerance=2.0,
        adjacent_theta_sign_change=True,
    )

    assert [
        (row["left_extremum_index"], row["right_extremum_index"])
        for row in line["adjacent_theta_extremum_matches"]
    ] == [(0, 0), (1, 1)]
    assert line["adjacent_theta_sign_bracket_count"] == 2
    assert line["matching_diagnostics"][0]["unmatched_left_extremum_indices"] == []
    assert line["matching_diagnostics"][0]["unmatched_right_extremum_indices"] == []
    assert line["assignment_ambiguity_count"] == 0
    assert line["interior_discovery_flag"] is True


def test_matching_ambiguity_blocks_line_empty_action_and_persists_unmatched() -> None:
    line = discovery.analyze_control_line(
        (
            {
                "theta_index": 4,
                "theta": 0.4,
                "candidate_analysis": _manual_extremum_analysis((1.0,), (0.2,)),
            },
            {
                "theta_index": 5,
                "theta": 0.5,
                "candidate_analysis": _manual_extremum_analysis(
                    (0.5, 1.5),
                    (0.2, 0.2),
                ),
            },
        ),
        time_match_tolerance=2.0,
        adjacent_theta_sign_change=True,
    )

    assert line["assignment_ambiguity_count"] == 1
    assert line["action_blocked_by_matching_ambiguity"] is True
    assert line["line_has_discovery_flag"] is True
    assert line["matching_diagnostics"][0]["unmatched_right_extremum_indices"] in ([0], [1])
    assert (
        line["next_protocol_action"]
        == "matching_ambiguity_requires_manual_resolution_before_line_action"
    )


@pytest.mark.parametrize(
    ("left_analysis", "right_analysis", "reason"),
    (
        (
            _manual_extremum_analysis(
                (),
                (),
                root_topologies=("sampled_maximum_of_f",),
            ),
            _manual_extremum_analysis(
                (),
                (),
                root_topologies=(
                    "sampled_maximum_of_f",
                    "sampled_minimum_of_f",
                    "sampled_maximum_of_f",
                ),
            ),
            "retained_f_t_root_count_changed",
        ),
        (
            _manual_extremum_analysis((1.0,), (0.2,)),
            _manual_extremum_analysis((4.0,), (0.2,)),
            "unmatched_left_f_tt_extrema",
        ),
        (
            _manual_extremum_analysis((1.0,), (0.2,)),
            _manual_extremum_analysis((), ()),
            "unmatched_left_f_tt_extrema",
        ),
        (
            _manual_extremum_analysis(
                (),
                (),
                root_topologies=("sampled_maximum_of_f",),
            ),
            _manual_extremum_analysis(
                (),
                (),
                root_topologies=("sampled_minimum_of_f",),
            ),
            "retained_f_t_topology_signature_changed",
        ),
    ),
)
def test_false_empty_topology_transitions_require_manual_review(
    left_analysis: dict[str, object],
    right_analysis: dict[str, object],
    reason: str,
) -> None:
    line = discovery.analyze_control_line(
        (
            {"theta_index": 4, "theta": 0.4, "candidate_analysis": left_analysis},
            {"theta_index": 5, "theta": 0.5, "candidate_analysis": right_analysis},
        ),
        time_match_tolerance=2.0,
        adjacent_theta_sign_change=True,
    )

    transition = line["matching_diagnostics"][0]
    assert transition["manual_review_required"] is True
    assert reason in transition["manual_review_reasons"]
    assert line["topology_transition_manual_review_required"] is True
    assert line["line_has_discovery_flag"] is True
    assert line["interior_discovery_flag"] is False
    assert (
        line["next_protocol_action"]
        == "topology_transition_requires_manual_review_before_line_action"
    )


def test_filter_boundary_transition_reasons_are_persisted_and_block_line_empty() -> None:
    left = _manual_extremum_analysis((), ())
    right = _manual_extremum_analysis((), ())
    right["excluded_f_tt_extrema"] = [
        {
            "bracket_type": "maximal_exact_zero_run",
            "extremum_kind": "unresolved_extremum_of_f_t",
            "exclusion_reasons": ["exact_zero_run_starts_before_minimum_analysis_time"],
        }
    ]
    right["excluded_f_tt_extremum_count"] = 1
    line = discovery.analyze_control_line(
        (
            {"theta_index": 4, "theta": 0.4, "candidate_analysis": left},
            {"theta_index": 5, "theta": 0.5, "candidate_analysis": right},
        ),
        time_match_tolerance=2.0,
        adjacent_theta_sign_change=True,
    )

    transition = line["matching_diagnostics"][0]
    assert transition["analysis_filter_signature_stable"] is False
    assert "analysis_filter_signature_changed" in transition["manual_review_reasons"]
    assert transition["right_topology_summary"]["excluded_f_tt_signature"] == [
        {
            "bracket_type": "maximal_exact_zero_run",
            "extremum_kind": "unresolved_extremum_of_f_t",
            "exclusion_reasons": ["exact_zero_run_starts_before_minimum_analysis_time"],
        }
    ]
    assert (
        line["next_protocol_action"]
        == "topology_transition_requires_manual_review_before_line_action"
    )


@pytest.mark.parametrize(
    ("left_theta", "left_height", "right_theta", "right_height", "zero_theta", "interior"),
    (
        (0.0, 0.0, 0.1, 0.2, 0.0, False),
        (0.9, 0.2, 1.0, 0.0, 1.0, False),
        (0.0, 0.2, 0.1, 0.0, 0.1, True),
        (0.9, 0.0, 1.0, 0.2, 0.9, True),
    ),
)
def test_exact_zero_action_distinguishes_endpoints_from_interior_controls(
    left_theta: float,
    left_height: float,
    right_theta: float,
    right_height: float,
    zero_theta: float,
    interior: bool,
) -> None:
    analyses = [
        _manual_extremum_analysis(
            (1.5,),
            (height,),
            near_zero=(height == 0.0,),
        )
        for height in (left_height, right_height)
    ]
    line = discovery.analyze_control_line(
        (
            {"theta_index": 0, "theta": left_theta, "candidate_analysis": analyses[0]},
            {"theta_index": 1, "theta": right_theta, "candidate_analysis": analyses[1]},
        ),
        time_match_tolerance=2.0,
        adjacent_theta_sign_change=True,
    )

    bracket = line["adjacent_theta_sign_brackets"][0]
    assert bracket["strict_opposite_sign"] is False
    assert bracket["exact_zero_theta_locations"] == [zero_theta]
    assert bracket["interior_root_evidence"] is interior
    assert line["interior_discovery_flag"] is interior
    assert line["next_protocol_action"] == (
        "freeze_candidate_only_then_implement_sensitivity_before_continuation"
        if interior
        else "endpoint_only_flag_does_not_authorize_candidate_freeze"
    )


def test_exact_zero_runs_are_deduplicated_and_initial_plateau_is_filtered() -> None:
    curves = {
        "time": np.asarray((0.0, 0.25, 0.5, 0.75, 1.0)),
        "f": np.asarray((0.0, 0.0, 1.0, 1.0, 1.0)),
        "f_t": np.asarray((0.0, 0.0, 0.2, 0.0, 0.0)),
        "f_tt": np.asarray((0.0, 0.0, -1.0, 0.0, 0.0)),
        "f_ttt": np.zeros(5),
        "survival": np.asarray((1.0, 1.0, 0.9, 0.8, 0.7)),
    }
    analysis = discovery.analyze_control_curves(
        curves,
        dimensionless_extremum_height_max=0.05,
        minimum_analysis_time=0.5,
        relative_density_floor=1.0e-12,
    )

    assert analysis["raw_f_t_bracket_count_before_filter"] == 2
    assert analysis["excluded_f_t_bracket_count"] == 1
    assert analysis["f_t_root_bracket_count"] == 1
    assert analysis["f_t_root_brackets"][0]["bracket_type"] == "maximal_exact_zero_run"
    assert analysis["f_t_root_brackets"][0]["left_index"] == 3
    assert analysis["f_t_root_brackets"][0]["right_index"] == 4

    endpoint_line = discovery.analyze_control_line(
        ({"theta_index": 0, "theta": 0.0, "candidate_analysis": analysis},),
        time_match_tolerance=2.0,
        adjacent_theta_sign_change=True,
    )
    assert endpoint_line["line_has_discovery_flag"]
    assert endpoint_line["interior_discovery_flag"] is False
    assert (
        endpoint_line["next_protocol_action"]
        == "endpoint_only_flag_does_not_authorize_candidate_freeze"
    )


def test_preanalysis_exact_zero_plateau_cannot_be_midpoint_shifted_into_action() -> None:
    analysis = discovery.analyze_control_curves(
        {
            "time": np.asarray((0.0, 0.25, 0.5, 0.75, 1.0, 1.25)),
            "f": np.ones(6),
            "f_t": np.zeros(6),
            "f_tt": np.asarray((0.0, 0.0, 0.0, 0.0, 0.0, 1.0)),
            "f_ttt": np.zeros(6),
            "survival": np.asarray((1.0, 0.95, 0.9, 0.85, 0.8, 0.75)),
        },
        dimensionless_extremum_height_max=0.05,
        minimum_analysis_time=0.5,
        relative_density_floor=1.0e-12,
    )

    assert analysis["f_tt_extremum_count"] == 0
    assert analysis["excluded_f_tt_extremum_count"] == 1
    assert analysis["excluded_f_tt_extrema"][0]["linear_extremum_time"] == pytest.approx(0.5)
    assert (
        "exact_zero_run_starts_before_minimum_analysis_time"
        in analysis["excluded_f_tt_extrema"][0]["exclusion_reasons"]
    )
    line = discovery.analyze_control_line(
        ({"theta_index": 5, "theta": 0.5, "candidate_analysis": analysis},),
        time_match_tolerance=2.0,
        adjacent_theta_sign_change=True,
    )
    assert line["line_has_discovery_flag"] is False
    assert line["interior_discovery_flag"] is False
    assert line["next_protocol_action"] == "line_empty_only_predeclared_simplex_followup_is_allowed"


def test_strict_json_loader_rejects_duplicate_and_nonfinite_values(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"value": 1, "value": 2}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        discovery._load_json_strict(duplicate, label="test")

    nonfinite = tmp_path / "nonfinite.json"
    nonfinite.write_text('{"value": NaN}', encoding="utf-8")
    with pytest.raises(ValueError, match="non-finite JSON token"):
        discovery._load_json_strict(nonfinite, label="test")


def test_small_dry_run_checkpoints_and_resumes_fail_closed(tmp_path: Path) -> None:
    configuration = discovery.RunConfiguration(
        midpoint_cells=7,
        relative_parallel_cells=9,
        relative_perp_cells=5,
        theta_values=(0.0, 0.5),
        time_start=0.0,
        time_stop=0.5,
        time_spacing=0.25,
        time_points=3,
        chunk_points=2,
    )
    output = tmp_path / "result.json"
    checkpoints = tmp_path / "checkpoints"
    first = discovery.run_discovery(
        manifest_path=discovery.DEFAULT_MANIFEST,
        output_path=output,
        checkpoint_dir=checkpoints,
        configuration=configuration,
        run_mode="dry_run",
    )

    assert first["status"] == "DRY_RUN_COMPLETE"
    assert first["formal_frozen_run_completed"] is False
    assert first["continuum_verified"] is False
    assert first["project_gate_passed"] is False
    assert first["provenance"]["running_in_repository_venv"] is True
    assert first["g1a_foundation_preflight"] == _expected_g1a_preflight()
    assert first["provenance"]["g1a_foundation_preflight"] == first["g1a_foundation_preflight"]
    assert first["runtime"]["controls_computed"] == 2
    assert first["runtime"]["controls_resumed"] == 0
    assert len(first["checkpoints"]) == 2
    assert first["checkpoint_integrity_ledger"]["entry_count"] == 2
    assert (checkpoints / discovery.CHECKPOINT_LEDGER_FILENAME).is_file()
    for control in first["controls"]:
        assert set(control["curves"]) == {
            "time",
            "f",
            "f_t",
            "f_tt",
            "f_ttt",
            "survival",
        }
        assert len(control["curves"]["time"]) == 3
        assert control["chunk_diagnostics"]["maximum_chunk_state_rows"] <= 2
        assert control["chunk_diagnostics"]["full_state_history_stored"] is False

    second = discovery.run_discovery(
        manifest_path=discovery.DEFAULT_MANIFEST,
        output_path=output,
        checkpoint_dir=checkpoints,
        configuration=configuration,
        run_mode="dry_run",
    )
    assert second["runtime"]["controls_computed"] == 0
    assert second["runtime"]["controls_resumed"] == 2
    assert all(row["resumed_this_invocation"] for row in second["checkpoints"])

    formal = discovery.RunConfiguration.from_manifest(discovery.EXPECTED_MANIFEST)
    with pytest.raises(ValueError, match="exactly equal"):
        discovery.run_discovery(
            manifest_path=discovery.DEFAULT_MANIFEST,
            output_path=tmp_path / "forbidden.json",
            checkpoint_dir=tmp_path / "forbidden_checkpoints",
            configuration=configuration,
            run_mode="frozen_formal_discovery",
        )
    assert formal.state_count == 207_025


def _one_control_configuration() -> discovery.RunConfiguration:
    return discovery.RunConfiguration(
        midpoint_cells=7,
        relative_parallel_cells=9,
        relative_perp_cells=5,
        theta_values=(0.0,),
        time_start=0.0,
        time_stop=0.5,
        time_spacing=0.25,
        time_points=3,
        chunk_points=2,
    )


def _checkpoint_fixture(
    tmp_path: Path,
) -> tuple[discovery.RunConfiguration, Path, Path, Path]:
    configuration = _one_control_configuration()
    output = tmp_path / "result.json"
    checkpoint_dir = tmp_path / "checkpoints"
    discovery.run_discovery(
        manifest_path=discovery.DEFAULT_MANIFEST,
        output_path=output,
        checkpoint_dir=checkpoint_dir,
        configuration=configuration,
        run_mode="dry_run",
    )
    checkpoint = checkpoint_dir / "theta_000.json"
    ledger = checkpoint_dir / discovery.CHECKPOINT_LEDGER_FILENAME
    return configuration, output, checkpoint, ledger


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _reseal_checkpoint(checkpoint: Path, ledger_path: Path) -> None:
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["entries"][checkpoint.name]["sha256"] = hashlib.sha256(
        checkpoint.read_bytes()
    ).hexdigest()
    _write_json(ledger_path, ledger)


@pytest.mark.parametrize(
    ("attack", "error"),
    (
        ("claim_scope", "provenance or frozen configuration mismatch"),
        ("diffusion", "parameters disagree"),
        ("parameter_numeric_type", "parameters disagree"),
        ("chunk_rows", "chunk dimensions"),
        ("truthy_gate", "Boolean true"),
        ("diagnostic_structure", "do not reproduce"),
        ("negative_runtime", "runtime must be"),
        ("survival_increase", "survival violates"),
        ("f_ttt_spike", "generator-action"),
        ("negative_density", "density is materially negative"),
        ("time_numeric_type", "must contain JSON floats"),
        ("grid_numeric_type", "grid disagrees"),
    ),
)
def test_resealed_checkpoint_semantic_tampering_is_rejected(
    tmp_path: Path,
    attack: str,
    error: str,
) -> None:
    configuration, output, checkpoint_path, ledger_path = _checkpoint_fixture(tmp_path)
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if attack == "claim_scope":
        checkpoint["claim_scope"] = "continuum fold verified"
    elif attack == "diffusion":
        checkpoint["parameters"]["diffusion"] = 999.0
    elif attack == "parameter_numeric_type":
        checkpoint["parameters"]["relative_perp_start"] = 0
    elif attack == "chunk_rows":
        checkpoint["chunk_diagnostics"]["maximum_chunk_state_rows"] = 999_999
    elif attack == "truthy_gate":
        gate = next(iter(checkpoint["model_diagnostics"]["gates"]))
        checkpoint["model_diagnostics"]["gates"][gate] = 1
    elif attack == "diagnostic_structure":
        checkpoint["model_diagnostics"]["diagnostics"].pop("physical_budget")
    elif attack == "negative_runtime":
        checkpoint["runtime_seconds"] = -1.0
    elif attack == "survival_increase":
        checkpoint["curves"]["survival"][1] = 2.0
    elif attack == "f_ttt_spike":
        checkpoint["curves"]["f_ttt"][1] = 999.0
    elif attack == "negative_density":
        checkpoint["curves"]["f"][1] = -1.0
    elif attack == "time_numeric_type":
        checkpoint["curves"]["time"][0] = 0
    elif attack == "grid_numeric_type":
        checkpoint["grid"]["midpoint_cells"] = 7.0
    else:  # pragma: no cover - parametrization is frozen above
        raise AssertionError(attack)
    _write_json(checkpoint_path, checkpoint)
    _reseal_checkpoint(checkpoint_path, ledger_path)

    with pytest.raises(ValueError, match=error):
        discovery.run_discovery(
            manifest_path=discovery.DEFAULT_MANIFEST,
            output_path=output,
            checkpoint_dir=checkpoint_path.parent,
            configuration=configuration,
            run_mode="dry_run",
        )


def test_single_checkpoint_file_tamper_fails_integrity_ledger(tmp_path: Path) -> None:
    configuration, output, checkpoint_path, _ = _checkpoint_fixture(tmp_path)
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint["curves"]["f_ttt"][1] = 999.0
    _write_json(checkpoint_path, checkpoint)

    with pytest.raises(ValueError, match="checkpoint integrity hash mismatch"):
        discovery.run_discovery(
            manifest_path=discovery.DEFAULT_MANIFEST,
            output_path=output,
            checkpoint_dir=checkpoint_path.parent,
            configuration=configuration,
            run_mode="dry_run",
        )


@pytest.mark.parametrize("attack", ("missing_ledger", "missing_checkpoint", "ledger_metadata"))
def test_checkpoint_ledger_orphan_missing_and_metadata_attacks_fail_closed(
    tmp_path: Path,
    attack: str,
) -> None:
    configuration, output, checkpoint_path, ledger_path = _checkpoint_fixture(tmp_path)
    if attack == "missing_ledger":
        ledger_path.unlink()
        error = "orphan checkpoints"
    elif attack == "missing_checkpoint":
        checkpoint_path.unlink()
        error = "files and integrity-ledger entries"
    else:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger["entries"][checkpoint_path.name]["theta"] = 0
        _write_json(ledger_path, ledger)
        error = "entry metadata mismatch"

    with pytest.raises(ValueError, match=error):
        discovery.run_discovery(
            manifest_path=discovery.DEFAULT_MANIFEST,
            output_path=output,
            checkpoint_dir=checkpoint_path.parent,
            configuration=configuration,
            run_mode="dry_run",
        )


@pytest.mark.parametrize(
    "temporary_name",
    (".theta_000.json.tmp", ".integrity_ledger.json.tmp"),
)
def test_interrupted_checkpoint_or_ledger_write_requires_audit(
    tmp_path: Path,
    temporary_name: str,
) -> None:
    configuration, output, checkpoint_path, _ = _checkpoint_fixture(tmp_path)
    (checkpoint_path.parent / temporary_name).write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="interrupted checkpoint writes require audit"):
        discovery.run_discovery(
            manifest_path=discovery.DEFAULT_MANIFEST,
            output_path=output,
            checkpoint_dir=checkpoint_path.parent,
            configuration=configuration,
            run_mode="dry_run",
        )


@pytest.mark.parametrize(
    "invalid_json",
    ('{"schema_version": 1, "schema_version": 1}', '{"value": NaN}'),
)
def test_checkpoint_ledger_rejects_duplicate_and_nonfinite_json(
    tmp_path: Path,
    invalid_json: str,
) -> None:
    configuration, output, checkpoint_path, ledger_path = _checkpoint_fixture(tmp_path)
    ledger_path.write_text(invalid_json, encoding="utf-8")

    with pytest.raises(ValueError, match="invalid checkpoint integrity ledger JSON"):
        discovery.run_discovery(
            manifest_path=discovery.DEFAULT_MANIFEST,
            output_path=output,
            checkpoint_dir=checkpoint_path.parent,
            configuration=configuration,
            run_mode="dry_run",
        )


def test_single_writer_lock_rejects_second_process_before_checkpoint_write(
    tmp_path: Path,
) -> None:
    checkpoint_dir = tmp_path / "shared_checkpoints"
    code = (
        "import sys\n"
        "from pathlib import Path\n"
        "import continuum_g1_discovery as d\n"
        "with d._single_writer_lock(Path(sys.argv[1]), "
        "run_mode='dry_run', configuration_hash='holder-hash'):\n"
        "    print('LOCKED', flush=True)\n"
        "    sys.stdin.readline()\n"
    )
    environment = {
        **os.environ,
        "PYTHONPATH": str(discovery.HERE.parent),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    holder = subprocess.Popen(
        [sys.executable, "-c", code, str(checkpoint_dir)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )
    try:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "LOCKED"
        with pytest.raises(RuntimeError, match="active writer"):
            discovery.run_discovery(
                manifest_path=discovery.DEFAULT_MANIFEST,
                output_path=tmp_path / "forbidden_result.json",
                checkpoint_dir=checkpoint_dir,
                configuration=_one_control_configuration(),
                run_mode="dry_run",
            )
        assert not list(checkpoint_dir.glob("theta_*.json"))
        assert not list(checkpoint_dir.glob(".*.tmp"))
        assert not (checkpoint_dir / discovery.CHECKPOINT_LEDGER_FILENAME).exists()
    finally:
        if holder.stdin is not None:
            holder.stdin.close()
        holder.wait(timeout=5)
    assert holder.returncode == 0, holder.stderr.read() if holder.stderr else ""
    lock_record = json.loads(
        (checkpoint_dir / discovery.RUN_LOCK_FILENAME).read_text(encoding="utf-8")
    )
    assert lock_record["status"] == "RELEASED"
    assert lock_record["configuration_hash"] == "holder-hash"
    assert type(lock_record["pid"]) is int


def test_wrong_venv_formal_guard_precedes_checkpoint_lock_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checkpoint_dir = tmp_path / "must_not_exist"
    monkeypatch.setattr(discovery.sys, "prefix", discovery.sys.base_prefix)

    with pytest.raises(RuntimeError, match="repository .venv"):
        discovery.run_discovery(
            manifest_path=discovery.DEFAULT_MANIFEST,
            output_path=tmp_path / "forbidden_formal.json",
            checkpoint_dir=checkpoint_dir,
            configuration=discovery.RunConfiguration.from_manifest(discovery.EXPECTED_MANIFEST),
            run_mode="frozen_formal_discovery",
        )
    assert not checkpoint_dir.exists()
