#!/usr/bin/env python3
"""Eight-stage H5 DAG entry: six frozen H4 stages, provisional release, audit."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import analyze_gpu_gating_v4_r2_combined_h4 as h4
import provision_gpu_gating_v4_r2_h5 as provision
import scientific_tail_replay_v4_r2_h2 as science
import submit_isambard_ai_gating_v4_r2_h1 as receipt_io
import terminal_audit_gpu_gating_v4_r2_h5 as terminal

ROOT = h4.ROOT
H4_DRIVER = ROOT / "code/submit_isambard_ai_gating_v4_r2_h4.py"
TERMINAL_CONTROLLER = ROOT / "code/terminal_audit_gpu_gating_v4_r2_h5.py"
H4_PHASES = (
    "v3_authority", "canary", "production", "reducer", "replay", "combined",
)
DAG_PHASES = (*H4_PHASES, "release", "terminal_audit")


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def delegate_h4(argv: list[str]) -> int:
    """Preserve frozen H4 stage mechanics while exposing one eight-stage entry."""
    translated: list[str] = []
    index = 0
    saw_h4_sha = False
    while index < len(argv):
        token = argv[index]
        if token == "--h5-payload-sha256":
            req(index + 1 < len(argv), "missing H5 payload value")
            index += 2
            continue
        if token == "--h4-payload-sha256":
            req(index + 1 < len(argv), "missing H4 payload value")
            translated.extend(["--payload-sha256", argv[index + 1]])
            saw_h4_sha = True
            index += 2
            continue
        translated.append(token)
        index += 1
    req(saw_h4_sha, "frozen H4 stage needs --h4-payload-sha256")
    return subprocess.run(
        [sys.executable, str(H4_DRIVER), *translated], cwd=ROOT,
        check=False).returncode


def common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--h5-payload-sha256", required=True)
    parser.add_argument("--h4-payload-sha256", required=True)
    parser.add_argument("--array-job", required=True)
    parser.add_argument("--reducer-job", required=True)
    parser.add_argument("--replay-job", required=True)
    parser.add_argument("--combined-job", required=True)
    parser.add_argument("--v3-release-sha256", required=True)
    parser.add_argument("--v4-replay-sha256", required=True)
    parser.add_argument("--replay-submission-sha256", required=True)
    parser.add_argument("--combined-submission-sha256", required=True)
    parser.add_argument("--combined-json-sha256", required=True)
    parser.add_argument("--combined-csv-sha256", required=True)


def parse_h5_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("release", "terminal_audit"),
                        required=True)
    common_args(parser)
    parser.add_argument("--release-job")
    return parser.parse_args(argv)


def validate_upstream(args: argparse.Namespace) -> tuple[Path, Path]:
    h4.decimal(args.array_job, args.reducer_job,
               args.replay_job, args.combined_job)
    req(science.sha(provision.H5_PAYLOAD) == args.h5_payload_sha256,
        "H5 submission payload drift")
    req(science.sha(provision.H4_PAYLOAD) == args.h4_payload_sha256,
        "H5 submission frozen H4 payload drift")
    h4.validate_v3_receipt(args.v3_release_sha256)
    h4.validate_replay_submission(
        expected_sha=args.replay_submission_sha256,
        h4_sha=args.h4_payload_sha256, array_job=args.array_job,
        reducer_job=args.reducer_job, replay_job=args.replay_job)
    h4.validate_replay_receipt(
        args.v4_replay_sha256, h4_sha=args.h4_payload_sha256,
        array_job=args.array_job, reducer_job=args.reducer_job,
        replay_job=args.replay_job)
    h4.validate_combined_submission(
        expected_sha=args.combined_submission_sha256,
        h4_sha=args.h4_payload_sha256, array_job=args.array_job,
        reducer_job=args.reducer_job, replay_job=args.replay_job,
        combined_job=args.combined_job, v3_sha=args.v3_release_sha256,
        replay_sha=args.v4_replay_sha256,
        replay_submit_sha=args.replay_submission_sha256)
    combined_json, combined_csv = h4.combined_paths(
        args.replay_job, args.combined_job)
    req(science.sha(combined_json) == args.combined_json_sha256
        and science.sha(combined_csv) == args.combined_csv_sha256,
        "H5 canonical combined hashes drift before release")
    value = science.strict_json(combined_json, mode600=True)
    authority = value.get("authorization")
    req(set(value) == h4.COMBINED_KEYS
        and value["schema"] == h4.COMBINED_SCHEMA
        and value["status"] == h4.COMBINED_STATUS
        and value["authorizes_scientific_release"] is False
        and isinstance(authority, dict)
        and set(authority) == h4.AUTHORIZATION_KEYS
        and authority["array_job_id"] == args.array_job
        and authority["reducer_job_id"] == args.reducer_job
        and authority["replay_job_id"] == args.replay_job
        and authority["combined_job_id"] == args.combined_job
        and authority["v3_release_receipt_sha256"]
            == args.v3_release_sha256
        and authority["v4_replay_receipt_sha256"]
            == args.v4_replay_sha256
        and authority["replay_submission_receipt_sha256"]
            == args.replay_submission_sha256,
        "H5 combined authority closure drift")
    return combined_json, combined_csv


def submit_release(args: argparse.Namespace) -> int:
    req(args.release_job is None,
        "H5 release submission must not accept a preselected release job ID")
    validate_upstream(args)
    output = provision.release_submission_path()
    req(not output.exists(), "H5 release already submitted")
    command = provision.release_command(
        h5_sha=args.h5_payload_sha256, h4_sha=args.h4_payload_sha256,
        array_job=args.array_job, reducer_job=args.reducer_job,
        replay_job=args.replay_job, combined_job=args.combined_job,
        v3_sha=args.v3_release_sha256, replay_sha=args.v4_replay_sha256,
        replay_submit_sha=args.replay_submission_sha256,
        combined_submit_sha=args.combined_submission_sha256,
        combined_json_sha=args.combined_json_sha256,
        combined_csv_sha=args.combined_csv_sha256,
    )
    completed = subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True)
    job = completed.stdout.strip().split(";")[0]
    req(job.isdecimal(), "sbatch returned nondecimal H5 release job ID")
    readback = subprocess.run(
        ["scontrol", "show", "job", "-o", job], cwd=ROOT, check=True,
        capture_output=True, text=True).stdout.strip()
    req(f"JobId={job}" in readback
        and f"Dependency=afterok:{args.combined_job}" in readback
        and f"WorkDir={ROOT}" in readback
        and provision.RELEASE_SCRIPT in readback,
        "H5 release scontrol readback drift")
    payload = {
        "schema": provision.SUBMIT_SCHEMA, "status": provision.SUBMIT_STATUS,
        "phase": "release", "job_id": job,
        "dependency_afterok": args.combined_job,
        "h5_payload_manifest_sha256": args.h5_payload_sha256,
        "h4_payload_manifest_sha256": args.h4_payload_sha256,
        "phase_inputs": provision.release_inputs(
            array_job=args.array_job, reducer_job=args.reducer_job,
            replay_job=args.replay_job, combined_job=args.combined_job,
            v3_sha=args.v3_release_sha256, replay_sha=args.v4_replay_sha256,
            replay_submit_sha=args.replay_submission_sha256,
            combined_submit_sha=args.combined_submission_sha256,
            combined_json_sha=args.combined_json_sha256,
            combined_csv_sha=args.combined_csv_sha256),
        "script": provision.release_script_record(), "argv": command,
        "authorities": provision.release_authorities(
            reducer_job=args.reducer_job, replay_job=args.replay_job,
            combined_job=args.combined_job, v3_sha=args.v3_release_sha256,
            replay_sha=args.v4_replay_sha256,
            replay_submit_sha=args.replay_submission_sha256,
            combined_submit_sha=args.combined_submission_sha256,
            combined_json_sha=args.combined_json_sha256,
            combined_csv_sha=args.combined_csv_sha256),
        "scontrol_readback": readback, "submit_line": " ".join(command),
    }
    req(set(payload) == provision.SUBMIT_KEYS,
        "H5 release submission internal exact-key drift")
    receipt_io.commit_receipt(output, payload)
    print(json.dumps({
        "status": payload["status"], "phase": "release", "job_id": job,
        "receipt_sha256": science.sha(output),
        "next_phase": "terminal_audit",
    }, sort_keys=True))
    return 0


def terminal_command(args: argparse.Namespace) -> list[str]:
    req(args.release_job is not None and args.release_job.isdecimal(),
        "terminal_audit needs --release-job")
    return [
        sys.executable, str(TERMINAL_CONTROLLER),
        "--h5-payload-sha256", args.h5_payload_sha256,
        "--h4-payload-sha256", args.h4_payload_sha256,
        "--array-job", args.array_job, "--reducer-job", args.reducer_job,
        "--replay-job", args.replay_job, "--combined-job", args.combined_job,
        "--release-job", args.release_job,
        "--v3-release-sha256", args.v3_release_sha256,
        "--v4-replay-sha256", args.v4_replay_sha256,
        "--replay-submission-sha256", args.replay_submission_sha256,
        "--combined-submission-sha256", args.combined_submission_sha256,
        "--combined-json-sha256", args.combined_json_sha256,
        "--combined-csv-sha256", args.combined_csv_sha256,
    ]


def main(argv: list[str] | None = None) -> int:
    actual = list(sys.argv[1:] if argv is None else argv)
    preview = argparse.ArgumentParser(add_help=False)
    preview.add_argument("--phase", choices=DAG_PHASES, required=True)
    known, _ = preview.parse_known_args(actual)
    if known.phase in H4_PHASES:
        return delegate_h4(actual)
    args = parse_h5_args(actual)
    if args.phase == "release":
        return submit_release(args)
    # This is a single login-node read/verify invocation.  It never polls,
    # sleeps, or submits another Slurm job; exit 75 means retry later.
    return subprocess.run(terminal_command(args), cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError,
            subprocess.CalledProcessError) as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        raise SystemExit(2)
