#!/usr/bin/env python3
"""Deterministic result-blind producer for the continuum C0-v2 candidate.

This producer never opens the historical scratch control/result payload, a
positive-budget design note, or the living continuum program.  It binds only
the five C0-only/control-free sources listed in ``FROZEN_SOURCES`` and keeps
the historical C0-v1 artifact byte-immutable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPORT = HERE.parents[1]
OUTPUT = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v2.json"
V1_PATH = REPORT / "artifacts/data/continuum_c0_model_contract_candidate_v1.json"
V1_SHA256 = "5bbe7d3c265736f98f0025a8aad80d83a53e464a5349d6b6be57a096ba9cdf66"

SCHEMA = "encounter_continuum_c0_model_contract_candidate_v2"
STATUS = "HOLD_C0_V2_CANDIDATE_RESULT_BLIND_MAPS_EXPLICIT_PRODUCTION_GAUGE_BRIDGE_OPEN"
PASS_CHECK = "PASS_C0_V2_REPRODUCIBLE_BUILD_CHECK_COMPLETE_C0_FALSE"
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_JSON_DEPTH = 128
MAX_JSON_NODES = 200_000
MAX_JSON_INTEGER_DIGITS = 128

FROZEN_SOURCES = {
    "configuration_family": {
        "path": "artifacts/data/physical_configuration_family_control_free_v1.json",
        "sha256": "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    },
    "control_method_commitment": {
        "path": "artifacts/data/continuum_c0_control_method_commitment_v2.json",
        "sha256": "288ad85d5992446a8f3b58416e445a88f1c15a4c71114ba008939d8fbd9a4a97",
    },
    "initial_source": {
        "path": "artifacts/data/physical_initial_analytic_source_v1.json",
        "sha256": "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f",
    },
    "killing_geometry_source": {
        "path": "artifacts/data/physical_killing_geometry_source_v1.json",
        "sha256": "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    },
    "mathematical_source": {
        "path": "artifacts/data/continuum_c0_mathematical_source_v2.json",
        "sha256": "522bd667e5f6fd6a4d12f270f0c2f4b9e86be9b207d471961d4f67db972df559",
    },
}

EXPECTED_SOURCE_TOP_KEYS = {
    "configuration_family": {
        "authority",
        "authorizes_scientific_execution",
        "axis_construction_contracts",
        "configuration_count",
        "configuration_order",
        "configurations",
        "contains_budget_value",
        "contains_control_values",
        "coordinate_order",
        "dynamics",
        "initial_geometry",
        "physical_dimension",
        "quotient_dimension",
        "schema",
        "scope",
        "status",
        "total_state_workload",
        "workload_semantics",
    },
    "control_method_commitment": {
        "constraints",
        "control_ids",
        "exclusions",
        "future_source",
        "schema",
        "status",
    },
    "initial_source": {
        "analytic_total_mass_exact",
        "construction",
        "coordinate_order",
        "half_width_binary64_hex",
        "marginal_density",
        "normalization",
        "periodic_coordinate",
        "periodic_wrap",
        "physical_dimension",
        "quotient_dimension",
        "schema",
        "scope",
        "shape_definition",
        "shared_normalizer_across_cells_and_axes",
        "starts_binary64_hex",
        "transverse_period_exact",
    },
    "killing_geometry_source": {
        "configuration_bundle",
        "contact_geometry",
        "coordinate_order",
        "flags",
        "physical_dimension",
        "quotient_dimension",
        "schema",
        "status",
        "support_basis",
    },
    "mathematical_source": {
        "boundary_contract",
        "field_convention",
        "gate_ownership",
        "identification_maps",
        "initial_law",
        "production_boundary",
        "row_generator_and_form",
        "schema",
        "stationary_mass_gauge",
        "status",
        "witnesses",
    },
}

FORBIDDEN_RESULT_KEYS = {
    "basin_mass",
    "control_weights",
    "mode_count_result",
    "peak_heights",
    "peak_time",
    "positive_budget_result",
    "root_interval",
    "root_times",
    "selected_weights",
    "scientific_result_values",
    "stationary_signature",
}

PHYSICAL_PARAMETERS = {
    "B": {
        "binary64_hex": "0x1.47ae147ae147bp-7",
        "exact": "5764607523034235/576460752303423488",
        "unit": "inverse_time_times_longitudinal_measure",
    },
    "D": {
        "binary64_hex": "0x1.0624dd2f1a9fcp-9",
        "exact": "1152921504606847/576460752303423488",
        "unit": "length_squared_per_time",
    },
    "W": {
        "binary64_hex": "0x1.0000000000000p+0",
        "exact": "1/1",
        "unit": "length",
    },
    "contact_radius_a": {
        "binary64_hex": "0x1.47ae147ae147bp-3",
        "exact": "5764607523034235/36028797018963968",
        "unit": "length",
    },
    "gamma": {
        "binary64_hex": "0x1.999999999999ap-4",
        "exact": "3602879701896397/36028797018963968",
        "unit": "inverse_time",
    },
    "zbar": {
        "binary64_hex": "0x1.e666666666666p-1",
        "exact": "4278419646001971/4503599627370496",
        "unit": "length",
    },
}

CONTINUUM_OBJECT = {
    "coordinate_order": ["midpoint_z", "relative_parallel", "relative_perpendicular"],
    "density_space": "X_pi=L2(pi^-1 dx)",
    "diffusion_matrix": ["D/2", "2*D", "2*D"],
    "drift": ["-gamma*(z-zbar)", "-gamma*relative_parallel", "0"],
    "form_core": "C_c_infinity(R^2)_tensor_C_infinity(T_W)",
    "form_domain": "weighted_H1_closure_of_form_core",
    "normalizer": "2*pi*D*W/gamma",
    "quotient": "R_z_times_R_relative_parallel_times_T_W",
    "reversible_density": (
        "normalizer^-1*exp(-gamma*(z-zbar)^2/D-gamma*relative_parallel^2/(4*D))"
    ),
    "weighted_state_space": "H=L2(pi dx)",
}

BOUNDARY_CONDITIONS = {
    "finite_box_midpoint": "reflecting_zero_flux_approximant_only",
    "finite_box_relative_parallel": "reflecting_zero_flux_approximant_only",
    "target_midpoint": "natural_decay_form_realization_no_reflecting_face",
    "target_relative_parallel": "natural_decay_form_realization_no_reflecting_face",
    "target_relative_perpendicular": "periodic_torus_exact",
}

EQUATION_CONTRACT = [
    "2.0",
    "2.1",
    "2.2",
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.6a",
    "2.7",
    "2.7a",
    "2.8",
    "2.8a",
    "2.9",
    "2.10",
    "2.11",
    "2.12",
    "2.13",
    "2.14",
    "2.15",
    "2.16",
    "2.17",
    "4.1",
    "4.2",
    "4.3",
    "4.4",
    "4.4a",
    "4.4b",
    "4.4c",
    "4.4d",
    "4.5",
    "4.5a",
    "4.5b",
]

CLAIM_BOUNDARY = {
    "c0a_operator_realization_proved": True,
    "complete_c0_independently_accepted": False,
    "c1_fixed_box_convergence_proved": False,
    "c2_quantitative_spatial_error_proved": False,
    "c3_derivative_box_error_proved": False,
    "continuum_stationary_topology_proved": False,
    "control_values_committed_for_c0": False,
    "f0_complete": False,
    "gauged_ideal_member_containment_proved_for_every_declared_configuration": False,
    "positive_budget_scientific_values_read": False,
    "production_centre_mosco_proved": False,
    "production_raw_to_gauged_bridge_proved": False,
    "release_eligible": False,
    "sealed_control_source_required_before_complete_c0": True,
}

MESH_CONTRACT = {
    "alignment_classes": [
        "cell_centred_reflecting",
        "vertex_centred_reflecting_dual",
        "cell_centred_periodic_base",
        "cell_centred_periodic_half_shift",
    ],
    "box_nesting_relations": [
        "O129/Base_midpoint_subset_M+_midpoint",
        "O129/Base_relative_subset_R+_relative",
        "M+_and_R+_product_equals_MR+_box",
        "MR+_box_equals_MR+F_box",
    ],
    "configuration_count": 12,
    "configuration_order": [
        "O113/Base",
        "E128/Base",
        "O129/Base",
        "O161/Base",
        "M+",
        "R+",
        "MR+",
        "MR+F",
        "A_M",
        "A_R",
        "A_Y",
        "A_MRY",
    ],
    "source_path": "artifacts/data/physical_configuration_family_control_free_v1.json",
}

INITIAL_LAW = {
    "analytic_mass_exact": "1/1",
    "initial_probability_cell_mass": "p0_h_i=integral_C_i_q0_dx",
    "initial_reference_mass": "pi_h_i",
    "meshwise_renormalization": False,
    "requirements": [
        "q0_in_X_pi",
        "q0_nonnegative",
        "integral_q0_dx_equals_one",
        "support_closure_strictly_inside_every_declared_nonperiodic_box",
    ],
    "source_path": "artifacts/data/physical_initial_analytic_source_v1.json",
    "support_certificate": {
        "configuration_count_checked": 12,
        "global_minimum_clearance_exact": (
            "106645239176133349/288230376151711744"
        ),
        "midpoint_support_closure_exact": [
            "34587645138205413/288230376151711744",
            "46116860184273883/288230376151711744",
        ],
        "nonperiodic_axes_checked": 24,
        "periodic_axes_checked": 12,
        "periodic_support_handled_as_wrapped_arc": True,
        "relative_parallel_support_closure_exact": [
            "-106645239176133339/288230376151711744",
            "-95116024130064869/288230376151711744",
        ],
        "strict_side_inequalities_checked": 48,
        "support_closure_strictly_inside_all_nonperiodic_boxes": True,
    },
    "unique_discrete_density_ratio": "u0_h_i=p0_h_i/pi_h_i=P_h[u0]_i",
}

KILLING_FIELD = {
    "contact": (
        "indicator(relative_parallel^2+minimum_image(relative_perpendicular)^2<=a^2)"
    ),
    "field": "W^-1*contact*sum_j(w_c_j*phi_j(midpoint))",
    "profile_count": 4,
    "profiles": "fixed_bounded_nonnegative_unit_integral_compact_bumps",
    "sharp_contact_retained": True,
}

SOURCE_POLICY = {
    "allowed_opened_source_roles": sorted(FROZEN_SOURCES),
    "embedded_source_paths_followed": False,
    "living_continuum_program_pinned": False,
    "opaque_scratch_or_result_payload_opened": False,
    "positive_budget_design_note_opened": False,
    "same_bytes_used_for_source_hash_and_parse": True,
}


class BuildHold(RuntimeError):
    """Fail-closed producer error."""


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode(
        "ascii"
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _no_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BuildHold(f"duplicate JSON key in source: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise BuildHold(f"nonfinite JSON value in source: {value}")


def _reject_float(value: str) -> Any:
    raise BuildHold(f"JSON float not allowed in exact source: {value}")


def _parse_int(value: str) -> int:
    if len(value.lstrip("-")) > MAX_JSON_INTEGER_DIGITS:
        raise BuildHold("JSON integer exceeds digit limit")
    try:
        return int(value)
    except ValueError as error:
        raise BuildHold("invalid JSON integer") from error


def _validate_json_bounds(value: Any) -> None:
    stack: list[tuple[Any, int]] = [(value, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if depth > MAX_JSON_DEPTH or nodes > MAX_JSON_NODES:
            raise BuildHold("source JSON exceeds nesting or node limit")
        if type(current) is dict:
            stack.extend((child, depth + 1) for child in current.values())
        elif type(current) is list:
            stack.extend((child, depth + 1) for child in current)


def parse_source_json(payload: bytes) -> dict[str, Any]:
    if len(payload) > MAX_FILE_BYTES:
        raise BuildHold("source bytes exceed size cap before JSON parsing")
    if payload.startswith(b"\xef\xbb\xbf") or not payload.endswith(b"\n"):
        raise BuildHold("source must be UTF-8 JSON with no BOM and one final newline")
    try:
        decoded = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_no_duplicate_pairs,
            parse_constant=_reject_constant,
            parse_float=_reject_float,
            parse_int=_parse_int,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, MemoryError, RecursionError, ValueError) as error:
        raise BuildHold("invalid UTF-8 JSON source") from error
    if type(decoded) is not dict:
        raise BuildHold("source top level must be an object")
    _validate_json_bounds(decoded)
    return decoded


def _normalize_key(key: str) -> str:
    first = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key)
    return re.sub(r"[^a-z0-9]+", "_", first.lower()).strip("_")


def _is_forbidden_payload_path(value: str) -> bool:
    lowered = value.lower().replace("\\", "/")
    segments = {segment for segment in lowered.split("/") if segment}
    exact_names = {
        "scratch",
        "result",
        "results",
        "control",
        "controls",
        "result.json",
        "results.json",
        "control.json",
        "controls.json",
    }
    forbidden_suffixes = (
        "_result.json",
        "-result.json",
        "_results.json",
        "-results.json",
        "_control.json",
        "-control.json",
        "_controls.json",
        "-controls.json",
    )
    return bool(segments & exact_names) or any(
        segment.endswith(forbidden_suffixes) for segment in segments
    )


def _scan_result_bearing(value: Any) -> None:
    stack: list[tuple[Any, int]] = [(value, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if depth > MAX_JSON_DEPTH or nodes > MAX_JSON_NODES:
            raise BuildHold("source JSON exceeds nesting or node limit")
        if type(current) is dict:
            for key, child in current.items():
                if _normalize_key(key) in FORBIDDEN_RESULT_KEYS:
                    raise BuildHold(f"result-bearing source key: {key}")
                stack.append((child, depth + 1))
        elif type(current) is list:
            stack.extend((child, depth + 1) for child in current)
        elif type(current) is str and _is_forbidden_payload_path(current):
            raise BuildHold(f"forbidden scratch/result/control path in source: {current}")


def _read_capped(fd: int, *, label: str) -> bytes:
    blocks: list[bytes] = []
    total = 0
    while True:
        block = os.read(fd, min(1 << 20, MAX_FILE_BYTES - total + 1))
        if not block:
            break
        total += len(block)
        if total > MAX_FILE_BYTES:
            raise BuildHold(f"frozen source grew beyond size cap: {label}")
        blocks.append(block)
    return b"".join(blocks)


def read_regular_snapshot(path: Path) -> bytes:
    if not hasattr(os, "O_NOFOLLOW"):
        raise BuildHold("platform lacks O_NOFOLLOW")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as error:
        raise BuildHold(f"cannot open frozen source: {path}") from error
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise BuildHold(f"frozen source is not a regular file: {path}")
        if before.st_size > MAX_FILE_BYTES:
            raise BuildHold(f"frozen source exceeds size cap: {path}")
        payload = _read_capped(fd, label=str(path))
        after = os.fstat(fd)
        try:
            named = os.lstat(path)
        except OSError as error:
            raise BuildHold(f"frozen source name changed during read: {path}") from error
        identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        if identity != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise BuildHold(f"frozen source changed during read: {path}")
        if stat.S_ISLNK(named.st_mode) or (named.st_dev, named.st_ino) != (
            before.st_dev,
            before.st_ino,
        ):
            raise BuildHold(f"frozen source path was replaced or linked: {path}")
        if len(payload) != before.st_size:
            raise BuildHold(f"frozen source size changed during read: {path}")
        return payload
    except OSError as error:
        raise BuildHold(f"frozen source read failed: {path}") from error
    finally:
        os.close(fd)


def read_relative_snapshot(root: Path, relative: Path) -> bytes:
    """Open every path component descriptor-relatively with no symlink following."""

    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise BuildHold(f"invalid frozen relative path: {relative}")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise BuildHold("platform lacks descriptor-safe directory flags")
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | os.O_NOFOLLOW
        | os.O_DIRECTORY
    )
    file_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW
    descriptors: list[int] = []
    try:
        parent_fd = os.open(root, directory_flags)
        descriptors.append(parent_fd)
        for component in relative.parts[:-1]:
            parent_fd = os.open(component, directory_flags, dir_fd=parent_fd)
            descriptors.append(parent_fd)
        file_fd = os.open(relative.name, file_flags, dir_fd=parent_fd)
        descriptors.append(file_fd)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode):
            raise BuildHold(f"frozen source is not regular: {relative}")
        if before.st_size > MAX_FILE_BYTES:
            raise BuildHold(f"frozen source exceeds size cap: {relative}")
        payload = _read_capped(file_fd, label=str(relative))
        after = os.fstat(file_fd)
        named = os.stat(relative.name, dir_fd=parent_fd, follow_symlinks=False)
        identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        if identity != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise BuildHold(f"frozen source changed during read: {relative}")
        if stat.S_ISLNK(named.st_mode) or (named.st_dev, named.st_ino) != (
            before.st_dev,
            before.st_ino,
        ):
            raise BuildHold(f"frozen source name changed during read: {relative}")
        if len(payload) != before.st_size:
            raise BuildHold(f"frozen source size changed during read: {relative}")
        return payload
    except OSError as error:
        raise BuildHold(f"cannot open frozen relative source: {relative}") from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def load_frozen_sources(*, report: Path = REPORT) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for role, descriptor in FROZEN_SOURCES.items():
        payload = read_relative_snapshot(report, Path(descriptor["path"]))
        if sha256_bytes(payload) != descriptor["sha256"]:
            raise BuildHold(f"frozen source hash mismatch: {role}")
        decoded = parse_source_json(payload)
        _scan_result_bearing(decoded)
        if set(decoded) != EXPECTED_SOURCE_TOP_KEYS[role]:
            raise BuildHold(f"frozen source top-level schema mismatch: {role}")
        # The initial source preserves a historical key ordering.  Its exact bytes
        # are SHA-pinned and receive the same duplicate/nonfinite/schema checks;
        # every newly authored source must additionally use canonical ordering.
        if role != "initial_source" and payload != canonical_json_bytes(decoded):
            raise BuildHold(f"frozen source is not canonical JSON: {role}")
        loaded[role] = decoded
    math_source = loaded["mathematical_source"]
    control_source = loaded["control_method_commitment"]
    if math_source.get("schema") != "encounter_continuum_c0_mathematical_source_v2":
        raise BuildHold("mathematical source schema mismatch")
    if control_source.get("schema") != "encounter_continuum_c0_control_method_commitment_v2":
        raise BuildHold("control method source schema mismatch")
    if control_source.get("exclusions", {}).get("actual_control_values_included") is not False:
        raise BuildHold("control method source is not result-blind")
    return loaded


def assert_v1_immutable(*, report: Path = REPORT) -> bytes:
    payload = read_relative_snapshot(report, V1_PATH.relative_to(REPORT))
    if sha256_bytes(payload) != V1_SHA256:
        raise BuildHold("historical C0-v1 bytes changed")
    return payload


def build_payload(*, report: Path = REPORT) -> dict[str, Any]:
    assert_v1_immutable(report=report)
    sources = load_frozen_sources(report=report)
    mathematics = sources["mathematical_source"]
    control = sources["control_method_commitment"]
    return {
        "boundary_conditions": BOUNDARY_CONDITIONS,
        "claim_boundary": CLAIM_BOUNDARY,
        "control_contract": control,
        "continuum_object": CONTINUUM_OBJECT,
        "discrete_operator_convention": mathematics["row_generator_and_form"],
        "equation_contract": EQUATION_CONTRACT,
        "finite_volume_identification": mathematics["identification_maps"],
        "frozen_sources": FROZEN_SOURCES,
        "initial_law": INITIAL_LAW,
        "killing_field": KILLING_FIELD,
        "mesh_contract": MESH_CONTRACT,
        "physical_dimension": 2,
        "physical_parameters": PHYSICAL_PARAMETERS,
        "previous_contract": {
            "path": "artifacts/data/continuum_c0_model_contract_candidate_v1.json",
            "sha256": V1_SHA256,
            "supersession_reason": (
                "result_blindness_repair_source_hash_drift_and_ambiguous_P_h_denominator"
            ),
            "v1_bytes_mutated": False,
        },
        "production_gauge_bridge": mathematics["production_boundary"],
        "quotient_dimension": 3,
        "scalar_convention": mathematics["field_convention"],
        "schema": SCHEMA,
        "source_policy": SOURCE_POLICY,
        "stationary_mass_gauge": mathematics["stationary_mass_gauge"],
        "status": STATUS,
        "witnesses": mathematics["witnesses"],
    }


def build_bytes(*, report: Path = REPORT) -> bytes:
    return canonical_json_bytes(build_payload(report=report))


def _exclusive_publish(path: Path, payload: bytes) -> None:
    if not path.is_absolute() or ".." in path.parts or not path.name:
        raise BuildHold(f"invalid publication path: {path}")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise BuildHold("platform lacks descriptor-safe publication flags")
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | os.O_NOFOLLOW | os.O_DIRECTORY
    )
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    temporary_name = f".{path.name}.tmp-{os.getpid()}"
    descriptors: list[int] = []
    temporary_created = False
    try:
        parent_fd = os.open(os.sep, directory_flags)
        descriptors.append(parent_fd)
        for component in path.parent.parts[1:]:
            if component in {"", ".", ".."}:
                raise BuildHold(f"invalid publication path component: {component!r}")
            parent_fd = os.open(component, directory_flags, dir_fd=parent_fd)
            descriptors.append(parent_fd)
        fd = os.open(temporary_name, file_flags, 0o644, dir_fd=parent_fd)
        temporary_created = True
        try:
            offset = 0
            while offset < len(payload):
                written = os.write(fd, payload[offset:])
                if written <= 0:
                    raise BuildHold("publication write made no progress")
                offset += written
            os.fsync(fd)
        finally:
            os.close(fd)
        os.link(
            temporary_name,
            path.name,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
            follow_symlinks=False,
        )
        os.fsync(parent_fd)
    finally:
        try:
            if temporary_created:
                try:
                    os.unlink(temporary_name, dir_fd=parent_fd)
                    os.fsync(parent_fd)
                except FileNotFoundError:
                    pass
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)


def _receipt(payload: bytes, action: str) -> dict[str, Any]:
    return {
        "action": action,
        "complete_c0": False,
        "contract_sha256": sha256_bytes(payload),
        "control_values_read": False,
        "opened_auxiliary_paths": [str(V1_PATH.relative_to(REPORT))],
        "opened_source_paths": [
            FROZEN_SOURCES[role]["path"] for role in sorted(FROZEN_SOURCES)
        ],
        "positive_budget_scientific_values_read": False,
        "release_eligible": False,
        "scratch_or_result_payload_read": False,
        "status": PASS_CHECK,
        "v1_sha256": V1_SHA256,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--create", action="store_true", help="create the v2 artifact once")
    mode.add_argument("--check", action="store_true", help="check the existing v2 artifact")
    args = parser.parse_args(argv)
    action = "create" if args.create else "check"
    try:
        expected = build_bytes()
        if args.create:
            if OUTPUT.exists() or OUTPUT.is_symlink():
                raise BuildHold("v2 output already exists; use --check and never overwrite")
            _exclusive_publish(OUTPUT, expected)
            observed = read_regular_snapshot(OUTPUT)
            if observed != expected:
                raise BuildHold("published v2 bytes differ from deterministic build")
        else:
            observed = read_regular_snapshot(OUTPUT)
            if observed != expected:
                raise BuildHold("published v2 bytes differ from deterministic build")
        assert_v1_immutable()
    except (BuildHold, FileExistsError, OSError) as error:
        print(json.dumps({"status": "HOLD_C0_V2_BUILD", "message": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(_receipt(observed, action), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
