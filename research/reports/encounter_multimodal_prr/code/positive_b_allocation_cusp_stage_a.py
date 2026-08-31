#!/usr/bin/env python3
"""Fail-closed Stage-A scaffold for a fixed-budget allocation cusp.

This module implements the algebra and bounded solver interfaces specified in
``notes/positive_b_allocation_cusp_promotion_design.md``.  Its public CLI is
deliberately limited to small-grid algebra dry runs.  It cannot execute the
scientific Stage-A meshes (65 and 97), write a result artifact, search an
unbounded control set, or promote a cusp claim.

The physical finite-volume factors are reused from the broad B=0 bridge.  The
allocation state tangents, direct observable recurrences, cusp map/Jacobian,
and explicit-CSR preflight are implemented independently here.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import LinearOperator, expm_multiply

EVIDENCE_TIMING = "ALGEBRA_DRY_RUN_ONLY_NOT_STAGE_A_DISCOVERY"
REFERENCE_CUSP_TIME = 13.30724696053485
REFERENCE_WEIGHTS = np.asarray(
    (
        0.28,
        0.23115240260064182,
        0.20722533378296604,
        0.28162226361639210,
    ),
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
BUDGET_SCHEDULE = (0.0, 0.0025, 0.0050, 0.0075, 0.0100)
SCIENTIFIC_STAGE_A_MESHES = (65, 97)
DRY_RUN_MAX_CELLS = 25
RETAINED_TIME_WINDOW = (0.5, 35.0)
DRY_RUN_NUMPY_SEED = 314159
REMOTE_CUSP_NEIGHBORHOOD = 0.25
REMOTE_RELATIVE_DENSITY_FLOOR = 1.0e-8
REMOTE_SCALED_CURVATURE_FLOOR = 0.05
REMOTE_SCALED_ROOT_RESIDUAL_CAP = 1.0e-8
REMOTE_MINIMUM_ROOT_SEPARATION = 0.25


@dataclass(frozen=True)
class TrustBox:
    minimum_time: float = 9.0
    maximum_time: float = 18.0
    maximum_theta_linf: float = 0.15
    minimum_weight: float = 0.03
    maximum_newton_iterations: int = 12
    maximum_step_halvings: int = 8
    scaled_residual_tolerance: float = 1.0e-10


TRUST_BOX = TrustBox()


def require_frozen_trust_box(trust_box: TrustBox) -> None:
    if trust_box != TRUST_BOX:
        raise ValueError("Stage-A solvers require the exact frozen trust-box configuration")


@dataclass(frozen=True)
class AllocationModel:
    """Fixed free dynamics and four per-budget patch killing fields."""

    cells: int
    factors: Any
    initial: np.ndarray
    patch_fields: np.ndarray
    direction_fields: np.ndarray

    @property
    def state_count(self) -> int:
        return int(self.initial.size)


@dataclass(frozen=True)
class CuspSnapshot:
    time: float
    budget: float
    theta: np.ndarray
    weights: np.ndarray
    state: np.ndarray
    state_tangents: np.ndarray
    per_budget_time_jets: np.ndarray
    allocation_time_jets: np.ndarray
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
    snapshot: CuspSnapshot | None
    reason: str


@dataclass(frozen=True)
class StationaryPoint:
    """A caller-supplied stationary-point candidate; no search is performed."""

    time: float
    density_per_budget: float
    first_derivative_per_budget: float
    second_derivative_per_budget: float


def weights_from_theta(theta: np.ndarray) -> np.ndarray:
    value = np.asarray(theta, dtype=float)
    if value.shape != (2,) or not np.all(np.isfinite(value)):
        raise ValueError("theta must be a finite two-vector")
    return REFERENCE_WEIGHTS + TANGENT_BASIS @ value


def basis_diagnostics() -> dict[str, float]:
    return {
        "budget_tangent_error": float(np.max(np.abs(np.ones(4) @ TANGENT_BASIS))),
        "orthonormality_error": float(np.max(np.abs(TANGENT_BASIS.T @ TANGENT_BASIS - np.eye(2)))),
        "reference_weight_sum_error": float(abs(np.sum(REFERENCE_WEIGHTS) - 1.0)),
        "reference_minimum_weight": float(np.min(REFERENCE_WEIGHTS)),
    }


def point_in_trust_box(
    time: float,
    theta: np.ndarray,
    trust_box: TrustBox = TRUST_BOX,
) -> tuple[bool, str]:
    value = np.asarray(theta, dtype=float)
    if not math.isfinite(float(time)) or value.shape != (2,) or not np.all(np.isfinite(value)):
        return False, "nonfinite_or_malformed_point"
    if not trust_box.minimum_time <= float(time) <= trust_box.maximum_time:
        return False, "time_outside_trust_box"
    if float(np.max(np.abs(value))) > trust_box.maximum_theta_linf:
        return False, "theta_outside_trust_box"
    weights = weights_from_theta(value)
    if float(np.min(weights)) < trust_box.minimum_weight:
        return False, "simplex_margin_below_trust_floor"
    return True, "inside"


def validate_dry_run_cells(cells: int) -> int:
    if type(cells) is not int or cells < 5:
        raise ValueError("dry-run cells must be an integer at least 5")
    if cells in SCIENTIFIC_STAGE_A_MESHES:
        raise ValueError("scientific Stage-A meshes are forbidden at the dry-run entrypoint")
    if cells > DRY_RUN_MAX_CELLS:
        raise ValueError(f"dry-run cells must not exceed {DRY_RUN_MAX_CELLS}")
    return cells


def require_dry_run_model(model: AllocationModel) -> None:
    """Reject scientific or spoofed meshes at every computational boundary."""

    validate_dry_run_cells(model.cells)
    midpoint_states = int(model.factors.midpoint_generator.shape[0])
    relative_states = int(model.factors.relative_generator.shape[0])
    if midpoint_states != model.cells or relative_states != model.cells**2:
        raise ValueError("model cell label does not match its finite-volume factors")
    expected_states = model.cells**3
    if model.initial.shape != (expected_states,):
        raise ValueError("model initial state does not match its dry-run cell count")
    if model.patch_fields.shape != (4, expected_states):
        raise ValueError("model patch fields do not match its dry-run cell count")
    if model.direction_fields.shape != (2, expected_states):
        raise ValueError("model direction fields do not match its dry-run cell count")


_BRIDGE: Any | None = None


def bridge_module() -> Any:
    """Load the legacy dry-run bridge only when Stage-A algebra is executed."""

    global _BRIDGE
    if _BRIDGE is None:
        _BRIDGE = importlib.import_module("continuum_broad_patch_b0_bridge")
    return _BRIDGE


def build_small_grid_model(cells: int) -> AllocationModel:
    """Build a physical model only after enforcing the dry-run mesh boundary."""

    count = validate_dry_run_cells(cells)
    manifest = {
        "physical_parameters": PHYSICAL_PARAMETERS,
        "finite_volume": FINITE_VOLUME,
    }
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
    direction_fields = np.asarray(TANGENT_BASIS.T @ patch_fields, dtype=float)
    initial = np.asarray(np.kron(factors.midpoint_initial, factors.relative_initial), dtype=float)
    if patch_fields.shape != (4, initial.size) or direction_fields.shape != (2, initial.size):
        raise RuntimeError("physical killing fields do not match the tensor state")
    if abs(float(np.sum(initial)) - 1.0) > 2.0e-13:
        raise RuntimeError("initial distribution is not normalized")
    return AllocationModel(
        cells=count,
        factors=factors,
        initial=initial,
        patch_fields=patch_fields,
        direction_fields=direction_fields,
    )


class AllocationKilledColumnOperator(LinearOperator):
    """Matrix-free column generator ``Q(theta, B)^T``."""

    def __init__(self, model: AllocationModel, budget: float, theta: np.ndarray) -> None:
        require_dry_run_model(model)
        self.model = model
        self.budget = float(budget)
        if not math.isfinite(self.budget) or self.budget < 0.0:
            raise ValueError("budget must be finite and nonnegative")
        self.theta = np.asarray(theta, dtype=float).copy()
        self.weights = weights_from_theta(self.theta)
        if float(np.min(self.weights)) <= 0.0:
            raise ValueError("allocation left the strict simplex interior")
        self.kappa = np.asarray(self.weights @ model.patch_fields, dtype=float)
        self.midpoint_generator = model.factors.midpoint_generator.tocsr()
        self.relative_generator = model.factors.relative_generator.tocsr()
        self.midpoint_cells = self.midpoint_generator.shape[0]
        self.relative_states = self.relative_generator.shape[0]
        self.kappa_matrix = self.kappa.reshape(self.midpoint_cells, self.relative_states)
        expected = self.midpoint_cells * self.relative_states
        self.trace_value = float(
            self.relative_states * np.sum(self.midpoint_generator.diagonal())
            + self.midpoint_cells * np.sum(self.relative_generator.diagonal())
            - self.budget * np.sum(self.kappa)
        )
        super().__init__(dtype=np.dtype(np.float64), shape=(expected, expected))

    def _column_action(self, vector: np.ndarray) -> np.ndarray:
        shaped = np.asarray(vector, dtype=float).reshape(self.midpoint_cells, self.relative_states)
        output = self.midpoint_generator.T @ shaped
        output += (self.relative_generator.T @ shaped.T).T
        output -= self.budget * self.kappa_matrix * shaped
        return np.asarray(output, dtype=float).reshape(-1)

    def _row_action(self, vector: np.ndarray) -> np.ndarray:
        shaped = np.asarray(vector, dtype=float).reshape(self.midpoint_cells, self.relative_states)
        output = self.midpoint_generator @ shaped
        output += (self.relative_generator @ shaped.T).T
        output -= self.budget * self.kappa_matrix * shaped
        return np.asarray(output, dtype=float).reshape(-1)

    def _matvec(self, vector: np.ndarray) -> np.ndarray:
        return self._column_action(vector)

    def _rmatvec(self, vector: np.ndarray) -> np.ndarray:
        return self._row_action(vector)

    def _matmat(self, matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix, dtype=float)
        return np.column_stack(
            [self._column_action(value[:, index]) for index in range(value.shape[1])]
        )

    def _rmatmat(self, matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix, dtype=float)
        return np.column_stack(
            [self._row_action(value[:, index]) for index in range(value.shape[1])]
        )


class AllocationTangentColumnOperator(LinearOperator):
    """Block generator for ``(p, partial_theta1 p, partial_theta2 p)``."""

    def __init__(self, base: AllocationKilledColumnOperator) -> None:
        self.base = base
        self.base_states = base.shape[0]
        self.direction_fields = base.model.direction_fields
        self.trace_value = 3.0 * base.trace_value
        super().__init__(
            dtype=np.dtype(np.float64),
            shape=(3 * self.base_states, 3 * self.base_states),
        )

    def _matvec(self, vector: np.ndarray) -> np.ndarray:
        values = np.asarray(vector, dtype=float)
        p = values[: self.base_states]
        tangent_1 = values[self.base_states : 2 * self.base_states]
        tangent_2 = values[2 * self.base_states :]
        return np.concatenate(
            (
                self.base.matvec(p),
                self.base.matvec(tangent_1) - self.base.budget * self.direction_fields[0] * p,
                self.base.matvec(tangent_2) - self.base.budget * self.direction_fields[1] * p,
            )
        )

    def _rmatvec(self, vector: np.ndarray) -> np.ndarray:
        values = np.asarray(vector, dtype=float)
        left = values[: self.base_states]
        right_1 = values[self.base_states : 2 * self.base_states]
        right_2 = values[2 * self.base_states :]
        return np.concatenate(
            (
                self.base.rmatvec(left)
                - self.base.budget
                * (self.direction_fields[0] * right_1 + self.direction_fields[1] * right_2),
                self.base.rmatvec(right_1),
                self.base.rmatvec(right_2),
            )
        )

    def _matmat(self, matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix, dtype=float)
        return np.column_stack([self._matvec(value[:, index]) for index in range(value.shape[1])])

    def _rmatmat(self, matrix: np.ndarray) -> np.ndarray:
        value = np.asarray(matrix, dtype=float)
        return np.column_stack([self._rmatvec(value[:, index]) for index in range(value.shape[1])])


@contextmanager
def pinned_numpy_global_seed(seed: int = DRY_RUN_NUMPY_SEED) -> Iterator[None]:
    """Isolate SciPy ``onenormest`` from ambient global RNG state."""

    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed must be a uint32-compatible integer")
    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)


def propagate(
    operator: LinearOperator, initial: np.ndarray, time: float, trace: float
) -> np.ndarray:
    value = float(time)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError("propagation time must be finite and nonnegative")
    if value == 0.0:
        return np.asarray(initial, dtype=float).copy()
    with pinned_numpy_global_seed():
        return np.asarray(
            expm_multiply(value * operator, initial, traceA=value * float(trace)),
            dtype=float,
        )


def _observable_recurrences(
    operator: AllocationKilledColumnOperator,
    maximum_order: int = 4,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``a_r=Q^r kappa`` and both exact allocation recurrences."""

    if maximum_order < 0:
        raise ValueError("maximum_order must be nonnegative")
    observables = [operator.kappa.copy()]
    tangent_observables = [operator.model.direction_fields.copy()]
    for _order in range(maximum_order):
        previous = observables[-1]
        previous_tangents = tangent_observables[-1]
        observables.append(np.asarray(operator.rmatvec(previous), dtype=float))
        tangent_observables.append(
            np.asarray(
                [
                    operator.rmatvec(previous_tangents[index])
                    - operator.budget * operator.model.direction_fields[index] * previous
                    for index in range(2)
                ],
                dtype=float,
            )
        )
    return np.asarray(observables, dtype=float), np.asarray(tangent_observables, dtype=float)


