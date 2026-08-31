from __future__ import annotations

import dataclasses
import hashlib
import json
import re
import subprocess
from pathlib import Path

import compile_theorem_first_submission as build
import pytest


def _mutated_snapshot(
    snapshot: build.common.FileSnapshot,
    payload: bytes,
) -> build.common.FileSnapshot:
    return dataclasses.replace(
        snapshot,
        payload=payload,
        sha256=hashlib.sha256(payload).hexdigest(),
    )


def test_closed_source_set_and_frozen_theorem_inputs() -> None:
    assert build.REPORT == build.HERE.parents[1]
    assert set(build._required_source_paths()) == {
        "manuscript/encounter_multimodal_prr_submission.tex",
        "manuscript/encounter_multimodal_prr_submission_supplement.tex",
        "manuscript/exact_m_theorem_spine.tex",
        "manuscript/exact_m_theorem_full_proof.tex",
        "manuscript/references.bib",
        "artifacts/data/rate_defined_tensor_f0_resource_v1.json",
        "artifacts/data/rate_defined_tensor_f0_resource_v1.json.resources.json",
        "code/compile_theorem_first_working.py",
        "code/compile_theorem_first_submission.py",
    }
    assert build._sha256(build.EXACT_M_SPINE_TEX) == build.EXPECTED_SPINE_SHA256
    assert build._sha256(build.EXACT_M_FULL_PROOF_TEX) == (
        build.EXPECTED_FULL_PROOF_SHA256
    )
    main = build.MAIN_TEX.read_text(encoding="utf-8")
    supplement = build.SUPPLEMENT_TEX.read_text(encoding="utf-8")
    assert main.count(r"\input{exact_m_theorem_spine.tex}") == 1
    assert supplement.count(r"\input{exact_m_theorem_full_proof.tex}") == 1


def test_live_terminal_receipt_selects_only_theorem_branch() -> None:
    receipt = build._validate_terminal_receipt(build._snapshot_sources())
    assert receipt == {
        "canonical_sha256": build.EXPECTED_CANONICAL_SHA256,
        "failure_reasons": list(build.EXPECTED_FAILURE_REASONS),
        "measurement": {
            "host_peak_footprint_bytes": 17_931_596_736,
            "peak_rss_bytes": 5_455_511_552,
            "process_swap_delta": 0,
            "wall_seconds_hex": "0x1.0317fdfccd100p+10",
        },
        "receipt_sha256": build.EXPECTED_TERMINAL_RECEIPT_SHA256,
        "status": build.EXPECTED_TERMINAL_STATUS,
    }


def test_receipt_reason_mutation_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    snapshots = build._snapshot_sources()
    key = "artifacts/data/rate_defined_tensor_f0_resource_v1.json.resources.json"
    value = json.loads(snapshots[key].payload)
    value["failure_reasons"] = ["rss_cap_exceeded"]
    payload = (json.dumps(value, sort_keys=True) + "\n").encode()
    snapshots[key] = _mutated_snapshot(snapshots[key], payload)
    monkeypatch.setattr(
        build, "EXPECTED_TERMINAL_RECEIPT_SHA256", snapshots[key].sha256
    )
    with pytest.raises(RuntimeError, match="failure reasons"):
        build._validate_terminal_receipt(snapshots)


def test_receipt_branch_mutation_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    snapshots = build._snapshot_sources()
    key = "artifacts/data/rate_defined_tensor_f0_resource_v1.json.resources.json"
    value = json.loads(snapshots[key].payload)
    value["status"] = "UNEXPECTED_BRANCH"
    payload = (json.dumps(value, sort_keys=True) + "\n").encode()
    snapshots[key] = _mutated_snapshot(snapshots[key], payload)
    monkeypatch.setattr(
        build, "EXPECTED_TERMINAL_RECEIPT_SHA256", snapshots[key].sha256
    )
    with pytest.raises(RuntimeError, match="does not select"):
        build._validate_terminal_receipt(snapshots)


def test_receipt_hash_mutation_is_rejected() -> None:
    snapshots = build._snapshot_sources()
    key = "artifacts/data/rate_defined_tensor_f0_resource_v1.json.resources.json"
    snapshots[key] = dataclasses.replace(snapshots[key], sha256="0" * 64)
    with pytest.raises(RuntimeError, match="receipt hash"):
        build._validate_terminal_receipt(snapshots)


