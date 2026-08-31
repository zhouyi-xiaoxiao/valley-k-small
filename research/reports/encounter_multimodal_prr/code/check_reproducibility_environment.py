"""Report whether the direct numerical environment matches the frozen baseline."""

from __future__ import annotations

import json
import platform
import sys
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version

EXPECTED_PYTHON = (3, 12)
EXPECTED_PACKAGES = {
    "gmpy2": "2.2.1",
    "matplotlib": "3.11.0",
    "numpy": "2.5.1",
    "pytest": "9.0.3",
    "scipy": "1.18.0",
}


def environment_report() -> dict[str, object]:
    observed: dict[str, str] = {}
    missing: list[str] = []
    mismatched: dict[str, dict[str, str]] = {}
    import_failures: dict[str, str] = {}

    for package, expected in EXPECTED_PACKAGES.items():
        try:
            observed_version = version(package)
        except PackageNotFoundError:
            missing.append(package)
            continue
        observed[package] = observed_version
        if observed_version != expected:
            mismatched[package] = {"expected": expected, "observed": observed_version}
        try:
            import_module(package)
        except Exception as exc:  # pragma: no cover - exercised only on broken runtimes
            import_failures[package] = f"{type(exc).__name__}: {exc}"

    python_minor = sys.version_info[:2]
    python_match = python_minor == EXPECTED_PYTHON
    return {
        "baseline": "encounter_multimodal_prr-direct-dependencies-v1",
        "expected_python_minor": ".".join(map(str, EXPECTED_PYTHON)),
        "observed_python": platform.python_version(),
        "python_minor_match": python_match,
        "observed_platform": platform.platform(),
        "expected_packages": EXPECTED_PACKAGES,
        "observed_packages": observed,
        "missing_packages": sorted(missing),
        "mismatched_packages": mismatched,
        "import_failures": import_failures,
        "match": python_match and not missing and not mismatched and not import_failures,
        "science_executed": False,
    }


def main() -> int:
    report = environment_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
