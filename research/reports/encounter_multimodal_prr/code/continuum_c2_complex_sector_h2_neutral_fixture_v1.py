#!/usr/bin/env python3
"""Build the Round-11 neutral mixed-NP sector/contour algebra fixture.

This is a finite algebraic diagnostic.  It does not numerically prove a
mixed-boundary PDE graph-domain theorem, an H2 resolvent estimate, a
source-bound reconstruction rate, C2, or any production/science claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import gmpy2

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DEFAULT_OUTPUT = (
    REPORT
    / "artifacts/data/continuum_c2_complex_sector_h2_neutral_fixture_v1.json"
)
SCHEMA = "encounter_continuum_c2_complex_sector_h2_neutral_fixture_v1"
STATUS = "PASS_NEUTRAL_MIXED_NP_SECTOR_CONTOUR_ALGEBRA_ONLY_COMPLETE_C2_HOLD"
PRECISION_BITS = 256

SIGMA = Fraction(1)
THETA_OVER_PI = Fraction(1, 3)
S_THETA = Fraction(1, 2)
BOX = {
    "diffusion_diagonal": ["1/1", "2/1", "1/1"],
    "periodic_width": "1/1",
    "r_interval": ["-1/1", "1/1"],
    "z_interval": ["-1/1", "1/1"],
}
MODE_P = range(3)
MODE_Q = range(3)
MODE_K = range(-2, 3)
RHO_VALUES = (
    Fraction(1, 16),
    Fraction(1, 4),
    Fraction(1),
    Fraction(4),
    Fraction(16),
)
TAU_VALUES = (Fraction(1, 4), Fraction(1), Fraction(3))
R_VALUES = (0, 1, 2)
PHI_OVER_PI_VALUES = (
    Fraction(-2, 3),
    Fraction(-1, 3),
    Fraction(0),
    Fraction(1, 3),
    Fraction(2, 3),
)
A_OVER_RHO_VALUES = (
    Fraction(0),
    Fraction(1, 4),
    Fraction(1),
    Fraction(4),
)
ENERGY_TO_MASS_VALUES = (
    Fraction(0),
    Fraction(1, 3),
    Fraction(3),
)

PHYSICAL_CLAIMS = {
    "bounded_multiplier_domain_theorem_proved_by_fixture": False,
    "box_exhaustion_complete": False,
    "complete_C1": False,
    "complete_C2": False,
    "complete_C3": False,
    "complex_sector_H2_pde_estimate_proved_by_fixture": False,
    "dimension_uniform_H2_to_Linfinity": False,
    "formal_mixed_NP_graph_domain_proved_by_fixture": False,
    "H2_resolvent_decay_as_abs_lambda_inverse": False,
    "positive_budget_science": False,
    "production_acceptance_receipt": False,
    "production_evidence": False,
    "production_member_bound": False,
    "release_submission_ready": False,
    "release_submission_science_execution": False,
    "science_result": False,
    "source_bound_killing_residual": False,
    "source_bound_reconstruction_map": False,
    "source_bound_resolvent_comparison": False,
    "tau_zero_extension": False,
    "unconditional_reconstructed_resolvent_C2_rate": False,
}


def _f(value: Fraction | int) -> str:
    exact = Fraction(value)
    return f"{exact.numerator}/{exact.denominator}"


def _mp(value: Fraction | int) -> gmpy2.mpfr:
    exact = Fraction(value)
    return gmpy2.mpfr(exact.numerator) / gmpy2.mpfr(exact.denominator)


def _hex(value: gmpy2.mpfr | float) -> str:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("nonfinite numeric summary")
    if result == 0.0:
        result = 0.0
    return result.hex()


def _mode_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pi = gmpy2.const_pi()
    for p in MODE_P:
        for q in MODE_Q:
            for k in MODE_K:
                coefficient = (
                    Fraction(p * p, 4)
                    + Fraction(q * q, 2)
                    + Fraction(4 * k * k)
                )
                rows.append(
                    {
                        "conjugate_periodic_partner": [p, q, -k],
                        "eigenvalue_hex": _hex(_mp(coefficient) * pi * pi),
                        "eigenvalue_over_pi_squared": _f(coefficient),
                        "k_periodic": k,
                        "p_neumann_z": p,
                        "q_neumann_r": q,
                        "r_endpoint_normal_derivatives_exact_zero": True,
                        "y_periodic_value_and_derivative_traces_match": True,
                        "z_endpoint_normal_derivatives_exact_zero": True,
                    }
                )
    rows.sort(
        key=lambda row: (
            Fraction(row["eigenvalue_over_pi_squared"]),
            row["p_neumann_z"],
            row["q_neumann_r"],
            row["k_periodic"],
        )
    )
    if len(rows) != 45 or rows[0]["eigenvalue_over_pi_squared"] != "0/1":
        raise AssertionError("mixed-NP mode window sentinel failed")
    return rows


def _weighted_square(values: list[Fraction], masses: list[Fraction]) -> Fraction:
    return sum(
        (mass * value * value for mass, value in zip(masses, values, strict=True)),
        Fraction(0),
    )


def _bounded_multiplier() -> dict[str, Any]:
    weights = [Fraction(1, 10), Fraction(1, 5), Fraction(3, 10), Fraction(2, 5)]
    suprema = [Fraction(1), Fraction(3, 2), Fraction(2), Fraction(5, 2)]
    profiles = [
        [Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)],
        [Fraction(1, 2), Fraction(3, 4), Fraction(1), Fraction(5, 4)],
        suprema,
    ]
    indicators = [0, 1, 1]
    budget = Fraction(3, 2)
    width = Fraction(1)
    v_star = max(suprema) / width
    k_star = budget * v_star
    rows = []
    k_values: list[Fraction] = []
    for index, (indicator, profile) in enumerate(
        zip(indicators, profiles, strict=True)
    ):
        weighted_patch = sum(
            (
                weight * value
                for weight, value in zip(weights, profile, strict=True)
            ),
            Fraction(0),
        )
        v_c = Fraction(indicator) * weighted_patch / width
        k_c = budget * v_c
        if not 0 <= k_c <= k_star:
            raise AssertionError("bounded multiplier sentinel failed")
        k_values.append(k_c)
        rows.append(
            {
                "K_c": _f(k_c),
                "V_c": _f(v_c),
                "patch_profile_values": [_f(value) for value in profile],
                "sample_index": index,
                "sharp_indicator": indicator,
                "weighted_patch": _f(weighted_patch),
            }
        )

    masses = [Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)]
    u = [Fraction(1), Fraction(-2), Fraction(3, 2)]
    h0_u = [Fraction(2), Fraction(-1), Fraction(4)]
    k_u = [
        k_value * value
        for k_value, value in zip(k_values, u, strict=True)
    ]
    hc_u = [
        free + killed
        for free, killed in zip(h0_u, k_u, strict=True)
    ]
    u_norm_squared = _weighted_square(u, masses)
    ku_norm_squared = _weighted_square(k_u, masses)
    bound_squared = k_star * k_star * u_norm_squared
    if not ku_norm_squared <= bound_squared:
        raise AssertionError("finite multiplier norm certificate failed")
    if any(
        killed != combined - free
        for killed, combined, free in zip(k_u, hc_u, h0_u, strict=True)
    ):
        raise AssertionError("Hc=H0+K ledger failed")

    return {
        "B": _f(budget),
        "K_star": _f(k_star),
        "V_star": _f(v_star),
        "control_weights": [_f(value) for value in weights],
        "finite_vector_certificate": {
            "H0_u": [_f(value) for value in h0_u],
            "Hc_equals_H0_plus_Ku_componentwise": True,
            "Hc_u": [_f(value) for value in hc_u],
            "K_star_squared_times_u_norm_squared": _f(bound_squared),
            "K_u": [_f(value) for value in k_u],
            "K_u_norm_squared": _f(ku_norm_squared),
            "K_u_norm_le_K_star_u_norm": True,
            "mass_weights": [_f(value) for value in masses],
            "u": [_f(value) for value in u],
            "u_norm_squared": _f(u_norm_squared),
        },
        "indicator_derivative_taken": False,
        "patch_suprema": [_f(value) for value in suprema],
        "rows": rows,
        "torus_width": _f(width),
    }


def _sector_distance_rows() -> list[dict[str, Any]]:
    rows = []
    pi = gmpy2.const_pi()
    for rho in RHO_VALUES:
        rho_mp = _mp(rho)
        for phi_ratio in PHI_OVER_PI_VALUES:
            phi = _mp(phi_ratio) * pi
            cosine = gmpy2.cos(phi)
            sine = gmpy2.sin(phi)
            half_cosine = gmpy2.cos(phi / 2)
            for a_ratio in A_OVER_RHO_VALUES:
                a = a_ratio * rho
                a_mp = _mp(a)
                real = a_mp + rho_mp * cosine
                imaginary = rho_mp * sine
                distance_ratio = gmpy2.sqrt(real * real + imaginary * imaginary) / (
                    a_mp + rho_mp
                )
                rotated_real_ratio = half_cosine
                if distance_ratio + gmpy2.mpfr("1e-60") < _mp(S_THETA):
                    raise AssertionError("sector-distance bound failed")
                rows.append(
                    {
                        "a": _f(a),
                        "a_over_rho": _f(a_ratio),
                        "distance_ratio_hex": _hex(distance_ratio),
                        "phi_over_pi": _f(phi_ratio),
                        "rho": _f(rho),
                        "rotated_real_ratio_hex": _hex(rotated_real_ratio),
                    }
                )
    return rows


def _rotated_coercivity_rows() -> list[dict[str, Any]]:
    rows = []
    pi = gmpy2.const_pi()
    sigma_mp = _mp(SIGMA)
    for rho in RHO_VALUES:
        rho_mp = _mp(rho)
        for phi_ratio in PHI_OVER_PI_VALUES:
            phi = _mp(phi_ratio) * pi
            cosine = gmpy2.cos(phi)
            sine = gmpy2.sin(phi)
            omega_real = gmpy2.cos(phi / 2)
            omega_imag = -gmpy2.sin(phi / 2)
            for energy in ENERGY_TO_MASS_VALUES:
                energy_mp = _mp(energy)
                b_real = energy_mp + sigma_mp + rho_mp * cosine
                b_imag = rho_mp * sine
                rotated_real = omega_real * b_real - omega_imag * b_imag
                coercive_scale = energy_mp + sigma_mp + rho_mp
                ratio = rotated_real / coercive_scale
                if abs(ratio - omega_real) > gmpy2.mpfr("1e-60"):
                    raise AssertionError("rotated-coercivity identity failed")
                if ratio + gmpy2.mpfr("1e-60") < _mp(S_THETA):
                    raise AssertionError("rotated-coercivity lower bound failed")
                rows.append(
                    {
                        "b_imag_hex": _hex(b_imag),
                        "b_real_hex": _hex(b_real),
                        "coercive_scale_hex": _hex(coercive_scale),
                        "energy": _f(energy),
                        "mass": "1/1",
                        "omega_imag_hex": _hex(omega_imag),
                        "omega_real_hex": _hex(omega_real),
                        "phi_over_pi": _f(phi_ratio),
                        "rho": _f(rho),
                        "rotated_real_hex": _hex(rotated_real),
                        "rotated_real_over_scale_hex": _hex(ratio),
                    }
                )
    return rows


def _lambda_minus_z_rows() -> list[dict[str, Any]]:
    rows = []
    pi = gmpy2.const_pi()
    for rho in RHO_VALUES:
        rho_mp = _mp(rho)
        for phi_ratio in (Fraction(-2, 3), Fraction(2, 3)):
            phi = _mp(phi_ratio) * pi
            lambda_real = rho_mp * gmpy2.cos(phi)
            lambda_imag = rho_mp * gmpy2.sin(phi)
            z_angle = -Fraction(1, 3) if phi_ratio > 0 else Fraction(1, 3)
            rows.append(
                {
                    "lambda_angle_over_pi": _f(phi_ratio),
                    "lambda_imag_hex": _hex(lambda_imag),
                    "lambda_plus_z_norm_hex": "0x0.0p+0",
                    "lambda_real_hex": _hex(lambda_real),
                    "rho": _f(rho),
                    "z_angle_over_pi": _f(z_angle),
                    "z_imag_hex": _hex(-lambda_imag),
                    "z_real_hex": _hex(-lambda_real),
                }
            )
    return rows


def _contour_targets() -> list[dict[str, Any]]:
    rows = []
    for h in (Fraction(1, 2), Fraction(2)):
        for tau in TAU_VALUES:
            for derivative_order in R_VALUES:
                target = _mp(h) ** derivative_order * gmpy2.exp(
                    -_mp(tau) * _mp(h)
                )
                rows.append(
                    {
                        "closed_form_h_power_exp_minus_t_h_hex": _hex(target),
                        "h": _f(h),
                        "r": derivative_order,
                        "t": _f(tau),
                    }
                )
    return rows


def _majorant_rows() -> list[dict[str, Any]]:
    rows = []
    cos_theta = Fraction(1, 2)
    for tau in TAU_VALUES:
        a = tau * cos_theta
        a_mp = _mp(a)
        for derivative_order in R_VALUES:
            p = Fraction(2 * derivative_order + 1, 2)
            p_mp = _mp(p)
            x = a_mp * _mp(SIGMA)
            upper_gamma = gmpy2.gamma_inc(p_mp, x)
            closed_form = (
                gmpy2.exp(x)
                * a_mp ** (-p_mp)
                * upper_gamma
            )
            rows.append(
                {
                    "a_equals_tau_cos_theta": _f(a),
                    "integrand_power_r_minus_one_half": _f(
                        Fraction(2 * derivative_order - 1, 2)
                    ),
                    "p_equals_r_plus_one_half": _f(p),
                    "r": derivative_order,
                    "tau": _f(tau),
                    "upper_incomplete_gamma_closed_form_hex": _hex(closed_form),
                }
            )
    return rows


def build_fixture() -> dict[str, Any]:
    with gmpy2.context(gmpy2.get_context(), precision=PRECISION_BITS):
        distance_rows = _sector_distance_rows()
        coercivity_rows = _rotated_coercivity_rows()
        minimum_distance = min(
            float.fromhex(row["distance_ratio_hex"]) for row in distance_rows
        )
        minimum_coercivity = min(
            float.fromhex(row["rotated_real_over_scale_hex"])
            for row in coercivity_rows
        )
        if minimum_distance != 0.5 or minimum_coercivity != 0.5:
            raise AssertionError("sharp sector constant sentinel failed")
        return {
            "bounded_sharp_multiplier_algebra": _bounded_multiplier(),
            "claim_boundary": dict(PHYSICAL_CLAIMS),
            "dunford_contour": {
                "lambda_equals_minus_z": True,
                "rays": [
                    {
                        "angle_over_pi": "2/3",
                        "canonical_zero_to_infinity_dlambda_sign": "plus",
                        "contour_direction": "zero_to_infinity",
                        "id": "upper",
                    },
                    {
                        "angle_over_pi": "-2/3",
                        "canonical_zero_to_infinity_dlambda_sign": "minus",
                        "contour_direction": "infinity_to_zero",
                        "id": "lower",
                    },
                ],
                "scalar_orientation_targets": _contour_targets(),
                "standard_prefactor": "exp(sigma*t)/(2*pi*i)",
            },
            "fixture_parameters": {
                "box": BOX,
                "mode_window": {
                    "k_periodic": [-2, -1, 0, 1, 2],
                    "p_neumann_z": [0, 1, 2],
                    "q_neumann_r": [0, 1, 2],
                },
                "precision_bits": PRECISION_BITS,
                "rho": [_f(value) for value in RHO_VALUES],
                "r": list(R_VALUES),
                "sigma": _f(SIGMA),
                "tau": [_f(value) for value in TAU_VALUES],
                "theta_over_pi": _f(THETA_OVER_PI),
            },
            "lambda_minus_z_map": {
                "identity": "lambda=-z",
                "rows": _lambda_minus_z_rows(),
            },
            "mixed_neumann_periodic_principal_modes": {
                "mode_definition": "cos(p*pi*(z+1)/2)*cos(q*pi*(r+1)/2)*exp(i*2*pi*k*y)",
                "operator": "-d_z^2-2*d_r^2-d_y^2",
                "rows": _mode_rows(),
            },
            "positive_time_majorant": {
                "cos_theta": "1/2",
                "equation": "note_Eq_8.6",
                "integral": "int_0^infinity exp(-a*rho)*(sigma+rho)^(r-1/2) drho",
                "rows": _majorant_rows(),
                "tau_strictly_positive": True,
            },
            "schema": SCHEMA,
            "scope": {
                "algebraic_checks_only": True,
                "does_not_differentiate_sharp_indicator": True,
                "does_not_prove_PDE_H2": True,
                "does_not_supply_source_binding": True,
                "does_not_test_production_member": True,
                "fixed_box_dimension": 3,
                "neutral_fixture": True,
            },
            "sector_geometry": {
                "distance_rows": distance_rows,
                "lambda_sector": "nonzero_abs_arg_lambda_le_pi_minus_theta",
                "minimum_distance_ratio_hex": minimum_distance.hex(),
                "resolvent_majorant_samples": [
                    {
                        "factor_hex": _hex(
                            (_mp(SIGMA) + _mp(rho)) ** gmpy2.mpfr("-0.5")
                        ),
                        "rho": _f(rho),
                    }
                    for rho in RHO_VALUES
                ],
                "rotated_coercivity": {
                    "form_convention": "first_factor_conjugated",
                    "lambda_coefficient_not_conjugated": True,
                    "minimum_rotated_ratio_hex": minimum_coercivity.hex(),
                    "omega": "exp(-i*arg(lambda)/2)",
                    "rows": coercivity_rows,
                },
                "s_theta": _f(S_THETA),
                "sharp_equality_sampled_at": "abs_phi=pi-theta_and_a=rho",
            },
            "status": STATUS,
        }


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def _exclusive_write(output: Path, payload: bytes) -> None:
    output = output.resolve()
    if not output.parent.is_dir():
        raise FileNotFoundError(f"output parent does not exist: {output.parent}")
    descriptor = os.open(
        output,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o644,
    )
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            output.unlink()
        except FileNotFoundError:
            pass
        raise
    directory_descriptor = os.open(output.parent, os.O_RDONLY)
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="require exact canonical artifact bytes without writing",
    )
    arguments = parser.parse_args()
    try:
        expected = _canonical_bytes(build_fixture())
        expected_sha256 = hashlib.sha256(expected).hexdigest()
        output = arguments.output.resolve()
        if arguments.check:
            if not output.is_file():
                raise FileNotFoundError(f"artifact missing: {output}")
            actual = output.read_bytes()
            if actual != expected:
                raise ValueError(
                    "artifact bytes differ from regenerated fixture: "
                    f"expected_sha256={expected_sha256} "
                    f"actual_sha256={hashlib.sha256(actual).hexdigest()}"
                )
            print(
                "PASS complex_sector_h2_neutral_v1_check "
                f"sha256={expected_sha256} bytes={len(expected)} "
                "output_not_written=true"
            )
            return 0

        _exclusive_write(output, expected)
        print(
            "PASS complex_sector_h2_neutral_v1_build "
            f"sha256={expected_sha256} bytes={len(expected)} "
            "no_overwrite=true output_not_reopened=true"
        )
        return 0
    except (
        AssertionError,
        FileExistsError,
        FileNotFoundError,
        OSError,
        ValueError,
    ) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
