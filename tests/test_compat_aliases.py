from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from report_registry import load_registry


def test_no_compat_aliases_and_no_root_legacy_symlinks() -> None:
    registry = load_registry()
    for item in registry:
        canonical = ROOT / item["path"]
        assert canonical.is_dir()
        assert item.get("aliases", []) == []

    root_symlinks = [p for p in (ROOT / "reports").iterdir() if p.is_symlink()]
    assert not root_symlinks, f"legacy symlinks should be removed: {root_symlinks}"
