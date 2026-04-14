#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path


TARGET = (
    Path(__file__).resolve().parents[1]
    / "platform"
    / "tools"
    / "web"
    / "validate_web_data.py"
)


if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
