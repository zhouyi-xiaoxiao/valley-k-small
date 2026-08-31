#!/usr/bin/env python3
"""Terminal H4 release with canonical paths and independent inference replay."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

import analyze_gpu_gating_v4_r2_combined_h4 as h4
import finalize_gpu_gating_v4_r2_h2 as h2_final
import runtime_probe_v4_r2_h4 as runtime
import scientific_tail_replay_v4_r2_h2 as science

ROOT = h4.ROOT
PAYLOAD = h4.PAYLOAD
SUB = h4.SUB
SCRIPT = "isambard_ai_gating_v4_r2_release_h4.sbatch"
FINAL_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h4-final-release-v1"
FINAL_STATUS = "PASS_AUTHORIZE_H4_SCIENTIFIC_INFERENCE"
FINAL_KEYS = {
    "schema", "status", "h4_payload_manifest_sha256", "jobs",
    "combined_json", "combined_csv", "v3_release", "v4_replay",
    "replay_submission", "combined_submission", "release_submission",
    "runtime_receipts", "terminal_slurm_receipt",
    "pack_heterogeneity_status", "authorizes_scientific_release",
}


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def release_submission_path() -> Path:
    return h4.submission_path("release")


def terminal_path(replay_job: str, combined_job: str) -> Path:
    h4.decimal(replay_job, combined_job)
    return ROOT / (
        f"artifacts/releases_h4/replay-{replay_job}-combined-{combined_job}-terminal.psv"
    )


def final_path(replay_job: str, combined_job: str, release_job: str) -> Path:
    h4.decimal(replay_job, combined_job, release_job)
    return ROOT / (
        "artifacts/releases_h4/"
        f"final-release-replay-{replay_job}-combined-{combined_job}-"
        f"release-{release_job}.json"
    )


def expected_submission_binding(
    submission: Mapping[str, Any], *, combined_submit_sha: str,
    replay_job: str, replay_submit_sha: str, combined_job: str,
) -> dict[str, Any]:
    value = {
        "combined_job_id": combined_job,
        "combined_submission_receipt_path": str(h4.submission_path("combined")),
        "combined_submission_receipt_sha256": combined_submit_sha,
        "replay_job_id": replay_job,
        "replay_submission_receipt_path": str(h4.submission_path("replay")),
        "replay_submission_receipt_sha256": replay_submit_sha,
        "script": submission["script"], "argv": submission["argv"],
        "scontrol_readback_sha256": hashlib.sha256(
            submission["scontrol_readback"].encode()).hexdigest(),
    }
    req(set(value) == h4.SUBMISSION_BINDING_KEYS,
        "H4 expected submission-binding key drift")
    return value


def expected_csv_record(csv_path: Path, csv_sha: str, fieldnames: list[str]
                        ) -> dict[str, Any]:
    value = {
        "path": str(csv_path), "filename": csv_path.name,
        "sha256": csv_sha, "rows": 75, "fieldnames": fieldnames,
    }
    req(set(value) == h4.CSV_KEYS, "H4 expected CSV record key drift")
    return value


def validate_combined_payload(
    combined: Mapping[str, Any], *, combined_path: Path, csv_path: Path,
    replay_job: str, combined_job: str,
    expected_authorization: Mapping[str, Any],
    expected_submission: Mapping[str, Any],
    expected_runtime: Mapping[str, Any],
    expected_primary: Mapping[str, Any], expected_surface: Mapping[str, Any],
    expected_heterogeneity: Mapping[str, Any],
    expected_csv: Mapping[str, Any],
) -> None:
    """Pure exact-tree gate used by runtime finalization and killing tests."""
    canonical_json, canonical_csv = h4.combined_paths(replay_job, combined_job)
    req(combined_path == canonical_json and csv_path == canonical_csv,
        "H4 combined JSON/CSV path is not canonical")
    req(set(combined) == h4.COMBINED_KEYS
        and combined.get("schema") == h4.COMBINED_SCHEMA
        and combined.get("status") == h4.COMBINED_STATUS
        and combined.get("authorizes_scientific_release") is False,
        "H4 combined exact schema/envelope drift")
    req(isinstance(combined.get("authorization"), dict)
        and set(combined["authorization"]) == h4.AUTHORIZATION_KEYS,
        "H4 combined authorization exact-key drift")
    req(isinstance(combined.get("submission_binding"), dict)
        and set(combined["submission_binding"]) == h4.SUBMISSION_BINDING_KEYS,
        "H4 combined submission-binding exact-key drift")
    req(isinstance(combined.get("csv"), dict)
        and set(combined["csv"]) == h4.CSV_KEYS,
        "H4 combined CSV exact-key drift")
    science.close_tree(combined["authorization"], dict(expected_authorization),
                       "H4 combined.authorization")
    science.close_tree(combined["submission_binding"], dict(expected_submission),
                       "H4 combined.submission_binding")
    science.close_tree(combined["runtime_binding"], dict(expected_runtime),
                       "H4 combined.runtime_binding")
    # These three comparisons are to fresh CSV-derived recomputations.  A PASS
    # string or a synchronously updated outer SHA can never substitute for them.
    science.close_tree(combined["primary"], dict(expected_primary),
                       "H4 combined.primary")
    science.close_tree(combined["surface"], dict(expected_surface),
                       "H4 combined.surface")
    science.close_tree(combined["pack_heterogeneity"],
                       dict(expected_heterogeneity),
                       "H4 combined.pack_heterogeneity")
    science.close_tree(combined["csv"], dict(expected_csv), "H4 combined.csv")


def validate_release_submission(
    *, h4_sha: str, array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, release_job: str, v3_sha: str, replay_sha: str,
    replay_submit_sha: str, combined_submit_sha: str,
    combined_json_sha: str, combined_csv_sha: str,
) -> dict[str, Any]:
    path = release_submission_path()
    value = h4.read_submission(path, science.sha(path))
    combined_json, combined_csv = h4.combined_paths(replay_job, combined_job)
    inputs = {
        "array_job_id": array_job, "reducer_job_id": reducer_job,
        "replay_job_id": replay_job, "combined_job_id": combined_job,
        "v3_release_sha256": v3_sha,
        "v4_replay_receipt_sha256": replay_sha,
        "replay_submission_sha256": replay_submit_sha,
        "combined_submission_sha256": combined_submit_sha,
        "combined_json_sha256": combined_json_sha,
        "combined_csv_sha256": combined_csv_sha,
    }
    authorities = {
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
    req(value["phase"] == "release" and value["job_id"] == release_job
        and value["dependency_afterok"] == combined_job
        and value["payload_manifest_sha256"] == h4_sha
        and value["phase_inputs"] == inputs and value["authorities"] == authorities,
        "H4 release submission full authority closure drift")
    args = [
        h4_sha, array_job, reducer_job, replay_job, combined_job, v3_sha,
        replay_sha, replay_submit_sha, combined_submit_sha,
        combined_json_sha, combined_csv_sha, str(path),
    ]
    expected_argv = [
        "sbatch", "--parsable", f"--dependency=afterok:{combined_job}",
        f"code/{SCRIPT}", *args,
    ]
    readback = value["scontrol_readback"]
    req(value["script"] == h4.script_record(SCRIPT)
        and value["argv"] == expected_argv and isinstance(readback, str)
        and f"JobId={release_job}" in readback
        and f"Dependency=afterok:{combined_job}" in readback
        and f"WorkDir={ROOT}" in readback and SCRIPT in readback,
        "H4 release submission script/argv/readback drift")
    return value


def finalize(
    *, h4_sha: str, array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, release_job: str, v3_sha: str, replay_sha: str,
    replay_submit_sha: str, combined_submit_sha: str,
    combined_json_sha: str, combined_csv_sha: str,
) -> dict[str, Any]:
    h4.decimal(array_job, reducer_job, replay_job, combined_job, release_job)
    req(science.sha(PAYLOAD) == h4_sha, "H4 payload drift at final release")
    combined_json, combined_csv = h4.combined_paths(replay_job, combined_job)
    req(science.sha(combined_json) == combined_json_sha
        and science.sha(combined_csv) == combined_csv_sha,
        "H4 canonical combined output hash drift")
    combined = science.strict_json(combined_json, mode600=True)

    # Reopen every canonical upstream authority instead of trusting the
    # combined receipt's PASS fields or its caller-supplied paths.
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
    expected_submission = expected_submission_binding(
        combined_submission, combined_submit_sha=combined_submit_sha,
        replay_job=replay_job, replay_submit_sha=replay_submit_sha,
        combined_job=combined_job,
    )
    combined_runtime_path = h4.runtime_path("combined", combined_job)
    expected_runtime = runtime.binding(
        combined_runtime_path, phase="combined", job_id=combined_job)
    csv_data, fieldnames = h4.csv_bytes(computed["surface"])
    recomputed_csv_sha = hashlib.sha256(csv_data).hexdigest()
    req(recomputed_csv_sha == combined_csv_sha
        and combined_csv.read_bytes() == csv_data,
        "H4 combined CSV bytes do not equal independent surface recomputation")
    expected_csv = expected_csv_record(
        combined_csv, combined_csv_sha, fieldnames)
    validate_combined_payload(
        combined, combined_path=combined_json, csv_path=combined_csv,
        replay_job=replay_job, combined_job=combined_job,
        expected_authorization=expected_authorization,
        expected_submission=expected_submission,
        expected_runtime=expected_runtime,
        expected_primary=computed["primary"],
        expected_surface=computed["surface"],
        expected_heterogeneity=computed["pack_heterogeneity"],
        expected_csv=expected_csv,
    )
    release_submission = validate_release_submission(
        h4_sha=h4_sha, array_job=array_job, reducer_job=reducer_job,
        replay_job=replay_job, combined_job=combined_job,
        release_job=release_job, v3_sha=v3_sha, replay_sha=replay_sha,
        replay_submit_sha=replay_submit_sha,
        combined_submit_sha=combined_submit_sha,
        combined_json_sha=combined_json_sha,
        combined_csv_sha=combined_csv_sha,
    )
    release_runtime_path = h4.runtime_path("release", release_job)
    release_runtime = runtime.binding(
        release_runtime_path, phase="release", job_id=release_job)
    terminal_receipt = terminal_path(replay_job, combined_job)
    terminal = h2_final.terminal_sacct(terminal_receipt, combined_job)
    payload = {
        "schema": FINAL_SCHEMA, "status": FINAL_STATUS,
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
            "sha256": replay_submit_sha,
            "job_id": replay_submission["job_id"],
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
        },
        "runtime_receipts": {
            "v3_authority": v3_release["runtime_binding"],
            "replay": replay["runtime_binding"],
            "combined": expected_runtime, "release": release_runtime,
        },
        "terminal_slurm_receipt": {
            "path": str(terminal_receipt), **terminal,
        },
        "pack_heterogeneity_status": computed["pack_heterogeneity"]["status"],
        "authorizes_scientific_release": True,
    }
    req(set(payload) == FINAL_KEYS, "H4 final receipt internal exact-key drift")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
        output = final_path(args.replay_job, args.combined_job, args.release_job)
        payload = finalize(
            h4_sha=args.h4_payload_sha256, array_job=args.array_job,
            reducer_job=args.reducer_job, replay_job=args.replay_job,
            combined_job=args.combined_job, release_job=args.release_job,
            v3_sha=args.v3_release_sha256, replay_sha=args.v4_replay_sha256,
            replay_submit_sha=args.replay_submission_sha256,
            combined_submit_sha=args.combined_submission_sha256,
            combined_json_sha=args.combined_json_sha256,
            combined_csv_sha=args.combined_csv_sha256,
        )
        h2_final.commit(output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": science.sha(output),
                      "canonical_release": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