def evaluate_point(
    model: AllocationModel,
    time: float,
    budget: float,
    theta: np.ndarray,
) -> CuspSnapshot:
    """Evaluate normalized density jets and exact fixed-budget allocation tangents."""

    theta_value = np.asarray(theta, dtype=float)
    operator = AllocationKilledColumnOperator(model, budget, theta_value)
    augmented = AllocationTangentColumnOperator(operator)
    initial = np.concatenate((model.initial, np.zeros(2 * model.state_count, dtype=float)))
    propagated = propagate(augmented, initial, time, augmented.trace_value)
    state = propagated[: model.state_count]
    tangents = propagated[model.state_count :].reshape(2, model.state_count)
    observables, observable_tangents = _observable_recurrences(operator, maximum_order=4)
    time_jets = np.asarray([float(state @ value) for value in observables], dtype=float)
    allocation_time_jets = np.asarray(
        [
            [
                float(tangents[index] @ observables[order])
                + float(state @ observable_tangents[order, index])
                for order in range(5)
            ]
            for index in range(2)
        ],
        dtype=float,
    )
    cusp_map = time_jets[1:4].copy()
    cusp_jacobian = np.asarray(
        (
            (time_jets[2], allocation_time_jets[0, 1], allocation_time_jets[1, 1]),
            (time_jets[3], allocation_time_jets[0, 2], allocation_time_jets[1, 2]),
            (time_jets[4], allocation_time_jets[0, 3], allocation_time_jets[1, 3]),
        ),
        dtype=float,
    )
    state_derivative = operator.matvec(state)
    tangent_derivatives = np.asarray(
        [
            operator.matvec(tangents[index])
            - operator.budget * model.direction_fields[index] * state
            for index in range(2)
        ],
        dtype=float,
    )
    survival_residuals = np.asarray(
        [
            abs(float(np.sum(state_derivative)) + operator.budget * time_jets[0]),
            *(
                abs(
                    float(np.sum(tangent_derivatives[index]))
                    + operator.budget * allocation_time_jets[index, 0]
                )
                for index in range(2)
            ),
        ],
        dtype=float,
    )
    return CuspSnapshot(
        time=float(time),
        budget=float(budget),
        theta=theta_value.copy(),
        weights=operator.weights.copy(),
        state=state,
        state_tangents=tangents,
        per_budget_time_jets=time_jets,
        allocation_time_jets=allocation_time_jets,
        cusp_map=cusp_map,
        cusp_jacobian=cusp_jacobian,
        survival_identity_residuals=survival_residuals,
    )


