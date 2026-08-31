#!/usr/bin/env python3
"""Reproducibly compile and audit the theorem-first PRR working set.

This driver is deliberately independent of ``compile_manuscript.py`` and its
positive-budget numerical evidence.  It builds only the theorem-first main
text and supplement from a closed source snapshot, twice each, and publishes
the checked working set with rollback on any replacement failure.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
MANUSCRIPT = REPORT / "manuscript"
DATA = REPORT / "artifacts" / "data"
LOGS = REPORT / "artifacts" / "logs"
OUTPUT_PDF = REPORT / "output" / "pdf"

MAIN_TEX = MANUSCRIPT / "encounter_multimodal_prr_theorem_first_working.tex"
SUPPLEMENT_TEX = MANUSCRIPT / "encounter_multimodal_prr_supplement.tex"
EXACT_M_SPINE_TEX = MANUSCRIPT / "exact_m_theorem_spine.tex"
EXACT_M_FULL_PROOF_TEX = MANUSCRIPT / "exact_m_theorem_full_proof.tex"
REFERENCES_BIB = MANUSCRIPT / "references.bib"

FINAL_MAIN_PDF = OUTPUT_PDF / "encounter_multimodal_prr_theorem_first_working.pdf"
FINAL_SUPPLEMENT_PDF = OUTPUT_PDF / "encounter_multimodal_prr_theorem_first_supplement_working.pdf"
MAIN_TEX_LOG = LOGS / "theorem_first_working_main_tex.log"
MAIN_LATEXMK_LOG = LOGS / "theorem_first_working_main_latexmk.log"
SUPPLEMENT_TEX_LOG = LOGS / "theorem_first_working_supplement_tex.log"
SUPPLEMENT_LATEXMK_LOG = LOGS / "theorem_first_working_supplement_latexmk.log"
MANIFEST = DATA / "theorem_first_working_compile.json"

SOURCE_DATE_EPOCH = "1783987200"
EXPECTED_MEDIA_BOX = (0.0, 0.0, 612.0, 792.0)
MEDIA_BOX_TOLERANCE = 0.01
RELEASE_ELIGIBLE = False
SCHEMA_VERSION = 3


@dataclass(frozen=True)
class FileSnapshot:
    """Stable bytes and identity for one ordinary, nonsymlink file."""

    path: Path
    sha256: str
    payload: bytes


@dataclass(frozen=True)
class BuildRun:
    """Checked artifacts from one isolated LaTeX build."""

    pdf: Path
    pdf_sha256: str
    tex_log: bytes
    latexmk_log: bytes
    pdf_audit: dict[str, Any]


def _required_source_paths() -> dict[str, Path]:
    """Return the complete and intentionally small theorem-first input set."""

    return {
        "manuscript/encounter_multimodal_prr_theorem_first_working.tex": MAIN_TEX,
        "manuscript/encounter_multimodal_prr_supplement.tex": SUPPLEMENT_TEX,
        "manuscript/exact_m_theorem_spine.tex": EXACT_M_SPINE_TEX,
        "manuscript/exact_m_theorem_full_proof.tex": EXACT_M_FULL_PROOF_TEX,
        "manuscript/references.bib": REFERENCES_BIB,
        "code/compile_theorem_first_working.py": HERE,
    }


def _published_file_paths() -> dict[str, Path]:
    """Return published files whose bytes can be pinned by the manifest."""

    return {
        "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf": FINAL_MAIN_PDF,
        (
            "output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf"
        ): FINAL_SUPPLEMENT_PDF,
        "artifacts/logs/theorem_first_working_main_tex.log": MAIN_TEX_LOG,
        "artifacts/logs/theorem_first_working_main_latexmk.log": MAIN_LATEXMK_LOG,
        "artifacts/logs/theorem_first_working_supplement_tex.log": SUPPLEMENT_TEX_LOG,
        ("artifacts/logs/theorem_first_working_supplement_latexmk.log"): SUPPLEMENT_LATEXMK_LOG,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _payload_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _snapshot_regular_file(path: Path, *, label: str) -> FileSnapshot:
    """Read a file without following a final-component symlink or accepting races."""

    try:
        before = path.lstat()
    except FileNotFoundError as error:
        raise FileNotFoundError(f"required theorem-first {label} is missing: {path}") from error
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise RuntimeError(f"required theorem-first {label} is not an ordinary nonsymlink: {path}")

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise RuntimeError(f"required theorem-first {label} is not a regular file: {path}")
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise RuntimeError(f"required theorem-first {label} changed before it was read: {path}")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            payload = handle.read()
    finally:
        os.close(descriptor)

    after = path.lstat()
    before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if before_identity != after_identity or len(payload) != opened.st_size:
        raise RuntimeError(f"required theorem-first {label} changed while it was read: {path}")
    return FileSnapshot(path=path, sha256=_payload_sha256(payload), payload=payload)


def _validate_text_source(snapshot: FileSnapshot, *, label: str) -> None:
    try:
        source = snapshot.payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"required theorem-first {label} is not valid UTF-8") from error
    controls = re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", source)
    if controls:
        codes = ", ".join(sorted({f"U+{ord(value):04X}" for value in controls}))
        raise RuntimeError(f"required theorem-first {label} contains control characters: {codes}")
    if "\ufffd" in source:
        raise RuntimeError(f"required theorem-first {label} contains a replacement character")


def _snapshot_sources() -> dict[str, FileSnapshot]:
    snapshots: dict[str, FileSnapshot] = {}
    for relative, path in _required_source_paths().items():
        snapshot = _snapshot_regular_file(path, label=relative)
        _validate_text_source(snapshot, label=relative)
        snapshots[relative] = snapshot
    return snapshots


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as reader, target.open("wb") as writer:
        shutil.copyfileobj(reader, writer)
        writer.flush()
        os.fsync(writer.fileno())


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _required_tools() -> dict[str, str]:
    tools: dict[str, str] = {}
    for name in ("latexmk", "pdfinfo", "pdffonts", "pdftotext", "gs"):
        executable = shutil.which(name)
        if executable is None:
            raise FileNotFoundError(f"{name} is required for the theorem-first build")
        tools[name] = executable
    return tools


def _run_checked(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    label: str,
) -> subprocess.CompletedProcess[bytes]:
    process = subprocess.run(
        command,
        cwd=cwd,
        env=None if env is None else dict(env),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        combined = process.stdout + b"\n" + process.stderr
        tail = combined[-6000:].decode("utf-8", errors="replace")
        raise RuntimeError(f"{label} failed with exit code {process.returncode}:\n{tail}")
    return process


def _audit_tex_log(payload: bytes, *, label: str) -> None:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"{label} is not valid UTF-8") from error
    forbidden = {
        "undefined reference": r"(?:LaTeX Warning: )?Reference .+ undefined",
        "undefined references": r"There were undefined references",
        "undefined citation": r"(?:LaTeX Warning: )?Citation .+ undefined",
        "undefined citations": r"There were undefined citations",
        "overfull box": r"Overfull \\[hv]box",
        "multiply-defined label": r"multiply defined",
        "unresolved rerun request": r"Label\(s\) may have changed",
        "LaTeX error": r"! (?:LaTeX|Package [^\n]+) Error",
        "TeX error": r"^! ",
        "emergency stop": r"Emergency stop|Fatal error occurred",
    }
    for description, pattern in forbidden.items():
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            raise RuntimeError(f"{label} contains {description}")


def _parse_pdfinfo(payload: bytes, *, label: str) -> dict[str, str]:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"{label} pdfinfo output is not valid UTF-8") from error
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def _page_media_box(
    pdf: Path,
    *,
    page: int,
    pdfinfo: str,
    label: str,
) -> tuple[float, float, float, float]:
    process = _run_checked(
        [pdfinfo, "-box", "-f", str(page), "-l", str(page), str(pdf)],
        label=f"{label} page-{page} MediaBox check",
    )
    text = process.stdout.decode("utf-8", errors="strict")
    match = re.search(
        rf"^Page\s+{page}\s+MediaBox:\s+"
        r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+"
        r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*$",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError(f"{label} page {page} has no parseable MediaBox")
    box = tuple(float(value) for value in match.groups())
    if not all(math.isfinite(value) for value in box):
        raise RuntimeError(f"{label} page {page} has a non-finite MediaBox")
    if any(
        abs(observed - expected) > MEDIA_BOX_TOLERANCE
        for observed, expected in zip(box, EXPECTED_MEDIA_BOX, strict=True)
    ):
        raise RuntimeError(
            f"{label} page {page} MediaBox {box} is not expected letter {EXPECTED_MEDIA_BOX}"
        )
    return box  # type: ignore[return-value]


def _font_audit(pdf: Path, *, pdffonts: str, label: str) -> dict[str, Any]:
    process = _run_checked([pdffonts, str(pdf)], label=f"{label} font audit")
    lines = process.stdout.decode("utf-8", errors="strict").splitlines()
    rows = [line for line in lines[2:] if line.strip()]
    if not rows:
        raise RuntimeError(f"{label} exposes no auditable PDF fonts")
    for row in rows:
        tokens = row.split()
        if len(tokens) < 7:
            raise RuntimeError(f"{label} has an unparseable pdffonts row: {row}")
        if "Type 3" in row:
            raise RuntimeError(f"{label} contains a forbidden Type 3 font")
        if tokens[-5].lower() != "yes":
            raise RuntimeError(f"{label} contains an unembedded font: {row}")
    return {"all_fonts_embedded": True, "font_count": len(rows), "type3_fonts": 0}


def _text_audit(pdf: Path, *, pdftotext: str, label: str) -> dict[str, Any]:
    process = _run_checked(
        [pdftotext, "-enc", "UTF-8", str(pdf), "-"],
        label=f"{label} text extraction",
    )
    try:
        text = process.stdout.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"{label} extracted text is not valid UTF-8") from error
    if "\x00" in text or "\ufffd" in text:
        raise RuntimeError(f"{label} extracted text contains NUL or replacement characters")
    if not text.strip():
        raise RuntimeError(f"{label} extracted text is empty")
    return {
        "characters": len(text),
        "nul_or_replacement_characters": 0,
    }


def _audit_pdf(pdf: Path, *, tools: Mapping[str, str], label: str) -> dict[str, Any]:
    snapshot = _snapshot_regular_file(pdf, label=f"{label} PDF")
    if not snapshot.payload.startswith(b"%PDF-"):
        raise RuntimeError(f"{label} does not begin with a PDF signature")

    info_process = _run_checked(
        [tools["pdfinfo"], "-box", str(pdf)],
        label=f"{label} pdfinfo audit",
    )
    info = _parse_pdfinfo(info_process.stdout, label=label)
    try:
        pages = int(info["Pages"])
    except (KeyError, ValueError) as error:
        raise RuntimeError(f"{label} has no valid page count") from error
    if pages < 1:
        raise RuntimeError(f"{label} has an empty page count")
    if info.get("Encrypted", "").lower() != "no":
        raise RuntimeError(f"{label} is encrypted or has no explicit encryption audit")
    if info.get("JavaScript", "").lower() != "no":
        raise RuntimeError(f"{label} contains JavaScript or has no explicit JavaScript audit")

    media_boxes = [
        _page_media_box(
            pdf,
            page=page,
            pdfinfo=tools["pdfinfo"],
            label=label,
        )
        for page in range(1, pages + 1)
    ]
    _run_checked(
        [
            tools["gs"],
            "-q",
            "-dSAFER",
            "-dNOPAUSE",
            "-dBATCH",
            "-sDEVICE=nullpage",
            str(pdf),
        ],
        label=f"{label} Ghostscript parse",
    )
    font_audit = _font_audit(pdf, pdffonts=tools["pdffonts"], label=label)
    text_audit = _text_audit(pdf, pdftotext=tools["pdftotext"], label=label)
    return {
        "all_page_media_boxes_points": [list(box) for box in media_boxes],
        "encrypted": False,
        "font_audit": font_audit,
        "ghostscript_parse": True,
        "javascript": False,
        "media_box_points": list(media_boxes[0]),
        "pages": pages,
        "text_audit": text_audit,
    }


def _materialize_source_tree(
    snapshots: Mapping[str, FileSnapshot],
    source_root: Path,
) -> None:
    source_root.mkdir(parents=True, exist_ok=False)
    for relative in (
        "manuscript/encounter_multimodal_prr_theorem_first_working.tex",
        "manuscript/encounter_multimodal_prr_supplement.tex",
        "manuscript/exact_m_theorem_spine.tex",
        "manuscript/exact_m_theorem_full_proof.tex",
        "manuscript/references.bib",
    ):
        _write_bytes(source_root / Path(relative).name, snapshots[relative].payload)


def _build_document(
    snapshots: Mapping[str, FileSnapshot],
    *,
    run_root: Path,
    tex_name: str,
    tools: Mapping[str, str],
    label: str,
) -> BuildRun:
    source_root = run_root / "source"
    build_root = run_root / "build"
    _materialize_source_tree(snapshots, source_root)
    build_root.mkdir(parents=True, exist_ok=False)

    environment = dict(os.environ)
    environment.update(
        {
            "BIBINPUTS": f"{source_root}{os.pathsep}",
            "FORCE_SOURCE_DATE": "1",
            "LC_ALL": "C",
            "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH,
            "TEXINPUTS": f"{source_root}{os.pathsep}",
            "TZ": "UTC",
        }
    )
    process = _run_checked(
        [
            tools["latexmk"],
            "-pdf",
            "-g",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            f"-outdir={build_root}",
            tex_name,
        ],
        cwd=source_root,
        env=environment,
        label=f"{label} latexmk build",
    )
    latexmk_log = process.stdout + process.stderr
    pdf = build_root / f"{Path(tex_name).stem}.pdf"
    tex_log_path = build_root / f"{Path(tex_name).stem}.log"
    tex_log_snapshot = _snapshot_regular_file(tex_log_path, label=f"{label} TeX log")
    _audit_tex_log(tex_log_snapshot.payload, label=f"{label} TeX log")
    pdf_audit = _audit_pdf(pdf, tools=tools, label=label)
    return BuildRun(
        pdf=pdf,
        pdf_sha256=_sha256(pdf),
        tex_log=tex_log_snapshot.payload,
        latexmk_log=latexmk_log,
        pdf_audit=pdf_audit,
    )


def _assert_identical(first: BuildRun, second: BuildRun, *, label: str) -> None:
    if first.pdf_sha256 != second.pdf_sha256:
        raise RuntimeError(
            f"{label} isolated PDF rebuilds are not byte-identical: "
            f"{first.pdf_sha256} != {second.pdf_sha256}"
        )
    if first.pdf_audit != second.pdf_audit:
        raise RuntimeError(f"{label} isolated PDF audits disagree")


def _normalized_log_bundle(
    first: bytes,
    second: bytes,
    *,
    temporary_root: Path,
) -> bytes:
    def normalize(payload: bytes) -> bytes:
        # TeX hard-wraps long file names inside its log, including in the
        # middle of the random TemporaryDirectory basename.  Match each path
        # byte with an optional intervening line break so those wrapped forms
        # do not leak run-specific bytes into the published evidence logs.
        candidates = {
            str(temporary_root).encode("utf-8"),
            str(temporary_root.resolve()).encode("utf-8"),
            temporary_root.name.encode("utf-8"),
        }
        for candidate in sorted(candidates, key=len, reverse=True):
            wrapped_literal = rb"(?:\r?\n)?".join(re.escape(bytes([value])) for value in candidate)
            payload = re.sub(wrapped_literal, b"<TEMP_BUILD_ROOT>", payload)
        return payload

    return (
        b"===== isolated build 1 =====\n"
        + normalize(first)
        + b"\n===== isolated build 2 =====\n"
        + normalize(second)
    )


def _same_snapshots(
    before: Mapping[str, FileSnapshot],
    after: Mapping[str, FileSnapshot],
) -> bool:
    return {key: value.sha256 for key, value in before.items()} == {
        key: value.sha256 for key, value in after.items()
    }


def _latexmk_version(executable: str) -> str:
    process = _run_checked([executable, "-v"], label="latexmk version query")
    text = (process.stdout + process.stderr).decode("utf-8", errors="replace")
    return next((line.strip() for line in text.splitlines() if line.strip()), "latexmk")


def _manifest_payload(
    *,
    snapshots: Mapping[str, FileSnapshot],
    main: BuildRun,
    supplement: BuildRun,
    published_hashes: Mapping[str, str],
    latexmk_version: str,
) -> dict[str, Any]:
    driver_relative = "code/compile_theorem_first_working.py"

    def output_record(run: BuildRun, path: str) -> dict[str, Any]:
        return {
            "all_page_media_boxes_points": run.pdf_audit["all_page_media_boxes_points"],
            "byte_identical_rebuilds": True,
            "encrypted": False,
            "font_audit": run.pdf_audit["font_audit"],
            "ghostscript_parse": True,
            "javascript": False,
            "media_box_points": run.pdf_audit["media_box_points"],
            "pages": run.pdf_audit["pages"],
            "path": path,
            "sha256": run.pdf_sha256,
            "text_audit": run.pdf_audit["text_audit"],
        }

    published_outputs = [
        *_published_file_paths(),
        "artifacts/data/theorem_first_working_compile.json",
    ]
    return {
        "build": {
            "compiler": latexmk_version,
            "driver": driver_relative,
            "driver_sha256": snapshots[driver_relative].sha256,
            "isolated_builds": {"main": 2, "supplement": 2},
            "source_date_epoch": int(SOURCE_DATE_EPOCH),
        },
        "inputs": {key: value.sha256 for key, value in snapshots.items()},
        "outputs": {
            "main": output_record(
                main,
                "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf",
            ),
            "supplement": output_record(
                supplement,
                ("output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf"),
            ),
        },
        "positive_budget_evaluated": False,
        "positive_budget_scientific_values_read": False,
        "publication_transaction": {
            "all_checks_before_publish": True,
            "preflight_before_canonical_writes": True,
            "published_outputs": published_outputs,
            "same_directory_atomic_replace_with_rollback": True,
            "temporary_source_snapshot": True,
        },
        "published_files": dict(published_hashes),
        "release_eligible": RELEASE_ELIGIBLE,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_INTERNAL_THEOREM_FIRST_WORKING_SET",
        "validation": {
            "all_fonts_embedded": True,
            "byte_identical_main_rebuilds": True,
            "byte_identical_supplement_rebuilds": True,
            "ghostscript_parse": True,
            "overfull_boxes": 0,
            "text_extraction_replacement_or_nul_characters": 0,
            "type3_fonts": 0,
            "undefined_citations": 0,
            "undefined_references": 0,
        },
    }


def _manifest_freshness_errors(
    payload: Mapping[str, Any],
    *,
    source_paths: Mapping[str, Path] | None = None,
    published_paths: Mapping[str, Path] | None = None,
) -> tuple[str, ...]:
    """Return every stale or malformed pin in a theorem-first manifest."""

    sources = _required_source_paths() if source_paths is None else dict(source_paths)
    outputs = _published_file_paths() if published_paths is None else dict(published_paths)
    errors: list[str] = []
    if payload.get("release_eligible") is not False:
        errors.append("release_eligible is not fail-closed false")

    recorded_inputs = payload.get("inputs")
    if not isinstance(recorded_inputs, Mapping):
        errors.append("inputs is missing or malformed")
    else:
        if set(recorded_inputs) != set(sources):
            errors.append("input path set differs from the required source set")
        for relative, path in sources.items():
            if not path.is_file():
                errors.append(f"required input is missing: {relative}")
            elif recorded_inputs.get(relative) != _sha256(path):
                errors.append(f"input hash mismatch: {relative}")

    build = payload.get("build")
    driver_relative = "code/compile_theorem_first_working.py"
    if not isinstance(build, Mapping):
        errors.append("build metadata is missing or malformed")
    elif build.get("driver_sha256") != (
        _sha256(sources[driver_relative])
        if sources.get(driver_relative, Path()).is_file()
        else None
    ):
        errors.append("build driver hash mismatch")

    recorded_outputs = payload.get("published_files")
    if not isinstance(recorded_outputs, Mapping):
        errors.append("published_files is missing or malformed")
    else:
        if set(recorded_outputs) != set(outputs):
            errors.append("published path set differs from the required output set")
        for relative, path in outputs.items():
            if not path.is_file():
                errors.append(f"published output is missing: {relative}")
            elif recorded_outputs.get(relative) != _sha256(path):
                errors.append(f"published output hash mismatch: {relative}")
    return tuple(errors)


def _publish_transaction(
    staged_outputs: Mapping[Path, Path],
    *,
    replace: Callable[[os.PathLike[str] | str, os.PathLike[str] | str], None] = os.replace,
) -> None:
    """Atomically replace each checked file and roll back the set on any failure."""

    if not staged_outputs or len(staged_outputs) != len(set(staged_outputs)):
        raise RuntimeError("publication transaction has no outputs or duplicate targets")
    for target, staged in staged_outputs.items():
        if not staged.is_file():
            raise FileNotFoundError(f"staged publication output is missing: {staged}")
        if target.is_dir():
            raise IsADirectoryError(target)

    prepared: dict[Path, Path] = {}
    backups: dict[Path, Path | None] = {}
    existed: dict[Path, bool] = {}
    published: list[Path] = []
    touched_directories: set[Path] = set()
    try:
        for target, staged in staged_outputs.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            touched_directories.add(target.parent)
            incoming_descriptor, incoming_name = tempfile.mkstemp(
                prefix=f".{target.name}.incoming.", suffix=".tmp", dir=target.parent
            )
            incoming = Path(incoming_name)
            with os.fdopen(incoming_descriptor, "wb") as writer, staged.open("rb") as reader:
                shutil.copyfileobj(reader, writer)
                writer.flush()
                os.fsync(writer.fileno())
            prepared[target] = incoming
            existed[target] = target.exists()
            if existed[target]:
                backup_descriptor, backup_name = tempfile.mkstemp(
                    prefix=f".{target.name}.backup.", suffix=".tmp", dir=target.parent
                )
                backup = Path(backup_name)
                with os.fdopen(backup_descriptor, "wb") as writer, target.open("rb") as reader:
                    shutil.copyfileobj(reader, writer)
                    writer.flush()
                    os.fsync(writer.fileno())
                backups[target] = backup
            else:
                backups[target] = None

        for target in staged_outputs:
            replace(prepared[target], target)
            published.append(target)
        for directory in touched_directories:
            _fsync_directory(directory)
    except BaseException:
        rollback_errors: list[str] = []
        for target in reversed(published):
            try:
                backup = backups[target]
                if existed[target] and backup is not None:
                    replace(backup, target)
                    backups[target] = None
                else:
                    target.unlink(missing_ok=True)
            except BaseException as error:  # pragma: no cover - catastrophic filesystem failure
                rollback_errors.append(f"{target}: {error}")
        for directory in touched_directories:
            try:
                _fsync_directory(directory)
            except OSError as error:  # pragma: no cover - catastrophic filesystem failure
                rollback_errors.append(f"fsync {directory}: {error}")
        if rollback_errors:
            raise RuntimeError(
                "publication transaction failed and rollback was incomplete: "
                + "; ".join(rollback_errors)
            )
        raise
    finally:
        temporary_paths = [*prepared.values(), *(p for p in backups.values() if p is not None)]
        for path in temporary_paths:
            path.unlink(missing_ok=True)


def _build_and_publish() -> dict[str, Any]:
    snapshots = _snapshot_sources()
    tools = _required_tools()
    with tempfile.TemporaryDirectory(prefix="theorem-first-working-") as temporary_name:
        temporary_root = Path(temporary_name)
        main_first = _build_document(
            snapshots,
            run_root=temporary_root / "main-1",
            tex_name=MAIN_TEX.name,
            tools=tools,
            label="theorem-first main build 1",
        )
        main_second = _build_document(
            snapshots,
            run_root=temporary_root / "main-2",
            tex_name=MAIN_TEX.name,
            tools=tools,
            label="theorem-first main build 2",
        )
        supplement_first = _build_document(
            snapshots,
            run_root=temporary_root / "supplement-1",
            tex_name=SUPPLEMENT_TEX.name,
            tools=tools,
            label="theorem-first supplement build 1",
        )
        supplement_second = _build_document(
            snapshots,
            run_root=temporary_root / "supplement-2",
            tex_name=SUPPLEMENT_TEX.name,
            tools=tools,
            label="theorem-first supplement build 2",
        )
        _assert_identical(main_first, main_second, label="theorem-first main")
        _assert_identical(
            supplement_first,
            supplement_second,
            label="theorem-first supplement",
        )

        # Detect a concurrent source edit before constructing any canonical replacement.
        current_snapshots = _snapshot_sources()
        if not _same_snapshots(snapshots, current_snapshots):
            raise RuntimeError("theorem-first sources changed during the isolated builds")

        stage = temporary_root / "publication"
        staged_by_relative = {
            "output/pdf/encounter_multimodal_prr_theorem_first_working.pdf": (
                stage / FINAL_MAIN_PDF.name
            ),
            ("output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf"): stage
            / FINAL_SUPPLEMENT_PDF.name,
            "artifacts/logs/theorem_first_working_main_tex.log": (stage / MAIN_TEX_LOG.name),
            "artifacts/logs/theorem_first_working_main_latexmk.log": (
                stage / MAIN_LATEXMK_LOG.name
            ),
            "artifacts/logs/theorem_first_working_supplement_tex.log": (
                stage / SUPPLEMENT_TEX_LOG.name
            ),
            ("artifacts/logs/theorem_first_working_supplement_latexmk.log"): stage
            / SUPPLEMENT_LATEXMK_LOG.name,
        }
        _copy_file(
            main_first.pdf,
            staged_by_relative["output/pdf/encounter_multimodal_prr_theorem_first_working.pdf"],
        )
        _copy_file(
            supplement_first.pdf,
            staged_by_relative[
                "output/pdf/encounter_multimodal_prr_theorem_first_supplement_working.pdf"
            ],
        )
        _write_bytes(
            staged_by_relative["artifacts/logs/theorem_first_working_main_tex.log"],
            _normalized_log_bundle(
                main_first.tex_log,
                main_second.tex_log,
                temporary_root=temporary_root,
            ),
        )
        _write_bytes(
            staged_by_relative["artifacts/logs/theorem_first_working_main_latexmk.log"],
            _normalized_log_bundle(
                main_first.latexmk_log,
                main_second.latexmk_log,
                temporary_root=temporary_root,
            ),
        )
        _write_bytes(
            staged_by_relative["artifacts/logs/theorem_first_working_supplement_tex.log"],
            _normalized_log_bundle(
                supplement_first.tex_log,
                supplement_second.tex_log,
                temporary_root=temporary_root,
            ),
        )
        _write_bytes(
            staged_by_relative["artifacts/logs/theorem_first_working_supplement_latexmk.log"],
            _normalized_log_bundle(
                supplement_first.latexmk_log,
                supplement_second.latexmk_log,
                temporary_root=temporary_root,
            ),
        )
        published_hashes = {
            relative: _sha256(path) for relative, path in staged_by_relative.items()
        }
        manifest_payload = _manifest_payload(
            snapshots=snapshots,
            main=main_first,
            supplement=supplement_first,
            published_hashes=published_hashes,
            latexmk_version=_latexmk_version(tools["latexmk"]),
        )
        staged_manifest = stage / MANIFEST.name
        _write_bytes(
            staged_manifest,
            (json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )

        staged_outputs = {
            _published_file_paths()[relative]: path for relative, path in staged_by_relative.items()
        }
        staged_outputs[MANIFEST] = staged_manifest
        _publish_transaction(staged_outputs)
    return manifest_payload


def main() -> None:
    payload = _build_and_publish()
    print(
        "Published fail-closed theorem-first working set: "
        f"main={payload['outputs']['main']['sha256']} "
        f"supplement={payload['outputs']['supplement']['sha256']}"
    )


if __name__ == "__main__":
    main()
