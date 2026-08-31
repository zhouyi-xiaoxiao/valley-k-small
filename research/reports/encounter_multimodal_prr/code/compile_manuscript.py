#!/usr/bin/env python3
"""Compile the PRR working draft in a clean temporary directory and audit it."""

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
from typing import Any, Callable

import build_manuscript_inputs
import build_positive_b_manuscript_input

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
MANUSCRIPT = REPORT / "manuscript"
DATA = REPORT / "artifacts" / "data"
LOGS = REPORT / "artifacts" / "logs"
TEX = MANUSCRIPT / "encounter_multimodal_prr.tex"
BIB = MANUSCRIPT / "references.bib"
FINAL_PDF = MANUSCRIPT / "encounter_multimodal_prr.pdf"
NUMERICAL_INPUT = MANUSCRIPT / "inputs" / "numerical_results.tex"
POSITIVE_B_INPUT = MANUSCRIPT / "inputs" / "positive_b_results.tex"
EXPECTED_TITLE = (
    "Conserved-reactivity control of encounter-time modality: "
    "weak-reaction theory and continuum-kernel designs"
)
EXPECTED_AUTHOR = "Xiaoxiao Zhouyi and Luca Giuggioli"
SOURCE_DATE_EPOCH = "1783900800"


@dataclass(frozen=True)
class FileSnapshot:
    path: Path
    relative: str
    sha256: str
    payload: bytes


