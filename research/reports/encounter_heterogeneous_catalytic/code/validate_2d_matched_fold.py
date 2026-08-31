#!/usr/bin/env python3
"""Matched-budget 2D fold certificate on finite reflecting grids.

The continuation changes only the spatial allocation of Doi reactivity,

    kappa_theta(c) = (1-theta) kappa_bar
                     + theta [0.5 1_Cnear(c) + 15 1_Cfar(c)].

``kappa_bar`` is recomputed on every grid so that the declared discrete
budget of killing rates over the finite-radius encounter tube is identical at
every theta.  The principal budget is the Markov-state sum; a separate
product-control-volume quadrature is audited as a one-factor sensitivity.
Fold derivatives are actions of the sparse generator, not finite
differences of sampled curves.  Parameter sensitivity is obtained from the
standard augmented matrix exponential.

The script intentionally records the non-convergence and budget-measure
sensitivity of the fold coordinate.  Thus the result is a finite-lattice
mechanism certificate, while the cross-grid endpoint resolution-class
contrast is the promoted numerical conclusion.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import sparse
from scipy.integrate import quad
from scipy.optimize import brentq, least_squares, root
from scipy.sparse.linalg import expm_multiply
from vkcore.encounter2d import (
    DoiCatalyticPatch,
    RectangularGrid2D,
    build_doi_encounter_2d,
    contact_safe_initial_distribution_2d,
    initial_distribution_diagnostics_2d,
    reflecting_advection_diffusion_generator_2d,
)
from vkcore.plotting import enforce_publication_graphics
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

GRIDS = ((9, 5), (11, 7), (13, 9))
ENDPOINT_GRIDS = ((9, 5), (10, 6), (11, 7), (12, 8), (13, 9))
REACTION_RADIUS = 0.17
START_ONE = (0.0, 0.5)
START_TWO = (0.28, 0.5)
WALKER_ONE = {
    "diffusion": 0.0025,
    "drift_x": 0.115,
    "transverse_confinement": 1.5,
}
WALKER_TWO = {
    "diffusion": 0.0008,
    "drift_x": 0.02,
    "transverse_confinement": 1.5,
}
NEAR_CENTRE = (0.25, 0.5)
NEAR_RADIUS = 0.18
NEAR_RATE = 0.5
FAR_CENTRE = (0.72, 0.5)
FAR_RADIUS = 0.20
FAR_RATE = 15.0
SHAPE_TMAX = 60.0
SHAPE_DT = 0.05
TAIL_TIME = 480.0
QUADRATURE_TMAX = 40.0
QUADRATURE_STEPS = (0.20, 0.10, 0.05)
SCALING_MU = np.asarray(
    (0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05),
    dtype=float,
)
SCALING_FIT_COUNT = 6
HELD_OUT_DELTA = 0.005
MIN_RESOLVED_PEAK_RATIO = 0.03
MAX_RESOLVED_VALLEY_RATIO = 0.95
FOLD_RESIDUAL_TOLERANCE = 1e-8
FOLD_DETERMINANT_TOLERANCE = 1e-14
FOLD_INITIAL_GUESSES = {
    (9, 5): (16.81, 0.275),
    (11, 7): (18.10, 0.014),
    (13, 9): (16.60, 0.256),
}
WEIGHTED_FOLD_INITIAL_GUESSES = {
    (9, 5): (16.75, 0.624),
    (11, 7): (18.19, 0.241),
    (13, 9): (16.43, 0.459),
}


@dataclass(frozen=True)
class MatchedFamily:
    grid: RectangularGrid2D
    kappa_bar: float
    budget_measure: str
    matching_weights: np.ndarray
    tube_measure: float
    near_measure: float
    far_measure: float
    tube_count: int
    near_count: int
    far_count: int
    budget: float
    A0: sparse.csr_matrix
    Atheta: sparse.csr_matrix
    k0: np.ndarray
    ktheta: np.ndarray
    initial: np.ndarray
    initial_diagnostics: dict[str, object]
    patterned_channel_rates: sparse.csr_matrix


def _product_matching_weights(
    grid: RectangularGrid2D,
    budget_measure: str,
) -> np.ndarray:
    """Return the declared product-state measure used only for budget matching.

    The CTMC generator and its probability measure are unchanged.  The
    ``product_trapezoidal`` option is the tensor-product boundary-node
    trapezoidal rule (equivalently, boundary control-volume weights) on the
    four-dimensional two-walker product domain.
    """

    if budget_measure == "state_count":
        return np.ones(grid.state_count**2, dtype=float)
    if budget_measure != "product_trapezoidal":
        raise ValueError(f"unknown budget measure: {budget_measure}")
    weights_x = np.ones(grid.nx, dtype=float)
    weights_y = np.ones(grid.ny, dtype=float)
    weights_x[[0, -1]] = 0.5
    weights_y[[0, -1]] = 0.5
    single = (
        np.kron(weights_x, weights_y)
        * grid.spacing_x
        * grid.spacing_y
    )
    return np.kron(single, single)


def _patches(theta: float, kappa_bar: float) -> tuple[DoiCatalyticPatch, ...]:
    return (
        DoiCatalyticPatch(
            (0.5, 0.5),
            1.0,
            (1.0 - theta) * kappa_bar,
            "homogeneous",
        ),
        DoiCatalyticPatch(
            NEAR_CENTRE,
            NEAR_RADIUS,
            theta * NEAR_RATE,
            "near",
        ),
        DoiCatalyticPatch(
            FAR_CENTRE,
            FAR_RADIUS,
            theta * FAR_RATE,
            "far",
        ),
    )


def _build_family(
    nx: int,
    ny: int,
    *,
    budget_measure: str = "state_count",
) -> MatchedFamily:
    grid = RectangularGrid2D(nx, ny)
    generator_one = reflecting_advection_diffusion_generator_2d(
        grid,
        **WALKER_ONE,
    )
    generator_two = reflecting_advection_diffusion_generator_2d(
        grid,
        **WALKER_TWO,
    )
    patterned = build_doi_encounter_2d(
        grid,
        generator_one,
        generator_two,
        reaction_radius=REACTION_RADIUS,
        patches=(
            DoiCatalyticPatch(
                NEAR_CENTRE,
                NEAR_RADIUS,
                NEAR_RATE,
                "near",
            ),
            DoiCatalyticPatch(
                FAR_CENTRE,
                FAR_RADIUS,
                FAR_RATE,
                "far",
            ),
        ),
        centre_weight=0.5,
    )
    unit_tube = build_doi_encounter_2d(
        grid,
        generator_one,
        generator_two,
        reaction_radius=REACTION_RADIUS,
        patches=(DoiCatalyticPatch((0.5, 0.5), 1.0, 1.0, "tube"),),
        centre_weight=0.5,
    )
    tube_count = int(unit_tube.reactive_state_counts[0])
    near_count, far_count = map(int, patterned.reactive_state_counts)
    weights = _product_matching_weights(grid, budget_measure)
    tube_indicator = np.asarray(
        unit_tube.channel_rate_matrix.sum(axis=1)
    ).reshape(-1)
    patterned_total = np.asarray(
        patterned.channel_rate_matrix.sum(axis=1)
    ).reshape(-1)
    tube_measure = float(np.dot(weights, tube_indicator))
    channel_measures = np.asarray(
        weights @ patterned.channel_rate_matrix
    ).reshape(-1)
    near_measure, far_measure = map(float, channel_measures)
    budget = float(np.dot(weights, patterned_total))
    kappa_bar = budget / tube_measure

    model_zero = build_doi_encounter_2d(
        grid,
        generator_one,
        generator_two,
        reaction_radius=REACTION_RADIUS,
        patches=_patches(0.0, kappa_bar),
        centre_weight=0.5,
    )
    model_one = build_doi_encounter_2d(
        grid,
        generator_one,
        generator_two,
        reaction_radius=REACTION_RADIUS,
        patches=_patches(1.0, kappa_bar),
        centre_weight=0.5,
    )
    k0 = np.asarray(model_zero.channel_rate_matrix.sum(axis=1)).reshape(-1)
    k1 = np.asarray(model_one.channel_rate_matrix.sum(axis=1)).reshape(-1)
    if abs(float(np.dot(weights, k0)) - budget) > 2e-12:
        raise RuntimeError("homogeneous endpoint does not match the discrete budget")
    if abs(float(np.dot(weights, k1)) - budget) > 2e-12:
        raise RuntimeError("patterned endpoint does not match the discrete budget")
    initial = contact_safe_initial_distribution_2d(
        unit_tube,
        START_ONE,
        START_TWO,
    )
    initial_diagnostics = asdict(
        initial_distribution_diagnostics_2d(
            unit_tube,
            initial,
            walker1_position=START_ONE,
            walker2_position=START_TWO,
        )
    )
    return MatchedFamily(
        grid=grid,
        kappa_bar=float(kappa_bar),
        budget_measure=budget_measure,
        matching_weights=weights,
        tube_measure=tube_measure,
        near_measure=near_measure,
        far_measure=far_measure,
        tube_count=tube_count,
        near_count=near_count,
        far_count=far_count,
        budget=float(budget),
        A0=model_zero.killed_generator,
        Atheta=model_one.killed_generator - model_zero.killed_generator,
        k0=k0,
        ktheta=k1 - k0,
        initial=initial,
        initial_diagnostics=initial_diagnostics,
        patterned_channel_rates=model_one.channel_rate_matrix,
    )


def _operator(family: MatchedFamily, theta: float) -> tuple[sparse.csr_matrix, np.ndarray]:
    return (
        family.A0 + float(theta) * family.Atheta,
        family.k0 + float(theta) * family.ktheta,
    )


def _resolution_diagnostics(grid: RectangularGrid2D) -> dict[str, float | str]:
    """Dimensionless diagnostics that prevent an SDE-refinement interpretation."""

    def walker_rows(parameters: dict[str, float]) -> dict[str, float]:
        diffusion = float(parameters["diffusion"])
        drift_x = abs(float(parameters["drift_x"]))
        confinement = float(parameters["transverse_confinement"])
        pe_x = drift_x * grid.spacing_x / diffusion
        pe_y_boundary = confinement * 0.5 * grid.spacing_y / diffusion
        return {
            "cell_peclet_x": pe_x,
            "upwind_effective_diffusion_x_ratio": 1.0 + 0.5 * pe_x,
            "maximum_boundary_cell_peclet_y": pe_y_boundary,
            "one_cell_from_centre_peclet_y": (
                confinement * grid.spacing_y**2 / diffusion
            ),
        }

    return {
        "interpretation": (
            "finite-lattice family; high cell Peclet numbers preclude treating "
            "these grids as a controlled continuum-SDE refinement"
        ),
        "reaction_radius_over_spacing_x": REACTION_RADIUS / grid.spacing_x,
        "reaction_radius_over_spacing_y": REACTION_RADIUS / grid.spacing_y,
        "near_patch_radius_over_spacing_x": NEAR_RADIUS / grid.spacing_x,
        "near_patch_radius_over_spacing_y": NEAR_RADIUS / grid.spacing_y,
        "far_patch_radius_over_spacing_x": FAR_RADIUS / grid.spacing_x,
        "far_patch_radius_over_spacing_y": FAR_RADIUS / grid.spacing_y,
        "walker_one": walker_rows(WALKER_ONE),
        "walker_two": walker_rows(WALKER_TWO),
    }


def _state(family: MatchedFamily, time: float, theta: float) -> np.ndarray:
    operator, _ = _operator(family, theta)
    return np.asarray(
        expm_multiply(operator.T * float(time), family.initial),
        dtype=float,
    )


def _state_and_sensitivity(
    family: MatchedFamily,
    time: float,
    theta: float,
) -> tuple[np.ndarray, np.ndarray]:
    operator, _ = _operator(family, theta)
    n = family.initial.size
    augmented = sparse.bmat(
        [
            [operator.T, None],
            [family.Atheta.T, operator.T],
        ],
        format="csr",
    )
    augmented_initial = np.concatenate((family.initial, np.zeros(n, dtype=float)))
    value = np.asarray(
        expm_multiply(augmented * float(time), augmented_initial),
        dtype=float,
    )
    return value[:n], value[n:]


def _fold_quantities(
    family: MatchedFamily,
    time: float,
    theta: float,
    *,
    sensitivity: bool,
) -> dict[str, float]:
    operator, killing = _operator(family, theta)
    if sensitivity:
        state, state_theta = _state_and_sensitivity(family, time, theta)
    else:
        state = _state(family, time, theta)
        state_theta = None
    Ak = np.asarray(operator @ killing, dtype=float)
    A2k = np.asarray(operator @ Ak, dtype=float)
    A3k = np.asarray(operator @ A2k, dtype=float)
    values = {
        "f": float(np.dot(state, killing)),
        "f_t": float(np.dot(state, Ak)),
        "f_tt": float(np.dot(state, A2k)),
        "f_ttt": float(np.dot(state, A3k)),
        "survival": float(state.sum()),
    }
    if sensitivity:
        assert state_theta is not None
        derivative_Ak = family.Atheta @ killing + operator @ family.ktheta
        derivative_A2k = (
            family.Atheta @ Ak
            + operator @ (family.Atheta @ killing)
            + operator @ (operator @ family.ktheta)
        )
        values["f_ttheta"] = float(
            np.dot(state_theta, Ak) + np.dot(state, derivative_Ak)
        )
        values["f_tt_theta"] = float(
            np.dot(state_theta, A2k) + np.dot(state, derivative_A2k)
        )
        values["state_theta_l1"] = float(np.linalg.norm(state_theta, ord=1))
    return values


def _solve_fold(
    family: MatchedFamily,
    *,
    initial_guess: tuple[float, float] | None = None,
    require_physical: bool = True,
) -> tuple[dict, np.ndarray]:
    grid_key = (family.grid.nx, family.grid.ny)

    def objective(point: np.ndarray) -> np.ndarray:
        values = _fold_quantities(
            family,
            float(point[0]),
            float(point[1]),
            sensitivity=True,
        )
        return np.asarray((values["f_t"], values["f_tt"]), dtype=float)

    def jacobian(point: np.ndarray) -> np.ndarray:
        values = _fold_quantities(
            family,
            float(point[0]),
            float(point[1]),
            sensitivity=True,
        )
        return np.asarray(
            (
                (values["f_tt"], values["f_ttheta"]),
                (values["f_ttt"], values["f_tt_theta"]),
            ),
            dtype=float,
        )

    solution = root(
        objective,
        FOLD_INITIAL_GUESSES[grid_key] if initial_guess is None else initial_guess,
        jac=jacobian,
        tol=1e-11,
    )
    if not solution.success:
        raise RuntimeError(f"fold solve failed on {grid_key}: {solution.message}")
    time, theta = map(float, solution.x)
    if require_physical and not (0.0 < time < SHAPE_TMAX and 0.0 < theta < 1.0):
        raise RuntimeError(f"fold root is outside the physical continuation: {solution.x}")
    values = _fold_quantities(family, time, theta, sensitivity=True)
    determinant = -values["f_ttheta"] * values["f_ttt"]
    density_scale = max(abs(values["f"]), np.finfo(float).tiny)
    dimensionless_f_t_residual = abs(values["f_t"]) * max(abs(time), 1.0) / density_scale
    dimensionless_f_tt_residual = (
        abs(values["f_tt"]) * max(abs(time), 1.0) ** 2 / density_scale
    )
    max_dimensionless_residual = max(
        dimensionless_f_t_residual,
        dimensionless_f_tt_residual,
    )
    if max_dimensionless_residual > FOLD_RESIDUAL_TOLERANCE:
        raise RuntimeError(
            "fold optimizer reported success without satisfying the equations: "
            f"grid={grid_key}, point={solution.x.tolist()}, "
            f"dimensionless_residual={max_dimensionless_residual:.6g}"
        )
    if (
        not np.isfinite(determinant)
        or abs(determinant) <= FOLD_DETERMINANT_TOLERANCE
        or values["f_ttt"] == 0.0
        or values["f_ttheta"] == 0.0
    ):
        raise RuntimeError(
            f"fold root is degenerate on {grid_key}: determinant={determinant:.6g}"
        )
    fold = {
        "time": time,
        "theta": theta,
        "density": values["f"],
        "f_t_residual": values["f_t"],
        "f_tt_residual": values["f_tt"],
        "dimensionless_f_t_residual": dimensionless_f_t_residual,
        "dimensionless_f_tt_residual": dimensionless_f_tt_residual,
        "max_dimensionless_residual": max_dimensionless_residual,
        "f_ttt": values["f_ttt"],
        "f_ttheta": values["f_ttheta"],
        "f_tt_theta": values["f_tt_theta"],
        "state_theta_l1": values["state_theta_l1"],
        "jacobian_determinant": determinant,
        "root_success": bool(solution.success),
        "root_message": str(solution.message),
        "residual_gate_tolerance": FOLD_RESIDUAL_TOLERANCE,
        "nondegeneracy_gate_tolerance": FOLD_DETERMINANT_TOLERANCE,
        "derivative_method": "sparse generator actions plus augmented expm sensitivity",
    }
    return fold, jacobian(solution.x)


def _ft(family: MatchedFamily, time: float, theta: float) -> float:
    return _fold_quantities(family, time, theta, sensitivity=False)["f_t"]


def _stationary_point(
    family: MatchedFamily,
    theta: float,
    left: float,
    right: float,
) -> dict[str, float | str]:
    time = float(
        brentq(
            lambda value: _ft(family, value, theta),
            float(left),
            float(right),
            xtol=2e-12,
            rtol=2e-14,
        )
    )
    values = _fold_quantities(family, time, theta, sensitivity=False)
    return {
        "time": time,
        "density": values["f"],
        "f_t_residual": values["f_t"],
        "f_tt": values["f_tt"],
        "kind": "minimum" if values["f_tt"] > 0.0 else "maximum",
    }


def _scaling_rows(family: MatchedFamily, fold: dict) -> tuple[dict, list[dict]]:
    time_c = float(fold["time"])
    theta_c = float(fold["theta"])
    normal_coefficient = float(fold["f_ttheta"])
    curvature = float(fold["f_ttt"])
    half_separation_coefficient = float(
        np.sqrt(-2.0 * normal_coefficient / curvature)
    )
    separation_coefficient = 2.0 * half_separation_coefficient
    prominence_coefficient = float(
        2.0 / 3.0 * abs(curvature) * half_separation_coefficient**3
    )
    rows: list[dict] = []
    for mu in SCALING_MU:
        theta = theta_c + float(mu)
        predicted = half_separation_coefficient * float(np.sqrt(mu))

        factor = 2.0
        while _ft(family, time_c - factor * predicted, theta) > 0.0:
            factor *= 1.5
        minimum = _stationary_point(
            family,
            theta,
            time_c - factor * predicted,
            time_c,
        )
        factor = 2.0
        while _ft(family, time_c + factor * predicted, theta) > 0.0:
            factor *= 1.5
        maximum = _stationary_point(
            family,
            theta,
            time_c,
            time_c + factor * predicted,
        )
        separation = float(maximum["time"] - minimum["time"])
        prominence = float(maximum["density"] - minimum["density"])
        if separation <= 0.0 or prominence <= 0.0:
            raise RuntimeError("supercritical fold did not create a min/max pair")
        predicted_separation = separation_coefficient * float(np.sqrt(mu))
        predicted_prominence = prominence_coefficient * float(mu**1.5)
        rows.append(
            {
                "mu": float(mu),
                "theta": theta,
                "minimum_time": float(minimum["time"]),
                "maximum_time": float(maximum["time"]),
                "separation": separation,
                "prominence": prominence,
                "normal_form_half_separation": predicted,
                "normal_form_separation": predicted_separation,
                "normal_form_prominence": predicted_prominence,
                "separation_ratio_to_normal_form": separation
                / predicted_separation,
                "prominence_ratio_to_normal_form": prominence
                / predicted_prominence,
                "minimum_f_t_residual": float(minimum["f_t_residual"]),
                "maximum_f_t_residual": float(maximum["f_t_residual"]),
            }
        )

    fit = rows[:SCALING_FIT_COUNT]
    log_mu = np.log([row["mu"] for row in fit])
    separation_fit = np.polyfit(
        log_mu,
        np.log([row["separation"] for row in fit]),
        1,
    )
    prominence_fit = np.polyfit(
        log_mu,
        np.log([row["prominence"] for row in fit]),
        1,
    )
    summary = {
        "fit_mu_max": float(fit[-1]["mu"]),
        "fit_points": SCALING_FIT_COUNT,
        "separation_exponent": float(separation_fit[0]),
        "separation_prefactor": float(np.exp(separation_fit[1])),
        "prominence_exponent": float(prominence_fit[0]),
        "prominence_prefactor": float(np.exp(prominence_fit[1])),
        "expected_separation_exponent": 0.5,
        "expected_prominence_exponent": 1.5,
        "normal_form_half_separation_coefficient": half_separation_coefficient,
        "normal_form_separation_coefficient": separation_coefficient,
        "normal_form_prominence_coefficient": prominence_coefficient,
    }
    return summary, rows


def _uniform_series(
    family: MatchedFamily,
    theta: float,
    times: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    operator, killing = _operator(family, theta)
    time_array = np.asarray(times, dtype=float)
    if time_array.size < 2 or not np.allclose(
        np.diff(time_array),
        time_array[1] - time_array[0],
        rtol=1e-11,
        atol=1e-14,
    ):
        raise ValueError("series times must be a nontrivial uniform grid")
    time_step = float(time_array[1] - time_array[0])
    derivative_vector = np.asarray(operator @ killing, dtype=float)
    density = np.empty(time_array.size, dtype=float)
    derivative = np.empty(time_array.size, dtype=float)
    survival = np.empty(time_array.size, dtype=float)

    # Chunking bounds peak memory on the 13x9 product grid.  The state at the
    # end of a chunk is exactly the initial state of the next matrix
    # exponential, so no time stepping approximation is introduced.
    current = (
        family.initial.copy()
        if time_array[0] == 0.0
        else np.asarray(
            expm_multiply(operator.T * float(time_array[0]), family.initial),
            dtype=float,
        )
    )
    start_index = 0
    chunk_intervals = 200
    while start_index < time_array.size:
        stop_index = min(start_index + chunk_intervals, time_array.size - 1)
        interval_count = stop_index - start_index
        if interval_count == 0:
            states = current.reshape(1, -1)
        else:
            states = np.asarray(
                expm_multiply(
                    operator.T,
                    current,
                    start=0.0,
                    stop=interval_count * time_step,
                    num=interval_count + 1,
                    endpoint=True,
                ),
                dtype=float,
            )
        local_slice = slice(start_index, stop_index + 1)
        density[local_slice] = np.dot(states, killing)
        derivative[local_slice] = np.dot(states, derivative_vector)
        survival[local_slice] = states.sum(axis=1)
        current = states[-1].copy()
        if stop_index == time_array.size - 1:
            break
        start_index = stop_index
    return density, derivative, survival


def _uniform_fold_derivative_series(
    family: MatchedFamily,
    theta: float,
    times: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return first and second density derivatives from the finite semigroup."""

    operator, killing = _operator(family, theta)
    first_vector = np.asarray(operator @ killing, dtype=float)
    second_vector = np.asarray(operator @ first_vector, dtype=float)
    states = np.asarray(
        expm_multiply(
            operator.T,
            family.initial,
            start=float(times[0]),
            stop=float(times[-1]),
            num=int(times.size),
            endpoint=True,
        ),
        dtype=float,
    )
    return np.asarray(states @ first_vector), np.asarray(states @ second_vector)


