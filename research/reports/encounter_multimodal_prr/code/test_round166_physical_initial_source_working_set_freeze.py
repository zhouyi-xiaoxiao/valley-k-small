"""Freeze the independently accepted Round-166 physical initial-source set."""

from __future__ import annotations

import hashlib
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND166_SHA256 = {
    "artifacts/data/physical_initial_analytic_source_v1.json": (
        "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
    ),
    "code/rate_defined_tensor_f0_physical_initial_source.py": (
        "afef401d6edcfb5a770d4f01a5a1c38f7837cea47cd2d94c676a1e5974dc9417"
    ),
    "code/rate_defined_tensor_f0_physical_initial_replay.py": (
        "755fd35001423bf931cc9cf2141ad2901a3a67036aa6a7d8e20bd849fe1c3796"
    ),
    "code/test_rate_defined_tensor_f0_physical_initial_source.py": (
        "0e324a3cc3d61437568d4bf387fa1667594900026996ee8bd5c23157cc642989"
    ),
    "notes/continuum_research_program_v2.md": (
        "c639dc2b6fbe636c1f24340ea2ea96003487b3613bdd616399c3cd7cb984284c"
    ),
    "notes/research_contract.md": (
        "01804e5328f669236d9f53f38cbfdda813b37f41e2641c91940ad0e90e60038c"
    ),
    "notes/continuum_next_stage_path.md": (
        "49e5f6b12d8d5b6581c092b80b1bf2af3121054e7f88b6dfa4dcadf826a2cbd7"
    ),
    "code/test_continuum_research_program_v2_scope.py": (
        "65566f202b8ddfe1c06c6237236769a3c859f58630b0c25b85a48acc6113fc6c"
    ),
    "code/test_general_dimension_scope_consistency.py": (
        "48885cd1a9701d5feae632ceef252bc191787eaae586d1293784b14725aa88da"
    ),
    "code/test_round149_exact_m_hash_freeze.py": (
        "b61bf10c40fa5e6dca68b7d471538914de10b6faef36db9ff0714a8d64eb8708"
    ),
    "code/test_round165_continuum_c0a_working_set_freeze.py": (
        "0a60e3466b0cd3796f08e456ae9a5b2bd5085e5fe90d9e2a053e3263b3c58a7e"
    ),
    "manuscript/encounter_multimodal_prr_theorem_first_working.tex": (
        "baa40059995679065dcab4a9ec1ee62d5f4d0a19d53e352605a82b9c990cadbe"
    ),
    "manuscript/encounter_multimodal_prr_supplement.tex": (
        "8168abfd6c20d0f89e193329dd3bd7d1d34dbcfd7d4f5e59e0ac03cce301d7f1"
    ),
    "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf": (
        "cd14b52523fb9cf5989416997d313a72d26d20f4f9b94159b663444acb354851"
    ),
    "output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf": (
        "04953aa8377aada4d604fb2d8bd16ba1adee0a1d08022be7fe09433fdb346729"
    ),
    "artifacts/data/theorem_first_working_compile.json": (
        "54feedc6838ac43305d1239d5e65644cd1aa325c640fe251fab26dda1462f038"
    ),
    "audits/round_166_physical_initial_source_binding_independent_reaudit.md": (
        "f4e4ca3c1d903bcba75c2ec55aa53b76ab8ade8ddffe2be0118d135cd3bd56b3"
    ),
}

ROUND166_LIVING_SUCCESSORS = {
    "notes/continuum_research_program_v2.md",
    "notes/research_contract.md",
    "notes/continuum_next_stage_path.md",
    "code/test_continuum_research_program_v2_scope.py",
    "code/test_general_dimension_scope_consistency.py",
    "manuscript/encounter_multimodal_prr_theorem_first_working.tex",
    "manuscript/encounter_multimodal_prr_supplement.tex",
    "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf",
    "output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf",
    "artifacts/data/theorem_first_working_compile.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_round166_integrated_bytes_are_frozen() -> None:
    audit = (
        REPORT / "audits/round_166_physical_initial_source_binding_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    for relative, expected in ROUND166_SHA256.items():
        path = REPORT / relative
        assert path.is_file(), relative
        if relative in ROUND166_LIVING_SUCCESSORS:
            assert expected in audit, relative
        else:
            assert _sha256(path) == expected, relative


def test_round166_historical_compile_was_fail_closed() -> None:
    audit = (
        REPORT / "audits/round_166_physical_initial_source_binding_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()
    for phrase in (
        "main pages 6",
        "supplemental pages 22",
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


def test_round166_audit_keeps_all_open_boundaries_explicit() -> None:
    audit = (
        REPORT / "audits/round_166_physical_initial_source_binding_independent_reaudit.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()
    for phrase in (
        "final p0 = 0 / p1 = 0 / p2 = 0",
        "current-target serialized lineage = open",
        "production source-to-box streaming = open",
        "operator-axis geometry binding = open",
        "production resource gate = open",
        "f0 complete finite-volume certificate = hold",
        "f1 positive-budget campaign = not authorized / not run",
        "strict continuum topology = hold",
        "prr submission package = hold",
        "the tiny exact source box is a necessary initial-data preflight; it is not a proof",
    ):
        assert phrase in compact


def test_round166_provenance_flags_do_not_promote_the_current_result() -> None:
    source = (REPORT / "code/rate_defined_tensor_f0_physical_initial_source.py").read_text(
        encoding="utf-8"
    )
    for token in (
        "analytic_source_certificate_retained",
        "independent_replay_receipt_retained",
        "result_self_contained_source_provenance",
        "current_target_lineage_replayed",
        "operator_axis_geometry_bound",
        "positive_budget_scientific_result_read",
    ):
        assert token in source

    assert "independent_replay_receipt_retained=False" in source
    assert "result_self_contained_source_provenance=False" in source
    assert "current_target_lineage_replayed=False" in source
    assert "operator_axis_geometry_bound=False" in source
    assert "positive_budget_scientific_result_read=False" in source
