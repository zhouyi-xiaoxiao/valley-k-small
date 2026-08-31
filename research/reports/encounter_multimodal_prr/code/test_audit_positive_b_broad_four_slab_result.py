from __future__ import annotations

import copy
from pathlib import Path

import audit_positive_b_broad_four_slab_result as audit
import pytest


def _root(
    time: float,
    topology: str,
    density: float,
    survival: float,
) -> dict[str, float | str]:
    sign = -1.0 if topology == "maximum" else 1.0
    f_tt = sign * 0.1
    return {
        "time": time,
        "topology": topology,
        "density": density,
        "f_t": 0.0,
        "f_tt": f_tt,
        "f_ttt": 0.0,
        "survival": survival,
        "boundary_layer_fraction": 0.0,
        "scaled_first_derivative_residual": 0.0,
        "scaled_second_derivative": time**2 * f_tt / density,
        "differential_mass_balance_residual": 0.0,
        "minimum_state_component": 0.0,
    }


def _row(cells: int) -> dict[str, object]:
    roots = [
        _root(1.05, "maximum", 1.0, 0.9895),
        _root(2.05, "minimum", 0.5, 0.9795),
        _root(3.05, "maximum", 0.8, 0.9695),
        _root(4.05, "minimum", 0.4, 0.9595),
        _root(5.05, "maximum", 0.7, 0.9495),
    ]
    peak = 0.7
    valleys = [0.625, 0.4 / 0.7]
    masses = [0.0205, 0.02, 0.5595]
    gates = {
        "initial_mass": True,
        "physical_budget": True,
        "weights_positive_unit_sum": True,
        "five_alternating_simple_roots": True,
        "peak_ratio": True,
        "valley_ratios": True,
        "root_residuals": True,
        "curvature_margins": True,
        "endpoint_derivative_signs": True,
        "sampled_density_positive": True,
        "root_density_positive": True,
        "survival_positive": True,
        "state_positivity_tolerance": True,
        "survival_monotone_through_final_time": True,
        "tail_final_state_positivity": True,
        "generator_Q_one_equals_minus_B_k0": True,
        "mass_balance_on_saved_scan": True,
        "mass_balance_at_roots": True,
        "mass_balance_at_final_time": True,
        "mass_balance_on_tail_checkpoints": True,
        "event_basin_masses": True,
        "event_mass_partition_closure": True,
        "tangent_state_reproduction": True,
        "tangent_time_jet_reproduction": True,
    }
    root_times = [float(root["time"]) for root in roots]

    def derivative(time: float) -> float:
        value = -1.0
        for root_time in root_times:
            value *= time - root_time
        return value

    saved_trace = [
        {
            "time": 0.1 * index,
            "f": 1.0,
            "f_t": derivative(0.1 * index),
            "f_tt": 0.0,
            "f_ttt": 0.0,
            "survival": 1.0 - 0.001 * index,
            "boundary_layer_fraction": 0.0,
            "differential_mass_balance_residual": 0.0,
        }
        for index in range(351)
    ]
    tail_trace = [
        {
            "time": time,
            "density": density,
            "survival": survival,
            "minimum_state_component": 0.0,
            "differential_mass_balance_residual": 0.0,
        }
        for time, density, survival in (
            (35.0, 1.0, 0.65),
            (50.0, 0.8, 0.55),
            (75.0, 0.6, 0.45),
            (100.0, 0.4, 0.4),
        )
    ]
    control_rows = [
        {
            "time": root["time"],
            "time_jets_f_f_t_f_tt_f_ttt": [
                root["density"],
                root["f_t"],
                root["f_tt"],
                root["f_ttt"],
            ],
            "budget_control_jets": {
                "f_B": 0.0,
                "f_tB": 0.0,
                "f_ttB": 0.0,
                "survival_B": 0.0,
            },
            "direct_vs_tangent_state_relative_l1": 0.0,
            "maximum_direct_vs_tangent_time_jet_absolute_difference": 0.0,
        }
        for root in roots
    ]
    factor_diagnostics = {
        "cells_per_coordinate": cells,
        "contact_area": 0.0804247719318987,
        "contact_area_error_estimate": 0.0,
        "contact_area_exact": 0.0804247719318987,
        "maximum_initial_quadrature_error_estimate": 0.0,
        "maximum_patch_quadrature_error_estimate": 0.0,
        "midpoint_generator_row_error": 0.0,
        "midpoint_initial_mass": 1.0,
        "patch_integrals": [1.0, 1.0, 1.0, 1.0],
        "relative_generator_row_error": 0.0,
        "relative_initial_mass": 1.0,
        "spacings": {
            "midpoint": 2.1 / cells,
            "relative_parallel": 3.6 / cells,
            "relative_perp": 1.0 / cells,
        },
        "state_count_if_full_matrix_formed": cells**3,
    }
    return {
        "mesh": [cells, cells, cells],
        "diagnostics": {
            "mesh": [cells, cells, cells],
            "state_count": cells**3,
            "matrix_free_full_generator": True,
            "midpoint_generator_nnz": cells,
            "relative_generator_nnz": cells,
            "analytic_column_operator_trace": -1.0,
            "initial_mass_error": 0.0,
            "physical_budget": 0.01,
            "physical_budget_absolute_error": 0.0,
            "minimum_weight": 0.0857172266153233,
            "weight_sum_error": 0.0,
            "minimum_killing_per_budget": 0.0,
            "maximum_killing_per_budget": 1.0,
            "killed_mass_balance_operator_error": 0.0,
            "factor_diagnostics": factor_diagnostics,
        },
        "scan": {
            "time_grid": {
                "start": 0.0,
                "stop": 35.0,
                "spacing": 0.02,
                "points": 1751,
                "chunk_points": 11,
            },
            "sampled_peak_density": 1.0,
            "minimum_sampled_density_from_frozen_start": 1.0,
            "minimum_density_sampling_start": 0.5,
            "strict_sign_change_bracket_count": 5,
            "maximum_sampled_survival_increase": -0.0002,
            "minimum_streamed_state_component": 0.0,
            "maximum_boundary_layer_fraction": 0.0,
            "maximum_sampled_differential_mass_balance_residual": 0.0,
            "positive_derivative_checkpoint": {"time": 0.5, "f_t": derivative(0.5)},
            "derivative_at_scan_stop": derivative(35.0),
            "survival_at_scan_stop": 0.65,
            "saved_trace": saved_trace,
        },
        "stationary_structure": {
            "stationary_root_count": 5,
            "topology": audit.EXPECTED_TOPOLOGY,
            "roots": roots,
            "peak_minimum_to_maximum_ratio": peak,
            "valley_to_smaller_adjacent_peak_ratios": valleys,
        },
        "survival_and_event_mass": {
            "final_time": 100.0,
            "final_survival": 0.4,
            "total_reaction_mass_to_final_time": 0.6,
            "basin_reaction_masses": masses,
            "basin_mass_sum": 0.6,
            "basin_mass_sum_vs_total_reaction_difference": 0.0,
            "final_differential_mass_balance_residual": 0.0,
        },
        "tail_35_to_100": {
            "checkpoints": [35.0, 50.0, 75.0, 100.0],
            "trace": tail_trace,
            "survival_at_scan_stop": 0.65,
            "final_survival": 0.4,
            "survival_decrease_from_scan_stop": 0.25,
            "maximum_checkpoint_survival_increase": -0.04999999999999999,
            "minimum_checkpoint_density": 0.4,
            "minimum_tail_state_component": 0.0,
            "minimum_final_state_component": 0.0,
            "maximum_checkpoint_differential_mass_balance_residual": 0.0,
        },
        "time_and_budget_control_jets": {
            "control_variable": "full installed budget B",
            "analytic_augmented_operator_trace": -2.0,
            "rows": control_rows,
            "maximum_direct_vs_tangent_state_relative_l1": 0.0,
            "maximum_direct_vs_tangent_time_jet_absolute_difference": 0.0,
        },
        "gates": gates,
        "all_mesh_gates_passed": True,
    }


