from __future__ import annotations

import fnmatch
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from report_registry import load_registry


ALLOWED_EXTRA_PDF_PATTERNS = (
    "note_*.pdf",
    "method_comparison*.pdf",
    "fig*_description*.pdf",
)


def is_allowed_extra(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in ALLOWED_EXTRA_PDF_PATTERNS)


def test_only_canonical_or_whitelisted_top_level_pdfs() -> None:
    for item in load_registry():
        report_dir = ROOT / item["path"]
        assert report_dir.is_dir(), f"missing report dir: {report_dir}"
        canonical = {f"{Path(tex).stem}.pdf" for tex in item.get("main_tex", [])}
        for pdf in sorted(report_dir.glob("*.pdf")):
            assert pdf.name in canonical or is_allowed_extra(pdf.name), (
                f"unexpected top-level pdf in {report_dir}: {pdf.name}"
            )
