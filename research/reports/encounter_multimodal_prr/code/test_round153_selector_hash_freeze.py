"""Freeze the selector bytes independently accepted in Round 153."""

from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND153_SHA256 = {
    "code/f1_to_f2_common_observable_selector_v2.py": (
        "b80e720a0a88df053b3e9133582a0a27c31d513b3bb091da006f520a4e3bace6"
    ),
    "code/test_f1_to_f2_common_observable_selector_v2.py": (
        "ed951bbe0c58084d49067e7941084e1bef9f9e215cb3162e195506aefd6230ba"
    ),
    "code/test_f1_to_f2_common_observable_selector_v2_round131_independent.py": (
        "e4c88f44f02e92deed9fbe4be742cdf03519d4811196e2413b0f3fd2b42b1345"
    ),
    "code/test_f1_to_f2_common_observable_selector_v2_round139_independent.py": (
        "76ba6cb1b990fc632528e4cff5a9739242b9de87108d371e09c1ccca026c6b77"
    ),
    "code/test_f1_to_f2_common_observable_selector_v2_round140_repair.py": (
        "1dfbf2fd7a72caa9afef120b0ef79df9759f5fc2bdd60105ea854cfaf8699f2f"
    ),
    "code/test_f1_to_f2_common_observable_selector_v2_round143_certificate_repair.py": (
        "c8464e35c98dcfccc5ff726483bede774db58ce7512dc5f442f93031298aacdc"
    ),
    "code/test_f1_to_f2_common_observable_selector_v2_round144_isolation_closure.py": (
        "0e3817e6bd138cd9caea7ee001f95e59cf506a75677f3abe36a1e346e577322e"
    ),
    "audits/round_151_selector_orphan_test_race_repair.md": (
        "38173fcf06c2a582067495b9cb17ee943c1725b3bcae627967a25fbc3d6ad689"
    ),
    "audits/round_153_selector_round151_independent_attack.md": (
        "216749d4deb0b46ed25f7fff4358c9354e9a9e2425d2ba708395d070ceece462"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round153_selector_bytes_have_not_drifted() -> None:
    for relative, expected in ROUND153_SHA256.items():
        path = REPORT / relative
        assert path.is_file(), relative
        assert _sha256(path) == expected, relative


def test_round153_acceptance_remains_process_scoped_and_science_free() -> None:
    audit = (REPORT / "audits/round_153_selector_round151_independent_attack.md").read_text(
        encoding="utf-8"
    )
    for required in (
        "P0 = 0, P1 = 0, P2 = 2",
        "sampled second-parent checked-in assertion           OPEN P2 HARDENING",
        "second-POSIX replay                                   OPEN P2",
        "F0 / F1 / F2 / F3 / positive-budget science          NOT RUN / NOT AUTHORIZED",
    ):
        assert required in audit
