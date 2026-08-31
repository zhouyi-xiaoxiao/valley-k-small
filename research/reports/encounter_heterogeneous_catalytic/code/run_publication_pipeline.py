#!/usr/bin/env python3
"""One-command, fail-closed publication build for the encounter study.

The numerical scripts remain independently executable.  This driver provides
the submission-facing orchestration layer: it records every command, refuses
to continue after a failed gate, and writes a transitive SHA-256 inventory of
the resulting research package.
"""

from __future__ import annotations

import argparse
import ast
import fcntl
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from packaging.markers import default_environment
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = REPORT / "artifacts" / "data"
LOGS = REPORT / "artifacts" / "logs"
MANUSCRIPT = REPORT / "manuscript"
FORMAL = REPO / "research" / "reports" / "ring_lazy_jump_ext_rev2" / "code" / "formal_lean"
FORMAL_ALLOWED_AXIOMS = frozenset(
    {"propext", "Classical.choice", "Quot.sound"}
)
FORMAL_DRIVER_REPORTS = {
    "AxiomsReport.lean": "axioms_report_20260714.txt",
    "EncounterAxioms.lean": "encounter_axioms_report_20260711.txt",
    "EncounterContinuumAxioms.lean": (
        "encounter_continuum_axioms_report_20260711.txt"
    ),
    "EncounterDesignAxioms.lean": "encounter_design_axioms_report_20260711.txt",
}
FORMAL_STAGE_DRIVERS = {
    "lean4_legacy_axioms": "AxiomsReport.lean",
    "lean4_encounter_axioms": "EncounterAxioms.lean",
    "lean4_continuum_axioms": "EncounterContinuumAxioms.lean",
    "lean4_design_axioms": "EncounterDesignAxioms.lean",
}
FORMAL_BUILD_TARGETS = (
    "FormalLean",
    "FormalLean.MarkedTransfer",
    "FormalLean.SlowFast",
    "FormalLean.CertificateAudit",
    "FormalLean.Encounter",
    "FormalLean.EncounterContinuum",
    "FormalLean.EncounterDesign",
)
RUNTIME_ROOT_PACKAGES = (
    "ipykernel",
    "jsonschema",
    "matplotlib",
    "nbclient",
    "nbformat",
    "numpy",
    "pandas",
    "pytest",
    "pyyaml",
    "scipy",
)
VERIFY_STAGE_NAMES = (
    "pytest_publication_gates",
    "lean4_static_integrity",
    "lean4_build",
    "lean4_legacy_axioms",
    "lean4_encounter_axioms",
    "lean4_continuum_axioms",
    "lean4_design_axioms",
)
REPRODUCIBLE_STAGE_ENV = {
    "SOURCE_DATE_EPOCH": "1783728000",
    "FORCE_SOURCE_DATE": "1",
    "TZ": "UTC",
}
VKCORE_SRC = REPO / "packages" / "vkcore" / "src" / "vkcore"
LEAN_WORKSPACE_ROOT = (
    Path.home()
    / ".local-build"
    / "valley-k-small"
    / "encounter_formal_pipeline"
)
LEAN_ROOT_FILES = (
    "lakefile.toml",
    "lake-manifest.json",
    "lean-toolchain",
    "FormalLean.lean",
    "AxiomsReport.lean",
    "EncounterAxioms.lean",
    "EncounterContinuumAxioms.lean",
    "EncounterDesignAxioms.lean",
)
FORBIDDEN_LEAN_PATTERNS = {
    "sorry": re.compile(r"\bsorry\b"),
    "admit": re.compile(r"\badmit\b"),
    "axiom declaration": re.compile(
        r"(?m)^\s*(?:@\[[^\]\n]*\]\s*)*"
        r"(?:(?:private|protected|public|noncomputable|local|scoped|unsafe|partial)\s+)*axiom\b"
    ),
    "constant declaration": re.compile(
        r"(?m)^\s*(?:@\[[^\]\n]*\]\s*)*"
        r"(?:(?:private|protected|public|noncomputable|local|scoped|unsafe|partial)\s+)*constant\b"
    ),
    "opaque declaration": re.compile(
        r"(?m)^\s*(?:@\[[^\]\n]*\]\s*)*"
        r"(?:(?:private|protected|public|noncomputable|local|scoped|unsafe|partial)\s+)*opaque\b"
    ),
    "unsafe declaration": re.compile(
        r"(?m)^\s*(?:@\[[^\]\n]*\]\s*)*"
        r"(?:(?:private|protected|public|noncomputable|local|scoped|partial)\s+)*"
        r"unsafe\s+(?:def|theorem|instance)\b"
    ),
    "native_decide": re.compile(r"\bnative_decide\b"),
}
# macOS File Provider's dataless flag is not exposed by Python's ``stat``
# module.  Reading such a placeholder can block a release build indefinitely.
MACOS_FILE_PROVIDER_DATALESS = 0x40000000


@dataclass(frozen=True)
class Stage:
    name: str
    command: tuple[str, ...]
    profiles: tuple[str, ...]
    cwd: Path = REPO


@dataclass
class StageResult:
    name: str
    command: list[str]
    cwd: str
    started_at_utc: str
    duration_seconds: float
    returncode: int
    log: str
    log_bytes: int
    log_sha256: str


class WorkspaceLockUnavailable(RuntimeError):
    """Raised before any artifact write when another publication run is active."""


def _python(script: str) -> tuple[str, ...]:
    return (sys.executable, str(REPORT / "code" / script))


def _stage_environment() -> dict[str, str]:
    """Return the deterministic environment inherited by every build stage."""

    env = os.environ.copy()
    source = str(REPO / "packages" / "vkcore" / "src")
    env["PYTHONPATH"] = source + os.pathsep + env.get("PYTHONPATH", "")
    env.update(REPRODUCIBLE_STAGE_ENV)
    return env


def _acquire_workspace_lock(path: Path):
    """Acquire the exclusive artifact lock or fail without touching artifacts."""

    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, BlockingIOError) as exc:
        handle.close()
        raise WorkspaceLockUnavailable(
            "another publication pipeline owns the artifact workspace lock "
            f"({path}): {exc}"
        ) from exc
    return handle


def _stages() -> list[Stage]:
    return [
        Stage(
            "lean4_static_integrity",
            _python("verify_lean_formal.py"),
            ("full",),
        ),
        Stage("model_schematic", _python("plot_model_schematic.py"), ("quick", "full")),
        Stage("finite_green_spectrum", _python("validate_finite_green_spectrum.py"), ("quick", "full")),
        Stage("discovery_and_ctmc", _python("build_report.py"), ("quick", "full")),
        Stage("gig_and_finite_ctmc_fold", _python("validate_gig_fold.py"), ("quick", "full")),
        Stage(
            "modality_susceptibility",
            _python("validate_modality_susceptibility.py"),
            ("quick", "full"),
        ),
        Stage("multid_gig_design", _python("validate_multid_gig_design.py"), ("quick", "full")),
        Stage(
            "finite_radius_2d_matched_fold",
            _python("validate_2d_matched_fold.py"),
            ("quick", "full"),
        ),
        Stage("finite_radius_2d", _python("validate_2d_finite_radius.py"), ("quick", "full")),
        Stage("finite_radius_2d_trimodal", _python("validate_2d_trimodal.py"), ("full",)),
        Stage(
            "spectral_modality",
            _python("validate_spectral_modality.py"),
            ("full",),
        ),
        Stage("finite_radius_2d_centre_coordinate", _python("validate_2d_centre_coordinate.py"), ("full",)),
        Stage("finite_radius_2d_mechanisms", _python("validate_2d_mechanisms.py"), ("full",)),
        Stage("finite_radius_2d_matched_control", _python("validate_2d_matched_homogeneous.py"), ("quick", "full")),
        Stage("finite_radius_2d_capacity", _python("validate_2d_capacity.py"), ("full",)),
        Stage("finite_radius_3d_capacity", _python("validate_3d_capacity.py"), ("full",)),
        Stage("reader_notebook", _python("build_publication_notebook.py"), ("full",)),
        Stage("manuscript_compile", _python("compile_manuscript.py"), ("full",)),
        Stage(
            "legacy_manifest_refresh",
            _python("refresh_legacy_manifest.py"),
            ("full",),
        ),
        Stage(
            "audit_ledger",
            _python("build_audit_ledger.py"),
            ("full",),
        ),
    ]


