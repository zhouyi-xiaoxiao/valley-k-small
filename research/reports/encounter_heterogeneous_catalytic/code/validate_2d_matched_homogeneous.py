#!/usr/bin/env python3
"""Matched homogeneous control for patterned 2D encounter reactivity.

Confinement alone can create a late encounter hump.  This script therefore
does not compare a patterned catalyst with a weak arbitrary homogeneous sink.
For every grid it constructs a homogeneous Doi sink whose *integrated killing
strength on the same discrete encounter tube* exactly equals that of the
patterned sink.  The transport, initial condition, reaction radius, domain,
and boundary conditions are otherwise identical.

The resulting comparison isolates reactivity-induced secondary-mode
amplification.  With a joint contact-safe hierarchical initial law, the
patterned model is canonically resolved-bimodal on the four finer grids and a
resolved shoulder on the coarsest grid; every principal state-sum matched
homogeneous control is resolved-unimodal.  The product-control-volume
sensitivity has one classifier shoulder but no accepted two-peak scale view.
Detected sign changes, Brent-refined with finite-matrix semigroup derivative
evaluations on the declared windows, retain both secondary maxima on all five
grids.  Thus patterning amplifies a detected transport mode rather than
creating its observed finite-window existence.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq
from scipy.sparse.linalg import expm_multiply
from vkcore.encounter2d import (
    DoiCatalyticPatch,
    RectangularGrid2D,
    build_doi_encounter_2d,
    contact_safe_initial_distribution_2d,
    initial_distribution_diagnostics_2d,
    reflecting_advection_diffusion_generator_2d,
    solve_doi_encounter_2d,
)
from vkcore.morphology import MorphologyConfig, analyze_fpt_morphology
from vkcore.plotting import enforce_publication_graphics
from vkcore.provenance import build_artifact_manifest, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
FIGURES = REPORT / "artifacts" / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

GRIDS = ((9, 5), (11, 7), (13, 9), (15, 11), (17, 13))
REACTION_RADIUS = 0.13
START_ONE = (0.10, 0.50)
START_TWO = (0.35, 0.50)
WALKER_ONE = {
    "diffusion": 0.0025,
    "drift_x": 0.18,
    "transverse_confinement": 1.5,
}
WALKER_TWO = {
    "diffusion": 0.0008,
    "drift_x": 0.02,
    "transverse_confinement": 1.5,
}
PATTERNED_PATCHES = (
    DoiCatalyticPatch((0.25, 0.50), 0.18, 0.50, "near"),
    DoiCatalyticPatch((0.72, 0.50), 0.20, 15.00, "far"),
)
CONTINUUM_PATTERNED_AREA_WEIGHT = float(
    np.pi
    * sum(patch.radius**2 * patch.reaction_rate for patch in PATTERNED_PATCHES)
)
CONTINUUM_RELATIVE_DISK_AREA = float(np.pi * REACTION_RADIUS**2)
CONTINUUM_ENCOUNTER_TUBE_VOLUME = float(
    np.pi * REACTION_RADIUS**2
    - (8.0 / 3.0) * REACTION_RADIUS**3
    + 0.5 * REACTION_RADIUS**4
)
CONTINUUM_FINITE_A_MATCHED_RATE = float(
    CONTINUUM_PATTERNED_AREA_WEIGHT
    * CONTINUUM_RELATIVE_DISK_AREA
    / CONTINUUM_ENCOUNTER_TUBE_VOLUME
)
SHAPE_TIMES = np.linspace(0.0, 80.0, 801)
TAIL_TIME = 960.0
LATE_AUDIT_SAMPLES = 221
CUTOFF_SWEEP_SAMPLES = 101

MORPHOLOGY = MorphologyConfig(
    smoothing_windows=(1, 3, 5, 9, 15),
    bin_widths=(1, 2, 4, 8, 16),
    bin_offsets=(),
    min_peak_height_rel=0.03,
    min_prominence_rel=0.015,
    min_lobe_mass_rel=0.01,
    min_r_peak=0.05,
    max_r_valley=0.80,
    min_peak_separation_widths=1.0,
    expected_total_mass=1.0,
    mass_tolerance=0.03,
)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
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


def _morphology(result, *, config: MorphologyConfig = MORPHOLOGY):
    dt = float(result.times[1] - result.times[0])
    probability_mass = result.total_flux_density * dt
    probability_mass[[0, -1]] *= 0.5
    return analyze_fpt_morphology(
        probability_mass,
        times=result.times,
        config=config,
        tail_mass_upper_bound=result.tail_mass + result.quadrature_closure_error,
    )


def _late_audit(model, initial) -> dict[str, Any]:
    """Audit detected late maxima with finite-matrix semigroup derivatives.

    The declared mesh only supplies sign-change brackets.  Within each
    positive-to-negative bracket, Brent refinement evaluates
    ``alpha exp(T t) T b`` directly; sampled density comparisons are not used.
    This audit does not isolate tangential roots or roots outside its horizon.
    """

    times = np.linspace(
        float(SHAPE_TIMES[-1]),
        TAIL_TIME,
        LATE_AUDIT_SAMPLES,
    )
    states = expm_multiply(
        model.killed_generator.T,
        initial,
        start=float(times[0]),
        stop=float(times[-1]),
        num=times.size,
        endpoint=True,
    )
    total_rate = np.asarray(model.channel_rate_matrix.sum(axis=1)).reshape(-1)
    derivative_vector = np.asarray(model.killed_generator @ total_rate).reshape(-1)
    derivatives = np.asarray(states @ derivative_vector).reshape(-1)
    maximum_brackets = np.flatnonzero(
        (derivatives[:-1] > 0.0) & (derivatives[1:] <= 0.0)
    )

    def semigroup_derivative(time: float) -> float:
        state = expm_multiply(model.killed_generator.T * float(time), initial)
        return float(np.dot(state, derivative_vector))

    maximum_roots = [
        float(
            brentq(
                semigroup_derivative,
                float(times[index]),
                float(times[index + 1]),
                xtol=2e-12,
                rtol=2e-14,
            )
        )
        for index in maximum_brackets
    ]
    return {
        "tail_survival": float(np.sum(states[-1])),
        "maximum_sign_change_count": len(maximum_roots),
        "maximum_root_times": maximum_roots,
        "mesh_start": float(times[0]),
        "mesh_stop": float(times[-1]),
        "mesh_samples": int(times.size),
        "mesh_step": float(times[1] - times[0]),
        "bracketing_quantity": "alpha exp(T t) T b",
        "root_refinement": (
            "Brent refinement using finite-matrix semigroup first-derivative "
            "evaluations within the declared late-audit horizon"
        ),
    }


def _positive_views(morphology) -> int:
    return int(
        sum(
            len(view.accepted_peak_indices) >= 2
            for view in morphology.scale_views
            if not view.excluded_from_persistence
        )
    )


def _product_trapezoidal_weights(grid: RectangularGrid2D) -> np.ndarray:
    """Four-dimensional product control-volume weights for a boundary grid."""

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


def _resolution_diagnostics(grid: RectangularGrid2D) -> dict[str, Any]:
    def walker(parameters: dict[str, float]) -> dict[str, float]:
        diffusion = float(parameters["diffusion"])
        pe_x = abs(float(parameters["drift_x"])) * grid.spacing_x / diffusion
        pe_y = (
            float(parameters["transverse_confinement"])
            * 0.5
            * grid.spacing_y
            / diffusion
        )
        return {
            "cell_peclet_x": pe_x,
            "upwind_effective_diffusion_x_ratio": 1.0 + 0.5 * pe_x,
            "maximum_boundary_cell_peclet_y": pe_y,
            "one_cell_from_centre_peclet_y": (
                float(parameters["transverse_confinement"])
                * grid.spacing_y**2
                / diffusion
            ),
        }

    return {
        "interpretation": (
            "finite-lattice family; not a controlled continuum-SDE refinement"
        ),
        "reaction_radius_over_spacing_x": REACTION_RADIUS / grid.spacing_x,
        "reaction_radius_over_spacing_y": REACTION_RADIUS / grid.spacing_y,
        "walker_one": walker(WALKER_ONE),
        "walker_two": walker(WALKER_TWO),
    }


def _strict_stationary_points(model: Any, initial: np.ndarray) -> list[dict[str, Any]]:
    """Detect and Brent-refine sign changes on the declared shape window."""

    states = np.asarray(
        expm_multiply(
            model.killed_generator.T,
            initial,
            start=float(SHAPE_TIMES[0]),
            stop=float(SHAPE_TIMES[-1]),
            num=SHAPE_TIMES.size,
            endpoint=True,
        ),
        dtype=float,
    )
    rate = np.asarray(
        model.channel_rate_matrix.sum(axis=1), dtype=float
    ).reshape(-1)
    first_observable = np.asarray(model.killed_generator @ rate, dtype=float)
    second_observable = np.asarray(
        model.killed_generator @ first_observable, dtype=float
    )
    sampled_first = np.asarray(states @ first_observable, dtype=float)
    brackets = np.flatnonzero(
        np.signbit(sampled_first[:-1]) != np.signbit(sampled_first[1:])
    )

    def values(time: float) -> tuple[float, float, float]:
        state = np.asarray(
            expm_multiply(model.killed_generator.T * float(time), initial),
            dtype=float,
        )
        return (
            float(state @ rate),
            float(state @ first_observable),
            float(state @ second_observable),
        )

    roots: list[dict[str, Any]] = []
    for index in brackets:
        left = float(SHAPE_TIMES[index])
        right = float(SHAPE_TIMES[index + 1])
        root_time = float(
            brentq(
                lambda time: values(time)[1],
                left,
                right,
                xtol=2e-12,
                rtol=2e-14,
            )
        )
        density, first, second = values(root_time)
        roots.append(
            {
                "time": root_time,
                "density": density,
                "f_t": first,
                "f_tt": second,
                "type": "maximum" if second < 0.0 else "minimum",
            }
        )
    return roots


def main() -> None:
    rows: list[dict[str, Any]] = []
    archive: dict[str, np.ndarray] = {}
    sweep_inputs: dict[tuple[int, int, str], Any] = {}
    for nx, ny in GRIDS:
        grid = RectangularGrid2D(nx, ny)
        generator_one = reflecting_advection_diffusion_generator_2d(
            grid, **WALKER_ONE
        )
        generator_two = reflecting_advection_diffusion_generator_2d(
            grid, **WALKER_TWO
        )
        patterned = build_doi_encounter_2d(
            grid,
            generator_one,
            generator_two,
            reaction_radius=REACTION_RADIUS,
            patches=PATTERNED_PATCHES,
            centre_weight=0.5,
        )
        homogeneous_unit = build_doi_encounter_2d(
            grid,
            generator_one,
            generator_two,
            reaction_radius=REACTION_RADIUS,
            patches=(DoiCatalyticPatch((0.50, 0.50), 2.0, 1.0, "uniform"),),
            centre_weight=0.5,
        )
        patterned_integrated_rate = float(patterned.channel_rate_matrix.sum())
        unit_integrated_rate = float(homogeneous_unit.channel_rate_matrix.sum())
        matched_rate = patterned_integrated_rate / unit_integrated_rate
        product_weights = _product_trapezoidal_weights(grid)
        patterned_rate_vector = np.asarray(
            patterned.channel_rate_matrix.sum(axis=1)
        ).reshape(-1)
        unit_rate_vector = np.asarray(
            homogeneous_unit.channel_rate_matrix.sum(axis=1)
        ).reshape(-1)
        weighted_patterned_budget = float(
            np.dot(product_weights, patterned_rate_vector)
        )
        weighted_unit_budget = float(np.dot(product_weights, unit_rate_vector))
        weighted_matched_rate = weighted_patterned_budget / weighted_unit_budget
        homogeneous = build_doi_encounter_2d(
            grid,
            generator_one,
            generator_two,
            reaction_radius=REACTION_RADIUS,
            patches=(
                DoiCatalyticPatch(
                    (0.50, 0.50),
                    2.0,
                    matched_rate,
                    "uniform_matched",
                ),
            ),
            centre_weight=0.5,
        )
        homogeneous_integrated_rate = float(homogeneous.channel_rate_matrix.sum())
        weighted_homogeneous = build_doi_encounter_2d(
            grid,
            generator_one,
            generator_two,
            reaction_radius=REACTION_RADIUS,
            patches=(
                DoiCatalyticPatch(
                    (0.50, 0.50),
                    2.0,
                    weighted_matched_rate,
                    "uniform_product_trapezoidal_matched",
                ),
            ),
            centre_weight=0.5,
        )
        weighted_homogeneous_rate_vector = np.asarray(
            weighted_homogeneous.channel_rate_matrix.sum(axis=1)
        ).reshape(-1)
        weighted_homogeneous_budget = float(
            np.dot(product_weights, weighted_homogeneous_rate_vector)
        )
        initial = contact_safe_initial_distribution_2d(
            patterned, START_ONE, START_TWO
        )
        initial_diagnostics = initial_distribution_diagnostics_2d(
            patterned,
            initial,
            walker1_position=START_ONE,
            walker2_position=START_TWO,
        )

        outputs: dict[
            str, tuple[Any, Any, dict[str, Any], list[dict[str, Any]]]
        ] = {}
        patterned_expected = "shoulder" if (nx, ny) == (9, 5) else "bimodal"
        for label, model, expected in (
            ("patterned", patterned, patterned_expected),
            ("homogeneous", homogeneous, "unimodal"),
        ):
            result = solve_doi_encounter_2d(model, initial, SHAPE_TIMES)
            morphology = _morphology(result)
            if morphology.classification != expected:
                raise RuntimeError(
                    f"grid {(nx, ny)} {label} classified "
                    f"{morphology.classification}, expected {expected}"
                )
            late_audit = _late_audit(model, initial)
            strict_points = _strict_stationary_points(model, initial)
            outputs[label] = (
                result,
                morphology,
                late_audit,
                strict_points,
            )
            sweep_inputs[(nx, ny, label)] = result
            key = f"g{nx}x{ny}_{label}"
            archive[f"{key}_times"] = result.times
            archive[f"{key}_density"] = result.total_flux_density
            archive[f"{key}_channels"] = result.channel_flux_density

        weighted_result = solve_doi_encounter_2d(
            weighted_homogeneous,
            initial,
            SHAPE_TIMES,
        )
        weighted_morphology = _morphology(weighted_result)
        weighted_late_audit = _late_audit(weighted_homogeneous, initial)
        weighted_strict = _strict_stationary_points(weighted_homogeneous, initial)
        weighted_maxima = [
            point for point in weighted_strict if point["type"] == "maximum"
        ]
        weighted_strict_peak_ratio = (
            min(float(point["density"]) for point in weighted_maxima)
            / max(float(point["density"]) for point in weighted_maxima)
            if len(weighted_maxima) >= 2
            else 0.0
        )
        weighted_positive_views = _positive_views(weighted_morphology)
        if weighted_positive_views != 0 or weighted_strict_peak_ratio >= 0.03:
            raise RuntimeError(
                f"grid {(nx, ny)} weighted-budget homogeneous control became resolved"
            )
        weighted_key = f"g{nx}x{ny}_homogeneous_product_trapezoidal"
        sweep_inputs[(nx, ny, "homogeneous_product_trapezoidal")] = weighted_result
        archive[f"{weighted_key}_times"] = weighted_result.times
        archive[f"{weighted_key}_density"] = weighted_result.total_flux_density
        archive[f"{weighted_key}_channels"] = weighted_result.channel_flux_density

        (
            patterned_result,
            patterned_morphology,
            patterned_late_audit,
            patterned_strict,
        ) = outputs["patterned"]
        (
            homogeneous_result,
            homogeneous_morphology,
            homogeneous_late_audit,
            homogeneous_strict,
        ) = outputs["homogeneous"]
        homogeneous_maxima = [
            point for point in homogeneous_strict if point["type"] == "maximum"
        ]
        patterned_maxima = [
            point for point in patterned_strict if point["type"] == "maximum"
        ]
        if len(homogeneous_maxima) < 2 or len(patterned_maxima) < 2:
            raise RuntimeError(
                f"grid {(nx, ny)} lost an audited strict secondary maximum"
            )
        homogeneous_strict_peak_ratio = min(
            float(point["density"]) for point in homogeneous_maxima
        ) / max(float(point["density"]) for point in homogeneous_maxima)
        patterned_strict_peak_ratio = min(
            float(point["density"]) for point in patterned_maxima
        ) / max(float(point["density"]) for point in patterned_maxima)
        valley = (
            patterned_morphology.qualifying_valleys[0]
            if patterned_morphology.qualifying_valleys
            else None
        )
        rows.append(
            {
                "family_id": "M2D-E",
                "branch_id": "equal_budget_endpoint_amplification",
                "evidence_relationship": (
                    "five correlated grid evaluations of one M2D-E endpoint "
                    "family; not five independent model families"
                ),
                "nx": nx,
                "ny": ny,
                "spacing_x": grid.spacing_x,
                "spacing_y": grid.spacing_y,
                "product_states": patterned.state_count,
                "initial_distribution": asdict(initial_diagnostics),
                "patterned_classification": patterned_morphology.classification,
                "homogeneous_classification": homogeneous_morphology.classification,
                "classification_semantics": (
                    "canonical resolved morphology, not strict stationary-point count"
                ),
                "patterned_resolved_classification": (
                    f"resolved_{patterned_morphology.classification}"
                ),
                "homogeneous_resolved_classification": "resolved_unimodal",
                "patterned_strict_stationary_points": patterned_strict,
                "homogeneous_strict_stationary_points": homogeneous_strict,
                "patterned_strict_mode_count": sum(
                    point["type"] == "maximum" for point in patterned_strict
                ),
                "homogeneous_strict_mode_count": len(homogeneous_maxima),
                "patterned_strict_secondary_peak_ratio": (
                    patterned_strict_peak_ratio
                ),
                "homogeneous_strict_secondary_peak_ratio": (
                    homogeneous_strict_peak_ratio
                ),
                "patterned_peak_early": patterned_morphology.modal_peaks[0].time,
                "patterned_peak_late": (
                    patterned_morphology.modal_peaks[1].time
                    if len(patterned_morphology.modal_peaks) > 1
                    else float(patterned_maxima[-1]["time"])
                ),
                "homogeneous_peak": homogeneous_morphology.modal_peaks[0].time,
                "patterned_R_peak": None if valley is None else valley.r_peak,
                "patterned_R_valley": None if valley is None else valley.r_valley,
                "patterned_separation_widths": (
                    None if valley is None else valley.separation_widths
                ),
                "contact_safe_resolved_bimodal": (
                    patterned_morphology.classification == "bimodal"
                ),
                "patterned_positive_scale_views": _positive_views(
                    patterned_morphology
                ),
                "homogeneous_positive_scale_views": _positive_views(
                    homogeneous_morphology
                ),
                "scale_views": len(patterned_morphology.scale_views),
                "patterned_shape_tail": patterned_result.tail_mass,
                "homogeneous_shape_tail": homogeneous_result.tail_mass,
                "patterned_tail_at_960": patterned_late_audit["tail_survival"],
                "homogeneous_tail_at_960": homogeneous_late_audit["tail_survival"],
                "patterned_post_window_local_maxima": patterned_late_audit[
                    "maximum_sign_change_count"
                ],
                "homogeneous_post_window_local_maxima": homogeneous_late_audit[
                    "maximum_sign_change_count"
                ],
                "patterned_late_derivative_audit": patterned_late_audit,
                "homogeneous_late_derivative_audit": homogeneous_late_audit,
                "patterned_integrated_killing": patterned_integrated_rate,
                "homogeneous_integrated_killing": homogeneous_integrated_rate,
                "integrated_killing_relative_error": abs(
                    homogeneous_integrated_rate - patterned_integrated_rate
                )
                / patterned_integrated_rate,
                "matched_homogeneous_rate": matched_rate,
                "product_trapezoidal_matched_homogeneous_rate": (
                    weighted_matched_rate
                ),
                "product_trapezoidal_patterned_budget": weighted_patterned_budget,
                "product_trapezoidal_homogeneous_budget": weighted_homogeneous_budget,
                "product_trapezoidal_budget_relative_error": abs(
                    weighted_homogeneous_budget - weighted_patterned_budget
                )
                / weighted_patterned_budget,
                "product_trapezoidal_homogeneous_classification": (
                    weighted_morphology.classification
                ),
                "product_trapezoidal_homogeneous_resolved_classification": (
                    f"resolved_{weighted_morphology.classification}"
                ),
                "product_trapezoidal_homogeneous_strict_stationary_points": (
                    weighted_strict
                ),
                "product_trapezoidal_homogeneous_strict_mode_count": len(
                    weighted_maxima
                ),
                "product_trapezoidal_homogeneous_strict_secondary_peak_ratio": (
                    weighted_strict_peak_ratio
                ),
                "product_trapezoidal_homogeneous_positive_scale_views": (
                    weighted_positive_views
                ),
                "product_trapezoidal_homogeneous_tail_at_960": (
                    weighted_late_audit["tail_survival"]
                ),
                "product_trapezoidal_homogeneous_post_window_local_maxima": (
                    weighted_late_audit["maximum_sign_change_count"]
                ),
                "product_trapezoidal_homogeneous_late_derivative_audit": (
                    weighted_late_audit
                ),
                "continuum_patterned_area_weight": CONTINUUM_PATTERNED_AREA_WEIGHT,
                "continuum_relative_disk_area": CONTINUUM_RELATIVE_DISK_AREA,
                "continuum_encounter_tube_volume": CONTINUUM_ENCOUNTER_TUBE_VOLUME,
                "continuum_finite_a_matched_rate": CONTINUUM_FINITE_A_MATCHED_RATE,
                "far_patch_boundary_clearance": 1.0
                - PATTERNED_PATCHES[1].centre[0]
                - PATTERNED_PATCHES[1].radius,
                "resolution_diagnostics": _resolution_diagnostics(grid),
                "evidence_grade": (
                    "verified_contact_safe_secondary_mode_amplification"
                    if patterned_late_audit["tail_survival"] < 1e-8
                    and homogeneous_late_audit["tail_survival"] < 1e-8
                    and patterned_late_audit["maximum_sign_change_count"] == 0
                    and homogeneous_late_audit["maximum_sign_change_count"] == 0
                    else "conditional"
                ),
            }
        )

    # This open interval separates the *strict stationary-point height ratios*.
    # It is not itself a classifier theorem.  Re-evaluate the full morphology
    # classifier on a dense, explicitly persisted set of interior cutoffs.
    threshold_lower = max(
        max(
            row["homogeneous_strict_secondary_peak_ratio"],
            row[
                "product_trapezoidal_homogeneous_strict_secondary_peak_ratio"
            ],
        )
        for row in rows
    )
    threshold_upper = min(
        row["patterned_strict_secondary_peak_ratio"] for row in rows
    )
    if not threshold_lower < MORPHOLOGY.min_peak_height_rel < threshold_upper:
        raise RuntimeError("declared peak-height cutoff is outside the robust interval")
    sweep_margin = threshold_upper - threshold_lower
    sweep_cutoffs = np.linspace(
        threshold_lower + 1e-6 * sweep_margin,
        threshold_upper - 1e-6 * sweep_margin,
        CUTOFF_SWEEP_SAMPLES,
    )
    sweep_labels = (
        "patterned",
        "homogeneous",
        "homogeneous_product_trapezoidal",
    )
    for row in rows:
        nx = int(row["nx"])
        ny = int(row["ny"])
        expected = {
            "patterned": row["patterned_classification"],
            "homogeneous": row["homogeneous_classification"],
            "homogeneous_product_trapezoidal": row[
                "product_trapezoidal_homogeneous_classification"
            ],
        }
        classifications = {label: [] for label in sweep_labels}
        for cutoff in sweep_cutoffs:
            config = replace(MORPHOLOGY, min_peak_height_rel=float(cutoff))
            for label in sweep_labels:
                morphology = _morphology(
                    sweep_inputs[(nx, ny, label)],
                    config=config,
                )
                classifications[label].append(morphology.classification)
        all_expected = all(
            all(value == expected[label] for value in classifications[label])
            for label in sweep_labels
        )
        if not all_expected:
            mismatches = {
                label: sorted(set(classifications[label]) - {expected[label]})
                for label in sweep_labels
                if any(
                    value != expected[label]
                    for value in classifications[label]
                )
            }
            raise RuntimeError(
                f"grid {(nx, ny)} changed classification on the recorded "
                f"{CUTOFF_SWEEP_SAMPLES}-cutoff sweep: {mismatches}"
            )
        row["strict_secondary_ratio_interval_lower"] = threshold_lower
        row["strict_secondary_ratio_interval_upper"] = threshold_upper
        row["strict_secondary_ratio_interval_margin"] = sweep_margin
        row["classifier_cutoff_sweep"] = {
            "scope": (
                "finite recorded cutoff sample; no unsampled continuous-interval "
                "classifier-stability claim"
            ),
            "sample_count": int(sweep_cutoffs.size),
            "cutoffs": sweep_cutoffs.tolist(),
            "expected_classification": expected,
            "classifications": classifications,
            "all_sampled_cutoffs_match_expected": all_expected,
        }

    metrics_json = DATA / "finite_radius_2d_matched_control.json"
    metrics_csv = DATA / "finite_radius_2d_matched_control.csv"
    series_npz = DATA / "finite_radius_2d_matched_control_series.npz"
    _write_json(metrics_json, rows)
    _write_csv(metrics_csv, rows)
    series_tmp = series_npz.with_name(f".{series_npz.stem}.tmp.npz")
    np.savez_compressed(series_tmp, **archive)
    series_tmp.replace(series_npz)

    figure_pdf = FIGURES / "finite_radius_2d_matched_homogeneous.pdf"
    figure_png = FIGURES / "finite_radius_2d_matched_homogeneous.png"
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.8))

    ax = axes[0, 0]
    ax.set_aspect("equal")
    for patch, color in zip(
        PATTERNED_PATCHES,
        ("#d95f02", "#7570b3"),
        strict=True,
    ):
        ax.add_patch(plt.Circle(patch.centre, patch.radius, color=color, alpha=0.22))
        ax.scatter(*patch.centre, marker="*", s=90, color=color, label=patch.label)
    ax.scatter(*START_ONE, color="#1b9e77", s=55, label="start 1")
    ax.scatter(*START_TWO, color="#66a61e", s=55, label="start 2")
    ax.annotate(
        "both patches interior",
        xy=(0.92, 0.50),
        xytext=(0.45, 0.79),
        arrowprops={"arrowstyle": "->", "lw": 0.8},
        fontsize=8,
    )
    ax.set(
        xlim=(0.0, 1.0),
        ylim=(0.0, 1.0),
        xlabel="x",
        ylabel="y",
        title="(a) patterned patches",
    )
    ax.legend(frameon=False, fontsize=7, loc="lower right")

    representative = (15, 11)
    ax = axes[0, 1]
    for label, color, title in (
        ("patterned", "black", "patterned"),
        ("homogeneous", "#1b9e77", "homogeneous"),
    ):
        key = f"g{representative[0]}x{representative[1]}_{label}"
        times = archive[f"{key}_times"]
        density = archive[f"{key}_density"]
        visible = times <= 45.0
        ax.plot(times[visible], density[visible], color=color, lw=1.7, label=title)
    ax.set(
        xlabel="time",
        ylabel="reaction-time density",
        title="(b) matched transport and killing budget",
    )
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    for nx, ny in GRIDS:
        key = f"g{nx}x{ny}_patterned"
        times = archive[f"{key}_times"]
        density = archive[f"{key}_density"]
        visible = times <= 45.0
        ax.plot(times[visible], density[visible], lw=1.25, label=f"{nx}x{ny}")
    ax.set(
        xlabel="time",
        ylabel="patterned density",
        title="(c) patterned curves by grid",
    )
    ax.legend(frameon=False, fontsize=7)

    ax = axes[1, 1]
    spacings = np.asarray([row["spacing_x"] for row in rows])
    matched_rates = np.asarray([row["matched_homogeneous_rate"] for row in rows])
    ax.plot(spacings, matched_rates, "o-", color="#7570b3", label="grid match")
    weighted_matched_rates = np.asarray(
        [row["product_trapezoidal_matched_homogeneous_rate"] for row in rows]
    )
    ax.plot(
        spacings,
        weighted_matched_rates,
        "s-",
        color="#1b9e77",
        label="control-volume match",
    )
    ax.axhline(
        CONTINUUM_FINITE_A_MATCHED_RATE,
        color="black",
        ls="--",
        label="continuum tube",
    )
    ax.invert_xaxis()
    ax.set(
        xlabel=r"grid spacing $h_x$ (finer right)",
        ylabel="matched uniform reaction rate",
        title="(d) matched homogeneous rate",
    )
    ax.legend(frameon=False, fontsize=8)

    for ax in axes.reshape(-1):
        ax.grid(alpha=0.18)
    enforce_publication_graphics(fig)
    fig.tight_layout()
    temporary_pdf = figure_pdf.with_name(
        f".{figure_pdf.stem}.tmp{figure_pdf.suffix}"
    )
    temporary_png = figure_png.with_name(
        f".{figure_png.stem}.tmp{figure_png.suffix}"
    )
    fig.savefig(temporary_pdf)
    fig.savefig(temporary_png, dpi=300)
    temporary_pdf.replace(figure_pdf)
    temporary_png.replace(figure_png)
    plt.close(fig)

    outputs = [metrics_json, metrics_csv, series_npz, figure_pdf, figure_png]
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=["python", str(HERE.relative_to(REPO))],
        model_spec={
            "family_id": "M2D-E",
            "grids": [list(value) for value in GRIDS],
            "domain": [1.0, 1.0],
            "boundary": "reflecting",
            "discretization": "boundary-node nearest-neighbour lattice CTMC with binary masks",
            "reaction_model": "finite-radius Doi volume sink",
            "catalytic_coordinate": "arithmetic midpoint C_eta with eta=0.5",
            "reaction_radius": REACTION_RADIUS,
            "initial_distribution": (
                "hierarchical contact-safe selector: minimum physical Euclidean "
                "spread on the smallest feasible local stencil, followed by a "
                "strictly convex closest-to-product QP on the optimal LP face; "
                "exact product-bilinear return when already contact-safe"
            ),
            "patterned_patches": [asdict(patch) for patch in PATTERNED_PATCHES],
            "matching_rule": {
                "principal": (
                    "equal sum of statewise killing rates on the same discrete "
                    "encounter tube"
                ),
                "sensitivity": (
                    "exact matching under tensor-product boundary-node "
                    "trapezoidal/control-volume quadrature"
                ),
            },
            "continuum_patterned_area_weight": CONTINUUM_PATTERNED_AREA_WEIGHT,
            "continuum_relative_disk_area": CONTINUUM_RELATIVE_DISK_AREA,
            "continuum_encounter_tube_volume": CONTINUUM_ENCOUNTER_TUBE_VOLUME,
            "continuum_finite_a_matched_rate": CONTINUUM_FINITE_A_MATCHED_RATE,
            "walker_one": WALKER_ONE,
            "walker_two": WALKER_TWO,
            "start_one": START_ONE,
            "start_two": START_TWO,
        },
        classifier_spec={
            **asdict(MORPHOLOGY),
            "classification_semantics": "resolved morphology threshold, not strict root count",
            "strict_root_audit": (
                "finite sign-change scan with Brent refinement using finite-matrix "
                "semigroup derivative evaluations on the declared shape window"
            ),
            "strict_secondary_maxima_retained": True,
            "strict_peak_ratio_separation": {
                "lower": threshold_lower,
                "upper": threshold_upper,
                "margin": threshold_upper - threshold_lower,
            },
            "classifier_cutoff_sweep": {
                "sample_count": CUTOFF_SWEEP_SAMPLES,
                "all_grid_endpoint_samples_match_expected": all(
                    row["classifier_cutoff_sweep"][
                        "all_sampled_cutoffs_match_expected"
                    ]
                    for row in rows
                ),
                "scope": (
                    "recorded finite interior sample only; no continuous-interval claim"
                ),
            },
        },
        dependencies=[
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "encounter2d.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "morphology.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "plotting.py",
            REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py",
        ],
        outputs=outputs,
        horizon={
            "shape_tmax": float(SHAPE_TIMES[-1]),
            "shape_dt": float(SHAPE_TIMES[1] - SHAPE_TIMES[0]),
            "tail_check_time": TAIL_TIME,
            "late_derivative_mesh_samples": LATE_AUDIT_SAMPLES,
            "late_derivative_mesh_step": (
                TAIL_TIME - float(SHAPE_TIMES[-1])
            )
            / (LATE_AUDIT_SAMPLES - 1),
        },
    )
    manifest_path = DATA / "finite_radius_2d_matched_control.manifest.json"
    manifest_tmp = DATA / ".finite_radius_2d_matched_control.manifest.tmp.json"
    write_manifest(manifest_tmp, manifest)
    manifest_tmp.replace(manifest_path)


if __name__ == "__main__":
    main()
