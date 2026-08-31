#!/usr/bin/env python3
"""Validate and idempotently submit the frozen Isambard-AI v3 job chain.

The submission working directory is always the report root, making every
job's ``SLURM_SUBMIT_DIR`` the sole root of the remote payload.  The automatic
chain ends at the production reducer.  The frozen 160k tail manifest is kept
in state but is deliberately never submitted by this program.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Mapping, Sequence

MANIFEST_SCHEMA = "grid2d-one-two-target-gating-gpu-v3-manifest"
STATE_SCHEMA = "grid2d-one-two-target-gating-isambard-submission-state-v3"
STATE_VERSION = 3
REPORT_ROOT = Path(__file__).resolve().parents[1]
FIELD_PACK_RELATIVE = "artifacts/data/disorder_field_pack_v3.npz"
FIELD_PACK_MANIFEST_RELATIVE = "artifacts/data/disorder_field_pack_v3.manifest.json"
CANARY_MANIFEST_RELATIVE = "artifacts/data/gating_v3_canary_manifest.json"
PRODUCTION_MANIFEST_RELATIVE = "artifacts/data/gating_v3_production_manifest.json"
TAIL_MANIFEST_RELATIVE = "artifacts/data/gating_v3_tail160k_manifest.json"
PAYLOAD_SHA_RELATIVE = "notes/isambard_ai_v3_payload.sha256"
PAYLOAD_R2_ARCHIVE_RELATIVE = "notes/isambard_ai_v3_payload_r2.sha256"
CONTAINER_SHA_RELATIVE = "notes/isambard_ai_v3_container.sha256"
STATE_RELATIVE = "artifacts/outputs/isambard_ai_v3/submission/submission_state_v3.json"
LOCK_RELATIVE = "artifacts/outputs/isambard_ai_v3/submission/submission_state_v3.lock"
RUNNER_RELATIVE = "code/gpu_gating_mc_v3.py"
REDUCER_RELATIVE = "code/reduce_gpu_gating_v3.py"
CELL_SBATCH_RELATIVE = "code/isambard_ai_gating_v3_cell.sbatch"
ENVIRONMENT_SBATCH_RELATIVE = "code/isambard_ai_gating_v3_environment.sbatch"
REDUCE_SBATCH_RELATIVE = "code/isambard_ai_gating_v3_reduce.sbatch"
SUBMITTER_RELATIVE = "code/submit_isambard_ai_gating_v3.py"
EXACT_ORACLE_RELATIVE = "code/exact_homogeneous_oracle_v3.py"
ISAMBARD3_ORACLE_SBATCH_RELATIVE = "code/isambard3_exact_oracle_v3.sbatch"
SLURM_ARRAY_R2_NOTE_RELATIVE = "notes/isambard_ai_v3_slurm_array_r2.md"
BUNDLE_SBATCH_RELATIVE = "code/isambard_ai_gating_v3_bundle.sbatch"
SLURM_QOS_R3_NOTE_RELATIVE = "notes/isambard_ai_v3_slurm_qos_r3.md"
FIELD_GENERATOR_RELATIVE = "code/generate_disorder_field_pack_v3.py"
MANIFEST_BUILDER_RELATIVE = "code/build_gating_campaign_manifest_v3.py"
MANIFEST_VALIDATOR_RELATIVE = "code/validate_gating_campaign_manifest_v3.py"
PREREGISTERED_PROTOCOL_RELATIVE = "notes/isambard_ai_v3_preregistered_protocol.md"
FIELD_CONTRACT_RELATIVE = "notes/isambard_ai_v3_field_pack_manifest_contract.md"
MAX_ARRAY_SIZE_OBSERVED = 1_001
MAX_JOBS_PER_USER_OBSERVED = 256
MAX_SUBMIT_PER_USER_OBSERVED = 512
LIVE_EXPANDED_JOBS_BEFORE_V2_CANCEL = 15
CANCELLED_V2_GATING_JOBS = 10
R3_BASELINE_LIVE_JOBS = 5
R3_NEW_EXPANDED_JOBS = 491
R3_CONSERVATIVE_SUBMIT_UPPER_BOUND = R3_BASELINE_LIVE_JOBS + R3_NEW_EXPANDED_JOBS
PRODUCTION_ALLOCATION_COUNT = 480
PRODUCTION_LOCAL_MAX = PRODUCTION_ALLOCATION_COUNT - 1
PRODUCTION_CELLS_PER_ALLOCATION = 12
PRODUCTION_BUNDLE_STRIDE = 480
PRODUCTION_BUNDLE_OFFSETS = tuple(
    PRODUCTION_BUNDLE_STRIDE * index
    for index in range(PRODUCTION_CELLS_PER_ALLOCATION)
)
PRODUCTION_THROTTLE = 240
PAYLOAD_PATHS = tuple(
    sorted(
        (
            FIELD_PACK_RELATIVE,
            FIELD_PACK_MANIFEST_RELATIVE,
            CANARY_MANIFEST_RELATIVE,
            PRODUCTION_MANIFEST_RELATIVE,
            TAIL_MANIFEST_RELATIVE,
            CONTAINER_SHA_RELATIVE,
            RUNNER_RELATIVE,
            REDUCER_RELATIVE,
            CELL_SBATCH_RELATIVE,
            ENVIRONMENT_SBATCH_RELATIVE,
            REDUCE_SBATCH_RELATIVE,
            SUBMITTER_RELATIVE,
            EXACT_ORACLE_RELATIVE,
            ISAMBARD3_ORACLE_SBATCH_RELATIVE,
            SLURM_ARRAY_R2_NOTE_RELATIVE,
            BUNDLE_SBATCH_RELATIVE,
            SLURM_QOS_R3_NOTE_RELATIVE,
            FIELD_GENERATOR_RELATIVE,
            MANIFEST_BUILDER_RELATIVE,
            MANIFEST_VALIDATOR_RELATIVE,
            PREREGISTERED_PROTOCOL_RELATIVE,
            FIELD_CONTRACT_RELATIVE,
        )
    )
)
JOB_ORDER = (
    "environment",
    "canary_array",
    "canary_reducer",
    "production_array",
    "production_reducer",
)
JOB_ID_PATTERN = re.compile(r"^[1-9][0-9]*$")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-root",
        type=Path,
        default=REPORT_ROOT,
        help="Report root to use as the sbatch working directory and SLURM_SUBMIT_DIR.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the frozen payload and print the chain without writing or submitting.",
    )
    return parser.parse_args(argv)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root in {path} must be an object")
    return payload


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _sha256(value: Any, name: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise ValueError(f"{name} must be 64 hexadecimal digits")
    return value.lower()


def _relative_file(report_root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        raise ValueError(f"unsafe report-relative path: {relative!r}")
    candidate = (report_root / Path(*pure.parts)).resolve()
    try:
        candidate.relative_to(report_root)
    except ValueError as exc:
        raise ValueError(f"path escapes report root: {relative!r}") from exc
    if not candidate.is_file():
        raise FileNotFoundError(f"required payload file does not exist: {candidate}")
    return candidate


def _manifest_contract(
    *,
    report_root: Path,
    relative: str,
    expected_kind: str,
    expected_count: int,
    field_pack_sha256: str,
    field_sidecar_sha256: str,
    runner_sha256: str,
    container_reference: str,
    container_sha256: str,
) -> dict[str, Any]:
    path = _relative_file(report_root, relative)
    manifest = _load_json(path)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(f"{relative} has the wrong manifest schema")
    campaign = _mapping(manifest.get("campaign"), f"{relative}:campaign")
    if campaign.get("kind") != expected_kind:
        raise ValueError(
            f"{relative} campaign kind is {campaign.get('kind')!r}, expected {expected_kind!r}"
        )
    cells = manifest.get("cells")
    if not isinstance(cells, list) or len(cells) != expected_count:
        raise ValueError(f"{relative} must contain exactly {expected_count} cells")
    cell_ids: list[int] = []
    for index, cell_value in enumerate(cells):
        cell = _mapping(cell_value, f"{relative}:cells[{index}]")
        cell_id = cell.get("cell_id")
        if isinstance(cell_id, bool) or not isinstance(cell_id, int):
            raise ValueError(f"{relative}:cells[{index}].cell_id must be an integer")
        cell_ids.append(cell_id)
    if sorted(cell_ids) != list(range(expected_count)):
        raise ValueError(f"{relative} cell IDs must be exactly 0..{expected_count - 1}")
    if campaign.get("cell_count") != expected_count:
        raise ValueError(f"{relative} campaign.cell_count mismatch")
    if _sha256(manifest.get("field_pack_sha256"), f"{relative}:field_pack_sha256") != field_pack_sha256:
        raise ValueError(f"{relative} field-pack hash differs from the live field pack")
    artifacts = _mapping(manifest.get("artifacts"), f"{relative}:artifacts")
    field_record = _mapping(artifacts.get("field_pack"), f"{relative}:artifacts.field_pack")
    runner_record = _mapping(artifacts.get("runner_source"), f"{relative}:artifacts.runner_source")
    container_record = _mapping(artifacts.get("container"), f"{relative}:artifacts.container")
    if field_record.get("filename") != Path(FIELD_PACK_RELATIVE).name:
        raise ValueError(f"{relative} field-pack filename mismatch")
    if _sha256(field_record.get("sha256"), f"{relative}:field artifact") != field_pack_sha256:
        raise ValueError(f"{relative} field artifact hash mismatch")
    if _sha256(
        field_record.get("sidecar_sha256"), f"{relative}:field sidecar"
    ) != field_sidecar_sha256:
        raise ValueError(f"{relative} field sidecar hash mismatch")
    if runner_record.get("filename") != Path(RUNNER_RELATIVE).name:
        raise ValueError(f"{relative} runner filename mismatch")
    if _sha256(runner_record.get("sha256"), f"{relative}:runner") != runner_sha256:
        raise ValueError(f"{relative} runner hash mismatch")
    if container_record.get("reference") != container_reference:
        raise ValueError(f"{relative} container reference mismatch")
    if _sha256(container_record.get("sha256"), f"{relative}:container") != container_sha256:
        raise ValueError(f"{relative} container hash mismatch")
    if expected_kind == "tail160k":
        if campaign.get("activation_gate") != (
            "submit only when the verified 80k reducer tail gate is FAIL"
        ):
            raise ValueError("tail160k activation gate is not frozen")
        if any(cell.get("profile") != "tail_160k" for cell in cells):
            raise ValueError("every tail160k cell must select profile tail_160k")
    return {
        "path": relative,
        "sha256": _sha256_file(path),
        "campaign_kind": expected_kind,
        "cell_count": expected_count,
    }


def _container_contract(report_root: Path) -> tuple[str, str]:
    path = _relative_file(report_root, CONTAINER_SHA_RELATIVE)
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        raise ValueError("container SHA file must contain exactly one nonempty line")
    match = re.fullmatch(r"([0-9a-fA-F]{64})\s+(/\S+)", lines[0])
    if match is None:
        raise ValueError("container SHA file must use 'sha256  /absolute/container/path'")
    return match.group(2), match.group(1).lower()


def validate_inputs(report_root: Path) -> tuple[dict[str, Any], bytes]:
    report_root = report_root.resolve()
    if not report_root.is_dir():
        raise FileNotFoundError(f"report root does not exist: {report_root}")
    for relative in PAYLOAD_PATHS:
        _relative_file(report_root, relative)

    field_pack_path = _relative_file(report_root, FIELD_PACK_RELATIVE)
    field_pack_sha256 = _sha256_file(field_pack_path)
    field_sidecar_path = _relative_file(report_root, FIELD_PACK_MANIFEST_RELATIVE)
    field_sidecar_sha256 = _sha256_file(field_sidecar_path)
    field_sidecar = _load_json(field_sidecar_path)
    pack_record = _mapping(field_sidecar.get("pack"), "field-pack sidecar:pack")
    if pack_record.get("filename") != field_pack_path.name:
        raise ValueError("field-pack sidecar filename mismatch")
    if _sha256(pack_record.get("sha256"), "field-pack sidecar:pack.sha256") != field_pack_sha256:
        raise ValueError("field-pack sidecar does not match the live NPZ")

    runner_sha256 = _sha256_file(_relative_file(report_root, RUNNER_RELATIVE))
    container_reference, container_sha256 = _container_contract(report_root)
    common = {
        "report_root": report_root,
        "field_pack_sha256": field_pack_sha256,
        "field_sidecar_sha256": field_sidecar_sha256,
        "runner_sha256": runner_sha256,
        "container_reference": container_reference,
        "container_sha256": container_sha256,
    }
    canary = _manifest_contract(
        relative=CANARY_MANIFEST_RELATIVE,
        expected_kind="canary",
        expected_count=8,
        **common,
    )
    production = _manifest_contract(
        relative=PRODUCTION_MANIFEST_RELATIVE,
        expected_kind="production",
        expected_count=5_760,
        **common,
    )
    tail = _manifest_contract(
        relative=TAIL_MANIFEST_RELATIVE,
        expected_kind="tail160k",
        expected_count=384,
        **common,
    )

    payload_lines = [
        f"{_sha256_file(_relative_file(report_root, relative))}  {relative}\n"
        for relative in PAYLOAD_PATHS
    ]
    payload_bytes = "".join(payload_lines).encode("utf-8")
    contract = {
        "payload_sha_file": {
            "path": PAYLOAD_SHA_RELATIVE,
            "sha256": _sha256_bytes(payload_bytes),
            "member_count": len(PAYLOAD_PATHS),
        },
        "field_pack": {
            "path": FIELD_PACK_RELATIVE,
            "sha256": field_pack_sha256,
            "sidecar_path": FIELD_PACK_MANIFEST_RELATIVE,
            "sidecar_sha256": field_sidecar_sha256,
        },
        "runner": {"path": RUNNER_RELATIVE, "sha256": runner_sha256},
        "reducer": {
            "path": REDUCER_RELATIVE,
            "sha256": _sha256_file(_relative_file(report_root, REDUCER_RELATIVE)),
        },
        "container": {
            "reference": container_reference,
            "sha256": container_sha256,
            "receipt_path": CONTAINER_SHA_RELATIVE,
        },
        "canary_manifest": canary,
        "production_manifest": production,
        "tail160k_manifest": tail,
        "slurm_array_split_r2": {
            "note_path": SLURM_ARRAY_R2_NOTE_RELATIVE,
            "note_sha256": _sha256_file(
                _relative_file(report_root, SLURM_ARRAY_R2_NOTE_RELATIVE)
            ),
            "status": "superseded_before_submission",
        },
        "slurm_qos_bundle_r3": {
            "note_path": SLURM_QOS_R3_NOTE_RELATIVE,
            "note_sha256": _sha256_file(
                _relative_file(report_root, SLURM_QOS_R3_NOTE_RELATIVE)
            ),
            "max_array_size_observed": MAX_ARRAY_SIZE_OBSERVED,
            "max_jobs_per_user_observed": MAX_JOBS_PER_USER_OBSERVED,
            "max_submit_per_user_observed": MAX_SUBMIT_PER_USER_OBSERVED,
            "live_expanded_jobs_before_v2_cancel": LIVE_EXPANDED_JOBS_BEFORE_V2_CANCEL,
            "cancelled_v2_gating_jobs": CANCELLED_V2_GATING_JOBS,
            "r3_baseline_live_jobs": R3_BASELINE_LIVE_JOBS,
            "r3_new_expanded_jobs": R3_NEW_EXPANDED_JOBS,
            "r3_conservative_submit_upper_bound": R3_CONSERVATIVE_SUBMIT_UPPER_BOUND,
            "local_task_range": [0, PRODUCTION_LOCAL_MAX],
            "allocation_count": PRODUCTION_ALLOCATION_COUNT,
            "cells_per_allocation": PRODUCTION_CELLS_PER_ALLOCATION,
            "bundle_offsets": list(PRODUCTION_BUNDLE_OFFSETS),
            "array_throttle": PRODUCTION_THROTTLE,
            "active_production_gpu_max": PRODUCTION_THROTTLE,
        },
    }
    return contract, payload_bytes


def _atomic_write_new(path: Path, data: bytes) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise FileExistsError(f"refusing to overwrite existing file: {path}") from exc
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        temporary.unlink(missing_ok=True)


def ensure_payload_sha(report_root: Path, expected: bytes, *, create: bool) -> str:
    path = report_root / PAYLOAD_SHA_RELATIVE
    if path.exists():
        actual = path.read_bytes()
        if actual != expected:
            archive = report_root / PAYLOAD_R2_ARCHIVE_RELATIVE
            if archive.is_file() and actual == archive.read_bytes():
                if not create:
                    return "would_replace_archived_r2"
                _atomic_replace_bytes(path, expected)
                return "replaced_archived_r2"
            raise ValueError(f"payload SHA inventory is stale or noncanonical: {path}")
        return "validated_existing"
    if not create:
        return "would_create"
    _atomic_write_new(path, expected)
    return "created_new"


def _atomic_replace_bytes(path: Path, data: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        temporary.unlink(missing_ok=True)


def _json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
        "utf-8"
    )


def _atomic_replace_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _json_bytes(payload)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def exclusive_state_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _new_state(contract: Mapping[str, Any]) -> dict[str, Any]:
    now = _utc_now()
    return {
        "schema": STATE_SCHEMA,
        "state_version": STATE_VERSION,
        "revision": 0,
        "created_utc": now,
        "updated_utc": now,
        "input_contract": dict(contract),
        "slurm_submit_dir_policy": "sbatch_process_cwd_equals_report_root",
        "dependency_policy": "afterok_only",
        "jobs": {},
        "events": [],
        "tail160k": {
            "manifest": dict(contract["tail160k_manifest"]),
            "status": "frozen_not_submitted",
            "automatic_submission": False,
            "activation_gate": "only after verified 80k reducer tail gate failure",
        },
    }


def _validate_state(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    if state.get("schema") != STATE_SCHEMA or state.get("state_version") != STATE_VERSION:
        raise ValueError("submission state schema/version mismatch")
    if state.get("input_contract") != contract:
        raise ValueError("submission state input hashes differ from the live frozen payload")
    if _mapping(state.get("tail160k"), "state.tail160k").get("status") != (
        "frozen_not_submitted"
    ):
        raise ValueError("tail160k state must remain frozen_not_submitted")
    jobs = _mapping(state.get("jobs"), "state.jobs")
    unexpected = set(jobs) - set(JOB_ORDER)
    if unexpected:
        raise ValueError(f"submission state contains unexpected jobs: {sorted(unexpected)}")
    seen_gap = False
    verified_job_ids: dict[str, str] = {}
    for name in JOB_ORDER:
        if name not in jobs:
            seen_gap = True
            continue
        if seen_gap:
            raise ValueError("submission state job chain has a gap")
        record = _mapping(jobs[name], f"state.jobs.{name}")
        job_id = record.get("job_id")
        if not isinstance(job_id, str) or JOB_ID_PATTERN.fullmatch(job_id) is None:
            raise ValueError(f"state.jobs.{name}.job_id is invalid")
        expected_argv = _stage_argv(name, verified_job_ids)
        if record.get("argv") != expected_argv:
            raise ValueError(f"state.jobs.{name}.argv differs from the frozen chain")
        expected_dependency = next(
            (
                argument.removeprefix("--dependency=afterok:")
                for argument in expected_argv
                if argument.startswith("--dependency=afterok:")
            ),
            None,
        )
        if record.get("dependency_afterok") != expected_dependency:
            raise ValueError(f"state.jobs.{name} afterok dependency mismatch")
        verified_job_ids[name] = job_id


def _load_state(path: Path, contract: Mapping[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return _new_state(contract)
    state = _load_json(path)
    _validate_state(state, contract)
    return state


def _commit_state(
    path: Path,
    state: dict[str, Any],
    *,
    action: str,
    details: Mapping[str, Any],
) -> None:
    revision = state.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise ValueError("state revision must be a nonnegative integer")
    revision += 1
    now = _utc_now()
    state["revision"] = revision
    state["updated_utc"] = now
    events = state.get("events")
    if not isinstance(events, list):
        raise ValueError("state events must be an array")
    events.append(
        {
            "revision": revision,
            "utc": now,
            "action": action,
            "details": dict(details),
        }
    )
    _atomic_replace_json(path, state)


def _stage_argv(stage: str, job_ids: Mapping[str, str]) -> list[str]:
    if stage == "environment":
        return ["sbatch", "--parsable", ENVIRONMENT_SBATCH_RELATIVE]
    if stage == "canary_array":
        return [
            "sbatch",
            "--parsable",
            f"--dependency=afterok:{job_ids['environment']}",
            "--array=0-7%8",
            CELL_SBATCH_RELATIVE,
            CANARY_MANIFEST_RELATIVE,
            FIELD_PACK_RELATIVE,
            "canary",
            "0",
            job_ids["environment"],
        ]
    if stage == "canary_reducer":
        return [
            "sbatch",
            "--parsable",
            f"--dependency=afterok:{job_ids['canary_array']}",
            REDUCE_SBATCH_RELATIVE,
            "inventory",
            CANARY_MANIFEST_RELATIVE,
            FIELD_PACK_RELATIVE,
            "canary",
            job_ids["environment"],
            job_ids["canary_array"],
            "8",
        ]
    if stage == "production_array":
        return [
            "sbatch",
            "--parsable",
            f"--dependency=afterok:{job_ids['canary_reducer']}",
            f"--array=0-{PRODUCTION_LOCAL_MAX}%{PRODUCTION_THROTTLE}",
            BUNDLE_SBATCH_RELATIVE,
            PRODUCTION_MANIFEST_RELATIVE,
            FIELD_PACK_RELATIVE,
            "production",
            job_ids["environment"],
        ]
    if stage == "production_reducer":
        return [
            "sbatch",
            "--parsable",
            f"--dependency=afterok:{job_ids['production_array']}",
            REDUCE_SBATCH_RELATIVE,
            "full",
            PRODUCTION_MANIFEST_RELATIVE,
            FIELD_PACK_RELATIVE,
            "production",
            job_ids["environment"],
            job_ids["production_array"],
            "5760",
        ]
    raise ValueError(f"unknown submission stage: {stage}")


def _submit_one(report_root: Path, argv: Sequence[str]) -> str:
    sbatch = shutil.which("sbatch")
    if sbatch is None:
        raise RuntimeError("sbatch is not available on PATH")
    effective = [sbatch, *argv[1:]]
    completed = subprocess.run(
        effective,
        cwd=report_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"sbatch failed with exit {completed.returncode}: {completed.stderr.strip()}"
        )
    stdout = completed.stdout.strip()
    job_id = stdout.split(";", 1)[0]
    if JOB_ID_PATTERN.fullmatch(job_id) is None:
        raise RuntimeError(f"unexpected sbatch --parsable output: {stdout!r}")
    return job_id


def _production_coverage_record() -> dict[str, Any]:
    cells = [
        offset + local_task
        for local_task in range(PRODUCTION_ALLOCATION_COUNT)
        for offset in PRODUCTION_BUNDLE_OFFSETS
    ]
    expected = set(range(5_760))
    actual = set(cells)
    duplicates = len(cells) - len(actual)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    passed = (
        max(range(PRODUCTION_ALLOCATION_COUNT)) <= PRODUCTION_LOCAL_MAX
        and PRODUCTION_LOCAL_MAX < MAX_ARRAY_SIZE_OBSERVED
        and duplicates == 0
        and not missing
        and not unexpected
        and len(cells) == 5_760
    )
    if not passed:
        raise ValueError("frozen r3 production bundles do not cover cell IDs 0..5759 exactly")
    return {
        "passed": True,
        "bundle_offsets": list(PRODUCTION_BUNDLE_OFFSETS),
        "allocation_count": PRODUCTION_ALLOCATION_COUNT,
        "cells_per_allocation": PRODUCTION_CELLS_PER_ALLOCATION,
        "local_task_min": 0,
        "local_task_max": PRODUCTION_LOCAL_MAX,
        "max_array_size_observed": MAX_ARRAY_SIZE_OBSERVED,
        "global_cell_min": min(cells),
        "global_cell_max": max(cells),
        "global_cell_count": len(cells),
        "duplicate_count": duplicates,
        "missing_count": len(missing),
        "unexpected_count": len(unexpected),
        "array_throttle": PRODUCTION_THROTTLE,
        "active_production_gpu_max": PRODUCTION_THROTTLE,
        "max_jobs_per_user_observed": MAX_JOBS_PER_USER_OBSERVED,
        "max_submit_per_user_observed": MAX_SUBMIT_PER_USER_OBSERVED,
        "live_expanded_jobs_before_v2_cancel": LIVE_EXPANDED_JOBS_BEFORE_V2_CANCEL,
        "cancelled_v2_gating_jobs": CANCELLED_V2_GATING_JOBS,
        "r3_baseline_live_jobs": R3_BASELINE_LIVE_JOBS,
        "r3_new_expanded_jobs": R3_NEW_EXPANDED_JOBS,
        "r3_conservative_submit_upper_bound": R3_CONSERVATIVE_SUBMIT_UPPER_BOUND,
        "submit_headroom": MAX_SUBMIT_PER_USER_OBSERVED
        - R3_CONSERVATIVE_SUBMIT_UPPER_BOUND,
    }


def dry_run_plan(
    report_root: Path, contract: Mapping[str, Any], payload_action: str
) -> dict[str, Any]:
    placeholders: dict[str, str] = {}
    stages = []
    for stage in JOB_ORDER:
        argv = _stage_argv(stage, placeholders)
        stages.append({"stage": stage, "argv": argv})
        placeholders[stage] = f"<{stage}_job_id>"
    return {
        "schema": STATE_SCHEMA,
        "dry_run": True,
        "report_root": str(report_root),
        "slurm_submit_dir": str(report_root),
        "payload_sha_action": payload_action,
        "input_contract": contract,
        "stages": stages,
        "dependency_policy": "afterok_only",
        "production_split": _production_coverage_record(),
        "tail160k": {
            "manifest": contract["tail160k_manifest"],
            "status": "frozen_not_submitted",
        },
    }


def submit_chain(report_root: Path) -> dict[str, Any]:
    report_root = report_root.resolve()
    state_path = report_root / STATE_RELATIVE
    lock_path = report_root / LOCK_RELATIVE
    with exclusive_state_lock(lock_path):
        contract, payload_bytes = validate_inputs(report_root)
        payload_action = ensure_payload_sha(report_root, payload_bytes, create=True)
        state = _load_state(state_path, contract)
        if not state_path.exists():
            _commit_state(
                state_path,
                state,
                action="initialized",
                details={"payload_sha_action": payload_action},
            )
        else:
            _validate_state(state, contract)

        (report_root / "logs").mkdir(parents=True, exist_ok=True)
        jobs = state["jobs"]
        job_ids: dict[str, str] = {
            name: record["job_id"] for name, record in jobs.items()
        }
        for stage in JOB_ORDER:
            if stage in jobs:
                continue
            argv = _stage_argv(stage, job_ids)
            job_id = _submit_one(report_root, argv)
            dependency = next(
                (
                    argument.removeprefix("--dependency=afterok:")
                    for argument in argv
                    if argument.startswith("--dependency=afterok:")
                ),
                None,
            )
            record = {
                "job_id": job_id,
                "submitted_utc": _utc_now(),
                "dependency_afterok": dependency,
                "argv": argv,
            }
            jobs[stage] = record
            job_ids[stage] = job_id
            _commit_state(
                state_path,
                state,
                action="submitted_job",
                details={"stage": stage, "job_id": job_id},
            )
        _validate_state(state, contract)
        return state


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report_root = args.report_root.resolve()
    try:
        if args.dry_run:
            contract, payload_bytes = validate_inputs(report_root)
            payload_action = ensure_payload_sha(
                report_root, payload_bytes, create=False
            )
            print(
                json.dumps(
                    dry_run_plan(report_root, contract, payload_action),
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        state = submit_chain(report_root)
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(f"FAIL-CLOSED: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "schema": state["schema"],
                "revision": state["revision"],
                "jobs": {
                    name: state["jobs"][name]["job_id"] for name in JOB_ORDER
                },
                "state": str(report_root / STATE_RELATIVE),
                "tail160k": state["tail160k"]["status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
