from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_scientific_guardrails_are_wired() -> None:
    proc = subprocess.run(
        ["python3", "scripts/reportctl.py", "validate-science-rules"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout
