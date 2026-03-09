#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path


MAPPING = [
    ("2d_bimodality", "grid2d_bimodality"),
    ("2d_blackboard_bimodality", "grid2d_blackboard_bimodality"),
    ("2d_rect_bimodality", "grid2d_rect_bimodality"),
    ("2d_reflecting_bimodality", "grid2d_reflecting_bimodality"),
    ("2d_two_target_double_peak", "grid2d_two_target_double_peak"),
    ("deriv_k2", "ring_deriv_k2"),
    ("lazy_flux", "ring_lazy_flux"),
    ("lazy_jump", "ring_lazy_jump"),
    ("lazy_jump_ext", "ring_lazy_jump_ext"),
    ("lazy_jump_ext_rev2", "ring_lazy_jump_ext_rev2"),
    ("luca_regime_map", "cross_luca_regime_map"),
    ("two_target_ring", "ring_two_target"),
    ("valley", "ring_valley"),
    ("valley_dst", "ring_valley_dst"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rename reports/* directories and create compatibility symlinks.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without applying changes.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    reports = repo_root / "reports"

    for old_name, new_name in MAPPING:
        old_dir = reports / old_name
        new_dir = reports / new_name
        if old_dir.is_dir() and not old_dir.is_symlink() and not new_dir.exists():
            print(f"rename {old_dir} -> {new_dir}")
            if not args.dry_run:
                old_dir.rename(new_dir)

        link_path = reports / old_name
        if not link_path.exists() and new_dir.exists():
            print(f"symlink {link_path} -> {new_name}")
            if not args.dry_run:
                os.symlink(new_name, link_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
