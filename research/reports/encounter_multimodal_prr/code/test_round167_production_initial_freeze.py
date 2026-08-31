from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPORT = Path(__file__).resolve().parents[1]

ROUND167_IMMUTABLE_CURRENT = {
    "artifacts/data/physical_configuration_family_control_free_v1.json": (
        "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
    ),
    "artifacts/data/physical_initial_analytic_source_v1.json": (
        "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
    ),
    "code/rate_defined_tensor_f0.py": (
        "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5"
    ),
    "code/rate_defined_tensor_f0_packed.py": (
        "447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4"
    ),
    "code/rate_defined_tensor_f0_production_initial_stream.py": (
        "2871976855a0c598b26b8d83b33f4ea3a027a2c826ccdb2ad9b678761093e6cb"
    ),
    "code/rate_defined_tensor_f0_production_initial_rebuild.py": (
        "1ed8ea255df01fca10e294994557b1efc8660f933683477a5a289593da7c1c14"
    ),
    "code/rate_defined_tensor_f0_production_initial_independent.py": (
        "e0121dd2f90bbebc5f973f4e80f7b43dea5ec2d0ac04e1f253a6618b35cf0a96"
    ),
    "code/rate_defined_tensor_f0_geometry_bound_packed_axes.py": (
        "baa4c12032174f179f1aed6ed9bde78dc6f1fb163e262980897ba3e893af8cc6"
    ),
    "code/rate_defined_tensor_f0_production_initial_clean_replay.py": (
        "d8d6793519e64e662e612dddcf7f97074249850029423056e073ff3c11a76a38"
    ),
    "code/test_rate_defined_tensor_f0_production_initial_stream.py": (
        "d32cb29878946f1464587293e0bb76af567c9e3b909e81308623addfa5a13544"
    ),
    "artifacts/data/physical_production_initial_stream_v1/bundle.json": (
        "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
    ),
    "artifacts/data/physical_production_initial_stream_v1_relational_receipt.json": (
        "131ef316bbd70d7539c76bf83972b45643a2676b80c67fcfd78d6d8b089cc0b4"
    ),
    "artifacts/data/physical_production_initial_stream_v1_independent_receipt.json": (
        "2fb16af6545281f988ddf7527b5e88b46e98ec7e5a05fcbe1bb5bf457c6f9136"
    ),
    "artifacts/data/physical_production_initial_stream_v1_geometry_receipt.json": (
        "3b23c641ce82cb30a2f150d9956b235bca918948a40f57365f866e6aa54959fb"
    ),
    "artifacts/data/physical_production_initial_clean_process_replay_v1.json": (
        "e1b25ab5221434e26749e9b2103c04c36e27539a810e2a15c236c1806b333891"
    ),
    "manuscript/encounter_multimodal_prr_theorem_first_working.tex": (
        "7771c89c937d9a2561964de7cc12699f816bcaaa4525710dd647bf1b76747b3c"
    ),
    "manuscript/encounter_multimodal_prr_supplement.tex": (
        "b8182df7e269a90c81e504121db99ae0867c7c5cab8e093be3d32e6a86a58b86"
    ),
    "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf": (
        "937a109118bee0a3a445816cd8ed0b5ff915b038b51f0ca1eb343186af31d4aa"
    ),
    "output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf": (
        "70de25968298d58222bbab10639a2253067f5c01d4d6462d743e3e6eca5790fb"
    ),
    "artifacts/data/theorem_first_working_compile.json": (
        "f7712228afab0ec47000b2e29a28507c2a96abc3c76cd91ffa72efc97e44ab75"
    ),
    "notes/research_contract.md": (
        "9dc8f028ebc97bf81f5d0a9e775e246ecddce838abd4d0fc0029f45fdeeec697"
    ),
    "notes/continuum_next_stage_path.md": (
        "e69c31489ca53b3594509f0f274f022a773a73407e19a9144bddf65ed64f362f"
    ),
    "notes/continuum_research_program_v2.md": (
        "c639dc2b6fbe636c1f24340ea2ea96003487b3613bdd616399c3cd7cb984284c"
    ),
    "README.md": "2a318c9b17df74b8f6709697bcddb044f71e8979eaea00cd1d6949f758748572",
    "code/test_general_dimension_scope_consistency.py": (
        "5d7f5d1a42f08c0bdf6dc61400674ae8abd32fdc94f53d8d6f849a6278257af5"
    ),
    "audits/round_167_production_initial_stream_clean_replay_and_continuum_erratum.md": (
        "38e9a8e6ff5885aaa9188caea4720ae469fb409c88b390fc9578534fac48f9d1"
    ),
}

