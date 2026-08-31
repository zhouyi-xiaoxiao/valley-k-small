#!/usr/bin/env python3
"""Deep-authority h1 gate before preregistered v4-r2 pooled inference."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import independent_replay_gpu_gating_v4_r2_h1 as replay

ROOT = replay.ROOT
V3 = Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-20260726-r3")
SECONDARY = Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-secondary-r1-20260727")
V3_RECEIPT = replay.V3_RELEASE
FIXED_CONTRACTS = {
    "v3_manifest_sha256": "419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f",
    "active_v3_payload_manifest_sha256": "9a56344f23afc0f14a269c7e4c10a062e920d5393032a223eccbb9eaa4269dd9",
    "submission_state_sha256": "bfdab79ad8156de7a79a3d4a475eff6608bb08354847c5036b0dc081c795b947",
    "secondary_contract_sha256": "96a42bd4af0260a45876ba3cae8b671bc83888cb34d89c3f9a80c99a1fb21f74",
    "secondary_payload_manifest_sha256": "acdae65da56e5e7ff2d4de4cf36fe680ec9d5184ed211f7c726b18358d6d5c20",
}
FIXED_JOBS = {
    "environment": "5788353", "canary_array": "5788354",
    "canary_reducer": "5788356", "production_array": "5788357",
    "reducer": "5788358", "secondary": "5789031",
}
HEX64 = re.compile(r"[0-9a-f]{64}")


def req(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_regular(path: Path, *, mode600: bool = False) -> None:
    stat = path.lstat()
    req(path.is_file() and not path.is_symlink() and stat.st_nlink == 1,
        f"unsafe evidence file: {path}")
    if mode600:
        req(stat.st_mode & 0o777 == 0o600, f"evidence mode is not 0600: {path}")


def strict_json(path: Path, *, mode600: bool = False) -> dict[str, Any]:
    safe_regular(path, mode600=mode600)
    def hook(pairs):
        value = {}
        for key, item in pairs:
            req(key not in value, f"duplicate JSON key {key}: {path}")
            value[key] = item
        return value
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook,
                       parse_constant=lambda token: (_ for _ in ()).throw(
                           ValueError(f"nonfinite JSON {token}: {path}")))
    req(isinstance(value, dict), f"JSON root is not object: {path}")
    return value


def validate_replay_shape(value: Mapping[str, Any], h1_sha: str) -> None:
    """Pure receipt-shape gate used by tests before any reverse file reads."""
    req(set(value) == replay.OUTPUT_KEYS
        and value.get("schema") == "grid2d-one-two-target-gating-v4-r2-independent-replay-h1"
        and value.get("status") == "PASS_AUTHORIZE_V3_V4_R2_H1_COMBINED"
        and value.get("fixed_root") == str(ROOT), "replay receipt envelope drift")
    jobs = value["jobs"]
    req(isinstance(jobs, dict) and set(jobs) == {"run_token", "array", "reducer"}
        and jobs["run_token"] == jobs["array"]
        and all(isinstance(item, str) and item.isdigit() for item in jobs.values()),
        "replay receipt jobs drift")
    req(value["fixed_artifacts"] == {
        "manifest_sha256": replay.FIXED["manifest"],
        "field_pack_sha256": replay.FIXED["field"],
        "base_payload_sha256": replay.FIXED["base_payload"],
        "h1_payload_sha256": h1_sha,
        "container_sha256": replay.FIXED["container"],
    }, "replay receipt artifact pins drift")
    req(isinstance(value["hashes"], dict)
        and set(value["hashes"]) == {"reduction_json", "reduction_csv", "sacct_receipt"}
        and all(isinstance(item, str) and HEX64.fullmatch(item) is not None
                for item in value["hashes"].values()), "replay receipt hash map drift")
    raw = value["raw"]
    req(isinstance(raw, dict) and set(raw) == {"exact_tree", "cells", "pairs", "blocks", "raw_inventory_digest", "recomputed_block_digest"}
        and raw["cells"] == raw["pairs"] == 23040 and raw["blocks"] == 11520
        and raw["raw_inventory_digest"] == value["reduction_inventory_digest"]
        and all(isinstance(raw[key], str) and HEX64.fullmatch(raw[key]) is not None
                for key in ("raw_inventory_digest", "recomputed_block_digest")),
        "replay receipt raw summary drift")
    tree = raw["exact_tree"]
    req(isinstance(tree, dict) and tree == {"exact_tree": True, "cell_directories": 23040, "files": 46080, "tree_digest": tree.get("tree_digest")}
        and isinstance(tree["tree_digest"], str) and HEX64.fullmatch(tree["tree_digest"]) is not None,
        "replay receipt tree summary drift")
    sacct = value["extended_sacct"]
    req(isinstance(sacct, dict) and set(sacct) == {"independently_parsed", "array_job_id", "parent_rows", "tasks", "unique_allocations", "cells_per_allocation", "gpus_per_allocation", "nodes_per_allocation", "elapsed_raw_total_seconds", "actual_full_node_nhr", "receipt_sha256"}
        and sacct["independently_parsed"] is True and sacct["array_job_id"] == jobs["array"]
        and sacct["parent_rows"] == 1 and sacct["tasks"] == sacct["unique_allocations"] == 480
        and sacct["cells_per_allocation"] == 48 and sacct["gpus_per_allocation"] == 4
        and sacct["nodes_per_allocation"] == 1
        and isinstance(sacct["elapsed_raw_total_seconds"], int) and sacct["elapsed_raw_total_seconds"] > 0
        and sacct["actual_full_node_nhr"] == sacct["elapsed_raw_total_seconds"] / 3600.0
        and sacct["receipt_sha256"] == value["hashes"]["sacct_receipt"],
        "replay receipt sacct summary drift")
    chain = value["submission_chain"]
    req(isinstance(chain, dict) and set(chain) == {"v3_release_sha256", "canary_job_id", "canary_submission_receipt_sha256", "canary_receipt_sha256", "production_submission_receipt_sha256", "reducer_submission_receipt_sha256"}
        and isinstance(chain["canary_job_id"], str) and chain["canary_job_id"].isdigit()
        and all(isinstance(item, str) and HEX64.fullmatch(item) is not None
                for key, item in chain.items() if key != "canary_job_id"),
        "replay receipt submission summary drift")


def validate_v3(receipt_sha: str) -> tuple[dict[str, Any], Path]:
    req(HEX64.fullmatch(receipt_sha) is not None and sha(V3_RECEIPT) == receipt_sha,
        "v3 h1 release receipt SHA drift")
    value = strict_json(V3_RECEIPT, mode600=True)
    req(set(value) == {
        "schema", "status", "fixed_roots", "fixed_jobs", "fixed_contracts",
        "evidence_hashes", "inventory_digest", "raw_replay",
        "live_sacct_query_sha256", "secondary_result_schema",
        "secondary_result_status", "canary_reduction",
    } and value["schema"] == "grid2d-one-two-target-gating-v3-release-for-v4-r2-h1"
      and value["status"] == "PASS_AUTHORIZE_V4_R2_H1_HARDWARE_CANARY"
      and value["fixed_roots"] == {
          "v3": str(V3), "secondary": str(SECONDARY), "v4_r2": str(ROOT)
      } and value["fixed_jobs"] == FIXED_JOBS
      and value["fixed_contracts"] == FIXED_CONTRACTS,
      "v3 h1 release fixed contract drift")
    paths = {
        "manifest": V3 / "artifacts/data/gating_v3_production_manifest.json",
        "active_v3_payload": V3 / "notes/isambard_ai_v3_payload.sha256",
        "submission_state": V3 / "artifacts/outputs/isambard_ai_v3/submission/submission_state_v3.json",
        "reduction_json": V3 / "artifacts/outputs/isambard_ai_v3/reductions/production-5788353-reduce-5788358/reduction.json",
        "reduction_csv": V3 / "artifacts/outputs/isambard_ai_v3/reductions/production-5788353-reduce-5788358/reduction.csv",
        "sacct_receipt": V3 / "artifacts/outputs/isambard_ai_v3/reductions/production-5788353-reduce-5788358/sacct-production-5788353.psv",
        "contract": SECONDARY / "notes/isambard_ai_v3_secondary_analysis_contract_r1.json",
        "payload": SECONDARY / "notes/isambard_ai_v3_secondary_r1.sha256",
        "secondary_json": SECONDARY / "artifacts/outputs/isambard_ai_v3/secondary_r1/upstream-5788358-secondary-5789031/secondary_max_t_r1.json",
        "secondary_csv": SECONDARY / "artifacts/outputs/isambard_ai_v3/secondary_r1/upstream-5788358-secondary-5789031/secondary_max_t_r1.csv",
    }
    hashes = value["evidence_hashes"]
    req(isinstance(hashes, dict) and set(hashes) == set(paths),
        "v3 evidence exact hash inventory drift")
    for name, path in paths.items():
        safe_regular(path, mode600=name in {
            "submission_state", "reduction_json", "reduction_csv", "sacct_receipt",
            "secondary_json", "secondary_csv",
        })
        req(hashes[name] == sha(path), f"v3 reverse hash drift: {name}")
    req(hashes["manifest"] == FIXED_CONTRACTS["v3_manifest_sha256"]
        and hashes["active_v3_payload"] == FIXED_CONTRACTS["active_v3_payload_manifest_sha256"]
        and hashes["submission_state"] == FIXED_CONTRACTS["submission_state_sha256"]
        and hashes["contract"] == FIXED_CONTRACTS["secondary_contract_sha256"]
        and hashes["payload"] == FIXED_CONTRACTS["secondary_payload_manifest_sha256"],
        "v3 fixed evidence hash drift")
    for payload_path, base_root in ((paths["active_v3_payload"], V3),
                                    (paths["payload"], SECONDARY)):
        for line in payload_path.read_text(encoding="utf-8").splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)", line)
            req(match is not None, "malformed nested v3 payload manifest")
            digest, relative = match.groups(); member = base_root / relative
            safe_regular(member); req(sha(member) == digest, f"nested payload drift: {relative}")
    reduction = strict_json(paths["reduction_json"], mode600=True)
    req(reduction.get("schema") == "grid2d-one-two-target-gating-gpu-v3-reduction-v1"
        and reduction.get("mode") == "full" and reduction.get("audit", {}).get("pass") is True
        and reduction.get("audit", {}).get("fail_closed") is True
        and reduction.get("audit", {}).get("manifest_sha256") == FIXED_CONTRACTS["v3_manifest_sha256"]
        and reduction.get("audit", {}).get("inventory_digest") == value["inventory_digest"]
        and reduction.get("audit", {}).get("sacct", {}).get("receipt_sha256") == hashes["sacct_receipt"]
        and reduction.get("csv", {}).get("sha256") == hashes["reduction_csv"],
        "v3 production reduction authority drift")
    raw_replay = value["raw_replay"]
    req(raw_replay == {
        "independently_verified": True, "raw_cells": 5760,
        "json_npz_pairs": 5760, "block_means": 2880,
        "raw_inventory_digest": raw_replay.get("raw_inventory_digest"),
        "recomputed_block_digest": raw_replay.get("recomputed_block_digest"),
    } and all(HEX64.fullmatch(raw_replay[key]) is not None
              for key in ("raw_inventory_digest", "recomputed_block_digest")),
        "v3 raw replay receipt drift")
    req(HEX64.fullmatch(value["inventory_digest"]) is not None
        and HEX64.fullmatch(value["live_sacct_query_sha256"]) is not None
        and value["secondary_result_schema"] == "grid2d-one-two-target-gating-secondary-max-t-r1"
        and value["secondary_result_status"] == "PASS_SECONDARY_MAX_T_R1",
        "v3 release digest/secondary status drift")
    secondary = strict_json(paths["secondary_json"], mode600=True)
    req(secondary.get("schema") == value["secondary_result_schema"]
        and secondary.get("status") == value["secondary_result_status"]
        and secondary.get("audit", {}).get("pass") is True
        and secondary.get("audit", {}).get("fail_closed") is True
        and secondary.get("csv", {}).get("sha256") == hashes["secondary_csv"],
        "secondary result reverse authority drift")
    canary = value["canary_reduction"]
    req(isinstance(canary, dict) and set(canary) == {
        "schema", "status", "manifest_sha256", "reduction_json_sha256",
        "reduction_csv_sha256", "sacct_receipt_sha256", "cell_count",
        "allocation_count", "cells_per_allocation", "csv_rows",
        "inventory_digest", "independent_sacct",
    } and canary["schema"] == "grid2d-one-two-target-gating-v3-canary-release-h1"
      and canary["status"] == "PASS_CANARY_CONTENT"
      and canary["manifest_sha256"] == "5c056e20fc45c97f6e8d444ecdb9b63c334483ceb8461387d83d3e1612873fe4"
      and canary["cell_count"] == canary["allocation_count"] == canary["csv_rows"] == 8
      and canary["cells_per_allocation"] == 1,
      "v3 canary h1 receipt contract drift")
    canary_dir = V3 / "artifacts/outputs/isambard_ai_v3/reductions/canary-5788353-reduce-5788356"
    canary_paths = {
        "reduction_json_sha256": canary_dir / "reduction.json",
        "reduction_csv_sha256": canary_dir / "reduction.csv",
        "sacct_receipt_sha256": canary_dir / "sacct-canary-5788353.psv",
    }
    for key, path in canary_paths.items():
        safe_regular(path, mode600=True); req(canary[key] == sha(path), f"canary reverse hash drift: {key}")
    independent_sacct = canary["independent_sacct"]
    req(independent_sacct == {
        "independently_parsed": True, "parent_rows": 1, "allocations": 8,
        "cells": 8, "cells_per_allocation": 1, "state": "COMPLETED",
        "exit_code": "0:0", "receipt_sha256": canary["sacct_receipt_sha256"],
    } and canary["inventory_digest"] == strict_json(canary_paths["reduction_json"], mode600=True)["audit"]["inventory_digest"],
        "canary independent sacct/inventory authority drift")
    return value, paths["reduction_csv"]


def validate_v4(
    replay_path: Path, replay_sha: str, replay_job: str,
    replay_submission_path: Path, replay_submission_sha: str,
    h1_sha: str,
) -> tuple[dict[str, Any], Path]:
    req(replay_path.parent == ROOT / "artifacts/replay"
        and re.fullmatch(r"v4-r2-replay-h1-[0-9]+\.json", replay_path.name) is not None
        and sha(replay_path) == replay_sha,
        "v4 replay fixed path/SHA drift")
    value = strict_json(replay_path, mode600=True)
    validate_replay_shape(value, h1_sha)
    req(set(value) == replay.OUTPUT_KEYS
        and value["schema"] == "grid2d-one-two-target-gating-v4-r2-independent-replay-h1"
        and value["status"] == "PASS_AUTHORIZE_V3_V4_R2_H1_COMBINED"
        and value["fixed_root"] == str(ROOT), "v4 replay top-level authority drift")
    jobs = value["jobs"]
    req(isinstance(jobs, dict) and set(jobs) == {"run_token", "array", "reducer"}
        and jobs["run_token"] == jobs["array"]
        and all(isinstance(item, str) and item.isdigit() for item in jobs.values())
        and replay_path.name == f"v4-r2-replay-h1-{jobs['reducer']}.json",
        "v4 replay job identity drift")
    req(value["fixed_artifacts"] == {
        "manifest_sha256": replay.FIXED["manifest"],
        "field_pack_sha256": replay.FIXED["field"],
        "base_payload_sha256": replay.FIXED["base_payload"],
        "h1_payload_sha256": h1_sha,
        "container_sha256": replay.FIXED["container"],
    } and sha(replay.PAYLOAD) == h1_sha, "v4 replay fixed artifact drift")
    reduction_dir = ROOT / f"artifacts/outputs/isambard_ai_v4_r2/reduction-{jobs['array']}-{jobs['reducer']}"
    reduction_paths = {
        "reduction_json": reduction_dir / "reduction_v4_r2.json",
        "reduction_csv": reduction_dir / "reduction_v4_r2.csv",
        "sacct_receipt": reduction_dir / f"sacct-v4-r2-{jobs['array']}.psv",
    }
    req(isinstance(value["hashes"], dict) and set(value["hashes"]) == set(reduction_paths),
        "v4 replay exact evidence hash keys drift")
    for name, path in reduction_paths.items():
        safe_regular(path, mode600=True); req(value["hashes"][name] == sha(path), f"v4 reverse hash drift: {name}")
    reduction = strict_json(reduction_paths["reduction_json"], mode600=True)
    req(reduction.get("schema") == "grid2d-one-two-target-gating-gpu-v4-r2-reduction-v1"
        and reduction.get("mode") == "full" and reduction.get("audit", {}).get("pass") is True
        and reduction.get("audit", {}).get("fail_closed") is True
        and reduction.get("audit", {}).get("inventory_digest") == value["reduction_inventory_digest"]
        and reduction.get("audit", {}).get("sacct", {}).get("receipt_sha256") == value["hashes"]["sacct_receipt"]
        and reduction.get("csv", {}).get("sha256") == value["hashes"]["reduction_csv"],
        "v4 reduction reverse authority drift")
    raw = value["raw"]
    req(isinstance(raw, dict) and set(raw) == {
        "exact_tree", "cells", "pairs", "blocks", "raw_inventory_digest",
        "recomputed_block_digest",
    } and raw["cells"] == raw["pairs"] == 23040 and raw["blocks"] == 11520
      and raw["raw_inventory_digest"] == value["reduction_inventory_digest"]
      and all(HEX64.fullmatch(raw[key]) is not None
              for key in ("raw_inventory_digest", "recomputed_block_digest")),
      "v4 replay raw receipt drift")
    tree = raw["exact_tree"]
    req(tree == {"exact_tree": True, "cell_directories": 23040, "files": 46080,
                 "tree_digest": tree.get("tree_digest")}
        and HEX64.fullmatch(tree["tree_digest"]) is not None,
        "v4 replay exact raw-tree receipt drift")
    sacct = value["extended_sacct"]
    req(isinstance(sacct, dict) and set(sacct) == {
        "independently_parsed", "array_job_id", "parent_rows", "tasks",
        "unique_allocations", "cells_per_allocation", "gpus_per_allocation",
        "nodes_per_allocation", "elapsed_raw_total_seconds",
        "actual_full_node_nhr", "receipt_sha256",
    } and sacct["independently_parsed"] is True
      and sacct["array_job_id"] == jobs["array"] and sacct["parent_rows"] == 1
      and sacct["tasks"] == sacct["unique_allocations"] == 480
      and sacct["cells_per_allocation"] == 48 and sacct["gpus_per_allocation"] == 4
      and sacct["nodes_per_allocation"] == 1
      and isinstance(sacct["elapsed_raw_total_seconds"], int)
      and sacct["elapsed_raw_total_seconds"] > 0
      and sacct["actual_full_node_nhr"] == sacct["elapsed_raw_total_seconds"] / 3600.0
      and sacct["receipt_sha256"] == value["hashes"]["sacct_receipt"],
      "v4 independent extended sacct receipt drift")
    chain = value["submission_chain"]
    req(isinstance(chain, dict) and set(chain) == {
        "v3_release_sha256", "canary_job_id",
        "canary_submission_receipt_sha256", "canary_receipt_sha256",
        "production_submission_receipt_sha256", "reducer_submission_receipt_sha256",
    }, "v4 replay submission-chain exact keys drift")
    replayed_chain = replay.validate_submission_chain(
        array_job=jobs["array"], reducer_job=jobs["reducer"], h1_sha=h1_sha,
        production_path=replay.receipt_path("production"),
        production_sha=chain["production_submission_receipt_sha256"],
        reducer_path=replay.receipt_path("reducer"),
        reducer_sha=chain["reducer_submission_receipt_sha256"],
    )
    req(chain == replayed_chain, "v4 replay submission-chain reverse validation drift")
    replay_inputs = {
        "array_job_id": jobs["array"], "reducer_job_id": jobs["reducer"],
        "production_submission_sha256": chain["production_submission_receipt_sha256"],
        "reducer_submission_sha256": chain["reducer_submission_receipt_sha256"],
        "reduction_json_sha256": value["hashes"]["reduction_json"],
    }
    replay_authorities = {
        "production_submission": {
            "path": str(replay.receipt_path("production")),
            "sha256": chain["production_submission_receipt_sha256"],
        },
        "reducer_submission": {
            "path": str(replay.receipt_path("reducer")),
            "sha256": chain["reducer_submission_receipt_sha256"],
        },
        "reduction_json": {
            "path": str(reduction_paths["reduction_json"]),
            "sha256": value["hashes"]["reduction_json"],
        },
    }
    replay.validate_submission(
        phase="replay", path=replay_submission_path,
        expected_sha=replay_submission_sha, h1_sha=h1_sha,
        job=replay_job, dependency=jobs["reducer"],
        phase_inputs=replay_inputs, authorities=replay_authorities,
        script_args=[
            h1_sha, jobs["array"], jobs["array"], jobs["reducer"],
            value["hashes"]["reduction_json"],
            str(replay.receipt_path("production")),
            chain["production_submission_receipt_sha256"],
            str(replay.receipt_path("reducer")),
            chain["reducer_submission_receipt_sha256"],
        ],
    )
    return value, reduction_paths["reduction_csv"]


def analyze(
    *, v3_sha: str, replay_path: Path, replay_sha: str, replay_job: str,
    replay_submission: Path, replay_submission_sha: str, h1_sha: str,
) -> dict[str, Any]:
    import analyze_gpu_gating_v4_r2_combined as statistics
    v3, v3_csv = validate_v3(v3_sha)
    v4, v4_csv = validate_v4(replay_path, replay_sha, replay_job,
                              replay_submission, replay_submission_sha, h1_sha)
    v3_values = statistics.csv_values(v3_csv, 32, v3["evidence_hashes"]["reduction_csv"])
    v4_values = statistics.csv_values(v4_csv, 128, v4["hashes"]["reduction_csv"])
    a3 = statistics.effects(v3_values, 32); a4 = statistics.effects(v4_values, 128)
    pooled = np.vstack((a3, a4)); req(pooled.shape == (160, 75), "pooled matrix drift")
    return {
        "schema": "grid2d-one-two-target-gating-v4-r2-combined-h1",
        "status": "PASS_V4_R2_H1_COMBINED_INFERENCE",
        "authorization": {
            "v3_release_receipt_sha256": v3_sha,
            "v4_replay_receipt_sha256": replay_sha,
            "replay_submission_receipt_sha256": replay_submission_sha,
            "h1_payload_manifest_sha256": h1_sha,
            "v3_reduction_csv_sha256": sha(v3_csv),
            "v4_reduction_csv_sha256": sha(v4_csv),
        },
        "primary": {
            "v4_only": statistics.primary(a4, "v4-only reflect pack"),
            "combined": statistics.primary(pooled, "v3 plus independent v4-r2 reflect packs"),
        },
        "surface": {
            "v4_only": statistics.max_t(a4, 2026072700),
            "combined": statistics.max_t(pooled, 2026072701),
        },
    }


def commit(path: Path, data: bytes) -> None:
    req(not path.exists(), "combined output exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".combined-h1.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v3-release-sha256", required=True)
    parser.add_argument("--v4-replay-receipt", type=Path, required=True)
    parser.add_argument("--v4-replay-sha256", required=True)
    parser.add_argument("--replay-job", required=True)
    parser.add_argument("--replay-submission", type=Path, required=True)
    parser.add_argument("--replay-submission-sha256", required=True)
    parser.add_argument("--h1-payload-sha256", required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = analyze(
            v3_sha=args.v3_release_sha256,
            replay_path=args.v4_replay_receipt,
            replay_sha=args.v4_replay_sha256,
            replay_job=args.replay_job,
            replay_submission=args.replay_submission,
            replay_submission_sha=args.replay_submission_sha256,
            h1_sha=args.h1_payload_sha256,
        )
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=tuple(payload["surface"]["combined"]["rows"][0]),
                                lineterminator="\n")
        writer.writeheader(); writer.writerows(payload["surface"]["combined"]["rows"])
        csv_data = buffer.getvalue().encode()
        payload["csv"] = {"filename": args.output_csv.name,
                          "sha256": hashlib.sha256(csv_data).hexdigest(), "rows": 75}
        json_data = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        commit(args.output_csv, csv_data)
        try:
            commit(args.output_json, json_data)
        except BaseException:
            args.output_csv.unlink(missing_ok=True); raise
    except Exception as error:
        print(f"FAIL-CLOSED: {error}", file=os.sys.stderr); return 2
    print(json.dumps({"status": payload["status"],
                      "combined_n": payload["primary"]["combined"]["n"],
                      "df": payload["primary"]["combined"]["degrees_of_freedom"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
