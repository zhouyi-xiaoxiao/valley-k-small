#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from archive_report_runs import ROOT, dir_size_bytes, sha256_dir


INDEX = ROOT / "archives" / "reports" / "index.jsonl"


def migrate_index() -> int:
    if not INDEX.exists():
        return 0
    lines = INDEX.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    changed = 0
    for line in lines:
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("schema_version") == 2:
            out.append(json.dumps(row, ensure_ascii=False))
            continue

        archive_rel = row.get("archive_path") or row.get("archive_path_rel")
        source_rel = row.get("source_path") or row.get("source_path_rel")
        moved_at = row.get("moved_at") or row.get("moved_at_utc")
        checksum = row.get("checksum") or row.get("checksum_sha256")

        archive_abs = ROOT / str(archive_rel)
        if not checksum and archive_abs.exists():
            checksum = sha256_dir(archive_abs)

        size_bytes = int(row.get("size_bytes", 0))
        if size_bytes <= 0 and archive_abs.exists():
            size_bytes = dir_size_bytes(archive_abs)

        new = {
            "schema_version": 2,
            "report_id": row.get("report_id", ""),
            "pipeline": row.get("pipeline", "unknown"),
            "experiment_key": row.get("experiment_key", ""),
            "run_id": row.get("run_id", ""),
            "source_path_rel": str(source_rel),
            "archive_path_rel": str(archive_rel),
            "moved_at_utc": str(moved_at),
            "checksum_sha256": str(checksum),
            "size_bytes": int(size_bytes),
            "is_latest_snapshot": bool(row.get("is_latest_snapshot", False)),
            "latest_pointer_rel": str(row.get("latest_pointer_rel", "")),
        }
        out.append(json.dumps(new, ensure_ascii=False))
        changed += 1

    INDEX.write_text("\n".join(out) + ("\n" if out else ""), encoding="utf-8")
    return changed


def migrate_latest_manifests() -> int:
    changed = 0
    for mf in ROOT.glob("reports/*/**/latest/manifest.json"):
        try:
            payload = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        if payload.get("schema_version") == 2:
            continue

        archive_path = payload.get("archive_runs_path") or payload.get("archive_runs_path_rel") or ""
        parts = mf.relative_to(ROOT).parts
        report_id = parts[1] if len(parts) > 1 else ""
        pipeline = parts[3] if len(parts) > 3 else "unknown"
        experiment_key = "/".join(parts[2:-2]) if len(parts) > 4 else ""

        new = {
            "schema_version": 2,
            "report_id": payload.get("report_id", report_id),
            "pipeline": payload.get("pipeline", pipeline),
            "experiment_key": payload.get("experiment_key", experiment_key),
            "archive_runs_path_rel": str(archive_path),
            "archived_run_ids": list(payload.get("archived_run_ids", [])),
            "updated_at_utc": payload.get("updated_at") or payload.get("updated_at_utc") or "",
        }
        mf.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed += 1
    return changed


def main() -> int:
    c1 = migrate_index()
    c2 = migrate_latest_manifests()
    print(f"migrated_index_rows={c1}")
    print(f"migrated_latest_manifests={c2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
