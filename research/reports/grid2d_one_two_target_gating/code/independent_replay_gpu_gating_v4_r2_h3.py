#!/usr/bin/env python3
"""H3 v4 replay: H2 uniqueness/tail plus independent raw primary/ROPE."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import independent_replay_gpu_gating_v4_r2_h2 as h2
import scientific_primary_replay_v4_r2_h3 as primary
import scientific_tail_replay_v4_r2_h2 as science

ROOT = h2.ROOT
SUB = ROOT / "artifacts/submission_h3"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h3_payload.sha256"
V3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h3.json"
H3_SCHEMA = "grid2d-one-two-target-gating-v4-r2-independent-replay-h3"
H3_PASS = "PASS_AUTHORIZE_V3_V4_R2_H3_COMBINED"
SCRIPTS = {
    "canary": "isambard_ai_gating_v4_r2_gpu_canary_h3.sbatch",
    "production": "isambard_ai_gating_v4_r2_fullnode_h3.sbatch",
    "reducer": "isambard_ai_gating_v4_r2_reduce_h3.sbatch",
    "replay": "isambard_ai_gating_v4_r2_replay_h3.sbatch",
}


def validate_v3_release(expected_sha: str) -> None:
    value = h2.h1.authority(V3_RELEASE, expected_sha)
    science.req(value.get("schema") ==
                "grid2d-one-two-target-gating-v3-release-for-v4-r2-h3"
                and value.get("status") ==
                    "PASS_AUTHORIZE_V4_R2_H3_HARDWARE_CANARY"
                and value.get("authorizes_v4_r2_h3") is True
                and value.get("h3_primary_rope_replay", {}).get("status")
                    == "PASS_PRIMARY_ROPE_EVIDENCE",
                "H3 v3 release authority drift")


def replay(
    *, run: str, array: str, reducer: str, reduction_sha: str, h3_sha: str,
    production_submit: Path, production_submit_sha: str,
    reducer_submit: Path, reducer_submit_sha: str,
) -> dict[str, Any]:
    saved = {
        "SUB": h2.SUB, "PAYLOAD": h2.PAYLOAD, "V3_RELEASE": h2.V3_RELEASE,
        "H2_SCHEMA": h2.H2_SCHEMA, "H2_PASS": h2.H2_PASS,
        "SCRIPTS": h2.SCRIPTS, "validate_v3_release": h2.validate_v3_release,
    }
    h2.SUB = SUB; h2.PAYLOAD = PAYLOAD; h2.V3_RELEASE = V3_RELEASE
    h2.H2_SCHEMA = H3_SCHEMA; h2.H2_PASS = H3_PASS; h2.SCRIPTS = SCRIPTS
    h2.validate_v3_release = validate_v3_release
    try:
        base = h2.replay(
            run=run, array=array, reducer=reducer,
            reduction_sha=reduction_sha, h2_sha=h3_sha,
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
    fixed["h3_payload_sha256"] = fixed.pop("h2_payload_sha256")
    passed = (base["authorizes_combined"] is True
              and primary_replay["authorizes_ready_evidence"] is True)
    return {
        **base, "schema": H3_SCHEMA,
        "status": H3_PASS if passed else primary_replay["status"],
        "fixed_artifacts": fixed,
        "h3_primary_rope_replay": primary_replay,
        "authorizes_combined": passed,
    }


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    science.req(not path.exists(), "H3 replay receipt exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".h3-replay.", dir=path.parent)
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
    parser.add_argument("--h3-payload-sha256", required=True)
    parser.add_argument("--production-submit", type=Path, required=True)
    parser.add_argument("--production-submit-sha256", required=True)
    parser.add_argument("--reducer-submit", type=Path, required=True)
    parser.add_argument("--reducer-submit-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        expected = ROOT / f"artifacts/replay/v4-r2-replay-h3-{args.reducer_job}.json"
        science.req(args.output == expected, "H3 replay output path drift")
        payload = replay(
            run=args.run_token, array=args.array_job, reducer=args.reducer_job,
            reduction_sha=args.reduction_sha256, h3_sha=args.h3_payload_sha256,
            production_submit=args.production_submit,
            production_submit_sha=args.production_submit_sha256,
            reducer_submit=args.reducer_submit,
            reducer_submit_sha=args.reducer_submit_sha256,
        )
        commit(args.output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr); return 2
    print(json.dumps({"status": payload["status"], "sha256": science.sha(args.output)},
                     sort_keys=True))
    return 0 if payload["authorizes_combined"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
