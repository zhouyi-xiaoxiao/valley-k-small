"""Validate the result-blind roles 8--10 plan-v2 precommit package.

The validator is independent of every producer and of the operation-model
builder.  It authenticates the frozen operation model plus the bytes and
static joins of a runtime-closure manifest, replay plan, and candidate bundle;
it never creates requests, commitments, numerical outputs, or receipts.
Passing this structural gate is necessary but is not evidence that the pinned
host/runtime identities are true, that the future role-v3 numerical
entrypoints are scientifically complete, or that an external predecessor has
committed.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import stat
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any, Final, NoReturn, Sequence


def _load_sealed_protocol_constants() -> ModuleType:
    path = Path(__file__).with_name("continuum_c1_n0_roles_8_10_protocol_constants_v2.py")
    expected_sha256 = "4f0dbf1a243a9157f11176b89a3b27833cf6ccc76230cf976a1a985cbb178b15"
    try:
        before = path.lstat()
        if (
            stat.S_ISLNK(before.st_mode)
            or not stat.S_ISREG(before.st_mode)
            or stat.S_IMODE(before.st_mode) != 0o444
            or before.st_nlink != 1
        ):
            raise RuntimeError("protocol constants are not a sealed mode-0444 single-link file")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            opened = os.fstat(descriptor)
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1 << 20)
                if not chunk:
                    break
                chunks.append(chunk)
            after_open = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        after_path = path.lstat()
    except OSError as error:
        raise RuntimeError(f"cannot authenticate protocol constants: {error}") from error
    identities = {
        (
            metadata.st_dev,
            metadata.st_ino,
            metadata.st_mode,
            metadata.st_nlink,
            metadata.st_size,
            metadata.st_mtime_ns,
            metadata.st_ctime_ns,
        )
        for metadata in (before, opened, after_open, after_path)
    }
    if len(identities) != 1:
        raise RuntimeError("protocol constants changed while authenticating")
    raw = b"".join(chunks)
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise RuntimeError("protocol constants SHA-256 mismatch")
    module = ModuleType("_sealed_encounter_roles_8_10_protocol_constants_v2")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


protocol = _load_sealed_protocol_constants()

HOLD: Final = "HOLD_CONTINUUM_C1_N0_PRECOMMIT_PACKAGE_V2"
PASS_SCHEMA: Final = "encounter_continuum_c1_n0_precommit_package_v2_validation_ack_v1"
PASS_STATUS: Final = (
    "PASS_RESULT_BLIND_PRECOMMIT_PACKAGE_V2_STATIC_STRUCTURE_ONLY_NO_EXECUTION_RESULTS"
)
MAX_JSON_BYTES: Final = 2_097_152
MAX_FILE_BYTES: Final = 67_108_864
MAX_SOURCE_BYTES: Final = 8_000_000
MAX_JSON_DEPTH: Final = 96
MAX_INTEGER_BITS: Final = 65_536
_SHA_RE: Final = re.compile(r"[0-9a-f]{64}\Z")
_IMPORT_RE: Final = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
_RESOLVED_DEPENDENCY_KEYS: Final = ("import_name", "origin_kind", "path", "sha256")
_NATIVE_LIBRARY_KEYS: Final = ("path", "role", "sha256")
_NATIVE_RUNTIME_KEYS: Final = (
    "gmp",
    "gmpy2",
    "mpc",
    "mpfr",
    "python_abi",
    "python_version",
)
_PYTHON_IDENTITY_KEYS: Final = ("python_abi", "python_version")
_ORIGIN_KINDS: Final = {
    "builtin",
    "frozen",
    "file_report_local",
    "file_runtime_prefix",
    "numerical_native_extension",
}


class ProtocolFailure(RuntimeError):
    """A fail-closed plan-v2 protocol rejection."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"{HOLD}: {detail}")
        self.detail = detail


@dataclass(frozen=True)
class FileImage:
    path: Path
    raw: bytes
    sha256: str
    document: dict[str, Any] | None = None


@dataclass(frozen=True)
class RuntimeInfo:
    image: FileImage
    document: dict[str, Any]
    role_records: dict[int, dict[str, Any]]
    source_paths: frozenset[Path]
    source_digests: frozenset[str]
    all_input_paths: frozenset[Path]


@dataclass(frozen=True)
class PlanInfo:
    image: FileImage
    document: dict[str, Any]
    member_image: FileImage
    registry_image: FileImage
    shared_context: dict[str, Any]
    slot_paths: dict[str, Path]
    all_input_paths: frozenset[Path]


def _fail(detail: str) -> NoReturn:
    raise ProtocolFailure(detail)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    _validate_json_tree(value)
    try:
        text = json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            indent=2,
            separators=(",", ": "),
        )
        return (text + "\n").encode("ascii")
    except (TypeError, UnicodeError, ValueError) as error:
        _fail(f"value is not canonical ASCII JSON: {error}")


