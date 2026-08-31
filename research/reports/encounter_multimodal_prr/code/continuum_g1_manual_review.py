#!/usr/bin/env python3
"""Reproduce and classify the theta=0.7 post-result derivative wiggle.

This calculation is deliberately separate from the frozen G1b discovery.  It
cannot create a fold candidate, authorize the old line-empty action, or verify
the continuum model.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import continuum_g1_discovery as discovery
import numpy as np
import scipy

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
MANIFEST = DATA / "continuum_g1_manual_review_manifest.json"
FORMAL_RESULT = DATA / "continuum_g1_discovery_result.json"
OUTPUT = DATA / "continuum_g1_manual_review_result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if type(value) is not dict:
        raise ValueError(f"{path} must contain one JSON object")
    return value


def repository_venv() -> Path:
    return (REPOSITORY / ".venv").resolve()


def require_repository_venv() -> None:
    if Path(sys.prefix).resolve() != repository_venv():
        raise RuntimeError("manual review must run inside the repository .venv")


def configuration_from_manifest(manifest: dict[str, Any]) -> discovery.RunConfiguration:
    mesh = manifest["mesh"]
    time_grid = manifest["time_grid"]
    theta = manifest["control"]["theta"]
    configuration = discovery.RunConfiguration(
        midpoint_cells=mesh["midpoint_cells"],
        relative_parallel_cells=mesh["relative_parallel_cells"],
        relative_perp_cells=mesh["relative_perp_cells"],
        theta_values=(theta,),
        time_start=time_grid["start"],
        time_stop=time_grid["stop"],
        time_spacing=time_grid["spacing"],
        time_points=time_grid["points"],
        chunk_points=time_grid["chunk_points"],
    )
    configuration.validate()
    if configuration.state_count != mesh["state_count"]:
        raise ValueError("manual-review mesh state count is inconsistent")
    return configuration


def formal_theta_control(formal: dict[str, Any], theta: float) -> dict[str, Any]:
    matches = [control for control in formal["controls"] if control["theta"] == theta]
    if len(matches) != 1:
        raise ValueError("formal result must contain exactly one reviewed control")
    return matches[0]


def common_time_differences(
    dense_curves: dict[str, np.ndarray], formal_curves: dict[str, list[float]]
) -> dict[str, float]:
    dense_times = dense_curves["time"]
    formal_times = np.asarray(formal_curves["time"], dtype=float)
    selected = formal_times <= float(dense_times[-1]) + 1.0e-14
    common_times = formal_times[selected]
    dense_indices = np.rint(common_times / 0.05).astype(int)
    if not np.array_equal(dense_times[dense_indices], common_times):
        raise RuntimeError("dense and formal common times do not align exactly")
    return {
        name: float(
            np.max(
                np.abs(
                    dense_curves[name][dense_indices]
                    - np.asarray(formal_curves[name], dtype=float)[selected]
                )
            )
        )
        for name in ("f", "f_t", "f_tt", "f_ttt", "survival")
    }


def run() -> dict[str, Any]:
    require_repository_venv()
    manifest = load_json(MANIFEST)
    formal = load_json(FORMAL_RESULT)
    trigger = manifest["trigger"]
    observed_formal_sha = sha256(FORMAL_RESULT)
    if observed_formal_sha != trigger["formal_result_sha256"]:
        raise ValueError("formal result hash differs from the frozen manual-review trigger")
    if formal["provenance"]["discovery_code_sha256"] != trigger["formal_runner_sha256"]:
        raise ValueError("formal runner hash differs from the frozen manual-review trigger")
    if formal["line_candidate_analysis"]["topology_transition_manual_review_required"] is not True:
        raise ValueError("formal result no longer contains the manual-review trigger")

    configuration = configuration_from_manifest(manifest)
    theta = manifest["control"]["theta"]
    weights = np.asarray(manifest["control"]["weights"], dtype=float)
    expected_weights = (
        1.0 - theta
    ) * discovery.smoke.LOWER_WEIGHTS + theta * discovery.smoke.UPPER_WEIGHTS
    if not np.allclose(weights, expected_weights, rtol=0.0, atol=1.0e-15):
        raise ValueError("manual-review weights disagree with the frozen control line")
    model = discovery._assemble_model(configuration, theta)
    model_diagnostics = discovery._model_diagnostics(model)
    curves, chunk_diagnostics = discovery.evaluate_observables_chunked(
        model,
        configuration.times(),
        chunk_points=configuration.chunk_points,
    )
    rules = manifest["candidate_rules_reused_without_change"]
    analysis = discovery.analyze_control_curves(
        curves,
        dimensionless_extremum_height_max=rules["dimensionless_extremum_height_max"],
        minimum_analysis_time=rules["minimum_analysis_time"],
        relative_density_floor=rules["relative_density_floor"],
    )
    formal_control = formal_theta_control(formal, theta)
    differences = common_time_differences(curves, formal_control["curves"])

    classification = manifest["classification_rules"]
    roots = analysis["f_t_root_brackets"]
    extrema = analysis["f_tt_extrema"]
    extra_extrema = extrema[2:]
    comparison_limit = manifest["comparison_to_formal_curve"][
        "maximum_absolute_difference_per_observable"
    ]
    checks = {
        "formal_common_time_reproduction": all(
            value <= comparison_limit for value in differences.values()
        ),
        "one_retained_f_t_root": len(roots) == classification["required_retained_f_t_root_count"],
        "retained_root_is_maximum_of_f": len(roots) == 1
        and roots[0]["sampled_topology"] == classification["required_retained_root_topology"],
        "zero_near_zero_extrema": analysis["near_zero_extremum_count"]
        == classification["required_near_zero_extremum_count"],
        "extra_extrema_present": len(extra_extrema) >= 2,
        "extra_extrema_strictly_negative": bool(extra_extrema)
        and all(row["interpolated_f_t"] < 0.0 for row in extra_extrema),
        "extra_extrema_negative_margin": bool(extra_extrema)
        and all(
            row["interpolated_f_t"] <= -classification["minimum_absolute_negative_margin"]
            for row in extra_extrema
        ),
        "all_foundation_gates_true": all(model_diagnostics["gates"].values()),
        "full_state_history_not_stored": chunk_diagnostics["full_state_history_stored"] is False,
    }
    passed = all(checks.values())
    result = {
        "schema_version": 1,
        "stage": manifest["stage"],
        "status": "PASS_NEGATIVE_DERIVATIVE_WIGGLE_NOT_FOLD_AT_REVIEWED_CONTROL"
        if passed
        else "FAIL_MANUAL_REVIEW_UNRESOLVED",
        "claim_scope": manifest["claim_scope"],
        "evidence_timing": "POST_RESULT_DIAGNOSTIC_NOT_PREDECLARED_DISCOVERY_EVIDENCE",
        "continuum_verified": False,
        "project_gate_passed": False,
        "original_frozen_line_empty_action_authorized": False,
        "next_action": "freeze_new_prospective_G1c_protocol_or_stop_this_physical_family",
        "provenance": {
            "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "script": str(HERE.relative_to(REPORT)),
            "script_sha256": sha256(HERE),
            "manifest": str(MANIFEST.relative_to(REPORT)),
            "manifest_sha256": sha256(MANIFEST),
            "formal_result": str(FORMAL_RESULT.relative_to(REPORT)),
            "formal_result_sha256": observed_formal_sha,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "python_executable": sys.executable,
        },
        "configuration": configuration.to_dict(),
        "theta": theta,
        "weights": weights.tolist(),
        "checks": checks,
        "common_time_maximum_absolute_differences": differences,
        "candidate_analysis": analysis,
        "chunk_diagnostics": chunk_diagnostics,
        "reviewed_extrema": extrema,
        "minimum_extra_extremum_negative_margin": (
            float(min(-row["interpolated_f_t"] for row in extra_extrema)) if extra_extrema else None
        ),
        "curves": discovery._curves_to_json(curves),
        "limitations": [
            "single reviewed control on the discovery mesh",
            "result-informed diagnostic rather than preregistered discovery evidence",
            "does not resolve the unmatched-extremum condition of the frozen line protocol",
            "does not verify a continuum fold or cusp",
        ],
    }
    return result


def main() -> None:
    result = run()
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    temporary.replace(OUTPUT)
    print(json.dumps({key: result[key] for key in ("status", "next_action")}, indent=2))
    if not result["status"].startswith("PASS_"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
