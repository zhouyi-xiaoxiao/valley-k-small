from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "research" / "reports"

ALLOWED_ROOT_FILES = {"README.md", "AGENTS.md", "pyproject.toml", "requirements.txt"}
ALLOWED_ROOT_DIRS = {"research", "platform", "packages", "scripts", "tests"}
ALLOWED_REPORT_DIRS = {"code", "notes", "manuscript", "artifacts"}


def test_root_regular_layout_is_curated() -> None:
    regular_files = {p.name for p in ROOT.iterdir() if p.is_file() and not p.name.startswith(".")}
    regular_dirs = {
        p.name
        for p in ROOT.iterdir()
        if p.is_dir() and not p.is_symlink() and not p.name.startswith(".")
    }
    assert regular_files == ALLOWED_ROOT_FILES
    assert regular_dirs == ALLOWED_ROOT_DIRS


def test_real_report_dirs_follow_v2_layout() -> None:
    dirs = [p for p in REPORTS.iterdir() if p.is_dir() and not p.is_symlink()]
    assert dirs
    for d in dirs:
        assert (d / "README.md").exists(), f"missing README.md: {d}"
        assert (d / "code").is_dir(), f"missing code/: {d}"
        assert (d / "notes").is_dir(), f"missing notes/: {d}"
        assert (d / "manuscript").is_dir(), f"missing manuscript/: {d}"
        assert (d / "artifacts").is_dir(), f"missing artifacts/: {d}"
        top_level_regular_dirs = {
            p.name for p in d.iterdir() if p.is_dir() and not p.is_symlink()
        }
        top_level_regular_files = {
            p.name for p in d.iterdir() if p.is_file()
        }
        assert top_level_regular_dirs == ALLOWED_REPORT_DIRS, f"unexpected dirs in {d}: {top_level_regular_dirs}"
        assert top_level_regular_files == {"README.md"}, f"unexpected files in {d}: {top_level_regular_files}"


def test_report_roots_do_not_keep_top_level_tex_or_pdf() -> None:
    for d in REPORTS.iterdir():
        if not d.is_dir() or d.is_symlink():
            continue
        assert not list(d.glob("*.tex")), f"top-level tex files still present in {d}"
        assert not list(d.glob("*.pdf")), f"top-level pdf files still present in {d}"