def test_reader_proof_is_one_exact_presentation_edit() -> None:
    frozen = build.EXACT_M_FULL_PROOF_TEX.read_bytes()
    transformed = build._reader_proof(frozen)
    assert hashlib.sha256(frozen).hexdigest() == build.EXPECTED_FULL_PROOF_SHA256
    assert b"working paper" in frozen
    assert b"working paper" not in transformed
    assert b"used in the main\ntext" in transformed
    assert len(build._PROOF_READER_REPLACEMENTS) == 1


def test_reader_sources_have_no_internal_or_unfinished_markers() -> None:
    snapshots = build._snapshot_sources()
    for relative in (
        "manuscript/encounter_multimodal_prr_submission.tex",
        "manuscript/encounter_multimodal_prr_submission_supplement.tex",
        "manuscript/exact_m_theorem_spine.tex",
    ):
        build._audit_reader_text(
            build._strip_tex_comments(snapshots[relative].payload.decode("utf-8")),
            label=relative,
        )
    build._audit_reader_text(
        build._strip_tex_comments(
            build._reader_proof(
                snapshots["manuscript/exact_m_theorem_full_proof.tex"].payload
            ).decode("utf-8")
        ),
        label="reader proof",
    )


def test_published_pdfs_are_reader_clean_and_claim_bounded() -> None:
    required = {
        build.FINAL_MAIN_PDF,
        build.FINAL_SUPPLEMENT_PDF,
    }
    assert all(path.is_file() for path in required)
    text: dict[Path, str] = {}
    for path in required:
        process = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(path), "-"],
            check=True,
            stdout=subprocess.PIPE,
        )
        text[path] = process.stdout.decode("utf-8")
        build._audit_reader_text(text[path], label=path.name)

    main = text[build.FINAL_MAIN_PDF]
    main_linear = re.sub(r"\s+", " ", re.sub(r"\f\d+\s*", " ", main))
    assert "produces exactly" in main and "nondegenerate maxima" in main
    assert re.search(
        r"no numerical evidence for a particular finite-parameter realization",
        main_linear,
    )
    assert "make no rigorous numerical claim" in main_linear
    assert "DATA AVAILABILITY" in main_linear
    assert "purely mathematical work" in main_linear
    assert "no data were created or analyzed" in main_linear
    assert (
        "See Supplemental Material at [URL will be inserted by publisher]"
        in main_linear
    )
    assert "Joint distribution of multiple boundary local times" in main_linear
    assert "Xiaoxiao Zhouyi" in main_linear and "Luca Giuggioli" in main_linear
    assert "xiaoxiao.zhouyi@bristol.ac.uk" in main_linear

    supplement = text[build.FINAL_SUPPLEMENT_PDF]
    assert "EXACT PRESCRIBED FINITE MODALITY: COMPLETE PROOF" in supplement
    assert "Uniform weak-reaction mixed-jet bridge" in supplement


def test_manifest_is_fresh_and_keeps_human_metadata_separate() -> None:
    payload = json.loads(build.MANIFEST.read_text(encoding="utf-8"))
    assert not build._manifest_freshness_errors(payload)
    assert payload["reader_artifacts_ready"] is True
    assert payload["claim_scope"] == {
        "finite_parameter_physical_evidence": False,
        "off_lattice_execution": False,
        "rigorous_numerical_continuum_convergence": False,
        "scientific_result": "exact_prescribed_finite_modality_doi_continuum_theorem",
    }
    assert payload["terminal_branch_receipt"]["status"] == (
        build.EXPECTED_TERMINAL_STATUS
    )
    assert payload["terminal_branch_receipt"]["failure_reasons"] == list(
        build.EXPECTED_FAILURE_REASONS
    )
    assert payload["submission_metadata_gate"]["complete"] is False
    assert payload["validation"]["forbidden_reader_markers"] == 0


def test_supplement_is_formally_cited_and_its_references_are_in_main() -> None:
    main = build.MAIN_TEX.read_text(encoding="utf-8")
    bibliography = build.REFERENCES_BIB.read_text(encoding="utf-8")
    assert r"\cite{supplementalMaterial}" in main
    assert r"\nocite{grebenkov2020multiple}" in main
    assert "@misc{supplementalMaterial," in bibliography


@pytest.mark.parametrize(
    "payload",
    [
        "HOLD",
        "PASS",
        "F0",
        "F3",
        "C0",
        "C3",
        "working draft",
        "placeholder",
        "not a submission",
        "release_eligible",
        "round",
    ],
)
def test_reader_marker_gate_rejects_forbidden_terms(payload: str) -> None:
    with pytest.raises(RuntimeError, match="exposes"):
        build._audit_reader_text(payload, label="mutation")
