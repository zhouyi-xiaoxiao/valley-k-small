#!/usr/bin/env python3
"""Append-only H3 v3 authority: H2 tail/bijection plus raw primary/ROPE."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import scientific_primary_replay_v4_r2_h3 as primary
import scientific_tail_replay_v4_r2_h2 as science
import verify_v3_release_for_v4_r2_h2 as h2

ROOT = h2.ROOT
H3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h3.json"


def validate(h1_release_sha256: str) -> dict[str, Any]:
    base = h2.validate(h1_release_sha256)
    primary_replay = primary.replay(
        h2.V3_MANIFEST, h2.V3_RAW, h2.V3_REDUCTION,
        expected_blocks=32, tail_replay=base["scientific_tail_replay"],
    )
    passed = (base["authorizes_v4_r2_h2"] is True
              and primary_replay["authorizes_ready_evidence"] is True)
    return {
        "schema": "grid2d-one-two-target-gating-v3-release-for-v4-r2-h3",
        "status": ("PASS_AUTHORIZE_V4_R2_H3_HARDWARE_CANARY" if passed else
                   primary_replay["status"]),
        "fixed_roots": base["fixed_roots"], "fixed_jobs": base["fixed_jobs"],
        "h2_tail_and_allocation_authority": base,
        "h3_primary_rope_replay": primary_replay,
        "authorizes_v4_r2_h3": passed,
    }


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    science.req(path == H3_RELEASE and not path.exists(),
                "H3 v3 release path exists/drifted")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".v3-h3-release.", dir=path.parent)
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
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = validate(args.h1_release_sha256); commit(args.output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr); return 2
    print(json.dumps({"status": payload["status"], "sha256": science.sha(args.output)},
                     sort_keys=True))
    return 0 if payload["authorizes_v4_r2_h3"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
