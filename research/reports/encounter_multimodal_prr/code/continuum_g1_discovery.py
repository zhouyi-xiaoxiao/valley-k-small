#!/usr/bin/env python3
"""Frozen, resumable G1b topology-discovery runner.

The formal calculation is intentionally guarded by ``--execute-frozen``.
``--dry-run`` exercises the same manifest, checkpoint, chunked-semigroup, and
candidate-analysis paths on a small asymmetric grid.  Neither mode verifies a
continuum fold or passes a project gate.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import platform
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import continuum_g1_smoke as smoke
import numpy as np
import scipy
from scipy.sparse.linalg import expm_multiply

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPOSITORY = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
DEFAULT_MANIFEST = DATA / "continuum_g1_discovery_manifest.json"
DEFAULT_OUTPUT = DATA / "continuum_g1_discovery_result.json"
DEFAULT_CHECKPOINT_DIR = DATA / "continuum_g1_discovery_checkpoints"

STAGE = "G1b_discovery_not_continuum_confirmation"
CLAIM_SCOPE = "Discovery-grid topology screening only; never a continuum fold claim"
CHECKPOINT_SCHEMA_VERSION = 1
CHECKPOINT_LEDGER_SCHEMA_VERSION = 1
RESULT_SCHEMA_VERSION = 2
CHECKPOINT_LEDGER_FILENAME = "integrity_ledger.json"
RUN_LOCK_FILENAME = ".run.lock"
STATE_NEGATIVITY_TOLERANCE = 1.0e-11
SURVIVAL_MONOTONICITY_TOLERANCE = 1.0e-10

# This exact value is the protocol frozen before the 65 x 65 x 49 line run.
# Any added, removed, mistyped, or changed field is rejected rather than
# silently interpreted as a new protocol.
EXPECTED_MANIFEST: dict[str, Any] = {
    "schema_version": 1,
    "stage": STAGE,
    "status": "FROZEN_BEFORE_RUN",
    "date_frozen": "2026-07-13",
    "claim_scope": CLAIM_SCOPE,
    "known_prior_engineering_scan": {
        "grid": [25, 25, 25],
        "theta_count": 11,
        "finding": "one sampled critical maximum at every control",
        "evidence_role": "engineering_only_not_project_gate",
    },
    "mesh": {
        "midpoint_cells": 65,
        "relative_parallel_cells": 65,
        "relative_perp_cells": 49,
        "state_count": 207025,
    },
    "control_line": {
        "lower_weights": [0.70, 0.25, 0.05],
        "upper_weights": [0.05, 0.25, 0.70],
        "theta_values": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
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
        "adjacent_theta_sign_change": True,
    },
    "allowed_followup_if_line_empty": {
        "simplex_spacing": 0.1,
        "physical_retuning_allowed": False,
        "maximum_selected_segments": 1,
    },
    "required_g1a_foundation": {
        "artifact": "artifacts/data/continuum_g1_smoke.json",
        "schema_version": 3,
        "stage": "G1a_pre_fold_foundations",
        "status": "PASS",
        "continuum_verified": False,
        "gate_count": 42,
        "all_gates_true": True,
        "sha256": "a0a1894dbe6dd37bad6973ca6f3dd29b651441f7b911a5406186bb86a18fd3c3",
        "producer_code": "code/continuum_g1_smoke.py",
        "producer_code_sha256": "e0322b212e466b1b640f5adcf30d67d119d2f6fe4cc622eb532082b6cd251701",
    },
    "required_runtime": "repository .venv",
    "protocol_note": "notes/discovery_protocol.md",
}


@dataclass(frozen=True)
class RunConfiguration:
    """Numerical line configuration, formal or explicitly labelled dry-run."""

    midpoint_cells: int
    relative_parallel_cells: int
    relative_perp_cells: int
    theta_values: tuple[float, ...]
    time_start: float
    time_stop: float
    time_spacing: float
    time_points: int
    chunk_points: int

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> RunConfiguration:
        mesh = manifest["mesh"]
        time_grid = manifest["time_grid"]
        return cls(
            midpoint_cells=mesh["midpoint_cells"],
            relative_parallel_cells=mesh["relative_parallel_cells"],
            relative_perp_cells=mesh["relative_perp_cells"],
            theta_values=tuple(manifest["control_line"]["theta_values"]),
            time_start=time_grid["start"],
            time_stop=time_grid["stop"],
            time_spacing=time_grid["spacing"],
            time_points=time_grid["points"],
            chunk_points=time_grid["chunk_points"],
        )

    @classmethod
    def small_dry_run(cls) -> RunConfiguration:
        return cls(
            midpoint_cells=7,
            relative_parallel_cells=9,
            relative_perp_cells=5,
            theta_values=(0.0, 0.5, 1.0),
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "mesh": {
                "midpoint_cells": self.midpoint_cells,
                "relative_parallel_cells": self.relative_parallel_cells,
                "relative_perp_cells": self.relative_perp_cells,
                "state_count": self.state_count,
            },
            "theta_values": list(self.theta_values),
            "time_grid": {
                "start": self.time_start,
                "stop": self.time_stop,
                "spacing": self.time_spacing,
                "points": self.time_points,
                "chunk_points": self.chunk_points,
            },
        }

    def validate(self) -> None:
        cells = (
            self.midpoint_cells,
            self.relative_parallel_cells,
            self.relative_perp_cells,
        )
        if any(type(value) is not int or value < 3 for value in cells):
            raise ValueError("all mesh cell counts must be integers of at least three")
        if not self.theta_values:
            raise ValueError("theta_values must not be empty")
        theta = np.asarray(self.theta_values, dtype=float)
        if (
            np.any(~np.isfinite(theta))
            or np.any(theta < 0.0)
            or np.any(theta > 1.0)
            or np.any(np.diff(theta) <= 0.0)
        ):
            raise ValueError("theta_values must be finite, ordered, unique, and in [0, 1]")
        if type(self.time_points) is not int or self.time_points < 2:
            raise ValueError("time_points must be an integer of at least two")
        if type(self.chunk_points) is not int or not 2 <= self.chunk_points <= self.time_points:
            raise ValueError("chunk_points must lie between two and time_points")
        if (
            not np.isfinite(self.time_start)
            or not np.isfinite(self.time_stop)
            or not np.isfinite(self.time_spacing)
            or self.time_start < 0.0
            or self.time_spacing <= 0.0
            or self.time_stop <= self.time_start
        ):
            raise ValueError("invalid finite time grid")
        expected_stop = self.time_start + (self.time_points - 1) * self.time_spacing
        if not math.isclose(expected_stop, self.time_stop, rel_tol=0.0, abs_tol=1.0e-12):
            raise ValueError("time-grid start, stop, spacing, and points are inconsistent")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _json_canonical(value: Any) -> Any:
    """Return the JSON representation used for strict runtime contracts."""

    return json.loads(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False),
        object_pairs_hook=_reject_duplicate_keys,
    )


def _strict_json_equal(observed: Any, expected: Any) -> bool:
    """Compare JSON values without Python's bool/int/float coercions."""

    if type(observed) is not type(expected):
        return False
    if type(expected) is dict:
        return set(observed) == set(expected) and all(
            _strict_json_equal(observed[key], expected[key]) for key in expected
        )
    if type(expected) is list:
        return len(observed) == len(expected) and all(
            _strict_json_equal(left, right) for left, right in zip(observed, expected, strict=True)
        )
    if type(expected) in {str, int, float, bool, type(None)}:
        return bool(observed == expected)
    return False


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json_strict(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON token: {token}")
            ),
        )
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
        raise ValueError(f"invalid {label} JSON: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{label} JSON root must be an object")
    return payload


def load_and_validate_manifest(path: Path = DEFAULT_MANIFEST) -> tuple[dict[str, Any], str]:
    """Load the exact frozen manifest and return it with its raw-file hash."""

    manifest_path = Path(path)
    if not manifest_path.is_file():
        raise FileNotFoundError(f"discovery manifest is missing: {manifest_path}")
    payload = _load_json_strict(manifest_path, label="discovery manifest")
    if not _strict_json_equal(payload, EXPECTED_MANIFEST):
        raise ValueError("manifest does not exactly match the protocol frozen on 2026-07-13")

    mesh = payload["mesh"]
    state_count = (
        mesh["midpoint_cells"] * mesh["relative_parallel_cells"] * mesh["relative_perp_cells"]
    )
    if state_count != mesh["state_count"]:
        raise ValueError("manifest mesh state_count is inconsistent")
    RunConfiguration.from_manifest(payload).validate()
    if not np.array_equal(
        np.asarray(payload["control_line"]["lower_weights"]),
        smoke.LOWER_WEIGHTS,
    ) or not np.array_equal(
        np.asarray(payload["control_line"]["upper_weights"]),
        smoke.UPPER_WEIGHTS,
    ):
        raise ValueError("manifest control line disagrees with the hardened model")
    protocol = REPORT / payload["protocol_note"]
    if not protocol.is_file():
        raise FileNotFoundError(f"frozen protocol note is missing: {protocol}")
    return payload, _sha256(manifest_path)


