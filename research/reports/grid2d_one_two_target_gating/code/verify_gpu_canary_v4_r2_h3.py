#!/usr/bin/env python3
"""Verify H3 four-GPU canary against raw-primary-authorized v3 H3."""
from __future__ import annotations
import argparse
import json
import os
import tempfile
from pathlib import Path
import scientific_tail_replay_v4_r2_h2 as science


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lanes", type=Path, required=True)
    parser.add_argument("--release-receipt", type=Path, required=True)
    parser.add_argument("--release-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    science.req(science.sha(args.release_receipt) == args.release_sha256,
                "H3 release receipt hash drift")
    release = science.strict_json(args.release_receipt, mode600=True)
    science.req(release.get("schema") ==
                "grid2d-one-two-target-gating-v3-release-for-v4-r2-h3"
                and release.get("status") ==
                    "PASS_AUTHORIZE_V4_R2_H3_HARDWARE_CANARY"
                and release.get("authorizes_v4_r2_h3") is True,
                "H3 release did not authorize GPU canary")
    expected = {f"lane-{lane}.json" for lane in range(4)}
    science.req({item.name for item in args.lanes.iterdir()} == expected,
                "H3 lane exact inventory drift")
    rows = []
    for lane in range(4):
        path = args.lanes / f"lane-{lane}.json"
        value = science.strict_json(path, mode600=True)
        science.req(value.get("schema") ==
                    "grid2d-one-two-target-gating-v4-r2-gpu-lane-v1"
                    and value.get("lane") == lane,
                    "H3 lane schema/index drift"); rows.append(value)
    science.req(len({row["gpu"]["uuid"] for row in rows}) == 4
                and len({row["gpu"]["pci_bus_id"] for row in rows}) == 4
                and len({row["cuda_visible_devices"] for row in rows}) == 4,
                "H3 canary did not prove four distinct GPUs")
    payload = {
        "schema": "grid2d-one-two-target-gating-v4-r2-gpu-canary-v1",
        "status": "PASS_AUTHORIZE_V4_R2_PRODUCTION",
        "release_receipt_sha256": args.release_sha256,
        "lanes": [{"lane": row["lane"],
                   "cuda_visible_devices": row["cuda_visible_devices"],
                   "uuid": row["gpu"]["uuid"],
                   "pci_bus_id": row["gpu"]["pci_bus_id"],
                   "capture_sha256": science.sha(args.lanes / f"lane-{row['lane']}.json")}
                  for row in rows],
        "distinct_uuid_count": 4, "distinct_pci_count": 4,
        "distinct_cuda_visible_devices_count": 4}
    science.req(not args.output.exists(), "H3 canary receipt exists")
    raw = (json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    descriptor, name = tempfile.mkstemp(prefix=".canary-h3.", dir=args.output.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600); os.link(temporary, args.output)
    finally: temporary.unlink(missing_ok=True)
    print(json.dumps({"status": payload["status"], "sha256": science.sha(args.output)},
                     sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