def _fold_topology_diagnostics(
    even_families: dict[tuple[int, int], MatchedFamily],
) -> dict:
    """Record an out-of-domain root and a bounded no-root search.

    These are diagnostics, not exhaustive root-count proofs.  In particular,
    the 10x6 statement is deliberately limited to the declared curvature scan
    and four bounded least-squares starts.
    """

    family_12 = even_families[(12, 8)]
    extrapolated_fold, _ = _solve_fold(
        family_12,
        initial_guess=(18.27, -0.0616),
        require_physical=False,
    )
    if not extrapolated_fold["theta"] < 0.0:
        raise RuntimeError("12x8 diagnostic fold was expected outside theta >= 0")

    family_10 = even_families[(10, 6)]
    theta_scan = np.linspace(-0.2, 0.1, 31)
    time_scan = np.linspace(0.01, 40.0, 401)
    curvature_roots: list[dict[str, float]] = []
    for theta in theta_scan:
        _, second = _uniform_fold_derivative_series(family_10, float(theta), time_scan)
        crossings = np.flatnonzero(second[:-1] * second[1:] < 0.0)
        for index in crossings:
            time = float(
                brentq(
                    lambda value: _fold_quantities(
                        family_10,
                        value,
                        float(theta),
                        sensitivity=False,
                    )["f_tt"],
                    float(time_scan[index]),
                    float(time_scan[index + 1]),
                    xtol=1e-11,
                    rtol=1e-12,
                )
            )
            values = _fold_quantities(
                family_10,
                time,
                float(theta),
                sensitivity=False,
            )
            curvature_roots.append(
                {
                    "theta": float(theta),
                    "time": time,
                    "f_t": float(values["f_t"]),
                    "f_tt": float(values["f_tt"]),
                }
            )
    if not curvature_roots:
        raise RuntimeError("10x6 curvature scan found no branch to audit")

    def objective(point: np.ndarray) -> np.ndarray:
        values = _fold_quantities(
            family_10,
            float(point[0]),
            float(point[1]),
            sensitivity=True,
        )
        return np.asarray((values["f_t"], values["f_tt"]), dtype=float) / 1e-5

    def jacobian(point: np.ndarray) -> np.ndarray:
        values = _fold_quantities(
            family_10,
            float(point[0]),
            float(point[1]),
            sensitivity=True,
        )
        return np.asarray(
            (
                (values["f_tt"], values["f_ttheta"]),
                (values["f_ttt"], values["f_tt_theta"]),
            ),
            dtype=float,
        ) / 1e-5

    attempts: list[dict] = []
    for guess in ((15.3, -0.0957), (15.0, -0.1), (16.0, -0.09), (12.0, -0.13)):
        solution = least_squares(
            objective,
            guess,
            jac=jacobian,
            bounds=((8.0, -0.2), (25.0, 0.0)),
            x_scale=(10.0, 0.1),
            xtol=1e-13,
            ftol=1e-13,
            gtol=1e-13,
            max_nfev=300,
        )
        values = _fold_quantities(
            family_10,
            float(solution.x[0]),
            float(solution.x[1]),
            sensitivity=True,
        )
        attempts.append(
            {
                "initial_guess": list(guess),
                "time": float(solution.x[0]),
                "theta": float(solution.x[1]),
                "f_t": float(values["f_t"]),
                "f_tt": float(values["f_tt"]),
                "scaled_residual_norm": float(np.linalg.norm(solution.fun)),
                "success": bool(solution.success),
                "message": str(solution.message),
                "nfev": int(solution.nfev),
            }
        )
    if not all(row["success"] for row in attempts):
        raise RuntimeError("10x6 bounded least-squares diagnostic did not converge")
    if min(float(row["f_t"]) for row in attempts) <= 1e-6:
        raise RuntimeError("10x6 diagnostic unexpectedly approached a fold root")

    closest_scan = min(curvature_roots, key=lambda row: abs(row["f_t"]))
    return {
        "claim_boundary": (
            "bounded diagnostics only; absence of a 10x6 fold is not proved "
            "outside the declared scan and starts"
        ),
        "grid_12x8_extrapolated_fold": {
            **extrapolated_fold,
            "physical_theta_interval": [0.0, 1.0],
            "inside_physical_interval": False,
        },
        "grid_10x6_curvature_scan": {
            "theta_interval": [-0.2, 0.1],
            "theta_points": int(theta_scan.size),
            "time_interval": [0.01, 40.0],
            "time_points": int(time_scan.size),
            "curvature_root_count": len(curvature_roots),
            "closest_sampled_curvature_root": closest_scan,
            "all_curvature_roots": curvature_roots,
        },
        "grid_10x6_bounded_least_squares": {
            "bounds": {"time": [8.0, 25.0], "theta": [-0.2, 0.0]},
            "objective_scale": 1e-5,
            "attempts": attempts,
            "minimum_positive_f_t": min(float(row["f_t"]) for row in attempts),
            "root_found": False,
        },
    }


