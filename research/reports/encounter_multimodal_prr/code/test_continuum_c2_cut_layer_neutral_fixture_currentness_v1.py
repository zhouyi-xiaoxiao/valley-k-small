#!/usr/bin/env python3
"""Hash-currentness gate for the six-file neutral C2 cut-layer fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
MANIFEST = REPORT / "artifacts/data/continuum_c2_cut_layer_neutral_fixture_currentness_v1.json"
EXPECTED_SCHEMA = "encounter_continuum_c2_cut_layer_neutral_fixture_currentness_v1"
EXPECTED_STATUS = "CURRENTNESS_ONLY_NEUTRAL_FIXTURE_NO_C2_PROMOTION"
EXPECTED_ROLES = [
    "neutral_source",
    "neutral_fixture",
    "builder",
    "independent_integer_validator",
    "static_two_build_tests",
    "adversarial_mutation_tests",
]


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main() -> int:
    payload = MANIFEST.read_bytes()
    value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(value, dict) or set(value) != {"claim_boundary", "files", "schema", "status"}:
        raise ValueError("wrong currentness-manifest shape")
    canonical = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if payload != canonical:
        raise ValueError("currentness manifest is not canonical sorted JSON")
    if value["schema"] != EXPECTED_SCHEMA or value["status"] != EXPECTED_STATUS:
        raise ValueError("wrong currentness schema/status")
    claims = value["claim_boundary"]
    if not isinstance(claims, dict) or set(claims) != {
        "complete_C2",
        "production_geometry_evidence",
        "release_submission_science_execution",
    } or any(claims[key] is not False for key in claims):
        raise ValueError("currentness claim boundary changed")
    files = value["files"]
    if not isinstance(files, list) or len(files) != len(EXPECTED_ROLES):
        raise ValueError("currentness manifest must contain exactly six files")
    if [entry.get("role") for entry in files if isinstance(entry, dict)] != EXPECTED_ROLES:
        raise ValueError("currentness roles or order changed")
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "role", "sha256"}:
            raise ValueError("malformed currentness entry")
        relative = entry["path"]
        if not isinstance(relative, str) or relative in seen or relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError("unsafe or duplicate currentness path")
        seen.add(relative)
        path = (REPORT / relative).resolve()
        if path.relative_to(REPORT) is None or not path.is_file() or path.is_symlink():
            raise ValueError(f"invalid currentness file: {relative}")
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != entry["sha256"]:
            raise ValueError(f"stale currentness hash: {relative}")
        print(f"PASS current_{entry['role']}")
    print(f"SUMMARY {len(files)}/{len(files)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
