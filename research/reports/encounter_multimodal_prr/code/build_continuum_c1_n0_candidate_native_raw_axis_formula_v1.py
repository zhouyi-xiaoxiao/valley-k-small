"""Build the result-blind candidate-native role-8 raw-axis primitive.

The sole execution authority is a strict canonical-JSON request supplied by
absolute path.  It binds, by absolute path and SHA-256, the candidate member,
reference density, ideal formula source, control-free configuration family,
candidate method-parameter registry, every exact axis partition, this producer,
and the source-separated verifier.  The request also supplies a fresh absolute
output path, but contains no expected output/result hash or observed result.

This module imports no legacy scientific implementation.  Its scientific
scope is deliberately narrow: ungauged raw axis-cell ``mu``, both directed
axis-edge ``q`` values, reflecting boundary zero rates, direct common-flux
formula witnesses, product witnesses, and their nonempty intersection.  It
does not read a stationary-integral or killing-geometry result and does not
compute any downstream physical normalization, gauged tensor mass,
conductance, or reconstructed multiplier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import secrets
import stat
import sys
import threading
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final, Sequence

import gmpy2

_STAGE_OPEN: Final = os.open
_STAGE_FSTAT: Final = os.fstat

REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_raw_axis_formula_request_v2"
OUTPUT_SCHEMA: Final = "encounter_continuum_c1_n0_candidate_native_raw_axis_formula_v1"
OUTPUT_STATUS: Final = (
    "PASS_RESULT_BLIND_CANDIDATE_NATIVE_RAW_AXIS_FORMULA_"
    "PRIMARY_SENTINEL_CONTAINMENT_ONLY_NOT_EXTERNAL_COMMITMENT_NOT_COMPLETE_C1_C2"
)
MEMBER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_member_spec_v3_candidate"
REFERENCE_SCHEMA: Final = "encounter_continuum_c1_reference_density_source_v1"
FORMULA_SCHEMA: Final = "encounter_continuum_c1_ideal_formula_source_v1"
CONFIGURATION_SCHEMA: Final = "encounter_physical_configuration_family_control_free_v1"
FACTORIZATION_SCHEMA: Final = "encounter_continuum_c1_factorization_source_v2_candidate"
FACTORIZATION_STATUS: Final = (
    "OUTCOME_FREE_CONTROL_FREE_FACTORIZATION_CANDIDATE_ONLY_NOT_EXTERNALLY_"
    "COMMITTED_NO_NUMERIC_ENCLOSURES_NO_CONCRETE_KILLING"
)
FACTORIZATION_RELATIVE_PATH: Final = (
    "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"
)
FACTORIZATION_SHA256: Final = "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26"
PARAMETER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_method_parameter_registry_v3_candidate"
PARAMETER_STATUS: Final = (
    "RESULT_BLIND_CANDIDATE_NATIVE_METHOD_PARAMETERS_ONLY_NOT_EXTERNALLY_COMMITTED"
)
PARAMETER_DIGEST_DOMAIN: Final = "encounter-outward-method-parameters-v3"
PARAMETER_REGISTRY_RELATIVE_PATH: Final = (
    "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v3_candidate.json"
)
PARAMETER_REGISTRY_SHA256: Final = (
    "6c1879edaefe5f99da4fffcb76e12466862577376c305e14c857b880067e3b32"
)
PRIMARY_PARAMETER_ID: Final = "raw_flux_directed_mpfr_320_v2"
SENTINEL_PARAMETER_ID: Final = "raw_flux_directed_mpfr_640_sentinel_v2"
BINARY64_PARAMETER_ID: Final = "raw_flux_binary64_decode_v2"
EXACT_PARAMETER_ID: Final = "exact_fraction_expression_dag_v2"
GENERIC_CONTAINMENT: Final = "primary_interval_contains_higher_precision_same_backend_sentinel"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"
COORDINATES: Final = ("midpoint", "relative_parallel", "relative_perpendicular")

MAX_JSON_BYTES: Final = 8_000_000
MAX_OUTPUT_BYTES: Final = 64_000_000
MAX_INTEGER_BITS: Final = 65_536
MAX_JSON_DEPTH: Final = 64
MAX_CONFIGURATIONS: Final = 1_024
MAX_AXIS_CELLS: Final = 1_000_000

HOLD_REQUEST = "HOLD_CANDIDATE_RAW_AXIS_REQUEST"
HOLD_IMMUTABLE = "HOLD_CANDIDATE_RAW_AXIS_IMMUTABLE_INPUT"
HOLD_INPUT = "HOLD_CANDIDATE_RAW_AXIS_INPUT"
HOLD_MEMBER = "HOLD_CANDIDATE_RAW_AXIS_MEMBER_PARTITION"
HOLD_METHOD = "HOLD_CANDIDATE_RAW_AXIS_METHOD"
HOLD_RUNTIME = "HOLD_CANDIDATE_RAW_AXIS_RUNTIME"
HOLD_NUMERICAL = "HOLD_CANDIDATE_RAW_AXIS_NUMERICAL"
HOLD_OUTPUT = "HOLD_CANDIDATE_RAW_AXIS_OUTPUT"

_REQUEST_KEYS: Final = {
    "code_inputs",
    "input_authorities",
    "method_selection",
    "output",
    "partitions",
    "runtime_requirements",
    "schema",
    "status",
}
_PIN_KEYS: Final = {"path", "sha256"}
_SCHEMA_PIN_KEYS: Final = {"path", "schema", "sha256"}
_PARTITION_PIN_KEYS: Final = {
    "configuration_index",
    "coordinate",
    "member_report_relative_path",
    "path",
    "sha256",
}
_METHOD_SELECTION_KEYS: Final = {
    "binary64_parameter_id",
    "exact_parameter_id",
    "primary_parameter_id",
    "sentinel_parameter_id",
}
_RUNTIME_KEYS: Final = {"gmp", "gmpy2", "mpc", "mpfr", "python_abi"}
_OUTPUT_KEYS: Final = {"path", "schema"}
_INPUT_AUTHORITY_KEYS: Final = {
    "configuration",
    "configuration_design",
    "configuration_implementation",
    "configuration_test",
    "factorization",
    "factorization_initial_partition_bundle",
    "factorization_killing_geometry",
    "ideal_formula",
    "member_spec",
    "method_parameters",
    "reference_density",
}
_PARAMETER_REGISTRY_KEYS: Final = {
    "claim_boundary",
    "parameter_count",
    "parameters",
    "schema",
    "status",
}
_PREDECESSOR_CLAIM_KEYS: Final = {
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
}
_REFERENCE_CLAIM_KEYS: Final = {
    "box_truncation_proved",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "complete_C3",
    "continuum_topology_proved",
    "production_bridge_accepted",
    "release_eligible",
}
_FORMULA_CLAIM_KEYS: Final = {
    "binary64_centres_define_ideal_member",
    "complete_C0",
    "complete_C1",
    "complete_C2",
    "every_interval_endpoint_combination_is_a_model",
    "production_bridge_accepted",
    "release_eligible",
}
_PARAMETER_ORDER: Final = (
    "stationary_directed_mpfr_320_v2",
    "stationary_directed_mpfr_640_sentinel_v2",
    PRIMARY_PARAMETER_ID,
    SENTINEL_PARAMETER_ID,
    BINARY64_PARAMETER_ID,
    EXACT_PARAMETER_ID,
    "killing_contact_profile_mpfr_192_v2",
    "killing_analytic_disk_area_mpfr_256_v2",
    "killing_independent_simpson_remainder_v2",
    "killing_exact_full_cell_classification_v2",
)
_PARAMETER_DIGEST_ORDER: Final = (
    "2366cc19e4829ac91972a8b04eee8cb02f5ff6c9de2c0fee72d47bda49057243",
    "c8e809691b9229cf0c40c9d6089890f532cb61e2cb6146c7c14b0822c048a09f",
    "185982113248f46820593d4c2a372e9b67e73eaf2566a5f099fdc690765e0e40",
    "e64e254fa36cbd2368b1e263e0ebd0a130830f61ff379e173698e317e191054a",
    "82e9ecc9508ee6a2b06f83cdc2a77a4bcac4ba3418835bbcc591355cafe95e17",
    "5229e890cebb0711b6f1d57e434f30e3463f04eb77ccf14a2bf74e73bf6ef903",
    "c4f8169a819c79a563cae011938ff74f7e5963615f277a14d5ce8e81ce8f855e",
    "ca8dc076a6039a12fbbadca172f68a868da0a6040bdb9b114264bc2fd013c08b",
    "f03fa72ca1fccf49b65891271854cd3ebe085516e6415ca9d4f40134aefa0a65",
    "b853e67f59419df41893ee652e8cdb57485b4b2f09ac9290425d98d9511ddcb3",
)
_PARAMETER_SCOPES: Final = {
    "stationary_directed_mpfr_320_v2": ["role9_stationary_physical_integral"],
    "stationary_directed_mpfr_640_sentinel_v2": ["role9_stationary_physical_integral"],
    PRIMARY_PARAMETER_ID: ["role8_raw_axis_formula_primitive"],
    SENTINEL_PARAMETER_ID: ["role8_raw_axis_formula_primitive"],
    BINARY64_PARAMETER_ID: ["role8_raw_axis_formula_primitive"],
    EXACT_PARAMETER_ID: [
        "role8_raw_axis_formula_primitive",
        "role9_stationary_physical_integral",
        "same_member_mass_flux_composition",
        "symbolic_killing_composition",
    ],
    "killing_contact_profile_mpfr_192_v2": ["role10_killing_factor_geometry"],
    "killing_analytic_disk_area_mpfr_256_v2": ["role10_killing_factor_geometry"],
    "killing_independent_simpson_remainder_v2": ["role10_killing_factor_geometry"],
    "killing_exact_full_cell_classification_v2": ["role10_killing_factor_geometry"],
}
_MEMBER_KEYS: Final = {
    "claim_boundary",
    "configuration_order",
    "configuration_semantic_ids",
    "identity_properties",
    "member_identity_sha256",
    "member_semantics",
    "n0_sequence_bindings",
    "reconstruction_counts",
    "role_bindings",
    "schema",
    "source_lineage_evidence",
    "status",
}
_REFERENCE_KEYS: Final = {
    "boundary_and_measure",
    "claim_boundary",
    "coordinate_order",
    "diffusion_and_drift",
    "normalization",
    "physical_parameter_bundle",
    "schema",
    "source_pins",
    "status",
    "unit_table",
}
_FORMULA_KEYS: Final = {
    "claim_boundary",
    "formulae",
    "member_semantics",
    "potential_formulae",
    "schema",
    "source_pins",
    "status",
}
_CONFIGURATION_KEYS: Final = {
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
_FACTORIZATION_KEYS: Final = {
    "cell_average_formulae",
    "claim_boundary",
    "contact_geometry",
    "coordinate_and_measure_contract",
    "dependency_closure",
    "enclosure_semantics",
    "outcome_free_contract",
    "profile_basis",
    "schema",
    "source_pins",
    "status",
    "storage_contract",
}
_DYNAMICS_KEYS: Final = {
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
}


class CandidateRawAxisFailure(RuntimeError):
    """Fail-closed request, scientific, or publication failure."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code


@dataclass(frozen=True, slots=True)
class ExactInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if type(self.lower) is not Fraction or type(self.upper) is not Fraction:
            raise CandidateRawAxisFailure(HOLD_NUMERICAL, "non-Fraction interval endpoint")
        if self.lower > self.upper:
            raise CandidateRawAxisFailure(HOLD_NUMERICAL, "reversed interval")

    def contains(self, other: ExactInterval) -> bool:
        return self.lower <= other.lower and other.upper <= self.upper

    def multiply_nonnegative(self, other: ExactInterval) -> ExactInterval:
        if self.lower < 0 or other.lower < 0:
            raise CandidateRawAxisFailure(HOLD_NUMERICAL, "negative product factor")
        return ExactInterval(self.lower * other.lower, self.upper * other.upper)

    def intersect(self, other: ExactInterval) -> ExactInterval:
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower > upper:
            raise CandidateRawAxisFailure(HOLD_NUMERICAL, "disjoint common-flux witnesses")
        return ExactInterval(lower, upper)


@dataclass(frozen=True, slots=True)
class MPInterval:
    lower: gmpy2.mpfr
    upper: gmpy2.mpfr
    precision: int

    def exact(self) -> ExactInterval:
        return ExactInterval(_mpfr_fraction(self.lower), _mpfr_fraction(self.upper))


@dataclass(frozen=True, slots=True)
class Snapshot:
    path: Path
    raw: bytes
    sha256: str


