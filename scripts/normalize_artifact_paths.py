#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_string(value: str, *, root: Path) -> str:
    text = value
    root_str = str(root)
    if text.startswith(root_str + "/"):
        return Path(text).resolve().relative_to(root.resolve()).as_posix()

    # Historical absolute paths from pre-rename phase.
    text = text.replace(str(root.resolve()) + "/", "")
    text = text.replace("reports/luca_regime_map/", "reports/cross_luca_regime_map/")
    text = text.replace("reports/lazy_jump_ext_rev2/", "reports/ring_lazy_jump_ext_rev2/")

    # External dataset path: keep semantic meaning without machine-specific absolute path.
    user = getpass.getuser()
    text = text.replace(
        f"/Users/{user}/Desktop/sparse_double_peak_testset.json",
        "external/sparse_double_peak_testset.json",
    )
    return text


def walk(value: Any, *, root: Path) -> Any:
    if isinstance(value, dict):
        return {k: walk(v, root=root) for k, v in value.items()}
    if isinstance(value, list):
        return [walk(v, root=root) for v in value]
    if isinstance(value, str):
        return normalize_string(value, root=root)
    return value


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Normalize absolute artifact paths inside JSON payloads")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--include-archives", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    json_files = list((root / "reports").glob("**/*.json"))
    if args.include_archives:
        json_files += list((root / "archives").glob("**/*.json"))

    changed = 0
    for path in sorted(json_files):
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        new = walk(old, root=root)
        if new != old:
            changed += 1
            if not args.dry_run:
                path.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"normalized_json_files={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
