"""Independently validate the frozen C1/n=0 static runtime-root receipt.

This validator reopens the literal current tree through no-symlink directory
descriptors and reconstructs every entry, byte hash, inode, timestamp, and
declared security attribute name.  It does not read or claim extended-attribute
values.  It can validate the present tree.  It cannot independently re-prove
the materializer's historical fsync or renameatx_np syscall sequence, and the
exact receipt schema says so.
"""

from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Final, NoReturn

INVENTORY_SCHEMA: Final = "encounter_continuum_c1_n0_runtime_byte_pin_inventory_v1"
INVENTORY_BYTE_LENGTH: Final = 11_715
INVENTORY_SHA256: Final = "13b70ec6194bbad62e19cea2538f19a8351e6f6ad820ac7a09d0adf25433b8c6"
RECEIPT_SCHEMA: Final = "encounter_continuum_c1_n0_sealed_runtime_root_receipt_v1"
MATERIALIZER_SCHEMA: Final = "encounter_continuum_c1_n0_sealed_runtime_root_materializer_v1"
STATUS: Final = (
    "STATIC_RUNTIME_ROOT_MATERIALIZED_ONLY_NO_PROBE_NO_IMPORT_NO_RUNTIME_CLOSURE_"
    "NO_CANDIDATE_EXECUTION_NO_SCIENCE"
)
AUTHORITY_ROOT: Final = (
    "/Users/ae23069/.local-build/valley-k-small/runtime-authorities/"
    "encounter-c1-n0-cpython-3.12.13-gmpy2-2.2.1-arm64-v1"
)
PUBLICATION_PARENT: Final = "/Users/ae23069/.local-build/valley-k-small/runtime-authorities"
LOCK_NAME: Final = ".encounter-c1-n0-cpython-3.12.13-gmpy2-2.2.1-arm64-v1.materialize-v1.lock"
EXPECTED_UID: Final = 502
EXPECTED_GID: Final = 20
EXPECTED_DIRECTORY_COUNT: Final = 5
EXPECTED_FILE_COUNT: Final = 6
EXPECTED_TOTAL_FILE_BYTES: Final = 1_716_156
RENAME_FLAGS: Final = 0x00000014
ACL_TYPE_EXTENDED: Final = 0x00000100
XATTR_SHOWCOMPRESSION: Final = 0x00000020
ALLOWED_OS_MANAGED_XATTRS: Final = (b"com.apple.provenance",)
MAX_RECEIPT_BYTES: Final = 131_072
MAX_INVENTORY_BYTES: Final = 32_768
MAX_JSON_DEPTH: Final = 64
MAX_JSON_CONTAINER_ITEMS: Final = 8_192
MAX_JSON_TEXT_CHARS: Final = 4_096
MAX_JSON_INTEGER_BITS: Final = 64
MAX_JSON_INTEGER_CHARS: Final = 20
READ_CHUNK: Final = 1 << 20


@dataclass(frozen=True)
class _ExpectedFile:
    relative_path: str
    byte_length: int
    sha256: str
    mode: int


@dataclass(frozen=True)
class _ValidationConfig:
    authority_root: str
    publication_parent: str
    lock_name: str
    expected_uid: int
    expected_gid: int
    files: tuple[_ExpectedFile, ...]
    inventory_schema: str = INVENTORY_SCHEMA
    inventory_byte_length: int = INVENTORY_BYTE_LENGTH
    inventory_sha256: str = INVENTORY_SHA256


