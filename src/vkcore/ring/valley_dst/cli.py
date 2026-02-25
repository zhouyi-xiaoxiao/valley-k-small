from __future__ import annotations

from .mc import main_dst_usage as _main_dst_usage
from .mc import main_second_peak_usage as _main_second_peak_usage
from .scans import main_flux_scan as _main_flux_scan
from .scans import main_second_peak_scan as _main_second_peak_scan


def main_flux_scan() -> None:
    _main_flux_scan()


def main_dst_usage() -> None:
    _main_dst_usage()


def main_second_peak_scan() -> None:
    _main_second_peak_scan()


def main_second_peak_usage() -> None:
    _main_second_peak_usage()


def main_bimodality_flux_scan() -> None:
    main_flux_scan()


def main_dst_shortcut_usage_mc() -> None:
    main_dst_usage()


def main_second_peak_shortcut_usage_mc() -> None:
    main_second_peak_usage()
