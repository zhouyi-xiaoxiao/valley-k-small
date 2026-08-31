#!/usr/bin/env python3
"""Independently validate the C1/C2 n0 structural-member v4 candidate."""

from __future__ import annotations

import argparse
import errno
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
OUTPUT_RELATIVE: Final = "artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json"
DEFAULT_INPUT: Final = REPORT / OUTPUT_RELATIVE
V3_RELATIVE: Final = (
    "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/"
    "continuum_c1_c2_n0_member_spec_v3_candidate.json"
)
REFERENCE_RELATIVE: Final = "artifacts/data/continuum_c1_reference_density_source_v1.json"
IDEAL_RELATIVE: Final = "artifacts/data/continuum_c1_ideal_formula_source_v1.json"
FACTOR_RELATIVE: Final = "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"
CONFIG_RELATIVE: Final = "artifacts/data/physical_configuration_family_control_free_v1.json"
REFINEMENT_RELATIVE: Final = "artifacts/data/continuum_c1_genuine_joint_refinement_family_v2.json"
BUNDLE_RELATIVE: Final = "artifacts/data/physical_production_initial_stream_v1/bundle.json"

PINNED_SHA256: Final = {
    V3_RELATIVE: "b5eea6553d329bcbc4a1eb301dd3d5fb5b5acd387b80bfee5094286d3ca8ab71",
    REFERENCE_RELATIVE: ("7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575"),
    IDEAL_RELATIVE: "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be",
    FACTOR_RELATIVE: "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26",
    CONFIG_RELATIVE: "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    REFINEMENT_RELATIVE: ("1f7bc61ac37444c0fdb2c0b74924a4b81ed8e6d6ab70c794ebe3401156b5bee9"),
    BUNDLE_RELATIVE: "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e",
}
V1_FACTOR_RELATIVE: Final = "artifacts/data/continuum_c1_factorization_source_v1.json"
V1_FACTOR_SHA256: Final = "70cb49e63c496d489887c764c812671b03a7352d5752f6663c377734739a1dca"
SCHEMA: Final = "encounter_continuum_c1_c2_n0_member_spec_v4_candidate"
STATUS: Final = (
    "STRUCTURAL_PARTITION_IDENTITY_V4_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
)
IDENTITY_DOMAIN: Final = "encounter-continuum-c1-c2-n0-member-identity-v4"
KNOWN_IDENTITY: Final = "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
KNOWN_V3_IDENTITY: Final = "90f4be333a70797792d7b7ba74b7bec213db304360569b349edf92ae7aaee229"
COORDINATES: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)
CONFIGURATION_ORDER: Final = (
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
SEMANTIC_TRIPLES: Final = (
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
ALIGNMENT_COUNTS: Final = {
    "cell_centred_periodic_base": 10,
    "cell_centred_periodic_half_shift": 2,
    "cell_centred_reflecting": 20,
    "vertex_centred_reflecting_dual": 4,
}
COUNTS: Final = {
    "axis_cell_count": 5_037,
    "axis_count": 36,
    "axis_edge_count": 5_013,
    "configuration_count": 12,
    "periodic_seam_count": 12,
    "profile_index_count": 48,
    "total_virtual_tensor_state_count": 34_787_462,
}
SEMANTICS: Final = {
    "configuration_count": 12,
    "configuration_rows_are_finite_anchors": True,
    "coordinate_order": list(COORDINATES),
    "every_cartesian_interval_endpoint_combination_is_a_model": False,
    "one_formula_defined_correlated_member_per_configuration": True,
    "physical_dimension": 2,
    "quotient_dimension": 3,
    "scalar_convention": "complex_inner_product_conjugate_first_factor",
}
PROPERTIES: Final = {
    "alignment_counts": ALIGNMENT_COUNTS,
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
MAX_BYTES: Final = 64 * 1024 * 1024
MAX_NODES: Final = 500_000
MAX_DEPTH: Final = 64
MAX_CHARACTERS: Final = 16 * 1024 * 1024


class MemberValidationError(RuntimeError):
    """The candidate or an authority failed an independent invariant."""


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def encode_canonical(value: Any) -> bytes:
    node_count = 0
    character_count = 0

    def visit(node: Any, depth: int) -> None:
        nonlocal node_count, character_count
        node_count += 1
        if node_count > MAX_NODES or depth > MAX_DEPTH:
            raise MemberValidationError("JSON tree resource cap exceeded")
        if isinstance(node, float):
            raise MemberValidationError("floating JSON literal rejected")
        if type(node) is int:
            if node.bit_length() > 256:
                raise MemberValidationError("integer resource cap exceeded")
        elif type(node) is bool or node is None:
            pass
        elif type(node) is str:
            character_count += len(node)
            if (
                len(node) > 2 * 1024 * 1024
                or character_count > MAX_CHARACTERS
                or unicodedata.normalize("NFC", node) != node
            ):
                raise MemberValidationError("string resource/NFC invariant failed")
        elif type(node) is list:
            for item in node:
                visit(item, depth + 1)
        elif type(node) is dict:
            for key, item in node.items():
                if type(key) is not str:
                    raise MemberValidationError("non-string JSON key")
                visit(key, depth + 1)
                visit(item, depth + 1)
        else:
            raise MemberValidationError(f"unsupported JSON type {type(node).__name__}")

    visit(value, 0)
    result = (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")
    if len(result) > MAX_BYTES:
        raise MemberValidationError("canonical JSON byte cap exceeded")
    return result


def decode_canonical(payload: bytes, context: str) -> dict[str, Any]:
    if not payload or len(payload) > MAX_BYTES:
        raise MemberValidationError(f"JSON byte cap failed: {context}")

    def object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if type(key) is not str or key in result:
                raise MemberValidationError(f"duplicate JSON key: {context}")
            result[key] = value
        return result

    def no_noninteger_number(token: str) -> Any:
        raise MemberValidationError(f"non-integer JSON number {token}: {context}")

    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=object_without_duplicates,
            parse_float=no_noninteger_number,
            parse_constant=no_noninteger_number,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError,
    ) as error:
        raise MemberValidationError(f"strict JSON parse failed: {context}") from error
    if type(value) is not dict or encode_canonical(value) != payload:
        raise MemberValidationError(f"canonical byte representation failed: {context}")
    return value


def same(actual: Any, expected: Any, context: str) -> None:
    if encode_canonical(actual) != encode_canonical(expected):
        raise MemberValidationError(context)


def false_claims(value: Any, context: str) -> None:
    if (
        type(value) is not dict
        or set(value) != set(CLAIM_KEYS)
        or any(item is not False for item in value.values())
    ):
        raise MemberValidationError(f"exact all-false claim map required: {context}")


def exact_integer(value: Any, expected: int, context: str) -> None:
    if type(value) is not int or value != expected:
        raise MemberValidationError(f"exact integer failed: {context}")


def safe_relative(value: Any) -> Path:
    if type(value) is not str or not value or len(value) > 1024 or "\\" in value:
        raise MemberValidationError(f"unsafe report-relative path: {value!r}")
    parsed = PurePosixPath(value)
    if (
        parsed.is_absolute()
        or len(parsed.parts) > 24
        or any(part in {"", ".", ".."} for part in parsed.parts)
        or parsed.as_posix() != value
    ):
        raise MemberValidationError(f"unsafe report-relative path: {value!r}")
    return Path(*parsed.parts)


def close_quietly(descriptor: int) -> None:
    if descriptor < 0:
        return
    try:
        os.close(descriptor)
    except BaseException:
        pass


def parent_chain(path: Path) -> tuple[tuple[int, ...], str, tuple[tuple[int, int], ...]]:
    absolute = Path(os.path.abspath(path))
    if (
        not path.is_absolute()
        or path != absolute
        or len(path.parts) < 2
        or any(part in {"", ".", ".."} for part in path.parts[1:])
    ):
        raise MemberValidationError(f"canonical absolute path required: {path}")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptors: list[int] = []
    identities: list[tuple[int, int]] = []
    try:
        descriptor = os.open(path.anchor, flags)
        descriptors.append(descriptor)
        observed = os.fstat(descriptor)
        if not stat.S_ISDIR(observed.st_mode):
            raise MemberValidationError("filesystem anchor is not a directory")
        identities.append((observed.st_dev, observed.st_ino))
        for component in path.parts[1:-1]:
            descriptor = os.open(component, flags, dir_fd=descriptors[-1])
            descriptors.append(descriptor)
            observed = os.fstat(descriptor)
            if not stat.S_ISDIR(observed.st_mode):
                raise MemberValidationError("non-directory path component")
            identities.append((observed.st_dev, observed.st_ino))
        return tuple(descriptors), path.name, tuple(identities)
    except OSError as error:
        for descriptor in reversed(descriptors):
            close_quietly(descriptor)
        if error.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise MemberValidationError("symlink path component rejected") from error
        raise
    except BaseException:
        for descriptor in reversed(descriptors):
            close_quietly(descriptor)
        raise


def stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_nlink,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def verify_parent_chain(path: Path, expected: tuple[tuple[int, int], ...]) -> None:
    descriptors, _, actual = parent_chain(path)
    try:
        if actual != expected:
            raise MemberValidationError(f"live parent-chain identity drift: {path}")
    finally:
        for descriptor in reversed(descriptors):
            close_quietly(descriptor)


def snapshot(path: Path, context: str, *, normative: bool, cap: int = MAX_BYTES) -> bytes:
    descriptors, leaf, identities = parent_chain(path)
    parent = descriptors[-1]
    descriptor = -1
    live_descriptor = -1
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        descriptor = os.open(leaf, flags, dir_fd=parent)
        before = os.fstat(descriptor)
        allowed = {0o444} if normative else {0o444, 0o644}
        if (
            not stat.S_ISREG(before.st_mode)
            or stat.S_IMODE(before.st_mode) not in allowed
            or before.st_nlink != 1
            or before.st_size <= 0
            or before.st_size > cap
        ):
            raise MemberValidationError(f"bounded source invariant failed: {context}")
        pieces: list[bytes] = []
        remaining = before.st_size
        while remaining:
            piece = os.read(descriptor, min(remaining, 65_536))
            if not piece:
                raise MemberValidationError(f"short source read: {context}")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise MemberValidationError(f"source grew during read: {context}")
        after = os.fstat(descriptor)
        named = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if stat_identity(before) != stat_identity(after) or stat_identity(after) != stat_identity(
            named
        ):
            raise MemberValidationError(f"source identity changed: {context}")
        verify_parent_chain(path, identities)
        live_descriptor = os.open(leaf, flags, dir_fd=parent)
        if stat_identity(os.fstat(live_descriptor)) != stat_identity(after):
            raise MemberValidationError(f"live reopen identity changed: {context}")
        return b"".join(pieces)
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise MemberValidationError(f"symlink leaf rejected: {context}") from error
        raise
    finally:
        close_quietly(live_descriptor)
        close_quietly(descriptor)
        for item in reversed(descriptors):
            close_quietly(item)


def load(relative: str, context: str, *, normative: bool) -> dict[str, Any]:
    payload = snapshot(REPORT / safe_relative(relative), context, normative=normative)
    if sha256(payload) != PINNED_SHA256[relative]:
        raise MemberValidationError(f"authority SHA-256 mismatch: {context}")
    return decode_canonical(payload, context)


def fraction(value: Any) -> Fraction:
    if type(value) is not str or value.count("/") != 1:
        raise MemberValidationError(f"canonical rational required: {value!r}")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise MemberValidationError(f"invalid rational: {value!r}") from error
    if f"{result.numerator}/{result.denominator}" != value:
        raise MemberValidationError(f"noncanonical rational: {value!r}")
    return result


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def digest(domain: str, value: Any) -> str:
    return sha256(domain.encode("ascii") + b"\0" + encode_canonical(value))


def reconstruct_partition(axis: Any) -> dict[str, Any]:
    if type(axis) is not dict:
        raise MemberValidationError("refinement axis must be an object")
    coordinate = axis.get("coordinate")
    alignment = axis.get("alignment")
    domain = axis.get("domain")
    if (
        type(coordinate) is not str
        or not coordinate
        or type(alignment) is not str
        or not alignment
        or type(domain) is not dict
    ):
        raise MemberValidationError("axis identifiers/domain invalid")
    start_text = domain.get("start_exact", domain.get("lower_exact"))
    width_text = domain.get("period_exact", domain.get("width_exact"))
    start = fraction(start_text)
    width = fraction(width_text)
    size = axis.get("anchor_size")
    if type(size) is not int or size < 2 or width <= 0:
        raise MemberValidationError("axis size/width invalid")
    end = start + width
    shift_text = axis.get("periodic_shift_n0_exact", "0/1")
    shift = fraction(shift_text)
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
        raise MemberValidationError(f"unrecognized alignment: {alignment}")
    exact_integer(axis.get("anchor_interval_count"), interval_count, "axis interval count")
    if fraction(axis.get("spacing_h0_exact")) != spacing:
        raise MemberValidationError("axis spacing formula mismatch")
    return {
        "cell_segments_exact": [
            [[fraction_text(left), fraction_text(right)] for left, right in cell]
            for cell in segments
        ],
        "cell_volumes_exact": [fraction_text(item) for item in volumes],
        "construction": construction,
        "coordinate": coordinate,
        "domain_start_exact": start_text,
        "domain_width_exact": width_text,
        "periodic": periodic,
        "periodic_shift_exact": shift_text,
        "positions_exact": [fraction_text(item) for item in positions],
        "schema": "encounter_exact_axis_partition_v1",
        "size": size,
    }


def semantic_records() -> list[dict[str, str]]:
    return [
        {
            "authority_label": label,
            "refinement_family_id": family,
            "refinement_member_id": member,
        }
        for label, family, member in SEMANTIC_TRIPLES
    ]


def expected_roles() -> dict[str, dict[str, str]]:
    return {
        "configuration_source": {
            "path": CONFIG_RELATIVE,
            "sha256": PINNED_SHA256[CONFIG_RELATIVE],
        },
        "factorization_source": {
            "path": FACTOR_RELATIVE,
            "sha256": PINNED_SHA256[FACTOR_RELATIVE],
        },
        "ideal_formula_source": {
            "path": IDEAL_RELATIVE,
            "sha256": PINNED_SHA256[IDEAL_RELATIVE],
        },
        "reference_density_source": {
            "path": REFERENCE_RELATIVE,
            "sha256": PINNED_SHA256[REFERENCE_RELATIVE],
        },
    }


def validate_authority_semantics(
    v3: dict[str, Any],
    reference: dict[str, Any],
    ideal: dict[str, Any],
    factor: dict[str, Any],
    configuration: dict[str, Any],
    refinement: dict[str, Any],
    bundle: dict[str, Any],
) -> None:
    exact_v3_keys = {
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
    if (
        set(v3) != exact_v3_keys
        or v3.get("schema") != "encounter_continuum_c1_c2_n0_member_spec_v3_candidate"
        or v3.get("status")
        != (
            "STRUCTURAL_PARTITION_IDENTITY_CANDIDATE_ONLY_"
            "NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
        )
    ):
        raise MemberValidationError("v3 structural contract or registry injection")
    false_claims(v3.get("claim_boundary"), "v3")
    same(v3.get("identity_properties"), PROPERTIES, "v3 identity properties changed")
    same(v3.get("member_semantics"), SEMANTICS, "v3 member semantics changed")
    same(v3.get("reconstruction_counts"), COUNTS, "v3 counts changed")
    v3_identity = {
        "configuration_order": v3.get("configuration_order"),
        "configuration_semantic_ids": v3.get("configuration_semantic_ids"),
        "coordinate_order": v3.get("member_semantics", {}).get("coordinate_order"),
        "n0_sequence_bindings": v3.get("n0_sequence_bindings"),
        "role_bindings_1_through_4": v3.get("role_bindings"),
        "scalar_convention": v3.get("member_semantics", {}).get("scalar_convention"),
    }
    if (
        v3.get("member_identity_sha256") != KNOWN_V3_IDENTITY
        or digest("encounter-continuum-c1-c2-n0-member-identity-v3", v3_identity)
        != KNOWN_V3_IDENTITY
    ):
        raise MemberValidationError("v3 identity-domain replay changed")
    historical_roles = expected_roles()
    historical_roles["factorization_source"] = {
        "path": V1_FACTOR_RELATIVE,
        "sha256": V1_FACTOR_SHA256,
    }
    same(v3.get("role_bindings"), historical_roles, "v3 historical role binding changed")

    if (
        reference.get("schema") != "encounter_continuum_c1_reference_density_source_v1"
        or reference.get("status")
        != "FROZEN_CONTROL_FREE_REFERENCE_DENSITY_AUTHORITY_ONLY_NO_COMPLETE_C0_C1_C2"
    ):
        raise MemberValidationError("reference schema/status changed")
    if type(reference.get("claim_boundary")) is not dict or any(
        item is not False for item in reference["claim_boundary"].values()
    ):
        raise MemberValidationError("reference claim promotion")
    same(
        reference.get("coordinate_order"),
        list(COORDINATES),
        "reference coordinate order changed",
    )
    same(
        reference.get("source_pins", {}).get("configuration_source"),
        {"path": CONFIG_RELATIVE, "sha256": PINNED_SHA256[CONFIG_RELATIVE]},
        "reference nested configuration binding changed",
    )

    if (
        ideal.get("schema") != "encounter_continuum_c1_ideal_formula_source_v1"
        or ideal.get("status")
        != "FROZEN_CONTROL_FREE_IDEAL_FORMULA_AUTHORITY_ONLY_NO_PRODUCTION_ACCEPTANCE"
    ):
        raise MemberValidationError("ideal schema/status changed")
    if type(ideal.get("claim_boundary")) is not dict or any(
        item is not False for item in ideal["claim_boundary"].values()
    ):
        raise MemberValidationError("ideal claim promotion")
    same(
        ideal.get("member_semantics"),
        {
            "common_flux_uses_one_formula_defined_exact_value": True,
            "formula_defined_member_is_independent_of_production_centres": True,
            "global_gauge_is_single_scalar_per_configuration": True,
            "one_correlated_distinguished_member_required": True,
        },
        "ideal member-semantics changed",
    )

    if factor.get(
        "schema"
    ) != "encounter_continuum_c1_factorization_source_v2_candidate" or factor.get("status") != (
        "OUTCOME_FREE_CONTROL_FREE_FACTORIZATION_CANDIDATE_ONLY_"
        "NOT_EXTERNALLY_COMMITTED_NO_NUMERIC_ENCLOSURES_NO_CONCRETE_KILLING"
    ):
        raise MemberValidationError("factorization v2 schema/status changed or v1 fallback")
    false_claims(factor.get("claim_boundary"), "factorization v2")
    same(
        factor.get("source_pins", {}).get("configuration_source"),
        {
            "path": CONFIG_RELATIVE,
            "schema": "encounter_physical_configuration_family_control_free_v1",
            "sha256": PINNED_SHA256[CONFIG_RELATIVE],
        },
        "factorization nested configuration pin changed",
    )
    same(
        factor.get("source_pins", {}).get("initial_partition_bundle"),
        {
            "path": BUNDLE_RELATIVE,
            "schema": "encounter_control_free_production_initial_stream_v1",
            "sha256": PINNED_SHA256[BUNDLE_RELATIVE],
        },
        "factorization nested partition pin changed",
    )
    same(
        factor.get("outcome_free_contract"),
        {
            "budget_present": False,
            "concrete_killing_tensor_present": False,
            "control_weights_present": False,
            "external_commitment_present": False,
            "numeric_enclosure_payload_present": False,
            "primitive_source_only": True,
            "production_bridge_present": False,
        },
        "factorization outcome-free contract changed",
    )

    if configuration.get("schema") != "encounter_physical_configuration_family_control_free_v1":
        raise MemberValidationError("configuration schema changed")
    exact_integer(configuration.get("configuration_count"), 12, "configuration count")
    same(
        configuration.get("configuration_order"),
        list(CONFIGURATION_ORDER),
        "configuration order changed",
    )
    same(
        configuration.get("coordinate_order"),
        list(COORDINATES),
        "configuration coordinate order changed",
    )
    for key in (
        "authorizes_scientific_execution",
        "contains_budget_value",
        "contains_control_values",
    ):
        if configuration.get(key) is not False:
            raise MemberValidationError(f"configuration claim promotion: {key}")

    if refinement.get("schema") != "encounter_continuum_c1_genuine_joint_refinement_family_v2":
        raise MemberValidationError("refinement schema changed")
    exact_integer(refinement.get("sequence_count"), 12, "refinement sequence count")
    same(
        refinement.get("sequence_order"),
        list(CONFIGURATION_ORDER),
        "refinement order changed",
    )
    scope = refinement.get("established_scope")
    if type(scope) is not dict:
        raise MemberValidationError("refinement established-scope missing")
    for key in (
        "finite_twelve_family_geometric_uniformity_proved",
        "genuine_refinement_sequences_defined",
        "maximum_axis_spacing_limit_proved",
        "n0_configuration_geometry_anchor_exact",
        "shape_regularity_proved",
    ):
        if scope.get(key) is not True:
            raise MemberValidationError(f"refinement established-scope changed: {key}")
    if type(refinement.get("claim_boundary")) is not dict or any(
        item is not False for item in refinement["claim_boundary"].values()
    ):
        raise MemberValidationError("refinement claim promotion")

    if (
        bundle.get("schema") != "encounter_control_free_production_initial_stream_v1"
        or bundle.get("configuration_sha256") != PINNED_SHA256[CONFIG_RELATIVE]
    ):
        raise MemberValidationError("partition bundle schema/configuration binding changed")
    exact_integer(bundle.get("configuration_count"), 12, "partition bundle count")
    if type(bundle.get("flags")) is not dict:
        raise MemberValidationError("partition bundle flags missing")
    for key in (
        "authorizes_scientific_execution",
        "contains_budget_value",
        "contains_control_values",
        "full_operator_bound",
        "positive_budget_executed",
        "science_executed",
        "topology_complete",
    ):
        if bundle["flags"].get(key) is not False:
            raise MemberValidationError(f"partition bundle claim promotion: {key}")


def replay_bindings(
    v3: dict[str, Any],
    reference: dict[str, Any],
    configuration: dict[str, Any],
    refinement: dict[str, Any],
    bundle: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    configs = configuration.get("configurations")
    sequences = refinement.get("sequences")
    bundle_rows = bundle.get("rows")
    if (
        type(configs) is not list
        or type(sequences) is not list
        or type(bundle_rows) is not list
        or len(configs) != 12
        or len(sequences) != 12
        or len(bundle_rows) != 12
    ):
        raise MemberValidationError("twelve reconstruction rows required")
    semantics = semantic_records()
    same(v3.get("configuration_order"), list(CONFIGURATION_ORDER), "v3 order changed")
    same(v3.get("configuration_semantic_ids"), semantics, "v3 semantic IDs changed")
    physical = reference.get("physical_parameter_bundle")
    if type(physical) is not dict:
        raise MemberValidationError("physical-parameter bundle missing")
    physical_sha = digest("encounter-physical-parameter-bundle-v1", physical)
    partition_root = Path(BUNDLE_RELATIVE).parent
    result: list[dict[str, Any]] = []
    alignment_counter: Counter[str] = Counter()
    cell_count = 0
    edge_count = 0
    seam_count = 0
    state_count = 0

    for index, (config, sequence, row_pin, semantic) in enumerate(
        zip(configs, sequences, bundle_rows, semantics, strict=True)
    ):
        if type(config) is not dict or type(sequence) is not dict or type(row_pin) is not dict:
            raise MemberValidationError(f"row object missing at {index}")
        label = CONFIGURATION_ORDER[index]
        exact_integer(sequence.get("source_row_index"), index, f"sequence index {index}")
        exact_integer(row_pin.get("configuration_index"), index, f"bundle index {index}")
        if (
            type(config.get("label")) is not str
            or config["label"] != label
            or sequence.get("label") != label
            or row_pin.get("configuration_label") != label
        ):
            raise MemberValidationError(f"row label/order mismatch at {index}")
        shape = config.get("shape")
        states = config.get("expected_states")
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(item) is not int or item < 2 for item in shape)
            or type(states) is not int
            or states != shape[0] * shape[1] * shape[2]
        ):
            raise MemberValidationError(f"shape/state type or product mismatch at {index}")
        same(sequence.get("anchor_shape"), shape, f"anchor shape mismatch at {index}")
        exact_integer(sequence.get("anchor_expected_states"), states, f"sequence states {index}")
        exact_integer(row_pin.get("expected_states"), states, f"bundle states {index}")
        config_sha = sha256(encode_canonical(config))
        if sequence.get("source_row_canonical_sha256") != config_sha:
            raise MemberValidationError(f"source-row canonical digest mismatch at {index}")
        sequence_id = f"encounter_c1_joint_refinement_v2:{index}:{label}"
        if sequence.get("sequence_id") != sequence_id:
            raise MemberValidationError(f"sequence identifier mismatch at {index}")
        if sequence.get("anchor_geometry_exactly_reproduced_at_n0") is not True:
            raise MemberValidationError(f"n0 anchor assertion mismatch at {index}")

        descriptor = row_pin.get("row_manifest")
        if type(descriptor) is not dict or set(descriptor) != {
            "byte_length",
            "path",
            "sha256",
        }:
            raise MemberValidationError(f"row descriptor mismatch at {index}")
        row_relative = partition_root / safe_relative(descriptor["path"])
        row_bytes = snapshot(
            REPORT / row_relative,
            f"partition row {index}",
            normative=False,
            cap=2 * 1024 * 1024,
        )
        exact_integer(descriptor.get("byte_length"), len(row_bytes), f"row bytes {index}")
        if sha256(row_bytes) != descriptor.get("sha256"):
            raise MemberValidationError(f"row digest mismatch at {index}")
        row = decode_canonical(row_bytes, f"partition row {index}")
        if row.get("schema") != "encounter_control_free_production_initial_row_v1":
            raise MemberValidationError(f"row schema mismatch at {index}")
        exact_integer(row.get("configuration_index"), index, f"row index {index}")
        exact_integer(row.get("expected_states"), states, f"row states {index}")
        if (
            row.get("configuration_label") != label
            or row.get("configuration_sha256") != PINNED_SHA256[CONFIG_RELATIVE]
        ):
            raise MemberValidationError(f"row authority binding mismatch at {index}")
        row_axes = row.get("axes")
        sequence_axes = sequence.get("axes")
        if (
            type(row_axes) is not list
            or type(sequence_axes) is not list
            or len(row_axes) != 3
            or len(sequence_axes) != 3
        ):
            raise MemberValidationError(f"three axes required at {index}")

        axes: list[dict[str, Any]] = []
        for axis_index, coordinate in enumerate(COORDINATES):
            sequence_axis = sequence_axes[axis_index]
            row_axis = row_axes[axis_index]
            if (
                type(sequence_axis) is not dict
                or type(row_axis) is not dict
                or sequence_axis.get("coordinate") != coordinate
                or row_axis.get("coordinate") != coordinate
            ):
                raise MemberValidationError(f"axis order mismatch at {index}:{coordinate}")
            partition_pin = row_axis.get("partition_file")
            if type(partition_pin) is not dict or set(partition_pin) != {
                "byte_length",
                "path",
                "sha256",
            }:
                raise MemberValidationError(
                    f"partition descriptor mismatch at {index}:{coordinate}"
                )
            partition_relative = partition_root / safe_relative(partition_pin["path"])
            partition_bytes = snapshot(
                REPORT / partition_relative,
                f"partition {index}:{coordinate}",
                normative=False,
                cap=2 * 1024 * 1024,
            )
            exact_integer(
                partition_pin.get("byte_length"),
                len(partition_bytes),
                f"partition bytes {index}:{coordinate}",
            )
            partition_sha = sha256(partition_bytes)
            if partition_sha != partition_pin.get("sha256"):
                raise MemberValidationError(f"partition digest mismatch at {index}:{coordinate}")
            partition = decode_canonical(partition_bytes, f"partition {index}:{coordinate}")
            same(
                partition,
                reconstruct_partition(sequence_axis),
                f"independent partition replay mismatch at {index}:{coordinate}",
            )
            size = partition["size"]
            periodic = partition["periodic"]
            alignment = sequence_axis.get("alignment")
            if type(alignment) is not str or not alignment:
                raise MemberValidationError(f"alignment type mismatch at {index}:{coordinate}")
            alignment_counter[alignment] += 1
            cell_count += size
            edge_count += size if periodic else size - 1
            seam_count += int(periodic)
            axis_record: dict[str, Any] = {
                "alignment": alignment,
                "cell_count": size,
                "coordinate": coordinate,
                "exact_box_or_period": {
                    "domain_start_exact": partition["domain_start_exact"],
                    "domain_width_exact": partition["domain_width_exact"],
                },
                "partition_report_relative_path": partition_relative.as_posix(),
                "partition_schema": partition["schema"],
                "partition_sha256": partition_sha,
                "periodic": periodic,
                "refinement_family_id": semantic["refinement_family_id"],
                "refinement_member_id": semantic["refinement_member_id"],
                "sequence_id": sequence_id,
                "sequence_source_row_canonical_sha256": config_sha,
            }
            if periodic:
                axis_record["periodic_shift_n0_exact"] = sequence_axis["periodic_shift_n0_exact"]
            axes.append(axis_record)

        geometry = {
            "configuration_index": index,
            "configuration_row": config,
            "n0_partition_sha256s": [axis["partition_sha256"] for axis in axes],
        }
        result.append(
            {
                "authority_label": label,
                "configuration_geometry_sha256": digest(
                    "encounter-configuration-geometry-v1", geometry
                ),
                "configuration_index": index,
                "initial_partition_row_manifest_path": row_relative.as_posix(),
                "initial_partition_row_manifest_sha256": sha256(row_bytes),
                "n0_anchor_expected_states": states,
                "n0_anchor_shape": shape,
                "n0_axes": axes,
                "physical_parameter_bundle_sha256": physical_sha,
                "refinement_family_id": semantic["refinement_family_id"],
                "refinement_member_id": semantic["refinement_member_id"],
                "sequence_id": sequence_id,
                "sequence_source_row_canonical_sha256": config_sha,
                "sequence_source_row_index": index,
            }
        )
        state_count += states

    reconstructed_counts = {
        "axis_cell_count": cell_count,
        "axis_count": sum(alignment_counter.values()),
        "axis_edge_count": edge_count,
        "configuration_count": len(result),
        "periodic_seam_count": seam_count,
        "profile_index_count": len(result) * 4,
        "total_virtual_tensor_state_count": state_count,
    }
    same(dict(sorted(alignment_counter.items())), ALIGNMENT_COUNTS, "alignment counts differ")
    same(reconstructed_counts, COUNTS, "reconstruction counts differ")
    same(
        v3.get("n0_sequence_bindings"),
        result,
        "v3 bindings differ from independent replay",
    )
    return result, reconstructed_counts


def reject_registry(node: Any) -> None:
    if type(node) is dict:
        for key, item in node.items():
            if "registry" in key.lower():
                raise MemberValidationError("registry field injected into member")
            reject_registry(item)
    elif type(node) is list:
        for item in node:
            reject_registry(item)
    elif type(node) is str and "method_parameter_registry" in node.lower():
        raise MemberValidationError("registry value injected into member")


def expected_candidate() -> dict[str, Any]:
    v3 = load(V3_RELATIVE, "immutable member v3", normative=True)
    reference = load(REFERENCE_RELATIVE, "reference authority", normative=True)
    ideal = load(IDEAL_RELATIVE, "ideal authority", normative=True)
    factor = load(FACTOR_RELATIVE, "factorization v2 authority", normative=True)
    configuration = load(CONFIG_RELATIVE, "configuration authority", normative=True)
    bundle = load(BUNDLE_RELATIVE, "partition bundle", normative=True)
    refinement = load(REFINEMENT_RELATIVE, "joint-refinement evidence", normative=False)
    validate_authority_semantics(
        v3,
        reference,
        ideal,
        factor,
        configuration,
        refinement,
        bundle,
    )
    bindings, counts = replay_bindings(v3, reference, configuration, refinement, bundle)
    semantics = dict(SEMANTICS)
    semantic_ids = semantic_records()
    roles = expected_roles()
    identity = {
        "configuration_order": list(CONFIGURATION_ORDER),
        "configuration_semantic_ids": semantic_ids,
        "member_semantics": semantics,
        "n0_sequence_bindings": bindings,
        "role_bindings_1_through_4": roles,
    }
    identity_sha = digest(IDENTITY_DOMAIN, identity)
    if identity_sha != KNOWN_IDENTITY:
        raise MemberValidationError("known member-v4 identity does not independently replay")
    result = {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "configuration_order": list(CONFIGURATION_ORDER),
        "configuration_semantic_ids": semantic_ids,
        "identity_properties": PROPERTIES,
        "member_identity_sha256": identity_sha,
        "member_semantics": semantics,
        "n0_sequence_bindings": bindings,
        "reconstruction_counts": counts,
        "role_bindings": roles,
        "schema": SCHEMA,
        "source_lineage_evidence": {
            "initial_partition_bundle": {
                "path": BUNDLE_RELATIVE,
                "sha256": PINNED_SHA256[BUNDLE_RELATIVE],
            },
            "joint_refinement_family": {
                "path": REFINEMENT_RELATIVE,
                "sha256": PINNED_SHA256[REFINEMENT_RELATIVE],
            },
            "predecessor_member_v3": {
                "path": V3_RELATIVE,
                "sha256": PINNED_SHA256[V3_RELATIVE],
            },
        },
        "status": STATUS,
    }
    false_claims(result["claim_boundary"], "member v4")
    reject_registry(result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        path = Path(os.path.abspath(os.fspath(arguments.input.expanduser())))
        payload = snapshot(path, "member v4 candidate", normative=True)
        observed = decode_canonical(payload, "member v4 candidate")
        expected = expected_candidate()
        same(observed, expected, "member v4 candidate differs from independent replay")
        if observed.get("member_identity_sha256") != KNOWN_IDENTITY:
            raise MemberValidationError("candidate known identity mismatch")
        print(
            "PASS_MEMBER_SPEC_V4_CANDIDATE_VALIDATION "
            f"identity_sha256={KNOWN_IDENTITY} sha256={sha256(payload)}"
        )
        return 0
    except (MemberValidationError, OSError) as error:
        print(f"ERROR MemberSpecV4CandidateValidation: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
