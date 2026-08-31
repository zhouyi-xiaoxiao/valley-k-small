from __future__ import annotations

import copy
import math
from typing import Any

import audit_positive_b_allocation_cusp_discovery_result as auditor
import pytest

FIXTURE_MANIFEST = auditor.load_json(auditor.MANIFEST)


def _pins(manifest: dict[str, Any]) -> dict[str, str]:
    return {role: record["sha256"] for role, record in manifest["pinned_files"].items()}


def _hold_result(manifest: dict[str, Any]) -> dict[str, Any]:
    pins = _pins(manifest)

    def metadata(path: str, digest: str) -> dict[str, Any]:
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

    lexical = {"manifest": metadata("manifest.json", auditor.EXPECTED_MANIFEST_SHA256)}
    lexical.update({role: metadata(f"pin/{role}", digest) for role, digest in pins.items()})
    rows = []
    for cells in auditor.DISCOVERY_MESHES:
        rows.append(
            {
                "mesh": [cells, cells, cells],
                "status": "NOT_RUN_AFTER_PREFLIGHT_HOLD",
                "reason": "explicit_csr_preflight_held_before_scientific_construction",
                "model_diagnostics": None,
                "homotopy": None,
                "cusp": None,
                "cusp_diagnostics": None,
                "stationary_scan": None,
                "remote_pair": None,
                "branches": None,
                "all_mesh_discovery_gates_passed": False,
            }
        )
    return {
        "schema_version": auditor.SCHEMA_VERSION,
        "stage": auditor.STAGE,
        "status": auditor.HOLD_STATUS,
        "evidence_timing": "FROZEN_BEFORE_ANY_ALLOCATION_CUSP_MESH_65_OR_97_RUN",
        "claim_scope": manifest["claim_scope"],
        "manifest_sha256": auditor.EXPECTED_MANIFEST_SHA256,
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
        "discovery_mesh_rows": rows,
        "bounded_phase_discovery": None,
        "all_discovery_gates_passed": False,
        "required_claim_flags": manifest["required_claim_flags"],
        "forbidden_claims": manifest["forbidden_claims"],
        "pin_snapshots": {"before_formal": pins, "after_formal": pins},
        "lexical_pin_snapshots": {"before_formal": lexical, "after_formal": lexical},
        "pinned_file_hashes": pins,
        "software": {"python": "test", "numpy": "test", "scipy": "test"},
        "limitations": [
            "meshes 65 and 97 are two same-family discovery meshes; mesh 97 is not held out",
            "same finite-volume solver family and one fixed box",
            "no held-out parity, box, continuum, or independent-solver evidence",
            "retained-window modes are not a global exact-count theorem",
            "PASS_DISCOVERY_LOW_MESH_ONLY is not a manuscript confirmation or publication pass",
        ],
    }


def _evidence(
    manifest: dict[str, Any], result: dict[str, Any], result_bytes: bytes
) -> dict[str, Any]:
    pins = _pins(manifest)
    result_hash = auditor.sha256_bytes(result_bytes)
    return {
        "schema_version": 1,
        "stage": "allocation_cusp_discovery_two_process_reproducibility",
        "manifest_sha256": auditor.EXPECTED_MANIFEST_SHA256,
        "independent_process_count": 2,
        "execution_order": "sequential",
        "five_path_absence_before_replicas": auditor.EXPECTED_FIVE_PATH_ABSENCE,
        "promotion_staging_absence_before_replicas": auditor.EXPECTED_PROMOTION_STAGING_ABSENCE,
        "per_replica_launch_boundaries": [
            {
                "replica_index": 1,
                "allowed_present_science_paths": [],
                "promotion_staging_paths_absent": True,
            },
            {
                "replica_index": 2,
                "allowed_present_science_paths": [auditor.EXPECTED_FIVE_PATH_ABSENCE[2]],
                "promotion_staging_paths_absent": True,
            },
        ],
        "replica_exit_codes": [
            0 if result["all_discovery_gates_passed"] else 2,
            0 if result["all_discovery_gates_passed"] else 2,
        ],
        "replica_result_sha256": [result_hash, result_hash],
        "byte_identical": True,
        "canonical_result_sha256": result_hash,
        "result_status": result["status"],
        "all_discovery_gates_passed": result["all_discovery_gates_passed"],
        "pin_snapshot_before_replicas": pins,
        "pin_snapshot_after_replicas": pins,
        "lexical_snapshot_before_replicas": result["lexical_pin_snapshots"]["before_formal"],
        "lexical_snapshot_after_replicas": result["lexical_pin_snapshots"]["after_formal"],
    }


