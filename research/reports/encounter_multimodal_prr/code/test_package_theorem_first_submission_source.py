from __future__ import annotations

import copy
import io
import json
import tarfile

import package_theorem_first_submission_source as package
import pytest


def test_published_source_package_is_fresh_and_canonical() -> None:
    payload = json.loads(package.MANIFEST.read_text(encoding="utf-8"))
    assert package._freshness_errors(payload) == ()
    archive = package.ARCHIVE.read_bytes()
    members = package._read_archive(archive)
    package._verify_checksum_file(members)
    assert set(members) == {
        "README.md",
        "SHA256SUMS",
        "encounter_multimodal_prr_submission.tex",
        "encounter_multimodal_prr_submission_supplement.tex",
        "exact_m_theorem_full_proof.tex",
        "exact_m_theorem_spine.tex",
        "references.bib",
    }
    assert payload["validation"] == {
        "archive_rebuilt_main_pdf_byte_identically": True,
        "archive_rebuilt_supplement_pdf_byte_identically": True,
        "deterministic_archive_rebuilds": True,
        "forbidden_reader_markers": 0,
        "safe_regular_members_only": True,
        "sha256_ledger_valid": True,
    }


def test_archive_is_deterministic_for_current_sources() -> None:
    snapshots = package.submission._snapshot_sources()
    payloads = package._source_payloads(snapshots)
    assert package._archive_bytes(payloads) == package._archive_bytes(payloads)
    assert package._read_archive(package._archive_bytes(payloads)) == payloads


def test_clean_proof_is_the_exact_reader_transformation() -> None:
    members = package._read_archive(package.ARCHIVE.read_bytes())
    clean = members["exact_m_theorem_full_proof.tex"]
    frozen = package.submission.EXACT_M_FULL_PROOF_TEX.read_bytes()
    assert clean == package.submission._reader_proof(frozen)
    assert b"working paper" not in clean
    assert b"used in the main\ntext" in clean


def test_checksum_mutation_is_rejected() -> None:
    members = package._read_archive(package.ARCHIVE.read_bytes())
    mutated = copy.deepcopy(members)
    mutated["README.md"] += b" "
    with pytest.raises(RuntimeError, match="checksum"):
        package._verify_checksum_file(mutated)


def test_unsafe_archive_member_is_rejected() -> None:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as archive:
        member = tarfile.TarInfo("../escape")
        member.size = 1
        member.mode = 0o644
        member.mtime = package.SOURCE_DATE_EPOCH
        archive.addfile(member, io.BytesIO(b"x"))
    compressed = io.BytesIO()
    with package.gzip.GzipFile(
        filename="",
        mode="wb",
        fileobj=compressed,
        mtime=0,
    ) as stream:
        stream.write(raw.getvalue())
    with pytest.raises(RuntimeError, match="noncanonical"):
        package._read_archive(compressed.getvalue())


def test_package_reader_sources_have_no_internal_markers() -> None:
    members = package._read_archive(package.ARCHIVE.read_bytes())
    for name, payload in members.items():
        if name == "SHA256SUMS":
            continue
        text = payload.decode("utf-8")
        package.submission._audit_reader_text(
            package.submission._strip_tex_comments(text)
            if name.endswith(".tex")
            else text,
            label=name,
        )
