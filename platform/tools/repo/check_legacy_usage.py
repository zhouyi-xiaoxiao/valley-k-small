#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


OLD_NAMES = [
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
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def scan_text(path: Path, patterns: list[re.Pattern[str]]) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    out: dict[str, int] = {}
    for p in patterns:
        out[p.pattern] = len(p.findall(text))
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Count legacy-name usage in repo text files")
    p.add_argument("--json", action="store_true", help="Output JSON")
    args = p.parse_args()

    root = repo_root()
    patterns = [re.compile(rf"\b{name}\b") for name in OLD_NAMES]
    patterns.append(re.compile(r"/Users/"))

    files = [
        fp
        for fp in root.glob("**/*")
        if fp.is_file() and fp.suffix.lower() in {".py", ".md", ".tex", ".json", ".yaml", ".yml"}
    ]

    totals = {pat.pattern: 0 for pat in patterns}
    by_file: dict[str, dict[str, int]] = {}

    for fp in files:
        rel = fp.relative_to(root).as_posix()
        if rel.startswith(".git/"):
            continue
        stats = scan_text(fp, patterns)
        nonzero = {k: v for k, v in stats.items() if v > 0}
        if nonzero:
            by_file[rel] = nonzero
            for k, v in nonzero.items():
                totals[k] += v

    payload = {
        "compatibility_layer": "removed",
        "removed_on": "2026-02-16",
        "totals": totals,
        "files_with_legacy_refs": by_file,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("compatibility_layer: removed")
        print("removed_on: 2026-02-16")
        print("totals:")
        for k, v in sorted(totals.items()):
            print(f"  {k}: {v}")
        print(f"files_with_legacy_refs: {len(by_file)}")

    out = root / "docs" / "research_log" / "legacy_usage_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