PUBLIC_FILES: Final = (
    _ExpectedFile(
        "bin/python3.12",
        52_448,
        "31b9c9a8d50289f3a13f014b3efd8ea3534fc3eea7ca7d9809e166139910b805",
        0o555,
    ),
    _ExpectedFile(
        "site-packages/gmpy2/__init__.py",
        412,
        "3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2",
        0o444,
    ),
    _ExpectedFile(
        "site-packages/gmpy2/gmpy2.cpython-312-darwin.so",
        573_056,
        "9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b",
        0o444,
    ),
    _ExpectedFile(
        "site-packages/gmpy2.libs/libgmp.10.dylib",
        468_768,
        "22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049",
        0o444,
    ),
    _ExpectedFile(
        "site-packages/gmpy2.libs/libmpfr.6.dylib",
        469_360,
        "d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed",
        0o444,
    ),
    _ExpectedFile(
        "site-packages/gmpy2.libs/libmpc.3.dylib",
        152_112,
        "d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c",
        0o444,
    ),
)
PUBLIC_CONFIG: Final = _ValidationConfig(
    authority_root=AUTHORITY_ROOT,
    publication_parent=PUBLICATION_PARENT,
    lock_name=LOCK_NAME,
    expected_uid=EXPECTED_UID,
    expected_gid=EXPECTED_GID,
    files=PUBLIC_FILES,
)


class SealedRuntimeRootReceiptValidationFailure(RuntimeError):
    """Fail-closed receipt or current-tree validation failure."""


def _fail(message: str) -> NoReturn:
    raise SealedRuntimeRootReceiptValidationFailure(message)


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def _parse_json_integer(raw: str) -> int:
    if len(raw) > MAX_JSON_INTEGER_CHARS:
        _fail("JSON integer exceeds the fixed cap")
    value = int(raw, 10)
    if value.bit_length() > MAX_JSON_INTEGER_BITS:
        _fail("JSON integer exceeds the fixed cap")
    return value


def _object_identity(value: os.stat_result) -> tuple[int, int]:
    return value.st_dev, value.st_ino


def _stable_identity(
    value: os.stat_result,
) -> tuple[int, int, int, int, int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mode,
        value.st_nlink,
        value.st_uid,
        value.st_gid,
        value.st_mtime_ns,
        value.st_ctime_ns,
        getattr(value, "st_flags", 0),
    )


def _safe_relative(value: str) -> PurePosixPath:
    if type(value) is not str:
        _fail("relative path is not exact text")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or "\\" in value
        or path.as_posix() != value
    ):
        _fail("unsafe relative path")
    return path


class _ValidationCalls:
    """Private validator syscall seam for bounded mutation tests."""

    def open(
        self,
        path: str,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        return os.open(path, flags, mode, dir_fd=dir_fd)

    def close(self, fd: int) -> None:
        os.close(fd)

    def dup(self, fd: int) -> int:
        return os.dup(fd)

    def fstat(self, fd: int) -> os.stat_result:
        return os.fstat(fd)

    def stat(self, path: str, *, dir_fd: int) -> os.stat_result:
        return os.stat(path, dir_fd=dir_fd, follow_symlinks=False)

    def read(self, fd: int, count: int) -> bytes:
        return os.read(fd, count)

    def listdir(self, fd: int) -> list[str]:
        return os.listdir(fd)

    def event(self, name: str, **_details: object) -> None:
        del name

    def adapt_stat(
        self,
        relative_path: str,
        value: os.stat_result,
    ) -> os.stat_result:
        del relative_path
        return value

    def _libc(self) -> ctypes.CDLL:
        try:
            return ctypes.CDLL(None, use_errno=True)
        except OSError as error:
            _fail(f"Darwin metadata primitive unavailable: {error}")

    def list_xattrs(self, fd: int) -> tuple[bytes, ...]:
        libc = self._libc()
        if not hasattr(libc, "flistxattr"):
            _fail("flistxattr unavailable")
        function = libc.flistxattr
        function.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.c_int,
        ]
        function.restype = ctypes.c_ssize_t
        ctypes.set_errno(0)
        size = function(fd, None, 0, XATTR_SHOWCOMPRESSION)
        if size < 0:
            number = ctypes.get_errno()
            raise OSError(number, os.strerror(number))
        if size == 0:
            return ()
        buffer = ctypes.create_string_buffer(size)
        actual = function(fd, buffer, size, XATTR_SHOWCOMPRESSION)
        if actual < 0:
            number = ctypes.get_errno()
            raise OSError(number, os.strerror(number))
        if actual != size:
            _fail("flistxattr changed during validation")
        return tuple(item for item in buffer.raw[:actual].split(b"\0") if item)

    def has_extended_acl(self, fd: int) -> bool:
        libc = self._libc()
        if not hasattr(libc, "acl_get_fd_np") or not hasattr(libc, "acl_free"):
            _fail("Darwin ACL inspection primitive unavailable")
        getter = libc.acl_get_fd_np
        getter.argtypes = [ctypes.c_int, ctypes.c_int]
        getter.restype = ctypes.c_void_p
        ctypes.set_errno(0)
        pointer = getter(fd, ACL_TYPE_EXTENDED)
        if pointer:
            freer = libc.acl_free
            freer.argtypes = [ctypes.c_void_p]
            freer.restype = ctypes.c_int
            freer(pointer)
            return True
        number = ctypes.get_errno()
        if number in {0, errno.ENOENT}:
            return False
        raise OSError(number, os.strerror(number))