def _tube_volume() -> float:
    return float(
        np.pi * REACTION_RADIUS**2
        - (8.0 / 3.0) * REACTION_RADIUS**3
        + 0.5 * REACTION_RADIUS**4
    )


def _circular_segment_area(radius: float, signed_cut: float) -> float:
    """Area of the disk portion left of a signed vertical cut."""

    cut = float(np.clip(signed_cut, -radius, radius))
    return float(
        cut * np.sqrt(max(0.0, radius**2 - cut**2))
        + radius**2 * (np.arcsin(cut / radius) + 0.5 * np.pi)
    )


def _boundary_clipped_patch_joint_volume(
    centre_x: float,
    radius: float,
    *,
    boundary: str,
) -> float:
    """Integrate the exact midpoint-feasible patch volume over the relative disk."""

    if 0.5 - radius <= 0.5 * REACTION_RADIUS:
        raise ValueError("the current one-dimensional reduction assumes no y clipping")
    if boundary == "left":
        clearance = centre_x - radius

        def signed_cut(relative_x: float) -> float:
            return 0.5 * relative_x - centre_x

    elif boundary == "right":
        clearance = 1.0 - centre_x - radius

        def signed_cut(relative_x: float) -> float:
            return centre_x - (1.0 - 0.5 * relative_x)

    else:
        raise ValueError("boundary must be left or right")

    def integrand(relative_x: float) -> float:
        available_patch_area = (
            np.pi * radius**2
            - _circular_segment_area(radius, signed_cut(relative_x))
        )
        return float(
            4.0
            * np.sqrt(max(0.0, REACTION_RADIUS**2 - relative_x**2))
            * available_patch_area
        )

    break_point = 2.0 * clearance
    points = [break_point] if 0.0 < break_point < REACTION_RADIUS else None
    value, error = quad(
        integrand,
        0.0,
        REACTION_RADIUS,
        epsabs=1e-14,
        epsrel=1e-13,
        points=points,
        limit=500,
    )
    if error > 2e-13:
        raise RuntimeError(f"continuum patch-volume quadrature error={error:.6g}")
    return float(value)


