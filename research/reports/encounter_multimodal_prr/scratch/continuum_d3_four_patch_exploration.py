#!/usr/bin/env python3
"""Result-informed physical-d=3 exact-kernel four-slab exploration.

This scratch calculation is not a frozen result and must not be cited as a
project gate.  It tests whether the audited d=2 four-slab design survives when
the disk contact factor is replaced by the exact sphere factor on
R x T_W^2.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import j1

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
CODE = REPORT / "code"
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import continuum_observable_four_patch as base  # noqa: E402

OUTPUT = HERE.with_name("continuum_d3_four_patch_exploration_result.json")


class FourPatchContinuumD3(base.FourPatchContinuum):
    """Exact free-exposure clocks on R x T_W^2 for physical d=3."""

    def __init__(
        self,
        configuration: base.NumericalConfiguration,
        parameters: base.PhysicalParameters | None = None,
    ) -> None:
        super().__init__(configuration, parameters)
        pars = self.parameters
        nodes, weights = leggauss(configuration.contact_angle_order)
        self.sphere_parallel_targets = pars.contact_radius * nodes
        self.sphere_parallel_weights = pars.contact_radius * weights
        half_chords = pars.contact_radius * np.sqrt(np.maximum(0.0, 1.0 - nodes**2))

        indices = np.arange(configuration.transverse_fourier_modes + 1, dtype=float)
        wave_numbers = self.omega * indices
        radial_wave_number = np.sqrt(wave_numbers[:, None] ** 2 + wave_numbers[None, :] ** 2)
        disk_integrals = np.empty(
            (
                configuration.contact_angle_order,
                configuration.transverse_fourier_modes + 1,
                configuration.transverse_fourier_modes + 1,
            ),
            dtype=float,
        )
        for index, radius in enumerate(half_chords):
            argument = radial_wave_number * radius
            values = np.empty_like(radial_wave_number)
            zero = radial_wave_number == 0.0
            values[zero] = np.pi * radius**2
            values[~zero] = 2.0 * np.pi * radius * j1(argument[~zero]) / radial_wave_number[~zero]
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
        kernel = kernel.reshape(shape)
        midpoint = (
            np.einsum(
                "tcvu,u,v->tc",
                kernel,
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
        pars = self.parameters
        values = np.atleast_1d(np.asarray(times))
        modes = self.configuration.transverse_fourier_modes
        dtype = complex if np.iscomplexobj(values) else float
        output = np.empty((len(values), modes + 1), dtype=dtype)
        derivative = np.empty_like(output)
        output[:, 0] = 1.0 / pars.transverse_width
        derivative[:, 0] = 0.0
        decay = np.exp(-values[:, None] * self.transverse_eigenvalues[None, :])
        output[:, 1:] = (
            2.0
            / pars.transverse_width
            * decay
            * self.transverse_initial_cosine_coefficients[None, :]
        )
        derivative[:, 1:] = -self.transverse_eigenvalues[None, :] * output[:, 1:]
        return output, derivative

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
        parallel_d1 = np.einsum(
            "txu,u->tx",
            parallel_d1,
            self.bump_weights,
            optimize=True,
        )
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


def main() -> None:
    configuration = base.NumericalConfiguration(72, 72, 64, 16, 64, 0.4)
    model = FourPatchContinuumD3(configuration)
    cusp, diagnostics = base.locate_cusp(model, (10.0, 18.0))
    times = np.arange(0.1, 100.0 + 0.0025, 0.005)
    channels, derivatives = model.real_channels_and_first_derivatives(times)
    base_weights = np.asarray(cusp["weights"], dtype=float)
    direction = np.asarray(cusp["strict_inward_normal"]["direction_4d"], dtype=float)
    candidates: list[dict[str, object]] = []
    for step in base.candidate_steps(0.02, 0.20, 0.01):
        weights = base_weights + step * direction
        structure = base.stationary_structure(
            model,
            weights,
            times,
            channels,
            derivatives,
            relative_density_floor=1.0e-12,
            derivative_zero_relative_tolerance=5.0e-12,
        )
        row: dict[str, object] = {
            "step": step,
            "weights": weights.tolist(),
            "stationary_structure": structure,
        }
        eligible, gates = base.candidate_is_eligible(
            row,
            minimum_peak_ratio=0.1,
            maximum_valley_ratio=0.85,
            minimum_abs_scaled_curvature=1.0e-4,
            maximum_scaled_root_residual=1.0e-9,
        )
        row["eligible"] = eligible
        row["gates"] = gates
        candidates.append(row)
    selected = base.select_candidate(candidates)
    scan = {
        "candidates": candidates,
        "selected": selected,
    }
    payload = {
        "status": "SCRATCH_RESULT_INFORMED_D3_EXPLORATION",
        "claim_flags": {
            "formal_confirmation": False,
            "finite_B_Doi_verified": False,
            "project_gate_passed": False,
        },
        "configuration": asdict(configuration),
        "cusp": cusp,
        "cusp_diagnostics": diagnostics,
        "scan": scan,
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "cusp_time": cusp["time"],
                "cusp_weights": cusp["weights"],
                "scaled_fourth": cusp["scaled_fourth_derivative"],
                "svd_ratio": cusp["unfolding"]["dimensionless_svd_ratio"],
                "eligible_count": sum(row["eligible"] for row in scan["candidates"]),
                "selected": selected,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
