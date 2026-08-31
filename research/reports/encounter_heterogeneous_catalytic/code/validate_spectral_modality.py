#!/usr/bin/env python3
"""Validate the reversible spectral sign-variation modality diagnostic.

The mathematical zero-count bound is a direct corollary of the classical
generalized Descartes rule, not a new theorem.  This script tests its use as a
finite-model diagnostic on two production generators:

* the supercritical finite encounter CTMC, with three simple critical points;
* the coarse M2D-T generator, with five simple critical points.

It also records two adversarial counterexamples.  A four-stage
hypoexponential density has three spectral sign changes but only one mode, so
the condition is not sufficient.  A two-branch Erlang network feeding one
reactive state is bimodal, so killing-support rank does not bound mode count.
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
from scipy.linalg import eigh, expm
from scipy.optimize import brentq
from scipy.sparse.linalg import expm_multiply
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
DATA.mkdir(parents=True, exist_ok=True)

EIGENVALUE_GROUP_TOLERANCE = 2.0e-10
COEFFICIENT_RELATIVE_THRESHOLDS = (1e-12, 1e-10, 1e-8, 1e-6)


def _load_module(filename: str, name: str):
    path = HERE.with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _reversible_measure(generator: sparse.csr_matrix) -> tuple[np.ndarray, dict[str, float]]:
    """Recover reversible weights from off-diagonal detailed balance."""

    matrix = sparse.csr_matrix(generator)
    size = matrix.shape[0]
    log_weight = np.full(size, np.nan)
    log_weight[0] = 0.0
    stack = [0]
    maximum_log_balance_error = 0.0
    while stack:
        source = stack.pop()
        start, stop = matrix.indptr[source : source + 2]
        for target, forward in zip(
            matrix.indices[start:stop], matrix.data[start:stop], strict=True
        ):
            if target == source or forward <= 0.0:
                continue
            reverse = float(matrix[target, source])
            if reverse <= 0.0:
                raise RuntimeError("free generator has a one-way live transition")
            candidate = log_weight[source] + np.log(forward) - np.log(reverse)
            if np.isnan(log_weight[target]):
                log_weight[target] = candidate
                stack.append(int(target))
            else:
                maximum_log_balance_error = max(
                    maximum_log_balance_error,
                    abs(float(log_weight[target] - candidate)),
                )
    if not np.all(np.isfinite(log_weight)):
        raise RuntimeError("free generator is not connected")
    log_weight -= float(np.max(log_weight))
    weight = np.exp(log_weight)
    weight /= float(np.sum(weight))
    return weight, {
        "maximum_cycle_log_balance_error": maximum_log_balance_error,
        "log_weight_range": float(np.max(log_weight) - np.min(log_weight)),
    }


def _group_modes(
    decay_rates: np.ndarray, coefficients: np.ndarray
) -> list[dict[str, float | int]]:
    groups: list[dict[str, float | int]] = []
    start = 0
    while start < decay_rates.size:
        stop = start + 1
        while stop < decay_rates.size:
            scale = max(1.0, abs(float(decay_rates[start])), abs(float(decay_rates[stop])))
            if abs(float(decay_rates[stop] - decay_rates[start])) > EIGENVALUE_GROUP_TOLERANCE * scale:
                break
            stop += 1
        groups.append(
            {
                "group_index": len(groups),
                "multiplicity": stop - start,
                "decay_rate": float(np.mean(decay_rates[start:stop])),
                "coefficient": float(np.sum(coefficients[start:stop])),
            }
        )
        start = stop
    return groups


def _sign_variations(values: np.ndarray, threshold: float) -> tuple[int, int]:
    retained = np.asarray(values)[np.abs(values) > threshold]
    if retained.size == 0:
        return 0, 0
    signs = np.signbit(retained)
    return int(np.count_nonzero(signs[1:] != signs[:-1])), int(retained.size)


def _spectral_expansion(
    *,
    case: str,
    free_generator: sparse.csr_matrix,
    killed_generator: sparse.csr_matrix,
    killing: np.ndarray,
    initial: np.ndarray,
    critical_times: list[float],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    reversible_weight, balance = _reversible_measure(free_generator)
    root_weight = np.sqrt(reversible_weight)
    symmetric = (
        sparse.diags(root_weight)
        @ killed_generator
        @ sparse.diags(1.0 / root_weight)
    ).toarray()
    symmetry_residual = float(np.max(np.abs(symmetric - symmetric.T)))
    symmetric = 0.5 * (symmetric + symmetric.T)
    eigenvalues, eigenvectors = eigh(symmetric, driver="evd")
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    decay_rates = -eigenvalues
    if np.min(decay_rates) <= 0.0:
        raise RuntimeError(f"{case} killed generator is not transient")

    left_observable = initial / root_weight
    right_observable = root_weight * killing
    coefficients = (left_observable @ eigenvectors) * (
        eigenvectors.T @ right_observable
    )
    eigen_residual = float(
        np.max(
            np.abs(
                symmetric @ eigenvectors
                - eigenvectors * eigenvalues[np.newaxis, :]
            )
        )
    )
    orthogonality_residual = float(
        np.max(np.abs(eigenvectors.T @ eigenvectors - np.eye(eigenvectors.shape[1])))
    )
    groups = _group_modes(decay_rates, coefficients)
    grouped_coefficients = np.asarray([row["coefficient"] for row in groups], dtype=float)
    coefficient_scale = float(np.sum(np.abs(grouped_coefficients)))
    threshold_rows = []
    for relative_threshold in COEFFICIENT_RELATIVE_THRESHOLDS:
        variations, retained = _sign_variations(
            grouped_coefficients, relative_threshold * coefficient_scale
        )
        threshold_rows.append(
            {
                "relative_threshold": relative_threshold,
                "absolute_threshold": relative_threshold * coefficient_scale,
                "retained_group_count": retained,
                "sign_variations": variations,
            }
        )

    reconstruction_rows = []
    for time in critical_times:
        exponential = np.exp(-decay_rates * time)
        spectral_density = float(np.dot(coefficients, exponential))
        spectral_derivative = float(np.dot(-decay_rates * coefficients, exponential))
        state = expm_multiply(killed_generator.T * time, initial)
        direct_density = float(np.dot(state, killing))
        direct_derivative = float(np.dot(state, killed_generator @ killing))
        reconstruction_rows.append(
            {
                "time": time,
                "spectral_density": spectral_density,
                "direct_density": direct_density,
                "density_relative_error": abs(spectral_density - direct_density)
                / max(abs(direct_density), 1e-15),
                "spectral_scaled_derivative_residual": abs(spectral_derivative)
                * time
                / max(abs(direct_density), 1e-15),
                "direct_scaled_derivative_residual": abs(direct_derivative)
                * time
                / max(abs(direct_density), 1e-15),
            }
        )

    coefficient_rows = [
        {
            "case": case,
            "mode_index": index,
            "decay_rate": float(decay_rates[index]),
            "coefficient": float(coefficients[index]),
            "coefficient_sign": int(np.sign(coefficients[index])),
        }
        for index in range(decay_rates.size)
    ]
    summary = {
        "case": case,
        "state_count": int(killed_generator.shape[0]),
        "contact_safe_initial_flux": float(np.dot(initial, killing)),
        "symmetry_residual": symmetry_residual,
        "eigen_residual_max": eigen_residual,
        "orthogonality_residual_max": orthogonality_residual,
        "reversibility": balance,
        "distinct_decay_group_count": len(groups),
        "coefficient_absolute_sum": coefficient_scale,
        "coefficient_sum_f0": float(np.sum(coefficients)),
        "critical_point_count": len(critical_times),
        "critical_times": critical_times,
        "threshold_robustness": threshold_rows,
        "minimum_retained_sign_variations": min(
            row["sign_variations"] for row in threshold_rows
        ),
        "reconstruction": reconstruction_rows,
    }
    return summary, coefficient_rows


def _encounter_case() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    module = _load_module("validate_gig_fold.py", "spectral_gig_fold")
    fold, _ = module.locate_physical_fold()
    delta = 0.032
    model = module.physical_ctmc(
        float(fold["theta_log_kappa_near_over_far"]) + delta
    )
    continuation, _ = module.physical_continuation(fold)
    local = next(
        row for row in continuation if np.isclose(row["delta_theta"], delta)
    )
    late = float(
        brentq(
            lambda time: module.ctmc_density_derivative(model, time, 1),
            196.0,
            220.0,
            xtol=1e-12,
            rtol=1e-13,
        )
    )
    critical_times = [
        float(local["early_maximum_time"]),
        float(local["intervening_minimum_time"]),
        late,
    ]
    return _spectral_expansion(
        case="finite_encounter_supercritical",
        free_generator=module.FREE_GENERATOR,
        killed_generator=model.killed_generator,
        killing=model.total_rate,
        initial=model.initial,
        critical_times=critical_times,
    )


def _trimodal_case() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    module = _load_module("validate_2d_trimodal.py", "spectral_trimodal")
    grid = module.RectangularGrid2D(9, 5)
    model = module._model(grid)
    initial = module.contact_safe_initial_distribution_2d(
        model, module.START_ONE, module.START_TWO
    )
    with (DATA / "finite_radius_2d_trimodal_roots.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    critical_times = [
        float(row["time"])
        for row in rows
        if int(row["nx"]) == 9 and int(row["ny"]) == 5
    ]
    if len(critical_times) != 5:
        raise RuntimeError("M2D-T 9x5 artifact no longer has five critical points")
    killing = np.asarray(model.channel_rate_matrix.sum(axis=1)).reshape(-1)
    return _spectral_expansion(
        case="M2D-T_9x5",
        free_generator=model.free_generator,
        killed_generator=model.killed_generator,
        killing=killing,
        initial=initial,
        critical_times=critical_times,
    )


def _hypoexponential_counterexample() -> dict[str, Any]:
    decay_rates = np.asarray([1.0, 2.0, 3.0, 4.0])
    coefficients = np.asarray([4.0, -12.0, 12.0, -4.0])
    variations, retained = _sign_variations(coefficients, 0.0)
    root = float(np.log(4.0))
    density = float(4.0 * np.exp(-root) * (1.0 - np.exp(-root)) ** 3)
    return {
        "density": "4 exp(-t) (1-exp(-t))^3",
        "decay_rates": decay_rates.tolist(),
        "coefficients": coefficients.tolist(),
        "retained_coefficients": retained,
        "sign_variations": variations,
        "unique_positive_critical_point": root,
        "critical_point_type": "maximum",
        "density_at_critical_point": density,
        "conclusion": "three sign variations are not sufficient for bimodality",
    }


def _rank_one_counterexample() -> dict[str, Any]:
    branch_shape = 12
    rates = (12.0, 1.2)
    killing_rate = 100.0
    reactive_index = 2 * branch_shape
    size = reactive_index + 1
    transport = np.zeros((size, size), dtype=float)
    for branch, rate in enumerate(rates):
        offset = branch * branch_shape
        for stage in range(branch_shape):
            source = offset + stage
            target = reactive_index if stage == branch_shape - 1 else source + 1
            transport[source, target] = rate
            transport[source, source] = -rate
    killing = np.zeros(size)
    killing[reactive_index] = killing_rate
    generator = transport - np.diag(killing)
    initial = np.zeros(size)
    initial[0] = 0.5
    initial[branch_shape] = 0.5
    derivative_observable = generator @ killing
    second_observable = generator @ derivative_observable

    times = np.linspace(0.0, 30.0, 60_001)
    states = expm_multiply(
        sparse.csr_matrix(generator.T),
        initial,
        start=0.0,
        stop=30.0,
        num=times.size,
        endpoint=True,
    )
    derivative = states @ derivative_observable
    changes = np.flatnonzero(derivative[:-1] * derivative[1:] < 0.0)
    roots = []
    for index in changes:
        time = float(
            brentq(
                lambda value: float(
                    initial @ expm(generator * value) @ derivative_observable
                ),
                float(times[index]),
                float(times[index + 1]),
                xtol=1e-13,
                rtol=1e-13,
            )
        )
        state = initial @ expm(generator * time)
        curvature = float(state @ second_observable)
        roots.append(
            {
                "time": time,
                "type": "maximum" if curvature < 0.0 else "minimum",
                "density": float(state @ killing),
                "scaled_derivative_residual": abs(float(state @ derivative_observable))
                * time
                / max(float(state @ killing), 1e-15),
            }
        )
    if [row["type"] for row in roots] != ["maximum", "minimum", "maximum"]:
        raise RuntimeError("rank-one counterexample lost its bimodal root pattern")
    return {
        "branch_shape": branch_shape,
        "branch_rates": list(rates),
        "initial_branch_weights": [0.5, 0.5],
        "reactive_state_count": 1,
        "killing_support_rank": 1,
        "reactive_state_killing_rate": killing_rate,
        "critical_points": roots,
        "conclusion": "one reactive state can support a bimodal reaction-time density",
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    encounter, encounter_coefficients = _encounter_case()
    trimodal, trimodal_coefficients = _trimodal_case()
    hypoexponential = _hypoexponential_counterexample()
    rank_one = _rank_one_counterexample()

    if encounter["minimum_retained_sign_variations"] < 3:
        raise RuntimeError("encounter bimodality lacks three robust spectral sign changes")
    if trimodal["minimum_retained_sign_variations"] < 5:
        raise RuntimeError("M2D-T trimodality lacks five robust spectral sign changes")
    for case in (encounter, trimodal):
        if case["symmetry_residual"] > 1e-10:
            raise RuntimeError(f"{case['case']} failed reversible symmetrization")
        if case["eigen_residual_max"] > 2e-10:
            raise RuntimeError(f"{case['case']} eigendecomposition residual is too large")
        # The strongly biased finite encounter chain has a detailed-balance
        # weight range of many decades.  Its early fold density is reconstructed
        # by cancellation of O(1e5)-larger residues, so the eigensystem audit is
        # deliberately scaled to that conditioning rather than to the direct
        # semigroup root tolerance.  M2D-T is several orders more accurate.
        if max(row["density_relative_error"] for row in case["reconstruction"]) > 2e-5:
            raise RuntimeError(f"{case['case']} spectral density reconstruction failed")
        if max(
            row["spectral_scaled_derivative_residual"]
            for row in case["reconstruction"]
        ) > 5e-6:
            raise RuntimeError(f"{case['case']} spectral critical-point reconstruction failed")

    summary = {
        "evidence_level": "finite reversible spectral diagnostic plus exact/numerical counterexamples",
        "classical_corollary": (
            "After repeated decay rates are grouped and zero residues removed, "
            "the number of positive-time zeros of f' counted with multiplicity "
            "does not exceed the sign variations of the ordered residues."
        ),
        "mode_necessity": (
            "m nondegenerate interior modes require at least 2m-1 ordered "
            "spectral-residue sign variations."
        ),
        "not_claimed": [
            "novelty of the generalized Descartes rule",
            "sufficiency of the sign-variation condition",
            "a mode-count bound for nonreversible or Jordan-block phase-type laws",
            "a mode-count bound based on reaction-channel or killing-support rank",
            "a continuum spectral theorem without convergence and domain hypotheses",
        ],
        "production_cases": [encounter, trimodal],
        "hypoexponential_non_sufficiency": hypoexponential,
        "rank_one_killing_bimodality": rank_one,
    }
    summary_path = DATA / "spectral_modality_summary.json"
    coefficient_path = DATA / "spectral_modality_coefficients.csv"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_csv(
        coefficient_path,
        encounter_coefficients + trimodal_coefficients,
    )
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=[sys.executable, str(HERE.relative_to(REPO))],
        model_spec={
            "spectral_scope": "finite reversible killed generators with grouped real decay rates",
            "encounter_control_offset": 0.032,
            "trimodal_grid": [9, 5],
            "eigenvalue_group_relative_tolerance": EIGENVALUE_GROUP_TOLERANCE,
            "coefficient_relative_thresholds": list(COEFFICIENT_RELATIVE_THRESHOLDS),
            "rank_one_counterexample": "two 12-stage Erlang branches feeding one killing state",
        },
        classifier_spec={
            "critical_points": "direct generator-derivative Brent roots from frozen production families",
            "sign_variations": "ordered grouped residues after threshold removal",
            "claim_boundary": summary["evidence_level"],
        },
        dependencies=[
            HERE.with_name("validate_gig_fold.py"),
            HERE.with_name("validate_2d_trimodal.py"),
            REPORT / "notes" / "spectral_modality_bound.md",
            DATA / "finite_radius_2d_trimodal_roots.csv",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
        ],
        outputs=[summary_path, coefficient_path],
        horizon={
            "encounter_critical_time_max": max(encounter["critical_times"]),
            "trimodal_critical_time_max": max(trimodal["critical_times"]),
            "rank_one_scan_stop": 30.0,
        },
    )
    write_manifest(DATA / "spectral_modality.manifest.json", manifest)
    print(
        json.dumps(
            {
                "encounter_minimum_sign_variations": encounter[
                    "minimum_retained_sign_variations"
                ],
                "trimodal_minimum_sign_variations": trimodal[
                    "minimum_retained_sign_variations"
                ],
                "hypoexponential_sign_variations": hypoexponential[
                    "sign_variations"
                ],
                "hypoexponential_mode_count": 1,
                "rank_one_critical_points": rank_one["critical_points"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
