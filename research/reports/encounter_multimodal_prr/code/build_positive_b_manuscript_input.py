#!/usr/bin/env python3
"""Build claim-gated TeX macros for the canonical fixed-control positive-B point."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
DEFAULT_OUTPUT = REPORT / "manuscript" / "inputs" / "positive_b_results.tex"

MANIFEST_NAME = "positive_b_broad_four_slab_manifest.json"
RESULT_NAME = "positive_b_broad_four_slab_result.json"
EVIDENCE_NAME = "positive_b_broad_four_slab_reproducibility.json"
AUDIT_NAME = "positive_b_broad_four_slab_independent_audit.json"

EXPECTED_MANIFEST_SHA256 = "955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c"
EXPECTED_RESULT_SHA256 = "51e8eb4bdb652124865d0c39e6f36b99d13ed61578b161e0f75b142cada49401"
EXPECTED_EVIDENCE_SHA256 = "6c0eccaae09ef95923843ddd7a141a27311e1575ee68d3301b4757b785ee9890"
EXPECTED_AUDIT_SHA256 = "60c541a6f0decd5431cefa5c203311176e61006586ce69043d5fcf5380ed517d"
EXPECTED_AUDITOR_SHA256 = "8e84d8930393e4ba60a906519eef7f1734c713a273791153a55d1f6f16ec3985"

RESULT_STATUS = "PASS_RESULT_INFORMED_POSITIVE_B_EVENT_MASS_SHAPE_CONFIRMATION"
EXPECTED_CLAIM_SCOPE = (
    "One result-informed broad four-slab geometry with fixed absolute weights and "
    "fixed B=0.01, tested by a matrix-free killed-Doi finite-volume semigroup on "
    "two held-out odd cubic meshes in one fixed reflecting box."
)
EXPECTED_NEGATIVE_FLAGS = {
    "continuum_interval_verified": False,
    "independent_solver_verified": False,
    "preregistered_discovery": False,
    "project_gate_passed": False,
    "unbounded_domain_FV_limit_verified": False,
}
EXPECTED_KNOWN_BEFORE_FREEZE = {
    "B0_exact_and_mesh_bridge_result_known": True,
    "positive_B_mesh_65_budgets_evaluated": [0.01, 0.02, 0.04, 0.08],
    "positive_B_mesh_97_budgets_evaluated": [0.01, 0.02],
    "positive_B_mesh_113_evaluated": False,
    "positive_B_mesh_129_evaluated": False,
}
EXPECTED_NUMERICAL_REPRODUCIBILITY = {
    "numpy_global_seed": 271828,
    "restore_numpy_global_rng_state": True,
    "analytic_linear_operator_traces_required": True,
    "full_rerun_byte_identity_required": True,
    "independent_full_processes_required": 2,
    "canonical_promotion_requires_byte_identity": True,
    "reproducibility_evidence_file": (
        "artifacts/data/positive_b_broad_four_slab_reproducibility.json"
    ),
    "subprocess_environment": {
        "PYTHONHASHSEED": "0",
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    },
}
EXPECTED_EXECUTION_BOUNDARY = {
    "formal_execution_requires_explicit_execute_frozen_flag": True,
    "public_and_replica_modes_require_external_manifest_sha256": True,
    "public_entrypoint_runs_two_sequential_subprocess_replicas": True,
    "replica_only_mode_requires_frozen_manifest_sha256": True,
    "canonical_result_promoted_only_after_byte_identity": True,
    "reproducibility_evidence_written_before_canonical_promotion": True,
    "meshes_run_sequentially_within_each_process": True,
    "complete_processes_run_sequentially_for_memory_safety": True,
    "no_elapsed_timestamp_or_temporary_path_in_result_JSON": True,
}
EXPECTED_PREFLIGHT_VALIDATION = {
    "small_mesh_cells": 9,
    "explicit_CSR_row_and_column_actions": True,
    "matrix_and_vector_adjoint_actions": True,
    "full_and_augmented_analytic_traces": True,
    "augmented_block_orientation": True,
    "budget_tangent_B_plus_minus_h": True,
    "p_f_and_four_time_jets": True,
    "actual_root_checkpoint_vs_direct_from_zero": True,
    "S_prime_equals_minus_f": True,
    "Q_one_equals_minus_B_k0": True,
    "three_basin_mass_partition_closure": True,
    "structural_HOLD_null_serialization": True,
    "full_manifest_mutation_rejection": True,
    "two_independent_subprocess_replica_harness": True,
    "tail_35_to_100_gate_regression": True,
    "recursive_nonfinite_rejection": True,
    "native_json_boolean_gate_normalization": True,
    "formal_tests_passed_before_heldout_run": 16,
}
EXPECTED_FORBIDDEN_PROMOTIONS = [
    "preregistered discovery",
    "interval-certified root count",
    "unbounded-domain finite-volume convergence",
    "independent-solver confirmation",
    "physical d=3 confirmation",
    "project or publication gate pass",
]
EXPECTED_LIMITATIONS = [
    "result-informed fixed control and selected budget",
    "two fixed-box finite-volume meshes, not a PDE or unbounded-domain proof",
    "same solver family on both meshes, not independent-solver verification",
    "floating-point sign-screen and root refinement, not interval certification",
    "no physical d=3 or project/publication gate",
]
EXPECTED_AUDIT_EXTREMA = [
    "minimum_sampled_density_from_frozen_start",
    "minimum_streamed_state_component",
    "maximum_sampled_survival_increase",
    "maximum_sampled_differential_mass_balance_residual",
]
FORBIDDEN_METADATA_KEYS = {
    "elapsed_seconds",
    "timestamp",
    "temporary_path",
    "temp_path",
    "output_path",
}

EXPECTED_STAGE = "result_informed_positive_B_broad_four_slab_heldout_mesh_confirmation"
EXPECTED_EVIDENCE_TIMING = "RESULT_INFORMED_FIXED_CONTROL_WITH_HELDOUT_FINE_MESHES"
EXPECTED_TOPOLOGY = ["maximum", "minimum", "maximum", "minimum", "maximum"]
EXPECTED_FIXED_WEIGHTS = [
    0.28,
    0.27736690132708747,
    0.0857172266153233,
    0.3569158720575891,
]
EXPECTED_PHYSICAL_PARAMETERS = {
    "particle_diffusion": 0.002,
    "ou_stiffness": 0.1,
    "ou_mean": 0.95,
    "transverse_width": 1.0,
    "contact_radius": 0.16,
    "midpoint_start": 0.14,
    "initial_half_width": 0.02,
    "relative_parallel_start": -0.35,
    "relative_perp_start": 0.0,
    "patch_centres": [0.35, 0.6, 0.75, 0.9],
    "patch_half_width": 0.04,
    "fixed_first_weight": 0.28,
}
EXPECTED_FINITE_VOLUME = {
    "midpoint_bounds": [-0.25, 1.85],
    "relative_parallel_bounds": [-1.8, 1.8],
    "scheme": "cell-centred Scharfetter-Gummel/periodic killed-Doi tensor generator",
}
EXPECTED_TIME_SCAN = {
    "start": 0.0,
    "stop": 35.0,
    "spacing": 0.02,
    "points": 1751,
    "chunk_points": 11,
    "minimum_root_time": 0.5,
    "saved_trace_spacing": 0.1,
}
EXPECTED_ROOT_GATES = {
    "relative_density_floor": 1.0e-8,
    "minimum_peak_ratio": 0.1,
    "maximum_valley_ratio": 0.85,
    "maximum_scaled_root_residual": 1.0e-8,
    "minimum_absolute_scaled_curvature": 0.05,
    "positive_derivative_time": 0.5,
    "negative_derivative_time": 35.0,
    "maximum_negative_state_tolerance": 1.0e-12,
    "maximum_survival_increase": 1.0e-12,
    "maximum_tangent_state_relative_l1": 1.0e-9,
    "maximum_tangent_time_jet_absolute_difference": 1.0e-9,
}
EXPECTED_TAIL_GATES = {
    "checkpoints": [35.0, 50.0, 75.0, 100.0],
    "minimum_density_sampling_start": 0.5,
    "minimum_density": 0.0,
    "maximum_survival_increase": 1.0e-12,
    "maximum_negative_state_tolerance": 1.0e-12,
}
EXPECTED_EVENT_MASS = {
    "final_time": 100.0,
    "minimum_each_basin_mass": 0.005,
    "maximum_mass_balance_error": 1.0e-9,
}
EXPECTED_MESH_AGREEMENT = {
    "maximum_paired_root_time_difference": 0.1,
    "maximum_peak_ratio_difference": 0.03,
    "maximum_valley_ratio_difference": 0.03,
    "maximum_event_mass_difference": 0.01,
    "maximum_final_survival_difference": 0.02,
}
EXPECTED_FACTOR_NORMALIZATION_TOLERANCE = 1.0e-10
EXPECTED_PIN_ROLES = {
    "B0_bridge_manifest",
    "B0_bridge_producer",
    "B0_bridge_result",
    "exact_continuum_dependency",
    "feasibility_N65_all_budgets",
    "feasibility_N97_B001",
    "feasibility_N97_B002",
    "feasibility_producer",
    "finite_volume_dependency",
    "grid_dependency",
    "operational_erratum",
    "producer",
    "protocol",
    "tests",
}
EXPECTED_MANIFEST_KEYS = {
    "schema_version",
    "stage",
    "freeze_date",
    "known_before_freeze",
    "evidence_timing",
    "claim_scope",
    "physical_parameters",
    "fixed_absolute_weights",
    "positive_budget",
    "selection_record",
    "heldout_meshes",
    "finite_volume",
    "time_scan",
    "root_gates",
    "tail_gates",
    "event_mass",
    "mesh_agreement",
    "numerical_reproducibility",
    "execution_boundary",
    "preflight_validation",
    "required_claim_flags",
    "forbidden_promotions",
    "pinned_files",
}
EXPECTED_RESULT_KEYS = {
    "schema_version",
    "stage",
    "status",
    "evidence_timing",
    "claim_scope",
    "positive_B_event_mass_shape_confirmation",
    *EXPECTED_NEGATIVE_FLAGS,
    "physical_parameters",
    "fixed_absolute_weights",
    "positive_budget",
    "weights_refit",
    "heldout_mesh_rows",
    "mesh_agreement",
    "all_gates_passed",
    "required_claim_flags",
    "numerical_reproducibility",
    "reproducibility_evidence",
    "pinned_file_hashes",
    "manifest_sha256",
    "software",
    "limitations",
}
EXPECTED_RESULT_ROW_KEYS = {
    "mesh",
    "diagnostics",
    "scan",
    "stationary_structure",
    "survival_and_event_mass",
    "tail_35_to_100",
    "time_and_budget_control_jets",
    "gates",
    "all_mesh_gates_passed",
}
EXPECTED_DIAGNOSTIC_KEYS = {
    "mesh",
    "state_count",
    "matrix_free_full_generator",
    "midpoint_generator_nnz",
    "relative_generator_nnz",
    "analytic_column_operator_trace",
    "initial_mass_error",
    "physical_budget",
    "physical_budget_absolute_error",
    "minimum_weight",
    "weight_sum_error",
    "minimum_killing_per_budget",
    "maximum_killing_per_budget",
    "killed_mass_balance_operator_error",
    "factor_diagnostics",
}
EXPECTED_SCAN_KEYS = {
    "time_grid",
    "sampled_peak_density",
    "minimum_sampled_density_from_frozen_start",
    "minimum_density_sampling_start",
    "strict_sign_change_bracket_count",
    "maximum_sampled_survival_increase",
    "minimum_streamed_state_component",
    "maximum_boundary_layer_fraction",
    "maximum_sampled_differential_mass_balance_residual",
    "positive_derivative_checkpoint",
    "derivative_at_scan_stop",
    "survival_at_scan_stop",
    "saved_trace",
}
EXPECTED_SCAN_TRACE_KEYS = {
    "time",
    "f",
    "f_t",
    "f_tt",
    "f_ttt",
    "survival",
    "boundary_layer_fraction",
    "differential_mass_balance_residual",
}
EXPECTED_FACTOR_DIAGNOSTIC_KEYS = {
    "cells_per_coordinate",
    "contact_area",
    "contact_area_error_estimate",
    "contact_area_exact",
    "maximum_initial_quadrature_error_estimate",
    "maximum_patch_quadrature_error_estimate",
    "midpoint_generator_row_error",
    "midpoint_initial_mass",
    "patch_integrals",
    "relative_generator_row_error",
    "relative_initial_mass",
    "spacings",
    "state_count_if_full_matrix_formed",
}
EXPECTED_FACTOR_SPACING_KEYS = {"midpoint", "relative_parallel", "relative_perp"}
EXPECTED_STRUCTURE_KEYS = {
    "stationary_root_count",
    "topology",
    "roots",
    "peak_minimum_to_maximum_ratio",
    "valley_to_smaller_adjacent_peak_ratios",
}
EXPECTED_ROOT_KEYS = {
    "time",
    "topology",
    "density",
    "f_t",
    "f_tt",
    "f_ttt",
    "survival",
    "boundary_layer_fraction",
    "scaled_first_derivative_residual",
    "scaled_second_derivative",
    "differential_mass_balance_residual",
    "minimum_state_component",
}
EXPECTED_MASS_KEYS = {
    "final_time",
    "final_survival",
    "total_reaction_mass_to_final_time",
    "basin_reaction_masses",
    "basin_mass_sum",
    "basin_mass_sum_vs_total_reaction_difference",
    "final_differential_mass_balance_residual",
}
EXPECTED_TAIL_KEYS = {
    "checkpoints",
    "trace",
    "survival_at_scan_stop",
    "final_survival",
    "survival_decrease_from_scan_stop",
    "maximum_checkpoint_survival_increase",
    "minimum_checkpoint_density",
    "minimum_tail_state_component",
    "minimum_final_state_component",
    "maximum_checkpoint_differential_mass_balance_residual",
}
EXPECTED_TAIL_TRACE_KEYS = {
    "time",
    "density",
    "survival",
    "minimum_state_component",
    "differential_mass_balance_residual",
}
EXPECTED_CONTROL_KEYS = {
    "control_variable",
    "analytic_augmented_operator_trace",
    "rows",
    "maximum_direct_vs_tangent_state_relative_l1",
    "maximum_direct_vs_tangent_time_jet_absolute_difference",
}
EXPECTED_CONTROL_ROW_KEYS = {
    "time",
    "time_jets_f_f_t_f_tt_f_ttt",
    "budget_control_jets",
    "direct_vs_tangent_state_relative_l1",
    "maximum_direct_vs_tangent_time_jet_absolute_difference",
}
EXPECTED_BUDGET_CONTROL_KEYS = {"f_B", "f_tB", "f_ttB", "survival_B"}
EXPECTED_GATE_KEYS = {
    "initial_mass",
    "physical_budget",
    "weights_positive_unit_sum",
    "five_alternating_simple_roots",
    "peak_ratio",
    "valley_ratios",
    "root_residuals",
    "curvature_margins",
    "endpoint_derivative_signs",
    "sampled_density_positive",
    "root_density_positive",
    "survival_positive",
    "state_positivity_tolerance",
    "survival_monotone_through_final_time",
    "tail_final_state_positivity",
    "generator_Q_one_equals_minus_B_k0",
    "mass_balance_on_saved_scan",
    "mass_balance_at_roots",
    "mass_balance_at_final_time",
    "mass_balance_on_tail_checkpoints",
    "event_basin_masses",
    "event_mass_partition_closure",
    "tangent_state_reproduction",
    "tangent_time_jet_reproduction",
}
EXPECTED_AGREEMENT_GATE_KEYS = {
    "paired_root_times",
    "peak_ratio",
    "valley_ratios",
    "event_basin_masses",
    "final_survival",
}
EXPECTED_AGREEMENT_KEYS = {
    "mesh_pair",
    "maximum_paired_root_time_difference",
    "peak_ratio_absolute_difference",
    "maximum_valley_ratio_absolute_difference",
    "maximum_event_mass_absolute_difference",
    "final_survival_absolute_difference",
    "gates",
    "all_agreement_gates_passed",
}


@dataclass(frozen=True)
class FileSnapshot:
    """One ordinary-file payload whose hash and parser see identical bytes."""

    path: Path
    sha256: str
    payload: bytes


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def require_finite_json(value: Any, location: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"nonfinite JSON number at {location}")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            require_finite_json(item, f"{location}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError(f"non-string JSON key at {location}")
            require_finite_json(item, f"{location}.{key}")
        return
    raise TypeError(f"unsupported JSON value at {location}: {type(value).__name__}")


def canonical_json_bytes(value: dict[str, Any]) -> bytes:
    require_finite_json(value)
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def load_object_from_bytes(
    payload: bytes,
    *,
    label: str,
    require_canonical: bool,
) -> dict[str, Any]:
    value = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_reject_duplicate_pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    if type(value) is not dict:
        raise TypeError(f"{label} must contain one JSON object")
    require_finite_json(value)
    if require_canonical and canonical_json_bytes(value) != payload:
        raise RuntimeError(f"{label} is not canonical JSON")
    return value


def load_object(path: Path, *, require_canonical: bool) -> dict[str, Any]:
    return load_object_from_bytes(
        path.read_bytes(),
        label=str(path),
        require_canonical=require_canonical,
    )


def _snapshot_regular_file(path: Path, *, root: Path, label: str) -> FileSnapshot:
    """Read one contained ordinary file once with no symlink traversal at any component."""

    root = root.resolve(strict=True)
    candidate = Path(os.path.abspath(path))
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise RuntimeError(f"{label} escapes the report root") from error
    if not relative.parts:
        raise RuntimeError(f"{label} is not a file below the report root")

    current = root
    for index, component in enumerate(relative.parts):
        current = current / component
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError as error:
            raise FileNotFoundError(f"{label} is missing: {current}") from error
        if stat.S_ISLNK(mode):
            raise RuntimeError(f"{label} must be an ordinary nonsymlink file")
        if index < len(relative.parts) - 1 and not stat.S_ISDIR(mode):
            raise RuntimeError(f"{label} has a non-directory path component")
        if index == len(relative.parts) - 1 and not stat.S_ISREG(mode):
            raise RuntimeError(f"{label} must be an ordinary nonsymlink file")

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(candidate, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise RuntimeError(f"{label} must be an ordinary nonsymlink file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
        ):
            raise RuntimeError(f"{label} changed while its snapshot was read")
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if len(payload) != after.st_size:
        raise RuntimeError(f"{label} was not read completely")
    return FileSnapshot(path=candidate, sha256=sha256_bytes(payload), payload=payload)


def _snapshot_report_path(report: Path, relative: object, *, label: str) -> FileSnapshot:
    if not isinstance(relative, str) or not relative:
        raise RuntimeError(f"{label} has an invalid path")
    raw = Path(relative)
    if raw.is_absolute() or ".." in raw.parts:
        raise RuntimeError(f"{label} escapes the report root")
    return _snapshot_regular_file(report / raw, root=report, label=label)


def _require_snapshot_hash(snapshot: FileSnapshot, expected: str, *, label: str) -> None:
    observed = snapshot.sha256
    if observed != expected:
        raise RuntimeError(f"{label} SHA-256 mismatch: expected {expected}, observed {observed}")


def _exact_keys(value: object, expected: set[str], *, label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != expected:
        observed = sorted(value) if type(value) is dict else type(value).__name__
        raise RuntimeError(f"{label} schema changed: {observed}")
    return value


def _exact_json_equal(observed: object, expected: object) -> bool:
    """Compare JSON values without Python's bool/int or int/float aliases."""

    if type(observed) is not type(expected):
        return False
    if type(expected) is dict:
        return set(observed) == set(expected) and all(
            _exact_json_equal(observed[key], expected[key]) for key in expected
        )
    if type(expected) is list:
        return len(observed) == len(expected) and all(
            _exact_json_equal(left, right)
            for left, right in zip(observed, expected, strict=True)
        )
    return observed == expected


