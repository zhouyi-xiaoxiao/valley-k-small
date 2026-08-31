#!/usr/bin/env python3
"""Frozen result-informed physical-d=3 four-slab exact-kernel confirmation.

The production representation integrates the two-dimensional periodic heat
kernel over transverse disks with the Fourier--Bessel disk formula.  A frozen
independent reference instead integrates the pointwise product of the two
periodic heat kernels directly in spherical coordinates.

The geometry and approximate answer were known before this chain was frozen.
Consequently this is neither preregistered discovery nor interval, finite-B,
independent-PDE, project, or publication certification.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import scipy
from numpy.polynomial.legendre import leggauss
from scipy.special import j1

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "continuum_observable_four_patch_d3_manifest.json"
OUTPUT = DATA / "continuum_observable_four_patch_d3_result.json"
TEST_FILE = HERE.with_name("test_continuum_observable_four_patch_d3.py")
PROTOCOL = REPORT / "notes" / "observable_four_patch_d3_protocol.md"
BASE_FILE = HERE.with_name("continuum_observable_four_patch.py")

if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))

import continuum_observable_four_patch as base  # noqa: E402

EVIDENCE_TIMING = "RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY"
RESULT_STATUS = "PASS_RESULT_INFORMED_PHYSICAL_D3_OBSERVABLE_FREE_EXPOSURE_CONFIRMATION"

COARSE = base.NumericalConfiguration(56, 56, 56, 12, 48, 0.50)
PRIMARY = base.NumericalConfiguration(72, 72, 72, 16, 64, 0.40)
FINE = base.NumericalConfiguration(96, 96, 96, 24, 80, 0.30)


class FourPatchContinuumD3(base.FourPatchContinuum):
    """Exact free-exposure clocks on R x T_W^2 for physical d=3."""

    def __init__(
        self,
        configuration: base.NumericalConfiguration,
        parameters: base.PhysicalParameters | None = None,
    ) -> None:
        super().__init__(configuration, parameters)
        pars = self.parameters
        # The frozen initial law uses an independent compact bump in each of
        # the two transverse relative coordinates, exactly as in the d=2
        # baseline. Spell this out so the d=3 model contract does not depend
        # on an implicit interpretation of the inherited field.
        transverse_starts = pars.relative_perp_start + pars.initial_half_width * self.bump_nodes
        self.transverse_initial_cosine_coefficients = np.asarray(
            [
                np.dot(
                    self.bump_weights,
                    np.cos(mode * self.omega * transverse_starts),
                )
                for mode in self.mode_numbers
            ],
            dtype=float,
        )
        nodes, weights = leggauss(configuration.contact_angle_order)
        self.sphere_parallel_targets = pars.contact_radius * nodes
        self.sphere_parallel_weights = pars.contact_radius * weights
        half_chords = pars.contact_radius * np.sqrt(np.maximum(0.0, 1.0 - nodes**2))

        indices = np.arange(configuration.transverse_fourier_modes + 1, dtype=float)
        wave_numbers = self.omega * indices
        radial_wave_numbers = np.sqrt(wave_numbers[:, None] ** 2 + wave_numbers[None, :] ** 2)
        disk_integrals = np.empty(
            (
                configuration.contact_angle_order,
                configuration.transverse_fourier_modes + 1,
                configuration.transverse_fourier_modes + 1,
            ),
            dtype=float,
        )
        zero_mode = radial_wave_numbers == 0.0
        for index, radius in enumerate(half_chords):
            arguments = radial_wave_numbers * radius
            values = np.empty_like(radial_wave_numbers)
            values[zero_mode] = np.pi * radius**2
            values[~zero_mode] = (
                2.0 * np.pi * radius * j1(arguments[~zero_mode]) / radial_wave_numbers[~zero_mode]
            )
            disk_integrals[index] = values
        self.transverse_disk_integrals = disk_integrals

    def _midpoint_factors(
        self,
        times: np.ndarray,
        *,
        first_derivative: bool,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        pars = self.parameters
        flat_targets = self.patch_targets.reshape(-1)
        if first_derivative:
            kernel, kernel_d1 = base.ou_density_and_first_derivative(
                np.asarray(times, dtype=float),
                flat_targets,
                self.midpoint_starts,
                diffusion_coefficient=pars.particle_diffusion / 2.0,
                stiffness=pars.ou_stiffness,
                mean=pars.ou_mean,
            )
        else:
            kernel = base.ou_transition_density(
                np.asarray(times, dtype=complex),
                flat_targets,
                self.midpoint_starts,
                diffusion_coefficient=pars.particle_diffusion / 2.0,
                stiffness=pars.ou_stiffness,
                mean=pars.ou_mean,
            )
            kernel_d1 = None
        shape = (
            len(times),
            4,
            self.configuration.patch_order,
            self.configuration.bump_order,
        )
        midpoint = (
            np.einsum(
                "tcvu,u,v->tc",
                kernel.reshape(shape),
                self.bump_weights,
                self.patch_weights,
                optimize=True,
            )
            / pars.transverse_width**2
        )
        if kernel_d1 is None:
            return midpoint, None
        midpoint_d1 = (
            np.einsum(
                "tcvu,u,v->tc",
                kernel_d1.reshape(shape),
                self.bump_weights,
                self.patch_weights,
                optimize=True,
            )
            / pars.transverse_width**2
        )
        return midpoint, midpoint_d1

    def _transverse_coefficients(
        self,
        times: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Cosine-series coefficients and exact first time derivatives."""

        pars = self.parameters
        values = np.atleast_1d(np.asarray(times))
        modes = self.configuration.transverse_fourier_modes
        dtype = complex if np.iscomplexobj(values) else float
        coefficients = np.empty((len(values), modes + 1), dtype=dtype)
        derivatives = np.empty_like(coefficients)
        coefficients[:, 0] = 1.0 / pars.transverse_width
        derivatives[:, 0] = 0.0
        decay = np.exp(-values[:, None] * self.transverse_eigenvalues[None, :])
        coefficients[:, 1:] = (
            2.0
            / pars.transverse_width
            * decay
            * self.transverse_initial_cosine_coefficients[None, :]
        )
        derivatives[:, 1:] = -self.transverse_eigenvalues[None, :] * coefficients[:, 1:]
        return coefficients, derivatives

    def _sphere_contact(
        self,
        times: np.ndarray,
        *,
        first_derivative: bool,
    ) -> tuple[np.ndarray, np.ndarray | None]:
        pars = self.parameters
        if first_derivative:
            parallel, parallel_d1 = base.ou_density_and_first_derivative(
                np.asarray(times, dtype=float),
                self.sphere_parallel_targets,
                self.relative_parallel_starts,
                diffusion_coefficient=2.0 * pars.particle_diffusion,
                stiffness=pars.ou_stiffness,
                mean=0.0,
            )
        else:
            parallel = base.ou_transition_density(
                np.asarray(times, dtype=complex),
                self.sphere_parallel_targets,
                self.relative_parallel_starts,
                diffusion_coefficient=2.0 * pars.particle_diffusion,
                stiffness=pars.ou_stiffness,
                mean=0.0,
            )
            parallel_d1 = None
        parallel = np.einsum("txu,u->tx", parallel, self.bump_weights, optimize=True)
        coefficients, coefficient_d1 = self._transverse_coefficients(times)
        disk = np.einsum(
            "ti,xij,tj->tx",
            coefficients,
            self.transverse_disk_integrals,
            coefficients,
            optimize=True,
        )
        contact = np.einsum(
            "tx,tx,x->t",
            parallel,
            disk,
            self.sphere_parallel_weights,
            optimize=True,
        )
        if parallel_d1 is None:
            return contact, None
        parallel_d1 = np.einsum("txu,u->tx", parallel_d1, self.bump_weights, optimize=True)
        disk_d1 = 2.0 * np.einsum(
            "ti,xij,tj->tx",
            coefficient_d1,
            self.transverse_disk_integrals,
            coefficients,
            optimize=True,
        )
        contact_d1 = np.einsum(
            "tx,tx,x->t",
            parallel_d1,
            disk,
            self.sphere_parallel_weights,
            optimize=True,
        ) + np.einsum(
            "tx,tx,x->t",
            parallel,
            disk_d1,
            self.sphere_parallel_weights,
            optimize=True,
        )
        return contact, contact_d1

    def factors(self, times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        values = np.atleast_1d(np.asarray(times, dtype=complex))
        midpoint, _ = self._midpoint_factors(values, first_derivative=False)
        contact, _ = self._sphere_contact(values, first_derivative=False)
        return midpoint, contact

    def real_channels_and_first_derivatives(
        self,
        times: np.ndarray,
        *,
        chunk_size: int = 96,
    ) -> tuple[np.ndarray, np.ndarray]:
        values = np.atleast_1d(np.asarray(times, dtype=float))
        if np.any(values <= 0.0):
            raise ValueError("time grid must be strictly positive")
        channels = np.empty((len(values), 4), dtype=float)
        derivatives = np.empty_like(channels)
        for start in range(0, len(values), chunk_size):
            stop = min(start + chunk_size, len(values))
            local = values[start:stop]
            midpoint, midpoint_d1 = self._midpoint_factors(local, first_derivative=True)
            contact, contact_d1 = self._sphere_contact(local, first_derivative=True)
            assert midpoint_d1 is not None and contact_d1 is not None
            channels[start:stop] = midpoint * contact[:, None]
            derivatives[start:stop] = (
                midpoint_d1 * contact[:, None] + midpoint * contact_d1[:, None]
            )
        return channels, derivatives


def direct_spherical_contact_values(
    model: FourPatchContinuumD3,
    times: Sequence[float],
    *,
    radial_order: int,
    polar_order: int,
    azimuthal_points: int,
) -> np.ndarray:
    """Directly integrate p_parallel*p_perp1*p_perp2 over the contact sphere.

    This calculation deliberately does not call the Bessel disk formula or use
    ``transverse_disk_integrals``.  Gauss--Legendre rules integrate radius and
    mu=cos(theta); an equispaced trapezoidal rule integrates azimuth.
    """

    if radial_order < 12 or polar_order < 12 or azimuthal_points < 32:
        raise ValueError("direct spherical reference orders are too small")
    pars = model.parameters
    radial_nodes, radial_weights = leggauss(radial_order)
    radii = 0.5 * pars.contact_radius * (radial_nodes + 1.0)
    radial_weights = 0.5 * pars.contact_radius * radial_weights
    polar_nodes, polar_weights = leggauss(polar_order)
    azimuths = 2.0 * np.pi * np.arange(azimuthal_points) / azimuthal_points

    parallel_targets = radii[:, None] * polar_nodes[None, :]
    transverse_radius = radii[:, None] * np.sqrt(np.maximum(0.0, 1.0 - polar_nodes[None, :] ** 2))
    transverse_one = transverse_radius[:, :, None] * np.cos(azimuths)[None, None, :]
    transverse_two = transverse_radius[:, :, None] * np.sin(azimuths)[None, None, :]
    volume_weights = radial_weights[:, None] * radii[:, None] ** 2 * polar_weights[None, :]
    azimuthal_weight = 2.0 * np.pi / azimuthal_points

    outputs = []
    wave_numbers = model.omega * model.mode_numbers
    for time in times:
        value = float(time)
        if value <= 0.0:
            raise ValueError("reference times must be positive")
        parallel_kernel = base.ou_transition_density(
            np.asarray((value,)),
            parallel_targets.reshape(-1),
            model.relative_parallel_starts,
            diffusion_coefficient=2.0 * pars.particle_diffusion,
            stiffness=pars.ou_stiffness,
            mean=0.0,
        )[0]
        parallel_density = np.real(parallel_kernel @ model.bump_weights).reshape(
            radial_order, polar_order
        )
        coefficient, _ = model._transverse_coefficients(np.asarray((value,)))
        transverse_density_one = np.full_like(
            transverse_one,
            float(coefficient[0, 0]),
            dtype=float,
        )
        transverse_density_two = np.full_like(
            transverse_two,
            float(coefficient[0, 0]),
            dtype=float,
        )
        for mode_index, wave_number in enumerate(wave_numbers, start=1):
            amplitude = float(coefficient[0, mode_index])
            transverse_density_one += amplitude * np.cos(wave_number * transverse_one)
            transverse_density_two += amplitude * np.cos(wave_number * transverse_two)
        integrand = parallel_density[:, :, None] * transverse_density_one * transverse_density_two
        outputs.append(
            float(
                np.einsum(
                    "rp,rpa->",
                    volume_weights,
                    integrand,
                    optimize=True,
                )
                * azimuthal_weight
            )
        )
    return np.asarray(outputs, dtype=float)


def spherical_contact_reference(
    model: FourPatchContinuumD3,
    times: Sequence[float],
    *,
    radial_order: int,
    polar_order: int,
    azimuthal_points: int,
) -> dict[str, Any]:
    direct = direct_spherical_contact_values(
        model,
        times,
        radial_order=radial_order,
        polar_order=polar_order,
        azimuthal_points=azimuthal_points,
    )
    production, _ = model._sphere_contact(
        np.asarray(tuple(times), dtype=complex),
        first_derivative=False,
    )
    production_real = np.real(production)
    differences = np.abs(direct - production_real)
    relative = differences / np.maximum(np.abs(production_real), np.finfo(float).tiny)
    return {
        "representation": (
            "direct spherical coordinates of the pointwise product of one OU "
            "and two periodic heat kernels; no Bessel disk formula"
        ),
        "radial_order": radial_order,
        "polar_order": polar_order,
        "azimuthal_points": azimuthal_points,
        "rows": [
            {
                "time": float(time),
                "fourier_bessel": float(fourier_bessel),
                "direct_spherical": float(spherical),
                "absolute_difference": float(difference),
                "relative_difference": float(rel),
            }
            for time, fourier_bessel, spherical, difference, rel in zip(
                times,
                production_real,
                direct,
                differences,
                relative,
                strict=True,
            )
        ],
        "maximum_relative_difference": float(np.max(relative)),
    }


def require_repository_venv() -> None:
    expected = (REPOSITORY / ".venv").resolve()
    if Path(sys.prefix).resolve() != expected:
        raise RuntimeError("physical-d=3 confirmation must run inside repository .venv")


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("evidence_timing") != EVIDENCE_TIMING:
        raise RuntimeError("manifest evidence timing is not fail-closed")
    required_flags = {
        "preregistered_discovery": False,
        "continuum_verified": False,
        "finite_B_Doi_verified": False,
        "independent_PDE_solver_verified": False,
        "project_gate_passed": False,
    }
    if manifest.get("required_claim_flags") != required_flags:
        raise RuntimeError("manifest negative claim flags were altered")
    expected_hashes = {
        "producer": (HERE, manifest["frozen_files"]["producer_sha256"]),
        "test": (TEST_FILE, manifest["frozen_files"]["test_sha256"]),
        "protocol": (PROTOCOL, manifest["frozen_files"]["protocol_sha256"]),
        "base_dependency": (
            BASE_FILE,
            manifest["frozen_files"]["base_dependency_sha256"],
        ),
    }
    for label, (path, expected) in expected_hashes.items():
        observed = base.sha256(path)
        if observed != expected:
            raise RuntimeError(
                f"frozen {label} hash mismatch: expected {expected}, observed {observed}"
            )
    expected_parameters = json.loads(json.dumps(asdict(base.PhysicalParameters()), allow_nan=False))
    if manifest["physical_model"]["parameters"] != expected_parameters:
        raise RuntimeError("manifest physical parameters do not match the producer")
    expected_configurations = {
        "coarse": asdict(COARSE),
        "primary": asdict(PRIMARY),
        "fine": asdict(FINE),
    }
    if manifest["numerical_configurations"] != expected_configurations:
        raise RuntimeError("manifest numerical configurations do not match the producer")
    scan = manifest["inward_step_scan"]
    expected_steps = base.candidate_steps(
        scan["step_start"], scan["step_stop"], scan["step_spacing"]
    )
    if scan["candidate_steps"] != expected_steps:
        raise RuntimeError("manifest candidate step grid is inconsistent")
    if scan["selection_priority"] != [
        "maximum minimum catalyst weight",
        "maximum worst-valley margin to the 0.85 ceiling",
        "maximum minimum-to-maximum peak ratio",
        "smallest step as deterministic final tie-break",
    ]:
        raise RuntimeError("manifest candidate selection priority was altered")


def _candidate_scan(
    model: FourPatchContinuumD3,
    cusp: dict[str, Any],
    scan: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], np.ndarray]:
    times = np.arange(
        scan["time_start"],
        scan["time_stop"] + 0.5 * scan["time_spacing"],
        scan["time_spacing"],
    )
    channels, derivatives = model.real_channels_and_first_derivatives(times)
    base_weights = np.asarray(cusp["weights"], dtype=float)
    direction = np.asarray(cusp["strict_inward_normal"]["direction_4d"], dtype=float)
    candidates: list[dict[str, Any]] = []
    for step in scan["candidate_steps"]:
        weights = base_weights + step * direction
        structure = base.stationary_structure(
            model,
            weights,
            times,
            channels,
            derivatives,
            relative_density_floor=scan["relative_density_floor"],
            derivative_zero_relative_tolerance=scan["derivative_zero_relative_tolerance"],
        )
        row: dict[str, Any] = {
            "step": step,
            "weights": weights.tolist(),
            "stationary_structure": structure,
        }
        eligible, gates = base.candidate_is_eligible(
            row,
            minimum_peak_ratio=scan["minimum_peak_ratio"],
            maximum_valley_ratio=scan["maximum_valley_ratio"],
            minimum_abs_scaled_curvature=scan["minimum_abs_scaled_curvature"],
            maximum_scaled_root_residual=scan["maximum_scaled_root_residual"],
        )
        row["eligible"] = eligible
        row["gates"] = gates
        candidates.append(row)
    return candidates, base.select_candidate(candidates), times


