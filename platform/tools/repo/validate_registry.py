#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from report_registry import load_registry_payload, registry_path
from schema_utils import validate_with_schema


ID_RE = re.compile(r"^[a-z0-9_]+$")
PATH_RE = re.compile(r"^(?!/)(?!\.\./).+")
TEX_RE = re.compile(r"^[a-zA-Z0-9_.\-\/]+\.tex$")
PY_RE = re.compile(r"^[a-zA-Z0-9_.\-\/]+\.py$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_yaml_payload(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        return load_registry_payload(path)

    raw = path.read_text(encoding="utf-8")
    parsed = yaml.safe_load(raw)
    if not isinstance(parsed, dict):
        raise ValueError("registry yaml root must be an object")
    return parsed


def validate_payload(payload: dict[str, Any], *, root: Path) -> list[str]:
    errors: list[str] = []
    reports = payload.get("reports", [])
    if not isinstance(reports, list):
        return ["reports must be a list"]

    ids: set[str] = set()
    seen_paths: set[str] = set()
    aliases: set[str] = set()

    for idx, item in enumerate(reports):
        if not isinstance(item, dict):
            errors.append(f"reports[{idx}] must be an object")
            continue
        where = f"reports[{idx}]"

        rid = str(item.get("id", ""))
        rpath = str(item.get("path", ""))
        manuscript_dir = str(item.get("manuscript_dir", ""))
        artifact_dir = str(item.get("artifact_dir", ""))
        if not ID_RE.match(rid):
            errors.append(f"{where}.id invalid: {rid!r}")
        if rid in ids:
            errors.append(f"{where}.id duplicated: {rid}")
        ids.add(rid)

        if not PATH_RE.match(rpath):
            errors.append(f"{where}.path must be repo-relative: {rpath!r}")
            continue
        if not rpath.startswith("research/reports/"):
            errors.append(f"{where}.path must start with research/reports/: {rpath!r}")
        if rpath in seen_paths:
            errors.append(f"{where}.path duplicated: {rpath}")
        seen_paths.add(rpath)
        if Path(rpath).name != rid:
            errors.append(f"{where}.path basename should match id ({rid}): {rpath}")

        report_dir = (root / rpath).resolve()
        if not report_dir.exists() or not report_dir.is_dir():
            errors.append(f"{where}.path does not exist: {rpath}")

        if manuscript_dir != "manuscript":
            errors.append(f"{where}.manuscript_dir must be 'manuscript': {manuscript_dir!r}")
        if artifact_dir != "artifacts":
            errors.append(f"{where}.artifact_dir must be 'artifacts': {artifact_dir!r}")
        manuscript_root = report_dir / manuscript_dir if report_dir.exists() else report_dir

        for tex in item.get("main_tex", []):
            tex = str(tex)
            if not TEX_RE.match(tex):
                errors.append(f"{where}.main_tex has invalid name: {tex}")
                continue
            if report_dir.exists() and not (manuscript_root / tex).is_file():
                errors.append(f"{where}.main_tex file missing: {rpath}/{manuscript_dir}/{tex}")

        for entry in item.get("entry_scripts", []):
            entry = str(entry)
            if not PY_RE.match(entry):
                errors.append(f"{where}.entry_scripts has invalid name: {entry}")
                continue
            if report_dir.exists() and not (report_dir / entry).is_file():
                errors.append(f"{where}.entry_scripts file missing: {rpath}/{entry}")

        for alias in item.get("aliases", []):
            alias = str(alias)
            if not ID_RE.match(alias):
                errors.append(f"{where}.aliases invalid: {alias!r}")
            if alias in ids or alias in aliases:
                errors.append(f"{where}.aliases collision: {alias!r}")
            aliases.add(alias)

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate research/reports/report_registry.yaml")
    p.add_argument("--json", action="store_true", help="Print parsed payload as JSON")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    schema_path = root / "platform" / "schemas" / "report_registry.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    payload = _load_yaml_payload(registry_path())

    errors = [f"schema: {msg}" for msg in validate_with_schema(payload, schema)]
    errors.extend(validate_payload(payload, root=root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("OK: report registry is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
