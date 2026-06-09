from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "research" / "reports"
REPO_TOOLS = ROOT / "platform" / "tools" / "repo"
if str(REPO_TOOLS) not in sys.path:
    sys.path.insert(0, str(REPO_TOOLS))

from report_registry import load_registry  # noqa: E402

ALLOWED_ROOT_FILES = {
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
}
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


# Gitignored runtime dirs may be diverted out of OneDrive (od-divert) and live
# behind a symlink into ~/.local-build/. Only these names are allowed; layout
# symlinks for tracked content remain banned.
ALLOWED_RUNTIME_SYMLINKS = {".venv", ".local"}


def test_root_has_no_legacy_symlinks() -> None:
    legacy = [
        p.name
        for p in ROOT.iterdir()
        if p.is_symlink() and p.name not in ALLOWED_RUNTIME_SYMLINKS
    ]
    assert legacy == [], f"legacy root symlinks should be removed: {legacy}"


def test_registered_report_dirs_follow_v2_layout() -> None:
    dirs = [ROOT / item["path"] for item in load_registry()]
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
