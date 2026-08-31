"""Freeze the bounded F0 implementation primitive accepted in Round 155."""

from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND155_SHA256 = {
    "code/rate_defined_tensor_f0_packed.py": (
        "447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4"
    ),
    "code/test_rate_defined_tensor_f0_packed.py": (
        "adf4e7dd316a623ff2248d8876592bd6799045976369211f1f0da1ecd6b80458"
    ),
    "code/rate_defined_tensor_f0_packed_interval_action.py": (
        "2f3201a9eb1b6fbe577b43c3b046ad5f7f369816a7d4a32f4381506e63494f2a"
    ),
    "code/test_rate_defined_tensor_f0_packed_interval_action.py": (
        "8ec937f23579d3560cda7a505a7960b14cf297cfa9f7f8b4604eed121e40362d"
    ),
    "audits/round_152_f0_packed_directed_action_independent_attack.md": (
        "aa3180306aef40cc6ecb04a32e7d29c88aacc5c9168fc8b6d98521756c130410"
    ),
    "audits/round_154_f0_packed_directed_action_repair.md": (
        "eba413a7cfe57061196c2a5cead79007d1ae27e8da1966d5ddb16d907716aff7"
    ),
    "audits/round_155_f0_packed_directed_action_independent_reaudit.md": (
        "f5757c5da6ca152f99c184cd921ab3babdb1fe63d3192d133fc8a737cc06ccc1"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round155_f0_primitive_bytes_have_not_drifted() -> None:
    for relative, expected in ROUND155_SHA256.items():
        path = REPORT / relative
        assert path.is_file(), relative
        assert _sha256(path) == expected, relative


def test_round155_acceptance_remains_bounded_and_science_free() -> None:
    audit = (
        REPORT / "audits/round_155_f0_packed_directed_action_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    for required in (
        "ACCEPT ROUND-154 REPAIR AS A BOUNDED IMPLEMENTATION PRIMITIVE / HOLD F0 / NO F1",
        "result relationship consistency                PASS / NOT AUTHENTICATION",
        "separate implementation / fresh verifier       OPEN",
        "F0                                               HOLD",
        "F1 / positive-budget science                    NOT AUTHORIZED / NOT RUN",
        "bounded implementation primitive.  No release, F0, F1, or PRR evidentiary",
    ):
        assert required in audit


def test_round155_digest_is_not_a_fresh_verifier_or_authentication() -> None:
    audit = (
        REPORT / "audits/round_155_f0_packed_directed_action_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    for required in (
        "the result digest is not authentication",
        "The digest is intentionally public and unkeyed.",
        "it is not\nauthentication, provenance, producer-independent recomputation, or a fresh\nverifier receipt.",
        "No downstream stage may upgrade it to any of those roles.",
    ):
        assert required in audit
