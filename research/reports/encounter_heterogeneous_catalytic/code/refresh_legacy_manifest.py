#!/usr/bin/env python3
"""Refresh the legacy report-wide manifest after all child generators run."""

from __future__ import annotations

from pathlib import Path

from build_report import REPO, write_current_legacy_manifest


def main() -> None:
    generator = Path(__file__).resolve()
    path = write_current_legacy_manifest(
        generator=generator,
        command=["python", str(generator.relative_to(REPO))],
    )
    print(path)


if __name__ == "__main__":
    main()
