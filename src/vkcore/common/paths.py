from __future__ import annotations

from pathlib import Path
from typing import Iterable


def repo_root(start: Path | None = None) -> Path:
    """Resolve repository root by searching for `reports/` and `scripts/`."""
    cur = (start or Path(__file__)).resolve()
    if cur.is_file():
        cur = cur.parent
    for candidate in [cur, *cur.parents]:
        if (candidate / "reports").exists() and (candidate / "scripts").exists():
            return candidate
    raise RuntimeError("Cannot resolve repository root")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def rel_to_repo(path: Path, root: Path | None = None) -> str:
    rr = root or repo_root(path)
    return path.resolve().relative_to(rr.resolve()).as_posix()


def ensure_dirs(paths: Iterable[Path]) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)
