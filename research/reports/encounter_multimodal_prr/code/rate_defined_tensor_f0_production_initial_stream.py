"""File-backed control-free production geometry and initial-box evidence.

This module closes a narrow pre-F0 gap for the frozen twelve-row physical
configuration family.  It reconstructs exact finite-volume partitions and
free-axis rate intervals without instantiating the positive-budget parameter
object, encloses the frozen analytic compact-bump initial law, and writes a
sparse component box with an exact implicit positive-zero background.

The output is producer-consistency evidence only.  It contains no killing
array, control values, positive budget, propagation, topology conclusion,
continuum conclusion, or F0/F1 decision.  A separate numerical implementation
must rederive the geometry/rate and source/box relations before those relations
can be described as independently replayed.
"""

from __future__ import annotations

import argparse
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
from itertools import product
from pathlib import Path, PurePosixPath
from typing import Final, Iterable, Sequence

_CODE_DIRECTORY = Path(__file__).resolve().parent
if str(_CODE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(_CODE_DIRECTORY))

import rate_defined_tensor_f0 as f0  # noqa: E402

SCHEMA: Final = "encounter_control_free_production_initial_stream_v1"
ROW_SCHEMA: Final = "encounter_control_free_production_initial_row_v1"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"
RAW_SCHEMA: Final = "encounter_big_endian_binary64_interval_file_v1"
SPARSE_SCHEMA: Final = "encounter_sparse_component_interval_box_v1"
CONFIGURATION_SCHEMA: Final = "encounter_physical_configuration_family_control_free_v1"
ANALYTIC_SOURCE_SCHEMA: Final = "encounter_physical_initial_analytic_source_v1"
STATUS: Final = (
    "PASS_CONTROL_FREE_12_ROW_FILE_BACKED_PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0_NOT_F1"
)

ACCEPTED_CONFIGURATION_SHA256: Final = (
    "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
)
ACCEPTED_ANALYTIC_SOURCE_SHA256: Final = (
    "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
)
ACCEPTED_F0_SOURCE_SHA256: Final = (
    "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5"
)

CONFIGURATION_RELATIVE_PATH: Final = Path(
    "artifacts/data/physical_configuration_family_control_free_v1.json"
)
ANALYTIC_SOURCE_RELATIVE_PATH: Final = Path(
    "artifacts/data/physical_initial_analytic_source_v1.json"
)
TENSOR_ORDER: Final = "C:midpoint_outer_relative_parallel_middle_transverse_inner"
COORDINATE_ORDER: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)
PANELS_PER_UNIT: Final = 16_384
PRECISION_BITS: Final = 192
SPARSE_MAGIC: Final = b"ECSPBX01"
SPARSE_VERSION: Final = 1
SPARSE_IMPLICIT_POSITIVE_ZERO: Final = 1
SPARSE_HEADER: Final = struct.Struct(">8sIIQQQQQII")
SPARSE_RECORD: Final = struct.Struct(">Qdd")
ZERO_INTERVAL_RECORD: Final = struct.pack(">dd", 0.0, 0.0)
ZERO_HASH_BLOCK_STATES: Final = 65_536

