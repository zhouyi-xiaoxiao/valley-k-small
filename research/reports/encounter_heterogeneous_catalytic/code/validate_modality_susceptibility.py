#!/usr/bin/env python3
"""Validate a budget-projected modality susceptibility for killed CTMCs.

For a live-state row generator

    T(k) = L - diag(k),       f(t;k) = alpha exp(T(k)t) k,

the directional derivative of ``f_t`` with respect to an additive killing
perturbation ``h`` is evaluated in three independent ways:

1. the exact Frechet derivative of the finite matrix exponential;
2. an adjoint/Duhamel convolution kernel;
3. a held-out five-point finite difference.

The resulting gradient is then projected onto a fixed-budget hyperplane and
the closed-form optimal local redistribution is checked against random
feasible directions.  A second calculation applies the same identity to the
two reactive states of the manuscript's finite encounter CTMC at its saved
modality fold.  This is an exact finite-state design identity, not a continuum
optimal-control theorem and not a finite-amplitude guarantee of multimodality.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse
from scipy.linalg import expm, expm_frechet
from scipy.sparse.linalg import expm_multiply
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
DATA.mkdir(parents=True, exist_ok=True)

SEED = 20260713
RANDOM_DIRECTION_COUNT = 256
RANDOM_OPTIMIZATION_COUNT = 20_000
GAUSS_LEGENDRE_ORDER = 160
FINITE_DIFFERENCE_STEP = 2.0e-4


def _load_fold_module():
    path = HERE.with_name("validate_gig_fold.py")
    spec = importlib.util.spec_from_file_location("encounter_gig_fold_for_design", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _transport_generator(rng: np.random.Generator, size: int) -> np.ndarray:
    """Return a deterministic irreducible row-conservative transport generator."""

    off_diagonal = np.zeros((size, size), dtype=float)
    for index in range(size):
        off_diagonal[index, (index + 1) % size] += rng.uniform(0.35, 1.15)
        off_diagonal[index, (index - 1) % size] += rng.uniform(0.35, 1.15)
    for _ in range(2 * size):
        source, target = rng.choice(size, size=2, replace=False)
        off_diagonal[source, target] += rng.uniform(0.02, 0.25)
    generator = off_diagonal.copy()
    generator[np.diag_indices(size)] = -off_diagonal.sum(axis=1)
    if not np.allclose(generator.sum(axis=1), 0.0, atol=2e-15):
        raise RuntimeError("transport generator lost row conservation")
    return generator


def killed_generator(transport: np.ndarray, killing: np.ndarray) -> np.ndarray:
    return np.asarray(transport, dtype=float) - np.diag(np.asarray(killing, dtype=float))


def density_time_derivative(
    transport: np.ndarray,
    killing: np.ndarray,
    initial: np.ndarray,
    time: float,
) -> float:
    """Evaluate ``f_t=alpha exp(Tt) T k``."""

    generator = killed_generator(transport, killing)
    return float(initial @ expm(generator * time) @ generator @ killing)


def frechet_ft_direction(
    transport: np.ndarray,
    killing: np.ndarray,
    initial: np.ndarray,
    time: float,
    direction: np.ndarray,
) -> float:
    """Exact finite-matrix directional derivative of ``f_t``."""

    generator = killed_generator(transport, killing)
    generator_direction = -np.diag(direction)
    exponential, exponential_direction = expm_frechet(
        generator * time,
        generator_direction * time,
        compute_expm=True,
    )
    observable = generator @ killing
    observable_direction = generator_direction @ killing + generator @ direction
    return float(
        initial @ exponential_direction @ observable
        + initial @ exponential @ observable_direction
    )


def frechet_ft_gradient(
    transport: np.ndarray,
    killing: np.ndarray,
    initial: np.ndarray,
    time: float,
) -> np.ndarray:
    identity = np.eye(killing.size)
    return np.asarray(
        [
            frechet_ft_direction(transport, killing, initial, time, basis)
            for basis in identity
        ],
        dtype=float,
    )


def duhamel_ft_gradient(
    transport: np.ndarray,
    killing: np.ndarray,
    initial: np.ndarray,
    time: float,
) -> np.ndarray:
    """Evaluate the componentwise Duhamel/adjoint kernel by Gauss quadrature."""

    generator = killed_generator(transport, killing)
    exponential = expm(generator * time)
    direct = initial @ exponential @ generator - killing * (initial @ exponential)

    nodes, weights = np.polynomial.legendre.leggauss(GAUSS_LEGENDRE_ORDER)
    quadrature_times = 0.5 * time * (nodes + 1.0)
    quadrature_weights = 0.5 * time * weights
    convolution = np.zeros_like(killing, dtype=float)
    terminal_observable = generator @ killing
    for sample_time, weight in zip(quadrature_times, quadrature_weights, strict=True):
        left = initial @ expm(generator * (time - sample_time))
        right = expm(generator * sample_time) @ terminal_observable
        convolution += weight * left * right
    return np.asarray(direct - convolution, dtype=float)


def five_point_direction(
    transport: np.ndarray,
    killing: np.ndarray,
    initial: np.ndarray,
    time: float,
    direction: np.ndarray,
    step: float = FINITE_DIFFERENCE_STEP,
) -> float:
    if np.min(killing - 2.0 * step * np.abs(direction)) <= 0.0:
        raise ValueError("finite-difference perturbation leaves positive killing cone")

    def value(multiplier: float) -> float:
        return density_time_derivative(
            transport,
            killing + multiplier * step * direction,
            initial,
            time,
        )

    return float((-value(2.0) + 8.0 * value(1.0) - 8.0 * value(-1.0) + value(-2.0)) / (12.0 * step))


def budget_projected_optimum(
    gradient: np.ndarray,
    budget_weights: np.ndarray,
    metric_diagonal: np.ndarray,
) -> tuple[np.ndarray, float, float]:
    """Maximize ``g.h`` subject to ``c.h=0`` and ``h'Mh=1``."""

    inverse_metric = 1.0 / metric_diagonal
    multiplier = float(
        np.dot(budget_weights * inverse_metric, gradient)
        / np.dot(budget_weights * inverse_metric, budget_weights)
    )
    projected_covector = gradient - multiplier * budget_weights
    raw_direction = inverse_metric * projected_covector
    norm = float(np.sqrt(np.dot(metric_diagonal * raw_direction, raw_direction)))
    if not norm > 0.0:
        raise RuntimeError("modality gradient is parallel to the budget covector")
    direction = raw_direction / norm
    optimum = float(np.dot(gradient, direction))
    return direction, multiplier, optimum