def _continuum_budget_reference() -> dict[str, float | str]:
    """Exact boundary-clipped and factorized counterfactual continuum rates."""

    tube_volume = _tube_volume()
    near_joint_volume = _boundary_clipped_patch_joint_volume(
        NEAR_CENTRE[0],
        NEAR_RADIUS,
        boundary="left",
    )
    far_joint_volume = _boundary_clipped_patch_joint_volume(
        FAR_CENTRE[0],
        FAR_RADIUS,
        boundary="right",
    )
    exact_rate = (
        NEAR_RATE * near_joint_volume + FAR_RATE * far_joint_volume
    ) / tube_volume
    patterned_centre_integral = np.pi * (
        NEAR_RATE * NEAR_RADIUS**2 + FAR_RATE * FAR_RADIUS**2
    )
    factorized_rate = float(
        np.pi
        * REACTION_RADIUS**2
        * patterned_centre_integral
        / tube_volume
    )
    return {
        "exact_boundary_clipped_kappa_bar": float(exact_rate),
        "interior_patch_factorized_counterfactual_kappa_bar": factorized_rate,
        "factorized_relative_error": factorized_rate / exact_rate - 1.0,
        "tube_volume": tube_volume,
        "near_patch_joint_volume": near_joint_volume,
        "far_patch_joint_volume": far_joint_volume,
        "quadrature_reduction": (
            "one-dimensional integration over |r_x| after analytic r_y width; "
            "y clipping is absent for both patches"
        ),
    }