def _duplicate_rejector(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            _fail("duplicate or invalid JSON object key")
        result[key] = value
    return result


def _reject_float(token: str) -> NoReturn:
    _fail(f"JSON floating literal forbidden: {token}")


def _reject_constant(token: str) -> NoReturn:
    _fail(f"JSON nonfinite literal forbidden: {token}")


def _validate_json_tree(value: Any, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        _fail("JSON depth cap exceeded")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if value.bit_length() > MAX_INTEGER_BITS:
            _fail("JSON integer bit cap exceeded")
        return
    if type(value) is float:
        _fail("JSON float object forbidden")
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            _fail("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _validate_json_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                _fail("invalid JSON object key")
            _validate_json_tree(item, depth + 1)
        return
    _fail(f"unsupported JSON value type: {type(value).__name__}")


def _decode_json(raw: bytes, label: str) -> dict[str, Any]:
    if len(raw) > MAX_JSON_BYTES:
        _fail(f"{label}: JSON byte cap exceeded")
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_duplicate_rejector,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except ProtocolFailure:
        raise
    except (UnicodeError, json.JSONDecodeError) as error:
        _fail(f"{label}: invalid ASCII JSON: {error}")
    if type(value) is not dict:
        _fail(f"{label}: top-level JSON object required")
    _validate_json_tree(value)
    if canonical_bytes(value) != raw:
        _fail(f"{label}: noncanonical JSON bytes")
    return value


def _exact_keys(value: Any, expected: Sequence[str], label: str) -> dict[str, Any]:
    if type(value) is not dict:
        _fail(f"{label}: object required")
    if set(value) != set(expected):
        missing = sorted(set(expected) - set(value))
        extra = sorted(set(value) - set(expected))
        _fail(f"{label}: exact-key mismatch missing={missing} extra={extra}")
    return value


def _strict_equal(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return set(actual) == set(expected) and all(
            _strict_equal(actual[key], expected[key]) for key in expected
        )
    if type(expected) in {list, tuple}:
        return len(actual) == len(expected) and all(
            _strict_equal(left, right) for left, right in zip(actual, expected, strict=True)
        )
    return actual == expected


def _valid_sha(value: Any) -> bool:
    return type(value) is str and _SHA_RE.fullmatch(value) is not None


def _ascii_nonempty(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        _fail(f"{label}: nonempty string required")
    try:
        value.encode("ascii")
    except UnicodeError:
        _fail(f"{label}: ASCII string required")
    return value


def _canonical_absolute(value: Any, label: str) -> Path:
    if type(value) is not str or not value or "\x00" in value:
        _fail(f"{label}: absolute path string required")
    path = Path(value)
    if (
        value.startswith("//")
        or path.anchor != "/"
        or not path.is_absolute()
        or os.path.normpath(value) != value
        or str(path) != value
    ):
        _fail(f"{label}: canonical absolute path required")
    cursor = Path(path.anchor)
    for component in path.parts[1:]:
        cursor /= component
        try:
            metadata = cursor.lstat()
        except FileNotFoundError:
            break
        except OSError as error:
            _fail(f"{label}: cannot inspect path component {cursor}: {error}")
        if stat.S_ISLNK(metadata.st_mode):
            _fail(f"{label}: symlink path component forbidden: {cursor}")
    return path


def _relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _lexically_disjoint(left: Path, right: Path) -> bool:
    return not _relative_to(left, right) and not _relative_to(right, left)


def _stat_identity(metadata: os.stat_result) -> tuple[int, ...]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_uid,
        metadata.st_gid,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _directory_identity(metadata: os.stat_result) -> tuple[int, ...]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_uid,
        metadata.st_gid,
    )


def _open_directory_chain(directory: Path, label: str) -> tuple[list[int], list[tuple[int, ...]]]:
    if not directory.is_absolute():
        _fail(f"{label}: anchored directory must be absolute")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    identities: list[tuple[int, ...]] = []
    try:
        root = os.open("/", flags)
        descriptors.append(root)
        identities.append(_directory_identity(os.fstat(root)))
        for component in directory.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptors[-1])
            metadata = os.fstat(child)
            if not stat.S_ISDIR(metadata.st_mode):
                os.close(child)
                _fail(f"{label}: non-directory path component: {component}")
            descriptors.append(child)
            identities.append(_directory_identity(metadata))
    except (OSError, ProtocolFailure) as error:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        if isinstance(error, ProtocolFailure):
            raise
        _fail(f"{label}: cannot open anchored directory chain: {error}")
    return descriptors, identities


def _close_descriptors(descriptors: Sequence[int]) -> None:
    for descriptor in reversed(descriptors):
        try:
            os.close(descriptor)
        except OSError:
            pass


def _read_file_anchored(
    path: Path,
    label: str,
    parent_descriptors: Sequence[int],
    parent_identities: Sequence[tuple[int, ...]],
    *,
    require_immutable: bool,
    expected_mode: int | None,
) -> FileImage:
    try:
        before = os.stat(path.name, dir_fd=parent_descriptors[-1], follow_symlinks=False)
    except OSError as error:
        _fail(f"{label}: cannot stat {path}: {error}")
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        _fail(f"{label}: regular non-symlink file required: {path}")
    if before.st_nlink != 1:
        _fail(f"{label}: single-link file required: {path}")
    if require_immutable and before.st_mode & 0o222:
        _fail(f"{label}: read-only file required: {path}")
    if expected_mode is not None and stat.S_IMODE(before.st_mode) != expected_mode:
        _fail(f"{label}: exact mode {expected_mode:04o} required: {path}")

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path.name, flags, dir_fd=parent_descriptors[-1])
    except OSError as error:
        _fail(f"{label}: cannot open {path}: {error}")
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            _fail(f"{label}: file identity changed before read: {path}")
        chunks: list[bytes] = []
        size = 0
        while True:
            chunk = os.read(descriptor, 1 << 20)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_FILE_BYTES:
                _fail(f"{label}: file byte cap exceeded: {path}")
            chunks.append(chunk)
        after_open = os.fstat(descriptor)
    finally:
        os.close(descriptor)

    try:
        after_path = os.stat(path.name, dir_fd=parent_descriptors[-1], follow_symlinks=False)
    except OSError as error:
        _fail(f"{label}: cannot restat {path}: {error}")
    for descriptor, expected_identity in zip(parent_descriptors, parent_identities, strict=True):
        if _directory_identity(os.fstat(descriptor)) != expected_identity:
            _fail(f"{label}: anchored parent changed while reading: {path}")

    rebound_descriptors, rebound_identities = _open_directory_chain(path.parent, label)
    try:
        try:
            rebound_path = os.stat(path.name, dir_fd=rebound_descriptors[-1], follow_symlinks=False)
        except OSError as error:
            _fail(f"{label}: cannot rebind anchored path {path}: {error}")
        if list(rebound_identities) != list(parent_identities):
            _fail(f"{label}: anchored parent path was replaced: {path}")
    finally:
        _close_descriptors(rebound_descriptors)

    identities = {
        _stat_identity(before),
        _stat_identity(opened),
        _stat_identity(after_open),
        _stat_identity(after_path),
        _stat_identity(rebound_path),
    }
    if len(identities) != 1:
        _fail(f"{label}: file changed while reading: {path}")
    raw = b"".join(chunks)
    if len(raw) != before.st_size:
        _fail(f"{label}: short or growing read: {path}")
    return FileImage(path=path, raw=raw, sha256=_sha256(raw))


def _read_file(
    path: Path,
    label: str,
    *,
    require_immutable: bool = True,
    expected_mode: int | None = None,
) -> FileImage:
    parent_descriptors, parent_identities = _open_directory_chain(path.parent, label)
    try:
        return _read_file_anchored(
            path,
            label,
            parent_descriptors,
            parent_identities,
            require_immutable=require_immutable,
            expected_mode=expected_mode,
        )
    finally:
        _close_descriptors(parent_descriptors)


def _read_json_file(path: Path, label: str) -> FileImage:
    image = _read_file(path, label, expected_mode=0o444)
    document = _decode_json(image.raw, label)
    return FileImage(path=image.path, raw=image.raw, sha256=image.sha256, document=document)


def _plain_pin(value: Any, label: str, *, expected_mode: int = 0o444) -> FileImage:
    pin = _exact_keys(value, protocol.PIN_EXACT_KEYS, label)
    path = _canonical_absolute(pin["path"], f"{label}.path")
    if not _valid_sha(pin["sha256"]):
        _fail(f"{label}: lowercase SHA-256 required")
    image = _read_file(path, label, expected_mode=expected_mode)
    if image.sha256 != pin["sha256"]:
        _fail(f"{label}: SHA-256 mismatch")
    return image


def _schema_pin(value: Any, expected_schema: str, label: str) -> FileImage:
    pin = _exact_keys(value, protocol.SCHEMA_PIN_EXACT_KEYS, label)
    if pin["schema"] != expected_schema:
        _fail(f"{label}: schema pin mismatch")
    path = _canonical_absolute(pin["path"], f"{label}.path")
    if not _valid_sha(pin["sha256"]):
        _fail(f"{label}: lowercase SHA-256 required")
    image = _read_json_file(path, label)
    if image.sha256 != pin["sha256"]:
        _fail(f"{label}: SHA-256 mismatch")
    assert image.document is not None
    if image.document.get("schema") != expected_schema:
        _fail(f"{label}: opened document schema mismatch")
    return image


def _pin_object(image: FileImage, *, schema: str | None = None) -> dict[str, str]:
    result = {"path": str(image.path), "sha256": image.sha256}
    if schema is not None:
        result["schema"] = schema
    return result


def _report_root_from_operation_model(path: Path) -> Path:
    expected_suffix = PurePosixPath(protocol.OPERATION_MODEL_REPORT_RELATIVE_PATH).parts
    if tuple(path.parts[-len(expected_suffix) :]) != expected_suffix:
        _fail("operation model path does not have the frozen report-relative suffix")
    return Path(*path.parts[: -len(expected_suffix)])


def _jsonish(value: Any) -> Any:
    if type(value) is tuple:
        return [_jsonish(item) for item in value]
    if type(value) is list:
        return [_jsonish(item) for item in value]
    if type(value) is dict:
        return {str(key): _jsonish(item) for key, item in value.items()}
    return value


def _assert_protocol_constants_join_model(model: dict[str, Any]) -> None:
    replay = model["replay_plan_contract"]
    entry = replay["entry_contract"]
    runtime = replay["runtime_closure"]
    objects = replay["objects"]
    bundle = replay["candidate_bundle_contract"]
    request = replay["request_contract"]
    shared = replay["shared_context_contract"]
    runner = replay["global_replay_runner_contract"]

    joins: list[tuple[Any, Any, str]] = [
        (entry["exact_keys"], list(protocol.ENTRY_EXACT_KEYS), "entry exact keys"),
        (
            entry["authority_schema_by_key"],
            protocol.AUTHORITY_SCHEMAS,
            "authority schemas",
        ),
        (entry["catalog_order"], list(protocol.ROLE_ORDER), "entry role order"),
        (
            entry["method_parameter_ids_by_role"],
            _jsonish(protocol.METHOD_PARAMETER_IDS),
            "method parameter IDs",
        ),
        (
            entry["normative_input_authority_keys_by_role"],
            _jsonish(protocol.NORMATIVE_INPUT_AUTHORITY_KEYS),
            "normative authority keys",
        ),
        (
            entry["source_version_identity_by_role"],
            _jsonish(protocol.SOURCE_BASENAMES),
            "v3 source basenames",
        ),
        (
            entry["invocation_templates_by_role"],
            _jsonish(protocol.INVOCATION_TEMPLATES),
            "invocation templates",
        ),
        (runtime["exact_keys"], list(protocol.RUNTIME_EXACT_KEYS), "runtime exact keys"),
        (
            runtime["claim_boundary"],
            protocol.RUNTIME_CLAIM_BOUNDARY,
            "runtime claim boundary",
        ),
        (runtime["role_order"], list(protocol.ROLE_ORDER), "runtime role order"),
        (
            runtime["role_exact_keys"],
            list(protocol.RUNTIME_ROLE_EXACT_KEYS),
            "runtime role exact keys",
        ),
        (
            objects["runtime_code_inputs"]["exact_keys"],
            list(protocol.RUNTIME_CODE_INPUT_EXACT_KEYS),
            "runtime code-input keys",
        ),
        (
            objects["runtime_python_imports"]["exact_keys"],
            list(protocol.RUNTIME_SIDE_EXACT_KEYS),
            "runtime side keys",
        ),
        (
            objects["runtime_native_library"]["exact_keys"],
            list(_NATIVE_LIBRARY_KEYS),
            "native library keys",
        ),
        (
            runtime["role_field_schemas"]["native_libraries"]["order"],
            list(protocol.NATIVE_LIBRARY_ROLES),
            "native library roles",
        ),
        (
            objects["runtime_native_runtime"]["exact_keys"],
            list(_NATIVE_RUNTIME_KEYS),
            "native runtime keys",
        ),
        (
            objects["runtime_python_identity"]["exact_keys"],
            list(_PYTHON_IDENTITY_KEYS),
            "Python identity keys",
        ),
        (
            objects["resolved_python_dependency"]["exact_keys"],
            list(_RESOLVED_DEPENDENCY_KEYS),
            "resolved dependency keys",
        ),
        (
            objects["runtime_global_runner"]["exact_keys"],
            list(protocol.GLOBAL_RUNNER_EXACT_KEYS),
            "global runner exact keys",
        ),
        (
            objects["runtime_host_trust_boundary"]["exact_keys"],
            list(protocol.HOST_RUNTIME_EXACT_KEYS),
            "host trust-boundary keys",
        ),
        (
            objects["runtime_host_trust_boundary"]["field_schemas"]["scope"]["exact_order"],
            list(protocol.HOST_RUNTIME_SCOPE),
            "host trust-boundary scope",
        ),
        (
            objects["invocation"]["exact_keys"],
            list(protocol.INVOCATION_EXACT_KEYS),
            "invocation keys",
        ),
        (
            objects["replay_partition_binding"]["exact_keys"],
            list(protocol.PARTITION_BINDING_EXACT_KEYS),
            "partition binding keys",
        ),
        (replay["slot_object_contract"]["exact_keys"], list(protocol.SLOT_EXACT_KEYS), "slot keys"),
        (
            [
                {key: value for key, value in slot.items() if key != "path_field"}
                for slot in replay["slot_templates"]
            ],
            _jsonish(protocol.SLOT_TEMPLATES),
            "slot templates",
        ),
        (bundle["schema"], protocol.BUNDLE_SCHEMA, "bundle schema"),
        (bundle["status"], protocol.BUNDLE_STATUS, "bundle status"),
        (bundle["exact_keys"], list(protocol.BUNDLE_EXACT_KEYS), "bundle exact keys"),
        (bundle["claim_boundary"], protocol.PLAN_CLAIM_BOUNDARY, "bundle claim boundary"),
        (request["exact_keys"], list(protocol.REQUEST_EXACT_KEYS), "request exact keys"),
        (request["schemas_by_role"], _jsonish(protocol.REQUEST_SCHEMAS), "request schemas"),
        (request["status"], protocol.REQUEST_STATUS, "request status"),
        (
            objects["request_role"]["exact_keys"],
            list(protocol.REQUEST_ROLE_EXACT_KEYS),
            "request role keys",
        ),
        (shared["exact_keys"], list(protocol.SHARED_CONTEXT_EXACT_KEYS), "shared keys"),
        (runner["entrypoint_basename"], protocol.GLOBAL_RUNNER_BASENAME, "runner basename"),
        (runner["runner_id"], protocol.GLOBAL_RUNNER_ID, "runner ID"),
        (
            model["resource_caps"]["maximum_json_file_bytes"],
            MAX_JSON_BYTES,
            "maximum JSON bytes",
        ),
        (
            model["resource_caps"]["maximum_tree_total_bytes"],
            MAX_FILE_BYTES,
            "maximum generic file bytes",
        ),
    ]
    for role_id in protocol.ROLE_ORDER:
        role_key = str(role_id)
        joins.extend(
            [
                (
                    runtime["role_values"][role_key]["role_id"],
                    role_id,
                    f"runtime role {role_id} ID",
                ),
                (
                    runtime["role_values"][role_key]["role_name"],
                    protocol.ROLE_NAMES[role_id],
                    f"runtime role {role_id} name",
                ),
                (
                    entry["values_by_role"][role_key]["entry_id"],
                    protocol.ROLE_NAMES[role_id],
                    f"entry role {role_id} name",
                ),
                (
                    entry["values_by_role"][role_key]["request_slot_id"],
                    protocol.REQUEST_SLOT_IDS[role_id],
                    f"entry role {role_id} request slot",
                ),
                (
                    entry["values_by_role"][role_key]["output_slot_ids"],
                    list(protocol.OUTPUT_SLOT_IDS[role_id]),
                    f"entry role {role_id} output slots",
                ),
            ]
        )
    for key in (
        "anti_vacuity_policy",
        "configuration",
        "factorization",
        "ideal_formula",
        "member_spec",
        "method_parameter_registry",
        "reference_density",
    ):
        joins.append(
            (
                shared["field_schemas"][key]["expected_schema"],
                protocol.AUTHORITY_SCHEMAS[key],
                f"shared authority schema {key}",
            )
        )
    joins.extend(
        [
            (
                shared["field_schemas"]["role10_operation_model"]["expected_schema"],
                protocol.OPERATION_MODEL_SCHEMA,
                "shared operation-model schema",
            ),
            (
                shared["field_schemas"]["member_identity_sha256"],
                f"literal_{protocol.MEMBER_IDENTITY_SHA256}",
                "member identity digest",
            ),
            (
                shared["field_schemas"]["configuration_row_inventory_sha256"],
                f"literal_{protocol.CONFIGURATION_ROW_INVENTORY_SHA256}",
                "configuration inventory digest",
            ),
            (
                shared["field_schemas"]["partition_inventory_sha256"],
                f"literal_{protocol.PARTITION_INVENTORY_SHA256}",
                "partition inventory digest",
            ),
            (
                replay["pin_schemas"]["pin"]["exact_keys"],
                list(protocol.PIN_EXACT_KEYS),
                "pin exact keys",
            ),
            (
                replay["pin_schemas"]["schema_pin"]["exact_keys"],
                list(protocol.SCHEMA_PIN_EXACT_KEYS),
                "schema-pin exact keys",
            ),
            (
                replay["canonical_digest_framing"]["entry_projection"],
                f"domain_{protocol.ENTRY_PROJECTION_DOMAIN}+NUL+uint64be_byte_length+"
                "canonical_entry_with_only_precommit_projection_sha256_omitted",
                "entry projection domain",
            ),
            (
                replay["canonical_digest_framing"]["shared_precommit_context"],
                f"domain_{protocol.SHARED_PRECOMMIT_DOMAIN}+NUL+canonical_shared_context_"
                "bytes_with_no_length_prefix",
                "shared precommit domain",
            ),
            (
                request["shared_replay_preimage"]["domain"],
                protocol.SHARED_REPLAY_DOMAIN,
                "shared replay domain",
            ),
        ]
    )
    for actual, expected, label in joins:
        if not _strict_equal(actual, expected):
            _fail(f"operation model/constants join drift: {label}")


def _assert_known_operation_model(path: Path) -> tuple[FileImage, Path]:
    image = _read_json_file(path, "operation model v2")
    if image.sha256 != protocol.OPERATION_MODEL_SHA256:
        _fail("operation model v2 is not the frozen ac0c artifact")
    assert image.document is not None
    model = image.document
    if (
        model.get("schema") != protocol.OPERATION_MODEL_SCHEMA
        or model.get("status") != protocol.OPERATION_MODEL_STATUS
    ):
        _fail("operation model schema/status mismatch")
    replay = model.get("replay_plan_contract")
    if type(replay) is not dict:
        _fail("operation model replay-plan contract missing")
    joins = (
        (replay.get("schema"), protocol.PLAN_SCHEMA, "plan schema"),
        (replay.get("status"), protocol.PLAN_STATUS, "plan status"),
        (replay.get("plan_exact_keys"), list(protocol.PLAN_EXACT_KEYS), "plan keys"),
        (
            replay.get("shared_context_exact_keys"),
            list(protocol.SHARED_CONTEXT_EXACT_KEYS),
            "shared-context keys",
        ),
        (
            replay.get("plan_claim_boundary"),
            protocol.PLAN_CLAIM_BOUNDARY,
            "plan claim boundary",
        ),
    )
    for actual, expected, label in joins:
        if not _strict_equal(actual, expected):
            _fail(f"operation model {label} drift")
    process_raw = canonical_bytes(model.get("process_contract"))
    if _sha256(process_raw) != protocol.PROCESS_CONTRACT_SHA256:
        _fail("operation model process-contract digest drift")
    runner_raw = canonical_bytes(replay.get("global_replay_runner_contract"))
    if _sha256(runner_raw) != protocol.GLOBAL_RUNNER_CONTRACT_SHA256:
        _fail("operation model global-runner contract digest drift")
    _assert_protocol_constants_join_model(model)
    return image, _report_root_from_operation_model(path)


def _sorted_unique_ascii_strings(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if type(value) is not list or (nonempty and not value):
        _fail(f"{label}: {'nonempty ' if nonempty else ''}array required")
    result: list[str] = []
    for index, item in enumerate(value):
        text = _ascii_nonempty(item, f"{label}[{index}]")
        result.append(text)
    if result != sorted(set(result)):
        _fail(f"{label}: unique lexicographic order required")
    return result


def _with_parent_imports(imports: set[str]) -> set[str]:
    expanded = set(imports)
    for import_name in tuple(imports):
        parts = import_name.split(".")
        expanded.update(".".join(parts[:index]) for index in range(1, len(parts)))
    return expanded


def _source_imports(
    path: Path,
    label: str,
) -> tuple[set[str], ast.Module]:
    image = _read_file(path, label, expected_mode=0o444)
    if len(image.raw) > MAX_SOURCE_BYTES:
        _fail(f"{label}: source byte cap exceeded")
    try:
        text = image.raw.decode("utf-8")
        tree = ast.parse(text, filename=str(path))
    except (UnicodeError, SyntaxError) as error:
        _fail(f"{label}: invalid Python source: {error}")
    imports: set[str] = set()
    lowered = text.lower()
    for basename in protocol.FORBIDDEN_LEGACY_RESULT_BASENAMES:
        if basename.lower() in lowered:
            _fail(f"{label}: forbidden legacy result basename embedded in source")
    for payload in protocol.FORBIDDEN_SCIENTIFIC_PAYLOADS:
        if payload.lower() in lowered:
            _fail(f"{label}: forbidden scientific payload embedded in source")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__" and node.level == 0:
                continue
            if node.module == "typing" and node.level == 0:
                imports.add("typing")
                continue
            _fail(
                f"{label}: from-import forbidden by the static closure profile; "
                "use an explicit module import"
            )
        elif isinstance(node, ast.Call):
            dynamic_names = {
                "__import__",
                "compile",
                "eval",
                "exec",
                "getattr",
                "import_module",
            }
            if isinstance(node.func, ast.Name) and node.func.id in dynamic_names:
                _fail(f"{label}: dynamic execution/import primitive forbidden")
            if isinstance(node.func, ast.Attribute) and node.func.attr in dynamic_names:
                _fail(f"{label}: dynamic execution/import attribute forbidden")
        if isinstance(node, ast.Name) and node.id in {
            "__import__",
            "compile",
            "eval",
            "exec",
            "getattr",
            "import_module",
        }:
            _fail(f"{label}: dynamic execution/import primitive reference forbidden")
        if isinstance(node, ast.Attribute) and node.attr in {
            "__import__",
            "compile",
            "eval",
            "exec",
            "getattr",
            "import_module",
        }:
            _fail(f"{label}: dynamic execution/import attribute reference forbidden")
    for import_name in imports:
        if any(
            import_name == prefix or import_name.startswith(prefix + ".")
            for prefix in protocol.FORBIDDEN_LEGACY_IMPORT_PREFIXES
        ):
            _fail(f"{label}: forbidden legacy import {import_name}")
    return imports, tree


def _validate_resolved_dependencies(
    value: Any,
    imports: list[str],
    root_imports: set[str],
    source_paths: set[Path],
    gmpy2_extension: FileImage,
    report_root: Path,
    label: str,
) -> tuple[set[Path], set[Path]]:
    if type(value) is not list:
        _fail(f"{label}: dependency array required")
    names: list[str] = []
    dependency_paths: set[Path] = set()
    report_local_paths: set[Path] = set()
    import_graph: dict[str, set[str]] = {}
    file_import_names: dict[Path, str] = {}
    for index, item in enumerate(value):
        current = _exact_keys(item, _RESOLVED_DEPENDENCY_KEYS, f"{label}[{index}]")
        import_name = _ascii_nonempty(current["import_name"], f"{label}[{index}].import_name")
        if _IMPORT_RE.fullmatch(import_name) is None:
            _fail(f"{label}[{index}]: invalid import name")
        origin = current["origin_kind"]
        if origin not in _ORIGIN_KINDS:
            _fail(f"{label}[{index}]: invalid origin kind")
        names.append(import_name)
        if origin in {"builtin", "frozen"}:
            if current["path"] is not None or current["sha256"] is not None:
                _fail(f"{label}[{index}]: builtin/frozen path and digest must be null")
            import_graph[import_name] = set()
            continue
        image = _plain_pin(
            {"path": current["path"], "sha256": current["sha256"]},
            f"{label}[{index}]",
        )
        previous_import_name = file_import_names.get(image.path)
        if previous_import_name is not None and previous_import_name != import_name:
            _fail(f"{label}[{index}]: one file path is mapped to multiple import names")
        file_import_names[image.path] = import_name
        dependency_paths.add(image.path)
        if origin == "file_report_local":
            if not _relative_to(image.path, report_root):
                _fail(f"{label}[{index}]: report-local origin outside report root")
            if image.path not in source_paths:
                _fail(f"{label}[{index}]: unbound report-local dependency")
            if image.path.name == "__init__.py":
                _fail(f"{label}[{index}]: report-local package imports are forbidden")
            if import_name != image.path.stem:
                _fail(f"{label}[{index}]: report-local import/path identity mismatch")
            report_local_paths.add(image.path)
        elif origin == "file_runtime_prefix":
            if _relative_to(image.path, report_root):
                _fail(f"{label}[{index}]: report-root file reclassified as runtime prefix")
            expected_tail = (
                image.path.parent.name if image.path.name == "__init__.py" else image.path.stem
            )
            if import_name.split(".")[-1] != expected_tail:
                _fail(f"{label}[{index}]: runtime-prefix import/path identity mismatch")
        elif origin == "numerical_native_extension":
            if (
                import_name != "gmpy2"
                or image.path != gmpy2_extension.path
                or image.sha256 != gmpy2_extension.sha256
            ):
                _fail(f"{label}[{index}]: numerical extension pin mismatch")
        nested_imports: set[str] = set()
        if image.path.suffix == ".py":
            nested_imports, _ = _source_imports(
                image.path,
                f"{label}[{index}] source",
            )
        import_graph[import_name] = _with_parent_imports(nested_imports)
    if names != sorted(names) or len(names) != len(set(names)) or names != imports:
        _fail(f"{label}: resolved dependency/import closure mismatch")
    declared = set(imports)
    reachable: set[str] = set()
    pending = list(_with_parent_imports(root_imports))
    while pending:
        import_name = pending.pop()
        if import_name in reachable:
            continue
        if import_name not in declared:
            _fail(f"{label}: reachable import lacks one resolved dependency: {import_name}")
        reachable.add(import_name)
        pending.extend(import_graph[import_name] - reachable)
    if reachable != declared:
        unreachable = sorted(declared - reachable)
        _fail(f"{label}: unreachable resolved dependency records: {unreachable}")
    return dependency_paths, report_local_paths


def _validate_runtime_closure(
    image: FileImage,
    model: dict[str, Any],
    report_root: Path,
) -> RuntimeInfo:
    document = image.document
    assert document is not None
    _exact_keys(document, protocol.RUNTIME_EXACT_KEYS, "runtime closure")
    if (
        document["schema"] != protocol.RUNTIME_CLOSURE_SCHEMA
        or document["status"] != protocol.RUNTIME_CLOSURE_STATUS
        or not _strict_equal(document["claim_boundary"], protocol.RUNTIME_CLAIM_BOUNDARY)
    ):
        _fail("runtime closure schema/status/claim boundary mismatch")
    _walk_forbidden_precommit(document["roles"], "runtime role closure")
    _walk_forbidden_precommit(document["global_runner"], "global runner closure")
    if not _strict_equal(document["process_contract"], model["process_contract"]):
        _fail("runtime closure process contract does not equal operation model")
    if _sha256(canonical_bytes(document["process_contract"])) != protocol.PROCESS_CONTRACT_SHA256:
        _fail("runtime closure process-contract digest mismatch")

    host = _exact_keys(
        document["host_runtime_trust_boundary"],
        protocol.HOST_RUNTIME_EXACT_KEYS,
        "host runtime trust boundary",
    )
    _walk_forbidden_precommit(host, "host runtime trust boundary")
    if (
        host["byte_complete"] is not False
        or host["status"] != protocol.HOST_RUNTIME_STATUS
        or not _strict_equal(host["scope"], list(protocol.HOST_RUNTIME_SCOPE))
    ):
        _fail("host runtime trust boundary mismatch")
    for key in ("darwin_kernel_release", "machine", "macos_build_version"):
        _ascii_nonempty(host[key], f"host runtime {key}")

    roles = document["roles"]
    if type(roles) is not list or len(roles) != 3:
        _fail("runtime closure must contain exactly three roles")
    role_records: dict[int, dict[str, Any]] = {}
    all_input_paths: set[Path] = {image.path}
    all_source_paths: set[Path] = set()
    all_source_digests: set[str] = set()
    producer_source_paths: set[Path] = set()
    producer_source_digests: set[str] = set()
    verifier_source_paths: set[Path] = set()
    verifier_source_digests: set[str] = set()
    code_input_paths: set[Path] = set()
    declared_report_dependency_paths: set[Path] = set()
    python_pin: dict[str, str] | None = None
    python_identity: tuple[str, str] | None = None
    role_gmpy2_extensions: dict[int, FileImage] = {}

    for ordinal, role_id in enumerate(protocol.ROLE_ORDER):
        role = _exact_keys(
            roles[ordinal], protocol.RUNTIME_ROLE_EXACT_KEYS, f"runtime role {role_id}"
        )
        if (
            type(role["role_id"]) is not int
            or role["role_id"] != role_id
            or role["role_name"] != protocol.ROLE_NAMES[role_id]
        ):
            _fail(f"runtime role {role_id}: identity mismatch")
        role_records[role_id] = role

        if role["allowed_shared_protocol"] is not None:
            _fail(
                "non-null allowed_shared_protocol is unsupported until an exact frozen "
                "semantics-free byte allowlist is added"
            )

        code_inputs = _exact_keys(
            role["code_inputs"],
            protocol.RUNTIME_CODE_INPUT_EXACT_KEYS,
            f"runtime role {role_id} code inputs",
        )
        code_images: dict[str, FileImage] = {}
        direct_imports: dict[str, set[str]] = {}
        for side in protocol.RUNTIME_SIDE_EXACT_KEYS:
            code_image = _plain_pin(code_inputs[side], f"runtime role {role_id} {side} code")
            expected_basename = protocol.SOURCE_BASENAMES[role_id][f"{side}_basename"]
            if code_image.path.name != expected_basename or not _relative_to(
                code_image.path, report_root
            ):
                _fail(f"runtime role {role_id} {side}: v3 source identity mismatch")
            imports, _ = _source_imports(code_image.path, f"runtime role {role_id} {side}")
            code_images[side] = code_image
            direct_imports[side] = imports
            all_input_paths.add(code_image.path)
            if code_image.path in code_input_paths:
                _fail("runtime closure reuses a v3 code input path")
            code_input_paths.add(code_image.path)

        if code_images["producer"].path == code_images["verifier"].path:
            _fail(f"runtime role {role_id}: producer/verifier path overlap")
        if code_images["producer"].sha256 == code_images["verifier"].sha256:
            _fail(f"runtime role {role_id}: producer/verifier byte overlap")
        verifier_stem = code_images["verifier"].path.stem
        producer_stem = code_images["producer"].path.stem
        if any(
            name == verifier_stem or name.endswith("." + verifier_stem)
            for name in direct_imports["producer"]
        ):
            _fail(f"runtime role {role_id}: producer imports verifier")
        if any(
            name == producer_stem or name.endswith("." + producer_stem)
            for name in direct_imports["verifier"]
        ):
            _fail(f"runtime role {role_id}: verifier imports producer")

        executable = _plain_pin(
            role["python_executable"],
            f"runtime role {role_id} Python",
            expected_mode=0o555,
        )
        current_python_pin = _pin_object(executable)
        if python_pin is None:
            python_pin = current_python_pin
        elif current_python_pin != python_pin:
            _fail("runtime roles do not share one pinned Python executable")
        all_input_paths.add(executable.path)

        native_runtime = _exact_keys(
            role["native_runtime"], _NATIVE_RUNTIME_KEYS, f"runtime role {role_id} native runtime"
        )
        for key, value in native_runtime.items():
            _ascii_nonempty(value, f"runtime role {role_id} native_runtime.{key}")
        current_identity = (native_runtime["python_abi"], native_runtime["python_version"])
        if python_identity is None:
            python_identity = current_identity
        elif current_identity != python_identity:
            _fail("runtime roles do not share one Python ABI/version identity")

        libraries = role["native_libraries"]
        if type(libraries) is not list or len(libraries) != len(protocol.NATIVE_LIBRARY_ROLES):
            _fail(f"runtime role {role_id}: native library cardinality mismatch")
        library_images: dict[str, FileImage] = {}
        for library_ordinal, expected_role in enumerate(protocol.NATIVE_LIBRARY_ROLES):
            library = _exact_keys(
                libraries[library_ordinal],
                _NATIVE_LIBRARY_KEYS,
                f"runtime role {role_id} native library {expected_role}",
            )
            if not _strict_equal(library["role"], expected_role):
                _fail(f"runtime role {role_id}: native library order/role mismatch")
            library_image = _plain_pin(
                {"path": library["path"], "sha256": library["sha256"]},
                f"runtime role {role_id} native library {expected_role}",
            )
            library_images[expected_role] = library_image
            all_input_paths.add(library_image.path)
        role_gmpy2_extensions[role_id] = library_images["gmpy2_extension"]

        imports_map = _exact_keys(
            role["python_imports"],
            protocol.RUNTIME_SIDE_EXACT_KEYS,
            f"runtime role {role_id} Python imports",
        )
        dependency_map = _exact_keys(
            role["resolved_python_dependencies"],
            protocol.RUNTIME_SIDE_EXACT_KEYS,
            f"runtime role {role_id} resolved dependencies",
        )
        report_dependencies = _exact_keys(
            role["report_local_dependencies"],
            protocol.RUNTIME_SIDE_EXACT_KEYS,
            f"runtime role {role_id} report dependencies",
        )

        side_paths: dict[str, set[Path]] = {}
        side_digests: dict[str, set[str]] = {}
        for side in protocol.RUNTIME_SIDE_EXACT_KEYS:
            imports = _sorted_unique_ascii_strings(
                imports_map[side], f"runtime role {role_id} {side} imports", nonempty=True
            )
            if not direct_imports[side].issubset(set(imports)):
                _fail(f"runtime role {role_id} {side}: direct imports absent from closure")
            for import_name in imports:
                if _IMPORT_RE.fullmatch(import_name) is None:
                    _fail(f"runtime role {role_id} {side}: invalid import name")
                if any(
                    import_name == prefix or import_name.startswith(prefix + ".")
                    for prefix in protocol.FORBIDDEN_LEGACY_IMPORT_PREFIXES
                ):
                    _fail(f"runtime role {role_id} {side}: forbidden legacy import")

            dependencies = report_dependencies[side]
            if type(dependencies) is not list:
                _fail(f"runtime role {role_id} {side}: report dependency array required")
            dependency_pins: list[dict[str, str]] = []
            report_dependency_paths: set[Path] = set()
            source_paths = {code_images[side].path}
            source_digests = {code_images[side].sha256}
            for dep_index, dependency in enumerate(dependencies):
                dep_image = _plain_pin(
                    dependency, f"runtime role {role_id} {side} report dependency {dep_index}"
                )
                if not _relative_to(dep_image.path, report_root):
                    _fail(f"runtime role {role_id} {side}: report dependency outside report root")
                dependency_pins.append(_pin_object(dep_image))
                report_dependency_paths.add(dep_image.path)
                declared_report_dependency_paths.add(dep_image.path)
                source_paths.add(dep_image.path)
                source_digests.add(dep_image.sha256)
                all_input_paths.add(dep_image.path)
            if dependency_pins != sorted(dependency_pins, key=lambda pin: pin["path"]):
                _fail(f"runtime role {role_id} {side}: report dependencies not path-sorted")
            if len({pin["path"] for pin in dependency_pins}) != len(dependency_pins):
                _fail(f"runtime role {role_id} {side}: duplicate report dependency")
            dependency_paths, reachable_report_paths = _validate_resolved_dependencies(
                dependency_map[side],
                imports,
                direct_imports[side],
                source_paths,
                library_images["gmpy2_extension"],
                report_root,
                f"runtime role {role_id} {side} resolved dependencies",
            )
            if report_dependency_paths != reachable_report_paths:
                _fail(
                    f"runtime role {role_id} {side}: declared report dependencies do not "
                    "exactly equal the reachable report-local import closure"
                )
            all_input_paths.update(dependency_paths)
            side_paths[side] = source_paths
            side_digests[side] = source_digests

        if side_paths["producer"] & side_paths["verifier"]:
            _fail(f"runtime role {role_id}: producer/verifier source path overlap")
        if side_digests["producer"] & side_digests["verifier"]:
            _fail(f"runtime role {role_id}: producer/verifier source byte overlap")
        all_source_paths.update(side_paths["producer"] | side_paths["verifier"])
        all_source_digests.update(side_digests["producer"] | side_digests["verifier"])
        producer_source_paths.update(side_paths["producer"])
        producer_source_digests.update(side_digests["producer"])
        verifier_source_paths.update(side_paths["verifier"])
        verifier_source_digests.update(side_digests["verifier"])

    if producer_source_paths & verifier_source_paths:
        _fail("runtime closure producer/verifier transitive source path overlap across roles")
    if producer_source_digests & verifier_source_digests:
        _fail("runtime closure producer/verifier transitive source byte overlap across roles")
    if declared_report_dependency_paths & code_input_paths:
        _fail("runtime report-local dependencies must exclude all six code inputs")

    runner = _exact_keys(
        document["global_runner"], protocol.GLOBAL_RUNNER_EXACT_KEYS, "global replay runner"
    )
    if (
        runner["runner_id"] != protocol.GLOBAL_RUNNER_ID
        or runner["runner_contract_sha256"] != protocol.GLOBAL_RUNNER_CONTRACT_SHA256
    ):
        _fail("global replay runner identity/contract digest mismatch")
    runner_code = _plain_pin(runner["code_input"], "global replay runner code")
    if runner_code.path.name != protocol.GLOBAL_RUNNER_BASENAME or not _relative_to(
        runner_code.path, report_root
    ):
        _fail("global replay runner v2 source identity mismatch")
    runner_direct_imports, _ = _source_imports(runner_code.path, "global replay runner code")
    forbidden_runner_import_roots = {
        "cmath",
        "decimal",
        "fractions",
        "gmpy2",
        "math",
        "mpmath",
        "statistics",
    }
    for import_name in runner_direct_imports:
        if (
            import_name.split(".")[0] in forbidden_runner_import_roots
            or "candidate_native" in import_name
        ):
            _fail("global replay runner imports numerical/scientific implementation code")
    runner_source_text = runner_code.raw.decode("utf-8", errors="strict")
    for parameter_id in (
        parameter_id
        for role_id in protocol.ROLE_ORDER
        for parameter_id in protocol.METHOD_PARAMETER_IDS[role_id]
    ):
        if parameter_id in runner_source_text:
            _fail("global replay runner embeds numerical method parameters")
    if runner_code.path in all_source_paths or runner_code.sha256 in all_source_digests:
        _fail("global replay runner overlaps a role numerical source")
    runner_python = _plain_pin(
        runner["python_executable"], "global replay runner Python", expected_mode=0o555
    )
    if _pin_object(runner_python) != python_pin:
        _fail("global replay runner Python pin differs from role pins")
    runner_identity = _exact_keys(
        runner["python_runtime"], _PYTHON_IDENTITY_KEYS, "global runner Python identity"
    )
    if (runner_identity["python_abi"], runner_identity["python_version"]) != python_identity:
        _fail("global replay runner Python identity differs from roles")
    runner_imports = _sorted_unique_ascii_strings(
        runner["python_imports"], "global runner imports", nonempty=True
    )
    for import_name in runner_imports:
        if (
            import_name.split(".")[0] in forbidden_runner_import_roots
            or "candidate_native" in import_name
        ):
            _fail("global replay runner transitive closure imports numerical code")
    if not runner_direct_imports.issubset(set(runner_imports)):
        _fail("global runner direct imports absent from closure")
    runner_dep_images: list[FileImage] = []
    runner_source_paths = {runner_code.path}
    runner_source_digests = {runner_code.sha256}
    runner_dependencies = runner["report_local_dependencies"]
    if type(runner_dependencies) is not list:
        _fail("global runner report-local dependency array required")
    runner_dependency_pins: list[dict[str, str]] = []
    runner_report_dependency_paths: set[Path] = set()
    for index, dependency in enumerate(runner_dependencies):
        dep_image = _plain_pin(dependency, f"global runner report dependency {index}")
        if not _relative_to(dep_image.path, report_root):
            _fail("global runner report dependency outside report root")
        runner_dep_images.append(dep_image)
        runner_dependency_pins.append(_pin_object(dep_image))
        runner_report_dependency_paths.add(dep_image.path)
        runner_source_paths.add(dep_image.path)
        runner_source_digests.add(dep_image.sha256)
    if runner_code.path in runner_report_dependency_paths:
        _fail("global runner report dependencies must exclude its code input")
    if runner_dependency_pins != sorted(runner_dependency_pins, key=lambda pin: pin["path"]):
        _fail("global runner report dependencies not path-sorted")
    if len({pin["path"] for pin in runner_dependency_pins}) != len(runner_dependency_pins):
        _fail("global runner has duplicate report dependencies")
    if runner_source_paths & all_source_paths or runner_source_digests & all_source_digests:
        _fail("global replay runner closure overlaps a role numerical source")
    runner_resolved_paths, runner_reachable_report_paths = _validate_resolved_dependencies(
        runner["resolved_python_dependencies"],
        runner_imports,
        runner_direct_imports,
        runner_source_paths,
        role_gmpy2_extensions[8],
        report_root,
        "global runner resolved dependencies",
    )
    if runner_report_dependency_paths != runner_reachable_report_paths:
        _fail(
            "global runner report dependencies do not exactly equal the reachable "
            "report-local import closure"
        )
    all_input_paths.update(
        {runner_code.path, runner_python.path}
        | {image.path for image in runner_dep_images}
        | runner_resolved_paths
    )
    all_source_paths.update(runner_source_paths)
    all_source_digests.update(runner_source_digests)

    return RuntimeInfo(
        image=image,
        document=document,
        role_records=role_records,
        source_paths=frozenset(all_source_paths),
        source_digests=frozenset(all_source_digests),
        all_input_paths=frozenset(all_input_paths),
    )


def _walk_forbidden_precommit(value: Any, label: str, path: tuple[str, ...] = ()) -> None:
    if type(value) is dict:
        for key, item in value.items():
            current = (*path, key)
            normalized = key.lower()
            if key in protocol.FORBIDDEN_PRECOMMIT_FIELDS:
                _fail(f"{label}: forbidden precommit field at {'/'.join(current)}")
            if any(fragment in normalized for fragment in protocol.FORBIDDEN_RESULT_KEY_FRAGMENTS):
                _fail(f"{label}: result-bearing field at {'/'.join(current)}")
            _walk_forbidden_precommit(item, label, current)
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _walk_forbidden_precommit(item, label, (*path, str(index)))
        return
    if type(value) is str:
        basename = Path(value).name
        if basename in protocol.FORBIDDEN_LEGACY_RESULT_BASENAMES:
            _fail(f"{label}: forbidden legacy result path at {'/'.join(path)}")
        if value in protocol.FORBIDDEN_SCIENTIFIC_PAYLOADS:
            _fail(f"{label}: forbidden scientific payload at {'/'.join(path)}")
        compact = "".join(
            character
            for character in unicodedata.normalize("NFKC", value).casefold()
            if character.isalnum()
        )
        forbidden_tokens = (
            *protocol.FORBIDDEN_PRECOMMIT_FIELDS,
            *protocol.FORBIDDEN_RESULT_KEY_FRAGMENTS,
            *protocol.FORBIDDEN_SCIENTIFIC_PAYLOADS,
        )
        for token in forbidden_tokens:
            token_compact = "".join(
                character for character in token.casefold() if character.isalnum()
            )
            if token_compact and token_compact in compact:
                _fail(f"{label}: forbidden result token in value at {'/'.join(path)}")


def _expected_authority_pin(model: dict[str, Any], report_root: Path, key: str) -> dict[str, str]:
    binding = model.get("authority_bindings", {}).get(key)
    if type(binding) is not dict:
        _fail(f"operation model authority binding missing: {key}")
    expected_schema = protocol.AUTHORITY_SCHEMAS[key]
    expected_sha = protocol.AUTHORITY_SHA256[key]
    if binding.get("schema") != expected_schema or binding.get("sha256") != expected_sha:
        _fail(f"operation model authority binding drift: {key}")
    relative = binding.get("path")
    if type(relative) is not str or PurePosixPath(relative).is_absolute():
        _fail(f"operation model authority path invalid: {key}")
    path = report_root.joinpath(*PurePosixPath(relative).parts)
    return {"path": str(path), "schema": expected_schema, "sha256": expected_sha}


def _member_identity(document: dict[str, Any]) -> str:
    identity = {
        "configuration_order": document.get("configuration_order"),
        "configuration_semantic_ids": document.get("configuration_semantic_ids"),
        "member_semantics": document.get("member_semantics"),
        "n0_sequence_bindings": document.get("n0_sequence_bindings"),
        "role_bindings_1_through_4": document.get("role_bindings"),
    }
    raw = b"encounter-continuum-c1-c2-n0-member-identity-v4\0" + canonical_bytes(identity)
    return _sha256(raw)


def _domain_digest(domain: str, value: Any) -> str:
    return _sha256(domain.encode("ascii") + b"\0" + canonical_bytes(value))


def _configuration_inventory(configuration: dict[str, Any]) -> list[dict[str, Any]]:
    rows = configuration.get("configurations")
    if type(rows) is not list or len(rows) != 12:
        _fail("configuration authority must contain exactly 12 rows")
    records: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if type(row) is not dict:
            _fail(f"configuration row {index}: object required")
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
    if type(bindings) is not list or len(bindings) != 12:
        _fail("member-v4 partition inventory must contain exactly 12 bindings")
    records: list[dict[str, Any]] = []
    for index, binding in enumerate(bindings):
        if (
            type(binding) is not dict
            or type(binding.get("configuration_index")) is not int
            or binding.get("configuration_index") != index
        ):
            _fail("member-v4 partition inventory order mismatch")
        axes = binding.get("n0_axes")
        if type(axes) is not list or len(axes) != len(protocol.COORDINATE_ORDER):
            _fail("member-v4 partition inventory axis cardinality mismatch")
        for coordinate, axis in zip(protocol.COORDINATE_ORDER, axes, strict=True):
            if type(axis) is not dict or not _strict_equal(axis.get("coordinate"), coordinate):
                _fail("member-v4 partition inventory coordinate order mismatch")
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


def _validate_method_registry(document: dict[str, Any]) -> None:
    if document.get("schema") != protocol.AUTHORITY_SCHEMAS["method_parameter_registry"]:
        _fail("method-parameter registry schema mismatch")
    parameters = document.get("parameters")
    if (
        type(parameters) is not list
        or type(document.get("parameter_count")) is not int
        or document.get("parameter_count") != len(parameters)
    ):
        _fail("method-parameter registry cardinality mismatch")
    records: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(parameters):
        current = _exact_keys(
            record,
            ("method_parameter_sha256", "parameter_id", "parameters"),
            f"method registry record {index}",
        )
        parameter_id = _ascii_nonempty(current["parameter_id"], f"method registry record {index}")
        digest = current["method_parameter_sha256"]
        if not _valid_sha(digest):
            _fail(f"method registry record {index}: invalid digest")
        expected = _sha256(
            b"encounter-outward-method-parameters-v4\0" + canonical_bytes(current["parameters"])
        )
        if digest != expected or parameter_id in records:
            _fail(f"method registry record {index}: digest or identity mismatch")
        records[parameter_id] = current
    required = {
        parameter_id
        for role in protocol.ROLE_ORDER
        for parameter_id in protocol.METHOD_PARAMETER_IDS[role]
    }
    if not required.issubset(records):
        _fail("method registry does not contain every plan-v2 selected method")


def _safe_report_relative(value: Any, label: str) -> PurePosixPath:
    if type(value) is not str or not value or "\\" in value:
        _fail(f"{label}: canonical report-relative path required")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        _fail(f"{label}: unsafe report-relative path")
    if path.as_posix() != value:
        _fail(f"{label}: noncanonical report-relative path")
    return path


def _validate_sealed_mirror_tree(manifest_image: FileImage) -> set[Path]:
    manifest = manifest_image.document
    assert manifest is not None
    root = manifest_image.path.parent
    try:
        root_metadata = root.lstat()
    except OSError as error:
        _fail(f"sealed mirror root unavailable: {error}")
    if (
        stat.S_ISLNK(root_metadata.st_mode)
        or not stat.S_ISDIR(root_metadata.st_mode)
        or stat.S_IMODE(root_metadata.st_mode) != 0o555
    ):
        _fail("sealed mirror root must be a non-symlink mode-0555 directory")
    entries = manifest.get("entries")
    if (
        type(entries) is not list
        or type(manifest.get("entry_count")) is not int
        or manifest.get("entry_count") != len(entries)
        or len(entries) != 40
    ):
        _fail("sealed mirror manifest entry cardinality mismatch")
    expected_files = {"manifest.json"}
    expected_directories: set[str] = set()
    opened_paths: set[Path] = {root, manifest_image.path}
    base_keys = {
        "byte_length",
        "mirror_relative_path",
        "ordinal",
        "semantic_role",
        "sha256",
        "source_report_relative_path",
    }
    partition_extra_keys = {"configuration_index", "configuration_label", "coordinate"}
    for index, entry in enumerate(entries):
        if type(entry) is not dict:
            _fail(f"sealed mirror entry {index}: object required")
        expected_keys = (
            base_keys | partition_extra_keys
            if entry.get("semantic_role") == "member_v4_partition"
            else base_keys
        )
        if set(entry) != expected_keys:
            _fail(f"sealed mirror entry {index}: exact-key mismatch")
        if (
            type(entry["ordinal"]) is not int
            or entry["ordinal"] != index
            or type(entry["byte_length"]) is not int
            or entry["byte_length"] <= 0
            or not _valid_sha(entry["sha256"])
        ):
            _fail(f"sealed mirror entry {index}: identity/length/digest mismatch")
        source = _safe_report_relative(
            entry["source_report_relative_path"], f"sealed mirror entry {index} source"
        )
        mirror_relative = _safe_report_relative(
            entry["mirror_relative_path"], f"sealed mirror entry {index} mirror path"
        )
        if mirror_relative != PurePosixPath("files") / source:
            _fail(f"sealed mirror entry {index}: report-relative suffix mismatch")
        absolute = root.joinpath(*mirror_relative.parts)
        image = _read_file(
            absolute,
            f"sealed mirror entry {index}",
            expected_mode=0o444,
        )
        if image.sha256 != entry["sha256"] or len(image.raw) != entry["byte_length"]:
            _fail(f"sealed mirror entry {index}: byte authentication mismatch")
        opened_paths.add(absolute)
        expected_files.add(mirror_relative.as_posix())
        parent = mirror_relative.parent
        while parent != PurePosixPath("."):
            expected_directories.add(parent.as_posix())
            parent = parent.parent

    observed_files: set[str] = set()
    observed_directories: set[str] = set()
    for directory, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        directory_path = Path(directory)
        relative_directory = directory_path.relative_to(root)
        if relative_directory != Path("."):
            metadata = directory_path.lstat()
            if (
                stat.S_ISLNK(metadata.st_mode)
                or not stat.S_ISDIR(metadata.st_mode)
                or stat.S_IMODE(metadata.st_mode) != 0o555
            ):
                _fail("sealed mirror contains a non-mode-0555 directory")
            observed_directories.add(relative_directory.as_posix())
        for name in [*directory_names, *file_names]:
            if name in {"", ".", ".."} or "/" in name or "\\" in name:
                _fail("sealed mirror contains an unsafe directory entry")
            child = directory_path / name
            metadata = child.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                _fail("sealed mirror contains a symlink")
        for name in file_names:
            child = directory_path / name
            metadata = child.lstat()
            if (
                not stat.S_ISREG(metadata.st_mode)
                or stat.S_IMODE(metadata.st_mode) != 0o444
                or metadata.st_nlink != 1
            ):
                _fail("sealed mirror contains a noncanonical file object")
            observed_files.add(child.relative_to(root).as_posix())
    if observed_files != expected_files or observed_directories != expected_directories:
        _fail("sealed mirror contains missing or extra filesystem entries")
    opened_paths.update(root.joinpath(*PurePosixPath(path).parts) for path in observed_directories)
    return opened_paths


def _partition_expectations(
    member: dict[str, Any], mirror: dict[str, Any], mirror_manifest_path: Path
) -> list[dict[str, Any]]:
    if member.get("member_identity_sha256") != protocol.MEMBER_IDENTITY_SHA256:
        _fail("member-v4 stored identity mismatch")
    if _member_identity(member) != protocol.MEMBER_IDENTITY_SHA256:
        _fail("member-v4 identity replay mismatch")
    rows = member.get("n0_sequence_bindings")
    if type(rows) is not list or len(rows) != 12:
        _fail("member-v4 must contain 12 n0 sequence bindings")
    entries = mirror.get("entries")
    if type(entries) is not list:
        _fail("sealed mirror entries missing")
    mirror_by_source: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if type(entry) is not dict or entry.get("semantic_role") != "member_v4_partition":
            continue
        source = entry.get("source_report_relative_path")
        if type(source) is not str or source in mirror_by_source:
            _fail("sealed mirror partition source identity mismatch")
        mirror_by_source[source] = entry
    if len(mirror_by_source) != protocol.PARTITION_BINDING_COUNT:
        _fail("sealed mirror does not contain exactly 36 member-v4 partitions")

    expected: list[dict[str, Any]] = []
    for configuration_index, row in enumerate(rows):
        if (
            type(row) is not dict
            or type(row.get("configuration_index")) is not int
            or row.get("configuration_index") != configuration_index
        ):
            _fail("member-v4 configuration order mismatch")
        axes = row.get("n0_axes")
        if type(axes) is not list or len(axes) != 3:
            _fail("member-v4 n0 axis cardinality mismatch")
        for axis_index, coordinate in enumerate(protocol.COORDINATE_ORDER):
            axis = axes[axis_index]
            if type(axis) is not dict or not _strict_equal(axis.get("coordinate"), coordinate):
                _fail("member-v4 coordinate order mismatch")
            relative = axis.get("partition_report_relative_path")
            sha = axis.get("partition_sha256")
            if type(relative) is not str or not _valid_sha(sha):
                _fail("member-v4 partition binding malformed")
            mirror_entry = mirror_by_source.get(relative)
            if (
                mirror_entry is None
                or mirror_entry.get("sha256") != sha
                or type(mirror_entry.get("mirror_relative_path")) is not str
            ):
                _fail("member-v4 partition is not authenticated by sealed mirror")
            mirror_path = mirror_manifest_path.parent.joinpath(
                *PurePosixPath(mirror_entry["mirror_relative_path"]).parts
            )
            partition = _read_json_file(
                mirror_path, f"sealed partition {configuration_index}/{coordinate}"
            )
            if partition.sha256 != sha or partition.document is None:
                _fail("sealed partition SHA-256 mismatch")
            if partition.document.get("schema") != axis.get("partition_schema"):
                _fail("sealed partition schema mismatch")
            expected.append(
                {
                    "configuration_index": configuration_index,
                    "coordinate": coordinate,
                    "member_report_relative_path": relative,
                    "path": str(mirror_path),
                    "sha256": sha,
                }
            )
    if len(expected) != protocol.PARTITION_BINDING_COUNT:
        _fail("partition expectation cardinality mismatch")
    return expected


def _validate_shared_context(
    shared: Any,
    model: dict[str, Any],
    operation_image: FileImage,
    report_root: Path,
) -> tuple[dict[str, Any], dict[str, FileImage]]:
    context = _exact_keys(shared, protocol.SHARED_CONTEXT_EXACT_KEYS, "shared context")
    if context["member_identity_sha256"] != protocol.MEMBER_IDENTITY_SHA256:
        _fail("shared context member identity mismatch")
    if (
        context["configuration_row_inventory_sha256"] != protocol.CONFIGURATION_ROW_INVENTORY_SHA256
        or context["partition_inventory_sha256"] != protocol.PARTITION_INVENTORY_SHA256
    ):
        _fail("shared context inventory digest mismatch")
    images: dict[str, FileImage] = {}
    for key in (
        "anti_vacuity_policy",
        "configuration",
        "factorization",
        "ideal_formula",
        "member_spec",
        "method_parameter_registry",
        "reference_density",
    ):
        expected_pin = _expected_authority_pin(model, report_root, key)
        if context[key] != expected_pin:
            _fail(f"shared context authority pin mismatch: {key}")
        images[key] = _schema_pin(context[key], protocol.AUTHORITY_SCHEMAS[key], f"shared {key}")
    operation_pin = _pin_object(operation_image, schema=protocol.OPERATION_MODEL_SCHEMA)
    if context["role10_operation_model"] != operation_pin:
        _fail("shared context operation-model pin mismatch")
    images["role10_operation_model"] = operation_image
    member_document = images["member_spec"].document
    configuration_document = images["configuration"].document
    registry_document = images["method_parameter_registry"].document
    assert (
        member_document is not None
        and configuration_document is not None
        and registry_document is not None
    )
    if _member_identity(member_document) != protocol.MEMBER_IDENTITY_SHA256:
        _fail("shared member-v4 identity mismatch")
    configuration_inventory_sha256 = _domain_digest(
        protocol.CONFIGURATION_INVENTORY_DOMAIN,
        _configuration_inventory(configuration_document),
    )
    partition_inventory_sha256 = _domain_digest(
        protocol.PARTITION_INVENTORY_DOMAIN,
        _partition_inventory(member_document),
    )
    if (
        configuration_inventory_sha256 != protocol.CONFIGURATION_ROW_INVENTORY_SHA256
        or context["configuration_row_inventory_sha256"] != configuration_inventory_sha256
        or partition_inventory_sha256 != protocol.PARTITION_INVENTORY_SHA256
        or context["partition_inventory_sha256"] != partition_inventory_sha256
    ):
        _fail("shared context inventory digest replay mismatch")
    _validate_method_registry(registry_document)
    return context, images


def _validate_slots(value: Any) -> tuple[dict[str, Path], set[Path]]:
    if type(value) is not list or len(value) != len(protocol.SLOT_TEMPLATES):
        _fail("replay plan must contain exactly ten slots")
    slot_paths: dict[str, Path] = {}
    output_paths: set[Path] = set()
    resolved_leaf_keys: set[tuple[int, int, str]] = set()
    for index, template in enumerate(protocol.SLOT_TEMPLATES):
        slot = _exact_keys(value[index], protocol.SLOT_EXACT_KEYS, f"slot {index}")
        for key, expected in template.items():
            if not _strict_equal(slot[key], expected):
                _fail(f"slot {index}: template field drift: {key}")
        path = _canonical_absolute(slot["path"], f"slot {index}.path")
        try:
            parent_metadata = path.parent.lstat()
        except OSError as error:
            _fail(f"slot {index}: preexisting parent required: {error}")
        if stat.S_ISLNK(parent_metadata.st_mode) or not stat.S_ISDIR(parent_metadata.st_mode):
            _fail(f"slot {index}: non-symlink directory parent required")
        parent_descriptors, parent_identities = _open_directory_chain(
            path.parent, f"slot {index} parent"
        )
        try:
            parent_identity = os.fstat(parent_descriptors[-1])
            if _directory_identity(parent_identity) != parent_identities[-1]:
                _fail(f"slot {index}: parent identity drift")
            resolved_leaf_key = (parent_identity.st_dev, parent_identity.st_ino, path.name)
        finally:
            _close_descriptors(parent_descriptors)
        if resolved_leaf_key in resolved_leaf_keys:
            _fail("slot paths alias through a resolved parent identity")
        resolved_leaf_keys.add(resolved_leaf_key)
        if slot["slot_id"] in slot_paths:
            _fail("duplicate slot id")
        slot_paths[slot["slot_id"]] = path
        if slot["kind"] == "request" and (path.exists() or path.is_symlink()):
            _fail(f"slot {index}: future request already materialized before commitment")
        if slot["slot_id"] in protocol.OUTPUT_SLOT_ID_SET:
            if path.exists() or path.is_symlink():
                _fail(f"slot {index}: output is not absent at validation time")
            output_paths.add(path)
    paths = list(slot_paths.values())
    if len(set(paths)) != len(paths):
        _fail("slot paths are not pairwise unique")
    for left_index, left in enumerate(paths):
        for right in paths[left_index + 1 :]:
            if not _lexically_disjoint(left, right):
                _fail("slot paths have ancestor/descendant alias")
    role10_paths = [slot_paths[slot_id] for slot_id in protocol.OUTPUT_SLOT_IDS[10]]
    if len({path.parent for path in role10_paths}) != 1:
        _fail("role10 outputs do not share one parent")
    parent = role10_paths[0].parent
    try:
        parent_stat = parent.lstat()
    except OSError as error:
        _fail(f"role10 output parent missing: {error}")
    if (
        not stat.S_ISDIR(parent_stat.st_mode)
        or stat.S_ISLNK(parent_stat.st_mode)
        or stat.S_IMODE(parent_stat.st_mode) != 0o700
        or parent_stat.st_uid != os.geteuid()
    ):
        _fail("role10 output parent must be owned mode-0700 directory")
    return slot_paths, output_paths


def _expected_invocations(
    role_id: int,
    runtime_role: dict[str, Any],
    slot_paths: dict[str, Path],
) -> dict[str, dict[str, Any]]:
    python_path = runtime_role["python_executable"]["path"]
    code_inputs = runtime_role["code_inputs"]
    if role_id == 8:
        return {
            "producer": {
                "argv": [
                    python_path,
                    "-I",
                    "-B",
                    code_inputs["producer"]["path"],
                    "--request",
                    str(slot_paths["role8_request"]),
                    "--output",
                    str(slot_paths["role8_artifact"]),
                ],
                "invocation_id": "role8_raw_axis_formula_producer_v3",
                "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
            },
            "verifier": {
                "argv": [
                    python_path,
                    "-I",
                    "-B",
                    code_inputs["verifier"]["path"],
                    "--request",
                    str(slot_paths["role8_request"]),
                    "--output",
                    str(slot_paths["role8_artifact"]),
                    "--receipt",
                    str(slot_paths["role8_validation_receipt"]),
                ],
                "invocation_id": "role8_raw_axis_formula_verifier_v3",
                "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
            },
        }
    if role_id == 9:
        return {
            "producer": {
                "argv": [
                    python_path,
                    "-I",
                    "-B",
                    code_inputs["producer"]["path"],
                    "--request",
                    str(slot_paths["role9_request"]),
                    "--output",
                    str(slot_paths["role9_artifact"]),
                ],
                "invocation_id": "role9_stationary_integrals_producer_v3",
                "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
            },
            "verifier": {
                "argv": [
                    python_path,
                    "-I",
                    "-B",
                    code_inputs["verifier"]["path"],
                    "--request",
                    str(slot_paths["role9_request"]),
                    "--output",
                    str(slot_paths["role9_artifact"]),
                    "--receipt",
                    str(slot_paths["role9_validation_receipt"]),
                ],
                "invocation_id": "role9_stationary_integrals_verifier_v3",
                "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
            },
        }
    return {
        "transaction_orchestrator": {
            "argv": [
                python_path,
                "-I",
                "-B",
                code_inputs["verifier"]["path"],
                "--request",
                str(slot_paths["role10_request"]),
                "--output",
                str(slot_paths["role10_artifact_directory"]),
                "--semantic-receipt",
                str(slot_paths["role10_semantic_receipt"]),
                "--receipt",
                str(slot_paths["role10_outer_validation_receipt"]),
            ],
            "invocation_id": "role10_killing_geometry_transaction_orchestrator_v3",
            "process_contract_sha256": protocol.PROCESS_CONTRACT_SHA256,
        }
    }


def entry_projection_sha256(entry: dict[str, Any]) -> str:
    projection = dict(entry)
    projection.pop("precommit_projection_sha256", None)
    raw = canonical_bytes(projection)
    framed = (
        protocol.ENTRY_PROJECTION_DOMAIN.encode("ascii") + b"\0" + len(raw).to_bytes(8, "big") + raw
    )
    return _sha256(framed)


def shared_context_sha256(shared_context: dict[str, Any]) -> str:
    return _sha256(
        protocol.SHARED_PRECOMMIT_DOMAIN.encode("ascii") + b"\0" + canonical_bytes(shared_context)
    )


def _validate_plan(
    image: FileImage,
    runtime: RuntimeInfo,
    model: dict[str, Any],
    operation_image: FileImage,
    report_root: Path,
) -> PlanInfo:
    plan = image.document
    assert plan is not None
    _exact_keys(plan, protocol.PLAN_EXACT_KEYS, "replay plan v2")
    if (
        plan["schema"] != protocol.PLAN_SCHEMA
        or plan["status"] != protocol.PLAN_STATUS
        or not _strict_equal(plan["claim_boundary"], protocol.PLAN_CLAIM_BOUNDARY)
    ):
        _fail("replay plan schema/status/claim boundary mismatch")
    _walk_forbidden_precommit(plan, "replay plan")

    expected_runtime_pin = _pin_object(runtime.image, schema=protocol.RUNTIME_CLOSURE_SCHEMA)
    if not _strict_equal(plan["runtime_closure"], expected_runtime_pin):
        _fail("replay plan runtime-closure pin mismatch")
    shared, shared_images = _validate_shared_context(
        plan["shared_context"], model, operation_image, report_root
    )
    shared_digest = shared_context_sha256(shared)
    if plan["shared_precommit_context_sha256"] != shared_digest:
        _fail("replay plan shared-precommit digest mismatch")
    slot_paths, output_paths = _validate_slots(plan["slots"])

    member_image = shared_images["member_spec"]
    registry_image = shared_images["method_parameter_registry"]
    mirror_pin = _expected_authority_pin(model, report_root, "sealed_authentication_mirror")
    mirror_image = _schema_pin(
        mirror_pin,
        protocol.AUTHORITY_SCHEMAS["sealed_authentication_mirror"],
        "sealed authentication mirror",
    )
    mirror_tree_paths = _validate_sealed_mirror_tree(mirror_image)
    assert member_image.document is not None and mirror_image.document is not None
    partitions = _partition_expectations(
        member_image.document, mirror_image.document, mirror_image.path
    )

    entries = plan["entries"]
    if type(entries) is not list or len(entries) != 3:
        _fail("replay plan must contain exactly three entries")
    all_input_paths: set[Path] = set(runtime.all_input_paths)
    all_input_paths.update(image.path for image in shared_images.values())
    all_input_paths.update(mirror_tree_paths)
    all_input_paths.update(Path(binding["path"]) for binding in partitions)
    common_partitions: Any = None
    for ordinal, role_id in enumerate(protocol.ROLE_ORDER):
        entry = _exact_keys(entries[ordinal], protocol.ENTRY_EXACT_KEYS, f"role {role_id} entry")
        if (
            type(entry["role"]) is not int
            or entry["role"] != role_id
            or type(entry["runtime_role_id"]) is not int
            or entry["runtime_role_id"] != role_id
            or entry["entry_id"] != protocol.ROLE_NAMES[role_id]
            or entry["request_slot_id"] != protocol.REQUEST_SLOT_IDS[role_id]
            or not _strict_equal(entry["output_slot_ids"], list(protocol.OUTPUT_SLOT_IDS[role_id]))
        ):
            _fail(f"role {role_id} entry identity/slot mismatch")
        if not _strict_equal(
            entry["method_selection"], list(protocol.METHOD_PARAMETER_IDS[role_id])
        ):
            _fail(f"role {role_id} method selection mismatch")

        authorities = _exact_keys(
            entry["input_authorities"],
            protocol.NORMATIVE_INPUT_AUTHORITY_KEYS[role_id],
            f"role {role_id} input authorities",
        )
        for key in protocol.NORMATIVE_INPUT_AUTHORITY_KEYS[role_id]:
            expected = shared.get(key)
            if expected is None:
                expected = _expected_authority_pin(model, report_root, key)
            if not _strict_equal(authorities[key], expected):
                _fail(f"role {role_id} authority pin mismatch: {key}")
            authority_image = _schema_pin(
                authorities[key], protocol.AUTHORITY_SCHEMAS[key], f"role {role_id} {key}"
            )
            all_input_paths.add(authority_image.path)

        expected_invocations = _expected_invocations(
            role_id, runtime.role_records[role_id], slot_paths
        )
        invocations = entry["invocations"]
        if type(invocations) is not dict or not _strict_equal(invocations, expected_invocations):
            _fail(f"role {role_id} invocation mismatch")
        for name, invocation in invocations.items():
            _exact_keys(invocation, protocol.INVOCATION_EXACT_KEYS, f"role {role_id} {name}")

        if not _strict_equal(entry["partition_path_bindings"], partitions):
            _fail(f"role {role_id} partition bindings mismatch member/mirror")
        if common_partitions is None:
            common_partitions = entry["partition_path_bindings"]
        elif not _strict_equal(entry["partition_path_bindings"], common_partitions):
            _fail("roles 8--10 partition bindings are not byte-identical")
        if entry["precommit_projection_sha256"] != entry_projection_sha256(entry):
            _fail(f"role {role_id} precommit projection digest mismatch")

    all_input_paths.add(image.path)
    request_paths = {
        path for slot_id, path in slot_paths.items() if slot_id not in protocol.OUTPUT_SLOT_ID_SET
    }
    for output in output_paths:
        for dependency in all_input_paths | request_paths:
            if output == dependency:
                _fail("planned output aliases a protocol input")
            if not _lexically_disjoint(output, dependency):
                _fail("planned output has ancestor/descendant conflict with protocol input")

    return PlanInfo(
        image=image,
        document=plan,
        member_image=member_image,
        registry_image=registry_image,
        shared_context=shared,
        slot_paths=slot_paths,
        all_input_paths=frozenset(all_input_paths),
    )


def _validate_bundle(
    image: FileImage,
    plan: PlanInfo,
    runtime: RuntimeInfo,
    operation_image: FileImage,
) -> None:
    bundle = image.document
    assert bundle is not None
    _exact_keys(bundle, protocol.BUNDLE_EXACT_KEYS, "candidate bundle v2")
    if (
        bundle["schema"] != protocol.BUNDLE_SCHEMA
        or bundle["status"] != protocol.BUNDLE_STATUS
        or not _strict_equal(bundle["claim_boundary"], protocol.PLAN_CLAIM_BOUNDARY)
    ):
        _fail("candidate bundle schema/status/claim boundary mismatch")
    _walk_forbidden_precommit(bundle, "candidate bundle")
    expected_pins = {
        "member_spec": _pin_object(
            plan.member_image, schema=protocol.AUTHORITY_SCHEMAS["member_spec"]
        ),
        "method_parameter_registry": _pin_object(
            plan.registry_image,
            schema=protocol.AUTHORITY_SCHEMAS["method_parameter_registry"],
        ),
        "operation_model": _pin_object(operation_image, schema=protocol.OPERATION_MODEL_SCHEMA),
        "replay_plan": _pin_object(plan.image, schema=protocol.PLAN_SCHEMA),
        "runtime_closure": _pin_object(runtime.image, schema=protocol.RUNTIME_CLOSURE_SCHEMA),
    }
    for key, expected in expected_pins.items():
        if not _strict_equal(bundle[key], expected):
            _fail(f"candidate bundle pin mismatch: {key}")
        _schema_pin(bundle[key], protocol.BUNDLE_PIN_SCHEMAS[key], f"bundle {key}")
    if (
        bundle["shared_precommit_context_sha256"]
        != plan.document["shared_precommit_context_sha256"]
    ):
        _fail("candidate bundle shared-precommit digest mismatch")


def validate_package(
    operation_model_path: Path,
    runtime_closure_path: Path,
    replay_plan_path: Path,
    candidate_bundle_path: Path,
) -> dict[str, Any]:
    paths = [
        _canonical_absolute(str(operation_model_path), "operation model CLI path"),
        _canonical_absolute(str(runtime_closure_path), "runtime closure CLI path"),
        _canonical_absolute(str(replay_plan_path), "replay plan CLI path"),
        _canonical_absolute(str(candidate_bundle_path), "candidate bundle CLI path"),
    ]
    if len(set(paths)) != len(paths):
        _fail("package CLI paths must be pairwise distinct")
    operation_image, report_root = _assert_known_operation_model(paths[0])
    model = operation_image.document
    assert model is not None
    runtime_image = _read_json_file(paths[1], "runtime closure v1")
    runtime = _validate_runtime_closure(runtime_image, model, report_root)
    plan_image = _read_json_file(paths[2], "replay plan v2")
    plan = _validate_plan(plan_image, runtime, model, operation_image, report_root)
    bundle_image = _read_json_file(paths[3], "candidate bundle v2")
    _validate_bundle(bundle_image, plan, runtime, operation_image)
    bundle_path = paths[3]
    for dependency in plan.all_input_paths:
        if bundle_path == dependency or not _lexically_disjoint(bundle_path, dependency):
            _fail("candidate bundle path conflicts with a plan/runtime input")
    for slot_path in plan.slot_paths.values():
        if slot_path == bundle_path or not _lexically_disjoint(slot_path, bundle_path):
            _fail("candidate bundle conflicts with a planned slot path")
    return {
        "candidate_bundle_sha256": bundle_image.sha256,
        "completed_checks": [
            "operation_model_v2_authenticated",
            "runtime_closure_manifest_v1_static_joins_validated_under_nonbytecomplete_"
            "host_boundary",
            "replay_plan_v2_static_joins_authenticated",
            "candidate_bundle_v2_static_joins_authenticated",
            "plan_and_bundle_execution_release_same_member_claims_remain_false",
            "package_contains_no_request_commitment_or_result_fields",
        ],
        "schema": PASS_SCHEMA,
        "status": PASS_STATUS,
    }


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operation-model", required=True, type=Path)
    parser.add_argument("--runtime-closure", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--candidate-bundle", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parse_args(argv)
    try:
        ack = validate_package(
            arguments.operation_model,
            arguments.runtime_closure,
            arguments.plan,
            arguments.candidate_bundle,
        )
    except ProtocolFailure as error:
        print(str(error), file=sys.stderr)
        return 2
    print(canonical_bytes(ack).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
