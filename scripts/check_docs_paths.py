#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REL_PATH_RE = re.compile(r"`((?:reports|docs|scripts|src|archives)/[^`\n]+)`")
ABS_PATH_RE = re.compile(r"/Users/[A-Za-z0-9._-]+/")

DEFAULT_FILES = (
    "README.md",
    "reports/README.md",
    "docs/README.md",
    "docs/RESEARCH_SUMMARY.md",
    "scripts/README.md",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _is_placeholder(token: str) -> bool:
    return any(sym in token for sym in ("<", ">", "{", "}", "*"))


def _normalize_token(token: str) -> str:
    token = token.strip()
    token = token.rstrip(".,;:)")
    return token


def _scan_file(path: Path, *, root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = path.relative_to(root).as_posix()
    broken_paths: list[str] = []
    absolute_paths: list[str] = []

    for match in REL_PATH_RE.finditer(text):
        token = _normalize_token(match.group(1))
        if _is_placeholder(token):
            continue
        target = root / token
        if not target.exists():
            broken_paths.append(token)

    if not rel.startswith("docs/research_log/"):
        for match in ABS_PATH_RE.finditer(text):
            absolute_paths.append(match.group(0))

    return {
        "file": rel,
        "broken_paths": sorted(set(broken_paths)),
        "absolute_path_tokens": sorted(set(absolute_paths)),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check active docs for broken repo-relative paths and absolute paths.")
    p.add_argument("--json", action="store_true", help="Output full JSON payload.")
    p.add_argument(
        "--files",
        nargs="*",
        default=list(DEFAULT_FILES),
        help="Files to scan (repo-relative).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()

    findings: list[dict[str, Any]] = []
    errors = 0
    for rel in args.files:
        path = root / rel
        if not path.exists():
            findings.append({"file": rel, "error": "missing"})
            errors += 1
            continue
        row = _scan_file(path, root=root)
        findings.append(row)
        errors += len(row["broken_paths"])
        errors += len(row["absolute_path_tokens"])

    payload = {"ok": errors == 0, "errors": errors, "files": findings}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for row in findings:
            if "error" in row:
                print(f"ERROR: {row['file']}: {row['error']}")
                continue
            for p in row["broken_paths"]:
                print(f"ERROR: {row['file']}: broken path `{p}`")
            for p in row["absolute_path_tokens"]:
                print(f"ERROR: {row['file']}: absolute path token `{p}`")
        if errors == 0:
            print("OK: documentation paths are valid")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
