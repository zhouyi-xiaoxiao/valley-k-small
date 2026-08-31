from __future__ import annotations

from pathlib import Path

import check_reproducibility_environment as envcheck


def test_current_environment_matches_report_baseline() -> None:
    report = envcheck.environment_report()
    assert report["match"] is True
    assert report["science_executed"] is False
    assert report["missing_packages"] == []
    assert report["mismatched_packages"] == {}
    assert report["import_failures"] == {}


def test_requirements_file_matches_checker_exactly() -> None:
    path = Path(envcheck.__file__).with_name("requirements-reproducibility.txt")
    requirements = {
        line.split("==", 1)[0]: line.split("==", 1)[1].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    assert requirements == envcheck.EXPECTED_PACKAGES