ROUND167_LIVING_SUCCESSORS = {
    "manuscript/encounter_multimodal_prr_theorem_first_working.tex",
    "manuscript/encounter_multimodal_prr_supplement.tex",
    "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf",
    "output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf",
    "artifacts/data/theorem_first_working_compile.json",
    "notes/research_contract.md",
    "notes/continuum_research_program_v2.md",
    "README.md",
    "code/test_general_dimension_scope_consistency.py",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(relative: str) -> dict[str, object]:
    return json.loads((REPORT / relative).read_bytes())


def test_round167_integrated_bytes_are_frozen() -> None:
    audit = (
        REPORT / "audits/round_167_production_initial_stream_clean_replay_and_continuum_erratum.md"
    ).read_text(encoding="utf-8")
    for relative, expected in ROUND167_IMMUTABLE_CURRENT.items():
        path = REPORT / relative
        assert path.is_file(), relative
        if relative in ROUND167_LIVING_SUCCESSORS:
            assert expected in audit, relative
        else:
            assert _sha256(path) == expected, relative


def test_round167_bundle_and_receipts_keep_the_narrow_scope() -> None:
    bundle_root = REPORT / "artifacts/data/physical_production_initial_stream_v1"
    bundle = _json("artifacts/data/physical_production_initial_stream_v1/bundle.json")
    assert bundle["configuration_count"] == 12
    assert bundle["total_state_workload"] == 34_787_462
    assert bundle["total_dense_expansion_byte_length"] == 556_599_392
    assert len(bundle["file_inventory"]) == 206
    files = [path for path in bundle_root.rglob("*") if path.is_file()]
    assert len(files) == 207
    assert sum(path.stat().st_size for path in files) == 1_439_598
    for key in (
        "authorizes_scientific_execution",
        "clean_process_replay_complete",
        "full_operator_bound",
        "killing_contact_geometry_bound",
        "positive_budget_executed",
        "production_resource_gate",
        "science_executed",
        "topology_complete",
    ):
        assert bundle["flags"][key] is False

    clean = _json("artifacts/data/physical_production_initial_clean_process_replay_v1.json")
    assert clean["receipt_sha256"] == (
        "f33dd0b2695464370e29a2896d3753e753525d9cf5d38b5917a616181096bf9b"
    )
    assert clean["repeat_count"] == 2
    assert clean["total_fresh_processes_observed"] == 10
    assert clean["repeat_evidence_sha256s"] == [
        "865bcd7c57aff7f635fa6032ddd47b393f9d34e9fd74e6b5873d59fe4dc1bd10",
        "865bcd7c57aff7f635fa6032ddd47b393f9d34e9fd74e6b5873d59fe4dc1bd10",
    ]
    assert clean["flags"]["clean_process_replay_complete_for_declared_scope"] is True
    assert clean["flags"]["independent_backend"] is False
    for key in (
        "continuum_verified",
        "f0_pass",
        "full_operator_bound",
        "independent_semantic_replay_complete",
        "killing_contact_geometry_bound",
        "positive_budget_executed",
        "production_resource_gate",
        "propagation_executed",
        "science_executed",
        "topology_complete",
    ):
        assert clean["flags"][key] is False


def test_round167_audit_preserves_the_erratum_and_open_gates() -> None:
    audit = (
        REPORT / "audits/round_167_production_initial_stream_clean_replay_and_continuum_erratum.md"
    ).read_text(encoding="utf-8")
    compact = " ".join(audit.split()).lower()
    for required in (
        "final p0 = 0 / p1 = 0 / p2 = 0",
        "independent_backend=false",
        "killing open / full operator open / production resource gate open / f0 hold",
        "contact-killing geometry not constructed",
        "f1 positive-budget 36-row campaign not authorized / not run",
        "continuum c0-c3 open",
        "prr release hold",
        "z=\\frac{2\\pi d w}{\\gamma}",
        "\\mathbf d\\nabla\\log\\pi=b",
    ):
        assert required in compact
