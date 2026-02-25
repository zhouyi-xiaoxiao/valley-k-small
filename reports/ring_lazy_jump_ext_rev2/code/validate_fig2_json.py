#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple

WINDOWS = ["peak1", "valley", "peak2"]
CLASSES = ["C0J0", "C1pJ0", "C0J1p", "C1pJ1p"]


def _fail(msg: str) -> None:
    print(f"[validate_fig2_json] ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _warn(msg: str) -> None:
    print(f"[validate_fig2_json] WARN: {msg}", file=sys.stderr)


def _require_keys(obj: Dict, keys: Iterable[str], ctx: str) -> None:
    for k in keys:
        if k not in obj:
            _fail(f"missing key '{k}' in {ctx}")


def _check_interval(interval: list, window: str) -> None:
    if not isinstance(interval, list) or len(interval) != 2:
        _fail(f"bin_intervals[{window}] must be [tL, tR]")
    tL, tR = interval
    try:
        tL = float(tL)
        tR = float(tR)
    except Exception as exc:
        _fail(f"bin_intervals[{window}] non-numeric: {exc}")
    if tL >= tR:
        _fail(f"bin_intervals[{window}] invalid: tL >= tR")


def _check_props(props: Dict[str, Dict[str, Dict[str, float]]]) -> None:
    for k_label, win_map in props.items():
        for window in WINDOWS:
            if window not in win_map:
                _fail(f"proportions missing window '{window}' for {k_label}")
            cls_map = win_map[window]
            for cls in CLASSES:
                if cls not in cls_map:
                    _fail(f"proportions missing class '{cls}' for {k_label}/{window}")
                val = cls_map[cls]
                if not isinstance(val, (int, float)):
                    _fail(f"proportions[{k_label}][{window}][{cls}] not numeric")
                if val < 0:
                    _fail(f"proportions[{k_label}][{window}][{cls}] negative")
            s = float(sum(cls_map.values()))
            if abs(s - 1.0) > 1e-2:
                _warn(f"{k_label}/{window} proportions sum {s:.4f} (will be renormalized in plotting)")


def _check_counts(counts: Dict[str, Dict[str, Dict[str, float]]]) -> None:
    for k_label, win_map in counts.items():
        for window in WINDOWS:
            if window not in win_map:
                _fail(f"counts missing window '{window}' for {k_label}")
            cls_map = win_map[window]
            for cls in CLASSES:
                if cls not in cls_map:
                    _fail(f"counts missing class '{cls}' for {k_label}/{window}")
                val = cls_map[cls]
                if not isinstance(val, (int, float)):
                    _fail(f"counts[{k_label}][{window}][{cls}] not numeric")
                if val < 0:
                    _fail(f"counts[{k_label}][{window}][{cls}] negative")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate fig2 JSON inputs.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--schema", required=False, type=Path)
    args = parser.parse_args()

    data = json.loads(args.input.read_text())
    _require_keys(data, ["windows", "bin_colors", "classes", "class_colors", "bin_intervals", "proportions"], "root")

    for window in WINDOWS:
        if window not in data["bin_intervals"]:
            _fail(f"bin_intervals missing window '{window}'")
        _check_interval(data["bin_intervals"][window], window)

    for cls in CLASSES:
        if cls not in data["class_colors"]:
            _fail(f"class_colors missing class '{cls}'")

    _check_props(data["proportions"])

    if "counts" in data:
        _check_counts(data["counts"])

    print("fig2 JSON validation OK")


if __name__ == "__main__":
    main()