FIGURE_CONTRACTS: dict[str, dict[str, object]] = {
    "observable_four_patch.pdf": {
        "metadata_sha256": "881ce1e3809466821226b32ff71cf5bd71b583dc3df399b670586ffab7ff57fe",
        "metadata_keys": {
            "schema_version",
            "stage",
            "status",
            "evidence_timing",
            "manifest_stage",
            "caption",
            "limitations",
            "claim_flags",
            "publication_scope_flags",
            "chart_contract",
            "provenance",
            "source_pins",
            "render_policy",
            "recomputation",
            "outputs",
            "pdf_qa",
        },
        "evidence_timing": "RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY",
        "claim_flags": {
            "continuum_verified": False,
            "finite_B_Doi_verified": False,
            "observable_free_exposure_confirmation_passed": True,
            "preregistered_discovery": False,
            "project_gate_passed": False,
        },
        "publication_scope_flags": {
            "continuum_verified": False,
            "event_mass_observability_verified": False,
            "finite_B_Doi_verified": False,
            "independent_PDE_solver_verified": False,
            "project_gate_passed": False,
            "relative_shape_gate_passed": True,
        },
        "source_roles": {"manifest", "producer", "protocol", "result", "source_test"},
    },
    "d2_d3_four_patch.pdf": {
        "metadata_sha256": "67d923386dafc1b01b4430f6ee369b4bdff660d6a626ade8c780ccae0234f8c7",
        "metadata_keys": {
            "schema_version",
            "stage",
            "status",
            "evidence_timing",
            "caption",
            "limitations",
            "claim_flags",
            "chart_contract",
            "provenance",
            "source_pins",
            "render_policy",
            "recomputation",
            "outputs",
            "pdf_qa",
        },
        "evidence_timing": "RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY",
        "claim_flags": {
            "continuum_verified": False,
            "d2_relative_shape_gate_passed": True,
            "d3_relative_shape_gate_passed": True,
            "event_mass_observability_verified": False,
            "finite_B_Doi_verified": False,
            "independent_PDE_solver_verified": False,
            "preregistered_discovery": False,
            "project_gate_passed": False,
            "relative_shape_only": True,
        },
        "nested_source_claim_flags": {
            "d2": {
                "continuum_verified": False,
                "finite_B_Doi_verified": False,
                "observable_free_exposure_confirmation_passed": True,
                "preregistered_discovery": False,
                "project_gate_passed": False,
            },
            "d3": {
                "continuum_verified": False,
                "finite_B_Doi_verified": False,
                "independent_PDE_solver_verified": False,
                "observable_d3_free_exposure_confirmation_passed": True,
                "preregistered_discovery": False,
                "project_gate_passed": False,
            },
        },
        "source_roles": {
            "d2.manifest",
            "d2.producer",
            "d2.result",
            "d2.test",
            "d3.manifest",
            "d3.producer",
            "d3.result",
            "d3.test",
        },
    },
    "positive_b_broad_four_slab.pdf": {
        "metadata_sha256": "0ad8214b6ae80c420321a24a5188f3e62cb3accebc520c8ac0be1153231a3821",
        "metadata_keys": {
            "schema_version",
            "stage",
            "status",
            "evidence_timing",
            "claim_scope",
            "caption",
            "limitations",
            "claim_flags",
            "scope_constraints",
            "figure_contract",
            "plotted_data",
            "source_pins",
            "renderer",
            "outputs",
            "pdf_qa",
        },
        "evidence_timing": "RESULT_INFORMED_FIXED_CONTROL_WITH_HELDOUT_FINE_MESHES",
        "claim_scope": (
            "One result-informed broad four-slab geometry with fixed absolute weights and "
            "fixed B=0.01, tested by a matrix-free killed-Doi finite-volume semigroup on "
            "two held-out odd cubic meshes in one fixed reflecting box."
        ),
        "claim_flags": {
            "allocation_cusp_verified": False,
            "continuum_interval_verified": False,
            "independent_solver_verified": False,
            "physical_d3_verified": False,
            "preregistered_discovery": False,
            "project_gate_passed": False,
            "publication_gate_passed": False,
            "unbounded_domain_FV_limit_verified": False,
        },
        "scope_constraints": {
            "finite_gate_time_max": 100.0,
            "finite_time_window_only": True,
            "fixed_box_two_mesh_semidiscrete_point_only": True,
            "heldout_odd_meshes": [113, 129],
            "positive_budget": 0.01,
            "same_solver_family_only": True,
            "saved_trace_time_max": 35.0,
            "weights_refit": False,
        },
        "source_roles": {
            "canonical_result",
            "independent_audit",
            "plotter",
            "reproducibility_evidence",
            "test",
        },
    },
    "finite_grid_fold.pdf": {
        "metadata_sha256": "bafb0d96b07578cc466c5280ad496ced224ee3daa78c0633d846a3c380f7a9aa",
        "metadata_keys": {
            "schema_version",
            "stage",
            "status",
            "evidence_timing",
            "manifest_stage",
            "claim_scope",
            "caption",
            "limitations",
            "continuum_verified",
            "finite_B_Doi_fold",
            "finite_grid_fold_confirmed",
            "interval_global_root_proof",
            "observable_trimodality_verified",
            "project_gate_passed",
            "normal_form",
            "side_root_semantics",
            "chart_contract",
            "provenance",
            "source_pins",
            "render_policy",
            "recomputation",
            "outputs",
            "pdf_qa",
        },
        "evidence_timing": "POST_RESULT_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY",
        "claim_scope": "one 65x65x49 finite-grid B=0.6 fold only",
        "top_level_flags": {
            "continuum_verified": False,
            "finite_B_Doi_fold": True,
            "finite_grid_fold_confirmed": True,
            "interval_global_root_proof": False,
            "observable_trimodality_verified": False,
            "project_gate_passed": False,
        },
        "source_roles": {"manifest", "result", "runner"},
    },
}


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPORT.resolve()))


def _run(command: tuple[str, ...], *, cwd: Path | None = None) -> str:
    process = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if process.returncode:
        tail = "\n".join(process.stdout.splitlines()[-80:])
        raise RuntimeError(f"command failed ({process.returncode}): {' '.join(command)}\n{tail}")
    return process.stdout


def _pdf_info(pdf: Path) -> dict[str, str]:
    executable = shutil.which("pdfinfo")
    if executable is None:
        raise FileNotFoundError("pdfinfo is required for the manuscript gate")
    output = _run((executable, str(pdf)))
    result: dict[str, str] = {}
    for line in output.splitlines():
        key, separator, value = line.partition(":")
        if separator:
            result[key.strip()] = value.strip()
    return result


