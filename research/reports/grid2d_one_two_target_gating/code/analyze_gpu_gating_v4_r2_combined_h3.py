#!/usr/bin/env python3
"""H3 combined analysis over raw-primary-authorized v3/v4 receipts."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
from typing import Any

import numpy as np

import analyze_gpu_gating_v4_r2_combined as statistics
import analyze_gpu_gating_v4_r2_combined_h2 as h2
import scientific_tail_replay_v4_r2_h2 as science

ROOT = h2.ROOT
V3 = h2.V3
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h3_payload.sha256"
V3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h3.json"
SUB = ROOT / "artifacts/submission_h3"
SUBMIT_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h3-submission-v1"
COMBINED_SCRIPT = "isambard_ai_gating_v4_r2_combined_h3.sbatch"


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def validate_combined_submission(*args: Any, **kwargs: Any) -> dict[str, Any]:
    saved = (h2.SUB, h2.SUBMIT_SCHEMA, h2.COMBINED_SCRIPT)
    h2.SUB = SUB; h2.SUBMIT_SCHEMA = SUBMIT_SCHEMA; h2.COMBINED_SCRIPT = COMBINED_SCRIPT
    try:
        return h2.validate_combined_submission(*args, **kwargs)
    finally:
        h2.SUB, h2.SUBMIT_SCHEMA, h2.COMBINED_SCRIPT = saved


def analyze(
    *, h3_sha: str, v3_path: Path, v3_sha: str, replay_path: Path,
    replay_sha: str, replay_job: str, replay_submit: Path,
    replay_submit_sha: str, combined_submit: Path, slurm_job_id: str,
    runtime_receipt: Path,
) -> dict[str, Any]:
    req(science.sha(PAYLOAD) == h3_sha, "H3 payload hash drift")
    req(v3_path == V3_RELEASE and science.sha(v3_path) == v3_sha,
        "H3 v3 release path/hash drift")
    v3_release = science.strict_json(v3_path, mode600=True)
    req(v3_release.get("schema") ==
        "grid2d-one-two-target-gating-v3-release-for-v4-r2-h3"
        and v3_release.get("status") == "PASS_AUTHORIZE_V4_R2_H3_HARDWARE_CANARY"
        and v3_release.get("authorizes_v4_r2_h3") is True
        and v3_release.get("h3_primary_rope_replay", {}).get("status")
            == "PASS_PRIMARY_ROPE_EVIDENCE",
        "H3 v3 release did not pass independent primary replay")
    req(replay_path.parent == ROOT / "artifacts/replay"
        and science.sha(replay_path) == replay_sha,
        "H3 replay path/hash drift")
    replay = science.strict_json(replay_path, mode600=True)
    req(replay.get("schema") ==
        "grid2d-one-two-target-gating-v4-r2-independent-replay-h3"
        and replay.get("status") == "PASS_AUTHORIZE_V3_V4_R2_H3_COMBINED"
        and replay.get("authorizes_combined") is True
        and replay.get("h3_primary_rope_replay", {}).get("status")
            == "PASS_PRIMARY_ROPE_EVIDENCE",
        "H3 v4 replay did not pass independent primary replay")
    submission = validate_combined_submission(
        combined_submit, job_id=slurm_job_id, replay_job=replay_job,
        h2_sha=h3_sha, v3_path=v3_path, v3_sha=v3_sha,
        replay_path=replay_path, replay_sha=replay_sha,
        replay_submit=replay_submit, replay_submit_sha=replay_submit_sha,
    )
    runtime = science.strict_json(runtime_receipt, mode600=True)
    req(runtime.get("schema") == "grid2d-one-two-target-gating-v4-r2-h3-runtime-v1"
        and runtime.get("status") == "PASS_PINNED_HOST_AND_SIF_PYTHON"
        and runtime.get("phase") == "combined"
        and runtime.get("slurm_job_id") == slurm_job_id,
        "H3 combined runtime receipt drift")
    h2_authority = v3_release["h2_tail_and_allocation_authority"]
    h1_path = Path(h2_authority["h1_release"]["path"])
    req(science.sha(h1_path) == h2_authority["h1_release"]["sha256"],
        "nested H1 release hash drift")
    h1_release = science.strict_json(h1_path, mode600=True)
    v3_csv = V3 / ("artifacts/outputs/isambard_ai_v3/reductions/"
                   "production-5788353-reduce-5788358/reduction.csv")
    req(science.sha(v3_csv) == h1_release["evidence_hashes"]["reduction_csv"],
        "H3 v3 CSV reverse hash drift")
    jobs = replay["jobs"]
    v4_csv = ROOT / (f"artifacts/outputs/isambard_ai_v4_r2/reduction-"
                     f"{jobs['array']}-{jobs['reducer']}/reduction_v4_r2.csv")
    req(science.sha(v4_csv) == replay["hashes"]["reduction_csv"],
        "H3 v4 CSV reverse hash drift")
    values3 = statistics.csv_values(v3_csv, 32, science.sha(v3_csv))
    values4 = statistics.csv_values(v4_csv, 128, science.sha(v4_csv))
    a3 = statistics.effects(values3, 32); a4 = statistics.effects(values4, 128)
    pooled = np.vstack((a3, a4)); req(pooled.shape == (160, 75), "H3 pooled shape drift")
    contract = science.strict_json(h2.HETERO_CONTRACT)
    heterogeneity = h2.pack_heterogeneity(a3, a4, contract)
    return {
        "schema": "grid2d-one-two-target-gating-v4-r2-combined-h3",
        "status": "PASS_H3_COMBINED_COMPUTATION_AWAIT_TERMINAL_RELEASE",
        "authorization": {
            "h3_payload_manifest_sha256": h3_sha,
            "v3_release_receipt_sha256": v3_sha,
            "v4_replay_receipt_sha256": replay_sha,
            "replay_submission_receipt_sha256": replay_submit_sha,
            "v3_primary_raw_replay_digest": science.canonical_digest(
                v3_release["h3_primary_rope_replay"]),
            "v4_primary_raw_replay_digest": science.canonical_digest(
                replay["h3_primary_rope_replay"]),
            "v3_reduction_csv_sha256": science.sha(v3_csv),
            "v4_reduction_csv_sha256": science.sha(v4_csv),
        },
        "submission_binding": {
            "combined_job_id": slurm_job_id,
            "combined_submission_receipt_path": str(combined_submit),
            "combined_submission_receipt_sha256": science.sha(combined_submit),
            "script": submission["script"], "argv": submission["argv"],
            "scontrol_readback_sha256": hashlib.sha256(
                submission["scontrol_readback"].encode()).hexdigest(),
            "runtime_receipt_path": str(runtime_receipt),
            "runtime_receipt_sha256": science.sha(runtime_receipt),
        },
        "primary": {
            "v3_only": statistics.primary(a3, "v3 pack"),
            "v4_only": statistics.primary(a4, "v4-r2 reflect pack"),
            "combined": statistics.primary(pooled, "v3 plus independent v4-r2 packs"),
        },
        "surface": {
            "v3_only": statistics.max_t(a3, 2026072699),
            "v4_only": statistics.max_t(a4, 2026072700),
            "combined": statistics.max_t(pooled, 2026072701),
        },
        "pack_heterogeneity": heterogeneity,
        "authorizes_scientific_release": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h3-payload-sha256", required=True)
    parser.add_argument("--v3-release", type=Path, required=True)
    parser.add_argument("--v3-release-sha256", required=True)
    parser.add_argument("--v4-replay-receipt", type=Path, required=True)
    parser.add_argument("--v4-replay-sha256", required=True)
    parser.add_argument("--replay-job", required=True)
    parser.add_argument("--replay-submission", type=Path, required=True)
    parser.add_argument("--replay-submission-sha256", required=True)
    parser.add_argument("--combined-submission", type=Path, required=True)
    parser.add_argument("--slurm-job-id", required=True)
    parser.add_argument("--runtime-receipt", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = analyze(
            h3_sha=args.h3_payload_sha256, v3_path=args.v3_release,
            v3_sha=args.v3_release_sha256, replay_path=args.v4_replay_receipt,
            replay_sha=args.v4_replay_sha256, replay_job=args.replay_job,
            replay_submit=args.replay_submission,
            replay_submit_sha=args.replay_submission_sha256,
            combined_submit=args.combined_submission,
            slurm_job_id=args.slurm_job_id, runtime_receipt=args.runtime_receipt)
        buffer = io.StringIO(newline=""); rows = payload["surface"]["combined"]["rows"]
        writer = csv.DictWriter(buffer, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows); csv_data = buffer.getvalue().encode()
        payload["csv"] = {"filename": args.output_csv.name,
                          "sha256": hashlib.sha256(csv_data).hexdigest(), "rows": 75}
        json_data = (json.dumps(payload, indent=2, sort_keys=True,
                                allow_nan=False) + "\n").encode()
        h2.commit(args.output_csv, csv_data)
        try: h2.commit(args.output_json, json_data)
        except BaseException: args.output_csv.unlink(missing_ok=True); raise
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr); return 2
    print(json.dumps({"status": payload["status"],
                      "combined_job_id": args.slurm_job_id}, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
