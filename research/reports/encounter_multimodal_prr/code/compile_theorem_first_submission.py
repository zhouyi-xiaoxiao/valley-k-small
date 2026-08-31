#!/usr/bin/env python3
"""Build the reader-facing theorem branch selected by the terminal resource receipt."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping

import compile_theorem_first_working as common

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
MANUSCRIPT = REPORT / "manuscript"
DATA = REPORT / "artifacts" / "data"
LOGS = REPORT / "artifacts" / "logs"
OUTPUT_PDF = REPORT / "output" / "pdf"

MAIN_TEX = MANUSCRIPT / "encounter_multimodal_prr_submission.tex"
SUPPLEMENT_TEX = MANUSCRIPT / "encounter_multimodal_prr_submission_supplement.tex"
EXACT_M_SPINE_TEX = MANUSCRIPT / "exact_m_theorem_spine.tex"
EXACT_M_FULL_PROOF_TEX = MANUSCRIPT / "exact_m_theorem_full_proof.tex"
REFERENCES_BIB = MANUSCRIPT / "references.bib"
COMMON_BUILD_DRIVER = REPORT / "code" / "compile_theorem_first_working.py"
CANONICAL_RESOURCE = DATA / "rate_defined_tensor_f0_resource_v1.json"
TERMINAL_RECEIPT = DATA / "rate_defined_tensor_f0_resource_v1.json.resources.json"

FINAL_MAIN_PDF = OUTPUT_PDF / "encounter_multimodal_prr_submission.pdf"
FINAL_SUPPLEMENT_PDF = OUTPUT_PDF / "encounter_multimodal_prr_submission_supplement.pdf"
MAIN_TEX_LOG = LOGS / "theorem_first_submission_main_tex.log"
MAIN_LATEXMK_LOG = LOGS / "theorem_first_submission_main_latexmk.log"
SUPPLEMENT_TEX_LOG = LOGS / "theorem_first_submission_supplement_tex.log"
SUPPLEMENT_LATEXMK_LOG = LOGS / "theorem_first_submission_supplement_latexmk.log"
MANIFEST = DATA / "theorem_first_submission_compile.json"

SOURCE_DATE_EPOCH = "1784505600"
SCHEMA_VERSION = 1

EXPECTED_CANONICAL_SHA256 = (
    "0681015f350f9df702d32c4aaa712b89fce7aa742ebccb345a9336a5b64ad2b1"
)
EXPECTED_TERMINAL_RECEIPT_SHA256 = (
    "98ed3190c518614f5adf6a9d64933d847ab52bbf6cb4eb73c9635d4035a23061"
)
EXPECTED_PAYLOAD_BINDING_SHA256 = (
    "8453be4a115875c81e4ccd60208883afbfc2d3b4096337b7ffaf4db32e023f33"
)
EXPECTED_SCHEDULE_SHA256 = (
    "b42aa67fa9aa85e4c3c46577e3725ca616ba3ff3de156d77f976a99d0b380344"
)
EXPECTED_SPINE_SHA256 = (
    "79b0a4467a67999f605b8a5d8ec07e41a88c07edc8cdf1639ad6b8d4ce70658e"
)
EXPECTED_FULL_PROOF_SHA256 = (
    "a372b5a33d2203b8f3214a153f4aaf1e81497bf146c0ac1db1cfda97919c1c7b"
)
EXPECTED_TERMINAL_STATUS = "HOLD_F0_METHOD_OR_RESOURCE"
EXPECTED_FAILURE_REASONS = ("rss_cap_exceeded", "peak_footprint_cap_exceeded")

_PROOF_READER_REPLACEMENTS = {
    (
        b"This section proves the exact finite-mode statement used in the theorem-first\n"
        b"working paper."
    ): (
        b"This section proves the exact finite-mode statement used in the main\n"
        b"text."
    )
}

_FORBIDDEN_READER_PATTERNS = {
    "internal branch status": re.compile(r"\b(?:HOLD|PASS|F[0-3]|C[0-3])\b"),
    "internal iteration label": re.compile(r"\bround\b", re.I),
    "unfinished marker": re.compile(
        r"\bplaceholder\b|working\s+draft|working\s+paper|"
        r"not\s+a\s+submission|release_eligible",
        re.I,
    ),
}


def _required_source_paths() -> dict[str, Path]:
    return {
        "manuscript/encounter_multimodal_prr_submission.tex": MAIN_TEX,
        (
            "manuscript/encounter_multimodal_prr_submission_supplement.tex"
        ): SUPPLEMENT_TEX,
        "manuscript/exact_m_theorem_spine.tex": EXACT_M_SPINE_TEX,
        "manuscript/exact_m_theorem_full_proof.tex": EXACT_M_FULL_PROOF_TEX,
        "manuscript/references.bib": REFERENCES_BIB,
        "artifacts/data/rate_defined_tensor_f0_resource_v1.json": CANONICAL_RESOURCE,
        (
            "artifacts/data/rate_defined_tensor_f0_resource_v1.json.resources.json"
        ): TERMINAL_RECEIPT,
        "code/compile_theorem_first_working.py": COMMON_BUILD_DRIVER,
        "code/compile_theorem_first_submission.py": HERE,
    }


def _published_file_paths() -> dict[str, Path]:
    return {
        "output/pdf/encounter_multimodal_prr_submission.pdf": FINAL_MAIN_PDF,
        (
            "output/pdf/encounter_multimodal_prr_submission_supplement.pdf"
        ): FINAL_SUPPLEMENT_PDF,
        "artifacts/logs/theorem_first_submission_main_tex.log": MAIN_TEX_LOG,
        "artifacts/logs/theorem_first_submission_main_latexmk.log": MAIN_LATEXMK_LOG,
        (
            "artifacts/logs/theorem_first_submission_supplement_tex.log"
        ): SUPPLEMENT_TEX_LOG,
        (
            "artifacts/logs/theorem_first_submission_supplement_latexmk.log"
        ): SUPPLEMENT_LATEXMK_LOG,
    }


def _sha256(path: Path) -> str:
    return common._sha256(path)


def _snapshot_sources() -> dict[str, common.FileSnapshot]:
    snapshots: dict[str, common.FileSnapshot] = {}
    for relative, path in _required_source_paths().items():
        snapshot = common._snapshot_regular_file(path, label=relative)
        if path.suffix in {".tex", ".bib", ".py"}:
            common._validate_text_source(snapshot, label=relative)
        snapshots[relative] = snapshot
    return snapshots


def _json_object(payload: bytes, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not a JSON object")
    return value


def _validate_terminal_receipt(
    snapshots: Mapping[str, common.FileSnapshot],
) -> dict[str, Any]:
    canonical_key = "artifacts/data/rate_defined_tensor_f0_resource_v1.json"
    receipt_key = canonical_key + ".resources.json"
    canonical_snapshot = snapshots[canonical_key]
    receipt_snapshot = snapshots[receipt_key]
    if canonical_snapshot.sha256 != EXPECTED_CANONICAL_SHA256:
        raise RuntimeError("canonical resource hash does not match the terminal branch pin")
    if receipt_snapshot.sha256 != EXPECTED_TERMINAL_RECEIPT_SHA256:
        raise RuntimeError("terminal receipt hash does not match the terminal branch pin")

    canonical = _json_object(canonical_snapshot.payload, label="canonical resource")
    receipt = _json_object(receipt_snapshot.payload, label="terminal receipt")
    if canonical.get("schema") != "rate_defined_tensor_f0_resource_canonical_v1":
        raise RuntimeError("canonical resource schema is not the frozen schema")
    if canonical.get("status") != "CANONICAL_METHOD_EVIDENCE_AWAITING_RESOURCE_EVALUATION":
        raise RuntimeError("canonical resource has an unexpected status")
    if canonical.get("payload_binding_sha256") != EXPECTED_PAYLOAD_BINDING_SHA256:
        raise RuntimeError("canonical resource payload binding is not frozen")

    if receipt.get("schema") != "rate_defined_tensor_f0_resource_observation_v1":
        raise RuntimeError("terminal receipt schema is not the frozen schema")
    if receipt.get("status") != EXPECTED_TERMINAL_STATUS:
        raise RuntimeError("terminal receipt does not select the theorem-only branch")
    if tuple(receipt.get("failure_reasons", ())) != EXPECTED_FAILURE_REASONS:
        raise RuntimeError("terminal receipt failure reasons differ from the frozen reasons")
    if receipt.get("resource_caps_satisfied") is not False:
        raise RuntimeError("terminal receipt unexpectedly satisfies the resource caps")

    canonical_record = receipt.get("canonical_artifact")
    if not isinstance(canonical_record, dict):
        raise RuntimeError("terminal receipt has no canonical artifact record")
    if canonical_record.get("sha256") != canonical_snapshot.sha256:
        raise RuntimeError("terminal receipt does not bind the canonical resource bytes")
    if canonical_record.get("byte_count") != len(canonical_snapshot.payload):
        raise RuntimeError("terminal receipt canonical byte count is incorrect")
    if Path(str(canonical_record.get("absolute_path", ""))).resolve() != CANONICAL_RESOURCE.resolve():
        raise RuntimeError("terminal receipt names a different canonical resource path")

    schedule = receipt.get("schedule")
    if not isinstance(schedule, dict) or schedule.get("artifact_sha256") != (
        EXPECTED_SCHEDULE_SHA256
    ):
        raise RuntimeError("terminal receipt schedule hash is not frozen")
    if receipt.get("dependencies_before") != receipt.get("dependencies_after"):
        raise RuntimeError("terminal receipt dependencies changed during execution")
    dependencies = receipt.get("dependencies_before")
    if not isinstance(dependencies, dict) or not dependencies:
        raise RuntimeError("terminal receipt dependency pins are missing")
    for name, record in dependencies.items():
        if not isinstance(record, dict):
            raise RuntimeError(f"terminal receipt dependency {name} is malformed")
        if record.get("accepted") is not True or record.get("expected_sha256") != record.get(
            "observed_sha256"
        ):
            raise RuntimeError(f"terminal receipt dependency {name} is not hash-accepted")

    expected_flags = {
        "authorizes_f1": False,
        "authorizes_scientific_execution": False,
        "control_exclusion_proved": False,
        "f0_pass": False,
        "independent_audit_complete": False,
        "production_resource_gate": False,
        "production_scale_execution_classified": False,
        "resource_pass": False,
        "science_executed": False,
        "science_free_proved": False,
    }
    if receipt.get("promotion_flags") != expected_flags:
        raise RuntimeError("terminal receipt promotion flags are not fail-closed")
    if canonical.get("promotion_flags") != expected_flags:
        raise RuntimeError("canonical resource promotion flags are not fail-closed")

    measurement = receipt.get("measurement")
    fixture = receipt.get("fixture")
    if not isinstance(measurement, dict) or not isinstance(fixture, dict):
        raise RuntimeError("terminal receipt resource measurement is missing")
    if measurement.get("peak_rss_bytes", 0) <= fixture.get("maximum_rss_bytes", 0):
        raise RuntimeError("terminal receipt does not substantiate the resident-memory reason")
    if measurement.get("host_peak_footprint_bytes", 0) <= fixture.get(
        "maximum_peak_footprint_bytes", 0
    ):
        raise RuntimeError("terminal receipt does not substantiate the footprint reason")
    return {
        "canonical_sha256": canonical_snapshot.sha256,
        "failure_reasons": list(EXPECTED_FAILURE_REASONS),
        "measurement": {
            "host_peak_footprint_bytes": measurement["host_peak_footprint_bytes"],
            "peak_rss_bytes": measurement["peak_rss_bytes"],
            "process_swap_delta": measurement["process_swap_delta"],
            "wall_seconds_hex": measurement["wall_seconds_hex"],
        },
        "receipt_sha256": receipt_snapshot.sha256,
        "status": receipt["status"],
    }


def _strip_tex_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines())


def _audit_reader_text(text: str, *, label: str) -> None:
    for description, pattern in _FORBIDDEN_READER_PATTERNS.items():
        match = pattern.search(text)
        if match is not None:
            raise RuntimeError(
                f"{label} exposes {description}: {match.group(0)!r}"
            )


def _reader_proof(payload: bytes) -> bytes:
    if hashlib.sha256(payload).hexdigest() != EXPECTED_FULL_PROOF_SHA256:
        raise RuntimeError("complete proof differs from its accepted frozen bytes")
    transformed = payload
    for old, new in _PROOF_READER_REPLACEMENTS.items():
        if transformed.count(old) != 1:
            raise RuntimeError("complete proof reader edit no longer has one exact target")
        transformed = transformed.replace(old, new)
    return transformed


def _materialize_source_tree(
    snapshots: Mapping[str, common.FileSnapshot],
    source_root: Path,
) -> None:
    source_root.mkdir(parents=True, exist_ok=False)
    mapping = {
        MAIN_TEX.name: "manuscript/encounter_multimodal_prr_submission.tex",
        SUPPLEMENT_TEX.name: (
            "manuscript/encounter_multimodal_prr_submission_supplement.tex"
        ),
        EXACT_M_SPINE_TEX.name: "manuscript/exact_m_theorem_spine.tex",
        REFERENCES_BIB.name: "manuscript/references.bib",
    }
    for target_name, relative in mapping.items():
        payload = snapshots[relative].payload
        common._write_bytes(source_root / target_name, payload)
        if target_name.endswith(".tex"):
            _audit_reader_text(
                _strip_tex_comments(payload.decode("utf-8")),
                label=f"staged source {target_name}",
            )

    proof = _reader_proof(
        snapshots["manuscript/exact_m_theorem_full_proof.tex"].payload
    )
    common._write_bytes(source_root / EXACT_M_FULL_PROOF_TEX.name, proof)
    _audit_reader_text(
        _strip_tex_comments(proof.decode("utf-8")),
        label="staged complete proof",
    )


def _build_document(
    snapshots: Mapping[str, common.FileSnapshot],
    *,
    run_root: Path,
    tex_name: str,
    tools: Mapping[str, str],
    label: str,
) -> common.BuildRun:
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
    process = common._run_checked(
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
    pdf = build_root / f"{Path(tex_name).stem}.pdf"
    tex_log = common._snapshot_regular_file(
        build_root / f"{Path(tex_name).stem}.log",
        label=f"{label} TeX log",
    ).payload
    common._audit_tex_log(tex_log, label=f"{label} TeX log")
    audit = common._audit_pdf(pdf, tools=tools, label=label)
    extracted = common._run_checked(
        [tools["pdftotext"], "-enc", "UTF-8", str(pdf), "-"],
        label=f"{label} reader-language audit",
    ).stdout.decode("utf-8")
    _audit_reader_text(extracted, label=f"{label} PDF")
    return common.BuildRun(
        pdf=pdf,
        pdf_sha256=_sha256(pdf),
        tex_log=tex_log,
        latexmk_log=process.stdout + process.stderr,
        pdf_audit=audit,
    )


def _same_snapshots(
    before: Mapping[str, common.FileSnapshot],
    after: Mapping[str, common.FileSnapshot],
) -> bool:
    return {key: value.sha256 for key, value in before.items()} == {
        key: value.sha256 for key, value in after.items()
    }


def _output_record(run: common.BuildRun, path: str) -> dict[str, Any]:
    return {
        "all_page_media_boxes_points": run.pdf_audit["all_page_media_boxes_points"],
        "byte_identical_rebuilds": True,
        "font_audit": run.pdf_audit["font_audit"],
        "ghostscript_parse": True,
        "media_box_points": run.pdf_audit["media_box_points"],
        "pages": run.pdf_audit["pages"],
        "path": path,
        "sha256": run.pdf_sha256,
        "text_audit": run.pdf_audit["text_audit"],
    }


def _manifest_payload(
    *,
    snapshots: Mapping[str, common.FileSnapshot],
    receipt: Mapping[str, Any],
    main: common.BuildRun,
    supplement: common.BuildRun,
    published_hashes: Mapping[str, str],
    latexmk_version: str,
) -> dict[str, Any]:
    return {
        "build": {
            "compiler": latexmk_version,
            "driver": "code/compile_theorem_first_submission.py",
            "driver_sha256": snapshots[
                "code/compile_theorem_first_submission.py"
            ].sha256,
            "isolated_builds": {"main": 2, "supplement": 2},
            "source_date_epoch": int(SOURCE_DATE_EPOCH),
        },
        "claim_scope": {
            "finite_parameter_physical_evidence": False,
            "off_lattice_execution": False,
            "rigorous_numerical_continuum_convergence": False,
            "scientific_result": "exact_prescribed_finite_modality_doi_continuum_theorem",
        },
        "inputs": {key: value.sha256 for key, value in snapshots.items()},
        "outputs": {
            "main": _output_record(
                main, "output/pdf/encounter_multimodal_prr_submission.pdf"
            ),
            "supplement": _output_record(
                supplement,
                "output/pdf/encounter_multimodal_prr_submission_supplement.pdf",
            ),
        },
        "published_files": dict(published_hashes),
        "reader_artifacts_ready": True,
        "schema_version": SCHEMA_VERSION,
        "submission_metadata_gate": {
            "complete": False,
            "human_fields_not_inferred": [
                "conflict_of_interest_declaration",
                "contributor_roles",
                "funding",
                "orcid",
                "related_work_identifier_if_applicable",
            ],
        },
        "terminal_branch_receipt": dict(receipt),
        "validation": {
            "byte_identical_main_rebuilds": True,
            "byte_identical_supplement_rebuilds": True,
            "forbidden_reader_markers": 0,
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
    sources = _required_source_paths() if source_paths is None else dict(source_paths)
    outputs = _published_file_paths() if published_paths is None else dict(published_paths)
    errors: list[str] = []
    recorded_inputs = payload.get("inputs")
    if not isinstance(recorded_inputs, Mapping) or set(recorded_inputs) != set(sources):
        errors.append("input path set differs from the required source set")
    else:
        for relative, path in sources.items():
            if not path.is_file():
                errors.append(f"required input is missing: {relative}")
            elif recorded_inputs.get(relative) != _sha256(path):
                errors.append(f"input hash mismatch: {relative}")
    recorded_outputs = payload.get("published_files")
    if not isinstance(recorded_outputs, Mapping) or set(recorded_outputs) != set(outputs):
        errors.append("published path set differs from the required output set")
    else:
        for relative, path in outputs.items():
            if not path.is_file():
                errors.append(f"published output is missing: {relative}")
            elif recorded_outputs.get(relative) != _sha256(path):
                errors.append(f"published output hash mismatch: {relative}")
    if payload.get("reader_artifacts_ready") is not True:
        errors.append("reader artifacts are not marked ready")
    return tuple(errors)


def _build_and_publish() -> dict[str, Any]:
    snapshots = _snapshot_sources()
    if snapshots["manuscript/exact_m_theorem_spine.tex"].sha256 != EXPECTED_SPINE_SHA256:
        raise RuntimeError("the theorem spine differs from its accepted frozen bytes")
    receipt = _validate_terminal_receipt(snapshots)
    tools = common._required_tools()
    with tempfile.TemporaryDirectory(prefix="theorem-first-submission-") as name:
        temporary_root = Path(name)
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
        common._assert_identical(main_first, main_second, label="theorem-first main")
        common._assert_identical(
            supplement_first, supplement_second, label="theorem-first supplement"
        )
        current = _snapshot_sources()
        if not _same_snapshots(snapshots, current):
            raise RuntimeError("submission sources changed during isolated builds")
        _validate_terminal_receipt(current)

        stage = temporary_root / "publication"
        staged_by_relative = {
            "output/pdf/encounter_multimodal_prr_submission.pdf": stage
            / FINAL_MAIN_PDF.name,
            "output/pdf/encounter_multimodal_prr_submission_supplement.pdf": stage
            / FINAL_SUPPLEMENT_PDF.name,
            "artifacts/logs/theorem_first_submission_main_tex.log": stage
            / MAIN_TEX_LOG.name,
            "artifacts/logs/theorem_first_submission_main_latexmk.log": stage
            / MAIN_LATEXMK_LOG.name,
            "artifacts/logs/theorem_first_submission_supplement_tex.log": stage
            / SUPPLEMENT_TEX_LOG.name,
            "artifacts/logs/theorem_first_submission_supplement_latexmk.log": stage
            / SUPPLEMENT_LATEXMK_LOG.name,
        }
        common._copy_file(
            main_first.pdf,
            staged_by_relative["output/pdf/encounter_multimodal_prr_submission.pdf"],
        )
        common._copy_file(
            supplement_first.pdf,
            staged_by_relative[
                "output/pdf/encounter_multimodal_prr_submission_supplement.pdf"
            ],
        )
        for relative, first_log, second_log in (
            (
                "artifacts/logs/theorem_first_submission_main_tex.log",
                main_first.tex_log,
                main_second.tex_log,
            ),
            (
                "artifacts/logs/theorem_first_submission_main_latexmk.log",
                main_first.latexmk_log,
                main_second.latexmk_log,
            ),
            (
                "artifacts/logs/theorem_first_submission_supplement_tex.log",
                supplement_first.tex_log,
                supplement_second.tex_log,
            ),
            (
                "artifacts/logs/theorem_first_submission_supplement_latexmk.log",
                supplement_first.latexmk_log,
                supplement_second.latexmk_log,
            ),
        ):
            common._write_bytes(
                staged_by_relative[relative],
                common._normalized_log_bundle(
                    first_log, second_log, temporary_root=temporary_root
                ),
            )
        published_hashes = {
            relative: _sha256(path) for relative, path in staged_by_relative.items()
        }
        manifest = _manifest_payload(
            snapshots=snapshots,
            receipt=receipt,
            main=main_first,
            supplement=supplement_first,
            published_hashes=published_hashes,
            latexmk_version=common._latexmk_version(tools["latexmk"]),
        )
        staged_manifest = stage / MANIFEST.name
        common._write_bytes(
            staged_manifest,
            (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        staged_outputs = {
            _published_file_paths()[relative]: path
            for relative, path in staged_by_relative.items()
        }
        staged_outputs[MANIFEST] = staged_manifest
        common._publish_transaction(staged_outputs)
    return manifest


def main() -> None:
    payload = _build_and_publish()
    print(
        "Published theorem-branch reader artifacts: "
        f"main={payload['outputs']['main']['sha256']} "
        f"supplement={payload['outputs']['supplement']['sha256']}"
    )


if __name__ == "__main__":
    main()
