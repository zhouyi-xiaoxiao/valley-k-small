#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


# Re-exec into .venv/bin/python when invoked via a different interpreter.
# Subcommands like `doctor` shell out via sys.executable; if the user's
# `python3` resolves to a system Python without project deps (pytest, numpy,
# ...), those subcommands fail. The project's .venv is the canonical env.
_VENV_PY = Path(__file__).resolve().parents[1] / ".venv" / "bin" / "python"
if _VENV_PY.exists() and Path(sys.executable).resolve() != _VENV_PY.resolve():
    os.execv(str(_VENV_PY), [str(_VENV_PY), *sys.argv])


IMPL_PATH = (
    Path(__file__).resolve().parents[1]
    / "platform"
    / "tools"
    / "repo"
    / "reportctl.py"
)
if str(IMPL_PATH.parent) not in sys.path:
    sys.path.insert(0, str(IMPL_PATH.parent))


def _load_impl() -> object:
    spec = importlib.util.spec_from_file_location("valley_k_small_reportctl", IMPL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load reportctl implementation: {IMPL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_IMPL = _load_impl()
globals().update(
    {
        name: value
        for name, value in vars(_IMPL).items()
        if not name.startswith("__")
    }
)


if __name__ == "__main__":
    raise SystemExit(main())
