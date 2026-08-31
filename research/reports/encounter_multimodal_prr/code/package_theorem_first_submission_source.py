#!/usr/bin/env python3
"""Build and verify the clean, deterministic theorem-article source archive."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import tarfile
import tempfile
from pathlib import Path
from typing import Any, Mapping

import compile_theorem_first_submission as submission


HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
OUTPUT = REPORT / "output" / "source"

ARCHIVE = OUTPUT / "encounter_multimodal_prr_submission_source.tar.gz"
MANIFEST = DATA / "theorem_first_submission_source_package.json"
ARCHIVE_ROOT = "encounter_multimodal_prr_submission_source"
SCHEMA_VERSION = 1
SOURCE_DATE_EPOCH = int(submission.SOURCE_DATE_EPOCH)

README = b"""# Prescribed finite-window reaction-time modality

This archive contains the clean reader source for the main article and
Supplemental Material.  It contains no generated scientific figure or
empirical dataset; the result is analytical.

Requirements:

- REVTeX 4.2
- LaTeXmk with pdfLaTeX and BibTeX

From this directory, a deterministic rebuild is:

```bash
export SOURCE_DATE_EPOCH=1784505600
export FORCE_SOURCE_DATE=1
export LC_ALL=C
export TZ=UTC
latexmk -pdf -g -interaction=nonstopmode -halt-on-error \
  -file-line-error encounter_multimodal_prr_submission.tex
latexmk -pdf -g -interaction=nonstopmode -halt-on-error \
  -file-line-error encounter_multimodal_prr_submission_supplement.tex
```

