from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import continuum_g1c_simplex as g1c
import numpy as np
import pytest


def small_configuration() -> g1c.SimplexConfiguration:
    return g1c.SimplexConfiguration(
        midpoint_cells=7,
        relative_parallel_cells=9,
        relative_perp_cells=5,
        denominator=10,
        integer_triplets=g1c.full_simplex_triplets(10),
        time_start=0.0,
        time_stop=1.0,
        time_spacing=0.25,
        time_points=5,
        chunk_points=3,
    )


def extremum(
    *,
    index: int = 0,
    time: float = 2.0,
    height: float = 0.2,
    kind: str = "maximum_of_f_t",
    near_zero: bool = False,
) -> dict[str, Any]:
    return {
        "extremum_index": index,
        "linear_extremum_time": time,
        "interpolated_f_t": height,
        "extremum_kind": kind,
        "near_zero_candidate": near_zero,
    }


def candidate_analysis(extrema: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "f_t_root_brackets": [{"sampled_topology": "sampled_maximum_of_f"}],
        "f_t_root_bracket_count": 1,
        "excluded_f_t_brackets": [],
        "excluded_f_t_bracket_count": 0,
        "excluded_f_tt_extrema": [],
        "excluded_f_tt_extremum_count": 0,
        "f_tt_extrema": extrema,
    }


def control(
    index: int,
    triplet: tuple[int, int, int],
    extrema: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "control_index": index,
        "control_id": g1c.control_id(triplet),
        "integer_triplet": list(triplet),
        "weights": (np.asarray(triplet, dtype=float) / 10.0).tolist(),
        "candidate_analysis": candidate_analysis(extrema),
    }


