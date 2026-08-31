#!/usr/bin/env python3
"""Standalone fail-closed validator for the frozen v4 manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_gating_campaign_manifest_v4 import DEFAULT_PACK, DEFAULT_SIDECAR, load_json, validate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--field-pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--field-sidecar", type=Path, default=DEFAULT_SIDECAR)
    parser.add_argument("--runner", type=Path, default=Path(__file__).with_name("gpu_gating_mc_v4.py"))
    parser.add_argument("--engine", type=Path, default=Path(__file__).with_name("gpu_gating_mc_v3.py"))
    args = parser.parse_args()
    summary = validate(load_json(args.manifest.absolute()), pack=args.field_pack.absolute(), sidecar=args.field_sidecar.absolute(), runner=args.runner.absolute(), engine=args.engine.absolute())
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
