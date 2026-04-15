from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def test_scripts_surface_is_minimal() -> None:
    regular_files = sorted(
        p.name
        for p in SCRIPTS.iterdir()
        if p.is_file() and not p.name.startswith(".")
    )
    assert regular_files == ["README.md", "ka", "reportctl.py"]
