#!/usr/bin/env python3
"""Build the non-promoting Round-177 predecessor-authority candidate.

The package does not directly read role-8--10 artifact bytes.  Its method
inventory nevertheless binds legacy code that contains outcome-specific
hashes, so that inventory is an explicitly incomplete draft.  This package is
not a seal, receipt, formal symbolic candidate, or production replay.  In
particular, this process cannot clear any Round-176 blocker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
import unicodedata
from collections import Counter
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
PACKAGE_RELATIVE: Final = Path(
    "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1"
)

MEMBER_NAME: Final = "continuum_c1_c2_n0_member_spec_v3_candidate.json"
PARAMETER_NAME: Final = "continuum_c1_c2_n0_method_parameter_registry_v2_candidate.json"
METHOD_NAME: Final = "continuum_c1_c2_n0_outward_method_registry_v2_candidate.json"
POLICY_NAME: Final = "continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate.json"
MANIFEST_NAME: Final = "continuum_c1_c2_n0_predecessor_authority_candidate_manifest_v1.json"
SEAL_REQUEST_NAME: Final = "continuum_c1_c2_n0_external_commitment_review_request_v1.json"
BUNDLE_NAME: Final = "bundle.json"
OUTPUT_NAMES: Final = (
    MEMBER_NAME,
    PARAMETER_NAME,
    METHOD_NAME,
    POLICY_NAME,
    MANIFEST_NAME,
    SEAL_REQUEST_NAME,
    BUNDLE_NAME,
)

VALIDATOR_RELATIVE: Final = Path(
    "code/validate_continuum_c1_n0_predecessor_authority_candidate_v1.py"
)
STATIC_TEST_RELATIVE: Final = Path(
    "code/test_continuum_c1_n0_predecessor_authority_candidate_v1.py"
)
MUTATION_TEST_RELATIVE: Final = Path(
    "code/test_continuum_c1_n0_predecessor_authority_candidate_mutations_v1.py"
)

AXIS_ORDER: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)
PROFILE_ORDER: Final = (0, 1, 2, 3)
EXPECTED_ALIGNMENT_COUNTS: Final = {
    "cell_centred_periodic_base": 10,
    "cell_centred_periodic_half_shift": 2,
    "cell_centred_reflecting": 20,
    "vertex_centred_reflecting_dual": 4,
}
EXPECTED_TOTAL_STATES: Final = 34_787_462
EXPECTED_AXIS_CELLS: Final = 5_037
EXPECTED_AXIS_EDGES: Final = 5_013
EXPECTED_PERIODIC_SEAMS: Final = 12

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

FORBIDDEN_BASENAMES: Final = {
    "encounter_c1_gauge_killing_symbolic_candidate_v1.json",
    "encounter_c1_gauge_killing_symbolic_acceptance_receipt_v1.json",
}
_SNAPSHOT_CACHE: dict[Path, tuple[bytes, int]] = {}


class CandidateBuildError(RuntimeError):
    """A predecessor-candidate source or publication invariant failed."""


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > 64:
        raise CandidateBuildError("JSON depth cap exceeded")
    if isinstance(value, float):
        raise CandidateBuildError("JSON floating literals are forbidden")
    if type(value) in (bool, int) or value is None:
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise CandidateBuildError("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise CandidateBuildError("invalid JSON key")
            _strict_tree(item, depth + 1)
        return
    raise CandidateBuildError(f"forbidden JSON type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    _strict_tree(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def domain_digest(domain: str, value: Any) -> str:
    return sha256(domain.encode("ascii") + b"\x00" + canonical_bytes(value))


def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise CandidateBuildError("duplicate or invalid JSON key")
        result[key] = value
    return result


def parse_canonical_json(payload: bytes, role: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=reject_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(
                CandidateBuildError(f"forbidden JSON constant in {role}: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CandidateBuildError(f"{role} is not canonical ASCII JSON") from error
    if type(value) is not dict or canonical_bytes(value) != payload:
        raise CandidateBuildError(f"{role} canonical-byte drift")
    return value


def safe_relative(value: str) -> Path:
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or not pure.parts
        or "." in pure.parts
        or ".." in pure.parts
        or pure.as_posix() != value
    ):
        raise CandidateBuildError(f"unsafe report-relative path: {value!r}")
    return Path(*pure.parts)


def no_symlink_components(path: Path, *, allow_missing_leaf: bool = False) -> None:
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    parts = absolute.parts[1:]
    for index, part in enumerate(parts):
        current /= part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            if allow_missing_leaf and index == len(parts) - 1:
                return
            raise
        if stat.S_ISLNK(info.st_mode):
            raise CandidateBuildError(f"path contains symlink component: {current}")


def secure_mkdirs_no_symlink(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            try:
                os.mkdir(current, 0o755)
            except FileExistsError:
                pass
            info = os.lstat(current)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise CandidateBuildError(
                f"directory path contains a symlink or non-directory: {current}"
            )


def _read_stable_snapshot(path: Path, cap: int) -> bytes:
    absolute = Path(os.path.abspath(path))
    no_symlink_components(absolute)
    if not hasattr(os, "O_NOFOLLOW"):
        raise CandidateBuildError("O_NOFOLLOW unavailable")
    descriptor = os.open(absolute, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size <= 0 or before.st_size > cap:
            raise CandidateBuildError(f"unbounded or nonregular source: {path}")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                raise CandidateBuildError(f"short source read: {path}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise CandidateBuildError(f"source grew during read: {path}")
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)

    def identity(item: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
        return (
            item.st_dev,
            item.st_ino,
            item.st_mode,
            item.st_nlink,
            item.st_size,
            item.st_mtime_ns,
            item.st_ctime_ns,
        )

    if identity(before) != identity(after):
        raise CandidateBuildError(f"source changed during read: {path}")
    lexical = os.lstat(absolute)
    if (lexical.st_dev, lexical.st_ino) != (before.st_dev, before.st_ino):
        raise CandidateBuildError(f"source path replaced during read: {path}")
    return b"".join(chunks)


def stable_snapshot(path: Path, cap: int = 8_000_000) -> bytes:
    absolute = Path(os.path.abspath(path))
    cached = _SNAPSHOT_CACHE.get(absolute)
    if cached is not None:
        payload, original_cap = cached
        if len(payload) > cap:
            raise CandidateBuildError(f"cached source exceeds requested cap: {path}")
        _SNAPSHOT_CACHE[absolute] = (payload, max(original_cap, cap))
        return payload
    payload = _read_stable_snapshot(absolute, cap)
    _SNAPSHOT_CACHE[absolute] = (payload, cap)
    return payload


def verify_snapshot_cache() -> None:
    for path, (expected, cap) in sorted(_SNAPSHOT_CACHE.items(), key=lambda item: str(item[0])):
        observed = _read_stable_snapshot(path, cap)
        if observed != expected:
            raise CandidateBuildError(f"cached input changed during build: {path}")


def pinned_source(role: str) -> tuple[dict[str, Any], bytes]:
    relative, expected = SOURCE_PINS[role]
    payload = stable_snapshot(REPORT / safe_relative(relative))
    observed = sha256(payload)
    if observed != expected:
        raise CandidateBuildError(f"{role} drift: {observed} != {expected}")
    if relative.endswith(".json"):
        return parse_canonical_json(payload, role), payload
    return {}, payload


def source_pin(role: str) -> dict[str, str]:
    path, digest = SOURCE_PINS[role]
    return {"path": path, "sha256": digest}


def generated_pin(name: str, value: Any) -> dict[str, str]:
    return {
        "path": (PACKAGE_RELATIVE / name).as_posix(),
        "sha256": sha256(canonical_bytes(value)),
    }


def rational(value: Any) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise CandidateBuildError(f"canonical rational required: {value!r}")
    result = Fraction(value)
    if f"{result.numerator}/{result.denominator}" != value:
        raise CandidateBuildError(f"noncanonical rational: {value!r}")
    return result


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def expected_partition_geometry(axis: dict[str, Any]) -> dict[str, Any]:
    domain = axis["domain"]
    start_text = domain.get("start_exact", domain.get("lower_exact"))
    width_text = domain.get("period_exact", domain.get("width_exact"))
    start = rational(start_text)
    width = rational(width_text)
    end = start + width
    size = axis["anchor_size"]
    alignment = axis["alignment"]
    shift_text = axis.get("periodic_shift_n0_exact", "0/1")
    shift = rational(shift_text)
    if type(size) is not int or type(size) is bool or size < 2:
        raise CandidateBuildError("invalid axis size")

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
        raise CandidateBuildError(f"unknown alignment: {alignment}")

    if (
        axis["anchor_interval_count"] != interval_count
        or rational(axis["spacing_h0_exact"]) != spacing
    ):
        raise CandidateBuildError("Round172 spacing or interval-count drift")
    return {
        "cell_segments_exact": [
            [[rational_text(left), rational_text(right)] for left, right in cell]
            for cell in segments
        ],
        "cell_volumes_exact": [rational_text(value) for value in volumes],
        "construction": construction,
        "coordinate": axis["coordinate"],
        "domain_start_exact": start_text,
        "domain_width_exact": width_text,
        "periodic": periodic,
        "periodic_shift_exact": shift_text,
        "positions_exact": [rational_text(value) for value in positions],
        "schema": "encounter_exact_axis_partition_v1",
        "size": size,
    }


def digest_record(domain: str, value: Any) -> str:
    return domain_digest(domain, value)


def build_member(
    configuration: dict[str, Any],
    legacy_member: dict[str, Any],
    refinement: dict[str, Any],
    partition_bundle: dict[str, Any],
    reference: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    configurations = configuration["configurations"]
    sequences = refinement["sequences"]
    bundle_rows = partition_bundle["rows"]
    semantics = legacy_member["configuration_semantic_ids"]
    if not (len(configurations) == len(sequences) == len(bundle_rows) == len(semantics) == 12):
        raise CandidateBuildError("configuration cardinality drift")
    labels = [row["label"] for row in configurations]
    if legacy_member["configuration_order"] != labels or len(set(labels)) != len(labels):
        raise CandidateBuildError("configuration order or label uniqueness drift")
    semantic_ids = [
        (
            row["authority_label"],
            row["refinement_family_id"],
            row["refinement_member_id"],
        )
        for row in semantics
    ]
    sequence_ids = [row["sequence_id"] for row in sequences]
    if len(set(semantic_ids)) != 12 or len(set(sequence_ids)) != 12:
        raise CandidateBuildError("semantic or sequence identifier uniqueness drift")

    physical_parameters = reference["physical_parameter_bundle"]
    physical_parameter_digest = digest_record(
        "encounter-physical-parameter-bundle-v1", physical_parameters
    )
    bindings: list[dict[str, Any]] = []
    alignment_counts: Counter[str] = Counter()
    total_states = 0
    total_cells = 0
    total_edges = 0
    periodic_seams = 0

    partition_root = Path(SOURCE_PINS["initial_partition_bundle"][0]).parent
    for index, (config, sequence, bundle_index, semantic) in enumerate(
        zip(configurations, sequences, bundle_rows, semantics, strict=True)
    ):
        label = config["label"]
        if (
            sequence["source_row_index"] != index
            or bundle_index["configuration_index"] != index
            or label != sequence["label"]
            or label != bundle_index["configuration_label"]
            or label != semantic["authority_label"]
            or config["shape"] != sequence["anchor_shape"]
            or config["expected_states"] != sequence["anchor_expected_states"]
            or config["expected_states"] != bundle_index["expected_states"]
        ):
            raise CandidateBuildError(f"row identity drift at configuration {index}")
        if sequence["source_row_canonical_sha256"] != sha256(canonical_bytes(config)):
            raise CandidateBuildError(
                f"Round172 source-row canonical digest drift at configuration {index}"
            )
        row_relative = partition_root / safe_relative(bundle_index["row_manifest"]["path"])
        row_payload = stable_snapshot(REPORT / row_relative)
        if sha256(row_payload) != bundle_index["row_manifest"]["sha256"]:
            raise CandidateBuildError(f"partition row manifest drift at configuration {index}")
        row = parse_canonical_json(row_payload, f"partition row {index}")
        if (
            row["configuration_index"] != index
            or row["configuration_label"] != label
            or row["expected_states"] != config["expected_states"]
            or len(row["axes"]) != 3
            or len(sequence["axes"]) != 3
        ):
            raise CandidateBuildError(f"partition row semantic drift at {index}")

        axes: list[dict[str, Any]] = []
        for axis_index, coordinate in enumerate(AXIS_ORDER):
            sequence_axis = sequence["axes"][axis_index]
            row_axis = row["axes"][axis_index]
            partition_file = row_axis["partition_file"]
            if sequence_axis["coordinate"] != coordinate or row_axis["coordinate"] != coordinate:
                raise CandidateBuildError(f"axis-order drift at {index}:{coordinate}")
            partition_relative = partition_root / safe_relative(partition_file["path"])
            partition_payload = stable_snapshot(REPORT / partition_relative)
            partition_digest = sha256(partition_payload)
            if (
                partition_digest != partition_file["sha256"]
                or len(partition_payload) != partition_file["byte_length"]
            ):
                raise CandidateBuildError(f"partition byte drift at {index}:{coordinate}")
            partition = parse_canonical_json(partition_payload, f"partition {index}:{coordinate}")
            expected = expected_partition_geometry(sequence_axis)
            if partition != expected:
                raise CandidateBuildError(
                    f"independent n0 partition reconstruction failed at {index}:{coordinate}"
                )
            periodic = partition["periodic"]
            cell_count = partition["size"]
            alignment_counts[sequence_axis["alignment"]] += 1
            total_cells += cell_count
            total_edges += cell_count if periodic else cell_count - 1
            periodic_seams += int(periodic)
            exact_box = {
                "domain_start_exact": partition["domain_start_exact"],
                "domain_width_exact": partition["domain_width_exact"],
            }
            axis_binding = {
                "alignment": sequence_axis["alignment"],
                "cell_count": cell_count,
                "coordinate": coordinate,
                "exact_box_or_period": exact_box,
                "partition_report_relative_path": partition_relative.as_posix(),
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
            axes.append(axis_binding)

        geometry_record = {
            "configuration_index": index,
            "configuration_row": config,
            "n0_partition_sha256s": [axis["partition_sha256"] for axis in axes],
        }
        bindings.append(
            {
                "authority_label": label,
                "configuration_geometry_sha256": digest_record(
                    "encounter-configuration-geometry-v1", geometry_record
                ),
                "configuration_index": index,
                "initial_partition_row_manifest_path": row_relative.as_posix(),
                "initial_partition_row_manifest_sha256": sha256(row_payload),
                "n0_anchor_expected_states": config["expected_states"],
                "n0_anchor_shape": config["shape"],
                "n0_axes": axes,
                "physical_parameter_bundle_sha256": physical_parameter_digest,
                "refinement_family_id": semantic["refinement_family_id"],
                "refinement_member_id": semantic["refinement_member_id"],
                "sequence_id": sequence["sequence_id"],
                "sequence_source_row_canonical_sha256": (sequence["source_row_canonical_sha256"]),
                "sequence_source_row_index": index,
            }
        )
        total_states += config["expected_states"]

    counts = {
        "axis_count": sum(alignment_counts.values()),
        "axis_cell_count": total_cells,
        "axis_edge_count": total_edges,
        "configuration_count": len(bindings),
        "periodic_seam_count": periodic_seams,
        "profile_index_count": len(bindings) * len(PROFILE_ORDER),
        "total_virtual_tensor_state_count": total_states,
    }
    if (
        dict(sorted(alignment_counts.items())) != EXPECTED_ALIGNMENT_COUNTS
        or total_states != EXPECTED_TOTAL_STATES
        or total_cells != EXPECTED_AXIS_CELLS
        or total_edges != EXPECTED_AXIS_EDGES
        or periodic_seams != EXPECTED_PERIODIC_SEAMS
    ):
        raise CandidateBuildError("member reconstruction count drift")

    identity = {
        "configuration_order": legacy_member["configuration_order"],
        "configuration_semantic_ids": semantics,
        "coordinate_order": list(AXIS_ORDER),
        "n0_sequence_bindings": bindings,
        "role_bindings_1_through_4": legacy_member["role_bindings"],
        "scalar_convention": legacy_member["member_semantics"]["scalar_convention"],
    }
    member = {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "configuration_order": legacy_member["configuration_order"],
        "configuration_semantic_ids": semantics,
        "identity_properties": {
            "alignment_counts": dict(sorted(alignment_counts.items())),
            "candidate_authoritative": False,
            "current_enclosures_bind_this_candidate": False,
            "n0_partition_sha256s_structurally_bound": True,
            "partition_file_count": 36,
            "round172_source_itself_contains_partition_sha256": False,
            "source_roles_1_through_4_only_in_production_role_bindings": True,
        },
        "member_identity_sha256": digest_record(
            "encounter-continuum-c1-c2-n0-member-identity-v3", identity
        ),
        "member_semantics": {
            "configuration_count": 12,
            "configuration_rows_are_finite_anchors": True,
            "coordinate_order": list(AXIS_ORDER),
            "every_cartesian_interval_endpoint_combination_is_a_model": False,
            "one_formula_defined_correlated_member_per_configuration": True,
            "physical_dimension": 2,
            "quotient_dimension": 3,
            "scalar_convention": legacy_member["member_semantics"]["scalar_convention"],
        },
        "n0_sequence_bindings": bindings,
        "reconstruction_counts": counts,
        "role_bindings": legacy_member["role_bindings"],
        "schema": "encounter_continuum_c1_c2_n0_member_spec_v3_candidate",
        "source_lineage_evidence": {
            "initial_partition_bundle": source_pin("initial_partition_bundle"),
            "joint_refinement_family": source_pin("joint_refinement_family"),
            "legacy_member_spec": source_pin("legacy_member_spec"),
            "round176_member_candidate": source_pin("round176_member_candidate"),
        },
        "status": (
            "STRUCTURAL_PARTITION_IDENTITY_CANDIDATE_ONLY_"
            "NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
        ),
    }
    if any(member["claim_boundary"].values()):
        raise CandidateBuildError("member claim promotion")
    return member, counts


def code_pin(relative: str) -> dict[str, str]:
    payload = stable_snapshot(REPORT / safe_relative(relative), cap=4_000_000)
    return {"path": relative, "sha256": sha256(payload)}


def closure(name: str, keys: tuple[str, ...]) -> dict[str, Any]:
    files = [code_pin(CODE_PATHS[key]) for key in keys]
    return {
        "inventory_id": name,
        "files": files,
        "sha256": digest_record("encounter-method-code-inventory-draft-v1", files),
    }


def parameter_specs() -> list[dict[str, Any]]:
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


def build_parameter_registry() -> dict[str, Any]:
    entries = []
    for specification in parameter_specs():
        entry = dict(specification)
        entry["method_parameter_sha256"] = digest_record(
            "encounter-outward-method-parameters-v2", specification["parameters"]
        )
        entries.append(entry)
    result = {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "parameter_count": len(entries),
        "parameters": entries,
        "schema": "encounter_continuum_c1_c2_n0_method_parameter_registry_v2_candidate",
        "status": "RESULT_BLIND_METHOD_PARAMETER_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED",
    }
    if any(result["claim_boundary"].values()):
        raise CandidateBuildError("parameter-registry claim promotion")
    return result


def build_method_registry(parameter_registry: dict[str, Any]) -> dict[str, Any]:
    closures = {
        "stationary": closure(
            "stationary_authenticated_mpfr_v1",
            (
                "stationary_producer",
                "stationary_verifier",
            ),
        ),
        "raw_flux": closure(
            "raw_flux_authenticated_mpfr_v1",
            (
                "raw_flux_producer",
                "raw_flux_verifier",
            ),
        ),
        "killing": closure(
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
    parameter_by_id = {entry["parameter_id"]: entry for entry in parameter_registry["parameters"]}
    parameter_pin = generated_pin(PARAMETER_NAME, parameter_registry)

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
    methods = []
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
        parameter = parameter_by_id[method_id]
        methods.append(
            {
                "analytic_remainder_rule": remainder,
                "backend_and_version": backend,
                "coordinate_order": list(AXIS_ORDER),
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
                "producer_code_sha256": code_pin(CODE_PATHS[producer_key])["sha256"],
                "rounding_mode": rounding,
                "source_role_scope": role_scope,
                "unit": unit,
                "verifier_code_path": CODE_PATHS[verifier_key],
                "verifier_code_sha256": code_pin(CODE_PATHS[verifier_key])["sha256"],
            }
        )

    result = {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "enumerated_code_inventory_drafts": [closures[key] for key in sorted(closures)],
        "method_count": len(methods),
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
    if any(result["claim_boundary"].values()):
        raise CandidateBuildError("method-registry claim promotion")
    return result


def build_policy(
    legacy_policy: dict[str, Any],
    member: dict[str, Any],
    method_registry: dict[str, Any],
) -> dict[str, Any]:
    result = {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "join_requirements": {
            "axis_order_exact": list(AXIS_ORDER),
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
            "legacy_policy": source_pin("legacy_policy"),
            "member_spec_v3_candidate": generated_pin(MEMBER_NAME, member),
            "outward_method_registry_v2_candidate": generated_pin(METHOD_NAME, method_registry),
            "round176_policy_candidate": source_pin("round176_policy_candidate"),
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
    if any(result["claim_boundary"].values()):
        raise CandidateBuildError("policy claim promotion")
    return result


def build_manifest(
    member: dict[str, Any],
    parameter_registry: dict[str, Any],
    method_registry: dict[str, Any],
    policy: dict[str, Any],
    counts: dict[str, int],
) -> dict[str, Any]:
    roles = [
        {"role": "role1_reference_density_source", **source_pin("reference_density_source")},
        {"role": "role2_ideal_formula_source", **source_pin("ideal_formula_source")},
        {"role": "role3_factorization_source", **source_pin("factorization_source")},
        {"role": "role4_configuration_source", **source_pin("configuration_source")},
        {"role": "role5_member_spec_candidate", **generated_pin(MEMBER_NAME, member)},
        {
            "role": "role6_outward_method_registry_candidate",
            **generated_pin(METHOD_NAME, method_registry),
        },
        {"role": "role7_anti_vacuity_policy_candidate", **generated_pin(POLICY_NAME, policy)},
        {
            "role": "role11_symbolic_control_method_source",
            **source_pin("symbolic_control_method_source"),
        },
    ]
    supporting = [
        {"role": "joint_refinement_family", **source_pin("joint_refinement_family")},
        {"role": "initial_partition_bundle", **source_pin("initial_partition_bundle")},
        {"role": "legacy_member_spec", **source_pin("legacy_member_spec")},
        {"role": "legacy_policy", **source_pin("legacy_policy")},
        {
            "role": "round176_member_candidate",
            **source_pin("round176_member_candidate"),
        },
        {
            "role": "round176_policy_candidate",
            **source_pin("round176_policy_candidate"),
        },
        {"role": "control_method_commitment", **source_pin("control_method_commitment")},
        {"role": "killing_geometry_authority", **source_pin("killing_geometry_authority")},
        {
            "role": "method_parameter_registry_candidate",
            **generated_pin(PARAMETER_NAME, parameter_registry),
        },
    ]
    subordinate_inventory = []
    subordinate_edges = []
    for row in member["n0_sequence_bindings"]:
        row_index = row["configuration_index"]
        row_role = f"initial_partition_row_{row_index:02d}"
        subordinate_inventory.append(
            {
                "path": row["initial_partition_row_manifest_path"],
                "role": row_role,
                "sha256": row["initial_partition_row_manifest_sha256"],
            }
        )
        subordinate_edges.append(["initial_partition_bundle", row_role])
        for axis in row["n0_axes"]:
            partition_role = f"initial_partition_{row_index:02d}_{axis['coordinate']}"
            subordinate_inventory.append(
                {
                    "path": axis["partition_report_relative_path"],
                    "role": partition_role,
                    "sha256": axis["partition_sha256"],
                }
            )
            subordinate_edges.extend(
                [
                    [row_role, partition_role],
                    [partition_role, "role5_member_spec_candidate"],
                ]
            )
    if len(subordinate_inventory) != 48:
        raise CandidateBuildError("predecessor subordinate inventory must contain 48 files")
    code_inventory = []
    for key in sorted(CODE_PATHS):
        code_inventory.append({"role": f"code_{key}", **code_pin(CODE_PATHS[key])})

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
    for entry in code_inventory:
        edges.append([entry["role"], "role6_outward_method_registry_candidate"])
    edges.extend(subordinate_edges)
    result = {
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
    if any(result["claim_boundary"].values()):
        raise CandidateBuildError("manifest claim promotion")
    return result


def build_seal_request(
    member: dict[str, Any],
    parameter_registry: dict[str, Any],
    method_registry: dict[str, Any],
    policy: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    commitment_set = [
        {"role": "member_spec_candidate", **generated_pin(MEMBER_NAME, member)},
        {
            "role": "method_parameter_registry_candidate",
            **generated_pin(PARAMETER_NAME, parameter_registry),
        },
        {
            "role": "outward_method_registry_candidate",
            **generated_pin(METHOD_NAME, method_registry),
        },
        {"role": "anti_vacuity_policy_candidate", **generated_pin(POLICY_NAME, policy)},
        {
            "role": "predecessor_authority_candidate_manifest",
            **generated_pin(MANIFEST_NAME, manifest),
        },
        {"role": "candidate_builder", **code_pin(str(SELF.relative_to(REPORT)))},
        {"role": "independent_candidate_validator", **code_pin(VALIDATOR_RELATIVE.as_posix())},
        {"role": "candidate_static_tests", **code_pin(STATIC_TEST_RELATIVE.as_posix())},
        {"role": "candidate_mutation_tests", **code_pin(MUTATION_TEST_RELATIVE.as_posix())},
    ]
    message_sha = digest_record(
        "encounter-external-predecessor-commitment-request-v1", commitment_set
    )
    result = {
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
    if any(result["claim_boundary"].values()):
        raise CandidateBuildError("seal-request claim promotion")
    return result


def blocker_ledger() -> list[dict[str, Any]]:
    structural = {
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
    result = []
    for blocker in BLOCKERS:
        prepared, note = structural.get(
            blocker,
            (False, "no authoritative structural remedy is materialized in this package"),
        )
        result.append(
            {
                "blocker_id": blocker,
                "cleared": False,
                "structural_remedy_prepared": prepared,
                "structural_note": note,
            }
        )
    return result


def build_bundle(
    payloads: dict[str, dict[str, Any]],
    counts: dict[str, int],
) -> dict[str, Any]:
    inventory = [
        {
            "byte_length": len(canonical_bytes(payloads[name])),
            "path": name,
            "sha256": sha256(canonical_bytes(payloads[name])),
        }
        for name in OUTPUT_NAMES
        if name != BUNDLE_NAME
    ]
    claims = {key: False for key in CLAIM_KEYS}
    result = {
        "blocking_conditions": blocker_ledger(),
        "claim_boundary": claims,
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
        "reserved_basename_absence_required": sorted(FORBIDDEN_BASENAMES),
        "schema": "encounter_continuum_c1_c2_n0_predecessor_authority_candidate_bundle_v1",
        "status": (
            "PASS_PREPRODUCTION_PREDECESSOR_AUTHORITY_STRUCTURAL_CANDIDATE_ONLY_"
            "B04_REMEDY_PREPARED_B06_HASH_INVENTORY_DRAFT_NO_BLOCKER_CLEARED"
        ),
    }
    if any(claims.values()) or any(item["cleared"] for item in result["blocking_conditions"]):
        raise CandidateBuildError("bundle promotion")
    return result


def build_outputs() -> dict[str, dict[str, Any]]:
    _SNAPSHOT_CACHE.clear()
    loaded = {role: pinned_source(role)[0] for role in SOURCE_PINS}
    member, counts = build_member(
        loaded["configuration_source"],
        loaded["legacy_member_spec"],
        loaded["joint_refinement_family"],
        loaded["initial_partition_bundle"],
        loaded["reference_density_source"],
    )
    parameter_registry = build_parameter_registry()
    method_registry = build_method_registry(parameter_registry)
    policy = build_policy(loaded["legacy_policy"], member, method_registry)
    manifest = build_manifest(member, parameter_registry, method_registry, policy, counts)
    seal_request = build_seal_request(member, parameter_registry, method_registry, policy, manifest)
    payloads = {
        MEMBER_NAME: member,
        PARAMETER_NAME: parameter_registry,
        METHOD_NAME: method_registry,
        POLICY_NAME: policy,
        MANIFEST_NAME: manifest,
        SEAL_REQUEST_NAME: seal_request,
    }
    payloads[BUNDLE_NAME] = build_bundle(payloads, counts)
    verify_snapshot_cache()
    return payloads


def write_file_exclusive(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o444)
    try:
        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0:
                raise CandidateBuildError(f"short package write: {path.name}")
            written += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def compare_package(destination: Path, outputs: dict[str, dict[str, Any]]) -> None:
    no_symlink_components(destination)
    info = os.lstat(destination)
    if not stat.S_ISDIR(info.st_mode):
        raise CandidateBuildError("candidate package is not a directory")
    observed_names = sorted(entry.name for entry in os.scandir(destination))
    if observed_names != sorted(OUTPUT_NAMES):
        raise CandidateBuildError("candidate package filename inventory drift")
    for name in OUTPUT_NAMES:
        path = destination / name
        before = os.lstat(path)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_mode & 0o222:
            raise CandidateBuildError(
                f"immutable single-link regular package file required: {name}"
            )
        expected = canonical_bytes(outputs[name])
        observed = stable_snapshot(path)
        after = os.lstat(path)
        if (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_nlink,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_nlink,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise CandidateBuildError(f"candidate package file changed during check: {name}")
        if observed != expected:
            raise CandidateBuildError(
                f"candidate output drift for {name}: {sha256(observed)} != {sha256(expected)}"
            )


def publish_package(destination: Path, outputs: dict[str, dict[str, Any]]) -> None:
    parent = destination.parent
    secure_mkdirs_no_symlink(parent)
    no_symlink_components(destination, allow_missing_leaf=True)
    if destination.exists():
        raise CandidateBuildError("candidate package already exists; use --check")
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=parent))
    published = False
    try:
        for name in OUTPUT_NAMES:
            write_file_exclusive(staging / name, canonical_bytes(outputs[name]))
        directory_descriptor = os.open(staging, os.O_RDONLY | os.O_CLOEXEC)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
        if destination.exists():
            raise CandidateBuildError("candidate package appeared before publish")
        os.rename(staging, destination)
        published = True
        parent_descriptor = os.open(parent, os.O_RDONLY | os.O_CLOEXEC)
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
        compare_package(destination, outputs)
    finally:
        if not published:
            shutil.rmtree(staging, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPORT,
        help="root under which the canonical report-relative package is published",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate exact current package bytes without writing",
    )
    arguments = parser.parse_args()
    try:
        outputs = build_outputs()
        destination = Path(os.path.abspath(arguments.output_root)) / PACKAGE_RELATIVE
        verify_snapshot_cache()
        if arguments.check:
            compare_package(destination, outputs)
        else:
            publish_package(destination, outputs)
        verify_snapshot_cache()
        bundle_bytes = canonical_bytes(outputs[BUNDLE_NAME])
        print(
            "PASS_PREDECESSOR_AUTHORITY_CANDIDATE_BUILD "
            f"bundle_sha256={sha256(bundle_bytes)} files={len(outputs)} "
            "configurations=12 partitions=36 methods=9 "
            "B04_structural_remedy_prepared=true "
            "B06_structural_remedy_prepared=false "
            "B06_hash_inventory_draft=true "
            "blockers_cleared=0 external_commitment=false replay=false release=false"
        )
        return 0
    except (CandidateBuildError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"ERROR PredecessorAuthorityCandidateBuild: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
