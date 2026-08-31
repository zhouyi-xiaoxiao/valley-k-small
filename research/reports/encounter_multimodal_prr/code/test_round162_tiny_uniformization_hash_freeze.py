from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND162_SHA256 = {
    "code/rate_defined_tensor_f0_packed_uniformization.py": (
        "20c95975b5e43fcd5ed2ccd91c578c32524f6a3b2cc4ab5133da36fc3eddb72c"
    ),
    "code/test_rate_defined_tensor_f0_packed_uniformization.py": (
        "dcd3d1c6ae36059a13f98fc9ee9e7409b512ac72e59a25274a3df0e4bdcbd4cd"
    ),
    "code/rate_defined_tensor_f0_packed.py": (
        "447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4"
    ),
    "code/rate_defined_tensor_f0_packed_interval_action.py": (
        "2f3201a9eb1b6fbe577b43c3b046ad5f7f369816a7d4a32f4381506e63494f2a"
    ),
    "code/rate_defined_tensor_f0_packed_rate_action.py": (
        "7c1586e54bac2008ac910d5c2b910cee5206dab8c19948f5b5857db6563813c9"
    ),
    "code/test_rate_defined_tensor_f0_packed_rate_action.py": (
        "b5127aa26ab3179986b5ad5cafbcae55c3dd6768217a2b500ea496f1f833939f"
    ),
    "audits/round_162_tiny_uniformization_hash_specific_independent_attack.md": (
        "03dfc718fce839debd3c82270ca28145a51eb5b79906868bda697b7581ad26a1"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round162_exact_method_bytes_are_frozen() -> None:
    for relative, expected in ROUND162_SHA256.items():
        assert _sha256(REPORT / relative) == expected, relative


def test_round162_acceptance_is_producer_path_only() -> None:
    audit = (
        REPORT / "audits/round_162_tiny_uniformization_hash_specific_independent_attack.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()

    assert "accept exact producer bytes as a bounded" in compact
    assert "p0 = 0 / p1 = 0 / p2 = 2" in compact
    assert "does not accept an externally supplied result or ledger" in compact
    assert "hold f0" in compact
    assert "no f1" in compact
    assert "non_authoritative = true" in compact
    assert "fresh_process = false" in compact
    assert "f0_pass = false" in compact


def test_round162_preserves_both_ledger_authority_findings() -> None:
    audit = (
        REPORT / "audits/round_162_tiny_uniformization_hash_specific_independent_attack.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()

    assert "the power hash chain is not an action replay" in compact
    assert "the poisson validator is not an exponential replay" in compact
    assert "no downstream stage may use a deserialized or modified power ledger" in compact
    assert "only the direct return of the frozen producer" in compact
    assert "promoting either validator to authority" in compact


def test_round162_does_not_promote_resources_or_science() -> None:
    audit = (
        REPORT / "audits/round_162_tiny_uniformization_hash_specific_independent_attack.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()

    assert "cannot substitute for the `7,165,305`-state resource gate" in compact
    assert "positive budget" in compact
    assert "all 36 f1 rows" in compact
    assert "not f0 acceptance or a manuscript result" in compact