def _random_budget_direction(
    rng: np.random.Generator,
    budget_weights: np.ndarray,
    metric_diagonal: np.ndarray,
) -> np.ndarray:
    proposal = rng.normal(size=budget_weights.size)
    inverse_metric_budget = budget_weights / metric_diagonal
    proposal -= inverse_metric_budget * (
        np.dot(budget_weights, proposal)
        / np.dot(budget_weights, inverse_metric_budget)
    )
    norm = float(np.sqrt(np.dot(metric_diagonal * proposal, proposal)))
    if norm <= 1e-14:
        return _random_budget_direction(rng, budget_weights, metric_diagonal)
    return proposal / norm


def _finite_ctmc_validation() -> tuple[dict[str, Any], list[dict[str, float]]]:
    rng = np.random.default_rng(SEED)
    size = 11
    transport = _transport_generator(rng, size)
    killing = rng.uniform(0.18, 0.95, size=size)
    initial = rng.dirichlet(np.ones(size))
    time = 1.37
    budget_weights = rng.uniform(0.55, 1.65, size=size)
    metric_diagonal = rng.uniform(0.65, 1.85, size=size)

    frechet_gradient = frechet_ft_gradient(transport, killing, initial, time)
    duhamel_gradient = duhamel_ft_gradient(transport, killing, initial, time)
    gradient_scale = max(float(np.linalg.norm(frechet_gradient)), 1e-15)
    convolution_relative_error = float(
        np.linalg.norm(frechet_gradient - duhamel_gradient) / gradient_scale
    )

    direction_rows: list[dict[str, float]] = []
    maximum_fd_error = 0.0
    maximum_linearity_error = 0.0
    for index in range(RANDOM_DIRECTION_COUNT):
        direction = _random_budget_direction(rng, budget_weights, metric_diagonal)
        predicted = float(np.dot(frechet_gradient, direction))
        direct = frechet_ft_direction(transport, killing, initial, time, direction)
        finite_difference = five_point_direction(
            transport, killing, initial, time, direction
        )
        scale = max(abs(predicted), abs(direct), abs(finite_difference), 1e-12)
        linearity_error = abs(predicted - direct) / scale
        finite_difference_error = abs(predicted - finite_difference) / scale
        maximum_linearity_error = max(maximum_linearity_error, linearity_error)
        maximum_fd_error = max(maximum_fd_error, finite_difference_error)
        direction_rows.append(
            {
                "direction_index": float(index),
                "predicted_gradient_dot_direction": predicted,
                "frechet_directional_derivative": direct,
                "five_point_directional_derivative": finite_difference,
                "relative_linearity_error": linearity_error,
                "relative_finite_difference_error": finite_difference_error,
                "budget_residual": float(np.dot(budget_weights, direction)),
                "metric_norm_residual": float(
                    np.dot(metric_diagonal * direction, direction) - 1.0
                ),
            }
        )

    optimum_direction, multiplier, optimum = budget_projected_optimum(
        frechet_gradient, budget_weights, metric_diagonal
    )
    random_responses = np.asarray(
        [
            np.dot(
                frechet_gradient,
                _random_budget_direction(rng, budget_weights, metric_diagonal),
            )
            for _ in range(RANDOM_OPTIMIZATION_COUNT)
        ]
    )
    best_random = float(np.max(random_responses))

    permutation = rng.permutation(size)
    permuted_transport = transport[np.ix_(permutation, permutation)]
    permuted_gradient = frechet_ft_gradient(
        permuted_transport,
        killing[permutation],
        initial[permutation],
        time,
    )
    permutation_error = float(
        np.max(np.abs(permuted_gradient - frechet_gradient[permutation]))
        / max(np.max(np.abs(frechet_gradient)), 1e-15)
    )

    summary = {
        "state_count": size,
        "time": time,
        "seed": SEED,
        "frechet_gradient": frechet_gradient.tolist(),
        "duhamel_gradient": duhamel_gradient.tolist(),
        "duhamel_relative_l2_error": convolution_relative_error,
        "held_out_direction_count": RANDOM_DIRECTION_COUNT,
        "maximum_gradient_linearity_relative_error": maximum_linearity_error,
        "maximum_five_point_relative_error": maximum_fd_error,
        "optimal_direction": optimum_direction.tolist(),
        "budget_multiplier": multiplier,
        "optimal_response": optimum,
        "optimal_budget_residual": float(np.dot(budget_weights, optimum_direction)),
        "optimal_metric_norm_residual": float(
            np.dot(metric_diagonal * optimum_direction, optimum_direction) - 1.0
        ),
        "random_feasible_direction_count": RANDOM_OPTIMIZATION_COUNT,
        "best_random_response": best_random,
        "best_random_over_optimum": best_random / optimum,
        "permutation_equivariance_relative_error": permutation_error,
        "killing_minimum": float(np.min(killing)),
    }
    return summary, direction_rows


