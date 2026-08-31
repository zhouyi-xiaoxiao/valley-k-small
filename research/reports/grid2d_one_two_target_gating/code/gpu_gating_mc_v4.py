#!/usr/bin/env python3
"""Frozen v4 runner facade over the independently hash-pinned v3 engine."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import gpu_gating_mc_v3 as _engine

MANIFEST_SCHEMA = "grid2d-one-two-target-gating-gpu-v4-manifest"
RESULT_SCHEMA = "grid2d-one-two-target-gating-fixed-mean-gpu-v4"


def main(argv: Sequence[str] | None = None) -> int:
    # Scientific dynamics are unchanged by the preregistration.  Pin this
    # facade and the v3 engine separately in the v4 payload inventory.
    _engine.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    _engine.RESULT_SCHEMA = RESULT_SCHEMA
    _engine.__file__ = str(Path(__file__).resolve())
    return _engine.main(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
