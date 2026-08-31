#!/usr/bin/env python3
"""Login-node H6 terminal audit with exact candidate-byte binding."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
from pathlib import Path
from typing import Any, Callable, Mapping

import provision_gpu_gating_v4_r2_h5 as provision
import scientific_tail_replay_v4_r2_h2 as science
import terminal_audit_gpu_gating_v4_r2_h5 as h5

ROOT = h5.ROOT
H6_PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h6_payload.sha256"
CONTROLLER_SCRIPT = "terminal_audit_gpu_gating_v4_r2_h6.py"
CONTROLLER_WALLTIME_LIMIT_SECONDS = h5.CONTROLLER_WALLTIME_LIMIT_SECONDS
FINAL_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h6-final-release-v1"
FINAL_STATUS = "PASS_AUTHORIZE_H6_SCIENTIFIC_INFERENCE"
FINAL_KEYS = {
    "schema", "status", "h6_payload_manifest_sha256",
    "h5_payload_manifest_sha256", "h4_payload_manifest_sha256", "jobs",
    "provisional_candidate", "release_terminal_receipt",
    "release_submission", "release_runtime", "h4_full_recomputation",
    "controller", "authorizes_scientific_release",
}

# The H5 scheduler and immutable-receipt gates remain the H6 implementation.
RELEASE_JOB_NAME = h5.RELEASE_JOB_NAME
ACCOUNT = h5.ACCOUNT
PARTITION = h5.PARTITION
SACCT_FIELDS = h5.SACCT_FIELDS
SACCT_FORMAT = h5.SACCT_FORMAT
WAIT_STATES = h5.WAIT_STATES
FAIL_STATES = h5.FAIL_STATES
query_release_sacct = h5.query_release_sacct
parse_one_row = h5.parse_one_row
state_token = h5.state_token
tres_map = h5.tres_map
exact_release_identity = h5.exact_release_identity
terminal_gate = h5.terminal_gate
canonical_sacct_bytes = h5.canonical_sacct_bytes
exclusive_directory_lock = h5.exclusive_directory_lock
terminal_dir = h5.terminal_dir
ensure_terminal_receipt = h5.ensure_terminal_receipt


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def discover_candidate(
    *, array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, release_job: str,
) -> tuple[Path, str, dict[str, Any]]:
    """Discover one content-addressed candidate before semantic validation."""
    directory = provision.candidate_dir(
        array_job, reducer_job, replay_job, combined_job, release_job)
    req(directory.is_dir() and not directory.is_symlink(),
        "H6 provisional candidate directory missing/unsafe")
    candidates = list(directory.glob("candidate-*.json"))
    req(len(candidates) == 1, "H6 provisional candidate uniqueness drift")
    path = candidates[0]
    match = re.fullmatch(r"candidate-([0-9a-f]{64})\.json", path.name)
    req(match is not None and science.sha(path) == match.group(1),
        "H6 provisional candidate content-address drift")
    return path, match.group(1), science.strict_json(path, mode600=True)


def validate_candidate(
    candidate: Mapping[str, Any], *, candidate_path: Path,
    candidate_sha: str, expected_full: Mapping[str, Any], h5_sha: str,
    h4_sha: str,
) -> None:
    """Require H5 semantics, then exact producer-canonical source bytes."""
    h5.validate_candidate(
        candidate, expected_full=expected_full, h5_sha=h5_sha, h4_sha=h4_sha)
    expected_candidate = provision.candidate_payload(
        expected_full, h5_sha=h5_sha, h4_sha=h4_sha)
    expected_raw = provision.canonical_bytes(expected_candidate)
    actual_raw = candidate_path.read_bytes()
    req(actual_raw == expected_raw,
        "H6 provisional candidate raw canonical-byte drift")
    req(hashlib.sha256(expected_raw).hexdigest() == candidate_sha,
        "H6 provisional candidate canonical digest drift")


def final_dir(jobs: Mapping[str, str]) -> Path:
    h5.h4.decimal(jobs["array"], jobs["reducer"], jobs["replay"],
                  jobs["combined"], jobs["release"])
    return ROOT / (
        "artifacts/releases_h6/final/"
        f"array-{jobs['array']}-reducer-{jobs['reducer']}-"
        f"replay-{jobs['replay']}-combined-{jobs['combined']}-"
        f"release-{jobs['release']}"
    )


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(
        payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def write_final(payload: Mapping[str, Any]) -> tuple[Path, str, bool]:
    raw = canonical_json_bytes(payload)
    digest = hashlib.sha256(raw).hexdigest()
    directory = final_dir(payload["jobs"])
    terminal_sha = payload["release_terminal_receipt"]["sha256"]
    req(science.HEX64.fullmatch(terminal_sha) is not None,
        "H6 final terminal receipt digest drift")
    path = directory / f"final-terminal-{terminal_sha}-authority-{digest}.json"
    with exclusive_directory_lock(directory, ".final-authority.lock"):
        existing = list(directory.glob("final-terminal-*-authority-*.json"))
        if existing:
            req(len(existing) == 1 and existing[0] == path
                and existing[0].read_bytes() == raw
                and science.sha(existing[0]) == digest,
                "H6 final authority uniqueness/content drift")
            return path, digest, False
        descriptor = os.open(
            path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        req(science.sha(path) == digest,
            "H6 final content-address verification failed")
        return path, digest, True


def controller_record() -> dict[str, Any]:
    path = Path(__file__).resolve().parent / CONTROLLER_SCRIPT
    return {
        "execution_surface": "login_node_single_shot_no_poll",
        "script": {"path": f"code/{CONTROLLER_SCRIPT}",
                   "sha256": science.sha(path)},
        "walltime_limit_seconds": CONTROLLER_WALLTIME_LIMIT_SECONDS,
        "slurm_node_hours": 0.0,
        "submits_slurm_job": False,
    }


def final_payload(
    *, h6_sha: str, h5_sha: str, h4_sha: str,
    expected_full: Mapping[str, Any], candidate_path: Path,
    candidate_sha: str, terminal_path: Path, terminal_sha: str,
    terminal_row: Mapping[str, str],
) -> dict[str, Any]:
    release_submission = provision.release_submission_path()
    release_runtime = provision.release_runtime_path(
        expected_full["jobs"]["release"])
    payload = {
        "schema": FINAL_SCHEMA,
        "status": FINAL_STATUS,
        "h6_payload_manifest_sha256": h6_sha,
        "h5_payload_manifest_sha256": h5_sha,
        "h4_payload_manifest_sha256": h4_sha,
        "jobs": dict(expected_full["jobs"]),
        "provisional_candidate": {
            "path": str(candidate_path), "sha256": candidate_sha,
            "status": provision.CANDIDATE_STATUS,
            "authorizes_scientific_release": False,
        },
        "release_terminal_receipt": {
            "path": str(terminal_path), "sha256": terminal_sha,
            "fields": dict(terminal_row),
        },
        "release_submission": {
            "path": str(release_submission),
            "sha256": science.sha(release_submission),
        },
        "release_runtime": {
            "path": str(release_runtime), "sha256": science.sha(release_runtime),
        },
        "h4_full_recomputation": dict(expected_full),
        "controller": controller_record(),
        "authorizes_scientific_release": True,
    }
    req(set(payload) == FINAL_KEYS,
        "H6 final authority internal exact-key drift")
    return payload


def audit(
    *, h6_sha: str, h5_sha: str, h4_sha: str, array_job: str,
    reducer_job: str, replay_job: str, combined_job: str, release_job: str,
    v3_sha: str, replay_sha: str, replay_submit_sha: str,
    combined_submit_sha: str, combined_json_sha: str, combined_csv_sha: str,
    query: Callable[[str], str] = query_release_sacct,
) -> dict[str, Any]:
    h5.h4.decimal(array_job, reducer_job, replay_job, combined_job, release_job)
    req(science.sha(H6_PAYLOAD) == h6_sha,
        "H6 terminal controller payload drift")
    req(science.sha(provision.H5_PAYLOAD) == h5_sha,
        "H6 terminal controller frozen H5 payload drift")
    req(science.sha(provision.H4_PAYLOAD) == h4_sha,
        "H6 terminal controller frozen H4 payload drift")
    submission = provision.validate_release_submission(
        h5_sha=h5_sha, h4_sha=h4_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job, release_job=release_job, v3_sha=v3_sha,
        replay_sha=replay_sha, replay_submit_sha=replay_submit_sha,
        combined_submit_sha=combined_submit_sha,
        combined_json_sha=combined_json_sha, combined_csv_sha=combined_csv_sha,
    )
    decision, row = terminal_gate(
        query(release_job), release_job=release_job, submission=submission)
    if decision == "WAIT":
        return {
            "status": "WAIT_RELEASE_NOT_TERMINAL", "release_job_id": release_job,
            "observed_state": state_token(row["State"]), "retry_safe": True,
            "wrote_terminal_receipt": False, "wrote_final_authority": False,
        }
    terminal_receipt, terminal_sha = ensure_terminal_receipt(
        row, array_job=array_job, reducer_job=reducer_job,
        replay_job=replay_job, combined_job=combined_job,
        release_job=release_job,
    )
    expected_full = provision.full_recomputation(
        h5_sha=h5_sha, h4_sha=h4_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job, release_job=release_job, v3_sha=v3_sha,
        replay_sha=replay_sha, replay_submit_sha=replay_submit_sha,
        combined_submit_sha=combined_submit_sha,
        combined_json_sha=combined_json_sha, combined_csv_sha=combined_csv_sha,
    )
    candidate_path, candidate_sha, candidate = discover_candidate(
        array_job=array_job, reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job, release_job=release_job,
    )
    validate_candidate(
        candidate, candidate_path=candidate_path, candidate_sha=candidate_sha,
        expected_full=expected_full, h5_sha=h5_sha, h4_sha=h4_sha)
    payload = final_payload(
        h6_sha=h6_sha, h5_sha=h5_sha, h4_sha=h4_sha,
        expected_full=expected_full, candidate_path=candidate_path,
        candidate_sha=candidate_sha, terminal_path=terminal_receipt,
        terminal_sha=terminal_sha, terminal_row=row,
    )
    output, digest, created = write_final(payload)
    return {
        "status": payload["status"] if created else "PASS_EXISTING_FINAL_VERIFIED",
        "final_authority": str(output), "sha256": digest,
        "created": created, "authorizes_scientific_release": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h6-payload-sha256", required=True)
    parser.add_argument("--h5-payload-sha256", required=True)
    parser.add_argument("--h4-payload-sha256", required=True)
    parser.add_argument("--array-job", required=True)
    parser.add_argument("--reducer-job", required=True)
    parser.add_argument("--replay-job", required=True)
    parser.add_argument("--combined-job", required=True)
    parser.add_argument("--release-job", required=True)
    parser.add_argument("--v3-release-sha256", required=True)
    parser.add_argument("--v4-replay-sha256", required=True)
    parser.add_argument("--replay-submission-sha256", required=True)
    parser.add_argument("--combined-submission-sha256", required=True)
    parser.add_argument("--combined-json-sha256", required=True)
    parser.add_argument("--combined-csv-sha256", required=True)
    args = parser.parse_args()
    signal.signal(
        signal.SIGALRM,
        lambda _signum, _frame: (_ for _ in ()).throw(
            TimeoutError("H6 terminal controller 1800s walltime limit exceeded")),
    )
    signal.alarm(CONTROLLER_WALLTIME_LIMIT_SECONDS)
    try:
        result = audit(
            h6_sha=args.h6_payload_sha256, h5_sha=args.h5_payload_sha256,
            h4_sha=args.h4_payload_sha256, array_job=args.array_job,
            reducer_job=args.reducer_job, replay_job=args.replay_job,
            combined_job=args.combined_job, release_job=args.release_job,
            v3_sha=args.v3_release_sha256, replay_sha=args.v4_replay_sha256,
            replay_submit_sha=args.replay_submission_sha256,
            combined_submit_sha=args.combined_submission_sha256,
            combined_json_sha=args.combined_json_sha256,
            combined_csv_sha=args.combined_csv_sha256,
        )
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    finally:
        signal.alarm(0)
    print(json.dumps(result, sort_keys=True))
    return 75 if result["status"] == "WAIT_RELEASE_NOT_TERMINAL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
