#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

# Report-specific wrapper for grid2d_rect_bimodality.
os.environ.setdefault("VK_REPORT_DIR", str(Path(__file__).resolve().parents[1]))

from vkcore.grid2d.rect_bimodality.cli import *  # noqa: F401,F403

if __name__ == "__main__":
    from vkcore.grid2d.rect_bimodality.cli import main

    raise SystemExit(main())
