#!/usr/bin/env python3
"""H4 combined analysis with canonical paths and closed receipt authority."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import analyze_gpu_gating_v4_r2_combined as statistics
import analyze_gpu_gating_v4_r2_combined_h1 as h1_authority
import analyze_gpu_gating_v4_r2_combined_h2 as h2_statistics
import independent_replay_gpu_gating_v4_r2_h4 as replay_h4
import runtime_probe_v4_r2_h4 as runtime
import scientific_tail_replay_v4_r2_h2 as science
import verify_v3_release_for_v4_r2_h4 as v3_h4

ROOT = replay_h4.ROOT
V3 = h2_statistics.V3
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h4_payload.sha256"
SUB = ROOT / "artifacts/submission_h4"
SUBMIT_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h4-submission-v1"
SUBMIT_STATUS = "SUBMITTED_WITH_EXACT_READBACK"
COMBINED_SCRIPT = "isambard_ai_gating_v4_r2_combined_h4.sbatch"
REPLAY_SCRIPT = "isambard_ai_gating_v4_r2_replay_h4.sbatch"
COMBINED_SCHEMA = "grid2d-one-two-target-gating-v4-r2-combined-h4-v1"
COMBINED_STATUS = "PASS_H4_COMBINED_COMPUTATION_AWAIT_TERMINAL_RELEASE"
SUBMIT_KEYS = {
    "schema", "status", "phase", "job_id", "dependency_afterok",
    "payload_manifest_sha256", "phase_inputs", "script", "argv",
    "authorities", "scontrol_readback",
}
COMBINED_KEYS = {
    "schema", "status", "authorization", "submission_binding",
    "runtime_binding", "primary", "surface", "pack_heterogeneity", "csv",
    "authorizes_scientific_release",
}
AUTHORIZATION_KEYS = {
    "h4_payload_manifest_sha256",
    "v3_release_receipt_path", "v3_release_receipt_sha256",
    "v4_replay_receipt_path", "v4_replay_receipt_sha256",
    "replay_submission_receipt_path", "replay_submission_receipt_sha256",
    "v3_primary_raw_replay_status", "v3_primary_raw_replay_digest",
    "v4_primary_raw_replay_status", "v4_primary_raw_replay_digest",
    "v3_reduction_csv_path", "v3_reduction_csv_sha256",
    "v4_reduction_csv_path", "v4_reduction_csv_sha256",
    "array_job_id", "reducer_job_id", "replay_job_id", "combined_job_id",
}
SUBMISSION_BINDING_KEYS = {
    "combined_job_id", "combined_submission_receipt_path",
    "combined_submission_receipt_sha256", "replay_job_id",
    "replay_submission_receipt_path", "replay_submission_receipt_sha256",
    "script", "argv", "scontrol_readback_sha256",
}
CSV_KEYS = {"path", "filename", "sha256", "rows", "fieldnames"}


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def decimal(*values: str) -> None:
    req(all(isinstance(value, str) and value.isdecimal() for value in values),
        "H4 Slurm IDs must be decimal")


def v3_release_path() -> Path:
    return ROOT / "artifacts/releases/v3-release-for-v4-r2-h4.json"


def replay_receipt_path(reducer_job: str) -> Path:
    return ROOT / f"artifacts/replay/v4-r2-replay-h4-{reducer_job}.json"


def submission_path(phase: str) -> Path:
    return SUB / f"{phase}-submission.json"


def combined_paths(replay_job: str, combined_job: str) -> tuple[Path, Path]:
    """The sole H4 combined location; callers cannot nominate a path."""
    decimal(replay_job, combined_job)
    directory = ROOT / (
        f"artifacts/combined_h4/replay-{replay_job}-combined-{combined_job}"
    )
    return (directory / "combined_v4_r2_h4.json",
            directory / "combined_v4_r2_h4.csv")


def runtime_path(phase: str, job_id: str) -> Path:
    decimal(job_id)
    return ROOT / f"artifacts/runtime_h4/{phase}-{job_id}.json"


def script_record(name: str) -> dict[str, str]:
    path = ROOT / "code" / name
    return {"path": f"code/{name}", "sha256": science.sha(path)}


def read_submission(path: Path, expected_sha: str) -> dict[str, Any]:
    req(science.HEX64.fullmatch(expected_sha) is not None
        and science.sha(path) == expected_sha,
        f"H4 submission receipt path/hash drift: {path.name}")
    value = science.strict_json(path, mode600=True)
    req(set(value) == SUBMIT_KEYS and value["schema"] == SUBMIT_SCHEMA
        and value["status"] == SUBMIT_STATUS,
        f"H4 submission exact envelope drift: {path.name}")
    return value


def validate_replay_submission(
    *, expected_sha: str, h4_sha: str, array_job: str, reducer_job: str,
    replay_job: str,
) -> dict[str, Any]:
    path = submission_path("replay")
    value = read_submission(path, expected_sha)
    req(value["phase"] == "replay" and value["job_id"] == replay_job
        and value["dependency_afterok"] == reducer_job
        and value["payload_manifest_sha256"] == h4_sha,
        "H4 replay submission job/dependency/payload drift")
    inputs = value["phase_inputs"]
    req(isinstance(inputs, dict) and set(inputs) == {
        "array_job_id", "reducer_job_id", "production_submission_sha256",
        "reducer_submission_sha256", "reduction_json_sha256",
    } and inputs["array_job_id"] == array_job
      and inputs["reducer_job_id"] == reducer_job,
      "H4 replay submission inputs drift")
    production = submission_path("production")
    reducer = submission_path("reducer")
    reduction = ROOT / (
        f"artifacts/outputs/isambard_ai_v4_r2/reduction-{array_job}-{reducer_job}/"
        "reduction_v4_r2.json"
    )
    authorities = {
        "production_submission": {
            "path": str(production),
            "sha256": inputs["production_submission_sha256"],
        },
        "reducer_submission": {
            "path": str(reducer),
            "sha256": inputs["reducer_submission_sha256"],
        },
        "reduction_json": {
            "path": str(reduction), "sha256": inputs["reduction_json_sha256"],
        },
    }
    req(value["authorities"] == authorities
        and science.sha(production) == inputs["production_submission_sha256"]
        and science.sha(reducer) == inputs["reducer_submission_sha256"]
        and science.sha(reduction) == inputs["reduction_json_sha256"],
        "H4 replay submission authority closure drift")
    args = [
        h4_sha, array_job, array_job, reducer_job,
        inputs["reduction_json_sha256"], str(production),
        inputs["production_submission_sha256"], str(reducer),
        inputs["reducer_submission_sha256"],
    ]
    expected_argv = [
        "sbatch", "--parsable", f"--dependency=afterok:{reducer_job}",
        f"code/{REPLAY_SCRIPT}", *args,
    ]
    readback = value["scontrol_readback"]
    req(value["script"] == script_record(REPLAY_SCRIPT)
        and value["argv"] == expected_argv and isinstance(readback, str)
        and f"JobId={replay_job}" in readback
        and f"Dependency=afterok:{reducer_job}" in readback
        and f"WorkDir={ROOT}" in readback and REPLAY_SCRIPT in readback,
        "H4 replay submission script/argv/readback drift")
    return value


def validate_combined_submission(
    *, expected_sha: str, h4_sha: str, array_job: str, reducer_job: str,
    replay_job: str, combined_job: str, v3_sha: str, replay_sha: str,
    replay_submit_sha: str,
) -> dict[str, Any]:
    path = submission_path("combined")
    value = read_submission(path, expected_sha)
    inputs = {
        "array_job_id": array_job, "reducer_job_id": reducer_job,
        "replay_job_id": replay_job, "v3_release_sha256": v3_sha,
        "v4_replay_receipt_sha256": replay_sha,
        "replay_submission_sha256": replay_submit_sha,
    }
    authorities = {
        "v3_release": {"path": str(v3_release_path()), "sha256": v3_sha},
        "v4_replay": {
            "path": str(replay_receipt_path(reducer_job)), "sha256": replay_sha,
        },
        "replay_submission": {
            "path": str(submission_path("replay")), "sha256": replay_submit_sha,
        },
    }
    req(value["phase"] == "combined" and value["job_id"] == combined_job
        and value["dependency_afterok"] == replay_job
        and value["payload_manifest_sha256"] == h4_sha
        and value["phase_inputs"] == inputs and value["authorities"] == authorities,
        "H4 combined submission authority map drift")
    args = [h4_sha, array_job, reducer_job, replay_job, v3_sha, replay_sha,
            replay_submit_sha]
    expected_argv = [
        "sbatch", "--parsable", f"--dependency=afterok:{replay_job}",
        f"code/{COMBINED_SCRIPT}", *args,
    ]
    readback = value["scontrol_readback"]
    req(value["script"] == script_record(COMBINED_SCRIPT)
        and value["argv"] == expected_argv and isinstance(readback, str)
        and f"JobId={combined_job}" in readback
        and f"Dependency=afterok:{replay_job}" in readback
        and f"WorkDir={ROOT}" in readback and COMBINED_SCRIPT in readback,
        "H4 combined submission script/argv/readback drift")
    return value


def validate_v3_receipt(expected_sha: str, *, v3_authority_job: str | None = None
                        ) -> dict[str, Any]:
    path = v3_release_path()
    req(science.sha(path) == expected_sha, "H4 v3 release SHA drift")
    value = science.strict_json(path, mode600=True)
    req(set(value) == v3_h4.TOP_KEYS and value["schema"] == v3_h4.SCHEMA
        and value["status"] == v3_h4.STATUS
        and value["authorizes_v4_r2_h4"] is True
        and value["h4_primary_rope_replay"].get("status")
            == "PASS_PRIMARY_ROPE_EVIDENCE"
        and value["h4_primary_rope_replay"].get("authorizes_ready_evidence") is True,
        "H4 v3 receipt schema/status/primary authority drift")
    binding = value["runtime_binding"]
    req(isinstance(binding, dict) and set(binding) == {"path", "sha256", "receipt"}
        and science.sha(Path(binding["path"])) == binding["sha256"],
        "H4 v3 runtime binding drift")
    job = v3_authority_job or binding["receipt"].get("slurm_job_id")
    expected_path = runtime_path("v3_authority", job)
    req(Path(binding["path"]) == expected_path,
        "H4 v3 runtime canonical path drift")
    checked = runtime.validate_path(expected_path, phase="v3_authority", job_id=job)
    science.close_tree(binding["receipt"], checked, "H4 v3 runtime receipt")
    return value


def validate_replay_receipt(
    expected_sha: str, *, h4_sha: str, array_job: str, reducer_job: str,
    replay_job: str,
) -> dict[str, Any]:
    path = replay_receipt_path(reducer_job)
    req(science.sha(path) == expected_sha, "H4 replay receipt SHA drift")
    value = science.strict_json(path, mode600=True)
    req(set(value) == replay_h4.TOP_KEYS and value["schema"] == replay_h4.H4_SCHEMA
        and value["status"] == replay_h4.H4_PASS
        and value["authorizes_combined"] is True
        and value["jobs"] == {
            "run_token": array_job, "array": array_job, "reducer": reducer_job,
        } and value["fixed_artifacts"].get("h4_payload_sha256") == h4_sha
        and value["h4_primary_rope_replay"].get("status")
            == "PASS_PRIMARY_ROPE_EVIDENCE"
        and value["h4_primary_rope_replay"].get("authorizes_ready_evidence") is True,
        "H4 replay schema/status/jobs/raw-primary authority drift")
    binding = value["runtime_binding"]
    expected_path = runtime_path("replay", replay_job)
    req(isinstance(binding, dict) and set(binding) == {"path", "sha256", "receipt"}
        and Path(binding["path"]) == expected_path
        and science.sha(expected_path) == binding["sha256"],
        "H4 replay runtime binding drift")
    checked = runtime.validate_path(expected_path, phase="replay", job_id=replay_job)
    science.close_tree(binding["receipt"], checked, "H4 replay runtime receipt")
    return value


def reduction_csvs(v3_release: Mapping[str, Any], replay: Mapping[str, Any]
                   ) -> tuple[Path, str, Path, str]:
    h2_authority = v3_release["h2_tail_and_allocation_authority"]
    req(isinstance(h2_authority, dict) and set(h2_authority) == {
        "schema", "status", "fixed_roots", "fixed_jobs", "h1_release",
        "h1_evidence_digest", "production_allocation_bijection",
        "canary_allocation_bijection", "scientific_tail_replay",
        "authorizes_v4_r2_h2",
    } and h2_authority["status"] == "PASS_AUTHORIZE_V4_R2_H2_HARDWARE_CANARY"
      and h2_authority["authorizes_v4_r2_h2"] is True,
      "H4 nested v3 H2 authority drift")
    h1_path = ROOT / "artifacts/releases/v3-release-for-v4-r2-h1.json"
    h1_record = h2_authority["h1_release"]
    req(h1_record == {"path": str(h1_path), "sha256": h1_record.get("sha256")}
        and science.sha(h1_path) == h1_record["sha256"],
        "H4 nested v3 H1 path/hash drift")
    h1_value, v3_csv = h1_authority.validate_v3(h1_record["sha256"])
    v3_sha = h1_value["evidence_hashes"]["reduction_csv"]
    req(science.sha(v3_csv) == v3_sha, "H4 v3 reduction CSV hash drift")
    jobs = replay["jobs"]
    v4_csv = ROOT / (
        f"artifacts/outputs/isambard_ai_v4_r2/reduction-{jobs['array']}-"
        f"{jobs['reducer']}/reduction_v4_r2.csv"
    )
    v4_sha = replay["hashes"]["reduction_csv"]
    req(science.sha(v4_csv) == v4_sha, "H4 v4 reduction CSV hash drift")
    return v3_csv, v3_sha, v4_csv, v4_sha


def recompute_inference(v3_csv: Path, v3_sha: str, v4_csv: Path,
                        v4_sha: str) -> dict[str, Any]:
    values3 = statistics.csv_values(v3_csv, 32, v3_sha)
    values4 = statistics.csv_values(v4_csv, 128, v4_sha)
    a3 = statistics.effects(values3, 32)
    a4 = statistics.effects(values4, 128)
    pooled = np.vstack((a3, a4))
    req(pooled.shape == (160, 75), "H4 pooled effect matrix drift")
    contract = science.strict_json(h2_statistics.HETERO_CONTRACT)
    return {
        "primary": {
            "v3_only": statistics.primary(a3, "v3 pack"),
            "v4_only": statistics.primary(a4, "v4-r2 reflect pack"),
            "combined": statistics.primary(
                pooled, "v3 plus independent v4-r2 packs"),
        },
        "surface": {
            "v3_only": statistics.max_t(a3, 2026072699),
            "v4_only": statistics.max_t(a4, 2026072700),
            "combined": statistics.max_t(pooled, 2026072701),
        },
        "pack_heterogeneity": h2_statistics.pack_heterogeneity(
            a3, a4, contract),
    }


def csv_bytes(surface: Mapping[str, Any]) -> tuple[bytes, list[str]]:
    rows = surface["combined"]["rows"]
    req(isinstance(rows, list) and len(rows) == 75 and rows,
        "H4 combined surface row inventory drift")
    fieldnames = list(rows[0])
    req(all(isinstance(row, dict) and list(row) == fieldnames for row in rows),
        "H4 combined surface row schema drift")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return buffer.getvalue().encode(), fieldnames


def authorization(
    *, h4_sha: str, v3_sha: str, replay_sha: str, replay_submit_sha: str,
    v3_release: Mapping[str, Any], replay: Mapping[str, Any],
    v3_csv: Path, v3_csv_sha: str, v4_csv: Path, v4_csv_sha: str,
    array_job: str, reducer_job: str, replay_job: str, combined_job: str,
) -> dict[str, Any]:
    value = {
        "h4_payload_manifest_sha256": h4_sha,
        "v3_release_receipt_path": str(v3_release_path()),
        "v3_release_receipt_sha256": v3_sha,
        "v4_replay_receipt_path": str(replay_receipt_path(reducer_job)),
        "v4_replay_receipt_sha256": replay_sha,
        "replay_submission_receipt_path": str(submission_path("replay")),
        "replay_submission_receipt_sha256": replay_submit_sha,
        "v3_primary_raw_replay_status":
            v3_release["h4_primary_rope_replay"]["status"],
        "v3_primary_raw_replay_digest": science.canonical_digest(
            v3_release["h4_primary_rope_replay"]),
        "v4_primary_raw_replay_status":
            replay["h4_primary_rope_replay"]["status"],
        "v4_primary_raw_replay_digest": science.canonical_digest(
            replay["h4_primary_rope_replay"]),
        "v3_reduction_csv_path": str(v3_csv),
        "v3_reduction_csv_sha256": v3_csv_sha,
        "v4_reduction_csv_path": str(v4_csv),
        "v4_reduction_csv_sha256": v4_csv_sha,
        "array_job_id": array_job, "reducer_job_id": reducer_job,
        "replay_job_id": replay_job, "combined_job_id": combined_job,
    }
    req(set(value) == AUTHORIZATION_KEYS, "H4 authorization internal key drift")
    return value


def analyze(
    *, h4_sha: str, array_job: str, reducer_job: str, replay_job: str,
    combined_job: str, v3_sha: str, replay_sha: str,
    replay_submit_sha: str, combined_submit_sha: str,
) -> dict[str, Any]:
    decimal(array_job, reducer_job, replay_job, combined_job)
    req(science.sha(PAYLOAD) == h4_sha, "H4 payload manifest hash drift")
    v3_release = validate_v3_receipt(v3_sha)
    replay_submission = validate_replay_submission(
        expected_sha=replay_submit_sha, h4_sha=h4_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
    )
    replay = validate_replay_receipt(
        replay_sha, h4_sha=h4_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
    )
    combined_submission = validate_combined_submission(
        expected_sha=combined_submit_sha, h4_sha=h4_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job, combined_job=combined_job,
        v3_sha=v3_sha, replay_sha=replay_sha,
        replay_submit_sha=replay_submit_sha,
    )
    runtime_receipt = runtime_path("combined", combined_job)
    runtime_binding = runtime.binding(
        runtime_receipt, phase="combined", job_id=combined_job)
    v3_csv, v3_csv_sha, v4_csv, v4_csv_sha = reduction_csvs(v3_release, replay)
    computed = recompute_inference(v3_csv, v3_csv_sha, v4_csv, v4_csv_sha)
    auth = authorization(
        h4_sha=h4_sha, v3_sha=v3_sha, replay_sha=replay_sha,
        replay_submit_sha=replay_submit_sha, v3_release=v3_release,
        replay=replay, v3_csv=v3_csv, v3_csv_sha=v3_csv_sha,
        v4_csv=v4_csv, v4_csv_sha=v4_csv_sha, array_job=array_job,
        reducer_job=reducer_job, replay_job=replay_job,
        combined_job=combined_job,
    )
    payload = {
        "schema": COMBINED_SCHEMA, "status": COMBINED_STATUS,
        "authorization": auth,
        "submission_binding": {
            "combined_job_id": combined_job,
            "combined_submission_receipt_path":
                str(submission_path("combined")),
            "combined_submission_receipt_sha256": combined_submit_sha,
            "replay_job_id": replay_job,
            "replay_submission_receipt_path": str(submission_path("replay")),
            "replay_submission_receipt_sha256": replay_submit_sha,
            "script": combined_submission["script"],
            "argv": combined_submission["argv"],
            "scontrol_readback_sha256": hashlib.sha256(
                combined_submission["scontrol_readback"].encode()).hexdigest(),
        },
        "runtime_binding": runtime_binding,
        "primary": computed["primary"], "surface": computed["surface"],
        "pack_heterogeneity": computed["pack_heterogeneity"],
        "csv": {}, "authorizes_scientific_release": False,
    }
    req(set(payload) == COMBINED_KEYS
        and set(payload["submission_binding"]) == SUBMISSION_BINDING_KEYS,
        "H4 combined internal exact-key drift")
    _ = replay_submission
    return payload


def commit(path: Path, data: bytes) -> None:
    req(not path.exists(), "H4 canonical combined output exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = __import__("tempfile").mkstemp(
        prefix=".combined-h4.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h4-payload-sha256", required=True)
    parser.add_argument("--array-job", required=True)
    parser.add_argument("--reducer-job", required=True)
    parser.add_argument("--replay-job", required=True)
    parser.add_argument("--slurm-job-id", required=True)
    parser.add_argument("--v3-release-sha256", required=True)
    parser.add_argument("--v4-replay-sha256", required=True)
    parser.add_argument("--replay-submission-sha256", required=True)
    parser.add_argument("--combined-submission-sha256", required=True)
    args = parser.parse_args()
    try:
        json_path, csv_path = combined_paths(args.replay_job, args.slurm_job_id)
        req(not json_path.parent.exists(), "H4 canonical combined directory exists")
        json_path.parent.mkdir(parents=True, mode=0o700)
        payload = analyze(
            h4_sha=args.h4_payload_sha256, array_job=args.array_job,
            reducer_job=args.reducer_job, replay_job=args.replay_job,
            combined_job=args.slurm_job_id, v3_sha=args.v3_release_sha256,
            replay_sha=args.v4_replay_sha256,
            replay_submit_sha=args.replay_submission_sha256,
            combined_submit_sha=args.combined_submission_sha256,
        )
        data, fieldnames = csv_bytes(payload["surface"])
        payload["csv"] = {
            "path": str(csv_path), "filename": csv_path.name,
            "sha256": hashlib.sha256(data).hexdigest(), "rows": 75,
            "fieldnames": fieldnames,
        }
        req(set(payload["csv"]) == CSV_KEYS, "H4 CSV receipt key drift")
        json_data = (json.dumps(payload, indent=2, sort_keys=True,
                                allow_nan=False) + "\n").encode()
        commit(csv_path, data)
        try:
            commit(json_path, json_data)
        except BaseException:
            csv_path.unlink(missing_ok=True)
            raise
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"],
                      "combined_job_id": args.slurm_job_id,
                      "canonical_json": str(json_path),
                      "canonical_csv": str(csv_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
