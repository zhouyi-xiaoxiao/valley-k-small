#!/usr/bin/env python3
"""H2 combined analysis with submission binding and pack diagnostics."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.stats import t as student_t

import analyze_gpu_gating_v4_r2_combined as statistics
import scientific_tail_replay_v4_r2_h2 as science

ROOT = Path("/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727")
V3 = Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-20260726-r3")
H2_PAYLOAD = ROOT / "notes/isambard_ai_v4_r2_h2_payload.sha256"
HETERO_CONTRACT = ROOT / "notes/isambard_ai_v4_r2_h2_pack_heterogeneity_contract.json"
H2_V3_RELEASE = ROOT / "artifacts/releases/v3-release-for-v4-r2-h2.json"
SUB = ROOT / "artifacts/submission_h2"
SUBMIT_SCHEMA = "grid2d-one-two-target-gating-v4-r2-h2-submission-v1"
SUBMIT_STATUS = "SUBMITTED_WITH_EXACT_READBACK"
COMBINED_SCRIPT = "isambard_ai_gating_v4_r2_combined_h2.sbatch"
TOP_KEYS = {
    "schema", "status", "phase", "job_id", "dependency_afterok",
    "payload_manifest_sha256", "phase_inputs", "script", "argv",
    "authorities", "scontrol_readback",
}


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def validate_combined_submission(
    path: Path, *, job_id: str, replay_job: str, h2_sha: str,
    v3_path: Path, v3_sha: str, replay_path: Path, replay_sha: str,
    replay_submit: Path, replay_submit_sha: str,
) -> dict[str, Any]:
    req(path == SUB / "combined-submission.json", "combined receipt path drift")
    value = science.strict_json(path, mode600=True)
    req(set(value) == TOP_KEYS and value["schema"] == SUBMIT_SCHEMA
        and value["status"] == SUBMIT_STATUS and value["phase"] == "combined"
        and value["job_id"] == job_id
        and value["dependency_afterok"] == replay_job
        and value["payload_manifest_sha256"] == h2_sha,
        "combined submission envelope drift")
    phase_inputs = {
        "v3_release_sha256": v3_sha,
        "v4_replay_receipt_sha256": replay_sha,
        "replay_job_id": replay_job,
        "replay_submission_sha256": replay_submit_sha,
    }
    authorities = {
        "v3_release": {"path": str(v3_path), "sha256": v3_sha},
        "v4_replay": {"path": str(replay_path), "sha256": replay_sha},
        "replay_submission": {"path": str(replay_submit),
                              "sha256": replay_submit_sha},
    }
    req(value["phase_inputs"] == phase_inputs
        and value["authorities"] == authorities,
        "combined submission authority map drift")
    script = ROOT / "code" / COMBINED_SCRIPT
    req(value["script"] == {"path": f"code/{COMBINED_SCRIPT}",
                             "sha256": science.sha(script)},
        "combined script path/hash drift")
    args = [
        h2_sha, str(v3_path), v3_sha, str(replay_path), replay_sha,
        replay_job, str(replay_submit), replay_submit_sha, str(path),
    ]
    expected_argv = [
        "sbatch", "--parsable", f"--dependency=afterok:{replay_job}",
        f"code/{COMBINED_SCRIPT}", *args,
    ]
    req(value["argv"] == expected_argv, "combined exact sbatch argv drift")
    readback = value["scontrol_readback"]
    req(isinstance(readback, str) and f"JobId={job_id}" in readback
        and f"Dependency=afterok:{replay_job}" in readback
        and f"WorkDir={ROOT}" in readback and COMBINED_SCRIPT in readback,
        "combined scontrol readback drift")
    return value


def welch(values3: np.ndarray, values4: np.ndarray) -> dict[str, Any]:
    n3, n4 = len(values3), len(values4)
    m3, m4 = float(values3.mean()), float(values4.mean())
    v3, v4 = float(values3.var(ddof=1)), float(values4.var(ddof=1))
    se2 = v3 / n3 + v4 / n4
    req(se2 > 0.0 and math.isfinite(se2), "pack Welch variance is invalid")
    se = math.sqrt(se2)
    df = se2 * se2 / ((v3 / n3) ** 2 / (n3 - 1)
                      + (v4 / n4) ** 2 / (n4 - 1))
    critical = float(student_t.ppf(0.975, df))
    difference = m4 - m3
    return {
        "v3_mean": m3, "v4_r2_mean": m4,
        "v4_r2_minus_v3": difference,
        "standard_error": se, "welch_degrees_of_freedom": df,
        "t_critical": critical,
        "ci_lower": difference - critical * se,
        "ci_upper": difference + critical * se,
        "observed_t": difference / se,
    }


def pack_heterogeneity(a3: np.ndarray, a4: np.ndarray,
                       contract: Mapping[str, Any]) -> dict[str, Any]:
    req(a3.shape == (32, 75) and a4.shape == (128, 75),
        "pack heterogeneity matrix shape drift")
    surface = [welch(a3[:, index], a4[:, index]) for index in range(75)]
    resamples = int(contract["surface_method"]["resamples"])
    seed = int(contract["surface_method"]["seed"])
    rng = np.random.Generator(np.random.PCG64(seed))
    centered3 = a3 - a3.mean(axis=0)
    centered4 = a4 - a4.mean(axis=0)
    maxima = np.empty(resamples)
    for start in range(0, resamples, 125):
        stop = min(start + 125, resamples)
        i3 = rng.integers(0, 32, size=(stop - start, 32), dtype=np.int64)
        i4 = rng.integers(0, 128, size=(stop - start, 128), dtype=np.int64)
        s3 = centered3[i3]
        s4 = centered4[i4]
        difference = s4.mean(axis=1) - s3.mean(axis=1)
        se = np.sqrt(s3.var(axis=1, ddof=1) / 32
                     + s4.var(axis=1, ddof=1) / 128)
        req(bool(np.all(se > 0)), "bootstrap pack Welch SE is zero")
        maxima[start:stop] = np.max(np.abs(difference / se), axis=1)
    order = int(contract["surface_method"]["critical_order_statistic_one_indexed"])
    critical = float(np.sort(maxima)[order - 1])
    observed = np.asarray([row["observed_t"] for row in surface])
    adjusted = (1 + np.sum(maxima[:, None] >= np.abs(observed)[None, :], axis=0)) \
        / (resamples + 1)
    band = float(contract["compatibility_band_absolute_probability"])
    rows: list[dict[str, Any]] = []
    for index, ((x, y, amplitude), item) in enumerate(zip(statistics.COLUMNS,
                                                           surface, strict=True)):
        item = dict(item)
        item.update({
            "contrast_index": index, "target2_x": x, "target2_y": y,
            "control_amplitude": 0.0, "treatment_amplitude": amplitude,
            "simultaneous_ci_lower": item["v4_r2_minus_v3"]
                                     - critical * item["standard_error"],
            "simultaneous_ci_upper": item["v4_r2_minus_v3"]
                                     + critical * item["standard_error"],
            "adjusted_p_value": float(adjusted[index]),
        })
        rows.append(item)
    primary_spec = contract["primary_contrast"]
    primary_index = statistics.COLUMNS.index((
        int(primary_spec["target2_x"]), int(primary_spec["target2_y"]),
        float(primary_spec["amplitude_high"]),
    ))
    primary = rows[primary_index]
    primary_flag = ((primary["ci_lower"] > 0.0 or primary["ci_upper"] < 0.0)
                    and abs(primary["v4_r2_minus_v3"]) > band)
    surface_flags = [row["contrast_index"] for row in rows
                     if row["adjusted_p_value"] <= 0.05
                     and abs(row["v4_r2_minus_v3"]) > band]
    flagged = primary_flag or bool(surface_flags)
    return {
        "contract_sha256": science.sha(HETERO_CONTRACT),
        "estimand": contract["estimand"],
        "primary": primary,
        "surface": {
            "resamples": resamples, "seed": seed,
            "critical_value": critical, "rows": rows,
        },
        "flagged_contrast_indices": surface_flags,
        "status": ("FLAG_PACK_HETEROGENEITY_REVIEW" if flagged else
                   "PASS_NO_MATERIAL_PACK_HETEROGENEITY_DETECTED"),
        "pooling_policy": contract["decision_rule"]["pooling_policy"],
    }


def analyze(
    *, h2_sha: str, v3_path: Path, v3_sha: str, replay_path: Path,
    replay_sha: str, replay_job: str, replay_submit: Path,
    replay_submit_sha: str, combined_submit: Path, slurm_job_id: str,
    runtime_receipt: Path,
) -> dict[str, Any]:
    req(science.sha(H2_PAYLOAD) == h2_sha, "H2 payload hash drift")
    req(v3_path == H2_V3_RELEASE and science.sha(v3_path) == v3_sha,
        "H2 v3 release path/hash drift")
    v3_release = science.strict_json(v3_path, mode600=True)
    req(v3_release.get("schema") ==
        "grid2d-one-two-target-gating-v3-release-for-v4-r2-h2"
        and v3_release.get("status") == "PASS_AUTHORIZE_V4_R2_H2_HARDWARE_CANARY"
        and v3_release.get("authorizes_v4_r2_h2") is True
        and v3_release.get("scientific_tail_replay", {}).get("status")
            == "PASS_TAIL_EVIDENCE",
        "H2 v3 release did not pass raw tail replay")
    req(replay_path.parent == ROOT / "artifacts/replay"
        and science.sha(replay_path) == replay_sha,
        "H2 v4 replay path/hash drift")
    replay = science.strict_json(replay_path, mode600=True)
    req(replay.get("schema") ==
        "grid2d-one-two-target-gating-v4-r2-independent-replay-h2"
        and replay.get("status") == "PASS_AUTHORIZE_V3_V4_R2_H2_COMBINED"
        and replay.get("authorizes_combined") is True
        and replay.get("scientific_tail_replay", {}).get("status")
            == "PASS_TAIL_EVIDENCE",
        "H2 v4 replay did not authorize combined analysis")
    submission = validate_combined_submission(
        combined_submit, job_id=slurm_job_id, replay_job=replay_job,
        h2_sha=h2_sha, v3_path=v3_path, v3_sha=v3_sha,
        replay_path=replay_path, replay_sha=replay_sha,
        replay_submit=replay_submit, replay_submit_sha=replay_submit_sha,
    )
    runtime = science.strict_json(runtime_receipt, mode600=True)
    req(runtime.get("status") == "PASS_FIXED_CONTAINER_PYTHON_GE_3_10"
        and runtime.get("phase") == "combined"
        and runtime.get("slurm_job_id") == slurm_job_id,
        "combined runtime receipt drift")
    h1_path = Path(v3_release["h1_release"]["path"])
    req(science.sha(h1_path) == v3_release["h1_release"]["sha256"],
        "nested H1 v3 release hash drift")
    h1_release = science.strict_json(h1_path, mode600=True)
    v3_csv = V3 / (
        "artifacts/outputs/isambard_ai_v3/reductions/"
        "production-5788353-reduce-5788358/reduction.csv"
    )
    req(science.sha(v3_csv) == h1_release["evidence_hashes"]["reduction_csv"],
        "v3 reduction CSV reverse hash drift")
    jobs = replay["jobs"]
    v4_csv = ROOT / (
        f"artifacts/outputs/isambard_ai_v4_r2/reduction-{jobs['array']}-"
        f"{jobs['reducer']}/reduction_v4_r2.csv"
    )
    req(science.sha(v4_csv) == replay["hashes"]["reduction_csv"],
        "v4 reduction CSV reverse hash drift")
    values3 = statistics.csv_values(v3_csv, 32, science.sha(v3_csv))
    values4 = statistics.csv_values(v4_csv, 128, science.sha(v4_csv))
    a3 = statistics.effects(values3, 32)
    a4 = statistics.effects(values4, 128)
    pooled = np.vstack((a3, a4))
    req(pooled.shape == (160, 75), "H2 pooled matrix drift")
    contract = science.strict_json(HETERO_CONTRACT)
    heterogeneity = pack_heterogeneity(a3, a4, contract)
    return {
        "schema": "grid2d-one-two-target-gating-v4-r2-combined-h2",
        "status": "PASS_H2_COMBINED_COMPUTATION_AWAIT_TERMINAL_RELEASE",
        "authorization": {
            "h2_payload_manifest_sha256": h2_sha,
            "v3_release_receipt_sha256": v3_sha,
            "v4_replay_receipt_sha256": replay_sha,
            "replay_submission_receipt_sha256": replay_submit_sha,
            "v3_reduction_csv_sha256": science.sha(v3_csv),
            "v4_reduction_csv_sha256": science.sha(v4_csv),
        },
        "submission_binding": {
            "combined_job_id": slurm_job_id,
            "combined_submission_receipt_path": str(combined_submit),
            "combined_submission_receipt_sha256": science.sha(combined_submit),
            "script": submission["script"],
            "argv": submission["argv"],
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


def commit(path: Path, data: bytes) -> None:
    req(not path.exists(), "H2 combined output exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".combined-h2.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h2-payload-sha256", required=True)
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
            h2_sha=args.h2_payload_sha256, v3_path=args.v3_release,
            v3_sha=args.v3_release_sha256, replay_path=args.v4_replay_receipt,
            replay_sha=args.v4_replay_sha256, replay_job=args.replay_job,
            replay_submit=args.replay_submission,
            replay_submit_sha=args.replay_submission_sha256,
            combined_submit=args.combined_submission,
            slurm_job_id=args.slurm_job_id,
            runtime_receipt=args.runtime_receipt,
        )
        buffer = io.StringIO(newline="")
        rows = payload["surface"]["combined"]["rows"]
        writer = csv.DictWriter(buffer, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
        csv_data = buffer.getvalue().encode()
        payload["csv"] = {"filename": args.output_csv.name,
                          "sha256": hashlib.sha256(csv_data).hexdigest(), "rows": 75}
        json_data = (json.dumps(payload, indent=2, sort_keys=True,
                                allow_nan=False) + "\n").encode()
        commit(args.output_csv, csv_data)
        try:
            commit(args.output_json, json_data)
        except BaseException:
            args.output_csv.unlink(missing_ok=True)
            raise
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr)
        return 2
    print(json.dumps({"status": payload["status"],
                      "combined_job_id": args.slurm_job_id}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
