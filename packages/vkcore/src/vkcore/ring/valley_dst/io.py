from __future__ import annotations

from pathlib import Path

from .common import copy_latest


def copy_run_outputs_to_latest(run_files: list[Path], latest_dir: Path) -> None:
    latest_dir.mkdir(parents=True, exist_ok=True)
    for src in run_files:
        copy_latest(src, latest_dir / src.name)