def _budget_measure_sensitivity(
    state_count_families: dict[tuple[int, int], MatchedFamily],
    state_count_folds: dict[tuple[int, int], dict],
) -> dict:
    """Recompute folds with product control-volume budget matching."""

    continuum_reference = _continuum_budget_reference()
    continuum_rate = float(continuum_reference["exact_boundary_clipped_kappa_bar"])
    rows: list[dict] = []
    for grid_key in GRIDS:
        state_family = state_count_families[grid_key]
        weighted_family = _build_family(
            *grid_key,
            budget_measure="product_trapezoidal",
        )
        weighted_fold, _ = _solve_fold(
            weighted_family,
            initial_guess=WEIGHTED_FOLD_INITIAL_GUESSES[grid_key],
        )
        weighted_budget_zero = float(
            np.dot(weighted_family.matching_weights, weighted_family.k0)
        )
        weighted_budget_one = float(
            np.dot(
                weighted_family.matching_weights,
                weighted_family.k0 + weighted_family.ktheta,
            )
        )
        state_fold = state_count_folds[grid_key]
        rows.append(
            {
                "grid": list(grid_key),
                "state_count_budget": {
                    "kappa_bar": state_family.kappa_bar,
                    "relative_error_to_continuum_rate": (
                        state_family.kappa_bar / continuum_rate - 1.0
                    ),
                    "theta_c": state_fold["theta"],
                    "time_c": state_fold["time"],
                },
                "product_trapezoidal_budget": {
                    "definition": (
                        "tensor-product boundary-node trapezoidal/control-volume "
                        "weights on the four-dimensional two-walker domain"
                    ),
                    "kappa_bar": weighted_family.kappa_bar,
                    "relative_error_to_continuum_rate": (
                        weighted_family.kappa_bar / continuum_rate - 1.0
                    ),
                    "weighted_budget_theta0": weighted_budget_zero,
                    "weighted_budget_theta1": weighted_budget_one,
                    "weighted_budget_invariance_error": max(
                        abs(weighted_budget_zero - weighted_family.budget),
                        abs(weighted_budget_one - weighted_family.budget),
                    ),
                    "tube_measure": weighted_family.tube_measure,
                    "near_measure": weighted_family.near_measure,
                    "far_measure": weighted_family.far_measure,
                    "fold": weighted_fold,
                },
                "theta_c_measure_shift": (
                    weighted_fold["theta"] - state_fold["theta"]
                ),
            }
        )
    weighted_theta = [
        float(row["product_trapezoidal_budget"]["fold"]["theta"])
        for row in rows
    ]
    return {
        "claim_boundary": (
            "fold existence persists under this one-factor budget-measure "
            "control, but theta_c remains nonmonotone and nonconverged"
        ),
        "continuum_finite_a_reference": continuum_reference,
        "rows": rows,
        "weighted_theta_c_range": max(weighted_theta) - min(weighted_theta),
        "all_weighted_folds_physical_and_nondegenerate": all(
            0.0 < row["product_trapezoidal_budget"]["fold"]["theta"] < 1.0
            and abs(
                row["product_trapezoidal_budget"]["fold"]["jacobian_determinant"]
            )
            > FOLD_DETERMINANT_TOLERANCE
            for row in rows
        ),
    }


def _stationary_points_from_scan(
    family: MatchedFamily,
    theta: float,
    times: np.ndarray,
    derivative: np.ndarray,
) -> list[dict]:
    crossings = np.flatnonzero(derivative[:-1] * derivative[1:] < 0.0)
    return [
        _stationary_point(family, theta, times[index], times[index + 1])
        for index in crossings
    ]


def _endpoint_metrics(
    family: MatchedFamily,
    theta: float,
) -> tuple[dict, dict[str, np.ndarray]]:
    times = np.linspace(
        0.0,
        SHAPE_TMAX,
        int(round(SHAPE_TMAX / SHAPE_DT)) + 1,
    )
    density, derivative, survival = _uniform_series(family, theta, times)
    points = _stationary_points_from_scan(family, theta, times, derivative)
    ordered_points = sorted(points, key=lambda point: float(point["time"]))
    maxima = [point for point in ordered_points if point["kind"] == "maximum"]
    minima = [point for point in ordered_points if point["kind"] == "minimum"]
    classification = (
        "strict_unimodal"
        if len(maxima) == 1 and not minima
        else "strict_bimodal"
        if len(maxima) == 2 and len(minima) == 1
        else "other"
    )
    tail_at_completion = float(_state(family, TAIL_TIME, theta).sum())
    quadrature_mass = float(np.trapezoid(density, times))
    result = {
        "theta": theta,
        "classification": classification,
        "stationary_points": points,
        "shape_tail": float(survival[-1]),
        "tail_at_480": tail_at_completion,
        "exact_reaction_mass_at_480": 1.0 - tail_at_completion,
        "shape_quadrature_mass": quadrature_mass,
        "shape_quadrature_closure_error": abs(
            quadrature_mass + float(survival[-1]) - 1.0
        ),
    }
    if classification == "strict_bimodal":
        ordered = sorted(points, key=lambda point: float(point["time"]))
        early, valley, late = ordered
        result["peak_height_ratio"] = min(
            float(early["density"]), float(late["density"])
        ) / max(float(early["density"]), float(late["density"]))
        result["valley_ratio"] = float(valley["density"]) / min(
            float(early["density"]), float(late["density"])
        )
        channel_fluxes: list[list[float]] = []
        for point in (early, late):
            state = _state(family, float(point["time"]), theta)
            channel_fluxes.append(
                np.asarray(state @ family.patterned_channel_rates, dtype=float).tolist()
            )
        result["patterned_channel_flux_at_peaks"] = channel_fluxes
    return result, {
        "times": times,
        "density": density,
        "derivative": derivative,
        "survival": survival,
    }


def _held_out_metrics(
    family: MatchedFamily,
    fold: dict,
) -> tuple[dict, dict[str, np.ndarray]]:
    time_c = float(fold["time"])
    theta_c = float(fold["theta"])
    times = np.linspace(time_c - 2.5, time_c + 2.5, 201)
    rows: dict[str, dict] = {}
    archive: dict[str, np.ndarray] = {"times": times}
    for label, theta in (
        ("subcritical", theta_c - HELD_OUT_DELTA),
        ("critical", theta_c),
        ("supercritical", theta_c + HELD_OUT_DELTA),
    ):
        density, derivative, _ = _uniform_series(family, theta, times)
        # At criticality f_t merely touches zero.  A sign-change scanner is
        # mathematically inapplicable there and can manufacture two brackets
        # from roundoff around the double root.
        points = (
            [
                {
                    "time": time_c,
                    "density": float(fold["density"]),
                    "f_t_residual": float(fold["f_t_residual"]),
                    "f_tt": float(fold["f_tt_residual"]),
                    "kind": "degenerate_fold",
                }
            ]
            if label == "critical"
            else _stationary_points_from_scan(family, theta, times, derivative)
        )
        rows[label] = {
            "theta": theta,
            "max_f_t_on_local_window": float(np.max(derivative)),
            "min_f_t_on_local_window": float(np.min(derivative)),
            "local_stationary_points": points,
        }
        archive[f"{label}_density"] = density
        archive[f"{label}_f_t"] = derivative
    return rows, archive


def _time_step_metrics(family: MatchedFamily, theta: float) -> list[dict]:
    rows: list[dict] = []
    for step in QUADRATURE_STEPS:
        times = np.linspace(
            0.0,
            QUADRATURE_TMAX,
            int(round(QUADRATURE_TMAX / step)) + 1,
        )
        density, _, survival = _uniform_series(family, theta, times)
        reaction_mass = float(np.trapezoid(density, times))
        rows.append(
            {
                "dt": step,
                "quadrature_closure_error": abs(
                    reaction_mass + float(survival[-1]) - 1.0
                ),
            }
        )
    return rows


