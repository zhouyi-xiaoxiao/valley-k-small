"""Bind replayed control-free axis geometry to native packed rate payloads.

The accepted input is the twelve-row file bundle plus a freshly reconstructed
deterministic relational receipt.  Big-endian forward/backward endpoint files
are decoded and repacked to the host-native immutable format with no numerical
arithmetic; every destination is round-tripped back to the canonical
big-endian bytes.  A wrapper retains the row, partition, axis-relation, replay,
and conversion joins that the bare ``PackedAxisPayload`` type cannot carry.

Only the free-axis part of the future operator is bound.  This module never
creates killing data, ``PackedKernelInputs``, a tensor kernel, a propagated
target, or an F0/F1 result.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import math
import os
import stat
import struct
import sys
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Final

_CODE_DIRECTORY = Path(__file__).resolve().parent
if str(_CODE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(_CODE_DIRECTORY))

import rate_defined_tensor_f0_packed as packed  # noqa: E402
import rate_defined_tensor_f0_production_initial_independent as independent  # noqa: E402
import rate_defined_tensor_f0_production_initial_rebuild as rebuild  # noqa: E402

SCHEMA: Final = "encounter_geometry_bound_packed_axes_v1"
CONVERSION_SCHEMA: Final = "encounter_be_to_native_packed_rate_receipt_v1"
RECEIPT_SCHEMA: Final = "encounter_geometry_bound_packed_axes_receipt_v1"
CONVERSION_ID: Final = "decode_be_binary64_repack_native_binary64_no_arithmetic_v1"
STATUS: Final = (
    "PASS_INDEPENDENTLY_VERIFIED_FREE_AXIS_GEOMETRY_RATE_PACKED_BINDING_"
    "ONLY_NOT_FULL_OPERATOR_NOT_F0"
)
RECEIPT_STATUS: Final = (
    "PASS_12_ROW_FREE_AXIS_GEOMETRY_PACKED_BINDING_ONLY_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
PACKED_SOURCE_SHA256: Final = "447aa3bc224685ea1cc556d9d322dafba05ef148945d4ae41291f83e29f3deb4"
REBUILD_SOURCE_SHA256: Final = "1ed8ea255df01fca10e294994557b1efc8660f933683477a5a289593da7c1c14"
INDEPENDENT_SOURCE_SHA256: Final = (
    "e0121dd2f90bbebc5f973f4e80f7b43dea5ec2d0ac04e1f253a6618b35cf0a96"
)
COORDINATES: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
VALIDATION_BLOCK_SIZE: Final = 65_536
MAXIMUM_WORKING_BYTES: Final = 2_000_000


class GeometryBoundPackedAxesFailure(RuntimeError):
    """Fail-closed error for canonical-BE to geometry-bound packed conversion."""


@dataclass(frozen=True, slots=True)
class GeometryBoundPackedAxes:
    schema: str
    status: str
    configuration_index: int
    configuration_label: str
    tensor_shape: tuple[int, int, int]
    row_relation_sha256: str
    source_box_relation_sha256: str
    relational_rebuild_receipt_sha256: str
    relational_rebuild_receipt_bytes: bytes
    independent_semantic_receipt_sha256: str
    independent_semantic_receipt_bytes: bytes
    partition_sha256s: tuple[str, str, str]
    axis_relation_sha256s: tuple[str, str, str]
    stationary_mass_raw_sha256s: tuple[str, str, str]
    axes: tuple[packed.PackedAxisPayload, packed.PackedAxisPayload, packed.PackedAxisPayload]
    conversion_receipts: tuple[dict[str, object], ...]
    wrapper_binding_sha256: str
    relational_rebuild_receipt_retained: bool
    independent_semantic_receipt_retained: bool
    canonical_to_native_conversion_bound: bool
    free_axis_operator_geometry_bound: bool
    independent_source_partition_free_axis_semantic_replay_complete: bool
    independent_semantic_replay_complete: bool
    killing_contact_geometry_bound: bool
    full_operator_bound: bool
    propagation_executed: bool
    positive_budget_executed: bool
    production_resource_gate: bool
    f0_pass: bool


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha(_read_regular(path))


def _canonical(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _digest(domain: bytes, payload: object) -> str:
    if not domain.endswith(b"\0"):
        raise GeometryBoundPackedAxesFailure("digest domain is not terminated")
    return _sha(domain + _canonical(payload))


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise GeometryBoundPackedAxesFailure("JSON has a duplicate or invalid key")
        result[key] = value
    return result


def _parse_canonical(source: bytes, *, label: str) -> dict[str, object]:
    try:
        payload = json.loads(source.decode("ascii"), object_pairs_hook=_strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GeometryBoundPackedAxesFailure(f"{label} is not strict JSON") from error
    if type(payload) is not dict or _canonical(payload) != source:
        raise GeometryBoundPackedAxesFailure(f"{label} is not a canonical object")
    return payload


def _read_regular(path: Path, *, maximum: int = 10_000_000) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise GeometryBoundPackedAxesFailure(f"required file unavailable: {path}") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise GeometryBoundPackedAxesFailure(f"required file is unsafe/oversized: {path}")
        chunks: list[bytes] = []
        observed = 0
        while block := os.read(descriptor, min(1 << 20, maximum + 1 - observed)):
            chunks.append(block)
            observed += len(block)
            if observed > maximum:
                raise GeometryBoundPackedAxesFailure(f"required file is oversized: {path}")
        after = os.fstat(descriptor)
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ) or observed != before.st_size:
            raise GeometryBoundPackedAxesFailure(f"required file changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _safe_join(root: Path, relative: object) -> Path:
    if type(relative) is not str:
        raise GeometryBoundPackedAxesFailure("bundle relative path type is invalid")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or pure.as_posix() != relative:
        raise GeometryBoundPackedAxesFailure("bundle relative path is unsafe")
    return root / Path(*pure.parts)


def _packed_manifest_payload(manifest: packed.PackedIntervalManifest) -> dict[str, object]:
    packed.validate_packed_interval_manifest(manifest)
    return {
        "array_shape": list(manifest.array_shape),
        "block_size": manifest.block_size,
        "endpoint_order": manifest.endpoint_order,
        "logical_shape": list(manifest.logical_shape),
        "maximum_working_bytes": manifest.maximum_working_bytes,
        "nonnegative": manifest.nonnegative,
        "raw_byte_length": manifest.raw_byte_length,
        "raw_sha256": manifest.raw_sha256,
        "role": manifest.role,
        "schema": manifest.schema,
        "state_count": manifest.state_count,
    }


def _decode_be_pairs(source: bytes, *, expected_count: int) -> tuple[tuple[float, float], ...]:
    if len(source) != 16 * expected_count:
        raise GeometryBoundPackedAxesFailure("canonical BE rate length drifted")
    pairs: list[tuple[float, float]] = []
    for lower, upper in struct.iter_unpack(">dd", source):
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or lower < 0.0
            or lower > upper
            or (lower == 0.0 and math.copysign(1.0, lower) < 0)
            or (upper == 0.0 and math.copysign(1.0, upper) < 0)
        ):
            raise GeometryBoundPackedAxesFailure("canonical BE rate endpoint is invalid")
        pairs.append((lower, upper))
    return tuple(pairs)


def _native_roundtrip(payload: packed.PackedIntervalPayload) -> bytes:
    packed.validate_packed_interval_payload(payload)
    source = payload.raw_bytes
    result = bytearray(len(source))
    for index in range(payload.manifest.state_count):
        lower, upper = struct.unpack_from("=dd", source, 16 * index)
        struct.pack_into(">dd", result, 16 * index, lower, upper)
    return bytes(result)


def _conversion_receipt(
    *,
    row_index: int,
    row_label: str,
    axis_name: str,
    direction: str,
    partition_sha256: str,
    axis_relation_sha256: str,
    source_file: dict[str, object],
    source_manifest: dict[str, object],
    source_bytes: bytes,
    destination: packed.PackedIntervalPayload,
) -> dict[str, object]:
    roundtrip = _native_roundtrip(destination)
    if not hmac.compare_digest(roundtrip, source_bytes):
        raise GeometryBoundPackedAxesFailure("native packed bytes do not round-trip to source BE")
    packed_manifest = _packed_manifest_payload(destination.manifest)
    core = {
        "axis_name": axis_name,
        "axis_relation_sha256": axis_relation_sha256,
        "conversion_id": CONVERSION_ID,
        "direction": direction,
        "destination_native_raw_byte_length": len(destination.raw_bytes),
        "destination_native_raw_sha256": _sha(destination.raw_bytes),
        "destination_packed_manifest_sha256": _digest(
            b"geometry-bound-packed-destination-manifest-v1\0", packed_manifest
        ),
        "host_byteorder": sys.byteorder,
        "native_roundtrip_to_canonical_be": True,
        "partition_sha256": partition_sha256,
        "row_index": row_index,
        "row_label": row_label,
        "schema": CONVERSION_SCHEMA,
        "source_be_file": source_file,
        "source_be_manifest": source_manifest,
        "source_be_manifest_sha256": _digest(
            b"geometry-bound-packed-source-be-manifest-v1\0", source_manifest
        ),
        "source_be_raw_byte_length": len(source_bytes),
        "source_be_raw_sha256": _sha(source_bytes),
    }
    return {
        **core,
        "conversion_receipt_sha256": _digest(
            b"geometry-bound-packed-conversion-receipt-v1\0", core
        ),
    }


def _wrapper_binding_payload(wrapper: GeometryBoundPackedAxes) -> dict[str, object]:
    return {
        "axis_relation_sha256s": list(wrapper.axis_relation_sha256s),
        "configuration_index": wrapper.configuration_index,
        "configuration_label": wrapper.configuration_label,
        "conversion_receipt_sha256s": [
            receipt["conversion_receipt_sha256"] for receipt in wrapper.conversion_receipts
        ],
        "destination_packed_manifest_sha256s": [
            _digest(
                b"geometry-bound-packed-destination-manifest-v1\0",
                _packed_manifest_payload(payload.manifest),
            )
            for axis in wrapper.axes
            for payload in (axis.forward, axis.backward)
        ],
        "partition_sha256s": list(wrapper.partition_sha256s),
        "independent_semantic_receipt_sha256": wrapper.independent_semantic_receipt_sha256,
        "relational_rebuild_receipt_sha256": wrapper.relational_rebuild_receipt_sha256,
        "row_relation_sha256": wrapper.row_relation_sha256,
        "source_box_relation_sha256": wrapper.source_box_relation_sha256,
        "stationary_mass_raw_sha256s": list(wrapper.stationary_mass_raw_sha256s),
        "tensor_shape": list(wrapper.tensor_shape),
    }


def validate_geometry_bound_packed_axes_structure_only(
    wrapper: GeometryBoundPackedAxes,
) -> None:
    """Validate retained bytes and joins, without re-opening the source bundle.

    This is deliberately not an authority check for a publicly constructed
    dataclass.  Use :func:`verify_geometry_bound_packed_axes` when the source
    bundle is available.
    """

    if type(wrapper) is not GeometryBoundPackedAxes:
        raise GeometryBoundPackedAxesFailure("geometry-bound wrapper has wrong exact type")
    if (
        wrapper.schema != SCHEMA
        or wrapper.status != STATUS
        or type(wrapper.configuration_index) is not int
        or wrapper.configuration_index < 0
        or type(wrapper.configuration_label) is not str
        or len(wrapper.axes) != 3
        or tuple(axis.name for axis in wrapper.axes) != COORDINATES
        or tuple(axis.size for axis in wrapper.axes) != wrapper.tensor_shape
        or len(wrapper.partition_sha256s) != 3
        or len(wrapper.axis_relation_sha256s) != 3
        or len(wrapper.stationary_mass_raw_sha256s) != 3
        or len(wrapper.conversion_receipts) != 6
    ):
        raise GeometryBoundPackedAxesFailure("geometry-bound wrapper structure drifted")
    if type(wrapper.relational_rebuild_receipt_bytes) is not bytes:
        raise GeometryBoundPackedAxesFailure("retained relational receipt is invalid")
    relational_receipt = _parse_canonical(
        wrapper.relational_rebuild_receipt_bytes, label="retained relational receipt"
    )
    if "receipt_sha256" not in relational_receipt:
        raise GeometryBoundPackedAxesFailure("retained relational receipt is invalid")
    relational_core = {
        key: value for key, value in relational_receipt.items() if key != "receipt_sha256"
    }
    if (
        relational_receipt["receipt_sha256"]
        != _digest(b"production-initial-relational-rebuild-receipt-v1\0", relational_core)
        or relational_receipt["receipt_sha256"] != wrapper.relational_rebuild_receipt_sha256
        or relational_receipt.get("schema") != rebuild.RECEIPT_SCHEMA
        or relational_receipt.get("status") != rebuild.RECEIPT_STATUS
        or relational_receipt.get("rebuild_source_sha256") != REBUILD_SOURCE_SHA256
        or _sha_file(Path(rebuild.__file__).resolve()) != REBUILD_SOURCE_SHA256
        or type(relational_receipt.get("rows")) is not list
        or wrapper.configuration_index >= len(relational_receipt["rows"])
    ):
        raise GeometryBoundPackedAxesFailure("retained relational receipt binding drifted")
    replayed_row = relational_receipt["rows"][wrapper.configuration_index]
    if (
        type(replayed_row) is not dict
        or replayed_row.get("configuration_index") != wrapper.configuration_index
        or replayed_row.get("configuration_label") != wrapper.configuration_label
        or replayed_row.get("tensor_shape") != list(wrapper.tensor_shape)
        or replayed_row.get("expected_states") != math.prod(wrapper.tensor_shape)
        or replayed_row.get("row_relation_sha256") != wrapper.row_relation_sha256
        or replayed_row.get("source_box_relation_sha256") != wrapper.source_box_relation_sha256
    ):
        raise GeometryBoundPackedAxesFailure("retained row/rebuild join drifted")
    if type(wrapper.independent_semantic_receipt_bytes) is not bytes:
        raise GeometryBoundPackedAxesFailure("retained independent receipt is invalid")
    semantic_receipt = _parse_canonical(
        wrapper.independent_semantic_receipt_bytes,
        label="retained independent receipt",
    )
    if "receipt_sha256" not in semantic_receipt:
        raise GeometryBoundPackedAxesFailure("retained independent receipt is invalid")
    semantic_core = {
        key: value for key, value in semantic_receipt.items() if key != "receipt_sha256"
    }
    semantic_flags = semantic_receipt.get("flags")
    if (
        semantic_receipt["receipt_sha256"]
        != _digest(b"production-initial-independent-semantic-receipt-v1\0", semantic_core)
        or semantic_receipt["receipt_sha256"] != wrapper.independent_semantic_receipt_sha256
        or semantic_receipt.get("schema") != independent.SCHEMA
        or semantic_receipt.get("status") != independent.STATUS
        or semantic_receipt.get("verifier_source_sha256") != INDEPENDENT_SOURCE_SHA256
        or _sha_file(Path(independent.__file__).resolve()) != INDEPENDENT_SOURCE_SHA256
        or semantic_receipt.get("bundle_manifest_sha256")
        != relational_receipt.get("bundle_manifest_sha256")
        or semantic_receipt.get("configuration_sha256")
        != relational_receipt.get("configuration_sha256")
        or semantic_receipt.get("family_relation_sha256")
        != relational_receipt.get("family_relation_sha256")
        or type(semantic_flags) is not dict
        or semantic_flags.get("independent_numerical_implementation") is not True
        or semantic_flags.get("independent_semantic_replay_complete_for_declared_scope") is not True
        or type(semantic_receipt.get("rows")) is not list
        or wrapper.configuration_index >= len(semantic_receipt["rows"])
    ):
        raise GeometryBoundPackedAxesFailure("retained independent receipt binding drifted")
    semantic_row = semantic_receipt["rows"][wrapper.configuration_index]
    if (
        type(semantic_row) is not dict
        or semantic_row.get("configuration_index") != wrapper.configuration_index
        or semantic_row.get("configuration_label") != wrapper.configuration_label
        or semantic_row.get("tensor_shape") != list(wrapper.tensor_shape)
        or semantic_row.get("row_relation_sha256") != wrapper.row_relation_sha256
        or semantic_row.get("source_box_relation_sha256") != wrapper.source_box_relation_sha256
    ):
        raise GeometryBoundPackedAxesFailure("retained independent row join drifted")
    for axis in wrapper.axes:
        packed.validate_packed_axis_payload(axis)
    receipt_directions = tuple(
        (receipt.get("axis_name"), receipt.get("direction"))
        for receipt in wrapper.conversion_receipts
    )
    expected_directions = tuple(
        (coordinate, direction)
        for coordinate in COORDINATES
        for direction in ("forward", "backward")
    )
    if receipt_directions != expected_directions:
        raise GeometryBoundPackedAxesFailure("conversion receipt order drifted")
    destination_payloads = tuple(
        payload for axis in wrapper.axes for payload in (axis.forward, axis.backward)
    )
    repeated_partitions = tuple(value for value in wrapper.partition_sha256s for _ in range(2))
    repeated_relations = tuple(value for value in wrapper.axis_relation_sha256s for _ in range(2))
    for receipt, destination, partition_sha256, axis_relation_sha256 in zip(
        wrapper.conversion_receipts,
        destination_payloads,
        repeated_partitions,
        repeated_relations,
        strict=True,
    ):
        if type(receipt) is not dict or "conversion_receipt_sha256" not in receipt:
            raise GeometryBoundPackedAxesFailure("conversion receipt structure drifted")
        core = {key: value for key, value in receipt.items() if key != "conversion_receipt_sha256"}
        source_file = receipt.get("source_be_file")
        source_manifest = receipt.get("source_be_manifest")
        roundtrip = _native_roundtrip(destination)
        if (
            receipt["conversion_receipt_sha256"]
            != _digest(b"geometry-bound-packed-conversion-receipt-v1\0", core)
            or receipt.get("schema") != CONVERSION_SCHEMA
            or receipt.get("host_byteorder") != sys.byteorder
            or receipt.get("row_index") != wrapper.configuration_index
            or receipt.get("row_label") != wrapper.configuration_label
            or receipt.get("partition_sha256") != partition_sha256
            or receipt.get("axis_relation_sha256") != axis_relation_sha256
            or receipt.get("conversion_id") != CONVERSION_ID
            or receipt.get("native_roundtrip_to_canonical_be") is not True
            or type(source_file) is not dict
            or set(source_file) != {"byte_length", "path", "sha256"}
            or type(source_manifest) is not dict
            or source_manifest.get("schema") != "encounter_big_endian_binary64_interval_file_v1"
            or source_manifest.get("byte_order") != "big"
            or source_manifest.get("record_format") != ">dd"
            or source_manifest.get("role")
            != f"control_free_axis_{receipt.get('axis_name')}_{receipt.get('direction')}"
            or source_manifest.get("record_count") != destination.manifest.state_count
            or source_manifest.get("logical_shape") != [destination.manifest.state_count]
            or receipt.get("source_be_manifest_sha256")
            != _digest(b"geometry-bound-packed-source-be-manifest-v1\0", source_manifest)
            or source_file.get("sha256") != receipt.get("source_be_raw_sha256")
            or source_file.get("byte_length") != receipt.get("source_be_raw_byte_length")
            or source_manifest.get("raw_sha256") != receipt.get("source_be_raw_sha256")
            or source_manifest.get("raw_byte_length") != receipt.get("source_be_raw_byte_length")
            or len(roundtrip) != receipt.get("source_be_raw_byte_length")
            or _sha(roundtrip) != receipt.get("source_be_raw_sha256")
            or receipt.get("destination_native_raw_sha256") != _sha(destination.raw_bytes)
            or receipt.get("destination_native_raw_byte_length") != len(destination.raw_bytes)
            or receipt.get("destination_packed_manifest_sha256")
            != _digest(
                b"geometry-bound-packed-destination-manifest-v1\0",
                _packed_manifest_payload(destination.manifest),
            )
        ):
            raise GeometryBoundPackedAxesFailure("conversion receipt relation drifted")
    reconstructed_axis_relations: list[str] = []
    for axis_index, coordinate in enumerate(COORDINATES):
        forward_receipt = wrapper.conversion_receipts[2 * axis_index]
        backward_receipt = wrapper.conversion_receipts[2 * axis_index + 1]
        relation = {
            "coordinate": coordinate,
            "partition_sha256": wrapper.partition_sha256s[axis_index],
            "rate_raw_sha256s": {
                "backward": backward_receipt["source_be_raw_sha256"],
                "forward": forward_receipt["source_be_raw_sha256"],
                "stationary_mass": wrapper.stationary_mass_raw_sha256s[axis_index],
            },
        }
        reconstructed = _digest(b"production-initial-axis-geometry-rate-relation-v1\0", relation)
        if reconstructed != wrapper.axis_relation_sha256s[axis_index]:
            raise GeometryBoundPackedAxesFailure("retained axis relation algebra drifted")
        reconstructed_axis_relations.append(reconstructed)
    reconstructed_row_relation = _digest(
        b"production-initial-row-relation-v1\0",
        {
            "axis_relation_sha256s": reconstructed_axis_relations,
            "configuration_index": wrapper.configuration_index,
            "configuration_label": wrapper.configuration_label,
            "source_box_relation_sha256": wrapper.source_box_relation_sha256,
        },
    )
    if reconstructed_row_relation != wrapper.row_relation_sha256:
        raise GeometryBoundPackedAxesFailure("retained row relation algebra drifted")
    if (
        wrapper.relational_rebuild_receipt_retained is not True
        or wrapper.independent_semantic_receipt_retained is not True
        or wrapper.canonical_to_native_conversion_bound is not True
        or wrapper.free_axis_operator_geometry_bound is not True
        or wrapper.independent_source_partition_free_axis_semantic_replay_complete is not True
        or any(
            value is not False
            for value in (
                wrapper.independent_semantic_replay_complete,
                wrapper.killing_contact_geometry_bound,
                wrapper.full_operator_bound,
                wrapper.propagation_executed,
                wrapper.positive_budget_executed,
                wrapper.production_resource_gate,
                wrapper.f0_pass,
            )
        )
    ):
        raise GeometryBoundPackedAxesFailure("geometry-bound wrapper scope flags drifted")
    expected_binding = _digest(
        b"geometry-bound-packed-axes-wrapper-v1\0", _wrapper_binding_payload(wrapper)
    )
    if not hmac.compare_digest(expected_binding, wrapper.wrapper_binding_sha256):
        raise GeometryBoundPackedAxesFailure("geometry-bound wrapper digest drifted")


def build_all_geometry_bound_packed_axes(bundle: Path) -> tuple[GeometryBoundPackedAxes, ...]:
    """Freshly rebuild the bundle, then convert all twelve rows without killing."""

    if not hmac.compare_digest(_sha_file(Path(packed.__file__).resolve()), PACKED_SOURCE_SHA256):
        raise GeometryBoundPackedAxesFailure("accepted packed-core bytes changed")
    if not hmac.compare_digest(_sha_file(Path(rebuild.__file__).resolve()), REBUILD_SOURCE_SHA256):
        raise GeometryBoundPackedAxesFailure("accepted relational-rebuild source bytes changed")
    if not hmac.compare_digest(
        _sha_file(Path(independent.__file__).resolve()), INDEPENDENT_SOURCE_SHA256
    ):
        raise GeometryBoundPackedAxesFailure("accepted independent-verifier source bytes changed")
    relational_receipt = rebuild.rebuild_bundle(bundle)
    semantic_receipt = independent.verify_bundle_independently(bundle)
    receipt_flags = relational_receipt["flags"]
    if (
        receipt_flags["deterministic_relational_rebuild_complete"] is not True
        or receipt_flags["free_axis_geometry_rate_relational_rebuild_complete"] is not True
        or receipt_flags["source_box_relational_rebuild_complete"] is not True
        or receipt_flags["independent_numerical_implementation"] is not False
        or receipt_flags["independent_semantic_replay_complete"] is not False
    ):
        raise GeometryBoundPackedAxesFailure("relational rebuild receipt scope drifted")
    semantic_flags = semantic_receipt["flags"]
    if (
        semantic_flags["independent_numerical_implementation"] is not True
        or semantic_flags["independent_semantic_replay_complete_for_declared_scope"] is not True
        or semantic_flags["free_axis_rate_semantic_containment_complete"] is not True
        or semantic_flags["initial_marginal_semantic_containment_complete"] is not True
        or semantic_flags["initial_component_semantic_containment_complete"] is not True
        or semantic_receipt["bundle_manifest_sha256"]
        != relational_receipt["bundle_manifest_sha256"]
        or semantic_receipt["family_relation_sha256"]
        != relational_receipt["family_relation_sha256"]
    ):
        raise GeometryBoundPackedAxesFailure("independent semantic receipt scope drifted")
    if bundle.is_symlink():
        raise GeometryBoundPackedAxesFailure("bundle root is a symlink")
    root = bundle.resolve()
    bundle_bytes = _read_regular(root / "bundle.json", maximum=2_000_000)
    if not hmac.compare_digest(_sha(bundle_bytes), relational_receipt["bundle_manifest_sha256"]):
        raise GeometryBoundPackedAxesFailure("bundle changed after relational rebuild")
    manifest = _parse_canonical(bundle_bytes, label="bundle manifest")
    wrappers: list[GeometryBoundPackedAxes] = []
    for summary, replayed_row in zip(manifest["rows"], relational_receipt["rows"], strict=True):
        row_bytes = _read_regular(_safe_join(root, summary["row_manifest"]["path"]))
        if len(row_bytes) != summary["row_manifest"]["byte_length"] or not hmac.compare_digest(
            _sha(row_bytes), summary["row_manifest"]["sha256"]
        ):
            raise GeometryBoundPackedAxesFailure("row changed after relational rebuild")
        row = _parse_canonical(row_bytes, label="row manifest")
        if (
            row["configuration_index"] != replayed_row["configuration_index"]
            or row["configuration_label"] != replayed_row["configuration_label"]
            or row["row_relation_sha256"] != replayed_row["row_relation_sha256"]
            or row["source_box_relation_sha256"] != replayed_row["source_box_relation_sha256"]
        ):
            raise GeometryBoundPackedAxesFailure("row relation changed after rebuild")
        axes: list[packed.PackedAxisPayload] = []
        receipts: list[dict[str, object]] = []
        partition_sha256s: list[str] = []
        axis_relation_sha256s: list[str] = []
        stationary_mass_raw_sha256s: list[str] = []
        for axis_entry in row["axes"]:
            axis_name = axis_entry["coordinate"]
            partition_sha256 = axis_entry["partition_file"]["sha256"]
            partition_bytes = _read_regular(_safe_join(root, axis_entry["partition_file"]["path"]))
            if not hmac.compare_digest(_sha(partition_bytes), partition_sha256):
                raise GeometryBoundPackedAxesFailure("partition changed after relational rebuild")
            axis_relation = {
                "coordinate": axis_name,
                "partition_sha256": partition_sha256,
                "rate_raw_sha256s": {
                    name: axis_entry["rates"][name]["file"]["sha256"]
                    for name in sorted(axis_entry["rates"])
                },
            }
            if axis_entry["axis_relation_sha256"] != _digest(
                b"production-initial-axis-geometry-rate-relation-v1\0", axis_relation
            ):
                raise GeometryBoundPackedAxesFailure("axis relation changed after rebuild")
            converted: dict[str, packed.PackedIntervalPayload] = {}
            for direction in ("forward", "backward"):
                source_entry = axis_entry["rates"][direction]
                source_file = source_entry["file"]
                source_manifest = source_entry["manifest"]
                source_bytes = _read_regular(_safe_join(root, source_file["path"]))
                if (
                    len(source_bytes) != source_file["byte_length"]
                    or not hmac.compare_digest(_sha(source_bytes), source_file["sha256"])
                    or source_manifest["raw_sha256"] != source_file["sha256"]
                ):
                    raise GeometryBoundPackedAxesFailure("BE rate changed after relational rebuild")
                pairs = _decode_be_pairs(
                    source_bytes, expected_count=source_manifest["record_count"]
                )
                destination = packed.create_packed_interval_payload(
                    pairs,
                    role=f"science_free_axis_{axis_name}_{direction}",
                    logical_shape=(source_manifest["record_count"],),
                    nonnegative=True,
                    block_size=VALIDATION_BLOCK_SIZE,
                    maximum_working_bytes=MAXIMUM_WORKING_BYTES,
                )
                converted[direction] = destination
                receipts.append(
                    _conversion_receipt(
                        row_index=row["configuration_index"],
                        row_label=row["configuration_label"],
                        axis_name=axis_name,
                        direction=direction,
                        partition_sha256=partition_sha256,
                        axis_relation_sha256=axis_entry["axis_relation_sha256"],
                        source_file=source_file,
                        source_manifest=source_manifest,
                        source_bytes=source_bytes,
                        destination=destination,
                    )
                )
            stationary_entry = axis_entry["rates"]["stationary_mass"]["file"]
            stationary_bytes = _read_regular(_safe_join(root, stationary_entry["path"]))
            if len(stationary_bytes) != stationary_entry["byte_length"] or not hmac.compare_digest(
                _sha(stationary_bytes), stationary_entry["sha256"]
            ):
                raise GeometryBoundPackedAxesFailure(
                    "stationary-mass bytes changed after relational rebuild"
                )
            axis = packed.PackedAxisPayload(
                name=axis_name,
                size=source_manifest["record_count"],
                periodic=axis_name == "relative_perpendicular",
                forward=converted["forward"],
                backward=converted["backward"],
            )
            packed.validate_packed_axis_payload(axis)
            axes.append(axis)
            partition_sha256s.append(partition_sha256)
            axis_relation_sha256s.append(axis_entry["axis_relation_sha256"])
            stationary_mass_raw_sha256s.append(stationary_entry["sha256"])
        provisional = GeometryBoundPackedAxes(
            schema=SCHEMA,
            status=STATUS,
            configuration_index=row["configuration_index"],
            configuration_label=row["configuration_label"],
            tensor_shape=tuple(row["sparse_component_box"]["shape"]),
            row_relation_sha256=row["row_relation_sha256"],
            source_box_relation_sha256=row["source_box_relation_sha256"],
            relational_rebuild_receipt_sha256=relational_receipt["receipt_sha256"],
            relational_rebuild_receipt_bytes=_canonical(relational_receipt),
            independent_semantic_receipt_sha256=semantic_receipt["receipt_sha256"],
            independent_semantic_receipt_bytes=_canonical(semantic_receipt),
            partition_sha256s=tuple(partition_sha256s),
            axis_relation_sha256s=tuple(axis_relation_sha256s),
            stationary_mass_raw_sha256s=tuple(stationary_mass_raw_sha256s),
            axes=tuple(axes),
            conversion_receipts=tuple(receipts),
            wrapper_binding_sha256="0" * 64,
            relational_rebuild_receipt_retained=True,
            independent_semantic_receipt_retained=True,
            canonical_to_native_conversion_bound=True,
            free_axis_operator_geometry_bound=True,
            independent_source_partition_free_axis_semantic_replay_complete=True,
            independent_semantic_replay_complete=False,
            killing_contact_geometry_bound=False,
            full_operator_bound=False,
            propagation_executed=False,
            positive_budget_executed=False,
            production_resource_gate=False,
            f0_pass=False,
        )
        wrapper = replace(
            provisional,
            wrapper_binding_sha256=_digest(
                b"geometry-bound-packed-axes-wrapper-v1\0",
                _wrapper_binding_payload(provisional),
            ),
        )
        validate_geometry_bound_packed_axes_structure_only(wrapper)
        wrappers.append(wrapper)
    if tuple(wrapper.configuration_label for wrapper in wrappers) != tuple(
        row["configuration_label"] for row in relational_receipt["rows"]
    ):
        raise GeometryBoundPackedAxesFailure("geometry-bound row order drifted")
    return tuple(wrappers)


def verify_geometry_bound_packed_axes(
    bundle: Path,
    claimed: GeometryBoundPackedAxes,
) -> GeometryBoundPackedAxes:
    """Rebuild the bundle and require exact equality to one claimed wrapper."""

    if type(claimed) is not GeometryBoundPackedAxes:
        raise GeometryBoundPackedAxesFailure("claimed wrapper has wrong exact type")
    expected_rows = build_all_geometry_bound_packed_axes(bundle)
    if claimed.configuration_index >= len(expected_rows):
        raise GeometryBoundPackedAxesFailure("claimed wrapper row index is outside registry")
    expected = expected_rows[claimed.configuration_index]
    if claimed != expected:
        raise GeometryBoundPackedAxesFailure("claimed wrapper differs from bundle-aware rebuild")
    validate_geometry_bound_packed_axes_structure_only(claimed)
    return claimed


def build_geometry_receipt(bundle: Path) -> dict[str, object]:
    """Build all wrappers and serialize their narrow, non-promoting evidence."""

    wrappers = build_all_geometry_bound_packed_axes(bundle)
    bundle_bytes = _read_regular(bundle.resolve() / "bundle.json", maximum=2_000_000)
    rows = [
        {
            "configuration_index": wrapper.configuration_index,
            "configuration_label": wrapper.configuration_label,
            "conversion_receipt_sha256s": [
                _sha(_canonical(receipt)) for receipt in wrapper.conversion_receipts
            ],
            "independent_semantic_receipt_sha256": (wrapper.independent_semantic_receipt_sha256),
            "relational_rebuild_receipt_sha256": (wrapper.relational_rebuild_receipt_sha256),
            "row_relation_sha256": wrapper.row_relation_sha256,
            "source_box_relation_sha256": wrapper.source_box_relation_sha256,
            "tensor_shape": list(wrapper.tensor_shape),
            "wrapper_binding_sha256": wrapper.wrapper_binding_sha256,
        }
        for wrapper in wrappers
    ]
    core = {
        "bundle_manifest_sha256": _sha(bundle_bytes),
        "configuration_count": len(rows),
        "flags": {
            "authorizes_scientific_execution": False,
            "canonical_to_native_conversion_bound_all_rows": True,
            "clean_process_observed": False,
            "f0_pass": False,
            "free_axis_operator_geometry_bound_all_rows": True,
            "fresh_process": False,
            "full_operator_bound": False,
            "independent_semantic_replay_complete": False,
            "independent_source_partition_free_axis_semantic_replay_complete": True,
            "killing_contact_geometry_bound": False,
            "positive_budget_executed": False,
            "production_resource_gate": False,
            "propagation_executed": False,
            "science_executed": False,
            "topology_complete": False,
        },
        "geometry_source_sha256": _sha_file(Path(__file__).resolve()),
        "independent_source_sha256": INDEPENDENT_SOURCE_SHA256,
        "packed_source_sha256": PACKED_SOURCE_SHA256,
        "rebuild_source_sha256": REBUILD_SOURCE_SHA256,
        "rows": rows,
        "schema": RECEIPT_SCHEMA,
        "status": RECEIPT_STATUS,
    }
    return {
        **core,
        "receipt_sha256": _digest(b"geometry-bound-packed-axes-receipt-v1\0", core),
    }


def write_geometry_receipt(bundle: Path, output: Path) -> dict[str, object]:
    receipt = build_geometry_receipt(bundle)
    if output.exists() or output.is_symlink():
        raise GeometryBoundPackedAxesFailure("receipt output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("xb") as target:
            target.write(_canonical(receipt))
        os.replace(temporary, output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return receipt


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    arguments = parser.parse_args()
    receipt = write_geometry_receipt(arguments.bundle, arguments.receipt)
    print(
        _canonical(
            {"receipt_sha256": receipt["receipt_sha256"], "status": receipt["status"]}
        ).decode("ascii"),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