The two PDFs should be submitted as separate article and Supplemental
Material files.  Author declarations and public-archive metadata are entered
through the journal workflow and are not inferred by this archive.
"""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _source_payloads(
    snapshots: Mapping[str, submission.common.FileSnapshot],
) -> dict[str, bytes]:
    payloads = {
        submission.MAIN_TEX.name: snapshots[
            "manuscript/encounter_multimodal_prr_submission.tex"
        ].payload,
        submission.SUPPLEMENT_TEX.name: snapshots[
            "manuscript/encounter_multimodal_prr_submission_supplement.tex"
        ].payload,
        submission.EXACT_M_SPINE_TEX.name: snapshots[
            "manuscript/exact_m_theorem_spine.tex"
        ].payload,
        submission.EXACT_M_FULL_PROOF_TEX.name: submission._reader_proof(
            snapshots["manuscript/exact_m_theorem_full_proof.tex"].payload
        ),
        submission.REFERENCES_BIB.name: snapshots[
            "manuscript/references.bib"
        ].payload,
        "README.md": README,
    }
    for name, payload in payloads.items():
        text = payload.decode("utf-8")
        submission._audit_reader_text(
            submission._strip_tex_comments(text) if name.endswith(".tex") else text,
            label=f"source archive {name}",
        )
    checksums = "".join(
        f"{_sha256(payloads[name])}  {name}\n"
        for name in sorted(payloads)
    ).encode("ascii")
    payloads["SHA256SUMS"] = checksums
    return payloads


def _archive_bytes(payloads: Mapping[str, bytes]) -> bytes:
    tar_buffer = io.BytesIO()
    with tarfile.open(
        fileobj=tar_buffer,
        mode="w",
        format=tarfile.USTAR_FORMAT,
    ) as archive:
        for name in sorted(payloads):
            payload = payloads[name]
            member = tarfile.TarInfo(f"{ARCHIVE_ROOT}/{name}")
            member.size = len(payload)
            member.mode = 0o644
            member.mtime = SOURCE_DATE_EPOCH
            member.uid = 0
            member.gid = 0
            member.uname = ""
            member.gname = ""
            archive.addfile(member, io.BytesIO(payload))
    compressed = io.BytesIO()
    with gzip.GzipFile(
        filename="",
        mode="wb",
        fileobj=compressed,
        compresslevel=9,
        mtime=0,
    ) as stream:
        stream.write(tar_buffer.getvalue())
    return compressed.getvalue()


def _read_archive(payload: bytes) -> dict[str, bytes]:
    members: dict[str, bytes] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            for member in archive.getmembers():
                prefix = f"{ARCHIVE_ROOT}/"
                short_name = (
                    member.name[len(prefix) :]
                    if member.name.startswith(prefix)
                    else ""
                )
                if (
                    not member.isfile()
                    or not member.name.startswith(prefix)
                    or short_name in {"", ".", ".."}
                    or "/" in short_name
                    or member.mode != 0o644
                    or member.mtime != SOURCE_DATE_EPOCH
                    or member.uid != 0
                    or member.gid != 0
                    or short_name in members
                ):
                    raise RuntimeError("source archive contains a noncanonical member")
                reader = archive.extractfile(member)
                if reader is None:
                    raise RuntimeError("source archive member cannot be read")
                members[short_name] = reader.read()
    except (tarfile.TarError, OSError) as error:
        raise RuntimeError("source archive is invalid") from error
    return members


def _verify_checksum_file(payloads: Mapping[str, bytes]) -> None:
    expected = "".join(
        f"{_sha256(payloads[name])}  {name}\n"
        for name in sorted(payloads)
        if name != "SHA256SUMS"
    ).encode("ascii")
    if payloads.get("SHA256SUMS") != expected:
        raise RuntimeError("source archive checksum ledger is incorrect")


def _materialize(payloads: Mapping[str, bytes], root: Path) -> None:
    root.mkdir(parents=True, exist_ok=False)
    for name, payload in payloads.items():
        if "/" in name or name in {"", ".", ".."}:
            raise RuntimeError("unsafe source package member")
        submission.common._write_bytes(root / name, payload)


def _rebuild_from_archive(
    payloads: Mapping[str, bytes],
    *,
    temporary_root: Path,
    tools: Mapping[str, str],
) -> dict[str, str]:
    source = temporary_root / "source"
    _materialize(payloads, source)
    environment = dict(os.environ)
    environment.update(
        {
            "BIBINPUTS": f"{source}{os.pathsep}",
            "FORCE_SOURCE_DATE": "1",
            "LC_ALL": "C",
            "SOURCE_DATE_EPOCH": str(SOURCE_DATE_EPOCH),
            "TEXINPUTS": f"{source}{os.pathsep}",
            "TZ": "UTC",
        }
    )
    hashes: dict[str, str] = {}
    for label, tex_name in (
        ("main", submission.MAIN_TEX.name),
        ("supplement", submission.SUPPLEMENT_TEX.name),
    ):
        build = temporary_root / f"build-{label}"
        build.mkdir(parents=True, exist_ok=False)
        submission.common._run_checked(
            [
                tools["latexmk"],
                "-pdf",
                "-g",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                f"-outdir={build}",
                tex_name,
            ],
            cwd=source,
            env=environment,
            label=f"source archive {label} rebuild",
        )
        pdf = build / f"{Path(tex_name).stem}.pdf"
        log = build / f"{Path(tex_name).stem}.log"
        submission.common._audit_tex_log(
            log.read_bytes(),
            label=f"source archive {label} TeX log",
        )
        submission.common._audit_pdf(
            pdf,
            tools=tools,
            label=f"source archive {label}",
        )
        extracted = submission.common._run_checked(
            [tools["pdftotext"], "-enc", "UTF-8", str(pdf), "-"],
            label=f"source archive {label} text audit",
        ).stdout.decode("utf-8")
        submission._audit_reader_text(
            extracted,
            label=f"source archive {label} PDF",
        )
        hashes[label] = submission._sha256(pdf)
    return hashes


def _manifest_payload(
    *,
    archive: bytes,
    payloads: Mapping[str, bytes],
    snapshots: Mapping[str, submission.common.FileSnapshot],
    rebuilt: Mapping[str, str],
) -> dict[str, Any]:
    expected_pdfs = {
        "main": submission._sha256(submission.FINAL_MAIN_PDF),
        "supplement": submission._sha256(submission.FINAL_SUPPLEMENT_PDF),
    }
    if dict(rebuilt) != expected_pdfs:
        raise RuntimeError("source archive rebuild differs from the published PDFs")
    source_keys = (
        "manuscript/encounter_multimodal_prr_submission.tex",
        "manuscript/encounter_multimodal_prr_submission_supplement.tex",
        "manuscript/exact_m_theorem_spine.tex",
        "manuscript/exact_m_theorem_full_proof.tex",
        "manuscript/references.bib",
    )
    return {
        "archive": {
            "byte_count": len(archive),
            "path": "output/source/encounter_multimodal_prr_submission_source.tar.gz",
            "root": ARCHIVE_ROOT,
            "sha256": _sha256(archive),
        },
        "build_inputs": {
            "code/compile_theorem_first_submission.py": snapshots[
                "code/compile_theorem_first_submission.py"
            ].sha256,
            "code/compile_theorem_first_working.py": snapshots[
                "code/compile_theorem_first_working.py"
            ].sha256,
            "code/package_theorem_first_submission_source.py": _sha256(
                HERE.read_bytes()
            ),
        },
        "entries": {
            name: {
                "byte_count": len(payload),
                "mode": "0644",
                "sha256": _sha256(payload),
            }
            for name, payload in sorted(payloads.items())
        },
        "published_pdf_sha256": expected_pdfs,
        "schema_version": SCHEMA_VERSION,
        "source_inputs": {
            key: snapshots[key].sha256 for key in source_keys
        },
        "validation": {
            "archive_rebuilt_main_pdf_byte_identically": True,
            "archive_rebuilt_supplement_pdf_byte_identically": True,
            "deterministic_archive_rebuilds": True,
            "forbidden_reader_markers": 0,
            "safe_regular_members_only": True,
            "sha256_ledger_valid": True,
        },
    }


def _freshness_errors(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if not ARCHIVE.is_file():
        errors.append("source archive is missing")
        return tuple(errors)
    archive = ARCHIVE.read_bytes()
    record = payload.get("archive")
    if not isinstance(record, Mapping):
        errors.append("archive record is missing")
    else:
        if record.get("sha256") != _sha256(archive):
            errors.append("archive hash mismatch")
        if record.get("byte_count") != len(archive):
            errors.append("archive byte count mismatch")
    try:
        members = _read_archive(archive)
        _verify_checksum_file(members)
    except RuntimeError as error:
        errors.append(str(error))
        members = {}
    recorded_entries = payload.get("entries")
    observed_entries = {
        name: {
            "byte_count": len(value),
            "mode": "0644",
            "sha256": _sha256(value),
        }
        for name, value in sorted(members.items())
    }
    if recorded_entries != observed_entries:
        errors.append("archive entry ledger mismatch")
    snapshots = submission._snapshot_sources()
    expected_source_keys = {
        "manuscript/encounter_multimodal_prr_submission.tex",
        "manuscript/encounter_multimodal_prr_submission_supplement.tex",
        "manuscript/exact_m_theorem_spine.tex",
        "manuscript/exact_m_theorem_full_proof.tex",
        "manuscript/references.bib",
    }
    recorded_inputs = payload.get("source_inputs")
    if (
        not isinstance(recorded_inputs, Mapping)
        or set(recorded_inputs) != expected_source_keys
    ):
        errors.append("source input ledger is missing")
    else:
        for key, digest in recorded_inputs.items():
            if key not in snapshots or snapshots[key].sha256 != digest:
                errors.append(f"source input hash mismatch: {key}")
    expected_build_inputs = {
        "code/compile_theorem_first_submission.py": snapshots[
            "code/compile_theorem_first_submission.py"
        ].sha256,
        "code/compile_theorem_first_working.py": snapshots[
            "code/compile_theorem_first_working.py"
        ].sha256,
        "code/package_theorem_first_submission_source.py": _sha256(
            HERE.read_bytes()
        ),
    }
    if payload.get("build_inputs") != expected_build_inputs:
        errors.append("build input ledger mismatch")
    expected_pdfs = {
        "main": submission._sha256(submission.FINAL_MAIN_PDF),
        "supplement": submission._sha256(submission.FINAL_SUPPLEMENT_PDF),
    }
    if payload.get("published_pdf_sha256") != expected_pdfs:
        errors.append("published PDF hash ledger mismatch")
    return tuple(errors)


def build_and_publish() -> dict[str, Any]:
    compile_manifest = json.loads(submission.MANIFEST.read_text(encoding="utf-8"))
    freshness = submission._manifest_freshness_errors(compile_manifest)
    if freshness:
        raise RuntimeError("submission compile manifest is stale: " + "; ".join(freshness))
    snapshots = submission._snapshot_sources()
    submission._validate_terminal_receipt(snapshots)
    payloads = _source_payloads(snapshots)
    first = _archive_bytes(payloads)
    second = _archive_bytes(payloads)
    if first != second:
        raise RuntimeError("source archive rebuild is not byte-identical")
    readback = _read_archive(first)
    if readback != payloads:
        raise RuntimeError("source archive readback differs from staged sources")
    _verify_checksum_file(readback)
    tools = submission.common._required_tools()
    with tempfile.TemporaryDirectory(prefix="theorem-source-package-") as name:
        temporary_root = Path(name)
        rebuilt = _rebuild_from_archive(
            readback,
            temporary_root=temporary_root / "rebuild",
            tools=tools,
        )
        manifest = _manifest_payload(
            archive=first,
            payloads=payloads,
            snapshots=snapshots,
            rebuilt=rebuilt,
        )
        stage = temporary_root / "publication"
        staged_archive = stage / ARCHIVE.name
        staged_manifest = stage / MANIFEST.name
        submission.common._write_bytes(staged_archive, first)
        submission.common._write_bytes(
            staged_manifest,
            (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        submission.common._publish_transaction(
            {
                ARCHIVE: staged_archive,
                MANIFEST: staged_manifest,
            }
        )
    return manifest


def main() -> None:
    payload = build_and_publish()
    print(
        "Published clean theorem source package: "
        f"{payload['archive']['sha256']}"
    )


if __name__ == "__main__":
    main()