def _resolved_endpoint_audit(family: MatchedFamily, theta: float) -> dict:
    """Classify endpoint modes with an explicit amplitude-resolution rule.

    Every sign-changing stationary point detected by the declared scan is
    retained.  A secondary maximum is called resolved only when its height is
    at least three percent of the larger maximum and the intervening valley is
    below 95 percent of the smaller maximum.  This separates tiny reflection
    ripples on the even grids from the patterned endpoint without deleting the
    detected ripples from the record.  Only exact one-maximum/no-minimum and
    exact alternating two-maximum/one-minimum topologies are mapped to resolved
    unimodal or bimodal labels; every higher-order or non-alternating topology
    fails closed as ``resolved_other``.  The scan does not certify the absence
    of tangential or narrower roots between sample points.
    """

    times = np.linspace(0.0, 45.0, 451)
    density, derivative, survival = _uniform_series(family, theta, times)
    points = _stationary_points_from_scan(family, theta, times, derivative)
    ordered_points = sorted(points, key=lambda point: float(point["time"]))
    maxima = [point for point in ordered_points if point["kind"] == "maximum"]
    minima = [point for point in ordered_points if point["kind"] == "minimum"]
    kinds = [str(point["kind"]) for point in ordered_points]
    alternating_topology = bool(
        kinds
        and kinds[0] == "maximum"
        and kinds[-1] == "maximum"
        and len(maxima) == len(minima) + 1
        and all(left != right for left, right in zip(kinds[:-1], kinds[1:]))
    )
    strict_classification = (
        "strict_unimodal"
        if len(maxima) == 1 and not minima
        else "strict_bimodal"
        if len(maxima) == 2 and len(minima) == 1
        else "other"
    )
    pair_audits: list[dict[str, float | bool]] = []
    if alternating_topology:
        for index in range(0, len(ordered_points) - 2, 2):
            left_peak, valley, right_peak = ordered_points[index : index + 3]
            smaller_peak = min(
                float(left_peak["density"]), float(right_peak["density"])
            )
            larger_peak = max(
                float(left_peak["density"]), float(right_peak["density"])
            )
            pair_peak_ratio = smaller_peak / larger_peak
            pair_valley_ratio = float(valley["density"]) / smaller_peak
            pair_audits.append(
                {
                    "left_peak_time": float(left_peak["time"]),
                    "valley_time": float(valley["time"]),
                    "right_peak_time": float(right_peak["time"]),
                    "peak_height_ratio": pair_peak_ratio,
                    "valley_ratio": pair_valley_ratio,
                    "resolved": bool(
                        pair_peak_ratio >= MIN_RESOLVED_PEAK_RATIO
                        and pair_valley_ratio <= MAX_RESOLVED_VALLEY_RATIO
                    ),
                }
            )
    resolved_pair_count = sum(bool(pair["resolved"]) for pair in pair_audits)
    exact_unimodal_topology = (
        alternating_topology and len(maxima) == 1 and len(minima) == 0
    )
    exact_bimodal_topology = (
        alternating_topology and len(maxima) == 2 and len(minima) == 1
    )
    if exact_unimodal_topology:
        resolved_classification = "resolved_unimodal"
    elif exact_bimodal_topology and resolved_pair_count == 0:
        resolved_classification = "resolved_unimodal"
    elif exact_bimodal_topology and resolved_pair_count == 1:
        resolved_classification = "resolved_bimodal"
    else:
        resolved_classification = "resolved_other"
    strongest_pair = max(
        pair_audits,
        key=lambda pair: float(pair["peak_height_ratio"]),
        default=None,
    )
    peak_ratio = (
        0.0 if strongest_pair is None else float(strongest_pair["peak_height_ratio"])
    )
    valley_ratio = (
        None if strongest_pair is None else float(strongest_pair["valley_ratio"])
    )
    return {
        "grid": [family.grid.nx, family.grid.ny],
        "theta": theta,
        "tube_count": family.tube_count,
        "near_count": family.near_count,
        "far_count": family.far_count,
        "kappa_bar": family.kappa_bar,
        "matched_budget": family.budget,
        "stationary_point_count": len(ordered_points),
        "strict_mode_count": len(maxima),
        "strict_minimum_count": len(minima),
        "stationary_topology_alternating": alternating_topology,
        "strict_stationary_classification": strict_classification,
        "resolved_classification": resolved_classification,
        "resolved_adjacent_pair_count": resolved_pair_count,
        "adjacent_peak_pair_audits": pair_audits,
        "stationary_points": ordered_points,
        "secondary_peak_ratio": peak_ratio,
        "valley_ratio": valley_ratio,
        "tail_at_45": float(survival[-1]),
        "tail_at_480": float(_state(family, TAIL_TIME, theta).sum()),
    }


def _write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _write_json(path: Path, payload: object) -> None:
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _figure(
    grid_rows: list[dict],
    archives: dict[tuple[int, int], dict[str, np.ndarray]],
    endpoint_robustness: list[dict],
    pdf_path: Path,
    png_path: Path,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 8.0))

    ax = axes[0, 0]
    ax.set_aspect("equal")
    for centre, radius, color, label in (
        (NEAR_CENTRE, NEAR_RADIUS, "#d95f02", r"near $\kappa=0.5$"),
        (FAR_CENTRE, FAR_RADIUS, "#7570b3", r"far $\kappa=15$"),
    ):
        ax.add_patch(plt.Circle(centre, radius, color=color, alpha=0.24, label=label))
        ax.scatter(*centre, marker="*", color=color, s=80)
    ax.scatter(*START_ONE, color="#1b9e77", s=55, label="start 1")
    ax.scatter(*START_TWO, color="#66a61e", s=55, label="start 2")
    ax.set(
        xlim=(-0.06, 1.02),
        ylim=(0.0, 1.0),
        xlabel="x",
        ylabel="y",
        title="(a) matched-budget geometry",
    )
    ax.legend(frameon=False, fontsize=7, loc="upper right")

    ax = axes[0, 1]
    colors = {
        (9, 5): "#d95f02",
        (11, 7): "#1b9e77",
        (13, 9): "#377eb8",
    }
    endpoint_by_theta = {
        theta: sorted(
            (row for row in endpoint_robustness if row["theta"] == theta),
            key=lambda row: row["grid"][0],
        )
        for theta in (0.0, 1.0)
    }
    for theta, marker, color, label in (
        (0.0, "o", "#e41a1c", "homogeneous"),
        (1.0, "s", "#377eb8", "patterned"),
    ):
        rows = endpoint_by_theta[theta]
        ax.plot(
            np.arange(len(rows)),
            [row["secondary_peak_ratio"] for row in rows],
            marker=marker,
            color=color,
            lw=1.5,
            label=label,
        )
    labels = [
        f"{row['grid'][0]}x{row['grid'][1]}"
        for row in endpoint_by_theta[0.0]
    ]
    ax.axhline(
        MIN_RESOLVED_PEAK_RATIO,
        color="black",
        ls=":",
        lw=1.0,
        label="3% threshold",
    )
    ax.set_xticks(np.arange(len(labels)), labels, rotation=25)
    ax.set(
        xlabel="physical grid",
        ylabel="secondary / primary peak height",
        ylim=(-0.004, 0.125),
        title="(b) endpoint robustness",
    )
    ax.legend(frameon=False, fontsize=7, loc="upper left")

    ax = axes[1, 0]
    for row in grid_rows:
        key = tuple(row["grid"])
        archive = archives[key]
        for label, linestyle in (
            ("subcritical", "--"),
            ("critical", ":"),
            ("supercritical", "-"),
        ):
            ax.plot(
                archive["local_times"],
                1e4 * archive[f"local_{label}_f_t"],
                color=colors[key],
                ls=linestyle,
                lw=1.45,
                label=f"{key[0]}x{key[1]} {label}",
            )
    ax.axhline(0.0, color="black", lw=0.8)
    ax.text(
        0.03,
        0.04,
        r"orange/green/blue: $9\!\times\!5$/$11\!\times\!7$/$13\!\times\!9$"
        "\n-- sub; : fold; solid super",
        transform=ax.transAxes,
        fontsize=7.5,
        va="bottom",
    )
    ax.set(
        xlabel="time",
        ylabel=r"$10^4\,\partial_t f$",
        title="(c) derivative tangency",
    )

    ax = axes[1, 1]
    reference_mu = SCALING_MU[2]
    for row in grid_rows:
        key = tuple(row["grid"])
        scale = row["scaling_rows"]
        mu = np.asarray([value["mu"] for value in scale])
        separation = np.asarray([value["separation"] for value in scale])
        prominence = np.asarray([value["prominence"] for value in scale])
        reference = int(np.argmin(np.abs(mu - reference_mu)))
        ax.loglog(
            mu,
            separation / separation[reference],
            "o-",
            color=colors[key],
            ms=4,
            label=f"{key[0]}x{key[1]} sep.",
        )
        ax.loglog(
            mu,
            prominence / prominence[reference],
            "s--",
            color=colors[key],
            ms=4,
            label="_nolegend_",
        )
    reference = SCALING_MU / reference_mu
    ax.loglog(SCALING_MU, reference**0.5, color="black", lw=1.0, label="slope 1/2")
    ax.loglog(
        SCALING_MU,
        reference**1.5,
        color="0.45",
        lw=1.0,
        label="slope 3/2",
    )
    ax.set(
        xlabel=r"$\mu=\theta-\theta_c$",
        ylabel="normalized fold observable",
        title="(d) local fold scaling",
    )
    ax.legend(frameon=False, fontsize=6, ncol=3, loc="upper left")

    for ax in axes.reshape(-1):
        ax.grid(alpha=0.18)
    enforce_publication_graphics(fig)
    fig.tight_layout()
    temporary_pdf = pdf_path.with_name(f".{pdf_path.stem}.tmp{pdf_path.suffix}")
    temporary_png = png_path.with_name(f".{png_path.stem}.tmp{png_path.suffix}")
    fig.savefig(temporary_pdf)
    fig.savefig(temporary_png, dpi=300)
    temporary_pdf.replace(pdf_path)
    temporary_png.replace(png_path)
    plt.close(fig)


