#!/usr/bin/env python3
"""Frozen, result-blind low-mesh discovery runner for an allocation cusp.

The formal entrypoint is intentionally restricted to the two discovery meshes
65 and 97.  It can establish only ``PASS_DISCOVERY_LOW_MESH_ONLY``; every
continuum, held-out confirmation, independent-solver, and publication flag is
hard-coded false.  Formal execution requires an external SHA-256 of the
frozen manifest and two byte-identical sequential subprocess replicas.

The default-safe mode is a small explicit-CSR algebra dry run.  Merely
importing this module never evaluates a scientific mesh or writes an artifact.
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import functools
import hashlib
import importlib.util
import io
import json
import math
import os
import platform
import re
import stat
import subprocess
import sys
import sysconfig
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import brentq
from scipy.sparse.linalg import LinearOperator, expm_multiply

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "positive_b_allocation_cusp_discovery_manifest.json"
OUTPUT = DATA / "positive_b_allocation_cusp_discovery_result.json"
REPRODUCIBILITY_OUTPUT = DATA / "positive_b_allocation_cusp_discovery_reproducibility.json"
TEST_FILE = HERE.with_name("test_positive_b_allocation_cusp_discovery.py")
ROUND50_TEST_FILE = HERE.with_name("test_positive_b_allocation_cusp_discovery_round50.py")
ROUND61_TEST_FILE = HERE.with_name("test_positive_b_allocation_cusp_discovery_round61.py")
PROTOCOL = REPORT / "notes" / "positive_b_allocation_cusp_discovery_protocol.md"
INDEPENDENT_AUDIT_OUTPUT = DATA / "positive_b_allocation_cusp_discovery_independent_audit.json"

SCHEMA_VERSION = 6
STAGE = "result_blind_fixed_B_allocation_cusp_two_mesh_discovery_v6"
EVIDENCE_TIMING = "FROZEN_BEFORE_ANY_ALLOCATION_CUSP_MESH_65_OR_97_RUN"
PASS_STATUS = "PASS_DISCOVERY_LOW_MESH_ONLY"
HOLD_STATUS = "HOLD_DISCOVERY"
DISCOVERY_MESHES = (65, 97)
DRY_RUN_MAX_CELLS = 9

REFERENCE_CUSP_TIME = 13.30724696053485
REFERENCE_WEIGHTS = np.asarray(
    (0.28, 0.23115240260064182, 0.20722533378296604, 0.28162226361639210),
    dtype=float,
)
TANGENT_BASIS = np.asarray(
    (
        (-0.0333951724537727, 0.0474675452740631),
        (-0.588571155923409, -0.569871639404847),
        (0.790069638665939, -0.256745888525331),
        (-0.168103310288757, 0.779149982656115),
    ),
    dtype=float,
)

PHYSICAL_PARAMETERS = {
    "particle_diffusion": 0.002,
    "ou_stiffness": 0.1,
    "ou_mean": 0.95,
    "transverse_width": 1.0,
    "contact_radius": 0.16,
    "midpoint_start": 0.14,
    "initial_half_width": 0.02,
    "relative_parallel_start": -0.35,
    "relative_perp_start": 0.0,
    "patch_centres": [0.35, 0.60, 0.75, 0.90],
    "patch_half_width": 0.04,
    "fixed_first_weight": 0.28,
}
FINITE_VOLUME = {
    "midpoint_bounds": [-0.25, 1.85],
    "relative_parallel_bounds": [-1.8, 1.8],
    "scheme": "cell-centred Scharfetter-Gummel/periodic killed-Doi tensor generator",
}
FACTOR_GATES = {
    "maximum_mass_or_conservation_error": 1.0e-10,
    "maximum_quadrature_error_estimate": 1.0e-10,
    "maximum_generator_row_error": 1.0e-10,
    "maximum_spacing_reconstruction_error": 5.0e-13,
    "maximum_error_estimate_undercoverage": 5.0e-13,
}
ALLOCATION_CHART = {
    "source": "B0 full-simplex dimensionless-response SVD",
    "reference_cusp_time": REFERENCE_CUSP_TIME,
    "reference_weights": REFERENCE_WEIGHTS.tolist(),
    "coordinate_rule": "w(theta)=reference_weights+P theta",
    "column_order": "decreasing nonzero singular value",
    "column_sign_rule": "largest-magnitude component positive",
    "metric": "Euclidean allocation metric",
    "P": TANGENT_BASIS.tolist(),
    "source_nonzero_singular_values": [29.4584764696, 4.96688503058],
}
BUDGET_HOMOTOPY = {
    "target_budget": 0.01,
    "schedule": [0.0, 0.0025, 0.0050, 0.0075, 0.0100],
    "initial_point_each_mesh": [REFERENCE_CUSP_TIME, 0.0, 0.0],
    "map": ["F_t", "F_tt", "F_ttt"],
    "normalization": "F=f/B for B>0 and its continuous B=0 limit",
    "analytic_full_jacobian": True,
}
SOLVER = {
    "time_trust_box": [9.0, 18.0],
    "maximum_theta_linf": 0.15,
    "minimum_simplex_weight": 0.03,
    "maximum_newton_iterations": 12,
    "maximum_step_halvings": 8,
    "scaled_residual_tolerance": 1.0e-10,
    "strict_descent_required": True,
}
DERIVATIVE_AUDIT = {
    "allocation_steps": [2.0e-5, 1.0e-5],
    "relative_time_steps": [2.0e-5, 1.0e-5],
    "roundoff_floor": 5.0e-8,
    "required_error_reduction_factor": 0.8,
    "maximum_normalized_disagreement": 1.0e-6,
}
CUSP_GATES = {
    "maximum_dimensionless_residual": 1.0e-8,
    "minimum_simplex_weight": 0.03,
    "minimum_absolute_scaled_fourth_derivative": 5.0,
    "minimum_projected_second_singular_value": 0.5,
    "minimum_projected_singular_value_ratio": 0.05,
    "minimum_full_jacobian_singular_value": 0.25,
    "maximum_determinant_factorization_relative_residual": 1.0e-9,
    "maximum_explicit_action_residual": 1.0e-11,
    "maximum_mixed_jet_disagreement": 1.0e-6,
}
PREFLIGHT = {
    "small_explicit_csr_cells": 7,
    "row_and_column_actions": True,
    "augmented_row_and_column_actions": True,
    "maximum_action_residual": 1.0e-11,
    "formal_replica_runs_preflight_before_scientific_meshes": True,
}
ROOT_SEARCH = {
    "time_window": [0.5, 35.0],
    "mesh_65_spacing": 0.05,
    "mesh_97_spacing": 0.05,
    "chunk_points": 11,
    "saved_trace_spacing": 0.50,
    "brent_absolute_tolerance": 1.0e-11,
    "brent_relative_tolerance": 4.0e-15,
    "maximum_brent_iterations": 100,
    "relative_density_floor": 1.0e-8,
    "maximum_scaled_root_residual": 1.0e-8,
    "minimum_absolute_scaled_curvature": 0.05,
    "minimum_root_separation": 0.25,
    "cusp_exclusion_radius": 0.25,
    "endpoint_signs": ["positive_at_0.5", "negative_at_35"],
}
REMOTE_PAIR = {
    "ordered_types": ["maximum", "minimum"],
    "same_side_of_cusp_required": True,
    "minimum_root_separation": 0.25,
    "cusp_exclusion_radius": 0.25,
    "minimum_absolute_scaled_curvature": 0.05,
    "maximum_adjacent_root_time_drift": 1.0,
    "lineage_anchor": "cusp stationary scan",
    "lineage_rule": (
        "fixed eligible-root count, global ordinal, type, signed side, origin bracket, "
        "and order-preserving predecessor/successor continuation"
    ),
    "birth_death_crossing_unmatched_or_excess_drift": "HOLD_BRANCH",
}
FOLD_CONTINUATION = {
    "predictor_time_offsets": [-0.10, 0.10],
    "predictor_equations": [
        "R1 eta = f_tttt tau^3 / 3",
        "R2 eta = -f_tttt tau^2 / 2",
    ],
    "fixed_time_seed_correction": True,
    "initial_arclength_step": 0.05,
    "minimum_arclength_step": 0.025,
    "maximum_arclength_step": 0.20,
    "step_increase_factor": 2.0,
    "increase_if_iterations_at_most": 3,
    "step_decrease_factor": 0.5,
    "decrease_if_iterations_at_least": 8,
    "retry_once_at_half_step_after_failure": True,
    "maximum_accepted_noncusp_nodes": 24,
    "stop_absolute_time_offset": 2.0,
    "required_absolute_time_reach": 0.75,
    "minimum_accepted_noncusp_nodes": 6,
    "comparison_time_offsets": [0.25, 0.50, 0.75],
    "maximum_comparison_time_offset_mismatch": 0.125,
    "comparison_selection_rule": (
        "signed-side ordered greedy nearest-node selection without replacement"
    ),
    "comparison_node_tie_break": [
        "smallest absolute offset mismatch",
        "smallest normalized residual",
        "earliest acceptance index",
    ],
    "maximum_normalized_fold_residual": 1.0e-8,
    "minimum_scaled_third_derivative": 0.10,
    "minimum_dimensionless_fold_singular_value": 0.05,
    "remote_pair_checked_at_each_comparison_node": True,
}
PHASE_SEARCH = {
    "centre": "mesh_97 positive-B cusp theta",
    "centre_formula_absolute_tolerance": 5.0e-13,
    "radii": [0.02, 0.05, 0.09, 0.13],
    "directions": [
        [1.0, 0.0],
        [0.7071067811865476, 0.7071067811865476],
        [0.0, 1.0],
        [-0.7071067811865476, 0.7071067811865476],
        [-1.0, 0.0],
        [-0.7071067811865476, -0.7071067811865476],
        [0.0, -1.0],
        [0.7071067811865476, -0.7071067811865476],
    ],
    "candidate_count": 32,
    "screen_mesh": 65,
    "advance_mesh": 97,
    "maximum_advanced_per_mode_count": 3,
    "target_retained_maximum_counts": [1, 2, 3],
    "final_time": 100.0,
    "score_terms": [
        "peak_ratio",
        "valley_ratio",
        "absolute_scaled_curvature",
        "event_basin_mass",
    ],
    "root_residual_role": "eligibility_gate_not_ranking_term",
    "score_formulas": {
        "lower_bound_margin": "value / lower_bound - 1",
        "upper_bound_margin": "(upper_bound - value) / (1 - upper_bound)",
        "worst_control_score": "minimum of the four ordered score-term margins",
    },
    "ranking_tie_break": "lexicographically increasing physical weight vector",
    "representative_rule": "maximum worst score over meshes 65 and 97",
    "wrong_endpoint_signs_ineligible": True,
    "out_of_trust_or_simplex_candidates_discarded": True,
    "radius_expansion_forbidden": True,
}
REPRESENTATIVE_GATES = {
    "minimum_peak_ratio": 0.10,
    "maximum_valley_ratio": 0.85,
    "minimum_absolute_scaled_curvature": 0.05,
    "maximum_scaled_root_residual": 1.0e-8,
    "minimum_each_event_basin_mass": 0.005,
    "maximum_negative_state_tolerance": 1.0e-12,
    "maximum_survival_increase": 1.0e-12,
    "minimum_density": 0.0,
    "minimum_survival": 0.0,
    "maximum_initial_mass_error": 1.0e-12,
    "maximum_installed_budget_error": 1.0e-12,
    "maximum_survival_identity_error": 1.0e-9,
    "maximum_generator_killing_identity_error": 1.0e-9,
    "maximum_differential_mass_balance_error": 1.0e-9,
    "maximum_event_partition_closure_error": 1.0e-9,
    "tail_checkpoints": [35.0, 50.0, 75.0, 100.0],
}
REPRODUCIBILITY = {
    "numpy_global_seed": 1618033,
    "restore_numpy_global_rng_state": True,
    "python_hash_mode": "isolated_randomized_per_process",
    "python_ignore_environment_required": True,
    "python_hash_randomization_required": True,
    "unordered_boundary_rule": "explicit_sort_before_numeric_or_serialized_use",
    "independent_full_processes_required": 2,
    "execution_order": "sequential",
    "byte_identical_results_required": True,
    "external_manifest_sha256_required": True,
    "canonical_promotion_only_after_replica_comparison": True,
    "subprocess_environment": {
        "PYTHONNOUSERSITE": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    },
}
FAILURE_CONTRACT = {
    "scientific_failure_status": HOLD_STATUS,
    "operational_exception_may_promote_output": False,
    "structural_failure_uses_null": True,
    "nonfinite_json_forbidden": True,
    "missing_mesh_rows_forbidden": True,
    "later_mesh_after_earlier_hold": "NOT_RUN_AFTER_HOLD",
    "search_expansion_after_hold_forbidden": True,
}
EXECUTION_BOUNDARY = {
    "formal_flag": "--execute-frozen",
    "replica_flag": "--execute-replica",
    "dry_run_flag": "--algebra-dry-run",
    "scientific_meshes": [65, 97],
    "dry_run_maximum_cells": DRY_RUN_MAX_CELLS,
    "canonical_result_path": "artifacts/data/positive_b_allocation_cusp_discovery_result.json",
    "reproducibility_path": (
        "artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json"
    ),
    "canonical_and_evidence_staged_fsync_no_replace_install": True,
    "rollback_only_outputs_created_by_this_invocation": True,
    "manifest_rechecked_before_and_after_each_replica": True,
    "all_pins_rechecked_before_and_after_each_replica": True,
    "all_pins_rechecked_before_and_after_promotion": True,
    "canonical_bytes_reread_after_final_directory_fsync": True,
    "scientific_meshes_built_and_run_sequentially": True,
    "formal_result_absent_at_freeze": True,
    "first_replica_complete_five_path_absence_required": True,
    "per_replica_exact_allowed_path_and_staging_boundary_required": True,
    "isolated_python_flag_required_for_replicas": True,
    "no_site_python_flag_required_for_formal_parent_and_replicas": True,
    "dont_write_bytecode_flag_required_for_formal_parent_and_replicas": True,
    "absolute_repository_site_packages_bootstrap_required": True,
    "python_and_native_loader_injection_environment_forbidden": True,
    "python_stdlib_and_distribution_record_closure_required": True,
    "stdlib_closure_includes_pyc_and_symlink_metadata": True,
    "numpy_scipy_import_trees_include_all_pyc_and_unrecorded_files": True,
    "stdlib_attestation_is_reproducibility_not_hostile_bootstrap_prevention": True,
    "numpy_scipy_native_extension_closure_required": True,
    "bounded_non_system_native_image_closure_required": True,
    "non_system_native_phase_exact_set_required": True,
    "python_hash_randomization_under_isolation_required": True,
    "signed_system_dyld_cache_attestation_required": True,
    "numpy_build_configuration_exactly_bound": True,
    "runtime_closure_rebuilt_before_third_party_import_in_each_formal_process": True,
    "runtime_modules_bound_to_absolute_pinned_descriptors": True,
    "silent_canonical_or_audit_deletion_forbidden": True,
    "lexical_lstat_regular_files_required": True,
    "open_nofollow_required": True,
    "stable_file_descriptor_snapshot_required": True,
    "complete_initial_final_metadata_and_bytes_snapshot_required": True,
    "no_concurrent_writer_contract": True,
    "no_onedrive_replacement_during_execution_contract": True,
}

ISOLATED_RUNNER_BOOTSTRAP = """\
import ctypes
import hashlib
import importlib
import json
import os
import runpy
import stat
import sys

runner, site_packages, *arguments = sys.argv[1:]
if sys.flags.isolated != 1 or sys.flags.no_site != 1 or not sys.dont_write_bytecode:
    raise SystemExit("formal bootstrap requires -I -S -B")
if not os.path.isabs(runner) or not os.path.isabs(site_packages):
    raise SystemExit("formal bootstrap paths must be absolute")
if "sitecustomize" in sys.modules or "usercustomize" in sys.modules:
    raise SystemExit("formal bootstrap loaded a customization module")

def stable_bytes(path):
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise SystemExit("formal bootstrap input is not a regular file")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        closed = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after = os.lstat(path)
    identities = {
        (item.st_dev, item.st_ino, item.st_mode, item.st_size, item.st_mtime_ns)
        for item in (before, opened, closed, after)
    }
    if len(identities) != 1:
        raise SystemExit("formal bootstrap input changed during capture")
    payload = b"".join(chunks)
    if len(payload) != before.st_size:
        raise SystemExit("formal bootstrap input was read short")
    return payload

def closure_digest(rows):
    digest = hashlib.sha256()
    for name, file_hash in sorted(rows):
        digest.update(name.encode("utf-8"))
        digest.update(b"\\0")
        digest.update(file_hash.encode("utf-8"))
        digest.update(b"\\n")
    return digest.hexdigest()

def tree_closure(root, file_hash_cache=None):
    try:
        root_metadata = os.lstat(root)
    except FileNotFoundError:
        return {
            "present": False,
            "entry_count": 0,
            "regular_file_count": 0,
            "pyc_file_count": 0,
            "symlink_count": 0,
            "closure_sha256": closure_digest([]),
        }
    if stat.S_ISLNK(root_metadata.st_mode) or not stat.S_ISDIR(root_metadata.st_mode):
        raise SystemExit("formal bootstrap import-tree root is not a lexical directory")
    cache = file_hash_cache if file_hash_cache is not None else {}
    rows = []
    regular_count = 0
    pyc_count = 0
    symlink_count = 0
    for directory, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        kept_directories = []
        for name in sorted(directory_names):
            path = os.path.join(directory, name)
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode):
                relative = os.path.relpath(path, root).replace(os.sep, "/")
                rows.append(
                    (
                        relative,
                        f"L:{metadata.st_mode}:{metadata.st_size}:{os.readlink(path)}",
                    )
                )
                symlink_count += 1
                continue
            if not stat.S_ISDIR(metadata.st_mode):
                raise SystemExit("formal bootstrap import tree contains a non-directory")
            kept_directories.append(name)
        directory_names[:] = kept_directories
        for name in sorted(file_names):
            path = os.path.join(directory, name)
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode):
                relative = os.path.relpath(path, root).replace(os.sep, "/")
                rows.append(
                    (
                        relative,
                        f"L:{metadata.st_mode}:{metadata.st_size}:{os.readlink(path)}",
                    )
                )
                symlink_count += 1
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit("formal bootstrap import tree contains a special file")
            relative = os.path.relpath(path, root).replace(os.sep, "/")
            file_hash = cache.get(path)
            if file_hash is None:
                file_hash = hashlib.sha256(stable_bytes(path)).hexdigest()
                cache[path] = file_hash
            rows.append(
                (
                    relative,
                    f"F:{metadata.st_mode}:{metadata.st_size}:{file_hash}",
                )
            )
            regular_count += 1
            pyc_count += int(name.endswith(".pyc"))
    return {
        "present": True,
        "entry_count": len(rows),
        "regular_file_count": regular_count,
        "pyc_file_count": pyc_count,
        "symlink_count": symlink_count,
        "closure_sha256": closure_digest(rows),
    }

def lexical_regular_under(root, path):
    root = os.path.abspath(root)
    path = os.path.abspath(os.path.normpath(path))
    if os.path.commonpath((root, path)) != root or path == root:
        raise SystemExit("formal bootstrap package path escapes the frozen venv")
    current = root
    parts = os.path.relpath(path, root).split(os.sep)
    for index, part in enumerate(parts):
        current = os.path.join(current, part)
        metadata = os.lstat(current)
        if stat.S_ISLNK(metadata.st_mode):
            raise SystemExit("formal bootstrap package path contains a symlink")
        expected = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not expected(metadata.st_mode):
            raise SystemExit("formal bootstrap package path has the wrong file type")
    return stable_bytes(path)

if arguments.count("--expected-manifest-sha256") != 1:
    raise SystemExit("formal bootstrap requires one external manifest hash")
hash_index = arguments.index("--expected-manifest-sha256")
if hash_index + 1 >= len(arguments):
    raise SystemExit("formal bootstrap manifest hash value is missing")
expected_manifest_hash = arguments[hash_index + 1]
report = os.path.dirname(os.path.dirname(runner))
repository = os.path.realpath(os.path.join(os.path.dirname(runner), "../../../.."))
manifest_path = os.path.join(
    report, "artifacts", "data", "positive_b_allocation_cusp_discovery_manifest.json"
)
manifest_bytes = stable_bytes(manifest_path)
if hashlib.sha256(manifest_bytes).hexdigest() != expected_manifest_hash:
    raise SystemExit("formal bootstrap external manifest hash mismatch")
manifest = json.loads(manifest_bytes)
provenance = manifest.get("runtime_provenance")
if not isinstance(provenance, dict) or provenance.get("contract") != "bounded_runtime_closure_v2":
    raise SystemExit("formal bootstrap runtime provenance is missing")
runner_pin = manifest["pinned_files"]["runner"]
expected_runner = os.path.realpath(os.path.join(report, runner_pin["path"]))
runner_bytes = stable_bytes(runner)
if (
    os.path.realpath(runner) != expected_runner
    or hashlib.sha256(runner_bytes).hexdigest() != runner_pin["sha256"]
):
    raise SystemExit("formal bootstrap runner pin mismatch")
expected_site = os.path.realpath(
    os.path.join(
        repository,
        ".venv",
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        "site-packages",
    )
)
if os.path.realpath(site_packages) != expected_site or not os.path.isdir(expected_site):
    raise SystemExit("formal bootstrap repository site-packages mismatch")

python_provenance = provenance.get("python")
if not isinstance(python_provenance, dict):
    raise SystemExit("formal bootstrap Python provenance is malformed")
real_executable = os.path.realpath(sys.executable)
expected_stdlib = os.path.realpath(
    os.path.join(
        sys.base_prefix,
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
    )
)
if (
    python_provenance.get("version") != sys.version
    or python_provenance.get("cache_tag") != sys.implementation.cache_tag
    or python_provenance.get("invocation_path") != os.path.abspath(sys.executable)
    or python_provenance.get("real_executable_path") != real_executable
    or python_provenance.get("stdlib_root") != expected_stdlib
):
    raise SystemExit("formal bootstrap Python identity mismatch")
if (
    hashlib.sha256(stable_bytes(real_executable)).hexdigest()
    != python_provenance.get("real_executable_sha256")
):
    raise SystemExit("formal bootstrap Python executable hash mismatch")
if tree_closure(expected_stdlib) != python_provenance.get("stdlib_closure"):
    raise SystemExit("formal bootstrap stdlib closure mismatch")
framework_files = python_provenance.get("framework_files")
if not isinstance(framework_files, dict) or not framework_files:
    raise SystemExit("formal bootstrap Python framework closure is malformed")
for path, expected_hash in framework_files.items():
    if not os.path.isabs(path) or hashlib.sha256(stable_bytes(path)).hexdigest() != expected_hash:
        raise SystemExit("formal bootstrap Python framework hash mismatch")

venv_root = os.path.realpath(os.path.join(repository, ".venv"))
if (
    provenance.get("venv_root") != venv_root
    or provenance.get("site_packages") != expected_site
):
    raise SystemExit("formal bootstrap frozen venv identity mismatch")

import csv
import io

def distribution_closure(record_path, file_hash_cache):
    record_bytes = lexical_regular_under(venv_root, record_path)
    try:
        records = list(csv.reader(io.StringIO(record_bytes.decode("utf-8"), newline="")))
    except (UnicodeDecodeError, csv.Error) as error:
        raise SystemExit("formal bootstrap package RECORD is malformed") from error
    rows = []
    native_rows = []
    seen = set()
    for record in records:
        if len(record) != 3 or not record[0]:
            raise SystemExit("formal bootstrap package RECORD row is malformed")
        path = os.path.abspath(os.path.normpath(os.path.join(expected_site, record[0])))
        relative = os.path.relpath(path, venv_root).replace(os.sep, "/")
        if relative in seen:
            raise SystemExit("formal bootstrap package RECORD contains a duplicate path")
        seen.add(relative)
        file_hash = file_hash_cache.get(path)
        if file_hash is None:
            file_hash = hashlib.sha256(lexical_regular_under(venv_root, path)).hexdigest()
            file_hash_cache[path] = file_hash
        rows.append((relative, file_hash))
        if relative.endswith((".so", ".dylib", ".pyd", ".dll")):
            native_rows.append((relative, file_hash))
    return {
        "record_file_count": len(rows),
        "record_sha256": hashlib.sha256(record_bytes).hexdigest(),
        "record_closure_sha256": closure_digest(rows),
        "native_extension_count": len(native_rows),
        "native_extension_closure_sha256": closure_digest(native_rows),
    }

distributions = provenance.get("distributions")
if not isinstance(distributions, dict) or set(distributions) != {"numpy", "scipy"}:
    raise SystemExit("formal bootstrap distribution provenance is malformed")
for distribution_name, distribution in distributions.items():
    record_path = distribution.get("record_path")
    file_hash_cache = {}
    observed_trees = {}
    expected_trees = distribution.get("import_tree_closures")
    if (
        not isinstance(expected_trees, dict)
        or set(expected_trees) != {distribution_name, f"{distribution_name}.libs"}
    ):
        raise SystemExit("formal bootstrap import-tree provenance is malformed")
    for root_name, expected_tree in expected_trees.items():
        if not isinstance(root_name, str) or not isinstance(expected_tree, dict):
            raise SystemExit("formal bootstrap import-tree row is malformed")
        root_path = expected_tree.get("path")
        expected_root_path = os.path.join(expected_site, root_name)
        if not isinstance(root_path, str) or root_path != expected_root_path:
            raise SystemExit("formal bootstrap import-tree path is malformed")
        observed_trees[root_name] = {"path": root_path, **tree_closure(root_path, file_hash_cache)}
    if observed_trees != expected_trees:
        raise SystemExit("formal bootstrap import-tree exact-set closure mismatch")
    expected_closure = {
        key: distribution.get(key)
        for key in (
            "record_file_count",
            "record_sha256",
            "record_closure_sha256",
            "native_extension_count",
            "native_extension_closure_sha256",
        )
    }
    if (
        not isinstance(record_path, str)
        or distribution_closure(record_path, file_hash_cache) != expected_closure
    ):
        raise SystemExit("formal bootstrap distribution RECORD closure mismatch")

system_native = provenance.get("system_native")
if not isinstance(system_native, dict):
    raise SystemExit("formal bootstrap system-native provenance is malformed")
codesign_tool = system_native.get("codesign_tool")
if (
    not isinstance(codesign_tool, dict)
    or codesign_tool.get("path") != "/usr/bin/codesign"
    or hashlib.sha256(stable_bytes(codesign_tool["path"])).hexdigest()
    != codesign_tool.get("sha256")
):
    raise SystemExit("formal bootstrap codesign tool mismatch")

import subprocess

cache_rows = system_native.get("dyld_cache_code_directories")
if not isinstance(cache_rows, list) or not cache_rows:
    raise SystemExit("formal bootstrap dyld cache provenance is malformed")
cache_root = system_native.get("dyld_cache_root")
expected_cache_paths = {row.get("path") for row in cache_rows if isinstance(row, dict)}
observed_cache_paths = set()
cache_prefix = "dyld_shared_cache_arm64e"
for name in os.listdir(cache_root):
    suffix = name[len(cache_prefix):] if name.startswith(cache_prefix) else ""
    if name == cache_prefix or (
        suffix.startswith(".") and suffix[1:].split(".", 1)[0].isdigit()
    ):
        observed_cache_paths.add(os.path.join(cache_root, name))
if observed_cache_paths != expected_cache_paths:
    raise SystemExit("formal bootstrap dyld cache file set mismatch")
codesign_environment = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
for row in cache_rows:
    path = row.get("path")
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise SystemExit("formal bootstrap dyld cache is not a regular file")
    verified = subprocess.run(
        [codesign_tool["path"], "--verify", "--strict", path],
        env=codesign_environment,
        check=False,
        capture_output=True,
        text=True,
    )
    described = subprocess.run(
        [codesign_tool["path"], "-dvvv", path],
        env=codesign_environment,
        check=False,
        capture_output=True,
        text=True,
    )
    after = os.lstat(path)
    identity_before = (before.st_dev, before.st_ino, before.st_mode, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_mode, after.st_size, after.st_mtime_ns)
    full_hashes = [
        line.split("=", 1)[1]
        for line in (described.stdout + described.stderr).splitlines()
        if line.startswith("CandidateCDHashFull sha256=")
    ]
    if (
        verified.returncode != 0
        or described.returncode != 0
        or identity_before != identity_after
        or row.get("size") != before.st_size
        or full_hashes != [row.get("candidate_cdhash_full_sha256")]
    ):
        raise SystemExit("formal bootstrap signed dyld cache attestation mismatch")

non_system_native = provenance.get("non_system_native")
native_phases = (
    "bootstrap_pre_third_party",
    "runner_post_import",
    "post_manifest_validation",
    "full_stack_post_import",
)
system_prefixes = (
    "/System/Library/",
    "/usr/lib/",
    "/System/Volumes/Preboot/Cryptexes/OS/System/Library/",
)
if (
    not isinstance(non_system_native, dict)
    or non_system_native.get("contract") != "bounded_non_system_macho_closure_v1"
    or non_system_native.get("threat_boundary")
    != "reproducibility_witness_not_malicious_same_uid_prevention"
    or non_system_native.get("bootstrap_root_of_trust_includes_hash_primitive") is not True
    or non_system_native.get("probe_induced_images_included") != ["ctypes", "_ctypes"]
    or non_system_native.get("system_leaf_prefixes") != list(system_prefixes)
):
    raise SystemExit("formal bootstrap non-system native provenance is malformed")

def is_system_native(path):
    return any(path.startswith(prefix) for prefix in system_prefixes)

def loaded_non_system_images():
    dyld = ctypes.CDLL(None)
    dyld._dyld_image_count.restype = ctypes.c_uint32
    dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    rows = {}
    for index in range(int(dyld._dyld_image_count())):
        encoded = dyld._dyld_get_image_name(index)
        if not encoded:
            continue
        lexical = os.fsdecode(encoded)
        if not os.path.isabs(lexical):
            raise SystemExit("formal bootstrap dyld image path is not absolute")
        resolved = os.path.realpath(lexical)
        if is_system_native(lexical) or is_system_native(resolved):
            continue
        row = {"lexical_path": lexical, "resolved_path": resolved}
        previous = rows.setdefault(resolved, row)
        if previous != row:
            raise SystemExit("formal bootstrap dyld image alias changed")
    return [rows[key] for key in sorted(rows)]

phase_images = non_system_native.get("phase_images")
if not isinstance(phase_images, dict) or set(phase_images) != set(native_phases):
    raise SystemExit("formal bootstrap native phase map is malformed")
phase_sets = {}
previous_phase = set()
for phase in native_phases:
    phase_rows = phase_images.get(phase)
    if not isinstance(phase_rows, list) or not phase_rows:
        raise SystemExit("formal bootstrap native phase is empty")
    resolved_order = []
    for row in phase_rows:
        if (
            not isinstance(row, dict)
            or set(row) != {"lexical_path", "resolved_path"}
            or not isinstance(row.get("lexical_path"), str)
            or not isinstance(row.get("resolved_path"), str)
            or not os.path.isabs(row["lexical_path"])
            or not os.path.isabs(row["resolved_path"])
            or os.path.realpath(row["lexical_path"]) != row["resolved_path"]
            or is_system_native(row["lexical_path"])
            or is_system_native(row["resolved_path"])
        ):
            raise SystemExit("formal bootstrap native phase row is malformed")
        resolved_order.append(row["resolved_path"])
    if resolved_order != sorted(set(resolved_order)):
        raise SystemExit("formal bootstrap native phase is not uniquely sorted")
    phase_sets[phase] = set(resolved_order)
    if not previous_phase.issubset(phase_sets[phase]):
        raise SystemExit("formal bootstrap native phases are not monotone")
    previous_phase = phase_sets[phase]
if loaded_non_system_images() != phase_images["bootstrap_pre_third_party"]:
    raise SystemExit("formal bootstrap pre-third-party native image set changed")

transition_causes = non_system_native.get("phase_transition_causes")
transition_added = [
    row
    for row in phase_images["post_manifest_validation"]
    if row not in phase_images["runner_post_import"]
]
if (
    not isinstance(transition_causes, dict)
    or set(transition_causes) != {"post_manifest_validation"}
    or transition_causes["post_manifest_validation"]
    != {
        "operation": "signed_dyld_cache_provenance.platform.mac_ver",
        "added_images": transition_added,
    }
    or len(transition_added) != 1
    or not os.path.basename(transition_added[0]["resolved_path"]).startswith("pyexpat.")
):
    raise SystemExit("formal bootstrap native phase-transition cause changed")

main_image = non_system_native.get("main_executable_image")
if (
    not isinstance(main_image, dict)
    or set(main_image) != {"lexical_path", "resolved_path"}
    or main_image not in phase_images["bootstrap_pre_third_party"]
):
    raise SystemExit("formal bootstrap main native image is malformed")
native_executable = main_image["resolved_path"]
otool = non_system_native.get("otool")
if (
    not isinstance(otool, dict)
    or set(otool) != {"path", "sha256"}
    or otool.get("path") != "/usr/bin/otool"
    or hashlib.sha256(stable_bytes(otool["path"])).hexdigest() != otool.get("sha256")
):
    raise SystemExit("formal bootstrap otool provenance mismatch")

