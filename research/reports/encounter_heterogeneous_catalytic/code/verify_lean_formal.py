#!/usr/bin/env python3
"""Fail-closed static and saved-output audit of the Lean proof package."""

from __future__ import annotations

import json

from run_publication_pipeline import _formal_integrity_payload, _write_formal_integrity_report


def main() -> None:
    path = _write_formal_integrity_report()
    payload = _formal_integrity_payload()
    print(json.dumps(payload["theorem_counts"], sort_keys=True))
    print(f"formal integrity report: {path}")


if __name__ == "__main__":
    main()
