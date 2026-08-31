#!/usr/bin/env python3
"""Terminal H3 release over the preserved H2 receipt and sacct checks."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import finalize_gpu_gating_v4_r2_h2 as h2
import scientific_tail_replay_v4_r2_h2 as science

ROOT = h2.ROOT
SUB = ROOT / "artifacts/submission_h3"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h3_payload.sha256"
SCRIPT = "isambard_ai_gating_v4_r2_release_h3.sbatch"
SUBMIT_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h3-submission-v1"


def req(value: bool, message: str) -> None:
    if not value: raise ValueError(message)


def finalize(**kwargs: Any) -> dict[str, Any]:
    h3_sha = kwargs["h3_sha"]; combined_job = kwargs["combined_job"]
    combined_json = kwargs["combined_json"]; combined_json_sha = kwargs["combined_json_sha"]
    combined_csv = kwargs["combined_csv"]; combined_csv_sha = kwargs["combined_csv_sha"]
    combined_submit = kwargs["combined_submit"]; combined_submit_sha = kwargs["combined_submit_sha"]
    release_submit = kwargs["release_submit"]; release_job = kwargs["release_job"]
    terminal_receipt = kwargs["terminal_receipt"]; runtime_receipt = kwargs["runtime_receipt"]
    req(science.sha(PAYLOAD) == h3_sha and science.sha(combined_json) == combined_json_sha
        and science.sha(combined_csv) == combined_csv_sha
        and science.sha(combined_submit) == combined_submit_sha,
        "H3 release authority hash drift")
    combined = science.strict_json(combined_json, mode600=True)
    req(combined.get("schema") == "grid2d-one-two-target-gating-v4-r2-combined-h3"
        and combined.get("status") ==
            "PASS_H3_COMBINED_COMPUTATION_AWAIT_TERMINAL_RELEASE"
        and combined.get("authorizes_scientific_release") is False,
        "H3 combined computation envelope drift")
    req(combined.get("csv", {}).get("sha256") == combined_csv_sha
        and combined.get("csv", {}).get("rows") == 75,
        "H3 combined CSV reverse receipt drift")
    binding = combined.get("submission_binding", {})
    req(binding.get("combined_job_id") == combined_job
        and binding.get("combined_submission_receipt_path") == str(combined_submit)
        and binding.get("combined_submission_receipt_sha256") == combined_submit_sha,
        "H3 combined submission binding drift")
    combined_submission = science.strict_json(combined_submit, mode600=True)
    req(combined_submission.get("job_id") == combined_job
        and combined_submission.get("script") == binding.get("script")
        and combined_submission.get("argv") == binding.get("argv")
        and hashlib.sha256(combined_submission["scontrol_readback"].encode()).hexdigest()
            == binding.get("scontrol_readback_sha256"),
        "H3 combined script/argv/readback binding drift")
    saved = (h2.SUB, h2.PAYLOAD, h2.SCRIPT, h2.SUBMIT_SCHEMA)
    h2.SUB = SUB; h2.PAYLOAD = PAYLOAD; h2.SCRIPT = SCRIPT; h2.SUBMIT_SCHEMA = SUBMIT_SCHEMA
    try:
        release_submission = h2.validate_release_submission(
            release_submit, release_job=release_job, combined_job=combined_job,
            h2_sha=h3_sha, combined_json=combined_json,
            combined_json_sha=combined_json_sha, combined_csv=combined_csv,
            combined_csv_sha=combined_csv_sha, combined_submit=combined_submit,
            combined_submit_sha=combined_submit_sha)
    finally:
        h2.SUB, h2.PAYLOAD, h2.SCRIPT, h2.SUBMIT_SCHEMA = saved
    runtime = science.strict_json(runtime_receipt, mode600=True)
    req(runtime.get("schema") == "grid2d-one-two-target-gating-v4-r2-h3-runtime-v1"
        and runtime.get("status") == "PASS_PINNED_HOST_AND_SIF_PYTHON"
        and runtime.get("phase") == "release"
        and runtime.get("slurm_job_id") == release_job,
        "H3 release runtime receipt drift")
    terminal = h2.terminal_sacct(terminal_receipt, combined_job)
    return {
        "schema": "grid2d-one-two-target-gating-v4-r2-h3-final-release-v1",
        "status": "PASS_AUTHORIZE_H3_SCIENTIFIC_INFERENCE",
        "h3_payload_manifest_sha256": h3_sha, "combined_job_id": combined_job,
        "combined_json": {"path": str(combined_json), "sha256": combined_json_sha},
        "combined_csv": {"path": str(combined_csv), "sha256": combined_csv_sha},
        "combined_submission": {"path": str(combined_submit), "sha256": combined_submit_sha,
                                "script": binding["script"], "argv": binding["argv"],
                                "scontrol_readback_sha256": binding["scontrol_readback_sha256"]},
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h3-payload-sha256", required=True); parser.add_argument("--combined-job", required=True)
    parser.add_argument("--combined-json", type=Path, required=True); parser.add_argument("--combined-json-sha256", required=True)
    parser.add_argument("--combined-csv", type=Path, required=True); parser.add_argument("--combined-csv-sha256", required=True)
    parser.add_argument("--combined-submission", type=Path, required=True); parser.add_argument("--combined-submission-sha256", required=True)
    parser.add_argument("--release-submission", type=Path, required=True); parser.add_argument("--release-job", required=True)
    parser.add_argument("--terminal-receipt", type=Path, required=True); parser.add_argument("--runtime-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    try:
        payload = finalize(h3_sha=args.h3_payload_sha256, combined_job=args.combined_job,
            combined_json=args.combined_json, combined_json_sha=args.combined_json_sha256,
            combined_csv=args.combined_csv, combined_csv_sha=args.combined_csv_sha256,
            combined_submit=args.combined_submission, combined_submit_sha=args.combined_submission_sha256,
            release_submit=args.release_submission, release_job=args.release_job,
            terminal_receipt=args.terminal_receipt, runtime_receipt=args.runtime_receipt)
        h2.commit(args.output, payload)
    except Exception as error: print(f"FAIL-CLOSED: {error}", file=os.sys.stderr); return 2
    print(json.dumps({"status": payload["status"], "sha256": science.sha(args.output)}, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
