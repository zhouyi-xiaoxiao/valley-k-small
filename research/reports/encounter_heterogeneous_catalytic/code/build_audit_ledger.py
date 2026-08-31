#!/usr/bin/env python3
"""Build the machine-readable thirteen-round adversarial-audit ledger."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
AUDITS = REPORT / "audits"
OUTPUT = AUDITS / "audit_ledger.json"
EXPECTED_ROUNDS = tuple(range(1, 14))
REQUIRED_FILES = ("reviewer_a.md", "reviewer_b.md", "resolution.md")


class AuditStatus(str, Enum):
    PASS = "PASS"
    HOLD = "HOLD"
    FAIL = "FAIL"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _status(path: Path) -> tuple[AuditStatus, str]:
    source = path.read_text(encoding="utf-8")
    matches = re.findall(r"(?mi)^Status:\s*(.+?)\s*$", source)
    if len(matches) != 1:
        raise RuntimeError(
            f"resolution must have exactly one Status line: {path}: found={len(matches)}"
        )
    status_text = re.sub(r"[*`]", "", matches[0]).strip()
    match = re.fullmatch(r"(PASS|HOLD|FAIL)(?:\b(.*))?", status_text, re.IGNORECASE)
    if match is None:
        raise RuntimeError(
            f"round resolution has invalid status enum (PASS/HOLD/FAIL): "
            f"{path}: {status_text}"
        )
    status = AuditStatus(match.group(1).upper())
    detail = (match.group(2) or "").strip(" ;:-")
    return status, detail


def build_ledger() -> dict[str, object]:
    directories = sorted(AUDITS.glob("round_[0-9][0-9]_*"))
    by_number: dict[int, Path] = {}
    for directory in directories:
        match = re.match(r"round_(\d{2})_", directory.name)
        if match is None:
            continue
        number = int(match.group(1))
        if number in by_number:
            raise RuntimeError(f"duplicate audit round {number}")
        by_number[number] = directory
    if tuple(sorted(by_number)) != EXPECTED_ROUNDS:
        raise RuntimeError(
            f"audit round set mismatch: expected={EXPECTED_ROUNDS} "
            f"observed={tuple(sorted(by_number))}"
        )

    rows: list[dict[str, object]] = []
    for number in EXPECTED_ROUNDS:
        directory = by_number[number]
        missing = [name for name in REQUIRED_FILES if not (directory / name).is_file()]
        if missing:
            raise FileNotFoundError(f"round {number:02d} is missing {missing}")
        if any((directory / name).stat().st_size == 0 for name in REQUIRED_FILES):
            raise RuntimeError(f"round {number:02d} contains an empty required review file")
        reviewer_hashes = {
            _sha256(directory / "reviewer_a.md"),
            _sha256(directory / "reviewer_b.md"),
        }
        if len(reviewer_hashes) != 2:
            raise RuntimeError(
                f"round {number:02d} reviewer files are byte-identical; "
                "two independent review records are required"
            )
        files = []
        for path in sorted(directory.glob("*.md")):
            files.append(
                {
                    "path": str(path.relative_to(REPORT)),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
        status, status_detail = _status(directory / "resolution.md")
        rows.append(
            {
                "round": number,
                "directory": str(directory.relative_to(REPORT)),
                "status": status.value,
                "status_detail": status_detail,
                "required_files": list(REQUIRED_FILES),
                "files": files,
            }
        )
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    generated_at = (
        datetime.fromtimestamp(int(source_date_epoch), tz=timezone.utc)
        if source_date_epoch is not None
        else datetime.now(timezone.utc)
    )
    return {
        "schema_version": 2,
        "generated_at_utc": generated_at.isoformat(),
        "source_date_epoch": (
            int(source_date_epoch) if source_date_epoch is not None else None
        ),
        "policy": "two independent reviewers plus root resolution for each round",
        "round_count": len(rows),
        "all_rounds_pass": len(rows) == len(EXPECTED_ROUNDS)
        and all(row["status"] == AuditStatus.PASS.value for row in rows),
        "rounds": rows,
    }


def main() -> None:
    payload = build_ledger()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {OUTPUT} with {payload['round_count']} rounds; "
        f"all_rounds_pass={payload['all_rounds_pass']}"
    )


if __name__ == "__main__":
    main()
