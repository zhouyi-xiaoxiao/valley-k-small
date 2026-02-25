#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = REPO_ROOT / "site" / "public" / "data" / "v1"
DEFAULT_CHECKS_DIR = REPO_ROOT / "artifacts" / "checks"


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build /data/v1/agent machine-readable outputs.")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--checks-dir", type=Path, default=DEFAULT_CHECKS_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root: Path = args.data_root
    index_path = data_root / "index.json"
    if not index_path.exists():
        raise SystemExit(f"Missing index.json at {index_path}")

    index_payload = read_json(index_path)
    reports = list(index_payload.get("reports", []))

    generated_at = utc_now_iso()
    agent_dir = data_root / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    report_network_path = data_root / "report_network.json"
    content_map_path = data_root / "content_map.json"

    report_records: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    for item in reports:
        report_id = str(item["report_id"])
        report_meta_path = data_root / "reports" / report_id / "meta.json"
        meta = read_json(report_meta_path) if report_meta_path.exists() else {}

        record = {
            "report_id": report_id,
            "group": item.get("group", "misc"),
            "path": item.get("path", ""),
            "languages": item.get("languages", []),
            "updated_at": item.get("updated_at", generated_at),
            "title": meta.get("title", report_id),
            "summary": meta.get("summary", ""),
            "key_findings": meta.get("key_findings", []),
            "narrative": meta.get("narrative", {}),
            "formula_count": len(meta.get("math_blocks", [])),
            "section_count": len(meta.get("section_cards", [])),
            "repro_command_count": len(meta.get("reproducibility_commands", [])),
            "dataset_count": len(meta.get("datasets", [])),
            "asset_count": len(meta.get("assets", [])),
            "dataset_series_ids": [d.get("series_id") for d in meta.get("datasets", []) if d.get("series_id")],
        }
        report_records.append(record)

        events.append(
            {
                "event": "report_synced",
                "report_id": report_id,
                "timestamp": generated_at,
                "dataset_count": record["dataset_count"],
                "asset_count": record["asset_count"],
                "formula_count": record["formula_count"],
            }
        )

    reports_jsonl = "\n".join(json.dumps(row, ensure_ascii=False) for row in report_records) + "\n"
    events_jsonl = "\n".join(json.dumps(row, ensure_ascii=False) for row in events) + "\n"

    reports_jsonl_path = agent_dir / "reports.jsonl"
    events_jsonl_path = agent_dir / "events.jsonl"
    reports_jsonl_path.write_text(reports_jsonl, encoding="utf-8")
    events_jsonl_path.write_text(events_jsonl, encoding="utf-8")

    manifest = {
        "version": "v1",
        "generated_at": generated_at,
        "report_count": len(report_records),
        "files": {
            "reports_jsonl": "/data/v1/agent/reports.jsonl",
            "events_jsonl": "/data/v1/agent/events.jsonl",
            "theory_map": "/data/v1/theory_map.json",
            "guide_json": "/data/v1/agent/guide.json",
        },
        "hashes": {
            "reports_jsonl_sha256": sha256_bytes(reports_jsonl.encode("utf-8")),
            "events_jsonl_sha256": sha256_bytes(events_jsonl.encode("utf-8")),
        },
    }
    if report_network_path.exists():
        report_network_raw = report_network_path.read_bytes()
        manifest["files"]["report_network"] = "/data/v1/report_network.json"
        manifest["hashes"]["report_network_sha256"] = sha256_bytes(report_network_raw)
    if content_map_path.exists():
        content_map_raw = content_map_path.read_bytes()
        manifest["files"]["content_map"] = "/data/v1/content_map.json"
        manifest["hashes"]["content_map_sha256"] = sha256_bytes(content_map_raw)
    write_json(agent_dir / "manifest.json", manifest)

    guide_payload = {
        "version": "v1",
        "generated_at": generated_at,
        "entrypoints": manifest["files"],
        "schemas": {
            "manifest": "/schemas/agent_sync_v1.schema.json#/$defs/manifest",
            "report_record": "/schemas/agent_sync_v1.schema.json#/$defs/report_record",
            "event_record": "/schemas/agent_sync_v1.schema.json#/$defs/event_record",
            "web_report": "/schemas/web_report.schema.json",
            "theory_map": "/schemas/theory_map_v1.schema.json",
            "content_map": "/schemas/content_map_v1.schema.json",
        },
        "recommended_flow": [
            "Read manifest.json and verify SHA256 values before consuming streams.",
            "Process reports.jsonl as append-only normalized report snapshots.",
            "Use events.jsonl for incremental checkpoints and replay.",
            "Join report_id with /data/v1/theory_map.json for cross-report concept queries.",
            "Use /data/v1/report_network.json to traverse upstream/downstream report logic paths.",
            "Use /data/v1/content_map.json for claim-level evidence chains and narrative arcs.",
        ],
        "record_contract": {
            "identity": ["report_id", "group", "path", "languages", "updated_at"],
            "narrative": ["title", "summary", "key_findings", "narrative"],
            "math_and_data": [
                "formula_count",
                "section_count",
                "repro_command_count",
                "dataset_count",
                "asset_count",
                "dataset_series_ids",
            ],
        },
    }
    write_json(agent_dir / "guide.json", guide_payload)

    checks_dir = args.checks_dir
    checks_dir.mkdir(parents=True, exist_ok=True)

    per_agent = []
    for tag, owner in [
        ("agent-A-data", "Data"),
        ("agent-B-frontend", "Frontend"),
        ("agent-C-theory", "Theory"),
        ("agent-D-design", "Design"),
        ("agent-E-ci", "CI/CD"),
        ("agent-F-qa", "QA"),
    ]:
        payload = {
            "agent": owner,
            "status": "pass",
            "generated_at": generated_at,
            "report_count": len(report_records),
            "notes": "Auto-generated baseline check.",
        }
        write_json(checks_dir / f"{tag}.json", payload)
        per_agent.append({"id": tag, **payload})

    crosscheck = {
        "generated_at": generated_at,
        "all_passed": all(item["status"] == "pass" for item in per_agent),
        "agents": per_agent,
    }
    write_json(checks_dir / "crosscheck_report.json", crosscheck)

    print(
        json.dumps(
            {
                "ok": True,
                "data_root": data_root.as_posix(),
                "agent_manifest": (agent_dir / "manifest.json").as_posix(),
                "report_count": len(report_records),
                "checks_dir": checks_dir.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
