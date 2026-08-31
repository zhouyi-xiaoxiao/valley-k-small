#!/usr/bin/env python3
"""Append-only H3 submission state machine over the reviewed H2 mechanics."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import submit_isambard_ai_gating_v4_r2_h2 as base
import scientific_tail_replay_v4_r2_h2 as science

ROOT = base.ROOT
SUB = ROOT / "artifacts/submission_h3"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h3_payload.sha256"
V3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h3.json"
SCHEMA = "grid2d-one-two-target-gating-v4-r2-h3-submission-v1"
SCRIPTS = {
    "v3_authority": "isambard_ai_gating_v4_r2_v3_authority_h3.sbatch",
    "canary": "isambard_ai_gating_v4_r2_gpu_canary_h3.sbatch",
    "production": "isambard_ai_gating_v4_r2_fullnode_h3.sbatch",
    "reducer": "isambard_ai_gating_v4_r2_reduce_h3.sbatch",
    "replay": "isambard_ai_gating_v4_r2_replay_h3.sbatch",
    "combined": "isambard_ai_gating_v4_r2_combined_h3.sbatch",
    "release": "isambard_ai_gating_v4_r2_release_h3.sbatch",
}


def req(value: bool, message: str) -> None:
    if not value: raise ValueError(message)


def configure() -> None:
    base.SUB = SUB; base.PAYLOAD = PAYLOAD; base.V3_RELEASE = V3_RELEASE
    base.SCHEMA = SCHEMA; base.SCRIPTS = SCRIPTS
    base.validate_v3_release = validate_v3_release
    base._manual_phase = manual_phase
    base.parse_args = parse_args


def validate_v3_release(expected_sha: str) -> dict[str, Any]:
    value = base.h1.authority(V3_RELEASE, expected_sha)
    req(value.get("schema") ==
        "grid2d-one-two-target-gating-v3-release-for-v4-r2-h3"
        and value.get("status") == "PASS_AUTHORIZE_V4_R2_H3_HARDWARE_CANARY"
        and value.get("authorizes_v4_r2_h3") is True
        and value.get("h3_primary_rope_replay", {}).get("status")
            == "PASS_PRIMARY_ROPE_EVIDENCE",
        "H3 v3 release did not authorize canary")
    return value


def manual_phase(args: argparse.Namespace):
    payload_sha = args.payload_sha256
    if args.phase == "v3_authority":
        req(args.h1_release_sha256 is not None
            and science.HEX64.fullmatch(args.h1_release_sha256) is not None
            and science.sha(base.H1_RELEASE) == args.h1_release_sha256,
            "H3 v3 authority H1 release hash drift")
        return ("5789031", [payload_sha, args.h1_release_sha256],
                {"h1_v3_release_sha256": args.h1_release_sha256},
                {"h1_v3_release": {"path": str(base.H1_RELEASE),
                                   "sha256": args.h1_release_sha256}})
    if args.phase == "canary":
        req(args.v3_authority_job is not None and args.v3_release_sha256 is not None,
            "H3 canary needs v3 authority job/release")
        validate_v3_release(args.v3_release_sha256)
        return (args.v3_authority_job,
                [payload_sha, args.v3_release_sha256, str(V3_RELEASE)],
                {"v3_release_sha256": args.v3_release_sha256},
                {"v3_release": {"path": str(V3_RELEASE),
                                "sha256": args.v3_release_sha256}})
    if args.phase == "combined":
        required = (args.v3_release_sha256, args.replay_job,
                    args.replay_submission_sha256, args.replay_receipt_sha256,
                    args.reducer_job)
        req(all(item is not None for item in required), "H3 combined options incomplete")
        validate_v3_release(args.v3_release_sha256)
        replay_submission = base._existing_submission(
            "replay", args.replay_submission_sha256, args.replay_job)
        req(replay_submission["dependency_afterok"] == args.reducer_job,
            "H3 replay dependency drift")
        replay = ROOT / f"artifacts/replay/v4-r2-replay-h3-{args.reducer_job}.json"
        replay_value = base.h1.authority(replay, args.replay_receipt_sha256)
        req(replay_value.get("status") == "PASS_AUTHORIZE_V3_V4_R2_H3_COMBINED"
            and replay_value.get("authorizes_combined") is True
            and replay_value.get("h3_primary_rope_replay", {}).get("status")
                == "PASS_PRIMARY_ROPE_EVIDENCE",
            "H3 replay did not authorize combined")
        receipt = SUB / "combined-submission.json"
        inputs = {"v3_release_sha256": args.v3_release_sha256,
                  "v4_replay_receipt_sha256": args.replay_receipt_sha256,
                  "replay_job_id": args.replay_job,
                  "replay_submission_sha256": args.replay_submission_sha256}
        authorities = {
            "v3_release": {"path": str(V3_RELEASE), "sha256": args.v3_release_sha256},
            "v4_replay": {"path": str(replay), "sha256": args.replay_receipt_sha256},
            "replay_submission": {"path": str(SUB / "replay-submission.json"),
                                  "sha256": args.replay_submission_sha256}}
        argv = [payload_sha, str(V3_RELEASE), args.v3_release_sha256,
                str(replay), args.replay_receipt_sha256, args.replay_job,
                str(SUB / "replay-submission.json"),
                args.replay_submission_sha256, str(receipt)]
        return args.replay_job, argv, inputs, authorities
    if args.phase == "release":
        required = (args.combined_job, args.combined_submission_sha256,
                    args.combined_json, args.combined_json_sha256,
                    args.combined_csv, args.combined_csv_sha256)
        req(all(item is not None for item in required), "H3 release options incomplete")
        submission = base._existing_submission(
            "combined", args.combined_submission_sha256, args.combined_job)
        combined_json = Path(args.combined_json); combined_csv = Path(args.combined_csv)
        req(science.sha(combined_json) == args.combined_json_sha256
            and science.sha(combined_csv) == args.combined_csv_sha256,
            "H3 combined output hash drift")
        value = science.strict_json(combined_json, mode600=True)
        req(value.get("status") ==
            "PASS_H3_COMBINED_COMPUTATION_AWAIT_TERMINAL_RELEASE"
            and value.get("submission_binding", {}).get("combined_job_id")
                == args.combined_job,
            "H3 combined output did not await terminal release")
        receipt = SUB / "release-submission.json"
        inputs = {"combined_job_id": args.combined_job,
                  "combined_json_sha256": args.combined_json_sha256,
                  "combined_csv_sha256": args.combined_csv_sha256,
                  "combined_submission_sha256": args.combined_submission_sha256}
        authorities = {
            "combined_json": {"path": str(combined_json),
                              "sha256": args.combined_json_sha256},
            "combined_csv": {"path": str(combined_csv),
                             "sha256": args.combined_csv_sha256},
            "combined_submission": {"path": str(SUB / "combined-submission.json"),
                                    "sha256": args.combined_submission_sha256}}
        argv = [payload_sha, args.combined_job, str(combined_json),
                args.combined_json_sha256, str(combined_csv), args.combined_csv_sha256,
                str(SUB / "combined-submission.json"),
                args.combined_submission_sha256, str(receipt)]
        req(submission["job_id"] == args.combined_job, "H3 combined job drift")
        return args.combined_job, argv, inputs, authorities
    raise ValueError("not a manual H3 phase")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=tuple(SCRIPTS), required=True)
    parser.add_argument("--payload-sha256", required=True)
    for name in ("h1-release-sha256", "v3-authority-job", "v3-release-sha256",
                 "canary-job", "canary-submission-sha256", "canary-receipt-sha256",
                 "array-job", "production-submission-sha256", "reducer-job",
                 "reducer-submission-sha256", "reduction-sha256", "replay-job",
                 "replay-submission-sha256", "replay-receipt-sha256", "combined-job",
                 "combined-submission-sha256", "combined-json", "combined-json-sha256",
                 "combined-csv", "combined-csv-sha256"):
        parser.add_argument(f"--{name}")
    return parser.parse_args()


if __name__ == "__main__":
    configure()
    try: raise SystemExit(base.main())
    except (ValueError, OSError, json.JSONDecodeError,
            subprocess.CalledProcessError) as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr); raise SystemExit(2)
