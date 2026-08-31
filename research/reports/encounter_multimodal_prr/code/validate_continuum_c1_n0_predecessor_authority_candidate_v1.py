#!/usr/bin/env python3
"""Independently validate the Round-177 predecessor-authority package.

The validator does not import or execute the builder.  It takes stable,
descriptor-relative snapshots of the atomic package, reopens every pinned
source independently, reconstructs all 36 level-n=0 partitions from the
Round-172 formulas, and derives the expected member, method, policy, manifest,
external-review-request, and bundle objects from those retained bytes.

This remains a non-promoting structural check.  No blocker is cleared and no
local process, child process, or subagent review is treated as an external
predecessor commitment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import unicodedata
from collections import Counter
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
DEFAULT_PACKAGE: Final = REPORT / (
    "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1"
)
PACKAGE_REPORT_RELATIVE: Final = Path(
    "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1"
)

MEMBER_NAME: Final = "continuum_c1_c2_n0_member_spec_v3_candidate.json"
PARAMETER_NAME: Final = "continuum_c1_c2_n0_method_parameter_registry_v2_candidate.json"
METHOD_NAME: Final = "continuum_c1_c2_n0_outward_method_registry_v2_candidate.json"
POLICY_NAME: Final = "continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate.json"
MANIFEST_NAME: Final = "continuum_c1_c2_n0_predecessor_authority_candidate_manifest_v1.json"
SEAL_REQUEST_NAME: Final = "continuum_c1_c2_n0_external_commitment_review_request_v1.json"
BUNDLE_NAME: Final = "bundle.json"
PACKAGE_NAMES: Final = (
    MEMBER_NAME,
    PARAMETER_NAME,
    METHOD_NAME,
    POLICY_NAME,
    MANIFEST_NAME,
    SEAL_REQUEST_NAME,
    BUNDLE_NAME,
)

BUILDER_RELATIVE: Final = "code/build_continuum_c1_n0_predecessor_authority_candidate_v1.py"
VALIDATOR_RELATIVE: Final = "code/validate_continuum_c1_n0_predecessor_authority_candidate_v1.py"
STATIC_TEST_RELATIVE: Final = "code/test_continuum_c1_n0_predecessor_authority_candidate_v1.py"
MUTATION_TEST_RELATIVE: Final = (
    "code/test_continuum_c1_n0_predecessor_authority_candidate_mutations_v1.py"
)

COORDINATES: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)
PROFILE_ORDER: Final = (0, 1, 2, 3)
EXPECTED_ALIGNMENTS: Final = {
    "cell_centred_periodic_base": 10,
    "cell_centred_periodic_half_shift": 2,
    "cell_centred_reflecting": 20,
    "vertex_centred_reflecting_dual": 4,
}
EXPECTED_COUNTS: Final = {
    "axis_count": 36,
    "axis_cell_count": 5_037,
    "axis_edge_count": 5_013,
    "configuration_count": 12,
    "periodic_seam_count": 12,
    "profile_index_count": 48,
    "total_virtual_tensor_state_count": 34_787_462,
}

SOURCE_PINS: Final = {
    "reference_density_source": (
        "artifacts/data/continuum_c1_reference_density_source_v1.json",
        "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575",
    ),
    "ideal_formula_source": (
        "artifacts/data/continuum_c1_ideal_formula_source_v1.json",
        "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be",
    ),
    "factorization_source": (
        "artifacts/data/continuum_c1_factorization_source_v1.json",
        "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca",
    ),
    "configuration_source": (
        "artifacts/data/physical_configuration_family_control_free_v1.json",
        "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    ),
    "legacy_member_spec": (
        "artifacts/data/continuum_c1_c2_fixed_row_member_spec_v1.json",
        "e2166e62ae2e5e67a8e3eb058fe4333f59192525ca5614939f417ba285d8d2ef",
    ),
    "legacy_policy": (
        "artifacts/data/continuum_c1_c2_fixed_row_anti_vacuity_policy_v1.json",
        "c8b9f3aca2b3a516935eeb1fdfb2bf542ba0da2d12ae4c11581f6f1ee607f628",
    ),
    "round176_member_candidate": (
        "artifacts/data/continuum_c1_c2_n0_member_spec_v2.json",
        "cbf967d795648fe5c433ed827d1365e70b84ff1a2444811e3a14244abedadc21",
    ),
    "round176_policy_candidate": (
        "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v2.json",
        "7e36369a9a1e22aa9c2c256ff8eaa4a0c8bf973316e2b6265247c8beff4ddb13",
    ),
    "joint_refinement_family": (
        "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json",
        "1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9",
    ),
    "initial_partition_bundle": (
        "artifacts/data/physical_production_initial_stream_v1/bundle.json",
        "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e",
    ),
    "symbolic_control_method_source": (
        "artifacts/data/continuum_c1_symbolic_control_method_source_v1.json",
        "fd6edf9046956d311366ff51f229523ab605d80073515b9768d5fa5cafa8904f",
    ),
    "control_method_commitment": (
        "artifacts/data/continuum_c0_control_method_commitment_v2.json",
        "288ad85d5992446a8f3b58416e445a88f1c15a4c71114ba008939d8fbd9a4a97",
    ),
    "killing_geometry_authority": (
        "artifacts/data/physical_killing_geometry_source_v1.json",
        "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    ),
}

CODE_PATHS: Final = {
    "stationary_producer": "code/build_continuum_c1_stationary_integral_source_v1.py",
    "stationary_verifier": "code/validate_continuum_c1_stationary_integral_source_v1.py",
    "raw_flux_producer": "code/build_continuum_c1_fixed_row_raw_flux_source_v1.py",
    "raw_flux_verifier": "code/validate_continuum_c1_fixed_row_raw_flux_source_v1.py",
    "killing_producer": "code/rate_defined_tensor_f0_production_killing_geometry.py",
    "killing_verifier": "code/rate_defined_tensor_f0_production_killing_geometry_independent.py",
    "killing_f0_core": "code/rate_defined_tensor_f0.py",
    "killing_partition_producer": "code/rate_defined_tensor_f0_production_initial_stream.py",
    "killing_uniformization_dependency": "code/verified_uniformization_enclosure.py",
}

CLAIM_KEYS: Final = (
    "backend_independence_claimed",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "external_predecessor_commitment_present",
    "formal_outer_open_operation_model_present",
    "formal_selected_source_dag_complete",
    "formal_symbolic_candidate_materialized",
    "one_correlated_distinguished_ideal_member_is_contained",
    "ordered_roles_8_10_replay_executed",
    "policy_predecessor_order_independently_sealed",
    "production_same_member_bridge_accepted",
    "release_eligible",
    "root_transfer_complete",
    "science_executed",
    "submission_eligible",
    "symbolic_acceptance_receipt_materialized",
)
BLOCKERS: Final = (
    "B01_current_roles_8_9_bind_legacy_member_spec_v1",
    "B02_policy_predecessor_order_not_independently_sealed",
    "B03_current_enclosures_predate_no_sealed_v2_policy",
    "B04_round172_has_no_partition_sha256",
    "B05_killing_rows_lack_member_native_provenance",
    "B06_method_registry_missing_code_and_parameter_hashes",
    "B07_formal_outer_open_operation_model_and_complete_dag_absent",
    "B08_exact_dag_interval_replay_absent",
    "B09_independent_symbolic_acceptance_receipt_absent",
)
RESERVED_BASENAMES: Final = {
    "encounter_c1_gauge_killing_symbolic_candidate_v1.json",
    "encounter_c1_gauge_killing_symbolic_acceptance_receipt_v1.json",
}


class CandidateValidationError(ValueError):
    """A strict package or predecessor-source invariant failed."""


def file_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_json_tree(value: Any, depth: int = 0) -> None:
    if depth > 64:
        raise CandidateValidationError("JSON depth cap exceeded")
    if isinstance(value, float):
        raise CandidateValidationError("JSON floating literals are forbidden")
    if type(value) in (bool, int) or value is None:
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise CandidateValidationError("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_json_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise CandidateValidationError("non-NFC or non-string JSON key")
            _strict_json_tree(item, depth + 1)
        return
    raise CandidateValidationError(f"forbidden JSON type: {type(value).__name__}")


def canonical_json(value: Any) -> bytes:
    _strict_json_tree(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def domain_sha256(domain: str, value: Any) -> str:
    return file_sha256(domain.encode("ascii") + b"\x00" + canonical_json(value))


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise CandidateValidationError(f"duplicate or invalid JSON key: {key!r}")
        result[key] = value
    return result


def _reject_noninteger(token: str) -> Any:
    raise CandidateValidationError(f"non-integer JSON number forbidden: {token}")


def decode_canonical(payload: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=_unique_object,
            parse_float=_reject_noninteger,
            parse_constant=_reject_noninteger,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise CandidateValidationError(f"strict JSON failure for {context}: {error}") from error
    if type(value) is not dict:
        raise CandidateValidationError(f"top-level JSON object required: {context}")
    if canonical_json(value) != payload:
        raise CandidateValidationError(f"canonical JSON byte drift: {context}")
    return value


def exact_tree_equal(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return set(actual) == set(expected) and all(
            exact_tree_equal(actual[key], expected[key]) for key in expected
        )
    if type(expected) is list:
        return len(actual) == len(expected) and all(
            exact_tree_equal(left, right) for left, right in zip(actual, expected, strict=True)
        )
    return actual == expected


def require_exact(actual: Any, expected: Any, context: str) -> None:
    if not exact_tree_equal(actual, expected):
        raise CandidateValidationError(f"semantic drift: {context}")


def require_false_claims(value: Any, context: str) -> None:
    expected = {key: False for key in CLAIM_KEYS}
    require_exact(value, expected, f"{context} claim boundary")


def safe_report_relative(value: Any) -> Path:
    if type(value) is not str:
        raise CandidateValidationError(f"report-relative path must be a string: {value!r}")
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or not pure.parts
        or "." in pure.parts
        or ".." in pure.parts
        or pure.as_posix() != value
    ):
        raise CandidateValidationError(f"unsafe report-relative path: {value!r}")
    return Path(*pure.parts)


def reject_symlink_components(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        info = os.lstat(current)
        if stat.S_ISLNK(info.st_mode):
            raise CandidateValidationError(f"path contains symlink component: {current}")


def file_stat_signature(item: os.stat_result) -> tuple[int, ...]:
    return (
        item.st_dev,
        item.st_ino,
        item.st_mode,
        item.st_nlink,
        item.st_size,
        item.st_mtime_ns,
        item.st_ctime_ns,
    )


def directory_stat_signature(item: os.stat_result) -> tuple[int, ...]:
    return (
        item.st_dev,
        item.st_ino,
        item.st_mode,
        item.st_mtime_ns,
        item.st_ctime_ns,
    )


def stable_file_snapshot(path: Path, *, cap: int = 8_000_000) -> bytes:
    absolute = Path(os.path.abspath(path))
    reject_symlink_components(absolute)
    if not hasattr(os, "O_NOFOLLOW"):
        raise CandidateValidationError("O_NOFOLLOW is required")
    descriptor = os.open(
        absolute,
        os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
    )
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size <= 0 or before.st_size > cap:
            raise CandidateValidationError(f"bounded regular file required: {path}")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                raise CandidateValidationError(f"short read: {path}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise CandidateValidationError(f"file grew during read: {path}")
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if file_stat_signature(before) != file_stat_signature(after):
        raise CandidateValidationError(f"file changed during snapshot: {path}")
    named = os.lstat(absolute)
    if (named.st_dev, named.st_ino) != (after.st_dev, after.st_ino):
        raise CandidateValidationError(f"file path replaced during snapshot: {path}")
    return b"".join(chunks)


def snapshot_atomic_package(package: Path) -> dict[str, bytes]:
    if not package.is_absolute():
        raise CandidateValidationError("--package must be an absolute path")
    reject_symlink_components(package)
    lexical = os.lstat(package)
    if not stat.S_ISDIR(lexical.st_mode):
        raise CandidateValidationError("package path must be a directory")
    flags = os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_DIRECTORY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(package, flags)
    try:
        before_dir = os.fstat(directory)
        names_before = sorted(os.listdir(directory))
        if RESERVED_BASENAMES.intersection(names_before):
            raise CandidateValidationError("reserved formal candidate/receipt basename present")
        if names_before != sorted(PACKAGE_NAMES):
            raise CandidateValidationError("atomic package filename inventory drift")
        snapshots: dict[str, bytes] = {}
        for name in PACKAGE_NAMES:
            descriptor = os.open(
                name,
                os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory,
            )
            try:
                before = os.fstat(descriptor)
                if (
                    not stat.S_ISREG(before.st_mode)
                    or before.st_nlink != 1
                    or before.st_size <= 0
                    or before.st_size > 8_000_000
                    or before.st_mode & 0o222
                ):
                    raise CandidateValidationError(
                        f"immutable single-link regular package file required: {name}"
                    )
                chunks: list[bytes] = []
                remaining = before.st_size
                while remaining:
                    chunk = os.read(descriptor, min(65_536, remaining))
                    if not chunk:
                        raise CandidateValidationError(f"short package read: {name}")
                    chunks.append(chunk)
                    remaining -= len(chunk)
                if os.read(descriptor, 1):
                    raise CandidateValidationError(f"package file grew during read: {name}")
                after = os.fstat(descriptor)
                named = os.stat(name, dir_fd=directory, follow_symlinks=False)
            finally:
                os.close(descriptor)
            if file_stat_signature(before) != file_stat_signature(after):
                raise CandidateValidationError(f"package file changed during read: {name}")
            if (named.st_dev, named.st_ino) != (after.st_dev, after.st_ino):
                raise CandidateValidationError(f"package entry replaced during read: {name}")
            snapshots[name] = b"".join(chunks)
        names_after = sorted(os.listdir(directory))
        after_dir = os.fstat(directory)
    finally:
        os.close(directory)
    if names_after != names_before or directory_stat_signature(
        before_dir
    ) != directory_stat_signature(after_dir):
        raise CandidateValidationError("package directory changed during snapshot")
    final_named = os.lstat(package)
    if (final_named.st_dev, final_named.st_ino) != (after_dir.st_dev, after_dir.st_ino):
        raise CandidateValidationError("package directory path replaced during snapshot")
    return snapshots


def pinned_descriptor(role: str) -> dict[str, str]:
    path, digest = SOURCE_PINS[role]
    return {"path": path, "sha256": digest}


def generated_descriptor(name: str, value: Any) -> dict[str, str]:
    return {
        "path": (PACKAGE_REPORT_RELATIVE / name).as_posix(),
        "sha256": file_sha256(canonical_json(value)),
    }


def code_descriptor(relative: str) -> dict[str, str]:
    payload = stable_file_snapshot(REPORT / safe_report_relative(relative), cap=4_000_000)
    return {"path": relative, "sha256": file_sha256(payload)}


def load_pinned_sources() -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for role, (relative, expected_digest) in SOURCE_PINS.items():
        path = REPORT / safe_report_relative(relative)
        payload = stable_file_snapshot(path)
        observed = file_sha256(payload)
        if observed != expected_digest:
            raise CandidateValidationError(
                f"pinned source drift for {role}: {observed} != {expected_digest}"
            )
        if relative.endswith(".json"):
            loaded[role] = decode_canonical(payload, role)
    return loaded


def canonical_fraction(value: Any) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise CandidateValidationError(f"canonical rational required: {value!r}")
    result = Fraction(value)
    if f"{result.numerator}/{result.denominator}" != value:
        raise CandidateValidationError(f"noncanonical rational: {value!r}")
    return result


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def reconstruct_partition(axis: dict[str, Any]) -> dict[str, Any]:
    domain = axis["domain"]
    start_text = domain.get("start_exact", domain.get("lower_exact"))
    width_text = domain.get("period_exact", domain.get("width_exact"))
    start = canonical_fraction(start_text)
    width = canonical_fraction(width_text)
    if width <= 0:
        raise CandidateValidationError("positive Round172 axis width required")
    end = start + width
    size = axis["anchor_size"]
    if type(size) is not int or type(size) is bool or size < 2:
        raise CandidateValidationError("invalid Round172 anchor size")
    alignment = axis["alignment"]
    shift_text = axis.get("periodic_shift_n0_exact", "0/1")
    shift = canonical_fraction(shift_text)

    if alignment == "cell_centred_reflecting":
        construction = "cell_centred_reflecting_scharfetter_gummel"
        periodic = False
        spacing = width / size
        positions = [start + (2 * index + 1) * spacing / 2 for index in range(size)]
        boundaries = [start + index * spacing for index in range(size + 1)]
        segments = [[[boundaries[index], boundaries[index + 1]]] for index in range(size)]
        volumes = [spacing] * size
        interval_count = size
    elif alignment == "vertex_centred_reflecting_dual":
        construction = "vertex_centred_reflecting_scharfetter_gummel"
        periodic = False
        spacing = width / (size - 1)
        positions = [start + index * spacing for index in range(size)]
        boundaries = [start]
        boundaries.extend((positions[index - 1] + positions[index]) / 2 for index in range(1, size))
        boundaries.append(end)
        segments = [[[boundaries[index], boundaries[index + 1]]] for index in range(size)]
        volumes = [boundaries[index + 1] - boundaries[index] for index in range(size)]
        interval_count = size - 1
    elif alignment in {
        "cell_centred_periodic_base",
        "cell_centred_periodic_half_shift",
    }:
        construction = (
            "cell_centred_periodic_diffusion"
            if alignment == "cell_centred_periodic_base"
            else "cell_centred_periodic_diffusion_half_shift"
        )
        periodic = True
        spacing = width / size
        positions = [
            start + ((index * spacing + spacing / 2 + shift) % width) for index in range(size)
        ]
        segments = []
        for position in positions:
            lower = position - spacing / 2
            upper = position + spacing / 2
            if lower < start:
                segments.append([[lower + width, end], [start, upper]])
            elif upper > end:
                segments.append([[lower, end], [start, upper - width]])
            else:
                segments.append([[lower, upper]])
        volumes = [spacing] * size
        interval_count = size
    else:
        raise CandidateValidationError(f"unknown Round172 alignment: {alignment}")

    if (
        axis["anchor_interval_count"] != interval_count
        or canonical_fraction(axis["spacing_h0_exact"]) != spacing
    ):
        raise CandidateValidationError("Round172 spacing or interval-count drift")
    return {
        "cell_segments_exact": [
            [[fraction_text(left), fraction_text(right)] for left, right in cell]
            for cell in segments
        ],
        "cell_volumes_exact": [fraction_text(value) for value in volumes],
        "construction": construction,
        "coordinate": axis["coordinate"],
        "domain_start_exact": start_text,
        "domain_width_exact": width_text,
        "periodic": periodic,
        "periodic_shift_exact": shift_text,
        "positions_exact": [fraction_text(value) for value in positions],
        "schema": "encounter_exact_axis_partition_v1",
        "size": size,
    }


def derive_member_and_subordinates(
    sources: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, int], list[dict[str, str]]]:
    configuration = sources["configuration_source"]
    legacy = sources["legacy_member_spec"]
    refinement = sources["joint_refinement_family"]
    initial_bundle = sources["initial_partition_bundle"]
    reference = sources["reference_density_source"]
    if (
        configuration.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or configuration.get("configuration_count") != 12
        or configuration.get("coordinate_order") != list(COORDINATES)
        or configuration.get("contains_budget_value") is not False
        or configuration.get("contains_control_values") is not False
        or configuration.get("authorizes_scientific_execution") is not False
    ):
        raise CandidateValidationError("configuration authority semantic drift")
    if legacy.get("schema") != "encounter_continuum_c1_c2_fixed_row_member_spec_v1" or legacy.get(
        "configuration_order"
    ) != configuration.get("configuration_order"):
        raise CandidateValidationError("legacy member authority semantic drift")
    if (
        refinement.get("schema") != "encounter_continuum_c1_genuine_joint_refinement_family_v2"
        or refinement.get("sequence_count") != 12
        or refinement.get("sequence_order") != configuration.get("configuration_order")
    ):
        raise CandidateValidationError("Round172 authority semantic drift")
    if (
        initial_bundle.get("schema") != "encounter_control_free_production_initial_stream_v1"
        or initial_bundle.get("configuration_count") != 12
        or len(initial_bundle.get("rows", [])) != 12
    ):
        raise CandidateValidationError("initial partition bundle semantic drift")
    if reference.get(
        "schema"
    ) != "encounter_continuum_c1_reference_density_source_v1" or reference.get(
        "coordinate_order"
    ) != list(COORDINATES):
        raise CandidateValidationError("reference density authority semantic drift")

    configurations = configuration.get("configurations")
    sequences = refinement.get("sequences")
    bundle_rows = initial_bundle.get("rows")
    semantics = legacy.get("configuration_semantic_ids")
    if not all(
        type(items) is list and len(items) == 12
        for items in (
            configurations,
            sequences,
            bundle_rows,
            semantics,
        )
    ):
        raise CandidateValidationError("12-row predecessor authority required")
    labels = [row["label"] for row in configurations]
    semantic_ids = [
        (
            row["authority_label"],
            row["refinement_family_id"],
            row["refinement_member_id"],
        )
        for row in semantics
    ]
    sequence_ids = [row["sequence_id"] for row in sequences]
    if (
        configuration["configuration_order"] != labels
        or legacy["configuration_order"] != labels
        or refinement["sequence_order"] != labels
        or len(set(labels)) != 12
        or len(set(semantic_ids)) != 12
        or len(set(sequence_ids)) != 12
    ):
        raise CandidateValidationError(
            "configuration order/label or semantic/sequence identifier uniqueness drift"
        )

    physical_parameters = reference["physical_parameter_bundle"]
    physical_parameter_digest = domain_sha256(
        "encounter-physical-parameter-bundle-v1", physical_parameters
    )
    partition_root = Path(SOURCE_PINS["initial_partition_bundle"][0]).parent
    bindings: list[dict[str, Any]] = []
    subordinate_inventory: list[dict[str, str]] = []
    alignments: Counter[str] = Counter()
    states = 0
    cells = 0
    edges = 0
    seams = 0
    seen_paths: set[str] = set()

    for row_index, (config, sequence, bundle_row, semantic) in enumerate(
        zip(configurations, sequences, bundle_rows, semantics, strict=True)
    ):
        label = config["label"]
        shape = config["shape"]
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(value) is not int or type(value) is bool or value < 2 for value in shape)
            or shape[0] * shape[1] * shape[2] != config["expected_states"]
            or sequence["source_row_index"] != row_index
            or bundle_row["configuration_index"] != row_index
            or semantic["authority_label"] != label
            or sequence["label"] != label
            or bundle_row["configuration_label"] != label
            or sequence["anchor_shape"] != shape
            or sequence["anchor_expected_states"] != config["expected_states"]
            or bundle_row["expected_states"] != config["expected_states"]
            or sequence["source_row_canonical_sha256"] != file_sha256(canonical_json(config))
        ):
            raise CandidateValidationError(f"configuration/sequence row drift at {row_index}")

        row_file = bundle_row["row_manifest"]
        row_relative = partition_root / safe_report_relative(row_file["path"])
        row_payload = stable_file_snapshot(REPORT / row_relative)
        if (
            file_sha256(row_payload) != row_file["sha256"]
            or len(row_payload) != row_file["byte_length"]
        ):
            raise CandidateValidationError(f"initial row snapshot drift at {row_index}")
        row = decode_canonical(row_payload, f"initial partition row {row_index}")
        if (
            row.get("schema") != "encounter_control_free_production_initial_row_v1"
            or row.get("configuration_index") != row_index
            or row.get("configuration_label") != label
            or row.get("configuration_sha256") != SOURCE_PINS["configuration_source"][1]
            or row.get("expected_states") != config["expected_states"]
            or row.get("row_relation_sha256") != bundle_row.get("row_relation_sha256")
            or len(row.get("axes", [])) != 3
            or len(sequence.get("axes", [])) != 3
        ):
            raise CandidateValidationError(f"initial row semantic drift at {row_index}")
        row_path_text = row_relative.as_posix()
        if row_path_text in seen_paths:
            raise CandidateValidationError("duplicate subordinate row path")
        seen_paths.add(row_path_text)
        subordinate_inventory.append(
            {
                "path": row_path_text,
                "role": f"initial_partition_row_{row_index:02d}",
                "sha256": file_sha256(row_payload),
            }
        )

        axis_bindings: list[dict[str, Any]] = []
        for axis_index, coordinate in enumerate(COORDINATES):
            sequence_axis = sequence["axes"][axis_index]
            row_axis = row["axes"][axis_index]
            if (
                sequence_axis.get("coordinate") != coordinate
                or row_axis.get("coordinate") != coordinate
                or sequence_axis.get("anchor_size") != shape[axis_index]
            ):
                raise CandidateValidationError(
                    f"axis order/shape drift at {row_index}:{coordinate}"
                )
            partition_file = row_axis["partition_file"]
            partition_relative = partition_root / safe_report_relative(partition_file["path"])
            partition_payload = stable_file_snapshot(REPORT / partition_relative)
            partition_digest = file_sha256(partition_payload)
            if (
                partition_digest != partition_file["sha256"]
                or len(partition_payload) != partition_file["byte_length"]
            ):
                raise CandidateValidationError(
                    f"partition snapshot drift at {row_index}:{coordinate}"
                )
            partition = decode_canonical(
                partition_payload, f"initial partition {row_index}:{coordinate}"
            )
            independently_reconstructed = reconstruct_partition(sequence_axis)
            require_exact(
                partition,
                independently_reconstructed,
                f"Round172 partition reconstruction {row_index}:{coordinate}",
            )
            partition_path_text = partition_relative.as_posix()
            if partition_path_text in seen_paths:
                raise CandidateValidationError("duplicate subordinate partition path")
            seen_paths.add(partition_path_text)
            subordinate_inventory.append(
                {
                    "path": partition_path_text,
                    "role": f"initial_partition_{row_index:02d}_{coordinate}",
                    "sha256": partition_digest,
                }
            )
            cell_count = partition["size"]
            periodic = partition["periodic"]
            alignments[sequence_axis["alignment"]] += 1
            cells += cell_count
            edges += cell_count if periodic else cell_count - 1
            seams += int(periodic)
            axis_binding: dict[str, Any] = {
                "alignment": sequence_axis["alignment"],
                "cell_count": cell_count,
                "coordinate": coordinate,
                "exact_box_or_period": {
                    "domain_start_exact": partition["domain_start_exact"],
                    "domain_width_exact": partition["domain_width_exact"],
                },
                "partition_report_relative_path": partition_path_text,
                "partition_schema": partition["schema"],
                "partition_sha256": partition_digest,
                "periodic": periodic,
                "refinement_family_id": semantic["refinement_family_id"],
                "refinement_member_id": semantic["refinement_member_id"],
                "sequence_id": sequence["sequence_id"],
                "sequence_source_row_canonical_sha256": (sequence["source_row_canonical_sha256"]),
            }
            if periodic:
                axis_binding["periodic_shift_n0_exact"] = sequence_axis["periodic_shift_n0_exact"]
            axis_bindings.append(axis_binding)

        geometry_record = {
            "configuration_index": row_index,
            "configuration_row": config,
            "n0_partition_sha256s": [axis["partition_sha256"] for axis in axis_bindings],
        }
        bindings.append(
            {
                "authority_label": label,
                "configuration_geometry_sha256": domain_sha256(
                    "encounter-configuration-geometry-v1", geometry_record
                ),
                "configuration_index": row_index,
                "initial_partition_row_manifest_path": row_path_text,
                "initial_partition_row_manifest_sha256": file_sha256(row_payload),
                "n0_anchor_expected_states": config["expected_states"],
                "n0_anchor_shape": shape,
                "n0_axes": axis_bindings,
                "physical_parameter_bundle_sha256": physical_parameter_digest,
                "refinement_family_id": semantic["refinement_family_id"],
                "refinement_member_id": semantic["refinement_member_id"],
                "sequence_id": sequence["sequence_id"],
                "sequence_source_row_canonical_sha256": sequence["source_row_canonical_sha256"],
                "sequence_source_row_index": row_index,
            }
        )
        states += config["expected_states"]

    counts = {
        "axis_count": sum(alignments.values()),
        "axis_cell_count": cells,
        "axis_edge_count": edges,
        "configuration_count": len(bindings),
        "periodic_seam_count": seams,
        "profile_index_count": len(bindings) * len(PROFILE_ORDER),
        "total_virtual_tensor_state_count": states,
    }
    require_exact(dict(sorted(alignments.items())), EXPECTED_ALIGNMENTS, "alignment counts")
    require_exact(counts, EXPECTED_COUNTS, "12/36/5037/5013/48/state counts")
    if len(subordinate_inventory) != 48:
        raise CandidateValidationError("48 subordinate row/partition files required")

    identity = {
        "configuration_order": legacy["configuration_order"],
        "configuration_semantic_ids": semantics,
        "coordinate_order": list(COORDINATES),
        "n0_sequence_bindings": bindings,
        "role_bindings_1_through_4": legacy["role_bindings"],
        "scalar_convention": legacy["member_semantics"]["scalar_convention"],
    }
    member = {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "configuration_order": legacy["configuration_order"],
        "configuration_semantic_ids": semantics,
        "identity_properties": {
            "alignment_counts": dict(sorted(alignments.items())),
            "candidate_authoritative": False,
            "current_enclosures_bind_this_candidate": False,
            "n0_partition_sha256s_structurally_bound": True,
            "partition_file_count": 36,
            "round172_source_itself_contains_partition_sha256": False,
            "source_roles_1_through_4_only_in_production_role_bindings": True,
        },
        "member_identity_sha256": domain_sha256(
            "encounter-continuum-c1-c2-n0-member-identity-v3", identity
        ),
        "member_semantics": {
            "configuration_count": 12,
            "configuration_rows_are_finite_anchors": True,
            "coordinate_order": list(COORDINATES),
            "every_cartesian_interval_endpoint_combination_is_a_model": False,
            "one_formula_defined_correlated_member_per_configuration": True,
            "physical_dimension": 2,
            "quotient_dimension": 3,
            "scalar_convention": legacy["member_semantics"]["scalar_convention"],
        },
        "n0_sequence_bindings": bindings,
        "reconstruction_counts": counts,
        "role_bindings": legacy["role_bindings"],
        "schema": "encounter_continuum_c1_c2_n0_member_spec_v3_candidate",
        "source_lineage_evidence": {
            "initial_partition_bundle": pinned_descriptor("initial_partition_bundle"),
            "joint_refinement_family": pinned_descriptor("joint_refinement_family"),
            "legacy_member_spec": pinned_descriptor("legacy_member_spec"),
            "round176_member_candidate": pinned_descriptor("round176_member_candidate"),
        },
        "status": (
            "STRUCTURAL_PARTITION_IDENTITY_CANDIDATE_ONLY_"
            "NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
        ),
    }
    return member, counts, subordinate_inventory


def parameter_specifications() -> list[dict[str, Any]]:
    return [
        {
            "parameter_id": "stationary_directed_mpfr_320_v2",
            "parameters": {
                "aggregation": "exact_Fraction_endpoint_sums_and_nonnegative_products",
                "dense_tensor_materialized": False,
                "precision_bits": 320,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role9_stationary_integral"],
            },
        },
        {
            "parameter_id": "stationary_directed_mpfr_640_sentinel_v2",
            "parameters": {
                "containment_relation": "primary_320_interval_contains_640_sentinel",
                "independent_backend": False,
                "precision_bits": 640,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role9_stationary_integral"],
            },
        },
        {
            "parameter_id": "raw_flux_directed_mpfr_320_v2",
            "parameters": {
                "aggregation": "exact_Fraction_endpoint_algebra",
                "common_kappa_rule": "intersection_after_formula_witness",
                "precision_bits": 320,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role8_raw_axis_enclosure"],
            },
        },
        {
            "parameter_id": "raw_flux_directed_mpfr_640_sentinel_v2",
            "parameters": {
                "containment_relation": "primary_320_interval_contains_640_sentinel",
                "independent_backend": False,
                "precision_bits": 640,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role8_raw_axis_enclosure"],
            },
        },
        {
            "parameter_id": "raw_flux_binary64_decode_v2",
            "parameters": {
                "decode": "exact_binary64_endpoint_to_reduced_dyadic_fraction",
                "precision_bits": 53,
                "rounding_mode": "stored_outward_endpoints",
                "source_role_scope": ["role8_raw_axis_enclosure"],
            },
        },
        {
            "parameter_id": "exact_fraction_expression_dag_v2",
            "parameters": {
                "arithmetic": "Python_Fraction_exact_reduced_rationals",
                "precision_bits": "unbounded_integer_fraction",
                "rounding_mode": "exact",
                "source_role_scope": [
                    "role8_raw_axis_enclosure",
                    "role9_stationary_integral",
                ],
            },
        },
        {
            "parameter_id": "killing_contact_profile_mpfr_192_v2",
            "parameters": {
                "contact_fraction_record_format": ">dd",
                "panels_per_unit": 16384,
                "precision_bits": 192,
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role10_killing_geometry"],
                "support_density_record_format": ">dd",
            },
        },
        {
            "parameter_id": "killing_analytic_disk_area_mpfr_256_v2",
            "parameters": {
                "analytic_area_precision_bits": 256,
                "formula": "pi_times_radius_squared",
                "rounding_mode": "directed_RoundDown_RoundUp",
                "source_role_scope": ["role10_killing_geometry"],
            },
        },
        {
            "parameter_id": "killing_independent_simpson_remainder_v2",
            "parameters": {
                "independent_backend": False,
                "maximum_panel_count": 4194304,
                "primary_precision_bits": 384,
                "remainder_rule": "rigorous_fourth_derivative_simpson_remainder",
                "sentinel_precision_bits": 512,
                "source_role_scope": ["role10_killing_geometry"],
            },
        },
        {
            "parameter_id": "killing_exact_full_cell_classification_v2",
            "parameters": {
                "classification": (
                    "every_corner_of_every_exact_partition_segment_inside_or_on_contact_disk"
                ),
                "full_cell_serialization": "exact_[1,1]",
                "precision_bits": "exact_rational",
                "rounding_mode": "exact",
                "source_role_scope": ["role10_killing_geometry"],
            },
        },
    ]


def derive_parameter_registry() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for specification in parameter_specifications():
        entry = dict(specification)
        entry["method_parameter_sha256"] = domain_sha256(
            "encounter-outward-method-parameters-v2", specification["parameters"]
        )
        entries.append(entry)
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "parameter_count": 10,
        "parameters": entries,
        "schema": "encounter_continuum_c1_c2_n0_method_parameter_registry_v2_candidate",
        "status": "RESULT_BLIND_METHOD_PARAMETER_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED",
    }


def derive_code_closure(closure_id: str, keys: tuple[str, ...]) -> dict[str, Any]:
    files = [code_descriptor(CODE_PATHS[key]) for key in keys]
    return {
        "inventory_id": closure_id,
        "files": files,
        "sha256": domain_sha256("encounter-method-code-inventory-draft-v1", files),
    }


def derive_method_registry(parameter_registry: dict[str, Any]) -> dict[str, Any]:
    closures = {
        "stationary": derive_code_closure(
            "stationary_authenticated_mpfr_v1",
            (
                "stationary_producer",
                "stationary_verifier",
            ),
        ),
        "raw_flux": derive_code_closure(
            "raw_flux_authenticated_mpfr_v1",
            (
                "raw_flux_producer",
                "raw_flux_verifier",
            ),
        ),
        "killing": derive_code_closure(
            "killing_geometry_same_backend_v1",
            (
                "killing_producer",
                "killing_verifier",
                "killing_f0_core",
                "killing_partition_producer",
                "killing_uniformization_dependency",
            ),
        ),
    }
    parameters = {entry["parameter_id"]: entry for entry in parameter_registry["parameters"]}
    parameter_pin = generated_descriptor(PARAMETER_NAME, parameter_registry)
    specifications = [
        (
            "stationary_directed_mpfr_320_v2",
            "stationary",
            "stationary_producer",
            "stationary_verifier",
            320,
            "directed_RoundDown_RoundUp",
            "gmpy2_2.2.1_MPFR_4.2.1",
            "MPFR_correct_rounding_for_exp_erf_sqrt_and_exact_rational_algebra",
            ["role9_stationary_integral"],
            "restricted_global_reference_density_axis_cell_mass",
            "axis_mass_length",
        ),
        (
            "stationary_directed_mpfr_640_sentinel_v2",
            "stationary",
            "stationary_producer",
            "stationary_verifier",
            640,
            "directed_RoundDown_RoundUp",
            "gmpy2_2.2.1_MPFR_4.2.1",
            "same_formula_higher_precision_containment_sentinel",
            ["role9_stationary_integral"],
            "restricted_global_reference_density_axis_cell_mass",
            "axis_mass_length",
        ),
        (
            "raw_flux_directed_mpfr_320_v2",
            "raw_flux",
            "raw_flux_producer",
            "raw_flux_verifier",
            320,
            "directed_RoundDown_RoundUp",
            "gmpy2_2.2.1_MPFR_4.2.1",
            "directed_SG_Bernoulli_formula_and_common_flux_intersection",
            ["role8_raw_axis_enclosure"],
            "ungauged_axis_primitive_mu",
            "axis_mass_and_inverse_time",
        ),
        (
            "raw_flux_directed_mpfr_640_sentinel_v2",
            "raw_flux",
            "raw_flux_producer",
            "raw_flux_verifier",
            640,
            "directed_RoundDown_RoundUp",
            "gmpy2_2.2.1_MPFR_4.2.1",
            "same_formula_higher_precision_containment_sentinel",
            ["role8_raw_axis_enclosure"],
            "ungauged_axis_primitive_mu",
            "axis_mass_and_inverse_time",
        ),
        (
            "raw_flux_binary64_decode_v2",
            "raw_flux",
            "raw_flux_producer",
            "raw_flux_verifier",
            53,
            "stored_outward_endpoints",
            "IEEE_754_binary64",
            "exact_binary64_endpoint_to_reduced_dyadic_fraction",
            ["role8_raw_axis_enclosure"],
            "ungauged_axis_primitive_mu",
            "axis_mass_and_inverse_time",
        ),
        (
            "killing_contact_profile_mpfr_192_v2",
            "killing",
            "killing_producer",
            "killing_verifier",
            192,
            "directed_RoundDown_RoundUp",
            "gmpy2_2.2.1_MPFR_4.2.1",
            "directed_contact_fraction_and_normalized_bump_profile_enclosures",
            ["role10_killing_geometry"],
            "cell_average_contact_and_support_factorization",
            "dimensionless_contact_and_inverse_length_support",
        ),
        (
            "killing_analytic_disk_area_mpfr_256_v2",
            "killing",
            "killing_producer",
            "killing_verifier",
            256,
            "directed_RoundDown_RoundUp",
            "gmpy2_2.2.1_MPFR_4.2.1",
            "directed_pi_times_radius_squared_analytic_anchor",
            ["role10_killing_geometry"],
            "physical_contact_area",
            "length_squared",
        ),
        (
            "killing_independent_simpson_remainder_v2",
            "killing",
            "killing_producer",
            "killing_verifier",
            "producer_192_verifier_384_512",
            "directed_with_rigorous_remainder",
            "gmpy2_2.2.1_MPFR_4.2.1",
            "rigorous_fourth_derivative_Simpson_remainder_and_sentinel_containment",
            ["role10_killing_geometry"],
            "unit_mass_support_profile",
            "dimensionless_integral",
        ),
        (
            "killing_exact_full_cell_classification_v2",
            "killing",
            "killing_producer",
            "killing_verifier",
            "exact_rational",
            "exact",
            "Python_Fraction_3.12",
            "exact_corner_classification_before_unit_interval_serialization",
            ["role10_killing_geometry"],
            "exact_partition_contact_geometry",
            "dimensionless_fraction",
        ),
    ]
    methods: list[dict[str, Any]] = []
    for (
        method_id,
        closure_key,
        producer_key,
        verifier_key,
        precision,
        rounding,
        backend,
        remainder,
        role_scope,
        normalization,
        unit,
    ) in specifications:
        parameter = parameters[method_id]
        methods.append(
            {
                "analytic_remainder_rule": remainder,
                "backend_and_version": backend,
                "coordinate_order": list(COORDINATES),
                "enumerated_code_inventory_id": closures[closure_key]["inventory_id"],
                "enumerated_code_inventory_sha256": closures[closure_key]["sha256"],
                "method_id": method_id,
                "method_parameter_path": parameter_pin["path"],
                "method_parameter_record_id": method_id,
                "method_parameter_sha256": parameter["method_parameter_sha256"],
                "method_parameter_source_sha256": parameter_pin["sha256"],
                "normalization_convention": normalization,
                "precision_bits": precision,
                "producer_code_path": CODE_PATHS[producer_key],
                "producer_code_sha256": code_descriptor(CODE_PATHS[producer_key])["sha256"],
                "rounding_mode": rounding,
                "source_role_scope": role_scope,
                "unit": unit,
                "verifier_code_path": CODE_PATHS[verifier_key],
                "verifier_code_sha256": code_descriptor(CODE_PATHS[verifier_key])["sha256"],
            }
        )
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "enumerated_code_inventory_drafts": [closures[key] for key in sorted(closures)],
        "method_count": 9,
        "method_identity_properties": {
            "all_methods_bind_parameter_hashes": True,
            "all_methods_bind_producer_and_verifier_code_hashes": True,
            "all_report_local_dependency_closures_bound": False,
            "B06_structural_remedy_prepared": False,
            "current_registered_producers_emit_legacy_schemas": True,
            "enumerated_top_level_kernel_files_bound": True,
            "external_predecessor_commitment_required_before_replay": True,
            "future_successor_native_source_materialized": False,
            "legacy_kernel_hash_inventory_draft_prepared": True,
            "missing_candidate_native_method_ids": ["exact_fraction_expression_dag_v2"],
            "parameterized_successor_native_producers_and_verifiers_frozen": False,
            "roles_8_9_10_method_scopes_present": True,
            "transitive_report_local_dependency_closure_complete": False,
        },
        "methods": methods,
        "parameter_registry": parameter_pin,
        "schema": "encounter_continuum_c1_c2_n0_outward_method_registry_v2_candidate",
        "status": (
            "LEGACY_KERNEL_HASH_INVENTORY_DRAFT_ONLY_"
            "B06_REMEDY_NOT_PREPARED_NOT_EXTERNALLY_COMMITTED_NOT_REPLAY_AUTHORITY"
        ),
    }


def validate_method_hash_closure(
    parameter_registry: dict[str, Any], method_registry: dict[str, Any]
) -> None:
    parameter_ids = [entry["parameter_id"] for entry in parameter_registry["parameters"]]
    method_ids = [entry["method_id"] for entry in method_registry["methods"]]
    if (
        [item for item in parameter_ids if item != "exact_fraction_expression_dag_v2"] != method_ids
        or len(set(method_ids)) != 9
        or method_registry["method_identity_properties"]["missing_candidate_native_method_ids"]
        != ["exact_fraction_expression_dag_v2"]
    ):
        raise CandidateValidationError("method/parameter registry identity drift")
    closure_by_id = {
        closure["inventory_id"]: closure
        for closure in method_registry["enumerated_code_inventory_drafts"]
    }
    if len(closure_by_id) != 3:
        raise CandidateValidationError("three unique code-inventory drafts required")
    for closure in closure_by_id.values():
        if closure["sha256"] != domain_sha256(
            "encounter-method-code-inventory-draft-v1", closure["files"]
        ):
            raise CandidateValidationError("enumerated code-inventory digest drift")
        for descriptor in closure["files"]:
            if code_descriptor(descriptor["path"]) != descriptor:
                raise CandidateValidationError("dependency closure code hash drift")
    parameter_by_id = {entry["parameter_id"]: entry for entry in parameter_registry["parameters"]}
    for method in method_registry["methods"]:
        parameter = parameter_by_id[method["method_id"]]
        if (
            method["method_parameter_sha256"]
            != domain_sha256("encounter-outward-method-parameters-v2", parameter["parameters"])
            or method["producer_code_sha256"]
            != code_descriptor(method["producer_code_path"])["sha256"]
            or method["verifier_code_sha256"]
            != code_descriptor(method["verifier_code_path"])["sha256"]
            or method["enumerated_code_inventory_id"] not in closure_by_id
            or method["enumerated_code_inventory_sha256"]
            != closure_by_id[method["enumerated_code_inventory_id"]]["sha256"]
        ):
            raise CandidateValidationError("method code-inventory/parameter hash drift")


def derive_policy(
    sources: dict[str, dict[str, Any]],
    member: dict[str, Any],
    method_registry: dict[str, Any],
) -> dict[str, Any]:
    legacy_policy = sources["legacy_policy"]
    if legacy_policy.get("schema") != "encounter_continuum_c1_c2_fixed_row_anti_vacuity_policy_v1":
        raise CandidateValidationError("legacy anti-vacuity policy schema drift")
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "join_requirements": {
            "axis_order_exact": list(COORDINATES),
            "axis_partition_path_sha_cell_count_equal": True,
            "cell_and_edge_native_record_keys_unique": True,
            "configuration_count_exactly_12": True,
            "configuration_index_and_label_unique": True,
            "killing_member_partition_formula_method_unit_binding_equal": True,
            "profile_index_order_exact": list(PROFILE_ORDER),
            "raw_stationary_member_partition_formula_method_unit_binding_equal": True,
        },
        "ordering": {
            "current_enclosure_sources_eligible_for_acceptance": False,
            "external_predecessor_commitment_present": False,
            "future_replay_must_pin_exact_member_registry_policy_hashes": True,
            "future_replay_required": True,
            "policy_predecessor_order_independently_sealed": False,
            "retroactive_acceptance_authorized": False,
            "roles_8_10_outputs_read_while_constructing_this_policy": False,
            "timestamp_ordering_is_sufficient": False,
        },
        "requirements": legacy_policy["requirements"],
        "schema": "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate",
        "source_pins": {
            "legacy_policy": pinned_descriptor("legacy_policy"),
            "member_spec_v3_candidate": generated_descriptor(MEMBER_NAME, member),
            "outward_method_registry_v2_candidate": generated_descriptor(
                METHOD_NAME, method_registry
            ),
            "round176_policy_candidate": pinned_descriptor("round176_policy_candidate"),
        },
        "status": (
            "RESULT_BLIND_POLICY_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_"
            "CURRENT_ENCLOSURES_PERMANENTLY_INELIGIBLE"
        ),
        "threshold_lineage": {
            "all_exact_thresholds_equal_to_legacy_policy": True,
            "post_enclosure_adaptation_allowed": False,
            "threshold_loosening_detected": False,
        },
    }


def derive_manifest(
    member: dict[str, Any],
    parameter_registry: dict[str, Any],
    method_registry: dict[str, Any],
    policy: dict[str, Any],
    counts: dict[str, int],
    subordinate_inventory: list[dict[str, str]],
) -> dict[str, Any]:
    roles = [
        {
            "role": "role1_reference_density_source",
            **pinned_descriptor("reference_density_source"),
        },
        {"role": "role2_ideal_formula_source", **pinned_descriptor("ideal_formula_source")},
        {"role": "role3_factorization_source", **pinned_descriptor("factorization_source")},
        {"role": "role4_configuration_source", **pinned_descriptor("configuration_source")},
        {"role": "role5_member_spec_candidate", **generated_descriptor(MEMBER_NAME, member)},
        {
            "role": "role6_outward_method_registry_candidate",
            **generated_descriptor(METHOD_NAME, method_registry),
        },
        {
            "role": "role7_anti_vacuity_policy_candidate",
            **generated_descriptor(POLICY_NAME, policy),
        },
        {
            "role": "role11_symbolic_control_method_source",
            **pinned_descriptor("symbolic_control_method_source"),
        },
    ]
    supporting = [
        {"role": "joint_refinement_family", **pinned_descriptor("joint_refinement_family")},
        {"role": "initial_partition_bundle", **pinned_descriptor("initial_partition_bundle")},
        {"role": "legacy_member_spec", **pinned_descriptor("legacy_member_spec")},
        {"role": "legacy_policy", **pinned_descriptor("legacy_policy")},
        {
            "role": "round176_member_candidate",
            **pinned_descriptor("round176_member_candidate"),
        },
        {
            "role": "round176_policy_candidate",
            **pinned_descriptor("round176_policy_candidate"),
        },
        {
            "role": "control_method_commitment",
            **pinned_descriptor("control_method_commitment"),
        },
        {
            "role": "killing_geometry_authority",
            **pinned_descriptor("killing_geometry_authority"),
        },
        {
            "role": "method_parameter_registry_candidate",
            **generated_descriptor(PARAMETER_NAME, parameter_registry),
        },
    ]
    code_inventory = [
        {"role": f"code_{key}", **code_descriptor(CODE_PATHS[key])} for key in sorted(CODE_PATHS)
    ]
    subordinate_edges: list[list[str]] = []
    for row_index in range(12):
        row_role = f"initial_partition_row_{row_index:02d}"
        subordinate_edges.append(["initial_partition_bundle", row_role])
        for coordinate in COORDINATES:
            partition_role = f"initial_partition_{row_index:02d}_{coordinate}"
            subordinate_edges.extend(
                [
                    [row_role, partition_role],
                    [partition_role, "role5_member_spec_candidate"],
                ]
            )
    nodes = [entry["role"] for entry in roles + supporting + subordinate_inventory + code_inventory]
    edges = [
        ["role1_reference_density_source", "role5_member_spec_candidate"],
        ["role2_ideal_formula_source", "role5_member_spec_candidate"],
        ["role3_factorization_source", "role5_member_spec_candidate"],
        ["role4_configuration_source", "role5_member_spec_candidate"],
        ["joint_refinement_family", "role5_member_spec_candidate"],
        ["initial_partition_bundle", "role5_member_spec_candidate"],
        ["legacy_member_spec", "role5_member_spec_candidate"],
        ["round176_member_candidate", "role5_member_spec_candidate"],
        ["method_parameter_registry_candidate", "role6_outward_method_registry_candidate"],
        ["role5_member_spec_candidate", "role7_anti_vacuity_policy_candidate"],
        ["role6_outward_method_registry_candidate", "role7_anti_vacuity_policy_candidate"],
        ["legacy_policy", "role7_anti_vacuity_policy_candidate"],
        ["round176_policy_candidate", "role7_anti_vacuity_policy_candidate"],
        ["role3_factorization_source", "role11_symbolic_control_method_source"],
        ["control_method_commitment", "role11_symbolic_control_method_source"],
        ["killing_geometry_authority", "role11_symbolic_control_method_source"],
    ]
    edges.extend(
        [entry["role"], "role6_outward_method_registry_candidate"] for entry in code_inventory
    )
    edges.extend(subordinate_edges)
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "code_inventory": code_inventory,
        "forbidden_selected_roles": {
            "budget_value_sources": [],
            "control_value_sources": [],
            "result_or_scratch_sources": [],
            "role10_killing_geometry_sources": [],
            "role8_raw_axis_enclosure_sources": [],
            "role9_stationary_integral_sources": [],
        },
        "predecessor_prefix_dag": {
            "edges": edges,
            "formal_selected_source_dag_complete": False,
            "nodes": nodes,
            "predecessor_prefix_dag_complete": True,
            "role8_to_role10_outputs_materialized": False,
        },
        "reconstruction_counts": counts,
        "role_catalog": roles,
        "schema": "encounter_continuum_c1_c2_n0_predecessor_authority_candidate_manifest_v1",
        "stage": "preproduction_predecessor_authority_candidate_only",
        "status": (
            "PREDECESSOR_PREFIX_COMPLETE_ONLY_NO_FORMAL_OUTER_OPEN_NO_ROLES_8_10_NO_ACCEPTANCE"
        ),
        "subordinate_inventory": subordinate_inventory,
        "supporting_evidence": supporting,
    }


def validate_prefix_dag(manifest: dict[str, Any]) -> None:
    dag = manifest["predecessor_prefix_dag"]
    nodes = dag["nodes"]
    edges = dag["edges"]
    if type(nodes) is not list or len(nodes) != len(set(nodes)):
        raise CandidateValidationError("DAG nodes must be unique")
    node_set = set(nodes)
    if any(
        type(node) is not str
        or node.startswith("role8_")
        or node.startswith("role9_")
        or node.startswith("role10_")
        for node in nodes
    ):
        raise CandidateValidationError("roles 8-10 are forbidden from predecessor DAG nodes")
    adjacency: dict[str, list[str]] = {node: [] for node in nodes}
    seen_edges: set[tuple[str, str]] = set()
    for edge in edges:
        if type(edge) is not list or len(edge) != 2 or any(type(item) is not str for item in edge):
            raise CandidateValidationError("malformed predecessor DAG edge")
        left, right = edge
        if left not in node_set or right not in node_set or left == right:
            raise CandidateValidationError("DAG edge endpoint/self-edge drift")
        pair = (left, right)
        if pair in seen_edges:
            raise CandidateValidationError("duplicate predecessor DAG edge")
        seen_edges.add(pair)
        adjacency[left].append(right)
    colors: dict[str, int] = {node: 0 for node in nodes}

    def visit(node: str) -> None:
        if colors[node] == 1:
            raise CandidateValidationError("predecessor DAG cycle detected")
        if colors[node] == 2:
            return
        colors[node] = 1
        for child in adjacency[node]:
            visit(child)
        colors[node] = 2

    for node in nodes:
        visit(node)
    if any(manifest["forbidden_selected_roles"].values()):
        raise CandidateValidationError("forbidden roles/control/budget/result sources selected")


def derive_seal_request(
    member: dict[str, Any],
    parameter_registry: dict[str, Any],
    method_registry: dict[str, Any],
    policy: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    commitment_set = [
        {"role": "member_spec_candidate", **generated_descriptor(MEMBER_NAME, member)},
        {
            "role": "method_parameter_registry_candidate",
            **generated_descriptor(PARAMETER_NAME, parameter_registry),
        },
        {
            "role": "outward_method_registry_candidate",
            **generated_descriptor(METHOD_NAME, method_registry),
        },
        {
            "role": "anti_vacuity_policy_candidate",
            **generated_descriptor(POLICY_NAME, policy),
        },
        {
            "role": "predecessor_authority_candidate_manifest",
            **generated_descriptor(MANIFEST_NAME, manifest),
        },
        {"role": "candidate_builder", **code_descriptor(BUILDER_RELATIVE)},
        {
            "role": "independent_candidate_validator",
            **code_descriptor(VALIDATOR_RELATIVE),
        },
        {"role": "candidate_static_tests", **code_descriptor(STATIC_TEST_RELATIVE)},
        {
            "role": "candidate_mutation_tests",
            **code_descriptor(MUTATION_TEST_RELATIVE),
        },
    ]
    message_sha = domain_sha256(
        "encounter-external-predecessor-commitment-request-v1", commitment_set
    )
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "commitment_set": commitment_set,
        "local_state": {
            "candidate_ready_for_external_predecessor_commitment": False,
            "external_authentication_present": False,
            "local_or_subagent_review_is_external_authentication": False,
            "same_process_may_satisfy_request": False,
            "timestamp_or_mtime_is_commitment_evidence": False,
        },
        "requested_external_record": {
            "accepted_authentication_classes": [
                "distinct_operator_authenticated_signature",
                "independently_audited_predecessor_commit_hash",
                "independent_trust_domain_receipt_hash",
            ],
            "forbidden_evidence_classes": [
                "filesystem_mtime_or_timestamp_only",
                "local_self_hash_only",
                "same_process_or_child_process_assertion",
                "subagent_review_without_distinct_authentication",
            ],
            "current_request_action": (
                "independent_review_only_candidate_revision_required_before_commitment"
            ),
            "current_request_may_authorize_roles_8_10_replay": False,
            "must_bind_candidate_bundle_sha256": True,
            "must_bind_commitment_message_sha256": message_sha,
            "must_exist_before_any_roles_8_10_replay": True,
            "must_identify_distinct_reviewer_or_operator_authority": True,
            "must_not_be_created_or_consumed_by_this_builder_invocation": True,
            "required_top_level_keys": [
                "authentication",
                "authority",
                "candidate_bundle",
                "claim_boundary",
                "commitment_message_sha256",
                "ordering",
                "schema",
                "status",
            ],
            "required_schema": "encounter_external_predecessor_commitment_v1",
        },
        "schema": "encounter_continuum_c1_c2_n0_external_commitment_review_request_v1",
        "status": (
            "INDEPENDENT_REVIEW_REQUEST_ONLY_B06_REVISION_REQUIRED_"
            "EXTERNAL_PREDECESSOR_COMMITMENT_ABSENT"
        ),
    }


def derive_blocker_ledger() -> list[dict[str, Any]]:
    prepared = {
        "B04_round172_has_no_partition_sha256": (
            True,
            "candidate v3 independently reconstructs and binds all 36 partition hashes",
        ),
        "B06_method_registry_missing_code_and_parameter_hashes": (
            False,
            "legacy kernel hash inventory exists, but candidate-native result-blind "
            "producers and verifiers are not frozen",
        ),
    }
    ledger: list[dict[str, Any]] = []
    for blocker in BLOCKERS:
        structural, note = prepared.get(
            blocker,
            (False, "no authoritative structural remedy is materialized in this package"),
        )
        ledger.append(
            {
                "blocker_id": blocker,
                "cleared": False,
                "structural_remedy_prepared": structural,
                "structural_note": note,
            }
        )
    return ledger


def derive_bundle(payloads: dict[str, dict[str, Any]], counts: dict[str, int]) -> dict[str, Any]:
    inventory = [
        {
            "byte_length": len(canonical_json(payloads[name])),
            "path": name,
            "sha256": file_sha256(canonical_json(payloads[name])),
        }
        for name in PACKAGE_NAMES
        if name != BUNDLE_NAME
    ]
    return {
        "blocking_conditions": derive_blocker_ledger(),
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "external_authority_boundary": {
            "candidate_can_authorize_itself": False,
            "candidate_ready_for_external_predecessor_commitment": False,
            "external_predecessor_commitment_present": False,
            "not_authoritative_until_external_predecessor_commitment": True,
            "revision_required_before_commitment": (
                "freeze candidate-native result-blind role8-role10 "
                "producer-verifier transitive closures"
            ),
            "same_process_or_subagent_review_counts_as_external": False,
        },
        "file_inventory": inventory,
        "package_publication": {
            "executed_builder_bytes_authenticated": False,
            "hostile_writer_atomicity_claimed": False,
            "input_snapshots_reverified_before_and_after_publish": True,
            "per_file_fsync_before_publish": True,
            "single_same_filesystem_directory_rename": True,
            "stable_reread_after_publish": True,
            "whole_package_no_replace_under_no_hostile_writer_contract": True,
        },
        "reconstruction_counts": counts,
        "reserved_basename_absence_required": sorted(RESERVED_BASENAMES),
        "schema": "encounter_continuum_c1_c2_n0_predecessor_authority_candidate_bundle_v1",
        "status": (
            "PASS_PREPRODUCTION_PREDECESSOR_AUTHORITY_STRUCTURAL_CANDIDATE_ONLY_"
            "B04_REMEDY_PREPARED_B06_HASH_INVENTORY_DRAFT_NO_BLOCKER_CLEARED"
        ),
    }


def derive_expected_outputs(
    sources: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    member, counts, subordinate_inventory = derive_member_and_subordinates(sources)
    parameter_registry = derive_parameter_registry()
    method_registry = derive_method_registry(parameter_registry)
    policy = derive_policy(sources, member, method_registry)
    manifest = derive_manifest(
        member,
        parameter_registry,
        method_registry,
        policy,
        counts,
        subordinate_inventory,
    )
    seal_request = derive_seal_request(
        member, parameter_registry, method_registry, policy, manifest
    )
    payloads = {
        MEMBER_NAME: member,
        PARAMETER_NAME: parameter_registry,
        METHOD_NAME: method_registry,
        POLICY_NAME: policy,
        MANIFEST_NAME: manifest,
        SEAL_REQUEST_NAME: seal_request,
    }
    payloads[BUNDLE_NAME] = derive_bundle(payloads, counts)
    return payloads, counts


def validate_blockers_and_authority(bundle: dict[str, Any]) -> None:
    ledger = bundle["blocking_conditions"]
    if (
        type(ledger) is not list
        or [entry.get("blocker_id") for entry in ledger] != list(BLOCKERS)
        or any(entry.get("cleared") is not False for entry in ledger)
    ):
        raise CandidateValidationError("all nine blockers must remain present and uncleared")
    prepared = {entry["blocker_id"]: entry["structural_remedy_prepared"] for entry in ledger}
    if {key for key, value in prepared.items() if value is True} != {
        "B04_round172_has_no_partition_sha256",
    } or any(type(value) is not bool for value in prepared.values()):
        raise CandidateValidationError("only B04 may be structurally prepared")
    boundary = bundle["external_authority_boundary"]
    if (
        boundary["candidate_can_authorize_itself"] is not False
        or boundary["candidate_ready_for_external_predecessor_commitment"] is not False
        or boundary["external_predecessor_commitment_present"] is not False
        or boundary["not_authoritative_until_external_predecessor_commitment"] is not True
        or boundary["same_process_or_subagent_review_counts_as_external"] is not False
    ):
        raise CandidateValidationError("external predecessor authority boundary drift")


def validate_package(
    package_path: Path = DEFAULT_PACKAGE,
) -> tuple[str, dict[str, int]]:
    package = Path(os.path.abspath(package_path)) if package_path.is_absolute() else package_path
    snapshots = snapshot_atomic_package(package)
    observed = {
        name: decode_canonical(snapshots[name], f"package/{name}") for name in PACKAGE_NAMES
    }
    sources = load_pinned_sources()
    expected, counts = derive_expected_outputs(sources)
    for name in PACKAGE_NAMES:
        require_exact(observed[name], expected[name], f"package payload {name}")
        if snapshots[name] != canonical_json(expected[name]):
            raise CandidateValidationError(f"canonical byte mismatch for {name}")

    member = observed[MEMBER_NAME]
    parameter_registry = observed[PARAMETER_NAME]
    method_registry = observed[METHOD_NAME]
    policy = observed[POLICY_NAME]
    manifest = observed[MANIFEST_NAME]
    seal_request = observed[SEAL_REQUEST_NAME]
    bundle = observed[BUNDLE_NAME]
    for context, value in (
        ("member", member),
        ("parameter registry", parameter_registry),
        ("method registry", method_registry),
        ("policy", policy),
        ("manifest", manifest),
        ("external review request", seal_request),
        ("bundle", bundle),
    ):
        require_false_claims(value["claim_boundary"], context)

    validate_method_hash_closure(parameter_registry, method_registry)
    validate_prefix_dag(manifest)
    validate_blockers_and_authority(bundle)
    if manifest["subordinate_inventory"] != expected[MANIFEST_NAME]["subordinate_inventory"]:
        raise CandidateValidationError("48-file subordinate inventory drift")
    if len(manifest["subordinate_inventory"]) != 48:
        raise CandidateValidationError("manifest must bind 12 row and 36 partition files")
    if (
        policy["ordering"]["external_predecessor_commitment_present"] is not False
        or policy["ordering"]["policy_predecessor_order_independently_sealed"] is not False
        or policy["ordering"]["current_enclosure_sources_eligible_for_acceptance"] is not False
        or policy["ordering"]["retroactive_acceptance_authorized"] is not False
        or policy["ordering"]["future_replay_required"] is not True
        or policy["threshold_lineage"]["threshold_loosening_detected"] is not False
        or policy["threshold_lineage"]["post_enclosure_adaptation_allowed"] is not False
    ):
        raise CandidateValidationError("anti-vacuity predecessor ordering/threshold drift")
    local_state = seal_request["local_state"]
    if any(value is not False for value in local_state.values()):
        raise CandidateValidationError(
            "external review request falsely claims local external authority"
        )
    requested = seal_request["requested_external_record"]
    if set(requested["accepted_authentication_classes"]).intersection(
        requested["forbidden_evidence_classes"]
    ):
        raise CandidateValidationError("seal authentication classes overlap")
    if bundle["reserved_basename_absence_required"] != sorted(RESERVED_BASENAMES):
        raise CandidateValidationError("reserved basename absence contract drift")
    inventory = bundle["file_inventory"]
    expected_inventory_names = [name for name in PACKAGE_NAMES if name != BUNDLE_NAME]
    if [entry["path"] for entry in inventory] != expected_inventory_names:
        raise CandidateValidationError("bundle file inventory order/path drift")
    for entry in inventory:
        payload = snapshots[entry["path"]]
        if entry["sha256"] != file_sha256(payload) or entry["byte_length"] != len(payload):
            raise CandidateValidationError("bundle file inventory hash/length drift")
    return file_sha256(snapshots[BUNDLE_NAME]), counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--package",
        type=Path,
        default=DEFAULT_PACKAGE,
        help="absolute path to the atomic seven-file candidate package",
    )
    arguments = parser.parse_args()
    try:
        if not arguments.package.is_absolute():
            raise CandidateValidationError("--package must be an absolute path")
        bundle_sha, counts = validate_package(arguments.package)
        print(
            "PASS_PREDECESSOR_AUTHORITY_CANDIDATE_VALIDATION "
            f"bundle_sha256={bundle_sha} files=7 "
            f"configurations={counts['configuration_count']} "
            f"partitions={counts['axis_count']} "
            f"cells={counts['axis_cell_count']} "
            f"edges={counts['axis_edge_count']} "
            f"profiles={counts['profile_index_count']} "
            "B04_structural_remedy_prepared=true "
            "B06_structural_remedy_prepared=false "
            "B06_hash_inventory_draft=true "
            "blockers_cleared=0 external_commitment=false replay=false release=false"
        )
        return 0
    except (CandidateValidationError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"ERROR PredecessorAuthorityCandidateValidation: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
