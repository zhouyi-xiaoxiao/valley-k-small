#!/usr/bin/env python3
"""Fail-closed adversarial mutations for the Round-11 neutral fixture."""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
ARTIFACT = (
    REPORT
    / "artifacts/data/continuum_c2_complex_sector_h2_neutral_fixture_v1.json"
)
INDEPENDENT_TEST = (
    REPORT
    / "code/test_continuum_c2_complex_sector_h2_neutral_fixture_v1.py"
)

FORBIDDEN_RUNTIME_MARKERS = (
    "Traceback (most recent call last)",
    "ModuleNotFoundError",
    "ImportError",
)


def _canonical(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def _validate(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(INDEPENDENT_TEST),
            "--artifact",
            str(path),
        ],
        cwd=REPORT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _require_clean_baseline(
    result: subprocess.CompletedProcess[str],
) -> int:
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if (
        result.returncode != 0
        or not lines
        or any(marker in result.stdout for marker in FORBIDDEN_RUNTIME_MARKERS)
    ):
        raise AssertionError(
            "canonical baseline did not pass cleanly\n"
            f"returncode={result.returncode}\n{result.stdout}"
        )
    match = re.fullmatch(r"SUMMARY ([1-9][0-9]*)/\1 PASS", lines[-1])
    if match is None:
        raise AssertionError(
            "canonical baseline lacks an exact all-pass summary\n"
            f"returncode={result.returncode}\n{result.stdout}"
        )
    return int(match.group(1))


def _require_semantic_rejection(
    name: str,
    result: subprocess.CompletedProcess[str],
    *,
    allowed_error_kinds: tuple[str, ...] = ("AssertionError",),
) -> None:
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    error_lines = [line for line in lines if line.startswith("ERROR ")]
    allowed_prefixes = tuple(
        f"ERROR {kind}: " for kind in allowed_error_kinds
    )
    if (
        result.returncode != 1
        or not lines
        or len(error_lines) != 1
        or lines[-1] != error_lines[0]
        or not error_lines[0].startswith(allowed_prefixes)
        or any(line.startswith("SUMMARY ") for line in lines)
        or any(marker in result.stdout for marker in FORBIDDEN_RUNTIME_MARKERS)
    ):
        raise AssertionError(
            "mutation did not receive an allowed semantic ERROR exit=1: "
            f"{name}\nreturncode={result.returncode}\n{result.stdout}"
        )


def main() -> int:
    baseline = _validate(ARTIFACT)
    baseline_checks = _require_clean_baseline(baseline)
    print(f"PASS canonical_baseline_validator_{baseline_checks}_of_{baseline_checks}")

    base = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        (
            "complete_C2_promotion",
            lambda value: value["claim_boundary"].__setitem__(
                "complete_C2",
                True,
            ),
        ),
        (
            "production_promotion",
            lambda value: value["claim_boundary"].__setitem__(
                "production_evidence",
                True,
            ),
        ),
        (
            "source_bound_resolvent_promotion",
            lambda value: value["claim_boundary"].__setitem__(
                "source_bound_resolvent_comparison",
                True,
            ),
        ),
        (
            "false_boolean_numeric_alias",
            lambda value: value["claim_boundary"].__setitem__(
                "complete_C2",
                0,
            ),
        ),
        (
            "extra_physical_claim",
            lambda value: value["claim_boundary"].__setitem__(
                "invented_claim",
                False,
            ),
        ),
        (
            "numerical_PDE_H2_promotion",
            lambda value: value["scope"].__setitem__(
                "does_not_prove_PDE_H2",
                False,
            ),
        ),
        (
            "false_H2_inverse_lambda_decay",
            lambda value: value["claim_boundary"].__setitem__(
                "H2_resolvent_decay_as_abs_lambda_inverse",
                True,
            ),
        ),
        (
            "mode_eigenvalue_exact",
            lambda value: value["mixed_neumann_periodic_principal_modes"][
                "rows"
            ][1].__setitem__("eigenvalue_over_pi_squared", "1/3"),
        ),
        (
            "mode_integer_boolean_alias",
            lambda value: value["mixed_neumann_periodic_principal_modes"][
                "rows"
            ][1].__setitem__("p_neumann_z", True),
        ),
        (
            "mode_boundary_trace",
            lambda value: value["mixed_neumann_periodic_principal_modes"][
                "rows"
            ][0].__setitem__(
                "z_endpoint_normal_derivatives_exact_zero",
                False,
            ),
        ),
        (
            "mode_row_order",
            lambda value: value["mixed_neumann_periodic_principal_modes"].__setitem__(
                "rows",
                list(
                    reversed(
                        value["mixed_neumann_periodic_principal_modes"]["rows"]
                    )
                ),
            ),
        ),
        (
            "differentiated_sharp_indicator",
            lambda value: value["bounded_sharp_multiplier_algebra"].__setitem__(
                "indicator_derivative_taken",
                True,
            ),
        ),
        (
            "nonbinary_sharp_indicator",
            lambda value: value["bounded_sharp_multiplier_algebra"]["rows"][
                0
            ].__setitem__("sharp_indicator", 2),
        ),
        (
            "multiplier_norm_bound",
            lambda value: value["bounded_sharp_multiplier_algebra"][
                "finite_vector_certificate"
            ].__setitem__("K_u_norm_squared", "999/1"),
        ),
        (
            "wrong_theta",
            lambda value: value["fixture_parameters"].__setitem__(
                "theta_over_pi",
                "1/4",
            ),
        ),
        (
            "wrong_sector",
            lambda value: value["sector_geometry"]["distance_rows"][0].__setitem__(
                "phi_over_pi",
                "-3/4",
            ),
        ),
        (
            "sector_distance",
            lambda value: value["sector_geometry"]["distance_rows"][0].__setitem__(
                "distance_ratio_hex",
                "0x1.0p-3",
            ),
        ),
        (
            "resolvent_half_power",
            lambda value: value["sector_geometry"][
                "resolvent_majorant_samples"
            ][0].__setitem__("factor_hex", "0x1.0p+0"),
        ),
        (
            "second_factor_conjugation",
            lambda value: value["sector_geometry"]["rotated_coercivity"].__setitem__(
                "form_convention",
                "second_factor_conjugated",
            ),
        ),
        (
            "conjugated_lambda_coefficient",
            lambda value: value["sector_geometry"]["rotated_coercivity"].__setitem__(
                "lambda_coefficient_not_conjugated",
                False,
            ),
        ),
        (
            "wrong_rotation_sign",
            lambda value: value["sector_geometry"]["rotated_coercivity"].__setitem__(
                "omega",
                "exp(+i*arg(lambda)/2)",
            ),
        ),
        (
            "rotated_coercivity_value",
            lambda value: value["sector_geometry"]["rotated_coercivity"][
                "rows"
            ][0].__setitem__("rotated_real_over_scale_hex", "0x1.0p-3"),
        ),
        (
            "rotated_coercivity_nested_unknown_key",
            lambda value: value["sector_geometry"]["rotated_coercivity"][
                "rows"
            ][0].__setitem__("complete_C2", True),
        ),
        (
            "lambda_equals_z",
            lambda value: value["lambda_minus_z_map"].__setitem__(
                "identity",
                "lambda=z",
            ),
        ),
        (
            "lambda_z_component",
            lambda value: value["lambda_minus_z_map"]["rows"][0].__setitem__(
                "z_real_hex",
                value["lambda_minus_z_map"]["rows"][0]["lambda_real_hex"],
            ),
        ),
        (
            "lambda_z_nested_unknown_key",
            lambda value: value["lambda_minus_z_map"]["rows"][0].__setitem__(
                "production_evidence",
                True,
            ),
        ),
        (
            "upper_ray_reversed",
            lambda value: value["dunford_contour"]["rays"][0].__setitem__(
                "contour_direction",
                "infinity_to_zero",
            ),
        ),
        (
            "lower_ray_orientation_flip",
            lambda value: value["dunford_contour"]["rays"][1].__setitem__(
                "contour_direction",
                "zero_to_infinity",
            ),
        ),
        (
            "lower_ray_dlambda_sign",
            lambda value: value["dunford_contour"]["rays"][1].__setitem__(
                "canonical_zero_to_infinity_dlambda_sign",
                "plus",
            ),
        ),
        (
            "Dunford_prefactor",
            lambda value: value["dunford_contour"].__setitem__(
                "standard_prefactor",
                "exp(sigma*t)/(pi*i)",
            ),
        ),
        (
            "Dunford_scalar_target",
            lambda value: value["dunford_contour"]["scalar_orientation_targets"][
                0
            ].__setitem__(
                "closed_form_h_power_exp_minus_t_h_hex",
                "0x1.0p+0",
            ),
        ),
        (
            "Dunford_target_integer_boolean_alias",
            lambda value: value["dunford_contour"]["scalar_orientation_targets"][
                1
            ].__setitem__("r", True),
        ),
        (
            "Dunford_target_nested_unknown_key",
            lambda value: value["dunford_contour"]["scalar_orientation_targets"][
                0
            ].__setitem__("release_submission_ready", True),
        ),
        (
            "tau_zero",
            lambda value: value["positive_time_majorant"]["rows"][0].__setitem__(
                "tau",
                "0/1",
            ),
        ),
        (
            "tau_zero_extension",
            lambda value: value["claim_boundary"].__setitem__(
                "tau_zero_extension",
                True,
            ),
        ),
        (
            "majorant_power",
            lambda value: value["positive_time_majorant"]["rows"][0].__setitem__(
                "integrand_power_r_minus_one_half",
                "1/2",
            ),
        ),
        (
            "incomplete_gamma_value",
            lambda value: value["positive_time_majorant"]["rows"][0].__setitem__(
                "upper_incomplete_gamma_closed_form_hex",
                "0x1.0p+0",
            ),
        ),
        (
            "incomplete_gamma_integer_boolean_alias",
            lambda value: value["positive_time_majorant"]["rows"][1].__setitem__(
                "r",
                True,
            ),
        ),
        (
            "incomplete_gamma_nested_unknown_key",
            lambda value: value["positive_time_majorant"]["rows"][0].__setitem__(
                "unconditional_reconstructed_resolvent_C2_rate",
                True,
            ),
        ),
        (
            "schema",
            lambda value: value.__setitem__("schema", "wrong"),
        ),
        (
            "status",
            lambda value: value.__setitem__("status", "wrong"),
        ),
    ]

    passes = 0
    with tempfile.TemporaryDirectory(
        prefix="complex-sector-h2-neutral-mutations-"
    ) as directory:
        root = Path(directory)
        canonical_copy = root / "canonical_custom_branch.json"
        canonical_copy.write_bytes(ARTIFACT.read_bytes())
        custom_baseline_checks = _require_clean_baseline(
            _validate(canonical_copy)
        )
        if custom_baseline_checks != baseline_checks - 6:
            raise AssertionError(
                "default/custom baseline count relation changed: "
                f"default={baseline_checks} custom={custom_baseline_checks}"
            )
        print(
            "PASS canonical_custom_branch_baseline_validator_"
            f"{custom_baseline_checks}_of_{custom_baseline_checks}"
        )

        for name, mutate in mutations:
            candidate = copy.deepcopy(base)
            mutate(candidate)
            path = root / f"{name}.json"
            path.write_bytes(_canonical(candidate))
            result = _validate(path)
            _require_semantic_rejection(name, result)
            print(f"PASS reject_{name}")
            passes += 1

        duplicate = root / "duplicate_key.json"
        raw = ARTIFACT.read_text(encoding="utf-8")
        duplicate.write_text(
            raw.replace(
                '{\n  "bounded_sharp_multiplier_algebra"',
                '{\n  "schema": "duplicate",\n  "bounded_sharp_multiplier_algebra"',
                1,
            ),
            encoding="utf-8",
        )
        _require_semantic_rejection(
            "duplicate_key",
            _validate(duplicate),
            allowed_error_kinds=("ValueError",),
        )
        print("PASS reject_duplicate_key")
        passes += 1

        noncanonical = root / "noncanonical.json"
        noncanonical.write_text(
            json.dumps(base, sort_keys=False),
            encoding="utf-8",
        )
        _require_semantic_rejection(
            "noncanonical_json",
            _validate(noncanonical),
        )
        print("PASS reject_noncanonical_json")
        passes += 1

        malformed = root / "malformed.json"
        malformed.write_text('{"schema":', encoding="utf-8")
        _require_semantic_rejection(
            "malformed_json",
            _validate(malformed),
            allowed_error_kinds=("JSONDecodeError",),
        )
        print("PASS reject_malformed_json")
        passes += 1

    total = passes + 2
    print(f"SUMMARY {total}/{total} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
