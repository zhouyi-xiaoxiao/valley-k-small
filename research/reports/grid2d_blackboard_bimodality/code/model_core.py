#!/usr/bin/env python3
# wrapper-report-id: grid2d_blackboard_bimodality
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from vkcore.grid2d.model_core_reflecting import *  # noqa: F401,F403
