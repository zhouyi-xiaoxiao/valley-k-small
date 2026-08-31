#!/usr/bin/env python3
"""Confirm one G1c finite-grid fold with exact control sensitivities.

The selected segment is frozen outside this code.  A passing result confirms
only one fold of the 65x65x49 killed finite-volume model; it never promotes a
continuum or project-level claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import continuum_g1c_simplex as g1c
import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import brentq
from scipy.sparse.linalg import expm_multiply

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "continuum_g1d_fold_confirmation_manifest.json"
OUTPUT = DATA / "continuum_g1d_fold_confirmation_result.json"
G1C_MANIFEST = DATA / "continuum_g1c_simplex_manifest.json"
G1C_RESULT = DATA / "continuum_g1c_simplex_result.json"
TOPOLOGY_REVIEW = REPORT / "audits" / "round_24_g1c_topology_manual_review.md"
PROTOCOL = REPORT / "notes" / "g1d_fold_confirmation_protocol.md"

STAGE = "G1d_post_result_single_segment_finite_grid_fold_confirmation"
PASS_STATUS = "PASS_FINITE_GRID_FOLD_ONLY"
FAIL_STATUS = "FAIL_G1D_FOLD_CONFIRMATION"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if type(value) is not dict:
        raise ValueError(f"{path} must contain one JSON object")
    return value


def require_repository_venv() -> None:
    if Path(sys.prefix).resolve() != (REPOSITORY / ".venv").resolve():
        raise RuntimeError("G1d must run inside the repository .venv")


def selected_weights(control: float) -> np.ndarray:
    value = float(control)
    return np.asarray((0.2, 0.1 * value, 0.8 - 0.1 * value), dtype=float)


WEIGHT_DERIVATIVE = np.asarray((0.0, 0.1, -0.1), dtype=float)


def configuration() -> g1c.SimplexConfiguration:
    config = g1c.SimplexConfiguration.from_manifest(load_json(G1C_MANIFEST))
    config.validate()
    return config


def assemble_float_model(
    config: g1c.SimplexConfiguration,
    control: float,
) -> tuple[Any, np.ndarray, sparse.csr_matrix]:
    """Assemble the selected float-weight control and its generator tangent."""

    weights = selected_weights(control)
    if (
        not np.isfinite(weights).all()
        or abs(float(np.sum(weights)) - 1.0) > 2.0e-15
        or float(np.min(weights)) < 0.0
    ):
        raise ValueError("selected G1d weights left the admissible simplex")
    baseline = g1c._shared_baseline(config)  # noqa: SLF001
    parameters = baseline.parameters
    budget_density = parameters.installed_budget / parameters.transverse_width
    kappa = budget_density * (weights @ baseline.patch_cell_averages)
    kappa_derivative = budget_density * (WEIGHT_DERIVATIVE @ baseline.patch_cell_averages)
    killing = np.kron(kappa, baseline.contact_fraction_relative)
    killing_derivative = np.kron(kappa_derivative, baseline.contact_fraction_relative)
    killed = baseline.free_generator - sparse.diags(killing, format="csr")
    generator_derivative = -sparse.diags(killing_derivative, format="csr")
    physical_budget = float(
        parameters.transverse_width * np.sum(kappa) * baseline.grid.midpoint_spacing
    )
    killed_balance = float(
        np.max(np.abs(np.asarray(killed.sum(axis=1)).reshape(-1) + killing))
    )
    model = replace(
        baseline,
        theta=0.0,
        killed_generator=killed,
        killing=killing,
        killing_derivative=killing_derivative,
        kappa=kappa,
        kappa_derivative=kappa_derivative,
        physical_budget=physical_budget,
        killed_mass_balance_error=killed_balance,
    )
    return model, weights, generator_derivative


def model_gates(model: Any, weights: np.ndarray, generator_derivative: sparse.csr_matrix) -> dict[str, Any]:
    parameters = model.parameters
    spacing = model.grid.midpoint_spacing
    patch_integrals = np.sum(model.patch_cell_averages, axis=1) * spacing
    expected_kappa = (
        parameters.installed_budget
        / parameters.transverse_width
        * (weights @ model.patch_cell_averages)
    )
    expected_kappa_derivative = (
        parameters.installed_budget
        / parameters.transverse_width
        * (WEIGHT_DERIVATIVE @ model.patch_cell_averages)
    )
    expected_killing = np.kron(expected_kappa, model.contact_fraction_relative)
    expected_killing_derivative = np.kron(
        expected_kappa_derivative, model.contact_fraction_relative
    )
    expected_generator_derivative = -sparse.diags(expected_killing_derivative, format="csr")
    physical_budget = float(parameters.transverse_width * np.sum(model.kappa) * spacing)
    derivative_budget = float(
        parameters.transverse_width * np.sum(model.kappa_derivative) * spacing
    )

    def sparse_max_abs(matrix: sparse.spmatrix) -> float:
        values = matrix.tocsr().data
        return float(np.max(np.abs(values))) if values.size else 0.0

    diagnostics = {
        "weight_sum_error": float(abs(np.sum(weights) - 1.0)),
        "minimum_weight": float(np.min(weights)),
        "maximum_patch_integral_error": float(np.max(np.abs(patch_integrals - 1.0))),
        "physical_budget_relative_error": float(
            abs(physical_budget - parameters.installed_budget) / parameters.installed_budget
        ),
        "control_tangent_budget_absolute_error": abs(derivative_budget),
        "kappa_reconstruction_max_abs_error": float(np.max(np.abs(model.kappa - expected_kappa))),
        "kappa_tangent_reconstruction_max_abs_error": float(
            np.max(np.abs(model.kappa_derivative - expected_kappa_derivative))
        ),
        "killing_reconstruction_max_abs_error": float(
            np.max(np.abs(model.killing - expected_killing))
        ),
        "killing_tangent_reconstruction_max_abs_error": float(
            np.max(np.abs(model.killing_derivative - expected_killing_derivative))
        ),
        "generator_tangent_reconstruction_max_abs_error": sparse_max_abs(
            generator_derivative - expected_generator_derivative
        ),
        "killed_mass_balance_error": float(model.killed_mass_balance_error),
        "initial_mass_error": float(abs(np.sum(model.initial) - 1.0)),
        "initial_contact_mass": float(model.initial_contact_mass),
        "minimum_kappa": float(np.min(model.kappa)),
        "minimum_killing": float(np.min(model.killing)),
    }
    gates = {
        "weight_sum_unit": diagnostics["weight_sum_error"] <= 2.0e-15,
        "weights_nonnegative": diagnostics["minimum_weight"] >= 0.0,
        "patch_integrals_unit": diagnostics["maximum_patch_integral_error"] <= 1.0e-10,
        "physical_budget_fixed": diagnostics["physical_budget_relative_error"] <= 1.0e-10,
        "control_tangent_preserves_budget": diagnostics[
            "control_tangent_budget_absolute_error"
        ]
        <= 1.0e-12,
        "kappa_reconstructed": diagnostics["kappa_reconstruction_max_abs_error"] <= 1.0e-14,
        "kappa_tangent_reconstructed": diagnostics[
            "kappa_tangent_reconstruction_max_abs_error"
        ]
        <= 1.0e-14,
        "killing_reconstructed": diagnostics["killing_reconstruction_max_abs_error"]
        <= 1.0e-14,
        "killing_tangent_reconstructed": diagnostics[
            "killing_tangent_reconstruction_max_abs_error"
        ]
        <= 1.0e-14,
        "generator_tangent_reconstructed": diagnostics[
            "generator_tangent_reconstruction_max_abs_error"
        ]
        <= 1.0e-14,
        "killed_mass_balance": diagnostics["killed_mass_balance_error"] <= 1.0e-12,
        "initial_mass_unit": diagnostics["initial_mass_error"] <= 1.0e-12,
        "initial_contact_safe": diagnostics["initial_contact_mass"] == 0.0,
        "kappa_nonnegative": diagnostics["minimum_kappa"] >= -1.0e-14,
        "killing_nonnegative": diagnostics["minimum_killing"] >= -1.0e-14,
    }
    return {"diagnostics": diagnostics, "gates": gates}


def action_jets(
    model: Any,
    generator_derivative: sparse.csr_matrix,
    maximum_order: int = 3,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    generator = model.killed_generator
    values = [np.asarray(model.killing, dtype=float)]
    derivatives = [np.asarray(model.killing_derivative, dtype=float)]
    for _ in range(maximum_order):
        derivatives.append(
            np.asarray(
                generator_derivative @ values[-1] + generator @ derivatives[-1],
                dtype=float,
            )
        )
        values.append(np.asarray(generator @ values[-1], dtype=float))
    return values, derivatives


def point_fold_jet(config: g1c.SimplexConfiguration, time: float, control: float) -> dict[str, Any]:
    model, weights, generator_derivative = assemble_float_model(config, control)
    generator = model.killed_generator.tocsr()
    operator = generator.T.tocsr()
    block = sparse.bmat(
        [[operator, None], [generator_derivative, operator]],
        format="csr",
    )
    initial = np.concatenate((model.initial, np.zeros_like(model.initial)))
    trace = float(np.sum(generator.diagonal()))
    propagated = np.asarray(
        expm_multiply(block * time, initial, traceA=2.0 * time * trace),
        dtype=float,
    )
    state_count = model.grid.state_count
    state = propagated[:state_count]
    sensitivity = propagated[state_count:]
    values, derivatives = action_jets(model, generator_derivative, maximum_order=3)
    time_jets = np.asarray([state @ vector for vector in values], dtype=float)
    control_jets = np.asarray(
        [sensitivity @ value + state @ derivative for value, derivative in zip(values, derivatives)],
        dtype=float,
    )
    density = float(time_jets[0])
    if density <= 0.0 or not np.isfinite(time_jets).all() or not np.isfinite(control_jets).all():
        raise FloatingPointError("invalid point fold jet")
    return {
        "time": float(time),
        "control": float(control),
        "weights": weights,
        "time_jets": time_jets,
        "control_jets": control_jets,
        "state": state,
        "sensitivity": sensitivity,
        "model": model,
        "generator_derivative": generator_derivative,
    }


def solve_fold(config: g1c.SimplexConfiguration, manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    solve = manifest["solve"]
    x = np.asarray(solve["initial_guess"], dtype=float)
    history: list[dict[str, Any]] = []
    for iteration in range(solve["maximum_iterations"]):
        payload = point_fold_jet(config, float(x[0]), float(x[1]))
        jets = payload["time_jets"]
        controls = payload["control_jets"]
        residual = np.asarray((jets[1], jets[2]), dtype=float)
        jacobian = np.asarray(((jets[2], controls[1]), (jets[3], controls[2])), dtype=float)
        scaled = np.asarray(
            (abs(x[0] * jets[1] / jets[0]), abs(x[0] ** 2 * jets[2] / jets[0])),
            dtype=float,
        )
        history.append(
            {
                "iteration": iteration,
                "time": float(x[0]),
                "control": float(x[1]),
                "scaled_residuals": scaled.tolist(),
                "raw_jacobian_determinant": float(np.linalg.det(jacobian)),
            }
        )
        if float(np.max(scaled)) <= solve["newton_scaled_residual_tolerance"]:
            return payload, history
        step = np.linalg.solve(jacobian, -residual)
        accepted = False
        for damping in (1.0, 0.5, 0.25, 0.125, 0.0625):
            candidate = x + damping * step
            if (
                solve["time_bounds"][0] <= candidate[0] <= solve["time_bounds"][1]
                and solve["control_bounds"][0]
                <= candidate[1]
                <= solve["control_bounds"][1]
            ):
                x = candidate
                accepted = True
                break
        if not accepted:
            raise RuntimeError("Newton step left the frozen solve box")
    raise RuntimeError("Newton failed to converge inside the frozen iteration limit")


def point_time_jets(config: g1c.SimplexConfiguration, time: float, control: float) -> np.ndarray:
    model, _weights, generator_derivative = assemble_float_model(config, control)
    generator = model.killed_generator.tocsr()
    trace = float(np.sum(generator.diagonal()))
    state = np.asarray(
        expm_multiply(generator.T * time, model.initial, traceA=time * trace),
        dtype=float,
    )
    values, _derivatives = action_jets(model, generator_derivative, maximum_order=3)
    return np.asarray([state @ value for value in values], dtype=float)


def evaluate_declared_uniform_grid(
    model: Any,
    *,
    spacing: float,
    points: int,
    chunk_points: int,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Evaluate a grid defined by integer ticks, without re-inferring its spacing.

    The inherited discovery helper rejects decimal spacings such as 0.02 under
    a tolerance comparable to one floating-point ulp.  Here the integer-tick
    construction is the definition of uniformity, and every exponential chunk
    uses ``spacing * integer_steps`` directly.
    """

    times = spacing * np.arange(points, dtype=float)
    generator = model.killed_generator.tocsr()
    operator = generator.T.tocsr()
    values, _derivatives = action_jets(
        model,
        sparse.csr_matrix(generator.shape, dtype=float),
        maximum_order=3,
    )
    actions = np.column_stack(values)
    current = np.asarray(model.initial, dtype=float).copy()
    initial_observables = current @ actions
    accumulated: dict[str, list[float]] = {
        "f": [float(initial_observables[0])],
        "f_t": [float(initial_observables[1])],
        "f_tt": [float(initial_observables[2])],
        "f_ttt": [float(initial_observables[3])],
        "survival": [float(np.sum(current))],
    }
    cursor = 0
    chunks = 0
    minimum_state_mass = float(np.min(current))
    maximum_rows = 1
    trace = float(np.sum(generator.diagonal()))
    while cursor < points - 1:
        end = min(cursor + chunk_points - 1, points - 1)
        rows = end - cursor + 1
        local_stop = spacing * (end - cursor)
        states = np.asarray(
            expm_multiply(
                operator,
                current,
                start=0.0,
                stop=local_stop,
                num=rows,
                endpoint=True,
                traceA=trace,
            ),
            dtype=float,
        )
        minimum_state_mass = min(minimum_state_mass, float(np.min(states)))
        new_states = states[1:]
        observables = new_states @ actions
        survival = np.sum(new_states, axis=1)
        for column, name in enumerate(("f", "f_t", "f_tt", "f_ttt")):
            accumulated[name].extend(float(value) for value in observables[:, column])
        accumulated["survival"].extend(float(value) for value in survival)
        current = states[-1].copy()
        cursor = end
        chunks += 1
        maximum_rows = max(maximum_rows, rows)
    curves = {"time": times}
    curves.update({name: np.asarray(data, dtype=float) for name, data in accumulated.items()})
    if any(data.shape != times.shape or not np.isfinite(data).all() for data in curves.values()):
        raise FloatingPointError("invalid declared-grid observable curve")
    maximum_survival_increase = float(np.max(np.diff(curves["survival"])))
    if minimum_state_mass < -1.0e-11 or float(np.min(curves["f"])) < -1.0e-11:
        raise RuntimeError("declared-grid semigroup produced negative mass or density")
    if maximum_survival_increase > 1.0e-10:
        raise RuntimeError("declared-grid survival is not monotone")
    return curves, {
        "chunk_count": chunks,
        "chunk_points_limit": chunk_points,
        "maximum_chunk_state_rows": maximum_rows,
        "state_dimension": model.grid.state_count,
        "full_state_history_stored": False,
        "minimum_state_mass": minimum_state_mass,
        "minimum_density": float(np.min(curves["f"])),
        "maximum_survival_increase": maximum_survival_increase,
        "uniform_grid_definition": "integer ticks times the frozen decimal spacing",
    }


