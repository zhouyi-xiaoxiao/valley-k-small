#!/usr/bin/env python3
"""Build the result-blind successor anti-vacuity policy v4 candidate.

Only three immutable, outcome-free inputs are opened: the v3 policy lineage,
the successor structural member v4, and the successor method-parameter
registry v4.  No role-8--10 output, result, receipt, or enclosure is opened.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import stat
import sys
import threading
import unicodedata
from pathlib import Path
from typing import Any, Final

_STAGE_OPEN: Final = os.open
_STAGE_FSTAT: Final = os.fstat

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
OUTPUT_RELATIVE: Final = "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json"
DEFAULT_OUTPUT: Final = REPORT / OUTPUT_RELATIVE

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
EXPECTED_CLAIMS: Final = {key: False for key in CLAIM_KEYS}

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
V3_TOP_LEVEL_KEYS: Final = {
    "claim_boundary",
    "join_requirements",
    "ordering",
    "requirements",
    "schema",
    "source_pins",
    "status",
    "threshold_lineage",
}

MEMBER_TOP_LEVEL_KEYS: Final = {
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

REGISTRY_TOP_LEVEL_KEYS: Final = {
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
REGISTRY_DIGEST_DOMAIN: Final = b"encounter-outward-method-parameters-v4"

ORDERING: Final = {
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
SUCCESSOR_BINDING_COUNTS: Final = {
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
TOP_LEVEL_KEYS: Final = {
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

MAX_JSON_BYTES: Final = 4 * 1024 * 1024
MAX_JSON_DEPTH: Final = 64
MAX_JSON_NODES: Final = 200_000
MAX_STRING_CHARACTERS: Final = 2 * 1024 * 1024
MAX_SINGLE_STRING_CHARACTERS: Final = 1 * 1024 * 1024
MAX_INTEGER_DIGITS: Final = 256


class PolicyBuildError(RuntimeError):
    """An input, semantic, or publication invariant failed."""


class StageCreationTransaction:
    """Retain a staging descriptor even across asynchronous interruption."""

    def __init__(self, parent_descriptor: int, leaf: str) -> None:
        self.parent_descriptor = parent_descriptor
        self.leaf = leaf
        self.descriptor: int | None = None
        self.identity: tuple[int, int] | None = None
        self.error: BaseException | None = None
        self._ready = threading.Event()
        self._thread = threading.Thread(
            target=self._create,
            name="anti-vacuity-policy-v4-stage-create",
        )

    def _create(self) -> None:
        try:
            descriptor = _STAGE_OPEN(
                self.leaf,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                0o400,
                dir_fd=self.parent_descriptor,
            )
            self.descriptor = descriptor
            opened = _STAGE_FSTAT(descriptor)
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_uid != os.getuid()
                or stat.S_IMODE(opened.st_mode) != 0o400
                or opened.st_nlink != 1
                or opened.st_size != 0
            ):
                raise PolicyBuildError("new 0400 staging inode invariant failure")
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
            raise PolicyBuildError("stage transaction lost authoritative state")

    def settle(self) -> None:
        while self._thread.is_alive():
            try:
                self._thread.join()
            except BaseException:
                continue

    def release_descriptor(self, descriptor: int) -> None:
        if self.descriptor != descriptor:
            raise PolicyBuildError("stage descriptor transfer mismatch")
        self.descriptor = None


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _check_json_tree(value: Any) -> None:
    nodes = 0
    characters = 0

    def visit(node: Any, depth: int) -> None:
        nonlocal nodes, characters
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise PolicyBuildError("JSON node cap exceeded")
        if depth > MAX_JSON_DEPTH:
            raise PolicyBuildError("JSON depth cap exceeded")
        if type(node) in (bool, int) or node is None:
            return
        if isinstance(node, float):
            raise PolicyBuildError("floating JSON value forbidden")
        if type(node) is str:
            if unicodedata.normalize("NFC", node) != node:
                raise PolicyBuildError("non-NFC JSON string")
            if len(node) > MAX_SINGLE_STRING_CHARACTERS:
                raise PolicyBuildError("single JSON string cap exceeded")
            characters += len(node)
            if characters > MAX_STRING_CHARACTERS:
                raise PolicyBuildError("aggregate JSON string cap exceeded")
            return
        if type(node) is list:
            for item in node:
                visit(item, depth + 1)
            return
        if type(node) is dict:
            for key, item in node.items():
                if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                    raise PolicyBuildError("invalid JSON object key")
                characters += len(key)
                if characters > MAX_STRING_CHARACTERS:
                    raise PolicyBuildError("aggregate JSON string cap exceeded")
                visit(item, depth + 1)
            return
        raise PolicyBuildError(f"forbidden JSON type: {type(node).__name__}")

    visit(value, 0)


def canonical_bytes(value: Any) -> bytes:
    _check_json_tree(value)
    payload = (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode(
        "ascii"
    )
    if len(payload) > MAX_JSON_BYTES:
        raise PolicyBuildError("canonical JSON byte cap exceeded")
    return payload


def decode_canonical(payload: bytes) -> dict[str, Any]:
    if not payload or len(payload) > MAX_JSON_BYTES:
        raise PolicyBuildError("JSON byte cap violation")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if type(key) is not str or key in result:
                raise PolicyBuildError("duplicate or invalid JSON key")
            result[key] = item
        return result

    def strict_integer(token: str) -> int:
        digits = token[1:] if token.startswith("-") else token
        if len(digits) > MAX_INTEGER_DIGITS:
            raise PolicyBuildError("JSON integer digit cap exceeded")
        return int(token)

    def reject_number(token: str) -> Any:
        raise PolicyBuildError(f"non-integer JSON number forbidden: {token}")

    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=unique_object,
            parse_int=strict_integer,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        OverflowError,
        RecursionError,
    ) as error:
        raise PolicyBuildError("strict JSON decoding failed") from error
    if type(value) is not dict or canonical_bytes(value) != payload:
        raise PolicyBuildError("canonical JSON byte drift")
    return value


def open_parent_anchored(path: Path) -> tuple[int, str]:
    if not path.is_absolute() or path != Path(os.path.abspath(path)) or len(path.parts) < 2:
        raise PolicyBuildError("canonical absolute path required")
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
                raise PolicyBuildError("unsafe path component")
            following = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
        leaf = path.parts[-1]
        if leaf in {"", ".", ".."}:
            raise PolicyBuildError("unsafe path leaf")
        return descriptor, leaf
    except BaseException:
        os.close(descriptor)
        raise


def _descriptor_matches(descriptor: int, identity: tuple[int, int]) -> bool:
    try:
        observed = os.fstat(descriptor)
    except BaseException:
        return False
    return stat.S_ISDIR(observed.st_mode) and (observed.st_dev, observed.st_ino) == identity


def _verify_live_parent(
    path: Path,
    anchored_descriptor: int,
    identity: tuple[int, int],
) -> None:
    verification, _ = open_parent_anchored(path)
    try:
        if not _descriptor_matches(
            anchored_descriptor,
            identity,
        ) or not _descriptor_matches(verification, identity):
            raise PolicyBuildError("directory chain changed")
    finally:
        os.close(verification)


def read_immutable(
    path: Path,
    expected_sha256: str | None = None,
    cap: int = MAX_JSON_BYTES,
) -> bytes:
    """Read a current-user-owned 0444 single-link regular file stably."""

    parent, leaf = open_parent_anchored(path)
    parent_stat = os.fstat(parent)
    parent_identity = parent_stat.st_dev, parent_stat.st_ino
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
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_uid != os.getuid()
            or stat.S_IMODE(opened.st_mode) != 0o444
            or opened.st_nlink != 1
            or opened.st_size <= 0
            or opened.st_size > cap
        ):
            raise PolicyBuildError("current-user-owned 0444 single-link regular input required")
        payload = bytearray()
        while len(payload) < opened.st_size:
            block = os.read(descriptor, opened.st_size - len(payload))
            if not block:
                raise PolicyBuildError("short immutable input read")
            payload.extend(block)
        if os.read(descriptor, 1):
            raise PolicyBuildError("immutable input grew during read")
        after = os.fstat(descriptor)
        linked = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        stable_fields = (
            "st_dev",
            "st_ino",
            "st_mode",
            "st_uid",
            "st_nlink",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        if any(getattr(opened, key) != getattr(after, key) for key in stable_fields):
            raise PolicyBuildError("immutable input descriptor changed during read")
        if (linked.st_dev, linked.st_ino) != (opened.st_dev, opened.st_ino):
            raise PolicyBuildError("immutable input path changed during read")
        _verify_live_parent(path, parent, parent_identity)
        result = bytes(payload)
        if expected_sha256 is not None and sha256(result) != expected_sha256:
            raise PolicyBuildError("immutable input SHA-256 mismatch")
        return result
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent)


def _exact_false_claims(value: Any, label: str) -> None:
    if type(value) is not dict or set(value) != set(CLAIM_KEYS):
        raise PolicyBuildError(f"{label} claim-key set drift")
    if any(type(value[key]) is not bool or value[key] is not False for key in CLAIM_KEYS):
        raise PolicyBuildError(f"{label} contains a promoted or non-Boolean claim")


def validate_policy_v3(value: dict[str, Any]) -> None:
    if set(value) != V3_TOP_LEVEL_KEYS:
        raise PolicyBuildError("v3 policy top-level key drift")
    if value["schema"] != POLICY_V3_SCHEMA or value["status"] != POLICY_V3_STATUS:
        raise PolicyBuildError("v3 policy schema/status drift")
    _exact_false_claims(value["claim_boundary"], "v3 policy")
    if value["requirements"] != V3_REQUIREMENTS:
        raise PolicyBuildError("v3 policy requirement drift")
    if value["join_requirements"] != V3_JOIN_REQUIREMENTS:
        raise PolicyBuildError("v3 policy join-requirement drift")
    if value["threshold_lineage"] != V3_THRESHOLD_LINEAGE:
        raise PolicyBuildError("v3 policy threshold-lineage drift")
    if value["ordering"] != V3_ORDERING:
        raise PolicyBuildError("v3 policy ordering drift")
    if value["source_pins"] != V3_SOURCE_PINS:
        raise PolicyBuildError("v3 policy copied lineage drift")
    if type(value["requirements"]["minimum_configuration_count"]) is not int:
        raise PolicyBuildError("v3 minimum count Boolean/integer alias")
    if any(
        type(item) is not int for item in value["join_requirements"]["profile_index_order_exact"]
    ):
        raise PolicyBuildError("v3 profile index Boolean/integer alias")


def validate_member_v4(value: dict[str, Any]) -> None:
    if set(value) != MEMBER_TOP_LEVEL_KEYS:
        raise PolicyBuildError("member-v4 top-level key drift")
    if value["schema"] != MEMBER_V4_SCHEMA or value["status"] != MEMBER_V4_STATUS:
        raise PolicyBuildError("member-v4 schema/status drift")
    if value["member_identity_sha256"] != MEMBER_V4_IDENTITY_SHA256:
        raise PolicyBuildError("member-v4 identity drift")
    _exact_false_claims(value["claim_boundary"], "member-v4")
    counts = value["reconstruction_counts"]
    if (
        type(counts) is not dict
        or counts != MEMBER_COUNTS
        or any(type(item) is not int for item in counts.values())
    ):
        raise PolicyBuildError("member-v4 reconstruction-count drift")
    roles = value["role_bindings"]
    if type(roles) is not dict or set(roles) != MEMBER_ROLE_KEYS:
        raise PolicyBuildError("member-v4 source-role count drift")
    for role in MEMBER_ROLE_KEYS:
        record = roles[role]
        if (
            type(record) is not dict
            or set(record) != {"path", "sha256"}
            or type(record["path"]) is not str
            or type(record["sha256"]) is not str
            or len(record["sha256"]) != 64
        ):
            raise PolicyBuildError("member-v4 source-role record drift")

    configuration_order = value["configuration_order"]
    semantic_ids = value["configuration_semantic_ids"]
    sequences = value["n0_sequence_bindings"]
    if (
        type(configuration_order) is not list
        or len(configuration_order) != 12
        or len(set(configuration_order)) != 12
        or type(semantic_ids) is not list
        or len(semantic_ids) != 12
        or type(sequences) is not list
        or len(sequences) != 12
    ):
        raise PolicyBuildError("member-v4 configuration/sequence count drift")

    partition_paths: set[str] = set()
    axis_cell_count = 0
    axis_edge_count = 0
    periodic_seam_count = 0
    virtual_states = 0
    for expected_index, sequence in enumerate(sequences):
        if type(sequence) is not dict:
            raise PolicyBuildError("member-v4 sequence record type drift")
        if (
            type(sequence.get("configuration_index")) is not int
            or sequence["configuration_index"] != expected_index
            or sequence.get("authority_label") != configuration_order[expected_index]
        ):
            raise PolicyBuildError("member-v4 configuration index/order drift")
        shape = sequence.get("n0_anchor_shape")
        if (
            type(shape) is not list
            or len(shape) != 3
            or any(type(item) is not int or item <= 0 for item in shape)
        ):
            raise PolicyBuildError("member-v4 n0 shape drift")
        expected_states = shape[0] * shape[1] * shape[2]
        if (
            type(sequence.get("n0_anchor_expected_states")) is not int
            or sequence["n0_anchor_expected_states"] != expected_states
        ):
            raise PolicyBuildError("member-v4 tensor-state reconstruction drift")
        virtual_states += expected_states
        axes = sequence.get("n0_axes")
        if type(axes) is not list or len(axes) != 3:
            raise PolicyBuildError("member-v4 per-sequence axis count drift")
        if tuple(axis.get("coordinate") for axis in axes) != AXIS_ORDER:
            raise PolicyBuildError("member-v4 axis ordering drift")
        if [axis.get("cell_count") for axis in axes] != shape:
            raise PolicyBuildError("member-v4 axis-cell/shape join drift")
        for axis in axes:
            cell_count = axis.get("cell_count")
            periodic = axis.get("periodic")
            path = axis.get("partition_report_relative_path")
            digest = axis.get("partition_sha256")
            if (
                type(cell_count) is not int
                or cell_count <= 0
                or type(periodic) is not bool
                or type(path) is not str
                or type(digest) is not str
                or len(digest) != 64
                or path in partition_paths
            ):
                raise PolicyBuildError("member-v4 partition binding drift")
            partition_paths.add(path)
            axis_cell_count += cell_count
            axis_edge_count += cell_count if periodic else cell_count - 1
            periodic_seam_count += int(periodic)

    if (
        len(partition_paths) != 36
        or axis_cell_count != MEMBER_COUNTS["axis_cell_count"]
        or axis_edge_count != MEMBER_COUNTS["axis_edge_count"]
        or periodic_seam_count != MEMBER_COUNTS["periodic_seam_count"]
        or virtual_states != MEMBER_COUNTS["total_virtual_tensor_state_count"]
    ):
        raise PolicyBuildError("member-v4 reconstructed partition counts drift")
    properties = value["identity_properties"]
    if (
        type(properties) is not dict
        or properties.get("partition_file_count") != 36
        or type(properties.get("partition_file_count")) is not int
        or properties.get("source_roles_1_through_4_only_in_production_role_bindings") is not True
    ):
        raise PolicyBuildError("member-v4 identity properties drift")


def validate_registry_v4(value: dict[str, Any]) -> None:
    if set(value) != REGISTRY_TOP_LEVEL_KEYS:
        raise PolicyBuildError("registry-v4 top-level key drift")
    if value["schema"] != REGISTRY_V4_SCHEMA or value["status"] != REGISTRY_V4_STATUS:
        raise PolicyBuildError("registry-v4 schema/status drift")
    _exact_false_claims(value["claim_boundary"], "registry-v4")
    if type(value["parameter_count"]) is not int or value["parameter_count"] != 10:
        raise PolicyBuildError("registry-v4 parameter count drift")
    parameters = value["parameters"]
    if type(parameters) is not list or len(parameters) != 10:
        raise PolicyBuildError("registry-v4 parameter list drift")
    if tuple(item.get("parameter_id") for item in parameters) != REGISTRY_PARAMETER_ORDER:
        raise PolicyBuildError("registry-v4 parameter ordering drift")
    for item in parameters:
        if type(item) is not dict or set(item) != {
            "method_parameter_sha256",
            "parameter_id",
            "parameters",
        }:
            raise PolicyBuildError("registry-v4 parameter record shape drift")
        if type(item["parameter_id"]) is not str or type(item["parameters"]) is not dict:
            raise PolicyBuildError("registry-v4 parameter record type drift")
        expected_digest = sha256(
            REGISTRY_DIGEST_DOMAIN + b"\0" + canonical_bytes(item["parameters"])
        )
        if item["method_parameter_sha256"] != expected_digest:
            raise PolicyBuildError("registry-v4 semantic digest drift")
        scope = item["parameters"].get("source_role_scope")
        if type(scope) is not list or not scope or any(type(role) is not str for role in scope):
            raise PolicyBuildError("registry-v4 source-role scope drift")


def _read_normative_inputs(
    report: Path,
) -> tuple[
    bytes,
    dict[str, Any],
    bytes,
    dict[str, Any],
    bytes,
    dict[str, Any],
]:
    report = Path(os.path.abspath(os.fspath(report)))
    policy_bytes = read_immutable(report / POLICY_V3_RELATIVE, POLICY_V3_SHA256)
    member_bytes = read_immutable(report / MEMBER_V4_RELATIVE, MEMBER_V4_SHA256)
    registry_bytes = read_immutable(report / REGISTRY_V4_RELATIVE, REGISTRY_V4_SHA256)
    policy = decode_canonical(policy_bytes)
    member = decode_canonical(member_bytes)
    registry = decode_canonical(registry_bytes)
    validate_policy_v3(policy)
    validate_member_v4(member)
    validate_registry_v4(registry)
    return policy_bytes, policy, member_bytes, member, registry_bytes, registry


def normative_policy(report: Path = REPORT) -> dict[str, Any]:
    (
        policy_bytes,
        policy,
        member_bytes,
        member,
        registry_bytes,
        registry,
    ) = _read_normative_inputs(report)
    result = {
        "claim_boundary": dict(EXPECTED_CLAIMS),
        "join_requirements": policy["join_requirements"],
        "ordering": dict(ORDERING),
        "requirements": policy["requirements"],
        "schema": SCHEMA,
        "source_pins": {
            "member_spec_v4_candidate": {
                "member_identity_sha256": MEMBER_V4_IDENTITY_SHA256,
                "path": MEMBER_V4_RELATIVE,
                "schema": MEMBER_V4_SCHEMA,
                "sha256": sha256(member_bytes),
            },
            "method_parameter_registry_v4_candidate": {
                "path": REGISTRY_V4_RELATIVE,
                "schema": REGISTRY_V4_SCHEMA,
                "sha256": sha256(registry_bytes),
            },
            "policy_v3_lineage": {
                "path": POLICY_V3_RELATIVE,
                "schema": POLICY_V3_SCHEMA,
                "sha256": sha256(policy_bytes),
            },
        },
        "status": STATUS,
        "successor_binding_counts": dict(SUCCESSOR_BINDING_COUNTS),
        "threshold_lineage": policy["threshold_lineage"],
    }
    if set(result) != TOP_LEVEL_KEYS:
        raise PolicyBuildError("internal v4 policy top-level drift")
    _exact_false_claims(result["claim_boundary"], "v4 policy")
    if member["member_identity_sha256"] != MEMBER_V4_IDENTITY_SHA256:
        raise PolicyBuildError("member identity changed after validation")
    if registry["parameter_count"] != SUCCESSOR_BINDING_COUNTS["registry_parameter_count"]:
        raise PolicyBuildError("registry count changed after validation")

    # Re-open only the same three outcome-free inputs.  This catches a path
    # replacement between semantic reconstruction and candidate publication.
    second = _read_normative_inputs(report)
    if second[0] != policy_bytes or second[2] != member_bytes or second[4] != registry_bytes:
        raise PolicyBuildError("normative input changed across reconstruction")
    return result


def _unlink_owned(parent: int, leaf: str, identity: tuple[int, int]) -> bool:
    try:
        current = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if (current.st_dev, current.st_ino) != identity:
        return False
    os.unlink(leaf, dir_fd=parent)
    return True


def _close_safely(descriptor: int) -> None:
    if descriptor < 0:
        return
    try:
        os.close(descriptor)
    except BaseException:
        pass


def publish_no_replace(path: Path, payload: bytes) -> None:
    """Publish a 0444 single-link inode without replacing an existing leaf."""

    parent, leaf = open_parent_anchored(path)
    parent_stat = os.fstat(parent)
    parent_identity = parent_stat.st_dev, parent_stat.st_ino
    stage_leaf = f".{leaf}.{secrets.token_hex(16)}.stage"
    descriptor = -1
    recovery_parent = -1
    stage_identity: tuple[int, int] | None = None
    transaction: StageCreationTransaction | None = None
    final_attempted = False
    try:
        transaction = StageCreationTransaction(parent, stage_leaf)
        transaction.start()
        transaction.await_ready()
        descriptor = -1 if transaction.descriptor is None else transaction.descriptor
        stage_identity = transaction.identity
        if descriptor < 0 or stage_identity is None:
            raise PolicyBuildError("staging transaction result missing")
        transaction.release_descriptor(descriptor)
        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0 or count > len(payload) - written:
                raise PolicyBuildError("short staged write")
            written += count
        os.fchmod(descriptor, 0o444)
        os.fsync(descriptor)
        staged = os.fstat(descriptor)
        if (
            (staged.st_dev, staged.st_ino) != stage_identity
            or staged.st_uid != os.getuid()
            or stat.S_IMODE(staged.st_mode) != 0o444
            or staged.st_nlink != 1
            or staged.st_size != len(payload)
        ):
            raise PolicyBuildError("staged policy identity/mode/size drift")
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
            raise PolicyBuildError(f"refusing to replace existing output: {path}") from error
        if not _unlink_owned(parent, stage_leaf, stage_identity):
            raise PolicyBuildError("staging identity changed before cleanup")
        os.fsync(parent)
        final = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (final.st_dev, final.st_ino) != stage_identity
            or final.st_uid != os.getuid()
            or stat.S_IMODE(final.st_mode) != 0o444
            or final.st_nlink != 1
            or final.st_size != len(payload)
        ):
            raise PolicyBuildError("published policy identity/mode/size drift")
        if read_immutable(path, sha256(payload), len(payload)) != payload:
            raise PolicyBuildError("published policy byte acknowledgement drift")
        _verify_live_parent(path, parent, parent_identity)
        os.close(parent)
        parent = -1
    except BaseException:
        if transaction is not None:
            transaction.settle()
            if stage_identity is None:
                stage_identity = transaction.identity
            if transaction.descriptor is not None:
                if descriptor < 0:
                    descriptor = transaction.descriptor
                elif descriptor != transaction.descriptor:
                    _close_safely(transaction.descriptor)
                transaction.descriptor = None
        if descriptor >= 0 and stage_identity is None:
            try:
                opened = _STAGE_FSTAT(descriptor)
                stage_identity = opened.st_dev, opened.st_ino
            except BaseException:
                pass
        _close_safely(descriptor)
        descriptor = -1

        cleanup_parent = -1
        if _descriptor_matches(parent, parent_identity):
            cleanup_parent = parent
        else:
            try:
                recovered, recovered_leaf = open_parent_anchored(path)
                if recovered_leaf == leaf and _descriptor_matches(
                    recovered,
                    parent_identity,
                ):
                    recovery_parent = recovered
                    cleanup_parent = recovered
                else:
                    _close_safely(recovered)
            except BaseException:
                pass
        if cleanup_parent >= 0 and stage_identity is not None:
            if final_attempted:
                try:
                    _unlink_owned(cleanup_parent, leaf, stage_identity)
                except BaseException:
                    pass
            try:
                _unlink_owned(cleanup_parent, stage_leaf, stage_identity)
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
                _close_safely(transaction.descriptor)
                transaction.descriptor = None
        _close_safely(descriptor)
        _close_safely(recovery_parent)
        _close_safely(parent)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", type=Path, default=REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        report = Path(os.path.abspath(os.fspath(arguments.report_root.expanduser())))
        output = Path(os.path.abspath(os.fspath(arguments.output.expanduser())))
        payload = canonical_bytes(normative_policy(report))
        if arguments.check:
            if read_immutable(output, sha256(payload), len(payload)) != payload:
                raise PolicyBuildError("anti-vacuity policy v4 candidate byte drift")
            print(
                "PASS_ANTI_VACUITY_POLICY_V4_CANDIDATE_CHECK "
                f"sha256={sha256(payload)} claims={len(CLAIM_KEYS)} "
                "configurations=12 partitions=36 replay_roles=3"
            )
            return 0
        publish_no_replace(output, payload)
        print(
            "PASS_ANTI_VACUITY_POLICY_V4_CANDIDATE_BUILD "
            f"path={output} sha256={sha256(payload)} claims={len(CLAIM_KEYS)} "
            "configurations=12 partitions=36 replay_roles=3"
        )
        return 0
    except (OSError, PolicyBuildError) as error:
        print(f"ERROR AntiVacuityPolicyV4CandidateBuild: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
