#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from report_registry import load_registry, resolve_report


ALLOWED_EXTRA_PDF_PATTERNS = (
    "note_*.pdf",
    "method_comparison*.pdf",
    "fig*_description*.pdf",
)
LEGACY_NAME_PREFIXES = (
    "2d_bimodality",
    "2d_blackboard_bimodality",
    "2d_rect_bimodality",
    "2d_reflecting_bimodality",
    "2d_two_target_double_peak",
    "deriv_k2",
    "lazy_flux",
    "lazy_jump",
    "lazy_jump_ext",
    "lazy_jump_ext_rev2",
    "luca_regime_map",
    "two_target_ring",
    "valley",
    "valley_dst",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(1024 * 1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def is_allowed_extra_pdf(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in ALLOWED_EXTRA_PDF_PATTERNS)


def is_legacy_named_pdf(name: str) -> bool:
    stem = Path(name).stem
    for pref in LEGACY_NAME_PREFIXES:
        if stem == pref or stem.startswith(pref + "_"):
            return True
    return False


def canonical_pdf_names(item: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for tex in item.get("main_tex", []):
        stem = Path(str(tex)).stem
        out.add(f"{stem}.pdf")
    return out


def discover_candidates(*, root: Path, report_token: str | None) -> list[tuple[dict[str, Any], Path]]:
    registry = load_registry()
    if report_token:
        item = resolve_report(report_token, registry)
        scope = [item]
    else:
        scope = registry

    out: list[tuple[dict[str, Any], Path]] = []
    for item in scope:
        report_dir = root / str(item["path"])
        if not report_dir.is_dir():
            continue
        canonical = canonical_pdf_names(item)
        for pdf in sorted(report_dir.glob("*.pdf")):
            name = pdf.name
            if not is_legacy_named_pdf(name):
                continue
            if name in canonical:
                continue
            if is_allowed_extra_pdf(name):
                continue
            out.append((item, pdf))
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Archive legacy-named top-level report PDFs.")
    p.add_argument("--dry-run", action="store_true", help="Show planned moves only.")
    p.add_argument("--report", default=None, help="Process only one report id/alias.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    archive_root = root / "research" / "archives" / "reports" / "_legacy_named_artifacts"
    manifest_path = archive_root / "manifest.jsonl"

    try:
        candidates = discover_candidates(root=root, report_token=args.report)
    except KeyError as exc:
        raise SystemExit(str(exc))

    if not candidates:
        print("candidates=0")
        return 0

    moved = 0
    total_bytes = 0
    entries: list[dict[str, Any]] = []
    now = utc_now()

    for item, src in candidates:
        rel_src = src.relative_to(root).as_posix()
        dst = archive_root / item["id"] / src.name
        if dst.exists():
            dst = archive_root / item["id"] / f"{src.stem}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}{src.suffix}"
        rel_dst = dst.relative_to(root).as_posix()
        size_bytes = src.stat().st_size
        checksum = sha256_file(src)

        if args.dry_run:
            print(f"DRY-RUN move {rel_src} -> {rel_dst}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print(f"moved {rel_src} -> {rel_dst}")

        moved += 1
        total_bytes += size_bytes
        entries.append(
            {
                "schema_version": 1,
                "report_id": item["id"],
                "source_path_rel": rel_src,
                "archive_path_rel": rel_dst,
                "moved_at_utc": now,
                "checksum_sha256": checksum,
                "size_bytes": size_bytes,
                "reason": "legacy_named_top_level_pdf",
            }
        )

    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with manifest_path.open("a", encoding="utf-8") as f:
            for row in entries:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"candidates={len(candidates)} moved={moved} total_bytes={total_bytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
