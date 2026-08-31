#!/usr/bin/env python3
"""Build a neutral one-dimensional free-residual scaling fixture.

The fixture evaluates the ideal analytic, exact-adjoint Scharfetter--Gummel
and periodic finite-volume families used by the encounter continuum programme.
It contains no production member, control, killing field, reaction-time result,
root, topology, or release payload.

Three deliberately separate checks are recorded:

* a cell-centred reflecting OU probe with zero endpoint derivative;
* periodic base and half-cell-shift Fourier probes;
* the vertex-dual constant mode, for which P_h 1 = rho_h and the endpoint
  half volumes produce the sharp square-root residual scale.
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
    / "artifacts/data/continuum_c2_one_sided_free_residual_neutral_fixture_v1.json"
)
SCHEMA = "encounter_continuum_c2_one_sided_free_residual_neutral_fixture_v1"
STATUS = "PASS_NEUTRAL_IDEAL_1D_FREE_RESIDUAL_SCALING_ONLY_COMPLETE_C2_HOLD"
PRECISION_BITS = 256
REFINEMENT_INTERVALS = (16, 32, 64, 128, 256)

OU_LOWER = Fraction(-3, 2)
OU_UPPER = Fraction(2)
OU_DIFFUSION = Fraction(1, 5)
OU_GAMMA = Fraction(3, 5)
OU_MEAN = Fraction(1, 4)

PERIODIC_WIDTH = Fraction(5, 2)
PERIODIC_DIFFUSION = Fraction(7, 9)
PERIODIC_MODE = 3


def _mp(value: Fraction | int) -> gmpy2.mpfr:
    exact = Fraction(value)
    return gmpy2.mpfr(exact.numerator) / gmpy2.mpfr(exact.denominator)


def _float_hex(value: gmpy2.mpfr | float) -> str:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("nonfinite numeric summary")
    if result == 0.0:
        result = 0.0
    return result.hex()


def _structural_zero(value: gmpy2.mpfr) -> gmpy2.mpfr:
    threshold = gmpy2.mpfr(2) ** (-PRECISION_BITS // 2 + 8)
    return gmpy2.mpfr(0) if abs(value) < threshold else value


def _bernoulli(value: gmpy2.mpfr) -> gmpy2.mpfr:
    return gmpy2.mpfr(1) if value == 0 else value / gmpy2.expm1(value)


def _potential(position: Fraction) -> Fraction:
    return (
        OU_GAMMA
        * (position - OU_MEAN) ** 2
        / (2 * OU_DIFFUSION)
    )


def _potential_prime(position: Fraction) -> Fraction:
    return OU_GAMMA * (position - OU_MEAN) / OU_DIFFUSION


def _gaussian_moments(
    lower: gmpy2.mpfr,
    upper: gmpy2.mpfr,
    alpha: gmpy2.mpfr,
    maximum_power: int,
) -> list[gmpy2.mpfr]:
    """Integrate y^k exp(-alpha*y^2) by a boundary recurrence."""

    if lower >= upper or alpha <= 0 or maximum_power < 0:
        raise ValueError("invalid Gaussian moment request")
    root = gmpy2.sqrt(alpha)
    moments = [
        gmpy2.sqrt(gmpy2.const_pi())
        * (gmpy2.erf(root * upper) - gmpy2.erf(root * lower))
        / (2 * root)
    ]
    if maximum_power == 0:
        return moments
    moments.append(
        (gmpy2.exp(-alpha * lower**2) - gmpy2.exp(-alpha * upper**2))
        / (2 * alpha)
    )
    for power in range(2, maximum_power + 1):
        boundary = (
            lower ** (power - 1) * gmpy2.exp(-alpha * lower**2)
            - upper ** (power - 1) * gmpy2.exp(-alpha * upper**2)
        ) / (2 * alpha)
        moments.append(
            boundary + (power - 1) * moments[power - 2] / (2 * alpha)
        )
    return moments


def _polynomial_product(
    left: dict[int, Fraction],
    right: dict[int, Fraction],
) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = result.get(power, Fraction(0)) + (
                left_coefficient * right_coefficient
            )
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def _polynomial_sum(
    *terms: tuple[Fraction, dict[int, Fraction]],
) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for scale, polynomial in terms:
        for power, coefficient in polynomial.items():
            result[power] = result.get(power, Fraction(0)) + scale * coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def _smoothstep_polynomial() -> dict[int, Fraction]:
    width = OU_UPPER - OU_LOWER
    scaled = {0: -OU_LOWER / width, 1: Fraction(1, 1) / width}
    squared = _polynomial_product(scaled, scaled)
    cubed = _polynomial_product(squared, scaled)
    return _polynomial_sum((Fraction(3), squared), (Fraction(-2), cubed))


def _differentiate(
    polynomial: dict[int, Fraction],
) -> dict[int, Fraction]:
    return {
        power - 1: power * coefficient
        for power, coefficient in polynomial.items()
        if power
    }


def _evaluate(
    polynomial: dict[int, Fraction],
    position: Fraction,
) -> Fraction:
    return sum(
        (coefficient * position**power for power, coefficient in polynomial.items()),
        Fraction(0),
    )


def _integrate_weighted_polynomial(
    polynomial: dict[int, Fraction],
    lower: Fraction,
    upper: Fraction,
) -> gmpy2.mpfr:
    alpha = _mp(OU_GAMMA / (2 * OU_DIFFUSION))
    mean = _mp(OU_MEAN)
    moments = _gaussian_moments(
        _mp(lower) - mean,
        _mp(upper) - mean,
        alpha,
        max(polynomial, default=0),
    )
    result = gmpy2.mpfr(0)
    for power, coefficient in polynomial.items():
        for centred_power in range(power + 1):
            translated = (
                coefficient
                * math.comb(power, centred_power)
                * OU_MEAN ** (power - centred_power)
            )
            result += _mp(translated) * moments[centred_power]
    return result


def _box_mass() -> gmpy2.mpfr:
    alpha = _mp(OU_GAMMA / (2 * OU_DIFFUSION))
    mean = _mp(OU_MEAN)
    return _gaussian_moments(
        _mp(OU_LOWER) - mean,
        _mp(OU_UPPER) - mean,
        alpha,
        0,
    )[0]


def _observed_order(
    coarse: dict[str, Any],
    fine: dict[str, Any],
    key: str,
) -> float:
    coarse_value = float.fromhex(coarse[key])
    fine_value = float.fromhex(fine[key])
    coarse_h = float.fromhex(coarse["h_hex"])
    fine_h = float.fromhex(fine["h_hex"])
    if min(coarse_value, fine_value, coarse_h, fine_h) <= 0:
        raise ValueError(f"invalid observed-order values for {key}")
    return math.log(coarse_value / fine_value) / math.log(coarse_h / fine_h)


def _cell_centred_row(intervals: int) -> dict[str, Any]:
    h = (OU_UPPER - OU_LOWER) / intervals
    positions = tuple(
        OU_LOWER + (index + Fraction(1, 2)) * h
        for index in range(intervals)
    )
    potentials = [_mp(_potential(position)) for position in positions]
    raw_masses = [
        _mp(h) * gmpy2.exp(-potential)
        for potential in potentials
    ]
    gauge = _box_mass() / sum(raw_masses, gmpy2.mpfr(0))
    probe = _smoothstep_polynomial()
    probe_prime = _differentiate(probe)
    projected = [
        _integrate_weighted_polynomial(
            probe,
            OU_LOWER + index * h,
            OU_LOWER + (index + 1) * h,
        )
        / (gauge * _mp(h) * gmpy2.exp(-potentials[index]))
        for index in range(intervals)
    ]

    dual_squared = gmpy2.mpfr(0)
    maximum_face_residual = gmpy2.mpfr(0)
    for left in range(intervals - 1):
        face = OU_LOWER + (left + 1) * h
        delta = potentials[left + 1] - potentials[left]
        conductance = (
            gauge
            * _mp(OU_DIFFUSION)
            / _mp(h)
            * gmpy2.exp(-potentials[left])
            * _bernoulli(delta)
        )
        continuum_flux = (
            _mp(OU_DIFFUSION)
            * gmpy2.exp(-_mp(_potential(face)))
            * _mp(_evaluate(probe_prime, face))
        )
        residual = conductance * (
            projected[left + 1] - projected[left]
        ) - continuum_flux
        dual_squared += residual * residual / conductance
        maximum_face_residual = max(maximum_face_residual, abs(residual))
    dual_norm = gmpy2.sqrt(dual_squared)
    return {
        "alignment": "cell_centred_reflecting_ou",
        "dual_energy_residual_norm_hex": _float_hex(dual_norm),
        "h_hex": _float_hex(_mp(h)),
        "intervals": intervals,
        "maximum_face_residual_hex": _float_hex(maximum_face_residual),
        "probe": "u(x)=3*s(x)^2-2*s(x)^3_with_s=(x-ell)/(r-ell)",
        "probe_endpoint_derivatives_zero": (
            _evaluate(probe_prime, OU_LOWER) == 0
            and _evaluate(probe_prime, OU_UPPER) == 0
        ),
        "residual_norm_over_h_hex": _float_hex(dual_norm / _mp(h)),
    }


def _vertex_dual_row(intervals: int) -> dict[str, Any]:
    h = (OU_UPPER - OU_LOWER) / intervals
    positions = tuple(
        OU_LOWER + index * h
        for index in range(intervals + 1)
    )
    volumes = tuple(
        h / 2 if index in (0, intervals) else h
        for index in range(intervals + 1)
    )
    potentials = [_mp(_potential(position)) for position in positions]
    raw_masses = [
        _mp(volume) * gmpy2.exp(-potential)
        for volume, potential in zip(volumes, potentials, strict=True)
    ]
    gauge = _box_mass() / sum(raw_masses, gmpy2.mpfr(0))
    masses = [gauge * raw for raw in raw_masses]

    physical_masses: list[gmpy2.mpfr] = []
    for index in range(intervals + 1):
        lower = OU_LOWER if index == 0 else positions[index] - h / 2
        upper = OU_UPPER if index == intervals else positions[index] + h / 2
        physical_masses.append(
            _integrate_weighted_polynomial({0: Fraction(1)}, lower, upper)
        )
    rhos = [
        physical / discrete
        for physical, discrete in zip(physical_masses, masses, strict=True)
    ]

    dual_squared = gmpy2.mpfr(0)
    endpoint_residuals: list[gmpy2.mpfr] = []
    for left in range(intervals):
        delta = potentials[left + 1] - potentials[left]
        conductance = (
            gauge
            * _mp(OU_DIFFUSION)
            / _mp(h)
            * gmpy2.exp(-potentials[left])
            * _bernoulli(delta)
        )
        residual = conductance * (rhos[left + 1] - rhos[left])
        dual_squared += residual * residual / conductance
        if left in (0, intervals - 1):
            endpoint_residuals.append(residual)
    dual_norm = gmpy2.sqrt(dual_squared)
    left_limit = (
        _mp(OU_DIFFUSION)
        * gmpy2.exp(-_mp(_potential(OU_LOWER)))
        * _mp(_potential_prime(OU_LOWER))
        / 4
    )
    right_limit = (
        _mp(OU_DIFFUSION)
        * gmpy2.exp(-_mp(_potential(OU_UPPER)))
        * _mp(_potential_prime(OU_UPPER))
        / 4
    )
    return {
        "alignment": "vertex_centred_reflecting_dual_ou",
        "constant_probe_continuum_operator_zero": True,
        "dual_energy_residual_norm_hex": _float_hex(dual_norm),
        "dual_norm_over_h_power_0_75_hex": _float_hex(
            dual_norm / _mp(h) ** gmpy2.mpfr("0.75")
        ),
        "dual_norm_over_sqrt_h_hex": _float_hex(
            dual_norm / gmpy2.sqrt(_mp(h))
        ),
        "endpoint_half_volumes_exact": (
            volumes[0] == h / 2
            and volumes[-1] == h / 2
            and all(volume == h for volume in volumes[1:-1])
        ),
        "h_hex": _float_hex(_mp(h)),
        "intervals": intervals,
        "left_endpoint_flux_defect_hex": _float_hex(endpoint_residuals[0]),
        "left_endpoint_limit_hex": _float_hex(left_limit),
        "left_endpoint_ratio_to_nonzero_limit_hex": _float_hex(
            endpoint_residuals[0] / left_limit
        ),
        "probe": "u(x)=1",
        "right_endpoint_flux_defect_hex": _float_hex(endpoint_residuals[1]),
        "right_endpoint_limit_hex": _float_hex(right_limit),
        "right_endpoint_ratio_to_nonzero_limit_hex": _float_hex(
            endpoint_residuals[1] / right_limit
        ),
    }


def _periodic_row(intervals: int, half_shift: bool) -> dict[str, Any]:
    h = PERIODIC_WIDTH / intervals
    shift = h / 2 if half_shift else Fraction(0)
    width = _mp(PERIODIC_WIDTH)
    diffusion = _mp(PERIODIC_DIFFUSION)
    wave_number = (
        2 * gmpy2.const_pi() * PERIODIC_MODE / width
    )
    z = wave_number * _mp(h) / 2
    sinc = gmpy2.sin(z) / z
    projected = [
        sinc
        * gmpy2.cos(
            wave_number
            * _mp(shift + (index + Fraction(1, 2)) * h)
        )
        for index in range(intervals)
    ]
    conductance = diffusion / (width * _mp(h))
    dual_squared = gmpy2.mpfr(0)
    for left in range(intervals):
        right = (left + 1) % intervals
        face = shift + (left + 1) * h
        continuum_flux = (
            -diffusion
            * wave_number
            / width
            * gmpy2.sin(wave_number * _mp(face))
        )
        residual = (
            conductance * (projected[right] - projected[left])
            - continuum_flux
        )
        dual_squared += residual * residual / conductance
    dual_norm = gmpy2.sqrt(dual_squared)
    closed_form = (
        gmpy2.sqrt(diffusion / 2)
        * wave_number
        * abs(1 - sinc * sinc)
    )
    return {
        "alignment": "periodic_half_shift" if half_shift else "periodic_base",
        "closed_form_dual_energy_residual_norm_hex": _float_hex(closed_form),
        "dual_energy_residual_norm_hex": _float_hex(dual_norm),
        "enumeration_minus_closed_form_hex": _float_hex(
            _structural_zero(abs(dual_norm - closed_form))
        ),
        "h_hex": _float_hex(_mp(h)),
        "intervals": intervals,
        "normalized_cell_mass_exact": str(h / PERIODIC_WIDTH),
        "probe": f"u(y)=cos(2*pi*{PERIODIC_MODE}*y/W)",
        "residual_norm_over_h_hex": _float_hex(dual_norm / _mp(h)),
        "wrapped_cell_count": 1 if half_shift else 0,
    }


def _orders(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    pair_orders = [
        _observed_order(coarse, fine, key)
        for coarse, fine in zip(rows, rows[1:], strict=False)
    ]
    return {
        "all_successive_orders": pair_orders,
        "last_pair_order": pair_orders[-1],
        "minimum_successive_order": min(pair_orders),
    }


def build_fixture() -> dict[str, Any]:
    with gmpy2.context(gmpy2.get_context(), precision=PRECISION_BITS):
        cell_rows = [
            _cell_centred_row(intervals)
            for intervals in REFINEMENT_INTERVALS
        ]
        vertex_rows = [
            _vertex_dual_row(intervals)
            for intervals in REFINEMENT_INTERVALS
        ]
        periodic_base_rows = [
            _periodic_row(intervals, False)
            for intervals in REFINEMENT_INTERVALS
        ]
        periodic_shift_rows = [
            _periodic_row(intervals, True)
            for intervals in REFINEMENT_INTERVALS
        ]
        translation_gaps = [
            abs(
                float.fromhex(base["dual_energy_residual_norm_hex"])
                - float.fromhex(shifted["dual_energy_residual_norm_hex"])
            )
            for base, shifted in zip(
                periodic_base_rows,
                periodic_shift_rows,
                strict=True,
            )
        ]

        left_limit = float.fromhex(vertex_rows[-1]["left_endpoint_limit_hex"])
        right_limit = float.fromhex(vertex_rows[-1]["right_endpoint_limit_hex"])
        if left_limit == 0.0 or right_limit == 0.0:
            raise AssertionError("vertex endpoint limit must be nonzero")

        return {
            "claim_boundary": {
                "all_alignment_tensor_residual_proved": False,
                "box_exhaustion_complete": False,
                "complete_C1": False,
                "complete_C2": False,
                "complete_C3": False,
                "continuum_rate_accepted": False,
                "formal_one_sided_free_residual_theorem_proved": False,
                "neutral_one_dimensional_residual_scaling_verified": True,
                "positive_budget_science": False,
                "production_acceptance_receipt": False,
                "production_evidence": False,
                "production_member_bound": False,
                "release_submission_ready": False,
                "release_submission_science_execution": False,
                "science_result": False,
            },
            "definitions": {
                "continuum_flux": "F=d*pi*u_prime",
                "discrete_energy_norm": (
                    "||v_h||_(1,h)^2=||v_h||_h^2+a_h(v_h,v_h)"
                ),
                "exact_adjoint_projection": (
                    "P_h[u]_i=(integral_C_i u*pi)/m_i"
                ),
                "face_defect": (
                    "E_(i+1/2)=c_(i+1/2)*(P_hu_(i+1)-P_hu_i)-F_(i+1/2)"
                ),
                "residual_dual_energy_norm": (
                    "(sum_edges E_edge^2/c_edge)^(1/2)"
                ),
                "vertex_constant_mode": "P_h[1]=rho_h=M_i/m_i",
            },
            "fixture_grid": {
                "intervals": list(REFINEMENT_INTERVALS),
                "precision_bits": PRECISION_BITS,
            },
            "ideal_parameters": {
                "ou": {
                    "diffusion": str(OU_DIFFUSION),
                    "gamma": str(OU_GAMMA),
                    "lower": str(OU_LOWER),
                    "mean": str(OU_MEAN),
                    "reference_density_normalizer": "1",
                    "upper": str(OU_UPPER),
                },
                "periodic": {
                    "diffusion": str(PERIODIC_DIFFUSION),
                    "fourier_mode": PERIODIC_MODE,
                    "width": str(PERIODIC_WIDTH),
                },
            },
            "numerical_encoding": {
                "arithmetic": "gmpy2_mpfr_at_256_bits_then_binary64_hex_summary",
                "json": "utf8_indent_2_sorted_keys_ascii_newline",
            },
            "periodic": {
                "base_rows": periodic_base_rows,
                "base_scaling": _orders(
                    periodic_base_rows,
                    "dual_energy_residual_norm_hex",
                ),
                "half_shift_rows": periodic_shift_rows,
                "half_shift_scaling": _orders(
                    periodic_shift_rows,
                    "dual_energy_residual_norm_hex",
                ),
                "translation_gap_max_hex": float(max(translation_gaps)).hex(),
                "uniform_O_h_requirement_supported": (
                    _orders(
                        periodic_base_rows,
                        "dual_energy_residual_norm_hex",
                    )["minimum_successive_order"]
                    >= 1
                    and _orders(
                        periodic_shift_rows,
                        "dual_energy_residual_norm_hex",
                    )["minimum_successive_order"]
                    >= 1
                ),
            },
            "reflecting_cell_centred": {
                "rows": cell_rows,
                "scaling": _orders(
                    cell_rows,
                    "dual_energy_residual_norm_hex",
                ),
                "uniform_O_h_requirement_supported": (
                    _orders(
                        cell_rows,
                        "dual_energy_residual_norm_hex",
                    )["minimum_successive_order"]
                    >= 1
                ),
            },
            "schema": SCHEMA,
            "scope": {
                "does_not_contain": [
                    "production_rates_or_centres",
                    "control_or_killing_payload",
                    "reaction_time_or_root_result",
                    "positive_budget_topology",
                    "tensor_or_asynchronous_residual_proof",
                    "complex_sector_regularity_proof",
                    "C1_C2_C3_or_release_receipt",
                ],
                "ideal_analytic_only": True,
                "source_formula_files": [
                    "notes/continuum_c1_free_form_and_functional_bridge_candidate.md",
                    "notes/continuum_c2_qf2_checkerboard_and_residual_route_candidate.md",
                    "code/rate_defined_tensor_f0.py",
                ],
            },
            "status": STATUS,
            "vertex_dual": {
                "analytic_sharpness_certificate": {
                    "any_uniform_alpha_greater_than_one_half_rejected": True,
                    "left_endpoint_limit": (
                        "d*pi(ell)*Phi_prime(ell)/4_nonzero"
                    ),
                    "logic": (
                        "u=1_has_Au=0_but_P_h1=rho;_E_left_tends_to_a_nonzero_"
                        "constant_and_c_left_is_Theta(1/h),_so_the_residual_dual_"
                        "energy_norm_is_bounded_below_by_C*sqrt(h)"
                    ),
                    "regularity_cannot_repair": (
                        "the_witness_u=1_is_smooth"
                    ),
                    "right_endpoint_limit": (
                        "d*pi(r)*Phi_prime(r)/4_nonzero"
                    ),
                },
                "rows": vertex_rows,
                "scaling": _orders(
                    vertex_rows,
                    "dual_energy_residual_norm_hex",
                ),
                "sqrt_h_scaled_last_pair_relative_change_hex": _float_hex(
                    abs(
                        _mp(
                            Fraction.from_float(
                                float.fromhex(
                                    vertex_rows[-1][
                                        "dual_norm_over_sqrt_h_hex"
                                    ]
                                )
                            )
                        )
                        / _mp(
                            Fraction.from_float(
                                float.fromhex(
                                    vertex_rows[-2][
                                        "dual_norm_over_sqrt_h_hex"
                                    ]
                                )
                            )
                        )
                        - 1
                    )
                ),
                "square_root_rate_supported": (
                    0.45
                    <= _orders(
                        vertex_rows,
                        "dual_energy_residual_norm_hex",
                    )["last_pair_order"]
                    <= 0.55
                ),
            },
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
                "PASS one_sided_free_residual_neutral_v1_check "
                f"sha256={expected_sha256} bytes={len(expected)} "
                "output_not_written=true"
            )
            return 0

        _exclusive_write(output, expected)
        print(
            "PASS one_sided_free_residual_neutral_v1_build "
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
