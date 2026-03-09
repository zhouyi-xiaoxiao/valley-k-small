#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

REPORT_ROOT = Path(__file__).resolve().parents[1]
# Shared implementation wrapper for ring_lazy_jump_ext.
from vkcore.ring.jump_reports import main_plot_scan_summaries

if __name__ == "__main__":
    raise SystemExit(main_plot_scan_summaries(report_root=REPORT_ROOT))
