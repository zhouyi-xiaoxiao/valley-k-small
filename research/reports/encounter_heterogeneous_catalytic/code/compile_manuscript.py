#!/usr/bin/env python3
"""Compile and audit the encounter manuscript with the local TeX Live runtime."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from vkcore.provenance import build_artifact_manifest, file_sha256, write_manifest

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
MANUSCRIPT = REPORT / "manuscript"
DATA = REPORT / "artifacts" / "data"
LOGS = REPORT / "artifacts" / "logs"
MAIN_TEX = MANUSCRIPT / "encounter_modality_jcp.tex"
SUPPLEMENT_TEX = MANUSCRIPT / "encounter_modality_supplement.tex"
BIB = MANUSCRIPT / "references.bib"
ALT_TEXT = MANUSCRIPT / "figure_table_alt_text.txt"
SUBMISSION_METADATA = MANUSCRIPT / "SUBMISSION_METADATA_REQUIRED.md"
MAIN_PDF = MANUSCRIPT / "encounter_modality_jcp.pdf"
SUPPLEMENT_PDF = MANUSCRIPT / "encounter_modality_supplement.pdf"
MAIN_PDF_TITLE = (
    "Spectral diagnostics and local fixed-budget sensitivity of critical points in finite encounter-reaction models"
)
SUPPLEMENT_PDF_TITLE = (
    "Supplemental Material: Spectral diagnostics and local fixed-budget sensitivity of critical points in finite encounter-reaction models"
)
EXPECTED_PDF_AUTHOR = "Xiaoxiao Zhouyi and Luca Giuggioli"
SOURCE_DATE_EPOCH = 1783728000
DOCUMENT_SPECS = (
    {
        "role": "main",
        "tex": MAIN_TEX,
        "pdf": MAIN_PDF,
        "log": LOGS / "manuscript_latexmk.log",
        "title": MAIN_PDF_TITLE,
    },
    {
        "role": "supplement",
        "tex": SUPPLEMENT_TEX,
        "pdf": SUPPLEMENT_PDF,
        "log": LOGS / "supplement_latexmk.log",
        "title": SUPPLEMENT_PDF_TITLE,
    },
)
DATA.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)


def _figure_dependencies(source: str) -> list[Path]:
    dependencies: list[Path] = []
    for name in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", source):
        candidate = Path(name)
        if candidate.suffix:
            paths = [REPORT / "artifacts" / "figures" / candidate]
        else:
            paths = [
                REPORT / "artifacts" / "figures" / f"{candidate}.pdf",
                REPORT / "artifacts" / "figures" / f"{candidate}.png",
            ]
        existing = next((path for path in paths if path.is_file()), None)
        if existing is None:
            raise FileNotFoundError(f"manuscript figure is missing: {name}")
        dependencies.append(existing)
    return dependencies


def _pdf_info(path: Path) -> dict[str, str]:
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo is None:
        raise FileNotFoundError("pdfinfo is not on PATH")
    process = subprocess.run(
        (pdfinfo, str(path)),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    info: dict[str, str] = {}
    for line in process.stdout.splitlines():
        key, separator, value = line.partition(":")
        if separator:
            info[key.strip()] = value.strip()
    return info


def _font_audit(path: Path) -> dict[str, object]:
    pdffonts = shutil.which("pdffonts")
    if pdffonts is None:
        raise FileNotFoundError("pdffonts is not on PATH")
    rows = subprocess.run(
        (pdffonts, str(path)),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.splitlines()[2:]
    rows = [row for row in rows if row.strip()]
    type3_rows = [row for row in rows if "Type 3" in row]
    unembedded_rows = [
        row for row in rows if re.split(r"\s+", row.strip())[-5] != "yes"
    ]
    if not rows or type3_rows or unembedded_rows:
        raise RuntimeError(
            "PDF font gate failed: "
            f"rows={len(rows)}, type3={len(type3_rows)}, "
            f"unembedded={len(unembedded_rows)}"
        )
    return {
        "font_rows": len(rows),
        "type3_rows": len(type3_rows),
        "unembedded_rows": len(unembedded_rows),
    }


FORBIDDEN_LOG_PATTERNS = {
    "undefined_references": r"There were undefined references",
    "undefined_citations": r"Citation .* undefined",
    "overfull_boxes": r"Overfull \\[hv]box",
    "missing_files": r"LaTeX Error: File .* not found",
    "pdf_string_warnings": r"Package hyperref Warning: Token not allowed in a PDF string",
}


def _compile_document(
    *,
    latexmk: str,
    role: str,
    tex: Path,
    final_pdf: Path,
    run_log: Path,
    expected_title: str,
) -> dict[str, object]:
    """Compile and audit one independently submitted PDF."""

    source = tex.read_text(encoding="utf-8")
    figures = _figure_dependencies(source)
    table_count = len(re.findall(r"\\begin\{table\*?\}", source))

    with tempfile.TemporaryDirectory(prefix=f"{tex.stem}_") as directory:
        build = Path(directory)
        command = (
            latexmk,
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-outdir={build}",
            tex.name,
        )
        process = subprocess.run(
            command,
            cwd=MANUSCRIPT,
            env={
                **os.environ,
                "SOURCE_DATE_EPOCH": str(SOURCE_DATE_EPOCH),
                "FORCE_SOURCE_DATE": "1",
                "TZ": "UTC",
            },
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        run_log.write_text(process.stdout, encoding="utf-8")
        if process.returncode:
            tail = "\n".join(process.stdout.splitlines()[-80:])
            raise RuntimeError(f"{role} latexmk failed:\n{tail}")

        built_pdf = build / final_pdf.name
        built_log = build / f"{tex.stem}.log"
        if not built_pdf.is_file() or not built_log.is_file():
            raise RuntimeError(
                f"{role} latexmk succeeded without the expected PDF/log"
            )
        log_text = built_log.read_text(encoding="utf-8", errors="replace")
        warning_counts = {
            name: len(re.findall(pattern, log_text))
            for name, pattern in FORBIDDEN_LOG_PATTERNS.items()
        }
        if any(warning_counts.values()):
            raise RuntimeError(
                f"{role} manuscript warning gate failed: {warning_counts}"
            )
        shutil.copy2(built_pdf, final_pdf)

    pdf_info = _pdf_info(final_pdf)
    pages = int(pdf_info.get("Pages", "-1"))
    if pages <= 0:
        raise RuntimeError(f"invalid {role} PDF page count: {pages}")
    if pdf_info.get("Title") != expected_title:
        raise RuntimeError(
            f"{role} PDF title metadata is missing or stale: "
            f"{pdf_info.get('Title')!r}"
        )
    if pdf_info.get("Author") != EXPECTED_PDF_AUTHOR:
        raise RuntimeError(
            f"{role} PDF author metadata is missing or stale: "
            f"{pdf_info.get('Author')!r}"
        )
    if not pdf_info.get("Subject") or not pdf_info.get("Keywords"):
        raise RuntimeError(f"{role} PDF subject/keyword metadata is missing")

    return {
        "role": role,
        "tex": str(tex.relative_to(REPO)),
        "pdf": str(final_pdf.relative_to(REPO)),
        "log": str(run_log.relative_to(REPO)),
        "figure_count": len(figures),
        "figures": [str(path.relative_to(REPO)) for path in figures],
        "table_count": table_count,
        "pages": pages,
        "pdf_metadata": {
            key: pdf_info[key]
            for key in ("Title", "Author", "Subject", "Keywords")
        },
        "font_audit": _font_audit(final_pdf),
        "pdf_bytes": final_pdf.stat().st_size,
        "pdf_sha256": file_sha256(final_pdf),
        "warning_counts": warning_counts,
    }


def main() -> None:
    latexmk = shutil.which("latexmk")
    if latexmk is None:
        raise FileNotFoundError("latexmk is not on PATH")
    required = (
        MAIN_TEX,
        SUPPLEMENT_TEX,
        BIB,
        ALT_TEXT,
        SUBMISSION_METADATA,
    )
    if not all(path.is_file() for path in required):
        raise FileNotFoundError(
            "main/Supplement TeX, bibliography, alt text, or metadata gate is missing"
        )

    documents = [
        _compile_document(
            latexmk=latexmk,
            role=str(spec["role"]),
            tex=Path(spec["tex"]),
            final_pdf=Path(spec["pdf"]),
            run_log=Path(spec["log"]),
            expected_title=str(spec["title"]),
        )
        for spec in DOCUMENT_SPECS
    ]
    main_document = documents[0]
    report_path = DATA / "manuscript_compile.json"
    report = {
        "bibliography": str(BIB.relative_to(REPO)),
        "accessibility_alt_text": str(ALT_TEXT.relative_to(REPO)),
        "submission_metadata_gate": str(SUBMISSION_METADATA.relative_to(REPO)),
        "documents": documents,
        "latexmk": latexmk,
        "source_date_epoch": SOURCE_DATE_EPOCH,
    }
    # Preserve the original single-manuscript report surface as a view of the
    # main article while exposing both independent submission documents.
    for key in (
        "tex",
        "figure_count",
        "figures",
        "pages",
        "pdf_metadata",
        "font_audit",
        "pdf_bytes",
        "pdf_sha256",
        "warning_counts",
    ):
        report[key] = main_document[key]
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    figure_inputs: list[Path] = []
    seen_figures: set[Path] = set()
    for document in documents:
        for relative in document["figures"]:
            path = REPO / str(relative)
            if path not in seen_figures:
                seen_figures.add(path)
                figure_inputs.append(path)

    metadata_gates = {
        document["role"]: {
            "title": document["pdf_metadata"]["Title"],
            "author": EXPECTED_PDF_AUTHOR,
            "subject_and_keywords_required": True,
        }
        for document in documents
    }
    manifest = build_artifact_manifest(
        repo_root=REPO,
        generator=str(HERE.relative_to(REPO)),
        command=[sys.executable, str(HERE.relative_to(REPO))],
        model_spec={
            "documentclass": "revtex4-2 aps,pre,reprint",
            "documents": ["main", "supplement"],
            "independent_auxiliary_files": True,
            "warning_gate": FORBIDDEN_LOG_PATTERNS,
            "pdf_metadata_gate": metadata_gates,
            "pdf_font_gate": "all fonts embedded; Type 3 forbidden",
        },
        inputs=[
            MAIN_TEX,
            SUPPLEMENT_TEX,
            BIB,
            ALT_TEXT,
            SUBMISSION_METADATA,
            *figure_inputs,
        ],
        dependencies=[REPO / "packages" / "vkcore" / "src" / "vkcore" / "provenance.py"],
        outputs=[
            MAIN_PDF,
            SUPPLEMENT_PDF,
            report_path,
            LOGS / "manuscript_latexmk.log",
            LOGS / "supplement_latexmk.log",
        ],
    )
    write_manifest(DATA / "manuscript_compile.manifest.json", manifest)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