def _font_gate(pdf: Path) -> dict[str, int]:
    executable = shutil.which("pdffonts")
    if executable is None:
        raise FileNotFoundError("pdffonts is required for the manuscript gate")
    rows = [row for row in _run((executable, str(pdf))).splitlines()[2:] if row.strip()]
    type3 = [row for row in rows if "Type 3" in row]
    unembedded = [
        row
        for row in rows
        if len(re.split(r"\s+", row.strip())) >= 6 and re.split(r"\s+", row.strip())[-5] != "yes"
    ]
    if not rows or type3 or unembedded:
        raise RuntimeError(
            f"font gate failed: rows={len(rows)}, type3={len(type3)}, unembedded={len(unembedded)}"
        )
    return {
        "font_rows": len(rows),
        "type3_rows": len(type3),
        "unembedded_rows": len(unembedded),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _require_finite_json(value: Any, location: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"nonfinite JSON number at {location}")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _require_finite_json(item, f"{location}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError(f"non-string JSON key at {location}")
            _require_finite_json(item, f"{location}.{key}")
        return
    raise TypeError(f"unsupported JSON value at {location}: {type(value).__name__}")


def _strict_json_object(snapshot: FileSnapshot, *, require_canonical: bool = True) -> dict[str, Any]:
    value = json.loads(
        snapshot.payload.decode("utf-8"),
        object_pairs_hook=_reject_duplicate_pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    if type(value) is not dict:
        raise TypeError(f"{snapshot.relative} must contain one JSON object")
    _require_finite_json(value)
    if require_canonical:
        canonical = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        if canonical != snapshot.payload:
            raise RuntimeError(f"{snapshot.relative} is not canonical JSON")
    return value


def _snapshot_regular_file(
    path: Path,
    *,
    root: Path | None = None,
    label: str,
) -> FileSnapshot:
    root = (REPORT if root is None else root).resolve(strict=True)
    candidate = Path(os.path.abspath(path))
    try:
        relative_path = candidate.relative_to(root)
    except ValueError as error:
        raise RuntimeError(f"{label} escapes the report root") from error
    if not relative_path.parts:
        raise RuntimeError(f"{label} is not a file below the report root")
    current = root
    for index, component in enumerate(relative_path.parts):
        current = current / component
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError as error:
            raise FileNotFoundError(f"{label} is missing: {current}") from error
        if stat.S_ISLNK(mode):
            raise RuntimeError(f"{label} must be an ordinary nonsymlink file")
        if index < len(relative_path.parts) - 1 and not stat.S_ISDIR(mode):
            raise RuntimeError(f"{label} has a non-directory path component")
        if index == len(relative_path.parts) - 1 and not stat.S_ISREG(mode):
            raise RuntimeError(f"{label} must be an ordinary nonsymlink file")
    descriptor = os.open(
        candidate,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise RuntimeError(f"{label} must be an ordinary nonsymlink file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
        ):
            raise RuntimeError(f"{label} changed while its snapshot was read")
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if len(payload) != after.st_size:
        raise RuntimeError(f"{label} was not read completely")
    return FileSnapshot(
        path=candidate,
        relative=str(relative_path),
        sha256=hashlib.sha256(payload).hexdigest(),
        payload=payload,
    )


def _verify_source_pins(
    pins: dict[str, object],
    metadata: FileSnapshot,
    *,
    snapshots: dict[str, FileSnapshot],
    prefix: str = "",
) -> list[dict[str, str]]:
    """Verify flat or grouped figure source pins and return one provenance row per file."""

    verified: list[dict[str, str]] = []
    for label in pins:
        if label.endswith("_sha256") and label.removesuffix("_sha256") not in pins:
            raise RuntimeError(f"orphan figure source hash {label!r}: {metadata.relative}")
    for label, value in pins.items():
        if label.endswith("_sha256"):
            continue
        role = f"{prefix}.{label}" if prefix else label
        if label == "claim_flags":
            if type(value) is not dict or not all(
                isinstance(key, str) and isinstance(flag, bool) for key, flag in value.items()
            ):
                raise RuntimeError(
                    f"invalid nested claim flags in source pins: {metadata.relative}"
                )
            forbidden_true = {
                "continuum_verified",
                "continuum_interval_verified",
                "event_mass_observability_verified",
                "finite_B_Doi_verified",
                "independent_PDE_solver_verified",
                "independent_solver_verified",
                "preregistered_discovery",
                "project_gate_passed",
                "publication_gate_passed",
                "unbounded_domain_FV_limit_verified",
            }
            if any(value.get(key) is True for key in forbidden_true):
                raise RuntimeError(f"nested figure source claim was promoted: {metadata.relative}")
            continue
        expected = pins.get(f"{label}_sha256")
        if type(value) is dict and expected is None:
            verified.extend(
                _verify_source_pins(value, metadata, snapshots=snapshots, prefix=role)
            )
            continue
        if (
            not isinstance(value, str)
            or not value
            or Path(value).is_absolute()
            or ".." in Path(value).parts
            or not isinstance(expected, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected)
        ):
            raise RuntimeError(f"figure source pin {role!r} is incomplete: {metadata.relative}")
        pinned_path = REPORT / value
        snapshot = snapshots.get(value)
        if snapshot is None:
            snapshot = _snapshot_regular_file(
                pinned_path, label=f"figure source pin {role!r}"
            )
            snapshots[value] = snapshot
        if snapshot.sha256 != expected:
            raise RuntimeError(
                f"figure source pin {role!r} hash mismatch: "
                f"expected {expected}, observed {snapshot.sha256}"
            )
        verified.append(
            {
                "role": role,
                "path": snapshot.relative,
                "sha256": snapshot.sha256,
            }
        )
    return verified


def _validate_figure_contract(
    figure: FileSnapshot,
    metadata: FileSnapshot,
    payload: dict[str, Any],
    verified_pins: list[dict[str, str]],
) -> None:
    contract = FIGURE_CONTRACTS.get(Path(figure.relative).name)
    if contract is None:
        raise RuntimeError(f"included figure has no frozen claim contract: {figure.relative}")
    expected_keys = contract["metadata_keys"]
    if type(expected_keys) is not set or set(payload) != expected_keys:
        raise RuntimeError(f"figure metadata schema changed: {metadata.relative}")
    if payload.get("evidence_timing") != contract["evidence_timing"]:
        raise RuntimeError(f"figure evidence timing changed: {metadata.relative}")
    if "claim_scope" in contract and payload.get("claim_scope") != contract["claim_scope"]:
        raise RuntimeError(f"figure claim scope changed: {metadata.relative}")
    if "claim_flags" in contract and payload.get("claim_flags") != contract["claim_flags"]:
        raise RuntimeError(f"figure claim flags changed: {metadata.relative}")
    observed_nested_claim_flags: dict[str, dict[str, bool]] = {}

    def collect_nested_claim_flags(value: dict[str, object], prefix: str = "") -> None:
        for label, item in value.items():
            role = f"{prefix}.{label}" if prefix else label
            if label == "claim_flags":
                if not prefix or type(item) is not dict or any(
                    type(key) is not str or type(flag) is not bool
                    for key, flag in item.items()
                ):
                    raise RuntimeError(
                        f"nested figure source claim schema changed: {metadata.relative}"
                    )
                observed_nested_claim_flags[prefix] = item
            elif type(item) is dict and f"{label}_sha256" not in value:
                collect_nested_claim_flags(item, role)

    source_pins = payload.get("source_pins")
    if type(source_pins) is not dict:
        raise RuntimeError(f"figure source-pin schema changed: {metadata.relative}")
    collect_nested_claim_flags(source_pins)
    expected_nested_claim_flags = contract.get("nested_source_claim_flags", {})
    if observed_nested_claim_flags != expected_nested_claim_flags:
        raise RuntimeError(f"nested figure source claim flags changed: {metadata.relative}")
    if (
        "publication_scope_flags" in contract
        and payload.get("publication_scope_flags") != contract["publication_scope_flags"]
    ):
        raise RuntimeError(f"figure publication-scope flags changed: {metadata.relative}")
    if (
        "scope_constraints" in contract
        and payload.get("scope_constraints") != contract["scope_constraints"]
    ):
        raise RuntimeError(f"figure scope constraints changed: {metadata.relative}")
    top_level_flags = contract.get("top_level_flags")
    if type(top_level_flags) is dict and any(
        payload.get(key) is not value for key, value in top_level_flags.items()
    ):
        raise RuntimeError(f"figure top-level claim flags changed: {metadata.relative}")
    outputs = payload.get("outputs")
    expected_output_keys = (
        {"metadata", "pdf", "pdf_bytes", "pdf_sha256"}
        if Path(figure.relative).name == "positive_b_broad_four_slab.pdf"
        else {"pdf", "pdf_sha256", "png", "png_sha256"}
    )
    if type(outputs) is not dict or set(outputs) != expected_output_keys:
        raise RuntimeError(f"figure outputs schema changed: {metadata.relative}")
    if outputs.get("pdf") != figure.relative or outputs.get("pdf_sha256") != figure.sha256:
        raise RuntimeError(f"figure PDF hash/path is not pinned by metadata: {figure.relative}")
    if "metadata" in outputs and outputs["metadata"] != metadata.relative:
        raise RuntimeError(f"figure metadata self-path changed: {metadata.relative}")
    if "pdf_bytes" in outputs and outputs["pdf_bytes"] != len(figure.payload):
        raise RuntimeError(f"figure byte count changed: {figure.relative}")
    expected_roles = contract["source_roles"]
    observed_roles = {row["role"] for row in verified_pins}
    if (
        type(expected_roles) is not set
        or observed_roles != expected_roles
        or len(verified_pins) != len(observed_roles)
        or len(verified_pins) != len(expected_roles)
    ):
        raise RuntimeError(f"figure source-role set changed: {metadata.relative}")
    if metadata.sha256 != contract["metadata_sha256"]:
        raise RuntimeError(f"figure metadata hash changed: {metadata.relative}")


def _figure_provenance_with_snapshots(
    source: str,
) -> tuple[list[dict[str, object]], dict[str, FileSnapshot]]:
    """Resolve figures and retain the exact attested bytes used by LaTeX."""

    graphic_directories = [MANUSCRIPT]
    for payload in re.findall(r"\\graphicspath\{((?:\{[^{}]+\})+)\}", source):
        graphic_directories.extend(
            MANUSCRIPT / entry for entry in re.findall(r"\{([^{}]+)\}", payload)
        )
    names = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^{}]+)\}", source)
    rows: list[dict[str, object]] = []
    source_snapshots: dict[str, FileSnapshot] = {}
    figure_snapshots: dict[str, FileSnapshot] = {}
    for name in names:
        supplied = Path(name)
        if supplied.is_absolute() or ".." in supplied.parts:
            raise RuntimeError(f"included figure path escapes the manuscript: {name!r}")
        candidates: list[Path] = []
        suffixes = ("",) if supplied.suffix else (".pdf", ".png", ".eps")
        for directory in graphic_directories:
            candidates.extend(directory / f"{name}{suffix}" for suffix in suffixes)
        figure: FileSnapshot | None = None
        for candidate in candidates:
            try:
                figure = _snapshot_regular_file(candidate, label=f"included figure {name!r}")
            except FileNotFoundError:
                continue
            break
        if figure is None:
            raise FileNotFoundError(f"could not resolve included figure {name!r}")
        metadata_path = figure.path.with_name(f"{figure.path.stem}_metadata.json")
        metadata = _snapshot_regular_file(
            metadata_path, label=f"metadata for included figure {name!r}"
        )
        payload = _strict_json_object(metadata)
        pins = payload.get("source_pins")
        if type(pins) is not dict:
            raise RuntimeError(f"figure metadata lacks source_pins: {metadata.relative}")
        verified_pins = _verify_source_pins(
            pins, metadata, snapshots=source_snapshots
        )
        if not verified_pins:
            raise RuntimeError(
                f"figure metadata has no verifiable source files: {metadata.relative}"
            )
        _validate_figure_contract(figure, metadata, payload, verified_pins)
        rows.append(
            {
                "path": figure.relative,
                "sha256": figure.sha256,
                "metadata": metadata.relative,
                "metadata_sha256": metadata.sha256,
                "evidence_timing": payload["evidence_timing"],
                "claim_flags": payload.get("claim_flags"),
                "scope_constraints": payload.get("scope_constraints"),
                "verified_source_pins": verified_pins,
            }
        )
        figure_snapshots[figure.relative] = figure
    return rows, figure_snapshots


def _figure_provenance(source: str) -> list[dict[str, object]]:
    return _figure_provenance_with_snapshots(source)[0]


def _validate_tex_source(source: str) -> None:
    control_characters = re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", source)
    if control_characters:
        codes = sorted({f"U+{ord(value):04X}" for value in control_characters})
        raise RuntimeError("TeX source contains control characters: " + ", ".join(codes))
    malformed_commands = re.findall(r"(?<!\\)\b(?:qquad|nonumber|textbf|mathrm)\b", source)
    if malformed_commands:
        raise RuntimeError(
            "possible TeX commands missing a backslash: "
            + ", ".join(sorted(set(malformed_commands)))
        )


def _write_staged_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def _write_staged_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _copy_staged_file(source: Path, target: Path) -> None:
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


def _publish_transaction(
    staged_outputs: dict[Path, Path],
    *,
    replace: Callable[
        [
            str | bytes | os.PathLike[str] | os.PathLike[bytes],
            str | bytes | os.PathLike[str] | os.PathLike[bytes],
        ],
        None,
    ] = os.replace,
) -> None:
    """Publish a checked output set with same-directory atomic replaces and rollback."""

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
                prefix=f".{target.name}.incoming.",
                suffix=".tmp",
                dir=target.parent,
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
                    prefix=f".{target.name}.backup.",
                    suffix=".tmp",
                    dir=target.parent,
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
            except BaseException as error:  # pragma: no cover - catastrophic filesystem error
                rollback_errors.append(f"{target}: {error}")
        for directory in touched_directories:
            try:
                _fsync_directory(directory)
            except OSError as error:  # pragma: no cover - catastrophic filesystem error
                rollback_errors.append(f"fsync {directory}: {error}")
        if rollback_errors:
            raise RuntimeError(
                "publication transaction failed and rollback was incomplete: "
                + "; ".join(rollback_errors)
            )
        raise
    finally:
        for path in (*prepared.values(), *(path for path in backups.values() if path is not None)):
            path.unlink(missing_ok=True)


def main() -> None:
    # Complete numerical and figure provenance closure before any canonical write.
    numerical_provenance = build_manuscript_inputs.verify_numerical_sources()
    numerical_text = build_manuscript_inputs.render_verified_macros(numerical_provenance)
    positive_b_provenance = build_positive_b_manuscript_input.verify_sources()
    positive_b_text = build_positive_b_manuscript_input.render_verified_macros(
        positive_b_provenance
    )
    tex_snapshot = _snapshot_regular_file(TEX, label="manuscript TeX")
    bibliography_snapshot = _snapshot_regular_file(BIB, label="manuscript bibliography")
    source = tex_snapshot.payload.decode("utf-8")
    _validate_tex_source(source)
    figure_provenance, figure_snapshots = _figure_provenance_with_snapshots(source)
    tex_sha256 = tex_snapshot.sha256
    bibliography_sha256 = bibliography_snapshot.sha256
    latexmk = shutil.which("latexmk")
    if latexmk is None:
        raise FileNotFoundError("latexmk is required for the manuscript build")

    forbidden = {
        "undefined_references": r"There were undefined references",
        "undefined_citations": r"Citation .* undefined",
        "overfull_boxes": r"Overfull \\[hv]box",
        "missing_files": r"LaTeX Error: File .* not found",
    }
    build_hashes: list[str] = []
    latexmk_logs: list[str] = []
    warning_counts: dict[str, int] = {}
    with tempfile.TemporaryDirectory(prefix="encounter_multimodal_prr_") as directory:
        root = Path(directory)
        snapshot_report = root / "report"
        snapshot_manuscript = snapshot_report / "manuscript"
        snapshot_tex = snapshot_manuscript / TEX.name
        snapshot_bib = snapshot_manuscript / BIB.name
        snapshot_input = snapshot_manuscript / "inputs" / NUMERICAL_INPUT.name
        snapshot_positive_b_input = snapshot_manuscript / "inputs" / POSITIVE_B_INPUT.name
        _write_staged_text(snapshot_tex, source)
        _write_staged_bytes(snapshot_bib, bibliography_snapshot.payload)
        _write_staged_text(snapshot_input, numerical_text)
        _write_staged_text(snapshot_positive_b_input, positive_b_text)
        for row in figure_provenance:
            relative = row["path"]
            if not isinstance(relative, str):
                raise RuntimeError("figure provenance path is malformed")
            snapshot = figure_snapshots.get(relative)
            if snapshot is None or snapshot.sha256 != row["sha256"]:
                raise RuntimeError("figure snapshot/provenance identity is malformed")
            _write_staged_bytes(snapshot_report / relative, snapshot.payload)

        built_pdfs: list[Path] = []
        for replica in ("clean_a", "clean_b"):
            build = root / replica
            build.mkdir()
            process = subprocess.run(
                (
                    latexmk,
                    "-norc",
                    "-pdf",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    f"-outdir={build}",
                    snapshot_tex.name,
                ),
                cwd=snapshot_manuscript,
                env={
                    **os.environ,
                    "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH,
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
            latexmk_logs.append(f"[{replica}]\n{process.stdout}")
            if process.returncode:
                tail = "\n".join(process.stdout.splitlines()[-80:])
                raise RuntimeError(f"latexmk failed in {replica}:\n{tail}")
            built_pdf = build / FINAL_PDF.name
            built_log = build / f"{TEX.stem}.log"
            if not built_pdf.is_file() or not built_log.is_file():
                raise RuntimeError("latexmk did not create the expected PDF and log")
            log_text = built_log.read_text(encoding="utf-8", errors="replace")
            counts = {
                name: len(re.findall(pattern, log_text)) for name, pattern in forbidden.items()
            }
            if any(counts.values()):
                raise RuntimeError(f"manuscript warning gate failed in {replica}: {counts}")
            if replica == "clean_a":
                warning_counts = counts
            built_pdfs.append(built_pdf)
            build_hashes.append(_sha256(built_pdf))

        if len(set(build_hashes)) != 1:
            raise RuntimeError(f"clean manuscript builds are not byte-identical: {build_hashes}")
        staged_pdf = built_pdfs[0]
        info = _pdf_info(staged_pdf)
        if info.get("Title") != EXPECTED_TITLE:
            raise RuntimeError(f"unexpected PDF title: {info.get('Title')!r}")
        if info.get("Author") != EXPECTED_AUTHOR:
            raise RuntimeError(f"unexpected PDF author: {info.get('Author')!r}")
        if not info.get("Subject") or not info.get("Keywords"):
            raise RuntimeError("PDF subject or keywords are missing")
        pages = int(info.get("Pages", "0"))
        if pages <= 0:
            raise RuntimeError(f"invalid PDF page count: {pages}")
        font_audit = _font_gate(staged_pdf)

        staged_tex_log = root / "publication" / "manuscript_tex.log"
        staged_latexmk_log = root / "publication" / "manuscript_latexmk.log"
        _write_staged_text(
            staged_tex_log,
            (root / "clean_a" / f"{TEX.stem}.log").read_text(encoding="utf-8", errors="replace"),
        )
        _write_staged_text(staged_latexmk_log, "\n\n".join(latexmk_logs))

        # Close the time-of-check/time-of-use window before publication.
        if build_manuscript_inputs.verify_numerical_sources() != numerical_provenance:
            raise RuntimeError("numerical source provenance changed during the manuscript build")
        if build_positive_b_manuscript_input.verify_sources() != positive_b_provenance:
            raise RuntimeError("positive-B source provenance changed during the manuscript build")
        if _figure_provenance(source) != figure_provenance:
            raise RuntimeError("figure provenance changed during the manuscript build")
        if (
            _snapshot_regular_file(TEX, label="post-build manuscript TeX").sha256
            != tex_sha256
            or _snapshot_regular_file(BIB, label="post-build manuscript bibliography").sha256
            != bibliography_sha256
        ):
            raise RuntimeError("manuscript TeX or bibliography changed during the build")

        report = {
            "status": "PASS",
            "evidence_scope": "working-draft build and PDF hygiene only; not a scientific gate",
            "release_eligible": False,
            "release_blocker": (
                "scientific continuum gates and author-confirmed submission metadata remain open"
            ),
            "submission_metadata_checklist": "manuscript/SUBMISSION_METADATA_REQUIRED.md",
            "tex": str(TEX.relative_to(REPORT)),
            "tex_sha256": tex_sha256,
            "bibliography": str(BIB.relative_to(REPORT)),
            "bibliography_sha256": bibliography_sha256,
            "numerical_input": str(NUMERICAL_INPUT.relative_to(REPORT)),
            "numerical_input_sha256": _sha256(snapshot_input),
            "positive_b_input": str(POSITIVE_B_INPUT.relative_to(REPORT)),
            "positive_b_input_sha256": _sha256(snapshot_positive_b_input),
            "positive_b_source_hashes": positive_b_provenance["hashes"],
            "numerical_source_manifest": numerical_provenance["manifest"],
            "numerical_source_manifest_sha256": numerical_provenance["manifest_sha256"],
            "verified_numerical_sources": numerical_provenance["verified_files"],
            "figure_inputs": figure_provenance,
            "build_driver": str(HERE.relative_to(REPORT)),
            "build_driver_sha256": _sha256(HERE),
            "numerical_input_builder": str(build_manuscript_inputs.HERE.relative_to(REPORT)),
            "numerical_input_builder_sha256": _sha256(build_manuscript_inputs.HERE),
            "positive_b_input_builder": str(
                build_positive_b_manuscript_input.HERE.relative_to(REPORT)
            ),
            "positive_b_input_builder_sha256": _sha256(build_positive_b_manuscript_input.HERE),
            "pdf": str(FINAL_PDF.relative_to(REPORT)),
            "pages": pages,
            "pdf_bytes": staged_pdf.stat().st_size,
            "pdf_sha256": _sha256(staged_pdf),
            "clean_build_sha256_pair": build_hashes,
            "byte_identical_clean_rebuilds": len(set(build_hashes)) == 1,
            "pdf_metadata": {key: info[key] for key in ("Title", "Author", "Subject", "Keywords")},
            "font_audit": font_audit,
            "warning_counts": warning_counts,
            "source_date_epoch": SOURCE_DATE_EPOCH,
            "publication_transaction": {
                "preflight_before_canonical_writes": True,
                "temporary_source_snapshot": True,
                "all_checks_before_publish": True,
                "same_directory_atomic_replace_with_rollback": True,
                "published_outputs": [
                    str(path.relative_to(REPORT))
                    for path in (
                        NUMERICAL_INPUT,
                        POSITIVE_B_INPUT,
                        FINAL_PDF,
                        LOGS / "manuscript_tex.log",
                        LOGS / "manuscript_latexmk.log",
                        DATA / "manuscript_compile.json",
                    )
                ],
            },
        }
        staged_manifest = root / "publication" / "manuscript_compile.json"
        _write_staged_text(
            staged_manifest,
            json.dumps(report, indent=2, sort_keys=True) + "\n",
        )
        _publish_transaction(
            {
                NUMERICAL_INPUT: snapshot_input,
                POSITIVE_B_INPUT: snapshot_positive_b_input,
                FINAL_PDF: staged_pdf,
                LOGS / "manuscript_tex.log": staged_tex_log,
                LOGS / "manuscript_latexmk.log": staged_latexmk_log,
                DATA / "manuscript_compile.json": staged_manifest,
            }
        )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
