#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
GIT_GENERATED_PREFIXES = (
    "research/archives/",
    ".local/",
    "platform/web/public/data/",
    "platform/web/public/artifacts/",
)
REPORT_GENERATED_SEGMENTS = (
    "/data/",
    "/figures/",
    "/outputs/",
    "/tables/",
    "/build/",
)


@dataclass(frozen=True)
class StatusRow:
    raw: str
    x: str
    y: str
    path: str
    is_untracked: bool
    is_generated: bool
    top_level: str


def _extract_path(raw_line: str) -> str:
    body = raw_line[3:]
    if " -> " in body:
        return body.split(" -> ", 1)[1]
    return body


def is_generated_path(path: str) -> bool:
    if path.startswith(GIT_GENERATED_PREFIXES):
        return True
    if path.startswith("research/reports/"):
        return any(seg in path for seg in REPORT_GENERATED_SEGMENTS)
    return False


def parse_status() -> list[StatusRow]:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "").strip() or "git status failed")

    rows: list[StatusRow] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        x = line[0]
        y = line[1]
        path = _extract_path(line)
        rows.append(
            StatusRow(
                raw=line,
                x=x,
                y=y,
                path=path,
                is_untracked=(x == "?" and y == "?"),
                is_generated=is_generated_path(path),
                top_level=path.split("/", 1)[0] if "/" in path else path,
            )
        )
    return rows


def cmd_summary(rows: list[StatusRow], as_json: bool) -> int:
    top_counts: Counter[str] = Counter(row.top_level for row in rows)
    source_rows = [r for r in rows if not r.is_generated]
    generated_rows = [r for r in rows if r.is_generated]
    payload = {
        "total": len(rows),
        "source": len(source_rows),
        "generated": len(generated_rows),
        "untracked": sum(1 for r in rows if r.is_untracked),
        "source_untracked": sum(1 for r in source_rows if r.is_untracked),
        "generated_untracked": sum(1 for r in generated_rows if r.is_untracked),
        "top_levels": dict(top_counts.most_common(20)),
    }
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"total: {payload['total']}")
    print(f"source: {payload['source']}")
    print(f"generated: {payload['generated']}")
    print(f"untracked: {payload['untracked']}")
    print(f"source_untracked: {payload['source_untracked']}")
    print(f"generated_untracked: {payload['generated_untracked']}")
    print("top-level counts:")
    for key, value in top_counts.most_common(20):
        print(f"  {key:20s} {value}")
    return 0


def cmd_focus(rows: list[StatusRow], limit: int, as_json: bool) -> int:
    focused = [r for r in rows if not r.is_generated]
    clipped = focused[: max(1, int(limit))]
    if as_json:
        print(
            json.dumps(
                {
                    "total_focus": len(focused),
                    "shown": len(clipped),
                    "rows": [{"status": f"{r.x}{r.y}", "path": r.path} for r in clipped],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(f"focus_total: {len(focused)} (showing {len(clipped)})")
    for row in clipped:
        print(row.raw)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize dirty worktree and show source-focused status."
    )
    sub = parser.add_subparsers(dest="subcmd", required=True)

    p_summary = sub.add_parser("summary", help="Show worktree summary")
    p_summary.add_argument("--json", action="store_true")

    p_focus = sub.add_parser("focus", help="Show status excluding generated paths")
    p_focus.add_argument("--limit", type=int, default=200)
    p_focus.add_argument("--json", action="store_true")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        rows = parse_status()
        if args.subcmd == "summary":
            return cmd_summary(rows, bool(args.json))
        if args.subcmd == "focus":
            return cmd_focus(rows, int(args.limit), bool(args.json))
        raise RuntimeError(f"unsupported subcommand: {args.subcmd}")
    except Exception as exc:
        print(f"[worktree-hygiene] error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