@dataclass(frozen=True, slots=True)
class MethodParameters:
    primary_id: str
    sentinel_id: str
    binary64_id: str
    exact_id: str
    primary_bits: int
    sentinel_bits: int
    parameter_digests: dict[str, str]


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise CandidateRawAxisFailure(HOLD_INPUT, "duplicate or invalid JSON key")
        result[key] = value
    return result


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        raise CandidateRawAxisFailure(HOLD_INPUT, "JSON depth cap exceeded")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if value.bit_length() > MAX_INTEGER_BITS:
            raise CandidateRawAxisFailure(HOLD_INPUT, "JSON integer bit cap exceeded")
        return
    if type(value) is float:
        raise CandidateRawAxisFailure(HOLD_INPUT, "JSON floating literals are forbidden")
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise CandidateRawAxisFailure(HOLD_INPUT, "non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise CandidateRawAxisFailure(HOLD_INPUT, "invalid JSON object key")
            _strict_tree(item, depth + 1)
        return
    raise CandidateRawAxisFailure(HOLD_INPUT, "unsupported JSON value type")


def canonical_bytes(value: Any) -> bytes:
    _strict_tree(value)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _parse_canonical(raw: bytes, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                CandidateRawAxisFailure(HOLD_INPUT, f"{label}: float {token}")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                CandidateRawAxisFailure(HOLD_INPUT, f"{label}: constant {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CandidateRawAxisFailure(HOLD_INPUT, f"{label}: invalid ASCII JSON") from error
    _strict_tree(value)
    if type(value) is not dict or canonical_bytes(value) != raw:
        raise CandidateRawAxisFailure(HOLD_INPUT, f"{label}: noncanonical JSON")
    return value


def _exact_keys(value: Any, keys: set[str], *, code: str, label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise CandidateRawAxisFailure(code, f"{label}: exact-key mismatch")
    return value


def _json_exactly_equal(value: Any, expected: Any) -> bool:
    if type(value) is not type(expected):
        return False
    if type(value) is dict:
        return set(value) == set(expected) and all(
            _json_exactly_equal(value[key], expected[key]) for key in expected
        )
    if type(value) is list:
        return len(value) == len(expected) and all(
            _json_exactly_equal(left, right) for left, right in zip(value, expected, strict=True)
        )
    return bool(value == expected)


def _is_sha256(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _absolute_lexical(value: Any, *, code: str, label: str) -> Path:
    if type(value) is not str or not value:
        raise CandidateRawAxisFailure(code, f"{label}: path must be a string")
    path = Path(value)
    lexical = Path(os.path.abspath(path))
    if not path.is_absolute() or path != lexical:
        raise CandidateRawAxisFailure(code, f"{label}: canonical absolute path required")
    return path


def _directory_flags() -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NONBLOCK
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _close_descriptors(descriptors: Sequence[int]) -> None:
    for descriptor in reversed(descriptors):
        try:
            os.close(descriptor)
        except OSError:
            pass


def _open_anchored_directory_chain(
    directory: Path, *, code: str
) -> tuple[list[int], list[tuple[int, str, int, int, int]]]:
    lexical = Path(os.path.abspath(directory))
    if not directory.is_absolute() or directory != lexical:
        raise CandidateRawAxisFailure(code, "directory chain must be canonical absolute")
    descriptors: list[int] = []
    links: list[tuple[int, str, int, int, int]] = []
    try:
        root = os.open(directory.anchor, _directory_flags())
        descriptors.append(root)
        root_metadata = os.fstat(root)
        if not stat.S_ISDIR(root_metadata.st_mode):
            raise CandidateRawAxisFailure(code, "filesystem anchor is not a directory")
        for component in directory.parts[1:]:
            parent = descriptors[-1]
            child = os.open(component, _directory_flags(), dir_fd=parent)
            descriptors.append(child)
            opened = os.fstat(child)
            linked = os.stat(component, dir_fd=parent, follow_symlinks=False)
            if (
                not stat.S_ISDIR(opened.st_mode)
                or not stat.S_ISDIR(linked.st_mode)
                or (opened.st_dev, opened.st_ino) != (linked.st_dev, linked.st_ino)
            ):
                raise CandidateRawAxisFailure(code, "directory component identity mismatch")
            links.append((parent, component, child, opened.st_dev, opened.st_ino))
    except CandidateRawAxisFailure:
        _close_descriptors(descriptors)
        raise
    except OSError as error:
        _close_descriptors(descriptors)
        raise CandidateRawAxisFailure(
            code, "symlink path component or unavailable anchored directory"
        ) from error
    return descriptors, links


def _revalidate_anchored_directory_chain(
    links: Sequence[tuple[int, str, int, int, int]], *, code: str
) -> None:
    try:
        for parent, component, child, device, inode in links:
            opened = os.fstat(child)
            linked = os.stat(component, dir_fd=parent, follow_symlinks=False)
            if (
                not stat.S_ISDIR(opened.st_mode)
                or not stat.S_ISDIR(linked.st_mode)
                or (opened.st_dev, opened.st_ino) != (device, inode)
                or (linked.st_dev, linked.st_ino) != (device, inode)
            ):
                raise CandidateRawAxisFailure(code, "anchored directory chain changed")
    except CandidateRawAxisFailure:
        raise
    except OSError as error:
        raise CandidateRawAxisFailure(code, "anchored directory chain changed") from error


def immutable_snapshot(path: Path, *, cap: int = MAX_JSON_BYTES) -> Snapshot:
    lexical = Path(os.path.abspath(path))
    if not path.is_absolute() or path != lexical or not path.name:
        raise CandidateRawAxisFailure(HOLD_IMMUTABLE, "input path must be canonical absolute")
    directories, links = _open_anchored_directory_chain(path.parent, code=HOLD_IMMUTABLE)
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    try:
        descriptor = os.open(path.name, flags, dir_fd=directories[-1])
        before = os.fstat(descriptor)
        linked_before = os.stat(
            path.name,
            dir_fd=directories[-1],
            follow_symlinks=False,
        )
        if (
            not stat.S_ISREG(before.st_mode)
            or not stat.S_ISREG(linked_before.st_mode)
            or (before.st_dev, before.st_ino) != (linked_before.st_dev, linked_before.st_ino)
            or before.st_uid != os.getuid()
            or before.st_nlink != 1
            or before.st_mode & 0o222
            or before.st_size <= 0
            or before.st_size > cap
        ):
            raise CandidateRawAxisFailure(
                HOLD_IMMUTABLE, f"input must be owned, read-only, single-link regular: {path}"
            )
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1 << 20))
            if not chunk:
                raise CandidateRawAxisFailure(HOLD_IMMUTABLE, f"short read: {path}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise CandidateRawAxisFailure(HOLD_IMMUTABLE, f"input grew: {path}")
        after = os.fstat(descriptor)

        def identity(item: os.stat_result) -> tuple[int, ...]:
            return (
                item.st_dev,
                item.st_ino,
                item.st_mode,
                item.st_nlink,
                item.st_uid,
                item.st_size,
                item.st_mtime_ns,
                item.st_ctime_ns,
            )

        if identity(before) != identity(after):
            raise CandidateRawAxisFailure(HOLD_IMMUTABLE, f"input changed: {path}")
        linked_after = os.stat(
            path.name,
            dir_fd=directories[-1],
            follow_symlinks=False,
        )
        if not stat.S_ISREG(linked_after.st_mode) or (linked_after.st_dev, linked_after.st_ino) != (
            before.st_dev,
            before.st_ino,
        ):
            raise CandidateRawAxisFailure(HOLD_IMMUTABLE, "anchored input link changed")
        _revalidate_anchored_directory_chain(links, code=HOLD_IMMUTABLE)
    except CandidateRawAxisFailure:
        raise
    except OSError as error:
        raise CandidateRawAxisFailure(
            HOLD_IMMUTABLE, f"symlink path component or cannot read input: {path}"
        ) from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
        _close_descriptors(directories)
    raw = b"".join(chunks)
    return Snapshot(path=path, raw=raw, sha256=hashlib.sha256(raw).hexdigest())


def _pin_snapshot(pin: Any, *, label: str, cap: int = MAX_JSON_BYTES) -> Snapshot:
    current = _exact_keys(pin, _PIN_KEYS, code=HOLD_REQUEST, label=label)
    path = _absolute_lexical(current["path"], code=HOLD_REQUEST, label=label)
    expected = current["sha256"]
    if not _is_sha256(expected):
        raise CandidateRawAxisFailure(HOLD_REQUEST, f"{label}: invalid SHA-256")
    observed = immutable_snapshot(path, cap=cap)
    if observed.sha256 != expected:
        raise CandidateRawAxisFailure(HOLD_INPUT, f"{label}: SHA-256 mismatch")
    return observed


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _fraction(value: Any, *, code: str = HOLD_INPUT, label: str = "fraction") -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise CandidateRawAxisFailure(code, f"{label}: canonical p/q required")
    numerator_text, denominator_text = value.split("/")
    try:
        result = Fraction(int(numerator_text), int(denominator_text))
    except (ValueError, ZeroDivisionError) as error:
        raise CandidateRawAxisFailure(code, f"{label}: invalid fraction") from error
    if result.denominator <= 0 or _fraction_text(result) != value:
        raise CandidateRawAxisFailure(code, f"{label}: noncanonical fraction")
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_INTEGER_BITS:
        raise CandidateRawAxisFailure(code, f"{label}: fraction bit cap exceeded")
    return result


def _binary64_fraction(value: Any, *, label: str) -> Fraction:
    if type(value) is not str:
        raise CandidateRawAxisFailure(HOLD_INPUT, f"{label}: binary64 hex required")
    try:
        parsed = float.fromhex(value)
    except (OverflowError, ValueError) as error:
        raise CandidateRawAxisFailure(HOLD_INPUT, f"{label}: invalid binary64 hex") from error
    if (
        not math.isfinite(parsed)
        or parsed.hex() != value
        or (parsed == 0 and math.copysign(1.0, parsed) < 0)
    ):
        raise CandidateRawAxisFailure(HOLD_INPUT, f"{label}: noncanonical binary64")
    return Fraction.from_float(parsed)


def _domain_digest(domain: str, value: Any) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\0" + canonical_bytes(value)).hexdigest()


def _interval_json(value: ExactInterval) -> dict[str, str]:
    return {
        "lower_exact_p_over_q": _fraction_text(value.lower),
        "upper_exact_p_over_q": _fraction_text(value.upper),
    }


def _context(bits: int, rounding: int) -> gmpy2.context:
    return gmpy2.context(
        precision=bits,
        round=rounding,
        emax=1_073_741_823,
        emin=-1_073_741_823,
        subnormalize=False,
        trap_underflow=False,
        trap_overflow=False,
        trap_inexact=False,
        trap_invalid=False,
        trap_erange=False,
        trap_divzero=False,
        allow_complex=False,
        rational_division=False,
        allow_release_gil=False,
    )


def _mp_fraction(value: Fraction, precision: int, rounding: int) -> gmpy2.mpfr:
    with gmpy2.context(_context(precision, rounding)):
        return +gmpy2.mpfr(gmpy2.mpq(value.numerator, value.denominator))


def _mpfr_fraction(value: gmpy2.mpfr) -> Fraction:
    rational = gmpy2.mpq(value)
    return Fraction(int(rational.numerator), int(rational.denominator))


def _mp_interval(value: Fraction, precision: int) -> MPInterval:
    return MPInterval(
        _mp_fraction(value, precision, gmpy2.RoundDown),
        _mp_fraction(value, precision, gmpy2.RoundUp),
        precision,
    )


def _mp_binary(
    left: gmpy2.mpfr,
    right: gmpy2.mpfr,
    precision: int,
    rounding: int,
    operation: str,
) -> gmpy2.mpfr:
    with gmpy2.context(_context(precision, rounding)):
        if operation == "multiply":
            return +(left * right)
        if operation == "divide":
            return +(left / right)
    raise CandidateRawAxisFailure(HOLD_NUMERICAL, "unknown MPFR binary operation")


def _mp_multiply_nonnegative(left: MPInterval, right: MPInterval) -> MPInterval:
    if left.precision != right.precision or left.lower < 0 or right.lower < 0:
        raise CandidateRawAxisFailure(HOLD_NUMERICAL, "invalid nonnegative MPFR product")
    precision = left.precision
    return MPInterval(
        _mp_binary(left.lower, right.lower, precision, gmpy2.RoundDown, "multiply"),
        _mp_binary(left.upper, right.upper, precision, gmpy2.RoundUp, "multiply"),
        precision,
    )


def _mp_scale_nonnegative(value: MPInterval, factor: Fraction) -> MPInterval:
    if factor < 0:
        raise CandidateRawAxisFailure(HOLD_NUMERICAL, "negative MPFR scale")
    return _mp_multiply_nonnegative(value, _mp_interval(factor, value.precision))


def _mp_exp(value: Fraction, precision: int) -> MPInterval:
    source = _mp_interval(value, precision)
    with gmpy2.context(_context(precision, gmpy2.RoundDown)):
        lower = +gmpy2.exp(source.lower)
    with gmpy2.context(_context(precision, gmpy2.RoundUp)):
        upper = +gmpy2.exp(source.upper)
    return MPInterval(lower, upper, precision)


def _mp_bernoulli_positive(value: Fraction, precision: int) -> MPInterval:
    if value <= 0:
        raise CandidateRawAxisFailure(HOLD_NUMERICAL, "positive Bernoulli input required")
    source = _mp_interval(value, precision)
    one = _mp_fraction(Fraction(1), precision, gmpy2.RoundToNearest)
    with gmpy2.context(_context(precision, gmpy2.RoundDown)):
        denominator_lower = +(gmpy2.exp(source.lower) - one)
    with gmpy2.context(_context(precision, gmpy2.RoundUp)):
        denominator_upper = +(gmpy2.exp(source.upper) - one)
    if denominator_lower <= 0:
        raise CandidateRawAxisFailure(HOLD_NUMERICAL, "Bernoulli denominator is not positive")
    return MPInterval(
        _mp_binary(
            source.lower,
            denominator_upper,
            precision,
            gmpy2.RoundDown,
            "divide",
        ),
        _mp_binary(
            source.upper,
            denominator_lower,
            precision,
            gmpy2.RoundUp,
            "divide",
        ),
        precision,
    )


def _mp_bernoulli(value: Fraction, precision: int) -> MPInterval:
    if value == 0:
        return _mp_interval(Fraction(1), precision)
    if value > 0:
        return _mp_bernoulli_positive(value, precision)
    positive = -value
    return _mp_multiply_nonnegative(
        _mp_exp(positive, precision),
        _mp_bernoulli_positive(positive, precision),
    )


def _raw_mu(potential: Fraction, volume: Fraction, precision: int) -> ExactInterval:
    if volume <= 0:
        raise CandidateRawAxisFailure(HOLD_NUMERICAL, "nonpositive cell volume")
    return _mp_scale_nonnegative(_mp_exp(-potential, precision), volume).exact()


def _directed_rate(
    delta_potential: Fraction,
    diffusion: Fraction,
    origin_volume: Fraction,
    distance: Fraction,
    precision: int,
) -> ExactInterval:
    if diffusion <= 0 or origin_volume <= 0 or distance <= 0:
        raise CandidateRawAxisFailure(HOLD_NUMERICAL, "invalid directed-rate parameter")
    factor = diffusion / (origin_volume * distance)
    return _mp_scale_nonnegative(_mp_bernoulli(delta_potential, precision), factor).exact()


def _direct_kappa(
    origin_potential: Fraction,
    delta_potential: Fraction,
    diffusion: Fraction,
    distance: Fraction,
    precision: int,
) -> ExactInterval:
    if diffusion <= 0 or distance <= 0:
        raise CandidateRawAxisFailure(HOLD_NUMERICAL, "invalid direct-kappa parameter")
    return _mp_scale_nonnegative(
        _mp_multiply_nonnegative(
            _mp_exp(-origin_potential, precision),
            _mp_bernoulli(delta_potential, precision),
        ),
        diffusion / distance,
    ).exact()


def _modulo(value: Fraction, period: Fraction) -> Fraction:
    if period <= 0:
        raise CandidateRawAxisFailure(HOLD_MEMBER, "nonpositive periodic width")
    return value - (value // period) * period


def _reconstruct_partition(
    coordinate: str,
    configuration_axis: dict[str, Any],
    dynamics: dict[str, Any],
) -> dict[str, Any]:
    size = configuration_axis.get("size")
    alignment = configuration_axis.get("alignment")
    if type(size) is not int or size < 2 or size > MAX_AXIS_CELLS or type(alignment) is not str:
        raise CandidateRawAxisFailure(HOLD_MEMBER, "invalid configuration axis")
    if alignment in {"cell_centred_reflecting", "vertex_centred_reflecting_dual"}:
        lower = _binary64_fraction(configuration_axis.get("lower_binary64_hex"), label="axis lower")
        upper = _binary64_fraction(configuration_axis.get("upper_binary64_hex"), label="axis upper")
        if lower >= upper:
            raise CandidateRawAxisFailure(HOLD_MEMBER, "reflecting domain is reversed")
        width = upper - lower
        shift = Fraction(0)
        if alignment == "cell_centred_reflecting":
            step = width / size
            positions = [lower + (Fraction(index) + Fraction(1, 2)) * step for index in range(size)]
            segments = [
                [(lower + index * step, lower + (index + 1) * step)] for index in range(size)
            ]
            construction = "cell_centred_reflecting_scharfetter_gummel"
        else:
            step = width / (size - 1)
            positions = [lower + index * step for index in range(size)]
            boundaries = (
                [lower]
                + [lower + (Fraction(index) - Fraction(1, 2)) * step for index in range(1, size)]
                + [upper]
            )
            segments = [[(boundaries[index], boundaries[index + 1])] for index in range(size)]
            construction = "vertex_centred_reflecting_scharfetter_gummel"
        start = lower
        periodic = False
    elif alignment in {"cell_centred_periodic_base", "cell_centred_periodic_half_shift"}:
        start = _fraction(
            dynamics.get("transverse_domain_start_exact"), code=HOLD_MEMBER, label="period start"
        )
        width = _fraction(
            dynamics.get("transverse_period_exact"), code=HOLD_MEMBER, label="period width"
        )
        step = width / size
        shift = _fraction(
            configuration_axis.get("periodic_shift_exact"),
            code=HOLD_MEMBER,
            label="periodic shift",
        )
        expected_shift = Fraction(0) if alignment.endswith("_base") else step / 2
        if shift != expected_shift:
            raise CandidateRawAxisFailure(HOLD_MEMBER, "periodic shift mismatch")
        positions = [
            start + _modulo((Fraction(index) + Fraction(1, 2)) * step + shift, width)
            for index in range(size)
        ]
        end = start + width
        segments: list[list[tuple[Fraction, Fraction]]] = []
        for index in range(size):
            cell_start = start + _modulo(index * step + shift, width)
            cell_end = cell_start + step
            if cell_end <= end:
                segments.append([(cell_start, cell_end)])
            else:
                segments.append([(cell_start, end), (start, start + cell_end - end)])
        construction = (
            "cell_centred_periodic_diffusion"
            if alignment.endswith("_base")
            else "cell_centred_periodic_diffusion_half_shift"
        )
        periodic = True
    else:
        raise CandidateRawAxisFailure(HOLD_MEMBER, "unknown axis alignment")
    volumes = [sum((upper - lower for lower, upper in cell), Fraction(0)) for cell in segments]
    return {
        "cell_segments_exact": [
            [[_fraction_text(lower), _fraction_text(upper)] for lower, upper in cell]
            for cell in segments
        ],
        "cell_volumes_exact": [_fraction_text(value) for value in volumes],
        "construction": construction,
        "coordinate": coordinate,
        "domain_start_exact": _fraction_text(start),
        "domain_width_exact": _fraction_text(width),
        "periodic": periodic,
        "periodic_shift_exact": _fraction_text(shift),
        "positions_exact": [_fraction_text(value) for value in positions],
        "schema": PARTITION_SCHEMA,
        "size": size,
    }


def _runtime_versions() -> dict[str, str]:
    return {
        "gmp": gmpy2.mp_version(),
        "gmpy2": gmpy2.__version__,
        "mpc": gmpy2.mpc_version(),
        "mpfr": gmpy2.mpfr_version(),
        "python_abi": f"CPython {sys.version_info.major}.{sys.version_info.minor}",
    }


def _validate_runtime(request: dict[str, Any]) -> dict[str, str]:
    required = _exact_keys(
        request["runtime_requirements"], _RUNTIME_KEYS, code=HOLD_REQUEST, label="runtime"
    )
    if any(type(value) is not str or not value for value in required.values()):
        raise CandidateRawAxisFailure(HOLD_REQUEST, "runtime values must be nonempty strings")
    observed = _runtime_versions()
    if observed != required:
        raise CandidateRawAxisFailure(HOLD_RUNTIME, "runtime version mismatch")
    return observed


def _validate_method_registry(
    registry: dict[str, Any], selection: dict[str, Any]
) -> MethodParameters:
    _exact_keys(selection, _METHOD_SELECTION_KEYS, code=HOLD_REQUEST, label="method selection")
    _exact_keys(
        registry,
        _PARAMETER_REGISTRY_KEYS,
        code=HOLD_METHOD,
        label="parameter registry",
    )
    claims = registry["claim_boundary"]
    if (
        registry["schema"] != PARAMETER_SCHEMA
        or registry["status"] != PARAMETER_STATUS
        or type(claims) is not dict
        or set(claims) != _PREDECESSOR_CLAIM_KEYS
        or any(value is not False for value in claims.values())
    ):
        raise CandidateRawAxisFailure(HOLD_METHOD, "parameter registry boundary mismatch")
    _reject_result_observed_keys(registry, code=HOLD_METHOD, label="parameter registry")
    entries = registry["parameters"]
    if (
        type(entries) is not list
        or registry["parameter_count"] != 10
        or len(entries) != 10
        or [entry.get("parameter_id") if type(entry) is dict else None for entry in entries]
        != list(_PARAMETER_ORDER)
    ):
        raise CandidateRawAxisFailure(HOLD_METHOD, "parameter registry cardinality/order mismatch")
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if type(entry) is not dict or set(entry) != {
            "method_parameter_sha256",
            "parameter_id",
            "parameters",
        }:
            raise CandidateRawAxisFailure(HOLD_METHOD, "invalid parameter entry")
        identifier = entry["parameter_id"]
        parameters = entry["parameters"]
        digest = entry["method_parameter_sha256"]
        if (
            type(identifier) is not str
            or identifier in by_id
            or type(parameters) is not dict
            or not _is_sha256(digest)
            or digest != _domain_digest(PARAMETER_DIGEST_DOMAIN, parameters)
            or parameters.get("source_role_scope") != _PARAMETER_SCOPES.get(identifier)
            or (
                identifier
                in {
                    "stationary_directed_mpfr_640_sentinel_v2",
                    SENTINEL_PARAMETER_ID,
                }
                and parameters.get("containment_relation") != GENERIC_CONTAINMENT
            )
        ):
            raise CandidateRawAxisFailure(HOLD_METHOD, "parameter digest mismatch")
        by_id[identifier] = entry
    identifiers = {
        "primary": selection["primary_parameter_id"],
        "sentinel": selection["sentinel_parameter_id"],
        "binary64": selection["binary64_parameter_id"],
        "exact": selection["exact_parameter_id"],
    }
    if identifiers != {
        "primary": PRIMARY_PARAMETER_ID,
        "sentinel": SENTINEL_PARAMETER_ID,
        "binary64": BINARY64_PARAMETER_ID,
        "exact": EXACT_PARAMETER_ID,
    }:
        raise CandidateRawAxisFailure(HOLD_METHOD, "selected parameter identity mismatch")
    primary = by_id[identifiers["primary"]]["parameters"]
    sentinel = by_id[identifiers["sentinel"]]["parameters"]
    binary64 = by_id[identifiers["binary64"]]["parameters"]
    exact = by_id[identifiers["exact"]]["parameters"]
    scope = ["role8_raw_axis_formula_primitive"]
    expected_primary = {
        "aggregation": "exact_Fraction_endpoint_algebra",
        "common_kappa_rule": "intersection_after_formula_witness",
        "precision_bits": 320,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": scope,
    }
    expected_sentinel = {
        "containment_relation": GENERIC_CONTAINMENT,
        "independent_backend": False,
        "precision_bits": 640,
        "rounding_mode": "directed_RoundDown_RoundUp",
        "source_role_scope": scope,
    }
    expected_binary64 = {
        "decode": "exact_binary64_endpoint_to_reduced_dyadic_fraction",
        "precision_bits": 53,
        "rounding_mode": "stored_outward_endpoints",
        "source_role_scope": scope,
    }
    expected_exact = {
        "arithmetic": "Python_Fraction_exact_reduced_rationals",
        "precision_bits": "unbounded_integer_fraction",
        "rounding_mode": "exact",
        "source_role_scope": list(_PARAMETER_SCOPES[EXACT_PARAMETER_ID]),
    }
    if (
        not _json_exactly_equal(primary, expected_primary)
        or not _json_exactly_equal(sentinel, expected_sentinel)
        or not _json_exactly_equal(binary64, expected_binary64)
        or not _json_exactly_equal(exact, expected_exact)
    ):
        raise CandidateRawAxisFailure(HOLD_METHOD, "raw-axis method semantics mismatch")
    if (
        tuple(by_id[identifier]["method_parameter_sha256"] for identifier in _PARAMETER_ORDER)
        != _PARAMETER_DIGEST_ORDER
    ):
        raise CandidateRawAxisFailure(HOLD_METHOD, "registry normative parameter mismatch")
    return MethodParameters(
        primary_id=identifiers["primary"],
        sentinel_id=identifiers["sentinel"],
        binary64_id=identifiers["binary64"],
        exact_id=identifiers["exact"],
        primary_bits=320,
        sentinel_bits=640,
        parameter_digests={
            identifier: by_id[identifier]["method_parameter_sha256"]
            for identifier in identifiers.values()
        },
    )


def _walk_keys(value: Any) -> list[str]:
    result: list[str] = []
    if type(value) is dict:
        for key, item in value.items():
            result.append(key)
            result.extend(_walk_keys(item))
    elif type(value) is list:
        for item in value:
            result.extend(_walk_keys(item))
    return result


def _reject_result_observed_keys(value: Any, *, code: str, label: str) -> None:
    offending = sorted(
        {key for key in _walk_keys(value) if "result" in key.lower() or "observed" in key.lower()}
    )
    if offending:
        raise CandidateRawAxisFailure(
            code, f"{label}: result/observed metadata key forbidden: {offending[0]}"
        )


def _load_request(request_path: Path, output_path: Path) -> tuple[dict[str, Any], Snapshot]:
    request_snapshot = immutable_snapshot(request_path, cap=MAX_JSON_BYTES)
    request = _parse_canonical(request_snapshot.raw, label="request")
    _exact_keys(request, _REQUEST_KEYS, code=HOLD_REQUEST, label="request")
    if (
        request["schema"] != REQUEST_SCHEMA
        or request["status"] != "RESULT_BLIND_REQUEST_NOT_EXECUTION_RESULT"
    ):
        raise CandidateRawAxisFailure(HOLD_REQUEST, "request boundary mismatch")
    output = _exact_keys(request["output"], _OUTPUT_KEYS, code=HOLD_REQUEST, label="output")
    requested_output = _absolute_lexical(
        output["path"], code=HOLD_REQUEST, label="requested output"
    )
    if output["schema"] != OUTPUT_SCHEMA or requested_output != output_path:
        raise CandidateRawAxisFailure(HOLD_REQUEST, "request/CLI output mismatch")
    forbidden_fragments = (
        "artifact_sha",
        "expected_output",
        "output_sha",
    )
    if any(
        "result" in key.lower()
        or "observed" in key.lower()
        or any(fragment in key.lower() for fragment in forbidden_fragments)
        for key in _walk_keys(request)
    ):
        raise CandidateRawAxisFailure(HOLD_REQUEST, "request contains a result/observed pin")
    return request, request_snapshot


def _relative_pin_matches(
    pin: Any, snapshot: Snapshot, *, label: str, code: str = HOLD_MEMBER
) -> None:
    if type(pin) is not dict or set(pin) != {"path", "sha256"}:
        raise CandidateRawAxisFailure(code, f"{label}: invalid bound source pin")
    relative = pin["path"]
    if type(relative) is not str or type(pin["sha256"]) is not str:
        raise CandidateRawAxisFailure(code, f"{label}: invalid bound source values")
    pure = PurePosixPath(relative)
    if (
        pure.is_absolute()
        or ".." in pure.parts
        or not pure.parts
        or tuple(snapshot.path.parts[-len(pure.parts) :]) != pure.parts
        or pin["sha256"] != snapshot.sha256
    ):
        raise CandidateRawAxisFailure(code, f"{label}: request-bound source mismatch")


def _require_exact_authority(
    snapshot: Snapshot,
    *,
    relative_path: str,
    sha256: str,
    label: str,
    code: str,
) -> None:
    pure = PurePosixPath(relative_path)
    if snapshot.sha256 != sha256 or tuple(snapshot.path.parts[-len(pure.parts) :]) != pure.parts:
        raise CandidateRawAxisFailure(code, f"{label}: exact authority path/SHA mismatch")


def _schema_pin_matches(
    pin: Any,
    snapshot: Snapshot,
    *,
    expected_schema: str,
    label: str,
    code: str,
) -> None:
    current = _exact_keys(pin, _SCHEMA_PIN_KEYS, code=code, label=label)
    if current["schema"] != expected_schema:
        raise CandidateRawAxisFailure(code, f"{label}: schema mismatch")
    _relative_pin_matches(
        {"path": current["path"], "sha256": current["sha256"]},
        snapshot,
        label=label,
        code=code,
    )


def _require_snapshot_schema(
    snapshot: Snapshot,
    *,
    expected_schema: str,
    label: str,
    code: str,
) -> None:
    nested = _parse_canonical(snapshot.raw, label=label)
    if nested.get("schema") != expected_schema:
        raise CandidateRawAxisFailure(code, f"{label}: nested authority schema mismatch")


def _validate_false_claims(claims: Any, expected_keys: set[str], *, code: str, label: str) -> None:
    if (
        type(claims) is not dict
        or set(claims) != expected_keys
        or any(value is not False for value in claims.values())
    ):
        raise CandidateRawAxisFailure(code, f"{label}: false claim boundary mismatch")


def _validate_relative_pin_shape(pin: Any, *, code: str, label: str) -> dict[str, str]:
    current = _exact_keys(pin, _PIN_KEYS, code=code, label=label)
    relative = current["path"]
    digest = current["sha256"]
    pure = PurePosixPath(relative) if type(relative) is str else PurePosixPath("/")
    if (
        type(relative) is not str
        or pure.is_absolute()
        or ".." in pure.parts
        or not pure.parts
        or not _is_sha256(digest)
    ):
        raise CandidateRawAxisFailure(code, f"{label}: invalid relative source pin")
    return current


def _formula_contract() -> dict[str, str]:
    return {
        "bernoulli": "Bernoulli(s)=s/(exp(s)-1),Bernoulli(0)=1",
        "common_axis_flux": "kappa_edge=mu_i*q_i_to_j=mu_j*q_j_to_i",
        "discrete_killing": "k=B*V",
        "exact_adjoint_map": "P_h[u]_i=integral_C_i_u*pi_dx/pi_h_i",
        "global_gauge": "G=M_L/(S_midpoint*S_relative_parallel*S_relative_perpendicular)",
        "ideal_axis_mass": "mu_i=cell_volume_i*exp(-potential(representative_i))",
        "map_ratio": "rho_i=M_i_pi/pi_h_i",
        "periodic_axis_mass": "mu_i=cell_volume_i",
        "periodic_rate": "q=D_axis/(cell_width^2)",
        "physical_cell_mass": "M_i_pi=integral_C_i_pi_dx",
        "reconstructed_killing_multiplier": "K=V/rho",
        "reflecting_sg_rate": (
            "q_i_to_j=D_axis/(cell_volume_i*distance_ij)*Bernoulli(potential_j-potential_i)"
        ),
        "tensor_common_conductance": ("c_edge=G*kappa_axis_edge*product_spectator_axis_mu"),
        "tensor_gauged_mass": "pi_h_tensor=G*product_axis_mu",
    }


def _axis_construction_contract() -> dict[str, dict[str, str]]:
    periodic_common = {
        "boundary_rule": "periodic_endpoints_identified_no_duplicate_endpoint",
        "cardinality_semantics": "size_equal_periodic_control_volumes",
        "cell_segments_formula": (
            "[domain_start+mod(i*h+shift,width),"
            "domain_start+mod(i*h+shift,width)+h] split into two ordered segments "
            "when it crosses domain_start+width"
        ),
        "cell_volumes_formula": "h for every cell",
        "positions_formula": ("domain_start+mod((i+1/2)*h+shift,width), i=0,...,size-1"),
        "step_formula": "h=width/size",
    }
    return {
        "cell_centred_periodic_base": {
            **periodic_common,
            "shift_formula": "shift=0",
            "source_construction_tag": "cell_centred_periodic_diffusion",
        },
        "cell_centred_periodic_half_shift": {
            **periodic_common,
            "shift_formula": "shift=h/2",
            "source_construction_tag": "cell_centred_periodic_diffusion_half_shift",
        },
        "cell_centred_reflecting": {
            "boundary_rule": "reflecting_zero_flux_no_transition_through_endpoints",
            "cardinality_semantics": "size_equal_control_volumes",
            "cell_segments_formula": ("C_i=[lower+i*h,lower+(i+1)*h], i=0,...,size-1"),
            "cell_volumes_formula": "h for every cell",
            "positions_formula": "lower+(i+1/2)*h, i=0,...,size-1",
            "source_construction_tag": "cell_centred_reflecting_scharfetter_gummel",
            "step_formula": "h=(upper-lower)/size",
        },
        "vertex_centred_reflecting_dual": {
            "boundary_rule": "reflecting_zero_flux_no_transition_through_endpoints",
            "cardinality_semantics": (
                "size_vertices_and_size_dual_control_volumes_with_size_minus_one_intervals"
            ),
            "cell_segments_formula": (
                "with x_i=lower+i*h and boundaries=(x_0,(x_0+x_1)/2,...,"
                "(x_(size-2)+x_(size-1))/2,x_(size-1)), "
                "C_i=[boundary_i,boundary_(i+1)]"
            ),
            "cell_volumes_formula": "h/2 at i=0 and i=size-1; h otherwise",
            "positions_formula": "lower+i*h, i=0,...,size-1",
            "source_construction_tag": ("vertex_centred_reflecting_scharfetter_gummel"),
            "step_formula": "h=(upper-lower)/(size-1)",
        },
    }


def _validate_factorization_authority(
    factorization: dict[str, Any], snapshots: dict[str, Snapshot]
) -> None:
    _exact_keys(
        factorization,
        _FACTORIZATION_KEYS,
        code=HOLD_INPUT,
        label="factorization",
    )
    _reject_result_observed_keys(factorization, code=HOLD_INPUT, label="factorization")
    _validate_false_claims(
        factorization["claim_boundary"],
        _PREDECESSOR_CLAIM_KEYS,
        code=HOLD_INPUT,
        label="factorization",
    )
    if (
        factorization["schema"] != FACTORIZATION_SCHEMA
        or factorization["status"] != FACTORIZATION_STATUS
    ):
        raise CandidateRawAxisFailure(HOLD_INPUT, "factorization boundary mismatch")
    pins = _exact_keys(
        factorization["source_pins"],
        {
            "configuration_source",
            "initial_partition_bundle",
            "killing_geometry_source",
        },
        code=HOLD_INPUT,
        label="factorization source pins",
    )
    _schema_pin_matches(
        pins["configuration_source"],
        snapshots["configuration"],
        expected_schema=CONFIGURATION_SCHEMA,
        label="factorization configuration source",
        code=HOLD_INPUT,
    )
    _schema_pin_matches(
        pins["initial_partition_bundle"],
        snapshots["factorization_initial_partition_bundle"],
        expected_schema="encounter_control_free_production_initial_stream_v1",
        label="factorization initial partition bundle",
        code=HOLD_INPUT,
    )
    _require_snapshot_schema(
        snapshots["factorization_initial_partition_bundle"],
        expected_schema="encounter_control_free_production_initial_stream_v1",
        label="factorization initial partition bundle",
        code=HOLD_INPUT,
    )
    _schema_pin_matches(
        pins["killing_geometry_source"],
        snapshots["factorization_killing_geometry"],
        expected_schema="encounter_physical_killing_geometry_source_v1",
        label="factorization killing geometry source",
        code=HOLD_INPUT,
    )
    _require_snapshot_schema(
        snapshots["factorization_killing_geometry"],
        expected_schema="encounter_physical_killing_geometry_source_v1",
        label="factorization killing geometry source",
        code=HOLD_INPUT,
    )


def _validate_nested_authorities(
    reference: dict[str, Any],
    formula: dict[str, Any],
    configuration: dict[str, Any],
    member: dict[str, Any],
    snapshots: dict[str, Snapshot],
) -> None:
    for label, value, code in (
        ("reference", reference, HOLD_INPUT),
        ("formula", formula, HOLD_INPUT),
        ("configuration", configuration, HOLD_INPUT),
        ("member", member, HOLD_MEMBER),
    ):
        _reject_result_observed_keys(value, code=code, label=label)
    _validate_false_claims(
        reference["claim_boundary"],
        _REFERENCE_CLAIM_KEYS,
        code=HOLD_INPUT,
        label="reference",
    )
    if (
        reference["status"]
        != "FROZEN_CONTROL_FREE_REFERENCE_DENSITY_AUTHORITY_ONLY_NO_COMPLETE_C0_C1_C2"
        or not _json_exactly_equal(
            reference["boundary_and_measure"],
            {
                "finite_nonperiodic_faces": "reflecting_zero_flux_approximants",
                "finite_periodic_coordinate": "relative_perpendicular_mod_W",
                "physical_cell_measure": (
                    "d_midpoint*d_relative_parallel*d_relative_perpendicular"
                ),
                "target_nonperiodic_domain": "R_times_R",
                "target_periodic_domain": "T_W",
            },
        )
        or not _json_exactly_equal(
            reference["diffusion_and_drift"],
            {
                "diffusion_diagonal": [
                    "particle_diffusion/2",
                    "2*particle_diffusion",
                    "2*particle_diffusion",
                ],
                "drift": [
                    "-ou_stiffness*(midpoint-ou_mean)",
                    "-ou_stiffness*relative_parallel",
                    "0/1",
                ],
            },
        )
        or not _json_exactly_equal(
            reference["normalization"],
            {
                "box_mass": "M_L=integral_Omega_L_pi_dx",
                "conditional_box_renormalization_used": False,
                "full_space_normalizer": "Z=2*pi*particle_diffusion*W/ou_stiffness",
                "periodic_factor": "1/W",
                "reference_density": (
                    "pi=Z^-1*exp[-ou_stiffness*(midpoint-ou_mean)^2/"
                    "particle_diffusion-ou_stiffness*relative_parallel^2/"
                    "(4*particle_diffusion)]"
                ),
                "restricted_density_retains_global_normalization": True,
            },
        )
        or not _json_exactly_equal(
            reference["unit_table"],
            {
                "box_mass_M_L": "dimensionless_probability",
                "diffusion_coefficients": "length_squared_per_time",
                "full_space_normalizer_Z": "length_cubed",
                "ou_stiffness": "inverse_time",
                "physical_cell_measure": "length_cubed",
                "reference_density_pi": "inverse_length_cubed",
                "spatial_coordinates": "length",
                "transverse_period_W": "length",
            },
        )
    ):
        raise CandidateRawAxisFailure(HOLD_INPUT, "reference nested semantics mismatch")
    reference_pins = _exact_keys(
        reference["source_pins"],
        {"c0_mathematical_source", "configuration_source"},
        code=HOLD_INPUT,
        label="reference source pins",
    )
    _validate_relative_pin_shape(
        reference_pins["c0_mathematical_source"],
        code=HOLD_INPUT,
        label="reference c0 pin",
    )
    _relative_pin_matches(
        reference_pins["configuration_source"],
        snapshots["configuration"],
        label="reference configuration source",
        code=HOLD_INPUT,
    )

    _validate_false_claims(
        formula["claim_boundary"],
        _FORMULA_CLAIM_KEYS,
        code=HOLD_INPUT,
        label="formula",
    )
    if (
        formula["status"]
        != "FROZEN_CONTROL_FREE_IDEAL_FORMULA_AUTHORITY_ONLY_NO_PRODUCTION_ACCEPTANCE"
        or not _json_exactly_equal(formula["formulae"], _formula_contract())
        or not _json_exactly_equal(
            formula["potential_formulae"],
            {
                "midpoint": "ou_stiffness*(x-ou_mean)^2/particle_diffusion",
                "relative_parallel": "ou_stiffness*x^2/(4*particle_diffusion)",
                "relative_perpendicular": "0/1",
            },
        )
        or not _json_exactly_equal(
            formula["member_semantics"],
            {
                "common_flux_uses_one_formula_defined_exact_value": True,
                "formula_defined_member_is_independent_of_production_centres": True,
                "global_gauge_is_single_scalar_per_configuration": True,
                "one_correlated_distinguished_member_required": True,
            },
        )
    ):
        raise CandidateRawAxisFailure(HOLD_INPUT, "formula nested semantics mismatch")
    formula_pins = _exact_keys(
        formula["source_pins"],
        {"c0_mathematical_source", "production_bridge_design"},
        code=HOLD_INPUT,
        label="formula source pins",
    )
    c0_formula = _validate_relative_pin_shape(
        formula_pins["c0_mathematical_source"],
        code=HOLD_INPUT,
        label="formula c0 pin",
    )
    c0_reference = reference_pins["c0_mathematical_source"]
    _validate_relative_pin_shape(
        formula_pins["production_bridge_design"],
        code=HOLD_INPUT,
        label="formula design pin",
    )
    if c0_formula != c0_reference:
        raise CandidateRawAxisFailure(HOLD_INPUT, "reference/formula c0 source pin mismatch")

    dynamics = _exact_keys(
        configuration["dynamics"], _DYNAMICS_KEYS, code=HOLD_INPUT, label="dynamics"
    )
    if (
        configuration["status"] != "CONTROL_FREE_GEOMETRY_SPEC_ONLY_NOT_F0_NOT_F1"
        or configuration["scope"] != "physical_d2_control_free_axis_and_initial_geometry_only"
        or configuration["workload_semantics"]
        != ("sum_of_state_counts_across_the_12_prescribed_axis_triples_for_one_future_control")
        or not _json_exactly_equal(
            configuration["axis_construction_contracts"],
            _axis_construction_contract(),
        )
        or dynamics["directed_precision_bits"] != 192
        or dynamics["midpoint_diffusion_formula"] != "particle_diffusion/2"
        or dynamics["midpoint_potential_formula"]
        != "ou_stiffness*(x-ou_mean)^2/(2*midpoint_diffusion)"
        or dynamics["relative_diffusion_formula"] != "2*particle_diffusion"
        or dynamics["relative_parallel_mean_exact"] != "0/1"
        or dynamics["relative_parallel_potential_formula"]
        != "ou_stiffness*x^2/(2*relative_diffusion)"
        or dynamics["relative_perpendicular_potential_formula"] != "0/1"
    ):
        raise CandidateRawAxisFailure(HOLD_INPUT, "configuration nested semantics mismatch")
    for key in (
        "ou_mean_binary64_hex",
        "ou_stiffness_binary64_hex",
        "particle_diffusion_binary64_hex",
    ):
        _binary64_fraction(dynamics[key], label=f"dynamics {key}")
    if _fraction(dynamics["transverse_period_exact"], label="dynamics period") <= 0:
        raise CandidateRawAxisFailure(HOLD_INPUT, "configuration period is nonpositive")
    _fraction(dynamics["transverse_domain_start_exact"], label="dynamics period start")
    authority = _exact_keys(
        configuration["authority"],
        {
            "design_path",
            "design_sha256",
            "implementation_path",
            "implementation_sha256",
            "test_path",
            "test_sha256",
        },
        code=HOLD_INPUT,
        label="configuration authority",
    )
    for prefix in ("design", "implementation", "test"):
        _relative_pin_matches(
            {
                "path": authority[f"{prefix}_path"],
                "sha256": authority[f"{prefix}_sha256"],
            },
            snapshots[f"configuration_{prefix}"],
            label=f"configuration {prefix} pin",
            code=HOLD_INPUT,
        )
    initial = _exact_keys(
        configuration["initial_geometry"],
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
        code=HOLD_INPUT,
        label="initial geometry",
    )
    starts = _exact_keys(
        initial["starts_binary64_hex"],
        set(COORDINATES),
        code=HOLD_INPUT,
        label="initial starts",
    )
    if (
        initial["construction"]
        != "independent_product_of_three_analytically_normalized_compact_bumps"
        or initial["normalization"] != "I_b=integral_-1^1_b(u)_du"
        or initial["periodic_wrap"] != "sum_over_periodic_images_before_cell_integration"
        or initial["shape_definition"] != "b(u)=indicator(abs(u)<1)*exp(-1/(1-u^2))"
        or initial["source_schema"] != "encounter_physical_initial_analytic_source_v1"
    ):
        raise CandidateRawAxisFailure(HOLD_INPUT, "initial geometry semantics mismatch")
    _validate_relative_pin_shape(
        {"path": initial["source_path"], "sha256": initial["source_sha256"]},
        code=HOLD_INPUT,
        label="initial geometry source",
    )
    if _binary64_fraction(initial["half_width_binary64_hex"], label="initial half width") <= 0:
        raise CandidateRawAxisFailure(HOLD_INPUT, "initial half width is nonpositive")
    for coordinate, value in starts.items():
        _binary64_fraction(value, label=f"initial start {coordinate}")

    _validate_false_claims(
        member["claim_boundary"],
        _PREDECESSOR_CLAIM_KEYS,
        code=HOLD_MEMBER,
        label="member",
    )
    if member["status"] != (
        "STRUCTURAL_PARTITION_IDENTITY_CANDIDATE_ONLY_NOT_EXTERNALLY_"
        "COMMITTED_NOT_PRODUCTION_MEMBER"
    ):
        raise CandidateRawAxisFailure(HOLD_MEMBER, "member status mismatch")
    lineage = _exact_keys(
        member["source_lineage_evidence"],
        {
            "initial_partition_bundle",
            "joint_refinement_family",
            "legacy_member_spec",
            "round176_member_candidate",
        },
        code=HOLD_MEMBER,
        label="member lineage",
    )
    for label, pin in lineage.items():
        _validate_relative_pin_shape(pin, code=HOLD_MEMBER, label=f"member lineage {label}")


def _validate_source_semantics(
    reference: dict[str, Any],
    formula: dict[str, Any],
    configuration: dict[str, Any],
    factorization: dict[str, Any],
    member: dict[str, Any],
    snapshots: dict[str, Snapshot],
) -> None:
    _exact_keys(reference, _REFERENCE_KEYS, code=HOLD_INPUT, label="reference")
    _exact_keys(formula, _FORMULA_KEYS, code=HOLD_INPUT, label="formula")
    _exact_keys(configuration, _CONFIGURATION_KEYS, code=HOLD_INPUT, label="configuration")
    _exact_keys(member, _MEMBER_KEYS, code=HOLD_MEMBER, label="member")
    if (
        reference["schema"] != REFERENCE_SCHEMA
        or formula["schema"] != FORMULA_SCHEMA
        or configuration["schema"] != CONFIGURATION_SCHEMA
        or member["schema"] != MEMBER_SCHEMA
    ):
        raise CandidateRawAxisFailure(HOLD_INPUT, "source schema mismatch")
    _validate_factorization_authority(factorization, snapshots)
    _validate_nested_authorities(reference, formula, configuration, member, snapshots)
    if (
        reference["coordinate_order"] != list(COORDINATES)
        or configuration["coordinate_order"] != list(COORDINATES)
        or configuration["authorizes_scientific_execution"] is not False
        or configuration["contains_budget_value"] is not False
        or configuration["contains_control_values"] is not False
    ):
        raise CandidateRawAxisFailure(HOLD_INPUT, "normalization/configuration boundary mismatch")
    reference_parameters = _exact_keys(
        reference["physical_parameter_bundle"],
        {
            "ou_mean_binary64_hex",
            "ou_stiffness_binary64_hex",
            "particle_diffusion_binary64_hex",
            "physical_dimension",
            "quotient_dimension",
            "transverse_period_exact",
        },
        code=HOLD_INPUT,
        label="physical parameter bundle",
    )
    dynamics = configuration["dynamics"]
    if type(reference_parameters) is not dict or type(dynamics) is not dict:
        raise CandidateRawAxisFailure(HOLD_INPUT, "physical parameter bundle missing")
    shared = (
        "ou_mean_binary64_hex",
        "ou_stiffness_binary64_hex",
        "particle_diffusion_binary64_hex",
        "transverse_period_exact",
    )
    if any(reference_parameters.get(key) != dynamics.get(key) for key in shared):
        raise CandidateRawAxisFailure(HOLD_INPUT, "reference/configuration parameter mismatch")
    if (
        reference_parameters.get("physical_dimension") != configuration["physical_dimension"]
        or reference_parameters.get("quotient_dimension") != configuration["quotient_dimension"]
        or reference_parameters.get("physical_dimension") != 2
        or reference_parameters.get("quotient_dimension") != 3
    ):
        raise CandidateRawAxisFailure(HOLD_INPUT, "dimension mismatch")
    role_bindings = member["role_bindings"]
    if type(role_bindings) is not dict or set(role_bindings) != {
        "configuration_source",
        "factorization_source",
        "ideal_formula_source",
        "reference_density_source",
    }:
        raise CandidateRawAxisFailure(HOLD_MEMBER, "member role bindings mismatch")
    _relative_pin_matches(
        role_bindings["factorization_source"],
        snapshots["factorization"],
        label="member factorization source",
        code=HOLD_MEMBER,
    )
    _relative_pin_matches(
        role_bindings["configuration_source"], snapshots["configuration"], label="configuration"
    )
    _relative_pin_matches(
        role_bindings["ideal_formula_source"], snapshots["ideal_formula"], label="formula"
    )
    _relative_pin_matches(
        role_bindings["reference_density_source"], snapshots["reference_density"], label="reference"
    )


def _validate_member_and_partitions(
    request: dict[str, Any],
    member: dict[str, Any],
    reference: dict[str, Any],
    configuration: dict[str, Any],
) -> tuple[list[tuple[dict[str, Any], list[dict[str, Any]]]], list[dict[str, Any]]]:
    parameters = reference["physical_parameter_bundle"]
    rows = configuration["configurations"]
    bindings = member["n0_sequence_bindings"]
    order = member["configuration_order"]
    semantics = member["configuration_semantic_ids"]
    if (
        type(rows) is not list
        or type(bindings) is not list
        or type(order) is not list
        or type(semantics) is not list
        or not 1 <= len(rows) <= MAX_CONFIGURATIONS
        or not len(rows) == len(bindings) == len(order) == len(semantics)
        or configuration["configuration_count"] != len(rows)
        or configuration["configuration_order"] != order
    ):
        raise CandidateRawAxisFailure(HOLD_MEMBER, "candidate cardinality/order mismatch")
    member_semantics = member["member_semantics"]
    if (
        type(member_semantics) is not dict
        or set(member_semantics)
        != {
            "configuration_count",
            "configuration_rows_are_finite_anchors",
            "coordinate_order",
            "every_cartesian_interval_endpoint_combination_is_a_model",
            "one_formula_defined_correlated_member_per_configuration",
            "physical_dimension",
            "quotient_dimension",
            "scalar_convention",
        }
        or member_semantics.get("configuration_count") != len(rows)
        or member_semantics.get("coordinate_order") != list(COORDINATES)
        or member_semantics.get("configuration_rows_are_finite_anchors") is not True
        or member_semantics.get("every_cartesian_interval_endpoint_combination_is_a_model")
        is not False
        or member_semantics.get("one_formula_defined_correlated_member_per_configuration")
        is not True
        or member_semantics.get("physical_dimension") != 2
        or member_semantics.get("quotient_dimension") != 3
        or member_semantics.get("scalar_convention")
        != "complex_inner_product_conjugate_first_factor"
    ):
        raise CandidateRawAxisFailure(HOLD_MEMBER, "candidate member semantics mismatch")
    parameter_digest = _domain_digest("encounter-physical-parameter-bundle-v1", parameters)

    raw_partition_pins = request["partitions"]
    if type(raw_partition_pins) is not list or len(raw_partition_pins) != 3 * len(rows):
        raise CandidateRawAxisFailure(HOLD_REQUEST, "partition request cardinality mismatch")
    requested: dict[tuple[int, str], dict[str, Any]] = {}
    expected_order = [
        (index, coordinate) for index in range(len(rows)) for coordinate in COORDINATES
    ]
    for ordinal, raw_pin in enumerate(raw_partition_pins):
        pin = _exact_keys(raw_pin, _PARTITION_PIN_KEYS, code=HOLD_REQUEST, label="partition pin")
        index = pin["configuration_index"]
        coordinate = pin["coordinate"]
        if (
            type(index) is not int
            or type(coordinate) is not str
            or (index, coordinate) != expected_order[ordinal]
            or (index, coordinate) in requested
            or not _is_sha256(pin["sha256"])
        ):
            raise CandidateRawAxisFailure(HOLD_REQUEST, "invalid/unsorted partition pin")
        requested[(index, coordinate)] = pin

    dynamics = configuration["dynamics"]
    result: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    output_pins: list[dict[str, Any]] = []
    identity_bindings: list[dict[str, Any]] = []
    seen_labels: set[str] = set()
    seen_sequences: set[str] = set()
    total_states = 0
    axis_cell_count = 0
    axis_edge_count = 0
    periodic_seam_count = 0
    alignment_counts = {
        "cell_centred_periodic_base": 0,
        "cell_centred_periodic_half_shift": 0,
        "cell_centred_reflecting": 0,
        "vertex_centred_reflecting_dual": 0,
    }
    for index, (row, binding, label, semantic) in enumerate(
        zip(rows, bindings, order, semantics, strict=True)
    ):
        _exact_keys(
            row,
            {
                "expected_states",
                "label",
                "midpoint",
                "purpose",
                "relative_parallel",
                "relative_perpendicular",
                "shape",
            },
            code=HOLD_MEMBER,
            label="configuration row",
        )
        _exact_keys(
            binding,
            {
                "authority_label",
                "configuration_geometry_sha256",
                "configuration_index",
                "initial_partition_row_manifest_path",
                "initial_partition_row_manifest_sha256",
                "n0_anchor_expected_states",
                "n0_anchor_shape",
                "n0_axes",
                "physical_parameter_bundle_sha256",
                "refinement_family_id",
                "refinement_member_id",
                "sequence_id",
                "sequence_source_row_canonical_sha256",
                "sequence_source_row_index",
            },
            code=HOLD_MEMBER,
            label="member sequence binding",
        )
        _exact_keys(
            semantic,
            {"authority_label", "refinement_family_id", "refinement_member_id"},
            code=HOLD_MEMBER,
            label="member semantic id",
        )
        if (
            type(label) is not str
            or not label
            or row.get("label") != label
            or type(row.get("purpose")) is not str
            or not row["purpose"]
            or binding.get("authority_label") != label
            or type(binding.get("configuration_index")) is not int
            or binding.get("configuration_index") != index
            or type(binding.get("sequence_source_row_index")) is not int
            or binding.get("sequence_source_row_index") != index
            or semantic.get("authority_label") != label
            or type(semantic.get("refinement_family_id")) is not str
            or not semantic["refinement_family_id"]
            or type(semantic.get("refinement_member_id")) is not str
            or not semantic["refinement_member_id"]
            or type(binding.get("refinement_family_id")) is not str
            or not binding["refinement_family_id"]
            or type(binding.get("refinement_member_id")) is not str
            or not binding["refinement_member_id"]
            or label in seen_labels
        ):
            raise CandidateRawAxisFailure(HOLD_MEMBER, "candidate row identity mismatch")
        seen_labels.add(label)
        sequence_id = binding.get("sequence_id")
        if type(sequence_id) is not str or not sequence_id or sequence_id in seen_sequences:
            raise CandidateRawAxisFailure(HOLD_MEMBER, "duplicate sequence identity")
        seen_sequences.add(sequence_id)
        _validate_relative_pin_shape(
            {
                "path": binding["initial_partition_row_manifest_path"],
                "sha256": binding["initial_partition_row_manifest_sha256"],
            },
            code=HOLD_MEMBER,
            label="initial partition row manifest",
        )
        row_sha = hashlib.sha256(canonical_bytes(row)).hexdigest()
        shape = row.get("shape")
        expected_states = row.get("expected_states")
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(size) is not int or size < 2 for size in shape)
            or type(expected_states) is not int
            or math.prod(shape) != expected_states
            or binding.get("sequence_source_row_canonical_sha256") != row_sha
            or binding.get("physical_parameter_bundle_sha256") != parameter_digest
            or binding.get("n0_anchor_expected_states") != expected_states
            or binding.get("n0_anchor_shape") != shape
            or binding.get("refinement_family_id") != semantic.get("refinement_family_id")
            or binding.get("refinement_member_id") != semantic.get("refinement_member_id")
        ):
            raise CandidateRawAxisFailure(HOLD_MEMBER, "candidate row/binding mismatch")
        total_states += expected_states
        axes = binding.get("n0_axes")
        if type(axes) is not list or len(axes) != 3:
            raise CandidateRawAxisFailure(HOLD_MEMBER, "candidate axis binding mismatch")
        loaded: list[dict[str, Any]] = []
        partition_hashes: list[str] = []
        for axis_index, (coordinate, axis_binding) in enumerate(
            zip(COORDINATES, axes, strict=True)
        ):
            config_axis = row.get(coordinate)
            if type(config_axis) is not dict:
                raise CandidateRawAxisFailure(HOLD_MEMBER, "configuration axis is not an object")
            alignment = config_axis.get("alignment")
            expected_config_axis_keys = (
                {"alignment", "lower_binary64_hex", "size", "upper_binary64_hex"}
                if alignment in {"cell_centred_reflecting", "vertex_centred_reflecting_dual"}
                else {"alignment", "periodic_shift_exact", "size"}
            )
            _exact_keys(
                config_axis,
                expected_config_axis_keys,
                code=HOLD_MEMBER,
                label="configuration axis",
            )
            if alignment not in alignment_counts:
                raise CandidateRawAxisFailure(HOLD_MEMBER, "unknown alignment")
            alignment_counts[alignment] += 1
            expected_axis_binding_keys = {
                "alignment",
                "cell_count",
                "coordinate",
                "exact_box_or_period",
                "partition_report_relative_path",
                "partition_schema",
                "partition_sha256",
                "periodic",
                "refinement_family_id",
                "refinement_member_id",
                "sequence_id",
                "sequence_source_row_canonical_sha256",
            }
            if alignment.startswith("cell_centred_periodic"):
                expected_axis_binding_keys.add("periodic_shift_n0_exact")
            _exact_keys(
                axis_binding,
                expected_axis_binding_keys,
                code=HOLD_MEMBER,
                label="member axis binding",
            )
            if (
                type(axis_binding) is not dict
                or axis_binding.get("coordinate") != coordinate
                or axis_binding.get("alignment") != config_axis.get("alignment")
                or shape[axis_index] != config_axis.get("size")
            ):
                raise CandidateRawAxisFailure(HOLD_MEMBER, "candidate axis order mismatch")
            request_pin = requested[(index, coordinate)]
            member_relative = axis_binding.get("partition_report_relative_path")
            if (
                type(member_relative) is not str
                or request_pin["member_report_relative_path"] != member_relative
                or request_pin["sha256"] != axis_binding.get("partition_sha256")
                or axis_binding.get("partition_schema") != PARTITION_SCHEMA
                or axis_binding.get("refinement_family_id") != binding.get("refinement_family_id")
                or axis_binding.get("refinement_member_id") != binding.get("refinement_member_id")
                or axis_binding.get("sequence_id") != sequence_id
                or axis_binding.get("sequence_source_row_canonical_sha256") != row_sha
            ):
                raise CandidateRawAxisFailure(HOLD_MEMBER, "member/request partition mismatch")
            pure = PurePosixPath(member_relative)
            absolute = _absolute_lexical(
                request_pin["path"], code=HOLD_REQUEST, label="partition path"
            )
            if (
                pure.is_absolute()
                or ".." in pure.parts
                or not pure.parts
                or tuple(absolute.parts[-len(pure.parts) :]) != pure.parts
            ):
                raise CandidateRawAxisFailure(HOLD_MEMBER, "partition path suffix mismatch")
            snapshot = immutable_snapshot(absolute, cap=MAX_JSON_BYTES)
            if snapshot.sha256 != request_pin["sha256"]:
                raise CandidateRawAxisFailure(HOLD_INPUT, "partition SHA-256 mismatch")
            partition = _parse_canonical(snapshot.raw, label=f"partition {index}:{coordinate}")
            expected = _reconstruct_partition(coordinate, config_axis, dynamics)
            if not _json_exactly_equal(partition, expected):
                raise CandidateRawAxisFailure(
                    HOLD_MEMBER, f"partition geometry mismatch at {index}:{coordinate}"
                )
            if (
                axis_binding.get("cell_count") != partition["size"]
                or axis_binding.get("periodic") is not partition["periodic"]
                or axis_binding.get("exact_box_or_period")
                != {
                    "domain_start_exact": partition["domain_start_exact"],
                    "domain_width_exact": partition["domain_width_exact"],
                }
                or (
                    partition["periodic"]
                    and axis_binding.get("periodic_shift_n0_exact")
                    != partition["periodic_shift_exact"]
                )
            ):
                raise CandidateRawAxisFailure(HOLD_MEMBER, "axis geometry binding mismatch")
            loaded.append(partition)
            partition_hashes.append(snapshot.sha256)
            axis_cell_count += partition["size"]
            axis_edge_count += partition["size"] if partition["periodic"] else partition["size"] - 1
            periodic_seam_count += int(partition["periodic"])
            output_pins.append(
                {
                    "configuration_index": index,
                    "coordinate": coordinate,
                    "path": str(absolute),
                    "sha256": snapshot.sha256,
                }
            )
        geometry_record = {
            "configuration_index": index,
            "configuration_row": row,
            "n0_partition_sha256s": partition_hashes,
        }
        if binding.get("configuration_geometry_sha256") != _domain_digest(
            "encounter-configuration-geometry-v1", geometry_record
        ):
            raise CandidateRawAxisFailure(HOLD_MEMBER, "configuration geometry digest mismatch")
        result.append((binding, loaded))
        identity_bindings.append(binding)

    if configuration["total_state_workload"] != total_states:
        raise CandidateRawAxisFailure(HOLD_MEMBER, "configuration workload mismatch")
    expected_reconstruction = {
        "axis_cell_count": axis_cell_count,
        "axis_count": 3 * len(rows),
        "axis_edge_count": axis_edge_count,
        "configuration_count": len(rows),
        "periodic_seam_count": periodic_seam_count,
        "profile_index_count": 4 * len(rows),
        "total_virtual_tensor_state_count": total_states,
    }
    if not _json_exactly_equal(member["reconstruction_counts"], expected_reconstruction):
        raise CandidateRawAxisFailure(HOLD_MEMBER, "member reconstruction counts mismatch")
    if not _json_exactly_equal(
        member["identity_properties"],
        {
            "alignment_counts": alignment_counts,
            "candidate_authoritative": False,
            "current_enclosures_bind_this_candidate": False,
            "n0_partition_sha256s_structurally_bound": True,
            "partition_file_count": 3 * len(rows),
            "round172_source_itself_contains_partition_sha256": False,
            "source_roles_1_through_4_only_in_production_role_bindings": True,
        },
    ):
        raise CandidateRawAxisFailure(HOLD_MEMBER, "member identity properties mismatch")
    identity = {
        "configuration_order": order,
        "configuration_semantic_ids": semantics,
        "coordinate_order": list(COORDINATES),
        "n0_sequence_bindings": identity_bindings,
        "role_bindings_1_through_4": member["role_bindings"],
        "scalar_convention": member_semantics.get("scalar_convention"),
    }
    if member.get("member_identity_sha256") != _domain_digest(
        "encounter-continuum-c1-c2-n0-member-identity-v3", identity
    ):
        raise CandidateRawAxisFailure(HOLD_MEMBER, "member identity digest mismatch")
    return result, output_pins


def _potentials(
    coordinate: str,
    positions: list[Fraction],
    *,
    stiffness: Fraction,
    diffusion: Fraction,
    mean: Fraction,
) -> list[Fraction]:
    if coordinate == "midpoint":
        return [stiffness * (position - mean) ** 2 / diffusion for position in positions]
    if coordinate == "relative_parallel":
        return [stiffness * position**2 / (4 * diffusion) for position in positions]
    if coordinate == "relative_perpendicular":
        return [Fraction(0) for _ in positions]
    raise CandidateRawAxisFailure(HOLD_MEMBER, "unknown coordinate")


def _four_way_intersection(values: Sequence[ExactInterval]) -> ExactInterval:
    if len(values) != 4:
        raise CandidateRawAxisFailure(HOLD_NUMERICAL, "four common-flux witnesses required")
    result = values[0]
    for value in values[1:]:
        result = result.intersect(value)
    return result


def _relative_width(value: ExactInterval) -> Fraction:
    if value.lower <= 0:
        raise CandidateRawAxisFailure(HOLD_NUMERICAL, "positive interval required")
    return (value.upper - value.lower) / value.lower


def build_from_request(request_path: Path, output_path: Path) -> bytes:
    request, request_snapshot = _load_request(request_path, output_path)
    runtime = _validate_runtime(request)
    authorities = _exact_keys(
        request["input_authorities"],
        _INPUT_AUTHORITY_KEYS,
        code=HOLD_REQUEST,
        label="input authorities",
    )
    code_inputs = _exact_keys(
        request["code_inputs"],
        {"producer", "verifier"},
        code=HOLD_REQUEST,
        label="code inputs",
    )
    snapshots = {
        role: _pin_snapshot(pin, label=role) for role, pin in {**authorities, **code_inputs}.items()
    }
    current_source = Path(os.path.abspath(__file__))
    if snapshots["producer"].path != current_source:
        raise CandidateRawAxisFailure(HOLD_INPUT, "producer source pin path mismatch")
    if snapshots["verifier"].path == current_source:
        raise CandidateRawAxisFailure(HOLD_INPUT, "producer/verifier sources must differ")
    forbidden_input_paths = {snapshot.path for snapshot in snapshots.values()}
    forbidden_input_paths.add(request_snapshot.path)
    if output_path in forbidden_input_paths:
        raise CandidateRawAxisFailure(HOLD_REQUEST, "output aliases an input path")

    member = _parse_canonical(snapshots["member_spec"].raw, label="member")
    reference = _parse_canonical(snapshots["reference_density"].raw, label="reference")
    formula = _parse_canonical(snapshots["ideal_formula"].raw, label="formula")
    configuration = _parse_canonical(snapshots["configuration"].raw, label="configuration")
    factorization = _parse_canonical(snapshots["factorization"].raw, label="factorization")
    registry = _parse_canonical(snapshots["method_parameters"].raw, label="method parameters")
    _validate_source_semantics(
        reference,
        formula,
        configuration,
        factorization,
        member,
        snapshots,
    )
    methods = _validate_method_registry(registry, request["method_selection"])
    _require_exact_authority(
        snapshots["factorization"],
        relative_path=FACTORIZATION_RELATIVE_PATH,
        sha256=FACTORIZATION_SHA256,
        label="factorization",
        code=HOLD_INPUT,
    )
    _require_exact_authority(
        snapshots["method_parameters"],
        relative_path=PARAMETER_REGISTRY_RELATIVE_PATH,
        sha256=PARAMETER_REGISTRY_SHA256,
        label="parameter registry",
        code=HOLD_METHOD,
    )
    rows_and_partitions, partition_pins = _validate_member_and_partitions(
        request, member, reference, configuration
    )

    parameters = reference["physical_parameter_bundle"]
    diffusion = _binary64_fraction(
        parameters.get("particle_diffusion_binary64_hex"), label="particle diffusion"
    )
    stiffness = _binary64_fraction(
        parameters.get("ou_stiffness_binary64_hex"), label="OU stiffness"
    )
    mean = _binary64_fraction(parameters.get("ou_mean_binary64_hex"), label="OU mean")
    period = _fraction(parameters.get("transverse_period_exact"), label="period")
    if diffusion <= 0 or stiffness <= 0 or period <= 0:
        raise CandidateRawAxisFailure(HOLD_INPUT, "nonpositive physical parameter")
    axis_diffusions = {
        "midpoint": diffusion / 2,
        "relative_parallel": 2 * diffusion,
        "relative_perpendicular": 2 * diffusion,
    }

    output_rows: list[dict[str, Any]] = []
    cell_count = 0
    edge_count = 0
    boundary_zero_count = 0
    periodic_seam_count = 0
    nondegenerate_interval_count = 0
    maximum_mu_width = Fraction(0)
    maximum_q_width = Fraction(0)
    maximum_kappa_width = Fraction(0)
    configuration_rows = configuration["configurations"]
    for index, ((binding, partitions), config_row) in enumerate(
        zip(rows_and_partitions, configuration_rows, strict=True)
    ):
        axes_output: list[dict[str, Any]] = []
        for coordinate, partition in zip(COORDINATES, partitions, strict=True):
            size = partition["size"]
            periodic = partition["periodic"]
            positions = [
                _fraction(value, code=HOLD_MEMBER, label="partition position")
                for value in partition["positions_exact"]
            ]
            volumes = [
                _fraction(value, code=HOLD_MEMBER, label="partition volume")
                for value in partition["cell_volumes_exact"]
            ]
            if any(volume <= 0 for volume in volumes):
                raise CandidateRawAxisFailure(HOLD_MEMBER, "nonpositive partition volume")
            potentials = _potentials(
                coordinate,
                positions,
                stiffness=stiffness,
                diffusion=diffusion,
                mean=mean,
            )
            primary_mu: list[ExactInterval] = []
            sentinel_mu: list[ExactInterval] = []
            for potential, volume in zip(potentials, volumes, strict=True):
                if periodic:
                    primary = ExactInterval(volume, volume)
                    sentinel = primary
                else:
                    primary = _raw_mu(potential, volume, methods.primary_bits)
                    sentinel = _raw_mu(potential, volume, methods.sentinel_bits)
                if primary.lower <= 0 or not primary.contains(sentinel):
                    raise CandidateRawAxisFailure(
                        HOLD_NUMERICAL, "primary raw-mu interval misses positive sentinel"
                    )
                primary_mu.append(primary)
                sentinel_mu.append(sentinel)
                maximum_mu_width = max(maximum_mu_width, _relative_width(primary))
                if primary.lower < primary.upper:
                    nondegenerate_interval_count += 1
            cells = [
                {
                    "cell_index": cell_index,
                    "raw_mu_interval": _interval_json(value),
                }
                for cell_index, value in enumerate(primary_mu)
            ]

            axis_diffusion = axis_diffusions[coordinate]
            edge_records: list[dict[str, Any]] = []
            edge_indices = range(size) if periodic else range(size - 1)
            seam_count = 0
            for edge_index, left_index in enumerate(edge_indices):
                right_index = (left_index + 1) % size
                if periodic:
                    cell_width = _fraction(partition["domain_width_exact"], code=HOLD_MEMBER) / size
                    if any(volume != cell_width for volume in volumes):
                        raise CandidateRawAxisFailure(
                            HOLD_MEMBER, "periodic partition is not uniform"
                        )
                    oriented_distance = cell_width
                    crosses_cut = positions[right_index] <= positions[left_index]
                    seam_count += int(crosses_cut)
                    forward_primary = ExactInterval(
                        axis_diffusion / cell_width**2,
                        axis_diffusion / cell_width**2,
                    )
                    forward_sentinel = forward_primary
                    reverse_primary = forward_primary
                    reverse_sentinel = forward_primary
                    direct_left_primary = ExactInterval(
                        axis_diffusion / cell_width,
                        axis_diffusion / cell_width,
                    )
                    direct_left_sentinel = direct_left_primary
                    direct_right_primary = direct_left_primary
                    direct_right_sentinel = direct_left_primary
                else:
                    oriented_distance = positions[right_index] - positions[left_index]
                    if oriented_distance <= 0:
                        raise CandidateRawAxisFailure(
                            HOLD_MEMBER, "reflecting representatives are not increasing"
                        )
                    crosses_cut = False
                    delta = potentials[right_index] - potentials[left_index]
                    forward_primary = _directed_rate(
                        delta,
                        axis_diffusion,
                        volumes[left_index],
                        oriented_distance,
                        methods.primary_bits,
                    )
                    forward_sentinel = _directed_rate(
                        delta,
                        axis_diffusion,
                        volumes[left_index],
                        oriented_distance,
                        methods.sentinel_bits,
                    )
                    reverse_primary = _directed_rate(
                        -delta,
                        axis_diffusion,
                        volumes[right_index],
                        oriented_distance,
                        methods.primary_bits,
                    )
                    reverse_sentinel = _directed_rate(
                        -delta,
                        axis_diffusion,
                        volumes[right_index],
                        oriented_distance,
                        methods.sentinel_bits,
                    )
                    direct_left_primary = _direct_kappa(
                        potentials[left_index],
                        delta,
                        axis_diffusion,
                        oriented_distance,
                        methods.primary_bits,
                    )
                    direct_left_sentinel = _direct_kappa(
                        potentials[left_index],
                        delta,
                        axis_diffusion,
                        oriented_distance,
                        methods.sentinel_bits,
                    )
                    direct_right_primary = _direct_kappa(
                        potentials[right_index],
                        -delta,
                        axis_diffusion,
                        oriented_distance,
                        methods.primary_bits,
                    )
                    direct_right_sentinel = _direct_kappa(
                        potentials[right_index],
                        -delta,
                        axis_diffusion,
                        oriented_distance,
                        methods.sentinel_bits,
                    )
                primary_values = (
                    forward_primary,
                    reverse_primary,
                    direct_left_primary,
                    direct_right_primary,
                )
                sentinel_values = (
                    forward_sentinel,
                    reverse_sentinel,
                    direct_left_sentinel,
                    direct_right_sentinel,
                )
                if any(
                    primary.lower <= 0 or not primary.contains(sentinel)
                    for primary, sentinel in zip(primary_values, sentinel_values, strict=True)
                ):
                    raise CandidateRawAxisFailure(
                        HOLD_NUMERICAL, "primary edge interval misses positive sentinel"
                    )
                forward_product_primary = primary_mu[left_index].multiply_nonnegative(
                    forward_primary
                )
                reverse_product_primary = primary_mu[right_index].multiply_nonnegative(
                    reverse_primary
                )
                forward_product_sentinel = sentinel_mu[left_index].multiply_nonnegative(
                    forward_sentinel
                )
                reverse_product_sentinel = sentinel_mu[right_index].multiply_nonnegative(
                    reverse_sentinel
                )
                common_primary = _four_way_intersection(
                    (
                        direct_left_primary,
                        direct_right_primary,
                        forward_product_primary,
                        reverse_product_primary,
                    )
                )
                common_sentinel = _four_way_intersection(
                    (
                        direct_left_sentinel,
                        direct_right_sentinel,
                        forward_product_sentinel,
                        reverse_product_sentinel,
                    )
                )
                if common_primary.lower <= 0 or not common_primary.contains(common_sentinel):
                    raise CandidateRawAxisFailure(
                        HOLD_NUMERICAL, "primary common kappa misses positive sentinel"
                    )
                maximum_q_width = max(
                    maximum_q_width,
                    _relative_width(forward_primary),
                    _relative_width(reverse_primary),
                )
                maximum_kappa_width = max(maximum_kappa_width, _relative_width(common_primary))
                nondegenerate_interval_count += sum(
                    value.lower < value.upper
                    for value in (
                        forward_primary,
                        reverse_primary,
                        direct_left_primary,
                        direct_right_primary,
                        common_primary,
                    )
                )
                edge_records.append(
                    {
                        "common_kappa_interval": _interval_json(common_primary),
                        "direct_left_kappa_interval": _interval_json(direct_left_primary),
                        "direct_right_kappa_interval": _interval_json(direct_right_primary),
                        "edge_index": edge_index,
                        "forward_product_kappa_interval": _interval_json(forward_product_primary),
                        "forward_q_interval": _interval_json(forward_primary),
                        "left_cell_index": left_index,
                        "orientation": (
                            "left_to_right_increasing_partition_index_modulo"
                            if periodic
                            else "left_to_right_increasing_representative_coordinate"
                        ),
                        "oriented_distance_exact": _fraction_text(oriented_distance),
                        "periodic_domain_cut_crossing": crosses_cut,
                        "reverse_product_kappa_interval": _interval_json(reverse_product_primary),
                        "reverse_q_interval": _interval_json(reverse_primary),
                        "right_cell_index": right_index,
                    }
                )
                edge_count += 1
            if periodic and seam_count != 1:
                raise CandidateRawAxisFailure(
                    HOLD_MEMBER, "periodic representative ordering must cross one domain cut"
                )
            periodic_seam_count += seam_count
            boundary_records: list[dict[str, Any]] = []
            if not periodic:
                zero = _interval_json(ExactInterval(Fraction(0), Fraction(0)))
                boundary_records = [
                    {"cell_index": 0, "direction": "reverse", "q_interval": zero},
                    {
                        "cell_index": size - 1,
                        "direction": "forward",
                        "q_interval": zero,
                    },
                ]
                boundary_zero_count += 2
            axis_binding = binding["n0_axes"][COORDINATES.index(coordinate)]
            axes_output.append(
                {
                    "boundary_zero_q_records": boundary_records,
                    "cell_count": size,
                    "cells": cells,
                    "coordinate": coordinate,
                    "edge_count": len(edge_records),
                    "edges": edge_records,
                    "partition_path": axis_binding["partition_report_relative_path"],
                    "partition_sha256": axis_binding["partition_sha256"],
                    "periodic": periodic,
                    "periodic_domain_cut_crossing_edge_count": seam_count,
                }
            )
            cell_count += size
        output_rows.append(
            {
                "axes": axes_output,
                "configuration_index": index,
                "configuration_label": config_row["label"],
                "refinement_family_id": binding["refinement_family_id"],
                "refinement_member_id": binding["refinement_member_id"],
                "sequence_id": binding["sequence_id"],
                "tensor_state_count_not_materialized": config_row["expected_states"],
            }
        )

    output = {
        "claim_boundary": {
            "backend_independence_claimed": False,
            "complete_C1": False,
            "complete_C2": False,
            "externally_committed_request": False,
            "release_eligible": False,
            "stationary_or_killing_result_consumed": False,
        },
        "method": {
            "binary64_decode_parameter_id": methods.binary64_id,
            "dense_tensor_materialized": False,
            "exact_parameter_id": methods.exact_id,
            "parameter_sha256s": methods.parameter_digests,
            "primary_parameter_id": methods.primary_id,
            "primary_precision_bits": methods.primary_bits,
            "rounding": "directed_RoundDown_RoundUp",
            "sentinel_parameter_id": methods.sentinel_id,
            "sentinel_precision_bits": methods.sentinel_bits,
            "sentinel_semantics": "same_backend_higher_precision_containment_only",
        },
        "normalization_scope": {
            "axis_diffusion_units": "coordinate_squared_per_time",
            "common_kappa_units": "coordinate_volume_per_time",
            "downstream_physical_normalization_applied": False,
            "periodic_raw_mu_rule": "cell_volume_without_period_reciprocal_factor",
            "raw_mu_scope": "ungauged_axis_cell_volume_times_exp_minus_potential",
            "raw_mu_units": "coordinate_volume",
            "stationary_integral_scope": "distinct_downstream_role_not_computed",
        },
        "request": {
            "path": str(request_snapshot.path),
            "sha256": request_snapshot.sha256,
        },
        "rows": output_rows,
        "runtime": runtime,
        "schema": OUTPUT_SCHEMA,
        "source_pins": {
            "code_inputs": {
                role: {"path": str(snapshots[role].path), "sha256": snapshots[role].sha256}
                for role in sorted(code_inputs)
            },
            "input_authorities": {
                role: {"path": str(snapshots[role].path), "sha256": snapshots[role].sha256}
                for role in sorted(authorities)
            },
            "partitions": partition_pins,
        },
        "status": OUTPUT_STATUS,
        "summary": {
            "all_primary_intervals_contain_sentinels": True,
            "axis_cell_count": cell_count,
            "axis_edge_count": edge_count,
            "configuration_count": len(output_rows),
            "maximum_common_kappa_relative_width_exact": _fraction_text(maximum_kappa_width),
            "maximum_directed_q_relative_width_exact": _fraction_text(maximum_q_width),
            "maximum_raw_mu_relative_width_exact": _fraction_text(maximum_mu_width),
            "nondegenerate_primary_interval_count": nondegenerate_interval_count,
            "periodic_domain_cut_crossing_edge_count": periodic_seam_count,
            "reflecting_boundary_zero_q_count": boundary_zero_count,
            "total_virtual_tensor_state_count": sum(
                row["tensor_state_count_not_materialized"] for row in output_rows
            ),
        },
    }
    payload = canonical_bytes(output)
    if len(payload) > MAX_OUTPUT_BYTES:
        raise CandidateRawAxisFailure(HOLD_OUTPUT, "output exceeds deterministic size cap")
    return payload


def _publication_identity(metadata: os.stat_result) -> tuple[int, int]:
    return metadata.st_dev, metadata.st_ino


def _publication_entry_identity(parent_descriptor: int, name: str) -> tuple[int, int] | None:
    try:
        metadata = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return None
    return _publication_identity(metadata)


def _unlink_owned_publication_entry(
    parent_descriptor: int,
    name: str,
    expected_identity: tuple[int, int],
) -> bool:
    try:
        if _publication_entry_identity(parent_descriptor, name) != expected_identity:
            return False
        os.unlink(name, dir_fd=parent_descriptor)
        return True
    except FileNotFoundError:
        return False


def _close_publication_descriptor(
    descriptor: int | None,
    expected_identity: tuple[int, int] | None,
) -> BaseException | None:
    if descriptor is None:
        return None
    try:
        if expected_identity is not None:
            metadata = os.fstat(descriptor)
            if _publication_identity(metadata) != expected_identity:
                return None
        os.close(descriptor)
    except OSError:
        return None
    except BaseException as error:
        return error
    return None


def _close_publication_directories(
    descriptors: Sequence[int],
    identities: Sequence[tuple[int, int]],
) -> BaseException | None:
    first_error: BaseException | None = None
    for index in reversed(range(len(descriptors))):
        descriptor = descriptors[index]
        identity = identities[index] if index < len(identities) else None
        error = _close_publication_descriptor(descriptor, identity)
        if error is not None and first_error is None:
            first_error = error
    return first_error


class StageCreationTransaction:
    def __init__(self, parent_descriptor: int, leaf: str) -> None:
        self.parent_descriptor = parent_descriptor
        self.leaf = leaf
        self.descriptor: int | None = None
        self.identity: tuple[int, int] | None = None
        self.error: BaseException | None = None
        self._ready = threading.Event()
        self._thread = threading.Thread(
            target=self._create,
            name="raw-axis-stage-create",
        )

    def _create(self) -> None:
        try:
            descriptor = _STAGE_OPEN(
                self.leaf,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NONBLOCK | os.O_NOFOLLOW,
                0o400,
                dir_fd=self.parent_descriptor,
            )
            self.descriptor = descriptor
            observed = _STAGE_FSTAT(descriptor)
            if (
                not stat.S_ISREG(observed.st_mode)
                or observed.st_uid != os.getuid()
                or observed.st_nlink != 1
                or observed.st_size != 0
                or observed.st_mode & 0o222
            ):
                raise CandidateRawAxisFailure(HOLD_OUTPUT, "new staging inode invariant failure")
            self.identity = _publication_identity(observed)
        except BaseException as error:
            self.error = error
        finally:
            self._ready.set()

    def start(self) -> None:
        self._thread.start()

    def await_ready(self) -> None:
        self._ready.wait()
        if self.error is not None:
            raise self.error
        if self.descriptor is None or self.identity is None:
            raise CandidateRawAxisFailure(
                HOLD_OUTPUT, "stage creation transaction lost authoritative state"
            )

    def settle(self) -> None:
        while self._thread.is_alive():
            try:
                self._thread.join()
            except BaseException:
                continue

    def release_descriptor(self, descriptor: int) -> None:
        if self.descriptor != descriptor:
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "stage descriptor transfer mismatch")
        self.descriptor = None


def _rollback_publication(
    parent_descriptor: int,
    *,
    final_name: str,
    installation_attempted: bool,
    stage_identity: tuple[int, int] | None,
    stage_name: str | None,
) -> None:
    if stage_identity is None:
        return
    changed = False
    for name, eligible in (
        (final_name, installation_attempted),
        (stage_name, stage_name is not None),
    ):
        if not eligible or name is None:
            continue
        try:
            changed = (
                _unlink_owned_publication_entry(parent_descriptor, name, stage_identity) or changed
            )
        except BaseException:
            pass
    if changed:
        try:
            os.fsync(parent_descriptor)
        except BaseException:
            pass


def _rollback_via_live_parent(
    path: Path,
    expected_parent_identity: tuple[int, int],
    *,
    installation_attempted: bool,
    stage_identity: tuple[int, int] | None,
    stage_name: str | None,
) -> None:
    descriptors: list[int] = []
    identities: list[tuple[int, int]] = []
    try:
        descriptors, _ = _open_anchored_directory_chain(path.parent, code=HOLD_OUTPUT)
        identities = [_publication_identity(os.fstat(descriptor)) for descriptor in descriptors]
        if identities[-1] == expected_parent_identity:
            _rollback_publication(
                descriptors[-1],
                final_name=path.name,
                installation_attempted=installation_attempted,
                stage_identity=stage_identity,
                stage_name=stage_name,
            )
    except BaseException:
        pass
    finally:
        _close_publication_directories(descriptors, identities)


def _read_published_output(
    parent_descriptor: int,
    name: str,
    expected_identity: tuple[int, int],
    payload_size: int,
) -> bytes:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    close_error: BaseException | None = None
    try:
        descriptor = os.open(name, flags, dir_fd=parent_descriptor)
        before = os.fstat(descriptor)
        if (
            _publication_identity(before) != expected_identity
            or not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.getuid()
            or before.st_nlink != 1
            or before.st_mode & 0o222
            or before.st_size != payload_size
        ):
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "published output metadata mismatch")
        remaining = payload_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1 << 20))
            if not chunk:
                raise CandidateRawAxisFailure(HOLD_OUTPUT, "short published output read")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "published output grew")
        after = os.fstat(descriptor)
        if (
            _publication_identity(after) != expected_identity
            or (
                after.st_mode,
                after.st_nlink,
                after.st_uid,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
            )
            != (
                before.st_mode,
                before.st_nlink,
                before.st_uid,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
            )
            or _publication_entry_identity(parent_descriptor, name) != expected_identity
        ):
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "published output changed")
        return b"".join(chunks)
    finally:
        if descriptor is not None:
            close_error = _close_publication_descriptor(descriptor, expected_identity)
        if close_error is not None:
            raise close_error


