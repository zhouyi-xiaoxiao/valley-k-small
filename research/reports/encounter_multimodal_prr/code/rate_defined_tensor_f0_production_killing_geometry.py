"""Produce compact control-free contact and support geometry for all 12 rows.

This layer binds the accepted control-free configuration and exact production
partitions to two kinds of interval-valued geometry:

* one relative two-dimensional contact-fraction field per row; and
* four midpoint support-density fields per row.

The numerical values are reconstructed with the accepted F0 core, so the
result is deliberately labelled same-core producer consistency.  It is not an
independent replay.  In particular, this module never reads a budget or a
control, never forms a concrete killing field or ``PackedKernelInputs``, and
never constructs a full operator, propagates a state, classifies topology, or
executes F0/F1 science.
"""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import hmac
import json
import math
import os
import shutil
import stat
import struct
import sys
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Final, Sequence

_CODE_DIRECTORY = Path(__file__).resolve().parent
if str(_CODE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(_CODE_DIRECTORY))

import rate_defined_tensor_f0 as f0  # noqa: E402
import rate_defined_tensor_f0_production_initial_stream as initial_stream  # noqa: E402

SCHEMA: Final = "encounter_control_free_production_killing_geometry_v1"
ROW_SCHEMA: Final = "encounter_control_free_production_killing_geometry_row_v1"
RAW_SCHEMA: Final = "encounter_big_endian_binary64_interval_file_v1"
SOURCE_SCHEMA: Final = "encounter_physical_killing_geometry_source_v1"
STATUS: Final = (
    "PASS_CONTROL_FREE_12_ROW_KILLING_GEOMETRY_PRODUCER_CONSISTENCY_ONLY_"
    "NOT_INDEPENDENT_NO_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
ROW_STATUS: Final = (
    "PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NO_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0"
)

ACCEPTED_CONFIGURATION_SHA256: Final = (
    "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
)
ACCEPTED_KILLING_SOURCE_SHA256: Final = (
    "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669"
)
ACCEPTED_PARTITION_BUNDLE_SHA256: Final = (
    "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
)
ACCEPTED_F0_SOURCE_SHA256: Final = (
    "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5"
)
ACCEPTED_INITIAL_STREAM_SOURCE_SHA256: Final = (
    "2871976855a0c598b26b8d83b33f4ea3a027a2c826ccdb2ad9b678761093e6cb"
)

CONFIGURATION_RELATIVE_PATH: Final = Path(
    "artifacts/data/physical_configuration_family_control_free_v1.json"
)
KILLING_SOURCE_RELATIVE_PATH: Final = Path(
    "artifacts/data/physical_killing_geometry_source_v1.json"
)
PARTITION_BUNDLE_RELATIVE_PATH: Final = Path(
    "artifacts/data/physical_production_initial_stream_v1/bundle.json"
)
F0_SOURCE_RELATIVE_PATH: Final = Path("code/rate_defined_tensor_f0.py")
INITIAL_STREAM_SOURCE_RELATIVE_PATH: Final = Path(
    "code/rate_defined_tensor_f0_production_initial_stream.py"
)
PRODUCER_SOURCE_RELATIVE_PATH: Final = Path(
    "code/rate_defined_tensor_f0_production_killing_geometry.py"
)
PARTITION_BUNDLE_DIRECTORY_RELATIVE_PATH: Final = PARTITION_BUNDLE_RELATIVE_PATH.parent

PANELS_PER_UNIT: Final = 16_384
PRECISION_BITS: Final = 192
CONTACT_COORDINATE_ORDER: Final = ("relative_parallel", "relative_perpendicular")
TOTAL_CONTACT_RECORDS: Final = 233_139
TOTAL_MIDPOINT_CELLS: Final = 1_713
TOTAL_SUPPORT_PROFILES: Final = 48
TOTAL_SUPPORT_RECORDS: Final = 6_852
TOTAL_RAW_RECORDS: Final = TOTAL_CONTACT_RECORDS + TOTAL_SUPPORT_RECORDS
TOTAL_RAW_BYTES: Final = 16 * TOTAL_RAW_RECORDS
EXPECTED_INVENTORY_FILES: Final = 75
EXPECTED_INVENTORY_DIRECTORIES: Final = 14
MAXIMUM_BUNDLE_TREE_NODES: Final = 128
MAXIMUM_BUNDLE_RELATIVE_DEPTH: Final = 3
ANALYTIC_AREA_PRECISION_BITS: Final = 256
CONTACT_AREA_WIDTH_OVER_RADIUS_SQUARED_CAP: Final = Fraction(1, 10_000_000_000)
ANALYTIC_AREA_WIDTH_OVER_RADIUS_SQUARED_CAP: Final = Fraction(1, 1_000_000_000_000)
SUPPORT_INTEGRAL_WIDTH_CAP: Final = Fraction(1, 10_000_000_000)

_FACTORIZATION_CONTRACT: Final = {
    "budget_and_weights_present": False,
    "concrete_killing_constructed": False,
    "contact_flat_index_formula": "a*n_Y+b",
    "contact_logical_shape": ["n_R", "n_Y"],
    "coordinate_order": ["midpoint", "relative_parallel", "relative_perpendicular"],
    "factorized_basis_formula": "H_j[i_M,a,b]=Phi_j[i_M]*C[a,b]",
    "full_flat_index_formula": "i=(i_M*n_R+i_R)*n_Y+i_Y",
    "full_logical_shape": ["n_M", "n_R", "n_Y"],
    "midpoint_broadcast": "C[a,b]_is_broadcast_unchanged_over_i_M",
    "ordered_profile_mapping": [
        {
            "centre_exact": "3152519739159347/9007199254740992",
            "profile_index": 0,
            "raw_role": "physical_midpoint_support_density_00",
        },
        {
            "centre_exact": "5404319552844595/9007199254740992",
            "profile_index": 1,
            "raw_role": "physical_midpoint_support_density_01",
        },
        {
            "centre_exact": "3/4",
            "profile_index": 2,
            "raw_role": "physical_midpoint_support_density_02",
        },
        {
            "centre_exact": "8106479329266893/9007199254740992",
            "profile_index": 3,
            "raw_role": "physical_midpoint_support_density_03",
        },
    ],
    "physical_assembly_deferred": True,
    "schema": "encounter_control_free_killing_factorization_flatten_contract_v1",
    "support_files_are_separate_by_profile": True,
    "support_flat_index_formula": "i_M",
    "support_logical_shape_each": ["n_M"],
    "tensor_storage_order": (
        "full:midpoint_outer_relative_parallel_middle_relative_perpendicular_inner"
    ),
}
FACTORIZATION_CONTRACT_SHA256: Final = hashlib.sha256(
    b"production-killing-factorization-flatten-contract-v1\0"
    + (
        json.dumps(_FACTORIZATION_CONTRACT, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    ).encode("ascii")
).hexdigest()

_SOURCE_TOP_KEYS: Final = {
    "configuration_bundle",
    "contact_geometry",
    "coordinate_order",
    "flags",
    "physical_dimension",
    "quotient_dimension",
    "schema",
    "status",
    "support_basis",
}
_SOURCE_CONFIGURATION_KEYS: Final = {
    "configuration_path",
    "configuration_sha256",
    "partition_bundle_path",
    "partition_bundle_sha256",
}
_SOURCE_CONTACT_KEYS: Final = {
    "cell_fraction_definition",
    "contact_set",
    "radius_binary64_hex",
    "radius_exact",
    "transverse_cut_locus_condition",
    "transverse_period_exact",
}
_SOURCE_SUPPORT_KEYS: Final = {
    "analytic_integral_each",
    "centres_binary64_hex",
    "centres_exact",
    "density_definition",
    "half_width_binary64_hex",
    "half_width_exact",
    "normalizer_definition",
    "profile_count",
    "shape_definition",
}
_SOURCE_FLAGS: Final = {
    "authorizes_scientific_execution": False,
    "concrete_killing_constructed": False,
    "contact_geometry_defined": True,
    "contains_budget_value": False,
    "contains_control_values": False,
    "continuum_verified": False,
    "f0_pass": False,
    "full_operator_bound": False,
    "positive_budget_executed": False,
    "production_resource_gate": False,
    "propagation_executed": False,
    "science_executed": False,
    "support_basis_defined": True,
    "topology_complete": False,
}
_SOURCE_STATUS: Final = (
    "FROZEN_CONTROL_FREE_CONTACT_AND_SUPPORT_BASIS_SOURCE_ONLY_"
    "NO_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
_SOURCE_PINS: Final = {
    "configuration": {
        "path": CONFIGURATION_RELATIVE_PATH.as_posix(),
        "sha256": ACCEPTED_CONFIGURATION_SHA256,
    },
    "f0_core": {
        "path": F0_SOURCE_RELATIVE_PATH.as_posix(),
        "sha256": ACCEPTED_F0_SOURCE_SHA256,
    },
    "killing_geometry_source": {
        "path": KILLING_SOURCE_RELATIVE_PATH.as_posix(),
        "sha256": ACCEPTED_KILLING_SOURCE_SHA256,
    },
    "partition_bundle_manifest": {
        "path": PARTITION_BUNDLE_RELATIVE_PATH.as_posix(),
        "sha256": ACCEPTED_PARTITION_BUNDLE_SHA256,
    },
    "production_initial_stream": {
        "path": INITIAL_STREAM_SOURCE_RELATIVE_PATH.as_posix(),
        "sha256": ACCEPTED_INITIAL_STREAM_SOURCE_SHA256,
    },
}
_BUNDLE_FLAGS: Final = {
    "authorizes_scientific_execution": False,
    "concrete_killing_constructed": False,
    "contact_fraction_geometry_producer_consistent_all_rows": True,
    "contains_budget_value": False,
    "contains_control_values": False,
    "continuum_verified": False,
    "f0_pass": False,
    "full_operator_bound": False,
    "independent_killing_geometry_replay_complete": False,
    "killing_geometry_bound": True,
    "positive_budget_executed": False,
    "production_resource_gate": False,
    "propagation_executed": False,
    "producer_consistent_control_free_killing_geometry_all_rows": True,
    "same_core_producer_consistency_only": True,
    "science_executed": False,
    "single_physical_operator_bound": False,
    "support_density_basis_producer_consistent_all_rows": True,
    "topology_complete": False,
}
_ROW_FLAGS: Final = {
    "authorizes_scientific_execution": False,
    "concrete_killing_constructed": False,
    "contact_fraction_geometry_producer_consistent": True,
    "contains_budget_value": False,
    "contains_control_values": False,
    "continuum_verified": False,
    "f0_pass": False,
    "full_operator_bound": False,
    "independent_killing_geometry_replay": False,
    "killing_geometry_bound": True,
    "positive_budget_executed": False,
    "producer_consistent_control_free_killing_geometry": True,
    "production_resource_gate": False,
    "propagation_executed": False,
    "same_core_producer_consistency_only": True,
    "science_executed": False,
    "single_physical_operator_bound": False,
    "support_density_basis_producer_consistent": True,
    "topology_complete": False,
}
_ROW_GATES: Final = {
    "analytic_disk_area_anchor_is_contained_and_quality_capped": True,
    "contact_area_enclosure_is_positive_and_domain_bounded": True,
    "contact_area_overlaps_direct_core_domain_enclosure": True,
    "contact_fraction_intervals_are_canonical_and_in_unit_range": True,
    "geometrically_full_contact_cells_are_exact_unit_intervals": True,
    "partition_bytes_match_same_core_exact_reconstruction": True,
    "support_density_intervals_are_canonical_and_nonnegative": True,
    "support_centres_are_strictly_distinct_and_pairwise_disjoint": True,
    "support_integral_enclosures_contain_analytic_unit_mass": True,
    "support_integral_widths_pass_predeclared_cap": True,
    "support_ranges_are_strictly_inside_midpoint_domain": True,
}
_METHOD: Final = {
    "contact_active_cell_count_definition": "saved_interval_upper_endpoint_strictly_positive",
    "contact_coordinate_order": list(CONTACT_COORDINATE_ORDER),
    "contact_fraction_record_format": ">dd",
    "contact_full_cell_count_definition": (
        "every_corner_of_every_exact_partition_segment_inside_or_on_contact_disk"
    ),
    "contact_full_cell_serialization": (
        "exact_[1,1]_after_exact_rational_corner_classification"
    ),
    "concrete_killing_materialized": False,
    "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
    "panels_per_unit": PANELS_PER_UNIT,
    "precision_bits": PRECISION_BITS,
    "same_core_numerical_primitives": [
        "build_contact_fraction_intervals_v2",
        "build_normalized_bump_profile",
    ],
    "same_mpfr_backend_anchor_is_independent": False,
    "support_density_record_format": ">dd",
}

_BUNDLE_KEYS: Final = {
    "configuration_count",
    "family_relation_sha256",
    "factorization_contract",
    "factorization_contract_sha256",
    "file_inventory",
    "flags",
    "method",
    "partition_reference_graph_sha256",
    "request_snapshots",
    "rows",
    "schema",
    "source_pins",
    "status",
    "totals",
}
_ROW_KEYS: Final = {
    "configuration_index",
    "configuration_label",
    "contact_fraction_relative",
    "expected_states",
    "factorization_contract_sha256",
    "flags",
    "gates",
    "partition_source",
    "row_relation_sha256",
    "schema",
    "shape",
    "source_pins",
    "status",
    "support_densities",
}
_ROW_SUMMARY_KEYS: Final = {
    "active_contact_cell_count",
    "configuration_index",
    "configuration_label",
    "contact_fraction_records",
    "expected_states",
    "full_contact_cell_count",
    "midpoint_cells",
    "row_manifest",
    "row_relation_sha256",
    "shape",
    "support_density_records",
    "support_profile_count",
}
_CONTACT_KEYS: Final = {
    "active_cell_count",
    "area_enclosure_exact",
    "file",
    "full_cell_count",
    "manifest",
    "quality_ledger",
    "relation_sha256",
}
_SUPPORT_KEYS: Final = {
    "centre_binary64_hex",
    "centre_exact",
    "file",
    "half_width_binary64_hex",
    "half_width_exact",
    "integral_enclosure_exact",
    "manifest",
    "profile_index",
    "quality_ledger",
    "relation_sha256",
}
_PARTITION_SOURCE_KEYS: Final = {
    "bundle_manifest_sha256",
    "bundle_row_manifest",
    "bundle_row_relation_sha256",
    "partitions",
}
_PARTITION_BINDING_KEYS: Final = {"axis_relation_sha256", "coordinate", "file"}
_RAW_MANIFEST_KEYS: Final = {
    "byte_order",
    "logical_shape",
    "raw_byte_length",
    "raw_sha256",
    "record_count",
    "record_format",
    "role",
    "schema",
}
_FILE_ENTRY_KEYS: Final = {"byte_length", "path", "sha256"}
_INITIAL_BUNDLE_KEYS: Final = {
    "analytic_source_sha256",
    "configuration_count",
    "configuration_sha256",
    "family_relation_sha256",
    "file_inventory",
    "flags",
    "method",
    "rows",
    "schema",
    "status",
    "total_dense_expansion_byte_length",
    "total_state_workload",
}
_INITIAL_ROW_KEYS: Final = {
    "axes",
    "configuration_index",
    "configuration_label",
    "configuration_sha256",
    "expected_states",
    "flags",
    "initial_marginals",
    "row_relation_sha256",
    "schema",
    "source_box_relation_sha256",
    "sparse_component_box",
    "status",
}
_INITIAL_AXIS_KEYS: Final = {
    "axis_relation_sha256",
    "coordinate",
    "partition_file",
    "rates",
}


class ProductionKillingGeometryFailure(RuntimeError):
    """Fail-closed error for this narrow same-core producer layer."""


@dataclass(frozen=True, slots=True)
class KillingGeometrySource:
    radius: Fraction
    transverse_period: Fraction
    support_centres: tuple[Fraction, Fraction, Fraction, Fraction]
    support_centres_hex: tuple[str, str, str, str]
    support_half_width: Fraction
    support_half_width_hex: str


@dataclass(frozen=True, slots=True)
class InputSnapshot:
    family: dict[str, object]
    family_bytes: bytes
    source: KillingGeometrySource
    source_payload: dict[str, object]
    source_bytes: bytes
    partition_manifest: dict[str, object]
    partition_bytes: bytes
    partition_inventory: dict[str, dict[str, object]]
    producer_sha256: str


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise ProductionKillingGeometryFailure("JSON has a duplicate or invalid key")
        result[key] = value
    return result


def _reject_json_float(token: str) -> object:
    raise ProductionKillingGeometryFailure(f"JSON floating literal is forbidden: {token}")


def _parse_strict_json(source: bytes, *, label: str) -> object:
    if type(source) is not bytes:
        raise ProductionKillingGeometryFailure(f"{label} does not have exact bytes type")
    try:
        return json.loads(
            source.decode("ascii"),
            object_pairs_hook=_strict_object,
            parse_float=_reject_json_float,
            parse_constant=_reject_json_float,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProductionKillingGeometryFailure(f"{label} is not strict ASCII JSON") from error


def _parse_canonical_json(source: bytes, *, label: str) -> object:
    payload = _parse_strict_json(source, label=label)
    if _canonical_json_bytes(payload) != source:
        raise ProductionKillingGeometryFailure(f"{label} is not canonical sorted indent-2 JSON")
    return payload


def _require_exact_keys(payload: object, expected: set[str], *, label: str) -> dict[str, object]:
    if type(payload) is not dict or set(payload) != expected:
        raise ProductionKillingGeometryFailure(f"{label} key set is invalid")
    return payload


def _require_sha256(value: object, *, label: str) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ProductionKillingGeometryFailure(f"{label} is not canonical SHA-256 text")
    return value


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_text(value: object, *, label: str) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise ProductionKillingGeometryFailure(f"{label} is not a canonical fraction")
    numerator_text, denominator_text = value.split("/")
    try:
        numerator = int(numerator_text)
        denominator = int(denominator_text)
    except ValueError as error:
        raise ProductionKillingGeometryFailure(f"{label} is not an integer fraction") from error
    if denominator <= 0:
        raise ProductionKillingGeometryFailure(f"{label} has a nonpositive denominator")
    result = Fraction(numerator, denominator)
    if _fraction_text(result) != value:
        raise ProductionKillingGeometryFailure(f"{label} is not reduced canonical text")
    return result


def _parse_hex_fraction(value: object, *, label: str) -> Fraction:
    if type(value) is not str:
        raise ProductionKillingGeometryFailure(f"{label} is not binary64 hex text")
    try:
        parsed = float.fromhex(value)
    except ValueError as error:
        raise ProductionKillingGeometryFailure(f"{label} is not valid binary64 hex") from error
    if not math.isfinite(parsed) or parsed.hex() != value:
        raise ProductionKillingGeometryFailure(f"{label} is not canonical finite binary64")
    if parsed == 0.0 and math.copysign(1.0, parsed) < 0:
        raise ProductionKillingGeometryFailure(f"{label} is negative zero")
    return Fraction.from_float(parsed)


def _domain_digest(domain: bytes, payload: object) -> str:
    if not domain.endswith(b"\0"):
        raise ProductionKillingGeometryFailure("digest domain is not NUL terminated")
    return _sha256_bytes(domain + _canonical_json_bytes(payload))


def _read_regular_bytes(path: Path, *, maximum_bytes: int) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ProductionKillingGeometryFailure(f"required file is unavailable: {path}") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum_bytes:
            raise ProductionKillingGeometryFailure(f"required file is unsafe or oversized: {path}")
        chunks: list[bytes] = []
        observed = 0
        while block := os.read(descriptor, min(1 << 20, maximum_bytes + 1 - observed)):
            chunks.append(block)
            observed += len(block)
            if observed > maximum_bytes:
                raise ProductionKillingGeometryFailure(f"required file is oversized: {path}")
        after = os.fstat(descriptor)
        before_identity = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        after_identity = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if before_identity != after_identity or observed != before.st_size:
            raise ProductionKillingGeometryFailure(f"required file changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _file_entry(path: str, payload: bytes) -> dict[str, object]:
    return {"byte_length": len(payload), "path": path, "sha256": _sha256_bytes(payload)}


def _validate_file_entry(entry: object, *, label: str) -> dict[str, object]:
    result = _require_exact_keys(entry, _FILE_ENTRY_KEYS, label=label)
    relative = result["path"]
    if type(relative) is not str:
        raise ProductionKillingGeometryFailure(f"{label} path type is invalid")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or pure.as_posix() != relative:
        raise ProductionKillingGeometryFailure(f"{label} path is unsafe")
    if type(result["byte_length"]) is not int or result["byte_length"] < 0:
        raise ProductionKillingGeometryFailure(f"{label} byte length is invalid")
    _require_sha256(result["sha256"], label=f"{label} SHA-256")
    return result


def _verify_runtime_source_pins(report_root: Path) -> str:
    expected = (
        (F0_SOURCE_RELATIVE_PATH, ACCEPTED_F0_SOURCE_SHA256, Path(f0.__file__).resolve()),
        (
            INITIAL_STREAM_SOURCE_RELATIVE_PATH,
            ACCEPTED_INITIAL_STREAM_SOURCE_SHA256,
            Path(initial_stream.__file__).resolve(),
        ),
    )
    for relative, digest, imported in expected:
        lexical = report_root / relative
        if imported != lexical.resolve():
            raise ProductionKillingGeometryFailure(
                f"imported implementation path drifted: {relative}"
            )
        observed = _sha256_bytes(_read_regular_bytes(lexical, maximum_bytes=2_000_000))
        if not hmac.compare_digest(observed, digest):
            raise ProductionKillingGeometryFailure(
                f"accepted implementation bytes changed: {relative}"
            )
    producer_path = report_root / PRODUCER_SOURCE_RELATIVE_PATH
    if Path(__file__).resolve() != producer_path.resolve():
        raise ProductionKillingGeometryFailure("imported producer implementation path drifted")
    return _sha256_bytes(_read_regular_bytes(producer_path, maximum_bytes=2_000_000))


def _validate_source(payload: object) -> KillingGeometrySource:
    source = _require_exact_keys(payload, _SOURCE_TOP_KEYS, label="killing geometry source")
    configuration = _require_exact_keys(
        source["configuration_bundle"],
        _SOURCE_CONFIGURATION_KEYS,
        label="source configuration bundle",
    )
    contact = _require_exact_keys(
        source["contact_geometry"], _SOURCE_CONTACT_KEYS, label="source contact geometry"
    )
    support = _require_exact_keys(
        source["support_basis"], _SOURCE_SUPPORT_KEYS, label="source support basis"
    )
    if (
        source["schema"] != SOURCE_SCHEMA
        or source["status"] != _SOURCE_STATUS
        or source["physical_dimension"] != 2
        or source["quotient_dimension"] != 3
        or source["coordinate_order"] != ["midpoint", "relative_parallel", "relative_perpendicular"]
        or source["flags"] != _SOURCE_FLAGS
        or configuration
        != {
            "configuration_path": CONFIGURATION_RELATIVE_PATH.as_posix(),
            "configuration_sha256": ACCEPTED_CONFIGURATION_SHA256,
            "partition_bundle_path": PARTITION_BUNDLE_RELATIVE_PATH.as_posix(),
            "partition_bundle_sha256": ACCEPTED_PARTITION_BUNDLE_SHA256,
        }
    ):
        raise ProductionKillingGeometryFailure("killing geometry source boundary drifted")
    if (
        contact["cell_fraction_definition"]
        != (
            "physical_area_of_contact_disk_intersection_with_relative_cell_divided_by_"
            "exact_relative_cell_volume"
        )
        or contact["contact_set"]
        != (
            "r_parallel_squared_plus_minimum_image_r_perpendicular_squared_less_than_or_"
            "equal_to_radius_squared"
        )
        or contact["transverse_cut_locus_condition"] != "2*radius<transverse_period"
        or contact["transverse_period_exact"] != "1/1"
    ):
        raise ProductionKillingGeometryFailure("contact source definitions drifted")
    radius_hex = _parse_hex_fraction(contact["radius_binary64_hex"], label="contact radius")
    radius_exact = _parse_fraction_text(contact["radius_exact"], label="exact contact radius")
    period = _parse_fraction_text(contact["transverse_period_exact"], label="transverse period")
    if radius_hex != radius_exact or radius_exact <= 0 or 2 * radius_exact >= period:
        raise ProductionKillingGeometryFailure("contact source exact/hex relation drifted")
    if (
        support["analytic_integral_each"] != "1/1"
        or support["density_definition"] != "phi_j(M)=b((M-centre_j)/half_width)/(half_width*I_b)"
        or support["normalizer_definition"] != "I_b=integral_from_minus_one_to_one_b(u)_du"
        or support["profile_count"] != 4
        or support["shape_definition"] != "b(u)=indicator(abs(u)<1)*exp(-1/(1-u^2))"
    ):
        raise ProductionKillingGeometryFailure("support source definitions drifted")
    centres_hex_payload = support["centres_binary64_hex"]
    centres_exact_payload = support["centres_exact"]
    if (
        type(centres_hex_payload) is not list
        or type(centres_exact_payload) is not list
        or len(centres_hex_payload) != 4
        or len(centres_exact_payload) != 4
    ):
        raise ProductionKillingGeometryFailure("support centre list shape drifted")
    centres_hex = tuple(centres_hex_payload)
    if any(type(value) is not str for value in centres_hex):
        raise ProductionKillingGeometryFailure("support centre hex type drifted")
    centres = tuple(
        _parse_hex_fraction(value, label=f"support centre {index}")
        for index, value in enumerate(centres_hex)
    )
    exact_centres = tuple(
        _parse_fraction_text(value, label=f"exact support centre {index}")
        for index, value in enumerate(centres_exact_payload)
    )
    width_hex_text = support["half_width_binary64_hex"]
    width = _parse_hex_fraction(width_hex_text, label="support half width")
    exact_width = _parse_fraction_text(support["half_width_exact"], label="exact support width")
    if (
        centres != exact_centres
        or tuple(sorted(centres)) != centres
        or len(set(centres)) != 4
        or width != exact_width
    ):
        raise ProductionKillingGeometryFailure("support source exact/hex relation drifted")
    if (
        width <= 0
        or any(centre - width >= centre + width for centre in centres)
        or any(left + width >= right - width for left, right in zip(centres, centres[1:]))
    ):
        raise ProductionKillingGeometryFailure("support source geometry is invalid")
    contract_centres = tuple(
        _parse_fraction_text(entry["centre_exact"], label=f"factorization profile centre {index}")
        for index, entry in enumerate(_FACTORIZATION_CONTRACT["ordered_profile_mapping"])
    )
    if centres != contract_centres:
        raise ProductionKillingGeometryFailure(
            "support centres drifted from ordered factorization contract"
        )
    return KillingGeometrySource(
        radius=radius_exact,
        transverse_period=period,
        support_centres=centres,  # type: ignore[arg-type]
        support_centres_hex=centres_hex,  # type: ignore[arg-type]
        support_half_width=width,
        support_half_width_hex=width_hex_text,
    )


def _generic_inventory_map(
    manifest: dict[str, object], *, expected_count: int | None
) -> dict[str, dict[str, object]]:
    entries = manifest.get("file_inventory")
    if type(entries) is not list or (expected_count is not None and len(entries) != expected_count):
        raise ProductionKillingGeometryFailure("file inventory count is invalid")
    result: dict[str, dict[str, object]] = {}
    for item in entries:
        current = _validate_file_entry(item, label="inventory entry")
        relative = current["path"]
        if relative in result:
            raise ProductionKillingGeometryFailure("file inventory path is duplicate")
        result[relative] = current
    if list(result) != sorted(result):
        raise ProductionKillingGeometryFailure("file inventory is not sorted")
    return result


def _load_input_snapshot(report_root: Path) -> InputSnapshot:
    report_root = report_root.resolve()
    producer_sha256 = _verify_runtime_source_pins(report_root)
    family, family_bytes = initial_stream.load_configuration_family(report_root)
    if not hmac.compare_digest(_sha256_bytes(family_bytes), ACCEPTED_CONFIGURATION_SHA256):
        raise ProductionKillingGeometryFailure("configuration bytes changed")
    source_bytes = _read_regular_bytes(
        report_root / KILLING_SOURCE_RELATIVE_PATH, maximum_bytes=100_000
    )
    if not hmac.compare_digest(_sha256_bytes(source_bytes), ACCEPTED_KILLING_SOURCE_SHA256):
        raise ProductionKillingGeometryFailure("killing geometry source bytes changed")
    source_payload = _parse_canonical_json(source_bytes, label="killing geometry source")
    source = _validate_source(source_payload)
    partition_bytes = _read_regular_bytes(
        report_root / PARTITION_BUNDLE_RELATIVE_PATH, maximum_bytes=2_000_000
    )
    if not hmac.compare_digest(_sha256_bytes(partition_bytes), ACCEPTED_PARTITION_BUNDLE_SHA256):
        raise ProductionKillingGeometryFailure("partition bundle manifest bytes changed")
    partition_manifest = _require_exact_keys(
        _parse_canonical_json(partition_bytes, label="partition bundle manifest"),
        _INITIAL_BUNDLE_KEYS,
        label="partition bundle manifest",
    )
    if (
        partition_manifest["schema"] != initial_stream.SCHEMA
        or partition_manifest["status"] != initial_stream.STATUS
        or partition_manifest["configuration_sha256"] != ACCEPTED_CONFIGURATION_SHA256
        or partition_manifest["configuration_count"] != 12
        or partition_manifest["total_state_workload"] != 34_787_462
        or partition_manifest["flags"] != initial_stream._BUNDLE_FLAGS
    ):
        raise ProductionKillingGeometryFailure("partition bundle boundary metadata drifted")
    partition_inventory = _generic_inventory_map(partition_manifest, expected_count=206)
    return InputSnapshot(
        family=family,
        family_bytes=family_bytes,
        source=source,
        source_payload=source_payload,
        source_bytes=source_bytes,
        partition_manifest=partition_manifest,
        partition_bytes=partition_bytes,
        partition_inventory=partition_inventory,
        producer_sha256=producer_sha256,
    )


def _read_external_inventory_file(
    report_root: Path,
    inventory: dict[str, dict[str, object]],
    entry: object,
    *,
    maximum_bytes: int,
) -> bytes:
    current = _validate_file_entry(entry, label="external inventory reference")
    relative = current["path"]
    if inventory.get(relative) != current:
        raise ProductionKillingGeometryFailure("external file is not bound to pinned inventory")
    source = _read_regular_bytes(
        report_root / PARTITION_BUNDLE_DIRECTORY_RELATIVE_PATH / Path(relative),
        maximum_bytes=maximum_bytes,
    )
    if len(source) != current["byte_length"] or not hmac.compare_digest(
        _sha256_bytes(source), current["sha256"]
    ):
        raise ProductionKillingGeometryFailure("external inventory file bytes changed")
    return source


def _partition_source_for_row(
    report_root: Path,
    snapshot: InputSnapshot,
    *,
    row_index: int,
    row: dict[str, object],
    axes: tuple[f0.TensorAxis, f0.TensorAxis, f0.TensorAxis],
) -> dict[str, object]:
    summaries = snapshot.partition_manifest["rows"]
    if type(summaries) is not list or len(summaries) != 12:
        raise ProductionKillingGeometryFailure("partition bundle row list is invalid")
    summary = _require_exact_keys(
        summaries[row_index], initial_stream._ROW_SUMMARY_KEYS, label="partition row summary"
    )
    if (
        summary["configuration_index"] != row_index
        or summary["configuration_label"] != row["label"]
        or summary["expected_states"] != row["expected_states"]
    ):
        raise ProductionKillingGeometryFailure("partition row summary drifted")
    row_file = _validate_file_entry(summary["row_manifest"], label="partition row manifest")
    row_bytes = _read_external_inventory_file(
        report_root,
        snapshot.partition_inventory,
        row_file,
        maximum_bytes=2_000_000,
    )
    row_manifest = _require_exact_keys(
        _parse_canonical_json(row_bytes, label="partition row manifest"),
        _INITIAL_ROW_KEYS,
        label="partition row manifest",
    )
    row_axes = row_manifest["axes"]
    if (
        row_manifest["schema"] != initial_stream.ROW_SCHEMA
        or row_manifest["configuration_index"] != row_index
        or row_manifest["configuration_label"] != row["label"]
        or row_manifest["configuration_sha256"] != ACCEPTED_CONFIGURATION_SHA256
        or row_manifest["expected_states"] != row["expected_states"]
        or row_manifest["row_relation_sha256"] != summary["row_relation_sha256"]
        or type(row_axes) is not list
        or len(row_axes) != 3
    ):
        raise ProductionKillingGeometryFailure("partition row manifest binding drifted")
    bindings: list[dict[str, object]] = []
    for axis_entry, expected_axis in zip(row_axes, axes, strict=True):
        axis_entry = _require_exact_keys(
            axis_entry, _INITIAL_AXIS_KEYS, label="partition axis entry"
        )
        if axis_entry["coordinate"] != expected_axis.name:
            raise ProductionKillingGeometryFailure("partition coordinate order drifted")
        partition_file = _validate_file_entry(axis_entry["partition_file"], label="partition file")
        partition_bytes = _read_external_inventory_file(
            report_root,
            snapshot.partition_inventory,
            partition_file,
            maximum_bytes=2_000_000,
        )
        expected_partition_bytes = _canonical_json_bytes(
            initial_stream._partition_payload(expected_axis)
        )
        if partition_bytes != expected_partition_bytes:
            raise ProductionKillingGeometryFailure(
                "partition bytes differ from same-core exact reconstruction"
            )
        _require_sha256(axis_entry["axis_relation_sha256"], label="partition axis relation SHA-256")
        bindings.append(
            {
                "axis_relation_sha256": axis_entry["axis_relation_sha256"],
                "coordinate": expected_axis.name,
                "file": partition_file,
            }
        )
    return {
        "bundle_manifest_sha256": ACCEPTED_PARTITION_BUNDLE_SHA256,
        "bundle_row_manifest": row_file,
        "bundle_row_relation_sha256": summary["row_relation_sha256"],
        "partitions": bindings,
    }


def _validate_interval(interval: f0.OutwardInterval, *, label: str) -> None:
    if type(interval) is not f0.OutwardInterval:
        raise ProductionKillingGeometryFailure(f"{label} has wrong interval type")
    interval.require_nonnegative(label)
    for endpoint in (interval.lower, interval.upper):
        if not math.isfinite(endpoint):
            raise ProductionKillingGeometryFailure(f"{label} has a nonfinite endpoint")
        if endpoint == 0.0 and math.copysign(1.0, endpoint) < 0:
            raise ProductionKillingGeometryFailure(f"{label} has a signed-zero endpoint")


def _interval_raw_bytes(intervals: Sequence[f0.OutwardInterval], *, label: str) -> bytes:
    raw = bytearray(16 * len(intervals))
    for index, interval in enumerate(intervals):
        _validate_interval(interval, label=f"{label}[{index}]")
        struct.pack_into(">dd", raw, 16 * index, interval.lower, interval.upper)
    return bytes(raw)


def _raw_manifest(raw: bytes, *, role: str, shape: Sequence[int]) -> dict[str, object]:
    logical_shape = list(shape)
    return {
        "byte_order": "big",
        "logical_shape": logical_shape,
        "raw_byte_length": len(raw),
        "raw_sha256": _sha256_bytes(raw),
        "record_count": math.prod(logical_shape),
        "record_format": ">dd",
        "role": role,
        "schema": RAW_SCHEMA,
    }


def _parse_interval_raw(
    raw: bytes,
    manifest: object,
    *,
    expected_role: str,
    expected_shape: Sequence[int],
) -> tuple[f0.OutwardInterval, ...]:
    current = _require_exact_keys(manifest, _RAW_MANIFEST_KEYS, label="raw manifest")
    shape = list(expected_shape)
    if (
        current["schema"] != RAW_SCHEMA
        or current["byte_order"] != "big"
        or current["record_format"] != ">dd"
        or current["role"] != expected_role
        or current["logical_shape"] != shape
        or current["record_count"] != math.prod(shape)
        or current["raw_byte_length"] != len(raw)
        or current["raw_sha256"] != _sha256_bytes(raw)
        or len(raw) != 16 * math.prod(shape)
    ):
        raise ProductionKillingGeometryFailure("raw interval manifest is invalid")
    intervals: list[f0.OutwardInterval] = []
    for offset in range(0, len(raw), 16):
        lower, upper = struct.unpack_from(">dd", raw, offset)
        try:
            interval = f0.OutwardInterval(lower, upper)
            _validate_interval(interval, label="file-backed interval")
        except f0.F0VerificationFailure as error:
            raise ProductionKillingGeometryFailure(
                "file-backed interval is not a valid finite nonnegative interval"
            ) from error
        intervals.append(interval)
    return tuple(intervals)


def _weighted_enclosure(
    intervals: Sequence[f0.OutwardInterval], volumes: Sequence[Fraction]
) -> tuple[Fraction, Fraction]:
    if len(intervals) != len(volumes) or not intervals:
        raise ProductionKillingGeometryFailure("weighted enclosure shape is invalid")
    lower = sum(
        (
            interval.lower_fraction * volume
            for interval, volume in zip(intervals, volumes, strict=True)
        ),
        Fraction(0),
    )
    upper = sum(
        (
            interval.upper_fraction * volume
            for interval, volume in zip(intervals, volumes, strict=True)
        ),
        Fraction(0),
    )
    if lower < 0 or lower > upper:
        raise ProductionKillingGeometryFailure("weighted enclosure is invalid")
    return lower, upper


def _contact_cell_counts(
    intervals: Sequence[f0.OutwardInterval],
    relative_parallel: f0.TensorAxis,
    relative_perpendicular: f0.TensorAxis,
    radius: Fraction,
) -> tuple[int, int]:
    """Return positive-intersection and exact whole-cell contact counts."""

    full_mask = _contact_full_cell_mask(
        relative_parallel,
        relative_perpendicular,
        radius,
    )
    if len(intervals) != len(full_mask):
        raise ProductionKillingGeometryFailure("contact count shape is invalid")
    active = sum(interval.upper > 0.0 for interval in intervals)
    full = 0
    for interval, geometrically_full in zip(intervals, full_mask, strict=True):
        if geometrically_full:
            if interval.lower != 1.0 or interval.upper != 1.0:
                raise ProductionKillingGeometryFailure(
                    "geometrically full contact cell is not the exact unit interval"
                )
            full += 1
        elif interval.lower == 1.0:
            raise ProductionKillingGeometryFailure(
                "non-full contact cell has an inadmissible unit lower endpoint"
            )
    if not 0 < full < active < len(intervals):
        raise ProductionKillingGeometryFailure("contact active/full-cell counts are invalid")
    return active, full


def _contact_full_cell_mask(
    relative_parallel: f0.TensorAxis,
    relative_perpendicular: f0.TensorAxis,
    radius: Fraction,
) -> tuple[bool, ...]:
    """Classify exact full cells from rational partition segments.

    The squared Euclidean norm is convex on each axis-aligned rectangle, so a
    rectangle lies in the closed disk exactly when all four corners do.  A
    periodic wrap cell is full only when every exact segment-pair rectangle is
    full.  Segment-volume closure is checked before the classification is used
    to replace a numerical enclosure by the mathematical singleton ``[1,1]``.
    """

    relative_parallel.validate()
    relative_perpendicular.validate()
    radius_squared = radius * radius
    full: list[bool] = []
    for parallel_segments, parallel_volume in zip(
        relative_parallel.cell_segments,
        relative_parallel.cell_volumes,
        strict=True,
    ):
        if sum((x1 - x0 for x0, x1 in parallel_segments), Fraction(0)) != parallel_volume:
            raise ProductionKillingGeometryFailure("parallel segment-volume closure failed")
        for transverse_segments, transverse_volume in zip(
            relative_perpendicular.cell_segments,
            relative_perpendicular.cell_volumes,
            strict=True,
        ):
            if (
                sum((y1 - y0 for y0, y1 in transverse_segments), Fraction(0))
                != transverse_volume
            ):
                raise ProductionKillingGeometryFailure(
                    "transverse segment-volume closure failed"
                )
            full.append(
                all(
                    max(
                        x0 * x0 + y0 * y0,
                        x0 * x0 + y1 * y1,
                        x1 * x1 + y0 * y0,
                        x1 * x1 + y1 * y1,
                    )
                    <= radius_squared
                    for x0, x1 in parallel_segments
                    for y0, y1 in transverse_segments
                )
            )
    return tuple(full)


def _canonicalize_full_contact_intervals(
    intervals: Sequence[f0.OutwardInterval],
    relative_parallel: f0.TensorAxis,
    relative_perpendicular: f0.TensorAxis,
    radius: Fraction,
) -> tuple[f0.OutwardInterval, ...]:
    """Replace rigorously full contact cells by the exact singleton ``[1,1]``."""

    full_mask = _contact_full_cell_mask(
        relative_parallel,
        relative_perpendicular,
        radius,
    )
    if len(intervals) != len(full_mask):
        raise ProductionKillingGeometryFailure("contact canonicalization shape is invalid")
    canonical: list[f0.OutwardInterval] = []
    for interval, geometrically_full in zip(intervals, full_mask, strict=True):
        if geometrically_full:
            if not interval.lower <= 1.0 <= interval.upper:
                raise ProductionKillingGeometryFailure(
                    "numerical contact enclosure excludes an exact full-cell value"
                )
            canonical.append(f0.OutwardInterval(1.0, 1.0))
        else:
            canonical.append(interval)
    return tuple(canonical)


def _directed_analytic_disk_area(radius: Fraction) -> f0.OutwardInterval:
    """Enclose pi*r^2 with separately directed MPFR operations.

    This is a second calculation path, but it deliberately uses the same
    gmpy2/MPFR backend as the accepted producer core and is not independent
    numerical evidence.
    """

    gmpy2 = f0.gmpy2
    radius_lower = f0._mpfr_from_fraction(radius, ANALYTIC_AREA_PRECISION_BITS, gmpy2.RoundDown)
    radius_upper = f0._mpfr_from_fraction(radius, ANALYTIC_AREA_PRECISION_BITS, gmpy2.RoundUp)
    with gmpy2.context(
        gmpy2.get_context(),
        precision=ANALYTIC_AREA_PRECISION_BITS,
        round=gmpy2.RoundDown,
    ):
        lower = gmpy2.const_pi() * radius_lower * radius_lower
    with gmpy2.context(
        gmpy2.get_context(),
        precision=ANALYTIC_AREA_PRECISION_BITS,
        round=gmpy2.RoundUp,
    ):
        upper = gmpy2.const_pi() * radius_upper * radius_upper
    return f0.OutwardInterval(
        f0.reference._mpfr_to_float_lower(lower),
        f0.reference._mpfr_to_float_upper(upper),
    )


def _contact_quality_ledger(
    aggregate: tuple[Fraction, Fraction],
    *,
    radius: Fraction,
) -> dict[str, object]:
    analytic = _directed_analytic_disk_area(radius)
    analytic_bounds = (analytic.lower_fraction, analytic.upper_fraction)
    aggregate_width = aggregate[1] - aggregate[0]
    analytic_width = analytic_bounds[1] - analytic_bounds[0]
    radius_squared = radius * radius
    aggregate_ratio = aggregate_width / radius_squared
    analytic_ratio = analytic_width / radius_squared
    if (
        not aggregate[0] <= analytic_bounds[0] <= analytic_bounds[1] <= aggregate[1]
        or aggregate_ratio > CONTACT_AREA_WIDTH_OVER_RADIUS_SQUARED_CAP
        or analytic_ratio > ANALYTIC_AREA_WIDTH_OVER_RADIUS_SQUARED_CAP
    ):
        raise ProductionKillingGeometryFailure("analytic disk-area containment/quality gate failed")
    return {
        "aggregate_contains_analytic_enclosure": True,
        "aggregate_width_exact": _fraction_text(aggregate_width),
        "aggregate_width_over_radius_squared_cap_exact": _fraction_text(
            CONTACT_AREA_WIDTH_OVER_RADIUS_SQUARED_CAP
        ),
        "aggregate_width_over_radius_squared_exact": _fraction_text(aggregate_ratio),
        "analytic_area_enclosure_exact": _enclosure_payload(analytic_bounds),
        "analytic_area_precision_bits": ANALYTIC_AREA_PRECISION_BITS,
        "analytic_width_exact": _fraction_text(analytic_width),
        "analytic_width_over_radius_squared_cap_exact": _fraction_text(
            ANALYTIC_AREA_WIDTH_OVER_RADIUS_SQUARED_CAP
        ),
        "analytic_width_over_radius_squared_exact": _fraction_text(analytic_ratio),
        "backend": "gmpy2_mpfr_same_backend_as_producer_core",
        "independent_backend": False,
        "separately_directed_formula": "pi*radius_exact^2",
    }


def _support_quality_ledger(
    integral: tuple[Fraction, Fraction],
    *,
    centre: Fraction,
    half_width: Fraction,
    midpoint: f0.TensorAxis,
) -> dict[str, object]:
    support_lower = centre - half_width
    support_upper = centre + half_width
    integral_width = integral[1] - integral[0]
    if (
        not midpoint.domain_start
        < support_lower
        < support_upper
        < midpoint.domain_start + midpoint.domain_width
        or integral_width > SUPPORT_INTEGRAL_WIDTH_CAP
    ):
        raise ProductionKillingGeometryFailure("support range/mass-width quality gate failed")
    return {
        "analytic_mass_exact": "1/1",
        "integral_width_cap_exact": _fraction_text(SUPPORT_INTEGRAL_WIDTH_CAP),
        "integral_width_exact": _fraction_text(integral_width),
        "midpoint_domain_lower_exact": _fraction_text(midpoint.domain_start),
        "midpoint_domain_upper_exact": _fraction_text(
            midpoint.domain_start + midpoint.domain_width
        ),
        "support_lower_exact": _fraction_text(support_lower),
        "support_strictly_inside_midpoint_domain": True,
        "support_upper_exact": _fraction_text(support_upper),
    }


def _enclosure_payload(bounds: tuple[Fraction, Fraction]) -> dict[str, str]:
    return {"lower_exact": _fraction_text(bounds[0]), "upper_exact": _fraction_text(bounds[1])}


def _parse_enclosure(payload: object, *, label: str) -> tuple[Fraction, Fraction]:
    current = _require_exact_keys(payload, {"lower_exact", "upper_exact"}, label=label)
    lower = _parse_fraction_text(current["lower_exact"], label=f"{label} lower")
    upper = _parse_fraction_text(current["upper_exact"], label=f"{label} upper")
    if lower < 0 or lower > upper:
        raise ProductionKillingGeometryFailure(f"{label} range is invalid")
    return lower, upper


def _safe_slug(label: str) -> str:
    translated = label.lower().replace("+", "_plus").replace("/", "_")
    slug = "".join(character if character.isalnum() else "_" for character in translated)
    return "_".join(part for part in slug.split("_") if part)


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        target.write(payload)


def _source_pins_copy(producer_sha256: str) -> dict[str, dict[str, str]]:
    _require_sha256(producer_sha256, label="producer source SHA-256")
    pins = {role: dict(pin) for role, pin in _SOURCE_PINS.items()}
    pins["producer"] = {
        "path": PRODUCER_SOURCE_RELATIVE_PATH.as_posix(),
        "sha256": producer_sha256,
    }
    return pins


def _contact_relation_payload(
    *,
    active_cell_count: int,
    full_cell_count: int,
    row_index: int,
    row_label: str,
    shape: tuple[int, int],
    raw_sha256: str,
    area_enclosure: dict[str, str],
    partition_source: dict[str, object],
    producer_sha256: str,
    quality_ledger: dict[str, object],
    source: KillingGeometrySource,
) -> dict[str, object]:
    partition_hashes = {
        entry["coordinate"]: entry["file"]["sha256"]
        for entry in partition_source["partitions"]
        if entry["coordinate"] in CONTACT_COORDINATE_ORDER
    }
    axis_relation_hashes = {
        entry["coordinate"]: entry["axis_relation_sha256"]
        for entry in partition_source["partitions"]
        if entry["coordinate"] in CONTACT_COORDINATE_ORDER
    }
    return {
        "active_cell_count": active_cell_count,
        "area_enclosure_exact": area_enclosure,
        "axis_relation_sha256s": axis_relation_hashes,
        "configuration_index": row_index,
        "configuration_label": row_label,
        "contact_coordinate_order": list(CONTACT_COORDINATE_ORDER),
        "contact_raw_sha256": raw_sha256,
        "full_cell_count": full_cell_count,
        "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
        "killing_geometry_source_sha256": ACCEPTED_KILLING_SOURCE_SHA256,
        "logical_shape": list(shape),
        "partition_sha256s": partition_hashes,
        "producer_source_sha256": producer_sha256,
        "quality_ledger": quality_ledger,
        "radius_exact": _fraction_text(source.radius),
    }


def _support_relation_payload(
    *,
    row_index: int,
    row_label: str,
    profile_index: int,
    centre: Fraction,
    shape: tuple[int],
    raw_sha256: str,
    integral_enclosure: dict[str, str],
    partition_source: dict[str, object],
    producer_sha256: str,
    quality_ledger: dict[str, object],
    source: KillingGeometrySource,
) -> dict[str, object]:
    midpoint_partition = next(
        entry["file"]["sha256"]
        for entry in partition_source["partitions"]
        if entry["coordinate"] == "midpoint"
    )
    midpoint_axis_relation = next(
        entry["axis_relation_sha256"]
        for entry in partition_source["partitions"]
        if entry["coordinate"] == "midpoint"
    )
    return {
        "configuration_index": row_index,
        "configuration_label": row_label,
        "centre_exact": _fraction_text(centre),
        "half_width_exact": _fraction_text(source.support_half_width),
        "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
        "integral_enclosure_exact": integral_enclosure,
        "killing_geometry_source_sha256": ACCEPTED_KILLING_SOURCE_SHA256,
        "logical_shape": list(shape),
        "midpoint_axis_relation_sha256": midpoint_axis_relation,
        "midpoint_partition_sha256": midpoint_partition,
        "profile_index": profile_index,
        "producer_source_sha256": producer_sha256,
        "quality_ledger": quality_ledger,
        "support_density_raw_sha256": raw_sha256,
    }


def _row_relation_payload(
    *,
    row_index: int,
    row_label: str,
    shape: tuple[int, int, int],
    contact_relation_sha256: str,
    support_relation_sha256s: Sequence[str],
    partition_source: dict[str, object],
    producer_sha256: str,
) -> dict[str, object]:
    return {
        "configuration_index": row_index,
        "configuration_label": row_label,
        "contact_relation_sha256": contact_relation_sha256,
        "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
        "partition_bundle_row_relation_sha256": partition_source["bundle_row_relation_sha256"],
        "shape": list(shape),
        "source_pins": _source_pins_copy(producer_sha256),
        "support_relation_sha256s": list(support_relation_sha256s),
    }


def _build_row_geometry(
    root: Path,
    report_root: Path,
    snapshot: InputSnapshot,
    *,
    row_index: int,
    row: dict[str, object],
) -> tuple[dict[str, object], list[dict[str, object]], dict[str, object]]:
    shape = tuple(row["shape"])
    if len(shape) != 3 or any(type(value) is not int for value in shape):
        raise ProductionKillingGeometryFailure("configuration row shape is invalid")
    axes = initial_stream._build_control_free_axes(row, snapshot.family["dynamics"])
    if tuple(axis.size for axis in axes) != shape:
        raise ProductionKillingGeometryFailure("same-core axis shape drifted")
    partition_source = _partition_source_for_row(
        report_root, snapshot, row_index=row_index, row=row, axes=axes
    )
    midpoint, relative_parallel, relative_perpendicular = axes
    contact = f0.build_contact_fraction_intervals_v2(
        relative_parallel,
        relative_perpendicular,
        radius=snapshot.source.radius,
        precision_bits=PRECISION_BITS,
    )
    contact = _canonicalize_full_contact_intervals(
        contact,
        relative_parallel,
        relative_perpendicular,
        snapshot.source.radius,
    )
    supports = tuple(
        f0.build_normalized_bump_profile(
            midpoint,
            centre=centre,
            half_width=snapshot.source.support_half_width,
            panels_per_unit=PANELS_PER_UNIT,
            precision_bits=PRECISION_BITS,
        )
        for centre in snapshot.source.support_centres
    )
    if len(contact) != shape[1] * shape[2] or any(
        len(profile.density_intervals) != shape[0] or profile.analytic_total_mass != 1
        for profile in supports
    ):
        raise ProductionKillingGeometryFailure("same-core geometry output shape drifted")
    if any(interval.upper > 1.0 for interval in contact):
        raise ProductionKillingGeometryFailure("contact fraction escaped [0,1]")
    contact_volumes = tuple(
        parallel_volume * transverse_volume
        for parallel_volume in relative_parallel.cell_volumes
        for transverse_volume in relative_perpendicular.cell_volumes
    )
    contact_area = _weighted_enclosure(contact, contact_volumes)
    domain_area = relative_parallel.domain_width * relative_perpendicular.domain_width
    direct_area = f0.disk_rectangle_area_interval(
        relative_parallel.domain_start,
        relative_parallel.domain_start + relative_parallel.domain_width,
        relative_perpendicular.domain_start,
        relative_perpendicular.domain_start + relative_perpendicular.domain_width,
        snapshot.source.radius,
        precision_bits=PRECISION_BITS,
    )
    if (
        contact_area[0] <= 0
        or contact_area[1] > domain_area
        or max(contact_area[0], direct_area.lower_fraction)
        > min(contact_area[1], direct_area.upper_fraction)
    ):
        raise ProductionKillingGeometryFailure("aggregate contact-area gates failed")
    contact_quality = _contact_quality_ledger(
        contact_area,
        radius=snapshot.source.radius,
    )
    support_integrals = tuple(
        _weighted_enclosure(profile.density_intervals, midpoint.cell_volumes)
        for profile in supports
    )
    if any(not lower <= 1 <= upper for lower, upper in support_integrals):
        raise ProductionKillingGeometryFailure("support integral misses analytic unit mass")
    support_qualities = tuple(
        _support_quality_ledger(
            integral,
            centre=centre,
            half_width=snapshot.source.support_half_width,
            midpoint=midpoint,
        )
        for integral, centre in zip(support_integrals, snapshot.source.support_centres, strict=True)
    )

    row_directory = Path("rows") / f"{row_index:02d}_{_safe_slug(row['label'])}"
    files: list[dict[str, object]] = []

    def emit(relative: Path, payload: bytes) -> dict[str, object]:
        full_relative = row_directory / relative
        _write_bytes(root / full_relative, payload)
        entry = _file_entry(full_relative.as_posix(), payload)
        files.append(entry)
        return entry

    contact_raw = _interval_raw_bytes(contact, label="contact fraction")
    contact_file = emit(Path("contact_fraction_relative.be64"), contact_raw)
    active_contact_cells, full_contact_cells = _contact_cell_counts(
        contact,
        relative_parallel,
        relative_perpendicular,
        snapshot.source.radius,
    )
    contact_area_payload = _enclosure_payload(contact_area)
    contact_manifest = _raw_manifest(
        contact_raw,
        role="physical_contact_fraction_relative",
        shape=(shape[1], shape[2]),
    )
    contact_relation = _domain_digest(
        b"production-killing-contact-relation-v1\0",
        _contact_relation_payload(
            active_cell_count=active_contact_cells,
            full_cell_count=full_contact_cells,
            row_index=row_index,
            row_label=row["label"],
            shape=(shape[1], shape[2]),
            raw_sha256=contact_file["sha256"],
            area_enclosure=contact_area_payload,
            partition_source=partition_source,
            producer_sha256=snapshot.producer_sha256,
            quality_ledger=contact_quality,
            source=snapshot.source,
        ),
    )
    contact_entry = {
        "active_cell_count": active_contact_cells,
        "area_enclosure_exact": contact_area_payload,
        "file": contact_file,
        "full_cell_count": full_contact_cells,
        "manifest": contact_manifest,
        "quality_ledger": contact_quality,
        "relation_sha256": contact_relation,
    }

    support_entries: list[dict[str, object]] = []
    support_relations: list[str] = []
    for profile_index, (profile, centre, centre_hex, integral, quality) in enumerate(
        zip(
            supports,
            snapshot.source.support_centres,
            snapshot.source.support_centres_hex,
            support_integrals,
            support_qualities,
            strict=True,
        )
    ):
        raw = _interval_raw_bytes(
            profile.density_intervals, label=f"support density {profile_index}"
        )
        raw_file = emit(Path(f"midpoint_support_density_{profile_index:02d}.be64"), raw)
        raw_manifest = _raw_manifest(
            raw,
            role=f"physical_midpoint_support_density_{profile_index:02d}",
            shape=(shape[0],),
        )
        integral_payload = _enclosure_payload(integral)
        relation = _domain_digest(
            b"production-killing-support-relation-v1\0",
            _support_relation_payload(
                row_index=row_index,
                row_label=row["label"],
                profile_index=profile_index,
                centre=centre,
                shape=(shape[0],),
                raw_sha256=raw_file["sha256"],
                integral_enclosure=integral_payload,
                partition_source=partition_source,
                producer_sha256=snapshot.producer_sha256,
                quality_ledger=quality,
                source=snapshot.source,
            ),
        )
        support_relations.append(relation)
        support_entries.append(
            {
                "centre_binary64_hex": centre_hex,
                "centre_exact": _fraction_text(centre),
                "file": raw_file,
                "half_width_binary64_hex": snapshot.source.support_half_width_hex,
                "half_width_exact": _fraction_text(snapshot.source.support_half_width),
                "integral_enclosure_exact": integral_payload,
                "manifest": raw_manifest,
                "profile_index": profile_index,
                "quality_ledger": quality,
                "relation_sha256": relation,
            }
        )
    row_relation = _domain_digest(
        b"production-killing-row-relation-v1\0",
        _row_relation_payload(
            row_index=row_index,
            row_label=row["label"],
            shape=shape,  # type: ignore[arg-type]
            contact_relation_sha256=contact_relation,
            support_relation_sha256s=support_relations,
            partition_source=partition_source,
            producer_sha256=snapshot.producer_sha256,
        ),
    )
    row_manifest = {
        "configuration_index": row_index,
        "configuration_label": row["label"],
        "contact_fraction_relative": contact_entry,
        "expected_states": row["expected_states"],
        "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
        "flags": dict(_ROW_FLAGS),
        "gates": dict(_ROW_GATES),
        "partition_source": partition_source,
        "row_relation_sha256": row_relation,
        "schema": ROW_SCHEMA,
        "shape": list(shape),
        "source_pins": _source_pins_copy(snapshot.producer_sha256),
        "status": ROW_STATUS,
        "support_densities": support_entries,
    }
    row_bytes = _canonical_json_bytes(row_manifest)
    row_file = emit(Path("row.json"), row_bytes)
    summary = {
        "active_contact_cell_count": active_contact_cells,
        "configuration_index": row_index,
        "configuration_label": row["label"],
        "contact_fraction_records": shape[1] * shape[2],
        "expected_states": row["expected_states"],
        "full_contact_cell_count": full_contact_cells,
        "midpoint_cells": shape[0],
        "row_manifest": row_file,
        "row_relation_sha256": row_relation,
        "shape": list(shape),
        "support_density_records": 4 * shape[0],
        "support_profile_count": 4,
    }
    return summary, files, partition_source


def _partition_reference_graph_payload(
    rows: Sequence[tuple[dict[str, object], dict[str, object]]],
) -> dict[str, object]:
    return {
        "partition_bundle_manifest_sha256": ACCEPTED_PARTITION_BUNDLE_SHA256,
        "rows": [
            {
                "configuration_index": summary["configuration_index"],
                "bundle_row_manifest": source["bundle_row_manifest"],
                "bundle_row_relation_sha256": source["bundle_row_relation_sha256"],
                "partitions": source["partitions"],
            }
            for summary, source in rows
        ],
    }


def _family_relation_payload(
    *,
    rows: Sequence[dict[str, object]],
    partition_reference_graph_sha256: str,
    producer_sha256: str,
) -> dict[str, object]:
    return {
        "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
        "ordered_row_relation_sha256s": [row["row_relation_sha256"] for row in rows],
        "partition_reference_graph_sha256": partition_reference_graph_sha256,
        "source_pins": _source_pins_copy(producer_sha256),
    }


def _rename_directory_no_replace(source: Path, destination: Path) -> None:
    """Atomically publish one directory without replacing an existing path."""

    if destination.exists() or destination.is_symlink():
        raise ProductionKillingGeometryFailure("output path already exists")
    libc = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source)
    destination_bytes = os.fsencode(destination)
    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        function = libc.renamex_np
        function.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        function.restype = ctypes.c_int
        result = function(source_bytes, destination_bytes, 0x00000004)  # RENAME_EXCL
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        function = libc.renameat2
        function.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        function.restype = ctypes.c_int
        result = function(-100, source_bytes, -100, destination_bytes, 0x00000001)
    else:
        raise ProductionKillingGeometryFailure(
            "atomic no-replace publication is unsupported on this platform"
        )
    if result != 0:
        observed_errno = ctypes.get_errno()
        if observed_errno in {errno.EEXIST, errno.ENOTEMPTY}:
            raise ProductionKillingGeometryFailure("output path already exists")
        raise ProductionKillingGeometryFailure(
            f"atomic no-replace publication failed with errno {observed_errno}"
        )


def produce_bundle(report_root: Path, output: Path) -> dict[str, object]:
    """Build, fully verify, and atomically publish a new compact bundle."""

    report_root = report_root.resolve()
    lexical_output = output.expanduser().absolute()
    if lexical_output.exists() or lexical_output.is_symlink():
        raise ProductionKillingGeometryFailure("output path already exists")
    output = lexical_output.parent.resolve() / lexical_output.name
    if output.exists() or output.is_symlink():
        raise ProductionKillingGeometryFailure("resolved output path already exists")
    snapshot = _load_input_snapshot(report_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent))
    published = False
    try:
        request_payloads = {
            "configuration": ("request/configuration.json", snapshot.family_bytes),
            "killing_geometry_source": (
                "request/killing_geometry_source.json",
                snapshot.source_bytes,
            ),
            "partition_bundle_manifest": (
                "request/partition_bundle_manifest.json",
                snapshot.partition_bytes,
            ),
        }
        request_snapshots: dict[str, dict[str, object]] = {}
        files: list[dict[str, object]] = []
        for role, (relative, payload) in request_payloads.items():
            _write_bytes(temporary / Path(relative), payload)
            entry = _file_entry(relative, payload)
            request_snapshots[role] = entry
            files.append(entry)
        rows: list[dict[str, object]] = []
        partition_rows: list[tuple[dict[str, object], dict[str, object]]] = []
        configurations = snapshot.family["configurations"]
        if type(configurations) is not list or len(configurations) != 12:
            raise ProductionKillingGeometryFailure("configuration row list is invalid")
        for row_index, row in enumerate(configurations):
            if type(row) is not dict:
                raise ProductionKillingGeometryFailure("configuration row type is invalid")
            summary, row_files, partition_source = _build_row_geometry(
                temporary,
                report_root,
                snapshot,
                row_index=row_index,
                row=row,
            )
            rows.append(summary)
            partition_rows.append((summary, partition_source))
            files.extend(row_files)
        files.sort(key=lambda entry: entry["path"])
        partition_reference_graph_sha256 = _domain_digest(
            b"production-killing-partition-reference-graph-v1\0",
            _partition_reference_graph_payload(partition_rows),
        )
        family_relation_sha256 = _domain_digest(
            b"production-killing-family-relation-v1\0",
            _family_relation_payload(
                rows=rows,
                partition_reference_graph_sha256=partition_reference_graph_sha256,
                producer_sha256=snapshot.producer_sha256,
            ),
        )
        manifest = {
            "configuration_count": 12,
            "family_relation_sha256": family_relation_sha256,
            "factorization_contract": _FACTORIZATION_CONTRACT,
            "factorization_contract_sha256": FACTORIZATION_CONTRACT_SHA256,
            "file_inventory": files,
            "flags": dict(_BUNDLE_FLAGS),
            "method": dict(_METHOD),
            "partition_reference_graph_sha256": partition_reference_graph_sha256,
            "request_snapshots": request_snapshots,
            "rows": rows,
            "schema": SCHEMA,
            "source_pins": _source_pins_copy(snapshot.producer_sha256),
            "status": STATUS,
            "totals": {
                "active_contact_cell_count": sum(row["active_contact_cell_count"] for row in rows),
                "contact_fraction_records": TOTAL_CONTACT_RECORDS,
                "contact_fraction_raw_bytes": 16 * TOTAL_CONTACT_RECORDS,
                "full_contact_cell_count": sum(row["full_contact_cell_count"] for row in rows),
                "midpoint_cells": TOTAL_MIDPOINT_CELLS,
                "raw_interval_bytes": TOTAL_RAW_BYTES,
                "raw_interval_records": TOTAL_RAW_RECORDS,
                "support_density_records": TOTAL_SUPPORT_RECORDS,
                "support_density_raw_bytes": 16 * TOTAL_SUPPORT_RECORDS,
                "support_profile_count": TOTAL_SUPPORT_PROFILES,
            },
        }
        _write_bytes(temporary / "bundle.json", _canonical_json_bytes(manifest))
        verified = verify_bundle(report_root, temporary)
        _rename_directory_no_replace(temporary, output)
        published = True
        return verified
    finally:
        if not published:
            shutil.rmtree(temporary, ignore_errors=True)


def _verify_inventory(root: Path, inventory: dict[str, dict[str, object]]) -> None:
    expected_files = set(inventory) | {"bundle.json"}
    expected_directories: set[str] = set()
    for relative in expected_files:
        parent = PurePosixPath(relative).parent
        while parent != PurePosixPath("."):
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    if len(expected_directories) != EXPECTED_INVENTORY_DIRECTORIES:
        raise ProductionKillingGeometryFailure("inventory-derived directory count is invalid")

    actual_files: set[str] = set()
    actual_directories: set[str] = set()
    observed_inodes: dict[tuple[int, int], str] = {}
    node_count = 0
    pending: list[tuple[Path, PurePosixPath]] = [(root, PurePosixPath("."))]
    while pending:
        directory, relative_directory = pending.pop()
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    relative = (
                        PurePosixPath(entry.name)
                        if relative_directory == PurePosixPath(".")
                        else relative_directory / entry.name
                    )
                    relative_text = relative.as_posix()
                    node_count += 1
                    if node_count > MAXIMUM_BUNDLE_TREE_NODES:
                        raise ProductionKillingGeometryFailure("bundle tree node cap exceeded")
                    if len(relative.parts) > MAXIMUM_BUNDLE_RELATIVE_DEPTH:
                        raise ProductionKillingGeometryFailure("bundle tree depth cap exceeded")
                    try:
                        metadata = entry.stat(follow_symlinks=False)
                    except OSError as exc:
                        raise ProductionKillingGeometryFailure(
                            f"bundle tree node could not be inspected: {relative_text}"
                        ) from exc
                    mode = metadata.st_mode
                    if stat.S_ISLNK(mode):
                        raise ProductionKillingGeometryFailure(
                            f"bundle contains a symlink: {relative_text}"
                        )
                    inode = (metadata.st_dev, metadata.st_ino)
                    previous = observed_inodes.get(inode)
                    if previous is not None:
                        raise ProductionKillingGeometryFailure(
                            "bundle contains a hard-link or inode alias: "
                            f"{previous} and {relative_text}"
                        )
                    observed_inodes[inode] = relative_text
                    if stat.S_ISDIR(mode):
                        actual_directories.add(relative_text)
                        pending.append((Path(entry.path), relative))
                    elif stat.S_ISREG(mode):
                        if metadata.st_nlink != 1:
                            raise ProductionKillingGeometryFailure(
                                f"bundle regular file has multiple hard links: {relative_text}"
                            )
                        actual_files.add(relative_text)
                    else:
                        raise ProductionKillingGeometryFailure(
                            f"bundle contains a non-regular node: {relative_text}"
                        )
        except OSError as exc:
            raise ProductionKillingGeometryFailure("bundle tree could not be enumerated") from exc
    if actual_files != expected_files:
        raise ProductionKillingGeometryFailure("bundle has missing or unexpected files")
    if actual_directories != expected_directories:
        raise ProductionKillingGeometryFailure(
            "bundle has missing, empty, or unexpected directories"
        )
    for relative, entry in inventory.items():
        source = _read_regular_bytes(root / Path(relative), maximum_bytes=2_000_000)
        if len(source) != entry["byte_length"] or not hmac.compare_digest(
            _sha256_bytes(source), entry["sha256"]
        ):
            raise ProductionKillingGeometryFailure(f"bundle file bytes changed: {relative}")


def _record_reference(
    entry: object,
    inventory: dict[str, dict[str, object]],
    referenced: set[str],
    *,
    label: str,
) -> dict[str, object]:
    current = _validate_file_entry(entry, label=label)
    relative = current["path"]
    if inventory.get(relative) != current:
        raise ProductionKillingGeometryFailure(f"{label} is not bound to inventory")
    if relative in referenced:
        raise ProductionKillingGeometryFailure(f"duplicate file reference: {relative}")
    referenced.add(relative)
    return current


def _read_internal_file(
    root: Path,
    entry: object,
    inventory: dict[str, dict[str, object]],
    *,
    maximum_bytes: int,
) -> bytes:
    current = _validate_file_entry(entry, label="internal file reference")
    if inventory.get(current["path"]) != current:
        raise ProductionKillingGeometryFailure("internal file is not bound to inventory")
    source = _read_regular_bytes(root / Path(current["path"]), maximum_bytes=maximum_bytes)
    if len(source) != current["byte_length"] or not hmac.compare_digest(
        _sha256_bytes(source), current["sha256"]
    ):
        raise ProductionKillingGeometryFailure("internal file changed after inventory snapshot")
    return source


def verify_bundle(report_root: Path, root: Path) -> dict[str, object]:
    """Verify every file, relation, interval gate, and non-promotion flag."""

    report_root = report_root.resolve()
    snapshot = _load_input_snapshot(report_root)
    if root.is_symlink():
        raise ProductionKillingGeometryFailure("bundle root is a symlink")
    root = root.resolve()
    if not root.is_dir():
        raise ProductionKillingGeometryFailure("bundle root is not a directory")
    manifest = _require_exact_keys(
        _parse_canonical_json(
            _read_regular_bytes(root / "bundle.json", maximum_bytes=2_000_000),
            label="bundle manifest",
        ),
        _BUNDLE_KEYS,
        label="bundle manifest",
    )
    recorded_totals = _require_exact_keys(
        manifest["totals"],
        {
            "active_contact_cell_count",
            "contact_fraction_raw_bytes",
            "contact_fraction_records",
            "full_contact_cell_count",
            "midpoint_cells",
            "raw_interval_bytes",
            "raw_interval_records",
            "support_density_raw_bytes",
            "support_density_records",
            "support_profile_count",
        },
        label="bundle totals",
    )
    active_total = recorded_totals["active_contact_cell_count"]
    full_total = recorded_totals["full_contact_cell_count"]
    if (
        type(active_total) is not int
        or type(full_total) is not int
        or not 0 < full_total < active_total < TOTAL_CONTACT_RECORDS
    ):
        raise ProductionKillingGeometryFailure("bundle contact-cell totals are invalid")
    expected_totals = {
        "active_contact_cell_count": active_total,
        "contact_fraction_records": TOTAL_CONTACT_RECORDS,
        "contact_fraction_raw_bytes": 16 * TOTAL_CONTACT_RECORDS,
        "full_contact_cell_count": full_total,
        "midpoint_cells": TOTAL_MIDPOINT_CELLS,
        "raw_interval_bytes": TOTAL_RAW_BYTES,
        "raw_interval_records": TOTAL_RAW_RECORDS,
        "support_density_records": TOTAL_SUPPORT_RECORDS,
        "support_density_raw_bytes": 16 * TOTAL_SUPPORT_RECORDS,
        "support_profile_count": TOTAL_SUPPORT_PROFILES,
    }
    if (
        manifest["schema"] != SCHEMA
        or manifest["status"] != STATUS
        or manifest["configuration_count"] != 12
        or manifest["factorization_contract"] != _FACTORIZATION_CONTRACT
        or manifest["factorization_contract_sha256"] != FACTORIZATION_CONTRACT_SHA256
        or manifest["flags"] != _BUNDLE_FLAGS
        or manifest["method"] != _METHOD
        or manifest["source_pins"] != _source_pins_copy(snapshot.producer_sha256)
        or manifest["totals"] != expected_totals
    ):
        raise ProductionKillingGeometryFailure("bundle boundary metadata is invalid")
    inventory = _generic_inventory_map(manifest, expected_count=EXPECTED_INVENTORY_FILES)
    _verify_inventory(root, inventory)
    referenced: set[str] = set()
    request_snapshots = _require_exact_keys(
        manifest["request_snapshots"],
        {"configuration", "killing_geometry_source", "partition_bundle_manifest"},
        label="request snapshots",
    )
    expected_request_bytes = {
        "configuration": snapshot.family_bytes,
        "killing_geometry_source": snapshot.source_bytes,
        "partition_bundle_manifest": snapshot.partition_bytes,
    }
    for role, expected_bytes in expected_request_bytes.items():
        entry = _record_reference(
            request_snapshots[role], inventory, referenced, label=f"{role} request snapshot"
        )
        observed = _read_internal_file(root, entry, inventory, maximum_bytes=2_000_000)
        if observed != expected_bytes:
            raise ProductionKillingGeometryFailure(f"{role} request snapshot drifted")

    rows = manifest["rows"]
    configurations = snapshot.family["configurations"]
    if type(rows) is not list or len(rows) != 12 or type(configurations) is not list:
        raise ProductionKillingGeometryFailure("bundle row list is invalid")
    row_relations: list[str] = []
    partition_rows: list[tuple[dict[str, object], dict[str, object]]] = []
    totals = {
        "active_contact_cell_count": 0,
        "contact_fraction_records": 0,
        "contact_fraction_raw_bytes": 0,
        "full_contact_cell_count": 0,
        "midpoint_cells": 0,
        "raw_interval_bytes": 0,
        "raw_interval_records": 0,
        "support_density_records": 0,
        "support_density_raw_bytes": 0,
        "support_profile_count": 0,
    }
    for row_index, (summary_payload, row) in enumerate(zip(rows, configurations, strict=True)):
        if type(row) is not dict:
            raise ProductionKillingGeometryFailure("configuration row type is invalid")
        summary = _require_exact_keys(summary_payload, _ROW_SUMMARY_KEYS, label="row summary")
        shape = tuple(row["shape"])
        expected_summary_scalars = {
            "configuration_index": row_index,
            "configuration_label": row["label"],
            "contact_fraction_records": shape[1] * shape[2],
            "expected_states": row["expected_states"],
            "midpoint_cells": shape[0],
            "shape": list(shape),
            "support_density_records": 4 * shape[0],
            "support_profile_count": 4,
        }
        if any(summary[key] != value for key, value in expected_summary_scalars.items()):
            raise ProductionKillingGeometryFailure("row summary scalar binding drifted")
        row_file = _record_reference(
            summary["row_manifest"], inventory, referenced, label="row manifest"
        )
        row_manifest = _require_exact_keys(
            _parse_canonical_json(
                _read_internal_file(root, row_file, inventory, maximum_bytes=2_000_000),
                label="row manifest",
            ),
            _ROW_KEYS,
            label="row manifest",
        )
        if (
            row_manifest["schema"] != ROW_SCHEMA
            or row_manifest["status"] != ROW_STATUS
            or row_manifest["configuration_index"] != row_index
            or row_manifest["configuration_label"] != row["label"]
            or row_manifest["expected_states"] != row["expected_states"]
            or row_manifest["factorization_contract_sha256"] != FACTORIZATION_CONTRACT_SHA256
            or row_manifest["shape"] != list(shape)
            or row_manifest["source_pins"] != _source_pins_copy(snapshot.producer_sha256)
            or row_manifest["flags"] != _ROW_FLAGS
            or row_manifest["gates"] != _ROW_GATES
            or row_manifest["row_relation_sha256"] != summary["row_relation_sha256"]
        ):
            raise ProductionKillingGeometryFailure("row manifest boundary metadata drifted")
        axes = initial_stream._build_control_free_axes(row, snapshot.family["dynamics"])
        expected_partition_source = _partition_source_for_row(
            report_root,
            snapshot,
            row_index=row_index,
            row=row,
            axes=axes,
        )
        partition_source = _require_exact_keys(
            row_manifest["partition_source"],
            _PARTITION_SOURCE_KEYS,
            label="partition source",
        )
        bindings = partition_source["partitions"]
        if type(bindings) is not list or len(bindings) != 3:
            raise ProductionKillingGeometryFailure("partition source list is invalid")
        for binding in bindings:
            current = _require_exact_keys(
                binding, _PARTITION_BINDING_KEYS, label="partition binding"
            )
            _validate_file_entry(current["file"], label="partition binding file")
        if partition_source != expected_partition_source:
            raise ProductionKillingGeometryFailure("partition source binding drifted")
        midpoint, relative_parallel, relative_perpendicular = axes
        expected_contact = f0.build_contact_fraction_intervals_v2(
            relative_parallel,
            relative_perpendicular,
            radius=snapshot.source.radius,
            precision_bits=PRECISION_BITS,
        )
        expected_contact = _canonicalize_full_contact_intervals(
            expected_contact,
            relative_parallel,
            relative_perpendicular,
            snapshot.source.radius,
        )
        contact_payload = _require_exact_keys(
            row_manifest["contact_fraction_relative"], _CONTACT_KEYS, label="contact field"
        )
        contact_file = _record_reference(
            contact_payload["file"], inventory, referenced, label="contact raw file"
        )
        contact_raw = _read_internal_file(root, contact_file, inventory, maximum_bytes=2_000_000)
        contact = _parse_interval_raw(
            contact_raw,
            contact_payload["manifest"],
            expected_role="physical_contact_fraction_relative",
            expected_shape=(shape[1], shape[2]),
        )
        expected_contact_raw = _interval_raw_bytes(expected_contact, label="expected contact")
        if contact_raw != expected_contact_raw or any(interval.upper > 1.0 for interval in contact):
            raise ProductionKillingGeometryFailure(
                "contact field differs from same-core source reconstruction"
            )
        active_contact_cells, full_contact_cells = _contact_cell_counts(
            contact,
            relative_parallel,
            relative_perpendicular,
            snapshot.source.radius,
        )
        if (
            contact_payload["active_cell_count"] != active_contact_cells
            or contact_payload["full_cell_count"] != full_contact_cells
            or summary["active_contact_cell_count"] != active_contact_cells
            or summary["full_contact_cell_count"] != full_contact_cells
            or not 0 < full_contact_cells < active_contact_cells < len(contact)
        ):
            raise ProductionKillingGeometryFailure("contact active/full-cell counts drifted")
        contact_volumes = tuple(
            parallel_volume * transverse_volume
            for parallel_volume in relative_parallel.cell_volumes
            for transverse_volume in relative_perpendicular.cell_volumes
        )
        contact_area = _weighted_enclosure(contact, contact_volumes)
        recorded_area = _parse_enclosure(
            contact_payload["area_enclosure_exact"], label="contact area"
        )
        direct_area = f0.disk_rectangle_area_interval(
            relative_parallel.domain_start,
            relative_parallel.domain_start + relative_parallel.domain_width,
            relative_perpendicular.domain_start,
            relative_perpendicular.domain_start + relative_perpendicular.domain_width,
            snapshot.source.radius,
            precision_bits=PRECISION_BITS,
        )
        if (
            recorded_area != contact_area
            or contact_area[0] <= 0
            or contact_area[1]
            > relative_parallel.domain_width * relative_perpendicular.domain_width
            or max(contact_area[0], direct_area.lower_fraction)
            > min(contact_area[1], direct_area.upper_fraction)
        ):
            raise ProductionKillingGeometryFailure("contact area enclosure drifted")
        contact_quality = _contact_quality_ledger(
            contact_area,
            radius=snapshot.source.radius,
        )
        if contact_payload["quality_ledger"] != contact_quality:
            raise ProductionKillingGeometryFailure("contact quality ledger drifted")
        expected_contact_relation = _domain_digest(
            b"production-killing-contact-relation-v1\0",
            _contact_relation_payload(
                active_cell_count=active_contact_cells,
                full_cell_count=full_contact_cells,
                row_index=row_index,
                row_label=row["label"],
                shape=(shape[1], shape[2]),
                raw_sha256=contact_file["sha256"],
                area_enclosure=contact_payload["area_enclosure_exact"],
                partition_source=partition_source,
                producer_sha256=snapshot.producer_sha256,
                quality_ledger=contact_quality,
                source=snapshot.source,
            ),
        )
        if contact_payload["relation_sha256"] != expected_contact_relation:
            raise ProductionKillingGeometryFailure("contact relation digest drifted")

        supports_payload = row_manifest["support_densities"]
        if type(supports_payload) is not list or len(supports_payload) != 4:
            raise ProductionKillingGeometryFailure("support profile list is invalid")
        expected_supports = tuple(
            f0.build_normalized_bump_profile(
                midpoint,
                centre=centre,
                half_width=snapshot.source.support_half_width,
                panels_per_unit=PANELS_PER_UNIT,
                precision_bits=PRECISION_BITS,
            )
            for centre in snapshot.source.support_centres
        )
        support_relations: list[str] = []
        for profile_index, (payload, expected_profile, centre, centre_hex) in enumerate(
            zip(
                supports_payload,
                expected_supports,
                snapshot.source.support_centres,
                snapshot.source.support_centres_hex,
                strict=True,
            )
        ):
            support = _require_exact_keys(payload, _SUPPORT_KEYS, label="support profile")
            if (
                support["profile_index"] != profile_index
                or support["centre_binary64_hex"] != centre_hex
                or support["centre_exact"] != _fraction_text(centre)
                or support["half_width_binary64_hex"] != snapshot.source.support_half_width_hex
                or support["half_width_exact"] != _fraction_text(snapshot.source.support_half_width)
            ):
                raise ProductionKillingGeometryFailure("support source binding drifted")
            support_file = _record_reference(
                support["file"], inventory, referenced, label="support raw file"
            )
            support_raw = _read_internal_file(
                root, support_file, inventory, maximum_bytes=2_000_000
            )
            decoded = _parse_interval_raw(
                support_raw,
                support["manifest"],
                expected_role=f"physical_midpoint_support_density_{profile_index:02d}",
                expected_shape=(shape[0],),
            )
            expected_raw = _interval_raw_bytes(
                expected_profile.density_intervals,
                label=f"expected support {profile_index}",
            )
            if support_raw != expected_raw:
                raise ProductionKillingGeometryFailure(
                    "support density differs from same-core source reconstruction"
                )
            integral = _weighted_enclosure(decoded, midpoint.cell_volumes)
            if (
                _parse_enclosure(
                    support["integral_enclosure_exact"],
                    label=f"support {profile_index} integral",
                )
                != integral
                or not integral[0] <= 1 <= integral[1]
            ):
                raise ProductionKillingGeometryFailure("support integral enclosure drifted")
            support_quality = _support_quality_ledger(
                integral,
                centre=centre,
                half_width=snapshot.source.support_half_width,
                midpoint=midpoint,
            )
            if support["quality_ledger"] != support_quality:
                raise ProductionKillingGeometryFailure("support quality ledger drifted")
            relation = _domain_digest(
                b"production-killing-support-relation-v1\0",
                _support_relation_payload(
                    row_index=row_index,
                    row_label=row["label"],
                    profile_index=profile_index,
                    centre=centre,
                    shape=(shape[0],),
                    raw_sha256=support_file["sha256"],
                    integral_enclosure=support["integral_enclosure_exact"],
                    partition_source=partition_source,
                    producer_sha256=snapshot.producer_sha256,
                    quality_ledger=support_quality,
                    source=snapshot.source,
                ),
            )
            if support["relation_sha256"] != relation:
                raise ProductionKillingGeometryFailure("support relation digest drifted")
            support_relations.append(relation)
        expected_row_relation = _domain_digest(
            b"production-killing-row-relation-v1\0",
            _row_relation_payload(
                row_index=row_index,
                row_label=row["label"],
                shape=shape,  # type: ignore[arg-type]
                contact_relation_sha256=expected_contact_relation,
                support_relation_sha256s=support_relations,
                partition_source=partition_source,
                producer_sha256=snapshot.producer_sha256,
            ),
        )
        if row_manifest["row_relation_sha256"] != expected_row_relation:
            raise ProductionKillingGeometryFailure("row relation digest drifted")
        row_relations.append(expected_row_relation)
        partition_rows.append((summary, partition_source))
        totals["active_contact_cell_count"] += active_contact_cells
        totals["contact_fraction_records"] += shape[1] * shape[2]
        totals["contact_fraction_raw_bytes"] += 16 * shape[1] * shape[2]
        totals["full_contact_cell_count"] += full_contact_cells
        totals["midpoint_cells"] += shape[0]
        totals["support_density_records"] += 4 * shape[0]
        totals["support_density_raw_bytes"] += 16 * 4 * shape[0]
        totals["support_profile_count"] += 4
        totals["raw_interval_records"] += shape[1] * shape[2] + 4 * shape[0]
        totals["raw_interval_bytes"] += 16 * (shape[1] * shape[2] + 4 * shape[0])
    if referenced != set(inventory):
        raise ProductionKillingGeometryFailure("inventory/reference graph is not exact")
    if totals != expected_totals:
        raise ProductionKillingGeometryFailure("bundle aggregate counts drifted")
    partition_reference_graph_sha256 = _domain_digest(
        b"production-killing-partition-reference-graph-v1\0",
        _partition_reference_graph_payload(partition_rows),
    )
    if manifest["partition_reference_graph_sha256"] != partition_reference_graph_sha256:
        raise ProductionKillingGeometryFailure("partition reference graph digest drifted")
    family_relation_sha256 = _domain_digest(
        b"production-killing-family-relation-v1\0",
        _family_relation_payload(
            rows=[{"row_relation_sha256": relation} for relation in row_relations],
            partition_reference_graph_sha256=partition_reference_graph_sha256,
            producer_sha256=snapshot.producer_sha256,
        ),
    )
    if manifest["family_relation_sha256"] != family_relation_sha256:
        raise ProductionKillingGeometryFailure("family relation digest drifted")
    return manifest


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    produce = subparsers.add_parser("produce")
    produce.add_argument("--report-root", type=Path, required=True)
    produce.add_argument("--output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--report-root", type=Path, required=True)
    verify.add_argument("--bundle", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.command == "produce":
        manifest = produce_bundle(arguments.report_root, arguments.output)
    else:
        manifest = verify_bundle(arguments.report_root, arguments.bundle)
    print(_canonical_json_bytes({"status": manifest["status"]}).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