def _sha256(path: Path) -> str:
    _require_materialized(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_materialized(path: Path) -> None:
    flags = getattr(path.stat(), "st_flags", 0)
    if flags & MACOS_FILE_PROVIDER_DATALESS:
        raise RuntimeError(
            f"source/artifact is an unmaterialized cloud placeholder: {path}; "
            "download or pin it before running publication proofs"
        )


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return str(path.resolve())


def _sanitize_lean_source(text: str, *, strip_literals: bool) -> str:
    """Remove comments safely, optionally blanking string-literal contents.

    Lean comment delimiters inside strings are ordinary characters.  A regex or
    comment-only state machine can therefore both hide executable declarations
    and report false proof escapes from prose strings.  This small lexer keeps
    byte/line positions stable while handling nested block comments and escaped
    double quotes.
    """

    output: list[str] = []
    index = 0
    block_depth = 0
    in_string = False
    escaped = False
    while index < len(text):
        character = text[index]
        pair = text[index : index + 2]
        if block_depth:
            if pair == "/-":
                block_depth += 1
                output.extend("  ")
                index += 2
            elif pair == "-/":
                block_depth -= 1
                output.extend("  ")
                index += 2
            else:
                output.append("\n" if character == "\n" else " ")
                index += 1
            continue
        if in_string:
            output.append(
                character
                if not strip_literals or character == "\n"
                else " "
            )
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if pair == "/-":
            block_depth = 1
            output.extend("  ")
            index += 2
            continue
        if pair == "--":
            newline = text.find("\n", index)
            if newline < 0:
                output.extend(" " * (len(text) - index))
                break
            output.extend(" " * (newline - index))
            output.append("\n")
            index = newline + 1
            continue
        if character == '"':
            in_string = True
            output.append(" " if strip_literals else character)
            index += 1
            continue
        output.append(character)
        index += 1
    if block_depth:
        raise RuntimeError("unterminated Lean block comment")
    if in_string:
        raise RuntimeError("unterminated Lean string literal")
    return "".join(output)


def _strip_lean_comments(text: str) -> str:
    """Remove nested Lean comments while preserving strings and line structure."""

    return _sanitize_lean_source(text, strip_literals=False)


def _module_theorems(path: Path) -> list[str]:
    source = _strip_lean_comments(path.read_text(encoding="utf-8"))
    return re.findall(r"(?m)^\s*theorem\s+([^\s({:]+)", source)


def _driver_theorems(path: Path) -> list[str]:
    source = _strip_lean_comments(path.read_text(encoding="utf-8"))
    return re.findall(r"(?m)^\s*#print\s+axioms\s+([^\s]+)\s*$", source)


def _forbidden_lean_declarations(path: Path) -> list[str]:
    """Return forbidden proof escapes/declarations in executable Lean source."""

    source = _sanitize_lean_source(
        path.read_text(encoding="utf-8"), strip_literals=True
    )
    return [
        label for label, pattern in FORBIDDEN_LEAN_PATTERNS.items() if pattern.search(source)
    ]


def _parse_axiom_output(text: str) -> dict[str, set[str]]:
    rows: dict[str, set[str]] = {}
    pattern = re.compile(
        r"(?m)^'([^']+)' depends on axioms: \[([^\]]*)\]\s*$"
    )
    for theorem, payload in pattern.findall(text):
        if theorem in rows:
            raise RuntimeError(f"duplicate axiom row for {theorem}")
        rows[theorem] = {
            item.strip() for item in payload.split(",") if item.strip()
        }
    return rows


def _axiom_output_errors(expected: set[str], text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    for marker in ("sorryax", "declaration uses 'sorry'", "unknown declaration"):
        if marker in lowered:
            errors.append(f"forbidden Lean output marker: {marker}")
    try:
        rows = _parse_axiom_output(text)
    except RuntimeError as exc:
        return [str(exc)]
    actual = set(rows)
    if actual != expected:
        errors.append(
            "axiom-report theorem set mismatch: "
            f"missing={sorted(expected - actual)} extra={sorted(actual - expected)}"
        )
    for theorem, axioms in rows.items():
        unexpected = axioms - FORMAL_ALLOWED_AXIOMS
        if unexpected:
            errors.append(f"{theorem} has nonstandard axioms {sorted(unexpected)}")
    return errors


def _formal_integrity_payload() -> dict[str, object]:
    lake_config = tomllib.loads((FORMAL / "lakefile.toml").read_text(encoding="utf-8"))
    default_targets = tuple(lake_config.get("defaultTargets", ()))
    modules = sorted((FORMAL / "FormalLean").glob("*.lean"))
    if not modules:
        raise FileNotFoundError(f"formal modules are missing below {FORMAL}")
    theorem_rows: list[dict[str, object]] = []
    theorem_names: set[str] = set()
    forbidden_rows: list[str] = []
    encounter_stems = {"Encounter", "EncounterContinuum", "EncounterDesign"}
    counts = {"legacy": 0, "encounter": 0}
    group_names: dict[str, set[str]] = {
        "AxiomsReport.lean": set(),
        "EncounterAxioms.lean": set(),
        "EncounterContinuumAxioms.lean": set(),
        "EncounterDesignAxioms.lean": set(),
    }
    lean_sources = {
        FORMAL / "FormalLean.lean",
        *FORMAL.glob("*Axioms*.lean"),
        *modules,
    }
    for path in sorted(lean_sources):
        forbidden_rows.extend(
            f"{_relative(path)}:{label}"
            for label in _forbidden_lean_declarations(path)
        )
    for path in modules:
        names = _module_theorems(path)
        qualified = {f"DPMA.{name}" for name in names}
        duplicates = theorem_names & qualified
        if duplicates:
            raise RuntimeError(f"duplicate formal theorem names: {sorted(duplicates)}")
        theorem_names.update(qualified)
        group = "encounter" if path.stem in encounter_stems else "legacy"
        counts[group] += len(names)
        driver = (
            f"{path.stem}Axioms.lean"
            if path.stem in encounter_stems
            else "AxiomsReport.lean"
        )
        group_names[driver].update(qualified)
        theorem_rows.append(
            {
                "path": _relative(path),
                "sha256": _sha256(path),
                "theorem_count": len(names),
                "group": group,
            }
        )
    errors: list[str] = []
    if forbidden_rows:
        errors.append(f"forbidden proof tokens: {forbidden_rows}")
    if default_targets != FORMAL_BUILD_TARGETS:
        errors.append(
            "lake default targets do not cover the publication build: "
            f"observed={default_targets} expected={FORMAL_BUILD_TARGETS}"
        )
    if counts != {"legacy": 80, "encounter": 60}:
        errors.append(f"theorem partition is {counts}, expected legacy=80 encounter=60")
    if len(theorem_names) != 140:
        errors.append(f"total theorem count is {len(theorem_names)}, expected 140")

    report_rows: list[dict[str, object]] = []
    printed_names: set[str] = set()
    for driver_name, report_name in FORMAL_DRIVER_REPORTS.items():
        driver = FORMAL / driver_name
        report = FORMAL / report_name
        expected = group_names[driver_name]
        declared = set(_driver_theorems(driver))
        if declared != expected:
            errors.append(
                f"{driver_name} coverage mismatch: "
                f"missing={sorted(expected - declared)} "
                f"extra={sorted(declared - expected)}"
            )
        duplicates = printed_names & declared
        if duplicates:
            errors.append(
                f"theorems printed by multiple axiom drivers: {sorted(duplicates)}"
            )
        printed_names.update(declared)
        if not report.is_file():
            errors.append(f"saved axiom report missing: {_relative(report)}")
            continue
        report_text = report.read_text(encoding="utf-8")
        errors.extend(
            f"{report_name}: {message}"
            for message in _axiom_output_errors(expected, report_text)
        )
        report_rows.append(
            {
                "driver": _relative(driver),
                "driver_sha256": _sha256(driver),
                "report": _relative(report),
                "report_sha256": _sha256(report),
                "theorem_count": len(expected),
            }
        )
    if printed_names != theorem_names:
        errors.append(
            "combined axiom-driver coverage mismatch: "
            f"missing={sorted(theorem_names - printed_names)} "
            f"extra={sorted(printed_names - theorem_names)}"
        )
    if errors:
        raise RuntimeError("formal integrity gate failed:\n- " + "\n- ".join(errors))
    return {
        "schema_version": 1,
        "status": "pass",
        "theorem_counts": {
            "legacy": counts["legacy"],
            "encounter_specific": counts["encounter"],
            "total": len(theorem_names),
        },
        "default_build_targets": list(default_targets),
        "forbidden_declarations": sorted(FORBIDDEN_LEAN_PATTERNS),
        "allowed_axioms": sorted(FORMAL_ALLOWED_AXIOMS),
        "module_inventory": theorem_rows,
        "axiom_reports": report_rows,
    }


def _write_formal_integrity_report() -> Path:
    payload = _formal_integrity_payload()
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / "lean_formal_integrity.json"
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path


def _validate_lean_stage_output(stage_name: str, output: str) -> list[str]:
    if stage_name == "lean4_build":
        lowered = output.lower()
        return [
            f"forbidden Lean build marker: {marker}"
            for marker in ("sorryax", "declaration uses 'sorry'")
            if marker in lowered
        ]
    driver_name = FORMAL_STAGE_DRIVERS.get(stage_name)
    if driver_name is None:
        return []
    expected = set(_driver_theorems(FORMAL / driver_name))
    return _axiom_output_errors(expected, output)


def _tracked_outputs(
    *, include_logs: bool = True, include_audits: bool = True
) -> list[dict[str, object]]:
    roots = [
        REPORT / "artifacts" / "data",
        REPORT / "artifacts" / "figures",
        REPORT / "manuscript",
        REPORT / "notebooks",
    ]
    if include_audits:
        roots.append(REPORT / "audits")
    if include_logs:
        roots.append(REPORT / "artifacts" / "logs")
    suffixes = {
        ".bib",
        ".csv",
        ".ipynb",
        ".json",
        ".log",
        ".npz",
        ".pdf",
        ".png",
        ".tex",
        ".txt",
    }
    rows: list[dict[str, object]] = []
    declared_logs: set[Path] = {
        LOGS / "manuscript_latexmk.log",
        LOGS / "supplement_latexmk.log",
    }
    if include_logs:
        manifest_candidates = [
            DATA / "publication_pipeline.full.manifest.json",
            DATA / "publication_pipeline.verify.manifest.json",
            *sorted((DATA / "publication_pipeline_attempts").glob("*.manifest.json")),
        ]
        for manifest_candidate in manifest_candidates:
            if not manifest_candidate.is_file():
                continue
            try:
                manifest_payload = json.loads(
                    manifest_candidate.read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError):
                continue
            for stage_row in manifest_payload.get("stages", []):
                if isinstance(stage_row, dict) and stage_row.get("log"):
                    declared_logs.add((REPO / str(stage_row["log"])).resolve())
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if (
                path.suffix == ".json"
                and (
                    (
                        path.parent.resolve() == DATA.resolve()
                        and path.name.startswith("publication_pipeline")
                    )
                    or "publication_pipeline_attempts" in path.parts
                )
            ):
                continue
            if root.resolve() == LOGS.resolve() and path.resolve() not in {
                candidate.resolve() for candidate in declared_logs
            }:
                continue
            if path.is_file() and path.suffix.lower() in suffixes:
                rows.append(
                    {
                        "path": _relative(path),
                        "bytes": path.stat().st_size,
                        "sha256": _sha256(path),
                    }
                )
    legacy_manifest = REPORT / "artifacts" / "manifest.json"
    if legacy_manifest.is_file():
        rows.append(
            {
                "path": _relative(legacy_manifest),
                "bytes": legacy_manifest.stat().st_size,
                "sha256": _sha256(legacy_manifest),
            }
        )
    return rows


def _vkcore_module_path(module: str) -> Path | None:
    if module == "vkcore":
        candidate = VKCORE_SRC / "__init__.py"
    elif module.startswith("vkcore."):
        relative = module.removeprefix("vkcore.").replace(".", "/")
        module_file = VKCORE_SRC / f"{relative}.py"
        package_file = VKCORE_SRC / relative / "__init__.py"
        candidate = module_file if module_file.is_file() else package_file
    else:
        return None
    return candidate if candidate.is_file() else None


def _module_name_for_vkcore_path(path: Path) -> str:
    relative = path.resolve().relative_to(VKCORE_SRC.resolve())
    if relative.name == "__init__.py":
        suffix = relative.parent.parts
    else:
        suffix = (*relative.parent.parts, relative.stem)
    return ".".join(("vkcore", *suffix))


def _imported_vkcore_modules(path: Path) -> set[str]:
    """Parse direct local imports, including relative imports inside vkcore."""

    try:
        _require_materialized(path)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeError) as exc:
        raise RuntimeError(f"cannot parse publication Python source {path}: {exc}") from exc
    current_module = (
        _module_name_for_vkcore_path(path)
        if path.resolve().is_relative_to(VKCORE_SRC.resolve())
        else ""
    )
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name != "vkcore" and not alias.name.startswith("vkcore."):
                    continue
                if _vkcore_module_path(alias.name) is None:
                    raise FileNotFoundError(
                        f"local vkcore import {alias.name!r} from {path} does not resolve"
                    )
                modules.add(alias.name)
            continue
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level:
            if not current_module:
                continue
            current_path = path.resolve().relative_to(VKCORE_SRC.resolve())
            package_parts = list(current_module.split("."))
            if current_path.name != "__init__.py":
                package_parts.pop()
            pop_count = node.level - 1
            if pop_count > len(package_parts) - 1:
                raise RuntimeError(f"invalid relative import in {path}: level={node.level}")
            if pop_count:
                package_parts = package_parts[:-pop_count]
            if node.module:
                package_parts.extend(node.module.split("."))
            base = ".".join(package_parts)
        else:
            base = node.module or ""
        if base == "vkcore" or base.startswith("vkcore."):
            if _vkcore_module_path(base) is None:
                raise FileNotFoundError(
                    f"local vkcore import {base!r} from {path} does not resolve"
                )
            modules.add(base)
            for alias in node.names:
                possible_submodule = f"{base}.{alias.name}"
                if _vkcore_module_path(possible_submodule) is not None:
                    modules.add(possible_submodule)
    return modules


def _vkcore_import_closure(seed_paths: list[Path]) -> list[Path]:
    """Resolve the transitive local ``vkcore`` source closure fail-closed."""

    pending = list(seed_paths)
    included: set[Path] = set()
    parsed: set[Path] = set()
    init = _vkcore_module_path("vkcore")
    if init is None:
        raise FileNotFoundError(f"vkcore package initializer is missing below {VKCORE_SRC}")
    included.add(init.resolve())
    pending.append(init)
    while pending:
        source = pending.pop().resolve()
        if source in parsed or not source.is_file():
            continue
        parsed.add(source)
        for module in _imported_vkcore_modules(source):
            target = _vkcore_module_path(module)
            if target is None:
                raise FileNotFoundError(
                    f"local vkcore import {module!r} from {source} does not resolve"
                )
            resolved = target.resolve()
            if resolved not in included:
                included.add(resolved)
                pending.append(resolved)
    return sorted(included)


def _source_inventory(*, include_audits: bool = True) -> list[dict[str, object]]:
    python_seeds = [
        *sorted((REPORT / "code").glob("*.py")),
        *sorted((REPO / "tests").glob("test_encounter*.py")),
        REPO / "tests" / "test_channel_mixture.py",
        REPO / "tests" / "test_dpma_2d_signed_spectrum.py",
        REPO / "tests" / "test_grid2d_encounter_audit.py",
        REPO / "tests" / "test_grid2d_reflecting_audit.py",
        REPO / "tests" / "test_peaks.py",
        REPO / "tests" / "test_ring_two_walker_encounter_shortcut.py",
        REPO / "tests" / "test_spectral.py",
        REPO / "tests" / "test_research_audit_artifacts.py",
        REPO / "tests" / "test_fpt.py",
        REPO / "tests" / "test_morphology.py",
        REPO / "tests" / "test_provenance.py",
    ]
    python_seeds = [path for path in python_seeds if path.is_file()]
    candidates = [
        REPORT / "README.md",
        MANUSCRIPT / "SUBMISSION_METADATA_REQUIRED.md",
        REPO / "pyproject.toml",
        REPO / "uv.lock",
        *python_seeds,
        *sorted((REPORT / "notes").glob("*.md")),
        *sorted(MANUSCRIPT.glob("*.tex")),
        *sorted(MANUSCRIPT.glob("*.bib")),
        *sorted(MANUSCRIPT.glob("*.txt")),
        *sorted(MANUSCRIPT.glob("*.md")),
        *_vkcore_import_closure(python_seeds),
        # Freeze the complete local package as a conservative backstop for
        # literal/dynamic imports and future nested modules.  The AST closure
        # above still fail-closes unresolved static imports.
        *sorted(VKCORE_SRC.rglob("*.py")),
        FORMAL / "README.md",
        FORMAL / "lakefile.toml",
        FORMAL / "lake-manifest.json",
        FORMAL / "lean-toolchain",
        FORMAL / "FormalLean.lean",
        *sorted(FORMAL.glob("*Axioms*.lean")),
        *sorted((FORMAL / "FormalLean").glob("*.lean")),
    ]
    if include_audits:
        candidates.extend(sorted((REPORT / "audits").glob("**/*.md")))
    rows: list[dict[str, object]] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen or not path.is_file():
            continue
        seen.add(resolved)
        rows.append(
            {
                "path": _relative(path),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return rows


def _formal_evidence() -> list[dict[str, object]]:
    """Inventory the exact reports validated by the current driver mapping."""

    payload = _formal_integrity_payload()
    report_rows = payload.get("axiom_reports")
    if not isinstance(report_rows, list):
        raise RuntimeError("formal integrity payload has no axiom-report inventory")
    rows: list[dict[str, object]] = []
    for report_row in report_rows:
        if not isinstance(report_row, dict) or "report" not in report_row:
            raise RuntimeError(f"malformed formal report row: {report_row}")
        path = REPO / str(report_row["report"])
        if not path.is_file():
            raise FileNotFoundError(f"formal axiom report is missing: {path}")
        rows.append(
            {
                "path": _relative(path),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return rows


def _git(*args: str) -> str | None:
    process = subprocess.run(
        ("git", *args),
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return process.stdout.strip() if process.returncode == 0 else None


def _git_start_snapshot() -> dict[str, object]:
    status = _git("status", "--porcelain")
    return {
        "commit": _git("rev-parse", "HEAD"),
        "branch": _git("branch", "--show-current"),
        "exact_tag": _git("describe", "--exact-match", "--tags", "HEAD"),
        "clean": status == "" if status is not None else None,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def _runtime_dependency_closure(errors: list[str]) -> dict[str, str]:
    """Resolve the installed dependency closure of all publication roots."""

    environment = default_environment()
    environment["extra"] = ""
    pending = [canonicalize_name(name) for name in RUNTIME_ROOT_PACKAGES]
    installed: dict[str, str] = {}
    while pending:
        name = pending.pop()
        if name in installed:
            continue
        try:
            distribution = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            errors.append(f"required runtime package is not installed: {name}")
            continue
        installed[name] = distribution.version
        for requirement_text in distribution.requires or ():
            try:
                requirement = Requirement(requirement_text)
            except InvalidRequirement as exc:
                errors.append(
                    f"installed metadata has an invalid requirement for {name}: "
                    f"{requirement_text!r}: {exc}"
                )
                continue
            if requirement.marker is not None and not requirement.marker.evaluate(
                environment
            ):
                continue
            dependency = canonicalize_name(requirement.name)
            if dependency not in installed:
                pending.append(dependency)
    return dict(sorted(installed.items()))


def _runtime_lock_evidence() -> dict[str, object]:
    lock_path = REPO / "uv.lock"
    errors: list[str] = []
    try:
        payload = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        payload = {}
        errors.append(f"could not read the runtime lock {lock_path}: {exc}")
    try:
        locked_versions: dict[str, set[str]] = {}
        for row in payload.get("package", []):
            if not isinstance(row, dict) or "name" not in row or "version" not in row:
                continue
            locked_versions.setdefault(canonicalize_name(str(row["name"])), set()).add(
                str(row["version"])
            )
    except (AttributeError, TypeError, ValueError) as exc:
        locked_versions = {}
        errors.append(f"runtime lock package table is malformed: {exc}")
    installed = _runtime_dependency_closure(errors)
    for name, version in installed.items():
        expected = locked_versions.get(name)
        if not expected:
            errors.append(f"required runtime package is absent from uv.lock: {name}")
        elif version not in expected:
            errors.append(
                f"runtime version mismatch for {name}: "
                f"installed={version} locked={sorted(expected)}"
            )
    try:
        lock_hash = _sha256(lock_path) if lock_path.is_file() else None
    except OSError as exc:
        lock_hash = None
        errors.append(f"could not hash the runtime lock {lock_path}: {exc}")
    return {
        "lock_path": _relative(lock_path),
        "lock_sha256": lock_hash,
        "root_packages": list(RUNTIME_ROOT_PACKAGES),
        "packages": {
            name: {
                "installed": installed[name],
                "locked": (
                    next(iter(locked_versions[name]))
                    if len(locked_versions.get(name, ())) == 1
                    else sorted(locked_versions.get(name, ()))
                ),
            }
            for name in sorted(installed)
        },
        "matches_lock": not errors,
        "errors": errors,
    }


def _command_version(
    command: str, *arguments: str, cwd: Path = REPO
) -> dict[str, object]:
    executable = shutil.which(command)
    if executable is None:
        return {"executable": None, "available": False, "version": None}
    process = subprocess.run(
        (executable, *arguments),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    first_line = next((line.strip() for line in process.stdout.splitlines() if line.strip()), "")
    return {
        "executable": str(Path(executable).resolve()),
        "cwd": _relative(cwd),
        "available": process.returncode == 0,
        "returncode": process.returncode,
        "version": first_line or None,
    }


def _tool_version_evidence() -> dict[str, object]:
    """Record exact interpreter and external-tool identities without hiding absence."""

    python_path = Path(sys.executable).absolute()
    return {
        "python": {
            "executable": str(python_path),
            "realpath": str(python_path.resolve()),
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "sha256": _sha256(python_path) if python_path.is_file() else None,
        },
        "git": _command_version("git", "--version"),
        "latexmk": _command_version("latexmk", "--version"),
        "pdfinfo": _command_version("pdfinfo", "-v"),
        "lake": _command_version("lake", "--version", cwd=FORMAL),
        "lean": _command_version("lean", "--version", cwd=FORMAL),
    }


def _inventory_digest(rows: list[dict[str, object]]) -> str:
    payload = json.dumps(
        rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _inventory_changes(
    before: list[dict[str, object]], after: list[dict[str, object]]
) -> list[str]:
    """Describe added, removed, or byte-changed source files deterministically."""

    before_map = {str(row["path"]): row for row in before}
    after_map = {str(row["path"]): row for row in after}
    changes = [f"added:{path}" for path in sorted(after_map.keys() - before_map.keys())]
    changes.extend(
        f"removed:{path}" for path in sorted(before_map.keys() - after_map.keys())
    )
    changes.extend(
        f"changed:{path}"
        for path in sorted(before_map.keys() & after_map.keys())
        if before_map[path] != after_map[path]
    )
    return changes


def _run(
    stage: Stage,
    *,
    env: dict[str, str],
    log_dir: Path | None = None,
) -> StageResult:
    if log_dir is None:
        log_dir = (
            LOGS
            / "adhoc"
            / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}-{os.getpid()}"
        )
    log_dir.mkdir(parents=True, exist_ok=True)
    log = log_dir / f"{stage.name}.log"
    started = datetime.now(timezone.utc)
    before = time.monotonic()
    process = subprocess.run(
        stage.command,
        cwd=stage.cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    duration = time.monotonic() - before
    validation_errors = _validate_lean_stage_output(stage.name, process.stdout)
    effective_returncode = process.returncode
    log_text = process.stdout
    if validation_errors:
        if effective_returncode == 0:
            effective_returncode = 97
        log_text += (
            "\nFORMAL_OUTPUT_VALIDATION_FAILURE\n- "
            + "\n- ".join(validation_errors)
            + "\n"
        )
    log.write_text(log_text, encoding="utf-8")
    result = StageResult(
        name=stage.name,
        command=list(stage.command),
        cwd=_relative(stage.cwd),
        started_at_utc=started.isoformat(),
        duration_seconds=duration,
        returncode=effective_returncode,
        log=_relative(log),
        log_bytes=log.stat().st_size,
        log_sha256=_sha256(log),
    )
    print(
        f"[{stage.name}] returncode={effective_returncode} "
        f"duration={duration:.2f}s"
    )
    return result


def _verification_stages() -> list[Stage]:
    pytest_command = (
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/test_encounter.py",
        "tests/test_encounter_biased.py",
        "tests/test_encounter_green_ctmc.py",
        "tests/test_encounter_green_formula_comparison.py",
        "tests/test_encounter_green_uniformization.py",
        "tests/test_encounter_green_spectral_artifact.py",
        "tests/test_encounter_gig_fold.py",
        "tests/test_encounter_modality_design.py",
        "tests/test_encounter_spectral_modality.py",
        "tests/test_encounter_multid_gig_design.py",
        "tests/test_encounter_2d.py",
        "tests/test_encounter_2d_artifacts.py",
        "tests/test_encounter_2d_atomic_artifacts.py",
        "tests/test_encounter_2d_mechanisms_artifacts.py",
        "tests/test_encounter_2d_matched_control_artifacts.py",
        "tests/test_encounter_2d_matched_fold.py",
        "tests/test_encounter_2d_matched_fold_artifacts.py",
        "tests/test_encounter_2d_trimodal_artifacts.py",
        "tests/test_encounter_2d_centre_coordinate_artifacts.py",
        "tests/test_encounter_2d_capacity_artifacts.py",
        "tests/test_encounter_3d.py",
        "tests/test_encounter_3d_artifacts.py",
        "tests/test_encounter_manuscript.py",
        "tests/test_encounter_publication_notebook.py",
        "tests/test_encounter_publication_pipeline.py",
        "tests/test_encounter_publication_workflow_hardening.py",
        "tests/test_encounter_reflecting_mean_validation.py",
        "tests/test_encounter_search.py",
        "tests/test_research_audit_artifacts.py",
        "tests/test_channel_mixture.py",
        "tests/test_dpma_2d_signed_spectrum.py",
        "tests/test_fpt.py",
        "tests/test_grid2d_encounter_audit.py",
        "tests/test_grid2d_reflecting_audit.py",
        "tests/test_morphology.py",
        "tests/test_peaks.py",
        "tests/test_provenance.py",
        "tests/test_ring_two_walker_encounter_shortcut.py",
        "tests/test_spectral.py",
    )
    stages = [
        Stage("pytest_publication_gates", pytest_command, ("verify",)),
        Stage(
            "lean4_static_integrity",
            _python("verify_lean_formal.py"),
            ("verify",),
        ),
    ]
    lake = shutil.which("lake")
    if lake is None:
        raise FileNotFoundError("lake is not on PATH; install elan before verification")
    formal_local = _prepare_lean_workspace()
    stages.extend(
        [
            Stage(
                "lean4_build",
                (lake, "build", *FORMAL_BUILD_TARGETS),
                ("verify",),
                formal_local,
            ),
            Stage(
                "lean4_legacy_axioms",
                (lake, "env", "lean", "AxiomsReport.lean"),
                ("verify",),
                formal_local,
            ),
            Stage(
                "lean4_encounter_axioms",
                (lake, "env", "lean", "EncounterAxioms.lean"),
                ("verify",),
                formal_local,
            ),
            Stage(
                "lean4_continuum_axioms",
                (lake, "env", "lean", "EncounterContinuumAxioms.lean"),
                ("verify",),
                formal_local,
            ),
            Stage(
                "lean4_design_axioms",
                (lake, "env", "lean", "EncounterDesignAxioms.lean"),
                ("verify",),
                formal_local,
            ),
        ]
    )
    return stages


def _profile_plan(profile: str) -> tuple[list[Stage], list[str], list[str]]:
    """Return executable stages and an independent fail-closed expectation.

    Verification preparation can fail before a ``Stage`` exists (for example,
    if ``lake`` or the local mathlib cache is absent).  The expected stage list
    must nevertheless remain complete so the attempted proof is recorded as
    incomplete instead of leaving an older passing manifest ambiguous.
    """

    if profile != "verify":
        selected = [stage for stage in _stages() if profile in stage.profiles]
        return selected, [stage.name for stage in selected], []
    try:
        selected = _verification_stages()
    except Exception as exc:
        return [], list(VERIFY_STAGE_NAMES), [f"verification preflight failed: {exc}"]
    observed_plan = [stage.name for stage in selected]
    failures = []
    if observed_plan != list(VERIFY_STAGE_NAMES):
        failures.append(
            "verification stage plan differs from the declared contract: "
            f"expected={list(VERIFY_STAGE_NAMES)} observed={observed_plan}"
        )
    return selected, list(VERIFY_STAGE_NAMES), failures


def _prepare_lean_workspace() -> Path:
    """Copy Lean sources off OneDrive while reusing the local mathlib cache."""

    if not (FORMAL / "lakefile.toml").is_file():
        raise FileNotFoundError(f"Lean project not found at {FORMAL}")
    target = LEAN_WORKSPACE_ROOT / f"run-{os.getpid()}"
    _cleanup_lean_workspace(target)
    try:
        target.mkdir(parents=True, exist_ok=False)
        for filename in LEAN_ROOT_FILES:
            shutil.copy2(FORMAL / filename, target / filename)
        shutil.copytree(FORMAL / "FormalLean", target / "FormalLean")
        source_inventory = _lean_workspace_inventory(FORMAL)
        copied_inventory = _lean_workspace_inventory(target)
        copy_changes = _inventory_changes(source_inventory, copied_inventory)
        if copy_changes:
            raise RuntimeError(
                "temporary Lean workspace differs from the frozen source copy: "
                + ", ".join(copy_changes)
            )

        shared_packages = (
            Path.home()
            / ".local-build"
            / "valley-k-small"
            / "formal_lean"
            / ".lake"
            / "packages"
        )
        if not shared_packages.is_dir():
            raise FileNotFoundError(
                "local mathlib cache is missing; run `lake exe cache get` in a local "
                f"copy first (expected {shared_packages})"
            )
        lake_dir = target / ".lake"
        lake_dir.mkdir(exist_ok=True)
        (lake_dir / "packages").symlink_to(
            shared_packages, target_is_directory=True
        )
        return target
    except Exception:
        _cleanup_lean_workspace(target)
        raise


def _lean_workspace_inventory(root: Path) -> list[dict[str, object]]:
    """Hash exactly the Lean project bytes copied into the local workspace."""

    candidates = [*(root / name for name in LEAN_ROOT_FILES)]
    candidates.extend(sorted((root / "FormalLean").glob("*.lean")))
    missing = [str(path) for path in candidates if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Lean workspace source is incomplete: {missing}")
    return [
        {
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in candidates
    ]


def _cleanup_lean_workspace(path: Path) -> None:
    """Remove only pipeline-owned ephemeral Lean workspaces."""

    root = LEAN_WORKSPACE_ROOT.resolve()
    resolved = path.resolve()
    if resolved.parent != root or not resolved.name.startswith("run-"):
        raise ValueError(f"refusing to remove non-pipeline Lean workspace: {path}")
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _manifest_base(
    profile: str,
    results: list[StageResult],
    *,
    include_audits: bool,
    expected_stages: list[str],
    failures: list[str],
    run_id: str,
    start_git: dict[str, object] | None = None,
    release_requested: bool = False,
    source_inventory_start: list[dict[str, object]] | None = None,
    source_inventory_end: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    status = _git("status", "--porcelain")
    start_sources = (
        _source_inventory(include_audits=False)
        if source_inventory_start is None
        else source_inventory_start
    )
    end_sources = start_sources if source_inventory_end is None else source_inventory_end
    source_changes = _inventory_changes(start_sources, end_sources)
    recorded_sources = (
        _source_inventory(include_audits=True) if include_audits else start_sources
    )
    return {
        "schema_version": 3,
        "profile": profile,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git": {
            "commit": _git("rev-parse", "HEAD"),
            "branch": _git("branch", "--show-current"),
            "dirty": None if status is None else bool(status),
        },
        "start_git": _git_start_snapshot() if start_git is None else start_git,
        "release": {
            "requested": release_requested,
            "start_gate_passed": bool(start_git)
            and start_git.get("clean") is True
            and bool(start_git.get("commit"))
            and bool(start_git.get("exact_tag")),
        },
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "deterministic_environment": dict(REPRODUCIBLE_STAGE_ENV),
            "tools": _tool_version_evidence(),
            "uv_lock": _runtime_lock_evidence(),
        },
        "source_freeze": {
            "start_count": len(start_sources),
            "end_count": len(end_sources),
            "start_sha256": _inventory_digest(start_sources),
            "end_sha256": _inventory_digest(end_sources),
            "unchanged": not source_changes,
            "changes": source_changes,
        },
        "execution": {
            "run_id": run_id,
            "expected_stages": expected_stages,
            "observed_stages": [result.name for result in results],
            "failures": failures,
            "complete": bool(expected_stages)
            and [result.name for result in results] == expected_stages
            and not failures
            and all(result.returncode == 0 for result in results),
        },
        "stages": [asdict(result) for result in results],
        "source_files": recorded_sources,
        "formal_evidence": _formal_evidence(),
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_attempt_sentinel(
    profile: str,
    *,
    run_id: str,
    expected_stages: list[str],
    start_git: dict[str, object],
    release_requested: bool,
) -> Path | None:
    """Reserve the latest attempt before preflight so crashes fail closed."""

    if profile not in {"full", "verify"}:
        return None
    attempts = DATA / "publication_pipeline_attempts"
    attempts.mkdir(parents=True, exist_ok=True)
    path = attempts / f"{profile}.{run_id}.manifest.json"
    payload: dict[str, object] = {
        "schema_version": 3,
        "profile": profile,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "start_git": start_git,
        "release": {
            "requested": release_requested,
            "start_gate_passed": False,
        },
        "execution": {
            "run_id": run_id,
            "expected_stages": expected_stages,
            "observed_stages": [],
            "failures": [
                "publication run started but did not reach its final manifest"
            ],
            "complete": False,
        },
        "stages": [],
    }
    _write_json(path, payload)
    return path


def _current_profile_stage_contract(profile: str) -> list[str]:
    if profile == "verify":
        return list(VERIFY_STAGE_NAMES)
    return [stage.name for stage in _stages() if profile in stage.profiles]


def _inventory_freshness_errors(
    label: str,
    stored: list[dict[str, object]],
    live: list[dict[str, object]],
) -> list[str]:
    """Require exact live coverage, including add-only inventory changes."""

    try:
        stored_paths = [str(row["path"]) for row in stored]
        live_paths = [str(row["path"]) for row in live]
    except (KeyError, TypeError) as exc:
        return [f"{label} inventory is malformed: {exc}"]
    errors: list[str] = []
    if len(stored_paths) != len(set(stored_paths)):
        errors.append(f"{label} stored inventory contains duplicate paths")
    if len(live_paths) != len(set(live_paths)):
        errors.append(f"{label} live inventory contains duplicate paths")
    changes = _inventory_changes(stored, live)
    if changes:
        errors.append(f"{label} live inventory differs: {changes}")
    return errors


def _profile_payload_errors(payload: dict[str, object]) -> list[str]:
    """Validate that one successful profile proof still matches live bytes."""

    errors: list[str] = []
    profile = str(payload.get("profile", ""))
    if payload.get("schema_version") != 3:
        errors.append(
            f"{profile or 'unknown'} profile schema is not the current version 3"
        )
    if profile not in {"full", "verify"}:
        errors.append(f"profile proof has an invalid identity: {profile!r}")
        return errors
    execution = payload.get("execution", {})
    if not isinstance(execution, dict) or not execution.get("complete", False):
        errors.append(f"{profile or 'unknown'} profile execution is not complete")
        return errors
    expected = _current_profile_stage_contract(profile)
    if execution.get("expected_stages") != expected:
        errors.append(
            f"{profile} expected-stage contract is stale: "
            f"stored={execution.get('expected_stages')} current={expected}"
        )
    if execution.get("observed_stages") != expected:
        errors.append(f"{profile} observed stages do not exactly match the contract")
    if execution.get("failures") != []:
        errors.append(f"{profile} execution retains failure rows")

    source_freeze = payload.get("source_freeze", {})
    if not isinstance(source_freeze, dict):
        errors.append(f"{profile} source freeze evidence is malformed")
        source_freeze = {}
    else:
        if source_freeze.get("unchanged") is not True:
            errors.append(
                f"{profile} sources changed during execution: "
                f"{source_freeze.get('changes', [])}"
            )
        if source_freeze.get("start_sha256") != source_freeze.get("end_sha256"):
            errors.append(f"{profile} pre/post source inventory hashes differ")
        if source_freeze.get("start_count") != source_freeze.get("end_count"):
            errors.append(f"{profile} pre/post source inventory counts differ")

    valid_sections: dict[str, list[dict[str, object]]] = {}
    for section in ("source_files", "formal_evidence", "outputs"):
        rows = payload.get(section, [])
        if not isinstance(rows, list):
            errors.append(f"{profile} {section} is not a list")
            continue
        valid = True
        seen_paths: set[str] = set()
        for row in rows:
            if (
                not isinstance(row, dict)
                or "path" not in row
                or "sha256" not in row
                or "bytes" not in row
            ):
                errors.append(f"{profile} has a malformed {section} row: {row}")
                valid = False
                continue
            row_path = str(row["path"])
            if row_path in seen_paths:
                errors.append(f"{profile} {section} contains duplicate path {row_path}")
                valid = False
            seen_paths.add(row_path)
            candidate = Path(str(row["path"]))
            if not candidate.is_absolute():
                candidate = REPO / candidate
            if not candidate.is_file():
                errors.append(f"{profile} {section} file is missing: {candidate}")
                valid = False
                continue
            if candidate.stat().st_size != row["bytes"]:
                errors.append(f"{profile} {section} byte count changed: {candidate}")
                valid = False
            if _sha256(candidate) != row["sha256"]:
                errors.append(f"{profile} {section} hash changed: {candidate}")
                valid = False
        if valid:
            valid_sections[section] = rows

    stored_sources = valid_sections.get("source_files")
    if stored_sources is not None:
        if source_freeze.get("start_count") != len(stored_sources):
            errors.append(f"{profile} source-freeze count does not match source rows")
        if source_freeze.get("start_sha256") != _inventory_digest(stored_sources):
            errors.append(f"{profile} source-freeze hash does not match source rows")
        try:
            live_sources = _source_inventory(include_audits=False)
        except Exception as exc:
            errors.append(f"{profile} live source inventory could not be built: {exc}")
        else:
            errors.extend(
                _inventory_freshness_errors(
                    f"{profile} source", stored_sources, live_sources
                )
            )

    stored_formal = valid_sections.get("formal_evidence")
    if stored_formal is not None:
        try:
            live_formal = _formal_evidence()
        except Exception as exc:
            errors.append(f"{profile} live formal evidence could not be built: {exc}")
        else:
            errors.extend(
                _inventory_freshness_errors(
                    f"{profile} formal evidence", stored_formal, live_formal
                )
            )

    stored_outputs = valid_sections.get("outputs")
    if stored_outputs is not None:
        try:
            live_outputs = _tracked_outputs(
                include_logs=False, include_audits=False
            )
        except Exception as exc:
            errors.append(f"{profile} live output inventory could not be built: {exc}")
        else:
            errors.extend(
                _inventory_freshness_errors(
                    f"{profile} output", stored_outputs, live_outputs
                )
            )

    stages = payload.get("stages", [])
    if not isinstance(stages, list):
        errors.append(f"{profile} stages is not a list")
        return errors
    stage_names: list[str] = []
    for row in stages:
        if not isinstance(row, dict) or not row.get("log"):
            errors.append(f"{profile} has a malformed stage row: {row}")
            continue
        stage_names.append(str(row.get("name", "")))
        if row.get("returncode") != 0:
            errors.append(
                f"{profile} stage {row.get('name', 'unknown')} has nonzero return code"
            )
        log = Path(str(row["log"]))
        if not log.is_absolute():
            log = REPO / log
        if not log.is_file():
            errors.append(f"{profile} stage log is missing: {log}")
            continue
        if log.stat().st_size != row.get("log_bytes"):
            errors.append(f"{profile} stage log byte count changed: {log}")
        if _sha256(log) != row.get("log_sha256"):
            errors.append(f"{profile} stage log hash changed: {log}")
    if stage_names != expected:
        errors.append(
            f"{profile} stage rows do not exactly match the current contract"
        )
    return errors


def _canonical_profile_errors(profile: str) -> list[str]:
    """Require a fresh success proof whose latest attempt is that success."""

    canonical = DATA / f"publication_pipeline.{profile}.manifest.json"
    if not canonical.is_file():
        return [f"canonical {profile} profile proof is missing: {canonical}"]
    try:
        payload = json.loads(canonical.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"canonical {profile} profile proof is unreadable: {exc}"]
    errors = []
    if payload.get("profile") != profile:
        errors.append(
            f"canonical {profile} proof contains profile {payload.get('profile')!r}"
        )
    errors.extend(_profile_payload_errors(payload))
    attempts = DATA / "publication_pipeline_attempts"
    candidates = sorted(attempts.glob(f"{profile}.*.manifest.json"))
    if not candidates:
        errors.append(f"no immutable {profile} attempt proof exists")
        return errors
    latest = candidates[-1]
    try:
        latest_payload = json.loads(latest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"latest {profile} attempt proof is unreadable: {exc}")
        return errors
    latest_execution = latest_payload.get("execution", {})
    canonical_execution = payload.get("execution", {})
    if not isinstance(latest_execution, dict) or not latest_execution.get(
        "complete", False
    ):
        errors.append(f"latest {profile} attempt is not complete: {latest}")
    if not isinstance(canonical_execution, dict) or latest_execution.get(
        "run_id"
    ) != canonical_execution.get("run_id"):
        errors.append(
            f"latest {profile} attempt does not match the canonical success"
        )
    if latest_payload != payload:
        errors.append(
            f"latest {profile} attempt payload is not content-identical "
            "to the canonical success"
        )
    return errors


def _attempt_manifest_rows() -> list[dict[str, object]]:
    """Hash every immutable full/verify attempt, not only the latest one."""

    attempts = DATA / "publication_pipeline_attempts"
    rows: list[dict[str, object]] = []
    for path in sorted(attempts.glob("*.manifest.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        execution = payload.get("execution", {})
        if not isinstance(execution, dict):
            raise RuntimeError(f"attempt manifest has malformed execution data: {path}")
        rows.append(
            {
                "profile": payload.get("profile"),
                "path": _relative(path),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "run_id": execution.get("run_id"),
                "complete": bool(execution.get("complete", False)),
            }
        )
    return rows


def _write_manifest(
    profile: str,
    results: list[StageResult],
    *,
    expected_stages: list[str] | None = None,
    failures: list[str] | None = None,
    run_id: str = "inventory-only",
    start_git: dict[str, object] | None = None,
    release_requested: bool = False,
    source_inventory_start: list[dict[str, object]] | None = None,
    source_inventory_end: list[dict[str, object]] | None = None,
) -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    manifest_path = DATA / "publication_pipeline.manifest.json"
    expected = [] if expected_stages is None else list(expected_stages)
    failure_rows = [] if failures is None else list(failures)
    postflight_errors: list[str] = []
    source_kwargs: dict[str, object] = {}
    if source_inventory_start is not None:
        source_kwargs["source_inventory_start"] = source_inventory_start
    if source_inventory_end is not None:
        source_kwargs["source_inventory_end"] = source_inventory_end
    if profile in {"full", "verify"}:
        run_payload = _manifest_base(
            profile,
            results,
            include_audits=False,
            expected_stages=expected,
            failures=failure_rows,
            run_id=run_id,
            start_git=start_git,
            release_requested=release_requested,
            **source_kwargs,
        )
        run_payload["outputs"] = _tracked_outputs(
            include_logs=False, include_audits=False
        )
        if bool(run_payload["execution"]["complete"]):
            postflight_errors.extend(_profile_payload_errors(run_payload))
            if profile == "verify":
                postflight_errors.extend(_canonical_profile_errors("full"))
        if postflight_errors:
            failure_rows.extend(
                f"publication proof postflight: {message}"
                for message in postflight_errors
            )
            run_payload = _manifest_base(
                profile,
                results,
                include_audits=False,
                expected_stages=expected,
                failures=failure_rows,
                run_id=run_id,
                start_git=start_git,
                release_requested=release_requested,
                **source_kwargs,
            )
            run_payload["outputs"] = _tracked_outputs(
                include_logs=False, include_audits=False
            )
        attempts = DATA / "publication_pipeline_attempts"
        attempts.mkdir(parents=True, exist_ok=True)
        attempt_path = attempts / f"{profile}.{run_id}.manifest.json"
        _write_json(attempt_path, run_payload)
        if bool(run_payload["execution"]["complete"]):
            canonical_path = DATA / f"publication_pipeline.{profile}.manifest.json"
            _write_json(canonical_path, run_payload)

    payload = _manifest_base(
        profile,
        results,
        include_audits=True,
        expected_stages=expected,
        failures=failure_rows,
        run_id=run_id,
        start_git=start_git,
        release_requested=release_requested,
        **source_kwargs,
    )
    profile_runs: list[dict[str, object]] = []
    for run_profile in ("full", "verify"):
        run_path = DATA / f"publication_pipeline.{run_profile}.manifest.json"
        if run_path.is_file():
            run_payload = json.loads(run_path.read_text(encoding="utf-8"))
            profile_runs.append(
                {
                    "profile": run_profile,
                    "path": _relative(run_path),
                    "bytes": run_path.stat().st_size,
                    "sha256": _sha256(run_path),
                    "stage_count": len(run_payload.get("stages", [])),
                    "all_stages_passed": bool(
                        run_payload.get("execution", {}).get("complete", False)
                    ),
                }
            )
    payload["profile_runs"] = profile_runs
    latest_attempts: list[dict[str, object]] = []
    attempts = DATA / "publication_pipeline_attempts"
    for run_profile in ("full", "verify"):
        candidates = sorted(attempts.glob(f"{run_profile}.*.manifest.json"))
        if candidates:
            attempt_path = candidates[-1]
            attempt_payload = json.loads(attempt_path.read_text(encoding="utf-8"))
            latest_attempts.append(
                {
                    "profile": run_profile,
                    "path": _relative(attempt_path),
                    "bytes": attempt_path.stat().st_size,
                    "sha256": _sha256(attempt_path),
                    "run_id": attempt_payload.get("execution", {}).get("run_id"),
                    "complete": bool(
                        attempt_payload.get("execution", {}).get("complete", False)
                    ),
                }
            )
    payload["latest_attempts"] = latest_attempts
    payload["attempt_runs"] = _attempt_manifest_rows()
    payload["outputs"] = _tracked_outputs(
        include_logs=True, include_audits=True
    )
    _write_json(manifest_path, payload)
    if postflight_errors:
        raise RuntimeError("\n".join(postflight_errors))
    return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=("quick", "full", "verify"),
        default="full",
        help="quick: core figures; full: all numerical evidence; verify: tests and Lean",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="record later independent stages after a failure (submission builds should omit this)",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="require that the run starts from a clean commit at an exact tag",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env = _stage_environment()
    start_git: dict[str, object] = {}
    results: list[StageResult] = []
    failures: list[str] = []
    selected: list[Stage] = []
    expected_stages = _current_profile_stage_contract(args.profile)
    source_inventory_start: list[dict[str, object]] | None = None
    source_inventory_end: list[dict[str, object]] | None = None
    formal_lock = None
    formal_workspace: Path | None = None
    pipeline_lock = None
    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        + f"-{os.getpid()}"
    )
    pipeline_lock_path = (
        Path.home()
        / ".local-build"
        / "valley-k-small"
        / "encounter_publication_pipeline.lock"
    )
    try:
        pipeline_lock = _acquire_workspace_lock(pipeline_lock_path)
        print(f"[publication_lock] acquired {pipeline_lock_path}")
    except WorkspaceLockUnavailable as exc:
        # The lock owner is the only process allowed to mutate the artifact
        # workspace.  In particular, do not write a failed attempt or aggregate
        # manifest here: doing so would race the winning run.
        print(str(exc), file=sys.stderr)
        raise SystemExit(75) from exc
    start_git = _git_start_snapshot()
    try:
        _write_attempt_sentinel(
            args.profile,
            run_id=run_id,
            expected_stages=expected_stages,
            start_git=start_git,
            release_requested=args.release,
        )
    except Exception:
        fcntl.flock(pipeline_lock.fileno(), fcntl.LOCK_UN)
        pipeline_lock.close()
        pipeline_lock = None
        raise
    if args.release:
        if start_git["clean"] is not True:
            failures.append("release run must start from a clean working tree")
        if not start_git["commit"]:
            failures.append("release run has no readable Git commit")
        if not start_git["exact_tag"]:
            failures.append("release run must start at an exact Git tag")
    runtime_errors = list(_runtime_lock_evidence()["errors"])
    if runtime_errors:
        failures.extend(runtime_errors)
    try:
        source_inventory_start = _source_inventory(include_audits=False)
    except Exception as exc:
        failures.append(f"could not freeze pre-run source inventory: {exc}")
    if not failures:
        selected, planned_stages, plan_failures = _profile_plan(args.profile)
        failures.extend(plan_failures)
        if planned_stages != expected_stages:
            failures.append(
                "profile plan differs from the declared stage contract: "
                f"expected={expected_stages} observed={planned_stages}"
            )
        formal_workspace = next(
            (
                stage.cwd
                for stage in selected
                if stage.name == "lean4_build"
                and stage.cwd.resolve().parent == LEAN_WORKSPACE_ROOT.resolve()
            ),
            None,
        )
    try:
        for stage in (() if failures else selected):
            try:
                if stage.name == "lean4_build" and formal_lock is None:
                    lock_path = (
                        Path.home()
                        / ".local-build"
                        / "valley-k-small"
                        / "formal_lean_pipeline.lock"
                    )
                    lock_path.parent.mkdir(parents=True, exist_ok=True)
                    formal_lock = lock_path.open("a+", encoding="utf-8")
                    try:
                        fcntl.flock(
                            formal_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB
                        )
                    except BlockingIOError as exc:
                        raise RuntimeError(
                            "another publication pipeline is using the shared "
                            f"Lean package cache ({lock_path})"
                        ) from exc
                    print(f"[lean4_lock] acquired {lock_path}")
                result = _run(
                    stage,
                    env=env,
                    log_dir=LOGS / args.profile / run_id,
                )
                results.append(result)
                if result.returncode:
                    log = REPO / result.log
                    tail = "\n".join(
                        log.read_text(encoding="utf-8").splitlines()[-40:]
                    )
                    failures.append(
                        f"stage {stage.name!r} failed; tail of {result.log}:\n{tail}"
                    )
                    if not args.keep_going:
                        break
            except Exception as exc:
                failures.append(str(exc))
                if not args.keep_going:
                    break
    finally:
        if formal_lock is not None:
            fcntl.flock(formal_lock.fileno(), fcntl.LOCK_UN)
            formal_lock.close()
        if formal_workspace is not None:
            try:
                _cleanup_lean_workspace(formal_workspace)
            except Exception as exc:
                failures.append(f"could not clean temporary Lean workspace: {exc}")
    try:
        source_inventory_end = _source_inventory(include_audits=False)
    except Exception as exc:
        failures.append(f"could not freeze post-run source inventory: {exc}")
    if source_inventory_start is not None and source_inventory_end is not None:
        source_changes = _inventory_changes(
            source_inventory_start, source_inventory_end
        )
        if source_changes:
            failures.append(
                "source inventory changed during publication run: "
                + ", ".join(source_changes)
            )
    try:
        manifest = _write_manifest(
            args.profile,
            results,
            expected_stages=expected_stages,
            failures=failures,
            run_id=run_id,
            start_git=start_git,
            release_requested=args.release,
            source_inventory_start=source_inventory_start,
            source_inventory_end=source_inventory_end,
        )
    finally:
        if pipeline_lock is not None:
            fcntl.flock(pipeline_lock.fileno(), fcntl.LOCK_UN)
            pipeline_lock.close()
    print(f"manifest={manifest}")
    if failures:
        raise RuntimeError("\n\n".join(failures))


if __name__ == "__main__":
    main()
