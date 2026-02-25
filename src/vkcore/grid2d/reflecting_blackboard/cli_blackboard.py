from __future__ import annotations

from . import _screenshot_scan, _z_scan
from .pipeline import run_blackboard_pipeline


def main() -> None:
    run_blackboard_pipeline()


def main_z_scan() -> None:
    _z_scan.main()


def main_screenshot_scan() -> None:
    _screenshot_scan.main()
