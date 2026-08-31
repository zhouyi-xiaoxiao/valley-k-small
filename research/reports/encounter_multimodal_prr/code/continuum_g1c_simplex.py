#!/usr/bin/env python3
"""Prospective G1c full-simplex discovery for the fixed encounter family.

G1c is result-informed by G1b, but frozen before any G1c control value is
computed.  It screens the complete 0.1 three-weight simplex.  Any returned
flag is only a seed for a separately frozen confirmation segment; this module
never verifies a continuum fold or passes the project gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

import continuum_g1_discovery as discovery
import numpy as np
import scipy
from scipy import sparse

smoke = discovery.smoke

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
DEFAULT_MANIFEST = DATA / "continuum_g1c_simplex_manifest.json"
DEFAULT_OUTPUT = DATA / "continuum_g1c_simplex_result.json"
DEFAULT_CHECKPOINT_DIR = DATA / "continuum_g1c_simplex_checkpoints"

STAGE = "G1c_result_informed_full_simplex_discovery_not_confirmation"
CLAIM_SCOPE = (
    "Result-informed sequential full-simplex grid discovery in one fixed physical family; "
    "candidate seeds only, never continuum fold or project-gate evidence"
)
CHECKPOINT_SCHEMA_VERSION = 1
LEDGER_SCHEMA_VERSION = 1
RESULT_SCHEMA_VERSION = 1
LEDGER_FILENAME = "integrity_ledger.json"
RUN_LOCK_FILENAME = discovery.RUN_LOCK_FILENAME
STATE_NEGATIVITY_TOLERANCE = discovery.STATE_NEGATIVITY_TOLERANCE
SURVIVAL_MONOTONICITY_TOLERANCE = discovery.SURVIVAL_MONOTONICITY_TOLERANCE


EXPECTED_MANIFEST: dict[str, Any] = {
    "schema_version": 1,
    "stage": STAGE,
    "status": "FROZEN_BEFORE_G1C_RUN",
    "date_frozen": "2026-07-13",
    "claim_scope": CLAIM_SCOPE,
    "evidence_timing": "PROSPECTIVE_FOR_G1C_VALUES_AFTER_G1B_AND_MANUAL_REVIEW_RESULTS_WERE_KNOWN",
    "sequential_design_record": {
        "prior_line_outcome": (
            "G1b line contained no near-zero or adjacent-sign candidate and had an "
            "unmatched-extrema manual-review flag"
        ),
        "post_result_diagnostic_outcome": (
            "the reviewed theta=0.7 extra extrema remained strictly below f_t=0 and were not a fold"
        ),
        "old_line_empty_action_authorized": False,
        "reason_for_new_stage": (
            "freeze a new result-informed full-simplex design rather than retroactively "
            "relabel the G1b line as empty"
        ),
    },
    "pre_run_amendments": [
        (
            "An unmatched or changed topology with no eligible candidate is "
            "INCONCLUSIVE_MANUAL_REVIEW, not a failed family gate."
        ),
        (
            "Sign-edge interior eligibility is determined by the linearly interpolated "
            "crossing weight; an exact-zero endpoint uses that endpoint weight."
        ),
        (
            "Formal execution must match the externally frozen runner and protocol-note "
            "SHA-256 pins recorded in the manifest."
        ),
        (
            "A matched extremum that is exactly zero at both edge endpoints is an "
            "unresolved whole-edge-zero manual-review case, not a boundary diagnostic."
        ),
    ],
    "mesh": {
        "midpoint_cells": 65,
        "relative_parallel_cells": 65,
        "relative_perp_cells": 49,
        "state_count": 207025,
    },
    "simplex_control": {
        "component_names": ["left_patch", "middle_patch", "right_patch"],
        "integer_denominator": 10,
        "spacing": 0.1,
        "enumeration": "i=0..10, j=0..10-i, k=10-i-j, in increasing (i,j)",
        "control_count": 66,
        "constraints": ("i,j,k are nonnegative integers; weights=(i,j,k)/10; i+j+k=10"),
        "physical_retuning_allowed": False,
    },
    "time_grid": {
        "start": 0.0,
        "stop": 80.0,
        "spacing": 0.25,
        "points": 321,
        "chunk_points": 41,
    },
    "observables": ["f", "f_t", "f_tt", "f_ttt", "survival"],
    "candidate_rules": {
        "dimensionless_extremum_height_max": 0.05,
        "minimum_analysis_time": 0.5,
        "relative_density_floor": 1.0e-12,
        "time_match_tolerance": 2.0,
        "simplex_edge_l1_integer_distance": 2,
        "matched_extremum_sign_change": True,
    },
    "outcome_policy": {
        "candidate_sources": [
            "near_zero_extremum_at_strictly_interior_control",
            "matched_extremum_sign_change_at_strictly_interior_interpolated_crossing",
        ],
        "candidate_eligibility": (
            "all three weights must be strictly positive at a near-zero control or at "
            "the interpolated sign crossing; exact-zero evidence uses the zero endpoint weight"
        ),
        "boundary_flags_are_diagnostic_only": True,
        "unmatched_topology_is_candidate": False,
        "unmatched_topology_requires_manual_review": True,
        "candidate_automatically_confirms_fold": False,
        "candidate_automatically_selects_segment": False,
        "maximum_later_confirmation_segments": 1,
        "later_confirmation_requires_new_frozen_manifest": True,
        "no_candidate_no_manual_review_action": (
            "mark this fixed physical family discovery gate failed; do not retune inside G1c"
        ),
        "no_candidate_with_manual_review_action": (
            "mark G1c inconclusive and require manual review; do not promote the topology "
            "flag or retune inside G1c"
        ),
    },
    "required_inputs": {
        "g1a_foundation": {
            "artifact": "artifacts/data/continuum_g1_smoke.json",
            "artifact_sha256": ("a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3"),
            "producer_code": "code/continuum_g1_smoke.py",
            "producer_code_sha256": (
                "e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701"
            ),
            "required_status": "PASS",
            "required_stage": "G1a_pre_fold_foundations",
            "required_schema_version": 3,
            "required_gate_count": 42,
            "required_continuum_verified": False,
        },
        "g1b_formal_line": {
            "artifact": "artifacts/data/continuum_g1_discovery_result.json",
            "artifact_sha256": ("2052c1d26211661995d6048b2cd3ca909f04ce48efb9a96c32bd153c7c63d40d"),
            "producer_code": "code/continuum_g1_discovery.py",
            "producer_code_sha256": (
                "1411384398ed4e476dba15371cdfd662e94ed3a53cffdc02a1562201cfa7b52e"
            ),
            "required_status": "DISCOVERY_LINE_COMPLETE",
            "required_stage": "G1b_discovery_not_continuum_confirmation",
            "required_formal_frozen_run_completed": True,
            "required_near_zero_extremum_count": 0,
            "required_adjacent_sign_bracket_count": 0,
            "required_manual_review": True,
            "required_continuum_verified": False,
            "required_project_gate_passed": False,
        },
        "g1b_manual_review": {
            "artifact": "artifacts/data/continuum_g1_manual_review_result.json",
            "artifact_sha256": ("6f869fb4e961297a9ba4784c394fa56fbb083f1a89091aa0c27738331127de65"),
            "producer_code": "code/continuum_g1_manual_review.py",
            "producer_code_sha256": (
                "4453444abd878d771b59185aaee5371ae5d9c786fdb0da9222f25c0605035451"
            ),
            "required_status": ("PASS_NEGATIVE_DERIVATIVE_WIGGLE_NOT_FOLD_AT_REVIEWED_CONTROL"),
            "required_stage": "G1b_post_result_manual_review",
            "required_evidence_timing": (
                "POST_RESULT_DIAGNOSTIC_NOT_PREDECLARED_DISCOVERY_EVIDENCE"
            ),
            "required_original_line_empty_action_authorized": False,
            "required_continuum_verified": False,
            "required_project_gate_passed": False,
        },
    },
    "required_runtime": "repository .venv",
    "protocol_note": "notes/g1c_simplex_protocol.md",
}


def full_simplex_triplets(denominator: int = 10) -> tuple[tuple[int, int, int], ...]:
    """Return the fixed increasing-(i,j) triangular-lattice enumeration."""

    if type(denominator) is not int or denominator < 1:
        raise ValueError("simplex denominator must be a positive integer")
    return tuple(
        (i, j, denominator - i - j)
        for i in range(denominator + 1)
        for j in range(denominator - i + 1)
    )


def control_id(triplet: Sequence[int]) -> str:
    values = tuple(triplet)
    if len(values) != 3 or any(type(value) is not int or value < 0 for value in values):
        raise ValueError("control triplet must contain three nonnegative integers")
    return "w_" + "_".join(f"{value:02d}" for value in values)


@dataclass(frozen=True)
class SimplexConfiguration:
    midpoint_cells: int
    relative_parallel_cells: int
    relative_perp_cells: int
    denominator: int
    integer_triplets: tuple[tuple[int, int, int], ...]
    time_start: float
    time_stop: float
    time_spacing: float
    time_points: int
    chunk_points: int

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> SimplexConfiguration:
        mesh = manifest["mesh"]
        control = manifest["simplex_control"]
        time_grid = manifest["time_grid"]
        denominator = control["integer_denominator"]
        return cls(
            midpoint_cells=mesh["midpoint_cells"],
            relative_parallel_cells=mesh["relative_parallel_cells"],
            relative_perp_cells=mesh["relative_perp_cells"],
            denominator=denominator,
            integer_triplets=full_simplex_triplets(denominator),
            time_start=time_grid["start"],
            time_stop=time_grid["stop"],
            time_spacing=time_grid["spacing"],
            time_points=time_grid["points"],
            chunk_points=time_grid["chunk_points"],
        )

    @classmethod
    def small_full_simplex_dry_run(cls) -> SimplexConfiguration:
        """Use all 66 controls but a tiny implementation-only state/time grid."""

        return cls(
            midpoint_cells=7,
            relative_parallel_cells=9,
            relative_perp_cells=5,
            denominator=10,
            integer_triplets=full_simplex_triplets(10),
            time_start=0.0,
            time_stop=1.0,
            time_spacing=0.25,
            time_points=5,
            chunk_points=3,
        )

    @property
    def state_count(self) -> int:
        return self.midpoint_cells * self.relative_parallel_cells * self.relative_perp_cells

    def times(self) -> np.ndarray:
        return self.time_start + self.time_spacing * np.arange(self.time_points, dtype=float)

    def weights(self, triplet: tuple[int, int, int]) -> np.ndarray:
        self.validate_triplet(triplet)
        return np.asarray(triplet, dtype=float) / float(self.denominator)

    def validate_triplet(self, triplet: tuple[int, int, int]) -> None:
        if (
            type(triplet) is not tuple
            or len(triplet) != 3
            or any(type(value) is not int or value < 0 for value in triplet)
            or sum(triplet) != self.denominator
        ):
            raise ValueError("invalid integer simplex triplet")

    def validate(self) -> None:
        cells = (
            self.midpoint_cells,
            self.relative_parallel_cells,
            self.relative_perp_cells,
        )
        if any(type(value) is not int or value < 3 for value in cells):
            raise ValueError("all mesh cell counts must be integers of at least three")
        if type(self.denominator) is not int or self.denominator < 1:
            raise ValueError("simplex denominator must be a positive integer")
        if not self.integer_triplets:
            raise ValueError("simplex control set must not be empty")
        for triplet in self.integer_triplets:
            self.validate_triplet(triplet)
        if len(set(self.integer_triplets)) != len(self.integer_triplets):
            raise ValueError("simplex controls must be unique")
        if type(self.time_points) is not int or self.time_points < 2:
            raise ValueError("time_points must be an integer of at least two")
        if type(self.chunk_points) is not int or not 2 <= self.chunk_points <= self.time_points:
            raise ValueError("chunk_points must lie between two and time_points")
        if (
            type(self.time_start) is not float
            or type(self.time_stop) is not float
            or type(self.time_spacing) is not float
            or not np.isfinite((self.time_start, self.time_stop, self.time_spacing)).all()
            or self.time_start < 0.0
            or self.time_spacing <= 0.0
            or self.time_stop <= self.time_start
        ):
            raise ValueError("invalid finite time grid")
        expected_stop = self.time_start + (self.time_points - 1) * self.time_spacing
        if not math.isclose(expected_stop, self.time_stop, rel_tol=0.0, abs_tol=1.0e-12):
            raise ValueError("time grid fields are inconsistent")

    def to_dict(self) -> dict[str, Any]:
        return {
            "mesh": {
                "midpoint_cells": self.midpoint_cells,
                "relative_parallel_cells": self.relative_parallel_cells,
                "relative_perp_cells": self.relative_perp_cells,
                "state_count": self.state_count,
            },
            "simplex": {
                "integer_denominator": self.denominator,
                "control_count": len(self.integer_triplets),
                "integer_triplets": [list(triplet) for triplet in self.integer_triplets],
            },
            "time_grid": {
                "start": self.time_start,
                "stop": self.time_stop,
                "spacing": self.time_spacing,
                "points": self.time_points,
                "chunk_points": self.chunk_points,
            },
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )
    return hashlib.sha256(payload).hexdigest()


def load_and_validate_manifest(path: Path = DEFAULT_MANIFEST) -> tuple[dict[str, Any], str]:
    manifest_path = Path(path)
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise FileNotFoundError(f"G1c manifest is missing or not a regular file: {manifest_path}")
    payload = discovery._load_json_strict(manifest_path, label="G1c manifest")
    if type(payload) is not dict:
        raise ValueError("G1c manifest must be a JSON object")
    protocol_body = dict(payload)
    frozen_implementation = protocol_body.pop("frozen_implementation", None)
    if not discovery._strict_json_equal(protocol_body, EXPECTED_MANIFEST):
        raise ValueError("G1c manifest does not exactly match the prospective frozen protocol")
    if type(frozen_implementation) is not dict or set(frozen_implementation) != {
        "runner",
        "runner_sha256",
        "protocol_note",
        "protocol_note_sha256",
    }:
        raise ValueError("G1c frozen implementation pins do not match the required schema")
    runner, runner_display = _safe_report_file(
        frozen_implementation["runner"], label="G1c frozen runner"
    )
    protocol, protocol_display = _safe_report_file(
        frozen_implementation["protocol_note"], label="G1c frozen protocol note"
    )
    if runner != HERE or runner_display != "code/continuum_g1c_simplex.py":
        raise ValueError("G1c frozen runner pin does not identify this runner")
    if protocol_display != payload["protocol_note"]:
        raise ValueError("G1c frozen protocol pin disagrees with protocol_note")
    expected_runner_hash = _validate_hash(
        frozen_implementation["runner_sha256"], label="G1c frozen runner pin"
    )
    expected_protocol_hash = _validate_hash(
        frozen_implementation["protocol_note_sha256"], label="G1c frozen protocol pin"
    )
    if _sha256(runner) != expected_runner_hash:
        raise ValueError("G1c frozen runner SHA-256 mismatch")
    if _sha256(protocol) != expected_protocol_hash:
        raise ValueError("G1c frozen protocol-note SHA-256 mismatch")
    configuration = SimplexConfiguration.from_manifest(payload)
    configuration.validate()
    expected_count = (configuration.denominator + 1) * (configuration.denominator + 2) // 2
    if (
        len(configuration.integer_triplets) != payload["simplex_control"]["control_count"]
        or len(configuration.integer_triplets) != expected_count
        or not math.isclose(
            payload["simplex_control"]["spacing"],
            1.0 / configuration.denominator,
            rel_tol=0.0,
            abs_tol=0.0,
        )
        or configuration.state_count != payload["mesh"]["state_count"]
    ):
        raise ValueError("G1c simplex count, spacing, or mesh state count is inconsistent")
    return payload, _sha256(manifest_path)


def _safe_report_file(relative: str, *, label: str) -> tuple[Path, str]:
    if type(relative) is not str or not relative:
        raise ValueError(f"{label} path must be a nonempty string")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"{label} path must remain relative to the report")
    root = REPORT.resolve()
    path = (root / candidate).resolve()
    try:
        display = str(path.relative_to(root))
    except ValueError as error:
        raise ValueError(f"{label} path escapes the report") from error
    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError(f"{label} is missing or not a regular file: {path}")
    return path, display


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def validate_execution_paths(
    *,
    manifest: dict[str, Any],
    manifest_path: Path,
    output_path: Path,
    checkpoint_dir: Path,
) -> None:
    """Reject output/checkpoint aliases before the first writable action."""

    output = Path(output_path)
    checkpoints = Path(checkpoint_dir)
    if output.is_symlink():
        raise ValueError("G1c output path must not be a symlink")
    if output.exists() and not output.is_file():
        raise ValueError("G1c output path must be absent or a regular file")
    if checkpoints.is_symlink():
        raise ValueError("G1c checkpoint directory must not be a symlink")
    if checkpoints.exists() and not checkpoints.is_dir():
        raise ValueError("G1c checkpoint path must be absent or a directory")

    output_resolved = output.resolve()
    checkpoint_resolved = checkpoints.resolve()
    protected = {Path(manifest_path).resolve(), HERE}
    protocol, _ = _safe_report_file(manifest["protocol_note"], label="G1c protocol note")
    protected.add(protocol)
    for requirement in manifest["required_inputs"].values():
        for field, label in (("artifact", "artifact"), ("producer_code", "producer")):
            path, _ = _safe_report_file(requirement[field], label=f"G1c protected {label}")
            protected.add(path)

    if output_resolved in protected:
        raise ValueError("G1c output path aliases a manifest, runner, protocol, or pinned input")
    if _is_within(output_resolved, checkpoint_resolved):
        raise ValueError("G1c output path must remain outside the checkpoint namespace")
    if any(_is_within(path, checkpoint_resolved) for path in protected):
        raise ValueError("G1c checkpoint namespace must not contain protected inputs")

    lock_path = checkpoints / RUN_LOCK_FILENAME
    if lock_path.is_symlink():
        raise ValueError("G1c run-lock path must not be a symlink")


def _validate_hash(value: Any, *, label: str) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} must be one lowercase SHA-256 digest")
    return value


def validate_required_inputs(requirements: dict[str, Any]) -> dict[str, Any]:
    """Validate pinned G1a, G1b, and post-result diagnostic artifacts."""

    if type(requirements) is not dict or set(requirements) != {
        "g1a_foundation",
        "g1b_formal_line",
        "g1b_manual_review",
    }:
        raise ValueError("required input names do not match the frozen G1c schema")

    validated: dict[str, Any] = {}
    loaded: dict[str, dict[str, Any]] = {}
    for name, requirement in requirements.items():
        if type(requirement) is not dict:
            raise ValueError(f"{name} requirement must be an object")
        artifact, artifact_display = _safe_report_file(
            requirement.get("artifact"), label=f"{name} artifact"
        )
        producer, producer_display = _safe_report_file(
            requirement.get("producer_code"), label=f"{name} producer"
        )
        expected_artifact_hash = _validate_hash(
            requirement.get("artifact_sha256"), label=f"{name} artifact pin"
        )
        expected_producer_hash = _validate_hash(
            requirement.get("producer_code_sha256"), label=f"{name} producer pin"
        )
        observed_artifact_hash = _sha256(artifact)
        observed_producer_hash = _sha256(producer)
        if observed_artifact_hash != expected_artifact_hash:
            raise ValueError(f"{name} artifact SHA-256 mismatch")
        if observed_producer_hash != expected_producer_hash:
            raise ValueError(f"{name} producer SHA-256 mismatch")
        payload = discovery._load_json_strict(artifact, label=f"{name} artifact")
        loaded[name] = payload
        validated[name] = {
            "validation_status": "PASS",
            "artifact": artifact_display,
            "artifact_sha256": observed_artifact_hash,
            "producer_code": producer_display,
            "producer_code_sha256": observed_producer_hash,
        }

    g1a_req = requirements["g1a_foundation"]
    g1a = loaded["g1a_foundation"]
    g1a_expected = {
        "schema_version": g1a_req["required_schema_version"],
        "stage": g1a_req["required_stage"],
        "status": g1a_req["required_status"],
        "continuum_verified": g1a_req["required_continuum_verified"],
    }
    for field, expected in g1a_expected.items():
        if type(g1a.get(field)) is not type(expected) or g1a.get(field) != expected:
            raise ValueError(f"G1a artifact field {field} disagrees with its G1c pin")
    g1a_gates = g1a.get("gates")
    if (
        type(g1a_gates) is not dict
        or len(g1a_gates) != g1a_req["required_gate_count"]
        or any(type(value) is not bool or value is not True for value in g1a_gates.values())
    ):
        raise ValueError("G1a artifact does not contain the pinned all-true gate set")
    if Path(smoke.__file__).resolve() != (REPORT / g1a_req["producer_code"]).resolve():
        raise ValueError("imported G1a model code is not the pinned producer")
    validated["g1a_foundation"]["gate_count"] = len(g1a_gates)

    g1b_req = requirements["g1b_formal_line"]
    g1b = loaded["g1b_formal_line"]
    exact_g1b_fields = {
        "stage": g1b_req["required_stage"],
        "status": g1b_req["required_status"],
        "formal_frozen_run_completed": g1b_req["required_formal_frozen_run_completed"],
        "continuum_verified": g1b_req["required_continuum_verified"],
        "project_gate_passed": g1b_req["required_project_gate_passed"],
    }
    for field, expected in exact_g1b_fields.items():
        if type(g1b.get(field)) is not type(expected) or g1b.get(field) != expected:
            raise ValueError(f"G1b artifact field {field} disagrees with its G1c pin")
    line = g1b.get("line_candidate_analysis")
    if type(line) is not dict:
        raise ValueError("G1b artifact lacks line candidate analysis")
    line_expected = {
        "near_zero_extremum_count": g1b_req["required_near_zero_extremum_count"],
        "adjacent_theta_sign_bracket_count": g1b_req["required_adjacent_sign_bracket_count"],
        "topology_transition_manual_review_required": g1b_req["required_manual_review"],
    }
    for field, expected in line_expected.items():
        if type(line.get(field)) is not type(expected) or line.get(field) != expected:
            raise ValueError(f"G1b line field {field} disagrees with its G1c pin")
    provenance = g1b.get("provenance")
    if (
        type(provenance) is not dict
        or provenance.get("discovery_code_sha256") != g1b_req["producer_code_sha256"]
        or Path(discovery.__file__).resolve() != (REPORT / g1b_req["producer_code"]).resolve()
    ):
        raise ValueError("imported G1b analysis code is not the pinned producer")

    review_req = requirements["g1b_manual_review"]
    review = loaded["g1b_manual_review"]
    exact_review_fields = {
        "stage": review_req["required_stage"],
        "status": review_req["required_status"],
        "evidence_timing": review_req["required_evidence_timing"],
        "original_frozen_line_empty_action_authorized": review_req[
            "required_original_line_empty_action_authorized"
        ],
        "continuum_verified": review_req["required_continuum_verified"],
        "project_gate_passed": review_req["required_project_gate_passed"],
    }
    for field, expected in exact_review_fields.items():
        if type(review.get(field)) is not type(expected) or review.get(field) != expected:
            raise ValueError(f"manual-review field {field} disagrees with its G1c pin")
    review_provenance = review.get("provenance")
    if (
        type(review_provenance) is not dict
        or review_provenance.get("script_sha256") != review_req["producer_code_sha256"]
        or review_provenance.get("formal_result_sha256") != g1b_req["artifact_sha256"]
    ):
        raise ValueError("manual-review producer or formal-result linkage is invalid")
    return validated


def _repository_venv_status() -> tuple[Path, bool]:
    repository_venv = (REPOSITORY / ".venv").resolve()
    active = (
        repository_venv.exists()
        and Path(sys.prefix).resolve() == repository_venv
        and sys.prefix != sys.base_prefix
    )
    return repository_venv, active


def _provenance(
    manifest_path: Path,
    manifest_sha256: str,
    input_preflight: dict[str, Any],
) -> dict[str, Any]:
    protocol = REPORT / EXPECTED_MANIFEST["protocol_note"]
    repository_venv, active = _repository_venv_status()
    try:
        manifest_display = str(manifest_path.resolve().relative_to(REPORT.resolve()))
    except ValueError:
        manifest_display = str(manifest_path.resolve())
    return {
        "manifest": manifest_display,
        "manifest_sha256": manifest_sha256,
        "g1c_code": str(HERE.relative_to(REPORT)),
        "g1c_code_sha256": _sha256(HERE),
        "protocol_note": str(protocol.relative_to(REPORT)),
        "protocol_note_sha256": _sha256(protocol),
        "pinned_input_preflight": input_preflight,
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "python_prefix": sys.prefix,
        "python_base_prefix": sys.base_prefix,
        "repository_venv": str(repository_venv),
        "running_in_repository_venv": active,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
    }


def _configuration_hash(configuration: SimplexConfiguration, run_mode: str) -> str:
    return _json_sha256({"run_mode": run_mode, "configuration": configuration.to_dict()})


def _grid(configuration: SimplexConfiguration) -> smoke.QuotientGrid2D:
    parameters = smoke.PilotParameters()
    return smoke.QuotientGrid2D(
        midpoint_cells=configuration.midpoint_cells,
        relative_parallel_cells=configuration.relative_parallel_cells,
        relative_perp_cells=configuration.relative_perp_cells,
        midpoint_bounds=parameters.midpoint_bounds,
        relative_parallel_bounds=parameters.relative_parallel_bounds,
        transverse_width=parameters.transverse_width,
    )


@lru_cache(maxsize=4)
def _shared_baseline(configuration: SimplexConfiguration) -> smoke.QuotientModel:
    """Build one genuine theta-line endpoint only as the shared G1a baseline."""

    configuration.validate()
    return smoke.build_model(_grid(configuration), theta=0.0, parameters=smoke.PilotParameters())


@lru_cache(maxsize=4)
def shared_foundation_baseline(configuration: SimplexConfiguration) -> dict[str, Any]:
    """Validate the unchanged G1a structure before arbitrary control assembly.

    The legacy foundation gates are called only on their genuine theta=0
    endpoint.  They are never called on an arbitrary simplex-weight model.
    """

    baseline = _shared_baseline(configuration)
    diagnostics = smoke.foundation_diagnostics(baseline)
    gates = smoke.foundation_gates(baseline, diagnostics)
    if not all(gates.values()):
        failed = sorted(name for name, passed in gates.items() if not passed)
        raise RuntimeError(f"shared G1a structural baseline failed: {failed}")
    return {
        "scope": "unchanged transport, grid, geometry, patches, initial law, and endpoint baseline",
        "legacy_theta_endpoint": 0.0,
        "gate_count": len(gates),
        "gates": gates,
        "diagnostics": diagnostics,
    }


def _sparse_max_abs(matrix: sparse.spmatrix) -> float:
    values = matrix.tocsr().data
    return float(np.max(np.abs(values))) if values.size else 0.0


def assemble_arbitrary_weight_model(
    configuration: SimplexConfiguration,
    triplet: tuple[int, int, int],
) -> smoke.QuotientModel:
    """Assemble a control directly from three weights, never from old theta."""

    configuration.validate_triplet(triplet)
    weights = configuration.weights(triplet)
    baseline = _shared_baseline(configuration)
    parameters = baseline.parameters
    budget_density = parameters.installed_budget / parameters.transverse_width
    kappa = budget_density * (weights @ baseline.patch_cell_averages)
    killing = np.kron(kappa, baseline.contact_fraction_relative)
    killed = baseline.free_generator - sparse.diags(killing, format="csr")
    physical_budget = float(
        parameters.transverse_width * np.sum(kappa) * baseline.grid.midpoint_spacing
    )
    killed_balance = float(np.max(np.abs(np.asarray(killed.sum(axis=1)).reshape(-1) + killing)))
    # theta and its derivative are explicit inert implementation sentinels.
    # Neither is used to identify or assemble this arbitrary control.
    return replace(
        baseline,
        theta=0.0,
        killed_generator=killed,
        killing=killing,
        killing_derivative=np.zeros_like(killing),
        kappa=kappa,
        kappa_derivative=np.zeros_like(kappa),
        physical_budget=physical_budget,
        killed_mass_balance_error=killed_balance,
    )


def arbitrary_weight_model_diagnostics(
    configuration: SimplexConfiguration,
    triplet: tuple[int, int, int],
    model: smoke.QuotientModel,
) -> dict[str, Any]:
    """Independent control gates that do not read theta-line current_weights."""

    configuration.validate_triplet(triplet)
    weights = configuration.weights(triplet)
    parameters = model.parameters
    spacing = model.grid.midpoint_spacing
    expected_kappa = (
        parameters.installed_budget
        / parameters.transverse_width
        * (weights @ model.patch_cell_averages)
    )
    expected_killing = np.kron(expected_kappa, model.contact_fraction_relative)
    expected_killed = model.free_generator - sparse.diags(expected_killing, format="csr")
    free_row_error = float(np.max(np.abs(np.asarray(model.free_generator.sum(axis=1)).reshape(-1))))
    killed_balance_error = float(
        np.max(np.abs(np.asarray(model.killed_generator.sum(axis=1)).reshape(-1) + model.killing))
    )
    physical_budget = float(parameters.transverse_width * np.sum(model.kappa) * spacing)
    patch_integrals = np.sum(model.patch_cell_averages, axis=1) * spacing
    free_offdiagonal = model.free_generator - sparse.diags(
        model.free_generator.diagonal(), format="csr"
    )
    killed_offdiagonal = model.killed_generator - sparse.diags(
        model.killed_generator.diagonal(), format="csr"
    )
    generator_actions = [np.asarray(model.killing, dtype=float)]
    for _ in range(4):
        generator_actions.append(
            np.asarray(model.killed_generator @ generator_actions[-1], dtype=float)
        )
    diagnostics = {
        "integer_triplet": list(triplet),
        "weights": weights.tolist(),
        "weight_sum_error": float(abs(np.sum(weights) - 1.0)),
        "minimum_weight": float(np.min(weights)),
        "physical_budget": physical_budget,
        "physical_budget_relative_error": float(
            abs(physical_budget - parameters.installed_budget) / parameters.installed_budget
        ),
        "patch_integrals": [float(value) for value in patch_integrals],
        "maximum_patch_integral_error": float(np.max(np.abs(patch_integrals - 1.0))),
        "minimum_kappa": float(np.min(model.kappa)),
        "minimum_killing": float(np.min(model.killing)),
        "kappa_reconstruction_max_abs_error": float(np.max(np.abs(model.kappa - expected_kappa))),
        "tensor_killing_max_abs_error": float(np.max(np.abs(model.killing - expected_killing))),
        "killed_generator_reconstruction_max_abs_error": _sparse_max_abs(
            model.killed_generator - expected_killed
        ),
        "free_generator_row_error": free_row_error,
        "killed_mass_balance_error": killed_balance_error,
        "free_offdiagonal_minimum": (
            float(np.min(free_offdiagonal.data)) if free_offdiagonal.nnz else 0.0
        ),
        "killed_offdiagonal_minimum": (
            float(np.min(killed_offdiagonal.data)) if killed_offdiagonal.nnz else 0.0
        ),
        "initial_mass_error": float(abs(np.sum(model.initial) - 1.0)),
        "initial_contact_mass": float(model.initial_contact_mass),
        "generator_actions_finite": all(
            bool(np.all(np.isfinite(action))) for action in generator_actions
        ),
        "generator_action_max_abs": [float(np.max(np.abs(action))) for action in generator_actions],
        "legacy_theta_field_role": "inert_zero_sentinel_not_control_coordinate",
    }
    gates = {
        "triplet_exact_integer_simplex": (
            all(type(value) is int and value >= 0 for value in triplet)
            and sum(triplet) == configuration.denominator
        ),
        "weight_sum_unit": diagnostics["weight_sum_error"] <= 1.0e-15,
        "weights_nonnegative": diagnostics["minimum_weight"] >= 0.0,
        "patch_integrals_unit": diagnostics["maximum_patch_integral_error"] <= 1.0e-10,
        "physical_budget_fixed": diagnostics["physical_budget_relative_error"] <= 1.0e-10,
        "kappa_nonnegative": diagnostics["minimum_kappa"] >= -1.0e-14,
        "killing_nonnegative": diagnostics["minimum_killing"] >= -1.0e-14,
        "kappa_reconstructed_from_arbitrary_weights": diagnostics[
            "kappa_reconstruction_max_abs_error"
        ]
        <= 1.0e-14,
        "tensor_killing_reconstructed": diagnostics["tensor_killing_max_abs_error"] <= 1.0e-14,
        "killed_generator_reconstructed": diagnostics[
            "killed_generator_reconstruction_max_abs_error"
        ]
        <= 1.0e-14,
        "free_generator_row_sums": diagnostics["free_generator_row_error"] <= 1.0e-12,
        "killed_mass_balance": diagnostics["killed_mass_balance_error"] <= 1.0e-12,
        "free_offdiagonal_nonnegative": diagnostics["free_offdiagonal_minimum"] >= -1.0e-14,
        "killed_offdiagonal_nonnegative": diagnostics["killed_offdiagonal_minimum"] >= -1.0e-14,
        "initial_mass_unit": diagnostics["initial_mass_error"] <= 1.0e-12,
        "initial_contact_safe": diagnostics["initial_contact_mass"] == 0.0,
        "generator_actions_finite": diagnostics["generator_actions_finite"],
    }
    if not all(gates.values()):
        failed = sorted(name for name, passed in gates.items() if not passed)
        raise RuntimeError(f"arbitrary-weight model gates failed: {failed}")
    return {
        "gate_scope": (
            "arbitrary weights, fixed installed budget, tensor killing, generator, "
            "initial law, and generator-action jets"
        ),
        "gates": gates,
        "diagnostics": diagnostics,
    }


def _control_is_strictly_interior(triplet: Sequence[int]) -> bool:
    return all(int(value) > 0 for value in triplet)


def simplex_edges(controls: Sequence[dict[str, Any]], *, l1_distance: int) -> list[tuple[int, int]]:
    if type(l1_distance) is not int or l1_distance != 2:
        raise ValueError("G1c simplex adjacency requires integer L1 distance exactly two")
    triplets: list[tuple[int, int, int]] = []
    for control in controls:
        raw = control["integer_triplet"]
        if type(raw) is not list or len(raw) != 3 or any(type(value) is not int for value in raw):
            raise ValueError("control integer_triplet has the wrong JSON form")
        triplets.append(tuple(raw))
    if len(set(triplets)) != len(triplets):
        raise ValueError("simplex controls contain duplicate triplets")
    return [
        (left, right)
        for left in range(len(triplets))
        for right in range(left + 1, len(triplets))
        if sum(abs(a - b) for a, b in zip(triplets[left], triplets[right], strict=True))
        == l1_distance
    ]


def _topology_summary(analysis: dict[str, Any]) -> dict[str, Any]:
    return discovery._control_topology_transition_summary(analysis)


def analyze_simplex(
    controls: Sequence[dict[str, Any]],
    *,
    time_match_tolerance: float,
    simplex_edge_l1_integer_distance: int,
    matched_extremum_sign_change: bool,
) -> dict[str, Any]:
    """Analyze only true triangular-lattice edges; never create an umbrella candidate."""

    tolerance = float(time_match_tolerance)
    if not np.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("time_match_tolerance must be finite and positive")
    if type(matched_extremum_sign_change) is not bool:
        raise ValueError("matched_extremum_sign_change must be boolean")
    if not controls:
        raise ValueError("at least one simplex control is required")
    indices = [control["control_index"] for control in controls]
    if any(type(index) is not int for index in indices) or indices != list(range(len(controls))):
        raise ValueError("simplex controls must have consecutive ordered indices")
    edges = simplex_edges(
        controls,
        l1_distance=simplex_edge_l1_integer_distance,
    )

    interior_near_zero: list[dict[str, Any]] = []
    boundary_near_zero: list[dict[str, Any]] = []
    for control in controls:
        triplet = control["integer_triplet"]
        interior = _control_is_strictly_interior(triplet)
        for extremum in control["candidate_analysis"]["f_tt_extrema"]:
            if extremum["near_zero_candidate"]:
                row = {
                    "control_index": control["control_index"],
                    "control_id": control["control_id"],
                    "integer_triplet": triplet,
                    "weights": control["weights"],
                    "strictly_interior_control": interior,
                    **extremum,
                }
                (interior_near_zero if interior else boundary_near_zero).append(row)

    interior_sign_edges: list[dict[str, Any]] = []
    boundary_sign_edges: list[dict[str, Any]] = []
    unresolved_whole_edge_zero_rows: list[dict[str, Any]] = []
    matched_rows: list[dict[str, Any]] = []
    topology_review_rows: list[dict[str, Any]] = []
    for left_index, right_index in edges:
        left_control = controls[left_index]
        right_control = controls[right_index]
        left_analysis = left_control["candidate_analysis"]
        right_analysis = right_control["candidate_analysis"]
        left_extrema = left_analysis["f_tt_extrema"]
        right_extrema = right_analysis["f_tt_extrema"]
        assignment = discovery._order_preserving_extremum_matching(
            left_extrema,
            right_extrema,
            tolerance=tolerance,
        )
        left_triplet = left_control["integer_triplet"]
        right_triplet = right_control["integer_triplet"]
        interior_interior = bool(
            _control_is_strictly_interior(left_triplet)
            and _control_is_strictly_interior(right_triplet)
        )
        edge_has_double_zero_match = False
        for left_extremum_index, right_extremum_index in assignment["pairs"]:
            left_extremum = left_extrema[left_extremum_index]
            right_extremum = right_extrema[right_extremum_index]
            left_height = float(left_extremum["interpolated_f_t"])
            right_height = float(right_extremum["interpolated_f_t"])
            strict_opposite = bool(
                left_height != 0.0
                and right_height != 0.0
                and np.signbit(left_height) != np.signbit(right_height)
            )
            exact_zero_endpoints = []
            if left_height == 0.0:
                exact_zero_endpoints.append(left_control["control_id"])
            if right_height == 0.0:
                exact_zero_endpoints.append(right_control["control_id"])
            edge_has_double_zero_match = bool(
                edge_has_double_zero_match or len(exact_zero_endpoints) == 2
            )
            sign_evidence = bool(
                matched_extremum_sign_change and (strict_opposite or len(exact_zero_endpoints) == 1)
            )
            crossing_fraction: float | None
            crossing_kind: str
            if strict_opposite:
                crossing_fraction = float(-left_height / (right_height - left_height))
                crossing_kind = "linear_strict_sign_crossing"
            elif left_height == 0.0 and right_height != 0.0:
                crossing_fraction = 0.0
                crossing_kind = "exact_zero_left_endpoint"
            elif right_height == 0.0 and left_height != 0.0:
                crossing_fraction = 1.0
                crossing_kind = "exact_zero_right_endpoint"
            elif left_height == 0.0 and right_height == 0.0:
                crossing_fraction = None
                crossing_kind = "whole_edge_sampled_zero_manual_review"
            else:
                crossing_fraction = None
                crossing_kind = "no_sign_crossing"
            crossing_weights = (
                None
                if crossing_fraction is None
                else (
                    (1.0 - crossing_fraction) * np.asarray(left_control["weights"], dtype=float)
                    + crossing_fraction * np.asarray(right_control["weights"], dtype=float)
                ).tolist()
            )
            crossing_strictly_interior = bool(
                crossing_weights is not None and all(value > 0.0 for value in crossing_weights)
            )
            row = {
                "left_control_index": left_index,
                "right_control_index": right_index,
                "left_control_id": left_control["control_id"],
                "right_control_id": right_control["control_id"],
                "left_integer_triplet": left_triplet,
                "right_integer_triplet": right_triplet,
                "left_weights": left_control["weights"],
                "right_weights": right_control["weights"],
                "integer_l1_distance": simplex_edge_l1_integer_distance,
                "interior_interior_edge": interior_interior,
                "left_extremum_index": left_extremum_index,
                "right_extremum_index": right_extremum_index,
                "extremum_kind": left_extremum["extremum_kind"],
                "left_time": left_extremum["linear_extremum_time"],
                "right_time": right_extremum["linear_extremum_time"],
                "time_separation": abs(
                    float(left_extremum["linear_extremum_time"])
                    - float(right_extremum["linear_extremum_time"])
                ),
                "left_interpolated_f_t": left_height,
                "right_interpolated_f_t": right_height,
                "strict_opposite_sign": strict_opposite,
                "exact_zero_endpoints": exact_zero_endpoints,
                "matched_sign_evidence": sign_evidence,
                "crossing_kind": crossing_kind,
                "linear_crossing_fraction_from_left": crossing_fraction,
                "interpolated_crossing_weights": crossing_weights,
                "crossing_strictly_interior": crossing_strictly_interior,
                "eligible_candidate_seed": bool(sign_evidence and crossing_strictly_interior),
            }
            matched_rows.append(row)
            if len(exact_zero_endpoints) == 2:
                unresolved_whole_edge_zero_rows.append(row)
            elif sign_evidence:
                (interior_sign_edges if crossing_strictly_interior else boundary_sign_edges).append(
                    row
                )

        left_summary = _topology_summary(left_analysis)
        right_summary = _topology_summary(right_analysis)
        root_count_stable = (
            left_summary["retained_f_t_root_count"] == right_summary["retained_f_t_root_count"]
        )
        topology_stable = discovery._strict_json_equal(
            left_summary["retained_f_t_topology_signature"],
            right_summary["retained_f_t_topology_signature"],
        )
        filter_stable = discovery._strict_json_equal(
            {
                "excluded_f_t_signature": left_summary["excluded_f_t_signature"],
                "excluded_f_tt_signature": left_summary["excluded_f_tt_signature"],
            },
            {
                "excluded_f_t_signature": right_summary["excluded_f_t_signature"],
                "excluded_f_tt_signature": right_summary["excluded_f_tt_signature"],
            },
        )
        reasons: list[str] = []
        if not root_count_stable:
            reasons.append("retained_f_t_root_count_changed")
        if not topology_stable:
            reasons.append("retained_f_t_topology_signature_changed")
        if assignment["unmatched_left_extremum_indices"]:
            reasons.append("unmatched_left_f_tt_extrema")
        if assignment["unmatched_right_extremum_indices"]:
            reasons.append("unmatched_right_f_tt_extrema")
        if assignment["assignment_ambiguous"]:
            reasons.append("order_preserving_assignment_ambiguous")
        if not filter_stable:
            reasons.append("analysis_filter_signature_changed")
        if edge_has_double_zero_match:
            reasons.append("matched_extremum_zero_at_both_edge_endpoints")
        if reasons:
            topology_review_rows.append(
                {
                    "left_control_index": left_index,
                    "right_control_index": right_index,
                    "left_control_id": left_control["control_id"],
                    "right_control_id": right_control["control_id"],
                    "left_integer_triplet": left_triplet,
                    "right_integer_triplet": right_triplet,
                    "interior_interior_edge": interior_interior,
                    "manual_review_reasons": reasons,
                    "optimal_match_count": assignment["optimal_match_count"],
                    "total_time_separation": assignment["total_time_separation"],
                    "assignment_ambiguous": assignment["assignment_ambiguous"],
                    "unmatched_left_extremum_indices": assignment[
                        "unmatched_left_extremum_indices"
                    ],
                    "unmatched_right_extremum_indices": assignment[
                        "unmatched_right_extremum_indices"
                    ],
                    "left_topology_summary": left_summary,
                    "right_topology_summary": right_summary,
                }
            )

    interior_candidate_seeds = [
        {"source": "near_zero_extremum_at_strictly_interior_control", **row}
        for row in interior_near_zero
    ] + [
        {
            "source": "matched_extremum_sign_change_at_strictly_interior_interpolated_crossing",
            **row,
        }
        for row in interior_sign_edges
    ]
    boundary_diagnostics = [
        {"source": "near_zero_extremum_at_boundary_control", **row} for row in boundary_near_zero
    ] + [
        {"source": "matched_extremum_sign_change_at_boundary_crossing", **row}
        for row in boundary_sign_edges
    ]
    eligible_seed_count = len(interior_candidate_seeds)
    topology_review_required = bool(topology_review_rows)
    family_gate_passed: bool | None
    if eligible_seed_count:
        family_gate_passed = True
    elif topology_review_required:
        family_gate_passed = None
    else:
        family_gate_passed = False
    return {
        "method": (
            "triangular-lattice L1-distance-two edges; order-preserving maximum-cardinality "
            "then minimum-time-separation same-kind extremum matching"
        ),
        "simplex_edge_l1_integer_distance": simplex_edge_l1_integer_distance,
        "simplex_edge_count": len(edges),
        "simplex_edges": [
            {
                "left_control_index": left,
                "right_control_index": right,
                "left_control_id": controls[left]["control_id"],
                "right_control_id": controls[right]["control_id"],
            }
            for left, right in edges
        ],
        "matched_extremum_rows": matched_rows,
        "matched_extremum_count": len(matched_rows),
        "interior_near_zero_extrema": interior_near_zero,
        "interior_near_zero_extremum_count": len(interior_near_zero),
        "boundary_near_zero_diagnostics": boundary_near_zero,
        "boundary_near_zero_diagnostic_count": len(boundary_near_zero),
        "interior_sign_crossing_edges": interior_sign_edges,
        "interior_sign_crossing_edge_count": len(interior_sign_edges),
        "boundary_touching_sign_edge_diagnostics": boundary_sign_edges,
        "boundary_touching_sign_edge_diagnostic_count": len(boundary_sign_edges),
        "unresolved_whole_edge_zero_matches": unresolved_whole_edge_zero_rows,
        "unresolved_whole_edge_zero_match_count": len(unresolved_whole_edge_zero_rows),
        "unmatched_topology_manual_review_rows": topology_review_rows,
        "unmatched_topology_manual_review_count": len(topology_review_rows),
        "topology_manual_review_required": topology_review_required,
        "interior_candidate_seeds": interior_candidate_seeds,
        "boundary_diagnostics": boundary_diagnostics,
        "eligible_candidate_seed_count": eligible_seed_count,
        "family_discovery_gate_passed": family_gate_passed,
        "family_discovery_gate_status": (
            "PASS_ELIGIBLE_INTERIOR_CANDIDATE_SEED_FOUND"
            if family_gate_passed is True
            else (
                "INCONCLUSIVE_MANUAL_REVIEW"
                if family_gate_passed is None
                else "FAIL_NO_ELIGIBLE_INTERIOR_NEAR_ZERO_OR_SIGN_CROSSING"
            )
        ),
        "candidate_automatically_confirms_fold": False,
        "candidate_automatically_selects_segment": False,
        "confirmation_segment_authorized": False,
        "next_protocol_action": (
            "manually_review_topology_then_freeze_at_most_one_new_confirmation_segment"
            if family_gate_passed is True and topology_review_required
            else (
                "freeze_at_most_one_new_confirmation_segment"
                if family_gate_passed is True
                else (
                    "inconclusive_manual_review_without_candidate_promotion_inside_G1c"
                    if family_gate_passed is None
                    else "family_gate_failed_stop_without_physical_retuning"
                )
            )
        ),
        "continuum_verified": False,
        "project_gate_passed": False,
    }


def _curves_to_json(curves: dict[str, np.ndarray]) -> dict[str, list[float]]:
    return {name: [float(value) for value in values] for name, values in curves.items()}


def _checkpoint_filename(control_index: int, triplet: tuple[int, int, int]) -> str:
    return f"control_{control_index:03d}_{control_id(triplet)}.json"


def _checkpoint_path(directory: Path, control_index: int, triplet: tuple[int, int, int]) -> Path:
    return Path(directory) / _checkpoint_filename(control_index, triplet)


def _ledger_template(
    *,
    run_mode: str,
    configuration: SimplexConfiguration,
    configuration_hash: str,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "stage": STAGE,
        "status": "ACTIVE_CHECKPOINT_INTEGRITY_LEDGER",
        "run_mode": run_mode,
        "claim_scope": CLAIM_SCOPE,
        "configuration": configuration.to_dict(),
        "configuration_hash": configuration_hash,
        "provenance": provenance,
        "entries": {},
    }


def _load_and_validate_ledger(
    directory: Path,
    *,
    run_mode: str,
    configuration: SimplexConfiguration,
    configuration_hash: str,
    provenance: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    directory = Path(directory)
    ledger_path = directory / LEDGER_FILENAME
    expected = _ledger_template(
        run_mode=run_mode,
        configuration=configuration,
        configuration_hash=configuration_hash,
        provenance=provenance,
    )
    if directory.exists():
        interrupted = list(directory.glob(".control_*.json.tmp"))
        ledger_tmp = ledger_path.with_name(f".{ledger_path.name}.tmp")
        if ledger_tmp.exists():
            interrupted.append(ledger_tmp)
        if interrupted:
            raise ValueError(f"interrupted checkpoint writes require audit: {interrupted}")
    checkpoint_files = {
        path.name: path for path in directory.glob("control_*.json") if path.is_file()
    }
    if not ledger_path.exists():
        if checkpoint_files:
            raise ValueError("orphan G1c checkpoints exist without an integrity ledger")
        return ledger_path, expected
    if ledger_path.is_symlink() or not ledger_path.is_file():
        raise ValueError("G1c integrity ledger must be a regular file")
    ledger = discovery._load_json_strict(ledger_path, label="G1c checkpoint ledger")
    if type(ledger) is not dict or set(ledger) != set(expected):
        raise ValueError("G1c integrity ledger keys do not match the frozen schema")
    for field in set(expected) - {"entries"}:
        if not discovery._strict_json_equal(ledger[field], expected[field]):
            raise ValueError(f"G1c integrity ledger {field} mismatch")
    entries = ledger["entries"]
    if type(entries) is not dict or set(entries) != set(checkpoint_files):
        raise ValueError("G1c checkpoint files and ledger entries do not agree")
    allowed = {
        _checkpoint_filename(index, triplet): (index, triplet, configuration.weights(triplet))
        for index, triplet in enumerate(configuration.integer_triplets)
    }
    for filename, entry in entries.items():
        if filename not in allowed:
            raise ValueError(f"G1c ledger contains unknown checkpoint {filename}")
        if type(entry) is not dict or set(entry) != {
            "control_index",
            "control_id",
            "integer_triplet",
            "weights",
            "sha256",
        }:
            raise ValueError("G1c ledger entry has the wrong schema")
        index, triplet, weights = allowed[filename]
        expected_entry = {
            "control_index": index,
            "control_id": control_id(triplet),
            "integer_triplet": list(triplet),
            "weights": weights.tolist(),
        }
        for field, expected_value in expected_entry.items():
            if not discovery._strict_json_equal(entry[field], expected_value):
                raise ValueError(f"G1c ledger entry {field} mismatch")
        expected_hash = _validate_hash(entry["sha256"], label="G1c checkpoint ledger hash")
        checkpoint = checkpoint_files[filename]
        if checkpoint.is_symlink() or _sha256(checkpoint) != expected_hash:
            raise ValueError(f"G1c checkpoint integrity hash mismatch for {filename}")
    return ledger_path, ledger


def _record_checkpoint(
    ledger_path: Path,
    ledger: dict[str, Any],
    *,
    checkpoint_path: Path,
    control_index: int,
    triplet: tuple[int, int, int],
    weights: np.ndarray,
) -> None:
    filename = checkpoint_path.name
    if filename in ledger["entries"]:
        raise ValueError(f"G1c ledger already contains {filename}")
    ledger["entries"][filename] = {
        "control_index": control_index,
        "control_id": control_id(triplet),
        "integer_triplet": list(triplet),
        "weights": weights.tolist(),
        "sha256": _sha256(checkpoint_path),
    }
    discovery._atomic_write_json(ledger_path, ledger)


def _compute_control(
    *,
    control_index: int,
    triplet: tuple[int, int, int],
    configuration: SimplexConfiguration,
    run_mode: str,
    configuration_hash: str,
    provenance: dict[str, Any],
    manifest: dict[str, Any],
    shared_foundation: dict[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    weights = configuration.weights(triplet)
    model = assemble_arbitrary_weight_model(configuration, triplet)
    control_diagnostics = arbitrary_weight_model_diagnostics(configuration, triplet, model)
    curves, chunk_diagnostics = discovery.evaluate_observables_chunked(
        model,
        configuration.times(),
        chunk_points=configuration.chunk_points,
    )
    rules = manifest["candidate_rules"]
    candidate_analysis = discovery.analyze_control_curves(
        curves,
        dimensionless_extremum_height_max=rules["dimensionless_extremum_height_max"],
        minimum_analysis_time=rules["minimum_analysis_time"],
        relative_density_floor=rules["relative_density_floor"],
    )
    return {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "stage": STAGE,
        "status": "CONTROL_COMPLETE",
        "run_mode": run_mode,
        "claim_scope": CLAIM_SCOPE,
        "evidence_role": (
            "implementation_diagnostic_only"
            if run_mode == "dry_run"
            else "prospective_G1c_discovery_grid_only"
        ),
        "continuum_verified": False,
        "project_gate_passed": False,
        "configuration_hash": configuration_hash,
        "provenance": provenance,
        "control_index": control_index,
        "control_id": control_id(triplet),
        "integer_triplet": list(triplet),
        "weights": weights.tolist(),
        "parameters": discovery._json_canonical(asdict(model.parameters)),
        "grid": configuration.to_dict()["mesh"],
        "shared_g1a_structural_foundation": shared_foundation,
        "arbitrary_weight_model_diagnostics": control_diagnostics,
        "curves": _curves_to_json(curves),
        "chunk_diagnostics": chunk_diagnostics,
        "candidate_analysis": candidate_analysis,
        "runtime_seconds": time.perf_counter() - started,
    }


def _validate_resumed_checkpoint(
    payload: dict[str, Any],
    *,
    control_index: int,
    triplet: tuple[int, int, int],
    configuration: SimplexConfiguration,
    run_mode: str,
    configuration_hash: str,
    provenance: dict[str, Any],
    manifest: dict[str, Any],
    shared_foundation: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "stage",
        "status",
        "run_mode",
        "claim_scope",
        "evidence_role",
        "continuum_verified",
        "project_gate_passed",
        "configuration_hash",
        "provenance",
        "control_index",
        "control_id",
        "integer_triplet",
        "weights",
        "parameters",
        "grid",
        "shared_g1a_structural_foundation",
        "arbitrary_weight_model_diagnostics",
        "curves",
        "chunk_diagnostics",
        "candidate_analysis",
        "runtime_seconds",
    }
    if type(payload) is not dict or set(payload) != required:
        raise ValueError("G1c checkpoint keys do not match the frozen schema")
    expected_scalars = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "stage": STAGE,
        "status": "CONTROL_COMPLETE",
        "run_mode": run_mode,
        "claim_scope": CLAIM_SCOPE,
        "evidence_role": (
            "implementation_diagnostic_only"
            if run_mode == "dry_run"
            else "prospective_G1c_discovery_grid_only"
        ),
        "continuum_verified": False,
        "project_gate_passed": False,
        "configuration_hash": configuration_hash,
        "control_index": control_index,
        "control_id": control_id(triplet),
    }
    for field, expected in expected_scalars.items():
        if type(payload[field]) is not type(expected) or payload[field] != expected:
            raise ValueError(f"G1c checkpoint field {field} mismatch")
    if not discovery._strict_json_equal(payload["provenance"], provenance):
        raise ValueError("G1c checkpoint provenance mismatch")
    if not discovery._strict_json_equal(payload["integer_triplet"], list(triplet)):
        raise ValueError("G1c checkpoint triplet mismatch")
    if not discovery._strict_json_equal(
        payload["weights"], configuration.weights(triplet).tolist()
    ):
        raise ValueError("G1c checkpoint arbitrary weights mismatch")
    if (
        type(payload["runtime_seconds"]) is not float
        or not math.isfinite(payload["runtime_seconds"])
        or payload["runtime_seconds"] < 0.0
    ):
        raise ValueError("G1c checkpoint runtime is invalid")

    model = assemble_arbitrary_weight_model(configuration, triplet)
    if not discovery._strict_json_equal(
        payload["parameters"], discovery._json_canonical(asdict(model.parameters))
    ):
        raise ValueError("G1c checkpoint physical parameters mismatch")
    if not discovery._strict_json_equal(payload["grid"], configuration.to_dict()["mesh"]):
        raise ValueError("G1c checkpoint mesh mismatch")
    if not discovery._strict_json_equal(
        payload["shared_g1a_structural_foundation"], shared_foundation
    ):
        raise ValueError("G1c checkpoint shared foundation does not reproduce")
    fresh_control_diagnostics = arbitrary_weight_model_diagnostics(configuration, triplet, model)
    if not discovery._strict_json_equal(
        payload["arbitrary_weight_model_diagnostics"], fresh_control_diagnostics
    ):
        raise ValueError("G1c checkpoint arbitrary-weight diagnostics do not reproduce")
    curves = discovery._validate_checkpoint_curves(
        payload["curves"],
        configuration=configuration,
        model=model,
    )
    discovery._validate_chunk_diagnostics(
        payload["chunk_diagnostics"],
        configuration=configuration,
        curves=curves,
    )
    rules = manifest["candidate_rules"]
    expected_analysis = discovery.analyze_control_curves(
        curves,
        dimensionless_extremum_height_max=rules["dimensionless_extremum_height_max"],
        minimum_analysis_time=rules["minimum_analysis_time"],
        relative_density_floor=rules["relative_density_floor"],
    )
    if not discovery._strict_json_equal(payload["candidate_analysis"], expected_analysis):
        raise ValueError("G1c checkpoint candidate analysis does not reproduce")


def _run_locked(
    *,
    manifest: dict[str, Any],
    manifest_path: Path,
    provenance: dict[str, Any],
    configuration: SimplexConfiguration,
    run_mode: str,
    output_path: Path,
    checkpoint_dir: Path,
    resume: bool,
) -> dict[str, Any]:
    configuration_hash = _configuration_hash(configuration, run_mode)
    shared_foundation = shared_foundation_baseline(configuration)
    ledger_path, ledger = _load_and_validate_ledger(
        checkpoint_dir,
        run_mode=run_mode,
        configuration=configuration,
        configuration_hash=configuration_hash,
        provenance=provenance,
    )
    if not resume and ledger["entries"]:
        raise FileExistsError("G1c checkpoint ledger is nonempty and resume is disabled")

    started_utc = _utc_now()
    started = time.perf_counter()
    controls: list[dict[str, Any]] = []
    checkpoint_rows: list[dict[str, Any]] = []
    computed = 0
    resumed_count = 0
    for control_index, triplet in enumerate(configuration.integer_triplets):
        path = _checkpoint_path(checkpoint_dir, control_index, triplet)
        was_resumed = False
        if path.exists():
            if not resume:
                raise FileExistsError(f"G1c checkpoint exists and resume is disabled: {path}")
            checkpoint = discovery._load_json_strict(path, label="G1c checkpoint")
            _validate_resumed_checkpoint(
                checkpoint,
                control_index=control_index,
                triplet=triplet,
                configuration=configuration,
                run_mode=run_mode,
                configuration_hash=configuration_hash,
                provenance=provenance,
                manifest=manifest,
                shared_foundation=shared_foundation,
            )
            was_resumed = True
            resumed_count += 1
        else:
            checkpoint = _compute_control(
                control_index=control_index,
                triplet=triplet,
                configuration=configuration,
                run_mode=run_mode,
                configuration_hash=configuration_hash,
                provenance=provenance,
                manifest=manifest,
                shared_foundation=shared_foundation,
            )
            discovery._atomic_write_json(path, checkpoint)
            _record_checkpoint(
                ledger_path,
                ledger,
                checkpoint_path=path,
                control_index=control_index,
                triplet=triplet,
                weights=configuration.weights(triplet),
            )
            computed += 1
        controls.append(checkpoint)
        checkpoint_rows.append(
            {
                "control_index": control_index,
                "control_id": control_id(triplet),
                "integer_triplet": list(triplet),
                "weights": configuration.weights(triplet).tolist(),
                "filename": path.name,
                "sha256": _sha256(path),
                "resumed_this_invocation": was_resumed,
                "runtime_seconds": checkpoint["runtime_seconds"],
            }
        )

    rules = manifest["candidate_rules"]
    simplex_analysis = analyze_simplex(
        controls,
        time_match_tolerance=rules["time_match_tolerance"],
        simplex_edge_l1_integer_distance=rules["simplex_edge_l1_integer_distance"],
        matched_extremum_sign_change=rules["matched_extremum_sign_change"],
    )
    formal = run_mode == "frozen_formal_G1c"
    family_gate_state = simplex_analysis["family_discovery_gate_passed"]
    if family_gate_state is True:
        formal_status = "G1C_SIMPLEX_COMPLETE_CANDIDATE_SEED_ONLY"
    elif family_gate_state is None:
        formal_status = "G1C_SIMPLEX_INCONCLUSIVE_MANUAL_REVIEW"
    else:
        formal_status = "G1C_SIMPLEX_COMPLETE_FIXED_FAMILY_GATE_FAILED"
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "stage": STAGE,
        "status": (
            "DRY_RUN_COMPLETE_IMPLEMENTATION_DIAGNOSTIC_ONLY" if not formal else formal_status
        ),
        "run_mode": run_mode,
        "formal_frozen_run_completed": formal,
        "evidence_role": (
            "implementation_diagnostic_only"
            if not formal
            else "prospective_result_informed_G1c_discovery_only"
        ),
        "claim_scope": CLAIM_SCOPE,
        "continuum_verified": False,
        "project_gate_passed": False,
        "configuration": configuration.to_dict(),
        "configuration_hash": configuration_hash,
        "provenance": provenance,
        "manifest_status_at_run": manifest["status"],
        "sequential_design_record": manifest["sequential_design_record"],
        "pre_run_amendments": manifest["pre_run_amendments"],
        "candidate_rules": rules,
        "outcome_policy": manifest["outcome_policy"],
        "shared_g1a_structural_foundation": shared_foundation,
        "controls": controls,
        "simplex_candidate_analysis": simplex_analysis,
        "checkpoints": checkpoint_rows,
        "checkpoint_integrity_ledger": {
            "filename": ledger_path.name,
            "sha256": _sha256(ledger_path),
            "entry_count": len(ledger["entries"]),
        },
        "runtime": {
            "started_utc": started_utc,
            "finished_utc": _utc_now(),
            "wall_seconds": time.perf_counter() - started,
            "controls_computed": computed,
            "controls_resumed": resumed_count,
            "maximum_chunk_points": configuration.chunk_points,
            "full_state_history_stored": False,
        },
        "limitations": [
            "G1c is result-informed by G1b and its post-result manual review.",
            "The simplex is a finite discovery grid, not continuum verification.",
            "Boundary flags are diagnostics and cannot pass the interior family gate.",
            "Unmatched topology requires review and is never an automatic candidate.",
            "No candidate automatically selects a confirmation segment.",
            "No control sensitivity, continuation, convergence, tail, or independent-method gate is run.",
        ],
    }
    discovery._atomic_write_json(output_path, result)
    return result


def run_simplex(
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    output_path: Path = DEFAULT_OUTPUT,
    checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR,
    configuration: SimplexConfiguration | None = None,
    run_mode: str,
    resume: bool = True,
) -> dict[str, Any]:
    if run_mode not in {"dry_run", "frozen_formal_G1c"}:
        raise ValueError("run_mode must be dry_run or frozen_formal_G1c")
    manifest_path = Path(manifest_path)
    manifest, manifest_hash = load_and_validate_manifest(manifest_path)
    frozen = SimplexConfiguration.from_manifest(manifest)
    selected = frozen if configuration is None else configuration
    selected.validate()
    if run_mode == "frozen_formal_G1c" and selected != frozen:
        raise ValueError("formal G1c configuration must exactly equal the frozen manifest")
    if run_mode == "dry_run" and selected.integer_triplets != frozen.integer_triplets:
        raise ValueError("G1c dry run must exercise the same complete 66-control simplex")
    input_preflight = validate_required_inputs(manifest["required_inputs"])
    validate_execution_paths(
        manifest=manifest,
        manifest_path=manifest_path,
        output_path=Path(output_path),
        checkpoint_dir=Path(checkpoint_dir),
    )
    provenance = _provenance(manifest_path, manifest_hash, input_preflight)
    if run_mode == "frozen_formal_G1c" and not provenance["running_in_repository_venv"]:
        raise RuntimeError("formal G1c must run inside the repository .venv")
    configuration_hash = _configuration_hash(selected, run_mode)
    # Runtime and all pins are checked before the lock helper can create a directory.
    with discovery._single_writer_lock(
        Path(checkpoint_dir),
        run_mode=run_mode,
        configuration_hash=configuration_hash,
    ):
        return _run_locked(
            manifest=manifest,
            manifest_path=manifest_path,
            provenance=provenance,
            configuration=selected,
            run_mode=run_mode,
            output_path=Path(output_path),
            checkpoint_dir=Path(checkpoint_dir),
            resume=resume,
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="run all 66 controls on the small implementation-only grid",
    )
    mode.add_argument(
        "--execute-frozen",
        action="store_true",
        help="explicitly authorize the exact frozen 65x65x49 G1c simplex",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--checkpoint-dir", type=Path)
    parser.add_argument("--no-resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.dry_run:
        temporary_root: Path | None = None
        if args.output is None or args.checkpoint_dir is None:
            temporary_root = Path(tempfile.mkdtemp(prefix="continuum_g1c_simplex_dry_"))
        output = args.output or temporary_root / "dry_run_result.json"
        checkpoint_dir = args.checkpoint_dir or temporary_root / "checkpoints"
        configuration = SimplexConfiguration.small_full_simplex_dry_run()
        run_mode = "dry_run"
    else:
        output = args.output or DEFAULT_OUTPUT
        checkpoint_dir = args.checkpoint_dir or DEFAULT_CHECKPOINT_DIR
        configuration = None
        run_mode = "frozen_formal_G1c"
    result = run_simplex(
        manifest_path=args.manifest,
        output_path=output,
        checkpoint_dir=checkpoint_dir,
        configuration=configuration,
        run_mode=run_mode,
        resume=not args.no_resume,
    )
    analysis = result["simplex_candidate_analysis"]
    print(
        json.dumps(
            {
                "status": result["status"],
                "run_mode": result["run_mode"],
                "formal_frozen_run_completed": result["formal_frozen_run_completed"],
                "family_discovery_gate_passed": analysis["family_discovery_gate_passed"],
                "eligible_candidate_seed_count": analysis["eligible_candidate_seed_count"],
                "topology_manual_review_required": analysis["topology_manual_review_required"],
                "continuum_verified": result["continuum_verified"],
                "project_gate_passed": result["project_gate_passed"],
                "output": str(output),
                "output_sha256": _sha256(output),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
