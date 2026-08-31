#!/usr/bin/env python3
"""Independent checks for the neutral one-sided free-residual fixture."""

from __future__ import annotations

import argparse
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

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
BUILDER = (
    REPORT
    / "code/continuum_c2_one_sided_free_residual_neutral_fixture_v1.py"
)
ARTIFACT = (
    REPORT
    / "artifacts/data/continuum_c2_one_sided_free_residual_neutral_fixture_v1.json"
)
EXPECTED_ARTIFACT_SHA256 = (
    "93364229ec1495f1fbb15f0319bfd85a7da44c4821c2a5b925e1bf8ac1ad80c7"
)
SCHEMA = "encounter_continuum_c2_one_sided_free_residual_neutral_fixture_v1"
STATUS = "PASS_NEUTRAL_IDEAL_1D_FREE_RESIDUAL_SCALING_ONLY_COMPLETE_C2_HOLD"
INTERVALS = (16, 32, 64, 128, 256)

OU_LOWER = -1.5
OU_UPPER = 2.0
OU_DIFFUSION = 0.2
OU_GAMMA = 0.6
OU_MEAN = 0.25

PERIODIC_WIDTH = 2.5
PERIODIC_DIFFUSION = 7.0 / 9.0
PERIODIC_MODE = 3


def _check(condition: bool, name: str) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"PASS {name}")