def _sparse_directional_ft(
    generator: sparse.csr_matrix,
    killing: np.ndarray,
    initial: np.ndarray,
    time: float,
    direction: np.ndarray,
) -> float:
    generator_direction = sparse.diags(-direction, format="csr")
    zero = sparse.csr_matrix(generator.shape)
    augmented = sparse.bmat(
        [[generator.T, zero], [generator_direction.T, generator.T]],
        format="csr",
    )
    state_and_sensitivity = expm_multiply(
        augmented * time,
        np.concatenate([initial, np.zeros_like(initial)]),
    )
    state, sensitivity = np.split(state_and_sensitivity, 2)
    return float(
        np.dot(sensitivity, generator @ killing)
        + np.dot(state, generator_direction @ killing + generator @ direction)
    )


def _encounter_fold_validation() -> dict[str, Any]:
    fold_module = _load_fold_module()
    fold, model = fold_module.locate_physical_fold()
    support = (fold_module.NEAR_INDEX, fold_module.FAR_INDEX)
    basis_gradients = []
    for state_index in support:
        direction = np.zeros_like(model.total_rate)
        direction[state_index] = 1.0
        basis_gradients.append(
            _sparse_directional_ft(
                model.killed_generator,
                model.total_rate,
                model.initial,
                float(fold["time"]),
                direction,
            )
        )
    gradient = np.asarray(basis_gradients, dtype=float)
    theta_chain_rule = float(gradient[0] * model.kappa_near)
    saved_transversality = float(fold["time_parameter_transversality"])

    fixed_budget_direction = np.asarray([1.0, -1.0]) / np.sqrt(2.0)
    fixed_budget_response = float(np.dot(gradient, fixed_budget_direction))
    direct_direction = np.zeros_like(model.total_rate)
    direct_direction[support[0]] = fixed_budget_direction[0]
    direct_direction[support[1]] = fixed_budget_direction[1]
    direct_fixed_budget_response = _sparse_directional_ft(
        model.killed_generator,
        model.total_rate,
        model.initial,
        float(fold["time"]),
        direct_direction,
    )

    return {
        "fold_time": float(fold["time"]),
        "fold_theta": float(fold["theta_log_kappa_near_over_far"]),
        "kappa_near": float(model.kappa_near),
        "kappa_far": float(model.kappa_far),
        "reactive_support_gradient": {
            "near": float(gradient[0]),
            "far": float(gradient[1]),
        },
        "theta_chain_rule_transversality": theta_chain_rule,
        "saved_augmented_transversality": saved_transversality,
        "theta_chain_rule_relative_error": abs(theta_chain_rule - saved_transversality)
        / max(abs(saved_transversality), 1e-15),
        "fixed_state_sum_budget_direction": fixed_budget_direction.tolist(),
        "fixed_state_sum_budget_residual": float(np.sum(fixed_budget_direction)),
        "fixed_state_sum_budget_transversality": fixed_budget_response,
        "fixed_state_sum_direct_transversality": direct_fixed_budget_response,
        "fixed_state_sum_linearity_relative_error": abs(
            fixed_budget_response - direct_fixed_budget_response
        )
        / max(abs(direct_fixed_budget_response), 1e-15),
        "interpretation": (
            "The projected two-site direction is the locally most responsive "
            "unit Euclidean redistribution on the declared reactive support."
        ),
    }