def macho_commands(path):
    completed = subprocess.run(
        [otool["path"], "-l", path],
        env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit("formal bootstrap otool inspection failed")
    lines = completed.stdout.splitlines()
    install_names = []
    rpaths = []
    dependencies = []
    load_commands = {
        "LC_LOAD_DYLIB",
        "LC_LOAD_WEAK_DYLIB",
        "LC_REEXPORT_DYLIB",
        "LC_LOAD_UPWARD_DYLIB",
    }
    for index, line in enumerate(lines):
        command = line.strip()
        if command == "cmd LC_ID_DYLIB":
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("name "):
                    install_names.append(item[5:].split(" (offset ", 1)[0])
                    break
        elif command.removeprefix("cmd ") in load_commands:
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("name "):
                    dependencies.append(item[5:].split(" (offset ", 1)[0])
                    break
        elif command == "cmd LC_RPATH":
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("path "):
                    rpaths.append(item[5:].split(" (offset ", 1)[0])
                    break
    unique_install_names = sorted(set(install_names))
    if len(unique_install_names) > 1:
        raise SystemExit("formal bootstrap native install names disagree")
    return (
        unique_install_names[0] if unique_install_names else None,
        list(dict.fromkeys(rpaths)),
        sorted(set(dependencies)),
    )

def expand_anchor(value, loader):
    if value == "@loader_path":
        return os.path.dirname(loader)
    if value.startswith("@loader_path/"):
        return os.path.join(os.path.dirname(loader), value[len("@loader_path/") :])
    if value == "@executable_path":
        return os.path.dirname(native_executable)
    if value.startswith("@executable_path/"):
        return os.path.join(
            os.path.dirname(native_executable), value[len("@executable_path/") :]
        )
    if os.path.isabs(value):
        return value
    raise SystemExit("formal bootstrap unsupported Mach-O path anchor")

def resolve_dependency(install_name, loader, rpaths):
    if is_system_native(install_name):
        return {
            "install_name": install_name,
            "classification": "system_dyld_cache",
            "lexical_path": install_name,
            "resolved_path": None,
        }
    if install_name.startswith("@rpath/"):
        suffix = install_name[len("@rpath/") :]
        candidates = []
        for rpath in rpaths:
            candidate = os.path.abspath(
                os.path.normpath(os.path.join(expand_anchor(rpath, loader), suffix))
            )
            if os.path.lexists(candidate):
                candidates.append(candidate)
        if not candidates:
            raise SystemExit("formal bootstrap unresolved @rpath dependency")
        lexical = candidates[0]
    else:
        lexical = os.path.abspath(os.path.normpath(expand_anchor(install_name, loader)))
    resolved = os.path.realpath(lexical)
    if is_system_native(lexical) or is_system_native(resolved):
        return {
            "install_name": install_name,
            "classification": "system_dyld_cache",
            "lexical_path": lexical,
            "resolved_path": None,
        }
    if not os.path.lexists(lexical):
        raise SystemExit("formal bootstrap non-system dependency is absent")
    return {
        "install_name": install_name,
        "classification": "non_system",
        "lexical_path": lexical,
        "resolved_path": resolved,
    }

image_rows = non_system_native.get("images")
if (
    not isinstance(image_rows, list)
    or non_system_native.get("closure_image_count") != len(image_rows)
    or not image_rows
):
    raise SystemExit("formal bootstrap native closure rows are malformed")
expected_image_keys = {
    "resolved_path",
    "lexical_paths",
    "install_name",
    "size",
    "sha256",
    "rpaths",
    "dependencies",
    "actual_loaded_phases",
}
row_map = {}
observed_aliases = {}
observed_metadata = {}
for phase in native_phases:
    for row in phase_images[phase]:
        observed_aliases.setdefault(row["resolved_path"], set()).add(row["lexical_path"])
for row in image_rows:
    if (
        not isinstance(row, dict)
        or set(row) != expected_image_keys
        or not isinstance(row.get("resolved_path"), str)
        or row["resolved_path"] in row_map
        or not os.path.isabs(row["resolved_path"])
        or is_system_native(row["resolved_path"])
    ):
        raise SystemExit("formal bootstrap native closure row is malformed")
    path = row["resolved_path"]
    payload = stable_bytes(path)
    if len(payload) != row.get("size") or hashlib.sha256(payload).hexdigest() != row.get("sha256"):
        raise SystemExit("formal bootstrap native image bytes changed")
    install_name, rpaths, raw_dependencies = macho_commands(path)
    dependencies = sorted(
        [resolve_dependency(name, path, rpaths) for name in raw_dependencies],
        key=lambda item: (
            item["install_name"],
            item["lexical_path"],
            item["resolved_path"] or "",
        ),
    )
    for dependency in dependencies:
        if dependency["resolved_path"] is not None:
            observed_aliases.setdefault(dependency["resolved_path"], set()).add(
                dependency["lexical_path"]
            )
    actual_phases = [phase for phase in native_phases if path in phase_sets[phase]]
    observed_metadata[path] = {
        "install_name": install_name,
        "rpaths": rpaths,
        "dependencies": dependencies,
        "actual_loaded_phases": actual_phases,
    }
    row_map[path] = row
if list(row_map) != sorted(row_map):
    raise SystemExit("formal bootstrap native closure is not path-sorted")
for path, row in row_map.items():
    aliases = row.get("lexical_paths")
    if (
        not isinstance(aliases, list)
        or aliases != sorted(set(aliases))
        or aliases != sorted(observed_aliases.get(path, {path}))
        or any(os.path.realpath(alias) != path for alias in aliases)
        or row.get("install_name") != observed_metadata[path]["install_name"]
        or row.get("rpaths") != observed_metadata[path]["rpaths"]
        or row.get("dependencies") != observed_metadata[path]["dependencies"]
        or row.get("actual_loaded_phases") != observed_metadata[path]["actual_loaded_phases"]
    ):
        raise SystemExit("formal bootstrap native image graph changed")
    for dependency in row["dependencies"]:
        target = dependency["resolved_path"]
        if target is not None and target not in row_map:
            raise SystemExit("formal bootstrap native dependency escapes the closure")
reachable = set(phase_sets["full_stack_post_import"])
pending = sorted(reachable)
while pending:
    path = pending.pop(0)
    if path not in row_map:
        raise SystemExit("formal bootstrap loaded native image is absent from closure")
    for dependency in row_map[path]["dependencies"]:
        target = dependency["resolved_path"]
        if target is not None and target not in reachable:
            reachable.add(target)
            pending.append(target)
            pending.sort()
if reachable != set(row_map):
    raise SystemExit("formal bootstrap native closure contains unreachable rows")
encoded_image_rows = json.dumps(
    image_rows, allow_nan=False, separators=(",", ":"), sort_keys=True
).encode("utf-8")
if hashlib.sha256(encoded_image_rows).hexdigest() != non_system_native.get("closure_sha256"):
    raise SystemExit("formal bootstrap native closure digest changed")

sys.path.append(expected_site)
sys.argv = [runner, *arguments]
runpy.run_path(runner, run_name="__main__")
"""
CLAIM_FLAGS = {
    "low_mesh_discovery_completed": False,
    "heldout_mesh_confirmation_verified": False,
    "parity_verified": False,
    "box_robustness_verified": False,
    "continuum_interval_verified": False,
    "unbounded_domain_verified": False,
    "independent_solver_verified": False,
    "publication_gate_passed": False,
}
FORBIDDEN_CLAIMS = [
    "held-out mesh confirmation",
    "mesh convergence",
    "parity robustness",
    "box or unbounded-domain robustness",
    "continuum cusp existence",
    "global exact modal count",
    "independent-solver verification",
    "publication gate pass",
]
LIMITATIONS = [
    "meshes 65 and 97 are two same-family discovery meshes; mesh 97 is not held out",
    "same finite-volume solver family and one fixed box",
    "no held-out parity, box, continuum, or independent-solver evidence",
    "retained-window modes are not a global exact-count theorem",
    "PASS_DISCOVERY_LOW_MESH_ONLY is not a manuscript confirmation or publication pass",
]
CONTROL_GATE_NAMES = (
    "alternating_topology",
    "endpoint_signs",
    "peak_ratio",
    "valley_ratio",
    "curvature",
    "root_residual",
    "event_masses",
    "positive_density_and_survival",
    "survival_monotone",
    "sampled_state_nonnegative",
    "sampled_survival_monotone",
    "survival_density_identity",
    "generator_killing_identity",
    "differential_mass_balance",
    "event_partition_closure",
    "final_state_nonnegative",
    "initial_mass",
    "installed_budget",
    "finite_factor_diagnostics",
)
SCAN_PHYSICAL_GATE_NAMES = (
    "positive_density_and_survival",
    "state_nonnegative",
    "sampled_survival_monotone",
    "survival_density_identity",
    "generator_killing_identity",
    "differential_mass_balance",
    "initial_mass",
    "installed_budget",
    "finite_factor_diagnostics",
    "all_bracketed_roots_physical",
)
BRANCH_GATE_NAMES = (
    "minimum_nodes",
    "required_reach",
    "comparison_nodes_present",
    "comparison_nodes_distinct",
    "comparison_nodes_on_signed_side",
    "comparison_offset_mismatch",
    "fold_residuals",
    "third_derivative",
    "fold_rank",
    "physical_law",
    "comparison_scan_physical_law",
    "remote_pair_retained",
    "stable_remote_pair_identity",
    "remote_pair_lineage",
)
PIN_PATHS = {
    "runner": "code/positive_b_allocation_cusp_discovery.py",
    "tests": "code/test_positive_b_allocation_cusp_discovery.py",
    "round_50_attack_tests": "code/test_positive_b_allocation_cusp_discovery_round50.py",
    "round_61_attack_tests": "code/test_positive_b_allocation_cusp_discovery_round61.py",
    "round_74_prerun_attack": "audits/round_74_allocation_v3_independent_prerun_attack.md",
    "round_74_attack_tests": "code/test_positive_b_allocation_cusp_discovery_round74.py",
    "round_80_prerun_attack": "audits/round_80_allocation_v4_independent_prerun_attack.md",
    "round_80_attack_tests": "code/test_positive_b_allocation_cusp_discovery_round80.py",
    "round_84_prerun_attack": "audits/round_84_allocation_v5_independent_prerun_attack.md",
    "round_85_repair_tests": "code/test_positive_b_allocation_cusp_discovery_round85.py",
    "protocol": "notes/positive_b_allocation_cusp_discovery_protocol.md",
    "stage_a_scaffold": "code/positive_b_allocation_cusp_stage_a.py",
    "stage_a_tests": "code/test_positive_b_allocation_cusp_stage_a.py",
    "promotion_design": "notes/positive_b_allocation_cusp_promotion_design.md",
    "round_36_design_attack": "audits/round_36_allocation_cusp_design_attack.md",
    "round_44_scaffold_attack": "audits/round_44_allocation_cusp_stage_a_code_attack.md",
    "round_50_prerun_attack": "audits/round_50_allocation_discovery_prerun_attack.md",
    "round_61_prerun_attack": "audits/round_61_allocation_v2_independent_prerun_attack.md",
    "positive_B_v2_manifest": "artifacts/data/positive_b_broad_four_slab_manifest.json",
    "positive_B_v2_protocol": "notes/positive_b_broad_four_slab_protocol.md",
    "positive_B_v2_producer": "code/positive_b_broad_four_slab.py",
    "B0_bridge_result": "artifacts/data/continuum_broad_patch_b0_bridge_result.json",
    "B0_bridge_manifest": "artifacts/data/continuum_broad_patch_b0_bridge_manifest.json",
    "B0_bridge_producer": "code/continuum_broad_patch_b0_bridge.py",
    "finite_volume_dependency": "code/continuum_weak_budget_design.py",
    "grid_dependency": "code/continuum_g1_smoke.py",
    "continuum_runtime_dependency": "code/continuum_observable_four_patch.py",
}

RUNTIME_MODULE_PINS = (
    ("continuum_g1_smoke", "grid_dependency"),
    ("continuum_observable_four_patch", "continuum_runtime_dependency"),
    ("continuum_weak_budget_design", "finite_volume_dependency"),
    ("continuum_broad_patch_b0_bridge", "B0_bridge_producer"),
)
SAFE_INHERITED_ENVIRONMENT_KEYS = (
    "HOME",
    "LANG",
    "LC_ALL",
    "PATH",
    "SSL_CERT_DIR",
    "SSL_CERT_FILE",
    "TMPDIR",
)
DANGEROUS_PYTHON_ENVIRONMENT_KEYS = (
    "PYTHONPATH",
    "PYTHONHOME",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
)
DANGEROUS_NATIVE_ENVIRONMENT_PREFIXES = ("DYLD_", "LD_")
SYSTEM_NATIVE_PREFIXES = (
    "/System/Library/",
    "/usr/lib/",
    "/System/Volumes/Preboot/Cryptexes/OS/System/Library/",
)
NATIVE_IMAGE_PHASES = (
    "bootstrap_pre_third_party",
    "runner_post_import",
    "post_manifest_validation",
    "full_stack_post_import",
)
NATIVE_IMAGE_PROBE = r"""\
import csv
import ctypes
import hashlib
import importlib
import io
import json
import os
import runpy
import stat
import subprocess
import sys

runner, site_packages = sys.argv[1:]
code_directory = os.path.dirname(runner)
system_prefixes = (
    "/System/Library/",
    "/usr/lib/",
    "/System/Volumes/Preboot/Cryptexes/OS/System/Library/",
)

def loaded_non_system_images():
    dyld = ctypes.CDLL(None)
    dyld._dyld_image_count.restype = ctypes.c_uint32
    dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    rows = {}
    count = int(dyld._dyld_image_count())
    for index in range(count):
        encoded = dyld._dyld_get_image_name(index)
        if not encoded:
            continue
        lexical = os.fsdecode(encoded)
        if not os.path.isabs(lexical):
            raise SystemExit("dyld returned a non-absolute image path")
        resolved = os.path.realpath(lexical)
        if lexical.startswith(system_prefixes) or resolved.startswith(system_prefixes):
            continue
        row = {"lexical_path": lexical, "resolved_path": resolved}
        previous = rows.setdefault(resolved, row)
        if previous != row:
            raise SystemExit("dyld returned multiple lexical names for one loaded image")
    return [rows[key] for key in sorted(rows)]

def main_executable_image():
    dyld = ctypes.CDLL(None)
    dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    encoded = dyld._dyld_get_image_name(0)
    if not encoded:
        raise SystemExit("dyld did not expose the main executable image")
    lexical = os.fsdecode(encoded)
    return {"lexical_path": lexical, "resolved_path": os.path.realpath(lexical)}

bootstrap = loaded_non_system_images()
sys.path.append(site_packages)
import argparse
import functools
import math
import platform
import re
import sysconfig
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import brentq
from scipy.sparse.linalg import LinearOperator, expm_multiply
runner_import = loaded_non_system_images()
platform.mac_ver()
post_manifest_validation = loaded_non_system_images()
sys.path.insert(0, code_directory)
for local_name in (
    "continuum_g1_smoke",
    "continuum_observable_four_patch",
    "continuum_weak_budget_design",
    "continuum_broad_patch_b0_bridge",
):
    importlib.import_module(local_name)
full_stack = loaded_non_system_images()
print(
    json.dumps(
        {
            "main_executable_image": main_executable_image(),
            "phase_images": {
                "bootstrap_pre_third_party": bootstrap,
                "runner_post_import": runner_import,
                "post_manifest_validation": post_manifest_validation,
                "full_stack_post_import": full_stack,
            },
        },
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
)
"""


@dataclass(frozen=True)
class AllocationModel:
    cells: int
    factors: Any
    initial: np.ndarray
    patch_fields: np.ndarray
    direction_fields: np.ndarray

    @property
    def state_count(self) -> int:
        return int(self.initial.size)


@dataclass(frozen=True)
class Snapshot:
    time: float
    budget: float
    theta: np.ndarray
    weights: np.ndarray
    state: np.ndarray
    state_tangents: np.ndarray
    jets: np.ndarray
    allocation_jets: np.ndarray
    cusp_map: np.ndarray
    cusp_jacobian: np.ndarray
    survival_identity_residuals: np.ndarray

    @property
    def fold_jacobian(self) -> np.ndarray:
        return self.cusp_jacobian[:2].copy()


@dataclass(frozen=True)
class CuspSolve:
    status: str
    converged: bool
    iterations: int
    snapshot: Snapshot | None
    reason: str


_BRIDGE_MODULE: Any | None = None
_BOUND_RUNTIME_MODULES: dict[str, tuple[Any, Path, dict[str, Any], bytes]] = {}


def _runtime_pin_records() -> dict[str, tuple[Path, str]]:
    """Resolve the exact manifest records for every executable local module."""

    manifest = load_json(MANIFEST)
    pins = manifest.get("pinned_files")
    if type(pins) is not dict:
        raise RuntimeError("runtime manifest pin map is malformed")
    records: dict[str, tuple[Path, str]] = {}
    for module_name, role in RUNTIME_MODULE_PINS:
        row = pins.get(role)
        expected_relative = PIN_PATHS[role]
        if (
            type(row) is not dict
            or set(row) != {"path", "sha256"}
            or row["path"] != expected_relative
            or type(row["sha256"]) is not str
        ):
            raise RuntimeError(f"runtime pin record is malformed: {role}")
        path = lexical_report_path(expected_relative)
        payload, metadata = stable_regular_file_bytes(path)
        if metadata["sha256"] != row["sha256"]:
            raise RuntimeError(f"runtime source hash changed: {role}")
        records[module_name] = (path.resolve(), row["sha256"])
    return records


def _attest_bound_runtime_modules(records: dict[str, tuple[Path, str]]) -> None:
    """Re-attest module identity, absolute source, descriptor bytes, and hash."""

    if set(_BOUND_RUNTIME_MODULES) != set(records):
        raise RuntimeError("runtime module binding set changed")
    for module_name, (expected_path, expected_hash) in records.items():
        module, bound_path, initial_metadata, initial_payload = _BOUND_RUNTIME_MODULES[module_name]
        if sys.modules.get(module_name) is not module:
            raise RuntimeError(f"runtime sys.modules binding changed: {module_name}")
        module_file = getattr(module, "__file__", None)
        if type(module_file) is not str or Path(module_file).resolve() != expected_path:
            raise RuntimeError(f"runtime module absolute path changed: {module_name}")
        if bound_path != expected_path:
            raise RuntimeError(f"runtime descriptor path changed: {module_name}")
        final_payload, final_metadata = stable_regular_file_bytes(expected_path)
        if (
            final_metadata["sha256"] != expected_hash
            or initial_metadata != final_metadata
            or initial_payload != final_payload
        ):
            raise RuntimeError(f"runtime module source changed after execution: {module_name}")


def _load_bound_runtime_module(module_name: str, expected_path: Path, expected_hash: str) -> Any:
    """Execute one source captured from its exact manifest-pinned descriptor path."""

    if module_name in sys.modules:
        raise RuntimeError(f"preloaded runtime module is forbidden: {module_name}")
    initial_payload, initial_metadata = stable_regular_file_bytes(expected_path)
    if initial_metadata["sha256"] != expected_hash:
        raise RuntimeError(f"runtime module hash mismatch before import: {module_name}")
    spec = importlib.util.spec_from_file_location(module_name, expected_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot create an absolute runtime module spec: {module_name}")
    module = importlib.util.module_from_spec(spec)
    code_object = compile(initial_payload, str(expected_path), "exec", dont_inherit=True)
    sys.modules[module_name] = module
    try:
        exec(code_object, module.__dict__)
        final_payload, final_metadata = stable_regular_file_bytes(expected_path)
        if initial_metadata != final_metadata or initial_payload != final_payload:
            raise RuntimeError(f"runtime module source changed during import: {module_name}")
        module_file = getattr(module, "__file__", None)
        if type(module_file) is not str or Path(module_file).resolve() != expected_path:
            raise RuntimeError(f"runtime module did not bind its absolute source: {module_name}")
        _BOUND_RUNTIME_MODULES[module_name] = (
            module,
            expected_path,
            initial_metadata,
            initial_payload,
        )
        return module
    except BaseException:
        if sys.modules.get(module_name) is module:
            del sys.modules[module_name]
        _BOUND_RUNTIME_MODULES.pop(module_name, None)
        raise


def bridge_module() -> Any:
    """Load the FV bridge only from exact, descriptor-stable manifest pins."""

    global _BRIDGE_MODULE
    if _BRIDGE_MODULE is None:
        records = _runtime_pin_records()
        if _BOUND_RUNTIME_MODULES:
            _attest_bound_runtime_modules(records)
            _BRIDGE_MODULE = _BOUND_RUNTIME_MODULES["continuum_broad_patch_b0_bridge"][0]
        else:
            loaded: list[str] = []
            try:
                for module_name, _role in RUNTIME_MODULE_PINS:
                    path, digest = records[module_name]
                    _load_bound_runtime_module(module_name, path, digest)
                    loaded.append(module_name)
                _attest_bound_runtime_modules(records)
                _BRIDGE_MODULE = _BOUND_RUNTIME_MODULES["continuum_broad_patch_b0_bridge"][0]
            except BaseException:
                for module_name in reversed(loaded):
                    binding = _BOUND_RUNTIME_MODULES.pop(module_name, None)
                    if binding is not None and sys.modules.get(module_name) is binding[0]:
                        del sys.modules[module_name]
                raise
    else:
        _attest_bound_runtime_modules(_runtime_pin_records())
    return _BRIDGE_MODULE


def scientific_output_paths() -> tuple[Path, Path, Path, Path, Path]:
    first, second = replica_paths()
    return (OUTPUT, REPRODUCIBILITY_OUTPUT, first, second, INDEPENDENT_AUDIT_OUTPUT)


def lexical_path_exists(path: Path) -> bool:
    try:
        os.lstat(path)
    except FileNotFoundError:
        return False
    return True


def regular_path_inode(path: Path) -> tuple[int, int]:
    item = os.lstat(path)
    if stat.S_ISLNK(item.st_mode) or not stat.S_ISREG(item.st_mode):
        raise RuntimeError(f"owned path is not a lexical regular file: {path}")
    return int(item.st_dev), int(item.st_ino)


def unlink_owned_path(path: Path, ownership: tuple[int, int] | None) -> bool:
    if ownership is None or not lexical_path_exists(path):
        return False
    try:
        current = regular_path_inode(path)
    except RuntimeError:
        return False
    if current != ownership:
        return False
    path.unlink()
    fsync_directory(path.parent)
    return True


def require_lexically_absent(paths: Sequence[Path], label: str) -> None:
    present = [str(path) for path in paths if lexical_path_exists(Path(path))]
    if present:
        raise RuntimeError(f"{label} must be lexically absent: {present}")


def require_exact_present_science_paths(allowed: Sequence[Path]) -> None:
    allowed_strings = {str(Path(path)) for path in allowed}
    observed = {str(path) for path in scientific_output_paths() if lexical_path_exists(Path(path))}
    if observed != allowed_strings:
        raise RuntimeError(
            f"scientific/evidence/audit lexical path boundary changed: {sorted(observed)}"
        )
    for path in allowed:
        metadata = os.lstat(path)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"allowed staging/output path is not regular: {path}")


def require_exact_present_paths(
    universe: Sequence[Path], allowed: Sequence[Path], label: str
) -> None:
    allowed_strings = {str(Path(path)) for path in allowed}
    universe_paths = tuple(Path(path) for path in universe)
    universe_strings = {str(path) for path in universe_paths}
    if not allowed_strings.issubset(universe_strings):
        raise RuntimeError(f"{label} allowed path escapes its universe")
    observed = {str(path) for path in universe_paths if lexical_path_exists(path)}
    if observed != allowed_strings:
        raise RuntimeError(f"{label} changed: {sorted(observed)}")
    for path in allowed:
        metadata = os.lstat(path)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"{label} allowed path is not regular: {path}")


def _metadata_from_stat(path: Path, value: os.stat_result, digest: str) -> dict[str, Any]:
    return {
        "path": str(path),
        "st_dev": int(value.st_dev),
        "st_ino": int(value.st_ino),
        "st_mode": int(value.st_mode),
        "st_nlink": int(value.st_nlink),
        "st_uid": int(value.st_uid),
        "st_gid": int(value.st_gid),
        "st_size": int(value.st_size),
        "st_mtime_ns": int(value.st_mtime_ns),
        "sha256": digest,
    }


def stable_regular_file_bytes(path: Path) -> tuple[bytes, dict[str, Any]]:
    """Capture one lexical regular file through one stable ``O_NOFOLLOW`` FD."""

    lexical = Path(path)
    before = os.lstat(lexical)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise RuntimeError(f"lexical path is not a regular non-symlink file: {lexical}")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise RuntimeError("O_NOFOLLOW is unavailable")
    descriptor = os.open(lexical, flags | nofollow)
    try:
        opened_before = os.fstat(descriptor)
        if not stat.S_ISREG(opened_before.st_mode):
            raise RuntimeError(f"opened pin is not regular: {lexical}")
        identity = (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_size,
            before.st_mtime_ns,
        )
        opened_identity = (
            opened_before.st_dev,
            opened_before.st_ino,
            opened_before.st_mode,
            opened_before.st_size,
            opened_before.st_mtime_ns,
        )
        if opened_identity != identity:
            raise RuntimeError(f"lexical/open identity mismatch: {lexical}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        payload = b"".join(chunks)
        opened_after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after = os.lstat(lexical)
    final_identity = (
        opened_after.st_dev,
        opened_after.st_ino,
        opened_after.st_mode,
        opened_after.st_size,
        opened_after.st_mtime_ns,
    )
    lexical_after_identity = (
        after.st_dev,
        after.st_ino,
        after.st_mode,
        after.st_size,
        after.st_mtime_ns,
    )
    if final_identity != identity or lexical_after_identity != identity:
        raise RuntimeError(f"file changed during stable capture: {lexical}")
    if len(payload) != before.st_size:
        raise RuntimeError(f"short stable read: {lexical}")
    digest = sha256_bytes(payload)
    return payload, _metadata_from_stat(lexical, after, digest)


def lexical_report_path(relative: str) -> Path:
    raw = Path(relative)
    if raw.is_absolute() or ".." in raw.parts or not raw.parts:
        raise ValueError("report-relative pin path is malformed")
    current = REPORT
    for index, part in enumerate(raw.parts):
        current = current / part
        metadata = os.lstat(current)
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"pinned path contains a symlink: {relative}")
        if index < len(raw.parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"pinned path parent is not a directory: {relative}")
    return current


def capture_complete_freeze_snapshot(
    manifest_path: Path, manifest: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    metadata: dict[str, dict[str, Any]] = {}
    payloads: dict[str, bytes] = {}
    manifest_bytes, manifest_metadata = stable_regular_file_bytes(Path(manifest_path))
    metadata["manifest"] = manifest_metadata
    payloads["manifest"] = manifest_bytes
    for role in sorted(PIN_PATHS):
        relative = manifest["pinned_files"][role]["path"]
        path = lexical_report_path(relative)
        payload, item = stable_regular_file_bytes(path)
        metadata[role] = item
        payloads[role] = payload
    return metadata, payloads


def require_same_freeze_snapshot(
    initial_metadata: dict[str, dict[str, Any]],
    initial_payloads: dict[str, bytes],
    final_metadata: dict[str, dict[str, Any]],
    final_payloads: dict[str, bytes],
) -> None:
    if initial_metadata != final_metadata or initial_payloads != final_payloads:
        raise RuntimeError("complete lexical metadata/byte snapshot changed")


def sha256(path: Path) -> str:
    payload, _metadata = stable_regular_file_bytes(Path(path))
    return sha256_bytes(payload)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _closure_sha256(rows: Sequence[tuple[str, str]]) -> str:
    digest = hashlib.sha256()
    for name, file_hash in sorted(rows):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def exact_import_tree_closure(
    root: Path, file_hash_cache: dict[str, str] | None = None
) -> dict[str, Any]:
    """Bind the exact regular-file bytes and symlink metadata below an import root."""

    base = Path(os.path.abspath(root))
    try:
        base_metadata = os.lstat(base)
    except FileNotFoundError:
        return {
            "present": False,
            "entry_count": 0,
            "regular_file_count": 0,
            "pyc_file_count": 0,
            "symlink_count": 0,
            "closure_sha256": _closure_sha256([]),
        }
    if stat.S_ISLNK(base_metadata.st_mode) or not stat.S_ISDIR(base_metadata.st_mode):
        raise RuntimeError("runtime import-tree root is not a lexical directory")
    cache = file_hash_cache if file_hash_cache is not None else {}
    rows: list[tuple[str, str]] = []
    regular_count = 0
    pyc_count = 0
    symlink_count = 0
    for directory, directory_names, file_names in os.walk(base, topdown=True, followlinks=False):
        directory_path = Path(directory)
        kept_directories: list[str] = []
        for name in sorted(directory_names):
            path = directory_path / name
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode):
                relative = path.relative_to(base).as_posix()
                rows.append(
                    (
                        relative,
                        f"L:{metadata.st_mode}:{metadata.st_size}:{os.readlink(path)}",
                    )
                )
                symlink_count += 1
                continue
            if not stat.S_ISDIR(metadata.st_mode):
                raise RuntimeError("runtime import tree contains a non-directory")
            kept_directories.append(name)
        directory_names[:] = kept_directories
        for name in sorted(file_names):
            path = directory_path / name
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode):
                relative = path.relative_to(base).as_posix()
                rows.append(
                    (
                        relative,
                        f"L:{metadata.st_mode}:{metadata.st_size}:{os.readlink(path)}",
                    )
                )
                symlink_count += 1
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise RuntimeError("runtime import tree contains a special file")
            cache_key = str(path)
            file_hash = cache.get(cache_key)
            if file_hash is None:
                payload, _snapshot = stable_regular_file_bytes(path)
                file_hash = sha256_bytes(payload)
                cache[cache_key] = file_hash
            rows.append(
                (
                    path.relative_to(base).as_posix(),
                    f"F:{metadata.st_mode}:{metadata.st_size}:{file_hash}",
                )
            )
            regular_count += 1
            pyc_count += int(name.endswith(".pyc"))
    return {
        "present": True,
        "entry_count": len(rows),
        "regular_file_count": regular_count,
        "pyc_file_count": pyc_count,
        "symlink_count": symlink_count,
        "closure_sha256": _closure_sha256(rows),
    }


def stdlib_tree_closure(root: Path) -> dict[str, Any]:
    """Attest the full stdlib tree, including pyc bytes and symlink targets."""

    closure = exact_import_tree_closure(Path(os.path.realpath(root)))
    if closure["present"] is not True:
        raise RuntimeError("Python stdlib root is missing")
    return closure


def _lexical_regular_under(root: Path, path: Path) -> tuple[bytes, dict[str, Any]]:
    base = Path(os.path.abspath(root))
    target = Path(os.path.abspath(os.path.normpath(path)))
    if target == base or not target.is_relative_to(base):
        raise RuntimeError("runtime package path escapes the frozen venv")
    current = base
    parts = target.relative_to(base).parts
    for index, part in enumerate(parts):
        current /= part
        metadata = os.lstat(current)
        if stat.S_ISLNK(metadata.st_mode):
            raise RuntimeError("runtime package path contains a symlink")
        expected = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not expected(metadata.st_mode):
            raise RuntimeError("runtime package path has the wrong file type")
    return stable_regular_file_bytes(target)


def distribution_record_closure(
    venv_root: Path,
    site_packages: Path,
    record_path: Path,
    file_hash_cache: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Rebuild a wheel RECORD closure from native file bytes, not RECORD digests."""

    root = Path(os.path.abspath(venv_root))
    site = Path(os.path.abspath(site_packages))
    record = Path(os.path.abspath(record_path))
    record_bytes, _metadata = _lexical_regular_under(root, record)
    try:
        records = list(csv.reader(io.StringIO(record_bytes.decode("utf-8"), newline="")))
    except (UnicodeDecodeError, csv.Error) as error:
        raise RuntimeError("runtime distribution RECORD is malformed") from error
    rows: list[tuple[str, str]] = []
    native_rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    cache = file_hash_cache if file_hash_cache is not None else {}
    for row in records:
        if len(row) != 3 or not row[0]:
            raise RuntimeError("runtime distribution RECORD row is malformed")
        path = Path(os.path.abspath(os.path.normpath(site / row[0])))
        if not path.is_relative_to(root):
            raise RuntimeError("runtime distribution RECORD path escapes the frozen venv")
        relative = path.relative_to(root).as_posix()
        if relative in seen:
            raise RuntimeError("runtime distribution RECORD has a duplicate path")
        seen.add(relative)
        file_hash = cache.get(str(path))
        if file_hash is None:
            payload, _snapshot = _lexical_regular_under(root, path)
            file_hash = sha256_bytes(payload)
            cache[str(path)] = file_hash
        rows.append((relative, file_hash))
        if relative.endswith((".so", ".dylib", ".pyd", ".dll")):
            native_rows.append((relative, file_hash))
    return {
        "record_file_count": len(rows),
        "record_sha256": sha256_bytes(record_bytes),
        "record_closure_sha256": _closure_sha256(rows),
        "native_extension_count": len(native_rows),
        "native_extension_closure_sha256": _closure_sha256(native_rows),
    }


def _is_system_native_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in SYSTEM_NATIVE_PREFIXES)


def loaded_non_system_native_images() -> list[dict[str, str]]:
    """List exact currently mapped non-system Mach-O images via dyld."""

    dyld = ctypes.CDLL(None)
    dyld._dyld_image_count.restype = ctypes.c_uint32
    dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    rows: dict[str, dict[str, str]] = {}
    for index in range(int(dyld._dyld_image_count())):
        encoded = dyld._dyld_get_image_name(index)
        if not encoded:
            continue
        lexical = os.fsdecode(encoded)
        if not os.path.isabs(lexical):
            raise RuntimeError("dyld returned a non-absolute image path")
        resolved = os.path.realpath(lexical)
        if _is_system_native_path(lexical) or _is_system_native_path(resolved):
            continue
        row = {"lexical_path": lexical, "resolved_path": resolved}
        previous = rows.setdefault(resolved, row)
        if previous != row:
            raise RuntimeError("dyld returned multiple lexical names for one loaded image")
    return [rows[key] for key in sorted(rows)]


def isolated_native_image_probe() -> dict[str, Any]:
    """Reproduce bootstrap, runner, post-validation, and full-stack image sets."""

    site_packages = repository_site_packages()
    environment = {
        "HOME": os.environ.get("HOME", str(Path.home())),
        "PATH": "/usr/bin:/bin",
        "LANG": "C",
        "LC_ALL": "C",
        "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }
    completed = subprocess.run(
        [
            os.path.abspath(sys.executable),
            "-I",
            "-S",
            "-B",
            "-c",
            NATIVE_IMAGE_PROBE,
            str(HERE),
            str(site_packages),
        ],
        cwd=REPOSITORY,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"isolated native-image probe failed: {completed.stderr.strip()}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("isolated native-image probe returned malformed JSON") from error
    if type(value) is not dict or set(value) != {"main_executable_image", "phase_images"}:
        raise RuntimeError("isolated native-image probe schema changed")
    main = value["main_executable_image"]
    phases = value["phase_images"]
    if (
        type(main) is not dict
        or set(main) != {"lexical_path", "resolved_path"}
        or type(phases) is not dict
        or set(phases) != set(NATIVE_IMAGE_PHASES)
    ):
        raise RuntimeError("isolated native-image phase schema changed")
    previous: set[str] = set()
    for phase in NATIVE_IMAGE_PHASES:
        rows = phases[phase]
        if type(rows) is not list or not rows:
            raise RuntimeError("isolated native-image phase is empty")
        resolved_order: list[str] = []
        for row in rows:
            if (
                type(row) is not dict
                or set(row) != {"lexical_path", "resolved_path"}
                or type(row["lexical_path"]) is not str
                or type(row["resolved_path"]) is not str
                or not os.path.isabs(row["lexical_path"])
                or not os.path.isabs(row["resolved_path"])
                or os.path.realpath(row["lexical_path"]) != row["resolved_path"]
                or _is_system_native_path(row["lexical_path"])
                or _is_system_native_path(row["resolved_path"])
            ):
                raise RuntimeError("isolated native-image phase row is malformed")
            resolved_order.append(row["resolved_path"])
        if resolved_order != sorted(set(resolved_order)):
            raise RuntimeError("isolated native-image phase is not uniquely sorted")
        current = set(resolved_order)
        if not previous.issubset(current):
            raise RuntimeError("isolated native-image phases are not monotone")
        previous = current
    if main not in phases["bootstrap_pre_third_party"]:
        raise RuntimeError("native-image probe main executable is not in the bootstrap phase")
    return value


def _macho_load_commands(path: Path, otool: Path) -> tuple[str | None, list[str], list[str]]:
    completed = subprocess.run(
        [str(otool), "-l", str(path)],
        env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"otool failed for native image: {path}")
    lines = completed.stdout.splitlines()
    install_names: list[str] = []
    rpaths: list[str] = []
    dependencies: list[str] = []
    load_commands = {
        "LC_LOAD_DYLIB",
        "LC_LOAD_WEAK_DYLIB",
        "LC_REEXPORT_DYLIB",
        "LC_LOAD_UPWARD_DYLIB",
    }
    for index, line in enumerate(lines):
        command = line.strip()
        if command == "cmd LC_ID_DYLIB":
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("name "):
                    install_names.append(item[5:].split(" (offset ", 1)[0])
                    break
        elif command.removeprefix("cmd ") in load_commands:
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("name "):
                    dependencies.append(item[5:].split(" (offset ", 1)[0])
                    break
        elif command == "cmd LC_RPATH":
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("path "):
                    rpaths.append(item[5:].split(" (offset ", 1)[0])
                    break
    unique_install_names = sorted(set(install_names))
    if len(unique_install_names) > 1:
        raise RuntimeError(f"native image has architecture-dependent install names: {path}")
    return (
        unique_install_names[0] if unique_install_names else None,
        list(dict.fromkeys(rpaths)),
        sorted(set(dependencies)),
    )


def _expand_macho_anchor(value: str, loader: Path, executable: Path) -> Path:
    if value == "@loader_path":
        return loader.parent
    if value.startswith("@loader_path/"):
        return loader.parent / value[len("@loader_path/") :]
    if value == "@executable_path":
        return executable.parent
    if value.startswith("@executable_path/"):
        return executable.parent / value[len("@executable_path/") :]
    if os.path.isabs(value):
        return Path(value)
    raise RuntimeError(f"unsupported Mach-O path anchor: {value}")


def _resolve_macho_dependency(
    install_name: str,
    loader: Path,
    executable: Path,
    rpaths: Sequence[str],
) -> tuple[str, str, str | None]:
    if _is_system_native_path(install_name):
        return "system_dyld_cache", install_name, None
    if install_name.startswith("@rpath/"):
        suffix = install_name[len("@rpath/") :]
        candidates: list[Path] = []
        for rpath in rpaths:
            base = _expand_macho_anchor(rpath, loader, executable)
            candidate = Path(os.path.abspath(os.path.normpath(base / suffix)))
            if os.path.lexists(candidate):
                candidates.append(candidate)
        if not candidates:
            raise RuntimeError(f"unresolved @rpath dependency {install_name} in {loader}")
        lexical = str(candidates[0])
    else:
        lexical = str(
            Path(
                os.path.abspath(
                    os.path.normpath(_expand_macho_anchor(install_name, loader, executable))
                )
            )
        )
    resolved = os.path.realpath(lexical)
    if _is_system_native_path(lexical) or _is_system_native_path(resolved):
        return "system_dyld_cache", lexical, None
    if not os.path.lexists(lexical):
        raise RuntimeError(f"non-system native dependency is absent: {lexical}")
    return "non_system", lexical, resolved


def bounded_non_system_native_provenance() -> dict[str, Any]:
    """Rebuild actual loaded-image sets and their recursive non-system Mach-O closure."""

    probe = isolated_native_image_probe()
    phases = probe["phase_images"]
    executable = Path(probe["main_executable_image"]["resolved_path"])
    otool = Path("/usr/bin/otool")
    otool_bytes, _otool_metadata = stable_regular_file_bytes(otool)
    aliases: dict[str, set[str]] = {}
    actual_phases: dict[str, set[str]] = {}
    for phase in NATIVE_IMAGE_PHASES:
        actual_phases[phase] = {row["resolved_path"] for row in phases[phase]}
        for row in phases[phase]:
            aliases.setdefault(row["resolved_path"], set()).add(row["lexical_path"])

    pending = sorted(actual_phases["full_stack_post_import"])
    metadata: dict[str, tuple[str | None, list[str], list[dict[str, Any]]]] = {}
    while pending:
        resolved = pending.pop(0)
        if resolved in metadata:
            continue
        path = Path(resolved)
        if not path.is_absolute() or _is_system_native_path(resolved):
            raise RuntimeError("non-system native closure contains an invalid root")
        install_name, rpaths, raw_dependencies = _macho_load_commands(path, otool)
        dependency_rows: list[dict[str, Any]] = []
        for raw in raw_dependencies:
            classification, lexical, dependency_resolved = _resolve_macho_dependency(
                raw, path, executable, rpaths
            )
            dependency_rows.append(
                {
                    "install_name": raw,
                    "classification": classification,
                    "lexical_path": lexical,
                    "resolved_path": dependency_resolved,
                }
            )
            if dependency_resolved is not None:
                aliases.setdefault(dependency_resolved, set()).add(lexical)
                if dependency_resolved not in metadata and dependency_resolved not in pending:
                    pending.append(dependency_resolved)
                    pending.sort()
        metadata[resolved] = (
            install_name,
            rpaths,
            sorted(
                dependency_rows,
                key=lambda row: (
                    row["install_name"],
                    row["lexical_path"],
                    row["resolved_path"] or "",
                ),
            ),
        )

    rows: list[dict[str, Any]] = []
    for resolved in sorted(metadata):
        payload, snapshot = stable_regular_file_bytes(Path(resolved))
        install_name, rpaths, dependencies = metadata[resolved]
        lexical_paths = sorted(aliases.get(resolved, {resolved}))
        if any(os.path.realpath(path) != resolved for path in lexical_paths):
            raise RuntimeError("native-image lexical alias does not resolve to its frozen row")
        rows.append(
            {
                "resolved_path": resolved,
                "lexical_paths": lexical_paths,
                "install_name": install_name,
                "size": int(snapshot["st_size"]),
                "sha256": sha256_bytes(payload),
                "rpaths": rpaths,
                "dependencies": dependencies,
                "actual_loaded_phases": [
                    phase for phase in NATIVE_IMAGE_PHASES if resolved in actual_phases[phase]
                ],
            }
        )
    encoded_rows = json.dumps(rows, allow_nan=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    transition_added = [
        row for row in phases["post_manifest_validation"] if row not in phases["runner_post_import"]
    ]
    if len(transition_added) != 1 or not Path(transition_added[0]["resolved_path"]).name.startswith(
        "pyexpat."
    ):
        raise RuntimeError("post-manifest-validation phase did not add exactly pyexpat")
    return {
        "contract": "bounded_non_system_macho_closure_v1",
        "threat_boundary": "reproducibility_witness_not_malicious_same_uid_prevention",
        "bootstrap_root_of_trust_includes_hash_primitive": True,
        "probe_induced_images_included": ["ctypes", "_ctypes"],
        "phase_transition_causes": {
            "post_manifest_validation": {
                "operation": "signed_dyld_cache_provenance.platform.mac_ver",
                "added_images": transition_added,
            }
        },
        "system_leaf_prefixes": list(SYSTEM_NATIVE_PREFIXES),
        "main_executable_image": probe["main_executable_image"],
        "phase_images": phases,
        "otool": {"path": str(otool), "sha256": sha256_bytes(otool_bytes)},
        "closure_image_count": len(rows),
        "closure_sha256": sha256_bytes(encoded_rows),
        "images": rows,
    }


def require_loaded_native_phase(manifest: dict[str, Any], phase: str) -> None:
    if phase not in NATIVE_IMAGE_PHASES:
        raise RuntimeError("unknown native-image runtime phase")
    try:
        expected = manifest["runtime_provenance"]["non_system_native"]["phase_images"][phase]
    except (KeyError, TypeError) as error:
        raise RuntimeError("manifest native-image phase is malformed") from error
    observed = loaded_non_system_native_images()
    if observed != expected:
        raise RuntimeError(f"non-system native loaded-image set changed at {phase}")


def signed_dyld_cache_provenance() -> dict[str, Any]:
    """Verify and bind every arm64e dyld shared-cache code directory."""

    codesign = Path("/usr/bin/codesign")
    codesign_bytes, _metadata = stable_regular_file_bytes(codesign)
    cache_root = Path("/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld")
    prefix = "dyld_shared_cache_arm64e"
    cache_paths = sorted(
        (
            path
            for path in cache_root.iterdir()
            if path.name == prefix
            or re.fullmatch(r"dyld_shared_cache_arm64e\.\d+(?:\..+)?", path.name)
        ),
        key=lambda path: path.name,
    )
    if not cache_paths:
        raise RuntimeError("arm64e dyld shared cache is missing")
    environment = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
    rows: list[dict[str, Any]] = []
    for path in cache_paths:
        before = os.lstat(path)
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
            raise RuntimeError("dyld cache is not a lexical regular file")
        verified = subprocess.run(
            [str(codesign), "--verify", "--strict", str(path)],
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        described = subprocess.run(
            [str(codesign), "-dvvv", str(path)],
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        after = os.lstat(path)
        initial_identity = (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_size,
            before.st_mtime_ns,
        )
        final_identity = (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_size,
            after.st_mtime_ns,
        )
        hashes = [
            line.split("=", 1)[1]
            for line in (described.stdout + described.stderr).splitlines()
            if line.startswith("CandidateCDHashFull sha256=")
        ]
        if (
            verified.returncode != 0
            or described.returncode != 0
            or initial_identity != final_identity
            or len(hashes) != 1
            or not re.fullmatch(r"[0-9a-f]{64}", hashes[0])
        ):
            raise RuntimeError(f"signed dyld cache attestation failed: {path}")
        rows.append(
            {
                "path": str(path),
                "size": int(before.st_size),
                "candidate_cdhash_full_sha256": hashes[0],
            }
        )
    return {
        "darwin_uname": list(os.uname()),
        "mac_ver": [platform.mac_ver()[0], list(platform.mac_ver()[1]), platform.mac_ver()[2]],
        "machine": platform.machine(),
        "codesign_tool": {"path": str(codesign), "sha256": sha256_bytes(codesign_bytes)},
        "dyld_cache_root": str(cache_root),
        "dyld_cache_code_directories": rows,
    }


def rebuild_runtime_provenance() -> dict[str, Any]:
    """Recompute the bounded Python/NumPy/SciPy/native runtime closure."""

    venv_root = (REPOSITORY / ".venv").resolve()
    site_packages = repository_site_packages()
    stdlib_root = Path(sysconfig.get_path("stdlib")).resolve()
    real_executable = Path(os.path.realpath(sys.executable))
    executable_bytes, _metadata = stable_regular_file_bytes(real_executable)
    base_prefix = Path(sys.base_prefix).resolve()
    framework_paths = (
        base_prefix / "Python",
        base_prefix / "Resources" / "Python.app" / "Contents" / "MacOS" / "Python",
    )
    framework_files: dict[str, str] = {}
    for path in framework_paths:
        payload, _snapshot = stable_regular_file_bytes(path)
        framework_files[str(path)] = sha256_bytes(payload)

    distributions: dict[str, dict[str, Any]] = {}
    for name, version, module_file in (
        ("numpy", np.__version__, np.__file__),
        ("scipy", scipy.__version__, scipy.__file__),
    ):
        file_hash_cache: dict[str, str] = {}
        import_tree_closures = {
            root_name: {
                "path": str(site_packages / root_name),
                **exact_import_tree_closure(site_packages / root_name, file_hash_cache),
            }
            for root_name in (name, f"{name}.libs")
        }
        record_path = site_packages / f"{name}-{version}.dist-info" / "RECORD"
        distributions[name] = {
            "version": version,
            "module_origin": str(Path(module_file).resolve()),
            "record_path": str(record_path),
            **distribution_record_closure(
                venv_root,
                site_packages,
                record_path,
                file_hash_cache,
            ),
            "import_tree_closures": import_tree_closures,
        }

    numpy_configuration = np.show_config(mode="dicts")
    if type(numpy_configuration) is not dict:
        raise RuntimeError("NumPy build configuration is not a dictionary")
    provenance = {
        "contract": "bounded_runtime_closure_v2",
        "python": {
            "version": sys.version,
            "cache_tag": sys.implementation.cache_tag,
            "invocation_path": os.path.abspath(sys.executable),
            "real_executable_path": str(real_executable),
            "real_executable_sha256": sha256_bytes(executable_bytes),
            "stdlib_root": str(stdlib_root),
            "stdlib_closure": stdlib_tree_closure(stdlib_root),
            "framework_files": framework_files,
        },
        "venv_root": str(venv_root),
        "site_packages": str(site_packages),
        "distributions": distributions,
        "numpy_build_configuration": numpy_configuration,
        "non_system_native": bounded_non_system_native_provenance(),
        "system_native": signed_dyld_cache_provenance(),
    }
    require_finite_json(provenance)
    return provenance


@functools.lru_cache(maxsize=1)
def frozen_runtime_provenance_reference() -> dict[str, Any]:
    """Memoize the contract reference; validation still recomputes a fresh closure."""

    return rebuild_runtime_provenance()


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


def sorted_bool_mapping(values: dict[str, Any]) -> dict[str, bool]:
    """Canonicalize a boolean gate map without inheriting insertion/hash order."""

    if type(values) is not dict or any(type(key) is not str for key in values):
        raise TypeError("boolean gate mapping must have string keys")
    return {key: bool(values[key]) for key in sorted(values)}


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    require_finite_json(payload)
    return (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def load_json(path: Path) -> dict[str, Any]:
    payload, _metadata = stable_regular_file_bytes(Path(path))
    value = parse_json_object_bytes(payload, str(path), require_canonical=False)
    return value


def parse_json_object_bytes(
    payload: bytes, label: str, *, require_canonical: bool = True
) -> dict[str, Any]:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key in {label}: {key}")
            value[key] = item
        return value

    def reject_constant(value: str) -> Any:
        raise ValueError(f"nonfinite JSON constant in {label}: {value}")

    try:
        text = payload.decode("utf-8")
        value = json.loads(text, object_pairs_hook=object_pairs, parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from error
    if type(value) is not dict:
        raise ValueError(f"{label} must contain one JSON object")
    require_finite_json(value)
    if require_canonical and canonical_json_bytes(value) != payload:
        raise ValueError(f"{label} is not canonical JSON")
    return value


def exact_json_contract(observed: Any, expected: Any) -> bool:
    if type(observed) is not type(expected):
        return False
    if type(expected) is dict:
        return set(observed) == set(expected) and all(
            exact_json_contract(observed[key], expected[key]) for key in expected
        )
    if type(expected) is list:
        return len(observed) == len(expected) and all(
            exact_json_contract(left, right) for left, right in zip(observed, expected, strict=True)
        )
    return bool(observed == expected)


def expected_manifest_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "stage": STAGE,
        "evidence_timing": EVIDENCE_TIMING,
        "freeze_date": "2026-07-14",
        "claim_scope": (
            "Result-blind discovery on exactly the fixed-box cubic meshes 65 and 97 "
            "for a B=0.01 fixed-total-budget allocation cusp in the frozen broad "
            "four-slab d=2 killed-Doi family."
        ),
        "known_before_freeze": {
            "B0_continuum_cusp_known": True,
            "positive_B_fixed_control_shape_runs_known": True,
            "allocation_cusp_mesh_65_evaluated": False,
            "allocation_cusp_mesh_97_evaluated": False,
            "allocation_fold_or_phase_search_evaluated": False,
            "formal_result_file_present": False,
        },
        "physical_parameters": PHYSICAL_PARAMETERS,
        "finite_volume": FINITE_VOLUME,
        "factor_gates": FACTOR_GATES,
        "allocation_chart": ALLOCATION_CHART,
        "budget_homotopy": BUDGET_HOMOTOPY,
        "solver": SOLVER,
        "derivative_audit": DERIVATIVE_AUDIT,
        "cusp_gates": CUSP_GATES,
        "preflight": PREFLIGHT,
        "root_search": ROOT_SEARCH,
        "remote_pair": REMOTE_PAIR,
        "fold_continuation": FOLD_CONTINUATION,
        "phase_search": PHASE_SEARCH,
        "representative_gates": REPRESENTATIVE_GATES,
        "reproducibility": REPRODUCIBILITY,
        "failure_contract": FAILURE_CONTRACT,
        "execution_boundary": EXECUTION_BOUNDARY,
        "runtime_provenance": frozen_runtime_provenance_reference(),
        "required_claim_flags": CLAIM_FLAGS,
        "forbidden_claims": FORBIDDEN_CLAIMS,
    }


def validate_manifest(
    manifest: dict[str, Any],
    *,
    require_outputs_absent: bool = True,
    allowed_present_science_paths: Sequence[Path] = (),
) -> dict[str, str]:
    contract = expected_manifest_contract()
    if set(manifest) != set(contract) | {"pinned_files"}:
        raise ValueError("manifest top-level contract changed")
    for key, expected in contract.items():
        if not exact_json_contract(manifest[key], expected):
            raise ValueError(f"manifest {key} contract changed")
    pins = manifest["pinned_files"]
    if type(pins) is not dict or set(pins) != set(PIN_PATHS):
        raise ValueError("manifest pinned-file role set changed")
    observed: dict[str, str] = {}
    raw_paths: list[str] = []
    for role, expected_path in PIN_PATHS.items():
        item = pins[role]
        if type(item) is not dict or set(item) != {"path", "sha256"}:
            raise ValueError(f"pinned {role} record shape changed")
        if item["path"] != expected_path or type(item["path"]) is not str:
            raise ValueError(f"pinned {role} path changed")
        resolved = lexical_report_path(item["path"])
        expected_hash = item["sha256"]
        if (
            type(expected_hash) is not str
            or len(expected_hash) != 64
            or any(character not in "0123456789abcdef" for character in expected_hash)
        ):
            raise ValueError(f"pinned {role} SHA-256 is malformed")
        _payload, metadata = stable_regular_file_bytes(resolved)
        observed[role] = metadata["sha256"]
        if observed[role] != expected_hash:
            raise ValueError(f"pinned {role} hash mismatch")
        raw_paths.append(item["path"])
    if len(raw_paths) != len(set(raw_paths)):
        raise ValueError("duplicate pinned paths are forbidden")
    if require_outputs_absent:
        allowed = {os.path.abspath(path) for path in allowed_present_science_paths}
        scientific = {os.path.abspath(path): path for path in scientific_output_paths()}
        if not allowed.issubset(scientific):
            raise ValueError("allowed science path escapes the frozen five-path boundary")
        present = {absolute for absolute, path in scientific.items() if lexical_path_exists(path)}
        if present != allowed:
            raise ValueError(
                "five-path scientific/evidence/audit boundary mismatch: "
                f"expected {sorted(allowed)}, observed {sorted(present)}"
            )
    return observed


def require_repository_venv() -> None:
    expected_venv = (REPOSITORY / ".venv").resolve()
    if sys.flags.no_site == 1:
        expected_site = repository_site_packages()
        observed_sites = [
            Path(value).resolve()
            for value in sys.path
            if value and Path(value).exists() and Path(value).resolve() == expected_site
        ]
        executable = Path(os.path.abspath(sys.executable))
        if len(observed_sites) != 1 or not executable.is_relative_to(expected_venv):
            raise RuntimeError(
                "isolated allocation discovery must use the absolute repository "
                "site-packages bootstrap"
            )
    elif Path(sys.prefix).resolve() != expected_venv:
        raise RuntimeError("allocation discovery must run inside the repository .venv")


def repository_site_packages() -> Path:
    return (
        REPOSITORY
        / ".venv"
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    ).resolve()


def isolated_runner_command(arguments: Sequence[str]) -> list[str]:
    site_packages = repository_site_packages()
    if not site_packages.is_dir():
        raise RuntimeError("repository site-packages directory is missing")
    return [
        sys.executable,
        "-I",
        "-S",
        "-B",
        "-c",
        ISOLATED_RUNNER_BOOTSTRAP,
        str(HERE),
        str(site_packages),
        *map(str, arguments),
    ]


@contextmanager
def pinned_numpy_seed(seed: int) -> Iterator[None]:
    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed must be uint32-compatible")
    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)


def weights_from_theta(theta: np.ndarray) -> np.ndarray:
    value = np.asarray(theta, dtype=float)
    if value.shape != (2,) or not np.all(np.isfinite(value)):
        raise ValueError("theta must be a finite two-vector")
    return REFERENCE_WEIGHTS + TANGENT_BASIS @ value


def point_in_trust_box(time: float, theta: np.ndarray) -> tuple[bool, str]:
    values = np.asarray(theta, dtype=float)
    if values.shape != (2,) or not np.all(np.isfinite(values)) or not math.isfinite(time):
        return False, "nonfinite_or_malformed_point"
    if not SOLVER["time_trust_box"][0] <= time <= SOLVER["time_trust_box"][1]:
        return False, "time_outside_trust_box"
    if float(np.max(np.abs(values))) > SOLVER["maximum_theta_linf"]:
        return False, "theta_outside_trust_box"
    if float(np.min(weights_from_theta(values))) < SOLVER["minimum_simplex_weight"]:
        return False, "simplex_margin_below_floor"
    return True, "inside"


def validate_cells(cells: int, *, formal: bool) -> int:
    if type(cells) is not int:
        raise ValueError("cells must be an integer")
    if formal:
        if cells not in DISCOVERY_MESHES:
            raise ValueError("formal discovery permits exactly meshes 65 and 97")
    elif cells < 5 or cells > DRY_RUN_MAX_CELLS or cells in DISCOVERY_MESHES:
        raise ValueError("dry-run cells must be between 5 and 9 and cannot be scientific")
    return cells


def build_model(cells: int, manifest: dict[str, Any], *, formal: bool) -> AllocationModel:
    count = validate_cells(cells, formal=formal)
    bridge = bridge_module()
    parameters = bridge.parameters_from_manifest(manifest)
    factors = bridge.build_fv_factors(count, parameters, manifest)
    patch_fields = np.asarray(
        [
            np.kron(profile / parameters.transverse_width, factors.contact_profile)
            for profile in factors.patch_profiles
        ],
        dtype=float,
    )
    initial = np.asarray(np.kron(factors.midpoint_initial, factors.relative_initial), dtype=float)
    direction_fields = np.asarray(TANGENT_BASIS.T @ patch_fields, dtype=float)
    if patch_fields.shape != (4, count**3) or direction_fields.shape != (2, count**3):
        raise RuntimeError("killing fields do not match the cubic tensor grid")
    if initial.shape != (count**3,) or abs(float(np.sum(initial)) - 1.0) > 2.0e-13:
        raise RuntimeError("initial law is malformed or not normalized")
    return AllocationModel(count, factors, initial, patch_fields, direction_fields)


def allocation_model_diagnostics(
    model: AllocationModel, budget: float, theta: np.ndarray
) -> dict[str, Any]:
    """Serialize the finite-volume and killed-generator invariants used by every gate."""

    operator = KilledColumnOperator(model, budget, theta)
    parameters = bridge_module().parameters_from_manifest(expected_manifest_contract())
    midpoint_profile = operator.weights @ model.factors.patch_profiles
    physical_budget = float(
        parameters.transverse_width
        * budget
        * np.sum(midpoint_profile / parameters.transverse_width)
        * model.factors.grid.midpoint_spacing
    )
    q_one = np.asarray(operator.rmatvec(np.ones(model.state_count)), dtype=float)
    diagnostics = {
        "mesh": [model.cells] * 3,
        "state_count": model.state_count,
        "matrix_free_full_generator": True,
        "initial_mass": float(np.sum(model.initial)),
        "initial_mass_error": float(abs(np.sum(model.initial) - 1.0)),
        "installed_budget": float(budget),
        "physical_installed_budget": physical_budget,
        "physical_installed_budget_absolute_error": float(abs(physical_budget - budget)),
        "minimum_weight": float(np.min(operator.weights)),
        "weight_sum_error": float(abs(np.sum(operator.weights) - 1.0)),
        "minimum_killing_per_budget": float(np.min(operator.kappa)),
        "maximum_killing_per_budget": float(np.max(operator.kappa)),
        "midpoint_killing_profile_minimum": float(np.min(midpoint_profile)),
        "midpoint_killing_profile_maximum": float(np.max(midpoint_profile)),
        "midpoint_killing_profile_sum": float(np.sum(midpoint_profile)),
        "contact_killing_profile_minimum": float(np.min(model.factors.contact_profile)),
        "contact_killing_profile_maximum": float(np.max(model.factors.contact_profile)),
        "contact_killing_profile_sum": float(np.sum(model.factors.contact_profile)),
        "midpoint_generator_diagonal_sum": float(
            np.sum(model.factors.midpoint_generator.diagonal())
        ),
        "relative_generator_diagonal_sum": float(
            np.sum(model.factors.relative_generator.diagonal())
        ),
        "generator_killing_identity_error": float(np.max(np.abs(q_one + budget * operator.kappa))),
        "analytic_column_operator_trace": operator.trace_value,
        "factor_diagnostics": model.factors.diagnostics,
    }
    require_finite_json(diagnostics)
    return diagnostics


def state_law_diagnostics(
    model: AllocationModel,
    budget: float,
    theta: np.ndarray,
    state: np.ndarray,
    jets: np.ndarray | None = None,
) -> dict[str, float]:
    """Evaluate positivity plus ``S_t=-f`` and differential mass balance."""

    operator = KilledColumnOperator(model, budget, theta)
    value = np.asarray(state, dtype=float)
    if value.shape != (model.state_count,) or not np.all(np.isfinite(value)):
        raise ValueError("state is malformed or nonfinite")
    density_per_budget = (
        float(np.asarray(jets, dtype=float)[0])
        if jets is not None
        else float(value @ operator.kappa)
    )
    if not math.isfinite(density_per_budget):
        raise ValueError("density is nonfinite")
    density = float(budget * density_per_budget)
    survival_derivative = float(np.sum(operator.matvec(value)))
    row = {
        "density": density,
        "density_per_budget": density_per_budget,
        "survival": float(np.sum(value)),
        "minimum_state_component": float(np.min(value)),
        "survival_derivative": survival_derivative,
        "survival_density_identity_error": float(abs(survival_derivative + density)),
        "differential_mass_balance_error": float(abs(survival_derivative + density)),
    }
    require_finite_json(row)
    return row


def factor_diagnostics_pass(model_diagnostics: Any) -> bool:
    """Reconstruct the frozen FV factor contract from primitive diagnostics."""

    try:
        if type(model_diagnostics) is not dict:
            return False
        mesh = model_diagnostics["mesh"]
        factors = model_diagnostics["factor_diagnostics"]
        if (
            type(mesh) is not list
            or len(mesh) != 3
            or not all(type(item) is int for item in mesh)
            or len(set(mesh)) != 1
            or not _exact_keys(factors, FACTOR_DIAGNOSTIC_KEYS)
            or type(factors["cells_per_coordinate"]) is not int
            or type(factors["state_count_if_full_matrix_formed"]) is not int
        ):
            return False
        cells = mesh[0]
        if (
            cells <= 0
            or factors["cells_per_coordinate"] != cells
            or factors["state_count_if_full_matrix_formed"] != cells**3
            or not _exact_keys(
                factors["spacings"], {"midpoint", "relative_parallel", "relative_perp"}
            )
            or not all(type(item) is float for item in factors["spacings"].values())
            or not _float_vector(factors["patch_integrals"], 4)
            or not all(
                type(factors[key]) is float
                for key in FACTOR_DIAGNOSTIC_KEYS
                - {
                    "cells_per_coordinate",
                    "state_count_if_full_matrix_formed",
                    "spacings",
                    "patch_integrals",
                }
            )
        ):
            return False
        expected_spacings = {
            "midpoint": (FINITE_VOLUME["midpoint_bounds"][1] - FINITE_VOLUME["midpoint_bounds"][0])
            / cells,
            "relative_parallel": (
                FINITE_VOLUME["relative_parallel_bounds"][1]
                - FINITE_VOLUME["relative_parallel_bounds"][0]
            )
            / cells,
            "relative_perp": PHYSICAL_PARAMETERS["transverse_width"] / cells,
        }
        spacing_error = max(
            abs(factors["spacings"][key] - expected) for key, expected in expected_spacings.items()
        )
        patch_error = max(abs(item - 1.0) for item in factors["patch_integrals"])
        initial_error = max(
            abs(factors["midpoint_initial_mass"] - 1.0),
            abs(factors["relative_initial_mass"] - 1.0),
        )
        exact_contact = math.pi * PHYSICAL_PARAMETERS["contact_radius"] ** 2
        contact_exact_error = abs(factors["contact_area_exact"] - exact_contact)
        contact_error = abs(factors["contact_area"] - factors["contact_area_exact"])
        patch_estimate = factors["maximum_patch_quadrature_error_estimate"]
        initial_estimate = factors["maximum_initial_quadrature_error_estimate"]
        contact_estimate = factors["contact_area_error_estimate"]
        row_errors = (
            factors["midpoint_generator_row_error"],
            factors["relative_generator_row_error"],
        )
        scalar_values = [
            *factors["spacings"].values(),
            *factors["patch_integrals"],
            patch_estimate,
            factors["midpoint_initial_mass"],
            factors["relative_initial_mass"],
            initial_estimate,
            factors["contact_area"],
            factors["contact_area_exact"],
            contact_estimate,
            *row_errors,
        ]
        if not all(math.isfinite(item) for item in scalar_values):
            return False
        mass_tolerance = FACTOR_GATES["maximum_mass_or_conservation_error"]
        estimate_tolerance = FACTOR_GATES["maximum_quadrature_error_estimate"]
        undercoverage = FACTOR_GATES["maximum_error_estimate_undercoverage"]
        return bool(
            spacing_error <= FACTOR_GATES["maximum_spacing_reconstruction_error"]
            and patch_error <= mass_tolerance
            and initial_error <= mass_tolerance
            and contact_exact_error <= undercoverage
            and contact_error <= mass_tolerance
            and all(
                0.0 <= item <= estimate_tolerance
                for item in (
                    patch_estimate,
                    initial_estimate,
                    contact_estimate,
                )
            )
            and patch_error <= patch_estimate + undercoverage
            and initial_error <= initial_estimate + undercoverage
            and contact_error <= contact_estimate + undercoverage
            and all(
                0.0 <= item <= FACTOR_GATES["maximum_generator_row_error"] for item in row_errors
            )
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def law_gate_results(
    model_diagnostics: dict[str, Any], law_rows: Sequence[dict[str, float]]
) -> dict[str, bool]:
    """Common physical-law gates for cusps, folds, scans, tails, and controls."""

    rows = list(law_rows)
    gates = {
        "positive_density_and_survival": bool(
            rows
            and min(row["density"] for row in rows) > REPRESENTATIVE_GATES["minimum_density"]
            and min(row["survival"] for row in rows) > REPRESENTATIVE_GATES["minimum_survival"]
        ),
        "state_nonnegative": bool(
            rows
            and min(row["minimum_state_component"] for row in rows)
            >= -REPRESENTATIVE_GATES["maximum_negative_state_tolerance"]
        ),
        "survival_density_identity": bool(
            rows
            and max(row["survival_density_identity_error"] for row in rows)
            <= REPRESENTATIVE_GATES["maximum_survival_identity_error"]
        ),
        "generator_killing_identity": bool(
            model_diagnostics["generator_killing_identity_error"]
            <= REPRESENTATIVE_GATES["maximum_generator_killing_identity_error"]
        ),
        "differential_mass_balance": bool(
            rows
            and max(row["differential_mass_balance_error"] for row in rows)
            <= REPRESENTATIVE_GATES["maximum_differential_mass_balance_error"]
        ),
        "initial_mass": bool(
            model_diagnostics["initial_mass_error"]
            <= REPRESENTATIVE_GATES["maximum_initial_mass_error"]
        ),
        "installed_budget": bool(
            model_diagnostics["physical_installed_budget_absolute_error"]
            <= REPRESENTATIVE_GATES["maximum_installed_budget_error"]
        ),
        "finite_factor_diagnostics": factor_diagnostics_pass(model_diagnostics),
    }
    return sorted_bool_mapping(gates)


def scan_physical_gate_results(
    scan: dict[str, Any], model_diagnostics: dict[str, Any]
) -> dict[str, bool]:
    """Gate the complete scan and every bracket-refined root, not sparse traces only."""

    full_scan = scan["full_scan_trace"]
    bracketed = scan["all_bracketed_roots"]
    rows = [
        {
            "density": float(row["density"]),
            "survival": float(row["survival"]),
            "minimum_state_component": float(row["minimum_state_component"]),
            "survival_density_identity_error": float(row["differential_mass_balance_error"]),
            "differential_mass_balance_error": float(row["differential_mass_balance_error"]),
        }
        for row in full_scan
    ]
    root_rows = [
        {
            "density": float(BUDGET_HOMOTOPY["target_budget"] * row["density_per_budget"]),
            "survival": float(row["survival"]),
            "minimum_state_component": float(row["minimum_state_component"]),
            "survival_density_identity_error": float(row["differential_mass_balance_error"]),
            "differential_mass_balance_error": float(row["differential_mass_balance_error"]),
        }
        for row in bracketed
    ]
    base = law_gate_results(model_diagnostics, [*rows, *root_rows])
    all_roots_physical = bool(
        bracketed
        and all(
            float(row["density_per_budget"]) > REPRESENTATIVE_GATES["minimum_density"]
            and float(row["survival"]) > REPRESENTATIVE_GATES["minimum_survival"]
            and float(row["minimum_state_component"])
            >= -REPRESENTATIVE_GATES["maximum_negative_state_tolerance"]
            and float(row["differential_mass_balance_error"])
            <= REPRESENTATIVE_GATES["maximum_differential_mass_balance_error"]
            for row in bracketed
        )
    )
    gates = {
        "positive_density_and_survival": bool(
            base["positive_density_and_survival"]
            and float(scan["minimum_sampled_density"]) > REPRESENTATIVE_GATES["minimum_density"]
            and float(scan["minimum_sampled_survival"]) > REPRESENTATIVE_GATES["minimum_survival"]
        ),
        "state_nonnegative": bool(
            base["state_nonnegative"]
            and float(scan["minimum_sampled_state"])
            >= -REPRESENTATIVE_GATES["maximum_negative_state_tolerance"]
        ),
        "sampled_survival_monotone": bool(
            float(scan["maximum_sampled_survival_increase"])
            <= REPRESENTATIVE_GATES["maximum_survival_increase"]
        ),
        "survival_density_identity": bool(
            base["survival_density_identity"]
            and float(scan["maximum_sampled_differential_mass_balance_error"])
            <= REPRESENTATIVE_GATES["maximum_survival_identity_error"]
        ),
        "generator_killing_identity": base["generator_killing_identity"],
        "differential_mass_balance": bool(
            base["differential_mass_balance"]
            and float(scan["maximum_sampled_differential_mass_balance_error"])
            <= REPRESENTATIVE_GATES["maximum_differential_mass_balance_error"]
        ),
        "initial_mass": base["initial_mass"],
        "installed_budget": base["installed_budget"],
        "finite_factor_diagnostics": base["finite_factor_diagnostics"],
        "all_bracketed_roots_physical": all_roots_physical,
    }
    if set(gates) != set(SCAN_PHYSICAL_GATE_NAMES):
        raise RuntimeError("scan physical-gate schema changed")
    return sorted_bool_mapping(gates)


class KilledColumnOperator(LinearOperator):
    """Matrix-free column action of ``Q(theta,B)^T``."""

    def __init__(self, model: AllocationModel, budget: float, theta: np.ndarray) -> None:
        self.model = model
        self.budget = float(budget)
        if not math.isfinite(self.budget) or self.budget < 0.0:
            raise ValueError("budget must be finite and nonnegative")
        self.theta = np.asarray(theta, dtype=float).copy()
        self.weights = weights_from_theta(self.theta)
        if float(np.min(self.weights)) <= 0.0:
            raise ValueError("allocation left the strict simplex interior")
        self.kappa = np.asarray(self.weights @ model.patch_fields, dtype=float)
        self.midpoint = model.factors.midpoint_generator.tocsr()
        self.relative = model.factors.relative_generator.tocsr()
        self.midpoint_cells = int(self.midpoint.shape[0])
        self.relative_states = int(self.relative.shape[0])
        expected = self.midpoint_cells * self.relative_states
        if expected != model.state_count or self.kappa.shape != (expected,):
            raise ValueError("operator fields do not match tensor dimensions")
        self.kappa_matrix = self.kappa.reshape(self.midpoint_cells, self.relative_states)
        self.trace_value = float(
            self.relative_states * np.sum(self.midpoint.diagonal())
            + self.midpoint_cells * np.sum(self.relative.diagonal())
            - self.budget * np.sum(self.kappa)
        )
        super().__init__(dtype=np.dtype(np.float64), shape=(expected, expected))

    def _column(self, vector: np.ndarray) -> np.ndarray:
        shaped = np.asarray(vector, dtype=float).reshape(self.midpoint_cells, self.relative_states)
        output = self.midpoint.T @ shaped
        output += (self.relative.T @ shaped.T).T
        output -= self.budget * self.kappa_matrix * shaped
        return np.asarray(output, dtype=float).reshape(-1)

    def _row(self, vector: np.ndarray) -> np.ndarray:
        shaped = np.asarray(vector, dtype=float).reshape(self.midpoint_cells, self.relative_states)
        output = self.midpoint @ shaped
        output += (self.relative @ shaped.T).T
        output -= self.budget * self.kappa_matrix * shaped
        return np.asarray(output, dtype=float).reshape(-1)

    def _matvec(self, vector: np.ndarray) -> np.ndarray:
        return self._column(vector)

    def _rmatvec(self, vector: np.ndarray) -> np.ndarray:
        return self._row(vector)

    def _matmat(self, matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix, dtype=float)
        return np.column_stack([self._column(value[:, index]) for index in range(value.shape[1])])

    def _rmatmat(self, matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix, dtype=float)
        return np.column_stack([self._row(value[:, index]) for index in range(value.shape[1])])


class AllocationTangentOperator(LinearOperator):
    """Block column generator for ``(p,p_theta1,p_theta2)``."""

    def __init__(self, base: KilledColumnOperator) -> None:
        self.base = base
        self.states = base.shape[0]
        self.trace_value = 3.0 * base.trace_value
        super().__init__(dtype=np.dtype(np.float64), shape=(3 * self.states, 3 * self.states))

    def _matvec(self, vector: np.ndarray) -> np.ndarray:
        value = np.asarray(vector, dtype=float)
        p, s1, s2 = np.split(value, (self.states, 2 * self.states))
        fields = self.base.model.direction_fields
        return np.concatenate(
            (
                self.base.matvec(p),
                self.base.matvec(s1) - self.base.budget * fields[0] * p,
                self.base.matvec(s2) - self.base.budget * fields[1] * p,
            )
        )

    def _rmatvec(self, vector: np.ndarray) -> np.ndarray:
        value = np.asarray(vector, dtype=float)
        left, right1, right2 = np.split(value, (self.states, 2 * self.states))
        fields = self.base.model.direction_fields
        return np.concatenate(
            (
                self.base.rmatvec(left)
                - self.base.budget * (fields[0] * right1 + fields[1] * right2),
                self.base.rmatvec(right1),
                self.base.rmatvec(right2),
            )
        )

    def _matmat(self, matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix, dtype=float)
        return np.column_stack([self._matvec(value[:, index]) for index in range(value.shape[1])])

    def _rmatmat(self, matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix, dtype=float)
        return np.column_stack([self._rmatvec(value[:, index]) for index in range(value.shape[1])])


def propagate(
    operator: LinearOperator, initial: np.ndarray, time: float, trace_value: float
) -> np.ndarray:
    if not math.isfinite(time) or time < 0.0:
        raise ValueError("propagation time must be finite and nonnegative")
    if time == 0.0:
        return np.asarray(initial, dtype=float).copy()
    with pinned_numpy_seed(int(REPRODUCIBILITY["numpy_global_seed"])):
        return np.asarray(
            expm_multiply(time * operator, initial, traceA=time * trace_value), dtype=float
        )


def observable_recurrences(
    operator: KilledColumnOperator, maximum_order: int = 4
) -> tuple[np.ndarray, np.ndarray]:
    observables = [operator.kappa.copy()]
    tangents = [operator.model.direction_fields.copy()]
    for _ in range(maximum_order):
        previous = observables[-1]
        previous_tangents = tangents[-1]
        observables.append(np.asarray(operator.rmatvec(previous), dtype=float))
        tangents.append(
            np.asarray(
                [
                    operator.rmatvec(previous_tangents[index])
                    - operator.budget * operator.model.direction_fields[index] * previous
                    for index in range(2)
                ]
            )
        )
    return np.asarray(observables), np.asarray(tangents)


def evaluate_point(
    model: AllocationModel, time: float, budget: float, theta: np.ndarray
) -> Snapshot:
    base = KilledColumnOperator(model, budget, theta)
    augmented = AllocationTangentOperator(base)
    initial = np.concatenate((model.initial, np.zeros(2 * model.state_count)))
    propagated = propagate(augmented, initial, float(time), augmented.trace_value)
    state = propagated[: model.state_count]
    state_tangents = propagated[model.state_count :].reshape(2, model.state_count)
    observables, observable_tangents = observable_recurrences(base)
    jets = np.asarray([float(state @ observable) for observable in observables])
    allocation_jets = np.asarray(
        [
            [
                float(state_tangents[index] @ observables[order])
                + float(state @ observable_tangents[order, index])
                for order in range(5)
            ]
            for index in range(2)
        ]
    )
    cusp_map = jets[1:4].copy()
    cusp_jacobian = np.asarray(
        (
            (jets[2], allocation_jets[0, 1], allocation_jets[1, 1]),
            (jets[3], allocation_jets[0, 2], allocation_jets[1, 2]),
            (jets[4], allocation_jets[0, 3], allocation_jets[1, 3]),
        )
    )
    survival_identities = np.asarray(
        [
            abs(float(np.sum(base.matvec(state))) + float(state @ base.kappa) * budget),
            *[
                abs(
                    float(
                        np.sum(
                            base.matvec(state_tangents[index])
                            - budget * model.direction_fields[index] * state
                        )
                    )
                    + budget
                    * float(
                        state_tangents[index] @ base.kappa + state @ model.direction_fields[index]
                    )
                )
                for index in range(2)
            ],
        ]
    )
    for name, value in (
        ("state", state),
        ("state tangents", state_tangents),
        ("time jets", jets),
        ("allocation jets", allocation_jets),
        ("cusp map", cusp_map),
        ("cusp Jacobian", cusp_jacobian),
        ("survival identities", survival_identities),
    ):
        if not np.all(np.isfinite(value)):
            raise ValueError(f"{name} is nonfinite")
    return Snapshot(
        float(time),
        float(budget),
        np.asarray(theta, dtype=float).copy(),
        base.weights.copy(),
        state,
        state_tangents,
        jets,
        allocation_jets,
        cusp_map,
        cusp_jacobian,
        survival_identities,
    )


def evaluate_without_tangents(
    model: AllocationModel, time: float, budget: float, theta: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    operator = KilledColumnOperator(model, budget, theta)
    state = propagate(operator, model.initial, float(time), operator.trace_value)
    observables, _ = observable_recurrences(operator)
    jets = np.asarray([float(state @ observable) for observable in observables])
    if not np.all(np.isfinite(state)) or not np.all(np.isfinite(jets)):
        raise ValueError("state or observable jets are nonfinite")
    return state, jets


def dimensionless_residual(snapshot: Snapshot) -> np.ndarray:
    density = float(snapshot.jets[0])
    if density <= 0.0 or not math.isfinite(density):
        raise ValueError("density must be finite and positive")
    time = snapshot.time
    return (
        np.asarray(
            (time * snapshot.jets[1], time**2 * snapshot.jets[2], time**3 * snapshot.jets[3])
        )
        / density
    )


def dimensionless_jacobian(snapshot: Snapshot) -> np.ndarray:
    density = float(snapshot.jets[0])
    time = snapshot.time
    row_scale = np.asarray((time / density, time**2 / density, time**3 / density))
    column_scale = np.asarray((time, 1.0, 1.0))
    return row_scale[:, None] * snapshot.cusp_jacobian * column_scale[None, :]


def solve_cusp(
    evaluator: Callable[[float, float, np.ndarray], Snapshot],
    budget: float,
    initial_point: np.ndarray,
) -> CuspSolve:
    point = np.asarray(initial_point, dtype=float).copy()
    if point.shape != (3,):
        raise ValueError("initial cusp point must be a three-vector")
    inside, reason = point_in_trust_box(float(point[0]), point[1:])
    if not inside:
        return CuspSolve(HOLD_STATUS, False, 0, None, reason)
    last: Snapshot | None = None
    for iteration in range(int(SOLVER["maximum_newton_iterations"]) + 1):
        try:
            current = evaluator(float(point[0]), float(budget), point[1:])
            norm = float(np.max(np.abs(dimensionless_residual(current))))
        except (ArithmeticError, RuntimeError, ValueError) as error:
            return CuspSolve(HOLD_STATUS, False, iteration, None, f"evaluation:{error}")
        last = current
        if math.isfinite(norm) and norm <= SOLVER["scaled_residual_tolerance"]:
            return CuspSolve("PASS_CUSP_SOLVE", True, iteration, current, "converged")
        if iteration == SOLVER["maximum_newton_iterations"]:
            break
        try:
            step = np.linalg.solve(current.cusp_jacobian, -current.cusp_map)
        except np.linalg.LinAlgError:
            return CuspSolve(HOLD_STATUS, False, iteration, current, "singular_jacobian")
        if not np.all(np.isfinite(step)):
            return CuspSolve(HOLD_STATUS, False, iteration, current, "nonfinite_step")
        accepted = False
        for halving in range(int(SOLVER["maximum_step_halvings"]) + 1):
            candidate = point + step / 2**halving
            if not point_in_trust_box(float(candidate[0]), candidate[1:])[0]:
                continue
            try:
                candidate_snapshot = evaluator(float(candidate[0]), float(budget), candidate[1:])
                candidate_norm = float(np.max(np.abs(dimensionless_residual(candidate_snapshot))))
            except (ArithmeticError, RuntimeError, ValueError):
                continue
            if math.isfinite(candidate_norm) and candidate_norm < norm:
                point = candidate
                accepted = True
                break
        if not accepted:
            return CuspSolve(HOLD_STATUS, False, iteration, current, "line_search_failed")
    return CuspSolve(
        HOLD_STATUS,
        False,
        int(SOLVER["maximum_newton_iterations"]),
        last,
        "maximum_iterations",
    )


def run_homotopy(model: AllocationModel) -> dict[str, Any]:
    def evaluator(time: float, budget: float, theta: np.ndarray) -> Snapshot:
        return evaluate_point(model, time, budget, theta)

    point = np.asarray(BUDGET_HOMOTOPY["initial_point_each_mesh"], dtype=float)
    rows: list[dict[str, Any]] = []
    final_snapshot: Snapshot | None = None
    for budget in BUDGET_HOMOTOPY["schedule"]:
        solve = solve_cusp(evaluator, float(budget), point)
        row: dict[str, Any] = {
            "budget": float(budget),
            "status": solve.status,
            "converged": solve.converged,
            "iterations": solve.iterations,
            "reason": solve.reason,
            "point": None,
            "maximum_scaled_residual": None,
        }
        if solve.snapshot is not None:
            row["point"] = [
                solve.snapshot.time,
                *solve.snapshot.theta.tolist(),
            ]
            row["maximum_scaled_residual"] = float(
                np.max(np.abs(dimensionless_residual(solve.snapshot)))
            )
        rows.append(row)
        if not solve.converged or solve.snapshot is None:
            return {"status": HOLD_STATUS, "rows": rows, "snapshot": None}
        final_snapshot = solve.snapshot
        point = np.asarray((final_snapshot.time, *final_snapshot.theta))
    return {"status": "PASS_HOMOTOPY", "rows": rows, "snapshot": final_snapshot}


def finite_difference_audit(model: AllocationModel, snapshot: Snapshot) -> dict[str, Any]:
    rows: list[dict[str, float]] = []
    analytic = dimensionless_jacobian(snapshot)
    for allocation_step, relative_time_step in zip(
        DERIVATIVE_AUDIT["allocation_steps"],
        DERIVATIVE_AUDIT["relative_time_steps"],
        strict=True,
    ):
        time_step = float(relative_time_step) * snapshot.time
        plus = evaluate_without_tangents(
            model, snapshot.time + time_step, snapshot.budget, snapshot.theta
        )[1][1:4]
        minus = evaluate_without_tangents(
            model, snapshot.time - time_step, snapshot.budget, snapshot.theta
        )[1][1:4]
        columns = [(plus - minus) / (2.0 * time_step)]
        state_errors: list[float] = []
        for index in range(2):
            increment = np.zeros(2)
            increment[index] = float(allocation_step)
            plus_state, plus_jets = evaluate_without_tangents(
                model,
                snapshot.time,
                snapshot.budget,
                snapshot.theta + increment,
            )
            minus_state, minus_jets = evaluate_without_tangents(
                model,
                snapshot.time,
                snapshot.budget,
                snapshot.theta - increment,
            )
            finite_state = (plus_state - minus_state) / (2.0 * allocation_step)
            denominator = max(float(np.linalg.norm(finite_state, ord=1)), 1.0e-300)
            state_errors.append(
                float(
                    np.linalg.norm(snapshot.state_tangents[index] - finite_state, ord=1)
                    / denominator
                )
            )
            columns.append((plus_jets[1:4] - minus_jets[1:4]) / (2.0 * allocation_step))
        raw = np.column_stack(columns)
        density = float(snapshot.jets[0])
        row_scale = np.asarray(
            (snapshot.time / density, snapshot.time**2 / density, snapshot.time**3 / density)
        )
        column_scale = np.asarray((snapshot.time, 1.0, 1.0))
        finite = row_scale[:, None] * raw * column_scale[None, :]
        rows.append(
            {
                "allocation_step": float(allocation_step),
                "relative_time_step": float(relative_time_step),
                "maximum_state_tangent_relative_l1_error": max(state_errors),
                "maximum_dimensionless_jacobian_error": float(np.max(np.abs(analytic - finite))),
            }
        )
    large, small = rows
    floor = float(DERIVATIVE_AUDIT["roundoff_floor"])
    factor = float(DERIVATIVE_AUDIT["required_error_reduction_factor"])
    state_decreased = small["maximum_state_tangent_relative_l1_error"] <= max(
        floor, factor * large["maximum_state_tangent_relative_l1_error"]
    )
    jacobian_decreased = small["maximum_dimensionless_jacobian_error"] <= max(
        floor, factor * large["maximum_dimensionless_jacobian_error"]
    )
    passed = bool(
        state_decreased
        and jacobian_decreased
        and small["maximum_state_tangent_relative_l1_error"]
        <= DERIVATIVE_AUDIT["maximum_normalized_disagreement"]
        and small["maximum_dimensionless_jacobian_error"]
        <= DERIVATIVE_AUDIT["maximum_normalized_disagreement"]
    )
    return {
        "rows": rows,
        "state_error_decrease_or_floor": bool(state_decreased),
        "jacobian_error_decrease_or_floor": bool(jacobian_decreased),
        "passed": passed,
    }


def cusp_diagnostics(
    model: AllocationModel, snapshot: Snapshot, derivative: dict[str, Any]
) -> dict[str, Any]:
    scaled = dimensionless_jacobian(snapshot)
    projected = scaled[:2, 1:]
    projected_singular = np.linalg.svd(projected, compute_uv=False)
    full_singular = np.linalg.svd(scaled, compute_uv=False)
    fourth = float(snapshot.time**4 * snapshot.jets[4] / snapshot.jets[0])
    determinant_left = float(np.linalg.det(scaled))
    determinant_right = float(fourth * np.linalg.det(projected))
    denominator = max(abs(determinant_left), abs(determinant_right), 1.0e-300)
    model_diagnostics = allocation_model_diagnostics(model, snapshot.budget, snapshot.theta)
    law = state_law_diagnostics(
        model, snapshot.budget, snapshot.theta, snapshot.state, snapshot.jets
    )
    physical_gates = law_gate_results(model_diagnostics, [law])
    diagnostics = {
        "maximum_dimensionless_residual": float(np.max(np.abs(dimensionless_residual(snapshot)))),
        "minimum_weight": float(np.min(snapshot.weights)),
        "scaled_fourth_derivative": fourth,
        "projected_singular_values": projected_singular.tolist(),
        "projected_singular_value_ratio": (
            float(projected_singular[-1] / projected_singular[0])
            if projected_singular[0] > 0.0
            else 0.0
        ),
        "full_smallest_singular_value": float(full_singular[-1]),
        "determinant_factorization_relative_residual": float(
            abs(determinant_left - determinant_right) / denominator
        ),
        "maximum_survival_identity_residual": float(np.max(snapshot.survival_identity_residuals)),
        "model_diagnostics": model_diagnostics,
        "state_law_diagnostics": law,
        "dimensionless_jacobian": scaled.tolist(),
        "derivative_audit": derivative,
    }
    gates = {
        "cusp_residual": diagnostics["maximum_dimensionless_residual"]
        <= CUSP_GATES["maximum_dimensionless_residual"],
        "simplex_margin": diagnostics["minimum_weight"] >= CUSP_GATES["minimum_simplex_weight"],
        "quartic_nondegeneracy": abs(fourth)
        >= CUSP_GATES["minimum_absolute_scaled_fourth_derivative"],
        "projected_rank_floor": projected_singular[-1]
        >= CUSP_GATES["minimum_projected_second_singular_value"],
        "projected_rank_ratio": diagnostics["projected_singular_value_ratio"]
        >= CUSP_GATES["minimum_projected_singular_value_ratio"],
        "full_jacobian_rank": full_singular[-1]
        >= CUSP_GATES["minimum_full_jacobian_singular_value"],
        "determinant_factorization": diagnostics["determinant_factorization_relative_residual"]
        <= CUSP_GATES["maximum_determinant_factorization_relative_residual"],
        "mixed_jet_audit": bool(derivative["passed"]),
        "survival_identities": diagnostics["maximum_survival_identity_residual"]
        <= CUSP_GATES["maximum_explicit_action_residual"],
        **physical_gates,
    }
    diagnostics["gates"] = sorted_bool_mapping(gates)
    diagnostics["all_gates_passed"] = bool(all(gates.values()))
    return diagnostics


def serialize_snapshot(snapshot: Snapshot, model: AllocationModel | None = None) -> dict[str, Any]:
    row = {
        "time": snapshot.time,
        "budget": snapshot.budget,
        "theta": snapshot.theta.tolist(),
        "weights": snapshot.weights.tolist(),
        "density_per_budget": float(snapshot.jets[0]),
        "per_budget_time_jets_0_to_4": snapshot.jets.tolist(),
        "allocation_time_jets": snapshot.allocation_jets.tolist(),
    }
    if model is not None:
        row["state_law_diagnostics"] = state_law_diagnostics(
            model, snapshot.budget, snapshot.theta, snapshot.state, snapshot.jets
        )
    return row


def explicit_csr_preflight(model: AllocationModel) -> dict[str, Any]:
    theta = np.asarray((0.013, -0.009))
    budget = 0.01
    base = KilledColumnOperator(model, budget, theta)
    augmented = AllocationTangentOperator(base)
    midpoint_states = model.factors.midpoint_generator.shape[0]
    relative_states = model.factors.relative_generator.shape[0]
    free = sparse.kron(
        model.factors.midpoint_generator,
        sparse.eye(relative_states, format="csr"),
        format="csr",
    ) + sparse.kron(
        sparse.eye(midpoint_states, format="csr"),
        model.factors.relative_generator,
        format="csr",
    )
    row = (free - sparse.diags(budget * base.kappa, format="csr")).tocsr()
    column = row.T.tocsr()
    zero = sparse.csr_matrix(column.shape)
    couplings = [sparse.diags(-budget * field, format="csr") for field in model.direction_fields]
    explicit_augmented = sparse.bmat(
        (
            (column, zero, zero),
            (couplings[0], column, zero),
            (couplings[1], zero, column),
        ),
        format="csr",
    )
    vector = np.sin(np.arange(model.state_count) + 0.31)
    block_vector = np.cos(np.arange(3 * model.state_count) + 0.17)
    errors = {
        "column_action": float(np.max(np.abs(base.matvec(vector) - row.T @ vector))),
        "row_action": float(np.max(np.abs(base.rmatvec(vector) - row @ vector))),
        "augmented_column_action": float(
            np.max(np.abs(augmented.matvec(block_vector) - explicit_augmented @ block_vector))
        ),
        "augmented_row_action": float(
            np.max(np.abs(augmented.rmatvec(block_vector) - explicit_augmented.T @ block_vector))
        ),
    }
    return {
        "mesh": [model.cells] * 3,
        "state_count": model.state_count,
        "errors": errors,
        "maximum_error": max(errors.values()),
        "passed": max(errors.values()) <= CUSP_GATES["maximum_explicit_action_residual"],
    }


def density_jets_at(
    model: AllocationModel, budget: float, theta: np.ndarray, time: float
) -> tuple[np.ndarray, np.ndarray]:
    return evaluate_without_tangents(model, time, budget, theta)


def stationary_scan(
    model: AllocationModel, budget: float, theta: np.ndarray, spacing: float
) -> dict[str, Any]:
    start, stop = (float(value) for value in ROOT_SEARCH["time_window"])
    points = int(round((stop - start) / spacing)) + 1
    times = start + spacing * np.arange(points)
    operator = KilledColumnOperator(model, budget, theta)
    observables, _tangents = observable_recurrences(operator, maximum_order=2)
    state = propagate(operator, model.initial, start, operator.trace_value)
    projected: list[tuple[float, float, float, float, float, float, float]] = []
    minimum_state = float(np.min(state))
    full_scan_trace: list[dict[str, float]] = []
    saved_trace: list[dict[str, float]] = []
    trace_stride = int(round(float(ROOT_SEARCH["saved_trace_spacing"]) / spacing))
    if trace_stride < 1 or abs(trace_stride * spacing - ROOT_SEARCH["saved_trace_spacing"]) > 1e-12:
        raise ValueError("saved trace spacing is inconsistent with the scan grid")
    chunk_points = int(ROOT_SEARCH["chunk_points"])
    produced = 0
    while produced < points:
        count = min(chunk_points, points - produced)
        if produced == 0:
            chunk_start_state = state
            include_start = True
        else:
            chunk_start_state = state
            include_start = False
            count += 1
        duration = spacing * (count - 1)
        if count == 1:
            states = np.asarray([chunk_start_state])
        else:
            with pinned_numpy_seed(int(REPRODUCIBILITY["numpy_global_seed"])):
                states = np.asarray(
                    expm_multiply(
                        operator,
                        chunk_start_state,
                        start=0.0,
                        stop=duration,
                        num=count,
                        endpoint=True,
                        traceA=operator.trace_value,
                    )
                )
        selected = states if include_start else states[1:]
        if not np.all(np.isfinite(selected)):
            raise ValueError("stationary scan produced a nonfinite state")
        minimum_state = min(minimum_state, float(np.min(selected)))
        for selected_state in selected:
            density_per_budget = float(selected_state @ observables[0])
            survival = float(np.sum(selected_state))
            survival_derivative = float(np.sum(operator.matvec(selected_state)))
            differential_error = float(abs(survival_derivative + budget * density_per_budget))
            projected.append(
                (
                    density_per_budget,
                    float(selected_state @ observables[1]),
                    float(selected_state @ observables[2]),
                    survival,
                    budget * density_per_budget,
                    differential_error,
                    float(np.min(selected_state)),
                )
            )
        produced += len(selected)
        state = states[-1]
    if len(projected) != points:
        raise RuntimeError("streamed stationary scan produced the wrong number of rows")
    values = np.asarray(projected, dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("stationary scan projection is nonfinite")
    for index, (time_value, projection) in enumerate(zip(times, values, strict=True)):
        trace_row = {
            "time": float(time_value),
            "density": float(projection[4]),
            "density_per_budget": float(projection[0]),
            "first_derivative_per_budget": float(projection[1]),
            "second_derivative_per_budget": float(projection[2]),
            "survival": float(projection[3]),
            "minimum_state_component": float(projection[6]),
            "differential_mass_balance_error": float(projection[5]),
        }
        full_scan_trace.append(trace_row)
        if index % trace_stride == 0 or index == points - 1:
            saved_trace.append(dict(trace_row))
    brackets: list[tuple[float, float]] = []
    for index in range(points - 1):
        left = float(values[index, 1])
        right = float(values[index + 1, 1])
        if left == 0.0:
            brackets.append((float(times[index]), float(times[index])))
        elif left * right < 0.0:
            brackets.append((float(times[index]), float(times[index + 1])))
    roots: list[dict[str, Any]] = []
    reference_density = float(np.max(values[:, 0]))
    for bracket_index, (left, right) in enumerate(brackets):
        if left == right:
            root_time = left
        else:
            root_time = float(
                brentq(
                    lambda time: density_jets_at(model, budget, theta, time)[1][1],
                    left,
                    right,
                    xtol=float(ROOT_SEARCH["brent_absolute_tolerance"]),
                    rtol=float(ROOT_SEARCH["brent_relative_tolerance"]),
                    maxiter=int(ROOT_SEARCH["maximum_brent_iterations"]),
                )
            )
        state, jets = density_jets_at(model, budget, theta, root_time)
        density = float(jets[0])
        law = state_law_diagnostics(model, budget, theta, state, jets)
        positive_density = bool(density > 0.0 and reference_density > 0.0)
        scaled_residual = abs(root_time * float(jets[1]) / density) if positive_density else None
        scaled_curvature = root_time**2 * float(jets[2]) / density if positive_density else None
        density_eligible = bool(
            positive_density
            and density >= ROOT_SEARCH["relative_density_floor"] * reference_density
        )
        residual_eligible = bool(
            scaled_residual is not None
            and scaled_residual <= ROOT_SEARCH["maximum_scaled_root_residual"]
        )
        curvature_eligible = bool(
            scaled_curvature is not None
            and abs(scaled_curvature) >= ROOT_SEARCH["minimum_absolute_scaled_curvature"]
        )
        duplicate = bool(roots and root_time - roots[-1]["time"] < 1.0e-8)
        reasons = []
        if not density_eligible:
            reasons.append("density_floor_or_positivity")
        if not residual_eligible:
            reasons.append("scaled_root_residual")
        if not curvature_eligible:
            reasons.append("scaled_curvature")
        if duplicate:
            reasons.append("duplicate_refined_root")
        roots.append(
            {
                "bracket_index": bracket_index,
                "bracket": [left, right],
                "time": root_time,
                "density_per_budget": density,
                "scaled_root_residual": scaled_residual,
                "scaled_curvature": scaled_curvature,
                "type": (
                    "maximum"
                    if scaled_curvature is not None and scaled_curvature < 0.0
                    else "minimum"
                ),
                "survival": float(np.sum(state)),
                "minimum_state_component": float(np.min(state)),
                "differential_mass_balance_error": law["differential_mass_balance_error"],
                "density_eligible": density_eligible,
                "residual_eligible": residual_eligible,
                "curvature_eligible": curvature_eligible,
                "duplicate_refined_root": duplicate,
                "eligible": bool(
                    density_eligible and residual_eligible and curvature_eligible and not duplicate
                ),
                "separation_eligible": True,
                "eligibility_reasons": reasons,
            }
        )
    minimum_separation = float(ROOT_SEARCH["minimum_root_separation"])
    distinct = [root for root in roots if not root["duplicate_refined_root"]]
    for index, root in enumerate(distinct):
        left_gap = root["time"] - distinct[index - 1]["time"] if index > 0 else math.inf
        right_gap = (
            distinct[index + 1]["time"] - root["time"] if index + 1 < len(distinct) else math.inf
        )
        separated = min(left_gap, right_gap) >= minimum_separation
        root["separation_eligible"] = bool(separated)
        root["eligible"] = bool(root["eligible"] and separated)
        if not separated:
            root["eligibility_reasons"].append("minimum_root_separation")
    eligible_roots = [root for root in roots if root["eligible"]]
    return {
        "spacing": spacing,
        "time_window": [start, stop],
        "grid_point_count": points,
        "reference_maximum_density_per_budget": reference_density,
        "endpoint_first_derivatives_per_budget": [
            float(values[0, 1]),
            float(values[-1, 1]),
        ],
        "endpoint_signs_passed": bool(values[0, 1] > 0.0 and values[-1, 1] < 0.0),
        "minimum_sampled_state": minimum_state,
        "minimum_sampled_density": float(np.min(values[:, 4])),
        "minimum_sampled_survival": float(np.min(values[:, 3])),
        "maximum_sampled_survival_increase": float(
            max(0.0, np.max(np.diff(values[:, 3]))) if len(values) > 1 else 0.0
        ),
        "maximum_sampled_differential_mass_balance_error": float(np.max(values[:, 5])),
        "full_scan_trace": full_scan_trace,
        "saved_trace": saved_trace,
        "roots": eligible_roots,
        "all_bracketed_roots": roots,
        "topology": [root["type"] for root in eligible_roots],
    }


def assess_remote_pair(scan: dict[str, Any], cusp_time: float) -> dict[str, Any]:
    roots = list(scan["roots"])
    lineage = []
    for index, root in enumerate(roots):
        side = "positive_time" if float(root["time"]) > cusp_time else "negative_time"
        lineage.append(
            {
                "global_root_ordinal": index,
                "type": root["type"],
                "side": side,
                "time": float(root["time"]),
                "origin_bracket_index": int(root["bracket_index"]),
                "previous_bracket_index": int(root["bracket_index"]),
                "current_bracket_index": int(root["bracket_index"]),
                "predecessor_global_root_ordinal": index - 1 if index > 0 else None,
                "successor_global_root_ordinal": index + 1 if index + 1 < len(roots) else None,
                "matched_previous_global_root_ordinal": index,
                "adjacent_time_drift": 0.0,
            }
        )
    pair = None
    pair_identity = None
    for index, (left, right) in enumerate(zip(roots, roots[1:])):
        left_time = float(left["time"])
        right_time = float(right["time"])
        outside = bool(
            abs(left_time - cusp_time) > REMOTE_PAIR["cusp_exclusion_radius"]
            and abs(right_time - cusp_time) > REMOTE_PAIR["cusp_exclusion_radius"]
        )
        same_side = (left_time - cusp_time) * (right_time - cusp_time) > 0.0
        separated = right_time - left_time >= REMOTE_PAIR["minimum_root_separation"]
        if (
            left["type"] == "maximum"
            and right["type"] == "minimum"
            and outside
            and same_side
            and separated
        ):
            side = "positive_time" if left_time > cusp_time else "negative_time"
            origin = [int(left["bracket_index"]), int(right["bracket_index"])]
            pair_identity = (
                f"{side}:maximum_minimum:global_{index}_{index + 1}:"
                f"origin_brackets_{origin[0]}_{origin[1]}"
            )
            pair = {
                "maximum": left,
                "minimum": right,
                "side": side,
                "pair_type": "maximum_minimum",
                "selected_global_root_indices": [index, index + 1],
                "origin_bracket_lineage": origin,
                "maximum_global_root_ordinal": index,
                "minimum_global_root_ordinal": index + 1,
                "maximum_bracket_index": origin[0],
                "minimum_bracket_index": origin[1],
                "eligible_root_count_at_anchor": len(roots),
            }
            break
    return {
        "remote_pair_present": pair is not None,
        "pair_identity": pair_identity,
        "anchor_pair_identity": pair_identity,
        "pair": pair,
        "root_lineage": lineage,
        "lineage_status": "CUSP_ANCHOR" if pair is not None else "HOLD_NO_ANCHOR_PAIR",
        "lineage_passed": pair is not None,
        "lineage_hold_reasons": [] if pair is not None else ["missing_cusp_anchor_pair"],
        "maximum_observed_adjacent_drift": 0.0,
        "candidate_search_bounded_to_frozen_window": True,
    }


def continue_remote_pair_lineage(
    scan: dict[str, Any],
    cusp_time: float,
    anchor: dict[str, Any],
    previous: dict[str, Any],
) -> dict[str, Any]:
    """Continue the cusp-anchored pair by global order and predecessor/successor."""

    roots = list(scan["roots"])
    anchor_lineage = anchor.get("root_lineage")
    previous_lineage = previous.get("root_lineage")
    reasons: list[str] = []
    if type(anchor_lineage) is not list or type(previous_lineage) is not list:
        reasons.append("unmatched_lineage")
        anchor_lineage = []
        previous_lineage = []
    if len(roots) != len(anchor_lineage) or len(roots) != len(previous_lineage):
        reasons.append("eligible_root_birth_or_death")
    lineage = []
    maximum_drift = 0.0
    for index, root in enumerate(roots):
        if index >= len(anchor_lineage) or index >= len(previous_lineage):
            reasons.append("unmatched_root")
            break
        origin = anchor_lineage[index]
        predecessor = previous_lineage[index]
        time = float(root["time"])
        side = "positive_time" if time > cusp_time else "negative_time"
        drift = abs(time - float(predecessor["time"]))
        maximum_drift = max(maximum_drift, drift)
        expected_predecessor = index - 1 if index > 0 else None
        expected_successor = index + 1 if index + 1 < len(roots) else None
        if (
            origin.get("global_root_ordinal") != index
            or predecessor.get("global_root_ordinal") != index
            or root.get("type") != origin.get("type")
            or root.get("type") != predecessor.get("type")
            or side != origin.get("side")
            or predecessor.get("predecessor_global_root_ordinal") != expected_predecessor
            or predecessor.get("successor_global_root_ordinal") != expected_successor
        ):
            reasons.append("root_crossing_type_side_or_order_change")
        if drift > REMOTE_PAIR["maximum_adjacent_root_time_drift"]:
            reasons.append("excess_adjacent_root_time_drift")
        lineage.append(
            {
                "global_root_ordinal": index,
                "type": root["type"],
                "side": side,
                "time": time,
                "origin_bracket_index": int(origin["origin_bracket_index"]),
                "previous_bracket_index": int(predecessor["current_bracket_index"]),
                "current_bracket_index": int(root["bracket_index"]),
                "predecessor_global_root_ordinal": expected_predecessor,
                "successor_global_root_ordinal": expected_successor,
                "matched_previous_global_root_ordinal": index,
                "adjacent_time_drift": float(drift),
            }
        )
    pair = None
    pair_identity = None
    anchor_pair = anchor.get("pair")
    selected = (
        anchor_pair.get("selected_global_root_indices") if type(anchor_pair) is dict else None
    )
    if (
        type(selected) is not list
        or len(selected) != 2
        or not all(type(value) is int for value in selected)
        or selected[1] != selected[0] + 1
        or selected[0] < 0
        or selected[1] >= len(roots)
    ):
        reasons.append("unmatched_anchor_pair")
    else:
        left_index, right_index = selected
        left = roots[left_index]
        right = roots[right_index]
        left_time = float(left["time"])
        right_time = float(right["time"])
        side = "positive_time" if left_time > cusp_time else "negative_time"
        pair_valid = bool(
            left["type"] == "maximum"
            and right["type"] == "minimum"
            and side == anchor_pair["side"]
            and (left_time - cusp_time) * (right_time - cusp_time) > 0.0
            and abs(left_time - cusp_time) > REMOTE_PAIR["cusp_exclusion_radius"]
            and abs(right_time - cusp_time) > REMOTE_PAIR["cusp_exclusion_radius"]
            and right_time - left_time >= REMOTE_PAIR["minimum_root_separation"]
        )
        if not pair_valid:
            reasons.append("selected_pair_type_side_or_separation_changed")
        else:
            pair_identity = anchor.get("pair_identity")
            pair = {
                "maximum": left,
                "minimum": right,
                "side": side,
                "pair_type": "maximum_minimum",
                "selected_global_root_indices": [left_index, right_index],
                "origin_bracket_lineage": list(anchor_pair["origin_bracket_lineage"]),
                "maximum_global_root_ordinal": left_index,
                "minimum_global_root_ordinal": right_index,
                "maximum_bracket_index": int(left["bracket_index"]),
                "minimum_bracket_index": int(right["bracket_index"]),
                "eligible_root_count_at_anchor": int(anchor_pair["eligible_root_count_at_anchor"]),
            }
    reasons = list(dict.fromkeys(reasons))
    passed = not reasons and pair is not None and len(lineage) == len(roots)
    return {
        "remote_pair_present": passed,
        "pair_identity": pair_identity,
        "anchor_pair_identity": anchor.get("pair_identity"),
        "pair": pair,
        "root_lineage": lineage,
        "lineage_status": "MATCHED_COMPARISON" if passed else "HOLD_LINEAGE",
        "lineage_passed": passed,
        "lineage_hold_reasons": reasons,
        "maximum_observed_adjacent_drift": float(maximum_drift),
        "candidate_search_bounded_to_frozen_window": True,
    }


def fold_predictor(snapshot: Snapshot, time_offset: float) -> np.ndarray:
    response = snapshot.cusp_jacobian[:2, 1:]
    fourth = float(snapshot.jets[4])
    eta = np.linalg.solve(
        response,
        np.asarray((fourth * time_offset**3 / 3.0, -fourth * time_offset**2 / 2.0)),
    )
    return np.asarray((snapshot.time + time_offset, *(snapshot.theta + eta)))


def correct_fold_fixed_time(
    evaluator: Callable[[float, float, np.ndarray], Snapshot],
    budget: float,
    initial_point: np.ndarray,
) -> dict[str, Any]:
    time = float(initial_point[0])
    theta = np.asarray(initial_point[1:], dtype=float).copy()
    for iteration in range(int(SOLVER["maximum_newton_iterations"]) + 1):
        if not point_in_trust_box(time, theta)[0]:
            return {"status": "HOLD_BRANCH", "snapshot": None, "iterations": iteration}
        try:
            snapshot = evaluator(time, budget, theta)
        except (ArithmeticError, RuntimeError, ValueError):
            return {
                "status": "HOLD_BRANCH",
                "snapshot": None,
                "iterations": iteration,
            }
        residual = dimensionless_residual(snapshot)[:2]
        norm = float(np.max(np.abs(residual)))
        if norm <= SOLVER["scaled_residual_tolerance"]:
            return {"status": "PASS_BRANCH_NODE", "snapshot": snapshot, "iterations": iteration}
        if iteration == SOLVER["maximum_newton_iterations"]:
            break
        try:
            step = np.linalg.solve(snapshot.cusp_jacobian[:2, 1:], -snapshot.cusp_map[:2])
        except np.linalg.LinAlgError:
            break
        accepted = False
        for halving in range(int(SOLVER["maximum_step_halvings"]) + 1):
            candidate = theta + step / 2**halving
            if not point_in_trust_box(time, candidate)[0]:
                continue
            try:
                candidate_snapshot = evaluator(time, budget, candidate)
            except (ArithmeticError, RuntimeError, ValueError):
                continue
            if float(np.max(np.abs(dimensionless_residual(candidate_snapshot)[:2]))) < norm:
                theta = candidate
                accepted = True
                break
        if not accepted:
            break
    return {
        "status": "HOLD_BRANCH",
        "snapshot": None,
        "iterations": int(SOLVER["maximum_newton_iterations"]),
    }


def fold_null_direction(snapshot: Snapshot, previous: np.ndarray | None) -> np.ndarray:
    _left, singular, right = np.linalg.svd(snapshot.fold_jacobian)
    if singular[-1] <= 1.0e-14:
        raise ValueError("rank-deficient fold Jacobian")
    direction = np.asarray(right[-1])
    direction /= np.linalg.norm(direction)
    if previous is not None and float(direction @ previous) < 0.0:
        direction = -direction
    return direction


def pseudo_arclength_correct(
    evaluator: Callable[[float, float, np.ndarray], Snapshot],
    budget: float,
    predictor: np.ndarray,
    direction: np.ndarray,
) -> dict[str, Any]:
    point = np.asarray(predictor, dtype=float).copy()
    direction = np.asarray(direction, dtype=float) / np.linalg.norm(direction)
    for iteration in range(int(SOLVER["maximum_newton_iterations"]) + 1):
        if not point_in_trust_box(float(point[0]), point[1:])[0]:
            return {"status": "HOLD_BRANCH", "snapshot": None, "iterations": iteration}
        try:
            snapshot = evaluator(float(point[0]), budget, point[1:])
        except (ArithmeticError, RuntimeError, ValueError):
            return {
                "status": "HOLD_BRANCH",
                "snapshot": None,
                "iterations": iteration,
            }
        residual = np.asarray(
            (
                dimensionless_residual(snapshot)[0],
                dimensionless_residual(snapshot)[1],
                float(direction @ (point - predictor)),
            )
        )
        norm = float(np.max(np.abs(residual)))
        if norm <= SOLVER["scaled_residual_tolerance"]:
            return {"status": "PASS_BRANCH_NODE", "snapshot": snapshot, "iterations": iteration}
        if iteration == SOLVER["maximum_newton_iterations"]:
            break
        raw = np.asarray((snapshot.cusp_map[0], snapshot.cusp_map[1], residual[2]))
        jacobian = np.vstack((snapshot.fold_jacobian, direction))
        try:
            step = np.linalg.solve(jacobian, -raw)
        except np.linalg.LinAlgError:
            break
        accepted = False
        for halving in range(int(SOLVER["maximum_step_halvings"]) + 1):
            candidate = point + step / 2**halving
            if not point_in_trust_box(float(candidate[0]), candidate[1:])[0]:
                continue
            try:
                candidate_snapshot = evaluator(float(candidate[0]), budget, candidate[1:])
            except (ArithmeticError, RuntimeError, ValueError):
                continue
            candidate_residual = np.asarray(
                (
                    dimensionless_residual(candidate_snapshot)[0],
                    dimensionless_residual(candidate_snapshot)[1],
                    float(direction @ (candidate - predictor)),
                )
            )
            if float(np.max(np.abs(candidate_residual))) < norm:
                point = candidate
                accepted = True
                break
        if not accepted:
            break
    return {
        "status": "HOLD_BRANCH",
        "snapshot": None,
        "iterations": int(SOLVER["maximum_newton_iterations"]),
    }


def serialize_fold_node(model: AllocationModel, snapshot: Snapshot, index: int) -> dict[str, Any]:
    scaled = dimensionless_jacobian(snapshot)[:2]
    singular = np.linalg.svd(scaled, compute_uv=False)
    try:
        model_diagnostics = allocation_model_diagnostics(model, snapshot.budget, snapshot.theta)
        state_law = state_law_diagnostics(
            model, snapshot.budget, snapshot.theta, snapshot.state, snapshot.jets
        )
        physical_gates = law_gate_results(model_diagnostics, [state_law])
    except (AttributeError, TypeError, ValueError):
        model_diagnostics = None
        state_law = None
        physical_gates = {
            "positive_density_and_survival": False,
            "state_nonnegative": False,
            "survival_density_identity": False,
            "generator_killing_identity": False,
            "differential_mass_balance": False,
            "initial_mass": False,
            "installed_budget": False,
            "finite_factor_diagnostics": False,
        }
    return {
        "acceptance_index": index,
        "time": snapshot.time,
        "theta": snapshot.theta.tolist(),
        "weights": snapshot.weights.tolist(),
        "normalized_fold_residual": float(np.max(np.abs(dimensionless_residual(snapshot)[:2]))),
        "scaled_third_derivative": abs(
            float(snapshot.time**3 * snapshot.jets[3] / snapshot.jets[0])
        ),
        "dimensionless_fold_singular_values": singular.tolist(),
        "model_diagnostics": model_diagnostics,
        "state_law_diagnostics": state_law,
        "physical_law_gates": physical_gates,
    }


def continue_branch(
    model: AllocationModel,
    cusp: Snapshot,
    time_offset: float,
    cusp_scan: dict[str, Any] | None = None,
    cusp_remote_pair: dict[str, Any] | None = None,
) -> dict[str, Any]:
    def hold() -> dict[str, Any]:
        return {
            "status": "HOLD_BRANCH",
            "orientation": "positive_time" if time_offset > 0.0 else "negative_time",
            "nodes": [],
            "comparison_nodes": None,
            "comparison_node_remote_pairs": None,
            "gates": {name: False for name in BRANCH_GATE_NAMES},
        }

    def evaluator(time: float, budget: float, theta: np.ndarray) -> Snapshot:
        return evaluate_point(model, time, budget, theta)

    try:
        predictor = fold_predictor(cusp, time_offset)
    except (np.linalg.LinAlgError, ValueError):
        return hold()
    seed = correct_fold_fixed_time(evaluator, cusp.budget, predictor)
    if seed["snapshot"] is None:
        return hold()
    current: Snapshot = seed["snapshot"]
    try:
        direction = fold_null_direction(current, None)
    except ValueError:
        return hold()
    desired_sign = 1.0 if time_offset > 0.0 else -1.0
    if desired_sign * direction[0] < 0.0:
        direction = -direction
    nodes = [serialize_fold_node(model, current, 0)]
    step = float(FOLD_CONTINUATION["initial_arclength_step"])
    for index in range(1, int(FOLD_CONTINUATION["maximum_accepted_noncusp_nodes"])):
        predictor = np.asarray((current.time, *current.theta)) + step * direction
        corrected = pseudo_arclength_correct(evaluator, cusp.budget, predictor, direction)
        if corrected["snapshot"] is None and step > FOLD_CONTINUATION["minimum_arclength_step"]:
            step = max(
                float(FOLD_CONTINUATION["minimum_arclength_step"]),
                step * float(FOLD_CONTINUATION["step_decrease_factor"]),
            )
            predictor = np.asarray((current.time, *current.theta)) + step * direction
            corrected = pseudo_arclength_correct(evaluator, cusp.budget, predictor, direction)
        if corrected["snapshot"] is None:
            break
        next_snapshot: Snapshot = corrected["snapshot"]
        try:
            next_direction = fold_null_direction(next_snapshot, direction)
        except ValueError:
            break
        current = next_snapshot
        direction = next_direction
        nodes.append(serialize_fold_node(model, current, index))
        iterations = int(corrected["iterations"])
        if iterations <= FOLD_CONTINUATION["increase_if_iterations_at_most"]:
            step = min(
                float(FOLD_CONTINUATION["maximum_arclength_step"]),
                step * float(FOLD_CONTINUATION["step_increase_factor"]),
            )
        elif iterations >= FOLD_CONTINUATION["decrease_if_iterations_at_least"]:
            step = max(
                float(FOLD_CONTINUATION["minimum_arclength_step"]),
                step * float(FOLD_CONTINUATION["step_decrease_factor"]),
            )
        if (
            abs(current.time - cusp.time) >= FOLD_CONTINUATION["stop_absolute_time_offset"]
            or float(np.min(current.weights)) <= SOLVER["minimum_simplex_weight"]
        ):
            break
    comparisons = []
    used_indices: set[int] = set()
    for target in FOLD_CONTINUATION["comparison_time_offsets"]:
        eligible = [
            node
            for node in nodes
            if desired_sign * (node["time"] - cusp.time) > 0.0
            and node["acceptance_index"] not in used_indices
        ]
        if not eligible:
            comparisons = []
            break
        chosen = min(
            eligible,
            key=lambda node: (
                abs(desired_sign * (node["time"] - cusp.time) - target),
                node["normalized_fold_residual"],
                node["acceptance_index"],
            ),
        )
        chosen = dict(chosen)
        chosen["signed_time_offset"] = float(desired_sign * (chosen["time"] - cusp.time))
        chosen["target_signed_time_offset"] = float(target)
        chosen["absolute_time_offset_mismatch"] = float(abs(chosen["signed_time_offset"] - target))
        comparisons.append(chosen)
        used_indices.add(int(chosen["acceptance_index"]))
    if comparisons and cusp_remote_pair is None:
        try:
            anchor_scan = (
                cusp_scan
                if cusp_scan is not None
                else stationary_scan(
                    model,
                    cusp.budget,
                    cusp.theta,
                    float(ROOT_SEARCH["mesh_65_spacing"]),
                )
            )
            cusp_remote_pair = assess_remote_pair(anchor_scan, cusp.time)
        except (ArithmeticError, KeyError, RuntimeError, TypeError, ValueError):
            cusp_remote_pair = None
    remote_pair_rows = []
    previous_remote = cusp_remote_pair
    for node in comparisons:
        scan = None
        try:
            scan = stationary_scan(
                model,
                cusp.budget,
                np.asarray(node["theta"], dtype=float),
                float(ROOT_SEARCH["mesh_65_spacing"]),
            )
            model_diagnostics = allocation_model_diagnostics(
                model, cusp.budget, np.asarray(node["theta"], dtype=float)
            )
            scan["physical_law_gates"] = scan_physical_gate_results(scan, model_diagnostics)
            if cusp_remote_pair is None or previous_remote is None:
                raise ValueError("missing cusp-anchor remote pair")
            remote = continue_remote_pair_lineage(
                scan, float(node["time"]), cusp_remote_pair, previous_remote
            )
            previous_remote = remote
        except (ArithmeticError, KeyError, RuntimeError, TypeError, ValueError) as error:
            remote = {
                "remote_pair_present": False,
                "pair_identity": None,
                "anchor_pair_identity": (
                    cusp_remote_pair.get("pair_identity")
                    if type(cusp_remote_pair) is dict
                    else None
                ),
                "pair": None,
                "root_lineage": [],
                "lineage_status": "HOLD_LINEAGE",
                "lineage_passed": False,
                "lineage_hold_reasons": [f"comparison_scan_or_lineage_failure:{error}"],
                "maximum_observed_adjacent_drift": 0.0,
                "candidate_search_bounded_to_frozen_window": True,
            }
        remote_pair_rows.append(
            {
                "acceptance_index": node["acceptance_index"],
                "time": node["time"],
                "remote_pair": remote,
                "stationary_scan": scan,
            }
        )
    pair_identities = [row["remote_pair"].get("pair_identity") for row in remote_pair_rows]
    gates = {
        "minimum_nodes": len(nodes) >= FOLD_CONTINUATION["minimum_accepted_noncusp_nodes"],
        "required_reach": bool(
            nodes
            and max(desired_sign * (node["time"] - cusp.time) for node in nodes)
            >= FOLD_CONTINUATION["required_absolute_time_reach"]
        ),
        "comparison_nodes_present": len(comparisons) == 3,
        "comparison_nodes_distinct": len({node["acceptance_index"] for node in comparisons})
        == len(FOLD_CONTINUATION["comparison_time_offsets"]),
        "comparison_nodes_on_signed_side": len(comparisons) == 3
        and all(node["signed_time_offset"] > 0.0 for node in comparisons),
        "comparison_offset_mismatch": len(comparisons) == 3
        and all(
            node["absolute_time_offset_mismatch"]
            <= FOLD_CONTINUATION["maximum_comparison_time_offset_mismatch"]
            for node in comparisons
        ),
        "fold_residuals": bool(
            nodes
            and max(node["normalized_fold_residual"] for node in nodes)
            <= FOLD_CONTINUATION["maximum_normalized_fold_residual"]
        ),
        "third_derivative": bool(
            nodes
            and all(
                node["scaled_third_derivative"]
                >= FOLD_CONTINUATION["minimum_scaled_third_derivative"]
                for node in nodes
                if abs(node["time"] - cusp.time) >= 0.25
            )
        ),
        "fold_rank": bool(
            nodes
            and all(
                node["dimensionless_fold_singular_values"][-1]
                >= FOLD_CONTINUATION["minimum_dimensionless_fold_singular_value"]
                for node in nodes
            )
        ),
        "physical_law": bool(
            nodes and all(all(node["physical_law_gates"].values()) for node in nodes)
        ),
        "comparison_scan_physical_law": len(remote_pair_rows) == 3
        and all(
            type(row["stationary_scan"]) is dict
            and type(row["stationary_scan"].get("physical_law_gates")) is dict
            and set(row["stationary_scan"]["physical_law_gates"]) == set(SCAN_PHYSICAL_GATE_NAMES)
            and all(row["stationary_scan"]["physical_law_gates"].values())
            for row in remote_pair_rows
        ),
        "remote_pair_retained": len(remote_pair_rows) == 3
        and all(row["remote_pair"]["remote_pair_present"] for row in remote_pair_rows),
        "stable_remote_pair_identity": len(pair_identities) == 3
        and pair_identities[0] is not None
        and len(set(pair_identities)) == 1,
        "remote_pair_lineage": len(remote_pair_rows) == 3
        and cusp_remote_pair is not None
        and cusp_remote_pair.get("lineage_passed") is True
        and all(row["remote_pair"].get("lineage_passed") is True for row in remote_pair_rows)
        and all(
            row["remote_pair"].get("maximum_observed_adjacent_drift", math.inf)
            <= REMOTE_PAIR["maximum_adjacent_root_time_drift"]
            for row in remote_pair_rows
        ),
    }
    if set(gates) != set(BRANCH_GATE_NAMES):
        raise RuntimeError("branch gate schema changed")
    return {
        "status": "PASS_BRANCH_DISCOVERY" if all(gates.values()) else "HOLD_BRANCH",
        "orientation": "positive_time" if time_offset > 0.0 else "negative_time",
        "nodes": nodes,
        "comparison_nodes": comparisons if comparisons else None,
        "comparison_node_remote_pairs": remote_pair_rows if comparisons else None,
        "gates": sorted_bool_mapping(gates),
    }


def control_evaluation_hold(
    theta: np.ndarray, reason: str, final_survival: float | None = None
) -> dict[str, Any]:
    """Fixed finite schema for a scientific numerical/structural HOLD."""

    value = np.asarray(theta, dtype=float)
    row = {
        "status": "HOLD_CONTROL_EVALUATION",
        "reason": str(reason),
        "theta": value.tolist() if value.shape == (2,) and np.all(np.isfinite(value)) else None,
        "weights": (
            weights_from_theta(value).tolist()
            if value.shape == (2,) and np.all(np.isfinite(value))
            else None
        ),
        "retained_maximum_count": 0,
        "topology": [],
        "stationary_scan": None,
        "roots": [],
        "all_bracketed_roots": [],
        "tail_trace": None,
        "model_diagnostics": None,
        "peak_minimum_to_maximum_ratio": None,
        "valley_to_smaller_peak_ratios": None,
        "event_basin_masses": None,
        "event_partition_closure_error": None,
        "final_survival": (
            float(final_survival)
            if final_survival is not None and math.isfinite(final_survival)
            else None
        ),
        "minimum_final_state_component": None,
        "score_term_margins": None,
        "robustness_score": None,
        "gates": {name: False for name in CONTROL_GATE_NAMES},
        "all_gates_passed": False,
    }
    require_finite_json(row)
    return row


def evaluate_control_law(
    model: AllocationModel, theta: np.ndarray, spacing: float
) -> dict[str, Any]:
    observed_final_survival: float | None = None
    try:
        value = np.asarray(theta, dtype=float)
        scan = stationary_scan(model, 0.01, value, spacing)
        model_diagnostics = allocation_model_diagnostics(model, 0.01, value)
        scan["physical_law_gates"] = scan_physical_gate_results(scan, model_diagnostics)
        roots = scan["roots"]
        topology = scan["topology"]
        maxima = [root for root in roots if root["type"] == "maximum"]
        minima = [root for root in roots if root["type"] == "minimum"]
        alternating = topology in (
            ["maximum"],
            ["maximum", "minimum", "maximum"],
            ["maximum", "minimum", "maximum", "minimum", "maximum"],
        )
        maximum_count = len(maxima) if alternating else 0
        peak_ratio = (
            min(root["density_per_budget"] for root in maxima)
            / max(root["density_per_budget"] for root in maxima)
            if maxima
            else 0.0
        )
        valley_ratios = []
        for index, root in enumerate(roots):
            if root["type"] == "minimum" and 0 < index < len(roots) - 1:
                adjacent = min(
                    roots[index - 1]["density_per_budget"],
                    roots[index + 1]["density_per_budget"],
                )
                valley_ratios.append(root["density_per_budget"] / adjacent)
        valley_ratio = max(valley_ratios) if valley_ratios else 0.0

        survival_values = [1.0]
        for root in minima:
            survival_values.append(float(root["survival"]))

        tail_trace = []
        final_state: np.ndarray | None = None
        final_jets: np.ndarray | None = None
        for checkpoint in REPRESENTATIVE_GATES["tail_checkpoints"]:
            state, jets = evaluate_without_tangents(model, float(checkpoint), 0.01, value)
            law = state_law_diagnostics(model, 0.01, value, state, jets)
            tail_trace.append({"time": float(checkpoint), **law})
            final_state, final_jets = state, jets
        if final_state is None or final_jets is None:
            raise RuntimeError("tail trace is empty")
        observed_final_survival = float(np.sum(final_state))
        survival_values.append(observed_final_survival)
        masses = [
            survival_values[index] - survival_values[index + 1]
            for index in range(len(survival_values) - 1)
        ]
        closure_error = float(abs(sum(masses) - (1.0 - observed_final_survival)))
        minimum_curvature = min(
            (abs(float(root["scaled_curvature"])) for root in roots), default=0.0
        )
        maximum_residual = max(
            (float(root["scaled_root_residual"]) for root in roots), default=None
        )
        margins = {
            "peak_ratio": (peak_ratio / REPRESENTATIVE_GATES["minimum_peak_ratio"] - 1.0),
            "valley_ratio": (
                (REPRESENTATIVE_GATES["maximum_valley_ratio"] - valley_ratio)
                / (1.0 - REPRESENTATIVE_GATES["maximum_valley_ratio"])
            ),
            "absolute_scaled_curvature": (
                minimum_curvature / REPRESENTATIVE_GATES["minimum_absolute_scaled_curvature"] - 1.0
            ),
            "event_basin_mass": (
                min(masses, default=0.0) / REPRESENTATIVE_GATES["minimum_each_event_basin_mass"]
                - 1.0
            ),
        }
        score = min(margins[name] for name in PHASE_SEARCH["score_terms"])
        scan_law_rows = [
            {
                "density": float(row["density"]),
                "survival": float(row["survival"]),
                "minimum_state_component": float(row["minimum_state_component"]),
                "survival_density_identity_error": float(row["differential_mass_balance_error"]),
                "differential_mass_balance_error": float(row["differential_mass_balance_error"]),
            }
            for row in scan["saved_trace"]
        ]
        root_law_rows = [
            {
                "density": float(0.01 * root["density_per_budget"]),
                "survival": float(root["survival"]),
                "minimum_state_component": float(root["minimum_state_component"]),
                "survival_density_identity_error": float(root["differential_mass_balance_error"]),
                "differential_mass_balance_error": float(root["differential_mass_balance_error"]),
            }
            for root in scan["all_bracketed_roots"]
        ]
        physical_gates = law_gate_results(
            model_diagnostics, [*scan_law_rows, *root_law_rows, *tail_trace]
        )
        gates = {
            "alternating_topology": alternating,
            "endpoint_signs": bool(scan["endpoint_signs_passed"]),
            "peak_ratio": peak_ratio >= REPRESENTATIVE_GATES["minimum_peak_ratio"],
            "valley_ratio": valley_ratio <= REPRESENTATIVE_GATES["maximum_valley_ratio"],
            "curvature": minimum_curvature
            >= REPRESENTATIVE_GATES["minimum_absolute_scaled_curvature"],
            "root_residual": maximum_residual is not None
            and maximum_residual <= REPRESENTATIVE_GATES["maximum_scaled_root_residual"],
            "event_masses": bool(
                masses and min(masses) >= REPRESENTATIVE_GATES["minimum_each_event_basin_mass"]
            ),
            "positive_density_and_survival": physical_gates["positive_density_and_survival"]
            and scan["physical_law_gates"]["positive_density_and_survival"],
            "survival_monotone": all(
                right <= left + REPRESENTATIVE_GATES["maximum_survival_increase"]
                for left, right in zip(survival_values, survival_values[1:])
            )
            and all(
                right["survival"]
                <= left["survival"] + REPRESENTATIVE_GATES["maximum_survival_increase"]
                for left, right in zip(tail_trace, tail_trace[1:])
            ),
            "sampled_state_nonnegative": scan["physical_law_gates"]["state_nonnegative"],
            "sampled_survival_monotone": scan["physical_law_gates"]["sampled_survival_monotone"],
            "survival_density_identity": physical_gates["survival_density_identity"]
            and scan["physical_law_gates"]["survival_density_identity"],
            "generator_killing_identity": physical_gates["generator_killing_identity"],
            "differential_mass_balance": physical_gates["differential_mass_balance"]
            and scan["physical_law_gates"]["differential_mass_balance"]
            and scan["physical_law_gates"]["all_bracketed_roots_physical"],
            "event_partition_closure": closure_error
            <= REPRESENTATIVE_GATES["maximum_event_partition_closure_error"],
            "final_state_nonnegative": physical_gates["state_nonnegative"]
            and float(np.min(final_state))
            >= -REPRESENTATIVE_GATES["maximum_negative_state_tolerance"],
            "initial_mass": physical_gates["initial_mass"],
            "installed_budget": physical_gates["installed_budget"],
            "finite_factor_diagnostics": physical_gates["finite_factor_diagnostics"],
        }
        if set(gates) != set(CONTROL_GATE_NAMES):
            raise RuntimeError("control gate schema changed")
        row = {
            "status": "PASS_CONTROL_EVALUATION" if all(gates.values()) else HOLD_STATUS,
            "reason": "complete_finite_evaluation",
            "theta": value.tolist(),
            "weights": weights_from_theta(value).tolist(),
            "retained_maximum_count": maximum_count,
            "topology": topology,
            "stationary_scan": scan,
            "roots": roots,
            "all_bracketed_roots": scan["all_bracketed_roots"],
            "tail_trace": tail_trace,
            "model_diagnostics": model_diagnostics,
            "peak_minimum_to_maximum_ratio": peak_ratio,
            "valley_to_smaller_peak_ratios": valley_ratios,
            "event_basin_masses": masses,
            "event_partition_closure_error": closure_error,
            "final_survival": observed_final_survival,
            "minimum_final_state_component": float(np.min(final_state)),
            "score_term_margins": margins,
            "robustness_score": score,
            "gates": sorted_bool_mapping(gates),
            "all_gates_passed": bool(all(gates.values())),
        }
        require_finite_json(row)
        return row
    except (
        ArithmeticError,
        AttributeError,
        KeyError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        return control_evaluation_hold(
            value if "value" in locals() else theta, str(error), observed_final_survival
        )


def candidate_controls(theta_cusp_97: np.ndarray) -> list[dict[str, Any]]:
    candidates = []
    index = 0
    for radius in PHASE_SEARCH["radii"]:
        for direction in PHASE_SEARCH["directions"]:
            theta = theta_cusp_97 + float(radius) * np.asarray(direction)
            weights = weights_from_theta(theta)
            inside = point_in_trust_box(REFERENCE_CUSP_TIME, theta)[0]
            candidates.append(
                {
                    "candidate_index": index,
                    "radius": float(radius),
                    "direction": direction,
                    "theta": theta.tolist(),
                    "weights": weights.tolist(),
                    "eligible_geometry": bool(
                        inside and float(np.min(weights)) >= SOLVER["minimum_simplex_weight"]
                    ),
                }
            )
            index += 1
    if len(candidates) != PHASE_SEARCH["candidate_count"]:
        raise RuntimeError("candidate enumeration changed")
    return candidates


def phase_discovery(
    model_65: AllocationModel, model_97: AllocationModel, theta_cusp_97: np.ndarray
) -> dict[str, Any]:
    candidates = candidate_controls(theta_cusp_97)
    screened: list[dict[str, Any]] = []
    for candidate in candidates:
        row = dict(candidate)
        row["mesh_65"] = None
        row["mesh_65_evaluation_status"] = "NOT_ELIGIBLE_GEOMETRY"
        if candidate["eligible_geometry"]:
            try:
                row["mesh_65"] = evaluate_control_law(
                    model_65, np.asarray(candidate["theta"]), 0.05
                )
                require_finite_json(row["mesh_65"])
                row["mesh_65_evaluation_status"] = (
                    "HOLD_CONTROL_EVALUATION"
                    if row["mesh_65"].get("status") == "HOLD_CONTROL_EVALUATION"
                    else "EVALUATED"
                )
            except (ArithmeticError, KeyError, RuntimeError, TypeError, ValueError):
                row["mesh_65"] = None
                row["mesh_65_evaluation_status"] = "HOLD_CONTROL_EVALUATION"
        screened.append(row)
    missing_mesh_65 = [
        row["candidate_index"]
        for row in screened
        if row["eligible_geometry"] and row["mesh_65_evaluation_status"] != "EVALUATED"
    ]
    if missing_mesh_65:
        phase = {
            "phase_centre_theta": theta_cusp_97.tolist(),
            "candidate_generation": candidates,
            "screened_mesh_65": screened,
            "advanced_mesh_97": [],
            "representatives": {"1": None, "2": None, "3": None},
            "all_three_regions_found": False,
            "phase_complete": False,
            "hold_reasons": [f"missing_eligible_mesh_65_evaluations:{missing_mesh_65}"],
            "search_expanded": False,
        }
        require_finite_json(phase)
        return phase
    advanced: list[dict[str, Any]] = []
    representatives: dict[str, Any] = {}
    hold_reasons: list[str] = []
    for target in PHASE_SEARCH["target_retained_maximum_counts"]:
        eligible = [
            row
            for row in screened
            if row["mesh_65"] is not None
            and row["mesh_65"]["retained_maximum_count"] == target
            and row["mesh_65"]["gates"]["alternating_topology"]
            and row["mesh_65"]["gates"]["endpoint_signs"]
            and row["mesh_65"]["gates"].get("root_residual", True)
            and row["mesh_65"].get("robustness_score") is not None
        ]
        eligible.sort(
            key=lambda row: (
                -row["mesh_65"]["robustness_score"],
                tuple(row["weights"]),
            )
        )
        selected = eligible[: int(PHASE_SEARCH["maximum_advanced_per_mode_count"])]
        target_rows = []
        for row in selected:
            promoted = dict(row)
            try:
                promoted["mesh_97"] = evaluate_control_law(model_97, np.asarray(row["theta"]), 0.05)
                require_finite_json(promoted["mesh_97"])
                promoted["mesh_97_evaluation_status"] = (
                    "HOLD_CONTROL_EVALUATION"
                    if promoted["mesh_97"].get("status") == "HOLD_CONTROL_EVALUATION"
                    else "EVALUATED"
                )
            except (ArithmeticError, KeyError, RuntimeError, TypeError, ValueError):
                promoted["mesh_97"] = None
                promoted["mesh_97_evaluation_status"] = "HOLD_CONTROL_EVALUATION"
            if promoted["mesh_97_evaluation_status"] != "EVALUATED":
                promoted["worst_score"] = None
                promoted["both_meshes_pass"] = False
                target_rows.append(promoted)
                advanced.append(promoted)
                hold_reasons.append(f"missing_selected_mesh_97_evaluation:{row['candidate_index']}")
                continue
            promoted["worst_score"] = min(
                promoted["mesh_65"]["robustness_score"],
                promoted["mesh_97"]["robustness_score"],
            )
            promoted["both_meshes_pass"] = bool(
                promoted["mesh_65"]["all_gates_passed"]
                and promoted["mesh_97"]["all_gates_passed"]
                and promoted["mesh_97"]["retained_maximum_count"] == target
            )
            target_rows.append(promoted)
            advanced.append(promoted)
        passing = [row for row in target_rows if row.get("both_meshes_pass") is True]
        passing.sort(key=lambda row: (-row["worst_score"], tuple(row["weights"])))
        representatives[str(target)] = passing[0] if passing else None
    phase_complete = not hold_reasons
    if not phase_complete:
        representatives = {"1": None, "2": None, "3": None}
    passed = bool(
        phase_complete and all(representatives[str(target)] is not None for target in (1, 2, 3))
    )
    phase = {
        "phase_centre_theta": theta_cusp_97.tolist(),
        "candidate_generation": candidates,
        "screened_mesh_65": screened,
        "advanced_mesh_97": advanced,
        "representatives": representatives,
        "all_three_regions_found": passed,
        "phase_complete": phase_complete,
        "hold_reasons": hold_reasons,
        "search_expanded": False,
    }
    require_finite_json(phase)
    return phase


def not_run_mesh_row(cells: int, reason: str, status: str = "NOT_RUN_AFTER_HOLD") -> dict[str, Any]:
    return {
        "mesh": [cells, cells, cells],
        "status": status,
        "reason": reason,
        "model_diagnostics": None,
        "homotopy": None,
        "cusp": None,
        "cusp_diagnostics": None,
        "stationary_scan": None,
        "remote_pair": None,
        "branches": None,
        "all_mesh_discovery_gates_passed": False,
    }


def solve_discovery_mesh(model: AllocationModel) -> tuple[dict[str, Any], Snapshot | None]:
    homotopy = run_homotopy(model)
    snapshot = homotopy["snapshot"]
    serialized_homotopy = {"status": homotopy["status"], "rows": homotopy["rows"]}
    if snapshot is None:
        return (
            {
                "mesh": [model.cells] * 3,
                "status": HOLD_STATUS,
                "reason": "homotopy_failed",
                "model_diagnostics": None,
                "homotopy": serialized_homotopy,
                "cusp": None,
                "cusp_diagnostics": None,
                "stationary_scan": None,
                "remote_pair": None,
                "branches": None,
                "all_mesh_discovery_gates_passed": False,
            },
            None,
        )
    try:
        derivative = finite_difference_audit(model, snapshot)
        diagnostics = cusp_diagnostics(model, snapshot, derivative)
        model_diagnostics = allocation_model_diagnostics(model, snapshot.budget, snapshot.theta)
        scan = stationary_scan(model, 0.01, snapshot.theta, 0.05)
        scan["physical_law_gates"] = scan_physical_gate_results(scan, model_diagnostics)
        remote = assess_remote_pair(scan, snapshot.time)
        branches = {
            "negative": continue_branch(model, snapshot, -0.10, scan, remote),
            "positive": continue_branch(model, snapshot, 0.10, scan, remote),
        }
    except (ArithmeticError, RuntimeError, ValueError, np.linalg.LinAlgError):
        return (
            {
                "mesh": [model.cells] * 3,
                "status": HOLD_STATUS,
                "reason": "post_homotopy_numerical_evaluation_failed",
                "model_diagnostics": None,
                "homotopy": serialized_homotopy,
                "cusp": serialize_snapshot(snapshot),
                "cusp_diagnostics": None,
                "stationary_scan": None,
                "remote_pair": None,
                "branches": None,
                "all_mesh_discovery_gates_passed": False,
            },
            None,
        )
    passed = bool(
        diagnostics["all_gates_passed"]
        and all(scan["physical_law_gates"].values())
        and remote["remote_pair_present"]
        and all(branch["status"] == "PASS_BRANCH_DISCOVERY" for branch in branches.values())
    )
    return (
        {
            "mesh": [model.cells] * 3,
            "status": "PASS_MESH_DISCOVERY" if passed else HOLD_STATUS,
            "reason": "all_mesh_gates_passed" if passed else "mesh_gate_failed",
            "model_diagnostics": model_diagnostics,
            "homotopy": serialized_homotopy,
            "cusp": serialize_snapshot(snapshot, model),
            "cusp_diagnostics": diagnostics,
            "stationary_scan": scan,
            "remote_pair": remote,
            "branches": branches,
            "all_mesh_discovery_gates_passed": passed,
        },
        snapshot,
    )


def run_formal(
    manifest: dict[str, Any],
    manifest_sha256: str,
    *,
    allowed_present_science_paths: Sequence[Path] = (),
) -> dict[str, Any]:
    if sha256(MANIFEST) != manifest_sha256:
        raise ValueError("external manifest SHA-256 does not match")
    pinned_before = validate_manifest(
        manifest, allowed_present_science_paths=allowed_present_science_paths
    )
    require_loaded_native_phase(manifest, "post_manifest_validation")
    lexical_before, lexical_bytes_before = capture_complete_freeze_snapshot(MANIFEST, manifest)
    preflight = explicit_csr_preflight(
        build_model(int(PREFLIGHT["small_explicit_csr_cells"]), manifest, formal=False)
    )
    require_loaded_native_phase(manifest, "full_stack_post_import")
    models: dict[int, AllocationModel] = {}
    rows: list[dict[str, Any]] = []
    snapshots: dict[int, Snapshot] = {}
    phase = None
    stopped = not bool(preflight["passed"])
    if stopped:
        rows = [
            not_run_mesh_row(
                cells,
                "explicit_csr_preflight_held_before_scientific_construction",
                "NOT_RUN_AFTER_PREFLIGHT_HOLD",
            )
            for cells in DISCOVERY_MESHES
        ]
    else:
        for cells in DISCOVERY_MESHES:
            if stopped:
                rows.append(not_run_mesh_row(cells, "earlier_discovery_mesh_held"))
                continue
            model = build_model(cells, manifest, formal=True)
            models[cells] = model
            row, snapshot = solve_discovery_mesh(model)
            rows.append(row)
            if snapshot is None or not row["all_mesh_discovery_gates_passed"]:
                stopped = True
            else:
                snapshots[cells] = snapshot
        if not stopped and set(snapshots) == set(DISCOVERY_MESHES):
            phase = phase_discovery(models[65], models[97], snapshots[97].theta)
    passed = bool(
        preflight["passed"]
        and not stopped
        and phase is not None
        and phase["phase_complete"]
        and phase["all_three_regions_found"]
        and all(row["all_mesh_discovery_gates_passed"] for row in rows)
    )
    claim_flags = sorted_bool_mapping(CLAIM_FLAGS)
    claim_flags["low_mesh_discovery_completed"] = passed
    pinned_after = validate_manifest(
        manifest, allowed_present_science_paths=allowed_present_science_paths
    )
    lexical_after, lexical_bytes_after = capture_complete_freeze_snapshot(MANIFEST, manifest)
    if pinned_after != pinned_before:
        raise RuntimeError("complete pinned-file snapshot changed during formal calculation")
    require_same_freeze_snapshot(
        lexical_before, lexical_bytes_before, lexical_after, lexical_bytes_after
    )
    result = {
        "schema_version": SCHEMA_VERSION,
        "stage": STAGE,
        "status": PASS_STATUS if passed else HOLD_STATUS,
        "evidence_timing": EVIDENCE_TIMING,
        "claim_scope": manifest["claim_scope"],
        "manifest_sha256": manifest_sha256,
        "small_explicit_csr_preflight": preflight,
        "discovery_mesh_rows": rows,
        "bounded_phase_discovery": phase,
        "all_discovery_gates_passed": passed,
        "required_claim_flags": claim_flags,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "pin_snapshots": {
            "before_formal": pinned_before,
            "after_formal": pinned_after,
        },
        "lexical_pin_snapshots": {
            "before_formal": lexical_before,
            "after_formal": lexical_after,
        },
        "pinned_file_hashes": pinned_after,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "limitations": LIMITATIONS,
    }
    require_finite_json(result)
    require_loaded_native_phase(manifest, "full_stack_post_import")
    return result


def run_algebra_dry_run(manifest: dict[str, Any], cells: int) -> dict[str, Any]:
    validate_cells(cells, formal=False)
    model = build_model(cells, manifest, formal=False)
    preflight = explicit_csr_preflight(model)
    if sys.flags.isolated == 1:
        require_loaded_native_phase(manifest, "full_stack_post_import")
    return {
        "schema_version": SCHEMA_VERSION,
        "stage": STAGE,
        "status": "PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE" if preflight["passed"] else "HOLD_ALGEBRA",
        "evidence_timing": "SMALL_EXPLICIT_CSR_DRY_RUN_ONLY",
        "mesh": [cells] * 3,
        "scientific_meshes_executed": [],
        "explicit_csr_preflight": preflight,
        "required_claim_flags": CLAIM_FLAGS,
        "all_discovery_gates_passed": False,
    }


def _close(left: float, right: float, tolerance: float = 5.0e-13) -> bool:
    return abs(float(left) - float(right)) <= tolerance * max(1.0, abs(left), abs(right))


def _exact_keys(value: Any, keys: set[str]) -> bool:
    return type(value) is dict and set(value) == keys


def _nonnegative_float(value: Any) -> bool:
    return type(value) is float and math.isfinite(value) and value >= 0.0


def _bernoulli_scalar(value: float) -> float:
    if abs(value) < 1.0e-5:
        return 1.0 - value / 2.0 + value**2 / 12.0 - value**4 / 720.0 + value**6 / 30240.0
    return value / math.expm1(value)


def _sg_generator_trace(
    cells: int,
    bounds: Sequence[float],
    diffusion: float,
    drift: Callable[[float], float],
) -> float:
    spacing = (float(bounds[1]) - float(bounds[0])) / cells
    rate_scale = diffusion / spacing**2
    total = 0.0
    for index in range(1, cells):
        face = float(bounds[0]) + index * spacing
        peclet = drift(face) * spacing / diffusion
        total -= rate_scale * (_bernoulli_scalar(-peclet) + _bernoulli_scalar(peclet))
    return float(total)


def expected_generator_diagonal_sums(cells: int) -> tuple[float, float]:
    diffusion = PHYSICAL_PARAMETERS["particle_diffusion"]
    stiffness = PHYSICAL_PARAMETERS["ou_stiffness"]
    mean = PHYSICAL_PARAMETERS["ou_mean"]
    midpoint = _sg_generator_trace(
        cells,
        FINITE_VOLUME["midpoint_bounds"],
        diffusion / 2.0,
        lambda value: -stiffness * (value - mean),
    )
    parallel = _sg_generator_trace(
        cells,
        FINITE_VOLUME["relative_parallel_bounds"],
        2.0 * diffusion,
        lambda value: -stiffness * value,
    )
    perpendicular_spacing = PHYSICAL_PARAMETERS["transverse_width"] / cells
    perpendicular_rate = 2.0 * diffusion / perpendicular_spacing**2
    perpendicular = -2.0 * cells * perpendicular_rate
    relative = cells * parallel + cells * perpendicular
    return midpoint, float(relative)


MODEL_DIAGNOSTIC_KEYS = {
    "mesh",
    "state_count",
    "matrix_free_full_generator",
    "initial_mass",
    "initial_mass_error",
    "installed_budget",
    "physical_installed_budget",
    "physical_installed_budget_absolute_error",
    "minimum_weight",
    "weight_sum_error",
    "minimum_killing_per_budget",
    "maximum_killing_per_budget",
    "midpoint_killing_profile_minimum",
    "midpoint_killing_profile_maximum",
    "midpoint_killing_profile_sum",
    "contact_killing_profile_minimum",
    "contact_killing_profile_maximum",
    "contact_killing_profile_sum",
    "midpoint_generator_diagonal_sum",
    "relative_generator_diagonal_sum",
    "generator_killing_identity_error",
    "analytic_column_operator_trace",
    "factor_diagnostics",
}
FACTOR_DIAGNOSTIC_KEYS = {
    "cells_per_coordinate",
    "state_count_if_full_matrix_formed",
    "spacings",
    "patch_integrals",
    "maximum_patch_quadrature_error_estimate",
    "midpoint_initial_mass",
    "relative_initial_mass",
    "maximum_initial_quadrature_error_estimate",
    "contact_area",
    "contact_area_exact",
    "contact_area_error_estimate",
    "midpoint_generator_row_error",
    "relative_generator_row_error",
}
STATE_LAW_KEYS = {
    "density",
    "density_per_budget",
    "survival",
    "minimum_state_component",
    "survival_derivative",
    "survival_density_identity_error",
    "differential_mass_balance_error",
}
SAVED_TRACE_KEYS = {
    "time",
    "density",
    "density_per_budget",
    "first_derivative_per_budget",
    "second_derivative_per_budget",
    "survival",
    "minimum_state_component",
    "differential_mass_balance_error",
}
ROOT_KEYS = {
    "bracket_index",
    "bracket",
    "time",
    "density_per_budget",
    "scaled_root_residual",
    "scaled_curvature",
    "type",
    "survival",
    "minimum_state_component",
    "differential_mass_balance_error",
    "density_eligible",
    "residual_eligible",
    "curvature_eligible",
    "duplicate_refined_root",
    "eligible",
    "separation_eligible",
    "eligibility_reasons",
}
SCAN_KEYS = {
    "spacing",
    "time_window",
    "grid_point_count",
    "reference_maximum_density_per_budget",
    "endpoint_first_derivatives_per_budget",
    "endpoint_signs_passed",
    "minimum_sampled_state",
    "minimum_sampled_density",
    "minimum_sampled_survival",
    "maximum_sampled_survival_increase",
    "maximum_sampled_differential_mass_balance_error",
    "full_scan_trace",
    "saved_trace",
    "roots",
    "all_bracketed_roots",
    "topology",
    "physical_law_gates",
}
CONTROL_KEYS = {
    "status",
    "reason",
    "theta",
    "weights",
    "retained_maximum_count",
    "topology",
    "stationary_scan",
    "roots",
    "all_bracketed_roots",
    "tail_trace",
    "model_diagnostics",
    "peak_minimum_to_maximum_ratio",
    "valley_to_smaller_peak_ratios",
    "event_basin_masses",
    "event_partition_closure_error",
    "final_survival",
    "minimum_final_state_component",
    "score_term_margins",
    "robustness_score",
    "gates",
    "all_gates_passed",
}
LINEAGE_KEYS = {
    "global_root_ordinal",
    "type",
    "side",
    "time",
    "origin_bracket_index",
    "previous_bracket_index",
    "current_bracket_index",
    "predecessor_global_root_ordinal",
    "successor_global_root_ordinal",
    "matched_previous_global_root_ordinal",
    "adjacent_time_drift",
}
REMOTE_KEYS = {
    "remote_pair_present",
    "pair_identity",
    "anchor_pair_identity",
    "pair",
    "root_lineage",
    "lineage_status",
    "lineage_passed",
    "lineage_hold_reasons",
    "maximum_observed_adjacent_drift",
    "candidate_search_bounded_to_frozen_window",
}
REMOTE_PAIR_KEYS = {
    "maximum",
    "minimum",
    "side",
    "pair_type",
    "selected_global_root_indices",
    "origin_bracket_lineage",
    "maximum_global_root_ordinal",
    "minimum_global_root_ordinal",
    "maximum_bracket_index",
    "minimum_bracket_index",
    "eligible_root_count_at_anchor",
}
LAW_GATE_NAMES = {
    "positive_density_and_survival",
    "state_nonnegative",
    "survival_density_identity",
    "generator_killing_identity",
    "differential_mass_balance",
    "initial_mass",
    "installed_budget",
    "finite_factor_diagnostics",
}
HOMOTOPY_ROW_KEYS = {
    "budget",
    "status",
    "converged",
    "iterations",
    "reason",
    "point",
    "maximum_scaled_residual",
}
SNAPSHOT_KEYS = {
    "time",
    "budget",
    "theta",
    "weights",
    "density_per_budget",
    "per_budget_time_jets_0_to_4",
    "allocation_time_jets",
}
DERIVATIVE_ROW_KEYS = {
    "allocation_step",
    "relative_time_step",
    "maximum_state_tangent_relative_l1_error",
    "maximum_dimensionless_jacobian_error",
}
DERIVATIVE_AUDIT_KEYS = {
    "rows",
    "state_error_decrease_or_floor",
    "jacobian_error_decrease_or_floor",
    "passed",
}
CUSP_DIAGNOSTIC_BASE_KEYS = {
    "maximum_dimensionless_residual",
    "minimum_weight",
    "scaled_fourth_derivative",
    "projected_singular_values",
    "projected_singular_value_ratio",
    "full_smallest_singular_value",
    "determinant_factorization_relative_residual",
    "maximum_survival_identity_residual",
    "model_diagnostics",
    "state_law_diagnostics",
    "dimensionless_jacobian",
    "derivative_audit",
}
CUSP_GATE_NAMES = {
    "cusp_residual",
    "simplex_margin",
    "quartic_nondegeneracy",
    "projected_rank_floor",
    "projected_rank_ratio",
    "full_jacobian_rank",
    "determinant_factorization",
    "mixed_jet_audit",
    "survival_identities",
    *LAW_GATE_NAMES,
}
FOLD_NODE_KEYS = {
    "acceptance_index",
    "time",
    "theta",
    "weights",
    "normalized_fold_residual",
    "scaled_third_derivative",
    "dimensionless_fold_singular_values",
    "model_diagnostics",
    "state_law_diagnostics",
    "physical_law_gates",
}
COMPARISON_NODE_KEYS = {
    *FOLD_NODE_KEYS,
    "signed_time_offset",
    "target_signed_time_offset",
    "absolute_time_offset_mismatch",
}
BRANCH_KEYS = {
    "status",
    "orientation",
    "nodes",
    "comparison_nodes",
    "comparison_node_remote_pairs",
    "gates",
}


def validate_model_diagnostic_contract(
    value: Any,
    cells: int,
    *,
    budget: float | None = None,
    weights: list[float] | None = None,
) -> bool:
    if not _exact_keys(value, MODEL_DIAGNOSTIC_KEYS):
        return False
    factors = value["factor_diagnostics"]
    try:
        primitive_nonnegative = {
            "initial_mass_error",
            "installed_budget",
            "physical_installed_budget",
            "physical_installed_budget_absolute_error",
            "weight_sum_error",
            "minimum_killing_per_budget",
            "maximum_killing_per_budget",
            "midpoint_killing_profile_minimum",
            "midpoint_killing_profile_maximum",
            "midpoint_killing_profile_sum",
            "contact_killing_profile_minimum",
            "contact_killing_profile_maximum",
            "contact_killing_profile_sum",
            "generator_killing_identity_error",
        }
        cells_value = value["mesh"][0] if type(value.get("mesh")) is list else 0
        midpoint_spacing = (
            (FINITE_VOLUME["midpoint_bounds"][1] - FINITE_VOLUME["midpoint_bounds"][0])
            / cells_value
            if type(cells_value) is int and cells_value > 0
            else math.nan
        )
        parallel_spacing = (
            (
                FINITE_VOLUME["relative_parallel_bounds"][1]
                - FINITE_VOLUME["relative_parallel_bounds"][0]
            )
            / cells_value
            if type(cells_value) is int and cells_value > 0
            else math.nan
        )
        perp_spacing = (
            PHYSICAL_PARAMETERS["transverse_width"] / cells_value
            if type(cells_value) is int and cells_value > 0
            else math.nan
        )
        midpoint_minimum = value["midpoint_killing_profile_minimum"]
        midpoint_maximum = value["midpoint_killing_profile_maximum"]
        midpoint_sum = value["midpoint_killing_profile_sum"]
        contact_minimum = value["contact_killing_profile_minimum"]
        contact_maximum = value["contact_killing_profile_maximum"]
        contact_sum = value["contact_killing_profile_sum"]
        width = PHYSICAL_PARAMETERS["transverse_width"]
        reconstructed_minimum_killing = midpoint_minimum * contact_minimum / width
        reconstructed_maximum_killing = midpoint_maximum * contact_maximum / width
        reconstructed_killing_sum = midpoint_sum * contact_sum / width
        reconstructed_trace = (
            cells_value**2 * value["midpoint_generator_diagonal_sum"]
            + cells_value * value["relative_generator_diagonal_sum"]
            - value["installed_budget"] * reconstructed_killing_sum
        )
        row_error_bound = (
            factors["midpoint_generator_row_error"]
            + factors["relative_generator_row_error"]
            + FACTOR_GATES["maximum_error_estimate_undercoverage"]
        )
        expected_midpoint_diagonal, expected_relative_diagonal = expected_generator_diagonal_sums(
            cells_value
        )
        return bool(
            type(value["mesh"]) is list
            and len(value["mesh"]) == 3
            and all(type(item) is int and item == cells for item in value["mesh"])
            and type(value["state_count"]) is int
            and value["state_count"] == cells**3
            and value["matrix_free_full_generator"] is True
            and all(
                type(value[key]) is float
                for key in MODEL_DIAGNOSTIC_KEYS
                - {"mesh", "state_count", "matrix_free_full_generator", "factor_diagnostics"}
            )
            and _exact_keys(factors, FACTOR_DIAGNOSTIC_KEYS)
            and type(factors["cells_per_coordinate"]) is int
            and factors["cells_per_coordinate"] == cells
            and type(factors["state_count_if_full_matrix_formed"]) is int
            and factors["state_count_if_full_matrix_formed"] == cells**3
            and _exact_keys(factors["spacings"], {"midpoint", "relative_parallel", "relative_perp"})
            and all(type(item) is float for item in factors["spacings"].values())
            and type(factors["patch_integrals"]) is list
            and len(factors["patch_integrals"]) == 4
            and all(type(item) is float for item in factors["patch_integrals"])
            and all(
                type(factors[key]) is float
                for key in FACTOR_DIAGNOSTIC_KEYS
                - {
                    "cells_per_coordinate",
                    "state_count_if_full_matrix_formed",
                    "spacings",
                    "patch_integrals",
                }
            )
            and factor_diagnostics_pass(value)
            and all(_nonnegative_float(value[key]) for key in primitive_nonnegative)
            and type(value["initial_mass"]) is float
            and value["initial_mass"] > 0.0
            and type(value["minimum_weight"]) is float
            and type(value["midpoint_generator_diagonal_sum"]) is float
            and value["midpoint_generator_diagonal_sum"] <= 0.0
            and _close(value["midpoint_generator_diagonal_sum"], expected_midpoint_diagonal)
            and type(value["relative_generator_diagonal_sum"]) is float
            and value["relative_generator_diagonal_sum"] <= 0.0
            and _close(value["relative_generator_diagonal_sum"], expected_relative_diagonal)
            and midpoint_minimum <= midpoint_maximum <= 1.0 / midpoint_spacing + 5.0e-13
            and contact_minimum <= contact_maximum <= 1.0 + 5.0e-13
            and _close(midpoint_sum * midpoint_spacing, 1.0)
            and _close(
                contact_sum * parallel_spacing * perp_spacing,
                factors["contact_area"],
            )
            and _close(value["minimum_killing_per_budget"], reconstructed_minimum_killing)
            and _close(value["maximum_killing_per_budget"], reconstructed_maximum_killing)
            and value["minimum_killing_per_budget"] <= value["maximum_killing_per_budget"]
            and _close(value["analytic_column_operator_trace"], reconstructed_trace)
            and value["analytic_column_operator_trace"] <= 0.0
            and value["generator_killing_identity_error"] <= row_error_bound
            and _close(
                value["physical_installed_budget"],
                value["installed_budget"] * midpoint_sum * midpoint_spacing,
            )
            and _close(value["initial_mass_error"], abs(value["initial_mass"] - 1.0))
            and _close(
                value["physical_installed_budget_absolute_error"],
                abs(value["physical_installed_budget"] - value["installed_budget"]),
            )
            and (budget is None or _close(value["installed_budget"], budget))
            and (
                weights is None
                or (
                    _float_vector(weights, 4)
                    and _close(value["minimum_weight"], min(weights))
                    and _close(value["weight_sum_error"], abs(sum(weights) - 1.0))
                )
            )
        )
    except (KeyError, TypeError, ValueError):
        return False


def validate_state_law_contract(value: Any, *, budget: float | None = None) -> bool:
    return bool(
        _exact_keys(value, STATE_LAW_KEYS)
        and all(type(value[key]) is float for key in STATE_LAW_KEYS)
        and _nonnegative_float(value["survival_density_identity_error"])
        and _nonnegative_float(value["differential_mass_balance_error"])
        and _close(
            value["survival_density_identity_error"], value["differential_mass_balance_error"]
        )
        and _close(value["survival_derivative"] + value["density"], 0.0)
        and (budget is None or _close(value["density"], budget * value["density_per_budget"]))
    )


def validate_root_contract(root: Any, bracket_index: int) -> bool:
    if not _exact_keys(root, ROOT_KEYS):
        return False
    try:
        numeric = {
            "time",
            "density_per_budget",
            "survival",
            "minimum_state_component",
            "differential_mass_balance_error",
        }
        nullable = {"scaled_root_residual", "scaled_curvature"}
        booleans = {
            "density_eligible",
            "residual_eligible",
            "curvature_eligible",
            "duplicate_refined_root",
            "eligible",
            "separation_eligible",
        }
        return bool(
            type(root["bracket_index"]) is int
            and root["bracket_index"] == bracket_index
            and type(root["bracket"]) is list
            and len(root["bracket"]) == 2
            and all(type(item) is float for item in root["bracket"])
            and root["bracket"][0] <= root["time"] <= root["bracket"][1]
            and all(type(root[key]) is float for key in numeric)
            and all(root[key] is None or type(root[key]) is float for key in nullable)
            and _nonnegative_float(root["differential_mass_balance_error"])
            and (
                root["scaled_root_residual"] is None
                or _nonnegative_float(root["scaled_root_residual"])
            )
            and root["type"] in {"maximum", "minimum"}
            and all(type(root[key]) is bool for key in booleans)
            and type(root["eligibility_reasons"]) is list
            and all(type(item) is str for item in root["eligibility_reasons"])
            and root["eligible"]
            == bool(
                root["density_eligible"]
                and root["residual_eligible"]
                and root["curvature_eligible"]
                and not root["duplicate_refined_root"]
                and root["separation_eligible"]
            )
        )
    except (KeyError, TypeError):
        return False


def reconstruct_root_semantics(roots: list[dict[str, Any]], reference_density: float) -> bool:
    """Recompute every root flag, type, reason, duplicate, and separation decision."""

    try:
        distinct_indices = [
            index
            for index, root in enumerate(roots)
            if not (index > 0 and root["time"] - roots[index - 1]["time"] < 1.0e-8)
        ]
        distinct_position = {
            root_index: position for position, root_index in enumerate(distinct_indices)
        }
        for index, root in enumerate(roots):
            positive_density = bool(root["density_per_budget"] > 0.0 and reference_density > 0.0)
            density_eligible = bool(
                positive_density
                and root["density_per_budget"]
                >= ROOT_SEARCH["relative_density_floor"] * reference_density
            )
            residual_eligible = bool(
                root["scaled_root_residual"] is not None
                and root["scaled_root_residual"] >= 0.0
                and root["scaled_root_residual"] <= ROOT_SEARCH["maximum_scaled_root_residual"]
            )
            curvature_eligible = bool(
                root["scaled_curvature"] is not None
                and abs(root["scaled_curvature"])
                >= ROOT_SEARCH["minimum_absolute_scaled_curvature"]
            )
            duplicate = bool(index > 0 and root["time"] - roots[index - 1]["time"] < 1.0e-8)
            if duplicate:
                separation_eligible = True
            else:
                position = distinct_position[index]
                left_gap = (
                    root["time"] - roots[distinct_indices[position - 1]]["time"]
                    if position > 0
                    else math.inf
                )
                right_gap = (
                    roots[distinct_indices[position + 1]]["time"] - root["time"]
                    if position + 1 < len(distinct_indices)
                    else math.inf
                )
                separation_eligible = bool(
                    min(left_gap, right_gap) >= ROOT_SEARCH["minimum_root_separation"]
                )
            reasons: list[str] = []
            if not density_eligible:
                reasons.append("density_floor_or_positivity")
            if not residual_eligible:
                reasons.append("scaled_root_residual")
            if not curvature_eligible:
                reasons.append("scaled_curvature")
            if duplicate:
                reasons.append("duplicate_refined_root")
            if not separation_eligible:
                reasons.append("minimum_root_separation")
            expected_type = (
                "maximum"
                if root["scaled_curvature"] is not None and root["scaled_curvature"] < 0.0
                else "minimum"
            )
            eligible = bool(
                density_eligible
                and residual_eligible
                and curvature_eligible
                and not duplicate
                and separation_eligible
            )
            if (
                root["type"] != expected_type
                or root["density_eligible"] is not density_eligible
                or root["residual_eligible"] is not residual_eligible
                or root["curvature_eligible"] is not curvature_eligible
                or root["duplicate_refined_root"] is not duplicate
                or root["separation_eligible"] is not separation_eligible
                or root["eligibility_reasons"] != reasons
                or root["eligible"] is not eligible
            ):
                return False
        return True
    except (IndexError, KeyError, TypeError, ValueError):
        return False


def reconstruct_full_scan_primitives(scan: Any) -> bool:
    """Rebuild every saved row, aggregate, and sign-change bracket from 691 rows."""

    try:
        if type(scan) is not dict:
            return False
        spacing = scan["spacing"]
        start, stop = scan["time_window"]
        full = scan["full_scan_trace"]
        saved = scan["saved_trace"]
        roots = scan["all_bracketed_roots"]
        if (
            type(spacing) is not float
            or type(start) is not float
            or type(stop) is not float
            or type(full) is not list
            or type(saved) is not list
            or type(roots) is not list
        ):
            return False
        expected_count = int(round((stop - start) / spacing)) + 1
        if scan["grid_point_count"] != expected_count or len(full) != expected_count:
            return False
        for index, row in enumerate(full):
            if (
                not _exact_keys(row, SAVED_TRACE_KEYS)
                or not all(type(row[key]) is float for key in SAVED_TRACE_KEYS)
                or not _close(row["time"], start + index * spacing)
                or not _close(
                    row["density"],
                    BUDGET_HOMOTOPY["target_budget"] * row["density_per_budget"],
                )
                or not _nonnegative_float(row["differential_mass_balance_error"])
            ):
                return False
        stride = int(round(ROOT_SEARCH["saved_trace_spacing"] / spacing))
        if stride < 1 or not _close(stride * spacing, ROOT_SEARCH["saved_trace_spacing"]):
            return False
        expected_saved = [
            row for index, row in enumerate(full) if index % stride == 0 or index == len(full) - 1
        ]
        if saved != expected_saved:
            return False
        density_per_budget = [row["density_per_budget"] for row in full]
        survival = [row["survival"] for row in full]
        if (
            not _close(scan["reference_maximum_density_per_budget"], max(density_per_budget))
            or not all(
                _close(left, right)
                for left, right in zip(
                    scan["endpoint_first_derivatives_per_budget"],
                    [
                        full[0]["first_derivative_per_budget"],
                        full[-1]["first_derivative_per_budget"],
                    ],
                    strict=True,
                )
            )
            or not _close(
                scan["minimum_sampled_state"], min(row["minimum_state_component"] for row in full)
            )
            or not _close(scan["minimum_sampled_density"], min(row["density"] for row in full))
            or not _close(scan["minimum_sampled_survival"], min(survival))
            or not _close(
                scan["maximum_sampled_survival_increase"],
                max(
                    0.0,
                    max((right - left for left, right in zip(survival, survival[1:])), default=0.0),
                ),
            )
            or not _close(
                scan["maximum_sampled_differential_mass_balance_error"],
                max(row["differential_mass_balance_error"] for row in full),
            )
        ):
            return False
        brackets: list[list[float]] = []
        for left_row, right_row in zip(full, full[1:]):
            left = left_row["first_derivative_per_budget"]
            right = right_row["first_derivative_per_budget"]
            if left == 0.0:
                brackets.append([left_row["time"], left_row["time"]])
            elif left * right < 0.0:
                brackets.append([left_row["time"], right_row["time"]])
        if len(roots) != len(brackets):
            return False
        return all(
            root["bracket_index"] == index
            and len(root["bracket"]) == 2
            and all(
                _close(observed, expected)
                for observed, expected in zip(root["bracket"], bracket, strict=True)
            )
            for index, (root, bracket) in enumerate(zip(roots, brackets, strict=True))
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def validate_scan_contract(scan: Any, model_diagnostics: dict[str, Any]) -> bool:
    if not _exact_keys(scan, SCAN_KEYS):
        return False
    try:
        all_roots = scan["all_bracketed_roots"]
        roots = scan["roots"]
        full = scan["full_scan_trace"]
        saved = scan["saved_trace"]
        if (
            not reconstruct_full_scan_primitives(scan)
            or type(model_diagnostics.get("mesh")) is not list
            or len(model_diagnostics["mesh"]) != 3
            or not all(type(item) is int for item in model_diagnostics["mesh"])
            or len(set(model_diagnostics["mesh"])) != 1
            or type(scan["spacing"]) is not float
            or scan["spacing"] != ROOT_SEARCH[f"mesh_{model_diagnostics['mesh'][0]}_spacing"]
            or scan["time_window"] != ROOT_SEARCH["time_window"]
            or type(scan["grid_point_count"]) is not int
            or scan["grid_point_count"]
            != int(round((scan["time_window"][1] - scan["time_window"][0]) / scan["spacing"])) + 1
            or type(scan["reference_maximum_density_per_budget"]) is not float
            or scan["reference_maximum_density_per_budget"] <= 0.0
            or type(scan["endpoint_first_derivatives_per_budget"]) is not list
            or len(scan["endpoint_first_derivatives_per_budget"]) != 2
            or not all(
                type(item) is float for item in scan["endpoint_first_derivatives_per_budget"]
            )
            or type(scan["endpoint_signs_passed"]) is not bool
            or scan["endpoint_signs_passed"]
            is not bool(
                scan["endpoint_first_derivatives_per_budget"][0] > 0.0
                and scan["endpoint_first_derivatives_per_budget"][1] < 0.0
            )
            or not all(
                type(scan[key]) is float
                for key in {
                    "minimum_sampled_state",
                    "minimum_sampled_density",
                    "minimum_sampled_survival",
                    "maximum_sampled_survival_increase",
                    "maximum_sampled_differential_mass_balance_error",
                }
            )
            or scan["maximum_sampled_survival_increase"] < 0.0
            or scan["maximum_sampled_differential_mass_balance_error"] < 0.0
            or type(saved) is not list
            or not saved
            or any(
                not _exact_keys(row, SAVED_TRACE_KEYS)
                or not all(type(row[key]) is float for key in SAVED_TRACE_KEYS)
                or not _close(
                    row["density"],
                    BUDGET_HOMOTOPY["target_budget"] * row["density_per_budget"],
                )
                for row in saved
            )
            or saved[0]["time"] != scan["time_window"][0]
            or saved[-1]["time"] != scan["time_window"][1]
            or any(right["time"] <= left["time"] for left, right in zip(saved, saved[1:]))
            or any(
                abs(
                    (row["time"] - scan["time_window"][0]) / ROOT_SEARCH["saved_trace_spacing"]
                    - round(
                        (row["time"] - scan["time_window"][0]) / ROOT_SEARCH["saved_trace_spacing"]
                    )
                )
                > 5.0e-13
                for row in saved
            )
            or type(all_roots) is not list
            or any(not validate_root_contract(root, index) for index, root in enumerate(all_roots))
            or any(
                float(right["time"]) < float(left["time"])
                for left, right in zip(all_roots, all_roots[1:])
            )
            or roots != [root for root in all_roots if root["eligible"]]
            or not reconstruct_root_semantics(
                all_roots, scan["reference_maximum_density_per_budget"]
            )
            or any(
                (
                    root["bracket"][0] < scan["time_window"][0]
                    or root["bracket"][1] > scan["time_window"][1]
                    or (
                        root["bracket"][0] != root["bracket"][1]
                        and not _close(root["bracket"][1] - root["bracket"][0], scan["spacing"])
                    )
                    or any(
                        abs(
                            (endpoint - scan["time_window"][0]) / scan["spacing"]
                            - round((endpoint - scan["time_window"][0]) / scan["spacing"])
                        )
                        > 5.0e-13
                        for endpoint in root["bracket"]
                    )
                )
                for root in all_roots
            )
            or scan["reference_maximum_density_per_budget"] + 5.0e-13
            < max(
                [row["density_per_budget"] for row in saved]
                + [root["density_per_budget"] for root in all_roots]
            )
            or scan["topology"] != [root["type"] for root in roots]
            or type(scan["physical_law_gates"]) is not dict
            or set(scan["physical_law_gates"]) != set(SCAN_PHYSICAL_GATE_NAMES)
            or any(type(value) is not bool for value in scan["physical_law_gates"].values())
        ):
            return False
        serialized_rows = [
            *full,
            *[
                {
                    "time": root["time"],
                    "density": BUDGET_HOMOTOPY["target_budget"] * root["density_per_budget"],
                    "survival": root["survival"],
                    "minimum_state_component": root["minimum_state_component"],
                    "differential_mass_balance_error": root["differential_mass_balance_error"],
                }
                for root in all_roots
            ],
        ]
        ordered = sorted(serialized_rows, key=lambda item: item["time"])
        if (
            any(
                right["survival"]
                > left["survival"] + REPRESENTATIVE_GATES["maximum_survival_increase"]
                for left, right in zip(ordered, ordered[1:])
            )
            or scan["minimum_sampled_density"]
            > min(row["density"] for row in serialized_rows) + 5.0e-13
            or scan["minimum_sampled_survival"]
            > min(row["survival"] for row in serialized_rows) + 5.0e-13
            or scan["minimum_sampled_state"]
            > min(row["minimum_state_component"] for row in serialized_rows) + 5.0e-13
            or scan["maximum_sampled_differential_mass_balance_error"] + 5.0e-13
            < max(row["differential_mass_balance_error"] for row in serialized_rows)
        ):
            return False
        reconstructed = scan_physical_gate_results(scan, model_diagnostics)
        return scan["physical_law_gates"] == reconstructed
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def validate_control_contract(control: Any, cells: int) -> bool:
    if not _exact_keys(control, CONTROL_KEYS):
        return False
    gates = control["gates"]
    if type(gates) is not dict or set(gates) != set(CONTROL_GATE_NAMES):
        return False
    if any(type(value) is not bool for value in gates.values()):
        return False
    if control["status"] == "HOLD_CONTROL_EVALUATION":
        theta = control["theta"]
        weights = control["weights"]
        return bool(
            type(control["reason"]) is str
            and (theta is None or _float_vector(theta, 2))
            and (weights is None or _float_vector(weights, 4))
            and (
                (theta is None and weights is None)
                or (
                    theta is not None
                    and weights is not None
                    and all(
                        _close(left, right)
                        for left, right in zip(
                            weights,
                            weights_from_theta(np.asarray(theta, dtype=float)),
                            strict=True,
                        )
                    )
                )
            )
            and type(control["retained_maximum_count"]) is int
            and control["retained_maximum_count"] == 0
            and control["topology"] == []
            and control["stationary_scan"] is None
            and control["roots"] == []
            and control["all_bracketed_roots"] == []
            and control["tail_trace"] is None
            and control["model_diagnostics"] is None
            and control["peak_minimum_to_maximum_ratio"] is None
            and control["valley_to_smaller_peak_ratios"] is None
            and control["event_basin_masses"] is None
            and control["event_partition_closure_error"] is None
            and (control["final_survival"] is None or type(control["final_survival"]) is float)
            and control["minimum_final_state_component"] is None
            and control["score_term_margins"] is None
            and control["robustness_score"] is None
            and all(value is False for value in gates.values())
            and control["all_gates_passed"] is False
        )
    try:
        diagnostics = control["model_diagnostics"]
        scan = control["stationary_scan"]
        roots = control["roots"]
        tail = control["tail_trace"]
        if (
            control["status"] not in {"PASS_CONTROL_EVALUATION", HOLD_STATUS}
            or type(control["reason"]) is not str
            or type(control["retained_maximum_count"]) is not int
            or type(control["theta"]) is not list
            or len(control["theta"]) != 2
            or not all(type(value) is float for value in control["theta"])
            or type(control["weights"]) is not list
            or len(control["weights"]) != 4
            or not all(type(value) is float for value in control["weights"])
            or not np.array_equal(
                np.asarray(control["weights"]),
                weights_from_theta(np.asarray(control["theta"], dtype=float)),
            )
            or not validate_model_diagnostic_contract(
                diagnostics,
                cells,
                budget=BUDGET_HOMOTOPY["target_budget"],
                weights=control["weights"],
            )
            or not validate_scan_contract(scan, diagnostics)
            or control["roots"] != scan["roots"]
            or control["all_bracketed_roots"] != scan["all_bracketed_roots"]
            or control["topology"] != scan["topology"]
            or type(tail) is not list
            or len(tail) != len(REPRESENTATIVE_GATES["tail_checkpoints"])
            or any(
                not _exact_keys(row, {"time", *STATE_LAW_KEYS})
                or row["time"] != checkpoint
                or not validate_state_law_contract(
                    {key: row[key] for key in STATE_LAW_KEYS},
                    budget=BUDGET_HOMOTOPY["target_budget"],
                )
                for row, checkpoint in zip(
                    tail, REPRESENTATIVE_GATES["tail_checkpoints"], strict=True
                )
            )
        ):
            return False
        maxima = [root for root in roots if root["type"] == "maximum"]
        minima = [root for root in roots if root["type"] == "minimum"]
        topology = [root["type"] for root in roots]
        alternating = topology in (
            ["maximum"],
            ["maximum", "minimum", "maximum"],
            ["maximum", "minimum", "maximum", "minimum", "maximum"],
        )
        maximum_count = len(maxima) if alternating else 0
        if control["retained_maximum_count"] != maximum_count:
            return False
        peak_ratio = (
            min(root["density_per_budget"] for root in maxima)
            / max(root["density_per_budget"] for root in maxima)
            if maxima
            else 0.0
        )
        valley_ratios = [
            root["density_per_budget"]
            / min(roots[index - 1]["density_per_budget"], roots[index + 1]["density_per_budget"])
            for index, root in enumerate(roots)
            if root["type"] == "minimum" and 0 < index < len(roots) - 1
        ]
        survival = [1.0, *(root["survival"] for root in minima), control["final_survival"]]
        masses = [left - right for left, right in zip(survival, survival[1:])]
        if (
            type(control["event_basin_masses"]) is not list
            or len(control["event_basin_masses"]) != maximum_count
            or not all(_nonnegative_float(value) for value in control["event_basin_masses"])
            or len(masses) != maximum_count
            or any(value < 0.0 for value in masses)
            or not _nonnegative_float(control["event_partition_closure_error"])
            or not _nonnegative_float(control["final_survival"])
            or type(control["minimum_final_state_component"]) is not float
            or not _nonnegative_float(control["peak_minimum_to_maximum_ratio"])
            or not all(
                _nonnegative_float(value) for value in control["valley_to_smaller_peak_ratios"]
            )
            or any(
                not _close(left, right)
                for left, right in zip(control["event_basin_masses"], masses, strict=True)
            )
            or not _close(control["peak_minimum_to_maximum_ratio"], peak_ratio)
            or len(control["valley_to_smaller_peak_ratios"]) != len(valley_ratios)
            or any(
                not _close(left, right)
                for left, right in zip(
                    control["valley_to_smaller_peak_ratios"], valley_ratios, strict=True
                )
            )
            or not _close(control["final_survival"], tail[-1]["survival"])
            or not _close(
                control["minimum_final_state_component"], tail[-1]["minimum_state_component"]
            )
            or not _close(
                control["event_partition_closure_error"],
                abs(sum(masses) - (1.0 - control["final_survival"])),
            )
        ):
            return False
        rules = REPRESENTATIVE_GATES
        minimum_curvature = min((abs(root["scaled_curvature"]) for root in roots), default=0.0)
        maximum_residual = max((root["scaled_root_residual"] for root in roots), default=None)
        scan_gates = scan["physical_law_gates"]
        reconstructed = {
            "alternating_topology": alternating,
            "endpoint_signs": scan["endpoint_signs_passed"],
            "peak_ratio": peak_ratio >= rules["minimum_peak_ratio"],
            "valley_ratio": max(valley_ratios, default=0.0) <= rules["maximum_valley_ratio"],
            "curvature": minimum_curvature >= rules["minimum_absolute_scaled_curvature"],
            "root_residual": maximum_residual is not None
            and maximum_residual <= rules["maximum_scaled_root_residual"],
            "event_masses": bool(masses) and min(masses) >= rules["minimum_each_event_basin_mass"],
            "positive_density_and_survival": scan_gates["positive_density_and_survival"]
            and all(row["density"] > rules["minimum_density"] for row in tail)
            and all(row["survival"] > rules["minimum_survival"] for row in tail),
            "survival_monotone": all(
                right <= left + rules["maximum_survival_increase"]
                for left, right in zip(survival, survival[1:])
            )
            and all(
                right["survival"] <= left["survival"] + rules["maximum_survival_increase"]
                for left, right in zip(tail, tail[1:])
            ),
            "sampled_state_nonnegative": scan_gates["state_nonnegative"],
            "sampled_survival_monotone": scan_gates["sampled_survival_monotone"],
            "survival_density_identity": scan_gates["survival_density_identity"]
            and all(
                row["survival_density_identity_error"] <= rules["maximum_survival_identity_error"]
                for row in tail
            ),
            "generator_killing_identity": scan_gates["generator_killing_identity"],
            "differential_mass_balance": scan_gates["differential_mass_balance"]
            and scan_gates["all_bracketed_roots_physical"]
            and all(
                row["differential_mass_balance_error"]
                <= rules["maximum_differential_mass_balance_error"]
                for row in tail
            ),
            "event_partition_closure": control["event_partition_closure_error"]
            <= rules["maximum_event_partition_closure_error"],
            "final_state_nonnegative": control["minimum_final_state_component"]
            >= -rules["maximum_negative_state_tolerance"],
            "initial_mass": scan_gates["initial_mass"],
            "installed_budget": scan_gates["installed_budget"],
            "finite_factor_diagnostics": scan_gates["finite_factor_diagnostics"],
        }
        if gates != reconstructed or control["all_gates_passed"] is not all(gates.values()):
            return False
        if control["status"] != ("PASS_CONTROL_EVALUATION" if all(gates.values()) else HOLD_STATUS):
            return False
        margins = {
            "peak_ratio": peak_ratio / rules["minimum_peak_ratio"] - 1.0,
            "valley_ratio": (rules["maximum_valley_ratio"] - max(valley_ratios, default=0.0))
            / (1.0 - rules["maximum_valley_ratio"]),
            "absolute_scaled_curvature": minimum_curvature
            / rules["minimum_absolute_scaled_curvature"]
            - 1.0,
            "event_basin_mass": min(masses, default=0.0) / rules["minimum_each_event_basin_mass"]
            - 1.0,
        }
        return bool(
            _exact_keys(control["score_term_margins"], set(PHASE_SEARCH["score_terms"]))
            and all(
                _close(control["score_term_margins"][key], value) for key, value in margins.items()
            )
            and _close(
                control["robustness_score"],
                min(margins[key] for key in PHASE_SEARCH["score_terms"]),
            )
        )
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def validate_remote_contract(remote: Any) -> bool:
    if not _exact_keys(remote, REMOTE_KEYS):
        return False
    try:
        lineage = remote["root_lineage"]
        if (
            type(remote["remote_pair_present"]) is not bool
            or (remote["pair_identity"] is not None and type(remote["pair_identity"]) is not str)
            or (
                remote["anchor_pair_identity"] is not None
                and type(remote["anchor_pair_identity"]) is not str
            )
            or type(lineage) is not list
            or any(
                not _exact_keys(row, LINEAGE_KEYS)
                or row["global_root_ordinal"] != index
                or row["type"] not in {"maximum", "minimum"}
                or row["side"] not in {"negative_time", "positive_time"}
                or type(row["time"]) is not float
                or type(row["origin_bracket_index"]) is not int
                or type(row["previous_bracket_index"]) is not int
                or type(row["current_bracket_index"]) is not int
                or any(
                    row[key] is not None and type(row[key]) is not int
                    for key in {
                        "predecessor_global_root_ordinal",
                        "successor_global_root_ordinal",
                        "matched_previous_global_root_ordinal",
                    }
                )
                or type(row["adjacent_time_drift"]) is not float
                or row["adjacent_time_drift"] < 0.0
                for index, row in enumerate(lineage)
            )
            or type(remote["lineage_status"]) is not str
            or type(remote["lineage_passed"]) is not bool
            or type(remote["lineage_hold_reasons"]) is not list
            or not all(type(item) is str for item in remote["lineage_hold_reasons"])
            or type(remote["maximum_observed_adjacent_drift"]) is not float
            or remote["maximum_observed_adjacent_drift"] < 0.0
            or remote["candidate_search_bounded_to_frozen_window"] is not True
        ):
            return False
        pair = remote["pair"]
        if pair is None:
            return remote["remote_pair_present"] is False and remote["lineage_passed"] is False
        return bool(
            _exact_keys(pair, REMOTE_PAIR_KEYS)
            and all(
                type(pair[key]) is int
                for key in {
                    "maximum_global_root_ordinal",
                    "minimum_global_root_ordinal",
                    "maximum_bracket_index",
                    "minimum_bracket_index",
                    "eligible_root_count_at_anchor",
                }
            )
            and type(pair["selected_global_root_indices"]) is list
            and all(type(item) is int for item in pair["selected_global_root_indices"])
            and type(pair["origin_bracket_lineage"]) is list
            and all(type(item) is int for item in pair["origin_bracket_lineage"])
            and validate_root_contract(pair["maximum"], pair["maximum"]["bracket_index"])
            and validate_root_contract(pair["minimum"], pair["minimum"]["bracket_index"])
            and pair["pair_type"] == "maximum_minimum"
            and pair["maximum"]["type"] == "maximum"
            and pair["minimum"]["type"] == "minimum"
            and pair["side"] in {"negative_time", "positive_time"}
            and pair["selected_global_root_indices"]
            == [pair["maximum_global_root_ordinal"], pair["minimum_global_root_ordinal"]]
            and pair["minimum_global_root_ordinal"] == pair["maximum_global_root_ordinal"] + 1
            and pair["origin_bracket_lineage"]
            == [
                lineage[pair["maximum_global_root_ordinal"]]["origin_bracket_index"],
                lineage[pair["minimum_global_root_ordinal"]]["origin_bracket_index"],
            ]
            and remote["remote_pair_present"] is remote["lineage_passed"]
        )
    except (IndexError, KeyError, TypeError):
        return False


def _float_vector(value: Any, length: int) -> bool:
    return (
        type(value) is list and len(value) == length and all(type(item) is float for item in value)
    )


def _float_matrix(value: Any, rows: int, columns: int) -> bool:
    return (
        type(value) is list
        and len(value) == rows
        and all(_float_vector(row, columns) for row in value)
    )


def validate_homotopy_contract(homotopy: Any, cusp: Any) -> bool:
    if not _exact_keys(homotopy, {"status", "rows"}) or type(homotopy["rows"]) is not list:
        return False
    rows = homotopy["rows"]
    schedule = BUDGET_HOMOTOPY["schedule"]
    if not rows or len(rows) > len(schedule):
        return False
    try:
        for index, row in enumerate(rows):
            if (
                not _exact_keys(row, HOMOTOPY_ROW_KEYS)
                or type(row["budget"]) is not float
                or not _close(row["budget"], schedule[index])
                or type(row["status"]) is not str
                or type(row["converged"]) is not bool
                or type(row["iterations"]) is not int
                or not 0 <= row["iterations"] <= SOLVER["maximum_newton_iterations"]
                or type(row["reason"]) is not str
                or (row["point"] is not None and not _float_vector(row["point"], 3))
                or (
                    row["maximum_scaled_residual"] is not None
                    and type(row["maximum_scaled_residual"]) is not float
                )
                or (row["point"] is None) != (row["maximum_scaled_residual"] is None)
                or (
                    row["point"] is not None
                    and not point_in_trust_box(
                        row["point"][0], np.asarray(row["point"][1:], dtype=float)
                    )[0]
                )
                or (
                    row["maximum_scaled_residual"] is not None
                    and row["maximum_scaled_residual"] < 0.0
                )
            ):
                return False
            if row["converged"]:
                if (
                    row["status"] != "PASS_CUSP_SOLVE"
                    or row["point"] is None
                    or row["maximum_scaled_residual"] > SOLVER["scaled_residual_tolerance"]
                ):
                    return False
            elif index != len(rows) - 1 or row["status"] != HOLD_STATUS:
                return False
        passed = len(rows) == len(schedule) and all(row["converged"] for row in rows)
        if homotopy["status"] != ("PASS_HOMOTOPY" if passed else HOLD_STATUS):
            return False
        if passed:
            if cusp is None or not _float_vector(rows[-1]["point"], 3):
                return False
            return bool(
                _close(rows[-1]["point"][0], cusp["time"])
                and all(
                    _close(left, right)
                    for left, right in zip(rows[-1]["point"][1:], cusp["theta"], strict=True)
                )
            )
        return cusp is None or type(cusp) is dict
    except (IndexError, KeyError, TypeError):
        return False


def validate_snapshot_contract(snapshot: Any, *, include_state_law: bool) -> bool:
    keys = set(SNAPSHOT_KEYS)
    if include_state_law:
        keys.add("state_law_diagnostics")
    if not _exact_keys(snapshot, keys):
        return False
    try:
        if (
            type(snapshot["time"]) is not float
            or type(snapshot["budget"]) is not float
            or not _close(snapshot["budget"], BUDGET_HOMOTOPY["target_budget"])
            or not _float_vector(snapshot["theta"], 2)
            or not _float_vector(snapshot["weights"], 4)
            or type(snapshot["density_per_budget"]) is not float
            or snapshot["density_per_budget"] <= 0.0
            or not _float_vector(snapshot["per_budget_time_jets_0_to_4"], 5)
            or not _float_matrix(snapshot["allocation_time_jets"], 2, 5)
            or not point_in_trust_box(snapshot["time"], np.asarray(snapshot["theta"], dtype=float))[
                0
            ]
            or not _close(
                snapshot["density_per_budget"], snapshot["per_budget_time_jets_0_to_4"][0]
            )
            or any(
                not _close(left, right)
                for left, right in zip(
                    snapshot["weights"],
                    weights_from_theta(np.asarray(snapshot["theta"], dtype=float)),
                    strict=True,
                )
            )
        ):
            return False
        if not include_state_law:
            return True
        law = snapshot["state_law_diagnostics"]
        return bool(
            validate_state_law_contract(law, budget=snapshot["budget"])
            and _close(law["density_per_budget"], snapshot["density_per_budget"])
        )
    except (IndexError, KeyError, TypeError, ValueError):
        return False


def validate_derivative_audit_contract(derivative: Any) -> bool:
    if not _exact_keys(derivative, DERIVATIVE_AUDIT_KEYS):
        return False
    rows = derivative["rows"]
    if type(rows) is not list or len(rows) != 2:
        return False
    try:
        for index, row in enumerate(rows):
            if (
                not _exact_keys(row, DERIVATIVE_ROW_KEYS)
                or not all(type(row[key]) is float for key in DERIVATIVE_ROW_KEYS)
                or row["allocation_step"] != DERIVATIVE_AUDIT["allocation_steps"][index]
                or row["relative_time_step"] != DERIVATIVE_AUDIT["relative_time_steps"][index]
                or row["maximum_state_tangent_relative_l1_error"] < 0.0
                or row["maximum_dimensionless_jacobian_error"] < 0.0
            ):
                return False
        large, small = rows
        floor = DERIVATIVE_AUDIT["roundoff_floor"]
        factor = DERIVATIVE_AUDIT["required_error_reduction_factor"]
        state_decreased = small["maximum_state_tangent_relative_l1_error"] <= max(
            floor, factor * large["maximum_state_tangent_relative_l1_error"]
        )
        jacobian_decreased = small["maximum_dimensionless_jacobian_error"] <= max(
            floor, factor * large["maximum_dimensionless_jacobian_error"]
        )
        passed = bool(
            state_decreased
            and jacobian_decreased
            and small["maximum_state_tangent_relative_l1_error"]
            <= DERIVATIVE_AUDIT["maximum_normalized_disagreement"]
            and small["maximum_dimensionless_jacobian_error"]
            <= DERIVATIVE_AUDIT["maximum_normalized_disagreement"]
        )
        return bool(
            derivative["state_error_decrease_or_floor"] is state_decreased
            and derivative["jacobian_error_decrease_or_floor"] is jacobian_decreased
            and derivative["passed"] is passed
        )
    except (KeyError, TypeError):
        return False


def validate_cusp_diagnostics_contract(
    diagnostics: Any, cells: int, cusp: dict[str, Any], mesh_diagnostics: dict[str, Any]
) -> bool:
    if not _exact_keys(diagnostics, CUSP_DIAGNOSTIC_BASE_KEYS | {"gates", "all_gates_passed"}):
        return False
    try:
        scalar_keys = CUSP_DIAGNOSTIC_BASE_KEYS - {
            "model_diagnostics",
            "state_law_diagnostics",
            "dimensionless_jacobian",
            "derivative_audit",
            "projected_singular_values",
        }
        if (
            not all(type(diagnostics[key]) is float for key in scalar_keys)
            or not all(
                _nonnegative_float(diagnostics[key])
                for key in {
                    "maximum_dimensionless_residual",
                    "projected_singular_value_ratio",
                    "full_smallest_singular_value",
                    "determinant_factorization_relative_residual",
                    "maximum_survival_identity_residual",
                }
            )
            or diagnostics["model_diagnostics"] != mesh_diagnostics
            or not validate_model_diagnostic_contract(
                diagnostics["model_diagnostics"],
                cells,
                budget=cusp["budget"],
                weights=cusp["weights"],
            )
            or not validate_state_law_contract(
                diagnostics["state_law_diagnostics"], budget=cusp["budget"]
            )
            or not _float_vector(diagnostics["projected_singular_values"], 2)
            or not all(value >= 0.0 for value in diagnostics["projected_singular_values"])
            or not _float_matrix(diagnostics["dimensionless_jacobian"], 3, 3)
            or not validate_derivative_audit_contract(diagnostics["derivative_audit"])
            or type(diagnostics["gates"]) is not dict
            or set(diagnostics["gates"]) != CUSP_GATE_NAMES
            or any(type(value) is not bool for value in diagnostics["gates"].values())
            or type(diagnostics["all_gates_passed"]) is not bool
        ):
            return False
        time = cusp["time"]
        jets = np.asarray(cusp["per_budget_time_jets_0_to_4"], dtype=float)
        allocation = np.asarray(cusp["allocation_time_jets"], dtype=float)
        density = jets[0]
        if density <= 0.0:
            return False
        raw = np.asarray(
            (
                (jets[2], allocation[0, 1], allocation[1, 1]),
                (jets[3], allocation[0, 2], allocation[1, 2]),
                (jets[4], allocation[0, 3], allocation[1, 3]),
            )
        )
        row_scale = np.asarray((time / density, time**2 / density, time**3 / density))
        column_scale = np.asarray((time, 1.0, 1.0))
        matrix = row_scale[:, None] * raw * column_scale[None, :]
        projected = np.linalg.svd(matrix[:2, 1:], compute_uv=False)
        full = np.linalg.svd(matrix, compute_uv=False)
        fourth = float(time**4 * jets[4] / density)
        left = float(np.linalg.det(matrix))
        right = float(fourth * np.linalg.det(matrix[:2, 1:]))
        determinant_residual = abs(left - right) / max(abs(left), abs(right), 1.0e-300)
        residual = float(
            np.max(
                np.abs(np.asarray((time * jets[1], time**2 * jets[2], time**3 * jets[3])) / density)
            )
        )
        if (
            not np.allclose(
                matrix, diagnostics["dimensionless_jacobian"], rtol=5.0e-13, atol=5.0e-13
            )
            or not np.allclose(
                projected,
                diagnostics["projected_singular_values"],
                rtol=5.0e-13,
                atol=5.0e-13,
            )
            or not _close(diagnostics["maximum_dimensionless_residual"], residual)
            or not _close(diagnostics["minimum_weight"], min(cusp["weights"]))
            or not _close(diagnostics["scaled_fourth_derivative"], fourth)
            or not _close(
                diagnostics["projected_singular_value_ratio"],
                projected[-1] / projected[0] if projected[0] > 0.0 else 0.0,
            )
            or not _close(diagnostics["full_smallest_singular_value"], full[-1])
            or not _close(
                diagnostics["determinant_factorization_relative_residual"], determinant_residual
            )
        ):
            return False
        physical = law_gate_results(mesh_diagnostics, [diagnostics["state_law_diagnostics"]])
        gates = {
            "cusp_residual": residual <= CUSP_GATES["maximum_dimensionless_residual"],
            "simplex_margin": diagnostics["minimum_weight"] >= CUSP_GATES["minimum_simplex_weight"],
            "quartic_nondegeneracy": abs(fourth)
            >= CUSP_GATES["minimum_absolute_scaled_fourth_derivative"],
            "projected_rank_floor": projected[-1]
            >= CUSP_GATES["minimum_projected_second_singular_value"],
            "projected_rank_ratio": diagnostics["projected_singular_value_ratio"]
            >= CUSP_GATES["minimum_projected_singular_value_ratio"],
            "full_jacobian_rank": full[-1] >= CUSP_GATES["minimum_full_jacobian_singular_value"],
            "determinant_factorization": determinant_residual
            <= CUSP_GATES["maximum_determinant_factorization_relative_residual"],
            "mixed_jet_audit": diagnostics["derivative_audit"]["passed"],
            "survival_identities": diagnostics["maximum_survival_identity_residual"]
            <= CUSP_GATES["maximum_explicit_action_residual"],
            **physical,
        }
        return bool(
            diagnostics["gates"] == gates and diagnostics["all_gates_passed"] is all(gates.values())
        )
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def validate_fold_node_contract(node: Any, cells: int, *, comparison: bool = False) -> bool:
    keys = COMPARISON_NODE_KEYS if comparison else FOLD_NODE_KEYS
    if not _exact_keys(node, keys):
        return False
    try:
        if (
            type(node["acceptance_index"]) is not int
            or type(node["time"]) is not float
            or not _float_vector(node["theta"], 2)
            or not _float_vector(node["weights"], 4)
            or not point_in_trust_box(node["time"], np.asarray(node["theta"], dtype=float))[0]
            or any(
                not _close(left, right)
                for left, right in zip(
                    node["weights"],
                    weights_from_theta(np.asarray(node["theta"], dtype=float)),
                    strict=True,
                )
            )
            or type(node["normalized_fold_residual"]) is not float
            or not _nonnegative_float(node["normalized_fold_residual"])
            or type(node["scaled_third_derivative"]) is not float
            or not _float_vector(node["dimensionless_fold_singular_values"], 2)
            or not all(value >= 0.0 for value in node["dimensionless_fold_singular_values"])
            or not validate_model_diagnostic_contract(
                node["model_diagnostics"],
                cells,
                budget=BUDGET_HOMOTOPY["target_budget"],
                weights=node["weights"],
            )
            or not validate_state_law_contract(
                node["state_law_diagnostics"], budget=BUDGET_HOMOTOPY["target_budget"]
            )
            or type(node["physical_law_gates"]) is not dict
            or set(node["physical_law_gates"]) != LAW_GATE_NAMES
            or node["physical_law_gates"]
            != law_gate_results(node["model_diagnostics"], [node["state_law_diagnostics"]])
        ):
            return False
        return not comparison or (
            all(
                type(node[key]) is float
                for key in {
                    "signed_time_offset",
                    "target_signed_time_offset",
                    "absolute_time_offset_mismatch",
                }
            )
            and node["target_signed_time_offset"] >= 0.0
            and node["absolute_time_offset_mismatch"] >= 0.0
        )
    except (KeyError, TypeError, ValueError):
        return False


def validate_branch_contract(
    branch: Any,
    cells: int,
    sign: int,
    cusp_time: float,
    anchor: dict[str, Any],
) -> bool:
    if not _exact_keys(branch, BRANCH_KEYS):
        return False
    orientation = "positive_time" if sign > 0 else "negative_time"
    try:
        if (
            branch["orientation"] != orientation
            or type(branch["gates"]) is not dict
            or set(branch["gates"]) != set(BRANCH_GATE_NAMES)
            or any(type(value) is not bool for value in branch["gates"].values())
            or type(branch["nodes"]) is not list
        ):
            return False
        nodes = branch["nodes"]
        if any(
            not validate_fold_node_contract(node, cells) or node["acceptance_index"] != index
            for index, node in enumerate(nodes)
        ):
            return False
        comparisons = branch["comparison_nodes"]
        remote_rows = branch["comparison_node_remote_pairs"]
        if comparisons is None or remote_rows is None:
            if comparisons is not None or remote_rows is not None:
                return False
            comparisons_list: list[dict[str, Any]] = []
            remote_list: list[dict[str, Any]] = []
        else:
            if type(comparisons) is not list or type(remote_rows) is not list:
                return False
            comparisons_list = comparisons
            remote_list = remote_rows
        desired_sign = 1.0 if sign > 0 else -1.0
        expected_comparisons = []
        used: set[int] = set()
        for target in FOLD_CONTINUATION["comparison_time_offsets"]:
            eligible = [
                node
                for node in nodes
                if desired_sign * (node["time"] - cusp_time) > 0.0
                and node["acceptance_index"] not in used
            ]
            if not eligible:
                expected_comparisons = []
                break
            chosen = min(
                eligible,
                key=lambda node: (
                    abs(desired_sign * (node["time"] - cusp_time) - target),
                    node["normalized_fold_residual"],
                    node["acceptance_index"],
                ),
            )
            expected = dict(chosen)
            expected["signed_time_offset"] = float(desired_sign * (chosen["time"] - cusp_time))
            expected["target_signed_time_offset"] = float(target)
            expected["absolute_time_offset_mismatch"] = float(
                abs(expected["signed_time_offset"] - target)
            )
            expected_comparisons.append(expected)
            used.add(chosen["acceptance_index"])
        if comparisons_list != expected_comparisons:
            return False
        if len(remote_list) != len(comparisons_list):
            return False
        previous = anchor
        comparison_scan_passed = len(remote_list) == 3
        lineage_passed = len(remote_list) == 3 and anchor["lineage_passed"] is True
        identities = []
        for comparison, remote_row in zip(comparisons_list, remote_list, strict=True):
            if not _exact_keys(
                remote_row, {"acceptance_index", "time", "remote_pair", "stationary_scan"}
            ):
                return False
            if (
                remote_row["acceptance_index"] != comparison["acceptance_index"]
                or remote_row["time"] != comparison["time"]
            ):
                return False
            current = remote_row["remote_pair"]
            if remote_row["stationary_scan"] is None:
                if not (
                    validate_remote_contract(current)
                    and current["remote_pair_present"] is False
                    and current["pair_identity"] is None
                    and current["anchor_pair_identity"] == anchor["pair_identity"]
                    and current["pair"] is None
                    and current["root_lineage"] == []
                    and current["lineage_status"] == "HOLD_LINEAGE"
                    and current["lineage_passed"] is False
                    and current["lineage_hold_reasons"]
                    and current["maximum_observed_adjacent_drift"] == 0.0
                ):
                    return False
                comparison_scan_passed = False
                lineage_passed = False
            else:
                if not validate_scan_contract(
                    remote_row["stationary_scan"], comparison["model_diagnostics"]
                ):
                    return False
                expected_remote = continue_remote_pair_lineage(
                    remote_row["stationary_scan"], comparison["time"], anchor, previous
                )
                if current != expected_remote:
                    return False
                comparison_scan_passed = comparison_scan_passed and all(
                    remote_row["stationary_scan"]["physical_law_gates"].values()
                )
                lineage_passed = lineage_passed and current["lineage_passed"]
                previous = current
            identities.append(current["pair_identity"])
        signed_reach = max(
            (desired_sign * (node["time"] - cusp_time) for node in nodes), default=-math.inf
        )
        gates = {
            "minimum_nodes": len(nodes) >= FOLD_CONTINUATION["minimum_accepted_noncusp_nodes"],
            "required_reach": signed_reach >= FOLD_CONTINUATION["required_absolute_time_reach"],
            "comparison_nodes_present": len(comparisons_list) == 3,
            "comparison_nodes_distinct": len(
                {node["acceptance_index"] for node in comparisons_list}
            )
            == 3,
            "comparison_nodes_on_signed_side": len(comparisons_list) == 3
            and all(node["signed_time_offset"] > 0.0 for node in comparisons_list),
            "comparison_offset_mismatch": len(comparisons_list) == 3
            and all(
                node["absolute_time_offset_mismatch"]
                <= FOLD_CONTINUATION["maximum_comparison_time_offset_mismatch"]
                for node in comparisons_list
            ),
            "fold_residuals": bool(nodes)
            and max(node["normalized_fold_residual"] for node in nodes)
            <= FOLD_CONTINUATION["maximum_normalized_fold_residual"],
            "third_derivative": bool(nodes)
            and all(
                node["scaled_third_derivative"]
                >= FOLD_CONTINUATION["minimum_scaled_third_derivative"]
                for node in nodes
                if abs(node["time"] - cusp_time) >= 0.25
            ),
            "fold_rank": bool(nodes)
            and all(
                node["dimensionless_fold_singular_values"][-1]
                >= FOLD_CONTINUATION["minimum_dimensionless_fold_singular_value"]
                for node in nodes
            ),
            "physical_law": bool(nodes)
            and all(all(node["physical_law_gates"].values()) for node in nodes),
            "comparison_scan_physical_law": comparison_scan_passed,
            "remote_pair_retained": len(remote_list) == 3
            and all(row["remote_pair"]["remote_pair_present"] for row in remote_list),
            "stable_remote_pair_identity": len(identities) == 3
            and identities[0] is not None
            and len(set(identities)) == 1
            and identities[0] == anchor["pair_identity"],
            "remote_pair_lineage": lineage_passed,
        }
        return bool(
            branch["gates"] == gates
            and branch["status"]
            == ("PASS_BRANCH_DISCOVERY" if all(gates.values()) else "HOLD_BRANCH")
        )
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def validate_phase_contract(
    phase: Any,
    expected_cusp_theta: list[float] | None = None,
    cells: int = 65,
) -> bool:
    if phase is None:
        return True
    keys = {
        "phase_centre_theta",
        "candidate_generation",
        "screened_mesh_65",
        "advanced_mesh_97",
        "representatives",
        "all_three_regions_found",
        "phase_complete",
        "hold_reasons",
        "search_expanded",
    }
    if not _exact_keys(phase, keys):
        return False
    candidate_keys = {
        "candidate_index",
        "radius",
        "direction",
        "theta",
        "weights",
        "eligible_geometry",
    }
    screened_keys = candidate_keys | {"mesh_65", "mesh_65_evaluation_status"}
    advanced_keys = screened_keys | {
        "mesh_97",
        "mesh_97_evaluation_status",
        "worst_score",
        "both_meshes_pass",
    }
    try:
        generated = phase["candidate_generation"]
        screened = phase["screened_mesh_65"]
        advanced = phase["advanced_mesh_97"]
        if (
            not _float_vector(phase["phase_centre_theta"], 2)
            or (
                expected_cusp_theta is not None
                and (
                    not _float_vector(expected_cusp_theta, 2)
                    or any(
                        abs(left - right) > PHASE_SEARCH["centre_formula_absolute_tolerance"]
                        for left, right in zip(
                            phase["phase_centre_theta"], expected_cusp_theta, strict=True
                        )
                    )
                )
            )
            or type(generated) is not list
            or len(generated) != PHASE_SEARCH["candidate_count"]
            or type(screened) is not list
            or len(screened) != len(generated)
            or type(advanced) is not list
            or not _exact_keys(phase["representatives"], {"1", "2", "3"})
            or type(phase["all_three_regions_found"]) is not bool
            or type(phase["phase_complete"]) is not bool
            or type(phase["hold_reasons"]) is not list
            or not all(type(item) is str for item in phase["hold_reasons"])
            or phase["search_expanded"] is not False
        ):
            return False
        centre = np.asarray(phase["phase_centre_theta"], dtype=float)
        for index, candidate in enumerate(generated):
            if (
                not _exact_keys(candidate, candidate_keys)
                or type(candidate["candidate_index"]) is not int
                or candidate["candidate_index"] != index
            ):
                return False
            expected_radius = PHASE_SEARCH["radii"][index // len(PHASE_SEARCH["directions"])]
            expected_direction = PHASE_SEARCH["directions"][index % len(PHASE_SEARCH["directions"])]
            if (
                type(candidate["radius"]) is not float
                or candidate["radius"] != expected_radius
                or not _float_vector(candidate["direction"], 2)
                or candidate["direction"] != expected_direction
            ):
                return False
            theta = np.asarray(candidate["theta"], dtype=float)
            if not _float_vector(candidate["theta"], 2) or not np.all(np.isfinite(theta)):
                return False
            expected_theta = centre + expected_radius * np.asarray(expected_direction)
            if (
                np.max(np.abs(theta - expected_theta))
                > PHASE_SEARCH["centre_formula_absolute_tolerance"]
            ):
                return False
            if not _float_vector(candidate["weights"], 4) or any(
                not _close(left, right)
                for left, right in zip(candidate["weights"], weights_from_theta(theta), strict=True)
            ):
                return False
            expected_geometry = bool(
                point_in_trust_box(REFERENCE_CUSP_TIME, theta)[0]
                and min(candidate["weights"]) >= SOLVER["minimum_simplex_weight"]
            )
            if type(candidate["eligible_geometry"]) is not bool or (
                candidate["eligible_geometry"] is not expected_geometry
            ):
                return False
        for candidate, row in zip(generated, screened, strict=True):
            if not _exact_keys(row, screened_keys):
                return False
            if {key: row[key] for key in candidate_keys} != candidate:
                return False
            status = row["mesh_65_evaluation_status"]
            if status == "EVALUATED":
                if not validate_control_contract(row["mesh_65"], cells):
                    return False
            elif status == "NOT_ELIGIBLE_GEOMETRY":
                if row["eligible_geometry"] or row["mesh_65"] is not None:
                    return False
            elif status == "HOLD_CONTROL_EVALUATION":
                if row["mesh_65"] is not None and not validate_control_contract(
                    row["mesh_65"], cells
                ):
                    return False
            else:
                return False
        missing_65_indices = [
            row["candidate_index"]
            for row in screened
            if row["eligible_geometry"] and row["mesh_65_evaluation_status"] != "EVALUATED"
        ]
        if missing_65_indices:
            return bool(
                advanced == []
                and phase["representatives"] == {"1": None, "2": None, "3": None}
                and phase["all_three_regions_found"] is False
                and phase["phase_complete"] is False
                and phase["hold_reasons"]
                == [f"missing_eligible_mesh_65_evaluations:{missing_65_indices}"]
            )
        expected_advanced_bases = []
        for target in PHASE_SEARCH["target_retained_maximum_counts"]:
            eligible = [
                row
                for row in screened
                if row["mesh_65"] is not None
                and row["mesh_65_evaluation_status"] == "EVALUATED"
                and row["mesh_65"]["retained_maximum_count"] == target
                and row["mesh_65"]["gates"]["alternating_topology"]
                and row["mesh_65"]["gates"]["endpoint_signs"]
                and row["mesh_65"]["gates"]["root_residual"]
                and row["mesh_65"]["robustness_score"] is not None
            ]
            eligible.sort(
                key=lambda row: (-row["mesh_65"]["robustness_score"], tuple(row["weights"]))
            )
            expected_advanced_bases.extend(
                eligible[: int(PHASE_SEARCH["maximum_advanced_per_mode_count"])]
            )
        if len(advanced) != len(expected_advanced_bases):
            return False
        for base, row in zip(expected_advanced_bases, advanced, strict=True):
            if not _exact_keys(row, advanced_keys):
                return False
            if {key: row[key] for key in screened_keys} != base:
                return False
            if row["mesh_97_evaluation_status"] == "EVALUATED":
                if not validate_control_contract(row["mesh_97"], 97):
                    return False
                expected_worst = min(
                    row["mesh_65"]["robustness_score"], row["mesh_97"]["robustness_score"]
                )
                if not _close(row["worst_score"], expected_worst):
                    return False
                target = row["mesh_65"]["retained_maximum_count"]
                expected_both = bool(
                    row["mesh_65"]["all_gates_passed"]
                    and row["mesh_97"]["all_gates_passed"]
                    and row["mesh_97"]["retained_maximum_count"] == target
                )
                if row["both_meshes_pass"] is not expected_both:
                    return False
            elif row["mesh_97_evaluation_status"] == "HOLD_CONTROL_EVALUATION":
                if row["worst_score"] is not None or row["both_meshes_pass"] is not False:
                    return False
            else:
                return False
        expected_representatives: dict[str, Any] = {}
        for target in (1, 2, 3):
            passing = [
                row
                for row in advanced
                if row["mesh_65"]["retained_maximum_count"] == target
                and row["both_meshes_pass"] is True
            ]
            passing.sort(key=lambda row: (-row["worst_score"], tuple(row["weights"])))
            expected_representatives[str(target)] = passing[0] if passing else None
        missing = any(
            row["eligible_geometry"] and row["mesh_65_evaluation_status"] != "EVALUATED"
            for row in screened
        ) or any(row["mesh_97_evaluation_status"] != "EVALUATED" for row in advanced)
        expected_complete = not missing
        expected_hold_reasons = [
            f"missing_selected_mesh_97_evaluation:{row['candidate_index']}"
            for row in advanced
            if row["mesh_97_evaluation_status"] != "EVALUATED"
        ]
        if not expected_complete:
            expected_representatives = {"1": None, "2": None, "3": None}
        expected_found = bool(
            expected_complete
            and all(expected_representatives[str(target)] is not None for target in (1, 2, 3))
        )
        return bool(
            phase["phase_complete"] is expected_complete
            and phase["representatives"] == expected_representatives
            and phase["all_three_regions_found"] is expected_found
            and phase["hold_reasons"] == expected_hold_reasons
        )
    except (IndexError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def validate_lexical_snapshot_contract(value: Any, expected_pins: dict[str, str]) -> bool:
    expected_roles = {"manifest", *expected_pins}
    metadata_keys = {
        "path",
        "st_dev",
        "st_ino",
        "st_mode",
        "st_nlink",
        "st_uid",
        "st_gid",
        "st_size",
        "st_mtime_ns",
        "sha256",
    }
    if type(value) is not dict or set(value) != expected_roles:
        return False
    for role, row in value.items():
        if not _exact_keys(row, metadata_keys):
            return False
        if type(row["path"]) is not str or type(row["sha256"]) is not str:
            return False
        if any(type(row[key]) is not int for key in metadata_keys - {"path", "sha256"}):
            return False
        if role != "manifest" and row["sha256"] != expected_pins[role]:
            return False
    return True


def validate_nested_result_contract(result: dict[str, Any], expected_pins: dict[str, str]) -> bool:
    rows = result["discovery_mesh_rows"]
    for cells, row in zip(DISCOVERY_MESHES, rows, strict=True):
        if row["status"] in {"NOT_RUN_AFTER_HOLD", "NOT_RUN_AFTER_PREFLIGHT_HOLD"}:
            if row != not_run_mesh_row(cells, row["reason"], row["status"]):
                return False
            continue
        homotopy = row["homotopy"]
        if not validate_homotopy_contract(homotopy, row["cusp"]):
            return False
        if homotopy["status"] == HOLD_STATUS:
            if not (
                row["status"] == HOLD_STATUS
                and row["reason"] == "homotopy_failed"
                and row["model_diagnostics"] is None
                and row["cusp"] is None
                and row["cusp_diagnostics"] is None
                and row["stationary_scan"] is None
                and row["remote_pair"] is None
                and row["branches"] is None
                and row["all_mesh_discovery_gates_passed"] is False
            ):
                return False
            continue
        if row["cusp_diagnostics"] is None:
            if not (
                row["status"] == HOLD_STATUS
                and row["reason"] == "post_homotopy_numerical_evaluation_failed"
                and row["model_diagnostics"] is None
                and validate_snapshot_contract(row["cusp"], include_state_law=False)
                and row["stationary_scan"] is None
                and row["remote_pair"] is None
                and row["branches"] is None
                and row["all_mesh_discovery_gates_passed"] is False
            ):
                return False
            continue
        diagnostics = row["model_diagnostics"]
        cusp = row["cusp"]
        if (
            not validate_model_diagnostic_contract(diagnostics, cells)
            or not validate_snapshot_contract(cusp, include_state_law=True)
            or cusp["state_law_diagnostics"] != row["cusp_diagnostics"]["state_law_diagnostics"]
            or not validate_cusp_diagnostics_contract(
                row["cusp_diagnostics"], cells, cusp, diagnostics
            )
            or not validate_scan_contract(row["stationary_scan"], diagnostics)
            or not validate_remote_contract(row["remote_pair"])
            or row["remote_pair"] != assess_remote_pair(row["stationary_scan"], cusp["time"])
            or not _exact_keys(row["branches"], {"negative", "positive"})
        ):
            return False
        for name, sign in (("negative", -1), ("positive", 1)):
            if not validate_branch_contract(
                row["branches"][name], cells, sign, cusp["time"], row["remote_pair"]
            ):
                return False
        passed = bool(
            row["cusp_diagnostics"]["all_gates_passed"]
            and all(row["stationary_scan"]["physical_law_gates"].values())
            and row["remote_pair"]["remote_pair_present"]
            and all(
                branch["status"] == "PASS_BRANCH_DISCOVERY" for branch in row["branches"].values()
            )
        )
        if (
            row["all_mesh_discovery_gates_passed"] is not passed
            or row["status"] != ("PASS_MESH_DISCOVERY" if passed else HOLD_STATUS)
            or row["reason"] != ("all_mesh_gates_passed" if passed else "mesh_gate_failed")
        ):
            return False
    phase = result["bounded_phase_discovery"]
    expected_cusp_theta = None
    if phase is not None:
        mesh_97_cusp = rows[1]["cusp"]
        if type(mesh_97_cusp) is not dict or not _float_vector(mesh_97_cusp.get("theta"), 2):
            return False
        expected_cusp_theta = mesh_97_cusp["theta"]
    return validate_phase_contract(phase, expected_cusp_theta)


def validate_result_contract(
    result: Any, expected_manifest_sha256: str, expected_pins: dict[str, str]
) -> dict[str, Any]:
    """Fail closed on the exact v3 scientific and negative-claim result contract."""

    def fail(message: str) -> None:
        raise RuntimeError(f"result contract: {message}")

    if type(result) is not dict:
        fail("top level must be an object")
    try:
        require_finite_json(result)
    except (TypeError, ValueError) as error:
        fail(str(error))
    expected_keys = {
        "schema_version",
        "stage",
        "status",
        "evidence_timing",
        "claim_scope",
        "manifest_sha256",
        "small_explicit_csr_preflight",
        "discovery_mesh_rows",
        "bounded_phase_discovery",
        "all_discovery_gates_passed",
        "required_claim_flags",
        "forbidden_claims",
        "pin_snapshots",
        "lexical_pin_snapshots",
        "pinned_file_hashes",
        "software",
        "limitations",
    }
    if set(result) != expected_keys:
        fail("top-level key set changed")
    if (
        type(result["schema_version"]) is not int
        or result["schema_version"] != SCHEMA_VERSION
        or result["stage"] != STAGE
    ):
        fail("schema or stage changed")
    if result["evidence_timing"] != EVIDENCE_TIMING:
        fail("evidence timing changed")
    if result["claim_scope"] != expected_manifest_contract()["claim_scope"]:
        fail("claim scope differs from the frozen manifest contract")
    if result["manifest_sha256"] != expected_manifest_sha256:
        fail("wrong manifest SHA-256")

    preflight = result["small_explicit_csr_preflight"]
    preflight_keys = {"mesh", "state_count", "errors", "maximum_error", "passed"}
    if type(preflight) is not dict or set(preflight) != preflight_keys:
        fail("explicit-CSR preflight is malformed")
    if (
        type(preflight["mesh"]) is not list
        or len(preflight["mesh"]) != 3
        or not all(
            type(item) is int and item == PREFLIGHT["small_explicit_csr_cells"]
            for item in preflight["mesh"]
        )
        or type(preflight["state_count"]) is not int
        or preflight["state_count"] != PREFLIGHT["small_explicit_csr_cells"] ** 3
        or type(preflight["passed"]) is not bool
        or type(preflight["maximum_error"]) is not float
        or preflight["maximum_error"] < 0.0
        or type(preflight["errors"]) is not dict
        or set(preflight["errors"])
        != {
            "column_action",
            "row_action",
            "augmented_column_action",
            "augmented_row_action",
        }
        or not all(type(value) is float and value >= 0.0 for value in preflight["errors"].values())
        or preflight["maximum_error"] != max(preflight["errors"].values())
        or preflight["passed"]
        != (preflight["maximum_error"] <= PREFLIGHT["maximum_action_residual"])
    ):
        fail("explicit-CSR preflight values are inconsistent")
    rows = result["discovery_mesh_rows"]
    if type(rows) is not list or len(rows) != 2:
        fail("exactly two fixed-shape mesh rows are required")
    row_keys = {
        "mesh",
        "status",
        "reason",
        "model_diagnostics",
        "homotopy",
        "cusp",
        "cusp_diagnostics",
        "stationary_scan",
        "remote_pair",
        "branches",
        "all_mesh_discovery_gates_passed",
    }
    for cells, row in zip(DISCOVERY_MESHES, rows, strict=True):
        if type(row) is not dict or set(row) != row_keys:
            fail(f"mesh {cells} row key set changed")
        if (
            type(row["mesh"]) is not list
            or len(row["mesh"]) != 3
            or not all(type(item) is int and item == cells for item in row["mesh"])
        ):
            fail(f"mesh {cells} identity changed")
        if type(row["status"]) is not str or type(row["reason"]) is not str:
            fail(f"mesh {cells} status/reason is malformed")
        if type(row["all_mesh_discovery_gates_passed"]) is not bool:
            fail(f"mesh {cells} gate is not Boolean")
        if row["all_mesh_discovery_gates_passed"]:
            if row["status"] != "PASS_MESH_DISCOVERY":
                fail(f"mesh {cells} PASS implication failed")
            if any(
                row[key] is None
                for key in (
                    "model_diagnostics",
                    "homotopy",
                    "cusp",
                    "cusp_diagnostics",
                    "stationary_scan",
                    "remote_pair",
                    "branches",
                )
            ):
                fail(f"mesh {cells} PASS row is incomplete")
            cusp_diagnostics = row["cusp_diagnostics"]
            stationary = row["stationary_scan"]
            remote = row["remote_pair"]
            branches = row["branches"]
            if (
                type(cusp_diagnostics) is not dict
                or cusp_diagnostics.get("all_gates_passed") is not True
                or type(stationary) is not dict
                or type(stationary.get("physical_law_gates")) is not dict
                or not stationary["physical_law_gates"]
                or not all(value is True for value in stationary["physical_law_gates"].values())
                or type(remote) is not dict
                or remote.get("remote_pair_present") is not True
                or type(remote.get("pair_identity")) is not str
                or not remote["pair_identity"]
                or type(branches) is not dict
                or set(branches) != {"negative", "positive"}
                or any(
                    type(branch) is not dict or branch.get("status") != "PASS_BRANCH_DISCOVERY"
                    for branch in branches.values()
                )
            ):
                fail(f"mesh {cells} nested PASS implication failed")
        elif row["status"] not in {
            HOLD_STATUS,
            "NOT_RUN_AFTER_HOLD",
            "NOT_RUN_AFTER_PREFLIGHT_HOLD",
        }:
            fail(f"mesh {cells} HOLD status is invalid")
    if not preflight["passed"]:
        if [row["status"] for row in rows] != [
            "NOT_RUN_AFTER_PREFLIGHT_HOLD",
            "NOT_RUN_AFTER_PREFLIGHT_HOLD",
        ]:
            fail("preflight HOLD leaked scientific construction")
        if result["bounded_phase_discovery"] is not None:
            fail("preflight HOLD must not contain a phase result")
    if not rows[0]["all_mesh_discovery_gates_passed"] and rows[1]["status"] not in {
        "NOT_RUN_AFTER_HOLD",
        "NOT_RUN_AFTER_PREFLIGHT_HOLD",
    }:
        fail("mesh 97 ran after an earlier HOLD")

    phase = result["bounded_phase_discovery"]
    phase_passed = False
    if phase is not None:
        phase_keys = {
            "phase_centre_theta",
            "candidate_generation",
            "screened_mesh_65",
            "advanced_mesh_97",
            "representatives",
            "all_three_regions_found",
            "phase_complete",
            "hold_reasons",
            "search_expanded",
        }
        if type(phase) is not dict or set(phase) != phase_keys:
            fail("phase key set changed")
        if (
            not _float_vector(phase["phase_centre_theta"], 2)
            or type(phase["candidate_generation"]) is not list
            or len(phase["candidate_generation"]) != PHASE_SEARCH["candidate_count"]
            or type(phase["screened_mesh_65"]) is not list
            or len(phase["screened_mesh_65"]) != PHASE_SEARCH["candidate_count"]
            or type(phase["advanced_mesh_97"]) is not list
            or len(phase["advanced_mesh_97"]) > 3 * PHASE_SEARCH["maximum_advanced_per_mode_count"]
        ):
            fail("phase cardinalities changed")
        candidate_indices = [
            row.get("candidate_index") for row in phase["candidate_generation"] if type(row) is dict
        ]
        if not all(type(item) is int for item in candidate_indices) or candidate_indices != list(
            range(PHASE_SEARCH["candidate_count"])
        ):
            fail("phase candidate identities changed")
        if (
            type(phase["representatives"]) is not dict
            or set(phase["representatives"]) != {"1", "2", "3"}
            or type(phase["all_three_regions_found"]) is not bool
            or type(phase["phase_complete"]) is not bool
            or type(phase["hold_reasons"]) is not list
            or not all(type(item) is str for item in phase["hold_reasons"])
            or phase["search_expanded"] is not False
        ):
            fail("phase completeness/claim fields are malformed")
        if not phase["phase_complete"] and phase["all_three_regions_found"]:
            fail("incomplete phase cannot pass")
        missing_screen = any(
            type(row) is not dict
            or (
                row.get("eligible_geometry") is True
                and row.get("mesh_65_evaluation_status") != "EVALUATED"
            )
            for row in phase["screened_mesh_65"]
        )
        missing_advanced = any(
            type(row) is not dict or row.get("mesh_97_evaluation_status") != "EVALUATED"
            for row in phase["advanced_mesh_97"]
        )
        if phase["phase_complete"] == (missing_screen or missing_advanced):
            fail("phase completeness does not match evaluation coverage")
        for target in (1, 2, 3):
            representative = phase["representatives"][str(target)]
            if representative is None:
                continue
            if (
                type(representative) is not dict
                or representative.get("both_meshes_pass") is not True
                or type(representative.get("mesh_65")) is not dict
                or type(representative.get("mesh_97")) is not dict
                or representative["mesh_65"].get("retained_maximum_count") != target
                or representative["mesh_97"].get("retained_maximum_count") != target
                or representative["mesh_65"].get("all_gates_passed") is not True
                or representative["mesh_97"].get("all_gates_passed") is not True
            ):
                fail(f"phase representative {target} is inconsistent")
        phase_passed = bool(
            phase["phase_complete"]
            and phase["all_three_regions_found"]
            and all(phase["representatives"][key] is not None for key in ("1", "2", "3"))
        )

    passed = result["all_discovery_gates_passed"]
    if type(passed) is not bool:
        fail("overall gate is not Boolean")
    reconstructed_pass = bool(
        preflight["passed"]
        and all(row["all_mesh_discovery_gates_passed"] for row in rows)
        and phase_passed
    )
    if passed != reconstructed_pass:
        fail("overall PASS does not reconstruct from subordinate gates")
    if result["status"] != (PASS_STATUS if passed else HOLD_STATUS):
        fail("status/PASS implication failed")

    flags = result["required_claim_flags"]
    expected_flags = sorted_bool_mapping(CLAIM_FLAGS)
    expected_flags["low_mesh_discovery_completed"] = passed
    if not exact_json_contract(flags, expected_flags):
        fail("negative claim flags changed")
    if not exact_json_contract(result["forbidden_claims"], FORBIDDEN_CLAIMS):
        fail("forbidden claims changed")
    if not exact_json_contract(result["limitations"], LIMITATIONS):
        fail("limitations changed")

    pin_snapshots = result["pin_snapshots"]
    if (
        type(pin_snapshots) is not dict
        or set(pin_snapshots) != {"before_formal", "after_formal"}
        or not exact_json_contract(pin_snapshots["before_formal"], expected_pins)
        or not exact_json_contract(pin_snapshots["after_formal"], expected_pins)
        or not exact_json_contract(result["pinned_file_hashes"], expected_pins)
    ):
        fail("complete pin snapshots changed")
    software = result["software"]
    if (
        type(software) is not dict
        or set(software) != {"python", "numpy", "scipy"}
        or not all(type(value) is str and value for value in software.values())
    ):
        fail("software record is malformed")
    lexical = result["lexical_pin_snapshots"]
    if (
        type(lexical) is not dict
        or set(lexical) != {"before_formal", "after_formal"}
        or not validate_lexical_snapshot_contract(lexical["before_formal"], expected_pins)
        or not validate_lexical_snapshot_contract(lexical["after_formal"], expected_pins)
        or lexical["before_formal"] != lexical["after_formal"]
    ):
        fail("lexical metadata snapshots changed")
    if not validate_nested_result_contract(result, expected_pins):
        fail("recursive nested schema/algebra contract failed")
    return result


def replica_paths(canonical: Path = OUTPUT) -> tuple[Path, Path]:
    return (
        canonical.with_name(f".{canonical.stem}.replica_1.json"),
        canonical.with_name(f".{canonical.stem}.replica_2.json"),
    )


def promotion_staging_paths(canonical: Path, evidence: Path) -> tuple[Path, Path]:
    canonical = Path(canonical)
    evidence = Path(evidence)
    return (
        canonical.with_name(f".{canonical.name}.staging"),
        evidence.with_name(f".{evidence.name}.staging"),
    )


def fsync_write(path: Path, payload: bytes) -> tuple[int, int]:
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    ownership: tuple[int, int] | None = None
    try:
        descriptor = os.open(Path(path), flags, 0o600)
        try:
            opened = os.fstat(descriptor)
            ownership = int(opened.st_dev), int(opened.st_ino)
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        if regular_path_inode(Path(path)) != ownership:
            raise RuntimeError("newly written path no longer names its owned inode")
        return ownership
    except BaseException:
        unlink_owned_path(Path(path), ownership)
        raise


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def promote_replica_bytes(
    result_bytes: bytes,
    evidence_bytes: bytes,
    canonical: Path,
    evidence: Path,
    post_promotion_check: Callable[[], None] | None = None,
) -> None:
    canonical = Path(canonical)
    evidence = Path(evidence)
    if lexical_path_exists(canonical) or lexical_path_exists(evidence):
        raise RuntimeError("formal outputs are append-only and may not be overwritten")
    result_stage, evidence_stage = promotion_staging_paths(canonical, evidence)
    require_lexically_absent((result_stage, evidence_stage), "promotion staging boundary")
    promoted_evidence: tuple[int, int] | None = None
    promoted_result: tuple[int, int] | None = None
    result_stage_owned: tuple[int, int] | None = None
    evidence_stage_owned: tuple[int, int] | None = None
    try:
        result_stage_owned = fsync_write(result_stage, result_bytes)
        evidence_stage_owned = fsync_write(evidence_stage, evidence_bytes)
        os.link(evidence_stage, evidence, follow_symlinks=False)
        promoted_evidence = regular_path_inode(evidence)
        if promoted_evidence != evidence_stage_owned:
            raise RuntimeError("promoted evidence is not the owned staged inode")
        fsync_directory(evidence.parent)
        os.link(result_stage, canonical, follow_symlinks=False)
        promoted_result = regular_path_inode(canonical)
        if promoted_result != result_stage_owned:
            raise RuntimeError("promoted result is not the owned staged inode")
        fsync_directory(canonical.parent)
        if (
            stable_regular_file_bytes(canonical)[0] != result_bytes
            or stable_regular_file_bytes(evidence)[0] != evidence_bytes
        ):
            raise RuntimeError("post-replace canonical byte verification failed")
        if post_promotion_check is not None:
            post_promotion_check()
    except BaseException:
        unlink_owned_path(canonical, promoted_result)
        unlink_owned_path(evidence, promoted_evidence)
        raise
    finally:
        unlink_owned_path(result_stage, result_stage_owned)
        unlink_owned_path(evidence_stage, evidence_stage_owned)


def revalidate_complete_pin_snapshot(
    manifest_path: Path,
    expected_manifest_sha256: str,
    expected_pins: dict[str, str],
    *,
    allow_promoted_outputs: bool = False,
) -> dict[str, str]:
    """Rehash every pin for the real freeze, with a narrow unit-test fallback."""

    path = Path(manifest_path)
    if sha256(path) != expected_manifest_sha256:
        raise RuntimeError("manifest changed during frozen execution")
    if path.resolve() != MANIFEST.resolve():
        return dict(expected_pins)
    observed = validate_manifest(load_json(path), require_outputs_absent=False)
    if observed != expected_pins:
        raise RuntimeError("complete pinned-file snapshot changed during frozen execution")
    return observed


def run_replica_commands(
    commands: Sequence[Sequence[str]],
    replicas: Sequence[Path],
    manifest_path: Path,
    expected_manifest_sha256: str,
    environment: dict[str, str],
    canonical_output: Path = OUTPUT,
    reproducibility_output: Path = REPRODUCIBILITY_OUTPUT,
    pinned_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    if len(commands) != 2 or len(replicas) != 2:
        raise ValueError("exactly two replicas are required")
    if sha256(manifest_path) != expected_manifest_sha256:
        raise ValueError("external manifest SHA-256 does not match")
    pin_snapshot = {} if pinned_hashes is None else dict(pinned_hashes)
    real_freeze = os.path.abspath(manifest_path) == os.path.abspath(MANIFEST)
    promotion_stages = promotion_staging_paths(canonical_output, reproducibility_output)
    require_lexically_absent(promotion_stages, "promotion staging boundary before replicas")
    if real_freeze:
        require_lexically_absent(scientific_output_paths(), "five-path pre-run boundary")
        frozen_manifest = load_json(MANIFEST)
        lexical_before, lexical_bytes_before = capture_complete_freeze_snapshot(
            MANIFEST, frozen_manifest
        )
    else:
        require_lexically_absent(
            [*map(Path, replicas), Path(canonical_output), Path(reproducibility_output)],
            "unit-test replica/output boundary",
        )
        frozen_manifest = None
        lexical_before = {}
        lexical_bytes_before = {}
    revalidate_complete_pin_snapshot(manifest_path, expected_manifest_sha256, pin_snapshot)
    return_codes: list[int] = []
    completed_replicas: list[Path] = []
    replica_ownership: dict[Path, tuple[int, int]] = {}
    launch_boundaries: list[dict[str, Any]] = []

    def require_launch_boundary() -> None:
        require_lexically_absent(
            promotion_stages,
            "promotion staging boundary at replica launch",
        )
        if real_freeze:
            require_exact_present_science_paths(completed_replicas)
        else:
            require_exact_present_paths(
                [
                    *map(Path, replicas),
                    Path(canonical_output),
                    Path(reproducibility_output),
                ],
                completed_replicas,
                "unit-test per-replica launch boundary",
            )

    try:
        for command, replica in zip(commands, replicas, strict=True):
            revalidate_complete_pin_snapshot(manifest_path, expected_manifest_sha256, pin_snapshot)
            require_launch_boundary()
            launch_boundaries.append(
                {
                    "replica_index": len(completed_replicas) + 1,
                    "allowed_present_science_paths": [
                        str(path.relative_to(REPORT)) if real_freeze else str(path)
                        for path in completed_replicas
                    ],
                    "promotion_staging_paths_absent": True,
                }
            )
            completed = subprocess.run(
                [str(value) for value in command],
                cwd=REPOSITORY,
                env=environment,
                check=False,
            )
            return_codes.append(int(completed.returncode))
            replica_path = Path(replica)
            if lexical_path_exists(replica_path):
                replica_ownership[replica_path] = regular_path_inode(replica_path)
            if completed.returncode not in (0, 2):
                raise RuntimeError(f"replica failed operationally: {completed.returncode}")
            revalidate_complete_pin_snapshot(manifest_path, expected_manifest_sha256, pin_snapshot)
            if not lexical_path_exists(replica_path):
                raise RuntimeError("replica did not write its declared output")
            _payload, replica_metadata = stable_regular_file_bytes(replica_path)
            if (
                int(replica_metadata["st_dev"]),
                int(replica_metadata["st_ino"]),
            ) != replica_ownership[replica_path]:
                raise RuntimeError("replica path no longer names its created inode")
            completed_replicas.append(replica_path)
            require_launch_boundary()
            if real_freeze:
                lexical_now, lexical_bytes_now = capture_complete_freeze_snapshot(
                    MANIFEST, frozen_manifest
                )
                require_same_freeze_snapshot(
                    lexical_before,
                    lexical_bytes_before,
                    lexical_now,
                    lexical_bytes_now,
                )
        require_launch_boundary()
        payloads = [stable_regular_file_bytes(Path(path))[0] for path in replicas]
        if payloads[0] != payloads[1]:
            raise RuntimeError("full discovery replicas are not byte-identical")
        result = parse_json_object_bytes(payloads[0], "replica result")
        validate_result_contract(result, expected_manifest_sha256, pin_snapshot)
        passed = result["all_discovery_gates_passed"]
        expected_status = PASS_STATUS if passed else HOLD_STATUS
        expected_code = 0 if passed else 2
        if result.get("status") != expected_status or return_codes != [
            expected_code,
            expected_code,
        ]:
            raise RuntimeError("replica exit/status contract is inconsistent")
        revalidate_complete_pin_snapshot(manifest_path, expected_manifest_sha256, pin_snapshot)
        if real_freeze:
            lexical_after, lexical_bytes_after = capture_complete_freeze_snapshot(
                MANIFEST, frozen_manifest
            )
            require_same_freeze_snapshot(
                lexical_before,
                lexical_bytes_before,
                lexical_after,
                lexical_bytes_after,
            )
        else:
            lexical_after = {}
        result_hash = sha256_bytes(payloads[0])
        evidence = {
            "schema_version": 1,
            "stage": "allocation_cusp_discovery_two_process_reproducibility",
            "manifest_sha256": expected_manifest_sha256,
            "independent_process_count": 2,
            "execution_order": "sequential",
            "five_path_absence_before_replicas": [
                str(path.relative_to(REPORT)) for path in scientific_output_paths()
            ],
            "promotion_staging_absence_before_replicas": [
                str(path.relative_to(REPORT)) if real_freeze else str(path)
                for path in promotion_stages
            ],
            "per_replica_launch_boundaries": launch_boundaries,
            "replica_exit_codes": return_codes,
            "replica_result_sha256": [result_hash, result_hash],
            "byte_identical": True,
            "canonical_result_sha256": result_hash,
            "result_status": expected_status,
            "all_discovery_gates_passed": passed,
            "pin_snapshot_before_replicas": pin_snapshot,
            "pin_snapshot_after_replicas": pin_snapshot,
            "lexical_snapshot_before_replicas": lexical_before,
            "lexical_snapshot_after_replicas": lexical_after,
        }

        def post_promotion_check() -> None:
            revalidate_complete_pin_snapshot(
                manifest_path,
                expected_manifest_sha256,
                pin_snapshot,
                allow_promoted_outputs=True,
            )
            if real_freeze:
                require_exact_present_science_paths(
                    [*map(Path, replicas), Path(canonical_output), Path(reproducibility_output)]
                )
                final_metadata, final_payloads = capture_complete_freeze_snapshot(
                    MANIFEST, frozen_manifest
                )
                require_same_freeze_snapshot(
                    lexical_before,
                    lexical_bytes_before,
                    final_metadata,
                    final_payloads,
                )

        promote_replica_bytes(
            payloads[0],
            canonical_json_bytes(evidence),
            canonical_output,
            reproducibility_output,
            post_promotion_check=post_promotion_check,
        )
        return result
    finally:
        for path, ownership in replica_ownership.items():
            unlink_owned_path(path, ownership)


def subprocess_environment(manifest: dict[str, Any]) -> dict[str, str]:
    environment = {
        key: os.environ[key] for key in SAFE_INHERITED_ENVIRONMENT_KEYS if key in os.environ
    }
    environment.update(manifest["reproducibility"]["subprocess_environment"])
    if any(key in environment for key in DANGEROUS_PYTHON_ENVIRONMENT_KEYS):
        raise RuntimeError("dangerous Python environment leaked into a formal replica")
    if any(key.startswith(DANGEROUS_NATIVE_ENVIRONMENT_PREFIXES) for key in environment):
        raise RuntimeError("native loader injection environment leaked into a formal replica")
    return environment


def require_isolated_formal_runtime() -> None:
    if sys.flags.isolated != 1 or sys.flags.no_site != 1 or not sys.dont_write_bytecode:
        raise RuntimeError("formal parent and replicas require Python -I -S -B")
    if sys.flags.ignore_environment != 1 or not sys.flags.safe_path:
        raise RuntimeError("formal runtime lacks the isolated safe-path flags")
    if sys.flags.hash_randomization != 1:
        raise RuntimeError("formal runtime must retain isolated Python hash randomization")
    if any(key in os.environ for key in DANGEROUS_PYTHON_ENVIRONMENT_KEYS):
        raise RuntimeError("formal replica inherited a Python injection environment")
    if any(key.startswith(DANGEROUS_NATIVE_ENVIRONMENT_PREFIXES) for key in os.environ):
        raise RuntimeError("formal runtime inherited a native loader injection environment")
    if "sitecustomize" in sys.modules or "usercustomize" in sys.modules:
        raise RuntimeError("formal replica loaded a customization module")
    require_repository_venv()


def execute_replica(output: Path, expected_manifest_sha256: str) -> dict[str, Any]:
    require_isolated_formal_runtime()
    output = Path(output)
    replicas = replica_paths()
    if output.resolve() not in {path.resolve() for path in replicas}:
        raise ValueError("replica may write only one of the two frozen hidden paths")
    if sha256(MANIFEST) != expected_manifest_sha256:
        raise ValueError("external manifest SHA-256 does not match")
    manifest = load_json(MANIFEST)
    allowed_before = [replicas[0]] if output.resolve() == replicas[1].resolve() else []
    require_loaded_native_phase(manifest, "runner_post_import")
    pinned_before = validate_manifest(manifest, allowed_present_science_paths=allowed_before)
    require_loaded_native_phase(manifest, "post_manifest_validation")
    lexical_before, lexical_bytes_before = capture_complete_freeze_snapshot(MANIFEST, manifest)
    with pinned_numpy_seed(int(REPRODUCIBILITY["numpy_global_seed"])):
        result = run_formal(
            manifest,
            expected_manifest_sha256,
            allowed_present_science_paths=allowed_before,
        )
    pinned_after = validate_manifest(
        manifest,
        require_outputs_absent=True,
        allowed_present_science_paths=allowed_before,
    )
    lexical_after, lexical_bytes_after = capture_complete_freeze_snapshot(MANIFEST, manifest)
    if pinned_after != pinned_before:
        raise RuntimeError("complete pinned-file snapshot changed during replica")
    require_same_freeze_snapshot(
        lexical_before, lexical_bytes_before, lexical_after, lexical_bytes_after
    )
    validate_result_contract(result, expected_manifest_sha256, pinned_before)
    output_ownership = fsync_write(output, canonical_json_bytes(result))
    try:
        require_exact_present_science_paths([*allowed_before, output])
        if validate_manifest(manifest, require_outputs_absent=False) != pinned_before:
            raise RuntimeError("complete pinned-file snapshot changed after replica write")
        final_metadata, final_payloads = capture_complete_freeze_snapshot(MANIFEST, manifest)
        require_same_freeze_snapshot(
            lexical_before,
            lexical_bytes_before,
            final_metadata,
            final_payloads,
        )
    except BaseException:
        unlink_owned_path(output, output_ownership)
        raise
    return result


def execute_frozen(expected_manifest_sha256: str) -> dict[str, Any]:
    require_isolated_formal_runtime()
    if sha256(MANIFEST) != expected_manifest_sha256:
        raise ValueError("external manifest SHA-256 does not match")
    manifest = load_json(MANIFEST)
    require_loaded_native_phase(manifest, "runner_post_import")
    pinned_hashes = validate_manifest(manifest)
    require_loaded_native_phase(manifest, "post_manifest_validation")
    replicas = replica_paths()
    commands = [
        isolated_runner_command(
            [
                "--execute-replica",
                "--expected-manifest-sha256",
                expected_manifest_sha256,
                "--output",
                str(replica),
            ]
        )
        for replica in replicas
    ]
    return run_replica_commands(
        commands,
        replicas,
        MANIFEST,
        expected_manifest_sha256,
        subprocess_environment(manifest),
        pinned_hashes=pinned_hashes,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--algebra-dry-run", action="store_true")
    mode.add_argument("--execute-frozen", action="store_true")
    mode.add_argument("--execute-replica", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--cells", type=int, default=7)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    arguments = parser.parse_args(argv)
    require_repository_venv()
    if sha256(MANIFEST) != arguments.expected_manifest_sha256:
        parser.error("external manifest SHA-256 does not match")
    manifest = load_json(MANIFEST)
    require_loaded_native_phase(manifest, "runner_post_import")
    if arguments.algebra_dry_run:
        if arguments.output.resolve() != OUTPUT.resolve():
            parser.error("dry-run output is stdout only")
        validate_manifest(manifest)
        require_isolated_formal_runtime()
        require_loaded_native_phase(manifest, "post_manifest_validation")
        result = run_algebra_dry_run(manifest, arguments.cells)
        print(canonical_json_bytes(result).decode(), end="")
    elif arguments.execute_replica:
        result = execute_replica(arguments.output, arguments.expected_manifest_sha256)
        print(result["status"])
    else:
        if arguments.output.resolve() != OUTPUT.resolve():
            parser.error("formal execution may promote only the canonical output")
        result = execute_frozen(arguments.expected_manifest_sha256)
        print(result["status"])
        print(OUTPUT)
    return (
        0
        if result.get("all_discovery_gates_passed", False)
        else (0 if arguments.algebra_dry_run and result["explicit_csr_preflight"]["passed"] else 2)
    )


if __name__ == "__main__":
    raise SystemExit(main())