def _publish(path: Path, payload: bytes) -> None:
    directories: list[int] = []
    directory_identities: list[tuple[int, int]] = []
    links: list[tuple[int, str, int, int, int]] = []
    parent_descriptor: int | None = None
    parent_identity: tuple[int, int] | None = None
    stage_transaction: StageCreationTransaction | None = None
    stage_descriptor: int | None = None
    stage_identity: tuple[int, int] | None = None
    installation_attempted = False
    acknowledged = False
    stage_name: str | None = None
    try:
        directories, links = _open_anchored_directory_chain(path.parent, code=HOLD_OUTPUT)
        directory_identities = [
            _publication_identity(os.fstat(descriptor)) for descriptor in directories
        ]
        parent_descriptor = directories[-1]
        parent_identity = directory_identities[-1]
        parent_metadata = os.fstat(parent_descriptor)
        if (
            not stat.S_ISDIR(parent_metadata.st_mode)
            or parent_metadata.st_uid != os.getuid()
            or stat.S_IMODE(parent_metadata.st_mode) != 0o700
        ):
            raise CandidateRawAxisFailure(
                HOLD_OUTPUT, "output parent must be current-UID-owned mode 0700"
            )
        try:
            target_identity = _publication_entry_identity(parent_descriptor, path.name)
        except OSError as error:
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "output target unavailable") from error
        if target_identity is not None:
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "output already exists")
        for _ in range(16):
            candidate = f".{path.name}.stage.{os.getpid()}.{secrets.token_hex(16)}"
            stage_name = candidate
            stage_transaction = StageCreationTransaction(parent_descriptor, candidate)
            try:
                stage_transaction.start()
                stage_transaction.await_ready()
                stage_descriptor = stage_transaction.descriptor
                stage_identity = stage_transaction.identity
                if stage_descriptor is None or stage_identity is None:
                    raise CandidateRawAxisFailure(HOLD_OUTPUT, "stage transaction result missing")
                stage_transaction.release_descriptor(stage_descriptor)
                break
            except FileExistsError:
                stage_transaction.settle()
                stage_transaction = None
                stage_name = None
                continue
        if stage_descriptor is None or stage_identity is None or stage_name is None:
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "unable to allocate output stage")
        view = memoryview(payload)
        while view:
            written = os.write(stage_descriptor, view)
            if written <= 0:
                raise CandidateRawAxisFailure(HOLD_OUTPUT, "short output write")
            view = view[written:]
        os.fchmod(stage_descriptor, 0o400)
        os.fsync(stage_descriptor)
        stage_metadata = os.fstat(stage_descriptor)
        if (
            _publication_identity(stage_metadata) != stage_identity
            or not stat.S_ISREG(stage_metadata.st_mode)
            or stage_metadata.st_nlink != 1
            or stage_metadata.st_uid != os.getuid()
            or stage_metadata.st_mode & 0o222
            or stage_metadata.st_size != len(payload)
        ):
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "published output metadata mismatch")
        os.close(stage_descriptor)
        stage_descriptor = None

        _revalidate_anchored_directory_chain(links, code=HOLD_OUTPUT)
        installation_attempted = True
        try:
            os.link(
                stage_name,
                path.name,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "output already exists") from error
        target_metadata = os.stat(
            path.name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        if (
            _publication_identity(target_metadata) != stage_identity
            or target_metadata.st_nlink != 2
        ):
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "published output link mismatch")
        os.fsync(parent_descriptor)
        if not _unlink_owned_publication_entry(
            parent_descriptor,
            stage_name,
            stage_identity,
        ):
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "owned output stage cleanup failed")
        os.fsync(parent_descriptor)
        target_metadata = os.stat(
            path.name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        if (
            _publication_identity(target_metadata) != stage_identity
            or target_metadata.st_nlink != 1
            or not stat.S_ISREG(target_metadata.st_mode)
            or target_metadata.st_uid != os.getuid()
            or target_metadata.st_mode & 0o222
            or target_metadata.st_size != len(payload)
        ):
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "published output metadata mismatch")
        observed = _read_published_output(
            parent_descriptor,
            path.name,
            stage_identity,
            len(payload),
        )
        if observed != payload:
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "published output stable reread mismatch")
        _revalidate_anchored_directory_chain(links, code=HOLD_OUTPUT)

        close_error = _close_publication_directories(directories, directory_identities)
        if close_error is not None:
            raise close_error
        directories = []
        directory_identities = []
        acknowledged = True
    except BaseException as error:
        if stage_transaction is not None:
            stage_transaction.settle()
            if stage_identity is None:
                stage_identity = stage_transaction.identity
            if stage_transaction.descriptor is not None:
                if stage_descriptor is None:
                    stage_descriptor = stage_transaction.descriptor
                elif stage_descriptor != stage_transaction.descriptor:
                    _close_publication_descriptor(
                        stage_transaction.descriptor,
                        stage_transaction.identity,
                    )
                stage_transaction.descriptor = None
        if stage_identity is None and stage_descriptor is not None:
            try:
                stage_identity = _publication_identity(_STAGE_FSTAT(stage_descriptor))
            except BaseException:
                pass
        _close_publication_descriptor(stage_descriptor, stage_identity)
        stage_descriptor = None
        parent_is_live = False
        if parent_descriptor is not None and parent_identity is not None:
            try:
                parent_is_live = (
                    _publication_entry_identity(parent_descriptor, ".") == parent_identity
                )
            except BaseException:
                pass
        if parent_is_live and parent_descriptor is not None:
            _rollback_publication(
                parent_descriptor,
                final_name=path.name,
                installation_attempted=installation_attempted,
                stage_identity=stage_identity,
                stage_name=stage_name,
            )
        if parent_identity is not None:
            _rollback_via_live_parent(
                path,
                parent_identity,
                installation_attempted=installation_attempted,
                stage_identity=stage_identity,
                stage_name=stage_name,
            )
        _close_publication_directories(directories, directory_identities)
        if isinstance(error, CandidateRawAxisFailure):
            raise
        if isinstance(error, OSError):
            raise CandidateRawAxisFailure(HOLD_OUTPUT, "publication failed") from error
        raise
    finally:
        if stage_transaction is not None:
            stage_transaction.settle()
            if stage_transaction.descriptor is not None:
                _close_publication_descriptor(
                    stage_transaction.descriptor,
                    stage_transaction.identity,
                )
                stage_transaction.descriptor = None
        if not acknowledged and parent_identity is not None:
            _rollback_via_live_parent(
                path,
                parent_identity,
                installation_attempted=installation_attempted,
                stage_identity=stage_identity,
                stage_name=stage_name,
            )
        _close_publication_descriptor(stage_descriptor, stage_identity)
        _close_publication_directories(directories, directory_identities)
    if not acknowledged:
        raise CandidateRawAxisFailure(HOLD_OUTPUT, "publication was not acknowledged")


