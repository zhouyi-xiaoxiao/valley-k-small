#!/usr/bin/env python3
"""Build the result-blind C1/C2 n0 structural-member v4 candidate.

The candidate independently replays all twelve configuration rows and all
thirty-six exact n0 axis partitions.  It replaces only the historical role-3
factorization binding with the outcome-free v2 candidate.  It deliberately
contains no method registry, role-8--10 result, external commitment, or
production-member claim.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import secrets
import stat
import sys
import threading
import unicodedata
from collections import Counter
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Final

_STAGE_OPEN: Final = os.open
_STAGE_FSTAT: Final = os.fstat

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
OUTPUT_RELATIVE: Final = "artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json"
DEFAULT_OUTPUT: Final = REPORT / OUTPUT_RELATIVE

MEMBER_V3_RELATIVE: Final = (
    "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/"
    "continuum_c1_c2_n0_member_spec_v3_candidate.json"
)
REFERENCE_RELATIVE: Final = "artifacts/data/continuum_c1_reference_density_source_v1.json"
IDEAL_RELATIVE: Final = "artifacts/data/continuum_c1_ideal_formula_source_v1.json"
FACTORIZATION_RELATIVE: Final = "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"
CONFIGURATION_RELATIVE: Final = "artifacts/data/physical_configuration_family_control_free_v1.json"
REFINEMENT_RELATIVE: Final = "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json"
PARTITION_BUNDLE_RELATIVE: Final = (
    "artifacts/data/physical_production_initial_stream_v1/bundle.json"
)

MEMBER_V3_SHA256: Final = "b5eea6553d329bcbc4a1eb301dd3d5fb5b5acd387b80bfee5094286d3ca8ab71"
MEMBER_V3_IDENTITY_SHA256: Final = (
    "90f4be333a70797792d7b7ba74b7bec213db304360569b349edf92ae7aaee229"
)
REFERENCE_SHA256: Final = "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575"
IDEAL_SHA256: Final = "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be"
FACTORIZATION_SHA256: Final = "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26"
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
REFINEMENT_SHA256: Final = "1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9"
PARTITION_BUNDLE_SHA256: Final = "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
HISTORICAL_FACTORIZATION_V1_RELATIVE: Final = (
    "artifacts/data/continuum_c1_factorization_source_v1.json"
)
HISTORICAL_FACTORIZATION_V1_SHA256: Final = (
    "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca"
)

SCHEMA: Final = "encounter_continuum_c1_c2_n0_member_spec_v4_candidate"
STATUS: Final = (
    "STRUCTURAL_PARTITION_IDENTITY_V4_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
)
IDENTITY_DOMAIN: Final = "encounter-continuum-c1-c2-n0-member-identity-v4"
KNOWN_IDENTITY_SHA256: Final = "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
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
EXPECTED_COUNTS: Final = {
    "axis_cell_count": 5_037,
    "axis_count": 36,
    "axis_edge_count": 5_013,
    "configuration_count": 12,
    "periodic_seam_count": 12,
    "profile_index_count": 48,
    "total_virtual_tensor_state_count": 34_787_462,
}
EXPECTED_CONFIGURATION_ORDER: Final = (
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
EXPECTED_SEMANTIC_IDS: Final = (
    ("O113/Base", "finite_mesh_anchor_family", "o113_base"),
    ("E128/Base", "finite_mesh_anchor_family", "e128_base"),
    ("O129/Base", "finite_mesh_anchor_family", "o129_base"),
    ("O161/Base", "finite_mesh_anchor_family", "o161_base"),
    ("M+", "finite_box_challenge_family", "m_plus"),
    ("R+", "finite_box_challenge_family", "r_plus"),
    ("MR+", "finite_box_challenge_family", "mr_plus"),
    ("MR+F", "finite_box_challenge_family", "mr_plus_fine"),
    ("A_M", "finite_alignment_challenge_family", "a_midpoint"),
    ("A_R", "finite_alignment_challenge_family", "a_relative_parallel"),
    ("A_Y", "finite_alignment_challenge_family", "a_relative_perpendicular"),
    ("A_MRY", "finite_alignment_challenge_family", "a_all_axes"),
)
MEMBER_SEMANTICS: Final = {
    "configuration_count": 12,
    "configuration_rows_are_finite_anchors": True,
    "coordinate_order": list(AXIS_ORDER),
    "every_cartesian_interval_endpoint_combination_is_a_model": False,
    "one_formula_defined_correlated_member_per_configuration": True,
    "physical_dimension": 2,
    "quotient_dimension": 3,
    "scalar_convention": "complex_inner_product_conjugate_first_factor",
}
IDENTITY_PROPERTIES: Final = {
    "alignment_counts": EXPECTED_ALIGNMENT_COUNTS,
    "candidate_authoritative": False,
    "current_enclosures_bind_this_candidate": False,
    "n0_partition_sha256s_structurally_bound": True,
    "partition_file_count": 36,
    "round172_source_itself_contains_partition_sha256": False,
    "source_roles_1_through_4_only_in_production_role_bindings": True,
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
V3_TOP_LEVEL_KEYS: Final = {
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
MAX_JSON_BYTES: Final = 64 * 1024 * 1024
MAX_JSON_DEPTH: Final = 64
MAX_JSON_NODES: Final = 500_000
MAX_TOTAL_STRING_CHARACTERS: Final = 16 * 1024 * 1024
MAX_STRING_CHARACTERS: Final = 2 * 1024 * 1024


class MemberBuildError(RuntimeError):
    """A source, reconstruction, identity, or publication invariant failed."""


class StageCreationTransaction:
    """Create a staging inode while preserving ownership across BaseException."""

    def __init__(self, parent_descriptor: int, leaf: str) -> None:
        self.parent_descriptor = parent_descriptor
        self.leaf = leaf
        self.descriptor: int | None = None
        self.identity: tuple[int, int] | None = None
        self.error: BaseException | None = None
        self._ready = threading.Event()
        self._thread = threading.Thread(
            target=self._create,
            name="member-v4-stage-create",
        )

    def _create(self) -> None:
        try:
            descriptor = _STAGE_OPEN(
                self.leaf,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o400,
                dir_fd=self.parent_descriptor,
            )
            self.descriptor = descriptor
            opened = _STAGE_FSTAT(descriptor)
            if (
                not stat.S_ISREG(opened.st_mode)
                or stat.S_IMODE(opened.st_mode) != 0o400
                or opened.st_nlink != 1
                or opened.st_size != 0
            ):
                raise MemberBuildError("new 0400 staging inode invariant failure")
            self.identity = opened.st_dev, opened.st_ino
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
            raise MemberBuildError("stage transaction lost authoritative state")

    def settle(self) -> None:
        while self._thread.is_alive():
            try:
                self._thread.join()
            except BaseException:
                continue

    def release_descriptor(self, descriptor: int) -> None:
        if self.descriptor != descriptor:
            raise MemberBuildError("stage descriptor transfer mismatch")
        self.descriptor = None


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    nodes = 0
    characters = 0

    def check(node: Any, depth: int = 0) -> None:
        nonlocal nodes, characters
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise MemberBuildError("JSON node cap exceeded")
        if depth > MAX_JSON_DEPTH:
            raise MemberBuildError("JSON depth cap exceeded")
        if isinstance(node, float):
            raise MemberBuildError("floating JSON literals are forbidden")
        if type(node) is int:
            if node.bit_length() > 256:
                raise MemberBuildError("JSON integer bit-length cap exceeded")
            return
        if type(node) is bool or node is None:
            return
        if type(node) is str:
            characters += len(node)
            if (
                len(node) > MAX_STRING_CHARACTERS
                or characters > MAX_TOTAL_STRING_CHARACTERS
                or unicodedata.normalize("NFC", node) != node
            ):
                raise MemberBuildError("JSON string resource or NFC invariant failed")
            return
        if type(node) is list:
            for item in node:
                check(item, depth + 1)
            return
        if type(node) is dict:
            for key, item in node.items():
                if type(key) is not str:
                    raise MemberBuildError("non-string JSON key")
                check(key, depth + 1)
                check(item, depth + 1)
            return
        raise MemberBuildError(f"forbidden JSON type: {type(node).__name__}")

    check(value)
    payload = (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode(
        "ascii"
    )
    if len(payload) > MAX_JSON_BYTES:
        raise MemberBuildError("canonical JSON byte cap exceeded")
    return payload


def parse_canonical(payload: bytes, role: str) -> dict[str, Any]:
    if not payload or len(payload) > MAX_JSON_BYTES:
        raise MemberBuildError(f"JSON byte cap failed for {role}")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if type(key) is not str or key in result:
                raise MemberBuildError(f"duplicate or invalid key in {role}")
            result[key] = item
        return result

    def reject_number(token: str) -> Any:
        raise MemberBuildError(f"non-integer JSON number in {role}: {token}")

    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=unique_object,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ) as error:
        raise MemberBuildError(f"strict canonical JSON failure for {role}") from error
    if type(value) is not dict or canonical_bytes(value) != payload:
        raise MemberBuildError(f"canonical JSON byte drift for {role}")
    return value


def exact_equal(actual: Any, expected: Any, message: str) -> None:
    if canonical_bytes(actual) != canonical_bytes(expected):
        raise MemberBuildError(message)


def require_false_claims(value: Any, context: str) -> None:
    if (
        type(value) is not dict
        or set(value) != set(CLAIM_KEYS)
        or any(item is not False for item in value.values())
    ):
        raise MemberBuildError(f"exact all-false claim map required: {context}")


def require_exact_int(value: Any, expected: int, context: str) -> None:
    if type(value) is not int or value != expected:
        raise MemberBuildError(f"exact integer drift: {context}")


def require_nonempty_string(value: Any, context: str) -> str:
    if (
        type(value) is not str
        or not value
        or len(value) > 256
        or unicodedata.normalize("NFC", value) != value
    ):
        raise MemberBuildError(f"nonempty NFC string required: {context}")
    return value


def safe_relative(value: Any) -> Path:
    if type(value) is not str or not value or len(value) > 1024 or "\\" in value:
        raise MemberBuildError(f"unsafe report-relative path: {value!r}")
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or len(pure.parts) > 24
        or any(part in {"", ".", ".."} for part in pure.parts)
        or pure.as_posix() != value
    ):
        raise MemberBuildError(f"unsafe report-relative path: {value!r}")
    return Path(*pure.parts)


def close_safely(descriptor: int) -> None:
    if descriptor < 0:
        return
    try:
        os.close(descriptor)
    except BaseException:
        pass


def open_anchored_parent(path: Path) -> tuple[tuple[int, ...], str, tuple[tuple[int, int], ...]]:
    absolute = Path(os.path.abspath(path))
    if (
        not path.is_absolute()
        or path != absolute
        or len(path.parts) < 2
        or any(part in {"", ".", ".."} for part in path.parts[1:])
    ):
        raise MemberBuildError(f"canonical absolute leaf path required: {path}")
    for flag in ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK", "O_CLOEXEC"):
        if not hasattr(os, flag):
            raise MemberBuildError(f"{flag} is required")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptors: list[int] = []
    identities: list[tuple[int, int]] = []
    try:
        root = os.open(path.anchor, flags)
        descriptors.append(root)
        opened = os.fstat(root)
        if not stat.S_ISDIR(opened.st_mode):
            raise MemberBuildError("filesystem anchor is not a directory")
        identities.append((opened.st_dev, opened.st_ino))
        for component in path.parts[1:-1]:
            descriptor = os.open(component, flags, dir_fd=descriptors[-1])
            descriptors.append(descriptor)
            opened = os.fstat(descriptor)
            if not stat.S_ISDIR(opened.st_mode):
                raise MemberBuildError(f"non-directory path component: {component}")
            identities.append((opened.st_dev, opened.st_ino))
        return tuple(descriptors), path.parts[-1], tuple(identities)
    except OSError as error:
        for descriptor in reversed(descriptors):
            close_safely(descriptor)
        if error.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise MemberBuildError("symlink or non-directory path component rejected") from error
        raise
    except BaseException:
        for descriptor in reversed(descriptors):
            close_safely(descriptor)
        raise


def verify_anchored_parent(path: Path, expected: tuple[tuple[int, int], ...]) -> None:
    descriptors, _, observed = open_anchored_parent(path)
    try:
        if observed != expected:
            raise MemberBuildError(f"directory chain changed during operation: {path}")
    finally:
        for descriptor in reversed(descriptors):
            close_safely(descriptor)


def stat_signature(value: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_nlink,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def read_regular(
    path: Path,
    role: str,
    *,
    normative: bool,
    cap: int = MAX_JSON_BYTES,
) -> bytes:
    """Read through anchored descriptors and verify a live second open.

    Normative identity inputs are exactly 0444 and single-linked.  Historical
    row/refinement files are reconstruction evidence: their exact hashes are
    already frozen inside normative v3/bundle bytes, so their legacy 0644 mode
    is accepted while their regular-file, single-link, byte, and live-identity
    invariants are still enforced.
    """

    descriptors, leaf, identities = open_anchored_parent(path)
    parent = descriptors[-1]
    descriptor = -1
    reopened = -1
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        try:
            descriptor = os.open(leaf, flags, dir_fd=parent)
        except OSError as error:
            if error.errno == errno.ELOOP:
                raise MemberBuildError(f"symlink leaf rejected: {path}") from error
            raise
        before = os.fstat(descriptor)
        mode = stat.S_IMODE(before.st_mode)
        allowed_modes = {0o444} if normative else {0o444, 0o644}
        if (
            not stat.S_ISREG(before.st_mode)
            or mode not in allowed_modes
            or before.st_nlink != 1
            or before.st_size <= 0
            or before.st_size > cap
        ):
            raise MemberBuildError(f"bounded single-link source invariant failed for {role}")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 65_536))
            if not chunk:
                raise MemberBuildError(f"short source read for {role}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise MemberBuildError(f"source grew while reading {role}")
        after = os.fstat(descriptor)
        named = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if stat_signature(before) != stat_signature(after) or stat_signature(
            after
        ) != stat_signature(named):
            raise MemberBuildError(f"source changed during read for {role}")
        verify_anchored_parent(path, identities)
        reopened = os.open(leaf, flags, dir_fd=parent)
        live = os.fstat(reopened)
        if stat_signature(live) != stat_signature(after):
            raise MemberBuildError(f"live reopen identity drift for {role}")
        return b"".join(chunks)
    finally:
        close_safely(reopened)
        close_safely(descriptor)
        for item in reversed(descriptors):
            close_safely(item)


def load_json(
    relative: str,
    expected_sha256: str,
    role: str,
    *,
    normative: bool,
) -> dict[str, Any]:
    payload = read_regular(REPORT / safe_relative(relative), role, normative=normative)
    if sha256(payload) != expected_sha256:
        raise MemberBuildError(f"SHA-256 mismatch for {role}")
    return parse_canonical(payload, role)


def rational(value: Any) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise MemberBuildError(f"canonical p/q rational required: {value!r}")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise MemberBuildError(f"invalid rational: {value!r}") from error
    if f"{result.numerator}/{result.denominator}" != value:
        raise MemberBuildError(f"noncanonical rational: {value!r}")
    return result


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def domain_digest(domain: str, value: Any) -> str:
    require_nonempty_string(domain, "digest domain")
    return sha256(domain.encode("ascii") + b"\0" + canonical_bytes(value))


def expected_partition_geometry(axis: dict[str, Any]) -> dict[str, Any]:
    if type(axis) is not dict:
        raise MemberBuildError("axis record must be an object")
    coordinate = require_nonempty_string(axis.get("coordinate"), "axis coordinate")
    alignment = require_nonempty_string(axis.get("alignment"), "axis alignment")
    domain = axis.get("domain")
    if type(domain) is not dict:
        raise MemberBuildError("axis domain must be an object")
    start_text = domain.get("start_exact", domain.get("lower_exact"))
    width_text = domain.get("period_exact", domain.get("width_exact"))
    start = rational(start_text)
    width = rational(width_text)
    if width <= 0:
        raise MemberBuildError("axis width must be positive")
    end = start + width
    size = axis.get("anchor_size")
    if type(size) is not int or size < 2:
        raise MemberBuildError("exact positive axis size required")
    shift_text = axis.get("periodic_shift_n0_exact", "0/1")
    shift = rational(shift_text)

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
        segments: list[list[list[Fraction]]] = []
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
        raise MemberBuildError(f"unknown axis alignment: {alignment}")

    require_exact_int(axis.get("anchor_interval_count"), interval_count, "axis intervals")
    if rational(axis.get("spacing_h0_exact")) != spacing:
        raise MemberBuildError("axis spacing reconstruction drift")
    return {
        "cell_segments_exact": [
            [[rational_text(left), rational_text(right)] for left, right in cell]
            for cell in segments
        ],
        "cell_volumes_exact": [rational_text(value) for value in volumes],
        "construction": construction,
        "coordinate": coordinate,
        "domain_start_exact": start_text,
        "domain_width_exact": width_text,
        "periodic": periodic,
        "periodic_shift_exact": shift_text,
        "positions_exact": [rational_text(value) for value in positions],
        "schema": "encounter_exact_axis_partition_v1",
        "size": size,
    }


def validate_primary_sources() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    if FACTORIZATION_RELATIVE == HISTORICAL_FACTORIZATION_V1_RELATIVE:
        raise MemberBuildError("factorization v1 fallback is forbidden")
    member_v3 = load_json(
        MEMBER_V3_RELATIVE,
        MEMBER_V3_SHA256,
        "immutable member v3",
        normative=True,
    )
    reference = load_json(
        REFERENCE_RELATIVE,
        REFERENCE_SHA256,
        "role-1 reference authority",
        normative=True,
    )
    ideal = load_json(
        IDEAL_RELATIVE,
        IDEAL_SHA256,
        "role-2 ideal authority",
        normative=True,
    )
    factorization = load_json(
        FACTORIZATION_RELATIVE,
        FACTORIZATION_SHA256,
        "role-3 factorization v2 authority",
        normative=True,
    )
    configuration = load_json(
        CONFIGURATION_RELATIVE,
        CONFIGURATION_SHA256,
        "role-4 configuration authority",
        normative=True,
    )
    partition_bundle = load_json(
        PARTITION_BUNDLE_RELATIVE,
        PARTITION_BUNDLE_SHA256,
        "n0 partition bundle",
        normative=True,
    )
    refinement = load_json(
        REFINEMENT_RELATIVE,
        REFINEMENT_SHA256,
        "historical joint-refinement reconstruction evidence",
        normative=False,
    )

    if set(member_v3) != V3_TOP_LEVEL_KEYS:
        raise MemberBuildError("member v3 top-level contract drift or registry injection")
    if member_v3.get(
        "schema"
    ) != "encounter_continuum_c1_c2_n0_member_spec_v3_candidate" or member_v3.get("status") != (
        "STRUCTURAL_PARTITION_IDENTITY_CANDIDATE_ONLY_"
        "NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
    ):
        raise MemberBuildError("member v3 schema/status drift")
    require_false_claims(member_v3.get("claim_boundary"), "member v3")
    exact_equal(
        member_v3.get("identity_properties"),
        IDENTITY_PROPERTIES,
        "member v3 identity-property drift",
    )
    exact_equal(
        member_v3.get("member_semantics"),
        MEMBER_SEMANTICS,
        "member v3 complete semantic drift",
    )
    exact_equal(
        member_v3.get("reconstruction_counts"),
        EXPECTED_COUNTS,
        "member v3 reconstruction-count drift",
    )
    v3_identity = {
        "configuration_order": member_v3.get("configuration_order"),
        "configuration_semantic_ids": member_v3.get("configuration_semantic_ids"),
        "coordinate_order": member_v3.get("member_semantics", {}).get("coordinate_order"),
        "n0_sequence_bindings": member_v3.get("n0_sequence_bindings"),
        "role_bindings_1_through_4": member_v3.get("role_bindings"),
        "scalar_convention": member_v3.get("member_semantics", {}).get("scalar_convention"),
    }
    if (
        member_v3.get("member_identity_sha256") != MEMBER_V3_IDENTITY_SHA256
        or domain_digest("encounter-continuum-c1-c2-n0-member-identity-v3", v3_identity)
        != MEMBER_V3_IDENTITY_SHA256
    ):
        raise MemberBuildError("member v3 identity-domain replay drift")

    if (
        reference.get("schema") != "encounter_continuum_c1_reference_density_source_v1"
        or reference.get("status")
        != "FROZEN_CONTROL_FREE_REFERENCE_DENSITY_AUTHORITY_ONLY_NO_COMPLETE_C0_C1_C2"
    ):
        raise MemberBuildError("reference schema/status drift")
    reference_claims = reference.get("claim_boundary")
    if type(reference_claims) is not dict or any(
        value is not False for value in reference_claims.values()
    ):
        raise MemberBuildError("reference claim promotion")
    exact_equal(
        reference.get("coordinate_order"),
        list(AXIS_ORDER),
        "reference coordinate-order drift",
    )
    exact_equal(
        reference.get("source_pins", {}).get("configuration_source"),
        {"path": CONFIGURATION_RELATIVE, "sha256": CONFIGURATION_SHA256},
        "reference nested configuration pin drift",
    )

    if (
        ideal.get("schema") != "encounter_continuum_c1_ideal_formula_source_v1"
        or ideal.get("status")
        != "FROZEN_CONTROL_FREE_IDEAL_FORMULA_AUTHORITY_ONLY_NO_PRODUCTION_ACCEPTANCE"
    ):
        raise MemberBuildError("ideal schema/status drift")
    ideal_claims = ideal.get("claim_boundary")
    if type(ideal_claims) is not dict or any(value is not False for value in ideal_claims.values()):
        raise MemberBuildError("ideal claim promotion")
    exact_equal(
        ideal.get("member_semantics"),
        {
            "common_flux_uses_one_formula_defined_exact_value": True,
            "formula_defined_member_is_independent_of_production_centres": True,
            "global_gauge_is_single_scalar_per_configuration": True,
            "one_correlated_distinguished_member_required": True,
        },
        "ideal nested member-semantics drift",
    )

    if factorization.get(
        "schema"
    ) != "encounter_continuum_c1_factorization_source_v2_candidate" or factorization.get(
        "status"
    ) != (
        "OUTCOME_FREE_CONTROL_FREE_FACTORIZATION_CANDIDATE_ONLY_"
        "NOT_EXTERNALLY_COMMITTED_NO_NUMERIC_ENCLOSURES_NO_CONCRETE_KILLING"
    ):
        raise MemberBuildError("factorization v2 schema/status drift")
    require_false_claims(factorization.get("claim_boundary"), "factorization v2")
    exact_equal(
        factorization.get("source_pins", {}).get("configuration_source"),
        {
            "path": CONFIGURATION_RELATIVE,
            "schema": "encounter_physical_configuration_family_control_free_v1",
            "sha256": CONFIGURATION_SHA256,
        },
        "factorization nested configuration pin drift",
    )
    exact_equal(
        factorization.get("source_pins", {}).get("initial_partition_bundle"),
        {
            "path": PARTITION_BUNDLE_RELATIVE,
            "schema": "encounter_control_free_production_initial_stream_v1",
            "sha256": PARTITION_BUNDLE_SHA256,
        },
        "factorization nested partition pin drift",
    )
    exact_equal(
        factorization.get("outcome_free_contract"),
        {
            "budget_present": False,
            "concrete_killing_tensor_present": False,
            "control_weights_present": False,
            "external_commitment_present": False,
            "numeric_enclosure_payload_present": False,
            "primitive_source_only": True,
            "production_bridge_present": False,
        },
        "factorization outcome-free contract drift",
    )

    if (
        configuration.get("schema") != "encounter_physical_configuration_family_control_free_v1"
        or configuration.get("configuration_count") != 12
        or type(configuration.get("configuration_count")) is not int
    ):
        raise MemberBuildError("configuration source schema/count drift")
    exact_equal(
        configuration.get("configuration_order"),
        list(EXPECTED_CONFIGURATION_ORDER),
        "configuration source order drift",
    )
    exact_equal(
        configuration.get("coordinate_order"),
        list(AXIS_ORDER),
        "configuration source coordinate order drift",
    )
    if (
        configuration.get("authorizes_scientific_execution") is not False
        or configuration.get("contains_budget_value") is not False
        or configuration.get("contains_control_values") is not False
    ):
        raise MemberBuildError("configuration source claim promotion")

    if (
        partition_bundle.get("schema") != "encounter_control_free_production_initial_stream_v1"
        or partition_bundle.get("configuration_sha256") != CONFIGURATION_SHA256
    ):
        raise MemberBuildError("partition bundle schema/configuration drift")
    require_exact_int(partition_bundle.get("configuration_count"), 12, "partition bundle count")
    flags = partition_bundle.get("flags")
    if type(flags) is not dict:
        raise MemberBuildError("partition bundle flags missing")
    for key in (
        "authorizes_scientific_execution",
        "contains_budget_value",
        "contains_control_values",
        "full_operator_bound",
        "positive_budget_executed",
        "science_executed",
        "topology_complete",
    ):
        if flags.get(key) is not False:
            raise MemberBuildError(f"partition bundle claim promotion: {key}")

    if refinement.get("schema") != "encounter_continuum_c1_genuine_joint_refinement_family_v2":
        raise MemberBuildError("joint-refinement schema drift")
    require_exact_int(refinement.get("sequence_count"), 12, "refinement count")
    exact_equal(
        refinement.get("sequence_order"),
        list(EXPECTED_CONFIGURATION_ORDER),
        "joint-refinement order drift",
    )
    scope = refinement.get("established_scope")
    if type(scope) is not dict:
        raise MemberBuildError("joint-refinement scope missing")
    for key in (
        "finite_twelve_family_geometric_uniformity_proved",
        "genuine_refinement_sequences_defined",
        "maximum_axis_spacing_limit_proved",
        "n0_configuration_geometry_anchor_exact",
        "shape_regularity_proved",
    ):
        if scope.get(key) is not True:
            raise MemberBuildError(f"joint-refinement established-scope drift: {key}")
    refinement_claims = refinement.get("claim_boundary")
    if type(refinement_claims) is not dict or any(
        value is not False for value in refinement_claims.values()
    ):
        raise MemberBuildError("joint-refinement claim promotion")

    return (
        member_v3,
        reference,
        ideal,
        factorization,
        configuration,
        refinement,
        partition_bundle,
    )


def semantic_id_records() -> list[dict[str, str]]:
    return [
        {
            "authority_label": label,
            "refinement_family_id": family,
            "refinement_member_id": member,
        }
        for label, family, member in EXPECTED_SEMANTIC_IDS
    ]


def reconstruct_bindings(
    member_v3: dict[str, Any],
    reference: dict[str, Any],
    configuration: dict[str, Any],
    refinement: dict[str, Any],
    partition_bundle: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    configurations = configuration.get("configurations")
    sequences = refinement.get("sequences")
    bundle_rows = partition_bundle.get("rows")
    if not all(type(value) is list for value in (configurations, sequences, bundle_rows)):
        raise MemberBuildError("configuration/refinement/bundle row lists required")
    if not (len(configurations) == len(sequences) == len(bundle_rows) == 12):
        raise MemberBuildError("twelve-row reconstruction cardinality drift")
    expected_semantics = semantic_id_records()
    exact_equal(
        member_v3.get("configuration_semantic_ids"),
        expected_semantics,
        "member v3 semantic-id drift",
    )
    exact_equal(
        member_v3.get("configuration_order"),
        list(EXPECTED_CONFIGURATION_ORDER),
        "member v3 configuration-order drift",
    )

    physical_parameters = reference.get("physical_parameter_bundle")
    if type(physical_parameters) is not dict:
        raise MemberBuildError("reference physical-parameter bundle missing")
    physical_digest = domain_digest("encounter-physical-parameter-bundle-v1", physical_parameters)
    alignment_counts: Counter[str] = Counter()
    bindings: list[dict[str, Any]] = []
    total_states = 0
    total_cells = 0
    total_edges = 0
    periodic_seams = 0
    partition_root = Path(PARTITION_BUNDLE_RELATIVE).parent

    for index in range(12):
        config = configurations[index]
        sequence = sequences[index]
        bundle_index = bundle_rows[index]
        semantic = expected_semantics[index]
        if not all(type(value) is dict for value in (config, sequence, bundle_index)):
            raise MemberBuildError(f"row objects required at index {index}")
        label = EXPECTED_CONFIGURATION_ORDER[index]
        require_exact_int(sequence.get("source_row_index"), index, "sequence row index")
        require_exact_int(
            bundle_index.get("configuration_index"), index, "bundle configuration index"
        )
        for actual, context in (
            (config.get("label"), "configuration label"),
            (sequence.get("label"), "sequence label"),
            (bundle_index.get("configuration_label"), "bundle label"),
        ):
            if actual != label or type(actual) is not str:
                raise MemberBuildError(f"{context} drift at row {index}")
        shape = config.get("shape")
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(item) is not int or item < 2 for item in shape)
        ):
            raise MemberBuildError(f"exact three-axis shape required at row {index}")
        state_count = config.get("expected_states")
        if (
            type(state_count) is not int
            or state_count <= 0
            or state_count != shape[0] * shape[1] * shape[2]
        ):
            raise MemberBuildError(f"configuration state-count drift at row {index}")
        exact_equal(sequence.get("anchor_shape"), shape, f"sequence shape drift at {index}")
        require_exact_int(
            sequence.get("anchor_expected_states"),
            state_count,
            f"sequence state count {index}",
        )
        require_exact_int(
            bundle_index.get("expected_states"),
            state_count,
            f"bundle state count {index}",
        )
        config_digest = sha256(canonical_bytes(config))
        if sequence.get("source_row_canonical_sha256") != config_digest:
            raise MemberBuildError(f"sequence source-row digest drift at row {index}")
        expected_sequence_id = f"encounter_c1_joint_refinement_v2:{index}:{label}"
        if sequence.get("sequence_id") != expected_sequence_id:
            raise MemberBuildError(f"sequence identifier drift at row {index}")
        if sequence.get("anchor_geometry_exactly_reproduced_at_n0") is not True:
            raise MemberBuildError(f"sequence n0 anchor claim drift at row {index}")

        row_descriptor = bundle_index.get("row_manifest")
        if type(row_descriptor) is not dict or set(row_descriptor) != {
            "byte_length",
            "path",
            "sha256",
        }:
            raise MemberBuildError(f"row-manifest descriptor drift at row {index}")
        row_relative = partition_root / safe_relative(row_descriptor["path"])
        row_path_text = row_relative.as_posix()
        row_payload = read_regular(
            REPORT / row_relative,
            f"historical partition row {index}",
            normative=False,
            cap=2 * 1024 * 1024,
        )
        require_exact_int(
            row_descriptor.get("byte_length"), len(row_payload), f"row byte length {index}"
        )
        if sha256(row_payload) != row_descriptor.get("sha256"):
            raise MemberBuildError(f"row-manifest SHA drift at row {index}")
        row = parse_canonical(row_payload, f"partition row {index}")
        if row.get("schema") != "encounter_control_free_production_initial_row_v1":
            raise MemberBuildError(f"partition-row schema drift at row {index}")
        require_exact_int(row.get("configuration_index"), index, f"row index {index}")
        if row.get("configuration_label") != label:
            raise MemberBuildError(f"partition-row label drift at row {index}")
        require_exact_int(row.get("expected_states"), state_count, f"row states {index}")
        if row.get("configuration_sha256") != CONFIGURATION_SHA256:
            raise MemberBuildError(f"partition-row configuration pin drift at {index}")
        row_axes = row.get("axes")
        sequence_axes = sequence.get("axes")
        if (
            type(row_axes) is not list
            or type(sequence_axes) is not list
            or len(row_axes) != 3
            or len(sequence_axes) != 3
        ):
            raise MemberBuildError(f"three row/sequence axes required at row {index}")

        axes: list[dict[str, Any]] = []
        for axis_index, coordinate in enumerate(AXIS_ORDER):
            sequence_axis = sequence_axes[axis_index]
            row_axis = row_axes[axis_index]
            if type(sequence_axis) is not dict or type(row_axis) is not dict:
                raise MemberBuildError(f"axis objects required at {index}:{coordinate}")
            if (
                sequence_axis.get("coordinate") != coordinate
                or row_axis.get("coordinate") != coordinate
            ):
                raise MemberBuildError(f"axis-order drift at {index}:{coordinate}")
            partition_descriptor = row_axis.get("partition_file")
            if type(partition_descriptor) is not dict or set(partition_descriptor) != {
                "byte_length",
                "path",
                "sha256",
            }:
                raise MemberBuildError(f"partition descriptor drift at {index}:{coordinate}")
            partition_relative = partition_root / safe_relative(partition_descriptor["path"])
            partition_payload = read_regular(
                REPORT / partition_relative,
                f"historical exact partition {index}:{coordinate}",
                normative=False,
                cap=2 * 1024 * 1024,
            )
            require_exact_int(
                partition_descriptor.get("byte_length"),
                len(partition_payload),
                f"partition byte length {index}:{coordinate}",
            )
            partition_digest = sha256(partition_payload)
            if partition_digest != partition_descriptor.get("sha256"):
                raise MemberBuildError(f"partition SHA drift at {index}:{coordinate}")
            partition = parse_canonical(partition_payload, f"exact partition {index}:{coordinate}")
            expected_partition = expected_partition_geometry(sequence_axis)
            exact_equal(
                partition,
                expected_partition,
                f"independent partition reconstruction failed at {index}:{coordinate}",
            )
            cell_count = partition["size"]
            periodic = partition["periodic"]
            alignment = require_nonempty_string(
                sequence_axis.get("alignment"), f"alignment {index}:{coordinate}"
            )
            alignment_counts[alignment] += 1
            total_cells += cell_count
            total_edges += cell_count if periodic else cell_count - 1
            periodic_seams += int(periodic)
            exact_box = {
                "domain_start_exact": partition["domain_start_exact"],
                "domain_width_exact": partition["domain_width_exact"],
            }
            axis_binding: dict[str, Any] = {
                "alignment": alignment,
                "cell_count": cell_count,
                "coordinate": coordinate,
                "exact_box_or_period": exact_box,
                "partition_report_relative_path": partition_relative.as_posix(),
                "partition_schema": partition["schema"],
                "partition_sha256": partition_digest,
                "periodic": periodic,
                "refinement_family_id": semantic["refinement_family_id"],
                "refinement_member_id": semantic["refinement_member_id"],
                "sequence_id": expected_sequence_id,
                "sequence_source_row_canonical_sha256": config_digest,
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
                "configuration_geometry_sha256": domain_digest(
                    "encounter-configuration-geometry-v1", geometry_record
                ),
                "configuration_index": index,
                "initial_partition_row_manifest_path": row_path_text,
                "initial_partition_row_manifest_sha256": sha256(row_payload),
                "n0_anchor_expected_states": state_count,
                "n0_anchor_shape": shape,
                "n0_axes": axes,
                "physical_parameter_bundle_sha256": physical_digest,
                "refinement_family_id": semantic["refinement_family_id"],
                "refinement_member_id": semantic["refinement_member_id"],
                "sequence_id": expected_sequence_id,
                "sequence_source_row_canonical_sha256": config_digest,
                "sequence_source_row_index": index,
            }
        )
        total_states += state_count

    counts = {
        "axis_cell_count": total_cells,
        "axis_count": sum(alignment_counts.values()),
        "axis_edge_count": total_edges,
        "configuration_count": len(bindings),
        "periodic_seam_count": periodic_seams,
        "profile_index_count": len(bindings) * len(PROFILE_ORDER),
        "total_virtual_tensor_state_count": total_states,
    }
    exact_equal(
        dict(sorted(alignment_counts.items())),
        EXPECTED_ALIGNMENT_COUNTS,
        "alignment-count reconstruction drift",
    )
    exact_equal(counts, EXPECTED_COUNTS, "global member reconstruction-count drift")
    exact_equal(
        member_v3.get("n0_sequence_bindings"),
        bindings,
        "member v3 does not equal independent twelve-row/thirty-six-partition replay",
    )
    return bindings, counts


def role_bindings() -> dict[str, dict[str, str]]:
    return {
        "configuration_source": {
            "path": CONFIGURATION_RELATIVE,
            "sha256": CONFIGURATION_SHA256,
        },
        "factorization_source": {
            "path": FACTORIZATION_RELATIVE,
            "sha256": FACTORIZATION_SHA256,
        },
        "ideal_formula_source": {
            "path": IDEAL_RELATIVE,
            "sha256": IDEAL_SHA256,
        },
        "reference_density_source": {
            "path": REFERENCE_RELATIVE,
            "sha256": REFERENCE_SHA256,
        },
    }


def build_candidate() -> dict[str, Any]:
    (
        member_v3,
        reference,
        _ideal,
        _factorization,
        configuration,
        refinement,
        partition_bundle,
    ) = validate_primary_sources()
    historical_roles = member_v3.get("role_bindings")
    expected_historical_roles = role_bindings()
    expected_historical_roles["factorization_source"] = {
        "path": HISTORICAL_FACTORIZATION_V1_RELATIVE,
        "sha256": HISTORICAL_FACTORIZATION_V1_SHA256,
    }
    exact_equal(
        historical_roles,
        expected_historical_roles,
        "member v3 historical role-1--4 contract drift or registry injection",
    )
    bindings, counts = reconstruct_bindings(
        member_v3,
        reference,
        configuration,
        refinement,
        partition_bundle,
    )
    semantics = dict(MEMBER_SEMANTICS)
    semantic_ids = semantic_id_records()
    roles = role_bindings()
    identity = {
        "configuration_order": list(EXPECTED_CONFIGURATION_ORDER),
        "configuration_semantic_ids": semantic_ids,
        "member_semantics": semantics,
        "n0_sequence_bindings": bindings,
        "role_bindings_1_through_4": roles,
    }
    identity_sha256 = domain_digest(IDENTITY_DOMAIN, identity)
    if identity_sha256 != KNOWN_IDENTITY_SHA256:
        raise MemberBuildError(
            "known v4 identity mismatch after independent reconstruction: "
            f"{identity_sha256} != {KNOWN_IDENTITY_SHA256}"
        )
    candidate = {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "configuration_order": list(EXPECTED_CONFIGURATION_ORDER),
        "configuration_semantic_ids": semantic_ids,
        "identity_properties": IDENTITY_PROPERTIES,
        "member_identity_sha256": identity_sha256,
        "member_semantics": semantics,
        "n0_sequence_bindings": bindings,
        "reconstruction_counts": counts,
        "role_bindings": roles,
        "schema": SCHEMA,
        "source_lineage_evidence": {
            "initial_partition_bundle": {
                "path": PARTITION_BUNDLE_RELATIVE,
                "sha256": PARTITION_BUNDLE_SHA256,
            },
            "joint_refinement_family": {
                "path": REFINEMENT_RELATIVE,
                "sha256": REFINEMENT_SHA256,
            },
            "predecessor_member_v3": {
                "path": MEMBER_V3_RELATIVE,
                "sha256": MEMBER_V3_SHA256,
            },
        },
        "status": STATUS,
    }
    require_false_claims(candidate["claim_boundary"], "member v4 candidate")

    def reject_registry(node: Any) -> None:
        if type(node) is dict:
            for key, value in node.items():
                if "registry" in key.lower():
                    raise MemberBuildError("method-registry injection into member candidate")
                reject_registry(value)
        elif type(node) is list:
            for value in node:
                reject_registry(value)
        elif type(node) is str and "method_parameter_registry" in node.lower():
            raise MemberBuildError("method-registry value injection into member candidate")

    reject_registry(candidate)
    return candidate


def unlink_owned(parent: int, leaf: str, identity: tuple[int, int]) -> bool:
    try:
        current = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if (current.st_dev, current.st_ino) != identity:
        return False
    os.unlink(leaf, dir_fd=parent)
    return True


def parent_matches(descriptor: int, identity: tuple[int, int]) -> bool:
    try:
        observed = os.fstat(descriptor)
    except BaseException:
        return False
    return (
        stat.S_ISDIR(observed.st_mode)
        and (
            observed.st_dev,
            observed.st_ino,
        )
        == identity
    )


def publish_no_replace(path: Path, payload: bytes) -> None:
    descriptors, leaf, identities = open_anchored_parent(path)
    parent = descriptors[-1]
    parent_stat = os.fstat(parent)
    parent_identity = parent_stat.st_dev, parent_stat.st_ino
    stage_leaf = f".{leaf}.{secrets.token_hex(16)}.stage"
    recovery_descriptors: tuple[int, ...] = ()
    descriptor = -1
    transaction: StageCreationTransaction | None = None
    stage_identity: tuple[int, int] | None = None
    stage_attempted = False
    final_attempted = False
    try:
        stage_attempted = True
        transaction = StageCreationTransaction(parent, stage_leaf)
        transaction.start()
        transaction.await_ready()
        descriptor = -1 if transaction.descriptor is None else transaction.descriptor
        stage_identity = transaction.identity
        if descriptor < 0 or stage_identity is None:
            raise MemberBuildError("stage transaction result missing")
        transaction.release_descriptor(descriptor)

        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0 or count > len(payload) - written:
                raise MemberBuildError("short staged write")
            written += count
        os.fchmod(descriptor, 0o444)
        os.fsync(descriptor)
        staged = os.fstat(descriptor)
        if (
            (staged.st_dev, staged.st_ino) != stage_identity
            or stat.S_IMODE(staged.st_mode) != 0o444
            or staged.st_nlink != 1
            or staged.st_size != len(payload)
        ):
            raise MemberBuildError("staged output identity/mode/size drift")
        os.close(descriptor)
        descriptor = -1

        final_attempted = True
        try:
            os.link(
                stage_leaf,
                leaf,
                src_dir_fd=parent,
                dst_dir_fd=parent,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise MemberBuildError(f"refusing to replace existing output: {path}") from error
        if not unlink_owned(parent, stage_leaf, stage_identity):
            raise MemberBuildError("staging identity changed before cleanup")
        os.fsync(parent)
        final = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (final.st_dev, final.st_ino) != stage_identity
            or stat.S_IMODE(final.st_mode) != 0o444
            or final.st_nlink != 1
            or final.st_size != len(payload)
        ):
            raise MemberBuildError("published output identity/mode/size drift")
        if (
            read_regular(
                path,
                "published member-v4 acknowledgement",
                normative=True,
                cap=len(payload),
            )
            != payload
        ):
            raise MemberBuildError("published output byte acknowledgement drift")
        acknowledged = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (acknowledged.st_dev, acknowledged.st_ino) != stage_identity
            or stat.S_IMODE(acknowledged.st_mode) != 0o444
            or acknowledged.st_nlink != 1
            or acknowledged.st_size != len(payload)
        ):
            raise MemberBuildError("published output post-read identity drift")
        verify_anchored_parent(path, identities)
    except BaseException:
        if transaction is not None:
            transaction.settle()
            if stage_identity is None:
                stage_identity = transaction.identity
            if transaction.descriptor is not None:
                if descriptor < 0:
                    descriptor = transaction.descriptor
                elif descriptor != transaction.descriptor:
                    close_safely(transaction.descriptor)
                transaction.descriptor = None
        if descriptor >= 0 and stage_identity is None:
            try:
                opened = _STAGE_FSTAT(descriptor)
                stage_identity = opened.st_dev, opened.st_ino
            except BaseException:
                pass
        close_safely(descriptor)
        descriptor = -1

        cleanup_parent = -1
        if parent_matches(parent, parent_identity):
            cleanup_parent = parent
        else:
            try:
                recovered, recovered_leaf, recovered_identities = open_anchored_parent(path)
                if (
                    recovered_leaf == leaf
                    and recovered_identities == identities
                    and parent_matches(recovered[-1], parent_identity)
                ):
                    recovery_descriptors = recovered
                    cleanup_parent = recovered[-1]
                else:
                    for item in reversed(recovered):
                        close_safely(item)
            except BaseException:
                pass
        if cleanup_parent >= 0 and stage_identity is not None:
            if final_attempted:
                try:
                    unlink_owned(cleanup_parent, leaf, stage_identity)
                except BaseException:
                    pass
            if stage_attempted:
                try:
                    unlink_owned(cleanup_parent, stage_leaf, stage_identity)
                except BaseException:
                    pass
            try:
                os.fsync(cleanup_parent)
            except BaseException:
                pass
        raise
    finally:
        if transaction is not None:
            transaction.settle()
            if transaction.descriptor is not None:
                close_safely(transaction.descriptor)
                transaction.descriptor = None
        close_safely(descriptor)
        for item in reversed(recovery_descriptors):
            close_safely(item)
        for item in reversed(descriptors):
            close_safely(item)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that --output equals the independent reconstruction",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        payload = canonical_bytes(build_candidate())
        output = Path(os.path.abspath(os.fspath(arguments.output.expanduser())))
        if arguments.check:
            observed = read_regular(output, "member v4 candidate", normative=True)
            if observed != payload:
                raise MemberBuildError("member v4 candidate byte drift")
            print(
                "PASS_MEMBER_SPEC_V4_CANDIDATE_CHECK "
                f"identity_sha256={KNOWN_IDENTITY_SHA256} sha256={sha256(payload)}"
            )
            return 0
        publish_no_replace(output, payload)
        print(
            "PASS_MEMBER_SPEC_V4_CANDIDATE_BUILD "
            f"path={output} identity_sha256={KNOWN_IDENTITY_SHA256} "
            f"sha256={sha256(payload)}"
        )
        return 0
    except (MemberBuildError, OSError) as error:
        print(f"ERROR MemberSpecV4CandidateBuild: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
