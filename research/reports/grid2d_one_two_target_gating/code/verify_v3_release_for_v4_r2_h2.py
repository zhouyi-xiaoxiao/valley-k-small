#!/usr/bin/env python3
"""Append-only H2 v3 authority with raw tail and allocation-bijection replay."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import analyze_gpu_gating_v4_r2_combined_h1 as h1
import scientific_tail_replay_v4_r2_h2 as science

ROOT = Path("/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727")
V3 = Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-20260726-r3")
H1_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h1.json"
H2_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h2.json"
V3_REDUCTION = V3 / (
    "artifacts/outputs/isambard_ai_v3/reductions/"
    "production-5788353-reduce-5788358/reduction.json"
)
V3_RAW = V3 / "artifacts/outputs/isambard_ai_v3/production-5788353"
V3_MANIFEST = V3 / "artifacts/data/gating_v3_production_manifest.json"
V3_SACCT = V3 / (
    "artifacts/outputs/isambard_ai_v3/reductions/"
    "production-5788353-reduce-5788358/sacct-production-5788353.psv"
)
CANARY_REDUCTION = V3 / (
    "artifacts/outputs/isambard_ai_v3/reductions/"
    "canary-5788353-reduce-5788356/reduction.json"
)
CANARY_SACCT = CANARY_REDUCTION.with_name("sacct-canary-5788353.psv")


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def validate(h1_release_sha256: str) -> dict[str, Any]:
    req(science.HEX64.fullmatch(h1_release_sha256) is not None
        and science.sha(H1_RELEASE) == h1_release_sha256,
        "fixed H1 v3 release hash drift")
    h1_value, _ = h1.validate_v3(h1_release_sha256)
    reduction = science.strict_json(V3_REDUCTION, mode600=True)
    inventory = reduction.get("inventory")
    req(isinstance(inventory, list) and len(inventory) == 5760,
        "v3 production inventory drift")
    production_allocations = science.replay_sacct_bijection(
        V3_SACCT, "5788357", inventory, task_count=480,
        cells_per_allocation=12, require_extended=False,
    )
    canary = science.strict_json(CANARY_REDUCTION, mode600=True)
    canary_inventory = canary.get("inventory")
    req(isinstance(canary_inventory, list) and len(canary_inventory) == 8,
        "v3 canary inventory drift")
    canary_allocations = science.replay_sacct_bijection(
        CANARY_SACCT, "5788354", canary_inventory, task_count=8,
        cells_per_allocation=1, require_extended=False,
    )
    scientific = science.recompute_tail_evidence(
        V3_MANIFEST, V3_RAW, V3_REDUCTION,
        expected_cells=5760, expected_blocks=32,
    )
    passed = scientific["status"] == "PASS_TAIL_EVIDENCE"
    return {
        "schema": "grid2d-one-two-target-gating-v3-release-for-v4-r2-h2",
        "status": ("PASS_AUTHORIZE_V4_R2_H2_HARDWARE_CANARY" if passed
                   else "HOLD_STAGE_A2_160K"),
        "fixed_roots": h1_value["fixed_roots"],
        "fixed_jobs": h1_value["fixed_jobs"],
        "h1_release": {"path": str(H1_RELEASE), "sha256": h1_release_sha256},
        "h1_evidence_digest": science.canonical_digest(h1_value),
        "production_allocation_bijection": production_allocations,
        "canary_allocation_bijection": canary_allocations,
        "scientific_tail_replay": scientific,
        "authorizes_v4_r2_h2": passed,
    }


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    req(path == H2_RELEASE and not path.exists(), "H2 v3 release path exists/drifted")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".v3-h2-release.", dir=path.parent)
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
        payload = validate(args.h1_release_sha256)
        commit(args.output, payload)
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"], "sha256": science.sha(args.output)},
                     sort_keys=True))
    return 0 if payload["authorizes_v4_r2_h2"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