def _run_builder(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-B", str(BUILDER), *arguments],
        cwd=REPORT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


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


def _phi(x: float) -> float:
    return OU_GAMMA * (x - OU_MEAN) ** 2 / (2 * OU_DIFFUSION)


def _phi_prime(x: float) -> float:
    return OU_GAMMA * (x - OU_MEAN) / OU_DIFFUSION


def _smoothstep(x: float) -> float:
    s = (x - OU_LOWER) / (OU_UPPER - OU_LOWER)
    return 3 * s * s - 2 * s * s * s


def _smoothstep_prime(x: float) -> float:
    width = OU_UPPER - OU_LOWER
    s = (x - OU_LOWER) / width
    return 6 * s * (1 - s) / width


def _integral(function: Any, lower: float, upper: float) -> float:
    value, error = quad(
        function,
        lower,
        upper,
        epsabs=2e-14,
        epsrel=2e-14,
        limit=100,
    )
    if not math.isfinite(value) or error > 5e-12:
        raise AssertionError("independent quadrature failed")
    return value


def _bernoulli(value: float) -> float:
    return 1.0 if value == 0.0 else value / math.expm1(value)


def _independent_cell_centred(intervals: int) -> float:
    h = (OU_UPPER - OU_LOWER) / intervals
    positions = [OU_LOWER + (index + 0.5) * h for index in range(intervals)]
    potentials = [_phi(position) for position in positions]
    box_mass = _integral(
        lambda x: math.exp(-_phi(x)),
        OU_LOWER,
        OU_UPPER,
    )
    raw_masses = [h * math.exp(-potential) for potential in potentials]
    gauge = box_mass / math.fsum(raw_masses)
    projected = [
        _integral(
            lambda x: _smoothstep(x) * math.exp(-_phi(x)),
            OU_LOWER + index * h,
            OU_LOWER + (index + 1) * h,
        )
        / (gauge * h * math.exp(-potentials[index]))
        for index in range(intervals)
    ]
    terms: list[float] = []
    for left in range(intervals - 1):
        face = OU_LOWER + (left + 1) * h
        delta = potentials[left + 1] - potentials[left]
        conductance = (
            gauge
            * OU_DIFFUSION
            / h
            * math.exp(-potentials[left])
            * _bernoulli(delta)
        )
        continuum_flux = (
            OU_DIFFUSION
            * math.exp(-_phi(face))
            * _smoothstep_prime(face)
        )
        defect = (
            conductance * (projected[left + 1] - projected[left])
            - continuum_flux
        )
        terms.append(defect * defect / conductance)
    return math.sqrt(math.fsum(terms))


def _independent_vertex_constant(intervals: int) -> dict[str, float]:
    h = (OU_UPPER - OU_LOWER) / intervals
    positions = [OU_LOWER + index * h for index in range(intervals + 1)]
    potentials = [_phi(position) for position in positions]
    volumes = [
        h / 2 if index in (0, intervals) else h
        for index in range(intervals + 1)
    ]
    box_mass = _integral(
        lambda x: math.exp(-_phi(x)),
        OU_LOWER,
        OU_UPPER,
    )
    raw_masses = [
        volume * math.exp(-potential)
        for volume, potential in zip(volumes, potentials, strict=True)
    ]
    gauge = box_mass / math.fsum(raw_masses)
    masses = [gauge * raw for raw in raw_masses]
    physical_masses = []
    for index in range(intervals + 1):
        lower = OU_LOWER if index == 0 else positions[index] - h / 2
        upper = OU_UPPER if index == intervals else positions[index] + h / 2
        physical_masses.append(
            _integral(lambda x: math.exp(-_phi(x)), lower, upper)
        )
    rhos = [
        physical / discrete
        for physical, discrete in zip(physical_masses, masses, strict=True)
    ]
    terms: list[float] = []
    endpoints: list[float] = []
    for left in range(intervals):
        delta = potentials[left + 1] - potentials[left]
        conductance = (
            gauge
            * OU_DIFFUSION
            / h
            * math.exp(-potentials[left])
            * _bernoulli(delta)
        )
        defect = conductance * (rhos[left + 1] - rhos[left])
        terms.append(defect * defect / conductance)
        if left in (0, intervals - 1):
            endpoints.append(defect)
    return {
        "dual_norm": math.sqrt(math.fsum(terms)),
        "left_defect": endpoints[0],
        "left_limit": (
            OU_DIFFUSION
            * math.exp(-_phi(OU_LOWER))
            * _phi_prime(OU_LOWER)
            / 4
        ),
        "right_defect": endpoints[1],
        "right_limit": (
            OU_DIFFUSION
            * math.exp(-_phi(OU_UPPER))
            * _phi_prime(OU_UPPER)
            / 4
        ),
    }


def _independent_periodic_closed_form(intervals: int) -> float:
    h = PERIODIC_WIDTH / intervals
    wave_number = 2 * math.pi * PERIODIC_MODE / PERIODIC_WIDTH
    z = wave_number * h / 2
    sinc = math.sin(z) / z
    return (
        math.sqrt(PERIODIC_DIFFUSION / 2)
        * wave_number
        * abs(1 - sinc * sinc)
    )


def _assert_close(actual: float, expected: float, name: str) -> None:
    tolerance = max(3e-12 * abs(expected), 3e-14)
    _check(abs(actual - expected) <= tolerance, name)


def _row_map(rows: list[dict[str, Any]], alignment: str) -> dict[int, dict[str, Any]]:
    _check(
        [row["intervals"] for row in rows] == list(INTERVALS),
        f"{alignment}_row_order_exact",
    )
    _check(
        all(row["alignment"] == alignment for row in rows),
        f"{alignment}_labels_exact",
    )
    return {row["intervals"]: row for row in rows}


def _orders(rows: list[dict[str, Any]]) -> list[float]:
    result = []
    for coarse, fine in zip(rows, rows[1:], strict=False):
        coarse_value = float.fromhex(coarse["dual_energy_residual_norm_hex"])
        fine_value = float.fromhex(fine["dual_energy_residual_norm_hex"])
        coarse_h = float.fromhex(coarse["h_hex"])
        fine_h = float.fromhex(fine["h_hex"])
        result.append(
            math.log(coarse_value / fine_value)
            / math.log(coarse_h / fine_h)
        )
    return result


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

    _check(payload["schema"] == SCHEMA, "schema_exact")
    checks += 1
    _check(payload["status"] == STATUS, "status_exact")
    checks += 1
    _check(
        payload["fixture_grid"]
        == {"intervals": list(INTERVALS), "precision_bits": 256},
        "fixture_grid_exact",
    )
    checks += 1

    claims = payload["claim_boundary"]
    required_false = {
        "all_alignment_tensor_residual_proved",
        "box_exhaustion_complete",
        "complete_C1",
        "complete_C2",
        "complete_C3",
        "continuum_rate_accepted",
        "formal_one_sided_free_residual_theorem_proved",
        "positive_budget_science",
        "production_acceptance_receipt",
        "production_evidence",
        "production_member_bound",
        "release_submission_ready",
        "release_submission_science_execution",
        "science_result",
    }
    _check(
        set(claims) == required_false | {
            "neutral_one_dimensional_residual_scaling_verified"
        },
        "claim_keys_exact",
    )
    checks += 1
    _check(
        all(type(claims[key]) is bool and claims[key] is False for key in required_false),
        "all_C1_C2_C3_production_release_and_science_flags_false",
    )
    checks += 1
    _check(
        type(claims["neutral_one_dimensional_residual_scaling_verified"]) is bool
        and claims["neutral_one_dimensional_residual_scaling_verified"] is True,
        "only_neutral_scaling_flag_true",
    )
    checks += 1
    _check(
        payload["scope"]["ideal_analytic_only"] is True
        and "production_rates_or_centres" in payload["scope"]["does_not_contain"]
        and "tensor_or_asynchronous_residual_proof"
        in payload["scope"]["does_not_contain"],
        "ideal_only_scope_explicit",
    )
    checks += 1

    cell = payload["reflecting_cell_centred"]
    cell_rows = cell["rows"]
    cell_map = _row_map(cell_rows, "cell_centred_reflecting_ou")
    checks += 2
    for intervals in INTERVALS:
        row = cell_map[intervals]
        _check(
            type(row["probe_endpoint_derivatives_zero"]) is bool
            and row["probe_endpoint_derivatives_zero"] is True,
            f"cell_probe_neumann_N{intervals}",
        )
        checks += 1
        expected = _independent_cell_centred(intervals)
        _assert_close(
            float.fromhex(row["dual_energy_residual_norm_hex"]),
            expected,
            f"independent_cell_residual_N{intervals}",
        )
        checks += 1
    cell_orders = _orders(cell_rows)
    _check(min(cell_orders) > 1.9, "cell_residual_at_least_O_h")
    checks += 1
    _check(
        cell["uniform_O_h_requirement_supported"] is True
        and all(
            abs(left - right) < 2e-13
            for left, right in zip(
                cell_orders,
                cell["scaling"]["all_successive_orders"],
                strict=True,
            )
        ),
        "cell_recorded_orders_recomputed",
    )
    checks += 1

    periodic = payload["periodic"]
    base_rows = periodic["base_rows"]
    shift_rows = periodic["half_shift_rows"]
    base_map = _row_map(base_rows, "periodic_base")
    shift_map = _row_map(shift_rows, "periodic_half_shift")
    checks += 4
    for intervals in INTERVALS:
        expected = _independent_periodic_closed_form(intervals)
        base = base_map[intervals]
        shifted = shift_map[intervals]
        for label, row in (("base", base), ("shift", shifted)):
            _assert_close(
                float.fromhex(row["dual_energy_residual_norm_hex"]),
                expected,
                f"independent_periodic_{label}_N{intervals}",
            )
            checks += 1
            _check(
                float.fromhex(row["enumeration_minus_closed_form_hex"]) == 0.0,
                f"periodic_enumeration_closed_{label}_N{intervals}",
            )
            checks += 1
        _check(
            base["dual_energy_residual_norm_hex"]
            == shifted["dual_energy_residual_norm_hex"],
            f"periodic_shift_invariant_N{intervals}",
        )
        checks += 1
        _check(
            base["wrapped_cell_count"] == 0
            and shifted["wrapped_cell_count"] == 1,
            f"periodic_wrap_counts_N{intervals}",
        )
        checks += 1
        _check(
            Fraction(base["normalized_cell_mass_exact"])
            == Fraction(1, intervals)
            and Fraction(shifted["normalized_cell_mass_exact"])
            == Fraction(1, intervals),
            f"periodic_normalized_mass_N{intervals}",
        )
        checks += 1
    _check(
        float.fromhex(periodic["translation_gap_max_hex"]) == 0.0,
        "periodic_translation_gap_zero",
    )
    checks += 1
    _check(
        min(_orders(base_rows)) > 1.9
        and min(_orders(shift_rows)) > 1.9
        and periodic["uniform_O_h_requirement_supported"] is True,
        "periodic_residual_at_least_O_h",
    )
    checks += 1

    vertex = payload["vertex_dual"]
    vertex_rows = vertex["rows"]
    vertex_map = _row_map(
        vertex_rows,
        "vertex_centred_reflecting_dual_ou",
    )
    checks += 2
    for intervals in INTERVALS:
        row = vertex_map[intervals]
        _check(
            row["endpoint_half_volumes_exact"] is True
            and row["constant_probe_continuum_operator_zero"] is True,
            f"vertex_half_volume_and_constant_mode_N{intervals}",
        )
        checks += 1
        expected = _independent_vertex_constant(intervals)
        for key, field in (
            ("dual_norm", "dual_energy_residual_norm_hex"),
            ("left_defect", "left_endpoint_flux_defect_hex"),
            ("left_limit", "left_endpoint_limit_hex"),
            ("right_defect", "right_endpoint_flux_defect_hex"),
            ("right_limit", "right_endpoint_limit_hex"),
        ):
            _assert_close(
                float.fromhex(row[field]),
                expected[key],
                f"independent_vertex_{key}_N{intervals}",
            )
            checks += 1
    vertex_orders = _orders(vertex_rows)
    _check(
        0.50 < vertex_orders[-1] < 0.55
        and vertex["square_root_rate_supported"] is True,
        "vertex_last_pair_square_root_order",
    )
    checks += 1
    sqrt_scaled = [
        float.fromhex(row["dual_norm_over_sqrt_h_hex"])
        for row in vertex_rows
    ]
    _check(
        0.07 < sqrt_scaled[-1] < 0.10
        and abs(sqrt_scaled[-1] / sqrt_scaled[-2] - 1) < 0.03,
        "vertex_sqrt_h_scaled_nonzero_and_stabilizing",
    )
    checks += 1
    alpha_075 = [
        float.fromhex(row["dual_norm_over_h_power_0_75_hex"])
        for row in vertex_rows
    ]
    _check(
        alpha_075[-3] < alpha_075[-2] < alpha_075[-1],
        "vertex_alpha_0_75_quotient_eventually_increases",
    )
    checks += 1
    certificate = vertex["analytic_sharpness_certificate"]
    _check(
        certificate["any_uniform_alpha_greater_than_one_half_rejected"] is True
        and certificate["regularity_cannot_repair"]
        == "the_witness_u=1_is_smooth"
        and "nonzero" in certificate["left_endpoint_limit"]
        and "nonzero" in certificate["right_endpoint_limit"],
        "vertex_any_alpha_gt_half_analytic_boundary_explicit",
    )
    checks += 1

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=ARTIFACT)
    arguments = parser.parse_args()
    try:
        artifact = arguments.artifact.resolve()
        frozen_default = artifact == ARTIFACT.resolve()
        checks = 0
        if frozen_default:
            before = ARTIFACT.read_bytes()
            check_run = _run_builder("--check")
            _check(
                check_run.returncode == 0
                and check_run.stdout.startswith(
                    "PASS one_sided_free_residual_neutral_v1_check "
                )
                and "output_not_written=true" in check_run.stdout,
                "builder_check_regenerates_without_writing",
            )
            checks += 1
            _check(
                ARTIFACT.read_bytes() == before,
                "check_mode_preserves_artifact_bytes",
            )
            checks += 1
            with tempfile.TemporaryDirectory(
                prefix="one-sided-free-residual-"
            ) as directory:
                first = Path(directory) / "first.json"
                second = Path(directory) / "second.json"
                first_run = _run_builder("--output", str(first))
                second_run = _run_builder("--output", str(second))
                _check(
                    first_run.returncode == 0 and first.is_file(),
                    "clean_build_one",
                )
                checks += 1
                _check(
                    second_run.returncode == 0 and second.is_file(),
                    "clean_build_two",
                )
                checks += 1
                _check(
                    first.read_bytes() == second.read_bytes() == before,
                    "two_builds_byte_identical_and_current",
                )
                checks += 1
                duplicate_before = first.read_bytes()
                duplicate_run = _run_builder("--output", str(first))
                _check(
                    duplicate_run.returncode != 0,
                    "duplicate_output_rejected",
                )
                checks += 1
                _check(
                    first.read_bytes() == duplicate_before,
                    "duplicate_rejection_preserves_bytes",
                )
                checks += 1

        checks += validate_artifact(artifact, frozen_default=frozen_default)
        print(f"SUMMARY {checks}/{checks} PASS")
        return 0
    except (
        AssertionError,
        FileNotFoundError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
