#!/usr/bin/env python3
"""Issue final H2 authority only after the combined job is terminal success."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import scientific_tail_replay_v4_r2_h2 as science

ROOT = Path("/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727")
SUB = ROOT / "artifacts/submission_h2"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h2_payload.sha256"
SCRIPT = "isambard_ai_gating_v4_r2_release_h2.sbatch"
SUBMIT_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h2-submission-v1"
TOP_KEYS = {
    "schema", "status", "phase", "job_id", "dependency_afterok",
    "payload_manifest_sha256", "phase_inputs", "script", "argv",
    "authorities", "scontrol_readback",
}


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def terminal_sacct(path: Path, combined_job: str) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        rows = list(reader); header = reader.fieldnames
    expected = [
        "JobIDRaw", "JobID", "State", "ExitCode", "ElapsedRaw",
        "AllocTRES", "ReqTRES", "NNodes",
    ]
    req(header == expected and len(rows) == 1, "combined terminal sacct shape drift")
    row = rows[0]
    req(set(row) == set(expected) and row["JobIDRaw"] == combined_job
        and row["JobID"] == combined_job
        and row["State"].split("+")[0] == "COMPLETED"
        and row["ExitCode"] == "0:0" and int(row["ElapsedRaw"]) > 0
        and int(row["NNodes"]) == 1,
        "combined job is not exact terminal COMPLETED/0:0")
    return {
        "independently_parsed": True, "job_id": combined_job,
        "state": "COMPLETED", "exit_code": "0:0",
        "elapsed_raw_seconds": int(row["ElapsedRaw"]),
        "alloc_tres": row["AllocTRES"], "req_tres": row["ReqTRES"],
        "nodes": 1, "receipt_sha256": science.sha(path),
    }


def validate_release_submission(
    path: Path, *, release_job: str, combined_job: str, h2_sha: str,
    combined_json: Path, combined_json_sha: str,
    combined_csv: Path, combined_csv_sha: str,
    combined_submit: Path, combined_submit_sha: str,
) -> dict[str, Any]:
    req(path == SUB / "release-submission.json", "release submission path drift")
    value = science.strict_json(path, mode600=True)
    req(set(value) == TOP_KEYS and value["schema"] == SUBMIT_SCHEMA
        and value["status"] == "SUBMITTED_WITH_EXACT_READBACK"
        and value["phase"] == "release" and value["job_id"] == release_job
        and value["dependency_afterok"] == combined_job
        and value["payload_manifest_sha256"] == h2_sha,
        "release submission envelope drift")
    inputs = {
        "combined_job_id": combined_job,
        "combined_json_sha256": combined_json_sha,
        "combined_csv_sha256": combined_csv_sha,
        "combined_submission_sha256": combined_submit_sha,
    }
    authorities = {
        "combined_json": {"path": str(combined_json), "sha256": combined_json_sha},
        "combined_csv": {"path": str(combined_csv), "sha256": combined_csv_sha},
        "combined_submission": {"path": str(combined_submit),
                                "sha256": combined_submit_sha},
    }
    req(value["phase_inputs"] == inputs and value["authorities"] == authorities,
        "release submission inputs/authorities drift")
    script = ROOT / "code" / SCRIPT
    req(value["script"] == {"path": f"code/{SCRIPT}", "sha256": science.sha(script)},
        "release script path/hash drift")
    args = [
        h2_sha, combined_job, str(combined_json), combined_json_sha,
        str(combined_csv), combined_csv_sha, str(combined_submit),
        combined_submit_sha, str(path),
    ]
    expected_argv = ["sbatch", "--parsable", f"--dependency=afterok:{combined_job}",
                     f"code/{SCRIPT}", *args]
    req(value["argv"] == expected_argv, "release exact sbatch argv drift")
    readback = value["scontrol_readback"]
    req(isinstance(readback, str) and f"JobId={release_job}" in readback
        and f"Dependency=afterok:{combined_job}" in readback
        and f"WorkDir={ROOT}" in readback and SCRIPT in readback,
        "release scontrol readback drift")
    return value


def finalize(
    *, h2_sha: str, combined_job: str, combined_json: Path,
    combined_json_sha: str, combined_csv: Path, combined_csv_sha: str,
    combined_submit: Path, combined_submit_sha: str,
    release_submit: Path, release_job: str, terminal_receipt: Path,
    runtime_receipt: Path,
) -> dict[str, Any]:
    req(science.sha(PAYLOAD) == h2_sha, "H2 payload drift at release")
    req(science.sha(combined_json) == combined_json_sha
        and science.sha(combined_csv) == combined_csv_sha
        and science.sha(combined_submit) == combined_submit_sha,
        "combined authority hash drift at release")
    combined = science.strict_json(combined_json, mode600=True)
    req(combined.get("schema") == "grid2d-one-two-target-gating-v4-r2-combined-h2"
        and combined.get("status") ==
            "PASS_H2_COMBINED_COMPUTATION_AWAIT_TERMINAL_RELEASE"
        and combined.get("authorizes_scientific_release") is False,
        "combined computation envelope drift")
    csv_record = combined.get("csv")
    req(isinstance(csv_record, dict) and csv_record.get("sha256") == combined_csv_sha
        and csv_record.get("rows") == 75,
        "combined CSV reverse receipt drift")
    binding = combined.get("submission_binding")
    req(isinstance(binding, dict)
        and binding.get("combined_job_id") == combined_job
        and binding.get("combined_submission_receipt_path") == str(combined_submit)
        and binding.get("combined_submission_receipt_sha256") == combined_submit_sha,
        "combined output did not reverse-bind its submission/job ID")
    combined_submission = science.strict_json(combined_submit, mode600=True)
    req(combined_submission.get("job_id") == combined_job
        and combined_submission.get("script") == binding.get("script")
        and combined_submission.get("argv") == binding.get("argv")
        and hashlib.sha256(combined_submission["scontrol_readback"].encode()).hexdigest()
            == binding.get("scontrol_readback_sha256"),
        "combined script/argv/readback reverse binding drift")
    release_submission = validate_release_submission(
        release_submit, release_job=release_job, combined_job=combined_job,
        h2_sha=h2_sha, combined_json=combined_json,
        combined_json_sha=combined_json_sha, combined_csv=combined_csv,
        combined_csv_sha=combined_csv_sha, combined_submit=combined_submit,
        combined_submit_sha=combined_submit_sha,
    )
    runtime = science.strict_json(runtime_receipt, mode600=True)
    req(runtime.get("status") == "PASS_FIXED_CONTAINER_PYTHON_GE_3_10"
        and runtime.get("phase") == "release"
        and runtime.get("slurm_job_id") == release_job,
        "release runtime receipt drift")
    terminal = terminal_sacct(terminal_receipt, combined_job)
    return {
        "schema": "grid2d-one-two-target-gating-v4-r2-h2-final-release-v1",
        "status": "PASS_AUTHORIZE_H2_SCIENTIFIC_INFERENCE",
        "h2_payload_manifest_sha256": h2_sha,
        "combined_job_id": combined_job,
        "combined_json": {"path": str(combined_json), "sha256": combined_json_sha},
        "combined_csv": {"path": str(combined_csv), "sha256": combined_csv_sha},
        "combined_submission": {"path": str(combined_submit),
                                "sha256": combined_submit_sha,
                                "script": binding["script"],
                                "argv": binding["argv"],
                                "scontrol_readback_sha256":
                                    binding["scontrol_readback_sha256"]},
        "terminal_slurm_receipt": {"path": str(terminal_receipt), **terminal},
        "release_submission": {"path": str(release_submit),
                               "sha256": science.sha(release_submit),
                               "job_id": release_job,
                               "script": release_submission["script"]},
        "runtime_receipt": {"path": str(runtime_receipt),
                            "sha256": science.sha(runtime_receipt)},
        "pack_heterogeneity_status": combined["pack_heterogeneity"]["status"],
        "authorizes_scientific_release": True,
    }


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    req(not path.exists(), "H2 final release receipt exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".h2-final-release.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h2-payload-sha256", required=True)
    parser.add_argument("--combined-job", required=True)
    parser.add_argument("--combined-json", type=Path, required=True)
    parser.add_argument("--combined-json-sha256", required=True)
    parser.add_argument("--combined-csv", type=Path, required=True)
    parser.add_argument("--combined-csv-sha256", required=True)
    parser.add_argument("--combined-submission", type=Path, required=True)
    parser.add_argument("--combined-submission-sha256", required=True)
    parser.add_argument("--release-submission", type=Path, required=True)
    parser.add_argument("--release-job", required=True)
    parser.add_argument("--terminal-receipt", type=Path, required=True)
    parser.add_argument("--runtime-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = finalize(
            h2_sha=args.h2_payload_sha256, combined_job=args.combined_job,
            combined_json=args.combined_json,
            combined_json_sha=args.combined_json_sha256,
            combined_csv=args.combined_csv,
            combined_csv_sha=args.combined_csv_sha256,
            combined_submit=args.combined_submission,
            combined_submit_sha=args.combined_submission_sha256,
            release_submit=args.release_submission,
            release_job=args.release_job,
            terminal_receipt=args.terminal_receipt,
            runtime_receipt=args.runtime_receipt,
        )
        commit(args.output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": science.sha(args.output)},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
