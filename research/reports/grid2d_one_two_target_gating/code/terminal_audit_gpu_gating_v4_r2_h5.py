#!/usr/bin/env python3
"""Login-node H5 terminal audit; the sole writer of final true authority."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import csv
import fcntl
import hashlib
import io
import json
import os
import re
import signal
import stat
import subprocess
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

import analyze_gpu_gating_v4_r2_combined_h4 as h4
import provision_gpu_gating_v4_r2_h5 as provision
import runtime_probe_v4_r2_h5 as runtime_h5
import scientific_tail_replay_v4_r2_h2 as science

ROOT = provision.ROOT
CONTROLLER_SCRIPT = "terminal_audit_gpu_gating_v4_r2_h5.py"
CONTROLLER_WALLTIME_LIMIT_SECONDS = 1800
RELEASE_JOB_NAME = "vk-gating-v4-r2-release-h5"
ACCOUNT = "brics.b5dj"
PARTITION = "workq"
SACCT_FIELDS = [
    "JobIDRaw", "JobID", "JobName", "Account", "Partition", "State",
    "ExitCode", "ElapsedRaw", "AllocTRES", "ReqTRES", "NNodes",
    "WorkDir", "SubmitLine",
]
SACCT_FORMAT = (
    "JobIDRaw,JobID,JobName%64,Account%64,Partition%64,State,ExitCode,"
    "ElapsedRaw,AllocTRES%256,ReqTRES%256,NNodes,WorkDir%512,SubmitLine%2048"
)
WAIT_STATES = {
    "PENDING", "RUNNING", "CONFIGURING", "COMPLETING", "REQUEUED",
    "RESIZING", "SUSPENDED", "STAGE_OUT",
}
FAIL_STATES = {
    "FAILED", "TIMEOUT", "NODE_FAIL", "OUT_OF_MEMORY", "OOM",
    "CANCELLED", "DEADLINE", "BOOT_FAIL", "PREEMPTED", "REVOKED",
}
FINAL_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h5-final-release-v1"
FINAL_STATUS = "PASS_AUTHORIZE_H5_SCIENTIFIC_INFERENCE"
FINAL_KEYS = {
    "schema", "status", "h5_payload_manifest_sha256",
    "h4_payload_manifest_sha256", "jobs", "provisional_candidate",
    "release_terminal_receipt", "release_submission", "release_runtime",
    "h4_full_recomputation", "controller",
    "authorizes_scientific_release",
}


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def query_release_sacct(release_job: str) -> str:
    completed = subprocess.run(
        ["sacct", "-X", "-j", release_job, f"--format={SACCT_FORMAT}",
         "--parsable2"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    return completed.stdout


def parse_one_row(raw: str) -> dict[str, str]:
    with io.StringIO(raw, newline="") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        rows = list(reader); header = reader.fieldnames
    req(header == SACCT_FIELDS and len(rows) == 1,
        "H5 release sacct exact header/parent-row drift")
    row = rows[0]
    req(set(row) == set(SACCT_FIELDS)
        and all(isinstance(value, str) for value in row.values()),
        "H5 release sacct row shape drift")
    return row


def state_token(state: str) -> str:
    return state.split("+", 1)[0].split(" ", 1)[0]


def tres_map(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for token in value.split(","):
        key, separator, item = token.partition("=")
        req(bool(separator) and key not in result and bool(item),
            "H5 release TRES token drift")
        result[key] = item
    return result


def exact_release_identity(
    row: Mapping[str, str], *, release_job: str,
    submission: Mapping[str, Any], require_resources: bool,
) -> None:
    req(row["JobIDRaw"] == release_job and row["JobID"] == release_job,
        "H5 release sacct wrong job identity")
    req(row["JobName"] == RELEASE_JOB_NAME and row["Account"] == ACCOUNT
        and row["Partition"] == PARTITION,
        "H5 release sacct job/account/partition drift")
    req(row["WorkDir"] == str(ROOT), "H5 release sacct WorkDir drift")
    req(row["SubmitLine"] == submission["submit_line"],
        "H5 release sacct SubmitLine drift")
    if require_resources:
        req(int(row["ElapsedRaw"]) > 0 and int(row["NNodes"]) == 1,
            "H5 release sacct elapsed/node drift")
        allocated = tres_map(row["AllocTRES"])
        requested = tres_map(row["ReqTRES"])
        expected_tres_keys = {"billing", "cpu", "mem", "node"}
        req(set(allocated) == expected_tres_keys
            and set(requested) == expected_tres_keys
            and allocated.get("billing") == "32"
            and requested.get("billing") == "32"
            and allocated.get("cpu") == "32" and requested.get("cpu") == "32"
            and allocated.get("node") == "1" and requested.get("node") == "1"
            and allocated.get("mem") in {"128G", "131072M"}
            and requested.get("mem") in {"128G", "131072M"},
            "H5 release sacct AllocTRES/ReqTRES drift")


def terminal_gate(
    raw: str, *, release_job: str, submission: Mapping[str, Any],
) -> tuple[str, dict[str, str]]:
    """Return WAIT or PASS; every terminal failure raises before candidate reads."""
    row = parse_one_row(raw)
    exact_release_identity(
        row, release_job=release_job, submission=submission,
        require_resources=False)
    state = state_token(row["State"])
    if state in WAIT_STATES:
        req(row["ExitCode"] == "0:0",
            "H5 nonterminal release has an unexpected exit code")
        return "WAIT", row
    if state in FAIL_STATES:
        raise ValueError(f"H5 release terminal failure state: {state}")
    req(row["State"] == "COMPLETED" and row["ExitCode"] == "0:0",
        "H5 release is not exact terminal COMPLETED/0:0")
    exact_release_identity(
        row, release_job=release_job, submission=submission,
        require_resources=True)
    return "PASS", row


def canonical_sacct_bytes(row: Mapping[str, str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=SACCT_FIELDS, delimiter="|", lineterminator="\n")
    writer.writeheader(); writer.writerow(dict(row))
    return buffer.getvalue().encode()


@contextmanager
def exclusive_directory_lock(directory: Path, name: str) -> Iterator[None]:
    """Serialize the one-authority invariant for one immutable job tuple."""
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    req(directory.is_dir() and not directory.is_symlink(),
        "H5 authority directory missing/unsafe")
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(directory / name, flags, 0o600)
    try:
        metadata = os.fstat(descriptor)
        req(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1
            and metadata.st_mode & 0o777 == 0o600,
            "H5 authority lock is unsafe")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def terminal_dir(
    array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, release_job: str,
) -> Path:
    h4.decimal(array_job, reducer_job, replay_job, combined_job, release_job)
    return ROOT / (
        "artifacts/releases_h5/release_terminal/"
        f"array-{array_job}-reducer-{reducer_job}-replay-{replay_job}-"
        f"combined-{combined_job}-release-{release_job}"
    )


def ensure_terminal_receipt(
    row: Mapping[str, str], *, array_job: str, reducer_job: str,
    replay_job: str, combined_job: str, release_job: str,
) -> tuple[Path, str]:
    raw = canonical_sacct_bytes(row)
    digest = hashlib.sha256(raw).hexdigest()
    directory = terminal_dir(
        array_job, reducer_job, replay_job, combined_job, release_job)
    path = directory / f"release-terminal-{digest}.psv"
    with exclusive_directory_lock(directory, ".terminal-receipt.lock"):
        existing = list(directory.glob("release-terminal-*.psv"))
        if existing:
            req(len(existing) == 1 and existing[0] == path
                and existing[0].read_bytes() == raw,
                "H5 release terminal receipt uniqueness drift")
            return path, digest
        descriptor = os.open(
            path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        req(science.sha(path) == digest,
            "H5 terminal receipt content-address verification failed")
        return path, digest


def discover_candidate(
    *, array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, release_job: str,
) -> tuple[Path, str, dict[str, Any]]:
    directory = provision.candidate_dir(
        array_job, reducer_job, replay_job, combined_job, release_job)
    req(directory.is_dir() and not directory.is_symlink(),
        "H5 provisional candidate directory missing/unsafe")
    candidates = list(directory.glob("candidate-*.json"))
    req(len(candidates) == 1, "H5 provisional candidate uniqueness drift")
    path = candidates[0]
    match = re.fullmatch(r"candidate-([0-9a-f]{64})\.json", path.name)
    req(match is not None and science.sha(path) == match.group(1),
        "H5 provisional candidate content-address drift")
    return path, match.group(1), science.strict_json(path, mode600=True)


def validate_candidate(
    candidate: Mapping[str, Any], *, expected_full: Mapping[str, Any],
    h5_sha: str, h4_sha: str,
) -> None:
    req(set(candidate) == provision.CANDIDATE_KEYS
        and candidate.get("schema") == provision.CANDIDATE_SCHEMA
        and candidate.get("status") == provision.CANDIDATE_STATUS
        and candidate.get("h5_payload_manifest_sha256") == h5_sha
        and candidate.get("h4_payload_manifest_sha256") == h4_sha
        and candidate.get("jobs") == expected_full["jobs"]
        and candidate.get("candidate_writer") == provision.provision_script_record()
        and candidate.get("authorizes_scientific_release") is False,
        "H5 provisional candidate exact envelope drift")
    full = candidate.get("full_recomputation")
    req(isinstance(full, dict) and set(full) == provision.FULL_KEYS
        and full.get("authorizes_scientific_release") is False,
        "H5 provisional full-recomputation authority/key drift")
    req(provision.canonical_bytes(full)
        == provision.canonical_bytes(dict(expected_full)),
        "H5 provisional.full_recomputation exact tree drift")


def final_dir(jobs: Mapping[str, str]) -> Path:
    h4.decimal(jobs["array"], jobs["reducer"], jobs["replay"],
               jobs["combined"], jobs["release"])
    return ROOT / (
        "artifacts/releases_h5/final/"
        f"array-{jobs['array']}-reducer-{jobs['reducer']}-"
        f"replay-{jobs['replay']}-combined-{jobs['combined']}-"
        f"release-{jobs['release']}"
    )


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def write_final(payload: Mapping[str, Any]) -> tuple[Path, str, bool]:
    raw = canonical_json_bytes(payload)
    digest = hashlib.sha256(raw).hexdigest()
    directory = final_dir(payload["jobs"])
    terminal_sha = payload["release_terminal_receipt"]["sha256"]
    req(science.HEX64.fullmatch(terminal_sha) is not None,
        "H5 final terminal receipt digest drift")
    path = directory / f"final-terminal-{terminal_sha}-authority-{digest}.json"
    with exclusive_directory_lock(directory, ".final-authority.lock"):
        existing = list(directory.glob("final-terminal-*-authority-*.json"))
        if existing:
            req(len(existing) == 1 and existing[0] == path
                and existing[0].read_bytes() == raw
                and science.sha(existing[0]) == digest,
                "H5 final authority uniqueness/content drift")
            return path, digest, False
        descriptor = os.open(
            path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        req(science.sha(path) == digest,
            "H5 final content-address verification failed")
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
    *, h5_sha: str, h4_sha: str, expected_full: Mapping[str, Any],
    candidate_path: Path, candidate_sha: str, terminal_path: Path,
    terminal_sha: str, terminal_row: Mapping[str, str],
) -> dict[str, Any]:
    release_submission = provision.release_submission_path()
    release_runtime = provision.release_runtime_path(
        expected_full["jobs"]["release"])
    payload = {
        "schema": FINAL_SCHEMA, "status": FINAL_STATUS,
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
        "H5 final authority internal exact-key drift")
    return payload


def audit(
    *, h5_sha: str, h4_sha: str, array_job: str, reducer_job: str,
    replay_job: str, combined_job: str, release_job: str, v3_sha: str,
    replay_sha: str, replay_submit_sha: str, combined_submit_sha: str,
    combined_json_sha: str, combined_csv_sha: str,
    query: Callable[[str], str] = query_release_sacct,
) -> dict[str, Any]:
    h4.decimal(array_job, reducer_job, replay_job, combined_job, release_job)
    req(science.sha(provision.H5_PAYLOAD) == h5_sha,
        "H5 terminal controller payload drift")
    req(science.sha(provision.H4_PAYLOAD) == h4_sha,
        "H5 terminal controller frozen H4 payload drift")
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
            "observed_state": state_token(row["State"]),
            "retry_safe": True, "wrote_terminal_receipt": False,
            "wrote_final_authority": False,
        }
    # Candidate discovery intentionally occurs only after exact terminal PASS.
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
        candidate, expected_full=expected_full, h5_sha=h5_sha, h4_sha=h4_sha)
    payload = final_payload(
        h5_sha=h5_sha, h4_sha=h4_sha, expected_full=expected_full,
        candidate_path=candidate_path, candidate_sha=candidate_sha,
        terminal_path=terminal_receipt, terminal_sha=terminal_sha,
        terminal_row=row,
    )
    output, digest, created = write_final(payload)
    return {
        "status": payload["status"] if created else "PASS_EXISTING_FINAL_VERIFIED",
        "final_authority": str(output), "sha256": digest,
        "created": created, "authorizes_scientific_release": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
            TimeoutError("H5 terminal controller 1800s walltime limit exceeded")),
    )
    signal.alarm(CONTROLLER_WALLTIME_LIMIT_SECONDS)
    try:
        result = audit(
            h5_sha=args.h5_payload_sha256, h4_sha=args.h4_payload_sha256,
            array_job=args.array_job, reducer_job=args.reducer_job,
            replay_job=args.replay_job, combined_job=args.combined_job,
            release_job=args.release_job, v3_sha=args.v3_release_sha256,
            replay_sha=args.v4_replay_sha256,
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
