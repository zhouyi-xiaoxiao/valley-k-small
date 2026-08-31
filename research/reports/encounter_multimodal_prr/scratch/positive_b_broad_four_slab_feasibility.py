#!/usr/bin/env python3
"""Result-informed low-mesh feasibility for the fixed broad four-slab control.

This scratch calculation is intentionally not a formal positive-B gate.  It
uses one declared low mesh to choose at most one budget for a later frozen,
held-out mesh study.  Every explored result must remain disclosed.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
CODE = REPORT / "code"
sys.path.insert(0, str(CODE))

import continuum_broad_patch_b0_bridge as bridge  # noqa: E402
import continuum_weak_budget_design as discrete  # noqa: E402
import numpy as np  # noqa: E402
from scipy import sparse  # noqa: E402
from scipy.interpolate import PchipInterpolator  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

WEIGHTS = np.asarray(
    (0.28, 0.27736690132708747, 0.0857172266153233, 0.3569158720575891),
    dtype=float,
)
DEFAULT_OUTPUT = REPORT / "scratch" / "positive_b_broad_four_slab_feasibility_result.json"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def build_killed(
    cells: int,
    budget: float,
    manifest: dict[str, Any],
) -> tuple[sparse.csr_matrix, np.ndarray, np.ndarray, dict[str, Any]]:
    parameters = bridge.parameters_from_manifest(manifest)
    factors = bridge.build_fv_factors(cells, parameters, manifest)
    relative_states = cells * cells
    free = sparse.kron(
        factors.midpoint_generator,
        sparse.eye(relative_states, format="csr"),
        format="csr",
    ) + sparse.kron(
        sparse.eye(cells, format="csr"),
        factors.relative_generator,
        format="csr",
    )
    kappa_per_budget = WEIGHTS @ factors.patch_profiles / parameters.transverse_width
    killing_per_budget = np.kron(kappa_per_budget, factors.contact_profile)
    killing = float(budget) * killing_per_budget
    killed = free - sparse.diags(killing, format="csr")
    initial = np.kron(factors.midpoint_initial, factors.relative_initial)
    ones = np.ones_like(initial)
    diagnostics = {
        "mesh": [cells, cells, cells],
        "state_count": int(initial.size),
        "free_nnz": int(free.nnz),
        "killed_nnz": int(killed.nnz),
        "physical_budget": float(
            parameters.transverse_width
            * np.sum(float(budget) * kappa_per_budget)
            * factors.grid.midpoint_spacing
        ),
        "physical_budget_absolute_error": float(
            abs(
                parameters.transverse_width
                * np.sum(float(budget) * kappa_per_budget)
                * factors.grid.midpoint_spacing
                - budget
            )
        ),
        "initial_mass_error": float(abs(np.sum(initial) - 1.0)),
        "killed_mass_balance_operator_error": float(np.max(np.abs(killed @ ones + killing))),
        "minimum_killing": float(np.min(killing)),
        "maximum_killing": float(np.max(killing)),
        "factor_diagnostics": factors.diagnostics,
    }
    return killed, initial, killing, diagnostics


def stationary_structure(
    times: np.ndarray,
    projected: np.ndarray,
) -> dict[str, Any]:
    density = projected[:, 0]
    first = projected[:, 1]
    second = projected[:, 2]
    survival = projected[:, 4]
    interpolants = [PchipInterpolator(times, projected[:, index]) for index in range(5)]
    brackets = [
        (float(times[index]), float(times[index + 1]))
        for index in np.flatnonzero(first[:-1] * first[1:] < 0.0)
        if times[index] >= 0.1
    ]
    peak = float(np.max(density))
    roots = []
    for left, right in brackets:
        root = float(brentq(interpolants[1], left, right, xtol=2.0e-12, rtol=1.0e-13))
        values = np.asarray([curve(root) for curve in interpolants], dtype=float)
        if values[0] < 1.0e-8 * peak:
            continue
        roots.append(
            {
                "time": root,
                "topology": "maximum" if values[2] < 0.0 else "minimum",
                "density": float(values[0]),
                "scaled_second_derivative": float(root**2 * values[2] / values[0]),
                "survival": float(values[4]),
            }
        )
    maxima = [row for row in roots if row["topology"] == "maximum"]
    topology = [row["topology"] for row in roots]
    valley_ratios = []
    if topology == ["maximum", "minimum", "maximum", "minimum", "maximum"]:
        for index in (1, 3):
            valley_ratios.append(
                float(
                    roots[index]["density"]
                    / min(roots[index - 1]["density"], roots[index + 1]["density"])
                )
            )
    event_masses = []
    if len(roots) == 5 and topology == [
        "maximum",
        "minimum",
        "maximum",
        "minimum",
        "maximum",
    ]:
        first_survival = roots[1]["survival"]
        second_survival = roots[3]["survival"]
        event_masses = [
            float(1.0 - first_survival),
            float(first_survival - second_survival),
            float(second_survival - survival[-1]),
        ]
    peak_ratio = (
        float(min(row["density"] for row in maxima) / max(row["density"] for row in maxima))
        if maxima
        else 0.0
    )
    return {
        "interpolation": "PCHIP of spacing-0.05 feasibility trace; not formal point refinement",
        "sampled_sign_change_count": len(brackets),
        "stationary_root_count": len(roots),
        "topology": topology,
        "roots": roots,
        "peak_minimum_to_maximum_ratio": peak_ratio,
        "valley_to_smaller_adjacent_peak_ratios": valley_ratios,
        "event_basin_reaction_masses": event_masses,
        "final_survival": float(survival[-1]),
        "total_reaction_mass_to_time_stop": float(1.0 - survival[-1]),
        "maximum_sampled_survival_increase": float(np.max(np.diff(survival))),
        "minimum_sampled_density": float(np.min(density)),
        "minimum_sampled_second_derivative": float(np.min(second)),
    }


def run_one(
    cells: int,
    budget: float,
    times: np.ndarray,
    manifest: dict[str, Any],
    *,
    chunk_points: int,
) -> dict[str, Any]:
    started = time.monotonic()
    killed, initial, killing, diagnostics = build_killed(cells, budget, manifest)
    actions = [killing]
    for _ in range(3):
        actions.append(np.asarray(killed @ actions[-1], dtype=float))
    action_matrix = np.column_stack((*actions, np.ones_like(initial)))
    projected = discrete._projected_curves_chunked(  # noqa: SLF001
        killed,
        initial,
        action_matrix,
        times,
        chunk_points=chunk_points,
    )
    structure = stationary_structure(times, projected)
    topology = ["maximum", "minimum", "maximum", "minimum", "maximum"]
    valley_ratios = structure["valley_to_smaller_adjacent_peak_ratios"]
    masses = structure["event_basin_reaction_masses"]
    gates = {
        "five_alternating_roots": structure["topology"] == topology,
        "peak_ratio": structure["peak_minimum_to_maximum_ratio"] >= 0.10,
        "valley_ratios": len(valley_ratios) == 2 and max(valley_ratios) <= 0.85,
        "event_masses": len(masses) == 3 and min(masses) >= 0.005,
        "mass_balance_operator": diagnostics["killed_mass_balance_operator_error"] <= 1.0e-9,
        "survival_monotone": structure["maximum_sampled_survival_increase"] <= 1.0e-12,
    }
    stride = max(1, int(round(0.5 / (times[1] - times[0]))))
    trace_indices = np.arange(0, len(times), stride)
    return {
        "budget": budget,
        "diagnostics": diagnostics,
        "stationary_structure": structure,
        "feasibility_gates": gates,
        "all_feasibility_gates_passed": bool(all(gates.values())),
        "sampled_trace_spacing": float(times[stride] - times[0]),
        "sampled_trace": [
            {
                "time": float(times[index]),
                "f": float(projected[index, 0]),
                "f_t": float(projected[index, 1]),
                "f_tt": float(projected[index, 2]),
                "f_ttt": float(projected[index, 3]),
                "survival": float(projected[index, 4]),
            }
            for index in trace_indices
        ],
        "elapsed_seconds": float(time.monotonic() - started),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=int, default=65)
    parser.add_argument("--budgets", nargs="+", type=float, default=(0.01, 0.02, 0.04, 0.08))
    parser.add_argument("--time-spacing", type=float, default=0.05)
    parser.add_argument("--chunk-points", type=int, default=51)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    if args.mesh < 17 or args.mesh % 2 != 1:
        parser.error("mesh must be an odd integer of at least 17")
    points = int(round(100.0 / args.time_spacing)) + 1
    times = np.linspace(0.0, 100.0, points)
    if abs(float(times[1] - times[0]) - args.time_spacing) > 1.0e-14:
        parser.error("time spacing must close exactly on 100")
    manifest = bridge.load_json(bridge.MANIFEST)
    seed = int(manifest["numerical_reproducibility"]["numpy_global_seed"])
    with bridge.pinned_numpy_global_seed(seed):
        rows = [
            run_one(
                args.mesh,
                float(budget),
                times,
                manifest,
                chunk_points=args.chunk_points,
            )
            for budget in args.budgets
        ]
    payload = {
        "schema_version": 1,
        "stage": "RESULT_INFORMED_LOW_MESH_POSITIVE_B_FEASIBILITY_ONLY",
        "formal_confirmation": False,
        "positive_B_event_mass_shape_confirmation": False,
        "continuum_interval_verified": False,
        "unbounded_domain_FV_limit_verified": False,
        "independent_solver_verified": False,
        "project_gate_passed": False,
        "geometry": {
            "initial_half_width": 0.02,
            "patch_half_width": 0.04,
            "patch_centres": [0.35, 0.60, 0.75, 0.90],
            "weights_fixed_at_bridge_s_0p13": WEIGHTS.tolist(),
            "weights_refit": False,
        },
        "mesh": [args.mesh, args.mesh, args.mesh],
        "time_grid": {
            "start": 0.0,
            "stop": 100.0,
            "spacing": float(times[1] - times[0]),
            "points": len(times),
            "chunk_points": args.chunk_points,
        },
        "numpy_global_seed": seed,
        "budget_rows": rows,
        "limitations": [
            "low-mesh feasibility inspected before formal budget/mesh freeze",
            "PCHIP root estimates from spacing-0.05 traces, not pointwise formal roots",
            "no positive-B claim is permitted from this artifact",
        ],
    }
    write_json(args.output, payload)
    for row in rows:
        print(
            row["budget"],
            row["all_feasibility_gates_passed"],
            row["stationary_structure"]["valley_to_smaller_adjacent_peak_ratios"],
            row["stationary_structure"]["event_basin_reaction_masses"],
        )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