def refined_side_topology(
    config: g1c.SimplexConfiguration,
    control: float,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    side = manifest["side_topology"]
    spacing = side["spacing"]
    times = spacing * np.arange(side["points"], dtype=float)
    if not math.isclose(float(times[-1]), side["stop"], rel_tol=0.0, abs_tol=1.0e-12):
        raise ValueError("frozen side-topology time grid is internally inconsistent")
    model, weights, _generator_derivative = assemble_float_model(config, control)
    curves, chunk_diagnostics = evaluate_declared_uniform_grid(
        model,
        spacing=spacing,
        points=side["points"],
        chunk_points=side["chunk_points"],
    )
    start = side["analysis_start"]
    derivative = curves["f_t"]
    brackets = [
        (float(times[index]), float(times[index + 1]))
        for index in range(len(times) - 1)
        if times[index] >= start and derivative[index] * derivative[index + 1] < 0.0
    ]
    roots = []
    for left, right in brackets:
        root = float(
            brentq(
                lambda value: float(point_time_jets(config, value, control)[1]),
                left,
                right,
                xtol=side["root_absolute_tolerance"],
                rtol=side["root_relative_tolerance"],
            )
        )
        jets = point_time_jets(config, root, control)
        roots.append(
            {
                "time": root,
                "topology": "maximum" if jets[2] < 0.0 else "minimum",
                "density": float(jets[0]),
                "scaled_first_derivative_residual": float(abs(root * jets[1] / jets[0])),
                "scaled_second_derivative": float(root**2 * jets[2] / jets[0]),
            }
        )
    return {
        "control": float(control),
        "weights": weights.tolist(),
        "root_count": len(roots),
        "topology": [row["topology"] for row in roots],
        "roots": roots,
        "chunk_diagnostics": chunk_diagnostics,
    }


def finite_difference_check(
    config: g1c.SimplexConfiguration,
    fold: dict[str, Any],
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    time = fold["time"]
    control = fold["control"]
    exact = fold["control_jets"]
    rows = []
    for step in manifest["finite_difference_check"]["steps"]:
        plus = point_time_jets(config, time, control + step)
        minus = point_time_jets(config, time, control - step)
        estimate = (plus - minus) / (2.0 * step)
        relative_errors = [
            float(abs(estimate[order] - exact[order]) / max(abs(exact[order]), 1.0e-300))
            for order in (1, 2)
        ]
        rows.append(
            {
                "step": step,
                "estimates_f_tlambda_f_ttlambda": [float(estimate[1]), float(estimate[2])],
                "exact_f_tlambda_f_ttlambda": [float(exact[1]), float(exact[2])],
                "relative_errors": relative_errors,
                "maximum_relative_error": max(relative_errors),
            }
        )
    return rows


def validate_pins(manifest: dict[str, Any]) -> None:
    pins = manifest["pinned_inputs"]
    for name, path in (
        ("g1c_result", G1C_RESULT),
        ("g1c_manifest", G1C_MANIFEST),
        ("topology_review", TOPOLOGY_REVIEW),
        ("protocol", PROTOCOL),
        ("runner", HERE),
    ):
        observed = sha256(path)
        if observed != pins[f"{name}_sha256"]:
            raise ValueError(f"frozen G1d pin mismatch: {name}")
    g1c_result = load_json(G1C_RESULT)
    analysis = g1c_result["simplex_candidate_analysis"]
    if analysis["family_discovery_gate_passed"] is not True:
        raise ValueError("pinned G1c result no longer passes its narrow family gate")
    selected = manifest["selected_segment"]
    seeds = analysis["interior_candidate_seeds"]
    matches = [
        row
        for row in seeds
        if row["left_control_id"] == selected["left_control_id"]
        and row["right_control_id"] == selected["right_control_id"]
    ]
    if len(matches) != 1:
        raise ValueError("selected G1d segment is not the unique pinned G1c seed")
    if not np.allclose(
        matches[0]["interpolated_crossing_weights"],
        selected["g1c_seed_weights"],
        rtol=0.0,
        atol=1.0e-15,
    ):
        raise ValueError("selected G1d seed weights changed")


def run() -> dict[str, Any]:
    require_repository_venv()
    manifest = load_json(MANIFEST)
    validate_pins(manifest)
    config = configuration()
    fold, history = solve_fold(config, manifest)
    time = fold["time"]
    control = fold["control"]
    weights = fold["weights"]
    jets = fold["time_jets"]
    control_jets = fold["control_jets"]
    density = float(jets[0])
    scaled = {
        "f_t": float(time * jets[1] / density),
        "f_tt": float(time**2 * jets[2] / density),
        "f_ttt": float(time**3 * jets[3] / density),
        "f_tlambda": float(time * control_jets[1] / density),
        "f_ttlambda": float(time**2 * control_jets[2] / density),
    }
    dimensionless_jacobian = np.asarray(
        ((scaled["f_tt"], scaled["f_tlambda"]), (scaled["f_ttt"], scaled["f_ttlambda"])),
        dtype=float,
    )
    side_offset = manifest["side_topology"]["control_offset"]
    side_rows = [
        refined_side_topology(config, control - side_offset, manifest),
        refined_side_topology(config, control + side_offset, manifest),
    ]
    finite_difference = finite_difference_check(config, fold, manifest)
    foundations = model_gates(fold["model"], weights, fold["generator_derivative"])
    acceptance = manifest["acceptance"]
    topology_signatures = sorted((row["root_count"], tuple(row["topology"])) for row in side_rows)
    checks = {
        "newton_iteration_limit": len(history) <= manifest["solve"]["maximum_iterations"],
        "solution_inside_frozen_box": (
            manifest["solve"]["time_bounds"][0]
            <= time
            <= manifest["solve"]["time_bounds"][1]
            and manifest["solve"]["control_bounds"][0]
            <= control
            <= manifest["solve"]["control_bounds"][1]
        ),
        "scaled_fold_residuals": max(abs(scaled["f_t"]), abs(scaled["f_tt"]))
        <= acceptance["maximum_scaled_fold_residual"],
        "strict_interior_weight_floor": float(np.min(weights))
        >= acceptance["minimum_weight"],
        "third_time_jet_nondegenerate": abs(scaled["f_ttt"])
        >= acceptance["minimum_abs_scaled_f_ttt"],
        "control_unfolding_nondegenerate": abs(scaled["f_tlambda"])
        >= acceptance["minimum_abs_scaled_f_tlambda"],
        "dimensionless_jacobian_determinant": abs(float(np.linalg.det(dimensionless_jacobian)))
        >= acceptance["minimum_abs_dimensionless_jacobian_determinant"],
        "one_vs_three_side_topology": topology_signatures
        == [
            (1, ("maximum",)),
            (3, ("maximum", "minimum", "maximum")),
        ],
        "finite_difference_tangent_check": finite_difference[-1]["maximum_relative_error"]
        <= acceptance["maximum_finite_difference_relative_error"],
        "finite_difference_error_decreases": finite_difference[-1]["maximum_relative_error"]
        < finite_difference[0]["maximum_relative_error"],
        "all_foundation_gates": all(foundations["gates"].values()),
    }
    passed = all(checks.values())
    return {
        "schema_version": 1,
        "stage": STAGE,
        "status": PASS_STATUS if passed else FAIL_STATUS,
        "claim_scope": "one result-informed finite-grid fold on the frozen G1 family",
        "evidence_timing": "POST_RESULT_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY",
        "finite_grid_fold_confirmed": passed,
        "continuum_verified": False,
        "project_gate_passed": False,
        "finite_B_Doi_fold": True if passed else False,
        "configuration": config.to_dict(),
        "selected_segment": manifest["selected_segment"],
        "fold": {
            "time": time,
            "control": control,
            "weights": weights.tolist(),
            "density": density,
            "time_jets_orders_0_to_3": jets.tolist(),
            "control_jets_orders_0_to_3": control_jets.tolist(),
            "scaled_fold_jet": scaled,
            "dimensionless_jacobian": dimensionless_jacobian.tolist(),
            "dimensionless_jacobian_determinant": float(np.linalg.det(dimensionless_jacobian)),
        },
        "newton_history": history,
        "side_topology": side_rows,
        "finite_difference_check": finite_difference,
        "foundation": foundations,
        "checks": checks,
        "limitations": [
            "single 65x65x49 finite-volume mesh and one finite box",
            "result-informed segment selected after G1c",
            "no odd/even convergence or independent solver",
            "no continuum fold, cusp, trimodality, or project-gate claim",
        ],
        "provenance": {
            "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "runner": str(HERE.relative_to(REPORT)),
            "runner_sha256": sha256(HERE),
            "manifest": str(MANIFEST.relative_to(REPORT)),
            "manifest_sha256": sha256(MANIFEST),
            "g1c_result_sha256": sha256(G1C_RESULT),
            "topology_review_sha256": sha256(TOPOLOGY_REVIEW),
            "protocol_sha256": sha256(PROTOCOL),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "python_executable": sys.executable,
        },
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    result = run()
    write_json(args.output, result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "fold": result["fold"],
                "checks": result["checks"],
                "output": str(args.output),
                "output_sha256": sha256(args.output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["status"] == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
