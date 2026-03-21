#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


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
