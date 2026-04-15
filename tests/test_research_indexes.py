from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_research_docs_index_only_surfaces_active_material() -> None:
    text = (ROOT / "research" / "docs" / "README.md").read_text(encoding="utf-8")
    assert "research/archives/meta/agent_reports/" in text
    assert "research/docs/agentreport.md" not in text
    assert "AGENT_REPORT_2025-12-14.md" not in text


def test_research_reports_index_describes_canonical_layout_only() -> None:
    text = (ROOT / "research" / "reports" / "README.md").read_text(encoding="utf-8")
    assert "research/reports/<report_id>/" in text
    assert "compatibility symlink" not in text.lower()
    assert "loose `*.tex` or `*.pdf`" in text
