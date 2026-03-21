from __future__ import annotations

import fnmatch
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_TOOLS = ROOT / "platform" / "tools" / "repo"
if str(REPO_TOOLS) not in sys.path:
    sys.path.insert(0, str(REPO_TOOLS))

from report_registry import load_registry


ALLOWED_EXTRA_PDF_PATTERNS = (
    "note_*.pdf",
    "fig*_description*.pdf",
    "*_smoke.pdf",
)


def is_allowed_extra(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in ALLOWED_EXTRA_PDF_PATTERNS)


def test_only_canonical_or_whitelisted_top_level_pdfs() -> None:
    for item in load_registry():
        report_dir = ROOT / item["path"]
        assert report_dir.is_dir(), f"missing report dir: {report_dir}"
        manuscript_dir = report_dir / item.get("manuscript_dir", "manuscript")
        extras_dir = manuscript_dir / "extras"
        canonical = {f"{Path(tex).stem}.pdf" for tex in item.get("main_tex", [])}
        assert not list(report_dir.glob("*.pdf")), f"unexpected top-level pdf in {report_dir}"
        for pdf in sorted(manuscript_dir.glob("*.pdf")):
            assert pdf.name in canonical, f"unexpected manuscript pdf in {report_dir}: {pdf.name}"
        for pdf in sorted(extras_dir.glob("*.pdf")):
            assert is_allowed_extra(pdf.name), f"unexpected extra pdf in {report_dir}: {pdf.name}"
