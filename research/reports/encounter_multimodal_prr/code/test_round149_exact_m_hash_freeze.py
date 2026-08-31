"""Preserve immutable Round-149 bytes and its historical generated snapshot."""

from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND149_SHA256 = {
    "manuscript/exact_m_theorem_full_proof.tex": (
        "a372b5a33d2203b8f3214a153f4aaf1e81497bf146c0ac1db1cfda97919c1c7b"
    ),
    "manuscript/encounter_multimodal_prr_supplement.tex": (
        "566b752f2d5c2c8fabdf0a421f16599317a697dd46f7d41b6b16475495cb2e65"
    ),
    "manuscript/encounter_multimodal_prr_theorem_first_working.tex": (
        "6e7393e44bb1da9bb196b839534fdf43e18dd90d0829d941ad7e155f4afcbc67"
    ),
    "manuscript/exact_m_theorem_spine.tex": (
        "79b0a4467a67999f605b8a5d8ec07e41a88c07edc8cdf1639ad6b8d4ce70658e"
    ),
    "manuscript/references.bib": (
        "2f90b6735993c6d2fa8bb8f1a6c35c334706d02585361d4ee9238ac020ce9c76"
    ),
    "code/compile_theorem_first_working.py": (
        "15098db6e731e23a31967077b79ace723849b5e8383169bb497fa57f9b92725e"
    ),
    "code/test_compile_theorem_first_working.py": (
        "c48ecffdd4222ef7987151e20037c950c324eec867a814d1b806751ebb43aa7c"
    ),
    "artifacts/data/theorem_first_working_compile.json": (
        "797d536e16016a0ba80d44d7be265197a12be47ecfdb4e20da67e46248008646"
    ),
    "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf": (
        "c766de16ca3a70eda63397d4d78ccb9f44415982afa4d4b6e0a295197488984b"
    ),
    "output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf": (
        "3bf770bd28d577aaac54057601e315745d240d29246fa3831a1d39fc82f7dbea"
    ),
    "audits/round_149_exact_m_supplement_migration_independent_attack.md": (
        "f689002b01b1fff3549ed446c9b05efe3fbe3cfc4aa1a3b64c859bbb18dfea78"
    ),
}

# Round 149 remains the historical authority for the mathematical migration.
# The Supplemental wrapper and its generated outputs were later refreshed only
# to report that completed audit accurately.  The theorem proof, reader spine,
# bibliography, compiler, and audit record must remain byte-identical to the
# independently accepted Round-149 snapshot.  The theorem-first main wrapper
# may later gain separately audited method-boundary prose, so its Round-149
# bytes are preserved by the immutable audit rather than as a living-file pin.
ROUND149_IMMUTABLE_CURRENT = {
    key: ROUND149_SHA256[key]
    for key in (
        "manuscript/exact_m_theorem_full_proof.tex",
        "manuscript/exact_m_theorem_spine.tex",
        "manuscript/references.bib",
        "code/compile_theorem_first_working.py",
        "code/test_compile_theorem_first_working.py",
        "audits/round_149_exact_m_supplement_migration_independent_attack.md",
    )
}

ROUND149_HISTORICAL_GENERATED = {
    key: ROUND149_SHA256[key]
    for key in (
        "manuscript/encounter_multimodal_prr_supplement.tex",
        "manuscript/encounter_multimodal_prr_theorem_first_working.tex",
        "artifacts/data/theorem_first_working_compile.json",
        "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf",
        "output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf",
    )
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round149_mathematical_core_has_not_drifted() -> None:
    for relative, expected in ROUND149_IMMUTABLE_CURRENT.items():
        path = REPORT / relative
        assert path.is_file(), relative
        assert _sha256(path) == expected, relative


def test_round149_generated_snapshot_remains_in_the_immutable_audit() -> None:
    audit = (
        REPORT / "audits/round_149_exact_m_supplement_migration_independent_attack.md"
    ).read_text(encoding="utf-8")
    for expected in ROUND149_HISTORICAL_GENERATED.values():
        assert expected in audit


def test_round149_audit_preserves_the_narrow_acceptance_boundary() -> None:
    audit = (
        REPORT / "audits/round_149_exact_m_supplement_migration_independent_attack.md"
    ).read_text(encoding="utf-8")
    for required in (
        "P0 = 0, P1 = 0, P2 = 0",
        "useful finite positive budget                    NOT PROVED",
        "nontrivial-contact continuum realization         NOT PROVED",
        "event mass / survival / solver convergence       NOT PROVED",
        "F0                                               HOLD",
        "F1                                               HOLD",
        "PRR submission                                   HOLD",
    ):
        assert required in audit