def _directory_flags() -> int:
    return os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def _file_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)


def _open_absolute_directory(calls: _ValidationCalls, path: Path) -> int:
    if not path.is_absolute():
        _fail("validator directory anchor is not absolute")
    current = calls.open("/", _directory_flags())
    try:
        for part in path.parts[1:]:
            child = calls.open(part, _directory_flags(), dir_fd=current)
            calls.close(current)
            current = child
        if not stat.S_ISDIR(calls.fstat(current).st_mode):
            _fail("validator directory walk ended at a non-directory")
        return current
    except BaseException:
        calls.close(current)
        raise


def _require_absolute_anchor(
    calls: _ValidationCalls,
    path: Path,
    anchor_fd: int,
    identity: tuple[int, int],
    phase: str,
) -> None:
    if _object_identity(calls.fstat(anchor_fd)) != identity:
        _fail(f"validator parent descriptor changed {phase}")
    current_fd = _open_absolute_directory(calls, path)
    try:
        if _object_identity(calls.fstat(current_fd)) != identity:
            _fail(f"validator parent pathname was rebound {phase}")
    finally:
        calls.close(current_fd)
    if _object_identity(calls.fstat(anchor_fd)) != identity:
        _fail(f"validator parent descriptor changed {phase}")


def _require_lock_absent(
    calls: _ValidationCalls,
    parent_fd: int,
    lock_name: str,
    phase: str,
) -> None:
    try:
        calls.stat(lock_name, dir_fd=parent_fd)
    except FileNotFoundError:
        return
    _fail(f"fixed materialization lock is live {phase}")


def _require_parent_security(
    calls: _ValidationCalls,
    parent_fd: int,
    config: _ValidationConfig,
    phase: str,
) -> None:
    value = calls.fstat(parent_fd)
    if (
        not stat.S_ISDIR(value.st_mode)
        or value.st_uid != config.expected_uid
        or value.st_gid != config.expected_gid
        or stat.S_IMODE(value.st_mode) & 0o022
        or getattr(value, "st_flags", 0) != 0
    ):
        _fail(f"validator publication parent security metadata mismatch {phase}")
    if calls.has_extended_acl(parent_fd):
        _fail(f"validator publication parent extended ACL is present {phase}")


def _expected_tree(
    config: _ValidationConfig,
) -> dict[str, tuple[str, int, _ExpectedFile | None]]:
    result: dict[str, tuple[str, int, _ExpectedFile | None]] = {".": ("directory", 0o555, None)}
    for expected_file in config.files:
        relative = _safe_relative(expected_file.relative_path)
        result[relative.as_posix()] = ("file", expected_file.mode, expected_file)
        parent = relative.parent
        while parent != PurePosixPath("."):
            result.setdefault(parent.as_posix(), ("directory", 0o555, None))
            parent = parent.parent
    if (
        sum(kind == "directory" for kind, _, _ in result.values()) != EXPECTED_DIRECTORY_COUNT
        or sum(kind == "file" for kind, _, _ in result.values()) != EXPECTED_FILE_COUNT
    ):
        _fail("validator frozen tree shape mismatch")
    return result


