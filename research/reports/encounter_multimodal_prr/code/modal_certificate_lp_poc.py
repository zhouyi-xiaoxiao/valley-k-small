#!/usr/bin/env python3
"""Exploratory convex modal-certificate construction at B downarrow 0.

This module never evaluates a killed positive-budget generator.  It selects
allocations from exact free-exposure channel derivatives and then diagnoses
their stationary topology with the existing exact continuum kernel.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import continuum_observable_four_patch as continuum
import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent
DEFAULT_OUTPUT = REPORT / "scratch" / "modal_certificate_lp_poc_result.json"

SCHEMA_VERSION = 1
STAGE = "exploratory_free_exposure_modal_certificate_lp"
STATUS_PASS = "PASS_EXPLORATORY_FREE_EXPOSURE_MODAL_CERTIFICATE"
STATUS_HOLD = "HOLD_EXPLORATORY_MODAL_CERTIFICATE"


@dataclass(frozen=True)
class SignCertificateSpec:
    """Ordered derivative-sign checkpoints for an at-least-m certificate."""

    name: str
    target_maxima: int
    times: tuple[float, ...]
    signs: tuple[int, ...]
    weight_floor: float

    def validate(self, channel_count: int) -> None:
        if not self.name:
            raise ValueError("certificate name must be nonempty")
        if self.target_maxima < 1:
            raise ValueError("target_maxima must be positive")
        if len(self.times) != 2 * self.target_maxima:
            raise ValueError("a target-m certificate requires exactly 2m checkpoints")
        if len(self.signs) != len(self.times):
            raise ValueError("checkpoint times and signs must have equal length")
        if any(sign not in (-1, 1) for sign in self.signs):
            raise ValueError("certificate signs must be exact integers +/-1")
        expected = tuple(1 if index % 2 == 0 else -1 for index in range(len(self.signs)))
        if self.signs != expected:
            raise ValueError("certificate signs must alternate starting with +1")
        if any(not math.isfinite(time) or time <= 0.0 for time in self.times):
            raise ValueError("checkpoint times must be finite and positive")
        if any(left >= right for left, right in zip(self.times, self.times[1:])):
            raise ValueError("checkpoint times must be strictly increasing")
        if not math.isfinite(self.weight_floor) or self.weight_floor < 0.0:
            raise ValueError("weight_floor must be finite and nonnegative")
        if channel_count < 1 or self.weight_floor * channel_count >= 1.0:
            raise ValueError("weight floor leaves no feasible simplex interior")


BROAD_SPECS = (
    SignCertificateSpec("m1", 1, (5.5, 12.0), (1, -1), 0.03),
    SignCertificateSpec("m2", 2, (2.0, 5.5, 16.0, 35.0), (1, -1, 1, -1), 0.03),
    SignCertificateSpec(
        "m3",
        3,
        (2.0, 5.0, 6.5, 11.0, 17.0, 35.0),
        (1, -1, 1, -1, 1, -1),
        0.03,
    ),
)


def solve_sign_certificate(
    channel_derivatives: np.ndarray,
    spec: SignCertificateSpec,
) -> dict[str, Any]:
    """Maximize the minimum row-scaled alternating derivative margin."""

    derivatives = np.asarray(channel_derivatives, dtype=float)
    if derivatives.ndim != 2:
        raise ValueError("channel_derivatives must be a two-dimensional array")
    row_count, channel_count = derivatives.shape
    spec.validate(channel_count)
    if row_count != len(spec.times):
        raise ValueError("one channel-derivative row is required per checkpoint")
    if not np.all(np.isfinite(derivatives)):
        raise ValueError("channel derivatives must all be finite")

    scales = np.max(np.abs(derivatives), axis=1)
    if np.any(~np.isfinite(scales)) or np.any(scales <= 0.0):
        raise ValueError("every derivative row must have a positive finite scale")

    inequalities = np.zeros((row_count, channel_count + 1), dtype=float)
    for index, (row, scale, sign) in enumerate(zip(derivatives, scales, spec.signs, strict=True)):
        inequalities[index, :channel_count] = -float(sign) * row / scale
        inequalities[index, channel_count] = 1.0

    objective = np.zeros(channel_count + 1, dtype=float)
    objective[-1] = -1.0
    equality = np.zeros((1, channel_count + 1), dtype=float)
    equality[0, :channel_count] = 1.0
    bounds = [(spec.weight_floor, 1.0)] * channel_count + [(0.0, None)]
    result = linprog(
        objective,
        A_ub=inequalities,
        b_ub=np.zeros(row_count, dtype=float),
        A_eq=equality,
        b_eq=np.ones(1, dtype=float),
        bounds=bounds,
        method="highs",
    )
    if not result.success or result.x is None:
        return {
            "status": STATUS_HOLD,
            "reason": "linear_program_failed",
            "solver_status": int(result.status),
            "solver_message": str(result.message),
            "target_maxima": spec.target_maxima,
            "times": list(spec.times),
            "signs": list(spec.signs),
            "weight_floor": spec.weight_floor,
            "weights": None,
            "normalized_margin": None,
            "signed_normalized_checkpoint_margins": None,
            "row_scales": scales.tolist(),
        }

    weights = np.asarray(result.x[:channel_count], dtype=float)
    solver_reported_margin = float(result.x[channel_count])
    signed_margins = np.asarray(spec.signs, dtype=float) * (derivatives @ weights) / scales
    margin = float(np.min(signed_margins))
    feasible = bool(
        margin > 0.0
        and np.all(weights >= spec.weight_floor - 2.0e-13)
        and abs(float(np.sum(weights)) - 1.0) <= 2.0e-13
    )
    return {
        "status": STATUS_PASS if feasible else STATUS_HOLD,
        "reason": "positive_margin" if feasible else "postsolve_feasibility_failed",
        "solver_status": int(result.status),
        "solver_message": str(result.message),
        "target_maxima": spec.target_maxima,
        "times": list(spec.times),
        "signs": list(spec.signs),
        "weight_floor": spec.weight_floor,
        "weights": weights.tolist(),
        "weight_sum_error": abs(float(np.sum(weights)) - 1.0),
        "minimum_weight": float(np.min(weights)),
        "normalized_margin": margin,
        "solver_reported_margin": solver_reported_margin,
        "signed_normalized_checkpoint_margins": signed_margins.tolist(),
        "row_scales": scales.tolist(),
    }


def broad_parameters() -> continuum.PhysicalParameters:
    return continuum.PhysicalParameters(initial_half_width=0.02, patch_half_width=0.04)


def select_broad_controls() -> dict[str, dict[str, Any]]:
    model = continuum.FourPatchContinuum(continuum.PRIMARY, broad_parameters())
    rows: dict[str, dict[str, Any]] = {}
    for spec in BROAD_SPECS:
        _channels, derivatives = model.real_channels_and_first_derivatives(
            np.asarray(spec.times, dtype=float)
        )
        rows[spec.name] = solve_sign_certificate(derivatives, spec)
    return rows


def _general_valley_ratios(roots: Sequence[dict[str, Any]]) -> list[float]:
    ratios: list[float] = []
    for index in range(1, len(roots) - 1):
        row = roots[index]
        if row["topology"] != "minimum":
            continue
        left = roots[index - 1]
        right = roots[index + 1]
        if left["topology"] != "maximum" or right["topology"] != "maximum":
            raise ValueError("stationary roots do not alternate around a minimum")
        denominator = min(float(left["density"]), float(right["density"]))
        if denominator <= 0.0:
            raise ValueError("valley ratio requires positive adjacent peak densities")
        ratios.append(float(row["density"]) / denominator)
    return ratios


def _stationary_summary(structure: dict[str, Any]) -> dict[str, Any]:
    roots = structure["roots"]
    return {
        "stationary_root_count": int(structure["stationary_root_count"]),
        "topology": list(structure["topology"]),
        "roots": [
            {
                "time": float(row["time"]),
                "topology": str(row["topology"]),
                "density": float(row["density"]),
                "scaled_second_derivative": float(row["scaled_second_derivative"]),
                "scaled_first_derivative_residual": float(row["scaled_first_derivative_residual"]),
            }
            for row in roots
        ],
        "peak_minimum_to_maximum_ratio": float(structure["peak_minimum_to_maximum_ratio"]),
        "valley_to_smaller_adjacent_peak_ratios": _general_valley_ratios(roots),
        "derivative_at_time_start": float(structure["derivative_at_time_start"]),
        "derivative_at_time_stop": float(structure["derivative_at_time_stop"]),
    }


def build_broad_exploratory_result() -> dict[str, Any]:
    controls = select_broad_controls()
    if any(row["status"] != STATUS_PASS for row in controls.values()):
        return {
            "schema_version": SCHEMA_VERSION,
            "stage": STAGE,
            "status": STATUS_HOLD,
            "reason": "one_or_more_lp_controls_held",
            "controls": controls,
        }

    time_grid = np.linspace(0.1, 100.0, 49_951, dtype=float)
    configurations = (
        ("coarse", continuum.COARSE),
        ("primary", continuum.PRIMARY),
        ("fine", continuum.FINE),
    )
    validation: dict[str, dict[str, Any]] = {}
    for configuration_name, configuration in configurations:
        model = continuum.FourPatchContinuum(configuration, broad_parameters())
        channels, derivatives = model.real_channels_and_first_derivatives(time_grid)
        configuration_rows: dict[str, Any] = {}
        for spec in BROAD_SPECS:
            weights = np.asarray(controls[spec.name]["weights"], dtype=float)
            structure = continuum.stationary_structure(
                model,
                weights,
                time_grid,
                channels,
                derivatives,
                relative_density_floor=1.0e-8,
                derivative_zero_relative_tolerance=1.0e-12,
            )
            configuration_rows[spec.name] = _stationary_summary(structure)
        validation[configuration_name] = configuration_rows

    expected_topologies = {
        "m1": ["maximum"],
        "m2": ["maximum", "minimum", "maximum"],
        "m3": ["maximum", "minimum", "maximum", "minimum", "maximum"],
    }
    topology_gate = all(
        validation[configuration][name]["topology"] == expected
        for configuration in validation
        for name, expected in expected_topologies.items()
    )
    maximum_root_time_spread = 0.0
    maximum_scaled_curvature_spread = 0.0
    for name in expected_topologies:
        root_count = len(expected_topologies[name])
        for root_index in range(root_count):
            times = [
                validation[configuration][name]["roots"][root_index]["time"]
                for configuration in validation
            ]
            curvatures = [
                validation[configuration][name]["roots"][root_index]["scaled_second_derivative"]
                for configuration in validation
            ]
            maximum_root_time_spread = max(maximum_root_time_spread, max(times) - min(times))
            maximum_scaled_curvature_spread = max(
                maximum_scaled_curvature_spread,
                max(curvatures) - min(curvatures),
            )
    quadrature_gate = bool(
        maximum_root_time_spread <= 1.0e-7 and maximum_scaled_curvature_spread <= 1.0e-6
    )
    positive_margin_gate = all(
        row["normalized_margin"] is not None and row["normalized_margin"] > 0.0
        for row in controls.values()
    )
    gates = {
        "all_lp_margins_positive": positive_margin_gate,
        "expected_1_2_3_mode_topologies_on_all_quadratures": topology_gate,
        "root_and_curvature_quadrature_spread": quadrature_gate,
    }
    all_gates_passed = all(gates.values())
    pars = broad_parameters()
    return {
        "schema_version": SCHEMA_VERSION,
        "stage": STAGE,
        "status": STATUS_PASS if all_gates_passed else STATUS_HOLD,
        "evidence_timing": "POST_ALLOCATION_V6_HOLD_EXPLORATORY_B0_ONLY",
        "claim_scope": (
            "Exploratory maximum-margin allocations from exact d=2 broad-family "
            "free-exposure channel derivatives, checked on three quadrature configurations."
        ),
        "positive_budget_evaluated": False,
        "physical_parameters": {
            "particle_diffusion": pars.particle_diffusion,
            "ou_stiffness": pars.ou_stiffness,
            "ou_mean": pars.ou_mean,
            "transverse_width": pars.transverse_width,
            "contact_radius": pars.contact_radius,
            "midpoint_start": pars.midpoint_start,
            "initial_half_width": pars.initial_half_width,
            "relative_parallel_start": pars.relative_parallel_start,
            "relative_perp_start": pars.relative_perp_start,
            "patch_centres": list(pars.patch_centres),
            "patch_half_width": pars.patch_half_width,
        },
        "selection": {
            "method": "linear_program_maximum_normalized_alternating_derivative_margin",
            "row_scale": "maximum_absolute_channel_derivative_at_each_checkpoint",
            "solver": "scipy.optimize.linprog(method=highs)",
            "controls": controls,
        },
        "time_diagnostic": {
            "start": 0.1,
            "stop": 100.0,
            "points": 49_951,
            "spacing": 0.002,
            "interval_certified": False,
        },
        "quadrature_validation": validation,
        "maximum_root_time_spread": maximum_root_time_spread,
        "maximum_scaled_curvature_spread": maximum_scaled_curvature_spread,
        "gates": gates,
        "all_gates_passed": all_gates_passed,
        "limitations": [
            "exploratory result-informed free-exposure design, not preregistered discovery",
            "dense floating-point sign/root diagnostic, not interval certification",
            "no positive-budget killed-Doi evaluation",
            "no event-basin mass, box, mesh, alignment, or independent-process evidence",
            "does not rescue or alter the terminal allocation-v6 scientific HOLD",
            "not a project or publication gate",
        ],
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-exploratory-b0",
        action="store_true",
        help="run only the exact free-exposure broad-family exploratory calculation",
    )
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.execute_exploratory_b0:
        raise SystemExit("explicit --execute-exploratory-b0 is required")
    result = build_broad_exploratory_result()
    rendered = canonical_json(result)
    output = args.output
    if output is not None:
        output = output.resolve()
        if output != DEFAULT_OUTPUT.resolve():
            raise SystemExit(f"output must be exactly {DEFAULT_OUTPUT}")
        if output.exists():
            raise SystemExit("exploratory output already exists; refusing overwrite")
        output.write_text(rendered, encoding="utf-8")
        print(output)
    else:
        print(rendered, end="")
    return 0 if result["status"] == STATUS_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())
