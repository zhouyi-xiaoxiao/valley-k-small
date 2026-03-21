#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from report_registry import load_registry
from schema_utils import validate_with_schema


RUN_ID_RE = re.compile(r"^[0-9]{8}_[0-9]{6}$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def is_repo_relative(path_str: str) -> bool:
    p = Path(path_str)
    return bool(path_str) and (not p.is_absolute()) and ".." not in p.parts


def canonical_repo_rel(path_str: str) -> str:
    if path_str.startswith("research/") or path_str.startswith("platform/") or path_str.startswith("packages/"):
        return path_str
    if path_str.startswith("reports/"):
        return f"research/{path_str}"
    if path_str.startswith("docs/"):
        return f"research/{path_str}"
    if path_str.startswith("archives/"):
        return f"research/{path_str}"
    if path_str.startswith("site/"):
        return f"platform/web/{path_str.removeprefix('site/')}"
    if path_str.startswith("schemas/"):
        return f"platform/{path_str}"
    if path_str.startswith("skills/"):
        return f"platform/{path_str}"
    if path_str.startswith("src/"):
        return f"packages/vkcore/{path_str}"
    return path_str


def validate_index_entry(
    row: dict[str, Any], *, root: Path, valid_report_ids: set[str], schema: dict[str, Any]
) -> list[str]:
    errs: list[str] = []
    errs.extend([f"schema: {msg}" for msg in validate_with_schema(row, schema)])

    report_id = str(row.get("report_id", ""))
    if report_id not in valid_report_ids:
        errs.append(f"unknown report_id: {report_id}")

    run_id = str(row.get("run_id", ""))
    if run_id and not RUN_ID_RE.match(run_id):
        errs.append(f"invalid run_id: {run_id}")

    moved_at = str(row.get("moved_at_utc", ""))
    if moved_at and not UTC_RE.match(moved_at):
        errs.append(f"invalid moved_at_utc: {moved_at}")

    src_rel = str(row.get("source_path_rel", ""))
    if src_rel and not is_repo_relative(src_rel):
        errs.append(f"source_path_rel must be repo-relative: {src_rel}")

    archive_rel = str(row.get("archive_path_rel", ""))
    if archive_rel:
        if not is_repo_relative(archive_rel):
            errs.append(f"archive_path_rel must be repo-relative: {archive_rel}")
        elif not (root / canonical_repo_rel(archive_rel)).exists():
            errs.append(f"archive path does not exist: {archive_rel}")

    pointer_rel = str(row.get("latest_pointer_rel", ""))
    if pointer_rel:
        if not is_repo_relative(pointer_rel):
            errs.append(f"latest_pointer_rel must be repo-relative: {pointer_rel}")
        elif not (root / canonical_repo_rel(pointer_rel)).exists():
            errs.append(f"latest pointer missing: {pointer_rel}")
    return errs


def validate_latest_manifest(
    path: Path, *, root: Path, valid_report_ids: set[str], schema: dict[str, Any]
) -> list[str]:
    errs: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"invalid json {path}: {exc}"]

    errs.extend([f"{path}: schema: {msg}" for msg in validate_with_schema(payload, schema)])

    report_id = str(payload.get("report_id", ""))
    if report_id and report_id not in valid_report_ids:
        errs.append(f"{path}: unknown report_id: {report_id}")

    archive_runs_rel = str(payload.get("archive_runs_path_rel", ""))
    if archive_runs_rel and not is_repo_relative(archive_runs_rel):
        errs.append(f"{path}: archive_runs_path_rel must be repo-relative: {archive_runs_rel}")
    elif archive_runs_rel and not (root / canonical_repo_rel(archive_runs_rel)).exists():
        errs.append(f"{path}: archive_runs_path_rel missing: {archive_runs_rel}")

    updated_at = str(payload.get("updated_at_utc", ""))
    if updated_at and not UTC_RE.match(updated_at):
        errs.append(f"{path}: invalid updated_at_utc: {updated_at}")

    for run_id in payload.get("archived_run_ids", []):
        run_id = str(run_id)
        if not RUN_ID_RE.match(run_id):
            errs.append(f"{path}: invalid archived_run_id: {run_id}")
    return errs


def validate_archives(root: Path, *, strict: bool = False) -> list[str]:
    errs: list[str] = []
    index_schema = json.loads((root / "platform" / "schemas" / "archive_index.schema.json").read_text(encoding="utf-8"))
    latest_schema = json.loads((root / "platform" / "schemas" / "latest_manifest.schema.json").read_text(encoding="utf-8"))
    registry = load_registry()
    valid_report_ids = {item["id"] for item in registry}

    index_path = root / "research" / "archives" / "reports" / "index.jsonl"
    if not index_path.exists():
        return [f"missing archive index: {index_path}"]

    for n, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception as exc:
            errs.append(f"index line {n}: invalid json: {exc}")
            continue
        for msg in validate_index_entry(row, root=root, valid_report_ids=valid_report_ids, schema=index_schema):
            errs.append(f"index line {n}: {msg}")

    manifests: list[Path] = []
    for item in registry:
        report_root = root / item["path"]
        artifact_root = report_root / item.get("artifact_dir", "artifacts")
        manifests.extend(sorted(artifact_root.glob("**/latest/manifest.json")))
    if strict and not manifests:
        errs.append("no latest manifests found under research/reports/*/artifacts/**/latest/manifest.json")
    for mf in manifests:
        errs.extend(validate_latest_manifest(mf, root=root, valid_report_ids=valid_report_ids, schema=latest_schema))

    return errs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate research/archives/reports index + latest manifests")
    p.add_argument("--strict", action="store_true", help="Treat missing latest manifests as errors")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    errs = validate_archives(root, strict=bool(args.strict))
    if errs:
        for e in errs:
            print(f"ERROR: {e}")
        return 1
    print("OK: archive index/manifests are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