_CONFIGURATION_TOP_KEYS: Final = {
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
}
_ROW_KEYS: Final = {
    "expected_states",
    "label",
    "midpoint",
    "purpose",
    "relative_parallel",
    "relative_perpendicular",
    "shape",
}
_REFLECTING_AXIS_KEYS: Final = {
    "alignment",
    "lower_binary64_hex",
    "size",
    "upper_binary64_hex",
}
_PERIODIC_AXIS_KEYS: Final = {"alignment", "periodic_shift_exact", "size"}
_PARTITION_KEYS: Final = {
    "cell_segments_exact",
    "cell_volumes_exact",
    "construction",
    "coordinate",
    "domain_start_exact",
    "domain_width_exact",
    "periodic",
    "periodic_shift_exact",
    "positions_exact",
    "schema",
    "size",
}
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
_SPARSE_MANIFEST_KEYS: Final = {
    "active_component_count",
    "active_index_sha256",
    "dense_expansion_byte_length",
    "dense_expansion_record_format",
    "dense_expansion_sha256",
    "file",
    "implicit_background",
    "lower_mass_exact",
    "record_format",
    "schema",
    "shape",
    "state_count",
    "tensor_order",
    "upper_mass_exact",
}
_BUNDLE_KEYS: Final = {
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
_BUNDLE_FLAGS: Final = {
    "analytic_source_to_sparse_box_producer_consistent_all_rows": True,
    "authorizes_scientific_execution": False,
    "clean_process_replay_complete": False,
    "contains_budget_value": False,
    "contains_control_values": False,
    "free_axis_geometry_rate_producer_consistent_all_rows": True,
    "full_operator_bound": False,
    "independent_geometry_relation_replay_complete": False,
    "independent_source_box_replay_complete": False,
    "killing_contact_geometry_bound": False,
    "positive_budget_executed": False,
    "production_resource_gate": False,
    "science_executed": False,
    "topology_complete": False,
}
_ROW_MANIFEST_KEYS: Final = {
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
_ROW_SUMMARY_KEYS: Final = {
    "configuration_index",
    "configuration_label",
    "expected_states",
    "row_manifest",
    "row_relation_sha256",
}
_AXIS_ENTRY_KEYS: Final = {
    "axis_relation_sha256",
    "coordinate",
    "partition_file",
    "rates",
}
_MARGINAL_ENTRY_KEYS: Final = {
    "active_indices",
    "coordinate",
    "file",
    "manifest",
}
_RATE_ENTRY_KEYS: Final = {"file", "manifest"}
_ALIGNMENT_TO_CONSTRUCTION: Final = {
    "cell_centred_reflecting": "cell_centred_reflecting_scharfetter_gummel",
    "vertex_centred_reflecting_dual": "vertex_centred_reflecting_scharfetter_gummel",
    "cell_centred_periodic_base": "cell_centred_periodic_diffusion",
    "cell_centred_periodic_half_shift": "cell_centred_periodic_diffusion_half_shift",
}

_EXPECTED_SOURCE_OBJECT: Final = {
    "analytic_total_mass_exact": "1/1",
    "construction": "independent_product_of_three_analytically_normalized_compact_bumps",
    "coordinate_order": list(COORDINATE_ORDER),
    "half_width_binary64_hex": "0x1.47ae147ae147bp-6",
    "marginal_density": "b((x-c)/h)/(h*I_b)",
    "normalization": "I_b=integral_-1^1_b(u)_du",
    "periodic_coordinate": "relative_perpendicular",
    "periodic_wrap": "sum_over_periodic_images_before_cell_integration",
    "physical_dimension": 2,
    "quotient_dimension": 3,
    "schema": ANALYTIC_SOURCE_SCHEMA,
    "shared_normalizer_across_cells_and_axes": True,
    "scope": "physical_initial_law_only_no_control_no_budget",
    "shape_definition": "b(u)=indicator(abs(u)<1)*exp(-1/(1-u^2))",
    "starts_binary64_hex": {
        "midpoint": "0x1.1eb851eb851ecp-3",
        "relative_parallel": "-0x1.6666666666666p-2",
        "relative_perpendicular": "0x0.0p+0",
    },
    "transverse_period_exact": "1/1",
}


class ProductionInitialStreamFailure(RuntimeError):
    """Fail-closed error for the production initial-stream evidence layer."""


@dataclass(frozen=True, slots=True)
class AnalyticLaw:
    centres: tuple[Fraction, Fraction, Fraction]
    half_width: Fraction
    transverse_period: Fraction
    source_sha256: str


@dataclass(frozen=True, slots=True)
class SparseComponentBox:
    shape: tuple[int, int, int]
    state_count: int
    records: tuple[tuple[int, f0.OutwardInterval], ...]
    lower_mass: Fraction
    upper_mass: Fraction
    dense_be_sha256: str
    dense_be_byte_length: int
    active_index_sha256: str


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(_read_regular_bytes(path, maximum_bytes=10_000_000))


def _canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise ProductionInitialStreamFailure("JSON has a duplicate or invalid key")
        result[key] = value
    return result


def _reject_json_float(token: str) -> object:
    raise ProductionInitialStreamFailure(f"JSON floating literal is forbidden: {token}")


def _parse_strict_json(source: bytes, *, label: str) -> object:
    if type(source) is not bytes:
        raise ProductionInitialStreamFailure(f"{label} does not have exact bytes type")
    try:
        payload = json.loads(
            source.decode("ascii"),
            object_pairs_hook=_strict_object,
            parse_float=_reject_json_float,
            parse_constant=_reject_json_float,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProductionInitialStreamFailure(f"{label} is not strict ASCII JSON") from error
    return payload


def _parse_canonical_json(source: bytes, *, label: str) -> object:
    payload = _parse_strict_json(source, label=label)
    if _canonical_json_bytes(payload) != source:
        raise ProductionInitialStreamFailure(f"{label} is not canonical sorted indent-2 JSON")
    return payload


def _require_exact_keys(payload: object, expected: set[str], *, label: str) -> dict[str, object]:
    if type(payload) is not dict or set(payload) != expected:
        raise ProductionInitialStreamFailure(f"{label} key set is invalid")
    return payload


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _parse_fraction_text(value: object, *, label: str) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise ProductionInitialStreamFailure(f"{label} is not a canonical fraction")
    numerator_text, denominator_text = value.split("/")
    try:
        numerator = int(numerator_text)
        denominator = int(denominator_text)
    except ValueError as error:
        raise ProductionInitialStreamFailure(f"{label} is not an integer fraction") from error
    if denominator <= 0:
        raise ProductionInitialStreamFailure(f"{label} has a nonpositive denominator")
    parsed = Fraction(numerator, denominator)
    if _fraction_text(parsed) != value:
        raise ProductionInitialStreamFailure(f"{label} is not reduced canonical text")
    return parsed


def _parse_hex_fraction(value: object, *, label: str) -> Fraction:
    if type(value) is not str:
        raise ProductionInitialStreamFailure(f"{label} is not binary64 hex text")
    try:
        parsed = float.fromhex(value)
    except ValueError as error:
        raise ProductionInitialStreamFailure(f"{label} is not valid binary64 hex") from error
    if not math.isfinite(parsed) or parsed.hex() != value:
        raise ProductionInitialStreamFailure(f"{label} is not canonical finite binary64")
    if parsed == 0.0 and math.copysign(1.0, parsed) < 0:
        raise ProductionInitialStreamFailure(f"{label} is negative zero")
    return Fraction.from_float(parsed)


def _domain_digest(domain: bytes, payload: object) -> str:
    if not domain.endswith(b"\0"):
        raise ProductionInitialStreamFailure("digest domain is not NUL terminated")
    return _sha256_bytes(domain + _canonical_json_bytes(payload))


def _read_regular_bytes(path: Path, *, maximum_bytes: int) -> bytes:
    flags = os.O_RDONLY
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ProductionInitialStreamFailure(f"required file is unavailable: {path}") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum_bytes:
            raise ProductionInitialStreamFailure(f"required file is unsafe or oversized: {path}")
        chunks: list[bytes] = []
        observed = 0
        while block := os.read(descriptor, min(1 << 20, maximum_bytes + 1 - observed)):
            chunks.append(block)
            observed += len(block)
            if observed > maximum_bytes:
                raise ProductionInitialStreamFailure(f"required file is oversized: {path}")
        after = os.fstat(descriptor)
        snapshot_before = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        snapshot_after = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if snapshot_before != snapshot_after or observed != before.st_size:
            raise ProductionInitialStreamFailure(f"required file changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _verify_authority_files(report_root: Path, authority: object) -> None:
    fields = _require_exact_keys(
        authority,
        {
            "design_path",
            "design_sha256",
            "implementation_path",
            "implementation_sha256",
            "test_path",
            "test_sha256",
        },
        label="configuration authority",
    )
    for prefix in ("design", "implementation", "test"):
        relative = fields[f"{prefix}_path"]
        digest = fields[f"{prefix}_sha256"]
        if type(relative) is not str or type(digest) is not str:
            raise ProductionInitialStreamFailure("authority path/hash type is invalid")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or len(digest) != 64:
            raise ProductionInitialStreamFailure("authority path/hash syntax is invalid")
        observed = _sha256_file(report_root / Path(*pure.parts))
        if not hmac.compare_digest(observed, digest):
            raise ProductionInitialStreamFailure(f"{prefix} authority bytes changed")
    if fields["implementation_sha256"] != ACCEPTED_F0_SOURCE_SHA256:
        raise ProductionInitialStreamFailure("configuration points at an unaccepted F0 core")
    if not hmac.compare_digest(
        _sha256_file(Path(f0.__file__).resolve()), ACCEPTED_F0_SOURCE_SHA256
    ):
        raise ProductionInitialStreamFailure("imported F0 core bytes changed")


def _validate_configuration_semantics(report_root: Path, payload: object) -> dict[str, object]:
    family = _require_exact_keys(payload, _CONFIGURATION_TOP_KEYS, label="configuration family")
    if (
        family["schema"] != CONFIGURATION_SCHEMA
        or family["scope"] != "physical_d2_control_free_axis_and_initial_geometry_only"
        or family["status"] != "CONTROL_FREE_GEOMETRY_SPEC_ONLY_NOT_F0_NOT_F1"
        or family["physical_dimension"] != 2
        or family["quotient_dimension"] != 3
        or family["coordinate_order"] != list(COORDINATE_ORDER)
        or family["configuration_count"] != 12
        or family["configuration_order"] != list(f0.PHYSICAL_CONFIGURATION_ORDER_V2)
        or family["total_state_workload"] != 34_787_462
        or family["contains_budget_value"] is not False
        or family["contains_control_values"] is not False
        or family["authorizes_scientific_execution"] is not False
    ):
        raise ProductionInitialStreamFailure("configuration family boundary metadata is invalid")
    if family["workload_semantics"] != (
        "sum_of_state_counts_across_the_12_prescribed_axis_triples_for_one_future_control"
    ):
        raise ProductionInitialStreamFailure("configuration workload semantics drifted")
    _verify_authority_files(report_root, family["authority"])

    dynamics = _require_exact_keys(
        family["dynamics"],
        {
            "directed_precision_bits",
            "midpoint_diffusion_formula",
            "midpoint_potential_formula",
            "ou_mean_binary64_hex",
            "ou_stiffness_binary64_hex",
            "particle_diffusion_binary64_hex",
            "relative_diffusion_formula",
            "relative_parallel_mean_exact",
            "relative_parallel_potential_formula",
            "relative_perpendicular_potential_formula",
            "transverse_domain_start_exact",
            "transverse_period_exact",
        },
        label="dynamics",
    )
    if (
        dynamics["directed_precision_bits"] != PRECISION_BITS
        or dynamics["midpoint_diffusion_formula"] != "particle_diffusion/2"
        or dynamics["relative_diffusion_formula"] != "2*particle_diffusion"
        or dynamics["relative_parallel_mean_exact"] != "0/1"
        or dynamics["relative_perpendicular_potential_formula"] != "0/1"
        or dynamics["transverse_domain_start_exact"] != "-1/2"
        or dynamics["transverse_period_exact"] != "1/1"
    ):
        raise ProductionInitialStreamFailure("control-free dynamics contract drifted")
    for key in (
        "ou_mean_binary64_hex",
        "ou_stiffness_binary64_hex",
        "particle_diffusion_binary64_hex",
    ):
        _parse_hex_fraction(dynamics[key], label=key)

    initial = _require_exact_keys(
        family["initial_geometry"],
        {
            "construction",
            "half_width_binary64_hex",
            "normalization",
            "periodic_wrap",
            "shape_definition",
            "source_path",
            "source_schema",
            "source_sha256",
            "starts_binary64_hex",
        },
        label="initial geometry",
    )
    if (
        initial["source_path"] != ANALYTIC_SOURCE_RELATIVE_PATH.as_posix()
        or initial["source_schema"] != ANALYTIC_SOURCE_SCHEMA
        or initial["source_sha256"] != ACCEPTED_ANALYTIC_SOURCE_SHA256
    ):
        raise ProductionInitialStreamFailure("initial source binding drifted")
    if set(initial["starts_binary64_hex"]) != set(COORDINATE_ORDER):
        raise ProductionInitialStreamFailure("initial centre key set drifted")
    for coordinate in COORDINATE_ORDER:
        _parse_hex_fraction(initial["starts_binary64_hex"][coordinate], label=coordinate)
    _parse_hex_fraction(initial["half_width_binary64_hex"], label="initial half width")

    contracts = family["axis_construction_contracts"]
    if type(contracts) is not dict or set(contracts) != set(_ALIGNMENT_TO_CONSTRUCTION):
        raise ProductionInitialStreamFailure("axis construction contract key set drifted")
    for alignment, construction in _ALIGNMENT_TO_CONSTRUCTION.items():
        contract = contracts[alignment]
        if type(contract) is not dict or contract.get("source_construction_tag") != construction:
            raise ProductionInitialStreamFailure("axis construction tag mapping drifted")

    rows = family["configurations"]
    core_rows = f0.physical_configuration_specs_v2()
    if type(rows) is not list or len(rows) != len(core_rows):
        raise ProductionInitialStreamFailure("configuration row count drifted")
    for row, core in zip(rows, core_rows, strict=True):
        current = _require_exact_keys(row, _ROW_KEYS, label=f"row {core.label}")
        midpoint = _require_exact_keys(
            current["midpoint"], _REFLECTING_AXIS_KEYS, label=f"{core.label} midpoint"
        )
        relative = _require_exact_keys(
            current["relative_parallel"],
            _REFLECTING_AXIS_KEYS,
            label=f"{core.label} relative parallel",
        )
        transverse = _require_exact_keys(
            current["relative_perpendicular"],
            _PERIODIC_AXIS_KEYS,
            label=f"{core.label} transverse",
        )
        expected_midpoint_alignment = (
            "vertex_centred_reflecting_dual"
            if core.midpoint_vertex_centred
            else "cell_centred_reflecting"
        )
        expected_relative_alignment = (
            "vertex_centred_reflecting_dual"
            if core.relative_vertex_centred
            else "cell_centred_reflecting"
        )
        expected_transverse_alignment = (
            "cell_centred_periodic_half_shift"
            if core.transverse_half_shift
            else "cell_centred_periodic_base"
        )
        expected_shape = [core.midpoint_size, core.relative_size, core.transverse_size]
        expected_shift = Fraction(1, 2 * core.transverse_size) if core.transverse_half_shift else 0
        if (
            current["label"] != core.label
            or current["purpose"] != core.purpose
            or current["shape"] != expected_shape
            or current["expected_states"] != core.expected_states
            or midpoint["size"] != core.midpoint_size
            or relative["size"] != core.relative_size
            or transverse["size"] != core.transverse_size
            or midpoint["alignment"] != expected_midpoint_alignment
            or relative["alignment"] != expected_relative_alignment
            or transverse["alignment"] != expected_transverse_alignment
            or _parse_hex_fraction(midpoint["lower_binary64_hex"], label="midpoint lower")
            != core.midpoint_lower
            or _parse_hex_fraction(midpoint["upper_binary64_hex"], label="midpoint upper")
            != core.midpoint_upper
            or _parse_hex_fraction(relative["lower_binary64_hex"], label="relative lower")
            != core.relative_lower
            or _parse_hex_fraction(relative["upper_binary64_hex"], label="relative upper")
            != core.relative_upper
            or _parse_fraction_text(transverse["periodic_shift_exact"], label="shift")
            != expected_shift
        ):
            raise ProductionInitialStreamFailure(f"configuration row drifted: {core.label}")
    return family


def load_configuration_family(report_root: Path) -> tuple[dict[str, object], bytes]:
    path = report_root / CONFIGURATION_RELATIVE_PATH
    source = _read_regular_bytes(path, maximum_bytes=2_000_000)
    if not hmac.compare_digest(_sha256_bytes(source), ACCEPTED_CONFIGURATION_SHA256):
        raise ProductionInitialStreamFailure("configuration family bytes are not accepted")
    payload = _parse_canonical_json(source, label="configuration family")
    return _validate_configuration_semantics(report_root, payload), source


def load_analytic_law(report_root: Path) -> tuple[AnalyticLaw, bytes]:
    source = _read_regular_bytes(
        report_root / ANALYTIC_SOURCE_RELATIVE_PATH,
        maximum_bytes=100_000,
    )
    observed = _sha256_bytes(source)
    if not hmac.compare_digest(observed, ACCEPTED_ANALYTIC_SOURCE_SHA256):
        raise ProductionInitialStreamFailure("analytic source bytes are not accepted")
    payload = _parse_strict_json(source, label="analytic source")
    if payload != _EXPECTED_SOURCE_OBJECT:
        raise ProductionInitialStreamFailure("analytic source law drifted")
    starts = payload["starts_binary64_hex"]
    centres = tuple(
        _parse_hex_fraction(starts[name], label=f"{name} centre") for name in COORDINATE_ORDER
    )
    half_width = _parse_hex_fraction(payload["half_width_binary64_hex"], label="half width")
    period = _parse_fraction_text(payload["transverse_period_exact"], label="period")
    if half_width <= 0 or 2 * half_width >= period:
        raise ProductionInitialStreamFailure("analytic compact-bump support is invalid")
    return AnalyticLaw(centres, half_width, period, observed), source


def _build_control_free_axes(
    row: dict[str, object], dynamics: dict[str, object]
) -> tuple[f0.TensorAxis, f0.TensorAxis, f0.TensorAxis]:
    particle_diffusion = _parse_hex_fraction(
        dynamics["particle_diffusion_binary64_hex"], label="particle diffusion"
    )
    stiffness = _parse_hex_fraction(dynamics["ou_stiffness_binary64_hex"], label="OU stiffness")
    mean = _parse_hex_fraction(dynamics["ou_mean_binary64_hex"], label="OU mean")
    midpoint_diffusion = particle_diffusion / 2
    relative_diffusion = 2 * particle_diffusion
    midpoint_spec = row["midpoint"]
    relative_spec = row["relative_parallel"]
    transverse_spec = row["relative_perpendicular"]

    def potential(position: Fraction, *, centre: Fraction, diffusion: Fraction) -> Fraction:
        return stiffness * (position - centre) ** 2 / (2 * diffusion)

    def reflecting_axis(
        name: str,
        spec: dict[str, object],
        *,
        centre: Fraction,
        diffusion: Fraction,
    ) -> f0.TensorAxis:
        lower = _parse_hex_fraction(spec["lower_binary64_hex"], label=f"{name} lower")
        upper = _parse_hex_fraction(spec["upper_binary64_hex"], label=f"{name} upper")
        size = spec["size"]
        if type(size) is not int:
            raise ProductionInitialStreamFailure(f"{name} size type is invalid")

        def potential_at(point: Fraction) -> Fraction:
            return potential(point, centre=centre, diffusion=diffusion)

        if spec["alignment"] == "vertex_centred_reflecting_dual":
            step = (upper - lower) / (size - 1)
            positions = tuple(lower + index * step for index in range(size))
            return f0.build_reflecting_sg_axis(
                name,
                positions,
                tuple(potential_at(point) for point in positions),
                diffusion,
                precision_bits=PRECISION_BITS,
            )
        if spec["alignment"] != "cell_centred_reflecting":
            raise ProductionInitialStreamFailure(f"{name} reflecting alignment is invalid")
        return f0.build_cell_centred_reflecting_sg_axis(
            name,
            lower,
            upper,
            size,
            potential_at,
            diffusion,
            precision_bits=PRECISION_BITS,
        )

    midpoint = reflecting_axis("midpoint", midpoint_spec, centre=mean, diffusion=midpoint_diffusion)
    relative = reflecting_axis(
        "relative_parallel", relative_spec, centre=Fraction(0), diffusion=relative_diffusion
    )
    transverse = f0.build_periodic_diffusion_axis(
        "relative_perpendicular",
        transverse_spec["size"],
        Fraction(1),
        relative_diffusion,
        half_cell_shift=transverse_spec["alignment"] == "cell_centred_periodic_half_shift",
        domain_start=Fraction(-1, 2),
    )
    axes = (midpoint, relative, transverse)
    for axis, coordinate in zip(axes, COORDINATE_ORDER, strict=True):
        _validate_axis_geometry(axis, row[coordinate])
    return axes


def _mod_fraction(value: Fraction, width: Fraction) -> Fraction:
    return value - (value // width) * width


def _validate_axis_geometry(axis: f0.TensorAxis, specification: dict[str, object]) -> None:
    axis.validate()
    expected_construction = _ALIGNMENT_TO_CONSTRUCTION.get(specification["alignment"])
    if expected_construction is None or axis.construction != expected_construction:
        raise ProductionInitialStreamFailure(f"{axis.name} construction drifted")
    if axis.size != specification["size"]:
        raise ProductionInitialStreamFailure(f"{axis.name} size drifted")
    if axis.periodic:
        lower = Fraction(-1, 2)
        width = Fraction(1)
        step = width / axis.size
        shift = _parse_fraction_text(specification["periodic_shift_exact"], label="shift")
        positions = tuple(
            lower + _mod_fraction((index + Fraction(1, 2)) * step + shift, width)
            for index in range(axis.size)
        )
        volumes = (step,) * axis.size
        segments: list[tuple[tuple[Fraction, Fraction], ...]] = []
        for index in range(axis.size):
            start = lower + _mod_fraction(index * step + shift, width)
            stop = start + step
            if stop <= lower + width:
                segments.append(((start, stop),))
            else:
                segments.append(((start, lower + width), (lower, stop - width)))
        expected_segments = tuple(segments)
        expected_shift = shift
    else:
        lower = _parse_hex_fraction(specification["lower_binary64_hex"], label="lower")
        upper = _parse_hex_fraction(specification["upper_binary64_hex"], label="upper")
        width = upper - lower
        expected_shift = Fraction(0)
        if specification["alignment"] == "vertex_centred_reflecting_dual":
            step = width / (axis.size - 1)
            positions = tuple(lower + index * step for index in range(axis.size))
            boundaries = (
                (lower,)
                + tuple((left + right) / 2 for left, right in zip(positions, positions[1:]))
                + (upper,)
            )
            volumes = tuple(boundaries[index + 1] - boundaries[index] for index in range(axis.size))
            expected_segments = tuple(
                ((boundaries[index], boundaries[index + 1]),) for index in range(axis.size)
            )
        else:
            step = width / axis.size
            positions = tuple(lower + (index + Fraction(1, 2)) * step for index in range(axis.size))
            volumes = (step,) * axis.size
            expected_segments = tuple(
                ((lower + index * step, lower + (index + 1) * step),) for index in range(axis.size)
            )
    if (
        axis.domain_start != lower
        or axis.domain_width != width
        or axis.periodic_shift != expected_shift
        or axis.positions != positions
        or axis.cell_volumes != volumes
        or axis.cell_segments != expected_segments
        or sum(axis.cell_volumes, Fraction(0)) != width
    ):
        raise ProductionInitialStreamFailure(f"{axis.name} exact partition relation drifted")
    flattened = sorted(segment for cell in axis.cell_segments for segment in cell)
    cursor = lower
    for segment_lower, segment_upper in flattened:
        if segment_lower != cursor or segment_lower >= segment_upper:
            raise ProductionInitialStreamFailure(f"{axis.name} partition has a gap/overlap")
        cursor = segment_upper
    if cursor != lower + width:
        raise ProductionInitialStreamFailure(f"{axis.name} partition does not cover its domain")
    f0.verify_axis_detailed_balance(axis)


def _partition_payload(axis: f0.TensorAxis) -> dict[str, object]:
    return {
        "cell_segments_exact": [
            [[_fraction_text(lower), _fraction_text(upper)] for lower, upper in segments]
            for segments in axis.cell_segments
        ],
        "cell_volumes_exact": [_fraction_text(value) for value in axis.cell_volumes],
        "construction": axis.construction,
        "coordinate": axis.name,
        "domain_start_exact": _fraction_text(axis.domain_start),
        "domain_width_exact": _fraction_text(axis.domain_width),
        "periodic": axis.periodic,
        "periodic_shift_exact": _fraction_text(axis.periodic_shift),
        "positions_exact": [_fraction_text(value) for value in axis.positions],
        "schema": PARTITION_SCHEMA,
        "size": axis.size,
    }


def _validate_interval(interval: f0.OutwardInterval, *, label: str) -> None:
    if type(interval) is not f0.OutwardInterval:
        raise ProductionInitialStreamFailure(f"{label} has wrong interval type")
    interval.require_nonnegative(label)
    for endpoint in (interval.lower, interval.upper):
        if not math.isfinite(endpoint) or (endpoint == 0.0 and math.copysign(1.0, endpoint) < 0):
            raise ProductionInitialStreamFailure(f"{label} has noncanonical endpoint")


def _interval_raw_bytes(intervals: Sequence[f0.OutwardInterval], *, label: str) -> bytes:
    raw = bytearray(len(intervals) * 16)
    for index, interval in enumerate(intervals):
        _validate_interval(interval, label=f"{label}[{index}]")
        struct.pack_into(">dd", raw, 16 * index, interval.lower, interval.upper)
    return bytes(raw)


def _raw_manifest(
    raw: bytes,
    *,
    role: str,
    shape: Sequence[int],
    record_format: str = ">dd",
) -> dict[str, object]:
    return {
        "byte_order": "big",
        "logical_shape": list(shape),
        "raw_byte_length": len(raw),
        "raw_sha256": _sha256_bytes(raw),
        "record_count": math.prod(shape),
        "record_format": record_format,
        "role": role,
        "schema": RAW_SCHEMA,
    }


def _build_marginals(
    axes: tuple[f0.TensorAxis, f0.TensorAxis, f0.TensorAxis], law: AnalyticLaw
) -> tuple[f0.NormalizedBumpProfile, f0.NormalizedBumpProfile, f0.NormalizedBumpProfile]:
    profiles = tuple(
        f0.build_normalized_bump_profile(
            axis,
            centre=law.centres[index],
            half_width=law.half_width,
            period=law.transverse_period if axis.periodic else None,
            panels_per_unit=PANELS_PER_UNIT,
            precision_bits=PRECISION_BITS,
        )
        for index, axis in enumerate(axes)
    )
    for profile, axis in zip(profiles, axes, strict=True):
        if profile.analytic_total_mass != 1 or len(profile.mass_intervals) != axis.size:
            raise ProductionInitialStreamFailure("initial marginal construction drifted")
        lower = sum((entry.lower_fraction for entry in profile.mass_intervals), Fraction(0))
        upper = sum((entry.upper_fraction for entry in profile.mass_intervals), Fraction(0))
        if not lower <= 1 <= upper:
            raise ProductionInitialStreamFailure("initial marginal misses analytic unit mass")
    return profiles


def _active_index_digest(indices: Iterable[int]) -> str:
    digest = hashlib.sha256(b"production-initial-active-flat-indices-v1\0")
    for index in indices:
        digest.update(index.to_bytes(8, "big"))
    return digest.hexdigest()


def _update_zero_dense_hash(digest: object, states: int) -> None:
    block = ZERO_INTERVAL_RECORD * ZERO_HASH_BLOCK_STATES
    full, remainder = divmod(states, ZERO_HASH_BLOCK_STATES)
    for _ in range(full):
        digest.update(block)
    if remainder:
        digest.update(ZERO_INTERVAL_RECORD * remainder)


def _dense_be_digest(state_count: int, records: Sequence[tuple[int, f0.OutwardInterval]]) -> str:
    digest = hashlib.sha256()
    cursor = 0
    for index, interval in records:
        if index < cursor or index >= state_count:
            raise ProductionInitialStreamFailure("sparse component index order/range is invalid")
        _update_zero_dense_hash(digest, index - cursor)
        digest.update(struct.pack(">dd", interval.lower, interval.upper))
        cursor = index + 1
    _update_zero_dense_hash(digest, state_count - cursor)
    return digest.hexdigest()


def _build_sparse_component_box(
    profiles: tuple[
        f0.NormalizedBumpProfile,
        f0.NormalizedBumpProfile,
        f0.NormalizedBumpProfile,
    ],
) -> SparseComponentBox:
    shape = tuple(len(profile.mass_intervals) for profile in profiles)
    state_count = math.prod(shape)
    active_axes = tuple(
        tuple(index for index, entry in enumerate(profile.mass_intervals) if entry.upper > 0.0)
        for profile in profiles
    )
    if any(not indices for indices in active_axes):
        raise ProductionInitialStreamFailure("an initial marginal has empty active support")
    records: list[tuple[int, f0.OutwardInterval]] = []
    for i, j, k in product(*active_axes):
        interval = (
            profiles[0]
            .mass_intervals[i]
            .multiply_nonnegative(profiles[1].mass_intervals[j])
            .multiply_nonnegative(profiles[2].mass_intervals[k])
        )
        flat_index = (i * shape[1] + j) * shape[2] + k
        if interval.upper <= 0.0:
            raise ProductionInitialStreamFailure("active Cartesian product contains zero")
        _validate_interval(interval, label=f"component[{flat_index}]")
        records.append((flat_index, interval))
    expected_count = math.prod(len(indices) for indices in active_axes)
    if len(records) != expected_count or any(
        left[0] >= right[0] for left, right in zip(records, records[1:])
    ):
        raise ProductionInitialStreamFailure("sparse active Cartesian product is incomplete")
    active_sets = tuple(set(indices) for indices in active_axes)
    for coordinate, profile in enumerate(profiles):
        for index, interval in enumerate(profile.mass_intervals):
            if (index in active_sets[coordinate]) != (interval.upper > 0.0):
                raise ProductionInitialStreamFailure("implicit-zero support proof drifted")
    lower_mass = sum((entry.lower_fraction for _, entry in records), Fraction(0))
    upper_mass = sum((entry.upper_fraction for _, entry in records), Fraction(0))
    if not lower_mass <= 1 <= upper_mass:
        raise ProductionInitialStreamFailure("sparse tensor box misses analytic unit mass")
    frozen_records = tuple(records)
    return SparseComponentBox(
        shape=shape,
        state_count=state_count,
        records=frozen_records,
        lower_mass=lower_mass,
        upper_mass=upper_mass,
        dense_be_sha256=_dense_be_digest(state_count, frozen_records),
        dense_be_byte_length=16 * state_count,
        active_index_sha256=_active_index_digest(index for index, _ in frozen_records),
    )


def _sparse_raw(box: SparseComponentBox) -> bytes:
    raw = bytearray(
        SPARSE_HEADER.pack(
            SPARSE_MAGIC,
            SPARSE_VERSION,
            3,
            box.state_count,
            len(box.records),
            box.shape[0],
            box.shape[1],
            box.shape[2],
            SPARSE_RECORD.size,
            SPARSE_IMPLICIT_POSITIVE_ZERO,
        )
    )
    for index, interval in box.records:
        raw.extend(SPARSE_RECORD.pack(index, interval.lower, interval.upper))
    return bytes(raw)


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        target.write(payload)


def _safe_slug(label: str) -> str:
    translated = label.lower().replace("+", "_plus").replace("/", "_")
    slug = "".join(character if character.isalnum() else "_" for character in translated)
    return "_".join(part for part in slug.split("_") if part)


def _emit_row(
    root: Path,
    *,
    row_index: int,
    row: dict[str, object],
    dynamics: dict[str, object],
    law: AnalyticLaw,
    configuration_sha256: str,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    row_directory = Path("rows") / f"{row_index:02d}_{_safe_slug(row['label'])}"
    axes = _build_control_free_axes(row, dynamics)
    profiles = _build_marginals(axes, law)
    sparse = _build_sparse_component_box(profiles)
    files: list[dict[str, object]] = []

    def emit(relative: Path, payload: bytes) -> dict[str, object]:
        full_relative = row_directory / relative
        _write_bytes(root / full_relative, payload)
        entry = {
            "byte_length": len(payload),
            "path": full_relative.as_posix(),
            "sha256": _sha256_bytes(payload),
        }
        files.append(entry)
        return entry

    axis_entries: list[dict[str, object]] = []
    marginal_entries: list[dict[str, object]] = []
    for axis, profile in zip(axes, profiles, strict=True):
        partition_bytes = _canonical_json_bytes(_partition_payload(axis))
        partition_file = emit(Path(f"{axis.name}.partition.json"), partition_bytes)
        rate_files: dict[str, object] = {}
        for direction, intervals in (
            ("forward", axis.forward_rates),
            ("backward", axis.backward_rates),
            ("stationary_mass", axis.stationary_masses),
        ):
            raw = _interval_raw_bytes(intervals, label=f"{axis.name} {direction}")
            raw_file = emit(Path(f"{axis.name}.{direction}.be64"), raw)
            rate_files[direction] = {
                "file": raw_file,
                "manifest": _raw_manifest(
                    raw,
                    role=f"control_free_axis_{axis.name}_{direction}",
                    shape=(axis.size,),
                ),
            }
        axis_relation = {
            "coordinate": axis.name,
            "partition_sha256": partition_file["sha256"],
            "rate_raw_sha256s": {
                name: rate_files[name]["file"]["sha256"] for name in sorted(rate_files)
            },
        }
        axis_entries.append(
            {
                "axis_relation_sha256": _domain_digest(
                    b"production-initial-axis-geometry-rate-relation-v1\0", axis_relation
                ),
                "coordinate": axis.name,
                "partition_file": partition_file,
                "rates": rate_files,
            }
        )
        marginal_raw = _interval_raw_bytes(
            profile.mass_intervals, label=f"{axis.name} initial marginal"
        )
        marginal_file = emit(Path(f"{axis.name}.initial_marginal.be64"), marginal_raw)
        active_indices = [
            index for index, interval in enumerate(profile.mass_intervals) if interval.upper > 0.0
        ]
        marginal_entries.append(
            {
                "active_indices": active_indices,
                "coordinate": axis.name,
                "file": marginal_file,
                "manifest": _raw_manifest(
                    marginal_raw,
                    role=f"analytic_initial_marginal_{axis.name}",
                    shape=(axis.size,),
                ),
            }
        )

    sparse_raw = _sparse_raw(sparse)
    sparse_file = emit(Path("initial_component_box.sparse.be64"), sparse_raw)
    sparse_manifest = {
        "active_component_count": len(sparse.records),
        "active_index_sha256": sparse.active_index_sha256,
        "dense_expansion_byte_length": sparse.dense_be_byte_length,
        "dense_expansion_record_format": ">dd",
        "dense_expansion_sha256": sparse.dense_be_sha256,
        "file": sparse_file,
        "implicit_background": "positive_zero_interval_[0x0.0p+0,0x0.0p+0]",
        "lower_mass_exact": _fraction_text(sparse.lower_mass),
        "record_format": ">Qdd",
        "schema": SPARSE_SCHEMA,
        "shape": list(sparse.shape),
        "state_count": sparse.state_count,
        "tensor_order": TENSOR_ORDER,
        "upper_mass_exact": _fraction_text(sparse.upper_mass),
    }
    source_box_relation = {
        "analytic_source_sha256": law.source_sha256,
        "configuration_sha256": configuration_sha256,
        "marginal_raw_sha256s": [entry["file"]["sha256"] for entry in marginal_entries],
        "sparse_raw_sha256": sparse_file["sha256"],
        "dense_expansion_sha256": sparse.dense_be_sha256,
        "shape": list(sparse.shape),
        "tensor_order": TENSOR_ORDER,
    }
    row_core = {
        "axes": axis_entries,
        "configuration_index": row_index,
        "configuration_label": row["label"],
        "configuration_sha256": configuration_sha256,
        "expected_states": row["expected_states"],
        "initial_marginals": marginal_entries,
        "source_box_relation_sha256": _domain_digest(
            b"production-initial-source-box-relation-v1\0", source_box_relation
        ),
        "sparse_component_box": sparse_manifest,
    }
    row_relation = _domain_digest(
        b"production-initial-row-relation-v1\0",
        {
            "axis_relation_sha256s": [entry["axis_relation_sha256"] for entry in axis_entries],
            "configuration_index": row_index,
            "configuration_label": row["label"],
            "source_box_relation_sha256": row_core["source_box_relation_sha256"],
        },
    )
    row_manifest = {
        **row_core,
        "flags": {
            "analytic_source_to_sparse_box_producer_consistent": True,
            "free_axis_geometry_rate_producer_consistent": True,
            "full_operator_bound": False,
            "independent_geometry_relation_replay": False,
            "independent_source_box_replay": False,
            "killing_contact_geometry_bound": False,
            "positive_budget_executed": False,
        },
        "row_relation_sha256": row_relation,
        "schema": ROW_SCHEMA,
        "status": "PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0",
    }
    row_bytes = _canonical_json_bytes(row_manifest)
    row_file = emit(Path("row.json"), row_bytes)
    return (
        {
            "configuration_index": row_index,
            "configuration_label": row["label"],
            "expected_states": row["expected_states"],
            "row_manifest": row_file,
            "row_relation_sha256": row_relation,
        },
        files,
    )


def produce_bundle(report_root: Path, output: Path) -> dict[str, object]:
    """Atomically produce all twelve file-backed control-free row bundles."""

    report_root = report_root.resolve()
    output = output.resolve()
    if output.exists() or output.is_symlink():
        raise ProductionInitialStreamFailure("output path already exists")
    family, family_bytes = load_configuration_family(report_root)
    law, source_bytes = load_analytic_law(report_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent))
    try:
        _write_bytes(temporary / "request" / "configuration.json", family_bytes)
        _write_bytes(temporary / "request" / "analytic_source.json", source_bytes)
        files = [
            {
                "byte_length": len(family_bytes),
                "path": "request/configuration.json",
                "sha256": _sha256_bytes(family_bytes),
            },
            {
                "byte_length": len(source_bytes),
                "path": "request/analytic_source.json",
                "sha256": _sha256_bytes(source_bytes),
            },
        ]
        rows: list[dict[str, object]] = []
        for index, row in enumerate(family["configurations"]):
            summary, row_files = _emit_row(
                temporary,
                row_index=index,
                row=row,
                dynamics=family["dynamics"],
                law=law,
                configuration_sha256=ACCEPTED_CONFIGURATION_SHA256,
            )
            rows.append(summary)
            files.extend(row_files)
        files.sort(key=lambda entry: entry["path"])
        family_relation = _domain_digest(
            b"production-initial-family-relation-v1\0",
            {
                "analytic_source_sha256": ACCEPTED_ANALYTIC_SOURCE_SHA256,
                "configuration_sha256": ACCEPTED_CONFIGURATION_SHA256,
                "ordered_row_relation_sha256s": [row["row_relation_sha256"] for row in rows],
            },
        )
        manifest = {
            "analytic_source_sha256": ACCEPTED_ANALYTIC_SOURCE_SHA256,
            "configuration_count": 12,
            "configuration_sha256": ACCEPTED_CONFIGURATION_SHA256,
            "family_relation_sha256": family_relation,
            "file_inventory": files,
            "flags": dict(_BUNDLE_FLAGS),
            "method": {
                "dense_component_box_materialized": False,
                "marginal_endpoint_record_format": ">dd",
                "panels_per_unit": PANELS_PER_UNIT,
                "precision_bits": PRECISION_BITS,
                "sparse_component_record_format": ">Qdd",
                "tensor_order": TENSOR_ORDER,
            },
            "rows": rows,
            "schema": SCHEMA,
            "status": STATUS,
            "total_dense_expansion_byte_length": 16 * family["total_state_workload"],
            "total_state_workload": family["total_state_workload"],
        }
        _write_bytes(temporary / "bundle.json", _canonical_json_bytes(manifest))
        os.replace(temporary, output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return verify_bundle(output)


def _inventory_map(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    inventory = manifest["file_inventory"]
    if type(inventory) is not list or len(inventory) != 206:
        raise ProductionInitialStreamFailure("bundle file inventory is invalid")
    result: dict[str, dict[str, object]] = {}
    for entry in inventory:
        current = _require_exact_keys(entry, {"byte_length", "path", "sha256"}, label="file")
        relative = current["path"]
        if type(relative) is not str or relative in result:
            raise ProductionInitialStreamFailure("file inventory path is invalid/duplicate")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or pure.as_posix() != relative:
            raise ProductionInitialStreamFailure("file inventory path is unsafe")
        if (
            type(current["byte_length"]) is not int
            or current["byte_length"] < 0
            or type(current["sha256"]) is not str
            or len(current["sha256"]) != 64
        ):
            raise ProductionInitialStreamFailure("file inventory metadata is invalid")
        result[relative] = current
    if list(result) != sorted(result):
        raise ProductionInitialStreamFailure("file inventory is not sorted")
    return result


def _verify_inventory(root: Path, inventory: dict[str, dict[str, object]]) -> None:
    actual: set[str] = set()
    for candidate in root.rglob("*"):
        relative = candidate.relative_to(root).as_posix()
        if candidate.is_symlink():
            raise ProductionInitialStreamFailure(f"bundle contains a symlink: {relative}")
        if candidate.is_file():
            actual.add(relative)
    if actual != set(inventory) | {"bundle.json"}:
        raise ProductionInitialStreamFailure("bundle has missing or unexpected files")
    for relative, entry in inventory.items():
        path = root / Path(*PurePosixPath(relative).parts)
        source = _read_regular_bytes(path, maximum_bytes=10_000_000)
        if len(source) != entry["byte_length"] or not hmac.compare_digest(
            _sha256_bytes(source), entry["sha256"]
        ):
            raise ProductionInitialStreamFailure(f"bundle file bytes changed: {relative}")


def _record_inventory_reference(
    file_entry: object,
    inventory: dict[str, dict[str, object]],
    referenced: set[str],
    *,
    label: str,
) -> None:
    current = _require_exact_keys(file_entry, {"byte_length", "path", "sha256"}, label=label)
    relative = current["path"]
    if type(relative) is not str or relative not in inventory:
        raise ProductionInitialStreamFailure(f"{label} is not in the inventory")
    if relative in referenced:
        raise ProductionInitialStreamFailure(f"duplicate bound file reference: {relative}")
    referenced.add(relative)


def _bound_inventory_path(
    root: Path,
    file_entry: object,
    inventory: dict[str, dict[str, object]],
) -> Path:
    current = _require_exact_keys(
        file_entry, {"byte_length", "path", "sha256"}, label="bound file entry"
    )
    relative = current["path"]
    if type(relative) is not str or inventory.get(relative) != current:
        raise ProductionInitialStreamFailure("file pointer is not bound to root inventory")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or pure.as_posix() != relative:
        raise ProductionInitialStreamFailure("bound file pointer is unsafe")
    return root / Path(*pure.parts)


def _read_bound_inventory_file(
    root: Path,
    file_entry: object,
    inventory: dict[str, dict[str, object]],
    *,
    maximum_bytes: int,
) -> bytes:
    current = _require_exact_keys(
        file_entry, {"byte_length", "path", "sha256"}, label="bound file entry"
    )
    source = _read_regular_bytes(
        _bound_inventory_path(root, current, inventory), maximum_bytes=maximum_bytes
    )
    if len(source) != current["byte_length"] or not hmac.compare_digest(
        _sha256_bytes(source), current["sha256"]
    ):
        raise ProductionInitialStreamFailure("bound file changed after inventory snapshot")
    return source


def _validate_partition_payload(payload: object) -> dict[str, object]:
    partition = _require_exact_keys(payload, _PARTITION_KEYS, label="axis partition")
    if (
        partition["schema"] != PARTITION_SCHEMA
        or type(partition["coordinate"]) is not str
        or partition["coordinate"] not in COORDINATE_ORDER
        or type(partition["size"]) is not int
        or partition["size"] < 3
        or type(partition["periodic"]) is not bool
        or type(partition["construction"]) is not str
    ):
        raise ProductionInitialStreamFailure("axis partition metadata is invalid")
    size = partition["size"]
    start = _parse_fraction_text(partition["domain_start_exact"], label="domain start")
    width = _parse_fraction_text(partition["domain_width_exact"], label="domain width")
    shift = _parse_fraction_text(partition["periodic_shift_exact"], label="periodic shift")
    if width <= 0 or shift < 0 or shift >= width:
        raise ProductionInitialStreamFailure("axis partition domain/shift is invalid")
    raw_positions = partition["positions_exact"]
    raw_volumes = partition["cell_volumes_exact"]
    raw_cells = partition["cell_segments_exact"]
    if (
        type(raw_positions) is not list
        or type(raw_volumes) is not list
        or type(raw_cells) is not list
        or len(raw_positions) != size
        or len(raw_volumes) != size
        or len(raw_cells) != size
    ):
        raise ProductionInitialStreamFailure("axis partition array length drifted")
    positions = tuple(_parse_fraction_text(value, label="axis position") for value in raw_positions)
    volumes = tuple(_parse_fraction_text(value, label="cell volume") for value in raw_volumes)
    cells: list[tuple[tuple[Fraction, Fraction], ...]] = []
    for raw_cell in raw_cells:
        if type(raw_cell) is not list or not raw_cell:
            raise ProductionInitialStreamFailure("axis partition has an empty cell")
        segments: list[tuple[Fraction, Fraction]] = []
        for raw_segment in raw_cell:
            if type(raw_segment) is not list or len(raw_segment) != 2:
                raise ProductionInitialStreamFailure("axis partition segment is malformed")
            lower = _parse_fraction_text(raw_segment[0], label="segment lower")
            upper = _parse_fraction_text(raw_segment[1], label="segment upper")
            if lower < start or upper > start + width or lower >= upper:
                raise ProductionInitialStreamFailure("axis partition segment is outside domain")
            segments.append((lower, upper))
        cells.append(tuple(segments))
    if any(volume <= 0 for volume in volumes):
        raise ProductionInitialStreamFailure("axis partition has a nonpositive cell volume")
    if any(
        sum((upper - lower for lower, upper in segments), Fraction(0)) != volume
        for segments, volume in zip(cells, volumes, strict=True)
    ):
        raise ProductionInitialStreamFailure("axis partition cell measure/volume disagrees")
    flattened = sorted(segment for cell in cells for segment in cell)
    cursor = start
    for lower, upper in flattened:
        if lower != cursor:
            raise ProductionInitialStreamFailure("axis partition has a gap or overlap")
        cursor = upper
    if cursor != start + width or sum(volumes, Fraction(0)) != width:
        raise ProductionInitialStreamFailure("axis partition does not exactly cover its domain")
    construction = partition["construction"]
    if partition["periodic"]:
        if construction not in {
            "cell_centred_periodic_diffusion",
            "cell_centred_periodic_diffusion_half_shift",
        }:
            raise ProductionInitialStreamFailure("periodic construction tag is invalid")
        step = width / size
        expected_shift = (
            step / 2
            if construction == "cell_centred_periodic_diffusion_half_shift"
            else Fraction(0)
        )
        expected_positions = tuple(
            start + _mod_fraction((index + Fraction(1, 2)) * step + expected_shift, width)
            for index in range(size)
        )
        expected_cells: list[tuple[tuple[Fraction, Fraction], ...]] = []
        for index in range(size):
            lower = start + _mod_fraction(index * step + expected_shift, width)
            upper = lower + step
            if upper <= start + width:
                expected_cells.append(((lower, upper),))
            else:
                expected_cells.append(((lower, start + width), (start, upper - width)))
        expected_volumes = (step,) * size
        if shift != expected_shift:
            raise ProductionInitialStreamFailure("periodic construction/shift disagrees")
    else:
        if shift != 0 or construction not in {
            "cell_centred_reflecting_scharfetter_gummel",
            "vertex_centred_reflecting_scharfetter_gummel",
        }:
            raise ProductionInitialStreamFailure("reflecting construction metadata is invalid")
        if construction == "vertex_centred_reflecting_scharfetter_gummel":
            step = width / (size - 1)
            expected_positions = tuple(start + index * step for index in range(size))
            boundaries = (
                (start,)
                + tuple(
                    (left + right) / 2
                    for left, right in zip(expected_positions, expected_positions[1:])
                )
                + (start + width,)
            )
            expected_cells = [
                ((boundaries[index], boundaries[index + 1]),) for index in range(size)
            ]
            expected_volumes = tuple(
                boundaries[index + 1] - boundaries[index] for index in range(size)
            )
        else:
            step = width / size
            expected_positions = tuple(
                start + (index + Fraction(1, 2)) * step for index in range(size)
            )
            expected_cells = [
                ((start + index * step, start + (index + 1) * step),) for index in range(size)
            ]
            expected_volumes = (step,) * size
    if (
        positions != expected_positions
        or volumes != expected_volumes
        or tuple(cells) != tuple(expected_cells)
    ):
        raise ProductionInitialStreamFailure("axis partition construction formula drifted")
    return partition


def _parse_interval_raw(raw: bytes, manifest: dict[str, object]) -> tuple[f0.OutwardInterval, ...]:
    _require_exact_keys(manifest, _RAW_MANIFEST_KEYS, label="raw interval manifest")
    if (
        manifest.get("schema") != RAW_SCHEMA
        or manifest.get("byte_order") != "big"
        or manifest.get("record_format") != ">dd"
        or type(manifest.get("role")) is not str
        or type(manifest.get("logical_shape")) is not list
        or manifest.get("logical_shape") != [manifest.get("record_count")]
        or type(manifest.get("record_count")) is not int
        or manifest.get("record_count") < 1
        or manifest.get("raw_byte_length") != len(raw)
        or manifest.get("raw_sha256") != _sha256_bytes(raw)
        or manifest.get("record_count") * 16 != len(raw)
    ):
        raise ProductionInitialStreamFailure("raw interval manifest is invalid")
    result: list[f0.OutwardInterval] = []
    for offset in range(0, len(raw), 16):
        interval = f0.OutwardInterval(*struct.unpack_from(">dd", raw, offset))
        _validate_interval(interval, label="file-backed interval")
        result.append(interval)
    return tuple(result)


def _parse_sparse_raw(raw: bytes, manifest: dict[str, object]) -> SparseComponentBox:
    _require_exact_keys(manifest, _SPARSE_MANIFEST_KEYS, label="sparse manifest")
    file_entry = _require_exact_keys(
        manifest["file"], {"byte_length", "path", "sha256"}, label="sparse file"
    )
    if len(raw) < SPARSE_HEADER.size:
        raise ProductionInitialStreamFailure("sparse component file is truncated")
    (
        magic,
        version,
        rank,
        states,
        active,
        first,
        second,
        third,
        record_size,
        flags,
    ) = SPARSE_HEADER.unpack_from(raw)
    shape = (first, second, third)
    if (
        magic != SPARSE_MAGIC
        or version != SPARSE_VERSION
        or rank != 3
        or record_size != SPARSE_RECORD.size
        or flags != SPARSE_IMPLICIT_POSITIVE_ZERO
        or math.prod(shape) != states
        or len(raw) != SPARSE_HEADER.size + active * SPARSE_RECORD.size
        or manifest.get("schema") != SPARSE_SCHEMA
        or manifest.get("shape") != list(shape)
        or manifest.get("state_count") != states
        or manifest.get("active_component_count") != active
        or manifest.get("record_format") != ">Qdd"
        or manifest.get("dense_expansion_record_format") != ">dd"
        or manifest.get("implicit_background") != "positive_zero_interval_[0x0.0p+0,0x0.0p+0]"
        or manifest.get("tensor_order") != TENSOR_ORDER
        or file_entry["byte_length"] != len(raw)
        or file_entry["sha256"] != _sha256_bytes(raw)
    ):
        raise ProductionInitialStreamFailure("sparse component header/manifest is invalid")
    records: list[tuple[int, f0.OutwardInterval]] = []
    cursor = SPARSE_HEADER.size
    for _ in range(active):
        index, lower, upper = SPARSE_RECORD.unpack_from(raw, cursor)
        cursor += SPARSE_RECORD.size
        interval = f0.OutwardInterval(lower, upper)
        _validate_interval(interval, label="sparse component")
        if interval.upper <= 0.0 or (records and index <= records[-1][0]) or index >= states:
            raise ProductionInitialStreamFailure("sparse component record is invalid")
        records.append((index, interval))
    lower_mass = sum((entry.lower_fraction for _, entry in records), Fraction(0))
    upper_mass = sum((entry.upper_fraction for _, entry in records), Fraction(0))
    result = SparseComponentBox(
        shape=shape,
        state_count=states,
        records=tuple(records),
        lower_mass=lower_mass,
        upper_mass=upper_mass,
        dense_be_sha256=_dense_be_digest(states, records),
        dense_be_byte_length=16 * states,
        active_index_sha256=_active_index_digest(index for index, _ in records),
    )
    if (
        manifest.get("dense_expansion_sha256") != result.dense_be_sha256
        or manifest.get("dense_expansion_byte_length") != result.dense_be_byte_length
        or manifest.get("active_index_sha256") != result.active_index_sha256
        or manifest.get("lower_mass_exact") != _fraction_text(result.lower_mass)
        or manifest.get("upper_mass_exact") != _fraction_text(result.upper_mass)
        or not result.lower_mass <= 1 <= result.upper_mass
    ):
        raise ProductionInitialStreamFailure("sparse component derived ledger drifted")
    return result


def verify_bundle(root: Path) -> dict[str, object]:
    """Verify canonical files, hashes, sparse expansion, and all producer relations."""

    if not hmac.compare_digest(
        _sha256_file(Path(f0.__file__).resolve()), ACCEPTED_F0_SOURCE_SHA256
    ):
        raise ProductionInitialStreamFailure("imported F0 core bytes changed")
    if root.is_symlink():
        raise ProductionInitialStreamFailure("bundle root is a symlink")
    root = root.resolve()
    if not root.is_dir():
        raise ProductionInitialStreamFailure("bundle root is not a regular directory")
    manifest_bytes = _read_regular_bytes(root / "bundle.json", maximum_bytes=2_000_000)
    manifest = _parse_canonical_json(manifest_bytes, label="bundle manifest")
    manifest = _require_exact_keys(manifest, _BUNDLE_KEYS, label="bundle manifest")
    if (
        manifest.get("schema") != SCHEMA
        or manifest.get("status") != STATUS
        or manifest.get("configuration_sha256") != ACCEPTED_CONFIGURATION_SHA256
        or manifest.get("analytic_source_sha256") != ACCEPTED_ANALYTIC_SOURCE_SHA256
        or manifest.get("configuration_count") != 12
        or manifest.get("total_state_workload") != 34_787_462
        or manifest.get("total_dense_expansion_byte_length") != 556_599_392
        or manifest.get("flags") != _BUNDLE_FLAGS
        or manifest.get("method")
        != {
            "dense_component_box_materialized": False,
            "marginal_endpoint_record_format": ">dd",
            "panels_per_unit": PANELS_PER_UNIT,
            "precision_bits": PRECISION_BITS,
            "sparse_component_record_format": ">Qdd",
            "tensor_order": TENSOR_ORDER,
        }
    ):
        raise ProductionInitialStreamFailure("bundle boundary metadata is invalid")
    inventory = _inventory_map(manifest)
    _verify_inventory(root, inventory)
    referenced_paths = {
        "request/analytic_source.json",
        "request/configuration.json",
    }
    if not referenced_paths <= set(inventory):
        raise ProductionInitialStreamFailure("request files are missing from inventory")
    request_family = _parse_canonical_json(
        _read_bound_inventory_file(
            root,
            inventory["request/configuration.json"],
            inventory,
            maximum_bytes=2_000_000,
        ),
        label="request configuration",
    )
    request_source_bytes = _read_bound_inventory_file(
        root,
        inventory["request/analytic_source.json"],
        inventory,
        maximum_bytes=100_000,
    )
    request_source = _parse_strict_json(request_source_bytes, label="request source")
    if (
        _sha256_bytes(_canonical_json_bytes(request_family)) != ACCEPTED_CONFIGURATION_SHA256
        or not hmac.compare_digest(
            _sha256_bytes(request_source_bytes), ACCEPTED_ANALYTIC_SOURCE_SHA256
        )
        or request_source != _EXPECTED_SOURCE_OBJECT
    ):
        raise ProductionInitialStreamFailure("request-only source bundle drifted")
    request_law = AnalyticLaw(
        centres=tuple(
            _parse_hex_fraction(
                request_source["starts_binary64_hex"][coordinate],
                label=f"{coordinate} centre",
            )
            for coordinate in COORDINATE_ORDER
        ),
        half_width=_parse_hex_fraction(
            request_source["half_width_binary64_hex"], label="half width"
        ),
        transverse_period=Fraction(1),
        source_sha256=ACCEPTED_ANALYTIC_SOURCE_SHA256,
    )
    rows = manifest.get("rows")
    if type(rows) is not list or len(rows) != 12:
        raise ProductionInitialStreamFailure("bundle row list is invalid")
    ordered_relations: list[str] = []
    core_rows = f0.physical_configuration_specs_v2()
    for index, summary in enumerate(rows):
        core_row = core_rows[index]
        summary = _require_exact_keys(summary, _ROW_SUMMARY_KEYS, label="row summary")
        if (
            type(summary) is not dict
            or summary.get("configuration_index") != index
            or summary.get("configuration_label") != core_row.label
            or summary.get("expected_states") != core_row.expected_states
        ):
            raise ProductionInitialStreamFailure("row summary order drifted")
        _record_inventory_reference(
            summary["row_manifest"],
            inventory,
            referenced_paths,
            label="row manifest file",
        )
        row_manifest = _parse_canonical_json(
            _read_bound_inventory_file(
                root,
                summary["row_manifest"],
                inventory,
                maximum_bytes=2_000_000,
            ),
            label="row manifest",
        )
        row_manifest = _require_exact_keys(row_manifest, _ROW_MANIFEST_KEYS, label="row manifest")
        row_axes = row_manifest.get("axes")
        row_marginals = row_manifest.get("initial_marginals")
        if (
            type(row_axes) is not list
            or type(row_marginals) is not list
            or any(type(entry) is not dict for entry in (*row_axes, *row_marginals))
        ):
            raise ProductionInitialStreamFailure("row axis/marginal arrays are invalid")
        if (
            row_manifest.get("schema") != ROW_SCHEMA
            or row_manifest.get("configuration_index") != index
            or row_manifest.get("configuration_label") != summary["configuration_label"]
            or row_manifest.get("row_relation_sha256") != summary["row_relation_sha256"]
            or row_manifest.get("configuration_sha256") != ACCEPTED_CONFIGURATION_SHA256
            or row_manifest.get("expected_states") != core_row.expected_states
            or row_manifest.get("status") != "PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0"
            or row_manifest.get("flags")
            != {
                "analytic_source_to_sparse_box_producer_consistent": True,
                "free_axis_geometry_rate_producer_consistent": True,
                "full_operator_bound": False,
                "independent_geometry_relation_replay": False,
                "independent_source_box_replay": False,
                "killing_contact_geometry_bound": False,
                "positive_budget_executed": False,
            }
            or [entry.get("coordinate") for entry in row_axes] != list(COORDINATE_ORDER)
            or [entry.get("coordinate") for entry in row_marginals] != list(COORDINATE_ORDER)
        ):
            raise ProductionInitialStreamFailure("row manifest summary binding drifted")
        expected_axes = _build_control_free_axes(
            request_family["configurations"][index], request_family["dynamics"]
        )
        expected_profiles = _build_marginals(expected_axes, request_law)
        expected_sparse = _build_sparse_component_box(expected_profiles)
        for axis_entry, expected_axis in zip(row_axes, expected_axes, strict=True):
            _require_exact_keys(axis_entry, _AXIS_ENTRY_KEYS, label="axis entry")
            if type(axis_entry["rates"]) is not dict or set(axis_entry["rates"]) != {
                "backward",
                "forward",
                "stationary_mass",
            }:
                raise ProductionInitialStreamFailure("axis rate key set drifted")
            for rate_entry in axis_entry["rates"].values():
                _require_exact_keys(rate_entry, _RATE_ENTRY_KEYS, label="rate entry")
            _record_inventory_reference(
                axis_entry["partition_file"],
                inventory,
                referenced_paths,
                label="partition file",
            )
            partition_source = _read_bound_inventory_file(
                root,
                axis_entry["partition_file"],
                inventory,
                maximum_bytes=2_000_000,
            )
            partition = _validate_partition_payload(
                _parse_canonical_json(partition_source, label="axis partition")
            )
            if partition_source != _canonical_json_bytes(_partition_payload(expected_axis)):
                raise ProductionInitialStreamFailure(
                    "axis partition differs from accepted row reconstruction"
                )
            if partition["coordinate"] != axis_entry["coordinate"]:
                raise ProductionInitialStreamFailure("axis partition coordinate binding drifted")
            decoded_rates: dict[str, tuple[f0.OutwardInterval, ...]] = {}
            for direction, rate in axis_entry["rates"].items():
                _record_inventory_reference(
                    rate["file"],
                    inventory,
                    referenced_paths,
                    label="rate file",
                )
                raw = _read_bound_inventory_file(
                    root,
                    rate["file"],
                    inventory,
                    maximum_bytes=10_000_000,
                )
                intervals = _parse_interval_raw(raw, rate["manifest"])
                if len(intervals) != partition["size"]:
                    raise ProductionInitialStreamFailure("axis rate/partition size drifted")
                expected_intervals = {
                    "forward": expected_axis.forward_rates,
                    "backward": expected_axis.backward_rates,
                    "stationary_mass": expected_axis.stationary_masses,
                }.get(direction)
                if expected_intervals is None or raw != _interval_raw_bytes(
                    expected_intervals, label=f"expected {expected_axis.name} {direction}"
                ):
                    raise ProductionInitialStreamFailure(
                        "axis rate differs from accepted row reconstruction"
                    )
                expected_role = f"control_free_axis_{axis_entry['coordinate']}_{direction}"
                if rate["manifest"]["role"] != expected_role:
                    raise ProductionInitialStreamFailure("axis rate role binding drifted")
                decoded_rates[direction] = intervals
            if set(decoded_rates) != {"backward", "forward", "stationary_mass"}:
                raise ProductionInitialStreamFailure("axis rate direction set drifted")
            if not partition["periodic"] and (
                decoded_rates["backward"][0].upper != 0.0
                or decoded_rates["forward"][-1].upper != 0.0
            ):
                raise ProductionInitialStreamFailure("reflecting boundary rate drifted")
            edges = (
                range(partition["size"]) if partition["periodic"] else range(partition["size"] - 1)
            )
            for left in edges:
                right = (left + 1) % partition["size"]
                lhs = decoded_rates["stationary_mass"][left].multiply_nonnegative(
                    decoded_rates["forward"][left]
                )
                rhs = decoded_rates["stationary_mass"][right].multiply_nonnegative(
                    decoded_rates["backward"][right]
                )
                if max(lhs.lower_fraction, rhs.lower_fraction) > min(
                    lhs.upper_fraction, rhs.upper_fraction
                ):
                    raise ProductionInitialStreamFailure("file-backed detailed balance drifted")
            relation = {
                "coordinate": axis_entry["coordinate"],
                "partition_sha256": axis_entry["partition_file"]["sha256"],
                "rate_raw_sha256s": {
                    name: axis_entry["rates"][name]["file"]["sha256"]
                    for name in sorted(axis_entry["rates"])
                },
            }
            if axis_entry["axis_relation_sha256"] != _domain_digest(
                b"production-initial-axis-geometry-rate-relation-v1\0", relation
            ):
                raise ProductionInitialStreamFailure("axis geometry/rate relation digest drifted")
        for marginal, expected_profile in zip(row_marginals, expected_profiles, strict=True):
            _require_exact_keys(marginal, _MARGINAL_ENTRY_KEYS, label="initial marginal entry")
            _record_inventory_reference(
                marginal["file"],
                inventory,
                referenced_paths,
                label="marginal file",
            )
            raw = _read_bound_inventory_file(
                root,
                marginal["file"],
                inventory,
                maximum_bytes=10_000_000,
            )
            intervals = _parse_interval_raw(raw, marginal["manifest"])
            if raw != _interval_raw_bytes(
                expected_profile.mass_intervals,
                label=f"expected {marginal['coordinate']} marginal",
            ):
                raise ProductionInitialStreamFailure(
                    "initial marginal differs from accepted source reconstruction"
                )
            active = [i for i, entry in enumerate(intervals) if entry.upper > 0.0]
            if active != marginal["active_indices"]:
                raise ProductionInitialStreamFailure("marginal active-index proof drifted")
        sparse_manifest = row_manifest["sparse_component_box"]
        _record_inventory_reference(
            sparse_manifest["file"],
            inventory,
            referenced_paths,
            label="sparse file",
        )
        sparse_raw = _read_bound_inventory_file(
            root,
            sparse_manifest["file"],
            inventory,
            maximum_bytes=10_000_000,
        )
        if sparse_raw != _sparse_raw(expected_sparse):
            raise ProductionInitialStreamFailure(
                "sparse component box differs from accepted source reconstruction"
            )
        sparse = _parse_sparse_raw(sparse_raw, sparse_manifest)
        marginals = [
            _parse_interval_raw(
                _read_bound_inventory_file(
                    root,
                    entry["file"],
                    inventory,
                    maximum_bytes=10_000_000,
                ),
                entry["manifest"],
            )
            for entry in row_manifest["initial_marginals"]
        ]
        active_product = tuple(
            (i * sparse.shape[1] + j) * sparse.shape[2] + k
            for i, j, k in product(
                *(
                    tuple(n for n, entry in enumerate(axis) if entry.upper > 0.0)
                    for axis in marginals
                )
            )
        )
        if active_product != tuple(index_value for index_value, _ in sparse.records):
            raise ProductionInitialStreamFailure("sparse implicit-zero Cartesian proof drifted")
        expected_records = tuple(
            (
                (i * sparse.shape[1] + j) * sparse.shape[2] + k,
                marginals[0][i]
                .multiply_nonnegative(marginals[1][j])
                .multiply_nonnegative(marginals[2][k]),
            )
            for i, j, k in product(
                *(
                    tuple(n for n, entry in enumerate(axis) if entry.upper > 0.0)
                    for axis in marginals
                )
            )
        )
        if expected_records != sparse.records:
            raise ProductionInitialStreamFailure("sparse component product endpoints drifted")
        if sparse.state_count != core_row.expected_states or sparse.shape != (
            core_row.midpoint_size,
            core_row.relative_size,
            core_row.transverse_size,
        ):
            raise ProductionInitialStreamFailure("sparse component shape/spec binding drifted")
        source_box_relation = {
            "analytic_source_sha256": ACCEPTED_ANALYTIC_SOURCE_SHA256,
            "configuration_sha256": ACCEPTED_CONFIGURATION_SHA256,
            "marginal_raw_sha256s": [
                entry["file"]["sha256"] for entry in row_manifest["initial_marginals"]
            ],
            "sparse_raw_sha256": sparse_manifest["file"]["sha256"],
            "dense_expansion_sha256": sparse.dense_be_sha256,
            "shape": list(sparse.shape),
            "tensor_order": TENSOR_ORDER,
        }
        if row_manifest["source_box_relation_sha256"] != _domain_digest(
            b"production-initial-source-box-relation-v1\0", source_box_relation
        ):
            raise ProductionInitialStreamFailure("source/box relation digest drifted")
        row_relation = _domain_digest(
            b"production-initial-row-relation-v1\0",
            {
                "axis_relation_sha256s": [
                    entry["axis_relation_sha256"] for entry in row_manifest["axes"]
                ],
                "configuration_index": index,
                "configuration_label": row_manifest["configuration_label"],
                "source_box_relation_sha256": row_manifest["source_box_relation_sha256"],
            },
        )
        if row_relation != row_manifest["row_relation_sha256"]:
            raise ProductionInitialStreamFailure("row relation digest drifted")
        ordered_relations.append(row_relation)
    if referenced_paths != set(inventory):
        raise ProductionInitialStreamFailure("inventory/reference graph drifted")
    family_relation = _domain_digest(
        b"production-initial-family-relation-v1\0",
        {
            "analytic_source_sha256": ACCEPTED_ANALYTIC_SOURCE_SHA256,
            "configuration_sha256": ACCEPTED_CONFIGURATION_SHA256,
            "ordered_row_relation_sha256s": ordered_relations,
        },
    )
    if family_relation != manifest["family_relation_sha256"]:
        raise ProductionInitialStreamFailure("family relation digest drifted")
    if manifest.get("flags") != _BUNDLE_FLAGS:
        raise ProductionInitialStreamFailure("bundle non-promotion flags drifted")
    return manifest


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    produce = subparsers.add_parser("produce")
    produce.add_argument("--report-root", type=Path, required=True)
    produce.add_argument("--output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--bundle", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.command == "produce":
        manifest = produce_bundle(arguments.report_root, arguments.output)
    else:
        manifest = verify_bundle(arguments.bundle)
    print(_canonical_json_bytes({"status": manifest["status"]}).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
