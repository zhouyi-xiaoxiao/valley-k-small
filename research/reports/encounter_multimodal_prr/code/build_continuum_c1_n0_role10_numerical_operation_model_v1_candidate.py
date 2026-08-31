#!/usr/bin/env python3
"""Build the result-blind role-10 numerical operation-model authority.

This file freezes only a future numerical operation contract.  It neither
implements nor executes the role-10 geometry calculation and it cannot create
an external predecessor commitment or promote a scientific claim.
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
from typing import Any, Final, Sequence

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
DEFAULT_OUTPUT: Final = (
    REPORT / "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v1_candidate.json"
)

SCHEMA: Final = "encounter_continuum_c1_n0_role10_numerical_operation_model_v1_candidate"
STATUS: Final = "RESULT_BLIND_CONTRACT_ONLY_CANDIDATE_NO_NUMERICAL_IMPLEMENTATION_OR_EXECUTION"
SOURCE_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_source_v3"
ROW_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_row_v1"
RAW_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_raw_interval_file_v1"
SEMANTIC_RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_semantic_receipt_v1"
OUTER_RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_validation_receipt_v2"
METHOD_DIGEST_DOMAIN: Final = "encounter-outward-method-parameters-v4"
_STAGE_OPEN: Final = os.open
_STAGE_FSTAT: Final = os.fstat

MEMBER_IDENTITY_SHA256: Final = "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
CONFIGURATION_INVENTORY_SHA256: Final = (
    "8da99e7910cac1f2ba6b69fb2d0ec52b21412abfa1d59c898462e138d82ebbb2"
)
PARTITION_INVENTORY_SHA256: Final = (
    "f3507f4eec07e216bd54bcf4486ab5cef1589511367f781174b89fdfe2e7b51f"
)

AUTHORITY_SPECS: Final = {
    "anti_vacuity_policy": (
        "artifacts/data/continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate.json",
        "encounter_continuum_c1_c2_n0_anti_vacuity_policy_v4_candidate",
        "599252aa1a9fd1d65d9ff3d0faa1e21bb2609da96cca6b6fff1e61a89ebff196",
    ),
    "configuration": (
        "artifacts/data/physical_configuration_family_control_free_v1.json",
        "encounter_physical_configuration_family_control_free_v1",
        "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084",
    ),
    "factorization": (
        "artifacts/data/continuum_c1_factorization_source_v2_candidate.json",
        "encounter_continuum_c1_factorization_source_v2_candidate",
        "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26",
    ),
    "ideal_formula": (
        "artifacts/data/continuum_c1_ideal_formula_source_v1.json",
        "encounter_continuum_c1_ideal_formula_source_v1",
        "f31b637b659483102d787da7263cd45c72829b3fce3df2ff9100066dec94c2be",
    ),
    "initial_geometry": (
        "artifacts/data/physical_initial_analytic_source_v1.json",
        "encounter_physical_initial_analytic_source_v1",
        "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f",
    ),
    "initial_partition_bundle": (
        "artifacts/data/physical_production_initial_stream_v1/bundle.json",
        "encounter_control_free_production_initial_stream_v1",
        "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e",
    ),
    "killing_geometry": (
        "artifacts/data/physical_killing_geometry_source_v1.json",
        "encounter_physical_killing_geometry_source_v1",
        "5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669",
    ),
    "member_spec": (
        "artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json",
        "encounter_continuum_c1_c2_n0_member_spec_v4_candidate",
        "b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5",
    ),
    "method_parameter_registry": (
        "artifacts/data/continuum_c1_c2_n0_method_parameter_registry_v4_candidate.json",
        "encounter_continuum_c1_c2_n0_method_parameter_registry_v4_candidate",
        "e403a9576abb08d3ada884cd283cce29ce8f877b0e9843cc8d5b911c8c0b0ac5",
    ),
    "sealed_authentication_mirror": (
        (
            "artifacts/data/"
            "continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate/"
            "manifest.json"
        ),
        "encounter_continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate",
        "1ba1b582c17e90ab19f04f1aefce1ea5cf9a9dad8cbcfcaed309314014d8dc51",
    ),
    "reference_density": (
        "artifacts/data/continuum_c1_reference_density_source_v1.json",
        "encounter_continuum_c1_reference_density_source_v1",
        "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575",
    ),
}

METHOD_IDS: Final = (
    "killing_contact_profile_mpfr_192_v3",
    "killing_analytic_disk_area_mpfr_256_v3",
    "killing_source_independent_same_backend_verifier_v3",
    "killing_exact_contact_cell_classification_v3",
)
METHOD_DIGESTS: Final = (
    "b48ff460eb56ab91f27b26104b69874f0e0169e658ea69c71c2a6dd6f1fd30df",
    "0ade3fb790db8845715652762776073a1c2db6570bc562fec7b46a6a66c41057",
    "40907be35641ad4cfc2d64b9479d45df572adcd4ee2f7e9afdf39340ebe6b421",
    "ca866475725fe801833f8f2ec9702fe825010a69a59712c4d87f1584048fe631",
)

EXPECTED_ROWS: Final = (
    ("O113/Base", "finite_mesh_anchor_family", "o113_base", 113, 113, 113),
    ("E128/Base", "finite_mesh_anchor_family", "e128_base", 128, 128, 128),
    ("O129/Base", "finite_mesh_anchor_family", "o129_base", 129, 129, 129),
    ("O161/Base", "finite_mesh_anchor_family", "o161_base", 161, 161, 161),
    ("M+", "finite_box_challenge_family", "m_plus", 166, 129, 129),
    ("R+", "finite_box_challenge_family", "r_plus", 129, 172, 129),
    ("MR+", "finite_box_challenge_family", "mr_plus", 166, 172, 129),
    ("MR+F", "finite_box_challenge_family", "mr_plus_fine", 207, 215, 161),
    ("A_M", "finite_alignment_challenge_family", "a_midpoint", 129, 128, 128),
    (
        "A_R",
        "finite_alignment_challenge_family",
        "a_relative_parallel",
        128,
        129,
        128,
    ),
    (
        "A_Y",
        "finite_alignment_challenge_family",
        "a_relative_perpendicular",
        128,
        128,
        128,
    ),
    ("A_MRY", "finite_alignment_challenge_family", "a_all_axes", 129, 129, 128),
)

CLAIM_KEYS: Final = (
    "B06_cleared",
    "B06_structural_remedy_prepared",
    "backend_independence_claimed",
    "complete_C1",
    "external_predecessor_commitment_present",
    "numerical_execution_performed",
    "numerical_implementation_present",
    "ordered_roles_8_10_replay_executed",
    "production_same_member_bridge_accepted",
    "release_eligible",
    "role10_numerical_source_materialized",
    "same_member_acceptance",
    "science_executed",
    "submission_eligible",
)


class OperationModelBuildError(RuntimeError):
    """An authority, model reconstruction, or publication invariant failed."""


class StageCreationTransaction:
    """Capture the staging inode even when asynchronous interruption lands."""

    def __init__(self, parent_descriptor: int, leaf: str) -> None:
        self.parent_descriptor = parent_descriptor
        self.leaf = leaf
        self.descriptor: int | None = None
        self.identity: tuple[int, int] | None = None
        self.error: BaseException | None = None
        self._ready = threading.Event()
        self._thread = threading.Thread(
            target=self._create,
            name="role10-operation-model-stage-create",
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
                0o600,
                dir_fd=self.parent_descriptor,
            )
            self.descriptor = descriptor
            opened = _STAGE_FSTAT(descriptor)
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_nlink != 1
                or opened.st_size != 0
                or opened.st_uid != os.geteuid()
                or stat.S_IMODE(opened.st_mode) != 0o600
            ):
                raise OperationModelBuildError("new staging inode invariant failure")
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
            raise OperationModelBuildError("stage transaction lost authoritative state")

    def settle(self) -> None:
        while self._thread.is_alive():
            try:
                self._thread.join()
            except BaseException:
                continue

    def release_descriptor(self, descriptor: int) -> None:
        if self.descriptor != descriptor:
            raise OperationModelBuildError("stage descriptor transfer mismatch")
        self.descriptor = None


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > 64:
        raise OperationModelBuildError("JSON depth cap exceeded")
    if isinstance(value, float):
        raise OperationModelBuildError("floating JSON literal forbidden")
    if type(value) in (bool, int) or value is None:
        if type(value) is int and value.bit_length() > 65_536:
            raise OperationModelBuildError("JSON integer cap exceeded")
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise OperationModelBuildError("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise OperationModelBuildError("invalid JSON key")
            _strict_tree(item, depth + 1)
        return
    raise OperationModelBuildError(f"forbidden JSON type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    _strict_tree(value)
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise OperationModelBuildError("duplicate or invalid JSON key")
        result[key] = value
    return result


def parse_canonical_json(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                OperationModelBuildError(f"{label}: float {token} forbidden")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                OperationModelBuildError(f"{label}: constant {token} forbidden")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OperationModelBuildError(f"{label}: invalid ASCII JSON") from error
    if type(value) is not dict or canonical_bytes(value) != payload:
        raise OperationModelBuildError(f"{label}: noncanonical JSON")
    return value


def parse_authority_json(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                OperationModelBuildError(f"{label}: float {token} forbidden")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                OperationModelBuildError(f"{label}: constant {token} forbidden")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OperationModelBuildError(f"{label}: invalid ASCII JSON") from error
    if type(value) is not dict:
        raise OperationModelBuildError(f"{label}: JSON object required")
    _strict_tree(value)
    return value


def _canonical_absolute(path: Path) -> Path:
    expanded = path.expanduser()
    absolute = Path(os.path.abspath(os.fspath(expanded)))
    if not absolute.is_absolute() or absolute != Path(os.path.abspath(absolute)):
        raise OperationModelBuildError("canonical absolute path required")
    return absolute


def open_parent_anchored(path: Path) -> tuple[int, str]:
    path = _canonical_absolute(path)
    if len(path.parts) < 2:
        raise OperationModelBuildError("path requires parent and leaf")
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
                raise OperationModelBuildError("unsafe path component")
            following = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
        leaf = path.parts[-1]
        if leaf in {"", ".", ".."}:
            raise OperationModelBuildError("unsafe path leaf")
        return descriptor, leaf
    except BaseException:
        os.close(descriptor)
        raise


def _parent_matches(descriptor: int, identity: tuple[int, int]) -> bool:
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


def _verify_live_parent(path: Path, anchored: int, identity: tuple[int, int]) -> None:
    verification, _ = open_parent_anchored(path)
    try:
        if not _parent_matches(anchored, identity) or not _parent_matches(
            verification,
            identity,
        ):
            raise OperationModelBuildError("directory chain changed")
    finally:
        os.close(verification)


def read_regular(
    path: Path,
    *,
    cap: int,
    required_mode: int | None,
) -> bytes:
    path = _canonical_absolute(path)
    parent, leaf = open_parent_anchored(path)
    opened_parent = os.fstat(parent)
    parent_identity = opened_parent.st_dev, opened_parent.st_ino
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
            or opened.st_nlink != 1
            or opened.st_size <= 0
            or opened.st_size > cap
            or (required_mode is not None and stat.S_IMODE(opened.st_mode) != required_mode)
        ):
            raise OperationModelBuildError("bounded single-link regular file required")
        payload = bytearray()
        while len(payload) < opened.st_size:
            block = os.read(descriptor, opened.st_size - len(payload))
            if not block:
                raise OperationModelBuildError("short stable read")
            payload.extend(block)
        if os.read(descriptor, 1):
            raise OperationModelBuildError("file grew during stable read")
        after = os.fstat(descriptor)
        linked = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        opened_identity = (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
            opened.st_ctime_ns,
        )
        after_identity = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if after_identity != opened_identity or (linked.st_dev, linked.st_ino) != (
            opened.st_dev,
            opened.st_ino,
        ):
            raise OperationModelBuildError("file changed during stable read")
        _verify_live_parent(path, parent, parent_identity)
        return bytes(payload)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent)


def _read_authority(name: str) -> tuple[dict[str, Any], bytes]:
    relative, schema, expected_sha = AUTHORITY_SPECS[name]
    path = REPORT / relative
    payload = read_regular(path, cap=8_000_000, required_mode=None)
    if sha256(payload) != expected_sha:
        raise OperationModelBuildError(f"{name}: authority identity mismatch")
    value = parse_authority_json(payload, name)
    if value.get("schema") != schema:
        raise OperationModelBuildError(f"{name}: authority schema mismatch")
    return value, payload


def _method_digest(parameters: dict[str, Any]) -> str:
    return sha256(METHOD_DIGEST_DOMAIN.encode("ascii") + b"\0" + canonical_bytes(parameters))


def _selected_methods(registry: dict[str, Any]) -> list[dict[str, Any]]:
    if set(registry) != {"claim_boundary", "parameter_count", "parameters", "schema", "status"}:
        raise OperationModelBuildError("registry top-level key drift")
    records = registry["parameters"]
    if type(records) is not list or len(records) != 10 or registry["parameter_count"] != 10:
        raise OperationModelBuildError("registry cardinality drift")
    by_id = {
        record.get("parameter_id"): record
        for record in records
        if type(record) is dict and type(record.get("parameter_id")) is str
    }
    selected: list[dict[str, Any]] = []
    for identifier, expected_digest in zip(METHOD_IDS, METHOD_DIGESTS, strict=True):
        record = by_id.get(identifier)
        if (
            type(record) is not dict
            or set(record) != {"method_parameter_sha256", "parameter_id", "parameters"}
            or record["method_parameter_sha256"] != expected_digest
            or _method_digest(record["parameters"]) != expected_digest
            or record["parameters"].get("source_role_scope") != ["role10_killing_factor_geometry"]
        ):
            raise OperationModelBuildError(f"method record drift: {identifier}")
        selected.append(record)
    return selected


def _row_contracts(member: dict[str, Any]) -> list[dict[str, Any]]:
    bindings = member.get("n0_sequence_bindings")
    semantic_ids = member.get("configuration_semantic_ids")
    if type(bindings) is not list or type(semantic_ids) is not list:
        raise OperationModelBuildError("member row inventories missing")
    if len(bindings) != 12 or len(semantic_ids) != 12:
        raise OperationModelBuildError("member row cardinality drift")
    rows: list[dict[str, Any]] = []
    for index, expected in enumerate(EXPECTED_ROWS):
        label, family, member_id, n_m, n_r, n_y = expected
        binding = bindings[index]
        semantic_id = semantic_ids[index]
        if (
            binding.get("configuration_index") != index
            or binding.get("authority_label") != label
            or binding.get("n0_anchor_shape") != [n_m, n_r, n_y]
            or semantic_id
            != {
                "authority_label": label,
                "refinement_family_id": family,
                "refinement_member_id": member_id,
            }
        ):
            raise OperationModelBuildError(f"member row drift at {index}")
        row_dir = f"rows/row_{index:02d}"
        contact_count = n_r * n_y
        profile_file_records = n_m
        profiles = [
            {
                "byte_length": profile_file_records * 16,
                "flat_index": "m",
                "logical_shape": [n_m],
                "path": f"{row_dir}/profile_{profile_index:02d}.intervals.be64",
                "profile_index": profile_index,
                "record_count": profile_file_records,
                "units": "inverse_length",
            }
            for profile_index in range(4)
        ]
        rows.append(
            {
                "configuration_index": index,
                "configuration_semantic_id": semantic_id,
                "contact": {
                    "byte_length": contact_count * 16,
                    "flat_index": "a*n_Y+b",
                    "logical_shape": [n_r, n_y],
                    "path": f"{row_dir}/contact.intervals.be64",
                    "record_count": contact_count,
                    "units": "dimensionless",
                },
                "future_V_metadata_only": {
                    "flat_index": "(m*n_R+a)*n_Y+b",
                    "logical_shape": [n_m, n_r, n_y],
                    "materialization": "forbidden",
                },
                "profile_order": [0, 1, 2, 3],
                "profiles": profiles,
                "row_directory": row_dir,
                "row_manifest_path": f"{row_dir}/row.json",
                "row_schema": ROW_SCHEMA,
                "shape_order": ["n_M", "n_R", "n_Y"],
                "state_shape": [n_m, n_r, n_y],
                "virtual_state_count": n_m * n_r * n_y,
            }
        )
    return rows


def _file_paths(rows: list[dict[str, Any]]) -> list[str]:
    paths = ["manifest.json"]
    for row in rows:
        paths.extend(
            [
                row["row_manifest_path"],
                row["contact"]["path"],
                *(profile["path"] for profile in row["profiles"]),
            ]
        )
    return paths


def _validate_sealed_mirror(mirror: dict[str, Any], manifest_raw: bytes) -> dict[str, Any]:
    expected_keys = {
        "accepted_authorities",
        "claim_boundary",
        "coverage",
        "entries",
        "entry_count",
        "exclusions",
        "inventory_digests",
        "mirrored_source_pin",
        "schema",
        "status",
    }
    expected_coverage = {
        "configuration_authority_lineage_file_count": 3,
        "configuration_initial_geometry_file_count": 1,
        "exact_writable_precommit_input_closure_mirrored": True,
        "member_v4_partition_file_count": 36,
        "original_report_relative_suffix_preserved_under_files": True,
        "standalone_content_addressed_validation_without_original_writable_sources": True,
    }
    expected_exclusions = {
        "external_commitment_not_created": True,
        "legacy_role10_result_and_output_bytes_excluded": True,
        "numerical_execution_results_excluded": True,
        "replay_requests_plans_bundles_and_commitments_excluded": True,
        "role8_and_role9_outputs_excluded": True,
    }
    if (
        set(mirror) != expected_keys
        or mirror["coverage"] != expected_coverage
        or mirror["exclusions"] != expected_exclusions
        or mirror["entry_count"] != 40
        or mirror["inventory_digests"].get("configuration_row_inventory", {}).get("sha256")
        != CONFIGURATION_INVENTORY_SHA256
        or mirror["inventory_digests"].get("member_v4_partition_inventory", {}).get("sha256")
        != PARTITION_INVENTORY_SHA256
    ):
        raise OperationModelBuildError("sealed authentication mirror coverage drift")
    entries = mirror["entries"]
    if type(entries) is not list or len(entries) != 40:
        raise OperationModelBuildError("sealed authentication mirror entry drift")
    mirror_manifest_relative = AUTHORITY_SPECS["sealed_authentication_mirror"][0]
    mirror_root = (REPORT / mirror_manifest_relative).parent
    file_paths = {"manifest.json"}
    directory_paths = {"."}
    total_bytes = len(manifest_raw)
    for ordinal, entry in enumerate(entries):
        if (
            type(entry) is not dict
            or entry.get("ordinal") != ordinal
            or type(entry.get("mirror_relative_path")) is not str
            or type(entry.get("byte_length")) is not int
            or type(entry.get("sha256")) is not str
        ):
            raise OperationModelBuildError(f"sealed mirror entry drift at {ordinal}")
        relative = Path(entry["mirror_relative_path"])
        if (
            relative.is_absolute()
            or not relative.parts
            or relative.parts[0] != "files"
            or any(part in {"", ".", ".."} for part in relative.parts)
            or relative.as_posix() != entry["mirror_relative_path"]
            or relative.as_posix() in file_paths
        ):
            raise OperationModelBuildError(f"unsafe sealed mirror path at {ordinal}")
        payload = read_regular(
            mirror_root / relative,
            cap=8_000_000,
            required_mode=0o444,
        )
        if len(payload) != entry["byte_length"] or sha256(payload) != entry["sha256"]:
            raise OperationModelBuildError(f"sealed mirror byte drift at {ordinal}")
        file_paths.add(relative.as_posix())
        parent = relative.parent
        while parent != Path("."):
            directory_paths.add(parent.as_posix())
            parent = parent.parent
        total_bytes += len(payload)
    if len(file_paths) != 41 or len(directory_paths) != 20 or total_bytes != 1_176_207:
        raise OperationModelBuildError("sealed mirror package topology drift")
    return {
        "directory_count": 20,
        "entry_count": 40,
        "file_count": 41,
        "future_execution_source": (
            "sealed_mirror_copies_only_original_paths_retained_as_semantic_lineage"
        ),
        "manifest_path": mirror_manifest_relative,
        "manifest_schema": AUTHORITY_SPECS["sealed_authentication_mirror"][1],
        "manifest_sha256": AUTHORITY_SPECS["sealed_authentication_mirror"][2],
        "total_bytes": 1_176_207,
        "validated_coverage": expected_coverage,
    }


def build_model() -> dict[str, Any]:
    authority_images = {name: _read_authority(name) for name in AUTHORITY_SPECS}
    authorities = {name: image[0] for name, image in authority_images.items()}
    member = authorities["member_spec"]
    registry = authorities["method_parameter_registry"]
    if member.get("member_identity_sha256") != MEMBER_IDENTITY_SHA256 or member.get(
        "configuration_order"
    ) != [row[0] for row in EXPECTED_ROWS]:
        raise OperationModelBuildError("member identity drift")
    rows = _row_contracts(member)
    file_paths = _file_paths(rows)
    directory_paths = [".", "rows", *(f"rows/row_{index:02d}" for index in range(12))]
    total_contact_records = sum(row["contact"]["record_count"] for row in rows)
    total_profile_records = sum(
        profile["record_count"] for row in rows for profile in row["profiles"]
    )
    if (
        len(file_paths) != 73
        or len(directory_paths) != 14
        or total_contact_records != 233_139
        or total_profile_records != 6_852
    ):
        raise OperationModelBuildError("package topology arithmetic drift")

    authority_bindings = {
        name: {"path": path, "schema": schema, "sha256": digest}
        for name, (path, schema, digest) in AUTHORITY_SPECS.items()
    }
    mirror_contract = _validate_sealed_mirror(
        authorities["sealed_authentication_mirror"],
        authority_images["sealed_authentication_mirror"][1],
    )
    false_claims = {key: False for key in CLAIM_KEYS}
    return {
        "artifact_contract": {
            "directory_paths": directory_paths,
            "encoding": {
                "byte_order": "big",
                "endpoint_semantics": "closed_outward_binary64",
                "record_byte_length": 16,
                "record_format": ">dd",
            },
            "file_paths": file_paths,
            "path_templates": {
                "contact": "rows/row_{configuration_index:02d}/contact.intervals.be64",
                "profile": (
                    "rows/row_{configuration_index:02d}/profile_{profile_index:02d}.intervals.be64"
                ),
                "row_directory": "rows/row_{configuration_index:02d}",
                "row_manifest": "rows/row_{configuration_index:02d}/row.json",
                "top_manifest": "manifest.json",
            },
            "schema_key_contracts": {
                "contact_section_exact_keys": [
                    "analytic_area_anchor_reference",
                    "flat_index",
                    "full_cell_count",
                    "logical_shape",
                    "partial_cell_count",
                    "quality_gate_ledger",
                    "raw_file",
                    "raw_manifest",
                    "record_count",
                    "units",
                    "weighted_area_enclosure_exact",
                    "zero_cell_count",
                ],
                "profile_section_exact_keys": [
                    "centre_exact",
                    "flat_index",
                    "half_width_exact",
                    "logical_shape",
                    "profile_index",
                    "quality_gate_ledger",
                    "raw_file",
                    "raw_manifest",
                    "record_count",
                    "units",
                    "weighted_unit_mass_enclosure_exact",
                ],
                "raw_manifest_exact_keys": [
                    "byte_length",
                    "byte_order",
                    "endpoint_semantics",
                    "flat_index",
                    "logical_role",
                    "logical_shape",
                    "normalization",
                    "path",
                    "record_count",
                    "record_format",
                    "schema",
                    "sha256",
                    "units",
                ],
                "row_manifest_exact_keys": [
                    "authority_bindings",
                    "claim_boundary",
                    "configuration_binding",
                    "contact",
                    "expected_states",
                    "layout_and_units",
                    "member_binding",
                    "partition_bindings",
                    "producer_closure_binding",
                    "profiles",
                    "request_binding",
                    "row_relation_sha256",
                    "schema",
                    "shape",
                    "status",
                ],
                "top_manifest_exact_keys": [
                    "authority_bindings",
                    "candidate_bundle_binding",
                    "claim_boundary",
                    "external_commitment_binding",
                    "family_relation_sha256",
                    "file_inventory",
                    "member_binding",
                    "method_selection",
                    "normalization_anchor",
                    "operation_model_binding",
                    "partition_reference_digest",
                    "producer_runtime_closure",
                    "representation_contract",
                    "replay_plan_binding",
                    "request_binding",
                    "rows",
                    "schema",
                    "sealed_authentication_mirror_binding",
                    "shared_precommit_context_sha256",
                    "status",
                    "totals",
                ],
            },
            "rows": rows,
            "schemas": {
                "raw_interval_file": RAW_SCHEMA,
                "row": ROW_SCHEMA,
                "source": SOURCE_SCHEMA,
            },
            "stored_precision_policy": {
                "analytic_disk_area_anchor": (
                    "one_global_256_bit_outward_interval_saved_at_"
                    "manifest.json#/normalization_anchor/"
                    "analytic_disk_area_enclosure_exact_256"
                ),
                "contact_and_profile_payloads": ("producer_192_bit_outward_intervals_only"),
                "verifier_384_512_oracle_values": (
                    "forbidden_from_artifact_payload_and_not_retained_as_scientific_values"
                ),
            },
            "totals": {
                "configuration_rows": 12,
                "contact_interval_bytes": 3_730_224,
                "contact_interval_records": 233_139,
                "directories": 14,
                "files": 73,
                "profile_files": 48,
                "profile_interval_bytes": 109_632,
                "profile_interval_records": 6_852,
                "raw_numerical_leaves": 60,
                "row_manifests": 12,
                "top_manifests": 1,
            },
            "top_file_inventory": {
                "entry_count": 72,
                "excludes_self_referential_top_manifest": "required",
                "ordered_paths": file_paths[1:],
            },
        },
        "authority_bindings": authority_bindings,
        "authority_model": {
            "authentication_closure_roles": [
                "anti_vacuity_policy",
                "configuration_design",
                "configuration_implementation",
                "configuration_initial_geometry",
                "configuration_test",
                "external_predecessor_commitment",
                "ideal_formula",
                "initial_partition_bundle",
                "killing_geometry",
                "member_spec",
                "method_parameter_registry",
                "partition_path_bindings",
                "producer_runtime_closure",
                "reference_density",
                "verifier_runtime_closure",
            ],
            "configuration_row_inventory_sha256": CONFIGURATION_INVENTORY_SHA256,
            "member_identity_sha256": MEMBER_IDENTITY_SHA256,
            "normative_direct_role_dependencies": [1, 3, 5, 6, 7],
            "partition_inventory_sha256": PARTITION_INVENTORY_SHA256,
            "sealed_authentication_mirror": mirror_contract,
            "separation_rule": (
                "authentication_closure_roles_authenticate_nested_lineage_or_execution_"
                "bytes_but_are_not_additional_mathematical_dependency_edges"
            ),
        },
        "claim_boundary": false_claims,
        "forbidden_surface": {
            "forbidden_legacy_import_prefixes": [
                "numpy",
                "rate_defined_tensor_f0",
                "scipy",
            ],
            "legacy_import_scope": (
                "forbidden_in_future_producer_verifier_shared_protocol_and_numerical_"
                "runtime_dependency_edges_but_allowed_as_sealed_configuration_lineage_"
                "evidence_in_the_authentication_mirror"
            ),
            "forbidden_legacy_result_basenames": [
                "continuum_c2_killing_geometry_production_binding_v1.json",
                "physical_production_killing_geometry_two_repeat_outer_receipt_v1.json",
                "physical_production_killing_geometry_v1",
            ],
            "forbidden_precommit_or_artifact_fields": [
                "acceptance_bit",
                "artifact_sha256",
                "budget",
                "concrete_V",
                "control_weights",
                "discrete_diagonal_k",
                "independent_trust_domain_receipt_hash",
                "observed_output_digest",
                "observed_result",
                "reconstructed_K",
                "result_summary",
                "role10_result_digest",
                "tree_digest",
            ],
            "forbidden_scientific_payloads": [
                "384_bit_oracle_interval_values",
                "512_bit_sentinel_interval_values",
                "dense_V",
                "dense_k",
                "dense_K",
                "pi_h",
                "role8_result",
                "role9_result",
            ],
            "legacy_result_bytes_read": "forbidden",
            "future_code_hashes": (
                "required_in_runtime_closure_before_commitment_but_not_yet_"
                "available_in_this_contract"
            ),
            "unknown_future_output_or_result_hash_pins": "forbidden",
        },
        "invocation_contract": {
            "child_semantic_verifier_argv": [
                "{python_executable}",
                "-I",
                "-B",
                "{verifier_entrypoint}",
                "--semantic-child",
                "--request",
                "{request}",
                "--output",
                "{artifact}",
                "--semantic-receipt",
                "{temporary_semantic_receipt}",
            ],
            "outer_verifier_argv": [
                "{python_executable}",
                "-I",
                "-B",
                "{verifier_entrypoint}",
                "--request",
                "{request}",
                "--output",
                "{artifact}",
                "--semantic-receipt",
                "{semantic_receipt}",
                "--receipt",
                "{outer_receipt}",
            ],
            "process_isolation_and_cleanup": {
                "ack_protocol": (
                    "one_bounded_canonical_ack_per_child_after_semantic_receipt_fsync"
                ),
                "child_environment": (
                    "fixed_allowlist_no_PYTHONPATH_no_python_startup_no_user_site_"
                    "locale_C_utf8_hash_seed_zero"
                ),
                "child_process_group": "one_new_process_group_per_clean_child",
                "cleanup": (
                    "on_timeout_error_or_interrupt_terminate_process_group_then_kill_"
                    "after_bounded_grace_and_reap_before_owned_temporary_cleanup"
                ),
                "observation_bytes_maximum": 65_536,
                "semantic_deadline_seconds": 1_140,
                "stderr_bytes_maximum": 4_096,
                "stdout_ack_bytes_maximum": 4_096,
                "wall_deadline_seconds": 1_200,
            },
            "producer_argv": [
                "{python_executable}",
                "-I",
                "-B",
                "{producer_entrypoint}",
                "--request",
                "{request}",
                "--output",
                "{artifact}",
            ],
            "runtime_closure_rule": (
                "future_entrypoints_and_all_transitive_runtime_bytes_are_bound_only_in_"
                "a_later_result_blind_replay_plan_before_external_commitment"
            ),
            "shared_module_boundary": {
                "allowed_shared_surface": (
                    "one_separately_pinned_protocol_only_module_with_no_geometry_"
                    "partition_interval_package_or_receipt_semantics"
                ),
                "numerical_source_sets": "producer_and_verifier_disjoint",
                "shared_unpinned_module": "forbidden",
            },
        },
        "method_contract": {
            "digest_domain": METHOD_DIGEST_DOMAIN,
            "method_count": 4,
            "method_record_digests": list(METHOD_DIGESTS),
            "method_record_order": list(METHOD_IDS),
            "registry_binding": authority_bindings["method_parameter_registry"],
            "registry_record_count": 10,
            "role_scope": ["role10_killing_factor_geometry"],
            "selected_records": _selected_methods(registry),
        },
        "numerical_semantics": {
            "contact": {
                "cell_classification": {
                    "cell_full": "full_if_every_positive_area_wrapped_segment_pair_is_full",
                    "cell_partial": "partial_otherwise",
                    "cell_zero": "zero_if_every_positive_area_wrapped_segment_pair_is_zero",
                    "full_segment_pair": (
                        "all_four_corner_squared_distances_less_than_or_equal_to_radius_squared"
                    ),
                    "partial_segment_pair": "otherwise",
                    "zero_segment_pair": (
                        "nearest_squared_distance_greater_than_or_equal_to_radius_squared"
                    ),
                },
                "derived_expected_partial_cell_count": 1_304,
                "derived_count_role": (
                    "geometry_derived_expected_count_not_method_threshold_or_scientific_result"
                ),
                "flat_index": "a*n_Y+b",
                "normalization": (
                    "divide_contact_area_by_exact_R_cell_volume_times_exact_Y_cell_volume"
                ),
                "tangent_equality_convention": (
                    "zero_measure_tangency_is_exact_zero_and_zero_test_has_equality"
                ),
                "units": "dimensionless",
                "wrapped_periodic_segments": "exact_minimum_image_positive_area_segments",
            },
            "normalization_boundary": {
                "W_inverse_in_contact": "forbidden",
                "W_inverse_in_profile": "forbidden",
                "later_factorization_only": "V_jmab=W^-1*C_ab*Phi_jm",
            },
            "precision": {
                "analytic_area_saved_bits": 256,
                "producer_contact_bits": 192,
                "producer_profile_bits": 192,
                "verifier_primary_bits": 384,
                "verifier_sentinel_bits": 512,
            },
            "profile": {
                "cell_mass_width_definition": (
                    "cell_volume_exact*(published_upper_exact-published_lower_exact)"
                ),
                "density_definition": (
                    "Phi_jm=integral_over_M_cell_phi_j_dM_divided_by_exact_cell_volume"
                ),
                "flat_index": "m",
                "profile_order": [0, 1, 2, 3],
                "stored_quantity": "cell_average_density_not_cell_mass",
                "unit_mass_identity": ("sum_m_exact_cell_volume_times_Phi_jm_contains_exact_one"),
                "units": "inverse_length",
            },
            "producer_gates": {
                "analytic_area_relative_width": "1/1000000000000",
                "contact_area_relative_width_over_radius_squared": "1/10000000000",
                "profile_cell_mass_width": "1/1099511627776",
                "profile_integral_relative_width": "1/10000000000",
                "published_contact_interval_width": "1/1099511627776",
            },
        },
        "publication_contract": {
            "artifact_install": (
                "stage_below_authenticated_output_parent_on_same_filesystem_fsync_every_"
                "file_fsync_directories_postorder_and_install_without_replacement"
            ),
            "component_reads": (
                "component_anchored_no_symlink_regular_single_link_bounded_reads_only"
            ),
            "destination_policy": "existing_destination_is_terminal_failure_never_replaced",
            "directory_mode_transition": "0700_staging_to_0555_published",
            "file_mode_transition": "0600_staging_to_0444_published",
            "output_parent": {
                "creation_by_role10": "forbidden",
                "group_or_world_writable": "forbidden",
                "mode": "0700",
                "must_preexist": "required",
                "owner": "effective_uid",
                "same_filesystem_for_all_three_outputs": "required",
            },
            "outer_receipt_install": ("stage_fsync_install_without_replacement_then_fsync_parent"),
            "publication_order": [
                "artifact_directory",
                "canonical_semantic_receipt_sibling",
                "outer_validation_receipt_sibling",
            ],
            "semantic_receipt_install": (
                "stage_fsync_install_without_replacement_then_fsync_parent"
            ),
            "temporary_cleanup": (
                "remove_only_stage_or_child_paths_owned_by_the_current_inode_identity"
            ),
        },
        "receipt_contract": {
            "child_observation_count": 2,
            "child_semantic_body_rule": (
                "two_clean_isolated_children_create_byte_identical_canonical_temporary_"
                "semantic_receipt_bodies"
            ),
            "outer_receipt": {
                "claim_boundary": false_claims,
                "exact_sections": [
                    "schema",
                    "status",
                    "claim_boundary",
                    "request_binding",
                    "artifact_binding",
                    "authority_bindings",
                    "method_bindings",
                    "producer_runtime_closure_binding",
                    "verifier_runtime_closure_binding",
                    "canonical_semantic_receipt_binding",
                    "run_observations",
                    "tree_stability_evidence",
                    "cleanup_evidence",
                ],
                "maximum_bytes": 262_144,
                "schema": OUTER_RECEIPT_SCHEMA,
            },
            "retention_rule": (
                "outer_binds_one_canonical_semantic_receipt_sibling_and_retains_two_"
                "run_observations_tree_stability_evidence_and_child_cleanup_evidence"
            ),
            "slot_contract": {
                "global_plan_v2_slot_count": 10,
                "role10_output_count": 3,
                "role10_slots_including_request": 4,
                "roles8_9_slots_each": 3,
                "slots": {
                    "artifact": ("{output_parent}/role10.killing-factor-geometry"),
                    "outer_validation_receipt": (
                        "{output_parent}/role10.killing-factor-geometry.validation-receipt.json"
                    ),
                    "request": "{request_parent}/role10.request.json",
                    "semantic_receipt": (
                        "{output_parent}/role10.killing-factor-geometry.semantic-receipt.json"
                    ),
                },
            },
            "semantic_receipt": {
                "claim_boundary": false_claims,
                "exact_sections": [
                    "schema",
                    "status",
                    "claim_boundary",
                    "request_binding",
                    "artifact_binding",
                    "authority_bindings",
                    "method_bindings",
                    "verification_counts",
                    "precision_coverage",
                    "containment_ledger",
                    "tree_inventory_sha256",
                ],
                "maximum_bytes": 2_097_152,
                "schema": SEMANTIC_RECEIPT_SCHEMA,
            },
            "temporary_child_receipts": (
                "both_are_removed_after_outer_rechecks_byte_identity_and_retains_one_body"
            ),
        },
        "resource_caps": {
            "child_process_deadline_seconds": 1_200,
            "maximum_bump_breakpoints": 20_000,
            "maximum_child_ack_bytes": 4_096,
            "maximum_child_observation_bytes": 65_536,
            "maximum_child_semantic_receipt_bytes": 2_097_152,
            "maximum_child_stderr_bytes": 4_096,
            "maximum_dyadic_coordinate_component_bits": 256,
            "maximum_json_file_bytes": 2_097_152,
            "maximum_mpfr_to_mpq_denominator_bits": 4_096,
            "maximum_outer_receipt_bytes": 262_144,
            "maximum_raw_contact_file_bytes": 553_840,
            "maximum_raw_support_file_bytes": 3_312,
            "maximum_simpson_dfs_stack": 65,
            "maximum_simpson_dyadic_depth": 64,
            "maximum_simpson_exact_component_bits": 8_192,
            "maximum_simpson_panels": 4_194_304,
            "maximum_tree_directories": 64,
            "maximum_tree_files": 256,
            "maximum_tree_relative_depth": 3,
            "maximum_tree_total_bytes": 67_108_864,
            "outer_deadline_seconds": 2_700,
            "outer_nonchild_reserve_seconds": 300,
            "semantic_deadline_seconds": 1_140,
        },
        "schema": SCHEMA,
        "status": STATUS,
        "verification_contract": {
            "analytic_area": {
                "containment_chain": "saved_256_contains_oracle_384_contains_sentinel_512",
                "formula": "pi_times_radius_squared",
                "relative_width_gate": "1/1000000000000",
            },
            "backend_boundary": ("source_independent_same_MPFR_backend_not_backend_independent"),
            "contact_coverage": {
                "all_partial_cells_at_384": 1_304,
                "first_partial_cell_per_row_at_512": 12,
                "oracle_relative_width_gate_per_partial_cell": (
                    "1/1532495540865888858358347027150309183618739122183602176"
                ),
                "published_contains_primary_for_every_partial": 1_304,
                "published_contains_sentinel_for_first_partial_per_row": 12,
                "ratio_gate": (
                    "oracle_cell_width_divided_by_nonzero_producer_cell_width_at_most_1/8"
                ),
                "ratio_scope": "partial_nonzero_producer_widths_only",
            },
            "profile_coverage": {
                "all_profile_aggregates_at_paired_384_512": 48,
                "all_profile_cells_at_paired_384_512": 6_852,
                "aggregate_relative_width_gate": "1/10000000000",
                "cell_mass_width_gate": "1/1099511627776",
                "ratio_gate": (
                    "oracle_cell_mass_width_divided_by_nonzero_producer_cell_mass_width_at_most_1/8"
                ),
                "ratio_scope": ("nonzero_profile_cell_mass_widths_only_exact_zero_cells_excluded"),
            },
            "scientific_source_separation": {
                "candidate_values_used_for_oracle_branching": "forbidden",
                "producer_imports_verifier_numerics": "forbidden",
                "shared_numerical_implementation": "forbidden",
                "verifier_imports_producer_numerics": "forbidden",
                "verifier_reconstructs_from_frozen_authorities": "required",
            },
        },
    }


def _immutable_payload(path: Path) -> bytes:
    return read_regular(
        path,
        cap=8_000_000,
        required_mode=0o444,
    )


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
    path = _canonical_absolute(path)
    parent, leaf = open_parent_anchored(path)
    opened_parent = os.fstat(parent)
    parent_identity = opened_parent.st_dev, opened_parent.st_ino
    if (
        not stat.S_ISDIR(opened_parent.st_mode)
        or opened_parent.st_uid != os.geteuid()
        or stat.S_IMODE(opened_parent.st_mode) & 0o022
    ):
        os.close(parent)
        raise OperationModelBuildError(
            "pre-existing UID-owned non-group/world-writable output parent required"
        )
    stage = f".{leaf}.{secrets.token_hex(16)}.stage"
    recovery_parent = -1
    descriptor = -1
    transaction: StageCreationTransaction | None = None
    stage_identity: tuple[int, int] | None = None
    final_attempted = False
    try:
        transaction = StageCreationTransaction(parent, stage)
        transaction.start()
        transaction.await_ready()
        descriptor = -1 if transaction.descriptor is None else transaction.descriptor
        stage_identity = transaction.identity
        if descriptor < 0 or stage_identity is None:
            raise OperationModelBuildError("stage transaction result missing")
        transaction.release_descriptor(descriptor)

        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0 or count > len(payload) - written:
                raise OperationModelBuildError("short model write")
            written += count
        os.fchmod(descriptor, 0o444)
        os.fsync(descriptor)
        staged = os.fstat(descriptor)
        if (staged.st_dev, staged.st_ino) != stage_identity:
            raise OperationModelBuildError("staging descriptor identity changed")
        os.close(descriptor)
        descriptor = -1

        final_attempted = True
        try:
            os.link(
                stage,
                leaf,
                src_dir_fd=parent,
                dst_dir_fd=parent,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise OperationModelBuildError(
                f"refusing to replace existing output: {path}"
            ) from error
        if not _unlink_owned(parent, stage, stage_identity):
            raise OperationModelBuildError("staging identity changed before cleanup")
        os.fsync(parent)
        final = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (final.st_dev, final.st_ino) != stage_identity
            or stat.S_IMODE(final.st_mode) != 0o444
            or final.st_nlink != 1
            or final.st_uid != os.geteuid()
            or final.st_size != len(payload)
        ):
            raise OperationModelBuildError("published model identity/mode/size drift")
        if _immutable_payload(path) != payload:
            raise OperationModelBuildError("published model verification failed")
        acknowledged = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            (acknowledged.st_dev, acknowledged.st_ino) != stage_identity
            or stat.S_IMODE(acknowledged.st_mode) != 0o444
            or acknowledged.st_nlink != 1
            or acknowledged.st_uid != os.geteuid()
            or acknowledged.st_size != len(payload)
        ):
            raise OperationModelBuildError("published model post-read identity drift")
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
        if _parent_matches(parent, parent_identity):
            cleanup_parent = parent
        else:
            try:
                recovered, recovered_leaf = open_parent_anchored(path)
                if recovered_leaf == leaf and _parent_matches(recovered, parent_identity):
                    recovery_parent = recovered
                    cleanup_parent = recovered
                else:
                    _close_safely(recovered)
            except BaseException:
                pass
        if cleanup_parent >= 0:
            if final_attempted and stage_identity is not None:
                try:
                    _unlink_owned(cleanup_parent, leaf, stage_identity)
                except BaseException:
                    pass
            if stage_identity is not None:
                try:
                    _unlink_owned(cleanup_parent, stage, stage_identity)
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


def check(path: Path) -> str:
    expected = canonical_bytes(build_model())
    observed = _immutable_payload(path)
    if observed != expected or parse_canonical_json(observed, "operation model") != build_model():
        raise OperationModelBuildError("operation model byte drift")
    return sha256(observed)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parse_args(argv)
    output = arguments.output.resolve()
    try:
        if arguments.check:
            digest = check(output)
        else:
            payload = canonical_bytes(build_model())
            publish_no_replace(output, payload)
            digest = sha256(payload)
    except OperationModelBuildError as error:
        print(f"HOLD_ROLE10_OPERATION_MODEL: {error}", file=sys.stderr)
        return 2
    print(f"PASS_ROLE10_OPERATION_MODEL {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