def analyze_pair(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return g1c.analyze_simplex(
        [left, right],
        time_match_tolerance=2.0,
        simplex_edge_l1_integer_distance=2,
        matched_extremum_sign_change=True,
    )


def test_manifest_is_exact_and_full_configuration_is_frozen() -> None:
    manifest, manifest_hash = g1c.load_and_validate_manifest()
    configuration = g1c.SimplexConfiguration.from_manifest(manifest)
    assert len(manifest_hash) == 64
    assert configuration.state_count == 207025
    assert len(configuration.integer_triplets) == 66
    assert configuration.integer_triplets == g1c.full_simplex_triplets(10)
    assert configuration.time_points == 321
    assert manifest["pre_run_amendments"]
    assert manifest["frozen_implementation"]["runner"] == "code/continuum_g1c_simplex.py"


def test_frozen_implementation_hash_tamper_fails_closed(tmp_path: Path) -> None:
    manifest, _ = g1c.load_and_validate_manifest()
    for field, message in (
        ("runner_sha256", "runner SHA-256 mismatch"),
        ("protocol_note_sha256", "protocol-note SHA-256 mismatch"),
    ):
        mutated = copy.deepcopy(manifest)
        mutated["frozen_implementation"][field] = "0" * 64
        path = tmp_path / f"{field}.json"
        g1c.discovery._atomic_write_json(path, mutated)
        with pytest.raises(ValueError, match=message):
            g1c.load_and_validate_manifest(path)


def test_output_and_checkpoint_namespaces_fail_closed(tmp_path: Path) -> None:
    manifest, _ = g1c.load_and_validate_manifest()
    checkpoints = tmp_path / "checkpoints"
    with pytest.raises(ValueError, match="outside the checkpoint namespace"):
        g1c.validate_execution_paths(
            manifest=manifest,
            manifest_path=g1c.DEFAULT_MANIFEST,
            output_path=checkpoints / g1c.LEDGER_FILENAME,
            checkpoint_dir=checkpoints,
        )
    with pytest.raises(ValueError, match="aliases a manifest"):
        g1c.validate_execution_paths(
            manifest=manifest,
            manifest_path=g1c.DEFAULT_MANIFEST,
            output_path=g1c.DEFAULT_MANIFEST,
            checkpoint_dir=checkpoints,
        )


def test_symlinked_output_checkpoint_and_lock_fail_closed(tmp_path: Path) -> None:
    manifest, _ = g1c.load_and_validate_manifest()
    target = tmp_path / "target"
    target.write_text("protected\n", encoding="utf-8")
    output_link = tmp_path / "output.json"
    output_link.symlink_to(target)
    with pytest.raises(ValueError, match="output path must not be a symlink"):
        g1c.validate_execution_paths(
            manifest=manifest,
            manifest_path=g1c.DEFAULT_MANIFEST,
            output_path=output_link,
            checkpoint_dir=tmp_path / "checkpoints-a",
        )

    directory_target = tmp_path / "checkpoint-target"
    directory_target.mkdir()
    checkpoint_link = tmp_path / "checkpoint-link"
    checkpoint_link.symlink_to(directory_target, target_is_directory=True)
    with pytest.raises(ValueError, match="checkpoint directory must not be a symlink"):
        g1c.validate_execution_paths(
            manifest=manifest,
            manifest_path=g1c.DEFAULT_MANIFEST,
            output_path=tmp_path / "result-a.json",
            checkpoint_dir=checkpoint_link,
        )

    checkpoints = tmp_path / "checkpoints-b"
    checkpoints.mkdir()
    (checkpoints / g1c.RUN_LOCK_FILENAME).symlink_to(target)
    with pytest.raises(ValueError, match="run-lock path must not be a symlink"):
        g1c.validate_execution_paths(
            manifest=manifest,
            manifest_path=g1c.DEFAULT_MANIFEST,
            output_path=tmp_path / "result-b.json",
            checkpoint_dir=checkpoints,
        )


def test_strict_manifest_rejects_bool_for_integer(tmp_path: Path) -> None:
    manifest, _ = g1c.load_and_validate_manifest()
    mutated = copy.deepcopy(manifest)
    mutated["mesh"]["midpoint_cells"] = True
    path = tmp_path / "manifest.json"
    g1c.discovery._atomic_write_json(path, mutated)
    with pytest.raises(ValueError, match="does not exactly match"):
        g1c.load_and_validate_manifest(path)


def test_full_triangular_lattice_has_exactly_165_edges() -> None:
    controls = [
        control(index, triplet, []) for index, triplet in enumerate(g1c.full_simplex_triplets())
    ]
    edges = g1c.simplex_edges(controls, l1_distance=2)
    assert len(edges) == 165
    assert all(
        sum(
            abs(a - b)
            for a, b in zip(
                controls[left]["integer_triplet"],
                controls[right]["integer_triplet"],
                strict=True,
            )
        )
        == 2
        for left, right in edges
    )
    with pytest.raises(ValueError, match="exactly two"):
        g1c.simplex_edges(controls, l1_distance=4)


def test_dry_run_uses_same_complete_66_control_simplex() -> None:
    dry = g1c.SimplexConfiguration.small_full_simplex_dry_run()
    frozen = g1c.SimplexConfiguration.from_manifest(g1c.load_and_validate_manifest()[0])
    assert dry.integer_triplets == frozen.integer_triplets
    assert len(dry.integer_triplets) == 66
    assert dry.state_count == 315


def test_pinned_inputs_and_all_true_g1a_certificate_validate() -> None:
    manifest, _ = g1c.load_and_validate_manifest()
    result = g1c.validate_required_inputs(manifest["required_inputs"])
    assert set(result) == {"g1a_foundation", "g1b_formal_line", "g1b_manual_review"}
    assert result["g1a_foundation"]["gate_count"] == 42
    assert all(row["validation_status"] == "PASS" for row in result.values())


def test_pinned_input_hash_tamper_fails_closed() -> None:
    manifest, _ = g1c.load_and_validate_manifest()
    requirements = copy.deepcopy(manifest["required_inputs"])
    requirements["g1b_manual_review"]["artifact_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="artifact SHA-256 mismatch"):
        g1c.validate_required_inputs(requirements)


def test_arbitrary_weight_model_uses_non_line_weights_and_fixed_budget() -> None:
    configuration = small_configuration()
    triplet = (2, 3, 5)  # middle weight 0.3 is outside the old theta line.
    model = g1c.assemble_arbitrary_weight_model(configuration, triplet)
    diagnostics = g1c.arbitrary_weight_model_diagnostics(configuration, triplet, model)
    assert diagnostics["diagnostics"]["weights"] == [0.2, 0.3, 0.5]
    assert all(diagnostics["gates"].values())
    assert diagnostics["diagnostics"]["physical_budget"] == pytest.approx(0.6)
    old_line_middle_weight = 0.25
    assert diagnostics["diagnostics"]["weights"][1] != old_line_middle_weight


def test_arbitrary_model_gates_do_not_call_legacy_foundation_gates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configuration = small_configuration()
    model = g1c.assemble_arbitrary_weight_model(configuration, (2, 3, 5))

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("legacy foundation_gates called on arbitrary control")

    monkeypatch.setattr(g1c.smoke, "foundation_gates", forbidden)
    result = g1c.arbitrary_weight_model_diagnostics(configuration, (2, 3, 5), model)
    assert all(result["gates"].values())


def test_shared_structural_baseline_is_genuine_theta_endpoint() -> None:
    baseline = g1c.shared_foundation_baseline(small_configuration())
    assert baseline["legacy_theta_endpoint"] == 0.0
    assert baseline["gate_count"] == 38
    assert all(baseline["gates"].values())


def test_boundary_to_interior_strict_sign_edge_can_cross_interior() -> None:
    left = control(0, (0, 5, 5), [extremum(height=-0.2)])
    right = control(1, (1, 4, 5), [extremum(height=0.2)])
    result = analyze_pair(left, right)
    assert result["interior_sign_crossing_edge_count"] == 1
    assert result["boundary_touching_sign_edge_diagnostic_count"] == 0
    seed = result["interior_candidate_seeds"][0]
    assert seed["interpolated_crossing_weights"] == pytest.approx([0.05, 0.45, 0.5])
    assert seed["crossing_strictly_interior"] is True
    assert result["family_discovery_gate_passed"] is True


def test_sign_crossing_along_simplex_face_is_boundary_diagnostic_only() -> None:
    left = control(0, (0, 5, 5), [extremum(height=-0.2)])
    right = control(1, (0, 6, 4), [extremum(height=0.2)])
    result = analyze_pair(left, right)
    assert result["interior_sign_crossing_edge_count"] == 0
    assert result["boundary_touching_sign_edge_diagnostic_count"] == 1
    assert result["boundary_diagnostics"][0]["interpolated_crossing_weights"][0] == 0.0
    assert result["family_discovery_gate_passed"] is False


def test_exact_zero_boundary_endpoint_remains_boundary_diagnostic() -> None:
    left = control(0, (0, 5, 5), [extremum(height=0.0)])
    right = control(1, (1, 4, 5), [extremum(height=0.2)])
    result = analyze_pair(left, right)
    row = result["boundary_touching_sign_edge_diagnostics"][0]
    assert row["crossing_kind"] == "exact_zero_left_endpoint"
    assert row["interpolated_crossing_weights"] == [0.0, 0.5, 0.5]
    assert row["eligible_candidate_seed"] is False


def test_near_zero_control_is_split_between_interior_and_boundary() -> None:
    boundary = control(0, (0, 5, 5), [extremum(near_zero=True)])
    interior = control(1, (1, 4, 5), [extremum(near_zero=True)])
    result = analyze_pair(boundary, interior)
    assert result["interior_near_zero_extremum_count"] == 1
    assert result["boundary_near_zero_diagnostic_count"] == 1
    assert any(
        seed["source"].startswith("near_zero") for seed in result["interior_candidate_seeds"]
    )
    assert any(row["source"].startswith("near_zero") for row in result["boundary_diagnostics"])


def test_no_candidate_and_no_manual_review_is_failed_gate() -> None:
    left = control(0, (1, 4, 5), [extremum(height=0.2)])
    right = control(1, (2, 3, 5), [extremum(height=0.3)])
    result = analyze_pair(left, right)
    assert result["topology_manual_review_required"] is False
    assert result["family_discovery_gate_passed"] is False
    assert result["family_discovery_gate_status"].startswith("FAIL_")


def test_no_candidate_with_unmatched_topology_is_inconclusive_not_failed() -> None:
    left = control(0, (1, 4, 5), [extremum(height=0.2)])
    right = control(1, (2, 3, 5), [])
    result = analyze_pair(left, right)
    assert result["eligible_candidate_seed_count"] == 0
    assert result["topology_manual_review_required"] is True
    assert result["family_discovery_gate_passed"] is None
    assert result["family_discovery_gate_status"] == "INCONCLUSIVE_MANUAL_REVIEW"
    assert "inconclusive" in result["next_protocol_action"]


def test_double_exact_zero_edge_is_manual_review_not_automatic_segment() -> None:
    left = control(0, (1, 4, 5), [extremum(height=0.0)])
    right = control(1, (2, 3, 5), [extremum(height=0.0)])
    result = analyze_pair(left, right)
    assert result["topology_manual_review_required"] is True
    assert result["candidate_automatically_selects_segment"] is False
    assert result["eligible_candidate_seed_count"] == 0
    assert result["boundary_touching_sign_edge_diagnostic_count"] == 0
    assert result["unresolved_whole_edge_zero_match_count"] == 1
    assert result["unresolved_whole_edge_zero_matches"][0]["crossing_kind"] == (
        "whole_edge_sampled_zero_manual_review"
    )
    assert any(
        "matched_extremum_zero_at_both_edge_endpoints" in row["manual_review_reasons"]
        for row in result["unmatched_topology_manual_review_rows"]
    )


def test_formal_configuration_drift_fails_before_checkpoint_creation(tmp_path: Path) -> None:
    configuration = small_configuration()
    checkpoint_dir = tmp_path / "checkpoints"
    with pytest.raises(ValueError, match="must exactly equal"):
        g1c.run_simplex(
            configuration=configuration,
            run_mode="frozen_formal_G1c",
            output_path=tmp_path / "result.json",
            checkpoint_dir=checkpoint_dir,
        )
    assert not checkpoint_dir.exists()


def test_all_66_control_dry_run_resumes_from_integrity_ledger(tmp_path: Path) -> None:
    output = tmp_path / "dry_result.json"
    checkpoints = tmp_path / "checkpoints"
    configuration = g1c.SimplexConfiguration.small_full_simplex_dry_run()
    first = g1c.run_simplex(
        configuration=configuration,
        run_mode="dry_run",
        output_path=output,
        checkpoint_dir=checkpoints,
    )
    assert first["runtime"]["controls_computed"] == 66
    assert first["runtime"]["controls_resumed"] == 0
    assert first["checkpoint_integrity_ledger"]["entry_count"] == 66
    assert first["simplex_candidate_analysis"]["simplex_edge_count"] == 165
    assert first["evidence_role"] == "implementation_diagnostic_only"
    assert first["continuum_verified"] is False
    assert first["project_gate_passed"] is False

    second = g1c.run_simplex(
        configuration=configuration,
        run_mode="dry_run",
        output_path=output,
        checkpoint_dir=checkpoints,
    )
    assert second["runtime"]["controls_computed"] == 0
    assert second["runtime"]["controls_resumed"] == 66
    assert second["checkpoint_integrity_ledger"]["entry_count"] == 66


def test_claim_flags_are_hard_false_in_source() -> None:
    source = Path(g1c.HERE).read_text(encoding="utf-8")
    assert '"continuum_verified": False' in source
    assert '"project_gate_passed": False' in source
    assert '"confirmation_segment_authorized": False' in source
