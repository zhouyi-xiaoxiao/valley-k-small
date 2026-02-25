from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def test_real_report_dirs_have_readme_and_notes() -> None:
    dirs = [p for p in REPORTS.iterdir() if p.is_dir() and not p.is_symlink()]
    assert dirs
    for d in dirs:
        assert (d / "README.md").exists(), f"missing README.md: {d}"
        assert (d / "notes").is_dir(), f"missing notes/: {d}"
