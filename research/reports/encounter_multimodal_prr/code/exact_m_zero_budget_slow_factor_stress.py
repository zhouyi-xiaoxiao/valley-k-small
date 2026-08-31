#!/usr/bin/env python3
"""Deterministic B=0 stress test for the exact-m slow-factor theorem.

This is a numerical sanity check, not a root-exclusion certificate.  It uses a
dense deterministic sign scan and bisection on several declared common-scale
Gaussian mixtures.  The script never constructs a killed generator and never
evaluates positive budget.  Even a PASS cannot replace the analytic
posterior-sector proof in ``exact_m_mode_encounter_theorem_v2.md``.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

STATUS = "PASS_DETERMINISTIC_B0_STRESS_NOT_A_TOPOLOGY_CERTIFICATE"
WINDOW = (-1.7, 1.75)
SIGMAS = (0.16, 0.11, 0.075, 0.05)
GRID_SIZE = 300_001
BISECTION_STEPS = 90


@dataclass(frozen=True)
class StressCase:
    name: str
    centres: tuple[float, ...]
    weights: tuple[float, ...]

    @property
    def expected_roots(self) -> int:
        return 2 * len(self.centres) - 1


CASES = (
    StressCase("m1", (-0.2,), (1.0,)),
    StressCase("m2_weight_edge", (-0.8, 0.7), (0.03, 0.97)),
    StressCase("m3_weight_edge", (-1.0, 0.0, 1.0), (0.03, 0.61, 0.36)),
    StressCase(
        "m4_irregular",
        (-1.1, -0.25, 0.55, 1.25),
        (0.18, 0.31, 0.22, 0.29),
    ),
)


def _posterior_stats(
    x: float,
    sigma: float,
    centres: Sequence[float],
    weights: Sequence[float],
) -> tuple[float, float]:
    c = np.asarray(centres, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    log_terms = np.log(w) - 0.5 * ((x - c) / sigma) ** 2
    log_terms -= float(np.max(log_terms))
    posterior = np.exp(log_terms)
    posterior /= float(np.sum(posterior))
    mean = float(posterior @ c)
    variance = float(posterior @ ((c - mean) ** 2))
    return mean, variance


def _b(x: float, *, slow: bool) -> float:
    return 0.52 * math.cos(4.0 * x) if slow else 0.0


def _b_prime(x: float, *, slow: bool) -> float:
    return -2.08 * math.sin(4.0 * x) if slow else 0.0


def _d(
    x: float,
    sigma: float,
    case: StressCase,
    *,
    slow: bool,
) -> float:
    mean, _ = _posterior_stats(x, sigma, case.centres, case.weights)
    return _b(x, slow=slow) + (mean - x) / sigma**2


def _d_prime(
    x: float,
    sigma: float,
    case: StressCase,
    *,
    slow: bool,
) -> float:
    _, variance = _posterior_stats(x, sigma, case.centres, case.weights)
    return _b_prime(x, slow=slow) + variance / sigma**4 - 1.0 / sigma**2


def _roots(case: StressCase, sigma: float, *, slow: bool) -> list[float]:
    xs = np.linspace(WINDOW[0], WINDOW[1], GRID_SIZE, dtype=np.float64)
    centres = np.asarray(case.centres, dtype=np.float64)
    weights = np.asarray(case.weights, dtype=np.float64)
    log_terms = (
        np.log(weights)[None, :]
        - 0.5 * ((xs[:, None] - centres[None, :]) / sigma) ** 2
    )
    log_terms -= np.max(log_terms, axis=1)[:, None]
    posterior = np.exp(log_terms)
    posterior /= np.sum(posterior, axis=1)[:, None]
    mean = posterior @ centres
    values = (0.52 * np.cos(4.0 * xs) if slow else 0.0) + (mean - xs) / sigma**2
    brackets = np.flatnonzero(values[:-1] * values[1:] < 0.0)

    roots: list[float] = []
    for index in brackets:
        left = float(xs[index])
        right = float(xs[index + 1])
        f_left = _d(left, sigma, case, slow=slow)
        for _ in range(BISECTION_STEPS):
            midpoint = (left + right) / 2.0
            f_midpoint = _d(midpoint, sigma, case, slow=slow)
            if f_left * f_midpoint <= 0.0:
                right = midpoint
            else:
                left = midpoint
                f_left = f_midpoint
        roots.append((left + right) / 2.0)
    return roots


def _row(case: StressCase, sigma: float) -> dict[str, Any]:
    pure = _roots(case, sigma, slow=False)
    slow = _roots(case, sigma, slow=True)
    types = [
        "max" if _d_prime(root, sigma, case, slow=True) < 0.0 else "min"
        for root in slow
    ]
    expected_types = [
        "max" if index % 2 == 0 else "min"
        for index in range(case.expected_roots)
    ]
    peak_scaled_shifts = [
        abs(slow[index] - pure[index]) / sigma**2
        for index in range(0, len(slow), 2)
    ]
    valley_scaled_shifts = [
        abs(slow[index] - pure[index]) / sigma**4
        for index in range(1, len(slow), 2)
    ]
    passed = (
        len(pure) == case.expected_roots
        and len(slow) == case.expected_roots
        and types == expected_types
        and _d(WINDOW[0], sigma, case, slow=True) > 0.0
        and _d(WINDOW[1], sigma, case, slow=True) < 0.0
        and max(peak_scaled_shifts, default=0.0) < 1.0
        and max(valley_scaled_shifts, default=0.0) < 8.0
    )
    return {
        "case": case.name,
        "sigma": sigma,
        "expected_root_count": case.expected_roots,
        "pure_root_count": len(pure),
        "slow_root_count": len(slow),
        "slow_root_types": types,
        "slow_roots": slow,
        "max_abs_peak_shift_over_sigma2": max(peak_scaled_shifts, default=0.0),
        "max_abs_valley_shift_over_sigma4": max(valley_scaled_shifts, default=0.0),
        "endpoint_signs": [
            math.copysign(1.0, _d(WINDOW[0], sigma, case, slow=True)),
            math.copysign(1.0, _d(WINDOW[1], sigma, case, slow=True)),
        ],
        "pass": passed,
    }


def build_result() -> dict[str, Any]:
    rows = [_row(case, sigma) for case in CASES for sigma in SIGMAS]
    crossover_ratios = {
        str(constant): math.exp(-constant) for constant in (1.0, 4.0, 8.0)
    }
    all_pass = all(row["pass"] for row in rows)
    return {
        "schema_version": 1,
        "status": STATUS if all_pass else "HOLD_B0_STRESS_FAILURE",
        "positive_budget_evaluated": False,
        "killed_generator_constructed": False,
        "claim_boundary": (
            "dense sign scans can miss even roots and are not interval or "
            "topology certificates"
        ),
        "slow_factor": {
            "a": "exp(0.13*sin(4*x))",
            "b": "0.52*cos(4*x)",
            "sup_abs_b": 0.52,
            "sup_abs_b_prime": 2.08,
        },
        "window": list(WINDOW),
        "grid_size": GRID_SIZE,
        "bisection_steps": BISECTION_STEPS,
        "rows": rows,
        "fixed_crossover_edge_ratios": crossover_ratios,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute-b0-stress",
        action="store_true",
        help="run the declared zero-budget stress test and print canonical JSON",
    )
    args = parser.parse_args(argv)
    if not args.execute_b0_stress:
        parser.error("explicit --execute-b0-stress is required")
    result = build_result()
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