def _factor_diagnostics(cells: int) -> dict[str, Any]:
    return {
        "cells_per_coordinate": cells,
        "state_count_if_full_matrix_formed": cells**3,
        "spacings": {
            "midpoint": 2.1 / cells,
            "relative_parallel": 3.6 / cells,
            "relative_perp": 1.0 / cells,
        },
        "patch_integrals": [1.0, 1.0, 1.0, 1.0],
        "maximum_patch_quadrature_error_estimate": 0.0,
        "midpoint_initial_mass": 1.0,
        "relative_initial_mass": 1.0,
        "maximum_initial_quadrature_error_estimate": 0.0,
        "contact_area": math.pi * 0.16**2,
        "contact_area_exact": math.pi * 0.16**2,
        "contact_area_error_estimate": 0.0,
        "midpoint_generator_row_error": 0.0,
        "relative_generator_row_error": 0.0,
    }


def _full_scan_trace(
    roots: list[dict[str, Any]],
) -> tuple[list[dict[str, float]], list[dict[str, float]]]:
    spacing = 0.05
    start = 0.5
    count = 691
    survival_knots = [(start, 0.99), *[(root["time"], root["survival"]) for root in roots]]
    survival_knots.append((35.0, 0.50))

    def survival_at(time: float) -> float:
        for (left_time, left_value), (right_time, right_value) in zip(
            survival_knots, survival_knots[1:], strict=True
        ):
            if time <= right_time:
                fraction = (time - left_time) / (right_time - left_time)
                return float(left_value + fraction * (right_value - left_value))
        return 0.50

    full: list[dict[str, float]] = []
    for index in range(count):
        time = float(start + spacing * index)
        crossings = sum(time >= root["time"] for root in roots)
        derivative = 1.0 if crossings % 2 == 0 else -1.0
        density_per_budget = float(1.0 - 0.9 * index / (count - 1))
        full.append(
            {
                "time": time,
                "density": float(0.01 * density_per_budget),
                "density_per_budget": density_per_budget,
                "first_derivative_per_budget": derivative,
                "second_derivative_per_budget": -1.0 if derivative < 0.0 else 1.0,
                "survival": survival_at(time),
                "minimum_state_component": 0.0,
                "differential_mass_balance_error": 0.0,
            }
        )
    saved = [dict(row) for index, row in enumerate(full) if index % 10 == 0]
    assert len(saved) == 70 and saved[-1]["time"] == 35.0
    return full, saved


