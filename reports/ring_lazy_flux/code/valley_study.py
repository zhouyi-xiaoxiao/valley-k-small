#!/usr/bin/env python3
# wrapper-report-id: ring_lazy_flux
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from vkcore.ring.valley_study import *  # noqa: F401,F403

if __name__ == "__main__":
    from vkcore.ring.valley_study import main

    raise SystemExit(main())
