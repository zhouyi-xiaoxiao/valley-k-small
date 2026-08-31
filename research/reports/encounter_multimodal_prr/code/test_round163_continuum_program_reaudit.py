from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND163_SHA256 = {
    "audits/round_163_continuum_program_v2_repair_independent_reaudit.md": (
        "7ac8b2d23769340233f5ba1ae6c7531649e569eaa719f1a8ce865517b40e936d"
    ),
}

ROUND163_HISTORICAL_SNAPSHOT = (
    "7e075e83b23bd711c233f21cdb4e02bb60093ce7827abff70ad26bcb33abe286",
    "00145c8991975f558cf2b289b7937a59c27583c1a02172a1ee5461c45181fdcf",
    "011dd25b3a57339a8325702ae4337aaf57c18292881c36f7391e11e1a270f136",
    "537094d58158aff3fe63a7e589cd979380f7c50ead29818c0f402c23a7410a66",
    "a96b0caa4003037bb886817653fb999f142f0f68b72f6b81458146a2f0f4d004",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round163_exact_repaired_bytes_are_frozen() -> None:
    for relative, expected in ROUND163_SHA256.items():
        assert _sha256(REPORT / relative) == expected, relative
    audit = (
        REPORT / "audits/round_163_continuum_program_v2_repair_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    for expected in ROUND163_HISTORICAL_SNAPSHOT:
        assert expected in audit


def test_round163_is_a_design_reaudit_not_a_continuum_result() -> None:
    audit = (
        REPORT / "audits/round_163_continuum_program_v2_repair_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()

    assert "p0 = 0 / p1 = 0 / p2 = 0 after repair" in compact
    assert "operator template only" in compact
    assert "c0--c7 scientific chain open" in compact
    assert "hold continuum claim" in compact
    assert "no positive-b / no f1" in compact
    assert "not a proof of any one of those open dependencies" in compact


def test_round163_historical_route_is_recorded_in_its_audit() -> None:
    audit = (
        REPORT / "audits/round_163_continuum_program_v2_repair_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()

    assert "ordinary canonical local files, exact hashes" in compact
    assert "independently implemented numerical replay" in compact
    assert "this is a reproducibility route, not a new physical claim" in compact


def test_round163_keeps_the_actual_theorem_gates_open() -> None:
    audit = (
        REPORT / "audits/round_163_continuum_program_v2_repair_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()

    for phrase in (
        "concrete hash-bound c0 model contract = open",
        "fixed-box mosco / strong-resolvent theorem = open c1",
        "computable spatial errors r=0,1,2 = open c2",
        "box derivative errors r=1,2 = open c3",
        "broad-family continuum signature = hold",
        "positive-b / all 36 f1 rows = not authorized / not run",
    ):
        assert phrase in compact