def _recursive_key_paths(
    value: object, prefix: tuple[object, ...] = ()
) -> list[tuple[object, ...]]:
    paths: list[tuple[object, ...]] = []
    if type(value) is dict:
        for key, item in value.items():
            path = (*prefix, key)
            paths.append(path)
            paths.extend(_recursive_key_paths(item, path))
    elif type(value) is list:
        for index, item in enumerate(value):
            paths.extend(_recursive_key_paths(item, (*prefix, index)))
    return paths


def _require_authorized_claim_keys(result: dict[str, Any]) -> None:
    authorized: dict[str, set[tuple[object, ...]]] = {
        key: {(key,), ("required_claim_flags", key)} for key in EXPECTED_NEGATIVE_FLAGS
    }
    authorized["positive_B_event_mass_shape_confirmation"] = {
        ("positive_B_event_mass_shape_confirmation",)
    }
    for forbidden in (
        "allocation_cusp_verified",
        "physical_d3_verified",
        "continuum_verified",
        "publication_gate_passed",
    ):
        authorized[forbidden] = set()
    paths = _recursive_key_paths(result)
    for key, allowed in authorized.items():
        observed = {path for path in paths if path[-1] == key}
        if observed != allowed:
            raise RuntimeError(f"claim key {key} appears at an unauthorized location")