def main() -> None:
    grid_rows: list[dict] = []
    csv_rows: list[dict] = []
    archives: dict[tuple[int, int], dict[str, np.ndarray]] = {}
    families: dict[tuple[int, int], MatchedFamily] = {}
    folds: dict[tuple[int, int], dict] = {}

    for nx, ny in GRIDS:
        family = _build_family(nx, ny)
        families[(nx, ny)] = family
        fold, fold_jacobian = _solve_fold(family)
        folds[(nx, ny)] = fold
        scaling, scaling_rows = _scaling_rows(family, fold)
        held_out, local_archive = _held_out_metrics(family, fold)
        endpoint_zero, archive_zero = _endpoint_metrics(family, 0.0)
        endpoint_one, archive_one = _endpoint_metrics(family, 1.0)
        time_steps = {
            "theta0": _time_step_metrics(family, 0.0),
            "theta1": _time_step_metrics(family, 1.0),
        }

        budget_theta0 = float(np.dot(family.matching_weights, family.k0))
        budget_theta1 = float(
            np.dot(family.matching_weights, family.k0 + family.ktheta)
        )
        row = {
            "grid": [nx, ny],
            "single_walker_states": family.grid.state_count,
            "product_states": family.initial.size,
            "initial_distribution": family.initial_diagnostics,
            "spacing_x": family.grid.spacing_x,
            "spacing_y": family.grid.spacing_y,
            "tube_count": family.tube_count,
            "near_count": family.near_count,
            "far_count": family.far_count,
            "budget_measure": family.budget_measure,
            "tube_measure": family.tube_measure,
            "near_measure": family.near_measure,
            "far_measure": family.far_measure,
            "kappa_bar": family.kappa_bar,
            "matched_budget": family.budget,
            "budget_theta0": budget_theta0,
            "budget_theta1": budget_theta1,
            "budget_invariance_error": max(
                abs(budget_theta0 - family.budget),
                abs(budget_theta1 - family.budget),
            ),
            "fold": fold,
            "fold_jacobian": fold_jacobian.tolist(),
            "held_out": held_out,
            "scaling": scaling,
            "scaling_rows": scaling_rows,
            "endpoints": {
                "theta0": endpoint_zero,
                "theta1": endpoint_one,
            },
            "time_step_convergence": time_steps,
            "resolution_diagnostics": _resolution_diagnostics(family.grid),
        }
        grid_rows.append(row)
        archive = {
            "theta0_times": archive_zero["times"],
            "theta0_density": archive_zero["density"],
            "theta0_derivative": archive_zero["derivative"],
            "theta0_survival": archive_zero["survival"],
            "theta1_times": archive_one["times"],
            "theta1_density": archive_one["density"],
            "theta1_derivative": archive_one["derivative"],
            "theta1_survival": archive_one["survival"],
            "local_times": local_archive["times"],
        }
        for label in ("subcritical", "critical", "supercritical"):
            archive[f"local_{label}_density"] = local_archive[f"{label}_density"]
            archive[f"local_{label}_f_t"] = local_archive[f"{label}_f_t"]
        archives[(nx, ny)] = archive

        csv_rows.append(
            {
                "record_type": "fold",
                "nx": nx,
                "ny": ny,
                "theta": fold["theta"],
                "time": fold["time"],
                "f_t_residual": fold["f_t_residual"],
                "f_tt_residual": fold["f_tt_residual"],
                "f_ttt": fold["f_ttt"],
                "f_ttheta": fold["f_ttheta"],
                "matched_budget": family.budget,
                "kappa_bar": family.kappa_bar,
            }
        )
        for value in scaling_rows:
            csv_rows.append(
                {
                    "record_type": "scaling",
                    "nx": nx,
                    "ny": ny,
                    **value,
                }
            )
        for endpoint_label, endpoint in (
            ("theta0", endpoint_zero),
            ("theta1", endpoint_one),
        ):
            csv_rows.append(
                {
                    "record_type": "endpoint",
                    "nx": nx,
                    "ny": ny,
                    "endpoint": endpoint_label,
                    "theta": endpoint["theta"],
                    "classification": endpoint["classification"],
                    "tail_at_480": endpoint["tail_at_480"],
                    "peak_height_ratio": endpoint.get("peak_height_ratio", ""),
                    "valley_ratio": endpoint.get("valley_ratio", ""),
                }
            )
        for endpoint_label, values in time_steps.items():
            for value in values:
                csv_rows.append(
                    {
                        "record_type": "time_step",
                        "nx": nx,
                        "ny": ny,
                        "endpoint": endpoint_label,
                        **value,
                    }
                )

    endpoint_robustness: list[dict] = []
    for nx, ny in ENDPOINT_GRIDS:
        family = families.get((nx, ny))
        if family is None:
            family = _build_family(nx, ny)
            families[(nx, ny)] = family
        for theta in (0.0, 1.0):
            endpoint = _resolved_endpoint_audit(family, theta)
            endpoint_robustness.append(endpoint)
            csv_rows.append(
                {
                    "record_type": "endpoint_robustness",
                    "nx": nx,
                    "ny": ny,
                    "theta": theta,
                    "classification": endpoint["resolved_classification"],
                    "strict_classification": endpoint[
                        "strict_stationary_classification"
                    ],
                    "peak_height_ratio": endpoint["secondary_peak_ratio"],
                    "valley_ratio": endpoint["valley_ratio"],
                    "tail_at_480": endpoint["tail_at_480"],
                }
            )

    fold_topology = _fold_topology_diagnostics(families)
    budget_measure_sensitivity = _budget_measure_sensitivity(families, folds)
    for row in budget_measure_sensitivity["rows"]:
        weighted = row["product_trapezoidal_budget"]
        weighted_fold = weighted["fold"]
        csv_rows.append(
            {
                "record_type": "budget_measure_sensitivity",
                "nx": row["grid"][0],
                "ny": row["grid"][1],
                "budget_measure": "product_trapezoidal",
                "kappa_bar": weighted["kappa_bar"],
                "theta": weighted_fold["theta"],
                "time": weighted_fold["time"],
                "f_t_residual": weighted_fold["f_t_residual"],
                "f_tt_residual": weighted_fold["f_tt_residual"],
                "f_ttt": weighted_fold["f_ttt"],
                "f_ttheta": weighted_fold["f_ttheta"],
                "matched_budget": weighted["weighted_budget_theta0"],
            }
        )

    theta_values = [float(row["fold"]["theta"]) for row in grid_rows]
    time_values = [float(row["fold"]["time"]) for row in grid_rows]
    theta_difference = max(theta_values) - min(theta_values)
    time_difference = max(time_values) - min(time_values)
    comparison = {
        "theta_c_absolute_difference": theta_difference,
        "theta_c_range": theta_difference,
        "theta_c_values": theta_values,
        "time_c_absolute_difference": time_difference,
        "physical_fold_grids": [row["grid"] for row in grid_rows],
        "fold_location_tolerance": 0.05,
        "fold_location_grid_converged": theta_difference <= 0.05,
        "endpoint_modality_consistent": all(
            row["resolved_classification"]
            == ("resolved_unimodal" if row["theta"] == 0.0 else "resolved_bimodal")
            for row in endpoint_robustness
        ),
        "publication_gate_status": "mechanism_certificate_only",
        "promoted_claim": (
            "under the declared 3% peak-height and 95% valley resolution rule, "
            "matched-budget homogeneous and patterned endpoints are resolved-unimodal "
            "and resolved-bimodal, respectively, on five tested grids"
        ),
        "withheld_claim": (
            "the numerical value of theta_c is grid- and budget-measure-sensitive, "
            "is not grid-converged, and is not a continuum fold location"
        ),
    }
    if not comparison["endpoint_modality_consistent"]:
        raise RuntimeError(
            "M2D-F endpoint topology or resolved-class contract failed: "
            + json.dumps(endpoint_robustness, sort_keys=True)
        )
    metrics = {
        "schema_version": 1,
        "claim_scope": "finite-grid matched-budget mechanism certificate",
        "derivative_evidence": (
            "sparse generator actions and augmented matrix exponentials; no "
            "sampled finite differences are used for the fold equations"
        ),
        "model": {
            "family_id": "M2D-F",
            "domain": [1.0, 1.0],
            "boundary": "reflecting by omitted outward CTMC jumps",
            "reaction_model": "finite-radius Doi volume sink",
            "reaction_radius": REACTION_RADIUS,
            "start_one": list(START_ONE),
            "start_two": list(START_TWO),
            "walker_one": WALKER_ONE,
            "walker_two": WALKER_TWO,
            "initial_distribution": (
                "hierarchical contact-safe selector: minimum physical Euclidean "
                "spread on the smallest feasible local stencil, followed by a "
                "strictly convex closest-to-product QP on the optimal LP face; "
                "exact product-bilinear return when already contact-safe"
            ),
            "near_patch": {
                "centre": list(NEAR_CENTRE),
                "radius": NEAR_RADIUS,
                "rate": NEAR_RATE,
            },
            "far_patch": {
                "centre": list(FAR_CENTRE),
                "radius": FAR_RADIUS,
                "rate": FAR_RATE,
            },
            "continuation": (
                "kappa_theta=(1-theta)kappa_bar_grid+theta[0.5 I_near+15 I_far]"
            ),
        },
        "grids": grid_rows,
        "endpoint_resolution_rule": {
            "minimum_secondary_peak_ratio": MIN_RESOLVED_PEAK_RATIO,
            "maximum_valley_ratio": MAX_RESOLVED_VALLEY_RATIO,
            "detected_sign_changing_stationary_points_are_retained": True,
            "all_adjacent_max_min_max_pairs_are_audited": True,
            "unexpected_or_non_alternating_topology_fails_closed": True,
            "exhaustive_stationary_point_count_claimed": False,
        },
        "endpoint_robustness": endpoint_robustness,
        "grid_comparison": comparison,
        "fold_topology_diagnostics": fold_topology,
        "budget_measure_sensitivity": budget_measure_sensitivity,
    }

    metrics_json = DATA / "finite_radius_2d_fold_metrics.json"
    metrics_csv = DATA / "finite_radius_2d_fold_metrics.csv"
    series_npz = DATA / "finite_radius_2d_fold_series.npz"
    figure_pdf = FIGURES / "finite_radius_2d_fold_validation.pdf"
    figure_png = FIGURES / "finite_radius_2d_fold_validation.png"
    _write_json(metrics_json, metrics)
    _write_csv(metrics_csv, csv_rows)
    series_tmp = series_npz.with_name(f".{series_npz.stem}.tmp.npz")
    np.savez_compressed(
        series_tmp,
        **{
            f"g{nx}x{ny}_{name}": values
            for (nx, ny), archive in archives.items()
            for name, values in archive.items()
        },
    )
    series_tmp.replace(series_npz)
    _figure(grid_rows, archives, endpoint_robustness, figure_pdf, figure_png)

    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=["python", str(HERE.relative_to(REPO))],
        model_spec={
            "family_id": "M2D-F",
            "fold_grids": [list(grid) for grid in GRIDS],
            "endpoint_grids": [list(grid) for grid in ENDPOINT_GRIDS],
            "discretization": "boundary-node nearest-neighbour lattice CTMC with binary masks",
            "reaction_radius": REACTION_RADIUS,
            "catalytic_coordinate": "arithmetic midpoint C_eta with eta=0.5",
            "start_one": START_ONE,
            "start_two": START_TWO,
            "walker_one": WALKER_ONE,
            "walker_two": WALKER_TWO,
            "initial_distribution": (
                "hierarchical contact-safe selector: minimum physical Euclidean "
                "spread on the smallest feasible local stencil, followed by a "
                "strictly convex closest-to-product QP on the optimal LP face; "
                "exact product-bilinear return when already contact-safe"
            ),
            "near_patch": {
                "centre": NEAR_CENTRE,
                "radius": NEAR_RADIUS,
                "rate": NEAR_RATE,
            },
            "far_patch": {
                "centre": FAR_CENTRE,
                "radius": FAR_RADIUS,
                "rate": FAR_RATE,
            },
            "budget_matching": {
                "principal": "exact unweighted sum over encounter-tube Markov states",
                "sensitivity": (
                    "exact matching under a tensor-product boundary-node "
                    "trapezoidal/control-volume quadrature on the four-dimensional "
                    "product-state grid"
                ),
                "continuum_finite_a_reference": _continuum_budget_reference(),
            },
            "endpoint_resolution_rule": {
                "minimum_secondary_peak_ratio": MIN_RESOLVED_PEAK_RATIO,
                "maximum_valley_ratio": MAX_RESOLVED_VALLEY_RATIO,
            },
            "fold_initial_guesses": {
                f"{nx}x{ny}": list(FOLD_INITIAL_GUESSES[(nx, ny)])
                for nx, ny in GRIDS
            },
            "weighted_fold_initial_guesses": {
                f"{nx}x{ny}": list(WEIGHTED_FOLD_INITIAL_GUESSES[(nx, ny)])
                for nx, ny in GRIDS
            },
            "even_grid_topology_diagnostics": {
                "10x6_curvature_scan": {
                    "time_interval": [0.01, 40.0],
                    "time_points": 401,
                    "theta_interval": [-0.2, 0.1],
                    "theta_points": 31,
                },
                "10x6_bounded_least_squares": {
                    "time_bounds": [8.0, 25.0],
                    "theta_bounds": [-0.2, 0.0],
                    "starts": [
                        [15.3, -0.0957],
                        [15.0, -0.1],
                        [16.0, -0.09],
                        [12.0, -0.13],
                    ],
                },
                "12x8_extrapolated_initial_guess": [18.27, -0.0616],
            },
        },
        dependencies=[
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter2d.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
            REPORT / "notes" / "finite_radius_2d_matched_fold.md",
        ],
        outputs=[metrics_json, metrics_csv, series_npz, figure_pdf, figure_png],
        horizon={
            "shape_tmax": SHAPE_TMAX,
            "shape_dt": SHAPE_DT,
            "quadrature_tmax": QUADRATURE_TMAX,
            "quadrature_steps": list(QUADRATURE_STEPS),
            "tail_check_time": TAIL_TIME,
            "scaling_mu": SCALING_MU.tolist(),
            "held_out_delta": HELD_OUT_DELTA,
        },
    )
    manifest_path = DATA / "finite_radius_2d_fold.manifest.json"
    manifest_tmp = DATA / ".finite_radius_2d_fold.manifest.tmp.json"
    write_manifest(manifest_tmp, manifest)
    manifest_tmp.replace(manifest_path)
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