def _expected_nlink(
    expected: dict[str, tuple[str, int, _ExpectedFile | None]],
    path: str,
) -> int:
    if expected[path][0] == "file":
        return 1
    prefix = "" if path == "." else path + "/"
    depth = 0 if path == "." else len(PurePosixPath(path).parts)
    return 2 + sum(
        1
        for candidate in expected
        if candidate != "."
        and candidate.startswith(prefix)
        and len(PurePosixPath(candidate).parts) == depth + 1
    )


def _check_security(
    calls: _ValidationCalls,
    fd: int,
    relative: str,
    value: os.stat_result,
    config: _ValidationConfig,
    mode: int,
    nlink: int,
) -> tuple[os.stat_result, tuple[str, ...]]:
    checked = calls.adapt_stat(relative, value)
    if (
        checked.st_uid != config.expected_uid
        or checked.st_gid != config.expected_gid
        or stat.S_IMODE(checked.st_mode) != mode
        or checked.st_nlink != nlink
    ):
        _fail(f"{relative}: current-tree metadata mismatch")
    if getattr(checked, "st_flags", 0) != 0:
        _fail(f"{relative}: current-tree BSD flags are not zero")
    xattrs = calls.list_xattrs(fd)
    if len(xattrs) != len(set(xattrs)) or any(
        name not in ALLOWED_OS_MANAGED_XATTRS for name in xattrs
    ):
        _fail(f"{relative}: unexpected current-tree extended attribute is present")
    if calls.has_extended_acl(fd):
        _fail(f"{relative}: current-tree extended ACL is present")
    return checked, tuple(sorted(name.decode("ascii") for name in xattrs))


