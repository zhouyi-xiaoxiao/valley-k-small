#!/usr/bin/env python3
"""Independent verifier for the Round-11 neutral sector/contour fixture."""

from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

from scipy.integrate import quad
from scipy.special import gamma, gammaincc

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = (
    REPORT
    / "code/continuum_c2_complex_sector_h2_neutral_fixture_v1.py"
)
ARTIFACT = (
    REPORT
    / "artifacts/data/continuum_c2_complex_sector_h2_neutral_fixture_v1.json"
)
EXPECTED_ARTIFACT_SHA256 = (
    "c6975c3748761dd4314f424f6aec3b3781c0382aa5c8e957b72b0c0ef4cef001"
)
SCHEMA = "encounter_continuum_c2_complex_sector_h2_neutral_fixture_v1"
STATUS = "PASS_NEUTRAL_MIXED_NP_SECTOR_CONTOUR_ALGEBRA_ONLY_COMPLETE_C2_HOLD"

RHO_VALUES = (
    Fraction(1, 16),
    Fraction(1, 4),
    Fraction(1),
    Fraction(4),
    Fraction(16),
)
TAU_VALUES = (Fraction(1, 4), Fraction(1), Fraction(3))
PHI_VALUES = (
    Fraction(-2, 3),
    Fraction(-1, 3),
    Fraction(0),
    Fraction(1, 3),
    Fraction(2, 3),
)
A_RATIOS = (Fraction(0), Fraction(1, 4), Fraction(1), Fraction(4))
ENERGIES = (Fraction(0), Fraction(1, 3), Fraction(3))

PHYSICAL_CLAIM_KEYS = {
    "bounded_multiplier_domain_theorem_proved_by_fixture",
    "box_exhaustion_complete",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "complex_sector_H2_pde_estimate_proved_by_fixture",
    "dimension_uniform_H2_to_Linfinity",
    "formal_mixed_NP_graph_domain_proved_by_fixture",
    "H2_resolvent_decay_as_abs_lambda_inverse",
    "positive_budget_science",
    "production_acceptance_receipt",
    "production_evidence",
    "production_member_bound",
    "release_submission_ready",
    "release_submission_science_execution",
    "science_result",
    "source_bound_killing_residual",
    "source_bound_reconstruction_map",
    "source_bound_resolvent_comparison",
    "tau_zero_extension",
    "unconditional_reconstructed_resolvent_C2_rate",
}


