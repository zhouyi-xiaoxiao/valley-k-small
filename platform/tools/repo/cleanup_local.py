#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


DEFAULT_FILE_NAMES = {".DS_Store"}
DEFAULT_DIR_NAMES = {"__pycache__", ".pycache", ".mplcache", "build", ".pytest_cache"}
VENV_DIRS = {".venv", "venv"}
DEFAULT_FILE_SUFFIXES = {".pyc", ".pyo"}
RUNTIME_RELATIVE_DIRS = {
    Path(".openclaw"),
    Path(".local/loop"),
    Path(".local/keepalive"),
    Path(".local/checks/content_iteration"),
    Path(".local/deliverables"),
}
RUNTIME_RELATIVE_FILES = {
    Path(".local/checks/openclaw_review_history.jsonl"),
    Path(".local/checks/openclaw_review.json"),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove common local artifacts (safe cleanup)."
    )
    parser.add_argument(
        "--include-venv",
        action="store_true",
        help="Also remove .venv/ and venv/ directories.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be removed without deleting.",
    )
    parser.add_argument(
        "--include-runtime",
        action="store_true",
        help="Also remove hidden runtime artifacts under .local/ and .openclaw/.",
    )
    return parser.parse_args()


def should_remove_file(name: str) -> bool:
    return name in DEFAULT_FILE_NAMES or any(
        name.endswith(suffix) for suffix in DEFAULT_FILE_SUFFIXES
    )


def collect_paths(
    root: Path, include_venv: bool, include_runtime: bool
) -> tuple[list[Path], list[Path]]:
    files: list[Path] = []
    dirs: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        current = Path(dirpath)
        if not include_venv:
            dirnames[:] = [d for d in dirnames if d not in VENV_DIRS]
        for dirname in list(dirnames):
            if dirname in DEFAULT_DIR_NAMES:
                dirs.append(current / dirname)
                dirnames.remove(dirname)
            elif include_venv and dirname in VENV_DIRS and current == root:
                dirs.append(current / dirname)
                dirnames.remove(dirname)
        for filename in filenames:
            if should_remove_file(filename):
                files.append(current / filename)

    if include_runtime:
        for rel_path in RUNTIME_RELATIVE_DIRS:
            abs_path = root / rel_path
            if abs_path.exists() and abs_path.is_dir():
                dirs.append(abs_path)
        for rel_path in RUNTIME_RELATIVE_FILES:
            abs_path = root / rel_path
            if abs_path.exists() and abs_path.is_file():
                files.append(abs_path)

    return files, dirs


def remove_paths(files: list[Path], dirs: list[Path], dry_run: bool) -> None:
    for path in sorted(files):
        if dry_run:
            print(f"[dry-run] remove file: {path}")
        else:
            path.unlink(missing_ok=True)
    for path in sorted(dirs, reverse=True):
        if dry_run:
            print(f"[dry-run] remove dir: {path}")
        else:
            shutil.rmtree(path, ignore_errors=True)


def main() -> int:
    args = parse_args()
    root = repo_root()
    files, dirs = collect_paths(root, args.include_venv, args.include_runtime)
    remove_paths(files, dirs, args.dry_run)
    if not args.dry_run:
        print(f"Removed {len(files)} files and {len(dirs)} directories.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
