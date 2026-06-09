"""Keep the public CLI documentation in sync with reportctl's argparse reality.

Guards against the drift class found in the 2026-06-09 audit, where
scripts/README.md listed 20 of 29 subcommands and CLAUDE.md claimed 28.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPL = ROOT / "platform" / "tools" / "repo" / "reportctl.py"
SCRIPTS_README = ROOT / "scripts" / "README.md"
CLAUDE_MD = ROOT / "CLAUDE.md"

ADD_PARSER_RE = re.compile(r"add_parser\(\s*\"([a-z0-9-]+)\"")
BULLET_RE = re.compile(r"^- `([a-z0-9-]+)`$", re.M)
CLAUDE_COUNT_RE = re.compile(r"\((\d+) `reportctl\.py` subcommands")


def real_subcommands() -> set[str]:
    return set(ADD_PARSER_RE.findall(IMPL.read_text(encoding="utf-8")))


def test_impl_declares_subcommands() -> None:
    assert len(real_subcommands()) >= 20, "add_parser parsing looks broken"


def test_scripts_readme_lists_every_subcommand() -> None:
    documented = set(BULLET_RE.findall(SCRIPTS_README.read_text(encoding="utf-8")))
    real = real_subcommands()
    missing = sorted(real - documented)
    stale = sorted(documented - real)
    assert not missing, f"subcommands missing from scripts/README.md: {missing}"
    assert not stale, f"scripts/README.md documents nonexistent subcommands: {stale}"


def test_claude_md_subcommand_count_matches() -> None:
    text = CLAUDE_MD.read_text(encoding="utf-8")
    m = CLAUDE_COUNT_RE.search(text)
    assert m, "CLAUDE.md no longer states the reportctl subcommand count"
    assert int(m.group(1)) == len(real_subcommands()), (
        f"CLAUDE.md claims {m.group(1)} subcommands, "
        f"reportctl actually has {len(real_subcommands())}"
    )