def _current_model_contract() -> dict[str, Any]:
    return {
        "physical_parameters": _json_canonical(asdict(smoke.PilotParameters())),
        "control_endpoints": {
            "lower_weights": _json_canonical(smoke.LOWER_WEIGHTS.tolist()),
            "upper_weights": _json_canonical(smoke.UPPER_WEIGHTS.tolist()),
        },
    }


def validate_g1a_foundation_artifact(
    requirement: dict[str, Any],
    *,
    report_root: Path = REPORT,
) -> dict[str, Any]:
    """Verify the exact G1a certificate pinned by the discovery manifest."""

    required_keys = {
        "artifact",
        "schema_version",
        "stage",
        "status",
        "continuum_verified",
        "gate_count",
        "all_gates_true",
        "sha256",
        "producer_code",
        "producer_code_sha256",
    }
    if type(requirement) is not dict or set(requirement) != required_keys:
        raise ValueError("G1a foundation requirement keys do not match the frozen schema")
    if (
        type(requirement["artifact"]) is not str
        or not requirement["artifact"]
        or type(requirement["schema_version"]) is not int
        or type(requirement["stage"]) is not str
        or type(requirement["status"]) is not str
        or type(requirement["continuum_verified"]) is not bool
        or type(requirement["gate_count"]) is not int
        or type(requirement["all_gates_true"]) is not bool
        or type(requirement["sha256"]) is not str
        or type(requirement["producer_code"]) is not str
        or not requirement["producer_code"]
        or type(requirement["producer_code_sha256"]) is not str
    ):
        raise ValueError("G1a foundation requirement contains mistyped fields")
    if requirement["continuum_verified"] is not False:
        raise ValueError("G1a foundation pin must not claim continuum verification")
    if requirement["gate_count"] <= 0 or requirement["all_gates_true"] is not True:
        raise ValueError("G1a foundation pin must require a positive all-true gate set")
    pinned_sha256 = requirement["sha256"]
    if len(pinned_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in pinned_sha256
    ):
        raise ValueError("G1a foundation pin must contain a lowercase SHA-256 digest")
    producer_sha256 = requirement["producer_code_sha256"]
    if len(producer_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in producer_sha256
    ):
        raise ValueError("G1a producer-code pin must contain a lowercase SHA-256 digest")

    root = Path(report_root).resolve()
    relative_artifact = Path(requirement["artifact"])
    if relative_artifact.is_absolute() or ".." in relative_artifact.parts:
        raise ValueError("G1a foundation artifact path must remain relative to the report")
    artifact_path = (root / relative_artifact).resolve()
    try:
        artifact_display = str(artifact_path.relative_to(root))
    except ValueError as error:
        raise ValueError("G1a foundation artifact escapes the report root") from error
    if not artifact_path.is_file():
        raise FileNotFoundError(f"pinned G1a foundation artifact is missing: {artifact_path}")

    relative_producer = Path(requirement["producer_code"])
    if relative_producer.is_absolute() or ".." in relative_producer.parts:
        raise ValueError("G1a producer-code path must remain relative to the report")
    producer_path = (root / relative_producer).resolve()
    try:
        producer_display = str(producer_path.relative_to(root))
    except ValueError as error:
        raise ValueError("G1a producer-code path escapes the report root") from error
    if not producer_path.is_file():
        raise FileNotFoundError(f"pinned G1a producer code is missing: {producer_path}")
    if root == REPORT.resolve() and producer_path != Path(smoke.__file__).resolve():
        raise ValueError("imported model assembler is not the pinned G1a producer code")
    actual_producer_sha256 = _sha256(producer_path)
    if actual_producer_sha256 != producer_sha256:
        raise ValueError(
            "G1a producer-code SHA-256 mismatch: "
            f"expected {producer_sha256}, observed {actual_producer_sha256}"
        )

    actual_sha256 = _sha256(artifact_path)
    if actual_sha256 != pinned_sha256:
        raise ValueError(
            "G1a foundation artifact SHA-256 mismatch: "
            f"expected {pinned_sha256}, observed {actual_sha256}"
        )
    payload = _load_json_strict(artifact_path, label="G1a foundation artifact")
    for field in ("schema_version", "stage", "status", "continuum_verified"):
        if payload.get(field) != requirement[field]:
            raise ValueError(f"G1a foundation artifact {field} disagrees with its frozen pin")
    if type(payload["schema_version"]) is not int or payload["continuum_verified"] is not False:
        raise ValueError("G1a foundation artifact has mistyped certification fields")
    gates = payload.get("gates")
    if type(gates) is not dict or not gates:
        raise ValueError("G1a foundation artifact must contain a nonempty gate object")
    if any(type(name) is not str or not name for name in gates):
        raise ValueError("G1a foundation artifact contains an invalid gate name")
    if any(type(passed) is not bool for passed in gates.values()):
        raise ValueError("G1a foundation artifact gates must be booleans")
    if len(gates) != requirement["gate_count"]:
        raise ValueError("G1a foundation artifact gate count disagrees with its frozen pin")
    if not all(gates.values()):
        failed = sorted(name for name, passed in gates.items() if not passed)
        raise ValueError(f"G1a foundation artifact contains failed gates: {failed}")

    frozen_configuration = payload.get("frozen_configuration")
    if type(frozen_configuration) is not dict:
        raise ValueError("G1a foundation artifact lacks its frozen model configuration")
    pinned_model_contract = {
        "physical_parameters": frozen_configuration.get("physical_parameters"),
        "control_endpoints": frozen_configuration.get("control_endpoints"),
    }
    current_model_contract = _current_model_contract()
    if not _strict_json_equal(pinned_model_contract, current_model_contract):
        if not _strict_json_equal(
            pinned_model_contract["physical_parameters"],
            current_model_contract["physical_parameters"],
        ):
            raise ValueError("current PilotParameters disagree with the pinned G1a model contract")
        raise ValueError("current control endpoints disagree with the pinned G1a model contract")

    return {
        "validation_status": "PASS",
        "artifact": artifact_display,
        "schema_version": payload["schema_version"],
        "stage": payload["stage"],
        "status": payload["status"],
        "continuum_verified": payload["continuum_verified"],
        "gate_count": len(gates),
        "all_gates_true": True,
        "sha256": actual_sha256,
        "producer_code": producer_display,
        "producer_code_sha256": actual_producer_sha256,
        "model_contract": current_model_contract,
        "model_contract_sha256": _json_sha256(current_model_contract),
    }


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