def _write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    finite, direction_rows = _finite_ctmc_validation()
    encounter = _encounter_fold_validation()
    summary = {
        "evidence_level": "exact finite-state sensitivity identity with numerical cross-checks",
        "claim": (
            "The budget-projected gradient gives the locally optimal infinitesimal "
            "killing redistribution for changing f_t at a declared time."
        ),
        "not_claimed": [
            "a continuum optimal-control theorem",
            "a finite-amplitude globally optimal catalyst pattern",
            "that every nonzero projected response creates a resolved mode",
            "novelty of Frechet, Duhamel, or adjoint sensitivity methods themselves",
        ],
        "finite_ctmc_cross_checks": finite,
        "encounter_fold_application": encounter,
        "acceptance_contract": {
            "duhamel_relative_l2_error_max": 2e-11,
            "gradient_linearity_relative_error_max": 2e-11,
            "five_point_relative_error_max": 2e-7,
            "permutation_equivariance_relative_error_max": 2e-11,
            "theta_chain_rule_relative_error_max": 2e-9,
            "fixed_budget_linearity_relative_error_max": 2e-10,
            "random_response_must_not_exceed_closed_form_optimum": True,
        },
    }
    contract = summary["acceptance_contract"]
    failures = []
    if finite["duhamel_relative_l2_error"] > contract["duhamel_relative_l2_error_max"]:
        failures.append("Duhamel kernel disagrees with Frechet gradient")
    if finite["maximum_gradient_linearity_relative_error"] > contract["gradient_linearity_relative_error_max"]:
        failures.append("basis gradient disagrees with Frechet directional derivative")
    if finite["maximum_five_point_relative_error"] > contract["five_point_relative_error_max"]:
        failures.append("held-out five-point derivative disagrees with exact gradient")
    if finite["permutation_equivariance_relative_error"] > contract["permutation_equivariance_relative_error_max"]:
        failures.append("gradient is not permutation equivariant")
    if finite["best_random_response"] > finite["optimal_response"] * (1.0 + 2e-12):
        failures.append("random feasible direction exceeds closed-form optimum")
    if encounter["theta_chain_rule_relative_error"] > contract["theta_chain_rule_relative_error_max"]:
        failures.append("encounter theta chain rule disagrees with saved transversality")
    if encounter["fixed_state_sum_linearity_relative_error"] > contract["fixed_budget_linearity_relative_error_max"]:
        failures.append("two-site budget response fails linearity")
    if failures:
        raise RuntimeError("; ".join(failures))

    summary_path = DATA / "modality_susceptibility_summary.json"
    rows_path = DATA / "modality_susceptibility_directions.csv"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_csv(rows_path, direction_rows)
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=[sys.executable, str(HERE.relative_to(REPO))],
        model_spec={
            "finite_state_density": "f(t;k)=alpha exp((L-diag(k))t) k",
            "design_target": "directional derivative of f_t",
            "budget_constraint": "c^T h=0",
            "local_metric_constraint": "h^T M h=1",
            "seed": SEED,
            "encounter_application": "two reactive states at the saved finite CTMC fold",
        },
        classifier_spec={
            "exact_gradient": "basis Frechet derivatives",
            "independent_kernel": f"Duhamel convolution with {GAUSS_LEGENDRE_ORDER}-point Gauss-Legendre quadrature",
            "held_out_check": f"{RANDOM_DIRECTION_COUNT} budget-zero directions with five-point finite differences",
            "optimization_check": f"closed form versus {RANDOM_OPTIMIZATION_COUNT} random feasible directions",
            "claim_boundary": summary["evidence_level"],
        },
        dependencies=[
            HERE.with_name("validate_gig_fold.py"),
            REPORT / "notes" / "modality_susceptibility.md",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
        ],
        outputs=[summary_path, rows_path],
        horizon={"finite_ctmc_time": finite["time"], "encounter_fold_time": encounter["fold_time"]},
    )
    write_manifest(DATA / "modality_susceptibility.manifest.json", manifest)
    print(json.dumps({
        "duhamel_relative_l2_error": finite["duhamel_relative_l2_error"],
        "maximum_five_point_relative_error": finite["maximum_five_point_relative_error"],
        "best_random_over_optimum": finite["best_random_over_optimum"],
        "theta_chain_rule_relative_error": encounter["theta_chain_rule_relative_error"],
        "fixed_budget_transversality": encounter["fixed_state_sum_budget_transversality"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
