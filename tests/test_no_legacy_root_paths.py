from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "research" / "docs" / "README.md",
    ROOT / "research" / "reports" / "README.md",
    ROOT / "platform" / "README.md",
    ROOT / "scripts" / "README.md",
]

FORBIDDEN_TOKENS = (
    "`reports/",
    "`docs/",
    "`archives/",
    "`site/",
    "`schemas/",
    "`skills/",
    "`src/",
)


def test_active_docs_do_not_reference_legacy_root_aliases() -> None:
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_TOKENS:
            assert token not in text, f"{path} still references legacy root alias {token}"


def test_repo_tooling_does_not_keep_legacy_migration_scripts() -> None:
    legacy_tool_files = [
        ROOT / "platform" / "tools" / "repo" / "check_legacy_usage.py",
        ROOT / "platform" / "tools" / "repo" / "migrate_archive_metadata_v2.py",
        ROOT / "platform" / "tools" / "repo" / "migrate_report_names.py",
        ROOT / "platform" / "tools" / "repo" / "normalize_artifact_paths.py",
    ]
    for path in legacy_tool_files:
        assert not path.exists(), f"legacy migration tool should be removed: {path}"
