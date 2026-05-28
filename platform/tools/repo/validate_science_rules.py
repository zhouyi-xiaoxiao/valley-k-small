#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_ANCHORS: dict[str, tuple[str, ...]] = {
    "AGENTS.md": (
        "Mathematical Guardrails",
        "Do not call a curve `double_peak` unless the quantitative peak classifier",
        "Use `shoulder` or `local_bump` for weaker structures.",
        "Do not confuse mean first-passage time with the full first-passage",
        "All transition probabilities must be nonnegative.",
        "row-stochastic",
        "Absorbing states must stop the process immediately.",
        "Mass balance must hold",
        "`f_total(t) = f_target1(t) + f_target2(t)`",
        "`f_E(t) = sum_k f_k(t)`",
        "Reflecting boundary means attempted-outside-stays",
        "Do not state that the 2D encounter walker always has eight directions",
        "Do not run large scans unless the task explicitly asks for them.",
        "Do not modify unrelated reports.",
        "End-of-run reports must include changed files, commands run",
    ),
    "CLAUDE.md": (
        "Mathematical guardrails",
        "Transition probabilities must be nonnegative.",
        "Discrete-time transition matrices must be row-stochastic",
        "Absorbing targets must stop the process immediately.",
        "Mass balance must hold.",
        "`f_total(t)=f_target1(t)+f_target2(t)`",
        "`f_E(t)=sum_k f_k(t)`",
        "Do not state that the 2D encounter walker always has eight directions",
        "Do not call a curve `double_peak` unless the classifier criteria are met.",
    ),
    "research/IMPLEMENTATION_ROADMAP.md": (
        "Setup",
        "Current Report Revision",
        "1D Two-Target First Passage",
        "2D Two-Target First Passage",
        "Encounter Mean Validation",
        "Encounter Diagonal Decomposition",
        "Scans",
        "Final Report Integration",
        "/goal",
        "Acceptance criteria",
    ),
    "platform/skills/valley-k-small-continuation/references/core-checklist.md": (
        "python3 scripts/reportctl.py validate-science-rules",
    ),
    "platform/skills/valley-k-small-continuation/references/research-conventions.md": (
        "Peak taxonomy",
        "`double_peak` is reserved",
        "Full distribution vs mean",
        "Mass-balance and transition checks",
        "Scope discipline",
    ),
    "scripts/README.md": (
        "validate-science-rules",
    ),
}


@dataclass(frozen=True)
class Finding:
    file: str
    message: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _check_required_anchors(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel, anchors in REQUIRED_ANCHORS.items():
        path = root / rel
        if not path.exists():
            findings.append(Finding(rel, "missing required guardrail file"))
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for anchor in anchors:
            if anchor not in text:
                findings.append(Finding(rel, f"missing guardrail anchor: {anchor!r}"))
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that scientific guardrails are wired into agent docs and CLI checks."
    )
    parser.add_argument("--json", action="store_true", help="Output full JSON payload.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    findings = _check_required_anchors(root)
    payload: dict[str, Any] = {
        "ok": not findings,
        "errors": len(findings),
        "findings": [finding.__dict__ for finding in findings],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            print(f"ERROR: {finding.file}: {finding.message}")
    else:
        print("OK: scientific guardrails are wired into agent docs and CLI checks")

    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
