"""Separate deterministic rebuild of the 12-row source/axis bundle.

This verifier intentionally does not import the producer module.  Starting
only from the request files retained in a bundle, it reconstructs every exact
partition JSON byte, every big-endian free-rate and stationary-mass endpoint,
every analytic initial marginal, every sparse component record, the virtual
dense stream digests, and all row/family relation digests.

It uses the same frozen finite-volume and directed-MPFR numerical core, so the
result is a separate artifact/relationship implementation but not an
independent numerical or semantic implementation.  It does not construct a
killing array, packed kernel, propagation result, topology result, F0, or F1.
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
from fractions import Fraction
from itertools import product
from pathlib import Path, PurePosixPath
from typing import Final, Sequence

_CODE_DIRECTORY = Path(__file__).resolve().parent
if str(_CODE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(_CODE_DIRECTORY))

import rate_defined_tensor_f0 as f0  # noqa: E402

BUNDLE_SCHEMA: Final = "encounter_control_free_production_initial_stream_v1"
ROW_SCHEMA: Final = "encounter_control_free_production_initial_row_v1"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"
RAW_SCHEMA: Final = "encounter_big_endian_binary64_interval_file_v1"
SPARSE_SCHEMA: Final = "encounter_sparse_component_interval_box_v1"
RECEIPT_SCHEMA: Final = "encounter_control_free_production_initial_relational_rebuild_v1"
BUNDLE_STATUS: Final = (
    "PASS_CONTROL_FREE_12_ROW_FILE_BACKED_PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0_NOT_F1"
)
RECEIPT_STATUS: Final = (
    "PASS_12_ROW_DETERMINISTIC_RELATIONAL_REBUILD_SAME_NUMERICAL_CORE_"
    "NOT_INDEPENDENT_SEMANTIC_NOT_F0_NOT_F1"
)
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
ANALYTIC_SOURCE_SHA256: Final = "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
F0_SOURCE_SHA256: Final = "321f12aa8a5df44ca9c9162704cccd0f2c526abf9577832b4824538b0afdb8e5"
TENSOR_ORDER: Final = "C:midpoint_outer_relative_parallel_middle_transverse_inner"
COORDINATES: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
PANELS_PER_UNIT: Final = 16_384
PRECISION_BITS: Final = 192
SPARSE_HEADER: Final = struct.Struct(">8sIIQQQQQII")
SPARSE_RECORD: Final = struct.Struct(">Qdd")
SPARSE_MAGIC: Final = b"ECSPBX01"
ZERO_PAIR: Final = struct.pack(">dd", 0.0, 0.0)
ZERO_BLOCK_STATES: Final = 65_536

_SOURCE_LAW: Final = {
    "analytic_total_mass_exact": "1/1",
    "construction": "independent_product_of_three_analytically_normalized_compact_bumps",
    "coordinate_order": list(COORDINATES),
    "half_width_binary64_hex": "0x1.47ae147ae147bp-6",
    "marginal_density": "b((x-c)/h)/(h*I_b)",
    "normalization": "I_b=integral_-1^1_b(u)_du",
    "periodic_coordinate": "relative_perpendicular",
    "periodic_wrap": "sum_over_periodic_images_before_cell_integration",
    "physical_dimension": 2,
    "quotient_dimension": 3,
    "schema": "encounter_physical_initial_analytic_source_v1",
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


class ProductionInitialRebuildFailure(RuntimeError):
    """Fail-closed error for the separate deterministic rebuild."""


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha(_read(path))


def _canonical(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise ProductionInitialRebuildFailure("JSON contains a duplicate/invalid key")
        result[key] = value
    return result


def _reject_float(token: str) -> object:
    raise ProductionInitialRebuildFailure(f"JSON floating token is forbidden: {token}")


def _parse(source: bytes, *, canonical: bool, label: str) -> object:
    try:
        payload = json.loads(
            source.decode("ascii"),
            object_pairs_hook=_strict_object,
            parse_float=_reject_float,
            parse_constant=_reject_float,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProductionInitialRebuildFailure(f"{label} is not strict ASCII JSON") from error
    if canonical and _canonical(payload) != source:
        raise ProductionInitialRebuildFailure(f"{label} is not canonical JSON")
    return payload


def _read(path: Path, *, maximum: int = 10_000_000) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ProductionInitialRebuildFailure(f"missing required file: {path}") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise ProductionInitialRebuildFailure(f"unsafe or oversized file: {path}")
        chunks: list[bytes] = []
        observed = 0
        while block := os.read(descriptor, min(1 << 20, maximum + 1 - observed)):
            chunks.append(block)
            observed += len(block)
            if observed > maximum:
                raise ProductionInitialRebuildFailure(f"oversized file: {path}")
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
            raise ProductionInitialRebuildFailure(f"file changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _hex(value: object, *, label: str) -> Fraction:
    if type(value) is not str:
        raise ProductionInitialRebuildFailure(f"{label} is not binary64 hex")
    try:
        parsed = float.fromhex(value)
    except ValueError as error:
        raise ProductionInitialRebuildFailure(f"{label} is invalid binary64 hex") from error
    if (
        not math.isfinite(parsed)
        or parsed.hex() != value
        or (parsed == 0.0 and math.copysign(1.0, parsed) < 0)
    ):
        raise ProductionInitialRebuildFailure(f"{label} is noncanonical binary64")
    return Fraction.from_float(parsed)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _digest(domain: bytes, payload: object) -> str:
    if not domain.endswith(b"\0"):
        raise ProductionInitialRebuildFailure("digest domain is not terminated")
    return _sha(domain + _canonical(payload))


def _entry(path: str, source: bytes) -> dict[str, object]:
    return {"byte_length": len(source), "path": path, "sha256": _sha(source)}


def _slug(label: str) -> str:
    value = label.lower().replace("+", "_plus").replace("/", "_")
    return "_".join(
        part
        for part in "".join(character if character.isalnum() else "_" for character in value).split(
            "_"
        )
        if part
    )


def _validate_configuration(payload: object) -> dict[str, object]:
    if type(payload) is not dict:
        raise ProductionInitialRebuildFailure("configuration request is not an object")
    if (
        payload.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or payload.get("configuration_order") != list(f0.PHYSICAL_CONFIGURATION_ORDER_V2)
        or payload.get("configuration_count") != 12
        or payload.get("total_state_workload") != 34_787_462
        or payload.get("contains_budget_value") is not False
        or payload.get("contains_control_values") is not False
        or payload.get("authorizes_scientific_execution") is not False
        or payload.get("coordinate_order") != list(COORDINATES)
    ):
        raise ProductionInitialRebuildFailure("configuration request boundary drifted")
    rows = payload.get("configurations")
    core_rows = f0.physical_configuration_specs_v2()
    if type(rows) is not list or len(rows) != 12:
        raise ProductionInitialRebuildFailure("configuration request row count drifted")
    for row, core in zip(rows, core_rows, strict=True):
        if (
            row.get("label") != core.label
            or row.get("purpose") != core.purpose
            or row.get("shape") != [core.midpoint_size, core.relative_size, core.transverse_size]
            or row.get("expected_states") != core.expected_states
            or _hex(row["midpoint"]["lower_binary64_hex"], label="M lower") != core.midpoint_lower
            or _hex(row["midpoint"]["upper_binary64_hex"], label="M upper") != core.midpoint_upper
            or _hex(row["relative_parallel"]["lower_binary64_hex"], label="R lower")
            != core.relative_lower
            or _hex(row["relative_parallel"]["upper_binary64_hex"], label="R upper")
            != core.relative_upper
        ):
            raise ProductionInitialRebuildFailure(f"configuration row drifted: {core.label}")
    return payload


def _axes(row: dict[str, object], dynamics: dict[str, object]) -> tuple[f0.TensorAxis, ...]:
    particle = _hex(dynamics["particle_diffusion_binary64_hex"], label="diffusion")
    stiffness = _hex(dynamics["ou_stiffness_binary64_hex"], label="stiffness")
    mean = _hex(dynamics["ou_mean_binary64_hex"], label="mean")
    midpoint_diffusion = particle / 2
    relative_diffusion = 2 * particle

    def make_reflecting(
        name: str, spec: dict[str, object], centre: Fraction, diffusion: Fraction
    ) -> f0.TensorAxis:
        lower = _hex(spec["lower_binary64_hex"], label=f"{name} lower")
        upper = _hex(spec["upper_binary64_hex"], label=f"{name} upper")
        size = spec["size"]

        def potential(point: Fraction) -> Fraction:
            return stiffness * (point - centre) ** 2 / (2 * diffusion)

        if spec["alignment"] == "vertex_centred_reflecting_dual":
            step = (upper - lower) / (size - 1)
            positions = tuple(lower + index * step for index in range(size))
            return f0.build_reflecting_sg_axis(
                name,
                positions,
                tuple(potential(point) for point in positions),
                diffusion,
                precision_bits=PRECISION_BITS,
            )
        return f0.build_cell_centred_reflecting_sg_axis(
            name,
            lower,
            upper,
            size,
            potential,
            diffusion,
            precision_bits=PRECISION_BITS,
        )

    midpoint = make_reflecting("midpoint", row["midpoint"], mean, midpoint_diffusion)
    relative = make_reflecting(
        "relative_parallel", row["relative_parallel"], Fraction(0), relative_diffusion
    )
    transverse_spec = row["relative_perpendicular"]
    transverse = f0.build_periodic_diffusion_axis(
        "relative_perpendicular",
        transverse_spec["size"],
        Fraction(1),
        relative_diffusion,
        half_cell_shift=transverse_spec["alignment"] == "cell_centred_periodic_half_shift",
        domain_start=Fraction(-1, 2),
    )
    return midpoint, relative, transverse


def _partition(axis: f0.TensorAxis) -> bytes:
    payload = {
        "cell_segments_exact": [
            [[_fraction_text(lower), _fraction_text(upper)] for lower, upper in cell]
            for cell in axis.cell_segments
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
    return _canonical(payload)


def _interval_bytes(intervals: Sequence[f0.OutwardInterval]) -> bytes:
    raw = bytearray(16 * len(intervals))
    for index, interval in enumerate(intervals):
        interval.require_nonnegative("relational rebuild interval")
        for endpoint in (interval.lower, interval.upper):
            if not math.isfinite(endpoint) or (
                endpoint == 0.0 and math.copysign(1.0, endpoint) < 0
            ):
                raise ProductionInitialRebuildFailure("noncanonical interval endpoint")
        struct.pack_into(">dd", raw, 16 * index, interval.lower, interval.upper)
    return bytes(raw)


def _raw_manifest(raw: bytes, role: str, size: int) -> dict[str, object]:
    return {
        "byte_order": "big",
        "logical_shape": [size],
        "raw_byte_length": len(raw),
        "raw_sha256": _sha(raw),
        "record_count": size,
        "record_format": ">dd",
        "role": role,
        "schema": RAW_SCHEMA,
    }


def _dense_digest(states: int, records: Sequence[tuple[int, f0.OutwardInterval]]) -> str:
    digest = hashlib.sha256()
    block = ZERO_PAIR * ZERO_BLOCK_STATES
    cursor = 0

    def zeros(count: int) -> None:
        full, remainder = divmod(count, ZERO_BLOCK_STATES)
        for _ in range(full):
            digest.update(block)
        if remainder:
            digest.update(ZERO_PAIR * remainder)

    for index, interval in records:
        zeros(index - cursor)
        digest.update(struct.pack(">dd", interval.lower, interval.upper))
        cursor = index + 1
    zeros(states - cursor)
    return digest.hexdigest()


def _active_digest(records: Sequence[tuple[int, f0.OutwardInterval]]) -> str:
    digest = hashlib.sha256(b"production-initial-active-flat-indices-v1\0")
    for index, _ in records:
        digest.update(index.to_bytes(8, "big"))
    return digest.hexdigest()


def _profiles(
    axes: tuple[f0.TensorAxis, ...], source: dict[str, object]
) -> tuple[f0.NormalizedBumpProfile, ...]:
    centres = tuple(_hex(source["starts_binary64_hex"][name], label=name) for name in COORDINATES)
    half_width = _hex(source["half_width_binary64_hex"], label="half width")
    return tuple(
        f0.build_normalized_bump_profile(
            axis,
            centre=centres[index],
            half_width=half_width,
            period=Fraction(1) if axis.periodic else None,
            panels_per_unit=PANELS_PER_UNIT,
            precision_bits=PRECISION_BITS,
        )
        for index, axis in enumerate(axes)
    )


def _sparse(profiles: tuple[f0.NormalizedBumpProfile, ...]) -> tuple[bytes, dict[str, object]]:
    shape = tuple(len(profile.mass_intervals) for profile in profiles)
    active = tuple(
        tuple(index for index, interval in enumerate(profile.mass_intervals) if interval.upper > 0)
        for profile in profiles
    )
    records: list[tuple[int, f0.OutwardInterval]] = []
    for i, j, k in product(*active):
        interval = (
            profiles[0]
            .mass_intervals[i]
            .multiply_nonnegative(profiles[1].mass_intervals[j])
            .multiply_nonnegative(profiles[2].mass_intervals[k])
        )
        records.append(((i * shape[1] + j) * shape[2] + k, interval))
    states = math.prod(shape)
    raw = bytearray(
        SPARSE_HEADER.pack(
            SPARSE_MAGIC,
            1,
            3,
            states,
            len(records),
            shape[0],
            shape[1],
            shape[2],
            SPARSE_RECORD.size,
            1,
        )
    )
    for index, interval in records:
        raw.extend(SPARSE_RECORD.pack(index, interval.lower, interval.upper))
    lower = sum((entry.lower_fraction for _, entry in records), Fraction(0))
    upper = sum((entry.upper_fraction for _, entry in records), Fraction(0))
    return bytes(raw), {
        "active_component_count": len(records),
        "active_index_sha256": _active_digest(records),
        "dense_expansion_byte_length": 16 * states,
        "dense_expansion_record_format": ">dd",
        "dense_expansion_sha256": _dense_digest(states, records),
        "implicit_background": "positive_zero_interval_[0x0.0p+0,0x0.0p+0]",
        "lower_mass_exact": _fraction_text(lower),
        "record_format": ">Qdd",
        "schema": SPARSE_SCHEMA,
        "shape": list(shape),
        "state_count": states,
        "tensor_order": TENSOR_ORDER,
        "upper_mass_exact": _fraction_text(upper),
    }


def _expected_row(
    index: int,
    row: dict[str, object],
    dynamics: dict[str, object],
    source: dict[str, object],
    expected_files: dict[str, bytes],
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    directory = f"rows/{index:02d}_{_slug(row['label'])}"

    def emit(name: str, raw: bytes) -> dict[str, object]:
        path = f"{directory}/{name}"
        if path in expected_files:
            raise ProductionInitialRebuildFailure("duplicate expected file path")
        expected_files[path] = raw
        return _entry(path, raw)

    axes = _axes(row, dynamics)
    profiles = _profiles(axes, source)
    axis_entries: list[dict[str, object]] = []
    marginal_entries: list[dict[str, object]] = []
    for axis, profile in zip(axes, profiles, strict=True):
        partition_file = emit(f"{axis.name}.partition.json", _partition(axis))
        rates: dict[str, object] = {}
        for direction, intervals in (
            ("forward", axis.forward_rates),
            ("backward", axis.backward_rates),
            ("stationary_mass", axis.stationary_masses),
        ):
            raw = _interval_bytes(intervals)
            file_entry = emit(f"{axis.name}.{direction}.be64", raw)
            rates[direction] = {
                "file": file_entry,
                "manifest": _raw_manifest(
                    raw, f"control_free_axis_{axis.name}_{direction}", axis.size
                ),
            }
        relation = {
            "coordinate": axis.name,
            "partition_sha256": partition_file["sha256"],
            "rate_raw_sha256s": {name: rates[name]["file"]["sha256"] for name in sorted(rates)},
        }
        axis_entries.append(
            {
                "axis_relation_sha256": _digest(
                    b"production-initial-axis-geometry-rate-relation-v1\0", relation
                ),
                "coordinate": axis.name,
                "partition_file": partition_file,
                "rates": rates,
            }
        )
        marginal_raw = _interval_bytes(profile.mass_intervals)
        marginal_file = emit(f"{axis.name}.initial_marginal.be64", marginal_raw)
        marginal_entries.append(
            {
                "active_indices": [
                    n for n, interval in enumerate(profile.mass_intervals) if interval.upper > 0
                ],
                "coordinate": axis.name,
                "file": marginal_file,
                "manifest": _raw_manifest(
                    marginal_raw, f"analytic_initial_marginal_{axis.name}", axis.size
                ),
            }
        )
    sparse_raw, sparse_core = _sparse(profiles)
    sparse_file = emit("initial_component_box.sparse.be64", sparse_raw)
    sparse_manifest = {**sparse_core, "file": sparse_file}
    source_relation = {
        "analytic_source_sha256": ANALYTIC_SOURCE_SHA256,
        "configuration_sha256": CONFIGURATION_SHA256,
        "marginal_raw_sha256s": [entry["file"]["sha256"] for entry in marginal_entries],
        "sparse_raw_sha256": sparse_file["sha256"],
        "dense_expansion_sha256": sparse_core["dense_expansion_sha256"],
        "shape": sparse_core["shape"],
        "tensor_order": TENSOR_ORDER,
    }
    source_relation_sha = _digest(b"production-initial-source-box-relation-v1\0", source_relation)
    row_relation = _digest(
        b"production-initial-row-relation-v1\0",
        {
            "axis_relation_sha256s": [entry["axis_relation_sha256"] for entry in axis_entries],
            "configuration_index": index,
            "configuration_label": row["label"],
            "source_box_relation_sha256": source_relation_sha,
        },
    )
    row_manifest = {
        "axes": axis_entries,
        "configuration_index": index,
        "configuration_label": row["label"],
        "configuration_sha256": CONFIGURATION_SHA256,
        "expected_states": row["expected_states"],
        "flags": {
            "analytic_source_to_sparse_box_producer_consistent": True,
            "free_axis_geometry_rate_producer_consistent": True,
            "full_operator_bound": False,
            "independent_geometry_relation_replay": False,
            "independent_source_box_replay": False,
            "killing_contact_geometry_bound": False,
            "positive_budget_executed": False,
        },
        "initial_marginals": marginal_entries,
        "row_relation_sha256": row_relation,
        "schema": ROW_SCHEMA,
        "source_box_relation_sha256": source_relation_sha,
        "sparse_component_box": sparse_manifest,
        "status": "PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0",
    }
    row_bytes = _canonical(row_manifest)
    row_file = emit("row.json", row_bytes)
    summary = {
        "configuration_index": index,
        "configuration_label": row["label"],
        "expected_states": row["expected_states"],
        "row_manifest": row_file,
        "row_relation_sha256": row_relation,
    }
    receipt_row = {
        "configuration_index": index,
        "configuration_label": row["label"],
        "exact_axis_partition_file_count": 3,
        "exact_be_interval_file_count": 12,
        "expected_states": row["expected_states"],
        "row_relation_sha256": row_relation,
        "source_box_relation_sha256": source_relation_sha,
        "tensor_shape": sparse_core["shape"],
    }
    return row_manifest, summary, receipt_row


def _actual_inventory(root: Path, manifest: dict[str, object]) -> dict[str, bytes]:
    inventory = manifest.get("file_inventory")
    if type(inventory) is not list:
        raise ProductionInitialRebuildFailure("bundle inventory is invalid")
    result: dict[str, bytes] = {}
    for entry in inventory:
        if type(entry) is not dict or set(entry) != {"byte_length", "path", "sha256"}:
            raise ProductionInitialRebuildFailure("bundle inventory entry is invalid")
        path = entry["path"]
        pure = PurePosixPath(path)
        if type(path) is not str or pure.is_absolute() or ".." in pure.parts or path in result:
            raise ProductionInitialRebuildFailure("bundle inventory path is unsafe/duplicate")
        source = _read(root / Path(*pure.parts))
        if len(source) != entry["byte_length"] or not hmac.compare_digest(
            _sha(source), entry["sha256"]
        ):
            raise ProductionInitialRebuildFailure(f"bundle inventory bytes changed: {path}")
        result[path] = source
    if list(result) != sorted(result):
        raise ProductionInitialRebuildFailure("bundle inventory is not sorted")
    actual_paths: set[str] = set()
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            raise ProductionInitialRebuildFailure("bundle contains a symlink")
        if candidate.is_file():
            actual_paths.add(candidate.relative_to(root).as_posix())
    if actual_paths != set(result) | {"bundle.json"}:
        raise ProductionInitialRebuildFailure("bundle file set is incomplete or enlarged")
    return result


def rebuild_bundle(bundle: Path) -> dict[str, object]:
    """Reconstruct the complete deterministic bundle and return a scoped receipt."""

    if bundle.is_symlink():
        raise ProductionInitialRebuildFailure("bundle root is a symlink")
    bundle = bundle.resolve()
    if not bundle.is_dir():
        raise ProductionInitialRebuildFailure("bundle root is not a directory")
    if not hmac.compare_digest(_sha_file(Path(f0.__file__).resolve()), F0_SOURCE_SHA256):
        raise ProductionInitialRebuildFailure("accepted numerical core bytes changed")
    bundle_bytes = _read(bundle / "bundle.json", maximum=2_000_000)
    manifest = _parse(bundle_bytes, canonical=True, label="bundle manifest")
    if type(manifest) is not dict or manifest.get("schema") != BUNDLE_SCHEMA:
        raise ProductionInitialRebuildFailure("bundle schema drifted")
    actual_files = _actual_inventory(bundle, manifest)
    configuration_bytes = actual_files.get("request/configuration.json")
    source_bytes = actual_files.get("request/analytic_source.json")
    if (
        configuration_bytes is None
        or source_bytes is None
        or not hmac.compare_digest(_sha(configuration_bytes), CONFIGURATION_SHA256)
        or not hmac.compare_digest(_sha(source_bytes), ANALYTIC_SOURCE_SHA256)
    ):
        raise ProductionInitialRebuildFailure("request-only root bytes drifted")
    configuration = _validate_configuration(
        _parse(configuration_bytes, canonical=True, label="configuration request")
    )
    source = _parse(source_bytes, canonical=False, label="analytic source request")
    if source != _SOURCE_LAW:
        raise ProductionInitialRebuildFailure("analytic source request law drifted")

    expected_files = {
        "request/analytic_source.json": source_bytes,
        "request/configuration.json": configuration_bytes,
    }
    row_summaries: list[dict[str, object]] = []
    receipt_rows: list[dict[str, object]] = []
    for index, row in enumerate(configuration["configurations"]):
        _, summary, receipt_row = _expected_row(
            index,
            row,
            configuration["dynamics"],
            source,
            expected_files,
        )
        row_summaries.append(summary)
        receipt_rows.append(receipt_row)
    if set(actual_files) != set(expected_files):
        raise ProductionInitialRebuildFailure("expected/actual file path sets disagree")
    for path, expected in expected_files.items():
        if not hmac.compare_digest(expected, actual_files[path]):
            raise ProductionInitialRebuildFailure(f"relational rebuild byte mismatch: {path}")
    inventory = [_entry(path, expected_files[path]) for path in sorted(expected_files)]
    family_relation = _digest(
        b"production-initial-family-relation-v1\0",
        {
            "analytic_source_sha256": ANALYTIC_SOURCE_SHA256,
            "configuration_sha256": CONFIGURATION_SHA256,
            "ordered_row_relation_sha256s": [row["row_relation_sha256"] for row in row_summaries],
        },
    )
    expected_manifest = {
        "analytic_source_sha256": ANALYTIC_SOURCE_SHA256,
        "configuration_count": 12,
        "configuration_sha256": CONFIGURATION_SHA256,
        "family_relation_sha256": family_relation,
        "file_inventory": inventory,
        "flags": {
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
        },
        "method": {
            "dense_component_box_materialized": False,
            "marginal_endpoint_record_format": ">dd",
            "panels_per_unit": PANELS_PER_UNIT,
            "precision_bits": PRECISION_BITS,
            "sparse_component_record_format": ">Qdd",
            "tensor_order": TENSOR_ORDER,
        },
        "rows": row_summaries,
        "schema": BUNDLE_SCHEMA,
        "status": BUNDLE_STATUS,
        "total_dense_expansion_byte_length": 556_599_392,
        "total_state_workload": 34_787_462,
    }
    if manifest != expected_manifest or bundle_bytes != _canonical(expected_manifest):
        raise ProductionInitialRebuildFailure("complete reconstructed bundle manifest disagrees")
    receipt_core = {
        "analytic_source_sha256": ANALYTIC_SOURCE_SHA256,
        "bundle_manifest_sha256": _sha(bundle_bytes),
        "configuration_sha256": CONFIGURATION_SHA256,
        "family_relation_sha256": family_relation,
        "file_count_reconstructed": len(expected_files),
        "flags": {
            "all_twelve_rows_rebuilt": True,
            "artifact_parser_implementation_separate": True,
            "authorizes_scientific_execution": False,
            "clean_process_observed": False,
            "deterministic_relational_rebuild_complete": True,
            "exact_bundle_bytes_reconstructed": True,
            "free_axis_geometry_rate_relational_rebuild_complete": True,
            "fresh_process": False,
            "full_operator_bound": False,
            "independent_numerical_implementation": False,
            "independent_semantic_replay_complete": False,
            "killing_contact_geometry_bound": False,
            "positive_budget_executed": False,
            "production_resource_gate": False,
            "science_executed": False,
            "source_box_relational_rebuild_complete": True,
            "topology_complete": False,
        },
        "numerical_core_sha256": F0_SOURCE_SHA256,
        "rebuild_source_sha256": _sha(_read(Path(__file__).resolve())),
        "rows": receipt_rows,
        "schema": RECEIPT_SCHEMA,
        "status": RECEIPT_STATUS,
        "total_state_workload": 34_787_462,
    }
    return {
        **receipt_core,
        "receipt_sha256": _digest(
            b"production-initial-relational-rebuild-receipt-v1\0", receipt_core
        ),
    }


def write_receipt(bundle: Path, output: Path) -> dict[str, object]:
    receipt = rebuild_bundle(bundle)
    if output.exists() or output.is_symlink():
        raise ProductionInitialRebuildFailure("receipt output already exists")
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
    receipt = write_receipt(arguments.bundle, arguments.receipt)
    print(
        _canonical(
            {"receipt_sha256": receipt["receipt_sha256"], "status": receipt["status"]}
        ).decode("ascii"),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