def _require_no_temporary_metadata(value: dict[str, Any], *, label: str) -> None:
    paths = _recursive_key_paths(value)
    keys = {path[-1] for path in paths if isinstance(path[-1], str)}
    if not keys.isdisjoint(FORBIDDEN_METADATA_KEYS):
        raise RuntimeError(f"{label} contains temporary metadata")

    def strings(item: object) -> list[str]:
        if type(item) is str:
            return [item]
        if type(item) is dict:
            return [text for child in item.values() for text in strings(child)]
        if type(item) is list:
            return [text for child in item for text in strings(child)]
        return []

    if any(
        token in text
        for text in strings(value)
        for token in (".replica_", ".staging", ".backup")
    ):
        raise RuntimeError(f"{label} exposes a temporary path")


def _number(value: object, *, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(float(value)):
        raise RuntimeError(f"{label} must be a finite JSON number")
    return float(value)


def _nonnegative_number(value: object, *, label: str) -> float:
    result = _number(value, label=label)
    if result < 0.0:
        raise RuntimeError(f"{label} must be nonnegative")
    return result


def _positive_number(value: object, *, label: str) -> float:
    result = _number(value, label=label)
    if result <= 0.0:
        raise RuntimeError(f"{label} must be positive")
    return result


def _unit_interval_number(value: object, *, label: str, tolerance: float = 0.0) -> float:
    result = _number(value, label=label)
    if not -tolerance <= result <= 1.0 + tolerance:
        raise RuntimeError(f"{label} must lie in [0,1] within tolerance")
    return result


def _number_list(value: object, length: int, *, label: str) -> list[float]:
    if type(value) is not list or len(value) != length:
        raise RuntimeError(f"{label} must contain exactly {length} numbers")
    return [_number(item, label=f"{label}[{index}]") for index, item in enumerate(value)]


def _close_list(left: list[float], right: object) -> bool:
    return type(right) is list and len(left) == len(right) and all(
        _close(a, b) for a, b in zip(left, right, strict=True)
    )


def _close(left: float, right: float, tolerance: float = 2.0e-15) -> bool:
    return math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=tolerance)


