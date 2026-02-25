#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from report_registry import load_registry, resolve_report


RUN_ID_RE = re.compile(r"^\d{8}_\d{6}$")


@dataclass
class MoveEntry:
    schema_version: int
    report_id: str
    pipeline: str
    experiment_key: str
    run_id: str
    source_path_rel: str
    archive_path_rel: str
    moved_at_utc: str
    checksum_sha256: str
    size_bytes: int
    is_latest_snapshot: bool
    latest_pointer_rel: str


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
ARCHIVE_ROOT = ROOT / "archives" / "reports"
INDEX_PATH = ARCHIVE_ROOT / "index.jsonl"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Archive timestamp runs into archives/reports")
    p.add_argument("--dry-run", action="store_true", help="Show what would be moved without changing files")
    p.add_argument("--report", default=None, help="Only process one report id/alias")
    p.add_argument("--verify", action="store_true", help="Only verify archive metadata, do not move")
    return p.parse_args()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sha256_dir(path: Path) -> str:
    h = hashlib.sha256()
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = file_path.relative_to(path).as_posix().encode("utf-8")
        h.update(rel)
        h.update(b"\0")
        h.update(sha256_file(file_path).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def dir_size_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def discover_run_dirs(report_filter: str | None = None) -> list[Path]:
    out: list[Path] = []
    allowed_report_dir: str | None = None
    if report_filter:
        item = resolve_report(report_filter, load_registry())
        allowed_report_dir = Path(item["path"]).name

    for p in REPORTS.rglob("*"):
        if not p.is_dir() or p.is_symlink():
            continue
        if p.parent.name != "runs" or not RUN_ID_RE.match(p.name):
            continue
        report_dir = p.relative_to(REPORTS).parts[0]
        if allowed_report_dir and report_dir != allowed_report_dir:
            continue
        out.append(p)
    return sorted(out)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def write_latest_manifest(*, latest_dir: Path, report_id: str, pipeline: str, experiment_key: str, archive_runs_rel: str, run_ids: list[str]) -> str:
    payload = {
        "schema_version": 2,
        "report_id": report_id,
        "pipeline": pipeline,
        "experiment_key": experiment_key,
        "archive_runs_path_rel": archive_runs_rel,
        "archived_run_ids": sorted(run_ids),
        "updated_at_utc": utc_now_iso(),
    }
    latest_path = latest_dir / "manifest.json"
    latest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return latest_path.relative_to(ROOT).as_posix()


def verify_only() -> int:
    from validate_archives import validate_archives

    errors = validate_archives(ROOT)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("OK: archive index/manifests are valid")
    return 0


def main() -> int:
    args = parse_args()

    if args.verify:
        return verify_only()

    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    entries: list[MoveEntry] = []
    experiment_runs: dict[str, list[str]] = {}

    run_dirs = discover_run_dirs(report_filter=args.report)
    for src in run_dirs:
        src_rel = src.relative_to(ROOT)
        dst = ARCHIVE_ROOT / src_rel.relative_to("reports")
        dst.parent.mkdir(parents=True, exist_ok=True)

        if args.dry_run:
            print(f"DRY-RUN move {src_rel.as_posix()} -> {dst.relative_to(ROOT).as_posix()}")
            continue

        shutil.move(str(src), str(dst))

        parts = src_rel.parts
        report_id = parts[1]
        pipeline = parts[3] if len(parts) > 3 else (parts[2] if len(parts) > 2 else "unknown")
        experiment_key = "/".join(parts[2:-2]) if len(parts) > 4 else ""
        run_id = parts[-1]

        archive_runs_rel = str(dst.parent.relative_to(ROOT))
        key = archive_runs_rel
        experiment_runs.setdefault(key, []).append(run_id)

        latest_pointer_rel = ""
        latest_dir = src.parent.parent / "latest"
        if latest_dir.exists() and latest_dir.is_dir():
            latest_pointer_rel = write_latest_manifest(
                latest_dir=latest_dir,
                report_id=report_id,
                pipeline=pipeline,
                experiment_key=experiment_key,
                archive_runs_rel=archive_runs_rel,
                run_ids=experiment_runs[key],
            )

        entry = MoveEntry(
            schema_version=2,
            report_id=report_id,
            pipeline=pipeline,
            experiment_key=experiment_key,
            run_id=run_id,
            source_path_rel=src_rel.as_posix(),
            archive_path_rel=dst.relative_to(ROOT).as_posix(),
            moved_at_utc=utc_now_iso(),
            checksum_sha256=sha256_dir(dst),
            size_bytes=dir_size_bytes(dst),
            is_latest_snapshot=False,
            latest_pointer_rel=latest_pointer_rel,
        )
        entries.append(entry)

        runs_dir = src.parent
        if runs_dir.exists() and runs_dir.is_dir() and not any(runs_dir.iterdir()):
            runs_dir.rmdir()

    if args.dry_run:
        print(f"dry_run_candidates={len(run_dirs)}")
        return 0

    if entries:
        with INDEX_PATH.open("a", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e.__dict__, ensure_ascii=False) + "\n")

    for archive_runs_rel, run_ids in sorted(experiment_runs.items()):
        archive_runs_dir = ROOT / archive_runs_rel
        manifest = {
            "schema_version": 2,
            "archive_runs_path_rel": archive_runs_rel,
            "run_ids": sorted(run_ids),
            "count": len(run_ids),
            "updated_at_utc": utc_now_iso(),
        }
        (archive_runs_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"archived_runs={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