def _write_bundle(tmp_path: Path) -> tuple[Path, Path]:
    manifest = audit.load_object(audit.MANIFEST)
    rows = [_row(113), _row(129)]
    agreement_gates = {
        "paired_root_times": True,
        "peak_ratio": True,
        "valley_ratios": True,
        "event_basin_masses": True,
        "final_survival": True,
    }
    result = {
        "schema_version": 1,
        "stage": audit.EXPECTED_STAGE,
        "status": "PASS_RESULT_INFORMED_POSITIVE_B_EVENT_MASS_SHAPE_CONFIRMATION",
        "evidence_timing": manifest["evidence_timing"],
        "claim_scope": manifest["claim_scope"],
        "positive_B_event_mass_shape_confirmation": True,
        **audit.EXPECTED_NEGATIVE_FLAGS,
        "physical_parameters": manifest["physical_parameters"],
        "fixed_absolute_weights": manifest["fixed_absolute_weights"],
        "positive_budget": manifest["positive_budget"],
        "weights_refit": False,
        "heldout_mesh_rows": rows,
        "mesh_agreement": {
            "mesh_pair": [[113, 113, 113], [129, 129, 129]],
            "maximum_paired_root_time_difference": 0.0,
            "peak_ratio_absolute_difference": 0.0,
            "maximum_valley_ratio_absolute_difference": 0.0,
            "maximum_event_mass_absolute_difference": 0.0,
            "final_survival_absolute_difference": 0.0,
            "gates": agreement_gates,
            "all_agreement_gates_passed": True,
        },
        "all_gates_passed": True,
        "required_claim_flags": audit.EXPECTED_NEGATIVE_FLAGS,
        "numerical_reproducibility": manifest["numerical_reproducibility"],
        "reproducibility_evidence": {
            "file": "artifacts/data/positive_b_broad_four_slab_reproducibility.json",
            "independent_full_processes_required": 2,
            "canonical_result_requires_external_byte_comparison": True,
        },
        "pinned_file_hashes": {
            role: pin["sha256"] for role, pin in manifest["pinned_files"].items()
        },
        "manifest_sha256": audit.EXPECTED_MANIFEST_SHA256,
        "software": {"python": "3.12.13", "numpy": "2.5.1", "scipy": "1.18.0"},
        "limitations": audit.EXPECTED_LIMITATIONS,
    }
    result_path = tmp_path / "result.json"
    result_path.write_bytes(audit.canonical_bytes(result))
    result_hash = audit.sha256(result_path)
    evidence = {
        "schema_version": 1,
        "stage": "positive_B_broad_four_slab_two_process_reproducibility",
        "manifest_sha256": audit.EXPECTED_MANIFEST_SHA256,
        "independent_process_count": 2,
        "execution_order": "sequential",
        "replica_exit_codes": [0, 0],
        "replica_result_sha256": [result_hash, result_hash],
        "byte_identical": True,
        "canonical_result_sha256": result_hash,
        "canonical_promotion_after_comparison": True,
        "result_status": result["status"],
        "all_gates_passed": True,
    }
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_bytes(audit.canonical_bytes(evidence))
    return result_path, evidence_path