def _validate_mesh_row(
    row: dict[str, Any],
    cells: int,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Reconstruct every claim-bearing mesh gate without trusting saved Booleans."""

    _exact_keys(row, EXPECTED_RESULT_ROW_KEYS, label=f"mesh {cells} row")
    if not _exact_json_equal(row["mesh"], [cells, cells, cells]):
        raise RuntimeError(f"mesh {cells} row identity changed")
    diagnostics = _exact_keys(
        row["diagnostics"], EXPECTED_DIAGNOSTIC_KEYS, label=f"mesh {cells} diagnostics"
    )
    scan = _exact_keys(row["scan"], EXPECTED_SCAN_KEYS, label=f"mesh {cells} scan")
    structure = _exact_keys(
        row["stationary_structure"],
        EXPECTED_STRUCTURE_KEYS,
        label=f"mesh {cells} stationary structure",
    )
    event = _exact_keys(
        row["survival_and_event_mass"], EXPECTED_MASS_KEYS, label=f"mesh {cells} event mass"
    )
    tail = _exact_keys(row["tail_35_to_100"], EXPECTED_TAIL_KEYS, label=f"mesh {cells} tail")
    control = _exact_keys(
        row["time_and_budget_control_jets"],
        EXPECTED_CONTROL_KEYS,
        label=f"mesh {cells} tangent control",
    )
    reported_gates = _exact_keys(
        row["gates"], EXPECTED_GATE_KEYS, label=f"mesh {cells} gate map"
    )
    if any(type(value) is not bool for value in reported_gates.values()):
        raise RuntimeError(f"mesh {cells} gate map contains a non-Boolean value")
    if type(row["all_mesh_gates_passed"]) is not bool:
        raise RuntimeError(f"mesh {cells} aggregate gate must be Boolean")
    survival_tolerance = _nonnegative_number(
        manifest["root_gates"]["maximum_negative_state_tolerance"],
        label="survival tolerance",
    )

    weights = _number_list(manifest["fixed_absolute_weights"], 4, label="manifest weights")
    budget = _number(manifest["positive_budget"], label="manifest positive budget")
    for key in ("state_count", "midpoint_generator_nnz", "relative_generator_nnz"):
        value = diagnostics[key]
        if type(value) is not int or value <= 0:
            raise RuntimeError(f"mesh {cells} diagnostics.{key} must be a positive integer")
    for key in EXPECTED_DIAGNOSTIC_KEYS - {
        "mesh",
        "state_count",
        "matrix_free_full_generator",
        "midpoint_generator_nnz",
        "relative_generator_nnz",
        "factor_diagnostics",
    }:
        _number(diagnostics[key], label=f"mesh {cells} diagnostics.{key}")
    for key in (
        "initial_mass_error",
        "physical_budget_absolute_error",
        "weight_sum_error",
        "killed_mass_balance_operator_error",
    ):
        _nonnegative_number(diagnostics[key], label=f"mesh {cells} diagnostics.{key}")
    _nonnegative_number(
        diagnostics["physical_budget"], label=f"mesh {cells} diagnostics.physical_budget"
    )
    if not _exact_json_equal(diagnostics["mesh"], [cells, cells, cells]):
        raise RuntimeError(f"mesh {cells} diagnostics identity changed")
    if diagnostics["matrix_free_full_generator"] is not True:
        raise RuntimeError(f"mesh {cells} matrix-free flag changed")
    if diagnostics["state_count"] != cells**3:
        raise RuntimeError(f"mesh {cells} state count changed")
    factor = _exact_keys(
        diagnostics["factor_diagnostics"],
        EXPECTED_FACTOR_DIAGNOSTIC_KEYS,
        label=f"mesh {cells} factor diagnostics",
    )
    for key in EXPECTED_FACTOR_DIAGNOSTIC_KEYS - {
        "cells_per_coordinate",
        "patch_integrals",
        "spacings",
        "state_count_if_full_matrix_formed",
    }:
        _number(factor[key], label=f"mesh {cells} factor diagnostics.{key}")
    for key in (
        "contact_area_error_estimate",
        "maximum_initial_quadrature_error_estimate",
        "maximum_patch_quadrature_error_estimate",
        "midpoint_generator_row_error",
        "relative_generator_row_error",
    ):
        _nonnegative_number(factor[key], label=f"mesh {cells} factor diagnostics.{key}")
    for key in (
        "contact_area",
        "contact_area_exact",
        "midpoint_initial_mass",
        "relative_initial_mass",
    ):
        _positive_number(factor[key], label=f"mesh {cells} factor diagnostics.{key}")
    patch_integrals = _number_list(
        factor["patch_integrals"], 4, label=f"mesh {cells} factor patch integrals"
    )
    if min(patch_integrals) <= 0.0:
        raise RuntimeError(f"mesh {cells} factor patch integrals must be positive")
    spacings = _exact_keys(
        factor["spacings"],
        EXPECTED_FACTOR_SPACING_KEYS,
        label=f"mesh {cells} factor spacings",
    )
    for key, value in spacings.items():
        _positive_number(value, label=f"mesh {cells} factor spacing {key}")
    midpoint_bounds = _number_list(
        manifest["finite_volume"]["midpoint_bounds"], 2, label="midpoint bounds"
    )
    parallel_bounds = _number_list(
        manifest["finite_volume"]["relative_parallel_bounds"],
        2,
        label="relative-parallel bounds",
    )
    expected_spacings = {
        "midpoint": (midpoint_bounds[1] - midpoint_bounds[0]) / cells,
        "relative_parallel": (parallel_bounds[1] - parallel_bounds[0]) / cells,
        "relative_perp": _number(
            manifest["physical_parameters"]["transverse_width"],
            label="transverse width",
        )
        / cells,
    }
    if any(not _close(spacings[key], expected) for key, expected in expected_spacings.items()):
        raise RuntimeError(f"mesh {cells} factor spacings contradict the frozen box")

    contact_area_exact = math.pi * _number(
        manifest["physical_parameters"]["contact_radius"], label="contact radius"
    ) ** 2
    if not _close(factor["contact_area_exact"], contact_area_exact):
        raise RuntimeError(f"mesh {cells} exact contact area contradicts the frozen radius")
    normalization_deviations = {
        "contact area": abs(
            _number(factor["contact_area"], label="contact area")
            - _number(factor["contact_area_exact"], label="exact contact area")
        ),
        "midpoint initial mass": abs(
            _number(factor["midpoint_initial_mass"], label="midpoint initial mass") - 1.0
        ),
        "relative initial mass": abs(
            _number(factor["relative_initial_mass"], label="relative initial mass") - 1.0
        ),
        "patch integrals": max(abs(value - 1.0) for value in patch_integrals),
        "midpoint generator row sum": _number(
            factor["midpoint_generator_row_error"], label="midpoint generator row error"
        ),
        "relative generator row sum": _number(
            factor["relative_generator_row_error"], label="relative generator row error"
        ),
    }
    if max(normalization_deviations.values()) > EXPECTED_FACTOR_NORMALIZATION_TOLERANCE:
        failed = sorted(
            key
            for key, value in normalization_deviations.items()
            if value > EXPECTED_FACTOR_NORMALIZATION_TOLERANCE
        )
        raise RuntimeError(f"mesh {cells} factor normalization fails: {failed}")
    error_estimate_bounds = {
        "contact area": _number(
            factor["contact_area_error_estimate"], label="contact-area error estimate"
        ),
        "midpoint initial mass": _number(
            factor["maximum_initial_quadrature_error_estimate"],
            label="initial quadrature error estimate",
        ),
        "relative initial mass": _number(
            factor["maximum_initial_quadrature_error_estimate"],
            label="initial quadrature error estimate",
        ),
        "patch integrals": _number(
            factor["maximum_patch_quadrature_error_estimate"],
            label="patch quadrature error estimate",
        ),
    }
    if any(
        normalization_deviations[key] > error_estimate + 5.0e-15
        for key, error_estimate in error_estimate_bounds.items()
    ):
        raise RuntimeError(f"mesh {cells} quadrature error estimate is not conservative")
    if (
        type(factor["cells_per_coordinate"]) is not int
        or type(factor["state_count_if_full_matrix_formed"]) is not int
        or factor["cells_per_coordinate"] != cells
        or factor["state_count_if_full_matrix_formed"] != cells**3
    ):
        raise RuntimeError(f"mesh {cells} factor diagnostics identity changed")
    if not _close(diagnostics["minimum_weight"], min(weights)):
        raise RuntimeError(f"mesh {cells} minimum weight does not match the manifest")
    if not _close(diagnostics["weight_sum_error"], abs(sum(weights) - 1.0)):
        raise RuntimeError(f"mesh {cells} weight-sum error does not reconstruct")
    if _number(
        diagnostics["analytic_column_operator_trace"],
        label=f"mesh {cells} analytic killed-generator trace",
    ) >= 0.0:
        raise RuntimeError(f"mesh {cells} analytic killed-generator trace must be negative")
    if not _close(
        diagnostics["physical_budget_absolute_error"],
        abs(_number(diagnostics["physical_budget"], label="physical budget") - budget),
    ):
        raise RuntimeError(f"mesh {cells} physical-budget error does not reconstruct")
    reconstructed_budget = budget * sum(
        weight * integral
        for weight, integral in zip(weights, patch_integrals, strict=True)
    )
    if not _close(diagnostics["physical_budget"], reconstructed_budget):
        raise RuntimeError(f"mesh {cells} physical budget contradicts patch integrals")
    minimum_killing = _nonnegative_number(
        diagnostics["minimum_killing_per_budget"], label=f"mesh {cells} minimum killing"
    )
    maximum_killing = _number(
        diagnostics["maximum_killing_per_budget"], label=f"mesh {cells} maximum killing"
    )
    if maximum_killing < minimum_killing:
        raise RuntimeError(f"mesh {cells} killing range is invalid")

    time_rules = _exact_keys(
        manifest["time_scan"],
        {"start", "stop", "spacing", "points", "chunk_points", "minimum_root_time", "saved_trace_spacing"},
        label="manifest time scan",
    )
    expected_grid = {
        key: time_rules[key] for key in ("start", "stop", "spacing", "points", "chunk_points")
    }
    if not _exact_json_equal(scan["time_grid"], expected_grid):
        raise RuntimeError(f"mesh {cells} time grid changed")
    if scan["minimum_density_sampling_start"] != manifest["tail_gates"]["minimum_density_sampling_start"]:
        raise RuntimeError(f"mesh {cells} density sampling start changed")
    if type(scan["strict_sign_change_bracket_count"]) is not int:
        raise RuntimeError(f"mesh {cells} bracket count must be an integer")
    for key in EXPECTED_SCAN_KEYS - {
        "time_grid",
        "strict_sign_change_bracket_count",
        "positive_derivative_checkpoint",
        "saved_trace",
    }:
        _number(scan[key], label=f"mesh {cells} scan.{key}")
    _nonnegative_number(
        scan["maximum_sampled_differential_mass_balance_residual"],
        label=f"mesh {cells} scan maximum mass residual",
    )
    _unit_interval_number(
        scan["maximum_boundary_layer_fraction"],
        label=f"mesh {cells} scan maximum boundary fraction",
        tolerance=survival_tolerance,
    )
    saved_trace = scan["saved_trace"]
    saved_spacing = _number(time_rules["saved_trace_spacing"], label="saved trace spacing")
    expected_saved_count = int(
        round(
            (_number(time_rules["stop"], label="scan stop") - _number(time_rules["start"], label="scan start"))
            / saved_spacing
        )
    ) + 1
    if type(saved_trace) is not list or len(saved_trace) != expected_saved_count:
        raise RuntimeError(f"mesh {cells} saved trace length changed")
    for index, trace_row in enumerate(saved_trace):
        _exact_keys(trace_row, EXPECTED_SCAN_TRACE_KEYS, label=f"mesh {cells} trace row {index}")
        for key in EXPECTED_SCAN_TRACE_KEYS:
            _number(trace_row[key], label=f"mesh {cells} trace row {index}.{key}")
        expected_time = _number(time_rules["start"], label="scan start") + index * saved_spacing
        if not _close(trace_row["time"], expected_time):
            raise RuntimeError(f"mesh {cells} saved trace time {index} changed")
        boundary_fraction = _number(
            trace_row["boundary_layer_fraction"],
            label=f"mesh {cells} trace row {index} boundary fraction",
        )
        _unit_interval_number(
            boundary_fraction,
            label=f"mesh {cells} trace row {index} boundary fraction",
            tolerance=survival_tolerance,
        )
        if _number(
            trace_row["differential_mass_balance_residual"],
            label=f"mesh {cells} trace row {index} mass residual",
        ) < 0.0:
            raise RuntimeError(f"mesh {cells} saved trace mass residual is negative")
        _unit_interval_number(
            trace_row["survival"],
            label=f"mesh {cells} trace row {index} survival",
            tolerance=survival_tolerance,
        )
    positive_time = _number(
        manifest["root_gates"]["positive_derivative_time"], label="positive derivative time"
    )
    positive_index = int(round((positive_time - _number(time_rules["start"], label="scan start")) / saved_spacing))
    checkpoint = _exact_keys(
        scan["positive_derivative_checkpoint"], {"time", "f_t"}, label=f"mesh {cells} endpoint checkpoint"
    )
    _number(checkpoint["time"], label=f"mesh {cells} checkpoint time")
    _number(checkpoint["f_t"], label=f"mesh {cells} checkpoint derivative")
    if not _close(checkpoint["time"], positive_time) or not _close(
        checkpoint["f_t"], saved_trace[positive_index]["f_t"]
    ):
        raise RuntimeError(f"mesh {cells} positive endpoint duplicate changed")
    if not _close(scan["derivative_at_scan_stop"], saved_trace[-1]["f_t"]) or not _close(
        scan["survival_at_scan_stop"], saved_trace[-1]["survival"]
    ):
        raise RuntimeError(f"mesh {cells} scan endpoint duplicate changed")
    if _number(scan["sampled_peak_density"], label="sampled peak") + 5.0e-15 < max(
        _number(item["f"], label="saved density") for item in saved_trace
    ):
        raise RuntimeError(f"mesh {cells} sampled peak contradicts its saved trace")
    sampled_from = _number(
        scan["minimum_density_sampling_start"], label="density sampling start"
    )
    sampled_trace = [
        item for item in saved_trace if _number(item["time"], label="saved time") >= sampled_from
    ]
    if not sampled_trace:
        raise RuntimeError(f"mesh {cells} saved density subset is empty")
    if _number(
        scan["minimum_sampled_density_from_frozen_start"], label="sampled density minimum"
    ) - 5.0e-15 > min(_number(item["f"], label="saved density") for item in sampled_trace):
        raise RuntimeError(f"mesh {cells} sampled minimum contradicts its saved trace")
    if _number(
        scan["maximum_boundary_layer_fraction"], label="boundary-layer maximum"
    ) + 5.0e-15 < max(
        _number(item["boundary_layer_fraction"], label="saved boundary fraction")
        for item in saved_trace
    ):
        raise RuntimeError(f"mesh {cells} boundary maximum contradicts its saved trace")
    if _number(
        scan["maximum_sampled_differential_mass_balance_residual"],
        label="sampled mass-balance maximum",
    ) + 5.0e-15 < max(
        _number(item["differential_mass_balance_residual"], label="saved mass residual")
        for item in saved_trace
    ):
        raise RuntimeError(f"mesh {cells} mass residual contradicts its saved trace")
    saved_survival_increases = [
        _number(right["survival"], label="saved survival")
        - _number(left["survival"], label="saved survival")
        for left, right in zip(saved_trace[:-1], saved_trace[1:], strict=True)
    ]
    trace_stride = int(
        round(saved_spacing / _number(time_rules["spacing"], label="scan spacing"))
    )
    if trace_stride <= 0:
        raise RuntimeError(f"mesh {cells} saved trace stride is invalid")
    if _number(
        scan["maximum_sampled_survival_increase"], label="sampled survival increase"
    ) + 5.0e-15 < max(saved_survival_increases) / trace_stride:
        raise RuntimeError(f"mesh {cells} survival-increase summary contradicts its saved trace")

    roots = structure["roots"]
    if (
        type(structure["stationary_root_count"]) is not int
        or type(roots) is not list
        or len(roots) != 5
        or structure["stationary_root_count"] != 5
    ):
        raise RuntimeError(f"mesh {cells} must contain exactly five retained roots")
    if scan["strict_sign_change_bracket_count"] != 5:
        raise RuntimeError(f"mesh {cells} root screen no longer has exactly five sign brackets")
    times: list[float] = []
    densities: list[float] = []
    survivals: list[float] = []
    topology: list[str] = []
    root_rules = manifest["root_gates"]
    density_floor = _number(root_rules["relative_density_floor"], label="relative density floor") * _number(
        scan["sampled_peak_density"], label="sampled peak"
    )
    for index, root in enumerate(roots):
        _exact_keys(root, EXPECTED_ROOT_KEYS, label=f"mesh {cells} root {index}")
        for key in EXPECTED_ROOT_KEYS - {"topology"}:
            _number(root[key], label=f"mesh {cells} root {index}.{key}")
        time_value = _number(root["time"], label=f"mesh {cells} root time")
        density = _number(root["density"], label=f"mesh {cells} root density")
        f_t = _number(root["f_t"], label=f"mesh {cells} root f_t")
        f_tt = _number(root["f_tt"], label=f"mesh {cells} root f_tt")
        if not (
            _number(time_rules["minimum_root_time"], label="minimum root time")
            <= time_value
            <= _number(time_rules["stop"], label="scan stop")
        ):
            raise RuntimeError(f"mesh {cells} root {index} lies outside the saved root screen")
        if density < density_floor:
            raise RuntimeError(f"mesh {cells} root {index} falls below the relative density floor")
        _nonnegative_number(
            root["scaled_first_derivative_residual"],
            label=f"mesh {cells} root {index} scaled residual",
        )
        _nonnegative_number(
            root["differential_mass_balance_residual"],
            label=f"mesh {cells} root {index} mass residual",
        )
        _unit_interval_number(
            root["boundary_layer_fraction"],
            label=f"mesh {cells} root {index} boundary fraction",
            tolerance=survival_tolerance,
        )
        _unit_interval_number(
            root["survival"],
            label=f"mesh {cells} root {index} survival",
            tolerance=survival_tolerance,
        )
        derived_topology = "maximum" if f_tt < 0.0 else "minimum"
        if root["topology"] != derived_topology:
            raise RuntimeError(f"mesh {cells} root {index} topology contradicts curvature")
        if not _close(root["scaled_first_derivative_residual"], abs(time_value * f_t / density)):
            raise RuntimeError(f"mesh {cells} root {index} residual identity failed")
        if not _close(root["scaled_second_derivative"], time_value**2 * f_tt / density):
            raise RuntimeError(f"mesh {cells} root {index} curvature identity failed")
        times.append(time_value)
        densities.append(density)
        survivals.append(_number(root["survival"], label=f"mesh {cells} root survival"))
        topology.append(derived_topology)
    if topology != EXPECTED_TOPOLOGY or structure["topology"] != EXPECTED_TOPOLOGY:
        raise RuntimeError(f"mesh {cells} root topology changed")
    if any(right <= left for left, right in zip(times[:-1], times[1:], strict=True)):
        raise RuntimeError(f"mesh {cells} root times are not strictly ordered")
    if any(right >= left for left, right in zip(survivals[:-1], survivals[1:], strict=True)):
        raise RuntimeError(f"mesh {cells} root survivals are not strictly decreasing")
    if scan["strict_sign_change_bracket_count"] < len(roots):
        raise RuntimeError(f"mesh {cells} saved root screen has too few sign brackets")
    for index, (time_value, root_survival) in enumerate(zip(times, survivals, strict=True)):
        bracket = next(
            (
                (left, right)
                for left, right in zip(saved_trace[:-1], saved_trace[1:], strict=True)
                if _number(left["time"], label="saved time")
                <= time_value
                <= _number(right["time"], label="saved time")
            ),
            None,
        )
        if bracket is None:
            raise RuntimeError(f"mesh {cells} root {index} lies outside the saved trace")
        left, right = bracket
        if _number(left["f_t"], label="saved derivative") * _number(
            right["f_t"], label="saved derivative"
        ) > 0.0:
            raise RuntimeError(f"mesh {cells} root {index} lacks a saved-trace sign bracket")
        bracket_survivals = (
            _number(left["survival"], label="saved survival"),
            _number(right["survival"], label="saved survival"),
        )
        if not (
            min(bracket_survivals) - survival_tolerance
            <= root_survival
            <= max(bracket_survivals) + survival_tolerance
        ):
            raise RuntimeError(
                f"mesh {cells} root {index} survival lies outside its saved-trace bracket"
            )

    peak_densities = [densities[index] for index in (0, 2, 4)]
    peak_ratio = min(peak_densities) / max(peak_densities)
    valleys = [
        densities[1] / min(peak_densities[0], peak_densities[1]),
        densities[3] / min(peak_densities[1], peak_densities[2]),
    ]
    _unit_interval_number(
        structure["peak_minimum_to_maximum_ratio"], label=f"mesh {cells} peak ratio"
    )
    reported_valleys = _number_list(
        structure["valley_to_smaller_adjacent_peak_ratios"],
        2,
        label=f"mesh {cells} valley ratios",
    )
    if any(not 0.0 <= value <= 1.0 for value in reported_valleys):
        raise RuntimeError(f"mesh {cells} valley ratios must lie in [0,1]")
    if not _close(peak_ratio, structure["peak_minimum_to_maximum_ratio"]):
        raise RuntimeError(f"mesh {cells} peak ratio does not reconstruct")
    if not _close_list(valleys, reported_valleys):
        raise RuntimeError(f"mesh {cells} valley ratios do not reconstruct")

    tail_rules = manifest["tail_gates"]
    for key in EXPECTED_TAIL_KEYS - {"checkpoints", "trace"}:
        _number(tail[key], label=f"mesh {cells} tail.{key}")
    if not _exact_json_equal(tail["checkpoints"], tail_rules["checkpoints"]):
        raise RuntimeError(f"mesh {cells} tail checkpoints changed")
    tail_trace = tail["trace"]
    if type(tail_trace) is not list or len(tail_trace) != len(tail_rules["checkpoints"]):
        raise RuntimeError(f"mesh {cells} tail trace changed")
    for index, tail_row in enumerate(tail_trace):
        _exact_keys(tail_row, EXPECTED_TAIL_TRACE_KEYS, label=f"mesh {cells} tail row {index}")
        for key in EXPECTED_TAIL_TRACE_KEYS:
            _number(tail_row[key], label=f"mesh {cells} tail row {index}.{key}")
        if not _close(tail_row["time"], tail_rules["checkpoints"][index]):
            raise RuntimeError(f"mesh {cells} tail time {index} changed")
        _nonnegative_number(
            tail_row["differential_mass_balance_residual"],
            label=f"mesh {cells} tail row {index} mass residual",
        )
        _unit_interval_number(
            tail_row["survival"],
            label=f"mesh {cells} tail row {index} survival",
            tolerance=survival_tolerance,
        )
    _nonnegative_number(
        tail["maximum_checkpoint_differential_mass_balance_residual"],
        label=f"mesh {cells} tail maximum mass residual",
    )
    tail_survival_increases = [
        _number(right["survival"], label="tail survival")
        - _number(left["survival"], label="tail survival")
        for left, right in zip(tail_trace[:-1], tail_trace[1:], strict=True)
    ]
    tail_identities = {
        "survival_at_scan_stop": tail_trace[0]["survival"],
        "final_survival": tail_trace[-1]["survival"],
        "survival_decrease_from_scan_stop": _number(tail_trace[0]["survival"], label="tail survival")
        - _number(tail_trace[-1]["survival"], label="tail survival"),
        "maximum_checkpoint_survival_increase": max(tail_survival_increases),
        "minimum_checkpoint_density": min(_number(item["density"], label="tail density") for item in tail_trace),
        "minimum_tail_state_component": min(
            _number(item["minimum_state_component"], label="tail state") for item in tail_trace
        ),
        "minimum_final_state_component": tail_trace[-1]["minimum_state_component"],
        "maximum_checkpoint_differential_mass_balance_residual": max(
            _number(item["differential_mass_balance_residual"], label="tail mass residual")
            for item in tail_trace
        ),
    }
    if any(not _close(tail[key], value) for key, value in tail_identities.items()):
        raise RuntimeError(f"mesh {cells} tail summaries do not reconstruct")
    if not (
        _close(tail_trace[0]["density"], saved_trace[-1]["f"])
        and _close(tail_trace[0]["survival"], saved_trace[-1]["survival"])
        and _close(
            tail_trace[0]["differential_mass_balance_residual"],
            saved_trace[-1]["differential_mass_balance_residual"],
        )
        and _close(tail["survival_at_scan_stop"], scan["survival_at_scan_stop"])
    ):
        raise RuntimeError(f"mesh {cells} scan/tail junction changed")

    final_time = _number(event["final_time"], label=f"mesh {cells} final time")
    if not _close(final_time, manifest["event_mass"]["final_time"]):
        raise RuntimeError(f"mesh {cells} final time changed")
    final_survival = _number(event["final_survival"], label=f"mesh {cells} final survival")
    _unit_interval_number(
        final_survival,
        label=f"mesh {cells} final survival",
        tolerance=survival_tolerance,
    )
    for key in EXPECTED_MASS_KEYS - {"basin_reaction_masses"}:
        _number(event[key], label=f"mesh {cells} event mass.{key}")
    _nonnegative_number(
        event["final_differential_mass_balance_residual"],
        label=f"mesh {cells} final mass residual",
    )
    _nonnegative_number(
        event["basin_mass_sum_vs_total_reaction_difference"],
        label=f"mesh {cells} basin partition difference",
    )
    if not _close(final_survival, tail["final_survival"]):
        raise RuntimeError(f"mesh {cells} final survival duplicate changed")
    masses = [
        1.0 - survivals[1],
        survivals[1] - survivals[3],
        survivals[3] - final_survival,
    ]
    saved_masses = _number_list(event["basin_reaction_masses"], 3, label=f"mesh {cells} basin masses")
    if not _close_list(masses, saved_masses):
        raise RuntimeError(f"mesh {cells} basin masses do not reconstruct")
    total_reaction = 1.0 - final_survival
    if not (
        _close(event["total_reaction_mass_to_final_time"], total_reaction)
        and _close(event["basin_mass_sum"], sum(masses))
        and _close(event["basin_mass_sum_vs_total_reaction_difference"], abs(sum(masses) - total_reaction))
        and _close(event["final_differential_mass_balance_residual"], tail_trace[-1]["differential_mass_balance_residual"])
    ):
        raise RuntimeError(f"mesh {cells} event-mass summaries do not reconstruct")

    _exact_keys(control, EXPECTED_CONTROL_KEYS, label=f"mesh {cells} tangent control")
    if control["control_variable"] != "full installed budget B":
        raise RuntimeError(f"mesh {cells} tangent control variable changed")
    augmented_trace = _number(
        control["analytic_augmented_operator_trace"],
        label=f"mesh {cells} augmented operator trace",
    )
    base_trace = _number(
        diagnostics["analytic_column_operator_trace"],
        label=f"mesh {cells} analytic killed-generator trace",
    )
    if not _close(augmented_trace, 2.0 * base_trace):
        raise RuntimeError(f"mesh {cells} augmented trace is not twice the base trace")
    _nonnegative_number(
        control["maximum_direct_vs_tangent_state_relative_l1"],
        label=f"mesh {cells} maximum tangent state difference",
    )
    _nonnegative_number(
        control["maximum_direct_vs_tangent_time_jet_absolute_difference"],
        label=f"mesh {cells} maximum tangent jet difference",
    )
    control_rows = control["rows"]
    if type(control_rows) is not list or len(control_rows) != 5:
        raise RuntimeError(f"mesh {cells} tangent rows changed")
    state_differences: list[float] = []
    jet_differences: list[float] = []
    for index, (control_row, root) in enumerate(zip(control_rows, roots, strict=True)):
        _exact_keys(control_row, EXPECTED_CONTROL_ROW_KEYS, label=f"mesh {cells} control row {index}")
        budget_jets = _exact_keys(
            control_row["budget_control_jets"],
            EXPECTED_BUDGET_CONTROL_KEYS,
            label=f"mesh {cells} budget jets {index}",
        )
        _number(control_row["time"], label=f"mesh {cells} control row {index} time")
        _nonnegative_number(
            control_row["direct_vs_tangent_state_relative_l1"],
            label=f"mesh {cells} control row {index} tangent state difference",
        )
        _nonnegative_number(
            control_row["maximum_direct_vs_tangent_time_jet_absolute_difference"],
            label=f"mesh {cells} control row {index} tangent jet difference",
        )
        for key, value in budget_jets.items():
            _number(value, label=f"mesh {cells} control row {index} budget jet {key}")
        if not _close(control_row["time"], root["time"]):
            raise RuntimeError(f"mesh {cells} control/root time mismatch")
        jets = _number_list(
            control_row["time_jets_f_f_t_f_tt_f_ttt"], 4, label=f"mesh {cells} time jets {index}"
        )
        expected_jets = [
            _number(root[key], label=f"mesh {cells} root {key}")
            for key in ("density", "f_t", "f_tt", "f_ttt")
        ]
        difference = max(abs(left - right) for left, right in zip(jets, expected_jets, strict=True))
        if not _close(control_row["maximum_direct_vs_tangent_time_jet_absolute_difference"], difference):
            raise RuntimeError(f"mesh {cells} tangent jet difference does not reconstruct")
        state_differences.append(
            _number(control_row["direct_vs_tangent_state_relative_l1"], label="tangent state difference")
        )
        jet_differences.append(difference)
    maximum_state_difference = max(state_differences)
    maximum_jet_difference = max(jet_differences)
    if not _close(control["maximum_direct_vs_tangent_state_relative_l1"], maximum_state_difference) or not _close(
        control["maximum_direct_vs_tangent_time_jet_absolute_difference"], maximum_jet_difference
    ):
        raise RuntimeError(f"mesh {cells} tangent maxima do not reconstruct")

    event_rules = manifest["event_mass"]
    state_components = [
        _number(scan["minimum_streamed_state_component"], label="minimum streamed state"),
        _number(tail["minimum_final_state_component"], label="minimum final state"),
        *[_number(root["minimum_state_component"], label="minimum root state") for root in roots],
    ]
    reconstructed_gates = {
        "initial_mass": _number(diagnostics["initial_mass_error"], label="initial mass error") <= 1.0e-12,
        "physical_budget": _number(diagnostics["physical_budget_absolute_error"], label="budget error") <= 1.0e-12,
        "weights_positive_unit_sum": _number(diagnostics["minimum_weight"], label="minimum weight") > 0.0
        and _number(diagnostics["weight_sum_error"], label="weight-sum error") <= 2.0e-14,
        "five_alternating_simple_roots": topology == EXPECTED_TOPOLOGY,
        "peak_ratio": peak_ratio >= _number(root_rules["minimum_peak_ratio"], label="peak-ratio floor"),
        "valley_ratios": max(valleys) <= _number(root_rules["maximum_valley_ratio"], label="valley ceiling"),
        "root_residuals": all(
            _number(root["scaled_first_derivative_residual"], label="root residual")
            <= _number(root_rules["maximum_scaled_root_residual"], label="root-residual ceiling")
            for root in roots
        ),
        "curvature_margins": all(
            abs(_number(root["scaled_second_derivative"], label="root curvature"))
            >= _number(root_rules["minimum_absolute_scaled_curvature"], label="curvature floor")
            for root in roots
        ),
        "endpoint_derivative_signs": _number(checkpoint["f_t"], label="positive endpoint derivative") > 0.0
        and _number(scan["derivative_at_scan_stop"], label="negative endpoint derivative") < 0.0
        and _close(checkpoint["time"], root_rules["positive_derivative_time"])
        and _close(scan["time_grid"]["stop"], root_rules["negative_derivative_time"]),
        "sampled_density_positive": _number(
            scan["minimum_sampled_density_from_frozen_start"], label="sampled density minimum"
        )
        > _number(tail_rules["minimum_density"], label="density floor")
        and _number(tail["minimum_checkpoint_density"], label="tail density minimum")
        > _number(tail_rules["minimum_density"], label="density floor"),
        "root_density_positive": min(densities) > 0.0,
        "survival_positive": _number(scan["survival_at_scan_stop"], label="scan survival") > 0.0
        and final_survival > 0.0,
        "state_positivity_tolerance": min(state_components)
        >= -_number(root_rules["maximum_negative_state_tolerance"], label="state tolerance"),
        "survival_monotone_through_final_time": _number(
            scan["maximum_sampled_survival_increase"], label="scan survival increase"
        )
        <= _number(root_rules["maximum_survival_increase"], label="survival ceiling")
        and _number(tail["maximum_checkpoint_survival_increase"], label="tail survival increase")
        <= _number(tail_rules["maximum_survival_increase"], label="tail survival ceiling"),
        "tail_final_state_positivity": _number(tail["minimum_tail_state_component"], label="tail state minimum")
        >= -_number(tail_rules["maximum_negative_state_tolerance"], label="tail state tolerance"),
        "generator_Q_one_equals_minus_B_k0": _number(
            diagnostics["killed_mass_balance_operator_error"], label="generator mass-balance error"
        )
        <= _number(event_rules["maximum_mass_balance_error"], label="mass-balance ceiling"),
        "mass_balance_on_saved_scan": _number(
            scan["maximum_sampled_differential_mass_balance_residual"], label="scan mass-balance residual"
        )
        <= _number(event_rules["maximum_mass_balance_error"], label="mass-balance ceiling"),
        "mass_balance_at_roots": max(
            _number(root["differential_mass_balance_residual"], label="root mass-balance residual")
            for root in roots
        )
        <= _number(event_rules["maximum_mass_balance_error"], label="mass-balance ceiling"),
        "mass_balance_at_final_time": _number(
            event["final_differential_mass_balance_residual"], label="final mass-balance residual"
        )
        <= _number(event_rules["maximum_mass_balance_error"], label="mass-balance ceiling"),
        "mass_balance_on_tail_checkpoints": _number(
            tail["maximum_checkpoint_differential_mass_balance_residual"], label="tail mass-balance residual"
        )
        <= _number(event_rules["maximum_mass_balance_error"], label="mass-balance ceiling"),
        "event_basin_masses": min(masses)
        >= _number(event_rules["minimum_each_basin_mass"], label="basin-mass floor"),
        "event_mass_partition_closure": abs(sum(masses) - total_reaction)
        <= _number(event_rules["maximum_mass_balance_error"], label="mass-balance ceiling"),
        "tangent_state_reproduction": maximum_state_difference
        <= _number(root_rules["maximum_tangent_state_relative_l1"], label="tangent-state ceiling"),
        "tangent_time_jet_reproduction": maximum_jet_difference
        <= _number(root_rules["maximum_tangent_time_jet_absolute_difference"], label="tangent-jet ceiling"),
    }
    if reported_gates != reconstructed_gates:
        raise RuntimeError(f"mesh {cells} reported gate map disagrees with reconstruction")
    if not all(reconstructed_gates.values()) or row["all_mesh_gates_passed"] is not True:
        failed = sorted(key for key, value in reconstructed_gates.items() if not value)
        raise RuntimeError(f"mesh {cells} fails frozen semantic gates: {failed}")

    return {
        "cells": cells,
        "times": times,
        "peak_ratio": peak_ratio,
        "valleys": valleys,
        "masses": masses,
        "final_survival": final_survival,
        "gates": reconstructed_gates,
        "final_time": final_time,
    }


def verify_sources(
    *,
    report: Path = REPORT,
    expected_manifest_sha256: str = EXPECTED_MANIFEST_SHA256,
    expected_result_sha256: str = EXPECTED_RESULT_SHA256,
    expected_evidence_sha256: str = EXPECTED_EVIDENCE_SHA256,
    expected_audit_sha256: str = EXPECTED_AUDIT_SHA256,
) -> dict[str, Any]:
    report = report.resolve(strict=True)
    data = report / "artifacts" / "data"
    paths = {
        "manifest": data / MANIFEST_NAME,
        "result": data / RESULT_NAME,
        "evidence": data / EVIDENCE_NAME,
        "audit": data / AUDIT_NAME,
    }
    expected_hashes = {
        "manifest": expected_manifest_sha256,
        "result": expected_result_sha256,
        "evidence": expected_evidence_sha256,
        "audit": expected_audit_sha256,
    }
    snapshots = {
        label: _snapshot_regular_file(path, root=report, label=label)
        for label, path in paths.items()
    }
    auditor_snapshot = _snapshot_report_path(
        report,
        "code/audit_positive_b_broad_four_slab_result.py",
        label="positive-B independent auditor source",
    )
    _require_snapshot_hash(
        auditor_snapshot,
        EXPECTED_AUDITOR_SHA256,
        label="positive-B independent auditor source",
    )
    for label, snapshot in snapshots.items():
        _require_snapshot_hash(snapshot, expected_hashes[label], label=label)
    manifest = load_object_from_bytes(
        snapshots["manifest"].payload,
        label=MANIFEST_NAME,
        require_canonical=False,
    )
    result = load_object_from_bytes(
        snapshots["result"].payload,
        label=RESULT_NAME,
        require_canonical=True,
    )
    evidence = load_object_from_bytes(
        snapshots["evidence"].payload,
        label=EVIDENCE_NAME,
        require_canonical=True,
    )
    audit = load_object_from_bytes(
        snapshots["audit"].payload,
        label=AUDIT_NAME,
        require_canonical=True,
    )
    _require_no_temporary_metadata(audit, label="positive-B independent audit")

    _exact_keys(manifest, EXPECTED_MANIFEST_KEYS, label="positive-B manifest")
    if (
        type(manifest["schema_version"]) is not int
        or manifest["schema_version"] != 1
        or manifest["stage"] != EXPECTED_STAGE
        or manifest["freeze_date"] != "2026-07-13"
        or manifest["evidence_timing"] != EXPECTED_EVIDENCE_TIMING
        or manifest["claim_scope"] != EXPECTED_CLAIM_SCOPE
        or not _exact_json_equal(manifest["heldout_meshes"], [113, 129])
        or not _exact_json_equal(manifest["positive_budget"], 0.01)
        or not _exact_json_equal(manifest["required_claim_flags"], EXPECTED_NEGATIVE_FLAGS)
        or not _exact_json_equal(
            manifest["known_before_freeze"], EXPECTED_KNOWN_BEFORE_FREEZE
        )
        or not _exact_json_equal(
            manifest["numerical_reproducibility"], EXPECTED_NUMERICAL_REPRODUCIBILITY
        )
        or not _exact_json_equal(
            manifest["execution_boundary"], EXPECTED_EXECUTION_BOUNDARY
        )
        or not _exact_json_equal(
            manifest["preflight_validation"], EXPECTED_PREFLIGHT_VALIDATION
        )
        or not _exact_json_equal(
            manifest["forbidden_promotions"], EXPECTED_FORBIDDEN_PROMOTIONS
        )
    ):
        raise RuntimeError("positive-B manifest identity or claim boundary changed")
    _exact_keys(
        manifest["physical_parameters"],
        {
            "particle_diffusion",
            "ou_stiffness",
            "ou_mean",
            "transverse_width",
            "contact_radius",
            "midpoint_start",
            "initial_half_width",
            "relative_parallel_start",
            "relative_perp_start",
            "patch_centres",
            "patch_half_width",
            "fixed_first_weight",
        },
        label="manifest physical parameters",
    )
    if not _exact_json_equal(manifest["physical_parameters"], EXPECTED_PHYSICAL_PARAMETERS):
        raise RuntimeError("manifest physical parameters changed")
    weights = _number_list(manifest["fixed_absolute_weights"], 4, label="manifest weights")
    if (
        not _exact_json_equal(manifest["fixed_absolute_weights"], EXPECTED_FIXED_WEIGHTS)
        or min(weights) <= 0.0
        or not _close(sum(weights), 1.0)
    ):
        raise RuntimeError("manifest weights are not a positive unit-sum control")
    selection = _exact_keys(
        manifest["selection_record"],
        {
            "selected_budget",
            "eligible_budgets_on_mesh_97",
            "rule",
            "weights_or_geometry_refit_for_positive_B",
            "other_budget_forbidden_on_heldout_meshes",
        },
        label="manifest selection record",
    )
    expected_selection = {
        "selected_budget": 0.01,
        "eligible_budgets_on_mesh_97": [0.01, 0.02],
        "rule": [
            "five alternating roots",
            "all three event-basin masses at least 0.005",
            "differential mass balance",
            "minimum worst valley excess on mesh 97",
            "smaller budget tie-break",
        ],
        "weights_or_geometry_refit_for_positive_B": False,
        "other_budget_forbidden_on_heldout_meshes": True,
    }
    if not _exact_json_equal(selection, expected_selection):
        raise RuntimeError("manifest selected-budget/fixed-control contract changed")
    _exact_keys(
        manifest["finite_volume"],
        {"midpoint_bounds", "relative_parallel_bounds", "scheme"},
        label="manifest finite-volume contract",
    )
    if not _exact_json_equal(manifest["finite_volume"], EXPECTED_FINITE_VOLUME):
        raise RuntimeError("manifest finite-volume contract changed")
    _exact_keys(
        manifest["root_gates"],
        {
            "relative_density_floor",
            "minimum_peak_ratio",
            "maximum_valley_ratio",
            "maximum_scaled_root_residual",
            "minimum_absolute_scaled_curvature",
            "positive_derivative_time",
            "negative_derivative_time",
            "maximum_negative_state_tolerance",
            "maximum_survival_increase",
            "maximum_tangent_state_relative_l1",
            "maximum_tangent_time_jet_absolute_difference",
        },
        label="manifest root gates",
    )
    if not _exact_json_equal(manifest["root_gates"], EXPECTED_ROOT_GATES):
        raise RuntimeError("manifest root-gate thresholds changed")
    _exact_keys(
        manifest["tail_gates"],
        {
            "checkpoints",
            "minimum_density_sampling_start",
            "minimum_density",
            "maximum_survival_increase",
            "maximum_negative_state_tolerance",
        },
        label="manifest tail gates",
    )
    if not _exact_json_equal(manifest["tail_gates"], EXPECTED_TAIL_GATES):
        raise RuntimeError("manifest tail-gate thresholds changed")
    _exact_keys(
        manifest["event_mass"],
        {"final_time", "minimum_each_basin_mass", "maximum_mass_balance_error"},
        label="manifest event-mass gates",
    )
    if not _exact_json_equal(manifest["event_mass"], EXPECTED_EVENT_MASS):
        raise RuntimeError("manifest event-mass thresholds changed")
    _exact_keys(
        manifest["mesh_agreement"],
        {
            "maximum_paired_root_time_difference",
            "maximum_peak_ratio_difference",
            "maximum_valley_ratio_difference",
            "maximum_event_mass_difference",
            "maximum_final_survival_difference",
        },
        label="manifest mesh-agreement gates",
    )
    if not _exact_json_equal(manifest["mesh_agreement"], EXPECTED_MESH_AGREEMENT):
        raise RuntimeError("manifest mesh-agreement thresholds changed")
    _exact_keys(
        manifest["time_scan"], set(EXPECTED_TIME_SCAN), label="manifest time-scan contract"
    )
    if not _exact_json_equal(manifest["time_scan"], EXPECTED_TIME_SCAN):
        raise RuntimeError("manifest time-scan contract changed")
    if (
        not _close(manifest["time_scan"]["stop"], 35.0)
        or not _close(manifest["event_mass"]["final_time"], 100.0)
        or manifest["tail_gates"]["checkpoints"] != [35.0, 50.0, 75.0, 100.0]
    ):
        raise RuntimeError("positive-B root-screen or event-mass time boundary changed")

    pins = manifest.get("pinned_files")
    result_pins = result.get("pinned_file_hashes")
    if (
        type(pins) is not dict
        or set(pins) != EXPECTED_PIN_ROLES
        or type(result_pins) is not dict
        or set(result_pins) != EXPECTED_PIN_ROLES
    ):
        raise RuntimeError("positive-B manifest/result pin set is incomplete")
    for role, pin in pins.items():
        if type(pin) is not dict or set(pin) != {"path", "sha256"}:
            raise RuntimeError(f"positive-B pin {role} is malformed")
        digest = pin["sha256"]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise RuntimeError(f"positive-B pin {role} has an invalid SHA-256")
        snapshot = _snapshot_report_path(report, pin["path"], label=f"pin {role}")
        _require_snapshot_hash(snapshot, digest, label=f"pin {role}")
        if result_pins.get(role) != digest:
            raise RuntimeError(f"result pin {role} does not match the frozen manifest")

    _exact_keys(result, EXPECTED_RESULT_KEYS, label="positive-B result")
    _require_no_temporary_metadata(result, label="positive-B result")
    _require_authorized_claim_keys(result)
    if (
        type(result.get("schema_version")) is not int
        or result.get("schema_version") != 1
        or result.get("stage") != EXPECTED_STAGE
        or result.get("status") != RESULT_STATUS
        or result.get("evidence_timing") != EXPECTED_EVIDENCE_TIMING
        or result.get("claim_scope") != EXPECTED_CLAIM_SCOPE
        or result.get("manifest_sha256") != expected_manifest_sha256
        or not _exact_json_equal(result.get("positive_budget"), 0.01)
        or not _exact_json_equal(
            result.get("physical_parameters"), manifest["physical_parameters"]
        )
        or not _exact_json_equal(
            result.get("fixed_absolute_weights"), manifest["fixed_absolute_weights"]
        )
        or result.get("weights_refit") is not False
        or result.get("positive_B_event_mass_shape_confirmation") is not True
        or not _exact_json_equal(
            result.get("required_claim_flags"), EXPECTED_NEGATIVE_FLAGS
        )
        or any(result.get(key) is not False for key in EXPECTED_NEGATIVE_FLAGS)
        or not _exact_json_equal(result.get("limitations"), EXPECTED_LIMITATIONS)
    ):
        raise RuntimeError("positive-B result status or claim boundary changed")
    if not _exact_json_equal(
        result.get("numerical_reproducibility"), EXPECTED_NUMERICAL_REPRODUCIBILITY
    ):
        raise RuntimeError("positive-B numerical-reproducibility contract changed")
    if not _exact_json_equal(
        result.get("reproducibility_evidence"),
        {
        "canonical_result_requires_external_byte_comparison": True,
        "file": "artifacts/data/positive_b_broad_four_slab_reproducibility.json",
        "independent_full_processes_required": 2,
        },
    ):
        raise RuntimeError("positive-B result reproducibility-evidence contract changed")
    software = _exact_keys(
        result.get("software"), {"python", "numpy", "scipy"}, label="positive-B software"
    )
    if any(type(value) is not str or not value for value in software.values()):
        raise RuntimeError("positive-B software versions must be nonempty strings")

    rows = result.get("heldout_mesh_rows")
    if type(rows) is not list or len(rows) != 2:
        raise RuntimeError("positive-B result must contain exactly two mesh rows")
    reconstructed = [
        _validate_mesh_row(row, cells, manifest)
        for row, cells in zip(rows, (113, 129), strict=True)
    ]
    first, second = reconstructed
    metrics = {
        "maximum_paired_root_time_difference": max(
            abs(left - right) for left, right in zip(first["times"], second["times"], strict=True)
        ),
        "peak_ratio_absolute_difference": abs(first["peak_ratio"] - second["peak_ratio"]),
        "maximum_valley_ratio_absolute_difference": max(
            abs(left - right)
            for left, right in zip(first["valleys"], second["valleys"], strict=True)
        ),
        "maximum_event_mass_absolute_difference": max(
            abs(left - right) for left, right in zip(first["masses"], second["masses"], strict=True)
        ),
        "final_survival_absolute_difference": abs(
            first["final_survival"] - second["final_survival"]
        ),
    }
    agreement = result.get("mesh_agreement")
    _exact_keys(agreement, EXPECTED_AGREEMENT_KEYS, label="positive-B mesh agreement")
    for key, value in metrics.items():
        reported = _nonnegative_number(
            agreement.get(key), label=f"positive-B mesh agreement {key}"
        )
        if not _close(value, reported):
            raise RuntimeError(f"positive-B mesh agreement {key} does not reconstruct")
    thresholds = manifest["mesh_agreement"]
    agreement_gates = {
        "paired_root_times": metrics["maximum_paired_root_time_difference"]
        <= _number(thresholds["maximum_paired_root_time_difference"], label="paired-root ceiling"),
        "peak_ratio": metrics["peak_ratio_absolute_difference"]
        <= _number(thresholds["maximum_peak_ratio_difference"], label="peak-ratio agreement ceiling"),
        "valley_ratios": metrics["maximum_valley_ratio_absolute_difference"]
        <= _number(thresholds["maximum_valley_ratio_difference"], label="valley agreement ceiling"),
        "event_basin_masses": metrics["maximum_event_mass_absolute_difference"]
        <= _number(thresholds["maximum_event_mass_difference"], label="event-mass agreement ceiling"),
        "final_survival": metrics["final_survival_absolute_difference"]
        <= _number(thresholds["maximum_final_survival_difference"], label="survival agreement ceiling"),
    }
    _exact_keys(
        agreement["gates"], EXPECTED_AGREEMENT_GATE_KEYS, label="positive-B agreement gate map"
    )
    if any(type(value) is not bool for value in agreement["gates"].values()):
        raise RuntimeError("positive-B agreement gate map contains a non-Boolean value")
    if type(agreement["all_agreement_gates_passed"]) is not bool:
        raise RuntimeError("positive-B agreement aggregate must be Boolean")
    if not _exact_json_equal(
        agreement["mesh_pair"], [[113, 113, 113], [129, 129, 129]]
    ):
        raise RuntimeError("positive-B mesh pair changed")
    if agreement["gates"] != agreement_gates:
        raise RuntimeError("positive-B agreement gates disagree with reconstructed metrics")
    if not all(agreement_gates.values()) or agreement["all_agreement_gates_passed"] is not True:
        failed = sorted(key for key, value in agreement_gates.items() if not value)
        raise RuntimeError(f"positive-B mesh agreement fails frozen ceilings: {failed}")
    if (
        type(result.get("all_gates_passed")) is not bool
        or result.get("all_gates_passed") is not True
    ):
        raise RuntimeError("positive-B aggregate result gate is not passing")

    _require_no_temporary_metadata(evidence, label="positive-B reproducibility evidence")
    expected_evidence = {
        "schema_version": 1,
        "stage": "positive_B_broad_four_slab_two_process_reproducibility",
        "manifest_sha256": expected_manifest_sha256,
        "independent_process_count": 2,
        "execution_order": "sequential",
        "replica_exit_codes": [0, 0],
        "replica_result_sha256": [expected_result_sha256, expected_result_sha256],
        "byte_identical": True,
        "canonical_promotion_after_comparison": True,
        "canonical_result_sha256": expected_result_sha256,
        "result_status": RESULT_STATUS,
        "all_gates_passed": True,
    }
    if not _exact_json_equal(evidence, expected_evidence):
        raise RuntimeError("positive-B two-process evidence contract changed")

    boundary = audit.get("claim_boundary")
    required_boundary = {
        "allocation_cusp_verified": False,
        "continuum_interval_verified": False,
        "fixed_box_two_mesh_semidiscrete_point_only": True,
        "independent_process_execution_observed_by_auditor": False,
        "independent_solver_verified": False,
        "preregistered_discovery": False,
        "project_gate_passed": False,
        "two_process_evidence_record_consistent": True,
        "unbounded_domain_FV_limit_verified": False,
    }
    required_independence_boundary = {
        "independently_algebraically_reconstructed": [
            "root scaled residuals and curvatures",
            "conditional peak and valley ratios",
            "conditional event-basin masses and closure",
            "tangent-row time-jet differences and summary maxima",
            "tail checkpoint summaries",
            "two-mesh nullable agreement metrics and gates",
        ],
        "re_evaluated_from_producer_reported_certified_extrema": [
            "full-scan minimum density",
            "full-scan minimum state component",
            "full-scan maximum adjacent survival increase",
            "full-scan maximum differential mass-balance residual",
            "generator mass-balance identity residual",
            "root minimum-state components and mass-balance residuals",
            "direct-versus-tangent state-norm residuals",
            "finite-volume factor quadrature and row-sum diagnostics",
        ],
    }
    _exact_keys(
        audit,
        {
            "schema_version",
            "stage",
            "status",
            "scientific_result_passed",
            "manifest_sha256",
            "canonical_result_sha256",
            "reproducibility_evidence_sha256",
            "auditor_sha256",
            "mesh_reconstructions",
            "agreement_reconstruction",
            "claim_boundary",
            "independence_boundary",
        },
        label="positive-B independent audit",
    )
    audit_agreement = _exact_keys(
        audit["agreement_reconstruction"],
        {"metrics", "gates", "all_agreement_gates_passed"},
        label="audit agreement reconstruction",
    )
    audit_metrics = _exact_keys(
        audit_agreement["metrics"], set(metrics), label="audit agreement metrics"
    )
    for key in metrics:
        _nonnegative_number(audit_metrics.get(key), label=f"audit agreement metric {key}")
    audit_agreement_gates = _exact_keys(
        audit_agreement["gates"],
        EXPECTED_AGREEMENT_GATE_KEYS,
        label="audit agreement gates",
    )
    if any(type(value) is not bool for value in audit_agreement_gates.values()):
        raise RuntimeError("audit agreement gate map contains a non-Boolean value")
    if type(audit_agreement["all_agreement_gates_passed"]) is not bool:
        raise RuntimeError("audit agreement aggregate must be Boolean")
    if (
        type(audit.get("schema_version")) is not int
        or audit.get("schema_version") != 1
        or audit.get("stage") != "independent_positive_B_result_reconstruction"
        or audit.get("status") != "PASS_INDEPENDENT_RECONSTRUCTION"
        or audit.get("scientific_result_passed") is not True
        or audit.get("manifest_sha256") != expected_manifest_sha256
        or audit.get("canonical_result_sha256") != expected_result_sha256
        or audit.get("reproducibility_evidence_sha256") != expected_evidence_sha256
        or audit.get("auditor_sha256") != EXPECTED_AUDITOR_SHA256
        or audit.get("auditor_sha256") != auditor_snapshot.sha256
        or not _exact_json_equal(boundary, required_boundary)
        or not _exact_json_equal(
            audit.get("independence_boundary"), required_independence_boundary
        )
        or any(not _close(audit_metrics.get(key), value) for key, value in metrics.items())
        or not _exact_json_equal(audit_agreement_gates, agreement_gates)
        or audit_agreement["all_agreement_gates_passed"] is not True
    ):
        raise RuntimeError("positive-B independent-audit contract changed")
    audit_meshes = audit.get("mesh_reconstructions")
    if type(audit_meshes) is not list or len(audit_meshes) != 2:
        raise RuntimeError("positive-B audit mesh reconstruction set changed")
    audit_mesh_keys = {
        "mesh",
        "root_times",
        "peak_ratio",
        "valley_ratios",
        "basin_masses",
        "final_survival",
        "expected_five_root_topology",
        "independently_algebraically_reconstructed_gates",
        "producer_reported_full_scan_extrema_used",
        "all_reported_mesh_gates_passed",
    }
    for summary, audited in zip(reconstructed, audit_meshes, strict=True):
        _exact_keys(audited, audit_mesh_keys, label=f"audit mesh {summary['cells']}")
        if type(audited["mesh"]) is not int:
            raise RuntimeError(f"audit mesh {summary['cells']} identity must be an integer")
        audited_gates = _exact_keys(
            audited["independently_algebraically_reconstructed_gates"],
            EXPECTED_GATE_KEYS,
            label=f"audit mesh {summary['cells']} gates",
        )
        if any(type(value) is not bool for value in audited_gates.values()):
            raise RuntimeError(f"audit mesh {summary['cells']} has non-Boolean gates")
        if type(audited["all_reported_mesh_gates_passed"]) is not bool:
            raise RuntimeError(f"audit mesh {summary['cells']} aggregate must be Boolean")
        if (
            audited["mesh"] != summary["cells"]
            or not _close_list(summary["times"], audited["root_times"])
            or not _close(summary["peak_ratio"], audited["peak_ratio"])
            or not _close_list(summary["valleys"], audited["valley_ratios"])
            or not _close_list(summary["masses"], audited["basin_masses"])
            or not _close(summary["final_survival"], audited["final_survival"])
            or audited["expected_five_root_topology"] is not True
            or not _exact_json_equal(audited_gates, summary["gates"])
            or not _exact_json_equal(
                audited["producer_reported_full_scan_extrema_used"], EXPECTED_AUDIT_EXTREMA
            )
            or audited["all_reported_mesh_gates_passed"] is not True
        ):
            raise RuntimeError(f"audit mesh {summary['cells']} disagrees with canonical result")

    return {
        "paths": paths,
        "hashes": expected_hashes,
        "manifest": manifest,
        "result": result,
        "meshes": reconstructed,
        "metrics": metrics,
        "auditor_sha256": auditor_snapshot.sha256,
    }


def macro(name: str, value: str) -> str:
    return rf"\providecommand{{\{name}}}{{{value}}}"


def tex_sci(value: float, digits: int = 2) -> str:
    mantissa, exponent = f"{value:.{digits}e}".split("e")
    return rf"{mantissa}\times10^{{{int(exponent)}}}"


def render_verified_macros(verified: dict[str, Any]) -> str:
    """Render only from the already verified same-byte snapshot objects."""

    result = verified["result"]
    manifest = verified["manifest"]
    first, second = verified["meshes"]
    metrics = verified["metrics"]
    weights = [float(value) for value in result["fixed_absolute_weights"]]
    all_masses = [*first["masses"], *second["masses"]]
    all_valleys = [*first["valleys"], *second["valleys"]]
    values = [
        macro("PositiveBBudget", f"{float(result['positive_budget']):.2f}"),
        macro("PositiveBWeights", ",".join(f"{value:.8f}" for value in weights)),
        macro("PositiveBMeshOne", str(first["cells"])),
        macro("PositiveBMeshTwo", str(second["cells"])),
        macro("PositiveBRootTimesOne", ",".join(f"{value:.5f}" for value in first["times"])),
        macro("PositiveBRootTimesTwo", ",".join(f"{value:.5f}" for value in second["times"])),
        macro("PositiveBPeakRatioOne", f"{first['peak_ratio']:.5f}"),
        macro("PositiveBPeakRatioTwo", f"{second['peak_ratio']:.5f}"),
        macro(
            "PositiveBPeakRatioRange",
            f"{min(first['peak_ratio'], second['peak_ratio']):.5f}\\text{{--}}"
            f"{max(first['peak_ratio'], second['peak_ratio']):.5f}",
        ),
        macro("PositiveBValleyRatiosOne", ",".join(f"{value:.5f}" for value in first["valleys"])),
        macro("PositiveBValleyRatiosTwo", ",".join(f"{value:.5f}" for value in second["valleys"])),
        macro("PositiveBBasinMassesOne", ",".join(f"{value:.8f}" for value in first["masses"])),
        macro("PositiveBBasinMassesTwo", ",".join(f"{value:.8f}" for value in second["masses"])),
        *[
            macro(
                f"PositiveBBasin{label}Range",
                f"{min(first['masses'][index], second['masses'][index]):.8f}\\text{{--}}"
                f"{max(first['masses'][index], second['masses'][index]):.8f}",
            )
            for index, label in enumerate(("One", "Two", "Three"))
        ],
        *[
            macro(
                f"PositiveBValley{label}Range",
                f"{min(first['valleys'][index], second['valleys'][index]):.5f}\\text{{--}}"
                f"{max(first['valleys'][index], second['valleys'][index]):.5f}",
            )
            for index, label in enumerate(("One", "Two"))
        ],
        macro("PositiveBFinalSurvivalOne", f"{first['final_survival']:.8f}"),
        macro("PositiveBFinalSurvivalTwo", f"{second['final_survival']:.8f}"),
        macro(
            "PositiveBFinalSurvivalRange",
            f"{min(first['final_survival'], second['final_survival']):.8f}\\text{{--}}"
            f"{max(first['final_survival'], second['final_survival']):.8f}",
        ),
        macro("PositiveBMinimumBasinMass", f"{min(all_masses):.8f}"),
        macro("PositiveBWorstValleyRatio", f"{max(all_valleys):.5f}"),
        macro(
            "PositiveBMaximumRootDifference",
            f"{metrics['maximum_paired_root_time_difference']:.5f}",
        ),
        macro(
            "PositiveBMaximumMassDifference",
            tex_sci(metrics["maximum_event_mass_absolute_difference"]),
        ),
        macro(
            "PositiveBFinalSurvivalDifference",
            tex_sci(metrics["final_survival_absolute_difference"]),
        ),
        macro("PositiveBFinalTime", f"{float(manifest['event_mass']['final_time']):g}"),
    ]
    header = [
        "% Generated by code/build_positive_b_manuscript_input.py; do not edit.",
        f"% manifest SHA-256: {verified['hashes']['manifest']}",
        f"% canonical result SHA-256: {verified['hashes']['result']}",
        f"% two-process evidence SHA-256: {verified['hashes']['evidence']}",
        f"% independent audit SHA-256: {verified['hashes']['audit']}",
        "% Scope: fixed box, same FV solver family, two odd meshes, finite window.",
        "% Forbidden: allocation cusp, continuum/unbounded, independent solver, PRR pass.",
    ]
    return "\n".join([*header, *values, ""])


def render_macros(**verify_kwargs: Any) -> str:
    return render_verified_macros(verify_sources(**verify_kwargs))


def write_atomic(output: Path, text: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    rendered = render_macros()
    write_atomic(args.output, rendered)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