@contextmanager
def _single_writer_lock(
    checkpoint_dir: Path,
    *,
    run_mode: str,
    configuration_hash: str,
):
    """Hold a fail-fast advisory lock for the complete checkpoint run."""

    directory = Path(checkpoint_dir)
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / RUN_LOCK_FILENAME
    handle = lock_path.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            handle.seek(0)
            owner = handle.read().strip() or "owner record unavailable"
            raise RuntimeError(
                f"checkpoint directory already has an active writer: {owner}"
            ) from error
        started_utc = _utc_now()
        owner_record = {
            "status": "LOCK_HELD",
            "pid": os.getpid(),
            "started_utc": started_utc,
            "run_mode": run_mode,
            "configuration_hash": configuration_hash,
        }
        handle.seek(0)
        handle.truncate()
        handle.write(json.dumps(owner_record, sort_keys=True, allow_nan=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        try:
            yield owner_record
        finally:
            released_record = {
                **owner_record,
                "status": "RELEASED",
                "finished_utc": _utc_now(),
            }
            handle.seek(0)
            handle.truncate()
            handle.write(json.dumps(released_record, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


def _provenance(
    manifest_path: Path,
    manifest_sha256: str,
    g1a_foundation_preflight: dict[str, Any],
) -> dict[str, Any]:
    smoke_path = Path(smoke.__file__).resolve()
    protocol_path = REPORT / EXPECTED_MANIFEST["protocol_note"]
    try:
        manifest_display = str(manifest_path.resolve().relative_to(REPORT))
    except ValueError:
        manifest_display = str(manifest_path.resolve())
    repository_venv = REPOSITORY / ".venv"
    running_in_repository_venv = (
        repository_venv.exists()
        and Path(sys.prefix).resolve() == repository_venv.resolve()
        and sys.prefix != sys.base_prefix
    )
    return {
        "manifest": manifest_display,
        "manifest_sha256": manifest_sha256,
        "g1a_foundation_preflight": g1a_foundation_preflight,
        "discovery_code": str(HERE.relative_to(REPORT)),
        "discovery_code_sha256": _sha256(HERE),
        "smoke_code": str(smoke_path.relative_to(REPORT)),
        "smoke_code_sha256": _sha256(smoke_path),
        "protocol_note": str(protocol_path.relative_to(REPORT)),
        "protocol_note_sha256": _sha256(protocol_path),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "python_prefix": sys.prefix,
        "python_base_prefix": sys.base_prefix,
        "repository_venv": str(repository_venv),
        "running_in_repository_venv": running_in_repository_venv,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
    }


def _configuration_hash(configuration: RunConfiguration, run_mode: str) -> str:
    return _json_sha256({"run_mode": run_mode, "configuration": configuration.to_dict()})


def evaluate_observables_chunked(
    model: smoke.QuotientModel,
    times: Sequence[float] | np.ndarray,
    *,
    chunk_points: int,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Evaluate complete observable curves while retaining only one state chunk.

    Consecutive chunks overlap at one state.  Therefore every call to
    ``expm_multiply`` returns at most ``chunk_points`` state vectors, and only
    the final vector is carried into the next call.
    """

    time_values = np.asarray(times, dtype=float).reshape(-1)
    if (
        time_values.size < 2
        or np.any(~np.isfinite(time_values))
        or time_values[0] < 0.0
        or np.any(np.diff(time_values) <= 0.0)
    ):
        raise ValueError("times must be a finite, increasing array with at least two points")
    steps = np.diff(time_values)
    if not np.allclose(steps, steps[0], rtol=1.0e-13, atol=1.0e-15):
        raise ValueError("chunked discovery requires a uniform time grid")
    if type(chunk_points) is not int or not 2 <= chunk_points <= time_values.size:
        raise ValueError("chunk_points must lie between two and the number of times")
    if not math.isclose(time_values[0], 0.0, rel_tol=0.0, abs_tol=1.0e-15):
        raise ValueError("the discovery semigroup must start at time zero")

    killed = model.killed_generator.tocsr()
    operator = killed.T.tocsr()
    action_zero = np.asarray(model.killing, dtype=float)
    action_one = np.asarray(killed @ action_zero, dtype=float)
    action_two = np.asarray(killed @ action_one, dtype=float)
    action_three = np.asarray(killed @ action_two, dtype=float)
    actions = np.column_stack((action_zero, action_one, action_two, action_three))
    if np.any(~np.isfinite(actions)):
        raise FloatingPointError("generator-action observable vectors are non-finite")

    current_state = np.asarray(model.initial, dtype=float).copy()
    if current_state.shape != (model.grid.state_count,):
        raise ValueError("initial state shape disagrees with the model grid")
    initial_observables = current_state @ actions
    accumulated: dict[str, list[float]] = {
        "f": [float(initial_observables[0])],
        "f_t": [float(initial_observables[1])],
        "f_tt": [float(initial_observables[2])],
        "f_ttt": [float(initial_observables[3])],
        "survival": [float(np.sum(current_state))],
    }
    minimum_state_mass = float(np.min(current_state))
    cursor = 0
    chunk_count = 0
    maximum_chunk_rows = 1
    trace = float(np.sum(killed.diagonal()))

    while cursor < time_values.size - 1:
        end = min(cursor + chunk_points - 1, time_values.size - 1)
        rows = end - cursor + 1
        local_stop = float(time_values[end] - time_values[cursor])
        states = np.asarray(
            expm_multiply(
                operator,
                current_state,
                start=0.0,
                stop=local_stop,
                num=rows,
                endpoint=True,
                traceA=trace,
            ),
            dtype=float,
        )
        if states.shape != (rows, model.grid.state_count):
            raise RuntimeError("expm_multiply returned an unexpected chunk shape")
        if np.any(~np.isfinite(states)):
            raise FloatingPointError("state chunk contains non-finite values")
        minimum_state_mass = min(minimum_state_mass, float(np.min(states)))
        new_states = states[1:]
        observable_block = np.asarray(new_states @ actions, dtype=float)
        survival_block = np.asarray(np.sum(new_states, axis=1), dtype=float)
        for column, name in enumerate(("f", "f_t", "f_tt", "f_ttt")):
            accumulated[name].extend(float(value) for value in observable_block[:, column])
        accumulated["survival"].extend(float(value) for value in survival_block)
        current_state = states[-1].copy()
        cursor = end
        chunk_count += 1
        maximum_chunk_rows = max(maximum_chunk_rows, rows)
        del states, new_states, observable_block, survival_block

    curves = {"time": time_values.copy()}
    curves.update({name: np.asarray(values, dtype=float) for name, values in accumulated.items()})
    for name, values in curves.items():
        if values.shape != time_values.shape or np.any(~np.isfinite(values)):
            raise FloatingPointError(f"invalid complete curve: {name}")
    maximum_survival_increase = float(np.max(np.diff(curves["survival"])))
    if minimum_state_mass < -1.0e-11:
        raise RuntimeError("chunked semigroup produced materially negative state mass")
    if float(np.min(curves["f"])) < -1.0e-11:
        raise RuntimeError("chunked semigroup produced a materially negative density")
    if maximum_survival_increase > 1.0e-10:
        raise RuntimeError("chunked semigroup survival is not monotone")
    return curves, {
        "chunk_count": chunk_count,
        "chunk_points_limit": int(chunk_points),
        "maximum_chunk_state_rows": maximum_chunk_rows,
        "state_dimension": model.grid.state_count,
        "full_state_history_stored": False,
        "minimum_state_mass": minimum_state_mass,
        "minimum_density": float(np.min(curves["f"])),
        "maximum_survival_increase": maximum_survival_increase,
    }


def _zero_fraction(left: float, right: float) -> float:
    if left == 0.0 and right == 0.0:
        return 0.5
    if left == 0.0:
        return 0.0
    if right == 0.0:
        return 1.0
    denominator = right - left
    if denominator == 0.0:
        return 0.5
    return float(np.clip(-left / denominator, 0.0, 1.0))


def _interpolate(left: float, right: float, fraction: float) -> float:
    return float(left + fraction * (right - left))


def _sign_bracket_intervals(values: np.ndarray) -> list[tuple[int, int, str]]:
    """Return opposite-sign pairs and one row per maximal exact-zero run."""

    data = np.asarray(values, dtype=float).reshape(-1)
    if data.size < 2 or np.any(~np.isfinite(data)):
        raise ValueError("sign-bracket data must contain at least two finite values")
    intervals: list[tuple[int, int, str]] = []
    index = 0
    while index < data.size:
        if data[index] == 0.0:
            end = index
            while end + 1 < data.size and data[end + 1] == 0.0:
                end += 1
            intervals.append((index, end, "maximal_exact_zero_run"))
            index = end + 1
            continue
        if (
            index + 1 < data.size
            and data[index + 1] != 0.0
            and np.signbit(data[index]) != np.signbit(data[index + 1])
        ):
            intervals.append((index, index + 1, "opposite_sign_samples"))
        index += 1
    return intervals


def _bracket_fraction(values: np.ndarray, left_index: int, right_index: int) -> float:
    if left_index == right_index:
        return 0.0
    left = float(values[left_index])
    right = float(values[right_index])
    if left == 0.0 and right == 0.0:
        return 0.5
    return _zero_fraction(left, right)


def _extremum_kind(values: np.ndarray, left_index: int, right_index: int) -> str:
    before = float(values[left_index - 1]) if left_index > 0 else None
    after = float(values[right_index + 1]) if right_index + 1 < values.size else None
    left = float(values[left_index])
    right = float(values[right_index])
    entering = before if left == 0.0 and before is not None else left
    leaving = after if right == 0.0 and after is not None else right
    if entering < 0.0 < leaving:
        return "minimum_of_f_t"
    if entering > 0.0 > leaving:
        return "maximum_of_f_t"
    return "unresolved_extremum_of_f_t"


def _validated_curves(curves: dict[str, Sequence[float] | np.ndarray]) -> dict[str, np.ndarray]:
    required = {"time", "f", "f_t", "f_tt", "f_ttt", "survival"}
    if set(curves) != required:
        raise ValueError(f"curve keys must be exactly {sorted(required)}")
    result = {name: np.asarray(values, dtype=float).reshape(-1) for name, values in curves.items()}
    sizes = {values.size for values in result.values()}
    if len(sizes) != 1 or next(iter(sizes)) < 2:
        raise ValueError("all curves must have one common length of at least two")
    if any(np.any(~np.isfinite(values)) for values in result.values()):
        raise ValueError("curves must be finite")
    if np.any(np.diff(result["time"]) <= 0.0):
        raise ValueError("curve times must be strictly increasing")
    return result


def analyze_control_curves(
    curves: dict[str, Sequence[float] | np.ndarray],
    *,
    dimensionless_extremum_height_max: float,
    minimum_analysis_time: float,
    relative_density_floor: float,
) -> dict[str, Any]:
    """Apply the frozen per-control sampled-bracket candidate rules."""

    data = _validated_curves(curves)
    threshold = float(dimensionless_extremum_height_max)
    if not np.isfinite(threshold) or threshold <= 0.0:
        raise ValueError("dimensionless extremum threshold must be positive")
    minimum_time = float(minimum_analysis_time)
    relative_floor = float(relative_density_floor)
    if not np.isfinite(minimum_time) or minimum_time < 0.0:
        raise ValueError("minimum_analysis_time must be finite and nonnegative")
    if not np.isfinite(relative_floor) or not 0.0 < relative_floor < 1.0:
        raise ValueError("relative_density_floor must lie strictly between zero and one")
    times = data["time"]
    density = data["f"]
    first = data["f_t"]
    second = data["f_tt"]
    peak_density = max(float(np.max(density)), 0.0)
    absolute_density_floor = relative_floor * peak_density

    def exclusion_reasons(
        estimated_time: float,
        estimated_density: float,
        *,
        left_time: float,
        bracket_type: str,
    ) -> list[str]:
        reasons: list[str] = []
        if left_time < minimum_time:
            reasons.append(
                "exact_zero_run_starts_before_minimum_analysis_time"
                if bracket_type == "maximal_exact_zero_run"
                else "bracket_starts_before_minimum_analysis_time"
            )
        if estimated_time < minimum_time:
            reasons.append("before_minimum_analysis_time")
        if estimated_density <= absolute_density_floor:
            reasons.append("at_or_below_relative_density_floor")
        return reasons

    root_brackets: list[dict[str, Any]] = []
    excluded_roots: list[dict[str, Any]] = []
    raw_root_intervals = _sign_bracket_intervals(first)
    for left_index, right_index, bracket_type in raw_root_intervals:
        fraction = _bracket_fraction(first, left_index, right_index)
        estimated_time = _interpolate(times[left_index], times[right_index], fraction)
        estimated_density = _interpolate(density[left_index], density[right_index], fraction)
        estimated_second = _interpolate(second[left_index], second[right_index], fraction)
        if estimated_second < 0.0:
            topology = "sampled_maximum_of_f"
        elif estimated_second > 0.0:
            topology = "sampled_minimum_of_f"
        else:
            topology = "sampled_degenerate_or_unresolved_root"
        scaled_curvature = (
            estimated_time**2 * estimated_second / estimated_density
            if estimated_density > 0.0
            else None
        )
        row = {
            "bracket_type": bracket_type,
            "left_index": left_index,
            "right_index": right_index,
            "left_time": float(times[left_index]),
            "right_time": float(times[right_index]),
            "left_f_t": float(first[left_index]),
            "right_f_t": float(first[right_index]),
            "linear_root_time": estimated_time,
            "linear_root_fraction": fraction,
            "interpolated_f": estimated_density,
            "interpolated_f_tt": estimated_second,
            "dimensionless_curvature": scaled_curvature,
            "sampled_topology": topology,
        }
        reasons = exclusion_reasons(
            estimated_time,
            estimated_density,
            left_time=float(times[left_index]),
            bracket_type=bracket_type,
        )
        if reasons:
            excluded_roots.append({**row, "exclusion_reasons": reasons})
        else:
            root_brackets.append(row)

    extrema: list[dict[str, Any]] = []
    excluded_extrema: list[dict[str, Any]] = []
    raw_extremum_intervals = _sign_bracket_intervals(second)
    for left_index, right_index, bracket_type in raw_extremum_intervals:
        fraction = _bracket_fraction(second, left_index, right_index)
        estimated_time = _interpolate(times[left_index], times[right_index], fraction)
        estimated_density = _interpolate(density[left_index], density[right_index], fraction)
        estimated_first = _interpolate(first[left_index], first[right_index], fraction)
        kind = _extremum_kind(second, left_index, right_index)
        scaled_height = (
            abs(estimated_time * estimated_first / estimated_density)
            if estimated_density > 0.0
            else None
        )
        row = {
            "extremum_index": len(extrema),
            "bracket_type": bracket_type,
            "left_index": left_index,
            "right_index": right_index,
            "left_time": float(times[left_index]),
            "right_time": float(times[right_index]),
            "left_f_tt": float(second[left_index]),
            "right_f_tt": float(second[right_index]),
            "linear_extremum_time": estimated_time,
            "linear_extremum_fraction": fraction,
            "interpolated_f": estimated_density,
            "interpolated_f_t": estimated_first,
            "extremum_kind": kind,
            "dimensionless_abs_t_f_t_over_f": scaled_height,
            "near_zero_candidate": bool(scaled_height is not None and scaled_height <= threshold),
        }
        reasons = exclusion_reasons(
            estimated_time,
            estimated_density,
            left_time=float(times[left_index]),
            bracket_type=bracket_type,
        )
        if reasons:
            excluded_extrema.append({**row, "exclusion_reasons": reasons})
        else:
            row["extremum_index"] = len(extrema)
            extrema.append(row)

    return {
        "method": (
            "maximal exact-zero runs plus opposite-sign samples; result-blind "
            "time/density filter; linear interpolation only"
        ),
        "dimensionless_extremum_height_max": threshold,
        "minimum_analysis_time": minimum_time,
        "relative_density_floor": relative_floor,
        "peak_sampled_density": peak_density,
        "absolute_density_floor": absolute_density_floor,
        "raw_f_t_bracket_count_before_filter": len(raw_root_intervals),
        "f_t_root_brackets": root_brackets,
        "f_t_root_bracket_count": len(root_brackets),
        "excluded_f_t_brackets": excluded_roots,
        "excluded_f_t_bracket_count": len(excluded_roots),
        "raw_f_tt_extremum_count_before_filter": len(raw_extremum_intervals),
        "f_tt_extrema": extrema,
        "f_tt_extremum_count": len(extrema),
        "excluded_f_tt_extrema": excluded_extrema,
        "excluded_f_tt_extremum_count": len(excluded_extrema),
        "near_zero_extremum_count": sum(row["near_zero_candidate"] for row in extrema),
    }


def _solve_order_preserving_matching(
    left_extrema: Sequence[dict[str, Any]],
    right_extrema: Sequence[dict[str, Any]],
    *,
    tolerance: float,
    forbidden_pair: tuple[int, int] | None = None,
) -> tuple[tuple[int, float], list[tuple[int, int]]]:
    """Maximize cardinality, then minimize separation, without branch crossing."""

    left_count = len(left_extrema)
    right_count = len(right_extrema)
    counts = [[0] * (right_count + 1) for _ in range(left_count + 1)]
    costs = [[0.0] * (right_count + 1) for _ in range(left_count + 1)]
    choices = [["done"] * (right_count + 1) for _ in range(left_count + 1)]

    def better(
        candidate: tuple[int, float, int, str],
        current: tuple[int, float, int, str],
    ) -> bool:
        if candidate[0] != current[0]:
            return candidate[0] > current[0]
        if not math.isclose(candidate[1], current[1], rel_tol=0.0, abs_tol=1.0e-12):
            return candidate[1] < current[1]
        return candidate[2] < current[2]

    for left_index in range(left_count, -1, -1):
        for right_index in range(right_count, -1, -1):
            if left_index == left_count and right_index == right_count:
                continue
            candidates: list[tuple[int, float, int, str]] = []
            if left_index < left_count:
                candidates.append(
                    (
                        counts[left_index + 1][right_index],
                        costs[left_index + 1][right_index],
                        1,
                        "skip_left",
                    )
                )
            if right_index < right_count:
                candidates.append(
                    (
                        counts[left_index][right_index + 1],
                        costs[left_index][right_index + 1],
                        2,
                        "skip_right",
                    )
                )
            if left_index < left_count and right_index < right_count:
                left = left_extrema[left_index]
                right = right_extrema[right_index]
                separation = abs(
                    float(left["linear_extremum_time"]) - float(right["linear_extremum_time"])
                )
                if (
                    (left_index, right_index) != forbidden_pair
                    and left["extremum_kind"] == right["extremum_kind"]
                    and separation <= tolerance
                ):
                    candidates.append(
                        (
                            1 + counts[left_index + 1][right_index + 1],
                            separation + costs[left_index + 1][right_index + 1],
                            0,
                            "match",
                        )
                    )
            best = candidates[0]
            for candidate in candidates[1:]:
                if better(candidate, best):
                    best = candidate
            counts[left_index][right_index] = best[0]
            costs[left_index][right_index] = best[1]
            choices[left_index][right_index] = best[3]

    pairs: list[tuple[int, int]] = []
    left_index = 0
    right_index = 0
    while left_index < left_count or right_index < right_count:
        choice = choices[left_index][right_index]
        if choice == "match":
            pairs.append((left_index, right_index))
            left_index += 1
            right_index += 1
        elif choice == "skip_left":
            left_index += 1
        elif choice == "skip_right":
            right_index += 1
        else:
            break
    return (counts[0][0], costs[0][0]), pairs


def _order_preserving_extremum_matching(
    left_extrema: Sequence[dict[str, Any]],
    right_extrema: Sequence[dict[str, Any]],
    *,
    tolerance: float,
) -> dict[str, Any]:
    for label, extrema in (("left", left_extrema), ("right", right_extrema)):
        times = [float(row["linear_extremum_time"]) for row in extrema]
        if any(not math.isfinite(value) for value in times) or any(
            later <= earlier for earlier, later in zip(times[:-1], times[1:], strict=True)
        ):
            raise ValueError(f"{label} extrema must be finite and strictly time ordered")
    score, pairs = _solve_order_preserving_matching(
        left_extrema,
        right_extrema,
        tolerance=tolerance,
    )
    ambiguous = False
    for pair in pairs:
        alternative_score, _ = _solve_order_preserving_matching(
            left_extrema,
            right_extrema,
            tolerance=tolerance,
            forbidden_pair=pair,
        )
        if alternative_score[0] == score[0] and math.isclose(
            alternative_score[1], score[1], rel_tol=0.0, abs_tol=1.0e-12
        ):
            ambiguous = True
            break
    used_left = {left for left, _ in pairs}
    used_right = {right for _, right in pairs}
    return {
        "pairs": pairs,
        "optimal_match_count": score[0],
        "total_time_separation": score[1],
        "assignment_ambiguous": ambiguous,
        "unmatched_left_extremum_indices": [
            index for index in range(len(left_extrema)) if index not in used_left
        ],
        "unmatched_right_extremum_indices": [
            index for index in range(len(right_extrema)) if index not in used_right
        ],
    }


def _control_topology_transition_summary(candidate_analysis: dict[str, Any]) -> dict[str, Any]:
    root_brackets = candidate_analysis["f_t_root_brackets"]
    excluded_roots = candidate_analysis["excluded_f_t_brackets"]
    excluded_extrema = candidate_analysis["excluded_f_tt_extrema"]
    return {
        "retained_f_t_root_count": candidate_analysis["f_t_root_bracket_count"],
        "retained_f_t_topology_signature": [row["sampled_topology"] for row in root_brackets],
        "excluded_f_t_bracket_count": candidate_analysis["excluded_f_t_bracket_count"],
        "excluded_f_t_signature": [
            {
                "bracket_type": row["bracket_type"],
                "sampled_topology": row["sampled_topology"],
                "exclusion_reasons": row["exclusion_reasons"],
            }
            for row in excluded_roots
        ],
        "excluded_f_tt_extremum_count": candidate_analysis["excluded_f_tt_extremum_count"],
        "excluded_f_tt_signature": [
            {
                "bracket_type": row["bracket_type"],
                "extremum_kind": row["extremum_kind"],
                "exclusion_reasons": row["exclusion_reasons"],
            }
            for row in excluded_extrema
        ],
    }


def analyze_control_line(
    controls: Sequence[dict[str, Any]],
    *,
    time_match_tolerance: float,
    adjacent_theta_sign_change: bool,
) -> dict[str, Any]:
    """Match adjacent-control extrema and apply the frozen sign-change rule."""

    tolerance = float(time_match_tolerance)
    if not np.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("time_match_tolerance must be positive")
    if type(adjacent_theta_sign_change) is not bool:
        raise ValueError("adjacent_theta_sign_change must be boolean")
    if not controls:
        raise ValueError("at least one control is required")
    theta_values = [float(control["theta"]) for control in controls]
    if np.any(np.diff(theta_values) <= 0.0):
        raise ValueError("controls must be strictly ordered by theta")

    near_zero: list[dict[str, Any]] = []
    for control in controls:
        for extremum in control["candidate_analysis"]["f_tt_extrema"]:
            if extremum["near_zero_candidate"]:
                near_zero.append(
                    {
                        "theta_index": int(control["theta_index"]),
                        "theta": float(control["theta"]),
                        **extremum,
                    }
                )

    matches: list[dict[str, Any]] = []
    sign_brackets: list[dict[str, Any]] = []
    matching_diagnostics: list[dict[str, Any]] = []
    for left_control, right_control in zip(controls[:-1], controls[1:], strict=True):
        left_analysis = left_control["candidate_analysis"]
        right_analysis = right_control["candidate_analysis"]
        left_extrema = left_analysis["f_tt_extrema"]
        right_extrema = right_analysis["f_tt_extrema"]
        left_summary = _control_topology_transition_summary(left_analysis)
        right_summary = _control_topology_transition_summary(right_analysis)
        assignment = _order_preserving_extremum_matching(
            left_extrema,
            right_extrema,
            tolerance=tolerance,
        )
        sign_bracket_count_before = len(sign_brackets)
        for left_index, right_index in assignment["pairs"]:
            left = left_extrema[left_index]
            right = right_extrema[right_index]
            separation = abs(
                float(left["linear_extremum_time"]) - float(right["linear_extremum_time"])
            )
            left_height = float(left["interpolated_f_t"])
            right_height = float(right["interpolated_f_t"])
            strict_opposite_sign = bool(
                left_height != 0.0
                and right_height != 0.0
                and np.signbit(left_height) != np.signbit(right_height)
            )
            exact_zero_theta_locations = []
            if left_height == 0.0:
                exact_zero_theta_locations.append(float(left_control["theta"]))
            if right_height == 0.0:
                exact_zero_theta_locations.append(float(right_control["theta"]))
            sampled_root_evidence = bool(strict_opposite_sign or exact_zero_theta_locations)
            changed_sign = bool(adjacent_theta_sign_change and sampled_root_evidence)
            interior_root_evidence = bool(
                changed_sign
                and (
                    strict_opposite_sign
                    or any(0.0 < theta < 1.0 for theta in exact_zero_theta_locations)
                )
            )
            row = {
                "left_theta_index": int(left_control["theta_index"]),
                "right_theta_index": int(right_control["theta_index"]),
                "left_theta": float(left_control["theta"]),
                "right_theta": float(right_control["theta"]),
                "left_extremum_index": int(left["extremum_index"]),
                "right_extremum_index": int(right["extremum_index"]),
                "extremum_kind": left["extremum_kind"],
                "left_time": float(left["linear_extremum_time"]),
                "right_time": float(right["linear_extremum_time"]),
                "time_separation": separation,
                "left_interpolated_f_t": left_height,
                "right_interpolated_f_t": right_height,
                "strict_opposite_sign": strict_opposite_sign,
                "exact_zero_theta_locations": exact_zero_theta_locations,
                "adjacent_theta_sign_bracket": changed_sign,
                "interior_root_evidence": interior_root_evidence,
            }
            matches.append(row)
            if changed_sign:
                sign_brackets.append(row.copy())
        root_count_stable = (
            left_summary["retained_f_t_root_count"] == right_summary["retained_f_t_root_count"]
        )
        topology_signature_stable = _strict_json_equal(
            left_summary["retained_f_t_topology_signature"],
            right_summary["retained_f_t_topology_signature"],
        )
        filter_signature_stable = _strict_json_equal(
            {
                "excluded_f_t_signature": left_summary["excluded_f_t_signature"],
                "excluded_f_tt_signature": left_summary["excluded_f_tt_signature"],
            },
            {
                "excluded_f_t_signature": right_summary["excluded_f_t_signature"],
                "excluded_f_tt_signature": right_summary["excluded_f_tt_signature"],
            },
        )
        review_reasons: list[str] = []
        if not root_count_stable:
            review_reasons.append("retained_f_t_root_count_changed")
        if not topology_signature_stable:
            review_reasons.append("retained_f_t_topology_signature_changed")
        if assignment["unmatched_left_extremum_indices"]:
            review_reasons.append("unmatched_left_f_tt_extrema")
        if assignment["unmatched_right_extremum_indices"]:
            review_reasons.append("unmatched_right_f_tt_extrema")
        if assignment["assignment_ambiguous"]:
            review_reasons.append("order_preserving_assignment_ambiguous")
        if not filter_signature_stable:
            review_reasons.append("analysis_filter_signature_changed")
        matching_diagnostics.append(
            {
                "left_theta_index": int(left_control["theta_index"]),
                "right_theta_index": int(right_control["theta_index"]),
                "left_theta": float(left_control["theta"]),
                "right_theta": float(right_control["theta"]),
                "optimal_match_count": assignment["optimal_match_count"],
                "total_time_separation": assignment["total_time_separation"],
                "assignment_ambiguous": assignment["assignment_ambiguous"],
                "left_topology_summary": left_summary,
                "right_topology_summary": right_summary,
                "retained_f_t_root_count_stable": root_count_stable,
                "retained_f_t_topology_signature_stable": topology_signature_stable,
                "analysis_filter_signature_stable": filter_signature_stable,
                "unmatched_left_extremum_indices": assignment["unmatched_left_extremum_indices"],
                "unmatched_right_extremum_indices": assignment["unmatched_right_extremum_indices"],
                "sign_bracket_count": len(sign_brackets) - sign_bracket_count_before,
                "manual_review_required": bool(review_reasons),
                "manual_review_reasons": review_reasons,
            }
        )

    assignment_ambiguity_count = sum(row["assignment_ambiguous"] for row in matching_diagnostics)
    matching_ambiguity = assignment_ambiguity_count > 0
    transition_review_rows = [row for row in matching_diagnostics if row["manual_review_required"]]
    transition_review_required = bool(transition_review_rows)
    line_has_flag = bool(near_zero or sign_brackets or transition_review_required)
    interior_near_zero = any(0.0 < row["theta"] < 1.0 for row in near_zero)
    interior_sign_bracket = any(row["interior_root_evidence"] for row in sign_brackets)
    interior_flag = bool(interior_near_zero or interior_sign_bracket)
    return {
        "method": (
            "order-preserving maximum-cardinality then minimum-total-time-separation "
            "matching within extremum kind"
        ),
        "time_match_tolerance": tolerance,
        "adjacent_theta_sign_change_enabled": adjacent_theta_sign_change,
        "near_zero_extrema": near_zero,
        "near_zero_extremum_count": len(near_zero),
        "adjacent_theta_extremum_matches": matches,
        "adjacent_theta_extremum_match_count": len(matches),
        "adjacent_theta_sign_brackets": sign_brackets,
        "adjacent_theta_sign_bracket_count": len(sign_brackets),
        "matching_diagnostics": matching_diagnostics,
        "assignment_ambiguity_count": assignment_ambiguity_count,
        "action_blocked_by_matching_ambiguity": matching_ambiguity,
        "topology_transition_manual_review_required": transition_review_required,
        "topology_transition_manual_review_rows": transition_review_rows,
        "line_has_discovery_flag": line_has_flag,
        "interior_discovery_flag": interior_flag,
        "next_protocol_action": (
            "matching_ambiguity_requires_manual_resolution_before_line_action"
            if matching_ambiguity
            else (
                "topology_transition_requires_manual_review_before_line_action"
                if transition_review_required
                else (
                    "freeze_candidate_only_then_implement_sensitivity_before_continuation"
                    if interior_flag
                    else (
                        "endpoint_only_flag_does_not_authorize_candidate_freeze"
                        if line_has_flag
                        else "line_empty_only_predeclared_simplex_followup_is_allowed"
                    )
                )
            )
        ),
        "continuum_verified": False,
        "project_gate_passed": False,
    }


def _curves_to_json(curves: dict[str, np.ndarray]) -> dict[str, list[float]]:
    return {name: [float(value) for value in values] for name, values in curves.items()}


def _assemble_model(configuration: RunConfiguration, theta: float) -> smoke.QuotientModel:
    parameters = smoke.PilotParameters()
    grid = smoke.QuotientGrid2D(
        midpoint_cells=configuration.midpoint_cells,
        relative_parallel_cells=configuration.relative_parallel_cells,
        relative_perp_cells=configuration.relative_perp_cells,
        midpoint_bounds=parameters.midpoint_bounds,
        relative_parallel_bounds=parameters.relative_parallel_bounds,
        transverse_width=parameters.transverse_width,
    )
    return smoke.build_model(grid, theta=theta, parameters=parameters)


def _model_diagnostics(model: smoke.QuotientModel) -> dict[str, Any]:
    diagnostics = smoke.foundation_diagnostics(model)
    gates = smoke.foundation_gates(model, diagnostics)
    if not all(gates.values()):
        failed = sorted(name for name, passed in gates.items() if not passed)
        raise RuntimeError(f"hardened model diagnostics failed: {failed}")
    return {"gates": gates, "diagnostics": diagnostics}


def _validate_checkpoint_curves(
    payload: Any,
    *,
    configuration: RunConfiguration,
    model: smoke.QuotientModel,
) -> dict[str, np.ndarray]:
    required = {"time", "f", "f_t", "f_tt", "f_ttt", "survival"}
    if type(payload) is not dict or set(payload) != required:
        raise ValueError("checkpoint curve keys do not match the frozen schema")
    for name in required:
        values = payload[name]
        if type(values) is not list or len(values) != configuration.time_points:
            raise ValueError(f"checkpoint curve {name} has the wrong JSON shape")
        if any(type(value) is not float for value in values):
            raise ValueError(f"checkpoint curve {name} must contain JSON floats")
        if any(not math.isfinite(value) for value in values):
            raise ValueError(f"checkpoint curve {name} contains non-finite values")

    expected_times = [float(value) for value in configuration.times()]
    if not _strict_json_equal(payload["time"], expected_times):
        raise ValueError("checkpoint time curve disagrees with the frozen configuration")
    curves = {name: np.asarray(values, dtype=float) for name, values in payload.items()}
    density = curves["f"]
    survival = curves["survival"]
    initial_mass = float(np.sum(model.initial))
    if not math.isclose(initial_mass, 1.0, rel_tol=0.0, abs_tol=1.0e-12):
        raise RuntimeError("freshly assembled model has an invalid initial mass")
    if not math.isclose(float(survival[0]), initial_mass, rel_tol=0.0, abs_tol=1.0e-12):
        raise ValueError("checkpoint initial survival disagrees with the fresh model mass")
    if (
        float(np.min(survival)) < -STATE_NEGATIVITY_TOLERANCE
        or float(np.max(survival)) > initial_mass + SURVIVAL_MONOTONICITY_TOLERANCE
        or float(np.max(np.diff(survival))) > SURVIVAL_MONOTONICITY_TOLERANCE
    ):
        raise ValueError("checkpoint survival violates mass bounds or monotonicity")
    if float(np.min(density)) < -STATE_NEGATIVITY_TOLERANCE:
        raise ValueError("checkpoint density is materially negative")

    actions = [np.asarray(model.killing, dtype=float)]
    for _ in range(4):
        actions.append(np.asarray(model.killed_generator @ actions[-1], dtype=float))
    if any(np.any(~np.isfinite(action)) for action in actions):
        raise RuntimeError("fresh model generator-action bounds are non-finite")
    action_curves = ("f", "f_t", "f_tt", "f_ttt")
    for order, name in enumerate(action_curves):
        values = curves[name]
        initial_value = float(model.initial @ actions[order])
        scale = max(1.0, float(np.max(np.abs(actions[order]))))
        if not math.isclose(
            float(values[0]),
            initial_value,
            rel_tol=2.0e-13,
            abs_tol=2.0e-13 * scale,
        ):
            raise ValueError(f"checkpoint initial {name} disagrees with the fresh model")
        pointwise_bound = survival * float(np.max(np.abs(actions[order])))
        tolerance = 2.0e-12 * scale
        if np.any(np.abs(values) > pointwise_bound + tolerance):
            raise ValueError(f"checkpoint {name} violates its generator-action mass bound")
        derivative_bound = initial_mass * float(np.max(np.abs(actions[order + 1])))
        if np.any(
            np.abs(np.diff(values)) > configuration.time_spacing * derivative_bound + tolerance
        ):
            raise ValueError(f"checkpoint {name} violates its generator-action increment bound")

    survival_loss = survival[:-1] - survival[1:]
    left_rectangle = configuration.time_spacing * density[:-1]
    density_derivative_bound = initial_mass * float(np.max(np.abs(actions[1])))
    quadrature_bound = 0.5 * configuration.time_spacing**2 * density_derivative_bound
    if np.any(np.abs(survival_loss - left_rectangle) > quadrature_bound + 2.0e-12):
        raise ValueError("checkpoint survival and density violate killed-mass balance bounds")
    return curves


def _validate_chunk_diagnostics(
    payload: Any,
    *,
    configuration: RunConfiguration,
    curves: dict[str, np.ndarray],
) -> None:
    required = {
        "chunk_count",
        "chunk_points_limit",
        "maximum_chunk_state_rows",
        "state_dimension",
        "full_state_history_stored",
        "minimum_state_mass",
        "minimum_density",
        "maximum_survival_increase",
    }
    if type(payload) is not dict or set(payload) != required:
        raise ValueError("checkpoint chunk diagnostics do not match the frozen schema")
    for field in (
        "chunk_count",
        "chunk_points_limit",
        "maximum_chunk_state_rows",
        "state_dimension",
    ):
        if type(payload[field]) is not int:
            raise ValueError(f"checkpoint chunk diagnostic {field} must be an integer")
    for field in ("minimum_state_mass", "minimum_density", "maximum_survival_increase"):
        if type(payload[field]) is not float or not math.isfinite(payload[field]):
            raise ValueError(f"checkpoint chunk diagnostic {field} must be a finite float")
    expected_chunk_count = (configuration.time_points - 1 + configuration.chunk_points - 2) // (
        configuration.chunk_points - 1
    )
    if payload["chunk_count"] != expected_chunk_count:
        raise ValueError("checkpoint chunk count disagrees with the frozen time grid")
    if (
        payload["chunk_points_limit"] != configuration.chunk_points
        or payload["maximum_chunk_state_rows"] != configuration.chunk_points
        or payload["state_dimension"] != configuration.state_count
        or payload["full_state_history_stored"] is not False
    ):
        raise ValueError("checkpoint chunk dimensions or history flag are invalid")
    observed_minimum_density = float(np.min(curves["f"]))
    observed_survival_increase = float(np.max(np.diff(curves["survival"])))
    if payload["minimum_density"] != observed_minimum_density:
        raise ValueError("checkpoint minimum-density diagnostic does not reproduce")
    if payload["maximum_survival_increase"] != observed_survival_increase:
        raise ValueError("checkpoint survival-increase diagnostic does not reproduce")
    if (
        payload["minimum_state_mass"] < -STATE_NEGATIVITY_TOLERANCE
        or payload["minimum_state_mass"] > 1.0 + SURVIVAL_MONOTONICITY_TOLERANCE
        or payload["minimum_density"] < -STATE_NEGATIVITY_TOLERANCE
        or payload["maximum_survival_increase"] > SURVIVAL_MONOTONICITY_TOLERANCE
    ):
        raise ValueError("checkpoint chunk diagnostics violate numerical bounds")


def _checkpoint_path(directory: Path, theta_index: int) -> Path:
    return directory / f"theta_{theta_index:03d}.json"


def _checkpoint_ledger_template(
    *,
    run_mode: str,
    configuration: RunConfiguration,
    configuration_hash: str,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": CHECKPOINT_LEDGER_SCHEMA_VERSION,
        "stage": STAGE,
        "status": "ACTIVE_CHECKPOINT_INTEGRITY_LEDGER",
        "run_mode": run_mode,
        "claim_scope": CLAIM_SCOPE,
        "configuration": configuration.to_dict(),
        "configuration_hash": configuration_hash,
        "provenance": provenance,
        "entries": {},
    }


def _load_and_validate_checkpoint_ledger(
    directory: Path,
    *,
    run_mode: str,
    configuration: RunConfiguration,
    configuration_hash: str,
    provenance: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    directory = Path(directory)
    ledger_path = directory / CHECKPOINT_LEDGER_FILENAME
    expected = _checkpoint_ledger_template(
        run_mode=run_mode,
        configuration=configuration,
        configuration_hash=configuration_hash,
        provenance=provenance,
    )
    if directory.exists():
        interrupted = list(directory.glob(".theta_*.json.tmp"))
        ledger_temporary = ledger_path.with_name(f".{ledger_path.name}.tmp")
        if ledger_temporary.exists():
            interrupted.append(ledger_temporary)
        if interrupted:
            raise ValueError(f"interrupted checkpoint writes require audit: {interrupted}")
    checkpoint_files = {
        path.name: path for path in directory.glob("theta_*.json") if path.is_file()
    }
    if not ledger_path.exists():
        if checkpoint_files:
            raise ValueError("orphan checkpoints exist without an integrity ledger")
        return ledger_path, expected
    if ledger_path.is_symlink() or not ledger_path.is_file():
        raise ValueError("checkpoint integrity ledger must be a regular file")
    ledger = _load_json_strict(ledger_path, label="checkpoint integrity ledger")
    if type(ledger) is not dict or set(ledger) != set(expected):
        raise ValueError("checkpoint integrity ledger keys do not match the frozen schema")
    for field in set(expected) - {"entries"}:
        if not _strict_json_equal(ledger[field], expected[field]):
            raise ValueError(f"checkpoint integrity ledger {field} mismatch")
    entries = ledger["entries"]
    if type(entries) is not dict:
        raise ValueError("checkpoint integrity ledger entries must be an object")
    if set(entries) != set(checkpoint_files):
        raise ValueError("checkpoint files and integrity-ledger entries do not agree")
    allowed_filenames = {
        _checkpoint_path(directory, index).name: (index, float(theta))
        for index, theta in enumerate(configuration.theta_values)
    }
    for filename, entry in entries.items():
        if filename not in allowed_filenames:
            raise ValueError(f"integrity ledger contains an unknown checkpoint: {filename}")
        if type(entry) is not dict or set(entry) != {"theta_index", "theta", "sha256"}:
            raise ValueError("checkpoint integrity-ledger entry has the wrong schema")
        theta_index, theta = allowed_filenames[filename]
        if (
            type(entry["theta_index"]) is not int
            or entry["theta_index"] != theta_index
            or type(entry["theta"]) is not float
            or entry["theta"] != theta
            or type(entry["sha256"]) is not str
            or len(entry["sha256"]) != 64
            or any(character not in "0123456789abcdef" for character in entry["sha256"])
        ):
            raise ValueError("checkpoint integrity-ledger entry metadata mismatch")
        checkpoint_path = checkpoint_files[filename]
        if checkpoint_path.is_symlink():
            raise ValueError("checkpoint must be a regular non-symlink file")
        actual_sha256 = _sha256(checkpoint_path)
        if actual_sha256 != entry["sha256"]:
            raise ValueError(
                f"checkpoint integrity hash mismatch for {filename}: "
                f"expected {entry['sha256']}, observed {actual_sha256}"
            )
    return ledger_path, ledger


def _record_checkpoint_in_ledger(
    ledger_path: Path,
    ledger: dict[str, Any],
    *,
    checkpoint_path: Path,
    theta_index: int,
    theta: float,
    checkpoint_sha256: str,
) -> None:
    filename = checkpoint_path.name
    if filename in ledger["entries"]:
        raise ValueError(f"integrity ledger already contains new checkpoint {filename}")
    ledger["entries"][filename] = {
        "theta_index": theta_index,
        "theta": theta,
        "sha256": checkpoint_sha256,
    }
    _atomic_write_json(ledger_path, ledger)


def _validate_resumed_checkpoint(
    payload: dict[str, Any],
    *,
    theta_index: int,
    theta: float,
    run_mode: str,
    configuration: RunConfiguration,
    configuration_hash: str,
    provenance: dict[str, Any],
    rules: dict[str, Any],
) -> None:
    required_top = {
        "schema_version",
        "stage",
        "status",
        "run_mode",
        "claim_scope",
        "continuum_verified",
        "project_gate_passed",
        "configuration_hash",
        "provenance",
        "theta_index",
        "theta",
        "weights",
        "parameters",
        "grid",
        "model_diagnostics",
        "curves",
        "chunk_diagnostics",
        "candidate_analysis",
        "runtime_seconds",
    }
    if set(payload) != required_top:
        raise ValueError("checkpoint keys do not match the frozen checkpoint schema")
    if (
        type(payload["schema_version"]) is not int
        or payload["schema_version"] != CHECKPOINT_SCHEMA_VERSION
        or type(payload["stage"]) is not str
        or payload["stage"] != STAGE
        or type(payload["status"]) is not str
        or payload["status"] != "THETA_COMPLETE"
        or type(payload["run_mode"]) is not str
        or payload["run_mode"] != run_mode
        or type(payload["claim_scope"]) is not str
        or payload["claim_scope"] != CLAIM_SCOPE
        or payload["continuum_verified"] is not False
        or payload["project_gate_passed"] is not False
        or type(payload["configuration_hash"]) is not str
        or payload["configuration_hash"] != configuration_hash
        or not _strict_json_equal(payload["provenance"], provenance)
        or type(payload["theta_index"]) is not int
        or payload["theta_index"] != theta_index
        or type(payload["theta"]) is not float
        or payload["theta"] != theta
    ):
        raise ValueError("checkpoint provenance or frozen configuration mismatch")
    if (
        type(payload["runtime_seconds"]) is not float
        or not math.isfinite(payload["runtime_seconds"])
        or payload["runtime_seconds"] < 0.0
    ):
        raise ValueError("checkpoint runtime must be a finite nonnegative float")

    model = _assemble_model(configuration, theta)
    expected_parameters = _json_canonical(asdict(model.parameters))
    if not _strict_json_equal(payload["parameters"], expected_parameters):
        raise ValueError("checkpoint parameters disagree with current frozen PilotParameters")
    expected_grid = configuration.to_dict()["mesh"]
    if not _strict_json_equal(payload["grid"], expected_grid):
        raise ValueError("checkpoint grid disagrees with the frozen configuration")
    expected_weights = ((1.0 - theta) * smoke.LOWER_WEIGHTS + theta * smoke.UPPER_WEIGHTS).tolist()
    if not _strict_json_equal(payload["weights"], expected_weights):
        raise ValueError("checkpoint weights disagree with the frozen control line")

    observed_model_diagnostics = payload["model_diagnostics"]
    if type(observed_model_diagnostics) is not dict or set(observed_model_diagnostics) != {
        "gates",
        "diagnostics",
    }:
        raise ValueError("checkpoint model diagnostics do not match the frozen schema")
    expected_model_diagnostics = _json_canonical(_model_diagnostics(model))
    observed_gates = observed_model_diagnostics["gates"]
    expected_gates = expected_model_diagnostics["gates"]
    if type(observed_gates) is not dict or set(observed_gates) != set(expected_gates):
        raise ValueError("checkpoint model gate names disagree with the fresh model")
    if any(type(value) is not bool or value is not True for value in observed_gates.values()):
        raise ValueError("checkpoint model gates must be Boolean true")
    if not _strict_json_equal(observed_model_diagnostics, expected_model_diagnostics):
        raise ValueError("checkpoint model diagnostics do not reproduce from a fresh model")

    curves = _validate_checkpoint_curves(
        payload["curves"],
        configuration=configuration,
        model=model,
    )
    _validate_chunk_diagnostics(
        payload["chunk_diagnostics"],
        configuration=configuration,
        curves=curves,
    )
    expected_analysis = analyze_control_curves(
        curves,
        dimensionless_extremum_height_max=rules["dimensionless_extremum_height_max"],
        minimum_analysis_time=rules["minimum_analysis_time"],
        relative_density_floor=rules["relative_density_floor"],
    )
    if not _strict_json_equal(payload["candidate_analysis"], expected_analysis):
        raise ValueError("checkpoint candidate analysis does not reproduce from its curves")


def _compute_control(
    *,
    theta_index: int,
    theta: float,
    configuration: RunConfiguration,
    run_mode: str,
    configuration_hash: str,
    provenance: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    model = _assemble_model(configuration, theta)
    parameters = model.parameters
    grid = model.grid
    model_diagnostics = _model_diagnostics(model)
    curves, chunk_diagnostics = evaluate_observables_chunked(
        model,
        configuration.times(),
        chunk_points=configuration.chunk_points,
    )
    rules = manifest["candidate_rules"]
    candidate_analysis = analyze_control_curves(
        curves,
        dimensionless_extremum_height_max=rules["dimensionless_extremum_height_max"],
        minimum_analysis_time=rules["minimum_analysis_time"],
        relative_density_floor=rules["relative_density_floor"],
    )
    lower = np.asarray(manifest["control_line"]["lower_weights"], dtype=float)
    upper = np.asarray(manifest["control_line"]["upper_weights"], dtype=float)
    weights = (1.0 - theta) * lower + theta * upper
    return {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "stage": STAGE,
        "status": "THETA_COMPLETE",
        "run_mode": run_mode,
        "claim_scope": CLAIM_SCOPE,
        "continuum_verified": False,
        "project_gate_passed": False,
        "configuration_hash": configuration_hash,
        "provenance": provenance,
        "theta_index": theta_index,
        "theta": theta,
        "weights": weights.tolist(),
        "parameters": asdict(parameters),
        "grid": {
            "midpoint_cells": grid.midpoint_cells,
            "relative_parallel_cells": grid.relative_parallel_cells,
            "relative_perp_cells": grid.relative_perp_cells,
            "state_count": grid.state_count,
        },
        "model_diagnostics": model_diagnostics,
        "curves": _curves_to_json(curves),
        "chunk_diagnostics": chunk_diagnostics,
        "candidate_analysis": candidate_analysis,
        "runtime_seconds": time.perf_counter() - started,
    }


def _run_discovery_locked(
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    output_path: Path = DEFAULT_OUTPUT,
    checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR,
    configuration: RunConfiguration | None = None,
    run_mode: str,
    resume: bool = True,
) -> dict[str, Any]:
    """Run or resume one manifest-bound discovery line."""

    if run_mode not in {"dry_run", "frozen_formal_discovery"}:
        raise ValueError("run_mode must be dry_run or frozen_formal_discovery")
    manifest_path = Path(manifest_path)
    manifest, manifest_sha256 = load_and_validate_manifest(manifest_path)
    frozen_configuration = RunConfiguration.from_manifest(manifest)
    selected = frozen_configuration if configuration is None else configuration
    selected.validate()
    if run_mode == "frozen_formal_discovery" and selected != frozen_configuration:
        raise ValueError("formal discovery configuration must exactly equal the frozen manifest")
    g1a_foundation_preflight = validate_g1a_foundation_artifact(manifest["required_g1a_foundation"])
    provenance = _provenance(
        manifest_path,
        manifest_sha256,
        g1a_foundation_preflight,
    )
    if run_mode == "frozen_formal_discovery" and not provenance["running_in_repository_venv"]:
        raise RuntimeError("formal discovery must run inside the repository .venv")
    configuration_hash = _configuration_hash(selected, run_mode)
    rules = manifest["candidate_rules"]
    checkpoint_dir = Path(checkpoint_dir)
    output_path = Path(output_path)
    ledger_path, checkpoint_ledger = _load_and_validate_checkpoint_ledger(
        checkpoint_dir,
        run_mode=run_mode,
        configuration=selected,
        configuration_hash=configuration_hash,
        provenance=provenance,
    )
    if not resume and checkpoint_ledger["entries"]:
        raise FileExistsError("checkpoint integrity ledger is nonempty and resume is disabled")
    started_utc = _utc_now()
    started = time.perf_counter()
    controls: list[dict[str, Any]] = []
    checkpoint_rows: list[dict[str, Any]] = []
    computed_count = 0
    resumed_count = 0

    for theta_index, theta_value in enumerate(selected.theta_values):
        theta = float(theta_value)
        checkpoint_path = _checkpoint_path(checkpoint_dir, theta_index)
        resumed = False
        if checkpoint_path.exists():
            if not resume:
                raise FileExistsError(
                    f"checkpoint exists and resume is disabled: {checkpoint_path}"
                )
            checkpoint = _load_json_strict(checkpoint_path, label="discovery checkpoint")
            _validate_resumed_checkpoint(
                checkpoint,
                theta_index=theta_index,
                theta=theta,
                run_mode=run_mode,
                configuration=selected,
                configuration_hash=configuration_hash,
                provenance=provenance,
                rules=rules,
            )
            resumed = True
            resumed_count += 1
        else:
            checkpoint = _compute_control(
                theta_index=theta_index,
                theta=theta,
                configuration=selected,
                run_mode=run_mode,
                configuration_hash=configuration_hash,
                provenance=provenance,
                manifest=manifest,
            )
            _atomic_write_json(checkpoint_path, checkpoint)
            checkpoint_sha256 = _sha256(checkpoint_path)
            _record_checkpoint_in_ledger(
                ledger_path,
                checkpoint_ledger,
                checkpoint_path=checkpoint_path,
                theta_index=theta_index,
                theta=theta,
                checkpoint_sha256=checkpoint_sha256,
            )
            computed_count += 1
        checkpoint_sha256 = _sha256(checkpoint_path)
        controls.append(checkpoint)
        checkpoint_rows.append(
            {
                "theta_index": theta_index,
                "theta": theta,
                "filename": checkpoint_path.name,
                "sha256": checkpoint_sha256,
                "resumed_this_invocation": resumed,
                "runtime_seconds": checkpoint["runtime_seconds"],
            }
        )

    line_analysis = analyze_control_line(
        controls,
        time_match_tolerance=rules["time_match_tolerance"],
        adjacent_theta_sign_change=rules["adjacent_theta_sign_change"],
    )
    finished_utc = _utc_now()
    wall_seconds = time.perf_counter() - started
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "stage": STAGE,
        "status": ("DRY_RUN_COMPLETE" if run_mode == "dry_run" else "DISCOVERY_LINE_COMPLETE"),
        "run_mode": run_mode,
        "formal_frozen_run_completed": run_mode == "frozen_formal_discovery",
        "claim_scope": CLAIM_SCOPE,
        "continuum_verified": False,
        "project_gate_passed": False,
        "configuration": selected.to_dict(),
        "configuration_hash": configuration_hash,
        "provenance": provenance,
        "g1a_foundation_preflight": g1a_foundation_preflight,
        "manifest_status_at_run": manifest["status"],
        "candidate_rules": rules,
        "controls": controls,
        "line_candidate_analysis": line_analysis,
        "checkpoints": checkpoint_rows,
        "checkpoint_integrity_ledger": {
            "filename": ledger_path.name,
            "sha256": _sha256(ledger_path),
            "entry_count": len(checkpoint_ledger["entries"]),
        },
        "runtime": {
            "started_utc": started_utc,
            "finished_utc": finished_utc,
            "wall_seconds": wall_seconds,
            "controls_computed": computed_count,
            "controls_resumed": resumed_count,
            "maximum_chunk_points": selected.chunk_points,
            "full_state_history_stored": False,
        },
        "limitations": [
            "This is topology discovery, not continuum verification.",
            "Linear interpolation of sampled brackets is not a fold residual or root certificate.",
            "No control sensitivity, continuation, convergence, tail, or independent-method gate is run.",
            "A discovery flag can only freeze a candidate for a separately manifested confirmation stage.",
        ],
    }
    _atomic_write_json(output_path, result)
    return result


def run_discovery(
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    output_path: Path = DEFAULT_OUTPUT,
    checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR,
    configuration: RunConfiguration | None = None,
    run_mode: str,
    resume: bool = True,
) -> dict[str, Any]:
    """Run one discovery line while enforcing a single checkpoint writer."""

    if run_mode not in {"dry_run", "frozen_formal_discovery"}:
        raise ValueError("run_mode must be dry_run or frozen_formal_discovery")
    manifest, manifest_sha256 = load_and_validate_manifest(Path(manifest_path))
    frozen_configuration = RunConfiguration.from_manifest(manifest)
    selected = frozen_configuration if configuration is None else configuration
    selected.validate()
    if run_mode == "frozen_formal_discovery" and selected != frozen_configuration:
        raise ValueError("formal discovery configuration must exactly equal the frozen manifest")
    g1a_foundation_preflight = validate_g1a_foundation_artifact(manifest["required_g1a_foundation"])
    provenance = _provenance(
        Path(manifest_path),
        manifest_sha256,
        g1a_foundation_preflight,
    )
    if run_mode == "frozen_formal_discovery" and not provenance["running_in_repository_venv"]:
        raise RuntimeError("formal discovery must run inside the repository .venv")
    configuration_hash = _configuration_hash(selected, run_mode)
    with _single_writer_lock(
        Path(checkpoint_dir),
        run_mode=run_mode,
        configuration_hash=configuration_hash,
    ):
        return _run_discovery_locked(
            manifest_path=manifest_path,
            output_path=output_path,
            checkpoint_dir=checkpoint_dir,
            configuration=configuration,
            run_mode=run_mode,
            resume=resume,
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="run the small asymmetric implementation check",
    )
    mode.add_argument(
        "--execute-frozen",
        action="store_true",
        help="explicitly authorize the exact 65x65x49 frozen discovery line",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--checkpoint-dir", type=Path)
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="fail if any matching checkpoint already exists",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.dry_run:
        temporary_root: Path | None = None
        if args.output is None or args.checkpoint_dir is None:
            temporary_root = Path(tempfile.mkdtemp(prefix="continuum_g1_discovery_dry_"))
        output = args.output or temporary_root / "dry_run_result.json"
        checkpoint_dir = args.checkpoint_dir or temporary_root / "checkpoints"
        configuration = RunConfiguration.small_dry_run()
        run_mode = "dry_run"
    else:
        output = args.output or DEFAULT_OUTPUT
        checkpoint_dir = args.checkpoint_dir or DEFAULT_CHECKPOINT_DIR
        configuration = None
        run_mode = "frozen_formal_discovery"
    result = run_discovery(
        manifest_path=args.manifest,
        output_path=output,
        checkpoint_dir=checkpoint_dir,
        configuration=configuration,
        run_mode=run_mode,
        resume=not args.no_resume,
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "stage": result["stage"],
                "run_mode": result["run_mode"],
                "continuum_verified": result["continuum_verified"],
                "project_gate_passed": result["project_gate_passed"],
                "line_has_discovery_flag": result["line_candidate_analysis"][
                    "line_has_discovery_flag"
                ],
                "output": str(output),
                "output_sha256": _sha256(output),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
