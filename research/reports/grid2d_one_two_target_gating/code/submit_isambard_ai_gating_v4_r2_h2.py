#!/usr/bin/env python3
"""Append-only, phase-exact H2 Slurm submission state machine."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import submit_isambard_ai_gating_v4_r2_h1 as h1
import scientific_tail_replay_v4_r2_h2 as science

ROOT = h1.ROOT
SUB = ROOT / "artifacts/submission_h2"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h2_payload.sha256"
V3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h2.json"
H1_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h1.json"
SCHEMA = "grid2d-one-two-target-gating-v4-r2-h2-submission-v1"
STATUS = "SUBMITTED_WITH_EXACT_READBACK"
SCRIPTS = {
    "v3_authority": "isambard_ai_gating_v4_r2_v3_authority_h2.sbatch",
    "canary": "isambard_ai_gating_v4_r2_gpu_canary_h2.sbatch",
    "production": "isambard_ai_gating_v4_r2_fullnode_h2.sbatch",
    "reducer": "isambard_ai_gating_v4_r2_reduce_h2.sbatch",
    "replay": "isambard_ai_gating_v4_r2_replay_h2.sbatch",
    "combined": "isambard_ai_gating_v4_r2_combined_h2.sbatch",
    "release": "isambard_ai_gating_v4_r2_release_h2.sbatch",
}
TOP_KEYS = h1.TOP_KEYS


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def _configure(v3_authority_job: str | None = None) -> None:
    h1.SUB = SUB
    h1.PAYLOAD = PAYLOAD
    h1.V3_RELEASE = V3_RELEASE
    h1.SCHEMA = SCHEMA
    h1.STATUS = STATUS
    h1.SCRIPTS = {key: value for key, value in SCRIPTS.items()
                  if key in {"canary", "production", "reducer", "replay", "combined"}}
    if v3_authority_job is not None:
        h1.V3_TERMINAL_JOB = v3_authority_job


def validate_v3_release(expected_sha: str) -> dict[str, Any]:
    value = h1.authority(V3_RELEASE, expected_sha)
    req(value.get("schema") ==
        "grid2d-one-two-target-gating-v3-release-for-v4-r2-h2"
        and value.get("status") == "PASS_AUTHORIZE_V4_R2_H2_HARDWARE_CANARY"
        and value.get("authorizes_v4_r2_h2") is True
        and value.get("scientific_tail_replay", {}).get("status")
            == "PASS_TAIL_EVIDENCE",
        "H2 v3 release did not authorize canary")
    return value


def _existing_submission(phase: str, expected_sha: str,
                         expected_job: str | None = None) -> dict[str, Any]:
    path = SUB / f"{phase}-submission.json"
    value = h1.authority(path, expected_sha)
    req(set(value) == TOP_KEYS and value["schema"] == SCHEMA
        and value["status"] == STATUS and value["phase"] == phase,
        f"{phase} submission receipt envelope drift")
    if expected_job is not None:
        req(value["job_id"] == expected_job, f"{phase} job ID drift")
    script = ROOT / "code" / SCRIPTS[phase]
    req(value["script"] == {"path": f"code/{SCRIPTS[phase]}",
                             "sha256": science.sha(script)},
        f"{phase} script binding drift")
    return value


def _manual_phase(args: argparse.Namespace) -> tuple[str, list[str], dict[str, str], dict[str, dict[str, str]]]:
    payload_sha = args.payload_sha256
    if args.phase == "v3_authority":
        req(args.h1_release_sha256 is not None and science.HEX64.fullmatch(
            args.h1_release_sha256) is not None,
            "v3_authority needs one H1 release SHA")
        req(science.sha(H1_RELEASE) == args.h1_release_sha256,
            "H1 release hash drift before H2 v3 authority")
        return (
            "5789031", [payload_sha, args.h1_release_sha256],
            {"h1_v3_release_sha256": args.h1_release_sha256},
            {"h1_v3_release": {"path": str(H1_RELEASE),
                               "sha256": args.h1_release_sha256}},
        )
    if args.phase == "canary":
        req(args.v3_authority_job is not None and args.v3_release_sha256 is not None,
            "canary needs v3 authority job/release SHA")
        validate_v3_release(args.v3_release_sha256)
        return (
            args.v3_authority_job,
            [payload_sha, args.v3_release_sha256, str(V3_RELEASE)],
            {"v3_release_sha256": args.v3_release_sha256},
            {"v3_release": {"path": str(V3_RELEASE),
                            "sha256": args.v3_release_sha256}},
        )
    if args.phase == "combined":
        required = (args.v3_release_sha256, args.replay_job,
                    args.replay_submission_sha256, args.replay_receipt_sha256,
                    args.reducer_job)
        req(all(value is not None for value in required),
            "combined phase options incomplete")
        validate_v3_release(args.v3_release_sha256)
        replay_submission = _existing_submission(
            "replay", args.replay_submission_sha256, args.replay_job)
        req(replay_submission["dependency_afterok"] == args.reducer_job,
            "combined replay dependency drift")
        replay = ROOT / f"artifacts/replay/v4-r2-replay-h2-{args.reducer_job}.json"
        replay_value = h1.authority(replay, args.replay_receipt_sha256)
        req(replay_value.get("status") ==
            "PASS_AUTHORIZE_V3_V4_R2_H2_COMBINED"
            and replay_value.get("authorizes_combined") is True,
            "H2 replay did not authorize combined phase")
        receipt = SUB / "combined-submission.json"
        inputs = {
            "v3_release_sha256": args.v3_release_sha256,
            "v4_replay_receipt_sha256": args.replay_receipt_sha256,
            "replay_job_id": args.replay_job,
            "replay_submission_sha256": args.replay_submission_sha256,
        }
        authorities = {
            "v3_release": {"path": str(V3_RELEASE),
                           "sha256": args.v3_release_sha256},
            "v4_replay": {"path": str(replay),
                          "sha256": args.replay_receipt_sha256},
            "replay_submission": {"path": str(SUB / "replay-submission.json"),
                                  "sha256": args.replay_submission_sha256},
        }
        argv = [payload_sha, str(V3_RELEASE), args.v3_release_sha256,
                str(replay), args.replay_receipt_sha256, args.replay_job,
                str(SUB / "replay-submission.json"),
                args.replay_submission_sha256, str(receipt)]
        return args.replay_job, argv, inputs, authorities
    if args.phase == "release":
        required = (args.combined_job, args.combined_submission_sha256,
                    args.combined_json, args.combined_json_sha256,
                    args.combined_csv, args.combined_csv_sha256)
        req(all(value is not None for value in required),
            "release phase options incomplete")
        combined_submission = _existing_submission(
            "combined", args.combined_submission_sha256, args.combined_job)
        combined_json = Path(args.combined_json)
        combined_csv = Path(args.combined_csv)
        req(science.sha(combined_json) == args.combined_json_sha256
            and science.sha(combined_csv) == args.combined_csv_sha256,
            "combined output hashes drift before release")
        value = science.strict_json(combined_json, mode600=True)
        req(value.get("status") ==
            "PASS_H2_COMBINED_COMPUTATION_AWAIT_TERMINAL_RELEASE"
            and value.get("submission_binding", {}).get("combined_job_id")
                == args.combined_job,
            "combined output did not await terminal release")
        receipt = SUB / "release-submission.json"
        inputs = {
            "combined_job_id": args.combined_job,
            "combined_json_sha256": args.combined_json_sha256,
            "combined_csv_sha256": args.combined_csv_sha256,
            "combined_submission_sha256": args.combined_submission_sha256,
        }
        authorities = {
            "combined_json": {"path": str(combined_json),
                              "sha256": args.combined_json_sha256},
            "combined_csv": {"path": str(combined_csv),
                             "sha256": args.combined_csv_sha256},
            "combined_submission": {
                "path": str(SUB / "combined-submission.json"),
                "sha256": args.combined_submission_sha256,
            },
        }
        argv = [payload_sha, args.combined_job, str(combined_json),
                args.combined_json_sha256, str(combined_csv),
                args.combined_csv_sha256, str(SUB / "combined-submission.json"),
                args.combined_submission_sha256, str(receipt)]
        req(combined_submission["job_id"] == args.combined_job,
            "release combined receipt/job drift")
        return args.combined_job, argv, inputs, authorities
    raise ValueError("not a manual H2 phase")


def phase_spec(args: argparse.Namespace) -> tuple[str, list[str], dict[str, str], dict[str, dict[str, str]]]:
    if args.phase in {"v3_authority", "canary", "combined", "release"}:
        return _manual_phase(args)
    req(args.v3_authority_job is not None,
        f"{args.phase} needs the fixed H2 v3 authority job ID")
    _configure(args.v3_authority_job)
    h1.validate_v3_release = validate_v3_release
    # The H1 phase implementation is reused only after all authority constants,
    # schemas, scripts, and release validation have been replaced with H2 values.
    return h1.phase_spec(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=tuple(SCRIPTS), required=True)
    parser.add_argument("--payload-sha256", required=True)
    for name in (
        "h1-release-sha256", "v3-authority-job", "v3-release-sha256",
        "canary-job", "canary-submission-sha256", "canary-receipt-sha256",
        "array-job", "production-submission-sha256", "reducer-job",
        "reducer-submission-sha256", "reduction-sha256", "replay-job",
        "replay-submission-sha256", "replay-receipt-sha256", "combined-job",
        "combined-submission-sha256", "combined-json", "combined-json-sha256",
        "combined-csv", "combined-csv-sha256",
    ):
        parser.add_argument(f"--{name}")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    req(science.HEX64.fullmatch(args.payload_sha256) is not None
        and science.sha(PAYLOAD) == args.payload_sha256,
        "H2 payload manifest drift")
    _configure(args.v3_authority_job)
    h1.validate_v3_release = validate_v3_release
    script = ROOT / "code" / SCRIPTS[args.phase]
    output = SUB / f"{args.phase}-submission.json"
    req(script.is_file() and not script.is_symlink() and not output.exists(),
        "H2 phase script missing or phase already submitted")
    dependency, script_args, inputs, authorities = phase_spec(args)
    req(isinstance(dependency, str) and dependency.isdecimal(),
        "H2 dependency is not decimal")
    command = ["sbatch", "--parsable", f"--dependency=afterok:{dependency}",
               f"code/{SCRIPTS[args.phase]}", *script_args]
    completed = subprocess.run(command, cwd=ROOT, check=True,
                               capture_output=True, text=True)
    job = completed.stdout.strip().split(";")[0]
    req(job.isdecimal(), "sbatch returned a nondecimal H2 job ID")
    readback = subprocess.run(["scontrol", "show", "job", "-o", job],
                              cwd=ROOT, check=True, capture_output=True,
                              text=True).stdout.strip()
    req(f"JobId={job}" in readback and f"Dependency=afterok:{dependency}" in readback
        and f"WorkDir={ROOT}" in readback and SCRIPTS[args.phase] in readback,
        "H2 scontrol readback drift")
    payload = {
        "schema": SCHEMA, "status": STATUS, "phase": args.phase,
        "job_id": job, "dependency_afterok": dependency,
        "payload_manifest_sha256": args.payload_sha256,
        "phase_inputs": inputs,
        "script": {"path": f"code/{SCRIPTS[args.phase]}",
                   "sha256": science.sha(script)},
        "argv": command, "authorities": authorities,
        "scontrol_readback": readback,
    }
    req(set(payload) == TOP_KEYS, "H2 internal submission receipt key drift")
    h1.commit_receipt(output, payload)
    print(json.dumps({"status": STATUS, "phase": args.phase, "job_id": job,
                      "receipt_sha256": science.sha(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError,
            subprocess.CalledProcessError) as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        raise SystemExit(2)
