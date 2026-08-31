#!/usr/bin/env python3
"""Exact, phase-specific, append-only v4-r2-h1 Slurm submit state machine."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping

ROOT = Path("/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727")
SUB = ROOT / "artifacts/submission_h1"
PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h1_payload.sha256"
V3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h1.json"
V3_TERMINAL_JOB = "5789031"
SCHEMA = "grid2d-one-two-target-gating-v4-r2-h1-submission-v1"
STATUS = "SUBMITTED_WITH_EXACT_READBACK"
SCRIPTS = {
    "canary": "isambard_ai_gating_v4_r2_gpu_canary_h1.sbatch",
    "production": "isambard_ai_gating_v4_r2_fullnode_h1.sbatch",
    "reducer": "isambard_ai_gating_v4_r2_reduce_h1.sbatch",
    "replay": "isambard_ai_gating_v4_r2_replay_h1.sbatch",
    "combined": "isambard_ai_gating_v4_r2_combined_h1.sbatch",
}
TOP_KEYS = {
    "schema", "status", "phase", "job_id", "dependency_afterok",
    "payload_manifest_sha256", "phase_inputs", "script", "argv",
    "authorities", "scontrol_readback",
}
HEX64 = re.compile(r"[0-9a-f]{64}")
DECIMAL = re.compile(r"[0-9]+")


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path, *, mode600: bool = True) -> dict[str, Any]:
    stat = path.lstat()
    req(path.is_file() and not path.is_symlink() and stat.st_nlink == 1,
        f"unsafe JSON authority: {path}")
    if mode600:
        req(stat.st_mode & 0o777 == 0o600, f"authority mode is not 0600: {path}")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            req(key not in value, f"duplicate JSON key {key}: {path}")
            value[key] = item
        return value

    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=pairs_hook,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"nonfinite JSON token {token}: {path}")),
    )
    req(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def authority(path: Path, expected_sha: str) -> dict[str, Any]:
    req(HEX64.fullmatch(expected_sha) is not None, "authority SHA is not lowercase hex64")
    req(sha(path) == expected_sha, f"authority SHA drift: {path}")
    return load_json(path)


def validate_v3_release(expected_sha: str) -> dict[str, Any]:
    value = authority(V3_RELEASE, expected_sha)
    req(set(value) == {
        "schema", "status", "fixed_roots", "fixed_jobs", "fixed_contracts",
        "evidence_hashes", "inventory_digest", "raw_replay",
        "live_sacct_query_sha256", "secondary_result_schema",
        "secondary_result_status", "canary_reduction",
    }, "v3 h1 release exact keys drift")
    req(value["schema"] == "grid2d-one-two-target-gating-v3-release-for-v4-r2-h1"
        and value["status"] == "PASS_AUTHORIZE_V4_R2_H1_HARDWARE_CANARY",
        "v3 h1 release did not authorize hardware canary")
    return value


def canary_receipt_path(canary_job: str) -> Path:
    req(DECIMAL.fullmatch(canary_job) is not None, "invalid canary job ID")
    return ROOT / f"artifacts/canary/canary-{canary_job}/canary-receipt.json"


def validate_canary_receipt(
    canary_job: str, expected_sha: str, release_sha: str,
) -> dict[str, Any]:
    path = canary_receipt_path(canary_job)
    value = authority(path, expected_sha)
    req(set(value) == {
        "schema", "status", "release_receipt_sha256", "lanes",
        "distinct_uuid_count", "distinct_pci_count",
        "distinct_cuda_visible_devices_count",
    }, "GPU canary receipt exact keys drift")
    req(value["schema"] == "grid2d-one-two-target-gating-v4-r2-gpu-canary-v1"
        and value["status"] == "PASS_AUTHORIZE_V4_R2_PRODUCTION"
        and value["release_receipt_sha256"] == release_sha,
        "GPU canary authority drift")
    req(value["distinct_uuid_count"] == 4
        and value["distinct_pci_count"] == 4
        and value["distinct_cuda_visible_devices_count"] == 4,
        "GPU canary did not prove four distinct assignments")
    rows = value["lanes"]
    req(isinstance(rows, list) and len(rows) == 4
        and {row.get("lane") for row in rows} == set(range(4)),
        "GPU canary lane inventory drift")
    directory = path.parent
    req({member.name for member in directory.iterdir()} == {
        "canary-receipt.json", *(f"lane-{lane}.json" for lane in range(4))
    }, "GPU canary output exact inventory drift")
    uuids: set[str] = set()
    pci_ids: set[str] = set()
    visible_ids: set[str] = set()
    by_lane = {int(row["lane"]): row for row in rows}
    for lane in range(4):
        lane_path = directory / f"lane-{lane}.json"
        lane_stat = lane_path.lstat()
        req(lane_path.is_file() and not lane_path.is_symlink()
            and lane_stat.st_nlink == 1 and lane_stat.st_mode & 0o777 == 0o600,
            "unsafe GPU lane capture")
        capture = load_json(lane_path)
        req(set(capture) == {
            "schema", "lane", "cuda_visible_devices", "slurm_job_id",
            "slurm_step_id", "gpu",
        }, "GPU lane capture exact keys drift")
        req(capture["schema"] == "grid2d-one-two-target-gating-v4-r2-gpu-lane-v1"
            and capture["lane"] == lane and capture["slurm_job_id"] == canary_job,
            "GPU lane capture identity drift")
        gpu = capture["gpu"]
        req(isinstance(gpu, dict) and set(gpu) == {
            "index", "uuid", "pci_bus_id", "name", "driver_version"
        }, "GPU lane device record drift")
        row = by_lane[lane]
        req(set(row) == {
            "lane", "cuda_visible_devices", "uuid", "pci_bus_id", "capture_sha256"
        } and row["capture_sha256"] == sha(lane_path)
            and row["cuda_visible_devices"] == capture["cuda_visible_devices"]
            and row["uuid"] == gpu["uuid"] and row["pci_bus_id"] == gpu["pci_bus_id"],
            "GPU canary reverse binding drift")
        uuids.add(str(gpu["uuid"])); pci_ids.add(str(gpu["pci_bus_id"]))
        visible_ids.add(str(capture["cuda_visible_devices"]))
    req(len(uuids) == len(pci_ids) == len(visible_ids) == 4,
        "GPU lane captures are not physically distinct")
    return value


def receipt_path(phase: str) -> Path:
    return SUB / f"{phase}-submission.json"


def validate_submission(
    phase: str, expected_sha: str, h1_sha: str, *, expected_job: str | None = None,
    expected_dependency: str | None = None,
) -> dict[str, Any]:
    path = receipt_path(phase)
    value = authority(path, expected_sha)
    req(set(value) == TOP_KEYS and value["schema"] == SCHEMA
        and value["status"] == STATUS and value["phase"] == phase,
        f"{phase} submission receipt contract drift")
    job = value["job_id"]; dependency = value["dependency_afterok"]
    req(isinstance(job, str) and DECIMAL.fullmatch(job) is not None
        and isinstance(dependency, str) and DECIMAL.fullmatch(dependency) is not None,
        f"{phase} submission IDs invalid")
    if expected_job is not None:
        req(job == expected_job, f"{phase} job ID drift")
    if expected_dependency is not None:
        req(dependency == expected_dependency, f"{phase} dependency drift")
    req(value["payload_manifest_sha256"] == h1_sha,
        f"{phase} payload binding drift")
    script = ROOT / "code" / SCRIPTS[phase]
    script_record = value["script"]
    req(isinstance(script_record, dict) and set(script_record) == {"path", "sha256"}
        and script_record["path"] == f"code/{SCRIPTS[phase]}"
        and script_record["sha256"] == sha(script),
        f"{phase} script binding drift")
    inputs = value["phase_inputs"]; authorities = value["authorities"]
    if phase == "canary":
        req(set(inputs) == {"v3_release_sha256"}, "canary phase input keys drift")
        expected_authorities = {"v3_release": {"path": str(V3_RELEASE), "sha256": inputs["v3_release_sha256"]}}
        phase_args = [h1_sha, inputs["v3_release_sha256"], str(V3_RELEASE)]
        req(dependency == V3_TERMINAL_JOB, "canary fixed dependency drift")
    elif phase == "production":
        req(set(inputs) == {"v3_release_sha256", "canary_job_id", "canary_submission_sha256", "canary_receipt_sha256"}, "production phase input keys drift")
        canary_path = canary_receipt_path(inputs["canary_job_id"])
        expected_authorities = {
            "v3_release": {"path": str(V3_RELEASE), "sha256": inputs["v3_release_sha256"]},
            "canary_submission": {"path": str(receipt_path("canary")), "sha256": inputs["canary_submission_sha256"]},
            "canary_receipt": {"path": str(canary_path), "sha256": inputs["canary_receipt_sha256"]},
        }
        phase_args = [h1_sha, str(V3_RELEASE), inputs["v3_release_sha256"], str(canary_path), inputs["canary_receipt_sha256"]]
        req(dependency == inputs["canary_job_id"], "production dependency/canary drift")
    elif phase == "reducer":
        req(set(inputs) == {"array_job_id", "production_submission_sha256", "canary_job_id", "canary_receipt_sha256"}, "reducer phase input keys drift")
        canary_path = canary_receipt_path(inputs["canary_job_id"])
        expected_authorities = {
            "production_submission": {"path": str(receipt_path("production")), "sha256": inputs["production_submission_sha256"]},
            "canary_receipt": {"path": str(canary_path), "sha256": inputs["canary_receipt_sha256"]},
        }
        phase_args = [h1_sha, inputs["array_job_id"], inputs["array_job_id"], str(canary_path), inputs["canary_receipt_sha256"], str(receipt_path("production")), inputs["production_submission_sha256"]]
        req(dependency == inputs["array_job_id"], "reducer dependency/array drift")
    elif phase == "replay":
        req(set(inputs) == {"array_job_id", "reducer_job_id", "production_submission_sha256", "reducer_submission_sha256", "reduction_json_sha256"}, "replay phase input keys drift")
        reduction = ROOT / f"artifacts/outputs/isambard_ai_v4_r2/reduction-{inputs['array_job_id']}-{inputs['reducer_job_id']}/reduction_v4_r2.json"
        expected_authorities = {
            "production_submission": {"path": str(receipt_path("production")), "sha256": inputs["production_submission_sha256"]},
            "reducer_submission": {"path": str(receipt_path("reducer")), "sha256": inputs["reducer_submission_sha256"]},
            "reduction_json": {"path": str(reduction), "sha256": inputs["reduction_json_sha256"]},
        }
        phase_args = [h1_sha, inputs["array_job_id"], inputs["array_job_id"], inputs["reducer_job_id"], inputs["reduction_json_sha256"], str(receipt_path("production")), inputs["production_submission_sha256"], str(receipt_path("reducer")), inputs["reducer_submission_sha256"]]
        req(dependency == inputs["reducer_job_id"], "replay dependency/reducer drift")
    else:
        req(set(inputs) == {"array_job_id", "reducer_job_id", "replay_job_id", "v3_release_sha256", "replay_submission_sha256", "replay_receipt_sha256"}, "combined phase input keys drift")
        replay_path = ROOT / f"artifacts/replay/v4-r2-replay-h1-{inputs['reducer_job_id']}.json"
        expected_authorities = {
            "v3_release": {"path": str(V3_RELEASE), "sha256": inputs["v3_release_sha256"]},
            "replay_submission": {"path": str(receipt_path("replay")), "sha256": inputs["replay_submission_sha256"]},
            "replay_receipt": {"path": str(replay_path), "sha256": inputs["replay_receipt_sha256"]},
        }
        phase_args = [h1_sha, inputs["v3_release_sha256"], str(replay_path), inputs["replay_receipt_sha256"], inputs["array_job_id"], inputs["reducer_job_id"], inputs["replay_job_id"], str(receipt_path("replay")), inputs["replay_submission_sha256"]]
        req(dependency == inputs["replay_job_id"], "combined dependency/replay drift")
    req(authorities == expected_authorities, f"{phase} exact authority map drift")
    argv = value["argv"]
    req(argv == ["sbatch", "--parsable", f"--dependency=afterok:{dependency}",
                    f"code/{SCRIPTS[phase]}", *phase_args],
        f"{phase} exact sbatch argv drift")
    readback = value["scontrol_readback"]
    req(isinstance(readback, str) and f"JobId={job}" in readback
        and f"Dependency=afterok:{dependency}" in readback
        and f"WorkDir={ROOT}" in readback and SCRIPTS[phase] in readback,
        f"{phase} scontrol exact readback drift")
    req(isinstance(value["phase_inputs"], dict)
        and isinstance(value["authorities"], dict),
        f"{phase} structured inputs drift")
    return value


def provided_options(args: argparse.Namespace) -> set[str]:
    names = {
        "v3_release_sha256", "canary_job", "canary_submission_sha256",
        "canary_receipt_sha256", "array_job", "production_submission_sha256",
        "reducer_job", "reducer_submission_sha256", "reduction_sha256",
        "replay_job", "replay_submission_sha256", "replay_receipt_sha256",
    }
    return {name for name in names if getattr(args, name) is not None}


def exact_options(args: argparse.Namespace, allowed: set[str]) -> None:
    req(provided_options(args) == allowed,
        f"phase-specific options drift: got {sorted(provided_options(args))}, "
        f"expected {sorted(allowed)}")
    for name in allowed:
        value = getattr(args, name)
        if name.endswith("sha256"):
            req(isinstance(value, str) and HEX64.fullmatch(value) is not None,
                f"{name} is not lowercase hex64")
        elif name.endswith("job"):
            req(isinstance(value, str) and DECIMAL.fullmatch(value) is not None,
                f"{name} is not decimal")


def phase_spec(args: argparse.Namespace) -> tuple[str, list[str], dict[str, str], dict[str, dict[str, str]]]:
    h1_sha = args.payload_sha256
    if args.phase == "canary":
        exact_options(args, {"v3_release_sha256"})
        validate_v3_release(args.v3_release_sha256)
        inputs = {"v3_release_sha256": args.v3_release_sha256}
        authorities = {"v3_release": {"path": str(V3_RELEASE), "sha256": args.v3_release_sha256}}
        return V3_TERMINAL_JOB, [h1_sha, args.v3_release_sha256, str(V3_RELEASE)], inputs, authorities

    if args.phase == "production":
        exact_options(args, {
            "v3_release_sha256", "canary_job", "canary_submission_sha256",
            "canary_receipt_sha256",
        })
        validate_v3_release(args.v3_release_sha256)
        canary_submission = validate_submission(
            "canary", args.canary_submission_sha256, h1_sha,
            expected_job=args.canary_job, expected_dependency=V3_TERMINAL_JOB,
        )
        req(canary_submission["phase_inputs"] == {
            "v3_release_sha256": args.v3_release_sha256
        }, "canary submission release lineage drift")
        canary = canary_receipt_path(args.canary_job)
        validate_canary_receipt(args.canary_job, args.canary_receipt_sha256,
                                args.v3_release_sha256)
        inputs = {
            "v3_release_sha256": args.v3_release_sha256,
            "canary_job_id": args.canary_job,
            "canary_submission_sha256": args.canary_submission_sha256,
            "canary_receipt_sha256": args.canary_receipt_sha256,
        }
        authorities = {
            "v3_release": {"path": str(V3_RELEASE), "sha256": args.v3_release_sha256},
            "canary_submission": {"path": str(receipt_path("canary")), "sha256": args.canary_submission_sha256},
            "canary_receipt": {"path": str(canary), "sha256": args.canary_receipt_sha256},
        }
        argv = [h1_sha, str(V3_RELEASE), args.v3_release_sha256,
                str(canary), args.canary_receipt_sha256]
        return args.canary_job, argv, inputs, authorities

    if args.phase == "reducer":
        exact_options(args, {
            "array_job", "production_submission_sha256", "canary_receipt_sha256",
        })
        production = validate_submission(
            "production", args.production_submission_sha256, h1_sha,
            expected_job=args.array_job,
        )
        pi = production["phase_inputs"]
        req(set(pi) == {
            "v3_release_sha256", "canary_job_id", "canary_submission_sha256",
            "canary_receipt_sha256",
        } and pi["canary_receipt_sha256"] == args.canary_receipt_sha256,
            "production lineage drift before reducer")
        canary_job = pi["canary_job_id"]
        req(production["dependency_afterok"] == canary_job,
            "production dependency/canary lineage drift")
        canary = canary_receipt_path(canary_job)
        validate_canary_receipt(canary_job, args.canary_receipt_sha256,
                                pi["v3_release_sha256"])
        inputs = {
            "array_job_id": args.array_job,
            "production_submission_sha256": args.production_submission_sha256,
            "canary_job_id": canary_job,
            "canary_receipt_sha256": args.canary_receipt_sha256,
        }
        authorities = {
            "production_submission": {"path": str(receipt_path("production")), "sha256": args.production_submission_sha256},
            "canary_receipt": {"path": str(canary), "sha256": args.canary_receipt_sha256},
        }
        argv = [h1_sha, args.array_job, args.array_job, str(canary),
                args.canary_receipt_sha256, str(receipt_path("production")),
                args.production_submission_sha256]
        return args.array_job, argv, inputs, authorities

    if args.phase == "replay":
        exact_options(args, {
            "array_job", "production_submission_sha256", "reducer_job",
            "reducer_submission_sha256", "reduction_sha256",
        })
        production = validate_submission(
            "production", args.production_submission_sha256, h1_sha,
            expected_job=args.array_job,
        )
        reducer = validate_submission(
            "reducer", args.reducer_submission_sha256, h1_sha,
            expected_job=args.reducer_job, expected_dependency=args.array_job,
        )
        req(reducer["phase_inputs"].get("array_job_id") == args.array_job
            and reducer["phase_inputs"].get("production_submission_sha256")
                == args.production_submission_sha256,
            "reducer submission lineage drift")
        reduction = ROOT / (
            f"artifacts/outputs/isambard_ai_v4_r2/reduction-{args.array_job}-"
            f"{args.reducer_job}/reduction_v4_r2.json"
        )
        authority(reduction, args.reduction_sha256)
        inputs = {
            "array_job_id": args.array_job,
            "reducer_job_id": args.reducer_job,
            "production_submission_sha256": args.production_submission_sha256,
            "reducer_submission_sha256": args.reducer_submission_sha256,
            "reduction_json_sha256": args.reduction_sha256,
        }
        authorities = {
            "production_submission": {"path": str(receipt_path("production")), "sha256": args.production_submission_sha256},
            "reducer_submission": {"path": str(receipt_path("reducer")), "sha256": args.reducer_submission_sha256},
            "reduction_json": {"path": str(reduction), "sha256": args.reduction_sha256},
        }
        argv = [h1_sha, args.array_job, args.array_job, args.reducer_job,
                args.reduction_sha256, str(receipt_path("production")),
                args.production_submission_sha256, str(receipt_path("reducer")),
                args.reducer_submission_sha256]
        return args.reducer_job, argv, inputs, authorities

    exact_options(args, {
        "array_job", "reducer_job", "replay_job", "v3_release_sha256",
        "replay_submission_sha256", "replay_receipt_sha256",
    })
    validate_v3_release(args.v3_release_sha256)
    replay_submission = validate_submission(
        "replay", args.replay_submission_sha256, h1_sha,
        expected_job=args.replay_job, expected_dependency=args.reducer_job,
    )
    req(replay_submission["phase_inputs"].get("array_job_id") == args.array_job
        and replay_submission["phase_inputs"].get("reducer_job_id") == args.reducer_job,
        "replay submission lineage drift")
    replay = ROOT / f"artifacts/replay/v4-r2-replay-h1-{args.reducer_job}.json"
    replay_value = authority(replay, args.replay_receipt_sha256)
    req(replay_value.get("schema") == "grid2d-one-two-target-gating-v4-r2-independent-replay-h1"
        and replay_value.get("status") == "PASS_AUTHORIZE_V3_V4_R2_H1_COMBINED"
        and replay_value.get("jobs") == {
            "run_token": args.array_job, "array": args.array_job,
            "reducer": args.reducer_job,
        }, "independent replay authority drift")
    inputs = {
        "array_job_id": args.array_job, "reducer_job_id": args.reducer_job,
        "replay_job_id": args.replay_job,
        "v3_release_sha256": args.v3_release_sha256,
        "replay_submission_sha256": args.replay_submission_sha256,
        "replay_receipt_sha256": args.replay_receipt_sha256,
    }
    authorities = {
        "v3_release": {"path": str(V3_RELEASE), "sha256": args.v3_release_sha256},
        "replay_submission": {"path": str(receipt_path("replay")), "sha256": args.replay_submission_sha256},
        "replay_receipt": {"path": str(replay), "sha256": args.replay_receipt_sha256},
    }
    argv = [h1_sha, args.v3_release_sha256, str(replay),
            args.replay_receipt_sha256, args.array_job, args.reducer_job,
            args.replay_job, str(receipt_path("replay")),
            args.replay_submission_sha256]
    return args.replay_job, argv, inputs, authorities


def commit_receipt(path: Path, payload: Mapping[str, Any]) -> None:
    req(not path.exists(), "phase submission receipt already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".h1-submit.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=tuple(SCRIPTS), required=True)
    parser.add_argument("--payload-sha256", required=True)
    for name in (
        "v3-release-sha256", "canary-job", "canary-submission-sha256",
        "canary-receipt-sha256", "array-job", "production-submission-sha256",
        "reducer-job", "reducer-submission-sha256", "reduction-sha256",
        "replay-job", "replay-submission-sha256", "replay-receipt-sha256",
    ):
        parser.add_argument(f"--{name}")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    req(HEX64.fullmatch(args.payload_sha256) is not None
        and sha(PAYLOAD) == args.payload_sha256,
        "h1 payload manifest drift")
    script = ROOT / "code" / SCRIPTS[args.phase]
    req(script.is_file() and not script.is_symlink(), "fixed phase script missing/symlinked")
    output = receipt_path(args.phase)
    req(not output.exists(), "phase already submitted")
    dependency, script_args, inputs, authorities = phase_spec(args)
    command = ["sbatch", "--parsable", f"--dependency=afterok:{dependency}",
               f"code/{SCRIPTS[args.phase]}", *script_args]
    completed = subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True,
    )
    job = completed.stdout.strip().split(";")[0]
    req(DECIMAL.fullmatch(job) is not None, "sbatch returned a nondecimal job ID")
    readback = subprocess.run(
        ["scontrol", "show", "job", "-o", job], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    req(f"JobId={job}" in readback and f"Dependency=afterok:{dependency}" in readback
        and f"WorkDir={ROOT}" in readback and SCRIPTS[args.phase] in readback,
        "scontrol job/dependency/workdir/command readback drift")
    payload = {
        "schema": SCHEMA, "status": STATUS, "phase": args.phase,
        "job_id": job, "dependency_afterok": dependency,
        "payload_manifest_sha256": args.payload_sha256,
        "phase_inputs": inputs,
        "script": {"path": f"code/{SCRIPTS[args.phase]}", "sha256": sha(script)},
        "argv": command, "authorities": authorities,
        "scontrol_readback": readback,
    }
    req(set(payload) == TOP_KEYS, "internal submission receipt key drift")
    commit_receipt(output, payload)
    print(json.dumps({"status": STATUS, "phase": args.phase, "job_id": job,
                      "receipt_sha256": sha(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError,
            subprocess.CalledProcessError) as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        raise SystemExit(2)
