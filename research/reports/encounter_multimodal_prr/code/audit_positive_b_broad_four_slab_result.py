#!/usr/bin/env python3
"""Independent, fail-closed audit of the frozen positive-B confirmation output.

This module deliberately does not import the numerical producer.  It checks the
canonical result and two-process evidence against the externally frozen
manifest, and independently reconstructs every claim-bearing scalar that can
be recovered from the published result JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "positive_b_broad_four_slab_manifest.json"
RESULT = DATA / "positive_b_broad_four_slab_result.json"
REPRODUCIBILITY = DATA / "positive_b_broad_four_slab_reproducibility.json"
AUDIT_OUTPUT = DATA / "positive_b_broad_four_slab_independent_audit.json"

EXPECTED_MANIFEST_SHA256 = "955e59bf333b5fd70e415a53dc26becae9c7a34c5d40f1230c96b1dab8f5677c"
EXPECTED_STAGE = "result_informed_positive_B_broad_four_slab_heldout_mesh_confirmation"
EXPECTED_TOPOLOGY = ["maximum", "minimum", "maximum", "minimum", "maximum"]
EXPECTED_NEGATIVE_FLAGS = {
    "preregistered_discovery": False,
    "continuum_interval_verified": False,
    "unbounded_domain_FV_limit_verified": False,
    "independent_solver_verified": False,
    "project_gate_passed": False,
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
EXPECTED_AGREEMENT_GATE_KEYS = {
    "paired_root_times",
    "peak_ratio",
    "valley_ratios",
    "event_basin_masses",
    "final_survival",
}
EXPECTED_EVIDENCE_KEYS = {
    "schema_version",
    "stage",
    "manifest_sha256",
    "independent_process_count",
    "execution_order",
    "replica_exit_codes",
    "replica_result_sha256",
    "byte_identical",
    "canonical_result_sha256",
    "canonical_promotion_after_comparison",
    "result_status",
    "all_gates_passed",
}
EXPECTED_LIMITATIONS = [
    "result-informed fixed control and selected budget",
    "two fixed-box finite-volume meshes, not a PDE or unbounded-domain proof",
    "same solver family on both meshes, not independent-solver verification",
    "floating-point sign-screen and root refinement, not interval certification",
    "no physical d=3 or project/publication gate",
]
FORBIDDEN_METADATA_KEYS = {
    "elapsed_seconds",
    "timestamp",
    "temporary_path",
    "temp_path",
    "output_path",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def lexical_absolute(path: Path) -> Path:
    """Return an absolute lexical path without resolving symbolic links."""
    return Path(os.path.abspath(os.fspath(path)))


def require_regular_nonsymlink_file(path: Path, label: str) -> Path:
    """Fail closed unless *path itself* names one ordinary, non-link file."""
    lexical = lexical_absolute(path)
    try:
        mode = lexical.lstat().st_mode
    except OSError as error:
        raise ValueError(f"{label} is not an accessible regular file") from error
    require(
        stat.S_ISREG(mode) and not stat.S_ISLNK(mode),
        f"{label} must be a non-symlink regular file",
    )
    return lexical


def require_finite_json(value: Any, location: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"non-finite JSON number at {location}")
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


def canonical_bytes(value: dict[str, Any]) -> bytes:
    require_finite_json(value)
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def load_canonical_object_with_bytes(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = Path(path).read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if type(value) is not dict:
        raise TypeError(f"{path} must contain one JSON object")
    if canonical_bytes(value) != raw:
        raise ValueError(f"{path} is not canonical JSON")
    return value, raw


def load_canonical_object(path: Path) -> dict[str, Any]:
    return load_canonical_object_with_bytes(path)[0]


def load_object_from_bytes(raw: bytes, path: Path) -> dict[str, Any]:
    value = json.loads(raw.decode("utf-8"))
    if type(value) is not dict:
        raise TypeError(f"{path} must contain one JSON object")
    require_finite_json(value)
    return value


def load_object(path: Path) -> dict[str, Any]:
    return load_object_from_bytes(Path(path).read_bytes(), Path(path))


def close(left: float, right: float, *, scale: float = 1.0) -> bool:
    return abs(float(left) - float(right)) <= 2.0e-12 * max(
        float(scale), abs(float(left)), abs(float(right))
    )


def same_float(left: Any, right: Any) -> bool:
    if type(left) not in (int, float) or type(left) is bool:
        return False
    if type(right) not in (int, float) or type(right) is bool:
        return False
    return math.isclose(float(left), float(right), rel_tol=5.0e-13, abs_tol=5.0e-15)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def require_float(value: Any, label: str) -> float:
    require(type(value) is float and math.isfinite(value), f"{label} must be a finite float")
    return value


def require_nonnegative_float(value: Any, label: str) -> float:
    result = require_float(value, label)
    require(result >= 0.0, f"{label} must be nonnegative")
    return result


def require_unit_interval_float(value: Any, label: str, tolerance: float = 0.0) -> float:
    result = require_float(value, label)
    require(
        -tolerance <= result <= 1.0 + tolerance,
        f"{label} must lie in the unit interval",
    )
    return result


def require_int(value: Any, label: str) -> int:
    require(type(value) is int and type(value) is not bool, f"{label} must be an integer")
    return value


def require_mesh_triplet(value: Any, cells: int, label: str) -> None:
    require(
        type(value) is list
        and len(value) == 3
        and all(type(item) is int and type(item) is not bool and item == cells for item in value),
        f"{label} must be the exact integer mesh triplet [{cells}, {cells}, {cells}]",
    )


def require_exact_keys(value: Any, expected: set[str], message: str) -> dict[str, Any]:
    require(type(value) is dict and set(value) == expected, message)
    return value


def exact_json_equal(observed: Any, expected: Any) -> bool:
    """Compare JSON contracts without Python's bool/int or int/float aliases."""
    if type(observed) is not type(expected):
        return False
    if type(expected) is dict:
        return set(observed) == set(expected) and all(
            exact_json_equal(observed[key], expected[key]) for key in expected
        )
    if type(expected) is list:
        return len(observed) == len(expected) and all(
            exact_json_equal(left, right) for left, right in zip(observed, expected, strict=True)
        )
    return observed == expected


def recursive_keys(value: Any) -> set[str]:
    if type(value) is dict:
        return set(value).union(*(recursive_keys(item) for item in value.values()))
    if type(value) is list:
        return set().union(*(recursive_keys(item) for item in value))
    return set()


