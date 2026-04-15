from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_TOOLS = ROOT / "platform" / "tools" / "repo"
if str(REPO_TOOLS) not in sys.path:
    sys.path.insert(0, str(REPO_TOOLS))

from validate_archives import validate_archives


def test_archive_index_and_manifests_validate() -> None:
    errors = validate_archives(ROOT, strict=True)
    assert not errors, "\\n".join(errors)
