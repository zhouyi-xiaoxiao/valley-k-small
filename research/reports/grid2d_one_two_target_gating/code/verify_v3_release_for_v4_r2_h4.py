#!/usr/bin/env python3
"""H4 v3 authority with exact receipt and complete runtime binding."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import runtime_probe_v4_r2_h4 as runtime
import scientific_tail_replay_v4_r2_h2 as science
import verify_v3_release_for_v4_r2_h3 as h3

ROOT = h3.ROOT
H4_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h4.json"
SCHEMA = "grid2d-one-two-target-gating-v3-release-for-v4-r2-h4"
STATUS = "PASS_AUTHORIZE_V4_R2_H4_HARDWARE_CANARY"
TOP_KEYS = {
    "schema", "status", "fixed_roots", "fixed_jobs",
    "h2_tail_and_allocation_authority", "h4_primary_rope_replay",
    "runtime_binding", "authorizes_v4_r2_h4",
}


def validate(h1_release_sha256: str, *, runtime_receipt: Path,
             slurm_job_id: str) -> dict[str, Any]:
    expected_runtime = ROOT / f"artifacts/runtime_h4/v3_authority-{slurm_job_id}.json"
    science.req(runtime_receipt == expected_runtime,
                "H4 v3 authority runtime path drift")
    base = h3.validate(h1_release_sha256)
    primary_replay = base["h3_primary_rope_replay"]
    passed = (base["authorizes_v4_r2_h3"] is True
              and primary_replay.get("status") == "PASS_PRIMARY_ROPE_EVIDENCE"
              and primary_replay.get("authorizes_ready_evidence") is True)
    payload = {
        "schema": SCHEMA,
        "status": STATUS if passed else primary_replay.get("status"),
        "fixed_roots": base["fixed_roots"],
        "fixed_jobs": base["fixed_jobs"],
        "h2_tail_and_allocation_authority":
            base["h2_tail_and_allocation_authority"],
        "h4_primary_rope_replay": primary_replay,
        "runtime_binding": runtime.binding(
            runtime_receipt, phase="v3_authority", job_id=slurm_job_id),
        "authorizes_v4_r2_h4": passed,
    }
    science.req(set(payload) == TOP_KEYS, "H4 v3 receipt internal key drift")
    return payload


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    science.req(path == H4_RELEASE and not path.exists(),
                "H4 v3 release path exists/drifted")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".v3-h4-release.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h1-release-sha256", required=True)
    parser.add_argument("--runtime-receipt", type=Path, required=True)
    parser.add_argument("--slurm-job-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = validate(
            args.h1_release_sha256, runtime_receipt=args.runtime_receipt,
            slurm_job_id=args.slurm_job_id,
        )
        commit(args.output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": science.sha(args.output)},
                     sort_keys=True))
    return 0 if payload["authorizes_v4_r2_h4"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
