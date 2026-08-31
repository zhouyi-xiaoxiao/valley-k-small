#!/usr/bin/env python3
"""H2 v4-r2 replay: H1 deep checks plus bijection and raw tail authority."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import independent_replay_gpu_gating_v4_r2_h1 as h1
import scientific_tail_replay_v4_r2_h2 as science

ROOT = h1.ROOT
SUB = ROOT / "artifacts/submission_h2"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h2_payload.sha256"
V3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h2.json"
H2_SCHEMA = "grid2d-one-two-target-gating-v4-r2-independent-replay-h2"
H2_PASS = "PASS_AUTHORIZE_V3_V4_R2_H2_COMBINED"
SCRIPTS = {
    "canary": "isambard_ai_gating_v4_r2_gpu_canary_h2.sbatch",
    "production": "isambard_ai_gating_v4_r2_fullnode_h2.sbatch",
    "reducer": "isambard_ai_gating_v4_r2_reduce_h2.sbatch",
    "replay": "isambard_ai_gating_v4_r2_replay_h2.sbatch",
}


def _configure_h1() -> None:
    # H1 is frozen.  H2 reuses its parser after replacing only module-level
    # authority locations with append-only H2 locations.
    h1.SUB = SUB
    h1.PAYLOAD = PAYLOAD
    h1.V3_RELEASE = V3_RELEASE
    h1.SUBMIT_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h2-submission-v1"
    h1.SCRIPTS = SCRIPTS
    h1.validate_v3_release = validate_v3_release


def validate_v3_release(expected_sha: str) -> None:
    value = h1.authority(V3_RELEASE, expected_sha)
    science.req(value.get("schema") ==
                "grid2d-one-two-target-gating-v3-release-for-v4-r2-h2"
                and value.get("status") ==
                    "PASS_AUTHORIZE_V4_R2_H2_HARDWARE_CANARY"
                and value.get("authorizes_v4_r2_h2") is True
                and value.get("scientific_tail_replay", {}).get("status")
                    == "PASS_TAIL_EVIDENCE",
                "H2 v3 release authority drift")


def validate_submission_chain_h2(
    *, array_job: str, reducer_job: str, h1_sha: str,
    production_path: Path, production_sha: str,
    reducer_path: Path, reducer_sha: str,
) -> dict[str, str]:
    """H2 chain replay with the H2 v3-authority job as canary dependency."""
    science.req(production_path == h1.receipt_path("production")
                and reducer_path == h1.receipt_path("reducer"),
                "H2 production/reducer submission paths drift")
    production_preview = h1.authority(production_path, production_sha)
    inputs = production_preview.get("phase_inputs")
    science.req(isinstance(inputs, dict) and set(inputs) == {
        "v3_release_sha256", "canary_job_id", "canary_submission_sha256",
        "canary_receipt_sha256",
    }, "H2 production phase input schema drift")
    release_sha = inputs["v3_release_sha256"]
    canary_job = inputs["canary_job_id"]
    canary_submit_sha = inputs["canary_submission_sha256"]
    canary_receipt_sha = inputs["canary_receipt_sha256"]
    validate_v3_release(release_sha)
    canary_submission = h1.authority(h1.receipt_path("canary"),
                                     canary_submit_sha)
    v3_authority_job = canary_submission.get("dependency_afterok")
    science.req(isinstance(v3_authority_job, str) and v3_authority_job.isdecimal()
                and canary_submission.get("phase_inputs") == {
                    "v3_release_sha256": release_sha},
                "H2 canary/v3-authority lineage drift")
    h1.validate_submission(
        phase="canary", path=h1.receipt_path("canary"),
        expected_sha=canary_submit_sha, h1_sha=h1_sha, job=canary_job,
        dependency=v3_authority_job,
        phase_inputs={"v3_release_sha256": release_sha},
        authorities={"v3_release": {"path": str(V3_RELEASE),
                                     "sha256": release_sha}},
        script_args=[h1_sha, release_sha, str(V3_RELEASE)],
    )
    canary_path = ROOT / f"artifacts/canary/canary-{canary_job}/canary-receipt.json"
    h1.validate_canary_receipt(canary_job, canary_receipt_sha, release_sha)
    h1.validate_submission(
        phase="production", path=production_path, expected_sha=production_sha,
        h1_sha=h1_sha, job=array_job, dependency=canary_job,
        phase_inputs=inputs,
        authorities={
            "v3_release": {"path": str(V3_RELEASE), "sha256": release_sha},
            "canary_submission": {"path": str(h1.receipt_path("canary")),
                                  "sha256": canary_submit_sha},
            "canary_receipt": {"path": str(canary_path),
                               "sha256": canary_receipt_sha},
        },
        script_args=[h1_sha, str(V3_RELEASE), release_sha,
                     str(canary_path), canary_receipt_sha],
    )
    expected_reducer_inputs = {
        "array_job_id": array_job,
        "production_submission_sha256": production_sha,
        "canary_job_id": canary_job,
        "canary_receipt_sha256": canary_receipt_sha,
    }
    reducer_preview = h1.authority(reducer_path, reducer_sha)
    science.req(reducer_preview.get("phase_inputs") == expected_reducer_inputs,
                "H2 reducer input lineage drift")
    h1.validate_submission(
        phase="reducer", path=reducer_path, expected_sha=reducer_sha,
        h1_sha=h1_sha, job=reducer_job, dependency=array_job,
        phase_inputs=expected_reducer_inputs,
        authorities={
            "production_submission": {"path": str(production_path),
                                      "sha256": production_sha},
            "canary_receipt": {"path": str(canary_path),
                               "sha256": canary_receipt_sha},
        },
        script_args=[h1_sha, array_job, array_job, str(canary_path),
                     canary_receipt_sha, str(production_path), production_sha],
    )
    return {
        "v3_release_sha256": release_sha,
        "canary_job_id": canary_job,
        "canary_submission_receipt_sha256": canary_submit_sha,
        "canary_receipt_sha256": canary_receipt_sha,
        "production_submission_receipt_sha256": production_sha,
        "reducer_submission_receipt_sha256": reducer_sha,
    }


def replay_sacct(path: Path, array_job: str,
                 inventory: list[dict[str, Any]]) -> dict[str, Any]:
    for task in range(480):
        cells = {int(row["cell_id"]) for row in inventory
                 if int(row["slurm_array_task_id"]) == task}
        expected = {task + 480 * (gpu + 4 * bundle)
                    for gpu in range(4) for bundle in range(12)}
        science.req(cells == expected, f"task {task} exact 48-cell mapping drift")
    result = science.replay_sacct_bijection(
        path, array_job, inventory, task_count=480,
        cells_per_allocation=48, require_extended=True,
    )
    # Preserve H1's exact resource proof while adding the H2 bijection digest.
    with path.open(encoding="utf-8") as handle:
        rows = list(__import__("csv").DictReader(handle, delimiter="|"))
    task_rows = [row for row in rows if row["JobID"] != array_job]
    for row in task_rows:
        science.req(h1.gpu_count(row["AllocTRES"]) == 4
                    and h1.gpu_count(row["ReqTRES"]) == 4,
                    "task did not request and allocate four GPUs")
    elapsed = int(result["elapsed_raw_total_seconds"])
    return {
        "independently_parsed": True, "array_job_id": array_job,
        "parent_rows": 1, "tasks": 480, "unique_allocations": 480,
        "unique_job_id_raw": 480,
        "job_id_raw_task_bijection_digest": result["bijection_digest"],
        "cells_per_allocation": 48, "gpus_per_allocation": 4,
        "nodes_per_allocation": 1,
        "elapsed_raw_total_seconds": elapsed,
        "actual_full_node_nhr": elapsed / 3600.0,
        "receipt_sha256": result["receipt_sha256"],
    }


def replay(
    *, run: str, array: str, reducer: str, reduction_sha: str, h2_sha: str,
    production_submit: Path, production_submit_sha: str,
    reducer_submit: Path, reducer_submit_sha: str,
) -> dict[str, Any]:
    _configure_h1()
    original = h1.replay_sacct
    original_chain = h1.validate_submission_chain
    h1.replay_sacct = replay_sacct
    h1.validate_submission_chain = validate_submission_chain_h2
    try:
        base = h1.replay(
            run=run, array=array, reducer=reducer,
            reduction_sha=reduction_sha, h1_sha=h2_sha,
            production_submit=production_submit,
            production_submit_sha=production_submit_sha,
            reducer_submit=reducer_submit,
            reducer_submit_sha=reducer_submit_sha,
        )
    finally:
        h1.replay_sacct = original
        h1.validate_submission_chain = original_chain
    reduction = ROOT / (
        f"artifacts/outputs/isambard_ai_v4_r2/reduction-{array}-{reducer}/"
        "reduction_v4_r2.json"
    )
    raw = ROOT / f"artifacts/outputs/isambard_ai_v4_r2/production-{run}"
    scientific = science.recompute_tail_evidence(
        h1.MANIFEST, raw, reduction, expected_cells=23040, expected_blocks=128,
    )
    fixed = dict(base["fixed_artifacts"])
    fixed["h2_payload_sha256"] = fixed.pop("h1_payload_sha256")
    extended = dict(base["extended_sacct"])
    science.req(extended.get("unique_job_id_raw") == 480
                and isinstance(extended.get("job_id_raw_task_bijection_digest"), str),
                "H2 global allocation uniqueness was not recorded")
    passed = scientific["status"] == "PASS_TAIL_EVIDENCE"
    return {
        **base,
        "schema": H2_SCHEMA,
        "status": H2_PASS if passed else "HOLD_STAGE_A2_160K",
        "fixed_artifacts": fixed,
        "extended_sacct": extended,
        "scientific_tail_replay": scientific,
        "authorizes_combined": passed,
    }


def commit(path: Path, payload: Mapping[str, Any]) -> None:
    science.req(not path.exists(), "H2 replay receipt exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".h2-replay.", dir=path.parent)
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
    parser.add_argument("--h2-payload-sha256", required=True)
    parser.add_argument("--production-submit", type=Path, required=True)
    parser.add_argument("--production-submit-sha256", required=True)
    parser.add_argument("--reducer-submit", type=Path, required=True)
    parser.add_argument("--reducer-submit-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        expected = ROOT / f"artifacts/replay/v4-r2-replay-h2-{args.reducer_job}.json"
        science.req(args.output == expected, "H2 replay output path drift")
        payload = replay(
            run=args.run_token, array=args.array_job, reducer=args.reducer_job,
            reduction_sha=args.reduction_sha256, h2_sha=args.h2_payload_sha256,
            production_submit=args.production_submit,
            production_submit_sha=args.production_submit_sha256,
            reducer_submit=args.reducer_submit,
            reducer_submit_sha=args.reducer_submit_sha256,
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
