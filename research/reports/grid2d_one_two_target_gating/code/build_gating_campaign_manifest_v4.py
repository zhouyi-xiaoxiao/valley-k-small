#!/usr/bin/env python3
"""Build the exact 23,040-cell frozen v4 production manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

import numpy as np

SCHEMA = "grid2d-one-two-target-gating-gpu-v4-manifest"
PACK_SCHEMA = "grid2d-one-two-target-gating-disorder-field-pack-v4"
RESULT_SCHEMA = "grid2d-one-two-target-gating-fixed-mean-gpu-v4"
FIELD_COUNT = 128
GEOMETRIES = tuple((x, y) for x in (24, 32, 40) for y in (9, 16, 24, 31, 38))
AMPLITUDES = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25)
STREAMS = (0, 1)
WALK_SEED_BASE = 12_000_000_000
FIELD_STRIDE = 104_729
STREAM_STRIDE = 1_009
CONTAINER_REFERENCE = "/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif"
CONTAINER_SHA256 = "aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4"
REPORT_ROOT = Path(__file__).resolve().parents[1]
DATA = REPORT_ROOT / "artifacts/data"
DEFAULT_PACK = DATA / "disorder_field_pack_v4.npz"
DEFAULT_SIDECAR = DATA / "disorder_field_pack_v4.manifest.json"
DEFAULT_OUTPUT = DATA / "gating_v4_production_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    def strict(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key!r}")
            result[key] = value
        return result
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict)
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def walk_seed(field: int, stream: int) -> int:
    return WALK_SEED_BASE + FIELD_STRIDE * field + STREAM_STRIDE * stream


def cells() -> list[dict[str, Any]]:
    result = []
    for x, y in GEOMETRIES:
        for amplitude in AMPLITUDES:
            for field in range(FIELD_COUNT):
                for stream in STREAMS:
                    result.append({
                        "cell_id": len(result), "target2_x": x, "target2_y": y,
                        "amplitude": amplitude, "disorder_replicate": field,
                        "walk_replicate": stream, "walk_seed": walk_seed(field, stream),
                    })
    return result


def validate(manifest: Mapping[str, Any], *, pack: Path, sidecar: Path, runner: Path, engine: Path) -> dict[str, Any]:
    if set(manifest) != {"schema", "campaign", "defaults", "profiles", "field_pack_sha256", "artifacts", "preregistration", "cells"}:
        raise ValueError("v4 manifest top-level inventory drift")
    if manifest["schema"] != SCHEMA:
        raise ValueError("v4 manifest schema drift")
    campaign = manifest["campaign"]
    if campaign != {"kind": "production", "cell_count": 23040, "domain": {"width": 64, "height": 48}}:
        raise ValueError("campaign identity drift")
    defaults = {
        "walkers": 1_000_000, "steps": 80_000, "batch_size": 131_072,
        "base_hold": 0.30, "target_radius": 3, "start_x": 7, "start_y": 24,
        "target1_x": 54, "target1_y": 24,
        "checkpoints": [5_000, 10_000, 20_000, 40_000, 80_000],
        "seed_base": WALK_SEED_BASE,
    }
    if manifest["defaults"] != defaults or manifest["profiles"] != {"frozen_80k": {}}:
        raise ValueError("scientific defaults drift")
    if sha256_file(pack) != manifest["field_pack_sha256"]:
        raise ValueError("field pack hash drift")
    side = load_json(sidecar)
    if side.get("schema") != PACK_SCHEMA or side.get("pack", {}).get("sha256") != sha256_file(pack):
        raise ValueError("field sidecar drift")
    with np.load(pack, allow_pickle=False) as value:
        contrasts = np.asarray(value["contrasts"], dtype="<f8")
        seeds = np.asarray(value["seeds"], dtype="<i8")
    if contrasts.shape != (128, 48, 64) or seeds.tolist() != [8_202_607_270_000 + 1_000_003 * i for i in range(128)]:
        raise ValueError("field pack shape/seed domain drift")
    records = side.get("fields")
    if not isinstance(records, list) or len(records) != 128:
        raise ValueError("field record inventory drift")
    for i, field in enumerate(contrasts):
        if math.fsum(float(v) for v in field.reshape(-1)) != 0.0 or float(np.max(np.abs(field))) != 1.0:
            raise ValueError(f"field {i} normalization drift")
        if records[i].get("index") != i or records[i].get("seed") != int(seeds[i]):
            raise ValueError(f"field {i} sidecar identity drift")
        if hashlib.sha256(field.tobytes(order="C")).hexdigest() != records[i].get("sha256_float64_le"):
            raise ValueError(f"field {i} content hash drift")
    artifacts = manifest["artifacts"]
    expected_artifacts = {
        "field_pack": {"filename": pack.name, "sha256": sha256_file(pack), "sidecar_filename": sidecar.name, "sidecar_sha256": sha256_file(sidecar)},
        "runner_source": {"filename": runner.name, "sha256": sha256_file(runner)},
        "runner_engine": {"filename": engine.name, "sha256": sha256_file(engine)},
        "container": {"reference": CONTAINER_REFERENCE, "sha256": CONTAINER_SHA256},
        "result_schema": RESULT_SCHEMA,
    }
    if artifacts != expected_artifacts:
        raise ValueError("artifact hash inventory drift")
    expected_cells = cells()
    if manifest["cells"] != expected_cells:
        raise ValueError("23,040-cell scientific inventory/order drift")
    mapping = {t + 480 * (g + 4 * k) for t in range(480) for g in range(4) for k in range(12)}
    if mapping != set(range(23040)):
        raise ValueError("full-node allocation mapping is not bijective")
    if len({walk_seed(f, s) for f in range(128) for s in STREAMS}) != 256:
        raise ValueError("walk seed collision")
    pre = manifest["preregistration"]
    if pre != {
        "protocol_id": "grid2d_one_two_target_gating_isambard_ai_v4_fullnode_20260727",
        "release_gate": "v3 canary, primary reducer, and secondary max-t integrity audits all PASS; unconditional on v3 effect sign",
        "geometry_count": 15, "amplitudes": list(AMPLITUDES), "field_count": 128,
        "walk_streams": [0, 1], "cell_count": 23040,
        "array": {"tasks": 480, "task_ids": "0-479", "concurrency": 240, "gpus_per_allocation": 4, "cells_per_allocation": 48, "cells_per_gpu": 12,
                  "cell_formula": "t + 480 * (g + 4*k)"},
        "inference_unit": "disorder field after averaging two walk streams",
        "combined_blocks": 160, "combined_bootstrap_seed": 2026072701, "combined_bootstrap_resamples": 20000,
        "claim_boundary": "finite-horizon physical-grid evidence only",
    }:
        raise ValueError("preregistration drift")
    return {"status": "PASS", "cells": 23040, "fields": 128, "allocations": 480}


def build(*, pack: Path, sidecar: Path, runner: Path, engine: Path, output: Path, v3_pack: Path | None = None) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError("v4 production manifest is append-only")
    if v3_pack is not None and sha256_file(v3_pack) == sha256_file(pack):
        raise ValueError("v4 pack collides with v3 pack hash")
    payload = {
        "schema": SCHEMA,
        "campaign": {"kind": "production", "cell_count": 23040, "domain": {"width": 64, "height": 48}},
        "defaults": {"walkers": 1_000_000, "steps": 80_000, "batch_size": 131_072, "base_hold": 0.30, "target_radius": 3, "start_x": 7, "start_y": 24, "target1_x": 54, "target1_y": 24, "checkpoints": [5000, 10000, 20000, 40000, 80000], "seed_base": WALK_SEED_BASE},
        "profiles": {"frozen_80k": {}},
        "field_pack_sha256": sha256_file(pack),
        "artifacts": {"field_pack": {"filename": pack.name, "sha256": sha256_file(pack), "sidecar_filename": sidecar.name, "sidecar_sha256": sha256_file(sidecar)}, "runner_source": {"filename": runner.name, "sha256": sha256_file(runner)}, "runner_engine": {"filename": engine.name, "sha256": sha256_file(engine)}, "container": {"reference": CONTAINER_REFERENCE, "sha256": CONTAINER_SHA256}, "result_schema": RESULT_SCHEMA},
        "preregistration": {"protocol_id": "grid2d_one_two_target_gating_isambard_ai_v4_fullnode_20260727", "release_gate": "v3 canary, primary reducer, and secondary max-t integrity audits all PASS; unconditional on v3 effect sign", "geometry_count": 15, "amplitudes": list(AMPLITUDES), "field_count": 128, "walk_streams": [0, 1], "cell_count": 23040, "array": {"tasks": 480, "task_ids": "0-479", "concurrency": 240, "gpus_per_allocation": 4, "cells_per_allocation": 48, "cells_per_gpu": 12, "cell_formula": "t + 480 * (g + 4*k)"}, "inference_unit": "disorder field after averaging two walk streams", "combined_blocks": 160, "combined_bootstrap_seed": 2026072701, "combined_bootstrap_resamples": 20000, "claim_boundary": "finite-horizon physical-grid evidence only"},
        "cells": cells(),
    }
    validate(payload, pack=pack, sidecar=sidecar, runner=runner, engine=engine)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False); handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
        os.link(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--field-pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--field-sidecar", type=Path, default=DEFAULT_SIDECAR)
    parser.add_argument("--runner", type=Path, default=Path(__file__).with_name("gpu_gating_mc_v4.py"))
    parser.add_argument("--engine", type=Path, default=Path(__file__).with_name("gpu_gating_mc_v3.py"))
    parser.add_argument("--v3-pack", type=Path, default=DATA / "disorder_field_pack_v3.npz")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build(pack=args.field_pack.absolute(), sidecar=args.field_sidecar.absolute(), runner=args.runner.absolute(), engine=args.engine.absolute(), output=args.output.absolute(), v3_pack=args.v3_pack.absolute())
    print(json.dumps({"status": "PASS", "cells": len(payload["cells"]), "sha256": sha256_file(args.output.absolute())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