def _file_entry(
    calls: _ValidationCalls,
    parent_fd: int,
    name: str,
    relative: str,
    expected_file: _ExpectedFile,
    config: _ValidationConfig,
) -> dict[str, Any]:
    path_before = calls.stat(name, dir_fd=parent_fd)
    fd = calls.open(name, _file_flags(), dir_fd=parent_fd)
    try:
        before = calls.fstat(fd)
        if (
            not stat.S_ISREG(path_before.st_mode)
            or not stat.S_ISREG(before.st_mode)
            or _object_identity(path_before) != _object_identity(before)
        ):
            _fail(f"{relative}: current-tree file identity mismatch")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = calls.read(fd, min(READ_CHUNK, expected_file.byte_length + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > expected_file.byte_length:
                _fail(f"{relative}: current-tree file exceeds frozen size")
        after = calls.fstat(fd)
        if _stable_identity(before) != _stable_identity(after):
            _fail(f"{relative}: current-tree file changed while read")
        path_after = calls.stat(name, dir_fd=parent_fd)
        if _stable_identity(before) != _stable_identity(path_after):
            _fail(f"{relative}: current-tree file pathname changed while read")
        checked, xattrs = _check_security(
            calls,
            fd,
            relative,
            after,
            config,
            expected_file.mode,
            1,
        )
        security_after = calls.fstat(fd)
        security_path = calls.stat(name, dir_fd=parent_fd)
        if _stable_identity(before) != _stable_identity(security_after) or _stable_identity(
            before
        ) != _stable_identity(security_path):
            _fail(f"{relative}: current-tree file changed during security inspection")
        raw = b"".join(chunks)
        if (
            len(raw) != expected_file.byte_length
            or hashlib.sha256(raw).hexdigest() != expected_file.sha256
        ):
            _fail(f"{relative}: current-tree file bytes mismatch")
        return {
            "ctime_ns": checked.st_ctime_ns,
            "dev": checked.st_dev,
            "gid": checked.st_gid,
            "ino": checked.st_ino,
            "mode": f"{stat.S_IMODE(checked.st_mode):04o}",
            "mtime_ns": checked.st_mtime_ns,
            "nlink": checked.st_nlink,
            "path": relative,
            "sha256": expected_file.sha256,
            "size": expected_file.byte_length,
            "type": "file",
            "uid": checked.st_uid,
            "xattrs": list(xattrs),
        }
    finally:
        calls.close(fd)


def _confirm_root_snapshot(
    calls: _ValidationCalls,
    parent_fd: int,
    root_name: str,
    expected_value: os.stat_result,
    config: _ValidationConfig,
    expected: dict[str, tuple[str, int, _ExpectedFile | None]],
) -> None:
    path_value = calls.stat(root_name, dir_fd=parent_fd)
    fd = calls.open(root_name, _directory_flags(), dir_fd=parent_fd)
    try:
        before = calls.fstat(fd)
        if (
            not stat.S_ISDIR(path_value.st_mode)
            or _stable_identity(path_value) != _stable_identity(expected_value)
            or _stable_identity(before) != _stable_identity(expected_value)
        ):
            _fail("validator root changed after traversal")
        _check_security(
            calls,
            fd,
            ".",
            before,
            config,
            0o555,
            _expected_nlink(expected, "."),
        )
        after = calls.fstat(fd)
        final_path = calls.stat(root_name, dir_fd=parent_fd)
        if _stable_identity(after) != _stable_identity(expected_value) or _stable_identity(
            final_path
        ) != _stable_identity(expected_value):
            _fail("validator root changed during final confirmation")
    finally:
        calls.close(fd)


def _scan_current_tree(
    config: _ValidationConfig,
    calls: _ValidationCalls,
) -> tuple[os.stat_result, list[dict[str, Any]]]:
    root = Path(config.authority_root)
    parent = Path(config.publication_parent)
    if not root.is_absolute() or root.parent != parent:
        _fail("validator configuration has an unsafe root")
    parent_fd = -1
    root_fd = -1
    try:
        parent_fd = _open_absolute_directory(calls, parent)
        parent_value = calls.fstat(parent_fd)
        parent_identity = _object_identity(parent_value)
        _require_parent_security(calls, parent_fd, config, "before traversal")
        _require_absolute_anchor(
            calls,
            parent,
            parent_fd,
            parent_identity,
            "before traversal",
        )
        _require_lock_absent(calls, parent_fd, config.lock_name, "before traversal")
        root_path = calls.stat(root.name, dir_fd=parent_fd)
        root_fd = calls.open(root.name, _directory_flags(), dir_fd=parent_fd)
        root_before = calls.fstat(root_fd)
        if (
            not stat.S_ISDIR(root_path.st_mode)
            or not stat.S_ISDIR(root_before.st_mode)
            or _object_identity(root_path) != _object_identity(root_before)
        ):
            _fail("validator current root identity mismatch")
        expected = _expected_tree(config)
        entries: list[dict[str, Any]] = []

        def visit(
            directory_fd: int,
            relative: str,
            containing_fd: int | None,
            containing_name: str | None,
        ) -> None:
            before = calls.fstat(directory_fd)
            if not stat.S_ISDIR(before.st_mode):
                _fail(f"{relative}: validator expected a directory")
            _, mode, _ = expected[relative]
            checked, xattrs = _check_security(
                calls,
                directory_fd,
                relative,
                before,
                config,
                mode,
                _expected_nlink(expected, relative),
            )
            entries.append(
                {
                    "ctime_ns": checked.st_ctime_ns,
                    "dev": checked.st_dev,
                    "gid": checked.st_gid,
                    "ino": checked.st_ino,
                    "mode": f"{stat.S_IMODE(checked.st_mode):04o}",
                    "mtime_ns": checked.st_mtime_ns,
                    "nlink": checked.st_nlink,
                    "path": relative,
                    "type": "directory",
                    "uid": checked.st_uid,
                    "xattrs": list(xattrs),
                }
            )
            prefix = "" if relative == "." else relative + "/"
            depth = 0 if relative == "." else len(PurePosixPath(relative).parts)
            expected_children = sorted(
                candidate[len(prefix) :]
                for candidate in expected
                if candidate != "."
                and candidate.startswith(prefix)
                and len(PurePosixPath(candidate).parts) == depth + 1
            )
            actual_children = calls.listdir(directory_fd)
            if (
                len(actual_children) != len(set(actual_children))
                or sorted(actual_children) != expected_children
            ):
                _fail(f"{relative}: validator exact tree membership mismatch")
            for name in expected_children:
                child_relative = name if relative == "." else f"{relative}/{name}"
                child_kind, _, expected_file = expected[child_relative]
                if child_kind == "directory":
                    path_value = calls.stat(name, dir_fd=directory_fd)
                    child_fd = calls.open(name, _directory_flags(), dir_fd=directory_fd)
                    try:
                        if not stat.S_ISDIR(path_value.st_mode) or _object_identity(
                            path_value
                        ) != _object_identity(calls.fstat(child_fd)):
                            _fail(f"{child_relative}: validator directory identity mismatch")
                        calls.event(
                            "after_directory_open",
                            relative=child_relative,
                            containing_fd=directory_fd,
                            entry_name=name,
                            child_fd=child_fd,
                        )
                        visit(child_fd, child_relative, directory_fd, name)
                    finally:
                        calls.close(child_fd)
                else:
                    if expected_file is None:
                        _fail("validator internal file specification missing")
                    entries.append(
                        _file_entry(
                            calls,
                            directory_fd,
                            name,
                            child_relative,
                            expected_file,
                            config,
                        )
                    )
            after = calls.fstat(directory_fd)
            if _stable_identity(before) != _stable_identity(after):
                _fail(f"{relative}: validator directory changed during traversal")
            if containing_fd is not None and containing_name is not None:
                current = calls.stat(containing_name, dir_fd=containing_fd)
                if not stat.S_ISDIR(current.st_mode) or _stable_identity(
                    before
                ) != _stable_identity(current):
                    _fail(f"{relative}: validator directory pathname changed")

        visit(root_fd, ".", None, None)
        root_after = calls.fstat(root_fd)
        if _stable_identity(root_before) != _stable_identity(root_after):
            _fail("validator current root changed during traversal")
        root_path_after = calls.stat(root.name, dir_fd=parent_fd)
        if _stable_identity(root_before) != _stable_identity(root_path_after):
            _fail("validator current root pathname changed during traversal")
        calls.event("before_parent_postcheck", parent_fd=parent_fd)
        _require_lock_absent(calls, parent_fd, config.lock_name, "after traversal")
        _require_absolute_anchor(
            calls,
            parent,
            parent_fd,
            parent_identity,
            "after traversal",
        )
        _require_parent_security(calls, parent_fd, config, "after traversal")
        _confirm_root_snapshot(
            calls,
            parent_fd,
            root.name,
            root_after,
            config,
            expected,
        )
        _require_lock_absent(calls, parent_fd, config.lock_name, "after final root check")
        if len(entries) != EXPECTED_DIRECTORY_COUNT + EXPECTED_FILE_COUNT:
            _fail("validator current-tree entry count mismatch")
        if sum(entry.get("size", 0) for entry in entries) != EXPECTED_TOTAL_FILE_BYTES:
            _fail("validator current-tree total size mismatch")
        return root_after, sorted(entries, key=lambda entry: entry["path"])
    except OSError as error:
        _fail(f"validator secure current-tree read failed: {error}")
    finally:
        if root_fd >= 0:
            calls.close(root_fd)
        if parent_fd >= 0:
            calls.close(parent_fd)


def _expected_document(
    config: _ValidationConfig,
    root_value: os.stat_result,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "authority_root": {
            "ctime_ns": root_value.st_ctime_ns,
            "dev": root_value.st_dev,
            "gid": root_value.st_gid,
            "ino": root_value.st_ino,
            "mode": f"{stat.S_IMODE(root_value.st_mode):04o}",
            "mtime_ns": root_value.st_mtime_ns,
            "path": config.authority_root,
            "uid": root_value.st_uid,
        },
        "claim_boundary": {
            "candidate_execution_performed": False,
            "complete_runtime_closure_claimed": False,
            "current_static_tree_observed": True,
            "historical_fsync_and_rename_attestation_independently_reproven_by_validator": False,
            "host_runtime_bytes_complete": False,
            "import_resolution_observed": False,
            "only_declared_os_managed_xattrs_permitted": True,
            "operation_model_runtime_closure_substitution_allowed": False,
            "pathname_toctou_closure_claimed": False,
            "root_receipt_substitutes_for_runtime_probe": False,
            "runtime_metadata_observed": False,
            "runtime_probe_performed": False,
            "scientific_claim_made": False,
            "static_root_materialized": True,
            "trust_boundary": (
                "THIS_INVOCATION_STATIC_BYTE_TREE_PUBLICATION_ONLY_"
                "HOST_RUNTIME_AND_CONCURRENT_EXTERNAL_WRITERS_OUT_OF_SCOPE"
            ),
            "xattr_values_claimed": False,
        },
        "entries": entries,
        "materializer": {
            "atomic_publish_flags": RENAME_FLAGS,
            "atomic_publish_primitive": "renameatx_np",
            "directories_bottom_up_fchmod_0555_and_fsync": True,
            "files_write_fsync_fchmod_fsync": True,
            "fixed_o_excl_lock_name": config.lock_name,
            "no_ordinary_rename_fallback": True,
            "parent_fsync_after_atomic_publish": True,
            "parent_identity_rechecked": True,
            "post_publish_independent_fd_tree_readback": True,
            "permitted_os_managed_xattr_names": [
                name.decode("ascii") for name in ALLOWED_OS_MANAGED_XATTRS
            ],
            "schema": MATERIALIZER_SCHEMA,
            "source_same_fd_read_hash_with_pre_post_fstat": True,
            "stage_is_hidden_and_same_parent": True,
        },
        "schema": RECEIPT_SCHEMA,
        "static_inventory": {
            "byte_length": config.inventory_byte_length,
            "schema": config.inventory_schema,
            "sha256": config.inventory_sha256,
        },
        "status": STATUS,
        "summary": {
            "directory_count": EXPECTED_DIRECTORY_COUNT,
            "file_count": EXPECTED_FILE_COUNT,
            "total_file_bytes": EXPECTED_TOTAL_FILE_BYTES,
        },
        "validator_scope": {
            "can_rebuild_current_tree_from_independent_fds": True,
            "cannot_independently_prove_historical_fsync_or_rename_syscalls": True,
            "does_not_read_or_claim_xattr_values": True,
        },
    }


def _decode_receipt(raw: bytes) -> dict[str, Any]:
    if type(raw) is not bytes:
        _fail("receipt must be immutable bytes")
    if not raw or len(raw) > MAX_RECEIPT_BYTES:
        _fail("receipt byte length is outside the fixed cap")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                _fail("receipt contains a duplicate JSON key")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=pairs,
            parse_int=_parse_json_integer,
            parse_float=lambda _value: _fail("receipt contains a float"),
            parse_constant=lambda _value: _fail("receipt contains a constant"),
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        RecursionError,
        MemoryError,
        ValueError,
        OverflowError,
    ) as error:
        _fail(f"receipt is not ASCII JSON: {error}")
    try:
        is_canonical = canonical_json_bytes(value) == raw
    except (RecursionError, MemoryError, ValueError, OverflowError) as error:
        _fail(f"receipt canonicalization failed: {error}")
    if type(value) is not dict or not is_canonical:
        _fail("receipt is not canonical JSON")
    _measure_json(value)
    return value


def _measure_json(value: object) -> None:
    container_items = 0
    stack: list[tuple[object, int]] = [(value, 1)]
    while stack:
        current, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            _fail("JSON nesting exceeds the fixed cap")
        if type(current) is dict:
            container_items += len(current)
            for key, child in current.items():
                if type(key) is not str or len(key) > MAX_JSON_TEXT_CHARS:
                    _fail("JSON key exceeds the fixed text cap")
                stack.append((child, depth + 1))
        elif type(current) is list:
            container_items += len(current)
            stack.extend((child, depth + 1) for child in current)
        elif type(current) is str:
            if len(current) > MAX_JSON_TEXT_CHARS:
                _fail("JSON text exceeds the fixed cap")
        elif type(current) is int:
            if current.bit_length() > MAX_JSON_INTEGER_BITS:
                _fail("JSON integer exceeds the fixed cap")
        elif type(current) not in {bool, type(None)}:
            _fail("JSON contains a forbidden value type")
        if container_items > MAX_JSON_CONTAINER_ITEMS:
            _fail("JSON container work exceeds the fixed cap")


def _decode_inventory(raw: bytes, config: _ValidationConfig) -> dict[str, Any]:
    if type(raw) is not bytes:
        _fail("static inventory must be immutable bytes")
    if (
        not raw
        or len(raw) > MAX_INVENTORY_BYTES
        or len(raw) != config.inventory_byte_length
        or hashlib.sha256(raw).hexdigest() != config.inventory_sha256
    ):
        _fail("static inventory bytes do not match the independent pin")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                _fail("static inventory contains a duplicate JSON key")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=pairs,
            parse_int=_parse_json_integer,
            parse_float=lambda _value: _fail("static inventory contains a float"),
            parse_constant=lambda _value: _fail("static inventory contains a constant"),
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        RecursionError,
        MemoryError,
        ValueError,
        OverflowError,
    ) as error:
        _fail(f"static inventory is not ASCII JSON: {error}")
    try:
        is_canonical = canonical_json_bytes(value) == raw
    except (RecursionError, MemoryError, ValueError, OverflowError) as error:
        _fail(f"static inventory canonicalization failed: {error}")
    if type(value) is not dict or not is_canonical:
        _fail("static inventory is not canonical JSON")
    _measure_json(value)
    if value.get("schema") != config.inventory_schema:
        _fail("static inventory schema mismatch")
    if config.inventory_schema == INVENTORY_SCHEMA:
        _require_inventory_matches_config(value, config)
    return value


