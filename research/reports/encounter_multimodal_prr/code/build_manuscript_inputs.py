#!/usr/bin/env python3
"""Generate claim-gated TeX macros from frozen PRR result artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
DATA = REPORT / "artifacts" / "data"
DEFAULT_OUTPUT = REPORT / "manuscript" / "inputs" / "numerical_results.tex"
FOUR_PATCH = DATA / "continuum_observable_four_patch_result.json"
FOUR_PATCH_D3 = DATA / "continuum_observable_four_patch_d3_result.json"
G1C = DATA / "continuum_g1c_simplex_result.json"
G1D = DATA / "continuum_g1d_fold_confirmation_result.json"
BROAD_B0 = DATA / "continuum_broad_patch_b0_bridge_result.json"
NUMERICAL_SOURCE_MANIFEST = DATA / "manuscript_numerical_sources_manifest.json"
EXPECTED_NUMERICAL_SOURCE_MANIFEST_SHA256 = (
    "6ea29628e1cba423d37588b72a78dd3f5934f5e77b9c83df70394739375c88e7"
)

EXPECTED_RELEASE_SCOPE_FLAGS = {
    "d2": {
        "relative_shape_gate_passed": True,
        "event_mass_observability_verified": False,
        "finite_B_Doi_verified": False,
        "independent_PDE_solver_verified": False,
        "project_gate_passed": False,
    },
    "d3": {
        "relative_shape_gate_passed": True,
        "event_mass_observability_verified": False,
        "finite_B_Doi_verified": False,
        "independent_PDE_solver_verified": False,
        "project_gate_passed": False,
    },
    "g1c": {
        "candidate_seed_only": True,
        "continuum_verified": False,
        "project_gate_passed": False,
    },
    "g1d": {
        "finite_grid_fold_verified": True,
        "continuum_verified": False,
        "independent_PDE_solver_verified": False,
        "project_gate_passed": False,
    },
    "broad_b0": {
        "relative_shape_gate_passed": True,
        "event_mass_observability_verified": False,
        "finite_B_Doi_verified": False,
        "independent_PDE_solver_verified": False,
        "unbounded_domain_FV_limit_verified": False,
        "project_gate_passed": False,
        "legacy_positive_flag_alias": "exact_continuum_observability_passed",
    },
}
EXPECTED_RELEASE_KEYS = {
    "schema_version",
    "stage",
    "status",
    "claim_scope",
    "result_roles",
    "release_scope_flags",
    "families",
}
EXPECTED_RELEASE_STAGE = "prr_manuscript_numerical_source_closure"
EXPECTED_RELEASE_STATUS = "FROZEN_FIVE_FAMILY_SOURCE_CLOSURE"
EXPECTED_RELEASE_CLAIM_SCOPE = (
    "Fail-closed provenance closure for the five numerical families currently rendered "
    "into manuscript/inputs/numerical_results.tex. This is a source-integrity gate, "
    "not a scientific or release gate."
)
EXPECTED_RESULT_ROLES = {
    "d2": "d2.result",
    "d3": "d3.result",
    "g1c": "g1c.result",
    "g1d": "g1d.result",
    "broad_b0": "broad_b0.result",
}
EXPECTED_FAMILY_ROLES = {
    "d2": {"manifest", "producer", "protocol", "result", "test"},
    "d3": {"base_dependency", "manifest", "producer", "protocol", "result", "test"},
    "g1c": {
        "g1a_producer_dependency",
        "g1a_result_dependency",
        "g1b_producer_dependency",
        "g1b_result_dependency",
        "manifest",
        "manual_review_producer_dependency",
        "manual_review_result_dependency",
        "producer",
        "protocol",
        "result",
        "test",
    },
    "g1d": {
        "g1c_manifest_dependency",
        "g1c_result_dependency",
        "manifest",
        "producer",
        "protocol",
        "result",
        "test",
        "topology_review",
    },
    "broad_b0": {
        "exact_continuum_dependency",
        "finite_volume_dependency",
        "grid_dependency",
        "manifest",
        "producer",
        "protocol",
        "result",
        "test",
    },
}
EXPECTED_D2_KEYS = {
    "claim_flags",
    "cusp",
    "cusp_diagnostics",
    "evidence_timing",
    "gates",
    "inward_step_scan",
    "limitations",
    "model",
    "polar_contact_check",
    "provenance",
    "quadrature_and_cauchy_convergence",
    "schema_version",
    "selected_absolute_weight_fine_crosscheck",
    "selected_root_time_absolute_differences_primary_vs_fine",
    "stage",
    "status",
}
EXPECTED_D3_KEYS = {
    "claim_flags",
    "cusp",
    "cusp_diagnostics",
    "direct_spherical_coordinate_check",
    "evidence_timing",
    "gates",
    "inward_step_scan",
    "limitations",
    "model",
    "provenance",
    "quadrature_and_cauchy_convergence",
    "schema_version",
    "selected_absolute_weight_fine_crosscheck",
    "selected_root_time_absolute_differences_primary_vs_fine",
    "stage",
    "status",
}
EXPECTED_G1C_KEYS = {
    "candidate_rules",
    "checkpoint_integrity_ledger",
    "checkpoints",
    "claim_scope",
    "configuration",
    "configuration_hash",
    "continuum_verified",
    "controls",
    "evidence_role",
    "formal_frozen_run_completed",
    "limitations",
    "manifest_status_at_run",
    "outcome_policy",
    "pre_run_amendments",
    "project_gate_passed",
    "provenance",
    "run_mode",
    "runtime",
    "schema_version",
    "sequential_design_record",
    "shared_g1a_structural_foundation",
    "simplex_candidate_analysis",
    "stage",
    "status",
}
EXPECTED_G1D_KEYS = {
    "checks",
    "claim_scope",
    "configuration",
    "continuum_verified",
    "evidence_timing",
    "finite_B_Doi_fold",
    "finite_difference_check",
    "finite_grid_fold_confirmed",
    "fold",
    "foundation",
    "limitations",
    "newton_history",
    "project_gate_passed",
    "provenance",
    "schema_version",
    "selected_segment",
    "side_topology",
    "stage",
    "status",
}
EXPECTED_BROAD_KEYS = {
    "all_gates_passed",
    "bridge_control_selection",
    "claim_scope",
    "continuum_interval_verified",
    "convergence_summary",
    "evidence_timing",
    "exact_continuum",
    "exact_continuum_observability_passed",
    "finite_B_Doi_verified",
    "finite_volume_B0_bridge_passed",
    "finite_volume_mesh_rows",
    "gates",
    "limitations",
    "manifest_sha256",
    "numerical_reproducibility",
    "physical_parameters",
    "pinned_file_hashes",
    "preregistered_discovery",
    "project_gate_passed",
    "schema_version",
    "software",
    "stage",
    "status",
    "unbounded_domain_FV_limit_verified",
}
EXPECTED_D2_FLAGS = {
    "preregistered_discovery": False,
    "continuum_verified": False,
    "finite_B_Doi_verified": False,
    "project_gate_passed": False,
    "observable_free_exposure_confirmation_passed": True,
}
EXPECTED_D3_FLAGS = {
    "preregistered_discovery": False,
    "continuum_verified": False,
    "finite_B_Doi_verified": False,
    "independent_PDE_solver_verified": False,
    "project_gate_passed": False,
    "observable_d3_free_exposure_confirmation_passed": True,
}
EXPECTED_D2_LIMITATIONS = [
    "geometry, approximate cusp, and a passing inward step were known before freeze",
    "floating-point quadrature convergence is not interval certification",
    "the calculation is the B=0 derivative per unit full installed budget",
    "no explicit positive-B persistence radius or killed-Doi calculation is included",
    "no bounded-box SG/FEM or independent PDE solver is included",
    "no physical d=3 calculation is included",
]
EXPECTED_D3_LIMITATIONS = [
    "geometry, approximate cusp, and a passing inward step were known before freeze",
    "floating-point quadrature convergence is not interval certification",
    "the calculation is the B=0 derivative per unit full installed budget",
    "no explicit positive-B persistence radius or killed-Doi event mass is included",
    "no independent bounded-box PDE solver is included",
    "the result confirms this fixed four-slab geometry, not arbitrary geometries",
]
EXPECTED_G1C_LIMITATIONS = [
    "G1c is result-informed by G1b and its post-result manual review.",
    "The simplex is a finite discovery grid, not continuum verification.",
    "Boundary flags are diagnostics and cannot pass the interior family gate.",
    "Unmatched topology requires review and is never an automatic candidate.",
    "No candidate automatically selects a confirmation segment.",
    "No control sensitivity, continuation, convergence, tail, or independent-method gate is run.",
]
EXPECTED_G1D_LIMITATIONS = [
    "single 65x65x49 finite-volume mesh and one finite box",
    "result-informed segment selected after G1c",
    "no odd/even convergence or independent solver",
    "no continuum fold, cusp, trimodality, or project-gate claim",
]
EXPECTED_BROAD_LIMITATIONS = [
    "result-informed geometry and mesh trend, not preregistered discovery",
    "floating-point root screen, not interval-exhaustive certification",
    "finite-volume convergence is on one fixed reflecting box",
    "B=0 free exposure only; no positive-budget killed-Doi solve",
    "no physical d=3 calculation and no project or publication gate",
]
DANGEROUS_FALSE_CLAIM_KEYS = {
    "allocation_cusp_verified",
    "continuum_verified",
    "continuum_interval_verified",
    "event_mass_observability_verified",
    "finite_B_Doi_verified",
    "independent_PDE_solver_verified",
    "independent_solver_verified",
    "interval_global_root_proof",
    "observable_trimodality_verified",
    "physical_d3_verified",
    "preregistered_discovery",
    "project_gate_passed",
    "publication_gate_passed",
    "unbounded_domain_FV_limit_verified",
}


@dataclass(frozen=True)
class FileSnapshot:
    """One ordinary-file payload whose hash and parser see identical bytes."""

    path: Path
    sha256: str
    payload: bytes


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON constant {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _require_finite_json(value: object, *, label: str) -> None:
    if type(value) is float and not math.isfinite(value):
        raise ValueError(f"{label} contains a nonfinite number")
    if type(value) is dict:
        for key, item in value.items():
            _require_finite_json(item, label=f"{label}.{key}")
    elif type(value) is list:
        for index, item in enumerate(value):
            _require_finite_json(item, label=f"{label}[{index}]")


def _exact_json_equal(observed: object, expected: object) -> bool:
    if type(observed) is not type(expected):
        return False
    if type(expected) is dict:
        return set(observed) == set(expected) and all(
            _exact_json_equal(observed[key], expected[key]) for key in expected
        )
    if type(expected) is list:
        return len(observed) == len(expected) and all(
            _exact_json_equal(left, right)
            for left, right in zip(observed, expected, strict=True)
        )
    return observed == expected


def _exact_keys(value: object, expected: set[str], *, label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != expected:
        raise RuntimeError(f"{label} schema changed")
    return value


def _require_dangerous_claims_false(value: object, *, label: str) -> None:
    if type(value) is dict:
        for key, item in value.items():
            if key in DANGEROUS_FALSE_CLAIM_KEYS and item is not False:
                raise RuntimeError(f"{label} promotes dangerous claim key {key}")
            _require_dangerous_claims_false(item, label=label)
    elif type(value) is list:
        for item in value:
            _require_dangerous_claims_false(item, label=label)


def load_object_from_bytes(payload: bytes, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from error
    _require_finite_json(value, label=label)
    if type(value) is not dict:
        raise TypeError(f"{label} must contain one JSON object")
    return value


def load_object(path: Path) -> dict[str, Any]:
    return load_object_from_bytes(Path(path).read_bytes(), label=str(path))


def _snapshot_regular_file(path: Path, *, root: Path, label: str) -> FileSnapshot:
    """Read one contained ordinary file once without following any symlink component."""

    root = root.resolve(strict=True)
    candidate = Path(os.path.abspath(path))
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise RuntimeError(f"numerical source {label} escapes the report root") from error
    if not relative.parts:
        raise RuntimeError(f"numerical source {label} is not below the report root")

    current = root
    for index, component in enumerate(relative.parts):
        current = current / component
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError as error:
            raise FileNotFoundError(f"numerical source {label} is missing: {current}") from error
        if stat.S_ISLNK(mode):
            raise RuntimeError(f"numerical source {label} must be an ordinary nonsymlink file")
        if index < len(relative.parts) - 1 and not stat.S_ISDIR(mode):
            raise RuntimeError(f"numerical source {label} has a non-directory path component")
        if index == len(relative.parts) - 1 and not stat.S_ISREG(mode):
            raise RuntimeError(f"numerical source {label} must be an ordinary nonsymlink file")

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(candidate, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise RuntimeError(f"numerical source {label} must be an ordinary nonsymlink file")
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
            raise RuntimeError(f"numerical source {label} changed while read")
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    if len(payload) != after.st_size:
        raise RuntimeError(f"numerical source {label} was not read completely")
    return FileSnapshot(path=candidate, sha256=sha256_bytes(payload), payload=payload)


def _snapshot_report_path(report: Path, relative: object, *, label: str) -> FileSnapshot:
    if not isinstance(relative, str) or not relative:
        raise RuntimeError(f"numerical source {label} has an invalid relative path")
    raw = Path(relative)
    if raw.is_absolute() or ".." in raw.parts:
        raise RuntimeError(f"numerical source {label} has an invalid relative path")
    return _snapshot_regular_file(report / raw, root=report, label=label)


def _require_pin_matches(
    pin: dict[str, Any],
    *,
    path: object,
    digest: object,
    label: str,
) -> None:
    if path != pin["path"] or digest != pin["sha256"]:
        raise RuntimeError(
            f"nested numerical provenance mismatch for {label}: "
            f"expected ({pin['path']}, {pin['sha256']}), "
            f"observed ({path}, {digest})"
        )


def _require_schema_one(result: dict[str, Any], *, label: str) -> None:
    if type(result.get("schema_version")) is not int or result.get("schema_version") != 1:
        raise RuntimeError(f"{label} schema version changed")


def _validate_family_result(family: str, result: dict[str, Any]) -> None:
    """Freeze claim-bearing result identity before any value can reach TeX."""

    if family == "d2":
        _exact_keys(result, EXPECTED_D2_KEYS, label="d2 result")
        _require_schema_one(result, label="d2 result")
        if (
            result.get("stage") != "G1o_observable_four_patch_continuum_confirmation"
            or result.get("status")
            != "PASS_RESULT_INFORMED_OBSERVABLE_FREE_EXPOSURE_CONFIRMATION"
            or result.get("evidence_timing")
            != "RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY"
            or not _exact_json_equal(result.get("claim_flags"), EXPECTED_D2_FLAGS)
            or not _exact_json_equal(result.get("limitations"), EXPECTED_D2_LIMITATIONS)
        ):
            raise RuntimeError("d2 result identity or claim boundary changed")
    elif family == "d3":
        _exact_keys(result, EXPECTED_D3_KEYS, label="d3 result")
        _require_schema_one(result, label="d3 result")
        if (
            result.get("stage")
            != "G1p_observable_four_patch_physical_d3_exact_kernel_confirmation"
            or result.get("status")
            != "PASS_RESULT_INFORMED_PHYSICAL_D3_OBSERVABLE_FREE_EXPOSURE_CONFIRMATION"
            or result.get("evidence_timing")
            != "RESULT_INFORMED_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY"
            or not _exact_json_equal(result.get("claim_flags"), EXPECTED_D3_FLAGS)
            or not _exact_json_equal(result.get("limitations"), EXPECTED_D3_LIMITATIONS)
        ):
            raise RuntimeError("d3 result identity or claim boundary changed")
    elif family == "g1c":
        _exact_keys(result, EXPECTED_G1C_KEYS, label="G1c result")
        _require_schema_one(result, label="G1c result")
        if (
            result.get("stage") != "G1c_result_informed_full_simplex_discovery_not_confirmation"
            or result.get("status") != "G1C_SIMPLEX_COMPLETE_CANDIDATE_SEED_ONLY"
            or result.get("claim_scope")
            != "Result-informed sequential full-simplex grid discovery in one fixed physical "
            "family; candidate seeds only, never continuum fold or project-gate evidence"
            or result.get("evidence_role") != "prospective_result_informed_G1c_discovery_only"
            or result.get("run_mode") != "frozen_formal_G1c"
            or result.get("manifest_status_at_run") != "FROZEN_BEFORE_G1C_RUN"
            or result.get("formal_frozen_run_completed") is not True
            or result.get("continuum_verified") is not False
            or result.get("project_gate_passed") is not False
            or not _exact_json_equal(result.get("limitations"), EXPECTED_G1C_LIMITATIONS)
        ):
            raise RuntimeError("G1c result identity or claim boundary changed")
    elif family == "g1d":
        _exact_keys(result, EXPECTED_G1D_KEYS, label="G1d result")
        _require_schema_one(result, label="G1d result")
        if (
            result.get("stage") != "G1d_post_result_single_segment_finite_grid_fold_confirmation"
            or result.get("status") != "PASS_FINITE_GRID_FOLD_ONLY"
            or result.get("evidence_timing")
            != "POST_RESULT_CONFIRMATION_NOT_PREREGISTERED_DISCOVERY"
            or result.get("claim_scope") != "one result-informed finite-grid fold on the frozen G1 family"
            or result.get("finite_grid_fold_confirmed") is not True
            or result.get("finite_B_Doi_fold") is not True
            or result.get("continuum_verified") is not False
            or result.get("project_gate_passed") is not False
            or not _exact_json_equal(result.get("limitations"), EXPECTED_G1D_LIMITATIONS)
        ):
            raise RuntimeError("G1d result identity or claim boundary changed")
    elif family == "broad_b0":
        _exact_keys(result, EXPECTED_BROAD_KEYS, label="broad B0 result")
        _require_schema_one(result, label="broad B0 result")
        expected_flags = {
            "preregistered_discovery": False,
            "continuum_interval_verified": False,
            "finite_B_Doi_verified": False,
            "unbounded_domain_FV_limit_verified": False,
            "project_gate_passed": False,
            "exact_continuum_observability_passed": True,
            "finite_volume_B0_bridge_passed": True,
            "all_gates_passed": True,
        }
        if (
            result.get("stage") != "result_informed_broad_patch_B0_numerical_bridge"
            or result.get("status") != "PASS_RESULT_INFORMED_B0_NUMERICAL_BRIDGE"
            or result.get("evidence_timing")
            != "RESULT_INFORMED_NUMERICAL_BRIDGE_NOT_PREREGISTERED_DISCOVERY"
            or result.get("claim_scope")
            != "Exact unbounded-OU x periodic free-exposure observability plus a fixed-box, "
            "factorized, cell-centred Scharfetter-Gummel B=0 mesh bridge for one "
            "result-informed four-patch geometry only."
            or any(result.get(key) is not expected for key, expected in expected_flags.items())
            or not _exact_json_equal(result.get("limitations"), EXPECTED_BROAD_LIMITATIONS)
        ):
            raise RuntimeError("broad B0 result identity or claim boundary changed")
    else:  # pragma: no cover - the release family set is frozen above
        raise RuntimeError(f"unknown numerical family {family}")
    _require_dangerous_claims_false(result, label=f"{family} result")


def verify_numerical_sources(
    *,
    report: Path = REPORT,
    manifest_path: Path | None = None,
    expected_manifest_sha256: str = EXPECTED_NUMERICAL_SOURCE_MANIFEST_SHA256,
) -> dict[str, Any]:
    """Verify every manuscript numerical result and its complete pinned source chain."""

    report = report.resolve(strict=True)
    manifest_path = (
        report / "artifacts" / "data" / "manuscript_numerical_sources_manifest.json"
        if manifest_path is None
        else Path(manifest_path)
    )
    manifest_snapshot = _snapshot_regular_file(
        manifest_path, root=report, label="numerical-source manifest"
    )
    if manifest_snapshot.sha256 != expected_manifest_sha256:
        raise RuntimeError(
            "manuscript numerical-source manifest hash mismatch: "
            f"expected {expected_manifest_sha256}, observed {manifest_snapshot.sha256}"
        )
    release = load_object_from_bytes(
        manifest_snapshot.payload, label="manuscript numerical-source manifest"
    )
    _exact_keys(release, EXPECTED_RELEASE_KEYS, label="numerical-source manifest")
    if (
        type(release.get("schema_version")) is not int
        or release.get("schema_version") != 1
        or release.get("stage") != EXPECTED_RELEASE_STAGE
        or release.get("status") != EXPECTED_RELEASE_STATUS
        or release.get("claim_scope") != EXPECTED_RELEASE_CLAIM_SCOPE
    ):
        raise RuntimeError("numerical-source manifest schema or status is not frozen")
    if not _exact_json_equal(release.get("release_scope_flags"), EXPECTED_RELEASE_SCOPE_FLAGS):
        raise RuntimeError("release-level numerical scope flags are not fail-closed")
    families = release.get("families")
    expected_families = set(EXPECTED_FAMILY_ROLES)
    if type(families) is not dict or set(families) != expected_families:
        raise RuntimeError("numerical-source manifest does not contain exactly five families")
    if not _exact_json_equal(release.get("result_roles"), EXPECTED_RESULT_ROLES):
        raise RuntimeError("numerical-source result-role map is incomplete")

    resolved: dict[str, dict[str, dict[str, Any]]] = {}
    verified_files: list[dict[str, str]] = []
    snapshot_cache: dict[str, FileSnapshot] = {}
    for family_name in sorted(families):
        family = families[family_name]
        if type(family) is not dict or set(family) != EXPECTED_FAMILY_ROLES[family_name]:
            raise RuntimeError(f"numerical source family {family_name} is incomplete")
        resolved[family_name] = {}
        for role, raw_pin in family.items():
            label = f"{family_name}.{role}"
            if type(raw_pin) is not dict or set(raw_pin) != {"path", "sha256"}:
                raise RuntimeError(f"numerical source pin {label} is malformed")
            expected = raw_pin["sha256"]
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise RuntimeError(f"numerical source pin {label} has an invalid SHA-256")
            relative = raw_pin["path"]
            if not isinstance(relative, str) or not relative:
                raise RuntimeError(f"numerical source pin {label} has an invalid path")
            snapshot = snapshot_cache.get(relative)
            if snapshot is None:
                snapshot = _snapshot_report_path(report, relative, label=label)
                snapshot_cache[relative] = snapshot
            observed = snapshot.sha256
            if observed != expected:
                raise RuntimeError(
                    f"numerical source pin {label} hash mismatch: "
                    f"expected {expected}, observed {observed}"
                )
            row = {"role": label, "path": raw_pin["path"], "sha256": observed}
            resolved[family_name][role] = {**row, "snapshot": snapshot}
            verified_files.append(row)

    def pin(family: str, role: str) -> dict[str, Any]:
        return resolved[family][role]

    d2_result = load_object_from_bytes(
        pin("d2", "result")["snapshot"].payload, label="d2 result"
    )
    d2_manifest = load_object_from_bytes(
        pin("d2", "manifest")["snapshot"].payload, label="d2 manifest"
    )
    _validate_family_result("d2", d2_result)
    d2_provenance = d2_result.get("provenance")
    d2_frozen = d2_manifest.get("frozen_files")
    if type(d2_provenance) is not dict or type(d2_frozen) is not dict:
        raise RuntimeError("d2 result/manifest provenance is missing")
    for role, result_role, manifest_role in (
        ("manifest", "manifest", None),
        ("producer", "producer", "producer"),
        ("test", "test", "test"),
        ("protocol", "protocol", "protocol"),
    ):
        expected = pin("d2", role)
        _require_pin_matches(
            expected,
            path=d2_provenance.get(result_role),
            digest=d2_provenance.get(f"{result_role}_sha256"),
            label=f"d2.result.{result_role}",
        )
        if manifest_role is not None:
            _require_pin_matches(
                expected,
                path=d2_frozen.get(manifest_role),
                digest=d2_frozen.get(f"{manifest_role}_sha256"),
                label=f"d2.manifest.{manifest_role}",
            )

    d3_result = load_object_from_bytes(
        pin("d3", "result")["snapshot"].payload, label="d3 result"
    )
    d3_manifest = load_object_from_bytes(
        pin("d3", "manifest")["snapshot"].payload, label="d3 manifest"
    )
    _validate_family_result("d3", d3_result)
    d3_provenance = d3_result.get("provenance")
    d3_frozen = d3_manifest.get("frozen_files")
    if type(d3_provenance) is not dict or type(d3_frozen) is not dict:
        raise RuntimeError("d3 result/manifest provenance is missing")
    for role, result_role, manifest_role in (
        ("manifest", "manifest", None),
        ("producer", "producer", "producer"),
        ("test", "test", "test"),
        ("protocol", "protocol", "protocol"),
        ("base_dependency", "base_dependency", "base_dependency"),
    ):
        expected = pin("d3", role)
        _require_pin_matches(
            expected,
            path=d3_provenance.get(result_role),
            digest=d3_provenance.get(f"{result_role}_sha256"),
            label=f"d3.result.{result_role}",
        )
        if manifest_role is not None:
            _require_pin_matches(
                expected,
                path=d3_frozen.get(manifest_role),
                digest=d3_frozen.get(f"{manifest_role}_sha256"),
                label=f"d3.manifest.{manifest_role}",
            )

    g1c_result = load_object_from_bytes(
        pin("g1c", "result")["snapshot"].payload, label="G1c result"
    )
    g1c_manifest = load_object_from_bytes(
        pin("g1c", "manifest")["snapshot"].payload, label="G1c manifest"
    )
    _validate_family_result("g1c", g1c_result)
    g1c_provenance = g1c_result.get("provenance")
    if type(g1c_provenance) is not dict:
        raise RuntimeError("G1c result provenance is missing")
    for role, path_key, digest_key in (
        ("manifest", "manifest", "manifest_sha256"),
        ("producer", "g1c_code", "g1c_code_sha256"),
        ("protocol", "protocol_note", "protocol_note_sha256"),
    ):
        _require_pin_matches(
            pin("g1c", role),
            path=g1c_provenance.get(path_key),
            digest=g1c_provenance.get(digest_key),
            label=f"g1c.result.{path_key}",
        )
    g1c_frozen = g1c_manifest.get("frozen_implementation")
    if type(g1c_frozen) is not dict:
        raise RuntimeError("G1c frozen implementation is missing")
    _require_pin_matches(
        pin("g1c", "producer"),
        path=g1c_frozen.get("runner"),
        digest=g1c_frozen.get("runner_sha256"),
        label="g1c.manifest.runner",
    )
    _require_pin_matches(
        pin("g1c", "protocol"),
        path=g1c_frozen.get("protocol_note"),
        digest=g1c_frozen.get("protocol_note_sha256"),
        label="g1c.manifest.protocol",
    )
    g1c_inputs = g1c_provenance.get("pinned_input_preflight")
    g1c_required = g1c_manifest.get("required_inputs")
    if type(g1c_inputs) is not dict or type(g1c_required) is not dict:
        raise RuntimeError("G1c pinned inputs are missing")
    for input_name, result_role, producer_role in (
        ("g1a_foundation", "g1a_result_dependency", "g1a_producer_dependency"),
        ("g1b_formal_line", "g1b_result_dependency", "g1b_producer_dependency"),
        (
            "g1b_manual_review",
            "manual_review_result_dependency",
            "manual_review_producer_dependency",
        ),
    ):
        observed = g1c_inputs.get(input_name)
        required = g1c_required.get(input_name)
        if type(observed) is not dict or type(required) is not dict:
            raise RuntimeError(f"G1c input {input_name} has no nested provenance")
        for container, label in ((observed, "result"), (required, "manifest")):
            _require_pin_matches(
                pin("g1c", result_role),
                path=container.get("artifact"),
                digest=container.get("artifact_sha256"),
                label=f"g1c.{label}.{input_name}.artifact",
            )
            _require_pin_matches(
                pin("g1c", producer_role),
                path=container.get("producer_code"),
                digest=container.get("producer_code_sha256"),
                label=f"g1c.{label}.{input_name}.producer",
            )

    g1d_result = load_object_from_bytes(
        pin("g1d", "result")["snapshot"].payload, label="G1d result"
    )
    g1d_manifest = load_object_from_bytes(
        pin("g1d", "manifest")["snapshot"].payload, label="G1d manifest"
    )
    _validate_family_result("g1d", g1d_result)
    g1d_provenance = g1d_result.get("provenance")
    g1d_inputs = g1d_manifest.get("pinned_inputs")
    if type(g1d_provenance) is not dict or type(g1d_inputs) is not dict:
        raise RuntimeError("G1d result/manifest provenance is missing")
    _require_pin_matches(
        pin("g1d", "manifest"),
        path=g1d_provenance.get("manifest"),
        digest=g1d_provenance.get("manifest_sha256"),
        label="g1d.result.manifest",
    )
    _require_pin_matches(
        pin("g1d", "producer"),
        path=g1d_provenance.get("runner"),
        digest=g1d_provenance.get("runner_sha256"),
        label="g1d.result.runner",
    )
    for role, key in (
        ("protocol", "protocol_sha256"),
        ("topology_review", "topology_review_sha256"),
    ):
        expected = pin("g1d", role)["sha256"]
        if g1d_provenance.get(key) != expected or g1d_inputs.get(key) != expected:
            raise RuntimeError(f"nested numerical provenance mismatch for g1d.{role}")
    if g1d_inputs.get("runner_sha256") != pin("g1d", "producer")["sha256"]:
        raise RuntimeError("nested numerical provenance mismatch for g1d.runner")
    g1c_result_sha = pin("g1c", "result")["sha256"]
    if (
        pin("g1d", "g1c_result_dependency")["sha256"] != g1c_result_sha
        or g1d_provenance.get("g1c_result_sha256") != g1c_result_sha
        or g1d_inputs.get("g1c_result_sha256") != g1c_result_sha
    ):
        raise RuntimeError("G1d-to-G1c nested result hash is not closed")
    g1c_manifest_sha = pin("g1c", "manifest")["sha256"]
    if (
        pin("g1d", "g1c_manifest_dependency")["sha256"] != g1c_manifest_sha
        or g1d_inputs.get("g1c_manifest_sha256") != g1c_manifest_sha
    ):
        raise RuntimeError("G1d-to-G1c nested manifest hash is not closed")

    broad_result = load_object_from_bytes(
        pin("broad_b0", "result")["snapshot"].payload, label="broad B0 result"
    )
    broad_manifest = load_object_from_bytes(
        pin("broad_b0", "manifest")["snapshot"].payload, label="broad B0 manifest"
    )
    _validate_family_result("broad_b0", broad_result)
    broad_pins = broad_manifest.get("pinned_files")
    broad_result_pins = broad_result.get("pinned_file_hashes")
    if type(broad_pins) is not dict or type(broad_result_pins) is not dict:
        raise RuntimeError("broad-patch pinned provenance is missing")
    if broad_result.get("manifest_sha256") != pin("broad_b0", "manifest")["sha256"]:
        raise RuntimeError("broad-patch result does not pin its manifest")
    broad_roles = {
        "producer": "producer",
        "tests": "test",
        "protocol": "protocol",
        "exact_continuum_dependency": "exact_continuum_dependency",
        "finite_volume_dependency": "finite_volume_dependency",
        "grid_dependency": "grid_dependency",
    }
    for manifest_role, release_role in broad_roles.items():
        raw = broad_pins.get(manifest_role)
        if type(raw) is not dict:
            raise RuntimeError(f"broad-patch manifest pin {manifest_role} is missing")
        expected = pin("broad_b0", release_role)
        _require_pin_matches(
            expected,
            path=raw.get("path"),
            digest=raw.get("sha256"),
            label=f"broad_b0.manifest.{manifest_role}",
        )
        if broad_result_pins.get(manifest_role) != expected["sha256"]:
            raise RuntimeError(
                f"broad-patch result pin {manifest_role} does not match the release manifest"
            )

    public_families: dict[str, dict[str, dict[str, str]]] = {}
    for family_name, roles in resolved.items():
        public_families[family_name] = {
            role: {key: value for key, value in row.items() if key != "snapshot"}
            for role, row in roles.items()
        }
    return {
        "manifest": str(manifest_snapshot.path.relative_to(report)),
        "manifest_sha256": expected_manifest_sha256,
        "families": public_families,
        "verified_files": verified_files,
        "result_objects": {
            "d2": d2_result,
            "d3": d3_result,
            "g1c": g1c_result,
            "g1d": g1d_result,
            "broad_b0": broad_result,
        },
        "snapshots": snapshot_cache,
    }


def tex_sci(value: float, digits: int = 2) -> str:
    mantissa, exponent = f"{value:.{digits}e}".split("e")
    return rf"{mantissa}\times10^{{{int(exponent)}}}"


def macro(name: str, value: str) -> str:
    return rf"\providecommand{{\{name}}}{{{value}}}"


def render_verified_macros(verified: dict[str, Any]) -> str:
    """Render only from result objects parsed from the verified same-byte snapshots."""

    families = verified.get("families")
    snapshots = verified.get("snapshots")
    expected_families = {"d2", "d3", "g1c", "g1d", "broad_b0"}
    if type(families) is not dict or set(families) != expected_families:
        raise RuntimeError("verified numerical family set is incomplete")
    if type(snapshots) is not dict:
        raise RuntimeError("verified numerical snapshot set is missing")
    objects: dict[str, dict[str, Any]] = {}
    for family in expected_families:
        result_row = families[family]["result"]
        snapshot = snapshots.get(result_row["path"])
        if (
            type(snapshot) is not FileSnapshot
            or sha256_bytes(snapshot.payload) != snapshot.sha256
            or snapshot.sha256 != result_row["sha256"]
        ):
            raise RuntimeError(f"verified {family} result snapshot identity changed")
        objects[family] = load_object_from_bytes(
            snapshot.payload, label=f"verified {family} result snapshot"
        )
        _validate_family_result(family, objects[family])
    four = objects["d2"]
    d3 = objects["d3"]
    g1c = objects["g1c"]
    g1d = objects["g1d"]
    broad = objects["broad_b0"]

    if four.get("status") != "PASS_RESULT_INFORMED_OBSERVABLE_FREE_EXPOSURE_CONFIRMATION":
        raise RuntimeError("four-patch artifact has no passing confirmation status")
    if four.get("claim_flags") != {
        "preregistered_discovery": False,
        "continuum_verified": False,
        "finite_B_Doi_verified": False,
        "project_gate_passed": False,
        "observable_free_exposure_confirmation_passed": True,
    }:
        raise RuntimeError("four-patch claim flags are not fail-closed as expected")
    if d3.get("status") != (
        "PASS_RESULT_INFORMED_PHYSICAL_D3_OBSERVABLE_FREE_EXPOSURE_CONFIRMATION"
    ):
        raise RuntimeError("physical-d=3 four-patch artifact has no passing confirmation status")
    if d3.get("claim_flags") != {
        "preregistered_discovery": False,
        "continuum_verified": False,
        "finite_B_Doi_verified": False,
        "independent_PDE_solver_verified": False,
        "project_gate_passed": False,
        "observable_d3_free_exposure_confirmation_passed": True,
    }:
        raise RuntimeError("physical-d=3 four-patch claim flags are not fail-closed")
    if g1c.get("status") != "G1C_SIMPLEX_COMPLETE_CANDIDATE_SEED_ONLY":
        raise RuntimeError("G1c artifact is not the completed candidate-only result")
    if g1d.get("status") != "PASS_FINITE_GRID_FOLD_ONLY":
        raise RuntimeError("G1d artifact has no finite-grid-only pass")
    if not g1d.get("finite_grid_fold_confirmed") or not g1d.get("finite_B_Doi_fold"):
        raise RuntimeError("G1d finite-grid fold flags are missing")
    if g1d.get("continuum_verified") or g1d.get("project_gate_passed"):
        raise RuntimeError("G1d artifact improperly promotes continuum/project scope")
    if broad.get("status") != "PASS_RESULT_INFORMED_B0_NUMERICAL_BRIDGE":
        raise RuntimeError("broad-patch B=0 artifact has no bridge-only pass")
    expected_broad_flags = {
        "preregistered_discovery": False,
        "continuum_interval_verified": False,
        "finite_B_Doi_verified": False,
        "unbounded_domain_FV_limit_verified": False,
        "project_gate_passed": False,
        "exact_continuum_observability_passed": True,
        "finite_volume_B0_bridge_passed": True,
        "all_gates_passed": True,
    }
    for name, expected in expected_broad_flags.items():
        if broad.get(name) is not expected:
            raise RuntimeError(f"broad-patch B=0 flag {name} is not fail-closed")

    cusp = four["cusp"]
    selected = four["inward_step_scan"]["selected"]
    structure = selected["stationary_structure"]
    roots = structure["roots"]
    if [row["topology"] for row in roots] != [
        "maximum",
        "minimum",
        "maximum",
        "minimum",
        "maximum",
    ]:
        raise RuntimeError("four-patch root topology is not max-min-max-min-max")
    convergence = four["quadrature_and_cauchy_convergence"]
    cusp_times = [float(row["cusp_time"]) for row in convergence]
    weight_rows = [row["weights"] for row in convergence]
    time_spread = max(cusp_times) - min(cusp_times)
    weight_spread = max(
        abs(float(left) - float(right))
        for row in weight_rows
        for other in weight_rows
        for left, right in zip(row, other, strict=True)
    )
    primary = next(row for row in convergence if row["label"] == "primary")
    fine = next(row for row in convergence if row["label"] == "fine")
    fourth_difference = abs(
        float(primary["scaled_fourth_derivative"]) - float(fine["scaled_fourth_derivative"])
    )
    d3_cusp = d3["cusp"]
    d3_selected = d3["inward_step_scan"]["selected"]
    d3_structure = d3_selected["stationary_structure"]
    d3_roots = d3_structure["roots"]
    if [row["topology"] for row in d3_roots] != [
        "maximum",
        "minimum",
        "maximum",
        "minimum",
        "maximum",
    ]:
        raise RuntimeError("physical-d=3 root topology is not max-min-max-min-max")
    d3_convergence = {row["label"]: row for row in d3["quadrature_and_cauchy_convergence"]}
    d3_primary = d3_convergence["primary"]
    d3_fine = d3_convergence["fine"]
    d3_time_difference = abs(float(d3_fine["cusp_time"]) - float(d3_primary["cusp_time"]))
    d3_weight_difference = max(
        abs(float(left) - float(right))
        for left, right in zip(d3_fine["weights"], d3_primary["weights"], strict=True)
    )
    d3_fourth_difference = abs(
        float(d3_fine["scaled_fourth_derivative"]) - float(d3_primary["scaled_fourth_derivative"])
    )
    d3_root_difference = max(
        float(value) for value in d3["selected_root_time_absolute_differences_primary_vs_fine"]
    )

    analysis = g1c["simplex_candidate_analysis"]
    fold = g1d["fold"]
    scaled = fold["scaled_fold_jet"]
    side_topology = g1d["side_topology"]
    if [row["root_count"] for row in side_topology] != [3, 1]:
        raise RuntimeError("G1d side screen is not the declared 3-versus-1 result")
    bridge_selection = broad["bridge_control_selection"]
    bridge_selected = bridge_selection["selected"]
    broad_cusp = broad["exact_continuum"]["primary_cusp"]
    broad_weights = bridge_selection["exact_continuum_selected_stationary_structure"]["weights"]
    if not bridge_selected["required_meshes_observable"] or float(bridge_selected["step"]) != 0.13:
        raise RuntimeError("broad-patch bridge did not retain the frozen selected control")
    cusp_errors = [
        float(value) for value in broad["convergence_summary"]["cusp_time_absolute_errors"]
    ]
    root_errors = [
        float(value)
        for value in broad["convergence_summary"]["maximum_fixed_control_root_time_absolute_errors"]
    ]
    if any(right >= left for left, right in zip(cusp_errors, cusp_errors[1:])):
        raise RuntimeError("broad-patch cusp errors are not strictly decreasing")
    if any(right >= left for left, right in zip(root_errors, root_errors[1:])):
        raise RuntimeError("broad-patch root errors are not strictly decreasing")

    values = [
        macro("FourPatchCuspTime", f"{float(cusp['time']):.10f}"),
        macro(
            "FourPatchCuspWeights",
            ",".join(f"{float(value):.8f}" for value in cusp["weights"]),
        ),
        macro(
            "FourPatchMaxResidual",
            tex_sci(max(abs(float(value)) for value in cusp["scaled_residuals_orders_1_to_3"])),
        ),
        macro("FourPatchScaledFourth", f"{float(cusp['scaled_fourth_derivative']):.4f}"),
        macro(
            "FourPatchSvdRatio",
            f"{float(cusp['unfolding']['dimensionless_svd_ratio']):.6f}",
        ),
        macro("FourPatchSelectedStep", f"{float(selected['step']):.2f}"),
        macro(
            "FourPatchSelectedWeights",
            ",".join(f"{float(value):.8f}" for value in selected["weights"]),
        ),
        macro("FourPatchRootOne", f"{float(roots[0]['time']):.5f}"),
        macro("FourPatchRootTwo", f"{float(roots[1]['time']):.5f}"),
        macro("FourPatchRootThree", f"{float(roots[2]['time']):.5f}"),
        macro("FourPatchRootFour", f"{float(roots[3]['time']):.5f}"),
        macro("FourPatchRootFive", f"{float(roots[4]['time']):.5f}"),
        macro(
            "FourPatchPeakRatio",
            f"{float(structure['peak_minimum_to_maximum_ratio']):.5f}",
        ),
        macro(
            "FourPatchValleyOne",
            f"{float(structure['valley_to_smaller_adjacent_peak_ratios'][0]):.5f}",
        ),
        macro(
            "FourPatchValleyTwo",
            f"{float(structure['valley_to_smaller_adjacent_peak_ratios'][1]):.5f}",
        ),
        macro("FourPatchCuspTimeSpread", tex_sci(time_spread)),
        macro("FourPatchWeightSpread", tex_sci(weight_spread)),
        macro("FourPatchFourthDifference", tex_sci(fourth_difference)),
        macro(
            "FourPatchPolarDifference",
            tex_sci(float(four["polar_contact_check"]["maximum_relative_difference"])),
        ),
        macro(
            "FourPatchRootDifference",
            tex_sci(
                max(
                    float(value)
                    for value in four["selected_root_time_absolute_differences_primary_vs_fine"]
                )
            ),
        ),
        macro("DThreeCuspTime", f"{float(d3_cusp['time']):.10f}"),
        macro(
            "DThreeCuspWeights",
            ",".join(f"{float(value):.8f}" for value in d3_cusp["weights"]),
        ),
        *[
            macro(f"DThreeCuspWeight{index}", f"{float(value):.8f}")
            for index, value in zip(("One", "Two", "Three", "Four"), d3_cusp["weights"])
        ],
        macro(
            "DThreeScaledFourth",
            f"{float(d3_cusp['scaled_fourth_derivative']):.4f}",
        ),
        macro(
            "DThreeSvdRatio",
            f"{float(d3_cusp['unfolding']['dimensionless_svd_ratio']):.6f}",
        ),
        macro("DThreeSelectedStep", f"{float(d3_selected['step']):.2f}"),
        macro(
            "DThreeSelectedWeights",
            ",".join(f"{float(value):.8f}" for value in d3_selected["weights"]),
        ),
        *[
            macro(f"DThreeSelectedWeight{index}", f"{float(value):.8f}")
            for index, value in zip(("One", "Two", "Three", "Four"), d3_selected["weights"])
        ],
        macro("DThreeRootOne", f"{float(d3_roots[0]['time']):.5f}"),
        macro("DThreeRootTwo", f"{float(d3_roots[1]['time']):.5f}"),
        macro("DThreeRootThree", f"{float(d3_roots[2]['time']):.5f}"),
        macro("DThreeRootFour", f"{float(d3_roots[3]['time']):.5f}"),
        macro("DThreeRootFive", f"{float(d3_roots[4]['time']):.5f}"),
        macro(
            "DThreePeakRatio",
            f"{float(d3_structure['peak_minimum_to_maximum_ratio']):.5f}",
        ),
        macro(
            "DThreeValleyOne",
            f"{float(d3_structure['valley_to_smaller_adjacent_peak_ratios'][0]):.5f}",
        ),
        macro(
            "DThreeValleyTwo",
            f"{float(d3_structure['valley_to_smaller_adjacent_peak_ratios'][1]):.5f}",
        ),
        macro(
            "DThreeSphericalDifference",
            tex_sci(float(d3["direct_spherical_coordinate_check"]["maximum_relative_difference"])),
        ),
        macro("DThreeCuspTimeDifference", tex_sci(d3_time_difference)),
        macro("DThreeWeightDifference", tex_sci(d3_weight_difference)),
        macro("DThreeFourthDifference", tex_sci(d3_fourth_difference)),
        macro("DThreeRootDifference", tex_sci(d3_root_difference)),
        macro(
            "DThreeEligibleCount",
            str(int(d3["inward_step_scan"]["eligible_count"])),
        ),
        macro("GOneCControlCount", str(len(g1c["controls"]))),
        macro("GOneCEdgeCount", str(int(analysis["simplex_edge_count"]))),
        macro("GOneCSeedCount", str(int(analysis["eligible_candidate_seed_count"]))),
        macro(
            "GOneCManualReviewCount",
            str(int(analysis["unmatched_topology_manual_review_count"])),
        ),
        macro("GOneDFoldTime", f"{float(fold['time']):.10f}"),
        macro("GOneDFoldControl", f"{float(fold['control']):.10f}"),
        macro(
            "GOneDFoldWeights",
            ",".join(f"{float(value):.8f}" for value in fold["weights"]),
        ),
        macro("GOneDFoldWeightOne", f"{float(fold['weights'][0]):.8f}"),
        macro("GOneDFoldWeightTwo", f"{float(fold['weights'][1]):.8f}"),
        macro("GOneDFoldWeightThree", f"{float(fold['weights'][2]):.8f}"),
        macro("GOneDFoldDensity", f"{float(fold['density']):.10f}"),
        macro("GOneDScaledFt", tex_sci(float(scaled["f_t"]))),
        macro("GOneDScaledFtt", tex_sci(float(scaled["f_tt"]))),
        macro("GOneDScaledFttt", f"{float(scaled['f_ttt']):.4f}"),
        macro("GOneDScaledFtlambda", f"{float(scaled['f_tlambda']):.5f}"),
        macro("GOneDScaledFttlambda", f"{float(scaled['f_ttlambda']):.5f}"),
        macro(
            "GOneDJacobianDeterminant",
            f"{float(fold['dimensionless_jacobian_determinant']):.5f}",
        ),
        macro("BroadBZeroSelectedStep", f"{float(bridge_selected['step']):.2f}"),
        macro("BroadBZeroCuspTime", f"{float(broad_cusp['time']):.8f}"),
        macro(
            "BroadBZeroScaledFourth",
            f"{float(broad_cusp['scaled_fourth_derivative']):.4f}",
        ),
        macro(
            "BroadBZeroSvdRatio",
            f"{float(broad_cusp['unfolding']['dimensionless_svd_ratio']):.4f}",
        ),
        macro(
            "BroadBZeroSelectedWeights",
            ",".join(f"{float(value):.5f}" for value in broad_weights),
        ),
        macro(
            "BroadBZeroCuspErrors",
            ",".join(f"{value:.4f}" for value in cusp_errors),
        ),
        macro(
            "BroadBZeroRootErrors",
            ",".join(f"{value:.4f}" for value in root_errors),
        ),
        macro("BroadBZeroFinestCuspError", f"{cusp_errors[-1]:.5f}"),
        macro("BroadBZeroFinestRootError", f"{root_errors[-1]:.5f}"),
        macro(
            "BroadBZeroWorstValleyMargin",
            f"{float(bridge_selected['worst_valley_margin_across_required_meshes']):.5f}",
        ),
    ]
    header = [
        "% Generated by code/build_manuscript_inputs.py; do not edit by hand.",
        f"% numerical-source manifest SHA-256: {verified['manifest_sha256']}",
        f"% four-patch SHA-256: {verified['families']['d2']['result']['sha256']}",
        f"% physical-d=3 four-patch SHA-256: {verified['families']['d3']['result']['sha256']}",
        f"% G1c SHA-256: {verified['families']['g1c']['result']['sha256']}",
        f"% G1d SHA-256: {verified['families']['g1d']['result']['sha256']}",
        f"% broad-patch B=0 bridge SHA-256: {verified['families']['broad_b0']['result']['sha256']}",
    ]
    return "\n".join([*header, *values, ""])


def render_macros(
    *,
    report: Path = REPORT,
    manifest_path: Path | None = None,
    expected_manifest_sha256: str = EXPECTED_NUMERICAL_SOURCE_MANIFEST_SHA256,
) -> str:
    verified = verify_numerical_sources(
        report=report,
        manifest_path=manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,
    )
    return render_verified_macros(verified)


def write_atomic(output: Path, text: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.",
        suffix=".tmp",
        dir=output.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        Path(temporary_name).replace(output)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    write_atomic(args.output, render_macros())
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
