from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND165_HISTORICAL_SNAPSHOT = {
    "notes/continuum_research_program_v2.md": (
        "d965b604214a16ac74666a008a5913029dfe52519b4e06496f6416d01cee2ed4"
    ),
    "code/test_continuum_research_program_v2_scope.py": (
        "21e69583d404a0a7650dc48a46dbf32c38a67d394fcc3c21ea49a901fb57cb71"
    ),
    "notes/research_contract.md": (
        "28789c9a23ce0d7386b15333ec9141ea0c329eeee763e13c634903fe716d8d46"
    ),
    "notes/continuum_next_stage_path.md": (
        "99976f000d673722d6e36984d4d092646f7a70147fce31eda832b45291eaa0b3"
    ),
    "code/test_general_dimension_scope_consistency.py": (
        "fefa5e3a6fc837ab9335a4cc5b17ac9757c52ad3d6bbce1e6df4ecd4aab55099"
    ),
    "manuscript/encounter_multimodal_prr_supplement.tex": (
        "1323786749826d403535fac7034554a4b5fc32ce8dd1173ccf1747422ff69e77"
    ),
    "manuscript/encounter_multimodal_prr_theorem_first_working.tex": (
        "6e7393e44bb1da9bb196b839534fdf43e18dd90d0829d941ad7e155f4afcbc67"
    ),
    "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf": (
        "c766de16ca3a70eda63397d4d78ccb9f44415982afa4d4b6e0a295197488984b"
    ),
    "output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf": (
        "ea2a33a1faa18bf8c24f002b75b177f94204fc05381ee73d14ae65d251db11ab"
    ),
    "artifacts/data/theorem_first_working_compile.json": (
        "38c03adfc95d3929aa5039b206cbe892a914f9ccf7a7e047ede337d9b2ffcb1b"
    ),
    "audits/round_165_continuum_c0a_and_working_set_independent_reaudit.md": (
        "8a7657a9477d033d02b3640c68544e72871c85a9ec2e13b1dada305e3c3e5d10"
    ),
}

ROUND165_IMMUTABLE_CURRENT = {
    "audits/round_165_continuum_c0a_and_working_set_independent_reaudit.md": (
        "8a7657a9477d033d02b3640c68544e72871c85a9ec2e13b1dada305e3c3e5d10"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round165_immutable_audit_is_frozen() -> None:
    for relative, expected in ROUND165_IMMUTABLE_CURRENT.items():
        assert _sha256(REPORT / relative) == expected, relative


def test_round165_historical_snapshot_remains_in_the_immutable_audit() -> None:
    audit = (
        REPORT / "audits/round_165_continuum_c0a_and_working_set_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    for relative, expected in ROUND165_HISTORICAL_SNAPSHOT.items():
        if relative not in ROUND165_IMMUTABLE_CURRENT:
            assert expected in audit, relative


def test_round165_historical_build_was_deterministic_and_fail_closed() -> None:
    audit = (
        REPORT / "audits/round_165_continuum_c0a_and_working_set_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()
    for phrase in (
        "main pages 5",
        "supplemental pages 21",
        "main rebuilds byte-identical yes",
        "supplemental rebuilds byte-identical yes",
        "all fonts embedded yes",
        "type-3 fonts 0",
        "overfull boxes 0",
        "undefined references 0",
        "undefined citations 0",
        "ghostscript parse pass",
        "release_eligible false",
        "positive_budget_evaluated false",
        "positive_budget_scientific_values_read false",
    ):
        assert phrase in compact


def test_round165_keeps_c0a_separate_from_open_continuum_and_f0_gates() -> None:
    audit = (
        REPORT / "audits/round_165_continuum_c0a_and_working_set_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()
    for phrase in (
        "final p0 = 0 / p1 = 0 / p2 = 0",
        "concrete hash-bound model contract = open c0",
        "fixed-box mosco / strong-resolvent convergence = open c1",
        "computable positive-time spatial errors r=0,1,2 = open c2",
        "first/second derivative box-truncation errors = open c3",
        "continuum stationary topology = hold",
        "f0 complete certificate = hold",
        "f1 positive-budget 36-row campaign = not authorized / not run",
        "prr submission package = hold",
    ):
        assert phrase in compact
    assert "page count is not treated as a publication gate" in compact