def _rewrite(path: Path, payload: dict[str, object]) -> None:
    path.write_bytes(audit.canonical_bytes(payload))


def _convert_to_structural_hold(result_path: Path, evidence_path: Path) -> None:
    result = audit.load_canonical_object(result_path)
    for row in result["heldout_mesh_rows"]:
        row["stationary_structure"] = {
            "stationary_root_count": 0,
            "topology": [],
            "roots": [],
            "peak_minimum_to_maximum_ratio": None,
            "valley_to_smaller_adjacent_peak_ratios": None,
        }
        row["survival_and_event_mass"]["basin_reaction_masses"] = None
        row["survival_and_event_mass"]["basin_mass_sum"] = None
        row["survival_and_event_mass"]["basin_mass_sum_vs_total_reaction_difference"] = None
        row["time_and_budget_control_jets"]["rows"] = []
        row["time_and_budget_control_jets"]["maximum_direct_vs_tangent_state_relative_l1"] = 0.0
        row["time_and_budget_control_jets"][
            "maximum_direct_vs_tangent_time_jet_absolute_difference"
        ] = 0.0
        row["scan"]["strict_sign_change_bracket_count"] = 0
        for trace_row in row["scan"]["saved_trace"]:
            trace_row["f_t"] = -1.0
        row["scan"]["positive_derivative_checkpoint"]["f_t"] = -1.0
        row["scan"]["derivative_at_scan_stop"] = -1.0
        for key in (
            "five_alternating_simple_roots",
            "peak_ratio",
            "valley_ratios",
            "root_residuals",
            "curvature_margins",
            "endpoint_derivative_signs",
            "root_density_positive",
            "mass_balance_at_roots",
            "event_basin_masses",
            "event_mass_partition_closure",
            "tangent_state_reproduction",
            "tangent_time_jet_reproduction",
        ):
            row["gates"][key] = False
        row["all_mesh_gates_passed"] = False
    result["mesh_agreement"].update(
        {
            "maximum_paired_root_time_difference": None,
            "peak_ratio_absolute_difference": None,
            "maximum_valley_ratio_absolute_difference": None,
            "maximum_event_mass_absolute_difference": None,
            "final_survival_absolute_difference": 0.0,
            "gates": {
                "paired_root_times": False,
                "peak_ratio": False,
                "valley_ratios": False,
                "event_basin_masses": False,
                "final_survival": True,
            },
            "all_agreement_gates_passed": False,
        }
    )
    result["status"] = "HOLD_RESULT_INFORMED_POSITIVE_B_CONFIRMATION"
    result["positive_B_event_mass_shape_confirmation"] = False
    result["all_gates_passed"] = False
    _rewrite(result_path, result)
    result_hash = audit.sha256(result_path)
    evidence = audit.load_canonical_object(evidence_path)
    evidence["replica_exit_codes"] = [2, 2]
    evidence["replica_result_sha256"] = [result_hash, result_hash]
    evidence["canonical_result_sha256"] = result_hash
    evidence["result_status"] = result["status"]
    evidence["all_gates_passed"] = False
    _rewrite(evidence_path, evidence)


