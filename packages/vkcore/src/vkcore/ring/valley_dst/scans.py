from __future__ import annotations

from . import _bimodality_flux_scan as _flux
from . import _second_peak_scan as _scan


def main_flux_scan() -> None:
    _flux.main()


def main_second_peak_scan() -> None:
    _scan.main()