def evaluate_without_tangents(
    model: AllocationModel,
    time: float,
    budget: float,
    theta: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Independent base propagation used by allocation finite differences."""

    operator = AllocationKilledColumnOperator(model, budget, theta)
    state = propagate(operator, model.initial, time, operator.trace_value)
    observables, _tangents = _observable_recurrences(operator, maximum_order=4)
    jets = np.asarray([float(state @ value) for value in observables], dtype=float)
    return state, jets


def dimensionless_cusp_residual(snapshot: CuspSnapshot) -> np.ndarray:
    scale = float(snapshot.per_budget_time_jets[0])
    if not math.isfinite(scale) or scale <= 0.0:
        return np.full(3, math.inf)
    time = snapshot.time
    return np.asarray(
        (
            time * snapshot.cusp_map[0] / scale,
            time**2 * snapshot.cusp_map[1] / scale,
            time**3 * snapshot.cusp_map[2] / scale,
        ),
        dtype=float,
    )


def dimensionless_cusp_jacobian(snapshot: CuspSnapshot) -> np.ndarray:
    scale = float(snapshot.per_budget_time_jets[0])
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("positive density is required to scale the cusp Jacobian")
    row_scale = np.asarray(
        (snapshot.time / scale, snapshot.time**2 / scale, snapshot.time**3 / scale),
        dtype=float,
    )
    column_scale = np.asarray((snapshot.time, 1.0, 1.0), dtype=float)
    return row_scale[:, None] * snapshot.cusp_jacobian * column_scale[None, :]


def require_snapshot_jet_consistency(snapshot: CuspSnapshot) -> None:
    """Reject hand-assembled snapshots whose H/J fields disagree with their jets."""

    if snapshot.per_budget_time_jets.shape != (5,):
        raise ValueError("snapshot must contain time-jet orders zero through four")
    if snapshot.allocation_time_jets.shape != (2, 5):
        raise ValueError("snapshot must contain two allocation jet rows through order four")
    if snapshot.cusp_map.shape != (3,) or snapshot.cusp_jacobian.shape != (3, 3):
        raise ValueError("snapshot cusp map/Jacobian shapes are invalid")
    expected_map = snapshot.per_budget_time_jets[1:4]
    expected_jacobian = np.asarray(
        (
            (
                snapshot.per_budget_time_jets[2],
                snapshot.allocation_time_jets[0, 1],
                snapshot.allocation_time_jets[1, 1],
            ),
            (
                snapshot.per_budget_time_jets[3],
                snapshot.allocation_time_jets[0, 2],
                snapshot.allocation_time_jets[1, 2],
            ),
            (
                snapshot.per_budget_time_jets[4],
                snapshot.allocation_time_jets[0, 3],
                snapshot.allocation_time_jets[1, 3],
            ),
        )
    )
    if not np.all(np.isfinite(snapshot.per_budget_time_jets)) or not np.all(
        np.isfinite(snapshot.allocation_time_jets)
    ):
        raise ValueError("snapshot jets must be finite")
    if not np.allclose(snapshot.cusp_map, expected_map, rtol=0.0, atol=1.0e-14):
        raise ValueError("snapshot cusp map is inconsistent with its time jets")
    if not np.allclose(snapshot.cusp_jacobian, expected_jacobian, rtol=0.0, atol=1.0e-14):
        raise ValueError("snapshot cusp Jacobian is inconsistent with its mixed jets")


def require_near_cusp_snapshot(
    snapshot: CuspSnapshot,
    maximum_scaled_residual: float = 1.0e-8,
) -> float:
    """Return the residual only when all three cusp equations are certified small."""

    require_snapshot_jet_consistency(snapshot)
    tolerance = float(maximum_scaled_residual)
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("maximum scaled cusp residual must be finite and nonnegative")
    inside, reason = point_in_trust_box(snapshot.time, snapshot.theta)
    if not inside:
        raise ValueError(f"cusp snapshot violates the frozen trust box: {reason}")
    if not np.allclose(
        snapshot.weights,
        weights_from_theta(snapshot.theta),
        rtol=0.0,
        atol=2.0e-14,
    ):
        raise ValueError("cusp snapshot weights are inconsistent with the frozen chart")
    residual = dimensionless_cusp_residual(snapshot)
    observed = float(np.max(np.abs(residual)))
    if not math.isfinite(observed) or observed > tolerance:
        raise ValueError("operation requires a verified near-cusp snapshot")
    return observed


def require_near_fold_snapshot(
    snapshot: CuspSnapshot,
    maximum_scaled_residual: float = 1.0e-8,
) -> float:
    """Return the fold residual only when ``F_t=F_tt=0`` is certified small."""

    require_snapshot_jet_consistency(snapshot)
    tolerance = float(maximum_scaled_residual)
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("maximum scaled fold residual must be finite and nonnegative")
    inside, reason = point_in_trust_box(snapshot.time, snapshot.theta)
    if not inside:
        raise ValueError(f"fold snapshot violates the frozen trust box: {reason}")
    if not np.allclose(
        snapshot.weights,
        weights_from_theta(snapshot.theta),
        rtol=0.0,
        atol=2.0e-14,
    ):
        raise ValueError("fold snapshot weights are inconsistent with the frozen chart")
    residual = dimensionless_cusp_residual(snapshot)[:2]
    observed = float(np.max(np.abs(residual)))
    if not math.isfinite(observed) or observed > tolerance:
        raise ValueError("operation requires a verified near-fold snapshot")
    return observed


def cusp_nondegeneracy(
    snapshot: CuspSnapshot,
    *,
    maximum_scaled_residual: float = 1.0e-8,
) -> dict[str, Any]:
    """Report cusp factors only after a fail-closed near-cusp check."""

    observed_residual = require_near_cusp_snapshot(snapshot, maximum_scaled_residual)
    scaled = dimensionless_cusp_jacobian(snapshot)
    if not np.all(np.isfinite(scaled)):
        raise ValueError("dimensionless cusp Jacobian must be finite")
    projected = scaled[:2, 1:]
    projected_singular = np.linalg.svd(projected, compute_uv=False)
    full_singular = np.linalg.svd(scaled, compute_uv=False)
    fourth = float(
        snapshot.time**4 * snapshot.per_budget_time_jets[4] / snapshot.per_budget_time_jets[0]
    )
    determinant_left = float(np.linalg.det(scaled))
    determinant_right = float(fourth * np.linalg.det(projected))
    denominator = max(abs(determinant_left), abs(determinant_right), 1.0e-300)
    projected_ratio = (
        float(projected_singular[-1] / projected_singular[0])
        if projected_singular[0] > 0.0
        else 0.0
    )
    return {
        "maximum_scaled_cusp_residual": observed_residual,
        "scaled_fourth_derivative": fourth,
        "projected_singular_values": projected_singular.tolist(),
        "projected_singular_value_ratio": projected_ratio,
        "full_smallest_singular_value": float(full_singular[-1]),
        "determinant_factorization_relative_residual": float(
            abs(determinant_left - determinant_right) / denominator
        ),
    }


def solve_cusp(
    model: AllocationModel,
    budget: float,
    initial_time: float,
    initial_theta: np.ndarray,
    trust_box: TrustBox = TRUST_BOX,
) -> CuspSolve:
    """Bounded analytic-Newton solve; every failure returns an explicit HOLD."""

    require_dry_run_model(model)
    require_frozen_trust_box(trust_box)
    point = np.asarray((initial_time, *np.asarray(initial_theta, dtype=float)), dtype=float)
    inside, reason = point_in_trust_box(point[0], point[1:], trust_box)
    if not inside:
        return CuspSolve("HOLD_DISCOVERY", False, 0, None, reason)
    last: CuspSnapshot | None = None
    for iteration in range(trust_box.maximum_newton_iterations + 1):
        try:
            current = evaluate_point(model, point[0], budget, point[1:])
        except (ArithmeticError, RuntimeError, ValueError) as error:
            return CuspSolve("HOLD_DISCOVERY", False, iteration, None, f"evaluation:{error}")
        last = current
        residual = dimensionless_cusp_residual(current)
        norm = float(np.max(np.abs(residual)))
        if math.isfinite(norm) and norm <= trust_box.scaled_residual_tolerance:
            return CuspSolve("PASS_DISCOVERY_SOLVE", True, iteration, current, "converged")
        if iteration == trust_box.maximum_newton_iterations:
            break
        if not np.all(np.isfinite(current.cusp_jacobian)):
            return CuspSolve("HOLD_DISCOVERY", False, iteration, current, "nonfinite_jacobian")
        try:
            step = np.linalg.solve(current.cusp_jacobian, -current.cusp_map)
        except np.linalg.LinAlgError:
            return CuspSolve("HOLD_DISCOVERY", False, iteration, current, "singular_jacobian")
        if not np.all(np.isfinite(step)):
            return CuspSolve("HOLD_DISCOVERY", False, iteration, current, "nonfinite_newton_step")
        accepted = False
        for halving in range(trust_box.maximum_step_halvings + 1):
            candidate = point + step / (2**halving)
            candidate_inside, _candidate_reason = point_in_trust_box(
                candidate[0], candidate[1:], trust_box
            )
            if not candidate_inside:
                continue
            try:
                candidate_snapshot = evaluate_point(model, candidate[0], budget, candidate[1:])
            except (ArithmeticError, RuntimeError, ValueError):
                continue
            candidate_norm = float(np.max(np.abs(dimensionless_cusp_residual(candidate_snapshot))))
            if math.isfinite(candidate_norm) and candidate_norm < norm:
                point = candidate
                accepted = True
                break
        if not accepted:
            return CuspSolve(
                "HOLD_DISCOVERY", False, iteration, current, "bounded_line_search_failed"
            )
    return CuspSolve(
        "HOLD_DISCOVERY",
        False,
        trust_box.maximum_newton_iterations,
        last,
        "maximum_newton_iterations_reached",
    )


def run_budget_homotopy(
    model: AllocationModel,
    initial_time: float = REFERENCE_CUSP_TIME,
    initial_theta: np.ndarray | None = None,
) -> dict[str, Any]:
    """Apply exactly the predeclared B schedule, stopping at the first HOLD."""

    require_dry_run_model(model)
    theta = (
        np.zeros(2, dtype=float)
        if initial_theta is None
        else np.asarray(initial_theta, dtype=float)
    )
    time = float(initial_time)
    rows: list[dict[str, Any]] = []
    for budget in BUDGET_SCHEDULE:
        solve = solve_cusp(model, budget, time, theta)
        row: dict[str, Any] = {
            "budget": budget,
            "status": solve.status,
            "converged": solve.converged,
            "iterations": solve.iterations,
            "reason": solve.reason,
        }
        if solve.snapshot is not None:
            row.update(
                {
                    "time": solve.snapshot.time,
                    "theta": solve.snapshot.theta.tolist(),
                    "weights": solve.snapshot.weights.tolist(),
                    "maximum_scaled_residual": float(
                        np.max(np.abs(dimensionless_cusp_residual(solve.snapshot)))
                    ),
                }
            )
        rows.append(row)
        if not solve.converged or solve.snapshot is None:
            return {
                "status": "HOLD_DISCOVERY",
                "completed_budget_schedule": False,
                "rows": rows,
            }
        time = solve.snapshot.time
        theta = solve.snapshot.theta
    return {
        "status": "PASS_DRY_RUN_HOMOTOPY_ONLY",
        "completed_budget_schedule": True,
        "rows": rows,
    }


def explicit_row_generator(
    model: AllocationModel,
    budget: float,
    theta: np.ndarray,
) -> sparse.csr_matrix:
    """Construct the full row generator solely for a small-grid audit."""

    operator = AllocationKilledColumnOperator(model, budget, theta)
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
    return (free - sparse.diags(operator.budget * operator.kappa, format="csr")).tocsr()


def explicit_augmented_column_generator(
    model: AllocationModel,
    budget: float,
    theta: np.ndarray,
) -> sparse.csr_matrix:
    row = explicit_row_generator(model, budget, theta)
    column = row.T.tocsr()
    zero = sparse.csr_matrix(column.shape, dtype=float)
    couplings = tuple(
        sparse.diags(-float(budget) * field, format="csr") for field in model.direction_fields
    )
    return sparse.bmat(
        (
            (column, zero, zero),
            (couplings[0], column, zero),
            (couplings[1], zero, column),
        ),
        format="csr",
    )


def _relative_l1_error(left: np.ndarray, right: np.ndarray) -> float:
    denominator = max(float(np.linalg.norm(right, ord=1)), 1.0e-300)
    return float(np.linalg.norm(np.asarray(left) - np.asarray(right), ord=1) / denominator)


def _finite_difference_snapshot(
    model: AllocationModel,
    time: float,
    budget: float,
    theta: np.ndarray,
    allocation_step: float,
    relative_time_step: float,
) -> tuple[np.ndarray, np.ndarray]:
    theta_value = np.asarray(theta, dtype=float)
    time_step = float(relative_time_step) * float(time)
    plus_time = evaluate_without_tangents(model, time + time_step, budget, theta_value)[1][1:4]
    minus_time = evaluate_without_tangents(model, time - time_step, budget, theta_value)[1][1:4]
    columns = [(plus_time - minus_time) / (2.0 * time_step)]
    state_columns = []
    for index in range(2):
        increment = np.zeros(2, dtype=float)
        increment[index] = float(allocation_step)
        plus_state, plus_jets = evaluate_without_tangents(
            model, time, budget, theta_value + increment
        )
        minus_state, minus_jets = evaluate_without_tangents(
            model, time, budget, theta_value - increment
        )
        state_columns.append((plus_state - minus_state) / (2.0 * allocation_step))
        columns.append((plus_jets[1:4] - minus_jets[1:4]) / (2.0 * allocation_step))
    return np.asarray(state_columns, dtype=float), np.column_stack(columns)


def algebra_preflight(
    model: AllocationModel,
    *,
    time: float = REFERENCE_CUSP_TIME,
    budget: float = 0.01,
    theta: np.ndarray | None = None,
) -> dict[str, Any]:
    """Compare matrix-free algebra with explicit CSR and two finite differences."""

    require_dry_run_model(model)
    theta_value = np.zeros(2, dtype=float) if theta is None else np.asarray(theta, dtype=float)
    snapshot = evaluate_point(model, time, budget, theta_value)
    base = AllocationKilledColumnOperator(model, budget, theta_value)
    augmented = AllocationTangentColumnOperator(base)
    explicit_row = explicit_row_generator(model, budget, theta_value)
    explicit_augmented = explicit_augmented_column_generator(model, budget, theta_value)

    state_count = model.state_count
    vector = np.sin(np.arange(state_count, dtype=float) + 0.37)
    augmented_vector = np.cos(np.arange(3 * state_count, dtype=float) + 0.19)
    column_action_error = float(np.max(np.abs(base.matvec(vector) - explicit_row.T @ vector)))
    row_action_error = float(np.max(np.abs(base.rmatvec(vector) - explicit_row @ vector)))
    augmented_column_action_error = float(
        np.max(np.abs(augmented.matvec(augmented_vector) - explicit_augmented @ augmented_vector))
    )
    augmented_row_action_error = float(
        np.max(
            np.abs(augmented.rmatvec(augmented_vector) - explicit_augmented.T @ augmented_vector)
        )
    )
    augmented_initial = np.concatenate(
        (model.initial, np.zeros(2 * model.state_count, dtype=float))
    )
    with pinned_numpy_global_seed():
        explicit_propagated = np.asarray(
            expm_multiply(float(time) * explicit_augmented, augmented_initial),
            dtype=float,
        )
    matrix_free_propagated = np.concatenate((snapshot.state, snapshot.state_tangents.reshape(-1)))
    propagation_relative_l1_error = _relative_l1_error(matrix_free_propagated, explicit_propagated)

    # Independently form Q^r kappa with the explicit row matrix.  The tangent
    # recurrence is then checked against centred differences of those explicit
    # powers, so a self-consistent error in the matrix-free recurrence cannot
    # pass merely by being reused on both sides of the audit.
    observables, observable_tangents = _observable_recurrences(base, maximum_order=4)
    explicit_observables = [base.kappa.copy()]
    for _order in range(4):
        explicit_observables.append(
            np.asarray(explicit_row @ explicit_observables[-1], dtype=float)
        )
    observable_recurrence_error = float(
        np.max(np.abs(observables - np.asarray(explicit_observables)))
    )
    observable_tangent_errors = []
    observable_tangent_step = 2.0e-5
    for index in range(2):
        increment = np.zeros(2, dtype=float)
        increment[index] = observable_tangent_step
        plus_operator = AllocationKilledColumnOperator(model, budget, theta_value + increment)
        minus_operator = AllocationKilledColumnOperator(model, budget, theta_value - increment)
        plus_row = explicit_row_generator(model, budget, theta_value + increment)
        minus_row = explicit_row_generator(model, budget, theta_value - increment)
        plus_observables = [plus_operator.kappa.copy()]
        minus_observables = [minus_operator.kappa.copy()]
        for _order in range(4):
            plus_observables.append(np.asarray(plus_row @ plus_observables[-1], dtype=float))
            minus_observables.append(np.asarray(minus_row @ minus_observables[-1], dtype=float))
        explicit_difference = (np.asarray(plus_observables) - np.asarray(minus_observables)) / (
            2.0 * observable_tangent_step
        )
        observable_tangent_errors.append(
            float(np.max(np.abs(observable_tangents[:, index] - explicit_difference)))
        )
    observable_tangent_recurrence_error = max(observable_tangent_errors)

    steps = ((2.0e-5, 2.0e-5), (1.0e-5, 1.0e-5))
    finite_difference_rows = []
    for allocation_step, relative_time_step in steps:
        fd_states, fd_jacobian = _finite_difference_snapshot(
            model,
            time,
            budget,
            theta_value,
            allocation_step,
            relative_time_step,
        )
        state_error = max(
            _relative_l1_error(snapshot.state_tangents[index], fd_states[index])
            for index in range(2)
        )
        scale = float(snapshot.per_budget_time_jets[0])
        row_scale = np.asarray((time / scale, time**2 / scale, time**3 / scale))
        column_scale = np.asarray((time, 1.0, 1.0))
        scaled_fd = row_scale[:, None] * fd_jacobian * column_scale[None, :]
        scaled_analytic = dimensionless_cusp_jacobian(snapshot)
        jacobian_error = float(np.max(np.abs(scaled_analytic - scaled_fd)))
        time_column_error = float(np.max(np.abs(scaled_analytic[:, 0] - scaled_fd[:, 0])))
        allocation_column_error = float(np.max(np.abs(scaled_analytic[:, 1:] - scaled_fd[:, 1:])))
        finite_difference_rows.append(
            {
                "allocation_step": allocation_step,
                "relative_time_step": relative_time_step,
                "maximum_state_tangent_relative_l1_error": state_error,
                "maximum_dimensionless_cusp_jacobian_absolute_error": jacobian_error,
                "dimensionless_time_column_absolute_error": time_column_error,
                "dimensionless_allocation_columns_absolute_error": allocation_column_error,
            }
        )

    large = finite_difference_rows[0]
    small = finite_difference_rows[1]
    roundoff_floor = 5.0e-8
    state_decrease = bool(
        small["maximum_state_tangent_relative_l1_error"]
        <= max(
            roundoff_floor,
            0.8 * large["maximum_state_tangent_relative_l1_error"],
        )
    )
    time_column_decrease = bool(
        small["dimensionless_time_column_absolute_error"]
        <= max(
            roundoff_floor,
            0.8 * large["dimensionless_time_column_absolute_error"],
        )
    )
    allocation_column_decrease = bool(
        small["dimensionless_allocation_columns_absolute_error"]
        <= max(
            roundoff_floor,
            0.8 * large["dimensionless_allocation_columns_absolute_error"],
        )
    )
    gates = {
        "basis_fixed_budget": basis_diagnostics()["budget_tangent_error"] <= 2.0e-14,
        "basis_orthonormal": basis_diagnostics()["orthonormality_error"] <= 2.0e-14,
        "explicit_column_action": column_action_error <= 1.0e-11,
        "explicit_row_action": row_action_error <= 1.0e-11,
        "explicit_augmented_column_action": augmented_column_action_error <= 1.0e-11,
        "explicit_augmented_row_action": augmented_row_action_error <= 1.0e-11,
        "explicit_propagation": propagation_relative_l1_error <= 1.0e-10,
        "explicit_observable_recurrence": observable_recurrence_error <= 1.0e-11,
        "explicit_observable_tangent_recurrence": observable_tangent_recurrence_error <= 1.0e-8,
        "state_tangent_two_step_finite_difference": state_decrease
        and small["maximum_state_tangent_relative_l1_error"] <= 1.0e-6,
        "complete_H_jacobian_two_step_finite_difference": time_column_decrease
        and allocation_column_decrease
        and small["maximum_dimensionless_cusp_jacobian_absolute_error"] <= 1.0e-6,
        "survival_derivative_identities": float(np.max(snapshot.survival_identity_residuals))
        <= 1.0e-11,
    }
    return {
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "explicit_csr": {
            "state_count": state_count,
            "row_generator_nnz": int(explicit_row.nnz),
            "augmented_column_generator_nnz": int(explicit_augmented.nnz),
            "column_action_maximum_absolute_error": column_action_error,
            "row_action_maximum_absolute_error": row_action_error,
            "augmented_column_action_maximum_absolute_error": augmented_column_action_error,
            "augmented_row_action_maximum_absolute_error": augmented_row_action_error,
            "propagation_relative_l1_error": propagation_relative_l1_error,
            "observable_recurrence_maximum_absolute_error": observable_recurrence_error,
            "observable_tangent_recurrence_maximum_absolute_error": (
                observable_tangent_recurrence_error
            ),
        },
        "finite_difference": {
            "roundoff_floor": roundoff_floor,
            "rows": finite_difference_rows,
            "state_error_decrease_or_floor": state_decrease,
            "time_column_error_decrease_or_floor": time_column_decrease,
            "allocation_column_error_decrease_or_floor": allocation_column_decrease,
        },
        "maximum_survival_identity_residual": float(np.max(snapshot.survival_identity_residuals)),
        "snapshot": {
            "time": snapshot.time,
            "budget": snapshot.budget,
            "theta": snapshot.theta.tolist(),
            "weights": snapshot.weights.tolist(),
            "per_budget_time_jets_orders_0_to_4": snapshot.per_budget_time_jets.tolist(),
            "allocation_time_jets": snapshot.allocation_time_jets.tolist(),
            "dimensionless_cusp_jacobian": dimensionless_cusp_jacobian(snapshot).tolist(),
        },
    }


def fold_predictor(snapshot: CuspSnapshot, time_offset: float) -> np.ndarray:
    """Return the two allocation coordinates from the frozen cusp predictor."""

    require_near_cusp_snapshot(snapshot)
    tau = float(time_offset)
    if not math.isfinite(tau) or tau == 0.0:
        raise ValueError("fold predictor requires a finite nonzero time offset")
    response = snapshot.cusp_jacobian[:2, 1:]
    if not np.all(np.isfinite(response)):
        raise ValueError("projected cusp response is nonfinite")
    if np.linalg.matrix_rank(response) != 2:
        raise ValueError("projected cusp response is rank deficient")
    fourth = float(snapshot.per_budget_time_jets[4])
    if not math.isfinite(fourth) or fourth == 0.0:
        raise ValueError("cusp fourth derivative must be finite and nonzero")
    eta = np.linalg.solve(
        response,
        np.asarray((fourth * tau**3 / 3.0, -fourth * tau**2 / 2.0)),
    )
    predicted_theta = snapshot.theta + eta
    inside, reason = point_in_trust_box(snapshot.time + tau, predicted_theta)
    if not inside:
        raise ValueError(f"fold predictor violates the frozen trust box: {reason}")
    return predicted_theta


def canonical_outgoing_fold_predictors(snapshot: CuspSnapshot) -> dict[str, np.ndarray]:
    """Return exactly the two predeclared ``tau=-0.10,+0.10`` predictors."""

    return {
        "negative": np.asarray(
            (snapshot.time - 0.10, *fold_predictor(snapshot, -0.10)), dtype=float
        ),
        "positive": np.asarray(
            (snapshot.time + 0.10, *fold_predictor(snapshot, 0.10)), dtype=float
        ),
    }


def validate_arclength_step(step: float) -> float:
    """Enforce the predeclared continuation-step interval."""

    value = float(step)
    if not math.isfinite(value) or not 0.025 <= value <= 0.20:
        raise ValueError("arclength step must lie in the frozen interval [0.025, 0.20]")
    return value


def fold_null_direction(
    snapshot: CuspSnapshot,
    previous_direction: np.ndarray | None = None,
) -> np.ndarray:
    """Return a continuously oriented unit null vector of the fold Jacobian."""

    require_near_fold_snapshot(snapshot)
    if not np.all(np.isfinite(snapshot.fold_jacobian)):
        raise ValueError("fold Jacobian must be finite")
    _left, singular_values, right = np.linalg.svd(snapshot.fold_jacobian)
    if singular_values[-1] <= 1.0e-14:
        raise ValueError("fold Jacobian is rank deficient")
    direction = np.asarray(right[-1], dtype=float)
    direction /= np.linalg.norm(direction)
    if previous_direction is not None:
        previous = np.asarray(previous_direction, dtype=float)
        if previous.shape != (3,) or not np.all(np.isfinite(previous)):
            raise ValueError("previous branch direction must be a finite three-vector")
        previous_norm = float(np.linalg.norm(previous))
        if previous_norm == 0.0:
            raise ValueError("previous branch direction must be nonzero")
        overlap = float(direction @ (previous / previous_norm))
        if abs(overlap) <= 1.0e-12:
            raise ValueError("previous branch direction cannot orient the new null vector")
        if overlap < 0.0:
            direction = -direction
    return direction


def correct_fold_at_fixed_time(
    model: AllocationModel,
    budget: float,
    time: float,
    initial_theta: np.ndarray,
    trust_box: TrustBox = TRUST_BOX,
) -> dict[str, Any]:
    """Boundedly correct ``(F_t,F_tt)=0`` at a caller-supplied fixed time."""

    require_dry_run_model(model)
    require_frozen_trust_box(trust_box)
    theta = np.asarray(initial_theta, dtype=float).copy()
    for iteration in range(trust_box.maximum_newton_iterations + 1):
        inside, reason = point_in_trust_box(time, theta, trust_box)
        if not inside:
            return {"status": "HOLD_BRANCH", "converged": False, "reason": reason}
        try:
            snapshot = evaluate_point(model, time, budget, theta)
        except (ArithmeticError, RuntimeError, ValueError):
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "evaluation_failed",
            }
        scale = float(snapshot.per_budget_time_jets[0])
        if not math.isfinite(scale) or scale <= 0.0:
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "nonpositive_or_nonfinite_density",
            }
        residual = np.asarray(
            (time * snapshot.cusp_map[0] / scale, time**2 * snapshot.cusp_map[1] / scale)
        )
        if not np.all(np.isfinite(residual)):
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "nonfinite_residual",
            }
        norm = float(np.max(np.abs(residual)))
        if norm <= trust_box.scaled_residual_tolerance:
            return {
                "status": "PASS_BRANCH_CORRECTION",
                "converged": True,
                "iterations": iteration,
                "snapshot": snapshot,
            }
        if iteration == trust_box.maximum_newton_iterations:
            break
        jacobian = snapshot.cusp_jacobian[:2, 1:]
        if not np.all(np.isfinite(jacobian)):
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "nonfinite_allocation_fold_jacobian",
            }
        try:
            step = np.linalg.solve(jacobian, -snapshot.cusp_map[:2])
        except np.linalg.LinAlgError:
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "singular_allocation_fold_jacobian",
            }
        if not np.all(np.isfinite(step)):
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "nonfinite_newton_step",
            }
        accepted = False
        for halving in range(trust_box.maximum_step_halvings + 1):
            candidate = theta + step / (2**halving)
            candidate_inside, _reason = point_in_trust_box(time, candidate, trust_box)
            if not candidate_inside:
                continue
            try:
                candidate_snapshot = evaluate_point(model, time, budget, candidate)
            except (ArithmeticError, RuntimeError, ValueError):
                continue
            candidate_scale = float(candidate_snapshot.per_budget_time_jets[0])
            if not math.isfinite(candidate_scale) or candidate_scale <= 0.0:
                continue
            candidate_residual = np.asarray(
                (
                    time * candidate_snapshot.cusp_map[0] / candidate_scale,
                    time**2 * candidate_snapshot.cusp_map[1] / candidate_scale,
                )
            )
            if (
                np.all(np.isfinite(candidate_residual))
                and float(np.max(np.abs(candidate_residual))) < norm
            ):
                theta = candidate
                accepted = True
                break
        if not accepted:
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "bounded_line_search_failed",
            }
    return {
        "status": "HOLD_BRANCH",
        "converged": False,
        "reason": "maximum_newton_iterations_reached",
    }


def pseudo_arclength_corrector(
    model: AllocationModel,
    budget: float,
    predicted_point: np.ndarray,
    branch_direction: np.ndarray,
    trust_box: TrustBox = TRUST_BOX,
) -> dict[str, Any]:
    """Correct one predeclared branch predictor; this routine performs no scan."""

    require_dry_run_model(model)
    require_frozen_trust_box(trust_box)
    predictor = np.asarray(predicted_point, dtype=float)
    direction = np.asarray(branch_direction, dtype=float)
    if predictor.shape != (3,) or direction.shape != (3,):
        raise ValueError("predictor and branch direction must be three-vectors")
    if not np.all(np.isfinite(predictor)) or not np.all(np.isfinite(direction)):
        raise ValueError("predictor and branch direction must be finite")
    norm_direction = float(np.linalg.norm(direction))
    if norm_direction == 0.0:
        raise ValueError("branch direction must be nonzero")
    direction = direction / norm_direction
    point = predictor.copy()
    for iteration in range(trust_box.maximum_newton_iterations + 1):
        inside, reason = point_in_trust_box(point[0], point[1:], trust_box)
        if not inside:
            return {"status": "HOLD_BRANCH", "converged": False, "reason": reason}
        try:
            snapshot = evaluate_point(model, point[0], budget, point[1:])
        except (ArithmeticError, RuntimeError, ValueError):
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "evaluation_failed",
            }
        scale = float(snapshot.per_budget_time_jets[0])
        if not math.isfinite(scale) or scale <= 0.0:
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "nonpositive_or_nonfinite_density",
            }
        residual = np.asarray(
            (
                point[0] * snapshot.cusp_map[0] / scale,
                point[0] ** 2 * snapshot.cusp_map[1] / scale,
                float(direction @ (point - predictor)),
            ),
            dtype=float,
        )
        if not np.all(np.isfinite(residual)):
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "nonfinite_residual",
            }
        if float(np.max(np.abs(residual))) <= trust_box.scaled_residual_tolerance:
            return {
                "status": "PASS_BRANCH_CORRECTION",
                "converged": True,
                "iterations": iteration,
                "snapshot": snapshot,
            }
        if iteration == trust_box.maximum_newton_iterations:
            break
        raw_residual = np.asarray(
            (snapshot.cusp_map[0], snapshot.cusp_map[1], residual[2]), dtype=float
        )
        jacobian = np.vstack((snapshot.fold_jacobian, direction))
        if not np.all(np.isfinite(jacobian)):
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "nonfinite_corrector_jacobian",
            }
        try:
            step = np.linalg.solve(jacobian, -raw_residual)
        except np.linalg.LinAlgError:
            return {"status": "HOLD_BRANCH", "converged": False, "reason": "singular_corrector"}
        if not np.all(np.isfinite(step)):
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "nonfinite_newton_step",
            }
        accepted = False
        current_norm = float(np.max(np.abs(residual)))
        for halving in range(trust_box.maximum_step_halvings + 1):
            candidate = point + step / (2**halving)
            candidate_inside, _reason = point_in_trust_box(candidate[0], candidate[1:], trust_box)
            if not candidate_inside:
                continue
            try:
                candidate_snapshot = evaluate_point(model, candidate[0], budget, candidate[1:])
            except (ArithmeticError, RuntimeError, ValueError):
                continue
            candidate_scale = float(candidate_snapshot.per_budget_time_jets[0])
            if not math.isfinite(candidate_scale) or candidate_scale <= 0.0:
                continue
            candidate_residual = np.asarray(
                (
                    candidate[0] * candidate_snapshot.cusp_map[0] / candidate_scale,
                    candidate[0] ** 2 * candidate_snapshot.cusp_map[1] / candidate_scale,
                    float(direction @ (candidate - predictor)),
                )
            )
            if (
                np.all(np.isfinite(candidate_residual))
                and float(np.max(np.abs(candidate_residual))) < current_norm
            ):
                point = candidate
                accepted = True
                break
        if not accepted:
            return {
                "status": "HOLD_BRANCH",
                "converged": False,
                "reason": "bounded_line_search_failed",
            }
    return {
        "status": "HOLD_BRANCH",
        "converged": False,
        "reason": "maximum_newton_iterations_reached",
    }


def assess_supplied_remote_pair(
    cusp_time: float,
    candidates: Sequence[StationaryPoint],
    reference_density: float,
) -> dict[str, Any]:
    """Gate supplied roots only; candidate discovery is intentionally out of scope."""

    if (
        not math.isfinite(cusp_time)
        or not RETAINED_TIME_WINDOW[0] <= cusp_time <= RETAINED_TIME_WINDOW[1]
    ):
        raise ValueError("cusp time must lie in the fixed retained-time window")
    if not math.isfinite(reference_density) or reference_density <= 0.0:
        raise ValueError("reference density must be finite and positive")
    ordered = sorted(enumerate(candidates), key=lambda item: item[1].time)
    eligible: list[tuple[int, StationaryPoint, str]] = []
    for source_index, candidate in ordered:
        values = (
            candidate.time,
            candidate.density_per_budget,
            candidate.first_derivative_per_budget,
            candidate.second_derivative_per_budget,
        )
        if not all(math.isfinite(value) for value in values):
            continue
        if not RETAINED_TIME_WINDOW[0] <= candidate.time <= RETAINED_TIME_WINDOW[1]:
            continue
        if abs(candidate.time - cusp_time) <= REMOTE_CUSP_NEIGHBORHOOD:
            continue
        if candidate.density_per_budget <= 0.0:
            continue
        if candidate.density_per_budget < REMOTE_RELATIVE_DENSITY_FLOOR * reference_density:
            continue
        scaled_first = abs(
            candidate.time * candidate.first_derivative_per_budget / candidate.density_per_budget
        )
        scaled_second = (
            candidate.time**2
            * candidate.second_derivative_per_budget
            / candidate.density_per_budget
        )
        if (
            scaled_first > REMOTE_SCALED_ROOT_RESIDUAL_CAP
            or abs(scaled_second) < REMOTE_SCALED_CURVATURE_FLOOR
        ):
            continue
        eligible.append((source_index, candidate, "maximum" if scaled_second < 0.0 else "minimum"))
    pair = None
    for left, right in zip(eligible, eligible[1:]):
        same_side_of_cusp = (left[1].time - cusp_time) * (right[1].time - cusp_time) > 0.0
        separated = right[1].time - left[1].time >= REMOTE_MINIMUM_ROOT_SEPARATION
        if left[2] == "maximum" and right[2] == "minimum" and same_side_of_cusp and separated:
            pair = {
                "maximum_time": left[1].time,
                "minimum_time": right[1].time,
                "maximum_source_index": left[0],
                "minimum_source_index": right[0],
            }
            break
    return {
        "remote_pair_present": pair is not None,
        "eligible_candidate_count": len(eligible),
        "pair": pair,
        "candidate_search_performed": False,
        "retained_time_window": list(RETAINED_TIME_WINDOW),
        "frozen_thresholds": {
            "cusp_neighborhood": REMOTE_CUSP_NEIGHBORHOOD,
            "relative_density_floor": REMOTE_RELATIVE_DENSITY_FLOOR,
            "scaled_curvature_floor": REMOTE_SCALED_CURVATURE_FLOOR,
            "scaled_root_residual_cap": REMOTE_SCALED_ROOT_RESIDUAL_CAP,
            "minimum_root_separation": REMOTE_MINIMUM_ROOT_SEPARATION,
        },
    }


def run_algebra_dry_run(cells: int) -> dict[str, Any]:
    model = build_small_grid_model(cells)
    preflight = algebra_preflight(model)
    homotopy = run_budget_homotopy(model)
    return {
        "schema_version": 1,
        "stage": "fixed_budget_allocation_cusp_stage_a_scaffold",
        "evidence_timing": EVIDENCE_TIMING,
        "status": (
            "PASS_ALGEBRA_DRY_RUN_HOLD_SCIENCE"
            if preflight["all_gates_passed"]
            else "HOLD_ALGEBRA_DRY_RUN"
        ),
        "mesh": [model.cells, model.cells, model.cells],
        "scientific_stage_a_meshes_executed": [],
        "basis_diagnostics": basis_diagnostics(),
        "trust_box": {
            "time": [TRUST_BOX.minimum_time, TRUST_BOX.maximum_time],
            "maximum_theta_linf": TRUST_BOX.maximum_theta_linf,
            "minimum_weight": TRUST_BOX.minimum_weight,
            "maximum_newton_iterations": TRUST_BOX.maximum_newton_iterations,
            "maximum_step_halvings": TRUST_BOX.maximum_step_halvings,
        },
        "budget_schedule": list(BUDGET_SCHEDULE),
        "algebra_preflight": preflight,
        "bounded_small_grid_homotopy": homotopy,
        "claim_flags": {
            "positive_B_allocation_cusp_verified": False,
            "fold_branches_verified": False,
            "remote_pair_verified": False,
            "phase_representatives_verified": False,
            "mesh_convergence_verified": False,
            "unbounded_domain_verified": False,
            "independent_solver_verified": False,
            "publication_gate_passed": False,
        },
        "limitations": [
            "small-grid algebra dry run only",
            "homotopy outcome is not Stage-A discovery evidence",
            "no stationary-root or allocation-control scan is implemented",
            "no result artifact or freeze manifest is written",
        ],
    }


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--algebra-dry-run",
        action="store_true",
        help="run the only enabled small-grid, non-scientific execution mode",
    )
    parser.add_argument("--cells", type=int, default=11)
    arguments = parser.parse_args(argv)
    if not arguments.algebra_dry_run:
        parser.error("only --algebra-dry-run is enabled; scientific Stage A is not frozen")
    payload = run_algebra_dry_run(arguments.cells)
    require_finite_json(payload)
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))
    return 0 if payload["algebra_preflight"]["all_gates_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
