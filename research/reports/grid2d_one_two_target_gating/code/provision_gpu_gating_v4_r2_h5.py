#!/usr/bin/env python3
"""Produce an H5 content-addressed provisional candidate with no authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

import analyze_gpu_gating_v4_r2_combined_h4 as h4
import finalize_gpu_gating_v4_r2_h2 as h2_final
import finalize_gpu_gating_v4_r2_h4 as h4_final
import runtime_probe_v4_r2_h4 as runtime_h4
import runtime_probe_v4_r2_h5 as runtime_h5
import scientific_tail_replay_v4_r2_h2 as science

ROOT = h4.ROOT
H4_PAYLOAD = h4.PAYLOAD
H5_PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h5_payload.sha256"
SUB = ROOT / "artifacts/submission_h5"
RELEASE_SCRIPT = "isambard_ai_gating_v4_r2_release_h5.sbatch"
PROVISION_SCRIPT = "provision_gpu_gating_v4_r2_h5.py"
SUBMIT_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h5-submission-v1"
SUBMIT_STATUS = "SUBMITTED_WITH_EXACT_READBACK"
SUBMIT_KEYS = {
    "schema", "status", "phase", "job_id", "dependency_afterok",
    "h5_payload_manifest_sha256", "h4_payload_manifest_sha256",
    "phase_inputs", "script", "argv", "authorities",
    "scontrol_readback", "submit_line",
}
FULL_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h4-full-recomputation-h5-v1"
FULL_STATUS = "PASS_H4_FULL_RECOMPUTATION_NO_RELEASE_AUTHORITY"
FULL_KEYS = {
    "schema", "status", "h5_payload_manifest_sha256",
    "h4_payload_manifest_sha256", "jobs", "combined_json", "combined_csv",
    "v3_release", "v4_replay", "replay_submission", "combined_submission",
    "release_submission", "runtime_receipts", "combined_terminal_slurm_receipt",
    "authorization", "primary", "surface", "pack_heterogeneity",
    "authorizes_scientific_release",
}
CANDIDATE_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h5-provisional-candidate-v1"
CANDIDATE_STATUS = "PASS_H5_PROVISIONAL_AWAIT_RELEASE_TERMINAL_AUDIT"
CANDIDATE_KEYS = {
    "schema", "status", "h5_payload_manifest_sha256",
    "h4_payload_manifest_sha256", "jobs", "full_recomputation",
    "candidate_writer", "authorizes_scientific_release",
}


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def release_submission_path() -> Path:
    return SUB / "release-submission.json"


def release_runtime_path(release_job: str) -> Path:
    h4.decimal(release_job)
    return ROOT / f"artifacts/runtime_h5/release-{release_job}.json"


def provisional_input_dir(
    array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, release_job: str,
) -> Path:
    h4.decimal(array_job, reducer_job, replay_job, combined_job, release_job)
    return ROOT / (
        "artifacts/releases_h5/provisional_inputs/"
        f"array-{array_job}-reducer-{reducer_job}-replay-{replay_job}-"
        f"combined-{combined_job}-release-{release_job}"
    )


def combined_terminal_path(
    array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, release_job: str,
) -> Path:
    return provisional_input_dir(
        array_job, reducer_job, replay_job, combined_job, release_job,
    ) / "combined-terminal.psv"


def candidate_dir(
    array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, release_job: str,
) -> Path:
    h4.decimal(array_job, reducer_job, replay_job, combined_job, release_job)
    return ROOT / (
        "artifacts/releases_h5/provisional/"
        f"array-{array_job}-reducer-{reducer_job}-replay-{replay_job}-"
        f"combined-{combined_job}-release-{release_job}"
    )


def candidate_path(
    *, digest: str, array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, release_job: str,
) -> Path:
    req(science.HEX64.fullmatch(digest) is not None,
        "H5 candidate digest is not SHA-256")
    return candidate_dir(
        array_job, reducer_job, replay_job, combined_job, release_job,
    ) / f"candidate-{digest}.json"


def release_script_record() -> dict[str, str]:
    path = Path(__file__).resolve().parent / RELEASE_SCRIPT
    return {"path": f"code/{RELEASE_SCRIPT}", "sha256": science.sha(path)}


def provision_script_record() -> dict[str, str]:
    path = Path(__file__).resolve().parent / PROVISION_SCRIPT
    return {"path": f"code/{PROVISION_SCRIPT}", "sha256": science.sha(path)}


def release_command(
    *, h5_sha: str, h4_sha: str, array_job: str, reducer_job: str,
    replay_job: str, combined_job: str, v3_sha: str, replay_sha: str,
    replay_submit_sha: str, combined_submit_sha: str,
    combined_json_sha: str, combined_csv_sha: str,
) -> list[str]:
    args = [
        h5_sha, h4_sha, array_job, reducer_job, replay_job, combined_job,
        v3_sha, replay_sha, replay_submit_sha, combined_submit_sha,
        combined_json_sha, combined_csv_sha, str(release_submission_path()),
    ]
    return [
        "sbatch", "--parsable", f"--dependency=afterok:{combined_job}",
        f"code/{RELEASE_SCRIPT}", *args,
    ]


def release_inputs(
    *, array_job: str, reducer_job: str, replay_job: str, combined_job: str,
    v3_sha: str, replay_sha: str, replay_submit_sha: str,
    combined_submit_sha: str, combined_json_sha: str, combined_csv_sha: str,
) -> dict[str, str]:
    return {
        "array_job_id": array_job, "reducer_job_id": reducer_job,
        "replay_job_id": replay_job, "combined_job_id": combined_job,
        "v3_release_sha256": v3_sha,
        "v4_replay_receipt_sha256": replay_sha,
        "replay_submission_sha256": replay_submit_sha,
        "combined_submission_sha256": combined_submit_sha,
        "combined_json_sha256": combined_json_sha,
        "combined_csv_sha256": combined_csv_sha,
    }


def release_authorities(
    *, reducer_job: str, replay_job: str, combined_job: str,
    v3_sha: str, replay_sha: str, replay_submit_sha: str,
    combined_submit_sha: str, combined_json_sha: str, combined_csv_sha: str,
) -> dict[str, dict[str, str]]:
    combined_json, combined_csv = h4.combined_paths(replay_job, combined_job)
    return {
        "v3_release": {"path": str(h4.v3_release_path()), "sha256": v3_sha},
        "v4_replay": {
            "path": str(h4.replay_receipt_path(reducer_job)),
            "sha256": replay_sha,
        },
        "replay_submission": {
            "path": str(h4.submission_path("replay")),
            "sha256": replay_submit_sha,
        },
        "combined_submission": {
            "path": str(h4.submission_path("combined")),
            "sha256": combined_submit_sha,
        },
        "combined_json": {"path": str(combined_json),
                          "sha256": combined_json_sha},
        "combined_csv": {"path": str(combined_csv),
                         "sha256": combined_csv_sha},
    }


def validate_release_submission(
    *, h5_sha: str, h4_sha: str, array_job: str, reducer_job: str,
    replay_job: str, combined_job: str, release_job: str, v3_sha: str,
    replay_sha: str, replay_submit_sha: str, combined_submit_sha: str,
    combined_json_sha: str, combined_csv_sha: str,
) -> dict[str, Any]:
    path = release_submission_path()
    value = science.strict_json(path, mode600=True)
    command = release_command(
        h5_sha=h5_sha, h4_sha=h4_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job, v3_sha=v3_sha, replay_sha=replay_sha,
        replay_submit_sha=replay_submit_sha,
        combined_submit_sha=combined_submit_sha,
        combined_json_sha=combined_json_sha, combined_csv_sha=combined_csv_sha,
    )
    inputs = release_inputs(
        array_job=array_job, reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job, v3_sha=v3_sha, replay_sha=replay_sha,
        replay_submit_sha=replay_submit_sha,
        combined_submit_sha=combined_submit_sha,
        combined_json_sha=combined_json_sha, combined_csv_sha=combined_csv_sha,
    )
    authorities = release_authorities(
        reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job, v3_sha=v3_sha, replay_sha=replay_sha,
        replay_submit_sha=replay_submit_sha,
        combined_submit_sha=combined_submit_sha,
        combined_json_sha=combined_json_sha, combined_csv_sha=combined_csv_sha,
    )
    readback = value.get("scontrol_readback")
    req(set(value) == SUBMIT_KEYS and value["schema"] == SUBMIT_SCHEMA
        and value["status"] == SUBMIT_STATUS and value["phase"] == "release"
        and value["job_id"] == release_job
        and value["dependency_afterok"] == combined_job
        and value["h5_payload_manifest_sha256"] == h5_sha
        and value["h4_payload_manifest_sha256"] == h4_sha
        and value["phase_inputs"] == inputs and value["authorities"] == authorities
        and value["script"] == release_script_record()
        and value["argv"] == command and value["submit_line"] == " ".join(command)
        and isinstance(readback, str) and f"JobId={release_job}" in readback
        and f"Dependency=afterok:{combined_job}" in readback
        and f"WorkDir={ROOT}" in readback and RELEASE_SCRIPT in readback,
        "H5 release submission exact authority drift")
    return value


def full_recomputation(
    *, h5_sha: str, h4_sha: str, array_job: str, reducer_job: str,
    replay_job: str, combined_job: str, release_job: str, v3_sha: str,
    replay_sha: str, replay_submit_sha: str, combined_submit_sha: str,
    combined_json_sha: str, combined_csv_sha: str,
) -> dict[str, Any]:
    """Rerun every H4 final computation without issuing release authority."""
    h4.decimal(array_job, reducer_job, replay_job, combined_job, release_job)
    req(science.sha(H5_PAYLOAD) == h5_sha, "H5 payload manifest drift")
    req(science.sha(H4_PAYLOAD) == h4_sha, "frozen H4 payload manifest drift")
    combined_json, combined_csv = h4.combined_paths(replay_job, combined_job)
    req(science.sha(combined_json) == combined_json_sha
        and science.sha(combined_csv) == combined_csv_sha,
        "H5 canonical combined output hash drift")
    combined = science.strict_json(combined_json, mode600=True)
    v3_release = h4.validate_v3_receipt(v3_sha)
    replay_submission = h4.validate_replay_submission(
        expected_sha=replay_submit_sha, h4_sha=h4_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
    )
    replay = h4.validate_replay_receipt(
        replay_sha, h4_sha=h4_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
    )
    combined_submission = h4.validate_combined_submission(
        expected_sha=combined_submit_sha, h4_sha=h4_sha,
        array_job=array_job, reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job, v3_sha=v3_sha, replay_sha=replay_sha,
        replay_submit_sha=replay_submit_sha,
    )
    v3_csv, v3_csv_sha, v4_csv, v4_csv_sha = h4.reduction_csvs(
        v3_release, replay)
    computed = h4.recompute_inference(v3_csv, v3_csv_sha, v4_csv, v4_csv_sha)
    expected_authorization = h4.authorization(
        h4_sha=h4_sha, v3_sha=v3_sha, replay_sha=replay_sha,
        replay_submit_sha=replay_submit_sha, v3_release=v3_release,
        replay=replay, v3_csv=v3_csv, v3_csv_sha=v3_csv_sha,
        v4_csv=v4_csv, v4_csv_sha=v4_csv_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job,
    )
    expected_submission = h4_final.expected_submission_binding(
        combined_submission, combined_submit_sha=combined_submit_sha,
        replay_job=replay_job, replay_submit_sha=replay_submit_sha,
        combined_job=combined_job,
    )
    combined_runtime_path = h4.runtime_path("combined", combined_job)
    expected_runtime = runtime_h4.binding(
        combined_runtime_path, phase="combined", job_id=combined_job)
    csv_data, fieldnames = h4.csv_bytes(computed["surface"])
    req(hashlib.sha256(csv_data).hexdigest() == combined_csv_sha
        and combined_csv.read_bytes() == csv_data,
        "H5 combined CSV bytes differ from fresh H4 recomputation")
    h4_final.validate_combined_payload(
        combined, combined_path=combined_json, csv_path=combined_csv,
        replay_job=replay_job, combined_job=combined_job,
        expected_authorization=expected_authorization,
        expected_submission=expected_submission,
        expected_runtime=expected_runtime,
        expected_primary=computed["primary"],
        expected_surface=computed["surface"],
        expected_heterogeneity=computed["pack_heterogeneity"],
        expected_csv=h4_final.expected_csv_record(
            combined_csv, combined_csv_sha, fieldnames),
    )
    release_submission = validate_release_submission(
        h5_sha=h5_sha, h4_sha=h4_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job, release_job=release_job, v3_sha=v3_sha,
        replay_sha=replay_sha, replay_submit_sha=replay_submit_sha,
        combined_submit_sha=combined_submit_sha,
        combined_json_sha=combined_json_sha, combined_csv_sha=combined_csv_sha,
    )
    release_runtime = runtime_h5.binding(
        release_runtime_path(release_job), phase="release", job_id=release_job)
    combined_terminal = combined_terminal_path(
        array_job, reducer_job, replay_job, combined_job, release_job)
    terminal = h2_final.terminal_sacct(combined_terminal, combined_job)
    result = {
        "schema": FULL_SCHEMA, "status": FULL_STATUS,
        "h5_payload_manifest_sha256": h5_sha,
        "h4_payload_manifest_sha256": h4_sha,
        "jobs": {
            "array": array_job, "reducer": reducer_job,
            "replay": replay_job, "combined": combined_job,
            "release": release_job,
        },
        "combined_json": {"path": str(combined_json),
                          "sha256": combined_json_sha},
        "combined_csv": {"path": str(combined_csv),
                         "sha256": combined_csv_sha},
        "v3_release": {"path": str(h4.v3_release_path()), "sha256": v3_sha},
        "v4_replay": {"path": str(h4.replay_receipt_path(reducer_job)),
                      "sha256": replay_sha},
        "replay_submission": {
            "path": str(h4.submission_path("replay")),
            "sha256": replay_submit_sha, "job_id": replay_submission["job_id"],
        },
        "combined_submission": {
            "path": str(h4.submission_path("combined")),
            "sha256": combined_submit_sha,
            "job_id": combined_submission["job_id"],
        },
        "release_submission": {
            "path": str(release_submission_path()),
            "sha256": science.sha(release_submission_path()),
            "job_id": release_submission["job_id"],
            "submit_line": release_submission["submit_line"],
        },
        "runtime_receipts": {
            "v3_authority": v3_release["runtime_binding"],
            "replay": replay["runtime_binding"],
            "combined": expected_runtime, "release": release_runtime,
        },
        "combined_terminal_slurm_receipt": {
            "path": str(combined_terminal), **terminal,
        },
        "authorization": expected_authorization,
        "primary": computed["primary"], "surface": computed["surface"],
        "pack_heterogeneity": computed["pack_heterogeneity"],
        "authorizes_scientific_release": False,
    }
    req(set(result) == FULL_KEYS,
        "H5 full recomputation internal exact-key drift")
    return result


def candidate_payload(
    full: Mapping[str, Any], *, h5_sha: str, h4_sha: str,
) -> dict[str, Any]:
    payload = {
        "schema": CANDIDATE_SCHEMA, "status": CANDIDATE_STATUS,
        "h5_payload_manifest_sha256": h5_sha,
        "h4_payload_manifest_sha256": h4_sha,
        "jobs": dict(full["jobs"]),
        "full_recomputation": dict(full),
        "candidate_writer": provision_script_record(),
        "authorizes_scientific_release": False,
    }
    req(set(payload) == CANDIDATE_KEYS
        and payload["full_recomputation"]["authorizes_scientific_release"] is False,
        "H5 candidate internal authority/key drift")
    return payload


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def write_candidate(payload: Mapping[str, Any]) -> tuple[Path, str]:
    raw = canonical_bytes(payload)
    digest = hashlib.sha256(raw).hexdigest()
    jobs = payload["jobs"]
    path = candidate_path(
        digest=digest, array_job=jobs["array"], reducer_job=jobs["reducer"],
        replay_job=jobs["replay"], combined_job=jobs["combined"],
        release_job=jobs["release"],
    )
    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    req(not list(directory.glob("candidate-*.json")),
        "H5 provisional directory already contains a candidate")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    req(science.sha(path) == digest,
        "H5 provisional content-addressed write verification failed")
    return path, digest


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
    try:
        full = full_recomputation(
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
        payload = candidate_payload(
            full, h5_sha=args.h5_payload_sha256,
            h4_sha=args.h4_payload_sha256)
        output, digest = write_candidate(payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({
        "status": payload["status"], "candidate": str(output),
        "sha256": digest, "authorizes_scientific_release": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
