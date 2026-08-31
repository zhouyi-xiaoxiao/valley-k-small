#!/usr/bin/env python3
"""Deterministic positive-B killed-Doi confirmation for one fixed four-slab control."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import continuum_broad_patch_b0_bridge as bridge
import continuum_g1_smoke as smoke
import numpy as np
import scipy
from scipy.optimize import brentq
from scipy.sparse.linalg import LinearOperator, expm_multiply

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "positive_b_broad_four_slab_manifest.json"
OUTPUT = DATA / "positive_b_broad_four_slab_result.json"
REPRODUCIBILITY_OUTPUT = DATA / "positive_b_broad_four_slab_reproducibility.json"
TEST_FILE = HERE.with_name("test_positive_b_broad_four_slab.py")
PROTOCOL = REPORT / "notes" / "positive_b_broad_four_slab_protocol.md"

STAGE = "result_informed_positive_B_broad_four_slab_heldout_mesh_confirmation"
EVIDENCE_TIMING = "RESULT_INFORMED_FIXED_CONTROL_WITH_HELDOUT_FINE_MESHES"
CLAIM_SCOPE = (
    "One result-informed broad four-slab geometry with fixed absolute weights and fixed "
    "B=0.01, tested by a matrix-free killed-Doi finite-volume semigroup on two held-out "
    "odd cubic meshes in one fixed reflecting box."
)
FROZEN_PHYSICAL_PARAMETERS = {
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
FROZEN_KNOWN_BEFORE = {
    "B0_exact_and_mesh_bridge_result_known": True,
    "positive_B_mesh_65_budgets_evaluated": [0.01, 0.02, 0.04, 0.08],
    "positive_B_mesh_97_budgets_evaluated": [0.01, 0.02],
    "positive_B_mesh_113_evaluated": False,
    "positive_B_mesh_129_evaluated": False,
}
FROZEN_SELECTION_RECORD = {
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

FROZEN_WEIGHTS = [
    0.28,
    0.27736690132708747,
    0.0857172266153233,
    0.3569158720575891,
]
FROZEN_TIME_SCAN = {
    "start": 0.0,
    "stop": 35.0,
    "spacing": 0.02,
    "points": 1751,
    "chunk_points": 11,
    "minimum_root_time": 0.5,
    "saved_trace_spacing": 0.1,
}
FROZEN_ROOT_GATES = {
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
FROZEN_EVENT_MASS = {
    "final_time": 100.0,
    "minimum_each_basin_mass": 0.005,
    "maximum_mass_balance_error": 1.0e-9,
}
FROZEN_TAIL_GATES = {
    "checkpoints": [35.0, 50.0, 75.0, 100.0],
    "minimum_density_sampling_start": 0.5,
    "minimum_density": 0.0,
    "maximum_survival_increase": 1.0e-12,
    "maximum_negative_state_tolerance": 1.0e-12,
}
FROZEN_MESH_AGREEMENT = {
    "maximum_paired_root_time_difference": 0.1,
    "maximum_peak_ratio_difference": 0.03,
    "maximum_valley_ratio_difference": 0.03,
    "maximum_event_mass_difference": 0.01,
    "maximum_final_survival_difference": 0.02,
}
FROZEN_REPRODUCIBILITY = {
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
FROZEN_NEGATIVE_FLAGS = {
    "preregistered_discovery": False,
    "continuum_interval_verified": False,
    "unbounded_domain_FV_limit_verified": False,
    "independent_solver_verified": False,
    "project_gate_passed": False,
}
FROZEN_FINITE_VOLUME = {
    "midpoint_bounds": [-0.25, 1.85],
    "relative_parallel_bounds": [-1.8, 1.8],
    "scheme": "cell-centred Scharfetter-Gummel/periodic killed-Doi tensor generator",
}
FROZEN_PREFLIGHT = {
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
FROZEN_EXECUTION_BOUNDARY = {
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
FROZEN_FORBIDDEN_PROMOTIONS = [
    "preregistered discovery",
    "interval-certified root count",
    "unbounded-domain finite-volume convergence",
    "independent-solver confirmation",
    "physical d=3 confirmation",
    "project or publication gate pass",
]
FROZEN_PIN_PATHS = {
    "producer": "code/positive_b_broad_four_slab.py",
    "tests": "code/test_positive_b_broad_four_slab.py",
    "protocol": "notes/positive_b_broad_four_slab_protocol.md",
    "operational_erratum": "notes/positive_b_broad_four_slab_operational_erratum_v2.md",
    "B0_bridge_result": "artifacts/data/continuum_broad_patch_b0_bridge_result.json",
    "B0_bridge_manifest": "artifacts/data/continuum_broad_patch_b0_bridge_manifest.json",
    "B0_bridge_producer": "code/continuum_broad_patch_b0_bridge.py",
    "exact_continuum_dependency": "code/continuum_observable_four_patch.py",
    "finite_volume_dependency": "code/continuum_weak_budget_design.py",
    "grid_dependency": "code/continuum_g1_smoke.py",
    "feasibility_producer": "scratch/positive_b_broad_four_slab_feasibility.py",
    "feasibility_N65_all_budgets": ("scratch/positive_b_broad_four_slab_feasibility_result.json"),
    "feasibility_N97_B001": ("scratch/positive_b_broad_four_slab_feasibility_N97_B001.json"),
    "feasibility_N97_B002": ("scratch/positive_b_broad_four_slab_feasibility_N97_B002.json"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if type(value) is not dict:
        raise ValueError(f"{path} must contain one JSON object")
    return value


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
                raise TypeError(f"non-string JSON object key at {location}")
            require_finite_json(item, f"{location}.{key}")
        return
    raise TypeError(f"unsupported JSON value {type(value).__name__} at {location}")


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    require_finite_json(payload)
    return (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_bytes(canonical_json_bytes(payload))


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


def native_json_boolean_gates(gates: dict[str, Any]) -> dict[str, bool]:
    """Convert only Boolean scalar gates to native JSON-compatible booleans."""
    normalized: dict[str, bool] = {}
    for key, value in gates.items():
        if type(key) is not str:
            raise TypeError("gate names must be strings")
        if type(value) is bool:
            normalized[key] = value
        elif type(value) is np.bool_:
            normalized[key] = bool(value)
        else:
            raise TypeError(f"gate {key} must be a Boolean scalar")
    return normalized


def require_repository_venv() -> None:
    if Path(sys.prefix).resolve() != (REPOSITORY / ".venv").resolve():
        raise RuntimeError("positive-B confirmation must run inside the repository .venv")


@contextmanager
def pinned_numpy_global_seed(seed: int) -> Iterator[None]:
    if type(seed) is not int or seed < 0 or seed > 2**32 - 1:
        raise ValueError("seed must be a uint32-compatible integer")
    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)


class KilledColumnOperator(LinearOperator):
    """Matrix-free column generator Q_B^T on the midpoint-relative tensor."""

    def __init__(
        self,
        midpoint_generator: Any,
        relative_generator: Any,
        killing_per_budget: np.ndarray,
        budget: float,
    ) -> None:
        self.midpoint_generator = midpoint_generator.tocsr()
        self.relative_generator = relative_generator.tocsr()
        self.midpoint_cells = self.midpoint_generator.shape[0]
        self.relative_states = self.relative_generator.shape[0]
        self.killing_per_budget = np.asarray(killing_per_budget, dtype=float)
        self.budget = float(budget)
        expected = self.midpoint_cells * self.relative_states
        if self.killing_per_budget.shape != (expected,):
            raise ValueError("killing field does not match tensor dimensions")
        self.killing_matrix = self.killing_per_budget.reshape(
            self.midpoint_cells, self.relative_states
        )
        self.trace_value = float(
            self.relative_states * np.sum(self.midpoint_generator.diagonal())
            + self.midpoint_cells * np.sum(self.relative_generator.diagonal())
            - self.budget * np.sum(self.killing_per_budget)
        )
        super().__init__(dtype=np.dtype(np.float64), shape=(expected, expected))

    def _column_action(self, vector: np.ndarray) -> np.ndarray:
        shaped = np.asarray(vector, dtype=float).reshape(self.midpoint_cells, self.relative_states)
        output = self.midpoint_generator.T @ shaped
        output += (self.relative_generator.T @ shaped.T).T
        output -= self.budget * self.killing_matrix * shaped
        return np.asarray(output, dtype=float).reshape(-1)

    def _row_action(self, vector: np.ndarray) -> np.ndarray:
        shaped = np.asarray(vector, dtype=float).reshape(self.midpoint_cells, self.relative_states)
        output = self.midpoint_generator @ shaped
        output += (self.relative_generator @ shaped.T).T
        output -= self.budget * self.killing_matrix * shaped
        return np.asarray(output, dtype=float).reshape(-1)

    def _matvec(self, vector: np.ndarray) -> np.ndarray:
        return self._column_action(vector)

    def _rmatvec(self, vector: np.ndarray) -> np.ndarray:
        return self._row_action(vector)

    def _matmat(self, matrix: np.ndarray) -> np.ndarray:
        values = np.asarray(matrix, dtype=float)
        return np.column_stack(
            [self._column_action(values[:, index]) for index in range(values.shape[1])]
        )

    def _rmatmat(self, matrix: np.ndarray) -> np.ndarray:
        values = np.asarray(matrix, dtype=float)
        return np.column_stack(
            [self._row_action(values[:, index]) for index in range(values.shape[1])]
        )


class BudgetTangentColumnOperator(LinearOperator):
    """Column generator for (p, partial_B p) at the fixed budget."""

    def __init__(self, base: KilledColumnOperator) -> None:
        self.base = base
        self.base_states = base.shape[0]
        self.trace_value = 2.0 * base.trace_value
        super().__init__(
            dtype=np.dtype(np.float64),
            shape=(2 * self.base_states, 2 * self.base_states),
        )

    def _matvec(self, vector: np.ndarray) -> np.ndarray:
        values = np.asarray(vector, dtype=float)
        p = values[: self.base_states]
        tangent = values[self.base_states :]
        return np.concatenate(
            (
                self.base.matvec(p),
                self.base.matvec(tangent) - self.base.killing_per_budget * p,
            )
        )

    def _rmatvec(self, vector: np.ndarray) -> np.ndarray:
        values = np.asarray(vector, dtype=float)
        left = values[: self.base_states]
        right = values[self.base_states :]
        return np.concatenate(
            (
                self.base.rmatvec(left) - self.base.killing_per_budget * right,
                self.base.rmatvec(right),
            )
        )

    def _matmat(self, matrix: np.ndarray) -> np.ndarray:
        values = np.asarray(matrix, dtype=float)
        return np.column_stack([self._matvec(values[:, index]) for index in range(values.shape[1])])

    def _rmatmat(self, matrix: np.ndarray) -> np.ndarray:
        values = np.asarray(matrix, dtype=float)
        return np.column_stack(
            [self._rmatvec(values[:, index]) for index in range(values.shape[1])]
        )


@dataclass(frozen=True)
class TensorKilledModel:
    cells: int
    budget: float
    weights: np.ndarray
    factors: bridge.FVFactors
    operator: KilledColumnOperator
    initial: np.ndarray
    killing_per_budget: np.ndarray
    q0: np.ndarray
    q1: np.ndarray
    q2: np.ndarray
    q3: np.ndarray
    qones: np.ndarray
    boundary_mask: np.ndarray
    diagnostics: dict[str, Any]


def build_model(cells: int, manifest: dict[str, Any]) -> TensorKilledModel:
    parameters = bridge.parameters_from_manifest(manifest)
    budget = float(manifest["positive_budget"])
    weights = np.asarray(manifest["fixed_absolute_weights"], dtype=float)
    if weights.shape != (4,) or abs(float(np.sum(weights)) - 1.0) > 2.0e-14:
        raise ValueError("four fixed unit-sum weights are required")
    factors = bridge.build_fv_factors(cells, parameters, manifest)
    kappa_per_budget = weights @ factors.patch_profiles / parameters.transverse_width
    killing_per_budget = np.kron(kappa_per_budget, factors.contact_profile)
    operator = KilledColumnOperator(
        factors.midpoint_generator,
        factors.relative_generator,
        killing_per_budget,
        budget,
    )
    initial = np.kron(factors.midpoint_initial, factors.relative_initial)
    q0 = killing_per_budget
    q1 = np.asarray(operator.rmatvec(q0), dtype=float)
    q2 = np.asarray(operator.rmatvec(q1), dtype=float)
    q3 = np.asarray(operator.rmatvec(q2), dtype=float)
    qones = np.asarray(operator.rmatvec(np.ones_like(initial)), dtype=float)
    boundary_mask = smoke.boundary_layer_union_mask(cells, cells, cells, layers=2).reshape(-1)
    physical_budget = float(
        parameters.transverse_width
        * np.sum(budget * kappa_per_budget)
        * factors.grid.midpoint_spacing
    )
    diagnostics = {
        "mesh": [cells, cells, cells],
        "state_count": int(initial.size),
        "matrix_free_full_generator": True,
        "midpoint_generator_nnz": int(factors.midpoint_generator.nnz),
        "relative_generator_nnz": int(factors.relative_generator.nnz),
        "analytic_column_operator_trace": operator.trace_value,
        "initial_mass_error": float(abs(np.sum(initial) - 1.0)),
        "physical_budget": physical_budget,
        "physical_budget_absolute_error": abs(physical_budget - budget),
        "minimum_weight": float(np.min(weights)),
        "weight_sum_error": float(abs(np.sum(weights) - 1.0)),
        "minimum_killing_per_budget": float(np.min(killing_per_budget)),
        "maximum_killing_per_budget": float(np.max(killing_per_budget)),
        "killed_mass_balance_operator_error": float(
            np.max(np.abs(qones + budget * killing_per_budget))
        ),
        "factor_diagnostics": factors.diagnostics,
    }
    return TensorKilledModel(
        cells=cells,
        budget=budget,
        weights=weights,
        factors=factors,
        operator=operator,
        initial=initial,
        killing_per_budget=killing_per_budget,
        q0=q0,
        q1=q1,
        q2=q2,
        q3=q3,
        qones=qones,
        boundary_mask=boundary_mask,
        diagnostics=diagnostics,
    )


def propagate(
    operator: LinearOperator,
    state: np.ndarray,
    delta: float,
    trace_value: float,
) -> np.ndarray:
    value = float(delta)
    if value < 0.0 or not np.isfinite(value):
        raise ValueError("propagation increment must be finite and nonnegative")
    if value == 0.0:
        return np.asarray(state, dtype=float).copy()
    return np.asarray(
        expm_multiply(
            value * operator,
            state,
            traceA=value * trace_value,
        ),
        dtype=float,
    )


def project_state(model: TensorKilledModel, state: np.ndarray) -> np.ndarray:
    value = np.asarray(state, dtype=float)
    budget = model.budget
    return np.asarray(
        (
            budget * (value @ model.q0),
            budget * (value @ model.q1),
            budget * (value @ model.q2),
            budget * (value @ model.q3),
            np.sum(value),
            np.sum(value[model.boundary_mask]),
            value @ model.qones,
        ),
        dtype=float,
    )


def project_states(model: TensorKilledModel, states: np.ndarray) -> np.ndarray:
    values = np.asarray(states, dtype=float)
    budget = model.budget
    return np.column_stack(
        (
            budget * (values @ model.q0),
            budget * (values @ model.q1),
            budget * (values @ model.q2),
            budget * (values @ model.q3),
            np.sum(values, axis=1),
            np.sum(values[:, model.boundary_mask], axis=1),
            values @ model.qones,
        )
    )


def stream_scan(
    model: TensorKilledModel,
    manifest: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], np.ndarray]:
    rules = manifest["time_scan"]
    start = float(rules["start"])
    stop = float(rules["stop"])
    spacing = float(rules["spacing"])
    points = int(rules["points"])
    chunk_points = int(rules["chunk_points"])
    minimum_root_time = float(rules["minimum_root_time"])
    positive_derivative_time = float(manifest["root_gates"]["positive_derivative_time"])
    minimum_density_sampling_start = float(manifest["tail_gates"]["minimum_density_sampling_start"])
    if start != 0.0 or points != int(round((stop - start) / spacing)) + 1:
        raise ValueError("time scan is inconsistent")
    trace_stride = int(round(float(rules["saved_trace_spacing"]) / spacing))
    if trace_stride < 1:
        raise ValueError("saved trace spacing is too small")

    state = model.initial.copy()
    previous_time = 0.0
    previous_state = state.copy()
    previous_projection = project_state(model, state)
    sampled_peak = float(previous_projection[0])
    minimum_sampled_density = math.inf
    maximum_survival_increase = -math.inf
    minimum_state = float(np.min(state))
    maximum_boundary_fraction = float(previous_projection[5] / previous_projection[4])
    maximum_mass_balance_residual = float(abs(previous_projection[6] + previous_projection[0]))
    positive_endpoint_projection: np.ndarray | None = None
    brackets: list[dict[str, Any]] = []
    saved_trace = []

    def save(index: int, time_value: float, projection: np.ndarray) -> None:
        if index % trace_stride == 0 or index == points - 1:
            saved_trace.append(
                {
                    "time": time_value,
                    "f": float(projection[0]),
                    "f_t": float(projection[1]),
                    "f_tt": float(projection[2]),
                    "f_ttt": float(projection[3]),
                    "survival": float(projection[4]),
                    "boundary_layer_fraction": float(projection[5] / projection[4]),
                    "differential_mass_balance_residual": float(abs(projection[6] + projection[0])),
                }
            )

    save(0, 0.0, previous_projection)
    cursor = 0
    while cursor < points - 1:
        end = min(cursor + chunk_points - 1, points - 1)
        rows = end - cursor + 1
        span = spacing * (rows - 1)
        states = np.asarray(
            expm_multiply(
                model.operator,
                state,
                start=0.0,
                stop=span,
                num=rows,
                endpoint=True,
                traceA=model.operator.trace_value,
            ),
            dtype=float,
        )
        projections = project_states(model, states)
        minimum_state = min(minimum_state, float(np.min(states)))
        for local_index in range(1, rows):
            global_index = cursor + local_index
            time_value = start + spacing * global_index
            projection = projections[local_index]
            sampled_peak = max(sampled_peak, float(projection[0]))
            if time_value >= minimum_density_sampling_start:
                minimum_sampled_density = min(
                    minimum_sampled_density,
                    float(projection[0]),
                )
            maximum_survival_increase = max(
                maximum_survival_increase,
                float(projection[4] - previous_projection[4]),
            )
            maximum_boundary_fraction = max(
                maximum_boundary_fraction,
                float(projection[5] / projection[4]),
            )
            maximum_mass_balance_residual = max(
                maximum_mass_balance_residual,
                float(abs(projection[6] + projection[0])),
            )
            if abs(time_value - positive_derivative_time) <= 0.25 * spacing:
                positive_endpoint_projection = projection.copy()
            if previous_time >= minimum_root_time and previous_projection[1] * projection[1] < 0.0:
                brackets.append(
                    {
                        "left_time": previous_time,
                        "right_time": time_value,
                        "left_first_derivative": float(previous_projection[1]),
                        "right_first_derivative": float(projection[1]),
                        "left_state": previous_state.copy(),
                    }
                )
            save(global_index, time_value, projection)
            previous_time = time_value
            previous_state = states[local_index].copy()
            previous_projection = projection.copy()
        state = states[-1].copy()
        cursor = end

    if positive_endpoint_projection is None:
        raise RuntimeError("positive derivative checkpoint was absent from the frozen time grid")
    if not math.isfinite(minimum_sampled_density):
        raise RuntimeError("density sampling interval was absent from the frozen time grid")

    payload = {
        "time_grid": {
            "start": start,
            "stop": stop,
            "spacing": spacing,
            "points": points,
            "chunk_points": chunk_points,
        },
        "sampled_peak_density": sampled_peak,
        "minimum_sampled_density_from_frozen_start": minimum_sampled_density,
        "minimum_density_sampling_start": minimum_density_sampling_start,
        "strict_sign_change_bracket_count": len(brackets),
        "maximum_sampled_survival_increase": maximum_survival_increase,
        "minimum_streamed_state_component": minimum_state,
        "maximum_boundary_layer_fraction": maximum_boundary_fraction,
        "maximum_sampled_differential_mass_balance_residual": maximum_mass_balance_residual,
        "positive_derivative_checkpoint": {
            "time": positive_derivative_time,
            "f_t": float(positive_endpoint_projection[1]),
        },
        "derivative_at_scan_stop": float(previous_projection[1]),
        "survival_at_scan_stop": float(previous_projection[4]),
        "saved_trace": saved_trace,
    }
    return payload, brackets, state


def refine_roots(
    model: TensorKilledModel,
    brackets: list[dict[str, Any]],
    sampled_peak: float,
    manifest: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[np.ndarray]]:
    rules = manifest["root_gates"]
    density_floor = float(rules["relative_density_floor"]) * sampled_peak
    roots = []
    root_states = []
    for bracket in brackets:
        left = float(bracket["left_time"])
        right = float(bracket["right_time"])
        left_state = np.asarray(bracket["left_state"], dtype=float)

        def first_derivative(time_value: float) -> float:
            state = propagate(
                model.operator,
                left_state,
                time_value - left,
                model.operator.trace_value,
            )
            return float(model.budget * (state @ model.q1))

        root = float(brentq(first_derivative, left, right, xtol=3.0e-12, rtol=1.0e-13))
        state = propagate(
            model.operator,
            left_state,
            root - left,
            model.operator.trace_value,
        )
        values = project_state(model, state)
        if values[0] < density_floor:
            continue
        roots.append(
            {
                "time": root,
                "topology": "maximum" if values[2] < 0.0 else "minimum",
                "density": float(values[0]),
                "f_t": float(values[1]),
                "f_tt": float(values[2]),
                "f_ttt": float(values[3]),
                "survival": float(values[4]),
                "boundary_layer_fraction": float(values[5] / values[4]),
                "scaled_first_derivative_residual": float(abs(root * values[1] / values[0])),
                "scaled_second_derivative": float(root**2 * values[2] / values[0]),
                "differential_mass_balance_residual": float(abs(values[6] + values[0])),
                "minimum_state_component": float(np.min(state)),
            }
        )
        root_states.append(state)
    return roots, root_states


def budget_control_jets(
    model: TensorKilledModel,
    roots: list[dict[str, Any]],
    direct_states: list[np.ndarray],
) -> dict[str, Any]:
    tangent_operator = BudgetTangentColumnOperator(model.operator)
    total_states = model.initial.size
    augmented = np.concatenate((model.initial, np.zeros_like(model.initial)))
    previous_time = 0.0
    rows = []
    maximum_state_difference = 0.0
    maximum_time_jet_difference = 0.0
    qb_q0 = -model.killing_per_budget * model.q0
    derivative_q2 = -model.killing_per_budget * model.q1 + model.operator.rmatvec(qb_q0)
    for root, direct_state in zip(roots, direct_states, strict=True):
        time_value = float(root["time"])
        augmented = propagate(
            tangent_operator,
            augmented,
            time_value - previous_time,
            tangent_operator.trace_value,
        )
        p = augmented[:total_states]
        tangent = augmented[total_states:]
        relative_state_difference = float(
            np.sum(np.abs(p - direct_state))
            / max(np.sum(np.abs(direct_state)), np.finfo(float).tiny)
        )
        maximum_state_difference = max(maximum_state_difference, relative_state_difference)
        time_jets = np.asarray(
            (
                model.budget * (p @ model.q0),
                model.budget * (p @ model.q1),
                model.budget * (p @ model.q2),
                model.budget * (p @ model.q3),
            )
        )
        direct_time_jets = np.asarray((root["density"], root["f_t"], root["f_tt"], root["f_ttt"]))
        time_jet_difference = float(np.max(np.abs(time_jets - direct_time_jets)))
        maximum_time_jet_difference = max(maximum_time_jet_difference, time_jet_difference)
        control_jets = {
            "f_B": float(p @ model.q0 + model.budget * (tangent @ model.q0)),
            "f_tB": float(
                p @ (model.q1 + model.budget * qb_q0) + tangent @ (model.budget * model.q1)
            ),
            "f_ttB": float(
                p @ (model.q2 + model.budget * derivative_q2) + tangent @ (model.budget * model.q2)
            ),
            "survival_B": float(np.sum(tangent)),
        }
        rows.append(
            {
                "time": time_value,
                "time_jets_f_f_t_f_tt_f_ttt": time_jets.tolist(),
                "budget_control_jets": control_jets,
                "direct_vs_tangent_state_relative_l1": relative_state_difference,
                "maximum_direct_vs_tangent_time_jet_absolute_difference": time_jet_difference,
            }
        )
        previous_time = time_value
    return {
        "control_variable": "full installed budget B",
        "analytic_augmented_operator_trace": tangent_operator.trace_value,
        "rows": rows,
        "maximum_direct_vs_tangent_state_relative_l1": maximum_state_difference,
        "maximum_direct_vs_tangent_time_jet_absolute_difference": maximum_time_jet_difference,
    }


def propagate_tail(
    model: TensorKilledModel,
    scan_end_state: np.ndarray,
    scan: dict[str, Any],
    manifest: dict[str, Any],
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    checkpoints = [float(value) for value in manifest["tail_gates"]["checkpoints"]]
    if checkpoints[0] != float(scan["time_grid"]["stop"]):
        raise ValueError("first tail checkpoint must equal the scan stop")
    if checkpoints[-1] != float(manifest["event_mass"]["final_time"]):
        raise ValueError("last tail checkpoint must equal the event-mass final time")
    if any(right <= left for left, right in zip(checkpoints[:-1], checkpoints[1:], strict=True)):
        raise ValueError("tail checkpoints must be strictly increasing")

    state = np.asarray(scan_end_state, dtype=float).copy()
    projection = project_state(model, state)
    previous_survival = float(projection[4])
    maximum_survival_increase = -math.inf
    minimum_density = float(projection[0])
    minimum_state = float(np.min(state))
    maximum_mass_balance_residual = float(abs(projection[6] + projection[0]))
    trace = [
        {
            "time": checkpoints[0],
            "density": float(projection[0]),
            "survival": previous_survival,
            "minimum_state_component": float(np.min(state)),
            "differential_mass_balance_residual": float(abs(projection[6] + projection[0])),
        }
    ]
    previous_time = checkpoints[0]
    for time_value in checkpoints[1:]:
        state = propagate(
            model.operator,
            state,
            time_value - previous_time,
            model.operator.trace_value,
        )
        projection = project_state(model, state)
        survival = float(projection[4])
        maximum_survival_increase = max(
            maximum_survival_increase,
            survival - previous_survival,
        )
        minimum_density = min(minimum_density, float(projection[0]))
        minimum_state = min(minimum_state, float(np.min(state)))
        maximum_mass_balance_residual = max(
            maximum_mass_balance_residual,
            float(abs(projection[6] + projection[0])),
        )
        trace.append(
            {
                "time": time_value,
                "density": float(projection[0]),
                "survival": survival,
                "minimum_state_component": float(np.min(state)),
                "differential_mass_balance_residual": float(abs(projection[6] + projection[0])),
            }
        )
        previous_time = time_value
        previous_survival = survival

    payload = {
        "checkpoints": checkpoints,
        "trace": trace,
        "survival_at_scan_stop": float(trace[0]["survival"]),
        "final_survival": float(projection[4]),
        "survival_decrease_from_scan_stop": float(trace[0]["survival"] - projection[4]),
        "maximum_checkpoint_survival_increase": maximum_survival_increase,
        "minimum_checkpoint_density": minimum_density,
        "minimum_tail_state_component": minimum_state,
        "minimum_final_state_component": float(np.min(state)),
        "maximum_checkpoint_differential_mass_balance_residual": (maximum_mass_balance_residual),
    }
    return payload, state, projection


def tail_gate_results(tail: dict[str, Any], manifest: dict[str, Any]) -> dict[str, bool]:
    rules = manifest["tail_gates"]
    return native_json_boolean_gates(
        {
            "tail_checkpoint_density_positive": tail["minimum_checkpoint_density"]
            > float(rules["minimum_density"]),
            "tail_checkpoint_survival_nonincreasing": tail["maximum_checkpoint_survival_increase"]
            <= float(rules["maximum_survival_increase"]),
            "tail_state_positivity_tolerance": tail["minimum_tail_state_component"]
            >= -float(rules["maximum_negative_state_tolerance"]),
        }
    )


def solve_mesh(cells: int, manifest: dict[str, Any]) -> dict[str, Any]:
    model = build_model(cells, manifest)
    scan, brackets, scan_end_state = stream_scan(model, manifest)
    roots, root_states = refine_roots(
        model,
        brackets,
        float(scan["sampled_peak_density"]),
        manifest,
    )
    final_time = float(manifest["event_mass"]["final_time"])
    tail, final_state, final_projection = propagate_tail(
        model,
        scan_end_state,
        scan,
        manifest,
    )
    control = budget_control_jets(model, roots, root_states)
    expected_topology = ["maximum", "minimum", "maximum", "minimum", "maximum"]
    topology = [row["topology"] for row in roots]
    maxima = [row for row in roots if row["topology"] == "maximum"]
    peak_ratio: float | None = None
    valley_ratios: list[float] | None = None
    event_masses: list[float] | None = None
    if topology == expected_topology:
        peak_ratio = float(
            min(row["density"] for row in maxima) / max(row["density"] for row in maxima)
        )
        valley_ratios = []
        for index in (1, 3):
            valley_ratios.append(
                float(
                    roots[index]["density"]
                    / min(roots[index - 1]["density"], roots[index + 1]["density"])
                )
            )
        first_survival = roots[1]["survival"]
        second_survival = roots[3]["survival"]
        event_masses = [
            float(1.0 - first_survival),
            float(first_survival - second_survival),
            float(second_survival - final_projection[4]),
        ]
    thresholds = manifest["root_gates"]
    event_rules = manifest["event_mass"]
    tail_gates = tail_gate_results(tail, manifest)
    gates = {
        "initial_mass": model.diagnostics["initial_mass_error"] <= 1.0e-12,
        "physical_budget": model.diagnostics["physical_budget_absolute_error"] <= 1.0e-12,
        "weights_positive_unit_sum": model.diagnostics["minimum_weight"] > 0.0
        and model.diagnostics["weight_sum_error"] <= 2.0e-14,
        "five_alternating_simple_roots": topology == expected_topology,
        "peak_ratio": peak_ratio is not None
        and peak_ratio >= float(thresholds["minimum_peak_ratio"]),
        "valley_ratios": valley_ratios is not None
        and len(valley_ratios) == 2
        and max(valley_ratios) <= float(thresholds["maximum_valley_ratio"]),
        "root_residuals": bool(roots)
        and all(
            row["scaled_first_derivative_residual"]
            <= float(thresholds["maximum_scaled_root_residual"])
            for row in roots
        ),
        "curvature_margins": bool(roots)
        and all(
            abs(row["scaled_second_derivative"])
            >= float(thresholds["minimum_absolute_scaled_curvature"])
            for row in roots
        ),
        "endpoint_derivative_signs": scan["positive_derivative_checkpoint"]["f_t"] > 0.0
        and scan["derivative_at_scan_stop"] < 0.0
        and scan["positive_derivative_checkpoint"]["time"]
        == float(thresholds["positive_derivative_time"])
        and scan["time_grid"]["stop"] == float(thresholds["negative_derivative_time"]),
        "sampled_density_positive": scan["minimum_sampled_density_from_frozen_start"]
        > float(manifest["tail_gates"]["minimum_density"])
        and tail_gates["tail_checkpoint_density_positive"],
        "root_density_positive": bool(roots) and min(row["density"] for row in roots) > 0.0,
        "survival_positive": scan["survival_at_scan_stop"] > 0.0 and final_projection[4] > 0.0,
        "state_positivity_tolerance": min(
            scan["minimum_streamed_state_component"],
            float(np.min(final_state)),
            *(row["minimum_state_component"] for row in roots),
        )
        >= -float(thresholds["maximum_negative_state_tolerance"]),
        "survival_monotone_through_final_time": scan["maximum_sampled_survival_increase"]
        <= float(thresholds["maximum_survival_increase"])
        and tail_gates["tail_checkpoint_survival_nonincreasing"],
        "tail_final_state_positivity": tail_gates["tail_state_positivity_tolerance"],
        "generator_Q_one_equals_minus_B_k0": model.diagnostics["killed_mass_balance_operator_error"]
        <= float(event_rules["maximum_mass_balance_error"]),
        "mass_balance_on_saved_scan": scan["maximum_sampled_differential_mass_balance_residual"]
        <= float(event_rules["maximum_mass_balance_error"]),
        "mass_balance_at_roots": bool(roots)
        and max(row["differential_mass_balance_residual"] for row in roots)
        <= float(event_rules["maximum_mass_balance_error"]),
        "mass_balance_at_final_time": abs(final_projection[6] + final_projection[0])
        <= float(event_rules["maximum_mass_balance_error"]),
        "mass_balance_on_tail_checkpoints": tail[
            "maximum_checkpoint_differential_mass_balance_residual"
        ]
        <= float(event_rules["maximum_mass_balance_error"]),
        "event_basin_masses": event_masses is not None
        and len(event_masses) == 3
        and min(event_masses) >= float(event_rules["minimum_each_basin_mass"]),
        "event_mass_partition_closure": event_masses is not None
        and len(event_masses) == 3
        and abs(sum(event_masses) - (1.0 - final_projection[4]))
        <= float(event_rules["maximum_mass_balance_error"]),
        "tangent_state_reproduction": len(control["rows"]) == 5
        and control["maximum_direct_vs_tangent_state_relative_l1"]
        <= float(thresholds["maximum_tangent_state_relative_l1"]),
        "tangent_time_jet_reproduction": len(control["rows"]) == 5
        and control["maximum_direct_vs_tangent_time_jet_absolute_difference"]
        <= float(thresholds["maximum_tangent_time_jet_absolute_difference"]),
    }
    gates = native_json_boolean_gates(gates)
    return {
        "mesh": [cells, cells, cells],
        "diagnostics": model.diagnostics,
        "scan": scan,
        "stationary_structure": {
            "stationary_root_count": len(roots),
            "topology": topology,
            "roots": roots,
            "peak_minimum_to_maximum_ratio": peak_ratio,
            "valley_to_smaller_adjacent_peak_ratios": valley_ratios,
        },
        "survival_and_event_mass": {
            "final_time": final_time,
            "final_survival": float(final_projection[4]),
            "total_reaction_mass_to_final_time": float(1.0 - final_projection[4]),
            "basin_reaction_masses": event_masses,
            "basin_mass_sum": (float(sum(event_masses)) if event_masses is not None else None),
            "basin_mass_sum_vs_total_reaction_difference": (
                float(abs(sum(event_masses) - (1.0 - final_projection[4])))
                if event_masses is not None
                else None
            ),
            "final_differential_mass_balance_residual": float(
                abs(final_projection[6] + final_projection[0])
            ),
        },
        "tail_35_to_100": tail,
        "time_and_budget_control_jets": control,
        "gates": gates,
        "all_mesh_gates_passed": bool(all(gates.values())),
    }


def validate_manifest(manifest: dict[str, Any]) -> dict[str, str]:
    expected_contract = {
        "schema_version": 1,
        "stage": STAGE,
        "evidence_timing": EVIDENCE_TIMING,
        "freeze_date": "2026-07-13",
        "claim_scope": CLAIM_SCOPE,
        "known_before_freeze": FROZEN_KNOWN_BEFORE,
        "selection_record": FROZEN_SELECTION_RECORD,
        "physical_parameters": FROZEN_PHYSICAL_PARAMETERS,
        "fixed_absolute_weights": FROZEN_WEIGHTS,
        "positive_budget": 0.01,
        "heldout_meshes": [113, 129],
        "finite_volume": FROZEN_FINITE_VOLUME,
        "time_scan": FROZEN_TIME_SCAN,
        "root_gates": FROZEN_ROOT_GATES,
        "event_mass": FROZEN_EVENT_MASS,
        "tail_gates": FROZEN_TAIL_GATES,
        "mesh_agreement": FROZEN_MESH_AGREEMENT,
        "preflight_validation": FROZEN_PREFLIGHT,
        "numerical_reproducibility": FROZEN_REPRODUCIBILITY,
        "execution_boundary": FROZEN_EXECUTION_BOUNDARY,
        "required_claim_flags": FROZEN_NEGATIVE_FLAGS,
        "forbidden_promotions": FROZEN_FORBIDDEN_PROMOTIONS,
    }
    expected_top_level = set(expected_contract) | {"pinned_files"}
    if type(manifest) is not dict or set(manifest) != expected_top_level:
        raise ValueError("manifest top-level contract changed")
    for key, expected in expected_contract.items():
        if not exact_json_contract(manifest[key], expected):
            raise ValueError(f"manifest {key} contract changed")

    pins = manifest["pinned_files"]
    if type(pins) is not dict or set(pins) != set(FROZEN_PIN_PATHS):
        raise ValueError("pinned-file role set changed")
    raw_paths = [item.get("path") for item in pins.values() if type(item) is dict]
    if len(raw_paths) != len(set(raw_paths)):
        raise ValueError("duplicate pinned-file paths are forbidden")

    report_root = REPORT.resolve(strict=True)
    observed = {}
    for label, expected_relative in FROZEN_PIN_PATHS.items():
        item = pins[label]
        if type(item) is not dict or set(item) != {"path", "sha256"}:
            raise ValueError(f"pinned {label} record shape changed")
        if type(item["path"]) is not str or item["path"] != expected_relative:
            raise ValueError(f"pinned {label} path changed")
        raw_path = Path(item["path"])
        if raw_path.is_absolute() or ".." in raw_path.parts:
            raise ValueError(f"pinned {label} path is not report-relative")
        resolved = (REPORT / raw_path).resolve(strict=True)
        try:
            resolved.relative_to(report_root)
        except ValueError as error:
            raise ValueError(f"pinned {label} escapes the report root") from error
        if not resolved.is_file():
            raise ValueError(f"pinned {label} is not a regular file")
        expected_hash = item["sha256"]
        if (
            type(expected_hash) is not str
            or len(expected_hash) != 64
            or any(character not in "0123456789abcdef" for character in expected_hash)
        ):
            raise ValueError(f"pinned {label} SHA-256 is malformed")
        observed[label] = sha256(resolved)
        if observed[label] != expected_hash:
            raise ValueError(f"pinned {label} hash mismatch")
    return observed


def mesh_agreement(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    if len(rows) != 2:
        raise ValueError("exactly two held-out mesh rows are required")
    left, right = rows
    left_structure = left["stationary_structure"]
    right_structure = right["stationary_structure"]
    left_roots = left_structure["roots"]
    right_roots = right_structure["roots"]
    expected_topology = ["maximum", "minimum", "maximum", "minimum", "maximum"]
    comparable_topology = (
        left_structure.get("topology") == expected_topology
        and right_structure.get("topology") == expected_topology
        and len(left_roots) == len(right_roots) == 5
    )

    def finite_float(value: Any) -> float | None:
        if type(value) not in (int, float) or type(value) is bool:
            return None
        result = float(value)
        return result if math.isfinite(result) else None

    root_difference: float | None = None
    if comparable_topology:
        paired_root_differences = [
            abs(float(a["time"]) - float(b["time"]))
            for a, b in zip(left_roots, right_roots, strict=True)
            if finite_float(a.get("time")) is not None and finite_float(b.get("time")) is not None
        ]
        if len(paired_root_differences) == 5:
            root_difference = max(paired_root_differences)

    left_valleys = left_structure.get("valley_to_smaller_adjacent_peak_ratios")
    right_valleys = right_structure.get("valley_to_smaller_adjacent_peak_ratios")
    valley_difference: float | None = None
    if (
        comparable_topology
        and type(left_valleys) is list
        and type(right_valleys) is list
        and len(left_valleys) == len(right_valleys) == 2
        and all(finite_float(value) is not None for value in left_valleys + right_valleys)
    ):
        valley_difference = max(
            abs(float(a) - float(b)) for a, b in zip(left_valleys, right_valleys, strict=True)
        )

    left_masses = left["survival_and_event_mass"].get("basin_reaction_masses")
    right_masses = right["survival_and_event_mass"].get("basin_reaction_masses")
    mass_difference: float | None = None
    if (
        comparable_topology
        and type(left_masses) is list
        and type(right_masses) is list
        and len(left_masses) == len(right_masses) == 3
        and all(finite_float(value) is not None for value in left_masses + right_masses)
    ):
        mass_difference = max(
            abs(float(a) - float(b)) for a, b in zip(left_masses, right_masses, strict=True)
        )

    left_peak = finite_float(left_structure.get("peak_minimum_to_maximum_ratio"))
    right_peak = finite_float(right_structure.get("peak_minimum_to_maximum_ratio"))
    peak_difference = (
        abs(left_peak - right_peak)
        if comparable_topology and left_peak is not None and right_peak is not None
        else None
    )
    left_survival = finite_float(left["survival_and_event_mass"].get("final_survival"))
    right_survival = finite_float(right["survival_and_event_mass"].get("final_survival"))
    survival_difference = (
        abs(left_survival - right_survival)
        if left_survival is not None and right_survival is not None
        else None
    )
    thresholds = manifest["mesh_agreement"]
    gates = {
        "paired_root_times": root_difference is not None
        and root_difference <= float(thresholds["maximum_paired_root_time_difference"]),
        "peak_ratio": peak_difference is not None
        and peak_difference <= float(thresholds["maximum_peak_ratio_difference"]),
        "valley_ratios": valley_difference is not None
        and valley_difference <= float(thresholds["maximum_valley_ratio_difference"]),
        "event_basin_masses": mass_difference is not None
        and mass_difference <= float(thresholds["maximum_event_mass_difference"]),
        "final_survival": survival_difference is not None
        and survival_difference <= float(thresholds["maximum_final_survival_difference"]),
    }
    gates = native_json_boolean_gates(gates)
    return {
        "mesh_pair": [left["mesh"], right["mesh"]],
        "maximum_paired_root_time_difference": root_difference,
        "peak_ratio_absolute_difference": peak_difference,
        "maximum_valley_ratio_absolute_difference": valley_difference,
        "maximum_event_mass_absolute_difference": mass_difference,
        "final_survival_absolute_difference": survival_difference,
        "gates": gates,
        "all_agreement_gates_passed": bool(all(gates.values())),
    }


def _run_with_seed_active(manifest: dict[str, Any]) -> dict[str, Any]:
    pinned = validate_manifest(manifest)
    rows = [solve_mesh(int(cells), manifest) for cells in manifest["heldout_meshes"]]
    agreement = mesh_agreement(rows, manifest)
    passed = bool(all(row["all_mesh_gates_passed"] for row in rows)) and bool(
        agreement["all_agreement_gates_passed"]
    )
    return {
        "schema_version": 1,
        "stage": STAGE,
        "status": (
            "PASS_RESULT_INFORMED_POSITIVE_B_EVENT_MASS_SHAPE_CONFIRMATION"
            if passed
            else "HOLD_RESULT_INFORMED_POSITIVE_B_CONFIRMATION"
        ),
        "evidence_timing": EVIDENCE_TIMING,
        "claim_scope": manifest["claim_scope"],
        "positive_B_event_mass_shape_confirmation": passed,
        "preregistered_discovery": False,
        "continuum_interval_verified": False,
        "unbounded_domain_FV_limit_verified": False,
        "independent_solver_verified": False,
        "project_gate_passed": False,
        "physical_parameters": manifest["physical_parameters"],
        "fixed_absolute_weights": manifest["fixed_absolute_weights"],
        "positive_budget": manifest["positive_budget"],
        "weights_refit": False,
        "heldout_mesh_rows": rows,
        "mesh_agreement": agreement,
        "all_gates_passed": passed,
        "required_claim_flags": manifest["required_claim_flags"],
        "numerical_reproducibility": manifest["numerical_reproducibility"],
        "reproducibility_evidence": {
            "file": manifest["numerical_reproducibility"]["reproducibility_evidence_file"],
            "independent_full_processes_required": 2,
            "canonical_result_requires_external_byte_comparison": True,
        },
        "pinned_file_hashes": pinned,
        "manifest_sha256": sha256(MANIFEST),
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "limitations": [
            "result-informed fixed control and selected budget",
            "two fixed-box finite-volume meshes, not a PDE or unbounded-domain proof",
            "same solver family on both meshes, not independent-solver verification",
            "floating-point sign-screen and root refinement, not interval certification",
            "no physical d=3 or project/publication gate",
        ],
    }


def run_formal(manifest: dict[str, Any]) -> dict[str, Any]:
    seed = int(manifest["numerical_reproducibility"]["numpy_global_seed"])
    with pinned_numpy_global_seed(seed):
        return _run_with_seed_active(manifest)


def replica_output_paths(canonical_output: Path) -> tuple[Path, Path]:
    canonical = Path(canonical_output)
    return (
        canonical.with_name(f".{canonical.stem}.replica_1.json"),
        canonical.with_name(f".{canonical.stem}.replica_2.json"),
    )


def frozen_subprocess_environment(manifest: dict[str, Any]) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(manifest["numerical_reproducibility"]["subprocess_environment"])
    return environment


def run_replica_commands(
    commands: Sequence[Sequence[str]],
    replica_paths: Sequence[Path],
    canonical_output: Path,
    evidence_output: Path,
    manifest_path: Path,
    expected_manifest_sha256: str,
    environment: dict[str, str],
) -> dict[str, Any]:
    required_processes = int(FROZEN_REPRODUCIBILITY["independent_full_processes_required"])
    if len(commands) != required_processes or len(replica_paths) != required_processes:
        raise ValueError("exactly two replica commands and outputs are required")
    if (
        len(expected_manifest_sha256) != 64
        or any(character not in "0123456789abcdef" for character in expected_manifest_sha256)
        or sha256(manifest_path) != expected_manifest_sha256
    ):
        raise ValueError("external frozen-manifest SHA-256 does not match")

    canonical_output = Path(canonical_output)
    evidence_output = Path(evidence_output)
    replicas = [Path(path) for path in replica_paths]
    canonical_staging = canonical_output.with_name(f".{canonical_output.name}.staging")
    evidence_staging = evidence_output.with_name(f".{evidence_output.name}.staging")
    canonical_backup = canonical_output.with_name(f".{canonical_output.name}.backup")
    evidence_backup = evidence_output.with_name(f".{evidence_output.name}.backup")
    cleanup_before = [
        canonical_staging,
        evidence_staging,
        canonical_backup,
        evidence_backup,
        *replicas,
    ]
    for path in cleanup_before:
        path.unlink(missing_ok=True)
    had_canonical = canonical_output.is_file()
    had_evidence = evidence_output.is_file()

    promoted = False
    return_codes: list[int] = []
    try:
        for command, replica in zip(commands, replicas, strict=True):
            completed = subprocess.run(
                [str(value) for value in command],
                cwd=REPOSITORY,
                env=environment,
                check=False,
            )
            return_codes.append(int(completed.returncode))
            if completed.returncode not in (0, 2):
                raise RuntimeError(
                    f"replica process failed operationally with code {completed.returncode}"
                )
            if sha256(manifest_path) != expected_manifest_sha256:
                raise RuntimeError("frozen manifest changed during replica execution")
            if not replica.is_file():
                raise RuntimeError("replica process did not write its declared output")

        replica_bytes = [path.read_bytes() for path in replicas]
        if replica_bytes[0] != replica_bytes[1]:
            raise RuntimeError("complete replica outputs are not byte-identical")
        payload = json.loads(replica_bytes[0].decode("utf-8"))
        if type(payload) is not dict:
            raise RuntimeError("replica output is not a JSON object")
        require_finite_json(payload)
        if canonical_json_bytes(payload) != replica_bytes[0]:
            raise RuntimeError("replica output is not canonical JSON")
        passed = payload.get("all_gates_passed")
        if type(passed) is not bool:
            raise RuntimeError("replica result lacks a Boolean all_gates_passed")
        expected_status = (
            "PASS_RESULT_INFORMED_POSITIVE_B_EVENT_MASS_SHAPE_CONFIRMATION"
            if passed
            else "HOLD_RESULT_INFORMED_POSITIVE_B_CONFIRMATION"
        )
        expected_return_code = 0 if passed else 2
        if payload.get("status") != expected_status:
            raise RuntimeError("replica status is inconsistent with its gate result")
        if payload.get("manifest_sha256") != expected_manifest_sha256:
            raise RuntimeError("replica result cites the wrong frozen manifest")
        if return_codes != [expected_return_code] * required_processes:
            raise RuntimeError("replica exit codes are inconsistent with the result")
        if sha256(manifest_path) != expected_manifest_sha256:
            raise RuntimeError("frozen manifest changed before canonical promotion")

        result_hash = sha256_bytes(replica_bytes[0])
        evidence = {
            "schema_version": 1,
            "stage": "positive_B_broad_four_slab_two_process_reproducibility",
            "manifest_sha256": expected_manifest_sha256,
            "independent_process_count": required_processes,
            "execution_order": "sequential",
            "replica_exit_codes": return_codes,
            "replica_result_sha256": [result_hash, result_hash],
            "byte_identical": True,
            "canonical_result_sha256": result_hash,
            "canonical_promotion_after_comparison": True,
            "result_status": expected_status,
            "all_gates_passed": passed,
        }
        canonical_staging.write_bytes(replica_bytes[0])
        evidence_staging.write_bytes(canonical_json_bytes(evidence))
        if had_canonical:
            canonical_backup.write_bytes(canonical_output.read_bytes())
        if had_evidence:
            evidence_backup.write_bytes(evidence_output.read_bytes())
        evidence_staging.replace(evidence_output)
        canonical_staging.replace(canonical_output)
        promoted = True
        canonical_backup.unlink(missing_ok=True)
        evidence_backup.unlink(missing_ok=True)
        return payload
    finally:
        for path in (*replicas, canonical_staging, evidence_staging):
            path.unlink(missing_ok=True)
        if not promoted:
            if canonical_backup.is_file():
                canonical_backup.replace(canonical_output)
            elif not had_canonical:
                canonical_output.unlink(missing_ok=True)
            if evidence_backup.is_file():
                evidence_backup.replace(evidence_output)
            elif not had_evidence:
                evidence_output.unlink(missing_ok=True)
        canonical_backup.unlink(missing_ok=True)
        evidence_backup.unlink(missing_ok=True)


def execute_replica(
    output: Path,
    expected_manifest_sha256: str,
) -> dict[str, Any]:
    allowed_outputs = {path.resolve() for path in replica_output_paths(OUTPUT)}
    if Path(output).resolve() not in allowed_outputs:
        raise ValueError("replica-only mode may write only the two frozen replica paths")
    if sha256(MANIFEST) != expected_manifest_sha256:
        raise ValueError("external frozen-manifest SHA-256 does not match")
    manifest = load_json(MANIFEST)
    result = run_formal(manifest)
    if sha256(MANIFEST) != expected_manifest_sha256:
        raise RuntimeError("frozen manifest changed during the full replica calculation")
    write_json(output, result)
    return result


def execute_two_process_formal(
    expected_manifest_sha256: str,
) -> dict[str, Any]:
    if sha256(MANIFEST) != expected_manifest_sha256:
        raise ValueError("external frozen-manifest SHA-256 does not match")
    manifest = load_json(MANIFEST)
    validate_manifest(manifest)
    replicas = replica_output_paths(OUTPUT)
    commands = [
        [
            sys.executable,
            str(HERE),
            "--execute-replica",
            "--expected-manifest-sha256",
            expected_manifest_sha256,
            "--output",
            str(replica),
        ]
        for replica in replicas
    ]
    return run_replica_commands(
        commands,
        replicas,
        OUTPUT,
        REPRODUCIBILITY_OUTPUT,
        MANIFEST,
        expected_manifest_sha256,
        frozen_subprocess_environment(manifest),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--execute-frozen", action="store_true")
    mode.add_argument("--execute-replica", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    require_repository_venv()
    if args.execute_replica:
        result = execute_replica(args.output, args.expected_manifest_sha256)
    else:
        if args.output.resolve() != OUTPUT.resolve():
            parser.error("public formal execution may promote only the canonical output")
        result = execute_two_process_formal(args.expected_manifest_sha256)
    print(result["status"])
    for row in result["heldout_mesh_rows"]:
        print(
            row["mesh"][0],
            row["stationary_structure"]["valley_to_smaller_adjacent_peak_ratios"],
            row["survival_and_event_mass"]["basin_reaction_masses"],
        )
    print(args.output)
    return 0 if result["all_gates_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
