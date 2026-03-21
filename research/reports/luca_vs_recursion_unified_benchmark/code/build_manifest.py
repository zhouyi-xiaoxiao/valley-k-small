#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from common import DATA_DIR, ensure_dirs, manifest_rows


def write_manifest(path: Path) -> None:
    rows = manifest_rows()
    fields = [
        "workload_id",
        "task_kind",
        "source_report",
        "model_family",
        "geometry_kind",
        "method_family",
        "solver_variant",
        "native_horizon",
        "curve_horizon",
        "effective_horizon",
        "state_size",
        "defect_pairs",
        "target_count",
        "common_error_horizon",
        "title_en",
        "title_cn",
        "note_en",
        "note_cn",
        "config_figure_id",
        "historical_source",
        "display_params_json",
        "config_json",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build manifest for unified Luca-vs-recursion benchmark.")
    parser.add_argument("--out", type=str, default=str(DATA_DIR / "manifest.csv"))
    args = parser.parse_args()

    ensure_dirs()
    out = Path(args.out)
    write_manifest(out)
    print(json.dumps({"manifest": str(out), "rows": len(manifest_rows())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
