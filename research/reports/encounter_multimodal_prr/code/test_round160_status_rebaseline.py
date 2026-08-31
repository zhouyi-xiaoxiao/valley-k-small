from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND160_SHA256 = {
    "manuscript/README.md": ("b426ecd016c4487c531cd1ab2b47a088c6745148091da596fce45e81e72dd6d0"),
    "code/check_reproducibility_environment.py": (
        "c592a78ed0f2ac07afde518d8fb2426f1f14a93f034e784d73b291dfeaf90fe1"
    ),
    "code/requirements-reproducibility.txt": (
        "373f9cc7f054a4ffd858a463ec5da50666e1c0a3d2607202f5b05c202c94774e"
    ),
    "code/test_check_reproducibility_environment.py": (
        "091d1f2ca4a02aa9940f7a685d15cb502af9f49a123c7c7474f7db1fab104f59"
    ),
    "notes/reproducibility_environment.md": (
        "a203bccef6f329afbdac258356f94b438aa547fa9cec7cff7b7c73fe9ffa4941"
    ),
    "audits/round_160_theorem_first_status_and_environment_rebaseline.md": (
        "f8df1d612be2a13a3d4efed98bf9da23a7c346bed3b09e2b58abfc99a1210ea1"
    ),
}

ROUND160_HISTORICAL_GENERATED = (
    "f89135e25b35cff16a5e7d39305b94f3615f776f9d2322dc2dc5d90bde64c183",
    "c766de16ca3a70eda63397d4d78ccb9f44415982afa4d4b6e0a295197488984b",
    "3831626dd565aa21abd32c407db609125737f5a3de130e1e0f853bcb2f202ae2",
    "b3923de0615fbe2e6399aa9196a92b86f10331ceb80da38d8a182a4d41b9bef0",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round160_status_and_environment_bytes_are_frozen() -> None:
    for relative, expected in ROUND160_SHA256.items():
        assert _sha256(REPORT / relative) == expected, relative


def test_round160_preserves_the_fail_closed_boundary() -> None:
    audit = (
        REPORT / "audits/round_160_theorem_first_status_and_environment_rebaseline.md"
    ).read_text(encoding="utf-8")
    pointer = (REPORT / "manuscript/README.md").read_text(encoding="utf-8")
    environment = (REPORT / "notes/reproducibility_environment.md").read_text(encoding="utf-8")
    compact_audit = " ".join(audit.split()).lower()
    for expected in ROUND160_HISTORICAL_GENERATED:
        assert expected in audit
    assert "frozen mathematical migration passed round 149" in compact_audit
    assert "finite-parameter f0--f3" in compact_audit
    assert "release_eligible" not in compact_audit
    assert "Do not upload either file" in pointer
    assert "not a submission package" in " ".join(pointer.split())
    assert "not yet a transitive wheel/hash lock" in environment
    assert "does not evaluate a positive budget" in environment
