from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_TOOLS = ROOT / "platform" / "tools" / "repo"
if str(REPO_TOOLS) not in sys.path:
    sys.path.insert(0, str(REPO_TOOLS))

import pytest

from report_registry import load_registry, resolve_report


def test_registry_resolves_canonical_id() -> None:
    registry = load_registry()
    resolved = resolve_report("ring_valley_dst", registry)
    assert resolved["id"] == "ring_valley_dst"
    assert resolved["path"] == "research/reports/ring_valley_dst"
    assert resolved["manuscript_dir"] == "manuscript"
    assert resolved["artifact_dir"] == "artifacts"


def test_registry_contains_unique_ids() -> None:
    registry = load_registry()
    ids = [item["id"] for item in registry]
    assert len(ids) == len(set(ids))


def test_old_alias_no_longer_resolves() -> None:
    registry = load_registry()
    with pytest.raises(KeyError):
        resolve_report("valley_dst", registry)
