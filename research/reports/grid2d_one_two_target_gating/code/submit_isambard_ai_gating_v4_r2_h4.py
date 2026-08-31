#!/usr/bin/env python3
"""Append-only H4 submission machine with canonical combined/release paths."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import analyze_gpu_gating_v4_r2_combined_h4 as h4
import independent_replay_gpu_gating_v4_r2_h4 as replay_h4
import scientific_tail_replay_v4_r2_h2 as science
import submit_isambard_ai_gating_v4_r2_h2 as base
import verify_v3_release_for_v4_r2_h4 as v3_h4

ROOT = base.ROOT
SUB = ROOT / "artifacts/submission_h4"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h4_payload.sha256"
V3_RELEASE = h4.v3_release_path()
SCHEMA = h4.SUBMIT_SCHEMA
SCRIPTS = {
    "v3_authority": "isambard_ai_gating_v4_r2_v3_authority_h4.sbatch",
    "canary": "isambard_ai_gating_v4_r2_gpu_canary_h4.sbatch",
    "production": "isambard_ai_gating_v4_r2_fullnode_h4.sbatch",
    "reducer": "isambard_ai_gating_v4_r2_reduce_h4.sbatch",
    "replay": "isambard_ai_gating_v4_r2_replay_h4.sbatch",
    "combined": h4.COMBINED_SCRIPT,
    "release": "isambard_ai_gating_v4_r2_release_h4.sbatch",
}


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def configure() -> None:
    base.SUB = SUB; base.PAYLOAD = PAYLOAD; base.V3_RELEASE = V3_RELEASE
    base.SCHEMA = SCHEMA; base.SCRIPTS = SCRIPTS
    base.validate_v3_release = validate_v3_release
    base._manual_phase = manual_phase
    base.parse_args = parse_args


def validate_v3_release(expected_sha: str) -> dict[str, Any]:
    value = h4.validate_v3_receipt(expected_sha)
    req(value["schema"] == v3_h4.SCHEMA and value["status"] == v3_h4.STATUS
        and value["authorizes_v4_r2_h4"] is True,
        "H4 v3 release did not authorize canary")
    return value


def manual_phase(args: argparse.Namespace):
    payload_sha = args.payload_sha256
    if args.phase == "v3_authority":
        req(args.h1_release_sha256 is not None
            and science.HEX64.fullmatch(args.h1_release_sha256) is not None
            and science.sha(base.H1_RELEASE) == args.h1_release_sha256,
            "H4 v3 authority H1 release hash drift")
        return (
            "5789031", [payload_sha, args.h1_release_sha256],
            {"h1_v3_release_sha256": args.h1_release_sha256},
            {"h1_v3_release": {"path": str(base.H1_RELEASE),
                               "sha256": args.h1_release_sha256}},
        )
    if args.phase == "canary":
        req(args.v3_authority_job is not None
            and args.v3_release_sha256 is not None,
            "H4 canary needs v3 authority job/release")
        validate_v3_release(args.v3_release_sha256)
        return (
            args.v3_authority_job,
            [payload_sha, args.v3_release_sha256, str(V3_RELEASE)],
            {"v3_release_sha256": args.v3_release_sha256},
            {"v3_release": {"path": str(V3_RELEASE),
                            "sha256": args.v3_release_sha256}},
        )
    if args.phase == "combined":
        required = (
            args.array_job, args.reducer_job, args.replay_job,
            args.v3_release_sha256, args.replay_submission_sha256,
            args.replay_receipt_sha256,
        )
        req(all(item is not None for item in required),
            "H4 combined options incomplete")
        h4.decimal(args.array_job, args.reducer_job, args.replay_job)
        validate_v3_release(args.v3_release_sha256)
        h4.validate_replay_submission(
            expected_sha=args.replay_submission_sha256, h4_sha=payload_sha,
            array_job=args.array_job, reducer_job=args.reducer_job,
            replay_job=args.replay_job,
        )
        h4.validate_replay_receipt(
            args.replay_receipt_sha256, h4_sha=payload_sha,
            array_job=args.array_job, reducer_job=args.reducer_job,
            replay_job=args.replay_job,
        )
        receipt = h4.submission_path("combined")
        inputs = {
            "array_job_id": args.array_job,
            "reducer_job_id": args.reducer_job,
            "replay_job_id": args.replay_job,
            "v3_release_sha256": args.v3_release_sha256,
            "v4_replay_receipt_sha256": args.replay_receipt_sha256,
            "replay_submission_sha256": args.replay_submission_sha256,
        }
        authorities = {
            "v3_release": {"path": str(V3_RELEASE),
                           "sha256": args.v3_release_sha256},
            "v4_replay": {
                "path": str(h4.replay_receipt_path(args.reducer_job)),
                "sha256": args.replay_receipt_sha256,
            },
            "replay_submission": {
                "path": str(h4.submission_path("replay")),
                "sha256": args.replay_submission_sha256,
            },
        }
        argv = [
            payload_sha, args.array_job, args.reducer_job, args.replay_job,
            args.v3_release_sha256, args.replay_receipt_sha256,
            args.replay_submission_sha256,
        ]
        return args.replay_job, argv, inputs, authorities
    if args.phase == "release":
        required = (
            args.array_job, args.reducer_job, args.replay_job,
            args.combined_job, args.v3_release_sha256,
            args.replay_receipt_sha256, args.replay_submission_sha256,
            args.combined_submission_sha256, args.combined_json_sha256,
            args.combined_csv_sha256,
        )
        req(all(item is not None for item in required),
            "H4 release options incomplete")
        h4.decimal(args.array_job, args.reducer_job,
                   args.replay_job, args.combined_job)
        combined_submission = h4.validate_combined_submission(
            expected_sha=args.combined_submission_sha256, h4_sha=payload_sha,
            array_job=args.array_job, reducer_job=args.reducer_job,
            replay_job=args.replay_job, combined_job=args.combined_job,
            v3_sha=args.v3_release_sha256,
            replay_sha=args.replay_receipt_sha256,
            replay_submit_sha=args.replay_submission_sha256,
        )
        combined_json, combined_csv = h4.combined_paths(
            args.replay_job, args.combined_job)
        req(science.sha(combined_json) == args.combined_json_sha256
            and science.sha(combined_csv) == args.combined_csv_sha256,
            "H4 canonical combined hashes drift before release submission")
        value = science.strict_json(combined_json, mode600=True)
        authorization = value.get("authorization")
        req(set(value) == h4.COMBINED_KEYS
            and value["schema"] == h4.COMBINED_SCHEMA
            and value["status"] == h4.COMBINED_STATUS
            and value["authorizes_scientific_release"] is False
            and isinstance(authorization, dict)
            and set(authorization) == h4.AUTHORIZATION_KEYS
            and isinstance(value["csv"], dict)
            and set(value["csv"]) == h4.CSV_KEYS
            and authorization["array_job_id"] == args.array_job
            and authorization["reducer_job_id"] == args.reducer_job
            and authorization["replay_job_id"] == args.replay_job
            and authorization["combined_job_id"] == args.combined_job
            and authorization["v3_release_receipt_sha256"]
                == args.v3_release_sha256
            and authorization["v4_replay_receipt_sha256"]
                == args.replay_receipt_sha256
            and authorization["replay_submission_receipt_sha256"]
                == args.replay_submission_sha256
            and value["csv"] == {
                **value["csv"], "path": str(combined_csv),
                "sha256": args.combined_csv_sha256,
            }, "H4 combined output did not close canonical release inputs")
        receipt = h4.submission_path("release")
        inputs = {
            "array_job_id": args.array_job,
            "reducer_job_id": args.reducer_job,
            "replay_job_id": args.replay_job,
            "combined_job_id": args.combined_job,
            "v3_release_sha256": args.v3_release_sha256,
            "v4_replay_receipt_sha256": args.replay_receipt_sha256,
            "replay_submission_sha256": args.replay_submission_sha256,
            "combined_submission_sha256": args.combined_submission_sha256,
            "combined_json_sha256": args.combined_json_sha256,
            "combined_csv_sha256": args.combined_csv_sha256,
        }
        authorities = {
            "v3_release": {"path": str(V3_RELEASE),
                           "sha256": args.v3_release_sha256},
            "v4_replay": {
                "path": str(h4.replay_receipt_path(args.reducer_job)),
                "sha256": args.replay_receipt_sha256,
            },
            "replay_submission": {
                "path": str(h4.submission_path("replay")),
                "sha256": args.replay_submission_sha256,
            },
            "combined_submission": {
                "path": str(h4.submission_path("combined")),
                "sha256": args.combined_submission_sha256,
            },
            "combined_json": {"path": str(combined_json),
                              "sha256": args.combined_json_sha256},
            "combined_csv": {"path": str(combined_csv),
                             "sha256": args.combined_csv_sha256},
        }
        argv = [
            payload_sha, args.array_job, args.reducer_job, args.replay_job,
            args.combined_job, args.v3_release_sha256,
            args.replay_receipt_sha256, args.replay_submission_sha256,
            args.combined_submission_sha256, args.combined_json_sha256,
            args.combined_csv_sha256, str(receipt),
        ]
        req(combined_submission["job_id"] == args.combined_job,
            "H4 combined job drift")
        return args.combined_job, argv, inputs, authorities
    raise ValueError("not a manual H4 phase")


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
        "combined-submission-sha256", "combined-json-sha256",
        "combined-csv-sha256",
    ):
        parser.add_argument(f"--{name}")
    return parser.parse_args()


if __name__ == "__main__":
    configure()
    try:
        raise SystemExit(base.main())
    except (ValueError, OSError, json.JSONDecodeError,
            subprocess.CalledProcessError) as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        raise SystemExit(2)
