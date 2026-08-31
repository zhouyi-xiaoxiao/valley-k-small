#!/usr/bin/env python3
"""Source-separated validator for the role-10 numerical operation model.

The validator imports no builder code and performs no numerical geometry
calculation.  It authenticates the accepted registry/member/mirror sources,
reconstructs the exact package inventory, and enforces the result-blind
contract boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import unicodedata
from pathlib import Path
from typing import Any, Final, Sequence

SELF: Final = Path(__file__).resolve()
REPORT: Final = SELF.parents[1]
DEFAULT_MODEL: Final = (
    REPORT / "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v1_candidate.json"
)

SCHEMA: Final = "encounter_continuum_c1_n0_role10_numerical_operation_model_v1_candidate"
STATUS: Final = "RESULT_BLIND_CONTRACT_ONLY_CANDIDATE_NO_NUMERICAL_IMPLEMENTATION_OR_EXECUTION"
SOURCE_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_source_v3"
ROW_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_row_v1"
RAW_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_raw_interval_file_v1"
SEMANTIC_RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_semantic_receipt_v1"
OUTER_RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_validation_receipt_v2"
EXPECTED_MODEL_SHA256: Final = "d0e4abd040865863f1cbf9768d17975f4fbd4310f47eda87d9878bd4fffd6109"
METHOD_DIGEST_DOMAIN: Final = "encounter-outward-method-parameters-v4"

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
    "reference_density": (
        "artifacts/data/continuum_c1_reference_density_source_v1.json",
        "encounter_continuum_c1_reference_density_source_v1",
        "7b890d727ad0b229557de1841ae82befb8d8f83e79edc6b5348b277c3024e575",
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
CLAIM_KEYS: Final = {
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
}
TOP_KEYS: Final = {
    "artifact_contract",
    "authority_bindings",
    "authority_model",
    "claim_boundary",
    "forbidden_surface",
    "invocation_contract",
    "method_contract",
    "numerical_semantics",
    "publication_contract",
    "receipt_contract",
    "resource_caps",
    "schema",
    "status",
    "verification_contract",
}


class OperationModelValidationError(RuntimeError):
    """The operation-model candidate is not the frozen result-blind authority."""


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > 64:
        raise OperationModelValidationError("JSON depth cap exceeded")
    if isinstance(value, float):
        raise OperationModelValidationError("floating JSON literal forbidden")
    if type(value) in (bool, int) or value is None:
        if type(value) is int and value.bit_length() > 65_536:
            raise OperationModelValidationError("JSON integer cap exceeded")
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise OperationModelValidationError("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                raise OperationModelValidationError("invalid JSON key")
            _strict_tree(item, depth + 1)
        return
    raise OperationModelValidationError(f"forbidden JSON type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    _strict_tree(value)
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise OperationModelValidationError("duplicate or invalid JSON key")
        result[key] = value
    return result


def parse_canonical_json(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                OperationModelValidationError(f"{label}: float {token} forbidden")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                OperationModelValidationError(f"{label}: constant {token} forbidden")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OperationModelValidationError(f"{label}: invalid ASCII JSON") from error
    if type(value) is not dict or canonical_bytes(value) != payload:
        raise OperationModelValidationError(f"{label}: noncanonical JSON")
    return value


def parse_authority_json(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("ascii"),
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                OperationModelValidationError(f"{label}: float {token} forbidden")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                OperationModelValidationError(f"{label}: constant {token} forbidden")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OperationModelValidationError(f"{label}: invalid ASCII JSON") from error
    if type(value) is not dict:
        raise OperationModelValidationError(f"{label}: JSON object required")
    _strict_tree(value)
    return value


def _canonical_absolute(path: Path) -> Path:
    absolute = Path(os.path.abspath(os.fspath(path.expanduser())))
    if not absolute.is_absolute() or absolute != Path(os.path.abspath(absolute)):
        raise OperationModelValidationError("canonical absolute path required")
    return absolute


def open_parent_anchored(path: Path) -> tuple[int, str]:
    path = _canonical_absolute(path)
    if len(path.parts) < 2:
        raise OperationModelValidationError("path requires parent and leaf")
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
                raise OperationModelValidationError("unsafe path component")
            following = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
        leaf = path.parts[-1]
        if leaf in {"", ".", ".."}:
            raise OperationModelValidationError("unsafe path leaf")
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
            raise OperationModelValidationError("directory chain changed")
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
            raise OperationModelValidationError("bounded single-link regular file required")
        payload = bytearray()
        while len(payload) < opened.st_size:
            block = os.read(descriptor, opened.st_size - len(payload))
            if not block:
                raise OperationModelValidationError("short stable read")
            payload.extend(block)
        if os.read(descriptor, 1):
            raise OperationModelValidationError("file grew during stable read")
        after = os.fstat(descriptor)
        linked = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ) != (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
            opened.st_ctime_ns,
        ) or (linked.st_dev, linked.st_ino) != (opened.st_dev, opened.st_ino):
            raise OperationModelValidationError("file changed during stable read")
        _verify_live_parent(path, parent, parent_identity)
        return bytes(payload)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent)


def _read_authority(name: str, *, immutable: bool = False) -> tuple[dict[str, Any], bytes]:
    relative, schema, expected_sha = AUTHORITY_SPECS[name]
    payload = read_regular(
        REPORT / relative,
        cap=8_000_000,
        required_mode=0o444 if immutable else None,
    )
    if sha256(payload) != expected_sha:
        raise OperationModelValidationError(f"{name}: authority SHA-256 drift")
    value = parse_authority_json(payload, name)
    if value.get("schema") != schema:
        raise OperationModelValidationError(f"{name}: authority schema drift")
    return value, payload


def _method_digest(parameters: dict[str, Any]) -> str:
    return sha256(METHOD_DIGEST_DOMAIN.encode("ascii") + b"\0" + canonical_bytes(parameters))


def _selected_methods(registry: dict[str, Any]) -> list[dict[str, Any]]:
    if set(registry) != {"claim_boundary", "parameter_count", "parameters", "schema", "status"}:
        raise OperationModelValidationError("registry exact-key drift")
    records = registry["parameters"]
    if type(records) is not list or len(records) != 10 or registry["parameter_count"] != 10:
        raise OperationModelValidationError("registry cardinality drift")
    by_id = {
        record.get("parameter_id"): record
        for record in records
        if type(record) is dict and type(record.get("parameter_id")) is str
    }
    selected: list[dict[str, Any]] = []
    for identifier, digest in zip(METHOD_IDS, METHOD_DIGESTS, strict=True):
        record = by_id.get(identifier)
        if (
            type(record) is not dict
            or set(record) != {"method_parameter_sha256", "parameter_id", "parameters"}
            or record["method_parameter_sha256"] != digest
            or _method_digest(record["parameters"]) != digest
            or record["parameters"].get("source_role_scope") != ["role10_killing_factor_geometry"]
        ):
            raise OperationModelValidationError(f"method record drift: {identifier}")
        selected.append(record)
    return selected


def _expected_rows(member: dict[str, Any]) -> list[dict[str, Any]]:
    bindings = member.get("n0_sequence_bindings")
    semantic_ids = member.get("configuration_semantic_ids")
    if type(bindings) is not list or type(semantic_ids) is not list:
        raise OperationModelValidationError("member row inventories missing")
    rows: list[dict[str, Any]] = []
    for index, expected in enumerate(EXPECTED_ROWS):
        label, family, member_id, n_m, n_r, n_y = expected
        semantic_id = {
            "authority_label": label,
            "refinement_family_id": family,
            "refinement_member_id": member_id,
        }
        if (
            bindings[index].get("configuration_index") != index
            or bindings[index].get("authority_label") != label
            or bindings[index].get("n0_anchor_shape") != [n_m, n_r, n_y]
            or semantic_ids[index] != semantic_id
        ):
            raise OperationModelValidationError(f"member row drift at {index}")
        row_dir = f"rows/row_{index:02d}"
        profiles = [
            {
                "byte_length": n_m * 16,
                "flat_index": "m",
                "logical_shape": [n_m],
                "path": f"{row_dir}/profile_{profile_index:02d}.intervals.be64",
                "profile_index": profile_index,
                "record_count": n_m,
                "units": "inverse_length",
            }
            for profile_index in range(4)
        ]
        rows.append(
            {
                "configuration_index": index,
                "configuration_semantic_id": semantic_id,
                "contact": {
                    "byte_length": n_r * n_y * 16,
                    "flat_index": "a*n_Y+b",
                    "logical_shape": [n_r, n_y],
                    "path": f"{row_dir}/contact.intervals.be64",
                    "record_count": n_r * n_y,
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


def _expected_paths(rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    directories = [".", "rows", *(f"rows/row_{index:02d}" for index in range(12))]
    files = ["manifest.json"]
    for row in rows:
        files.extend(
            [
                row["row_manifest_path"],
                row["contact"]["path"],
                *(profile["path"] for profile in row["profiles"]),
            ]
        )
    return directories, files


def _validate_mirror(mirror: dict[str, Any], manifest_raw: bytes) -> dict[str, Any]:
    expected_coverage = {
        "configuration_authority_lineage_file_count": 3,
        "configuration_initial_geometry_file_count": 1,
        "exact_writable_precommit_input_closure_mirrored": True,
        "member_v4_partition_file_count": 36,
        "original_report_relative_suffix_preserved_under_files": True,
        "standalone_content_addressed_validation_without_original_writable_sources": True,
    }
    if (
        mirror.get("coverage") != expected_coverage
        or mirror.get("entry_count") != 40
        or type(mirror.get("entries")) is not list
        or len(mirror["entries"]) != 40
        or mirror.get("inventory_digests", {}).get("configuration_row_inventory", {}).get("sha256")
        != CONFIGURATION_INVENTORY_SHA256
        or mirror.get("inventory_digests", {})
        .get("member_v4_partition_inventory", {})
        .get("sha256")
        != PARTITION_INVENTORY_SHA256
    ):
        raise OperationModelValidationError("sealed mirror coverage drift")
    manifest_relative = AUTHORITY_SPECS["sealed_authentication_mirror"][0]
    mirror_root = (REPORT / manifest_relative).parent
    files = {"manifest.json"}
    directories = {"."}
    total_bytes = len(manifest_raw)
    for ordinal, entry in enumerate(mirror["entries"]):
        if (
            type(entry) is not dict
            or entry.get("ordinal") != ordinal
            or type(entry.get("mirror_relative_path")) is not str
            or type(entry.get("byte_length")) is not int
            or type(entry.get("sha256")) is not str
        ):
            raise OperationModelValidationError(f"sealed mirror entry drift at {ordinal}")
        relative = Path(entry["mirror_relative_path"])
        if (
            relative.is_absolute()
            or not relative.parts
            or relative.parts[0] != "files"
            or any(part in {"", ".", ".."} for part in relative.parts)
            or relative.as_posix() != entry["mirror_relative_path"]
            or relative.as_posix() in files
        ):
            raise OperationModelValidationError(f"unsafe sealed mirror path at {ordinal}")
        payload = read_regular(mirror_root / relative, cap=8_000_000, required_mode=0o444)
        if len(payload) != entry["byte_length"] or sha256(payload) != entry["sha256"]:
            raise OperationModelValidationError(f"sealed mirror byte drift at {ordinal}")
        files.add(relative.as_posix())
        parent = relative.parent
        while parent != Path("."):
            directories.add(parent.as_posix())
            parent = parent.parent
        total_bytes += len(payload)
    if len(files) != 41 or len(directories) != 20 or total_bytes != 1_176_207:
        raise OperationModelValidationError("sealed mirror package topology drift")
    return {
        "directory_count": 20,
        "entry_count": 40,
        "file_count": 41,
        "future_execution_source": (
            "sealed_mirror_copies_only_original_paths_retained_as_semantic_lineage"
        ),
        "manifest_path": manifest_relative,
        "manifest_schema": AUTHORITY_SPECS["sealed_authentication_mirror"][1],
        "manifest_sha256": AUTHORITY_SPECS["sealed_authentication_mirror"][2],
        "total_bytes": 1_176_207,
        "validated_coverage": expected_coverage,
    }


def _exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != expected:
        raise OperationModelValidationError(f"{label}: exact-key drift")
    return value


def validate_value(
    model: dict[str, Any],
    *,
    raw: bytes | None = None,
    enforce_frozen_sha: bool = True,
) -> None:
    _strict_tree(model)
    _exact_keys(model, TOP_KEYS, "model")
    if model["schema"] != SCHEMA or model["status"] != STATUS:
        raise OperationModelValidationError("model identity drift")
    claims = _exact_keys(model["claim_boundary"], CLAIM_KEYS, "claim boundary")
    if any(value is not False for value in claims.values()):
        raise OperationModelValidationError("claim boundary must remain all false")

    expected_bindings = {
        name: {"path": path, "schema": schema, "sha256": digest}
        for name, (path, schema, digest) in AUTHORITY_SPECS.items()
    }
    if model["authority_bindings"] != expected_bindings:
        raise OperationModelValidationError("authority binding drift")
    registry, _ = _read_authority("method_parameter_registry", immutable=True)
    member, _ = _read_authority("member_spec", immutable=True)
    mirror, mirror_raw = _read_authority("sealed_authentication_mirror", immutable=True)
    selected_methods = _selected_methods(registry)
    mirror_contract = _validate_mirror(mirror, mirror_raw)

    method = _exact_keys(
        model["method_contract"],
        {
            "digest_domain",
            "method_count",
            "method_record_digests",
            "method_record_order",
            "registry_binding",
            "registry_record_count",
            "role_scope",
            "selected_records",
        },
        "method contract",
    )
    if (
        method["digest_domain"] != METHOD_DIGEST_DOMAIN
        or method["method_count"] != 4
        or method["method_record_order"] != list(METHOD_IDS)
        or method["method_record_digests"] != list(METHOD_DIGESTS)
        or method["registry_binding"] != expected_bindings["method_parameter_registry"]
        or method["registry_record_count"] != 10
        or method["role_scope"] != ["role10_killing_factor_geometry"]
        or method["selected_records"] != selected_methods
    ):
        raise OperationModelValidationError("selected method contract drift")

    authority_model = _exact_keys(
        model["authority_model"],
        {
            "authentication_closure_roles",
            "configuration_row_inventory_sha256",
            "member_identity_sha256",
            "normative_direct_role_dependencies",
            "partition_inventory_sha256",
            "sealed_authentication_mirror",
            "separation_rule",
        },
        "authority model",
    )
    if (
        authority_model["normative_direct_role_dependencies"] != [1, 3, 5, 6, 7]
        or authority_model["member_identity_sha256"] != MEMBER_IDENTITY_SHA256
        or authority_model["configuration_row_inventory_sha256"] != CONFIGURATION_INVENTORY_SHA256
        or authority_model["partition_inventory_sha256"] != PARTITION_INVENTORY_SHA256
        or authority_model["sealed_authentication_mirror"] != mirror_contract
    ):
        raise OperationModelValidationError("authority model drift")

    rows = _expected_rows(member)
    directories, files = _expected_paths(rows)
    artifact = _exact_keys(
        model["artifact_contract"],
        {
            "directory_paths",
            "encoding",
            "file_paths",
            "path_templates",
            "rows",
            "schema_key_contracts",
            "schemas",
            "stored_precision_policy",
            "top_file_inventory",
            "totals",
        },
        "artifact contract",
    )
    expected_totals = {
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
    }
    if (
        artifact["rows"] != rows
        or artifact["directory_paths"] != directories
        or artifact["file_paths"] != files
        or artifact["totals"] != expected_totals
        or artifact["schemas"]
        != {"raw_interval_file": RAW_SCHEMA, "row": ROW_SCHEMA, "source": SOURCE_SCHEMA}
        or artifact["top_file_inventory"]
        != {
            "entry_count": 72,
            "excludes_self_referential_top_manifest": "required",
            "ordered_paths": files[1:],
        }
    ):
        raise OperationModelValidationError("artifact topology drift")
    key_contracts = artifact["schema_key_contracts"]
    if (
        set(key_contracts["raw_manifest_exact_keys"])
        != {
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
        }
        or "record_count" not in key_contracts["profile_section_exact_keys"]
        or set(key_contracts["top_manifest_exact_keys"])
        != {
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
        }
    ):
        raise OperationModelValidationError("manifest exact-key contract drift")

    resources = model["resource_caps"]
    if resources != {
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
    }:
        raise OperationModelValidationError("resource/deadline cap drift")

    receipt = model["receipt_contract"]
    if (
        receipt["child_observation_count"] != 2
        or receipt["semantic_receipt"]["schema"] != SEMANTIC_RECEIPT_SCHEMA
        or receipt["semantic_receipt"]["maximum_bytes"] != 2_097_152
        or receipt["outer_receipt"]["schema"] != OUTER_RECEIPT_SCHEMA
        or receipt["outer_receipt"]["maximum_bytes"] != 262_144
        or receipt["slot_contract"]["global_plan_v2_slot_count"] != 10
        or receipt["slot_contract"]["role10_output_count"] != 3
        or any(
            value is not False for value in receipt["semantic_receipt"]["claim_boundary"].values()
        )
        or any(value is not False for value in receipt["outer_receipt"]["claim_boundary"].values())
    ):
        raise OperationModelValidationError("receipt topology drift")

    invocations = model["invocation_contract"]
    for role in (
        "producer_argv",
        "outer_verifier_argv",
        "child_semantic_verifier_argv",
    ):
        if invocations[role][1:3] != ["-I", "-B"]:
            raise OperationModelValidationError(f"{role}: isolation flags drift")
    if (
        "--semantic-receipt" not in invocations["outer_verifier_argv"]
        or "--receipt" not in invocations["outer_verifier_argv"]
        or invocations["shared_module_boundary"]["numerical_source_sets"]
        != "producer_and_verifier_disjoint"
    ):
        raise OperationModelValidationError("invocation/runtime separation drift")

    contact = model["numerical_semantics"]["contact"]
    profile = model["numerical_semantics"]["profile"]
    verification = model["verification_contract"]
    if (
        contact["derived_expected_partial_cell_count"] != 1_304
        or contact["cell_classification"]["zero_segment_pair"]
        != "nearest_squared_distance_greater_than_or_equal_to_radius_squared"
        or contact["cell_classification"]["full_segment_pair"]
        != "all_four_corner_squared_distances_less_than_or_equal_to_radius_squared"
        or profile["cell_mass_width_definition"]
        != "cell_volume_exact*(published_upper_exact-published_lower_exact)"
        or model["numerical_semantics"]["normalization_boundary"]["W_inverse_in_contact"]
        != "forbidden"
        or model["numerical_semantics"]["normalization_boundary"]["W_inverse_in_profile"]
        != "forbidden"
        or verification["contact_coverage"]["all_partial_cells_at_384"] != 1_304
        or verification["contact_coverage"]["first_partial_cell_per_row_at_512"] != 12
        or verification["profile_coverage"]["all_profile_cells_at_paired_384_512"] != 6_852
        or verification["profile_coverage"]["all_profile_aggregates_at_paired_384_512"] != 48
        or "1/8" not in verification["contact_coverage"]["ratio_gate"]
        or "1/8" not in verification["profile_coverage"]["ratio_gate"]
    ):
        raise OperationModelValidationError("numerical semantic boundary drift")

    forbidden = model["forbidden_surface"]
    if (
        forbidden["future_code_hashes"]
        != ("required_in_runtime_closure_before_commitment_but_not_yet_available_in_this_contract")
        or forbidden["unknown_future_output_or_result_hash_pins"] != "forbidden"
        or "producer_code_sha256" in forbidden["forbidden_precommit_or_artifact_fields"]
        or "verifier_code_sha256" in forbidden["forbidden_precommit_or_artifact_fields"]
    ):
        raise OperationModelValidationError("future hash boundary drift")

    publication = model["publication_contract"]
    if publication["output_parent"] != {
        "creation_by_role10": "forbidden",
        "group_or_world_writable": "forbidden",
        "mode": "0700",
        "must_preexist": "required",
        "owner": "effective_uid",
        "same_filesystem_for_all_three_outputs": "required",
    }:
        raise OperationModelValidationError("future publication-parent drift")

    if raw is not None:
        if canonical_bytes(model) != raw:
            raise OperationModelValidationError("model canonical byte drift")
        if enforce_frozen_sha:
            if EXPECTED_MODEL_SHA256.startswith("TO_BE_FROZEN"):
                raise OperationModelValidationError("validator SHA is not frozen")
            if sha256(raw) != EXPECTED_MODEL_SHA256:
                raise OperationModelValidationError("operation-model SHA-256 drift")


def validate(path: Path) -> str:
    raw = read_regular(path, cap=8_000_000, required_mode=0o444)
    model = parse_canonical_json(raw, "operation model")
    validate_value(model, raw=raw)
    return sha256(raw)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parse_args(argv)
    try:
        digest = validate(arguments.model)
    except (OSError, OperationModelValidationError) as error:
        print(f"HOLD_ROLE10_OPERATION_MODEL_VALIDATION: {error}", file=sys.stderr)
        return 2
    print(f"PASS_ROLE10_OPERATION_MODEL_VALIDATION {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
