"""Build the result-blind role-10 sealed authentication-closure mirror.

This builder copies exactly the writable precommit inputs whose bytes must
remain available after an external replay environment loses access to the
working report tree.  It never opens a role-10 numerical result, artifact, or
receipt.  The resulting directory is an internal authentication candidate; it
does not create an external commitment and does not execute a replay.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import stat
import sys
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Final, NoReturn, Sequence

CODE: Final = Path(__file__).resolve().parent
REPORT: Final = CODE.parent
ARTIFACT_NAME: Final = "continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate"
DEFAULT_OUTPUT: Final = REPORT / "artifacts/data" / ARTIFACT_NAME

SCHEMA: Final = "encounter_continuum_c1_n0_role10_sealed_authentication_mirror_v1_candidate"
STATUS: Final = (
    "RESULT_BLIND_SEALED_AUTHENTICATION_CLOSURE_MIRROR_CANDIDATE_ONLY_"
    "NOT_EXTERNAL_COMMITMENT_NOT_REPLAY"
)
MEMBER_SCHEMA: Final = "encounter_continuum_c1_c2_n0_member_spec_v4_candidate"
MEMBER_STATUS: Final = (
    "STRUCTURAL_PARTITION_IDENTITY_V4_CANDIDATE_ONLY_NOT_EXTERNALLY_COMMITTED_NOT_PRODUCTION_MEMBER"
)
CONFIGURATION_SCHEMA: Final = "encounter_physical_configuration_family_control_free_v1"
CONFIGURATION_STATUS: Final = "CONTROL_FREE_GEOMETRY_SPEC_ONLY_NOT_F0_NOT_F1"
FACTORIZATION_SCHEMA: Final = "encounter_continuum_c1_factorization_source_v2_candidate"
FACTORIZATION_STATUS: Final = (
    "OUTCOME_FREE_CONTROL_FREE_FACTORIZATION_CANDIDATE_ONLY_NOT_EXTERNALLY_"
    "COMMITTED_NO_NUMERIC_ENCLOSURES_NO_CONCRETE_KILLING"
)
INITIAL_BUNDLE_SCHEMA: Final = "encounter_control_free_production_initial_stream_v1"
INITIAL_BUNDLE_STATUS: Final = (
    "PASS_CONTROL_FREE_12_ROW_FILE_BACKED_PRODUCER_CONSISTENCY_ONLY_NOT_INDEPENDENT_NOT_F0_NOT_F1"
)
INITIAL_GEOMETRY_SCHEMA: Final = "encounter_physical_initial_analytic_source_v1"
PARTITION_SCHEMA: Final = "encounter_exact_axis_partition_v1"

MEMBER_RELATIVE: Final = PurePosixPath(
    "artifacts/data/continuum_c1_c2_n0_member_spec_v4_candidate.json"
)
CONFIGURATION_RELATIVE: Final = PurePosixPath(
    "artifacts/data/physical_configuration_family_control_free_v1.json"
)
FACTORIZATION_RELATIVE: Final = PurePosixPath(
    "artifacts/data/continuum_c1_factorization_source_v2_candidate.json"
)
INITIAL_BUNDLE_RELATIVE: Final = PurePosixPath(
    "artifacts/data/physical_production_initial_stream_v1/bundle.json"
)
INITIAL_BUNDLE_DIRECTORY: Final = INITIAL_BUNDLE_RELATIVE.parent
INITIAL_GEOMETRY_RELATIVE: Final = PurePosixPath(
    "artifacts/data/physical_initial_analytic_source_v1.json"
)

MEMBER_SHA256: Final = "b2982e4e2b0bac208f80472d0de959fa152a5494c895677d081836c482e5f2d5"
MEMBER_IDENTITY_SHA256: Final = "68c8f9eeaca5127e9fb49c4671731990869350b358c67632fb11513f26472193"
CONFIGURATION_SHA256: Final = "063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084"
FACTORIZATION_SHA256: Final = "1cf32a65081dc4f381daae45a556e0e26dc9411eb248cd99e555b754ffad3e26"
INITIAL_BUNDLE_SHA256: Final = "5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e"
INITIAL_GEOMETRY_SHA256: Final = "0b2efec5dc1abea1380ab862e46825e7b79658fe9bfa0ac6637e1426ed9f7f5f"
CONFIGURATION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-configuration-row-inventory-v1"
PARTITION_INVENTORY_DOMAIN: Final = "encounter-continuum-c1-n0-partition-inventory-v1"
CONFIGURATION_INVENTORY_SHA256: Final = (
    "8da99e7910cac1f2ba6b69fb2d0ec52b21412abfa1d59c898462e138d82ebbb2"
)
PARTITION_INVENTORY_SHA256: Final = (
    "f3507f4eec07e216bd54bcf4486ab5cef1589511367f781174b89fdfe2e7b51f"
)
COORDINATES: Final = ("midpoint", "relative_parallel", "relative_perpendicular")
EXPECTED_CONFIGURATION_COUNT: Final = 12
EXPECTED_PARTITION_COUNT: Final = 36
EXPECTED_ENTRY_COUNT: Final = 40

CLAIM_KEYS: Final = (
    "candidate_authoritative",
    "external_predecessor_commitment_present",
    "numerical_killing_artifact_present",
    "ordered_roles_8_10_replay_executed",
    "production_same_member_bridge_accepted",
    "release_eligible",
    "role10_acceptance_receipt_present",
    "science_executed",
    "submission_eligible",
)
LINEAGE_ROLES: Final = (
    ("configuration_design", "design_path", "design_sha256"),
    ("configuration_implementation", "implementation_path", "implementation_sha256"),
    ("configuration_test", "test_path", "test_sha256"),
)
FORBIDDEN_REPORT_RELATIVE_FRAGMENTS: Final = (
    "physical_production_killing_geometry",
    "candidate_native_killing_factor_geometry",
    "/outputs/",
    "/receipts/",
)

_AFTER_SOURCE_OPEN_HOOK: Callable[[PurePosixPath, int], None] | None = None
_BEFORE_PUBLISH_HOOK: Callable[[Path], None] | None = None


class MirrorBuildError(RuntimeError):
    """Fail-closed mirror construction error."""


def _fail(message: str) -> NoReturn:
    raise MirrorBuildError(message)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _domain_digest(domain: str, value: Any) -> str:
    return _sha256(domain.encode("ascii") + b"\0" + canonical_bytes(value))


def _safe_relative(value: str | PurePosixPath, label: str) -> PurePosixPath:
    if type(value) not in {str, PurePosixPath}:
        _fail(f"{label}: path is not text")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or "\\" in str(value)
    ):
        _fail(f"{label}: unsafe report-relative path")
    return path


def _open_absolute_directory(path: Path) -> int:
    path = path.absolute()
    if not path.is_absolute():
        _fail("directory anchor is not absolute")
    flags = os.O_RDONLY | os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = -1
    try:
        fd = os.open("/", flags)
        for part in path.parts[1:]:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except OSError:
        if fd >= 0:
            os.close(fd)
        _fail(f"component-anchored directory open rejected: {path}")
    except BaseException:
        if fd >= 0:
            os.close(fd)
        raise


def _open_relative_directory(root_fd: int, parts: Sequence[str]) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.dup(root_fd)
    try:
        for part in parts:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _object_identity(value: os.stat_result) -> tuple[int, int]:
    return (value.st_dev, value.st_ino)


def _snapshot(root_fd: int, relative: PurePosixPath, *, immutable: bool) -> bytes:
    relative = _safe_relative(relative, "source")
    parent_fd = _open_relative_directory(root_fd, relative.parts[:-1])
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(relative.name, flags, dir_fd=parent_fd)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                _fail(f"{relative}: source is not a single-link regular file")
            if immutable and stat.S_IMODE(before.st_mode) != 0o444:
                _fail(f"{relative}: accepted authority is not mode 0444")
            if _AFTER_SOURCE_OPEN_HOOK is not None:
                _AFTER_SOURCE_OPEN_HOOK(relative, fd)
            chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1 << 20)
                if not chunk:
                    break
                chunks.append(chunk)
            after = os.fstat(fd)
            if _identity(before) != _identity(after):
                _fail(f"{relative}: source changed while read")
            path_after = os.stat(relative.name, dir_fd=parent_fd, follow_symlinks=False)
            if _identity(before) != _identity(path_after) or not stat.S_ISREG(path_after.st_mode):
                _fail(f"{relative}: source pathname was replaced while read")
            return b"".join(chunks)
        finally:
            os.close(fd)
    except OSError as error:
        _fail(f"{relative}: secure source open failed: {error}")
    finally:
        os.close(parent_fd)


def _decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        _fail(f"{label}: invalid ASCII JSON: {error}")
    if type(value) is not dict or canonical_bytes(value) != raw:
        _fail(f"{label}: JSON is not canonical")
    return value


def _configuration_inventory(configuration: dict[str, Any]) -> list[dict[str, Any]]:
    rows = configuration.get("configurations")
    if type(rows) is not list or len(rows) != EXPECTED_CONFIGURATION_COUNT:
        _fail("configuration: row cardinality mismatch")
    records: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if type(row) is not dict:
            _fail("configuration: row is not an object")
        records.append(
            {
                "configuration_index": index,
                "configuration_label": row.get("label"),
                "configuration_row_canonical_sha256": _sha256(canonical_bytes(row)),
                "expected_states": row.get("expected_states"),
                "shape": row.get("shape"),
            }
        )
    return records


def _partition_inventory(member: dict[str, Any]) -> list[dict[str, Any]]:
    bindings = member.get("n0_sequence_bindings")
    if type(bindings) is not list or len(bindings) != EXPECTED_CONFIGURATION_COUNT:
        _fail("member-v4: binding cardinality mismatch")
    records: list[dict[str, Any]] = []
    for index, binding in enumerate(bindings):
        if type(binding) is not dict or binding.get("configuration_index") != index:
            _fail("member-v4: binding order mismatch")
        axes = binding.get("n0_axes")
        if type(axes) is not list or len(axes) != len(COORDINATES):
            _fail("member-v4: axis cardinality mismatch")
        for coordinate, axis in zip(COORDINATES, axes, strict=True):
            if type(axis) is not dict or axis.get("coordinate") != coordinate:
                _fail("member-v4: coordinate order mismatch")
            records.append(
                {
                    "alignment": axis.get("alignment"),
                    "cell_count": axis.get("cell_count"),
                    "configuration_index": index,
                    "configuration_label": binding.get("authority_label"),
                    "coordinate": coordinate,
                    "partition_report_relative_path": axis.get("partition_report_relative_path"),
                    "partition_schema": axis.get("partition_schema"),
                    "partition_sha256": axis.get("partition_sha256"),
                    "periodic": axis.get("periodic"),
                    "refinement_family_id": binding.get("refinement_family_id"),
                    "refinement_member_id": binding.get("refinement_member_id"),
                    "sequence_id": binding.get("sequence_id"),
                }
            )
    return records


def _authority_pin(
    relative: PurePosixPath, schema: str, status: str | None, sha256: str
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "path": relative.as_posix(),
        "schema": schema,
        "sha256": sha256,
    }
    if status is not None:
        value["status"] = status
    return value


def _expected_entries(
    configuration: dict[str, Any],
    member: dict[str, Any],
    initial_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    authority = configuration.get("authority")
    if type(authority) is not dict or set(authority) != {
        "design_path",
        "design_sha256",
        "implementation_path",
        "implementation_sha256",
        "test_path",
        "test_sha256",
    }:
        _fail("configuration: authority closure mismatch")
    entries: list[dict[str, Any]] = []
    for semantic_role, path_key, sha_key in LINEAGE_ROLES:
        source = _safe_relative(authority[path_key], semantic_role)
        entries.append(
            {
                "ordinal": len(entries),
                "semantic_role": semantic_role,
                "source_report_relative_path": source.as_posix(),
                "mirror_relative_path": (PurePosixPath("files") / source).as_posix(),
                "sha256": authority[sha_key],
            }
        )
    entries.append(
        {
            "ordinal": len(entries),
            "semantic_role": "configuration_initial_geometry",
            "source_report_relative_path": INITIAL_GEOMETRY_RELATIVE.as_posix(),
            "mirror_relative_path": (PurePosixPath("files") / INITIAL_GEOMETRY_RELATIVE).as_posix(),
            "sha256": INITIAL_GEOMETRY_SHA256,
        }
    )
    inventory = initial_bundle.get("file_inventory")
    if type(inventory) is not list:
        _fail("initial bundle: file inventory missing")
    indexed_inventory: dict[str, dict[str, Any]] = {}
    for record in inventory:
        if type(record) is not dict or set(record) != {"byte_length", "path", "sha256"}:
            _fail("initial bundle: malformed file inventory")
        if record["path"] in indexed_inventory:
            _fail("initial bundle: duplicate file inventory path")
        indexed_inventory[record["path"]] = record
    analytic = indexed_inventory.get("request/analytic_source.json")
    if (
        analytic is None
        or analytic["sha256"] != INITIAL_GEOMETRY_SHA256
        or initial_bundle.get("analytic_source_sha256") != INITIAL_GEOMETRY_SHA256
    ):
        _fail("initial bundle: analytic source binding mismatch")
    entries[3]["byte_length"] = analytic["byte_length"]

    for record in _partition_inventory(member):
        source = _safe_relative(record["partition_report_relative_path"], "member partition")
        try:
            bundle_relative = source.relative_to(INITIAL_BUNDLE_DIRECTORY)
        except ValueError:
            _fail("member partition escapes initial-bundle directory")
        bundle_record = indexed_inventory.get(bundle_relative.as_posix())
        if (
            bundle_record is None
            or bundle_record["sha256"] != record["partition_sha256"]
            or record["partition_schema"] != PARTITION_SCHEMA
        ):
            _fail("member/initial-bundle partition binding mismatch")
        entries.append(
            {
                "byte_length": bundle_record["byte_length"],
                "configuration_index": record["configuration_index"],
                "configuration_label": record["configuration_label"],
                "coordinate": record["coordinate"],
                "mirror_relative_path": (PurePosixPath("files") / source).as_posix(),
                "ordinal": len(entries),
                "semantic_role": "member_v4_partition",
                "sha256": record["partition_sha256"],
                "source_report_relative_path": source.as_posix(),
            }
        )
    if len(entries) != EXPECTED_ENTRY_COUNT:
        _fail("entry cardinality mismatch")
    return entries


def _load_authorities(root_fd: int) -> tuple[dict[str, Any], ...]:
    definitions = (
        (MEMBER_RELATIVE, MEMBER_SHA256, MEMBER_SCHEMA, MEMBER_STATUS, "member-v4"),
        (
            CONFIGURATION_RELATIVE,
            CONFIGURATION_SHA256,
            CONFIGURATION_SCHEMA,
            CONFIGURATION_STATUS,
            "configuration",
        ),
        (
            FACTORIZATION_RELATIVE,
            FACTORIZATION_SHA256,
            FACTORIZATION_SCHEMA,
            FACTORIZATION_STATUS,
            "factorization-v2",
        ),
        (
            INITIAL_BUNDLE_RELATIVE,
            INITIAL_BUNDLE_SHA256,
            INITIAL_BUNDLE_SCHEMA,
            INITIAL_BUNDLE_STATUS,
            "initial bundle",
        ),
    )
    values: list[dict[str, Any]] = []
    for relative, expected_sha, schema, status, label in definitions:
        raw = _snapshot(root_fd, relative, immutable=True)
        if _sha256(raw) != expected_sha:
            _fail(f"{label}: accepted SHA-256 mismatch")
        value = _decode_canonical(raw, label)
        if value.get("schema") != schema or value.get("status") != status:
            _fail(f"{label}: schema/status mismatch")
        values.append(value)
    member, configuration, factorization, initial_bundle = values
    if member.get("member_identity_sha256") != MEMBER_IDENTITY_SHA256:
        _fail("member-v4: identity mismatch")
    if (
        configuration.get("configuration_count") != EXPECTED_CONFIGURATION_COUNT
        or initial_bundle.get("configuration_count") != EXPECTED_CONFIGURATION_COUNT
        or initial_bundle.get("configuration_sha256") != CONFIGURATION_SHA256
    ):
        _fail("configuration/initial-bundle join mismatch")
    source_pins = factorization.get("source_pins")
    expected_factorization_pins = {
        "configuration_source": (
            CONFIGURATION_RELATIVE.as_posix(),
            CONFIGURATION_SCHEMA,
            CONFIGURATION_SHA256,
        ),
        "initial_partition_bundle": (
            INITIAL_BUNDLE_RELATIVE.as_posix(),
            INITIAL_BUNDLE_SCHEMA,
            INITIAL_BUNDLE_SHA256,
        ),
    }
    if type(source_pins) is not dict:
        _fail("factorization-v2: source pins missing")
    for key, (path, schema, sha256) in expected_factorization_pins.items():
        pin = source_pins.get(key)
        if pin != {"path": path, "schema": schema, "sha256": sha256}:
            _fail(f"factorization-v2: {key} pin mismatch")
    if (
        _domain_digest(CONFIGURATION_INVENTORY_DOMAIN, _configuration_inventory(configuration))
        != CONFIGURATION_INVENTORY_SHA256
        or _domain_digest(PARTITION_INVENTORY_DOMAIN, _partition_inventory(member))
        != PARTITION_INVENTORY_SHA256
    ):
        _fail("accepted inventory digest mismatch")
    return member, configuration, factorization, initial_bundle


def _make_manifest(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "accepted_authorities": {
            "configuration": _authority_pin(
                CONFIGURATION_RELATIVE,
                CONFIGURATION_SCHEMA,
                CONFIGURATION_STATUS,
                CONFIGURATION_SHA256,
            ),
            "factorization_v2": _authority_pin(
                FACTORIZATION_RELATIVE,
                FACTORIZATION_SCHEMA,
                FACTORIZATION_STATUS,
                FACTORIZATION_SHA256,
            ),
            "initial_partition_bundle": _authority_pin(
                INITIAL_BUNDLE_RELATIVE,
                INITIAL_BUNDLE_SCHEMA,
                INITIAL_BUNDLE_STATUS,
                INITIAL_BUNDLE_SHA256,
            ),
            "member_v4": {
                **_authority_pin(MEMBER_RELATIVE, MEMBER_SCHEMA, MEMBER_STATUS, MEMBER_SHA256),
                "member_identity_sha256": MEMBER_IDENTITY_SHA256,
            },
        },
        "claim_boundary": dict.fromkeys(CLAIM_KEYS, False),
        "coverage": {
            "configuration_authority_lineage_file_count": 3,
            "configuration_initial_geometry_file_count": 1,
            "exact_writable_precommit_input_closure_mirrored": True,
            "member_v4_partition_file_count": EXPECTED_PARTITION_COUNT,
            "original_report_relative_suffix_preserved_under_files": True,
            "standalone_content_addressed_validation_without_original_writable_sources": True,
        },
        "entry_count": EXPECTED_ENTRY_COUNT,
        "entries": entries,
        "exclusions": {
            "external_commitment_not_created": True,
            "legacy_role10_result_and_output_bytes_excluded": True,
            "numerical_execution_results_excluded": True,
            "replay_requests_plans_bundles_and_commitments_excluded": True,
            "role8_and_role9_outputs_excluded": True,
        },
        "inventory_digests": {
            "configuration_row_inventory": {
                "domain": CONFIGURATION_INVENTORY_DOMAIN,
                "sha256": CONFIGURATION_INVENTORY_SHA256,
            },
            "member_v4_partition_inventory": {
                "domain": PARTITION_INVENTORY_DOMAIN,
                "sha256": PARTITION_INVENTORY_SHA256,
            },
        },
        "mirrored_source_pin": {
            "path": INITIAL_GEOMETRY_RELATIVE.as_posix(),
            "schema": INITIAL_GEOMETRY_SCHEMA,
            "sha256": INITIAL_GEOMETRY_SHA256,
        },
        "schema": SCHEMA,
        "status": STATUS,
    }


def _mkdir_chain(root_fd: int, parts: Sequence[str]) -> None:
    fd = os.dup(root_fd)
    flags = os.O_RDONLY | os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        for part in parts:
            try:
                os.mkdir(part, 0o700, dir_fd=fd)
            except FileExistsError:
                pass
            child = os.open(part, flags, dir_fd=fd)
            mode = os.fstat(child).st_mode
            if not stat.S_ISDIR(mode) or stat.S_IMODE(mode) != 0o700:
                os.close(child)
                _fail("staging directory mode/type mismatch")
            os.close(fd)
            fd = child
    finally:
        os.close(fd)


def _write_staged_file(root_fd: int, relative: PurePosixPath, raw: bytes) -> None:
    relative = _safe_relative(relative, "staged file")
    _mkdir_chain(root_fd, relative.parts[:-1])
    parent_fd = _open_relative_directory(root_fd, relative.parts[:-1])
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(relative.name, flags, 0o600, dir_fd=parent_fd)
        try:
            view = memoryview(raw)
            while view:
                written = os.write(fd, view)
                view = view[written:]
            os.fsync(fd)
            os.fchmod(fd, 0o444)
            os.fsync(fd)
        finally:
            os.close(fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def _seal_directories(root_fd: int, relative_directories: set[PurePosixPath]) -> None:
    ordered = sorted(relative_directories, key=lambda item: len(item.parts), reverse=True)
    for relative in ordered:
        fd = _open_relative_directory(root_fd, relative.parts)
        try:
            os.fchmod(fd, 0o555)
            os.fsync(fd)
        finally:
            os.close(fd)
    os.fchmod(root_fd, 0o555)
    os.fsync(root_fd)


def _rename_noreplace(parent_fd: int, source: str, destination: str) -> None:
    try:
        libc = ctypes.CDLL(None, use_errno=True)
    except OSError:
        _fail("atomic no-replace rename primitive unavailable")
    encoded_source = os.fsencode(source)
    encoded_destination = os.fsencode(destination)
    if hasattr(libc, "renameat2"):
        result = libc.renameat2(
            parent_fd,
            ctypes.c_char_p(encoded_source),
            parent_fd,
            ctypes.c_char_p(encoded_destination),
            1,
        )
    elif hasattr(libc, "renameatx_np"):
        result = libc.renameatx_np(
            parent_fd,
            ctypes.c_char_p(encoded_source),
            parent_fd,
            ctypes.c_char_p(encoded_destination),
            0x00000004,
        )
    else:
        _fail("atomic no-replace rename primitive unavailable")
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number), destination)


def _clear_owned_directory(directory_fd: int) -> None:
    """Remove contents through an already authenticated owned-directory fd."""

    value = os.fstat(directory_fd)
    if not stat.S_ISDIR(value.st_mode):
        _fail("owned rollback root is not a directory")
    os.fchmod(directory_fd, 0o700)
    for name in sorted(os.listdir(directory_fd)):
        try:
            before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            continue
        if stat.S_ISDIR(before.st_mode):
            flags = os.O_RDONLY | os.O_DIRECTORY
            if hasattr(os, "O_CLOEXEC"):
                flags |= os.O_CLOEXEC
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            try:
                child_fd = os.open(name, flags, dir_fd=directory_fd)
            except FileNotFoundError:
                continue
            try:
                if _object_identity(os.fstat(child_fd)) != _object_identity(before):
                    continue
                _clear_owned_directory(child_fd)
            finally:
                os.close(child_fd)
            try:
                current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            if stat.S_ISDIR(current.st_mode) and _object_identity(current) == _object_identity(
                before
            ):
                os.rmdir(name, dir_fd=directory_fd)
        else:
            try:
                current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            if _object_identity(current) == _object_identity(before):
                os.unlink(name, dir_fd=directory_fd)
    os.fsync(directory_fd)


def _remove_owned_directory_at_name(
    parent_fd: int,
    name: str,
    owned_identity: tuple[int, int],
) -> bool:
    """Remove one directory only when its current inode is invocation-owned."""

    try:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if not stat.S_ISDIR(before.st_mode) or _object_identity(before) != owned_identity:
        return False
    flags = os.O_RDONLY | os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        root_fd = os.open(name, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        return False
    try:
        if _object_identity(os.fstat(root_fd)) != owned_identity:
            return False
        _clear_owned_directory(root_fd)
    finally:
        os.close(root_fd)
    try:
        current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if stat.S_ISDIR(current.st_mode) and _object_identity(current) == owned_identity:
        os.rmdir(name, dir_fd=parent_fd)
        os.fsync(parent_fd)
        return True
    return False


def _parent_anchor_matches(
    parent_fd: int,
    parent_identity: tuple[int, int],
) -> bool:
    value = os.fstat(parent_fd)
    return stat.S_ISDIR(value.st_mode) and _object_identity(value) == parent_identity


def _require_parent_path_current(
    parent_path: Path,
    parent_fd: int,
    parent_identity: tuple[int, int],
    phase: str,
) -> None:
    """Require the no-symlink pathname image to remain the opened parent."""

    if not _parent_anchor_matches(parent_fd, parent_identity):
        _fail(f"publication parent descriptor changed {phase}")
    current_fd = _open_absolute_directory(parent_path)
    try:
        current = os.fstat(current_fd)
        if not stat.S_ISDIR(current.st_mode) or _object_identity(current) != parent_identity:
            _fail(f"publication parent pathname was rebound {phase}")
    finally:
        os.close(current_fd)
    if not _parent_anchor_matches(parent_fd, parent_identity):
        _fail(f"publication parent descriptor changed {phase}")


def _rollback_owned_publication(
    parent_fd: int,
    parent_identity: tuple[int, int],
    owned_identity: tuple[int, int],
) -> None:
    """Delete only the invocation-owned root, wherever it sits in the parent."""

    if not _parent_anchor_matches(parent_fd, parent_identity):
        _fail("publication parent anchor changed before rollback")
    for _attempt in range(3):
        matching_names: list[str] = []
        for name in sorted(os.listdir(parent_fd)):
            try:
                value = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            if stat.S_ISDIR(value.st_mode) and _object_identity(value) == owned_identity:
                matching_names.append(name)
        if not matching_names:
            break
        for name in matching_names:
            _remove_owned_directory_at_name(parent_fd, name, owned_identity)
    if not _parent_anchor_matches(parent_fd, parent_identity):
        _fail("publication parent anchor changed during rollback")
    for name in os.listdir(parent_fd):
        try:
            value = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            continue
        if stat.S_ISDIR(value.st_mode) and _object_identity(value) == owned_identity:
            _fail("owned publication rollback incomplete")


def _acknowledge(
    parent_fd: int,
    output_name: str,
    owned_identity: tuple[int, int],
    entries: list[dict[str, Any]],
    manifest_raw: bytes,
) -> None:
    flags = os.O_RDONLY | os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        root_fd = os.open(output_name, flags, dir_fd=parent_fd)
    except OSError:
        _fail("published root unavailable during acknowledgement")
    try:
        root_value = os.fstat(root_fd)
        if (
            _object_identity(root_value) != owned_identity
            or stat.S_IMODE(root_value.st_mode) != 0o555
        ):
            _fail("published root is not mode 0555")
        manifest = _snapshot(root_fd, PurePosixPath("manifest.json"), immutable=True)
        if manifest != manifest_raw:
            _fail("published manifest acknowledgement mismatch")
        for entry in entries:
            raw = _snapshot(root_fd, PurePosixPath(entry["mirror_relative_path"]), immutable=True)
            if len(raw) != entry["byte_length"] or _sha256(raw) != entry["sha256"]:
                _fail("published entry acknowledgement mismatch")
    finally:
        os.close(root_fd)
    try:
        final_value = os.stat(output_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        _fail("published root pathname disappeared during acknowledgement")
    if not stat.S_ISDIR(final_value.st_mode) or _object_identity(final_value) != owned_identity:
        _fail("published root pathname was replaced during acknowledgement")


def build_mirror(source_root: Path, output: Path) -> dict[str, Any]:
    """Build and publish one immutable mirror directory without replacement."""

    source_root = source_root.absolute()
    output = output.absolute()
    if output.name in {"", ".", ".."} or output.parent == output:
        _fail("unsafe output root")
    source_fd = _open_absolute_directory(source_root)
    try:
        member, configuration, _factorization, initial_bundle = _load_authorities(source_fd)
        entries = _expected_entries(configuration, member, initial_bundle)
        for entry in entries:
            source_relative = _safe_relative(entry["source_report_relative_path"], "entry source")
            if any(
                fragment in f"/{source_relative.as_posix()}/"
                for fragment in FORBIDDEN_REPORT_RELATIVE_FRAGMENTS
            ):
                _fail("forbidden legacy/output path entered the mirror")
            raw = _snapshot(source_fd, source_relative, immutable=False)
            if _sha256(raw) != entry["sha256"]:
                _fail(f"{source_relative}: accepted source SHA-256 mismatch")
            if "byte_length" in entry and len(raw) != entry["byte_length"]:
                _fail(f"{source_relative}: accepted source byte length mismatch")
            entry["byte_length"] = len(raw)
            entry["_raw"] = raw
        manifest_entries = [
            {key: value for key, value in entry.items() if key != "_raw"} for entry in entries
        ]
        manifest = _make_manifest(manifest_entries)
        manifest_raw = canonical_bytes(manifest)
    finally:
        os.close(source_fd)

    parent_fd = _open_absolute_directory(output.parent)
    parent_value = os.fstat(parent_fd)
    parent_mode = stat.S_IMODE(parent_value.st_mode)
    if parent_mode & 0o022:
        os.close(parent_fd)
        _fail("publication parent is group/other writable")
    parent_identity = _object_identity(parent_value)
    stage_name = f".{output.name}.stage-{os.getpid()}-{uuid.uuid4().hex}"
    owned_fd = -1
    owned_identity: tuple[int, int] | None = None
    try:
        try:
            os.stat(output.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            _fail("publication destination already exists")
        os.mkdir(stage_name, 0o700, dir_fd=parent_fd)
        owned_fd = os.open(
            stage_name,
            os.O_RDONLY
            | os.O_DIRECTORY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        owned_identity = _object_identity(os.fstat(owned_fd))
        directories: set[PurePosixPath] = set()
        _write_staged_file(owned_fd, PurePosixPath("manifest.json"), manifest_raw)
        for entry in entries:
            mirror_relative = PurePosixPath(entry["mirror_relative_path"])
            _write_staged_file(owned_fd, mirror_relative, entry["_raw"])
            parent = mirror_relative.parent
            while parent != PurePosixPath("."):
                directories.add(parent)
                parent = parent.parent
        _seal_directories(owned_fd, directories)
        if _BEFORE_PUBLISH_HOOK is not None:
            _BEFORE_PUBLISH_HOOK(output)
        _require_parent_path_current(
            output.parent,
            parent_fd,
            parent_identity,
            "before publication",
        )
        _rename_noreplace(parent_fd, stage_name, output.name)
        os.fsync(parent_fd)
        _require_parent_path_current(
            output.parent,
            parent_fd,
            parent_identity,
            "after publication",
        )
        _acknowledge(
            parent_fd,
            output.name,
            owned_identity,
            manifest_entries,
            manifest_raw,
        )
        _require_parent_path_current(
            output.parent,
            parent_fd,
            parent_identity,
            "after acknowledgement",
        )
        return manifest
    except FileExistsError as error:
        if owned_identity is not None:
            _rollback_owned_publication(parent_fd, parent_identity, owned_identity)
        _fail(f"publication destination appeared concurrently: {error}")
    except BaseException:
        if owned_identity is not None:
            _rollback_owned_publication(parent_fd, parent_identity, owned_identity)
        raise
    finally:
        if owned_fd >= 0:
            os.close(owned_fd)
        os.close(parent_fd)


def _parse_cli(argv: Sequence[str] | None = None) -> tuple[Path, Path]:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--source-root", default=str(REPORT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    arguments = parser.parse_args(argv)
    source_root = Path(arguments.source_root)
    output = Path(arguments.output)
    if not source_root.is_absolute() or not output.is_absolute():
        _fail("CLI paths must be absolute")
    return source_root, output


def main(argv: Sequence[str] | None = None) -> int:
    try:
        source_root, output = _parse_cli(argv)
        manifest = build_mirror(source_root, output)
    except MirrorBuildError as error:
        print(f"HOLD_ROLE10_SEALED_AUTHENTICATION_MIRROR_BUILD: {error}", file=sys.stderr)
        return 2
    print(
        "PASS_ROLE10_SEALED_AUTHENTICATION_MIRROR_CANDIDATE "
        f"entries={manifest['entry_count']} output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
