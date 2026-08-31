"""Independent semantic verifier for the control-free 12-row bundle.

This file does not import the finite-volume producer, its frozen numerical
core, the deterministic rebuild, packed kernels, or any of their tests.  It
reconstructs the exact partitions directly from the request JSON, implements
its own directed-MPFR Scharfetter--Gummel enclosures, and uses a finer
validated composite-Simpson rule for the compact-bump law.  Its enclosures
must be contained in the producer intervals for every free rate, stationary
mass, initial marginal, and active tensor component.

The receipt is scoped to source/partition/free-axis semantics.  It is not a
full operator, killing, propagation, topology, continuum, F0, or F1 result.
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
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path, PurePosixPath
from typing import Final, Iterable, Sequence

import gmpy2

SCHEMA: Final = "encounter_control_free_production_initial_independent_semantic_v1"
STATUS: Final = (
    "PASS_12_ROW_INDEPENDENT_SOURCE_PARTITION_FREE_AXIS_SEMANTICS_"
    "ONLY_NOT_FULL_OPERATOR_NOT_F0_NOT_F1"
)
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
ANALYTIC_SOURCE_SHA256: Final = "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
BUNDLE_SCHEMA: Final = "encounter_control_free_production_initial_stream_v1"
BUNDLE_STATUS: Final = (
    "PASS_CONTROL_FREE_12_ROW_FILE_BACKED_PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0_NOT_F1"
)
ROW_SCHEMA: Final = "encounter_control_free_production_initial_row_v1"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"
RAW_SCHEMA: Final = "encounter_big_endian_binary64_interval_file_v1"
SPARSE_SCHEMA: Final = "encounter_sparse_component_interval_box_v1"
COORDINATES: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
TENSOR_ORDER: Final = "C:midpoint_outer_relative_parallel_middle_transverse_inner"
INDEPENDENT_PRECISION_BITS: Final = 256
INDEPENDENT_PANELS_PER_UNIT: Final = 32_768
BUMP_FOURTH_BOUND: Final = Fraction(322_000)
SPARSE_HEADER: Final = struct.Struct(">8sIIQQQQQII")
SPARSE_RECORD: Final = struct.Struct(">Qdd")
SPARSE_MAGIC: Final = b"ECSPBX01"

_EXPECTED_LABELS: Final = (
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
)
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
_ROW_FLAGS: Final = {
    "analytic_source_to_sparse_box_producer_consistent": True,
    "free_axis_geometry_rate_producer_consistent": True,
    "full_operator_bound": False,
    "independent_geometry_relation_replay": False,
    "independent_source_box_replay": False,
    "killing_contact_geometry_bound": False,
    "positive_budget_executed": False,
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
_ROW_SUMMARY_KEYS: Final = {
    "configuration_index",
    "configuration_label",
    "expected_states",
    "row_manifest",
    "row_relation_sha256",
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
_RAW_KEYS: Final = {
    "byte_order",
    "logical_shape",
    "raw_byte_length",
    "raw_sha256",
    "record_count",
    "record_format",
    "role",
    "schema",
}
_SPARSE_KEYS: Final = {
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


class IndependentSemanticFailure(RuntimeError):
    """Fail-closed independent source/axis semantic verification error."""


@dataclass(frozen=True, slots=True)
class Interval:
    lower: float
    upper: float

    def __post_init__(self) -> None:
        if (
            not math.isfinite(self.lower)
            or not math.isfinite(self.upper)
            or self.lower > self.upper
            or self.lower < 0.0
            or (self.lower == 0.0 and math.copysign(1.0, self.lower) < 0)
            or (self.upper == 0.0 and math.copysign(1.0, self.upper) < 0)
        ):
            raise IndependentSemanticFailure("independent interval is noncanonical")

    @property
    def lower_fraction(self) -> Fraction:
        return Fraction.from_float(self.lower)

    @property
    def upper_fraction(self) -> Fraction:
        return Fraction.from_float(self.upper)

    @classmethod
    def from_bounds(cls, lower: Fraction, upper: Fraction) -> Interval:
        if lower < 0 or lower > upper:
            raise IndependentSemanticFailure("independent rational bounds are invalid")
        return cls(_float_fraction_lower(lower), _float_fraction_upper(upper))

    @classmethod
    def point(cls, value: Fraction) -> Interval:
        return cls.from_bounds(value, value)

    def add(self, other: Interval) -> Interval:
        return Interval.from_bounds(
            self.lower_fraction + other.lower_fraction,
            self.upper_fraction + other.upper_fraction,
        )

    def multiply(self, other: Interval) -> Interval:
        return Interval.from_bounds(
            self.lower_fraction * other.lower_fraction,
            self.upper_fraction * other.upper_fraction,
        )

    def scale(self, factor: Fraction) -> Interval:
        if factor < 0:
            raise IndependentSemanticFailure("independent interval scale is negative")
        return Interval.from_bounds(
            factor * self.lower_fraction,
            factor * self.upper_fraction,
        )

    def divide(self, denominator: Interval) -> Interval:
        if denominator.lower_fraction <= 0:
            raise IndependentSemanticFailure("independent denominator contains zero")
        return Interval.from_bounds(
            self.lower_fraction / denominator.upper_fraction,
            self.upper_fraction / denominator.lower_fraction,
        )


ZERO = Interval(0.0, 0.0)


@dataclass(frozen=True, slots=True)
class Axis:
    name: str
    size: int
    periodic: bool
    construction: str
    domain_start: Fraction
    domain_width: Fraction
    periodic_shift: Fraction
    positions: tuple[Fraction, ...]
    volumes: tuple[Fraction, ...]
    cells: tuple[tuple[tuple[Fraction, Fraction], ...], ...]
    forward: tuple[Interval, ...]
    backward: tuple[Interval, ...]
    stationary: tuple[Interval, ...]


def _sha(source: bytes) -> str:
    return hashlib.sha256(source).hexdigest()


def _canonical(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _digest(domain: bytes, payload: object) -> str:
    if not domain.endswith(b"\0"):
        raise IndependentSemanticFailure("digest domain is not terminated")
    return _sha(domain + _canonical(payload))


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise IndependentSemanticFailure("JSON has a duplicate or invalid key")
        result[key] = value
    return result


def _reject_float(token: str) -> object:
    raise IndependentSemanticFailure(f"JSON floating literal is forbidden: {token}")


def _parse(source: bytes, *, canonical: bool, label: str) -> object:
    try:
        payload = json.loads(
            source.decode("ascii"),
            object_pairs_hook=_strict_object,
            parse_float=_reject_float,
            parse_constant=_reject_float,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise IndependentSemanticFailure(f"{label} is not strict ASCII JSON") from error
    if canonical and _canonical(payload) != source:
        raise IndependentSemanticFailure(f"{label} is not canonical JSON")
    return payload


def _require_keys(payload: object, expected: set[str], *, label: str) -> dict[str, object]:
    if type(payload) is not dict or set(payload) != expected:
        raise IndependentSemanticFailure(f"{label} key set drifted")
    return payload


def _read(path: Path, *, maximum: int = 10_000_000) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise IndependentSemanticFailure(f"required file is unavailable: {path}") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise IndependentSemanticFailure(f"required file is unsafe/oversized: {path}")
        chunks: list[bytes] = []
        observed = 0
        while block := os.read(descriptor, min(1 << 20, maximum + 1 - observed)):
            chunks.append(block)
            observed += len(block)
            if observed > maximum:
                raise IndependentSemanticFailure(f"required file is oversized: {path}")
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
            raise IndependentSemanticFailure(f"required file changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _safe_path(root: Path, relative: object) -> Path:
    if type(relative) is not str:
        raise IndependentSemanticFailure("relative path type is invalid")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or pure.as_posix() != relative:
        raise IndependentSemanticFailure("relative path is unsafe")
    return root / Path(*pure.parts)


def _inventory(root: Path, manifest: dict[str, object]) -> dict[str, bytes]:
    entries = manifest.get("file_inventory")
    if type(entries) is not list or len(entries) != 206:
        raise IndependentSemanticFailure("bundle inventory is invalid")
    result: dict[str, bytes] = {}
    for entry in entries:
        if type(entry) is not dict or set(entry) != {"byte_length", "path", "sha256"}:
            raise IndependentSemanticFailure("bundle inventory entry is invalid")
        path = entry["path"]
        if type(path) is not str or path in result:
            raise IndependentSemanticFailure("bundle inventory path is invalid/duplicate")
        source = _read(_safe_path(root, path))
        if len(source) != entry["byte_length"] or not hmac.compare_digest(
            _sha(source), entry["sha256"]
        ):
            raise IndependentSemanticFailure(f"bundle inventory bytes changed: {path}")
        result[path] = source
    if list(result) != sorted(result):
        raise IndependentSemanticFailure("bundle inventory is not sorted")
    actual: set[str] = set()
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            raise IndependentSemanticFailure("bundle contains a symlink")
        if candidate.is_file():
            actual.add(candidate.relative_to(root).as_posix())
    if actual != set(result) | {"bundle.json"}:
        raise IndependentSemanticFailure("bundle file set drifted")
    return result


def _bound_file(entry: object, inventory: dict[str, bytes]) -> bytes:
    if type(entry) is not dict or set(entry) != {"byte_length", "path", "sha256"}:
        raise IndependentSemanticFailure("bound file entry is invalid")
    source = inventory.get(entry["path"])
    if (
        source is None
        or len(source) != entry["byte_length"]
        or not hmac.compare_digest(_sha(source), entry["sha256"])
    ):
        raise IndependentSemanticFailure("bound file entry disagrees with inventory")
    return source


def _bound_file_reference(
    entry: object,
    inventory: dict[str, bytes],
    referenced: set[str],
) -> bytes:
    current = _require_keys(entry, {"byte_length", "path", "sha256"}, label="bound file entry")
    relative = current["path"]
    if type(relative) is not str or relative not in inventory:
        raise IndependentSemanticFailure("bound file reference is absent from inventory")
    if relative in referenced:
        raise IndependentSemanticFailure(f"duplicate bound file reference: {relative}")
    referenced.add(relative)
    return _bound_file(current, inventory)


def _hex(value: object, *, label: str) -> Fraction:
    if type(value) is not str:
        raise IndependentSemanticFailure(f"{label} is not binary64 hex")
    try:
        parsed = float.fromhex(value)
    except ValueError as error:
        raise IndependentSemanticFailure(f"{label} is invalid binary64 hex") from error
    if (
        not math.isfinite(parsed)
        or parsed.hex() != value
        or (parsed == 0.0 and math.copysign(1.0, parsed) < 0)
    ):
        raise IndependentSemanticFailure(f"{label} is noncanonical binary64")
    return Fraction.from_float(parsed)


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _mpfr_fraction(value: Fraction, rounding: int) -> gmpy2.mpfr:
    with gmpy2.context(gmpy2.get_context(), precision=INDEPENDENT_PRECISION_BITS, round=rounding):
        return gmpy2.mpfr(value.numerator) / gmpy2.mpfr(value.denominator)


def _mpfr_float_lower(value: gmpy2.mpfr) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise IndependentSemanticFailure("independent MPFR lower is not finite")
    with gmpy2.context(gmpy2.get_context(), precision=INDEPENDENT_PRECISION_BITS):
        if gmpy2.mpfr(candidate) > value:
            candidate = math.nextafter(candidate, -math.inf)
    return candidate


def _mpfr_float_upper(value: gmpy2.mpfr) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise IndependentSemanticFailure("independent MPFR upper is not finite")
    with gmpy2.context(gmpy2.get_context(), precision=INDEPENDENT_PRECISION_BITS):
        if gmpy2.mpfr(candidate) < value:
            candidate = math.nextafter(candidate, math.inf)
    return candidate


def _float_fraction_lower(value: Fraction) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise IndependentSemanticFailure("independent fraction lower is not finite")
    if Fraction.from_float(candidate) > value:
        candidate = math.nextafter(candidate, -math.inf)
    return candidate


def _float_fraction_upper(value: Fraction) -> float:
    candidate = float(value)
    if not math.isfinite(candidate):
        raise IndependentSemanticFailure("independent fraction upper is not finite")
    if Fraction.from_float(candidate) < value:
        candidate = math.nextafter(candidate, math.inf)
    return candidate


def _exp_interval(value: Fraction) -> Interval:
    lower_input = _mpfr_fraction(value, gmpy2.RoundDown)
    upper_input = _mpfr_fraction(value, gmpy2.RoundUp)
    with gmpy2.context(
        gmpy2.get_context(), precision=INDEPENDENT_PRECISION_BITS, round=gmpy2.RoundDown
    ):
        lower = gmpy2.exp(lower_input)
    with gmpy2.context(
        gmpy2.get_context(), precision=INDEPENDENT_PRECISION_BITS, round=gmpy2.RoundUp
    ):
        upper = gmpy2.exp(upper_input)
    return Interval(_mpfr_float_lower(lower), _mpfr_float_upper(upper))


def _bernoulli_positive(value: Fraction) -> Interval:
    if value <= 0:
        raise IndependentSemanticFailure("positive Bernoulli input required")
    lower_input = _mpfr_fraction(value, gmpy2.RoundDown)
    upper_input = _mpfr_fraction(value, gmpy2.RoundUp)
    with gmpy2.context(
        gmpy2.get_context(), precision=INDEPENDENT_PRECISION_BITS, round=gmpy2.RoundDown
    ):
        denominator_lower = gmpy2.exp(lower_input) - 1
    with gmpy2.context(
        gmpy2.get_context(), precision=INDEPENDENT_PRECISION_BITS, round=gmpy2.RoundUp
    ):
        denominator_upper = gmpy2.exp(upper_input) - 1
    if denominator_lower <= 0:
        raise IndependentSemanticFailure("independent Bernoulli denominator unresolved")
    with gmpy2.context(
        gmpy2.get_context(), precision=INDEPENDENT_PRECISION_BITS, round=gmpy2.RoundDown
    ):
        lower = lower_input / denominator_upper
    with gmpy2.context(
        gmpy2.get_context(), precision=INDEPENDENT_PRECISION_BITS, round=gmpy2.RoundUp
    ):
        upper = upper_input / denominator_lower
    return Interval(_mpfr_float_lower(lower), _mpfr_float_upper(upper))


def _bernoulli(value: Fraction) -> Interval:
    if value == 0:
        return Interval.point(Fraction(1))
    if value > 0:
        return _bernoulli_positive(value)
    positive = -value
    return _exp_interval(positive).multiply(_bernoulli_positive(positive))


def _mod(value: Fraction, width: Fraction) -> Fraction:
    return value - (value // width) * width


def _build_axis(
    name: str,
    specification: dict[str, object],
    *,
    diffusion: Fraction,
    stiffness: Fraction,
    mean: Fraction,
) -> Axis:
    size = specification["size"]
    alignment = specification["alignment"]
    if name == "relative_perpendicular":
        start = Fraction(-1, 2)
        width = Fraction(1)
        step = width / size
        shift = step / 2 if alignment == "cell_centred_periodic_half_shift" else Fraction(0)
        positions = tuple(
            start + _mod((index + Fraction(1, 2)) * step + shift, width) for index in range(size)
        )
        cells: list[tuple[tuple[Fraction, Fraction], ...]] = []
        for index in range(size):
            lower = start + _mod(index * step + shift, width)
            upper = lower + step
            if upper <= start + width:
                cells.append(((lower, upper),))
            else:
                cells.append(((lower, start + width), (start, upper - width)))
        rate = Interval.point(diffusion / (step * step))
        stationary = Interval.point(step)
        return Axis(
            name,
            size,
            True,
            "cell_centred_periodic_diffusion_half_shift"
            if shift
            else "cell_centred_periodic_diffusion",
            start,
            width,
            shift,
            positions,
            (step,) * size,
            tuple(cells),
            (rate,) * size,
            (rate,) * size,
            (stationary,) * size,
        )
    lower = _hex(specification["lower_binary64_hex"], label=f"{name} lower")
    upper = _hex(specification["upper_binary64_hex"], label=f"{name} upper")
    width = upper - lower
    if alignment == "vertex_centred_reflecting_dual":
        step = width / (size - 1)
        positions = tuple(lower + index * step for index in range(size))
        boundaries = (
            (lower,)
            + tuple((left + right) / 2 for left, right in zip(positions, positions[1:]))
            + (upper,)
        )
        volumes = tuple(boundaries[index + 1] - boundaries[index] for index in range(size))
        cells = tuple(((boundaries[index], boundaries[index + 1]),) for index in range(size))
        construction = "vertex_centred_reflecting_scharfetter_gummel"
    else:
        step = width / size
        positions = tuple(lower + (index + Fraction(1, 2)) * step for index in range(size))
        volumes = (step,) * size
        cells = tuple(
            ((lower + index * step, lower + (index + 1) * step),) for index in range(size)
        )
        construction = "cell_centred_reflecting_scharfetter_gummel"
    potentials = tuple(
        stiffness * (position - mean) ** 2 / (2 * diffusion) for position in positions
    )
    forward = [ZERO for _ in range(size)]
    backward = [ZERO for _ in range(size)]
    for left in range(size - 1):
        right = left + 1
        distance = positions[right] - positions[left]
        delta = potentials[right] - potentials[left]
        forward[left] = _bernoulli(delta).scale(diffusion / (volumes[left] * distance))
        backward[right] = _bernoulli(-delta).scale(diffusion / (volumes[right] * distance))
    stationary = tuple(
        _exp_interval(-potential).scale(volume)
        for potential, volume in zip(potentials, volumes, strict=True)
    )
    return Axis(
        name,
        size,
        False,
        construction,
        lower,
        width,
        Fraction(0),
        positions,
        volumes,
        cells,
        tuple(forward),
        tuple(backward),
        stationary,
    )


def _partition_bytes(axis: Axis) -> bytes:
    return _canonical(
        {
            "cell_segments_exact": [
                [[_fraction_text(lower), _fraction_text(upper)] for lower, upper in cell]
                for cell in axis.cells
            ],
            "cell_volumes_exact": [_fraction_text(value) for value in axis.volumes],
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
    )


def _decode_intervals(source: bytes, *, count: int, label: str) -> tuple[Interval, ...]:
    if len(source) != 16 * count:
        raise IndependentSemanticFailure(f"{label} byte length drifted")
    return tuple(Interval(lower, upper) for lower, upper in struct.iter_unpack(">dd", source))


def _validate_raw_manifest(
    manifest: object,
    file_entry: object,
    source: bytes,
    *,
    role: str,
    count: int,
) -> None:
    current = _require_keys(manifest, _RAW_KEYS, label="BE interval manifest")
    file_fields = _require_keys(
        file_entry, {"byte_length", "path", "sha256"}, label="BE interval file"
    )
    if (
        current["schema"] != RAW_SCHEMA
        or current["byte_order"] != "big"
        or current["record_format"] != ">dd"
        or current["role"] != role
        or current["logical_shape"] != [count]
        or current["record_count"] != count
        or current["raw_byte_length"] != 16 * count
        or current["raw_byte_length"] != len(source)
        or current["raw_sha256"] != _sha(source)
        or file_fields["byte_length"] != len(source)
        or file_fields["sha256"] != _sha(source)
    ):
        raise IndependentSemanticFailure("BE interval manifest/file relation drifted")


def _active_index_sha(records: Sequence[tuple[int, Interval]]) -> str:
    digest = hashlib.sha256(b"production-initial-active-flat-indices-v1\0")
    for index, _ in records:
        digest.update(index.to_bytes(8, "big"))
    return digest.hexdigest()


def _dense_sha(states: int, records: Sequence[tuple[int, Interval]]) -> str:
    digest = hashlib.sha256()
    zero_pair = struct.pack(">dd", 0.0, 0.0)
    block_states = 65_536
    block = zero_pair * block_states
    cursor = 0

    def add_zeros(count: int) -> None:
        full, remainder = divmod(count, block_states)
        for _ in range(full):
            digest.update(block)
        if remainder:
            digest.update(zero_pair * remainder)

    for index, interval in records:
        add_zeros(index - cursor)
        digest.update(struct.pack(">dd", interval.lower, interval.upper))
        cursor = index + 1
    add_zeros(states - cursor)
    return digest.hexdigest()


def _contained(inner: Interval, outer: Interval) -> bool:
    return (
        outer.lower_fraction <= inner.lower_fraction
        and inner.upper_fraction <= outer.upper_fraction
    )


@lru_cache(maxsize=1)
def _verify_fourth_bound() -> Fraction:
    coefficients = {3: 24, 4: 300, 5: 672, 6: 624, 7: 192, 8: 16}
    derived = Fraction(0)
    for degree, coefficient in coefficients.items():
        exponential_lower = sum(
            (Fraction(degree**order, math.factorial(order)) for order in range(48)),
            Fraction(0),
        )
        derived += coefficient * Fraction(degree**degree) / exponential_lower
    if derived >= BUMP_FOURTH_BOUND:
        raise IndependentSemanticFailure("independent fourth-derivative proof failed")
    return BUMP_FOURTH_BOUND


def _ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


@lru_cache(maxsize=4096)
def _bump_integral(lower: Fraction, upper: Fraction) -> Interval:
    lo = max(Fraction(-1), lower)
    hi = min(Fraction(1), upper)
    if hi <= lo:
        return ZERO
    panel_count = max(2, _ceil_fraction((hi - lo) * INDEPENDENT_PANELS_PER_UNIT))
    if panel_count % 2:
        panel_count += 1
    step = (hi - lo) / panel_count
    lower_sum = Fraction(0)
    upper_sum = Fraction(0)
    for index in range(panel_count + 1):
        point = lo + index * step
        value = ZERO if point <= -1 or point >= 1 else _exp_interval(-1 / (1 - point * point))
        weight = 1 if index in (0, panel_count) else (4 if index % 2 else 2)
        lower_sum += weight * value.lower_fraction
        upper_sum += weight * value.upper_fraction
    error = (hi - lo) * step**4 * _verify_fourth_bound() / 180
    return Interval.from_bounds(
        max(Fraction(0), step * lower_sum / 3 - error),
        step * upper_sum / 3 + error,
    )


def _image_indices(
    lower: Fraction,
    upper: Fraction,
    *,
    centre: Fraction,
    half_width: Fraction,
    period: Fraction,
) -> range:
    first = _ceil_fraction((lower - centre - half_width) / period)
    last = (upper - centre + half_width) // period
    return range(first, last + 1)


def _profile(
    axis: Axis,
    *,
    centre: Fraction,
    half_width: Fraction,
    period: Fraction | None,
) -> tuple[Interval, ...]:
    normalization = _bump_integral(Fraction(-1), Fraction(1))
    result: list[Interval] = []
    for cell in axis.cells:
        raw = ZERO
        for segment_lower, segment_upper in cell:
            images: Iterable[int] = (0,)
            if period is not None:
                images = _image_indices(
                    segment_lower,
                    segment_upper,
                    centre=centre,
                    half_width=half_width,
                    period=period,
                )
            for image_index in images:
                image_centre = centre if period is None else centre + image_index * period
                overlap_lower = max(segment_lower, image_centre - half_width)
                overlap_upper = min(segment_upper, image_centre + half_width)
                if overlap_upper <= overlap_lower:
                    continue
                raw = raw.add(
                    _bump_integral(
                        (overlap_lower - image_centre) / half_width,
                        (overlap_upper - image_centre) / half_width,
                    )
                )
        result.append(raw.divide(normalization))
    lower_mass = sum((entry.lower_fraction for entry in result), Fraction(0))
    upper_mass = sum((entry.upper_fraction for entry in result), Fraction(0))
    if not lower_mass <= 1 <= upper_mass:
        raise IndependentSemanticFailure("independent marginal misses unit mass")
    return tuple(result)


def _decode_sparse(
    source: bytes,
    *,
    expected_shape: tuple[int, int, int],
) -> tuple[tuple[int, Interval], ...]:
    if len(source) < SPARSE_HEADER.size:
        raise IndependentSemanticFailure("sparse component file is truncated")
    header = SPARSE_HEADER.unpack_from(source)
    magic, version, rank, states, active, first, second, third, record_size, flags = header
    if (
        magic != SPARSE_MAGIC
        or version != 1
        or rank != 3
        or (first, second, third) != expected_shape
        or states != math.prod(expected_shape)
        or record_size != SPARSE_RECORD.size
        or flags != 1
        or len(source) != SPARSE_HEADER.size + active * SPARSE_RECORD.size
    ):
        raise IndependentSemanticFailure("sparse component header drifted")
    result: list[tuple[int, Interval]] = []
    for offset in range(SPARSE_HEADER.size, len(source), SPARSE_RECORD.size):
        index, lower, upper = SPARSE_RECORD.unpack_from(source, offset)
        if result and index <= result[-1][0]:
            raise IndependentSemanticFailure("sparse component order drifted")
        result.append((index, Interval(lower, upper)))
    return tuple(result)


def _verify_row(
    *,
    row_index: int,
    row_spec: dict[str, object],
    row_manifest: dict[str, object],
    inventory: dict[str, bytes],
    referenced: set[str],
    source: dict[str, object],
    dynamics: dict[str, object],
) -> dict[str, object]:
    row_manifest = _require_keys(row_manifest, _ROW_MANIFEST_KEYS, label="row manifest")
    particle = _hex(dynamics["particle_diffusion_binary64_hex"], label="particle diffusion")
    stiffness = _hex(dynamics["ou_stiffness_binary64_hex"], label="OU stiffness")
    mean = _hex(dynamics["ou_mean_binary64_hex"], label="OU mean")
    axes = (
        _build_axis(
            "midpoint",
            row_spec["midpoint"],
            diffusion=particle / 2,
            stiffness=stiffness,
            mean=mean,
        ),
        _build_axis(
            "relative_parallel",
            row_spec["relative_parallel"],
            diffusion=2 * particle,
            stiffness=stiffness,
            mean=Fraction(0),
        ),
        _build_axis(
            "relative_perpendicular",
            row_spec["relative_perpendicular"],
            diffusion=2 * particle,
            stiffness=Fraction(0),
            mean=Fraction(0),
        ),
    )
    manifest_axes = row_manifest["axes"]
    manifest_marginals = row_manifest["initial_marginals"]
    expected_states = math.prod(axis.size for axis in axes)
    if (
        row_manifest.get("schema") != ROW_SCHEMA
        or row_manifest.get("configuration_index") != row_index
        or row_manifest.get("configuration_label") != row_spec["label"]
        or row_manifest.get("configuration_sha256") != CONFIGURATION_SHA256
        or row_manifest.get("expected_states") != expected_states
        or row_manifest.get("flags") != _ROW_FLAGS
        or row_manifest.get("status") != "PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0"
        or type(manifest_axes) is not list
        or type(manifest_marginals) is not list
        or len(manifest_axes) != 3
        or len(manifest_marginals) != 3
    ):
        raise IndependentSemanticFailure("row manifest identity drifted")
    for entry, coordinate in zip(manifest_axes, COORDINATES, strict=True):
        current = _require_keys(entry, _AXIS_ENTRY_KEYS, label="axis entry")
        if current["coordinate"] != coordinate:
            raise IndependentSemanticFailure("axis coordinate order drifted")
    for entry, coordinate in zip(manifest_marginals, COORDINATES, strict=True):
        current = _require_keys(entry, _MARGINAL_ENTRY_KEYS, label="marginal entry")
        if current["coordinate"] != coordinate:
            raise IndependentSemanticFailure("marginal coordinate order drifted")
    rate_count = 0
    stationary_count = 0
    partition_hashes: list[str] = []
    axis_relation_hashes: list[str] = []
    for axis, axis_entry in zip(axes, manifest_axes, strict=True):
        if type(axis_entry.get("rates")) is not dict or set(axis_entry["rates"]) != {
            "backward",
            "forward",
            "stationary_mass",
        }:
            raise IndependentSemanticFailure("axis rate role set drifted")
        expected_partition = _partition_bytes(axis)
        observed_partition = _bound_file_reference(
            axis_entry["partition_file"], inventory, referenced
        )
        if observed_partition != expected_partition:
            raise IndependentSemanticFailure(f"exact partition differs: {row_spec['label']}")
        partition_sha = _sha(expected_partition)
        partition_hashes.append(partition_sha)
        for direction, independent in (
            ("forward", axis.forward),
            ("backward", axis.backward),
            ("stationary_mass", axis.stationary),
        ):
            rate_entry = _require_keys(
                axis_entry["rates"][direction],
                _RATE_ENTRY_KEYS,
                label="rate entry",
            )
            raw = _bound_file_reference(rate_entry["file"], inventory, referenced)
            producer = _decode_intervals(raw, count=axis.size, label=direction)
            _validate_raw_manifest(
                rate_entry["manifest"],
                rate_entry["file"],
                raw,
                role=f"control_free_axis_{axis.name}_{direction}",
                count=axis.size,
            )
            if any(not _contained(inner, outer) for inner, outer in zip(independent, producer)):
                raise IndependentSemanticFailure(
                    f"independent {direction} is not contained: {row_spec['label']}:{axis.name}"
                )
            if direction == "stationary_mass":
                stationary_count += axis.size
            else:
                rate_count += axis.size
        relation = {
            "coordinate": axis.name,
            "partition_sha256": partition_sha,
            "rate_raw_sha256s": {
                name: axis_entry["rates"][name]["file"]["sha256"]
                for name in sorted(axis_entry["rates"])
            },
        }
        expected_axis_relation = _digest(
            b"production-initial-axis-geometry-rate-relation-v1\0", relation
        )
        if expected_axis_relation != axis_entry["axis_relation_sha256"]:
            raise IndependentSemanticFailure("axis relation digest drifted")
        axis_relation_hashes.append(expected_axis_relation)

    centres = tuple(_hex(source["starts_binary64_hex"][name], label=name) for name in COORDINATES)
    half_width = _hex(source["half_width_binary64_hex"], label="half width")
    independent_profiles = tuple(
        _profile(
            axis,
            centre=centres[index],
            half_width=half_width,
            period=Fraction(1) if axis.periodic else None,
        )
        for index, axis in enumerate(axes)
    )
    producer_profiles: list[tuple[Interval, ...]] = []
    marginal_hashes: list[str] = []
    marginal_count = 0
    for axis, independent, marginal_entry in zip(
        axes, independent_profiles, manifest_marginals, strict=True
    ):
        raw = _bound_file_reference(marginal_entry["file"], inventory, referenced)
        producer = _decode_intervals(raw, count=axis.size, label="initial marginal")
        _validate_raw_manifest(
            marginal_entry["manifest"],
            marginal_entry["file"],
            raw,
            role=f"analytic_initial_marginal_{axis.name}",
            count=axis.size,
        )
        if any(not _contained(inner, outer) for inner, outer in zip(independent, producer)):
            raise IndependentSemanticFailure(
                f"independent marginal is not contained: {row_spec['label']}:{axis.name}"
            )
        independent_active = tuple(
            index for index, interval in enumerate(independent) if interval.upper > 0
        )
        producer_active = tuple(
            index for index, interval in enumerate(producer) if interval.upper > 0
        )
        if (
            independent_active != producer_active
            or list(producer_active) != marginal_entry["active_indices"]
        ):
            raise IndependentSemanticFailure("independent marginal support drifted")
        producer_profiles.append(producer)
        marginal_hashes.append(_sha(raw))
        marginal_count += axis.size

    shape = tuple(axis.size for axis in axes)
    sparse_manifest = _require_keys(
        row_manifest["sparse_component_box"], _SPARSE_KEYS, label="sparse manifest"
    )
    sparse_raw = _bound_file_reference(sparse_manifest["file"], inventory, referenced)
    producer_sparse = _decode_sparse(sparse_raw, expected_shape=shape)
    producer_lower_mass = sum(
        (interval.lower_fraction for _, interval in producer_sparse), Fraction(0)
    )
    producer_upper_mass = sum(
        (interval.upper_fraction for _, interval in producer_sparse), Fraction(0)
    )
    if (
        sparse_manifest["schema"] != SPARSE_SCHEMA
        or sparse_manifest["shape"] != list(shape)
        or sparse_manifest["state_count"] != math.prod(shape)
        or sparse_manifest["active_component_count"] != len(producer_sparse)
        or sparse_manifest["record_format"] != ">Qdd"
        or sparse_manifest["dense_expansion_record_format"] != ">dd"
        or sparse_manifest["tensor_order"] != TENSOR_ORDER
        or sparse_manifest["implicit_background"] != "positive_zero_interval_[0x0.0p+0,0x0.0p+0]"
        or sparse_manifest["active_index_sha256"] != _active_index_sha(producer_sparse)
        or sparse_manifest["dense_expansion_byte_length"] != 16 * math.prod(shape)
        or sparse_manifest["dense_expansion_sha256"]
        != _dense_sha(math.prod(shape), producer_sparse)
        or sparse_manifest["lower_mass_exact"] != _fraction_text(producer_lower_mass)
        or sparse_manifest["upper_mass_exact"] != _fraction_text(producer_upper_mass)
        or not producer_lower_mass <= 1 <= producer_upper_mass
    ):
        raise IndependentSemanticFailure("sparse manifest/expanded stream drifted")
    active_axes = tuple(
        tuple(index for index, interval in enumerate(profile) if interval.upper > 0)
        for profile in independent_profiles
    )
    independent_components: list[tuple[int, Interval]] = []
    for i, j, k in product(*active_axes):
        exact_lower = (
            independent_profiles[0][i].lower_fraction
            * independent_profiles[1][j].lower_fraction
            * independent_profiles[2][k].lower_fraction
        )
        exact_upper = (
            independent_profiles[0][i].upper_fraction
            * independent_profiles[1][j].upper_fraction
            * independent_profiles[2][k].upper_fraction
        )
        independent_components.append(
            ((i * shape[1] + j) * shape[2] + k, Interval.from_bounds(exact_lower, exact_upper))
        )
    if tuple(index for index, _ in independent_components) != tuple(
        index for index, _ in producer_sparse
    ):
        raise IndependentSemanticFailure("independent sparse active Cartesian product drifted")
    if any(
        not _contained(independent_interval, producer_interval)
        for (_, independent_interval), (_, producer_interval) in zip(
            independent_components, producer_sparse, strict=True
        )
    ):
        raise IndependentSemanticFailure("independent component interval is not contained")
    source_relation = {
        "analytic_source_sha256": ANALYTIC_SOURCE_SHA256,
        "configuration_sha256": CONFIGURATION_SHA256,
        "marginal_raw_sha256s": marginal_hashes,
        "sparse_raw_sha256": _sha(sparse_raw),
        "dense_expansion_sha256": sparse_manifest["dense_expansion_sha256"],
        "shape": list(shape),
        "tensor_order": TENSOR_ORDER,
    }
    source_relation_sha = _digest(b"production-initial-source-box-relation-v1\0", source_relation)
    if source_relation_sha != row_manifest["source_box_relation_sha256"]:
        raise IndependentSemanticFailure("source/box relation digest drifted")
    row_relation_sha = _digest(
        b"production-initial-row-relation-v1\0",
        {
            "axis_relation_sha256s": axis_relation_hashes,
            "configuration_index": row_index,
            "configuration_label": row_spec["label"],
            "source_box_relation_sha256": source_relation_sha,
        },
    )
    if row_relation_sha != row_manifest["row_relation_sha256"]:
        raise IndependentSemanticFailure("row relation digest drifted")
    return {
        "active_component_containment_count": len(independent_components),
        "configuration_index": row_index,
        "configuration_label": row_spec["label"],
        "exact_partition_count": 3,
        "free_rate_containment_count": rate_count,
        "initial_marginal_containment_count": marginal_count,
        "row_relation_sha256": row_relation_sha,
        "source_box_relation_sha256": source_relation_sha,
        "stationary_mass_containment_count": stationary_count,
        "tensor_shape": list(shape),
    }


def verify_bundle_independently(bundle: Path) -> dict[str, object]:
    """Independently verify all twelve source/partition/free-axis relations."""

    if bundle.is_symlink():
        raise IndependentSemanticFailure("bundle root is a symlink")
    root = bundle.resolve()
    if not root.is_dir():
        raise IndependentSemanticFailure("bundle root is not a directory")
    bundle_bytes = _read(root / "bundle.json", maximum=2_000_000)
    manifest = _require_keys(
        _parse(bundle_bytes, canonical=True, label="bundle manifest"),
        _BUNDLE_KEYS,
        label="bundle manifest",
    )
    if (
        manifest.get("schema") != BUNDLE_SCHEMA
        or manifest.get("status") != BUNDLE_STATUS
        or manifest.get("configuration_count") != 12
        or manifest.get("configuration_sha256") != CONFIGURATION_SHA256
        or manifest.get("analytic_source_sha256") != ANALYTIC_SOURCE_SHA256
        or manifest.get("total_state_workload") != 34_787_462
        or manifest.get("total_dense_expansion_byte_length") != 556_599_392
        or manifest.get("flags") != _BUNDLE_FLAGS
        or manifest.get("method")
        != {
            "dense_component_box_materialized": False,
            "marginal_endpoint_record_format": ">dd",
            "panels_per_unit": 16_384,
            "precision_bits": 192,
            "sparse_component_record_format": ">Qdd",
            "tensor_order": TENSOR_ORDER,
        }
    ):
        raise IndependentSemanticFailure("bundle boundary metadata drifted")
    files = _inventory(root, manifest)
    referenced_paths = {
        "request/analytic_source.json",
        "request/configuration.json",
    }
    if not referenced_paths <= set(files):
        raise IndependentSemanticFailure("request files are missing from inventory")
    configuration_bytes = files.get("request/configuration.json")
    source_bytes = files.get("request/analytic_source.json")
    if (
        configuration_bytes is None
        or source_bytes is None
        or _sha(configuration_bytes) != CONFIGURATION_SHA256
        or _sha(source_bytes) != ANALYTIC_SOURCE_SHA256
    ):
        raise IndependentSemanticFailure("request source hashes drifted")
    configuration = _parse(configuration_bytes, canonical=True, label="configuration")
    source = _parse(source_bytes, canonical=False, label="analytic source")
    if (
        type(configuration) is not dict
        or source != _SOURCE_LAW
        or configuration.get("configuration_order") != list(_EXPECTED_LABELS)
        or configuration.get("configuration_count") != 12
        or configuration.get("contains_budget_value") is not False
        or configuration.get("contains_control_values") is not False
        or configuration.get("authorizes_scientific_execution") is not False
    ):
        raise IndependentSemanticFailure("request semantics drifted")
    summaries = manifest.get("rows")
    row_specs = configuration.get("configurations")
    if type(summaries) is not list or type(row_specs) is not list or len(summaries) != 12:
        raise IndependentSemanticFailure("row family structure drifted")
    receipt_rows: list[dict[str, object]] = []
    for index, (summary, row_spec) in enumerate(zip(summaries, row_specs, strict=True)):
        summary = _require_keys(summary, _ROW_SUMMARY_KEYS, label="row summary")
        if type(row_spec) is not dict:
            raise IndependentSemanticFailure("configuration row is not an object")
        expected_shape = [
            row_spec["midpoint"]["size"],
            row_spec["relative_parallel"]["size"],
            row_spec["relative_perpendicular"]["size"],
        ]
        expected_states = math.prod(expected_shape)
        if (
            summary.get("configuration_index") != index
            or summary.get("configuration_label") != _EXPECTED_LABELS[index]
            or row_spec.get("label") != _EXPECTED_LABELS[index]
            or summary.get("expected_states") != expected_states
        ):
            raise IndependentSemanticFailure("row registry order drifted")
        row_manifest = _parse(
            _bound_file_reference(summary["row_manifest"], files, referenced_paths),
            canonical=True,
            label="row manifest",
        )
        verified_row = _verify_row(
            row_index=index,
            row_spec=row_spec,
            row_manifest=row_manifest,
            inventory=files,
            referenced=referenced_paths,
            source=source,
            dynamics=configuration["dynamics"],
        )
        if (
            verified_row["tensor_shape"] != expected_shape
            or summary["row_relation_sha256"] != verified_row["row_relation_sha256"]
        ):
            raise IndependentSemanticFailure("row summary relation binding drifted")
        receipt_rows.append(verified_row)
    if referenced_paths != set(files):
        raise IndependentSemanticFailure("inventory/reference graph drifted")
    family_relation = _digest(
        b"production-initial-family-relation-v1\0",
        {
            "analytic_source_sha256": ANALYTIC_SOURCE_SHA256,
            "configuration_sha256": CONFIGURATION_SHA256,
            "ordered_row_relation_sha256s": [row["row_relation_sha256"] for row in receipt_rows],
        },
    )
    if family_relation != manifest["family_relation_sha256"]:
        raise IndependentSemanticFailure("family relation digest drifted")
    core = {
        "analytic_source_sha256": ANALYTIC_SOURCE_SHA256,
        "bundle_manifest_sha256": _sha(bundle_bytes),
        "configuration_sha256": CONFIGURATION_SHA256,
        "family_relation_sha256": family_relation,
        "flags": {
            "all_twelve_rows_verified": True,
            "artifact_parser_implementation_separate": True,
            "authorizes_scientific_execution": False,
            "clean_process_observed": False,
            "continuum_verified": False,
            "exact_partitions_independently_reconstructed": True,
            "f0_pass": False,
            "free_axis_rate_semantic_containment_complete": True,
            "fresh_process": False,
            "full_operator_bound": False,
            "independent_numerical_implementation": True,
            "independent_semantic_replay_complete": False,
            "independent_semantic_replay_complete_for_declared_scope": True,
            "initial_component_semantic_containment_complete": True,
            "initial_marginal_semantic_containment_complete": True,
            "killing_contact_geometry_bound": False,
            "positive_budget_executed": False,
            "production_resource_gate": False,
            "producer_nonpromotion_flags_fail_closed": True,
            "producer_positive_semantic_claims_used_as_authority": False,
            "producer_interval_endpoints_consumed_only_as_outer_envelopes": True,
            "producer_quadrature_ledgers_consumed": False,
            "propagation_executed": False,
            "science_executed": False,
            "topology_complete": False,
        },
        "method": {
            "backend_independence_scope": (
                "separate_source_and_higher_precision_same_gmpy2_mpfr_library"
            ),
            "bump_fourth_derivative_bound_exact": _fraction_text(BUMP_FOURTH_BOUND),
            "bump_panels_per_unit": INDEPENDENT_PANELS_PER_UNIT,
            "directed_mpfr_precision_bits": INDEPENDENT_PRECISION_BITS,
            "free_rate_scheme": "independent_scharfetter_gummel_directed_mpfr_v1",
            "gmpy2_version": gmpy2.version(),
            "marginal_scheme": "independent_finer_validated_composite_simpson_v1",
            "mpfr_version": gmpy2.mpfr_version(),
        },
        "rows": receipt_rows,
        "schema": SCHEMA,
        "status": STATUS,
        "total_state_workload": 34_787_462,
        "verifier_source_sha256": _sha(_read(Path(__file__).resolve())),
    }
    return {
        **core,
        "receipt_sha256": _digest(b"production-initial-independent-semantic-receipt-v1\0", core),
    }


def write_receipt(bundle: Path, output: Path) -> dict[str, object]:
    receipt = verify_bundle_independently(bundle)
    if output.exists() or output.is_symlink():
        raise IndependentSemanticFailure("receipt output already exists")
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
