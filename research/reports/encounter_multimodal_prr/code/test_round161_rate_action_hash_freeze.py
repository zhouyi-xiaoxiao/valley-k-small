from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND161_SHA256 = {
    "code/rate_defined_tensor_f0_packed_rate_action.py": (
        "7c1586e54bac2008ac910d5c2b910cee5206dab8c19948f5b5857db6563813c9"
    ),
    "code/test_rate_defined_tensor_f0_packed_rate_action.py": (
        "b5127aa26ab3179986b5ad5cafbcae55c3dd6768217a2b500ea496f1f833939f"
    ),
    "code/rate_defined_tensor_f0_packed.py": (
        "447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4"
    ),
    "code/rate_defined_tensor_f0_packed_interval_action.py": (
        "2f3201a9eb1b6fbe577b43c3b046ad5f7f369816a7d4a32f4381506e63494f2a"
    ),
    "audits/round_161_rate_action_hash_specific_independent_attack.md": (
        "9ad9ebf640cb657e5c3c6033880e9f5bf3c9066dea284da9faee3a45f199cf4c"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round161_exact_rate_action_bytes_are_frozen() -> None:
    for relative, expected in ROUND161_SHA256.items():
        assert _sha256(REPORT / relative) == expected, relative


def test_round161_acceptance_is_method_only_and_fail_closed() -> None:
    audit = (REPORT / "audits/round_161_rate_action_hash_specific_independent_attack.md").read_text(
        encoding="utf-8"
    )
    compact = " ".join(audit.split()).lower()

    assert "accept exact hashes as a bounded method primitive" in compact
    assert "hold f0" in compact
    assert "no f1" in compact
    assert "authoritative = false" in compact
    assert "science_executed = false" in compact
    assert "f0_pass = false" in compact
    assert "does not close f0" in compact
    assert "did not read a prospective control or positive budget" in compact


def test_round161_does_not_promote_resource_or_recurrence_authority() -> None:
    audit = (REPORT / "audits/round_161_rate_action_hash_specific_independent_attack.md").read_text(
        encoding="utf-8"
    )
    compact = " ".join(audit.split()).lower()

    assert "not a python allocator, rss, swap, or wall-time proof" in compact
    assert "do not propagate a time-dependent state" in compact
    assert "must be independently attacked on its own hashes" in compact
