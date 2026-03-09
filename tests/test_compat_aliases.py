from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_TOOLS = ROOT / "platform" / "tools" / "repo"
if str(REPO_TOOLS) not in sys.path:
    sys.path.insert(0, str(REPO_TOOLS))

from report_registry import load_registry


def test_registry_has_no_compat_aliases() -> None:
    registry = load_registry()
    for item in registry:
        assert item.get("aliases", []) == []


def test_root_legacy_alias_targets_do_not_exist() -> None:
    for name in ("reports", "docs", "archives", "site", "schemas", "skills", "src", "artifacts"):
        assert not (ROOT / name).exists(), f"legacy root path still exists: {name}"