def _require_inventory_matches_config(
    value: dict[str, Any],
    config: _ValidationConfig,
) -> None:
    """Join the authenticated production inventory to the independently expected tree."""

    if value.get("authority_root") != config.authority_root:
        _fail("static inventory authority root does not match the validator tree")
    python = value.get("python")
    gmpy2 = value.get("gmpy2")
    libraries = value.get("numerical_libraries")
    if (
        type(python) is not dict
        or type(gmpy2) is not dict
        or type(gmpy2.get("wrapper")) is not dict
        or type(gmpy2.get("extension")) is not dict
        or type(libraries) is not list
        or len(libraries) != 3
        or any(type(item) is not dict for item in libraries)
    ):
        _fail("static inventory primary file map is malformed")

    records = [python, gmpy2["wrapper"], gmpy2["extension"], *libraries]
    observed: dict[str, str] = {}
    for record in records:
        path = record.get("path")
        digest = record.get("sha256")
        if type(path) is not str or type(digest) is not str or path in observed:
            _fail("static inventory primary file map is malformed or duplicated")
        observed[path] = digest
    expected = {
        f"{config.authority_root}/{expected_file.relative_path}": expected_file.sha256
        for expected_file in config.files
    }
    if observed != expected:
        _fail("static inventory path/hash map does not match the validator tree")