def recursive_key_paths(value: Any, prefix: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    paths: list[tuple[Any, ...]] = []
    if type(value) is dict:
        for key, item in value.items():
            path = (*prefix, key)
            paths.append(path)
            paths.extend(recursive_key_paths(item, path))
    elif type(value) is list:
        for index, item in enumerate(value):
            paths.extend(recursive_key_paths(item, (*prefix, index)))
    return paths


def require_authorized_claim_key_locations(result: dict[str, Any]) -> None:
    authorized = {key: {(key,), ("required_claim_flags", key)} for key in EXPECTED_NEGATIVE_FLAGS}
    authorized["positive_B_event_mass_shape_confirmation"] = {
        ("positive_B_event_mass_shape_confirmation",)
    }
    authorized["allocation_cusp_verified"] = set()
    authorized["physical_d3_verified"] = set()
    authorized["continuum_verified"] = set()
    authorized["publication_gate_passed"] = set()
    paths = recursive_key_paths(result)
    for key, allowed_paths in authorized.items():
        observed = {path for path in paths if path[-1] == key}
        require(observed == allowed_paths, f"claim key {key} appears at an unauthorized location")


def require_no_temporary_metadata(value: dict[str, Any], label: str) -> None:
    require(recursive_keys(value).isdisjoint(FORBIDDEN_METADATA_KEYS), f"{label} has metadata")

    def strings(item: Any) -> list[str]:
        if type(item) is str:
            return [item]
        if type(item) is dict:
            return [text for child in item.values() for text in strings(child)]
        if type(item) is list:
            return [text for child in item for text in strings(child)]
        return []

    forbidden = (".replica_", ".staging", ".backup")
    require(
        not any(token in text for text in strings(value) for token in forbidden),
        f"{label} exposes temporary paths",
    )


def validate_manifest(manifest_path: Path, report: Path) -> dict[str, Any]:
    manifest_file = require_regular_nonsymlink_file(manifest_path, "manifest")
    raw = manifest_file.read_bytes()
    require(sha256_bytes(raw) == EXPECTED_MANIFEST_SHA256, "manifest hash changed")
    # The externally hash-pinned manifest predates the canonical sorted-key
    # result format.  Its exact bytes are protected by the SHA-256 anchor.
    manifest = load_object_from_bytes(raw, Path(manifest_path))
    require(manifest.get("schema_version") == 1, "manifest schema changed")
    require(manifest.get("stage") == EXPECTED_STAGE, "manifest stage changed")
    require(manifest.get("heldout_meshes") == [113, 129], "held-out meshes changed")
    require(manifest.get("positive_budget") == 0.01, "positive budget changed")
    require(
        exact_json_equal(manifest.get("required_claim_flags"), EXPECTED_NEGATIVE_FLAGS),
        "manifest claim flags are not fail-closed",
    )
    pins = manifest.get("pinned_files")
    require(type(pins) is dict and bool(pins), "manifest pins are absent")
    root = report.resolve()
    for role, pin in pins.items():
        require(type(pin) is dict and set(pin) == {"path", "sha256"}, f"bad pin {role}")
        relative = Path(pin["path"])
        require(not relative.is_absolute() and ".." not in relative.parts, f"bad path {role}")
        candidate = require_regular_nonsymlink_file(root / relative, f"pinned input {role}")
        resolved = candidate.resolve()
        require(resolved.is_relative_to(root) and resolved.is_file(), f"missing pin {role}")
        require(
            sha256_bytes(resolved.read_bytes()) == pin["sha256"], f"pin hash mismatch for {role}"
        )
    return manifest


def reconstruct_row(row: dict[str, Any], cells: int, manifest: dict[str, Any]) -> dict[str, Any]:
    require_exact_keys(row, EXPECTED_RESULT_ROW_KEYS, f"mesh {cells} row schema changed")
    require_mesh_triplet(row["mesh"], cells, f"mesh {cells} row.mesh")
    diagnostics = require_exact_keys(
        row["diagnostics"], EXPECTED_DIAGNOSTIC_KEYS, f"mesh {cells} diagnostics schema"
    )
    scan = require_exact_keys(row["scan"], EXPECTED_SCAN_KEYS, f"mesh {cells} scan schema")
    structure = require_exact_keys(
        row["stationary_structure"],
        EXPECTED_STRUCTURE_KEYS,
        f"mesh {cells} stationary schema",
    )
    mass = require_exact_keys(
        row["survival_and_event_mass"], EXPECTED_MASS_KEYS, f"mesh {cells} mass schema"
    )
    tail = require_exact_keys(
        row["tail_35_to_100"], EXPECTED_TAIL_KEYS, f"mesh {cells} tail schema"
    )
    control = require_exact_keys(
        row["time_and_budget_control_jets"],
        EXPECTED_CONTROL_KEYS,
        f"mesh {cells} control schema",
    )
    gates = require_exact_keys(row["gates"], EXPECTED_GATE_KEYS, f"mesh {cells} gate schema")
    require(all(type(value) is bool for value in gates.values()), f"mesh {cells} non-Boolean gate")
    require(type(row["all_mesh_gates_passed"]) is bool, f"mesh {cells} aggregate type")
    survival_tolerance = float(manifest["root_gates"]["maximum_negative_state_tolerance"])

    def require_survival(value: float, label: str) -> None:
        require(
            -survival_tolerance <= value <= 1.0 + survival_tolerance,
            f"mesh {cells} {label} lies outside the probability range",
        )

    require_int(structure["stationary_root_count"], f"mesh {cells} stationary root count")
    require(type(structure["topology"]) is list, f"mesh {cells} topology type")
    for key in EXPECTED_TAIL_KEYS - {"checkpoints", "trace"}:
        require_float(tail[key], f"mesh {cells} tail.{key}")
    require(
        type(tail["checkpoints"]) is list
        and all(type(value) is float for value in tail["checkpoints"]),
        f"mesh {cells} tail checkpoint types",
    )

    for key in ("state_count", "midpoint_generator_nnz", "relative_generator_nnz"):
        require_int(diagnostics[key], f"mesh {cells} diagnostics.{key}")
        require(diagnostics[key] > 0, f"mesh {cells} diagnostics.{key} must be positive")
    for key in EXPECTED_DIAGNOSTIC_KEYS - {
        "mesh",
        "state_count",
        "matrix_free_full_generator",
        "midpoint_generator_nnz",
        "relative_generator_nnz",
        "factor_diagnostics",
    }:
        require_float(diagnostics[key], f"mesh {cells} diagnostics.{key}")
    for key in (
        "initial_mass_error",
        "physical_budget_absolute_error",
        "weight_sum_error",
        "killed_mass_balance_operator_error",
    ):
        require_nonnegative_float(diagnostics[key], f"mesh {cells} diagnostics.{key}")
    require(
        float(diagnostics["physical_budget"]) >= 0.0,
        f"mesh {cells} physical budget must be nonnegative",
    )
    factor_diagnostics = require_exact_keys(
        diagnostics["factor_diagnostics"],
        EXPECTED_FACTOR_DIAGNOSTIC_KEYS,
        f"mesh {cells} factor diagnostics schema",
    )
    for key in EXPECTED_FACTOR_DIAGNOSTIC_KEYS - {
        "cells_per_coordinate",
        "patch_integrals",
        "spacings",
        "state_count_if_full_matrix_formed",
    }:
        require_float(factor_diagnostics[key], f"mesh {cells} factor diagnostics.{key}")
    for key in (
        "contact_area_error_estimate",
        "maximum_initial_quadrature_error_estimate",
        "maximum_patch_quadrature_error_estimate",
        "midpoint_generator_row_error",
        "relative_generator_row_error",
    ):
        require_nonnegative_float(factor_diagnostics[key], f"mesh {cells} factor diagnostics.{key}")
    for key in (
        "contact_area",
        "contact_area_exact",
        "midpoint_initial_mass",
        "relative_initial_mass",
    ):
        require(
            float(factor_diagnostics[key]) > 0.0,
            f"mesh {cells} factor diagnostics.{key} must be positive",
        )
    require_int(
        factor_diagnostics["cells_per_coordinate"],
        f"mesh {cells} factor diagnostics.cells_per_coordinate",
    )
    require_int(
        factor_diagnostics["state_count_if_full_matrix_formed"],
        f"mesh {cells} factor diagnostics.state_count_if_full_matrix_formed",
    )
    require(
        factor_diagnostics["cells_per_coordinate"] == cells
        and factor_diagnostics["state_count_if_full_matrix_formed"] == cells**3,
        f"mesh {cells} factor diagnostics mesh duplicates",
    )
    patch_integrals = factor_diagnostics["patch_integrals"]
    require(
        type(patch_integrals) is list
        and len(patch_integrals) == 4
        and all(
            type(value) is float and math.isfinite(value) and value > 0.0
            for value in patch_integrals
        ),
        f"mesh {cells} factor diagnostics patch integrals",
    )
    spacings = require_exact_keys(
        factor_diagnostics["spacings"],
        EXPECTED_FACTOR_SPACING_KEYS,
        f"mesh {cells} factor diagnostics spacings",
    )
    require(
        all(
            type(value) is float and math.isfinite(value) and value > 0.0
            for value in spacings.values()
        ),
        f"mesh {cells} factor diagnostics spacing values",
    )
    require_int(scan["strict_sign_change_bracket_count"], f"mesh {cells} bracket count")
    require(
        scan["strict_sign_change_bracket_count"] >= 0,
        f"mesh {cells} bracket count must be nonnegative",
    )
    for key in EXPECTED_SCAN_KEYS - {
        "time_grid",
        "strict_sign_change_bracket_count",
        "positive_derivative_checkpoint",
        "saved_trace",
    }:
        require_float(scan[key], f"mesh {cells} scan.{key}")
    require_nonnegative_float(
        scan["maximum_sampled_differential_mass_balance_residual"],
        f"mesh {cells} scan.maximum_sampled_differential_mass_balance_residual",
    )
    require_unit_interval_float(
        scan["maximum_boundary_layer_fraction"],
        f"mesh {cells} scan.maximum_boundary_layer_fraction",
        survival_tolerance,
    )
    require_exact_keys(
        scan["positive_derivative_checkpoint"], {"time", "f_t"}, f"mesh {cells} checkpoint"
    )
    require_float(scan["positive_derivative_checkpoint"]["time"], f"mesh {cells} checkpoint time")
    require_float(scan["positive_derivative_checkpoint"]["f_t"], f"mesh {cells} checkpoint f_t")

    weights = [float(value) for value in manifest["fixed_absolute_weights"]]
    require_mesh_triplet(diagnostics["mesh"], cells, f"mesh {cells} diagnostics.mesh")
    require(diagnostics["state_count"] == cells**3, f"mesh {cells} state count")
    require(diagnostics["matrix_free_full_generator"] is True, f"mesh {cells} matrix-free flag")
    require(same_float(diagnostics["minimum_weight"], min(weights)), f"mesh {cells} min weight")
    require(
        same_float(diagnostics["weight_sum_error"], abs(sum(weights) - 1.0)),
        f"mesh {cells} weight sum",
    )
    require(
        same_float(
            diagnostics["physical_budget_absolute_error"],
            abs(float(diagnostics["physical_budget"]) - float(manifest["positive_budget"])),
        ),
        f"mesh {cells} budget duplicate",
    )
    require(
        float(diagnostics["minimum_killing_per_budget"]) >= 0.0
        and float(diagnostics["maximum_killing_per_budget"])
        >= float(diagnostics["minimum_killing_per_budget"]),
        f"mesh {cells} killing range",
    )

    expected_time_grid = {
        key: manifest["time_scan"][key]
        for key in ("start", "stop", "spacing", "points", "chunk_points")
    }
    require(
        exact_json_equal(scan["time_grid"], expected_time_grid),
        f"mesh {cells} scan grid changed",
    )
    require(
        same_float(
            scan["minimum_density_sampling_start"],
            manifest["tail_gates"]["minimum_density_sampling_start"],
        ),
        f"mesh {cells} density start",
    )
    saved_trace = scan["saved_trace"]
    require(type(saved_trace) is list and bool(saved_trace), f"mesh {cells} saved trace absent")
    saved_spacing = float(manifest["time_scan"]["saved_trace_spacing"])
    expected_saved_count = (
        int(
            round(
                (float(manifest["time_scan"]["stop"]) - float(manifest["time_scan"]["start"]))
                / saved_spacing
            )
        )
        + 1
    )
    require(len(saved_trace) == expected_saved_count, f"mesh {cells} saved trace length")
    for index, trace_row in enumerate(saved_trace):
        require_exact_keys(
            trace_row, EXPECTED_SCAN_TRACE_KEYS, f"mesh {cells} saved trace row {index}"
        )
        for key in EXPECTED_SCAN_TRACE_KEYS:
            require_float(trace_row[key], f"mesh {cells} saved trace {index}.{key}")
        require(
            same_float(
                trace_row["time"],
                float(manifest["time_scan"]["start"]) + saved_spacing * index,
            ),
            f"mesh {cells} saved trace time {index}",
        )
        require_nonnegative_float(
            trace_row["differential_mass_balance_residual"],
            f"mesh {cells} saved trace {index}.differential_mass_balance_residual",
        )
        require_unit_interval_float(
            trace_row["boundary_layer_fraction"],
            f"mesh {cells} saved trace {index}.boundary_layer_fraction",
            survival_tolerance,
        )
        require_survival(float(trace_row["survival"]), f"saved trace {index} survival")
    positive_index = int(
        round(float(manifest["root_gates"]["positive_derivative_time"]) / saved_spacing)
    )
    require(
        scan["positive_derivative_checkpoint"]
        == {
            "time": manifest["root_gates"]["positive_derivative_time"],
            "f_t": saved_trace[positive_index]["f_t"],
        },
        f"mesh {cells} positive checkpoint duplicate",
    )
    require(
        same_float(scan["derivative_at_scan_stop"], saved_trace[-1]["f_t"])
        and same_float(scan["survival_at_scan_stop"], saved_trace[-1]["survival"]),
        f"mesh {cells} scan endpoint duplicate",
    )
    sampled_from = float(scan["minimum_density_sampling_start"])
    sampled_trace = [row for row in saved_trace if float(row["time"]) >= sampled_from]
    require(
        float(scan["sampled_peak_density"]) + 5.0e-15
        >= max(float(trace_row["f"]) for trace_row in saved_trace),
        f"mesh {cells} sampled peak contradicts saved trace",
    )
    require(
        float(scan["minimum_sampled_density_from_frozen_start"]) - 5.0e-15
        <= min(float(trace_row["f"]) for trace_row in sampled_trace),
        f"mesh {cells} sampled minimum contradicts saved trace",
    )
    require(
        float(scan["maximum_boundary_layer_fraction"]) + 5.0e-15
        >= max(float(trace_row["boundary_layer_fraction"]) for trace_row in saved_trace),
        f"mesh {cells} boundary maximum contradicts saved trace",
    )
    require(
        float(scan["maximum_sampled_differential_mass_balance_residual"]) + 5.0e-15
        >= max(float(trace_row["differential_mass_balance_residual"]) for trace_row in saved_trace),
        f"mesh {cells} mass residual contradicts saved trace",
    )
    saved_survival_increases = [
        float(right["survival"]) - float(left["survival"])
        for left, right in zip(saved_trace[:-1], saved_trace[1:], strict=True)
    ]
    trace_stride = int(round(saved_spacing / float(manifest["time_scan"]["spacing"])))
    require(
        float(scan["maximum_sampled_survival_increase"]) + 5.0e-15
        >= max(saved_survival_increases) / trace_stride,
        f"mesh {cells} survival-increase summary contradicts saved trace",
    )

    roots = structure["roots"]
    require(type(roots) is list, f"mesh {cells} roots are not a list")
    require(structure["stationary_root_count"] == len(roots), f"mesh {cells} root count mismatch")
    times: list[float] = []
    densities: list[float] = []
    survivals: list[float] = []
    topology: list[str] = []
    for index, root in enumerate(roots):
        require_exact_keys(root, EXPECTED_ROOT_KEYS, f"mesh {cells} root {index} schema")
        for key in EXPECTED_ROOT_KEYS - {"topology"}:
            require_float(root[key], f"mesh {cells} root {index}.{key}")
        time_value = float(root["time"])
        density = float(root["density"])
        f_t = float(root["f_t"])
        f_tt = float(root["f_tt"])
        require(
            float(manifest["time_scan"]["minimum_root_time"])
            <= time_value
            <= float(manifest["time_scan"]["stop"]),
            f"mesh {cells} root {index} time lies outside the frozen root window",
        )
        require(density > 0.0, f"mesh {cells} nonpositive root density")
        require_nonnegative_float(
            root["scaled_first_derivative_residual"],
            f"mesh {cells} root {index}.scaled_first_derivative_residual",
        )
        require_nonnegative_float(
            root["differential_mass_balance_residual"],
            f"mesh {cells} root {index}.differential_mass_balance_residual",
        )
        require_unit_interval_float(
            root["boundary_layer_fraction"],
            f"mesh {cells} root {index}.boundary_layer_fraction",
            survival_tolerance,
        )
        derived_topology = "maximum" if f_tt < 0.0 else "minimum"
        require(root["topology"] == derived_topology, f"mesh {cells} root topology")
        require(
            same_float(root["scaled_first_derivative_residual"], abs(time_value * f_t / density)),
            f"mesh {cells} root residual identity",
        )
        require(
            same_float(root["scaled_second_derivative"], time_value**2 * f_tt / density),
            f"mesh {cells} root curvature identity",
        )
        times.append(time_value)
        densities.append(density)
        survivals.append(float(root["survival"]))
        require_survival(survivals[-1], f"root {index} survival")
        topology.append(derived_topology)
    require(
        all(right > left for left, right in zip(times[:-1], times[1:], strict=True)),
        f"mesh {cells} roots are unordered",
    )
    require(
        all(right < left for left, right in zip(survivals[:-1], survivals[1:], strict=True)),
        f"mesh {cells} root survival is not strictly decreasing",
    )
    require(structure["topology"] == topology, f"mesh {cells} topology copy mismatch")
    require(
        int(scan["strict_sign_change_bracket_count"]) >= len(roots),
        f"mesh {cells} bracket count is smaller than root count",
    )
    for index, time_value in enumerate(times):
        bracket = next(
            (
                (left, right)
                for left, right in zip(saved_trace[:-1], saved_trace[1:], strict=True)
                if float(left["time"]) <= time_value <= float(right["time"])
            ),
            None,
        )
        require(bracket is not None, f"mesh {cells} root {index} outside saved trace")
        left, right = bracket
        require(
            float(left["f_t"]) * float(right["f_t"]) <= 0.0,
            f"mesh {cells} root {index} lacks a saved-trace sign bracket",
        )
        left_survival = float(left["survival"])
        right_survival = float(right["survival"])
        root_survival = survivals[index]
        require(
            min(left_survival, right_survival) - survival_tolerance
            <= root_survival
            <= max(left_survival, right_survival) + survival_tolerance,
            f"mesh {cells} root {index} survival lies outside its saved-trace time bracket",
        )

    expected_shape = topology == EXPECTED_TOPOLOGY
    peak: float | None = None
    valleys: list[float] | None = None
    if expected_shape:
        peak = min(densities[index] for index in (0, 2, 4)) / max(
            densities[index] for index in (0, 2, 4)
        )
        valleys = [
            densities[1] / min(densities[0], densities[2]),
            densities[3] / min(densities[2], densities[4]),
        ]
        require_unit_interval_float(
            structure["peak_minimum_to_maximum_ratio"],
            f"mesh {cells} peak ratio",
        )
        require(
            same_float(peak, structure["peak_minimum_to_maximum_ratio"]),
            f"mesh {cells} peak ratio identity",
        )
        reported_valleys = structure["valley_to_smaller_adjacent_peak_ratios"]
        require(
            type(reported_valleys) is list
            and len(reported_valleys) == 2
            and all(
                type(value) is float and math.isfinite(value) and 0.0 <= value <= 1.0
                for value in reported_valleys
            )
            and all(same_float(a, b) for a, b in zip(valleys, reported_valleys, strict=True)),
            f"mesh {cells} valley ratio identity",
        )
    else:
        require(
            structure["peak_minimum_to_maximum_ratio"] is None
            and structure["valley_to_smaller_adjacent_peak_ratios"] is None,
            f"mesh {cells} unavailable shape metrics must be null",
        )

    require(
        exact_json_equal(tail["checkpoints"], manifest["tail_gates"]["checkpoints"]),
        f"mesh {cells} tail times",
    )
    tail_trace = tail["trace"]
    require(type(tail_trace) is list and len(tail_trace) == 4, f"mesh {cells} tail trace")
    for index, trace_row in enumerate(tail_trace):
        require_exact_keys(
            trace_row, EXPECTED_TAIL_TRACE_KEYS, f"mesh {cells} tail trace row {index}"
        )
        for key in EXPECTED_TAIL_TRACE_KEYS:
            require_float(trace_row[key], f"mesh {cells} tail trace {index}.{key}")
        require(
            same_float(trace_row["time"], manifest["tail_gates"]["checkpoints"][index]),
            f"mesh {cells} tail time {index}",
        )
        require_nonnegative_float(
            trace_row["differential_mass_balance_residual"],
            f"mesh {cells} tail trace {index}.differential_mass_balance_residual",
        )
        require_survival(float(trace_row["survival"]), f"tail trace {index} survival")
    require_nonnegative_float(
        tail["maximum_checkpoint_differential_mass_balance_residual"],
        f"mesh {cells} tail.maximum_checkpoint_differential_mass_balance_residual",
    )
    require(
        same_float(tail_trace[0]["density"], saved_trace[-1]["f"])
        and same_float(tail_trace[0]["survival"], saved_trace[-1]["survival"])
        and same_float(
            tail_trace[0]["differential_mass_balance_residual"],
            saved_trace[-1]["differential_mass_balance_residual"],
        ),
        f"mesh {cells} scan/tail junction",
    )
    tail_increases = [
        float(right["survival"]) - float(left["survival"])
        for left, right in zip(tail_trace[:-1], tail_trace[1:], strict=True)
    ]
    require(
        same_float(tail["survival_at_scan_stop"], tail_trace[0]["survival"])
        and same_float(tail["final_survival"], tail_trace[-1]["survival"])
        and same_float(
            tail["survival_decrease_from_scan_stop"],
            float(tail_trace[0]["survival"]) - float(tail_trace[-1]["survival"]),
        )
        and same_float(tail["maximum_checkpoint_survival_increase"], max(tail_increases))
        and same_float(
            tail["minimum_checkpoint_density"],
            min(float(trace_row["density"]) for trace_row in tail_trace),
        )
        and same_float(
            tail["minimum_tail_state_component"],
            min(float(trace_row["minimum_state_component"]) for trace_row in tail_trace),
        )
        and same_float(
            tail["minimum_final_state_component"], tail_trace[-1]["minimum_state_component"]
        )
        and same_float(
            tail["maximum_checkpoint_differential_mass_balance_residual"],
            max(float(trace_row["differential_mass_balance_residual"]) for trace_row in tail_trace),
        ),
        f"mesh {cells} tail summary identity",
    )

    final_survival = float(mass["final_survival"])
    require_survival(final_survival, "final survival")
    for key in (
        "final_time",
        "final_survival",
        "total_reaction_mass_to_final_time",
        "final_differential_mass_balance_residual",
    ):
        require_float(mass[key], f"mesh {cells} mass.{key}")
    require_nonnegative_float(
        mass["final_differential_mass_balance_residual"],
        f"mesh {cells} mass.final_differential_mass_balance_residual",
    )
    require(
        same_float(mass["final_time"], manifest["event_mass"]["final_time"])
        and same_float(final_survival, tail["final_survival"])
        and same_float(mass["total_reaction_mass_to_final_time"], 1.0 - final_survival)
        and same_float(
            mass["final_differential_mass_balance_residual"],
            tail_trace[-1]["differential_mass_balance_residual"],
        ),
        f"mesh {cells} final mass duplicates",
    )
    masses: list[float] | None = None
    if expected_shape:
        masses = [
            1.0 - survivals[1],
            survivals[1] - survivals[3],
            survivals[3] - final_survival,
        ]
        reported_masses = mass["basin_reaction_masses"]
        require(
            type(reported_masses) is list
            and len(reported_masses) == 3
            and all(same_float(a, b) for a, b in zip(masses, reported_masses, strict=True)),
            f"mesh {cells} event mass identity",
        )
        for index, value in enumerate(reported_masses):
            require_float(value, f"mesh {cells} basin mass {index}")
        require_float(mass["basin_mass_sum"], f"mesh {cells} basin sum")
        require_nonnegative_float(
            mass["basin_mass_sum_vs_total_reaction_difference"],
            f"mesh {cells} basin difference",
        )
        require(
            same_float(mass["basin_mass_sum"], sum(masses))
            and same_float(
                mass["basin_mass_sum_vs_total_reaction_difference"],
                abs(sum(masses) - (1.0 - final_survival)),
            ),
            f"mesh {cells} basin mass summary",
        )
    else:
        require(
            mass["basin_reaction_masses"] is None
            and mass["basin_mass_sum"] is None
            and mass["basin_mass_sum_vs_total_reaction_difference"] is None,
            f"mesh {cells} unavailable event metrics must be null",
        )

    require(control["control_variable"] == "full installed budget B", f"mesh {cells} control name")
    require_float(control["analytic_augmented_operator_trace"], f"mesh {cells} augmented trace")
    require_nonnegative_float(
        control["maximum_direct_vs_tangent_state_relative_l1"],
        f"mesh {cells} maximum tangent state difference",
    )
    require_nonnegative_float(
        control["maximum_direct_vs_tangent_time_jet_absolute_difference"],
        f"mesh {cells} maximum tangent jet difference",
    )
    control_rows = control["rows"]
    require(
        type(control_rows) is list and len(control_rows) == len(roots), f"mesh {cells} control rows"
    )
    state_differences: list[float] = []
    jet_differences: list[float] = []
    for index, (control_row, root) in enumerate(zip(control_rows, roots, strict=True)):
        require_exact_keys(
            control_row, EXPECTED_CONTROL_ROW_KEYS, f"mesh {cells} control row {index}"
        )
        require_float(control_row["time"], f"mesh {cells} control row {index}.time")
        require_float(
            control_row["direct_vs_tangent_state_relative_l1"],
            f"mesh {cells} control row {index}.state difference",
        )
        require(
            float(control_row["direct_vs_tangent_state_relative_l1"]) >= 0.0,
            f"mesh {cells} negative tangent state difference",
        )
        require_float(
            control_row["maximum_direct_vs_tangent_time_jet_absolute_difference"],
            f"mesh {cells} control row {index}.jet difference",
        )
        require(
            float(control_row["maximum_direct_vs_tangent_time_jet_absolute_difference"]) >= 0.0,
            f"mesh {cells} negative tangent jet difference",
        )
        for key, value in control_row["budget_control_jets"].items():
            require_float(value, f"mesh {cells} control row {index}.{key}")
        require_exact_keys(
            control_row["budget_control_jets"],
            EXPECTED_BUDGET_CONTROL_KEYS,
            f"mesh {cells} budget control row {index}",
        )
        require(same_float(control_row["time"], root["time"]), f"mesh {cells} control time")
        jets = control_row["time_jets_f_f_t_f_tt_f_ttt"]
        expected_jets = [root["density"], root["f_t"], root["f_tt"], root["f_ttt"]]
        require(
            type(jets) is list
            and len(jets) == 4
            and all(type(value) is float and math.isfinite(value) for value in jets),
            f"mesh {cells} tangent time-jet schema",
        )
        row_jet_difference = max(
            abs(float(a) - float(b)) for a, b in zip(jets, expected_jets, strict=True)
        )
        require(
            same_float(
                control_row["maximum_direct_vs_tangent_time_jet_absolute_difference"],
                row_jet_difference,
            ),
            f"mesh {cells} tangent row difference",
        )
        state_differences.append(float(control_row["direct_vs_tangent_state_relative_l1"]))
        jet_differences.append(row_jet_difference)
    maximum_state_difference = max(state_differences, default=0.0)
    maximum_jet_difference = max(jet_differences, default=0.0)
    require(
        same_float(control["maximum_direct_vs_tangent_state_relative_l1"], maximum_state_difference)
        and same_float(
            control["maximum_direct_vs_tangent_time_jet_absolute_difference"],
            maximum_jet_difference,
        ),
        f"mesh {cells} tangent maxima",
    )

    root_rules = manifest["root_gates"]
    event_rules = manifest["event_mass"]
    state_components = [
        float(scan["minimum_streamed_state_component"]),
        float(tail["minimum_final_state_component"]),
        *(float(root["minimum_state_component"]) for root in roots),
    ]
    independently_reconstructed = {
        "initial_mass": float(diagnostics["initial_mass_error"]) <= 1.0e-12,
        "physical_budget": float(diagnostics["physical_budget_absolute_error"]) <= 1.0e-12,
        "weights_positive_unit_sum": float(diagnostics["minimum_weight"]) > 0.0
        and float(diagnostics["weight_sum_error"]) <= 2.0e-14,
        "five_alternating_simple_roots": expected_shape,
        "peak_ratio": peak is not None and peak >= float(root_rules["minimum_peak_ratio"]),
        "valley_ratios": valleys is not None
        and max(valleys) <= float(root_rules["maximum_valley_ratio"]),
        "root_residuals": bool(roots)
        and all(
            float(root["scaled_first_derivative_residual"])
            <= float(root_rules["maximum_scaled_root_residual"])
            for root in roots
        ),
        "curvature_margins": bool(roots)
        and all(
            abs(float(root["scaled_second_derivative"]))
            >= float(root_rules["minimum_absolute_scaled_curvature"])
            for root in roots
        ),
        "endpoint_derivative_signs": float(scan["positive_derivative_checkpoint"]["f_t"]) > 0.0
        and float(scan["derivative_at_scan_stop"]) < 0.0,
        "sampled_density_positive": float(scan["minimum_sampled_density_from_frozen_start"])
        > float(manifest["tail_gates"]["minimum_density"])
        and float(tail["minimum_checkpoint_density"])
        > float(manifest["tail_gates"]["minimum_density"]),
        "root_density_positive": bool(roots) and min(densities) > 0.0,
        "survival_positive": float(scan["survival_at_scan_stop"]) > 0.0 and final_survival > 0.0,
        "state_positivity_tolerance": min(state_components)
        >= -float(root_rules["maximum_negative_state_tolerance"]),
        "survival_monotone_through_final_time": float(scan["maximum_sampled_survival_increase"])
        <= float(root_rules["maximum_survival_increase"])
        and float(tail["maximum_checkpoint_survival_increase"])
        <= float(manifest["tail_gates"]["maximum_survival_increase"]),
        "tail_final_state_positivity": float(tail["minimum_tail_state_component"])
        >= -float(manifest["tail_gates"]["maximum_negative_state_tolerance"]),
        "generator_Q_one_equals_minus_B_k0": float(
            diagnostics["killed_mass_balance_operator_error"]
        )
        <= float(event_rules["maximum_mass_balance_error"]),
        "mass_balance_on_saved_scan": float(
            scan["maximum_sampled_differential_mass_balance_residual"]
        )
        <= float(event_rules["maximum_mass_balance_error"]),
        "mass_balance_at_roots": bool(roots)
        and max(float(root["differential_mass_balance_residual"]) for root in roots)
        <= float(event_rules["maximum_mass_balance_error"]),
        "mass_balance_at_final_time": float(mass["final_differential_mass_balance_residual"])
        <= float(event_rules["maximum_mass_balance_error"]),
        "mass_balance_on_tail_checkpoints": float(
            tail["maximum_checkpoint_differential_mass_balance_residual"]
        )
        <= float(event_rules["maximum_mass_balance_error"]),
        "event_basin_masses": masses is not None
        and min(masses) >= float(event_rules["minimum_each_basin_mass"]),
        "event_mass_partition_closure": masses is not None
        and abs(sum(masses) - (1.0 - final_survival))
        <= float(event_rules["maximum_mass_balance_error"]),
        "tangent_state_reproduction": len(control_rows) == 5
        and maximum_state_difference <= float(root_rules["maximum_tangent_state_relative_l1"]),
        "tangent_time_jet_reproduction": len(control_rows) == 5
        and maximum_jet_difference
        <= float(root_rules["maximum_tangent_time_jet_absolute_difference"]),
    }
    require(
        gates == independently_reconstructed,
        f"mesh {cells} reported gates disagree with reconstructed values",
    )
    require(
        row["all_mesh_gates_passed"] is all(gates.values()),
        f"mesh {cells} gate aggregate",
    )

    return {
        "mesh": cells,
        "root_times": times,
        "peak_ratio": peak,
        "valley_ratios": valleys,
        "basin_masses": masses,
        "final_survival": final_survival,
        "expected_five_root_topology": expected_shape,
        "independently_algebraically_reconstructed_gates": independently_reconstructed,
        "producer_reported_full_scan_extrema_used": [
            "minimum_sampled_density_from_frozen_start",
            "minimum_streamed_state_component",
            "maximum_sampled_survival_increase",
            "maximum_sampled_differential_mass_balance_residual",
        ],
        "all_reported_mesh_gates_passed": all(gates.values()),
    }


def reconstruct_agreement(
    summaries: list[dict[str, Any]], result_agreement: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    require_exact_keys(result_agreement, EXPECTED_AGREEMENT_KEYS, "agreement schema changed")
    mesh_pair = result_agreement["mesh_pair"]
    require(type(mesh_pair) is list and len(mesh_pair) == 2, "agreement mesh pair schema")
    for index, cells in enumerate(manifest["heldout_meshes"]):
        require_mesh_triplet(mesh_pair[index], int(cells), f"agreement mesh_pair[{index}]")
    reported_gates = require_exact_keys(
        result_agreement["gates"], EXPECTED_AGREEMENT_GATE_KEYS, "agreement gate schema"
    )
    require(all(type(value) is bool for value in reported_gates.values()), "agreement gate types")
    left, right = summaries
    comparable = left["expected_five_root_topology"] and right["expected_five_root_topology"]
    metrics: dict[str, float | None] = {
        "maximum_paired_root_time_difference": (
            max(abs(a - b) for a, b in zip(left["root_times"], right["root_times"], strict=True))
            if comparable
            else None
        ),
        "peak_ratio_absolute_difference": (
            abs(float(left["peak_ratio"]) - float(right["peak_ratio"])) if comparable else None
        ),
        "maximum_valley_ratio_absolute_difference": (
            max(
                abs(a - b)
                for a, b in zip(left["valley_ratios"], right["valley_ratios"], strict=True)
            )
            if comparable
            else None
        ),
        "maximum_event_mass_absolute_difference": (
            max(
                abs(a - b) for a, b in zip(left["basin_masses"], right["basin_masses"], strict=True)
            )
            if comparable
            else None
        ),
        "final_survival_absolute_difference": abs(left["final_survival"] - right["final_survival"]),
    }
    for key, value in metrics.items():
        reported = result_agreement[key]
        if value is None:
            require(reported is None, f"agreement metric {key} must be null")
        else:
            require_nonnegative_float(reported, f"agreement metric {key}")
            require(same_float(value, reported), f"agreement metric {key} mismatch")
    thresholds = manifest["mesh_agreement"]
    gates = {
        "paired_root_times": metrics["maximum_paired_root_time_difference"] is not None
        and metrics["maximum_paired_root_time_difference"]
        <= float(thresholds["maximum_paired_root_time_difference"]),
        "peak_ratio": metrics["peak_ratio_absolute_difference"] is not None
        and metrics["peak_ratio_absolute_difference"]
        <= float(thresholds["maximum_peak_ratio_difference"]),
        "valley_ratios": metrics["maximum_valley_ratio_absolute_difference"] is not None
        and metrics["maximum_valley_ratio_absolute_difference"]
        <= float(thresholds["maximum_valley_ratio_difference"]),
        "event_basin_masses": metrics["maximum_event_mass_absolute_difference"] is not None
        and metrics["maximum_event_mass_absolute_difference"]
        <= float(thresholds["maximum_event_mass_difference"]),
        "final_survival": metrics["final_survival_absolute_difference"]
        <= float(thresholds["maximum_final_survival_difference"]),
    }
    require(reported_gates == gates, "agreement gates disagree with raw values")
    require(
        result_agreement["all_agreement_gates_passed"] is all(gates.values()),
        "agreement aggregate mismatch",
    )
    return {"metrics": metrics, "gates": gates, "all_agreement_gates_passed": all(gates.values())}


def audit(
    *,
    result_path: Path = RESULT,
    reproducibility_path: Path = REPRODUCIBILITY,
    manifest_path: Path = MANIFEST,
    report: Path = REPORT,
    return_snapshots: bool = False,
) -> dict[str, Any] | tuple[dict[str, Any], dict[Path, str]]:
    result_file = require_regular_nonsymlink_file(result_path, "canonical result")
    evidence_file = require_regular_nonsymlink_file(
        reproducibility_path, "canonical reproducibility evidence"
    )
    manifest_file = require_regular_nonsymlink_file(manifest_path, "frozen manifest")
    manifest = validate_manifest(manifest_file, report)
    result, result_raw = load_canonical_object_with_bytes(result_file)
    evidence, evidence_raw = load_canonical_object_with_bytes(evidence_file)
    result_hash = sha256_bytes(result_raw)
    evidence_hash = sha256_bytes(evidence_raw)
    auditor_hash = sha256_bytes(HERE.read_bytes())
    snapshots = {
        result_file: result_hash,
        evidence_file: evidence_hash,
        manifest_file: EXPECTED_MANIFEST_SHA256,
        lexical_absolute(HERE): auditor_hash,
    }
    for pin in manifest["pinned_files"].values():
        path = require_regular_nonsymlink_file(
            Path(report).resolve() / pin["path"], f"pinned input {pin['path']}"
        )
        snapshots[path] = pin["sha256"]

    require(set(result) == EXPECTED_RESULT_KEYS, "result top-level schema changed")
    require_no_temporary_metadata(result, "result")
    require_authorized_claim_key_locations(result)
    require_no_temporary_metadata(evidence, "evidence")
    require_int(result.get("schema_version"), "result schema version")
    require(result.get("schema_version") == 1, "result schema version changed")
    require(result.get("stage") == EXPECTED_STAGE, "result stage changed")
    require(result.get("evidence_timing") == manifest["evidence_timing"], "evidence timing")
    require(result.get("claim_scope") == manifest["claim_scope"], "claim scope changed")
    require(
        result.get("manifest_sha256") == EXPECTED_MANIFEST_SHA256,
        "result cites the wrong manifest",
    )
    for key, expected in EXPECTED_NEGATIVE_FLAGS.items():
        require(result.get(key) is expected, f"unsafe claim flag {key}")
    require(
        exact_json_equal(result.get("required_claim_flags"), EXPECTED_NEGATIVE_FLAGS),
        "nested claim flags changed",
    )
    require(result.get("weights_refit") is False, "weights were marked as refit")
    require(
        exact_json_equal(result.get("positive_budget"), manifest["positive_budget"]),
        "budget mismatch",
    )
    require(
        exact_json_equal(result.get("fixed_absolute_weights"), manifest["fixed_absolute_weights"]),
        "weights mismatch",
    )
    require(
        exact_json_equal(result.get("physical_parameters"), manifest["physical_parameters"]),
        "physical parameters mismatch",
    )
    require(
        exact_json_equal(
            result.get("numerical_reproducibility"), manifest["numerical_reproducibility"]
        ),
        "numerical reproducibility contract changed",
    )
    reproducibility_declaration = require_exact_keys(
        result.get("reproducibility_evidence"),
        {
            "file",
            "independent_full_processes_required",
            "canonical_result_requires_external_byte_comparison",
        },
        "nested reproducibility-evidence schema changed",
    )
    require(
        exact_json_equal(
            reproducibility_declaration,
            {
                "file": manifest["numerical_reproducibility"]["reproducibility_evidence_file"],
                "independent_full_processes_required": 2,
                "canonical_result_requires_external_byte_comparison": True,
            },
        ),
        "nested reproducibility-evidence declaration changed",
    )
    require(result.get("limitations") == EXPECTED_LIMITATIONS, "limitations changed")
    software = require_exact_keys(result.get("software"), {"python", "numpy", "scipy"}, "software")
    require(
        all(type(value) is str and bool(value) for value in software.values()),
        "software versions must be nonempty strings",
    )
    require(
        exact_json_equal(
            result.get("pinned_file_hashes"),
            {role: pin["sha256"] for role, pin in manifest["pinned_files"].items()},
        ),
        "result pin map mismatch",
    )

    rows = result.get("heldout_mesh_rows")
    require(type(rows) is list and len(rows) == 2, "result does not contain two mesh rows")
    summaries = [
        reconstruct_row(row, cells, manifest)
        for row, cells in zip(rows, manifest["heldout_meshes"], strict=True)
    ]
    agreement = reconstruct_agreement(summaries, result["mesh_agreement"], manifest)
    passed = (
        all(row["all_reported_mesh_gates_passed"] for row in summaries)
        and agreement["all_agreement_gates_passed"]
    )
    require(type(result.get("all_gates_passed")) is bool, "overall result gate type")
    require(
        type(result.get("positive_B_event_mass_shape_confirmation")) is bool,
        "positive-B claim flag type",
    )
    require(result.get("all_gates_passed") is passed, "overall result gate mismatch")
    require(
        result.get("positive_B_event_mass_shape_confirmation") is passed,
        "positive-B claim flag mismatch",
    )
    expected_status = (
        "PASS_RESULT_INFORMED_POSITIVE_B_EVENT_MASS_SHAPE_CONFIRMATION"
        if passed
        else "HOLD_RESULT_INFORMED_POSITIVE_B_CONFIRMATION"
    )
    require(result.get("status") == expected_status, "result status mismatch")

    require_exact_keys(evidence, EXPECTED_EVIDENCE_KEYS, "evidence schema changed")
    require_int(evidence.get("schema_version"), "evidence schema version")
    require(evidence.get("schema_version") == 1, "evidence schema version changed")
    require(
        evidence.get("stage") == "positive_B_broad_four_slab_two_process_reproducibility",
        "evidence stage changed",
    )
    require(
        evidence.get("manifest_sha256") == EXPECTED_MANIFEST_SHA256,
        "evidence cites the wrong manifest",
    )
    require_int(evidence.get("independent_process_count"), "replica count")
    require(evidence.get("independent_process_count") == 2, "replica count changed")
    require(evidence.get("execution_order") == "sequential", "replica order changed")
    require(
        type(evidence.get("replica_exit_codes")) is list
        and all(
            type(value) is int and type(value) is not bool
            for value in evidence["replica_exit_codes"]
        )
        and evidence.get("replica_exit_codes") == ([0, 0] if passed else [2, 2]),
        "replica exit codes mismatch",
    )
    require(
        evidence.get("replica_result_sha256") == [result_hash, result_hash],
        "replica hashes do not match the canonical result",
    )
    require(evidence.get("byte_identical") is True, "replicas were not byte-identical")
    require(
        evidence.get("canonical_result_sha256") == result_hash,
        "canonical result hash mismatch",
    )
    require(
        evidence.get("canonical_promotion_after_comparison") is True,
        "canonical promotion order is unsafe",
    )
    require(evidence.get("result_status") == expected_status, "evidence status mismatch")
    require(evidence.get("all_gates_passed") is passed, "evidence gate mismatch")

    payload = {
        "schema_version": 1,
        "stage": "independent_positive_B_result_reconstruction",
        "status": "PASS_INDEPENDENT_RECONSTRUCTION" if passed else "HOLD_REPRODUCED",
        "scientific_result_passed": passed,
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "canonical_result_sha256": result_hash,
        "reproducibility_evidence_sha256": evidence_hash,
        "auditor_sha256": auditor_hash,
        "mesh_reconstructions": summaries,
        "agreement_reconstruction": agreement,
        "claim_boundary": {
            **EXPECTED_NEGATIVE_FLAGS,
            "fixed_box_two_mesh_semidiscrete_point_only": True,
            "allocation_cusp_verified": False,
            "two_process_evidence_record_consistent": True,
            "independent_process_execution_observed_by_auditor": False,
        },
        "independence_boundary": {
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
        },
    }
    for path, expected_hash in snapshots.items():
        require_regular_nonsymlink_file(path, f"audited input {path}")
        require(
            sha256_bytes(path.read_bytes()) == expected_hash,
            f"audited input changed during validation: {path}",
        )
    validate_manifest(manifest_file, report)
    if return_snapshots:
        return payload, snapshots
    return payload


def require_unchanged_snapshots(snapshots: dict[Path, str]) -> None:
    for path, expected_hash in snapshots.items():
        require_regular_nonsymlink_file(path, f"audited input {path}")
        require(
            sha256_bytes(path.read_bytes()) == expected_hash,
            f"audited input changed before publication: {path}",
        )


def fsync_directory(path: Path) -> None:
    directory_fd = os.open(Path(path), os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def atomic_publish(output: Path, payload: dict[str, Any], snapshots: dict[Path, str]) -> None:
    target = Path(output)
    require(target.resolve() == AUDIT_OUTPUT.resolve(), "audit output path is not canonical")
    require(not target.is_symlink(), "audit output may not be a symlink")
    protected = set(snapshots) | {lexical_absolute(HERE)}
    require(lexical_absolute(target) not in protected, "audit output aliases a protected input")
    target.parent.mkdir(parents=True, exist_ok=True)
    had_prior = target.exists()
    if had_prior:
        require(target.is_file() and not target.is_symlink(), "prior audit is not a regular file")
        prior_raw = target.read_bytes()
    else:
        prior_raw = None
    staging = target.with_name(f".{target.name}.staging")
    require(not staging.exists() and not staging.is_symlink(), "audit staging path already exists")
    raw = canonical_bytes(payload)
    published = False
    try:
        with staging.open("xb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        require_unchanged_snapshots(snapshots)
        os.replace(staging, target)
        published = True
        require_unchanged_snapshots(snapshots)
        fsync_directory(target.parent)
        require_unchanged_snapshots(snapshots)
    except Exception:
        rollback_error: Exception | None = None
        if published:
            try:
                if had_prior:
                    require(prior_raw is not None, "prior audit snapshot missing")
                    staging.unlink(missing_ok=True)
                    with staging.open("xb") as handle:
                        handle.write(prior_raw)
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.replace(staging, target)
                else:
                    target.unlink(missing_ok=True)
                fsync_directory(target.parent)
            except Exception as error:  # pragma: no cover - catastrophic rollback path
                rollback_error = error
        staging.unlink(missing_ok=True)
        if rollback_error is not None:
            raise RuntimeError(
                "audit publication failed and rollback also failed"
            ) from rollback_error
        raise
    else:
        staging.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--reproducibility", type=Path, default=REPRODUCIBILITY)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=AUDIT_OUTPUT)
    args = parser.parse_args(argv)
    require(args.result.resolve() == RESULT.resolve(), "only the canonical result may be audited")
    require(
        args.reproducibility.resolve() == REPRODUCIBILITY.resolve(),
        "only the canonical reproducibility record may be audited",
    )
    require(
        args.manifest.resolve() == MANIFEST.resolve(), "only the frozen manifest may be audited"
    )
    require(
        args.output.resolve() == AUDIT_OUTPUT.resolve(), "only the canonical audit may be written"
    )
    audited = audit(
        result_path=args.result,
        reproducibility_path=args.reproducibility,
        manifest_path=args.manifest,
        report=REPORT,
        return_snapshots=True,
    )
    require(type(audited) is tuple, "internal snapshot contract failed")
    payload, snapshots = audited
    atomic_publish(args.output, payload, snapshots)
    print(payload["status"])
    print(args.output)
    return 0 if payload["scientific_result_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
