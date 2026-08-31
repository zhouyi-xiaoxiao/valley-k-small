#!/usr/bin/env python3
"""Adversarial mutations for the neutral one-sided free-residual fixture."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
ARTIFACT = (
    REPORT
    / "artifacts/data/continuum_c2_one_sided_free_residual_neutral_fixture_v1.json"
)
INDEPENDENT_TEST = (
    REPORT
    / "code/test_continuum_c2_one_sided_free_residual_neutral_fixture_v1.py"
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


def _require_semantic_rejection(
    name: str,
    result: subprocess.CompletedProcess[str],
) -> None:
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    forbidden_runtime_markers = (
        "Traceback (most recent call last)",
        "ModuleNotFoundError",
        "ImportError",
    )
    if (
        result.returncode != 1
        or not lines
        or not any(line.startswith("ERROR ") for line in lines)
        or any(line.startswith("SUMMARY ") for line in lines)
        or any(marker in result.stdout for marker in forbidden_runtime_markers)
    ):
        raise AssertionError(
            "mutation did not receive a semantic validator rejection: "
            f"{name}\nreturncode={result.returncode}\n{result.stdout}"
        )


def main() -> int:
    baseline = _validate(ARTIFACT)
    baseline_lines = [
        line for line in baseline.stdout.splitlines() if line.strip()
    ]
    if (
        baseline.returncode != 0
        or not baseline_lines
        or baseline_lines[-1] != "SUMMARY 107/107 PASS"
    ):
        raise AssertionError(
            "unmodified canonical artifact did not pass the independent "
            f"validator\nreturncode={baseline.returncode}\n{baseline.stdout}"
        )
    print("PASS canonical_baseline_validator_107_of_107")

    base = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    mutations: list[
        tuple[str, Callable[[dict[str, Any]], None]]
    ] = [
        (
            "complete_c2",
            lambda value: value["claim_boundary"].__setitem__(
                "complete_C2",
                True,
            ),
        ),
        (
            "production_evidence",
            lambda value: value["claim_boundary"].__setitem__(
                "production_evidence",
                True,
            ),
        ),
        (
            "science_result",
            lambda value: value["claim_boundary"].__setitem__(
                "science_result",
                True,
            ),
        ),
        (
            "neutral_flag_false",
            lambda value: value["claim_boundary"].__setitem__(
                "neutral_one_dimensional_residual_scaling_verified",
                False,
            ),
        ),
        (
            "false_numeric_alias",
            lambda value: value["claim_boundary"].__setitem__(
                "complete_C2",
                0,
            ),
        ),
        (
            "true_numeric_alias",
            lambda value: value["claim_boundary"].__setitem__(
                "neutral_one_dimensional_residual_scaling_verified",
                1,
            ),
        ),
        (
            "extra_claim",
            lambda value: value["claim_boundary"].__setitem__(
                "invented",
                False,
            ),
        ),
        (
            "ideal_scope",
            lambda value: value["scope"].__setitem__(
                "ideal_analytic_only",
                False,
            ),
        ),
        (
            "remove_production_exclusion",
            lambda value: value["scope"]["does_not_contain"].remove(
                "production_rates_or_centres"
            ),
        ),
        (
            "precision_bits",
            lambda value: value["fixture_grid"].__setitem__(
                "precision_bits",
                53,
            ),
        ),
        (
            "cell_residual",
            lambda value: value["reflecting_cell_centred"]["rows"][0].__setitem__(
                "dual_energy_residual_norm_hex",
                "0x1.0p+0",
            ),
        ),
        (
            "cell_neumann_flag",
            lambda value: value["reflecting_cell_centred"]["rows"][0].__setitem__(
                "probe_endpoint_derivatives_zero",
                False,
            ),
        ),
        (
            "cell_row_order",
            lambda value: value["reflecting_cell_centred"].__setitem__(
                "rows",
                list(reversed(value["reflecting_cell_centred"]["rows"])),
            ),
        ),
        (
            "cell_recorded_order",
            lambda value: value["reflecting_cell_centred"]["scaling"][
                "all_successive_orders"
            ].__setitem__(0, 1.0),
        ),
        (
            "periodic_translation_gap",
            lambda value: value["periodic"].__setitem__(
                "translation_gap_max_hex",
                "0x1.0p-10",
            ),
        ),
        (
            "periodic_base_residual",
            lambda value: value["periodic"]["base_rows"][0].__setitem__(
                "dual_energy_residual_norm_hex",
                "0x1.0p+0",
            ),
        ),
        (
            "periodic_shift_residual",
            lambda value: value["periodic"]["half_shift_rows"][0].__setitem__(
                "dual_energy_residual_norm_hex",
                "0x1.0p+0",
            ),
        ),
        (
            "periodic_wrap_count",
            lambda value: value["periodic"]["half_shift_rows"][0].__setitem__(
                "wrapped_cell_count",
                0,
            ),
        ),
        (
            "periodic_mass",
            lambda value: value["periodic"]["base_rows"][0].__setitem__(
                "normalized_cell_mass_exact",
                "1/15",
            ),
        ),
        (
            "vertex_residual",
            lambda value: value["vertex_dual"]["rows"][0].__setitem__(
                "dual_energy_residual_norm_hex",
                "0x1.0p+0",
            ),
        ),
        (
            "vertex_endpoint_limit",
            lambda value: value["vertex_dual"]["rows"][0].__setitem__(
                "left_endpoint_limit_hex",
                "0x0.0p+0",
            ),
        ),
        (
            "vertex_half_volume",
            lambda value: value["vertex_dual"]["rows"][0].__setitem__(
                "endpoint_half_volumes_exact",
                False,
            ),
        ),
        (
            "vertex_alpha_certificate",
            lambda value: value["vertex_dual"][
                "analytic_sharpness_certificate"
            ].__setitem__(
                "any_uniform_alpha_greater_than_one_half_rejected",
                False,
            ),
        ),
        (
            "vertex_regularization_claim",
            lambda value: value["vertex_dual"][
                "analytic_sharpness_certificate"
            ].__setitem__(
                "regularity_cannot_repair",
                "H3_repairs_the_endpoint_defect",
            ),
        ),
        (
            "remove_vertex_row",
            lambda value: value["vertex_dual"]["rows"].pop(),
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
        prefix="one-sided-free-residual-mutations-"
    ) as directory:
        root = Path(directory)
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
                '{\n  "claim_boundary"',
                '{\n  "schema": "duplicate",\n  "claim_boundary"',
                1,
            ),
            encoding="utf-8",
        )
        result = _validate(duplicate)
        _require_semantic_rejection("duplicate_key", result)
        print("PASS reject_duplicate_key")
        passes += 1

        noncanonical = root / "noncanonical.json"
        noncanonical.write_text(
            json.dumps(base, sort_keys=False),
            encoding="utf-8",
        )
        result = _validate(noncanonical)
        _require_semantic_rejection("noncanonical_json", result)
        print("PASS reject_noncanonical_json")
        passes += 1

    total = passes + 1
    print(f"SUMMARY {total}/{total} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