def _validate_with_config(
    receipt_bytes: bytes,
    static_inventory_bytes: bytes,
    config: _ValidationConfig,
    calls: _ValidationCalls,
) -> dict[str, Any]:
    """Private tmp-test seam; production callers must use the public API."""

    _decode_inventory(static_inventory_bytes, config)
    document = _decode_receipt(receipt_bytes)
    root_value, entries = _scan_current_tree(config, calls)
    expected = _expected_document(config, root_value, entries)
    if canonical_json_bytes(expected) != receipt_bytes:
        _fail("receipt does not exactly match the independently rebuilt current tree")
    return document


def validate_sealed_runtime_root_receipt_v1(
    receipt_bytes: bytes,
    static_inventory_bytes: bytes,
) -> dict[str, Any]:
    """Validate the one literal receipt and current production tree."""

    return _validate_with_config(
        receipt_bytes,
        static_inventory_bytes,
        PUBLIC_CONFIG,
        _ValidationCalls(),
    )


__all__ = [
    "AUTHORITY_ROOT",
    "INVENTORY_BYTE_LENGTH",
    "INVENTORY_SCHEMA",
    "INVENTORY_SHA256",
    "RECEIPT_SCHEMA",
    "SealedRuntimeRootReceiptValidationFailure",
    "validate_sealed_runtime_root_receipt_v1",
]