def test_independent_reconstruction_accepts_consistent_bundle(tmp_path: Path) -> None:
    result, evidence = _write_bundle(tmp_path)
    payload = audit.audit(result_path=result, reproducibility_path=evidence)
    assert payload["status"] == "PASS_INDEPENDENT_RECONSTRUCTION"
    assert payload["scientific_result_passed"] is True
    assert len(payload["mesh_reconstructions"]) == 2


def test_structural_hold_is_reproduced_not_rejected(tmp_path: Path) -> None:
    result, evidence = _write_bundle(tmp_path)
    _convert_to_structural_hold(result, evidence)
    payload = audit.audit(result_path=result, reproducibility_path=evidence)
    assert payload["status"] == "HOLD_REPRODUCED"
    assert payload["scientific_result_passed"] is False


def test_rejects_a_relabelled_valley_ratio(tmp_path: Path) -> None:
    result, evidence = _write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["heldout_mesh_rows"][0]["stationary_structure"][
        "valley_to_smaller_adjacent_peak_ratios"
    ][1] = 0.2
    _rewrite(result, payload)
    with pytest.raises(ValueError, match="valley ratio identity"):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_an_unsafe_claim_flag(tmp_path: Path) -> None:
    result, evidence = _write_bundle(tmp_path)
    payload = audit.load_canonical_object(result)
    payload["independent_solver_verified"] = True
    _rewrite(result, payload)
    with pytest.raises(ValueError, match="unsafe claim flag"):
        audit.audit(result_path=result, reproducibility_path=evidence)


def test_rejects_forged_replica_hashes(tmp_path: Path) -> None:
    result, evidence = _write_bundle(tmp_path)
    payload = copy.deepcopy(audit.load_canonical_object(evidence))
    payload["replica_result_sha256"] = ["0" * 64, "0" * 64]
    _rewrite(evidence, payload)
    with pytest.raises(ValueError, match="replica hashes"):
        audit.audit(result_path=result, reproducibility_path=evidence)