def _check(condition: bool, name: str) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"PASS {name}")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load(path: Path) -> tuple[bytes, dict[str, Any]]:
    raw = path.read_bytes()
    payload = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
    )
    if type(payload) is not dict:
        raise AssertionError("artifact root must be an object")
    canonical = (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    _check(raw == canonical, "artifact_is_canonical_sorted_json")
    return raw, payload


def _f(value: Fraction | int) -> str:
    exact = Fraction(value)
    return f"{exact.numerator}/{exact.denominator}"


def _fraction(value: Any) -> Fraction:
    if type(value) is not str or "/" not in value:
        raise AssertionError(f"canonical rational required: {value!r}")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise AssertionError(f"invalid rational: {value!r}") from exc
    if _f(result) != value:
        raise AssertionError(f"noncanonical rational: {value!r}")
    return result


def _float_hex(value: Any) -> float:
    if type(value) is not str:
        raise AssertionError("float hex must be a string")
    try:
        result = float.fromhex(value)
    except ValueError as exc:
        raise AssertionError(f"invalid float hex: {value!r}") from exc
    if not math.isfinite(result):
        raise AssertionError("nonfinite float hex")
    canonical = 0.0 if result == 0.0 else result
    if canonical.hex() != value:
        raise AssertionError(f"noncanonical float hex: {value!r}")
    return canonical


def _close(actual: float, expected: float, name: str, scale: float = 1.0) -> None:
    tolerance = 5e-13 * max(scale, abs(expected), 1.0)
    _check(abs(actual - expected) <= tolerance, name)


def _json_exact_equal(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            _json_exact_equal(actual[key], expected[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _json_exact_equal(left, right)
            for left, right in zip(actual, expected, strict=True)
        )
    return actual == expected


def _independent_modes() -> list[tuple[Fraction, int, int, int]]:
    modes = []
    for p in range(3):
        for q in range(3):
            for k in range(-2, 3):
                coefficient = (
                    Fraction(p * p, 4)
                    + Fraction(q * q, 2)
                    + Fraction(4 * k * k)
                )
                modes.append((coefficient, p, q, k))
    return sorted(modes)


def _expected_multiplier() -> dict[str, Any]:
    weights = [Fraction(1, 10), Fraction(1, 5), Fraction(3, 10), Fraction(2, 5)]
    suprema = [Fraction(1), Fraction(3, 2), Fraction(2), Fraction(5, 2)]
    profiles = [
        [Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)],
        [Fraction(1, 2), Fraction(3, 4), Fraction(1), Fraction(5, 4)],
        suprema,
    ]
    indicators = [0, 1, 1]
    budget = Fraction(3, 2)
    k_star = Fraction(15, 4)
    k_values = []
    rows = []
    for index, (indicator, profile) in enumerate(
        zip(indicators, profiles, strict=True)
    ):
        weighted = sum(
            (
                weight * value
                for weight, value in zip(weights, profile, strict=True)
            ),
            Fraction(0),
        )
        potential = Fraction(indicator) * weighted
        killing = budget * potential
        k_values.append(killing)
        rows.append(
            {
                "K_c": _f(killing),
                "V_c": _f(potential),
                "patch_profile_values": [_f(value) for value in profile],
                "sample_index": index,
                "sharp_indicator": indicator,
                "weighted_patch": _f(weighted),
            }
        )
    masses = [Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)]
    u = [Fraction(1), Fraction(-2), Fraction(3, 2)]
    h0_u = [Fraction(2), Fraction(-1), Fraction(4)]
    k_u = [left * right for left, right in zip(k_values, u, strict=True)]
    hc_u = [left + right for left, right in zip(h0_u, k_u, strict=True)]

    def norm_squared(values: list[Fraction]) -> Fraction:
        return sum(
            (
                mass * value * value
                for mass, value in zip(masses, values, strict=True)
            ),
            Fraction(0),
        )

    u_squared = norm_squared(u)
    ku_squared = norm_squared(k_u)
    return {
        "B": "3/2",
        "K_star": "15/4",
        "V_star": "5/2",
        "control_weights": [_f(value) for value in weights],
        "finite_vector_certificate": {
            "H0_u": [_f(value) for value in h0_u],
            "Hc_equals_H0_plus_Ku_componentwise": True,
            "Hc_u": [_f(value) for value in hc_u],
            "K_star_squared_times_u_norm_squared": _f(
                k_star * k_star * u_squared
            ),
            "K_u": [_f(value) for value in k_u],
            "K_u_norm_squared": _f(ku_squared),
            "K_u_norm_le_K_star_u_norm": True,
            "mass_weights": [_f(value) for value in masses],
            "u": [_f(value) for value in u],
            "u_norm_squared": _f(u_squared),
        },
        "indicator_derivative_taken": False,
        "patch_suprema": [_f(value) for value in suprema],
        "rows": rows,
        "torus_width": "1/1",
    }


def _run_builder(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(BUILDER), *arguments],
        cwd=REPORT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _contour_scalar(h: float, t: float, derivative_order: int) -> float:
    sigma = 1.0
    angle = 2.0 * math.pi / 3.0
    upper_direction = cmath.exp(1j * angle)
    lower_direction = cmath.exp(-1j * angle)

    def oriented_integrand(rho: float) -> complex:
        upper = rho * upper_direction
        lower = rho * lower_direction
        upper_value = (
            (-upper - sigma) ** derivative_order
            * cmath.exp(t * upper)
            / (h + sigma + upper)
            * upper_direction
        )
        # The lower contour is rho=infinity -> 0, hence the minus sign
        # after rewriting both ray integrals over rho=0 -> infinity.
        lower_value = -(
            (-lower - sigma) ** derivative_order
            * cmath.exp(t * lower)
            / (h + sigma + lower)
            * lower_direction
        )
        return upper_value + lower_value

    imaginary, error = quad(
        lambda rho: oriented_integrand(rho).imag,
        0.0,
        math.inf,
        epsabs=2e-10,
        epsrel=2e-10,
        limit=500,
    )
    if not math.isfinite(imaginary) or error > 3e-8:
        raise AssertionError("independent Dunford quadrature failed")
    return math.exp(sigma * t) * imaginary / (2.0 * math.pi)


def validate_artifact(path: Path, *, frozen_default: bool) -> int:
    checks = 0
    raw, payload = _load(path)
    checks += 1

    if frozen_default:
        _check(
            hashlib.sha256(raw).hexdigest() == EXPECTED_ARTIFACT_SHA256,
            "frozen_artifact_sha256",
        )
        checks += 1

    expected_top = {
        "bounded_sharp_multiplier_algebra",
        "claim_boundary",
        "dunford_contour",
        "fixture_parameters",
        "lambda_minus_z_map",
        "mixed_neumann_periodic_principal_modes",
        "positive_time_majorant",
        "schema",
        "scope",
        "sector_geometry",
        "status",
    }
    _check(set(payload) == expected_top, "top_level_keys_exact")
    checks += 1
    _check(payload["schema"] == SCHEMA, "schema_exact")
    checks += 1
    _check(payload["status"] == STATUS, "status_exact")
    checks += 1

    claims = payload["claim_boundary"]
    _check(set(claims) == PHYSICAL_CLAIM_KEYS, "physical_claim_keys_exact")
    checks += 1
    _check(
        all(type(claims[key]) is bool and claims[key] is False for key in claims),
        "every_physical_claim_strict_boolean_false",
    )
    checks += 1
    expected_scope = {
        "algebraic_checks_only": True,
        "does_not_differentiate_sharp_indicator": True,
        "does_not_prove_PDE_H2": True,
        "does_not_supply_source_binding": True,
        "does_not_test_production_member": True,
        "fixed_box_dimension": 3,
        "neutral_fixture": True,
    }
    _check(
        _json_exact_equal(payload["scope"], expected_scope),
        "neutral_nonclaim_scope_exact",
    )
    checks += 1

    expected_parameters = {
        "box": {
            "diffusion_diagonal": ["1/1", "2/1", "1/1"],
            "periodic_width": "1/1",
            "r_interval": ["-1/1", "1/1"],
            "z_interval": ["-1/1", "1/1"],
        },
        "mode_window": {
            "k_periodic": [-2, -1, 0, 1, 2],
            "p_neumann_z": [0, 1, 2],
            "q_neumann_r": [0, 1, 2],
        },
        "precision_bits": 256,
        "rho": [_f(value) for value in RHO_VALUES],
        "r": [0, 1, 2],
        "sigma": "1/1",
        "tau": [_f(value) for value in TAU_VALUES],
        "theta_over_pi": "1/3",
    }
    _check(
        _json_exact_equal(payload["fixture_parameters"], expected_parameters),
        "fixture_parameters_exact",
    )
    checks += 1

    modes = payload["mixed_neumann_periodic_principal_modes"]
    _check(
        set(modes)
        == {"mode_definition", "operator", "rows"}
        and modes["mode_definition"]
        == "cos(p*pi*(z+1)/2)*cos(q*pi*(r+1)/2)*exp(i*2*pi*k*y)"
        and modes["operator"] == "-d_z^2-2*d_r^2-d_y^2",
        "mixed_NP_mode_definition_exact",
    )
    checks += 1
    expected_modes = _independent_modes()
    rows = modes["rows"]
    _check(len(rows) == len(expected_modes) == 45, "mixed_NP_mode_count_45")
    checks += 1
    mode_row_keys = {
        "conjugate_periodic_partner",
        "eigenvalue_hex",
        "eigenvalue_over_pi_squared",
        "k_periodic",
        "p_neumann_z",
        "q_neumann_r",
        "r_endpoint_normal_derivatives_exact_zero",
        "y_periodic_value_and_derivative_traces_match",
        "z_endpoint_normal_derivatives_exact_zero",
    }
    for index, (row, expected) in enumerate(
        zip(rows, expected_modes, strict=True)
    ):
        coefficient, p, q, k = expected
        _check(set(row) == mode_row_keys, f"mode_{index}_keys_exact")
        checks += 1
        _check(
            type(row["p_neumann_z"]) is int
            and type(row["q_neumann_r"]) is int
            and type(row["k_periodic"]) is int
            and row["p_neumann_z"] == p
            and row["q_neumann_r"] == q
            and row["k_periodic"] == k
            and row["eigenvalue_over_pi_squared"] == _f(coefficient)
            and _json_exact_equal(
                row["conjugate_periodic_partner"],
                [p, q, -k],
            ),
            f"mode_{index}_indices_and_exact_eigenvalue",
        )
        checks += 1
        _close(
            _float_hex(row["eigenvalue_hex"]),
            float(coefficient) * math.pi**2,
            f"mode_{index}_independent_numeric_eigenvalue",
            scale=200.0,
        )
        checks += 1
        _check(
            all(
                type(row[key]) is bool and row[key] is True
                for key in (
                    "r_endpoint_normal_derivatives_exact_zero",
                    "y_periodic_value_and_derivative_traces_match",
                    "z_endpoint_normal_derivatives_exact_zero",
                )
            ),
            f"mode_{index}_mixed_boundary_traces",
        )
        checks += 1

    _check(
        _json_exact_equal(
            payload["bounded_sharp_multiplier_algebra"],
            _expected_multiplier(),
        ),
        "bounded_sharp_multiplier_exact_rational_ledger",
    )
    checks += 1

    sector = payload["sector_geometry"]
    _check(
        set(sector)
        == {
            "distance_rows",
            "lambda_sector",
            "minimum_distance_ratio_hex",
            "resolvent_majorant_samples",
            "rotated_coercivity",
            "s_theta",
            "sharp_equality_sampled_at",
        }
        and sector["lambda_sector"]
        == "nonzero_abs_arg_lambda_le_pi_minus_theta"
        and sector["s_theta"] == "1/2"
        and sector["sharp_equality_sampled_at"]
        == "abs_phi=pi-theta_and_a=rho",
        "sector_metadata_exact",
    )
    checks += 1
    distance_rows = sector["distance_rows"]
    _check(len(distance_rows) == 100, "sector_distance_row_count_100")
    checks += 1
    distance_index = 0
    independent_minimum = math.inf
    for rho in RHO_VALUES:
        for phi_ratio in PHI_VALUES:
            phi = float(phi_ratio) * math.pi
            for a_ratio in A_RATIOS:
                row = distance_rows[distance_index]
                _check(
                    set(row)
                    == {
                        "a",
                        "a_over_rho",
                        "distance_ratio_hex",
                        "phi_over_pi",
                        "rho",
                        "rotated_real_ratio_hex",
                    }
                    and row["rho"] == _f(rho)
                    and row["phi_over_pi"] == _f(phi_ratio)
                    and row["a_over_rho"] == _f(a_ratio)
                    and row["a"] == _f(rho * a_ratio),
                    f"sector_distance_{distance_index}_coordinates",
                )
                checks += 1
                a = float(rho * a_ratio)
                rho_float = float(rho)
                expected_distance = abs(
                    a + rho_float * cmath.exp(1j * phi)
                ) / (a + rho_float)
                expected_rotated = math.cos(phi / 2.0)
                _close(
                    _float_hex(row["distance_ratio_hex"]),
                    expected_distance,
                    f"sector_distance_{distance_index}_independent",
                )
                checks += 1
                _close(
                    _float_hex(row["rotated_real_ratio_hex"]),
                    expected_rotated,
                    f"sector_rotation_{distance_index}_independent",
                )
                checks += 1
                _check(
                    expected_distance >= 0.5 - 2e-15
                    and expected_rotated >= 0.5 - 2e-15,
                    f"sector_bound_{distance_index}",
                )
                checks += 1
                independent_minimum = min(independent_minimum, expected_distance)
                distance_index += 1
    _close(
        _float_hex(sector["minimum_distance_ratio_hex"]),
        independent_minimum,
        "sharp_sector_distance_minimum_one_half",
    )
    checks += 1

    majorant_samples = sector["resolvent_majorant_samples"]
    _check(
        len(majorant_samples) == len(RHO_VALUES),
        "resolvent_majorant_sample_count",
    )
    checks += 1
    for index, (row, rho) in enumerate(
        zip(majorant_samples, RHO_VALUES, strict=True)
    ):
        _check(
            set(row) == {"factor_hex", "rho"} and row["rho"] == _f(rho),
            f"resolvent_majorant_{index}_coordinates",
        )
        checks += 1
        _close(
            _float_hex(row["factor_hex"]),
            (1.0 + float(rho)) ** -0.5,
            f"resolvent_majorant_{index}_sigma_plus_rho_minus_half",
        )
        checks += 1

    coercivity = sector["rotated_coercivity"]
    _check(
        set(coercivity)
        == {
            "form_convention",
            "lambda_coefficient_not_conjugated",
            "minimum_rotated_ratio_hex",
            "omega",
            "rows",
        }
        and coercivity["form_convention"] == "first_factor_conjugated"
        and coercivity["lambda_coefficient_not_conjugated"] is True
        and coercivity["omega"] == "exp(-i*arg(lambda)/2)",
        "first_factor_conjugated_rotation_metadata_exact",
    )
    checks += 1
    coercivity_rows = coercivity["rows"]
    _check(len(coercivity_rows) == 75, "rotated_coercivity_row_count_75")
    checks += 1
    coercivity_row_keys = {
        "b_imag_hex",
        "b_real_hex",
        "coercive_scale_hex",
        "energy",
        "mass",
        "omega_imag_hex",
        "omega_real_hex",
        "phi_over_pi",
        "rho",
        "rotated_real_hex",
        "rotated_real_over_scale_hex",
    }
    coercivity_index = 0
    independent_coercivity_minimum = math.inf
    for rho in RHO_VALUES:
        for phi_ratio in PHI_VALUES:
            phi = float(phi_ratio) * math.pi
            omega = cmath.exp(-0.5j * phi)
            for energy in ENERGIES:
                row = coercivity_rows[coercivity_index]
                _check(
                    set(row) == coercivity_row_keys
                    and row["rho"] == _f(rho)
                    and row["phi_over_pi"] == _f(phi_ratio)
                    and row["energy"] == _f(energy)
                    and row["mass"] == "1/1",
                    f"coercivity_{coercivity_index}_coordinates",
                )
                checks += 1
                b_value = float(energy) + 1.0 + float(rho) * cmath.exp(1j * phi)
                scale = float(energy) + 1.0 + float(rho)
                rotated_real = (omega * b_value).real
                ratio = rotated_real / scale
                numeric_expectations = {
                    "b_real_hex": b_value.real,
                    "b_imag_hex": b_value.imag,
                    "coercive_scale_hex": scale,
                    "omega_real_hex": omega.real,
                    "omega_imag_hex": omega.imag,
                    "rotated_real_hex": rotated_real,
                    "rotated_real_over_scale_hex": ratio,
                }
                for key, expected_value in numeric_expectations.items():
                    _close(
                        _float_hex(row[key]),
                        expected_value,
                        f"coercivity_{coercivity_index}_{key}",
                        scale=25.0,
                    )
                    checks += 1
                _check(
                    ratio >= 0.5 - 2e-15
                    and abs(ratio - math.cos(phi / 2.0)) <= 2e-15,
                    f"coercivity_{coercivity_index}_identity_and_bound",
                )
                checks += 1
                independent_coercivity_minimum = min(
                    independent_coercivity_minimum,
                    ratio,
                )
                coercivity_index += 1
    _close(
        _float_hex(coercivity["minimum_rotated_ratio_hex"]),
        independent_coercivity_minimum,
        "sharp_rotated_coercivity_minimum_one_half",
    )
    checks += 1

    mapping = payload["lambda_minus_z_map"]
    _check(
        set(mapping) == {"identity", "rows"} and mapping["identity"] == "lambda=-z",
        "lambda_equals_minus_z_identity_exact",
    )
    checks += 1
    mapping_rows = mapping["rows"]
    _check(len(mapping_rows) == 10, "lambda_minus_z_row_count_10")
    checks += 1
    mapping_row_keys = {
        "lambda_angle_over_pi",
        "lambda_imag_hex",
        "lambda_plus_z_norm_hex",
        "lambda_real_hex",
        "rho",
        "z_angle_over_pi",
        "z_imag_hex",
        "z_real_hex",
    }
    map_index = 0
    for rho in RHO_VALUES:
        for phi_ratio in (Fraction(-2, 3), Fraction(2, 3)):
            row = mapping_rows[map_index]
            phi = float(phi_ratio) * math.pi
            lambda_value = float(rho) * cmath.exp(1j * phi)
            z_value = -lambda_value
            expected_z_angle = (
                Fraction(-1, 3) if phi_ratio > 0 else Fraction(1, 3)
            )
            _check(
                set(row) == mapping_row_keys
                and row["rho"] == _f(rho)
                and row["lambda_angle_over_pi"] == _f(phi_ratio)
                and row["z_angle_over_pi"] == _f(expected_z_angle),
                f"lambda_z_{map_index}_angles",
            )
            checks += 1
            for key, expected_value in {
                "lambda_real_hex": lambda_value.real,
                "lambda_imag_hex": lambda_value.imag,
                "z_real_hex": z_value.real,
                "z_imag_hex": z_value.imag,
                "lambda_plus_z_norm_hex": 0.0,
            }.items():
                _close(
                    _float_hex(row[key]),
                    expected_value,
                    f"lambda_z_{map_index}_{key}",
                    scale=20.0,
                )
                checks += 1
            map_index += 1

    contour = payload["dunford_contour"]
    expected_rays = [
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
    ]
    _check(
        set(contour)
        == {
            "lambda_equals_minus_z",
            "rays",
            "scalar_orientation_targets",
            "standard_prefactor",
        }
        and contour["lambda_equals_minus_z"] is True
        and contour["standard_prefactor"] == "exp(sigma*t)/(2*pi*i)"
        and _json_exact_equal(contour["rays"], expected_rays),
        "Dunford_ray_angles_and_orientation_exact",
    )
    checks += 1
    targets = contour["scalar_orientation_targets"]
    _check(len(targets) == 18, "Dunford_scalar_target_count_18")
    checks += 1
    target_row_keys = {
        "closed_form_h_power_exp_minus_t_h_hex",
        "h",
        "r",
        "t",
    }
    target_index = 0
    for h_fraction in (Fraction(1, 2), Fraction(2)):
        for tau in TAU_VALUES:
            for derivative_order in (0, 1, 2):
                row = targets[target_index]
                expected = float(h_fraction) ** derivative_order * math.exp(
                    -float(tau * h_fraction)
                )
                _check(
                    set(row) == target_row_keys
                    and row["h"] == _f(h_fraction)
                    and row["t"] == _f(tau)
                    and type(row["r"]) is int
                    and row["r"] == derivative_order,
                    f"Dunford_target_{target_index}_coordinates",
                )
                checks += 1
                _close(
                    _float_hex(
                        row["closed_form_h_power_exp_minus_t_h_hex"]
                    ),
                    expected,
                    f"Dunford_target_{target_index}_closed_form",
                )
                checks += 1
                contour_value = _contour_scalar(
                    float(h_fraction),
                    float(tau),
                    derivative_order,
                )
                _check(
                    abs(contour_value - expected)
                    <= 8e-10 * max(1.0, abs(expected)),
                    f"Dunford_target_{target_index}_independent_oriented_rays",
                )
                checks += 1
                target_index += 1

    majorant = payload["positive_time_majorant"]
    _check(
        set(majorant)
        == {
            "cos_theta",
            "equation",
            "integral",
            "rows",
            "tau_strictly_positive",
        }
        and majorant["cos_theta"] == "1/2"
        and majorant["equation"] == "note_Eq_8.6"
        and majorant["integral"]
        == "int_0^infinity exp(-a*rho)*(sigma+rho)^(r-1/2) drho"
        and majorant["tau_strictly_positive"] is True,
        "Eq_8_6_majorant_metadata_exact",
    )
    checks += 1
    gamma_rows = majorant["rows"]
    _check(len(gamma_rows) == 9, "Eq_8_6_row_count_9")
    checks += 1
    gamma_row_keys = {
        "a_equals_tau_cos_theta",
        "integrand_power_r_minus_one_half",
        "p_equals_r_plus_one_half",
        "r",
        "tau",
        "upper_incomplete_gamma_closed_form_hex",
    }
    gamma_index = 0
    for tau in TAU_VALUES:
        a_fraction = tau / 2
        a = float(a_fraction)
        for derivative_order in (0, 1, 2):
            row = gamma_rows[gamma_index]
            p_fraction = Fraction(2 * derivative_order + 1, 2)
            exponent_fraction = Fraction(2 * derivative_order - 1, 2)
            _check(
                set(row) == gamma_row_keys
                and row["tau"] == _f(tau)
                and type(row["r"]) is int
                and row["r"] == derivative_order
                and row["a_equals_tau_cos_theta"] == _f(a_fraction)
                and row["p_equals_r_plus_one_half"] == _f(p_fraction)
                and row["integrand_power_r_minus_one_half"]
                == _f(exponent_fraction)
                and a > 0,
                f"Eq_8_6_{gamma_index}_coordinates_and_positive_tau",
            )
            checks += 1
            direct, error = quad(
                lambda rho: math.exp(-a * rho)
                * (1.0 + rho) ** (derivative_order - 0.5),
                0.0,
                math.inf,
                epsabs=2e-12,
                epsrel=2e-12,
                limit=300,
            )
            p = float(p_fraction)
            gamma_form = math.exp(a) * a ** (-p) * gamma(p) * gammaincc(p, a)
            _check(
                math.isfinite(direct)
                and error <= 2e-9 * max(1.0, abs(direct))
                and abs(direct - gamma_form)
                <= 3e-12 * max(1.0, abs(direct)),
                f"Eq_8_6_{gamma_index}_independent_integral_equals_gamma",
            )
            checks += 1
            _close(
                _float_hex(
                    row["upper_incomplete_gamma_closed_form_hex"]
                ),
                gamma_form,
                f"Eq_8_6_{gamma_index}_artifact_gamma_value",
                scale=gamma_form,
            )
            checks += 1
            gamma_index += 1

    if frozen_default:
        original_bytes = path.read_bytes()
        original_stat = path.stat()
        check_default = _run_builder("--check")
        _check(
            check_default.returncode == 0
            and check_default.stdout.startswith("PASS ")
            and path.read_bytes() == original_bytes
            and path.stat().st_mtime_ns == original_stat.st_mtime_ns,
            "builder_check_default_is_read_only",
        )
        checks += 1
        with tempfile.TemporaryDirectory(
            prefix="complex-sector-h2-neutral-"
        ) as directory:
            root = Path(directory)
            first = root / "first.json"
            second = root / "second.json"
            absent = root / "absent.json"
            first_run = _run_builder("--output", str(first))
            second_run = _run_builder("--output", str(second))
            _check(
                first_run.returncode == 0
                and second_run.returncode == 0
                and first.read_bytes() == second.read_bytes() == raw,
                "two_clean_builds_byte_identical_to_frozen_artifact",
            )
            checks += 1
            before = first.stat().st_mtime_ns
            matching_check = _run_builder(
                "--output",
                str(first),
                "--check",
            )
            _check(
                matching_check.returncode == 0
                and first.read_bytes() == raw
                and first.stat().st_mtime_ns == before,
                "builder_check_custom_is_read_only",
            )
            checks += 1
            overwrite = _run_builder("--output", str(first))
            _check(
                overwrite.returncode == 1
                and "ERROR " in overwrite.stdout
                and "Traceback" not in overwrite.stdout
                and first.read_bytes() == raw,
                "builder_exclusive_write_rejects_overwrite_semantically",
            )
            checks += 1
            absent_check = _run_builder(
                "--output",
                str(absent),
                "--check",
            )
            _check(
                absent_check.returncode == 1
                and "ERROR " in absent_check.stdout
                and not absent.exists(),
                "builder_check_absent_does_not_write",
            )
            checks += 1

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=ARTIFACT)
    arguments = parser.parse_args()
    try:
        path = arguments.artifact.resolve()
        checks = validate_artifact(
            path,
            frozen_default=path == ARTIFACT.resolve(),
        )
        print(f"SUMMARY {checks}/{checks} PASS")
        return 0
    except (
        AssertionError,
        FileNotFoundError,
        json.JSONDecodeError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"ERROR {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