def _passing_control(
    manifest: dict[str, Any],
    maximum_count: int = 1,
    cells: int = 65,
    theta: list[float] | None = None,
    weights: list[float] | None = None,
) -> dict[str, Any]:
    theta = [0.0, 0.0] if theta is None else list(theta)
    if weights is None:
        reference = manifest["allocation_chart"]["reference_weights"]
        basis = manifest["allocation_chart"]["P"]
        weights = [
            reference[row] + sum(basis[row][column] * theta[column] for column in range(2))
            for row in range(4)
        ]
    root_count = 2 * maximum_count - 1
    roots = []
    for index in range(root_count):
        root_type = "maximum" if index % 2 == 0 else "minimum"
        survival = 0.95 - 0.10 * index
        time = 2.0 + index
        roots.append(
            {
                "bracket_index": index,
                "bracket": [time - 0.05, time],
                "time": time,
                "type": root_type,
                "density_per_budget": 1.0 if root_type == "maximum" else 0.5,
                "scaled_curvature": -1.0 if root_type == "maximum" else 1.0,
                "scaled_root_residual": 0.0,
                "survival": survival,
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
        )
    full, saved = _full_scan_trace(roots)
    final_survival = 0.4
    tail_survivals = [0.50, 0.45, 0.42, final_survival]
    tail = [
        {
            "time": time,
            "density": density,
            "density_per_budget": density / 0.01,
            "survival": survival,
            "minimum_state_component": 0.0,
            "survival_derivative": -density,
            "survival_density_identity_error": 0.0,
            "differential_mass_balance_error": 0.0,
        }
        for time, density, survival in zip(
            (35.0, 50.0, 75.0, 100.0),
            (0.001, 0.0008, 0.0005, 0.0003),
            tail_survivals,
            strict=True,
        )
    ]
    rules = manifest["representative_gates"]
    minimum_survivals = [root["survival"] for root in roots if root["type"] == "minimum"]
    basin_survivals = [1.0, *minimum_survivals, final_survival]
    masses = [left - right for left, right in zip(basin_survivals, basin_survivals[1:])]
    valley_ratio = 0.5 if maximum_count > 1 else 0.0
    margins = {
        "peak_ratio": 1.0 / rules["minimum_peak_ratio"] - 1.0,
        "valley_ratio": (rules["maximum_valley_ratio"] - valley_ratio)
        / (1.0 - rules["maximum_valley_ratio"]),
        "absolute_scaled_curvature": 1.0 / rules["minimum_absolute_scaled_curvature"] - 1.0,
        "event_basin_mass": min(masses) / rules["minimum_each_event_basin_mass"] - 1.0,
    }
    gates = {name: True for name in auditor.CONTROL_GATE_NAMES}
    return {
        "status": "PASS_CONTROL_EVALUATION",
        "reason": "complete_finite_evaluation",
        "theta": theta,
        "weights": weights,
        "retained_maximum_count": maximum_count,
        "topology": [root["type"] for root in roots],
        "stationary_scan": {
            "spacing": 0.05,
            "time_window": [0.5, 35.0],
            "grid_point_count": 691,
            "reference_maximum_density_per_budget": 1.0,
            "endpoint_first_derivatives_per_budget": [1.0, -1.0],
            "full_scan_trace": full,
            "saved_trace": saved,
            "endpoint_signs_passed": True,
            "minimum_sampled_state": 0.0,
            "minimum_sampled_density": 0.001,
            "minimum_sampled_survival": 0.50,
            "maximum_sampled_survival_increase": 0.0,
            "maximum_sampled_differential_mass_balance_error": 0.0,
            "roots": roots,
            "all_bracketed_roots": roots,
            "topology": [root["type"] for root in roots],
            "physical_law_gates": {name: True for name in auditor.SCAN_PHYSICAL_GATE_NAMES},
        },
        "roots": roots,
        "all_bracketed_roots": roots,
        "tail_trace": tail,
        "model_diagnostics": _model_diagnostics(cells, weights),
        "peak_minimum_to_maximum_ratio": 1.0,
        "valley_to_smaller_peak_ratios": [0.5] * (maximum_count - 1),
        "event_basin_masses": masses,
        "event_partition_closure_error": 0.0,
        "final_survival": final_survival,
        "minimum_final_state_component": 0.0,
        "score_term_margins": margins,
        "robustness_score": min(margins.values()),
        "gates": gates,
        "all_gates_passed": True,
    }


def _model_diagnostics(cells: int, weights: list[float] | None = None) -> dict[str, Any]:
    reference_weights = [
        0.28,
        0.23115240260064182,
        0.20722533378296604,
        0.2816222636163921,
    ]
    weights = reference_weights if weights is None else weights
    factors = _factor_diagnostics(cells)
    midpoint_spacing = factors["spacings"]["midpoint"]
    midpoint_sum = 1.0 / midpoint_spacing
    contact_sum = factors["contact_area"] / (
        factors["spacings"]["relative_parallel"] * factors["spacings"]["relative_perp"]
    )
    midpoint_diagonal_sum, relative_diagonal_sum = auditor.expected_generator_diagonal_sums(
        cells, FIXTURE_MANIFEST
    )
    trace = (
        cells**2 * midpoint_diagonal_sum
        + cells * relative_diagonal_sum
        - 0.01 * midpoint_sum * contact_sum
    )
    return {
        "mesh": [cells, cells, cells],
        "state_count": cells**3,
        "matrix_free_full_generator": True,
        "initial_mass": 1.0,
        "generator_killing_identity_error": 0.0,
        "initial_mass_error": 0.0,
        "installed_budget": 0.01,
        "physical_installed_budget": 0.01,
        "physical_installed_budget_absolute_error": 0.0,
        "minimum_weight": min(weights),
        "weight_sum_error": 0.0,
        "minimum_killing_per_budget": 0.0,
        "maximum_killing_per_budget": 1.0 / midpoint_spacing,
        "midpoint_killing_profile_minimum": 0.0,
        "midpoint_killing_profile_maximum": 1.0 / midpoint_spacing,
        "midpoint_killing_profile_sum": midpoint_sum,
        "contact_killing_profile_minimum": 0.0,
        "contact_killing_profile_maximum": 1.0,
        "contact_killing_profile_sum": contact_sum,
        "midpoint_generator_diagonal_sum": midpoint_diagonal_sum,
        "relative_generator_diagonal_sum": relative_diagonal_sum,
        "analytic_column_operator_trace": trace,
        "factor_diagnostics": factors,
    }


def _state_law(survival: float = 0.8, density: float = 0.01) -> dict[str, float]:
    return {
        "density": density,
        "density_per_budget": density / 0.01,
        "survival": survival,
        "minimum_state_component": 0.0,
        "survival_derivative": -density,
        "survival_density_identity_error": 0.0,
        "differential_mass_balance_error": 0.0,
    }


def _root(index: int, time: float, kind: str, survival: float) -> dict[str, Any]:
    return {
        "bracket_index": index,
        "bracket": [time - 0.05, time],
        "time": time,
        "type": kind,
        "density_per_budget": 1.0 if kind == "maximum" else 0.5,
        "scaled_curvature": -1.0 if kind == "maximum" else 1.0,
        "scaled_root_residual": 0.0,
        "survival": survival,
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


def _scan(roots: list[dict[str, Any]]) -> dict[str, Any]:
    full, saved = _full_scan_trace(roots)
    return {
        "spacing": 0.05,
        "time_window": [0.5, 35.0],
        "grid_point_count": 691,
        "reference_maximum_density_per_budget": 1.0,
        "endpoint_first_derivatives_per_budget": [1.0, -1.0],
        "full_scan_trace": full,
        "saved_trace": saved,
        "endpoint_signs_passed": True,
        "minimum_sampled_state": 0.0,
        "minimum_sampled_density": 0.001,
        "minimum_sampled_survival": 0.50,
        "maximum_sampled_survival_increase": 0.0,
        "maximum_sampled_differential_mass_balance_error": 0.0,
        "roots": roots,
        "all_bracketed_roots": roots,
        "topology": [root["type"] for root in roots],
        "physical_law_gates": {name: True for name in auditor.SCAN_PHYSICAL_GATE_NAMES},
    }


def _anchor_remote(scan: dict[str, Any], cusp_time: float) -> dict[str, Any]:
    roots = scan["roots"]
    identity = "negative_time:maximum_minimum:global_0_1:origin_brackets_0_1"
    lineage = []
    for index, root in enumerate(roots):
        lineage.append(
            {
                "global_root_ordinal": index,
                "type": root["type"],
                "side": "negative_time" if root["time"] < cusp_time else "positive_time",
                "time": root["time"],
                "origin_bracket_index": root["bracket_index"],
                "previous_bracket_index": root["bracket_index"],
                "current_bracket_index": root["bracket_index"],
                "predecessor_global_root_ordinal": index - 1 if index else None,
                "successor_global_root_ordinal": index + 1 if index + 1 < len(roots) else None,
                "matched_previous_global_root_ordinal": index,
                "adjacent_time_drift": 0.0,
            }
        )
    pair = {
        "maximum": roots[0],
        "minimum": roots[1],
        "side": "negative_time",
        "pair_type": "maximum_minimum",
        "selected_global_root_indices": [0, 1],
        "origin_bracket_lineage": [0, 1],
        "maximum_global_root_ordinal": 0,
        "minimum_global_root_ordinal": 1,
        "maximum_bracket_index": 0,
        "minimum_bracket_index": 1,
        "eligible_root_count_at_anchor": len(roots),
    }
    return {
        "remote_pair_present": True,
        "pair_identity": identity,
        "anchor_pair_identity": identity,
        "pair": pair,
        "root_lineage": lineage,
        "lineage_status": "CUSP_ANCHOR",
        "lineage_passed": True,
        "lineage_hold_reasons": [],
        "maximum_observed_adjacent_drift": 0.0,
        "candidate_search_bounded_to_frozen_window": True,
    }


def _comparison_remote(
    scan: dict[str, Any], anchor: dict[str, Any], previous: dict[str, Any]
) -> dict[str, Any]:
    roots = scan["roots"]
    lineage = []
    drifts = []
    for index, root in enumerate(roots):
        drift = abs(root["time"] - previous["root_lineage"][index]["time"])
        drifts.append(drift)
        lineage.append(
            {
                "global_root_ordinal": index,
                "type": root["type"],
                "side": anchor["root_lineage"][index]["side"],
                "time": root["time"],
                "origin_bracket_index": anchor["root_lineage"][index]["origin_bracket_index"],
                "previous_bracket_index": previous["root_lineage"][index]["current_bracket_index"],
                "current_bracket_index": root["bracket_index"],
                "predecessor_global_root_ordinal": index - 1 if index else None,
                "successor_global_root_ordinal": index + 1 if index + 1 < len(roots) else None,
                "matched_previous_global_root_ordinal": index,
                "adjacent_time_drift": drift,
            }
        )
    pair = {
        "maximum": roots[0],
        "minimum": roots[1],
        "side": "negative_time",
        "pair_type": "maximum_minimum",
        "selected_global_root_indices": [0, 1],
        "origin_bracket_lineage": [0, 1],
        "maximum_global_root_ordinal": 0,
        "minimum_global_root_ordinal": 1,
        "maximum_bracket_index": 0,
        "minimum_bracket_index": 1,
        "eligible_root_count_at_anchor": len(roots),
    }
    return {
        "remote_pair_present": True,
        "pair_identity": anchor["pair_identity"],
        "anchor_pair_identity": anchor["pair_identity"],
        "pair": pair,
        "root_lineage": lineage,
        "lineage_status": "MATCHED_COMPARISON",
        "lineage_passed": True,
        "lineage_hold_reasons": [],
        "maximum_observed_adjacent_drift": max(drifts),
        "candidate_search_bounded_to_frozen_window": True,
    }


def _fold_node(cells: int, index: int, time: float) -> dict[str, Any]:
    diagnostics = _model_diagnostics(cells)
    law = _state_law()
    return {
        "acceptance_index": index,
        "time": time,
        "theta": [0.0, 0.0],
        "weights": [0.28, 0.23115240260064182, 0.20722533378296604, 0.2816222636163921],
        "normalized_fold_residual": 0.0,
        "scaled_third_derivative": 1.0,
        "dimensionless_fold_singular_values": [1.0, 0.5],
        "model_diagnostics": diagnostics,
        "state_law_diagnostics": law,
        "physical_law_gates": {name: True for name in auditor.LAW_GATE_NAMES},
    }


def _branch(cells: int, sign: int, cusp_time: float, anchor: dict[str, Any]) -> dict[str, Any]:
    offsets = [0.10, 0.25, 0.50, 0.75, 0.90, 1.00]
    nodes = [
        _fold_node(cells, index, cusp_time + sign * offset) for index, offset in enumerate(offsets)
    ]
    comparisons = []
    remote_rows = []
    previous = anchor
    for sequence, (index, target) in enumerate(zip((1, 2, 3), (0.25, 0.50, 0.75), strict=True)):
        comparison = dict(nodes[index])
        comparison["signed_time_offset"] = target
        comparison["target_signed_time_offset"] = target
        comparison["absolute_time_offset_mismatch"] = 0.0
        comparisons.append(comparison)
        roots = [
            _root(0, 2.0 + 0.10 * (sequence + 1), "maximum", 0.95),
            _root(1, 3.0 + 0.10 * (sequence + 1), "minimum", 0.85),
            _root(2, 4.0 + 0.10 * (sequence + 1), "maximum", 0.75),
        ]
        scan = _scan(roots)
        remote = _comparison_remote(scan, anchor, previous)
        remote_rows.append(
            {
                "acceptance_index": comparison["acceptance_index"],
                "time": comparison["time"],
                "remote_pair": remote,
                "stationary_scan": scan,
            }
        )
        previous = remote
    return {
        "status": "PASS_BRANCH_DISCOVERY",
        "orientation": "positive_time" if sign > 0 else "negative_time",
        "nodes": nodes,
        "comparison_nodes": comparisons,
        "comparison_node_remote_pairs": remote_rows,
        "gates": {name: True for name in auditor.BRANCH_GATE_NAMES},
    }


def _cusp(cells: int, manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    time = 13.0
    density = 1.0
    fourth = 10.0
    jets = [density, 0.0, 0.0, 0.0, fourth / time**4]
    allocation = [
        [0.0, 2.0 / time, 0.0, 0.0, 0.0],
        [0.0, 0.0, 2.0 / time**2, 0.0, 0.0],
    ]
    law = _state_law()
    snapshot = {
        "time": time,
        "budget": 0.01,
        "theta": [0.0, 0.0],
        "weights": list(manifest["allocation_chart"]["reference_weights"]),
        "density_per_budget": density,
        "per_budget_time_jets_0_to_4": jets,
        "allocation_time_jets": allocation,
        "state_law_diagnostics": law,
    }
    matrix = [[0.0, 2.0, 0.0], [0.0, 0.0, 2.0], [10.0, 0.0, 0.0]]
    derivative_rows = [
        {
            "allocation_step": manifest["derivative_audit"]["allocation_steps"][index],
            "relative_time_step": manifest["derivative_audit"]["relative_time_steps"][index],
            "maximum_state_tangent_relative_l1_error": error,
            "maximum_dimensionless_jacobian_error": error,
        }
        for index, error in enumerate((1.0e-7, 1.0e-8))
    ]
    diagnostics = {
        "maximum_dimensionless_residual": 0.0,
        "minimum_weight": min(snapshot["weights"]),
        "scaled_fourth_derivative": fourth,
        "projected_singular_values": [2.0, 2.0],
        "projected_singular_value_ratio": 1.0,
        "full_smallest_singular_value": 2.0,
        "determinant_factorization_relative_residual": 0.0,
        "maximum_survival_identity_residual": 0.0,
        "model_diagnostics": _model_diagnostics(cells),
        "state_law_diagnostics": law,
        "dimensionless_jacobian": matrix,
        "derivative_audit": {
            "rows": derivative_rows,
            "state_error_decrease_or_floor": True,
            "jacobian_error_decrease_or_floor": True,
            "passed": True,
        },
        "gates": {name: True for name in auditor.CUSP_GATE_NAMES},
        "all_gates_passed": True,
    }
    return snapshot, diagnostics


def _mesh_row(cells: int, manifest: dict[str, Any]) -> dict[str, Any]:
    cusp, cusp_diagnostics = _cusp(cells, manifest)
    roots = [
        _root(0, 2.0, "maximum", 0.95),
        _root(1, 3.0, "minimum", 0.85),
        _root(2, 4.0, "maximum", 0.75),
    ]
    scan = _scan(roots)
    remote = _anchor_remote(scan, cusp["time"])
    homotopy_rows = [
        {
            "budget": budget,
            "status": "PASS_CUSP_SOLVE",
            "converged": True,
            "iterations": 1,
            "reason": "converged",
            "point": [cusp["time"], *cusp["theta"]],
            "maximum_scaled_residual": 0.0,
        }
        for budget in manifest["budget_homotopy"]["schedule"]
    ]
    return {
        "mesh": [cells, cells, cells],
        "status": "PASS_MESH_DISCOVERY",
        "reason": "all_mesh_gates_passed",
        "model_diagnostics": _model_diagnostics(cells),
        "homotopy": {"status": "PASS_HOMOTOPY", "rows": homotopy_rows},
        "cusp": cusp,
        "cusp_diagnostics": cusp_diagnostics,
        "stationary_scan": scan,
        "remote_pair": remote,
        "branches": {
            "negative": _branch(cells, -1, cusp["time"], remote),
            "positive": _branch(cells, 1, cusp["time"], remote),
        },
        "all_mesh_discovery_gates_passed": True,
    }


def _phase(manifest: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    screened = []
    reference = manifest["allocation_chart"]["reference_weights"]
    basis = manifest["allocation_chart"]["P"]
    directions = manifest["phase_search"]["directions"]
    for index in range(manifest["phase_search"]["candidate_count"]):
        radius = manifest["phase_search"]["radii"][index // len(directions)]
        direction = directions[index % len(directions)]
        theta = [radius * direction[0], radius * direction[1]]
        weights = [
            reference[row] + sum(basis[row][column] * theta[column] for column in range(2))
            for row in range(4)
        ]
        candidate = {
            "candidate_index": index,
            "radius": radius,
            "direction": direction,
            "theta": theta,
            "weights": weights,
            "eligible_geometry": True,
        }
        candidates.append(candidate)
        screened.append(
            {
                **candidate,
                "mesh_65": _passing_control(
                    manifest,
                    maximum_count=index % 3 + 1,
                    cells=65,
                    theta=theta,
                    weights=weights,
                ),
                "mesh_65_evaluation_status": "EVALUATED",
            }
        )
    advanced = []
    for target in manifest["phase_search"]["target_retained_maximum_counts"]:
        eligible = [row for row in screened if row["mesh_65"]["retained_maximum_count"] == target]
        eligible.sort(key=lambda row: (-row["mesh_65"]["robustness_score"], tuple(row["weights"])))
        for row in eligible[: manifest["phase_search"]["maximum_advanced_per_mode_count"]]:
            mesh_97 = _passing_control(
                manifest,
                maximum_count=target,
                cells=97,
                theta=row["theta"],
                weights=row["weights"],
            )
            advanced.append(
                {
                    **row,
                    "mesh_97": mesh_97,
                    "mesh_97_evaluation_status": "EVALUATED",
                    "worst_score": min(
                        row["mesh_65"]["robustness_score"], mesh_97["robustness_score"]
                    ),
                    "both_meshes_pass": True,
                }
            )
    representatives = {}
    for target in (1, 2, 3):
        passing = [row for row in advanced if row["mesh_65"]["retained_maximum_count"] == target]
        passing.sort(key=lambda row: (-row["worst_score"], tuple(row["weights"])))
        representatives[str(target)] = passing[0]
    return {
        "phase_centre_theta": [0.0, 0.0],
        "candidate_generation": candidates,
        "screened_mesh_65": screened,
        "advanced_mesh_97": advanced,
        "representatives": representatives,
        "all_three_regions_found": True,
        "phase_complete": True,
        "hold_reasons": [],
        "search_expanded": False,
    }


def _passing_result(manifest: dict[str, Any]) -> dict[str, Any]:
    result = _hold_result(manifest)
    result["status"] = auditor.PASS_STATUS
    result["small_explicit_csr_preflight"] = {
        "mesh": [7, 7, 7],
        "state_count": 343,
        "errors": {
            "column_action": 0.0,
            "row_action": 0.0,
            "augmented_column_action": 0.0,
            "augmented_row_action": 0.0,
        },
        "maximum_error": 0.0,
        "passed": True,
    }
    result["discovery_mesh_rows"] = [_mesh_row(cells, manifest) for cells in (65, 97)]
    result["bounded_phase_discovery"] = _phase(manifest)
    result["all_discovery_gates_passed"] = True
    result["required_claim_flags"]["low_mesh_discovery_completed"] = True
    return result


def test_valid_scientific_hold_is_integrity_pass_not_scientific_pass() -> None:
    manifest = auditor.load_json(auditor.MANIFEST)
    result = _hold_result(manifest)
    result_bytes = auditor.canonical_json_bytes(result)
    evidence = _evidence(manifest, result, result_bytes)
    audit = auditor.audit_payload(manifest, result, evidence, result_bytes)
    assert audit["audit_integrity_passed"] is True
    assert audit["scientific_result_passed"] is False
    assert audit["release_status"] == "HOLD_SCIENCE_AUDIT_VALID"
    assert audit["failed_checks"] == []


def test_complete_synthetic_scientific_pass_is_recursively_reconstructed() -> None:
    manifest = auditor.load_json(auditor.MANIFEST)
    result = _passing_result(manifest)
    result_bytes = auditor.canonical_json_bytes(result)
    evidence = _evidence(manifest, result, result_bytes)
    evidence_bytes = auditor.canonical_json_bytes(evidence)
    audit = auditor.audit_payload(manifest, result, evidence, result_bytes, evidence_bytes)
    assert audit["audit_integrity_passed"] is True, audit["failed_checks"]
    assert audit["scientific_result_passed"] is True
    assert audit["release_status"] == "PASS_AUDIT_DISCOVERY_LOW_MESH_ONLY"

    malformed = copy.deepcopy(result)
    malformed["discovery_mesh_rows"][0]["cusp_diagnostics"]["unknown"] = True
    malformed_bytes = auditor.canonical_json_bytes(malformed)
    malformed_evidence = _evidence(manifest, malformed, malformed_bytes)
    rejected = auditor.audit_payload(manifest, malformed, malformed_evidence, malformed_bytes)
    assert rejected["audit_integrity_passed"] is False
    assert "mesh_rows_and_branch_implications" in rejected["failed_checks"]

    def corrupt_model_minimum_weight(payload: dict[str, Any]) -> None:
        row = payload["discovery_mesh_rows"][0]
        row["model_diagnostics"]["minimum_weight"] = 0.5
        row["cusp_diagnostics"]["model_diagnostics"]["minimum_weight"] = 0.5

    for mutate in (
        lambda payload: payload["discovery_mesh_rows"][0]["cusp"].__setitem__("budget", 0.02),
        lambda payload: payload["discovery_mesh_rows"][0]["homotopy"]["rows"][0][
            "point"
        ].__setitem__(0, 30.0),
        lambda payload: payload["discovery_mesh_rows"][0]["cusp"][
            "state_law_diagnostics"
        ].__setitem__("density_per_budget", 2.0),
        corrupt_model_minimum_weight,
    ):
        inconsistent = copy.deepcopy(result)
        mutate(inconsistent)
        inconsistent_bytes = auditor.canonical_json_bytes(inconsistent)
        inconsistent_evidence = _evidence(manifest, inconsistent, inconsistent_bytes)
        inconsistent_audit = auditor.audit_payload(
            manifest,
            inconsistent,
            inconsistent_evidence,
            inconsistent_bytes,
        )
        assert inconsistent_audit["audit_integrity_passed"] is False
        assert "mesh_rows_and_branch_implications" in inconsistent_audit["failed_checks"]


def test_false_claim_and_evidence_tampering_fail_independently() -> None:
    manifest = auditor.load_json(auditor.MANIFEST)
    result = _hold_result(manifest)
    result["required_claim_flags"]["heldout_mesh_confirmation_verified"] = True
    result_bytes = auditor.canonical_json_bytes(result)
    evidence = _evidence(manifest, result, result_bytes)
    evidence["byte_identical"] = False
    audit = auditor.audit_payload(manifest, result, evidence, result_bytes)
    assert audit["audit_integrity_passed"] is False
    assert "negative_claim_flags" in audit["failed_checks"]
    assert "two_process_evidence" in audit["failed_checks"]


def test_control_score_and_law_gates_are_reconstructed_without_producer() -> None:
    manifest = auditor.load_json(auditor.MANIFEST)
    control = _passing_control(manifest)
    assert auditor.reconstruct_control(control, manifest)
    control["roots"][0]["scaled_root_residual"] = 1.0e-9
    assert auditor.reconstruct_control(control, manifest)
    bad = copy.deepcopy(control)
    bad["robustness_score"] += 0.1
    assert not auditor.reconstruct_control(bad, manifest)


def test_auditor_has_no_producer_import() -> None:
    source = auditor.HERE.read_text(encoding="utf-8")
    assert "import positive_b_allocation_cusp_discovery" not in source
    assert "from positive_b_allocation_cusp_discovery" not in source


def test_malformed_structural_payload_fails_closed_without_exception() -> None:
    manifest = auditor.load_json(auditor.MANIFEST)
    result = _hold_result(manifest)
    result["small_explicit_csr_preflight"] = {}
    result["discovery_mesh_rows"] = [None]
    result["bounded_phase_discovery"] = {}
    result_bytes = auditor.canonical_json_bytes(result)
    evidence = _evidence(manifest, result, result_bytes)
    audit = auditor.audit_payload(manifest, result, evidence, result_bytes)
    assert audit["audit_integrity_passed"] is False
    assert "preflight_reconstructed" in audit["failed_checks"]
    assert "mesh_rows_and_branch_implications" in audit["failed_checks"]
    assert "phase_and_control_algebra" in audit["failed_checks"]


def test_auditor_never_deletes_a_preexisting_staging_path(tmp_path) -> None:
    output = tmp_path / "audit.json"
    stage = tmp_path / ".audit.json.staging"
    stage.write_bytes(b"foreign-stage\n")
    with pytest.raises(RuntimeError, match="staging path already exists"):
        auditor.write_append_only(output, b"{}\n")
    assert stage.read_bytes() == b"foreign-stage\n"
    assert not output.exists()


def test_postresult_chain_is_frozen_without_a_hash_cycle() -> None:
    manifest = auditor.load_json(auditor.MANIFEST)
    pinned_paths = {record["path"] for record in manifest["pinned_files"].values()}
    assert auditor.sha256(auditor.MANIFEST) == auditor.EXPECTED_MANIFEST_SHA256
    assert "code/audit_positive_b_allocation_cusp_discovery_result.py" not in pinned_paths
    assert "code/test_audit_positive_b_allocation_cusp_discovery_result.py" not in pinned_paths
    assert "notes/positive_b_allocation_cusp_postresult_audit_protocol_v1.md" not in pinned_paths
    protocol = (
        auditor.REPORT / "notes" / "positive_b_allocation_cusp_postresult_audit_protocol_v1.md"
    ).read_text(encoding="utf-8")
    assert auditor.EXPECTED_MANIFEST_SHA256 in protocol
    assert auditor.sha256(auditor.HERE) in protocol