def _parse_cli(argv: Sequence[str] | None) -> tuple[Path, Path, bool]:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    request = _absolute_lexical(arguments.request, code=HOLD_REQUEST, label="request CLI")
    output = _absolute_lexical(arguments.output, code=HOLD_REQUEST, label="output CLI")
    if request == output:
        raise CandidateRawAxisFailure(HOLD_REQUEST, "request and output must differ")
    return request, output, arguments.check


def main(argv: Sequence[str] | None = None) -> int:
    try:
        request_path, output_path, check = _parse_cli(argv)
        payload = build_from_request(request_path, output_path)
        if check:
            observed = immutable_snapshot(output_path, cap=max(MAX_OUTPUT_BYTES, len(payload)))
            if observed.raw != payload:
                raise CandidateRawAxisFailure(HOLD_OUTPUT, "read-only check mismatch")
        else:
            _publish(output_path, payload)
    except CandidateRawAxisFailure as error:
        print(error, file=sys.stderr)
        return 2
    print(
        canonical_bytes(
            {
                "output_path": str(output_path),
                "schema": "encounter_continuum_c1_n0_raw_axis_formula_ack_v1",
                "status": "PASS_READ_ONLY_CHECK" if check else "PASS_EXCLUSIVE_PUBLICATION",
            }
        ).decode("ascii"),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