def run_formal(manifest: dict[str, Any]) -> dict[str, Any]:
    validate_manifest(manifest)
    bracket = tuple(manifest["cusp_confirmation"]["determinant_bracket"])
    scan = manifest["inward_step_scan"]
    primary_model = FourPatchContinuumD3(PRIMARY)
    cusp, cusp_diagnostics = base.locate_cusp(primary_model, bracket)
    candidates, selected, times = _candidate_scan(primary_model, cusp, scan)

    convergence_rows = []
    configuration_map = {"coarse": COARSE, "primary": PRIMARY, "fine": FINE}
    for label, configuration in configuration_map.items():
        if label == "primary":
            metrics = cusp
            diagnostics = cusp_diagnostics
        else:
            metrics, diagnostics = base.locate_cusp(FourPatchContinuumD3(configuration), bracket)
        convergence_rows.append(
            {
                "label": label,
                "configuration": asdict(configuration),
                "cusp_time": metrics["time"],
                "weights": metrics["weights"],
                "scaled_fourth_derivative": metrics["scaled_fourth_derivative"],
                "unfolding_svd_ratio": metrics["unfolding"]["dimensionless_svd_ratio"],
                "maximum_scaled_cusp_residual": max(metrics["scaled_residuals_orders_1_to_3"]),
                "maximum_imaginary_cauchy_residual": diagnostics[
                    "maximum_imaginary_cauchy_residual"
                ],
                "maximum_direct_vs_leibniz_difference": diagnostics[
                    "maximum_direct_vs_leibniz_difference"
                ],
            }
        )

    selected_weights = np.asarray(selected["weights"], dtype=float)
    fine_model = FourPatchContinuumD3(FINE)
    fine_channels, fine_derivatives = fine_model.real_channels_and_first_derivatives(times)
    fine_structure = base.stationary_structure(
        fine_model,
        selected_weights,
        times,
        fine_channels,
        fine_derivatives,
        relative_density_floor=scan["relative_density_floor"],
        derivative_zero_relative_tolerance=scan["derivative_zero_relative_tolerance"],
    )
    fine_row: dict[str, Any] = {
        "step": selected["step"],
        "weights": selected["weights"],
        "stationary_structure": fine_structure,
    }
    fine_eligible, fine_gates = base.candidate_is_eligible(
        fine_row,
        minimum_peak_ratio=scan["minimum_peak_ratio"],
        maximum_valley_ratio=scan["maximum_valley_ratio"],
        minimum_abs_scaled_curvature=scan["minimum_abs_scaled_curvature"],
        maximum_scaled_root_residual=scan["maximum_scaled_root_residual"],
    )
    fine_row["eligible"] = fine_eligible
    fine_row["gates"] = fine_gates

    reference_config = manifest["spherical_coordinate_check"]
    spherical_reference = spherical_contact_reference(
        primary_model,
        reference_config["times"],
        radial_order=reference_config["radial_order"],
        polar_order=reference_config["polar_order"],
        azimuthal_points=reference_config["azimuthal_points"],
    )
    convergence = {row["label"]: row for row in convergence_rows}
    primary_weights = np.asarray(convergence["primary"]["weights"])
    fine_weights = np.asarray(convergence["fine"]["weights"])
    primary_roots = selected["stationary_structure"]["roots"]
    fine_roots = fine_structure["roots"]
    root_differences = (
        [
            abs(left["time"] - right["time"])
            for left, right in zip(primary_roots, fine_roots, strict=True)
        ]
        if len(primary_roots) == len(fine_roots)
        else []
    )
    gates = {
        "cusp_weights_strictly_positive": cusp["minimum_weight"] > 0.0,
        "fixed_first_weight_preserved": abs(
            cusp["weights"][0] - base.PhysicalParameters().fixed_first_weight
        )
        < 1.0e-13,
        "cusp_residual": max(cusp["scaled_residuals_orders_1_to_3"])
        <= manifest["cusp_confirmation"]["maximum_scaled_cusp_residual"],
        "fourth_derivative_nonzero": abs(cusp["scaled_fourth_derivative"])
        >= manifest["cusp_confirmation"]["minimum_absolute_scaled_fourth_derivative"],
        "unfolding_rank_two": cusp["unfolding"]["rank"] == 2,
        "unfolding_ratio": cusp["unfolding"]["dimensionless_svd_ratio"]
        >= manifest["cusp_confirmation"]["minimum_unfolding_svd_ratio"],
        "strict_normal_first_projection": abs(
            cusp["strict_inward_normal"]["first_unfolding_projection"]
        )
        <= 1.0e-12,
        "strict_normal_signed_inward": (
            cusp["strict_inward_normal"]["second_unfolding_projection"]
            * cusp["strict_inward_normal"]["normal_form_cubic_coefficient"]
            < 0.0
        ),
        "eligible_candidate_exists": any(row["eligible"] for row in candidates),
        "selected_candidate_observable": selected["eligible"],
        "selected_step_follows_frozen_priority": selected == base.select_candidate(candidates),
        "fine_fixed_weight_observable": fine_eligible,
        "fine_primary_cusp_time_agreement": abs(
            convergence["fine"]["cusp_time"] - convergence["primary"]["cusp_time"]
        )
        <= manifest["convergence_gates"]["maximum_cusp_time_difference"],
        "fine_primary_weight_agreement": float(np.max(np.abs(fine_weights - primary_weights)))
        <= manifest["convergence_gates"]["maximum_weight_linf_difference"],
        "fine_primary_scaled_f4_agreement": abs(
            convergence["fine"]["scaled_fourth_derivative"]
            - convergence["primary"]["scaled_fourth_derivative"]
        )
        <= manifest["convergence_gates"]["maximum_scaled_f4_difference"],
        "fine_fixed_weight_root_count": len(primary_roots) == len(fine_roots) == 5,
        "fine_fixed_weight_root_times": bool(root_differences)
        and max(root_differences) <= manifest["convergence_gates"]["maximum_root_time_difference"],
        "direct_spherical_coordinate_check": spherical_reference["maximum_relative_difference"]
        <= reference_config["maximum_relative_difference"],
    }
    if not all(gates.values()):
        failed = [name for name, passed in gates.items() if not passed]
        raise RuntimeError(f"formal physical-d=3 confirmation failed gates: {failed}")

    return {
        "schema_version": 1,
        "stage": manifest["stage"],
        "status": RESULT_STATUS,
        "evidence_timing": EVIDENCE_TIMING,
        "claim_flags": {
            "preregistered_discovery": False,
            "continuum_verified": False,
            "finite_B_Doi_verified": False,
            "independent_PDE_solver_verified": False,
            "project_gate_passed": False,
            "observable_d3_free_exposure_confirmation_passed": True,
        },
        "model": {
            "physical_dimension": 3,
            "domain": "R longitudinal x T_W^2 transverse; unbounded OU/periodic kernels",
            "parameters": asdict(base.PhysicalParameters()),
            "contact_set": "true three-dimensional sphere",
            "full_budget_factor": "1 / transverse_width^2",
            "factorization": "g_j(t)=a_j(t)c_3(t)",
            "affine_control_slice": ("w0 fixed at 0.28; w1,w2 free; w3=1-w0-w1-w2"),
        },
        "cusp": cusp,
        "cusp_diagnostics": cusp_diagnostics,
        "inward_step_scan": {
            "selection_rule": scan["selection_priority"],
            "candidate_count": len(candidates),
            "eligible_count": sum(row["eligible"] for row in candidates),
            "candidates": candidates,
            "selected": selected,
        },
        "quadrature_and_cauchy_convergence": convergence_rows,
        "selected_absolute_weight_fine_crosscheck": fine_row,
        "selected_root_time_absolute_differences_primary_vs_fine": root_differences,
        "direct_spherical_coordinate_check": spherical_reference,
        "gates": gates,
        "limitations": [
            "geometry, approximate cusp, and a passing inward step were known before freeze",
            "floating-point quadrature convergence is not interval certification",
            "the calculation is the B=0 derivative per unit full installed budget",
            "no explicit positive-B persistence radius or killed-Doi event mass is included",
            "no independent bounded-box PDE solver is included",
            "the result confirms this fixed four-slab geometry, not arbitrary geometries",
        ],
        "provenance": {
            "manifest": str(MANIFEST.relative_to(REPORT)),
            "manifest_sha256": base.sha256(MANIFEST),
            "producer": str(HERE.relative_to(REPORT)),
            "producer_sha256": base.sha256(HERE),
            "test": str(TEST_FILE.relative_to(REPORT)),
            "test_sha256": base.sha256(TEST_FILE),
            "protocol": str(PROTOCOL.relative_to(REPORT)),
            "protocol_sha256": base.sha256(PROTOCOL),
            "base_dependency": str(BASE_FILE.relative_to(REPORT)),
            "base_dependency_sha256": base.sha256(BASE_FILE),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-frozen", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    if not args.execute_frozen:
        parser.error("formal execution requires --execute-frozen")
    require_repository_venv()
    manifest = base.load_json(MANIFEST)
    payload = run_formal(manifest)
    base.write_json(args.output, payload)
    selected = payload["inward_step_scan"]["selected"]
    structure = selected["stationary_structure"]
    print(
        f"cusp_time={payload['cusp']['time']:.12g} "
        f"selected_step={selected['step']:.2f} "
        f"valley_ratios={structure['valley_to_smaller_adjacent_peak_ratios']}"
    )
    print(
        "direct_spherical_max_relative="
        f"{payload['direct_spherical_coordinate_check']['maximum_relative_difference']:.6g}"
    )
    print(f"status={payload['status']}")
    print(f"output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
