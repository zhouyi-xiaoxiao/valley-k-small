#!/usr/bin/env python3
"""Hash-pinned facade for the unchanged v3 dynamics and v4-r2 contract."""
from __future__ import annotations
import sys
from pathlib import Path
import gpu_gating_mc_v3 as engine
MANIFEST_SCHEMA="grid2d-one-two-target-gating-gpu-v4-r2-manifest"
RESULT_SCHEMA="grid2d-one-two-target-gating-fixed-mean-gpu-v4-r2"
def main(argv=None):
 engine.MANIFEST_SCHEMA=MANIFEST_SCHEMA;engine.RESULT_SCHEMA=RESULT_SCHEMA;engine.__file__=str(Path(__file__).resolve())
 return engine.main(sys.argv[1:] if argv is None else argv)
if __name__=="__main__":raise SystemExit(main())
