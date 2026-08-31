#!/usr/bin/env python3
"""Independently validate the successor anti-vacuity policy v4 candidate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import sys
import unicodedata
from pathlib import Path
from typing import Any, Final

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
ARTIFACT_RELATIVE: Final = "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json"
DEFAULT_ARTIFACT: Final = REPORT / ARTIFACT_RELATIVE
POLICY_V3_RELATIVE: Final = (
    "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/"
    "continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate.json"
)
MEMBER_V4_RELATIVE: Final = "artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json"
REGISTRY_V4_RELATIVE: Final = (
    "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json"
)

POLICY_V3_SHA256: Final = "e0b3a649b45494881a534ecd84fe6f98f73012f0e5e6d7ca14b90fddffbccac8"
MEMBER_V4_SHA256: Final = "b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5"
MEMBER_V4_IDENTITY_SHA256: Final = (
    "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
)
REGISTRY_V4_SHA256: Final = "e403a9576abb08d3ada884cd283cce29ce8f877b0e9843cc8d5b911c8c0b0ac5"

POLICY_V3_SCHEMA: Final = "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v3_candidate"
POLICY_V3_STATUS: Final = (
    "RESULT_BLIND_POLICY_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_"
    "CURRENT_ENCLOSURES_PERMANENTLY_INELIGIBLE"
)
MEMBER_V4_SCHEMA: Final = "encounter_continuum_c1_c2_n0_member_spec_v4_candidate"
MEMBER_V4_STATUS: Final = (
    "STRUCTURAL_PARTITION_IDENTITY_V4_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
)
REGISTRY_V4_SCHEMA: Final = "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate"
REGISTRY_V4_STATUS: Final = (
    "RESULT_BLIND_CANDIDATE_NATIVE_METHOD_PARAMETERS_ONLY_NOT_EXTERNALLY_COMMITTED"
)
SCHEMA: Final = "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate"
STATUS: Final = (
    "RESULT_BLIND_SUCCESSOR_POLICY_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_"
    "CURRENT_AND_PROTOTYPE_ENCLOSURES_PERMANENTLY_INELIGIBLE"
)

CLAIM_KEYS: Final = {
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
V3_REQUIREMENTS: Final = {
    "all_box_mass_and_gauge_denominator_lowers_strictly_positive": True,
    "all_common_flux_forward_reverse_intersections_nonempty": True,
    "all_formula_values_contained_by_saved_raw_intervals": True,
    "all_map_ratio_interval_lowers_strictly_positive": True,
    "every_configuration_and_axis_present_exactly_once": True,
    "maximum_gauge_relative_width": "1/1099511627776",
    "maximum_map_anchor_constant": "1000000/1",
    "maximum_reconstructed_killing_anchor_constant": "1000000/1",
    "maximum_reference_cell_mass_relative_width": "1/1099511627776",
    "maximum_stationary_axis_relative_width": "1/1099511627776",
    "minimum_configuration_count": 12,
}
V3_JOIN_REQUIREMENTS: Final = {
    "axis_order_exact": [
        "midpoint",
        "relative_parallel",
        "relative_perpendicular",
    ],
    "axis_partition_path_sha_cell_count_equal": True,
    "cell_and_edge_native_record_keys_unique": True,
    "configuration_count_exactly_12": True,
    "configuration_index_and_label_unique": True,
    "killing_member_partition_formula_method_unit_binding_equal": True,
    "profile_index_order_exact": [0, 1, 2, 3],
    "raw_stationary_member_partition_formula_method_unit_binding_equal": True,
}
V3_THRESHOLD_LINEAGE: Final = {
    "all_exact_thresholds_equal_to_legacy_policy": True,
    "post_enclosure_adaptation_allowed": False,
    "threshold_loosening_detected": False,
}
V3_ORDERING: Final = {
    "current_enclosure_sources_eligible_for_acceptance": False,
    "external_predecessor_commitment_present": False,
    "future_replay_must_pin_exact_member_registry_policy_hashes": True,
    "future_replay_required": True,
    "policy_predecessor_order_independently_sealed": False,
    "retroactive_acceptance_authorized": False,
    "roles_8_10_outputs_read_while_constructing_this_policy": False,
    "timestamp_ordering_is_sufficient": False,
}
V3_SOURCE_PINS: Final = {
    "legacy_policy": {
        "path": "artifacts/data/continuum_c1_c2_fixed_row_anti_vacuity_policy_v1.json",
        "sha256": "c8b9f3aca2b3a516935eeb1fdfb2bf542ba0da2d12ae4c11581f6f1ee607f628",
    },
    "member_spec_v3_candidate": {
        "path": (
            "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/"
            "continuum_c1_c2_n0_member_spec_v3_candidate.json"
        ),
        "sha256": "b5eea6553d329bcbc4a1eb301dd3d5fb5b5acd387b80bfee5094286d3ca8ab71",
    },
    "outward_method_registry_v2_candidate": {
        "path": (
            "artifacts/data/continuum_c1_c2_n0_predecessor_authority_candidate_v1/"
            "continuum_c1_c2_n0_outward_method_registry_v2_candidate.json"
        ),
        "sha256": "2a455a3bb4808fb722a83b815a7c8cf8995669360394ee6f8adc73c87cc280fb",
    },
    "round176_policy_candidate": {
        "path": "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v2.json",
        "sha256": "7e36369a9a1e22aa9c2c256ff8eaa4a0c8bf973316e2b6265247c8beff4ddb13",
    },
}
V3_KEYS: Final = {
    "claim_boundary",
    "join_requirements",
    "ordering",
    "requirements",
    "schema",
    "source_pins",
    "status",
    "threshold_lineage",
}

MEMBER_KEYS: Final = {
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
MEMBER_ROLE_KEYS: Final = {
    "configuration_source",
    "factorization_source",
    "ideal_formula_source",
    "reference_density_source",
}
MEMBER_COUNTS: Final = {
    "axis_cell_count": 5_037,
    "axis_count": 36,
    "axis_edge_count": 5_013,
    "configuration_count": 12,
    "periodic_seam_count": 12,
    "profile_index_count": 48,
    "total_virtual_tensor_state_count": 34_787_462,
}
AXIS_ORDER: Final = (
    "midpoint",
    "relative_parallel",
    "relative_perpendicular",
)
REGISTRY_KEYS: Final = {
    "claim_boundary",
    "parameter_count",
    "parameters",
    "schema",
    "status",
}
REGISTRY_PARAMETER_ORDER: Final = (
    "stationary_directed_mpfr_320_v2",
    "stationary_directed_mpfr_640_sentinel_v2",
    "raw_flux_directed_mpfr_320_v2",
    "raw_flux_directed_mpfr_640_sentinel_v2",
    "raw_flux_binary64_decode_v2",
    "exact_fraction_expression_dag_v2",
    "killing_contact_profile_mpfr_192_v3",
    "killing_analytic_disk_area_mpfr_256_v3",
    "killing_source_independent_same_backend_verifier_v3",
    "killing_exact_contact_cell_classification_v3",
)
METHOD_DIGEST_DOMAIN: Final = b"encounter-outward-method-parameters-v4"

EXPECTED_ORDERING: Final = {
    "current_enclosure_sources_eligible_for_acceptance": False,
    "external_predecessor_commitment_present": False,
    "future_fresh_roles_8_10_replay_required": True,
    "future_replay_must_pin_exact_member_registry_policy_hashes": True,
    "future_replay_must_pin_exact_member_registry_policy_replay_plan_hashes": True,
    "future_replay_required": True,
    "policy_predecessor_order_independently_sealed": False,
    "prototype_enclosure_sources_eligible_for_acceptance": False,
    "result_blind_replay_plan_required": True,
    "retroactive_acceptance_authorized": False,
    "roles_8_9_10_may_execute_in_parallel_after_commitment": True,
    "roles_8_10_outputs_read_while_constructing_this_policy": False,
    "timestamp_ordering_is_sufficient": False,
}
EXPECTED_COUNTS: Final = {
    "future_fresh_replay_role_count": 3,
    "future_fresh_replay_role_catalog_order": [8, 9, 10],
    "future_fresh_replay_role_catalog_order_implies_dependency_edges": False,
    "member_axis_partition_count": 36,
    "member_configuration_count": 12,
    "member_n0_sequence_count": 12,
    "member_profile_index_count": 48,
    "member_source_role_count": 4,
    "registry_parameter_count": 10,
}
ARTIFACT_KEYS: Final = {
    "claim_boundary",
    "join_requirements",
    "ordering",
    "requirements",
    "schema",
    "source_pins",
    "status",
    "successor_binding_counts",
    "threshold_lineage",
}
EXPECTED_SOURCE_PINS: Final = {
    "member_spec_v4_candidate": {
        "member_identity_sha256": MEMBER_V4_IDENTITY_SHA256,
        "path": MEMBER_V4_RELATIVE,
        "schema": MEMBER_V4_SCHEMA,
        "sha256": MEMBER_V4_SHA256,
    },
    "method_parameter_registry_v4_candidate": {
        "path": REGISTRY_V4_RELATIVE,
        "schema": REGISTRY_V4_SCHEMA,
        "sha256": REGISTRY_V4_SHA256,
    },
    "policy_v3_lineage": {
        "path": POLICY_V3_RELATIVE,
        "schema": POLICY_V3_SCHEMA,
        "sha256": POLICY_V3_SHA256,
    },
}

MAX_JSON_BYTES: Final = 4 * 1024 * 1024
MAX_JSON_DEPTH: Final = 64
MAX_JSON_NODES: Final = 200_000
MAX_STRING_CHARACTERS: Final = 2 * 1024 * 1024
MAX_SINGLE_STRING_CHARACTERS: Final = 1 * 1024 * 1024
MAX_INTEGER_DIGITS: Final = 256


class PolicyValidationError(ValueError):
    """A byte, schema, lineage, result-blindness, or count invariant failed."""


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    node_count = 0
    character_count = 0

    def inspect(node: Any, depth: int) -> None:
        nonlocal node_count, character_count
        node_count += 1
        if node_count > MAX_JSON_NODES:
            raise PolicyValidationError("JSON node cap exceeded")
        if depth > MAX_JSON_DEPTH:
            raise PolicyValidationError("JSON depth cap exceeded")
        if type(node) in (bool, int) or node is None:
            return
        if isinstance(node, float):
            raise PolicyValidationError("floating JSON value forbidden")
        if type(node) is str:
            if unicodedata.normalize("NFC", node) != node:
                raise PolicyValidationError("non-NFC JSON string")
            if len(node) > MAX_SINGLE_STRING_CHARACTERS:
                raise PolicyValidationError("single JSON string cap exceeded")
            character_count += len(node)
            if character_count > MAX_STRING_CHARACTERS:
                raise PolicyValidationError("aggregate JSON string cap exceeded")
            return
        if type(node) is list:
            for child in node:
                inspect(child, depth + 1)
            return
        if type(node) is dict:
            for key, child in node.items():
                if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                    raise PolicyValidationError("invalid JSON key")
                character_count += len(key)
                if character_count > MAX_STRING_CHARACTERS:
                    raise PolicyValidationError("aggregate JSON string cap exceeded")
                inspect(child, depth + 1)
            return
        raise PolicyValidationError(f"forbidden JSON type: {type(node).__name__}")

    inspect(value, 0)
    payload = (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode(
        "ascii"
    )
    if len(payload) > MAX_JSON_BYTES:
        raise PolicyValidationError("canonical JSON byte cap exceeded")
    return payload


def decode_canonical(payload: bytes) -> dict[str, Any]:
    if not payload or len(payload) > MAX_JSON_BYTES:
        raise PolicyValidationError("JSON byte cap violation")

    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        output: dict[str, Any] = {}
        for key, item in pairs:
            if type(key) is not str or key in output:
                raise PolicyValidationError("duplicate or invalid JSON key")
            output[key] = item
        return output

    def bounded_integer(token: str) -> int:
        unsigned = token[1:] if token.startswith("-") else token
        if len(unsigned) > MAX_INTEGER_DIGITS:
            raise PolicyValidationError("JSON integer digit cap exceeded")
        return int(token)

    def no_non_integer(token: str) -> Any:
        raise PolicyValidationError(f"non-integer JSON number forbidden: {token}")

    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=no_duplicates,
            parse_int=bounded_integer,
            parse_float=no_non_integer,
            parse_constant=no_non_integer,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        OverflowError,
        RecursionError,
    ) as error:
        raise PolicyValidationError("strict JSON decoding failed") from error
    if type(value) is not dict or canonical_bytes(value) != payload:
        raise PolicyValidationError("canonical JSON byte drift")
    return value


def open_parent_anchored(path: Path) -> tuple[int, str]:
    if not path.is_absolute() or path != Path(os.path.abspath(path)) or len(path.parts) < 2:
        raise PolicyValidationError("canonical absolute path required")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(path.anchor, flags)
    try:
        for component in path.parts[1:-1]:
            if component in {"", ".", ".."}:
                raise PolicyValidationError("unsafe path component")
            successor = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = successor
        leaf = path.parts[-1]
        if leaf in {"", ".", ".."}:
            raise PolicyValidationError("unsafe path leaf")
        return descriptor, leaf
    except BaseException:
        os.close(descriptor)
        raise


def _same_directory(descriptor: int, identity: tuple[int, int]) -> bool:
    try:
        observed = os.fstat(descriptor)
    except BaseException:
        return False
    return stat.S_ISDIR(observed.st_mode) and (observed.st_dev, observed.st_ino) == identity


def read_immutable(
    path: Path,
    expected_sha256: str | None = None,
    cap: int = MAX_JSON_BYTES,
) -> bytes:
    parent, leaf = open_parent_anchored(path)
    parent_metadata = os.fstat(parent)
    parent_identity = parent_metadata.st_dev, parent_metadata.st_ino
    descriptor = -1
    try:
        descriptor = os.open(
            leaf,
            os.O_RDONLY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0),
            dir_fd=parent,
        )
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.getuid()
            or stat.S_IMODE(before.st_mode) != 0o444
            or before.st_nlink != 1
            or before.st_size <= 0
            or before.st_size > cap
        ):
            raise PolicyValidationError(
                "current-user-owned 0444 single-link regular input required"
            )
        blocks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, remaining)
            if not block:
                raise PolicyValidationError("short immutable input read")
            blocks.append(block)
            remaining -= len(block)
        if os.read(descriptor, 1):
            raise PolicyValidationError("immutable input grew during read")
        after = os.fstat(descriptor)
        linked = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        compared = (
            "st_dev",
            "st_ino",
            "st_mode",
            "st_uid",
            "st_nlink",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        if any(getattr(before, key) != getattr(after, key) for key in compared):
            raise PolicyValidationError("immutable input descriptor changed during read")
        if (linked.st_dev, linked.st_ino) != (before.st_dev, before.st_ino):
            raise PolicyValidationError("immutable input path changed during read")
        live_parent, _ = open_parent_anchored(path)
        try:
            if not _same_directory(parent, parent_identity) or not _same_directory(
                live_parent,
                parent_identity,
            ):
                raise PolicyValidationError("directory chain changed")
        finally:
            os.close(live_parent)
        payload = b"".join(blocks)
        if expected_sha256 is not None and digest(payload) != expected_sha256:
            raise PolicyValidationError("immutable input SHA-256 mismatch")
        return payload
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent)


def require_false_claims(value: Any, label: str) -> None:
    if type(value) is not dict or set(value) != CLAIM_KEYS:
        raise PolicyValidationError(f"{label} claim-key set drift")
    for key, item in value.items():
        if type(item) is not bool or item is not False:
            raise PolicyValidationError(f"{label} promoted or aliased claim: {key}")


def audit_v3(value: dict[str, Any]) -> None:
    if set(value) != V3_KEYS:
        raise PolicyValidationError("v3 policy top-level drift")
    if value["schema"] != POLICY_V3_SCHEMA or value["status"] != POLICY_V3_STATUS:
        raise PolicyValidationError("v3 policy schema/status drift")
    require_false_claims(value["claim_boundary"], "v3 policy")
    exact_sections = (
        ("requirements", V3_REQUIREMENTS),
        ("join_requirements", V3_JOIN_REQUIREMENTS),
        ("threshold_lineage", V3_THRESHOLD_LINEAGE),
        ("ordering", V3_ORDERING),
        ("source_pins", V3_SOURCE_PINS),
    )
    for key, expected in exact_sections:
        if value[key] != expected:
            raise PolicyValidationError(f"v3 policy {key} drift")
    if type(value["requirements"]["minimum_configuration_count"]) is not int:
        raise PolicyValidationError("v3 policy minimum-count alias")
    if any(
        type(item) is not int for item in value["join_requirements"]["profile_index_order_exact"]
    ):
        raise PolicyValidationError("v3 policy profile-order alias")


def audit_member(value: dict[str, Any]) -> None:
    if set(value) != MEMBER_KEYS:
        raise PolicyValidationError("member-v4 top-level drift")
    if value["schema"] != MEMBER_V4_SCHEMA or value["status"] != MEMBER_V4_STATUS:
        raise PolicyValidationError("member-v4 schema/status drift")
    if value["member_identity_sha256"] != MEMBER_V4_IDENTITY_SHA256:
        raise PolicyValidationError("member-v4 identity drift")
    require_false_claims(value["claim_boundary"], "member-v4")
    counts = value["reconstruction_counts"]
    if (
        type(counts) is not dict
        or counts != MEMBER_COUNTS
        or any(type(count) is not int for count in counts.values())
    ):
        raise PolicyValidationError("member-v4 declared-count drift")
    if type(value["role_bindings"]) is not dict or set(value["role_bindings"]) != MEMBER_ROLE_KEYS:
        raise PolicyValidationError("member-v4 source-role count drift")
    for record in value["role_bindings"].values():
        if (
            type(record) is not dict
            or set(record) != {"path", "sha256"}
            or type(record["path"]) is not str
            or type(record["sha256"]) is not str
            or len(record["sha256"]) != 64
        ):
            raise PolicyValidationError("member-v4 source-role binding drift")

    order = value["configuration_order"]
    semantics = value["configuration_semantic_ids"]
    sequences = value["n0_sequence_bindings"]
    if (
        type(order) is not list
        or len(order) != 12
        or len(set(order)) != 12
        or type(semantics) is not list
        or len(semantics) != 12
        or type(sequences) is not list
        or len(sequences) != 12
    ):
        raise PolicyValidationError("member-v4 configuration cardinality drift")

    seen_paths: set[str] = set()
    cells = 0
    edges = 0
    seams = 0
    states = 0
    for index, row in enumerate(sequences):
        if (
            type(row) is not dict
            or type(row.get("configuration_index")) is not int
            or row["configuration_index"] != index
            or row.get("authority_label") != order[index]
        ):
            raise PolicyValidationError("member-v4 row order/index drift")
        shape = row.get("n0_anchor_shape")
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(length) is not int or length <= 0 for length in shape)
        ):
            raise PolicyValidationError("member-v4 shape drift")
        row_states = shape[0] * shape[1] * shape[2]
        if (
            type(row.get("n0_anchor_expected_states")) is not int
            or row["n0_anchor_expected_states"] != row_states
        ):
            raise PolicyValidationError("member-v4 state-count drift")
        states += row_states
        axes = row.get("n0_axes")
        if type(axes) is not list or len(axes) != 3:
            raise PolicyValidationError("member-v4 row axis count drift")
        if tuple(axis.get("coordinate") for axis in axes) != AXIS_ORDER:
            raise PolicyValidationError("member-v4 coordinate order drift")
        if [axis.get("cell_count") for axis in axes] != shape:
            raise PolicyValidationError("member-v4 cell/shape join drift")
        for axis in axes:
            count = axis.get("cell_count")
            periodic = axis.get("periodic")
            path = axis.get("partition_report_relative_path")
            hash_value = axis.get("partition_sha256")
            if (
                type(count) is not int
                or count <= 0
                or type(periodic) is not bool
                or type(path) is not str
                or type(hash_value) is not str
                or len(hash_value) != 64
                or path in seen_paths
            ):
                raise PolicyValidationError("member-v4 partition record drift")
            seen_paths.add(path)
            cells += count
            edges += count if periodic else count - 1
            seams += int(periodic)
    observed = {
        "axis_cell_count": cells,
        "axis_count": len(seen_paths),
        "axis_edge_count": edges,
        "configuration_count": len(sequences),
        "periodic_seam_count": seams,
        "profile_index_count": counts["profile_index_count"],
        "total_virtual_tensor_state_count": states,
    }
    if observed != MEMBER_COUNTS:
        raise PolicyValidationError("member-v4 independently reconstructed counts drift")
    properties = value["identity_properties"]
    if (
        type(properties) is not dict
        or type(properties.get("partition_file_count")) is not int
        or properties["partition_file_count"] != 36
        or properties.get("source_roles_1_through_4_only_in_production_role_bindings") is not True
    ):
        raise PolicyValidationError("member-v4 identity-property drift")


def audit_registry(value: dict[str, Any]) -> None:
    if set(value) != REGISTRY_KEYS:
        raise PolicyValidationError("registry-v4 top-level drift")
    if value["schema"] != REGISTRY_V4_SCHEMA or value["status"] != REGISTRY_V4_STATUS:
        raise PolicyValidationError("registry-v4 schema/status drift")
    require_false_claims(value["claim_boundary"], "registry-v4")
    if type(value["parameter_count"]) is not int or value["parameter_count"] != 10:
        raise PolicyValidationError("registry-v4 parameter count drift")
    parameters = value["parameters"]
    if type(parameters) is not list or len(parameters) != 10:
        raise PolicyValidationError("registry-v4 parameter list drift")
    identifiers: list[str] = []
    roles: set[str] = set()
    for record in parameters:
        if type(record) is not dict or set(record) != {
            "method_parameter_sha256",
            "parameter_id",
            "parameters",
        }:
            raise PolicyValidationError("registry-v4 record shape drift")
        identifier = record["parameter_id"]
        parameter_map = record["parameters"]
        if type(identifier) is not str or type(parameter_map) is not dict:
            raise PolicyValidationError("registry-v4 record type drift")
        identifiers.append(identifier)
        expected = digest(METHOD_DIGEST_DOMAIN + b"\0" + canonical_bytes(parameter_map))
        if record["method_parameter_sha256"] != expected:
            raise PolicyValidationError("registry-v4 method digest drift")
        scope = parameter_map.get("source_role_scope")
        if type(scope) is not list or not scope or any(type(role) is not str for role in scope):
            raise PolicyValidationError("registry-v4 role-scope drift")
        roles.update(scope)
    if tuple(identifiers) != REGISTRY_PARAMETER_ORDER or len(set(identifiers)) != 10:
        raise PolicyValidationError("registry-v4 identifier order/uniqueness drift")
    if roles != {
        "role8_raw_axis_formula_primitive",
        "role9_stationary_physical_integral",
        "role10_killing_factor_geometry",
        "same_member_mass_flux_composition",
        "symbolic_killing_composition",
    }:
        raise PolicyValidationError("registry-v4 exact role inventory drift")


def expected_document() -> dict[str, Any]:
    return {
        "claim_boundary": {key: False for key in CLAIM_KEYS},
        "join_requirements": copy.deepcopy(V3_JOIN_REQUIREMENTS),
        "ordering": copy.deepcopy(EXPECTED_ORDERING),
        "requirements": copy.deepcopy(V3_REQUIREMENTS),
        "schema": SCHEMA,
        "source_pins": copy.deepcopy(EXPECTED_SOURCE_PINS),
        "status": STATUS,
        "successor_binding_counts": copy.deepcopy(EXPECTED_COUNTS),
        "threshold_lineage": copy.deepcopy(V3_THRESHOLD_LINEAGE),
    }


def audit_candidate(value: dict[str, Any]) -> None:
    if set(value) != ARTIFACT_KEYS:
        raise PolicyValidationError("policy-v4 top-level drift or output/result injection")
    if value["schema"] != SCHEMA or value["status"] != STATUS:
        raise PolicyValidationError("policy-v4 schema/status drift")
    require_false_claims(value["claim_boundary"], "policy-v4")
    if value != expected_document():
        raise PolicyValidationError("policy-v4 semantic reconstruction mismatch")
    counts = value["successor_binding_counts"]
    integer_count_keys = {
        "future_fresh_replay_role_count",
        "member_axis_partition_count",
        "member_configuration_count",
        "member_n0_sequence_count",
        "member_profile_index_count",
        "member_source_role_count",
        "registry_parameter_count",
    }
    if any(type(counts[key]) is not int for key in integer_count_keys) or any(
        type(role) is not int for role in counts["future_fresh_replay_role_catalog_order"]
    ):
        raise PolicyValidationError("policy-v4 Boolean/integer alias")
    if (
        value["ordering"]["current_enclosure_sources_eligible_for_acceptance"] is not False
        or value["ordering"]["prototype_enclosure_sources_eligible_for_acceptance"] is not False
        or value["ordering"]["external_predecessor_commitment_present"] is not False
        or value["ordering"]["future_fresh_roles_8_10_replay_required"] is not True
        or value["ordering"][
            "future_replay_must_pin_exact_member_registry_policy_replay_plan_hashes"
        ]
        is not True
        or value["ordering"]["result_blind_replay_plan_required"] is not True
        or value["ordering"]["policy_predecessor_order_independently_sealed"] is not False
        or value["ordering"]["roles_8_10_outputs_read_while_constructing_this_policy"] is not False
        or value["ordering"]["retroactive_acceptance_authorized"] is not False
        or value["ordering"]["roles_8_9_10_may_execute_in_parallel_after_commitment"] is not True
        or value["ordering"]["timestamp_ordering_is_sufficient"] is not False
        or counts["future_fresh_replay_role_catalog_order_implies_dependency_edges"] is not False
    ):
        raise PolicyValidationError("policy-v4 result-blind ordering boundary drift")


def validate_paths(report: Path, artifact: Path) -> tuple[bytes, dict[str, Any]]:
    report = Path(os.path.abspath(os.fspath(report)))
    artifact = Path(os.path.abspath(os.fspath(artifact)))
    v3_bytes = read_immutable(report / POLICY_V3_RELATIVE, POLICY_V3_SHA256)
    member_bytes = read_immutable(report / MEMBER_V4_RELATIVE, MEMBER_V4_SHA256)
    registry_bytes = read_immutable(report / REGISTRY_V4_RELATIVE, REGISTRY_V4_SHA256)
    artifact_bytes = read_immutable(artifact)
    v3 = decode_canonical(v3_bytes)
    member = decode_canonical(member_bytes)
    registry = decode_canonical(registry_bytes)
    candidate = decode_canonical(artifact_bytes)
    audit_v3(v3)
    audit_member(member)
    audit_registry(registry)
    audit_candidate(candidate)
    if candidate["source_pins"] != {
        "member_spec_v4_candidate": {
            "member_identity_sha256": MEMBER_V4_IDENTITY_SHA256,
            "path": MEMBER_V4_RELATIVE,
            "schema": MEMBER_V4_SCHEMA,
            "sha256": digest(member_bytes),
        },
        "method_parameter_registry_v4_candidate": {
            "path": REGISTRY_V4_RELATIVE,
            "schema": REGISTRY_V4_SCHEMA,
            "sha256": digest(registry_bytes),
        },
        "policy_v3_lineage": {
            "path": POLICY_V3_RELATIVE,
            "schema": POLICY_V3_SCHEMA,
            "sha256": digest(v3_bytes),
        },
    }:
        raise PolicyValidationError("policy-v4 live source-pin mismatch")

    # Verify that the three normative paths and the candidate remain on the
    # same expected bytes after the independent semantic reconstruction.
    if (
        read_immutable(report / POLICY_V3_RELATIVE, POLICY_V3_SHA256) != v3_bytes
        or read_immutable(report / MEMBER_V4_RELATIVE, MEMBER_V4_SHA256) != member_bytes
        or read_immutable(report / REGISTRY_V4_RELATIVE, REGISTRY_V4_SHA256) != registry_bytes
        or read_immutable(artifact, digest(artifact_bytes), len(artifact_bytes)) != artifact_bytes
    ):
        raise PolicyValidationError("input or candidate changed during validation")
    return artifact_bytes, candidate


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", type=Path, default=REPORT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        artifact_bytes, candidate = validate_paths(
            arguments.report_root.expanduser(),
            arguments.artifact.expanduser(),
        )
        print(
            "PASS_ANTI_VACUITY_POLICY_V4_CANDIDATE_VALIDATION "
            f"sha256={digest(artifact_bytes)} claims={len(candidate['claim_boundary'])} "
            "configurations=12 partitions=36 replay_roles=3 parameters=10"
        )
        return 0
    except (OSError, PolicyValidationError) as error:
        print(f"ERROR AntiVacuityPolicyV4CandidateValidation: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
