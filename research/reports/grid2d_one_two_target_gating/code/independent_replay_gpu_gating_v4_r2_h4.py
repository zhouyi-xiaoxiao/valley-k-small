#!/usr/bin/env python3
"""H4 v4 replay: H2 global checks, raw primary replay, exact runtime binding."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import independent_replay_gpu_gating_v4_r2_h2 as h2
import runtime_probe_v4_r2_h4 as runtime
import scientific_primary_replay_v4_r2_h3 as primary
import scientific_tail_replay_v4_r2_h2 as science
import verify_v3_release_for_v4_r2_h4 as v3_h4

ROOT = h2.ROOT
SUB = ROOT / "artifacts/submission_h4"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h4_payload.sha256"
V3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h4.json"
H4_SCHEMA = "grid2d-one-two-target-gating-v4-r2-independent-replay-h4"
H4_PASS = "PASS_AUTHORIZE_V3_V4_R2_H4_COMBINED"
SCRIPTS = {
    "canary": "isambard_ai_gating_v4_r2_gpu_canary_h4.sbatch",
    "production": "isambard_ai_gating_v4_r2_fullnode_h4.sbatch",
    "reducer": "isambard_ai_gating_v4_r2_reduce_h4.sbatch",
    "replay": "isambard_ai_gating_v4_r2_replay_h4.sbatch",
}
TOP_KEYS = {
    "schema", "status", "fixed_root", "jobs", "fixed_artifacts", "hashes",
    "raw", "reduction_inventory_digest", "extended_sacct", "submission_chain",
    "scientific_tail_replay", "h4_primary_rope_replay", "runtime_binding",
    "authorizes_combined",
}


def validate_v3_release(expected_sha: str) -> None:
    value = h2.h1.authority(V3_RELEASE, expected_sha)
    science.req(set(value) == v3_h4.TOP_KEYS and value.get("schema") == v3_h4.SCHEMA
                and value.get("status") == v3_h4.STATUS
                and value.get("authorizes_v4_r2_h4") is True
                and value.get("h4_primary_rope_replay", {}).get("status")
                    == "PASS_PRIMARY_ROPE_EVIDENCE",
                "H4 v3 release authority drift")


def replay(
    *, run: str, array: str, reducer: str, reduction_sha: str, h4_sha: str,
    production_submit: Path, production_submit_sha: str,
    reducer_submit: Path, reducer_submit_sha: str,
    runtime_receipt: Path, replay_job: str,
) -> dict[str, Any]:
    expected_runtime = ROOT / f"artifacts/runtime_h4/replay-{replay_job}.json"
    science.req(runtime_receipt == expected_runtime,
                "H4 replay runtime path drift")
    saved = {
        "SUB": h2.SUB, "PAYLOAD": h2.PAYLOAD, "V3_RELEASE": h2.V3_RELEASE,
        "H2_SCHEMA": h2.H2_SCHEMA, "H2_PASS": h2.H2_PASS,
        "SCRIPTS": h2.SCRIPTS, "validate_v3_release": h2.validate_v3_release,
    }
    h2.SUB = SUB; h2.PAYLOAD = PAYLOAD; h2.V3_RELEASE = V3_RELEASE
    h2.H2_SCHEMA = H4_SCHEMA; h2.H2_PASS = H4_PASS; h2.SCRIPTS = SCRIPTS
    h2.validate_v3_release = validate_v3_release
    try:
        base = h2.replay(
            run=run, array=array, reducer=reducer,
            reduction_sha=reduction_sha, h2_sha=h4_sha,
            production_submit=production_submit,
            production_submit_sha=production_submit_sha,
            reducer_submit=reducer_submit,
            reducer_submit_sha=reducer_submit_sha,
        )
    finally:
        for key, value in saved.items():
            setattr(h2, key, value)
    reduction = ROOT / (
        f"artifacts/outputs/isambard_ai_v4_r2/reduction-{array}-{reducer}/"
        "reduction_v4_r2.json"
    )
    raw = ROOT / f"artifacts/outputs/isambard_ai_v4_r2/production-{run}"
    primary_replay = primary.replay(
        h2.h1.MANIFEST, raw, reduction, expected_blocks=128,
        tail_replay=base["scientific_tail_replay"],
    )
    fixed = dict(base["fixed_artifacts"])
    fixed["h4_payload_sha256"] = fixed.pop("h2_payload_sha256")
    passed = (base["authorizes_combined"] is True
              and primary_replay["authorizes_ready_evidence"] is True)
    payload = {
        **base, "schema": H4_SCHEMA,
        "status": H4_PASS if passed else primary_replay["status"],
        "fixed_artifacts": fixed,
        "h4_primary_rope_replay": primary_replay,
        "runtime_binding": runtime.binding(
            runtime_receipt, phase="replay", job_id=replay_job),
        "authorizes_combined": passed,
    }
    science.req(set(payload) == TOP_KEYS, "H4 replay internal exact-key drift")
    return payload


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    science.req(not path.exists(), "H4 replay receipt exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".h4-replay.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-token", required=True)
    parser.add_argument("--array-job", required=True)
    parser.add_argument("--reducer-job", required=True)
    parser.add_argument("--reduction-sha256", required=True)
    parser.add_argument("--h4-payload-sha256", required=True)
    parser.add_argument("--production-submit", type=Path, required=True)
    parser.add_argument("--production-submit-sha256", required=True)
    parser.add_argument("--reducer-submit", type=Path, required=True)
    parser.add_argument("--reducer-submit-sha256", required=True)
    parser.add_argument("--runtime-receipt", type=Path, required=True)
    parser.add_argument("--slurm-job-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        expected = ROOT / f"artifacts/replay/v4-r2-replay-h4-{args.reducer_job}.json"
        science.req(args.output == expected and args.slurm_job_id.isdecimal(),
                    "H4 replay output/job path drift")
        payload = replay(
            run=args.run_token, array=args.array_job, reducer=args.reducer_job,
            reduction_sha=args.reduction_sha256, h4_sha=args.h4_payload_sha256,
            production_submit=args.production_submit,
            production_submit_sha=args.production_submit_sha256,
            reducer_submit=args.reducer_submit,
            reducer_submit_sha=args.reducer_submit_sha256,
            runtime_receipt=args.runtime_receipt, replay_job=args.slurm_job_id,
        )
        commit(args.output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": science.sha(args.output)},
                     sort_keys=True))
    return 0 if payload["authorizes_combined"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
